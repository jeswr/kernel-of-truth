# 99a Rev3 — Cross-Vendor GPT-5.6 Re-Review (verifies the Rev2-review fixes)

**Reviewer:** GPT-5.6 (`gpt-5.6-sol`, effort `xhigh`), via `poc/gpt56-review/run-review.sh` (isolated `CODEX_HOME`, npx codex `0.144.1`). **Date:** 2026-07-21.
**Target:** `kernel-construction-methodology-proposal-99a.md` (Rev3, `ff183ade`), against the Rev2 cross-vendor review `99a-rev2-xvendor-review.md`. **Raw output:** `poc/gpt56-review/99a-rev3-xvendor/`.

**Role note (mechanical):** verbatim reviewer output; verdict/findings are the reviewer's. **Verdict: targeted revision needed (converging).** Rev3 fully resolved 7 of 10 prior findings (graph isolation via A2-IR, crossed-hierarchy power, LCC, production-independence gate, identity/hash, C3-nonce, decision-zones-partial). **Residuals → Rev4:** 1 adoption-blocker (natural-stratum T-source estimand still unspecified) + 4 MAJOR (confirmatory-family FWER control; non-compensatory-endpoint completeness; Rung-0 futility not covering A2-IR/H; kill-vs-precedence consistency) + 1 MINOR (§8 stale-row consolidation). Governance architecture confirmed **sound for a bounded pilot**. Disposition: focused Rev4, then a re-review to clear for adoption (with the #59 maintainer decision).

---

## Verbatim GPT-5.6 re-review output

## Overall verdict

**Targeted revision needed.**

Rev3 is a substantial improvement and is not a material-redesign case. The governance architecture is sound enough for a bounded pilot. The constructed-store decision, graph-route adoption, and KBUILD-0 preregistration should remain blocked until the dominant text estimand and confirmatory statistics are repaired.

### Prior-finding crosswalk

| Finding | Assessment |
|---|---|
| C1 graph isolation | **Resolved in substance.** A2-IR receives matched atoms/relations, evidence, prompts, budgets, endorsement, and visibility; H−A2-IR removes the oracle-parse confound, and the family is explicitly an upper-bound mechanism test ([§3.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:475), [arms](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:632)). Narrow the claim to “explicit graph materialization/closure”: a flat list of typed relations still contains reconstructible topology. |
| C2 common text estimand | **Only partially resolved; still adoption-blocking.** T is now independent of constructed records and T′ is correctly confined to format with upstream costs charged. But the asserted common deterministic endpoint is only defined for nonce renderer text. The decision-grade natural comparison instead invokes an unspecified mixture of claim task, adequacy review, and conditional Stage 2 ([T arm](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:669), [common-estimand claim](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:751)). |
| C3 three-valued target | **Resolved for the nonce primary.** `R(packet)`, TRUE/FALSE/UNKNOWN, the fully-identifying restriction, and separate supported-content/abstention reporting are coherent ([§4.5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:727)). The natural stratum still needs its own packet-relative target specification. |
| Decision zones/testing family | **Partial.** The four zones and T/T′ separation landed, but the alpha procedure is not yet validly specified. |
| Crossed analysis/power/no widening | **Resolved.** The crossed model, exact-analysis simulation, joint power, specified true effect, and prohibition on power-driven margins are appropriate ([§4.6](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:777)). |
| Non-compensatory fidelity | **Conceptually resolved, operationally incomplete.** Hard gates exist, but the arm-level estimand after a record fails a gate is undefined. |
| LCC | **Resolved.** Declared prices, shared-cost allocation, uncertainty, robustness reversal, and the one-revision-cycle limitation are all present ([§4.8](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:924)). |
| Production independence | **Resolved.** Two-human/authority floor, evidence-first judgments, prohibited drafter source selection, dual assembly, and human-only KBUILD endorsement are strong ([§1.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:246)). |
| Rung 0 scope | **Core fix landed, integration incomplete.** It no longer directly kills reviewed routes, but its arm set was not updated for A2-IR/H. |
| Identity/hash separation | **Resolved.** Semantic identity now changes only with normative content; decision/provenance changes with selection inputs ([§1.1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:174)). |

## Prioritized residual and new issues

1. **Adoption blocker — define one executable T-source estimand.**

   The natural stratum has ordinary source text, for which the document itself supplies no deterministic parse-back, while the formal `R(packet)` scorer is defined only over the nonce generator grammar. Stage 2 is also conditional on a constructed-arm benefit, so the dominant text comparison could lose its realistic common consumer precisely when construction is weakest ([natural stratum](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:599), [Stage 2 condition](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:699)).

   **Fix:** make an unconditional, common held-out claim task the T-source decision endpoint, using the same blinded evaluator/consumer and budgets for T and constructed arms. Define natural TRUE/FALSE/UNKNOWN relative to the published build packet; use the held-out source for claim generation or external-truth evaluation, not to label unsupported packet content as known. Keep nonce oracle parse-back as an explicitly secondary upper bound. Specify one statistic—or a declared conjunctive hierarchy—feeding the four-zone decision.

2. **Major — the confirmatory family does not yet control familywise error.**

   Testing every member at full α=.05 after any earlier “definitive” classification is not ordinary fixed-sequence control: a correct early classification permits later tests, so classification-error probabilities can accumulate. The first member also contains plural shuffle contrasts without an internal allocation. Moreover, §4.5 calls A2−A1 and A1−A0 primary family contrasts, but §4.6 omits both, including H-REVIEW ([contrast list](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:764), [family](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:797)).

   The four zones can also overlap unless the relationship between δ and `m` is constrained.

   **Fix:** enumerate every elementary confirmatory claim and use Holm, closed testing, or a graphical gatekeeping procedure with local alpha weights and explicit recycling. Include H-REVIEW/citation increments or label them exploratory. Require `δ ≥ m` or otherwise specify mutually exclusive zones and precedence. Re-run power simulation under that final multiplicity procedure.

3. **Major — make the non-compensatory endpoint mathematically complete.**

   A failed record is said to be excluded from ranking, while construction failures must remain in the denominator. That leaves H−A2-IR undefined when either record breaches a hard gate ([composite](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:741)).

   **Fix:** preregister a hurdle or lexicographic estimand: first compare gate-pass/failure rates with confidence bounds; permit composite comparison only after every arm-level safety gate passes. Explicitly retain all failed records in the pass-rate denominator.

4. **Major — complete the Rung-0 conditional-futility design.**

   Rung 0 observes A0, unreviewed A2, B, and T, but not unreviewed A2-IR or unreviewed H. Therefore `best-unreviewed + Δ_rev` does not bound the newly added IR/graph routes or graph–drafter interaction ([Rung 0](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1084)).

   **Fix:** add unreviewed A2-IR and H, and base futility on the maximum credible *differential* review increment for every route versus T. Otherwise prohibit whole-branch termination and always advance survivors to the small reviewed pilot.

5. **Major consistency repair — reconcile kill and precedence rules.**

   “Kill H-GRAPH if H fails to beat” contradicts precedence row 9, which correctly says an indeterminate H result means no kill ([kill rule](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:960), [row 9](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:993)). Also, §3.2 appears to require lower LCC even when text is superior, while the operative rule correctly requires cost advantage only for equivalence.

   **Fix:** distinguish “advance,” “kill,” and “indeterminate”: kill only under a declared equivalence/inferiority or futility zone; lack of superiority merely blocks advancement. Change the text rule everywhere to “text superior, or equivalent with lower LCC.”

6. **Minor but necessary before freeze — remove stale normative rows and references.**

   The live prereg summary still says six endorsement conditions, H-vs-A2, omits A2-IR from arm completeness, retains the one-human floor, and says Rung 0 can kill the branch ([§8](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1135), [R2l](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1241)). These conflict with Rev3 even though the historical revision narrative is properly labelled historical.

   **Fix:** publish one consolidated Rev3-controlling prereg table and mark older rows superseded or amend them in place. Also correct the renderer-family cross-reference and use one canonical term for “decision/provenance hash” versus “evidence-release hash.”

## Strengths

- The A2-IR repair directly addresses the largest Rev2 control confound and preserves honest upper-bound scope.
- The T-source/T-format split is conceptually right; T′ can no longer manufacture a deflation result.
- The three-valued packet-relative target is a strong, formal repair of the abstention contradiction.
- The independence architecture is unusually careful about anchoring, source selection, correlated models, and human authority.
- The power/no-margin-widening rule, text-indeterminate adoption block, cost robustness, shuffles, human baseline, retained failures, and explicit extrapolation caps are all conservative and methodologically valuable.

**Bottom line:** adopt the governance architecture for a bounded pilot, but perform one focused Rev4 before preregistering or adopting the constructed store, graph route, or KBUILD-0 decision protocol.
