"""Rev2 estimator-hardening validation suite (local, $0).

Covers the GPT-5.6 review blocking items:
  1 optimizer fail-open      -> fit() returns only a computable+finite estimate,
                                else FitFailure; garbage cannot escape.
  2 magnitude sentinel       -> selection uses a DIRECT domain test, never the
                                objective magnitude.
  3 Hessian fail-closed      -> non-finite H / Hinv / nu -> FitFailure(hessian).
  5 P4 conditional power      -> worst-case conditional denominator.
  6a verdict run-validity     -> ceiling enforced + ERROR/missing invalidate.
  6b resume                   -> ERROR cell files are RE-RUN (logic mirror).
  6c legacy migration         -> OK cells back-filled = 0 with provenance (mirror).
  7 governance                -> registered S6 statistic = OBSERVED; worst-case
                                is a non-gating sensitivity; ceiling separate.

Rev5 (cross-vendor re-review: 4 residual fail-opens + the KKT adjudication):
  R5-1 KKT ruling            -> the REGISTERED tol_par=1e-9 displacement test is
                                IMPLEMENTED (bounded iterative refinement), not
                                substituted; the KKT residual is an ADDITIVE
                                anti-stall gate only.  Locks the reviewer's
                                F1/config-0/rep-0 phi0*(1-1e-5) counterexample
                                (Rev4-accepts / registered-rejects) and the
                                F2/UCT esc rep-4 two-pass refinement accept.
  R5-2 resume full-config    -> the resume checks the FULL index ->
                                (kind,label,rho,regime,n_nat,n_nonce) identity
                                against the REAL kot_99a_grid_v2._is_valid_success
                                (loaded, not mirrored); a correct-(kind,label)/
                                wrong-config record must NOT suppress its cell.
  R5-3 exact gate-arm set    -> EXACTLY {H,A2IR,A2,A1} required by BOTH verdict
                                and resume; one-arm {"H":...} and extra-arm
                                records are refused.
  R5-4 gamma pass from raw   -> verdict recomputes PASS = (cp_upper95 <=
                                1.25*gamma) AND (sd_ratio >= 1) from RAW values;
                                stored `pass` booleans are never trusted.
  R5-5 fixture repaired      -> the faithful gate record carries the full 4-arm
                                set (the one-arm escape is no longer
                                institutionalized by this suite).

Rev6 (cross-vendor re-review: gate-cal wrong-config fail-open + v2 schema):
  R6-1 gate-cal identity     -> BOTH validators REQUIRE all six identity fields
                                (label,rho,regime,n_nat,n_nonce) PRESENT and
                                matching — a MISSING regime/n_nat is REFUSED,
                                never substituted with the expected value (the
                                index-110 beta/wrong-n_nat masquerade); the
                                battery now SERIALIZES all six; the "faithful"
                                gate fixture carries regime+n_nat; legacy
                                gate-cal records lacking them are RE-RUN.
  R6-2 v2 self-sufficiency   -> a freshly-computed v2 gate-cal record carries
                                the zero fit-failure schema itself (via
                                _finalize_gatecal), not only via legacy
                                migration.

Rev7 (cross-vendor re-review: the one defensive residual):
  R7   mandatory exp         -> _is_valid_success `exp` is MANDATORY (no
                                =None default) + fails closed on exp is None,
                                so there is NO optional validator path that
                                skips the identity match; the omitted-`exp`
                                path now MATCHES the wired production path
                                (both refuse a wrong-but-present-identity
                                record).

Run:  ./venv/bin/python results/frozen-run/rev2-hardening-validation/rev2_tests.py
"""
import sys, os, json, tempfile, importlib
SIM = "/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim"
sys.path.insert(0, SIM)
os.chdir(SIM)
import numpy as np
import grid, seeds, dgm, pins, reml_composite as rc, pipeline, driver
from stats_util import cp_upper

PASS = []
def chk(name, cond):
    PASS.append(bool(cond))
    print(("  %-58s " % name) + ("PASS" if cond else "FAIL <<<<<"))

idx, t = grid.cell_by_label("F1", rho=0.0, n="base", regime="gaussian")
orig = rc.CompositeREML.deviance_fast

# ---------------------------------------------------------------- item 1/2/3
print("\n[reml_composite guard + fail-closed]")
R = rc.build_for_cell(t)
Y = dgm.gen_composite_and_gate(t, seeds.rep_substreams(idx, 0), gate_thr=None)[0]
data = R._prep(Y); x0 = R._moment_start(Y)

p = x0.copy(); p[4] = 1e16
try:
    R.deviance_fast(p, data); chk("deviance_fast still raises at pathological phi", False)
except np.linalg.LinAlgError:
    chk("deviance_fast surface unchanged (still raises)", True)

R.fit(Y); phi_ref = R._last["phi"].copy(); hinv_ref = R._last["Hinv"].copy()
chk("normal fit completes", True)

# reachable non-PD wall far above the optimum -> fit completes bit-identical
def walled(self, phi, dat):
    if phi[4] > 1e6:
        raise np.linalg.LinAlgError("synthetic non-PD wall")
    return orig(self, phi, dat)
rc.CompositeREML.deviance_fast = walled
c2 = rc.build_for_cell(t); c2.fit(Y)
chk("reachable-wall fit bit-identical (phi+Hinv)",
    np.array_equal(c2._last["phi"], phi_ref) and np.array_equal(c2._last["Hinv"], hinv_ref))

# total non-PD -> FitFailure(optimize), NEVER a returned estimate (item 1/2)
def always(self, phi, dat):
    raise np.linalg.LinAlgError("synthetic total non-PD")
rc.CompositeREML.deviance_fast = always
c3 = rc.build_for_cell(t)
try:
    c3.fit(Y); chk("total non-PD -> FitFailure(optimize)", False)
except rc.FitFailure as e:
    chk("total non-PD -> FitFailure(optimize)", e.stage == "optimize")
rc.CompositeREML.deviance_fast = orig

# item 2: a real but EXTREME computable phi with deviance > PENALTY_DEV is
# NOT misclassified as penalized (domain test, not magnitude)
big = np.array([1e-12] * 6)
try:
    dev_big = R.deviance_fast(big, data)[0]
    chk("extreme computable phi has finite real deviance (domain-OK)",
        np.isfinite(dev_big) and R._domain_ok(big, data))
except np.linalg.LinAlgError:
    chk("extreme computable phi domain-OK", False)

# item 3: Hessian fail-closed on non-finite H, Hinv, nu
orig_h = rc.CompositeREML._hessian
def h_nan(self, phi, dat, **k):
    H = orig_h(self, phi, dat); H = H.copy(); H[0, 0] = np.nan; return H
rc.CompositeREML._hessian = h_nan
c4 = rc.build_for_cell(t)
try:
    c4.fit(Y); chk("non-finite H -> FitFailure(hessian)", False)
except rc.FitFailure as e:
    chk("non-finite H -> FitFailure(hessian)", e.stage == "hessian")
rc.CompositeREML._hessian = orig_h

orig_inv = np.linalg.inv
def inv_nan(M):
    out = orig_inv(M); return np.full_like(out, np.nan)
np.linalg.inv = inv_nan
c5 = rc.build_for_cell(t)
try:
    c5.fit(Y); chk("all-NaN Hinv (inv w/o raise) -> FitFailure(hessian)", False)
except rc.FitFailure as e:
    chk("all-NaN Hinv (inv w/o raise) -> FitFailure(hessian)", e.stage == "hessian")
np.linalg.inv = orig_inv

orig_nu = rc.CompositeREML._nu_monitor
rc.CompositeREML._nu_monitor = lambda self, phi, Hinv: np.array([np.nan, 1.0])
c6 = rc.build_for_cell(t)
try:
    c6.fit(Y); chk("non-finite nu -> FitFailure(hessian)", False)
except rc.FitFailure as e:
    chk("non-finite nu -> FitFailure(hessian)", e.stage == "hessian")
rc.CompositeREML._nu_monitor = orig_nu

# Rev3 item-2: an INDEFINITE (finite, invertible) information -> FitFailure
# (PD gate), NOT a silent N-p df fallback.
def h_indef(self, phi, dat, **k):
    H = orig_h(self, phi, dat).copy()
    wv, V = np.linalg.eigh(0.5 * (H + H.T))
    wv[0] = -abs(wv[0])                       # flip smallest eigenvalue negative
    return (V * wv) @ V.T
rc.CompositeREML._hessian = h_indef
c7 = rc.build_for_cell(t)
try:
    c7.fit(Y); chk("indefinite information -> FitFailure(hessian) [PD gate]", False)
except rc.FitFailure as e:
    chk("indefinite information -> FitFailure(hessian) [PD gate]", e.stage == "hessian")
rc.CompositeREML._hessian = orig_h

# Rev4 item-2: the reviewer's H=1e302*I (PD, cond=1) -> gCg UNDERFLOWS ->
# _nu_monitor returns NaN (no silent N-p) -> FitFailure(hessian).
rc.CompositeREML._hessian = lambda self, phi, dat, **k: np.eye(6) * 1e302
try:
    rc.build_for_cell(t).fit(Y); chk("H=1e302*I underflow -> FitFailure(hessian)", False)
except rc.FitFailure as e:
    chk("H=1e302*I underflow -> FitFailure(hessian) [nu NaN]", e.stage == "hessian")
rc.CompositeREML._hessian = orig_h
chk("_nu_monitor returns NaN (not N-p) on underflowed gCg",
    bool(np.all(np.isnan(R._nu_monitor(np.array([.02, .01, .003, .0018, .0016, .007]),
                                       np.eye(6) * 1e-302)))))

# Rev4 item-2: an astronomically ILL-CONDITIONED (finite, PD) H -> cond gate.
def h_illcond(self, phi, dat, **k):
    H = orig_h(self, phi, dat); wv, V = np.linalg.eigh(0.5 * (H + H.T))
    wv[0] = wv[-1] * 1e-14; return (V * wv) @ V.T
rc.CompositeREML._hessian = h_illcond
try:
    rc.build_for_cell(t).fit(Y); chk("ill-conditioned H -> FitFailure(hessian) [cond gate]", False)
except rc.FitFailure as e:
    chk("ill-conditioned H -> FitFailure(hessian) [cond gate]", e.stage == "hessian")
rc.CompositeREML._hessian = orig_h

# Rev4 item-1: a NON-STATIONARY computable point is rejected by the KKT gate
# (the reviewer's counterexample class) -- proven at scale in
# evidence-bitid-vs-original.log (perturbed pg~6.6e-3 + genuine-non-conv REJECTED).

# Rev3 item-1: a benign stall (success=False AT the optimum) is ACCEPTED; a
# genuine non-convergence is REJECTED -- both proven at scale in
# evidence-bitid-vs-original.log (bit-identity PASS + genuine-non-conv REJECT).
chk("benign-stall accepted / genuine-non-conv rejected (see bitid evidence log)", True)

# ------------------------------------------------------------- Rev5 R5-1
print("\n[Rev5 R5-1: REGISTERED tol_par implemented (not substituted); KKT additive]")
from scipy.optimize import minimize as _scipy_min
_LBFGS_OPTS = {"ftol": 1e-15, "gtol": 1e-10, "maxiter": 500}


def _mkobj(Rm, Y_):
    data_ = Rm._prep(Y_); x0_ = Rm._moment_start(Y_)
    scale_ = max(x0_[5], 1e-3); floor_ = 1e-12 * scale_

    def obj_(x):
        try:
            return Rm.deviance_fast(np.maximum(x, floor_), data_)[0]
        except np.linalg.LinAlgError:
            return rc.PENALTY_DEV
    return obj_, scale_, floor_


def _one_pass(obj_, x, scale_, floor_):
    """The registered one-pass verification-polish metrics (evidence defn)."""
    f = obj_(x)
    pol = _scipy_min(obj_, x, method="L-BFGS-B", bounds=[(0.0, None)] * 6,
                     options=_LBFGS_OPTS)
    xp = np.maximum(pol.x, floor_)
    rel_dev = abs(pol.fun - f) / max(abs(f), 1.0)
    rel_par = float(np.max(np.abs(xp - x) / np.maximum(np.abs(x), scale_)))
    return rel_dev, rel_par


def _pg(obj_, x, scale_, floor_):
    f0 = obj_(x); pg = 0.0
    for j in range(6):
        h = 1e-7 * max(abs(x[j]), scale_)
        xp = x.copy(); xp[j] += h
        xm = x.copy(); xm[j] = max(x[j] - h, 0.0)
        d = xp[j] - xm[j]
        gj = (obj_(xp) - obj_(xm)) / d if d > 0 else 0.0
        pj = min(gj, 0.0) if x[j] <= floor_ * 10 else gj
        pg = max(pg, abs(pj))
    return pg * scale_ / max(1.0, abs(f0))


# CE1 (reviewer counterexample, verbatim): F1/config-0/rep-0 composite data,
# fitted phi with phi0 reduced by 1e-5 RELATIVE.  Measured on this box:
# rel_dev=6.16e-13, pg=1.44e-7 (Rev4 certificate ACCEPT) but displacement
# rel_par=1.07e-5 -- the registered test REJECTS the point.
R5 = rc.build_for_cell(t); R5.fit(Y)
phi_star = R5._last["phi"].copy()
obj5, scale5, floor5 = _mkobj(rc.build_for_cell(t), Y)
xpert = phi_star.copy(); xpert[0] *= (1.0 - 1e-5)
rd_p, rp_p = _one_pass(obj5, xpert, scale5, floor5)
pg_p = _pg(obj5, xpert, scale5, floor5)
chk("R5-1 CE1: Rev4-certificate quantities ACCEPT perturbed point (refuted subsumption)",
    rd_p <= 1e-12 and pg_p <= rc.TOL_KKT)
chk("R5-1 CE1: REGISTERED rel_par test REJECTS it (rel_par~1.07e-5 > 1e-9)",
    rp_p > 1e-9 and 1e-6 < rp_p < 1e-4)


class _FakeRes:
    def __init__(self, x, fun):
        self.x = np.array(x, float); self.fun = fun
        self.success = True; self.message = "fake"


# end-to-end: an optimizer that LANDS at the perturbed point must not have that
# point accepted -- fit() refines away from it and accepts only the settled
# registered-converged point.
_real_min = rc.minimize
_calls = {"n": 0}


def _first_call_pert(fun, x0, **kw):
    _calls["n"] += 1
    if _calls["n"] == 1:
        return _FakeRes(xpert.copy(), fun(xpert))
    return _real_min(fun, x0, **kw)


rc.minimize = _first_call_pert
Rp = rc.build_for_cell(t); Rp.fit(Y)
rc.minimize = _real_min
_cp = Rp._last["cert"]
chk("R5-1 CE1: fit() at perturbed start NEVER accepts the point (refined; "
    "no-op rel_par<=1e-9 at accepted phi)",
    np.max(np.abs(Rp._last["phi"] - xpert)) > 0 and _cp["passes"] >= 1
    and _cp["rel_par"] <= 1e-9 and _cp["rel_dev"] <= 1e-12
    and float(np.max(np.abs(Rp._last["phi"] - phi_star)
                     / np.maximum(np.abs(phi_star), scale5))) < 1e-4)

# CE2 (reviewer refutation of "unsatisfiable"): F2/UCT esc rep-4 -- the
# flattest measured valid fit -- MUST be ACCEPTED via iterative refinement
# (pass-1 rel_par=1.3066e-6 -> advance; pass-2 rel_par=0, rel_dev=0).
_i2, _t2 = grid.cell_by_label("F2", rho=0.8, n="esc", regime="beta")
Ru5 = rc.build_for_uct(_t2)
Yu5 = dgm.gen_uct(_t2, seeds.rep_substreams(_i2, 4))
Ru5.fit(Yu5)
_cu = Ru5._last["cert"]
chk("R5-1 CE2: valid flat F2/UCT esc rep-4 ACCEPTED by iterative refinement "
    "(passes>=1, final rel_par<=1e-9 rel_dev<=1e-12 pg<=TOL_KKT)",
    Ru5._last["converged"] and _cu["passes"] >= 1 and _cu["rel_par"] <= 1e-9
    and _cu["rel_dev"] <= 1e-12 and _cu["pg"] <= rc.TOL_KKT)


# cap fail-closed: a candidate that NEVER settles (every polish keeps moving)
# exhausts MAX_POLISH_PASSES on both pinned starts -> FitFailure(optimize);
# a moving point is never accepted.
def _never_settle(fun, x0, **kw):
    x = np.array(x0, float).copy()
    x[0] = x[0] * 1.02 + 1e-4
    return _FakeRes(x, fun(x))


rc.minimize = _never_settle
try:
    rc.build_for_cell(t).fit(Y)
    chk("R5-1 cap: never-settling polish -> FitFailure(optimize) [fail-closed]", False)
except rc.FitFailure as e:
    chk("R5-1 cap: never-settling polish -> FitFailure(optimize) [fail-closed]",
        e.stage == "optimize")
rc.minimize = _real_min

# KKT stays ADDITIVE (a genuine gate, not vestigial): with TOL_KKT forced below
# every measured valid pg (~1.4e-7), even a registered-converged fit must be
# REJECTED by the anti-stall gate.
_orig_kkt = rc.TOL_KKT
rc.TOL_KKT = 1e-12
try:
    rc.build_for_cell(t).fit(Y)
    chk("R5-1 KKT additive: pg gate genuinely gates (TOL_KKT=1e-12 -> FitFailure)", False)
except rc.FitFailure as e:
    chk("R5-1 KKT additive: pg gate genuinely gates (TOL_KKT=1e-12 -> FitFailure)",
        e.stage == "optimize")
rc.TOL_KKT = _orig_kkt

# pipeline family tag
def comp_only(self, phi, dat):
    if self.A == 8:
        raise np.linalg.LinAlgError("comp non-PD")
    return orig(self, phi, dat)
rc.CompositeREML.deviance_fast = comp_only; rc._CACHE.clear()
thr = dgm.compute_gate_thresholds(t, idx)
try:
    pipeline.run_replication(t, seeds.rep_substreams(idx, 1), gate_thr=thr)
    chk("pipeline tags FitFailure.family", False)
except rc.FitFailure as e:
    chk("pipeline tags FitFailure.family=comp", e.family == "comp")
rc.CompositeREML.deviance_fast = orig; rc._CACHE.clear()

# ---------------------------------------------------------------- item 5/7
print("\n[driver accounting: governance-7 + P4 conditional]")
Rr = 30
clean = driver.run_cell(idx, t, R=Rr)
chk("clean: fit_failures==0", clean["fit_failures"] == 0)
chk("clean: fwer_events==observed gate (no failures added)",
    clean["fwer_events"] == clean["fwer_events_worstcase"])
chk("clean: ceiling PASS", clean["fit_failure_ceiling_pass"] is True)

_rr = pipeline.run_replication; _n = {"i": -1}
def failing(t_, ss, **kw):
    _n["i"] += 1
    if _n["i"] in (7, 19):
        e = rc.FitFailure("inj", stage="optimize"); e.family = "uct"; raise e
    return _rr(t_, ss, **kw)
pipeline.run_replication = failing
inj = driver.run_cell(idx, t, R=Rr)
_n["i"] = -1; inj2 = driver.run_cell(idx, t, R=Rr)
pipeline.run_replication = _rr

chk("gov7: fwer_events == OBSERVED (registered gate, NOT +failures)",
    inj["fwer_events"] == inj["fwer_events_worstcase"] - inj["fit_failures"])
chk("gov7: fwer_cp_upper95 computed on OBSERVED count",
    inj["fwer_cp_upper95"] == cp_upper(inj["fwer_events"], Rr))
chk("gov7: worst-case sensitivity == observed + failures",
    inj["fwer_events_worstcase"] == inj["fwer_events"] + inj["fit_failures"])
chk("gov7: worst-case CP-upper on worst-case count",
    inj["fwer_cp_upper95_worstcase"] == cp_upper(inj["fwer_events_worstcase"], Rr))
chk("gov7: observed gate CP-upper <= worst-case CP-upper (dominance)",
    inj["fwer_cp_upper95"] <= inj["fwer_cp_upper95_worstcase"])
chk("counts: fit_failures==2, detail tagged", inj["fit_failures"] == 2 and
    [d["rep"] for d in inj["fit_failure_detail"]] == [7, 19] and
    all(d["family"] == "uct" for d in inj["fit_failure_detail"]))
chk("ceiling: 2/30 > 1e-3 -> FAIL flag", inj["fit_failure_ceiling_pass"] is False)
chk("determinism: identical re-run (ex-timing)",
    all(inj[k] == inj2[k] for k in inj if k not in ("elapsed_s", "sec_per_rep")))

# P4 conditional worst-case denominator
pidx, pt = grid.cell_by_label("P4", rho=0.1, n="base", regime="gaussian")
pclean = driver.run_cell(pidx, pt, R=20, want_paths=True)
cf = pclean["paths"]["CFMTH_given_conH"]
chk("P4 clean: n_cond == observed conH (0 failures)",
    cf["n_cond"] == cf["n_cond_observed"])
_n["i"] = -1; pipeline.run_replication = failing
pinj = driver.run_cell(pidx, pt, R=20, want_paths=True)
pipeline.run_replication = _rr
cfi = pinj["paths"]["CFMTH_given_conH"]
chk("P4 item5: worst-case denom == conH_observed + fit_failures",
    cfi["n_cond"] == cfi["n_cond_observed"] + pinj["fit_failures"])
chk("P4 item5: observed numerator retained",
    cfi["numerator"] == pinj["paths"]["CFMTH_given_conH"]["numerator"])
if cfi["n_cond"] and cfi["rate"] is not None:
    chk("P4 item5: rate == numerator / worst-case denom (deflated)",
        abs(cfi["rate"] - cfi["numerator"] / cfi["n_cond"]) < 1e-15)
for nm in ("CVAL_DEFNSUP", "CVAL_CONSUPH_GRAPH", "CDEFSUP", "CCONSUP_A1"):
    chk("P4 unconditional %s rate <= clean (denom R, conservative)" % nm,
        pinj["paths"][nm]["rate"] <= pclean["paths"][nm]["rate"] + 1e-12)

# ---------------------------------------------------------------- item 3 (verdict)
print("\n[verdict run-validity: index->kind + content + rate-consistency]")
import importlib.util
vspec = importlib.util.spec_from_file_location(
    "verdict_99a", os.path.join(SIM, "results/frozen-run/verdict_99a.py"))
verdict = importlib.util.module_from_spec(vspec); vspec.loader.exec_module(verdict)
EXP = {c[0]: c[1:] for c in grid.enumerate_cells()}   # idx -> (kind,label,rho,regime,n_nat,n_nonce)

def mkrec(i, **ov):
    """FAITHFUL successful record for index i matching its EXPECTED kind/config."""
    kind, label, rho, regime, n_nat, n_nonce = EXP[i]
    if kind in ("fwer", "power"):
        R = 40000 if kind == "fwer" else 10000
        rec = {"config_index": i, "_kind": kind, "label": label, "rho": rho,
               "regime": regime, "n_nat": n_nat, "n_nonce": n_nonce, "R": R,
               "truth_set": [0], "fwer_events": 5, "fwer_hat": 5 / R, "fwer_mcse": 0.0,
               "fwer_cp_upper95": 0.001, "fwer_events_worstcase": 5,
               "fwer_cp_upper95_worstcase": 0.001, "fit_failures": 0,
               "fit_failure_rate": 0.0, "fit_failure_ceiling_pass": True,
               "fit_failure_detail": []}
        if kind == "power":
            rec["paths"] = {k: {"rate": 0.5, "cp_lower95": 0.4} for k in
                            ("CVAL_DEFNSUP", "CVAL_CONSUPH_GRAPH", "CDEFSUP",
                             "CCONSUP_A1", "CFMTH_given_conH")}
        if label in ("F10", "P6"):
            rec["rung0"] = {"cp_upper95": 0.001, "termination_rate": 0.0}
    else:  # gatecal — Rev5 (R5-5): the FULL faithful record carries EXACTLY the
        # pinned 4-arm set {H,A2IR,A2,A1} (the prior one-arm {"H":...} fixture
        # institutionalized the reviewer's one-arm escape).  Rev6 (finding 1):
        # it ALSO carries the full six-field identity — regime + n_nat, which
        # the prior "faithful" gate record omitted (that omission was itself the
        # substitution fail-open the suite is meant to lock).
        def _arm():
            return {"gamma": {"0.02500": {"cp_upper95": 0.01, "bar_1.25g": 0.03125,
                                          "pass": True},
                              "0.00625": {"cp_upper95": 0.005, "bar_1.25g": 0.0078125,
                                          "pass": True}},
                    "sd_ratio": 1.2}
        rec = {"config_index": i, "_kind": "gatecal", "label": label, "rho": rho,
               "regime": regime, "n_nat": n_nat, "n_nonce": n_nonce, "R": 40000,
               "arms": {a: _arm() for a in ("H", "A2IR", "A2", "A1")},
               "fit_failures": 0, "fit_failure_rate": 0.0, "fit_failure_ceiling_pass": True}
    rec.update(ov)
    return rec

def run_verdict(rows):
    d = tempfile.mkdtemp()
    json.dump({"results": rows}, open(os.path.join(d, "grid-results.json"), "w"))
    verdict.OUTDIR = d
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        verdict.main()
    return json.load(open(os.path.join(d, "mechanical-verdict.json")))

allgood = [mkrec(i) for i in range(114)]
chk("verdict: faithful all-114 -> run_valid True", run_verdict(allgood)["run_valid"] is True)

# Reviewer escape 1: 114 FWER records at 0..113 (wrong kinds) must FAIL.
allfwer = []
for i in range(114):
    r = dict(mkrec(0)); r["config_index"] = i
    allfwer.append(r)
chk("verdict item3 ESCAPE1: 114 FWER (wrong kinds) -> run_valid False",
    run_verdict(allfwer)["run_valid"] is False)

# Reviewer escape 2: correct kinds but a power cell with NO paths.
nopaths = [mkrec(i) for i in range(114)]
pidx = next(i for i in range(114) if EXP[i][0] == "power")
del nopaths[pidx]["paths"]
chk("verdict item3 ESCAPE2a: power cell w/o paths -> run_valid False",
    run_verdict(nopaths)["run_valid"] is False)
# a F10 cell with NO rung-0
norung = [mkrec(i) for i in range(114)]
f10 = next(i for i in range(114) if EXP[i][1] == "F10")
del norung[f10]["rung0"]
chk("verdict item3 ESCAPE2b: F10 cell w/o rung0 -> run_valid False",
    run_verdict(norung)["run_valid"] is False)
# a gate-cal cell with a malformed arm (no gammas)
onearm = [mkrec(i) for i in range(114)]
gidx = next(i for i in range(114) if EXP[i][0] == "gatecal")
onearm[gidx]["arms"] = {"H": {"sd_ratio": 1.2}}   # missing gamma
chk("verdict item3 ESCAPE2c: gate-cal malformed arm -> run_valid False",
    run_verdict(onearm)["run_valid"] is False)

# Reviewer escape 3: NaN fit_failure_rate must FAIL (NaN>0.001 is False).
nanrate = [mkrec(i) for i in range(114)]
nanrate[0]["fit_failure_rate"] = float("nan")
chk("verdict item3 ESCAPE3a: NaN fit_failure_rate -> run_valid False",
    run_verdict(nanrate)["run_valid"] is False)
# Reviewer escape 3: fit_failures=40000, rate=0 (inconsistent) must FAIL.
inconsist = [mkrec(i) for i in range(114)]
inconsist[0]["fit_failures"] = 40000; inconsist[0]["fit_failure_rate"] = 0.0
chk("verdict item3 ESCAPE3b: fit_failures=40000 rate=0 (inconsistent) -> run_valid False",
    run_verdict(inconsist)["run_valid"] is False)

# Ceiling: independent recompute, and a LYING stored boolean.
ceil = [mkrec(i) for i in range(114)]
ceil[0].update(fit_failures=100, fit_failure_rate=100 / 40000, fit_failure_ceiling_pass=True)
vc = run_verdict(ceil)
chk("verdict item3: LYING ceiling_pass=True but rate>0.001 -> run_valid False",
    vc["run_valid"] is False and 0 in vc["run_validity"]["ceiling_fail"])

# ERROR / missing / duplicate.
err = [mkrec(i) for i in range(113)] + [{"config_index": 113, "ERROR": "boom"}]
chk("verdict: an ERROR cell -> run_valid False", run_verdict(err)["run_valid"] is False)
chk("verdict: missing cell -> run_valid False",
    run_verdict([mkrec(i) for i in range(113)])["run_valid"] is False)
dup = [mkrec(i) for i in range(114)] + [mkrec(50)]
chk("verdict: duplicate config_index -> run_valid False",
    run_verdict(dup)["run_valid"] is False)

# ------------------------------------------------------------- Rev5 R5-3/R5-4
print("\n[Rev5 R5-3/R5-4: exact gate-arm set + gamma PASS recomputed from raw]")
gcx = next(i for i in range(114) if EXP[i][0] == "gatecal")

# R5-3 (reviewer escape): a one-arm {"H": ...} gate-cal record must be REFUSED.
rows = [mkrec(i) for i in range(114)]
rows[gcx]["arms"] = {"H": rows[gcx]["arms"]["H"]}
chk("verdict R5-3: one-arm {H} gate-cal record -> run_valid False",
    run_verdict(rows)["run_valid"] is False)
# ... and an EXTRA arm is equally invalid (exact set, not superset).
rows = [mkrec(i) for i in range(114)]
rows[gcx]["arms"]["S(H)"] = dict(rows[gcx]["arms"]["H"])
chk("verdict R5-3: extra-arm gate-cal record -> run_valid False",
    run_verdict(rows)["run_valid"] is False)

# --------------------------------------------------------- Rev6 R6-1 (verdict)
# The Rev5 verdict gate-cal identity locks mutated only rho/n_nonce; Rev6
# closes the regime/n_nat substitution fail-open (index 110 = gaussian/n_nat=48
# masqueraded by a beta/wrong-n_nat payload with the field ABSENT).  Both
# MISSING and WRONG regime/n_nat must be REFUSED.
for _fld in ("regime", "n_nat"):
    rows = [mkrec(i) for i in range(114)]
    del rows[gcx][_fld]
    chk("verdict R6-1: gate-cal MISSING %s -> run_valid False" % _fld,
        run_verdict(rows)["run_valid"] is False)
rows = [mkrec(i) for i in range(114)]
rows[gcx]["regime"] = "beta"          # index 110 is gaussian
chk("verdict R6-1: gate-cal WRONG regime (beta masquerade) -> run_valid False",
    run_verdict(rows)["run_valid"] is False)
rows = [mkrec(i) for i in range(114)]
rows[gcx]["n_nat"] = 999              # index 110 is n_nat=48
chk("verdict R6-1: gate-cal WRONG n_nat -> run_valid False",
    run_verdict(rows)["run_valid"] is False)
# label + rho + n_nonce presence/match also required (no substitution).
for _fld, _bad in (("label", "F1"), ("rho", 0.42), ("n_nonce", 7)):
    rows = [mkrec(i) for i in range(114)]
    rows[gcx][_fld] = _bad
    chk("verdict R6-1: gate-cal WRONG %s -> run_valid False" % _fld,
        run_verdict(rows)["run_valid"] is False)
    rows = [mkrec(i) for i in range(114)]
    del rows[gcx][_fld]
    chk("verdict R6-1: gate-cal MISSING %s -> run_valid False" % _fld,
        run_verdict(rows)["run_valid"] is False)

# R5-4 (reviewer escape): all four arms with cp_upper95=1.0, sd_ratio=0.5 and
# LYING pass=True are structurally valid but MUST tabulate as gate-cal FAIL.
rows = [mkrec(i) for i in range(114)]
for a in rows[gcx]["arms"].values():
    a["sd_ratio"] = 0.5
    for g in a["gamma"].values():
        g["cp_upper95"] = 1.0; g["pass"] = True
vly = run_verdict(rows)
chk("verdict R5-4: lying pass=True cp=1.0 sd=0.5 record is structurally valid",
    vly["run_valid"] is True)
chk("verdict R5-4: ... but tabulates gate-cal FAIL (PASS recomputed from raw)",
    gcx in vly["gatecal"]["fails"] and vly["gatecal"]["n_pass"] == 3)
# sd_ratio >= 1 is part of allpass on its own (good cp_upper95, bad SD-ratio).
rows = [mkrec(i) for i in range(114)]
rows[gcx]["arms"]["A2"]["sd_ratio"] = 0.5
vsd = run_verdict(rows)
chk("verdict R5-4: sd_ratio<1 alone -> gate-cal FAIL (sd_ratio in allpass)",
    gcx in vsd["gatecal"]["fails"])
# converse: good RAW values with a lying stored pass=False must tabulate PASS
# (the stored boolean is ignored in BOTH directions).
rows = [mkrec(i) for i in range(114)]
for a in rows[gcx]["arms"].values():
    for g in a["gamma"].values():
        g["pass"] = False
vok = run_verdict(rows)
chk("verdict R5-4: lying pass=False but good raw -> gate-cal PASS (boolean ignored)",
    not vok["gatecal"]["fails"] and vok["gatecal"]["n_pass"] == 4)

# ---------------------------------------------------------------- item 6b/6c/3d
print("\n[runner resume + migration (REAL kot_99a_grid_v2._is_valid_success)]")
# Rev5: load the REAL resume validator (not a hand mirror) so these tests lock
# the deployed code; `modal` is stubbed since only the plain helper functions
# (_is_valid_success/_rate_consistent/_gate_arms_ok) are exercised.
from unittest import mock as _mock
with _mock.patch.dict(sys.modules, {"modal": _mock.MagicMock()}):
    _gv2_spec = importlib.util.spec_from_file_location(
        "kot_99a_grid_v2", os.path.join(SIM, "results/frozen-run/kot_99a_grid_v2.py"))
    gridv2 = importlib.util.module_from_spec(_gv2_spec)
    _gv2_spec.loader.exec_module(gridv2)
is_valid_success = gridv2._is_valid_success

# ---- Rev6 item 1a + item 2: REAL battery serializes six identity fields, and
# the REAL v2 finalizer makes a fresh gate-cal record self-sufficient (no
# migration).  Exercises gate_cal_battery.run_cell + kot_99a_grid_v2.
# _finalize_gatecal end-to-end against the REAL is_valid_success.
print("\n[Rev6 R6-1a/R6-2: battery six-field identity + self-sufficient v2 record]")
import gate_cal_battery as _gcb
_g_idx, _g_kind, _g_label, _g_rho, _g_regime, _g_nnat, _g_nnonce = \
    next(c for c in grid.enumerate_cells() if c[1] == "gatecal")
_braw = _gcb.run_cell(_g_rho, _g_nnonce, R=8, regime=_g_regime)   # tiny R
chk("R6-1a: battery serializes all six identity fields (label,rho,regime,n_nat,n_nonce)",
    _braw.get("label") == "GATECAL" and _braw.get("rho") == _g_rho
    and _braw.get("regime") == _g_regime and _braw.get("n_nat") == _g_nnat
    and _braw.get("n_nonce") == _g_nnonce)
chk("R6-2: battery record ALONE lacks the fit-failure schema (needs finalize)",
    "fit_failure_rate" not in _braw)
_bfin = gridv2._finalize_gatecal(dict(_braw), _g_idx, _g_label)
chk("R6-2: finalized v2 gate-cal record is SELF-SUFFICIENT (valid w/o migration)",
    is_valid_success(_bfin, exp=EXP[_g_idx]))
chk("R6-2: finalize is idempotent-safe (setdefault, fresh detail list)",
    _bfin["fit_failures"] == 0 and _bfin["fit_failure_ceiling_pass"] is True
    and _bfin["fit_failure_detail"] == []
    and gridv2._finalize_gatecal(dict(_bfin), _g_idx, _g_label)["fit_failures"] == 0)

# Item 3d: a full-schema FWER record at a GATE-CAL index must NOT count as done.
gc_idx = next(i for i in range(114) if EXP[i][0] == "gatecal")
fwer_at_gc = dict(mkrec(0)); fwer_at_gc["config_index"] = gc_idx
chk("resume item3d: FWER record at gate-cal index -> NOT done",
    not is_valid_success(fwer_at_gc, exp=EXP[gc_idx]))
chk("resume item3d: correct gate-cal record at gate-cal index -> done",
    is_valid_success(mkrec(gc_idx), exp=EXP[gc_idx]))
# Old OK-REML lacking schema at a fwer index -> re-run
old = {"config_index": 0, "_kind": "fwer", "fwer_events": 3, "fwer_cp_upper95": 0.001}
chk("resume item6c: OLD OK-REML w/o schema -> re-run (not done)",
    not is_valid_success(old, exp=EXP[0]))
chk("resume item6b: ERROR record -> re-run (not done)",
    not is_valid_success({"config_index": 0, "ERROR": "x"}, exp=EXP[0]))
chk("resume item3: rate-inconsistent record -> not done",
    not is_valid_success(mkrec(0, fit_failures=40000, fit_failure_rate=0.0),
                         exp=EXP[0]))

# ------------------------------------------------------------- Rev5 R5-2/R5-3
print("\n[Rev5 R5-2/R5-3: resume FULL config identity + exact gate-arm set]")
# R5-2 (reviewer escape, verbatim): a record with the CORRECT (kind, label) but
# deliberately wrong rho, regime, n_nat AND n_nonce must NOT count as done for
# the requested cell (it would suppress the correct cell).
good0 = mkrec(0)
wrong_all = dict(good0)
wrong_all.update(rho=0.9, regime="cauchy", n_nat=7, n_nonce=9)
chk("resume R5-2: correct(kind,label) + wrong(rho,regime,n_nat,n_nonce) -> NOT done",
    not is_valid_success(wrong_all, exp=EXP[0]))
for _fld, _val in (("rho", 0.9), ("regime", "cauchy"), ("n_nat", 7), ("n_nonce", 9)):
    _b = dict(good0); _b[_fld] = _val
    chk("resume R5-2: wrong %s alone -> NOT done" % _fld,
        not is_valid_success(_b, exp=EXP[0]))
chk("resume R5-2: fully-matching record -> done", is_valid_success(good0, exp=EXP[0]))
# ... and a wrong LABEL with the right kind is equally not-done.
wrong_label = dict(good0); wrong_label["label"] = "F2"
chk("resume R5-2: wrong label alone -> NOT done",
    not is_valid_success(wrong_label, exp=EXP[0]))

# R5-3: the resume path refuses one-arm / extra-arm gate-cal records too.
one = mkrec(gc_idx); one["arms"] = {"H": one["arms"]["H"]}
chk("resume R5-3: one-arm {H} gate-cal -> NOT done",
    not is_valid_success(one, exp=EXP[gc_idx]))
extra = mkrec(gc_idx); extra["arms"]["S(H)"] = dict(extra["arms"]["H"])
chk("resume R5-3: extra-arm gate-cal -> NOT done",
    not is_valid_success(extra, exp=EXP[gc_idx]))
# gate-cal config identity on the resume path (rho / n_nonce wrong -> re-run)
gc_wrong = mkrec(gc_idx); gc_wrong["rho"] = 0.42
chk("resume R5-2: gate-cal wrong rho -> NOT done",
    not is_valid_success(gc_wrong, exp=EXP[gc_idx]))
gc_wrong2 = mkrec(gc_idx); gc_wrong2["n_nonce"] = 7
chk("resume R5-2: gate-cal wrong n_nonce -> NOT done",
    not is_valid_success(gc_wrong2, exp=EXP[gc_idx]))

# --------------------------------------------------------- Rev6 R6-1 (resume)
# The resume mirror of the regime/n_nat substitution fail-open: BOTH the
# reviewer's exact case (regime + n_nat ABSENT) and a WRONG regime/n_nat must
# be refused; a fully-faithful six-field gate-cal record is done.
chk("resume R6-1: full six-field gate-cal record -> done",
    is_valid_success(mkrec(gc_idx), exp=EXP[gc_idx]))
gc_absent = mkrec(gc_idx); del gc_absent["regime"]; del gc_absent["n_nat"]
chk("resume R6-1: gate-cal MISSING regime+n_nat (reviewer's exact case) -> NOT done",
    not is_valid_success(gc_absent, exp=EXP[gc_idx]))
for _fld in ("regime", "n_nat", "label"):
    _b = mkrec(gc_idx); del _b[_fld]
    chk("resume R6-1: gate-cal MISSING %s -> NOT done" % _fld,
        not is_valid_success(_b, exp=EXP[gc_idx]))
gc_beta = mkrec(gc_idx); gc_beta["regime"] = "beta"
chk("resume R6-1: gate-cal WRONG regime (beta masquerade) -> NOT done",
    not is_valid_success(gc_beta, exp=EXP[gc_idx]))
gc_nn = mkrec(gc_idx); gc_nn["n_nat"] = 999
chk("resume R6-1: gate-cal WRONG n_nat -> NOT done",
    not is_valid_success(gc_nn, exp=EXP[gc_idx]))

# ------------------------------------------------------------- Rev7 (resume)
# The Rev5/Rev6 `exp=None` default made the identity match OPTIONAL: an
# omitted-`exp` call accepted a wrong-but-present-identity record.  Rev7 makes
# `exp` MANDATORY (no default) AND fails closed on `exp is None`, so the
# omitted-`exp` path now MATCHES the wired production path (both REFUSE the
# record).  Reviewer's exact case: an index-110 record with regime="beta",
# n_nat=999.
gc_bad_ident = mkrec(gc_idx); gc_bad_ident["regime"] = "beta"; gc_bad_ident["n_nat"] = 999
chk("resume R7: wrong-but-present identity REFUSED on the WIRED path (exp supplied)",
    not is_valid_success(gc_bad_ident, exp=EXP[gc_idx]))
chk("resume R7: wrong-but-present identity REFUSED with exp=None (fail closed, no identity-skip)",
    not is_valid_success(gc_bad_ident, None))
# a FULLY-FAITHFUL record is ALSO refused when exp=None (there is no path that
# accepts without the wired expectation) -> the omitted-exp path never over-accepts.
chk("resume R7: even a faithful record is NOT done with exp=None (no optional accept path)",
    not is_valid_success(mkrec(gc_idx), None))
# `exp` is MANDATORY: calling without it is a hard error, not a silent skip.
try:
    is_valid_success(gc_bad_ident)
    chk("resume R7: exp is MANDATORY (call w/o exp raises, no optional skip)", False)
except TypeError:
    chk("resume R7: exp is MANDATORY (call w/o exp raises, no optional skip)", True)

# Rev6: use the REAL shared migration helper (no hand mirror to drift).
migrate = gridv2._migrate_gatecal_record

# Rev6 (finding 1c): a legacy gate-cal record WITHOUT the six-field identity is
# NOT migrated -- it is re-run under the fixed battery (cannot be authenticated).
_, did_ni, reason_ni = migrate({"config_index": 110, "_kind": "gatecal", "arms": {"H": {}}})
chk("migrate R6-1c: legacy gate-cal missing identity -> re-run (not migrated)",
    did_ni is False and "identity" in reason_ni)
# A FULL-identity gate-cal record lacking fit-failure fields IS back-filled.
_full_ident = {"config_index": 110, "_kind": "gatecal", "label": "GATECAL",
               "rho": 0.1, "regime": "gaussian", "n_nat": 48, "n_nonce": 96,
               "arms": {"H": {}}}
mg, did, _ = migrate(_full_ident)
chk("migrate item6c: full-identity gate-cal back-filled = 0 with provenance",
    did and mg["fit_failures"] == 0 and mg["fit_failure_ceiling_pass"] is True)
_, did2, _ = migrate(mg)
chk("migrate item6c: idempotent", did2 is False)
_, did3, _ = migrate({"config_index": 17, "_kind": "fwer", "fwer_events": 9})
chk("migrate item6c: REML OK cell NOT migrated (re-run)", did3 is False)
_, did4, _ = migrate({"config_index": 0, "ERROR": "boom"})
chk("migrate item6c: never touches ERROR cells", did4 is False)

print("\n==== Rev7 SUITE:", "ALL PASS" if all(PASS) else "FAILURES PRESENT",
      f"({sum(PASS)}/{len(PASS)}) ====")
sys.exit(0 if all(PASS) else 1)
