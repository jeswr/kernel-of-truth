#!/usr/bin/env python3
"""UFO-CHECK-0 frozen power simulation (review fix 1; PROPOSED-ASM-1494).

The registered n=600 power claim was a bare stipulation; this script makes
it a FROZEN, seed-pinned simulation over a registered scenario grid, run
BEFORE freeze and pinned in pins.artifact_hashes. Registered decision rule:
n=600 STANDS iff the minimum primary power over the a0 grid at the +0.05
margin is >= 0.80; otherwise n must be raised and the record re-drafted.

Mechanism-faithful data-generating model (design §3-§6):
  - 600 scored paired items: 200 gold-U + 400 gold-E/C (fixtures balance).
  - Gold-U items: d_AU = U rejects NOTHING (licensed-rejection contract),
    shared greedy first pass => paired diff == 0 identically.
  - Gold-E/C items: greedy first answer correct w.p. a0 (item-level,
    seed-invariant); AU rejects EXACTLY the wrong answers (the checker's
    disposition IS the gold on scored items — engine-derived gold), so the
    per-seed paired diff is +1 iff (first wrong AND retry correct), else 0.
    Retry success r is calibrated per scenario so the TRUE lift equals the
    target: lift = (N_EC/N) * (1-a0) * r.
  - Seeds {0,1,2} govern retry sampling only -> per-item diff in
    {0, 1/3, 2/3, 1} (seed mean) — exactly the quantity
    analysis/ufo_check_0.py bootstraps.
  - Test statistic: one-sided BCa bootstrap LB (B=10000, alpha=0.05) of the
    paired item mean — the SAME statistic as the pinned analysis, via the
    exact multinomial-over-value-classes equivalence (paired diffs take
    <= 4 values, so resampling items IS a multinomial draw over classes).

Also reported (sensitivity, never decision-bearing): type-I at true lift 0,
power at 0.03/0.08 true lifts, and s5 non-inferiority (margin +0.02) power
under dangerous-wrong churn scenarios on the 200 gold-C items.

Deterministic: numpy default_rng(20260712). CPU-only, $0, no network.
Output: poc/ufo-check-0/inputs/power-sim.json + stdout table.
"""

import json
import math
import os

import numpy as np

SEED = 20260712
B = 10000
M = 2000          # simulated datasets per scenario
ALPHA = 0.05
N_ITEMS = 600
N_EC = 400        # gold-E/C items (fixtures balance: 200 E + 200 C)
N_C = 200         # gold-C items (s5 mechanism lives here)
N_SEEDS = 3
MARGIN = 0.05     # the registered smallest effect of interest
DW_MARGIN = 0.02  # s5 non-inferiority margin (PROPOSED-ASM-1488)
A0_GRID = (0.20, 0.35, 0.50, 0.65, 0.80)
LIFT_SENS = (0.0, 0.03, 0.08)
DW_TRUE = (0.0, 0.01)          # true dangerous-wrong increases probed
DW_CHURN = (0.02, 0.05, 0.10)  # symmetric churn floor on gold-C items
POWER_REQUIRED = 0.80


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p, lo=-10.0, hi=10.0):
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def bca_bound_from_classes(rng, values, counts, n, alpha, upper=False):
    """One-sided BCa bound for the mean of n iid draws over value CLASSES
    (values[i] with multiplicity counts[i]) — exactly equivalent to
    resampling the n items with replacement (analysis bca_lb semantics)."""
    p_hat = counts / n
    theta = float(np.dot(p_hat, values))
    boots = np.sort(rng.multinomial(n, p_hat, size=B) @ values / n)
    prop = float(np.searchsorted(boots, theta, side="left")) / B
    z0 = norm_ppf(min(max(prop, 1e-9), 1 - 1e-9))
    # jackknife acceleration in closed form over classes
    s = theta * n
    jack = (s - values) / (n - 1)            # per-class leave-one-out mean
    jm = float(np.dot(counts, jack)) / n
    d = jm - jack
    num = float(np.dot(counts, d ** 3))
    den = 6.0 * (float(np.dot(counts, d ** 2)) ** 1.5) or 1e-12
    a = num / den
    zq = norm_ppf(1 - alpha if upper else alpha)
    adj = norm_cdf(z0 + (z0 + zq) / (1 - a * (z0 + zq)))
    idx = min(max(int(adj * B), 0), B - 1)
    return float(boots[idx])


def primary_power(rng, a0, lift):
    """P(BCa LB > 0) under the mechanism model at first-pass accuracy a0
    on gold-E/C items and calibrated retry success."""
    r = lift * N_ITEMS / (N_EC * (1.0 - a0))
    if r > 1.0:
        return None, r  # scenario infeasible (lift unreachable)
    hits = 0
    for _ in range(M):
        n_wrong = rng.binomial(N_EC, 1.0 - a0)
        k = rng.binomial(N_SEEDS, r, size=n_wrong)  # retry successes /item
        # value classes for the seed-mean diff: 0, 1/3, 2/3, 1
        counts = np.array([
            (N_ITEMS - n_wrong) + int(np.sum(k == 0)),
            int(np.sum(k == 1)), int(np.sum(k == 2)), int(np.sum(k == 3)),
        ], dtype=float)
        values = np.array([0.0, 1 / 3, 2 / 3, 1.0])
        lb = bca_bound_from_classes(rng, values, counts, N_ITEMS, ALPHA)
        if lb > 0:
            hits += 1
    return hits / M, r


def s5_power(rng, delta, churn):
    """P(BCa UB of the dangerous-wrong increase < +0.02) when the true
    increase is delta with symmetric churn on the N_C gold-C items.
    Per-item per-seed dw diff in {-1, 0, +1}: p+ = churn + delta*N/N_C
    scaled to the full 600-item mean; churn is the +/- floor."""
    p_plus = churn + delta * N_ITEMS / N_C
    p_minus = churn
    if p_plus + p_minus > 1.0:
        return None
    hits = 0
    vals3 = np.array([-1.0, 0.0, 1.0])
    p3 = np.array([p_minus, 1.0 - p_plus - p_minus, p_plus])
    # seed-mean over 3 draws -> 7 value classes in {-1..1}/3
    values = np.array([v / 3.0 for v in range(-3, 4)])
    for _ in range(M):
        draws = rng.choice(vals3, size=(N_C, N_SEEDS), p=p3).mean(axis=1)
        counts = np.zeros(7)
        for j, v in enumerate(values):
            counts[j] = int(np.sum(np.isclose(draws, v)))
        counts[3] += N_ITEMS - N_C  # gold E/U items: dw diff == 0
        ub = bca_bound_from_classes(rng, values, counts, N_ITEMS, ALPHA,
                                    upper=True)
        if ub < DW_MARGIN:
            hits += 1
    return hits / M


def main():
    rng = np.random.default_rng(SEED)
    out = {"seed": SEED, "B": B, "M": M, "alpha": ALPHA,
           "n_items": N_ITEMS, "n_ec": N_EC, "n_seeds": N_SEEDS,
           "margin": MARGIN, "a0_grid": list(A0_GRID),
           "decision_rule": "n=600 stands iff min primary power over the "
                            "a0 grid at true lift +0.05 >= 0.80",
           "primary": [], "sensitivity": [], "s5": []}
    print("primary power at the +0.05 margin (M=%d sims, B=%d BCa):" % (M, B))
    worst = 1.0
    for a0 in A0_GRID:
        p, r = primary_power(rng, a0, MARGIN)
        out["primary"].append({"a0_ec": a0, "retry_success": r, "power": p})
        worst = min(worst, p if p is not None else 0.0)
        print("  a0=%.2f  r=%.3f  power=%.3f" % (a0, r, -1 if p is None
                                                 else p))
    for lift in LIFT_SENS:
        for a0 in (0.35, 0.65):
            p, r = primary_power(rng, a0, lift)
            out["sensitivity"].append({"a0_ec": a0, "true_lift": lift,
                                       "retry_success": r,
                                       "power_or_type1": p})
            print("  sens: a0=%.2f lift=%.2f -> %s=%.3f"
                  % (a0, lift, "type-I" if lift == 0 else "power",
                     -1 if p is None else p))
    print("s5 non-inferiority power (margin +%.2f):" % DW_MARGIN)
    for delta in DW_TRUE:
        for churn in DW_CHURN:
            p = s5_power(rng, delta, churn)
            out["s5"].append({"true_increase": delta, "churn": churn,
                              "power": p})
            print("  delta=%.3f churn=%.2f  power=%s"
                  % (delta, churn, "n/a" if p is None else "%.3f" % p))
    out["min_primary_power_at_margin"] = worst
    out["n600_stands"] = worst >= POWER_REQUIRED
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "inputs", "power-sim.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print("min primary power at margin: %.3f -> n=600 %s (wrote %s)"
          % (worst, "STANDS" if out["n600_stands"] else
             "INSUFFICIENT — RAISE n", path))
    if not out["n600_stands"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
