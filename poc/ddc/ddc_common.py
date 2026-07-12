#!/usr/bin/env python3
"""Shared DDC campaign plumbing: job enumeration, expected-grid
construction, dry-plan cost model, and the CANONICAL finalisation that
turns per-shard outputs into the exact three inputs analysis/ddc1.py
consumes (items.jsonl / cells.json / sidecar.json). Both the monolithic
runner and merge_shards.py call finalize(), so monolithic and
sharded+merged paths are byte-identical by construction (modulo the
disclosed cost ledger). Stdlib only.

Design constants come exclusively from inputs/ddc-manifest.json
(ASM-1654 coverage, ASM-1664 budgets); nothing here is tunable at run
time. This module states NO feasibility conclusion.
"""

from __future__ import annotations

import hashlib
import json
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.join(_HERE, "inputs", "ddc-manifest.json")

TIERS = ("t0", "ddc0", "s1", "s2")


def load_manifest(path=MANIFEST_PATH):
    with open(path) as f:
        return json.load(f)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rho_tag(rho):
    return ("%g" % rho).replace(".", "p")


def cells_for(manifest, rung):
    """All (arm, rho, seed) cells of a rung per ASM-1654 coverage."""
    cov = manifest["arm_coverage"][rung]
    cells = []
    for arm in sorted(cov):
        spec = cov[arm]
        for rho in spec["rhos"]:
            for seed in spec["seeds"]:
                cells.append((arm, float(rho), int(seed)))
    return cells


def build_jobs(manifest, tier):
    """The canonical independent-job plan (one Modal job per cell; every
    job far below the 12 h function timeout). Tags are stable identifiers
    for --jobs subsetting across accounts."""
    if tier == "t0":
        return [{"tag": "t0-a0-r135", "rung": "r135", "arm": "A0",
                 "rho": 1.0, "seed": 0}]
    if tier == "ddc0":
        return [{"tag": "ddc0-g0", "rung": "r135", "arm": None,
                 "rho": None, "seed": None}]
    if tier == "s1":
        return [{"tag": "s1-%s-rho%s-s%d" % (arm.lower(), rho_tag(rho),
                                             seed),
                 "rung": "r135", "arm": arm, "rho": rho, "seed": seed}
                for (arm, rho, seed) in cells_for(manifest, "r135")
                if arm != "A0"]
    if tier == "s2":
        jobs = [{"tag": "s2-a0-r360", "rung": "r360", "arm": "A0",
                 "rho": 1.0, "seed": 0}]
        jobs += [{"tag": "s2-%s-rho%s-s%d" % (arm.lower(), rho_tag(rho),
                                              seed),
                  "rung": "r360", "arm": arm, "rho": rho, "seed": seed}
                 for (arm, rho, seed) in cells_for(manifest, "r360")
                 if arm != "A0"]
        return jobs
    raise SystemExit("ERR_DDC_TIER: unknown tier %r (have %s)"
                     % (tier, ",".join(TIERS)))


def build_expected_grid(manifest, a2_ran, s2_ran):
    """sidecar.expected_grid for analysis/ddc1.py completeness: rung ->
    [[arm, rho, n_seeds], ...]; A2 rows only when ddc0 licensed the arm,
    r360 only when S2 ran (§8 promotion rule — mechanical flags)."""
    grid = {}
    for rung in ("r135",) + (("r360",) if s2_ran else ()):
        rows = []
        cov = manifest["arm_coverage"][rung]
        for arm in sorted(cov):
            if arm == "A2" and not a2_ran:
                continue
            spec = cov[arm]
            for rho in spec["rhos"]:
                rows.append([arm, float(rho), len(spec["seeds"])])
        grid[rung] = rows
    return grid


# --------------------------------------------------------------------------
# dry-plan cost model (fail-closed; ASM-1664 ceiling + ddc0 carve-out)
# --------------------------------------------------------------------------

def _cell_hours(manifest, rung, subset, filter_tasks):
    cm = manifest["cost_model"]
    fwd = 0.0
    gen = 0
    for b in filter_tasks:
        size = cm["bench_sizes"][b]
        if subset:
            size = min(size, manifest["subset_items_per_task"])
        if b == "gsm8k":
            gen += size
            fwd += size                       # gold-solution ppl pass
        else:
            fwd += size * cm["bench_options"][b]
    # fluency guard: arc_easy gold ppl comes free from its MC pass; if
    # arc_easy is filter-dropped it is still run for the guard (§5.1)
    if "arc_easy" not in filter_tasks:
        fwd += cm["bench_sizes"]["arc_easy"] * cm["bench_options"]["arc_easy"]
    hours = (fwd / cm["mc_forwards_per_sec"][rung]
             + gen * cm["gen_tokens_per_item"]
             / cm["gen_tok_per_sec"][rung]) / 3600.0
    return hours


def dry_plan_tier(manifest, tier, filter_tasks=None, log=print):
    """Fail-closed per-tier cost plan. Returns {jobs, gpu_hours, usd,
    worst_job_hours}. Raises ERR_DDC_COST on any breached cap."""
    cm = manifest["cost_model"]
    bud = manifest["budgets"]
    filt = list(filter_tasks or cm["assumed_filter"])
    rate = cm["usd_per_gpu_hour_a10g"]
    if tier == "ddc0":
        gpu_h = cm["g0_gpu_hours"]
        usd = gpu_h * rate + 6.0 * 0.20       # + CPU stats stage band
        worst = gpu_h
        jobs = build_jobs(manifest, tier)
    else:
        jobs = build_jobs(manifest, tier)
        gpu_h = 0.0
        worst = 0.0
        for j in jobs:
            rung = j["rung"]
            subset = (j["rho"] in manifest["subset_rhos"])
            h = _cell_hours(manifest, rung, subset,
                            filt if j["arm"] != "A0"
                            else manifest["eval"]["benchmarks"])
            if j["arm"] not in ("A0",):
                h += cm["surgery_overhead_hours"][rung]
                if j["arm"] in ("A1", "A2", "A3", "C1", "C2", "C3"):
                    h += cm["calibration_overhead_hours"][rung]
            gpu_h += h
            worst = max(worst, h)
        usd = gpu_h * rate
    log("DRY PLAN tier=%s (assumed filter: %s):" % (tier, ",".join(filt)))
    log("  %d job(s); est %.1f GPU-h; est $%.2f; worst single job %.2f h "
        "(cap %.0f h)" % (len(jobs), gpu_h, usd, worst,
                          bud["per_job_hours_cap"]))
    if worst > bud["per_job_hours_cap"]:
        raise SystemExit("ERR_DDC_COST: worst job %.2f h exceeds the %.0f h "
                         "Modal timeout bound — reshard before launching"
                         % (worst, bud["per_job_hours_cap"]))
    if tier == "ddc0" and usd > bud["ddc0_usd_cap"]:
        raise SystemExit("ERR_DDC_COST: ddc0 estimate $%.2f exceeds the "
                         "$%.2f carve-out (ASM-1730 band)"
                         % (usd, bud["ddc0_usd_cap"]))
    return {"tier": tier, "jobs": len(jobs), "gpu_hours": gpu_h,
            "usd": usd, "worst_job_hours": worst}


def dry_plan_campaign(manifest, filter_tasks=None, log=print):
    """All tiers + the fail-closed $60 campaign ceiling (ASM-1664)."""
    plans = [dry_plan_tier(manifest, t, filter_tasks, log) for t in TIERS]
    total = sum(p["usd"] for p in plans)
    cap = manifest["budgets"]["campaign_usd_cap"]
    log("CAMPAIGN total est $%.2f vs hard ceiling $%.2f" % (total, cap))
    if total > cap:
        raise SystemExit("ERR_DDC_COST: campaign estimate $%.2f exceeds "
                         "the $%.2f hard ceiling — DO NOT LAUNCH (MD-1 "
                         "scope; re-plan or drop cells)" % (total, cap))
    log("campaign dry-plan GREEN (fail-closed caps honoured)")
    return {"tiers": plans, "total_usd": total, "ceiling_usd": cap}


# --------------------------------------------------------------------------
# canonical finalisation (shared by monolithic runner and shard merger)
# --------------------------------------------------------------------------

ROW_KEYS = ("task", "item_id", "rung", "arm", "rho", "seed", "correct",
            "subset")


def row_sort_key(r):
    return (r["rung"], r["arm"], float(r["rho"]), int(r["seed"]),
            int(r["subset"]), r["task"], str(r["item_id"]))


def mock_t0_block(manifest):
    """SYNTHETIC campaign-level sidecar block for the $0 mock — identical
    bytes in every mock shard; NEVER a measurement. The real block is
    assembled by the runner identity at T0 (A0 baselines -> filter_set,
    power_sim_ddc1.py -> power_sim_result, license re-verification -> i4,
    corpus token parity -> i3) and staged to every shard."""
    return {
        "mock_disclosure": "SYNTHETIC mechanics-only T0 block",
        "filter_set": {"r135": ["arc_challenge", "arc_easy", "folio",
                                "gsm8k"],
                       "r360": ["arc_challenge", "arc_easy", "folio",
                                "gsm8k"]},
        "chance": manifest["eval"]["chance"],
        "i1_debug_iterations_used": 0,
        "i3_corpus_parity_valid": True,
        "i4_licenses_valid": True,
        "per_item_emission_valid": True,
        "power_sim_result": {
            "superiority_power_min_over_c": 0.95,
            "equivalence_power": 0.94,
            "least_favourable_c": 0.0,
            "infeasible_cells": [],
            "config": {"q_ref": 0.25, "campaigns": 2000,
                       "bootstrap": 10000, "seed": 20260712},
            "quick_mode": False,
            "mock": True},
        "ddc0_verdict_ref": "MOCK (real runs: registry/verdicts/ddc0.json)",
        "max_stat_outputs": {"winning_method": "ridge-cca",
                             "t_star": 0.4795, "n_layers_admitted": 12,
                             "source": "MOCK"},
    }


def finalize(shards, out_dir, mock, manifest):
    """shards: [(results_dict, rows_list, cells_list)]. Writes the three
    pinned-analysis inputs + the merged results json into out_dir and
    returns the merged results dict. Deterministic: canonical row order,
    sorted keys; the ONLY cross-run-varying fields are the measured cost
    ledger entries (usd/gpu_hours/wallClockHours), disclosed as parity
    exclusions in validate_mock.py."""
    os.makedirs(out_dir, exist_ok=True)
    suffix = "-mock" if mock else ""
    all_rows = []
    all_cells = []
    for _res, rows, cells in shards:
        all_rows.extend(rows)
        all_cells.extend(cells)
    all_rows.sort(key=row_sort_key)
    all_cells.sort(key=lambda c: (c["rung"], c["arm"], float(c["rho"]),
                                  int(c["seed"])))
    t0_blocks = [r["t0_block"] for r, _rw, _c in shards
                 if r.get("t0_block") is not None]
    if not t0_blocks:
        raise SystemExit("ERR_DDC_FINALIZE: no shard carries a t0_block")
    t0 = t0_blocks[0]

    # gate I-1: AND over every reported rotation check (rotated arms)
    i1_entries = {}
    for res, _rw, _c in shards:
        i1_entries.update(res.get("i1") or {})
    i1_valid = all(v.get("pass") for v in i1_entries.values()) \
        if i1_entries else True

    # gate I-2 (mechanics tripwire): C1@0.9 r135 pooled-item accuracy over
    # the filter set >= 95% of A0's — recomputed from rows in BOTH the
    # monolithic and merged paths (never trusted stored)
    filt = t0["filter_set"]

    def pooled(rung, arm, rho):
        acc = {}
        for r in all_rows:
            if (r["rung"] == rung and r["arm"] == arm
                    and float(r["rho"]) == rho and r["subset"] == 0
                    and r["task"] in filt.get(rung, [])):
                acc.setdefault((r["task"], r["item_id"]),
                               []).append(float(r["correct"]))
        if not acc:
            return None
        return sum(sum(v) / len(v) for v in acc.values()) / len(acc)

    a0_acc = pooled("r135", "A0", 1.0)
    c1_acc = pooled("r135", "C1", 0.9)
    i2_valid = bool(a0_acc and c1_acc is not None
                    and c1_acc >= manifest["gates"]
                    ["i2_c1_rho09_retention_min"] * a0_acc)

    a2_ran = any(c["arm"] == "A2" for c in all_cells)
    s2_ran = any(c["rung"] == "r360" for c in all_cells)

    a0_ppl = {}
    for c in all_cells:
        if c["arm"] == "A0" and c.get("gold_ppl_arc_easy") is not None:
            a0_ppl[c["rung"]] = c["gold_ppl_arc_easy"]

    usd_total = round(sum(r.get("usd_estimate", 0.0)
                          for r, _rw, _c in shards), 4)
    gpu_hours = round(sum(r.get("gpu_hours", 0.0)
                          for r, _rw, _c in shards), 4)

    items_path = os.path.join(out_dir, "items-ddc1%s.jsonl" % suffix)
    with open(items_path, "w") as f:
        for r in all_rows:
            f.write(json.dumps({k: r[k] for k in ROW_KEYS},
                               sort_keys=True) + "\n")
    cells_path = os.path.join(out_dir, "cells-ddc1%s.json" % suffix)
    with open(cells_path, "w") as f:
        json.dump({"cells": all_cells, "a0_gold_ppl": a0_ppl}, f,
                  indent=1, sort_keys=True)
    sidecar = {
        "filter_set": filt,
        "chance": t0["chance"],
        "i1_rotation_valid": i1_valid,
        "i1_debug_iterations_used": t0["i1_debug_iterations_used"],
        "i2_mechanics_valid": i2_valid,
        "i3_corpus_parity_valid": t0["i3_corpus_parity_valid"],
        "i4_licenses_valid": t0["i4_licenses_valid"],
        "per_item_emission_valid": t0["per_item_emission_valid"],
        "power_sim_result": t0["power_sim_result"],
        "a2_ran": a2_ran,
        "s2_ran": s2_ran,
        "ddc0_verdict_ref": t0["ddc0_verdict_ref"],
        "max_stat_outputs": t0["max_stat_outputs"],
        "usd_total": usd_total,
        "gpu_hours": gpu_hours,
        "expected_grid": build_expected_grid(manifest, a2_ran, s2_ran),
    }
    side_path = os.path.join(out_dir, "sidecar-ddc1%s.json" % suffix)
    with open(side_path, "w") as f:
        json.dump(sidecar, f, indent=1, sort_keys=True)
    res0 = shards[0][0]
    merged = {
        "experiment": "ddc1",
        "mode": "MOCK" if mock else "REAL",
        "outcome": res0.get("outcome", "OK"),
        "pins": res0["pins"],
        "n_rows": len(all_rows),
        "n_cells": len(all_cells),
        "records_file": os.path.basename(items_path),
        "records_sha256": sha256_file(items_path),
        "i1_results": i1_entries,
        "i2_recomputed": {"a0_pooled": a0_acc, "c1_rho09_pooled": c1_acc,
                          "valid": i2_valid},
        "a2_ran": a2_ran, "s2_ran": s2_ran,
        "usd_total": usd_total, "gpu_hours": gpu_hours,
        "wallClockHours": round(sum(r.get("wallClockHours", 0.0)
                                    for r, _rw, _c in shards), 4),
        "n_shards": len(shards),
        "shard_tags": sorted(str(r.get("shard_tag"))
                             for r, _rw, _c in shards),
    }
    with open(os.path.join(out_dir, "results-ddc1%s.json" % suffix),
              "w") as f:
        json.dump(merged, f, indent=1, sort_keys=True)
    return merged
