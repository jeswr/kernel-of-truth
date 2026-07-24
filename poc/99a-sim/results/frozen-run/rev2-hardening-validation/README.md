# 99a exact-REML numerical-hardening — Rev2 validation artifact

Auditable local ($0) evidence for the Rev2 estimator-hardening patch that fixes
the grid-run-v2 fit-failure blocker (88% cell fit-failure at full R) AND the
GPT-5.6 review REJECT items. Nothing here is committed by the estimator itself;
this directory is the evidence the executor/reviewer audits before the paid
re-run of the 100 failed cells.

## Files touched by the patch (operative code)
- `poc/99a-sim/reml_composite.py`  — the estimator: noncomputable-factorization
  penalty guard in `fit()`'s objective; computability-qualified candidate
  selection; fully fail-closed Hessian; `FitFailure` type; `_domain_ok`.
- `poc/99a-sim/pipeline.py`        — tags `FitFailure.family` (uct/comp) and
  re-raises so the driver counts per rep.
- `poc/99a-sim/driver.py`          — per-rep fit-failure counting; governance-7
  accounting (OBSERVED gate + worst-case sensitivity + ceiling); P4 conditional
  worst-case denominator.
- `poc/99a-sim/results/frozen-run/verdict_99a.py` — run-validity gate (ceiling,
  all-114, no-ERROR, fields present); observed = S6 gate, worst-case disclosed.
- `poc/99a-sim/results/frozen-run/kot_99a_grid_v2.py` — resume RE-RUNS ERROR
  cells; `migrate_legacy` back-fills the banked OK cells.

## What the local evidence proves

### 1. FIXTURE-RELEVANT BIT-IDENTITY  (`evidence-bitid-vs-original.log`)
`bitid_vs_original.py` compares Rev2 `fit()` against an inline reconstruction of
the ORIGINAL frozen selection logic across 320 fits (F1 config-0 + F2 esc, both
families). Result: **phi, Hinv, and every registered contrast (theta, SE, nu)
are bit-for-bit identical** — max|Δtheta| = 0, rel-SE = 0, rel-nu = 0; zero
Rev2 FitFailures on valid data. The only delta is the `converged` METADATA flag
on 2 reps (best.success vs the original's res.success — the review's own item-1
metadata fix); it never enters theta/SE/nu, so it is not a fixture quantity.

Why bit-identity holds despite the review's "require success": [MEASURED] the
reps whose first start reports success=False terminate with
`ABNORMAL_TERMINATION_IN_LNSRCH` AT the optimum (res1.fun == res2.fun to ~1e-10,
res1.x == res2.x to >4 dp, computable, interior) — a benign line-search stall,
and the deviance-lowest point is res1 itself. The patch therefore qualifies
candidates by COMPUTABILITY + finiteness (the actual fail-open defect), not the
raw success flag, keeping the registered "lowest REML deviance" selection
bit-identical on every valid fit while remaining fail-closed on the non-PD /
penalty / non-finite region.

### 2. GUARD + FAIL-CLOSED + ACCOUNTING SUITE  (`evidence-rev2-tests.log`)
`rev2_tests.py` — 39/39 PASS. Covers: deviance_fast surface unchanged (still
raises); reachable-wall fit bit-identical; total non-PD -> FitFailure(optimize);
an extreme computable phi with a genuine deviance is NOT misclassified (domain
test, not magnitude — review item 2); non-finite H / all-NaN Hinv (inv w/o
raise) / non-finite nu each -> FitFailure(hessian) (item 3); pipeline family
tag; governance-7 (fwer_events == OBSERVED gate, worst-case = observed+failures
as a NON-GATING sensitivity, ceiling separate); dominance observed<=worst-case;
determinism; P4 conditional worst-case denominator (item 5); verdict
run-validity (ERROR / missing cell / ceiling breach / missing fields all ->
run_valid False — item 6a); resume RE-RUNS ERROR cells (item 6b, logic mirror);
migrate_legacy idempotent + never touches ERROR cells (item 6c, logic mirror).

### 3. Regression
`reml_composite.py` __main__ fast-vs-dense self-test: max|dev_fast - dev_dense|
= 1.82e-12 (unchanged).

## MANDATORY on the pinned Modal image (executor — NOT replaceable by the above)
Bit-identity of phi/SE/nu supports but does NOT replace the S4.2 fixture gate:
1. Rebuild the pinned image; re-verify all 6 version pins exact.
2. Re-run the **S4.2 lme4/lmerTest fixture-equivalence** (config-0, reps 0-49,
   both families): |Δtheta| <= 1e-7, rel-SE <= 1e-5, rel-nu <= 1e-3, |Δp| <=
   B_run. EXPECTED to pass exactly as before (the engine's theta/SE/nu are
   bit-identical to the frozen selection on the computable domain).
3. Re-run S2 determinism (100/100), the exact-REML smoke, and the small-slice.
4. `python kot_99a_grid_v2.py --mode migrate` (back-fill the 14 banked OK cells),
   then resume `--mode full` (re-runs ONLY the 100 ERROR cells under the guard;
   OK cells skipped), then `verdict_99a.py` (must report RUN VALID True with the
   fit-failure rate per cell <= 0.1%).

## Governance
Numerics-only patch on the non-PD / penalty / non-finite region; the fixture
quantities (theta/SE/nu/p) are bit-identical on every valid fit and the
registered S6 statistic (OBSERVED realised FWER count) is UNCHANGED. No margin,
test, threshold, seed, R, or acceptance criterion is altered -> no re-freeze of
the frozen object; the patch goes through the normal pre-commit review gate.
The worst-case (failures-as-events) count is a disclosed non-gating sensitivity;
the S4.2 0.1% fit-failure ceiling is enforced separately as a run-validity gate.
