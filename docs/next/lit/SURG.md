# P3-LR-SURG — Compression, structured pruning, distillation + the exact invariances of transformer model surgery: decision-oriented literature review

> **Status: Phase-0 [LIT] deliverable of Programme-3 (bead kernel-of-truth-s55r.9).
> Nothing here is frozen, registered, or scheduled; no registry record, KB shard,
> or assumption entry is touched.** Author: Fable, 2026-07-11.
> Parent: `docs/next/programme-3-neurosymbolic-architecture.md` (rev 2) §3.5 +
> §5 P3-LR-SURG row. Spawns (recommendation only — the coordinator creates the
> bead): **P3-D-DD** (§8).
>
> **Tag convention** (house discipline mapped onto a lit-review):
> `[LIT-BACKED: source, year]` = external empirical fact read AT SOURCE this
> session (WebFetch/WebSearch 2026-07-11; URL in SURG.sources.jsonl). NOTE:
> this is author self-attestation — see §8 "Source counts" for what it does
> and does not make auditable;
> `[MEASURED: registry/...]` = restatement of a programme verdict inside its own
> envelope; `[STIPULATED]` = a judgement/recommendation made here;
> `[EXTRAPOLATION]` = forward projection, never a premise. Anything not
> verifiable at source is **UNVERIFIED** inline, never silently carried.

---

## 0. Dedup: what already exists in-repo, and what this review adds

Surveyed before anything was added (DEDUP-FIRST):

- `kb/records/` (639 records, kot-lit-1 schema): dense on **SAE
  mechanics/steering/geometry** (Gated SAEs 2404.16014, absorption 2409.14507,
  non-canonical 2502.04878, seed-instability 2501.16615, quasi-orthogonality
  2503.24277, universality 2410.06981, Gemma Scope, "How Pruning Reshapes
  Features" openalex-w7142557591, SSPU unlearning 2505.24428) and on
  **distillation-as-transfer** (KD survey 2402.13116, PaD 2305.13888,
  self-distillation knowledge injection 2412.14964, Llama SLayer 2410.02330,
  Atlas 2208.03299). It has essentially **nothing on retrained structured
  pruning as a compression practice** (no Minitron/Sheared-LLaMA/LLM-Pruner/
  SliceGPT records), **nothing on rotation/absorb invariance conditions**
  (no SliceGPT/QuaRot/SpinQuant/gauge-group records), and **nothing on
  size-vs-capability curves or knowledge-capacity scaling**. Where a KB record
  covers a fact I need, I cite the record and do NOT re-verify unless the fact
  is load-bearing here; KB records are recall infrastructure, not evidence.
  Per governance, nothing here is ingested into the KB — `SURG.sources.jsonl`
  is a passive staging file for the coordinator's central ingest.
- `reports/lit-llm-injection-priorart.md` — rule/knowledge-INJECTION prior art
  (P3-LR-RULE's parent). Injection is the *backfill* half of H-DD; this review
  does not re-derive its placement taxonomy, only cites where the store-side
  interface matters (§5).
- `docs/next/lit/{EVAL,PARSE,RAG}.md` — sibling Phase-0 reviews; no overlap
  with this scope except the shared skepticism protocol for unmatched-compute
  wins, which I restate in §6 rather than re-derive.
- Programme doc §3.5 [STIPULATED: ASM-0816] already names the four rev-1 H-DD
  errors. This review's job is to check those corrections against the
  literature and arm P3-D-DD; §2 finds all four consistent with the primary
  sources read, and sharpens #1 with a result the programme doc does not yet
  cite (the strict gauge group is claimed to be *smaller* than even the
  corrected claim assumed — §2.3, with a provenance caveat).

What is NEW here: the verified retrained-pruning+KD practice frontier and its
accounting (§1); the per-component invariance map with primary-source
conditions (§2); the SAE-geometry negative-results wall and what interp-guided
pruning actually achieved (§3); size-vs-capability and knowledge-capacity
anchors 100M–2B (§4); the H-DD prior-art verdict (§5); the matched-baseline
accounting table (§6); Phase-1 open questions (§7) and the P3-D-DD hand-off
(§8).

---

## 1. Retrained structured pruning + KD: the practice frontier the (iv) comparator must draw from

The programme corrected rev-1's pruning-without-recovery comparator to "the
strongest published-practice RETRAINED structured-pruning + KD baseline at
equal bytes and equal recovery compute" [STIPULATED: ASM-0816]. What that
means concretely:

- LOAD-BEARING: **Minitron** (NVIDIA) is the strongest published recipe at the
  relevant mechanism: joint width pruning (hidden/attention-head/MLP
  dimensions, activation-based importance) and/or depth pruning, followed by
  **knowledge-distillation retraining on <3% of the original data**. Deriving
  8B+4B from a 15B donor took **up to 40× fewer training tokens per model**
  than from-scratch, 1.8× compute saving across the family, and **up to 16%
  better MMLU than a from-scratch model of the same size under ISO-COMPUTE
  accounting — NOT at equal token count**: the from-scratch baseline receives
  MORE tokens because distillation pays the teacher's forward passes (§4.3/
  Table 11, re-verified this session: 4B pruned+distilled on 100B KD tokens
  scores 37.81 MMLU vs 26.24 for the 150B-token from-scratch twin; the
  asterisked rows denote iso-compute); results comparable to
  Mistral-7B/Gemma-7B/Llama-3-8B [LIT-BACKED: arXiv:2407.14679, 2024].
- The **practice sequel** adds the deployment-grade details: when the donor's
  original pretraining data is unavailable, **lightly fine-tune the teacher on
  the distillation dataset first ("teacher correction")** before KD; width
  pruning generally beats depth pruning at matched parameter cuts;
  Llama-3.1-8B→4B and Mistral-NeMo-12B→Minitron-8B (SOTA at release)
  [LIT-BACKED: arXiv:2408.11796, 2024].
- **Sheared-LLaMA** (ICLR 2024) is the other pillar: *targeted* structured
  pruning end-to-end to a pre-specified target shape (layers, heads,
  intermediate + hidden dims) + **dynamic batch loading** (re-mix the recovery
  data by per-domain loss). LLaMA2-7B→1.3B/2.7B **beats Pythia, INCITE,
  OpenLLaMA and concurrent TinyLlama at equivalent sizes with ~3% of
  from-scratch compute** [LIT-BACKED: arXiv:2310.06694 + ICLR'24
  openreview.net/forum?id=09iOdaeOzp, 2024]. Accounting caveat, load-bearing
  for §6: the 3% **excludes the donor's pretraining compute** — as a *derived
  artifact* claim it is honest; as a *total-cost* claim it is not.
- **LLM-Pruner** (NeurIPS 2023): gradient-based structural pruning over
  dependency-coupled groups, task-agnostic; recovery by LoRA in ~3 h on 50k
  samples at 20% ratio [LIT-BACKED: arXiv:2305.11627, 2023]. Useful as the
  cheap-recovery lower bound, not the comparator.
- **Layer pruning is shockingly cheap up to a point**: selecting blocks by
  inter-layer representational similarity and healing with QLoRA gives
  *minimal QA degradation until up to ~half the layers* are removed on some
  open-weight models (ICLR 2025) [LIT-BACKED: arXiv:2403.17887, 2025]. The KB
  corroborates from the injection side: shallow layers carry the
  knowledge-injection-critical structure (Llama SLayer, EMNLP-findings 2024)
  [KB: kb/records/arxiv_2410.02330.json, not re-verified]. Consequence for
  H-DD: *generic* capacity slack exists in depth; a concept-aligned method
  must beat the *depth-pruned+healed* point too, or it has found generic
  slack, not semantics [STIPULATED].
- **Distillation budgeting is now a measured science**: Apple's distillation
  scaling law (ICML 2025) predicts student performance from the compute split;
  **distillation beats supervised pretraining only below a compute level that
  scales predictably with student size, and only when the teacher is free or
  amortised**; the capacity gap (stronger teacher → worse student) is a
  learning-capacity gap [LIT-BACKED: arXiv:2502.08606, 2025]. This *directly
  parameterises* the "equal recovery compute" rule — but the law is
  regime-dependent and concerns compute-optimal distillation generally, not
  tiny-model pruning recovery specifically. Whether R-1-scale recovery budgets
  (135M/160M donors) fall inside KD's winning regime has NOT been computed
  here. HYPOTHESIS for P3-D-DD: they do, so the (iv) comparator should use KD
  rather than plain continued pretraining — P3-D-DD must apply the law's
  actual calculation at donor scale (and/or pilot both recovery modes) before
  pinning KD [STIPULATED — hypothesis, not a derived result].
- Caution the other way: **SliceGPT degrades faster on small models** — 25%
  slicing keeps 99% zero-shot on LLAMA2-70B/OPT-66B but only **90% on Phi-2
  (2.7B)** [LIT-BACKED: arXiv:2401.15024, ICLR 2024]. Small donors (135M–1.7B,
  our rungs) have *less* prunable slack; published big-model retention numbers
  must not be extrapolated down [EXTRAPOLATION-guard].

CANDIDATE for P3-D-DD [STIPULATED — proposed composition, NOT established
practice]: the (iv) comparator ingredients = Minitron-style joint width
pruning (+ the depth-pruned+healed variant as a sub-arm) + KD retraining with
teacher correction, data re-mixed Sheared-LLaMA-style, at *equal packed
KOT-SIZE/2 bytes and equal recovery tokens/FLOPs* as arm (i). CAVEATS the
design bead must resolve before this counts as "strongest published
practice": (a) **no cited paper evaluates this hybrid as a combined method**
— each ingredient is separately evidenced at 7–15B donors only; P3-D-DD must
benchmark candidate recipes on the actual 135M/160M donors before selecting
the comparator or fixing margins; (b) teacher correction, importance search,
dynamic remixing and recipe/hyperparameter selection all consume **tuning
compute that an equal-recovery-tokens/FLOPs rule does not capture** — it must
be counted symmetrically (§6); (c) **quantization and the resource-frontier
baseline sit outside this comparator** and are inherited from the
P3-D-FRONTIER controls. Anything weaker than a retrained-pruning+KD-class
comparator re-introduces the rev-1 straw-man; anything claiming more than
"candidate composition" overstates the literature.

---

## 2. The exact invariances of transformer surgery: what is actually proven

The rev-1 error was assuming arbitrary per-layer orthogonal rotations are
function-preserving. The literature now gives a precise, per-component map.

### 2.1 What IS exactly absorbable, and under what conditions

- LOAD-BEARING: **Computational invariance** (SliceGPT, ICLR 2024): an
  orthogonal transformation **Q of the residual stream** can be absorbed into
  the adjacent weight matrices with the network function unchanged, *provided
  the normalisation between blocks is (parameter-free) RMSNorm*
  [LIT-BACKED: arXiv:2401.15024, 2024]. The commutation identity, verified at
  source in QuaRot's derivation: **RMSNorm(X) = RMSNorm(XQᵀ)Q** — RMSNorm
  divides by the norm, rotations preserve norms
  [LIT-BACKED: arXiv:2404.00456 (HTML v2), 2024].
- **Preconditions, per component** [LIT-BACKED: arXiv:2404.00456, 2024]:
  - RMSNorm **per-channel gains must first be pre-fused** into adjacent weight
    matrices (input projections become Qᵀ·diag(α)·W), leaving parameter-free
    RMSNorm. LayerNorm networks must first be *converted* (mean-subtraction and
    scale absorbed into neighbours, SliceGPT's construction) — LayerNorm does
    not commute with Q directly.
  - Absorbable sites: W_q, W_k, W_v, W_up, W_gate (input side, as QᵀW after
    gain fusing); W_down, W_out (output side, as WQ); embeddings and the
    unembedding (rows rotated by the same global Q).
  - **NOT absorbable across the MLP nonlinearity**: a rotation of the MLP
    *inner* dimension does not commute with the elementwise/gating
    nonlinearity — QuaRot must run an **online Hadamard before W_down**
    because the gating nonlinearity regenerates structure that no weight-space
    absorption removes.
  - **NOT absorbable through RoPE**: rotary embeddings sit between the k/q
    projection and its use — "the existence of Pos prevents us from directly
    fusing the Hadamard matrix into W_q and W_k"; QuaRot applies *online
    head-wise* Hadamards to **queries and keys after RoPE** (both receive the
    matching rotation, so attention scores are unchanged); **values take a
    separate path** — a head-wise rotation pre-fused into W_v for KV-cache
    quantisation, needing no online transform (re-verified at source this
    session).
- **Global Q vs per-block Q_ℓ — two licit schemes, not one.** (a) If the
  rotation must be *fully absorbed into existing weights* with no new online
  operations (QuaRot's merged-rotation setting), the residual-addition
  structure forces a **single global Q** applied consistently at every
  residual read/write site. (b) **SliceGPT itself does NOT use one global Q**:
  because "the signals at different blocks of the network were not aligned",
  it applies a **different orthogonal matrix Q_ℓ at each block and inserts an
  explicit bridge matrix Qᵀ_{ℓ−1}Q_ℓ into each skip connection** — small
  online D×D operations that "cannot be pre-computed", accepted as overhead
  to enable slicing [LIT-BACKED: arXiv:2401.15024 §3.3/Fig. 4, re-verified at
  source this session — this CORRECTS the previous draft of this review,
  which wrongly stated SliceGPT uses one residual-stream Q]. Per-layer
  rotations change the function only if those bridges are omitted.
  Three symmetry questions that must not be conflated [STIPULATED]:
  (i) the strict gauge of the UNTOUCHED donor parameterisation (§2.3);
  (ii) invariances available after declared function-preserving
  re-parameterisations (gain fusing, LayerNorm conversion — this section);
  (iii) per-block invariances purchased with explicit online residual bridges
  (SliceGPT's actual scheme). P3-D-DD must derive all three per donor —
  global AND layer-specific — and validate each transformation with
  **end-to-end logits over a pinned corpus**, not per-matrix numerical checks
  alone.
  Tied embeddings (SmolLM2-135M ties input/output embeddings) are compatible
  with a single global Q — embedding and unembedding transform identically —
  but constrain scheme (b): the embedding side couples to Q_first and the
  unembedding to Q_last, so a tied matrix needs Q_first = Q_last or an
  explicit de-tying step, and either way the slicing errors of the two sides
  are coupled [STIPULATED — derivation for P3-D-DD to verify numerically per
  donor].
- **Slicing** (the surgery H-DD actually needs): after absorbing Q, deleting
  the trailing rows/columns (principal-component-ranked) shrinks the embedding
  dimension — this is NOT function-preserving; it is a controlled
  approximation, and what PCA minimises is the **L2 reconstruction error of
  the calibration activations** (the between-block signal matrix), NOT
  model-output or downstream behavioral error [LIT-BACKED: arXiv:2401.15024
  §3.4, re-verified at source this session]. Every H-DD "drop" step lives on
  this side of the line: the invariance gets you to a *favourable basis*; the
  drop itself is lossy, its objective is a proxy, and the behavioral damage
  must be measured directly [STIPULATED].

### 2.2 Rotations help — and the choice of rotation is not free

- **SpinQuant** (ICLR 2025): among output-invariant rotation
  parameterisations, *which* rotation you pick swings downstream zero-shot
  reasoning by **up to 13 points** at 4-bit; SpinQuant therefore *learns* the
  rotations (Stiefel-manifold optimisation) [LIT-BACKED: arXiv:2405.16406,
  2025]. The R1–R4 taxonomy (which merge into weights vs run online) is
  **UNVERIFIED** at source this session (full-text fetch 404'd) — carried as a
  flag; P3-D-DD should read the full paper before pinning its basis-selection
  variant. Implication either way: "rotate to a canonical basis" has a large
  *free parameter* — the basis-selection rule must be pinned in the prereg
  like any other IV [STIPULATED].

### 2.3 The gauge group is SMALLER than the corrected claim assumed

- LOAD-BEARING, new to the programme: with **generic (untouched) per-channel
  RMSNorm gain, the exact symmetry group of the coordinate system is only the
  signed-permutation group B_d = S_d ⋉ {±1}^d — not O(d)**; LayerNorm charts
  have only S_d **up to a global sign flip**. Permutation-only alignment is
  symmetry-*incomplete* for RMSNorm models (worked failure: SAE
  reconstruction NMSE 0.004 → 1.08 under permutation-only vs
  signed-permutation transport), and interpretability artifacts (steering
  vectors, SAEs, top-k neuron sets, attribution lists) must be co-transported
  under the same gauge element [LIT-BACKED: arXiv:2606.31963, 2026,
  re-verified this session]. WEIGHT caveat [STIPULATED]: this is a very
  recent single-author preprint scoped to *coordinate transport of
  interpretability artifacts across checkpoints* — the sharpest available
  statement of the strict checkpoint gauge, not the final answer to all
  transformer-surgery invariance questions. P3-D-DD must re-derive the
  B_d / S_d-with-sign-flip result independently per donor, not inherit it.
- Reconciliation [STIPULATED]: O(d) freedom exists only *after* the gain-fusing
  surgery of §2.1 (which changes the parameterisation, legitimately); on the
  *unmodified* donor the claimed exact invariance is B_d (RMSNorm) or
  S_d-with-global-sign-flip (LayerNorm). So P3-D-DD's "derived exact
  invariance group per donor" deliverable has three layers: (a) the strict
  gauge group of the donor as-parameterised (re-derived, per the caveat
  above); (b) the enlarged group available after declared,
  function-preserving refactorings (gain fusing, LayerNorm→RMSNorm
  conversion); (c) per-block Q_ℓ schemes with explicit Qᵀ_{ℓ−1}Q_ℓ residual
  bridges (§2.1) — each verified with end-to-end logits over a pinned corpus.
  Rev-2's correction #1 is consistent with the sources and *sharpened*:
  arbitrary bridge-free per-layer rotation was wrong; "one global rotation"
  is licit only after an explicit re-parameterisation step; per-block
  rotations additionally require explicit residual bridges.
- Related positive evidence that a shared/rotated basis is *meaningful*:
  jointly-learned functionality-preserving transformations align independently
  trained transformers onto low-loss-barrier linear interpolation paths —
  **near-zero barriers for medium-sized WikiText LMs; only small (nonzero)
  barriers for modern billion-parameter LLMs** [LIT-BACKED: arXiv:2606.23607,
  2026, re-verified this session — "near-zero" applies at medium scale only,
  not at billion-parameter scale]. The stronger
  "rotation hypothesis" framing (same function up to a residual-stream
  rotation learnable from one batch) appeared only in search snippets —
  **UNVERIFIED**, do not premise on it.

### 2.4 Fragility floor

- **Super weights**: pruning as few as ONE scalar parameter can destroy
  generation (perplexity up 3 orders of magnitude); identifiable data-free in
  a single forward pass; they induce rare massive "super activations"
  [LIT-BACKED: arXiv:2411.07191, 2024]. Any H-DD arm must locate and
  **document** the donor's super weights and treat their handling as a
  pre-registered **stratified/control variable** (protected vs not), rather
  than protecting them automatically — else a null result may be a
  single-coordinate artifact, and a positive one may hinge on an unexamined
  protection choice [STIPULATED].

---

## 3. SAE geometry and interpretability-guided pruning: a wall of measured negatives, one usable template

Rev-1's "SAE features give a removable orthogonal block" is dead several times
over; the corrected reformulation (concept-associated subspace, method an
experimental variable, causal gate mandatory) is exactly what the literature
supports.

- **Superposition is the baseline geometry**: models store more sparse
  features than dimensions as **non-orthogonal** directions; polysemanticity
  is strategic compression, with a phase transition governing when features
  share capacity [LIT-BACKED: arXiv:2209.10652, 2022]. There is no
  per-dimension concept ownership to find.
- **Even "linear" concept directions are non-orthogonal in the naive basis**:
  the right geometry is a *causal inner product* (a whitening-like transform
  under which causally separable concepts become orthogonal), validated on
  LLaMA-2 [LIT-BACKED: arXiv:2311.03658, ICML 2024]. Note the resonance with
  the encoder's own whitening step [MEASURED: encoder/ construction B,
  docs/architecture.md §1] — but the direction of use here is only: *any*
  concept-subspace identification for H-DD must estimate the metric, not
  assume Euclidean orthogonality [STIPULATED].
- **SAE dictionaries are not canonical, not stable, not complete**:
  - No canonical units: larger SAEs contain genuinely novel latents (stitching)
    and latents decompose into interpretable meta-latents ("Einstein" →
    "scientist"+"Germany"+"famous person") [LIT-BACKED: arXiv:2502.04878,
    2025].
  - Seed instability: only ~30% of features shared across random seeds
    (131K-latent SAE, Llama-3-8B); TopK worse than ReLU+L1
    [LIT-BACKED: arXiv:2501.16615, 2025].
  - Feature absorption: parent latents stop firing where child latents absorb
    them, across hundreds of LLM SAEs, not fixable by size/sparsity tuning —
    SAE latents are unreliable as COMPLETE concept indicators
    [LIT-BACKED: arXiv:2409.14507, NeurIPS 2025 oral].
  - At best quasi-orthogonal [KB: kb/records/arxiv_2503.24277.json, not
    re-verified].
- **Downstream utility of SAEs is currently negative vs baselines**: SAE
  probes do not consistently beat standard probing baselines across
  data-scarcity/imbalance/noise/shift regimes [LIT-BACKED: arXiv:2502.16681,
  2025]; the GDM mech-interp team found dense linear probes vastly outperform
  SAE probes (incl. OOD harmful-intent detection) and **deprioritised
  fundamental SAE research** (2025-03-26), while noting SAEs remain useful for
  dataset debugging [LIT-BACKED: Alignment Forum GDM post, 2025].
- **What interp-guided intervention HAS achieved (the usable template)**:
  Sparse Feature Circuits (ICLR 2025) discovers causal circuits of SAE
  features by attribution and — the part that matters for us — **SHIFT**:
  ablating human-judged task-irrelevant features measurably improves
  classifier generalisation [LIT-BACKED: arXiv:2403.19647, 2025]. This is the
  closest published ancestor of P3-E-DD-0 steps (1)–(2): identify → causally
  ablate → measure selective behavioral consequence. SAE-guided *unlearning*
  also works as targeted removal (SSPU: −3.22% harmful-knowledge accuracy vs
  strongest baseline on WMDP-Cyber, utility retained) — but it removes
  WITHOUT backfilling [LIT-BACKED: arXiv:2505.24428, 2025].
- **Pruning × SAE geometry**: under magnitude/Wanda pruning, RARE (low-firing)
  SAE features survive better than frequent ones (Spearman ρ=−1.0 in 11/17
  conditions); Wanda preserves feature geometry up to 3.7× better than
  magnitude pruning; and — the caution that matters — **geometric preservation
  does not predict causal importance** [LIT-BACKED: arXiv:2603.25325, 2026].
- **The localisation threat, verified**: causal-tracing localisation provides
  NO insight into which MLP layer is best to edit; editing succeeds across
  layers regardless of where tracing places the fact (NeurIPS 2023 spotlight)
  [LIT-BACKED: arXiv:2301.04213, 2023]. This is the single strongest published
  reason to believe H-DD's "semantically-identified" step may fail even when
  identification *looks* successful — and it is precisely why P3-E-DD-0
  demands ablate/patch selectivity AND store-reinjection restoration, not
  localisation evidence [STIPULATED].

DECISION for P3-D-DD [STIPULATED]: identification methods enter as pinned
experimental variables in this order of prior plausibility — (a) supervised
probes in an estimated (causal/whitened) metric, (b) SAE-derived subspaces via
pinned projection with signed-permutation-correct transport (§2.3), (c) dense
attribution/ablation screening à la SHIFT. Claims of "concept found" carry no
weight until P3-E-DD-0's selective-ablation + restoration criteria pass. The
mapper caution stands: any mapper-mediated concept matching inherits proxy
precision ~0.71 [MEASURED: registry/verdicts/m0a-llmproxy.json, weak proxy
pending human gold].

---

## 4. Size-vs-capability, 100M–2B: what the curves say

- **Controlled substrate**: Pythia — 16 models, 70M–12B, identical data in
  identical order, 154 checkpoints each with exact dataloader reconstruction
  [LIT-BACKED: arXiv:2304.01373, ICML 2023]. The natural second donor
  (Pythia-160M; LayerNorm + parallel blocks → a *different* invariance group
  than SmolLM2, which is the point of the two-donor requirement).
- **Practice frontier at our rungs**: SmolLM2 — a 135M/360M/1.7B family;
  **the 1.7B is trained on ~11T tokens** with multi-stage data-centric mixing
  and outperforms Qwen2.5-1.5B and Llama-3.2-1B. The abstract does NOT state
  the 135M/360M siblings' token counts — do not attribute ~11T to the 135M
  donor without checking the paper's training details
  [LIT-BACKED: arXiv:2502.02737, 2025]. The
  gap-to-frontier at 100M–2B is now mostly a *data* story, which is favourable
  for pruning+KD derivations (the recovery data quality lever is real and
  cheap) [STIPULATED].
- **Architecture matters below 1B**: deep-thin + embedding sharing + GQA gives
  +2.7pp/+4.3pp over prior 125M/350M SOTA (MobileLLM, ICML 2024)
  [LIT-BACKED: arXiv:2402.14905, 2024]. A width-slashed H-DD artifact lands in
  an architecture regime (thin-wide→thin-thin) where these choices dominate;
  the (iii) random-subspace control shares them by construction, the (iv)
  comparator must too [STIPULATED].
- LOAD-BEARING for the H-DD capacity math: **language models store at most
  ~2 bits of factual knowledge per parameter** (bit-complexity over controlled
  synthetic tuple corpora; stable under int8; GPT-2-with-RoPE matches
  LLaMA-style at storage; MoE/junk-data/under-exposure reduce it)
  [LIT-BACKED: arXiv:2404.05405, 2024]. Consequence [EXTRAPOLATION,
  registered as reasoning direction only]: the 2-bit/param figure is a
  **synthetic information-capacity sanity bound** — an order-of-magnitude
  anchor for how much factual content a parameter cut could plausibly have
  carried. It is NOT an upper bound on the packed store bytes needed to
  backfill: the paper estimates maximum factual entropy stored per parameter
  under controlled synthetic conditions, and an external store additionally
  pays addressing, keys, schema and retrieval-index overhead, so "dropping N
  params ⇒ ≲2N store bits" is an invalid inference. Use only as a sanity
  check in P3-D-POWER's G1 analogue, never as a store-size budget. Scope
  caveat: measured at GPT-2 scale on synthetic tuple corpora.
- **Small models degrade more under identical surgery** (SliceGPT Phi-2 vs
  70B, §1) — the published size-vs-retention direction is *against* easy wins
  at R-1 scale, which raises the value of the cheap P3-E-DD-0 kill
  [LIT-BACKED: arXiv:2401.15024, 2024].

---

## 5. The H-DD bet's prior art: has anyone dropped semantically-identified parameters and backfilled from an external store?

**Verdict: no exact prior art LOCATED IN THIS REVIEW** (session-bounded).
After targeted search (WebSearch, 2026-07-11), no published work was found
that (i) identifies concept-associated parameters/subspaces in an EXISTING
pretrained model, (ii) removes them structurally, and (iii) restores the lost
capability specifically from an external symbolic/typed store. The components
each exist separately — which is both encouragement (each step has precedent)
and the basis of the H-DD novelty claim [STIPULATED, search-bounded: absence
of evidence after a bounded search, not proof of absence].
AUDIT-TRAIL LIMITATION [STIPULATED]: the individual search strings,
databases/engines, per-query dates and inclusion/exclusion decisions were not
logged here or in `SURG.sources.jsonl`. This verdict therefore supports "no
exact prior art located in this review", NOT a durable novelty finding;
before the novelty claim becomes load-bearing, P3-D-DD (or the coordinator)
should re-run the search under a logged protocol.

Nearest neighbours, in decreasing proximity:

1. **LMLM — train-time knowledge externalisation** (closest to the
   *destination*): annotate the pretraining corpus with database lookups and
   **mask retrieved factual spans from the loss**, so the model learns lookup
   instead of memorisation; small LMLMs competitive with substantially larger
   vanilla LLMs; facts editable in the DB [LIT-BACKED: arXiv:2505.15962,
   2025]. Differences: trains a NEW model (no donor surgery, no identified
   subspace); the store is a flat fact DB, not a typed kernel. H-DD's
   distinctive claim survives; LMLM becomes both (a) evidence the
   store-backfilled *end state* is reachable, and (b) a candidate comparator
   arm at R-1 if training budget allows [STIPULATED]. Exact size-vs-match
   magnitudes not extracted from abstract — UNVERIFIED pending full-text read.
2. **Retrieval substitutes for parametric capacity**: RETRO matches
   GPT-3/Jurassic-1 on the Pile with **25× fewer parameters** given a 2T-token
   retrieval DB, and **RETROfit** retrofits a *pretrained* transformer with
   retrieval cheaply [LIT-BACKED: arXiv:2112.04426, 2022]; Atlas: 11B
   retrieval-augmented beats 540B PaLM on NQ-64-shot
   [KB: kb/records/arxiv_2208.03299.json, not re-verified]. Retrofit =
   add-capacity-without-removal; nobody measured *removal + retrieval
   restoration* on the same model.
3. **Factual capacity is separable and relocatable**: Memory Layers at Scale —
   sparse trainable KV memory replacing FFN capacity beats dense models given
   >2× compute and MoE at matched resources, largest gains on FACTUAL tasks,
   scaled to 128B memory params [LIT-BACKED: arXiv:2412.09764, 2024]. The
   architectural statement of H-DD's premise (facts live in a lookupable
   structure, not dense compute) — from the *training* side.
4. **Memorise-vs-retrieve is now a scaling-law question**: 30M–3B models under
   fixed data budgets; retrieval helps at all scales; a 3-D scaling framework
   (params × tokens × retrieval-corpus); optimal allocation task- and
   saturation-dependent [LIT-BACKED: arXiv:2604.00715, 2026]. Use in
   P3-D-DD's power analysis for how much store a given parameter cut plausibly
   buys back.
5. **Removal-without-backfill exists** (unlearning): SAE-subspace-guided
   projection removes targeted knowledge selectively with utility retained
   (SSPU) [LIT-BACKED: arXiv:2505.24428, 2025] — step (i)+(ii) without (iii).
   And **interp-guided ablation-with-purpose exists** (SHIFT)
   [LIT-BACKED: arXiv:2403.19647, 2025] — the causal-gate methodology.
6. **Against**: the Hase localisation negative (§3) says the "identified"
   step's evidence standard must be interventional; and the 2-bit/param result
   (§4) says what's dropped is *capacity*, not neatly addressable facts —
   both are why P3-E-DD-0 exists [LIT-BACKED: arXiv:2301.04213, 2023;
   arXiv:2404.05405, 2024].

---

## 6. What actually beat matched baselines, under what accounting (the skeptical ledger)

| Result | What it beat | Accounting honesty | Verdict for us |
|---|---|---|---|
| Minitron: pruned+KD beats from-scratch at same size, 40× fewer tokens [LIT-BACKED: 2407.14679] | from-scratch twin at equal size under ISO-COMPUTE, with UNEQUAL token counts (100B KD vs 150B scratch tokens — KD pays teacher forwards; §4.3/Table 11) | Donor pretraining compute EXCLUDED — legitimate for "derive a family from a paid-for donor", illegitimate for "cheaper than training" totals; tuning compute (teacher correction, importance search) also uncounted | A (iv)-comparator ingredient (§1 candidate); also the accounting template H-DD inherits (donor compute stated, never counted as free — programme §2.3 note "dimension-drop arms inherit their donor's training compute — stated") |
| Sheared-LLaMA beats Pythia/TinyLlama-class at 1.3B/2.7B with "3% compute" [LIT-BACKED: 2310.06694] | open from-scratch models of equal size | Same exclusion; also comparators differ in data quality | Confirms direction at OUR scale (1.3–2.7B); margins there are the non-inferiority anchor |
| SliceGPT 25%-cut ≈99% retention (70B) [LIT-BACKED: 2401.15024] | its own donor (no recovery training) | No-recovery, zero-shot; small-model figure is 90%, much worse | Never quote 70B retention for R-1 donors |
| RETRO ≈ GPT-3 at 25× fewer params [LIT-BACKED: 2112.04426] | matched-token GPT baselines | Retrieval DB (2T tokens) and retrieval FLOPs/IO not in the param count — bytes accounting absent | Exactly why KOT-SIZE/2 counts the packed store; a W1-style claim needs the store on the scale |
| Memory layers beat dense at >2× compute [LIT-BACKED: 2412.09764] | dense + MoE at matched resources | Compute-matched (good); memory params ARE counted | Cleanest matched-accounting win in the family |
| Distillation beats supervised (regime-bounded) [LIT-BACKED: 2502.08606] | supervised student at equal student compute | Teacher cost handled explicitly (the point of the law) | Use the law to SET recovery budgets, not just cite it |
| SHIFT improves generalisation by feature ablation [LIT-BACKED: 2403.19647] | unablated classifier + baselines | Human judgement in the loop (labelled) | Methodology import only |
| SAE probing/downstream: negatives [LIT-BACKED: 2502.16681; GDM 2025] | vs dense/standard probes | Well-matched baselines — that's the finding | Grounds for probe-first ordering in §3 |

Standing skepticism [STIPULATED]: every "X% of compute" claim in this
literature excludes donor pretraining; every retrieval-parity claim
under-counts store bytes/IO. KOT-SIZE/2 + KOT-LIFE/1 already close those two.
A THIRD systematic bias is NOT closed by existing rules:
**method-development/tuning compute** — teacher correction, importance
search, dynamic-remix scheduling, recipe and hyperparameter selection — is
invisible to an equal-recovery-tokens/FLOPs rule, so "equal recovery compute"
alone does not make arms comparable. PROPOSED IN-DOC (for the coordinator; no
registry write here): P3-D-DD's prereg must define a tuning-compute ledger
that is symmetric across arms (every arm may spend it; all spending is
counted). Additionally, quantization and the resource-frontier baseline sit
outside this table's comparator and must be inherited from the P3-D-FRONTIER
controls before any superiority claim. Existing accounting rules are
necessary but NOT yet sufficient for the (iv) comparator.

---

## 7. Open questions for Phase-1 (P3-D-DD must answer or pin)

1. **Donor pair + their derived invariance groups.** SmolLM2-135M (RMSNorm,
   tied embeddings, RoPE) vs Pythia-160M (LayerNorm, parallel attn+MLP,
   untied): derive (a) strict gauge group as-parameterised (expect B_d /
   S_d-with-global-sign-flip per §2.3 — re-derive independently, the source
   is a single-author preprint), (b) enlarged group after declared
   refactorings (gain-fusing; LayerNorm conversion), (c) per-block Q_ℓ
   schemes with explicit Qᵀ_{ℓ−1}Q_ℓ residual bridges (§2.1). Validation
   standard: **end-to-end logits over a pinned corpus for every
   transformation**, plus numerical-tolerance checks per site (incl. RoPE
   head-dim obstructions and the tied-embedding coupling).
2. **Basis-selection rule.** PCA-on-calibration (SliceGPT), learned rotation
   (SpinQuant — read full text first, R1–R4 UNVERIFIED), or
   probe-metric-aligned (causal inner product): pinned as an IV, one primary.
3. **Identification-method ordering** per §3 decision (probe-first, SAE as
   variant with correct gauge transport, SHIFT-style screening), and what
   "selective" means quantitatively in P3-E-DD-0 step (2) (effect-size ratio
   concept-relevant vs concept-irrelevant tasks; margins pre-registered).
4. **Super-weight handling** per §2.4: a pre-registered stratified/control
   variable (protected vs not), documented either way — cheap, data-free,
   must be in the harness before any ablation is interpreted.
5. **Non-inferiority margins + power**: 70B SliceGPT figures are out; but
   Sheared-LLaMA/Minitron deltas (7B→1.3B, 15B→4B) also do NOT transfer to
   135M/160M donors — **margins require a pilot benchmark of the candidate
   compression recipes on the actual donors** before being fixed. Apply the
   distillation scaling-law *calculation* at donor scale to set recovery
   budgets (§1 hypothesis); use the 2-bit/param figure only as a synthetic
   sanity bound (§4, never a store-size budget) + the 3-D
   memorise-vs-retrieve framework for the store-side Δ_max ceiling (feeds
   P3-D-POWER's G1 analogue).
6. **Recovery-compute symmetry rule**: tokens vs FLOPs; is teacher correction
   available to ALL arms (it must be, or (iv) is advantaged); dynamic batch
   loading allowed symmetrically; PLUS a tuning-compute ledger covering
   teacher correction, importance search, remix scheduling and
   recipe/hyperparameter selection, symmetric across arms (§6).
7. **Bytes parameterisation** (correction #3 discipline): explicit
   which-matrices-shrink-how table per arm; KOT-SIZE/2 measured bytes, never
   width fractions; embedding (linear) vs attention/MLP (≈quadratic) stated.
8. **Store-backfill interface** for P3-E-DD-0 step (4): retrieval-to-context
   vs KV-injection (AtlasKV-class, KB) vs memory-layer retrofit — pick the
   cheapest that is NLB-compatible; oracle-addressed version labelled
   `oracle-diagnostic` per ASM-0814.
9. **Whether to add an LMLM-style arm** (train-time externalisation) as a
   destination-architecture reference at R-0/R-1, budget permitting — it is
   the only published system already living at H-DD's end state.
10. **Control inheritance**: the full P3-D-FRONTIER resource-frontier
    baseline and the generic-RAG controls apply BEFORE any superiority claim
    — quantization and the frontier baseline are outside the (iv) comparator
    (§1, §6) and must not be silently dropped.

---

## 8. Phase-1 hand-off

**Spawns: P3-D-DD** (per §5 table of the programme doc; the coordinator
creates the bead — none created here, per governance).

Recommended `bd create` (for the coordinator):

- **P3-D-DD** — [DESIGN] P1, blocked by P3-LR-SURG (this deliverable).
  Deliverable per programme §5 row: invariance-group derivation per donor +
  P3-E-DD-0 causal gate + updated arm matrix with retrained-pruning+KD
  comparator + non-inferiority margins (§3.5). Opening inputs now available:
  the (iv) CANDIDATE comparator composition + its pilot obligation (§1), the
  three-layer invariance-group derivation plan incl. the strict-gauge
  re-derivation and the per-block-bridge scheme (§2.1, §2.3), the
  identification-method ordering + causal-gate evidence standard (§3), the
  capacity/margin anchors and their limits (§4, §6), the session-bounded
  prior-art map + LMLM reference arm option (§5), and the ten pinned open
  questions (§7).

**What this review hands off** (as Phase-1 hypotheses and derivation
obligations — NOT settled conclusions; P3-D-DD must derive, pilot, or pin
each rather than inherit it):

1. INVARIANCE (derivation obligation): the rev-2 H-DD corrections (ASM-0816)
   are consistent with the primary sources read, and correction #1 is
   sharpened — the strict gauge of an unmodified RMSNorm donor is claimed
   (single-author preprint, to be independently re-derived) to be only signed
   permutations B_d, with LayerNorm at S_d up to a global sign flip; O(d)
   freedom appears only after declared gain-fusing/norm-conversion
   refactorings; and per-block Q_ℓ is additionally licit with explicit
   Qᵀ_{ℓ−1}Q_ℓ residual bridges — SliceGPT's actual scheme. P3-D-DD derives
   BOTH global and layer-specific invariances per donor and validates every
   transformation with end-to-end logits over a pinned corpus (§2).
2. COMPARATOR (pilot obligation): the (iv) comparator is a CANDIDATE
   composition — Minitron-recipe width pruning + KD with teacher correction +
   Sheared-LLaMA data re-mixing, depth-pruned+healed sub-arm — that no cited
   paper evaluates as a combined method, and whose supporting evidence sits
   at 7–15B donors. P3-D-DD must benchmark candidate recipes on the actual
   135M/160M donors before selecting the comparator or fixing margins, and
   must count tuning compute (§1, §6).
3. IDENTIFICATION ORDERING (literature-supported working position):
   SAE-orthogonal-block thinking is contradicted across the literature —
   absorption, non-canonicity, seed instability, probing negatives, GDM
   deprioritisation. Probe-first identification; SAE as pinned variant with
   gauge-correct transport; causal gate mandatory. Best-supported starting
   ordering, still pinned as an experimental variable, not a theorem (§3).
4. PRIOR ART (session-bounded finding): no exact prior art for
   semantically-identified-drop + store-backfill was LOCATED IN THIS REVIEW;
   the search protocol was not logged, so this is not a durable novelty
   finding — re-run under a logged protocol before load-bearing use. Each
   component is separately precedented (LMLM, RETROfit, memory layers, SSPU,
   SHIFT), and two published threats (localisation ≠ editability;
   capacity-not-facts) are exactly what P3-E-DD-0's design must answer (§5).
5. ACCOUNTING (open — proposal in-doc): donor-compute exclusion and
   store-byte under-counting are closed by KOT-SIZE/2 + KOT-LIFE/1;
   method-development/tuning compute is NOT — P3-D-DD must add a symmetric
   tuning-compute ledger; and the full P3-D-FRONTIER + generic-RAG controls
   (incl. quantization) are inherited before any superiority claim (§6).

**Source counts**: 35 sources in `SURG.sources.jsonl` — 31 read at primary
source this session and marked `verified:true`, 4 carried flagged
(`verified:false`: 3 cited from KB records not re-verified this session, 1
explicit UNVERIFIED gap — the LMLM magnitude details; the SpinQuant R1–R4
taxonomy and the "rotation hypothesis" framing are additionally flagged
UNVERIFIED inline within otherwise-verified entries).
VERIFICATION SEMANTICS [STIPULATED]: `verified:true` records the author's own
at-source read (WebFetch, 2026-07-11) — an attestation, not an independently
auditable verification. The JSONL carries no per-claim page/section/table
locators, excerpts, or version dates, except for the claims re-verified in
the 2026-07-11 revision pass, whose claim text now cites locators
(SliceGPT §3.3/Fig. 4 + §3.4; Minitron §4.3/Table 11; QuaRot RoPE handling;
LMC barrier scales; signed-perm gauge statement; LMLM title at HTML v2).
Treat the JSONL as recall infrastructure; re-verify with locators before any
load-bearing use.
