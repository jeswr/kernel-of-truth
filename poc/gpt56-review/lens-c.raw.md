## Bottom line

The programme is falsifiable, but the present positive evidence supports a narrower object than the stated thesis: an aligned deterministic content oracle plus retry. It does not yet establish that NSM primes, Construction-B vectors, or content addressing cause the benefit. The highest-leverage next experiment is therefore an ablation of the claimed invention, not another benchmark run.

The strongest reframing is:

> Treat the kernel as a selective semantic compiler: it converts some claims into versioned, proof-carrying objects; it refuses the rest.

This is more defensible than either “better embeddings” or “hallucination-free output.” Its primary outcome should be risk versus coverage versus cost, with authoring cost included.

All experiments below are proposals, not evidence. Costs are rough direct spend excluding existing infrastructure, with person-time shown separately.

## Ranked proposals by information per dollar

| Rank | Experiment | Hypothesis | Cheapest decisive design | What it would decisively show | Rough cost |
|---:|---|---|---|---|---|
| 1 | **K-NULL: vector-free kernel ablation** | The observed verifier benefit requires the NSM/vector construction, rather than merely an aligned canonical answer table. | Re-score or rerun a small f2b-style cell with: current kernel; canonical AST/record-ID verifier with all vectors removed; normalized-text exact verifier; random opaque IDs preserving record alignment; shuffled alignment. Same retry topology and FLOPs. | If AST, text, or opaque-ID arms match the kernel, f2b supports a deterministic oracle—not NSM vectors. If only the true vector/NSM representation survives, the vector thesis receives its first causal support. | **$0–250; 1–2 days** |
| 2 | **ORACLE-FALL: pipeline ceiling decomposition** | Translation/mapping, not deterministic checking, is the binding correctness bottleneck. | On 200–300 natural outputs, cross predicted versus gold claim segmentation, record linking, query parse, and axioms in a factorial oracle ladder. Report conditional accuracy and losses at each boundary. | Identifies whether the next dollar belongs in records, mapper grammar, parsing, axioms, or model scale. It can also kill e9-full economically if the measured parser ceiling lies below its PASS threshold. | **$50–300; 2–3 days** |
| 3 | **COVERAGE-LOTTERY: randomized coverage expansion** | Kernel-checkable items are not merely an outcome-selected easy niche, and spending authoring effort on a random item yields measurable end-task value. | Draw a benchmark sample before viewing model outputs. Randomize items to “fixed-budget coverage attempt” or waitlist. Authors/mappers are blind to baseline model success. Cap effort per item. Measure successful checkability, augmentation lift, and lift per author-hour by intent to treat. | Directly measures the causal value and cost of growing coverage without cherry-picking items the kernel can help. A null says targeted covered-slice results cannot justify a general benchmark story. | **$500–2,000; 5–10 days** |
| 4 | **MUTATE-1: semantic minimal-pair linter challenge** | The structured checker catches localized semantic defects that text checkers systematically miss. | Start from externally sourced true claims. Apply exactly one gold-labelled mutation: negation, quantifier, argument swap, entity substitution, modality, temporal qualifier, scope attachment, or vacuity insertion. Include meaning-preserving paraphrase twins. Compare kernel linter, gloss self-check, RAG/NLI checker, and a strong general LLM judge. | Cleanly distinguishes semantic sensitivity from topic, style, and fluency cues; gives per-error-class sensitivity and false-positive rates. | **$300–1,000; 4–7 days** |
| 5 | **SURFACE-X: answer-surface invariance** | f2b-transfer lift survives removal of kernel-shaped option and prose cues. | For the same externally adjudicated meanings, create four independently rendered surfaces: ordinary prose, non-NSM controlled English, randomized option order with matched distractors, and open response scored by blind humans. Freeze semantic equivalence before inference. | If lift collapses only on non-kernel surfaces, the mechanism is interface/style compatibility rather than ground-truth transfer. If it persists, it materially strengthens f2b-transfer. | **$500–1,500; 5–8 days** |
| 6 | **TIMEPACK: counterfactual versioned worlds** | Content addressing provides useful correctness under changing or mutually inconsistent knowledge states, where model weights are an inappropriate authority. | Construct 100–200 queries against two valid, incompatible versioned packs—e.g. policy v1/v2, fictional worlds, or software APIs before/after a breaking change. Compare kernel router, oracle-text RAG, citations+retry, and model alone. Swap versions within session. | Shows whether hashes/version pins prevent temporal cross-contamination and stale-answer fabrication better than strong text retrieval. This is a more native test of content addressing than static QA. | **$500–2,000; 4–8 days** |
| 7 | **POG: proof-obligation generation** | Requiring claim-level proof obligations reduces unsupported covered claims without destroying useful output. | Constrain the model to emit `{claim, record_hash, axiom_ids, query, status}`; the engine accepts or rejects, then a deterministic renderer produces prose. Compare ordinary RAG with citations, gloss self-verify, post-hoc linting, and proof-obligation generation at matched compute. | Establishes whether prevention during generation beats post-hoc detection. It also separates syntactic validity, grounding validity, and source truth. | **$500–2,000; 5–10 days** |
| 8 | **RISK-CURVE: selective utility trial** | The linter improves factual risk at a practically tolerable answer/claim coverage and editing burden. | Evaluate flag, quarantine, and rewrite modes across thresholds. Primary endpoint: area under the selective-risk curve or error at fixed useful-claim coverage. Secondary: over-refusal, correct-claim deletion, latency, length, and human time-to-correct. Include no guardrail, RAG citations, LLM/NLI guardrail, and gloss self-check. | Determines whether the linter is a deployable selective system rather than a high-precision detector that rejects or deletes most useful content. | **$1,500–5,000; 1–2 weeks** |
| 9 | **LB-1P: prospective public-benchmark intervention** | Kernel augmentation produces value on naturally arising, prospectively checkable public items at matched cost. | Run only after b-cov and preferably COVERAGE-LOTTERY. Freeze checkability before model responses; use a fresh or temporally updated benchmark; compare model-alone, kernel, active gloss-text, oracle-text RAG, and shuffled alignment. Include a non-checkable placebo stratum. | Provides an externally styled treatment effect. It does not establish general LLM ability, but can establish augmentation value and quantify its blended impact. | **$2,000–8,000; GPU-dependent** |

Ranks 1–5 should precede more ingestion or frontier scaling. If K-NULL is null and ORACLE-FALL identifies mapping as the ceiling, much of the architecture ladder should be reframed around symbolic records and parsing rather than vectors.

## Direction (i): leaderboard benchmarks

### Critique

The proposed b-cov → LB-1 sequence is directionally correct, especially the separation of `κ_B^verify` and `κ_B^engine`. But “evaluate against LLM leaderboards” remains the wrong scientific frame.

First, a checkable-slice score is endogenous. Even if the slice is declared honestly, it may select definitional, lexically obvious, or unusually easy questions. Conditioning on checkability can therefore manufacture a favorable treatment population without deliberate misconduct.

Second, the classic suite is poorly aligned with the mechanism:

- GSM8K/MATH test multi-step mathematical execution, not lexical grounding.
- HellaSwag/WinoGrande emphasize continuation and contextual discrimination.
- MMLU aggregates heterogeneous subjects into a number with little mechanistic meaning.
- Multiple-choice surfaces permit option-structure and elimination effects unlike open generation.
- Static public benchmarks carry contamination and saturation risk. Fresh, objectively scored benchmarks are preferable where available; LiveBench is a relevant model for temporal refresh and objective grading. **Confidence: high.** [LiveBench paper](https://arxiv.org/abs/2406.19314)

Third, running many benchmark×mode cells creates a garden of forking paths. A favorable “definitional MMLU” result should not be allowed to become “leaderboard improvement.”

### Extension

Rename N1-LB from a leaderboard evaluation to a **prospective augmentation treatment study**. Pre-register four outputs:

1. `κ_B`: proportion successfully checkable under a fixed authoring/mapping budget.
2. `Δ_checkable`: treatment effect on the prospectively checkable slice.
3. `Δ_ITT`: intent-to-treat effect across all randomly sampled items, with unchanged items scored unchanged.
4. Marginal utility per author-hour and per inference dollar.

Add three controls missing from the current description:

- A matched non-checkable placebo stratum, to detect generic retry/prompt effects.
- A difficulty/representativeness audit comparing baseline accuracy, answer entropy, domain, length, and error classes across checkable and non-checkable items.
- Checkability authors blinded to baseline model answers and errors.

Do not publish a new composite “kernel leaderboard.” Publish an intervention curve: gain as a function of coverage and authoring budget.

## Direction (ii): linter/guardrail

### Critique

The five-way lattice is strong, particularly `ungrounded ≠ false`. The term **hallucination-free**, however, should be retired except for an explicitly closed contract.

A deterministic rewrite can guarantee only something like:

> Every emitted factual claim that was successfully parsed is licensed by the pinned kernel pack and renderer.

It cannot guarantee that:

- the parser recovered the intended claim;
- the authored axiom is true or current;
- the pack contains the relevant exception;
- omitted qualifiers preserve the speaker’s meaning;
- an ungrounded claim is false;
- a user will not over-trust a polished, mechanically certified answer.

Rewrite mode has a particularly important failure mode: it may improve measured precision by silently deleting nuance and useful ungrounded content. That is selective omission, not factual correction. Flag and quarantine are scientifically safer first products.

Grammar-constrained decoding guarantees grammatical membership, not semantic truth, and can distort the model’s conditional distribution; this is directly relevant to a record-constrained output head. **Confidence: high.** [Grammar-Aligned Decoding](https://arxiv.org/abs/2405.21047)

### Extension

Reframe the linter as two products:

- **Semantic static analyzer:** classifies propositions and reports proof obligations.
- **Strict certified channel:** emits only engine-licensed claims under a named, versioned contract.

The first should be evaluated with MUTATE-1 and natural-error corpora. The second should be evaluated with POG and RISK-CURVE. Its primary metric must combine error and coverage; precision alone rewards abstain-all and deletion.

Use claim-level factuality systems as explicit baselines:

- FActScore supplies the atomic-fact decomposition comparison. **Confidence: high.** [FActScore](https://arxiv.org/abs/2305.14251)
- SAFE supplies a strong search-augmented checking baseline. **Confidence: high.** [SAFE/LongFact](https://arxiv.org/abs/2403.18802)
- VERISCORE is especially relevant because it distinguishes verifiable from unverifiable claims, closely paralleling the proposed lattice. **Confidence: high.** [VERISCORE](https://arxiv.org/abs/2406.19276)
- FACTOR provides a corpus-to-controlled-factuality benchmark method that could generate non-kernel-authored challenge sets. **Confidence: high.** [FACTOR](https://aclanthology.org/2024.eacl-long.4/)
- BUMP and RobustLR motivate minimal-pair evaluation rather than relying only on naturally generated error mixtures. **Confidence: high.** [BUMP](https://aclanthology.org/2023.acl-long.716/), [RobustLR](https://aclanthology.org/2022.emnlp-main.653/)
- Selective classification and conformal abstention provide the right risk–coverage vocabulary, although any guarantee is distribution-specific. **Confidence: high.** [Selective classification](https://arxiv.org/abs/1705.08500), [conformal abstention for LLMs](https://arxiv.org/abs/2405.01563)

## Higher-leverage programme bets

Three portfolio-level reframings follow from the experiments above.

1. **Unbundle the object.** Track independent hypotheses for semantic primes, reductive explications, vectors, canonical ASTs, content hashes, authored axioms, and refusal semantics. At present, a pass by one component can rhetorically spill onto the whole bundle.

2. **Optimize marginal coverage value, not raw coverage.** The objective should be expected corrected errors per author-hour, not lemma-touch or even `κ_B`. A rare but high-error/high-consequence relation can be more valuable than thousands of easy definitions.

3. **Make versioned contradiction the flagship correctness use case.** Static world knowledge invites comparison with ever-stronger RAG. Versioned policies, APIs, contracts, scientific taxonomies, and fictional worlds are where deterministic refusal and content addressing offer a genuinely different capability.

## Honesty-rail warnings on these proposals

- MUTATE-1 can overstate natural-world performance because synthetic single errors are cleaner than model errors. It must be paired with a frozen natural-error secondary.
- COVERAGE-LOTTERY estimates value under its sampled benchmark and effort cap only; it licenses no global coverage-growth slope.
- SURFACE-X cannot prove complete absence of style leakage; it can only reject specified surface-cue explanations.
- POG proves derivability from a pack, not that the pack is true.
- TIMEPACK measures version obedience in constructed or bounded domains, not open-world factuality.
- Risk–coverage or conformal claims do not transfer across domains or distribution shift without recalibration.
- A public-benchmark PASS must not be described as a leaderboard capability gain unless the blended all-item score itself improves under the frozen intent-to-treat analysis.

The sharpest near-term decision sequence is: **K-NULL → ORACLE-FALL → COVERAGE-LOTTERY → MUTATE-1/SURFACE-X**. Together, these would determine what the kernel’s active ingredient is, where its ceiling lies, whether its covered slice is defensible, and whether the linter detects semantics rather than its own surface conventions.
