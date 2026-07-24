"""CORRECTED 99a full-grid harness (v2) — TOTAL-LOSS-PROOF + churn-resistant.

Fixes the v1 failure modes (post-mortem 2026-07-23):
  * v1 died when the Modal workspace was disabled mid-run; `order_outputs=True`
    held ALL completed cells in the live client's reorder buffer, so the crash
    lost ~71 buffered cells (finish-or-lose trap).
  * v1 ran 100 preemptible cpu=1 containers -> heavy CPU-preemption churn +
    ~2.4x slowdown + retry restarts.

v2 design:
  * DURABLE per-cell writes to a Modal Volume (`kot-99a-grid-vol`) keyed by
    config_index, COMMITTED after every cell -> results survive any client/app
    death.  Collection is DECOUPLED from the run (a separate `collect` reads the
    Volume), so a driver death never loses completed cells.
  * RESUMABLE: (re)launch reads the Volume, skips already-written cells, runs
    only the remainder -> a preemption just resumes.
  * CHURN-FREE: ONE many-core container (cpu=N) runs the cells with an
    in-container process Pool (BLAS threads pinned to 1/worker), so each cell
    runs at ~bench rate on a dedicated core with no 100-container contention.
    README intended path: ~32-64 cores, ~1.7-3.4h, ~108.7 core-h total.

The frozen SCIENCE is unchanged: same pinned image, same operative modules under
/root/sim (driver -> pipeline -> reml_composite exact-REML A+B, gate-cal battery,
rung0). This file is OPUS operational code (fan-out + durability only).
"""
import modal

SIM_LOCAL = "/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim"
VOL = modal.Volume.from_name("kot-99a-grid-vol", create_if_missing=True)

image = (
    modal.Image.from_registry("rocker/r-ver:4.4.1", add_python="3.12")
    .pip_install("numpy==2.1.3", "scipy==1.14.1")
    .run_commands(
        "R -q -e \"install.packages('remotes')\"",
        "R -q -e \"remotes::install_version('lme4', version='1.1-35.5', upgrade='never', dependencies=TRUE)\"",
        "R -q -e \"remotes::install_version('lmerTest', version='3.1-3', upgrade='never', dependencies=TRUE)\"",
    )
    .add_local_dir(
        SIM_LOCAL, remote_path="/root/sim",
        ignore=["venv/**", "__pycache__/**", "*.pyc", "results/**", ".git/**"],
    )
)
app = modal.App("kot-99a-grid-v2", image=image)

CELLDIR = "/vol/cells"


def _compute_cell(arg):
    """Top-level worker (picklable): compute ONE cell.  arg = (spec, R_override).
    R_override (int|None): if set, use it for ALL kinds (tiny validation); else
    the frozen R (FWER/gatecal 40000, power 10000)."""
    import os
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[v] = "1"
    import sys
    import time
    if "/root/sim" not in sys.path:
        sys.path.insert(0, "/root/sim")
    os.chdir("/root/sim")
    import traceback
    import grid
    import driver
    import rung0
    import pins
    import gate_cal_battery as gcb
    spec, R_override = arg
    idx, kind, label, rho, regime, n_nat, n_nonce = spec
    R_fwer = R_override if R_override else pins.R_FWER
    R_power = R_override if R_override else pins.R_POWER
    t0 = time.time()
    # CELL-LEVEL EXCEPTION ISOLATION (restores v1 return_exceptions behaviour):
    # a cell that raises (e.g. the frozen exact-REML estimator's LinAlgError on
    # some rep at full R) is recorded DURABLY as an ERROR cell so the batch keeps
    # going and passing cells still bank.  This does NOT alter the science: a
    # failed cell is marked unevaluable (fit-failure), NEVER pass/fail; how to
    # handle such a rep is a Fable design decision (S8 "fit-failure rates").
    try:
        if kind == "gatecal":
            res = gcb.run_cell(rho, n_nonce, R_fwer)
            res["_kind"] = "gatecal"
            res["config_index"] = idx
            res["label"] = label
        else:
            t = grid.resolve_cell(label, rho, regime, n_nat, n_nonce, kind=kind)
            if kind == "fwer":
                res = driver.run_cell(idx, t, R=R_fwer, want_paths=False)
                if label == "F10":
                    res["rung0"] = rung0.run_rung0_cell(idx, t, R=R_fwer)
            else:
                res = driver.run_cell(idx, t, R=R_power, want_paths=True)
                if label == "P6":
                    res["rung0"] = rung0.run_rung0_cell(idx, t, R=R_power)
            res["_kind"] = kind
            res["regime"] = regime
        res["_wall_s"] = time.time() - t0
        return res
    except Exception as e:
        frames = [ln.strip() for ln in traceback.format_exc().splitlines()
                  if ("reml_composite" in ln or "pipeline" in ln or "driver" in ln
                      or "gate" in ln or "Error" in ln)]
        return {"config_index": idx, "_kind": kind, "label": label, "rho": rho,
                "regime": regime, "n_nat": n_nat, "n_nonce": n_nonce,
                "ERROR": f"{type(e).__module__}.{type(e).__name__}: {e}",
                "error_frames": frames[-8:], "_wall_s": time.time() - t0}


def _batch_impl(specs, n_workers, R_override):
    """Run remaining cells with an in-container Pool; DURABLE per-cell Volume
    writes committed after each cell; RESUMABLE via the Volume."""
    import os
    import json
    import multiprocessing as mp
    os.makedirs(CELLDIR, exist_ok=True)
    VOL.reload()
    done = set()
    for f in os.listdir(CELLDIR):
        if f.startswith("cell_") and f.endswith(".json"):
            try:
                done.add(int(f[5:8]))
            except ValueError:
                pass
    todo = [(tuple(s), R_override) for s in specs if s[0] not in done]
    ran = []
    if todo:
        ctx = mp.get_context("spawn")
        with ctx.Pool(n_workers) as pool:
            for res in pool.imap_unordered(_compute_cell, todo):
                idx = res["config_index"]
                with open(os.path.join(CELLDIR, f"cell_{idx:03d}.json"), "w") as fh:
                    json.dump(res, fh, default=str)
                VOL.commit()                       # DURABLE after EVERY cell
                ran.append(idx)
                print(f"[{len(ran)}/{len(todo)}] durable-wrote cell {idx} "
                      f"({res.get('_kind')} {res.get('label')})", flush=True)
    return {"done_before": sorted(done), "ran": sorted(ran), "n_total": len(specs)}


@app.function(cpu=32.0, memory=32768, timeout=28800, volumes={"/vol": VOL}, retries=2)
def run_grid_batch(specs, n_workers: int = 30, R_override: int = 0):
    return _batch_impl(specs, n_workers, R_override or None)


@app.function(cpu=2.0, memory=2048, timeout=1800, volumes={"/vol": VOL})
def tiny_batch(specs, n_workers: int = 2, R_override: int = 50):
    return _batch_impl(specs, n_workers, R_override or None)


@app.function(volumes={"/vol": VOL})
def collect(full: bool = False):
    """DECOUPLED collection: read all durable cell files from the Volume."""
    import os
    import json
    VOL.reload()
    out = []
    if os.path.isdir(CELLDIR):
        for f in sorted(os.listdir(CELLDIR)):
            if f.startswith("cell_") and f.endswith(".json"):
                out.append(json.load(open(os.path.join(CELLDIR, f))))
    res = {"n_cells": len(out), "config_indices": sorted(c["config_index"] for c in out)}
    if full:
        res["cells"] = out
    return res


@app.function(cpu=8.0, timeout=3600)
def repro_frozen(labels: str = "", R: int = 8000, pin_threads: int = 1):
    """Instrument-check on the PINNED image (numpy 2.1.3), FROZEN path only
    (pipeline -> reml_composite; NO harness Pool).  Reproduces the crash
    condition (BLAS threads=1 by default) and COUNTS the per-cell raise RATE over
    R reps (does NOT break on first) -> quantifies scope (rare vs pervasive)."""
    import os
    if pin_threads:
        for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                  "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
            os.environ[v] = str(pin_threads)
    import sys
    import traceback
    if "/root/sim" not in sys.path:
        sys.path.insert(0, "/root/sim")
    os.chdir("/root/sim")
    import numpy
    import scipy
    import grid
    import seeds
    import pipeline
    import dgm
    cells = grid.enumerate_cells()
    want = set(labels.split(",")) if labels else None
    # representative sample: 3 power + 3 FWER cells spanning rho/n-levels
    sample_idx = {74, 79, 91, 0, 27, 42} if want is None else None
    scan = [c for c in cells if (c[2] in want if want else c[0] in sample_idx)]
    out = {"numpy": numpy.__version__, "scipy": scipy.__version__, "R": R,
           "pin_threads": pin_threads, "cells": []}
    for (idx, kind, label, rho, regime, n_nat, n_nonce) in scan:
        t = grid.resolve_cell(label, rho, regime, n_nat, n_nonce, kind=kind)
        thr = dgm.compute_gate_thresholds(t, idx)
        n_raise = 0
        first = None
        for r in range(R):
            ss = seeds.rep_substreams(idx, r)
            try:
                pipeline.run_replication(t, ss, gate_thr=thr)
            except Exception as e:
                n_raise += 1
                if first is None:
                    frames = [ln.strip() for ln in traceback.format_exc().splitlines()
                              if ("reml_composite" in ln or "pipeline" in ln
                                  or "Error" in ln)]
                    first = {"rep": r, "error": f"{type(e).__module__}.{type(e).__name__}: {e}",
                             "frames": frames[-5:]}
        out["cells"].append({"config_index": idx, "kind": kind, "label": label,
                             "rho": rho, "n": [n_nat, n_nonce], "R": R,
                             "n_raise": n_raise, "raise_rate": n_raise / R, "first": first})
    return out


@app.function(volumes={"/vol": VOL})
def clear_vol():
    """Wipe the Volume cells dir (for a clean tiny-validation reset)."""
    import os
    import shutil
    VOL.reload()
    if os.path.isdir(CELLDIR):
        shutil.rmtree(CELLDIR)
    os.makedirs(CELLDIR, exist_ok=True)
    VOL.commit()
    return {"cleared": True}


@app.local_entrypoint()
def main(mode: str = "tinyvalidate", repro_r: int = 3000):
    """tinyvalidate: durable-write + resume-skip green test on 2 cells @ R=50."""
    import sys
    import json
    sys.path.insert(0, SIM_LOCAL)
    import grid
    cells = grid.enumerate_cells()
    by = {c[2]: c for c in cells}  # label -> first spec
    if mode == "repro":
        print(json.dumps(repro_frozen.remote("", repro_r), indent=2, default=str))
        return
    if mode == "tinyvalidate":
        tiny = [list(by["F3"]), list(by["P3"])]  # one FWER + one power cell
        print("clearing volume ...", flush=True)
        print(json.dumps(clear_vol.remote()))
        print("RUN 1 (should compute both) ...", flush=True)
        r1 = tiny_batch.remote(tiny, 2, 50)
        print(json.dumps(r1))
        print("COLLECT (durable check) ...", flush=True)
        c1 = collect.remote()
        print(json.dumps(c1))
        print("RUN 2 (should SKIP both = resume) ...", flush=True)
        r2 = tiny_batch.remote(tiny, 2, 50)
        print(json.dumps(r2))
        ok = (sorted(r1["ran"]) == sorted(c1["config_indices"])
              and r2["ran"] == [] and sorted(r2["done_before"]) == sorted(r1["ran"]))
        print("TINY-VALIDATION:", "GREEN" if ok else "RED", flush=True)
    elif mode == "full":
        import os

        def _est(c):
            # est core-seconds: SHORTEST first -> cells bank early (crash-resilient
            # + real progress signal). Power R=10k < gate-cal/FWER R=40k; esc last.
            idx, kind, label, rho, regime, n_nat, n_nonce = c
            R = 10000 if kind == "power" else 40000
            per = 0.131 if (n_nat, n_nonce) == (96, 160) else 0.094
            return R * per
        specs = [list(c) for c in sorted(cells, key=_est)]
        print(f"[v2-full] launching {len(specs)} cells (SHORTEST-first) on ONE "
              f"cpu=32 container (durable Volume kot-99a-grid-vol, resumable) ...",
              flush=True)
        try:
            summary = run_grid_batch.remote(specs, 30, 0)
            print("[v2-full] run_grid_batch summary:", json.dumps(summary), flush=True)
        except Exception as e:
            print("[v2-full] run_grid_batch raised (completed cells still durable "
                  "in Volume; resume by re-running):", repr(e), flush=True)
        # collect from the durable Volume regardless of the run outcome
        c = collect.remote(True)
        print(f"[v2-full] collected {c['n_cells']} cells from Volume", flush=True)
        outdir = os.path.join(SIM_LOCAL, "results", "frozen-run", "grid-run-v2")
        os.makedirs(outdir, exist_ok=True)
        combined = {
            "note": "99a frozen full-grid raw results (v2 durable harness, jesse-70413). "
                    "Mechanical verdict via verdict_99a.py.",
            "base_seed": 990066001, "n_cells": c["n_cells"],
            "config_indices": c["config_indices"],
            "R_fwer": 40000, "R_power": 10000, "R_gatecal": 40000,
            "results": c.get("cells", []),
        }
        with open(os.path.join(outdir, "grid-results.json"), "w") as f:
            json.dump(combined, f, indent=2, default=str)
        print(f"[v2-full] WROTE {outdir}/grid-results.json ({c['n_cells']}/114 cells)", flush=True)
