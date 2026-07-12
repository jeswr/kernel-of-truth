#!/usr/bin/env python3
"""DDC shard merge — reconstructs the CANONICAL analysis-input triple
(items-ddc1[-mock].jsonl / cells-ddc1[-mock].json / sidecar-ddc1[-mock]
.json) from INDEPENDENT per-cell Modal shard outputs (one job per
(rung, arm, rho, seed) cell; modal/modal_ddc.py --print-jobs), mirroring
poc/rules-2/merge_shards.py.

FAIL-CLOSED assertions (any failure => no merged output):
  * every shard carries IDENTICAL pins (ddc-manifest sha, corpus shas,
    donor revisions) and mode — shards from mismatched harness bytes or
    corpora can NEVER be pooled;
  * every non-null t0_block is byte-identical — one T0 campaign block
    serves the whole campaign;
  * cell keys (rung, arm, rho, seed) are pairwise DISJOINT and row-level
    (rung, arm, rho, seed, subset, task, item_id) tuples are globally
    unique — a cell ran exactly once;
  * per-shard records sha re-verified against its own results json;
  * COVERAGE: the merged cell set equals EXACTLY the ASM-1654 grid
    (A2 rows required iff any A2 cell present — the G0-gated arm merges
    all-or-nothing; r360 rows iff any r360 cell present, §8 promotion).

The merged outputs are byte-identical to a monolithic ddc_runner.py run
over the same coverage (ddc_common.finalize is the single shared
finaliser; validate_mock.py proves the parity at $0, modulo the disclosed
measured cost fields). Row order is the canonical sort of
ddc_common.row_sort_key. This module states NO feasibility conclusion.

Usage:
  python3 merge_shards.py --out-dir <merged-dir> <shard-dir> [...]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import ddc_common as C  # noqa: E402

INVARIANT_FIELDS = ("experiment", "mode", "pins")


def load_shard(d):
    res_files = sorted(glob.glob(os.path.join(d, "results-ddc1*.json")))
    if len(res_files) != 1:
        raise SystemExit("ERR_MERGE: %s has %d results-ddc1*.json files "
                         "(need exactly 1)" % (d, len(res_files)))
    res = json.load(open(res_files[0]))
    rec_path = os.path.join(d, res["records_file"])
    if not os.path.exists(rec_path):
        raise SystemExit("ERR_MERGE: %s missing records file %s"
                         % (d, res["records_file"]))
    if C.sha256_file(rec_path) != res["records_sha256"]:
        raise SystemExit("ERR_MERGE: %s records sha mismatch vs its own "
                         "results json" % d)
    rows = [json.loads(x) for x in open(rec_path) if x.strip()]
    if len(rows) != res["n_rows"]:
        raise SystemExit("ERR_MERGE: %s n_rows %d != %d rows on disk"
                         % (d, res["n_rows"], len(rows)))
    suffix = "-mock" if res["mode"] == "MOCK" else ""
    cells = json.load(open(os.path.join(
        d, "cells-ddc1%s.json" % suffix)))["cells"]
    return res, rows, cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--manifest", default=C.MANIFEST_PATH)
    ap.add_argument("shard_dirs", nargs="+")
    args = ap.parse_args()
    manifest = C.load_manifest(args.manifest)

    shards = [load_shard(d) for d in args.shard_dirs]
    res0 = shards[0][0]

    # 1) invariants byte-identical across shards
    for i, (res, _rows, _cells) in enumerate(shards[1:], 1):
        for f in INVARIANT_FIELDS:
            if json.dumps(res.get(f), sort_keys=True) != \
                    json.dumps(res0.get(f), sort_keys=True):
                raise SystemExit(
                    "ERR_MERGE: shard %s field %r differs from shard %s — "
                    "mismatched harness/corpus bytes can never be pooled"
                    % (args.shard_dirs[i], f, args.shard_dirs[0]))
    t0_blocks = [json.dumps(r["t0_block"], sort_keys=True)
                 for r, _rw, _c in shards if r.get("t0_block") is not None]
    if not t0_blocks:
        raise SystemExit("ERR_MERGE: no shard carries a t0_block")
    if len(set(t0_blocks)) != 1:
        raise SystemExit("ERR_MERGE: shards carry DIFFERENT t0_blocks — "
                         "one T0 campaign block serves the whole campaign")

    # 2) disjoint cells; globally unique rows
    seen_cells = {}
    seen_rows = set()
    for i, (_res, rows, cells) in enumerate(shards):
        for c in cells:
            key = (c["rung"], c["arm"], float(c["rho"]), int(c["seed"]))
            if key in seen_cells:
                raise SystemExit("ERR_MERGE: cell %r appears in shards %s "
                                 "and %s — a cell ran twice"
                                 % (key, args.shard_dirs[seen_cells[key]],
                                    args.shard_dirs[i]))
            seen_cells[key] = i
        for r in rows:
            rk = (r["rung"], r["arm"], float(r["rho"]), int(r["seed"]),
                  int(r["subset"]), r["task"], str(r["item_id"]))
            if rk in seen_rows:
                raise SystemExit("ERR_MERGE: duplicate row %r (shard %s)"
                                 % (rk, args.shard_dirs[i]))
            seen_rows.add(rk)

    # 3) coverage == the ASM-1654 grid (A2 iff present; r360 iff present)
    a2_ran = any(k[1] == "A2" for k in seen_cells)
    s2_ran = any(k[0] == "r360" for k in seen_cells)
    expected = set()
    for rung in ("r135",) + (("r360",) if s2_ran else ()):
        cov = manifest["arm_coverage"][rung]
        for arm in sorted(cov):
            if arm == "A2" and not a2_ran:
                continue
            for rho in cov[arm]["rhos"]:
                for seed in cov[arm]["seeds"]:
                    expected.add((rung, arm, float(rho), int(seed)))
    missing = expected - set(seen_cells)
    extra = set(seen_cells) - expected
    if missing or extra:
        raise SystemExit("ERR_MERGE: coverage mismatch vs the ASM-1654 "
                         "grid — missing %s, unexpected %s (a sharded "
                         "launch covers exactly the cells a monolithic "
                         "one would)"
                         % (sorted(missing)[:8], sorted(extra)[:8]))

    merged = C.finalize(shards, args.out_dir, res0["mode"] == "MOCK",
                        manifest)
    merged["merge_note"] = (
        "merged by poc/ddc/merge_shards.py from %d shards; rows in the "
        "canonical ddc_common.row_sort_key order; the pinned analysis is "
        "row-order-independent" % len(shards))
    merged["shards"] = [{
        "dir": os.path.basename(os.path.normpath(d)),
        "shard_tag": res.get("shard_tag"),
        "cells_run": res["cells_run"],
        "n_rows": res["n_rows"],
        "records_sha256": res["records_sha256"],
    } for d, (res, _rw, _c) in zip(args.shard_dirs, shards)]
    suffix = "-mock" if res0["mode"] == "MOCK" else ""
    with open(os.path.join(args.out_dir,
                           "results-ddc1%s.json" % suffix), "w") as f:
        json.dump(merged, f, indent=1, sort_keys=True)
    print("merged %d shards -> %s (%d rows, records sha %s)"
          % (len(shards), args.out_dir, merged["n_rows"],
             merged["records_sha256"][:12]))


if __name__ == "__main__":
    main()
