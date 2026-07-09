# N1-S — The kernel-introduction SCHEDULE axis (literature assessment + experiment family)

**Kernel of Truth programme — next-direction node N1-S (extends N1-A
`docs/next/architecture-ladder.md`, specifically the L2c semantic-fixedness sweep §4.3).**
Author: Kern (Fable design agent). Date: 2026-07-09.
Status: **DESIGN/PLANNING document. Nothing here is pre-registered; nothing here spends
GPU money.** Binding constraints: `docs/kernel-design-directives.md` (§1, §2, §4, §6).

**Epistemic-tag discipline (binding on this document, maintainer 2026-07-08).** Every
load-bearing claim carries one of: **MEASURED** (cites a verdict/experiment id or the S0
pilot below), **LIT-BACKED** (cites the paper; `[search]` = live web verification
2026-07-09, `[memory]` = model recall not re-verified, untagged = carried from the repo's
verified reports), **STIPULATED** (explicit assumption), **NOVEL-EXTRAPOLATION** (flagged;
never used as a premise for a decision — registered as a fork to test).
Worked correction that motivates the discipline: m0b coverage is **MEASURED at 0.3542 on
the molecules-v0 rung of one kernel-v0 instance against one corpus** (per-rung secondary:
kernel-v0 0.2210, wn31-aligned 0.7841; `registry/verdicts/m0b.json`, audit CONFIRMED),
and per its own extrapolation envelope it **extrapolates to no other corpus or rung** —
it is not "the kernel's natural coverage" and is never used as such below.

**Standing context (MEASURED, new since N1-A).** The F2 verifier-offload pivot returned
**FAIL** (`registry/verdicts/f2.json`, computed 2026-07-09; primary
gap-closed-fraction fired the pre-declared kill; secondaries: the kernel-verifier arm
did beat the text null and the gloss-self-verify arm, but cascade dominance and the
external slice failed). Per N1-A §6.2 this weakens — it does not touch — the
instrument-first justification of L2c-lite; consequences for gating are drawn in §5.

---

## 0. What the maintainer proposed (restated, hedged as received)

Three mechanisms for introducing the kernel **gradually or after the fact**, rather than
pinning it from training step 0 (which is the only design point L2c currently sweeps):

- **(a) Post-hoc cut-out / re-projection.** Train (or take) a model WITHOUT the kernel.
  Identify where kernel concepts (densely) occupy the learned representation space.
  Rotate/re-project that subspace so the concepts occupy designated coordinates; then
  **delete** those coordinates and/or **fix** them to the kernel's canonical values.
- **(b) Periodic normalisation.** Between runs, at run end, or every N steps during a
  run, apply a normalisation step that restores the kernel-given relations among all
  covered concepts (the model's concept geometry is repeatedly "snapped back" to the
  kernel's relational structure).
- **(c) The when-axis.** An experiment family varying WHEN in the training cycle fixing
  vs normalisation is introduced (start / mid / end / post-hoc / periodic).

The maintainer explicitly asked for an honest literature assessment before any of this
becomes an experiment. That assessment is §§1–2; the S0 pilot (§3) is the one on-box
$0 measurement this turn could contribute; the experiment family (§§4–5) covers only
the sufficiently-backed parts, with the novel parts registered as forks (§6).

---

## 1. Mechanism decomposition and the per-mechanism backing table

Mechanism (a) is a **pipeline of four distinct operations**, each with its own prior-art
status — assessing it as one unit would smuggle the weakest step in under the strongest.

| # | Mechanism / step | Closest prior art | Backing tag | What is known | What is NOT known |
|---|---|---|---|---|---|
| A1 | *Identify* where kernel concepts live in a learned space | Linear probing/CAVs; concept-subspace identification as used by INLP (Ravfogel et al. 2020, arXiv:2004.07667 **[memory]**) and LEACE (Belrose et al., NeurIPS 2023, arXiv:2306.03819 **[search]**); SAE feature dictionaries (repo L3 §5) | **LIT-BACKED** (operation exists) with a **known adverse finding** | Linear concept information is reliably locatable enough to *erase* it (LEACE is closed-form and provably complete against linear probes) **[search]** | Whether kernel concepts occupy a *compact, dense* region at all: superposition says concept features are distributed many-per-dimension (arXiv:2209.10652, carried); SAE dictionaries are seed-unstable and non-canonical (arXiv:2501.16615, arXiv:2502.04878, carried). "Densely occupy" is a **STIPULATED premise, measured not assumed** in S1 |
| A2 | *Re-project/rotate* so concepts occupy designated dims | Concept Whitening (Chen, Bei & Rudin, Nature MI 2020, arXiv:2002.01650 **[search]**: whitening + rotation aligns latent axes with predefined concepts); interpretable-basis rotations of embedding spaces (arXiv:2404.02619 **[search]**; EFA-family rotations **[search]**); orthogonal Procrustes alignment across embedding spaces (bounds: arXiv:2510.13406 **[search]**; high-dim non-identifiability: arXiv:2008.04631 / Psychometrika 2022 **[search]**); model stitching (Lenc & Vedaldi 2015 **[memory]**; Bansal, Nakkiran & Barak, NeurIPS 2021 **[search]**; linear-feature transfer across LMs, arXiv:2506.06609 **[search]**); relative representations (Moschella et al., ICLR 2023 **[search]**); Platonic representation hypothesis (Huh et al., ICML 2024, arXiv:2405.07987 **[search]**) | **PARTIALLY-BACKED** | Rotating a learned space so *learned* concept directions become axes is established (CW at CNN scale; EFA rotations for embeddings). Aligning two *learned* spaces with one affine/orthogonal map works remarkably often (stitching, Platonic convergence) **[search]** | Every published alignment is **learned-space ↔ learned-space**. Learned ↔ *constructed deterministic* space (the kernel) is an empty cell — exactly E8's untested bet (repo L3 §5 verdict). Also the alignability *metric* is treacherous: see S0 (§3, MEASURED) — naive Procrustes fit is high under the null |
| A3 | *Delete* the identified subspace | INLP (iterative nullspace projection) **[memory]**; LEACE (minimal-change closed-form erasure + concept scrubbing every layer) **[search]** | **LIT-BACKED** | Linear erasure with minimal collateral change is solved in closed form; damage is measurable | Erasure is *removal of information*, not *removal of capacity usage*; behavioural damage of erasing a **65–10³-concept** panel at once (vs one attribute like gender) is unmeasured anywhere |
| A4 | *Fix* the cut-out dims to kernel values (and continue training/serving) | Affine steering that matches target mean/covariance ("representation surgery"-class optimal affine steering, Singh et al. 2024 **[memory]**; conceptor-based affine steering, OpenReview 9wjGUN65tY **[search]**); locate-and-edit weight writing ROME/MEMIT (arXiv:2202.05262, arXiv:2210.07229 **[memory]**, carried in repo) | **NOVEL-EXTRAPOLATION** (the composite delete-then-pin-to-external-canonical-values step has no published instance we could find) | Steering *adds/shifts* directions transiently and works when targets are geometrically separable (survey arXiv:2502.17601 **[search]**); editing *writes* fixed associations into weights | The measured editing record is adverse: edits are less local than believed, ripple-effect accuracy <50% across methods (TACL 2024, tacl_a_00644 **[search]**; arXiv:2407.12828 **[search]**), sequential edits cause gradual-then-catastrophic forgetting (arXiv:2401.07453 **[search]**), robustness collapses under rephrasing (arXiv:2410.09338 **[search]**). And the repo's own frozen-vector chain (fixed-vectors-in-llms.md, carried): early layers re-encode whatever they are given; semantic initialisation washes out |
| B | *Periodic normalisation* to kernel-given relations | **Concept Whitening's alternating optimisation is the closest published mechanism**: main-objective training alternates with periodic updates of a whitening+rotation module that keeps concept axes aligned (Nature MI 2020 **[search]**). Soft variant: representation-matching distillation to a **frozen** target (feature/embedding-matching KD, survey arXiv:2308.04268 **[search]**; teacher-aligned embedding distillation LEAF, arXiv:2509.12539 **[search]**). Hard variant: projection onto a constraint set during optimisation (projected/proximal methods, standard **[memory]**; hard-constraint enforcement in PINNs, OpenReview u3dX2CEIZb **[search]**) | **PARTIALLY-BACKED** (mechanism class exists; our constraint set is novel) | Alternating "train ↔ re-align a concept module" is real at CNN scale and did not destroy accuracy there **[search]**; distilling toward a fixed representation target is routine when the target is a *trained teacher* | CW aligns axes to *activation patterns of concept examples* (the model's own statistics), NOT to an externally fixed Gram matrix; nobody has periodically snapped an LM's concept geometry to a *designed* relational structure. The standing risk anchor transfers: a fixed semantic space as a persistent training target carried a scaling penalty in the one lineage that measured it (LCM/SONAR-LLM → CALM, repo L3 §4 row 11, carried) — L2c exists precisely because that anchor is confounded |
| C | *When-axis* (timing of constraint introduction) | Constraint/penalty annealing curricula (PINN curriculum training, arXiv:2503.15561, arXiv:2605.15254 **[search]**: physics-loss weight ramped 0→target); gradual unfreezing (ULMFiT, Howard & Ruder 2018, arXiv:1801.06146 **[memory]**; progressive freezing/unfreezing family **[search]**); early-training-period criticality (arXiv:2403.15210 **[search]**; critical learning periods, Achille et al. **[memory]**) | **PARTIALLY-BACKED** premise; the specific cell is **EMPTY (verified by search this week)** | That *when* a constraint is introduced changes the optimum is established in adjacent settings (PINNs: constraint-first vs refinement-later both beat naive joint training in different regimes **[search]**); freezing schedules trade stability vs adaptation | No published sweep of "when during LM training to introduce a fixed semantic subspace/target" exists that we could find; LCM/SONAR-class systems fixed the space from step 0 (carried). Direction is genuinely unknown — this is the axis's justification, not evidence it will help |

**Summary sentence per mechanism (the honest one-liners):**

- **(a)** = A1+A2+A3+A4. Steps A1–A3 are individually LIT-BACKED operations with
  measurable, known costs; the *composite* — and especially A4, pin-to-external-values —
  is **NOVEL-EXTRAPOLATION** whose nearest measured neighbours (knowledge editing,
  frozen semantic init) mostly *failed* in the relevant respect. It is registered below
  as a falsification-shaped experiment (S1), not a design decision.
- **(b)** is **PARTIALLY-BACKED**: the alternating-optimisation mechanism class exists
  (Concept Whitening) and the soft distillation-to-fixed-target machinery is routine,
  but the externally-fixed relational target is an empty cell and the fixed-target
  scaling anchor is adverse-until-de-confounded.
- **(c)** is **PARTIALLY-BACKED** as a question ("timing matters" is established
  elsewhere) and **EMPTY as a measured cell** — the strongest case for running it is
  that *no outcome direction can currently be asserted at all*.

**What none of this backs (stated to prevent drift):** nothing above supports a claim
that any of these mechanisms *will improve* accuracy or efficiency in an LLM. The
literature supports only that the operations are implementable, that their costs are
measurable, and that the timing question is open.

---

## 2. Why this axis is worth a design document at all (given F2 FAIL)

Three reasons, each tagged:

1. **The upfront-vs-gradual confound is real and cheap to name (design logic, not
   evidence).** L2c as drafted sweeps *how much* is pinned (φ) but implicitly fixes
   *when* (from step 0 / at adapter-training time). If φ>0 fails when imposed upfront,
   that is consistent with BOTH "fixedness is poison" AND "fixedness imposed before the
   model has learned the domain is poison". The LCM anchor cannot distinguish these —
   its lineage never varied timing (carried). A σ (schedule) axis de-confounds L2c the
   same way L2c de-confounds the LCM verdict. STIPULATED: that this second confound is
   worth a Tier-2 instrument before any Tier-4 φ spend; the maintainer decides.
2. **Post-hoc variants change the cost topology (design logic).** Upfront pinning
   requires from-scratch training per design point (Tier 4). Post-hoc projection (S1)
   runs on **frozen pretrained hosts** — Tier 2, no pretraining — so the schedule axis
   makes *some* fixedness questions answerable at 10–100× lower cost. That matters more,
   not less, after F2 FAIL tightened the case for expensive rungs.
3. **The alignability question doubles as the E8/L2a instrument (design logic).**
   S1's step-A1/A2 measurement — "does learned concept geometry align to the constructed
   kernel geometry better than nulls?" — is exactly the correlational premise under
   E8 (SAE-alignment, DRAFT) and L2a (kernel-labelled bottleneck). One Tier-2 experiment
   feeds three consumers.

---

## 3. S0 pilot (run this turn, on-box, $0): Procrustes alignment-null calibration — MEASURED

**Status: EXPLORATORY, UNREGISTERED.** Design-pilot evidence for instrument choice only;
not registry evidence; no hypothesis verdict. Code + full results:
`poc/pilots/s0-alignment-null/` (`dump-vectors.mjs`, `procrustes-null.py`,
`s0-results.json`). Deterministic given seeds; panel = 130 seeded synthetic explications
encoded by the pinned encoder (kot-enc-B/1, D=8192; depth 1–4 × clauses 1–8, Phase-X
generator), JL-projected (X4-class seeded Gaussian) to k ∈ {64,128,256,512}; n ∈
{16,32,65,130} row subsamples; 10 seeds/cell.

**Question.** Mechanism (a)'s step A2 will inevitably be scored by "how well does an
orthogonal map take the model's concept vectors onto the kernel's?". Before any model is
touched: how good does that score look **under the null** (targets with no shared
structure), as a function of panel size n and subspace dimension k?

**Results (means over 10 seeds; sd ≤ 0.01 unless noted; full grid in
`s0-results.json`):**

| Cell (n × k) | Procrustes fit R² — null-random | fit R² — null-shuffled | fit R² — planted σ=0.5 | Gram-RSA — null-random | Gram-RSA — planted σ=0.5 |
|---|---|---|---|---|---|
| 16 × 512 | **0.81** | **0.87** | 0.99 | 0.00 | 0.97 |
| 65 × 512 | **0.59** | **0.65** | 0.97 | 0.01 | 0.97 |
| 130 × 512 | 0.44 | 0.51 | 0.96 | 0.00 | 0.97 |
| 130 × 64 | −0.04 | 0.17 | 0.85 | −0.01 | 0.88 |

Post-map per-concept cosine is worse still: null-random reaches **mean cos 0.90 at
n=16, k=512** and 0.72 at n=130, k=512. Noise dose–response (n=65, k=512): planted-truth
Gram-RSA degrades 1.00 → 0.99 → 0.97 → 0.88 → 0.55 as σ goes 0 → 0.25 → 0.5 → 1.0 → 2.0,
i.e. relational recovery survives noise at twice the signal norm.

**Design consequences (MEASURED, and binding on any S1/E8/L2a alignability metric):**

1. **Raw Procrustes fit and post-map cosine are unusable as primary alignability
   evidence** in the regime any real experiment will occupy (tens-to-hundreds of
   concepts, hundreds of dims): a *random* target admits fit R² up to 0.81 and mean
   cosine 0.90. Any past or future report quoting such numbers without a null band is
   overclaiming by construction. (This is the X3-cosine-ban lesson recurring at the
   subspace level.)
2. **Rotation-invariant relational recovery (Gram-RSA) separates cleanly**: ≈0.00 under
   both nulls in every cell, ≥0.88 for planted structure at σ≤1.0. Primary metric for
   S1 is therefore Gram-RSA against the kernel's relational structure, with the
   shuffled and random null bands re-computed per cell.
3. **The shuffled null is systematically harder than the random null** (fit 0.51 vs
   0.44 at 130×512) — wrong-correspondence-right-geometry inflates naive fit; both
   nulls stay mandatory.

Scope honesty: S0 uses kernel-side synthetic geometry on both sides of the map; it
calibrates the **instrument**, not any property of LLM representations. It licenses no
claim about whether real learned spaces align to the kernel (that is S1's question).

---

## 4. The schedule axis σ, defined (extends L2c; does not replace it)

At any kernel seam with pinned fraction φ (N1-A §4.3), add the **kernel-introduction
schedule** as a second declared independent variable:

- **σ=U (upfront)** — pinned from step 0 of the relevant training. *This is L2c as
  drafted*; every σ sweep therefore contains L2c's design point as its control.
- **σ=G(t_intro, ramp)** — constraint weight/pinned fraction ramped from 0 starting at
  a declared fraction t_intro of training (mechanism (c) applied to (b)-soft or to φ
  itself; PINN-annealing shape **[search]**).
- **σ=P(period, strength)** — periodic normalisation during training: every `period`
  steps, covered-concept representations (or the pinned block) are re-projected toward
  kernel relations with declared strength ∈ (0,1] (mechanism (b); CW-shaped).
- **σ=E (end-only)** — one normalisation/projection pass at end of training, optional
  short repair fine-tune (mechanism (b) degenerate case; cheapest).
- **σ=H (post-hoc cut-out)** — no training-time kernel at all; identify → rotate →
  delete-or-pin on the finished model, optional repair fine-tune (mechanism (a)).

Axis-level rules, inherited without exception: two nulls (text-only, kernel-as-text) +
shuffled-kernel arm **at every σ** (a σ that helps with shuffled vectors is curriculum/
regularisation, not kernel semantics — KILL-3 discipline); full metric vector V; ≥2
scale rungs per claim, ≥3 for any scale adjective; run-vs-audit separation; the S0
metric discipline (§3) for every alignability endpoint.

---

## 5. The experiment family (pre-registerable designs, backed-steps only)

Order is cheapest-decisive-first. Gates tightened relative to N1-A drafts because of
the F2 FAIL (MEASURED): every rung here is **instrument-first** — its pass leaves an
instrument, not a deployment claim.

### S1 — post-hoc alignability + erase/replace probe on frozen hosts (Tier 2, ~$40–90)

The only rung that touches mechanism (a), and only its backed steps; the novel A4 step
enters as a budgeted falsification arm with an expected-fail prior.

- **Hypotheses.**
  - **HS1a (alignability; A1+A2).** In pretrained hosts R1–R3, the learned
    representations of kernel-covered concepts (mapper-exact identification, no
    similarity step) align to kernel geometry better than the S0-style null bands:
    Gram-RSA(model concept geometry, kernel Gram) exceeds the per-cell shuffled-null
    95th percentile, at ≥2 rungs. *Prior: genuinely open — Platonic convergence
    [search] argues learned↔learned alignment grows with scale; no evidence exists
    either way for learned↔constructed.*
  - **HS1b (erase; A3).** LEACE-class erasure of the identified kernel-concept subspace
    degrades covered-slice task accuracy MORE than matched random-subspace erasure of
    equal dimension (i.e. the subspace is load-bearing for covered content) while
    out-of-kernel accuracy is unaffected within a TOST margin.
  - **HS1c (replace; A4 — falsification arm, expected-fail per the editing/frozen-init
    record).** Pinning the erased subspace to adapter-bridged kernel values (E5 recipe,
    disjoint-split bridge) recovers a pre-declared fraction of HS1b's covered-slice
    damage. *A surprise pass here is the only evidence that could ever license σ=H at
    scale; a fail kills σ=H cheaply.*
- **Decisive test.** Per rung × layer-family (embedding edge / mid-network, the ROME
  locus, carried): arms {true-kernel target; shuffled-kernel target; random target;
  random-subspace erasure control; erase-only; erase+replace; erase+replace+repair-tune
  (LoRA-scale, budget-capped)}. DVs: Gram-RSA with S0-recomputed null bands (primary,
  HS1a); covered/uncovered accuracy deltas (primary, HS1b/c); full V including
  repair-tune cost.
- **Kill criteria (frozen at prereg).** HS1a: Gram-RSA within null band at all rungs ⇒
  no alignable kernel structure exists in learned spaces — **E8 and L2a's correlational
  premise dies with it**, and σ=H/σ=E die outright (they have nothing to project onto).
  HS1b: erasure indistinguishable from random-subspace control ⇒ identified subspace not
  load-bearing ⇒ A1's "densely occupy" premise false at these rungs. HS1c: recovery
  below margin (expected) ⇒ σ=H recorded dead; negative committed with full statistics.
- **Scale axis.** R1–R3 mandatory (≥3 rungs ⇒ trend statement licensed); the
  interesting published prediction is alignability *increasing* with scale (Platonic
  **[search]**) — a measured trend either way is reportable.
- **Why-now.** Zero training beyond probes/adapters; feeds E8, L2a, and the σ axis at
  once; and it is the direct test of the maintainer's step-(a) premise at the cheapest
  possible seam.

### S2 — normalisation-during-adaptation sweep (Tier 2–3, ~$80–200; mechanism (b)+(c) at fine-tuning scale)

- **Hypothesis (HS2).** During task fine-tuning of R1–R2 hosts on in-kernel tasks
  (m0b-filtered slices; coverage κ restated per cell), adding the kernel-relations
  regulariser `L_K = distance(Gram(model concepts), Gram(kernel))` under schedule σ ∈
  {U, G(0.5), P(period), E} yields, for at least one σ, covered-slice accuracy
  non-inferior to λ=0 (TOST) AND a strict improvement in ≥1 V component or in a
  pre-declared robustness endpoint (paraphrase-variance, L1a's endpoint family), at ≥2
  rungs, Holm-corrected across the σ grid.
- **Why fine-tuning first.** From-scratch σ sweeps are Tier 4; fine-tuning is the
  cheapest setting where "periodic vs upfront vs end-only" is even definable, and the
  soft (loss-based) variant is the backed one (distillation-to-fixed-target machinery
  **[search]**). STIPULATED: fine-tuning results do not license pretraining claims —
  stated in the prereg, enforced by the P8 envelope.
- **Arms.** λ=0 baseline; each σ × {true, shuffled} kernel Gram; kernel-as-text null
  (same relations rendered as text in the fine-tuning mix at matched tokens).
- **Kill criteria.** No σ passes the conjunction ⇒ mechanism (b) dies at the
  fine-tuning seam (from-scratch σ=P may still be argued ONLY via S3's gate, on the
  explicit record that its cheap probe failed). Shuffled arm recovers ≥ the pre-declared
  fraction of any effect ⇒ regulariser-not-semantics (KILL-3), kernel credit dies.
  Drift endpoint: if under σ=P the free subspace re-learns erased/conflicting concept
  geometry between normalisation passes faster than `period` (a MEASURED
  drift-half-life), periodic normalisation is Sisyphean at that seam and σ=P dies there.
- **Scale axis.** R1–R2, extension R3 on the pre-declared predicate.

### S3 — σ×φ from-scratch exponent leg (Tier 4; amendment to L2c-full, NOT a new spend)

- **Shape.** If and only if L2c-full runs (its own double gate: F2-verdict read —
  now FAIL, so maintainer sign-off is doing all the work — plus an L2c-lite interest
  region), extend its pre-declared grid φ ∈ {0, 0.5, 1.0} × σ ∈ {U} by **one** schedule
  arm chosen by S1+S2 outcomes (σ=G if S2's ramp won; σ=P if periodic won; none if both
  died). DVs and fits per L2c-full (Δα(φ,σ) vs the SONAR-LLM anchor band, P8 §2.4
  classification).
- **Kill criteria.** Inherited from L2c-full (KILL-1/2/3) applied per-σ; additionally
  σ-arm > σ=U on training FLOPs by more than the pre-declared overhead ceiling ⇒ the
  schedule's cost eats its benefit.
- **Honesty note.** S3 is deliberately parasitic: the schedule axis gets NO independent
  Tier-4 budget. If the cheap rungs cannot pick a surviving σ, the axis ends at Tier 2–3
  with a clean negative (directives §7: publishable).

### Cost/decision summary

| Rung | Tier / est. $ | Mechanisms touched | Decides | Gate |
|---|---|---|---|---|
| S0 (done) | 0 / $0 | metric for (a) | instrument choice: Gram-RSA over Procrustes fit — MEASURED | none (exploratory, unregistered) |
| S1 | 2 / ~$40–90 | (a): A1,A2,A3 backed; A4 as falsification arm | alignability premise for σ=H/σ=E, E8, L2a | POST-F2-INFRA-OPEN + maintainer read of F2 FAIL |
| S2 | 2–3 / ~$80–200 | (b) soft + (c) at fine-tuning seam | whether any σ beats upfront/off at the cheap seam; drift half-life | S1 HS1a not-dead + maintainer |
| S3 | 4 / inside L2c-full cap +~15–25% | (b)/(c) at pretraining seam | Δα(φ,σ) vs anchor | L2c-full's own double gate + surviving σ from S1/S2 |

---

## 6. Forks (directives §4 form — hypotheses, not decisions)

**FK-S-1 — subspace-identification instrument (A1).** *(a)* supervised linear probes on
mapper-exact concept occurrences; *(b)* LEACE-style class-conditional means; *(c)*
cross-seed-stable SAE feature clusters (repo L3 §5 stable-subset discipline). *Why
uncertain:* probe-based subspaces and SAE features disagree; SAE dictionaries are
non-canonical (carried). *Decided by:* S1 runs (a) and (b); (c) only if E8 lands first.
*Kill per option:* its identified subspace fails the HS1b load-bearing test.

**FK-S-2 — normalisation-operator identity (B).** *(a)* soft loss `L_K` on Gram
distance (S2 default; backed machinery); *(b)* hard periodic projection: rigid-align the
kernel configuration onto the model's covered rows (Procrustes in the *reverse*
direction) and overwrite (CW-shaped; stronger, riskier); *(c)* LEACE-style
minimal-change affine snap. *Why uncertain:* hard projection risks the frozen-init
wash-out record; soft loss risks doing nothing. *Decided by:* an S2 pilot cell per
operator before freeze. *Kill per option:* drift half-life < period (Sisyphus) or
KILL-3 shuffled recovery.

**FK-S-3 — t_intro grid for σ=G.** *(a)* coarse {0, 0.5, end}; *(b)* fine
{0, 0.25, 0.5, 0.75, end}. *Why uncertain:* no literature exists to size the effect
(§1 row C — empty cell); fine grids cost arms. *Decided by:* S2 runs coarse; fine only
if the coarse trend is monotone with CI excluding flat.

**FK-S-4 — repair-tune budget after σ=H/σ=E.** *(a)* none (pure surgery); *(b)*
LoRA-scale capped budget; *(c)* full fine-tune (defeats the cost point; falsification
reference only). *Decided by:* S1 arms. *Kill:* (b) exceeding a pre-declared fraction
of from-scratch adapter cost erases σ=H's cost rationale.

---

## 7. Honesty footer

This document asserts no empirical result beyond: the S0 pilot's measured null bands
(§3, exploratory, unregistered) and the registry state it cites (m0b PASS with its
envelope; F2 FAIL; E5/E9-defl as carried in N0). Mechanisms (a)-A4, (b)'s
externally-fixed target, and (c)'s specific cell are **not** claimed to work — they are
registered as falsifiable arms and forks with adverse-or-empty priors, per directives
§4. The maintainer's framing ("identify where concepts densely occupy the space") embeds
a premise the superposition literature disputes; S1/HS1b measures that premise instead
of assuming it in either direction. Nothing here amends L2c; σ=U remains the control in
every sweep. No registry entries are created by this document; **nothing is committed
by it** (working-tree only, per the turn's instruction).

---

*Cross-references:* `docs/next/architecture-ladder.md` §4.3 (L2c φ axis; §9 back-ref);
`docs/kernel-design-directives.md` (binding); `registry/verdicts/{m0b,f2}.json`
(MEASURED anchors); `reports/fixed-vectors-in-llms.md` (frozen-vector chain);
`reports/lit-llm-injection-priorart.md` (L3 laws, LCM anchor);
`poc/pilots/s0-alignment-null/` (S0 code + results);
`docs/research-plan/08-stats-and-extrapolation.md` (SAP, anchor classification).
