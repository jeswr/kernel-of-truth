# Cross-vendor review (GPT-5.6) — 99a estimator hardening (Rev1) — REJECT

> 6 blocking (fit()-selects-without-success garbage-fit; 1e12 sentinel not disjoint; Hessian not
> fail-closed; P4 conditional denominator; verdict/resume wiring; governance) + FWER math confirmed valid.
> All fixed in Rev2. Committed for the record.

---

Verdict: **REJECT**

The penalty concept is reasonable, and the failed-rep FWER bound is mathematically conservative, but current HEAD is not fail-closed and is not ready for the paid rerun.

1. Release-blocking optimizer defect

[reml_composite.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:356) selects results by `fun` without requiring `success`.

I reproduced these cases:

- Penalty-wall first start + finite but unsuccessful retry → estimate returned.
- Both starts unsuccessful with finite objectives → lower objective returned.
- Unsuccessful first start below a successful retry → unsuccessful result retained.

This directly violates the registered retry rule: after first-start non-convergence, the retry must converge or raise `FitFailure`. A penalty-induced abnormal line-search termination can therefore escape as a garbage fit. Additionally, `_last["converged"]` records `res.success`, not `best.success`.

A NaN first result also defeats the retry selection because `res2.fun < NaN` is false, causing `FitFailure` even when the retry succeeds.

Required correction: choose only among successful, computable results satisfying the pinned convergence tests; if neither start qualifies, raise `FitFailure`.

2. The `1e12` sentinel is not provably disjoint from real deviances

The claim “`fun >= 1e12` iff penalized” is false globally. On an actual composite-sized `8×96×3` design, I evaluated computable φ with all components `1e-12` and obtained a genuine deviance of approximately `6.79e13`, without a factorization failure.

Thus [the threshold test](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:367) can classify a real—albeit terrible—computable endpoint as the penalty. This is conservative failure rather than garbage acceptance, but the claimed equivalence is unsound. Validate the final φ by calling `deviance_fast` directly and track domain failures separately from numeric objective magnitude.

The objective catch also is not limited to `cho_factor(XtVinvX)`: it catches any `LinAlgError` from the entire `deviance_fast`, including the Woodbury-cap Cholesky and both NumPy Choleskys. That may be an acceptable “noncomputable factorization” policy, but the narrower claim is inaccurate.

3. Hessian handling is not completely fail-closed

[The Hessian wrapper](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:375) catches raised `LinAlgError`, but does not reject non-finite `H`, `Hinv`, or ν̂. `np.linalg.inv` can return an all-NaN matrix without raising; [contrast()](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:475) then silently falls back to `N-p` degrees of freedom because `NaN > 1e-300` is false. Explicit finiteness checks are required.

4. FWER conservatism itself is valid

For the intended event \(E\), define \(C=1\) on every failure and \(C=E\) otherwise. Then \(E\le C\) replication-by-replication, hence \(P(E)\le P(C)\) under arbitrary dependence between failure and rejection. No MCAR or independence-of-failure assumption is needed.

Clopper–Pearson remains valid provided replications are independent; its conclusion retains the registered 95% Monte-Carlo coverage qualification. Excluding failures or changing the denominator would indeed be invalid when failures correlate with extreme draws.

5. Power is not uniformly conservative

Unconditional power paths use denominator `R`, so failures are misses. But P4 is conditional:

[driver.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/driver.py:119) divides by successful-rep `conH_count`. Failed replications enter neither numerator nor denominator, so correlated failures can inflate \(P(\mathrm{FMT}\mid\mathrm{CON})\).

For a worst-case conservative completion, retain the observed numerator and use `conH_count + fit_failures` as the conditional denominator.

6. Verdict and resume wiring are incomplete

- [verdict_99a.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/results/frozen-run/verdict_99a.py:41) skips ERROR cells and never enforces `fit_failure_ceiling_pass`. It can therefore report FWER acceptance despite violating the registered 0.1% ceiling.
- The verdict does not require all 114 expected cells or the new failure fields.
- [The durable runner](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/results/frozen-run/kot_99a_grid_v2.py:118) treats every existing cell file—including the 100 ERROR files—as completed. It will not currently rerun those 100 cells.
- The 14 banked legacy records lack the new fit-failure fields. The ten completed REML cells can defensibly be migrated as zero failures because the old code would have crashed on any guarded probe; that migration still needs explicit provenance and wiring.

7. Fixture and freeze conclusions

At every φ where `deviance_fast` returns normally, the objective value is unchanged. Therefore a fit whose optimization path never activates the guard is byte-identical. That supports, but does not logically replace, the mandatory pinned-image lme4 fixture rerun. The claimed 160-fit SHA evidence is not committed as an auditable artifact.

“No re-freeze” is defensible for the numerical objective guard alone, subject to the fixture gate. It is not clearly defensible for replacing S6’s registered “realised FWER count” with the synthetic worst-case count: S4.2 says failed components are not rejected and counts fit failures separately, while S9 forbids changing acceptance criteria. Either:

- keep observed FWER as the registered statistic and report the worst-case count as a non-gating sensitivity, with the 0.1% ceiling separately enforced; or
- formally amend/re-freeze the controlling text before making the worst-case count the S6 verdict statistic.

Do not launch the 100-cell rerun until the optimizer-success, conditional-power, verdict, and resume defects are corrected and the fixture gate passes.