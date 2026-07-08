#!/usr/bin/env python3
"""g7_instrument — deterministic apply-clause cap/growth bulk projection (HS7 / NF6).

    python3 tools/experiments/g7_instrument.py [--root <repo>]

RAW OUTPUT ONLY (P2 §2.4): emits counts; renders NO verdict and knows nothing
about the pre-registered 10% bound (frozen in the g7 registry record, applied
by verdict-gen).

WHAT IT PROJECTS (NF6 verbatim: "project depth/clause-cap pressure at bulk
scale under both options"), per record of the committed bulk corpus
kernel-v0 (54) + molecules-v0 (54) + lexical-wn31 (117,791):

  c(r)  clause count of r's own explication — recursive count of kot-ast/1
        clause nodes (objects with "type" in {"pred","op"}); 0 for AxiomsOnly
        and molecule records (no explication AST committed).
  refs(r)  r's relational content: wn31 `axioms` targets; kernel-v0 manifest
        `references`; molecule `groundingRefs` + `axioms` targets.

  OPTION (a) apply/reference rendering: demand_ref(r) = max(1, c(r) + |refs(r)|)
        — each relational item is one reference-carrying clause (the kot-ast/2
        apply-clause floor; max(1,·) because an empty record still costs its
        identity stub).
  OPTION (b) inline-only rendering: demand_inline(r) = c(r) + Σ_t inline(t)
        over t in refs(r), one level deep (no recursion — a deliberate,
        documented UNDERSTATEMENT of inline pressure: real inlining recurses),
        where inline(t) = max(1, c(t) + |refs(t)|) when the target t is a
        committed record, else 1 (dangling floor).

  cap violation:   demand_inline(r) > 32 (CAPS.maxClauses,
                   encoder/src/lexicon.ts — the load-bearing grammar cap,
                   docs/architecture.md §"Structure").
  >1.5x growth:    |refs(r)| >= 1 AND demand_inline(r) > 1.5 * demand_ref(r).
  n_breached_either: union, counted per record.

Both biases run AGAINST the kill (one-level inlining understates option (b)'s
true cost; the 1-clause apply floor understates nothing), so a breach count
over 10% cannot be an artifact of generous accounting.

Deterministic: pure counting over committed files; no RNG, no model. Output
metric keys are EXACTLY the frozen analysis contract's input keys
(analysis/g7.py) plus reporting breakdowns.
"""

import argparse
import glob
import json
import os
import sys

MAX_CLAUSES = 32  # encoder/src/lexicon.ts CAPS.maxClauses (profile-1, load-bearing)
WN31_FILES = ("synsets-noun.jsonl", "synsets-verb.jsonl", "synsets-adj.jsonl", "synsets-adv.jsonl")


def fail(code, msg):
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def clause_count(node):
    """Recursive kot-ast/1 clause-node count: objects with type pred|op."""
    n = 0
    if isinstance(node, dict):
        if node.get("type") in ("pred", "op"):
            n += 1
        for v in node.values():
            n += clause_count(v)
    elif isinstance(node, list):
        for v in node:
            n += clause_count(v)
    return n


def main():
    ap = argparse.ArgumentParser(description="G7 raw cap/growth projection counts (no verdict).")
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    root = args.root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    c = {}     # record id -> own explication clause count
    refs = {}  # record id -> list of referenced record ids

    # kernel-v0: explication ASTs + manifest references.
    man_path = os.path.join(root, "data", "kernel-v0", "manifest.json")
    if not os.path.isfile(man_path):
        fail("ERR_G7_CORPUS", "missing %s" % man_path)
    with open(man_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    n_kernel = 0
    for entry in manifest["concepts"]:
        cid = entry["id"]
        with open(os.path.join(root, "data", "kernel-v0", entry["file"]), "r", encoding="utf-8") as f:
            rec = json.load(f)
        c[cid] = clause_count(rec.get("explication", {}))
        refs[cid] = list(entry.get("references") or [])
        n_kernel += 1

    # molecules-v0: no explication AST; groundingRefs + axiom targets.
    n_mol = 0
    for path in sorted(glob.glob(os.path.join(root, "data", "molecules-v0", "molecules", "*.json"))):
        with open(path, "r", encoding="utf-8") as f:
            rec = json.load(f)
        cid = rec["id"]
        c[cid] = clause_count(rec.get("partialExplication") or {})
        refs[cid] = list(rec.get("groundingRefs") or []) + \
            [a.get("target") for a in (rec.get("axioms") or []) if a.get("target")]
        n_mol += 1

    # lexical-wn31: AxiomsOnly; every axiom target is a reference.
    n_wn = 0
    for name in WN31_FILES:
        path = os.path.join(root, "data", "lexical-wn31", name)
        if not os.path.isfile(path):
            fail("ERR_G7_CORPUS", "missing corpus file %s" % path)
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                cid = rec["id"]
                c[cid] = 0
                refs[cid] = [a.get("target") for a in (rec.get("axioms") or []) if a.get("target")]
                n_wn += 1

    def demand_ref(rid):
        return max(1, c[rid] + len(refs[rid]))

    n_records = len(c)
    n_cap = n_growth = n_either = n_dangling_targets = 0
    for rid in c:
        r = refs[rid]
        inline = c[rid]
        for t in r:
            if t in c:
                inline += demand_ref(t)
            else:
                inline += 1
                n_dangling_targets += 1
        ref_demand = demand_ref(rid)
        cap = inline > MAX_CLAUSES
        growth = len(r) >= 1 and inline > 1.5 * ref_demand
        if cap:
            n_cap += 1
        if growth:
            n_growth += 1
        if cap or growth:
            n_either += 1

    metrics = {
        "n_records_bulk": n_records,
        "n_breached_either": n_either,
        "n_cap_violations": n_cap,
        "n_growth_over_1p5x": n_growth,
        "by_source_records": {"kernel-v0": n_kernel, "molecules-v0": n_mol, "lexical-wn31": n_wn},
        "n_dangling_targets_floored_to_1": n_dangling_targets,
        "max_clauses_cap": MAX_CLAUSES,
    }
    print(json.dumps(metrics, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
