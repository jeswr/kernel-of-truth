# Programme-3: Neurosymbolic Architecture — programme design + hierarchical work-breakdown

> **Status: DESIGN document + work-breakdown for maintainer review (external review
> pass expected before beading). NOTHING here is frozen, pre-registered, scheduled,
> or run; no registry experiment record, verdict, audit, or frozen object is touched;
> no bead is created by this document (the coordinator beads §5 after review).**
> Author: Fable, chief-architect role (`kern/fable-designer`), 2026-07-11.
> Branch context: design-only commit; quality gates = `tools/registry/registry-check.py`.
>
> Inputs read at source: `docs/next/feasibility-synthesis.md` (the capstone verdict,
> 2026-07-11); `registry/assessments/*.json` (esp. a-e2-census, l3a-parse, a5-nl,
> f2b-replicate, nsk1-*); `docs/next/architecture-ladder.md` (the L0–L4 centrality
> ladder); `docs/next/arch-survey.md` (N0 seam survey);
> `docs/next/benchmark-evaluation-strategy.md` (the SmolLM2 anchor suite);
> `docs/next/free-compute-recon.md` (the free-compute pool). Epistemic discipline:
> every PREMISE / DECISION / LOAD-BEARING line carries its `[TAG: ref]` on the same
> logical line; forward projections live in the register as EXTRAPOLATION entries
> (ASM-0804/0805/0806) and are **never premises**; new stipulations are registered in
> the fresh block ASM-0800–0808.

---

## 0. What Programme-3 is, and what it inherits

The maintainer's intent, restated: use something *like* the kernel + world
information this programme has built to create **neurosymbolic AI architectures**
that (1) achieve a **higher AI index than all other models of the same size and the
same compute**, and then (2) find how **small** the whole system (model + kernel +
world + everything else) can be made while staying competitive on that index.
Because the system is neurosymbolic, size cannot be parameters: size is **on-disk
footprint (GB)** plus **inference cost**. Start very small to learn cheaply which
architectures work; then continuously scale while improving them.

Programme-3 is a **new goal**, not a new evidence base. It inherits Programme-1/2's
instruments, seams, and — critically — its measured walls. The honest starting
position, restated from the capstone with its own tags:

- PREMISE: across the entire registry there are ZERO audited end-task wins over the
  kernel-as-text null attributable to the kernel's content; both value theses stand
  at INCONCLUSIVE-PENDING [MEASURED: docs/next/feasibility-synthesis.md §0/§6,
  restating registry/verdicts/* + registry/assessments/oracle-coverage.json].
- PREMISE: the deterministic engine is exact, fail-closed, µs-cheap, and ports
  across two verticals with a byte-identical binary — but only on its own
  closed-grammar, self-authored substrate [MEASURED: registry/verdicts/l3a.json
  600/600 + registry/verdicts/a5.json 855/855, both audit CONFIRMED].
- PREMISE: both measured natural-language crossings FAILED — l3a-parse retains
  47.6% of gold-parse exactness (safe failure), a5-nl retains 41.6% AND fired the
  S2 dangerous-wrong kill (5.0% wrong-with-provenance) [MEASURED:
  registry/verdicts/l3a-parse.json + registry/verdicts/a5-nl.json].
- PREMISE: the one end-task efficiency SIGN is real and audited — SmolLM2-135M +
  kernel-verify-retry beats 1.7B-alone by +0.1507 at ~10% of the per-query cost —
  but it is correct-ALIGNMENT-specific (not shown kernel-content-specific), on
  formal templated inputs only, and its de-confound (knull ablation / human
  f2b-transfer) is unrun [MEASURED: registry/verdicts/f2b-replicate.json PASS +
  registry/assessments/f2b-replicate.json does_not_license].
- PREMISE: coverage is a wall before reachability is: kernel-expressibility 0.3542
  on the friendliest measured corpus (corpus/rung/kernel-state-indexed, extrapolates
  to no other corpus), 0/1,000 random Mathlib declarations captured, 0/1,550 on the
  define-lane external-benchmark census [MEASURED: ASM-0001 (m0b);
  registry/verdicts/g8.json; registry/assessments/b-cov-define-lane.json].
- PREMISE: model-internal grounding is unresolved two-sided: text-delivered
  grounding measured NET-HARMFUL (0.76 → 0.43 on append; 0/24 rescues), the
  residual-stream channel delivers at echo grade (keyacc 0.81/0.85) but integration
  into free generation is unresolved (R− rescue 0/8) [MEASURED:
  registry/assessments/nsk1-g2d.json + nsk1-bprime2.json, exploratory/DRAFT status].
- PREMISE: cross-lingual concept minting shows a large MEMBERSHIP UPPER BOUND on
  prefill savings (~18.5–24.0% Qwen2.5 / 33.4–41.7% SmolLM2 at the 10k-concept
  anchor) with the entire consumption channel and mint-cost side unmeasured
  [MEASURED: registry/assessments/a-e2-census.json, Tier-0 exploratory census — an
  upper bound, never achievable savings].

Two consequences shape everything below.

- DECISION: Programme-3 adopts the four inherited hard constraints — (1) no
  real-input claim without an FK-NLB-3-class NL front-end gate cleared per vertical;
  (2) every kernel-contribution claim carries deranged-store + aligned-non-kernel
  controls; (3) coverage numbers stay corpus/rung/kernel-state-indexed; (4)
  membership/compression figures are upper bounds until a consumption channel is
  measured [STIPULATED: ASM-0808].
- DECISION: Programme-3's headline claims are **system-level competitive claims**
  (index at matched size/cost), not kernel-content-attribution claims — this is a
  deliberate re-aiming: even if a win turns out to be "aligned typed store +
  checker" rather than "NSM semantics", it still satisfies the maintainer's
  north-star, and the attribution question is carried as a separate, honest,
  secondary analysis rather than a blocker [STIPULATED: ASM-0800].

Relation to the existing L0–L4 ladder (`docs/next/architecture-ladder.md`): the
ladder enumerated *where the kernel can touch a model*; Programme-3 reuses those
seams as components but changes the objective function from "make the kernel more
central" to "beat matched-size/compute baselines on a pinned index, then shrink".
Rules-placement options in §3.3 map onto L2a/L2b/L3c; the GNN fusion family extends
the A2/E5 trained-bridge seam; the verifier-loop system is F2b productised.

---

## 1. North-star and falsifiable success criteria

### 1.1 The AI index — KOT-AI-INDEX/1

- DECISION: the "AI index" is operationalised as **KOT-AI-INDEX/1**: an unweighted
  macro-average of per-benchmark scores over a pinned suite, evaluated ONLY under
  the programme's own pinned harness (lighteval-pinned per the census manifest
  design), zero-shot/base-variant settings pinned per benchmark; published model-card
  numbers are anchors for sanity, never comparators [STIPULATED: ASM-0800].

Suite by rung (versioned; changing membership = an index version change that
re-baselines everything):

| Rung band | Suite | Why |
|---|---|---|
| R-0–R-2 (≤500M) | HellaSwag, ARC-Easy, ARC-Challenge, PIQA, MMLU-cloze, CommonsenseQA, WinoGrande, OpenBookQA, GSM8K (+TriviaQA iff its licence blocker resolves) | The exact suite the SmolLM2 host family publishes against — anchors exist at 135M/360M/1.7B, harness-pinning design already written (`docs/next/benchmark-evaluation-strategy.md` §1.1), and these benchmarks have measurable floors at tiny scale (Open-LLM-Leaderboard-v2-style suites floor out below ~1B). |
| R-3 (1–2B) | R-0 suite + MMLU-Pro, BBH, one pinned code benchmark (HumanEval+ or the roadmap's code track) | Small-suite saturation begins; the additions are the standard harder derivatives with published 1.7B-class anchors. |
| R-4+ (gated) | KOT-AI-INDEX/2, designed at promotion time by a Phase-1 task | Do not pretend today's suite discriminates at sizes we cannot yet afford to test. |

Alternatives considered and rejected for the tiny rungs: the HF Open LLM
Leaderboard v2 set (IFEval/BBH/MATH/GPQA/MuSR/MMLU-Pro) floors at ≤500M and would
make every rung-0/1 comparison noise; ARC-AGI-class suites measure a different
construct; "AI Index" in the Stanford-report sense is a survey, not a benchmark.
At R-0 specifically, where even this suite is weak, the index is supplemented (for
*learning*, not for the win condition) by TinyStories-class LM-eval losses and the
programme's own covered-slice probes.

Two standing index rules:

- DECISION: the index always reports the **full vector** (per-benchmark scores,
  refusal/abstention rates, and the covered-vs-uncovered split where a kernel is in
  play) alongside the scalar; the scalar exists for ranking, the vector for honesty
  — no Programme-3 claim may quote the scalar without the vector being one link
  away [STIPULATED: ASM-0800].
- DECISION: NL-input integrity — index items are consumed as their natural
  benchmark text; no arm may receive hand-formalised inputs; any kernel-touching
  arm therefore either includes its NL front-end inside the measured system or
  abstains on what it cannot parse. This is the anti-l3a/a5 rule: the parser is
  part of the product, and its failures are the system's failures [STIPULATED:
  ASM-0808].

### 1.2 Size — KOT-SIZE/1 (on-disk GB)

- DECISION: size := **raw on-disk bytes of the complete frozen deployment
  artifact** required to serve the eval — model weights as serialized at stored
  precision (int4 counts as its bytes, not its dequantised bytes), kernel store,
  world-layer records, all retrieval/lookup indices, GNN weights, adapters, rule
  tables, tokenizer files, and ALL code beyond a pinned common base image (the
  engine binary and any custom runtime count; CPython/PyTorch/node in the pinned
  base image do not, because both arms ship on the same base image); a zstd-19
  compressed figure is co-reported to expose compressibility asymmetries between
  weight bytes and store bytes, but the RAW figure is primary [STIPULATED:
  ASM-0800].

Same-size band for comparisons: ±10% on KOT-SIZE/1 raw bytes. Anything the
neurosymbolic arm ships that the baseline does not is inside its budget — there is
no "the kernel is free" accounting, ever. Quantisation games are symmetric: if the
neurosymbolic arm quantises, the baseline gets the same best-effort quantisation.

### 1.3 Inference cost — KOT-COST/1 (the dual ledger)

Symbolic operations have no canonical FLOP equivalent (a hash lookup, an index
probe, a unification step), so a single analytic ledger would let either side
cheat. Hence:

- DECISION: inference cost is measured on a **dual ledger**: (L1) analytic
  FLOPs/query for all neural components (standard 2·params·tokens accounting +
  attention terms, pinned formula sheet frozen with the framework), symbolic
  components entering ledger L1 at zero; (L2) measured whole-system wall-clock
  per query, peak resident memory, and energy per query (RAPL on CPU /
  `nvidia-smi`-class counters on GPU) on pinned hardware, batch size pinned,
  including every symbolic, retrieval, and I/O cost. A "compute-matched" claim
  must hold on **both** ledgers; a "cheaper" claim must name which ledger and hold
  on L2 at minimum (L2 is the deployed-reality ledger; L1 exists to keep the
  neural parts honest and hardware-independent) [STIPULATED: ASM-0800].

Precedent that the symbolic side can be genuinely cheap on L2 — but also that the
accounting has to be measured, not assumed:

- PREMISE: the deterministic engine answers covered queries at 5.29–7.82 µs/query,
  and the f2b system-level cost ratio vs the 1.7B host was measured at 0.103
  [MEASURED: registry/verdicts/l3a.json + registry/verdicts/a5.json engine timing;
  registry/verdicts/f2b-replicate.json cost_ratio_vs_R3].

### 1.4 The exact win condition and the exact shrink objective

**W1 (the competitive claim), verbatim:** at a given rung R-k, a Programme-3 system
S beats the baseline set iff, under the frozen KOT-AI-INDEX version for that rung,
own-harness, with all §2 mandatory controls surviving:

1. `INDEX(S) − INDEX(B) ≥ δ_k` with a one-sided 95% lower confidence bound > 0 and
   the pre-registered margin δ_k cleared, for **B = every model in the baseline
   set for that rung** (§2.3): the best open pure-neural models within ±10% of S's
   KOT-SIZE/1 bytes, re-evaluated under the identical harness; and
2. S's inference cost is within the matched band on **both** KOT-COST/1 ledgers
   (±10% L1 where L1 applies; ±10% wall-clock and ≤ baseline peak memory on L2);
   and
3. the decontamination audit (§2.2) passes; and
4. the deranged-store and aligned-non-kernel controls (§2.2) behave as
   pre-registered (derangement destroys any kernel-attributed component of the
   lift; the aligned-non-kernel result is REPORTED as the attribution split,
   whatever it shows).

**W2 (the shrink objective), verbatim:** once W1 first holds at any rung, minimise
KOT-SIZE/1 bytes subject to `INDEX(S) ≥ INDEX(M_ref)` where M_ref is a named,
pinned open reference model (initial M_ref = SmolLM2-1.7B own-harness; revisited by
maintainer fork per index version). The deliverable is the measured **Pareto
frontier over (bytes, L2 cost, index)**; headline success = at least one point that
strictly dominates every open model we can measure at the small end (smaller bytes,
≤ cost, ≥ index).

Falsifiability: W1 is falsified per-rung by failing its own margin; the programme
has an explicit kill shape in §7 if W1 fails everywhere through R-2. There is no
"moral victory" clause: matched-baseline parity is a FAIL of W1, however
interesting the architecture.

---

## 2. The measurement + fair-comparison framework (where the programme lives or dies)

Comparing a neurosymbolic system against pure-neural baselines at matched size and
compute is the single hardest methodological problem here — harder than any
individual architecture. Three named confounds, each with a mechanised answer, all
frozen together as **P3-MF (KOT-FAIR/1)** before any Phase-2 experiment freezes.

### 2.1 Confound A — size-accounting asymmetry

Weight bytes and store bytes are different substances: stores compress well, can
be lazily paged (disk vs RAM), and can be grown after deployment. Mechanised
answers: the raw-bytes-primary rule with zstd-19 co-report (§1.2); peak RSS on
ledger L2 (a store paged from disk pays latency on L2 instead — no free lunch
either way); and the artifact-freeze rule — the store hash is pinned at eval time,
so "grow the store after measuring size" is impossible by construction.

### 2.2 Confound B — the answer-key problem (the deepest one)

A store can encode benchmark answers far more directly than weights can. The f2b
lesson is exactly this in miniature:

- PREMISE: the f2b verifier accepts iff the answer string-equals the canonical
  record while gold is DEFINED by that same equality, so the measured +0.1507 is
  provably consistent with "aligned answer key + retry", and the shuffled control
  cannot discriminate content from alignment [MEASURED:
  registry/assessments/f2b-replicate.json does_not_license].

Mechanised answers, all mandatory for any W1 claim [STIPULATED: ASM-0801]:

1. **Decontamination audit (hard gate, win-voiding):** an automated n-gram overlap
   + embedding-similarity screen of every kernel/world/store record against every
   item of the frozen index suite, with a pinned threshold and a human-spot-check
   protocol on flagged pairs; stores may not be authored, selected, or grown using
   any index item, its paraphrase, or its source page. A win whose store fails the
   audit is VOID, not caveated. (Neural baselines carry the standard training-data
   contamination caveat symmetrically: we report known contamination status of
   baseline training corpora but cannot audit closed corpora — stated openly as an
   asymmetry that favours the baselines' scores, i.e. it is conservative for us.)
2. **Deranged-store control:** seed-pinned derangement of the store→item
   addressing (the f2b control, inherited); any component of the lift that
   survives derangement is not store-content and must be attributed to the
   architecture prior.
3. **Aligned-non-kernel-store control (the knull lesson):** a matched-size,
   matched-alignment store with non-kernel content (e.g. plain-English typed
   records) run in the same architecture. This is the attribution split between
   "the kernel's formal content helps" and "any well-aligned typed store helps".
   Under the §0 re-aiming this control does not gate W1 (a win with a generic
   store is still a neurosymbolic win) — but its result is always reported, and
   any *kernel-specific* claim rests on it.
4. **Kernel-as-text null:** the store's content delivered as plain prompt text at
   matched token budget — the null that Programme-1/2 never lost to and that
   nsk1-g2d showed can be actively harmful; it stays mandatory.

### 2.3 Confound C — baseline selection and compute matching

- DECISION: the baseline ladder per rung is (i) **anchors** — published card
  numbers of same-band open models, sanity only; (ii) **primary comparators** —
  own-harness re-evaluations of the strongest open pure-neural models within the
  ±10% size band (at R-1: SmolLM2-135M, plus the strongest same-band peers alive
  at freeze time, pinned by name+revision in the P3-MF freeze — the set is chosen
  at freeze, not after results); (iii) **training-compute-matched from-scratch
  baselines** — required only at rungs where the neurosymbolic arm itself trains
  from scratch (H-GU rungs), where both arms get the same token budget, data
  recipe, and tuning-attempt budget [STIPULATED: ASM-0801].
- DECISION: "same compute" binds on INFERENCE compute (both ledgers); training
  compute is always reported, and enforced as matched only on the ground-up fork —
  because the maintainer's objective is a property of the deployed system, and
  because dimension-drop arms *inherit* their donor's training compute, which is
  the honest statement rather than a matching problem [STIPULATED: ASM-0801].

Tuning-effort symmetry (the quiet killer of fair comparisons): every Phase-2
prereg pins the hyperparameter search budget PER ARM in advance (same number of
configurations, same selection rule on a dev split disjoint from the index suite).
An architecture that only wins with 10× the tuning attempts has not won.

Statistical shape (inherited house style): one primary endpoint per experiment;
pre-registered margins; bootstrap/Wilson bounds as appropriate; TOST for any
"retains capability" (non-inferiority) claim — note the dimension-drop central
claim is a NON-INFERIORITY claim and gets TOST, not a superiority test; kill
criteria verbatim in the prereg; the verdict generated by the mechanical grader
and cross-vendor audited, per standing practice.

### 2.4 What P3-MF-0 must deliver (the framework as an artifact)

A frozen `KOT-FAIR/1` spec: the index suite pins (datasets, revisions, harness
version, prompts, shot counts, scoring), the KOT-SIZE/1 measurement script, the
KOT-COST/1 formula sheet + measurement rig for the local box and one pinned GPU
class, the decontamination screener, the baseline-set selection rule, and a
**calibration report**: the framework run on pure-neural models ONLY (135M vs
360M vs 1.7B), demonstrating that the index separates known-ordered models with
the expected ordering and stable variance — the instrument is validated on cases
with known answers before it ever judges a neurosymbolic system. This is Phase-0/1
work on the local box + free credits, ~$0.

---

## 3. Architecture design space — named hypotheses

- DECISION: the design space is enumerated as the named families below; the
  enumeration is a scoping choice covering the maintainer's directed directions
  plus the seams Programme-2 built, and confers no evidence on any family
  [STIPULATED: ASM-0802].

Evidence-status legend used below, tied to §0's premises: **supported** (a
measured positive exists at some scope), **cautioned** (a measured negative or
unresolved result bears directly), **unmeasured** (no programme evidence either
way). Forward projections are registered: H-GNN → ASM-0805, H-RULE → ASM-0806,
H-DD → ASM-0804 — all EXTRAPOLATION, never premises.

### 3.1 H-VL — the verifier-loop system (small model + kernel-verify-retry, productised)

The one audited end-task SIGN, promoted from experiment to *system design*: a
small LM generates; the deterministic engine checks covered claims; failed checks
trigger bounded retry/abstain; the whole loop (with its NL front-end) is the
product being indexed.

- Rationale: it is the only family with a measured system-level cost win shape
  (+0.1507 at ~10% cost — formal inputs, alignment-confounded; §0).
- Evidence status: supported at formal-input scope; cautioned by the NL-boundary
  FAILs (the loop's real-input version does not exist until FK-NLB-3 clears) and
  by the unresolved attribution (knull / human f2b-transfer unrun).
- Expected profile: size = LM + store + engine (store dominates growth); cost =
  LM cost × (1 + retry rate) + µs-scale engine cost; wins ledger L2 easily on
  covered slices, pays on uncovered ones (retries that cannot verify).
- Cheapest falsifier: at R-1, on the index suite itself (not a self-authored
  slice), with the decontamination gate: if verify-retry over the honestly-parsed
  covered subset moves the index by less than its pre-registered δ against
  matched-cost baseline sampling (e.g. best-of-k with self-consistency at equal
  L2), H-VL dies as an index-mover at scope — likely killed by coverage (§7 R2)
  long before verification quality.

### 3.2 H-GNN-{ST, KV, LF} — hybrid GNN over the kernel+world graph

The kernel + world layer form a typed relational graph (concept URNs, axiom
records, world-layer edges). A small GNN encodes query-relevant subgraphs; the
encoding is fused into the LM at one of three seams:

| Variant | Fusion seam | Continuity | Expected cost/size delta |
|---|---|---|---|
| H-GNN-ST | GNN output → trained bridge → soft tokens at the input edge | The A2/E5 adapter seam, replicated positive at one rung | +GNN weights (small, MBs) + adapter; prefill shortens if soft tokens replace text serialisation — the only variant with a plausible cost *reduction* |
| H-GNN-KV | Graph nodes written as KV pairs into attention (KBLaM-style) | L2b kernel-addressed memory (ladder) | +KV construction cost per query; memory grows with injected node count |
| H-GNN-LF | Late fusion at logits/answer-selection | none (new) | cheapest to build, weakest hypothesised integration |

- Evidence status: unmeasured as a family; the *seam* is supported (E5 adapter
  PASS at one rung); cautioned hard by nsk1 — text-delivered grounding measured
  net-harmful and internal delivery reached only echo grade with integration
  unresolved (§0), so "the GNN delivers but the LM doesn't use it" is the named,
  measured-adjacent failure mode.
- Cheapest falsifier (kills all three variants at once if it fires): R-0/R-1
  relational-slice test — GNN-fusion vs the same subgraph serialised as text vs
  no-graph, matched L2 cost. If fusion ≤ text-of-graph, the GNN is decoration and
  the family dies at scope (text serialisation is the cheaper implementation of
  the same information). Registered projection: ASM-0805.

### 3.3 H-RULE-{CD, KV, AD, ACT, HL} — rules-based inference built into the LLM: the placement analysis

The maintainer asked *where* deterministic rule-inference should live inside the
model. Five placements, analysed on the axes that matter — cost at inference,
trainability/invasiveness, provenance (can the output cite the rule?),
fail-closedness (does an off-coverage query degrade to the base model or to
garbage?):

| Placement | Mechanism | Inference cost | Invasiveness | Provenance | Fail-closed | Prior evidence hook |
|---|---|---|---|---|---|---|
| **H-RULE-CD** constrained-decoding head | engine invoked mid-decode; covered spans constrained to record-derived continuations; uncovered decode untouched | engine µs + masking, near-zero overhead | none (no weights touched) | exact (record id per constrained span) | yes by construction | L3c (ladder); f2b loop is the unconstrained cousin |
| **H-RULE-KV** KV-side rule memory | rule heads/records inserted as KV pairs keyed by kernel content-hash; attention reads them | KV build per query; grows with fired-rule count | low (no base-weight change) | attributable via attention audit (weaker) | partial | L2b (ladder); KBLaM-family lit |
| **H-RULE-AD** rule adapters | LoRA-class adapters trained to implement rule families; swapped/composed at inference | adapter matmuls, small | medium (trained, but detachable) | none intrinsically | no — must be measured | A2/E5 trained-bridge precedent (input-side only) |
| **H-RULE-ACT** activation-level rule firing | rule conditions detected in activations; firing applies steering vectors / activation edits | probe + edit per layer, small | medium-high (runtime intervention) | weak | no — edits can corrupt off-target behaviour | nsk1 residual channel: delivery ECHO-grade, integration unresolved — the direct caution |
| **H-RULE-HL** dedicated hidden layer | a mid-network layer whose units are pinned to kernel concepts; rule inference as a deterministic map on that bottleneck | in the forward pass (cheap) but always-on | highest (architecture surgery, training from scratch or heavy retrofit) | strong if the bottleneck is read out | no — bottleneck can throttle general capability | L2a (ladder); the φ-sweep L2c is its dose-response |

Design ruling from the analysis (a prior ordering, not a verdict):

- DECISION: Phase-2 tests the placements in the order CD → KV → {AD, ACT} → HL —
  cheapest, least invasive, most provenance-preserving, most fail-closed first;
  HL (and the ground-up φ-sweep it shades into) is deferred until a shallower
  placement has shown a positive, because every deep-internal channel measured so
  far is unresolved-at-best while the external/decode-side seam holds the
  programme's only positive [STIPULATED: ASM-0802; the supporting facts are §0's
  nsk1 and f2b premises].
- Cheapest falsifier for the family: R-1 head-to-head of H-RULE-CD and H-RULE-KV
  against H-VL at matched accuracy on the covered slice, decided on the L2 ledger:
  if in-model placement cannot beat the external loop on cost at matched accuracy
  (it starts with a µs-cheap external competitor — a very low bar to lose to),
  in-model rules die at scope. Registered projection: ASM-0806.

### 3.4 H-RB — retrieve-vs-bake (the store-placement fork, cross-cutting)

For any store-using family: store on disk + retrieval at inference (bytes cheap,
L2 cost per query) vs distilled/baked into weights (bytes expensive, zero per-query
retrieval). This is a pure size↔cost trade under KOT-SIZE/1 + KOT-COST/1 and is
swept, not hypothesised: each Phase-2 winner is measured at both settings and the
Pareto points reported. (The a-e2 dense-I/O membership bound — an upper bound,
§0 — is the retrieve-side's long-run prize and stays quarantined until its
consumption channel is measured.)

### 3.5 The build-strategy fork: H-GU vs H-DD (compare cheaply at small scale)

**H-GU — ground-up neurosymbolic training.** Train small hosts from scratch with
the symbolic interface present from step 0 (concept-token I/O, bottleneck, or
verify-in-the-loop training). Only at rungs R-0/R-1 initially (training compute
matched to the from-scratch baseline, §2.3). Evidence status: unmeasured; the
ladder's L2c-full is its closest designed relative. Expected profile: the most
expensive path per experiment but the only one that can co-adapt weights to the
kernel. Cheapest falsifier: at R-0, ground-up-with-interface vs same-recipe
plain twin at matched tokens — if the interface confers nothing at R-0 on either
the index proxies or the covered slice, it is very unlikely to at R-2+.

**H-DD — dimension-drop of an existing model (the maintainer's strategy (b)).**
Hypothesis verbatim (registered as EXTRAPOLATION ASM-0804, never a premise): take
an existing model; learn an alignment between its hidden dimensions/subspaces and
the concepts encoded in kernel+world; **normalise** — apply an orthogonal rotation
absorbing into adjacent linear maps so the concept-aligned subspace becomes
axis-aligned (function-preserving by construction, testable to numerical
tolerance); then **drop ~80% of the dimensions** corresponding to encoded
concepts, letting the kernel+world store supply that content externally at
inference → a ~5× smaller model that retains language capability.

The designed central-claim experiment (P3-E-DD-1, the full design is P3-D-DD's
deliverable; this is its required shape):

1. **Donor:** SmolLM2-135M (own anchors exist) + Pythia-160M as a replication
   donor (open training provenance).
2. **Alignment step:** two pinned methods, compared — (a) supervised concept
   probes from kernel/world records to hidden states (the A2 bridge inverted);
   (b) sparse dictionary (SAE-class) features matched to kernel concepts by the
   mapper. The measured mapper caution applies to any mapper-mediated matching:
   proxy precision ~0.71 [MEASURED: registry/verdicts/m0a-llmproxy.json, weak
   proxy pending human gold].
3. **Normalise:** per-layer orthogonal rotation, verified function-preserving
   (max logit drift bound pre-registered) before any drop.
4. **Arms at matched KOT-SIZE/1 bytes:** (i) concept-aligned drop + store
   attached; (ii) concept-aligned drop, no store; (iii) **random-subspace drop of
   equal rank** (the decisive control); (iv) magnitude/structured pruning at equal
   bytes (the strongest published-practice control); (v) donor unmodified
   (ceiling); each ± the store, so store-attachment effects are separable.
5. **Primary endpoint:** TOST non-inferiority of arm (i) against a pre-registered
   fraction of the donor's index at the 5× size point, AND superiority of (i)
   over (iii) — the hypothesis is specifically that *concept-aligned* dimensions
   are the droppable ones; if (i) ≈ (iii), alignment adds nothing over generic
   rank reduction and H-DD's distinctive claim is dead even if compression
   succeeds generically.
6. **Dose-response:** drop fraction swept {20, 40, 60, 80}% — the 80%/5× point is
   the maintainer's target, not the only measurement; the curve is the result.

Honest evidence status, stated plainly: this is the programme's most aggressive
extrapolation. Nothing measured supports it yet — nsk1 found no resolved
integration between kernel vectors and model internals, and measured kernel
coverage (0.3542 friendliest-corpus, ~0 on external benchmark censuses, §0) is
far below "80% of a model's dimensions correspond to encoded concepts". Two
things keep it worth its cheap test: it is *continuous with the A-E2/compression
thesis* (the store-side membership bound is real and large, as an upper bound),
and its falsifier is genuinely cheap (no training from scratch; probes + rotations
+ evals at R-1 fit the free-compute pool). If it works even partially it directly
serves W2. Expected profile: best-in-programme bytes reduction if true; cost
profile neutral-to-worse (store lookups replace matmuls on covered content).

### 3.6 Design-space summary table

| Family | Maintainer direction | Evidence status | Distinct falsifier cost |
|---|---|---|---|
| H-VL | (efficiency lineage) | supported (formal, confounded) | ~$0–100, R-1, free credits |
| H-GNN-ST/KV/LF | "hybrid GNN" | seam supported; integration cautioned | ~$0–200, R-0/R-1 |
| H-RULE-CD/KV/AD/ACT/HL | "rules built into the LLM + where" | cautioned (nsk1) / unmeasured | ~$0–200 for CD/KV rung |
| H-RB | (cross-cutting) | store side measured as upper bound only | rider on other experiments |
| H-GU | "train from ground up" | unmeasured | R-0 from-scratch pair, ~10–50 GPU-h |
| H-DD | "drop ~80% of dimensions" | unmeasured; boldest extrapolation (ASM-0804) | probes+rotation+eval, ~10–30 GPU-h |

---

## 4. The scaling ladder

- DECISION: rungs, promotion gates, and kills as follows [STIPULATED: ASM-0803].

| Rung | Params-equivalent (orientation only; the binding band is bytes+cost) | What it exists to learn | Compute home | Est. cost |
|---|---|---|---|---|
| **R-0** | 1–30M, TinyStories-class data | Kill bad architectures fast: does the mechanism do anything at all? H-GU twin-training lives here; index proxies (LM-eval losses + covered-slice probes) supplement the weak tiny-scale index | Local box (harness, symbolic side, evals) + single free GPU (Modal/ARC) for training | ~$0 beyond free pool |
| **R-1** | 100–200M (SmolLM2-135M anchor) | The decisive cheap rung: H-DD central claim, H-VL index test, H-RULE-CD/KV vs H-VL, H-GNN falsifier — every family's kill-or-promote read | Oxford ARC / Modal academics; single-GPU jobs | ≤ ~50 GPU-h/family |
| **R-2** | 300–500M (SmolLM2-360M anchor) | Do R-1 survivors scale in the right direction? First serious W1 attempt; first Pareto (W2) sweep on the winner | ARC/Modal; AIRR Gateway if awarded | ~100–500 GPU-h total |
| **R-3** | 1–2B (SmolLM2-1.7B anchor) | W1 at a size the outside world cares about; index version bump (suite extension) | AIRR Gateway 10k GPU-h class; TRC for training-side replicas | gated: maintainer + secured allocation |
| **R-4** | 3–8B | Only if R-3 W1 holds; KOT-AI-INDEX/2 designed first | second-wave grants (§6) | gated: explicit maintainer fork |

Rung discipline: promotion requires the rung's pre-registered primary met (or an
explicit maintainer override of a diagnosed instrument failure); a family failing
its primary at two consecutive rungs is closed at scope; the W2 shrink sweep runs
at the lowest rung where W1 first holds, not before (shrinking a losing system is
motion, not progress). Architectures are allowed to *change between rungs* —
that is the maintainer's "continuously improve while scaling" — but every change
re-enters through prereg-freeze; there is no silent drift up the ladder.

---

## 5. Phased, hierarchical work-breakdown (the beadable structure)

- DECISION: Phase-0 = six literature reviews + one direct-design task (P3-MF-0)
  are the ONLY top-level beads; each names the Phase-1 design beads it spawns on
  completion; each Phase-1 design bead spawns its Phase-2 experiment beads through
  prereg-freeze. Nothing below is created/frozen/run by this document
  [STIPULATED: ASM-0807].

Node types: **[LIT]** = lit-review-then-fan-out (literature-researcher agent);
**[DESIGN]** = direct design (Fable / experiment-designer); **[EXP]** =
pre-registered experiment (experiment-designer freezes → runner runs → analyst
reads out). Every [EXP] additionally depends on P3-D-INDEX (the frozen framework).

### Phase-0 — top-level beads (all parallel, no cross-dependencies)

| Bead | Type | Scope (what the review must answer) | Spawns on completion |
|---|---|---|---|
| **P3-LR-NSA** — neurosymbolic architectures survey | [LIT] | The field map: neurosymbolic system taxonomies; what has beaten matched neural baselines anywhere, at what scale, under what accounting; each prior failure judged capability-limited vs fundamental; the strongest published baselines for W1-style claims | P3-D-GNN, P3-D-RULE, P3-D-GU (co-input); any new H-* family found |
| **P3-LR-GNN** — GNN–LLM fusion | [LIT] | GraphToken/KBLaM/GNN-adapter lineages; graph-encoder scaling at small sizes; measured fusion wins vs text-serialisation controls (the §3.2 falsifier's prior art); relational-benchmark practice | P3-D-GNN |
| **P3-LR-RULE** — rule-injection into transformers | [LIT] | Extends `reports/lit-llm-injection-priorart.md`: constrained/grammar decoding, KV-memory injection, steering/activation edits, adapter-encoded procedures, bottleneck architectures; per-placement evidence for the §3.3 table | P3-D-RULE |
| **P3-LR-COMP** — compression, dimension-pruning, interp-guided pruning | [LIT] | Structured pruning + rotation/absorb methods; SAE/dictionary-learning feature accounts and their pruning uses; published size-vs-capability curves at 100M–2B; whether ANY prior work dropped semantically-identified dimensions and backfilled from an external store (H-DD's closest prior art) | P3-D-DD |
| **P3-LR-EVAL** — evaluation + AI-index methodology | [LIT] | Composite-index construction and its failure modes; matched-size/matched-compute comparison methodology; contamination detection practice; energy/latency measurement practice; small-model benchmark floors | P3-D-INDEX (co-input with P3-MF-0), P3-D-BASE |
| **P3-LR-TINY** — tiny-model training + small-scale scaling laws | [LIT] | TinyStories/BabyLM/nanoGPT-class training recipes; what R-0-scale results have and have not predicted at 1B+; compute-matched twin-training practice | P3-D-GU, P3-D-BASE |
| **P3-MF-0** — measurement + fair-comparison framework design | [DESIGN] | §2 executed: draft KOT-FAIR/1 (index pins, size recipe, cost rig, decontamination screener, baseline rule, calibration plan) | P3-D-INDEX (its freeze vehicle) |

### Phase-1 — design beads (Fable; each blocked by its named Phase-0 parents)

| Bead | Type | Blocked by | Deliverable | Spawns |
|---|---|---|---|---|
| **P3-D-INDEX** | [DESIGN] | P3-MF-0 + P3-LR-EVAL | Frozen KOT-FAIR/1: KOT-AI-INDEX/1, KOT-SIZE/1, KOT-COST/1 + tooling + the pure-neural calibration prereg | P3-E-CAL |
| **P3-D-BASE** | [DESIGN] | P3-LR-EVAL + P3-LR-TINY | Baseline-set pins per rung + R-0 twin-training recipe + tuning-budget symmetry rules | (feeds every [EXP]) |
| **P3-D-GNN** | [DESIGN] | P3-LR-GNN + P3-LR-NSA | H-GNN-{ST,KV,LF} concrete designs + the text-of-graph control spec | P3-E-GNN-1 |
| **P3-D-RULE** | [DESIGN] | P3-LR-RULE + P3-LR-NSA | H-RULE placement designs, CD+KV first, incl. provenance/fail-closed instrumentation | P3-E-RULE-1 |
| **P3-D-DD** | [DESIGN] | P3-LR-COMP | The §3.5 dimension-drop experiment fully specified (alignment methods, rotation verification, arm matrix, TOST margins) | P3-E-DD-1 |
| **P3-D-GU** | [DESIGN] | P3-LR-TINY + P3-LR-NSA | Ground-up R-0 architecture(s) + matched-twin protocol | P3-E-GU-1 |
| **P3-D-VL** | [DESIGN] | none (may start with Phase-0; sharpened by P3-LR-NSA) | H-VL productisation design: loop + NL front-end integration + abstention policy; names its FK-NLB-3 dependency explicitly | P3-E-VL-1 |
| **P3-D-NLB** | [DESIGN] | none (shared infrastructure; = the FK-NLB-3 re-entry, co-owned with the standing programme) | The NL front-end that clears 0.90 retention + S2 fail-closed per vertical — the gate constraint ASM-0808(1) points at | P3-E-NLB-1 |

### Phase-2 — experiment beads (each: prereg-freeze → run → readout; all blocked by P3-E-CAL PASS except P3-E-CAL itself)

| Bead | Rung | Blocked by | Primary question (kill shape in §3/§7) |
|---|---|---|---|
| **P3-E-CAL** | — | P3-D-INDEX | Framework calibration on pure-neural models only; instrument gates, no architecture claim |
| **P3-E-NLB-1** | R-1 verticals | P3-D-NLB | Does the new parser clear 0.90 + S2 per vertical? (unblocks every real-input claim) |
| **P3-E-VL-1** | R-1 | P3-D-VL + P3-E-CAL (+P3-E-NLB-1 for the NL leg) | Does verify-retry move KOT-AI-INDEX/1 vs matched-cost baseline sampling? |
| **P3-E-GNN-1** | R-0/R-1 | P3-D-GNN + P3-E-CAL | Fusion vs text-of-graph vs no-graph at matched L2 (ASM-0805 resolver) |
| **P3-E-RULE-1** | R-1 | P3-D-RULE + P3-E-CAL | CD+KV placements vs H-VL external loop at matched accuracy on the dual ledger (ASM-0806 resolver) |
| **P3-E-DD-1** | R-1 | P3-D-DD + P3-E-CAL | The §3.5 five-arm central-claim test (ASM-0804 resolver) |
| **P3-E-GU-1** | R-0 | P3-D-GU + P3-E-CAL | Interface-present vs plain twin at matched training tokens |
| **P3-E-SCALE-2** | R-2 | ≥1 Phase-2 survivor + maintainer gate | First W1 attempt + first W2 Pareto sweep on the winner (designed then, not now) |

Dependency graph, flattened for the coordinator (arrows = "blocks"):

```
P3-LR-NSA ──────────────┬─► P3-D-GNN ─► P3-E-GNN-1 ─┐
P3-LR-GNN ──────────────┘                            │
P3-LR-NSA ──────────────┬─► P3-D-RULE ─► P3-E-RULE-1 ─┤
P3-LR-RULE ─────────────┘                            │
P3-LR-COMP ────────────────► P3-D-DD ──► P3-E-DD-1 ──┼─► P3-E-SCALE-2 (R-2 gate)
P3-LR-TINY ─────────────┬─► P3-D-GU ──► P3-E-GU-1 ──┤
P3-LR-NSA ──────────────┘                            │
(P3-D-VL, no Phase-0 block) ─► P3-E-VL-1 ────────────┘
P3-LR-EVAL ─┬─► P3-D-INDEX ─► P3-E-CAL ─► (every other P3-E-*)
P3-MF-0 ────┘
P3-LR-EVAL ─┬─► P3-D-BASE ──► (input to every P3-E-*)
P3-LR-TINY ─┘
(P3-D-NLB, shared infra) ─► P3-E-NLB-1 ─► (the NL leg of P3-E-VL-1 and all real-input claims)
```

Sizing note for the coordinator: the seven Phase-0 beads are parallel and
independent; P3-D-VL and P3-D-NLB may be beaded immediately alongside Phase-0
(their blockers are empty). Everything else is created by its parent bead on
completion, per the maintainer's fan-out instruction.

### What Phase-2 survivors spawn (Phase-3, named now, designed later)

R-2 promotion (P3-E-SCALE-2) → the first full W1 claim attempt; a W1 PASS at any
rung spawns the W2 shrink programme (Pareto sweep beads per §1.4); R-3 requires
the index-version design bead (KOT-AI-INDEX/2 scoping) plus a secured GPU
allocation (§6).

---

## 6. Compute, budget, and infrastructure (cheap-first)

- PREMISE: the free-compute pool documented for this programme spans Oxford ARC
  (free A100/H100/GH200, near-certain approval), AIRR Gateway (up to 10,000
  GPU-h), TPU Research Cloud, Modal for Academics (up to $10k serverless GPU),
  ~$1k-class inference-API credits, and an already-secured $100 Anyscale credit,
  with dollar ceilings explicitly not guarantees [LIT-BACKED:
  docs/next/free-compute-recon.md, consolidated 2026-07-10 — programme-internal
  recon, figures verified at their sources on that date].

Allocation policy by rung (all spend above the free pool is maintainer-gated per
ASM-0803):

- **Phase-0 + P3-MF-0 + P3-E-CAL:** local box (2 shared cores, `nice -n 10`,
  checkpointed — standing practice) + free API tiers. ~$0. Lit reviews are
  API/web-bound, not GPU-bound.
- **R-0:** local box for symbolic side + evals; single free GPU (Modal/ARC) for
  the H-GU twins. Inside the free pool.
- **R-1 (the decisive rung):** ARC + Modal academics; each family's falsifier is
  designed to fit ≤~50 GPU-h. The whole R-1 wave should fit inside ARC-free +
  Modal-credit capacity even if every family runs.
- **R-2:** ARC/Modal continue; AIRR Gateway application should be in flight
  during Phase-0 (its ~1-month award latency is the schedule-critical item, and
  applications cost nothing but form-filling).
- **R-3+:** hard-gated: requires a secured allocation (AIRR award or equivalent)
  AND a maintainer fork. No R-3 bead is created until both exist.
- **Operational discipline carried over:** Modal attached-run hygiene (explicit
  `modal app stop` after killing clients; nohup+setsid for long runs) per the
  standing programme memory; every run niced + checkpointed on the shared box.

Failure mode priced in: if no external GPU materialises, R-0 and the H-DD/H-VL
R-1 falsifiers (probe/rotation/eval workloads, no from-scratch training) remain
feasible on ARC-free alone; the programme degrades gracefully to its cheapest
decisive tests rather than stalling.

---

## 7. Honest risks and kill criteria

### 7.1 Programme-level kill

- DECISION: **K-P3 (verbatim):** if, after the R-1 wave completes (P3-E-VL-1,
  P3-E-GNN-1, P3-E-RULE-1, P3-E-DD-1, P3-E-GU-1 all read out) and the R-2 attempt
  P3-E-SCALE-2 has run for the best survivor, NO Programme-3 architecture has met
  W1 at R-2 — and the analyst post-mortems attribute the misses to fundamentals
  (coverage, integration, accounting) rather than to a diagnosed instrument
  failure — then the neurosymbolic-competitiveness thesis is judged weakened at
  small scale, no R-3 spend occurs, and the programme returns to the maintainer
  as a fork: kill, or re-scope to the strongest single surviving mechanism
  [STIPULATED: ASM-0803].

### 7.2 Named risks, each tied to current evidence

**R1 — the answer-key trap at programme scale (highest severity).** The whole
programme could "win" by encoding eval-adjacent content into stores. This is the
f2b confound (§2.2) writ large; the decontamination gate + deranged/aligned
controls are the mitigation, and the win-voiding rule is deliberately harsh.
Residual risk: paraphrase-level leakage below the screener's threshold — why the
screener design (P3-MF-0) includes an embedding channel and human spot-checks.

**R2 — the coverage wall may bind before any architecture question does.**
Measured coverage against external benchmark material is approximately zero today
(0/1,550 define-lane census; g8 0/1,000; m0b 0.3542 on the *friendliest* corpus —
§0). If kernel+world cannot cover index-relevant content at honest cost, H-VL,
H-RULE, and the store-side of H-DD have nothing to fire on, and every kernel-arm
index delta reads ≈0 regardless of mechanism quality. Mitigations: the coverage
censuses run FIRST inside each Phase-2 design (census-before-spend, standing
practice); the coverage-growth/ingestion line (`docs/next/
coverage-growth-ingestion-plan.md`) is a feeder workstream, and its costs count
inside the programme's honesty about mint-cost (unmeasured — A-F0 key-gated,
§0). This risk is the single most likely way Programme-3 dies, and it is
inherited, not new.

**R3 — the NL boundary is inherited by every real-input claim.** Both measured
crossings failed, one dangerously (§0). Programme-3's answer is structural: the
parser is inside the measured system (§1.1 NL-input integrity rule), P3-D-NLB is
shared infrastructure, and until P3-E-NLB-1 clears its gates every result is
formal-input-scoped by ASM-0808(1). The a5-nl lesson generalises: a wrong-but-
confident symbolic answer with provenance attached is WORSE than a refusal, so
fail-closedness is a scored dimension of every architecture (§3.3 table), not a
nicety.

**R4 — integration may not follow delivery (the nsk1 lesson).** For H-GNN and
H-RULE-ACT/HL especially: nsk1 showed content can be delivered into the residual
stream at echo grade while rescuing nothing, and text delivery measured net-
harmful (§0). Mitigation: every fusion design carries an integration endpoint
(does behaviour change on held-out uncovered-by-prompt items), never a delivery
endpoint alone; the placement ordering (§3.3) starts where integration is
enforced by construction (constrained decoding).

**R5 — H-DD rests on an unmeasured correspondence.** Stated at full prominence in
§3.5: nothing yet links kernel concept vectors to any model's internal subspaces,
and the 80%/5× target sits far beyond measured coverage. The risk is bounded by
the cheapness of P3-E-DD-1 and the arm matrix: even a total alignment failure
still yields a competent generic-compression baseline curve (arms iii/iv) that
serves W2. The distinctive claim dies cleanly if (i) ≈ (iii) — registered
resolution path on ASM-0804.

**R6 — the index is gameable by suite choice.** A suite chosen after seeing
results would be a thumb on the scale. Mitigation: the suite is pinned in
P3-D-INDEX before any architecture result exists, version-bumped only at rung
promotions, and the calibration experiment (P3-E-CAL) validates the instrument on
known-ordered pure-neural models first.

**R7 — small-scale findings may not transfer up the ladder.** R-0/R-1 kills could
discard architectures that only work at scale, and R-1 wins could evaporate at
R-2. This is accepted deliberately as the price of the maintainer's cheap-first
directive; the two-consecutive-rung kill rule (not one), plus per-rung
re-design freedom, is the hedge. Any claim about behaviour at unrun rungs is an
extrapolation and stays out of premises.

**R8 — relationship to the standing INCONCLUSIVE verdicts.** Programme-3 does not
assume either Programme-1/2 thesis true. If the correctness thesis eventually
resolves NOT-FEASIBLE (semantics unsound), Programme-3's stores degrade to "typed
records + checker" — which W1 can still legitimately win with (§0 re-aiming),
honestly labelled by the aligned-non-kernel control. If the efficiency de-confound
(knull / human f2b-transfer) resolves against kernel content, H-VL's prior weakens
sharply and its R-1 test inherits a mandatory aligned-generic-store arm — already
required by §2.2(3). The verdict-moving pending items of the old programme
(knull ablation, f2b-transfer Stage-1, g2) remain independently valuable to
Programme-3 and none is superseded by it.

### 7.3 What this document does NOT claim

No architecture herein is claimed likely to work; three of the six families start
from measured cautions and two from nothing. The claims this document actually
makes are: the objective is now falsifiably operationalised (§1), the comparison
can be made fair (§2), the design space is enumerated with per-family cheap
falsifiers (§3), and the work decomposes into a beadable lit-review-first
hierarchy (§5). Everything else is a hypothesis with a registered tag and a
priced test.

---

## Epistemic register (what this design relied on)

- **STIPULATED:** ASM-0800 (north-star operationalisation: index/size/cost +
  W1/W2); ASM-0801 (fair-comparison protocol + mandatory controls); ASM-0802
  (design-space enumeration + placement-test ordering); ASM-0803 (scaling ladder,
  promotion gates, K-P3); ASM-0807 (Phase-0→1→2 WBS); ASM-0808 (inherited
  constraint set).
- **EXTRAPOLATION (registered, never premises):** ASM-0804 (dimension-drop
  hypothesis), ASM-0805 (GNN-fusion advantage), ASM-0806 (internal-rules
  savings) — each with its named Phase-2 resolver.
- **MEASURED (restated strictly within their envelopes, §0):** the capstone
  verdicts and their constituent figures (l3a/a5, l3a-parse/a5-nl, f2b-replicate,
  g8, m0b via ASM-0001, nsk1 exploratory reads, a-e2-census upper bound,
  m0a-llmproxy precision).
- **LIT-BACKED:** the free-compute pool figures (docs/next/free-compute-recon.md,
  source-verified 2026-07-10).

This document changes no frozen object, no verdict, no audit, and no ASM outside
the fresh ASM-0800–0808 block.
