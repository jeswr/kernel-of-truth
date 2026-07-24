"""Prove the FIXTURE-RELEVANT quantities (phi, Hinv, and every registered
contrast theta/SE/nu) are BIT-IDENTICAL between Rev2's fit() and an inline
reconstruction of the ORIGINAL frozen selection logic.  The `converged`
metadata flag (which the review asked to change res.success -> best.success)
is reported SEPARATELY — it never enters theta/SE/nu, so it is not a
fixture-equivalence quantity."""
import sys, os
sys.path.insert(0, "/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim")
os.chdir("/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim")
import numpy as np
from scipy.optimize import minimize
import grid, seeds, dgm, pins, reml_composite as rc

_UCT_IDX = {a: i for i, a in enumerate(pins.UCT_ARMS)}
_COMP_IDX = {a: i for i, a in enumerate(pins.COMP_ARMS)}
_OPTS = {"ftol": 1e-15, "gtol": 1e-10, "maxiter": 500}


def original_phi(R, Ycomp):
    """Verbatim ORIGINAL frozen fit() selection (pre-hardening)."""
    data = R._prep(Ycomp)
    x0 = R._moment_start(Ycomp)
    scale = max(x0[5], 1e-3); floor = 1e-12 * scale

    def obj(x):
        phi = np.maximum(x, floor)
        return R.deviance_fast(phi, data)[0]     # original: NO guard (raises)
    res = minimize(obj, x0, method="L-BFGS-B", bounds=[(0.0, None)] * 6, options=_OPTS)
    phi = np.maximum(res.x, floor)
    if not res.success:
        tot = float(np.var(Ycomp)); x1 = np.array([tot / 6] * 6)
        res2 = minimize(obj, x1, method="L-BFGS-B", bounds=[(0.0, None)] * 6, options=_OPTS)
        if res2.fun < res.fun:
            phi = np.maximum(res2.x, floor)
    H = R._hessian(phi, data); Hinv = np.linalg.inv(H)
    R._last = dict(phi=phi, Hinv=Hinv, data=data, Ybar=data[0], converged=bool(res.success))
    return phi, Hinv, bool(res.success)


def contrasts(R, fam):
    if fam == "comp":
        out = [R.contrast(_COMP_IDX['H'], _COMP_IDX['A2IR'])]
        out += [R.contrast(_COMP_IDX[a], _COMP_IDX['S(%s)' % a]) for a in pins.SH_NONCE_ARMS]
    else:
        out = [R.contrast(_UCT_IDX[c], _UCT_IDX['T']) for c in pins.CANDIDATES]
    return np.array([[c.theta_hat, c.se, c.nu] for c in out])


def check(idx, t, n_reps, fam):
    build = rc.build_for_cell if fam == "comp" else rc.build_for_uct
    gen = (lambda ss: dgm.gen_composite_and_gate(t, ss, gate_thr=None)[0]) if fam == "comp" \
        else (lambda ss: dgm.gen_uct(t, ss))
    n_phi_diff = n_hinv_diff = n_con_diff = n_conv_flag_diff = n_rev2_fail = 0
    max_theta = max_se = max_nu = 0.0
    for r in range(n_reps):
        Y = gen(seeds.rep_substreams(idx, r))
        Rref = build(t); phi_o, Hinv_o, conv_o = original_phi(Rref, Y)
        con_o = contrasts(Rref, fam)
        Rr = build(t)
        try:
            Rr.fit(Y)
        except rc.FitFailure:
            n_rev2_fail += 1; continue
        phi_n = Rr._last["phi"]; Hinv_n = Rr._last["Hinv"]; conv_n = Rr._last["converged"]
        con_n = contrasts(Rr, fam)
        if not np.array_equal(phi_o, phi_n): n_phi_diff += 1
        if not np.array_equal(Hinv_o, Hinv_n): n_hinv_diff += 1
        if not np.array_equal(con_o, con_n):
            n_con_diff += 1
            max_theta = max(max_theta, np.max(np.abs(con_o[:, 0] - con_n[:, 0])))
            max_se = max(max_se, np.max(np.abs((con_o[:, 1] - con_n[:, 1]) / con_o[:, 1])))
            max_nu = max(max_nu, np.max(np.abs((con_o[:, 2] - con_n[:, 2]) / con_o[:, 2])))
        if conv_o != conv_n: n_conv_flag_diff += 1
    print(f"{fam} idx{idx} reps={n_reps}: phi_diff={n_phi_diff} Hinv_diff={n_hinv_diff} "
          f"contrast_diff={n_con_diff} (max|dtheta|={max_theta:.2e} relSE={max_se:.2e} "
          f"relnu={max_nu:.2e})  conv_flag_diff={n_conv_flag_diff}  rev2_fitfail={n_rev2_fail}")
    return n_phi_diff + n_hinv_diff + n_con_diff


i0, t0 = grid.cell_by_label("F1", rho=0.0, n="base", regime="gaussian")
i1, t1 = grid.cell_by_label("F2", rho=0.8, n="esc", regime="beta")
tot = 0
tot += check(i0, t0, 120, "comp"); tot += check(i0, t0, 120, "uct")
tot += check(i1, t1, 40, "comp"); tot += check(i1, t1, 40, "uct")
print("\nFIXTURE-RELEVANT BIT-IDENTITY (phi+Hinv+contrasts):",
      "PASS" if tot == 0 else f"FAIL ({tot} diffs)")
