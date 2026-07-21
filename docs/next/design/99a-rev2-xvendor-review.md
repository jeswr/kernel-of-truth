# 99a Rev2 — Cross-Vendor GPT-5.6 Review (the prescribed sign-off gate)

**Reviewer:** GPT-5.6 (`gpt-5.6-sol`, reasoning effort `xhigh`), via `poc/gpt56-review/run-review.sh` (isolated `CODEX_HOME`, npx-pinned codex `0.144.1`).
**Date:** 2026-07-21. **Brief:** neutral methodology-soundness framing (scratchpad `xv-99a-brief.md`). **Raw output:** `poc/gpt56-review/99a-xvendor-signoff/` (`events.jsonl` + `last-message.json`).
**Target:** `kernel-construction-methodology-proposal-99a.md` (Rev2, `751559aa`), with the Rev1 critique + both source-verify reports in context.

**Role note (mechanical):** this file transcribes the reviewer's verbatim output; the verdict and findings are the reviewer's, not the coordinator's. This is the **cross-vendor gate**; the earlier same-vendor Fable loop (Rev1 → critique → Rev2 → [SV]) did NOT substitute for it. The gate did its job: it surfaced **3 CRITICAL** estimand/control problems the same-vendor loop cleared past. Citations were independently re-confirmed (no citation error blocks adoption). **Disposition:** routes to a 99a **Rev3** (Fable) addressing the CRITICAL + MAJOR findings before any adoption of the constructed substrate / graph route / KBUILD-0 protocol; the verified-proposer **governance architecture** is provisionally adoptable for a pilot per the reviewer.

---

## Verbatim GPT-5.6 review output

## Overall verdict

**Conditionally sound, but not ready for wholesale adoption or preregistration freeze.**

The proposal is sound enough to adopt the **verified-proposer governance architecture** for a pilot: the model drafts, independent evidence and a human/authority floor govern promotion, and canonicality is explicitly separated from evidence adequacy and empirical truth. That architecture avoids making the generator its own source of truth.

It is **not yet sound enough to adopt the constructed-record store, graph route, or KBUILD-0 decision protocol**. Three critical estimand/control problems and several statistical specifications need repair first.

| Area | Assessment |
|---|---|
| Model-generated NSM-style records | Sound as a proposer/compiler, not as authority; conditionally adoptable |
| H-GRAPH framing | Correctly falsifiable and appropriately scoped, but its current implementation is confounded |
| Statistical/adoption plan | Strong safeguards, but not freeze-ready |

## Prioritized issues

1. **Critical — H versus A2 does not cleanly isolate the graph.**

   On nonce concepts, H receives a graph constructed from the shared typed IR, while ordinary constructors receive rendered descriptions. That gives H an oracle-quality parse/normalization channel in addition to a graph ([arms B/H](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:523), [packet construction](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:478)). The round-trip gate proves semantic preservation, but it does not equalize parsing burden. An H win could therefore mean “lossless machine-readable input helps,” not “graph topology or closure helps.”

   **Fix:** Either derive both A2 and H inputs through the same realistic text-to-IR extraction pipeline, or add an `A2-IR` control receiving the same atoms and relations in a flat, non-graph form. Keep the current oracle-IR graph only as an explicitly labelled upper-bound mechanism test. Match raw evidence, prompt, token/compute budget, and reviewer visibility.

2. **Critical — the dominant text-deflation comparison lacks a common estimand.**

   Stage 1 supposedly scores typed records, but T is raw source text, while T′ is a deterministic rendering of the *same endorsed record* as the constructed winner ([arm definitions](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:549), [Stage-1 endpoint](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:565)). Consequently:

   - T has no specified denotation for the deterministic typed-record scorer.
   - T′ fidelity equivalence is largely true by construction.
   - T′ does not test whether construction can be avoided: it depends on the winning record having already been constructed and endorsed.

   **Fix:** Split the hypothesis:

   - `T-format`: same semantic record rendered as prose versus AST/vector; evaluate only downstream comprehension, format, and consumer cost.
   - `T-source`: an independently governed plain-text store that avoids structured-record construction; compare it on an independent claim task and evidence-adequacy review.

   Charge T′ all shared upstream construction/review costs. Do not use a T′ Stage-1 fidelity TOST as evidence that plain text replaces construction.

3. **Critical — exact hidden-rule equivalence conflicts with correct abstention.**

   The adversarial subset deliberately includes insufficient evidence, where correct behavior is packet-relative abstention ([packets](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:498)). Yet the primary endpoint requires the record extension to equal the concealed full-rule extension, while also rewarding abstention ([endpoint](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:584)). A method cannot both refrain from guessing and exactly reproduce a rule that the packet underdetermines.

   **Fix:** Define a formal three-valued, packet-relative target: consequences true under every rule consistent with the packet, false under every consistent rule, and otherwise unknown. Use exact hidden-rule equivalence only for fully identifying packets. Report supported-content fidelity and abstention calibration separately for underdetermined packets.

4. **Major — the text decision rule needs more than TOST.**

   TOST can establish equivalence; failure of TOST does not establish non-equivalence or that construction is superior. The matrix does not fully distinguish text superior, constructed superior, equivalent, and genuinely indeterminate outcomes ([matrix](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:761)).

   **Fix:** Predefine a three/four-zone CI rule for constructed-minus-text fidelity:

   - CI wholly inside ±m: equivalent.
   - Lower bound above the superiority threshold: constructed superior.
   - Upper bound below the negative threshold: text superior.
   - Otherwise: indeterminate and adoption blocked.

   Also replace “T and/or T′” with an ordered testing family and define alpha allocation across H-GRAPH, H-TEXT, shuffle, and human-baseline confirmatory claims. Holm correction only for secondaries does not resolve the multiple primary/dominant claims.

5. **Major — the power requirement is good, but the analysis does not yet support it.**

   Requiring ≥90% power for every TOST and blocking adoption after an inconclusive dominant test are excellent safeguards. But they are planning requirements, not evidence that 96 or 160 concepts are adequate. Moreover, the analysis resamples concepts only, while the claimed estimand includes author seeds, model snapshots, renderers, and reviewers ([statistics](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:606)).

   **Fix:**

   - Analyze the crossed hierarchy—concept, author seed/snapshot, renderer, and reviewer—or explicitly average over fixed levels and narrow the claim.
   - Simulate power using the exact final analysis model, including the sequential boundary and winner hierarchy.
   - State equivalence power at a specified true effect, normally zero, and assess joint power for the adoption path.
   - Do not widen an equivalence margin merely because the sample cap makes power unreachable. The margin must come from substantive interchangeability; infeasibility should change sample/design or terminate the experiment.

6. **Major — both composites remain decision-sensitive but undefined.**

   Fidelity weighting and LCC weighting are deferred ([deferral list](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1114)). A weighted fidelity score can let one kind of error compensate for a fatal unsupported assertion. LCC can reverse decisions depending on exchange rates among human minutes, tokens, FLOPs, bytes, and one revision-cycle proxy.

   **Fix:** Make logical fidelity or packet-relative exactness non-compensatory, with minimum gates on unsupported, contradicted, omitted, and abstained content. If retaining a composite, freeze externally justified weights before outcome calibration and report component sensitivity. For LCC, convert resources using declared prices/shadow prices, allocate shared costs consistently, use uncertainty bounds on cost differences, and report robustness across plausible weights. Call the maintenance term “one-revision-cycle cost,” not evidence of full lifecycle cost.

7. **Major — the production independence gate needs protection against anchoring and source-selection bias.**

   The human/authority floor closes the model-only circularity loophole ([endorsement conditions](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:193)). Nevertheless, one human plus many correlated models is an anti-circularity minimum, not strong reliability. Reviewers also see the candidate, so proposal anchoring remains possible; “assembler is not the drafter family” does not fully specify human/operator independence.

   **Fix:** For ordinary lexical or empirical records, require at least two independently sampled qualified humans or a declared authoritative body; have reviewers make evidence-only clause judgments before seeing the candidate; prohibit drafter-assisted source selection; and use a pinned source sampling frame or dual independent packet assembly on an audit sample. Clarify that KBUILD uses human-only endorsement even though production permits non-sufficient model endorsements.

8. **Major — Rung 0 cannot validly kill the reviewed methodology from unreviewed arms alone.**

   Rung 0 can kill the branch based on unreviewed A2/B/T results ([Rung 0](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:840)), even though H-REVIEW explicitly hypothesizes that review changes fidelity. That extrapolates unreviewed futility to the reviewed route.

   **Fix:** Let Rung 0 kill only unreviewed routes, or require a conservative conditional-futility calculation allowing the maximum credible review increment from an independent pilot. Otherwise advance to a small reviewed pilot rather than terminating the branch.

9. **Minor — canonical selection identity conflicts with the two-hash design.**

   The proposal says changing *any* selection input changes selection identity ([canonicality test](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:147)), but elsewhere correctly separates semantic identity from evidence-release identity. A new source or endorsement can leave normative content unchanged.

   **Fix:** Require every input change to alter a decision/provenance hash; alter semantic identity only when the selected normative content changes.

## Source and extrapolation assessment

The repository and external-literature reports support the cited claims: both load-bearing repository citations were confirmed ([repo SV](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/99a-rev2-sv-report.md:12)), and all four supporting literature claims cleared verification ([external SV](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/99a-rev2-sv-report-extlit.md:17)). No citation error blocks adoption.

The K-NULL-to-construction bridge is now honestly tagged as extrapolation and is not used as a gate. Remaining extrapolation risks are instead:

- treating oracle-IR graph performance as production graph-import performance;
- letting unreviewed Rung-0 results terminate a reviewed route;
- treating one revision cycle as lifecycle evidence;
- extending nonce compilation results to natural concepts or dictionary-scale convergence.

The proposal already caps the last item reasonably; those caps must remain binding.

## Strengths

- Excellent separation of canonicality, evidence adequacy, and empirical grounding.
- The deterministic vector is correctly treated as derived encoding, never semantic authority.
- Human/authority promotion floor, explicit conflicts, forks, abstention, and bound production roles substantially reduce circularity.
- A2 is the right conceptual citation-only ablation.
- Graph import is properly demoted from recommendation to falsifiable, sector-scoped hypothesis.
- Strong instrumentation: shuffled and no-context controls, human baseline, leakage checks, round-trip validation, failures retained in denominators, and independent evaluation.
- The ≥90%-per-TOST requirement and adoption block after inconclusive text evidence are unusually conservative and directionally correct.
- Evidence presentation is two-sided, with K-NULL limitations and RULES-2’s claim cap carried explicitly.

In short: **adopt the governance architecture provisionally; repair and preregister the experiment before adopting any constructed substrate or graph route.**
