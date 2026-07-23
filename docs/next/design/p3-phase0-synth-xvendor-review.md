# Cross-vendor review (GPT-5.6 `gpt-5.6-sol`, xhigh) — Programme-3 Phase-0 synthesis

> Independent cross-vendor review of `p3-phase0-synthesis.md` (pre-Rev2). Verdict NEEDS-REVISION;
> all findings applied in Rev2 (see the synthesis doc's Revision-2 section). Committed for the record.
> Runner: poc/gpt56-review/run-review.sh (npx-pinned codex 0.144.1, isolated home; global codex untouched).

---

# Verdict: NEEDS-REVISION

The central directional read remains plausible: no qualifying matched-resource symbolic-reasoning win was located, and correctness/add-capability deserves first-class evaluation. But the document overstates the evidential breadth of that conclusion, under-bounds Memory Layers, and misclassifies grammar-constrained decoding. Those defects propagate into the “five concordant registers” steering argument.

## 1. Per-pathway ledger

- **FUSE — substantially faithful.** G-Retriever is correctly rejected as a qualifying topology-causal win. However, Deceive-KG concerns earlier systems and GTEval concerns related soft-token models; neither directly perturbs G-Retriever. Calling them two probes “against the structure channel” is stronger than the evidence.

  **Fix:** say they are two external warnings that make structure attribution unsafe, not two negative replications of G-Retriever.

- **RULE — materially over-bounded.** See §2 below. The shallow rule-injection verdict is sound, but Memory Layers cannot be reduced to a factual-only footnote.

  **Fix:** separate “no matched-resource shallow rule-injection win” from “a matched neural memory-architecture win exists but does not establish rule inference or frozen-host kernel value.”

- **NTP — basically faithful, but the final “No” rationale is too categorical.** Not every demonstrated win adds an exact capability: Polu is a within-executor allocation result; CTP adds structure with resource matching unestablished; Goedel/Pythagoras are sample-pinned parameter-efficiency comparisons. The common fact is that none establishes the requested comparison—not that every positive has one identical explanation.

  **Fix:** “No qualifying comparison established; candidates are add-capability, unmatched, or within-executor.”

- **PARSE — materially misstated.** Grammar-constrained decoding is not “compute-matched by construction”: it adds an incremental parser and CPU work; the paper reports negligible overhead for some tasks but material overhead for another. More importantly, the mechanism guarantees validity, but the observed outcomes include large improvements in task F1 and accuracy—not merely validity. The source reports, for example, better entity-disambiguation accuracy and constituency-parsing F1 alongside validity. [The primary paper](https://arxiv.org/html/2305.13971) supports that distinction.

  It still does not clearly clear the full bar: the grammar/candidate set supplies external task structure, and total compute/information parity was not audited.

  **Fix:** classify GCD as a strong same-host, near-compute-matched, add-structure candidate whose full matched-information/resource status is unestablished—not as a matched win that can be dismissed because its benefit is “validity only.”

- **RAG — honest within the row, wrongly called concordant afterward.** The review explicitly says the fair comparison has never been run in either direction. That is non-identification, not corroborating negative evidence.

  **Fix:** label RAG **OPEN / UNESTABLISHED BOTH DIRECTIONS**, never a fifth concordant register.

- **SURG — incomplete ledger.** The row omits the pathway’s most relevant store-backed candidate: LmLm-382M approximately matching LLaMA2-7B on factual-precision benchmarks ([SURG review](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-surg.md:72)). Its database bytes, training data, and total compute are not matched, so it is not a qualifying win—but it must be surfaced. Minitron is also a real iso-compute result, though not information- or total-lifecycle-matched.

  **Fix:** replace “no win claim” with “strong candidates exist; none has the required complete ledger.”

- **EVAL — correctly N/A**, but “proxy rungs kill reliably” is too broad. The underlying EVAL/TINY reconciliation permits strong kills from mechanism/coverage failures or replicated directional evidence; TINY explicitly warns that a single small-scale null can reverse.

  **Fix:** state those conditions.

- **TINY — otherwise faithful and non-probative on the crux.**
- **STORE — faithful: matched TCO is genuinely open in both directions.**
- **SYS — faithful and non-probative: it supplies instrumentation, not architecture evidence.**

## 2. Memory Layers: the bounded exception is bounded too tightly

The document is right that Memory Layers:

- are trained end-to-end from pretraining;
- are not a bolt-on frozen-host symbolic store;
- do not demonstrate rule inference, formal soundness, or kernel semantics;
- add parameters relative to the dense comparator.

But “params-up” does not defeat the MoE comparison: total parameters are matched there. More importantly, “factual recall, not reasoning” overstates the source. Factual gains are strongest, but the paper also reports improvements on multi-hop QA, coding, MMLU and other general benchmarks, with some mixed cells. [Memory Layers at Scale](https://arxiv.org/html/2412.09764) presents it as a compute-controlled architecture result against roughly parameter-matched MoE baselines.

Therefore it does break the broadest formulation—“no matched-resource architecture win located”—more than admitted. It does **not** break the narrower and programme-relevant claim:

> No matched-resource win was located for symbolic rule inference, exact reasoning, topology-causal fusion, or a training-free frozen-host store.

**Fix:** make that narrower claim the crux. Describe Memory Layers as a genuine learned-memory architecture efficiency precedent whose transfer to kernel-style reasoning remains unestablished. Also disclose that deployment bytes, bandwidth, optimizer state and lifecycle costs are outside the paper’s compute-and-parameter match.

## 3. Cross-pathway verdict

“FUSE holds across all ten” is not warranted. The correct evidence topology is:

- four pathway-specific audits found no qualifying win in purposive sweeps;
- RAG found that the relevant calculation has not been performed;
- SURG supplies deflation and unmatched candidates;
- EVAL, TINY, STORE and SYS do not test the existence claim.

“Zero counterexamples” in non-audit reviews cannot convert them into confirming observations. Nor are the four audits independent replications in the statistical sense: they cover different literatures, but share the audit frame, review pipeline, and prior-draft lineage.

**Fix:** replace the headline with:

> The four audit-bearing pathway sweeps reproduce the bounded FUSE result; none of the other six reviews establishes a contradiction, but they do not independently confirm it. RAG and STORE remain unestablished in both directions.

That still moves priors modestly. It does not justify “five concordant registers.”

## 4. Steering implication

The correctness/add-capability re-weight is defensible as a labelled portfolio judgement, particularly because the literature’s clearest positives involve executors, checkers, or hard interfaces. The document also correctly preserves:

- intact, falsifiable W1;
- the kernel-as-text and matched-generic-store nulls;
- the 0–0 four-condition scoreboard;
- the boundary between generic executor value and kernel-specific semantics.

However, three phrases overreach:

- “the literature-supported home of the kernel’s value” should be “the most defensible place to test for value”;
- “the deciding instruments” overstates F1-K while carrier validity is unresolved, any result is proxy-provisional, and no licensed negative rule exists;
- “supports HOLD” and “correct next spend” are operational recommendations derived from the extrapolative weighting, despite the repeated claim that extrapolations are premises of nothing.

**Fix:** call F1-K and gsx0 the most relevant currently frozen probes, conditional on their stated validity and asymmetric-licensing limitations. Mark HOLD and sequencing explicitly as `[EXTRAPOLATION / DECISION INPUT]`, not as literature-backed consequences.

## 5. Maintainer decision: my ranking

My ranking as the options are currently defined is:

1. **(a) Co-equal claim family**
2. **(b) Conjunctive W1 gate**
3. **(c) Pareto axis with no frozen claim rule**

Option (a) is sound because correctness and efficiency answer different scientific questions. It preserves W1 while allowing correctness to be adjudicated rather than hidden behind an efficiency failure. To resist gaming, it needs a frozen endpoint hierarchy, coverage floor, unconditional dangerous-wrong bound, multiplicity control, and explicit reporting language distinguishing “correctness-only success” from “W1 success.”

Option (b) is the most conservative single headline and resists declaring overall success from a narrow correctness gain. But it changes the estimand to “correctness **and** efficiency jointly” and can suppress a real correctness finding. It is appropriate only if the programme’s normative utility requires both simultaneously.

Option (c), as written, is not especially gaming-resistant. A Pareto surface without a frozen dominance/reference rule invites narrative selection after results are known. If it acquired a frozen reference point and decision rule, it could rival (a), but it would no longer be option (c) as defined.

## 6. Epistemic hygiene

Several corrections are needed:

- `[EXTRAPOLATION]` is used as a premise for the recommendation, HOLD, and sequencing. The claim that it is “a premise of nothing” is false in ordinary reasoning terms. It is only not a premise of a **mechanical verdict**.
- RAG’s extrapolative absence finding is promoted into “five concordant registers.”
- PARSE’s “compute-matched” classification is tagged too strongly despite added CPU work and unpriced grammar information.
- “Backfill proven only for facts, never computation” should be “the located evidence concerns facts; no computation-restoration result was located.”
- The provenance statement that every finding was primary-source verified is broader than the review tables, which include prior-verified, secondary, memory, claimed, and unverified entries.

**Fix:** distinguish source facts from cross-paper audit judgements sentence by sentence, and replace blanket verification language with “verification status inherited exactly from the owning review.”

## Single most important correction

Remove the claim that the finding is confirmed across all ten or five concordant registers. State that it is reproduced by **four bounded audits**, while the other six are non-contradictory but mostly non-probative or explicitly open. Everything downstream—strength of the steering re-weight, the Memory Layers boundary, and the #57 recommendation—should be recalibrated to that evidence structure.