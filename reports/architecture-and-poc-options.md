# Kernel of Truth — Architecture-Integration Options and PoC Harness

Research agent report, 2026-07-07. Programme: NSM-style kernel (~65 primes + explication molecules) with canonical **training-free** concept vectors integrated into LM/LCM architectures. Coordination: sparq-org/sparq#1683.

Evidence tags: **[established]** = verified against sources or standard, well-documented practice; **[claimed]** = reported by a source or confident recall, not independently verified; **[speculative]** = our inference/design judgement.

---

## PART 1 — Integration mechanics

### 1.1 Tokenizer → embedding → transformer → lm_head: the mechanics that matter

**Pipeline** [established]. Tokenizer maps text → integer ids over vocab `V`. `nn.Embedding(V, d)` is a lookup: row `i` is token `i`'s vector. The transformer stack maps embedded sequences → hidden states `h ∈ R^d`. `lm_head` is a linear map `R^d → R^V`; logits `z_i = h·W_out[i] (+ b_i)`, softmaxed for next-token probability.

**Adding vocabulary rows** [established]. In HF Transformers: `tokenizer.add_tokens([...])` (or `add_special_tokens`) then `model.resize_token_embeddings(len(tokenizer))` appends rows to both the input embedding and (if untied) the lm_head. New rows are randomly initialised; recent Transformers versions default to *mean-resizing* (new rows ~ multivariate normal around the mean of existing embeddings) which markedly improves convergence for added tokens [claimed — HF docs/release notes]. For our purposes we then **overwrite the new rows with kernel vectors** in a `torch.no_grad()` block. One practical caveat: resizing pads vocab to a multiple (e.g. 64) for kernel efficiency; the tokenizer/vocab bookkeeping must stay consistent.

**Per-row freezing** [established — this is standard, three interchangeable techniques]:
1. **Gradient masking via hook**: `requires_grad` is tensor-granular, not row-granular, so the standard trick is `embedding.weight.register_hook(lambda g: g * mask)` where `mask` zeroes kernel rows (or the complement). Documented in practice (e.g. [transformers#5570](https://github.com/huggingface/transformers/issues/5570), partial-freezing write-ups).
2. **Two-module decomposition**: separate `nn.Embedding` for frozen kernel rows (`requires_grad_(False)`) and trainable rows, routed by id range. Cleanest semantics; slightly more code.
3. **HF PEFT `TrainableTokens` / `trainable_token_indices`** [established — [PEFT docs](https://huggingface.co/docs/peft/en/package_reference/trainable_tokens)]: marks *listed* token rows trainable and leaves the rest untouched; usable standalone or inside `LoraConfig`. This is the inverse selection of what we want for condition (a) (freeze kernel rows, train the rest), but exactly what we want for adapter-style setups (train only non-kernel added rows), and it proves row-granular training is first-class in the ecosystem now. Known rough edges: [peft#2653](https://github.com/huggingface/peft/issues/2653), DeepSpeed ZeRO-3 incompatibility [peft#2603].

**Critical gotcha — weight decay and optimizer state** [established]: zeroing gradients does **not** freeze a row under AdamW, because decoupled weight decay shrinks weights independently of the gradient. Either (i) put the embedding in a no-weight-decay param group, (ii) re-copy kernel rows after each `optimizer.step()`, or (iii) use the two-module decomposition. Any E1-style experiment that ignores this silently un-freezes the kernel and invalidates the result. Also note momentum: if a row ever received gradient before masking was attached, Adam momentum keeps moving it.

**Tied lm_head and fixed OUTPUT concepts** [established]. Weight tying (`W_out = W_emb`; Press & Wolf, arXiv:1608.05859; Inan et al., arXiv:1611.01462) is default in GPT-2/SmolLM2-class models (`config.tie_word_embeddings`). Consequences:
- With tying, freezing input rows automatically freezes the corresponding **output logit directions**: the model emits concept `c` when it shapes `h` to have high dot product with the fixed `e_c`. So yes, the model **can emit reserved concept tokens through the ordinary softmax** — the fixed row acts as a fixed read-out direction, and the burden moves to the hidden states. This is the cleanest formulation of "fixed output concepts".
- **Norm calibration matters**: logit scale is `‖h‖‖e_c‖cosθ`, so kernel rows with norms far from the learned-row distribution are systematically under/over-selected. Kernel vectors should be norm-matched to the embedding distribution (or a learned per-row scalar gain allowed — a minimal, honest relaxation). Rare/unusual rows are known to degenerate logits (arXiv:2109.03127) [established].
- **Untied alternative**: untie and freeze only output rows (fixed decode directions, free input semantics) or vice versa — useful ablation axis.
- **Nearest-neighbour decode over kernel rows**: instead of softmax over extended vocab, add a regression head that outputs a continuous vector decoded by cosine-NN against the kernel matrix. Precedent: LCM's MSE-regression variant, which Meta found *clearly inferior* to diffusion/quantised variants for sentence-embedding prediction (arXiv:2412.08821) [established]; SONAR-LLM (arXiv:2508.05305) fixes this by back-propagating token-level cross-entropy through a frozen decoder [claimed]. For a small discrete kernel (~65–500 concepts) the softmax-over-extended-vocab route is simpler and better behaved; NN-decode only becomes interesting when concepts are *composed* into novel vectors (see E4's unseen-concept test).

### 1.2 Candidate architectures

**(a) Reserved frozen vocab rows ("concept tokens") in an otherwise normal LM.**
Sketch: extend vocab with `<c:GOOD>`, `<c:WANT>`, … rows set to kernel vectors, frozen (input and tied output); phrase→concept mapper (lemma/multiword lexicon first, embedding-similarity later) rewrites or augments training text with concept tokens; train the LM from scratch or finetune.
- *Tests*: the strongest, most direct claim — that fixed, structure-derived coordinates can serve as a native I/O interface without co-adaptation, and that their **content** (not just their fixedness) helps: sample efficiency, concept-relation probes, emission quality.
- *Cannot test*: internal rule-based inference; whether the model actually *uses* the geometry rather than treating rows as arbitrary ids. The Unicode-glyph result (§1.3) is a warning: transformers happily build semantics *on top of* arbitrary frozen vectors, so (a) without a random-frozen control is uninterpretable. Also cannot test cross-model canonicalness (one model, one basis).

**(b) Projection/adapter between kernel space and model embedding space.**
Sketch: kernel vectors fixed in kernel space `R^k`; a small trained map `A: R^k → R^d` (linear, or 2-layer MLP) produces the model-facing vectors; optionally `A` is shared across all concepts (so ~`k×d` trainable params total, not per-concept).
- *Precedent*: Frozen (arXiv:2106.13884) — trained encoder into a frozen LM; GraphToken (arXiv:2402.05862) — trained projection of structured data into frozen-LLM soft tokens; CoLLEGe (arXiv:2403.15362) — generated concept embeddings for frozen LLMs; frozen-tower alignment generally (LiT, arXiv:2111.07991) [established].
- *Tests*: a weaker but well-posed claim — that kernel **geometry** (relative positions) is informative and linearly compatible with LM space. Since any full-rank `A` can absorb a rotation, the honest control is an adapter trained on a **randomly shuffled kernel** (concept↔vector assignment permuted): if shuffled does as well, the geometry carries nothing.
- *Cannot test*: "training-free" in the strong sense (the adapter is trained, per model); canonical coordinates (only geometry-up-to-linear-map). This is, however, the most *plausible* route given relative-representation results (arXiv:2209.15430: latent spaces of independently trained models match only up to transformation) [established].

**(c) Concept-level encoder/decoder around a latent LM (LCM-style).**
Sketch: kernel space *is* the latent interface. Encoder: text → explication → bag/sequence of kernel vectors (the encoder can be symbolic: the phrase→concept mapper plus explication lookup — genuinely training-free). Latent LM: small transformer autoregressing over kernel-vector sequences. Decoder: kernel sequence → text (this must be trained; bootstrapping problem).
- *Precedent*: LCM (arXiv:2412.08821) — autoregression in SONAR sentence-embedding space at 1.6B/7B scale; found regression hard, diffusion/quantised better [established]. SONAR-LLM (arXiv:2508.05305) [claimed].
- *Tests*: the **dense concept-level I/O** claim directly — can a ~65-prime compositional space carry enough information to drive generation; information-per-symbol economics.
- *Cannot test*: integration into an existing LM (it's a separate architecture); and it's the most compute- and engineering-heavy option. LCM's own mixed results at 7B suggest this is high-risk at PoC scale [speculative]. Defer to phase 2, but a **toy** version over TinyStories-domain vocabulary is tractable (E3).

**(d) GNN / graph-token input: explication trees fed as graphs.**
Sketch: an explication is a tree/DAG over primes; a small GNN or graph transformer encodes it; output vectors enter the LM as soft tokens (GraphToken, arXiv:2402.05862 — encoder+projection trained, LLM frozen; GraphGPT, arXiv:2310.13023 — graph-text alignment projector + instruction tuning) [established]. Kernel vectors serve as **fixed node features**.
- *Tests*: whether explicit explication *structure* at the input improves compositional/systematic generalisation vs the same content flattened to text; whether fixed node features suffice (vs learned node embeddings — clean ablation).
- *Cannot test*: output-side concepts; canonical coordinates as LM-native vocabulary (the graph encoder is trained and can relabel everything).

**(e) Retrieval-style: kernel as external memory with cross-attention.**
Sketch: kernel matrix (concepts × vectors, plus explication links) as a memory bank; model reads it via cross-attention (RETRO, arXiv:2112.04426; Memorizing Transformers, arXiv:2203.08913) or output distributions are interpolated with nearest-neighbour lookups (kNN-LM, arXiv:1911.00172 — notable because the memory is consulted **without any training**, inference-time only) [established].
- *Tests*: kernel-as-consultable-knowledge; the kNN-LM variant tests a genuinely training-free form of grounding (does interpolating toward kernel-neighbour predictions improve concept-token perplexity at inference time, zero training?).
- *Cannot test*: kernel as native representational substrate; concept-level I/O. It's the weakest form of the hypothesis but the cheapest to bolt onto pretrained models.

### 1.3 Direct prior art (the search you asked for)

**Closest hit — and the most important calibration for the whole programme:**
- **"Emergent Semantics Beyond Token Embeddings: Transformer LMs with Frozen Visual Unicode Representations" (arXiv:2507.04886)** [established — abstract verified]. Embedding layer entirely frozen, vectors derived from the *visual structure of Unicode glyphs* (non-semantic, precomputed). Models converge robustly and **outperform architecturally identical trainable-embedding models on MMLU**. Authors' conclusion: semantics is an emergent property of the stack; the embedding layer functions as "structural primitives", and trainable embeddings may suffer "representational interference". **Implication cuts both ways**: (i) good news — frozen rows are not a handicap, so the mechanics of the kernel are viable; (ii) bad news — it suggests the *content* of frozen vectors may be nearly irrelevant, which is exactly the null hypothesis our E1/E4 must beat. Any kernel PoC that only compares frozen-kernel vs *trainable* embeddings is confounded; the load-bearing comparison is **kernel-frozen vs random-frozen**.
- **CoLLEGe (arXiv:2403.15362)** [established]: few-shot *generation* of new concept embeddings that a frozen LM can immediately use — proves new concept rows can be injected without retraining the LM, but embeddings are generated per-context, not canonical/fixed.
- **"Towards Universal Semantics with Large Language Models" (arXiv:2505.11764)** [established]: first NSM × LLM work — LLMs generating NSM explications. Not an architecture paper, but a ready-made pipeline precedent for *building* the kernel's explication data (and a citable bridge from Wierzbicka/Goddard's ~65 primes to NLP).
- **Concept-bottleneck LMs**: CB-LLMs (arXiv:2412.07992) and Concept Layers (arXiv:2502.13632) [established] insert human-interpretable concept layers into LLMs — concept-level internal interfaces exist and work, but the concept directions are *learned*, not fixed a priori.
- **LCM (arXiv:2412.08821) / SONAR-LLM (arXiv:2508.05305)** — concept-level (sentence-level) latent LMs; the latent space is a *pretrained learned* encoder space, not a designed kernel.
- **Soft prompts / P-tuning (arXiv:2104.08691)** [established]: the exact inverse of our setup (trained vectors, frozen model) — useful contrast when writing up.
- **Geometry evidence, pro and con** [established]: linear representation hypothesis (arXiv:2311.03658) and sparse-autoencoder dictionary features (Anthropic's Towards/Scaling Monosemanticity) show concepts are approximately linear directions — but learned, per-model. Relative representations (arXiv:2209.15430) show independently trained spaces match only up to a transform — this *weakens* raw architecture (a)'s "canonical coordinates" claim and *supports* adapter route (b). The Platonic Representation Hypothesis (arXiv:2405.07987) argues representations converge across models/modalities — mild support for the idea that a canonical space could exist at all.
- **Training-free structure-derived vectors** (how to actually *make* kernel vectors without training a text model): graph/spectral embeddings of the explication graph; hyperbolic embeddings of hierarchies (Poincaré, arXiv:1705.08039); deterministic codebooks (Bit Cipher, arXiv:2311.11012) [established as techniques; their use for an NSM kernel is [speculative]/novel].

**Verdict**: searches for "frozen concept embeddings", "fixed semantic anchors", "training-free grounding tokens" surface adjacent work (above) but **no published attempt to build fixed, human-designed (NSM-style) concept coordinates into an LM's vocabulary** — positive or negative. The niche appears genuinely open [established, to the limit of several web searches]; the nearest result (2507.04886) is best read as a *pre-registered threat* to the hypothesis rather than support.

---

## PART 2 — Practical harness

### 2.1 This box (audited 2026-07-07)

| Item | Found |
|---|---|
| Python | 3.9.25 (EOL Oct 2025 [established]; current transformers/torch increasingly require ≥3.10 [claimed]) |
| pip | 21.3.1 (user-local, `pip3`; no `pip` on PATH) |
| torch / numpy / any ML pkgs | **none installed** |
| CPU | 2 cores (shared with live server per box constraints) |
| RAM | 7.6 GiB total, ~3.7 GiB available, 8 GiB swap |
| **Disk** | **/ is 95% full — 3.0 GiB free of 50 GiB** |
| Compilers | no gcc/g++/cmake/make; git present |

**Feasibility verdict**: this box **cannot host the PoC compute**. The binding constraint is disk, not CPU: a CPU-only torch install is ~1.5–2 GiB with deps [established], which does not safely fit in 3.0 GiB on a volume shared with a live server, before any datasets or checkpoints. No compilers, so llama.cpp would need a prebuilt release binary (available, ~tens of MB [claimed]); a SmolLM2-135M Q4 GGUF (~100 MB) would fit, making *small inference-only demos* marginally possible — but with 2 shared cores and a live server, even that should be `nice`d and brief. **Appropriate roles for this box**: kernel data engineering (explication lexicon, phrase→concept mapper in pure Python/Node), experiment specs, orchestration of remote runs, and report writing. All training and all torch-based analysis (including E2 below) go to rented hardware or a laptop.

### 2.2 Small-model options for the PoC

- **TinyStories (arXiv:2305.07759)** [established]: GPT-generated children's-story corpus (~2.1M stories); models from ~1M to 33M params produce coherent English. Training budget: paper states models train in **under a day on a single GPU**; the released 33M checkpoint used 4×V100, ~20 epochs, ctx 512 [claimed — HF model-card discussion]; community replications pretrain 1M–33M models **in under an hour on consumer hardware** [claimed]. This is the ideal substrate for from-scratch embedding-freezing experiments: restricted vocabulary (a few thousand word types), small models where the embedding matrix is a large fraction of parameters, and an existing GPT-4-graded eval protocol. Use a **small vocab (4–8k BPE or word-level)** so ~65–500 kernel rows are a meaningful fraction.
- **nanoGPT** [established]: babyGPT/shakespeare-char configs (~1–10M params) train in minutes on one GPU; CPU-only training of a ~1M char-level model is hours-scale on a laptop — but not on this box (no torch fits). GPT-2 124M reproduction is ~8×A100×4 days — out of scope.
- **SmolLM2-135M/360M (arXiv:2502.02737)** [established]: strong pretrained checkpoints (2T/4T tokens — pretraining obviously out of reach; we only finetune/probe). LoRA finetuning 135M on 2 CPU cores: roughly 10²–10³ tok/s → 10M tokens ≈ 10–30 h [speculative estimate]; on a T4 it's minutes-to-an-hour. Use for finetuning-based experiments (E3/E5) and geometry probes (E2).
- **Qwen2.5-0.5B**: CPU LoRA impractical (days); fine on T4/A10G (~1–3 h for 10–20M tokens) [speculative estimate]. Only needed if we want a second model family for generality.
- **llama.cpp**: inference/logits/embeddings only — no training path for freezing experiments; useful for cheap qualitative demos and for E5-style inference-time kNN interpolation prototyping [established].
- **Rented hardware** [established — pricing pages, July 2026]: T4 from ~$0.06/hr (marketplace spot) to ~$0.53/hr (AWS g4dn.xlarge on-demand); A10G ~$0.43–1.01/hr (g5.xlarge on-demand $1.006/hr). The **entire E1–E5 programme fits in ~30–80 GPU-hours ≈ $10–80** on T4/A10G spot — trivially affordable; do not contort the design to fit this box.

### 2.3 Falsifiable PoC experiments (shortlist, priority order)

Common rules: ≥3 seeds per condition; success criteria fixed before running; all conditions matched for tokens, steps, LR schedule, and embedding-norm distribution; kernel vectors derived **training-free** from the explication graph (spectral/hyperbolic embedding of primes+molecules; no text-encoder shortcuts, which would smuggle in trained semantics).

**E2 — Geometry-alignment probe (run FIRST: cheapest, genuinely damaging if it fails).**
*Claim tested*: kernel geometry is "natural" — models trained on text converge toward it (the precondition for canonical vectors being anything but arbitrary).
*Method*: representational similarity analysis between the kernel's pairwise-cosine matrix over prime/molecule exponent words and (i) embedding-layer and (ii) mid-layer representations of existing checkpoints (TinyStories-33M, SmolLM2-135M, Qwen2.5-0.5B). Baselines: permutation null; frequency-matched random word sets. *Success*: Spearman ρ beats the permuted null at p<0.01 across ≥2 model families. *Failure*: no alignment → canonical-coordinate claim (arch (a)) loses its empirical hook; programme falls back to adapter route (b). *Compute*: <1 GPU-h or a laptop CPU afternoon; ~$1.

**E1 — Frozen kernel rows vs random-frozen vs trainable, from scratch (the core experiment).**
*Claim tested*: the **content** of fixed structure-derived vectors provides inductive bias — not merely their fixedness (which 2507.04886 already grants).
*Method*: TinyStories corpus augmented by the phrase→concept mapper (concept tokens interleaved/substituted for prime exponents and ~200 molecule words); GPT-2-style model, 5–15M non-embedding params, small vocab; three embedding conditions: kernel-frozen / random-frozen (norm-matched) / fully trainable. Track: val loss vs tokens (sample efficiency), concept-token perplexity, linear probes for explication relations, cloze accuracy on held-out explication-entailment templates.
*Success (pre-registered)*: kernel-frozen beats random-frozen on concept probes and concept cloze with non-overlapping 95% CIs over 3 seeds, at ≤50% of full training tokens. *Failure*: kernel ≈ random-frozen everywhere — the Unicode paper's prediction — which would directly damage the "canonical vectors matter" claim. This can fail cheaply and honestly. *Compute*: 9 runs × 1–3 T4-h ≈ 15–30 GPU-h; **$5–25 spot**.

**E4 — Emission / unseen-concept decode test (output side; the most discriminating design).**
*Claim tested*: fixed OUTPUT concept vectors are usable — and their geometry is what carries meaning.
*Method*: on the E1 model (tied, frozen kernel rows), train a gloss→concept-token task. Hold out ~20% of concepts entirely from emission targets. Measure top-1 on seen concepts and top-10 on **unseen** concepts (possible only via vector geometry: the model must place `h` near a never-trained read-out direction). Control: random-frozen kernel must sit at chance on unseen concepts. Compare softmax-over-extended-vocab vs NN-decode regression head.
*Success*: ≥90% top-1 seen; unseen top-10 above chance with random-frozen control at chance. *Failure*: unseen at chance → kernel rows are functioning as arbitrary ids. *Compute*: 2–5 GPU-h; **<$5**.

**E3 — Concept-density I/O test.**
*Claim tested*: dense concept-level I/O carries more usable information per symbol than text.
*Method*: tasks expressible in explications (entailment/paraphrase over NSM-explicable TinyStories-domain sentences, synthesised via the 2505.11764-style pipeline); finetune SmolLM2-135M (embeddings frozen, LoRA on attention; new concept rows initialised to kernel vectors and excluded from training via PEFT `trainable_token_indices` complement) under three input codings: text-only / text+concept-tokens / concept-tokens-only. Measure accuracy per input token and per training example. *Success*: concept-only ≥ text-only at ≤50% of the tokens. *Failure*: concept coding strictly worse at matched training → dense-I/O claim damaged. *Compute*: 6–12 GPU-h; **$5–15**.

**E5 — Adapter + shuffled-kernel control (tests route (b), the fallback claim).**
*Method*: frozen SmolLM2-135M; single linear adapter `R^k→R^d` shared across concepts, trained on a small concept-usage corpus; CoLLEGe-style test — inject a *nonce* concept defined only by its kernel-space composition of primes, measure usage/definition-match accuracy vs an adapter trained on a permuted kernel. *Success*: true kernel beats permuted kernel significantly on nonce-concept generalisation. *Compute*: 3–6 GPU-h.

**E6 (phase 2) — Explication-graph input (route (d))**: GraphToken-style encoder over explication trees with fixed kernel node features vs learned node features vs flattened text, on a compositional-generalisation split (SCAN/COGS-style templates in the TinyStories domain). Defer until E1/E4 read out. *Compute*: 10–20 GPU-h.

**Kill-chain logic** [speculative but recommended]: E2 fail + E1 null + E4 unseen-at-chance = the strong hypothesis (canonical training-free coordinates as native LM vocabulary) is dead at a total cost of ~$30, and the programme pivots to (b)/(d) as "kernel as structured supervision through trained adapters" — still publishable, honestly weaker. E4 unseen-concept success is the single cheapest result that would make the strong claim credible.

### 2.4 Recommended hardware plan

1. **This box**: kernel lexicon + explication data pipeline, phrase→concept mapper, experiment configs, result aggregation. Nothing heavier; `nice` everything; mind the 3 GB disk.
2. **Rented**: one **T4 spot** (g4dn.xlarge spot or a marketplace T4 at ~$0.06–0.25/hr) for E2/E4/E3/E5; T4 or A10G (~$1/hr on-demand ceiling) for the E1 grid. Whole programme ≈ **$10–80**. No multi-GPU, no A100s needed at PoC scale.

---

## Key sources

arXiv: 2305.07759 (TinyStories) · 2502.02737 (SmolLM2) · 2507.04886 (frozen Unicode embeddings) · 2403.15362 (CoLLEGe) · 2505.11764 (NSM explications via LLMs) · 2412.08821 (LCM) · 2508.05305 (SONAR-LLM) · 2412.07992 (CB-LLMs) · 2502.13632 (Concept Layers) · 2402.05862 (GraphToken) · 2310.13023 (GraphGPT) · 2106.13884 (Frozen) · 1911.00172 (kNN-LM) · 2112.04426 (RETRO) · 2203.08913 (Memorizing Transformers) · 1608.05859 / 1611.01462 (weight tying) · 2104.08691 (prompt tuning) · 2311.03658 (linear representation hypothesis) · 2209.15430 (relative representations) · 2405.07987 (Platonic representations) · 1705.08039 (Poincaré embeddings) · 2109.03127 (rare-token degeneration).
Web: HF PEFT TrainableTokens docs; huggingface/peft#1462, #2603, #2653; huggingface/transformers#5570; TinyStories-33M HF model-card discussion; getdeploying.com & thundercompute.com GPU pricing (July 2026).
