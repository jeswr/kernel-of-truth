# poc/e5 — E5: adapter + shuffled-kernel control (A2's decisive test)

**E5 — adapter + shuffled-kernel control** (docs/poc-design.md Phase E, E5
rev 2, MINOR 23; bead `kernel-of-truth-c24`). Everything in "Pre-registered
operationalisation" below was PINNED IN THIS FILE BEFORE the GPU run
(the E1/E4 lesson: guards and pins first). The spec text this experiment
answers to, verbatim:

> **E5 — adapter + shuffled-kernel control** (3–6 GPU-h). Rev 2 (MINOR 23):
> n ≥ 20 nonce concepts; exact permutation test, α=0.05; scoring by a fixed
> non-LLM rubric (slot-filling accuracy against the nonce's explication) or a
> leak-checked judge (judge prompt contains no explications). Success: true
> kernel > shuffled kernel on nonce-concept usage.

Position in the kill chain (docs/poc-design.md "Mixed" branch): E2 held (the
pre-registered primary met in 3/3 model families, robust to the post-hoc
sentence-embedding re-analysis — A2's premise, geometry-up-to-transform,
stands); E1 read out INCONCLUSIVE and E4 tier-2 NULL (A1 unsupported). E5
bears on **A2**: can a *learned* transform (the one thing A1 forbade and A2
licenses) carry training-free kernel content into a frozen model such that
the model can use concepts it has never seen — and does that ability depend
on the kernel's concept↔vector *assignment* being true rather than shuffled?

## The experiment in one paragraph

A frozen **SmolLM2-135M** (d_model = 576) never sees any concept's surface
form. Every concept is presented only as a single soft token: its kernel
vector (kot-enc-B/1 @ D=8192, JL-projected to 576 — the pre-registered
projected path) pushed through a **single shared linear adapter**
kernel-space→model-space, spliced into the input embedding sequence
(CoLLEGe-style nonce token; Teehan et al. 2024 meta-learn such embeddings
from example sentences — here the embedding comes from a *training-free
compositional code* instead, and only the linear map is learned). The adapter
(nothing else) is trained on a small concept-usage corpus of definitional
statements for **500 SEEN concepts**. At test, **24 NONCE concepts** — never
in any training item, glosses never seen — are injected the same way, and the
frozen model must pick each nonce's correct definition out of 5 candidates by
likelihood. Two adapters per seed, identically initialised and trained:
**true-kernel** vs **shuffled-kernel** (same vector spectrum, seeded
derangement of the concept↔vector assignment, Common rule 4). If the kernel's
geometry carries content usable up to a learned linear transform (A2), true
must beat shuffled on nonce items; if the geometry is decorative, the
derangement costs nothing.

## Pre-registered operationalisation (pinned 2026-07-07, before any GPU run)

Items the E5 spec leaves open are pinned here and FLAGGED as
operationalisations, per the Common-rules discipline.

### O1 — kernel space and vectors (Common rules 2–3)

- Encoder: **kot-enc-B/1, D=8192**, content-hash
  `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c` (THE
  pinned full-D encoder; fail closed on mismatch). Projected path (rule 3,
  path ii): the **X4 fixed JL matrix 8192→576** (Achlioptas signs, ±1/√576,
  SHA-256 stream `jl/8192/576`; `jlProject` copied VERBATIM from
  poc/harness/x4.ts). Published distortion inherited by this run:
  RDM Spearman **0.9608** (X4 synthetics) / **0.9706** (kernel v0),
  min-adversarial-to-floor ratio 70.3× at d=576 (poc/results/x4-report.json,
  x4-kernel-v0-report.json).
- **OPERATIONALISATION (flagged):** projected rows are L2-normalised to unit
  norm after projection (pre-normalisation norms recorded in the manifest).
  Adapter input geometry is therefore pure direction, matching the cosine
  convention every upstream phase (X1–X4, E2) measured.

### O2 — concept set (reuses the E4 synthetic vocabulary; leakage discipline inherited)

- Universe = E4's committed vocabulary: 54 authored kernel-v0 concepts +
  1,000 synthetic capped explications (poc/e4/inputs/synthetic-concepts.json,
  reused byte-identically; generator seeds `e4/synth/<i>`).
- **SEEN = 500**: all 54 authored + 446 synthetics drawn without replacement
  by DetStream label `e5/select/seen` from the synthetics not chosen as
  nonces.
- **NONCE = 24** (spec floor n ≥ 20): drawn by DetStream label
  `e5/select/nonce` from the synthetics with **depth ≥ 2 AND topClauses ≥ 2**
  (structural pre-filter, pinned here: single-clause depth-1 synthetics
  realize to near-vacuous glosses — "I happen." — which E4 flagged as
  near-ambiguous; the filter is on pre-hoc AST structure only, never on any
  model output). **No post-hoc nonce exclusion of any kind: all 24 enter the
  primary.**
- Descriptive compositional split: a nonce "shares structure" with the seen
  set iff every feature (frame + depth-1 clause skeletons, definition copied
  verbatim from poc/e4/harness/holdout.ts) is attested in the union of the
  500 seen concepts' feature sets. Reported descriptively, no inferential
  claim.

### O3 — task construction ("concept-usage corpus" + "slot-filling")

- Glosses: **reused from E4's committed, hash-published gloss set**
  (poc/e4/inputs/glosses.jsonl, sha-256
  `36181f9b65090887d8af45c845abe122d12d6352b61a16bcaa68f9c3c5794e12` =
  poc/e4/GLOSS-HASH.txt, published 2026-07-07T06:43Z, before any training
  anywhere consumed it; fail closed on mismatch). All E4 gloss discipline is
  inherited: authored from the explication AST (never from renderings),
  ≤7-word n-gram overlap with kernel-v0 gloss fields, target-lexicon
  disjointness, per-concept distinctness — and its honesty caveats (realizer
  English, same-agent-lineage authorship) carry over verbatim.
- Frame (one fixed template, identical in training and eval, identical
  across arms): tokens("The word") ⧺ [SLOT] ⧺ tokens(" means:") ⧺
  tokens(" " + gloss), BOS-prefixed. [SLOT] is ONE input-embedding position
  carrying the adapter output — the concept's surface form never appears
  anywhere (no vocab surgery; the nonce token is never emitted, so the Bq
  no-decode rule is not in play and the full-D path is used throughout).
- Training corpus (SEEN concepts only): gloss style variants **0–3** ×
  500 concepts = 2,000 items; a seeded 10% (DetStream `e5/valsplit`; 200
  items) is held out as the LR-selection/val set. Loss = cross-entropy on
  the gloss tokens only.
- Style variant **4 is reserved for evaluation** and appears in NO training
  item for ANY concept.
- **Nonce zero-exposure guard (mechanical, fail closed):** no nonce id, no
  nonce vector row, and no nonce gloss text (any style) occurs in any
  training or val item — equality AND nonce-gloss-as-substring-of-a-training-
  gloss are both forbidden; asserted by the prep tests over the built
  artifacts and re-asserted by the runner at load. **Pinned refinement
  (2026-07-07, at build time, before any run):** the REVERSE containment — a
  short seen-concept gloss occurring as a clause inside a longer nonce gloss
  (13 cases; realizer compositionality, e.g. seen syn-0142 "Something is
  able to do me." is the first clause of nonce syn-0346's gloss) — is
  compositional sharing identical across arms, is exactly what the
  compositional split measures, and is COUNTED in e5-items.json
  (`trainGlossInsideNonceGlossContainments`) rather than forbidden.
- Eval items (fixed at build time, seeded, identical across arms and seeds):
  - **Nonce items (primary): 24 nonces × 5 styles = 120 items.** Each item:
    the frame with the nonce's adapter embedding; candidates = the nonce's
    own style-s gloss + the style-s glosses of 4 other nonces (seeded
    balanced assignment, DetStream `e5/noncecand/<slug>/<style>`). 5-way,
    chance = 0.2.
  - **Seen validity items (instrument gate): 500 seen concepts × style 4,**
    candidates = own style-4 gloss + 4 other seen concepts' style-4 glosses
    (DetStream `e5/seencand/<slug>`). 5-way, chance = 0.2.
- **Scoring rubric (fixed, non-LLM, mechanical — the spec's first option):**
  candidate score = mean per-token log-probability of the candidate gloss
  tokens under the frozen model given the frame + injected embedding;
  prediction = argmax over the 5 candidates (exact float ties, if any, score
  as incorrect). "Slot-filling accuracy against the nonce's explication" is
  hereby operationalised as: the definition slot of the fixed frame must be
  filled with the realizer gloss OF THE NONCE'S OWN EXPLICATION rather than
  a competing explication's gloss. No LLM judge exists anywhere in E5.

### O4 — model, adapter, arms, training (Common rules 1, 4, 5)

- Model: **HuggingFaceTB/SmolLM2-135M**, frozen (no gradient anywhere in the
  model; eval mode; fp32; d_model asserted = 576 = the JL target d).
- Adapter: **one shared affine map** y = Wk + b, W ∈ R^{576×576},
  b ∈ R^576 (≈333k trainable params — the ONLY trainable params).
  **OPERATIONALISATION (flagged):** init W ~ N(0, σ²) with σ = the std of
  the frozen embedding-matrix entries (measured at run time, recorded), b =
  the mean embedding row — so an untrained adapter emits a generic-token-like
  embedding; init is seeded per experiment seed and IDENTICAL across arms
  (paired, Common rule 1).
- Arms (each 5 paired seeds, seeds 0–4):
  1. **true-kernel** — row i ↦ kernel vector of concept i.
  2. **shuffled-kernel** — row i ↦ kernel[perm_s[i]], perm_s = seeded
     derangement of ALL 524 rows (labels `e5/shuffle/<s>`, no fixed points;
     E4's construction). Same spectrum, assignment destroyed. Stated
     consequence: a nonce's shuffled vector is typically a TRAINED seen
     concept's vector, so shuffled is a *wrong-content* control, not an
     untrained-region control (the random arm covers that floor).
  3. **random-vector** — row i ↦ unit-norm i.i.d. Gaussian (labels
     `e5/random/<s>`), norm-matched to the kernel rows exactly.
     **DESCRIPTIVE ONLY** (per the E5 brief; no inferential claim).
- Training (identical across arms by construction; arms differ ONLY in the
  frozen vector table): AdamW (β=0.9/0.999, wd=0), batch 32, **2,000 steps**
  (~35 epochs of the 1,800 train items), linear warmup 100 steps then cosine
  to 0.1×, grad clip 1.0, fp32 (TF32 matmul allowed, recorded). Data order =
  seeded shuffle per epoch, a function of the seed index only (identical
  across arms; Common rule 1 pairing).
- LR rule (Common rule 5): per-arm sweep on seed 0 only, {3e-4, 1e-3, 3e-3}
  at half budget (1,000 steps), best by val cross-entropy, then fixed for
  all 5 seeds of that arm. `lr-selection` recorded in results.

### O5 — statistics (pre-registered)

- **Primary endpoint (one per experiment, Common rule 1):** nonce
  slot-filling accuracy, true-kernel vs shuffled-kernel.
  Per nonce j: d_j = mean over the 5 paired seeds of
  (acc_true[s,j] − acc_shuffled[s,j]), acc over that nonce's 5 items.
  **Test: one-sided exact sign-flip permutation over the 24 nonce-level
  paired differences** (statistic = Σ_j d_j; full 2^24 enumeration, exact by
  integer-lattice convolution; p includes the observed assignment),
  **α = 0.05**. This operationalises the spec's "n ≥ 20 nonce concepts;
  exact permutation test, α=0.05" with the nonce as the permutation unit.
  *Stated caveat (pinned):* nonce-level differences share the 5 trained
  adapter pairs, so they are not fully independent; the seed-level test
  below is the confirmatory secondary that treats the training run as the
  unit.
- **Instrument-validity gate (pre-registered — the E1 step-0 lesson):** the
  TRUE arm must beat chance on the SEEN validity items in ≥4 of 5 seeds
  (per-seed one-sided exact binomial vs 0.2 over 500 items, p < 0.05).
  Otherwise the adapter never learned the mapping at all and the run is
  reported as **INSTRUMENT-INVALID** (neither success nor null — an
  instrument failure), with no primary claim in either direction.
- **Secondary (Holm-corrected, m=1):** one-sided exact paired sign-flip over
  the 5 paired seed-mean nonce accuracies, true vs shuffled (min attainable
  p = 1/32).
- **Descriptive (no inferential claims):** random-arm accuracies;
  step-0 (untrained-adapter) accuracies for all arms; shuffled/random
  seen-item accuracies; per-item score margins; compositional shared/novel
  nonce split; per-seed and per-nonce tables.
- **Success (spec, verbatim): "true kernel > shuffled kernel on
  nonce-concept usage"** = the primary test rejects at α=0.05 with positive
  mean difference AND the validity gate passed. A non-rejection with the
  gate passed is reported as a NULL for E5's primary (the E5 spec
  pre-registers no TOST equivalence bound, so the null is "not
  demonstrated", scale-qualified as always). Gate failed ⇒ INSTRUMENT-INVALID.
- No shuffled-arm "hot control" invalidation is pre-registered: unlike E4's
  emission chance floor, an above-chance shuffled arm is legitimate here
  (frame/style regularities are shared by both arms); the contrast itself is
  the control.

### O6 — what a positive cannot license (Common rule 6)

Single model, single basis, toy scale, realizer-English glosses, synthetic
clean domain. A positive licenses exactly: *at toy scale, a frozen 135M
model given training-free kernel vectors through one learned linear map uses
never-seen concepts better when the kernel's concept↔vector assignment is
true than when it is shuffled* — an A2 statement. It does not establish
uniqueness of the kernel code (any encoder whose geometry mirrors
explication similarity could in principle pass), nor anything at scale, nor
anything about A1 (the adapter IS a learned projection, forbidden in
A1-labelled experiments by rule 3).

## Layout

| path | what |
|---|---|
| `harness/common.ts` | E5 constants, DetStream helpers, verbatim `jlProject`, kernel-v0/E4-artifact loaders, gloss-hash gate |
| `harness/selectConcepts.ts` | seeded seen/nonce selection + compositional features → `inputs/e5-concepts.json` |
| `harness/vectors.ts` | full-D encode (pin-gated) → JL@576 → `inputs/vectors/*.f32` + derangements + manifest |
| `harness/items.ts` | training/val/seen-val/nonce items + THE pre-registration manifest → `inputs/e5-items.json`, `inputs/e5-manifest.json` |
| `test/e5prep.test.ts` | fail-closed gates: pins, hashes, derangements, zero-exposure, determinism, item counts |
| `runner/e5_runner.py` | the ONLY thing the GPU runs: 3 arms × 5 paired seeds, LR rule, eval, pre-registered stats, verdict |
| `runner/check_smoke.py` | independent assertions over a mock run's outputs |
| `smoke/run_smoke.sh` | CPU end-to-end mock (tiny random-init model, disposable venv) |
| `results/` | committed smoke evidence; GPU results arrive via `results-incoming/` (Modal transport, poc/modal/modal_e5.py) |

```bash
cd poc/e5 && npm install && npm test     # verify committed artifacts (fail-closed gates)
npm run inputs                            # regenerate inputs (DELIBERATE only)
bash smoke/run_smoke.sh                   # CPU end-to-end mock + independent checks
# GPU (Modal transport; ONE full run, budget ~$3, cap = 4 h A10G ≈ $4.4):
cd ../..
poc/modal/.venv/bin/modal run poc/modal/modal_e5.py --mock   # transport smoke, ~pennies
poc/modal/.venv/bin/modal run poc/modal/modal_e5.py          # full pre-registered E5 (A10G)
```

## Cost/budget guard

Estimate: 39,000 training steps total (9 sweep runs × 1,000 + 15 full runs ×
2,000) of a 333k-param adapter through frozen SmolLM2-135M fp32, batch 32 +
~65k eval scorings ≈ **2–2.5 A10G-h ≈ $2.5–3** on Modal (per-second billing;
SmolLM2 weights already in the `kot-hf-cache` Volume from E2). Hard timeout
4 h (≈$4.4 worst case) — inside the ≤$8 authorization. T4 flavour exists but
is ~3× slower at fp32 and risks the timeout; A10G is the default.
