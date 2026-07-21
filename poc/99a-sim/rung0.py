"""S4.8 / §7 Rung-0 layer: nested cumulative interims + binding futility.

Per replication generate ONE accruing arm-side Rung-0 dataset (n_max concepts x
n_seeds records for the 5 Rung-0 arms T, unrev-A1..H; nonce screen scale
sigma_scr = sigma_comp; concept, concept x arm, seed, seed x arm, residual with
reviewer/consumer fractions folded into residual; substream 9; independent of
campaign data).  The four route contrasts D_hat_l(r) = mean(Y_r - Y_T) share the
T-arm and concept layer -> the pinned joint route correlation by construction.

Pilot estimates (Delta_hat_rev) are drawn JOINTLY N4(delta_p0, Sigma_p),
Sigma_p = s_p^2[(1-rho_p)I4 + rho_p J4], s_p = sigma_pilot/sqrt(n_p) (substream
10).  At each integer look l (§7 table) compute the one-sided upper prediction
bound

  U_l(r) = D_hat_l(r) + Delta_hat_rev(r) + B(r)
           + t_{1-alpha0/(4L), nu_hat} * sqrt(SE_l(r)^2 + s_p^2),
  B(r) = (kappa_pool+kappa_mix+kappa_budget)*max(|Delta_hat_rev(r)|, Delta_min),
  nu_hat = (SE_l^2+s_p^2)^2 / (SE_l^4/nu_D + s_p^4/nu_p),  nu_p = n_p-1.

Whole-branch termination iff at some look EVERY route U_l(r) < f.  Termination is
binding-futility-only (conservative for FWER).  F10 acceptance: the whole-branch
termination rate's exact one-sided 95% CP-upper bound <= tau_term0 = 0.055.
"""
import numpy as np
import pins
import copula
from inference import FamilyAnova
from stats_util import t_ppf, cp_upper, mc_se

_RUNG0_IDX = {a: i for i, a in enumerate(pins.RUNG0_ARMS)}  # T,A1,A2,A2IR,H


def _gen_rung0(t, gen):
    """Accruing Rung-0 arm-side dataset Y[5, n_max, n_seeds] (substream 9)."""
    n_max = t.n_nonce                # nonce budget identification (§7/R8f)
    arms = pins.RUNG0_ARMS
    A = len(arms)
    sig = pins.SIGMA_SCR
    # arm means: T = 0; unreviewed route r mean = d0(r) (true screen contrast).
    mu = np.array([0.0] + [t.rung_d0[r] for r in pins.RUNG0_ROUTES])
    scale = np.sqrt(pins.F_CONCEPT / 2.0) * sig
    coords = copula.sample_coords(gen, n_max, A, t.regime, t.rho, block_sizes=[A])
    b = gen.standard_normal(n_max) * np.sqrt(pins.F_CONCEPT) * sig
    v = gen.standard_normal(pins.N_SEEDS) * np.sqrt(pins.F_SEED) * sig
    av = gen.standard_normal((A, pins.N_SEEDS)) * np.sqrt(pins.F_SEED / 2.0) * sig
    # reviewer + consumer fractions folded into residual (no reviewer/consumer at Rung 0)
    rv = (pins.F_RESID + pins.F_REVIEWER + pins.F_CONSUMER) * sig ** 2 / 2.0
    eps = gen.standard_normal((A, n_max, pins.N_SEEDS)) * np.sqrt(rv)
    Y = (mu[:, None, None] + b[None, :, None] + (scale * coords).T[:, :, None]
         + v[None, None, :] + av[:, None, :] + eps)
    return Y


def run_rung0(t, ss):
    """Run the Rung-0 nested futility monitoring; return dict with terminated
    flag, per-look/route U bounds, and envelope-coverage per route."""
    Y = _gen_rung0(t, ss[pins.SS_RUNG0])
    n_max = t.n_nonce
    looks = pins.LOOK_TABLE[n_max]           # integer look sizes (§7 table)

    # joint pilot estimates (substream 10)
    s_p = pins.SIGMA_PILOT / np.sqrt(pins.N_PILOT)
    Sigma_p = s_p ** 2 * ((1 - pins.RHO_P) * np.eye(4) + pins.RHO_P * np.ones((4, 4)))
    mean_dp0 = np.array([t.rung_dp0[r] for r in pins.RUNG0_ROUTES])
    dhat_rev = ss[pins.SS_PILOT].multivariate_normal(mean_dp0, Sigma_p)
    nu_p = pins.N_PILOT - 1

    kap = pins.KAPPA_POOL + pins.KAPPA_MIX + pins.KAPPA_BUDGET
    tcoef = 1.0 - pins.ALPHA0 / (4 * pins.L_LOOKS)

    # true theta(r) and envelope coverage bookkeeping (per route)
    b_true = {r: t.s_b * kap * max(abs(t.rung_dp0[r]), pins.DELTA_MIN) for r in pins.RUNG0_ROUTES}
    theta_true = {r: t.rung_d0[r] + t.rung_dp0[r] + b_true[r] for r in pins.RUNG0_ROUTES}

    terminated = False
    envelope_cover = {r: False for r in pins.RUNG0_ROUTES}
    for li, n_l in enumerate(looks):
        an = FamilyAnova(Y[:, :n_l, :])
        all_below = True
        for ri, r in enumerate(pins.RUNG0_ROUTES):
            fit = an.contrast(_RUNG0_IDX[r], _RUNG0_IDX['T'])
            SE = fit.se
            nu_D = fit.nu
            B = kap * max(abs(dhat_rev[ri]), pins.DELTA_MIN)
            comb_var = SE ** 2 + s_p ** 2
            nu_hat = comb_var ** 2 / (SE ** 4 / nu_D + s_p ** 4 / nu_p)
            U = fit.theta_hat + dhat_rev[ri] + B + t_ppf(tcoef, nu_hat) * np.sqrt(comb_var)
            # envelope-coverage at the final look (does U cover the true theta?)
            if li == len(looks) - 1 and U >= theta_true[r]:
                envelope_cover[r] = True
            if not (U < pins.F_FUT):
                all_below = False
        if all_below:
            terminated = True
            break
    return {'terminated': terminated, 'envelope_cover': envelope_cover}


def run_rung0_cell(config_index, t, R):
    """Mock F10/P6 driver: whole-branch termination rate + CP-upper vs tau."""
    import seeds
    term = 0
    cover = {r: 0 for r in pins.RUNG0_ROUTES}
    for rr in range(R):
        sub = seeds.rep_substreams(config_index, rr)
        res = run_rung0(t, sub)
        if res['terminated']:
            term += 1
        for r in pins.RUNG0_ROUTES:
            if res['envelope_cover'][r]:
                cover[r] += 1
    rate = term / R
    return {
        'label': t.config_label, 'config_index': config_index, 'R': R,
        'termination_rate': rate, 'mcse': mc_se(rate, R),
        'cp_upper95': cp_upper(term, R),
        'tau_term0': pins.TAU_TERM0, 'tau_term': pins.TAU_TERM,
        'envelope_coverage': {r: cover[r] / R for r in pins.RUNG0_ROUTES},
    }
