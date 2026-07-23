"""OPUS local orchestrator for the 99a FULL frozen grid (experiment-runner).

Fans grid.enumerate_cells() (114 cells: 74 FWER R=40,000 + 36 power R=10,000 +
4 gate-cal R=40,000) across Modal via run_cell_job.map, ONE container per cell,
with incremental per-cell persistence + a combined results file.  Pure
collection: the science is the frozen modules under /root/sim.

Seeds: the frozen Philox map (pins.BASE_SEED=990066001; SeedSequence([BASE_SEED,
config_index, replication_index]).spawn(13)); beta-cal stream
SeedSequence([BASE_SEED, config_index, 999_999_999]).  Fully determined by the
config_index (0..113) and replication_index; registered in the run-log.

Run (creds already sourced into env; NEVER printed):
  ./venv/bin/python results/frozen-run/grid_driver.py
"""
import sys
import os
import json
import time

SIM = "/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim"
sys.path.insert(0, SIM)
sys.path.insert(0, os.path.join(SIM, "results", "frozen-run"))

import grid  # noqa: E402
from kot_99a_grid import app, run_cell_job  # noqa: E402

OUTDIR = os.path.join(SIM, "results", "frozen-run", "grid-run")
CELLDIR = os.path.join(OUTDIR, "cells")
os.makedirs(CELLDIR, exist_ok=True)

cells = grid.enumerate_cells()
specs = [tuple(c) for c in cells]
print(f"[grid_driver] {len(specs)} cells; launching Modal map ...", flush=True)

t0 = time.time()
results = {}
errors = {}
with app.run():
    for spec, res in zip(
        specs,
        run_cell_job.map(specs, order_outputs=True, return_exceptions=True),
    ):
        idx = spec[0]
        kind, label = spec[1], spec[2]
        if isinstance(res, Exception):
            rec = {"config_index": idx, "spec": list(spec), "ERROR": repr(res)}
            errors[idx] = repr(res)
        else:
            rec = res
        with open(os.path.join(CELLDIR, f"cell_{idx:03d}.json"), "w") as f:
            json.dump(rec, f, indent=2, default=str)
        results[idx] = rec
        # progress line with the key acceptance quantity
        key = ""
        if "ERROR" in rec:
            key = "ERROR " + rec["ERROR"][:120]
        elif kind == "fwer":
            key = f"fwer_hat={rec.get('fwer_hat')} cp_up={rec.get('fwer_cp_upper95')}"
        elif kind == "power":
            p = rec.get("paths", {})
            key = "paths=" + ",".join(
                f"{k}:{v.get('rate')}" for k, v in p.items() if isinstance(v, dict) and "rate" in v)
        elif kind == "gatecal":
            key = f"min_sd={min(a['sd_ratio'] for a in rec['arms'].values()):.3f}"
        print(f"[{len(results)}/{len(specs)}] idx={idx:3d} {kind:8s} {label:8s} "
              f"rho={spec[3]} n=({spec[5]},{spec[6]}) reg={spec[4]:8s} {key}",
              flush=True)

elapsed = time.time() - t0
combined = {
    "note": "99a frozen full-grid raw results (OPUS experiment-runner). "
            "Mechanical per-cell acceptance computed by verdict_99a.py.",
    "base_seed": 990066001,
    "n_cells": len(results),
    "n_errors": len(errors),
    "errors": errors,
    "elapsed_s": elapsed,
    "R_fwer": 40000, "R_power": 10000, "R_gatecal": 40000,
    "results": [results[i] for i in sorted(results)],
}
with open(os.path.join(OUTDIR, "grid-results.json"), "w") as f:
    json.dump(combined, f, indent=2, default=str)
print(f"[grid_driver] DONE {len(results)} cells, {len(errors)} errors, "
      f"{elapsed:.0f}s -> {os.path.join(OUTDIR, 'grid-results.json')}", flush=True)
