"""S4.3 concept-layer copula and regimes.

Produces, per stratum concept i, a coordinate vector (unit marginal variance)
with the configured dependence.  These are the concept x arm effects C_i[a]
(and gate dimensions G_i[a]); S4.1 scales them by sqrt(f_concept/2)*sigma_j.

Regimes (S4.3):
  gaussian : N(0,R), R = equicorrelation rho within the stratum.
  beta     : draw Gaussian Y~N(0,R), U=Phi(Y), replace each coord by the
             centered unit-variance standardized-Beta transform
             C~=(F_Beta^{-1}(U;a0,b0)-m0)/s0  (skew/bounded CONCEPT effect,
             R8d: theta enters ONCE via mu_a, NOT a second outcome marginal).
  block    : within-block rho_w, between-block rho_b (blocks within a stratum).

Correlation is the COPULA correlation R; realised product-moment correlations
under the Beta transform are an approximation to rho (disclosed, not silent).
"""
import numpy as np
from scipy import stats
import pins

# exact Beta(a0,b0) mean and SD for the standardizing transform (S4.3/R8d)
_M0 = pins.BETA_A0 / (pins.BETA_A0 + pins.BETA_B0)
_S0 = np.sqrt(pins.BETA_A0 * pins.BETA_B0 /
              ((pins.BETA_A0 + pins.BETA_B0) ** 2 * (pins.BETA_A0 + pins.BETA_B0 + 1)))


def _gaussian_equicorr(gen, n, dim, rho):
    """n x dim standard-normal coords with equicorrelation rho (rho in [0,1))."""
    if rho <= 0.0:
        return gen.standard_normal((n, dim))
    idio = gen.standard_normal((n, dim))
    common = gen.standard_normal((n, 1))
    return np.sqrt(1.0 - rho) * idio + np.sqrt(rho) * common


def _gaussian_block(gen, n, dim, block_sizes):
    """Two-level factor model giving within-block rho_w, between-block rho_b.
    block_sizes: list of ints summing to dim (order = coordinate order)."""
    rw, rb = pins.RHO_W, pins.RHO_B
    global_f = gen.standard_normal((n, 1))
    idio = gen.standard_normal((n, dim))
    out = np.sqrt(rb) * global_f + np.sqrt(1.0 - rw) * idio
    col = 0
    for bs in block_sizes:
        blk_common = gen.standard_normal((n, 1))
        out[:, col:col + bs] += np.sqrt(rw - rb) * blk_common
        col += bs
    return out


def _beta_transform(y):
    """Centered unit-variance standardized-Beta transform of Gaussian coords."""
    u = stats.norm.cdf(y)
    # clip to open interval for numerical safety at the tails
    u = np.clip(u, 1e-12, 1.0 - 1e-12)
    b = stats.beta.ppf(u, pins.BETA_A0, pins.BETA_B0)
    return (b - _M0) / _S0


def sample_coords(gen, n_concepts, dim, regime, rho, block_sizes=None):
    """Return (n_concepts x dim) coordinate array with unit marginal variance
    and the configured dependence.  For 'block', block_sizes partitions dim."""
    if regime == 'block':
        if block_sizes is None:
            block_sizes = [dim]
        y = _gaussian_block(gen, n_concepts, dim, block_sizes)
        return y  # block regime uses Gaussian marginals (S4.3)
    y = _gaussian_equicorr(gen, n_concepts, dim, rho)
    if regime == 'gaussian':
        return y
    if regime == 'beta':
        return _beta_transform(y)
    raise ValueError(f'unknown regime {regime}')
