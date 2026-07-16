#!/usr/bin/env python3
"""Regression proof for the GPT-5.6 RUN-HOLD CRITICAL geometry defect (f1k).

Demonstrates, MEASURED, that the superseded pinned analysis
(sha 9d01468e..., the 2026-07-15 REVISION-6 freeze) accepted OUT-OF-GEOMETRY
data to a valid PASS — a 97-cluster universe at n = 1573 satisfied the
>=-form power gate (c_ge8 = 97 >= 96) with every gate valid and
pass_gate=true — and that the fixed analysis/f1k.py rejects the identical
input fail-closed (ERR_P2_ANALYSIS, exit 1).

Usage:  git show <old-commit>:analysis/f1k.py > /tmp/f1k_old.py
        python3 tools/registry/_f1k_geometry_regress_20260715.py /tmp/f1k_old.py

Build artifact for the correction record
registry/corrections/f1k/1-prefreeze-correction.json; never pinned.
"""
import importlib.util
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    old = load("f1k_old", sys.argv[1])
    new = load("f1k_new", ROOT / "analysis" / "f1k.py")
    rng = random.Random(4242)
    rows = new._mock_campaign({"b0": 0.70, "d0": 0.70, "d1-drng": 0.70,
                               "d2": 0.70, "d3-text": 0.71, "K": 0.80}, rng)
    rows97 = [dict(r, cluster="c-096")
              if r["item_id"].startswith("it-000-0") else r for r in rows]
    assert len({r["cluster"] for r in rows97}) == 97
    assert len({r["item_id"] for r in rows97}) == 1573
    out = old.analyze(rows97, old._mock_sidecar())
    print("OLD: 97 clusters @ n=1573 -> power_gate_valid=%s all_gates=%s "
          "pass_gate=%s (the RUN-HOLD exploit)"
          % (out["gates"]["power_gate_valid"], all(out["gates"].values()),
             out["analysis"]["pass_gate"]))
    assert out["gates"]["power_gate_valid"] and out["analysis"]["pass_gate"]
    try:
        new.analyze(rows97, new._mock_sidecar())
    except SystemExit as e:
        assert e.code == 1
        print("NEW: identical input REJECTED fail-closed (exit 1, "
              "ERR_P2_ANALYSIS) — defect closed")
        return 0
    print("NEW: NOT REJECTED — FIX ABSENT", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
