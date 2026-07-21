"""S4.1 arm-side crossed-effects data-generating model (Rev8/R8a).

Per replication the DGM produces ARM-SIDE LONG-FORM observations
Y_{a,i,s(,k)} = mu_a + b_i + sqrt(f_concept/2)*sigma_j*C_i[a]
             + v_s + (av)_{a,s} [+ w_{r(a,i)}] [+ u_{k(a,i,s)}] + eps,
the SAME representation every ledger model is fitted to.  Concept main b_i and
seed main v_s cancel in every registered contrast (kept for faithfulness).
Consumer (UCT only) and reviewer (composite reviewed arms only) are assigned by
the PUBLISHED rotations; residual variance is layer-folded (S4.1) so the implied
per-pair difference variance equals sigma_j^2 for every registered contrast.

Substreams (pins.SS_*) and draw ordering follow S2.
"""
import numpy as np
import pins
import copula
from hypotheses import ParamVector


# ---- arm means (S4.1 anchors) ---------------------------------------------
def uct_means(t: ParamVector):
    mu = {'T': 0.0}
    for c in pins.CANDIDATES:
        mu[c] = t.uct[c]
    for a in pins.SH_NAT_ARMS:
        mu['S(%s)' % a] = mu[a] - t.sh_nat[a]
    return np.array([mu[a] for a in pins.UCT_ARMS], dtype=float)


def comp_means(t: ParamVector):
    mu = {'A0': 0.0}
    mu['A1'] = t.r_rev
    mu['A2'] = t.r_rev + t.r_cit
    mu['A2IR'] = t.r_rev + t.r_cit + t.r_IR
    mu['H'] = mu['A2IR'] + t.graph
    mu['E'] = max(mu['A0'], mu['A1'], mu['A2'], mu['A2IR'], mu['H']) + t.delta_E
    mu['S(H)'] = mu['H'] - t.sh_nonce['H']
    mu['S(A2IR)'] = mu['A2IR'] - t.sh_nonce['A2IR']
    return np.array([mu[a] for a in pins.COMP_ARMS], dtype=float)


def fmt_means(t: ParamVector, c: str):
    # arms order: T'(c), AST(c), VEC(c)
    return np.array([0.0, -t.fmt[(c, 'AST')], -t.fmt[(c, 'VEC')]], dtype=float)


# ---- generic arm-side family generator ------------------------------------
def _generate_family(mu, sigma_j, n, n_seeds, arm_names,
                     concept_coords, gens,
                     reviewed_idx=None, consumer=False,
                     resid_var=None):
    """Assemble Y[a,i,s] for one family.

    mu             : (A,) arm means
    concept_coords : (n, A) unit-variance concept x arm coords (scaled here)
    reviewed_idx   : dict arm_name->rev_arm_index for reviewed arms (composite);
                     None => no reviewer layer
    consumer       : True => UCT consumer rotation
    resid_var      : (A,) per-arm residual variance (layer-folded)
    gens           : dict of the substream Generators this family draws from
    """
    A = len(arm_names)
    scale = np.sqrt(pins.F_CONCEPT / 2.0) * sigma_j

    # concept main (cancels; drawn from concept stream)
    b = gens['concept'].standard_normal(n) * np.sqrt(pins.F_CONCEPT) * sigma_j
    # seed main (cancels) and seed x arm
    v = gens['seed'].standard_normal(n_seeds) * np.sqrt(pins.F_SEED) * sigma_j
    av = gens['seed'].standard_normal((A, n_seeds)) * np.sqrt(pins.F_SEED / 2.0) * sigma_j

    Y = (mu[:, None, None]
         + b[None, :, None]
         + (scale * concept_coords).T[:, :, None]      # (A, n, 1)
         + v[None, None, :]
         + av[:, None, :])

    # reviewer (composite reviewed arms only)
    if reviewed_idx is not None:
        w = gens['reviewer'].standard_normal(pins.N_REVIEWERS) * np.sqrt(pins.F_REVIEWER / 2.0) * sigma_j
        for a_i, a in enumerate(arm_names):
            if a in reviewed_idx:
                ri = (reviewed_idx[a] + np.arange(n)) % pins.N_REVIEWERS
                Y[a_i] += w[ri][:, None]

    # consumer (UCT only; k independent of s)
    if consumer:
        u = gens['consumer'].standard_normal(pins.N_CONSUMERS) * np.sqrt(pins.F_CONSUMER / 2.0) * sigma_j
        for a_i in range(A):
            ki = (a_i + np.arange(n)) % pins.N_CONSUMERS   # uct_arm_index = position in UCT_ARMS
            Y[a_i] += u[ki][:, None]

    # residual (layer-folded per-arm variance)
    eps = gens['resid'].standard_normal((A, n, n_seeds))
    Y = Y + eps * np.sqrt(resid_var)[:, None, None]
    return Y


def gen_uct(t: ParamVector, ss):
    """UCT family (natural, 10 arms).  ss = list of substream Generators."""
    n = t.n_nat
    mu = uct_means(t)
    coords = copula.sample_coords(ss[pins.SS_NAT_CONCEPT], n, len(pins.UCT_ARMS),
                                  t.regime, t.rho,
                                  block_sizes=[len(pins.UCT_ARMS)])
    # layer folding (S4.1): UCT resid var = (f_resid + f_reviewer)*sigma^2/2, all arms
    rv = (pins.F_RESID + pins.F_REVIEWER) * pins.SIGMA_UCT ** 2 / 2.0
    resid_var = np.full(len(pins.UCT_ARMS), rv)
    gens = {'concept': ss[pins.SS_NAT_CONCEPT], 'seed': ss[pins.SS_SEED_EFFECTS],
            'consumer': ss[pins.SS_CONSUMER], 'resid': ss[pins.SS_RESID_NAT]}
    Y = _generate_family(mu, pins.SIGMA_UCT, n, pins.N_SEEDS, pins.UCT_ARMS,
                         coords, gens, reviewed_idx=None, consumer=True,
                         resid_var=resid_var)
    return Y


def gen_composite_and_gate(t: ParamVector, ss, gate_thr=None):
    """Composite family (nonce, 8 arms) + gate indicators (4 gate arms).

    The nonce concept layer is drawn ONCE as 12 coordinates (8 composite arm
    coords + 4 gate dimensions) so composite and gate share the concept layer
    at the cell's rho (S4.3/S4.4).  gate_thr: precomputed per-cell gate
    thresholds (B4); None -> Gaussian ppf (valid only for non-beta regimes).
    """
    n = t.n_nonce
    nonce_dim = len(pins.COMP_ARMS) + len(pins.GATE_ARMS)   # 8 + 4
    block_sizes = [nonce_dim]      # nonce stratum is one block (block-2) in block regime
    nonce_coords = copula.sample_coords(ss[pins.SS_NONCE_CONCEPT], n, nonce_dim,
                                        t.regime, t.rho, block_sizes=block_sizes)
    comp_coords = nonce_coords[:, :len(pins.COMP_ARMS)]
    gate_coords = nonce_coords[:, len(pins.COMP_ARMS):]     # (n, 4) G_i[a]

    mu = comp_means(t)
    # layer folding (S4.1): reviewed arms (f_resid+f_consumer)/2; unreviewed
    # arms (f_resid+f_consumer+f_reviewer)/2.  (composite has no consumer -> fold)
    reviewed_idx = {a: i for i, a in enumerate(pins.REVIEWED_ARMS)}
    resid_var = np.empty(len(pins.COMP_ARMS))
    for i, a in enumerate(pins.COMP_ARMS):
        if a in reviewed_idx:
            resid_var[i] = (pins.F_RESID + pins.F_CONSUMER) * pins.SIGMA_COMP ** 2 / 2.0
        else:
            resid_var[i] = (pins.F_RESID + pins.F_CONSUMER + pins.F_REVIEWER) * pins.SIGMA_COMP ** 2 / 2.0
    gens = {'concept': ss[pins.SS_NONCE_CONCEPT], 'seed': ss[pins.SS_SEED_EFFECTS],
            'reviewer': ss[pins.SS_REVIEWER], 'resid': ss[pins.SS_RESID_NONCE]}
    Ycomp = _generate_family(mu, pins.SIGMA_COMP, n, pins.N_SEEDS, pins.COMP_ARMS,
                             comp_coords, gens, reviewed_idx=reviewed_idx,
                             consumer=False, resid_var=resid_var)

    gate = _gen_gate(t, gate_coords, ss, gate_thr=gate_thr)
    return Ycomp, gate


def gen_format(t: ParamVector, ss, c: str):
    """Stage-2 format family for candidate c (natural stratum, 3 arms
    T'(c), AST(c), VEC(c)); host-scored, no reviewer/consumer (S4.1 family D).
    Uses substream 8."""
    n = t.n_nat
    mu = fmt_means(t, c)
    coords = copula.sample_coords(ss[pins.SS_STAGE2_FMT], n, 3, t.regime, t.rho,
                                  block_sizes=[3])
    rv = (pins.F_RESID + pins.F_REVIEWER + pins.F_CONSUMER) * pins.SIGMA_F ** 2 / 2.0
    resid_var = np.full(3, rv)
    gens = {'concept': ss[pins.SS_STAGE2_FMT], 'seed': ss[pins.SS_SEED_EFFECTS],
            'resid': ss[pins.SS_STAGE2_FMT]}
    Y = _generate_family(mu, pins.SIGMA_F, n, pins.N_SEEDS, ['Tp', 'AST', 'VEC'],
                         coords, gens, reviewed_idx=None, consumer=False,
                         resid_var=resid_var)
    return Y   # arms: 0=T'(c), 1=AST(c), 2=VEC(c)


def _gen_gate(t: ParamVector, gate_coords, ss, gate_thr=None):
    """S4.4 gate DGM: pass indicators g_{a,i,s} for the 4 gate arms.

    Z = sqrt(f_c)*G_i[a] + sqrt(f_s)*v^g_s[a] + sqrt(f_r)*w^g_{r(a,i)}
        + sqrt(1-f_c-f_s-f_r)*e ; g = 1{Z > thr_a}.  Gaussian regime: thr_a =
    Phi^{-1}(1-pi_a) (exact marginal).  Bounded-Beta: thr recalibrated per cell
    (compute_gate_thresholds).  gate_thr overrides the on-the-fly Gaussian ppf.
    """
    from scipy import stats as _st
    n = t.n_nonce
    ga = pins.GATE_ARMS
    A = len(ga)
    fc, fsd, fr = pins.F_CONCEPT, pins.F_SEED, pins.F_REVIEWER
    fe = 1.0 - fc - fsd - fr
    gnoise = ss[pins.SS_GATE_NOISE]

    vg = gnoise.standard_normal((A, pins.N_SEEDS))          # v^g_s[a]
    wg = gnoise.standard_normal(pins.N_REVIEWERS)           # w^g reviewer pool
    e = gnoise.standard_normal((A, n, pins.N_SEEDS))        # residual latent

    # reviewer rotation over the reviewed-arm index of each gate arm
    rev_idx = {a: i for i, a in enumerate(pins.REVIEWED_ARMS)}
    Z = np.empty((A, n, pins.N_SEEDS))
    for a_i, a in enumerate(ga):
        conc = np.sqrt(fc) * gate_coords[:, a_i]            # (n,)
        ri = (rev_idx[a] + np.arange(n)) % pins.N_REVIEWERS
        wterm = np.sqrt(fr) * wg[ri]                        # (n,)
        Z[a_i] = (conc[:, None] + wterm[:, None]
                  + np.sqrt(fsd) * vg[a_i][None, :]
                  + np.sqrt(fe) * e[a_i])

    if gate_thr is None:                                    # on-the-fly Gaussian ppf
        gate_thr = np.array([_st.norm.ppf(1.0 - t.pi[a]) for a in pins.GATE_ARMS])
    g = (Z > np.asarray(gate_thr)[:, None, None]).astype(np.int8)
    return g


def compute_gate_thresholds(t: ParamVector, config_index: int,
                            n_draws: int = 10_000_000):
    """S4.4 per-cell gate threshold t_a (computed ONCE per cell, before any
    replication).  Gaussian/block regime: exact Phi^{-1}(1-pi_a).  Bounded-Beta:
    t_a = the (1-pi_a)-quantile of Z's marginal, estimated by n_draws (pinned
    10^7) Monte-Carlo draws on the dedicated per-cell calibration stream
    SeedSequence([BASE_SEED, config_index, 999_999_999]) — keeping P(g=1)=pi_a
    EXACT while the bounded-Beta shape supplies the dependence stress (R8d)."""
    from scipy import stats as _st
    import copula as _cop
    from seeds import beta_cal_stream
    ga = pins.GATE_ARMS
    if t.regime != 'beta':
        return np.array([_st.norm.ppf(1.0 - t.pi[a]) for a in ga])
    fc, fsd, fr = pins.F_CONCEPT, pins.F_SEED, pins.F_REVIEWER
    fe = 1.0 - fc - fsd - fr
    gen = beta_cal_stream(config_index)
    # draw Z's marginal in chunks (peak memory ~ one chunk); Z = sqrt(fc)*Cbeta
    # + sqrt(fsd)*N + sqrt(fr)*N + sqrt(fe)*N, Cbeta = standardized-Beta of N(0,1).
    Z = np.empty(n_draws)
    chunk = 1_000_000
    off = 0
    while off < n_draws:
        m = min(chunk, n_draws - off)
        y = gen.standard_normal(m)
        cbeta = _cop._beta_transform(y)
        Z[off:off + m] = (np.sqrt(fc) * cbeta
                          + np.sqrt(fsd) * gen.standard_normal(m)
                          + np.sqrt(fr) * gen.standard_normal(m)
                          + np.sqrt(fe) * gen.standard_normal(m))
        off += m
    return np.array([np.quantile(Z, 1.0 - t.pi[a]) for a in ga])
