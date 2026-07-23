"""S1 object-under-test: one full-pipeline replication.

Order (S1/S4.8->S4.2-S4.7): generate arm-side DGM -> ledger contrast fits +
gate tests -> build IUT component p-values -> graphical procedure over Stage-1
claims -> Stage-2 endogenous trigger (C-FMT testable iff >=1 C-CON-SUP rejected)
-> continue graphical.  Errors are counted at CLAIM level by the driver against
hypotheses.truth_set (S1).

Stage-1 binding futility (S4.6) and the Rung-0 branch (S4.8/§7) are
binding-futility-only: they can only REMOVE rejection opportunities, hence are
conservative for FWER.  They are implemented in futility.py / rung0.py and wired
for the cells that exercise them; for cells whose futility/rung-0 parameters sit
far from their boundaries (all mock FWER/power cells here) they never fire, so
the core pipeline determines the result exactly.  See README / SPEC-DEFECTS.
"""
import pins
import dgm
import gate_test
import graphical
import futility
import rung0
import reml_composite
from inference import FamilyAnova
from hypotheses import ParamVector

_UCT_IDX = {a: i for i, a in enumerate(pins.UCT_ARMS)}
_COMP_IDX = {a: i for i, a in enumerate(pins.COMP_ARMS)}
_REV_OFF = {a: i for i, a in enumerate(pins.REVIEWED_ARMS)}


def run_replication(t: ParamVector, ss, want_selection=False,
                    use_futility=True, use_rung0=True, gate_thr=None):
    """Run one replication; return dict with rejected claims + diagnostics.

    use_futility / use_rung0 (default ON = full-run-ready) enable the S4.6
    Stage-1 binding futility and the S4.8/§7 Rung-0 branch.  Both are
    binding-futility-only (can only REMOVE rejection opportunities), and both
    draw ONLY from their own substreams (rung0: SS_RUNG0/SS_PILOT; futility:
    no new draws — reads the already-generated interim slice), so with them ON
    but non-firing the rejection vector is IDENTICAL to OFF (regression-safe).
    gate_thr: precomputed per-cell gate thresholds (S4.4 bounded-Beta, B4);
    None -> Gaussian ppf on the fly.
    """
    dS, mT, dT, dG, mF, pi0 = (pins.DELTA_S, pins.M_T, pins.DELTA_T,
                               pins.DELTA_G, pins.M_F, pins.PI0)

    # ---- Rung-0 nested-interim screen (S4.8/§7); terminated branch tests
    #      NO confirmatory claim (conservative) ----
    rung0_terminated = False
    if use_rung0:
        rung0_terminated = rung0.run_rung0(t, ss)['terminated']
        if rung0_terminated:
            return {'rejected': set(), 'stage2': False,
                    'rung0_terminated': True, 'futility_dropped': set(),
                    'graph_futile': False}

    # ---- DGM (S4.1) ----
    Yuct = dgm.gen_uct(t, ss)
    Ycomp, gate = dgm.gen_composite_and_gate(t, ss, gate_thr=gate_thr)

    # ---- ledger fits (S4.2/R10a/R11a): EXACT REML per rotated-block family ----
    # Families A (UCT/consumer) and B (composite/reviewer) use the exact 6-component
    # REML (reml_composite); the pooled-ANOVA closed form is retired (SPEC-DEFECTS
    # B2 + the family-A finding).  Families C/D unchanged.
    uct_anova = reml_composite.get_uct(t); uct_anova.fit(Yuct)
    comp_anova = reml_composite.get_comp(t); comp_anova.fit(Ycomp)
    # UCT contrasts: Delta^UCT_c (c vs T) and Delta^SH_a natural (a vs S(a))
    uct_fit = {c: uct_anova.contrast(_UCT_IDX[c], _UCT_IDX['T']) for c in pins.CANDIDATES}
    shnat_fit = {a: uct_anova.contrast(_UCT_IDX[a], _UCT_IDX['S(%s)' % a])
                 for a in pins.SH_NAT_ARMS}
    # composite contrasts: Delta^G (H vs A2IR) and nonce shuffles
    graph_fit = comp_anova.contrast(_COMP_IDX['H'], _COMP_IDX['A2IR'])
    shnonce_fit = {a: comp_anova.contrast(_COMP_IDX[a], _COMP_IDX['S(%s)' % a])
                   for a in pins.SH_NONCE_ARMS}

    # ---- gate tests (S4.4), consumed gate-by-gate in arm-index order ----
    boot = ss[pins.SS_GATE_BOOT]
    gate_p = {}
    for gi, a in enumerate(pins.GATE_ARMS):
        gate_p[a] = gate_test.gate_pvalue(gate[gi], _REV_OFF[a], pi0, boot)

    # ---- build IUT component p-values per claim (§4.6(1)/S5-targeted) ----
    comp = {}
    comp['C-VAL'] = ([shnat_fit[a].p_lower(dS) for a in pins.SH_NAT_ARMS]
                     + [shnonce_fit[a].p_lower(dS) for a in pins.SH_NONCE_ARMS])
    comp['C-DEF-NSUP'] = [uct_fit[c].p_upper(mT) for c in pins.CANDIDATES]
    comp['C-DEF-SUP'] = [uct_fit[c].p_upper(-dT) for c in pins.CANDIDATES]
    for c in pins.CANDIDATES:
        comp['C-CON-SUP-%s' % c] = [uct_fit[c].p_lower(dT), gate_p[c]]
    comp['C-GRAPH'] = [graph_fit.p_lower(dG), gate_p['H'], gate_p['A2IR']]

    # ---- Stage-1 binding futility (S4.6): drop candidates / stop graph ----
    dropped = set()
    graph_futile = False
    if use_futility:
        dropped, graph_futile = futility.stage1_futility(gate, Ycomp, t)

    # ---- graphical procedure, Stage 1 (S4.7: C-FMT not yet testable) ----
    state = graphical.GraphState(pins.ALPHA)
    testable = {cl: True for cl in pins.STAGE1_CLAIMS}
    for cl in pins.FMT_CLAIMS:
        testable[cl] = False
    for c in dropped:                              # futility-dropped: unrejectable
        testable['C-CON-SUP-%s' % c] = False
    if graph_futile:
        testable['C-GRAPH'] = False
    state.run(comp, testable)

    # ---- Stage-2 endogenous trigger (S4.7) ----
    stage2 = False
    con_rejected = any(('C-CON-SUP-%s' % c) in state.rejected for c in pins.CANDIDATES)
    if con_rejected and t.stage2_mode == 'endogenous':
        stage2 = True
        for c in pins.CANDIDATES:
            if c in dropped:                       # C-FMT-c also unrejectable
                continue
            Yf = dgm.gen_format(t, ss, c)          # arms 0=T'(c),1=AST,2=VEC
            fanova = FamilyAnova(Yf)
            comps = []
            for fi, f in enumerate(pins.FORMATS):
                fit = fanova.contrast(0, fi + 1)   # T'(c) - f(c) = Delta^F_{c,f}
                comps.append(fit.p_upper(mF))      # H0: Delta^F >= m_F
                comps.append(fit.p_lower(-mF))     # H0: Delta^F <= -m_F
            comp['C-FMT-%s' % c] = comps
            testable['C-FMT-%s' % c] = True
        state.run(comp, testable)                  # continue same update

    result = {'rejected': set(state.rejected), 'stage2': stage2,
              'rung0_terminated': False, 'futility_dropped': dropped,
              'graph_futile': graph_futile}
    if want_selection:
        result['selection'] = _select(uct_fit, graph_fit, dropped)
        result['fits'] = {'uct': uct_fit, 'graph': graph_fit}
    return result


def _select(uct_fit, graph_fit, dropped=frozenset()):
    """S4.5 hierarchy selection of c* (one-sided 95% lower bounds; fallback A1).
    Futility-dropped candidates (S4.6) are skipped."""
    g = pins.SELECTION_LEVEL
    gamma = 1.0 - g
    if 'H' not in dropped and graph_fit.lower_bound(gamma) > pins.DELTA_G:
        return 'H'
    if 'A2IR' not in dropped and (
            uct_fit['A2IR'].lower_bound(gamma) - uct_fit['A2'].lower_bound(gamma) > pins.M_IR):
        # (approximation: rung increments read off the UCT fits; the operative
        #  increments are on the composite scale — documented simplification)
        return 'A2IR'
    return 'A1'
