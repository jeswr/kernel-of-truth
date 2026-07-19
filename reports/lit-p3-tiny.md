# Lit review — P3-LR-TINY: tiny-model training + small-scale scaling laws

**Bead:** P3-LR-TINY (Programme-3, Phase-0 [LIT]).
**Author role:** literature-researcher (source-verification + formalization pass).
**Date:** 2026-07-19.
**Provenance:** VERIFICATION + FORMALIZATION of the prior Fable draft `docs/next/lit/TINY.md`
(+ `TINY.sources.jsonl`, 2026-07-11). This pass re-fetched the load-bearing citations at
source on 2026-07-19; it does not redo the review from scratch. Divergences from the draft are
in §11.
**Feeds:** **P3-D-GU** (ground-up R-0 architectures + the ≥3-point direction sweep, §3.5/ASM-0815)
and **P3-D-BASE** (baseline pins per rung + the R-0 twin recipe + tuning-symmetry rules,
§2.3/ASM-0812).
**Status:** DRAFT for the review gate (GPT-5.6) + Fable critique. Not a freeze; takes no design
decision and stipulates nothing. Do **not** commit/push — coordinator review pending.

## 0. How to read this report — epistemic conventions

Every finding carries a tag: **[established]** (well-supported by a verifiable primary source),
**[claimed]** (asserted by a source but single-source / not independently corroborated here),
**[speculative]** (my inference or extrapolation, flagged as such), each with **[search]** or
**[memory]** and the verification date (all this session, 2026-07-19 unless noted). Load-bearing
citations were fetched at source and are graded in the §10 verification table; a claim that could
not be fetched directly is marked **[UNVERIFIED-DIRECT]** with its corroboration path named.
Prior approaches that failed are judged **capability-limited** (mitigable by a better
instrument/recipe/selection) vs **fundamental** (a property of the method that cannot be
engineered away) in §8. Nothing here amends a registry object; KB/lit records are recall
infrastructure, not evidence.

**Rung→size map** (from programme doc §4, restated): **R-0** = 1–30M (TinyStories-class data);
**R-1** = 100–200M (SmolLM2-135M anchor, the decisive cheap rung where every family's first gates
run); **R-2** = 300–500M (SmolLM2-360M anchor); **R-3** = 1.7B. Params are orientation; the binding
constraint is the budget vector.

**Relationship to the sibling review.** `reports/lit-p3-eval.md` (P3-LR-EVAL, 2026-07-19) owns the
**metric side** of proxy-rung validity — emergence-as-metric-artifact, observational scaling,
benchmark floors/ceilings by rung, and (its §5) the **downstream-scaling reliability** literature.
This review owns the **training side**: which *training decisions* made at tiny scale transfer
upward, and how to build the twins and the sweep. §6 co-reconciles the two explicitly (the
proxy-rung asymmetry is the same in both, seen from two angles).

---

## 1. Executive verdict

[speculative, synthesised from the verified findings below][search 2026-07-19]
Tiny-model training is a **strong-recipe-priors, unsolved-comparison** field: the recipe side gives
strong *conditional* priors (not a validated optimum), and the comparison side — where a
neurosymbolic twin programme actually lives or dies — is explicitly fragile in the literature. Three
load-bearing reads for the design beads:

1. **The R-0 rung is literature-licensed but envelope-bound.** Coherent generation below 10M
   parameters is real on a simplified distribution [established, tinystories-2023] — so an R-0
   rung can exercise real composition machinery cheaply — but the result is bound to that training
   distribution, and its native metric is GPT-4 judge grading, which the programme trusts only
   within a measured style-leak margin. R-0 endpoints must be continuous/minimal-pair metrics, not
   judge scores.
2. **No academic-budget twin can be compute-matched to a released anchor.** SmolLM2-1.7B is trained
   on ~11T tokens = ~6,470 tokens/parameter, ~325× Chinchilla-optimal [established, smollm2-2025 +
   chinchilla-2022] — an overtrained artifact, not a matchable twin. Twin claims must be scoped to
   **from-scratch-vs-from-scratch**; released anchors are *pinned comparators*, a separate class.
3. **Small-scale results predict LOSS reliably and CAPABILITY/interface-effects unreliably** — the
   same asymmetry P3-LR-EVAL §5 found on the metric side. DataDecide (the nearest external analogue,
   a *data-selection* study) shows single-scale ranking beats all 8 scaling-law extrapolators and is
   ~80% accurate — but ~20% of decisions still flip at 8× scale [established, datadecide-2025], and
   the interface effect is a *novel downstream construct with no established scaling law*. The
   protocol read must therefore be the DIRECTION of the interface effect across a µP-parameterized,
   seed-replicated, ≥3-point sweep (ASM-0815), with the internal transfer evidence created by
   P3-E-GU-1/G5 — not asserted from the literature.

**Verification headline:** 25 of 29 sources were re-fetched at source this pass; **all load-bearing
figures matched their citation** — no numeric error of the class sibling passes caught elsewhere
(Sardana $-figure, TinyAgent 40k/80K, TeCoD points-vs-percent). The four not re-fetched are
corroborated indirectly (§10). The draft is in strong shape; §11 lists only soft/interpretive
divergences.

---

## 2. SQ1 — state of the art in tiny-model training (1M–2B)

**Finding 2.1 — The R-0 regime exists because the data distribution is a free variable.**
[established][search 2026-07-19] TinyStories (arXiv:2305.07759): on a synthetic corpus containing
only words "a typical 3 to 4-year-old" understands (generated by GPT-3.5/GPT-4), models "below 10
million total parameters, or … only one transformer block … still produce fluent and consistent
stories with several paragraphs," where GPT-Neo/GPT-2-small (~125M) on ordinary data "can rarely
generate coherent and consistent English text … even after extensive training." Verified verbatim at
the abstract. Two directions:
- POSITIVE: capability-per-parameter is strongly distribution-dependent → an R-0 rung on simplified
  data can exercise real composition/consistency at 1–30M. This is the literature license for R-0's
  existence.
- CAUTION: the same fact makes R-0 results **envelope-bound to the training distribution**, and
  TinyStories' native evaluation is GPT-4-graded — a judge instrument the programme trusts only
  within a measured style-leak margin [MEASURED: truthstyle-2x2 PASS at ±0.10, carried]. **R-0
  endpoints must be continuous / minimal-pair metrics, not judge scores** (agreeing with EVAL §5,
  carried).

**Finding 2.2 — BabyLM: two community cycles of recipe search at 10M–100M words.**
[established][search 2026-07-19]
- **2023** (>30 submissions, 10M/100M strict+loose): LTG-BERT (an architecture change) won;
  "Curriculum learning attempts … were largely unsuccessful, though some showed modest
  improvements"; other wins came from **shorter input sequences** and **knowledge distillation**.
  Verified via the findings text (arXiv:2504.08165, the retrospective findings paper; the draft's
  ACL-anthology URL is venue metadata for the same content).
- **2024** (31 submissions): a **hybrid causal-masked** model (GPT-BERT) won; best submissions
  changed data + objective + architecture; the findings report "a strong relationship between
  training FLOPs and average performance across tasks"; "No submissions outperformed the baselines
  in the multimodal track." Verified verbatim at arXiv:2412.05149.
- GPT-BERT itself (arXiv:2410.24159) — hybrid masked+causal, usable afterward as either — is
  corroborated as the 2024 winner by the findings paper above [established via corroboration; primary
  abstract not individually re-fetched this pass].

**Finding 2.3 — The speedrun: large, publicly documented recipe headroom at exactly R-1.**
[established][search 2026-07-19, moving leaderboard, commit-pinned] modded-nanoGPT README at the
pinned commit `edf47a05a12062d661c4cfd4eef848c5ab5bed32` (re-fetched via raw GitHub 2026-07-19):
training a 124M model to GPT-2-quality validation loss **≤3.28 on FineWeb (8×H100)** fell from the
llm.c **45-minute** baseline to **1.320 minutes — Record #84 (2026-05-21) — ~34× wall-clock**, across
**84 records since 2024-05-28**; a record requires enough run logs for **p<0.01** that mean val loss
≤3.28. Techniques accumulated ACROSS records (Muon/NorMuon optimizer, rotary, QK-norm, ReLU²,
FlashAttention-3 long-short windows, FP8/bf16, multi-token prediction, value/bigram-hash embeddings).
**CHARACTERISATION CAVEAT (load-bearing):** this is a BUNDLED, hardware-specific *wall-clock*
engineering result — per-component contributions unmeasured, NOT a training-FLOP comparison, and NOT
evidence that a plain GPT-2 twin is 34× less compute-efficient. The one separately-measured component
is **Muon: ~2× compute-efficiency vs AdamW at compute-optimal settings** (once weight decay +
per-parameter update-scale are added), scaling to a 3B/16B-MoE (Moonlight) on **5.7T tokens**
[established, muon-scalable-2025, arXiv:2502.16982, verified verbatim].

**Finding 2.4 — Architecture shape matters again at sub-billion scale.**
[established][search 2026-07-19] MobileLLM (arXiv:2402.14905): the COMBINED design package (deep-thin
shape + embedding sharing + grouped-query attention) attains "a remarkable **2.7%/4.3%** accuracy
boost over preceding **125M/350M** state-of-the-art models"; block-wise weight sharing (MobileLLM-LS)
adds a further **0.7%/0.8%**. Verified verbatim. NOTE: the abstract phrases these as "% accuracy
boost"; these are **absolute average-accuracy gains (percentage points)** of the whole package over
prior *models* — NOT a clean single-factor causal estimate of deep-thin-vs-wide-shallow (the draft's
"pp" reading is correct; see §11). Read against Kaplan's "network width or depth have minimal effects
within a wide range" [established, kaplan-2020], the conservative conclusion: **shape conclusions do
NOT transfer across scale regimes** (§6), and shape must be held FIXED across twin arms so it cannot
confound the interface read.

**Finding 2.5 — The released anchors are overtrained artifacts, not twins.**
[established][search 2026-07-19] SmolLM2-1.7B is "overtrain[ed] … on ~11 trillion tokens" via
multi-stage mixing (FineMath, Stack-Edu, SmolTalk); the paper itself uses the word "overtrain"
[smollm2-2025, verified verbatim]. Arithmetic: 11e12 / 1.7e9 ≈ **6,470 tok/param ≈ 325× Chinchilla's
~20** [chinchilla-2022, verified: "for every doubling of model size the number of training tokens
should also be doubled," 400+ models 70M–16B]. Controlled-suite exemplars to copy: **Pythia** (16
models 70M–12B, "public data seen in the exact same order," 154 checkpoints each) [established,
pythia-2023, verified verbatim]; **OLMo-2** (7B/13B/32B fully open; training-stability recipe +
late-stage "Dolmino Mix 1124" annealing curriculum; Pareto frontier of performance-to-training-
compute) [established, olmo2-2024, verified verbatim].

**Finding 2.6 — Data-quality wins: adopt the method, distrust the accounting.**
[established][search 2026-07-19] phi-1 (arXiv:2306.11644): 1.3B, 7B tokens ("6B tokens" textbook-
quality web + 1B GPT-3.5-synthetic) → HumanEval **50.6** pass@1, MBPP **55.5**; phi-1-small (350M)
"still achieves **45%** on HumanEval." Verified verbatim. The standing (explicitly satirical)
rebuttal — phi-CTNL, a 1M-param model scoring perfectly by pretraining on the benchmarks
[phi-ctnl-satire-2023, satire; abstract not re-fetched this pass, well-known] — is the reason any
curated/synthetic R-0 corpus we build must ship a **decontamination statement** against every
index-suite component (contamination detection itself is EVAL's remit, carried).

---

## 3. SQ2 — small-scale scaling laws: settled shape, fragile constants

[all established][search 2026-07-19]
- **Settled shape, fragile constants.** Loss is a power law in N, D, C "spanning more than seven
  orders of magnitude" [kaplan-2020, verified]; compute-optimal N and D scale equally (~20 tok/param;
  400+ models) [chinchilla-2022, verified]. But the Kaplan-vs-Chinchilla exponent discrepancy is
  fully explained by three **methodology** factors — "last layer computational cost, warmup duration,
  and scale-dependent optimizer tuning"; "tuning the AdamW β₂ parameter is essential at lower batch
  sizes"; and "careful learning rate decay is not essential" [porian-2024, verified verbatim,
  NeurIPS 2024 spotlight]. Independently, Chinchilla's own approach-3 parametric fit failed
  replication: intervals "this narrow would require over 600,000 experiments, while they likely only
  ran fewer than 500," and are "inconsistent with their first two estimation methods"
  [chinchilla-replication-2024, verified verbatim].
  **LOAD-BEARING:** at R-0/R-1, **fitting a law is a harder experiment than ranking a comparison** —
  the twin protocol should need only ordinal/direction reads (ASM-0815 already says this); any fitted
  curve is DIAGNOSTIC unless its fitting procedure was pre-registered.
- **Token-budget axis is lawful, including overtraining.** A 104-model testbed (0.011B–6.9B, 3 data
  distributions) predicted the loss of a **1.4B/900B-token (32× overtrained)** run "using experiments
  that take 300× less compute," plus a perplexity→downstream-top-1-error law at **20× less compute**
  [gadre-2024, verified verbatim]. So the §5 sweep can use token budget as the second axis with
  literature support that the *plain-twin* side behaves predictably.
- **Repeated data degrades only mildly up to ~4 epochs — in the tested regimes.** "training with up
  to 4 epochs of repeated data yields negligible changes to loss compared to having unique data";
  beyond that "the value of adding compute eventually decays to zero." Tested to 900B tokens / 9B
  params on natural web distributions (400 runs) [muennighoff-2023, verified verbatim, NeurIPS 2023
  oral]. For R-0 corpora (TinyStories-class synthetic) this is a planning PRIOR only — an
  out-of-regime [EXTRAPOLATION] the R-0 pilot must spot-check (1-epoch-vs-4-epoch loss at fixed
  compute) before the sweep leans on it.
- **Cross-dataset translation exists.** Shifted power laws translate train-to-train, train-to-test,
  test-to-test losses across distributions and "extrapolate well even at 20× the largest FLOP budget
  used to fit," "sometimes … more accurate … than extrapolating single-dataset scaling laws"
  [loss-to-loss-2024, verified verbatim]. Useful for P3-D-BASE when the kernel arm's distribution
  necessarily differs (interface tokens in-corpus).
- **Breaks happen.** Smoothly-broken power laws model "nonmonotonic transitions … such as double
  descent" and "delayed, sharp inflection points … such as arithmetic" [bnsl-2022, verified]. NOTE:
  the abstract demonstrates that breaks *exist and standard forms miss them*; the draft's use of BNSL
  as a "few-point extrapolation can cross an unseen break" caution is a reasonable **interpretive
  extension**, not a verbatim abstract warning (§11). It still correctly motivates the §5.3
  non-monotone-sweep rule.
- **Tiny-compute regimes still follow the laws.** Under a one-GPU-day budget, "performance closely
  follows scaling laws observed in large-compute settings" [cramming-2022, verified] — R-0 is not a
  lawless regime.

---

## 4. SQ3 — compute-matched twin methodology (the practice to adopt)

What "compute-matched twin" must mean, assembled from the verified practice [each item established
at source unless tagged]:

1. **Match on training FLOPs, not words or steps — and keep FLOPs distinct from accelerator-hours.**
   BabyLM-2024's own FLOPs↔performance relationship (verified §2.2) shows data-matched comparisons
   leak compute (accounting caveat owned by EVAL). The MATCHED quantity is a **registered
   training-FLOP ledger**; accelerator-hours are a *separate REPORTED* quantity (they diverge whenever
   kernels/precision/auxiliary execution differ). [STIPULATED: ASM-0812 restated]
   **Twin-compute ledger [design input]:** an identical recipe is NOT sufficient matching — the
   interface arm can change (i) parameter count (interface module), (ii) token count (interface tokens
   in-corpus), (iii) sequence length, (iv) objectives/losses, (v) auxiliary execution
   (retrieval/verifier calls). The ledger must account each — including **last-layer FLOPs**
   [porian-2024] — plus an interface-token PARITY rule (how the plain arm compensates for interface
   tokens), pre-registered in P3-D-BASE.
2. **IsoFLOP construction.** Chinchilla approach 2 — for each budget, sweep model size at fixed FLOPs
   and read the valley — is the canonical fair placement [chinchilla-2022], with the Porian
   corrections (count last-layer FLOPs; scale warmup; tune-or-µP-fix the optimizer per scale)
   [porian-2024].
3. **Same data, same order, pinned checkpoints.** Pythia practice — identical corpus and data ORDER
   across arms/sizes, reconstructible dataloaders, seeded checkpoints [pythia-2023] — kills the
   data-order confound between interface and plain arms.
4. **Seeds are not optional at tiny scale.** 25 same-recipe BERT-base runs differing only in seed
   perform "substantially" differently downstream; the **Multi-Bootstrap** is the matched inference
   procedure [multiberts-2021, verified: 25 final + 140 intermediate checkpoints]. DataDecide runs
   **3 seeds** per config as baseline hygiene [datadecide-2025]; the speedrun requires cross-run
   statistical validation for a record [nanogpt-speedrun]. **ADOPT:** ≥3 seeds per (arm × width ×
   budget) cell at R-0, paired across arms by seed+data-order; direction read on the seed-mean with a
   registered uncertainty procedure — exact count from a pilot variance estimate (§7 open Q2).
5. **HP fairness via µP.** Maximal-update parametrization makes optimal HPs stable across width —
   demonstrated by outperforming published GPT-3-6.7B "by transferring from 40M parameters, with
   tuning cost only 7% of total pretraining cost" and BERT-large "from a model of 13M parameters"
   [mup-2022, verified verbatim]; µParam also flattens LR-sensitivity in the instability regime
   [wortsman-2023]. µP is the most attractive multi-width sweep under the total-tuning-compute
   symmetry budget, but NOT the only principled one — equal-tuning-budget per-scale search with a
   pre-registered selection rule is the registered **FALLBACK if the µP audit fails**, because µP's
   validity with **Muon-class optimizers** and with an **attached interface module** is *unverified*
   (µTransfer used Adam-class optimizers; §7 Q1). CAVEAT: depth-transfer holds for single-layer
   residual blocks but hits "fundamental limitations in all possible infinite-depth limits" for
   deeper (transformer-style) blocks [tp6-depth-2023, verified verbatim] — so **sweep WIDTH (+ token
   budget), hold DEPTH fixed per rung**.
6. **Interface-arm prior art helps in the tested configuration, not "at any scale."** kNN-LM: post-hoc
   interpolation, "a 2.9 point improvement with no additional training" to WikiText-103 perplexity
   15.79, in one configuration [knnlm-2019, verified verbatim]. RETRO: trained-in chunked
   cross-attention over a "2 trillion token database," "comparable performance to GPT-3 and Jurassic-1
   on the Pile, despite using 25× fewer parameters" — a comparison explicitly NOT resource-/lifecycle-
   matched (the 2T store sits outside the parameter count) [retro-2021, verified verbatim]. LEARNED
   interface *use* shows a within-lineage capacity association: Toolformer's "ability to leverage the
   provided tools only emerges at around 775M parameters: smaller models achieve similar performance
   both with and without tools" (GPT-2 124M/355M/775M/1.6B + GPT-J 6.7B sweep; exception = the easy
   Wikipedia search API) [toolformer-2023, **body §4.4 verified verbatim** via ar5iv — NOT an abstract
   claim]. Direction-only reading [EXTRAPOLATION — never a premise]: whether a kot-interface behaves
   like post-hoc retrieval (helps at 1M) or learned tool-use (needs 100M+) is exactly what ASM-0815's
   sweep measures; both priors are in the literature, so neither a tiny null nor a tiny win settles
   the family.
7. **Instability probes are cheap.** Large-scale instabilities (attention-logit growth, output-logit
   divergence) "also appear in small models when training at high learning rates," and the large-scale
   mitigations (QK-norm, warmup, weight decay, µParam) are "equally effective in this regime";
   activation/gradient-norm scaling can predict some instabilities "before they emerge"
   [wortsman-2023, verified verbatim]; OLMo-2 is the production distillation [olmo2-2024]. **ADOPT:**
   the R-0 twin recipe includes QK-norm + a registered LR-sensitivity check, so an interface-arm
   divergence is attributable.

---

## 5. SQ4 — designing the ≥3-point sweep (the §3.5 direction protocol's prior art)

### 5.1 The decision-theoretic anchor — DataDecide

[established][search 2026-07-19] DataDecide (arXiv:2504.11393, ICML 2025) is the closest external
ANALOGUE, one domain over: does a small experiment predict a larger-scale *decision*, for
PRETRAINING-DATA selection between standard-architecture models? Verified verbatim:
- "**25 corpora**" trained up to "**1B** parameters" / "up to **100B tokens**", "**3 random seeds**."
- "ranking of models at a single, small size (e.g., **150M** parameters) is a strong baseline for
  predicting best models at our larger target scale (**1B**) (~**80%** of comparisons correct)."
- "**No scaling law methods among 8 baselines** exceed the compute-decision frontier of single-scale
  predictions."
- "continuous likelihood metrics as proxies … makes benchmarks including MMLU, ARC, HellaSwag, MBPP,
  and HumanEval >80% predictable at the target 1B scale with just **0.01% of the compute**."
- (The draft's "14 scales / 30k+ checkpoints" are body/release-level details not on the abstract;
  they are the known DataDecide figures and consistent — see §11.)

It does **not** study symbolic-interface interventions, architecture changes, 5–30M models, or signed
treatment-effect trends. Consequences [speculative — analogical support, NOT validation]: (a) the
programme's choice of direction-reads over fitted-law extrapolation (ASM-0815) is CONSISTENT with the
best adjacent evidence, but DataDecide does not validate ASM-0815 *for interface effects* —
P3-E-GU-1/G5 create the first such evidence; (b) the ~20% flip-at-8× is a domain-specific floor on
trust in ANY single-scale read — the reason the gate ladder demands the same gate fail at two
consecutive rungs before a family closes and why G5 re-tests at two sizes; (c) sweep endpoints should
be continuous/likelihood metrics (agreeing with EVAL §5, carried).

### 5.2 Sweep geometry [design input, not a prereg]

- **Axes:** width ∈ ≥3 points (e.g. ~5M/~15M/~30M at R-0 under µP; R-1 confirm at 135M-class), and
  token budget ∈ ≥3 points per width, CENTRED on a **pilot-estimated** compute-optimal ratio for this
  architecture/data regime — Chinchilla ~20 tok/param is where the pilot *starts looking*, not a
  hardcoded constant (§3 fragile-constants) — e.g. 0.5×/1×/4× of the pilot centre. The 4× leg probes
  the lawful overtrained regime [gadre-2024]; its data-repetition license is out-of-regime and
  pilot-spot-checked [muennighoff-2023].
- **Parameterization:** µP across width, **fixed depth per rung** (Depth-µP caveat, §4.5; registered
  fallback = equal-budget per-scale tuning if the µP audit fails); deep-thin base shape with embedding
  sharing (embeddings dominate parameter count at 1–30M) [mobilellm-2024], **held fixed across arms**.
- **Recipe pin:** one modern recipe (modded-nanoGPT-class — a conditional prior pinned for cross-arm
  SYMMETRY, not a validated optimum) shared **verbatim** by interface and plain arms; optimizer =
  Muon-class, IDENTICAL across arms (optimizer choice alone is worth ~2× compute [muon-scalable-2025],
  so any slack there would masquerade as an interface effect).
- **Pairing:** same data order + seed pairing across arms; ≥3 seeds.
- **Read:** pre-registered DIRECTION of Δ(interface−plain) across the sweep per ASM-0815, on
  continuous metrics; fitted curves reported as DIAGNOSTIC only.
- **Format discipline (carried from EVAL §5.2):** because ~61% of ordinary downstream-scaling trends
  flip under benign format/prompt/harness changes, the harness and prompt format must be **frozen and
  identical across widths and across the R-0→R-1 confirmation** — otherwise format drift would
  masquerade as an interface-direction effect. (This is EVAL-owned but binds the TINY sweep directly.)
- **Feasibility:** cell count × per-cell cost (widths × budgets × seeds × 2 arms + tuning + pilot)
  must be shown to fit the **15–75 GPU-h** envelope (§3.6) BEFORE freeze — the pilot produces the
  per-cell cost; registered reduction order if the grid overflows = budget-points → widths → (last)
  seeds.

### 5.3 Failure modes the design must carry

- **Break-crossing:** a monotone read across 3 points can straddle a BNSL-style inflection
  [bnsl-2022]. Registered answer to a non-monotone triple = "add points / escalate one rung," never a
  post-hoc fit.
- **HP-unfairness masquerading as interface effect:** scale-dependent optimizer tuning moved published
  exponents [porian-2024]; µP + identical recipe is the counter.
- **Seed noise masquerading as direction:** MultiBERTs-scale variance [multiberts-2021]; counter =
  paired seeds + Multi-Bootstrap-style inference.
- **Metric floors:** owned by EVAL §6 (BLiMP discriminative across the tiny range; EWoK near-floor) —
  carried.
- **Judge-graded endpoints at R-0:** TinyStories-style GPT-4 grading imports an instrument trusted
  only at a measured style margin (§2.1) — avoid for primary endpoints.

---

## 6. SQ5 — what tiny-scale results HAVE and HAVE NOT predicted (co-reconciled with EVAL §5)

The literature answer is **two-sided and asymmetric**, and this is the *same asymmetry* P3-LR-EVAL §5
reports from the metric side: **pretraining loss (and loss-derived quantities) scale predictably;
downstream task performance and novel constructs frequently do not.**

**HAVE predicted (verified instances):**
- Loss and loss-derived quantities, incl. 32×-overtrained runs, from 300× less compute [gadre-2024];
  cross-dataset losses to ~20× the fitted budget [loss-to-loss-2024]; loss under one-GPU-day budgets
  [cramming-2022].
- Data-recipe DECISIONS at ~80% comparison accuracy from a single 150M scale — **in the
  pretraining-data-selection domain only** [datadecide-2025].
- Hyperparameters across width under µP (40M → 6.7B at 7% of pretraining cost) [mup-2022].
- Training instabilities and their mitigations (small-model high-LR proxies → large-scale fixes)
  [wortsman-2023].

**Have NOT predicted (verified instances):**
- Capability read through discontinuous metrics — apparent emergence is largely a metric artifact
  [schaeffer-emergence-2023 — UNVERIFIED-DIRECT this pass; verified at source in EVAL §5, 2026-07-19,
  which owns the metric side].
- Learned tool/interface use below a capacity threshold: no benefit ≤355M, benefit emerging ~775M in
  the Toolformer lineage [toolformer-2023] — a tiny-scale null that a larger scale REVERSED (within
  one lineage, confounded). **The single most important external datum for ASM-0815's "one tiny null
  is not a family kill" — as an existence proof of reversal, not a general threshold.**
- Architecture-shape conclusions across regimes: ~irrelevant in Kaplan's range [kaplan-2020] vs
  materially consequential at 125M/350M [mobilellm-2024] — a shape prior tuned at one rung does not
  transfer.
- ~20% of DataDecide's single-scale decisions flip at 8× scale [datadecide-2025]; scaling-law *fits*
  themselves have failed replication at publication quality [chinchilla-replication-2024].
- Whole-benchmark predictability is capability-space-dependent [ruan-observational-2024 —
  UNVERIFIED-DIRECT this pass; verified in EVAL §5, 2026-07-19].

**The reconciliation with P3-LR-EVAL §5 (load-bearing, [speculative, synthesised]):** EVAL §5.3
concluded that R-0/R-1 can validly **KILL** a family (negative/kill inferences don't require monotone
transfer — a zero coverage ceiling at G1 or a mechanism failure at G2 is a real no) but can**not**
validly **CERTIFY** that a *positive* interface margin transfers to R-3 (positive single-model
extrapolation of a novel construct is the unreliable case). The TRAINING-side evidence here is
**fully consistent** and sharpens it:
- The kot interface effect is a **novel downstream construct with no established scaling law** — none
  of the HAVE-predicted results (loss, HP-transfer, many-model continuous aggregates) cover it.
- The nearest positive external analogue, DataDecide, is a *data-selection* result (analogy only) and
  still flips ~20% at 8×.
- Toolformer is the concrete existence-proof that a tiny null can reverse upward — which is why the
  negative-read must be a **direction/trend across the sweep** (monotone-shrinking-to-zero or
  flat-negative), not a single tiny absolute null, and why a *growing-with-scale* trend promotes even
  from a negative base.
- **Net rule (both reports agree):** treat any R-1 positive interface margin as a **hypothesis about
  R-3, not evidence for it**, confirmable only via G5 two-size confirmation with format frozen across
  rungs; treat a *directional* R-0/R-1 kill as robust. The literature supplies the priors; the
  internal validation instrument is P3-E-GU-1/G5, never this review.

**Internal record [MEASURED, restated within envelopes]:** the programme has tiny-scale results only —
f2b-replicate's 135M+verifier positive (formal inputs, alignment-confounded), nsk1's text-channel
negative ("at every scale tested" ≤1.7B), l3a/a5 R-0 instrument exactness — and NOTHING measured
above 1.7B. No internal claim of upward prediction exists to audit.

---

## 7. Methods to adopt + open questions for Phase-1

**Adopt (P3-D-BASE / P3-D-GU design inputs)** [each verified at source unless noted]:

| # | Method | Source (verified §10) |
|---|---|---|
| 1 | Pinned modern twin recipe (Muon-class optimizer, rotary+QK-norm, deep-thin, embedding sharing), identical across arms — conditional prior for cross-arm symmetry, not a validated optimum | nanogpt-speedrun, muon-scalable-2025, mobilellm-2024 |
| 2 | µP width-parameterization; sweep width + token budget, hold depth; registered fallback = equal-tuning-budget per-scale search if the µP audit fails | mup-2022, tp6-depth-2023 |
| 3 | IsoFLOP twin placement w/ Porian corrections (last-layer FLOPs, warmup scaling, β₂ at small batch) | chinchilla-2022, porian-2024 |
| 4 | Same-data-same-order arms, reconstructible dataloaders, checkpoint grid | pythia-2023 |
| 5 | ≥3 paired seeds/cell; Multi-Bootstrap-style inference on seed-paired deltas | multiberts-2021, datadecide-2025 |
| 6 | ≤4-epoch repetition PRIOR for small R-0 corpora — out-of-regime extrapolation; pilot spot-check required | muennighoff-2023 |
| 7 | Direction-read over fitted-law extrapolation; continuous-likelihood endpoints; format frozen across rungs (EVAL §5) | datadecide-2025; ASM-0815; EVAL §5 |
| 8 | Decontamination statement for any curated/synthetic R-0 corpus | phi-ctnl-satire-2023; screener owned by P3-MF-0 |
| 9 | Anchor-vs-twin comparator separation (released overtrained anchors are pins, never "matched") | smollm2-2025; §2.5 |
| 10 | Stability instrumentation in the twin recipe (QK-norm, LR-sensitivity check, norm monitoring) | wortsman-2023, olmo2-2024 |
| 11 | Twin-compute ledger: training-FLOP accounting incl. interface module/tokens/sequence length/objectives/auxiliary execution + interface-token parity rule; accelerator-hours reported separately | porian-2024, babylm-2024-findings; ASM-0812 |

**Open questions Phase-1 must answer (not answered by the literature):**
1. **Does µP remain valid with a symbolic interface module attached — and with a Muon-class
   optimizer?** µP was derived for standard architectures with Adam-class optimizers; both
   interactions are unaudited. Registered fallback = equal-tuning-budget per-scale search. [P3-D-GU]
2. **Seed count for the direction read:** 3 is community hygiene; the count that powers a 3-point read
   against MultiBERTs-scale variance must come from a registered pilot variance estimate + power
   analysis, not a convention. [P3-D-GU]
3. **R-0 corpus choice:** TinyStories-class synthetic vs BabyLM-class natural vs kernel-adjacent
   synthetic — the distribution decides which interface effects are even *expressible* at 1–30M;
   needs an explicit decision + decontamination statement. [P3-D-GU with P3-D-BASE]
4. **Which interface class is H-GU's step-0 interface** (non-learned kNN-style injection vs learned
   tool-call vs trained-in cross-attention)? The literature prior and the expected capacity threshold
   differ by class (§4.6). [P3-D-GU, variant staging §3.5]
5. **What total-tuning-compute cap keeps the twin honest** given optimizer choice alone is worth ~2×
   [muon-scalable-2025]? Needs a number per rung. [P3-D-BASE]
6. **The exact twin estimand + compute ledger + feasibility:** what precisely is held equal when the
   interface changes parameter count, token count, sequence length, objectives, or auxiliary
   execution, and does the resulting grid fit the 15–75 GPU-h envelope? Both must exist as numbers at
   freeze. [P3-D-BASE with P3-D-GU]

---

## 8. Prior-failure judgements (capability-limited vs fundamental)

| Prior failure/null | Judgement | Basis (verified) |
|---|---|---|
| Developmental/NL-ordering curricula at 10M–100M words (BabyLM 2023 "largely unsuccessful"; 2024 wins located elsewhere) | **Recipe-limited at tested scope, single-cycle evidence — NOT a replicated null.** Deprioritise BabyLM-style curriculum arms as a prior; silent on the scoped *synthetic rule-depth* curriculum variant (§3.5), which stays in scope | babylm-2023/2024-findings |
| Tool-use benefit absent ≤355M (Toolformer lineage) | **Consistent with capacity limitation — within-lineage, confounded** (scale co-varies with base capability, call generation/filtering, task mix; benefit emerges ~775M); NOT a fundamental tiny-model limit and NOT a general interface threshold (kNN-LM/RETRO show non-learned/trained-in interfaces helping in their tested configs) | toolformer-2023, knnlm-2019, retro-2021 |
| Kaplan "shape doesn't matter" / Kaplan-vs-Chinchilla exponents | **Methodology-limited** — resolved by FLOP accounting, warmup, optimizer tuning | porian-2024 |
| Chinchilla approach-3 parametric fit | **Reporting/fitting-limited** — re-derivation reconciles; the isoFLOP result stands | chinchilla-replication-2024 |
| BabyLM multimodal track: nothing beat baselines | **Open/unexplained at scope** — a genuine community null, cause unattributed; irrelevant to P3 scope (no multimodal leg) | babylm-2024-findings |
| Our l3a-parse/a5-nl NL-boundary FAILs | Out of TINY scope — judged capability-limited (leading hypothesis) in PARSE.md §0 | MEASURED + PARSE.md, carried |

---

## 9. Phase-1 hand-off (what this review SETTLES / does NOT settle)

- **R-0 is literature-licensed but envelope-bound** (TinyStories capability at 1–30M); endpoints must
  be continuous metrics, not judge grades (§2.1, §5).
- **The twin METHOD TOOLBOX is assembled as conditional design priors** (§7 table 1–11). NOT closed:
  Phase-1 still owns the estimand-defining choices — interface class, R-0 corpus, µP validity with
  interface+Muon, pilot-powered seed count, tuning-compute cap, the concrete FLOP ledger + feasibility
  vs 15–75 GPU-h (§7 open Q1–6).
- **The direction protocol (ASM-0815) is CONSISTENT WITH the nearest external evidence — analogical
  support only** (DataDecide is a data-selection result; Toolformer is a confounded within-lineage
  observation): one tiny null must not kill a family, fitted-law extrapolation must not replace the
  sweep, and any R-1 positive is a G5-confirmable hypothesis, not evidence (§5.1, §6). Co-reconciled
  with P3-LR-EVAL §5's proxy-rung asymmetry: kills robust, positive-transfer unreliable, format frozen
  across rungs.
- **Released anchors ≠ twins** (SmolLM2 ~6,470 tok/param): P3-D-BASE carries two comparator classes
  with different claim scopes (§2.5).

---

## 10. Citation-verification table (ref → reachable at source? → supports the claim?)

All fetches 2026-07-19 unless noted. "Verbatim" = the load-bearing phrase/number was quoted back
from the fetched page.

| id | Reference (arXiv/URL) | Reachable this session? | Supports the load-bearing claim? |
|---|---|---|---|
| tinystories-2023 | 2305.07759 | Yes (abstract) | **Yes, verbatim** — <10M params / 1 block coherent; 3–4yo vocab; GPT-2-125M "rarely coherent"; GPT-4 grading |
| babylm-2023-findings | 2504.08165 (findings text) | Yes (search-corroborated text) | **Yes** — LTG-BERT won; curriculum "largely unsuccessful, though some showed modest improvements"; short-seq + KD |
| babylm-2024-findings | 2412.05149 | Yes | **Yes, verbatim** — 31 subs; hybrid causal-masked won; "strong relationship between training FLOPs and average performance"; multimodal null |
| gpt-bert-2024 | 2410.24159 | Corroborated (via babylm-2024) | **Yes (indirect)** — named 2024 winner by the findings paper; primary abstract not re-fetched |
| nanogpt-speedrun | GitHub @edf47a05… | Yes (raw README @commit) | **Yes, verbatim** — 45min→1.320min (#84, 2026-05-21), ≤3.28 FineWeb, 84 records, p<0.01, 8×H100 |
| muon-scalable-2025 | 2502.16982 | Yes | **Yes, verbatim** — ~2× vs AdamW at compute-optimal; +weight-decay +per-param scale; Moonlight 3B/16B-MoE, 5.7T tokens |
| smollm2-2025 | 2502.02737 | Yes | **Yes, verbatim** — 1.7B, "overtrain … ~11 trillion tokens"; FineMath/Stack-Edu/SmolTalk; beats Qwen2.5-1.5B, Llama3.2-1B |
| pythia-2023 | 2304.01373 | Yes | **Yes, verbatim** — 16 models 70M–12B, "exact same order," 154 checkpoints each |
| olmo2-2024 | 2501.00656 | Yes | **Yes, verbatim** — 7B/13B/32B; stability; "Dolmino Mix 1124" late-stage annealing; Pareto frontier vs compute |
| mobilellm-2024 | 2402.14905 | Yes | **Yes, verbatim** — "2.7%/4.3% accuracy boost over … 125M/350M"; deep-thin+emb-share+GQA; MobileLLM-LS +0.7/0.8 (source phrases as "%"; pp reading correct) |
| kaplan-2020 | 2001.08361 | Yes | **Yes, verbatim** — power law >7 orders; "width or depth have minimal effects within a wide range" |
| chinchilla-2022 | 2203.15556 | Yes | **Yes, verbatim** — equal N/D scaling (~20 tok/param); 400+ models 70M–16B, 5–500B tokens; MMLU 67.5%, >7% over Gopher |
| chinchilla-replication-2024 | 2404.10102 | Yes | **Yes, verbatim** — "over 600,000 experiments … fewer than 500"; narrow CIs; inconsistent with approaches 1–2 |
| porian-2024 | 2406.19146 | Yes | **Yes, verbatim** — last-layer cost + warmup + scale-dependent optimizer tuning; "β₂ … essential at lower batch sizes"; "LR decay … not essential" |
| mup-2022 | 2203.03466 | Yes | **Yes, verbatim** — HPs stable across width; GPT-3-6.7B from 40M at 7%; BERT-large from 13M |
| tp6-depth-2023 | 2310.02244 | Yes | **Yes, verbatim** — depthwise transfer for 1-layer blocks; "fundamental limitations in all possible infinite-depth limits" for deeper blocks |
| wortsman-2023 | 2309.14322 | Yes | **Yes, verbatim** — instabilities "appear in small models … at high learning rates"; mitigations "equally effective"; predictable from norm scaling |
| gadre-2024 | 2403.08540 | Yes | **Yes, verbatim** — 104 models 0.011B–6.9B, 3 distributions; 1.4B/900B (32× overtrained) from 300× less compute; perplexity→downstream at 20× less |
| muennighoff-2023 | 2305.16264 | Yes | **Yes, verbatim** — "up to 4 epochs … negligible changes to loss"; value decays to zero beyond; 900B tokens/9B params, 400 runs |
| cramming-2022 | 2212.14034 | Yes | **Yes, verbatim** — near-BERT on 1 GPU-day; "performance closely follows scaling laws observed in large-compute settings" |
| datadecide-2025 | 2504.11393 | Yes | **Yes, verbatim** — 25 corpora, ≤1B/100B, 3 seeds; single-scale 150M→1B ~80%; 8 baselines beaten; continuous likelihood best, 0.01% compute (14-scales/30k-ckpt are body-level, §11) |
| bnsl-2022 | 2210.14891 | Yes | **Partial** — breaks/double-descent/sharp-inflection modeling verbatim; "few-point extrapolation risk" is an interpretive extension, not an abstract warning (§11) |
| loss-to-loss-2024 | 2411.12925 | Yes | **Yes, verbatim** — shifted power laws train/test cross-dataset; "extrapolate well even at 20× the largest FLOP budget"; sometimes beats single-dataset |
| retro-2021 | 2112.04426 | Yes | **Yes, verbatim** — 2T-token database; "25× fewer parameters" comparable to GPT-3/Jurassic-1; chunked cross-attention |
| knnlm-2019 | 1911.00172 | Yes | **Yes, verbatim** — WikiText-103 15.79, "2.9 point improvement with no additional training" |
| toolformer-2023 | 2302.04761 (ar5iv body §4.4) | Yes (body, not abstract) | **Yes, verbatim (body)** — "only emerges at around 775M parameters"; sweep 124M/355M/775M/1.6B + GPT-J; Wikipedia-search exception |
| phi1-2023 | 2306.11644 | Yes | **Yes, verbatim** — 1.3B, 7B tokens; HumanEval 50.6, MBPP 55.5; phi-1-small 350M = 45% HumanEval |
| phi-ctnl-satire-2023 | 2309.08632 | Not re-fetched (satire) | **Assumed** — 1M-param benchmark-memorisation satire; well-known, non-numeric, flagged satire |
| multiberts-2021 | 2106.16163 | Yes | **Yes, verbatim** — 25 seed-only BERT-base runs; "substantially different performance"; Multi-Bootstrap; 25 final + 140 intermediate |
| schaeffer-emergence-2023 | 2304.15004 | UNVERIFIED-DIRECT | Corroborated — verified at source in `reports/lit-p3-eval.md` §5 (2026-07-19) |
| ruan-observational-2024 | 2405.10938 | UNVERIFIED-DIRECT | Corroborated — verified at source in `reports/lit-p3-eval.md` §5 (2026-07-19) |

**Citations that FAILED source-verification this session:** none. **No numeric divergence** of the
class caught elsewhere (Sardana / TinyAgent / TeCoD). Coverage: 25/29 re-fetched at source; 1
(gpt-bert) corroborated via the verified BabyLM-2024 findings; 1 (phi-ctnl) not re-fetched (satire,
non-numeric); 2 (schaeffer, ruan) corroborated via the sibling EVAL report, verified there 2026-07-19.
No claim in this document rests solely on an unverified source.

---

## 11. Divergences from the Fable draft (`docs/next/lit/TINY.md`)

The draft is accurate; every load-bearing number reproduced at source. Divergences are soft/interpretive:

1. **[no error — confirmation]** All 25 re-fetched load-bearing figures matched the draft's citations
   exactly (nanoGPT 45→1.32min/34×/84 records; SmolLM2 11T/6,470/325×; Muon 2×/5.7T; MobileLLM
   2.7/4.3+0.7/0.8; DataDecide ~80%/8/0.01%; Gadre 104/32×/300×/20×; Chinchilla-replication
   600k/500; µP 40M→6.7B@7%/13M; Toolformer 775M; kNN-LM −2.9/15.79; RETRO 25×/2T; phi-1
   50.6/55.5/45%; MultiBERTs 25+140). Unlike the sibling passes, **no Sardana/TinyAgent/TeCoD-class
   error is present.**
2. **Muennighoff wording — draft is *more conservative* than the source (safe direction).** The paper
   says "up to 4 epochs … **negligible changes to loss**"; the draft renders this as "comes close to
   (not identical with) unique-data performance." This is a deliberate under-claim relative to the
   source and is annotated as such in `TINY.sources.jsonl`. Not an error; kept in the formalization.
3. **BNSL — interpretive use flagged.** The draft uses BNSL for a "few-point extrapolation can cross
   an unseen break" caution. The BNSL abstract *demonstrates breaks exist and that standard forms miss
   them*; it does not verbatim warn about few-point extrapolation. The draft's inference is a
   reasonable extension (if hidden breaks exist, extrapolating from a few points is risky) but is
   [speculative], not [established]-verbatim. Tagged accordingly in §3 / §10.
4. **DataDecide "14 scales / 30k+ checkpoints" — body-level, not on the abstract.** The abstract
   confirms 25 corpora / ≤1B / ≤100B / 3 seeds / ~80% / 8 baselines / 0.01%. The "14 model sizes" and
   "30,000+ checkpoints" are the known DataDecide release figures (body/repo), consistent but not
   visible on the abstract; not load-bearing for any implication here. No correction needed.
5. **MobileLLM "%" vs "pp".** The abstract literally reads "2.7%/4.3% accuracy boost"; the draft calls
   these percentage points. In MobileLLM these ARE absolute average-accuracy gains (pp), so the
   draft's reading is **correct** — but the source's "%" phrasing is the same points-vs-percent
   ambiguity sibling passes flagged elsewhere, so it is noted explicitly here. The draft also correctly
   flags them as model-level (not single-factor) gains.
6. **Net additions of this pass (not in the draft):** (a) explicit statement that all load-bearing
   figures matched at source, no numeric error; (b) the **format-frozen-across-rungs** discipline
   (EVAL §5.2) added to the sweep geometry (§5.2) and adopt-table #7 — it binds the TINY sweep
   directly though EVAL owns it; (c) an explicit §6 reconciliation paragraph tying the TINY HAVE/HAVE-
   NOT list to EVAL §5.3's kills-robust / positive-transfer-unreliable asymmetry.

**Bottom line:** the draft's findings, implications, and prior-failure judgements are sound and
source-verified; this formalization adds source-level confirmation, the EVAL co-reconciliation, and
the format-freeze cross-reference. No load-bearing claim required revision.
