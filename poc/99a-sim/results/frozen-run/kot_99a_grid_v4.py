"""99a full-grid harness v4 — REP-PARALLEL, cell-per-container (opus-runner-1).

Coordinator-confirmed Option A re-plan (2026-07-25): the hardened exact-REML
estimator does REAL work (~0.6-0.86 s/rep on the pinned image), so the reps of a
cell are parallelised WITHIN the cell.  Topology:

  * LEVEL 1: Modal .map over the 114 cells -> ONE container per cell
    (cpu=8, order_outputs=False, timeout=28800s/8h, retries=2).
  * LEVEL 2: WITHIN each container, rep_parallel_cell runs the cell's R reps
    across 8 workers (BLAS threads pinned to 1/worker; workers <= cores -> NO
    oversubscription); F10/P6 add the SEQUENTIAL closed-form rung0; gate-cal via
    the existing bootstrap battery (no exact-REML).

Bit-identity: the rep-parallel path is BYTE-IDENTICAL (all science fields) to the
sequential driver.run_cell — proven on the pinned image (base + escalated cells)
+ fit_failure_detail order-invariance (see the v4-replan REPLAN-RECORD).  driver
was refactored behaviour-preservingly (run_one_rep + aggregate_cell; run_cell a
thin sequential caller); this harness calls those FROZEN primitives UNCHANGED.

Durability (addresses BOTH v1 failure modes): each container writes its ONE cell
durably to a FRESH Volume (kot-99a-grid-v4-vol) + VOL.commit() BEFORE returning
-> no client reorder buffer (total-loss); order_outputs=False; RESUMABLE via the
same structural-validation resume as v3 (a cell counts as done ONLY if it holds a
STRUCTURALLY-VALID SUCCESSFUL record whose FULL config identity matches the
enumeration).  cpu=8 on-demand containers doing real work (not cpu=1 preemptible
churn).  This file is OPUS operational code (fan-out + durability only).
"""
import modal

SIM_LOCAL = "/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim"
VOL = modal.Volume.from_name("kot-99a-grid-v4-vol", create_if_missing=True)

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
app = modal.App("kot-99a-grid-v4", image=image)

CELLDIR = "/vol/cells"

# ---------------------------------------------------------------------------
# STRUCTURAL-VALIDATION resume validators — VERBATIM from kot_99a_grid_v3.py
# (Rev3..Rev7 + cross-vendor review findings; kept in lockstep with
# verdict_99a._valid_success).  Copied unchanged so v4 resume-skip is identical.
# ---------------------------------------------------------------------------
_FWER_POWER_REQUIRED = ("fwer_events", "fwer_cp_upper95", "fwer_events_worstcase",
                        "fwer_cp_upper95_worstcase", "fit_failures",
                        "fit_failure_rate", "fit_failure_ceiling_pass",
                        "fit_failure_detail", "R")
_GATECAL_REQUIRED = ("arms", "R", "fit_failures", "fit_failure_rate",
                     "fit_failure_ceiling_pass")
_GATECAL_IDENTITY = ("label", "rho", "regime", "n_nat", "n_nonce")
_RUNG0_LABELS = {"F10", "P6"}
_POWER_PATHS = ("CVAL_DEFNSUP", "CVAL_CONSUPH_GRAPH", "CDEFSUP", "CCONSUP_A1",
                "CFMTH_given_conH")
_PINNED_GATE_ARMS = frozenset(("H", "A2IR", "A2", "A1"))
_GATE_GAMMAS = ("0.02500", "0.00625")


def _gate_arms_ok(arms):
    import math
    if not (isinstance(arms, dict) and set(arms.keys()) == set(_PINNED_GATE_ARMS)):
        return False
    for a in arms.values():
        if not isinstance(a, dict):
            return False
        sd = a.get("sd_ratio")
        if not (isinstance(sd, (int, float)) and not isinstance(sd, bool)
                and not math.isnan(sd)):
            return False
        g = a.get("gamma")
        if not (isinstance(g, dict) and all(k in g for k in _GATE_GAMMAS)):
            return False
        for k in _GATE_GAMMAS:
            gg = g[k]
            cpu = gg.get("cp_upper95") if isinstance(gg, dict) else None
            if not (isinstance(cpu, (int, float)) and not isinstance(cpu, bool)
                    and math.isfinite(cpu)):
                return False
    return True


def _rate_consistent(rec):
    import math
    R = rec.get("R"); ff = rec.get("fit_failures"); rate = rec.get("fit_failure_rate")
    if not (isinstance(R, int) and R > 0):
        return False
    if not (isinstance(ff, int) and not isinstance(ff, bool) and 0 <= ff <= R):
        return False
    if not (isinstance(rate, (int, float)) and not isinstance(rate, bool)
            and math.isfinite(rate) and rate >= 0.0):
        return False
    return abs(rate - ff / R) <= 1e-9


def _is_valid_success(rec, exp):
    """True iff rec is a structurally-valid SUCCESSFUL cell record for the
    EXPECTED cell exp = (kind, label, rho, regime, n_nat, n_nonce).  Same
    semantics as v3 (full config identity, expected kind, kind-appropriate
    schema/content, consistent fit-failure rate; exp MANDATORY, fail closed)."""
    if exp is None:
        return False
    if not isinstance(rec, dict) or "ERROR" in rec or "config_index" not in rec:
        return False
    kind = rec.get("_kind") or rec.get("kind")
    exp_kind, exp_label, exp_rho, exp_regime, exp_nnat, exp_nnonce = exp
    if kind != exp_kind or rec.get("label") != exp_label:
        return False
    if kind in ("fwer", "power"):
        if not all(k in rec for k in _FWER_POWER_REQUIRED):
            return False
        if (rec.get("rho") != exp_rho or rec.get("regime") != exp_regime
                or rec.get("n_nat") != exp_nnat or rec.get("n_nonce") != exp_nnonce):
            return False
        if kind == "power" and not (isinstance(rec.get("paths"), dict)
                                    and all(k in rec["paths"] for k in _POWER_PATHS)):
            return False
        if exp_label in _RUNG0_LABELS and not isinstance(rec.get("rung0"), dict):
            return False
    elif kind == "gatecal":
        if not all(k in rec for k in _GATECAL_REQUIRED):
            return False
        if not all(k in rec for k in _GATECAL_IDENTITY):
            return False
        if (rec["label"] != exp_label or rec["rho"] != exp_rho
                or rec["regime"] != exp_regime or rec["n_nat"] != exp_nnat
                or rec["n_nonce"] != exp_nnonce):
            return False
        if not _gate_arms_ok(rec.get("arms")):
            return False
    else:
        return False
    return _rate_consistent(rec)


def _finalize_gatecal(res, idx, label):
    """Stamp a fresh gate-cal battery result with its _kind/index/label + the
    structurally-exempt ZERO fit-failure schema (gate-cal runs the bootstrap
    gate test ONLY, never the exact-REML estimator).  Verbatim from v3."""
    res["_kind"] = "gatecal"
    res["config_index"] = idx
    res["label"] = label
    res.setdefault("fit_failures", 0)
    res.setdefault("fit_failure_rate", 0.0)
    res.setdefault("fit_failure_ceiling", 0.001)
    res.setdefault("fit_failure_ceiling_pass", True)
    res.setdefault("fit_failure_detail", [])
    return res


# ---------------------------------------------------------------------------
# REP-PARALLEL executor (opus operational fan-out) — same as the bit-identity-
# proven probe (kot_99a_repparallel_probe.py).  Calls the FROZEN science
# primitives driver.run_one_rep / driver.aggregate_cell UNCHANGED.
# ---------------------------------------------------------------------------
_BLAS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
         "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")


def _rep_chunk_worker(arg):
    """Top-level picklable worker: run_one_rep for a LIST of rep indices.  BLAS
    threads=1 BEFORE importing numpy; resolves t + gate_thr ONCE per chunk
    (deterministic -> bit-identical to run_cell's single compute)."""
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
    """Rep-parallel executor for ONE cell.  spec = (config_index, kind, label,
    rho, regime, n_nat, n_nonce).  Round-robin rep assignment across n_workers;
    outcomes re-indexed by rep and fed to driver.aggregate_cell (order-invariant).
    ONE parallelism level; BLAS threads pinned to 1/worker."""
    import time
    import multiprocessing as mp
    import grid
    import driver
    config_index, kind, label, rho, regime, n_nat, n_nonce = spec
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


def _compute_cell_repparallel(spec_full, R_override, n_workers):
    """Compute ONE cell (rep-parallel for fwer/power; sequential rung0 for
    F10/P6; bootstrap battery for gate-cal).  Same record shape + stamping as
    v3's _compute_cell (so verdict_99a + the resume validators are unchanged);
    cell-level exception isolation -> durable ERROR record on an unexpected
    raise (a fit-failure is handled INSIDE aggregate, not as a cell ERROR)."""
    import time
    import traceback
    import grid
    import rung0
    import pins
    import gate_cal_battery as gcb
    idx, kind, label, rho, regime, n_nat, n_nonce = spec_full
    R_fwer = R_override if R_override else pins.R_FWER
    R_power = R_override if R_override else pins.R_POWER
    spec = (idx, kind, label, rho, regime, n_nat, n_nonce)
    t0 = time.time()
    try:
        if kind == "gatecal":
            res = _finalize_gatecal(gcb.run_cell(rho, n_nonce, R_fwer, regime=regime),
                                    idx, label)
        else:
            if kind == "fwer":
                res = rep_parallel_cell(spec, R_fwer, n_workers, want_paths=False)
                if label == "F10":
                    t = grid.resolve_cell(label, rho, regime, n_nat, n_nonce, kind=kind)
                    res["rung0"] = rung0.run_rung0_cell(idx, t, R=R_fwer)
            else:
                res = rep_parallel_cell(spec, R_power, n_workers, want_paths=True)
                if label == "P6":
                    t = grid.resolve_cell(label, rho, regime, n_nat, n_nonce, kind=kind)
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


def _run_one_cell_impl(spec_full, R_override, n_workers):
    """LEVEL-1 body: resume-check (defensive) -> compute (rep-parallel) ->
    DURABLE per-cell Volume write + commit -> return status.  Runs in ONE
    container per cell (mapped by the driver)."""
    import os
    for v in _BLAS:
        os.environ[v] = "1"
    import sys
    import json
    if "/root/sim" not in sys.path:
        sys.path.insert(0, "/root/sim")
    os.chdir("/root/sim")
    os.makedirs(CELLDIR, exist_ok=True)
    import grid
    spec_full = list(spec_full)
    idx = spec_full[0]
    expected = {c[0]: tuple(c[1:]) for c in grid.enumerate_cells()}
    cellpath = os.path.join(CELLDIR, f"cell_{idx:03d}.json")
    # DEFENSIVE resume re-check (the driver also filters todo via list_done):
    VOL.reload()
    if os.path.exists(cellpath):
        try:
            rec = json.load(open(cellpath))
            if _is_valid_success(rec, exp=expected.get(idx)):
                return {"idx": idx, "status": "skipped-valid"}
        except Exception:
            pass
    res = _compute_cell_repparallel(spec_full, R_override, n_workers)
    with open(cellpath, "w") as fh:
        json.dump(res, fh, default=str)
    VOL.commit()                               # DURABLE before return
    return {"idx": idx, "status": ("error" if "ERROR" in res else "computed"),
            "kind": res.get("_kind"), "wall_s": res.get("_wall_s")}


@app.function(cpu=8.0, memory=16384, timeout=28800, volumes={"/vol": VOL}, retries=2)
def run_one_cell(spec_full):
    """FULL cell: frozen R (FWER/gatecal 40000, power 10000), 8 rep-workers."""
    return _run_one_cell_impl(spec_full, R_override=0, n_workers=8)


@app.function(cpu=2.0, memory=4096, timeout=1800, volumes={"/vol": VOL}, retries=2)
def run_one_cell_tiny(spec_full, R_override: int = 50):
    """TINY cell (validation): small R, 2 rep-workers, cpu=2."""
    return _run_one_cell_impl(spec_full, R_override=R_override or 50, n_workers=2)


@app.function(volumes={"/vol": VOL})
def list_done():
    """Structural-validation resume set: valid cell indices in the Volume."""
    import os
    import json
    import sys
    if "/root/sim" not in sys.path:
        sys.path.insert(0, "/root/sim")
    os.chdir("/root/sim")
    import grid
    expected = {c[0]: tuple(c[1:]) for c in grid.enumerate_cells()}
    VOL.reload()
    done = []
    if os.path.isdir(CELLDIR):
        for f in os.listdir(CELLDIR):
            if not (f.startswith("cell_") and f.endswith(".json")):
                continue
            try:
                rec = json.load(open(os.path.join(CELLDIR, f)))
            except Exception:
                continue
            idx = rec.get("config_index")
            if idx in expected and _is_valid_success(rec, exp=expected[idx]):
                done.append(int(idx))
    return sorted(done)


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


@app.function(volumes={"/vol": VOL})
def clear_vol():
    """Wipe the Volume cells dir (clean reset before the full run)."""
    import os
    import shutil
    VOL.reload()
    if os.path.isdir(CELLDIR):
        shutil.rmtree(CELLDIR)
    os.makedirs(CELLDIR, exist_ok=True)
    VOL.commit()
    return {"cleared": True}


def _est(c):
    """Shortest-first ordering key (power R=10k before FWER/gatecal R=40k)."""
    idx, kind, label, rho, regime, n_nat, n_nonce = c
    R = 10000 if kind == "power" else 40000
    per = 0.131 if (n_nat, n_nonce) == (96, 160) else 0.094
    return R * per


@app.local_entrypoint()
def main(mode: str = "tinyvalidate"):
    import sys
    import os
    import json
    sys.path.insert(0, SIM_LOCAL)
    import grid
    cells = grid.enumerate_cells()
    by = {}
    for c in cells:
        by.setdefault(c[1], c)                 # first spec per kind
    if mode == "tinyvalidate":
        tiny = [list(by["fwer"]), list(by["power"])]  # 1 fwer + 1 power @ R=50
        print("clearing volume ...", flush=True)
        print(json.dumps(clear_vol.remote()), flush=True)
        print("RUN 1 (compute both) ...", flush=True)
        r1 = list(run_one_cell_tiny.map(tiny, order_outputs=False))
        print(json.dumps(r1, default=str), flush=True)
        c1 = collect.remote()
        print("COLLECT:", json.dumps(c1, default=str), flush=True)
        done_mid = list_done.remote()
        print("LIST_DONE:", json.dumps(done_mid), flush=True)
        print("RUN 2 (should SKIP both = resume) ...", flush=True)
        r2 = list(run_one_cell_tiny.map(tiny, order_outputs=False))
        print(json.dumps(r2, default=str), flush=True)
        ran1 = sorted(x["idx"] for x in r1 if x["status"] == "computed")
        ok = (ran1 == sorted(c1["config_indices"])
              and sorted(done_mid) == ran1
              and all(x["status"] == "skipped-valid" for x in r2))
        print("TINY-VALIDATION:", "GREEN" if ok else "RED", flush=True)
    elif mode == "full":
        specs = [list(c) for c in sorted(cells, key=_est)]
        done = set(list_done.remote())
        todo = [s for s in specs if s[0] not in done]
        print(f"[v4-full] {len(done)} already-valid, {len(todo)} todo "
              f"(cell-per-container cpu=8, 8 rep-workers, durable Volume "
              f"kot-99a-grid-v4-vol, resumable) ...", flush=True)
        ran = []
        for res in run_one_cell.map(todo, order_outputs=False, return_exceptions=True):
            ran.append(res)
            if isinstance(res, dict):
                print(f"  [{len(ran)}/{len(todo)}] cell {res.get('idx')} "
                      f"{res.get('status')} ({res.get('kind')}) "
                      f"wall={res.get('wall_s')}", flush=True)
            else:
                print(f"  [{len(ran)}/{len(todo)}] container-exception: {res!r}", flush=True)
        c = collect.remote(True)
        print(f"[v4-full] collected {c['n_cells']} cells from Volume", flush=True)
        outdir = os.path.join(SIM_LOCAL, "results", "frozen-run", "grid-run-v4")
        os.makedirs(outdir, exist_ok=True)
        combined = {
            "note": "99a frozen full-grid raw results (v4 rep-parallel cell-per-"
                    "container harness). Mechanical verdict via verdict_99a.py.",
            "base_seed": 990066001, "n_cells": c["n_cells"],
            "config_indices": c["config_indices"],
            "R_fwer": 40000, "R_power": 10000, "R_gatecal": 40000,
            "results": c.get("cells", []),
        }
        with open(os.path.join(outdir, "grid-results.json"), "w") as f:
            json.dump(combined, f, indent=2, default=str)
        print(f"[v4-full] WROTE {outdir}/grid-results.json ({c['n_cells']}/114 cells)",
              flush=True)
