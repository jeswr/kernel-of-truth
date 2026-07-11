# P3-LR-TINY — Tiny-Model Training + Small-Scale Scaling Laws

**Kernel of Truth Programme-3, Phase-0 literature review.**
Author: Fable (Claude Fable 5, literature-researcher discipline), 2026-07-11.
Bead: `kernel-of-truth-s55r.11` (P3-LR-TINY, programme rev-2 §5 Phase-0 table).
Feeds (Phase-1): **P3-D-GU** (ground-up R-0 architectures + the ≥3-point sweep
protocol, §3.5/ASM-0815), **P3-D-BASE** (co: baseline pins per rung + the R-0 twin
recipe + tuning-symmetry rules, §2.3/ASM-0812).

**Epistemic contract.** Every load-bearing line carries [MEASURED|STIPULATED|EXTRAPOLATION];
literature claims carry `[LIT: <id>]` keys into `docs/next/lit/TINY.sources.jsonl`
(one JSON object per source; `verified:true` = primary page fetched by me 2026-07-11 at the
URL given — NOT a claim that every body figure was independently re-checked; where a
specific number is load-bearing its provenance is stated in-line; `verified:false` =
carried from a prior verified review (EVAL, same repo) — flagged in-line as
UNVERIFIED-THIS-PASS). KB/lit records are recall infrastructure, not evidence; nothing
here amends any registry object. Prior-failure judgements (capability-limited vs
fundamental) are §8's explicit deliverable.

**Dedup statement (what already exists; this review builds on, does not repeat):**
- `docs/next/lit/EVAL.md` (2026-07-11) — owns the **metric side** of proxy-rung
  validity: emergence-as-metric-artifact (Schaeffer 2304.15004), observational
  scaling (Ruan 2405.10938), BLiMP/EWoK floors at tiny scale, the BabyLM-2024
  eval-pipeline numbers, and the GPT-BERT *accounting caveat* (data-matched ≠
  compute-matched). §6 below cites those carried, and adds the **training side**:
  which *training decisions* made at tiny scale transfer upward, and how to design
  the sweeps.
- lit-KB (`kb/records/`, 552 records) — the tiny-scale keyword hits there
  (Pythia/TinyStories/SmolLM mentions) are **incidental**: they are
  architecture-seam/interp records (SAEs, codebook features, latent reasoning) in
  which those models are *subjects*, not training-recipe or scaling-law sources.
  The KB does hold kNN-LM (1911.00172) and RETRO (2112.04426) as seam records;
  §4.6 builds on them as interface-at-small-scale prior art. New sources found
  here are staged in `TINY.sources.jsonl` for the coordinator's central ingest —
  **no KB shard/index is mutated by this bead** (governance).
- `reports/lit-llm-injection-priorart.md`, `reports/lit-eval-benchmarks.md` — rule
  injection and benchmark fact-sheets; not re-covered.
- No `docs/`, `docs/research-plan/`, or `reports/` document covers training recipes
  at 1M–2B, scaling-law fitting practice, µP/HP-transfer, seed-variance methodology,
  or compute-matched twin construction — that is this document's net-new ground.

---

## 0. Executive verdict (one paragraph)

Training good tiny models is now a **strong-recipe-priors, unsolved-comparison**
field. The recipe side offers strong conditional priors, not a validated optimum:
coherent generation is reachable below 10M parameters on simplified distributions
[LIT: tinystories-2023]; the NanoGPT speedrun cut wall-clock to GPT-2-124M-quality
validation loss ~34× on fixed 8×H100 hardware — a BUNDLED community result
(optimizer + architecture + kernels + precision + objective + hardware-specific
engineering changed together; per-component contributions unmeasured)
[LIT: nanogpt-speedrun, muon-scalable-2025]; and at sub-billion scale architecture
shape matters again — MobileLLM's combined deep-thin design package beats prior
same-size models by 2.7–4.3 pp at 125M/350M, a model-level result in which shape is
one factor among several [LIT: mobilellm-2024].
The comparison side is where programmes die, and the literature is unusually explicit
about it: small-scale scaling-law *fits* are fragile to last-layer FLOP accounting,
warmup, optimizer tuning, and even the fitting procedure itself [LIT: porian-2024,
chinchilla-replication-2024]; released "small" anchors like SmolLM2-1.7B are trained
~6,500 tokens/param — ~325× past Chinchilla-optimal — so **no academic-budget twin can
be compute-matched to a released anchor**; twin claims must be scoped to
from-scratch-vs-from-scratch [LIT: smollm2-2025, chinchilla-2022; STIPULATED]. For the
§3.5 direction protocol, the closest external analogue is DataDecide — a
pretraining-DATA-selection study, not an interface-intervention one: ranking candidate
corpora at ONE small scale (150M) predicts the 1B-scale winner in ~80% of comparisons,
and *none of eight scaling-law extrapolation methods beat that single-scale ranking* —
with continuous likelihood metrics as the best proxies and 3 seeds per config
[LIT: datadecide-2025]. That is analogical support for cheap R-0/R-1 decision-making
(small-proxy decisions can transfer; continuous metrics are the best proxies) plus a
caution that even in its favourable domain ~20% of decisions flipped at 8× scale — it
does NOT validate interface-effect sweeps, which is why the pre-registered read must be
the DIRECTION of the interface effect across a µP-parameterized, seed-replicated,
≥3-point sweep and why P3-E-GU-1/G5 must create the transfer evidence internally — and
one tiny null is not a family kill (Toolformer observed tool-use benefit emerging only
around 775M within one lineage — suggestive of a capacity threshold for LEARNED
interface *use*, though scale co-varies with base capability and call filtering — while
kNN-LM/RETRO show retrieval interfaces helping in their specific tested configurations,
neither resource-matched) [LIT: toolformer-2023, knnlm-2019, retro-2021;
EXTRAPOLATION: whether kot-interfaces behave like learned tool-use or like post-hoc
retrieval is exactly what P3-E-GU-1 measures, ASM-0815].

---

## 1. What the programme needs from this review

The consumers and their open questions [MEASURED: programme doc rev-2, restated]:

- **P3-D-GU** (§3.5): train small hosts from scratch with the symbolic interface
  present from step 0, at R-0 (1–30M, TinyStories-class data) then R-1 (100–200M,
  SmolLM2-135M anchor); training compute matched to a from-scratch twin (§2.3(v));
  the pre-registered read is the **direction of the interface effect across ≥3
  widths or token budgets**: monotonically-shrinking-to-zero kills, flat-negative
  kills, growing-with-scale promotes even from a negative absolute base
  [STIPULATED: ASM-0815]. Budget ~15–75 GPU-h (§3.6).
- **P3-D-BASE** (co, §2.3): baseline pins per rung, the R-0 twin recipe, and
  tuning symmetry binding on **total tuning compute** with a fixed pre-registered
  selection rule [STIPULATED: ASM-0812].
- Internal measured context this review must not contradict: the one tiny-scale
  end-task positive (SmolLM2-135M + kernel-verify-retry beats 1.7B-alone by +0.1507
  at ~10% cost) is formal-input, alignment-confounded [MEASURED:
  registry/verdicts/f2b-replicate.json + its assessment]; text-delivered grounding
  measured net-harmful at every scale tested [MEASURED: nsk1 g2d, exploratory];
  and P3-E-CAL will calibrate the framework on 135M/360M/1.7B pure-neural models
  (§2.4). Nothing at R-2+ has been measured — the programme has NO internal
  evidence yet on whether its own tiny results predict upward; §6 is therefore a
  literature question with a pre-registered internal test (P3-E-GU-1/G5).

---

## 2. SQ1 — state of the art in tiny-model training, 1M–2B

### 2.1 The R-0 regime exists because data distribution is a free variable

TinyStories is the founding datum of the R-0 rung: on a synthetic corpus restricted
to a 3–4-year-old's vocabulary, models **below 10M parameters** (even one
transformer block) generate fluent, multi-paragraph, consistent stories — where
GPT-2-124M-class models on ordinary data "can rarely generate coherent and
consistent English text" [LIT: tinystories-2023]. Two lessons, one per direction:

- POSITIVE: capability-per-parameter is strongly distribution-dependent, so an R-0
  rung on simplified data can exercise real composition/consistency machinery at
  1–30M — this is the literature license for R-0's existence [LIT: tinystories-2023].
- CAUTION: the same fact means R-0 results are **envelope-bound to the training
  distribution**. TinyStories evaluation is GPT-4-graded (judge-based grammar/
  creativity/consistency scores) [LIT: tinystories-2023] — a judge instrument our
  programme only trusts within a measured style-leak margin [MEASURED:
  truthstyle-2x2 PASS at ±0.10, instrument-only]. R-0 endpoints for P3-E-GU-1
  should prefer the continuous/minimal-pair metrics EVAL §5 registered, not
  judge scores [STIPULATED; carried: EVAL.md §5].

### 2.2 BabyLM: two years of community-scale recipe search at 10M–100M words

- 2023 (>30 submissions, 10M/100M strict + loose tracks): winner LTG-BERT
  (architecture change); **curriculum-learning submissions were "largely
  unsuccessful, though some showed modest improvements"**; other wins came from
  shorter sequences and knowledge distillation [LIT: babylm-2023-findings].
- 2024 (31 submissions): winner GPT-BERT, a **hybrid masked+causal objective**
  usable afterwards as either a causal or masked LM [LIT: gpt-bert-2024,
  babylm-2024-findings]; best submissions changed data, objective, AND
  architecture; the findings report "a strong relationship between training FLOPs
  and average performance across tasks" — i.e. part of every "win" was compute
  [LIT: babylm-2024-findings]; no submission beat baselines on the multimodal
  track. (EVAL.md owns the eval-side numbers and the data-matched≠compute-matched
  accounting caveat; not repeated.)

Reading for P3-D-GU [STIPULATED — narrowed]: the direct curriculum evidence is ONE
cycle's submissions ("largely unsuccessful, though some showed modest improvements",
2023); the 2024 cycle's wins were simply located elsewhere (objective + architecture
+ data quality) rather than re-testing curricula head-on. That is a single-cycle
prior against cheap DEVELOPMENTAL/NL-ordering curricula at 10M–100M words — not a
replicated null — so H-GU variant staging should deprioritise BabyLM-style
curriculum arms in favour of interface/objective variants (the §3.5 list). It says
nothing about the programme's expressly scoped **synthetic curriculum over rule
depth / paraphrase diversity** variant (rev-2 §3.5): a different intervention class,
which stays in scope.

### 2.3 The speedrun result: large bundled recipe headroom at R-1, publicly documented

The NanoGPT speedrun holds the strongest practical result at exactly our R-1 scale:
training a 124M model to GPT-2-quality validation loss (≤3.28 on FineWeb, 8×H100)
fell from the llm.c 45-minute baseline to **~1.32 minutes — ~34× faster wall-clock
on that fixed hardware — across 84 community records since May 2024** (leaderboard
snapshot at the pinned commit), via the Muon
optimizer, rotary embeddings, QK-normalization, ReLU² activations, FlashAttention-3
with long-short sliding windows, FP8/bf16 precision splits, multi-token prediction,
and value/bigram-hash embeddings; records require statistical validation that val
loss stays ≤3.28 [LIT: nanogpt-speedrun — a moving leaderboard; provenance pinned in
the sources ledger to repo commit `edf47a05a12062d661c4cfd4eef848c5ab5bed32`
(master HEAD 2026-07-03, README re-fetched at that commit 2026-07-11; record #84 =
1.32 min, 2026-05-21)]. CHARACTERISATION CAVEAT: this is a BUNDLED,
hardware-specific engineering result — optimizer, architecture, kernels, precision,
embeddings, attention pattern, prediction objective, and 8×H100-specific tuning
changed together across records. It does NOT show that a plain GPT-2 twin is 34×
less compute-efficient, and no component is individually validated as optimal at
5–30M or with a symbolic interface attached. Muon itself is the one separately
measured component: ~2× compute-efficiency vs AdamW at compute-optimal settings,
scaling to a 3B/16B-MoE trained on 5.7T tokens once weight decay + per-parameter
update-scale are added [LIT: muon-scalable-2025].

LOAD-BEARING consequence for P3-D-BASE [STIPULATED]: **an untuned "plain GPT twin"
leaves large, publicly documented recipe headroom on the table** (order-of-magnitude
wall-clock at 124M in the bundled record; per-component magnitudes not
decomposable). The twin recipe must be pinned to a named modern reference
(modded-nanoGPT-class: Muon + rotary + QK-norm at minimum) as a CONDITIONAL DESIGN
PRIOR — the best-documented modern starting point, not a validated optimum — with
the SAME recipe used verbatim for interface and plain arms and the pin recorded in
the prereg. The pin's job is cross-arm SYMMETRY, not optimality: without it, any
"interface-present twin beats plain twin" result is attributable to recipe slack,
exactly the unmatched-compute pathology this review was told to be skeptical of.
NOTE: an identical recipe is necessary but NOT sufficient for compute matching —
the interface arm can change parameter count, token count, sequence length,
objectives, and auxiliary execution; §4.1's twin-compute ledger covers what the
recipe pin cannot.

### 2.4 Architecture priors at sub-billion scale

At 125M/350M, MobileLLM's COMBINED design package (deep-thin shape + embedding
sharing + grouped-query attention) improves +2.7/+4.3 pp average accuracy over prior
same-size SOTA; block-wise weight sharing adds a further +0.7/+0.8
[LIT: mobilellm-2024]. The headline pp figures are model-level improvements of the
whole package over prior models — NOT a clean single-factor causal estimate of
deep-thin-vs-wide-shallow; the paper's internal design exploration supports
deep-thin directionally within its setting. Read against Kaplan et al.'s finding
that shape has minimal impact within tested ranges [LIT: kaplan-2020], the
conservative conclusion is that shape choices are consequential at sub-billion
scale in ways larger-scale folklore did not predict — shape conclusions do NOT
transfer across scale regimes (see §6). P3-D-GU's R-0/R-1 base architecture should
start deep-thin with embedding sharing (embeddings dominate parameter count at
1–30M) as a design PRIOR, with shape held FIXED across arms so it cannot confound
the interface read [STIPULATED].

### 2.5 The released anchors are overtrained artifacts, not twins

SmolLM2-1.7B is trained on ~11T tokens — ~6,470 tokens/parameter, ~325× the
Chinchilla-optimal ~20 [LIT: smollm2-2025, chinchilla-2022] — via multi-stage data
mixing (FineMath/Stack-Edu/SmolTalk). OLMo-2 (7B/13B/32B, full data+code+checkpoint
release, COLM 2025) adds the two practices we should copy: training-stability
recipe changes and a **late-stage curriculum ("mid-training") data mix**
[LIT: olmo2-2024]. Pythia is the controlled-suite exemplar: 16 models, 70M–12B,
**same public data in the same order**, 154 checkpoints each, reconstructible
dataloaders (ICML 2023 oral) [LIT: pythia-2023].

LOAD-BEARING for P3-D-BASE [STIPULATED]: the rung anchors (SmolLM2-135M etc.) are
**pinned released comparators**, and the twins are **from-scratch-vs-from-scratch**
at matched training compute; the two comparator classes must never be conflated in
a claim — no academic-budget from-scratch run can be compute-matched to a ~6,500
tok/param artifact, and §2.3(v) only requires twins where the neurosymbolic arm
itself trains from scratch.

### 2.6 Data-quality wins: adopt the method, distrust the accounting

phi-1 (1.3B, 7B tokens of "textbook-quality" + synthetic data) reports HumanEval
50.6 / MBPP 55.5, and 45% HumanEval at 350M [LIT: phi1-2023]. The community's
standing rebuttal is the (explicitly satirical) phi-CTNL paper: a 1M-parameter
model achieves perfect benchmark scores by pretraining on the benchmarks —
"data-quality" claims are uninterpretable without a decontamination audit
[LIT: phi-ctnl-satire-2023]. Contamination detection practice is EVAL's remit
(carried); the TINY-side consequence [STIPULATED]: any synthetic/curated R-0
corpus we build (TinyStories-style, kernel-adjacent) must ship with a
decontamination statement against every index-suite component, because
curated-tiny-corpus + tiny-eval is the single easiest place in the whole programme
to manufacture a fake win.

---

## 3. SQ2 — small-scale scaling laws: what is settled, what is fragile

- **Settled shape, fragile constants.** Loss scales as a power law in N, D, C over
  ~7 orders of magnitude [LIT: kaplan-2020]; compute-optimal N and D scale roughly
  equally ("Chinchilla", ~20 tok/param, 400+ models 70M–16B) [LIT: chinchilla-2022].
  But the Kaplan-vs-Chinchilla exponent discrepancy is fully explained by three
  *methodology* choices — last-layer FLOP accounting, warmup duration,
  scale-dependent optimizer tuning — and AdamW β₂ tuning is essential at small
  batch sizes, while careful LR-decay is NOT essential (NeurIPS 2024 spotlight)
  [LIT: porian-2024]. Independently, Chinchilla's own parametric fit
  (approach 3) failed replication as reported — implausibly narrow CIs ("would
  require over 600,000 experiments"), inconsistency with approaches 1–2 — and only
  a re-derivation reconciles it [LIT: chinchilla-replication-2024].
  LOAD-BEARING [STIPULATED]: at R-0/R-1 scale, **fitting a law is a harder
  experiment than ranking a comparison** — the twin protocol should be designed to
  need only ordinal/direction reads (ASM-0815 already says this), and any fitted
  curve is DIAGNOSTIC unless its fitting procedure was pre-registered.
- **Token-budget axis is lawful, including overtraining.** Scaling laws extend
  reliably into the overtrained regime: a testbed of 104 models (0.011B–6.9B, 3
  data distributions) predicted the loss of a 1.4B/900B-token (32× overtrained)
  run and a 6.9B/138B run using 300×-less-compute experiments, plus a
  perplexity→downstream-top-1-error power law at 20×-less-compute
  [LIT: gadre-2024]. So the §3.5 sweep can use token budget as the second axis
  with literature support that the plain-twin side behaves predictably.
- **Repeated data degrades only mildly up to ~4 epochs — in the tested regimes.**
  At fixed compute under data constraint, up to ~4 epochs of repetition comes close
  to (not identical with) unique-data performance; beyond that the value of added
  compute decays toward zero. Tested on natural web-scale distributions up to 900B
  tokens / 9B params (NeurIPS 2023 oral) [LIT: muennighoff-2023]. For R-0 corpora
  (TinyStories-class, kernel-derived synthetic) this is a planning PRIOR only:
  those distributions are outside the tested regime, so the ≤4-epoch license is an
  [EXTRAPOLATION] the R-0 pilot must spot-check on the actual corpus (e.g.
  1-epoch-vs-4-epoch loss at fixed compute) before the sweep leans on it
  [STIPULATED].
- **Cross-dataset translation exists.** Shifted power laws translate train-to-train,
  train-to-test, and test-to-test losses between data distributions, extrapolating
  to ~20× the fitted FLOP budget — sometimes better than single-dataset laws
  [LIT: loss-to-loss-2024]. Useful for P3-D-BASE when the kernel arm's training
  distribution necessarily differs from the twin's (interface tokens in-corpus).
- **Breaks happen.** Smoothly-broken power laws (BNSL) are needed to model
  double descent and sharp inflections; naive extrapolation from a few points can
  cross an unseen break [LIT: bnsl-2022]. Mitigation for the ≥3-point protocol:
  §5.3.
- **Tiny-compute regimes still follow the laws.** Under a fixed one-GPU-day budget
  ("cramming"), performance tracks large-compute scaling laws, and the wins come
  from pipeline changes that respect them [LIT: cramming-2022] — the R-0 rung is
  not a lawless regime.

---

## 4. SQ3 — compute-matched twin methodology (the practice to adopt)

What "compute-matched twin" must mean, assembled from the verified practice:

1. **Match on training FLOPs, not words or steps — and keep FLOPs distinct from
   accelerator-hours.** The BabyLM findings' own FLOPs–performance relationship
   shows data-matched comparisons leak compute [LIT: babylm-2024-findings;
   accounting caveat owned by EVAL §7]. The MATCHED quantity is a registered
   training-FLOP ledger; accelerator-hours are logged per arm into KOT-LIFE/1
   (§2.3 already binds this) as a separate REPORTED quantity — the two diverge
   whenever kernels/precision/auxiliary execution differ between arms, so never
   substitute one for the other [STIPULATED: ASM-0812 restated].
   **Twin-compute ledger [STIPULATED — closes the gap the recipe pin cannot]:**
   an identical recipe is NOT sufficient matching, because the interface arm can
   change (i) parameter count (interface module), (ii) token count (interface
   tokens in-corpus), (iii) sequence length, (iv) objectives/losses, and
   (v) auxiliary execution (retrieval/verifier calls). The ledger must account
   each explicitly — including last-layer FLOPs [LIT: porian-2024] and an
   interface-token PARITY rule (how the plain arm's token budget compensates for
   interface tokens) — and be pre-registered in P3-D-BASE (§7 Q6).
2. **IsoFLOP construction.** Chinchilla approach 2 — for each budget, sweep model
   size at fixed FLOPs and read the valley — is the canonical way to place twin
   points fairly [LIT: chinchilla-2022]; with the Porian corrections (count
   last-layer FLOPs; scale warmup; tune or µP-fix the optimizer per scale)
   [LIT: porian-2024].
3. **Same data, same order, pinned checkpoints.** Pythia practice: identical
   corpus and data ORDER across arms/sizes, reconstructible dataloaders, seeded
   checkpoints [LIT: pythia-2023]. For twins this kills the data-order confound
   between interface and plain arms.
4. **Seeds are not optional at tiny scale.** 25 same-recipe BERT-base runs differ
   "substantially" downstream on seed alone; the Multi-Bootstrap is the matching
   inference procedure [LIT: multiberts-2021]. DataDecide runs 3 seeds per
   config as baseline hygiene [LIT: datadecide-2025]; the speedrun requires
   statistical validation across runs for a record [LIT: nanogpt-speedrun].
   ADOPT: ≥3 seeds per (arm × width × budget) cell at R-0, paired across arms by
   seed+data-order; direction read on seed-mean with a registered uncertainty
   procedure [STIPULATED — P3-D-GU decides the exact count from a pilot variance
   estimate; open question §7].
5. **HP fairness via µP.** Maximal-update parametrization makes optimal HPs stable
   across width — verified by tuning GPT-3-6.7B from a 40M proxy at ~7% of
   pretraining cost (NeurIPS 2021) [LIT: mup-2022] — and µParam also flattens
   LR-sensitivity in the instability regime [LIT: wortsman-2023]. µP is the most
   attractive way to run a multi-width sweep under the §2.3 total-tuning-compute
   symmetry budget, but NOT the only principled one: equal-tuning-budget per-scale
   search with a pre-registered selection rule, or registered proxy-tuning
   transfer rules, are legitimate (costlier) alternatives — and they are the
   registered FALLBACK if the µP audit fails, since µP's validity with Muon-class
   optimizers and with an attached interface module is itself unverified (µTransfer
   was demonstrated with Adam-class optimizers; §7 Q1). CAVEAT: depth-transfer
   (Depth-µP) holds for single-layer residual blocks but hits "fundamental
   limitations" for transformer-style multi-layer blocks [LIT: tp6-depth-2023] —
   so the sweep axis should be WIDTH (+ token budget), holding depth fixed per
   rung [STIPULATED].
6. **Interface-arm prior art.** Non-learned/trained-in interfaces have helped in
   the specific configurations tested — not "at any scale": kNN-LM adds −2.9
   perplexity on Wikitext-103 with NO additional training, in one configuration
   (ICLR 2020) [LIT: knnlm-2019]; RETRO (trained-in chunked cross-attention over a
   2T-token store) matches GPT-3-class perplexity at 25× fewer parameters — a
   comparison explicitly NOT resource- or lifecycle-matched, since the 2T-token
   store sits outside the parameter count [LIT: retro-2021]. Neither establishes
   that interfaces help regardless of host capacity. LEARNED interface *use* shows
   a within-lineage capacity ASSOCIATION: Toolformer's API-call benefit "only
   emerges at around 775M" (GPT-2 124M/355M/775M/1.6B sweep; paper-body figure via
   PDF excerpt, primary PDF located) — an observation in which scale co-varies
   with base capability, generated-call quality, filtering, and task mix, so it is
   prior evidence of a POSSIBLE threshold, not a general measured interface
   threshold [LIT: toolformer-2023]. Direction-only reading [EXTRAPOLATION —
   never a premise]: whether a kot-interface behaves like post-hoc retrieval
   (helps at 1M) or like learned tool-use (needs 100M+) is the exact uncertainty
   ASM-0815's sweep protocol was designed for; both priors are in the literature,
   so neither a tiny null nor a tiny win settles the family.
7. **Instability probes are cheap.** Large-scale instabilities (attention-logit
   growth, output-logit divergence) reproduce in SMALL models at high learning
   rates, and the large-scale mitigations (QK-norm, z-loss, warmup, weight decay,
   µParam) work there too; activation/gradient-norm scaling predicts some
   instabilities before they fire [LIT: wortsman-2023]. OLMo-2's stability recipe
   is the production distillation of the same lessons [LIT: olmo2-2024]. ADOPT:
   the R-0 twin recipe includes QK-norm + registered LR-sensitivity check, so an
   interface-arm divergence is attributable [STIPULATED].

---

## 5. SQ4 — designing the ≥3-point sweep (the §3.5 direction protocol's prior art)

### 5.1 The decision-theoretic anchor

DataDecide (ICML 2025; 25 corpora × 14 scales up to 1B/100B tokens, 3 seeds,
30k+ checkpoints) is the closest external ANALOGUE to our question, one domain
over: do small experiments predict larger-scale decisions — for PRETRAINING-DATA
selection between standard-architecture models at roughly 150M→1B? It does not
study symbolic-interface interventions, architecture changes, 5–30M models, or
signed treatment-effect trends; everything below transfers by analogy only.

- Ranking candidates at ONE small scale (150M) predicts the best-at-1B in **~80%
  of comparisons**.
- **None of eight scaling-law extrapolation baselines beat that single-scale
  ranking** for decision-making.
- Best cheap proxies are **continuous likelihood metrics** (correct-continuation
  likelihood), making MMLU/ARC/HellaSwag-class decisions >80% predictable at
  0.01% of target compute [LIT: datadecide-2025].

Consequences [STIPULATED — analogical support, not validation]: (a) the
programme's choice of direction-reads over fitted-law extrapolation (ASM-0815) is
CONSISTENT with the best adjacent evidence; DataDecide does not validate ASM-0815
for interface effects — whether interface-direction reads transfer like
data-ranking decisions is exactly what P3-E-GU-1/G5 will create the first evidence
on; (b) the ~20% flip rate is a domain-specific caution from the nearest analogue
— a floor on the trust placed in ANY single-scale read, not a measured error rate
for interface promotions/kills — and it is why the gate ladder demands the same
gate fail at two consecutive rungs before a family closes (§4 rung discipline),
and why G5 re-tests the margin at two sizes; (c) sweep endpoints at R-0/R-1 should
be continuous/likelihood metrics (agreeing with EVAL §5's independent metric-side
argument — carried).

### 5.2 Sweep geometry

Assembled recommendation for P3-D-GU [STIPULATED — design input, not a prereg]:

- **Axes:** width ∈ ≥3 points (e.g. ~5M/~15M/~30M at R-0 under µP; R-1 confirm at
  135M-class), and token budget ∈ ≥3 points per width, CENTRED ON A PILOT-ESTIMATED
  compute-optimal ratio for this architecture/data regime — Chinchilla's ~20
  tok/param is the prior for where the pilot starts looking, not a constant to
  hardcode (§3 fragile-constants) — e.g. 0.5×/1×/4× of the pilot centre. The 4×
  leg probes the overtrained regime that behaves lawfully [LIT: gadre-2024]; its
  data-repetition license is an out-of-regime extrapolation the pilot must
  spot-check (§3) [LIT: muennighoff-2023].
- **Parameterization:** µP across width, fixed depth per rung (Depth-µP caveat,
  §4.5; registered fallback = equal-budget per-scale tuning if the µP audit
  fails); deep-thin base shape with embedding sharing [LIT: mobilellm-2024].
- **Recipe pin:** one modern recipe (modded-nanoGPT-class, §2.3 — a conditional
  prior pinned for cross-arm symmetry, not a validated optimum) shared verbatim
  by interface and plain arms; optimizer = the pinned recipe's (Muon-class), with
  the §2.3 caveat that optimizer choice alone is worth ~2× compute
  [LIT: muon-scalable-2025] — so it must be IDENTICAL across arms.
- **Pairing:** same data order and seed pairing across arms (§4.3–4.4); ≥3 seeds.
- **Read:** pre-registered DIRECTION of Δ(interface−plain) across the sweep per
  ASM-0815, on continuous metrics; fitted curves reported as DIAGNOSTIC only.
- **Feasibility:** cell count × per-cell cost (widths × budgets × seeds × 2 arms
  + tuning + pilot) must be shown to fit §3.6's 15–75 GPU-h envelope BEFORE
  freeze — the pilot produces the per-cell cost estimate; if the full grid does
  not fit, the registered reduction order is budget-points, then widths, then
  (last) seeds [STIPULATED].

### 5.3 Failure modes the design must carry

- **Break-crossing:** a monotone read across 3 points can straddle a BNSL-style
  inflection [LIT: bnsl-2022]. Mitigation: if the three points are non-monotone,
  the protocol's registered answer is "add points / escalate one rung", not a
  post-hoc fit [STIPULATED].
- **HP-unfairness masquerading as interface effect:** scale-dependent optimizer
  tuning moved published scaling exponents [LIT: porian-2024]; µP + identical
  recipe is the counter.
- **Seed noise masquerading as direction:** MultiBERTs-scale run-to-run variance
  [LIT: multiberts-2021]; counter = paired seeds + Multi-Bootstrap-style inference.
- **Metric floors:** owned by EVAL §6 (BLiMP discriminative across the tiny range;
  EWoK near-floor) — carried, not restated.
- **Judge-graded endpoints at R-0:** TinyStories-style GPT-4 grading imports an
  instrument we only trust at a measured style margin (§2.1) — avoid for primary
  endpoints [STIPULATED].

---

## 6. SQ5 — what tiny-scale results HAVE and have NOT predicted

**HAVE predicted (verified instances):**

- Loss and loss-derived quantities, including 32×-overtrained runs, from 300×
  less compute [LIT: gadre-2024]; cross-dataset losses to ~20× the fitted budget
  [LIT: loss-to-loss-2024]; loss under one-GPU-day budgets tracks big-compute laws
  [LIT: cramming-2022].
- Data-recipe DECISIONS at ~80% comparison accuracy from a single 150M scale —
  in the pretraining-data-selection domain specifically (§5.1)
  [LIT: datadecide-2025].
- Hyperparameters across width under µP (40M → 6.7B at 7% of pretraining cost)
  [LIT: mup-2022].
- Training instabilities and their mitigations (small-model high-LR proxies →
  large-scale fixes) [LIT: wortsman-2023].

**Have NOT predicted (verified instances):**

- Capability read through discontinuous metrics: apparent emergence is largely a
  metric artifact, and MC-accuracy near floor carries ~no signal upward
  [LIT: schaeffer-emergence-2023 — UNVERIFIED-THIS-PASS, carried from EVAL.md §5
  where it was verified 2026-07-11; metric side owned there].
- Learned tool/interface use below a capacity threshold: no benefit ≤355M, benefit
  emerging ~775M in the Toolformer lineage [LIT: toolformer-2023] — a tiny-scale
  null that a larger scale REVERSED, within one lineage and with the §4.6
  confounds (scale co-varies with base capability, call generation/filtering).
  This is the single most important external datum for ASM-0815's "do not conclude
  fundamental failure from one tiny null" — as an existence proof of reversal, not
  as a general threshold.
- Architecture-shape conclusions across regimes: shape ~irrelevant in Kaplan's
  range [LIT: kaplan-2020] vs materially consequential at 125M/350M (bundled
  MobileLLM design package, §2.4) [LIT: mobilellm-2024] — a shape prior tuned at
  one rung does not transfer.
- ~20% of DataDecide's small-scale decisions flip at 8× scale [LIT:
  datadecide-2025]; and scaling-law fits themselves have failed replication at
  publication quality [LIT: chinchilla-replication-2024].
- Whole-benchmark predictability is capability-space-dependent (observational
  scaling: smooth sigmoids in a low-dim capability space — including post-training
  technique value) [LIT: ruan-observational-2024 — UNVERIFIED-THIS-PASS, carried
  from EVAL.md §5].

**Internal (our own R-0/R-1 record) [MEASURED, restated within envelopes]:** the
programme currently has tiny-scale results only — f2b-replicate's 135M+verifier
positive (formal inputs, alignment-confounded), nsk1's text-channel negative
("at every scale tested" ≤1.7B), l3a/a5's R0 instrument exactness — and NOTHING
measured above 1.7B. No internal claim of upward prediction exists to audit;
P3-E-GU-1 (direction protocol) + G5 (two-size confirmation) are the pre-registered
instruments that will create the first such evidence. [STIPULATED: this review
adds the literature priors; it neither strengthens nor weakens any internal
verdict.]

---

## 7. Methods to adopt + open questions for Phase-1

**Adopt (P3-D-BASE / P3-D-GU design inputs)** [STIPULATED, each with its source]:

| # | Method | Source |
|---|---|---|
| 1 | Pinned modern twin recipe (Muon-class optimizer, rotary+QK-norm, deep-thin, embedding sharing), identical across arms — a conditional design prior pinned for cross-arm symmetry, not a validated optimum (§2.3) | [LIT: nanogpt-speedrun, muon-scalable-2025, mobilellm-2024] |
| 2 | µP width-parameterization; sweep width + token budget, hold depth; registered fallback = equal-tuning-budget per-scale search if the µP audit fails (§4.5) | [LIT: mup-2022, tp6-depth-2023] |
| 3 | IsoFLOP twin placement w/ Porian corrections (last-layer FLOPs, warmup scaling, β₂ at small batch) | [LIT: chinchilla-2022, porian-2024] |
| 4 | Same-data-same-order arms, reconstructible dataloaders, checkpoint grid | [LIT: pythia-2023] |
| 5 | ≥3 paired seeds/cell; Multi-Bootstrap-style inference on seed-paired deltas | [LIT: multiberts-2021, datadecide-2025] |
| 6 | ≤4-epoch repetition PRIOR for small R-0 corpora — out-of-regime extrapolation; pilot spot-check required (§3) | [LIT: muennighoff-2023] |
| 7 | Direction-read over fitted-law extrapolation for promote/kill; continuous-likelihood endpoints (analogical support from the data-selection domain, §5.1) | [LIT: datadecide-2025; ASM-0815] |
| 8 | Decontamination statement for any curated/synthetic R-0 corpus | [LIT: phi-ctnl-satire-2023; screener owned by P3-MF-0] |
| 9 | Anchor-vs-twin comparator separation (released overtrained anchors are pins, never "matched") | [LIT: smollm2-2025; §2.5] |
| 10 | Stability instrumentation in the twin recipe (QK-norm, LR-sensitivity check, norm monitoring) | [LIT: wortsman-2023, olmo2-2024] |
| 11 | Twin-compute ledger: registered training-FLOP accounting incl. interface module/tokens/sequence length/objectives/auxiliary execution + interface-token parity rule; accelerator-hours reported separately, never substituted (§4.1) | [LIT: porian-2024, babylm-2024-findings; ASM-0812] |

**Open questions Phase-1 must answer (not answered by the literature):**

1. **Does µP remain valid with a symbolic interface module attached — and with a
   Muon-class optimizer?** µP is derived for standard architectures and was
   demonstrated with Adam-class optimizers; an interface block (adapter/
   cross-attention into kernel vectors) may need its own parameterization audit,
   and the µP×Muon interaction is equally unaudited — nothing published covers
   either. Registered fallback if the audit fails: equal-tuning-budget per-scale
   search (§4.5) [EXTRAPOLATION → P3-D-GU deliverable].
2. **Seed count for the direction read**: 3 is community hygiene; the count that
   powers a 3-point direction read against MultiBERTs-scale variance must come
   from a registered pilot variance estimate + power analysis, not a convention
   [P3-D-GU].
3. **R-0 corpus choice**: TinyStories-class synthetic vs BabyLM-class natural vs
   kernel-adjacent synthetic — the distribution decides which interface effects
   are even expressible at 1–30M (§2.1); needs an explicit decision with a
   decontamination statement [P3-D-GU with P3-D-BASE].
4. **Which interface class is H-GU's step-0 interface** (non-learned kNN-style
   injection vs learned tool-call vs trained-in cross-attention)? The literature
   prior differs by class (§4.6) and so does the expected capacity threshold
   [P3-D-GU, variant staging §3.5].
5. **What total-tuning-compute cap keeps the twin honest** given optimizer choice
   alone is worth ~2× [LIT: muon-scalable-2025]? The §2.3 rule needs a number per
   rung [P3-D-BASE].
6. **The exact twin estimand + compute ledger + feasibility**: what precisely is
   held equal when the interface changes parameter count, token count, sequence
   length, objectives, or auxiliary execution (§4.1 twin-compute ledger, incl.
   the interface-token parity rule), and does the resulting grid — cells × seeds
   × arms + tuning + pilot — fit the 15–75 GPU-h envelope (§5.2 feasibility)?
   Both must exist as numbers at P3-D-BASE freeze [P3-D-BASE with P3-D-GU].

---

## 8. Prior-failure judgements (capability-limited vs fundamental)

| Prior failure/null | Judgement | Basis |
|---|---|---|
| Developmental/NL-ordering curricula at 10M–100M words (BabyLM 2023 submissions "largely unsuccessful"; 2024 wins located elsewhere) | **Recipe-limited at tested scope, single-cycle evidence — NOT a replicated null.** Deprioritise BabyLM-style curriculum arms as a prior; says nothing about the scoped synthetic rule-depth curriculum variant (rev-2 §3.5), which stays in scope | [LIT: babylm-2023-findings, babylm-2024-findings] |
| Tool-use benefit absent ≤355M (Toolformer lineage) | **Consistent with capacity limitation — within-lineage observation, confounded** (scale co-varies with base capability, call generation/filtering, task mix; benefit emerges ~775M in-lineage); NOT a fundamental tiny-model limit and NOT a general interface threshold — kNN-LM/RETRO show non-learned/trained-in interfaces helping in their tested configurations | [LIT: toolformer-2023, knnlm-2019, retro-2021] |
| Kaplan "shape doesn't matter" / Kaplan-vs-Chinchilla exponents | **Methodology-limited** — resolved by FLOP accounting, warmup, optimizer tuning | [LIT: porian-2024] |
| Chinchilla approach-3 parametric fit | **Reporting/fitting-limited** — re-derivation reconciles; the isoFLOP result stands | [LIT: chinchilla-replication-2024] |
| BabyLM multimodal track: nothing beat baselines | **Open/unexplained at scope** — a genuine community null, cause unattributed; irrelevant to P3 scope (no multimodal leg) | [LIT: babylm-2024-findings] |
| Our l3a-parse/a5-nl NL-boundary FAILs | Out of TINY scope — judged capability-limited (leading hypothesis) in PARSE.md §0; nothing in the tiny-training literature changes that | [MEASURED + PARSE.md, carried] |

---

## 9. Phase-1 hand-off

**What this review SETTLES for the design beads:**

- The R-0 rung is literature-licensed (TinyStories-class capability at 1–30M) but
  envelope-bound to its corpus; endpoints must be continuous metrics, not judge
  grades (§2.1, §5.1).
- The twin METHOD TOOLBOX is assembled, as conditional design priors: pinned
  modern recipe (for cross-arm symmetry), µP width sweep with a registered
  fallback, pilot-centred token-budget axis, isoFLOP placement,
  same-data-same-order, ≥3 paired seeds, direction-read, twin-compute ledger
  (§7 table 1–11). NOT closed: Phase-1 still owns the estimand-defining choices —
  interface class, R-0 corpus, µP validity with interface+Muon, pilot-powered
  seed count, tuning-compute cap, and the concrete FLOP ledger + feasibility
  against the 15–75 GPU-h envelope (§7 open questions 1–6).
- The direction-protocol (ASM-0815) is CONSISTENT WITH the nearest external
  evidence — analogical support only (DataDecide's ~80% is a pretraining-data
  result, §5.1; the Toolformer threshold is a confounded within-lineage
  observation, §4.6): one tiny null must not kill a family, and fitted-law
  extrapolation must not replace the sweep (§5.1, §6). The internal validation
  instrument is P3-E-GU-1/G5, not this review.
- Released anchors ≠ twins (SmolLM2 ~6,500 tok/param): P3-D-BASE must carry two
  comparator classes with different claim scopes (§2.5).

**Design beads to bd-create on completion (per §5 Phase-0 table; governance: this
bead does not run bd — coordinator to execute):**

```bash
bd create --title="P3-D-GU: ground-up R-0 architecture(s) + ≥3-point sweep protocol + variant staging (§3.5)" \
  --type=task --priority=2 \
  --description="Blocked by P3-LR-TINY + P3-LR-NTP + P3-LR-FUSE (rev-2 §5). Inputs from docs/next/lit/TINY.md: §5.2 sweep geometry (µP width sweep, isoFLOP, pilot-centred token-budget axis, ≥3 paired seeds, direction read per ASM-0815), §7 open questions 1-4 (µP-validity with interface module + Muon, seed count from pilot variance, R-0 corpus choice + decontamination statement, interface-class selection), §2.2 (deprioritise BabyLM-style curriculum arms; synthetic rule-depth curriculum stays in scope), §2.3 recipe pin. Spawns P3-E-GU-1." \
  --acceptance="(1) step-0 interface class chosen and justified against §4.6 prior-art classes; (2) R-0 corpus chosen WITH decontamination statement vs every index-suite component; (3) µP-validity audit plan for interface-module + Muon-class optimizer, with equal-tuning-budget per-scale search registered as fallback; (4) seed count derived from a registered pilot variance estimate + power analysis for the 3-point direction read (NOT convention); (5) registered decision rule for ambiguous/non-monotone sweep trends = add points / escalate one rung, never a post-hoc fit (§5.3); (6) full grid (widths × budgets × seeds × 2 arms + tuning + pilot) shown numerically to fit the 15-75 GPU-h envelope of §3.6, with the registered reduction order budget-points → widths → seeds if it does not." \
  --notes="Also consumes P3-LR-NTP (proof-trace distillation variants) + P3-LR-FUSE (fusion variants) when those land."
bd create --title="P3-D-BASE: baseline-set pins per rung + R-0 twin recipe + total-tuning-compute symmetry rules (§2.3)" \
  --type=task --priority=0 \
  --description="Blocked by P3-LR-EVAL + P3-LR-TINY + P3-LR-RAG (rev-2 §5). Inputs from docs/next/lit/TINY.md: §7 adopt-table 1-11 (pinned modern twin recipe as conditional prior for cross-arm symmetry; anchor-vs-twin comparator separation — SmolLM2-class anchors are overtrained ~6,500 tok/param and are PINS not twins; isoFLOP twin placement w/ Porian corrections; same-data-same-order; ≤4-epoch repetition PRIOR w/ pilot spot-check; stability instrumentation; twin-compute ledger), §7 open questions 5-6 (tuning-compute cap per rung, optimizer worth ~2×; exact twin estimand + ledger + feasibility). Feeds every [EXP]." \
  --acceptance="(1) twin-compute ledger pre-registered: training-FLOP accounting incl. last-layer FLOPs, interface-module parameters, interface tokens in-corpus, sequence length, objectives/losses, auxiliary execution (§4.1); (2) explicit interface-token PARITY rule (how the plain arm's token budget compensates); (3) accelerator-hours logged per arm as a separate REPORTED quantity, never substituted for FLOPs; (4) total-tuning-compute cap per rung as a NUMBER with a fixed pre-registered selection rule (ASM-0812); (5) recipe pin recorded (modded-nanoGPT-class, commit-pinned) identical across arms, stated as conditional prior not validated optimum; (6) anchor-vs-twin claim-scope separation stated in every baseline pin; (7) per-cell cost + grid feasibility numbers vs the 15-75 GPU-h envelope exist at freeze." \
  --notes="Co-inputs: docs/next/lit/EVAL.md (metric floors, proxy-rung validity) + P3-LR-RAG (RAG-control baselines) — check both landed before freeze."
# after both exist:
bd dep add <P3-D-GU-id> kernel-of-truth-s55r.11
bd dep add <P3-D-BASE-id> kernel-of-truth-s55r.11
```

**Source counts:** 29 primary URLs/landing pages fetched and checked this pass
(`TINY.sources.jsonl`, `verified:true` — URL-level primary-venue check, per the
epistemic contract NOT a claim that every body figure was independently
re-verified; where a body figure is load-bearing its provenance is stated in-line,
e.g. the Toolformer PDF excerpt and the speedrun README at the pinned commit);
2 carried from EVAL.md's verified set without re-fetch (`verified:false`, flagged
in-line): schaeffer-emergence-2023, ruan-observational-2024. No claim in this
document rests solely on an unverified source.
