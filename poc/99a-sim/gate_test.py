"""S4.4 / §4.6(1b)(C) gate component test: crossed-binary latent-probit
parametric bootstrap.

Statistic T_gate = pihat_a = mean of the pass indicators over the arm's I*S
records.  Nuisance dependence (rho_c, rho_s, rho_r) is estimated by inverting
by-class pairwise concordances through the bivariate-normal orthant
probability; the p-value is a parametric bootstrap at the null boundary
pi = pi0 with the estimated dependence (B_boot = 999), p = (1+#{pihat* >=
pihat})/(B+1).  Reject H0: pi_a <= pi0 at local level gamma iff p <= gamma.
"""
import numpy as np
from scipy.stats import norm, multivariate_normal
import pins

_RHO_MAX = 0.98


def orthant_p11(rho: float, z: float) -> float:
    """P(Z1 > z, Z2 > z) for standard bivariate normal with correlation rho.
    By symmetry = Phi2(-z,-z; rho)."""
    if rho <= 0.0:
        return float((1.0 - norm.cdf(z)) ** 2)
    cov = [[1.0, rho], [rho, 1.0]]
    return float(multivariate_normal.cdf([-z, -z], mean=[0.0, 0.0], cov=cov))


def invert_orthant(Q: float, z: float) -> float:
    """Solve orthant_p11(rho, z) = Q for rho in [0, RHO_MAX] by bisection to
    |d rho| <= 1e-6.  Q at or below the independence value pihat^2 -> rho = 0
    (S4.4/§4.6(1b): 'if no root, set rho = 0')."""
    lo, hi = 0.0, _RHO_MAX
    f_lo = orthant_p11(0.0, z)
    if Q <= f_lo:
        return 0.0
    f_hi = orthant_p11(_RHO_MAX, z)
    if Q >= f_hi:
        return _RHO_MAX
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if orthant_p11(mid, z) < Q:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-6:
            break
    return 0.5 * (lo + hi)


def _concordances(g: np.ndarray, off: int):
    """By-class pairwise concordances for one gate arm.

    g   : (n, S) pass indicators (0/1) for the arm.
    off : the arm's reviewed-arm-index offset (reviewer rotation
          r(i) = (off + i) mod n_reviewers).
    Returns (Q_cr, Q_s, Q_r):
      Q_cr = same-concept (=> same reviewer under the rotation), diff seed
      Q_s  = same-seed, diff concept, diff reviewer
      Q_r  = same-reviewer, diff concept, diff seed
    """
    n, S = g.shape
    nrev = pins.N_REVIEWERS
    rclass = (off + np.arange(n)) % nrev
    rowsum = g.sum(axis=1)          # per concept, over seeds
    colsum = g.sum(axis=0)          # per seed, over concepts

    # ---- Q_cr: same concept, diff seed ----
    # per concept unordered same-concept pairs of 1s = C(rowsum,2)
    npair_cr = n * (S * (S - 1) // 2)
    num_cr = np.sum(rowsum * (rowsum - 1) / 2.0)
    Q_cr = num_cr / npair_cr if npair_cr > 0 else 0.0

    # ---- Q_s: same seed, diff concept, diff reviewer ----
    # per seed: total diff-concept unordered pairs of 1s minus same-reviewer ones
    total_s = np.sum(colsum * (colsum - 1) / 2.0)          # over all diff-concept pairs
    same_rev_s = 0.0
    for c in range(nrev):
        idx = (rclass == c)
        cs = g[idx].sum(axis=0)                            # per seed, concepts in class c
        same_rev_s += np.sum(cs * (cs - 1) / 2.0)
    num_s = total_s - same_rev_s
    class_size = n // nrev
    n_diffrev_pairs_per_seed = (n * (n - 1) // 2) - nrev * (class_size * (class_size - 1) // 2)
    npair_s = S * n_diffrev_pairs_per_seed
    Q_s = num_s / npair_s if npair_s > 0 else 0.0

    # ---- Q_r: same reviewer, diff concept, diff seed ----
    num_r = 0.0
    cnt_r = 0
    for c in range(nrev):
        idx = np.where(rclass == c)[0]
        m = len(idx)
        if m < 2:
            continue
        gc = g[idx]                                        # (m, S)
        rs = gc.sum(axis=1)                                # (m,)
        # sum over ordered i!=i' in class of (rs_i*rs_i' - dot(gc_i, gc_i'))
        rs_outer = np.outer(rs, rs)
        dots = gc @ gc.T                                   # (m, m)
        M = rs_outer - dots                                # diff-seed products, ordered incl diag
        diag = np.diag(M).sum()
        num_r += (M.sum() - diag) / 2.0                    # unordered i<i'
        cnt_r += (m * (m - 1) // 2) * (S * (S - 1))        # unordered concept pairs * ordered seed pairs
    # per unordered concept pair, ordered diff-seed pairs count = S*(S-1); above
    # M already sums ordered seed pairs (s!=s'), so divide product by that count.
    Q_r = (num_r / cnt_r) if cnt_r > 0 else 0.0
    return Q_cr, Q_s, Q_r


def estimate_rho_points(g: np.ndarray, off: int):
    """POINT dependence estimates (rho_c, rho_s, rho_r) per S4.4/§4.6(1b)(C).
    UNCHANGED by R9a: concordance-class inversion, no-root -> 0, and the
    rho_c = max(0, rho_cr - rho_r) decomposition.  Each is naturally in
    [0, 0.98] (invert_orthant returns [0, 0.98], rho_c a nonneg difference)."""
    pibar = float(g.mean())
    pibar = min(max(pibar, 1e-6), 1.0 - 1e-6)
    z = norm.ppf(1.0 - pibar)
    Q_cr, Q_s, Q_r = _concordances(g, off)
    rho_r = invert_orthant(Q_r, z)
    rho_cr = invert_orthant(Q_cr, z)
    rho_s = invert_orthant(Q_s, z)
    rho_c = max(0.0, rho_cr - rho_r)
    return float(rho_c), float(rho_s), float(rho_r)


def floored_triple(rho_points):
    """R9a conservative bootstrap plug-in rho~ built from the POINT estimates
    in the pinned order: (i) FLOOR the two small-cluster components
    rho~_s = max(rho_hat_s, RHO_FLOOR), rho~_r = max(rho_hat_r, RHO_FLOOR),
    rho~_c = rho_hat_c (no concept floor); (ii) clip each into [0, 0.98];
    (iii) if the sum > 0.98, rescale proportionally to sum 0.98."""
    rho_c, rho_s, rho_r = rho_points
    # (i) floor (asymmetric: seed/reviewer only)
    tc = rho_c
    ts = max(rho_s, pins.RHO_FLOOR)
    tr = max(rho_r, pins.RHO_FLOOR)
    # (ii) clip
    tc = min(max(tc, 0.0), _RHO_MAX)
    ts = min(max(ts, 0.0), _RHO_MAX)
    tr = min(max(tr, 0.0), _RHO_MAX)
    # (iii) proportional rescale
    tot = tc + ts + tr
    if tot > _RHO_MAX:
        s = _RHO_MAX / tot
        tc, ts, tr = tc * s, ts * s, tr * s
    return tc, ts, tr


# backward-compatible alias: the dependence triple fed to the bootstrap (R9a).
def estimate_rhos(g: np.ndarray, off: int):
    """Return the FLOORED bootstrap plug-in rho~ (R9a)."""
    return floored_triple(estimate_rho_points(g, off))


def gate_pvalue(g: np.ndarray, off: int, pi0: float, boot_gen,
                B: int = pins.B_BOOT, return_diag: bool = False):
    """Parametric-bootstrap p-value for H0: pi_a <= pi0 (S4.4), R9a: the
    null-boundary bootstrap consumes the FLOORED plug-in rho~.  With
    return_diag, also return per-replication dispersion/floor diagnostics."""
    n, S = g.shape
    pihat = float(g.mean())
    pts = estimate_rho_points(g, off)                      # POINT estimate
    rho_c, rho_s, rho_r = floored_triple(pts)              # R9a bootstrap plug-in
    rest = max(0.0, 1.0 - rho_c - rho_s - rho_r)
    z0 = norm.ppf(1.0 - pi0)
    nrev = pins.N_REVIEWERS
    ri = (off + np.arange(n)) % nrev

    # vectorised bootstrap: (B, ...) latent draws from the null-boundary model
    b_star = boot_gen.standard_normal((B, n))
    v_star = boot_gen.standard_normal((B, S))
    w_star = boot_gen.standard_normal((B, nrev))
    e_star = boot_gen.standard_normal((B, n, S))
    Z = (np.sqrt(rho_c) * b_star[:, :, None]
         + np.sqrt(rho_s) * v_star[:, None, :]
         + np.sqrt(rho_r) * w_star[:, ri][:, :, None]
         + np.sqrt(rest) * e_star)
    pistar = (Z > z0).mean(axis=(1, 2))                    # (B,)
    p = (1.0 + np.count_nonzero(pistar >= pihat)) / (B + 1.0)
    if return_diag:
        return float(p), {
            'pihat': pihat,
            'pistar_sd': float(pistar.std()),              # bootstrap-null SD
            'rho_points': pts,                             # (rho_hat_c, _s, _r)
            'rho_tilde': (rho_c, rho_s, rho_r),            # floored plug-in
        }
    return float(p)
