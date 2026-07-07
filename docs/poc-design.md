# PoC experiment programme (rev 1, pre-registered)

**Status:** draft, 2026-07-07 — companion to `architecture.md` §5. Experiments are **pre-registered**: success/failure criteria are fixed here, before any run; results will be reported against these criteria verbatim, including nulls. Derived from `../reports/architecture-and-poc-options.md` §2.3 (which carries the citations) with encoder-level phase X added.
**Author:** Kern (Claude Fable 5). Tracker: beads (`bd list` in repo root).

## Common rules

- ≥3 seeds per trained condition; conditions matched for tokens, steps, LR schedule, and embedding-norm distribution.
- Kernel vectors are derived **training-free** from explication structure (encoder v0; no text-encoder shortcuts — they would smuggle trained semantics into the "training-free" claim).
- The two load-bearing controls, everywhere applicable: **random-frozen** (same norms, no structure — the arXiv:2507.04886 null) and **shuffled-kernel** (same geometry, permuted concept↔vector assignment).
- Negative results are first-class deliverables; the kill-chain logic is stated in advance (§ Kill chain).

## Phase X — encoder property tests (this box, CPU, no GPU; run first)

**X0 — encoder verification.** Byte-determinism across platforms/runs; golden vectors for a fixed corpus (mirroring `@jeswr/concept-hash`'s golden-vector discipline).
**X1 — injectivity margins [pre-registered].** Over kernel v0 (~115 concepts) plus ≥10⁴ synthetic capped explications: pairwise cosine distribution; **success** = minimum pairwise angular separation of non-identical explications > 5× the fp16 noise floor at D=8192; **failure** = any collision or margin < 2×.
**X2 — decode depth.** Recursive unbind + cleanup over kernel v0: report exact-recovery rate by tree depth and clause count; **success** = 100% at depth ≤ 4 on kernel v0, degradation curve documented beyond.
**X3 — similarity pathology (documentation, not pass/fail).** Measure the NOT-flip / polarity problem quantitatively (cosine shift under single-operator meaning inversions vs under meaning-preserving paraphrase edits); publish the numbers — consumers of kernel similarity must see them. Test polarity-weighted variants; report whether any dominates.

## Phase E — model experiments (rented T4/A10G; ~$10–80 total)

**E2 — geometry-alignment probe** (first: cheapest genuine falsifier; <1 GPU-h, ~$1).
RSA (Spearman) between kernel pairwise-cosine matrix over prime/molecule exponent words and embedding-/mid-layer representations of TinyStories-33M, SmolLM2-135M, Qwen2.5-0.5B. Baselines: permutation null, frequency-matched random word sets.
**Success:** ρ beats permuted null at p<0.01 in ≥2 model families. **Failure:** no alignment → the canonical-coordinates claim (arch A1) loses its empirical hook; A2 becomes primary.

**E1 — frozen kernel rows vs random-frozen vs trainable** (the core experiment; 9 runs, 15–30 T4-h, $5–25).
TinyStories corpus + phrase→concept mapper augmentation; GPT-2-style 5–15M non-embedding params; three embedding conditions (kernel-frozen / random-frozen norm-matched / trainable), AdamW weight-decay masked off frozen rows (the silent-unfreezing gotcha).
Metrics: val loss vs tokens; concept-token perplexity; linear probes for explication relations; cloze on held-out explication-entailment templates.
**Success:** kernel-frozen beats random-frozen on concept probes + concept cloze, non-overlapping 95% CIs over 3 seeds, at ≤50% of training tokens. **Failure:** kernel ≈ random-frozen everywhere (the 2507.04886 prediction) → the content-matters claim is damaged at its strongest test.

**E4 — unseen-concept emission** (most discriminating; 2–5 GPU-h, <$5).
On the E1 kernel-frozen model (tied rows): gloss→concept-token task, ~20% of concepts held out of emission training. Only vector geometry can place `h` near a never-trained read-out direction.
**Success:** ≥90% top-1 on seen; unseen top-10 above chance with random-frozen control at chance. **Failure:** unseen at chance → rows function as arbitrary ids. *A positive here is the single cheapest result making the strong claim credible.*

**E3 — concept-density I/O** (6–12 GPU-h, $5–15).
NSM-explicable entailment/paraphrase tasks (2505.11764-style synthesis pipeline); SmolLM2-135M, frozen embeddings + LoRA attention, kernel-initialised concept rows excluded from training (PEFT `trainable_token_indices`); codings: text-only / text+concept-tokens / concept-only. Metric: accuracy per input token and per training example.
**Success:** concept-only ≥ text-only at ≤50% tokens. **Failure:** concept coding strictly worse at matched training.

**E5 — adapter + shuffled-kernel control** (tests arch A2; 3–6 GPU-h).
Frozen SmolLM2-135M; single shared linear adapter kernel→model space; CoLLEGe-style nonce-concept test (concept defined only by its kernel-space composition).
**Success:** true kernel beats shuffled kernel significantly on nonce-concept usage/definition-match. This is the fallback claim's decisive test.

**E6 — graph-input (arch A4) — phase 2, deferred** until E1/E4 read out (10–20 GPU-h).

## Kill chain (pre-registered decision rule)

- E2 fail **and** E1 null **and** E4 unseen-at-chance ⇒ **strong hypothesis dead** (~$30 spent): canonical training-free coordinates as native LM vocabulary is not supported. Programme pivots to A2/A5 ("canonical kernel outside the model; adapters as interface; verifiable grounding") — honestly weaker, still novel, still composes with the estate.
- E4 positive (unseen decode above chance, control at chance) ⇒ strong claim credible; scale E1 grid and begin frontier-lab prospectus on the strong form.
- Mixed (e.g. E2 positive, E1 null) ⇒ geometry is natural but content-as-inductive-bias unproven at tiny scale; report as such; A2 primary, A1 parked with the scaling caveat stated.

## Hardware

- **This box** (2 cores/8GB shared with a live server, ~3GB disk, Python 3.9, no torch/compilers): phase X (encoder is TypeScript on node 22), kernel v0 data, mapper, configs, aggregation. Everything `nice`d.
- **Rented** (needs AWS permissions or user-provisioned instance): one T4 spot (g4dn.xlarge, ~$0.16–0.26/hr spot) covers E2/E4/E5/E3; T4 or A10G (g5.xlarge, ~$0.4–0.6/hr spot) for the E1 grid. Whole programme **≈ $10–80**.
