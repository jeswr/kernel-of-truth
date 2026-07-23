"""Modal FULL-GRID app for the 99a frozen acceptance-artifact simulation.

OPUS OPERATIONAL CODE (experiment-runner): this file RUNS the FROZEN design.
It defines NO science: it fans the pinned operative pipeline (driver.py ->
pipeline.run_replication -> reml_composite exact-REML for families A/B, R11a)
across Modal containers, one container per grid cell, and collects results.
The estimator / DGM / graphical procedure / truth engine are the frozen modules
under /root/sim; nothing here alters them.

Pinned image (SIM-SPEC S2/R8g), byte-identical build to kot_99a_modal.py /
kot_99a_r10a_app.py so Modal reuses the cached digest im-k5wxPoFZ7ncQlZ2EJFSkXN:
CPython 3.12.1 / numpy 2.1.3 / scipy 1.14.1 / R 4.4.1 / lme4 1.1-35.5 /
lmerTest 3.1-3.

Grid (grid.enumerate_cells, S6/S7): 74 FWER (R=40,000) + 36 power (R=10,000) +
4 gate-cal (R=40,000).  Futility + Rung-0 default ON (driver.run_cell).  F10/P6
additionally run the frozen rung0.run_rung0_cell termination-acceptance analysis.
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
app = modal.App("kot-99a-grid", image=image)


def _setup():
    import sys
    import os
    if "/root/sim" not in sys.path:
        sys.path.insert(0, "/root/sim")
    os.chdir("/root/sim")


# ---------------------------------------------------------------------------
@app.function(cpu=1.0, timeout=600)
def smoke_reml():
    """STEP 2: prove the OPERATIVE pipeline path is exact-REML for BOTH families
    A (UCT/consumer) and B (composite/reviewer), R11a — not the retired pooled
    ANOVA.  Introspects the wiring, runs F3 R=8 green, and shows the operative
    CompositeREML contrast differs from the retired FamilyAnova contrast."""
    _setup()
    import inspect
    import numpy as np
    import grid
    import pins
    import pipeline
    import reml_composite
    import seeds
    import dgm
    from inference import FamilyAnova

    idx, t = grid.cell_by_label("F3", rho=0.1, n="base", regime="gaussian")

    # (1) the cached operative fitters are CompositeREML (exact-REML), both families
    uct_fitter = reml_composite.get_uct(t)
    comp_fitter = reml_composite.get_comp(t)
    fitter_types = {"uct": type(uct_fitter).__name__,
                    "comp": type(comp_fitter).__name__}

    # (2) pipeline.run_replication source references the exact-REML fitters for the
    #     UCT/composite ledger fits, and uses FamilyAnova ONLY in the Stage-2 format
    #     branch (family D), never for families A/B.
    src = inspect.getsource(pipeline.run_replication)
    wiring = {
        "uct_uses_get_uct": "reml_composite.get_uct(t)" in src,
        "comp_uses_get_comp": "reml_composite.get_comp(t)" in src,
        "familyanova_only_in_format_branch":
            ("FamilyAnova(Yf)" in src) and ("FamilyAnova(Yuct)" not in src)
            and ("FamilyAnova(Ycomp)" not in src),
    }

    # (3) run F3 R=8 green
    from hypotheses import truth_set
    T = truth_set(t)
    thr = dgm.compute_gate_thresholds(t, idx)
    fwer_events = 0
    for r in range(8):
        ss = seeds.rep_substreams(idx, r)
        rej = pipeline.run_replication(t, ss, gate_thr=thr)["rejected"]
        if rej & T:
            fwer_events += 1

    # (4) operative exact-REML contrast != retired pooled-ANOVA contrast (rep 0),
    #     confirming the exact-REML engine (not the pooled ANOVA) is operative.
    ss0 = seeds.rep_substreams(idx, 0)
    Yuct = dgm.gen_uct(t, ss0)
    Ycomp, _ = dgm.gen_composite_and_gate(t, ss0, gate_thr=thr)
    _UCT = {a: i for i, a in enumerate(pins.UCT_ARMS)}
    _CMP = {a: i for i, a in enumerate(pins.COMP_ARMS)}
    uct_fitter.fit(Yuct)
    comp_fitter.fit(Ycomp)
    reml_uct = uct_fitter.contrast(_UCT["H"], _UCT["T"])
    reml_cmp = comp_fitter.contrast(_CMP["H"], _CMP["A2IR"])
    an_uct = FamilyAnova(Yuct).contrast(_UCT["H"], _UCT["T"])
    an_cmp = FamilyAnova(Ycomp).contrast(_CMP["H"], _CMP["A2IR"])
    contrast_cmp = {
        "uct_H_vs_T": {
            "reml": {"theta": reml_uct.theta_hat, "se": reml_uct.se, "nu": reml_uct.nu},
            "pooled_anova": {"theta": an_uct.theta_hat, "se": an_uct.se, "nu": an_uct.nu},
            "se_differs": abs(reml_uct.se - an_uct.se) > 1e-9,
            "nu_differs": abs(reml_uct.nu - an_uct.nu) > 1e-6,
        },
        "comp_H_vs_A2IR": {
            "reml": {"theta": reml_cmp.theta_hat, "se": reml_cmp.se, "nu": reml_cmp.nu},
            "pooled_anova": {"theta": an_cmp.theta_hat, "se": an_cmp.se, "nu": an_cmp.nu},
            "se_differs": abs(reml_cmp.se - an_cmp.se) > 1e-9,
            "nu_differs": abs(reml_cmp.nu - an_cmp.nu) > 1e-6,
        },
    }
    return {"config_index": idx, "fitter_types": fitter_types, "wiring": wiring,
            "f3_R8_fwer_events": fwer_events, "contrast_compare": contrast_cmp}


# ---------------------------------------------------------------------------
@app.function(cpu=1.0, timeout=600)
def emit_s8():
    """S8: emit + hash the normative resolved-config table on the pinned image
    BEFORE any replication.  Returns the sha256 and a couple of truth-set spot
    checks (the file is written to the container tmpfs; the hash is the artifact)."""
    _setup()
    import json
    import hashlib
    from dataclasses import asdict
    import pins
    import grid
    from hypotheses import truth_set
    import emit_config

    cells = grid.enumerate_cells()
    records = []
    for (idx, kind, label, rho, regime, n_nat, n_nonce) in cells:
        t = grid.resolve_cell(label, rho, regime, n_nat, n_nonce, kind=kind)
        records.append({
            "config_index": idx, "kind": kind, "label": label,
            "rho": rho, "regime": regime, "n_nat": n_nat, "n_nonce": n_nonce,
            "vector": emit_config._vec_dict(t),
            "truth_set": sorted(truth_set(t)),
        })
    artifact = {
        "note": "MOCK S8 resolved-config table (99a SIM-SPEC). "
                "Truth sets are computed by hypotheses.truth_set (S5), never authored.",
        "base_seed": pins.BASE_SEED,
        "n_cells": len(records),
        "rotation_tables": emit_config.rotation_tables(),
        "cells": records,
    }
    blob = json.dumps(artifact, sort_keys=True, default=str).encode()
    sha = hashlib.sha256(blob).hexdigest()
    spot = {r["config_index"]: r["truth_set"] for r in records
            if r["config_index"] in (0, 27, 55, 58, 87, 104, 110)}
    return {"n_cells": len(records), "sha256": sha, "spot_truth_sets": spot,
            "base_seed": pins.BASE_SEED}


# ---------------------------------------------------------------------------
@app.function(cpu=1.0, timeout=1800)
def determinism():
    """S2 determinism: 100 pinned (config, rep) pairs, each run twice on the
    pinned image; rejection vectors must be bit-identical."""
    _setup()
    import json
    import hashlib
    import grid
    import seeds
    import pipeline
    import dgm
    import determinism_check as dc

    pairs = dc.pinned_pairs()
    records = []
    n_mismatch = 0
    thr_cache = {}
    for (ci, rp) in pairs:
        t = dc._cell_for_index(ci)
        if ci not in thr_cache:
            thr_cache[ci] = dgm.compute_gate_thresholds(t, ci)
        thr = thr_cache[ci]
        r1 = sorted(pipeline.run_replication(t, seeds.rep_substreams(ci, rp), gate_thr=thr)["rejected"])
        r2 = sorted(pipeline.run_replication(t, seeds.rep_substreams(ci, rp), gate_thr=thr)["rejected"])
        ident = (r1 == r2)
        if not ident:
            n_mismatch += 1
        records.append({"config_index": ci, "replication_index": rp,
                        "rejected": r1, "bit_identical": ident})
    blob = json.dumps(records, sort_keys=True).encode()
    return {"n_pairs": len(records), "n_mismatch": n_mismatch,
            "PASS": n_mismatch == 0,
            "rejection_vectors_sha256": hashlib.sha256(blob).hexdigest()}


# ---------------------------------------------------------------------------
@app.function(cpu=1.0, timeout=3600)
def validate_slice(label: str, rho: float, R: int, nlevel: str = "base",
                   regime: str = "gaussian", kind: str = "fwer",
                   want_paths: bool = False):
    """STEP 4 small-slice validation on the pinned image (host-mock reproduction)."""
    _setup()
    import grid
    import driver
    import gate_cal_battery as gcb
    if kind == "gatecal":
        n_nonce = 96 if nlevel == "base" else 160
        res = gcb.run_cell(rho, n_nonce, R)
        all_pass, any_sd_flag = gcb.cell_verdict(res)
        worst = {"0.02500": 0.0, "0.00625": 0.0}
        min_sd = 1e9
        for a, rec in res["arms"].items():
            min_sd = min(min_sd, rec["sd_ratio"])
            for g in ("0.02500", "0.00625"):
                worst[g] = max(worst[g], rec["gamma"][g]["cp_upper95"])
        return {"kind": "gatecal", "rho": rho, "n_nonce": n_nonce, "R": R,
                "all_pass": all_pass, "any_sd_flag": any_sd_flag,
                "min_sd_ratio": min_sd, "worst_cp_upper": worst,
                "config_index": res["config_index"]}
    idx, t = grid.cell_by_label(label, rho=rho, n=nlevel, regime=regime, kind=kind)
    out = driver.run_cell(idx, t, R=R, want_paths=want_paths)
    return {"kind": kind, "label": label, "config_index": idx, "rho": rho,
            "nlevel": nlevel, "R": R, "fwer_hat": out["fwer_hat"],
            "fwer_cp_upper95": out["fwer_cp_upper95"], "fwer_events": out["fwer_events"],
            "truth_set": out["truth_set"], "stage2_rate": out["stage2_rate"],
            "sec_per_rep": out["sec_per_rep"],
            "paths": out.get("paths"),
            "claim_rej_rate": out["claim_rej_rate"]}


# ---------------------------------------------------------------------------
@app.function(cpu=1.0, timeout=18000, retries=2)
def run_cell_job(spec):
    """Run ONE frozen grid cell at its pinned R.  spec = (config_index, kind,
    label, rho, regime, n_nat, n_nonce).  Returns the full per-cell record with
    exact one-sided CP bounds; F10/P6 add the frozen rung0 termination analysis."""
    _setup()
    import time
    import grid
    import driver
    import rung0
    import pins
    import gate_cal_battery as gcb
    idx, kind, label, rho, regime, n_nat, n_nonce = spec
    t0 = time.time()

    if kind == "gatecal":
        res = gcb.run_cell(rho, n_nonce, pins.R_FWER)   # frozen R=40,000 battery
        res["_kind"] = "gatecal"
        res["_wall_s"] = time.time() - t0
        res["config_index"] = idx
        res["label"] = label
        return res

    t = grid.resolve_cell(label, rho, regime, n_nat, n_nonce, kind=kind)
    if kind == "fwer":
        out = driver.run_cell(idx, t, R=pins.R_FWER, want_paths=False)
        if label == "F10":
            out["rung0"] = rung0.run_rung0_cell(idx, t, R=pins.R_FWER)
    else:  # power
        out = driver.run_cell(idx, t, R=pins.R_POWER, want_paths=True)
        if label == "P6":
            out["rung0"] = rung0.run_rung0_cell(idx, t, R=pins.R_POWER)
    out["_kind"] = kind
    out["regime"] = regime
    out["_wall_s"] = time.time() - t0
    return out


@app.local_entrypoint()
def main(mode: str = "smoke"):
    import json
    if mode == "smoke":
        print(json.dumps(smoke_reml.remote(), indent=2, default=str))
    elif mode == "s8":
        print(json.dumps(emit_s8.remote(), indent=2, default=str))
    elif mode == "determinism":
        print(json.dumps(determinism.remote(), indent=2, default=str))
    elif mode == "validate":
        res = {}
        res["F3_strongfwer"] = validate_slice.remote("F3", 0.1, 600, "base", "gaussian", "fwer")
        res["F11_globalnull"] = validate_slice.remote("F11", 0.1, 600, "base", "gaussian", "fwer")
        res["gatecal_r01_n96"] = validate_slice.remote("GATECAL", 0.1, 3000, "base", "gaussian", "gatecal")
        print(json.dumps(res, indent=2, default=str))
