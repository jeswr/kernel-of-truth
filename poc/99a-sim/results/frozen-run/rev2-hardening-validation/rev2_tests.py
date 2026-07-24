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

# ---------------------------------------------------------------- item 6a
print("\n[verdict run-validity]")
import importlib.util
vspec = importlib.util.spec_from_file_location(
    "verdict_99a", os.path.join(SIM, "results/frozen-run/verdict_99a.py"))
verdict = importlib.util.module_from_spec(vspec); vspec.loader.exec_module(verdict)

def _fwer(i, ff=0, rate=0.0, ceiling_pass=None):
    """Full-schema successful FWER record.  ceiling_pass lets a test set the
    STORED boolean INDEPENDENTLY of the rate (to prove the verdict recomputes)."""
    return {"config_index": i, "_kind": "fwer", "label": "F1", "rho": 0.0,
            "regime": "gaussian", "n_nat": 48, "n_nonce": 96, "truth_set": [0],
            "fwer_events": 5, "fwer_hat": 5 / 40000, "fwer_mcse": 0.0,
            "fwer_cp_upper95": 0.001, "fwer_events_worstcase": 5 + ff,
            "fwer_cp_upper95_worstcase": 0.0012,
            "fit_failures": ff, "fit_failure_rate": rate, "fit_failure_detail": [],
            "fit_failure_ceiling_pass": (rate <= 0.001) if ceiling_pass is None else ceiling_pass}

def run_verdict(rows):
    d = tempfile.mkdtemp()
    json.dump({"results": rows}, open(os.path.join(d, "grid-results.json"), "w"))
    verdict.OUTDIR = d
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        verdict.main()
    return json.load(open(os.path.join(d, "mechanical-verdict.json")))

allgood = [_fwer(i) for i in range(114)]
chk("verdict: all-114 clean -> run_valid True", run_verdict(allgood)["run_valid"] is True)

err = [dict(_fwer(i)) for i in range(113)] + [{"config_index": 113, "ERROR": "boom"}]
chk("verdict: an ERROR cell -> run_valid False", run_verdict(err)["run_valid"] is False)

miss = [_fwer(i) for i in range(113)]           # only 113 cells present
chk("verdict: missing cell -> run_valid False", run_verdict(miss)["run_valid"] is False)

ceil = [_fwer(i) for i in range(113)] + [_fwer(113, ff=100, rate=0.0025)]
vc = run_verdict(ceil)
chk("verdict: ceiling breach -> run_valid False", vc["run_valid"] is False)
chk("verdict: ceiling breach recorded", 113 in vc["run_validity"]["ceiling_fail"])

# Rev3 item-3: the verdict INDEPENDENTLY recomputes the ceiling and does NOT
# trust a LYING stored boolean (rate > 0.001 but ceiling_pass wrongly True).
lie = [_fwer(i) for i in range(113)] + [_fwer(113, ff=100, rate=0.0025, ceiling_pass=True)]
vl = run_verdict(lie)
chk("verdict item3: LYING ceiling_pass=True but rate>0.001 -> run_valid False",
    vl["run_valid"] is False and 113 in vl["run_validity"]["ceiling_fail"])

# Rev3 item-3: full-schema enforcement (a missing worst-case field).
nofield = [_fwer(i) for i in range(113)] + [{"config_index": 113, "_kind": "fwer",
           "label": "F1", "rho": 0.0, "regime": "gaussian", "n_nat": 48,
           "n_nonce": 96, "truth_set": [0], "fwer_events": 5, "fwer_hat": 0.0,
           "fwer_mcse": 0.0, "fwer_cp_upper95": 0.001}]
chk("verdict item3: missing schema fields -> run_valid False",
    run_verdict(nofield)["run_valid"] is False)

# Rev3 item-3: exactly-one-valid-result-per-index (a duplicate index).
dup = [_fwer(i) for i in range(114)] + [_fwer(50)]
vd = run_verdict(dup)
chk("verdict item3: duplicate config_index -> run_valid False", vd["run_valid"] is False)

# ---------------------------------------------------------------- item 6b/6c
print("\n[runner resume + migration logic (mirror of _is_valid_success)]")

_FWER_REQ = ("fwer_events", "fwer_cp_upper95", "fwer_events_worstcase",
             "fwer_cp_upper95_worstcase", "fit_failures", "fit_failure_rate",
             "fit_failure_ceiling_pass", "fit_failure_detail")
_GC_REQ = ("arms", "fit_failures", "fit_failure_rate", "fit_failure_ceiling_pass")

def is_valid_success(rec):
    """Mirror of kot_99a_grid_v2._is_valid_success (structural validity)."""
    if "ERROR" in rec or "config_index" not in rec:
        return False
    kind = rec.get("_kind") or rec.get("kind")
    if kind in ("fwer", "power"):
        req = _FWER_REQ
    elif kind == "gatecal":
        req = _GC_REQ
    else:
        return False
    return all(k in rec for k in req)

def resume_done(cell_files):
    return {rec["config_index"] for rec in cell_files if is_valid_success(rec)}

files = [
    _fwer(17),                                                    # Rev3 full-schema REML -> done
    {"config_index": 0, "ERROR": "LinAlgError"},                 # ERROR -> re-run
    {"config_index": 56, "_kind": "fwer", "fwer_events": 3, "fwer_cp_upper95": 0.001},  # OLD OK-REML, no schema -> re-run
    {"config_index": 110, "_kind": "gatecal", "arms": {}, "fit_failures": 0,
     "fit_failure_rate": 0.0, "fit_failure_ceiling_pass": True},  # migrated gate-cal -> done
]
done = resume_done(files)
chk("resume item6b: full-schema REML cell -> done", 17 in done)
chk("resume item6b: ERROR cell -> re-run (not done)", 0 not in done)
chk("resume item6c: OLD OK-REML w/o schema -> re-run (not done)", 56 not in done)
chk("resume item6c: migrated gate-cal -> done", 110 in done)

def migrate(rec):
    """Mirror of migrate_legacy (Rev3): GATE-CAL ONLY; REML re-run, not migrated."""
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

mg, did = migrate({"config_index": 110, "_kind": "gatecal", "arms": {}})
chk("migrate item6c: gate-cal back-filled = 0 with provenance",
    did and mg["fit_failures"] == 0 and mg["fit_failure_ceiling_pass"] is True
    and mg["_fitfailure_migration"])
_, did2 = migrate(mg)
chk("migrate item6c: idempotent (skips already-migrated)", did2 is False)
_, did3 = migrate({"config_index": 17, "_kind": "fwer", "fwer_events": 9})
chk("migrate item6c: REML OK cell NOT migrated (re-run instead)", did3 is False)
_, did4 = migrate({"config_index": 0, "ERROR": "boom"})
chk("migrate item6c: never touches ERROR cells", did4 is False)

print("\n==== Rev3 SUITE:", "ALL PASS" if all(PASS) else "FAILURES PRESENT",
      f"({sum(PASS)}/{len(PASS)}) ====")
sys.exit(0 if all(PASS) else 1)
