# GLM52-F1 — The GLM-5.2 follow-up experiment: Kernel-as-Expert (primary) plus concept-conditioned expert residency (secondary), as a decision tree on P0's outcome

> **Status: PRE-REGISTRATION-QUALITY DESIGN, awaiting maintainer sign-off. Nothing here
> is frozen, scheduled, or run; no frozen record, verdict, encoder pin, or registered
> assumption is touched; no git action, model run, or spend occurs in this pass. This
> document states NO feasibility conclusion — verdict generation is a separate role.**
> Author: Fable, architecture-design role (designer-5), 2026-07-12.
>
> **Revision note (same tick):** expanded on maintainer instruction to add **Lever C —
> Kernel-as-Expert (KaE)** as the PRIMARY lever (quality/correctness seam); the routing
> levers B1a/B1b are retained in full as secondary. The expansion was written, like the
> original, BEFORE any P0 routing-structure output was read.
>
> **REVISION-1 (2026-07-13):** the cross-vendor review
> (`poc/gpt56-review/glm-design/REVIEW-SUMMARY.md`, verdict FIX-FIRST, 5 blockers)
> is remediated in §R (REVISION-1, after §10). **Where §R conflicts with §§1–10, §R
> governs**; superseded clauses are marked in place. §R also registers the
> routing-analysis-v2 evidence (coordinator-verified re-analysis of the committed
> fingerprints) and reconciles the branch classifier with it. The emission-timing
> declaration below remains true OF THE ORIGINAL EMISSION; REVISION-1's own timing
> is declared in §R0. F1-K remains PRIMARY; the Branch A/B/C structure, all branch
> thresholds, and all endpoint directions are UNCHANGED by this revision.
>
> **Parent design:** `docs/next/design/glm52-kernel-integration-northstar.md` (GLM52-NS).
> This document makes GLM52-NS §5.3 "P1" concrete, adds the maintainer's new quality
> seam, and arranges everything so the maintainer can sign off ONCE on the plan +
> ceilings and the correct experiments fire mechanically the moment P0's analysis lands
> (no-pre-surface discipline).
>
> **Emission-timing declaration [MEASURED: this repository, this tick]:** at emission,
> the P0 probe is RUNNING on the authorised i4i.2xlarge; its outputs land at
> `s3://kernel-of-truth-artifacts-361738333660/glm52-probe/` as `probe-main.log` +
> `stats.tgz`. The only P0 numbers read before this design was fixed are the P0.1
> **baseline** partials quoted in §1.3 (disk-share, bandwidth, cold tok/s). **No
> routing-structure output (P0.2 traces, P0.3 replay, LOOKA counters, fingerprints,
> sense-pair statistics, TOPK sweep) has been read.** The branch classifier in §3 is
> therefore frozen blind to the quantity it classifies, and F1-K (§2) is independent of
> that quantity by construction.
>
> **ASM block claimed: ASM-2010..2033** (appendix, this file; owner designer-5). Range
> verified free at emission: central register tail in `registry/assumptions.jsonl` is
> ASM-1989; the ENGINE-INF companion block claims ASM-1990..2009; repo-wide grep for
> `ASM-2[0-9][0-9][0-9]` finds nothing above ASM-2005. Central registration is the
> coordinator's action, in the commit that lands this file, after the standing review
> gate; this pass writes the design + companion JSON only.
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = repository bytes or a
> pinned mechanical output read this tick; `[LIT-BACKED: ref]` = external fact verified
> at source; `[DERIVED]` = arithmetic over tagged premises; `[STIPULATED: ASM-id]` = a
> design choice made here; `[EXTRAPOLATION: ASM-id]` = registered projection, never a
> premise; `[ASSESSMENT]` = one designer's judgment, binding on nothing.

---

## 0. Plain-language summary (maintainer-facing)

GLM-5.2 answers each token by consulting a handful of "experts" chosen by a router.
This design puts three levers on that machinery, in priority order:

- **Lever C — Kernel-as-Expert (PRIMARY, quality).** For tokens whose context is about
  a concept the kernel grounds, splice a small grounded content-carrier into the MoE
  sum — alongside (ADD) or in place of (REPLACE) native experts — so the model's
  answer is pulled toward the kernel's grounded content exactly where GLM-5.2
  misremembers or hallucinates. This is the architectural form of the programme's one
  verdict-grade affirmative (f2b-transfer: kernel-authored *content* through a thin
  interface lifted a small model +0.25), delivered inside a frontier model's routing
  instead of at the prompt boundary. The word "kernel" is used loosely and honestly:
  on the programme's own knull findings, what is being tested is grounded CONTENT, not
  kernel-specific structure — and the deflator arms are built to keep that distinction
  enforced. F1-K, the experiment, does not depend on the probe's routing outcome.
- **Lever B1a — concept-conditioned expert PINNING (secondary, speed).** Keep each
  prompt's concept-relevant experts in RAM; fewer cold disk reads at byte-identical
  output. Runs only if the probe finds concept-shaped routing structure.
- **Lever B1b — concept-guided expert DROP (secondary, size).** Stop loading
  concept-irrelevant experts at all; smaller and faster with a quality cost to bound.
  Gated behind B1a's outcome.

The probe's routing result routes the SECONDARY levers through three pre-written
branches (concept structure → run the pinning A/B; predictable-but-not-conceptual →
one cheap salvage-or-kill ablation; no structure → both routing levers recorded dead
and an honest pivot). The PRIMARY lever runs regardless. Every experiment carries the
deflator that has capped this programme four times: the kernel arm must beat an
equally-sized kernel-free control, or the result is "content/conditioning helps," not
"the kernel helps."

---

## 1. The three levers, precisely

### 1.1 Lever C — Kernel-as-Expert (KaE) [STIPULATED: ASM-2024]

**Mechanism.** A training-free gate detects that the current context concerns a
concept the kernel grounds (crux 1, §2.3). For gated token positions, at a
pre-registered set of MoE layers, a small per-concept content-carrier K_c (crux 2,
§2.4) is spliced into the MoE output: **ADD** mode adds g·K_c(x) to the routed-expert
sum, leaving native experts intact (pure quality intervention); **REPLACE** mode
substitutes K_c for the lowest-weighted native expert(s) on gated tokens (quality plus
a per-token I/O saving, with an off-native risk to bound) (crux 3, §2.5).

**Hypothesis under test (stated, not asserted):** on public QA benchmarks restricted
to kernel-known concepts, KaE-ADD lifts accuracy by grounding concepts the model gets
wrong. GLM-5.2 is already strong; the plausible win is *correction where it errs*, not
new capability — the paired flip analysis in §2.7 is built for exactly that.

**Thesis linkage.** This is a CORRECTNESS-thesis experiment at 744B scale, the direct
architectural descendant of f2b-transfer (+0.25, audit-confirmed, content-attributed)
and DECONF-B (which showed the lift lives in the content, not kernel structure)
[MEASURED: README "Experiment summary"]. The claim ladder in §2.6 is therefore built
so that each rung says exactly what was beaten — extra content, concept-aligned
content, or kernel-authored content — and nothing more.

**Independence.** KaE's gate is external (lexical/anchor-based), not router-based; it
does not presuppose that native routing is concept-aligned. F1-K therefore runs in
EVERY branch of §3. [STIPULATED: ASM-2024]

### 1.2 Levers B1a and B1b — the routing levers [STIPULATED: ASM-2010; taxonomy carried from ASM-1973]

**B1a — concept-conditioned expert PINNING (speed; quality-safe by construction).**
For each prompt, map its kernel concept labels to a predicted per-layer expert working
set (the concept→expert map, built offline from P0's routing traces), and install that
set as colibri's pinned hot set (`PIN=` file) within a fixed RAM budget (`PIN_GB`).
Pinning changes **which expert bytes are already in RAM** when the router asks for
them; it never changes which experts the router selects or what is computed. The
output is byte-identical at greedy decoding; the entire effect is fewer cold NVMe
reads per token — a pure SPEED win with zero quality dimension (invariant verified
mechanically, §7.4).

**B1b — concept-guided expert DROP (size + I/O; function-changing).** Do not load
experts outside the concept-relevant set at all: soft mode restricts or re-biases the
router's candidate set (colibri's `TOPK`/`TOPP` knobs are the router-weight-only
control); hard mode builds a pruned expert shard for a concept-profiled workload
(disk estate shrinks toward f × 370 GB at retained fraction f). This is DDC's
training-free move with the expert as the deletion unit. It **changes the computed
function**, so it carries a quality cost that must be bounded by DDC-style
matched-compression retention arms before any claim (ASM-1978 carried).

### 1.3 The measured physics all three levers live in

From the P0.1 partials [MEASURED: `probe-main.log`, P0.1 baseline section, read
2026-07-12; re-verified against `stats.tgz` when it lands, ASM-2011]:

- expert-disk I/O = **80% of decode wall-time** on the probe box;
- effective NVMe read bandwidth **3.33 GB/s**;
- cold decode **0.09 tok/s**.

Consequences, all arithmetic [DERIVED: ASM-2012]:

1. **Amdahl ceiling for the routing levers.** With disk share d = 0.8, eliminating a
   fraction r of expert miss-bytes multiplies throughput by 1 / (0.2 + 0.8·(1 − r)):
   r = 0.3 → 1.32×, r = 0.5 → 1.67×, r = 1 → **5.0× ceiling on this box**. Any larger
   claim on this box is arithmetic error by definition.
2. **Bandwidth cross-check.** 3.33 GB/s ÷ ~11.4 GB/token (GLM52-NS §1.2) bounds cold
   decode at ~0.29 tok/s; the measured 0.09 tok/s implies ~31% effective read
   efficiency. Endpoints therefore use the engine's own miss-byte counters as primary
   and iostat as cross-check — bandwidth arithmetic is a sanity band, not a
   measurement.
3. **What the physics means for Lever C:** nothing about its *claim* — KaE's endpoint
   is accuracy, not throughput — but everything about its *evaluation cost*: at these
   speeds, generative benchmarking is unaffordable, so all F1-K scoring rides
   prefill/loglikelihood (ASM-1988 carried; §2.7), and REPLACE's I/O saving is a
   secondary systems observation priced by the same arithmetic as B1b.

### 1.4 What each lever presupposes

- **B1a/B1b** presuppose a concept→expert map with genuine conditional structure:
  distinct concept regions must route to measurably distinct expert sets. P0 measures
  precisely this; §3's decision tree is exhaustive over the outcome.
- **KaE** presupposes only (i) a phrase→concept trigger map (the minimal ~24-concept
  map suffices, §8), (ii) per-concept grounded content to carry, and (iii) an
  amendment to Law-1 (§2.2). It does NOT presuppose routing structure.

---

## 2. F1-K — Kernel-as-Expert (PRIMARY; unconditional on the routing outcome)

### 2.1 Question

On public multiple-choice QA restricted to kernel-known concepts, does splicing a
grounded per-concept content-carrier into GLM-5.2's MoE sum — training-free, gated by
concept detection — lift accuracy over the unmodified model, over an equal-capacity
concept-agnostic content injection, and over a plain-dictionary knull carrier?

### 2.2 Law-1 interaction — MAINTAINER GATE 0 [STIPULATED: ASM-2025]

House Law-1 (interface-locality) currently states that no kernel vector enters a
model's activations; kernel content enters as text/selection/external computation
[MEASURED: DDC.md §1.2]. KaE's carrier **writes into the residual stream** and
therefore requires an explicit, scoped, registered amendment to Law-1 before F1-K may
run. The maintainer's scope-expansion instruction signals intent, but the amendment
must be an explicit registry event, not an inference.

**MAINTAINER GATE 0:** approve a scoped Law-1 amendment — "kernel-derived content
vectors may enter model activations ONLY within the KaE track, only via the registered
splice, with the deflator ladder of §2.6 mandatory" — before any F1-K run. Without it
F1-K does not run, and the rest of this design is unaffected.

### 2.3 Crux 1 — training-free gating and the splice point [STIPULATED: ASM-2026]

**No router retraining, anywhere.** The native router (logits → sigmoid-plus-bias →
top-8 → weighted sum + shared expert, colibri `moe()` at `glm.c:1270`
[LIT-BACKED: coordinator brief this tick; fetch-grade — line number and semantics
re-verified from the checkout at bring-up per ASM-1971 discipline]) is left untouched.
The gate is a PARALLEL mechanism:

- **G-lex (primary): lexical phrase→concept gate, computed harness-side.** The
  harness runs the phrase→concept map (the ~24 probe concepts, trigger surface
  expanded with WordNet lemma/derivational sets; §8) over the tokenised context and
  emits per-position concept spans to a sidecar file the engine reads (`KAE=spans`).
  Zero learned components; deterministic; auditable byte-for-byte. Known honest
  weakness: word-level triggers conflate senses (the sense-split track's defect);
  sense-minimal-pair items are tagged so §2.7 can report them separately.
- **G-emb (registered variant, budget-permitting):** per-token cosine of the hidden
  state at the splice layer against per-concept anchor vectors (mean hidden states
  harvested from concept renderings by plain forward passes), threshold θ calibrated
  on the dev split to match G-lex's firing rate. Training-free (forward passes +
  arithmetic only). Run only if the ceiling allows; never substituted post hoc.
- **G-route (Branch-A-conditional variant, noted not scheduled):** fire when the
  native router's weight mass on concept-associated experts is high. Presupposes
  routing structure, so it is admissible only after a Branch-A classification (§3);
  recorded as a future-variant note.

**Splice point.** Inside `moe()`, after the routed top-8 weighted sum and the shared
expert are accumulated and before the result is written back to the residual stream:
for token position t gated to concept c, at layer l ∈ L_KaE:

- ADD: `y += g * K[c][l]`
- REPLACE: skip (do not load) the lowest-sigmoid-weight native expert of the top-8
  and add `w_dropped * K[c][l]` in its place.

**Layer set L_KaE.** A design choice, not a fact; pre-registered pilot on the dev
split (§2.7) over three configurations — L1 = one mid-stack MoE layer (≈ layer 40),
L2 = four evenly spaced mid-to-late MoE layers, L3 = all MoE layers at reduced g —
crossed with blend grid g ∈ {0.5, 1.0, 2.0} × mean native expert weight. The argmax
dev configuration is FROZEN before the main run; the main run reports that single
configuration plus the pre-registered arms. [STIPULATED: ASM-2026]
**[REVISED by REVISION-1 §R4: the selection statistic is carrier-BLIND (unlabeled
carrier panel), and the frozen configuration is applied identically to every arm
including deflator derangements. ASM-2040 supersedes the selection clause of
ASM-2026.]**

### 2.4 Crux 2 — what the kernel-expert concretely IS [STIPULATED: ASM-2027]

Options weighed, honestly:

| Candidate carrier | Verdict here | Why |
|---|---|---|
| **Per-concept definition offsets** (primary): for concept c and layer l, v_{c,l} = mean difference of hidden states at gated positions between contexts WITH the kernel explication of c prepended and matched contexts WITHOUT, over m = 16 construction contexts; K[c][l] := v_{c,l} | **ADOPTED** | Training-free (forward passes + arithmetic; no gradients); distils the mechanism f2b-transfer proved at the prompt boundary into the residual stream; tiny (24 concepts × |L_KaE| × 6,144 fp32 ≈ 0.6–44 MB); the deflator carriers are built by the IDENTICAL procedure with substituted content, giving clean symmetry. Steering-vector/task-arithmetic literature exists for this construction shape (cited at abstract level, not source-verified this tick). |
| Small trained LM/MLP as expert | REJECTED for F1-K | Requires training (or a learned projection to hidden dim 6,144) — outside the programme's training-free tier. |
| Decoded kernel concept vectors (the programme's own encoder output projected in) | DEFERRED | Foreign vectors the attention/FFN stack was never trained to read — the same objection that deferred B3 (ASM-1981); a research note, not an arm. |
| Retrieval-injection as TEXT (prepend definitions to the prompt) | Not an arm of F1-K, but the **bridge control** (§2.6, arm d3-text) | This is f2b-transfer's original seam; including it as a control shows whether the in-routing splice adds anything over plain prompt injection — an honest and cheap question the design must not dodge. |

**Construction protocol:** m = 16 contexts per concept (drawn from the probe corpus
plus WordNet-authored renderings, disjoint from all evaluation items), two variants
each (kernel explication prepended vs not), hidden states recorded at gated positions
at the moe() input of each l ∈ L_KaE via the C patch's dump mode (§2.8); v_{c,l} is
the mean difference. Deflator carriers (§2.6) substitute the prepended content; d0
substitutes a norm-matched random vector. All construction is forward passes on the
probe box. [STIPULATED: ASM-2027]

### 2.5 Crux 3 — ADD vs REPLACE [STIPULATED: ASM-2028]

**Ordering rule: ADD first; REPLACE only if ADD passes K-1 (§2.6).** REPLACE = ADD
plus removal; removal is only worth measuring once the addition demonstrably carries
value.

| | ADD | REPLACE |
|---|---|---|
| Intervention | `y += g·K[c][l]` on gated tokens; native experts intact | drop lowest-weight native expert of top-8 on gated tokens; K takes its weight |
| Claim type | pure quality | quality + per-token I/O saving on gated tokens (one fewer expert load per gated (token, layer)) |
| Primary endpoint | accuracy on the known-concept QA subset (§2.7) vs baseline | same accuracy endpoint vs ADD (non-inferiority), plus measured expert-bytes saved |
| Decision rule | see ladder, §2.6 | ADMITTED only after ADD passes K-1; PASSES iff the confidence-bound non-inferiority test of REVISION-1 §R1.2 passes AND measured I/O saving > 0 on gated tokens; else recorded "removal costs more than it saves" **[point-estimate rule REVISED by §R1.2 / ASM-2037]** |
| Off-concept guard | gate never fires → off-concept outputs byte-identical to baseline (mechanical check on a 60-item off-concept subset; SHA-256 over token ids; any mismatch voids the run) | identical guard, identical consequence |

### 2.6 Crux 4 — the deflator ladder (the knull discipline, mandatory) [STIPULATED: ASM-2029]

Arms, all with the SAME gate, SAME splice, SAME layer set, SAME g, differing ONLY in
carrier content; every carrier built by the §2.4 construction with substituted
prepend-content, norm-reported:

| Arm | Carrier content | What it controls |
|---|---|---|
| b0 | none (unmodified GLM-5.2) | baseline |
| d0 | norm-matched random vector | placebo/perturbation: if d0 beats b0, the instrument is measuring noise sensitivity → **run VOIDED** |
| d1 | ~~equal-capacity CONCEPT-AGNOSTIC content: offsets built from generic encyclopedic paragraphs unrelated to the gated concept~~ **REPLACED by REVISION-1 §R2: d1-drng — repeated seeded concept-label DERANGEMENTS of the IDENTICAL K carrier set, layerwise norm-matched; the only difference from K is whether the label→carrier mapping is the true kernel one (dose-exact)** | "any extra content helps" → sharpened to "misaligned kernel content at identical dose" — the arm that capped f2b/DECONF-B/RULES-2, now immune to length/norm/covariance/construction confounds [ASM-2036 supersedes the d1 clause of ASM-2029] |
| d2 | plain-dictionary definitions of the SAME concepts (the knull proper) | "any concept-aligned content helps" vs kernel-authored content |
| d3-text | kernel explication prepended as PROMPT TEXT, no splice | does the in-routing seam add anything over f2b-transfer's prompt seam? |
| K | kernel explication offsets (treatment) | — |

**The licensing ladder (each rung requires the paired test of §2.7 at its margin;
failing rung n caps the claim at rung n−1):**

- **K-1 (content seam works):** K > b0. Licenses: "content injection at the MoE seam
  lifts accuracy on concept-covered QA at this model/box."
- **K-2 (concept alignment matters):** K > d1-drng. Licenses: "the TRUE
  concept→carrier alignment beats label-deranged assignments of the identical
  carrier set at identical dose at this seam." **[wording REVISED by §R2]**
- **K-3 (kernel-specific, the hard bar):** K > d2. Licenses: "kernel-authored
  explications beat plain-dictionary definitions at this seam" — the first
  kernel-specific sentence the programme would ever have earned at a content seam;
  on the four-deflation record, a K≈d2 tie is the modal expectation and is reported
  with equal prominence in the pre-adopted content-not-structure wording.
- **K-seam (descriptive, not a rung):** K vs d3-text, reported both directions —
  whether the splice beats prompt injection is a mechanism finding either way.

A deflationary null at any rung is a real result: rung-1 null says the seam itself is
inert at this scale; rung-2 null says f2b's content effect does not survive the move
from prompt to routing; rung-3 null is the fifth content-not-structure datum. No
outcome licenses an intelligence, parity, or general-capability claim, and no outcome
moves a synthesis verdict — F1-K feeds the CORRECTNESS ledger only through
verdict-gen's own pathway. [STIPULATED: ASM-2029, ASM-2033]

### 2.7 QA-benchmark protocol [STIPULATED: ASM-2030]

**[REVISED by REVISION-1: scoring → §R1.1 (frozen candidate-independent label-token
template; one prefill per item per arm); n_min/splits/statistics → §R3 (cluster-aware
power-derived n, cluster-level primary test, expanded dev split); ASM-2035/2038
supersede the corresponding clauses of ASM-2030. The subset filter, off-concept
guard, ceiling-bound wording, and fixed-n/no-optional-stopping rules stand.]**

- **Known-concept subset construction (mechanical):** filter MMLU items (question +
  options) whose text lexically matches ≥1 trigger lemma of the phrase→concept map.
  Honest risk: ~24 concepts (kinship, sense pairs, molecule families) may yield a
  small or topically skewed subset; subset composition is reported verbatim. If MMLU
  yields fewer than the minimum, supplement — mechanically, same filter — from a
  pre-registered pool (ARC-Easy/Challenge, OpenBookQA, CommonsenseQA). **n_min = 240
  items; hard gate:** if the pooled subset < 240, F1-K does NOT run and returns to
  the maintainer with the measured coverage shortfall (this is the scale gate biting,
  §8 — not a failure of the lever). **[SUPERSEDED by REVISION-1 §R3.2's power gate:
  C ≥ 48 clusters with m ≥ 8 items within n_max = 1,440, n_required power-derived;
  ASM-2038.]**
- **Splits:** dev = 24 items (pilot: layer-set × g grid, §2.3) + the 60-item
  off-concept guard set; test = the remaining ≥216 items, untouched until arms are
  frozen. Construction contexts (§2.4) are disjoint from all of these.
- **Scoring:** loglikelihood over answer options via prefill (echo+logprobs through
  the gateway; the ASM-1988 mitigation — generative scoring is unaffordable at
  0.09 tok/s), argmax = the model's answer. Sense-minimal-pair items tagged and
  reported as a subgroup (descriptive).
- **Statistics:** unit = item; fully paired across arms; primary test = paired
  one-sided permutation on per-item correctness (10,000 resamples), α = 0.05, with a
  pre-registered effect floor of **≥ +3 accuracy points** for each ladder rung
  (§2.6); flip matrix (corrections vs regressions) reported as the mechanism-level
  secondary; baseline-wrong subgroup reported descriptively ONLY (selection on errors
  regresses to the mean under any perturbation — that is what d0 is for). Fixed n,
  no optional stopping, no post-hoc subgroups beyond those named here. An
  honesty-first penalised score (wrong = −2, per the programme's scoring memo) is a
  named secondary descriptive, not an endpoint.
- **Baseline strength caveat:** GLM-5.2 is expected near ceiling on many public QA
  items (unverified here; the b0 arm measures it). If b0 accuracy on the subset
  > 95%, headroom is < the effect floor and F1-K reports "ceiling-bound at this
  subset" rather than a null — worded in advance to prevent a headroom artifact
  masquerading as a lever failure.

### 2.8 Feasibility on colibri (the C patch, scoped) [STIPULATED: ASM-2031]

Colibri is a single ~2,400-line C file with no plugin architecture; the KaE patch is
an edit to `glm.c` on the instance, kept as an in-repo diff:

1. loader: read `KAE=` sidecar (per-position concept spans; per-concept per-layer
   offset table, ~0.6–44 MB fp32) — ~60 lines;
2. splice in `moe()` (`glm.c:1270`, re-verified at bring-up): ADD = one gated
   `axpy` after the expert sum; REPLACE = skip one expert load + substitute — ~40
   lines;
3. hidden-state dump mode at `moe()` input for construction runs (§2.4) — ~50 lines;
4. G-emb variant (per-token cosine vs anchor table) if run — ~50 lines.

Total ≈ 150–200 lines in one function plus a loader; tractable for one agent-day on
the instance [ASSESSMENT]. This EXCEEDS the P0 trace-dump-only C envelope
(ASM-1986/1989), so it rides MAINTAINER GATE 0's approval alongside the Law-1
amendment; fork-vs-upstream etiquette carried from ASM-1989 (the diff stays in-repo;
nothing is pushed upstream without a separate decision).

### 2.9 Cost [EXTRAPOLATION: ASM-2032]

**[SUPERSEDED by REVISION-1 §R6: n is power-derived (§R3), scoring is one prefill
per item per arm (§R1.1), and the ceiling is derived from the power-required n at
the pessimistic prefill band — new F1-K ceiling $450, with a pre-registered
degradation order that never cuts n below the power requirement. ASM-2041
supersedes ASM-2032.]** Original band retained for the record: ~$40–140 at $0.69/h,
ceiling $250, per-option prefill scoring, n 240–300.

---

## 3. The branch classifier for the ROUTING levers — mechanical, frozen before any routing output is read

F1-K (§2) is unconditional and is unaffected by this section.

### 3.1 Classifier quantities [STIPULATED: ASM-2013]

All quantities are computed by the P0.3 offline replay over the committed trace
dataset, at the matched RAM budget corresponding to the probe box (`PIN_GB` as
configured at P0; recorded in `stats.tgz`), on held-out prompts under the probe's
pre-registered split:

- **M_oracle** — relative miss-byte reduction of the *oracle per-prompt pin* (each
  prompt pinned from its own trace; the exploitable-structure ceiling) versus the
  *global-hot pin* (AUTOPIN-analog).
- **M_kernel** — relative miss-byte reduction of the *kernel-concept pin* versus the
  **stronger** of the two deflators (global-hot pin; embedding-cluster pin), i.e. the
  G-B1 quantity of ASM-1976.
- **p_perm** — one-sided permutation p (≥10,000 label shuffles) for
  within-concept-cluster fingerprint similarity exceeding across-cluster similarity
  (fingerprint = per-layer expert-usage histogram from colibri `STATS`; similarity as
  pre-registered in the P0 analysis plan).
- **SensePairSep** — fraction of the probe's registered sense-minimal-pair comparisons
  (break-fracture vs break-pause; bank-institution vs bank-riverside; as registered in
  the probe suite) in which cross-sense fingerprint distance exceeds within-sense
  distance.

### 3.2 Branch definitions [STIPULATED: ASM-2013]

| Branch | Condition (evaluated in this order) | Reading |
|---|---|---|
| **A** | M_kernel ≥ 10% AND p_perm < 0.05 | Concept-conditioned routing structure exists and the concept labelling exploits it beyond both deflators → **F1-A** (§4) fires. Sub-case **A1**: SensePairSep ≥ 0.75 → sense-level granularity live; B1b may later inherit sense-split shards. Sub-case **A2**: SensePairSep < 0.75 → F1-A proceeds identically, but the map's granularity is capped at word-level concepts and all sense-level routing claims (including sense-split B1b shards) are recorded unsupported at this scale — a datum for the sense-split track, not a licence. |
| **B** | not A, AND M_oracle ≥ 15% | Exploitable per-prompt routing structure exists, but concept labels do not beat kernel-free conditioning → **F1-B** salvage-or-kill (§5) fires. |
| **C** | M_oracle < 15% (regardless of p_perm) | Even the per-prompt oracle cannot meaningfully beat global-hot pinning at matched budget: there is no per-prompt structure for ANY conditioner — kernel or otherwise — to exploit → **F1-C** pivot (§6) fires. |

Rationale for the C threshold: if the ceiling (oracle) yields under 15% relative
miss reduction, then by §1.3(1) the best *achievable* speedup from any conditioning
policy is under ~1.14× on this box — beneath measurement dignity given run-to-run
variance, and both routing levers are honestly dead-at-this-model. Rationale for
evaluating A before B: A's condition is the registered admission gate G-B1
(ASM-1976) with its ≥10%-vs-both-deflators margin, now frozen at exactly 10% as that
ASM required of this prereg. [STIPULATED: ASM-2013]

Edge handling: if `stats.tgz` is corrupt, the trace dataset fails its integrity
check, or the replay cannot be reproduced from committed bytes, the classifier does
NOT fire; the probe is re-run within its own ceiling before any branch is taken.
[STIPULATED: ASM-2013]

**Sequencing on the one box:** on P0 landing, F1-K runs first (primary), then the
classified routing branch, both within their own ceilings. [STIPULATED: ASM-2010]

---

## 4. Branch A → F1-A: live concept-guided pinning A/B (secondary-primary)

### 4.1 Question

Does concept-conditioned expert pinning reduce expert I/O *live* (not in replay), at
matched RAM budget, beyond colibri's own usage-history pinning AND a kernel-free
embedding-cluster baseline, with byte-identical outputs?

### 4.2 Arms [STIPULATED: ASM-2014]

All arms decode the same held-out prompt set, greedy (`DRAFT=0`), `TOPK`/`TOPP` at
config defaults, `PILOT=0`, identical `PIN_GB` budget for every pinned arm, page-cache
state controlled per §7.2, and the KaE patch DISABLED (`KAE` unset — the routing
levers are measured on the unmodified function):

| Arm | Pin policy | Role |
|---|---|---|
| a0 | no pin; LRU only (colibri default) | floor / engine baseline |
| a1 | **AUTOPIN** — colibri's native usage-history pinning, warmed on the map-building corpus | **deflator 1** (the built-in kernel-free competitor) |
| a2 | **embedding-cluster pin** — map-building prompts clustered by a pinned off-the-shelf sentence embedding (frozen by content hash at bring-up), K = number of concept clusters; per-cluster expert histograms; held-out prompt assigned to nearest cluster; top experts pinned to budget | **deflator 2** (the knull-analog: concept-agnostic content conditioning) |
| a3 | **kernel-concept pin** — union of the prompt's labelled concepts' per-layer histograms from the P0-trace map (train split only), truncated to budget | treatment |
| a4 | random pin at matched budget (seeded) | floor control |
| a5 | oracle per-prompt pin (pin from a first pass's own trace, measure a second pass) | ceiling, never an arm to beat |

The concept→expert map is built exclusively from P0's committed traces (train split);
evaluation prompts are **fresh renderings never used in map construction** (§4.3).
Map-building is offline CPU work, re-analysable indefinitely.

### 4.3 Workload [STIPULATED: ASM-2014]

N = 48 fresh prompts **[REVISED by REVISION-1 §R3.3: N is power-derived from the
P0.3 replay variance via the frozen formula, N ∈ [48, 96]; 48 is now the FLOOR, not
the choice; ASM-2038 supersedes the N clause of ASM-2014/2017]**, stratified across
the probe's concept clusters (≥2 per cluster,
including fresh sense-minimal-pair items), authored from kernel explications plus
WordNet sense glosses/synonym sets (§8 scopes this), surface-disjoint from
map-building prompts (mechanical check: no shared content 5-gram). Decode length 96
tokens per prompt. The statistical unit is the prompt; the design is fully paired
(every arm sees every prompt).

### 4.4 Endpoints and decision rule [STIPULATED: ASM-2014, ASM-2017]

- **Primary endpoint:** expert miss-bytes per generated token (engine counter;
  iostat cross-check), per prompt.
- **Secondary:** tok/s; per-layer hit rate; wall-clock decode time.
- **Quality invariant (mandatory, mechanical):** `DRAFT=0` greedy outputs of a0–a5
  are byte-identical per prompt. Any divergence anywhere **voids the run** (it would
  mean pinning touched computation, i.e. an engine defect).
- **Statistics:** for each of the two licensed comparisons (a3 vs a1; a3 vs a2), the
  paired one-sided permutation test on per-prompt miss-bytes (10,000 resamples),
  α = 0.05, plus the pre-registered effect threshold: median relative miss-byte
  reduction ≥ 10%. **PASS requires BOTH comparisons to clear both criteria**
  (conjunction; conservative, no multiplicity correction needed). Anything else is
  the null. **[REVISED by REVISION-1 §R3.3: the primary permutation is cluster-aware
  — sign-flips at concept-cluster level on per-cluster mean paired differences —
  and cluster-level BCa 95% CIs are reported for both contrasts; ASM-2038.]**
- **Kill rule:** a3 ≤ either deflator on the effect threshold → the kernel-specific
  B1a claim is dead at this model/box; report as §4.5 null wording. No re-runs, no
  threshold movement, no post-hoc subgroups beyond the pre-registered per-cluster
  descriptives.

### 4.5 What each outcome says [STIPULATED: ASM-2022; caps of ASM-1987 carried]

- **Licensed PASS wording:** "Concept-conditioned expert pinning reduced expert I/O
  on concept-labelled workloads at this model and box, beyond both usage-history
  pinning and a kernel-free topic-cluster baseline, at matched RAM budget, with
  byte-identical outputs." Sign, not slope; one model, one box, labelled workloads
  only; **no intelligence, efficiency-thesis, parity, or cost claim**; the EFFICIENCY
  synthesis verdict does not move.
- **Deflationary-null wording (pre-adopted):** "Content/topic conditioning of expert
  residency helps (or does not); the kernel is one conditioner among several and
  earned no increment over the kernel-free baseline" — the f2b/DECONF-B/RULES-2
  content-not-structure form, reported with prominence equal to a pass, and feeding
  the same programme ledger that has already recorded four such deflations.
- Either way, B1b's own prereg may proceed ONLY on a PASS here (plus sense-pair
  scoping per §3.2 A1/A2); on a null, B1b is dead alongside (it presupposes the same
  map validity).

### 4.6 Rider (optional, zero marginal instance cost): B2 acceptance measurement

While the box is warm, measure engine-rendered draft acceptance on kinship/sense
items through colibri's existing draft path (GLM52-NS §2.3, lossless mode only).
Measurement, not a lever test; own wording caps; skipped without penalty if the
ceiling nears. [STIPULATED: ASM-2014]

### 4.7 Cost [EXTRAPOLATION: ASM-2021]

~27,650 decode tokens across a0–a5 (48 × 96 × 6) at a warm 0.09–0.25 tok/s → 31–85
instance-hours ≈ $21–59 at $0.69/h (i4i.2xlarge, on-demand), plus restore (~1 h),
map-building (CPU, negligible), and the a5 double-pass. **Ceiling: $150** (matches
the parent design's P1 band). S3 artifact retention $8.5/mo continues regardless.
**[SUPERSEDED by REVISION-1 §R6: N power-derived up to 96 → new ceiling $180;
ASM-2041.]**

---

## 5. Branch B → F1-B: salvage-or-kill (concept labels vs kernel-free conditioning)

### 5.1 The situation Branch B encodes

Routing has exploitable per-prompt structure (M_oracle ≥ 15%) but concept labels did
not beat kernel-free conditioning in replay. The honest hypothesis set: (i) the
structure is positional/frequency/surface-form, not conceptual; (ii) the structure is
conceptual but the 24-prompt probe under-powered the comparison; (iii) the kernel's
labelling is too coarse (un-sense-split, per the sense-split track's known defect).

### 5.2 Design [STIPULATED: ASM-2018]

Two components, strictly ordered:

**F1-B.1 — paraphrase diagnostic.** **[REVISED by REVISION-1 §R3.4: 16+16 pairs
(was 6+6), powered at ≥80% for a large standardized effect d ≥ 1.0 on the per-pair
routing-overlap contrast, one-sided two-sample permutation, α = 0.05; overlap
metric = MEAN-CENTERED fingerprint cosine (instrument-validity choice from the v2
re-analysis, §R0); ~$8–12; ASM-2038 supersedes the 6+6 clause of ASM-2018.]**
Original design for the record — six pairs: same concept, surface-disjoint
paraphrase renderings; six pairs:
surface-overlapping but concept-distinct. If *paraphrase pairs do not share routing*
while *surface-matched pairs do*, the structure is surface-form, hypothesis (i) is
confirmed, and the kernel routing lever is **killed directly** — no further spend. If
paraphrase pairs DO share routing, the replay failure was power- or
granularity-limited and F1-B.2 fires.

**F1-B.2 — additive ablation, live (three arms, paired, same protocol as §4):**
a2 (embedding-cluster pin, kernel-free) vs a2+K (embedding-cluster features PLUS
kernel concept labels, same budget) vs a1 (AUTOPIN). **Primary endpoint:** additive
relative miss-byte reduction of a2+K over a2. **Kill rule:** additive gain < 5%
median or p ≥ 0.05 (paired one-sided permutation, 10,000 resamples) → the
kernel-specific B1a claim is recorded dead at this model/box; B1b dies with it.
**Salvage rule:** additive gain ≥ 5% with p < 0.05 → B1a is re-admitted at reduced
expectation and a scoped F1-A (a1/a2/a2+K/a4 only) may run inside the remaining
Branch-B ceiling.

**What survives a kill, honestly:** the kernel-free structure itself. A
prefix-fingerprint pinning policy (decode a 16-token prefix, harvest the `STATS`
histogram, pin to budget, continue) is then a purely kernel-free engineering
candidate. It is explicitly NOT a kernel result, would be reported (and possibly
offered upstream) as such, and is not run under this programme's ceilings without a
separate maintainer decision. [STIPULATED: ASM-2018]

**MAINTAINER GATE 2:** if F1-B.1 indicates a power/granularity failure and F1-B.2
also lands within noise, any *expanded-N re-test* is a new spend decision — one
re-test maximum, never silently inside the Branch-B ceiling.

### 5.3 Wording [STIPULATED: ASM-2022]

- Licensed PASS (salvage): "Kernel concept labels add measurable expert-residency
  value over kernel-free content conditioning at this model/box on labelled
  workloads" — sign only, all ASM-1987 caps apply.
- Null: "Expert-routing structure at this model is exploitable but concept-agnostic;
  the kernel earned no increment" — recorded as a content-not-structure datum, with
  the same prominence discipline as §4.5.

### 5.4 Cost [EXTRAPOLATION: ASM-2021]

F1-B.1 ≈ $3–5; F1-B.2 ≈ 14,000 decode tokens ≈ 16–43 h ≈ $11–30. **Ceiling: $60.**
**[SUPERSEDED by REVISION-1 §R6: B.1 expanded to 16+16 pairs, B.2 N power-derived
up to 96 → new ceiling $85; ASM-2041.]**

---

## 6. Branch C → F1-C: the honest pivot (both routing levers dead; F1-K unaffected)

### 6.1 Mechanical record first [STIPULATED: ASM-2019]

Register: G-B1 FAIL; B1a and B1b **dead-at-this-model-and-box**; the concept→expert
map has no exploitable target. The P0 TOPK shrink-sweep result, whatever it shows, is
a colibri-native (concept-free) observation and is recorded without any kernel
sentence attached. The trace dataset stays committed — dead levers do not orphan
their data (delegate-and-reanalyse discipline). F1-K's admissibility is untouched:
its gate never depended on native routing structure (§1.4).

### 6.2 What Branch C does NOT license [STIPULATED: ASM-2019]

The 1M-kernel scale gate does **not** rescue absent routing structure: if per-prompt
expert usage is indistinguishable at 24-cluster granularity, adding concepts to the
kernel adds labels, not router signal. Deferring B1a/B1b "until the big kernel
exists" would be an unregistered extrapolation and is explicitly disallowed as a
default. The defensible re-entries, each requiring a fresh probe-grade design, are:
(a) a different MoE host with independently documented expert specialisation, or
(b) a materially finer-grained conditioning signal — and (b) is speculation until
designed. [ASSESSMENT, disposition STIPULATED: ASM-2019]

### 6.3 The pivot menu — MAINTAINER GATE 3 (choice of pivot is the maintainer's, not this document's)

| Option | What it is | Cost inside ceiling |
|---|---|---|
| C-i (recommended for consideration) | **A1 gateway plumbing**: engine as grounding/verification layer at `openai_server.py` — pre-generation closure injection, post-generation claim checking, GBNF constrained decoding; zero C changes; plumbing demonstration ONLY (thesis experiments stay gated on ENGINE-INF E0 + coverage + blocking pilot, ASM-1982 carried) | ≤ $40 keep-alive + demo |
| C-ii | **Park the routing substrate**: after F1-K completes, terminate the instance, retain the S3 artifact ($8.5/mo) and committed traces; the routing track closes until a re-entry design exists | ~$0 |
| C-iii | B2 acceptance measurement only (as §4.6), then park | ≤ $20 |

No option moves any thesis verdict; C-i produces no verdict-bearing number at all.
[STIPULATED: ASM-2019]

---

## 7. Shared measurement protocol (routing arms; F1-K deltas noted) [STIPULATED: ASM-2016]

### 7.1 Knobs

| Knob | Setting | Why |
|---|---|---|
| `PIN=<file>` | per-arm pin list (the routing intervention) | the zero-C-change integration point |
| `PIN_GB` | identical across all pinned arms within a branch; value fixed at bring-up from measured free RAM after dense weights + OS; recorded in the run manifest | matched-budget discipline — the entire comparison is void without it |
| `TOPK` / `TOPP` | config defaults, untouched in F1 | F1's routing arms test residency, not routing changes; TOPK belongs to B1b's own prereg |
| `STATS` | on (per-layer expert-usage histograms) | fingerprints + map building |
| `DIRECT` | routing arms — **primary configuration: on** (O_DIRECT; every miss pays NVMe) with page cache dropped between arms; **secondary configuration: off** (realistic L2), reported separately, never pooled. F1-K — off (quality endpoints; speed is not the measurement) | attribution: with 64 GB RAM the OS page cache is a policy-free L2 that blurs arm differences |
| `PILOT` | off | measured neutral on saturated disk; removes a variance source |
| `DRAFT` | 0 (greedy) | byte-identity invariants; determinism |
| `KAE` | unset in all routing arms; set per §2 in F1-K arms only | the routing levers are measured on the unmodified function |
| AUTOPIN / `.coli_usage` | enabled for arm a1 only; disabled (fresh state) elsewhere | a1 IS the deflator; leakage into other arms voids them |

Knob semantics are fetch-grade until re-verified from the checkout at bring-up
(ASM-1971 carried); any semantic surprise (e.g. `PIN_GB` not behaving as a hard
budget) halts the run for a protocol amendment BEFORE data collection, never after.

### 7.2 Run hygiene

Prompt order randomised per arm (seeded, logged); page cache dropped
(`drop_caches=3`) at every arm boundary and before every DIRECT-primary prompt;
arm order rotated across prompts to decorrelate thermal/background drift; every run
emits a manifest (binary hash, config hash, pin-file hashes, KaE sidecar + offset
table hashes where applicable, knob values, per-prompt/per-item counters) committed
with the results. All heavy work niced per box discipline.

### 7.3 Primary counter (routing arms)

Engine-reported expert miss-bytes per token (the deterministic counter), with iostat
device bytes as the cross-check; disagreement > 10% between counter and iostat on any
arm triggers instrument investigation before analysis.

### 7.4 Byte-identity checks

Routing arms: per prompt, SHA-256 over the decoded token-id sequence, compared across
all arms; a single mismatch voids the branch run (§4.4). F1-K: the off-concept guard
set must be byte-identical to b0 in every spliced arm (§2.5); a single mismatch voids
the F1-K run.

---

## 8. The scale gate, stated honestly [STIPULATED: ASM-2020, ASM-2033]

All three levers presuppose a concept map; what F1 can honestly use and what the full
claims need are different objects:

- **F1's minimal kernel/map (sufficient for every experiment above):** the probe's
  ~24 concept-stratified clusters, labelled by the existing <100-concept kernel, with
  WordNet lemma/gloss/synonym sets used ONLY to (i) author fresh surface-disjoint
  renderings within those clusters (routing arms) and (ii) expand the lexical trigger
  surface of the KaE gate (F1-K). WordNet supplies surface variation and triggers,
  not new concepts; word-level triggers conflate senses, which is why the A1/A2
  sub-casing (§3.2) and the sense-pair subgroup (§2.7) exist. Conditioning and gating
  need concept LABELS, not coverage (ASM-1983 carried); that is why F1 is runnable
  now — and why F1-K's n_min gate (§2.7) may bite if 24 concepts cannot reach 240
  benchmark items.
- **What the full claims need:** a ≥1M-concept, sense-split kernel (SCALE-1 S2) plus
  the runtime NL→concept mapper (the l3a parse wall), so that arbitrary unlabelled
  prompts can be conditioned/gated; for KaE additionally per-concept grounded content
  at that scale; and, for the only mechanism a topic model cannot replicate —
  conditioning on *entailed-but-unstated* concepts — engine closure at coverage
  (RULES-SCALE). Until then, every F1 result is scoped verbatim to "concept-labelled
  (or concept-covered) workloads at this model and box."

Nothing in F1 advances, and nothing in F1 waits on, the scale track: F1's role is to
find out — for hundreds of dollars at most — whether the concept→expert map and the
kernel-expert carrier are worth building at scale at all.

---

## 9. Cost and decision summary

**[Ceilings column SUPERSEDED by REVISION-1 §R6 (power-derived): K $450 / A $180 /
B $85 / C $40. Deflator column for F1-K REVISED per §R2 (d1 → d1-drng derangements).
Original table retained for the record.]**

| Experiment | Fires when | Primary endpoint | Deflator(s) that must be beaten | Ceiling |
|---|---|---|---|---|
| **F1-K KaE (PRIMARY)** | P0 lands + MAINTAINER GATE 0 (Law-1 amendment); independent of routing outcome | accuracy on the known-concept QA subset, ladder K-1/K-2/K-3 (≥ +3 pts, p<0.05 each rung) | d1 equal-capacity concept-agnostic content (rung 2) AND d2 plain-dictionary knull (rung 3); d0 placebo must NOT beat baseline | $250 |
| F1-A live pinning A/B | Branch A | miss-bytes/token, a3 vs both deflators, ≥10% median relative reduction, p<0.05 each | AUTOPIN (a1) AND embedding-cluster (a2) | $150 |
| F1-B salvage-or-kill | Branch B | additive miss-byte reduction of concept labels over kernel-free conditioner, ≥5%, p<0.05 | embedding-cluster conditioner (a2) | $60 |
| F1-C pivot | Branch C | none (no verdict-bearing number) | n/a | $40 |

MAINTAINER GATES, consolidated:

- **MAINTAINER GATE 0 (new, blocking F1-K only):** approve the scoped Law-1
  amendment (kernel-derived content vectors may enter activations only within the
  KaE track, only via the registered splice, deflator ladder mandatory) AND the
  ~150–200-line glm.c KaE patch (exceeds the P0 trace-dump C envelope; fork
  etiquette per ASM-1989).
- **MAINTAINER GATE 1 (the sign-off this document exists for):** approve the overall
  plan — F1-K primary + the routing decision tree — with the per-experiment ceilings
  **as revised power-derived in REVISION-1 §R6 (K $450 / A $180 / B $85 / C $40)**;
  thereafter F1-K runs on P0's landing (gate 0 permitting), the classifier
  fires mechanically, and each experiment runs without re-surfacing inside its
  ceiling. Sign-off additionally binds the FREEZE-GATE of §R5: no F1-K spend before
  the freeze manifest is committed.
- **MAINTAINER GATE 2:** Branch-B expanded-N re-test (one maximum) is a separate
  spend decision (§5.2).
- **MAINTAINER GATE 3:** Branch-C pivot choice C-i vs C-ii vs C-iii (§6.3).
- **MAINTAINER GATE 4 (carried from ASM-1989):** any further glm.c C change beyond
  the P0 trace-dump patch and the gate-0-approved KaE patch.

---

## 10. Self-check gate (governance)

Every load-bearing claim above carries MEASURED / LIT-BACKED / DERIVED / STIPULATED /
EXTRAPOLATION / ASSESSMENT; every design CHOICE is STIPULATED with an ASM id, never
smuggled as fact; the branch classifier, all thresholds, and the KaE ladder margins
are frozen BEFORE any routing-structure output is read (emission-timing declaration,
header); both outcome directions of every gate are worded in advance (§2.6, §2.7
ceiling-bound wording, §4.5, §5.3, §6.2); the deflator arms (d0/d1/d2/d3-text for
KaE; AUTOPIN + embedding-cluster for pinning) are mandatory before any
kernel-specific sentence, and the deflationary-null wording is pre-adopted in the
f2b/DECONF-B/RULES-2 form; the Law-1 conflict is surfaced as an explicit maintainer
gate rather than resolved by inference; claim caps are carried from ASM-1987 and
extended to KaE (ASM-2033); EXTRAPOLATION entries carry resolution paths and are
load-bearing nowhere; owner strings are role pseudonyms only. No frozen record,
verdict, encoder pin, or registered assumption is touched; no git action, no model
run, no spend occurs in this pass. Assumption block ASM-2010..2033 is emitted below
(range verified free at emission: central register tail ASM-1989; ENGINE-INF
companion claims 1990..2009; repo-wide grep for `ASM-2[0-9][0-9][0-9]` finds nothing
above ASM-2005); central registration in `registry/assumptions.jsonl` is the
coordinator's action, in the commit that lands this file, after the standing review
gate.

---

## §R — REVISION-1 (2026-07-13): cross-vendor review remediation

> **Status: PRE-REGISTRATION-QUALITY REVISION, awaiting maintainer sign-off (GATE 1)
> and the coordinator's re-review. No feasibility conclusion is stated here; no run,
> spend, or git action occurs in this pass.** Author: Fable, architecture-design role
> (designer-5), 2026-07-13.
>
> **Provenance.** Cross-vendor review `poc/gpt56-review/glm-design/REVIEW-SUMMARY.md`
> returned **FIX-FIRST with 5 blockers** [MEASURED: that file, read this tick]. Each
> blocker is remediated below (§R1–§R5), plus the classifier reconciliation (§R0) and
> the power-derived ceilings (§R6). Where §R conflicts with §§1–10, §R governs.
>
> **Emission-timing declaration for REVISION-1 [MEASURED: this repository, this
> tick]:** unlike the original emission, this revision is written AFTER reading
> fingerprint-level routing-structure output — specifically
> `poc/glm52-probe/results/routing-analysis-v2.json` (coordinator-verified) and the
> v1/v2 analysis provenance. Blindness is therefore no longer claimable for
> fingerprint-similarity quantities. Discipline consequence, stated in advance:
> REVISION-1 changes **no branch threshold, no branch condition, no endpoint
> direction, and no ladder margin**; every change below is a methodology remediation
> demanded verbatim by the review (scoring template, dose-exact deflator, power
> derivation, carrier-blind tuning, freeze mechanics) or a MEASURED-evidence
> registration (§R0). The still-unread quantities — P0.3 replay M_oracle / M_kernel,
> stats.tgz warm-throughput rows — remain unread at this revision.
> **ASM block claimed: ASM-2034..2042** (delta appendix, this file; owner
> designer-5). Range verified free at emission: central register tail ASM-2005;
> companion blocks in docs claim up to ASM-2033; repo-wide grep finds nothing above
> ASM-2033.

### R0. New MEASURED evidence and the classifier reconciliation

**The evidence [MEASURED: `poc/glm52-probe/results/routing-analysis-v2.json`,
sha256 e9d6813f…57cc, seed 20260712, n=24 fingerprints, 10,000 shuffles]:** the
original P0 analysis reported p = 0.33 for concept→routing structure; that number
was an artifact of a degenerate cyclic-shift permutation scheme (non-exchangeable
null), not a property of the data. The corrected pre-registered test form (≥10,000
random label shuffles, as ASM-2013 specified) on the SAME committed fingerprints
yields: raw cosine within-concept 0.9977 vs across 0.9545, p = 0.0001; after
removing the universal routing component (93.9% of histogram mass), MEAN-CENTERED
cosine within 0.9119 vs across −0.0740, p = 0.0001; sense-pair separation:
*break* Δ_centered = 0.1955, p = 0.0029; *bank* Δ_centered = 0.3259, p = 0.1026
(direction as predicted, not established at n=6).

**What this does and does not change [STIPULATED: ASM-2034]:**

1. **p_perm leg of Branch A: measured SATISFIED.** The v2 computation IS the
   registered p_perm quantity of §3.1/ASM-2013 executed correctly (the v1
   cyclic-shift run is recorded VOID as an instrument defect, superseded, not
   averaged). p_perm = 0.0001 < 0.05 under both the raw and mean-centered metric, so
   the branch outcome is invariant to metric choice and no threshold amendment is
   needed or made.
2. **The classifier does NOT fire yet.** Branch A requires the conjunction
   M_kernel ≥ 10% AND p_perm < 0.05; Branch B/C turn on M_oracle. **M_kernel and
   M_oracle — the kernel-SPECIFICITY question, kernel-concept pin vs the STRONGER of
   global-hot and embedding-cluster deflators in P0.3 replay miss-bytes — remain
   OPEN and unread.** Strong concept structure in routing does not establish that
   KERNEL labelling exploits it beyond a generic embedding cluster; that is exactly
   the deflator leg the classifier exists to decide. Branch selection waits on the
   replay, unchanged.
3. **SensePairSep:** computable from the same fingerprints under its frozen ≥ 0.75
   rule when the classifier fires; the v2 sense-pair numbers are recorded as
   descriptive direction only (break separates, bank not established at its n).
4. **F1-K is unmoved.** F1-K was unconditional on routing structure by construction
   (§1.4) and stays so; the v2 result strengthens the motivation for the routing
   levers' Branch-A path but confers no license on any arm, rung, or claim. G-route
   (§2.3) remains noted-not-scheduled, admissible only after a Branch-A
   classification.
5. **One instrument-validity consequence** (declared, since blindness is broken):
   all NEW fingerprint-similarity comparisons defined in this design whose data does
   not yet exist (F1-B.1's routing-overlap metric, §R3.4) use MEAN-CENTERED cosine
   as primary and raw cosine as secondary, because the measured universal component
   (93.9% of mass) compresses raw cosine into a 0.95–1.00 band. This choice is made
   on instrument grounds from P0 data before any F1-B data exists.

### R1. BLOCKER 1 — scoring template and REPLACE non-inferiority [STIPULATED: ASM-2035, ASM-2037]

**R1.1 Frozen candidate-independent scoring (supersedes the scoring clause of §2.7
/ ASM-2030).** Per-option continuation likelihood is abandoned — it is
length/distractor-biased and lets gating interact with option text differently per
candidate. Replacement, frozen before any run:

- **Template (frozen bytes, hashed in the freeze manifest §R5):** one fixed prompt
  rendering per item — instruction header, question, the k options rendered as
  labelled lines (`A. …` … `D. …`) in their PUBLISHED order (no per-arm or per-pass
  reordering), then the fixed answer cue ending at the label position. One template
  for every item, every arm, every pass; template text contains no concept triggers
  (verified mechanically against the trigger map at freeze).
- **Score:** ONE prefill per item per arm; read next-token logits at the answer
  position; the model's answer = argmax over the k answer-LABEL token logprobs
  (single-token labels; verified single-token under the tokenizer at freeze).
  Deterministic tie-break: lowest label index, tie logged. The scored token set is
  CANDIDATE-INDEPENDENT and length-invariant by construction: option content can
  influence the score only through the shared prefill, which is byte-identical
  across arms except for the splice itself.
- **Gate/option interaction (also resolves the option-dependent-gating part of
  Blocker 4):** gate spans are computed ONCE per item on the frozen full template
  (question + options), frozen per item in the sidecar, and identical across every
  arm and pass by construction — there are no per-option continuations left to gate
  differently. Spans may fall inside option text; if so they apply identically in
  all arms. The label tokens themselves are never triggers (checked at freeze).
- **Position-bias check (descriptive):** distribution of predicted labels vs gold
  labels reported per arm; a gross skew is an instrument note, not an endpoint.
- **Cost consequence:** scoring drops from k prefills per item-arm to 1 — this is
  what makes the power-derived n of §R3 affordable (§R6).

**R1.2 REPLACE non-inferiority, confidence-bound (supersedes the point-estimate
rule of §2.5 / ASM-2028).** REPLACE (admitted only after ADD passes K-1) PASSES
non-inferiority iff the lower bound of the one-sided 95% CI on the paired accuracy
difference (REPLACE − ADD) — cluster-level BCa bootstrap over concept clusters,
10,000 resamples, consistent with §R3's primary analysis — is **> −2 accuracy
points** (Δ_NI = 2 pts, pre-registered), AND measured expert-byte saving on gated
tokens > 0. A point estimate above −2 with a CI crossing it is a FAIL ("not shown
non-inferior"), worded in advance. REPLACE's affordability at the power-required n
is checked at bring-up; if unaffordable it is DEFERRED per §R6's degradation order,
never run underpowered.

### R2. BLOCKER 2 — dose-exact deflator: concept-label derangements [STIPULATED: ASM-2036]

The generic-paragraph d1 arm is REMOVED: its offsets differ from K in content
length, norm profile, covariance structure, and construction provenance — it
matches vector dimensionality, not intervention dose (the review's point, accepted
in full). Its replacement, **d1-drng**, is the knull "kernel content, not any
content" bar made dose-exact:

- **Construction:** the IDENTICAL carrier set {K[c][l]} as the treatment arm, with
  the concept→carrier assignment permuted by a seeded DERANGEMENT over the concepts
  present in the test set (no concept keeps its own carrier). **R = 5 independent
  derangement passes** (seeds enumerated in the freeze manifest; disjoint from the
  2 pilot derangements of §R4). The ONLY thing that differs from arm K is whether
  the label→carrier mapping is the true kernel one.
- **Layerwise norm matching:** a deranged carrier takes its DIRECTION from the
  donor concept and its NORM from the recipient: at each (concept c, layer l) the
  assigned vector is rescaled to ‖v^K_{c,l}‖, so the injected dose profile per
  gated position is numerically identical across K and every derangement. Raw
  (pre-rescale) norms are logged in the manifest.
- **Norm handling for ALL arms (resolves the raw-carrier-norm part of Blocker 4):**
  reference norm at each (c, l) is ‖v^K_{c,l}‖; d0's random vector and d2's
  dictionary offsets are likewise rescaled per (c, l) to the reference; g applies
  after rescaling; raw and post-rescale norms for every arm are manifest entries.
  Residual content-covariance differences are then exactly what rungs K-2/K-3 test.
- **Inference for rung K-2:** primary = the §R3 cluster-level paired test of K vs
  the per-item MEAN correctness over the R derangement passes, α = 0.05, +3-pt
  floor as before. Secondary (exactness check, descriptive at R = 5): K's rank
  among the R derangement passes on overall accuracy (best-of-6 ⇒ nominal 0.167;
  stated so the rank cannot be over-read).
- d0 (placebo, run-voiding), d2 (plain-dictionary knull, rung K-3), d3-text
  (prompt-seam bridge) are RETAINED unchanged in role.

### R3. BLOCKER 3 — cluster-aware power, derived n/N, powered diagnostics [STIPULATED: ASM-2038]

Items and prompts cluster by concept (same carrier ⇒ correlated treatment effects),
so item-level tests overstate information. All primary analyses and all sample
sizes are re-derived cluster-aware; ceilings follow in §R6.

**R3.1 Primary analysis form (all F1-K rungs; F1-A/B analogues in R3.3):**
per-concept-cluster mean of the paired per-item differences; one-sided
CLUSTER-LEVEL sign-flip permutation test (10,000 resamples), α = 0.05; effect
floor unchanged (observed paired lift ≥ +3 accuracy points); cluster-level BCa 95%
CI reported for every primary contrast.

**R3.2 F1-K power derivation (frozen formula + dev-measured inputs).** With C
clusters of average m items, paired-difference discordance rate δ, and
within-cluster ICC ρ of paired differences, SE(mean paired lift) ≈
√((ρδ + δ/m)/C). Design target: **SE ≤ 1.2 points**, which simultaneously gives
(i) ≥80% power at α = 0.05 (one-sided) to detect a true +3-point paired effect
under the test alone, and (ii) ≈80% joint power for the dual criterion
(p < 0.05 AND observed ≥ +3) at a true +4-point effect [DERIVED: normal
approximation, z₀.₉₅ = 1.645, z₀.₈₀ = 0.842, 2.487·1.206 ≈ 3.0].
Required clusters: **C ≥ (ρδ + δ/m) / (0.012)²**.

- **Planning point** (δ = 0.10, ρ = 0.03, m = 15 — assumption band stated for
  sign-off pricing only, δ ∈ [0.05, 0.15], ρ ∈ [0, 0.05]): C ≥ 67, n ≈ 1,005.
  Band over the stated assumptions: n ≈ 360–1,440 (the high corner exceeds the
  kernel's concept count and resolves ≈ +3.4 pts at C = 96, reported as such).
  **Hard cap n_max = 1,440.**
  ≥216 items is confirmed underpowered for +3 pts (at δ = 0.10 it resolves ~7 pts)
  — the review's point, accepted.
- **Consequences for the map (coverage):** ~24 concepts cannot supply C ≥ 67; the
  trigger map is EXPANDED to all kernel concepts with registered explications
  (target C ∈ [48, 96]; the kernel's <100 concepts bound C above). At C = 48 the
  detectable effect at 80% power is ≈ +3.5 pts (δ = 0.10, ρ = 0.03, m = 15) —
  reported as such if that is what coverage yields. **Power gate (hard):** if the
  mechanical filter cannot reach C ≥ 48 with m ≥ 8 within n_max, F1-K does not run
  and returns to the maintainer with the measured coverage-vs-power shortfall
  (this subsumes the old n_min = 240 gate, which is superseded).
- **Dev-measured inputs, frozen before the test run:** dev split expanded to 96
  items (stratified ≥1 per cluster; still disjoint from test and construction).
  After the §R4 pilot freezes (L, g): δ̂ = discordance rate between b0 and the
  frozen-config panel arms on dev-96, taken at its one-sided 80% upper confidence
  bound; ρ̂ = cluster ICC of dev paired differences, floored at 0.02. n_required =
  smallest n with SE ≤ 1.2 pts at (δ̂_U, ρ̂_floor, achievable C). n_required, its
  inputs, and the resulting cost projection are freeze-manifest entries (§R5); n
  is never reduced below n_required by any fallback.
- **REPLACE NI power:** same formula with Δ_NI = 2 pts and the REPLACE-vs-ADD δ̂
  measured on dev; run only if affordable (§R6).

**R3.3 F1-A / F1-B.2 sample size (supersedes N = 48 as a choice).** N is derived
from MEASURED replay variance, available before either fires: σ_d = SD of
per-prompt paired relative miss-byte differences between the corresponding replay
policies in P0.3; DEFF = 1 + (m̄ − 1)·ρ̂ over concept clusters (m̄ = N/C).
**N_required = ceil(DEFF · (1.645 + 0.842)² · (σ_d/Δ)²)** with Δ = 10% relative
(F1-A, each licensed comparison) or 5% additive (F1-B.2). **N ∈ [48, 96]**: 48 is
the floor (stratification minimum, ≥2 per cluster), 96 the affordability cap; if
N_required > 96, the branch experiment returns to the maintainer as underpowered
at admissible cost (power gate) instead of running. Primary analysis becomes
cluster-level sign-flip (as R3.1) with cluster BCa CIs; the ≥10%/≥5% median floors
and the conjunction rule of §4.4 are unchanged.

**R3.4 F1-B.1 diagnostic, powered (supersedes 6+6).** 16 same-concept
surface-disjoint paraphrase pairs + 16 surface-overlapping concept-distinct pairs;
endpoint = per-pair routing-overlap (mean-centered fingerprint cosine, per §R0.5;
raw cosine secondary); one-sided two-sample permutation, α = 0.05; powered ≥80%
for standardized effect d ≥ 1.0 [DERIVED: n_per_group ≈ 2·(1.645+0.842)²/d² ≈ 13
< 16]. The diagnostic claims only to detect the GROSS surface-form signature;
smaller effects fall through to F1-B.2 by design — stated so a B.1 pass-through
cannot be read as evidence of absence.

### R4. BLOCKER 4 — carrier-blind tuning and gate resolution [STIPULATED: ASM-2040]

**The defect accepted:** selecting (L_KaE, g) by argmax of the K arm on dev, then
applying that configuration to controls, hands the treatment a differential
optimization advantage (winner's-curse asymmetry).

**Fix — carrier-blind selection:** the pilot grid (3 layer sets × 3 g values, on a
48-item stratified dev subset) is run over an UNLABELED CARRIER PANEL of three
tables: the true-K assignment and 2 seeded derangements of it (pilot-reserved
seeds, disjoint from R2's main-run seeds). The selection statistic is
**S(L, g) = unweighted mean dev accuracy across the three panel members**, with
the panel unlabeled in the selection code; S is invariant to which member is the
true mapping, so the choice cannot favour the true carrier. Tie-break: fewer
spliced layers, then lower g (least intervention). The argmax (L, g) is FROZEN in
the manifest and applied IDENTICALLY to every arm — K, all R derangements, d0, d2
(d3-text has no splice). Panel composition, seeds, per-member dev accuracies
(unblinded only AFTER the freeze), and S values are manifest entries.

**Gate resolution (completing Blocker 4's specification demands):**

- **Multi-concept overlap:** exactly ONE carrier per gated position (dose
  control — carriers are never summed). If spans overlap, precedence: longest
  trigger match, then earliest span start, then lowest concept id; items with any
  overlap are tagged `multi-concept` and reported as a descriptive subgroup.
- **Answer-option gating:** resolved structurally by §R1.1 — spans computed once
  per item on the frozen template, identical across arms and passes; label tokens
  are never triggers.
- **Raw carrier norms:** per §R2 — raw norms logged; every carrier rescaled per
  (c, l) to ‖v^K_{c,l}‖; g applied post-rescale.

### R5. BLOCKER 5 — the pre-run FREEZE-GATE [STIPULATED: ASM-2039]

Maintainer sign-off (GATE 1) approves the RULES in this document; before any F1-K
spend, the coordinator commits a **freeze manifest** that mechanically instantiates
them. F1-K may not start without it; any post-freeze deviation is a protocol
amendment BEFORE further data collection, logged, never silent. Manifest contents:

1. scoring template bytes + sha256; label token ids (single-token verification);
   tie-break rule; option-order rule (§R1.1);
2. trigger-map version hash; gate precedence rules; per-item frozen span sidecars'
   hash (§R4);
3. carrier tables: construction-context list hash, raw + rescaled norms for every
   arm, reference-norm rule (§R2);
4. derangement seeds: pilot (2) and main (5), enumerated (§R2, §R4);
5. carrier-blind tuning record: panel composition, S(L, g) table, frozen (L, g)
   (§R4);
6. power record: δ̂_U, ρ̂_floor, achieved C and m, n_required, the SE target, and
   the resulting cost projection vs ceiling (§R3.2), plus the REPLACE NI margin +
   CI method (§R1.2);
7. bring-up measurements: measured s/prefill; affordability check + any invoked
   degradation steps in §R6's pre-registered order;
8. the off-concept guard set (60 items) and dev/test item id lists (hashes).

Items 1–5 freeze before the pilot where applicable (1–4) or at pilot completion
(5); item 6 freezes before the test run; the test set stays untouched until all
eight entries are committed.

### R6. Power-derived ceilings and the degradation order [EXTRAPOLATION: ASM-2041]

Scoring is now 1 prefill per item per arm (§R1.1). Arm passes: b0, d0, d1-drng ×5,
d2, d3-text, K = 10 (+1 conditional REPLACE). Worst-case admissible volume
(n_max = 1,440): main 11 × 1,440 = 15,840 prefills; construction ≤ 96 concepts ×
16 × 2 = 3,072; pilot 27 × 48 + δ̂ passes ≈ 1,500; guard 60 × 11 = 660 → ≈ 21.1k
prefills. Planning point (n = 1,005): ≈ 16.3k prefills. Prefill seconds/item are
UNKNOWN until bring-up (union-of-experts prefill; the original §2.9 band implies
~30–100 s warm); at 30–100 s: planning point ≈ 136–452 h ≈ $94–312; worst case
≈ 176–586 h ≈ $121–404 at $0.69/h.

| Experiment | Power basis | New ceiling |
|---|---|---|
| **F1-K (PRIMARY)** | n_required from §R3.2 (cap 1,440), 10–11 passes, 1 prefill/item/arm; worst case ≈ $404 + restore/contingency | **$450** |
| F1-A | N ∈ [48, 96] from replay variance (§R3.3); 6 arms + a5 double-pass at N = 96 ≈ $49–138 | **$180** |
| F1-B | B.1 16+16 pairs ≈ $8–12; B.2 3 arms × N ≤ 96 ≈ $21–59 | **$85** |
| F1-C | unchanged (no verdict-bearing number) | **$40** |

Maximum realized path = F1-K + one branch ≤ **$630** (Branch-A path); ceilings sum
to $755 but branches are exclusive. **Pre-registered degradation order** if the
bring-up cost projection at n_required exceeds the F1-K ceiling: (1) R 5 → 3
(−2 × n prefills; rank check loses granularity, noted); (2) defer REPLACE;
(3) defer d3-text (K-seam question deferred, ladder rungs intact); (4) if still
over ceiling, STOP and return to the maintainer with the measured projection —
**n is never cut below n_required; no arm needed by a ladder rung (b0, d0,
d1-drng, d2, K) is ever dropped.**

### R7. Revision self-check

Every REVISION-1 change is tagged; every choice is STIPULATED with an ASM id in
the delta block (ASM-2034..2042); the one new MEASURED item carries file + hash +
seed; EXTRAPOLATIONs carry resolution paths and bear no load; no branch threshold,
endpoint direction, or ladder margin moved; the broken-blindness status is
declared, with the still-unread quantities named; both outcome directions of every
new test (NI fail wording, B.1 pass-through wording, power-gate returns) are
pre-worded; no feasibility conclusion is stated; no git action, run, or spend
occurs in this pass. Central registration of ASM-2034..2042 in
`registry/assumptions.jsonl` is the coordinator's action, in the commit that lands
this revision, after the standing review gate.

---

## Appendix — assumption block ASM-2010..2033 (registry-style; coordinator registers with the commit)

```json
{
 "_readme": [
  "GLM52-F1 follow-up-experiment assumption block ASM-2010..2033 — EMITTED by the Fable architecture-design agent designer-5 (2026-07-12) for central registration by the coordinator with the commit; registry/assumptions.jsonl is NOT touched by this pass (no git actions, design-role constraint).",
  "Range verified free at emission: central register tail ASM-1989; ENGINE-INF companion block claims ASM-1990..2009; repo-wide grep for ASM-2[0-9][0-9][0-9] finds nothing above ASM-2005. ASM-2010..2023 were emitted first; ASM-2024..2033 were added the same tick under the maintainer's Lever-C scope expansion, before any P0 routing-structure output was read.",
  "Companion design: docs/next/design/glm52-followup-experiment.md. Tags: MEASURED | LIT-BACKED | DERIVED | STIPULATED | EXTRAPOLATION. EXTRAPOLATION entries carry an explicit resolution_path and are load_bearing=false."
 ],
 "assumptions": [
  {
   "id": "ASM-2010",
   "tag": "STIPULATED",
   "claim": "F1 PLAN FRAMING: the GLM-5.2 follow-up comprises (i) F1-K Kernel-as-Expert as the PRIMARY experiment, unconditional on the probe's routing outcome, and (ii) the SECONDARY routing levers pre-registered as a three-branch decision tree (A: concept structure -> F1-A live pinning A/B; B: predictable-but-not-conceptual -> F1-B salvage-or-kill; C: no exploitable per-prompt structure -> F1-C pivot), with per-experiment cost ceilings, signed off ONCE by the maintainer; after sign-off F1-K runs on P0's landing (subject to MAINTAINER GATE 0), the branch classifier fires mechanically, and each experiment runs without re-surfacing inside its ceiling (no-pre-surface discipline). Sequencing on the one box: F1-K first, then the classified routing branch. Lever definitions carried from ASM-1973: B1a = concept-conditioned expert PINNING (quality-safe, speed); B1b = concept-guided expert DROP (function-changing, size+I/O), gated behind B1a's outcome and its own future prereg.",
   "rationale": "Pre-writing the primary experiment and all routing branches before the probe's outcome is known removes outcome-contingent design freedom, and a single sign-off keeps the maintainer loop off the critical path.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md header, §1-§3, §9; docs/next/design/glm52-kernel-integration-northstar.md §2.1-§2.2, §5.3",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2011",
   "tag": "MEASURED",
   "claim": "P0.1 BASELINE PARTIALS read from the running probe's probe-main.log (S3 artifact bucket, glm52-probe prefix) on 2026-07-12: expert-disk I/O = 80% of decode wall-time on the probe i4i.2xlarge; effective NVMe read bandwidth 3.33 GB/s; cold decode 0.09 tok/s. These are the ONLY probe numbers read before the F1 design, its branch classifier, and the KaE ladder were fixed; no routing-structure output (traces, replay, LOOKA, fingerprints, sense pairs, TOPK sweep) was read. All three values are re-verified against the final stats.tgz when the probe lands; a material revision (>10% on any value) triggers re-derivation of ASM-2012 before any branch runs.",
   "rationale": "Pins exactly what was known at design-freeze so the pre-registration's blindness to the classified quantity is auditable.",
   "backing_ref": "s3://kernel-of-truth-artifacts-361738333660/glm52-probe/probe-main.log (P0.1 baseline section); docs/next/design/glm52-followup-experiment.md header, §1.3",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2012",
   "tag": "STIPULATED",
   "claim": "F1 PHYSICS ENVELOPE (arithmetic over ASM-2011 + ASM-1974): with disk share d=0.8, removing fraction r of expert miss-bytes multiplies decode throughput by 1/(0.2+0.8(1-r)) — r=0.3 -> 1.32x, r=0.5 -> 1.67x, r=1 -> 5.0x HARD CEILING on this box; any larger claim on this box is arithmetic error. Bandwidth cross-check: 3.33 GB/s / ~11.4 GB/token bounds cold decode at ~0.29 tok/s vs 0.09 measured, implying ~31% effective read efficiency; therefore endpoints use engine miss-byte counters as primary and iostat as cross-check, never bandwidth arithmetic as measurement. For F1-K the same physics constrains EVALUATION cost only (prefill/loglik mandatory per ASM-1988), not the quality claim.",
   "rationale": "Fixes the interpretation envelope before results exist and demotes bandwidth arithmetic to a sanity band.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §1.3; docs/next/design/glm52-kernel-integration-northstar.md §1.2",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2013",
   "tag": "STIPULATED",
   "claim": "BRANCH CLASSIFIER (routing levers only; F1-K exempt by construction), frozen blind (no routing-structure output read at emission): from P0.3 offline replay at the probe box's matched RAM budget on held-out prompts, compute M_oracle (relative miss-byte reduction of oracle per-prompt pin vs global-hot pin), M_kernel (kernel-concept pin vs the STRONGER of global-hot and embedding-cluster deflators; the G-B1 quantity with its margin now frozen at exactly 10% as ASM-1976 required of this prereg), p_perm (one-sided permutation p, >=10,000 shuffles, within- vs across-concept-cluster fingerprint similarity), SensePairSep (fraction of registered sense-minimal-pair comparisons where cross-sense fingerprint distance exceeds within-sense). Branch A iff M_kernel>=10% AND p_perm<0.05 (sub-case A1 iff SensePairSep>=0.75, else A2: F1-A proceeds but sense-level granularity and sense-split B1b shards are recorded unsupported at this scale). Branch B iff not-A AND M_oracle>=15%. Branch C iff M_oracle<15% (ceiling speedup <~1.14x by ASM-2012 — beneath measurement dignity; both routing levers dead). Corrupt/irreproducible probe outputs -> classifier does not fire; probe re-runs within its own ceiling first.",
   "rationale": "A mechanical, exhaustive, pre-frozen classifier is what makes the single-sign-off tree legitimate; thresholds are stated with their arithmetic justification rather than tuned to data.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §3; registry ASM-1976 (G-B1 shape)",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2014",
   "tag": "STIPULATED",
   "claim": "F1-A DESIGN (Branch A, secondary-primary): six arms, fully paired on N=48 fresh held-out prompts (>=2 per probe concept cluster, incl. fresh sense-minimal pairs; 96 decode tokens; surface-disjoint from map-building prompts, no shared content 5-gram; KaE patch disabled in all routing arms): a0 LRU-only, a1 AUTOPIN (deflator 1), a2 embedding-cluster pin (deflator 2, knull-analog; pinned off-the-shelf sentence embedding frozen by content hash at bring-up; K = concept-cluster count), a3 kernel-concept pin (treatment; map from P0 trace train-split only), a4 random pin (floor), a5 oracle per-prompt pin (ceiling, never to-beat). Primary endpoint: expert miss-bytes per generated token (engine counter, iostat cross-check). Mandatory quality invariant: DRAFT=0 greedy outputs byte-identical across arms per prompt (SHA-256 over token ids); any divergence voids the run. Optional zero-marginal-cost rider: B2 lossless draft-acceptance measurement on kinship/sense items, skipped without penalty near ceiling.",
   "rationale": "Instantiates the parent P1 with exact arms and the byte-identity check that makes B1a's quality-safety mechanically verified rather than asserted.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §4; docs/next/design/glm52-kernel-integration-northstar.md §5.3",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2015",
   "tag": "STIPULATED",
   "claim": "F1 ROUTING-LEVER DEFLATOR MANDATE (ASM-1977 instantiated): no kernel-specific sentence is licensed in any routing branch unless the kernel arm beats BOTH colibri's AUTOPIN usage-history pinning AND the concept-agnostic embedding-cluster baseline at matched PIN_GB budget on held-out prompts; a tie with either deflator is reported with equal prominence under the pre-adopted content-not-structure wording (the f2b/DECONF-B/RULES-2 form). In Branch B the mandate takes the additive form: concept labels must add >=5% median relative miss-byte reduction OVER the kernel-free conditioner or the kernel claim is dead at this model/box. The KaE deflator ladder is registered separately (ASM-2029).",
   "rationale": "The programme's four content-not-structure deflations make the kernel-free baselines the entire evidential question at these seams; fixing the licensing rule before data exists prevents post-hoc softening.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §4.4-§4.5, §5.2-§5.3; registry ASM-1977",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2016",
   "tag": "STIPULATED",
   "claim": "F1 MEASUREMENT PROTOCOL on the colibri knobs: PIN=<per-arm file>; PIN_GB identical across pinned arms within a branch (fixed at bring-up from measured free RAM, recorded in the run manifest) — the comparison is VOID without matched budget; TOPK/TOPP untouched at config defaults (routing changes belong to B1b's own future prereg); STATS on (fingerprints + maps); DIRECT on as the PRIMARY configuration for routing arms (O_DIRECT so every miss pays NVMe) with page cache dropped at arm boundaries, DIRECT off as a separately-reported secondary realistic configuration, never pooled, and DIRECT off for F1-K (quality endpoints); PILOT off; DRAFT=0; KAE unset in all routing arms and set per the F1-K prereg in F1-K arms only; AUTOPIN/.coli_usage enabled for arm a1 only and fresh elsewhere (leakage voids affected arms). Prompt order randomised and seeded; arm order rotated; every run emits a committed manifest (binary/config/pin-file/KaE-table hashes, knob values, per-prompt counters). Knob semantics are fetch-grade until re-verified from the checkout at bring-up (ASM-1971 carried); any semantic surprise halts for a protocol amendment BEFORE data collection.",
   "rationale": "Attribution discipline: the page cache is a policy-free L2 that blurs arm differences, and AUTOPIN state leakage would contaminate the very deflator the design exists to respect.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §7; registry ASM-1971",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2017",
   "tag": "STIPULATED",
   "claim": "F1 ROUTING-ARM STATISTICS: statistical unit = prompt; fully paired design; primary analysis = paired one-sided permutation test on per-prompt miss-bytes/token (10,000 resamples), alpha=0.05, PLUS a pre-registered effect threshold of >=10% median relative miss-byte reduction (F1-A, each of a3-vs-a1 and a3-vs-a2 individually; PASS requires the conjunction — conservative, no multiplicity correction) or >=5% additive (F1-B.2, a2+K vs a2); N=48 fixed in advance, confidence intervals reported, no optional stopping, no post-hoc subgroups beyond pre-registered per-cluster descriptives; instrument check: engine-counter vs iostat disagreement >10% on any arm triggers investigation before analysis. F1-K statistics are registered separately (ASM-2030).",
   "rationale": "Small-N paired systems measurements need the effect-size floor and the fixed-N rule to keep a noisy pass from being manufactured by re-running.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §4.4, §5.2, §7.3",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2018",
   "tag": "STIPULATED",
   "claim": "F1-B DESIGN (Branch B salvage-or-kill), strictly ordered: F1-B.1 paraphrase diagnostic (6 same-concept surface-disjoint pairs vs 6 surface-overlapping concept-distinct pairs; if paraphrase pairs do NOT share routing while surface-matched pairs do, the structure is surface-form and the kernel routing lever is killed with no further spend); else F1-B.2 additive ablation (a2 kernel-free embedding-cluster pin vs a2+K adding kernel concept labels at the same budget vs a1 AUTOPIN; kill if additive gain <5% median or p>=0.05; salvage -> scoped F1-A rerun inside the remaining ceiling). A kernel-free prefix-fingerprint pinning policy (16-token prefix, STATS harvest, pin, continue) that survives a kill is explicitly a NON-kernel engineering result, reported as such, and not pursued under this programme's ceilings without a separate maintainer decision.",
   "rationale": "Branch B is where wishful reading is most likely; the ordered diagnostic separates surface-form structure from power failure before any live spend, and the non-kernel salvage is firewalled from kernel credit.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §5",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2019",
   "tag": "STIPULATED",
   "claim": "F1-C DISPOSITION (Branch C): register G-B1 FAIL; B1a AND B1b recorded dead-at-this-model-and-box; the TOPK sweep result is recorded as a colibri-native concept-free observation with no kernel sentence attached; committed traces are retained for re-analysis; F1-K's admissibility is UNTOUCHED (its gate never depended on native routing structure). The 1M-kernel scale gate does NOT rescue absent routing structure (more concepts add labels, not router signal), so deferral-to-scale is disallowed as a default; defensible re-entries (different MoE host with documented expert specialisation; materially finer conditioning signal) each require a fresh probe-grade design. Pivot menu — the choice is a MAINTAINER decision: C-i A1 gateway plumbing demonstration (zero C changes; thesis experiments remain gated per ASM-1982; <=$40), C-ii park the routing substrate after F1-K completes (terminate instance, keep S3 artifact, ~$0), C-iii B2 acceptance measurement then park (<=$20). No option moves any thesis verdict.",
   "rationale": "Pre-writing the kill branch with its non-rescue clause prevents the commonest failure mode of dead levers: indefinite deferral disguised as patience.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §6; registry ASM-1976, ASM-1982",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2020",
   "tag": "STIPULATED",
   "claim": "F1 SCALE GATE (routing levers): F1's minimal kernel/map is the probe's ~24 concept-stratified clusters labelled by the existing <100-concept kernel, with WordNet sense glosses/synonym sets used ONLY to author fresh surface-disjoint renderings inside those clusters (surface variation, not new concepts; word-level/sense-level caution inherited from the sense-split track and handled by the A1/A2 sub-casing). The FULL B1a/B1b claim additionally requires a >=1M-concept sense-split kernel (SCALE-1 S2), the runtime NL->concept mapper (the l3a parse wall), and — for the one mechanism a topic model cannot replicate, conditioning on entailed-but-unstated concepts — engine closure at coverage (RULES-SCALE). Every F1 routing result is scoped verbatim to concept-labelled workloads at this model and box. KaE's scale gate is registered at ASM-2033.",
   "rationale": "Separates what is runnable now (labels, not coverage) from what the north-star claim needs, so no F1 sentence can be quoted beyond its scope.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §8; registry ASM-1983; docs/next/design/large-kernel-scale-track.md",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2021",
   "tag": "EXTRAPOLATION",
   "claim": "F1 ROUTING-ARM COST BANDS at i4i.2xlarge ~$0.69/h on-demand: F1-A ~27,650 decode tokens across six arms at a warm 0.09-0.25 tok/s -> 31-85 instance-hours ~= $21-59, ceiling $150; F1-B.1 ~$3-5 and F1-B.2 ~16-43h ~= $11-30, ceiling $60; F1-C <=$40 (pivot-dependent); S3 retention $8.5/mo continues throughout. Warm-throughput band is a projection until stats.tgz is read. No band is a premise or a commitment; ceilings, not estimates, bound spend. F1-K costs are registered at ASM-2032.",
   "rationale": "Prices the maintainer decision without letting an estimate masquerade as a measurement.",
   "resolution_path": "Instance receipts + the warm-throughput rows of the probe's final stats.tgz; bands replaced by measured values in the branch run report.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §4.7, §5.4, §6.3, §9",
   "load_bearing": false,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2022",
   "tag": "STIPULATED",
   "claim": "F1 ROUTING-LEVER CLAIM CAPS AND PRE-ADOPTED WORDING (ASM-1987 carried): a Branch-A PASS licenses at most 'concept-conditioned expert pinning reduced expert I/O on concept-labelled workloads at this model and box, beyond both usage-history and topic-cluster pinning at matched RAM budget, with byte-identical outputs' — sign not slope; a Branch-B salvage licenses at most the additive-value analogue; every null takes the content-not-structure wording at equal prominence. Nothing in any F1 routing branch licenses an intelligence, efficiency-thesis, parity, or cost claim, and no F1 routing outcome moves the CORRECTNESS or EFFICIENCY synthesis verdicts, which remain INCONCLUSIVE-PENDING under their own designated experiments. KaE claim caps are registered at ASM-2033.",
   "rationale": "GLM-5.2 numbers will be quotable; the cap is registered before any exists.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §4.5, §5.3, §6; registry ASM-1987",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2023",
   "tag": "STIPULATED",
   "claim": "F1 MAINTAINER GATES: (0) the scoped Law-1 amendment + the ~150-200-line glm.c KaE patch approval, blocking F1-K only (ASM-2025/2031); (1) the single plan sign-off — F1-K primary + routing decision tree + per-experiment ceilings (K $250 / A $150 / B $60 / C $40); after approval F1-K runs on P0's landing (gate 0 permitting), the classifier fires mechanically, and each experiment runs without re-surfacing inside its ceiling; (2) any Branch-B expanded-N re-test (one maximum) is a separate spend decision; (3) the Branch-C pivot choice C-i/C-ii/C-iii; (4) carried from ASM-1989, any further glm.c C change beyond the P0 trace-dump patch and the gate-0-approved KaE patch. Each is surfaced as a threaded issue per the maintainer-decisions-as-issues practice when actionable; none is decided in this document.",
   "rationale": "Separates what the designer proposes from what only the maintainer may decide, and makes the no-pre-surface boundary explicit on both sides.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §2.2, §2.8, §4.7, §5.2, §6.3, §9",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2024",
   "tag": "STIPULATED",
   "claim": "LEVER C DEFINITION AND PRIMACY (maintainer scope expansion, this tick): Kernel-as-Expert (KaE) — for tokens whose context maps to a kernel-grounded concept via a training-free external gate, splice a small per-concept grounded content-carrier into GLM-5.2's MoE output, ADD (alongside native experts; pure quality) or REPLACE (in place of the lowest-weight routed expert; quality + per-token I/O saving). KaE is the PRIMARY F1 experiment, is a CORRECTNESS-thesis test at 744B scale, is the architectural descendant of f2b-transfer (+0.25 content lift through a thin interface) and DECONF-B (content-not-structure attribution), and is UNCONDITIONAL on the probe's routing outcome because its gate is external, not router-based. 'Kernel' is used loosely and the design tests grounded CONTENT, not kernel structure; the ladder of ASM-2029 keeps every claim at exactly the rung it earned. Hypothesis (stated, not asserted): on concept-covered QA, grounding corrects items GLM-5.2 misremembers; the win, if any, is correction-where-wrong, not new capability.",
   "rationale": "The maintainer's stated goal (A) needs a quality seam; anchoring it to the programme's one audited affirmative and pre-declaring the content-not-structure framing keeps the strongest lever inside the honesty discipline.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §1.1, §2.1; README 'Experiment summary' (f2b-transfer, DECONF-B rows)",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2025",
   "tag": "STIPULATED",
   "claim": "KaE LAW-1 INTERACTION: house Law-1 (interface-locality — no kernel vector enters a model's activations) as stated PROHIBITS KaE's carrier, which writes into the residual stream. F1-K therefore requires an explicit, scoped, registered Law-1 amendment BEFORE any run: kernel-derived content vectors may enter activations ONLY within the KaE track, ONLY via the registered moe() splice, with the ASM-2029 deflator ladder mandatory. The maintainer's scope-expansion instruction signals intent but is not the amendment; the amendment is MAINTAINER GATE 0 and must be a registry event. Without it F1-K does not run and the remainder of F1 is unaffected.",
   "rationale": "A standing house law must be amended explicitly, not overridden by inference from a task brief; surfacing the conflict as a named gate is the only honest resolution available to a design pass.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §2.2; docs/next/design/DDC.md §1.2 (Law-1 statement); registry ASM-1981 (prior Law-1-motivated deferral)",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2026",
   "tag": "STIPULATED",
   "claim": "KaE GATING + SPLICE (crux 1), all training-free, native router untouched: PRIMARY gate G-lex = harness-side lexical phrase->concept matcher (the ~24 probe concepts, trigger surface expanded by WordNet lemma/derivational sets) emitting per-position concept spans via a KAE= sidecar file; REGISTERED VARIANT G-emb = per-token hidden-state cosine against per-concept anchor vectors (means from plain forward passes) at the splice layer, threshold calibrated on dev to match G-lex firing rate, run only budget-permitting; NOTED-NOT-SCHEDULED G-route (fires on native router weight mass over concept-associated experts) admissible only after a Branch-A classification. SPLICE: inside colibri moe() (reported at glm.c:1270; fetch-grade, re-verified at bring-up) after the routed top-8 weighted sum + shared expert, before residual writeback: ADD y += g*K[c][l]; REPLACE skips the lowest-sigmoid-weight top-8 expert and adds w_dropped*K[c][l]. LAYER SET: pre-registered dev pilot over L1={one mid-stack MoE layer ~40} / L2={4 evenly spaced mid-late} / L3={all MoE layers, reduced g}, crossed with g in {0.5,1.0,2.0}x mean native expert weight; argmax dev configuration FROZEN before the main run. Known honest weakness: word-level triggers conflate senses (sense-split track defect); sense-minimal-pair items are a tagged subgroup.",
   "rationale": "The gate must not touch the router (no retraining, per programme ethos) and must be auditable; a lexical sidecar gate is deterministic and byte-replayable, with the embedding gate as the registered generalisation.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §2.3; coordinator brief this tick (moe() location)",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2027",
   "tag": "STIPULATED",
   "claim": "KaE CARRIER (crux 2): ADOPTED = per-concept per-layer definition offsets v_{c,l}, the mean hidden-state difference at gated positions between contexts WITH the kernel explication of c prepended and matched contexts WITHOUT (m=16 construction contexts per concept, disjoint from all evaluation items; forward passes + arithmetic only, no gradients; storage ~0.6-44 MB). Deflator carriers are built by the IDENTICAL procedure with substituted prepend-content; d0 is a norm-matched random vector. REJECTED for F1-K: any trained LM/MLP expert or learned projection (training intervention outside the programme's tier). DEFERRED: decoded kernel concept vectors projected into activations (the ASM-1981/B3 objection — foreign vectors the stack was never trained to read). BRIDGE CONTROL d3-text: kernel explication prepended as prompt text, no splice — measures whether the in-routing seam adds anything over f2b-transfer's prompt seam. Steering-vector/task-arithmetic literature backs the construction shape at abstract level only (not source-verified this tick).",
   "rationale": "The offset construction is the only carrier that is simultaneously training-free, dimension-native, capacity-matchable across deflator arms, and a faithful in-activation transport of the exact content mechanism f2b-transfer already validated at the prompt boundary.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §2.4",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2028",
   "tag": "STIPULATED",
   "claim": "KaE ADD vs REPLACE (crux 3): ADD (y += g*K[c][l], native experts intact) is the pure-quality mode and runs FIRST; REPLACE (drop lowest-weight routed expert on gated tokens, K takes its weight; quality + one fewer expert load per gated token-layer) is ADMITTED only after ADD passes ladder rung K-1. REPLACE endpoints: paired accuracy non-inferiority vs ADD (>= ADD - 2 pts) AND measured expert-byte saving > 0 on gated tokens; failing either records 'removal costs more than it saves'. OFF-CONCEPT GUARD (both modes): the gate never fires off-concept, so a 60-item off-concept subset must be byte-identical to baseline (SHA-256 over token ids); any mismatch VOIDS the F1-K run.",
   "rationale": "Removal is only worth its quality risk once the addition is shown to carry value, and the byte-identity guard makes 'off-concept harmless' a mechanical fact rather than an assumption.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §2.5, §7.4",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2029",
   "tag": "STIPULATED",
   "claim": "KaE DEFLATOR LADDER (the knull discipline, mandatory; all arms same gate/splice/layers/g, differing ONLY in carrier content, all built by the ASM-2027 construction): b0 unmodified baseline; d0 norm-matched random vector (PLACEBO — if d0 beats b0 the run is VOIDED as noise-sensitive instrumentation); d1 equal-capacity CONCEPT-AGNOSTIC content offsets (generic encyclopedic paragraphs unrelated to the gated concept) — the 'any extra content helps' arm that capped f2b/DECONF-B/RULES-2; d2 plain-dictionary definitions of the SAME concepts (the knull proper); d3-text prompt-injection bridge control; K kernel explication offsets. LICENSING LADDER, each rung at the ASM-2030 test and margin, failing rung n caps the claim at rung n-1: K-1 K>b0 ('content injection at the MoE seam lifts accuracy on concept-covered QA at this model/box'); K-2 K>d1 ('concept-ALIGNED content beats equal-capacity generic content at this seam'); K-3 K>d2 ('kernel-authored explications beat plain-dictionary definitions at this seam' — the first kernel-specific content-seam sentence the programme could earn; a K~d2 tie is the modal expectation on the four-deflation record and is reported at equal prominence). K vs d3-text is a descriptive mechanism finding, both directions pre-worded. No rung licenses an intelligence, parity, or general-capability claim.",
   "rationale": "Without the ladder a KaE lift would be unattributable among perturbation, content-in-general, concept alignment, and kernel authorship; the ladder is the entire evidential content of the experiment.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §2.6; README 'Experiment summary' (knull, DECONF-B, RULES-2 rows)",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2030",
   "tag": "STIPULATED",
   "claim": "KaE QA PROTOCOL: known-concept subset = MMLU items whose question+options lexically match >=1 trigger lemma of the phrase->concept map, supplemented mechanically (same filter) from a pre-registered pool (ARC-Easy/Challenge, OpenBookQA, CommonsenseQA) if MMLU alone is insufficient; HARD GATE n_min=240 pooled items or F1-K does not run and returns to the maintainer with the measured coverage shortfall; subset composition reported verbatim. Splits: dev=24 (pilot) + 60 off-concept guard; test >=216, untouched until arms freeze; construction contexts disjoint from all. Scoring: per-option loglikelihood via prefill/echo+logprobs (ASM-1988 mitigation; generative scoring unaffordable at 0.09 tok/s), argmax=answer. Statistics: unit=item, fully paired; paired one-sided permutation on per-item correctness, 10,000 resamples, alpha=0.05, effect floor >= +3 accuracy points PER LADDER RUNG; flip matrix (corrections vs regressions) = mechanism secondary; baseline-wrong subgroup DESCRIPTIVE ONLY (selection on errors regresses to the mean under any perturbation — d0 is the control); honesty-first penalised score a named secondary descriptive; fixed n, no optional stopping. CEILING-BOUND WORDING pre-adopted: if b0 subset accuracy >95%, headroom < the effect floor and the result is reported 'ceiling-bound at this subset', not a lever null.",
   "rationale": "The subset filter, minimum-n gate, paired flip analysis, and ceiling-bound wording are each required to keep a 24-concept trigger map from producing an underpowered, skewed, or headroom-artifact result that reads as a verdict.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §2.7; registry ASM-1988",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2031",
   "tag": "STIPULATED",
   "claim": "KaE COLIBRI FEASIBILITY ENVELOPE: the patch is a single-file glm.c edit kept as an in-repo diff — sidecar+offset-table loader (~60 lines), moe() splice ADD/REPLACE (~40 lines), hidden-state dump mode for carrier construction (~50 lines), optional G-emb gate (~50 lines); ~150-200 lines total in one function plus a loader, estimated one agent-day on the instance. This EXCEEDS the P0 trace-dump-only C envelope (ASM-1986/1989) and therefore rides MAINTAINER GATE 0 with the Law-1 amendment; fork-vs-upstream etiquette carried from ASM-1989 (nothing offered upstream without a separate decision). The moe() location (glm.c:1270) and router semantics (logits -> sigmoid+bias -> top-8 -> weighted sum + shared expert) are coordinator-supplied fetch-grade facts, mechanically re-verified from the checkout at bring-up before the patch is written.",
   "rationale": "Bounds the engineering honestly (single function, single file, single author upstream) and keeps the one C-surface expansion inside an explicit maintainer gate rather than scope creep.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §2.8; registry ASM-1986, ASM-1989",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2032",
   "tag": "EXTRAPOLATION",
   "claim": "F1-K COST BANDS at i4i.2xlarge ~$0.69/h: prefill-dominated — construction 768 prefills (24 concepts x 16 contexts x 2 variants), pilot 9 configs x 24 dev items, main >=5 arms x 240-300 items x per-option prefills; prefill throughput on this box is UNKNOWN until measured at bring-up (union-of-experts loading dominates; page cache assists repeated related items); band ~$40-140; CEILING $250. Pre-registered fallback if the projected main run exceeds the ceiling: cut items to n_min=240 and defer REPLACE — never a budget overrun. No band is a premise or a commitment.",
   "rationale": "The single largest cost unknown in F1 is colibri prefill throughput; pricing it as a measured-at-bring-up quantity with a mechanical fallback keeps the ceiling honest.",
   "resolution_path": "Bring-up prefill-throughput measurement on the probe box (recorded in the F1-K run manifest) + instance receipts; bands replaced by measured values in the F1-K run report.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §2.9",
   "load_bearing": false,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  },
  {
   "id": "ASM-2033",
   "tag": "STIPULATED",
   "claim": "KaE SCALE GATE + CLAIM CAPS: F1-K's minimal map = the ~24 probe concepts with WordNet-expanded trigger lemmas and the existing kernel explications as carrier content; sufficient for gating and carrier construction but possibly insufficient for benchmark coverage (the n_min=240 gate is where this bites). The FULL KaE claim ('kernel grounding corrects a frontier model where it is wrong, on open workloads') requires a >=1M-concept sense-split kernel with per-concept grounded content (SCALE-1 S2), the runtime NL->concept mapper, and sense-correct gating. CAPS: every F1-K result is scoped verbatim to 'concept-covered QA items at this model and box'; the ladder rung earned (ASM-2029) is the entire licensed sentence; F1-K feeds the CORRECTNESS ledger ONLY through verdict-gen's registered pathway, and no F1-K outcome moves the CORRECTNESS or EFFICIENCY synthesis verdicts, which remain INCONCLUSIVE-PENDING under their own designated experiments.",
   "rationale": "KaE is the lever most likely to produce a quotable frontier-scale number; its scope and thesis pathway are therefore fixed before any number exists.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §2.6-§2.7, §8; registry ASM-1987; docs/next/design/large-kernel-scale-track.md",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-12"
  }
 ]
}
```

---

## Appendix B — REVISION-1 assumption delta block ASM-2034..2042 (registry-style; coordinator registers with the commit)

```json
{
 "_readme": [
  "GLM52-F1 REVISION-1 assumption delta block ASM-2034..2042 — EMITTED by the Fable architecture-design agent designer-5 (2026-07-13) remediating the cross-vendor FIX-FIRST review (poc/gpt56-review/glm-design/REVIEW-SUMMARY.md, 5 blockers); central registration by the coordinator with the commit; registry/assumptions.jsonl is NOT touched by this pass.",
  "Range verified free at emission: central register tail ASM-2005; companion blocks in docs claim up to ASM-2033; repo-wide grep for ASM-2[0-9][0-9][0-9] finds nothing above ASM-2033.",
  "Supersession map: ASM-2035 supersedes the scoring clause of ASM-2030; ASM-2036 supersedes the d1 clause of ASM-2029; ASM-2037 supersedes the REPLACE decision clause of ASM-2028; ASM-2038 supersedes the n/statistics clauses of ASM-2030, the N=48 clauses of ASM-2014/ASM-2017, and the 6+6 clause of ASM-2018; ASM-2040 supersedes the layer/g selection clause of ASM-2026; ASM-2041 supersedes ASM-2032 and the ceiling figures inside ASM-2021/ASM-2023. Superseded PARENT ASMs remain registered with their remaining content intact; branch thresholds, endpoint directions, and ladder margins are unchanged everywhere.",
  "Companion design: docs/next/design/glm52-followup-experiment.md §R. Tags: MEASURED | LIT-BACKED | STIPULATED | EXTRAPOLATION. EXTRAPOLATION entries carry an explicit resolution_path and are load_bearing=false."
 ],
 "assumptions": [
  {
   "id": "ASM-2034",
   "tag": "STIPULATED",
   "claim": "CLASSIFIER RECONCILIATION WITH ROUTING-ANALYSIS-V2 (evidence registered at ASM-2042): (1) the v2 10k-random-shuffle computation IS the registered p_perm quantity of ASM-2013 executed correctly; the v1 cyclic-shift run is VOID (non-exchangeable null, instrument defect), superseded not averaged; p_perm leg of Branch A is measured SATISFIED (p=0.0001 raw AND mean-centered; branch outcome invariant to metric choice, so no threshold amendment is needed or made). (2) The classifier does NOT fire: M_kernel (kernel-concept pin vs the STRONGER of global-hot and embedding-cluster deflators, P0.3 replay miss-bytes — the kernel-SPECIFICITY leg) and M_oracle remain OPEN and unread; strong concept structure in routing does not establish that kernel labelling exploits it beyond a generic embedding cluster; branch selection waits on the replay unchanged. (3) SensePairSep is computed under its frozen >=0.75 rule when the classifier fires; v2 sense-pair numbers (break p=0.0029; bank p=0.1026) are descriptive direction only. (4) F1-K is unmoved (unconditional by construction); G-route stays noted-not-scheduled. (5) Blindness consequence declared: REVISION-1 is written AFTER reading fingerprint-level structure; it therefore changes NO branch threshold, branch condition, endpoint direction, or ladder margin — only review-demanded methodology; new fingerprint-similarity metrics whose data does not yet exist (F1-B.1 overlap) use mean-centered cosine primary / raw secondary on instrument grounds (93.9% universal mass compresses raw cosine).",
   "rationale": "The corrected evidence resolves one conjunct of Branch A while the deflator conjunct stays open; registering exactly this split — plus the broken-blindness declaration and the rule that the revision moves no thresholds — is what keeps the pre-registration's legitimacy auditable after the coordinator's verified re-analysis was read.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §R0; poc/glm52-probe/results/routing-analysis-v2.json (ASM-2042); registry ASM-2013 (frozen classifier); poc/glm52-probe/interpretation-fable.md (v1 defect provenance)",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2035",
   "tag": "STIPULATED",
   "claim": "F1-K FROZEN CANDIDATE-INDEPENDENT SCORING (supersedes the per-option loglikelihood clause of ASM-2030): one fixed template per item (instruction header + question + options as labelled lines in PUBLISHED order + fixed answer cue), identical bytes across every arm and pass, hashed in the freeze manifest, containing no concept triggers (mechanically verified at freeze); ONE prefill per item per arm; answer = argmax over next-token logprobs of the k single-token answer-LABEL tokens at the answer position (single-token property verified at freeze); deterministic tie-break lowest label index, logged. Gate spans are computed ONCE per item on the frozen full template, frozen in the sidecar, identical across arms/passes by construction; spans inside option text apply identically in all arms; label tokens are never triggers. Predicted-label vs gold-label distribution reported per arm as a descriptive position-bias check. This removes distractor/length/option-dependent-gating bias structurally and cuts scoring cost from k prefills to 1 per item-arm.",
   "rationale": "Prefill-likelihood scoring is valid only when the scored continuation set is candidate-independent and the gate cannot interact with candidate text differentially; a frozen label-token readout achieves both by construction rather than by correction.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §R1.1; poc/gpt56-review/glm-design/REVIEW-SUMMARY.md blocker 1",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2036",
   "tag": "STIPULATED",
   "claim": "F1-K DOSE-EXACT DEFLATOR d1-drng (supersedes the generic-encyclopedic d1 clause of ASM-2029): the generic-paragraph d1 arm is REMOVED as confounded (matches dimensionality, not dose — content length, norm profile, covariance, construction provenance uncontrolled). Replacement: R=5 independent seeded DERANGEMENTS of the concept->carrier assignment over the IDENTICAL K carrier set (no concept keeps its own carrier; seeds enumerated in the freeze manifest, disjoint from the 2 pilot-reserved derangement seeds), with layerwise norm matching: deranged carriers take direction from the donor concept and norm from the recipient — rescaled per (concept, layer) to ||v^K_{c,l}||. Norm rule extended to ALL arms: d0 and d2 rescaled per (c,l) to the same reference; g applied post-rescale; raw and rescaled norms logged. Rung K-2 becomes K vs d1-drng: primary = cluster-level paired test (ASM-2038) of K vs per-item mean correctness over the R passes, alpha=0.05, +3-pt floor; secondary descriptive = K's exact rank among the R passes (best-of-6 nominal 0.167, stated so the rank cannot be over-read). Licensed K-2 wording: 'the TRUE concept->carrier alignment beats label-deranged assignments of the identical carrier set at identical dose at this seam.' d0/d2/d3-text retained unchanged in role.",
   "rationale": "Derangements of the same carrier set are the only control in which literally everything about the intervention is held fixed except whether the label->carrier mapping is the true kernel one — the knull 'kernel content, not any content' bar made dose-exact, as the review demanded.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §R2; poc/gpt56-review/glm-design/REVIEW-SUMMARY.md blocker 2; registry ASM-2029 (parent ladder)",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2037",
   "tag": "STIPULATED",
   "claim": "REPLACE CONFIDENCE-BOUND NON-INFERIORITY (supersedes the point-estimate 'accuracy >= ADD - 2 pts' clause of ASM-2028): REPLACE (still admitted only after ADD passes rung K-1) PASSES non-inferiority iff the lower bound of the one-sided 95% CI on the paired accuracy difference REPLACE minus ADD — cluster-level BCa bootstrap over concept clusters, 10,000 resamples, consistent with the ASM-2038 primary analysis — exceeds -2 accuracy points (Delta_NI = 2 pts, pre-registered), AND measured expert-byte saving on gated tokens > 0. A point estimate above -2 with a CI crossing -2 is a FAIL, pre-worded 'not shown non-inferior'. REPLACE NI is powered by the ASM-2038 formula with its own dev-measured discordance; if unaffordable at the power-required n it is DEFERRED per the ASM-2041 degradation order, never run underpowered.",
   "rationale": "A point estimate cannot license a non-inferiority sentence; only a confidence bound at a pre-registered margin can, and an underpowered NI test would pass vacuously — hence the defer-not-degrade rule.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §R1.2; poc/gpt56-review/glm-design/REVIEW-SUMMARY.md blocker 1",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2038",
   "tag": "STIPULATED",
   "claim": "CLUSTER-AWARE POWER AND SAMPLE-SIZE DERIVATION (supersedes the n_min=240/item-level-statistics clauses of ASM-2030, the N=48 clauses of ASM-2014/ASM-2017, and the 6+6 clause of ASM-2018): (1) PRIMARY ANALYSIS everywhere = per-concept-cluster mean of paired per-item (or per-prompt) differences, one-sided cluster-level sign-flip permutation, 10,000 resamples, alpha=0.05, cluster-level BCa 95% CI reported for every primary contrast; effect floors unchanged (+3 pts F1-K rungs; >=10% median relative F1-A; >=5% additive F1-B.2). (2) F1-K: SE(mean paired lift) ~ sqrt((rho*delta + delta/m)/C); design target SE <= 1.2 points == >=80% power at alpha=0.05 one-sided for a true +3-pt effect (and ~80% joint power for the dual criterion at true +4); required C >= (rho*delta + delta/m)/0.012^2; planning point (delta=0.10, rho=0.03, m=15) C>=67, n~1005; band over stated assumptions (delta in [0.05,0.15], rho in [0,0.05]) n~360-1440 (the high corner exceeds the kernel's concept count and resolves ~+3.4 pts at C=96, reported as such), HARD CAP n_max=1440; >=216 items confirmed underpowered for +3 pts. Trigger map EXPANDED to all kernel concepts with registered explications (target C in [48,96]; at C=48 detectable effect ~+3.5 pts, reported as such). POWER GATE: if the mechanical filter cannot reach C>=48 with m>=8 within n_max, F1-K does not run and returns to the maintainer (subsumes the old n_min=240 gate). Dev split expanded to 96 items; inputs frozen before the test run as delta-hat at its one-sided 80% upper bound and rho-hat floored at 0.02; n_required and inputs are freeze-manifest entries; no fallback ever cuts n below n_required. (3) F1-A/F1-B.2: N_required = ceil(DEFF*(1.645+0.842)^2*(sigma_d/Delta)^2) from MEASURED P0.3 replay variance, DEFF = 1+(m-bar - 1)*rho-hat over concept clusters; N in [48,96] (48 = stratification floor, 96 = affordability cap); N_required>96 -> power-gate return to the maintainer instead of running. (4) F1-B.1: 16+16 pairs, one-sided two-sample permutation on per-pair routing overlap (mean-centered fingerprint cosine primary per ASM-2034(5)), alpha=0.05, powered >=80% for d>=1.0 (n_per_group ~ 2*(1.645+0.842)^2/d^2 ~ 13 < 16); the diagnostic detects only the GROSS surface-form signature — smaller effects fall through to F1-B.2 by design, pre-worded so a pass-through is not evidence of absence.",
   "rationale": "Items and prompts cluster by concept (shared carriers correlate treatment effects), so item-level tests overstate information and 216 items cannot resolve +3 points; with cluster count bounded by the kernel's concept count, the only honest levers are more clusters, cluster-level inference, dev-measured variance inputs, and explicit power gates that return rather than run underpowered.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §R3; poc/gpt56-review/glm-design/REVIEW-SUMMARY.md blocker 3",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2039",
   "tag": "STIPULATED",
   "claim": "F1-K PRE-RUN FREEZE-GATE: maintainer sign-off (GATE 1) approves the RULES; before any F1-K spend the coordinator commits a freeze manifest instantiating them mechanically: (1) scoring template bytes + sha256, label token ids with single-token verification, tie-break and option-order rules; (2) trigger-map version hash, gate precedence rules, per-item frozen span sidecar hash; (3) carrier tables — construction-context list hash, raw + rescaled norms per arm, reference-norm rule; (4) enumerated derangement seeds (2 pilot + 5 main); (5) carrier-blind tuning record — panel composition, S(L,g) table, frozen (L,g); (6) power record — delta-hat_U, rho-hat_floor, achieved C/m, n_required, SE target, cost projection vs ceiling, REPLACE NI margin + CI method; (7) bring-up measurements — measured s/prefill, affordability check, any invoked degradation steps in the pre-registered order; (8) off-concept guard set and dev/test item id list hashes. Items 1-4 freeze before the pilot, 5 at pilot completion, 6 before the test run; the test set stays untouched until all eight entries are committed; any post-freeze deviation is a logged protocol amendment BEFORE further data collection, never silent. F1-K may not start without the manifest.",
   "rationale": "The review's fifth blocker is that sign-off without a mechanical freeze leaves every remediated degree of freedom re-openable at run time; a committed manifest converts the rules into checkable bytes and makes deviation auditable.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §R5; poc/gpt56-review/glm-design/REVIEW-SUMMARY.md blocker 5",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2040",
   "tag": "STIPULATED",
   "claim": "CARRIER-BLIND TUNING (supersedes the argmax-on-K layer/g selection clause of ASM-2026): the pilot grid (3 layer sets x 3 g values, 48-item stratified dev subset) is evaluated over an UNLABELED CARRIER PANEL of three tables — the true-K assignment plus 2 pilot-reserved seeded derangements of it (seeds disjoint from the main-run derangements); selection statistic S(L,g) = unweighted mean dev accuracy across the three panel members with the panel unlabeled in the selection code, so S is invariant to which member is the true mapping and cannot favour the true carrier; tie-break = fewer spliced layers then lower g; the frozen (L,g) is applied IDENTICALLY to every arm (K, all R derangements, d0, d2; d3-text has no splice). Panel composition, seeds, S table, and per-member accuracies (unblinded only after the freeze) are manifest entries. Gate resolution completed: exactly ONE carrier per gated position, never summed; overlap precedence = longest trigger match, then earliest span start, then lowest concept id, with overlapping items tagged multi-concept as a descriptive subgroup; answer-option gating resolved structurally by the ASM-2035 single-prefill template (spans computed once per item, identical across arms; label tokens never triggers); raw-carrier-norm handling per ASM-2036 (log raw, rescale per (c,l) to the K reference, g post-rescale).",
   "rationale": "Selecting the intervention configuration on the treatment arm and handing it unchanged to controls is a winner's-curse subsidy to the treatment; a selection statistic that is invariant to mapping truth removes the asymmetry without giving controls their own post-hoc tuning either.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §R4; poc/gpt56-review/glm-design/REVIEW-SUMMARY.md blocker 4",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2041",
   "tag": "EXTRAPOLATION",
   "claim": "POWER-DERIVED COST CEILINGS (supersede ASM-2032 and the ceiling figures inside ASM-2021/ASM-2023): with 1 prefill per item per arm (ASM-2035) and 10-11 arm passes, worst-case admissible F1-K volume at n_max=1440 is ~21.1k prefills (main 15,840 + construction <=3,072 + pilot ~1,500 + guard 660), planning point ~16.3k at n~1005; at the 30-100 s/prefill planning band this prices $94-312 (planning) to $121-404 (worst case) at $0.69/h -> F1-K CEILING $450; F1-A at N<=96 (6 arms + a5 double-pass) ~$49-138 -> CEILING $180; F1-B (B.1 16+16 ~$8-12; B.2 3 arms x N<=96 ~$21-59) -> CEILING $85; F1-C unchanged $40. Branches are exclusive: maximum realized path = F1-K + one branch <= $630; ceilings sum to $755. Pre-registered degradation order if the bring-up projection at n_required exceeds the F1-K ceiling: (1) R 5->3, (2) defer REPLACE, (3) defer d3-text, (4) STOP and return to the maintainer — n is never cut below n_required and no ladder-rung arm (b0, d0, d1-drng, d2, K) is ever dropped. No band is a premise or a commitment; ceilings, not estimates, bound spend.",
   "rationale": "The review required ceilings derived from the power calculation rather than asserted; pricing the power-required n at the pessimistic prefill band with a mechanical degradation order keeps the ceiling honest while the true prefill rate stays a bring-up measurement.",
   "resolution_path": "Bring-up s/prefill measurement + instance receipts recorded in the freeze manifest (ASM-2039 item 7); bands replaced by measured values in the F1-K and branch run reports.",
   "backing_ref": "docs/next/design/glm52-followup-experiment.md §R6; poc/gpt56-review/glm-design/REVIEW-SUMMARY.md blocker 3",
   "load_bearing": false,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-13"
  },
  {
   "id": "ASM-2042",
   "tag": "MEASURED",
   "claim": "ROUTING-ANALYSIS-V2 RESULT (coordinator-verified re-analysis of the committed P0 fingerprints; file poc/glm52-probe/results/routing-analysis-v2.json, sha256 e9d6813f99a6efa03645a3c15260a84c3d47221a3d0061ad6bbc68749e1c57cc, seed 20260712, n=24 fingerprints, keyspace 16,483, 10,000 random label shuffles): raw cosine within-concept 0.9977 vs across 0.9545 (delta 0.0432), perm p=0.0001; universal routing component carries 93.9% of histogram mass; MEAN-CENTERED cosine within 0.9119 vs across -0.0740 (delta 0.9859), perm p=0.0001; sense pairs (centered): break delta 0.1955 p=0.0029 (n=9), bank delta 0.3259 p=0.1026 (n=6). VERDICT recorded: the earlier p=0.33 (routing-analysis.json, v1) was produced by a degenerate cyclic-shift permutation scheme and is VOID as an instrument defect; v2 supersedes it. GLM-5.2 routing fingerprints carry strong concept-level structure; kernel-SPECIFICITY versus a generic embedding-cluster conditioner (M_kernel, and the M_oracle ceiling) is NOT measured by this analysis and remains open (ASM-2034).",
   "rationale": "Registers the corrected mechanical evidence with its hash, seed, and void-verdict on the defective v1 run so downstream documents cite one canonical record.",
   "backing_ref": "poc/glm52-probe/results/routing-analysis-v2.json; poc/glm52-probe/analyze_routing_v2.py; poc/glm52-probe/results/routing-analysis.json (v1, VOID); poc/glm52-probe/interpretation-fable.md §1.2 (defect provenance)",
   "load_bearing": true,
   "status": "open",
   "owner": "designer-5",
   "date": "2026-07-13"
  }
 ]
}
```
