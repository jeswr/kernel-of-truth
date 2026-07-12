#!/usr/bin/env python3
"""pi-project.py -- deterministic Pi projector over kot-ast/1 explication
structure (kernel-v0), per the FROZEN g2 design's source spec:
docs/design-dl-from-nsm-and-lean-reconstruction.md section 3.2 ("Call this
deterministic projection Pi: explication -> TBox skeleton. Pi is syntactic,
linear, and fail-closed").

STATUS: PROVISIONAL d-pi STAND-IN. The operational-DAG node `d-pi`
(docs/research-plan/03-operational-dag.md line 587: "implement Pi projector
over explication structure (kernel-v0, 54 records)") was never built and the
frozen registry entry pins it only as "PINNED-AT-INPUTS:d-pi (tools/pi/ +
derived-subsumption dump sha)". This file is the minimal faithful
implementation of the section-3.2 rule list, built for the
PROVISIONAL-ON-LLM-PROXY g2 run. It designs nothing beyond that list; every
rule cites its source line. Fail-closed: any AST node kind / pred / op /
role / refKind outside the enumerated kernel-v0 vocabulary aborts (ERR_PI_*).

Rules implemented (section 3.2 (i) read-out list, verbatim numbering):
  R1 "Subsumption from classification clauses": top-level clause
     BE-SPEC(undergoer=ref 1, attribute=SP) with SP head primeHead P
     => Self [= P; SP head kindFrame(of concept C) => Self [= C.
     Self = referent 1, InstanceSchema/WhenTrue frames only (gist section 4.6
     reading "referent 1 := an arbitrary instance"; for RelationalSchema
     referent 1 is a relatum, not Self -- no R1).
  R2 "Subsumption from reference structure": concept references NOT in
     classification position are exported as `references` edges, never as
     subsumptions ("the rest is `references` (already exported)").
  R3 "Domain/range at sort granularity": RelationalSchema frame =>
     domain = sort(refKind of referent 1), range = sort(refKind of
     referent 2). Emitted as judged axioms (a domain/range axiom is the
     subsumption Exists R.Top [= Domain / Top [= Forall R.Range).
  R4 "Existential role restrictions": every bind-introduced SP in a role
     slot of a pred clause in VERIDICAL context => Self [= Exists
     (pred.role).(sort & head restriction). Veridical context = top-level
     clauses and arguments of the scenario operators WHEN/AFTER/BEFORE/
     BECAUSE/LIKE (scenario-script projection is exactly the typicality
     risk G2 measures -- section 3.2 confidence note); scopes under
     NOT/CAN/MAYBE/IF, quote payloads (propositional-attitude content,
     section 3.1) and embedded complement clauses are NOT projected
     (projecting from non-veridical scope is unsound on its face; Pi is
     fail-closed).
  R5 "Definitional role composition": NOT IMPLEMENTED (the design gives no
     operational rule; inventing one is design work, out of runner scope).
     Recorded as zero-yield.
  R6 "Inverse pairs": mechanical swap-1-2 structural comparison of
     RelationalSchema clause sets (canonical JSON equality after renaming
     referents 1<->2); emits inverseOf edges.

Output: pi-derived.jsonl -- one line per derived axiom, plus `references`
edges (form=references, judged=false). Deterministic: sorted by canonical
key; ids g2:pi:NNN assigned in that order. No RNG anywhere.
"""
import json, os, sys, hashlib, glob

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
KERNEL = os.path.join(REPO, "data/kernel-v0/concepts")
OUT = os.path.join(REPO, "poc/g2/pi-derived.jsonl")

# closed kernel-v0 vocabulary (enumerated 2026-07-11 over the pinned corpus
# 8209cada...; anything outside it aborts -- fail-closed, ERR_PI_VOCAB)
PREDS = {"HAPPEN", "KNOW", "DO", "THERE-IS", "THINK", "SEE", "DON'T-WANT",
         "WANT", "BE-SPEC", "SAY", "BE-SOMEWHERE", "FEEL", "TRUE", "IS-MINE",
         "MOVE", "LIVE", "DIE", "HEAR"}
VERIDICAL_OPS = {"WHEN", "AFTER", "BEFORE", "BECAUSE", "LIKE"}
NONVERIDICAL_OPS = {"NOT", "CAN", "MAYBE", "IF"}
ROLES = {"undergoer", "time", "experiencer", "complement", "agent", "quote",
         "stimulus", "attribute", "topic", "locus", "comitative", "addressee",
         "instrument", "possessor", "manner", "duration"}
REFKINDS = {"SomethingRef": "Thing-sort", "SomeoneRef": "Person-sort",
            "TimeRef": "Time-sort", "PlaceRef": "Place-sort"}
PRIMES = {"WHEN~TIME", "PEOPLE", "SOMEONE", "SOMETHING~THING", "WORDS",
          "WHERE~PLACE", "BODY"}


def die(msg):
    sys.stderr.write("ERR_PI: %s\n" % msg)
    sys.exit(2)


def word(concept_id):
    return concept_id.rsplit(":", 1)[-1].replace("-", " ")


def sp_head_key(head, rec_id):
    """Canonical target key for an SP head. Returns (kind, value)."""
    k = head.get("kind")
    if k == "primeHead":
        p = head["prime"]
        if p not in PRIMES:
            die("unknown prime %r in %s" % (p, rec_id))
        return ("prime", p)
    if k == "kindFrame":
        of = head["of"]
        if of.get("kind") == "concept":
            return ("concept", of["id"])
        if of.get("kind") == "ref":
            return ("self-ref", of["index"])   # self-internal; no target
        die("kindFrame.of kind %r in %s" % (of.get("kind"), rec_id))
    if k == "partFrame":
        of = head["of"]
        if of.get("kind") == "ref":
            return ("part-of-ref", of["index"])
        if of.get("kind") == "concept":
            return ("part-of-concept", of["id"])
        die("partFrame.of kind %r in %s" % (of.get("kind"), rec_id))
    die("unknown SP head kind %r in %s" % (k, rec_id))


def collect_concept_refs(node, acc):
    if isinstance(node, dict):
        if node.get("kind") == "concept":
            acc.append(node["id"])
        for v in node.values():
            collect_concept_refs(v, acc)
    elif isinstance(node, list):
        for v in node:
            collect_concept_refs(v, acc)


def walk_veridical(node, ctx, hits, rec_id):
    """Collect (pred, role, sp, ctx_path) for bind-introduced SPs in
    veridical context (R4). ctx is the operator/scope path (provenance)."""
    if isinstance(node, list):
        for v in node:
            walk_veridical(v, ctx, hits, rec_id)
        return
    if not isinstance(node, dict):
        return
    t = node.get("type")
    if t == "op":
        op = node["op"]
        if op in VERIDICAL_OPS:
            for a in node.get("args", []):
                walk_veridical(a, ctx + [op], hits, rec_id)
        elif op in NONVERIDICAL_OPS:
            return          # non-veridical scope: no projection (fail-closed)
        else:
            die("unknown op %r in %s" % (op, rec_id))
        return
    if t == "pred":
        pred = node["pred"]
        if pred not in PREDS:
            die("unknown pred %r in %s" % (pred, rec_id))
        for role, filler in node.get("roles", {}).items():
            if role not in ROLES:
                die("unknown role %r in %s" % (role, rec_id))
            if not isinstance(filler, dict):
                die("bad filler in %s" % rec_id)
            fk = filler.get("kind")
            if fk == "sp" and "bind" in filler:
                hits.append((pred, role, filler, list(ctx)))
            # quote payloads and embedded complement clauses: NOT descended
            # (section 3.1: attitude content is native, never projected).
            # temporal/ref/prime/sp-without-bind fillers introduce nothing.
        return
    # bare arg nodes (ref / prime / temporal) inside op args: nothing to do


def project_record(rec):
    rid, expl = rec["id"], rec["explication"]
    if expl.get("schema") != "kot-ast/1":
        die("schema %r in %s" % (expl.get("schema"), rid))
    frame = expl["frame"]
    if frame not in ("InstanceSchema", "WhenTrue", "RelationalSchema"):
        die("frame %r in %s" % (frame, rid))
    refkinds = {}
    for r in expl["referents"]:
        if r["refKind"] not in REFKINDS:
            die("refKind %r in %s" % (r["refKind"], rid))
        refkinds[r["index"]] = r["refKind"]
    axioms = []

    # ---- R1: classification clauses (InstanceSchema/WhenTrue Self=ref1) ----
    if frame in ("InstanceSchema", "WhenTrue"):
        for ci, cl in enumerate(expl["clauses"]):
            if cl.get("type") != "pred" or cl.get("pred") != "BE-SPEC":
                continue
            und = cl["roles"].get("undergoer")
            att = cl["roles"].get("attribute")
            if not (isinstance(und, dict) and und.get("kind") == "ref"
                    and und.get("index") == 1 and isinstance(att, dict)
                    and att.get("kind") == "sp"):
                continue
            tk = sp_head_key(att["head"], rid)
            if tk[0] in ("prime", "concept"):
                axioms.append({"rule": "R1", "form": "subClassOf",
                               "subject": rid, "frame": frame,
                               "target_kind": tk[0], "target": tk[1],
                               "source": "clause[%d]" % ci, "judged": True})
            # self-ref / partFrame classification: no external target; skip

    # ---- R3: domain/range at sort granularity (RelationalSchema) ----
    if frame == "RelationalSchema":
        if 1 not in refkinds or 2 not in refkinds:
            die("RelationalSchema %s lacks referents 1/2" % rid)
        axioms.append({"rule": "R3", "form": "domain", "subject": rid,
                       "frame": frame, "target_kind": "sort",
                       "target": REFKINDS[refkinds[1]],
                       "source": "referents[1]", "judged": True})
        axioms.append({"rule": "R3", "form": "range", "subject": rid,
                       "frame": frame, "target_kind": "sort",
                       "target": REFKINDS[refkinds[2]],
                       "source": "referents[2]", "judged": True})

    # ---- R4: existential role restrictions (veridical binds) ----
    hits = []
    for ci, cl in enumerate(expl["clauses"]):
        walk_veridical(cl, ["top[%d]" % ci], hits, rid)
    for pred, role, sp, ctx in hits:
        bind = sp["bind"]
        tk = sp_head_key(sp["head"], rid)
        det_other = sp.get("det", "").startswith("OTHER")
        axioms.append({"rule": "R4", "form": "existential", "subject": rid,
                       "frame": frame, "pred": pred, "role": role,
                       "bind": bind, "target_kind": tk[0],
                       "target": tk[1] if tk[0] in ("prime", "concept") else str(tk[1]),
                       "det_other": det_other,
                       "source": "/".join(ctx), "judged": True})

    # ---- R2: reference edges (exported, never judged) ----
    refs = []
    collect_concept_refs(expl["clauses"], refs)
    classified = {a["target"] for a in axioms
                  if a["rule"] == "R1" and a["target_kind"] == "concept"}
    for cid in sorted(set(refs) - classified):
        axioms.append({"rule": "R2", "form": "references", "subject": rid,
                       "frame": frame, "target_kind": "concept",
                       "target": cid, "source": "reference-structure",
                       "judged": False})
    return axioms


def canonical_swap12(expl):
    """Referent-1<->2-swapped canonical clause JSON (R6)."""
    def swap(node):
        if isinstance(node, dict):
            out = {}
            for k, v in node.items():
                if k == "index" and node.get("kind") == "ref" and v in (1, 2):
                    out[k] = 3 - v
                elif k == "bind" and v in (1, 2):
                    out[k] = 3 - v
                else:
                    out[k] = swap(v)
            return out
        if isinstance(node, list):
            return [swap(v) for v in node]
        return node
    refs = sorted(
        [dict(r, index=(3 - r["index"] if r["index"] in (1, 2) else r["index"]))
         for r in expl["referents"]], key=lambda r: r["index"])
    return json.dumps({"referents": refs, "clauses": swap(expl["clauses"])},
                      sort_keys=True)


def canonical_plain(expl):
    return json.dumps({"referents": sorted(expl["referents"],
                                           key=lambda r: r["index"]),
                       "clauses": expl["clauses"]}, sort_keys=True)


def main():
    recs = []
    for f in sorted(glob.glob(os.path.join(KERNEL, "*.json"))):
        recs.append(json.load(open(f, encoding="utf-8")))
    if len(recs) != 54:
        die("expected 54 kernel-v0 records, got %d" % len(recs))
    axioms = []
    for r in recs:
        axioms.extend(project_record(r))
    # R6 inverse pairs over RelationalSchema records
    rels = [r for r in recs if r["explication"]["frame"] == "RelationalSchema"]
    plain = {r["id"]: canonical_plain(r["explication"]) for r in rels}
    swapped = {r["id"]: canonical_swap12(r["explication"]) for r in rels}
    for i, a in enumerate(rels):
        for b in rels[i + 1:]:
            if plain[a["id"]] == swapped[b["id"]]:
                axioms.append({"rule": "R6", "form": "inverseOf",
                               "subject": a["id"], "frame": "RelationalSchema",
                               "target_kind": "concept", "target": b["id"],
                               "source": "swap-1-2-structural", "judged": True})
    # deterministic order + ids
    def key(a):
        return (a["subject"], a["rule"], a["form"], str(a["target"]),
                a.get("pred", ""), a.get("role", ""), str(a.get("bind", "")),
                a["source"])
    axioms.sort(key=key)
    seen = set()
    for a in axioms:
        k = key(a)
        if k in seen:
            die("duplicate axiom key %r" % (k,))
        seen.add(k)
    for i, a in enumerate(axioms):
        a["id"] = "g2:pi:%03d" % i
    with open(OUT, "w", encoding="utf-8") as f:
        for a in axioms:
            f.write(json.dumps(a, sort_keys=True, ensure_ascii=False) + "\n")
    judged = [a for a in axioms if a["judged"]]
    by_rule = {}
    for a in axioms:
        by_rule[a["rule"]] = by_rule.get(a["rule"], 0) + 1
    litmus = any(a["rule"] == "R1" and a["subject"] == "urn:kernel-v0:promise"
                 and a["target_kind"] == "prime" and a["target"] == "WORDS"
                 for a in axioms)
    print(json.dumps({"total": len(axioms), "judged": len(judged),
                      "by_rule": by_rule,
                      "litmus_promise_sub_words_in_dump": litmus,
                      "out_sha256": hashlib.sha256(
                          open(OUT, "rb").read()).hexdigest()},
                     sort_keys=True))


if __name__ == "__main__":
    main()
