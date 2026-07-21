"""S4.4 gate-calibration battery under the R9a FLOORED test (mock scale).

Runs the FLOORED gate test ALONE at pi_a = pi0 over the 4 pinned cells
{rho in {0.1,0.8}} x {n_nonce in {96,160}}, Gaussian, and reports:
  * ACCEPTANCE: per (cell, arm, gamma in {0.025, 0.00625}) the realised
    component rejection rate's exact one-sided 95% CP-upper bound <= 1.25*gamma;
  * MANDATORY dispersion diagnostics (R9a): empirical SD of pihat across reps,
    mean bootstrap-null SD of pihat*, their ratio (fix predicts >= 1; ratio < 1
    is a REPORTED flag), floor-binding rates P(rho_hat_s < rho_floor) /
    P(rho_hat_r < rho_floor), and quartiles of each rho~ component.

MOCK: a few thousand reps per cell (NOT R = 40,000).  Usage:
  python gate_cal_battery.py [R]        # runs all 4 cells
  python gate_cal_battery.py [R] RHO N  # runs one cell (for parallel launch)
"""
import sys
import os
import json
import numpy as np
import pins
import seeds
import dgm
import gate_test
from stats_util import cp_upper, mc_se
import grid

_REV_OFF = {a: i for i, a in enumerate(pins.REVIEWED_ARMS)}
GAMMAS = (0.025, 0.00625)
CELLS = [(0.1, 96), (0.1, 160), (0.8, 96), (0.8, 160)]


def run_cell(rho, n_nonce, R):
    idx, t = grid.cell_by_label('GATECAL', rho=rho,
                                n='base' if n_nonce == 96 else 'esc')
    t.n_nonce = n_nonce
    t.n_nat = pins.N_NAT if n_nonce == 96 else pins.N_NAT_ESC
    arms = pins.GATE_ARMS
    # per-arm accumulators
    pihat = {a: [] for a in arms}
    pistar_sd = {a: [] for a in arms}
    rhat_s = {a: [] for a in arms}
    rhat_r = {a: [] for a in arms}
    tilde = {a: {'c': [], 's': [], 'r': []} for a in arms}
    counts = {a: {g: 0 for g in GAMMAS} for a in arms}

    for r in range(R):
        ss = seeds.rep_substreams(idx, r)
        _, gate = dgm.gen_composite_and_gate(t, ss)
        boot = ss[pins.SS_GATE_BOOT]
        for gi, a in enumerate(arms):
            p, d = gate_test.gate_pvalue(gate[gi], _REV_OFF[a], pins.PI0, boot,
                                         return_diag=True)
            pihat[a].append(d['pihat'])
            pistar_sd[a].append(d['pistar_sd'])
            rhat_s[a].append(d['rho_points'][1])
            rhat_r[a].append(d['rho_points'][2])
            tc, ts, tr = d['rho_tilde']
            tilde[a]['c'].append(tc); tilde[a]['s'].append(ts); tilde[a]['r'].append(tr)
            for g in GAMMAS:
                if p <= g:
                    counts[a][g] += 1

    result = {'config_index': idx, 'rho': rho, 'n_nonce': n_nonce, 'R': R,
              'pi0': pins.PI0, 'arms': {}}
    for a in arms:
        emp_sd = float(np.std(pihat[a]))
        boot_sd = float(np.mean(pistar_sd[a]))
        ratio = boot_sd / emp_sd if emp_sd > 0 else float('inf')
        arm_rec = {
            'emp_sd_pihat': emp_sd,
            'mean_boot_null_sd': boot_sd,
            'sd_ratio': ratio,
            'sd_ratio_flag': 'FLAG(<1)' if ratio < 1.0 else 'ok(>=1)',
            'floor_binding_s': float(np.mean(np.array(rhat_s[a]) < pins.RHO_FLOOR)),
            'floor_binding_r': float(np.mean(np.array(rhat_r[a]) < pins.RHO_FLOOR)),
            'rho_tilde_quartiles': {
                comp: [float(np.percentile(tilde[a][comp], q)) for q in (25, 50, 75)]
                for comp in ('c', 's', 'r')
            },
            'gamma': {},
        }
        for g in GAMMAS:
            k = counts[a][g]
            ub = cp_upper(k, R)
            bar = 1.25 * g
            arm_rec['gamma']['%.5f' % g] = {
                'rej_rate': k / R, 'rej_count': k, 'mcse': mc_se(k / R, R),
                'cp_upper95': ub, 'bar_1.25g': bar, 'pass': bool(ub <= bar),
            }
        result['arms'][a] = arm_rec
    return result


def print_cell(res):
    print(f"\n=== gate-cal (R9a) rho={res['rho']} n_nonce={res['n_nonce']} "
          f"R={res['R']} (pi_a=pi0={res['pi0']}) ===")
    for a, rec in res['arms'].items():
        print(f"  arm {a:5s} SD-ratio={rec['sd_ratio']:.3f} {rec['sd_ratio_flag']} "
              f"(boot_null_sd={rec['mean_boot_null_sd']:.4f} / emp_sd={rec['emp_sd_pihat']:.4f})")
        print(f"          floor-binding: s={rec['floor_binding_s']:.2f} r={rec['floor_binding_r']:.2f} "
              f"| rho~ medians c/s/r = "
              f"{rec['rho_tilde_quartiles']['c'][1]:.3f}/"
              f"{rec['rho_tilde_quartiles']['s'][1]:.3f}/"
              f"{rec['rho_tilde_quartiles']['r'][1]:.3f}")
        for g in GAMMAS:
            d = rec['gamma']['%.5f' % g]
            print(f"          gamma={g:.5f}: rej={d['rej_rate']:.4f} "
                  f"CPupper={d['cp_upper95']:.4f} (<=1.25g={d['bar_1.25g']:.4f}) "
                  f"{'PASS' if d['pass'] else 'FAIL'}")


def cell_verdict(res):
    all_pass = all(res['arms'][a]['gamma']['%.5f' % g]['pass']
                   for a in res['arms'] for g in GAMMAS)
    any_sd_flag = any(res['arms'][a]['sd_ratio'] < 1.0 for a in res['arms'])
    return all_pass, any_sd_flag


def main():
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    os.makedirs('results/gatecal_r9a', exist_ok=True)
    if len(sys.argv) > 3:
        rho = float(sys.argv[2]); n_nonce = int(sys.argv[3])
        res = run_cell(rho, n_nonce, R)
        print_cell(res)
        fn = f"results/gatecal_r9a/cell_rho{rho}_n{n_nonce}_R{R}.json"
        with open(fn, 'w') as f:
            json.dump(res, f, indent=2)
        print('wrote', fn)
        return
    all_res = []
    for rho, n_nonce in CELLS:
        res = run_cell(rho, n_nonce, R)
        print_cell(res)
        all_res.append(res)
    battery = {'R': R, 'rho_floor': pins.RHO_FLOOR, 'cells': all_res}
    with open('results/gatecal_r9a/gatecal_r9a.json', 'w') as f:
        json.dump(battery, f, indent=2)
    print('\nwrote results/gatecal_r9a/gatecal_r9a.json')


if __name__ == '__main__':
    main()
