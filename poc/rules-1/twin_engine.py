#!/usr/bin/env python3
# RULES-1 differential-twin forward chainer (WMRE-1 C3).
#
# Design anchors (every rule cites its source):
#   docs/next/arch/world-model-rules-engine.md §2.1 C3, §3 (worked example),
#   PROPOSED-ASM-1124 (twin role; twin GOVERNS if the sparq Rust build fails,
#   MD-4 as approved in issue #19), PROPOSED-ASM-1160 (termination = safe
#   function-free fragment + explicit per-item budgets, ERR_BUDGET_EXCEEDED;
#   closed inventory retained), PROPOSED-ASM-1162 (regime tag on every rule
#   and every proof node, regime in {owl-rl, horn-def, policy}; no entity
#   generation — no rule head here introduces a fresh individual).
#
# Rule inventory (CLOSED — anything else refuses ERR_RULE_UNIMPLEMENTED):
#   R-SUBP        rdfs7 / prp-spo1        regime owl-rl
#   R-DOM         prp-dom                 regime owl-rl
#   R-RNG         prp-rng                 regime owl-rl
#   R-INV         prp-inv1/2              regime owl-rl
#   R-CHAIN       prp-spo2 (length 2)     regime owl-rl
#   R-COVER-ELIM  compiled Horn policy rule with NAMED premises
#                 (PROPOSED-ASM-1120 UNA + PROPOSED-ASM-1121 covering +
#                  functional member axioms), per ASM-1121/§3   regime policy
#   CAX-DW        disjointWith conflict detection (E5 stratum)  regime owl-rl
#   PRP-FP+UNA    functional conflict detection under stated differentFrom
#
# Facts are ground tuples; no function symbols; rule heads only bind variables
# already bound in the body (safe Datalog) => the fixpoint terminates without
# any depth bound (ASM-1160). Budgets are still enforced, fail-closed.
#
# Determinism: worklist order is insertion order over sorted inputs; dict
# iteration never affects the derived SET or any proof (premise ids are
# canonical fact keys, not sequence numbers).
#
# Fail-closed codes: ERR_RULE_UNIMPLEMENTED, ERR_AXIOM_GRAMMAR,
# ERR_BUDGET_EXCEEDED, ERR_CONFLICT, ERR_INSUFFICIENT_PREMISES (query),
# ERR_AMBIGUOUS_ANSWER (query).

import json
from pathlib import Path

IMPLEMENTED_KINDS = ("functional", "range", "domain", "disjointWith",
                     "inverseOf", "subPropertyOf", "coveredBy",
                     "propertyChain", "classDeclaration")

# fact shapes:  ("rel", s, p, o)   ("cls", e, c)   ("diff", a, b)  a<b sorted


class EngineError(Exception):
    def __init__(self, code, msg):
        self.code = code
        super().__init__(f"{code}: {msg}")


class TBox:
    """Compiled axiom layer. Each axiom keeps its source record id."""

    def __init__(self):
        self.subprop = {}     # p -> {(super, axiom_ref)}
        self.domain = {}      # p -> (cls, ref)
        self.range = {}       # p -> (cls, ref)
        self.functional = {}  # p -> ref
        self.disjoint = []    # (c1, c2, ref)
        self.inverse = {}     # p -> (q, ref)
        self.chains = []      # (p1, p2, super, ref)
        self.covers = []      # (p, (m1, m2, ...), ref)
        self.known = set()    # every URN mentioned (licensing)

    def load_record(self, rec, ref):
        if rec.get("schema") != "kot-axiom/1":
            raise EngineError("ERR_AXIOM_GRAMMAR", f"{ref}: bad schema")
        subj = rec["subject"]
        self.known.add(subj)
        for c in rec["constraints"]:
            kind = c.get("kind")
            if kind not in IMPLEMENTED_KINDS:
                raise EngineError("ERR_RULE_UNIMPLEMENTED",
                                  f"{ref}: kind {kind!r} (closed inventory)")
            if kind == "functional":
                self.functional[subj] = ref
            elif kind == "range":
                self.range[subj] = (c["target"], ref)
                self.known.add(c["target"])
            elif kind == "domain":
                self.domain[subj] = (c["target"], ref)
                self.known.add(c["target"])
            elif kind == "disjointWith":
                self.disjoint.append((subj, c["target"], ref))
                self.known.add(c["target"])
            elif kind == "inverseOf":
                self.inverse[subj] = (c["target"], ref)
                self.known.add(c["target"])
            elif kind == "subPropertyOf":
                self.subprop.setdefault(subj, set()).add((c["target"], ref))
                self.known.add(c["target"])
            elif kind == "coveredBy":
                ms = tuple(c["members"])
                if len(ms) < 2:
                    raise EngineError("ERR_AXIOM_GRAMMAR",
                                      f"{ref}: coveredBy needs >=2 members")
                self.covers.append((subj, ms, ref))
                self.known.update(ms)
            elif kind == "propertyChain":
                ch = c["chain"]
                if len(ch) != 2:
                    # length-2 only in RULES-1 (safe fragment kept minimal;
                    # longer chains are a rule-language expansion => refuse)
                    raise EngineError("ERR_RULE_UNIMPLEMENTED",
                                      f"{ref}: chain length {len(ch)}")
                self.chains.append((ch[0], ch[1], subj, ref))
                self.known.update(ch)
            elif kind == "classDeclaration":
                pass  # licensing only


def load_tbox(paths):
    """Compile an EXPLICIT pinned record list (files or dirs).

    RULES-1 pins the kinship module: axioms-v0/{rel-mother, rel-father,
    class-man} + all of axioms-kinship-v1.  axioms-v0/{class-bookmark
    (cardinality), rel-maker-of, rel-part-of} are OUTSIDE the RULES-1 closed
    inventory and are not pinned; passing them refuses at load
    (ERR_RULE_UNIMPLEMENTED) — fail-closed, never silently skipped.
    """
    tbox = TBox()
    for d in paths:
        d = Path(d)
        files = ([p for p in sorted(d.glob("*.json"))
                  if p.name != "manifest.json"] if d.is_dir() else [d])
        for p in files:
            tbox.load_record(json.loads(p.read_text()), str(p))
    return tbox


class Closure:
    """Forward-chained closure of one (temporary) world against a TBox.

    why(fact_key) returns the proof tree: stated facts are leaves; every
    derived node carries {rule, regime, axiom_refs, premises}.
    """

    def __init__(self, tbox, stated, max_derived=10000, budget_note=None):
        self.tbox = tbox
        self.stated = []
        self.deriv = {}    # fact -> None (stated) | dict (derivation)
        self.conflicts = []
        self.max_derived = max_derived
        for f in stated:
            f = self._norm(f)
            if f not in self.deriv:
                self.deriv[f] = None
                self.stated.append(f)
        self._run()

    @staticmethod
    def _norm(f):
        if f[0] == "diff":
            a, b = sorted(f[1:])
            return ("diff", a, b)
        return tuple(f)

    def _add(self, fact, rule, regime, refs, premises):
        fact = self._norm(fact)
        if fact in self.deriv:
            return False
        if len(self.deriv) - len(self.stated) >= self.max_derived:
            raise EngineError("ERR_BUDGET_EXCEEDED",
                              f"max_derived={self.max_derived}")
        self.deriv[fact] = {"rule": rule, "regime": regime,
                            "axiom_refs": list(refs),
                            "premises": [list(p) for p in premises]}
        return True

    def _run(self):
        t = self.tbox
        changed = True
        while changed:
            changed = False
            facts = list(self.deriv.keys())
            rels = [f for f in facts if f[0] == "rel"]
            classes = [f for f in facts if f[0] == "cls"]
            diffs = {(f[1], f[2]) for f in facts if f[0] == "diff"}
            rel_index = {}
            for f in rels:
                rel_index.setdefault((f[1], f[2]), []).append(f)

            for f in rels:
                _, s, p, o = f
                # R-SUBP (rdfs7/prp-spo1) [owl-rl]
                for sup, ref in sorted(t.subprop.get(p, ())):
                    changed |= self._add(("rel", s, sup, o), "R-SUBP",
                                         "owl-rl", [ref], [f])
                # R-DOM / R-RNG (prp-dom/prp-rng) [owl-rl]
                if p in t.domain:
                    cls, ref = t.domain[p]
                    changed |= self._add(("cls", s, cls), "R-DOM",
                                         "owl-rl", [ref], [f])
                if p in t.range:
                    cls, ref = t.range[p]
                    changed |= self._add(("cls", o, cls), "R-RNG",
                                         "owl-rl", [ref], [f])
                # R-INV (prp-inv1) [owl-rl]
                if p in t.inverse:
                    q, ref = t.inverse[p]
                    changed |= self._add(("rel", o, q, s), "R-INV",
                                         "owl-rl", [ref], [f])
                # R-CHAIN (prp-spo2, length 2) [owl-rl] — the index is
                # rebuilt over ALL rels each pass, so matching f as the FIRST
                # hop only is complete at fixpoint.
                for p1, p2, sup, ref in t.chains:
                    if p == p1:
                        for g in rel_index.get((o, p2), ()):
                            changed |= self._add(("rel", s, sup, g[3]),
                                                 "R-CHAIN", "owl-rl",
                                                 [ref], [f, g])

            # R-COVER-ELIM [policy] — compiled Horn rule, named premises
            # (WMRE-1 §3): P coveredBy {m1..mk}; P(c)=p; for all members m_i
            # except exactly one m*, functional(m_i) & m_i(c)=x_i &
            # diff(x_i, p)  =>  m*(c)=p.
            for P, members, cover_ref in t.covers:
                for f in [f for f in rels if f[2] == P]:
                    _, c, _, p_ent = f
                    eliminated, remaining, prem, refs = [], [], [f], [cover_ref]
                    for m in members:
                        wit = [g for g in rels
                               if g[2] == m and g[1] == c and
                               tuple(sorted((g[3], p_ent))) in diffs]
                        if m in t.functional and wit:
                            g = wit[0]
                            eliminated.append(m)
                            prem.append(g)
                            prem.append(("diff",) +
                                        tuple(sorted((g[3], p_ent))))
                            refs.append(t.functional[m])
                        else:
                            remaining.append(m)
                    if len(remaining) == 1 and eliminated:
                        changed |= self._add(
                            ("rel", c, remaining[0], p_ent),
                            "R-COVER-ELIM", "policy", refs, prem)

            # conflict detection (surfaced, never resolved — E5 stratum)
            self.conflicts = []
            cls_index = {}
            for f in classes:
                cls_index.setdefault(f[1], set()).add(f[2])
            for c1, c2, ref in t.disjoint:
                for e, cs in sorted(cls_index.items()):
                    if c1 in cs and c2 in cs:
                        self.conflicts.append(
                            {"code": "ERR_CONFLICT", "rule": "CAX-DW",
                             "entity": e, "classes": [c1, c2],
                             "axiom_ref": ref})
            for p, ref in sorted(t.functional.items()):
                by_subj = {}
                for f in rels:
                    if f[2] == p:
                        by_subj.setdefault(f[1], []).append(f[3])
                for s, objs in sorted(by_subj.items()):
                    for i in range(len(objs)):
                        for j in range(i + 1, len(objs)):
                            if tuple(sorted((objs[i], objs[j]))) in diffs:
                                self.conflicts.append(
                                    {"code": "ERR_CONFLICT",
                                     "rule": "PRP-FP+UNA", "subject": s,
                                     "relation": p,
                                     "objects": sorted((objs[i], objs[j])),
                                     "axiom_ref": ref})

    # ---------------------------------------------------------------- api --
    def facts(self):
        return set(self.deriv.keys())

    def derived(self):
        return {f for f, d in self.deriv.items() if d is not None}

    def why(self, fact):
        fact = self._norm(fact)
        if fact not in self.deriv:
            raise EngineError("ERR_INSUFFICIENT_PREMISES",
                              f"not in closure: {fact}")
        d = self.deriv[fact]
        if d is None:
            return {"fact": list(fact), "stated": True}
        return {"fact": list(fact), "stated": False, "rule": d["rule"],
                "regime": d["regime"], "axiom_refs": d["axiom_refs"],
                "premises": [self.why(tuple(p)) for p in d["premises"]]}

    def query_relation(self, a, b, vocab):
        """All vocab-named relations w with ('rel', a, urn_w, b) in Cl(S).

        vocab: {surface_word: relation_urn}. Returns (word, why) or raises
        ERR_INSUFFICIENT_PREMISES / ERR_AMBIGUOUS_ANSWER (fail closed).
        """
        if self.conflicts:
            raise EngineError("ERR_CONFLICT",
                              json.dumps(self.conflicts[0], sort_keys=True))
        hits = [(w, ("rel", a, u, b)) for w, u in sorted(vocab.items())
                if ("rel", a, u, b) in self.deriv]
        if not hits:
            raise EngineError("ERR_INSUFFICIENT_PREMISES",
                              f"no licensed relation {a} -> {b}")
        # prefer the most specific: drop any hit that is a strict super-
        # property (direct or via chain-subsumption) of another hit
        urns = {w: u for w, u in vocab.items()}
        supers = set()
        for w, f in hits:
            u = urns[w]
            seen, stack = set(), [u]
            while stack:
                x = stack.pop()
                for sup, _ in self.tbox.subprop.get(x, ()):
                    if sup not in seen:
                        seen.add(sup)
                        stack.append(sup)
            supers |= {s for s in seen if s in {urns[w2] for w2, _ in hits}
                       and s != u}
        final = [(w, f) for w, f in hits if urns[w] not in supers]
        if len(final) != 1:
            raise EngineError("ERR_AMBIGUOUS_ANSWER",
                              f"{[w for w, _ in final]}")
        w, f = final[0]
        return w, self.why(f)
