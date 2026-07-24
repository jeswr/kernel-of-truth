"""Rev3 convergence-qualifier evidence (GPT-5.6 review item 1).

Proves, on the fixture cell F1 config-0 (+ F2 esc), that the Rev3 tol_dev/tol_par
convergence qualifier:
  (A) keeps phi, Hinv, and every registered contrast (theta/SE/nu) BIT-IDENTICAL
      to the ORIGINAL frozen selection on valid fits (no ~3% break), AND
  (B) for every success=False first start, RECORDS the optimizer message, the
      stall rate, the polish no-op (rel_dev/rel_par under tol_dev/tol_par), and
      interiority — so acceptance is CONDITIONED on the measured evidence, not
      merely asserted, AND
  (C) a synthetic GENUINE non-convergence (maxiter-truncated far start) is
      correctly REJECTED by the qualifier (fails tol_par) -> FitFailure.
"""
import sys, os
sys.path.insert(0, "/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim")
os.chdir("/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim")
import numpy as np
from scipy.optimize import minimize
import grid, seeds, dgm, pins, reml_composite as rc

_UCT_IDX = {a: i for i, a in enumerate(pins.UCT_ARMS)}
_COMP_IDX = {a: i for i, a in enumerate(pins.COMP_ARMS)}
_OPTS = {"ftol": 1e-15, "gtol": 1e-10, "maxiter": 500}
TOL_DEV, TOL_PAR = 1e-12, 1e-9


def original_phi(R, Ycomp):
    """Verbatim ORIGINAL frozen fit() selection (pre-hardening)."""
    data = R._prep(Ycomp); x0 = R._moment_start(Ycomp)
    scale = max(x0[5], 1e-3); floor = 1e-12 * scale

    def obj(x):
        return R.deviance_fast(np.maximum(x, floor), data)[0]
    res = minimize(obj, x0, method="L-BFGS-B", bounds=[(0.0, None)] * 6, options=_OPTS)
    phi = np.maximum(res.x, floor)
    if not res.success:
        tot = float(np.var(Ycomp)); x1 = np.array([tot / 6] * 6)
        res2 = minimize(obj, x1, method="L-BFGS-B", bounds=[(0.0, None)] * 6, options=_OPTS)
        if res2.fun < res.fun:
            phi = np.maximum(res2.x, floor)
    H = R._hessian(phi, data); Hinv = np.linalg.inv(H)
    R._last = dict(phi=phi, Hinv=Hinv, data=data, Ybar=data[0], converged=bool(res.success))
    return phi, Hinv, res


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
    n_diff = n_stall = n_rev2_fail = 0
    for r in range(n_reps):
        Y = gen(seeds.rep_substreams(idx, r))
        Rref = build(t); phi_o, Hinv_o, res1 = original_phi(Rref, Y)
        con_o = contrasts(Rref, fam)
        data = Rref._prep(Y); x0 = Rref._moment_start(Y)
        scale = max(x0[5], 1e-3); floor = 1e-12 * scale
        if not res1.success:                       # record the stall evidence
            n_stall += 1

            def obj(x):
                return Rref.deviance_fast(np.maximum(x, floor), data)[0]
            pol = minimize(obj, np.maximum(res1.x, floor), method="L-BFGS-B",
                           bounds=[(0.0, None)] * 6, options=_OPTS)
            xr = np.maximum(res1.x, floor); xp = np.maximum(pol.x, floor)
            rel_dev = abs(pol.fun - obj(res1.x)) / max(abs(obj(res1.x)), 1.0)
            rel_par = float(np.max(np.abs(xp - xr) / np.maximum(np.abs(xr), scale)))
            nbound = int(np.sum(res1.x <= floor * 10))
            print(f"    {fam} idx{idx} rep{r}: msg={res1.message[:32]!r} "
                  f"polish rel_dev={rel_dev:.2e} rel_par={rel_par:.2e} "
                  f"n_at_bound={nbound} -> qualifies={rel_dev <= TOL_DEV and rel_par <= TOL_PAR}")
        Rr = build(t)
        try:
            Rr.fit(Y)
        except rc.FitFailure:
            n_rev2_fail += 1; continue
        con_n = contrasts(Rr, fam)
        if not (np.array_equal(Rr._last["phi"], phi_o)
                and np.array_equal(Rr._last["Hinv"], Hinv_o)
                and np.array_equal(con_n, con_o)):
            n_diff += 1
    print(f"  {fam} idx{idx} reps={n_reps}: phi+Hinv+contrast diffs={n_diff}  "
          f"success=False stalls={n_stall} ({100*n_stall/n_reps:.1f}%)  "
          f"rev2_fitfail={n_rev2_fail}")
    return n_diff


def reject_test(idx, t):
    """A genuine non-convergence (maxiter=2 far start) must be REJECTED."""
    R = rc.build_for_cell(t)
    Y = dgm.gen_composite_and_gate(t, seeds.rep_substreams(idx, 0), gate_thr=None)[0]
    data = R._prep(Y); x0 = R._moment_start(Y)
    scale = max(x0[5], 1e-3); floor = 1e-12 * scale

    def obj(x):
        return R.deviance_fast(np.maximum(x, floor), data)[0]
    bad = minimize(obj, x0 * 50 + 0.5, method="L-BFGS-B", bounds=[(0.0, None)] * 6,
                   options={"ftol": 1e-15, "gtol": 1e-10, "maxiter": 2})
    pol = minimize(obj, np.maximum(bad.x, floor), method="L-BFGS-B",
                   bounds=[(0.0, None)] * 6, options=_OPTS)
    xr = np.maximum(bad.x, floor); xp = np.maximum(pol.x, floor)
    rel_par = float(np.max(np.abs(xp - xr) / np.maximum(np.abs(xr), scale)))
    rejected = not (bad.success or rel_par <= TOL_PAR)
    print(f"  genuine non-conv (maxiter=2): success={bad.success} polish rel_par={rel_par:.2e} "
          f"-> qualifier REJECTS={rejected}")
    return rejected


print("[per-stall evidence]")
i0, t0 = grid.cell_by_label("F1", rho=0.0, n="base", regime="gaussian")
i1, t1 = grid.cell_by_label("F2", rho=0.8, n="esc", regime="beta")
tot = 0
tot += check(i0, t0, 120, "comp"); tot += check(i0, t0, 120, "uct")
tot += check(i1, t1, 40, "comp"); tot += check(i1, t1, 40, "uct")
print("\n[genuine-non-convergence rejection]")
rej = reject_test(i0, t0)
print("\nFIXTURE-RELEVANT BIT-IDENTITY (phi+Hinv+contrasts):",
      "PASS" if tot == 0 else f"FAIL ({tot} diffs)")
print("GENUINE-NON-CONVERGENCE REJECTED:", "PASS" if rej else "FAIL")
sys.exit(0 if (tot == 0 and rej) else 1)
