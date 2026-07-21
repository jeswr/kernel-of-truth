"""S5 shared hypothesis-function module (the BINDING truth engine).

This single module defines the 12 null functions null_j(theta) over the
complete parameter vector.  Per SIM-SPEC S1/S5/S9 it is imported by BOTH:
  (a) the testing engine (graphical.py builds each claim's IUT components to
      target exactly these nulls), and
  (b) the per-cell truth derivation (truth_set below), which computes
      {j : null_j(theta) TRUE} programmatically.
No hand-maintained truth column exists anywhere.  S9 FORBIDS duplicating the
truth engine, so this is the one and only definition.

Margins are read from pins (S3); a cell is a ParamVector.
"""
from dataclasses import dataclass, field
from typing import Dict, Tuple
import pins


@dataclass
class ParamVector:
    """Complete parameter vector theta (S5).  Stored as overrides resolved
    against S3/S6 defaults by grid.resolve_cell()."""
    # --- 24 registered parameters ---
    sh_nat: Dict[str, float]              # Delta^SH_a natural, a in SH_NAT_ARMS (5)
    sh_nonce: Dict[str, float]            # Delta^SH_a nonce, a in SH_NONCE_ARMS (2)
    uct: Dict[str, float]                 # Delta^UCT_c, c in CANDIDATES (4)
    graph: float                          # Delta^G
    pi: Dict[str, float]                  # pi_a, a in GATE_ARMS (4)
    fmt: Dict[Tuple[str, str], float]     # Delta^F_{c,f}, (c,f) (8)
    # --- auxiliary pipeline parameters ---
    r_IR: float
    r_cit: float
    r_rev: float
    delta_E: float
    # rung-0 per-route (d0, dp0) and transfer-shift sign s_b
    rung_d0: Dict[str, float]             # d0(r), r in RUNG0_ROUTES
    rung_dp0: Dict[str, float]            # delta_p0(r)
    s_b: int                              # transfer-shift sign in {-1,0,+1}
    # cost table (S4.9) — kept at pinned defaults unless a cell overrides
    kappa_a: Dict[str, tuple] = field(default_factory=lambda: dict(pins.KAPPA_A))
    stage2_mode: str = 'endogenous'
    rho: float = 0.0
    regime: str = 'gaussian'              # 'gaussian' | 'beta' | 'block'
    n_nat: int = pins.N_NAT
    n_nonce: int = pins.N_NONCE
    # bookkeeping
    config_label: str = ''                # e.g. 'F3'
    kind: str = 'fwer'                    # 'fwer' | 'power' | 'gatecal'


# ---------- S5 null functions ----------------------------------------------
# Notation matches S5 verbatim.  Each returns True when the claim's UNION null
# holds (i.e. the claim is a TRUE null and any rejection of it is a Type-I
# error at that cell).

def null_CVAL(t: ParamVector) -> bool:
    # exists a: Delta^SH_a <= delta_S  (over all 7 shuffle contrasts)
    vals = list(t.sh_nat.values()) + list(t.sh_nonce.values())
    return any(v <= pins.DELTA_S for v in vals)


def null_CDEFNSUP(t: ParamVector) -> bool:
    # exists c: Delta^UCT_c >= m_T
    return any(v >= pins.M_T for v in t.uct.values())


def null_CDEFSUP(t: ParamVector) -> bool:
    # exists c: Delta^UCT_c >= -delta_T
    return any(v >= -pins.DELTA_T for v in t.uct.values())


def null_CCONSUP(t: ParamVector, c: str) -> bool:
    # (Delta^UCT_c <= delta_T) or (pi_c <= pi0)
    return (t.uct[c] <= pins.DELTA_T) or (t.pi[c] <= pins.PI0)


def null_CGRAPH(t: ParamVector) -> bool:
    # (Delta^G <= delta_G) or (pi_H <= pi0) or (pi_A2IR <= pi0)
    return (t.graph <= pins.DELTA_G) or (t.pi['H'] <= pins.PI0) or (t.pi['A2IR'] <= pins.PI0)


def null_CFMT(t: ParamVector, c: str) -> bool:
    # exists f: |Delta^F_{c,f}| >= m_F
    return any(abs(t.fmt[(c, f)]) >= pins.M_F for f in pins.FORMATS)


def is_null(claim: str, t: ParamVector) -> bool:
    """Dispatch: is `claim`'s null TRUE at parameter vector t?"""
    if claim == 'C-VAL':
        return null_CVAL(t)
    if claim == 'C-DEF-NSUP':
        return null_CDEFNSUP(t)
    if claim == 'C-DEF-SUP':
        return null_CDEFSUP(t)
    if claim.startswith('C-CON-SUP-'):
        return null_CCONSUP(t, claim[len('C-CON-SUP-'):])
    if claim == 'C-GRAPH':
        return null_CGRAPH(t)
    if claim.startswith('C-FMT-'):
        return null_CFMT(t, claim[len('C-FMT-'):])
    raise KeyError(claim)


def truth_set(t: ParamVector):
    """The error-counting set {j : null_j(theta) TRUE} (S1/S5), computed
    programmatically from the SAME functions the test engine targets."""
    return {c for c in pins.CLAIMS if is_null(c, t)}
