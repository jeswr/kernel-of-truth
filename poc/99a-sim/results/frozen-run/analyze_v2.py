"""Characterize the v2 grid: OK/ERROR inventory + failure pattern + assemble
grid-results.json for verdict_99a.py.  Mechanical only; no scientific conclusion.
"""
import os
import json
import glob
from collections import Counter

D = "/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/results/frozen-run/grid-run-v2"
CELLS = os.path.join(D, "cells")

cells = []
for f in sorted(glob.glob(os.path.join(CELLS, "cell_*.json"))):
    cells.append(json.load(open(f)))

ok = [c for c in cells if "ERROR" not in c]
err = [c for c in cells if "ERROR" in c]


def desc(c):
    idx = c["config_index"]
    kind = c.get("_kind") or c.get("kind")
    label = c.get("label")
    rho = c.get("rho")
    regime = c.get("regime")
    n = (c.get("n_nat"), c.get("n_nonce"))
    return idx, kind, label, rho, regime, n


print(f"=== TOTAL {len(cells)} | OK {len(ok)} | ERROR {len(err)} ===\n")

# ---- ERROR signature ----
print("=== ERROR SIGNATURES (exact message) ===")
sigs = Counter(c["ERROR"] for c in err)
for s, n in sigs.most_common():
    print(f"  [{n}x] {s}")
print("\n=== ERROR fit-path frames (representative) ===")
if err:
    for ln in err[0].get("error_frames", []):
        print("   ", ln)
# distinct leading-minor numbers
import re
minors = Counter()
for c in err:
    m = re.search(r"(\d+)-th leading minor", c["ERROR"])
    if m:
        minors[m.group(1)] += 1
print("\n=== leading-minor distribution ===", dict(minors))

# ---- OK cells ----
print(f"\n=== OK cells ({len(ok)}) — which succeeded ===")
for c in sorted(ok, key=lambda x: x["config_index"]):
    idx, kind, label, rho, regime, n = desc(c)
    print(f"  idx {idx:3d} {kind:8s} {label:8s} rho={rho} regime={regime} n={n}")

# ---- ERROR pattern breakdown ----
print(f"\n=== ERROR pattern breakdown ({len(err)}) ===")
for key, fn in [("by kind", lambda c: desc(c)[1]),
                ("by label", lambda c: desc(c)[2]),
                ("by rho", lambda c: desc(c)[3]),
                ("by regime", lambda c: desc(c)[4]),
                ("by n", lambda c: str(desc(c)[5]))]:
    print(f"  {key}:")
    ec = Counter(fn(c) for c in err)
    oc = Counter(fn(c) for c in ok)
    keys = sorted(set(list(ec) + list(oc)), key=str)
    for k in keys:
        print(f"     {str(k):20s} ERROR={ec.get(k,0):3d}  OK={oc.get(k,0):3d}")

# ---- assemble grid-results.json ----
combined = {
    "note": "99a v2 durable grid (jesse-70413). 100/114 cells hit the frozen "
            "exact-REML LinAlgError at full R; 14 OK. Verdict on OK cells only.",
    "base_seed": 990066001, "n_cells": len(cells),
    "n_ok": len(ok), "n_error": len(err),
    "R_fwer": 40000, "R_power": 10000, "R_gatecal": 40000,
    "results": cells,
}
with open(os.path.join(D, "grid-results.json"), "w") as f:
    json.dump(combined, f, indent=2, default=str)
print(f"\nwrote {D}/grid-results.json ({len(cells)} cells)")

# fit-failure rate (S8 anticipates this)
print(f"\nfit-failure rate (cell-level): {len(err)}/{len(cells)} = {len(err)/len(cells):.4f}")
