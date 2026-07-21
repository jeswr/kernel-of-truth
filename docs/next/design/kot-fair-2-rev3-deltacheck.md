# KOT-FAIR/2 Rev3 — Cross-Vendor GPT-5.6 Delta-Check Re-Review

**Reviewer:** GPT-5.6 (`gpt-5.6-sol`, xhigh) via `run-review.sh`. **Date:** 2026-07-21. **Target:** `kot-fair-2-spec-p3mf0.md` (Rev3, `151c3fab`) against the Rev2-re-review reconciliation. **Raw:** `poc/gpt56-review/kotfair2-rev3-deltacheck/`.

**Role note (mechanical):** verbatim reviewer output. **Verdict: targeted revision needed (a short Rev4-level textual repair).** The reviewer INDEPENDENTLY re-derived the census arithmetic and CONFIRMED R2-01 is soundly fixed (FOLIO 8013 vs 204; POWER-CENSUSED vs width-limited feasible+deterministic; P3-E-CAL GREEN no longer deadlocked; components vector-columns, not evicted). Residuals → **Rev4** (2 HIGH + 4 MEDIUM + 1 LOW, all textual): (1) repeatability still fail-open on the goodput FLOOR (needs a direction-aware admissibility rule); (2) CENSUS-WIDTH-LIMITED scalar-eligibility contradiction §0 vs §1.4 (needs 3 explicit states); (3) max-N census size §1.4 vs §7.2; (4) right-censored p95 conservative rule; (5) UNPROVEN path-(b) fit-leg comparator; (6) stale budget-coordinate count. Freeze remains externally gated regardless (#57/Part C/THREAT/empirical).

---

## Verbatim GPT-5.6 delta-check output

## Verdict

**Targeted revision needed.** Rev3 fixes the original arithmetic deadlock and most of the Rev2 findings without requiring material redesign. However, two downstream contradictions mean the priority repairs are not yet fully closed—most importantly, comparator repeatability can still fail open on the newly explicit goodput floor.

I did not count the four acknowledged external gates as findings.

## Priority findings

1. **HIGH — Repeatability/admissibility is still fail-open for floor-type resources.**

   Rev3 correctly defines minimum goodput as a floor and tests S conservatively with `LCB95(goodput) ≥ floor` ([§3.1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:342)). But the repeatability and membership clauses revert to ceiling-only language:

   - S generically proves fit at “resource UCB95.”
   - Comparator membership uses “point estimate (or LCB95).”
   - Only a dispersion-widened **UCB** crossing is mapped to block/carry ([§3.5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:451), [§5.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:664)).

   For a comparator whose point goodput exceeds the floor but whose LCB falls below it because of dispersion, choosing the permitted LCB membership rule can exclude it without triggering the UCB-only band-failure disposition. That reopens the exact uncertainty-driven attrition channel.

   **Fix:** freeze one direction-aware rule, preferably:

   - S: UCB for upper ceilings; LCB for lower floors.
   - Comparator membership: point estimate in the bound’s stated direction; or, if using a favorable bound, LCB for ceilings and UCB for floors.
   - Any point-fit/adverse-bound-fail case—UCB crossing a ceiling **or LCB crossing a floor**—must map to tiered W1 block/carry.
   - Remove the unresolved “point estimate (or LCB95)” choice and replace all generic “UCB”/“exceeds” wording accordingly.

2. **HIGH — `CENSUS-WIDTH-LIMITED` has contradictory scalar-eligibility semantics.**

   The operative census rule says a width-limited component still takes the exact LCB gate: a PASS remains scalar-eligible; only a FAIL becomes `WIDTH-LIMITED-INCONCLUSIVE` and vector-only ([§1.4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:207)). The self-check says the same ([self-check](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:1122)).

   But §0 lists the `CENSUS-WIDTH-LIMITED` terminal status itself as scalar-ineligibility, which makes W1 unavailable even after a passing maximum-N census ([§0](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:74)). Two conforming graders can therefore reach different W1 availability decisions.

   **Fix:** distinguish three states explicitly:

   - `POWER-CENSUSED/PASS`
   - `CENSUS-WIDTH-LIMITED/PASS`
   - `WIDTH-LIMITED-INCONCLUSIVE/FAIL`

   Only the third state should cause scalar ineligibility.

3. **MEDIUM — Maximum-N census size is inconsistent between §1.4 and the executing instrument.**

   Section 1.4 allows width-limited components 100% of rows when they feed no CAL-ORDER cell; otherwise the maximum is 50% ([§1.4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:207)). Step 2 instead caps every width-limited component at 50% ([§7.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:782)). This changes the LCB membership decision for components such as IFEval.

   **Fix:** state one deterministic rule in §1.4, §7.2, MF0-R3a, and the manifest schema. Also specify whether the hash partition is component-global or rung-specific. A clean rule is 50% whenever the component contributes to any known-order CAL-ORDER endpoint; otherwise 100%.

   The 50% cap does structurally preserve at least half the data for CAL-ORDER and item 17 requires a primary-power recheck. It does not, by itself, prove that reducing an earlier 80% order split to 50% preserves power; the item-17 failure consequence should explicitly return the cap/split design for revision.

4. **MEDIUM — Right-censoring does not yet define a unique, conservative p95.**

   Timed-out requests are declared “right-censored at the timeout value,” but no survival estimator or non-identifiable-tail rule is specified ([§3.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:404)). Ordinary rank-based order-statistic CIs do not directly handle censoring, and if at least 5% of requests time out, the true p95 may only be known to exceed the timeout. Treating censoring as an observed latency equal to the timeout is not conservative.

   **Fix:** for the binding budget coordinate, assign timed-out/dropped/unfinished queries `+∞` latency, with a pinned quantile convention; or specify a censored-data estimator and make a non-identifiable p95/UCB equal infinity. Then the p95 is mechanically fail-closed.

5. **MEDIUM — The pairwise `UNPROVEN` statistic is defined, but the automatic path-(b) fit leg lacks its comparator.**

   The predicate is now well defined for an energy-comparison row against comparator \(C\). But “S fits \(B_k\)” is a budget evaluation with no intrinsic \(C\), while the formula still requires `point(proxy(C))`; it also says the label lives on an energy-comparison row that may not exist for a fit-only evaluation ([§3.1a](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:383)).

   **Fix:** freeze the path-(b) reference—either the budget anchor or every comparator in the hashed roster—and define a fit-output field. State how multiple pairwise results aggregate into the admissibility disclosure.

6. **LOW — The budget coordinate count remains stale downstream.**

   Section 0 now has five independently binding coordinates because accelerator memory and host RSS are separate, while §3.1 still says “four authority-defined components” twice ([§0](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:53), [§3.1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:335)). Correct the count or call them four resource classes with two separate memory coordinates.

## What Rev3 got right

- The census arithmetic is substantially correct. Independently,  
  \(SE_{\text{norm}}\le .02/(z_{.95}+z_{.80})=.0080435\). This gives approximately:

  - FOLIO: 8,013 items versus 204 available.
  - GSM8K: 594, about 45% of 1,319.
  - HellaSwag: 5,540, about 55.2%, hence width-limited under the cap.
  - BLiMP: 17,923, about 26.8%.

  Cluster DEFF can only increase these requirements. For every currently instantiated manifest row, POWER-CENSUSED versus width-limited is feasible and deterministic once the frozen DEFF/taxonomy is supplied. P3-E-CAL GREEN is no longer structurally deadlocked, and components remain mandatory vector columns rather than being evicted.

- The builder-to-campaign repeatability architecture is otherwise strong: immutable hashed membership, explicit carry precedence, pooled `R=1` repeat records, non-band failure dispositions, `K≥3` scoring-run strata, and a mechanical tier map.

- The adaptive-band instrument is now real and adequately wired: three synthetic probe classes plus a non-gating real adaptive subject, with existence gating band ratification.

- The sealed DiD now has a common matched-domain estimand and one named CI family; the remaining studentization and degenerate-cell details are explicitly preregistered in item 16 rather than chosen after results.

- The intended scalar/vector invariant, collision-case comparator statistic, FLOP-ledger labelling law, CP restriction, small-cluster/day rules, challenger admission, matched-RAG parity, and the cross-vendor LOW cleanups are substantively repaired.

## Legitimately deferred, not defects

The unresolved release counts for CLUTRR, ProofWriter and LiveBench; taxonomy/DEFF artifacts; actual class-band values; probe hashes; small-cluster method selection; \(\kappa_m/\tau_m\); and FLOP-ledger mismatch caps are properly assigned to ratification artifacts with fail-closed prerequisites. They are stipulated inputs, not missing technical dispositions.

So the design is close, but Rev3 is not yet technically sound as written. A short Rev4-level textual repair addressing the direction-aware admissibility rule and the listed seam inconsistencies should be sufficient.
