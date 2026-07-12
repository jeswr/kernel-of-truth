# KOT-DDC — training-free kernel-guided dimension collapse (PDC): build-ready experiment plan

> **Status: Phase-1 [DESIGN] deliverable in the H-DD family (Programme-3), training-free
> tier. Nothing here is frozen, pre-registered, scheduled, or run; no verdict, audit, or
> frozen object is touched. This document composes the build-ready plan only — it states
> NO feasibility conclusion; the pre-registered outcome map (§11) fixes the wording of
> every possible result in advance, and the verdict, when it comes, is a pure function of
> the frozen record and the chained log.** Author: Fable, experiment-designer role
> (design side only; run, grade, and audit are other identities).
>
> **Provenance of this revision:** a multi-agent workflow drafted §§0–5.0; this
> finalisation (2026-07-12) completes §§5.1–12 + Appendices, applies the review's two
> technical fixes ((a) A2 basis orthonormalisation, §2.3; (b) centred-vs-uncentred
> second moment, §2.2/§2.5), folds in the convergent cross-model GPT-5.6 proposal
> (§1.3), and pins `poc/pubeval` as the evaluator (§5.1) in place of the draft's
> lm-eval assumption. Registry experiment ids claimed: **`ddc0`** (Stage-0 statistics)
> and **`ddc1`** (the arm campaign) — no collision with any id in
> `registry/experiments/`.
> **ASM block claimed: ASM-1650..1679** — renumbered from the workflow draft's
> original 1470-block claim because the register tail moved during authoring (sparq PR-1 consumed
> a 15xx block; the benchmarks survey and pubeval builds claimed PROPOSED-ASM-1590..1629);
> 1650..1679 verified collision-free repo-wide at finalisation time. If a concurrent
> wave consumes the block, the coordinator renumbers doc + rows together before commit,
> per house practice. The coordinator lands this file, appends Appendix A's assumption
> rows to `registry/assumptions.jsonl` in the same commit, and routes the document
> through the standing external-review gate before commit.
>
> **REWORK revision (2026-07-12, same day):** the standing cross-vendor external
> review (`poc/gpt56-review/ddc-review/`, final message) returned **REWORK — the
> core experiment is viable, but the preregistration is not statistically
> freeze-ready** — and this revision applies its three mandated fixes: (review
> fix 2) §2.3 now defines the A2 alignment MATHEMATICALLY — exact ridge-CCA and
> Procrustes matrices, the ridge grid, the concept splits, the direction scores,
> the null statistic, every tie-break, and the fail-closed treatment when fewer
> than r valid top-up vectors remain; (review fix 3) Procrustes is treated
> explicitly as an alignment MAP from which direction pairs are EXTRACTED and
> TESTED, under a single Westfall–Young **max-stat permutation family across
> directions × layers × method-selection**; (review fix 4) gate I-5 is replaced —
> a superiority MDE ≤ 3 points does not establish TOST power; §5.2 now carries a
> declared SESOI, a real TOST decision rule, and a pre-registered power
> SIMULATION with separate superiority and equivalence legs. Changed or new
> stipulations are re-issued as **PROPOSED-ASM-1700..1719** (verified
> collision-free at revision time; central register tail ASM-1691);
> ASM-1652/1656/1663/1668 are superseded by citation (Appendix A.1) and are no
> longer cited as live premises anywhere in this document. The review's
> remaining, non-mandated items (Holm-family enumeration detail, outcome-map
> inconclusive rows, C2 diversity matching, I-6 escalation, M1 count-matching
> exactness, I-1 max-error bound, re-costing from measured throughput) are left
> for the re-review pass and change no section structure here. This revision
> writes nothing to `registry/assumptions.jsonl`.
>
> **Re-review residual fix (2026-07-12, same day):** the cross-vendor re-review
> (`poc/gpt56-review/ddc-rereview/`, final message) returned **SHIP-WITH-FIXES**
> — REWORK fixes 2 and 3 FIXED, fix 4 substantively fixed — with ONE residual:
> the §5.2 superiority-power simulation specified PAIRWISE per-item outcomes,
> but the primary Δ* is the MINIMUM of two CORRELATED contrasts — both share
> the A1 outcomes, and R1 enters as a mean over its three seed columns — so
> independent pairwise simulation legs misstate min-statistic power. This
> revision replaces the simulation's data-generating model with a
> pre-registered JOINT per-item outcome model over (A1, M1, all R1 seeds)
> carrying an explicit, fully-swept dependence grid, and gates at the
> least-favourable registered dependence configuration (§5.2 + gate I-5, now
> v3). The changed stipulation is re-issued as **PROPOSED-ASM-1720** (block
> 1720..1729 claimed; verified collision-free repo-wide at revision time;
> central register tail ASM-1691); ASM-1704 is superseded by citation
> (Appendix A.2) and is no longer cited as a live premise anywhere in this
> document. This revision writes nothing to `registry/assumptions.jsonl`.
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = a programme registry
> verdict/record restated strictly inside its envelope; `[LIT-BACKED: ref]` = an external
> fact verified at source, cited by arXiv id/DOI/year (through `docs/next/lit/SURG.md`
> where that review covers it); `[STIPULATED: ASM-id]` = a design choice made here —
> every design CHOICE below is stipulated, none is smuggled in as established fact;
> `[EXTRAPOLATION: ASM-id]` = a registered projection, never a premise.
>
> **Inputs read in full at source:** the two method proposals (PDC, PAP) + their
> critiques; the cross-model GPT-5.6 proposal
> (`poc/gpt56-review/dimcollapse-gpt/last-message.json`); the pruning-landscape survey;
> `docs/next/lit/SURG.md` (P3-LR-SURG) §§1–8;
> `docs/next/programme-3-neurosymbolic-architecture.md` §3.5 (H-DD reformulation,
> P3-E-DD-0/1) and §5 (P3-D-DD row); `docs/next/design/rules-1-knull-ablation.md` (knull
> arm mechanics); `registry/experiments/knull.json` (plain-dictionary store pins);
> `poc/pubeval/` (harness source read in full; per-item-emission gap verified in
> `pubeval_runner.py`); `docs/next/analysis/existing-benchmarks-survey.md`;
> `tools/registry/claims-check.py` + `registry-check.py` (lint mechanics);
> `docs/next/optimal-resource-usage-plan.md` (Modal batching + hygiene rules).

---

## 0. Plain-language summary (maintainer-facing)

We take a small open language model and physically shrink it — deleting a chosen
fraction of the directions its internal computations run along — **without any
training**, using published, well-understood surgery (the SliceGPT rotate-and-slice
construction). The single question this experiment asks: **does choosing WHICH
directions to keep using the kernel — the NSM-grounded concept explications, and, in
one arm, the rules-engine's computed consequences — preserve more of the model's
measured ability than choosing them by weight magnitude or at random, at the same
size reduction?**

Five things make this worth running as designed:

1. Every arm is training-free and inference-only: the whole campaign is forward
   passes plus closed-form linear algebra — tens of GPU-hours, ~$40–60 total.
2. The controls are the honest ones. Besides the task-mandated magnitude and random
   controls, we keep the two controls that can *deflate* a kernel win: the same
   surgery calibrated on generic web text (if the kernel arm merely ties it, the
   result is "any small corpus steers pruning", which is already published), and the
   same surgery calibrated on the knull plain-dictionary store (if knull ties the
   kernel, NSM content specifically adds nothing).
3. The evaluation is public, human-built benchmarks scored by the programme's own
   pinned harness over third-party gold — nobody in this programme authored a single
   test item, so the result cannot be an artifact of our own evaluation design.
4. The claim wording for every possible outcome is fixed in advance (§11), so the
   result — positive, null, or negative — gets reported at exactly the strength the
   data licenses.
5. A near-zero-cost statistics stage (G0) runs first and can kill the weakest arm
   before any surgery is paid for.

What this experiment is NOT: it is not the recovery-trained, store-backfilled H-DD
arm experiment (P3-E-DD-1) — that design keeps its retrained-pruning+distillation
comparator and its store; this is the cheaper, training-free question that precedes
it. A win here supports only a training-free claim; a loss here does not kill the
recovery-trained bet.

---

## 1. Positioning, and what was picked

### 1.1 Method choice

DECISION [STIPULATED: ASM-1650]: the experiment runs **PDC (project-drop-complement)** on the SliceGPT
scaffold as the sole surgical method, with the PAP proposal's one distinctive
mechanism — orthogonal alignment computed directly against native-dimension kernel
vectors — absorbed as a *variant of PDC's geometry sub-arm* rather than a separate
method [STIPULATED: ASM-1650].

Reasoning, briefly: PDC is the best-defined and most-testable proposal — its
surgery is the literature-proven rotate-and-slice construction
[LIT-BACKED: SURG §2.1, arXiv:2401.15024, 2024], its critique verdict was
"needs-work" with three named, fixable pre-registration defects (all fixed below,
§2.4), and its control structure is already the falsifiable one. PAP as transmitted
is truncated and its Procrustes alignment is available only where kernel dimension
equals model dimension — exactly the condition PDC-B already exploits at d=576 —
so it contributes a basis-selection variant (§2.3), not a second method. The
critique's decisive-test staging (statistics first, slice second) is adopted as the
gate structure (§8).

### 1.2 Relation to the standing H-DD lineage

- This experiment discharges the *training-free* slice of the P3-D-DD design
  obligations: the invariance validation standard, the basis-selection rule pinned
  as an IV, super-weight handling, and the bytes parameterisation (SURG §7 open
  questions 1, 2, 4, 7) are answered here for the SmolLM2 donors. The
  recovery-compute symmetry rule, store-backfill interface, and the retrained+KD
  comparator (SURG §7 questions 3, 5, 6, 8–10) remain with P3-E-DD-0/1 and are
  **out of scope by design** — this campaign contains no training, so the
  retrained comparator would be a category error here; its absence is a stated
  limit on claim scope (§11), not an omission.
- PREMISE: an arbitrary bridge-free per-layer rotation is NOT function-preserving;
  orthogonal residual-stream rotations are absorbable only after RMSNorm gain
  fusing, and per-block rotations additionally require explicit residual bridge
  matrices — SliceGPT's actual scheme [LIT-BACKED: SURG §2.1–§2.3,
  arXiv:2401.15024 + arXiv:2404.00456, 2024]. Every surgical step below stays
  inside that derived group, and gate I-1 (§8) verifies it end-to-end.
- The standing resource-plan exclusion of H-DD GPU cells predates Programme-3's
  promotion of the dimension-drop bet; launching this campaign consumes the
  Programme-3 authorization, and the launch gate (§9, MD-1) makes that supersession
  explicit for the maintainer rather than silent.
- Law-1 interface-locality compliance, stated plainly: **no kernel vector ever
  enters the model.** Kernel text enters as calibration input (text); kernel
  vectors participate only outside the model, in selecting which of the *model's
  own* activation directions are kept. The raw-foreign-coordinates cell stays
  empty.

### 1.3 Cross-model convergence (GPT-5.6 proposal), and what was folded in

An independent cross-model proposal ("kernel-protected layer-selective low-rank
factorisation", `poc/gpt56-review/dimcollapse-gpt/last-message.json`, produced
against the same repository without sight of this plan) **converges on the same
core method**: frozen-model inference plus closed-form ridge-CCA / orthogonal
Procrustes at residual-stream sites, identifying the model subspace whose
activations covary with deterministic kernel encodings; the kernel expressed in the
*model's* basis, never the reverse; above-null alignment as the fail-closed
definition of "kernel-aligned"; magnitude / random / shuffled / structure-destroyed
controls; no gradients anywhere. This convergence is treated as evidence about
method choice only — two designers agreeing predicts nothing about outcomes.

Its strongest specifics are folded in at their citation sites:

- carrier-controlled probes with matched empty-carrier subtraction and
  carrier-half stability checks (§2.3);
- per-direction admission criteria for the aligned set, including a
  minimal-contrast probe stratum and a bag-of-primes structure-destroyed kernel
  null (§2.3, G0);
- the protected-budget cap k ≤ min(d/2, 256) so "kernel-aligned" can never consume
  the whole rank budget (§2.3);
- an explicit definition of *training-free* (below) [STIPULATED: ASM-1667];
- chance-corrected retention reporting (§5.2);
- the coarse-screen / full-evaluation cost split (§5.2, §7);
- its hybrid-as-alignment-target construction (signed-hash closure sketches
  appended to the alignment target, with shuffled-closure and stated-facts-only
  nulls) is registered as FORK-5 (§10), not adopted in v1.

Where it is deliberately NOT followed: (i) its per-matrix low-rank factorisation
scaffold (W′ = WP + SVD_{r−p}(W(I−P))) is a different surgical family from
rotate-and-slice; PDC stays the sole method per §1.1, because one surgery family
keeps every arm an exact structural twin. (ii) Its SVD-only attribution control is
discharged *inside* the rotate-and-slice family by C1 — generic-corpus
activation-PCA slicing IS the kernel-agnostic spectral control here; Wanda is
out-of-family (unstructured scalar sparsity; M2 is the disclosed dense-mask
analogue). (iii) Its evaluation suite (MMLU / HellaSwag / LAMBADA / WikiText-2 via
lm-eval) is not adopted, for the §5.1 reasons.

**Training-free, defined for this document** [STIPULATED: ASM-1667]: no learned
neural parameters, no optimizer, no loss-minimisation loop, no labelled-task
adaptation; frozen-model forward passes and closed-form calibration algebra
(covariance, eigendecomposition, SVD, CCA, Procrustes, analytic least squares) are
permitted. Under a stricter definition forbidding all data-dependent fitting, the
A2 alignment would be barred and only a fixed JL projection would remain — which
aligns dimensions, not semantics; every use of "training-free" below means the
stated definition.

---

## 2. The method, concretely enough to implement

### 2.1 What "normalise to the kernel" means here

Replace the model's d-dimensional residual stream with its orthogonal projection
onto an r-dimensional subspace (r < d) selected to span the model's own
representations *of kernel content*, then delete the orthogonal complement from
every weight matrix that reads from or writes to the residual stream, so the
compressed model can only compute with directions the kernel accounts for. The
normalisation is a rotation folded permanently into the weights plus a truncation —
never an activation-time intervention. The rotation is exactly function-preserving
under the conditions of §2.5; the truncation is a controlled approximation whose
damage is measured directly on public benchmarks, because what the basis selection
optimises (calibration-activation reconstruction) is a proxy, not behaviour
[LIT-BACKED: SURG §2.1, arXiv:2401.15024 §3.4, 2024].

### 2.2 STATIC-kernel arm (A1, the primary kernel arm)

Mechanics = SliceGPT with the calibration corpus swapped for the rendered kernel:

1. **Calibration corpus K-static** [STIPULATED: ASM-1651]: deterministic
   `renderExplication` (`encoder/src/render.ts`) over all committed concept records
   — the 65-prime profile-1 lexicon, the 54 kernel-v0 explications
   (`data/kernel-v0/concepts/`), and molecules-v0 (`data/molecules-v0/`) — plus
   seeded `generateExplication` (`encoder/src/synth.ts`) span expansion across the
   depth × clause-count grid, to N = 4096 sequences, ≤256 tokens each, seed 0,
   exact-duplicate-deduplicated. The corpus is hash-pinned under the current
   kot-corpus-hash recipe before freeze.
2. One forward pass (fp32); collect the token-activation matrix X_l at every
   residual block boundary l (embedding output, each block's post-residual output).
3. Per-layer basis Q_l = eigenvectors of the **uncentred second moment**
   (1/N)·X_lᵀX_l, sorted by kernel-corpus **energy**; keep the top r_l (§4 sweep).
   The centred-vs-uncentred choice is resolved deliberately, not by library default
   [STIPULATED: ASM-1665]: centring subtracts the corpus mean activation, and in
   small Llama-family models the massive-activation component induced by the
   documented super weights is a near-constant, high-magnitude direction
   [LIT-BACKED: SURG §2.4, arXiv:2411.07191, 2024] whose *centred variance* can be
   negligible even though deleting it is catastrophic — a centred basis would
   silently slice it and destroy every arm for reasons unrelated to basis choice.
   The uncentred moment ranks by energy, so that direction survives on its own
   mass. The identical convention applies to every PCA-based arm (A1/A3/C1/C2/C3),
   so the convention cannot confound any cross-arm contrast; a per-cell
   energy-capture diagnostic and tripwire back this up (§2.5, gate I-6). This step
   is mechanically SliceGPT-with-a-special-corpus, and is *claimed as nothing
   more*: the arm's novelty is zero by itself (domain-steered calibration pruning
   is published practice — D-Pruner, NAACL 2024; calibration-curation studies
   arXiv:2510.10618); kernel-specific value exists only relative to the C1/C2/C3
   controls (§3).
4. Surgery per §2.5; evaluation per §5.

### 2.3 Geometry sub-arm (A2 — PDC-B, native dimension only, gated by G0)

The only arm in which the kernel's *geometry*, not merely its text, guides the
drop — and the only arm whose success would license a kernel-geometry claim:

- **Pairing.** Pair each concept c_i with (a) its model-side representation
  h_l(c_i) and (b) its canonical encoder vector v_i from the quasi-orthogonal
  native codebook (`encoder/src/encoderQ.ts`, D ∈ {512, 576} enforced fail-closed
  by ERR_QUASI_DIMENSION — verified in source at `encoder/src/codebookQ.ts`).
  d=576 matches SmolLM2-135M exactly; **A2 therefore exists only on the 135M
  donor**. On the 360M donor (d=960) the encoder fails closed and the
  JL-projected route is explicitly refused: a random 8192→960 map carries no model
  alignment, and running it would report a PDC-A-equivalent mechanism under a
  geometry label — the critique's "silent degradation" failure mode. The E1
  512-d toy is dropped with reason: the public-benchmark endpoint (§5) is
  undefined on a toy that cannot attempt the benchmarks.
- **Probe construction** (critique mandatory fix 3; carrier machinery folded from
  the GPT-5.6 proposal) [STIPULATED: ASM-1700]: each concept is probed under
  P = 4 fixed carrier templates (canonical rendering alone; "The defined concept
  means: …"; a cloze carrier ending in a fixed delimiter; a question-form carrier
  with no answer requested) × ≥2 seeded render variants — ≥8 probe instances per
  concept, kernel target identical across carriers. h_l(c_i) = mean over all
  non-BOS tokens, averaged over probe instances, with (i) the matched
  **empty-carrier activation subtracted** per carrier (removes the carrier/template
  component at source) and (ii) the corpus grand mean μ_l subtracted across
  concepts (removes whatever shared component remains — the critique's flagged
  template/function-word artifact). A pre-registered diagnostic reports the
  variance fraction of the top principal component of {h_l(c_i)}: a single
  dominant direction is reported as template artifact, not concept structure. The
  probe set adds a **minimal-contrast stratum**: pairs of explications differing in
  exactly one prime, role, clause order, depth, or polarity — the structure-vs-
  vocabulary discriminator used by the admission criteria below.
- **Alignment step — defined mathematically** (critique mandatory fix 1; review
  REWORK fix 2) [STIPULATED: ASM-1700]. Fix a layer l and let n be the number
  of paired concepts (n ≈ 119; the exact inventory is pinned at T0). Let
  H ∈ R^{n×d} carry rows h_l(c_i) after the probe pipeline above
  (empty-carrier subtraction, probe-instance averaging, grand-mean centring),
  and V ∈ R^{n×d} carry the column-centred canonical encoder vectors v_i
  (D = d = 576). No benchmark item appears anywhere in the alignment data.
  - **Concept splits, fixed once.** Concepts are partitioned ONCE by seeded
    draw (seed 0), stratified by record class (primes / kernel-v0
    explications / molecules-v0), into **FIT** (60%, n_F = ⌈0.6n⌉), **SEL**
    (20%, n_S = ⌈0.2n⌉) and **TEST** (the remainder) — by concept, never by
    probe instance (all carriers travel with their concept). The one
    partition serves every layer, both methods, and every permutation
    replicate. FIT fits matrices and selects λ; SEL is reserved for
    admission criteria 2–4; TEST is read exactly once per candidate, after
    every selection is frozen.
  - **Ridge-CCA, exactly.** On FIT: S_hh = H_Fᵀ H_F / n_F,
    S_vv = V_Fᵀ V_F / n_F, S_hv = H_Fᵀ V_F / n_F. Solve the regularised
    canonical eigenproblem
    (S_hh + λI)⁻¹ S_hv (S_vv + λI)⁻¹ S_hvᵀ a_j = ρ_j² a_j
    (economy-SVD implementation; the unregularised problem is rank-deficient
    at n_F ≈ 71 ≪ d = 576 — the critique's original ill-posedness defect),
    variates normalised a_jᵀ (S_hh + λI) a_j = 1; kernel-side partner
    b_j = (S_vv + λI)⁻¹ S_hvᵀ a_j / ρ_j. One λ serves both blocks (the
    quasi-orthogonal codebook side is near-white by construction; a single λ
    removes one selection degree of freedom).
  - **Ridge grid + leave-one-concept-out selection.** λ ∈ {10⁻⁴, 10⁻³,
    10⁻², 10⁻¹, 1} × tr(S_hh)/d — five values, fixed now, selected per
    layer. For each λ and each FIT concept i: refit on FIT∖{i}; predict
    v̂_i = Σ_j ρ_j (a_jᵀ h_i) β_j with kernel-side loadings
    β_j = V_Fᵀ (H_F a_j)/(n_F − 1), summing all components with ρ_j > 0.
    λ*_l = argmin of the mean LOO error (1/n_F) Σ_i ‖v̂_i − v_i‖²; ties →
    the larger λ.
  - **Procrustes, exactly — a MAP, from which directions must be EXTRACTED
    (review REWORK fix 3).** On FIT: M = H_Fᵀ V_F; thin SVD M = U Σ Wᵀ; the
    (unscaled) orthogonal-Procrustes map is R* = U Wᵀ =
    argmin_{RᵀR = I} ‖H_F R − V_F‖_F. R* itself ranks nothing and is never
    tested as a whole. The tested objects are the principal alignment PAIRS
    of the cross-covariance: model-space direction u_j = column j of U,
    kernel-space partner w_j = column j of W, fit-strength σ_j (descending).
    σ_j orders CANDIDATES only and confers no admission — kernel-alignment
    of every pair is established exclusively by the held-out score against
    the max-stat null below.
  - **Candidate sets and direction scores.** Per layer per method, J =
    min(64, n_F − 1) candidates: for ridge-CCA the unit-normalised a_j
    (paired with b_j) in descending ρ_j; for Procrustes the (u_j, w_j) pairs
    in descending σ_j. Ordering ties → lower index j after the deterministic
    sign convention (first nonzero component of the model-side vector made
    positive). Score of a candidate: s_{m,l,j} = the SIGNED Pearson
    correlation, over TEST concepts only, between H_T u and V_T w —
    one-sided: the fitted sign must reproduce.
  - **Null statistic with max-stat correction across directions × layers ×
    method-selection (review REWORK fix 3)** [STIPULATED: ASM-1701]: B =
    1000 permutations π_b (pinned PRNG stream, seed 1) of the GLOBAL
    concept→vector pairing — v-rows permuted across all n concepts;
    partition membership stays with the concept on the model side. Each
    replicate re-runs the ENTIRE pipeline — per-layer LOO λ re-selection,
    CCA eigen-solve, Procrustes SVD, candidate extraction, TEST scoring —
    for BOTH methods at EVERY layer, and records the single maximum
    T_b = max_{m,l,j} s^{(b)}_{m,l,j}. If FORK-2's diagnostic routes to
    last-token pooling, the pooling variant is added to the max family, so
    the fork cannot inflate the error rate. Admission p-value of an
    observed score: p = (1 + #{b : T_b ≥ s_{m,l,j}}) / (B + 1); criterion 1
    passes iff p ≤ 0.05 — Westfall–Young FWER control at α = 0.05, jointly
    over every direction, every layer, and the CCA-vs-Procrustes choice; no
    uncorrected per-direction null appears anywhere in admission. Cost:
    closed-form algebra at d = 576, n ≈ 119 — 1000 full refits are
    CPU-minutes, inside the G0 budget.
  - **Method selection (FORK-1), after correction:** the method with
    max-stat-admitted directions (all four criteria below) in more layers
    advances; a tie → ridge-CCA (pre-declared v1 default). If neither
    method admits a direction in at least ⌈L/3⌉ layers, A2 is dead before
    any surgery (gate G0, §8).
- **Admission criteria, per aligned direction** (folded from the GPT-5.6
  proposal; all four required; criteria 2–4 are conjunctive FILTERS — they can
  only remove candidates, so criterion 1 alone carries the family-wise error
  control) [STIPULATED: ASM-1702]:
  1. **max-stat significance:** TEST-partition score s_{m,l,j} with max-stat
     p ≤ 0.05 against the joint directions × layers × methods permutation
     family above [STIPULATED: ASM-1701] — never a per-direction 95th
     percentile;
  2. carrier-half stability — refit on FIT with the carriers split into the
     two fixed halves {1,2} vs {3,4}; the direction is recovered in both
     halves with |cos ∠(u^{(12)}, u^{(34)})| ≥ 0.8, the halves' candidates
     matched by maximal kernel-side |cosine|;
  3. survives the minimal-contrast subset — the signed correlation on the
     minimal-contrast stratum (housed in SEL) is positive with per-stratum
     permutation p ≤ 0.05 (B = 1000, same seed stream);
  4. beats the **bag-of-primes structure-destroyed kernel null** (same concepts
     encoded with roles, clause order, and depth deleted): compute s^bag
     identically with v_i replaced by the bag encoding; the direction is
     admitted as STRUCTURAL only if the seeded paired bootstrap (10³ resamples
     over TEST concepts) 90% CI of s − s^bag excludes 0; otherwise it is
     admitted only as *lexical*, and flagged as such in every table.
  Cap: k ≤ min(d/2, 256) admitted directions per layer, so the protected set can
  never consume the entire rank budget.
- **Basis assembly — orthonormal by construction** (review fix (a))
  [STIPULATED: ASM-1700]: the admitted aligned directions are ordered by
  **null-beating strength** (TEST score s_{m,l,j} minus the shared max-stat
  threshold t* — the ⌈0.95(B+1)⌉-th order statistic of {T_b} — descending;
  ties → lower layer index, then lower candidate index j) and orthonormalised
  by QR / Gram–Schmidt in that
  order, giving Q_A (k columns; the ordering matters — QR preserves the leading,
  strongest directions exactly and orthogonalises weaker ones against them). The
  A1 top-up is then **projected onto the orthogonal complement** (I − Q_A·Q_Aᵀ):
  take the uncentred kernel-corpus PCA vectors (§2.2 convention, energy order),
  project each, discard residuals with norm < 1e-6, re-orthonormalise the
  survivors by QR in energy order, and fill the remaining r_l − k budget slots.
  The final Q_l = [Q_A | Q_top] is orthonormal by construction and verified
  numerically (max |Q_lᵀQ_l − I| ≤ 1e-6, a precondition of gate I-1). Without
  this step the concatenated basis is in general NOT orthonormal — the "rotation"
  ceases to be orthogonal, the RMSNorm commutation of §2.5 fails, and slicing is
  no longer an orthogonal projection; the fix makes that failure impossible
  rather than merely unlikely. Because the top-up is energy-ordered and
  uncentred, the massive-activation direction (§2.2) enters the A2 basis first
  whenever the aligned set does not already contain it — logged per layer. The
  fraction of budget occupied by aligned-vs-topped-up directions is logged per
  layer. **Top-up deficiency, fail-closed (review REWORK fix 2 — the
  fewer-than-r case):** the top-up pool is the FULL uncentred second-moment
  eigenbasis at layer l (all d eigenvectors in energy order), not only the top
  r_l; since d eigenvectors span R^d, exact arithmetic always completes the
  complement. If floating-point discards (projected residual norm < 1e-6)
  nonetheless leave fewer than r_l columns after the entire pool is exhausted,
  the harness raises **ERR_DDC_BASIS_DEFICIENT** and the A2 cell is reported as
  a basis-construction failure — never silently patched: no random completion,
  no threshold relaxation, no fallback to the A1 basis under the A2 label (the
  critique's silent-degradation failure mode, made mechanically impossible).

### 2.4 HYBRID-rules-kernel arm (A3) — stated honestly

The RULES-1 engine is a symbolic fixpoint reasoner over kot-axiom records. It is
not a vector and **cannot participate in the projection algebra; no rule becomes a
matrix.** The hybrid kernel therefore enters exactly two ways, and any claim about
this arm must be worded as corpus-and-eval, never as symbolic machinery inside the
weights [STIPULATED: ASM-1659]:

1. **As calibration content:** corpus K-hybrid = K-static (50%) + rendered axiom
   corpora and worlds — `data/axioms-kinship-v1`, `data/world-v0`, nsk1 worlds —
   AND their engine-computed closures Cl(S) rendered to NL via the rules-1/nsk1
   world-rendering path (50%), same N, token budget matched to K-static within
   ±10%. The closures are the point: the kept subspace is selected to carry
   activations for entailed-but-never-stated facts. The engine's certification is
   real and cited: 858/858 exact decisions on the paired entailment suite
   [MEASURED: registry/experiments/rules-1.json].
2. **As secondary behavioural evals:** engine-gold, kernel-distribution suites
   (`data/l3a-eval`, `data/nsk1-clutrr` host cells) run post-drop as *secondary,
   diagnostic* retention metrics (§5.3). They can never substitute for the public
   primary endpoint — they are in-distribution for this arm's calibration corpus,
   which is precisely the eval-circularity the critique flagged.

(The GPT-5.6 proposal's stronger hybrid mechanism — engine closures entering the
*alignment target* as signed-hash sketches, with shuffled-closure and
stated-facts-only nulls — is registered as FORK-5, §10, contingent on A2 surviving
G0; in v1 the engine's output touches calibration text and secondary evals only.)

### 2.5 Surgery specification (shared by all rotated arms)

All choices below are stipulated as one block [STIPULATED: ASM-1653]:

- **Donors:** `HuggingFaceTB/SmolLM2-135M` and `SmolLM2-360M` — BASE checkpoints,
  revisions pinned at T0. Architecture (Llama-type: RMSNorm, RoPE, gated MLP,
  tied embeddings; 135M: d=576, 30 layers; 360M: d=960, 32 layers, verified
  locally from the cached 360M config) [LIT-BACKED: SmolLM2, arXiv:2502.02737,
  2025; re-pinned from each base checkpoint's config.json at T0].
- **Convention pin** (critique minor-spec bug): weights are PyTorch
  `(out_features, in_features)`; y = xWᵀ. Reading-side matrices (W_q, W_k, W_v,
  W_up, W_gate; in_features = d) transform W ← W Q_r; writing-side (W_o, W_down;
  out_features = d) transform W ← Q_rᵀ W; embedding rows E ← E Q_r; unembedding
  = tied embedding (below). Q_r = first r columns of Q_l.
- **Order of operations:** (1) fuse RMSNorm per-channel gains into adjacent
  matrices, leaving parameter-free RMSNorm — the precondition for rotation
  commutation RMSNorm(X) = RMSNorm(XQᵀ)Q [LIT-BACKED: SURG §2.1,
  arXiv:2404.00456, 2024]; (2) per-block Q_l with explicit residual bridge
  matrices Qᵀ_{l-1}Q_l in each skip connection (SliceGPT's actual scheme —
  bridges are NOT optional) [LIT-BACKED: SURG §2.1, arXiv:2401.15024 §3.3, 2024];
  (3) slice to r.
- **Tied embeddings** (both donors tie input/output embeddings): the tied matrix
  is sliced ONCE in a designated basis Q_emb := Q_1 (identity bridge on the input
  side); one r×r bridge Qᵀ_L Q_1 is inserted before the unembedding read. Tying
  is preserved, embedding bytes compress properly, and correctness is not argued
  but *verified* — gate I-1 requires end-to-end logit equivalence of the
  rotation-only (r=d) model.
- **Untouched, explicitly:** attention head dimensions and RoPE (rotation of the
  d_model axis only — rotations do not cross the k/q RoPE application or the MLP
  nonlinearity, which are not absorbable sites [LIT-BACKED: SURG §2.1,
  arXiv:2404.00456, 2024]); the KV cache; the tokenizer.
- **Super weights** [STIPULATED: ASM-1658]: identified data-free in one forward
  pass and documented per donor before any slicing [LIT-BACKED: SURG §2.4,
  arXiv:2411.07191, 2024]; v1 handling = identical treatment in every arm (no
  protection), so the choice cannot confound cross-arm comparisons. Tied to the
  §2.2 second-moment resolution (review fix (b)): for every constructed basis at
  every cell, the harness logs the **energy capture of the documented
  massive-activation direction(s)** in the kept subspace — under the uncentred
  convention this is expected ≈1 by construction; any cell with capture < 0.99 is
  flagged in the readout (gate I-6) and arms MD-4. A protected-stratum re-run is
  a pre-registered follow-up decision (§9, MD-4), and any headline result whose
  sliced-away mass includes a documented super weight says so in the verdict
  text.
- **Numerics:** fp32 surgery and fp32 evaluation for both donors (135M/360M fit
  comfortably; eliminates dtype noise as a confound). pubeval scoring is
  loglikelihood-based; the GSM8K path is greedy (sampling-free); the only random
  objects in the campaign are the R1 bases, corpus synthesis, and bootstrap
  resampling — all seeded.
- **Probe variant, run first inside S1:** the LASER-style fold-in
  [LIT-BACKED: arXiv:2312.13558, 2023] — project last-third MLP W_down inputs
  onto the kernel subspace (W ← W P_l on the reading side per the convention
  above) without shrinking d_model — scans rank fractions {0.1..0.9} on the 135M
  donor in a few GPU-minutes per point. It is a *scout* (locates
  denoising-vs-damage regimes and sanity-checks the subspace before full
  surgery), logged exploratory, never citable as an arm.

---

## 3. Arms (all at matched compression, §4)

| Arm | Basis / mask selection | Calibration input | Role |
|---|---|---|---|
| **A0** | none (donor unmodified) | — | ceiling anchor at every grid point |
| **A1 kernel-static** | per-layer uncentred PCA of kernel-corpus activations | K-static (§2.2) | the task's "kernel-normalised + dropped (static)"; primary kernel arm |
| **A2 kernel-geometry** | max-stat-admitted ridge-CCA/Procrustes directions vs native Bq vectors, orthonormalised + complement-projected A1 top-up (§2.3) | K-static + kot-enc-Bq/1 at D=576 | 135M only; gated by G0; the only geometry-claim carrier |
| **A3 kernel-hybrid** | as A1 | K-hybrid incl. engine closures (§2.4) | the task's "kernel-normalised + dropped (hybrid)" |
| **M1 magnitude (structured)** | keep the r coordinate dimensions with largest summed squared weight mass across all residual-coupled matrices; no rotation, no bridges | none (data-free) | the task's MAGNITUDE-prune control, same structural family |
| **M2 magnitude (unstructured)** | global weight-magnitude mask to the same retained-parameter count | none (data-free) | secondary, literature-familiar magnitude control; dense-storage caveat disclosed |
| **R1 random** | Haar-random orthonormal Q_l (QR of Gaussian), seeds {0,1,2}; bridges as in §2.5 | none | the task's RANDOM-drop control; structural twin of A1 |
| **C1 generic-text** | as A1 | 4096 C4-en sequences, matched token budget, pinned sample | the corpus-steering deflator: A1 vs C1 is the kernel-specificity contrast; also the kernel-agnostic spectral (SVD-only-analogue) control, §1.3 |
| **C2 knull** | as A1 | the knull plain-dictionary authored store (`poc/knull/inputs/plain-authored.json`, token-band-matched by construction) rendered to gloss text [MEASURED: registry/experiments/knull.json pins] | the content deflator: matched authored definitional text, no NSM grounding |
| **C3 shuffled-kernel** | as A1 | K-static with within-sequence token shuffle, seed 0 (unigram statistics preserved, all structure destroyed) | the house scramble control: separates content from token statistics |

Null-structure mapping, for the record: C1 is this experiment's text-only null; C2
is the kernel-as-text null analogue (the kernel's real opponent under the standing
Law 2); C3 is the scramble control. The magnitude/random controls (M1/R1) carry the
task-mandated claim; the C-family carries the kernel-specificity claim — the two
claims are deliberately separated (§5.4) so a win over M1/R1 with a C1 tie cannot
be reported as kernel value.

Arm × grid coverage (cost control) [STIPULATED: ASM-1654]: A1, A3, C1, C2, M1 run
the full sweep; R1 runs 3 seeds at every 135M grid point (1 seed on 360M); A2 and
C3 and M2 run at ρ ∈ {0.75, 0.5}; the 360M stage runs {A1, A3, C1, C2, M1, R1} at
ρ ∈ {0.9, 0.75, 0.5}.

## 4. Compression grid and matching

- **Sweep** [STIPULATED: ASM-1654]: keep-fraction ρ = r/d ∈ {0.9, 0.75, 0.5, 0.3,
  0.15}, uniform across layers in v1 (allocation policies are FORK-4, exploratory).
  The aggressive tail is expected to be destroyed at this scale for every arm —
  SliceGPT retention at small scale is already ~90% at a 25% cut and degrades fast
  [LIT-BACKED: SURG §6, arXiv:2401.15024, 2024] — the tail is kept because the
  curve, including its floor, is the result, and it is cheap (subset-scored, §5.2).
- **Matched compression = matched retained parameter count** [STIPULATED:
  ASM-1657]. All rotated arms (A1/A2/A3/C1/C2/C3/R1) at the same ρ are exact
  structural twins (identical shapes incl. bridges). M1 carries no bridges, so at
  equal r it would retain FEWER parameters; M1's r is therefore raised to the
  smallest r' whose total retained count ≥ the rotated arms' count at that grid
  point (conservative in M1's favour); M2 is masked to the identical count. Exact
  counts per cell are computed by the harness and logged; no width fraction is
  ever quoted as a size claim. Packed artifact bytes (safetensors, fp32; M2
  additionally in sparse-CSR form) are reported per cell alongside parameter
  counts, and bridge FLOPs are disclosed in the inference-cost note —
  the H-DD correction-#3 discipline (width ≠ bytes) applied as measurement,
  with the full which-matrices-shrink-how parameterisation in Appendix B.
- **Models:** SmolLM2-135M is the primary donor (cheapest; native encoder
  dimension); SmolLM2-360M is the conditional replication donor (S2). No larger
  model is in scope; nothing in this design licenses extrapolation beyond these
  two donors (§8 envelope).

## 5. Evaluation

### 5.0 Instrument principle

Every headline number in this campaign is produced by third-party, human-built,
openly licensed benchmark items scored by one pinned in-house harness whose scoring
path is byte-identical across arms. Nobody in this programme authored a test item;
nothing the programme authored (kernel suites, §5.3) can carry a headline.

### 5.1 Primary instrument — the pinned `poc/pubeval` harness

**Evaluator pin** [STIPULATED: ASM-1655]: the evaluator for every cell is
**`poc/pubeval`** — the programme's public-benchmark harness (built 2026-07-12
against the maintainer's use-existing-human-built-benchmarks directive;
benchmark selection derived from `docs/next/analysis/existing-benchmarks-survey.md`
§4). It is pinned at T0 by content hash over
{`pubeval_runner.py`, `benchmarks.py`, `transforms.py`, `fetch_data.py`,
`modal/modal_pubeval.py`} plus the `data/manifest.json` sha pins
(pin-on-first-fetch; later drift fails closed, ERR_DATA_DRIFT). It runs on the
pinned Modal image (`poc/modal/requirements-image.txt`, sha `0fac7243…` — the same
image as the FROZEN f2b/deconf-b/rules-1 runs). **lm-eval-harness is deliberately
NOT used** — its dependency tree (datasets/pyarrow/…) would force an image change
barred by the image-reuse discipline (PROPOSED-ASM-1106/1610 lineage). This
replaces the multi-agent draft's lm-eval assumption; the task set changes with it.

**Benchmark set** (pubeval as wired; human gold only, no LLM-PROXY):

| Benchmark | Split (eval / few-shot) | n | Task / scoring | License (re-verified at source at T0, gate I-4) | Gold provenance |
|---|---|---|---|---|---|
| `folio` | validation / train | 203 | 3-way forced choice (True/False/Uncertain), loglikelihood | MIT | HUMAN-AUTHORED [LIT-BACKED: arXiv:2209.00840, 2022] |
| `arc_easy` | test / train | 2,376 | 4-way MC, loglikelihood (acc + acc_norm) | CC BY-SA 4.0 | HUMAN-SOURCED exam [LIT-BACKED: arXiv:1803.05457, 2018] |
| `arc_challenge` | test / train | 1,172 | 4-way MC, loglikelihood (acc + acc_norm) | CC BY-SA 4.0 | HUMAN-SOURCED exam [LIT-BACKED: arXiv:1803.05457, 2018] |
| `gsm8k` | test / train | 1,319 | greedy generation, exact match on final number | MIT | HUMAN-AUTHORED [LIT-BACKED: arXiv:2110.14168, 2021] |

**Configuration** (pubeval house convention, unchanged): 5-shot fixed exemplars,
seed 20260712; MC headline = `acc_norm` (per-token-normalised loglikelihood), GSM8K
headline = `exact_match`; gold-continuation perplexity (`gold_ppl`) recorded per
benchmark per cell. Numbers are **internal-relative** — fixed prompts/shots/seed,
never leaderboard-comparable; the harness's designed use is exactly this campaign's
shape: baseline-vs-weight-variant deltas [STIPULATED: ASM-1655].

**Transform-hook comparability guarantee:** every compressed checkpoint enters
through pubeval's weight-transform contract (`fn(model, **kwargs) -> model|None`,
applied once after load and before any scoring; prompts, few-shot exemplars, seed,
and scoring code byte-identical across variants; before/after parameter counts and
weight fingerprints recorded in the results JSON) or the equivalent
`HFLM.from_model` path for surgered artifacts. Metric deltas are attributable to
the weight change alone — the seam pubeval was built to provide.

**T0 mechanical harness additions** (each re-pinned by content hash and
mock-validated at $0 before freeze) [STIPULATED: ASM-1655]:

1. **Per-item record emission** — the paired statistics (§5.2) require per-item
   correctness records (item id, per-option logprobs, acc/acc_norm flags, EM
   flag); the current runner emits aggregates only (verified in source:
   `eval_mc`/`eval_gen` return summary dicts). Adding a `--log-items` sidecar is a
   mechanical harness task, done and re-pinned before freeze; the statistics are
   impossible without it, so gate I-5 cannot pass until it lands.
2. **BASE-checkpoint donor registry entries** — the surgery donors are SmolLM2
   BASE checkpoints (§2.5), while pubeval's current MODEL_REGISTRY pins the
   Instruct carriers of earlier frozen runs. The two BASE revisions are pinned at
   T0 under the same fail-closed rule (ERR_UNPINNED_MODEL). Base-not-instruct
   avoids the chat-template confound in likelihood scoring — also the cross-model
   proposal's independent recommendation (§1.3).

**Informative-task filter** [STIPULATED: ASM-1655]: the registered item pool
includes exactly those benchmarks on which the UNCOMPRESSED donor scores ≥ 10
accuracy points above chance at T0 (chance: FOLIO 1/3, ARC 1/4, GSM8K 0) — a
mechanical filter, fixed per donor at freeze, preventing at-chance tasks from
diluting the instrument. Expected consequences at 135M, disclosed now rather than
discovered later: GSM8K very likely fails the filter (base-135M exact-match ≈ 0),
which also removes the generation stage that dominates pubeval runtime (~60–75% of
suite cost); FOLIO and ARC-Challenge may sit near chance at 135M and drop. Whatever
the filter returns is what runs; if it returns too little to power the primary,
gate I-5 blocks freeze and MD-6 fires (§8, §9).

**Out-of-kernel fluency guard** (critique mandatory fix 2) [STIPULATED: ASM-1666]:
WikiText-2 is not wired in pubeval and is not added (image/scope discipline). The
guard is **gold-continuation perplexity on ARC-Easy** — human-written prose,
out-of-kernel-distribution, the largest item pool — reported for every cell whether
or not ARC-Easy is in the filter set, and never part of any accuracy aggregate. It
catches the domain-overfit collapse in which a sliced model keeps forced-choice
discrimination or kernel-suite scores while losing general fluency; it is the
perplexity term used by the S1→S2 promotion rule (§8).

**Exclusions, for the record:** HellaSwag (machine-generated negatives — fails the
human-built requirement), MMLU (at chance for this model class — uninformative),
LAMBADA (BookCorpus provenance), and any lm-eval-scored variant of the above
(image discipline). The cross-model proposal's suite is therefore deliberately not
adopted (§1.3). EntailmentBank's projection instrument stays with the f2b-transfer
lineage; only its ARC end-task carrier appears here (survey adoption #2 rider).

### 5.2 Endpoint and pre-registered claims

- **The deliverable curve:** retention(arm, ρ) = pooled-item accuracy of the
  compressed model ÷ A0 pooled-item accuracy over the filtered set, plotted
  against measured compression (fraction of parameters removed), one curve per
  arm, with per-cell fluency-guard perplexity alongside. Reported with it, per
  task: raw retention AND chance-corrected retention
  R^cc = (A − chance)/(A0 − chance) (folded from the GPT-5.6 proposal — the
  honest small-model convention near chance). All registered claims ride on raw
  paired accuracy deltas: chance correction is a per-task affine transform whose
  denominator degenerates near chance, exactly the F2 ratio failure mode.
- **Cell-tier discipline** [STIPULATED: ASM-1703]: cells at ρ ∈ {0.9, 0.75, 0.5}
  are scored on **full item sets** and are the only cells eligible for the
  registered statistical family. Cells at the aggressive tail ρ ∈ {0.3, 0.15} are
  scored on a **pre-declared deterministic 500-item-per-task subset** (pubeval's
  `det_u`-ranked subsampling, fixed at T0) — curve reporting only, no registered
  claim ever attaches to a subset-scored cell. This is the GPT-5.6 proposal's
  coarse-screen/full-eval split, adopted as cost control (§7).
- **EXACTLY ONE primary endpoint** [STIPULATED: ASM-1703]: at ρ = 0.75 on the
  135M donor, Δ* = min( retention(A1) − retention(M1), retention(A1) − mean-seed
  retention(R1) ), computed on pooled items over the filtered task set. The
  pre-registered primary claim: **Δ* > 0** — the kernel-calibrated drop retains
  more measured capability than BOTH the magnitude and random drops at matched
  compression — tested by task-stratified paired bootstrap (10⁴ resamples of
  pooled per-item records, resampling within task; statistic = min of the two
  paired deltas), one-sided 95% CI excluding 0. Pooled-item, not macro-average,
  is the primary statistic: pubeval's task pool is small and one 203-item task
  (FOLIO) would dominate macro noise; the macro-average is reported alongside.
  ρ = 0.75 is chosen as the primary point because it is the only grid point at
  which small-model rotate-and-slice is literature-anchored as alive
  [LIT-BACKED: SURG §6, 2024]; an absolute paired-difference primary is used, not
  a ratio, per the standing degenerate-denominator lesson [MEASURED:
  registry/verdicts/f2.json — the F2 kill fired on a degenerate ratio primary].
- **Secondary family, Holm-corrected, pre-registered as one family**
  [STIPULATED: ASM-1703]: (i) Δ* > 0 at ρ ∈ {0.9, 0.5} (full-item cells only —
  the task's "at some drop level" exists-claim resolves ONLY through this
  corrected family, never by uncorrected grid-scanning; the subset-scored tail
  can never enter); (ii) the kernel-specificity contrasts at ρ ∈ {0.75, 0.5}:
  retention(A1) − retention(C1), −(C2), −(C3); (iii) retention(A2) −
  retention(A1) at ρ ∈ {0.75, 0.5} (geometry over corpus; only if G0 passes);
  (iv) retention(A3) − retention(A1) (closure content); (v) 360M replication of
  the primary contrast (only if S2 runs).
- **Equivalence machinery — SESOI + TOST, pre-registered (review REWORK
  fix 4, definition side)** [STIPULATED: ASM-1703]: the SESOI is **±3.0 pooled
  accuracy points**, declared as the ddc1 primary endpoint's
  `smallest_effect_of_interest` in the registry record (the fail-closed freeze
  constraint behind every equivalence/NULL row of §11). Rationale, stipulated
  not derived: a paired pooled effect below 3 points sits inside the
  fixed-prompt instrument's exemplar/seed sensitivity band and would change no
  programme decision — it would neither motivate the recovery-trained
  follow-up nor retire the training-free tier; the margin is symmetric and
  identical for every registered equivalence claim. TOST operationalisation:
  two one-sided task-stratified paired bootstrap tests at α = 0.05 each (10⁴
  resamples, the same machinery as the primary) — equivalently, "equivalent"
  is declared iff the 90% percentile-bootstrap CI of the paired pooled delta
  lies entirely inside (−3.0, +3.0). Equivalence claims attach only to
  full-item cells and only to the contrasts pre-listed in this section; a
  wide-CI non-result (neither superiority nor CI containment) reads out as
  INCONCLUSIVE-underpowered, never as equivalence. The ±3.0 value survives
  from the draft (whose ±1.5 predecessor was set against an ≈8k-item lm-eval
  pool the pinned instrument does not have), but its power claim is no longer
  inherited from a superiority MDE — see the gate below.
- **Power gate v3 — superiority AND equivalence powered separately, on the
  JOINT contrast distribution (review REWORK fix 4, power side: a superiority
  MDE ≤ margin does NOT establish TOST power; the two one-sided equivalence
  tests at true Δ = 0 need margin/SE ≥ z₀.₉₅ + z₀.₉₅ ≈ 3.29, not the
  superiority requirement z₀.₉₅ + z₀.₉₀ ≈ 2.93. PLUS re-review residual fix:
  Δ* is the MINIMUM of two contrasts that SHARE the A1 outcomes — with R1
  entering as a mean over its three seed columns — so the two component
  deltas are correlated by construction, and simulating each pairwise
  contrast independently misstates min-statistic power; the simulation must
  draw the contrasts from their JOINT distribution)** [STIPULATED:
  ASM-1720]: at T0, after the informative-task filter fixes the pool, a
  pre-registered, seeded power SIMULATION runs (script
  `poc/ddc/power_sim_ddc1.py`, pinned in the ddc1 record alongside the
  analysis script; 2×10³ simulated campaigns per scenario cell; Monte-Carlo
  SE ≈ 0.007 at power 0.9, disclosed).
  **Data-generating model — JOINT, per item:** per filtered task t with
  measured item count n_t and measured A0 accuracy p_t, each simulated item
  draws the full outcome VECTOR (X^A1, X^M1, X^R1_s0, X^R1_s1, X^R1_s2) ∈
  {0,1}⁵ as follows. (1) X^A1 ~ Bernoulli(p_t). (2) Each control column
  C ∈ {M1, R1-seed-0, R1-seed-1, R1-seed-2} is generated RELATIVE to A1 by
  conditional flips: given X^A1 = 1 the column flips to 0 with probability
  a_C = (q + Δ_C)/(2 p_t); given X^A1 = 0 it flips to 1 with probability
  b_C = (q − Δ_C)/(2(1 − p_t)) — exactly reproducing, per pairwise contrast,
  the v2 marginals P(X^A1 ≠ X^C) = q and true paired delta
  E[X^A1 − X^C] = Δ_C = q(2θ_C − 1). A scenario cell whose (a_C, b_C) fall
  outside [0,1] at any measured p_t is reported INFEASIBLE-AT-MEASURED-p and
  excluded with disclosure — never silently clamped. (3) **Dependence — the
  object of this fix:** the four flip indicators of one item are driven by a
  single Gaussian-copula latent vector Z ∈ R⁴ with equicorrelation c (column
  C flips iff Φ(Z_C) < its conditional flip probability), with c swept over
  the full registered grid **c ∈ {0, 0.5, 1}**: c = 0 is conditional
  independence of the control columns given the shared A1 outcome (the
  shared-A1 correlation floor — the two contrasts still correlate through
  X^A1 itself); c = 1 is comonotone flipping (the same items are discordant
  in every contrast). (4) The second contrast uses the registered estimator
  exactly: per item, δ^AR = X^A1 − (1/3)Σ_s X^R1_s; δ^AM = X^A1 − X^M1;
  Δ* = min of the two pooled contrasts computed from these JOINT draws —
  never from two independently simulated pairwise legs. Every simulated
  campaign is analysed by the EXACT pre-registered pipeline (task-stratified
  paired bootstrap of the min statistic, 10⁴ resamples). Scenario grid:
  q ∈ {0.10, 0.15, 0.20, 0.25, 0.30} × Δ ∈ {0, +3.0} × c ∈ {0, 0.5, 1},
  reported in full; the GATE evaluates at the stipulated reference
  discordance **q_ref = 0.25** (planning bound from the SURG §6 small-donor
  retention band); the measured discordance of every registered contrast is
  recomputed in-flight by the analysis script, and any claim whose measured
  q exceeds q_ref is flagged in the readout with its achieved power (TOST
  itself stays self-policing — equivalence is only ever declared from the
  actual 90% CI). **Gate I-5 v3 requires BOTH**, at the measured filtered
  counts: (i) **superiority power ≥ 0.9** at true Δ_M1 = Δ_R1 = +3.0 (both
  component deltas at the boundary — the least-favourable boundary
  configuration) on the min-statistic Δ* from the joint model, taken as the
  **MINIMUM over the dependence grid c** — the least-favourable registered
  covariance configuration gates, so the pre-registered power never rides on
  an optimistic dependence assumption (for two boundary-mean contrasts,
  E[min] falls as their correlation falls — E[min] = Δ − σ_δ√((1−ρ)/π) for
  bivariate-normal contrast estimates — so low-c cells are expected binding;
  the attaining c* is disclosed, not assumed); (ii) **equivalence power
  ≥ 0.9** at true Δ = 0 for a pairwise TOST contrast (90% CI ⊂ (−3.0,
  +3.0); the machinery is identical for every TOST row; a single pairwise
  contrast is the MARGINAL of the joint model, so c does not enter this
  leg). Closed-form anchors, reported never gating — and disclosed as
  PAIRWISE anchors that upper-bound the min-statistic leg (at c < 1 the
  joint min-statistic power is strictly below the pairwise anchor by
  construction; the joint simulation, not the anchor, gates): with the full
  three-MC pool (n ≈ 3,751) at q_ref, SE ≈ 0.82 points and margin/SE ≈ 3.68
  — both legs nominally powered; if the filter reduces to ARC-Easy alone
  (n = 2,376), SE ≈ 1.03 and margin/SE ≈ 2.93 < 3.29 — the equivalence leg
  FAILS and MD-6 fires. Disclosed now: the draft's superiority-MDE gate
  concealed exactly this gap (an ARC-Easy-only pool at q ≤ 0.25 passes
  MDE ≤ 3.0 marginally while TOST is underpowered); under the corrected gate
  that outcome blocks freeze instead of shipping vacuous equivalence
  wording. Failure of either leg blocks freeze and surfaces MD-6.

### 5.3 Secondary, kernel-distribution suites (diagnostic only)

For A1/A2/A3 (and A0 as anchor): the 858-item engine-gold entailment suite
(`data/l3a-eval`) and the nsk1-clutrr host cells (`data/nsk1-clutrr`),
exact-match-scored against engine-certified labels [MEASURED:
registry/experiments/rules-1.json]. These are in-distribution for the kernel arms'
calibration corpora and are therefore labelled kernel-distribution diagnostics in
every table; they measure whether inference-bearing content survives the drop, and
they can never carry the headline claim.

### 5.4 What each comparison can and cannot say (fixed now)

- A1 vs {M1, R1}: the task-mandated claim — kernel-guided beats
  magnitude/random at matched compression. This alone says a *small coherent
  calibration corpus* steers slicing; it does not distinguish kernel content from
  any text.
- A1 vs C1 (and C2, C3): the kernel-specificity claim. Only a win here elevates
  the result above published corpus-steering; only A2 > A1 (native dim) would
  further elevate it from corpus to geometry.
- A3 vs A1: attributable solely to calibration-corpus content (closures), by
  construction (§2.4).

## 6. Procedure, stages, and execution split

| Stage | Content | Compute |
|---|---|---|
| **T0 mechanical** | pin donor BASE revisions + configs and add them to the pubeval MODEL_REGISTRY (fail-closed); build + hash-pin the five calibration corpora (K-static, K-hybrid, C4 sample, knull render, shuffle) with token-budget matching (gate I-3); land pubeval per-item emission + re-pin the harness content hash + `--mock` green at $0; `fetch_data.py` + `--verify` sha-pins for benchmark bytes; re-verify benchmark licenses at source (gate I-4); run A0 baselines (informative-task filter fixed; fluency-guard baseline recorded); super-weight census incl. massive-activation direction identification (§2.2/§2.5, feeds gate I-6); power SIMULATION run — superiority + equivalence legs on the joint contrast distribution (§5.2, gate I-5 v3); `--dry-plan` cost check per planned batch | CPU + ≤1 h small GPU |
| **G0 statistics (`ddc0`)** | forward passes over K-static/C4/knull + the carrier probe set on 135M; per-layer principal angles + subspace-overlap (1/r)‖P_ker P_C4‖²_F between top-r kernel and C4 subspaces (uncentred convention); ridge-CCA and Procrustes vs native Bq under the joint max-stat permutation family (directions × layers × methods, §2.3); the four admission criteria incl. carrier-half stability, minimal-contrast subset, and the bag-of-primes structure-destroyed null (§2.3); template-variance diagnostic; FORK-1/FORK-2 resolution | ≤2 GPU-h |
| **Freeze** | pre-freeze skeptic memo (mandatory, incl. the oracle-leakage checklist — note the primary endpoint is third-party public benchmarks scored by the pinned harness, so the eval's gold labels cannot coincide with any mechanism-internal accept test); then `prereg-freeze.py` for `ddc1`; freeze-before-run, append-never-edit | $0 |
| **S1 campaign (135M)** | LASER scout; surgery for all arm × grid cells (closed-form, minutes each); basis-orthonormality check + rotation-validation gate I-1 per rotated arm; pubeval full-item runs at ρ ∈ {0.9, 0.75, 0.5} and pinned 500-item subset runs at ρ ∈ {0.3, 0.15} (§5.2 cell tiers) + fluency guard + secondary suites per cell (~47 cells) | ≈12–17 GPU-h A10G |
| **S2 campaign (360M, conditional)** | reduced grid (§3) on promotion rule §8 | ≈10–12 GPU-h A10G |
| **Analysis + verdict** | pinned analysis script only; `verdict-gen.py` mechanical; anything else logged exploratory | CPU |

Execution split per the standing role separation: Fable implementer beads own the
surgery/statistics code, the corpora builders, and the two pubeval mechanical
additions; the runner identity owns Modal launch scripts, monitoring, log appends,
and the mechanical verdict; the cross-vendor auditor confirms any computed PASS;
interpretation is a Fable interpretation bead; this designer identity touches none
of the final runs. The document itself goes through the standing external-review
gate before the coordinator commits it.

**Record freeze-shape note (mechanical, so `prereg-freeze --experiment ddc0|ddc1
--dry-run` passes on first drafting)** [STIPULATED: ASM-1705]: two DRAFT kot-reg
records are drafted from this design before freeze. **`ddc0`** (Stage-0
statistics): exactly one primary endpoint — `n_layers_admitted`, the number of
layers in which the winning method admits ≥ 1 direction under all four §2.3
criteria; primary claim n_layers_admitted ≥ ⌈L/3⌉; mandatory baselines = the
permutation-null, bag-of-primes, and C4-subspace comparisons; no NULL verdict
row (so no SESOI is required on the ddc0 primary); verdict rules end in the
INCONCLUSIVE catch-all. **`ddc1`** (arm campaign): exactly one primary
endpoint — Δ* at ρ = 0.75 on 135M — carrying `smallest_effect_of_interest` =
3.0 pooled points (the §5.2 SESOI; required because §11's TOST rows freeze as
NULL-capable rules); verdict rules end in the INCONCLUSIVE catch-all; every
metric pointer in endpoints and verdict rules names a declared `output_fields`
entry of the pinned analysis script (constraint-2 discipline), including the
power-gate, fluency-guard, measured-discordance, and max-stat outputs; kill
criterion and envelope enter verbatim from §8; budget.usd_cap = 60 (no Tier-5
signoff); corpus pins under the current kot-corpus-hash recipe; no
scale-language fields are declared (the §8 envelope licenses none). The two
open-EXTRAPOLATION citations (ASM-1662, ASM-1706) trigger the freeze tool's
non-fatal PAUSE flag by design — guard conclusions, not experiments.

## 7. Cost and account

- **Estimate** [STIPULATED: ASM-1664]: T0+G0 ≈ $3; S1 ≈ $14–19; S2 ≈ $11–13;
  retries + 20% margin → ≈ **$40 total; hard ceiling $60**, alongside the
  free-tier credit the Modal workspaces carry. Inference-only, no gradients
  anywhere. Arithmetic: a full-suite pubeval pass on 135M is ~2.4 GPU-h at
  conservative batch-1, of which GSM8K generation is ~60–75%; with GSM8K
  filter-dropped (§5.1) a full-item MC cell is ≈0.6–1.0 GPU-h, roughly halved by
  batching — 30 full-item cells + 16 subset cells ≈ 12–17 GPU-h on 135M; 360M
  cells cost ≈1.6× (18 cells, full-item). Per-run worst-case is additionally
  capped by pubeval's own `--dry-plan` fail-closed $10/run check, which stacks
  under the campaign ceiling.
- **Account:** primary = the Modal workspace behind
  `~/.config/kot/modal2.env`; spillover for parallel eval shards =
  `modal3.env` / `modal4.env` (S2 on `modal3.env` keeps each workspace inside its
  free-credit band). `modal.env` currently lacks its token-secret line and must be
  repaired or skipped — verified at T0, never printed. House hygiene applies:
  batch same-image runs per account, `modal app stop` after every attached run,
  nohup+setsid, `reuse-check.py check --gate` before any paid launch. GPU class:
  A10G default; reuse the pinned f2b image (the same image pubeval targets) +
  pinned donor checkpoints (tier-1/2 reuse — corpora, images, checkpoints — which
  the standing reuse ruling permits; no logged-row consumption anywhere in this
  design).

## 8. Gates, go/no-go, and kill criteria (verbatim at freeze)

**Instrument gates (each with its own bound):**

- **I-1 rotation validity:** precondition — every constructed basis (including
  the assembled A2 basis of §2.3) passes max |QᵀQ − I| ≤ 1e-6. Then, for every
  rotated arm at r=d (no slicing), end-to-end logits over a pinned 64-sequence
  corpus must match the donor: median KL(donor‖rotated) ≤ 1e-5 and greedy top-1
  agreement = 100% [STIPULATED: ASM-1661]. Failure = surgery bug; nothing
  downstream runs.
- **I-2 mechanics sanity:** C1 at ρ=0.9 must retain ≥ 95% pooled-item accuracy —
  a gross-implementation tripwire, not a result.
- **I-3 corpus parity:** all five calibration corpora within ±10% total-token
  budget of K-static; hash pins verified.
- **I-4 licensing:** every primary-suite license re-verified at source at T0; any
  benchmark failing open-license verification is dropped from the filter set
  before freeze.
- **I-5 power (v3 — superiority AND equivalence legs on the JOINT contrast
  distribution; review REWORK fix 4 + re-review residual fix):** pubeval
  per-item emission landed and mock-validated; the T0 power SIMULATION of
  §5.2 [STIPULATED: ASM-1720], run on the measured filtered pool at the
  stipulated q_ref = 0.25, must show BOTH (i) superiority power ≥ 0.9 at true
  Δ_M1 = Δ_R1 = +3.0 on the min-statistic Δ* drawn from the JOINT per-item
  outcome model over (A1, M1, all three R1 seed columns) — both components at
  the boundary, power taken as the MINIMUM over the registered dependence
  grid c ∈ {0, 0.5, 1} (least-favourable covariance configuration gates;
  attaining c* disclosed) — AND (ii) TOST equivalence power ≥ 0.9 at true
  Δ = 0 (90% CI ⊂ (−3.0, +3.0); pairwise marginal of the joint model).
  Either leg failing blocks freeze and surfaces MD-6 — an underpowered
  campaign is never run silently; a superiority MDE is never accepted as
  evidence of equivalence power; and independent pairwise simulation legs are
  never accepted as evidence of min-statistic power.
- **I-6 second-moment sanity (review fix (b) tripwire):** the documented
  massive-activation direction's energy capture in the kept subspace is logged
  for every cell; capture < 0.99 in any cell does not block (the uncentred
  convention and identical cross-arm treatment prevent confounding) but flags
  the cell in the readout and arms MD-4.

**G0 routing rules (pre-registered):**

- If neither ridge-CCA nor Procrustes yields admitted directions (all four §2.3
  admission criteria, criterion 1 under the joint max-stat threshold across
  directions × layers × methods) in at least
  ⌈L/3⌉ layers, **A2 is dropped** and reported as killed-by-G0.
- If the kernel/C4 subspace overlap ≥ 0.9 at the working r for all layers, A1
  cannot mechanically differ from C1; the campaign still runs (the demonstrated
  null is cheap and informative) but the expected-tie flag is recorded at freeze
  and MD-2 is surfaced.
- FORK-1 and FORK-2 resolve mechanically inside G0 (§10); the template-variance
  and bag-of-primes diagnostics are recorded whatever they show.

**S1 → S2 promotion rule:** S2 runs iff the S1 primary claim holds (Δ* > 0 at
ρ=0.75, one-sided 95%) OR any Holm-surviving secondary Δ* > 0 exists at ρ ≥ 0.5
with fluency-guard perplexity inflation (ARC-Easy gold_ppl, §5.1) of A1 no worse
than 1.5× the better of M1/R1 at the same cell. Otherwise S2 does not run and the
ceiling is unspent.

**Kill criteria (verbatim):** "ddc1 is killed if (a) gate I-1 fails for any rotated
arm after one debugging iteration; or (b) at every full-item grid point ρ ≥ 0.5,
retention(A1) < retention(M1) and retention(A1) < mean-seed retention(R1) (kernel
guidance strictly worse than both controls where the surgery is
literature-viable); or (c) the A0 filtered task set is empty at T0 (donor too weak
for the instrument). A kill is reported at the same prominence as a pass."

**Extrapolation envelope (verbatim):** "Results bind only to: SmolLM2-135M and
-360M base checkpoints at the pinned revisions; training-free rotate-and-slice
surgery under the §2.5 scheme; the pinned corpora and the filtered
public-benchmark suite at the pinned poc/pubeval content hash (internal-relative
numbers, never leaderboard-comparable); keep-fractions in
{0.9, 0.75, 0.5, 0.3, 0.15}, registered claims from full-item cells only. Nothing
here extends to recovery-trained compression, to other donors or scales, to other
kernel states, or to deployment claims."

## 9. Maintainer decision points (each a tracked issue; ids live in beads)

- **MD-1 (launch / authorization)** — **`kernel-of-truth-ifvn`** (P1, flagged
  `human`; blocks MD-2..MD-6): approve the campaign + the $60 ceiling + the
  account allocation of §7, explicitly superseding the earlier resource-plan H-DD
  GPU-exclusion for this training-free tier. Per the standing no-re-surface rule,
  approval covers T0→S2 inclusive; nothing inside the ceiling comes back for
  permission.
- **MD-2 (conditional; only if G0 flags expected-tie)** — **`kernel-of-truth-vzk5`**:
  proceed-full vs proceed-reduced grid; expected-tie flag recorded at freeze
  either way.
- **MD-3 (conditional; post-readout, only on A2 geometry signal at 576)** —
  **`kernel-of-truth-dmi5`**: whether to commission the encoder version bump to
  new native dimensions (d=960 next) — an encoder content-hash version change
  with ALGORITHM_VERSION bump + X0 golden regeneration + Phase-X re-run, so
  maintainer-gated by definition.
- **MD-4 (conditional; post-readout, only if a headline cell's outcome plausibly
  hinges on super-weight / massive-activation handling — gate I-6 flags)** —
  **`kernel-of-truth-mlpj`**: authorize the protected-stratum re-run.
- **MD-5 (post-readout)** — **`kernel-of-truth-riws`**: whether the knull arm's
  authored store is adequate as the plain-dictionary control at this corpus size,
  or a matched-budget knull expansion should be authored before any
  kernel-specificity claim ships — connects to the open knull-fork maintainer
  thread.
- **MD-6 (conditional; only if gate I-5 v3 fails at T0)** — **`kernel-of-truth-j7mt`**:
  freeze is blocked; the maintainer picks (a) re-stipulate the SESOI upward to
  the smallest margin at which BOTH simulated power legs (superiority at
  Δ = SESOI on the joint min-statistic model at its least-favourable
  registered dependence, equivalence at Δ = 0) reach 0.9 on the measured pool
  (register row amended pre-freeze; every §11 equivalence wording weakens with it), or
  (b) wire one additional openly-licensed human-built benchmark into pubeval
  before freeze.

## 10. Registered forks (uncertainties an experiment decides, not prose)

- **FORK-1 — basis-selection rule for A2:** ridge-CCA vs orthogonal Procrustes.
  Why uncertain: n≈119 pairs in d=576 under-determines both; which survives the
  corrected null is an empirical fact. Decider: G0 (more layers with
  max-stat-admitted directions — all four §2.3 criteria — wins; tie →
  ridge-CCA, pre-declared; the method choice is itself inside the max-stat
  family, so the fork costs no uncorrected selection). Kill: neither admits in
  ⌈L/3⌉ layers → A2 dropped.
- **FORK-2 — pooling for h(c_i):** empty-carrier-subtracted, grand-mean-centred
  mean-pool (pinned v1) vs last-token-at-delimiter pooling. Why uncertain:
  template-artifact contamination is measured, not knowable a priori. Decider: G0
  template-variance diagnostic; the last-token variant runs in G0 at zero
  marginal cost. Kill: top-PC variance > 0.5 for both poolings → A2's h(c_i)
  construction reported as template-dominated.
- **FORK-3 — which magnitude control carries the task claim:** structured M1
  (pinned v1, same structural family) vs unstructured M2. Why uncertain:
  fairness-vs-familiarity trade. Decider: both run at ρ ∈ {0.75, 0.5}; the
  primary is pinned to M1 and M2 is reported alongside.
- **FORK-4 — allocation policy:** uniform (pinned v1) vs kernel-energy vs
  ID-profiled per-layer budgets. Why uncertain: the intrinsic-dimension
  literature says uniform over-cuts mid-layer abstraction phases [LIT-BACKED:
  arXiv:2405.15471, 2024]. Decider: a follow-up sweep only if S1 shows any
  Holm-surviving positive cell; not in v1's registered family.
- **FORK-5 — hybrid-as-target (GPT-5.6 construction):** engine closures entering
  the A2 *alignment target* as fixed signed-hash sketches (D_R = 2048,
  γ-normalised to equal mean squared norm), with shuffled-closure and
  stated-facts-only nulls — vs hybrid-as-corpus (pinned v1, A3). Why uncertain:
  whether closure structure is linearly visible in residual activations at all is
  exactly what G0-style statistics must decide first. Decider: runs only if A2
  survives G0 AND S1 shows a Holm-surviving positive cell; exploratory until then.
  Kill: fails its own shuffled-closure null → reported as
  features-not-closure-structure.

## 11. Pre-registered outcome map (wording fixed now; no conclusion drawn here)

| Observed pattern (after Holm, TOST where null) | Registered wording — no stronger |
|---|---|
| Δ* > 0 at ρ=0.75 AND A1 > C1, C2, C3 | "Training-free kernel-guided slicing preserved more public-benchmark capability than magnitude, random, generic-text, plain-dictionary, and scrambled controls at matched compression, on these two donors, at these keep-fractions. Kernel-specific calibration signal, training-free scope only." |
| Δ* > 0 but A1 ≈ C1 (TOST) | "Calibration-corpus-steered slicing beat magnitude/random controls; the kernel added nothing over a generic corpus at matched budget — a replication of published corpus-steering, carrying no kernel-specific value." |
| Δ* > 0, A1 > C1, but A1 ≈ C2 | "A small coherent *definitional* corpus steers slicing better than generic text, but NSM grounding specifically added nothing over plain-dictionary content." |
| A1 ≈ M1 ≈ R1 (TOST) across the viable grid | "No training-free kernel-guided advantage at 135M/360M scale under this surgery; small-donor slicing degradation dominates basis choice at these keep-fractions." |
| Δ* < 0 anywhere it is Holm-significant | Reported as a negative at full prominence: kernel calibration was strictly worse than the named control at the named cell. |
| Any A1 win whose cell breaches the fluency guard (ARC-Easy gold_ppl > 1.5× the better of M1/R1) | "The kernel arm's benchmark win is disclosed alongside its general-fluency damage; no clean-win wording is licensed for that cell." |
| A2 > A1 (native dim, G0-passed) | "First indication that kernel *geometry*, not merely kernel text, can guide the drop — scoped to d=576 and to this alignment construction; the encoder-dimension decision (MD-3) becomes live." |
| A3 ≠ A1 (either direction) | Attributed to calibration-corpus content (engine closures) only — never to symbolic machinery inside the weights (§2.4). |
| Gate I-1 unfixable / filter set empty / Δ* worse than both controls at every full-item ρ ≥ 0.5 | The verbatim kill of §8 fires; the kill is reported at the same prominence as a pass. |

## 12. Design self-check gate (run before hand-off; all six pass)

1. **Tag mechanics:** every load-bearing line carries exactly one inline tag with
   a lint-shaped backing; marker lines (PREMISE/DECISION) appear only where
   intended, as single logical lines.
2. **Choices are STIPULATED, not MEASURED:** every design choice cites an ASM-id
   from the claimed 1650..1679 / 1700..1719 / 1720..1729 blocks (superseded ids
   1652/1656/1663/1668 appear only as history in Appendix A; superseded id 1704
   appears only as history in Appendix A.1); no measurement is
   quoted outside its scope
   (the MEASURED citations — rules-1, knull pins, the F2 verdict lesson — restate
   registry records within scope; SmolLM2 config values are additionally
   re-pinned at T0).
3. **ASM registration with commit:** Appendix A carries the ready-to-append
   register rows; the coordinator lands doc + rows in one commit (renumbering
   together if 1650+ is consumed by a concurrent wave), so claims-check passes on
   push.
4. **No account-identifying strings:** accounts are referenced only by env-file
   basename; no handles, no vendor account names, no tokens anywhere.
5. **Instrument honesty:** the evaluator is pinned to `poc/pubeval` by content
   hash; its numbers are declared internal-relative; the two mechanical harness
   gaps (per-item emission, BASE registry entries) are disclosed in §5.1 and
   gated (I-5) rather than assumed away; the fluency guard survives the
   WikiText-2 → ARC-Easy-gold_ppl substitution with its purpose intact.
6. **Self-check present and honest:** no feasibility conclusion appears anywhere
   in this document; the outcome map (§11) is exhaustive over sign patterns
   including guard-breach and kill rows; both EXTRAPOLATION entries are
   load_bearing:false with resolution paths that G0 itself executes.

---

## Appendix A — PROPOSED-ASM-1650..1679 (emitted for central registration)

Rows for `registry/assumptions.jsonl`, owner pseudonym `designer-3`, all
`status:"open"`; ids final on coordinator registration (block renumbered from the
workflow draft's 1470 claim; 1650..1679 verified collision-free at finalisation):

> **REWORK amendment (2026-07-12, post-review):** rows **ASM-1652, ASM-1656,
> ASM-1663 and ASM-1668** below are SUPERSEDED by the Appendix A.1 successor
> rows (PROPOSED-ASM-1700..1706) under the register's append-only
> supersede-by-citation convention; the superseded lines stand as append-only
> history in the central register (they were registered before this revision)
> and are no longer cited as live premises anywhere in this document. The A.1
> rows are EMITTED HERE ONLY — the coordinator appends them centrally; this
> revision writes nothing to `registry/assumptions.jsonl`.

```jsonl
{"id":"ASM-1650","claim":"PDC (SliceGPT-scaffold rotate-and-slice) is the sole surgical method for ddc0/ddc1; PAP survives only as the Procrustes variant of the A2 basis fork; the convergent GPT-5.6 low-rank-factorisation scaffold is not adopted (its attribution controls are discharged in-family: C1 = kernel-agnostic spectral control)","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md sections 1.1 + 1.3","load_bearing":true,"status":"open","owner":"designer-3","rationale":"best-defined proposal; literature-proven surgery; critique defects all fixable pre-freeze; one surgery family keeps every arm an exact structural twin"}
{"id":"ASM-1651","claim":"Calibration corpora: N=4096 sequences, <=256 tokens, seed 0, renderExplication over 65 primes + 54 kernel-v0 explications + molecules-v0 with generateExplication span expansion; all arms' corpora token-matched within +/-10%","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 2.2","load_bearing":true,"status":"open","owner":"designer-3","rationale":"deterministic, hash-pinnable, spans the depth x clause grid; size chosen to keep one-GPU calibration passes in minutes"}
{"id":"ASM-1652","claim":"A2 alignment and basis assembly: carrier-controlled probes (P=4 fixed carriers x >=2 seeded renders, empty-carrier subtraction, grand-mean centring, mean-pool v1); ridge-CCA (leave-one-concept-out lambda) and orthogonal Procrustes each vs a 1000-draw permutation null on concept-split partitions; admitted aligned directions ordered by null-beating strength and QR-orthonormalised, A1 top-up projected onto their orthogonal complement and re-orthonormalised in energy order; final basis passes max|QtQ-I|<=1e-6 as an I-1 precondition","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 2.3","load_bearing":true,"status":"open","owner":"designer-3","rationale":"fixes the critique's CCA ill-posedness and template-artifact defects AND the review's orthonormality defect: a concatenated non-orthonormal basis breaks RMSNorm commutation and makes slicing a non-orthogonal projection"}
{"id":"ASM-1653","claim":"Surgery scheme: RMSNorm gain fusing first; per-block Q_l with explicit residual bridges; tied embedding sliced once in Q_1 with a single r x r bridge before the unembedding read; RoPE head dims and MLP inner dims untouched; fp32 throughout; donors = SmolLM2-135M/360M BASE checkpoints pinned at T0","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 2.5","load_bearing":true,"status":"open","owner":"designer-3","rationale":"stays inside the invariance group SURG.md derives from primary sources; tied-embedding handling is the one novel construction and is verified end-to-end by gate I-1 rather than assumed"}
{"id":"ASM-1654","claim":"Sweep rho in {0.9,0.75,0.5,0.3,0.15}, uniform allocation in v1; primary grid point rho=0.75; arm x grid coverage per section 3","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md sections 3-4","load_bearing":true,"status":"open","owner":"designer-3","rationale":"rho=0.75 is the only literature-anchored viable point for small-donor slicing; the tail is kept because the curve is the deliverable and tail cells are cheap subset-scored"}
{"id":"ASM-1655","claim":"The evaluator for every ddc cell is poc/pubeval, content-hash-pinned at T0 (runner+benchmarks+transforms+fetch+modal wrapper+data manifest), on the pinned f2b Modal image (sha 0fac7243 lineage); benchmark set = folio, arc_easy, arc_challenge, gsm8k (human gold, licenses re-verified at T0); 5-shot fixed exemplars seed 20260712, acc_norm/EM headlines, internal-relative numbers only; informative-task filter = donor >= chance+10pts at T0; two T0 mechanical harness additions (per-item emission; BASE donor registry entries) re-pinned and mock-validated before freeze; lm-eval-harness explicitly not used (image-reuse discipline)","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 5.1; poc/pubeval/README.md","load_bearing":true,"status":"open","owner":"designer-3","rationale":"third-party human gold scored by one pinned in-house harness whose transform hook makes cross-arm deltas attributable to the weight change alone"}
{"id":"ASM-1656","claim":"Exactly one primary endpoint: Delta* = min(paired pooled-item retention delta of A1 vs M1, vs R1 mean-seed) at rho=0.75 on 135M, one-sided 95% task-stratified paired bootstrap (1e4); Holm secondary family per section 5.2 restricted to full-item cells (rho in {0.9,0.75,0.5}); tail cells subset-scored (500 det_u items/task) and claim-ineligible; TOST margin +/-3.0 pooled points; power arithmetic re-run mechanically at T0 and gated (I-5: MDE <= margin, else freeze blocks -> MD-6)","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 5.2","load_bearing":true,"status":"open","owner":"designer-3","rationale":"absolute paired-difference primary avoids the F2 degenerate-ratio failure; min-of-two encodes beat-BOTH-controls in one number; pooled-item primary prevents a 203-item task dominating macro noise; the margin is sized to what the pinned instrument can actually resolve"}
{"id":"ASM-1657","claim":"Matched compression = matched retained parameter count; M1's r raised to cover rotated arms' bridge overhead; M2 masked to identical count; bytes (dense and sparse-CSR) and bridge FLOPs reported per cell; no width fraction quoted as size","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 4 + appendix B","load_bearing":true,"status":"open","owner":"designer-3","rationale":"the H-DD correction-3 discipline: size claims are measured artifacts, never inferred from width"}
{"id":"ASM-1658","claim":"Super weights: documented per donor pre-slice (data-free census at T0); v1 treats them identically across all arms (unprotected); per-cell energy-capture of the documented massive-activation direction logged, capture < 0.99 flags the cell (gate I-6) and arms MD-4; protected-stratum re-run is maintainer-gated follow-up","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md sections 2.5 + 8","load_bearing":true,"status":"open","owner":"designer-3","rationale":"identical handling cannot confound cross-arm comparisons; the tripwire makes silent super-weight deletion impossible rather than assumed-absent"}
{"id":"ASM-1659","claim":"The hybrid rules-kernel enters as calibration corpus (rendered axioms + engine closures) and secondary engine-gold evals ONLY; no rule enters the projection algebra; all A3 claims worded as corpus-and-eval effects; the GPT-5.6 hybrid-as-alignment-target construction is FORK-5, exploratory, contingent on A2 surviving G0","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md sections 2.4 + 10","load_bearing":true,"status":"open","owner":"designer-3","rationale":"the engine is a symbolic fixpoint reasoner, not a vector; honesty about what the hybrid arm can and cannot attribute"}
{"id":"ASM-1660","claim":"The knull control corpus is the rendered plain-dictionary authored store pinned by the knull experiment (poc/knull/inputs/plain-authored.json), token-band matched","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 3","load_bearing":true,"status":"open","owner":"designer-3","rationale":"reuses the programme's audited plain-dictionary asset at matched budget instead of authoring an unvetted new control; adequacy at this corpus size is MD-5"}
{"id":"ASM-1661","claim":"Rotation-validity gate: every constructed basis passes max|QtQ-I| <= 1e-6; the r=d rotated model must match donor logits (median KL <= 1e-5, greedy top-1 agreement 100%) on a pinned 64-sequence corpus before any slicing","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 8","load_bearing":true,"status":"open","owner":"designer-3","rationale":"SURG's validation standard: end-to-end logits over a pinned corpus, not per-matrix checks; the orthonormality precondition makes the fix-(a) failure mode mechanically impossible"}
{"id":"ASM-1662","claim":"The kernel-corpus activation subspace differs materially from the generic-corpus subspace at working r on these donors","tag":"EXTRAPOLATION","backing_ref":"docs/next/design/DDC.md section 8 (G0)","load_bearing":false,"status":"open","owner":"designer-3","resolution_path":"G0 measures principal angles and subspace overlap directly; overlap >= 0.9 routes to MD-2 with the expected-tie flag"}
{"id":"ASM-1663","claim":"Kernel geometry is transportable into model space by ridge-CCA/Procrustes at n~119 pairs, d=576","tag":"EXTRAPOLATION","backing_ref":"docs/next/design/DDC.md section 2.3","load_bearing":false,"status":"open","owner":"designer-3","resolution_path":"G0 permutation-null + admission-criteria test; failure in > 2L/3 layers kills A2 before surgery"}
{"id":"ASM-1664","claim":"Cost band ~$40, hard ceiling $60; A10G-class; primary workspace = modal2.env, spillover modal3.env/modal4.env; modal.env repaired or skipped at T0; per-run worst-case additionally capped by pubeval --dry-plan ($10/run fail-closed)","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 7","load_bearing":true,"status":"open","owner":"designer-3","rationale":"inference-only campaign sized from measured pubeval cell costs (GSM8K filter-drop disclosed) and cell-tier discipline; per-workspace free-credit bands respected"}
{"id":"ASM-1665","claim":"All activation-PCA bases use the UNCENTRED second moment (1/N)XtX, energy-ordered, identically in every PCA-based arm (A1/A3/C1/C2/C3) and in the A2 top-up; centring is confined to A2 alignment statistics and never produces a surgical basis","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 2.2","load_bearing":true,"status":"open","owner":"designer-3","rationale":"review fix (b): the massive-activation (super-weight) direction is near-constant and high-magnitude, so its CENTRED variance can be negligible - a centred basis would silently slice it and destroy every arm for reasons unrelated to basis choice; uncentred energy ranking retains it on its own mass, and gate I-6 verifies per cell"}
{"id":"ASM-1666","claim":"The out-of-kernel fluency guard is gold-continuation perplexity on ARC-Easy (pubeval gold_ppl), reported for every cell, outside every accuracy aggregate, and used by the S1->S2 promotion rule (A1 inflation <= 1.5x the better of M1/R1); WikiText-2 is not wired into the pinned harness and is not added","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md sections 5.1 + 8","load_bearing":true,"status":"open","owner":"designer-3","rationale":"preserves the critique's mandatory fix 2 (domain-overfit collapse detection) inside the pinned instrument instead of importing a new dependency tree"}
{"id":"ASM-1667","claim":"Training-free means: no learned neural parameters, no optimizer, no loss-minimisation loop, no labelled-task adaptation; frozen-model forward passes and closed-form calibration algebra (covariance/eigen/SVD/CCA/Procrustes/least-squares) are permitted","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 1.3","load_bearing":true,"status":"open","owner":"designer-3","rationale":"the GPT-5.6 convergent proposal's terminology point adopted verbatim in substance: reviewers may call closed-form calibration 'fitting'; the definition is fixed so the claim scope cannot drift"}
{"id":"ASM-1668","claim":"A2 aligned-direction admission requires all four criteria: held-out canonical correlation above the 95th-percentile permutation null; carrier-half stability (principal-angle cosine >= 0.8); survival on the minimal-contrast probe subset; superiority over the bag-of-primes structure-destroyed kernel null (else admitted as lexical and flagged); cap k <= min(d/2, 256) per layer","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 2.3","load_bearing":true,"status":"open","owner":"designer-3","rationale":"folded from the convergent GPT-5.6 proposal: prevents renaming arbitrary or merely lexical directions as kernel-aligned, and prevents the protected set consuming the whole rank budget"}
```

(ASM block 1669..1679 reserved unassigned within the claimed block for freeze-time
amendments — e.g. an MD-6(a) SESOI re-stipulation; never reused elsewhere.)

## Appendix A.1 — PROPOSED-ASM-1700..1706 (REWORK-revision rows; emitted for central registration)

Successors + new rows applying the cross-vendor review's mandated fixes 2/3/4;
owner pseudonym `designer-3`, all `status:"open"`; 1700..1719 verified
collision-free against the central register (tail ASM-1691) at revision time;
1707..1719 remain reserved unassigned (the re-review residual fix claimed the
1720..1729 block instead — Appendix A.2):

```jsonl
{"id":"ASM-1700","claim":"SUCCESSOR of ASM-1652 (supersede-by-citation; the ASM-1652 line stands as append-only history and is no longer cited by the DDC design). A2 probe + alignment + basis assembly, fully specified: carrier-controlled probes (P=4 carriers x >=2 seeded renders, empty-carrier subtraction, grand-mean centring, mean-pool v1); concept splits FIT/SEL/TEST = 60/20/20 by concept, seed 0, stratified by record class, one partition serving all layers, both methods, and every permutation replicate; ridge-CCA as the regularised eigenproblem (S_hh+lambda I)^-1 S_hv (S_vv+lambda I)^-1 S_hv^T a = rho^2 a with one lambda on both blocks, grid {1e-4,1e-3,1e-2,1e-1,1} x tr(S_hh)/d, leave-one-concept-out reconstruction selection (loadings-based rank-full predictor), ties to the larger lambda; Procrustes directions extracted as the SVD pairs (u_j, w_j, sigma_j) of the FIT cross-covariance M = H_F^T V_F (the map R*=UW^T itself is never tested; sigma orders candidates only); J = min(64, n_F-1) candidates per layer per method with deterministic sign/ordering tie-breaks; direction score = signed one-sided TEST-partition Pearson correlation of (H u, V w); basis assembly by null-beating-strength-ordered QR (score minus shared max-stat threshold t*, ties to lower layer then lower index) with complement-projected A1 top-up; top-up pool = the FULL d-vector uncentred eigenbasis, and floating-point deficiency (fewer than r_l columns after pool exhaustion) raises ERR_DDC_BASIS_DEFICIENT - the A2 cell fails closed as a basis-construction failure, never silently padded and never relabelled A1","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 2.3","load_bearing":true,"status":"open","owner":"designer-3","rationale":"review REWORK fix 2: the alignment was named but not defined; every matrix, grid, split, score, tie-break, and the fewer-than-r top-up path is now exact enough to implement, permute, and freeze"}
{"id":"ASM-1701","claim":"A2 admission significance is controlled by a single Westfall-Young max-stat permutation family across directions x layers x method-selection (ridge-CCA vs Procrustes; plus the FORK-2 pooling variant if routed): B=1000 seeded global concept-to-vector permutations (seed 1; partition membership fixed on the model side), the FULL pipeline re-run per replicate (per-layer LOO lambda re-selection included), T_b = max over all candidates of the TEST score; admission p = (1+#{T_b >= s})/(B+1) <= 0.05; no uncorrected per-direction null appears anywhere in admission; FORK-1 resolves on corrected admissions (more layers with admitted directions wins; tie -> ridge-CCA)","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 2.3","load_bearing":true,"status":"open","owner":"designer-3","rationale":"review REWORK fix 3: Procrustes supplies an alignment map, not inherently ranked directions, and the selections actually made (direction, layer, method, pooling) must be corrected jointly - the max statistic controls FWER over exactly that family"}
{"id":"ASM-1702","claim":"SUCCESSOR of ASM-1668 (supersede-by-citation; the ASM-1668 line stands as append-only history and is no longer cited by the DDC design). A2 aligned-direction admission requires all four criteria: (1) TEST score significant under the joint max-stat permutation family of ASM-1701 (p <= 0.05), never a per-direction 95th percentile; (2) carrier-half stability |cos| >= 0.8 between the two fixed carrier-half refits, halves matched by kernel-side cosine; (3) minimal-contrast survival: positive signed correlation on the SEL-housed minimal-contrast stratum with per-stratum permutation p <= 0.05; (4) bag-of-primes superiority: seeded paired bootstrap (1e3 resamples over TEST concepts) 90% CI of s - s_bag excludes 0, else admitted only as lexical and flagged; criteria 2-4 are conjunctive filters (they can only remove candidates), so criterion 1 alone carries the FWER control; cap k <= min(d/2, 256) per layer","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 2.3","load_bearing":true,"status":"open","owner":"designer-3","rationale":"folds the GPT-5.6 admission machinery under the corrected null: prevents renaming arbitrary or merely lexical directions as kernel-aligned and prevents the protected set consuming the rank budget"}
{"id":"ASM-1703","claim":"SUCCESSOR of ASM-1656 (supersede-by-citation; the ASM-1656 line stands as append-only history and is no longer cited by the DDC design). Exactly one primary endpoint: Delta* = min(paired pooled-item retention delta of A1 vs M1, vs R1 mean-seed) at rho=0.75 on 135M, one-sided 95% task-stratified paired bootstrap (1e4); Holm secondary family per section 5.2 restricted to full-item cells (rho in {0.9,0.75,0.5}); tail cells subset-scored (500 det_u items/task) and claim-ineligible; SESOI = +/-3.0 pooled accuracy points, declared as the ddc1 primary endpoint's smallest_effect_of_interest; TOST = two one-sided task-stratified paired bootstrap tests at alpha=0.05 each, equivalently equivalence iff the 90% percentile-bootstrap CI lies inside (-3.0,+3.0), full-item cells and pre-listed contrasts only; a wide-CI non-result reads out INCONCLUSIVE-underpowered, never as equivalence","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 5.2","load_bearing":true,"status":"open","owner":"designer-3","rationale":"review REWORK fix 4 (definition side): the +/-3.0 margin survives from the draft but equivalence is now a real TOST decision rule with a declared SESOI carried on the frozen primary endpoint, not an afterthought on a superiority MDE"}
{"id":"ASM-1704","claim":"Gate I-5 v2: at T0 a pre-registered seeded power SIMULATION (2e3 simulated campaigns per scenario cell, each analysed by the exact registered bootstrap pipeline; discordance-split data-generating model Delta = q(2theta-1) at measured per-task item counts and A0 accuracies; grid q in {0.10,0.15,0.20,0.25,0.30} x Delta in {0,+3.0}, full grid disclosed; gate evaluated at stipulated reference discordance q_ref=0.25; measured per-contrast discordance recomputed in-flight, claims with q > q_ref flagged with achieved power) must show BOTH superiority power >= 0.9 at true Delta* = +3.0 (min-statistic, both components at the boundary) AND TOST equivalence power >= 0.9 at true Delta = 0 (90% CI inside (-3.0,+3.0)); either leg failing blocks freeze and surfaces MD-6; a superiority MDE is never accepted as evidence of equivalence power","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md sections 5.2 + 8","load_bearing":true,"status":"open","owner":"designer-3","rationale":"review REWORK fix 4 (power side): the two one-sided tests at Delta=0 need margin/SE >= 3.29 vs the superiority 2.93; the draft's MDE gate demonstrably under-powered TOST - an ARC-Easy-only filter outcome passes MDE <= 3.0 marginally at q=0.25 while margin/SE ~ 2.93 leaves equivalence unpowered, and now blocks freeze instead"}
{"id":"ASM-1705","claim":"Freeze-shape obligations for the ddc records: ddc0 primary endpoint = n_layers_admitted (winning method, all four admission criteria) with primary claim n_layers_admitted >= ceil(L/3), mandatory baselines = permutation-null/bag-of-primes/C4-subspace comparisons, no NULL row (no SESOI required), INCONCLUSIVE catch-all last; ddc1 primary endpoint = Delta* at rho=0.75/135M carrying smallest_effect_of_interest = 3.0 pooled points, INCONCLUSIVE catch-all last, every endpoint/verdict-rule metric pointer a declared analysis-script output field (incl. power-gate, fluency-guard, measured-discordance, and max-stat outputs), kill + envelope verbatim from section 8, budget usd_cap = 60, corpus pins under the current kot-corpus-hash recipe, no scale-language fields declared","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md section 6","load_bearing":true,"status":"open","owner":"designer-3","rationale":"restates the prereg-freeze fail-closed constraints as design obligations so both records pass --dry-run mechanically on first drafting; the open-EXTRAPOLATION citations (ASM-1662, ASM-1706) trigger only the non-fatal PAUSE flag by design"}
{"id":"ASM-1706","claim":"SUCCESSOR of ASM-1663 (supersede-by-citation; the ASM-1663 line stands as append-only history and is no longer cited by the DDC design). Kernel geometry is transportable into model space by ridge-CCA/Procrustes at n~119 pairs, d=576","tag":"EXTRAPOLATION","backing_ref":"docs/next/design/DDC.md section 2.3","load_bearing":false,"status":"open","owner":"designer-3","resolution_path":"G0 joint max-stat permutation family + all-four admission criteria; fewer than ceil(L/3) layers with admitted directions for both methods kills A2 before surgery"}
```

## Appendix A.2 — PROPOSED-ASM-1720 (re-review residual-fix row; emitted for central registration)

Successor row applying the re-review's one residual fix (SHIP-WITH-FIXES,
`poc/gpt56-review/ddc-rereview/`); owner pseudonym `designer-3`, `status:"open"`;
block 1720..1729 verified collision-free against the central register (tail
ASM-1691) at revision time; 1721..1729 reserved unassigned for freeze-time
amendments. Row **ASM-1704** above is SUPERSEDED by this row under the register's
append-only supersede-by-citation convention and is no longer cited as a live
premise anywhere in this document; this revision writes nothing to
`registry/assumptions.jsonl` — the coordinator appends centrally:

```jsonl
{"id":"ASM-1720","claim":"SUCCESSOR of ASM-1704 (supersede-by-citation; the ASM-1704 line stands as append-only history and is no longer cited by the DDC design). Gate I-5 v3 - power simulation on the JOINT contrast distribution: at T0 a pre-registered seeded power SIMULATION (script poc/ddc/power_sim_ddc1.py pinned in the ddc1 record; 2e3 simulated campaigns per scenario cell, each analysed by the exact registered bootstrap pipeline) draws per-item outcomes for A1, M1, and all three R1 seed columns JOINTLY: X_A1 ~ Bernoulli(p_t) at measured per-task item counts and A0 accuracies; each control column C flips relative to A1 with conditional probabilities a_C=(q+Delta_C)/(2 p_t) given X_A1=1 and b_C=(q-Delta_C)/(2(1-p_t)) given X_A1=0, exactly reproducing the pairwise marginals (discordance q, true paired delta Delta_C=q(2theta_C-1)); scenario cells with (a_C,b_C) outside [0,1] at any measured p_t are reported INFEASIBLE-AT-MEASURED-p and excluded with disclosure, never clamped; the four flip indicators per item are coupled by a Gaussian copula with equicorrelation c in {0,0.5,1} (c=0 = conditional independence given the shared A1 outcome, the shared-A1 correlation floor; c=1 = comonotone flipping); Delta* = min of the two correlated contrasts (A1-M1 and A1-mean-of-3-R1-seeds) computed from these JOINT draws, never from independently simulated pairwise legs; grid q in {0.10,0.15,0.20,0.25,0.30} x Delta in {0,+3.0} x c in {0,0.5,1}, full grid disclosed; gate evaluated at stipulated reference discordance q_ref=0.25 with both component deltas at the +3.0 boundary, superiority power taken as the MINIMUM over the c grid (least-favourable registered dependence configuration gates; attaining c* disclosed); TOST equivalence leg at true Delta=0 is the pairwise marginal of the joint model (c does not enter a single contrast); measured per-contrast discordance recomputed in-flight, claims with q > q_ref flagged with achieved power; BOTH superiority power >= 0.9 AND equivalence power >= 0.9 required; either leg failing blocks freeze and surfaces MD-6; closed-form pairwise anchors are reported, disclosed as upper bounds on the min-statistic leg, and never gate","tag":"STIPULATED","backing_ref":"docs/next/design/DDC.md sections 5.2 + 8","load_bearing":true,"status":"open","owner":"designer-3","rationale":"re-review residual (SHIP-WITH-FIXES): the v2 simulation specified pairwise outcomes while the primary Delta* is the minimum of two contrasts sharing the A1 outcomes with R1 entering as a mean over seeds - correlated by construction; independent pairwise legs misstate min-statistic power (for two boundary-mean contrasts E[min] = Delta - sigma*sqrt((1-rho)/pi) falls as their correlation falls), so the joint model with a fully-swept dependence grid and a least-favourable gate makes the pre-registered power honest instead of optimistic"}
```

## Appendix B — bytes parameterisation (which matrices shrink how)

Per donor, with d → r = ρd, V = vocab, L = layers, d_ff = MLP inner, d_kv = KV
width; exact counts computed and logged by the harness at T0 (gate I-3 artifact),
and cross-checked at eval time against pubeval's recorded before/after parameter
counts and weight fingerprints (§5.1):

| Component | Shape (donor) | Sliced shape | Scaling |
|---|---|---|---|
| tied embedding (input + unembedding read) | V × d | V × r | linear in ρ |
| W_q, W_o per block | d × d | d(head) × r / r × d(head) sides — only the d_model side shrinks | linear in ρ |
| W_k, W_v per block | d_kv × d | d_kv × r | linear in ρ |
| W_up, W_gate, W_down per block | d_ff × d / d × d_ff | d_ff × r / r × d_ff | linear in ρ |
| residual bridges (rotated arms only) | — | L × (r × r), + 1 unembedding-side bridge | quadratic in r; counted |
| RMSNorm scale vectors | d | fused pre-surgery | removed by gain fusing |
| M1/M2 | same component set | M1: coordinate slice at r′ ≥ r (no bridges); M2: dense shape, masked | matched by total count |

Every per-cell size claim in the readout is the measured safetensors byte count of
the packed artifact (fp32; M2 also sparse-CSR), with parameter counts alongside —
never a width fraction.
