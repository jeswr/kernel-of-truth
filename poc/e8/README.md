# poc/e8 — kernel↔SAE alignment (E8; bead kernel-of-truth-u0x)

**Status:** harness built + locally validated 2026-07-07; the Modal run is
COORDINATOR-GATED (spend). Everything below §Design-pin was fixed BEFORE the
harness was built and before any SAE weight was downloaded; amendments would
be listed here, dated.

**Pre-registered criterion (docs/poc-design.md E8, verbatim):**
> Align kernel geometry to SAE feature dictionaries across ≥2 open model
> families (projected path, X4 distortion reported); criterion: kernel
> coordinates predict cross-model feature correspondence beyond
> shuffled-kernel and permutation nulls.

Framing: docs/architecture.md A6 (kernel as canonical label/coordinate space
for learned features), notes/panel-frontier-skeptic.md O6, and
notes/panel-kernel-design-review.md §3.4 (E8 is the cheap-integration,
no-mapper, post-hoc-analysis mode — "the one result that moves the room").

## Design pin (fixed 2026-07-07, before building)

### 1. SAE sources (surveyed 2026-07-07 via the HF API; access + size are the criteria)

| | family A | family B |
|---|---|---|
| base model | `openai-community/gpt2` (124M, 12 layers, ungated) | `EleutherAI/pythia-160m` (12 layers, ungated) |
| model revision | `607a30d783dfa663caf39e06633721c8d4cfcd7e` | `50f5173d932e8e61f858120bcb800b97af589f46` |
| SAE repo | `jbloom/GPT2-Small-SAEs-Reformatted` (the OpenAI-style residual L1 SAEs used across the sae_lens / Neuronpedia literature) | `EleutherAI/sae-pythia-160m-32k` (EleutherAI `sparsify`/`sae` TopK SAEs) |
| SAE revision | `57d08a4fd333fbf18caf3fbea63ceeb88e2f50d9` | `2046768ae0c8cb69a2e8ed64f2eafb9f8c5fa294` |
| file (one layer, one width) | `blocks.6.hook_resid_pre/sae_weights.safetensors` — 151.1 MB | `layers.5/sae.safetensors` — 201.5 MB |
| dictionary | d_in 768, d_sae 24,576, ReLU, L1 8e-5, 300M OpenWebText tokens | d_in 768, num_latents 32,768, TopK k=32, 8.2B Pile tokens |
| hookpoint | resid_pre of block 6 (0-based) | output of `gpt_neox.layers[5]` |

Both hookpoints are the SAME residual-stream site: the stream between blocks
5 and 6 (0-based) = HF `hidden_states[6]` = layer L/2 of 12 — E2's mid-layer
discipline carried over exactly.

Survey notes (what was rejected and why):
- **Gemma Scope** (`google/gemma-scope-2b-pt-res`, ungated) is the flagship
  suite, but the BASE model `google/gemma-2-2b` is gated (`gated: manual`) —
  a one-command coordinator run must not be hostage to an HF licence click.
  Filed as the natural third-family extension (follow-up bead).
- **Llama Scope**: gated base + 8B-class model — fails both access and size.
- **OpenAI's own GPT-2 SAEs**: published via Azure blobs, not cleanly
  addressable by pinned HF revision; jbloom's reformatted release of the same
  lineage is the community-standard pinnable artifact.
- `EleutherAI/sae-pythia-160m-32k`'s README mentions MLP SAEs only, but the
  repo carries both `layers.N.mlp` and `layers.N` hookpoints; per the
  EleutherAI `sae` library convention the hookpoint name is the module path,
  so `layers.5` is the residual stream leaving block 5. We use `layers.5`
  and record the README discrepancy here honestly.

Loading choice (task option "sae_lens if clean, else direct"): **direct
safetensors slicing.** sae_lens would drag transformer_lens + its transformers
version coupling into the pinned image; both dictionaries are two matrices and
two biases (headers verified by ranged request before pinning):
- jbloom: `W_enc [768,24576]`, `b_enc`, `W_dec [24576,768]`, `b_dec`;
  encode(x) = ReLU((x − b_dec) @ W_enc + b_enc)  (mats_sae_training-era
  standard arch; `b_dec_init_method: geometric_median` in its cfg.json).
- EleutherAI: `encoder.weight [32768,768]`, `encoder.bias`, `W_dec
  [32768,768]`, `b_dec`; encode(x) = TopK_32(ReLU((x − b_dec) @
  encoder.weightᵀ + encoder.bias)), non-top-k activations zeroed.

**Activation-basis corrections (the silent-failure hazard, pinned + gated):**
- The jbloom SAEs were trained on transformer_lens activations with default
  processing (`center_writing_weights=True`): every residual writer is
  mean-centered over d_model, and since centering is linear the TL residual
  equals the HF residual minus its own per-position mean over the hidden dim.
  Pinned: GPT-2 activations = `hidden_states[6] − mean(hidden_states[6],
  axis=-1)`. (LN folding does not touch resid_pre; centre_unembed is
  irrelevant to the residual.)
- EleutherAI `sae` trains on plain HF module outputs: Pythia activations =
  `hidden_states[6]`, no correction.
- BOS: GPT-2 SAE training windows begin with BOS (sae_lens-era
  `prepend_bos`), so E8 prepends `<|endoftext|>` for GPT-2 (a documented
  DEVIATION from E2's no-special-tokens extraction; word-span offsets are
  shifted accordingly). Pythia/`sparsify` streams raw concatenated documents:
  no BOS.
- **Fail-closed basis gate:** the container computes each SAE's fraction of
  variance unexplained (FVU) and mean L0 on our activations under the pinned
  convention. FVU > 0.5 (family A) / > 0.75 (family B, TopK k=32 is lossier
  by construction) ⇒ `ERR_SAE_BASIS`, run dies. A wrong basis must be a
  crash, not a quietly null result. FVU under the unpinned alternative
  convention is emitted as a diagnostic only.

### 2. Item set

The **51 E2 analysis items** (kernel-v0 explicated concepts minus the three
multi-word labels; `poc/e2/inputs/items.json`, sha-pinned in
`inputs/e8-manifest.json`), each with its E2 exponent word and 24-template
context bank (`poc/e2/inputs/contexts.json`, reused byte-identically).
Per-family in-vocab rule = E2's (` `+word → 1–4 tokens, no UNK); the analysed
set is the **intersection** of both families' survivors, both drop lists
published. Items whose SAE signature is all-zero in either family are dropped
and published; >10% zero-signatures ⇒ `ERR_DEAD_SIGNATURES`.

**Correction to the task premise, on the record:** the tasking said "54+108
explicated/molecule concepts". The repo holds 54 explicated kernel-v0
concepts and **54** molecules-v0 records (not 108) — and molecules have **no
kernel vectors at all**: they are grounding notes without explications, and
docs/design-molecule-tier.md pins molecule-vector derivation as an encoder
version change (new content-hash ⇒ new pre-registration). E8 therefore runs
on the 51 explicated analysis items only; the molecule-tier extension is
filed as a follow-up bead, blocked on the encoder change.

### 3. Operationalisation: concept → SAE-feature signature (pinned)

For concept c with exponent word w in family F: SAE-encode **per token**
(the unit SAEs are defined on — encode(mean(h)) ≠ mean(encode(h))), mean over
the tokens overlapping the word span (E2's span rule verbatim), then mean
over the 24 bank contexts:

  a_c^F = mean_{ctx ∈ bank(c)} mean_{t ∈ span(w)} SAE_F(h_t)  ∈ R^{d_sae(F)},  fp32.

The alternative in the tasking — direct feature-max (represent c by its
single top feature) — is **rejected**: it throws away the activation profile,
is brittle under feature splitting, and under TopK k=32 the max is close to
degenerate. Mean-profile is the pin.

### 4. Correspondence + statistics (E2 machinery imported, not reimplemented)

- Within-family concept RDMs: S^F = cosine over signatures (51×51 before
  attrition), via `e2_runner.cosine_sim_matrix`.
- **Cross-family concept correspondence** (no learned map — second-order
  profile matching; a learned aligner would violate the programme's
  training-free discipline): X(c,c′) = Spearman(S^A[c,M], S^B[c′,M]) with
  M = all anchors except {c,c′} (self-cells excluded from both profiles so
  the diagonal 1s cannot leak). X_sym = (X+Xᵀ)/2.
- All rank/partial/permutation primitives are imported from
  `poc/e2/runner/e2_runner.py` and `poc/e2/reanalysis/analyze.py`
  (`rankdata`, `pearson`, `offdiag`, `mantel`, `MaskedSpearman`,
  `MaskedPartial`). Seed 20260707, 10⁴ permutations, mid-rank ties — the E2
  discipline unchanged.
- **Nulls note (applies to every test):** at the RDM level, the programme's
  shuffled-kernel control (permuted concept↔vector assignment) and the Mantel
  concept-label permutation COINCIDE: a shuffled kernel's RDM is exactly
  P·K·Pᵀ. One permutation scheme therefore implements both named nulls; the
  tested (kernel) matrix permutes, target + covariates stay fixed (the E2
  re-analysis convention, generalised).

**Precondition gate G (kernel-free, reported first):** identification through
X — accuracy of argmax_{c′} X(c,c′) = c, both directions averaged, against
the label-permutation null (10⁴ perms). If G fails (p ≥ 0.05) there is no
detectable cross-family correspondence for the kernel to predict: the primary
is still reported, but the pre-declared reading is "E8 uninformative about
the kernel — the two dictionaries do not correspond on this item set at this
layer", NOT a kernel failure. (G is biased toward failure by the honest
confounds in §6 — that is conservative for the kernel claim.)

**Primary P1 (the spec-verbatim criterion):** Spearman(offdiag K_jl512,
offdiag X_sym), one-sided Mantel permutation of K's concept labels
(≡ shuffled-kernel, above), p < 0.01.

**Co-primary P2 (deflation guard, E2's lesson):** the same test as partial
Spearman controlling the three committed E2 baseline RDMs (word2vec cosine,
WordNet path, gloss word-overlap), p < 0.01.

**Decision rule (fixed before any number is seen):**
- **PASS** ("kernel coordinates predict cross-model feature correspondence
  beyond shuffled-kernel and permutation nulls") iff P1 AND P2 both p < 0.01
  and G passed;
- **"generic relatedness detected"** iff P1 passes and P2 fails;
- **PRECONDITION FAIL** iff G fails (kernel claim untested);
- **NULL** otherwise.
One family pair = ONE primary test — no ≥2-of-3 quantifier is available here,
and a PASS licenses exactly one pair (GPT-2↔Pythia-160m), nothing broader.

**Secondaries (Holm-corrected, 5 tests):** S1 = P2 with the four
sentence-embedding RDMs from the committed E2 re-analysis extraction added
(orig3+emb4 — matrices reused from
`poc/e2/results-incoming/20260707-112247-reanalysis/rdms-reanalysis.json`,
no new GPU work); S2/S3 = per-family partial Spearman K vs S^F | orig3
(E2-in-SAE-space); S4/S5 = kernel-as-label retrieval per family: top-1
accuracy matching S^F rows to K rows by masked profile-Spearman (the A6
"label a learned feature space with kernel coordinates" use case in
miniature), permutation null.

**Sensitivity (descriptive, not Holm):** full-D and jl576 kernel variants on
the P2 form; X-direction asymmetry (A→B vs B→A identification).

Permutation budgets: RDM-level tests 10⁴ (the E2 constant); the retrieval
nulls (S4/S5) rebuild the full masked-profile matrix per permutation and are
pinned at **2,000** permutations (min p 1/2001 ≈ 5×10⁻⁴, well below every
Holm threshold used) — ~10 min per family, niced, on this box. The fast
masked-Spearman implementation (exact single-removal mid-rank adjustment) is
unit-tested against the literal brute force, ties included.

**Projected path (Common rule 3 / X4):** primary kernel RDM = jl512 (E2's
declared primary). Inherited X4 distortion, quoted from
`poc/results/x4-kernel-v0-report.json`: R^8192→R^512 RDM Spearman **0.9718**;
R^8192→R^576 **0.9706**. Full-D + jl576 are sensitivity rows.

### 5. What runs where (one command, coordinator-gated)

- **Container (Modal T4, pattern `modal_e2_reanalysis.py`):** pinned image
  (`poc/modal/requirements-image.txt`, UNCHANGED — safetensors +
  huggingface_hub arrive transitively via transformers; likely a cache hit on
  the existing E2 image), `kot-hf-cache` volume, sha-asserted staging,
  provenance sidecars. Downloads (volume, NOT this box): gpt2 ~548 MB +
  pythia-160m ~375 MB + two SAE files 353 MB ≈ **1.28 GB**, revision-pinned.
  Extraction: 2 × 51 words × 24 contexts = 2,448 short sentences + per-token
  SAE encode — minutes. NO statistics in the container; it ships signatures
  (~12 MB npz) + diagnostics + provenance.
- **This box (CPU, niced):** `analyze.py` — all statistics, auditable and
  re-runnable without GPU spend.

### 6. Pre-named weaknesses (empirical honesty; none is fixable by this harness)

1. **The concept→feature mapping is itself a judgement.** The SAE sees the
   exponent WORD in 24 synthetic template contexts — never the explication.
   E8 tests: "kernel geometry over explications predicts cross-model
   SAE-signature correspondence of the concepts' exponent words." Polysemy,
   register, and tokenizer effects all load on the word bridge; the orig3
   (and S1's emb4) partials are the only guard against word-level
   relatedness carrying the result.
2. **Single family pair.** One pair = one test; a PASS here does not
   generalise across pairs, and the fallback-headline framing (A6) needs the
   Gemma-Scope third family before anyone shows this to an interp team.
3. **Confounded dictionary differences.** The two SAEs differ in architecture
   (ReLU-L1 vs TopK-32), training corpus (OpenWebText vs Pile), and width
   (24.6k vs 32.8k). These depress and confound correspondence STRENGTH; they
   cannot be separated from model-family differences with n=2. They bias G
   toward failure, which is the conservative direction for the kernel claim.
4. **Concept-level, not feature-level, correspondence.** A feature-level test
   through the same 51 concept probes is degenerate (target and predictor
   would both be functions of the same activation profiles); a non-circular
   feature-level version needs an independent shared corpus and is filed as
   a follow-up, not smuggled in here.
5. **Sparse-signature ties.** At k=32 / L1-sparse activations, signature
   cosines may bunch near zero; all statistics are mid-rank Spearman (ties
   handled), and signature-density diagnostics are published with the run.

## Extension 1 — third-family replication (bead kernel-of-truth-fnq; pre-registered 2026-07-07 BEFORE any ext-1 code or download)

**Context:** the original pair ran and PASSED (committed stamp
`results-incoming/20260707-131303-modal`: gate p=.0013; P1 rho=.386, P2
rho=.360, both p=1e-4; 5/5 Holm secondaries). This extension adds ONE new
family and pre-registers TWO new pairs against the committed signatures.

**Family C (surveyed via HF API 2026-07-07; both repos ungated):**
`HuggingFaceTB/SmolLM2-135M` @ `93efa2f097d58c2a74874c7e644dbc9b0cee75a2`
(llama architecture, 30 layers, d_model 576 — a genuinely THIRD architecture
family vs GPT-2 and GPT-NeoX, and one of E2's three model families) +
`EleutherAI/sae-SmolLM2-135M-64x` @
`57ea2cb986e2545844cdd4a5bb2eb39523243494`,
file `layers.15.mlp/sae.safetensors` (170.0 MB; TopK k=32, num_latents
36,864, d_in 576, FineWeb-Edu-dedup-10B). Two honesty notes: (i) the repo
name says 64x and 36,864/576 = 64, but its cfg.json says `expansion_factor:
32` — num_latents/d_in/k are the authoritative fields we pin; (ii) this
suite (like every recent ungated EleutherAI suite surveyed: pythia-410m-65k,
DeepSeek-R1-Distill-Qwen-1.5B-65k, SmolLM2) is **MLP-OUTPUT SAEs only** — no
residual hookpoints exist. Family C's dictionary therefore lives on the MLP
output of block 15 (= L/2 of 30, exactly), captured as the named-module
output (`layers.15.mlp`) per the EleutherAI `sae` convention, via a forward
hook. The site mismatch vs families A/B (residual stream) is a NEW named
confound (README §6.3 class): it can only depress correspondence strength —
conservative for the kernel claim. Basis "none", no BOS (sparsify
convention, as family B). Gemma Scope remains excluded (gated base model).
Rejected: pythia-410m (same family as B — replication value is lower than a
third architecture) and DeepSeek-R1-Distill-Qwen-1.5B (10x download for the
same MLP-site evidence).

**Reuse:** families A/B signatures are NOT re-extracted; the committed
`signatures-gpt2.npz` (sha256 `b40fe32e1e80…`) and
`signatures-pythia-160m.npz` (sha256 `3bbd06e57174…`) are consumed
byte-identically (full pins in `inputs/e8-manifest-ext1.json`). The Modal
run downloads family C only (~270 MB model + 170 MB SAE).

**Pre-registered pairs and criterion:** pairs (A=gpt2, C) and
(B=pythia-160m, C); per-pair battery IDENTICAL to the original (gate G;
P1 + P2 at p<0.01; Holm secondaries S1–S5; jl512 primary, full-D/jl576
sensitivity; item set per pair = committed 51 ∩ C survivors ∩ nonzero
signatures). **Replication rule (fixed before any number is seen): the
extension REPLICATES iff BOTH new pairs pass P1 AND P2 with gates passed** —
E8 then reports 3/3 pairs across 3 architecture families. Anything weaker is
reported per-pair, verbatim, no cherry-picking. Statistics run through
`analyze.full_battery` UNCHANGED (`analyze_ext1.py` is a loader around it;
`analyze.py`'s bytes stay as committed with the original verdict).

## Extension 2 — at-scale geometry, 1,054 concepts (pre-registered 2026-07-07 BEFORE any ext-2 code, encode, or download)

**Question:** does the E8 correspondence survive a 20x vocabulary — the
1,054-concept E4 vocabulary (54 kernel-v0 + 1,000 synthetic capped
explications, `poc/e4/inputs/synthetic-concepts.json`, combined per that
file's note) instead of the 51 word-anchored items?

**Kernel side (path discipline):** the E4 vector tables are kot-enc-Bq/1 @
D=512 — the TOY-NATIVE path, which E8's pre-registration does NOT use
(Common rule 3 pins E8 to the projected path). The 1,054 concepts are
therefore RE-ENCODED at D=8192 with the pinned kot-enc-B/1 encoder (content
hash asserted == `40e8c8ba…`, fail closed) and projected through the SAME
fixed Achlioptas JL streams `jl/8192/512` and `jl/8192/576` (jlProject
copied verbatim from the E2 harness, which copied it verbatim from
poc/harness/x4.ts — the construction the X4 numbers were measured on).
X4's distortion was measured on kernel v0 only, so the at-scale distortion
(full-D vs jl512/jl576 RDM Spearman over the 1,054) is RE-MEASURED and
published with the artifact. RDMs ship as raw float32 binaries + a
sha-pinned manifest (`poc/e8/scale/`, ~13 MB committed).

**Estimator changes forced by scale (each pinned here, before running):**
1. **Signature via glosses, not word-contexts.** Synthetic concepts have no
   exponent words. Signature = per-token SAE encode -> mean over all real
   tokens of the gloss (attention==1, nonzero offset width, prepended BOS
   excluded for gpt2) -> mean over the concept's 5 glosses
   (`poc/e4/inputs/glosses.jsonl`, GLOSS-HASH `36181f9b…` asserted). Same
   three families and revision pins as ext-1 (A gpt2 residual, B pythia-160m
   residual, C smollm2-135m MLP-out).
2. **Covariates: orig3 does not exist for synthetics** (no words for
   word2vec/WordNet). Deflation guard = cov2: gloss-TEXT embedding RDMs from
   the two committed E2-reanalysis embedders (all-MiniLM-L6-v2 mean-pool+L2;
   bge-small-en-v1.5 CLS-pool+L2), each gloss embedded separately, the 5
   unit vectors averaged then re-L2-normalised, cosine RDM. P2' = partial |
   cov2. Note this guard is STRONG by construction: signal and covariate
   read the same gloss strings — if SAE signatures only carry gloss surface
   semantics, cov2 removes them.
3. **Permutation budgets.** Mantel tests 2,000 permutations (min p 5x10^-4;
   10^4 is prohibitive at 555k off-diagonal cells x the full battery); gate
   G stays at 10^4 (cheap). **Retrieval (S4/S5) demoted to DESCRIPTIVE** —
   top-1 accuracy vs 1/n chance, NO permutation null (each null draw would
   rebuild a 1054^2 masked-profile matrix).
4. **Secondaries:** Holm over {S2', S3'} (per-family partial | cov2).
   Sensitivity: full-D + jl576 kernels on the P2' form.

**Pairs + decision rules (fixed before any number is seen):** all three
pairs run; per-pair rule as before with P2' in place of P2 ("gloss-surface
semantics not excluded" replaces "generic relatedness detected"). **The
at-scale headline claim holds iff the (gpt2, pythia-160m) pair — the pair
that PASSED at n=51 — passes gate + P1 + P2' at n~1054.** The two C-pairs
are reported alongside, framed by ext-1's outcome, whatever it is.

**Pre-named weaknesses (in addition to §6):** (i) gloss-mediated signatures
test correspondence of gloss RENDERINGS — one step further from the concept
than the word bridge, and the NSM-register gloss style is highly uniform
across concepts, pushing signatures toward a shared register direction
(depresses discriminability; conservative); (ii) the glosses were authored
by this programme for E4 — they are not independent text; (iii) 1,000 of
1,054 concepts are PURE PRIME synthetic structures with no corpus-attested
meaning — at-scale correspondence, if found, is about structural geometry,
not lexical semantics, and is reported in exactly those words.

**Cost:** one T4 container (3 families x 5,270 gloss texts + 2 embedders);
~10-20 min ~= $0.15-0.30. CPU analysis ~1-2 h niced (X build ~40 s per
pair; 6 Mantel tests x ~2.5 min per pair).

## Layout

- `build_inputs.py` — writes `inputs/e8-manifest.json`: sha-pins over the
  reused E2 inputs + committed re-analysis RDMs, HF revision pins, hookpoint
  + basis + BOS conventions, download sizes. Stdlib only, offline,
  deterministic.
- `inputs/e8-manifest.json` — generated, committed; THE pin the container
  asserts against.
- `runner/e8_runner.py` — extraction payload (torch in container;
  `--mock` = deterministic hash-seeded pseudo-SAEs, numpy-only, CPU).
- `analyze.py` — CPU statistics battery (imports the E2 machinery); writes
  `results-e8.json` + `verdict-e8.md` into the stamp dir.
- `test_e8.py` — unit suite: X-matrix correctness, planted-correspondence
  positive control (harness must PASS it), structured-null control
  (correspondence present but kernel-unrelated — harness must return NULL
  with G passing), pure-noise control (G must fail), mock end-to-end through
  the runner + analyze, Modal wiring against a stub.
- `validate.sh` — niced, token-free gate: unit suite + mock e2e + dry-plan.
- Entrypoint: `poc/modal/modal_e8.py`. Results land in
  `poc/e8/results-incoming/<stamp>-modal/`, NOT auto-committed.

## Run plan (coordinator gates the spend)

```bash
bash poc/e8/validate.sh                                   # token-free, this box
poc/modal/.venv/bin/python poc/modal/modal_e8.py --dry-plan   # plan + $ — no token
poc/modal/.venv/bin/modal run poc/modal/modal_e8.py           # THE run (T4)
python3 poc/e8/analyze.py poc/e8/results-incoming/<stamp>-modal   # stats, this box
```

Cost estimate (measured sizes, Modal T4 ~$0.59/h + CPU/mem overhead ≈
$0.75/h loaded): first run ≈ 5–15 min wall (1.28 GB cold downloads dominate)
≈ **$0.10–0.50**; warm re-run ≈ **$0.05–0.15**. Envelope in the tasking was
$5–15 — this sits >10× under it; the headroom is real, not padded.
