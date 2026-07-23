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


@app.function(cpu=32.0, memory=16384, timeout=21600, volumes={"/vol": VOL}, retries=2)
def run_grid_batch(specs, n_workers: int = 30, R_override: int = 0):
    return _batch_impl(specs, n_workers, R_override or None)


@app.function(cpu=2.0, memory=2048, timeout=1800, volumes={"/vol": VOL})
def tiny_batch(specs, n_workers: int = 2, R_override: int = 50):
    return _batch_impl(specs, n_workers, R_override or None)


@app.function(volumes={"/vol": VOL})
def collect():
    """DECOUPLED collection: read all durable cell files from the Volume."""
    import os
    import json
    VOL.reload()
    out = []
    if os.path.isdir(CELLDIR):
        for f in sorted(os.listdir(CELLDIR)):
            if f.startswith("cell_") and f.endswith(".json"):
                out.append(json.load(open(os.path.join(CELLDIR, f))))
    return {"n_cells": len(out), "config_indices": sorted(c["config_index"] for c in out)}


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
def main(mode: str = "tinyvalidate"):
    """tinyvalidate: durable-write + resume-skip green test on 2 cells @ R=50."""
    import sys
    import json
    sys.path.insert(0, SIM_LOCAL)
    import grid
    cells = grid.enumerate_cells()
    by = {c[2]: c for c in cells}  # label -> first spec
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
