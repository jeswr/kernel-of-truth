"""S4.4 gate-calibration battery (mock scale).

Runs the gate test ALONE at pi_a = pi0 for the 4 gate arms and checks the
realised component rejection rate's exact one-sided 95% upper bound against
1.25*gamma at the two audited local levels gamma in {0.025, 0.00625}.  This
directly validates level control of the custom crossed-binary bootstrap test
(load-bearing for the confirmatory family).  MOCK: a few hundred to ~1500 reps
per cell, not R = 40,000.
"""
import sys
import numpy as np
import pins
import seeds
import dgm
import gate_test
from stats_util import cp_upper
from hypotheses import ParamVector
import grid

_REV_OFF = {a: i for i, a in enumerate(pins.REVIEWED_ARMS)}
GAMMAS = (0.025, 0.00625)


def run(rho, n_nonce, R):
    n_nat = pins.N_NAT if n_nonce == 96 else pins.N_NAT_ESC
    idx, t = grid.cell_by_label('GATECAL', rho=rho, n='base' if n_nonce == 96 else 'esc')
    t.n_nonce = n_nonce; t.n_nat = n_nat
    # all pi_a = pi0 (boundary) — GATECAL override already sets this
    counts = {a: {g: 0 for g in GAMMAS} for a in pins.GATE_ARMS}
    pvals = {a: [] for a in pins.GATE_ARMS}
    for r in range(R):
        ss = seeds.rep_substreams(idx, r)
        _, gate = dgm.gen_composite_and_gate(t, ss)
        boot = ss[pins.SS_GATE_BOOT]
        for gi, a in enumerate(pins.GATE_ARMS):
            p = gate_test.gate_pvalue(gate[gi], _REV_OFF[a], pins.PI0, boot)
            pvals[a].append(p)
            for g in GAMMAS:
                if p <= g:
                    counts[a][g] += 1
    print(f"\n=== gate-cal rho={rho} n_nonce={n_nonce} R={R} (pi_a=pi0={pins.PI0}) ===")
    all_ok = True
    for a in pins.GATE_ARMS:
        pv = np.array(pvals[a])
        line = f"  arm {a:5s} mean_p={pv.mean():.3f} "
        for g in GAMMAS:
            k = counts[a][g]
            ub = cp_upper(k, R)
            thr = 1.25 * g
            ok = ub <= thr
            all_ok = all_ok and ok
            line += f"| gamma={g:.5f}: rej={k/R:.4f} CPupper={ub:.4f} (<=1.25g={thr:.4f}) {'OK' if ok else 'FAIL'} "
        print(line)
    print(f"  => cell {'ACCEPT' if all_ok else 'FAIL'} (mock scale)")
    return all_ok


if __name__ == '__main__':
    rho = float(sys.argv[1]) if len(sys.argv) > 1 else 0.1
    n_nonce = int(sys.argv[2]) if len(sys.argv) > 2 else 96
    R = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
    run(rho, n_nonce, R)
