# Cross-vendor re-review (GPT-5.6) — 99a estimator Rev3 — REJECT (counterexamples)

> Rev3 re-review: BLOCKING-1 (success!=tol_par; polish-no-op not a certificate), BLOCKING-2 (nu N-p
> fallback reachable via degenerate gCg), BLOCKING-3 (verdict index/content/rate not validated). Fixed
> in Rev4: direct rel_dev + KKT-stationarity certificate; cond-gate + nu NaN; verdict index->kind+content.

---

Verdict: **REJECT** — do not authorize the paid 110-cell rerun yet.

### Blocking findings

1. **BLOCKING-1 remains open; judgement call B is unsound.**

   [`_converged()`](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:374) accepts every finite/computable `res.success=True` result without evaluating either registered change test.

   The claimed subsumption is false:

   - L-BFGS-B stops when the `ftol` condition **or** the projected-gradient `gtol` condition fires—not both.
   - `ftol=1e-15` subsumes only `tol_dev=1e-12`; it says nothing about parameter change.
   - `gtol=1e-10` is dimensionally unrelated to `tol_par=1e-9` and does not bound the last parameter displacement or relative deviance change.

   These are separate stopping rules, and SciPy exposes no parameter-step tolerance for L-BFGS-B. [SciPy 1.14.1 documentation](https://docs.scipy.org/doc/scipy-1.14.1/reference/optimize.minimize-lbfgsb.html)

   Exact escaping class: a result with `success=True` from either stopping condition whose final relative parameter change exceeds `1e-9` is accepted at [lines 401–404](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:401).

   A same-options, numerical-Jacobian counterexample produced:

   - `success=True`, projected-gradient message
   - returned `x=0.49695` for an optimum at `1`
   - last `rel_par=0.4966`
   - relative objective gap `6.4e-10 > tol_dev`
   - a fresh identical polish was nevertheless a zero-change no-op

   Consequently, a polish no-op is not a general convergence certificate either. [`pol.success`, `pol.jac`, and KKT residuals are never checked](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:405). An abnormal line-search or finite-difference blind spot can repeat at the same non-optimal point and pass both comparisons.

   The 320-fit evidence is useful evidence about the observed benign stalls, but not adequate for the universal qualifier. It examines only `success=False` first starts and only one synthetic away-point. It does not record registered changes for `success=True` candidates, which is precisely the escaping branch. The asserted success-fit `~5e-6` polish wandering is also absent from the cited [evidence log](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/results/frozen-run/rev2-hardening-validation/evidence-bitid-vs-original.log:1); if genuine, it contradicts rather than subsumes the registered `tol_par`.

2. **BLOCKING-2 is improved but not fully closed; judgement call A is unsound as implemented.**

   The PD gate is applied only after [`_hessian()` returns](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:451). But `_hessian()` already calls [`_nu_monitor()` on every Richardson candidate](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:543), before the PD check at [line 476](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:476). Therefore the statement “reject indefinite H before the ν path” is false in call order.

   Also, PD implies `gCg > 0`, not `gCg > 1e-300`. For example, finite `H=1e302·I` passes the current PD/inverse checks while producing `gCg≈1.4e-303`; [`_nu_monitor()` then returns `N-p`](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:524). Thus the fallback is still reachable and can determine Richardson convergence for a fit whose final H passes the gate.

   Removing the fallback from [`contrast()`](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:582) is correct, but it does not repair the pre-gate ladder use.

3. **BLOCKING-3 remains fail-open.**

   The independent comparison against `0.001` and duplicate/missing-index detection are real improvements. However:

   - Expected index-to-kind/config mapping is not checked. The committed test itself supplies 114 FWER records for indices `0..113` and expects `run_valid=True` at [rev2_tests.py:231](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/results/frozen-run/rev2-hardening-validation/rev2_tests.py:231). I confirmed current code reports `run_valid=True`, with 114 FWER, zero power, and zero gate-cal cells.
   - “Full schema” is only key presence. Power `paths`, mandatory F10/P6 `rung0`, expected gate arms/gammas, and index metadata are not validated. I confirmed a correctly kind-labelled 114-record set with no power paths, no rung-0 records, and only one gate arm still reports `run_valid=True`.
   - [`fit_failure_rate`](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/results/frozen-run/verdict_99a.py:69) is not required to be finite, nonnegative, or consistent with `fit_failures/R`. `NaN > 0.001` is false. I confirmed both `NaN` and `fit_failures=40000, rate=0` can yield `run_valid=True`.
   - Resume validation has the same key-only/wrong-kind weakness at [kot_99a_grid_v2.py:60](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/results/frozen-run/kot_99a_grid_v2.py:60), so a full-schema FWER record at a gate-cal index can suppress the required cell.

   The committed bank does contain exactly 100 ERROR records, 10 old REML successes lacking the new fields, and four gate-cal successes at indices 110–113. Therefore the intended current-data scope is indeed 110 cells. The code does not fail-closed enforce that scope.

### New inconsistency

A polish-qualified `success=False` candidate is stored with [`_last["converged"] = False`](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:487). It appears unused, but now contradicts the qualifier’s semantics.

The Rev3 test suite could not be rerun in this read-only environment because SciPy’s stats import requires a writable temporary directory. The static review and the no-write counterexamples above are sufficient to establish the escaping cases.