# 99a Rev5 — Cross-Vendor GPT-5.6 Re-Review (final statistical gate)

**Reviewer:** GPT-5.6 (`gpt-5.6-sol`, xhigh) via `run-review.sh`. **Date:** 2026-07-21. **Target:** `kernel-construction-methodology-proposal-99a.md` (Rev5, `ac363d26`) vs `99a-rev4-xvendor-review.md`. **Raw:** `poc/gpt56-review/99a-rev5-xvendor/`.

**Role note (mechanical):** verbatim reviewer output. **Verdict: targeted revision needed — NOT prereg-suitable.** The non-statistical design has CONVERGED (UCT executability, early-node gatekeeping, kill-wording, Rung-0 substance all confirmed resolved). The remaining blocker is the **multiplicity / FWER machinery**, and these are **specification gaps, not deferrable constants**: (1) a provably-valid multiplicity procedure (theorem + unique safety-null ledger — the atomic-graphical matrix transfers full family weight while true elementary nulls remain); (2) the **FWER/power SIMULATION**, which the reviewer flags as "a preregistration acceptance artifact, not a value that can be pinned at freeze" (i.e. must be BUILT + RUN, not written); (3) Rung-0 across-sequential-look coverage + the prediction-bound algorithm; (4) MAJOR-new: H-TEXT-FORMAT selection-sensitivity / single-endpoint. **Coordinator disposition: PAUSE the revise-cycle** (2 rounds haven't closed FWER; the simulation is not a prose fix) and surface a design-strategy fork (simplify the confirmatory-claim structure to reach a standard cited procedure, vs push the ambitious atomic-graphical one) + the simulation-build to the maintainer (#59). Governance-architecture adoption for a bounded pilot remains available now (triple-confirmed).

---

## Verbatim GPT-5.6 re-review output

## Overall verdict

**Targeted revision needed.** Rev5 resolves the UCT residual and kill-rule inconsistency substantially, but the confirmatory experiment is **not yet suitable for preregistration**. The remaining problems are statistical specification defects, not a material redesign of the experiment or governance architecture.

## Prioritized issues

1. **BLOCKING — the advertised atomic strong-FWER procedure is not yet valid.**

   The zero-level gatekeeping property is fixed: all initial alpha is on E1, E1 only releases to E2, and an indeterminate E1 or E2 leaves downstream levels at zero ([transition matrix](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1061)). But the matrix operates on ten composite nodes, not the 95 elementary nulls.

   A node releases its **entire** alpha after any decisive zone, even though only part of its four-zone family has been rejected ([update rule](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1087)). For example, when E3 truly lies in the superiority zone, its superiority null is false but its inferiority and one equivalence-component null remain true; nevertheless all E3 weight transfers to E4. Standard graphical recycling does not justify transferring the full family weight while true elementary nulls remain unless a specific closed/gatekeeping theorem and compatible transfer rule are supplied. Independent errors at E3 and downstream can otherwise consume the same local alpha.

   The claimed atomic ledger is also incomplete or duplicative relative to the hurdle rule:

   - The endpoint says every arm in a Level-2 contrast must clear its safety gate ([§4.5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:895)), but E1/E1b contain no safety-gate nulls, and gates for B, T, T′ and shuffled comparators are absent from the enumeration.
   - Several gates, such as gate(A1), are counted repeatedly in different nodes rather than represented as unique elementary hypotheses.
   - E1 does not unambiguously pin the endpoint/stratum for each shuffle contrast.
   - “Holm-assigned” per-arm confidence intervals are not defined precisely enough to guarantee the claimed simultaneous coverage.

   **Fix:** publish a unique elementary-hypothesis ledger, explicitly identify which safety gates govern every contrast, and implement either:

   - a genuinely atomic graphical/closed procedure whose transfer matrix operates on elementary hypotheses and transfers only legally releasable alpha; or
   - a formally cited/proved family-gatekeeping procedure with valid rejection gain factors.

   Include a mathematical strong-FWER argument, not simulation alone.

2. **BLOCKING — the required FWER/power simulation has not actually been performed.**

   Rev5 mandates a future freeze-record simulation ([§4.6 item 7](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1131)); no tracked implementation or results accompany Rev5. Moreover, the proposed configuration “each single node’s nulls false” is infeasible for a four-zone node: its superiority and inferiority nulls cannot both be false simultaneously.

   **Fix:** after correcting the procedure, simulate feasible boundary/interior configurations for every zone, mixed safety-gate states, selection outcomes, Stage-2 execution/non-execution, and correlated as well as weakly correlated endpoints. Report Monte Carlo uncertainty and adoption-path power. This is a preregistration acceptance artifact, not a value that can simply be declared “pinned at freeze.”

3. **BLOCKING — Rung-0 is formalized across routes, but not across sequential looks.**

   Rev5 correctly defines \(U(r)\), covers all four reviewed routes, carries pilot transfer uncertainty, preserves the unboundable-increment fallback, and credits the pilot’s human cost ([Rung 0](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1503)). However:

   - Bonferroni \(\alpha_0/4\) covers routes only; it does not cover repeated interim looks.
   - The prediction-bound construction and transfer model are not specified—“propagates estimation-plus-transfer uncertainty” is not yet an executable algorithm.
   - Binding futility protects confirmatory FWER, but it does not validate the claimed \(1-\alpha_0\) futility bound under repeated looks. Power simulation quantifies branch loss; it does not restore sequential coverage.

   **Fix:** preregister either an anytime-valid simultaneous prediction sequence or an explicit route-by-look alpha allocation/spending rule, plus the exact pilot-to-campaign transfer model and bound formula.

4. **MAJOR, new — H-TEXT-FORMAT remains outcome-selection-sensitive and endpoint-inconsistent.**

   The hypothesis still describes equivalence on comprehension, format handling, and consumer cost ([§4.1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:639)), while E8 makes only Stage-2 host macro-BA confirmatory and calls the other outcomes descriptive ([E8](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1058)).

   Also, saying the estimand is “post-selection by definition” does not by itself make the selected-winner CI valid. Stage-1 selection and Stage-2 format effects can be correlated because they use the selected artifacts and concepts.

   **Fix:** rewrite H-TEXT-FORMAT to name only the single confirmatory endpoint, and either cover every candidate-arm × format contrast simultaneously, use outcome-disjoint Stage-2 data, or provide valid conditional/selective inference.

5. **Nonblocking operational cleanup — descriptive external-truth labeling lacks an assigned role.**

   Source-exposed generators may not label, while packet-only gold labelers may not see the held-out source. The descriptive external-truth label therefore has no specified producer. Add a separate source-exposed descriptive-label role or remove that secondary label. This does not compromise the confirmatory packet-relative estimand.

## Findings that are resolved

- **UCT:** The nine-claim 3/3/3 allocation, quota/replacement/fallback rules, generator–labeler separation, consumer assignment, carryover protection, rendering/truncation, and competence gate are executable. E2’s simultaneous four-candidate set makes the selected candidate-vs-T inference valid under arbitrary hierarchy selection ([UCT pins](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:944)).
- **Early-node gatekeeping:** An indeterminate E1 or E2 mathematically leaves downstream local levels at zero.
- **Kill wording:** The operative rules consistently treat hard-gate breach as cannot-advance, not kill ([§4.8](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1342)). The loose “killing or demoting” language in criterion 9 is non-operative editorial wording.
- **Rung-0 substance:** Route coverage, differential review increments, conservative fallback, and human-cost crediting are all improved correctly.

## Freeze-time values versus genuine gaps

The named margins, transition fractions, critical constants, budgets, candidate cap, reserve list, similarity/competence thresholds, \(\alpha_0\), futility threshold, look times, safety threshold, component weights, prices, seeds, and replication counts are legitimate freeze-time pins ([deferral list](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2054)).

The missing FWER theorem/transfer rule, unique safety-null ledger, Rung-0 across-look coverage mechanism, prediction-bound algorithm, E8 selection adjustment, and completed simulation are **specification gaps**, not deferrable constants.

The architecture remains strong and convergent, but one more targeted statistical revision is required before preregistration.
