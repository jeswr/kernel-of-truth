# 99a exact-REML numerical-hardening — Rev3 validation artifact

Auditable local ($0) evidence for the Rev3 estimator-hardening patch that fixes
the grid-run-v2 fit-failure blocker (88% cell fit-failure at full R) AND both
GPT-5.6 review REJECTs (Rev1, Rev2). Nothing here is committed by the estimator
itself; this directory is the evidence the executor/reviewer audits before the
paid re-run.

## Files touched by the patch (operative code)
- `poc/99a-sim/reml_composite.py`  — the estimator: noncomputable-factorization
  penalty guard; **convergence-qualified selection (registered tol_dev + tol_par
  tests, not raw success, not bare computability)**; fully fail-closed Hessian
  incl. **PD-information gate**; `contrast()` silent N-p fallback removed;
  `FitFailure`; `_domain_ok`.
- `poc/99a-sim/pipeline.py`        — tags `FitFailure.family` (uct/comp).
- `poc/99a-sim/driver.py`          — per-rep fit-failure counting; governance-7
  accounting (OBSERVED gate + worst-case sensitivity + ceiling); P4 conditional
  worst-case denominator.
- `poc/99a-sim/results/frozen-run/verdict_99a.py` — run-validity gate:
  **independent ceiling recompute**, **full-schema enforcement**, **exactly one
  structurally-valid success per expected index**; observed = S6 gate.
- `poc/99a-sim/results/frozen-run/kot_99a_grid_v2.py` — resume "done" =
  **structurally-valid successful record** (not merely "no ERROR"); migration =
  **gate-cal only** (the 10 OK-REML cells RE-RUN).

## What the local evidence proves

### 1. CONVERGENCE-QUALIFIER + BIT-IDENTITY  (`evidence-bitid-vs-original.log`)
`bitid_vs_original.py` (fixture cell F1 config-0 + F2 esc, 320 fits):
- **phi, Hinv, and every registered contrast (theta/SE/nu) are bit-for-bit
  identical** to the ORIGINAL frozen selection (diffs = 0) — NO ~3% break.
- Every `success=False` first start is recorded: message
  `ABNORMAL_TERMINATION_IN_LNSRCH`, INTERIOR (`n_at_bound=0`), and the
  verification-refinement (polish) is a stationary no-op (`rel_dev`/`rel_par`
  = 0.0, both <= tol_dev=1e-12 / tol_par=1e-9) -> qualifies. Stall rate
  1.7-5.0% per cell (the "~3%" claim, now measured per-rep, not asserted).
- A synthetic **GENUINE non-convergence** (maxiter=2 far start, polish
  rel_par = 0.62) is **REJECTED** by the qualifier -> FitFailure.

The qualifier: a candidate qualifies iff computable + finite + [ `res.success`
(L-BFGS-B gtol=1e-10 first-order / ftol=1e-15 convergence, strictly tighter than
the registered tol_dev/tol_par) OR (success=False but a fresh polish from res.x
is a stationary no-op meeting tol_dev AND tol_par) ]. This closes every review
item-1 escape (two unsuccessful-but-finite endpoints; an unsuccessful endpoint
below a successful retry; maxiter / abnormal-away-from-optimum) while keeping the
registered "lowest REML deviance" selection bit-identical on valid fits. Success
is trusted for the deviance+parameter criterion it already subsumes; the polish
rel_par test is NOT applied to success-certified fits because valid FLAT/boundary
optima wander up to ~5e-6 in a polish ([MEASURED]) — applying it uniformly would
wrongly reject them.

### 2. GUARD + FAIL-CLOSED + ACCOUNTING SUITE  (`evidence-rev2-tests.log`)
`rev2_tests.py` — 46/46 PASS. Adds over Rev2: **indefinite information ->
FitFailure(hessian)** (PD gate, review item 2); verdict **lying
`ceiling_pass=True` with rate>0.001 -> run_valid False** (independent recompute),
**missing-schema -> invalid**, **duplicate index -> invalid** (item 3); resume
**old OK-REML w/o schema -> re-run**, **migrated gate-cal -> done**; migration
**gate-cal only, REML re-run not migrated** (item 6c).

### 3. Regression
`reml_composite.py` __main__ fast-vs-dense self-test: max|dev_fast - dev_dense|
= 1.82e-12 (unchanged).

### 4. Verdict on the CURRENT banked data (demonstration)
`verdict_99a.py` on the 100-ERROR/14-OK banked grid reports **RUN VALID: False**
with 100 ERROR + 14 structurally-invalid (the 10 OK-REML cells missing the
fit-failure schema = must re-run; the 4 gate-cal cells missing the migrated
fields), 0/114 valid-success. Pre-Rev1 this printed "FWER 3/3 PASS" as if an
acceptance.

## MANDATORY on the pinned Modal image (executor — NOT replaceable by the above)
Bit-identity of phi/SE/nu supports but does NOT replace the S4.2 fixture gate:
1. Rebuild the pinned image; re-verify all 6 version pins exact.
2. Re-run the **S4.2 lme4/lmerTest fixture-equivalence** (config-0, reps 0-49,
   both families): |Dtheta| <= 1e-7, rel-SE <= 1e-5, rel-nu <= 1e-3, |Dp| <=
   B_run. EXPECTED to pass exactly as before (theta/SE/nu bit-identical on the
   computable, convergence-qualified domain).
3. Re-run S2 determinism (100/100), the exact-REML smoke, and the small-slice.
4. `python kot_99a_grid_v2.py --mode migrate` (back-fill the 4 gate-cal cells),
   then resume `--mode full` (re-runs the 100 ERROR + 10 OK-REML = **110 cells**
   under the convergence-qualified estimator; only the 4 gate-cal skipped), then
   `verdict_99a.py` (must report RUN VALID True; independently recomputes the
   0.1% ceiling and requires one valid-success per index).

## Governance
Numerics change confined to the non-PD / penalty / non-finite / non-converged
region; the fixture quantities (theta/SE/nu/p) are bit-identical on every valid
CONVERGED fit and the registered S6 statistic (OBSERVED realised FWER count) is
UNCHANGED. No margin, test, threshold, seed, R, or acceptance criterion is
altered; the registered tol_dev/tol_par convergence tests are now EVALUATED
(they were previously unused) -> no re-freeze of the frozen object; the patch
goes through the normal pre-commit review gate. The worst-case
(failures-as-events) count is a disclosed non-gating sensitivity; the S4.2 0.1%
fit-failure ceiling is enforced separately as a run-validity gate. Consequence
of requiring convergence: the 10 banked OK-REML cells may hold previously-
accepted NON-converged fits, so they are RE-RUN (not migrated).
