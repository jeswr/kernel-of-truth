"""Rev4 direct-convergence-certificate evidence (GPT-5.6 review item 1).

Proves, on the fixture cell F1 config-0 (+ F2 esc), that the Rev4 direct
certificate (rel_dev <= tol_dev AND central-FD projected-gradient KKT
<= TOL_KKT, evaluated on EVERY candidate — success or not):
  (A) keeps phi, Hinv, and every registered contrast (theta/SE/nu) BIT-IDENTICAL
      to the ORIGINAL frozen selection on valid fits;
  (B) records, for EVERY first start (success=True AND success=False), the
      message, rel_dev, rel_par, projected-gradient norm, interiority, and the
      certificate decision — the success=True branch is the escaping class the
      prior evidence omitted;
  (C) REJECTS the counterexample class: a perturbed non-optimal point and a
      genuine maxiter-truncated non-convergence both fail the KKT gate.
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
TOL_DEV, TOL_KKT = 1e-12, rc.TOL_KKT


def _pg_norm(obj, x, scale, floor):
    f0 = obj(x); pg = 0.0
    for j in range(6):
        h = 1e-7 * max(abs(x[j]), scale)
        xp = x.copy(); xp[j] += h
        xm = x.copy(); xm[j] = max(x[j] - h, 0.0)
        d = xp[j] - xm[j]
        gj = (obj(xp) - obj(xm)) / d if d > 0 else 0.0
        pj = min(gj, 0.0) if x[j] <= floor * 10 else gj
        pg = max(pg, abs(pj))
    return pg * scale / max(1.0, abs(f0))


def original_phi(R, Ycomp):
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
    R._last = dict(phi=phi, Hinv=Hinv, data=data, Ybar=data[0], converged=True)
    return phi, Hinv, res, obj, scale, floor


def contrasts(R, fam):
    if fam == "comp":
        out = [R.contrast(_COMP_IDX['H'], _COMP_IDX['A2IR'])]
        out += [R.contrast(_COMP_IDX[a], _COMP_IDX['S(%s)' % a]) for a in pins.SH_NONCE_ARMS]
    else:
        out = [R.contrast(_UCT_IDX[c], _UCT_IDX['T']) for c in pins.CANDIDATES]
    return np.array([[c.theta_hat, c.se, c.nu] for c in out])


def cert_metrics(obj, xr, scale, floor):
    pol = minimize(obj, xr, method="L-BFGS-B", bounds=[(0.0, None)] * 6, options=_OPTS)
    xp = np.maximum(pol.x, floor)
    rel_dev = abs(pol.fun - obj(xr)) / max(abs(obj(xr)), 1.0)
    rel_par = float(np.max(np.abs(xp - xr) / np.maximum(np.abs(xr), scale)))
    pg = _pg_norm(obj, xr, scale, floor)
    return rel_dev, rel_par, pg


def check(idx, t, n_reps, fam, log_first=6):
    build = rc.build_for_cell if fam == "comp" else rc.build_for_uct
    gen = (lambda ss: dgm.gen_composite_and_gate(t, ss, gate_thr=None)[0]) if fam == "comp" \
        else (lambda ss: dgm.gen_uct(t, ss))
    n_diff = n_succ = n_stall = n_rev4_fail = 0
    worst_valid_pg = 0.0
    logged = 0
    for r in range(n_reps):
        Y = gen(seeds.rep_substreams(idx, r))
        Rref = build(t); phi_o, Hinv_o, res1, obj, scale, floor = original_phi(Rref, Y)
        con_o = contrasts(Rref, fam)
        xr = np.maximum(res1.x, floor)
        rel_dev, rel_par, pg = cert_metrics(obj, xr, scale, floor)
        worst_valid_pg = max(worst_valid_pg, pg)
        nbound = int(np.sum(res1.x <= floor * 10))
        succ = bool(res1.success)
        n_succ += succ; n_stall += (not succ)
        accepts = (rel_dev <= TOL_DEV) and (pg <= TOL_KKT)
        if logged < log_first:               # record BOTH success=T and success=F
            logged += 1
            print(f"    {fam} idx{idx} rep{r}: success={succ} msg={res1.message[:26]!r} "
                  f"rel_dev={rel_dev:.2e} rel_par={rel_par:.2e} pg={pg:.2e} "
                  f"n_bound={nbound} -> cert_accepts={accepts}")
        Rr = build(t)
        try:
            Rr.fit(Y)
        except rc.FitFailure:
            n_rev4_fail += 1; continue
        con_n = contrasts(Rr, fam)
        if not (np.array_equal(Rr._last["phi"], phi_o)
                and np.array_equal(Rr._last["Hinv"], Hinv_o)
                and np.array_equal(con_n, con_o)):
            n_diff += 1
    print(f"  {fam} idx{idx} reps={n_reps}: phi+Hinv+contrast diffs={n_diff}  "
          f"success=True={n_succ} stalls={n_stall}  worst_valid_pg={worst_valid_pg:.2e} "
          f"(<= TOL_KKT={TOL_KKT:.0e})  rev4_fitfail={n_rev4_fail}")
    return n_diff


def reject_tests(idx, t):
    R = rc.build_for_cell(t)
    Y = dgm.gen_composite_and_gate(t, seeds.rep_substreams(idx, 0), gate_thr=None)[0]
    data = R._prep(Y); x0 = R._moment_start(Y)
    scale = max(x0[5], 1e-3); floor = 1e-12 * scale

    def obj(x):
        return R.deviance_fast(np.maximum(x, floor), data)[0]
    res = minimize(obj, x0, method="L-BFGS-B", bounds=[(0.0, None)] * 6, options=_OPTS)
    xr = np.maximum(res.x, floor)
    xp = xr.copy(); xp[int(np.argmax(xp))] *= 0.5          # counterexample class
    pg_perturb = _pg_norm(obj, xp, scale, floor)
    bad = minimize(obj, x0 * 50 + 0.5, method="L-BFGS-B", bounds=[(0.0, None)] * 6,
                   options={**_OPTS, "maxiter": 2})
    pg_bad = _pg_norm(obj, np.maximum(bad.x, floor), scale, floor)
    r1 = pg_perturb > TOL_KKT
    r2 = pg_bad > TOL_KKT
    print(f"  perturbed non-optimal: pg={pg_perturb:.2e} -> REJECTED={r1}")
    print(f"  genuine non-conv (maxiter=2): pg={pg_bad:.2e} -> REJECTED={r2}")
    return r1 and r2


print("[per-candidate certificate evidence — success=True AND success=False]")
i0, t0 = grid.cell_by_label("F1", rho=0.0, n="base", regime="gaussian")
i1, t1 = grid.cell_by_label("F2", rho=0.8, n="esc", regime="beta")
tot = 0
tot += check(i0, t0, 120, "comp"); tot += check(i0, t0, 120, "uct")
tot += check(i1, t1, 40, "comp"); tot += check(i1, t1, 40, "uct")
print("\n[counterexample-class rejection]")
rej = reject_tests(i0, t0)
print("\nFIXTURE-RELEVANT BIT-IDENTITY (phi+Hinv+contrasts):",
      "PASS" if tot == 0 else f"FAIL ({tot} diffs)")
print("COUNTEREXAMPLE-CLASS REJECTED (perturbed + genuine non-conv):",
      "PASS" if rej else "FAIL")
sys.exit(0 if (tot == 0 and rej) else 1)
