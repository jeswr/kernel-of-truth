"""S4.6 Stage-1 binding-futility boundary (nominal, moment-based).

ONE interim look at ceil(0.5*n) concepts per stratum.  Binding-futility-only:
it can only make claims UNREJECTABLE for a replication (never rejects), hence is
conservative for FWER.

  (i) per candidate c: nominal one-sided 95% moment Wald UB on pi_c =
      pihat_c + 1.645*SE_mom(pihat_c), with (S4.6, R9a floored dependence)
      SE_mom^2 = (1/N^2)[ N*pihat(1-pihat)
                          + sum_q N_q*max(0, P11(rho_q; pihat) - pihat^2) ]
      over the ledger-C pair classes q using the SAME floored rho~ as the
      ledger-C bootstrap (widening-only; negative concordance-excess truncated
      at 0).  If UB < pi0 -> drop c (C-CON-SUP-c and C-FMT-c unrejectable,
      c excluded from S4.5 selection).
  (ii) nominal one-sided 95% UB on Delta^G < delta_G -> graph branch
       futility-stopped (C-GRAPH unrejectable).
UCT and arm T are never gated (so C-VAL/C-DEF are unaffected).
"""
import math
import numpy as np
import pins
import gate_test
from inference import FamilyAnova

_COMP_IDX = {a: i for i, a in enumerate(pins.COMP_ARMS)}
_REV_OFF = {a: i for i, a in enumerate(pins.REVIEWED_ARMS)}
_Z95 = 1.6448536269514722                      # Phi^{-1}(0.95)


def _pair_counts(I, S, R, off):
    """Design pair counts for the S4.6 moment SE over I interim concepts,
    S seeds, R reviewers with rotation offset off.  Returns
    (N_q_sameconcept, N_q_samerev_diffconcept_diffseed,
     N_q_sameseed_diffrev, N_q_sameseed_samerev)."""
    sizes = np.bincount((off + np.arange(I)) % R, minlength=R)
    SR = int(np.sum(sizes * (sizes - 1) // 2))     # same-reviewer concept pairs
    DR = I * (I - 1) // 2 - SR                      # diff-reviewer concept pairs
    q1 = I * (S * (S - 1) // 2)                     # same concept (=> same reviewer)
    q2 = SR * S * (S - 1)                           # same rev, diff concept, diff seed
    q3 = DR * S                                     # same seed, diff reviewer
    q4 = SR * S                                     # same seed, same reviewer
    return q1, q2, q3, q4


def _se_mom(pihat, rho_t, counts, N):
    """S4.6 moment SE given floored rho~ = (rho_c, rho_s, rho_r)."""
    rc, rs, rr = rho_t
    q1, q2, q3, q4 = counts
    z = gate_test.norm.ppf(1.0 - pihat)
    p2 = pihat * pihat

    def exc(rho):
        return max(0.0, gate_test.orthant_p11(min(rho, 0.98), z) - p2)   # widening only

    var = (N * pihat * (1.0 - pihat)
           + q1 * exc(rc + rr)
           + q2 * exc(rr)
           + q3 * exc(rs)
           + q4 * exc(rs + rr)) / (N * N)
    return math.sqrt(max(var, 0.0))


def stage1_futility(gate, Ycomp, t):
    """Return (dropped_candidates set, graph_futile bool)."""
    I_int = math.ceil(0.5 * t.n_nonce)             # interim size, nonce stratum
    S = pins.N_SEEDS
    R = pins.N_REVIEWERS
    N = I_int * S

    dropped = set()
    # (i) per-candidate gate futility
    for gi, c in enumerate(pins.GATE_ARMS):
        g_int = gate[gi][:I_int, :]
        pihat = float(g_int.mean())
        pihat = min(max(pihat, 1e-6), 1.0 - 1e-6)
        rho_t = gate_test.floored_triple(gate_test.estimate_rho_points(g_int, _REV_OFF[c]))
        counts = _pair_counts(I_int, S, R, _REV_OFF[c])
        ub = pihat + _Z95 * _se_mom(pihat, rho_t, counts, N)
        if ub < pins.PI0:
            dropped.add(c)

    # (ii) graph-branch futility on Delta^G interim
    Yc_int = Ycomp[:, :I_int, :]
    an = FamilyAnova(Yc_int)
    gfit = an.contrast(_COMP_IDX['H'], _COMP_IDX['A2IR'])
    graph_ub = gfit.upper_bound(0.05)              # nominal one-sided 95% UB
    graph_futile = graph_ub < pins.DELTA_G
    return dropped, graph_futile
