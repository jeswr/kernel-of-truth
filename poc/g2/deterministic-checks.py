#!/usr/bin/env python3
"""deterministic-checks.py -- the g2 no-test deterministic checks (frozen
record dependent_vars: litmus_promise_recovered, partition_axioms_recovered,
sidecar_conflicts), computed mechanically over the Pi dump
(poc/g2/pi-derived.jsonl) and the endorsed sidecar data/axioms-v0/.

1. LITMUS (P1 HS2: "check Pi recovers `promise [= words`"): the dump must
   contain the R1 subsumption promise [= WORDS.

2. PARTITION RESIDUE (P1 HS2: Pi "cannot recover the partition-side axioms
   -- confirming the read-out/residue split"; frozen DV
   partition_axioms_recovered MUST be 0). Partition-side axioms = the
   endorsed sidecar constraints (axioms-v0: disjointWith, functional,
   cardinality, concept-granularity range, inverseOf -- the section-3.2 (ii)
   list). A sidecar constraint counts as RECOVERED iff Pi's output contains
   an axiom of the SAME kind, same subject, same target. Pi's only overlap
   channels: (a) R6 inverseOf edges; (b) R3 ranges -- these are
   sort-granularity, so a concept-granularity sidecar range is recovered
   only if the sidecar target IS a sort (it never is in axioms-v0).
   disjointWith/functional/cardinality have no Pi output form at all
   (checked: the dump contains no such forms).

3. SIDECAR CONFLICT (P1 HS2: "Additional kill for Pi-as-normative if Pi
   conflicts with any endorsed sidecar axiom on v0 (deterministic check,
   no test)"). Conflict rules, per constraint kind:
   - disjointWith(A,B): conflict iff the reflexive-transitive closure of
     Pi's subClassOf edges yields A [=* B, B [=* A, or a common Pi subject
     C with C [=* A and C [=* B.
   - functional / cardinality: Pi asserts no cardinalities => no conflict
     channel (recorded as vacuous).
   - range(R, C): conflict iff Pi asserts a sort-granularity range for R
     whose sort is INCOMPATIBLE with C's sort (C's sort = the sort of a
     kernel-v0 record's frame: InstanceSchema/WhenTrue subjects are
     Thing/Person-sort via referent-1 refKind; molecule targets without
     explications have no derivable sort => vacuous, recorded).
   - inverseOf(R,S): conflict iff Pi asserts inverseOf(R,T) with T != S
     (or inverseOf(S,T) with T != R).

Output: poc/g2/deterministic-checks.json (all three metrics + the full
per-constraint evidence table).
"""
import json, os, glob

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
DUMP = os.path.join(REPO, "poc/g2/pi-derived.jsonl")
OUT = os.path.join(REPO, "poc/g2/deterministic-checks.json")


def load_urn_map():
    m = {}
    for p in ("data/kernel-v0/minted-urns.jsonl",
              "data/molecules-v0/minted-urns.jsonl"):
        for l in open(os.path.join(REPO, p), encoding="utf-8"):
            l = l.strip()
            if l:
                o = json.loads(l)
                m[o["urn"]] = o["id"]
    return m


def concept_sort(cid):
    """Sort of a kernel-v0 concept via its record's referent-1 refKind
    (InstanceSchema/WhenTrue) -- None if unresolvable (molecule etc.)."""
    path = os.path.join(REPO, "data/kernel-v0/concepts",
                        cid.rsplit(":", 1)[-1] + ".json")
    if not os.path.exists(path):
        return None
    o = json.load(open(path, encoding="utf-8"))
    rk = {r["index"]: r["refKind"] for r in o["explication"]["referents"]}
    return {"SomethingRef": "Thing-sort", "SomeoneRef": "Person-sort",
            "TimeRef": "Time-sort", "PlaceRef": "Place-sort"}.get(rk.get(1))


def main():
    axioms = [json.loads(l) for l in open(DUMP, encoding="utf-8") if l.strip()]
    urn = load_urn_map()

    # 1. litmus
    litmus = any(a["rule"] == "R1" and a["subject"] == "urn:kernel-v0:promise"
                 and a["target_kind"] == "prime" and a["target"] == "WORDS"
                 for a in axioms)

    # Pi output indexes
    pi_forms = sorted({a["form"] for a in axioms})
    sub_edges = {(a["subject"], a["target"]) for a in axioms
                 if a["form"] == "subClassOf" and a["target_kind"] == "concept"}
    pi_ranges = {a["subject"]: a["target"] for a in axioms if a["form"] == "range"}
    pi_inverse = {}
    for a in axioms:
        if a["form"] == "inverseOf":
            pi_inverse.setdefault(a["subject"], set()).add(a["target"])
            pi_inverse.setdefault(a["target"], set()).add(a["subject"])

    # subClassOf closure (reflexive-transitive over Pi concept edges)
    def closure(start):
        seen, stack = {start}, [start]
        while stack:
            x = stack.pop()
            for (s, t) in sub_edges:
                if s == x and t not in seen:
                    seen.add(t)
                    stack.append(t)
        return seen

    # 2 + 3. per-constraint table
    table = []
    n_recovered = 0
    n_conflicts = 0
    for f in sorted(glob.glob(os.path.join(REPO, "data/axioms-v0/*.json"))):
        base = os.path.basename(f)
        if base == "manifest.json":
            continue
        o = json.load(open(f, encoding="utf-8"))
        subj = urn.get(o["subject"], o["subject"])
        for c in o["constraints"]:
            kind = c["kind"]
            tgt = urn.get(c.get("target", c.get("path", "")), c.get("target", c.get("path")))
            row = {"sidecar_record": base, "subject": subj, "kind": kind,
                   "target": tgt, "recovered": False, "conflict": False,
                   "evidence": ""}
            if kind == "disjointWith":
                # recovery: Pi has no disjointness form
                row["evidence"] = "Pi emits no disjointWith form (forms=%s)" % pi_forms
                a_up, b_up = closure(subj), closure(tgt)
                subj_all = {s for (s, _t) in sub_edges}
                common = [s for s in sorted(subj_all)
                          if subj in closure(s) and tgt in closure(s)]
                if tgt in a_up or subj in b_up or common:
                    row["conflict"] = True
                    row["evidence"] += ("; CONFLICT: closure relates the "
                                        "disjoint pair (common=%s)" % common)
                else:
                    row["evidence"] += ("; no Pi subsumption chain relates "
                                        "%s / %s" % (subj, tgt))
            elif kind == "functional":
                row["evidence"] = ("Pi emits no functional/global-role form; "
                                   "no cardinality claims => conflict channel vacuous")
            elif kind == "cardinality":
                row["evidence"] = ("Pi emits no cardinality form; no Pi "
                                   "cardinality claims => conflict channel vacuous")
            elif kind == "range":
                pr = pi_ranges.get(subj)
                if pr is None:
                    row["evidence"] = "Pi asserts no range for %s" % subj
                else:
                    tsort = concept_sort(tgt) if isinstance(tgt, str) else None
                    row["evidence"] = ("Pi range(%s)=%s (sort-granularity); "
                                       "sidecar target %s sort=%s"
                                       % (subj, pr, tgt, tsort))
                    # recovered only if identical axiom -- sort vs concept
                    # granularity => never identical here
                    if tsort is not None and tsort != pr:
                        row["conflict"] = True
                        row["evidence"] += " => INCOMPATIBLE sorts"
                    else:
                        row["evidence"] += " => compatible (no conflict)"
            elif kind == "inverseOf":
                got = pi_inverse.get(subj, set())
                if tgt in got:
                    row["recovered"] = True
                    row["evidence"] = "Pi R6 emitted inverseOf(%s,%s)" % (subj, tgt)
                elif got:
                    row["conflict"] = True
                    row["evidence"] = ("Pi asserts inverseOf(%s,%s) != sidecar "
                                       "target %s" % (subj, sorted(got), tgt))
                else:
                    row["evidence"] = ("Pi R6 emitted no inverse pair for %s "
                                       "(swap-1-2 structural comparison found "
                                       "no match)" % subj)
            else:
                raise SystemExit("ERR_CHECK: unknown sidecar kind %r" % kind)
            n_recovered += int(row["recovered"])
            n_conflicts += int(row["conflict"])
            table.append(row)

    out = {"litmus_promise_recovered": int(litmus),
           "partition_axioms_recovered": n_recovered,
           "sidecar_conflicts": n_conflicts,
           "pi_output_forms": pi_forms,
           "n_pi_axioms_total": len(axioms),
           "n_pi_axioms_judged": sum(1 for a in axioms if a["judged"]),
           "per_constraint": table}
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("litmus_promise_recovered",
                                          "partition_axioms_recovered",
                                          "sidecar_conflicts")}, sort_keys=True))


if __name__ == "__main__":
    main()
