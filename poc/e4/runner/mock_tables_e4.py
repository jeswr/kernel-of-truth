#!/usr/bin/env python3
"""MOCK E4 vector tables for the runner smoke ONLY (bead kernel-of-truth-hkp).

The real tables (poc/e4/inputs/vector-tables-manifest.json + .f32 files) are
pinned to kot-enc-Bq/1 @D=512, which fails closed at any other dimension —
the CPU mock runs at d_model=64, so it gets clearly-stamped MOCK tables with
the SAME manifest schema (one loader in finetune_e4.py serves both):

  - the 54 AUTHORED kernel rows are COPIED from the E1 mock tables
    ($E1_WORK/vector-tables-mock-d64.json), so the kernel arm's
    authored-row consistency gate (table x frozenScale == the E1
    checkpoint's frozen rows, bit-exact) is exercised for real in the smoke;
  - the 1,000 synthetic rows are random unit vectors (content-free by
    construction; the smoke checks MECHANICS, never content);
  - shuffled = seeded derangements over all 1,054 ids; random-frozen =
    N(0, 0.02^2) tables. Deterministic DetStream labels -> byte-identical
    reruns. Row order = the REAL manifest's ids (read-only), so the mapping
    logic under test is identical to the full run's.
"""

import argparse
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
E4_DIR = os.path.dirname(HERE)
E1_PIPELINE = os.path.join(os.path.dirname(E4_DIR), "e1", "pipeline")
sys.path.insert(0, E1_PIPELINE)
from mock_tables import derangement, gaussian_rows  # noqa: E402  (read-only reuse)

INIT_STD = 0.02


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d", type=int, default=64)
    ap.add_argument("--e1-tables", required=True, help="E1 mock vector-tables json")
    ap.add_argument("--out", required=True, help="output DIR (manifest + .f32 files)")
    ap.add_argument("--seeds", default="0,1")
    ap.add_argument("--ids-from", default=os.path.join(E4_DIR, "inputs",
                                                       "vector-tables-manifest.json"))
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]
    os.makedirs(os.path.join(args.out, "vectors"), exist_ok=True)

    with open(args.ids_from) as f:
        real = json.load(f)
    ids, slugs = real["ids"], real["slugs"]
    n = len(ids)

    with open(args.e1_tables) as f:
        e1t = json.load(f)
    if not e1t.get("mock"):
        raise SystemExit("ERR_TABLES: --e1-tables must be the E1 MOCK tables")
    if e1t["D"] != args.d:
        raise SystemExit(f"ERR_TABLES: e1 mock D={e1t['D']} != --d {args.d}")
    n_auth = len(e1t["ids"])
    if ids[:n_auth] != e1t["ids"]:
        raise SystemExit("ERR_TABLES: authored id order mismatch vs E1 mock tables")

    kernel = np.zeros((n, args.d), dtype=np.float32)
    kernel[:n_auth] = np.asarray(e1t["kernel"], dtype=np.float32)  # e1 trainer's exact cast
    for i, slug in enumerate(slugs[n_auth:], start=n_auth):
        row = gaussian_rows(f"e4/mock-kernel/{slug}", 1, args.d, 1.0)[0]
        nrm = math.sqrt(sum(x * x for x in row))
        kernel[i] = np.asarray([x / nrm for x in row], dtype=np.float32)
    kfile = os.path.join("vectors", f"kernel-mock-d{args.d}.f32")
    kernel.tofile(os.path.join(args.out, kfile))

    shuffled = []
    for s in seeds:
        perm, label, redraws = derangement(f"e4/mock-shuffle/{s}", n)
        shuffled.append({"seed": s, "label": label, "redraws": redraws, "perm": perm})

    random_frozen = []
    for s in seeds:
        rows = np.asarray(gaussian_rows(f"e4/mock-randfrozen/{s}", n, args.d, INIT_STD),
                          dtype=np.float32)
        rfile = os.path.join("vectors", f"random-mock-d{args.d}-seed{s}.f32")
        rows.tofile(os.path.join(args.out, rfile))
        random_frozen.append({"seed": s, "label": f"e4/mock-randfrozen/{s}", "file": rfile,
                              "sha256": sha256_file(os.path.join(args.out, rfile))})

    manifest = {
        "artifact": "e4-vector-tables-MOCK",
        "mock": True,
        "note": "RUNNER SMOKE ONLY: authored rows copied from the E1 mock tables, synthetic "
                "rows random units; never use for a result",
        "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "D": args.d,
        "rows": n,
        "ids": ids,
        "slugs": slugs,
        "kernel": {"file": kfile, "sha256": sha256_file(os.path.join(args.out, kfile))},
        "shuffled": shuffled,
        "randomFrozen": random_frozen,
        "initStd": INIT_STD,
        "frozenScale": INIT_STD * math.sqrt(args.d),
    }
    mpath = os.path.join(args.out, "vector-tables-mock-manifest.json")
    with open(mpath, "w") as f:
        json.dump(manifest, f)
    print(f"wrote MOCK e4 tables (D={args.d}, {n} rows) -> {mpath}")


if __name__ == "__main__":
    main()
