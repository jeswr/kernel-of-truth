"""Cell driver: run R replications of one resolved cell, count claim-level
errors / path events, and report point estimates with MC-SE and exact
one-sided Clopper-Pearson bounds (S6/S7 acceptance rules).

For the MOCK this runs a few hundred to ~2000 reps (NEVER the full R).
"""
import time
import numpy as np
import pins
import seeds
import pipeline
import dgm
import reml_composite
from hypotheses import truth_set
from stats_util import cp_upper, cp_lower, mc_se

# S4.2 registered per-cell fit-failure ceiling (acceptance requires <= 0.1%).
FIT_FAILURE_CEILING = 0.001


def run_cell(config_index, t, R, want_paths=False, progress=False,
             use_futility=True, use_rung0=True):
    """Run R reps of resolved cell t (config_index for the seed map).

    Fit-failure handling (S4.2 pinned + grid-run-v2 hardening; Rev2 governance
    item 7 — the REGISTERED S6 statistic is UNCHANGED): a rep whose exact-REML
    fit raises reml_composite.FitFailure (after the in-fit penalty guard AND
    the pinned second-start retry) is counted durably per cell and never
    rejects any component (S4.2).  Three SEPARATE quantities are reported:

      * REGISTERED S6 GATE = the realised OBSERVED FWER count ('fwer_events')
        over the completed reps — the pre-registered statistic, NOT altered
        (S4.2 counts fit-failures separately; S9 forbids changing acceptance).
      * NON-GATING worst-case SENSITIVITY ('fwer_events_worstcase' =
        observed + fit_failures): every failure counted as an event, which
        dominates every completion of a failed rep, so its CP-upper is an
        upper bound on the true FWER under arbitrary failure/rejection
        dependence.  DISCLOSED only — never the verdict statistic.
      * RUN-VALIDITY ceiling ('fit_failure_ceiling_pass'): the S4.2 per-cell
        fit-failure rate must be <= 0.1%; enforced SEPARATELY by the verdict
        (a breach makes the run INVALID, not an acceptance).

    Power paths: unconditional estimands keep denominator R (a failure is a
    miss — conservative).  The one CONDITIONAL estimand P4 (CFMTH | conH) uses
    the worst-case conditional denominator conH_count + fit_failures with the
    OBSERVED numerator (Rev2 fix for review item 5)."""
    T = truth_set(t)                       # {j : null_j true} — error-counting set
    # per-cell gate thresholds computed ONCE before replications (S4.4/B4)
    gate_thr = dgm.compute_gate_thresholds(t, config_index)
    claim_rej = {c: 0 for c in pins.CLAIMS}
    fwer_events = 0                        # >=1 TRUE-null claim rejected
    stage2_count = 0
    # path counters (power cells)
    paths = {'CVAL_DEFNSUP': 0, 'CVAL_CONSUPH_GRAPH': 0, 'CFMTH_given_conH': 0,
             'conH_count': 0, 'CDEFSUP': 0, 'CCONSUP_A1': 0}
    n_fitfail = 0
    fitfail_detail = []                    # capped; durable per-cell record
    t0 = time.time()
    for r in range(R):
        ss = seeds.rep_substreams(config_index, r)
        try:
            res = pipeline.run_replication(t, ss, use_futility=use_futility,
                                           use_rung0=use_rung0, gate_thr=gate_thr)
        except reml_composite.FitFailure as e:
            # S4.2 pinned rule: the failure is counted; no component of the
            # rep is rejected.  It does NOT touch the OBSERVED S6 gate count;
            # the accounting below adds it to the worst-case sensitivity
            # (observed + failures), inflates the P4 conditional denominator,
            # and flags the run-validity ceiling.
            n_fitfail += 1
            if len(fitfail_detail) < 50:
                fitfail_detail.append({'rep': r, 'family': e.family,
                                       'stage': e.stage, 'error': str(e)})
            continue
        rej = res['rejected']
        if res['stage2']:
            stage2_count += 1
        for c in rej:
            claim_rej[c] += 1
        if rej & T:
            fwer_events += 1
        if want_paths:
            if ('C-VAL' in rej) and ('C-DEF-NSUP' in rej):
                paths['CVAL_DEFNSUP'] += 1
            if ('C-VAL' in rej) and ('C-CON-SUP-H' in rej) and ('C-GRAPH' in rej):
                paths['CVAL_CONSUPH_GRAPH'] += 1
            if 'C-CON-SUP-H' in rej:
                paths['conH_count'] += 1
                if 'C-FMT-H' in rej:
                    paths['CFMTH_given_conH'] += 1
            if 'C-DEF-SUP' in rej:
                paths['CDEFSUP'] += 1
            if 'C-CON-SUP-A1' in rej:
                paths['CCONSUP_A1'] += 1
        if progress and (r + 1) % 200 == 0:
            print(f'  ... {r+1}/{R}  fwer_events={fwer_events}', flush=True)
    elapsed = time.time() - t0

    # REGISTERED S6 GATE STATISTIC = the realised OBSERVED FWER count (S4.2 /
    # S9: unchanged by the numerical guard; fit-failures are counted SEPARATELY
    # and never rejected).  The worst-case count is a DISCLOSED sensitivity.
    fwer_hat = fwer_events / R
    fwer_events_wc = fwer_events + n_fitfail
    fit_failure_rate = n_fitfail / R
    out = {
        'config_index': config_index,
        'label': t.config_label, 'kind': t.kind,
        'rho': t.rho, 'regime': t.regime, 'n_nat': t.n_nat, 'n_nonce': t.n_nonce,
        'R': R,
        'truth_set': sorted(T),
        # --- REGISTERED S6 gate (OBSERVED count) ---
        'fwer_events': fwer_events,
        'fwer_hat': fwer_hat,
        'fwer_mcse': mc_se(fwer_hat, R),
        'fwer_cp_upper95': cp_upper(fwer_events, R),
        # --- NON-GATING worst-case sensitivity (failures-as-events) ---
        'fwer_events_worstcase': fwer_events_wc,
        'fwer_hat_worstcase': fwer_events_wc / R,
        'fwer_cp_upper95_worstcase': cp_upper(fwer_events_wc, R),
        # --- run-validity fit-failure ceiling (S4.2, enforced separately) ---
        'fit_failures': n_fitfail,
        'fit_failure_rate': fit_failure_rate,
        'fit_failure_ceiling': FIT_FAILURE_CEILING,
        'fit_failure_ceiling_pass': fit_failure_rate <= FIT_FAILURE_CEILING,
        'fit_failure_detail': fitfail_detail,
        'claim_rej_rate': {c: claim_rej[c] / R for c in pins.CLAIMS},
        'stage2_rate': stage2_count / R,
        'elapsed_s': elapsed,
        'sec_per_rep': elapsed / R,
    }
    if want_paths:
        out['paths'] = {}
        for name in ('CVAL_DEFNSUP', 'CVAL_CONSUPH_GRAPH', 'CDEFSUP', 'CCONSUP_A1'):
            k = paths[name]
            out['paths'][name] = {
                'rate': k / R, 'mcse': mc_se(k / R, R),
                'cp_lower95': cp_lower(k, R),
            }
        # P4 is the one CONDITIONAL estimand P(FMT | conH).  Worst-case
        # conservative completion (Rev2 fix for review item 5): keep the
        # OBSERVED numerator, inflate the conditional denominator by the
        # fit-failures (conH_count + fit_failures) so correlated failures can
        # only DEFLATE the reported conditional rate, never inflate it.  With
        # zero failures this reduces to the observed conditional exactly.
        ch_obs = paths['conH_count']
        num = paths['CFMTH_given_conH']
        ch_wc = ch_obs + n_fitfail
        out['paths']['CFMTH_given_conH'] = {
            'rate': (num / ch_wc) if ch_wc else None,
            'n_cond': ch_wc,                 # worst-case denominator (verdict reads this)
            'n_cond_observed': ch_obs,
            'numerator': num,
        }
    return out


def print_report(out):
    print(f"\n=== cell {out['label']} idx={out['config_index']} "
          f"rho={out['rho']} regime={out['regime']} "
          f"n=({out['n_nat']},{out['n_nonce']}) R={out['R']} ===")
    print(f"  truth set (TRUE nulls): {out['truth_set']}")
    print(f"  FWER (>=1 true-null rejected) [REGISTERED S6, observed]: "
          f"{out['fwer_hat']:.5f} +/- {out['fwer_mcse']:.5f} (MC-SE)   "
          f"CP-upper95={out['fwer_cp_upper95']:.5f}")
    if out.get('fit_failures'):
        print(f"  FIT-FAILURES: {out['fit_failures']}/{out['R']} "
              f"(rate {out['fit_failure_rate']:.2e}; S4.2 ceiling "
              f"{out['fit_failure_ceiling']:g} "
              f"{'PASS' if out['fit_failure_ceiling_pass'] else 'FAIL -> RUN INVALID'})")
        print(f"  worst-case FWER sensitivity (failures-as-events, NON-GATING): "
              f"events {out['fwer_events_worstcase']}  "
              f"CP-upper95={out['fwer_cp_upper95_worstcase']:.5f}")
    print(f"  stage2 rate: {out['stage2_rate']:.4f}")
    print(f"  per-claim rejection rates:")
    for c in pins.CLAIMS:
        star = ' [TRUE-null]' if c in out['truth_set'] else ''
        print(f"     {c:16s} {out['claim_rej_rate'][c]:.5f}{star}")
    if 'paths' in out:
        print("  path estimands:")
        for name, d in out['paths'].items():
            if 'rate' in d and d['rate'] is not None and 'cp_lower95' in d:
                print(f"     {name:22s} {d['rate']:.4f} +/- {d.get('mcse',0):.4f}  "
                      f"CP-lower95={d['cp_lower95']:.4f}")
            else:
                print(f"     {name:22s} {d}")
    print(f"  timing: {out['sec_per_rep']*1000:.2f} ms/rep  "
          f"({out['elapsed_s']:.1f}s for {out['R']} reps)")
