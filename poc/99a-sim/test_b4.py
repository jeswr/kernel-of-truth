"""B4 verification: bounded-Beta gate threshold recalibration (S4.4).

Runs the gate-calibration battery on a bounded-Beta-regime cell with the
per-cell 10^7-draw recalibrated threshold and confirms it still passes
CP-upper <= 1.25*gamma with SD-ratio >= 1.  Also checks the marginal-mapping
obligation P(g=1) ~= pi_a under the recalibrated threshold.
"""
import sys
import numpy as np
from scipy.stats import norm
import grid, dgm, pins, seeds
import gate_cal_battery


def check_marginal():
    idx, t = grid.cell_by_label('GATECAL', rho=0.1)
    t.regime = 'beta'
    thr_beta = dgm.compute_gate_thresholds(t, idx)
    thr_gauss = np.array([norm.ppf(1.0 - t.pi[a]) for a in pins.GATE_ARMS])
    # empirical P(g=1) under the recalibrated threshold vs Gaussian threshold
    emp_beta = []; emp_gauss = []
    for r in range(400):
        ss = seeds.rep_substreams(idx, r)
        _, g = dgm.gen_composite_and_gate(t, ss, gate_thr=thr_beta)
        emp_beta.append(g.mean())
        ss = seeds.rep_substreams(idx, r)
        _, g2 = dgm.gen_composite_and_gate(t, ss, gate_thr=thr_gauss)
        emp_gauss.append(g2.mean())
    print(f"  beta thresholds t_a = {np.round(thr_beta,4)}  (Gaussian ppf = {np.round(thr_gauss,4)})")
    print(f"  P(g=1) under RECALIBRATED thr: {np.mean(emp_beta):.4f} (target pi0={pins.PI0}) "
          f"| under Gaussian thr (biased): {np.mean(emp_gauss):.4f}")


def main():
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    print("== B4: bounded-Beta gate marginal-mapping check (rho=0.1, n=96) ==")
    check_marginal()
    print(f"\n== B4: gate-cal battery on bounded-Beta cell (rho=0.1, n=96, R={R}) ==")
    res = gate_cal_battery.run_cell(0.1, 96, R, regime='beta')
    gate_cal_battery.print_cell(res)
    all_pass, any_flag = gate_cal_battery.cell_verdict(res)
    print(f"  => bounded-Beta cell {'ACCEPT (<=1.25g, SD-ratio>=1)' if all_pass and not any_flag else 'FAIL/FLAG'}")
    import json, os
    os.makedirs('results/gatecal_r9a', exist_ok=True)
    json.dump(res, open('results/gatecal_r9a/cell_beta_rho0.1_n96_R%d.json' % R, 'w'), indent=2)


if __name__ == '__main__':
    main()
