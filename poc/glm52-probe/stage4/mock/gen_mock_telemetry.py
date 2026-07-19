#!/usr/bin/env python3
"""gen_mock_telemetry.py — SYNTHETIC kot-s4tel/1 telemetry for the glm-s4drop-0
FULL-SCALE green mock (never a run input; the real telemetry is produced by the
runner's T-build phase and pinned by ops amendment, ASM-2385).

Deterministic (SHA-256 over fixed labels only). Spans the FULL registered cell
universe: 76 MoE layers 3..78 INCLUSIVE x 256 experts (ASM-2342 measured
correction; cross-model review 2026-07-16 finding C1 — the pre-review mock
spanned only 3..77). Cost distribution: a heavy rare tail (most miss bytes on
low-selection cells), a small always-resident head (zero miss), mimicking the
cache-constrained box.

    python3 gen_mock_telemetry.py          # rewrites mock_telemetry.json
"""
import hashlib, json, os

LAYERS = range(3, 79)      # 76 MoE layers, 3..78 (ASM-2342)
N_EXPERTS = 256
BYTES_PER_EXPERT = 19000000
DECODE_TOKENS = 3072
SEED = "glm-s4drop-0:mock-telemetry:20260716"


def h(cell: str, tag: str) -> int:
    return int(hashlib.sha256(("%s:%s:%s" % (SEED, cell, tag)).encode()).hexdigest(), 16)


def main():
    cells = {}
    for L in LAYERS:
        for E in range(N_EXPERTS):
            c = "main|%d|%d" % (L, E)
            r = h(c, "sel") % 100
            if r < 10:                     # unseen in T-build: zero everything
                sel, miss = 0, 0
            elif r < 40:                   # rare: low sel, full miss per selection
                sel = 1 + h(c, "s2") % 4
                miss = sel * BYTES_PER_EXPERT
            elif r < 90:                   # mid: partially cached
                sel = 5 + h(c, "s3") % 40
                miss = (sel * BYTES_PER_EXPERT * (h(c, "m") % 60)) // 100
            else:                          # hot head: resident, no misses
                sel = 60 + h(c, "s4") % 400
                miss = 0
            cells[c] = {"sel": sel, "bytes": BYTES_PER_EXPERT, "miss_bytes": miss}
    tel = {"_schema": "kot-s4tel/1", "tier": "M", "decode_tokens": DECODE_TOKENS,
           "split": "T-build",
           "_note": "SYNTHETIC mock telemetry (green-mock only, never a run input)",
           "cells": cells}
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_telemetry.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(tel, f, sort_keys=True)
    total = sum(v["miss_bytes"] for v in cells.values()) / DECODE_TOKENS
    print("cells=%d layers=%d..%d total_miss_bytes_per_tok=%.4g"
          % (len(cells), min(LAYERS), max(LAYERS), total))


if __name__ == "__main__":
    main()
