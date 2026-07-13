# knull-v2 (NULL / PASS-GENERIC) — interpretation

> **Provenance (coordinator, 2026-07-13).** The mechanical verdict is established separately:
> the pinned SAP (`analysis/knull_v3.py`, sha `54528cd4…`) on the complete 36-cell campaign gives
> `tost_equivalent=True`, superior/inferior `False`, all instrument gates `True` → by the frozen
> `verdict_rules` (rule 2) the verdict is **NULL** (carried as PASS-GENERIC, equal prominence to a
> PASS). Formal chain-verified registration (`results-log/knull-v2.jsonl` → `verdict-gen` →
> `registry/verdicts/knull-v2.json`) is a separate mechanical step.
>
> The interpretation below was authored by **GPT-5.6 (xhigh)** standing in for Fable (capped) per the
> standing overflow directive. It is **PROVISIONAL-ON-LLM-PROXY**: to be reconciled against an
> independent **Fable** read when Fable capacity returns (dual-model analysis); material divergence
> triggers a re-do. The coordinator does NOT author the feasibility conclusion — this is evidence
> weight on a single pre-registered result. Claims are tagged MEASURED / PRE-SPECIFIED (by the frozen
> design) / INTERPRETATION.

---

## 1. Plain-English meaning

[MEASURED] knull-v2 established equivalence within the pre-registered 0.05 SEOI: the kernel and the best aligned non-kernel store produced lifts close enough that both TOST bounds fell inside the equivalence margin.

[MEASURED] This is an informative equivalence result, not a failure to detect an effect. At matched FLOPs, kernel minus plain-padded was −0.0043 with a confidence interval spanning zero; against unmatched plain, kernel was slightly worse, at −0.0080 with CI [−0.0143, −0.0020].

[MEASURED] The result cannot be dismissed as a broken experiment: all instrument gates passed, including mechanism reproduction, eligible difficulty bands, FLOP parity, and the length guard. Verify-retry cells also improved over the model-alone baselines.

[PRE-SPECIFIED] Therefore the kernel-content attribution dies at this scope. The licensed forward description is: **the f2b lift is a generic aligned-deterministic-answer-key + retry effect at no greater, and possibly smaller, token budget than the kernel store.**

[INTERPRETATION] What was not shown is that grounded kernel content or kernel-specific organization adds incremental value over a plain-dictionary answer store under the tested conditions. What was shown is that a small host can benefit from aligned verification and retry, while the specialized kernel does not deserve distinctive credit for that benefit here.

[PRE-SPECIFIED] This conclusion applies only to hosts up to 1.7B, these self-authored templated definitional questions over 108 concepts, k=4, the frozen normalization and acceptance machinery, and the 0.3542 kernel-expressibility slice. It says nothing about externally authored items, non-templated phrasings, larger hosts, broader coverage, or gold-label independence.

## 2. Implications for the theses

[INTERPRETATION] For the **CORRECTNESS thesis**, this is a material dent to the narrow attribution that grounded kernel content adds checkable value on this definitional-QA line. The kernel works as a verifier store, but an aligned plain-dictionary store works equivalently; thus the evidence supports checkable answer-key alignment, not kernel-specific correctness value.

[PRE-SPECIFIED] Every arm retained an oracle-favourable construction: the verifier compared answers with the same canonical record used to define the gold answer, inflating the measured lift.

[INTERPRETATION] That caveat does not undo the randomized arm comparison, because it was held fixed across arms. It does limit how much either the kernel or generic verify-retry lift can support the broader correctness thesis outside this evaluation construction.

[INTERPRETATION] For the **EFFICIENCY thesis**, the NULL preserves some evidence weight for small-model verifier offload: verify-retry lifts occurred, including on the 135M host. It weakens the kernel-specific compression claim, however, because the specialized store delivered no matched-compute advantage over the plain-padded control and did not beat the shorter plain store.

[INTERPRETATION] The remaining efficiency question is consequently economic rather than architectural: whether a generic aligned store plus retry yields useful total-system savings after authoring, maintenance, inference, and failure-handling costs are counted. knull-v2 did not measure that full cost function.

## 3. Composition with prior results

[MEASURED] f2b-replicate showed that the verify-retry lift is real on the original surfaces, while knull-v2's bridge gate reproduced that mechanism on regenerated surfaces.

[PRE-SPECIFIED] knull-v2 now assigns that lift, within scope, to the generic aligned-deterministic-answer-key + retry mechanism rather than to kernel content.

[INTERPRETATION] RULES-2 remains evidence that kernel content can help on the rules line. Together, the results corroborate the narrower pattern: **content can matter, but kernel-specific structure remains unshown**. knull-v2 makes that qualification stronger on definitional QA.

[INTERPRETATION] The concern that kernel and knull artifacts may be behaviourally near-identical complicates mechanism interpretation, but it does not rescue the frozen attribution claim after equivalence passed. Instead, it motivates tests where the artifacts make genuinely different predictions or transfer differently.

## 4. Recommended next move

[INTERPRETATION] The single highest-value follow-up is **f2b-transfer**, designed to break the shared-gold construction and test whether verify-retry value survives gold-label independence. This directly addresses the largest pre-specified limitation and can distinguish transferable checking from evaluation-key alignment.

[PRE-SPECIFIED] In parallel, F2-line investment should reroute toward authoring-cost economics, comparing the total cost of producing and maintaining kernel versus generic aligned stores.

[INTERPRETATION] Do not claim that kernel methods are generally useless, that grounded content never helps, or that small-model verifier offload is established outside this envelope. The warranted update is narrower: PASS-GENERIC receives equal prominence, and evidence weight shifts away from kernel-specific attribution toward generic verification, transfer, and end-to-end economics.
