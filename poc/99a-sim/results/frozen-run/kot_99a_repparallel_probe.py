"""OPUS rep-parallel BIT-IDENTITY + TIMING probe (opus-runner-1, 2026-07-25).

Coordinator-directed re-plan: the hardened exact-REML estimator now does REAL
work (~1.6 s/rep), so the R reps of a cell must be parallelised WITHIN the cell.
The reps are INDEPENDENT (each a fresh registered-seeded dataset + one fit; S2
guarantees per-rep reproducibility independent of execution order).  This probe:

  1. proves BIT-IDENTITY: for one FWER + one power cell at R, the rep-parallel
     path (driver.run_one_rep across workers, round-robin rep assignment so reps
     are computed genuinely OUT OF ORDER, then driver.aggregate_cell) produces a
     cell record BYTE-IDENTICAL (all science fields; the two execution-dependent
     TIMING fields excluded) to the sequential driver.run_cell.
  2. measures TIMING: single-core seq s/rep + n_worker parallel throughput +
     parallel efficiency, on the PINNED image (numpy 2.1.3), to re-estimate the
     full-grid wall-clock.
  3. measures rung0 cost (F10/P6 cells call rung0.run_rung0_cell separately; it
     uses the closed-form FamilyAnova, NOT the exact-REML fit — expected cheap).

Runs the FROZEN science modules under /root/sim UNCHANGED (driver refactor is a
proven-bit-identical relocation).  This file is OPUS operational code (rep-level
fan-out only).  No Volume / no durable writes / NOT the full run.
"""
import modal

SIM_LOCAL = "/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim"

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
app = modal.App("kot-99a-repparallel-probe", image=image)

_BLAS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
         "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")


def _rep_chunk_worker(arg):
    """Top-level picklable worker: compute run_one_rep for a LIST of rep indices.
    Sets BLAS threads=1 BEFORE importing numpy (via driver); resolves t + gate_thr
    ONCE per chunk (deterministic -> bit-identical to run_cell's single compute)."""
    import os
    for v in _BLAS:
        os.environ[v] = "1"
    import sys
    if "/root/sim" not in sys.path:
        sys.path.insert(0, "/root/sim")
    os.chdir("/root/sim")
    import grid
    import dgm
    import driver
    (config_index, kind, label, rho, regime, n_nat, n_nonce,
     want_paths, use_futility, use_rung0, rep_list) = arg
    t = grid.resolve_cell(label, rho, regime, n_nat, n_nonce, kind=kind)
    gate_thr = dgm.compute_gate_thresholds(t, config_index)
    return [(r, driver.run_one_rep(config_index, t, r, gate_thr, want_paths,
                                   use_futility, use_rung0)) for r in rep_list]


def rep_parallel_cell(spec, R, n_workers, want_paths,
                      use_futility=True, use_rung0=True):
    """Rep-parallel executor for ONE cell (OPUS operational fan-out).  spec =
    (config_index, kind, label, rho, regime, n_nat, n_nonce).  Round-robin rep
    assignment across n_workers -> reps computed genuinely out of order; results
    re-indexed by rep and fed to driver.aggregate_cell (order-invariant).  ONE
    parallelism level (rep-level); BLAS threads pinned to 1/worker."""
    import time
    import multiprocessing as mp
    import grid
    import driver
    config_index, kind, label, rho, regime, n_nat, n_nonce = spec
    # round-robin chunks: worker w gets reps w, w+nw, w+2nw, ...
    chunks = [[] for _ in range(n_workers)]
    for r in range(R):
        chunks[r % n_workers].append(r)
    args = [(config_index, kind, label, rho, regime, n_nat, n_nonce,
             want_paths, use_futility, use_rung0, rl) for rl in chunks if rl]
    t = grid.resolve_cell(label, rho, regime, n_nat, n_nonce, kind=kind)
    outcomes = [None] * R
    t0 = time.time()
    ctx = mp.get_context("spawn")
    with ctx.Pool(n_workers) as pool:
        for chunk_res in pool.imap_unordered(_rep_chunk_worker, args):
            for (r, o) in chunk_res:
                outcomes[r] = o
    elapsed = time.time() - t0
    assert all(o is not None for o in outcomes), "missing rep outcome"
    return driver.aggregate_cell(config_index, t, R, outcomes, want_paths, elapsed)


def _science_only(rec):
    """Cell record minus the two execution-dependent TIMING fields (NOT science)."""
    return {k: v for k, v in rec.items() if k not in ("elapsed_s", "sec_per_rep")}


def _first_mismatch(a, b, path=""):
    """Return a human list of the first differing science leaves (a=seq, b=par)."""
    import math
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        ka, kb = set(a), set(b)
        if ka != kb:
            out.append(f"{path}: keys differ +{sorted(kb-ka)} -{sorted(ka-kb)}")
        for k in sorted(ka & kb):
            out += _first_mismatch(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: len {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            out += _first_mismatch(x, y, f"{path}[{i}]")
    else:
        eq = (a == b) or (isinstance(a, float) and isinstance(b, float)
                          and math.isnan(a) and math.isnan(b))
        if not eq:
            out.append(f"{path}: {a!r} != {b!r}")
    return out[:20]


@app.function(cpu=8.0, memory=16384, timeout=3600)
def bitident_and_timing(fwer_label: str = "F1", power_label: str = "P1",
                        reps: int = 200, n_workers: int = 8,
                        escalated: bool = False):
    """SEQ (driver.run_cell, single core) vs PAR (rep_parallel_cell) on one FWER
    + one power cell; report bit-identity (science fields) + timing/efficiency +
    rung0 cost.  escalated=True selects the first n_nonce==160 cell of each kind
    (the expensive escalated-n sizing point) instead of the first base-n cell."""
    R = reps
    import os
    for v in _BLAS:
        os.environ[v] = "1"
    import sys
    import time
    if "/root/sim" not in sys.path:
        sys.path.insert(0, "/root/sim")
    os.chdir("/root/sim")
    import numpy
    import scipy
    import grid
    import driver
    import rung0
    cells = grid.enumerate_cells()
    by = {}
    for c in cells:
        by.setdefault(c[2], c)             # first spec per label
    first_of_kind = {}
    for c in cells:
        first_of_kind.setdefault(c[1], c)  # first spec per kind (fallback)
    first_esc_of_kind = {}
    for c in cells:
        if c[6] == 160:                    # n_nonce == 160 -> escalated-n
            first_esc_of_kind.setdefault(c[1], c)
    out = {"numpy": numpy.__version__, "scipy": scipy.__version__,
           "R": R, "n_workers": n_workers, "escalated": escalated, "cells": {}}
    picks = [(fwer_label, "fwer"), (power_label, "power")]
    for label, kind_hint in picks:
        if escalated:
            spec_c = first_esc_of_kind[kind_hint]
        else:
            spec_c = by.get(label) or first_of_kind[kind_hint]
        idx, kind, lab, rho, regime, n_nat, n_nonce = spec_c
        t = grid.resolve_cell(lab, rho, regime, n_nat, n_nonce, kind=kind)
        want_paths = (kind == "power")
        spec = (idx, kind, lab, rho, regime, n_nat, n_nonce)
        # SEQ reference (single-core, in-process) = the frozen science
        t0 = time.time()
        ref = driver.run_cell(idx, t, R, want_paths=want_paths)
        seq_s = time.time() - t0
        # PAR (rep-parallel, round-robin, n_workers)
        par = rep_parallel_cell(spec, R, n_workers, want_paths)
        par_s = par["elapsed_s"]
        mism = _first_mismatch(_science_only(ref), _science_only(par))
        # rung0 cost probe (F10/P6 cells call this separately; cheap FamilyAnova)
        rung0_s = None
        t0 = time.time()
        _ = rung0.run_rung0_cell(idx, t, R=min(R, 200))
        rung0_s = time.time() - t0
        out["cells"][lab] = {
            "kind": kind, "idx": idx, "rho": rho, "regime": regime,
            "n": [n_nat, n_nonce], "want_paths": want_paths,
            "bit_identical": (len(mism) == 0),
            "mismatches": mism,
            "fwer_events": ref["fwer_events"],
            "fit_failures": ref["fit_failures"],
            "fit_failure_rate": ref["fit_failure_rate"],
            "seq_s": seq_s, "seq_s_per_rep": seq_s / R,
            "par_s": par_s, "par_s_per_rep": par_s / R,
            "speedup": seq_s / par_s if par_s else None,
            "efficiency_vs_nworkers": (seq_s / par_s / n_workers) if par_s else None,
            "rung0_s_per_rep": rung0_s / min(R, 200),
        }
    return out


@app.function(cpu=2.0, memory=4096, timeout=600)
def fitfail_order_test(R: int = 500):
    """MEASURED check of the ONE order-sensitive field (fit_failure_detail, cap
    50 in rep order).  Synthetic outcomes (NO fits): mark a scattered set of >50
    rep indices as fit-failures, feed to driver.aggregate_cell in (a) natural
    r-order and (b) a SHUFFLED-then-r-reindexed list (mimicking out-of-order
    parallel reassembly).  Both must yield fit_failure_detail == the 50 SMALLEST
    failing rep indices, and identical n_fitfail — proving the cap+ordering is
    invariant to computation order."""
    import os
    for v in _BLAS:
        os.environ[v] = "1"
    import sys
    import random
    if "/root/sim" not in sys.path:
        sys.path.insert(0, "/root/sim")
    os.chdir("/root/sim")
    import grid
    import driver
    cells = grid.enumerate_cells()
    idx, kind, label, rho, regime, n_nat, n_nonce = next(c for c in cells if c[1] == "fwer")
    t = grid.resolve_cell(label, rho, regime, n_nat, n_nonce, kind=kind)
    fails = set(range(2, R, 7))            # scattered, > 50 of them
    def _mk():
        out = [None] * R
        for r in range(R):
            if r in fails:
                out[r] = {"fitfail": {"family": "COMP", "stage": "fit",
                                      "error": f"synthetic@{r}"}}
            else:
                out[r] = {"rejected": set(), "stage2": False}
        return out
    a = driver.aggregate_cell(idx, t, R, _mk(), want_paths=False)
    # (b): build via a shuffled worker-order then r-reindex (as rep_parallel does)
    order = list(range(R)); random.Random(123).shuffle(order)
    scratch = _mk()
    reindexed = [None] * R
    for r in order:
        reindexed[r] = scratch[r]
    b = driver.aggregate_cell(idx, t, R, reindexed, want_paths=False)
    exp_reps = sorted(fails)[:50]
    ok = (a["fit_failures"] == len(fails) == b["fit_failures"]
          and [d["rep"] for d in a["fit_failure_detail"]] == exp_reps
          and [d["rep"] for d in b["fit_failure_detail"]] == exp_reps
          and a["fit_failure_detail"] == b["fit_failure_detail"])
    return {"R": R, "n_fails_injected": len(fails),
            "n_fitfail_a": a["fit_failures"], "n_fitfail_b": b["fit_failures"],
            "detail_reps_a": [d["rep"] for d in a["fit_failure_detail"]],
            "expected_first50": exp_reps,
            "fitfail_order_invariant": ok}


@app.local_entrypoint()
def main(fwer_label: str = "F1", power_label: str = "P1",
         reps: int = 200, n_workers: int = 8, escalated: bool = False,
         mode: str = "bitident"):
    import json
    if mode == "fitfail":
        print(json.dumps(fitfail_order_test.remote(500), indent=2, default=str))
        return
    res = bitident_and_timing.remote(fwer_label, power_label, reps, n_workers,
                                     escalated)
    print(json.dumps(res, indent=2, default=str))
    allok = all(c["bit_identical"] for c in res["cells"].values())
    print("BIT-IDENTITY:", "GREEN (seq==par on all science fields)" if allok
          else "RED (mismatch — see 'mismatches')")
