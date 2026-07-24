# Cross-vendor re-review (GPT-5.6) — 99a estimator hardening Rev2 — REJECT

> Rev2 re-review: 3 blocking (computability!=convergence; nu_monitor degenerate-inverse N-p fallback;
> verdict fail-open) + confirmed fixes. Coordinator adjudicated item 1 -> the registered tol_dev/tol_par
> convergence tests (not raw success, not bare computability). Fixed in Rev3. Committed for the record.

---

Verdict: **REJECT**

I require `success`—plus the pinned convergence checks—not computability alone.

### Blocking findings

1. **Computability does not establish convergence.**  
   `_admissible()` accepts any finite, computable result regardless of `res.success`; `fit()` then selects the lowest objective among those candidates ([reml_composite.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:374)). Therefore:

   - Two unsuccessful but finite/computable endpoints still produce an estimate.
   - An unsuccessful endpoint below a successful retry still wins.
   - `maxiter`, abnormal line-search away from the optimum, or another genuine non-convergence can escape identically to a benign stall.

   This conflicts with the registered rule: non-convergence triggers the retry, and a second non-convergence is counted as failure ([proposal](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2887)). The registered convergence tolerances are also not evaluated: `tol_dev` and `tol_par` are unused despite the required deviance **and** parameter-change tests ([proposal](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2966)).

   The cited [evidence log](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/results/frozen-run/rev2-hardening-validation/evidence-bitid-vs-original.log:1) proves identity with the already-rejected original selection. It does not record optimizer messages, start agreement, interiority, the asserted ~3% rate, or compare against a success-qualified implementation. Even if every observed stall was benign, the code does not condition acceptance on that evidence.

   Boundary retention does not justify accepting all unsuccessful endpoints. A narrowly certified boundary/KKT exception could be specified, but the present global computability exception is fail-open. The required policy is: select the lowest deviance only among successful, computable, finite candidates satisfying the pinned convergence tests; otherwise `FitFailure`.

2. **Hessian/ν handling is still not fully fail-closed.**  
   The new finite `H`/`Hinv` checks correctly close the all-NaN inverse case. But `_nu_monitor()` converts every `gCg <= 1e-300`—including a finite indefinite information inverse—into finite `N-p` ([reml_composite.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:483)). That finite fallback passes the ν finiteness gate, and `contrast()` contains the same fallback ([reml_composite.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/reml_composite.py:531)). Thus the claimed “fallback unreachable” property is false.

3. **The verdict validity gate is only partially fail-closed.**  
   It trusts the stored `fit_failure_ceiling_pass` boolean instead of independently checking `fit_failure_rate <= 0.001`, and requires only that boolean plus the rate ([verdict_99a.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim/results/frozen-run/verdict_99a.py:57)). Missing `fit_failures`, ceiling, detail, or worst-case fields can still pass. It also does not require exactly one structurally valid result per expected index.

### Delta disposition

| Item | Result |
|---|---|
| 2 magnitude sentinel | **Fixed.** No objective-magnitude classification remains; extreme computable deviances remain admissible. |
| 3 Hessian | **Partial; blocking residual** described above. |
| 5 P4 denominator | **Fixed.** Observed numerator over `conH_count + fit_failures` is the conservative completion. |
| 6a verdict | **Partial.** Current data correctly reports `RUN VALID: false` with 100 ERROR cells, but schema/ceiling enforcement remains fail-open. |
| 6b resume | **ERROR rerun fixed.** Absence of `ERROR` is treated as success without validating the record schema. |
| 6c migration | Mechanically implemented with provenance, but no longer sufficient after requiring optimizer success: the 10 banked REML cells may contain previously accepted unsuccessful fits and need revalidation/rerun. The four gate-cal cells are unaffected. |
| 7 governance | **Fixed.** Observed FWER remains the registered S6 gate; worst-case is non-gating sensitivity; 0.1% remains a separate validity gate. No registered threshold changed. |

Do not launch the paid 100-cell-only rerun. The computability qualifier leaves the original garbage-fit class open, and success qualification invalidates the assumption that all 10 banked REML cells can be migrated as zero failures.