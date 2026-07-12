#!/usr/bin/env python3
"""deconf-b freeze-time power-sizing simulation (deconf-stageb-spec.md §1.6,
PROPOSED-ASM-1100 — MANDATORY at freeze; the simulation GOVERNS on conflict
with the §1.3 normal approximation).

WHAT IT DOES: draws per-item true paired differences from the pinned planning
decomposition (PROPOSED-ASM-1101 — sigma_b^2 = 0.0301 between-item,
sigma_w^2 = 0.1600 within-item seed noise, the retry-vs-retry maxima
DERIVED from the MEASURED stage-2 run records; Gaussian generative form,
STIPULATED-planning, disclosed: the discrete d-bar_i support at s=5 is
11-point and CLT-safe at n >= 250 per the spec), applies the ACTUAL paired
BCa machinery of the pinned analysis (identical bca_bounds algorithm,
vectorised; B = 10,000) and the ACTUAL Holm family decision rule
(PROPOSED-ASM-1107: the primary fires on its Holm-adjusted p over the
four-member family; the worst-case floor alpha/4 = 0.0125 is co-computed —
the conservative bound the §1.4 sizing used), and reports empirical power at
true Delta = 0.10 for the pinned (n = 333, s = 5), plus the TOST
co-disclosure at true Delta = 0.

Under the Delta = 0.10 alternative the family co-members are anchored at
their measured/planning effects (bridge ~ +0.25 measured at stage-2;
gsa - gra ~ +0.25; grd - gra ~ +0.05) and simulated as independent contrast
draws — a disclosed simplification (the contrasts share arms); the FLOOR
number is the sizing bar and is simplification-free.

CPU-only, ~$0 marginal compute, seeded (PRNG 20260711), numpy for speed
(local sizing artifact, NOT the pinned analysis — analysis/deconf_b.py stays
stdlib). Output: poc/deconf-b/power-sim-result.json + stdout summary.

Usage: nice -n 10 python3 poc/deconf-b/power_sim.py [--nsim 1000] [--B 10000]
"""
import argparse
import json
import math

import numpy as np

SEED = 20260711
N_ITEMS = 333
N_SEEDS = 5
SIGMA_B2 = 0.0301      # PROPOSED-ASM-1101 primary planning value
SIGMA_W2 = 0.1600      # PROPOSED-ASM-1101 primary planning value
SIGMA_B2_PESS = 0.0576  # pessimistic sensitivity (kernel-alone shape)
DELTA_ALT = 0.10       # PROPOSED-ASM-1013 effect target
DELTA_SUP = 0.05
DELTA_EQ = 0.05
ALPHA = 0.05
HOLM_FLOOR = ALPHA / 4.0
POWER_TARGET = 0.90
# family co-member true effects under the alternative (anchored, disclosed)
CO_EFFECTS = {"bridge_lift": 0.25, "grd_minus_gra": 0.05,
              "gsa_minus_gra": 0.25}


def draw_dbar(rng, n, delta, sigma_b2=SIGMA_B2, sigma_w2=SIGMA_W2,
              s=N_SEEDS):
    """Seed-averaged per-item paired differences at the planning
    decomposition: d-bar_i ~ N(delta, sigma_b2 + sigma_w2/s)."""
    sd = math.sqrt(sigma_b2 + sigma_w2 / s)
    return rng.normal(delta, sd, size=n)


def bca_lower(d, B, rng, level):
    """One BCa lower bound of the mean of d at the given lower-tail level —
    the SAME algorithm as analysis/deconf_b.py bca_bounds (z0 from the
    bootstrap distribution, acceleration from the item jackknife of the
    mean), vectorised."""
    n = d.size
    theta = d.mean()
    idx = rng.integers(0, n, size=(B, n))
    thetas = d[idx].mean(axis=1)
    below = np.count_nonzero(thetas < theta)
    frac = min(max(below / B, 1.0 / (B + 1)), B / (B + 1.0))
    from statistics import NormalDist
    nd = NormalDist()
    z0 = nd.inv_cdf(frac)
    # jackknife of the mean: (S - x_i) / (n - 1)
    jack = (d.sum() - d) / (n - 1)
    jbar = jack.mean()
    num = ((jbar - jack) ** 3).sum()
    den = 6.0 * (((jbar - jack) ** 2).sum() ** 1.5)
    a = 0.0 if den == 0 else num / den
    srt = np.sort(thetas)

    def bound(lv):
        z = nd.inv_cdf(lv)
        adj = nd.cdf(z0 + (z0 + z) / (1 - a * (z0 + z)))
        pos = min(max(int(adj * B), 0), B - 1)
        return float(srt[pos])
    return bound, thetas


def one_sided_p(thetas, null):
    B = thetas.size
    return (1 + int(np.count_nonzero(thetas <= null))) / (B + 1)


def holm_adjusted(pvals):
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * pvals[i])
        adj[i] = min(1.0, running)
    return adj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nsim", type=int, default=1000)
    ap.add_argument("--B", type=int, default=10000)
    ap.add_argument("--out", default="poc/deconf-b/power-sim-result.json")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    counters = {"floor_reject": 0, "family_reject": 0, "unadj_reject": 0,
                "tost_pass_at_zero": 0, "floor_reject_pess": 0}
    for _ in range(args.nsim):
        # --- alternative world: true Delta = 0.10 on the primary -------------
        d = draw_dbar(rng, N_ITEMS, DELTA_ALT)
        bound, thetas = bca_lower(d, args.B, rng, ALPHA)
        p_primary = one_sided_p(thetas, DELTA_SUP)
        # worst-case Holm floor (the §1.4 sizing bar)
        if bound(HOLM_FLOOR) > DELTA_SUP:
            counters["floor_reject"] += 1
        if bound(ALPHA) > DELTA_SUP:
            counters["unadj_reject"] += 1
        # actual Holm family (co-members anchored; independence disclosed)
        ps = [p_primary]
        for name, eff in CO_EFFECTS.items():
            dc = draw_dbar(rng, N_ITEMS, eff)
            idx = rng.integers(0, N_ITEMS, size=(args.B, N_ITEMS))
            th = dc[idx].mean(axis=1)
            null = DELTA_SUP if name == "bridge_lift" else 0.0
            ps.append(one_sided_p(th, null))
        if holm_adjusted(ps)[0] <= ALPHA:
            counters["family_reject"] += 1
        # pessimistic-sigma sensitivity at the floor (disclosed corner)
        dp = draw_dbar(rng, N_ITEMS, DELTA_ALT, sigma_b2=SIGMA_B2_PESS)
        bp, _ = bca_lower(dp, args.B, rng, ALPHA)
        if bp(HOLM_FLOOR) > DELTA_SUP:
            counters["floor_reject_pess"] += 1
        # --- null world: true Delta = 0 -> TOST co-disclosure ----------------
        d0 = draw_dbar(rng, N_ITEMS, 0.0)
        b0, _ = bca_lower(d0, args.B, rng, ALPHA)
        lo, hi = b0(ALPHA), b0(1 - ALPHA)
        if -DELTA_EQ < lo and hi < DELTA_EQ:
            counters["tost_pass_at_zero"] += 1

    ns = args.nsim
    se = lambda p: math.sqrt(max(p * (1 - p), 1e-12) / ns)
    res = {
        "schema": "deconfb-power-sim/1",
        "prng_seed": SEED,
        "nsim": ns,
        "B": args.B,
        "n_items": N_ITEMS,
        "n_seeds": N_SEEDS,
        "planning": {"sigma_b2": SIGMA_B2, "sigma_w2": SIGMA_W2,
                     "sigma_b2_pessimistic": SIGMA_B2_PESS,
                     "delta_alt": DELTA_ALT, "delta_sup": DELTA_SUP,
                     "delta_eq": DELTA_EQ,
                     "co_effects": CO_EFFECTS,
                     "generative_form": "Gaussian d-bar_i ~ N(delta, "
                                        "sigma_b2 + sigma_w2/s); STIPULATED-"
                                        "planning, disclosed (spec §1.3/§1.6)"},
        "power_floor_alpha_over_4": counters["floor_reject"] / ns,
        "power_floor_se": se(counters["floor_reject"] / ns),
        "power_holm_family": counters["family_reject"] / ns,
        "power_unadjusted": counters["unadj_reject"] / ns,
        "power_floor_pessimistic_sigma": counters["floor_reject_pess"] / ns,
        "tost_power_at_delta0": counters["tost_pass_at_zero"] / ns,
        "target": POWER_TARGET,
        "floor_meets_target": counters["floor_reject"] / ns >= POWER_TARGET,
        "normal_approx_reference": {"power_floor": 0.922,
                                    "power_realised_alpha_over_2": 0.955,
                                    "power_unadjusted": 0.978,
                                    "tost_power": 0.956,
                                    "source": "deconf-stageb-spec.md §1.4/§1.5 "
                                              "[DERIVED]"},
        "rule": "the simulation GOVERNS on conflict with the normal "
                "approximation (PROPOSED-ASM-1100); if floor_meets_target is "
                "false the size is revised before freeze",
    }
    with open(args.out, "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({k: res[k] for k in (
        "power_floor_alpha_over_4", "power_holm_family", "power_unadjusted",
        "power_floor_pessimistic_sigma", "tost_power_at_delta0",
        "floor_meets_target")}, indent=2))


if __name__ == "__main__":
    main()
