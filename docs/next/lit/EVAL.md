# P3-LR-EVAL — Evaluation + AI-index methodology: decision-oriented literature review

> **Status: Phase-0 [LIT] deliverable of Programme-3 (bead kernel-of-truth-s55r.2).
> Nothing here is frozen, registered, or scheduled; no registry record, KB shard,
> or assumption entry is touched.** Author: Fable (chief-architect role,
> `kern/fable-designer`), 2026-07-11.
> Parent: `docs/next/programme-3-neurosymbolic-architecture.md` (revision 2) §5,
> P3-LR-EVAL row; the GPT-5.6 referee report
> (`poc/gpt56-review/p3-review-20260711/review.md`) named the works this review
> verifies. Spawns (recommendations only — the coordinator creates beads):
> **P3-D-INDEX, P3-D-SEAL, P3-D-POWER, P3-D-BASE** (§9).
>
> **Revision 2 (2026-07-11), per the independent GPT-5.6 review of this
> deliverable (`poc/gpt56-review/rev-lreval-20260711/`):** the sealed-evaluation
> gate is strengthened to a registered sealed-side baseline margin (§4); the
> GSM1k gap is re-read as observed drops in a tested population, not an
> honest-model tolerance band (§4, §8.5); ceiling, normalization-scope,
> bootstrap-estimand, and power-bound mathematics are corrected (§2, §5, §6);
> and floor-validation / hand-off claims are tempered to what the evidence
> carries (§3, §9). Sources unchanged except one corrected HELM claim and one
> added `verified:false` MATH-floor record.
>
> **Tag convention** (mapping the house discipline onto a lit-review):
> `[LIT-BACKED: source, year]` = external empirical fact verified AT SOURCE this
> session (WebFetch/WebSearch on 2026-07-11; URL in §10 / EVAL.sources.jsonl);
> `[MEASURED: registry/...]` = restatement of a programme verdict inside its own
> envelope; `[STIPULATED]` = a judgement or recommendation I make here;
> `[EXTRAPOLATION]` = a forward projection, never a premise. Anything not
> verifiable at source is marked **UNVERIFIED** inline, never silently carried.

---

## 0. Dedup: what already exists in-repo, and what this review adds

Surveyed before anything was added (the DEDUP-FIRST instruction):

- `reports/lit-eval-benchmarks.md` (Kern, 2026-07-10) — a G3-freeze fact sheet
  verifying at source: CLUTRR (arXiv:1908.06177, EMNLP 2019, CC-BY-NC-4.0,
  generator-based), the nine SmolLM2-card benchmarks (papers, licences, sizes,
  metrics, card scores incl. the MMLU cloze-vs-MMLU-Pro card inconsistency),
  HumanEval/MBPP/SWE-bench lineage, and the SWE-bench-Verified contamination
  deprecation (OpenAI ~2026-02-23: gold-patch reproduction + 59.4%-flawed-test
  audit; SWE-bench Pro's copyleft+held-out design as the replacement). **This
  review does not re-derive any of those facts; it cites them.**
- `docs/next/benchmark-evaluation-strategy.md` (2026-07-10) — the SmolLM2-suite
  triage (covered-help / non-regression / math-route), the anchoring protocol
  (±2.0 pp harness-fidelity tolerance), the Δ_B = κ_B × Δ_covered identity, and
  the "no cross-benchmark aggregation over the nine" rule. Programme-3 rev-2
  already demoted that nine-task suite to KOT-SMOL-CONT/1 (ASM-0811); this
  review supplies what replaces it.
- `kb/records/` (639 records, kot-lit-1 schema) — **architecture/mechanism
  records only** (seams, steering, PRMs, constrained decoding, knowledge
  injection). There is NO eval-methodology shard; the closest matches (Logic-LM,
  VersaPRM, MASPRM, draft-conditioned CD) are baseline-component prior art for
  P3-LR-RAG/P3-LR-RULE, not index methodology. Nothing below duplicates a KB
  record. Per governance, nothing here is ingested into the KB — the staging
  file `docs/next/lit/EVAL.sources.jsonl` is for the coordinator's central
  ingest.
- `docs/next/eval-necessity-adjudication.md`, `docs/research-plan/08-stats-*` —
  provenance-triple + one-primary discipline, inherited not restated.

What is NEW here: HELM's construction and aggregation; the OLLv2 component set,
normalization mathematics, and measured tiny-scale floors; contamination
detection limits + how sealed benchmarks are actually produced; proxy-rung
validity (the metric-dependence result); per-benchmark floor/ceiling evidence
for the KOT-AI-INDEX/2 D1–D7 table; and the four Phase-1 design hand-offs.

---

## 1. HELM: multi-scenario construction, and why a flat accuracy average is inadequate

- LOAD-BEARING: HELM (Liang, Bommasani, Lee et al., "Holistic Evaluation of
  Language Models", TMLR 2023) evaluates 42 scenarios (16 core + 26 targeted)
  with 7 metrics — accuracy, calibration, robustness, fairness, bias, toxicity,
  efficiency — measured for core scenarios *when possible* (87.5% of
  (core-scenario, metric) pairs, per the paper's own qualification; NOT
  unconditionally per scenario) — with standardized conditions that
  raised cross-model scenario coverage from 17.9% to 96.0% over 30 models
  [LIT-BACKED: arXiv:2211.09110, TMLR 2023].
- The construction the review told us to copy is the two-level structure:
  scenarios (use cases) × metrics (desiderata), taxonomized first and THEN
  populated, so gaps are explicit rather than invisible. A flat accuracy
  average has no seat for calibration/robustness at all, and mixes scenarios
  with different chance floors and variances into one number — HELM's central
  argument is that single-metric evaluation lets "metrics beyond accuracy fall
  to the wayside" and hides trade-offs [LIT-BACKED: arXiv:2211.09110, 2023].
- Aggregation caution: HELM's original headline aggregate was the **mean win
  rate** (fraction of head-to-head comparisons won across scenarios). This is
  ORDINAL — it obscures effect magnitude, and it is comparator-set-dependent:
  adding/removing models changes every score, and small scenario-score
  variations can invert ranks. Later HELM-family work moved to mean score over
  normalized metrics for exactly this reason. **UNVERIFIED at primary source**
  for the internal aggregation details (read via secondary sources — the AHELM
  paper and topic surveys; the HELM paper abstract itself was fetched but its
  aggregation section was not) — carried as a flag, not a fact.
- DECISION for P3-D-INDEX [STIPULATED]: adopt HELM's *structure* (domains ×
  metrics, gaps explicit, vector always published) but NOT mean-win-rate
  aggregation — a win-rate scalar would make KOT-AI-INDEX/2 comparator-set
  dependent, which directly conflicts with W1's pre-registered frontier F(B_k)
  (adding a comparator must not move S's own index). Use chance/ceiling
  normalization + macro-averaging (§2), which is absolute per system. The
  domain/benchmark weights inside that macro-average are a NORMATIVE registered
  choice — not a statistical consequence of HELM or metabench — and must be
  fixed at the P3-D-INDEX freeze, along with missing-domain handling and
  cross-rung comparability rules (§2, §8.2).

## 2. Composite-index statistics: normalization, macro-averaging, and when a scalar is defensible

**Normalization against chance (the practice standard).**

- LOAD-BEARING: the Open LLM Leaderboard v2 normalizes every score by
  subtracting the task's random-guess baseline and rescaling to 0–100:
  `norm = (raw − lower_bound)/(1 − lower_bound)`, clamped to 0 below chance;
  for tasks with heterogeneous subtasks (BBH's 24 subtasks with num_choices
  2–19; MuSR's 2/5/3-choice subtasks) each subtask is normalized against ITS
  OWN chance floor first and the normalized scores are then averaged;
  generative tasks (MATH, IFEval) take lower_bound = 0 [LIT-BACKED:
  huggingface.co/docs/leaderboards/open_llm_leaderboard/normalization, 2024].
- This verifies the exact shape ASM-0811 step (1)–(2) stipulated: normalize
  within-benchmark against chance, THEN average — with one difference:
  **OLLv2 pins the ceiling at 1.0; KOT-AI-INDEX/2 additionally pins a
  benchmark-specific ceiling** (human/large-reference). No published leaderboard
  we verified does ceiling-pinning; that piece is ours to freeze and defend
  [STIPULATED]. The candidate reference anchors this review verified: BLiMP
  human 88.6% (individual) / 96.4% (aggregate) [LIT-BACKED: arXiv:1912.00582,
  TACL 2020]; EWoK human > all tested models 1.3B–70B (exact human % in paper
  body, not re-verified here — pin at freeze) [LIT-BACKED: arXiv:2405.09605,
  TACL 2025]. Where no human reference exists, ASM-0811's "named pinned
  reference model" fallback stands. **CAUTION (review-mandated): none of these
  references are true ceilings.** They are noisy point estimates obtained under
  particular prompts and harnesses; pinning one as a denominator risks unstable
  denominators, normalized scores above 1, information loss if clamped at 1,
  and rank changes whenever the reference is updated. BLiMP's 88.6
  (individual-annotator) and 96.4 (aggregate-of-annotators) are DIFFERENT
  estimands, not interchangeable ceiling candidates. P3-D-INDEX must therefore
  register, per component: which estimand is pinned, the reference score's
  uncertainty, the above-reference/clamping rule, and a version-bump policy for
  reference updates (a reference change is an index version change) (§8.1)
  [STIPULATED].
- SCOPE limit of the normalization (review-mandated): the chance-to-ceiling
  formula above is defined for ACCURACY-type metrics only. Held-out LM loss
  (an R-0 index component), calibration, abstention/selective prediction, and
  robustness metrics have NO chance floor and no analogous verified transform
  anywhere in this review — each needs its own registered metric-specific
  transform, or exclusion from any scalar with vector-only reporting, before
  entering KOT-AI-INDEX/2. Likewise, the generative-task convention
  lower_bound = 0 is a CONVENTION, not a measured chance floor [STIPULATED].
- Different answer cardinalities are therefore handled (per-subtask floors),
  but **different variances are NOT handled by OLLv2** — a 250-item benchmark
  and a 14k-item benchmark enter the average with equal weight and very
  different standard errors. Nor does a hierarchical bootstrap "handle" them
  (the earlier draft overclaimed this): bootstrapping quantifies UNCERTAINTY in
  whatever aggregate is defined; it does not resolve the weighting estimand,
  which remains a registered normative choice. For a FIXED registered suite the
  correct shape is: fixed (registered) domain and benchmark weights, with the
  bootstrap resampling items, prompts/seeds, and paired system-vs-baseline
  outputs WITHIN benchmarks — resampling benchmark families would be coherent
  only if the suite were modelled as a sample from a larger benchmark universe,
  which a registered suite is not. Neither piece has an off-the-shelf
  leaderboard precedent we could verify; both go in the P3-D-INDEX analysis
  plan [STIPULATED].

**Is a scalar defensible at all?**

- LOAD-BEARING: metabench (Kipnis et al., ICLR 2025) fit IRT models over
  ~5,000 public LLMs × 28,632 items from six benchmarks (ARC, GSM8K, HellaSwag,
  MMLU, TruthfulQA, WinoGrande) and found (a) <3% of items reconstruct each
  benchmark score at 1.24% RMSE and the total at 0.58% RMSE, and (b) a single
  common factor with Spearman r = 0.94 against the total score [LIT-BACKED:
  arXiv:2407.12844, ICLR 2025].
- Reading for us [STIPULATED]: the six legacy benchmarks are so redundant that
  their average measures ONE factor — which is precisely the GPT-5.6 objection
  to revision-1's nine-task suite (seven correlated MC tasks). A scalar over a
  suite dominated by one factor is defensible but UNINFORMATIVE about a
  neurosymbolic system whose hypothesis is a *profile* change (D4 up, D2 flat).
  This is independent quantitative support for the domain-vector-first rule:
  the scalar exists for ranking, the vector for honesty (ASM-0811 (3)). It
  MOTIVATES but does not prove the D4 diagnostics: metabench establishes
  redundancy among those six benchmarks only — it does not show D4 is the only
  capability outside the common factor, nor does it validate the D1–D7
  ontology; whether D4 components load on the legacy factor is an open
  empirical question for P3-E-CAL. It also licenses item-level suite
  compression at R-1 (IRT-selected subsets) as a cost lever IF we accept
  reconstruction error as added variance — flagged as a P3-D-INDEX option, not
  a default [EXTRAPOLATION].

## 3. Open-LLM-Leaderboard-v2: components, and which floor out at 100M–2B

- LOAD-BEARING: OLLv2's six components and setups are: IFEval (0-shot, strict
  acc, prompt+inst level), BBH (3-shot, acc_norm over 24 subtasks, choices
  2–19), MATH Lvl-5 (4-shot, exact match), GPQA (0-shot, acc_norm, 4-choice),
  MuSR (0-shot, acc_norm, 3 subtasks: 2/5/3-choice), MMLU-Pro (5-shot, acc,
  10-choice); run on the EleutherAI lm-evaluation-harness with chat template
  for instruct models [LIT-BACKED:
  huggingface.co/docs/leaderboards/open_llm_leaderboard/about, 2024].
- Floor evidence at the programme's rungs, from the SmolLM2 instruct cards
  (own-harness lighteval; anchor numbers, not our measurements):
  - MMLU-Pro MCF: 1.7B-Instruct **19.3** vs 10% chance (10-choice) — ~9 pp of
    normalized headroom; Qwen2.5-1.5B-Instruct 24.2, Llama-1B-Instruct 12.7
    (≈ 3 pp above chance) [LIT-BACKED: HuggingFaceTB/SmolLM2-1.7B-Instruct
    card, 2025]. At 135M/360M the cards do not even report MMLU-Pro (they
    report MMLU-cloze) — the fact-sheet inconsistency stands [LIT-BACKED:
    reports/lit-eval-benchmarks.md §2 + HuggingFaceTB cards, 2025].
  - BBH 3-shot: 1.7B-Instruct **32.2**, 135M-Instruct **28.2** [LIT-BACKED:
    SmolLM2 instruct cards, 2025]. **CAUTION (review-mandated — the earlier
    draft's near-floor inference was unsafe):** those card numbers come from
    SmolLM2's own lighteval harness, while the 2–19-choice subtask inventory
    comes from OLLv2's OWN adaptation (24 subtasks, vs the original paper's 23
    tasks [LIT-BACKED: arXiv:2210.09261]); the two are NOT established to share
    task representation, metric, or aggregation, so no near-floor conclusion
    follows from combining them. The 4-raw-point 135M→1.7B gap is CONSISTENT
    WITH weak discrimination at ≤2B, nothing stronger [EXTRAPOLATION]; the
    actual normalized floor and discrimination must be computed mechanically on
    the ONE pinned harness (P3-E-CAL) before any floor-based placement claim.
  - GSM8K: base cards 1.4 / 3.2 / 31.0 (135M/360M/1.7B, 5-shot); 48.2 at
    1.7B-Instruct [LIT-BACKED: reports/lit-eval-benchmarks.md §2.9 +
    SmolLM2-1.7B-Instruct card, 2025]. Floored at ≤360M; discriminative at
    1.7B → D5 enters at R-2 (≥1.7B-class), not R-1, unless the R-1 rung is
    ≥1B [STIPULATED].
  - IFEval: 135M-Instruct **29.9** (card's prompt/inst average), 1.7B-Instruct
    **56.7** [LIT-BACKED: SmolLM2 instruct cards, 2025]. IFEval's floor is ~0
    (generative, strict verification), so it is above floor and discriminative
    ACROSS the whole 135M–1.7B range — better than the review's "iff above
    floor at R-2" prior suggested. Caveat: the card averages prompt-level and
    instance-level strict accuracy; the pinned harness must pick one (OLLv2
    uses both, reported separately) [LIT-BACKED: arXiv:2311.07911, 2023 — 25
    verifiable instruction types, ~500 prompts, strict/loose × prompt/inst].
  - MuSR: "few models achieve better than random performance" — the OLLv2
    docs' own words, at ALL scales it hosts [LIT-BACKED: OLLv2 about page,
    2024]. Exclude below R-3.
  - MATH Lvl-5 and GPQA: at ≤2B these sit at ~0 and ~chance respectively on
    the public leaderboard; **UNVERIFIED as specific numbers** (not fetched
    per-model this session) — but GSM8K 1.4–31.0 at our rungs bounds MATH
    Lvl-5 from above, and GPQA is designed to be expert-hard. Exclude below
    R-3 [EXTRAPOLATION].
- CONCLUSION (tempered per review — "floors out at 100M–2B" was too strong):
  **OLLv2 is the right R-3+ anchor family; at the programme's 100M–2B rungs its
  components are either at floor or too weakly discriminative to carry an index
  cell** — with the boundaries stated honestly: IFEval is usable from R-1
  (instruct hosts); MMLU-Pro at 1.7B is ABOVE floor (19.3 vs 10% chance, ~9 pp
  normalized headroom), so its R-3+ placement is a weak-discrimination
  judgement, NOT a demonstrated floor; BBH's near-floor status is unproven
  pending a pinned-harness computation (previous bullet); MATH/GPQA tiny-scale
  numbers remain unverified (§8.4). The rev-2 provisional table's R-3+
  placements survive as placement judgements, not as floor-validated facts
  [STIPULATED].

## 4. Contamination: what detection can and cannot do, and how sealed benchmarks are produced

**Detection limits (the review's skepticism is literature-confirmed).**

- LOAD-BEARING: simple variations of test data — paraphrase, translation —
  defeat n-gram/string-match decontamination: a 13B model trained on rephrased
  test sets reached GPT-4-level scores on MMLU/GSM8K/HumanEval while passing
  standard decontamination; their stronger LLM-based decontaminator then found
  8–18% of HumanEval overlapping in RedPajama-1T/StarCoder-Data, and
  contamination even inside GPT-3.5/4-generated synthetic data [LIT-BACKED:
  Yang, Chiang, Zheng, Gonzalez, Stoica, arXiv:2311.04850, 2023].
- LOAD-BEARING: contamination can be PROVEN (not just screened) from black-box
  log-probabilities via exchangeability — a contaminated model assigns higher
  likelihood to the benchmark's canonical ordering than to shuffles; works down
  to 1.4B models, 1,000-example sets, few duplications — but requires logprob
  access and duplication-rate knowledge, and a NEGATIVE result proves nothing
  [LIT-BACKED: Oren, Meister, Chatterji, Ladhak, Hashimoto, arXiv:2310.17623,
  2023 (ICLR 2024 — venue not restated on the arXiv page; UNVERIFIED as venue)].
- Design consequence [STIPULATED]: the §2.2 screener (n-gram + embedding) is a
  gross-leakage gate ONLY — the literature says paraphrase-level leakage passes
  it, which is exactly why the rev-2 design made the sealed evaluation (§2.2a)
  mandatory rather than optional. For OUR stores (which we control) the Oren
  test is inapplicable (it detects training-data memorization); the screener +
  authoring provenance rules carry that side. For DONOR WEIGHTS, the Oren test
  is a cheap, runnable diagnostic on any open comparator with logprob access —
  add it to the P3-D-SEAL toolbox.

**Producing a sealed/refreshed held-out benchmark (three verified recipes).**

- LOAD-BEARING (parallel-replica recipe): GSM1k built 1,000 NEW human-written
  problems matched to GSM8K on human solve rates, solution step counts, and
  answer magnitudes, kept the set private, and measured overfitting as the
  GSM8k→GSM1k gap: drops up to 8%, systematic across some model families,
  minimal at the frontier, with the gap correlating (Spearman r² = 0.36) with
  the model's probability of *generating* GSM8k items verbatim [LIT-BACKED:
  Zhang et al., arXiv:2405.00332, NeurIPS 2024 D&B].
- LOAD-BEARING (refresh recipe): LiveBench adds/updates questions monthly from
  fresh sources (competitions, arXiv, news), scores against objective ground
  truth without LLM judges, and versions each release; ICLR 2025 Spotlight
  [LIT-BACKED: White et al., arXiv:2406.19314, ICLR 2025]. The live site
  fetch returned no content this session (livebench.ai rendered empty to the
  fetcher) — current release ID **UNVERIFIED**; pin the release at P3-D-SEAL
  freeze from the GitHub tags, which the review itself cited.
- LOAD-BEARING (structural-resistance recipe): SWE-bench Pro's held-out set +
  strong-copyleft sourcing, verified in the prior fact sheet [LIT-BACKED:
  reports/lit-eval-benchmarks.md §3.5, arXiv:2509.16941, 2025].
- Recipe synthesis for P3-D-SEAL [STIPULATED]: (i) for D4/D5 procedural
  domains, a pinned generator FAMILY is the cheapest sealed producer (CLUTRR is
  literally built for this — generator + configurable splits [LIT-BACKED:
  arXiv:1908.06177, EMNLP 2019]) — but fresh seeds from a KNOWN generator are
  NOT sealing: anyone (including us) who has seen the generator can adapt to
  its distribution, so sealing requires maintainer-held generator secrecy or
  genuinely held-out generator families / rule-combinations reserved per
  release [STIPULATED per review]; (ii) for knowledge/instruction domains,
  GSM1k-style matched authoring with the difficulty-matching triple (solve
  rate, step count, answer magnitude) as the per-domain difficulty-calibration
  instrument; (iii) LiveBench-style versioning discipline — every refresh is a
  new version, never folded in (ASM-0812 verbatim).
- **CORRECTED READING of the GSM1k gap (the earlier draft misread this):**
  GSM1k observed frozen→sealed drops of *up to* 8% among the particular models
  it tested — systematic in some families, minimal at the frontier. That is a
  description of observed overfitting in one tested population, NOT a universal
  tolerance band for "honest" (uncontaminated) models; no published constant
  licenses a pre-set acceptable-gap band [LIT-BACKED: arXiv:2405.00332,
  NeurIPS 2024 D&B]. Any frozen-vs-sealed consistency band for our systems must
  be derived from OUR OWN calibration variance (P3-E-CAL seeds), and it serves
  only as a secondary overfitting DIAGNOSTIC — it is not the claim gate.
- **The claim gate itself [STIPULATED per review — supersedes any
  "directional consistency" phrasing]:** a W1-relevant claim passes the sealed
  evaluation only if S BEATS the resource-matched baseline ON THE SEALED
  RELEASE by a registered margin — i.e., the baseline family (P3-D-BASE) is run
  on the same sealed items under the same pinned harness, and the primary
  sealed endpoint is (S − B) ≥ δ_sealed with δ_sealed frozen in the prereg
  BEFORE unsealing. Directional consistency with the frozen suite is necessary
  but NOT sufficient: a frozen-suite win with weak or null sealed performance
  fails the gate. The protocol must additionally register: (a) custody and
  access rules for the sealed set; (b) ONE-SHOT use — each sealed release
  grades at most one claimed evaluation and is then burned; (c) post-evaluation
  disclosure of items and per-item outputs; (d) independent difficulty
  calibration per domain (the GSM1k matching triple is the verified instrument
  for that); (e) a no-feedback rule — anything learned from release N's
  disclosure may only inform claims graded against a fresh release N+1
  [STIPULATED].

## 5. Proxy-rung validity: when a cheap rung predicts a dearer one

The question P3-D-POWER and the G5 gate need answered: do R-0/R-1 measurements
predict R-2+? The literature's answer is **metric-dependent**, in a way that
directly shapes which metrics enter low rungs.

- LOAD-BEARING: apparent emergence (sharp capability jumps that would make
  small-scale results non-predictive) is largely an artifact of nonlinear/
  discontinuous metrics (exact match, MC accuracy); under continuous metrics
  the same models improve smoothly and predictably [LIT-BACKED: Schaeffer,
  Miranda, Koyejo, arXiv:2304.15004, 2023 (NeurIPS 2023 — venue not restated
  on the arXiv page)].
- LOAD-BEARING: the mechanism for WHY downstream MC accuracy resists scaling
  prediction: performance is computed from log-likelihoods through a chain of
  transformations (normalize, compare against specific incorrect choices) that
  progressively degrades the statistical relationship with scale — probability
  mass on the INCORRECT options fluctuates unpredictably [LIT-BACKED:
  Schaeffer, Schoelkopf, Biderman et al., arXiv:2406.04391, 2024].
- LOAD-BEARING: nevertheless, aggregate capabilities ARE predictable
  observationally: ~100 public models define a low-dimensional capability
  space in which "emergent" phenomena, agent performance, and even the value
  of post-training techniques (CoT, self-consistency) follow smooth sigmoids
  predictable from smaller/weaker models [LIT-BACKED: Ruan, Maddison,
  Hashimoto, arXiv:2405.10938, NeurIPS 2024 spotlight].
- Corroborating instance: BBH tasks that looked flat ("emergent") under
  direct prompting became smoothly improvable with CoT — the metric/method,
  not the underlying capability, produced the cliff [LIT-BACKED: Suzgun et
  al., arXiv:2210.09261, 2022].
- Design consequences [STIPULATED]:
  1. **R-0/R-1 components should be continuous or minimal-pair-logprob metrics**
     (held-out LM loss; BLiMP/EWoK forced-choice logprob). Precisely stated
     (the earlier draft's "carry predictive signal upward" was too strong): the
     cited results show continuous metrics AVOID the metric-induced
     discontinuity artifact and that some observational relationships are
     predictable — they do NOT by themselves license cross-rung prediction for
     BLiMP/EWoK, which must be validated empirically (the G5 two-size
     confirmation IS that validation, not a formality). MC accuracy at a rung
     where the model is near floor carries almost no predictive signal. This
     supports (not "validates") rev-2's R-0 row (LM loss + BLiMP/EWoK) and the
     MMLU-cloze drop [STIPULATED per review].
  2. **Proxy-rung validity must be CLAIMED per metric family, not per suite**:
     the G5 two-size confirmation should test the margin's direction on the
     continuous metrics first, and treat cross-rung MC-accuracy extrapolation
     as unsupported by default.
  3. For P3-D-POWER: Δ_max computations at R-1 on near-floor MC benchmarks are
     unstable (the baseline accuracy term a_b^cov is noise near chance). Two
     corrections registered here [STIPULATED per review]: (a) the below-floor
     EXCLUSION criterion must itself be registered from P3-E-CAL calibration
     data BEFORE campaign results are seen — components may not be dropped
     post hoc after looking at results; (b) the identity Δ_B = κ_B × Δ_covered
     and its max-gain bound κ(1 − a_cov) are stated on the RAW-accuracy scale —
     under chance/ceiling normalization the maximum covered-item contribution
     must be divided by the relevant normalization denominator and carried
     through the registered domain/benchmark weights, with uncertainty in κ and
     in covered-subset accuracy propagated. P3-D-POWER must restate the bound
     on the normalized scale before quoting any power number.

## 6. Per-benchmark floors/ceilings at tiny scale (the D1–D7 evidence table)

The rev-2 provisional domain table (programme doc §1.1), now annotated with
verified floors/ceilings. "Tiny scale" = the programme's 135M–1.7B hosts (and,
for D1, the BabyLM ≤100M-word training regime as the closest published probe
of very small capability).

| Benchmark | Verified construction | Floor/ceiling at tiny scale | Verdict for the index |
|---|---|---|---|
| **BLiMP** | 67 paradigms × 1,000 minimal pairs, forced-choice by sentence logprob, chance 50% [LIT-BACKED: arXiv:1912.00582, TACL 2020] | GPT-2 81.5 / LSTM 69.8 / 5-gram 61.2 / human 88.6 individual, 96.4 aggregate [LIT-BACKED: aclanthology.org/2020.tacl-1.25 via paper PDF]; BabyLM-2024 10M-word baselines 69.8, best 81.2; 100M-word best 86.1 [LIT-BACKED: arXiv:2412.05149, CoNLL 2024] | **KEEP at R-0/R-1 (D1)**: discriminative across the whole tiny range; candidate reference anchors exist but 88.6 (individual) and 96.4 (aggregate) are DIFFERENT estimands — register ONE, with uncertainty + clamping rule (§2, §8.1) |
| **EWoK** | 4,374 items, 11 domains, minimal pairs-of-pairs (context×target), chance 50%, logprob-scored [LIT-BACKED: arXiv:2405.09605, TACL 2025 + ewok-core pages] | All tested 1.3B–70B models below human; social domains highest, physical/spatial lowest [LIT-BACKED: same]; BabyLM-2024: baselines 50.7–51.9 (≈chance), best submission 58.4 — "most submissions perform near chance" [LIT-BACKED: arXiv:2412.05149] | **KEEP at R-0 with a floor warning**: at ≤100M-word training it is nearly floored; expect low headroom at 135M-param scale too; its value is the domain vector (physical/spatial deficit is exactly a world-knowledge probe), not the scalar [STIPULATED] |
| **CLUTRR** | Procedural kinship-graph generator; systematic (held-out rule combinations) + robustness splits; text vs symbolic-graph input arms [LIT-BACKED: arXiv:1908.06177, EMNLP 2019; licence CC-BY-NC-4.0 per reports/lit-eval-benchmarks.md] | Paper-era: BERT/MAC on text ≪ GAT on symbolic graphs for generalization+robustness [LIT-BACKED: same]. Published floors for MODERN small LMs (zero/few-shot, 135M–2B): **not found this session — UNVERIFIED/OPEN** | **KEEP (D4)**, generator-pinned; but the R-1 floor must be MEASURED by us in P3-E-CAL, not assumed. NC licence constrains artifact redistribution [LIT-BACKED: fact sheet §1.1] |
| **RuleTaker / ProofWriter** | NL rulebases; fine-tuned transformers reach 99% in-distribution and 95%+ on deeper unseen depths [LIT-BACKED: arXiv:2002.05867, IJCAI 2020]; ProofWriter adds proof generation + abduction, +9% over RuleTaker, depth/OOD generalization, open+closed world variants [LIT-BACKED: arXiv:2012.13048, Findings ACL 2021] | The 95–99% figures are FINE-TUNED ~355M-class encoder/T5 models — i.e., the tasks are LEARNABLE at small scale with supervision; zero/few-shot floors for small decoder LMs: **not published where we looked — UNVERIFIED/OPEN** | **KEEP (D4)** with the fine-tune-vs-prompt distinction made explicit in the index pin: as a PROMPTED index component it will likely floor at R-1; as a diagnostic with light adaptation it has near-100% ceiling — the gap itself is informative [STIPULATED] |
| **FOLIO** | 1,430 expert-written conclusions / 487 premise sets, FOL-verified; labels True/False/Unknown (3-way, chance ≈33%); CC-BY-SA-4.0 [LIT-BACKED: arXiv:2209.00840 + aclanthology.org/2024.emnlp-main.1229 (EMNLP 2024) + github.com/Yale-LILY/FOLIO] | "A subset remains a challenge for GPT-4" [LIT-BACKED: same] — but GPT-4 struggling is NOT floor evidence for tiny models; ≈chance at ≤1.7B is an unmeasured [EXTRAPOLATION], to be tested in P3-E-CAL if ever used | **R-3+ or oracle-diagnostic only**; too hard as a tiny-scale index component; its NL↔FOL pairs are valuable P3-LR-PARSE material [STIPULATED] |
| **IFEval** | 25 verifiable instruction types, ~500 prompts, strict/loose × prompt/inst metrics, floor ≈0 [LIT-BACKED: arXiv:2311.07911, 2023] | 135M-Instruct 29.9 (card avg), 1.7B-Instruct 56.7 [LIT-BACKED: SmolLM2 cards, 2025] | **PROMOTE: usable from R-1** (not just R-3 as the provisional table had it) on instruct hosts; pin ONE metric variant [STIPULATED] |
| **MMLU-Pro** | 10-choice (chance 10%), reasoning-heavier, 16–33% harder than MMLU, prompt sensitivity 4–5%→2% [LIT-BACKED: arXiv:2406.01574, NeurIPS 2024 D&B Spotlight] | 1.7B-Instruct 19.3; Llama-1B 12.7 (≈3 pp over chance) [LIT-BACKED: SmolLM2-1.7B card, 2025] | **R-3+ only**, confirming the rev-2 placement and the MMLU-cloze drop |
| **BBH** | 23 hard BIG-Bench tasks chosen where prior models < average human rater; CoT lifts substantially (Codex > human on 17/23); few-shot-no-CoT "substantially underestimates" capability [LIT-BACKED: arXiv:2210.09261, 2022] | 135M-Instruct 28.2 / 1.7B-Instruct 32.2 (3-shot, lighteval card) — cross-harness comparability with OLLv2's 24-subtask floor inventory NOT established (§3); consistent with weak discrimination, near-floor UNPROVEN pending pinned-harness computation [LIT-BACKED: SmolLM2 cards; inference tempered per review] | **R-3+**; also note BBH scores are STRATEGY-confounded (CoT vs not) — the index pin must fix the prompting strategy per rung [STIPULATED] |
| **BBEH** | Each BBH task replaced by a harder same-capability probe because "state-of-the-art models achieve near-perfect scores on many BBH tasks"; best general-purpose model 9.8 harmonic-mean acc, best reasoning model 44.8 [LIT-BACKED: arXiv:2502.19187, 2025] | Floors out even for frontier general models | **NOT for the tiny-scale index at all**; candidate only for a far-future R-4+ version [STIPULATED] |
| **GSM8K** | (fact sheet, verified 2026-07-10) 1,319-item test, EM metric [LIT-BACKED: reports/lit-eval-benchmarks.md §2.9] | 1.4 / 3.2 / 31.0 base (5-shot); 48.2 1.7B-Instruct [LIT-BACKED: same + 1.7B card] | **D5 enters at the ≥1B rung**; below that it is a floor-cell that only dilutes the index; ALSO contamination-suspect (GSM1k §4) — pair it with the sealed D5 generator leg [STIPULATED] |

Cross-cutting note: chance floors are verified for the MC benchmarks in this
table (50% BLiMP/EWoK; ~33% FOLIO; 10% MMLU-Pro; per-subtask 2–19-choice
BBH/MuSR). That is what the accuracy normalization needs FOR THOSE COMPONENTS
ONLY — it is not "every chance floor for the index": the generative
lower_bound = 0 (IFEval/GSM8K/MATH) is a convention, not a measured floor;
held-out LM loss and any calibration/abstention/robustness components have no
chance floor at all and need registered metric-specific transforms (§2); and
proposed domain components outside this table have no floor entry yet. The
CEILING side has candidate anchors only for BLiMP (88.6/96.4 — different
estimands, §2) — every other reference must be pinned by P3-D-INDEX from named
reference models, with estimand, uncertainty, clamping rule, and update policy
registered [STIPULATED].

## 7. What actually beat matched baselines (skeptical accounting)

The review asked every lit-bead to judge wins under their accounting. In the
evaluation-methodology literature itself the load-bearing "wins" are:

- **Compute-optimal test-time scaling beat best-of-N and beat bigger models at
  matched FLOPs**: >4× efficiency over best-of-N; a smaller model with
  compute-optimal test-time strategies outperformed a 14× larger model in
  FLOPs-matched evaluation [LIT-BACKED: Snell, Lee, Xu, Kumar, ICLR 2025 —
  verified BOTH at proceedings.iclr.cc (the review's exact link resolves to
  this paper) and arXiv:2408.03314]. Accounting: FLOPs-matched, but on
  MATH-class tasks with a trained verifier/reviser — the "matched" side does
  not include verifier training compute. The 14× result is also CONDITIONAL:
  it holds where the smaller model already has non-trivial success on the
  task, and depends strongly on prompt difficulty and verifier quality — it is
  not a blanket small-model win [LIT-BACKED: arXiv:2408.03314]. This is the
  strongest justification for the frontier-builder's clause (iv) — adaptive
  test-time compute as a comparator capability that MUST BE CONSIDERED and
  included where task-appropriate and budget-feasible (not unconditionally
  mandatory for every frontier) — and simultaneously a lifecycle-ledger
  cautionary tale (KOT-LIFE/1 must log the verifier's training cost on OUR
  side too) [STIPULATED].
- **GPT-BERT beat the BabyLM baselines at matched data budget** (10M/100M
  words, same eval pipeline): BLiMP 81.2 vs 69.8 baseline at 10M [LIT-BACKED:
  arXiv:2412.05149, CoNLL 2024]. Accounting: matched words, NOT matched
  training FLOPs — the findings paper itself reports a strong FLOPs–performance
  relationship across submissions, so part of the win is compute [LIT-BACKED:
  same]. Lesson for P3-D-BASE: data-matched ≠ compute-matched; our
  tuning-symmetry rule (total tuning compute) is the right axis.
- **CLUTRR's GNN-over-symbolic-graphs beat BERT-over-text** on systematic
  generalization and robustness [LIT-BACKED: arXiv:1908.06177, EMNLP 2019].
  Accounting: the GNN receives ORACLE symbolic input — this is precisely an
  `oracle-diagnostic` win in our terminology, not an NL-input win; it is the
  2019 version of our own l3a/a5 lesson (exact machinery inside the wall,
  boundary unpaid). It motivates the H-GNN family AND its ASM-0814 gating in
  one datum [STIPULATED].
- **Nothing in the composite-index literature shows a small model "beating"
  matched baselines via indexing choices** — the reverse: metabench shows most
  legacy-suite variance is one factor (§2), and GSM1k/rephrase results show
  apparent wins evaporating on sealed replicas (§4). The methodological moral
  for W1: index construction and sealing are where ILLUSORY wins are
  manufactured or destroyed, which is why P3-D-INDEX/P3-D-SEAL gate every
  W1-relevant experiment [STIPULATED].

## 8. Open questions Phase-1 must resolve (this review's residue)

1. **Reference pinning** (P3-D-INDEX): only BLiMP has verified human reference
   scores, and even those are two DIFFERENT estimands (88.6 individual / 96.4
   aggregate), noisy under particular prompts/harnesses — not true ceilings
   (§2). Freeze per component: the reference estimand, its score + uncertainty,
   the above-reference/clamping rule (naive clamping saturates; no clamping
   allows scores > 1), and the version-bump policy when a reference updates.
   Also: registered metric-specific transforms for LM loss / calibration /
   abstention / robustness, which have no chance-to-ceiling normalization (§2).
2. **Domain weights and the scalar** (P3-D-INDEX): equal-weight across D1–D7
   vs coverage-proportional; also benchmark weights within domain,
   missing-domain handling, and cross-rung comparability — all NORMATIVE
   registered choices (§1, §2), none a statistical consequence of the cited
   literature; metabench's one-factor result argues the scalar should be
   de-emphasized in favor of the vector + per-domain LCBs.
3. **Prompting-strategy pin** (P3-D-INDEX): BBH (and D4 suites) move
   enormously with CoT; per-rung strategy must be frozen or the index is
   gameable via strategy shopping — a threat-model row (P3-D-THREAT co-input).
4. **Tiny-scale D4 floors are unmeasured in the literature** (P3-D-POWER /
   P3-E-CAL): no published CLUTRR/ProofWriter zero-shot numbers at 135M–1.7B
   were found; the calibration run must measure them before margins δ_k are
   set. Fine-tuned-vs-prompted protocol for D4 must be decided (§6).
5. **Sealed gate margin + secondary band** (P3-D-SEAL): register δ_sealed —
   the sealed-side S-vs-baseline margin that is the actual claim gate (§4) —
   before unsealing; separately, derive any frozen-vs-sealed consistency band
   from OWN variance estimates (P3-E-CAL seeds). GSM1k publishes observed
   drops (up to 8%, specific to its tested model population), NOT a usable
   honest-model tolerance constant (§4).
6. **Proxy-rung claims per metric family** (P3-D-INDEX + G5): formalize
   "continuous metrics extrapolate, MC accuracy does not" into the analysis
   plan's cross-rung inference rules.
7. **Sealed producer independence** (P3-D-SEAL): generator-based sealing is
   cheap but WE author the generator, and fresh seeds from a known generator
   are not sealing (§4) — decide among maintainer-held generator secrecy,
   genuinely held-out generator families / rule-combinations per release, and
   cross-vendor generation; plus the operational rules §4 registers (custody,
   one-shot use, post-eval disclosure, no-feedback-across-releases, per-domain
   difficulty calibration). The independence question is the one governance
   question the literature cannot answer for us.
8. **CLUTRR licence** (P3-D-INDEX): CC-BY-NC-4.0 — eval-internal use is fine;
   no redistribution of derived artifacts; confirm the sealed refresh
   (our own generator re-implementation vs their generator) doesn't create a
   licensing dependency.

## 9. Phase-1 hand-off — the design beads this review recommends the coordinator create

- **P3-D-INDEX** — freeze KOT-AI-INDEX/2's concrete pins (suite membership,
  domain assignment, normalization constants, references, harness+prompt
  strategy, analysis plan). *De-risked here (partly):* the accuracy
  normalization has a verified working precedent (OLLv2 formula incl.
  per-subtask floors); chance floors are verified for the §6 MC components
  (NOT for the whole index — generative 0 is a convention; LM loss et al. need
  their own transforms, §2/§6); the D1–D7 placements are PARTIALLY
  floor-evidenced — verified anchors for D1 (BLiMP/EWoK), IFEval, GSM8K,
  MMLU-Pro; BBH near-floor unproven cross-harness (§3); MATH/GPQA and prompted
  CLUTRR/ProofWriter floors unverified; D2/D3/D7 not comprehensively
  validated — the placements are judgements pending P3-E-CAL, not validated
  facts; mean-win-rate aggregation is ruled out with cause. *Still open:*
  metric-specific transforms, reference estimands + uncertainty + clamping
  policy, fixed registered weights, registered floor/exclusion criteria,
  abstention scoring, strategy pin, D4 fine-tune-vs-prompt protocol, full
  D1–D7 calibration (§8.1–4).
- **P3-D-SEAL** — the sealed-eval protocol. *De-risked here:* three verified
  production recipes (procedural generator with secrecy/held-out families —
  fresh seeds alone insufficient / GSM1k-style matched authoring with a
  difficulty-matching triple / LiveBench versioned refresh), a verified reason
  screening alone cannot certify fairness (paraphrase evasion), one runnable
  extra tool (Oren logprob test for open donor weights), and the corrected
  gate shape: sealed-side baseline comparison with a registered margin
  δ_sealed as the claim gate, frozen-vs-sealed gap as a secondary diagnostic
  only — GSM1k's up-to-8% observed drops are NOT a tolerance anchor (§4).
  *Still open:* δ_sealed and the own-variance band; producer independence and
  generator secrecy; custody / one-shot-use / disclosure / no-feedback
  operational rules; per-domain difficulty calibration (§8.5, 8.7). These are
  useful recipes plus a gate specification — not yet a production protocol;
  that is the bead's job.
- **P3-D-POWER** — the coverage × max-gain power analysis. *The least
  de-risked hand-off.* De-risked here: chance floors for the §6 MC components
  are verified, and the metric-dependence result tells it which components
  support cross-rung extrapolation at all. *Still open (all blocking):*
  restating the Δ_max bound on the NORMALIZED scale — the raw-scale
  κ(1 − a_cov) form is not valid under chance/ceiling normalization (§5.3);
  a floor/exclusion criterion registered from calibration data, not post hoc;
  uncertainty in κ and covered-subset accuracy; suite covariance; registered
  δ values; the actual sample-size/power computations; and the unpublished
  tiny-scale D4 floors P3-E-CAL must measure (§8.4).
- **P3-D-BASE** — the baseline-family spec. *De-risked here:* adaptive
  test-time compute is verified as a real, large, FLOPs-matched baseline
  capability (Snell et al. at the review's exact ICLR-2025 link) — but the
  result is conditional (non-trivial base success, verifier quality; §7), so
  the frontier-builder clause (iv) reads: mandatory to CONSIDER, include where
  task-appropriate and budget-feasible — not unconditionally mandatory for
  every frontier; and the data-matched-vs-compute-matched distinction (BabyLM)
  confirms total-tuning-compute symmetry over config counts. *Still open:*
  this bead does not by itself specify credible rung baselines — it stays
  dependent on P3-LR-RAG, P3-LR-TINY and P3-D-FRONTIER for per-budget
  comparator pinning.

(P3-D-THREAT takes §8.3 — strategy-shopping — as a new enumerated gaming
channel; not a bead this review spawns, noted for its co-input.)

## 10. Source verification register

Machine-readable staging: `docs/next/lit/EVAL.sources.jsonl` (one JSON object
per source; the coordinator ingests centrally — nothing here touched kb/).

**Verified at primary venue this session (2026-07-11) — 25 distinct sources,
27 `verified:true` JSONL records** (the earlier "24" undercounted; EWoK and
FOLIO each carry one additional corroborating record — ewok-core pages and the
Yale-LILY repo — and the two OLLv2 docs pages are separate records): HELM
(arXiv:2211.09110/TMLR); OLLv2 about + normalization (2 HF docs pages); CLUTRR
(arXiv:1908.06177); LiveBench (arXiv:2406.19314, ICLR 2025); BLiMP
(arXiv:1912.00582/TACL + score table via paper PDF/anthology); EWoK
(arXiv:2405.09605/TACL 2025 + ewok-core corroboration); BabyLM-2 findings
(arXiv:2412.05149 HTML, baseline tables read directly); ProofWriter
(arXiv:2012.13048); RuleTaker (arXiv:2002.05867); FOLIO (arXiv:2209.00840 +
aclanthology 2024.emnlp-main.1229 + Yale-LILY GitHub); IFEval
(arXiv:2311.07911); MMLU-Pro (arXiv:2406.01574); BBH (arXiv:2210.09261); BBEH
(arXiv:2502.19187); Yang et al. rephrase-contamination (arXiv:2311.04850);
GSM1k (arXiv:2405.00332); Oren et al. (arXiv:2310.17623); Schaeffer mirage
(arXiv:2304.15004); Schaeffer downstream-prediction (arXiv:2406.04391); Ruan
observational scaling (arXiv:2405.10938); Snell test-time compute
(proceedings.iclr.cc hash + arXiv:2408.03314); metabench (arXiv:2407.12844);
SmolLM2-1.7B-Instruct card; SmolLM2-135M-Instruct card.

**UNVERIFIED / partial (each flagged inline; 6 `verified:false` JSONL
records):** HELM mean-win-rate internal detail (secondary only); livebench.ai
current release (site rendered empty); BBH/mirage/Oren publication venues
beyond arXiv (papers verified, venue lines not — carried as partial fields
INSIDE the `verified:true` records, see convention below); MATH-Lvl-5/GPQA/MuSR
per-model tiny-scale numbers (component list verified via OLLv2 docs; per-model
floors extrapolated — each now carries its own `verified:false` record,
including a new MATH record added at this revision); crfm.stanford.edu/helm
live page (title-only render; existence confirmed, content not).

**Ledger convention (made explicit per review):** `verified:true` attests the
record's `claim` field at the listed URL on 2026-07-11; a venue string flagged
"not re-verified" inside such a record is a partial field outside that
attestation. Extrapolated numbers with no fetched source always get their own
`verified:false` record rather than riding inside a verified one.

**Inherited from the in-repo fact sheet (verified 2026-07-10, not re-verified):**
the SmolLM2 base-card nine-benchmark table; GSM8K/ARC/OpenBookQA/HellaSwag/
CSQA/WinoGrande/PIQA/MMLU/TriviaQA canonical facts; HumanEval/MBPP/SWE-bench
lineage incl. the Verified deprecation and SWE-bench Pro
[LIT-BACKED: reports/lit-eval-benchmarks.md, 2026-07-10].
