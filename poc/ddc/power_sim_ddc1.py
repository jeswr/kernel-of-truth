#!/usr/bin/env python3
"""ddc1 gate I-5 v3 pre-registered power simulation (JOINT contrast model).

Design: docs/next/design/DDC.md §5.2 "Power gate v3" bullet + §8 gate I-5
[STIPULATED: PROPOSED-ASM-1720]. Re-review residual this script exists to
fix (poc/gpt56-review/ddc-rereview): Delta* is the MINIMUM of two
CORRELATED contrasts that SHARE the A1 outcome column (with R1 entering
as a mean over its three seed columns) — simulating each pairwise
contrast independently misstates min-statistic power; the contrasts must
be drawn from their JOINT per-item distribution, and the gate takes the
MINIMUM superiority power over the registered dependence grid c (the
least-favourable covariance configuration gates; the attaining c* is
disclosed, never assumed).

Data-generating model (JOINT, per item; ASM-1720 verbatim):
  Per filtered task t (n_t items, measured A0 accuracy p_t), each item
  draws the outcome vector (X_A1, X_M1, X_R1s0, X_R1s1, X_R1s2):
   1. X_A1 ~ Bernoulli(p_t).
   2. Each control column C flips RELATIVE to A1: given X_A1=1 it flips
      to 0 w.p. a = (q + Delta)/(2 p_t); given X_A1=0 it flips to 1 w.p.
      b = (q - Delta)/(2 (1 - p_t)) — reproducing pairwise discordance
      P(X_A1 != X_C) = q and true paired delta E[X_A1 - X_C] = Delta.
      Any (a, b) outside [0, 1] at any measured p_t makes the whole
      (q, Delta, c) cell INFEASIBLE-AT-MEASURED-p: recorded in
      infeasible_cells with the offending task and skipped — never
      clamped.
   3. Dependence: one Gaussian-copula latent vector per item with
      equicorrelation c across the 4 control columns, Z_C = sqrt(c) Z0 +
      sqrt(1-c) E_C (Z0, E_C iid N(0,1)); column C flips iff
      Phi(Z_C) < (a if X_A1 == 1 else b). Implemented in z-space via the
      exact equivalence Phi(Z) < u  <=>  Z < Phi^{-1}(u), with Phi(z) =
      0.5 (1 + erf(z / sqrt 2)) (scipy-free) and Phi^{-1} by bisection on
      the two scalar thresholds per task.
   4. Per item: d_AM = X_A1 - X_M1; d_AR = X_A1 - mean(X_R1s0..s2).

Analysis per simulated campaign = the EXACT registered pipeline
(ASM-1703): task-stratified paired bootstrap, B resamples of item
indices with replacement within task, the SAME resample applied to both
contrasts (realised as multinomial category-count resampling over the 16
joint (X_A1, X_M1, #R1-correct) categories — index-resampling and
count-resampling are the identical distribution because items within a
joint category carry identical (d_AM, d_AR)). Superiority reject iff the
5th-percentile (one-sided 95% LB, nearest rank) of the bootstrap min
statistics > 0. Equivalence leg: the pairwise A1-M1 marginal only, at
Delta = 0 cells: TOST pass iff the 90% percentile CI (5th, 95th) of mean
d_AM lies inside (-0.03, +0.03).

Grid: q in {0.10,0.15,0.20,0.25,0.30} x Delta in {0.0, 0.03} x
c in {0.0, 0.5, 1.0} (Delta in accuracy FRACTION; 0.03 = +3.0 points).
Superiority power is defined/reported at Delta = 0.03 cells, equivalence
power at Delta = 0.0 cells. Headline reductions: superiority = MINIMUM
over c at (q_ref = 0.25, Delta = 0.03) with the attaining c disclosed;
equivalence = minimum over c at (q_ref, Delta = 0) — the pairwise
marginal is c-invariant by construction, so the min is a conservative
Monte-Carlo tie-break, not a model choice. Closed-form pairwise anchor
(reported to stderr, never gating; it UPPER-bounds the min-statistic
leg): margin/SE = 0.03 / (sqrt(q_ref - Delta^2)/sqrt(n)).

Gate: superiority_ok = min-over-c power >= 0.9; equivalence_ok =
equivalence power >= 0.9; i5_pass = both. A --quick run (campaigns=100,
bootstrap=1000) carries quick_mode: true and can never gate (the
analysis script analysis/ddc1.py rejects quick-mode results).

Deterministic: numpy default_rng(seed) single stream, fixed grid order;
identical arguments give byte-identical result JSON.

CLI: python3 poc/ddc/power_sim_ddc1.py --pool pool.json --out result.json
     [--campaigns 2000] [--bootstrap 10000] [--seed 20260712] [--quick]
pool.json = {"tasks": [{"task": str, "n_items": int,
                        "a0_accuracy": float}, ...]}
"""

import argparse
import json
import math
import sys
import time

import numpy as np

SCHEMA = "ddc1-power-sim/1"
Q_GRID = (0.10, 0.15, 0.20, 0.25, 0.30)
DELTA_GRID = (0.0, 0.03)
C_GRID = (0.0, 0.5, 1.0)
Q_REF = 0.25            # stipulated reference discordance, ASM-1720
DELTA_BOUNDARY = 0.03   # SESOI in accuracy fraction (+3.0 points)
CHUNK = 250             # campaigns generated per numpy block (memory cap)

ERR = {"ERR_DDC1_POWERSIM_IO": 10, "ERR_DDC1_POWERSIM_MALFORMED": 11}


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(ERR[code])


def phi(z):
    """Standard normal CDF, scipy-free: 0.5*(1+erf(z/sqrt(2)))."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def phi_inv(u):
    """Scalar Phi^{-1} by bisection (thresholds are 2 scalars per task).
    Saturated endpoints map to +-38 (Phi indistinguishable from 0/1 in
    float64), used only for feasible u in [0, 1]."""
    if u <= 0.0:
        return -38.0
    if u >= 1.0:
        return 38.0
    lo, hi = -38.0, 38.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if phi(mid) < u:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def nearest_rank_idx(p, n):
    return max(0, min(n - 1, int(math.ceil(p * n)) - 1))


# joint category coding: code = X_A1*8 + X_M1*4 + k, k = #R1 seeds correct
def category_stats():
    dam = np.zeros(16)
    dar = np.zeros(16)
    for xa in (0, 1):
        for xm in (0, 1):
            for k in range(4):
                code = xa * 8 + xm * 4 + k
                dam[code] = xa - xm
                dar[code] = xa - k / 3.0
    return dam, dar


DAM_CAT, DAR_CAT = category_stats()


def cell_feasibility(tasks, q, delta):
    """INFEASIBLE-AT-MEASURED-p check per ASM-1720 step (2): never clamp."""
    viol = []
    for t in tasks:
        p = t["a0_accuracy"]
        a = (q + delta) / (2.0 * p)
        b = (q - delta) / (2.0 * (1.0 - p))
        if not (0.0 <= a <= 1.0 and 0.0 <= b <= 1.0):
            viol.append({"task": t["task"], "a": a, "b": b})
    return viol


def simulate_cell(rng, tasks, q, delta, c, campaigns, boot):
    """Returns (superiority_power, equivalence_power) for one grid cell.
    Both are computed from the same simulated campaigns; the caller
    reports each only where the design defines it."""
    n_tot = sum(t["n_items"] for t in tasks)
    sc, s1c = math.sqrt(c), math.sqrt(1.0 - c)
    per_task = []
    for t in tasks:
        p = t["a0_accuracy"]
        a = (q + delta) / (2.0 * p)
        b = (q - delta) / (2.0 * (1.0 - p))
        per_task.append((t["n_items"], p, phi_inv(a), phi_inv(b)))
    i05 = nearest_rank_idx(0.05, boot)
    i95 = nearest_rank_idx(0.95, boot)
    sup_hits = 0
    eq_hits = 0
    for start in range(0, campaigns, CHUNK):
        m = min(CHUNK, campaigns - start)
        counts_per_task = []
        for (n_t, p, za, zb) in per_task:
            # (1) X_A1 ~ Bernoulli(p_t)
            xa = (rng.random((m, n_t)) < p).astype(np.int64)
            # (3) equicorrelated Gaussian copula across the 4 columns
            z0 = rng.standard_normal((m, n_t))
            e = rng.standard_normal((m, n_t, 4))
            z = sc * z0[:, :, None] + s1c * e
            # (2) conditional flips: Phi(Z) < thr  <=>  Z < Phi^{-1}(thr)
            thr = np.where(xa == 1, za, zb)
            flips = z < thr[:, :, None]
            xm = np.where(flips[:, :, 0], 1 - xa, xa)
            k = np.where(flips[:, :, 1:], (1 - xa)[:, :, None],
                         xa[:, :, None]).sum(axis=2)
            code = xa * 8 + xm * 4 + k
            offs = code + 16 * np.arange(m)[:, None]
            cnt = np.bincount(offs.ravel(),
                              minlength=16 * m).reshape(m, 16)
            counts_per_task.append(cnt)
        # exact registered pipeline per campaign: task-stratified paired
        # bootstrap, SAME resample driving both contrasts (joint counts)
        for i in range(m):
            boot_am = np.zeros(boot)
            boot_ar = np.zeros(boot)
            for (n_t, _p, _za, _zb), cnt in zip(per_task,
                                                counts_per_task):
                w = rng.multinomial(n_t, cnt[i] / n_t, size=boot)
                boot_am += w @ DAM_CAT
                boot_ar += w @ DAR_CAT
            stat_min = np.minimum(boot_am, boot_ar) / n_tot
            if np.partition(stat_min, i05)[i05] > 0.0:
                sup_hits += 1
            am = np.sort(boot_am / n_tot)
            if am[i05] > -DELTA_BOUNDARY and am[i95] < DELTA_BOUNDARY:
                eq_hits += 1
    return sup_hits / campaigns, eq_hits / campaigns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--campaigns", type=int, default=2000)
    ap.add_argument("--bootstrap", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20260712)
    ap.add_argument("--quick", action="store_true",
                    help="campaigns=100 bootstrap=1000; smoke only, "
                         "never gates")
    args = ap.parse_args()
    try:
        with open(args.pool) as f:
            pool = json.load(f)
    except OSError as e:
        die("ERR_DDC1_POWERSIM_IO", str(e))
    except ValueError as e:
        die("ERR_DDC1_POWERSIM_MALFORMED", "json parse: %s" % e)
    tasks = pool.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        die("ERR_DDC1_POWERSIM_MALFORMED", "pool.tasks missing/empty")
    for t in tasks:
        if not isinstance(t, dict) or "task" not in t \
                or not isinstance(t.get("n_items"), int) \
                or t["n_items"] <= 0 \
                or not isinstance(t.get("a0_accuracy"), (int, float)) \
                or not (0.0 < t["a0_accuracy"] < 1.0):
            die("ERR_DDC1_POWERSIM_MALFORMED", "bad task entry: %r" % t)
    tasks = sorted(tasks, key=lambda t: t["task"])
    campaigns = 100 if args.quick else args.campaigns
    boot = 1000 if args.quick else args.bootstrap
    n_tot = sum(t["n_items"] for t in tasks)
    se = math.sqrt(Q_REF - DELTA_BOUNDARY ** 2) / math.sqrt(n_tot)
    sys.stderr.write(
        "power_sim_ddc1: pool n=%d, pairwise anchor margin/SE=%.2f at "
        "q_ref=%.2f (upper-bounds the min-statistic leg; never gates)\n"
        % (n_tot, DELTA_BOUNDARY / se, Q_REF))

    rng = np.random.default_rng(args.seed)
    grid = []
    infeasible_cells = []
    n_cells = len(Q_GRID) * len(DELTA_GRID) * len(C_GRID)
    done = 0
    t_start = time.time()
    projected = False
    for q in Q_GRID:
        for delta in DELTA_GRID:
            viol = cell_feasibility(tasks, q, delta)
            for c in C_GRID:
                if viol:
                    infeasible_cells.append(
                        {"q": q, "delta": delta, "c": c,
                         "reason": "INFEASIBLE-AT-MEASURED-p",
                         "violations": viol})
                    grid.append({"q": q, "delta": delta, "c": c,
                                 "superiority_power": None,
                                 "equivalence_power": None,
                                 "n_campaigns": 0, "infeasible": True})
                    done += 1
                    continue
                sup, eq = simulate_cell(rng, tasks, q, delta, c,
                                        campaigns, boot)
                grid.append({
                    "q": q, "delta": delta, "c": c,
                    "superiority_power": sup if delta > 0.0 else None,
                    "equivalence_power": eq if delta == 0.0 else None,
                    "n_campaigns": campaigns, "infeasible": False})
                done += 1
                if not projected:
                    per_cell = time.time() - t_start
                    sys.stderr.write(
                        "power_sim_ddc1: %.1fs/cell -> projected total "
                        "~%.1f min for %d cells\n"
                        % (per_cell, per_cell * n_cells / 60.0, n_cells))
                    projected = True
    # headline reductions at q_ref (gate I-5 v3): superiority = MIN over
    # the dependence grid c (least-favourable covariance gates)
    sup_rows = [r for r in grid
                if r["q"] == Q_REF and r["delta"] == DELTA_BOUNDARY
                and not r["infeasible"]]
    eq_rows = [r for r in grid
               if r["q"] == Q_REF and r["delta"] == 0.0
               and not r["infeasible"]]
    sup_min, c_star, eq_power = None, None, None
    if len(sup_rows) == len(C_GRID):
        sup_min = min(r["superiority_power"] for r in sup_rows)
        c_star = min(r["c"] for r in sup_rows
                     if r["superiority_power"] == sup_min)
    if len(eq_rows) == len(C_GRID):
        # pairwise marginal is c-invariant; min over c = conservative
        # Monte-Carlo tie-break (docstring)
        eq_power = min(r["equivalence_power"] for r in eq_rows)
    gate = {
        "superiority_ok": sup_min is not None and sup_min >= 0.9,
        "equivalence_ok": eq_power is not None and eq_power >= 0.9,
    }
    gate["i5_pass"] = gate["superiority_ok"] and gate["equivalence_ok"]
    result = {
        "schema": SCHEMA,
        "config": {"campaigns": campaigns, "bootstrap": boot,
                   "seed": args.seed, "q_ref": Q_REF,
                   "delta_boundary": DELTA_BOUNDARY,
                   "c_grid": list(C_GRID), "q_grid": list(Q_GRID),
                   "pool": {"tasks": tasks}},
        "grid": grid,
        "superiority_power_min_over_c": sup_min,
        "least_favourable_c": c_star,
        "equivalence_power": eq_power,
        "gate": gate,
        "mc_se_at_power_0.9": math.sqrt(0.9 * 0.1 / campaigns),
        "infeasible_cells": infeasible_cells,
        "quick_mode": bool(args.quick),
    }
    with open(args.out, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)
        f.write("\n")
    sys.stderr.write(
        "power_sim_ddc1: done in %.1fs; superiority_min_over_c=%s "
        "(c*=%s), equivalence=%s, i5_pass=%s, quick_mode=%s\n"
        % (time.time() - t_start, sup_min, c_star, eq_power,
           gate["i5_pass"], bool(args.quick)))


if __name__ == "__main__":
    main()
