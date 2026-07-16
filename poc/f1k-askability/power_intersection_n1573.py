#!/usr/bin/env python3
"""power_intersection_n1573.py — F1-K CO-PRIMARY INTERSECTION power sim
($0, blind; GPT-5.6 pre-run review-gate RUN-HOLD defect 2, 2026-07-15).

THE DEFECT: the frozen record's intersection disclosure carried a prose
figure ("full-PASS power at mu* plausibly ~0.70-0.75 under positive
dependence") that no simulation supported — the marginals alone only bound
P(all three co-primary rungs fire) to the Frechet interval
[max(0, 1 - sum(1-p_j)), min_j p_j] = [0.4102, 0.8001] at the committed
per-rung powers 0.8043 / 0.8058 / 0.8001 (ASM-2371).

THE FIX (this script): a JOINT-DEPENDENCE Monte-Carlo sim of the
probability that ALL THREE rungs fire simultaneously at mu* = +4.09 pts,
under the registered cluster-mean DGP with the cross-contrast dependence
modelled EXPLICITLY through the shared K arm:

    D_c^(j) = mu* + sd_c * ( sqrt(lambda) * A_c + sqrt(1-lambda) * E_c^(j) )

where sd_c^2 = DELTA*(RHO_U + (1-RHO_U)/m_c) is the registered per-cluster
marginal variance ([DES SSR-REV5]; marginals preserved EXACTLY for every
lambda), A_c is the shared (K-arm) noise component and E_c^(j) the
contrast-specific component. lambda = the cross-contrast cluster-mean
correlation, swept over the FULL grid {0, 0.25, 0.5, 0.75, 1} because the
true arm-level noise split is unknown pre-run (STIPULATED family:
equicorrelated Gaussian copula over cluster means; lambda = 0.5 is the
equal-arm-variance shared-K point, Corr = Var(K_c)/(Var(K_c)+Var(arm_c))).

FIDELITY ANCHOR: per contrast the sim REPLAYS the committed marginal run's
PRNG call sequence (seed sha256('20260713|<name>|C96'), noise first, then
the frozen +-1 sign-flip matrix — byte-identical to screen.py power_curve /
power_n1573.py), so at lambda=0 the realized per-rung marginal fire rates
REPRODUCE the committed 0.8043 / 0.8058 / 0.8001 EXACTLY (asserted below);
at every other lambda the marginals stay within MC noise of them.

Output: reports/power-intersection-n1573.json — the executable basis for
the /analysis/power_scope intersection disclosure and the record's
corrected assumption text.

$0, no GPU, no network, no model call, gold-label/model-outcome blind
(reads only the committed geometry report). Deterministic on re-run.
"""

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import numpy as np
import screen as sc  # frozen machinery/constants: POWER_SEED, N_SIM, B_FLIP,
                     # DELTA, RHO_U, MU_STAR, T_FIRE, CONTRASTS, _seed

C_APPROVED = 96
N_TEST_APPROVED = 1573
LAMBDAS = [0.0, 0.25, 0.5, 0.75, 1.0]   # full dependence grid (unknown split)
GE_CUT = 499                            # (1+ge)/(B+1) < 0.05 <=> ge<=499, B=1e4
CHUNK = 2000
STAMP = ("2026-07-15 fable RUN-HOLD defect-2 fix: co-primary intersection "
         "joint-dependence sim ($0, blind)")

# Committed per-rung marginals (poc/f1k-askability/reports/
# power-report-n1573.json, ASM-2371, MEASURED, seed 20260713).
COMMITTED = {"K-1": 0.8043, "K-2": 0.8058, "K-3": 0.8001}


def fire_vector(D, Z, rowsum, mu):
    """Per-dataset fire indicator of the exact licensing test (identical
    decision path to screen.py power_curve: add-one sign-flip p < 0.05 AND
    observed T >= +3 pts), chunked over datasets."""
    n_sim, C = D.shape
    fired = np.zeros(n_sim, dtype=bool)
    noise = D - mu                                    # (N_sim, C)
    for start in range(0, n_sim, CHUNK):
        end = min(start + CHUNK, n_sim)
        nz = noise[start:end]                         # (cs, C)
        zn = Z @ nz.T                                 # (B, cs)
        tb = (mu * rowsum[:, None] + zn) / C          # (B, cs)
        tobs = mu + nz.mean(axis=1)                   # (cs,)
        ge = (tb >= tobs[None, :]).sum(axis=0)        # (cs,)
        fired[start:end] = (ge <= GE_CUT) & (tobs >= sc.T_FIRE)
    return fired


def main():
    rep = json.load(open(HERE / "reports" / "power-report-n1573.json",
                         encoding="utf-8"))
    m_list = rep["geometry"]["m_list_by_rank"]
    if (len(m_list) != C_APPROVED or sum(m_list) != N_TEST_APPROVED
            or min(m_list) < sc.POWER_GATE_MIN_M):
        sc.fail("committed geometry report violates C=96/n=1573/m>=8")
    C = len(m_list)
    sd = np.sqrt(sc.DELTA * (sc.RHO_U + (1.0 - sc.RHO_U)
                             / np.asarray(m_list, dtype=np.float64)))
    mu = sc.MU_STAR

    # --- byte-identical replay of each contrast's committed PRNG stream ----
    E, Z, rowsum = {}, {}, {}
    for name, _R in sc.CONTRASTS:
        rng = np.random.default_rng(sc._seed(name, C))
        E[name] = rng.standard_normal((sc.N_SIM, C))       # committed noise
        Z[name] = (rng.integers(0, 2, size=(sc.B_FLIP, C), dtype=np.int8)
                   .astype(np.float64) * 2.0 - 1.0)        # committed flips
        rowsum[name] = Z[name].sum(axis=1)

    # shared (K-arm) component: its OWN deterministic sub-seed, disjoint from
    # every committed stream by construction of the label
    h = hashlib.sha256(("%d|intersection-shared|C%d"
                        % (sc.POWER_SEED, C)).encode())
    A = np.random.default_rng(int(h.hexdigest()[:16], 16)) \
        .standard_normal((sc.N_SIM, C))

    grid = []
    for lam in LAMBDAS:
        fires = {}
        for name, _R in sc.CONTRASTS:
            noise = sd[None, :] * (np.sqrt(lam) * A
                                   + np.sqrt(1.0 - lam) * E[name])
            D = mu + noise
            fires[name] = fire_vector(D, Z[name], rowsum[name], mu)
        inter = fires["K-1"] & fires["K-2"] & fires["K-3"]
        p_int = float(inter.mean())
        marg = {n: float(f.mean()) for n, f in fires.items()}
        if lam == 0.0:
            for n, want in COMMITTED.items():
                if round(marg[n], 4) != want:
                    sc.fail("lambda=0 marginal %s = %.4f != committed %.4f "
                            "— PRNG replay drift, STOP" % (n, marg[n], want))
            print("fidelity anchor: lambda=0 marginals reproduce the "
                  "committed 0.8043/0.8058/0.8001 EXACTLY")
        mc_se = round((p_int * (1 - p_int) / sc.N_SIM) ** 0.5, 5)
        grid.append({"lambda": lam, "intersection_power": round(p_int, 4),
                     "mc_se": mc_se,
                     "marginals": {n: round(v, 4) for n, v in marg.items()}})
        print("  lambda=%.2f: P(all three fire at mu*=+4.09) = %.4f "
              "(MC-SE %.5f)  marginals %s"
              % (lam, p_int, mc_se,
                 " ".join("%s=%.4f" % (n, marg[n]) for n in sorted(marg))))

    ps = [COMMITTED[n] for n in ("K-1", "K-2", "K-3")]
    frechet_lb = round(max(0.0, 1.0 - sum(1.0 - p for p in ps)), 4)
    frechet_ub = round(min(ps), 4)
    sim_lo = min(g["intersection_power"] for g in grid)
    sim_hi = max(g["intersection_power"] for g in grid)

    report = {
        "part": "co-primary intersection joint-dependence power sim "
                "(RUN-HOLD defect-2 fix)",
        "built": STAMP,
        "defect": "the frozen record's '~0.70-0.75' all-three-rungs figure "
                  "was unsupported prose; marginals alone only give the "
                  "Frechet interval below",
        "geometry": {"C": C, "n_test": N_TEST_APPROVED,
                     "m_list_source": "reports/power-report-n1573.json "
                                      "(ASM-2371 committed artifact)"},
        "params": {"seed": sc.POWER_SEED, "n_sim": sc.N_SIM,
                   "b_flip": sc.B_FLIP, "delta": sc.DELTA, "rho_u": sc.RHO_U,
                   "mu_star": sc.MU_STAR, "t_fire_pts": 3.0,
                   "lambda_grid": LAMBDAS,
                   "shared_component_seed_label": "20260713|intersection-"
                                                  "shared|C96"},
        "dgp": "D_c^(j) = mu* + sd_c*(sqrt(lambda)*A_c + sqrt(1-lambda)*"
               "E_c^(j)); sd_c^2 = delta*(rho_U+(1-rho_U)/m_c); registered "
               "marginal law preserved exactly at every lambda; per-contrast "
               "E and sign-flip matrices are the BYTE-IDENTICAL committed "
               "streams (fidelity anchor asserted at lambda=0)",
        "frechet_bounds_from_committed_marginals": {
            "lower": frechet_lb, "upper": frechet_ub,
            "basis": "assumption-free: max(0, 1-sum(1-p_j)) <= P(all 3) <= "
                     "min_j p_j at p = 0.8043/0.8058/0.8001"},
        "lambda_grid_results": grid,
        "intersection_power_range_under_family": {
            "lower": sim_lo, "upper": sim_hi,
            "at_equal_arm_variance_lambda_0.5":
                next(g["intersection_power"] for g in grid
                     if g["lambda"] == 0.5)},
        "MEASURED": "every lambda-grid intersection estimate (Monte-Carlo, "
                    "MC-SE ~= 0.005); the Frechet bounds are arithmetic on "
                    "the committed ASM-2371 marginals",
        "STIPULATED": "the dependence FAMILY (equicorrelated Gaussian copula "
                      "over cluster means via a shared component; the true "
                      "cross-contrast correlation lambda is unknown pre-run "
                      "and unmodellable without arm-level variance data) "
                      "and lambda=0.5 as the equal-arm-variance shared-K "
                      "point. The intersection is NOT separately powered to "
                      ">= 0.80 anywhere on the grid; the registered "
                      "maintainer criterion is PER-RUNG power >= 0.80 "
                      "(ASM-2371) and is unchanged.",
        "consequence": "elevated INCONCLUSIVE risk (2-of-3 shapes), NEVER a "
                       "false null: TOST/NULL rides only on K-1 and every "
                       "non-fire is scoped by the ~4.06-4.09-pt MDE wording "
                       "at /analysis/power_scope",
    }
    sc.write_json(HERE / "reports" / "power-intersection-n1573.json", report)
    print("\nFrechet (assumption-free): [%.4f, %.4f]; sim range under the "
          "shared-K family: [%.4f, %.4f]\n-> reports/power-intersection-"
          "n1573.json" % (frechet_lb, frechet_ub, sim_lo, sim_hi))


if __name__ == "__main__":
    main()
