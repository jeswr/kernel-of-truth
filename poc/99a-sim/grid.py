"""S6/S7 configuration grid, override discipline, and config_index expansion.

Cells are OVERRIDES of the S6-preamble default vector; the resolved full vector
per cell is produced by resolve_cell().  Claim truth is NEVER authored here — it
is derived by hypotheses.truth_set() from the resolved vector (S5/S6).

Expansion order (pins config_index, S6/S7):
  FWER cells first: config row (F1..F11) -> n-level (base, then escalated where
  applicable) -> regime (gaussian, beta, then block-R where applicable) ->
  rho ascending.  Then power cells (config -> n-level -> rho).  Then the 4
  gate-calibration cells (rho ascending, then n_nonce ascending).
"""
import copy
import pins
from hypotheses import ParamVector

BASE_N = (pins.N_NAT, pins.N_NONCE)          # (48, 96)
ESC_N = (pins.N_NAT_ESC, pins.N_NONCE_ESC)   # (96, 160)


def make_default(n_nat, n_nonce, rho, regime):
    return ParamVector(
        sh_nat={a: 0.30 for a in pins.SH_NAT_ARMS},
        sh_nonce={a: 0.30 for a in pins.SH_NONCE_ARMS},
        uct={c: -0.15 for c in pins.CANDIDATES},
        graph=0.16,
        pi={a: 0.85 for a in pins.GATE_ARMS},
        fmt={(c, f): 0.0 for c in pins.CANDIDATES for f in pins.FORMATS},
        r_IR=0.10, r_cit=0.10, r_rev=0.10,
        delta_E=-0.10,
        rung_d0={r: 0.20 for r in pins.RUNG0_ROUTES},
        rung_dp0={r: 0.05 for r in pins.RUNG0_ROUTES},
        s_b=0,
        kappa_a=dict(pins.KAPPA_A),
        stage2_mode='endogenous',
        rho=rho, regime=regime, n_nat=n_nat, n_nonce=n_nonce,
    )


def _b_star(dp0):   # B*(r) from TRUE quantities (S4.8)
    return (pins.KAPPA_POOL + pins.KAPPA_MIX + pins.KAPPA_BUDGET) * max(abs(dp0), pins.DELTA_MIN)


# ---- per-config overrides (S6 / S7 tables) --------------------------------
def apply_overrides(label, t: ParamVector):
    dS, mT, dT, dG, mF, pi0 = pins.DELTA_S, pins.M_T, pins.DELTA_T, pins.DELTA_G, pins.M_F, pins.PI0
    C = pins.CANDIDATES
    if label == 'F1':
        for a in t.sh_nat: t.sh_nat[a] = dS
        for a in t.sh_nonce: t.sh_nonce[a] = dS
        for c in C: t.uct[c] = 0.16
        for a in t.pi: t.pi[a] = 0.85
    elif label == 'F2':
        for c in C: t.uct[c] = mT
    elif label == 'F3':
        for c in C: t.uct[c] = dT
        t.graph = dG
    elif label == 'F4':
        t.uct['H'] = dT
        for c in ['A2IR', 'A2', 'A1']: t.uct[c] = -0.15
        t.graph = dG
        t.pi['H'] = pi0
    elif label == 'F5':
        t.uct['H'] = 0.16; t.uct['A2IR'] = 0.16
        t.uct['A2'] = 0.04; t.uct['A1'] = 0.04
        t.graph = 0.16
        t.pi['H'] = pi0; t.pi['A2IR'] = pi0
        t.pi['A2'] = 0.85; t.pi['A1'] = 0.85
    elif label == 'F6':
        t.uct['H'] = 0.16
        for c in ['A2IR', 'A2', 'A1']: t.uct[c] = 0.04
        for a in t.pi: t.pi[a] = 0.85
        for k in t.fmt: t.fmt[k] = mF
        t.stage2_mode = 'endogenous'
    elif label == 'F7':
        apply_overrides('F6', t)
        t.stage2_mode = 'forced-off'
    elif label == 'F8':
        for c in C: t.uct[c] = -dT
    elif label == 'F9':
        t.uct['H'] = dT; t.uct['A2IR'] = dT
        t.uct['A2'] = -0.15; t.uct['A1'] = -0.15
        t.graph = 0.0
    elif label == 'F10':
        # theta_true(r) = f for every route; d0 = f - dp0 - B*(r), dp0 = +0.05, s_b = +1
        for r in pins.RUNG0_ROUTES:
            t.rung_dp0[r] = 0.05
            t.rung_d0[r] = pins.F_FUT - 0.05 - _b_star(0.05)
        t.s_b = 1
        # campaign params as F3
        for c in C: t.uct[c] = dT
        t.graph = dG
    elif label == 'F11':
        for c in C: t.uct[c] = mT
        for a in t.sh_nat: t.sh_nat[a] = dS
        for a in t.sh_nonce: t.sh_nonce[a] = dS
        t.graph = dG
        for a in t.pi: t.pi[a] = pi0
        for k in t.fmt: t.fmt[k] = mF
    # ---- power configs ----
    elif label == 'P1':
        for c in C: t.uct[c] = 0.0
    elif label == 'P2':
        for c in C: t.uct[c] = -0.16
    elif label == 'P3':
        t.uct['H'] = 0.16
        for c in ['A2IR', 'A2', 'A1']: t.uct[c] = 0.04
        t.graph = 0.16
        for a in t.pi: t.pi[a] = 0.85
    elif label == 'P4':
        apply_overrides('P3', t)
        t.fmt[('H', 'AST')] = 0.0; t.fmt[('H', 'VEC')] = 0.0
        t.stage2_mode = 'endogenous'
    elif label == 'P5':
        t.r_IR = 0.0; t.r_cit = 0.0; t.r_rev = 0.0
        t.uct['A1'] = 0.16
        for c in ['H', 'A2IR', 'A2']: t.uct[c] = 0.04
        for a in t.pi: t.pi[a] = 0.85
    elif label == 'P6':
        apply_overrides('P3', t)
        for r in pins.RUNG0_ROUTES:
            t.rung_d0[r] = 0.10
            t.rung_dp0[r] = 0.05
        t.s_b = 1
    elif label == 'GATECAL':
        for a in t.pi: t.pi[a] = pi0
    else:
        raise KeyError(label)
    return t


def resolve_cell(label, rho, regime, n_nat, n_nonce, kind='fwer'):
    t = make_default(n_nat, n_nonce, rho, regime)
    apply_overrides(label, t)
    t.config_label = label
    t.kind = kind
    return t


# ---- config_index expansion (S6/S7) ---------------------------------------
_FWER_FULL_RHO = ('F1', 'F2', 'F3', 'F11')      # rho in {0,.1,.5,.8}, regimes g+b(+block)
_FWER_REDUCED = ('F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10')  # rho in {.1,.8}, gaussian, base n


def enumerate_cells():
    """Return the ordered list of (config_index, kind, label, rho, regime,
    n_nat, n_nonce).  This is the normative index->cell mapping (S8)."""
    cells = []
    idx = 0

    def add(kind, label, rho, regime, n):
        nonlocal idx
        cells.append((idx, kind, label, rho, regime, n[0], n[1]))
        idx += 1

    # ---- FWER cells ----
    for label in ('F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11'):
        if label in _FWER_FULL_RHO:
            nlevels = [BASE_N] if label == 'F1' else [BASE_N, ESC_N]
            for ni, n in enumerate(nlevels):
                is_base = (n == BASE_N)
                for regime in ('gaussian', 'beta'):
                    for rho in pins.RHO_REGIMES:      # 0,.1,.5,.8
                        add('fwer', label, rho, regime, n)
                if is_base:                            # block-R only at base n
                    add('fwer', label, 0.0, 'block', n)
        else:  # F4..F10: reduced spread, gaussian, base n
            for rho in (0.1, 0.8):
                add('fwer', label, rho, 'gaussian', BASE_N)

    # ---- power cells ----
    for label in ('P1', 'P2', 'P3', 'P4', 'P5', 'P6'):
        for n in (BASE_N, ESC_N):
            for rho in (0.1, 0.5, 0.8):
                add('power', label, rho, 'gaussian', n)

    # ---- gate-calibration cells (rho ascending, then n_nonce ascending) ----
    for rho in (0.1, 0.8):
        for n_nonce in (96, 160):
            n_nat = pins.N_NAT if n_nonce == 96 else pins.N_NAT_ESC
            add('gatecal', 'GATECAL', rho, 'gaussian', (n_nat, n_nonce))
    return cells


def cell_by_label(label, rho=0.1, n='base', regime='gaussian', kind=None):
    """Convenience: resolve a single cell by label (for the mock driver)."""
    n_tuple = BASE_N if n == 'base' else ESC_N
    if kind is None:
        kind = 'power' if label.startswith('P') else ('gatecal' if label == 'GATECAL' else 'fwer')
    # find its config_index from the enumeration
    for (idx, k, lab, r, reg, nn, nc) in enumerate_cells():
        if lab == label and abs(r - rho) < 1e-9 and reg == regime and (nn, nc) == n_tuple:
            t = resolve_cell(label, rho, regime, nn, nc, kind=kind)
            return idx, t
    # not in grid (e.g. custom) -> synthesize with a high index
    t = resolve_cell(label, rho, regime, n_tuple[0], n_tuple[1], kind=kind)
    return 100000, t
