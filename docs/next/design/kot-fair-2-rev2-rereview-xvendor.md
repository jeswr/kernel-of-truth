# KOT-FAIR/2 Rev2 — Cross-Vendor GPT-5.6 Re-Review

**Reviewer:** GPT-5.6 (`gpt-5.6-sol`, xhigh) via `run-review.sh`. **Date:** 2026-07-21. **Verdict:** targeted revision needed. **Raw:** `poc/gpt56-review/kotfair2-rev2-xvendor/`.

---

## Overall verdict: targeted revision needed

Revision 2 is substantially improved and does not require material redesign. The principal statistical architecture is now defensible, but several clauses remain internally inconsistent or insufficiently executable for the document to advance as technically complete.

I did not count the four acknowledged external blockers—Part C, the governance decision, THREAT ratification/hash pinning, or empirical ratifications—as findings.

### Disposition of the three CRITICAL findings

- **C-1: substantially, but not completely, resolved.** The operative analysis now fixes benchmark/domain weights, resamples item clusters within benchmarks, preserves pairing, and uses the same scheme for W1, domain NI, attribution and the sealed DiD. No operative within-domain benchmark-family resampling remains; the parent quotation is adequately disambiguated by the reading note ([§6.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:685)). Remaining problems concern the floor-census CP exception, incomplete max-t specification, and the sealed/public estimand alignment described below.
- **C-2: only partially resolved.** P3-E-CAL is now the named instrument for R0–R3 and correctly fails closed until the R0 model/hash is pinned ([§7.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:731)). I do not count the pending R0 pin itself as a finding. However, the new power rule is infeasible for several fixed benchmarks, so the census is not yet runnable as written.
- **C-3: only partially resolved.** Repeatability failure blocks W1 for the strongest-by-dev comparator and every \(C^d\), which closes the worst attrition channel. But lower-tier comparators may still be carried with an undefined “widened uncertainty” and W1 may subsequently pass. That does not satisfy a literal every-arm fail-closed gate.

## Prioritized issues and fixes

1. **HIGH — The floor-census power rule makes parts of the manifest impossible to calibrate.**

   [Section 1.4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:184) requires 80% power for distinguishing normalized effect \(2f=.04\) from the inclusion threshold \(f=.02\). Even under the optimistic independent-binomial model and using the entire benchmark, approximate power is only:

   - EWoK, \(n=4,374,c=.5\): 0.37
   - OpenBookQA, \(n=500,c=.25\): 0.17
   - FOLIO, \(n=204,c=1/3\): 0.09

   Cluster dependence reduces effective power further. Raising the `CAL-FLOOR` fraction cannot solve this once the full benchmark is insufficient, and §7.3 provides no disposition for that case.

   **Fix:** define a feasible, cluster-aware MDE/power target per component; compute power by simulation under its frozen cluster structure; enumerate every rung’s candidate set explicitly; and specify that an insufficient maximum available \(N\) makes the component vector-only or makes W1 unavailable, rather than making P3-E-CAL permanently impossible.

2. **HIGH — Census inference contradicts the claimed single cluster scheme.**

   Section 1.4 assigns Clopper–Pearson bounds to “single-accuracy components,” while §6.2 assigns nontrivial clusters to BLiMP, EWoK and other accuracy benchmarks. CP treats items as independent and can be anti-conservative under those clusters.

   **Fix:** use the cluster bootstrap whenever a manifest has non-singleton clusters. Permit CP only where the preregistration explicitly establishes that each item is its own independent cluster. Base census power on cluster count and cluster-size distribution, not raw item \(N\).

3. **HIGH — The lower-tier repeatability exception is not fail-closed or statistically defined.**

   [Section 3.5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:420) allows a non-frontier comparator to remain with its “class band replaced by measured dispersion.” It does not define how dispersion enters the item bootstrap, resource UCB, or W1 bound. Such a comparator can still be declared beaten despite failing the every-arm measurement gate.

   **Fix:** simplest and cleanest: any closed-roster comparator failing its frozen class band after the repeat rule blocks W1 at that rung. Remove the adverse-status scoring alternative. Also add the promised CPU/I/O/retry-heavy synthetic probes to the actual P3-E-CAL run steps, rather than mentioning them only in §3.5/register item 10.

4. **HIGH — The sealed DiD still needs a common estimand and one CI algorithm.**

   The sealed suite may contain a minimum of four domains, while the public rung index can contain a different domain set. Consequently, \(\Delta_{\text{sealed}}-\Delta_{\text{public}}\) can mix seal degradation with domain-composition change. In addition, “percentile/max-t” leaves two CI algorithms available ([§5.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:553)).

   **Fix:** require the two deltas to use the same frozen domains, construct map, normalization and macro-weights—either by sealing every active public domain or recomputing a public matched-domain delta. Select max-t or percentile explicitly, and specify studentization, null centering, zero-SE/degenerate-cell handling and Monte Carlo-error acceptance criteria.

5. **HIGH — The core-domain vector fallback conflicts with the scalar reporting rule.**

   [Section 0](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:64) says a non-scalar-eligible core domain can fall back to vector-column NI. But [§1.5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:198) prohibits reporting the scalar unless every core domain is scalar-eligible, while W1 still requires scalar superiority. Thus the fallback cannot actually preserve W1.

   **Fix:** choose one invariant. The least gameable rule is: if any core domain is not scalar-eligible, W1 is unavailable at that rung; vector NI remains diagnostic. If W1 is meant to remain available, the scalar’s surviving-domain estimand and weights must instead be defined explicitly.

6. **MEDIUM — `UNPROVEN` is named mechanically but its comparison statistic is not.**

   [The predicate](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:361) does not say whether proxy comparisons use means, medians, p95s or UCBs, how zeros are handled, or how measurement uncertainty affects a \(\kappa_m\) crossing. It also starts with “an advantage is claimed,” making its activation partially dependent on claim wording.

   **Fix:** define the summary and bound for every proxy, multiplicative-zero handling, and a path-(b) fit predicate that runs automatically whenever component-energy admissibility is invoked. The two-state boundary record, `UNPROVEN` claim label, total-energy prohibition and binding I/O/CPU interlock are otherwise sound.

7. **MEDIUM — The FLOP-ledger fallback cannot retain the “compute-matched twin” label.**

   The ledger itself is strong, but [§5.3 item 7](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:597) says that when exact ledger matching is infeasible, equal tuning compute plus publication of the mismatch suffices. Equal tuning budget does not make training exposures compute-matched.

   **Fix:** preregister a maximum allowable mismatch per ledger coordinate. Beyond it, retain the arm as an equal-tuning-budget comparator but prohibit “compute-matched twin” wording.

8. **LOW — Clean up remaining open and stale clauses.**

   - Resolve the acknowledged Offline batch-shopping rule; disclosure is not a fix ([§3.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:372)).
   - Freeze a minimal base-image allowlist, not merely “generic components.”
   - Add the proposed non-gating out-of-family calibration subject.
   - Change the stale R1b prereg row and Rev1 self-check from raw-score units to normalized units ([row R1b](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:931)).
   - Add an explicit `energy_boundary_ref` field to the KOT-LIFE schema.
   - Reword the C-2 self-check as conditional on register item 21; a register slot is not itself a defined R0 model/hash.

## What Revision 2 got right

- It removes operative benchmark-family resampling and aligns KOT-FAIR with the companion THREAT fixed-weight cluster scheme.
- It pins the DiD comparator before outcomes and resamples public and sealed suites jointly.
- It provides a real per-rung P3-E-CAL census path and explicitly discloses pure-neural anchor bias.
- It closes comparator attrition for the most consequential comparators and sensibly separates deterministic and adaptive/TTC repeatability bands.
- The energy-boundary state machine, naming discipline, path-(b) co-statement and Pareto-budget option are materially stronger and defensible.
- The matched-RAG control is comprehensive: proposition parity, shared and native retrieval, recall/provenance, position/random controls, and equal ledgers; the companion also supplies parsing/calibration/selective-prediction parity.
- Decontamination now uses directionally correct LCB/UCB gates, disjoint development/validation sets and mechanically decidable criteria.
- The sealed suite is power-sized rather than fixed at 250/domain.
- The THREAT adoption is faithful, including claim-conditioned `G-*`, and no duplicate prereg-row identifiers were found.

A short Revision 3 addressing the issues above should be sufficient for technical advancement.
