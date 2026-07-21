# 99a Rev4 — Cross-Vendor GPT-5.6 Re-Review (verifies the Rev3-re-review fixes)

**Reviewer:** GPT-5.6 (`gpt-5.6-sol`, xhigh) via `run-review.sh`. **Date:** 2026-07-21. **Target:** `kernel-construction-methodology-proposal-99a.md` (Rev4, `4c74e980`) vs `99a-rev3-xvendor-review.md`. **Raw:** `poc/gpt56-review/99a-rev4-xvendor/`.

**Role note (mechanical):** verbatim reviewer output. **Verdict: targeted revision needed (converging).** THIRD cross-vendor pass confirming the **governance architecture is sound to adopt for a bounded pilot**. Confirmatory-experiment prereg residuals → **Rev5** (all statistical/operational specification, no redesign): (1) atomic FWER enumeration + full transition matrix + procedure-adjusted bounds; (2) UCT executability pinning (claim count/class allocation, generator/labeler separation, comparator selection inference); (3) Rung-0 conditional futility as a formal simultaneous confidence bound; (4) MINOR kill-rule wording sweep. Reviewer: "after the four targeted fixes … the experiment should be suitable for preregistration."

---

## Verbatim GPT-5.6 re-review output

## Overall verdict

**Targeted revision needed (converging).** Rev4 is sound enough to adopt the governance architecture for a bounded pilot, but the confirmatory experiment is not yet ready to preregister/freeze. The remaining work is statistical and operational specification, not material redesign.

| Item | Assessment |
|---|---|
| T-source estimand | Resolved in concept; not fully executable at freeze quality |
| FWER / zone geometry | `δ ≥ m` resolved; FWER procedure still incomplete |
| Non-compensatory endpoint | Resolved |
| Rung-0 A2-IR/H coverage | Resolved in substance; uncertainty rule needs formalization |
| Kill / precedence / text rule | Original contradiction resolved; one minor inconsistency remains |
| §8 consolidation | Resolved |

## Prioritized issues

1. **MAJOR — strong FWER control is not yet demonstrated.**

   Rev4 provides a useful skeleton—initial weights summing to α, Holm within E1, recycling edges, and rejection-only propagation—but E1–E8 are not actually elementary nulls. E1 contains seven shuffle tests; E2/E3 contain several possible four-zone claims; H-HUMAN combines fidelity and cost; and H-TEXT-FORMAT potentially contains multiple formats/endpoints ([§4.6](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:920)).

   More directly, operative advancement rules still use 95% confidence bounds ([H-GRAPH threshold](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:954)), although initial graphical local levels are much smaller than .05. That conflicts with the later requirement for “matching confidence.” Also, every downstream node has positive initial alpha, so an indeterminate E1 does not mathematically prevent E2–E8 from being confirmatory despite the stated gatekeeping intent.

   **Fix:** enumerate every atomic null, including directional/equivalence components, safety gates, H-HUMAN endpoints, format comparisons, and candidate-vs-T comparisons. Publish the complete transition matrix and update algorithm. Derive each zone from one node-level simultaneous confidence set or a closed local test, and replace every operative 95% threshold with its procedure-adjusted bound. Then simulate both strong-FWER behavior and adoption-path power under that exact implementation.

2. **MAJOR before preregistration — complete the new UCT estimand and selection inference.**

   The central repair is substantively correct: natural packet-relative gold, the same blinded consumers and budgets, independence from Stage 2, and one natural-stratum macro-BA contrast feeding the four-zone rule are now explicit ([natural gold](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:641), [UCT definition](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:847)).

   Two details prevent calling it fully executable:

   - Per-concept three-class balanced accuracy is undefined when a natural concept has no claim from one of the three gold classes. Unlike the nonce stratum, the natural stratum does not explicitly guarantee a 3/3/3—or other positive-per-class—allocation.
   - The comparison arm is selected by the outcome-dependent hierarchy. A single selected-arm CI is not automatically valid when hierarchy outcomes and UCT performance are correlated.

   **Fix:** pin the natural claim count, class allocation, sampling/exclusion rules, and adjudication protocol. Separate held-out-source-exposed claim generators from packet-only gold labelers. Pin consumer assignment, carryover protection, rendering/truncation, and format-competence checks. For the comparator, either select using outcome-disjoint calibration data or include every candidate-vs-T UCT contrast in simultaneous/selective inference within E2.

3. **MAJOR preregistration condition — formalize Rung-0 conditional futility.**

   The requested structural repair landed: unreviewed A2-IR and H are included, and every reviewed route uses a route-specific differential review increment relative to T ([Rung 0](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1256)).

   “Maximum credible” is not yet a mathematical stopping bound. The calculation must propagate uncertainty from both the Rung-0 route-vs-T contrast and the review-calibration pilot, while respecting sequential and multiple-testing error. The independent pilot also uses human review, conflicting with the description of Rung 0 as occurring before any human apparatus exists.

   **Fix:** define a simultaneous one-sided upper confidence or prediction bound for each `route − T + Δ_rev(route)` and permit branch termination only when every bound lies in the futility region. Account for this rule in sequential error spending. Credit the calibration pilot’s human cost explicitly; if such bounds cannot be obtained, retain the already-stated fallback prohibiting whole-branch termination.

4. **MINOR — finish the kill-rule wording sweep.**

   The main H-GRAPH and text rules are corrected. However, R4e says killing occurs only through equivalence/inferiority or futility ([R4e](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1591)), while the unreviewed-drafting rule also kills on a breached hard gate ([§4.8](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1127)). Define a hard-gate breach as an allowed registered kill event, or change that outcome to “cannot advance.” Also replace the ambiguous “if H-GRAPH fails” in §3.2 with either “is killed” or “fails to advance.”

## Confirmed strengths

- The natural-stratum UCT is now the dominant decision task, not a conditional Stage-2 surrogate.
- Packet-relative `ENTAILED/CONTRADICTED/UNDERDETERMINED` labeling correctly prevents held-out truth from converting packet-unsupported content into known content.
- `δ ≥ m` makes the four decision zones geometrically non-overlapping.
- The hurdle endpoint retains every failed record, applies an arm-level safety gate, and floor-scores failures, making H−A2-IR defined on every concept ([§4.5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:812)).
- The original kill-versus-indeterminate contradiction and text-cost wording are substantially repaired.
- [§8.0](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1329) is now a clear controlling table; the older rows are explicitly amended, superseded, or historical.

After the four targeted fixes—especially the atomic FWER specification and adjusted decision bounds—the experiment should be suitable for preregistration.
