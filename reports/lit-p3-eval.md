# Lit review — P3-LR-EVAL: evaluation + AI-index methodology

**Bead:** P3-LR-EVAL (Programme-3, Phase-0 [LIT]).
**Author role:** literature-researcher (source-verification).
**Date:** 2026-07-19.
**Feeds:** the KOT-FAIR/2 measurement-framework freeze via **P3-D-INDEX** (co-input with
P3-MF-0), plus **P3-D-SEAL**, **P3-D-POWER**, **P3-D-BASE** (opening questions in §8).
**Status:** DRAFT for the review gate (GPT-5.6) + Fable critique. Not a freeze; takes no
design decision and stipulates nothing. Do **not** commit/push — coordinator review pending.

## 0. How to read this report — epistemic conventions

Every finding carries a tag: **[established]** (well-supported by a verifiable primary
source), **[claimed]** (asserted by a source but single-source / not independently
corroborated here), **[speculative]** (my inference or extrapolation, flagged as such),
each with **[search]** or **[memory]** and the verification date (all this session,
2026-07-19). Load-bearing citations were fetched at source where reachable; each is graded
in the §9 verification table. Where a source could not be fetched directly, the claim is
marked **[UNVERIFIED-DIRECT]** and the corroboration path is named. Prior approaches that
failed are judged **capability-limited** (mitigable by better instrument/selection) vs
**fundamental** (a property of the method that cannot be engineered away). §7 surfaces the
strongest reason a scalar AI-index could be indefensible for this programme — the honest null.

Rung→size map used throughout (from the programme doc §4): **R-0** = 1–30M (TinyStories
data); **R-1** = ~135M (SmolLM2-135M anchor, the decisive cheap rung); **R-2** = ~360M;
**R-3** = 1.7B; the binding constraint is the budget vector B_k, params are orientation only.

Some benchmark canonical facts (source, size, licence, metric, SmolLM2 card scores) were
already verified at source on 2026-07-10 and live in `reports/lit-eval-benchmarks.md`; this
report cites that fact sheet as **[LIT-BACKED prior-session]** for those and does not
re-derive them — it is the methodology layer above it.

---

## 1. HELM: how a defensible multi-scenario / multi-metric index is actually built

**Finding 1.1 — HELM's core structure is a scenario × metric matrix, densely populated.**
[established][search 2026-07-19] HELM (Liang, Bommasani, Lee et al., "Holistic Evaluation of
Language Models", arXiv:2211.09110, TMLR 2023) measures **7 metrics** (accuracy,
calibration, robustness, fairness, bias, toxicity, efficiency) across **16 core scenarios**
(populated 87.5% of the matrix), within a total of 42 scenarios; its headline contribution
is *standardisation* — density of the model×scenario matrix rose from ~17.9% to 96.0% by
running all models on the same core set under identical conditions. Verified via the CRFM
HELM pages and arXiv abstract.

**Finding 1.2 — HELM's ORIGINAL aggregation was "mean win rate"; HELM has since ABANDONED it
for mean-of-normalised-scores, and states exactly why.** [established][search 2026-07-19]
This is the single most load-bearing HELM finding for KOT-AI-INDEX/2, and it *updates* the
programme doc's "HELM-style" citation. Mean win rate = the probability a model beats a
uniformly-random other model in a head-to-head on a given metric, averaged over scenarios.
HELM **Capabilities** (CRFM, 2025-03-20) explicitly moves to **mean score**: "The models are
ranked based on the mean score, which aggregates metrics across scenarios," with all metrics
rescaled to 0–1 first (e.g. WildBench's 1–10 mapped to 0.0–1.0). The stated reason mean win
rate was dropped: it is "1) dependent on the set of models being compared, and 2) sensitive
to small variations in scenario scores that invert ranks." Verified at
`crfm.stanford.edu/2025/03/20/helm-capabilities.html`.

- **Implication for KOT-AI-INDEX/2:** the doc's §1.1 construction — normalise each benchmark
  against chance/ceiling, macro-average within domains then across domains — is
  **mean-of-normalised-scores**, i.e. HELM's *current* method, not the 2022 win-rate method.
  This is correct and defensible; the design should cite HELM Capabilities (2025), not (only)
  the 2022 paper, and should explicitly **forbid win-rate aggregation** in the analysis plan
  (it is model-set-dependent and rank-unstable — a §2.0 threat-model "index game").
- **Prior-failure judgment (mean win rate):** *fundamental* to ordinal head-to-head
  aggregation — model-set-dependence and rank-inversion are structural, not fixable with more
  data; HELM's own abandonment is the evidence. Mean-of-normalised-scores is the fix.

---

## 2. Composite-index statistics, and WHEN a scalar capability index is defensible at all

**Finding 2.1 — Chance/ceiling normalisation is standard and has a canonical formula.**
[established][search 2026-07-19] Both OLLv2 (§3) and HELM (§1) normalise so that
random→0, ceiling→1(00) before averaging. The generic form is
`s̃ = (s − chance)/(ceiling − chance)` — exactly the doc's §1.1 formula. This "balances the
influence of each benchmark based on difficulty" and is the mechanism by which macro-averaging
across benchmarks with different chance floors is even meaningful.

**Finding 2.2 — Macro-averaging within-then-across domains is the right shape, but the ceiling
choice is a live modelling decision that can move the scalar.** [established][search
2026-07-19] OLLv2 normalises subtasks individually against their own choice-count floor, then
averages (§3). The doc pins the ceiling at "published human/large-reference performance where
it exists, else a named pinned reference model's own-harness score." **Caution [speculative,
my inference]:** which ceiling you pin (human vs pinned-model vs 100%) changes each s̃ and can
change domain ranks — HELM's win-rate→mean-score episode is a proof-of-existence that
*aggregation/normalisation choices change rankings*. The ceiling constant must be frozen in
P3-D-INDEX and treated as a §2.0 "domain-reweighting/normalisation" game surface.

**Finding 2.3 — Variance/floor handling: report uncertainty, and beware near-floor discrete
metrics.** [established][search 2026-07-19] The construct-validity review (§2.5 below) finds
only **16%** of 445 benchmarks conducted any statistical testing — the programme's §2.5
(LCB95, hierarchical bootstrap over families/items, FWER) is already in the top decile of
practice. Separately, the **emergent-abilities-mirage** result (Schaeffer, Miranda, Koyejo,
"Are Emergent Abilities of LLMs a Mirage?", arXiv:2304.15004, NeurIPS 2023) shows that
**25 of 29 metrics** show smooth continuous scaling and that apparent "emergence" is an
artifact of *nonlinear / discontinuous* metrics (exact-match, thresholded accuracy) near the
floor. [established][search 2026-07-19]
- **Implication:** near a chance floor, discrete accuracy is a noisy, threshold-y estimator;
  the index should prefer *continuous* scores where a benchmark offers them (log-prob margin,
  per-token, Brier/calibration) and must report per-benchmark variance, or the scalar will
  inherit floor-induced instability precisely at R-0/R-1 where the programme's cheap decisive
  gate lives.

**Finding 2.4 — The honest answer to "when is a scalar capability index defensible at all":
the current construct-validity literature advises AGAINST composite indices and for measuring
individual phenomena.** [established][search 2026-07-19] "Measuring what Matters: Construct
Validity in Large Language Model Benchmarks" (arXiv:2511.04703; 445 benchmarks, 29 reviewers)
issues 8 recommendations; on fetch, the paper **"does not recommend aggregating multiple
benchmarks into indices; instead it emphasises measuring individual phenomena separately"**,
finds **47.8%** of benchmarks use *contested* construct definitions, and **only 16%** report
statistical testing. Its Rec-5 (implement contamination tests + maintain held-out sets) and
Rec-6 (report uncertainty for *all* primary scores) map directly onto the programme's
decontamination gate and §2.5. This is the strongest single citation for §7's honest null and
must be cited *by* P3-D-INDEX as the reason the vector, not the scalar, is the primary object.
- **Prior-failure judgment (scalar indices):** *fundamental*. A scalar cannot represent a
  multidimensional, non-fungible capability profile; the defence is not a better scalar but
  mandatory co-publication of the vector + a construct definition + uncertainty. The
  programme's "vector one link away, always" rule (§1.1) is the correct — and literature-
  endorsed — mitigation; the residual risk is that **W1 is *defined* on the scalar** (§7).

**Defensibility verdict [speculative, synthesised]:** a scalar capability index is defensible
**only as a ranking convenience atop a reported vector, under a frozen suite/normalisation,
with per-benchmark uncertainty, for models in a regime where its component benchmarks are
above floor and below ceiling.** Outside that envelope (near-floor small models; suite-shopped
membership; a spiky/abstaining system) the scalar is misleading and the programme should lean
on the domain vector and per-domain gating.

---

## 3. Open-LLM-Leaderboard-v2 design + small-model floors

**Finding 3.1 — OLLv2 composition and normalisation, verified at source.** [established]
[search 2026-07-19] OLLv2 evaluates six harder benchmarks — **IFEval, BBH, MATH (hard
subset), GPQA, MuSR, MMLU-Pro** — after v1 saturated. Normalisation (fetched from
`github.com/huggingface/leaderboards …/normalization.md`):
```
def normalize_within_range(value, lower_bound, higher_bound):
    return (value - lower_bound) / (higher_bound - lower_bound)
```
lower_bound = 1/num_choices for MC tasks (e.g. 0.25 for 4-choice), **returns 0 if the raw
score falls below the lower bound** (hard clamp), ×100 for scale; multi-subtask benchmarks
(BBH, MuSR) normalise each subtask against its own choice floor then average; generative tasks
(MATH, IFEval) take lower_bound ≈ 0 ("random generation is unlikely to produce correct
answers"). Final leaderboard score = **average of the six normalised benchmark scores**. This
is the exact template KOT-AI-INDEX/2 should reuse, with the addition of macro-averaging by
domain first.

**Finding 3.2 — OLLv2 floors out at small scale; the "≤500M" REVIEW-CITED claim is
CORROBORATED via mechanism + numbers.** [established][search 2026-07-19 for mechanism;
LIT-BACKED prior-session for SmolLM2 numbers] The clamp-to-0 rule means any model at or below
chance on a choice task scores **exactly 0** after normalisation, and near-chance maps to
near-0. Concretely, with the SmolLM2 card scores (verified 2026-07-10, `lit-eval-benchmarks.md`):
- **MMLU-Pro** random baseline = 10% (10 options, §6.5). SmolLM2-**1.7B** own-card MMLU-Pro
  MCF = **19.4** → normalised ≈ (19.4−10)/(100−10) ≈ **10.4**. The 135M/360M sit at/near 10%
  → normalised ≈ **0**.
- **GSM8K/MATH** (generative, floor ≈ 0): SmolLM2 GSM8K 5-shot = **1.4 / 3.2 / 31.0** for
  135M/360M/1.7B → the two small anchors are indistinguishable from zero.
- **IFEval** requires instruction-following that base models at R-1 largely lack (§6.6).
- **Conclusion:** at R-0/R-1 (≤~360M) the OLLv2-hard components collapse to a near-zero,
  non-discriminative band; **OLLv2 is the wrong general-capability anchor below ~R-3**, and the
  doc's decision to admit MMLU-Pro/BBH/MATH-family measurement **only at R-3+** is correct.
- **Prior-failure judgment:** *capability-limited AND measurement-floor* — partly the small
  model genuinely cannot, partly the discrete clamp erases what little signal exists. Mitigable
  by rung-appropriate benchmark selection (§6), not by re-normalising OLLv2.

---

## 4. Contamination detection + sealed-eval production

**Finding 4.1 — Contamination detection is a layered, individually-partial toolkit.**
[established][search 2026-07-19] Two surveys (arXiv:2404.00699 "A Comprehensive Survey of
Contamination Detection Methods in LLMs"; arXiv:2502.14425 "A Survey on Data Contamination for
LLMs") converge on: (a) **n-gram / substring overlap** (the doc's screener — cheap, but
*misses paraphrase*); (b) **canary strings** (require dataset-author cooperation); (c)
**membership inference** via per-token loss / **Min-K% probability** (bottom-k% token
probs; false-positive-prone); (d) **perturbation testing** (rewrite/swap/shuffle then
re-measure — *the most reliable signal and the most expensive*). No single method certifies
cleanliness; the honest posture is layered screening + a held-out sealed suite (§4.2).
- **Implication for the decontamination gate (§2.2(1)):** the doc's n-gram + embedding screen
  is necessary but insufficient by the literature's own account; add a **perturbation-robustness
  check** on flagged/near-threshold items and Min-K%-style membership probing where donor logits
  are available, and keep the human spot-check. Embedding-similarity partially covers the
  paraphrase gap n-gram misses. The doc's own §2.2a already concedes screening "CANNOT certify
  fairness" — this literature is exactly why, and names the residual holes.

**Finding 4.2 — Sealed-eval production: who, how, cadence — two production models.**
[established][search 2026-07-19]
- **LiveBench** (arXiv:2406.19314, ICLR 2025 spotlight): *procedural/refresh* model — questions
  drawn from **recently-released** sources (math competitions, arXiv papers, news, datasets);
  **updated monthly**, replacing on average **~1/6 of questions per update → full refresh
  ~every 6 months**; harder task versions released over time; **objective ground-truth scoring
  only** (no LLM/human judge); 6 categories (math, coding, reasoning, language, instruction-
  following, data analysis); top models still <70% (no ceiling-out). **Versioning discipline:
  each release is a distinct version, older items rotated out — never silently folded in.**
  *Note:* the arXiv title reads "Contamination-**Limited**"; some secondary write-ups say
  "Contamination-Free" — use "contamination-limited/-resistant", the authors' own hedge.
- **Scale SEAL** (`scale.com/blog/leaderboard`): *private-held-out* model — datasets built by
  a lab (Scale SEAL), scored by **verified domain experts**, kept **private/unpublished** so
  they cannot enter training data; contributors **barred from using any public code/questions**
  (StackOverflow, public GitHub) to guarantee novelty; **refreshed several times per year**.
- **Implication for P3-D-SEAL:** the doc's sealed-eval spec (independent party OR pinned
  procedural generator, versioned per release, temporally-fresh-facts leg for store systems,
  consistency-band gate) is a faithful hybrid of these two production models. Two concrete
  pins to adopt: (i) LiveBench's **"new release = new version, never silently merged"** rule;
  (ii) SEAL's **producer-isolation** rule (whoever/whatever authors the sealed suite must be
  disjoint from every developing agent and from the store-authoring pipeline — directly
  answers the "researcher adaptation to the frozen suite" hole in §2.2a).
- **Prior-failure judgment (public static benchmarks contaminating):** *fundamental* for any
  published static suite (the doc's own SWE-bench-Verified deprecation case, 2026, in
  `lit-eval-benchmarks.md` §3.4, is the canonical example — frontier models reproduced gold
  patches verbatim). The only structural fix is refresh (LiveBench) or privacy (SEAL); hence
  sealed eval is *mandatory*, not optional, for any W1 claim.

---

## 5. Proxy-rung validity — what R-0/R-1 (tiny-model) results have and have NOT predicted

This is the most consequential question for the programme's cheap-first ladder, and the
literature answer is **two-sided and asymmetric**: *pretraining loss* scales predictably;
*downstream task performance* frequently does not, especially near floors and across
formatting changes.

**Finding 5.1 — The optimistic side: downstream capability IS predictable from small models
when you aggregate many models and use continuous signal.** [established][search 2026-07-19]
- **Observational scaling laws** (Ruan, Maddison, Hashimoto, arXiv:2405.10938, NeurIPS 2024):
  build scaling laws from ~100 *existing* public models via low-rank (principal-component)
  decomposition of benchmark scores; several "emergent" phenomena become **smooth/sigmoidal
  and predictable** from smaller models.
- **Emergence-as-mirage** (arXiv:2304.15004): with linear/continuous metrics, 25/29 metrics
  scale smoothly — the "unpredictable jump" is largely a metric artifact.
- **Predicting Emergent Abilities with Infinite Resolution Evaluation** (arXiv:2310.03262,
  "PassUntil") and **Predicting Emergent Capabilities by Finetuning** (arXiv:2411.16035):
  targeted methods recover below-threshold signal / shift the emergence point to smaller
  models, making some emergence forecastable. [claimed][search 2026-07-19]

**Finding 5.2 — The honest-null side: downstream scaling is *unreliable*, and R-0/R-1 results
often fail to predict 1B+ direction.** [established][search 2026-07-19] "Scaling Laws Are
Unreliable for Downstream Tasks: A Reality Check" (arXiv:2507.00885): of **46 tasks, only
18 (39%) show smooth predictable improvement** — **61% are irregular** (inverse scaling,
non-monotonic, trendless, breakthrough). Failure modes: **data-dependency** (changing the
validation corpus *flips* which trend/corpus looks better), and **lack of robustness**
(benign changes to architecture, task formatting, or prompt design "completely change the
scaling trend" for the *same* task). Authors' prescription: **"verify scaling laws in your
own settings."** The emergent-abilities survey (arXiv:2503.05788) concurs: loss is
predictable, *task* performance "far from predictable"; near-random until a threshold.

**Finding 5.3 — What this means for THIS programme (the load-bearing synthesis).**
[speculative, synthesised from 5.1–5.2] The programme's ladder infers from an R-1 (~135M)
neurosymbolic *interface effect* toward an R-3 (1.7B) bet. That interface effect is a **novel
construct with no established scaling law** — none of the optimistic results (5.1) cover it;
they cover *pure-neural* capability aggregates over many *existing* models. The reality-check
(5.2) says even ordinary task scaling flips under formatting/data changes 61% of the time. So:
- R-0/R-1 can validly **kill** a family (a coverage ceiling that is zero at R-1, G1, is a real
  no; a mechanism that fails at G2 oracle is a real no) — *negative* proxy inferences are
  robust because they don't require monotone transfer.
- R-0/R-1 can**not** validly **certify** that a *positive* interface margin transfers to R-3.
  The doc partly handles this with **G5 two-size confirmation** and rung/gate discipline, but
  the design must treat any R-1 W1 margin as a **hypothesis about R-3, not evidence for it**,
  and hold benchmark harness/format *frozen and identical* across rungs (5.2's robustness
  failure is largely a formatting-drift artifact — controllable).
- **Prior-failure judgment (small-model proxying):** *capability-limited, conditionally
  mitigable* — reliable for above-floor, format-frozen, negative/kill inferences and for
  many-model continuous aggregates; *fundamentally unreliable* for near-floor discrete metrics,
  single-model positive extrapolation, and novel constructs. The programme lives on the
  mitigable side **only if** it (a) keeps components above floor per rung, (b) freezes format
  across rungs, (c) treats positive R-1 results as G5-confirmable hypotheses.

---

## 6. Per-benchmark suitability + floors/ceilings by rung

Chance floor and ceiling behaviour drive which benchmark discriminates at which rung. Summary
table, then notes. ("Chance" = normalisation lower bound; high chance ⇒ high floor ⇒ poor
small-model discrimination unless the benchmark is designed zero-shot for small models.)

| Benchmark | Construct / domain | Chance floor | Discriminates at R-0/R-1? | Best rung home | Verification |
|---|---|---|---|---|---|
| **BLiMP** | D1 grammar (minimal pairs) | 50% (2-way) | **Yes** — zero-shot, log-prob; BabyLM standard at 10–100M *words* | R-0/R-1 | [established] §6.1 |
| **EWoK** | D1/world-model (plausibility) | ~50% (2-way) | Partial — near-floor at BabyLM scale, discriminates as it grows | R-0/R-1 (with floor caveat) | [established] §6.1 |
| **CLUTRR** | D4 relational (kinship) | ~5% (many relations) | **Yes, by hop count** — but long hops floor at small scale | R-1 (D4 core) | [established] §6.2 |
| **ProofWriter / RuleTaker** | D4 rule/deductive | ~50% (binary entailment) | Partial — high floor; use **proof-depth** splits for signal | R-1 (held-out depths) | [established] §6.3 |
| **FOLIO** | D4 FOL (NL) | ~33% (True/False/Unknown) | Weak at R-1 — small, hard, human-curated | R-2/R-3 | [established] §6.3 |
| **IFEval** | D6 instruction-following | ~0 (generative, verifiable) | **No** at R-1 base models | R-2 iff above floor, else R-3 | [established] §6.6 |
| **MMLU-Pro** | D3 knowledge/reasoning | 10% (10-way) | **No** — floors ≤~R-2 | R-3+ | [established] §6.5 |
| **BBH / BBEH** | D5/reasoning | mixed (mostly MC) | **No** — BBH saturating *up*, BBEH hard even for SOTA | R-3+ (where discriminative) | [established] §6.4 |
| **GSM8K** | D5 math (generative) | ~0 | **No** at R-1 (SmolLM2 135M=1.4, 360M=3.2) | R-2/R-3 above-floor only | [LIT-BACKED prior-session] |

**§6.1 BLiMP / EWoK (D1 linguistic + world-model).** [established][search 2026-07-19]
- **BLiMP** (Warstadt et al., TACL 2020, arXiv:1912.00582): **67 paradigms × 1000 minimal
  pairs**; automatically generated from expert grammars; **human agreement 96.4%**; scored
  **zero-shot** by whether the LM assigns higher probability to the acceptable sentence (chance
  50%). Because it is a log-prob forced choice, it **discriminates at small scale** — it is the
  BabyLM standard and the right D1 anchor at R-0/R-1. Ceiling caution: strong LMs push into the
  90s, so it can ceiling-out by R-3 on easy paradigms — report per-paradigm, keep the hard
  paradigms.
- **EWoK** (Ivanova et al., arXiv:2405.09605, EWoK-CORE-1.0): **4,374 items across 11 knowledge
  domains**; plausible/implausible context–target matching (chance ~50%). BabyLM finding:
  systems trained on ≤100M words "do not learn world knowledge" — so EWoK is **near-floor at the
  smallest scales**; it earns its place as a *growth* discriminator through R-1→R-2, not as an
  R-0 separator. Report it, but do not weight the index on it at R-0.

**§6.2 CLUTRR (D4 relational — the neurosymbolic core).** [established][search 2026-07-19 +
prior-session] Sinha et al., EMNLP 2019, arXiv:1908.06177 — **verified at source**. Kinship
relation inference from short stories; a **procedural generator** parameterised by reasoning
hops k; **systematic-generalisation** splits = held-out *combinations* of logical rules;
**robustness** splits = added noise/supporting/irrelevant facts; metric = accuracy over ~20
kinship classes (chance ~5%, low floor → good discrimination). This is the ideal D4 instrument
because its held-out-rule-combination and held-out-hop-depth structure is exactly the
generalisation the neurosymbolic thesis claims, and its low chance floor gives signal at R-1.
Caveat: **licence CC-BY-NC-4.0** (non-commercial — cannot ship in a commercial artifact;
research/eval only). Small-scale caveat: long-hop splits floor at R-0/R-1 — stratify by hop.

**§6.3 ProofWriter / RuleTaker / FOLIO (D4 rule/deductive).** [established][search 2026-07-19]
- **RuleTaker** (Clark et al.) → **ProofWriter** (Tafjord et al.): synthetic NL deduction;
  RuleTaker D0–D5 subsets (~100k each) graded by **proof depth**; ProofWriter adds Open-World
  Assumption + proof generation. Mostly **binary entailment ⇒ chance ~50% (high floor)** — use
  the **proof-depth splits** (accuracy-vs-depth curve) rather than a single accuracy for signal,
  and hold out depths for generalisation (matches the doc's "held-out proof depths").
- **FOLIO** (Han et al., arXiv:2209.00840): **1,435** *human-expert-curated* FOL examples,
  **True/False/Unknown** (chance ~33%); richer, more natural language than the synthetic sets.
  Small, hard, higher floor ⇒ **weak at R-1**; better as an R-2/R-3 harder-generalisation probe.
- **Suitability:** ProofWriter/RuleTaker for the R-1 D4 workhorse (depth-stratified); FOLIO as
  the R-2+ naturalistic FOL check. Both binary/ternary floors demand careful chance-normalisation.

**§6.4 BBH / BBEH (reasoning).** [established][search 2026-07-19] BBH is **saturating upward** —
SOTA reaches near-perfect on many BBH tasks, diminishing its utility. **BBEH** (BIG-Bench Extra
Hard, arXiv:2502.19187, 2025) replaces each BBH task with a harder novel task probing the same
capability; SOTA harmonic-mean accuracies are low (reported in the ~9.8%–44.8% range across
model classes) — i.e. it **discriminates even among frontier models** but **floors out entirely
below R-3**. Use BBH/BBEH only at R-3+ and only on tasks shown discriminative at the target rung.

**§6.5 MMLU-Pro (knowledge/reasoning).** [established][search 2026-07-19] arXiv:2406.01574,
NeurIPS 2024 — **10 options ⇒ 10% random** (vs 25% for MMLU); **16–33% harder** than MMLU;
prompt sensitivity cut from 4–5% to **~2%** (24 prompt styles) — more stable and more
discriminative *at scale*. But 10% floor + reasoning difficulty ⇒ floors ≤~R-2; the doc's
placement at **R-3+ only**, replacing unstable MMLU-cloze, is correct. **Prior-failure judgment
(MMLU-cloze cross-rung):** *capability-limited/measurement* — the SmolLM2 cards mix cloze
(135M/360M) with MCF (1.7B), a **format** confound, not a capability regression; fixed by
pinning one format/harness across rungs (the programme already drops cloze).

**§6.6 IFEval (instruction-following).** [established][search 2026-07-19] arXiv:2311.07911 —
**25 verifiable instruction types**, ~**500 prompts**, scored objectively at prompt- and
instruction-level, strict and loose (generative, chance ≈ 0). Because it needs genuine
instruction-following, **base models at R-1 are near-floor**; the doc's "IFEval iff above floor
at R-2, full at R-3" gating is right. Its objective/verifiable design (no judge model) makes it
a clean, un-gameable D6 instrument *once above floor*.

---

## 7. The honest null — the strongest reason a scalar AI-index could be indefensible for THIS programme

[speculative, synthesised — flagged as the load-bearing skeptical read for the review gate]

The strongest published attack is **not** "your normalisation is slightly off"; it is that
**the current construct-validity literature affirmatively recommends against composite indices**
(Finding 2.4, arXiv:2511.04703) — measure individual phenomena, do not roll them into one
number. On top of that base objection, four programme-specific failure paths compound:

1. **W1 is *defined* on the scalar.** §1.4 makes the win condition `LCB95(INDEX(S) − INDEX(C))
   > δ_k` — a scalar difference. Every indefensibility of the scalar (suite-membership
   sensitivity, ceiling-constant choice, domain-weighting) becomes an indefensibility of the
   *win claim*. Reporting the vector "one link away" protects honesty of *description* but not
   the *decision rule*. **This is the sharpest steering finding of this review.**
2. **Spiky/abstaining profiles interact badly with macro-averaging.** A store-based system is
   expected to dominate D4 (covered relational/rule reasoning) and abstain/floor elsewhere.
   Macro-averaging either (a) scores abstention as chance/floor — burying a real, narrow win
   under five near-floor domains — or (b) excludes abstained items — inflating the scalar and
   opening an abstention game (§2.0 already names this). Either way the *scalar* misrepresents a
   system whose value is exactly its non-uniform profile.
3. **Aggregation choices demonstrably flip rankings.** HELM's own win-rate→mean-score migration
   (Finding 1.2) is existence-proof that the choice of aggregator changes who "wins." A single
   scalar hides this fragility.
4. **Proxy-rung non-transfer (Finding 5.2).** Even a per-rung-defensible scalar may not predict
   the R-3 direction of the interface effect; a scalar "win" at R-1 can be a scalar "loss" at
   R-3 for reasons unrelated to the architecture (formatting/data sensitivity, 61% irregular).

**Why the programme can still proceed (the rebuttal, tagged [speculative]):** the doc's
mitigations are individually best-practice — vector-always, domain-macro-then-scalar, abstention
and covered/uncovered splits reported, calibration on known-ordered neural models (P3-E-CAL),
frozen suite/normalisation, §2.5 uncertainty + FWER. The residual, un-eliminable risk is #1:
**a scalar-defined win condition inherits the scalar's indefensibility.** The design bead should
seriously consider **strengthening W1 from scalar-LCB to (scalar-LCB AND per-domain
non-inferiority / no-domain-regression)**, so that a "win" cannot be a scalar artifact of
one dominant domain masking regressions elsewhere. That is the honest null's actionable residue.

---

## 8. (a) Design recommendations P3-D-INDEX (+ P3-D-SEAL / P3-D-POWER / P3-D-BASE) should adopt

Opening questions for the spawned design beads are answered here as recommendations (I did not
create beads, per instruction; coordinator to spawn).

**For P3-D-INDEX / KOT-AI-INDEX/2:**
1. **Aggregate by mean-of-normalised-scores, never win rate.** Cite **HELM Capabilities (2025)**
   as the method source; forbid win-rate aggregation in the analysis plan as a §2.0 index game
   (model-set-dependent, rank-unstable). [from §1.2]
2. **Adopt the OLLv2 normalisation formula verbatim** — `(s−chance)/(ceiling−chance)`,
   per-subtask floors, clamp-to-0 — then macro-average within domain, then across domains.
   Pin `num_choices`-derived floors per benchmark. [from §3.1]
3. **Freeze the ceiling constant explicitly and treat it as a threat surface.** Pin
   human-or-reference ceiling per benchmark at freeze; register that changing it is a version
   bump. Prefer continuous per-benchmark signals near floors (log-prob margins) to blunt
   metric-artifact instability (emergence-mirage). [from §2.2, §2.3]
4. **Rung-gate benchmark membership by measured floor, not by prestige.** R-0/R-1 index: BLiMP,
   CLUTRR (hop-stratified), ProofWriter/RuleTaker (depth-stratified), EWoK (growth), reduced MC
   commonsense above floor. Defer MMLU-Pro, BBH/BBEH, FOLIO, MATH, IFEval-full to **R-2/R-3**.
   Run a **per-rung floor census** (does each candidate benchmark clear chance by a
   pre-registered margin on the pinned pure-neural anchors?) *before* admitting it. [from §3.2, §6]
5. **Report the full vector as the primary object; the scalar is a ranking convenience.**
   Include per-benchmark score + variance, refusal/abstention rate, covered-vs-uncovered split.
   Cite arXiv:2511.04703 as the reason. [from §2.4, §7]
6. **Consider strengthening W1** from scalar-LCB alone to scalar-LCB **and** per-domain
   no-regression / domain-vector non-inferiority — the honest null's actionable fix. [from §7]

**For P3-D-SEAL:** adopt the LiveBench **"new release = new version, never silently merged"**
versioning rule and the SEAL **producer-isolation** rule (sealed-suite author disjoint from all
developing agents and the store pipeline); include a temporally-fresh-facts leg for store
systems; pin the frozen-vs-sealed **consistency band** as a directional gate; use
"contamination-limited/-resistant," not "-free." Add a **perturbation-robustness** check to the
decontamination screener (the most reliable published signal) plus Min-K% membership probing
where donor logits are available. [from §4]

**For P3-D-POWER:** the G1 coverage-ceiling census must use **above-floor, normalised**
per-benchmark accuracies `a_b^cov` (not raw), because near-floor raw accuracies overstate
headroom on high-chance benchmarks. Compute `Δ_max` on the *normalised* scale so the power/
margin table is commensurate with the index the win is defined on. [from §2.3, §6]

**For P3-D-BASE:** pin the pure-neural anchors (SmolLM2 135M/360M/1.7B) with a **single frozen
harness and prompt format held identical across rungs** — cross-rung format drift is the
dominant cause of the 61%-irregular downstream-scaling result (§5.2) and would masquerade as an
architecture effect. Calibration (P3-E-CAL) should verify expected ordering *and* that
per-benchmark variance is within a pre-registered band at each rung before any architecture claim.

## 8. (b) Open questions the design bead MUST resolve

1. **Should W1's decision rule stay scalar, or become scalar + per-domain no-regression?** (§7#1)
   — a genuine measurement-philosophy fork, not answerable from literature alone.
2. **How is abstention scored in the index?** As floor/chance, as exclusion-with-coverage-
   penalty, or via a risk-coverage curve? This choice determines whether a spiky store system
   can win honestly, and is a §2.0 game surface. (§7#2)
3. **Which ceiling per benchmark** (human vs pinned-reference-model vs 100%), and how are
   benchmarks *without* a credible human ceiling handled? (§2.2)
4. **Continuous vs discrete metric per benchmark at R-0/R-1** — does the index take log-prob
   margins where available to avoid floor-induced metric artifacts, and how are continuous and
   discrete benchmarks combined commensurably? (§2.3, §5)
5. **Domain weighting** — equal-weight domains, or weight by discrimination/reliability? Equal
   weight is defensible-by-default but lets a low-signal domain add noise; weighting invites a
   game. (§2.2, §7#3)
6. **Sealed-suite producer** — independent human party vs pinned procedural generator vs both;
   who has the budget/independence to produce and refresh it on cadence? (§4.2)
7. **Cross-rung index continuity** — R-0/R-1 and R-3 indices share few benchmarks (floors force
   different membership); how is the *continuity* claim made when the suite legitimately changes
   between rungs? (§5.3, §6) — this is an index-version-management question the doc flags but
   does not resolve.

## 9. Citation-verification table (ref → reachable at source? → supports the claim?)

| # | Reference | Reachable this session? | Supports the load-bearing claim? |
|---|---|---|---|
| C1 | HELM, Liang et al., **arXiv:2211.09110** (TMLR 2023); CRFM HELM pages | Yes (abstract + CRFM) | **Yes** — 7 metrics × 16 core scenarios; original mean-win-rate |
| C2 | **HELM Capabilities**, `crfm.stanford.edu/2025/03/20/helm-capabilities.html` | Yes (fetched) | **Yes** — mean SCORE not win rate; win-rate is model-set-dependent + rank-unstable |
| C3 | OLLv2 normalization, `github.com/huggingface/leaderboards …/normalization.md` | Yes (fetched) | **Yes** — formula, per-subtask floors, clamp-to-0, average-of-normalised |
| C4 | OLLv2 composition + small-model range | Yes (search + HF space) | **Yes** — 6 hard benchmarks; sub-1B to 140B models present |
| C5 | **LiveBench**, **arXiv:2406.19314** (ICLR 2025 spotlight) | Yes (abstract fetched) | **Yes** — monthly updates, ~1/6 replaced, ~6-mo full refresh, objective scoring, "Contamination-Limited" |
| C6 | **CLUTRR**, Sinha et al., **arXiv:1908.06177** (EMNLP 2019) | Yes (abstract + GitHub) | **Yes** — kinship inference, held-out rule combos, hop generator; CC-BY-NC-4.0 |
| C7 | Construct validity, "Measuring what Matters", **arXiv:2511.04703** | Yes (HTML fetched) | **Yes** — 445 benchmarks; 8 recs; does NOT recommend composite indices; 16% stat-tested |
| C8 | Emergence-mirage, Schaeffer et al., **arXiv:2304.15004** (NeurIPS 2023) | Yes (search + NeurIPS) | **Yes** — 25/29 metrics smooth; emergence a metric artifact |
| C9 | Observational scaling laws, Ruan et al., **arXiv:2405.10938** (NeurIPS 2024) | Yes (NeurIPS + HF) | **Yes** — ~100 models, PC decomposition, predictable emergence |
| C10 | "Scaling Laws Are Unreliable for Downstream Tasks", **arXiv:2507.00885** | Yes (HTML fetched) | **Yes** — 39% smooth / 61% irregular of 46 tasks; format/data flips trends |
| C11 | Contamination surveys, **arXiv:2404.00699**, **arXiv:2502.14425** | Yes (search) | **Yes** — n-gram/canary/Min-K%/perturbation; each partial |
| C12 | Scale **SEAL**, `scale.com/blog/leaderboard` | Yes (search) | **Yes** — private held-out, expert-scored, producer-isolated, multi-yearly refresh |
| C13 | **MMLU-Pro**, **arXiv:2406.01574** (NeurIPS 2024) | Yes (search + HTML) | **Yes** — 10 options/10% chance; 16–33% harder; prompt sensitivity 4–5%→2% |
| C14 | **BBEH**, **arXiv:2502.19187** (2025) | Yes (search) | **Yes** — BBH saturated; BBEH harder, discriminates SOTA, floors below R-3 |
| C15 | **IFEval**, Zhou et al., **arXiv:2311.07911** | Yes (search + HF) | **Yes** — 25 verifiable instr. types, ~500 prompts, strict/loose, objective |
| C16 | **FOLIO**, Han et al., **arXiv:2209.00840** | Yes (search + HTML) | **Yes** — 1,435 expert FOL examples, True/False/Unknown |
| C17 | ProofWriter (Tafjord) / RuleTaker (Clark) | Yes (search, secondary) | **Partial** — structure/depth-splits confirmed via secondary sources; primary arXiv ids not individually fetched this session — see caveat |
| C18 | **BLiMP**, Warstadt et al., **arXiv:1912.00582** (TACL 2020) | Yes (search + ACL) | **Yes** — 67 paradigms × 1000 pairs, zero-shot, 96.4% human agreement |
| C19 | **EWoK**, Ivanova et al., **arXiv:2405.09605** | Yes (search) | **Yes** — EWoK-CORE-1.0, 4,374 items, 11 domains, plausibility 2-way |
| C20 | Snell et al. test-time compute, **arXiv:2408.03314** (ICLR 2025) | Yes (search) | **Yes** — confirms the doc's "ICLR-2025 test-time-compute" citation exists; **deep-dive deferred to P3-LR-RAG** (owner bead) |
| C21 | SmolLM2 card scores, MMLU/GSM8K floors | Prior-session (2026-07-10) | **Yes** — `reports/lit-eval-benchmarks.md`, source-verified then |

**Citations that FAILED source-verification this session:** none failed outright. **One
partial (C17):** ProofWriter and RuleTaker canonical facts (D0–D5 subset sizes, OWA/CWA proof
generation) were corroborated from *secondary* aggregations (survey PDFs, benchmark cards), not
by fetching Clark et al. (RuleTaker) or Tafjord et al. (ProofWriter) primary arXiv pages
individually — P3-D-INDEX should fetch both primaries before pinning any depth-split N or
licence for these two. **One naming caveat (C5):** LiveBench's arXiv title is
"Contamination-**Limited**"; some secondary write-ups say "Contamination-Free" — the doc should
use the authors' hedge. **One cross-bead deferral (C20):** the ICLR-2025 test-time-compute
result is verified to *exist* and is correctly cited, but its operational content is
P3-LR-RAG's deliverable, not this bead's.

---

## 10. Epistemic register (what this review relied on)

- Load-bearing methodology sources (HELM Capabilities aggregation, OLLv2 normalisation,
  LiveBench cadence, construct-validity recommendations, downstream-scaling reliability) were
  **fetched at source** and quoted. Benchmark-suitability claims mix source-fetched primaries
  (BLiMP, CLUTRR, MMLU-Pro, FOLIO, IFEval, BBEH, EWoK) with two secondary-corroborated items
  (ProofWriter/RuleTaker, C17).
- Programme-internal facts (SmolLM2 card scores, SWE-bench-Verified deprecation) are cited from
  `reports/lit-eval-benchmarks.md` (source-verified 2026-07-10), used as recall infrastructure,
  not as fresh evidence.
- The §7 honest-null and all cross-rung/W1 recommendations are **[speculative]** syntheses
  explicitly flagged for the review gate — they are the parts most in need of Fable + GPT-5.6
  critique, since they touch the win-condition definition, which is a maintainer-judgement
  surface (candidate for a GitHub decision issue if the design bead agrees the scalar-only W1
  rule should change).
