#!/usr/bin/env python3
"""UFO-CHECK-0 differential twin — CPU pre-materialisation engine.

Design anchors (every rule cites its source; design doc
docs/next/design/ufo-check-0.md, registry/experiments/ufo-check-0.json):
  §4.1 closed UFO-SN3 modal inventory {U-RIGID, U-ANTI-WIT, U-KIND-DISJ,
       U-SPEC-MASK, U-EXIST, U-CLOSED, U-OOP}; regime tag on every rule
       (PROPOSED-ASM-1482); anything else refuses ERR_RULE_UNIMPLEMENTED.
  §4.2 gold = the AU (full-inventory) disposition — ENGINE-DERIVED,
       ORACLE-DIAGNOSTIC (PROPOSED-ASM-1481).
  §5   arm checkers: AG taxonomy-only, AU full, AD deranged meta-typing
       (PROPOSED-ASM-1485), AN representation-matched stated-fact null
       (PROPOSED-ASM-1486).
  §3   licensed-rejection contract (PROPOSED-ASM-1487): d=E rejects {C,U};
       d=C rejects {E,U}; d=U and d=OOP reject NOTHING.

OWL-RL CORE REUSE: within-situation asserted-subsumption propagation runs on
poc/rules-1/twin_engine.py (imported READ-ONLY at its rules-1-pinned sha,
ERR_TWIN_PIN on mismatch; the rules-1 tree is byte-untouched) via the
memberOf-property encoding: holds(S, x, T) == ("rel", x, "m:"+T, S) and a
stated edge T1 ⊑ T2 == subPropertyOf("m:"+T1, "m:"+T2), so twin_engine's
R-SUBP (rdfs7/prp-spo1, regime owl-rl) IS the within-situation subsumption
rule. All modal/rigidity content is layered here, never inside rules-1.

FOUR-VALUED MAPPING (CK-UFO §1.7 verbatim contract, in contract order):
ENTAILED iff the candidate is derivable; else CONTRADICTED iff its negation
is derivable or a violation fires in a legitimately closed scope; else
OUT-OF-PROFILE iff the commitment exceeds the executable inventory; else
UNDERDETERMINED. Neither UNDERDETERMINED nor OUT-OF-PROFILE is ever
converted into a negative answer or a rejection.

REJECTION-MESSAGE DISCIPLINE (review fix 5, machine-enforced): a rejection
message carries rule + premises ONLY — never a disposition label, never a
replacement answer, never conclusion-equivalent text. lint_message() is the
enforcing regex battery; materialise.py asserts it over EVERY message byte
in the accept tables and the runner re-asserts at load (fail closed,
ERR_MESSAGE_DISCIPLINE).

Fail-closed codes: ERR_TWIN_PIN, ERR_RULE_UNIMPLEMENTED, ERR_AXIOM_GRAMMAR,
ERR_BUDGET_EXCEEDED, ERR_CONFLICT, ERR_FIXTURE_SHA, ERR_MESSAGE_DISCIPLINE.
"""

import hashlib
import json
import os
import re
import sys

# --------------------------------------------------------------------------
# READ-ONLY pinned import of the rules-1 twin (design §4.1; ERR_TWIN_PIN).
# --------------------------------------------------------------------------
TWIN_ENGINE_PIN = \
    "399fcd8d946b585e6a73317238e049602ae5e86aef7c4ed1b0243ff887e8dea8"
_HERE = os.path.dirname(os.path.abspath(__file__))
_RULES1 = os.path.normpath(os.path.join(_HERE, "..", "rules-1"))


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_twin_engine():
    path = os.path.join(_RULES1, "twin_engine.py")
    got = _sha256_file(path)
    if got != TWIN_ENGINE_PIN:
        raise SystemExit("ERR_TWIN_PIN: poc/rules-1/twin_engine.py sha %s != "
                         "rules-1 pinned %s — refusing (READ-ONLY import "
                         "contract, design §4.1)" % (got, TWIN_ENGINE_PIN))
    if _RULES1 not in sys.path:
        sys.path.insert(0, _RULES1)
    import twin_engine  # noqa: PLC0415
    return twin_engine


te = _load_twin_engine()

ANSWERS = ("ENTAILED", "CONTRADICTED", "UNDERDETERMINED")
E, C, U, OOP = "ENTAILED", "CONTRADICTED", "UNDERDETERMINED", "OUT-OF-PROFILE"
RIGID_METAS = frozenset({"kind", "subkind"})       # arch-synthesis §2 item 1
ANTI_RIGID_METAS = frozenset({"role", "phase"})    # CK-UFO §1.2
META_KINDS = frozenset(RIGID_METAS | ANTI_RIGID_METAS)
CANDIDATE_FORMS = frozenset({"membership", "necessity", "spec_consequence",
                             "oop"})  # closed; else ERR_RULE_UNIMPLEMENTED


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))


# --------------------------------------------------------------------------
# Materialised representation (design §5 / review fix 4): ONE canonical
# proposition/situation/reifier object per item, consumed BYTE-IDENTICALLY by
# the AU/AD/AG twins and the AN null. build_representation() is the single
# constructor; rep_counts() is the MEASURED node/edge/reifier/byte census
# that materialise.py emits and gates (never merely asserted).
# --------------------------------------------------------------------------
def build_representation(facts):
    reifiers = []
    for pol, key in (("holds", "holds"), ("notHolds", "not_holds")):
        for (s, e_, t) in facts.get(key, []):
            reifiers.append({"polarity": pol, "situation": s,
                             "entity": e_, "type": t})
    reifiers.sort(key=lambda r: (r["situation"], r["entity"], r["type"],
                                 r["polarity"]))
    for i, r in enumerate(reifiers):
        r["id"] = "p%03d" % i
    entities = sorted({r["entity"] for r in reifiers}
                      | {x for x, _s in facts.get("exists", [])})
    types = sorted(set(facts["meta_types"].keys())
                   | {t for pair in facts.get("subsumptions", [])
                      for t in pair})
    for t in types:
        if facts["meta_types"].get(t) not in META_KINDS:
            raise SystemExit("ERR_AXIOM_GRAMMAR: type %r lacks a first-class "
                             "meta-type in %s (design §2: meta-typing is "
                             "stated, never inferred from names)"
                             % (t, sorted(META_KINDS)))
    return {
        "situations": sorted(facts["situations"]),
        "accessible": sorted([list(p) for p in facts.get("accessible", [])]),
        "entities": entities,
        "types": types,
        "meta": {t: facts["meta_types"][t] for t in types},
        "subsumptions": sorted([list(p)
                                for p in facts.get("subsumptions", [])]),
        "exists": sorted([list(p) for p in facts.get("exists", [])]),
        "closed_for": sorted([list(p)
                              for p in facts.get("closed_for", [])]),
        "reifiers": reifiers,
    }


def rep_counts(rep):
    """MEASURED census of the materialised representation (review fix 4)."""
    blob = canonical(rep).encode("utf-8")
    n_reifiers = len(rep["reifiers"])
    n_nodes = (len(rep["situations"]) + len(rep["entities"])
               + len(rep["types"]) + n_reifiers)
    n_edges = (len(rep["accessible"]) + len(rep["exists"])
               + len(rep["types"])            # one meta-typing edge per type
               + len(rep["subsumptions"]) + len(rep["closed_for"])
               + 3 * n_reifiers)              # situation/entity/type roles
    return {"n_nodes": n_nodes, "n_edges": n_edges,
            "n_reifiers": n_reifiers, "bytes": len(blob),
            "sha256": hashlib.sha256(blob).hexdigest()}


# --------------------------------------------------------------------------
# Within-situation subsumption closure on the PINNED rules-1 engine
# (memberOf encoding; R-SUBP regime owl-rl).
# --------------------------------------------------------------------------
def _subsumption_closure(holds, edges):
    """holds: set[(S,e,T)]; edges: [(sub, super)] -> closed set[(S,e,T)]."""
    if not edges:
        return set(holds)
    tbox = te.TBox()
    for i, (sub, sup) in enumerate(sorted(edges)):
        tbox.load_record({"schema": "kot-axiom/1", "subject": "m:%s" % sub,
                          "constraints": [{"kind": "subPropertyOf",
                                           "target": "m:%s" % sup}]},
                         "ufo0-edge-%d" % i)
    stated = [("rel", e_, "m:%s" % t, s) for (s, e_, t) in sorted(holds)]
    cl = te.Closure(tbox, stated, max_derived=10000)
    out = set()
    for f in cl.facts():
        if f[0] == "rel" and f[2].startswith("m:"):
            out.add((f[3], f[1], f[2][2:]))
    return out


def _reach(edges):
    """(sub, super) stated edges -> {t: set(ancestors incl self)}."""
    up = {}
    for sub, sup in edges:
        up.setdefault(sub, set()).add(sup)
    anc = {}

    def walk(t):
        if t in anc:
            return anc[t]
        anc[t] = {t}
        for s in up.get(t, ()):  # acyclic by generator construction
            anc[t] |= walk(s)
        return anc[t]

    for t in list(up) + [s for v in up.values() for s in v]:
        walk(t)
    return anc


# --------------------------------------------------------------------------
# The full UFO-SN3 world closure (AU; AD = same code, deranged meta map).
# --------------------------------------------------------------------------
class UfoWorld:
    """Closure of one item's representation under the §4.1 inventory."""

    def __init__(self, rep, meta_map=None):
        self.rep = rep
        self.meta = dict(meta_map if meta_map is not None else rep["meta"])
        for t, m in self.meta.items():
            if m not in META_KINDS:
                raise SystemExit("ERR_RULE_UNIMPLEMENTED: meta-type %r for %r "
                                 "(closed inventory %s)"
                                 % (m, t, sorted(META_KINDS)))
        self.situations = list(rep["situations"])
        self.acc = {tuple(p) for p in rep["accessible"]}
        self.exists = {tuple(p) for p in rep["exists"]}
        stated_holds, stated_not = set(), set()
        for r in rep["reifiers"]:
            trip = (r["situation"], r["entity"], r["type"])
            (stated_holds if r["polarity"] == "holds"
             else stated_not).add(trip)
        self.stated_holds = stated_holds
        self.stated_not = stated_not
        edges = [tuple(p) for p in rep["subsumptions"]]
        # U-SPEC-MASK [validation; CK-UFO §1.3]: a rigid type may not
        # specialise an anti-rigid type; illegal edges are MASKED from
        # propagation and recorded as violations.
        self.illegal_edges = [(a, b) for (a, b) in edges
                              if self.meta[a] in RIGID_METAS
                              and self.meta[b] in ANTI_RIGID_METAS]
        self.legal_edges = [p for p in edges if p not in self.illegal_edges]
        self._close()

    def _close(self):
        holds = set(self.stated_holds)
        exists = set(self.exists)
        rounds = 0
        while True:
            rounds += 1
            if rounds > 50:  # ERR_BUDGET_EXCEEDED discipline (ASM-1160 form)
                raise SystemExit("ERR_BUDGET_EXCEEDED: ufo closure did not "
                                 "reach fixpoint in 50 rounds")
            before = (len(holds), len(exists))
            # R-SUBP via the PINNED rules-1 engine [owl-rl]
            holds = _subsumption_closure(holds, self.legal_edges)
            # U-EXIST [ufo-modal; arch-synthesis §2 item 1]
            for (s, e_, _t) in holds:
                exists.add((e_, s))
            # U-RIGID [ufo-modal; arch-synthesis §2 item 1]
            for (s1, e_, t) in sorted(holds):
                if self.meta.get(t) in RIGID_METAS:
                    for (a, b) in sorted(self.acc):
                        if a == s1 and (e_, b) in exists:
                            holds.add((b, e_, t))
            if (len(holds), len(exists)) == before:
                break
        self.holds = holds
        self.exists_cl = exists
        anc = _reach(self.legal_edges)
        # U-KIND-DISJ [horn-def; Guizzardi 2005 unique-ultimate-sortal via
        # arch-synthesis §2 item 2]: distinct Kinds, neither subkind-related,
        # are pairwise disjoint with ZERO authored disjointness.
        kinds = sorted(t for t, m in self.meta.items() if m == "kind")
        self.disjoint = set()
        for i, k1 in enumerate(kinds):
            for k2 in kinds[i + 1:]:
                if k2 not in anc.get(k1, {k1}) and k1 not in anc.get(k2, {k2}):
                    self.disjoint.add((k1, k2))
                    self.disjoint.add((k2, k1))
        # negative closure: stated notHolds propagate DOWN legal edges;
        # disjointness-derived negatives; then U-CLOSED [validation;
        # CK-UFO §4.1] STRATIFIED after the positive fixpoint.
        down = {}
        for sub, sup in self.legal_edges:
            down.setdefault(sup, set()).add(sub)

        def descend(t):
            out, stack = {t}, [t]
            while stack:
                x = stack.pop()
                for s in down.get(x, ()):
                    if s not in out:
                        out.add(s)
                        stack.append(s)
            return out

        neg = set()
        for (s, e_, t) in self.stated_not:
            for t2 in descend(t):
                neg.add((s, e_, t2))
        for (s, e_, t) in sorted(self.holds):
            for (k1, k2) in sorted(self.disjoint):
                if t == k1:
                    for t2 in descend(k2):
                        neg.add((s, e_, t2))
        for (s, t) in {tuple(p) for p in self.rep["closed_for"]}:
            for (e_, s2) in sorted(self.exists_cl):
                if s2 == s and (s, e_, t) not in self.holds:
                    neg.add((s, e_, t))  # U-CLOSED: closed scope only
        self.neg = neg

    def conflicts(self):
        return sorted(self.holds & self.neg)

    # ---------------------------------------------------------------- why --
    # PREMISE-CITATION discipline (review fix 5): a why() string names the
    # rule and lists STATED PREMISE facts only. It never states what the
    # rule concludes, never a disposition label, never a replacement answer
    # — lint_message() machine-enforces this over every rejection byte.
    def _why_holds(self, s, e_, t):
        if (s, e_, t) in self.stated_holds:
            return "the stated fact line: in %s '%s' is a '%s'" % (s, e_, t)
        anc = _reach(self.legal_edges)
        for (s2, e2, t2) in sorted(self.stated_holds | self.holds):
            if e2 == e_ and s2 == s and t2 != t and t in anc.get(t2, ()):
                return ("rule R-SUBP [owl-rl] premises: in %s '%s' is a "
                        "'%s'; the stated edge chain from '%s' up to '%s'"
                        % (s, e_, t2, t2, t))
        for (a, b) in sorted(self.acc):
            if b == s and (a, e_, t) in self.holds \
                    and self.meta.get(t) in RIGID_METAS:
                return ("rule U-RIGID [ufo-modal] premises: in %s '%s' is a "
                        "'%s'; '%s' is a %s type; '%s' exists in %s; %s is "
                        "possible from %s"
                        % (a, e_, t, t, self.meta[t], e_, s, s, a))
        return ("rules of the closed inventory applied to the stated "
                "membership lines for '%s' and '%s' at %s" % (e_, t, s))

    def _why_neg(self, s, e_, t):
        if (s, e_, t) in self.stated_not:
            return ("the stated fact line: in %s '%s' is not a '%s'"
                    % (s, e_, t))
        for (k1, k2) in sorted(self.disjoint):
            if (s, e_, k1) in self.holds and t == k2:
                return ("rule U-KIND-DISJ [horn-def] premises: in %s '%s' "
                        "is a '%s'; '%s' is a kind type; '%s' is a kind "
                        "type; no specialisation edge relates them"
                        % (s, e_, k1, k1, k2))
        for (s2, t2) in {tuple(p) for p in self.rep["closed_for"]}:
            if s2 == s:
                return ("rule U-CLOSED [validation] premises: the declared "
                        "complete '%s' membership scope at %s; '%s' exists "
                        "in %s; that scope carries no '%s' line for '%s'"
                        % (t2, s, e_, s, t, e_))
        return ("rules of the closed inventory applied to the stated "
                "non-membership lines for '%s' and '%s' at %s" % (e_, t, s))

    # -------------------------------------------------- candidate -> d ----
    def disposition(self, cand):
        """(d, reason) per the CK-UFO §1.7 contract, in contract order."""
        form = cand["form"]
        if form not in CANDIDATE_FORMS:
            raise SystemExit("ERR_RULE_UNIMPLEMENTED: candidate form %r "
                             "(closed inventory %s)"
                             % (form, sorted(CANDIDATE_FORMS)))
        if form == "oop":
            # U-OOP [reference-only guard; CK-UFO §1.7]
            return OOP, ("rule U-OOP [reference-only]: the candidate "
                         "commitment (%s) exceeds the executable UFO-SN3 "
                         "inventory" % cand.get("oop_kind", "unspecified"))
        if form == "membership":
            s, e_, t = cand["situation"], cand["entity"], cand["type"]
            if (s, e_, t) in self.holds:
                return E, self._why_holds(s, e_, t)
            if (s, e_, t) in self.neg:
                return C, self._why_neg(s, e_, t)
            return U, "no licensed proof either way"
        if form == "necessity":
            e_, t = cand["entity"], cand["type"]
            # U-ANTI-WIT [ufo-modal; CK-UFO §1.3]: witnessed counterexample
            # for a necessity candidate over an ANTI-RIGID type (design §4.1
            # rule table verbatim: "necessity candidate over anti-rigid T +
            # witness"); rigid-type necessity witnessing is OUTSIDE the
            # closed inventory, so the checker holds no proof there.
            for s in self.situations:
                if self.meta.get(t) in ANTI_RIGID_METAS \
                        and (s, e_, t) in self.neg \
                        and (e_, s) in self.exists_cl:
                    return C, ("rule U-ANTI-WIT [ufo-modal] premises: %s; "
                               "'%s' exists in %s"
                               % (self._why_neg(s, e_, t), e_, s))
            if all((s, e_, t) in self.holds for s in self.situations):
                return E, ("premises: the '%s' membership records for '%s' "
                           "at each of %s together with the declared "
                           "situation list"
                           % (t, e_, ", ".join(self.situations)))
            return U, ("no witness and no closed scope: absence of a "
                       "counterexample is not its nonexistence")
        # spec_consequence (F-SPEC; design §4.4 example 4)
        sub, sup, s = cand["sub"], cand["super"], cand["situation"]
        if (sub, sup) in self.illegal_edges:
            return C, ("rule U-SPEC-MASK [validation] premises: the stated "
                       "edge '%s' specialises '%s'; '%s' is a %s type; "
                       "'%s' is a %s type"
                       % (sub, sup, sub, self.meta[sub], sup,
                          self.meta[sup]))
        if (sub, sup) in self.legal_edges:
            return E, ("rule R-SUBP [owl-rl] premises: the stated edge "
                       "'%s' specialises '%s' at %s" % (sub, sup, s))
        return U, "the invoked specialisation edge is not stated"


# --------------------------------------------------------------------------
# AG — gUFO-taxonomy-only checker (design §5): asserted subsumption
# within-situation + STATED disjointness ONLY. No derived Kind disjointness,
# no cross-situation propagation, no rigidity/witness/scope semantics.
# --------------------------------------------------------------------------
def ag_disposition(rep, cand):
    if cand["form"] == "oop":
        return OOP, "outside the taxonomy-only inventory"
    if cand["form"] != "membership":
        # necessity/spec_consequence need modal or rigidity semantics the
        # taxonomy-only checker does not have -> no proof either way.
        return U, "taxonomy-only checker: no in-situation membership claim"
    stated_holds = {(r["situation"], r["entity"], r["type"])
                    for r in rep["reifiers"] if r["polarity"] == "holds"}
    stated_not = {(r["situation"], r["entity"], r["type"])
                  for r in rep["reifiers"] if r["polarity"] == "notHolds"}
    edges = [tuple(p) for p in rep["subsumptions"]]  # ALL stated (no mask)
    holds = _subsumption_closure(stated_holds, edges)
    down = {}
    for a, b in edges:
        down.setdefault(b, set()).add(a)
    neg = set()
    for (s, e_, t) in stated_not:
        stack, seen = [t], {t}
        while stack:
            x = stack.pop()
            neg.add((s, e_, x))
            for sb in down.get(x, ()):
                if sb not in seen:
                    seen.add(sb)
                    stack.append(sb)
    # STATED disjointness only: this item family authors none (F-DISJ tests
    # DERIVED disjointness precisely because nothing is authored), so the
    # stated-disjointness branch is structurally empty here — kept explicit.
    s, e_, t = cand["situation"], cand["entity"], cand["type"]
    if (s, e_, t) in holds:
        return E, ("stated class taxonomy: membership at %s via the stated "
                   "specialisation edges" % s)
    if (s, e_, t) in neg:
        return C, ("stated class taxonomy: a stated non-membership at %s "
                   "covers '%s'" % (s, t))
    return U, "taxonomy-only checker: no stated-taxonomy proof either way"


# --------------------------------------------------------------------------
# AN — representation-matched stated-fact null (design §5, CK-UFO §3.3 A1
# fold-in, PROPOSED-ASM-1486): SAME rep bytes, stated-fact lookup ONLY.
# --------------------------------------------------------------------------
def an_accepts(rep, cand, answer):
    """True iff the null checker accepts `answer`. No rules, byte lookup."""
    if cand["form"] == "oop":
        return True
    stated_holds = {(r["situation"], r["entity"], r["type"])
                    for r in rep["reifiers"] if r["polarity"] == "holds"}
    stated_not = {(r["situation"], r["entity"], r["type"])
                  for r in rep["reifiers"] if r["polarity"] == "notHolds"}
    if answer == U:
        return True  # accept U always (never converts absence into rejection)
    if cand["form"] == "membership":
        trip = (cand["situation"], cand["entity"], cand["type"])
        return trip in stated_holds if answer == E else trip in stated_not
    if cand["form"] == "necessity":
        if answer == E:
            return all((s, cand["entity"], cand["type"]) in stated_holds
                       for s in rep["situations"])
        return any((s, cand["entity"], cand["type"]) in stated_not
                   for s in rep["situations"])
    # spec_consequence: the candidate is about an edge, not a stated
    # holds/notHolds proposition -> literally-stated support never exists.
    return False


# --------------------------------------------------------------------------
# Sattolo derangement of the meta-type assignment (AD arm,
# PROPOSED-ASM-1485): a seed-pinned Sattolo CYCLE over the meta-label
# alphabet {kind, phase, role, subkind}, so EVERY type's kind/role/phase
# label moves (design §5 verbatim: "every type's kind/role/phase label
# moved"), dispositions re-derived under the deranged assignment.
# Deterministic from (seed, attempt); no fixed points by construction;
# materialise.py measures the resulting AU-coincidence rate and bumps
# `attempt` until the registered <=0.35 bound holds (attempt RECORDED).
# --------------------------------------------------------------------------
def sattolo_derangement(labels, seed, attempt=0):
    labels = sorted(labels)
    if len(labels) < 2:
        raise SystemExit("ERR_AXIOM_GRAMMAR: need >=2 labels to derange")
    idx = list(range(len(labels)))
    for i in range(len(idx) - 1, 0, -1):
        h = hashlib.sha256(("ufo-check-0/derange|%d|%d|%d"
                            % (seed, attempt, i)).encode()).digest()
        j = int.from_bytes(h[:8], "big") % i  # j in [0, i): Sattolo cycle
        idx[i], idx[j] = idx[j], idx[i]
    perm = {labels[k]: labels[idx[k]] for k in range(len(labels))}
    if any(a == b for a, b in perm.items()):
        raise SystemExit("ERR_AXIOM_GRAMMAR: fixed point in Sattolo cycle "
                         "(bug)")
    return perm


# --------------------------------------------------------------------------
# Licensed-rejection accept tables + message templates (design §3, §5.2).
# --------------------------------------------------------------------------
# Machine-enforced message discipline (review fix 5): NO disposition labels,
# NO replacement answers, NO conclusion-equivalent text. Any hit refuses.
MESSAGE_PROHIBITED = [re.compile(p, re.IGNORECASE) for p in (
    r"\bENTAILED\b", r"\bCONTRADICTED\b", r"\bUNDERDETERMINED\b",
    r"\bOUT.OF.PROFILE\b", r"\bentail", r"\bcontradict", r"\bunderdetermin",
    r"\btrue\b", r"\bfalse\b", r"\bcorrect\b", r"\bincorrect\b",
    r"answer\s+(?:is|was|should|must)\b", r"\binstead\b", r"\btherefore\b",
    r"\bso the claim\b", r"\bclaim (?:holds|fails)\b", r"\bright answer\b",
    r"\bderiv", r"\bprove", r"\bproof\b", r"\bconclu",
    r"\bthe claim is\b", r"\bshould\b", r"\bmust be\b",
)]


def lint_message(msg):
    """Returns the list of prohibited-pattern hits (empty == clean)."""
    return [p.pattern for p in MESSAGE_PROHIBITED if p.search(msg)]


REJ_FRAME = ("REJECTED: your answer conflicts with a licensed check. "
             "%s. Reconsider the stated facts and answer again.")
AN_MESSAGE = ("REJECTED: your answer conflicts with the recorded facts "
              "about situations S1 and S2. Review each stated fact line "
              "once more. Reconsider the stated facts and answer again.")
PAD_SENTENCE = " Check the situation records once more."


def rejection_message(arm, reason):
    if arm == "AN":
        return AN_MESSAGE
    return REJ_FRAME % reason


def accept_table_for(arm, rep, cand, world_or_none):
    """-> {answer: {"accept": bool, "message": str|None}}, d_arm.

    Licensed-rejection contract (PROPOSED-ASM-1487): d=E rejects {C,U};
    d=C rejects {E,U}; d=U and d=OOP reject NOTHING; AN is lookup-based.
    """
    table = {}
    if arm == "AN":
        for ans in ANSWERS:
            ok = an_accepts(rep, cand, ans)
            table[ans] = {"accept": ok,
                          "message": None if ok else rejection_message(
                              "AN", "")}
        return table, None
    if arm == "AG":
        d, reason = ag_disposition(rep, cand)
    else:  # AU / AD share the full-inventory code path
        d, reason = world_or_none.disposition(cand)
    rejected = {E: {C, U}, C: {E, U}}.get(d, set())
    for ans in ANSWERS:
        ok = ans not in rejected
        table[ans] = {"accept": ok,
                      "message": None if ok else rejection_message(
                          arm, reason)}
    return table, d


CYCLE_NEXT = {E: C, C: U, U: E}


def floors_for(table, gold):
    """Analytic trivial-policy floors per possible first answer
    (PROPOSED-ASM-1487; design §5.3). -> {first: {policy: expectation}}."""
    out = {}
    for first in ANSWERS:
        if table[first]["accept"]:
            v = 1.0 if first == gold else 0.0
            out[first] = {"uniform": v, "always_u": v, "cycle": v}
        else:
            nr = [a for a in ANSWERS if table[a]["accept"]]
            out[first] = {
                "uniform": (1.0 / len(nr)) if gold in nr else 0.0,
                "always_u": 1.0 if gold == U else 0.0,
                "cycle": 1.0 if CYCLE_NEXT[first] == gold else 0.0,
            }
    return out
