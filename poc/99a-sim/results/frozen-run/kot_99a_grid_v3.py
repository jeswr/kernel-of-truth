"""CORRECTED 99a full-grid harness (v2) — TOTAL-LOSS-PROOF + churn-resistant.

Fixes the v1 failure modes (post-mortem 2026-07-23):
  * v1 died when the Modal workspace was disabled mid-run; `order_outputs=True`
    held ALL completed cells in the live client's reorder buffer, so the crash
    lost ~71 buffered cells (finish-or-lose trap).
  * v1 ran 100 preemptible cpu=1 containers -> heavy CPU-preemption churn +
    ~2.4x slowdown + retry restarts.

v2 design:
  * DURABLE per-cell writes to a Modal Volume (`kot-99a-grid-v3-vol`) keyed by
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
VOL = modal.Volume.from_name("kot-99a-grid-v3-vol", create_if_missing=True)

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
app = modal.App("kot-99a-grid-v3", image=image)

CELLDIR = "/vol/cells"

# Required schema per kind for a record to count as a STRUCTURALLY-VALID
# SUCCESSFUL result (Rev3/Rev4 — GPT-5.6 review items 6b/6c + item 3d).  A record
# that lacks these (e.g. the 10 banked OK-REML cells produced BEFORE the
# convergence certificate + fit-failure schema), carries the WRONG kind for its
# index, or has an inconsistent fit-failure rate is NOT "done" and MUST be re-run.
_FWER_POWER_REQUIRED = ("fwer_events", "fwer_cp_upper95", "fwer_events_worstcase",
                        "fwer_cp_upper95_worstcase", "fit_failures",
                        "fit_failure_rate", "fit_failure_ceiling_pass",
                        "fit_failure_detail", "R")
_GATECAL_REQUIRED = ("arms", "R", "fit_failures", "fit_failure_rate",
                     "fit_failure_ceiling_pass")
# Rev6 (review finding 1): the six-field config identity a VALID gate-cal
# record MUST carry.  Required PRESENT and matched WITHOUT substitution — a
# record with regime / n_nat ABSENT is REJECTED (never assumed to equal the
# expected value), closing the beta/n_nat-masquerade fail-open.
_GATECAL_IDENTITY = ("label", "rho", "regime", "n_nat", "n_nonce")
_RUNG0_LABELS = {"F10", "P6"}
_POWER_PATHS = ("CVAL_DEFNSUP", "CVAL_CONSUPH_GRAPH", "CDEFSUP", "CCONSUP_A1",
                "CFMTH_given_conH")
# Pinned S4.4 gate-cal arm set + gamma keys (Rev5 — cross-vendor review
# finding 2): a gate-cal record is valid ONLY with EXACTLY these four arms
# (a one-arm {"H": ...} record, or any missing/extra arm, is NOT done) and
# per-(arm, gamma) numeric RAW content.  Kept in lockstep with
# verdict_99a._valid_success.
_PINNED_GATE_ARMS = frozenset(("H", "A2IR", "A2", "A1"))
_GATE_GAMMAS = ("0.02500", "0.00625")


def _gate_arms_ok(arms):
    """EXACT pinned arm set + numeric raw per-(arm,gamma) content (Rev5).
    cp_upper95 must be numeric + finite; sd_ratio numeric + non-NaN (the
    battery emits +inf for a degenerate zero empirical SD)."""
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
    EXPECTED cell exp = (kind, label, rho, regime, n_nat, n_nonce) from
    grid.enumerate_cells().  Rev5 (cross-vendor review finding 1): the FULL
    config identity is checked — a record with the correct (kind, label) but
    the WRONG rho / regime / n_nat / n_nonce must NOT count as done for the
    requested cell (it would suppress the correct cell).  Also required: no
    ERROR, the expected kind for the index (item 3d — a full-schema FWER
    record at a gate-cal index must NOT count as done), full kind-appropriate
    schema, kind-appropriate content (power paths / F10-P6 rung-0 / the EXACT
    pinned gate-cal arm set, review finding 2), and a fit-failure rate
    CONSISTENT with fit_failures/R.  Kept in lockstep with
    verdict_99a._valid_success.

    Rev7 (cross-vendor review): `exp` is MANDATORY — there is NO validator path
    that skips the identity match.  The Rev5/Rev6 `exp=None` default with
    `exp is not None`-guarded identity checks was a latent fail-open (an
    omitted-`exp` call accepted a wrong-but-present identity record, e.g. an
    index-110 record carrying regime="beta"/n_nat=999); `exp` is now required
    and `exp is None` fails closed, so the omitted-`exp` path matches the wired
    production path (kot_99a_grid_v2:_batch_impl passes exp=expected[idx])."""
    if exp is None:
        return False                          # Rev7: fail closed, no identity-skip path
    if not isinstance(rec, dict) or "ERROR" in rec or "config_index" not in rec:
        return False
    kind = rec.get("_kind") or rec.get("kind")
    exp_kind, exp_label, exp_rho, exp_regime, exp_nnat, exp_nnonce = exp
    if kind != exp_kind or rec.get("label") != exp_label:
        return False
    if kind in ("fwer", "power"):
        if not all(k in rec for k in _FWER_POWER_REQUIRED):
            return False
        # FULL config identity (Rev5): EVERY config field must match.
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
        # FULL SIX-FIELD config identity (Rev6 finding 1): ALL of label, rho,
        # regime, n_nat, n_nonce must be PRESENT and MATCH the enumeration.
        # A MISSING regime / n_nat is REJECTED — NEVER substituted with the
        # expected value (the Rev5 `.get(fld, expected)` default was the
        # fail-open: a beta / wrong-n_nat payload with the fields absent
        # masqueraded as the required Gaussian/48 cell).
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
    """Rev6 (review item 2): stamp a freshly-computed gate-cal battery result
    with its _kind, index/label, and the structurally-exempt ZERO fit-failure
    schema, so a v2 gate-cal record is SELF-SUFFICIENT — it carries the full
    _GATECAL_REQUIRED schema WITHOUT relying on the legacy-migration back-fill.
    A gate-cal cell runs the bootstrap gate test ONLY (it NEVER touches the
    exact-REML estimator), so zero fit-failures is exact BY CONSTRUCTION, not a
    measurement.  setdefault -> never overwrites a value the battery carries;
    fresh list per call (no shared-mutable aliasing)."""
    res["_kind"] = "gatecal"
    res["config_index"] = idx
    res["label"] = label
    res.setdefault("fit_failures", 0)
    res.setdefault("fit_failure_rate", 0.0)
    res.setdefault("fit_failure_ceiling", 0.001)
    res.setdefault("fit_failure_ceiling_pass", True)
    res.setdefault("fit_failure_detail", [])
    return res


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
            # Pass the spec's regime so the battery runs + serializes the
            # AUTHENTIC regime for this cell (Rev6 finding 1); n_nat is
            # constructed inside the battery from n_nonce and serialized there.
            # _finalize_gatecal stamps _kind/index/label + the structurally-
            # exempt zero fit-failure schema (Rev6 item 2) so the record is
            # self-sufficient.
            res = _finalize_gatecal(gcb.run_cell(rho, n_nonce, R_fwer, regime=regime),
                                    idx, label)
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
    import sys
    import json
    import multiprocessing as mp
    # OPUS operational fix (kern/opus-runner-1): the b13f22e0 hardening replaced
    # the filename-only resume with a structural-validation resume that imports
    # the sim science modules (grid.enumerate_cells()) in the container-MAIN
    # process, but the refactor dropped the /root/sim sys.path setup that
    # _compute_cell (lines ~206-210) still does -> ModuleNotFoundError: 'grid'.
    # Restore it (mirrors _compute_cell EXACTLY; touches NO science module, NO
    # validator logic, NO image digest) so `import grid` resolves to the shipped
    # /root/sim/grid.py.
    if "/root/sim" not in sys.path:
        sys.path.insert(0, "/root/sim")
    os.chdir("/root/sim")
    import grid
    os.makedirs(CELLDIR, exist_ok=True)
    VOL.reload()
    # RESUME (Rev3/Rev4 items 6b/6c + 3d; Rev5 review findings 1 + 2): a cell
    # counts as "done" ONLY if it holds a STRUCTURALLY-VALID SUCCESSFUL record
    # whose FULL config identity (kind, label, rho, regime, n_nat, n_nonce)
    # matches the enumeration for its index — a record with the right
    # (kind, label) but the WRONG rho/regime/n_nat/n_nonce, or a gate-cal
    # record without EXACTLY the pinned 4-arm set, must NOT suppress the
    # required cell — with full schema + content + a consistent fit-failure
    # rate; NOT merely "no ERROR key".  Consequence: the 100 ERROR cells AND
    # the 10 banked OK-REML cells (pre-certificate, lacking the schema and
    # possibly holding NON-CONVERGED fits) are BOTH re-run.
    # idx -> (kind, label, rho, regime, n_nat, n_nonce): the FULL config map.
    expected = {c[0]: tuple(c[1:]) for c in grid.enumerate_cells()}
    done = set()
    for f in os.listdir(CELLDIR):
        if not (f.startswith("cell_") and f.endswith(".json")):
            continue
        try:
            rec = json.load(open(os.path.join(CELLDIR, f)))
        except Exception:
            continue
        idx = rec.get("config_index")
        if idx not in expected:
            continue                          # unexpected index -> not done
        if _is_valid_success(rec, exp=expected[idx]):
            done.add(int(idx))
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


_MIGRATION_PROV = (
    "Rev3 legacy back-fill: GATE-CAL ONLY.  Gate-cal cells run the bootstrap "
    "gate test, NEVER the exact-REML estimator, so they are UNAFFECTED by the "
    "convergence-test qualifier and had zero exact-REML fit-failures by "
    "construction; the fit-failure fields are back-filled = 0, not re-measured.")


def _migrate_gatecal_record(rec):
    """PURE per-record legacy back-fill decision (Rev3 + Rev6), shared by
    migrate_legacy and the validation suite so neither drifts.  Returns
    (rec_out, migrated, reason).  Rules: ERROR + REML (fwer/power) cells are
    RE-RUN, never migrated; a gate-cal record lacking the full six-field
    identity is NOT migrated (Rev6 finding 1c — cannot be authenticated, so it
    is re-run under the fixed battery; back-filling identity from the
    enumeration is exactly the substitution the validators now forbid); an
    already-migrated record is an idempotent no-op; only a full-identity,
    not-yet-migrated gate-cal record is back-filled with the zero fit-failure
    schema.  Never mutates the input on a no-op; returns a fresh dict on
    migrate."""
    kind = rec.get("_kind") or rec.get("kind")
    if "ERROR" in rec:
        return rec, False, "error-cell (re-run)"
    if kind != "gatecal":
        return rec, False, "reml-cell (re-run, not migrated)"
    if not all(k in rec for k in _GATECAL_IDENTITY):
        return rec, False, "legacy gate-cal missing identity (re-run under fixed battery)"
    if rec.get("_fitfailure_migration") or "fit_failure_rate" in rec:
        return rec, False, "already-migrated"
    out = dict(rec)
    out["fit_failures"] = 0
    out["fit_failure_rate"] = 0.0
    out["fit_failure_ceiling"] = 0.001
    out["fit_failure_ceiling_pass"] = True
    out["fit_failure_detail"] = []
    out["_fitfailure_migration"] = _MIGRATION_PROV
    return out, True, "migrated"


@app.function(volumes={"/vol": VOL})
def migrate_legacy():
    """BLOCKING-6c (Rev3): back-fill the fit-failure fields (= 0) ONLY on the
    banked GATE-CAL cells (structurally exempt: no exact-REML).  The 10 banked
    OK-REML cells are NOT migrated -- under the pre-Rev3 code they were selected
    WITHOUT the tol_dev/tol_par convergence tests and may hold previously-
    accepted NON-CONVERGED fits, so they are RE-RUN (they lack the schema, so
    the resume 'done' test excludes them automatically).  Idempotent; never
    touches ERROR or REML cells.  Commits durably.

    Rev6 (review finding 1c): a legacy gate-cal record that lacks the full
    six-field config identity (regime / n_nat absent) is NOT migrated -- it
    CANNOT be authenticated (an absent regime/n_nat is indistinguishable from a
    beta / wrong-n_nat masquerade), so it is left to be RE-RUN under the fixed
    battery (which now serializes all six identity fields + the zero
    fit-failure schema).  Back-filling identity from the enumeration is exactly
    the substitution the validators now forbid, so it is NOT done here."""
    import os
    import json
    VOL.reload()
    migrated, skipped = [], []
    for f in sorted(os.listdir(CELLDIR)):
        if not (f.startswith("cell_") and f.endswith(".json")):
            continue
        p = os.path.join(CELLDIR, f)
        rec = json.load(open(p))
        out, did, reason = _migrate_gatecal_record(rec)
        if did:
            with open(p, "w") as fh:
                json.dump(out, fh, default=str)
            migrated.append(out.get("config_index"))
        else:
            skipped.append((rec.get("config_index"), reason))
    VOL.commit()
    return {"migrated": sorted(x for x in migrated if x is not None),
            "skipped": skipped}


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
    if mode == "migrate":
        # BLOCKING-6c: back-fill fit-failure fields on the banked OK cells
        # BEFORE the resume re-run (idempotent).  Run once on the durable Volume.
        print(json.dumps(migrate_legacy.remote(), indent=2, default=str))
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
        # Rev6: migrate_legacy is now a no-op on the 4 legacy gate-cal cells —
        # they lack the six-field identity the fixed validators require, so they
        # are NOT authenticated but RE-RUN under the fixed battery (which
        # serializes all six identity fields + the zero fit-failure schema).
        # The resume therefore re-runs ALL banked cells (100 ERROR + 10 OK-REML
        # + 4 legacy gate-cal) under the hardened estimator + fixed battery;
        # migrate_legacy is retained as a defensive idempotent pass (it will
        # only ever back-fill a record that ALREADY carries full identity).
        print("[v3-full] migrating legacy gate-cal cells (Rev6: no-op unless a "
              "record already carries full six-field identity) ...", flush=True)
        print("[v3-full] migrate_legacy:", json.dumps(migrate_legacy.remote(), default=str), flush=True)
        print(f"[v3-full] launching {len(specs)} cells (SHORTEST-first) on ONE "
              f"cpu=32 container (durable Volume kot-99a-grid-v3-vol, resumable; "
              f"100 ERROR + 10 OK-REML + 4 legacy gate-cal re-run under the "
              f"fixed battery) ...",
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
        outdir = os.path.join(SIM_LOCAL, "results", "frozen-run", "grid-run-v3")
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
