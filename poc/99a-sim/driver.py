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
from hypotheses import truth_set
from stats_util import cp_upper, cp_lower, mc_se


def run_cell(config_index, t, R, want_paths=False, progress=False,
             use_futility=True, use_rung0=True):
    """Run R reps of resolved cell t (config_index for the seed map)."""
    T = truth_set(t)                       # {j : null_j true} — error-counting set
    # per-cell gate thresholds computed ONCE before replications (S4.4/B4)
    gate_thr = dgm.compute_gate_thresholds(t, config_index)
    claim_rej = {c: 0 for c in pins.CLAIMS}
    fwer_events = 0                        # >=1 TRUE-null claim rejected
    stage2_count = 0
    # path counters (power cells)
    paths = {'CVAL_DEFNSUP': 0, 'CVAL_CONSUPH_GRAPH': 0, 'CFMTH_given_conH': 0,
             'conH_count': 0, 'CDEFSUP': 0, 'CCONSUP_A1': 0}
    t0 = time.time()
    for r in range(R):
        ss = seeds.rep_substreams(config_index, r)
        res = pipeline.run_replication(t, ss, use_futility=use_futility,
                                       use_rung0=use_rung0, gate_thr=gate_thr)
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

    fwer_hat = fwer_events / R
    out = {
        'config_index': config_index,
        'label': t.config_label, 'kind': t.kind,
        'rho': t.rho, 'regime': t.regime, 'n_nat': t.n_nat, 'n_nonce': t.n_nonce,
        'R': R,
        'truth_set': sorted(T),
        'fwer_events': fwer_events,
        'fwer_hat': fwer_hat,
        'fwer_mcse': mc_se(fwer_hat, R),
        'fwer_cp_upper95': cp_upper(fwer_events, R),
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
        ch = paths['conH_count']
        out['paths']['CFMTH_given_conH'] = {
            'rate': (paths['CFMTH_given_conH'] / ch) if ch else None,
            'n_cond': ch,
        }
    return out


def print_report(out):
    print(f"\n=== cell {out['label']} idx={out['config_index']} "
          f"rho={out['rho']} regime={out['regime']} "
          f"n=({out['n_nat']},{out['n_nonce']}) R={out['R']} ===")
    print(f"  truth set (TRUE nulls): {out['truth_set']}")
    print(f"  FWER (>=1 true-null rejected): {out['fwer_hat']:.5f} "
          f"+/- {out['fwer_mcse']:.5f} (MC-SE)   CP-upper95={out['fwer_cp_upper95']:.5f}")
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
