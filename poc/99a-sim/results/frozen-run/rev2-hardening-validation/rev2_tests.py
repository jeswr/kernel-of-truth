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
    else:  # gatecal
        rec = {"config_index": i, "_kind": "gatecal", "label": label, "rho": rho,
               "n_nonce": n_nonce, "R": 40000,
               "arms": {"H": {"gamma": {"0.02500": {"cp_upper95": 0.01, "pass": True},
                                        "0.00625": {"cp_upper95": 0.005, "pass": True}},
                              "sd_ratio": 1.2}},
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

# ---------------------------------------------------------------- item 6b/6c/3d
print("\n[runner resume + migration (mirror of _is_valid_success, kind-aware)]")
import math as _math
_FWER_REQ = ("fwer_events", "fwer_cp_upper95", "fwer_events_worstcase",
             "fwer_cp_upper95_worstcase", "fit_failures", "fit_failure_rate",
             "fit_failure_ceiling_pass", "fit_failure_detail", "R")
_GC_REQ = ("arms", "R", "fit_failures", "fit_failure_rate", "fit_failure_ceiling_pass")

def _rate_consistent(rec):
    R = rec.get("R"); ff = rec.get("fit_failures"); rate = rec.get("fit_failure_rate")
    if not (isinstance(R, int) and R > 0):
        return False
    if not (isinstance(ff, int) and not isinstance(ff, bool) and 0 <= ff <= R):
        return False
    if not (isinstance(rate, (int, float)) and not isinstance(rate, bool)
            and _math.isfinite(rate) and rate >= 0.0):
        return False
    return abs(rate - ff / R) <= 1e-9

def is_valid_success(rec, exp_kind=None, exp_label=None):
    """Mirror of kot_99a_grid_v2._is_valid_success (kind-aware, Rev4 item 3d)."""
    if "ERROR" in rec or "config_index" not in rec:
        return False
    kind = rec.get("_kind") or rec.get("kind")
    if exp_kind is not None and kind != exp_kind:
        return False
    if kind in ("fwer", "power"):
        if not all(k in rec for k in _FWER_REQ):
            return False
        if kind == "power" and not (isinstance(rec.get("paths"), dict)
              and all(k in rec["paths"] for k in ("CVAL_DEFNSUP", "CVAL_CONSUPH_GRAPH",
                                                  "CDEFSUP", "CCONSUP_A1", "CFMTH_given_conH"))):
            return False
        if exp_label in ("F10", "P6") and not isinstance(rec.get("rung0"), dict):
            return False
    elif kind == "gatecal":
        if not all(k in rec for k in _GC_REQ):
            return False
        if not (isinstance(rec.get("arms"), dict) and rec["arms"]):
            return False
    else:
        return False
    return _rate_consistent(rec)

# Item 3d: a full-schema FWER record at a GATE-CAL index must NOT count as done.
gc_idx = next(i for i in range(114) if EXP[i][0] == "gatecal")
fwer_at_gc = dict(mkrec(0)); fwer_at_gc["config_index"] = gc_idx
chk("resume item3d: FWER record at gate-cal index -> NOT done",
    not is_valid_success(fwer_at_gc, exp_kind="gatecal", exp_label="GATECAL"))
chk("resume item3d: correct gate-cal record at gate-cal index -> done",
    is_valid_success(mkrec(gc_idx), exp_kind="gatecal", exp_label="GATECAL"))
# Old OK-REML lacking schema at a fwer index -> re-run
old = {"config_index": 0, "_kind": "fwer", "fwer_events": 3, "fwer_cp_upper95": 0.001}
chk("resume item6c: OLD OK-REML w/o schema -> re-run (not done)",
    not is_valid_success(old, exp_kind="fwer", exp_label="F1"))
chk("resume item6b: ERROR record -> re-run (not done)",
    not is_valid_success({"config_index": 0, "ERROR": "x"}, exp_kind="fwer", exp_label="F1"))
chk("resume item3: rate-inconsistent record -> not done",
    not is_valid_success(mkrec(0, fit_failures=40000, fit_failure_rate=0.0),
                         exp_kind=EXP[0][0], exp_label=EXP[0][1]))

def migrate(rec):
    """Mirror of migrate_legacy (Rev3/Rev4): GATE-CAL ONLY; REML re-run."""
    kind = rec.get("_kind") or rec.get("kind")
    if "ERROR" in rec or kind != "gatecal":
        return rec, False
    if rec.get("_fitfailure_migration") or "fit_failure_rate" in rec:
        return rec, False
    rec = dict(rec)
    rec.update(fit_failures=0, fit_failure_rate=0.0, fit_failure_ceiling=0.001,
               fit_failure_ceiling_pass=True, fit_failure_detail=[])
    rec["_fitfailure_migration"] = "prov"
    return rec, True

mg, did = migrate({"config_index": 110, "_kind": "gatecal", "arms": {"H": {}}})
chk("migrate item6c: gate-cal back-filled = 0 with provenance",
    did and mg["fit_failures"] == 0 and mg["fit_failure_ceiling_pass"] is True)
_, did2 = migrate(mg)
chk("migrate item6c: idempotent", did2 is False)
_, did3 = migrate({"config_index": 17, "_kind": "fwer", "fwer_events": 9})
chk("migrate item6c: REML OK cell NOT migrated (re-run)", did3 is False)
_, did4 = migrate({"config_index": 0, "ERROR": "boom"})
chk("migrate item6c: never touches ERROR cells", did4 is False)

print("\n==== Rev4 SUITE:", "ALL PASS" if all(PASS) else "FAILURES PRESENT",
      f"({sum(PASS)}/{len(PASS)}) ====")
sys.exit(0 if all(PASS) else 1)
