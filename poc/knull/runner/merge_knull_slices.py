#!/usr/bin/env python3
"""Merge knull-v2 per-arm campaign slices into the ONE canonical
run-records.jsonl + item-meta.json that analysis/knull_v3.py consumes.

The Modal account fan (poc/knull/modal/README-knull-v2-run.md) launches one
knull_runner_v2.py slice per account (--arms kernel / plain / plain-padded /
opaque). Rows are self-describing, so the merge is a validated
concatenation, fail-closed on:
  * duplicate cells across slices (KNULL2M_ERR_DUP);
  * an incomplete union: the merged set must be EXACTLY the frozen 36-cell
    plan of registry/experiments/knull-v2.json — 4 arms x alone-R1 +
    {kernel,plain,opaque} x alone-R3 (ASM-1086 excludes plain-padded) +
    4 arms x verify-retry-R1(k=4) + kernel shuffled-verify-retry-R1,
    seeds {0,1,2} (KNULL2M_ERR_PLAN);
  * n mismatch across cells (KNULL2M_ERR_N);
  * mixed mock/real rows (KNULL2M_ERR_MODE);
  * item-meta divergence across slices — every slice writes the full
    four-arm meta from the pinned sidecar, so all copies must be
    byte-identical (KNULL2M_ERR_META).

Deterministic output order: (arm, cell, rung, seed) sorted — so the merged
file is byte-reproducible from the same slices.

Usage:
  python3 poc/knull/runner/merge_knull_slices.py \
      --slices <dir1> <dir2> ... --out-dir <merged>
  (each <dirN> is a runner --out-dir or an unpacked *-modal results dir
   containing run-records.jsonl + item-meta.json)
"""

import argparse
import json
import os
import sys

ARMS = ("kernel", "plain", "plain-padded", "opaque")   # knull-v2.json
R3_ARMS = ("kernel", "plain", "opaque")                # ASM-1086
SEEDS = (0, 1, 2)                                      # design.seeds


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(1)


def frozen_plan():
    plan = []
    for a in ARMS:
        plan += [(a, "model-alone", "R1", s) for s in SEEDS]
        if a in R3_ARMS:
            plan += [(a, "model-alone", "R3", s) for s in SEEDS]
        plan += [(a, "verify-retry", "R1", s) for s in SEEDS]
        if a == "kernel":
            plan += [(a, "shuffled-verify-retry", "R1", s) for s in SEEDS]
    return set(plan)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slices", nargs="+", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    rows, meta_bytes, provenance = {}, None, []
    for d in args.slices:
        rp = os.path.join(d, "run-records.jsonl")
        mp = os.path.join(d, "item-meta.json")
        if not (os.path.isfile(rp) and os.path.isfile(mp)):
            die("KNULL2M_ERR_SLICE", "%s lacks run-records.jsonl/item-meta.json" % d)
        n_here = 0
        with open(rp, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                key = (r["arm"], r["cell"], r["rung"], r["seed"])
                if key in rows:
                    die("KNULL2M_ERR_DUP", "cell %s appears in more than one "
                        "slice" % (key,))
                rows[key] = r
                n_here += 1
        mb = open(mp, "rb").read()
        if meta_bytes is None:
            meta_bytes = mb
        elif mb != meta_bytes:
            die("KNULL2M_ERR_META", "item-meta.json differs in %s — slices "
                "were built from different inputs" % d)
        provenance.append({"slice_dir": os.path.abspath(d), "n_cells": n_here})

    want = frozen_plan()
    got = set(rows)
    if got != want:
        die("KNULL2M_ERR_PLAN",
            "merged cells != the frozen 36-cell plan; missing=%s extra=%s"
            % (sorted(want - got), sorted(got - want)))
    ns = {r["n"] for r in rows.values()}
    if len(ns) != 1:
        die("KNULL2M_ERR_N", "inconsistent n across cells: %s" % sorted(ns))
    mocks = {bool(r.get("mock")) for r in rows.values()}
    if len(mocks) != 1:
        die("KNULL2M_ERR_MODE", "mixed mock/real rows across slices")

    os.makedirs(args.out_dir, exist_ok=True)
    out_records = os.path.join(args.out_dir, "run-records.jsonl")
    with open(out_records, "w", encoding="utf-8") as f:
        for key in sorted(rows):
            f.write(json.dumps(rows[key], sort_keys=True) + "\n")
    out_meta = os.path.join(args.out_dir, "item-meta.json")
    with open(out_meta, "wb") as f:
        f.write(meta_bytes)
    with open(os.path.join(args.out_dir, "merge-manifest.json"), "w") as f:
        json.dump({"schema": "kot-knull2-merge/1",
                   "n_cells": len(rows), "n_items": sorted(ns)[0],
                   "mode": "MOCK" if mocks == {True} else "REAL",
                   "slices": provenance}, f, indent=1, sort_keys=True)
        f.write("\n")
    print("merged %d slices -> %d cells (frozen 36-cell plan complete, "
          "n=%d, %s)" % (len(provenance), len(rows), sorted(ns)[0],
                         "MOCK" if mocks == {True} else "REAL"))
    print("next: python3 analysis/knull_v3.py --records %s --item-meta %s "
          "--out %s" % (out_records, out_meta,
                        os.path.join(args.out_dir, "analysis.json")))


if __name__ == "__main__":
    main()
