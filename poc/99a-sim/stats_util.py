"""Exact Clopper-Pearson one-sided bounds and t helpers (S2/S6/S7 acceptance).

The FWER/power acceptance rules use exact one-sided (Clopper-Pearson)
binomial confidence bounds.  scipy.stats.beta gives the exact CP bounds via
the beta-quantile identities.
"""
import numpy as np
from scipy import stats


def cp_upper(k: int, n: int, conf: float = 0.95) -> float:
    """Exact one-sided (1-alpha) UPPER Clopper-Pearson bound on a binomial
    proportion given k successes in n trials.  conf = 1 - alpha (0.95)."""
    if n == 0:
        return 1.0
    if k == n:
        return 1.0
    alpha = 1.0 - conf
    return float(stats.beta.ppf(1.0 - alpha, k + 1, n - k))


def cp_lower(k: int, n: int, conf: float = 0.95) -> float:
    """Exact one-sided (1-alpha) LOWER Clopper-Pearson bound."""
    if n == 0:
        return 0.0
    if k == 0:
        return 0.0
    alpha = 1.0 - conf
    return float(stats.beta.ppf(alpha, k, n - k + 1))


def mc_se(p_hat: float, n: int) -> float:
    """Monte-Carlo standard error of a rejection-rate point estimate."""
    if n == 0:
        return 0.0
    return float(np.sqrt(p_hat * (1.0 - p_hat) / n))


def t_sf(t: float, nu: float) -> float:
    """Upper-tail (survival) of Student-t: P(T > t)."""
    return float(stats.t.sf(t, nu))


def t_cdf(t: float, nu: float) -> float:
    return float(stats.t.cdf(t, nu))


def t_ppf(q: float, nu: float) -> float:
    return float(stats.t.ppf(q, nu))
