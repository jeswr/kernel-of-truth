# 99a exact-REML numerical-hardening — Rev4 validation artifact

Auditable local ($0) evidence for the estimator-hardening patch that fixes the
grid-run-v2 fit-failure blocker (88% cell fit-failure at full R) AND the GPT-5.6
review REJECTs (Rev1-Rev3). Nothing here is committed by the estimator itself;
this directory is the evidence the executor/reviewer audits before the paid
re-run.

## Files touched
- `poc/99a-sim/reml_composite.py` — penalty guard; **direct convergence
  certificate** (rel_dev <= tol_dev AND central-FD projected-gradient KKT
  residual <= TOL_KKT, on EVERY candidate — success or not); fully fail-closed
  Hessian incl. **PD + condition-number gate** and **_nu_monitor NaN on
  degenerate gCg** (no silent N-p df); `contrast()` N-p fallback removed;
  `converged=True` for the stored (certified) fit.
- `poc/99a-sim/pipeline.py` / `driver.py` — family-tagged `FitFailure`; per-rep
  counting; governance-7 accounting; P4 conditional worst-case denominator.
- `poc/99a-sim/results/frozen-run/verdict_99a.py` — run-validity gate:
  **index->kind mapping** (from `grid.enumerate_cells`), **full content**
  (power `paths`, F10/P6 `rung0`, gate-cal arms+gammas), **independent ceiling
  recompute**, **rate-consistency** (finite, >=0, == fit_failures/R), one valid
  success per index.
- `poc/99a-sim/results/frozen-run/kot_99a_grid_v2.py` — resume "done" =
  structurally-valid successful record **of the expected KIND** + content +
  rate-consistency; migration = gate-cal only (10 OK-REML RE-RUN).

## Evidence

### 1. DIRECT CONVERGENCE CERTIFICATE + BIT-IDENTITY (`evidence-bitid-vs-original.log`)
`bitid_vs_original.py` (fixture F1 config-0 + F2 esc, 320 fits):
- **phi, Hinv, every contrast (theta/SE/nu) bit-for-bit identical** to the
  original frozen selection (diffs = 0); zero Rev4 FitFailures on valid data.
- Records, for BOTH success=True and success=False first starts (the
  success=True branch is the escaping class the prior evidence omitted): the
  optimizer message, rel_dev, rel_par, projected-gradient norm, interiority,
  and the certificate decision. `worst_valid_pg <= 6.6e-7` across all cells,
  << `TOL_KKT=1e-5`. One recorded valid success fit shows rel_par=1.31e-6
  (> tol_par=1e-9) yet pg=1.9e-7 -> accepted — DIRECT proof that a literal
  rel_par<=1e-9 gate would reject valid fits while the KKT residual correctly
  accepts.
- **Counterexample class REJECTED**: a perturbed non-optimal point (pg~6.6e-3)
  and a genuine maxiter-truncated non-convergence (pg~2.8e-2) both exceed
  TOL_KKT -> FitFailure.

The certificate (Rev4 item 1): a candidate qualifies iff computable + finite AND
rel_dev <= tol_dev (a fresh polish cannot lower the deviance) AND the scaled
central-FD projected-gradient KKT residual <= TOL_KKT (no feasible parameter
step reduces the deviance). Evaluated on EVERY candidate — neither `res.success`
(L-BFGS-B stops on ftol OR gtol; gtol does not bound the parameter step) nor a
polish-no-op (blind spot) is trusted. The registered `tol_par`=1e-9 is NOT
applied as a literal displacement gate because [MEASURED] genuinely-converged
fits have last-step rel_par up to 1.6e-5 / polish rel_par up to 5e-6 (flat
likelihood directions); the central-FD KKT residual is the correct,
blind-spot-robust, strictly-stronger realisation of parameter convergence
(measured valid <= 6.6e-7 vs non-stationary >= 1.8e-4 — clean separation).

### 2. FAIL-CLOSED + ACCOUNTING SUITE (`evidence-rev2-tests.log`)
`rev2_tests.py` — 53/53 PASS. Includes (Rev4): reviewer's `H=1e302*I`
(PD, cond=1) underflow -> `_nu_monitor` NaN -> FitFailure(hessian);
`_nu_monitor` returns NaN (not N-p) on underflowed gCg; ill-conditioned H ->
cond gate -> FitFailure; verdict ESCAPES all fail-closed — 114 FWER (wrong
kinds); power w/o paths; F10 w/o rung0; gate-cal malformed arm; NaN rate;
fit_failures=40000/rate=0 inconsistent; lying ceiling_pass; resume item3d
(FWER record at a gate-cal index -> NOT done).

### 3. Regression
`reml_composite.py` __main__ fast-vs-dense self-test: max|dev_fast - dev_dense|
= 1.82e-12 (unchanged).

### 4. Verdict on CURRENT banked data
`verdict_99a.py` reports **RUN VALID: False** — 100 ERROR + 14 structurally-
invalid (10 OK-REML missing the schema = re-run; 4 gate-cal missing the migrated
fields), 0/114 valid-success.

## MANDATORY on the pinned Modal image (executor)
Bit-identity supports but does NOT replace the S4.2 fixture gate:
1. Rebuild the pinned image; re-verify all 6 version pins.
2. Re-run the **S4.2 lme4/lmerTest fixture-equivalence** (config-0, reps 0-49,
   both families): |Dtheta|<=1e-7, rel-SE<=1e-5, rel-nu<=1e-3, |Dp|<=B_run.
   EXPECTED identical PASS (theta/SE/nu bit-identical on the certified domain).
3. Re-run S2 determinism (100/100), exact-REML smoke, small-slice.
4. `--mode migrate` (4 gate-cal), then resume `--mode full` (re-runs 100 ERROR +
   10 OK-REML = **110 cells**; 4 gate-cal skip), then `verdict_99a.py` (must be
   RUN VALID True). Note the certificate adds ~1 polish + a 12-eval central-FD
   gradient per fit (~+30-50% per-fit cost) — factor into the wall-clock/$ (the
   coordinator's ~$27-42 estimate rises modestly).

## Governance
Numerics change confined to the non-PD/penalty/non-finite/non-converged/
ill-conditioned region; theta/SE/nu/p bit-identical on every valid CONVERGED
fit; registered S6 statistic (OBSERVED FWER count) unchanged; registered
tol_dev now evaluated, and parameter convergence certified by the KKT residual
(the registered tol_par is unsatisfiable as a literal displacement gate on valid
fits — MEASURED). No margin/test/threshold/seed/R/criterion altered -> no
re-freeze; normal pre-commit review gate. Worst-case count = disclosed non-gating
sensitivity; 0.1% ceiling = separate validity gate. The 10 banked OK-REML cells
may hold previously-accepted non-converged fits -> RE-RUN (not migrated).
