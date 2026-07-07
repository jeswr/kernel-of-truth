#!/usr/bin/env python3
"""Mock vector tables for the E1 smoke test ONLY (bead kernel-of-truth-bk0).

The real tables (inputs/vector-tables-d512.json) are pinned to kot-enc-Bq/1
@D=512, which fails closed at any other dimension — the CPU mock runs at
d_model=64, so it gets clearly-stamped MOCK tables with the same schema:
random unit-norm rows in place of kernel vectors (content-free by
construction; the smoke test checks MECHANICS — pipeline plumbing and
freezing-mask bit-identity — never content claims). Deterministic via the
same DetStream labels as the real generator, so reruns are byte-identical.
"""

import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E1_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from detstream import DetStream, det_permutation  # noqa: E402

INIT_STD = 0.02


def gaussian_rows(label, rows, cols, std):
    s = DetStream(label)
    out = []
    spare = [None]

    def nxt():
        if spare[0] is not None:
            v = spare[0]
            spare[0] = None
            return v
        u1 = 1 - s.next_float()
        u2 = s.next_float()
        r = math.sqrt(-2 * math.log(u1))
        spare[0] = r * math.sin(2 * math.pi * u2)
        return r * math.cos(2 * math.pi * u2)

    for _ in range(rows):
        out.append([nxt() * std for _ in range(cols)])
    return out


def derangement(base_label, n):
    attempt = 0
    while True:
        label = base_label if attempt == 0 else f"{base_label}/retry{attempt}"
        p = det_permutation(label, n)
        if all(v != i for i, v in enumerate(p)):
            return p, label, attempt
        attempt += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--d", type=int, default=64)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", default="0,1,2,3,4")
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]

    with open(os.path.join(E1_DIR, "inputs", "cloze-templates.json")) as f:
        slugs = [c["slug"] for c in json.load(f)["concepts"]]
    ids = [f"urn:kernel-v0:{s}" for s in slugs]
    n = len(ids)

    kernel = []
    for i, slug in enumerate(slugs):
        row = gaussian_rows(f"e1/mock-kernel/{slug}", 1, args.d, 1.0)[0]
        nrm = math.sqrt(sum(x * x for x in row))
        kernel.append([x / nrm for x in row])

    shuffled = []
    for s in seeds:
        perm, label, redraws = derangement(f"e1/mock-shuffle/{s}", n)
        shuffled.append({"seed": s, "label": label, "redraws": redraws, "perm": perm})

    random_frozen = [{"seed": s, "label": f"e1/mock-randfrozen/{s}",
                      "rows": gaussian_rows(f"e1/mock-randfrozen/{s}", n, args.d, INIT_STD)}
                     for s in seeds]

    with open(args.out, "w") as f:
        json.dump({
            "artifact": "e1-vector-tables-MOCK",
            "mock": True,
            "note": "SMOKE-TEST ONLY: random unit rows, not kernel vectors; never use for a result",
            "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "D": args.d,
            "initStd": INIT_STD,
            "frozenScale": INIT_STD * math.sqrt(args.d),
            "ids": ids,
            "kernel": kernel,
            "kernelInit": {"tableRef": "kernel"},
            "shuffled": shuffled,
            "randomFrozen": random_frozen,
        }, f)
    print(f"wrote MOCK tables (D={args.d}) -> {args.out}")


if __name__ == "__main__":
    main()
