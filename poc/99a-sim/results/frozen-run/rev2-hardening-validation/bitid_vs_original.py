"""Rev5 registered-convergence-test evidence (320-fit bit-identity path).

Rev4 history: this harness proved the Rev4 certificate bit-identical to the
ORIGINAL frozen selection on all 320 valid fixture fits.  The cross-vendor
re-review then REFUTED the Rev4 substitution (rel_dev + KKT does NOT subsume
the registered tol_par=1e-9 — valid-fixture counterexample F1/config-0/rep-0
phi0*(1-1e-5): rel_dev=6.16e-13, pg=1.44e-7, Rev4 ACCEPT, displacement
rel_par=1.07e-5).  Rev5 IMPLEMENTS the registered test via bounded iterative
refinement (+ KKT as an ADDITIVE anti-stall gate).

Rev5 proof obligations, on the fixture cells F1 config-0 (+ F2 esc), 320 fits:
  (A) UNAFFECTED fits — the registered one-pass test (rel_dev <= 1e-12 AND
      rel_par <= 1e-9) ALREADY holds at the original selection point — keep
      phi, Hinv, and every registered contrast (theta/SE/nu) BIT-IDENTICAL to
      the ORIGINAL frozen selection (diff count MUST be 0);
  (B) REFINED fits — the original point FAILS the registered test (it was
      under-converged at the registered tolerance) — are counted, and each
      accepted refined point must SATISFY the registered no-op test + the KKT
      gate with a deviance <= the original's (the mandated realisation of the
      registered test, never a relaxation);
  (C) the counterexample classes are REJECTED at the submitted point: the
      reviewer's phi0*(1-1e-5) point (registered rel_par test), a perturbed
      non-optimal point and a genuine maxiter-truncated non-convergence (KKT).
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
TOL_DEV, TOL_PAR, TOL_KKT = 1e-12, 1e-9, rc.TOL_KKT


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
    n_unaff = n_diff_unaff = n_refined = n_bad_refined = 0
    n_refined_par = n_refined_dev_only = 0
    n_succ = n_stall = n_rev5_fail = 0
    worst_valid_pg = 0.0
    max_passes = 0
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
        # Rev5 class test at the ORIGINAL SELECTION POINT: does the registered
        # one-pass test already hold there?  If yes the fit is UNAFFECTED and
        # must stay bit-identical; if no, the original point was UNDER-CONVERGED
        # at the registered tolerance and Rev5 MUST refine it (expected diff).
        rd_o, rp_o, pg_o = cert_metrics(obj, phi_o, scale, floor)
        unaffected = (rd_o <= TOL_DEV) and (rp_o <= TOL_PAR)
        if logged < log_first:               # record BOTH success=T and success=F
            logged += 1
            print(f"    {fam} idx{idx} rep{r}: success={succ} msg={res1.message[:26]!r} "
                  f"rel_dev={rel_dev:.2e} rel_par={rel_par:.2e} pg={pg:.2e} "
                  f"n_bound={nbound} -> registered_holds_at_orig={unaffected}")
        Rr = build(t)
        try:
            Rr.fit(Y)
        except rc.FitFailure:
            n_rev5_fail += 1; continue
        cert = Rr._last["cert"]
        max_passes = max(max_passes, cert["passes"])
        con_n = contrasts(Rr, fam)
        identical = (np.array_equal(Rr._last["phi"], phi_o)
                     and np.array_equal(Rr._last["Hinv"], Hinv_o)
                     and np.array_equal(con_n, con_o))
        if unaffected:
            n_unaff += 1
            if not identical:
                n_diff_unaff += 1
                print(f"    !! UNAFFECTED DIFF {fam} idx{idx} rep{r}")
        else:
            n_refined += 1
            # Rev6 (review item 3): classify WHICH registered tolerance the
            # ORIGINAL point failed.  The reviewer's claim is that every
            # refined fit failed tol_par SPECIFICALLY (the flat/under-identified
            # displacement directions), NOT tol_dev; assert this explicitly
            # rather than accepting the two-test disjunction blindly.
            if rp_o > TOL_PAR:
                n_refined_par += 1
            if (rd_o > TOL_DEV) and (rp_o <= TOL_PAR):
                n_refined_dev_only += 1        # MUST be 0 (tol_par-specific)
                print(f"    !! DEV-ONLY REFINEMENT {fam} idx{idx} rep{r}: "
                      f"rd_o={rd_o:.2e} rp_o={rp_o:.2e}")
            f_new = obj(Rr._last["phi"]); f_old = obj(phi_o)
            # Rev6 (review item 3): LITERAL f_new <= f_old (no 1e-9 slack) — a
            # refinement must NEVER raise the deviance.
            justified = (cert["rel_dev"] <= TOL_DEV and cert["rel_par"] <= TOL_PAR
                         and cert["pg"] <= TOL_KKT and f_new <= f_old)
            if not justified:
                n_bad_refined += 1
                print(f"    !! UNJUSTIFIED REFINEMENT {fam} idx{idx} rep{r}: "
                      f"cert={cert} f_new-f_old={f_new - f_old:.3e}")
    print(f"  {fam} idx{idx} reps={n_reps}: unaffected={n_unaff} "
          f"(diffs={n_diff_unaff})  refined={n_refined} "
          f"(tol_par-specific={n_refined_par}, dev-only={n_refined_dev_only}, "
          f"unjustified={n_bad_refined}, max_passes={max_passes})  "
          f"success=True={n_succ} stalls={n_stall}  "
          f"worst_valid_pg={worst_valid_pg:.2e} (<= TOL_KKT={TOL_KKT:.0e})  "
          f"rev5_fitfail={n_rev5_fail}")
    # bad = unaffected-diffs + unjustified refinements + any dev-only refinement
    # (the last asserts refined fits are tol_par-specific, per review item 3).
    return (n_diff_unaff + n_bad_refined + n_refined_dev_only,
            n_refined, n_refined_par, max_passes)


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
    # Rev5: the REVIEWER'S counterexample — fitted phi with phi0*(1-1e-5) —
    # passes rel_dev + KKT (the refuted Rev4 certificate) but MUST be rejected
    # by the REGISTERED rel_par displacement test at the submitted point.
    R2 = rc.build_for_cell(t); R2.fit(Y)
    xrev = R2._last["phi"].copy(); xrev[0] *= (1.0 - 1e-5)
    rd_rev, rp_rev, pg_rev = cert_metrics(obj, xrev, scale, floor)
    r0 = (rd_rev <= TOL_DEV) and (pg_rev <= TOL_KKT) and (rp_rev > TOL_PAR)
    r1 = pg_perturb > TOL_KKT
    r2 = pg_bad > TOL_KKT
    print(f"  reviewer phi0*(1-1e-5): rel_dev={rd_rev:.2e} pg={pg_rev:.2e} "
          f"(Rev4-would-ACCEPT) rel_par={rp_rev:.2e} -> REGISTERED-REJECTED={r0}")
    print(f"  perturbed non-optimal: pg={pg_perturb:.2e} -> REJECTED={r1}")
    print(f"  genuine non-conv (maxiter=2): pg={pg_bad:.2e} -> REJECTED={r2}")
    return r0 and r1 and r2


import numpy as _np2, scipy as _sp2
print("[per-candidate certificate evidence — success=True AND success=False]")
# Rev6 (review item 4): RECORD the package versions — the pass-cap behaviour
# depends on L-BFGS-B, so the evidence must be reproduced under the PAID image
# pins (NumPy 2.1.3 / SciPy 1.14.1), not just the reviewer's 2.0.2 / 1.13.1.
print(f"[env] numpy={_np2.__version__} scipy={_sp2.__version__} "
      f"(PAID-IMAGE PIN = numpy 2.1.3 / scipy 1.14.1)  "
      f"MAX_POLISH_PASSES={rc.MAX_POLISH_PASSES}")
i0, t0 = grid.cell_by_label("F1", rho=0.0, n="base", regime="gaussian")
i1, t1 = grid.cell_by_label("F2", rho=0.8, n="esc", regime="beta")
tot = 0; total_refined = 0; total_refined_par = 0; global_max_passes = 0
for args in ((i0, t0, 120, "comp"), (i0, t0, 120, "uct"),
             (i1, t1, 40, "comp"), (i1, t1, 40, "uct")):
    bad, refined, refined_par, mp = check(*args)
    tot += bad; total_refined += refined; total_refined_par += refined_par
    global_max_passes = max(global_max_passes, mp)
print("\n[counterexample-class rejection]")
rej = reject_tests(i0, t0)
# Cap scan (review item 4): the observed refinement depth must stay strictly
# below MAX_POLISH_PASSES for the cap to be non-binding on valid fits.
cap_ok = global_max_passes < rc.MAX_POLISH_PASSES
# tol_par-specificity (review item 3): EVERY refined fit failed tol_par.
par_specific = (total_refined_par == total_refined)
print(f"\n[env] reproduced under numpy={_np2.__version__} scipy={_sp2.__version__}")
print(f"[cap scan] global max refinement passes = {global_max_passes} "
      f"(< MAX_POLISH_PASSES={rc.MAX_POLISH_PASSES}): "
      + ("PASS" if cap_ok else "FAIL"))
print(f"[tol_par-specific] refined fits failing tol_par: "
      f"{total_refined_par}/{total_refined}: "
      + ("PASS" if par_specific else "FAIL"))
print(f"\nFIXTURE-RELEVANT BIT-IDENTITY on UNAFFECTED fits + refined-fit "
      f"justification (literal f_new<=f_old; {total_refined} refined of 320):",
      "PASS" if tot == 0 else f"FAIL ({tot} bad)")
print("COUNTEREXAMPLE-CLASS REJECTED (registered rel_par + perturbed + "
      "genuine non-conv):", "PASS" if rej else "FAIL")
sys.exit(0 if (tot == 0 and rej and cap_ok and par_specific) else 1)
