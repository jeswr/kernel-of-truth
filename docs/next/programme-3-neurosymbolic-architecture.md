# Programme-3: Neurosymbolic Architecture — programme design + hierarchical work-breakdown

> **Status: DESIGN document + work-breakdown for maintainer review. NOTHING here is
> frozen, pre-registered, scheduled, or run; no registry experiment record, verdict,
> audit, or frozen object is touched; no bead is created by this document (the
> coordinator beads §5 after review).**
> Author: Fable, chief-architect role (`kern/fable-designer`), 2026-07-11.
> **Revision: 2 (post-GPT-5.6).** Revision 1 (ASM-0800–0808) was sent for independent
> external review; the GPT-5.6 (gpt-5.6-sol) referee report is at
> `poc/gpt56-review/p3-review-20260711/review.md` and this revision answers it in
> full (five ranked concerns, eight technical errors, plus its per-family and
> work-breakdown recommendations). New stipulations from this revision live in the
> fresh append-only block **ASM-0810–0819**; the revision-1 block ASM-0800–0808
> stands in the registry with the superseded-in-part relations recorded in the new
> entries' notes (the registry is append-only; nothing is edited or deleted).
> Branch context: design-only commit; quality gates = `tools/registry/registry-check.py`.
>
> Inputs read at source: `docs/next/feasibility-synthesis.md` (the capstone verdict,
> 2026-07-11); `poc/gpt56-review/p3-review-20260711/review.md` (the external review,
> read in full); `registry/assessments/*.json` (esp. a-e2-census, l3a-parse, a5-nl,
> f2b-replicate, nsk1-*); `docs/next/architecture-ladder.md`;
> `docs/next/arch-survey.md`; `docs/next/benchmark-evaluation-strategy.md`;
> `docs/next/free-compute-recon.md`. Epistemic discipline: every PREMISE / DECISION /
> LOAD-BEARING line carries its `[TAG: ref]` on the same logical line; forward
> projections live in the register as EXTRAPOLATION entries and are **never
> premises**. External-literature citations introduced by the review (MLPerf,
> HELM, CLUTRR, LiveBench, Open-LLM-Leaderboard-v2, Sardana et al., the ICLR-2025
> test-time-compute result) are carried here as REVIEW-CITED design motivations —
> they are load-bearing for *what the lit-reviews must verify*, and become
> LIT-BACKED only after the named P3-LR-* bead verifies each at source.

---

## CHANGELOG (revision 2, each line → the review section it answers)

- **Replaced the ±10% size/compute BANDS with a resource-constrained FRONTIER** (budget
  vector; comparator may be smaller/cheaper; staircase/Pareto envelope reporting;
  win claim narrowed to pre-registered reproducible open comparators) → review §1
  "The ±10% matching rule is gameable" / ranked concern #1.
- **Replaced KOT-COST/1's neural-FLOP-only "same compute" with KOT-COST/2, a full
  RESOURCE VECTOR** (accelerator ops, CPU-seconds, bytes read, energy, memory,
  latency percentiles, throughput, warm/cold cache, TTFT/inter-token, output-length
  control), renamed the FLOP ledger a *neural-FLOP diagnostic*, and fixed the W1
  energy inconsistency (energy now binds in W1) → review §1 "'Same compute' is
  underspecified" + technical error #7.
- **Expanded KOT-SIZE to KOT-SIZE/2** (canonically-packed minimal bytes, compressed
  distribution bytes, warm RAM/VRAM, cold-start working set + bytes read,
  construction size+cost, remote dependencies; base image FROZEN before any
  architecture development) and **added the lifecycle ledger KOT-LIFE/1** (donor
  provenance, tuning/HP-search compute, store authoring/review costs, amortisation
  at 10^3/10^6/10^9 queries) → review §1 "Deployment size is useful, but not
  sufficient".
- **Corrected the statistics**: W1 now requires LCB95(INDEX(S)−INDEX(B)) > δ_k
  (not point-above-δ with LCB>0), simultaneous/family-wise error control across
  comparators, hierarchical bootstrap over benchmark families and items preserving
  paired predictions; the TOST mislabel is corrected (non-inferiority = single
  one-sided test/CI vs the margin; TOST = equivalence) → review §1 "Statistical
  specification needs correction" + technical errors #1, #2.
- **Rebuilt the AI index as KOT-AI-INDEX/2**: chance/ceiling-normalised scores,
  macro-average within capability domains then across, domain vector + scalar both
  published, HELM-like multi-scenario structure; added R-0 held-out LM loss +
  BLiMP/EWoK + procedural relational suites, neurosymbolic diagnostics
  (CLUTRR/ProofWriter-RuleTaker/FOLIO with held-out rules, compositions, depths,
  paraphrases), R-3+ MMLU-Pro/BBH-or-BBEH/IFEval/code + a frozen LiveBench release,
  and a versioned sealed contamination-resistant secondary; MMLU-cloze dropped as a
  cross-rung component; the old 9-task suite demoted to the **SmolLM2 continuity
  index (KOT-SMOL-CONT/1)**, never the headline → review §"The AI index" / ranked
  concern #2.
- **Encoded the NL/coverage wall in the dependency graph**: NLB now gates ALL
  natural-input store use (GNN retrieval, KV rules, constrained decoding, H-DD
  store reinjection), with the only alternative being explicitly-labelled
  ORACLE-input diagnostics that make NO W1 claim; P3-D-NLB is now blocked by the
  semantic-parsing/selective-prediction lit-review; the explicit NL→program-synthesis
  family (H-PS) added as first-class → review §5 "not fully encoded in
  dependencies" + §2 "Rule placement" / ranked concern #3.
- **Reformulated H-DD**: the incorrect rotation-invariance, SAE-orthogonality,
  80%-width→5×-size, and attention-provenance claims are corrected; the design now
  requires deriving the donor's exact invariance group, gives an explicit
  parameterisation for any size claim (bytes measured, never inferred from width),
  adds a cheap 5-step CAUSAL GATE (P3-E-DD-0) before the arm experiment, and
  compares against the strongest RETRAINED structured-pruning + distillation
  baselines → review §2 "Dimension drop" / ranked concern #4 + technical errors
  #3, #4, #5, #6.
- **Strengthened baselines and controls**: matched generic neural-RAG/tool-use
  control (same corpus, retriever, index, budgets) added as mandatory; factorial
  control design (content-type × retrieval-architecture × executor, incl. label
  permutation, structurally-matched irrelevant records, edge shuffling); baseline
  optimisation must include quantisation, structured pruning, distillation,
  retrieval, and optimised/adaptive test-time compute; tuning symmetry = matched
  TOTAL tuning compute with fixed selection rules, not config counts; sealed
  post-freeze evaluation added (decontamination alone cannot certify fairness) →
  review §1 "Baselines need strengthening" + "Decontamination … cannot certify
  fairness" / ranked concern #5.
- **Reorganised the ladder around information-gaining GATES** (G1 coverage-ceiling →
  G2 oracle-interface → G3 boundary-degradation → G4 full-system-vs-frontier →
  G5 scaling-across-two-sizes) so failures localise; added the verifier-loop
  coverage upper-bound kill (Δ_max ≤ Σ_b w_b κ_b (1−a_b^cov), computable without
  GPU); fixed the W2 inconsistency (the R-2 Pareto sweep is W1-conditional; earlier
  compression curves are labelled DIAGNOSTIC); NLB and coverage work no longer wait
  for index calibration → review §3 "Scaling ladder and cost approach".
- **Hardened the programme kill (K-P3v2)**: the subjective "analysts attribute misses
  to fundamentals" escape hatch is replaced with six pre-registered QUANTITATIVE
  kill conditions, and the default on W1 failing everywhere through R-2 is
  TERMINATE-the-competitiveness-programme (restart requires a new proposal), not an
  open-ended maintainer fork → review §5 "The programme-level kill is too soft".
- **Corrected the §7.3 overstatement**: the comparison has been made *auditable in
  several respects*, NOT shown "capable of being made fair" (training-data
  contamination of closed corpora, lifecycle cost, baseline-search completeness,
  and packaging/frontier gaming remain unresolved) → review §5 "it overstates one
  conclusion".
- **Rebuilt Section 5**: Phase-0 expands to ten lit-review beads (evaluation/index
  methodology; systems/lifecycle benchmarking; RAG/structured-retrieval/KG/tool-use
  baselines; semantic parsing/program synthesis/selective prediction; neural
  theorem proving/differentiable logic/proof-trace distillation; GNN-LLM fusion +
  neurosymbolic integration; rule-injection; model surgery/compression invariances;
  store authoring/knowledge-update economics; tiny-model training) plus the eight
  missing design tasks the review names (threat model, neural frontier-builder,
  coverage×gain power analysis, sealed benchmark, generic-RAG control, oracle-to-NL
  decomposition, hardware repeatability protocol, lifecycle amortisation), with the
  full dependency graph and the measurement-framework pieces that must land before
  ANY Phase-2 experiment → review §4 "Work breakdown".
- **Per-family fixes**: H-VL comparator set expanded (compute-optimal sampling,
  learned neural verifier, generic structured RAG, grammar decoding, non-kernel
  store) + the G1 coverage kill; H-GNN falsifier rescoped (tiny-graph text-win does
  not kill the family; graph-size/reasoning-depth sweep + six controls + four-stage
  decomposition); H-RULE claims tightened (CD is transport, not inference; KV/HL
  provenance requires causal validation; Pareto-frontier endpoint, not cost parity
  alone); H-GU gets a ≥3-point width/token sweep testing scaling direction + the
  five missing training variants → review §2 "Architecture bets".

---

## 0. What Programme-3 is, and what it inherits

The maintainer's intent, restated: use something *like* the kernel + world
information this programme has built to create **neurosymbolic AI architectures**
that (1) achieve a **higher AI index than comparably-resourced models**, and then
(2) find how **small** the whole system (model + kernel + world + everything else)
can be made while staying competitive on that index. Because the system is
neurosymbolic, size cannot be parameters: size is **deployment bytes** plus a full
**inference resource vector**. Start very small to learn cheaply which
architectures work; then continuously scale while improving them. (The review is
right that the literal "higher than ALL other models of the same size and compute"
is not a testable claim; §1.4 narrows what W1 actually licenses — the maintainer's
north-star is preserved as the *aspiration*, the testable claim is the frontier
statement.)

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

Three consequences shape everything below.

- DECISION: Programme-3 adopts the four inherited hard constraints — (1) no
  real-input claim without an FK-NLB-3-class NL front-end gate cleared per vertical;
  (2) every kernel-contribution claim carries deranged-store + aligned-non-kernel
  controls; (3) coverage numbers stay corpus/rung/kernel-state-indexed; (4)
  membership/compression figures are upper bounds until a consumption channel is
  measured [STIPULATED: ASM-0808].
- DECISION: constraint (1) is strengthened from a claims rule to a DEPENDENCY rule —
  every experiment whose store is addressed from natural input (verifier-loop NL
  legs, GNN retrieval from NL queries, KV rule-firing from NL, constrained decoding
  over NL prompts, H-DD store reinjection on NL tasks) is BLOCKED by the NLB gate
  (P3-E-NLB-1 clearing 0.90 retention + S2 fail-closed per vertical), OR runs on
  ORACLE inputs (gold parses/subgraphs/record addresses) and is labelled
  `oracle-diagnostic` in its prereg, licensing NO W1 claim and no real-input claim
  of any kind [STIPULATED: ASM-0814; the review's ranked concern #3 verbatim].
- DECISION: Programme-3's headline claims are **system-level competitive claims**
  (index at a pre-registered resource budget), not kernel-content-attribution
  claims — this is a deliberate re-aiming: even if a win turns out to be "aligned
  typed store + checker" rather than "NSM semantics", it still satisfies the
  maintainer's north-star, and the attribution question is carried as a separate,
  honest, secondary analysis rather than a blocker [STIPULATED: ASM-0800].

Relation to the existing L0–L4 ladder (`docs/next/architecture-ladder.md`): the
ladder enumerated *where the kernel can touch a model*; Programme-3 reuses those
seams as components but changes the objective function from "make the kernel more
central" to "beat the resource-constrained baseline frontier on a pinned index,
then shrink". Rules-placement options in §3.3 map onto L2a/L2b/L3c; the GNN fusion
family extends the A2/E5 trained-bridge seam; the verifier-loop system is F2b
productised; the program-synthesis family (H-PS, new in this revision) is the
direct attack on the measured NL boundary.

---

## 1. North-star and falsifiable success criteria

### 1.1 The AI index — KOT-AI-INDEX/2 (domain-structured), plus the continuity index

The review's diagnosis is accepted in full: revision 1's nine-task suite is seven
correlated multiple-choice commonsense/factual tasks plus two others, raw-averaged
across different chance floors and variances — adequate as a *SmolLM2 harness
continuity* instrument, inadequate as a headline capability index [STIPULATED:
ASM-0811, answering review ranked concern #2].

- DECISION: the headline "AI index" is **KOT-AI-INDEX/2**, constructed as follows.
  (1) Every per-benchmark score is normalised against its chance floor and a pinned
  ceiling: s̃ = (s − chance)/(ceiling − chance), with the ceiling pinned at index
  freeze (published human/large-reference performance where it exists, else a named
  pinned reference model's own-harness score). (2) Normalised scores are
  macro-averaged first WITHIN capability domains, then across domains, HELM-style
  (multi-scenario, multi-metric — REVIEW-CITED: Stanford HELM; verified by
  P3-LR-EVAL before freeze). (3) Every publication reports the **domain vector AND
  the scalar**; the scalar exists for ranking, the vector for honesty — no
  Programme-3 claim may quote the scalar without the vector one link away.
  (4) Suite membership, domain assignment, normalisation constants, harness
  version, prompts, and scoring are all pinned in the P3-D-INDEX freeze; any change
  is an index VERSION change that re-baselines everything [STIPULATED: ASM-0811].

Provisional domain structure (final membership fixed by P3-D-INDEX after
P3-LR-EVAL verifies floors/ceilings at each rung; REVIEW-CITED benchmark
suggestions adopted pending source verification):

| Domain | R-0 | R-1/R-2 | R-3+ additions |
|---|---|---|---|
| D1 linguistic competence | held-out LM loss (pinned corpus) + BLiMP + EWoK (BabyLM-style) | same, plus above-floor generation probes | — |
| D2 commonsense/world | — (floors) | reduced MC set: HellaSwag, PIQA, WinoGrande | — |
| D3 knowledge/factual | — | ARC-Easy/Challenge, OpenBookQA | MMLU-Pro |
| D4 relational/rule reasoning (the neurosymbolic diagnostics) | small procedural relational + rule-reasoning suites (synthetic, generator-pinned) | CLUTRR; ProofWriter/RuleTaker; FOLIO — each with held-out rules, held-out relation compositions, held-out proof depths, and lexical paraphrase splits (REVIEW-CITED: CLUTRR arXiv:1908.06177) | deeper splits of the same |
| D5 math/procedural | — | GSM8K (above floor only) | BBH or BBEH where discriminative |
| D6 instruction following | — | IFEval iff above floor at R-2 | IFEval |
| D7 code | — | — | one pinned code benchmark + frozen LiveBench release (REVIEW-CITED: LiveBench — each release versioned, never silently folded in) |
| S sealed secondary | §2.2a: sealed/refreshed suite, versioned per release, produced post-freeze | same | same |

- DECISION: **MMLU-cloze is dropped as a stable cross-rung component** — the
  programme's own benchmark-evaluation notes record inconsistent SmolLM2 MMLU
  variants across sizes; MMLU-family measurement enters only at R-3+ as MMLU-Pro
  under the pinned harness [STIPULATED: ASM-0811; answers review "MMLU-cloze is
  particularly problematic"].
- DECISION: the revision-1 nine-task suite is retained VERBATIM as
  **KOT-SMOL-CONT/1, the SmolLM2 continuity index** — used for anchor continuity
  with the host family's published numbers and for harness calibration
  (P3-E-CAL), reported alongside KOT-AI-INDEX/2, never as the headline and never
  in W1 [STIPULATED: ASM-0811; answers review "Keep the current suite as 'SmolLM2
  continuity index'"].

Alternatives considered: the HF Open-LLM-Leaderboard-v2 set
(IFEval/BBH/MATH/GPQA/MuSR/MMLU-Pro) remains the right R-3+ general-capability
anchor family but floors out at ≤500M (REVIEW-CITED, consistent with revision 1's
own reading); ARC-AGI-class suites measure a different construct.

Two standing index rules (carried from revision 1, unchanged in force):

- DECISION: the index always reports the **full vector** (per-benchmark scores,
  refusal/abstention rates, and the covered-vs-uncovered split where a store is in
  play) alongside the scalar [STIPULATED: ASM-0811, continuing ASM-0800(1)].
- DECISION: NL-input integrity — index items are consumed as their natural
  benchmark text; no arm may receive hand-formalised inputs; any store-touching
  arm therefore either includes its NL front-end inside the measured system or
  abstains on what it cannot parse. This is the anti-l3a/a5 rule: the parser is
  part of the product, and its failures are the system's failures [STIPULATED:
  ASM-0808].

### 1.2 Size — KOT-SIZE/2 (the six-figure size protocol)

Raw on-disk bytes remain the maintainer-directed primary, but packaging is a gaming
surface (serialization format, padding, duplicated metadata, what migrates into the
"free" base image) [STIPULATED: ASM-0810, answering review "Deployment size is
useful, but not sufficient"].

- DECISION: size is reported as SIX pinned figures, with figure (1) primary:
  (1) **canonically-packed, minimally-sufficient artifact bytes** — a pinned
  canonical packing script (deterministic serialization, no padding, deduplicated
  metadata) applied identically to every arm; (2) compressed distribution bytes
  (zstd-19, pinned level); (3) warm resident RAM/VRAM while serving; (4) cold-start
  working set + total bytes read to first answer; (5) index/store construction
  size and construction cost (feeds KOT-LIFE/1); (6) any remote service, cache, or
  corpus dependency — a system with a remote dependency CANNOT claim a smaller
  deployment than one without it; remote bytes count or the claim is void
  [STIPULATED: ASM-0810].
- DECISION: the **common base image is FROZEN (content-hashed) before any
  architecture development begins** — P3-D-INDEX's first deliverable; anything a
  system needs beyond the frozen image counts as its bytes. This closes the
  "migrate custom functionality into the free base" channel the review names
  [STIPULATED: ASM-0810].

There is no "the kernel is free" accounting, ever. Quantisation games are
symmetric: if the neurosymbolic arm quantises, every comparator gets the same
best-effort quantisation (via the frontier-builder, §2.3).

### 1.3 Inference cost — KOT-COST/2 (the resource vector) + the neural-FLOP diagnostic

The review's technical error #7 is accepted: a ledger in which symbolic
computation enters at zero is not a compute measure — a system doing substantial
CPU search, retrieval, decompression, or I/O could look "compute-matched" by
definition. Revision 1's L1 is therefore RENAMED and DEMOTED to what it actually
is, and the binding ledger becomes a full resource vector [STIPULATED: ASM-0810].

- DECISION: inference cost is the measured **resource vector KOT-COST/2**, per
  query and per suite, on pinned hardware under the P3-D-HW repeatability
  protocol: (a) accelerator time + estimated accelerator ops; (b) CPU-seconds;
  (c) bytes read from storage and network; (d) energy (RAPL on CPU,
  NVML/`nvidia-smi`-class counters on GPU, whole-run integration — not query-level
  spot reads); (e) peak accelerator memory AND host RSS; (f) end-to-end latency at
  p50 and p95; (g) throughput under a pinned concurrency distribution; (h) warm-
  and cold-cache conditions both measured, including startup/index-load time;
  (i) time-to-first-token and inter-token latency for generative arms; (j) output
  length controlled (pinned max-token + stop discipline) or cost normalised per
  emitted token, pinned per benchmark. Methodology borrows MLPerf inference +
  power measurement discipline (REVIEW-CITED: MLPerf inference-datacenter
  benchmarks + MLPerf power methodology; verified and operationalised by
  P3-LR-SYS → P3-D-HW before the framework freezes) [STIPULATED: ASM-0810].
- DECISION: the analytic neural-FLOP ledger survives as the **neural-FLOP
  diagnostic** (2·params·tokens + attention terms, pinned formula sheet): useful
  to keep the neural parts honest and hardware-independent, REPORTED always,
  BINDING never — no "compute-matched" claim may cite it alone [STIPULATED:
  ASM-0810; corrects technical error #7].

Precedent that the symbolic side can be genuinely cheap on the measured vector —
and that the accounting has to be measured, not assumed:

- PREMISE: the deterministic engine answers covered queries at 5.29–7.82 µs/query,
  and the f2b system-level cost ratio vs the 1.7B host was measured at 0.103
  [MEASURED: registry/verdicts/l3a.json + registry/verdicts/a5.json engine timing;
  registry/verdicts/f2b-replicate.json cost_ratio_vs_R3].

### 1.3a The lifecycle ledger — KOT-LIFE/1

The comparison this programme runs is a *deployment-efficiency* comparison, not an
equal-total-investment comparison — legitimate, but it must be named accurately
and priced [STIPULATED: ASM-0810, answering review "add a lifecycle ledger"].

- DECISION: every W1-relevant system (S and every comparator) publishes a
  **lifecycle ledger**: (1) donor pretraining provenance and compute where known
  (dimension-drop arms *inherit* their donor's training compute — stated, never
  netted out); (2) architecture fine-tuning + hyperparameter-search compute
  actually spent (the tuning-symmetry audit trail, §2.3); (3) store costs:
  authoring, parsing, embedding, indexing, and human review, in hours and $;
  (4) total cost of ownership amortised at three pinned deployment volumes —
  10^3, 10^6, 10^9 queries — using the measured KOT-COST/2 energy/latency figures.
  Training longer to obtain a smaller model is a real deployment strategy and
  optimal size depends on inference volume (REVIEW-CITED: Sardana et al., "Beyond
  Chinchilla-Optimal"; verified by P3-LR-SYS). The ledger CO-REPORTS with every W1
  claim and feeds kill condition K-P3v2(6); it does not gate W1 numerically
  because store-authoring hours and GPU-hours have no non-arbitrary common unit —
  the honesty mechanism is mandatory publication + the kill condition, not a
  fudged exchange rate [STIPULATED: ASM-0810].

### 1.4 The exact win condition and the exact shrink objective

The revision-1 ±10% band construction is WITHDRAWN as gameable (padding into a
favourable band; dodging a strong model just outside it; empty band
intersections; losing to a smaller/cheaper dominator while "winning the
neighbourhood") [STIPULATED: ASM-0810, accepting review ranked concern #1 in
full].

**W1 (the resource-frontier competitive claim), verbatim:** at rung R-k, with a
pre-registered resource budget vector
`B_k = (max canonically-packed deployment bytes; max p95 latency; max energy/query;
max peak accelerator memory + host RSS)`, a Programme-3 system S beats the
baseline frontier iff, under the frozen KOT-AI-INDEX/2 version for that rung,
own-harness:

1. **Admissibility:** S fits within EVERY component of B_k, measured under
   KOT-SIZE/2 + KOT-COST/2, warm and cold conditions per the P3-D-HW protocol
   (energy explicitly binds here — fixing revision 1's omission of energy from
   W1 while KOT-COST claimed it); and
2. **Frontier dominance:** for EVERY comparator C in the pre-registered comparator
   set F(B_k) — every pre-registered, reproducible open comparator and baseline
   family that fits within every component of B_k, explicitly INCLUDING systems
   smaller or cheaper than S, each optimised for the budget by the frontier-builder
   (§2.3) — the simultaneous one-sided 95% lower confidence bound satisfies
   `LCB95(INDEX(S) − INDEX(C)) > δ_k`, with family-wise error control across the
   comparator set and a hierarchical bootstrap over benchmark families and items
   preserving paired predictions (§2.5); and
3. the decontamination audit (§2.2) AND the sealed-evaluation consistency gate
   (§2.2a) pass; and
4. the factorial controls (§2.2) behave as pre-registered (derangement/permutation
   destroys any store-content-attributed component; the aligned-non-kernel and
   matched-generic-RAG results are REPORTED as the attribution split, whatever
   they show); and
5. the lifecycle ledger (§1.3a) is published alongside.

Reporting: the full **staircase/Pareto envelope** of neural and neural-retrieval
points across budgets (index vs bytes, index vs cost) is published with S plotted
against it — W1 means S lies significantly above the envelope at its budget, not
that it won a favourable neighbourhood.

**Scope of the claim licensed by a W1 PASS, verbatim:** "S exceeds every
pre-registered, reproducible open comparator and baseline family searched under
budget B_k by ≥ δ_k on KOT-AI-INDEX/2-vN" — NEVER "higher than all other models of
the same size and compute"; the literal universal is untestable and is hereby
retired from every claim surface [STIPULATED: ASM-0810].

**W2 (the shrink objective), verbatim:** once W1 first holds at any rung, minimise
KOT-SIZE/2 figure-(1) bytes subject to `INDEX(S) ≥ INDEX(M_ref)` where M_ref is a
named, pinned open reference model (initial M_ref = SmolLM2-1.7B own-harness;
revisited by maintainer fork per index version). The deliverable is the measured
**Pareto frontier over (bytes, resource vector, index)**; headline success = at
least one point that strictly dominates every measurable open point at the small
end. Consistency rule (fixing the review's W2 finding): the R-2 sweep inside
P3-E-SCALE-2 runs ONLY conditional on W1 passing at R-2; any compression curve
produced before a W1 PASS (e.g. H-DD dose-response curves) is labelled
**DIAGNOSTIC**, never W2 [STIPULATED: ASM-0817].

Falsifiability: W1 is falsified per-rung by failing its own margin against the
frontier; the programme has quantitative kill conditions in §7. There is no
"moral victory" clause: frontier parity is a FAIL of W1, however interesting the
architecture.

---

## 2. The measurement + fair-comparison framework (where the programme lives or dies)

Comparing a neurosymbolic system against the neural/RAG frontier at a fixed
resource budget is the single hardest methodological problem here — harder than
any individual architecture. The framework is frozen as **P3-MF (KOT-FAIR/2)**
before any Phase-2 W1-relevant experiment freezes, and it now begins with an
explicit threat model.

### 2.0 The threat model (new; P3-D-THREAT)

- DECISION: KOT-FAIR/2 includes a formal **resource/baseline threat model**: an
  enumerated adversary analysis of how each metric can be gamed by either side —
  packaging games (padding, base-image migration, remote dependencies), band/
  frontier games (comparator dodging, budget shopping), cost games (warm-cache-only
  reporting, output-length inflation/deflation, batch-size shopping,
  symbolic-work-hiding), index games (suite shopping, abstention gaming, domain
  reweighting), store games (answer-key encoding, error-analysis-driven authoring,
  researcher adaptation to the frozen suite), and tuning games (unequal search
  compute behind equal config counts) — each with its named mechanised counter in
  this section. The threat model is a frozen artifact; a game not counterable at
  freeze time is documented as a standing limitation on every claim it touches
  [STIPULATED: ASM-0812; answers review §4 "formal resource/baseline threat
  model"].

### 2.1 Confound A — size/packaging asymmetry

Answered by KOT-SIZE/2 (§1.2): canonical packing script, six co-reported figures,
frozen base image, remote-dependency rule, artifact-freeze (store hash pinned at
eval time, so "grow the store after measuring" is impossible by construction), and
peak-RSS/cold-start measurement so lazily-paged stores pay their true cost on the
resource vector.

### 2.2 Confound B — the answer-key problem (the deepest one)

A store can encode benchmark answers far more directly than weights can. The f2b
lesson is exactly this in miniature:

- PREMISE: the f2b verifier accepts iff the answer string-equals the canonical
  record while gold is DEFINED by that same equality, so the measured +0.1507 is
  provably consistent with "aligned answer key + retry", and the shuffled control
  cannot discriminate content from alignment [MEASURED:
  registry/assessments/f2b-replicate.json does_not_license].

Mechanised answers, all mandatory for any W1 claim [STIPULATED: ASM-0812]:

1. **Decontamination audit (hard gate, win-voiding):** automated n-gram overlap +
   embedding-similarity screen of every kernel/world/store record against every
   item of the frozen index suite, pinned threshold, human spot-check protocol on
   flagged pairs; stores may not be authored, selected, or grown using any index
   item, its paraphrase, or its source page. A win whose store fails the audit is
   VOID, not caveated. (Neural baselines carry the standard training-data
   contamination caveat symmetrically: we report known contamination status of
   baseline corpora but cannot audit closed corpora — an asymmetry that favours
   the baselines' scores, i.e. conservative for us.)
2. **The factorial control design** (replacing revision 1's derangement-centric
   list — derangement alone changes alignment and retrieval behaviour
   simultaneously and cannot localise what mattered): controls span
   **content-type × retrieval-architecture × executor**, drawn per experiment from:
   (a) seed-pinned deranged store→item addressing (the f2b control, inherited);
   (b) label permutation within records; (c) irrelevant-but-structurally-matched
   records (same schema, types, sizes; unrelated content); (d) edge/relation
   shuffling for graph arms; (e) the aligned-non-kernel store (matched-size,
   matched-alignment, plain-English typed records — the knull lesson); (f) the
   **matched generic-RAG/tool-use control** (§2.3, the strongest missing control);
   (g) kernel-as-text null at matched token budget (the null Programme-1/2 never
   lost to and that nsk1-g2d showed can be actively harmful — stays mandatory).
   Each Phase-2 prereg names which cells it instantiates and what each
   discriminates [STIPULATED: ASM-0812; answers review "Use a factorial control
   design"].

### 2.2a The sealed evaluation (new; P3-D-SEAL)

Decontamination screening is necessary but CANNOT certify fairness: it misses
benchmark-source knowledge encoded as rules/abstractions, selective store
authoring guided by benchmark error analysis, paraphrases below threshold,
contamination already in donor weights, and repeated researcher adaptation to the
frozen suite (the review's list, adopted verbatim) [STIPULATED: ASM-0812].

- DECISION: every W1 claim additionally requires a **sealed evaluation**: a
  secondary suite produced AFTER architecture + store freeze, by an independent
  party or a pinned procedural generator, unseen by every developing agent;
  for store-based systems it includes temporally-fresh facts and/or independently
  held-out domains. The sealed suite is versioned per release (LiveBench-style
  refresh discipline — each release a new version, never silently folded in). Gate
  shape: the sealed-suite result must be directionally consistent with the frozen
  suite (pre-registered consistency band); a large frozen-vs-sealed gap voids the
  win pending diagnosis [STIPULATED: ASM-0812].

### 2.3 Confound C — baseline strength, the frontier-builder, and tuning symmetry

- DECISION: the comparator set F(B_k) is built by a standing **neural
  frontier-builder** (P3-D-FRONTIER): for each pre-registered budget B_k it
  produces the strongest baselines that fit, drawing on (i) the strongest open
  pure-neural models at or below budget (pinned name+revision at freeze);
  (ii) budget-optimising transforms — quantisation, structured pruning,
  distillation — applied best-effort to those models; (iii) **neural + retrieval:
  a conventional RAG / tool-use architecture over the SAME corpus, SAME
  retriever/index, SAME budgets as the kernel arm** (the strongest missing control
  — the aligned-non-kernel store does NOT replace it); (iv) optimised/adaptive
  test-time compute — best-of-k self-consistency alone is too weak; the builder
  implements compute-optimal adaptive strategies (REVIEW-CITED: the ICLR-2025
  test-time-compute result; verified by P3-LR-RAG/P3-LR-EVAL) and learned/neural
  verifiers where budget permits; (v) training-compute-matched from-scratch twins,
  required only where the neurosymbolic arm itself trains from scratch (H-GU)
  [STIPULATED: ASM-0812].
- DECISION: the six-way attribution factorisation is a standing analysis
  requirement: any observed win must be decomposed as far as the control cells
  allow across **kernel semantics vs structured storage vs retrieval vs
  deterministic execution vs retry/search vs neural-symbolic integration** — the
  factorial cells in §2.2(2) + the RAG control are exactly the instruments for
  this [STIPULATED: ASM-0812].
- DECISION: tuning symmetry binds on **total tuning compute** (accelerator-hours +
  CPU-hours actually spent on search, logged per arm into KOT-LIFE/1), with a
  FIXED, pre-registered selection rule on a dev split disjoint from the index
  suite — equal config counts are NOT sufficient (configs differ enormously in
  cost). An architecture that only wins with more search compute has not won
  [STIPULATED: ASM-0812; corrects revision 1's config-count rule].

### 2.4 What P3-MF-0 must deliver (the framework as an artifact)

A frozen `KOT-FAIR/2` spec: the threat model (§2.0); index suite pins + domain
structure + normalisation constants (§1.1); the KOT-SIZE/2 canonical packing
script + six-figure recipe + frozen base image hash; the KOT-COST/2 measurement
rig + the P3-D-HW hardware-repeatability and warm/cold protocol; the KOT-LIFE/1
ledger template; the decontamination screener; the sealed-eval production
protocol; the frontier-builder spec + comparator pinning rule; the statistical
analysis plan (§2.5); and a **calibration report**: the full framework run on
pure-neural models ONLY (135M vs 360M vs 1.7B), demonstrating that the index
separates known-ordered models with the expected ordering and stable variance,
and that the cost rig reproduces across days/reboots within its pre-registered
repeatability band — the instrument is validated on cases with known answers
before it ever judges a neurosymbolic system. Phase-0/1 work on the local box +
free credits, ~$0.

### 2.5 Statistical specification (corrected)

- DECISION: the house statistical rules for Programme-3, correcting revision 1's
  two errors [STIPULATED: ASM-0813; answers review "Statistical specification
  needs correction" + technical errors #1/#2]:
  1. **Margin wins:** a margin-δ superiority claim requires
     `LCB95(INDEX(S) − INDEX(B)) > δ` — the lower confidence bound itself clears
     the margin. A point estimate above δ with an LCB merely > 0 is NOT a margin
     win and is never reported as one.
  2. **Multiplicity:** S is tested against multiple comparators (and multiple
     domains): use simultaneous confidence bounds / family-wise error control
     across the pre-registered comparator set; the FWER procedure is pinned in the
     analysis plan at freeze.
  3. **Resampling:** hierarchical bootstrap across benchmark families and items,
     preserving paired predictions (same items, per-system outputs paired).
  4. **Non-inferiority vs equivalence:** a "retains capability" claim is
     NON-INFERIORITY and uses a single one-sided test / one-sided CI against the
     pre-registered non-inferiority margin. TOST (two one-sided tests) is an
     EQUIVALENCE procedure and is reserved for genuine equivalence claims. All
     revision-1 uses of "TOST" for retention claims (the H-DD central claim
     included) are corrected accordingly.
  5. One primary endpoint per experiment; kill criteria verbatim in the prereg;
     verdicts generated by the mechanical grader and cross-vendor audited, per
     standing practice.

---

## 3. Architecture design space — named hypotheses

- DECISION: the design space is enumerated as the named families below — revision 2
  adds **H-PS (NL→program synthesis)** as a first-class family per the review; the
  enumeration is a scoping choice covering the maintainer's directed directions
  plus the seams Programme-2 built, and confers no evidence on any family
  [STIPULATED: ASM-0802 + ASM-0815].

Evidence-status legend, tied to §0's premises: **supported** (a measured positive
exists at some scope), **cautioned** (a measured negative or unresolved result
bears directly), **unmeasured** (no programme evidence either way). Forward
projections are registered: H-GNN → ASM-0805, H-RULE → ASM-0806, H-DD → ASM-0804 —
all EXTRAPOLATION, never premises. Every family's experiments are structured by
the G1–G5 gate ladder (§4); oracle-input stages are labelled `oracle-diagnostic`
and license no W1 claim [STIPULATED: ASM-0814].

### 3.1 H-VL — the verifier-loop system (small model + kernel-verify-retry, productised)

The one audited end-task SIGN, promoted from experiment to *system design*: a
small LM generates; the deterministic engine checks covered claims; failed checks
trigger bounded retry/abstain; the whole loop (with its NL front-end) is the
product being indexed.

- Rationale: the only family with a measured system-level cost win shape
  (+0.1507 at ~10% cost — formal inputs, alignment-confounded; §0).
- Evidence status: supported at formal-input scope; cautioned by the NL-boundary
  FAILs (the loop's real-input version does not exist until the NLB gate clears)
  and by the unresolved attribution (knull / human f2b-transfer unrun).
- **G1 coverage upper-bound kill (run FIRST, no GPU):** compute
  `Δ_max ≤ Σ_b w_b · κ_b · (1 − a_b^cov)` where w_b is benchmark b's index weight,
  κ_b the store-covered fraction of its items, and a_b^cov the baseline's accuracy
  on covered items — the index gain if EVERY covered item were corrected
  perfectly. If Δ_max < δ_k, the index-mover claim is killed on paper
  [STIPULATED: ASM-0817; the review's formula adopted verbatim]. Given the
  measured external coverage (§0: 0/1,550 define-lane, g8 0/1,000, m0b 0.3542
  friendliest-corpus), this gate is expected to bind hard and early — that is its
  job.
- G4 comparator set (expanded per the review): compute-optimal/adaptive neural
  sampling (not naive best-of-k); a learned neural verifier at matched budget;
  generic structured RAG over the same corpus; grammar/constrained decoding
  without the engine; the same loop with the aligned non-kernel store and with
  the matched generic store.
- Cheapest falsifier: G1 above (~$0); then, if it survives, the R-1 index test on
  natural benchmark text with the NLB-gated front-end inside the measured system.

### 3.2 H-GNN-{ST, KV, LF} — hybrid GNN over the kernel+world graph

The kernel + world layer form a typed relational graph (concept URNs, axiom
records, world-layer edges). A small GNN encodes query-relevant subgraphs; the
encoding is fused into the LM at one of three seams:

| Variant | Fusion seam | Continuity | Expected cost/size delta |
|---|---|---|---|
| H-GNN-ST | GNN output → trained bridge → soft tokens at the input edge | The A2/E5 adapter seam, replicated positive at one rung | +GNN weights (MBs) + adapter; prefill shortens if soft tokens replace text serialisation |
| H-GNN-KV | Graph nodes written as KV pairs into attention (KBLaM-style) | L2b kernel-addressed memory (ladder) | +KV construction cost per query; memory grows with injected node count |
| H-GNN-LF | Late fusion at logits/answer-selection | none (new) | cheapest to build, weakest hypothesised integration |

- Evidence status: unmeasured as a family; the *seam* is supported (E5 adapter
  PASS at one rung); cautioned hard by nsk1 — text-delivered grounding measured
  net-harmful and internal delivery reached only echo grade with integration
  unresolved (§0), so "the GNN delivers but the LM doesn't use it" is the named,
  measured-adjacent failure mode.
- **Falsifier, rescoped (accepting the review's correction):** "fusion ≤
  text-of-graph on tiny graphs at R-0/R-1" does NOT kill the family — text is
  often superior for tiny graphs; graph encoders may only pay off as graph size
  and reasoning depth grow. The kill is now: fusion ≤ text-of-graph at matched
  information and resource budgets ACROSS a pre-registered sweep of subgraph
  size × reasoning depth (including the D4 held-out relation compositions and
  proof depths) at R-1 — a flat or text-favouring curve over the whole sweep kills
  the family at scope; a depth-increasing fusion advantage promotes it even if
  tiny graphs favour text. Registered projection: ASM-0805.
- Controls (per the review, all pre-registered): same retrieved nodes with no
  edges; shuffled edges and relation labels; MLP/DeepSets/plain-Transformer
  encoders over the same inputs; text serialisation at equal information and
  resource budgets; held-out relation compositions and proof depths; **oracle
  subgraph vs NL-extracted subgraph** — the NL-extracted leg is NLB-gated per
  ASM-0814, the oracle leg is `oracle-diagnostic`.
- **Four-stage decomposition, separately instrumented:** retrieval → graph
  construction → graph encoding → LM use. A positive delivery probe is
  insufficient; the endpoint is causal behavioural improvement on held-out items
  (the nsk1 lesson, enforced by design).

### 3.3 H-RULE-{CD, KV, AD, ACT, HL} — rules-based inference built into the LLM: the placement analysis

The maintainer asked *where* deterministic rule-inference should live inside the
model. Five placements, analysed on the axes that matter. Two corrections from
the review are folded into the table and rulings: (a) **constrained decoding is
transport, not inference** — CD enforces an output language; the *engine* must
have already derived the valid continuation set, so H-RULE-CD is precisely
"engine-derived continuation sets delivered via masking", and without the
executor it is just a grammar; (b) **attention weights are not causal
provenance** — KV/HL provenance claims require causal ablation, intervention, or
executor traces [STIPULATED: ASM-0815; corrects technical errors #6 and #8].

| Placement | Mechanism | Inference cost | Invasiveness | Provenance | Fail-closed | Prior evidence hook |
|---|---|---|---|---|---|---|
| **H-RULE-CD** constrained-decoding head | engine derives valid continuation sets for covered spans mid-decode; masking delivers them; uncovered decode untouched | engine µs + masking, near-zero overhead | none (no weights touched) | exact (record id per constrained span; the engine's derivation IS the provenance) | yes by construction | L3c (ladder); f2b loop is the unconstrained cousin |
| **H-RULE-KV** KV-side rule memory | rule heads/records inserted as KV pairs keyed by kernel content-hash; attention reads them | KV build per query; grows with fired-rule count | low (no base-weight change) | requires causal ablation/intervention or executor traces — attention maps do NOT qualify | partial | L2b (ladder); KBLaM-family lit |
| **H-RULE-AD** rule adapters | LoRA-class adapters trained to implement rule families; swapped/composed at inference | adapter matmuls, small | medium (trained, but detachable) | none intrinsically | no — must be measured | A2/E5 trained-bridge precedent (input-side only) |
| **H-RULE-ACT** activation-level rule firing | rule conditions detected in activations; firing applies steering vectors / activation edits | probe + edit per layer, small | medium-high (runtime intervention) | weak; causal validation required | no — edits can corrupt off-target behaviour | nsk1 residual channel: delivery ECHO-grade, integration unresolved — the direct caution |
| **H-RULE-HL** dedicated hidden layer | a mid-network layer whose units are pinned to kernel concepts; rule inference as a deterministic map on that bottleneck | in the forward pass (cheap) but always-on | highest (architecture surgery, training from scratch or heavy retrofit) | naming units is NOT interpretability — bottleneck provenance must be causally validated (ablate/patch) | no — bottleneck can throttle general capability | L2a (ladder); the φ-sweep L2c is its dose-response |

Design ruling from the analysis (a prior ordering, not a verdict):

- DECISION: Phase-2 tests the placements in the order CD → KV → {AD, ACT} → HL —
  cheapest, least invasive, most provenance-preserving, most fail-closed first;
  HL is deferred until a shallower placement has shown a positive, because every
  deep-internal channel measured so far is unresolved-at-best while the
  external/decode-side seam holds the programme's only positive [STIPULATED:
  ASM-0802; the supporting facts are §0's nsk1 and f2b premises].
- **Endpoint, corrected:** cost parity with the external loop is NOT the sole
  endpoint — an internal placement can be worthwhile via accuracy, coverage, or
  latency-variance improvements even at equal cost. The family head-to-head
  (H-RULE-CD/KV vs H-VL at R-1) is decided on **Pareto frontiers over (accuracy on
  the covered slice, coverage reached, p95 latency, resource vector)**, with the
  pre-registered primary being frontier dominance, not a single-axis comparison
  [STIPULATED: ASM-0815; answers review "Compare Pareto frontiers"]. Registered
  projection: ASM-0806.

### 3.3a H-PS — NL→program synthesis (new; first-class)

The review's "promising missing design", adopted as a family rather than a
footnote because it attacks the programme's actual measured wall (the NL
boundary) directly instead of hoping rule knowledge emerges in a hidden layer
[STIPULATED: ASM-0815]:

- **Design shape:** parse natural input into a small executable DSL (the kernel's
  closed grammar, or a thin typed layer over it); execute deterministically
  (the µs engine); generate the surface answer FROM the checked result; abstain
  with calibration when parse confidence is low (selective prediction — the
  parser emits a calibrated confidence and the system's abstention policy is part
  of the measured product).
- Evidence status: cautioned — this is exactly the l3a-parse/a5-nl path, both
  measured FAIL at scope with the a1-hybrid front-end; H-PS is the *redesign* of
  that path with modern semantic-parsing/program-synthesis methods and calibrated
  abstention, which is why P3-D-PS and P3-D-NLB are both blocked by the
  P3-LR-PARSE lit-review (do not repeat the measured parser failure blindly).
- Relation to P3-D-NLB: NLB is the shared *gate instrument* (retention + S2
  fail-closed measurement per vertical); H-PS is an *architecture family* whose
  front-end, if it clears NLB, becomes the shared front-end other families use.
  They co-design; the gate stays independent of any one family's success.
- Cheapest falsifier: G2/G3 on the two existing verticals — oracle-parse ceiling
  (known: engine exact) vs synthesised-parse retention, against the pinned 0.90
  retention + S2 bars; then the D4 diagnostics with held-out compositions.

### 3.4 H-RB — retrieve-vs-bake (the store-placement fork, cross-cutting)

For any store-using family: store on disk + retrieval at inference (bytes cheap,
per-query resource cost) vs distilled/baked into weights (bytes expensive, zero
per-query retrieval). A pure size↔cost trade under KOT-SIZE/2 + KOT-COST/2,
swept, not hypothesised: each Phase-2 winner is measured at both settings and the
Pareto points reported. (The a-e2 dense-I/O membership bound — an upper bound, §0
— stays quarantined until its consumption channel is measured.)

### 3.5 The build-strategy fork: H-GU vs H-DD (compare cheaply at small scale)

**H-GU — ground-up neurosymbolic training.** Train small hosts from scratch with
the symbolic interface present from step 0. Only at rungs R-0/R-1 initially
(training compute matched to the from-scratch baseline, §2.3). Evidence status:
unmeasured; the ladder's L2c-full is its closest designed relative.

- **Scaling-direction protocol (accepting the review's correction):** one R-0
  failure does NOT imply failure at R-2 — interfaces may need capacity to become
  usable. The twin protocol runs at **≥3 widths or token budgets** and the
  pre-registered read is the DIRECTION of the interface effect across the sweep:
  monotonically-shrinking-to-zero kills; flat-negative kills; growing-with-scale
  promotes even from a negative absolute base [STIPULATED: ASM-0815].
- **Training variants in scope (the review's list, adopted):** distillation from
  symbolic proof traces; verifier-guided training (verifier in the loss/loop, not
  only retry at inference); synthetic curriculum over increasing rule depth and
  paraphrase diversity; learned routing (symbolic path activated selectively);
  conditional-compute/MoE with a symbolic expert. P3-D-GU selects and stages
  these; each is a separate arm, not a blended recipe.

**H-DD — dimension-drop of an existing model (the maintainer's strategy (b)) —
REFORMULATED.** Revision 1's formulation contained four technical errors, each
acknowledged and corrected here [STIPULATED: ASM-0816; answers review ranked
concern #4 + technical errors #3/#4/#5/#6]:

1. **Rotation invariance was overclaimed.** An arbitrary per-layer orthogonal
   rotation is NOT generally function-preserving through elementwise
   nonlinearities, normalisation, residual connections, attention-head structure,
   and tied embeddings merely because adjacent linear maps are adjusted. Only
   restricted basis changes (e.g. certain residual-stream rotations commuting
   with the chosen norm/attention structure) can be absorbed. **P3-D-DD's first
   deliverable is the derived EXACT invariance group of the chosen donor
   architecture(s)** — which transformations are absorbable, where, with proofs
   or numerical-tolerance verification per site; every "normalise" step is
   restricted to that group.
2. **SAE features do not give a removable orthogonal block.** SAE/dictionary
   features are overcomplete and non-orthogonal; matching them to kernel concepts
   does NOT yield an orthogonal coordinate block that can be dropped. The
   alignment step is reframed as identifying a **concept-associated subspace or
   parameter set** whose causal role is then tested (gate below) — with the
   method (supervised probes; SAE-derived subspaces via pinned projection) an
   experimental variable, not an assumption. The mapper caution applies to any
   mapper-mediated matching: proxy precision ~0.71 [MEASURED:
   registry/verdicts/m0a-llmproxy.json, weak proxy pending human gold].
3. **80% width ≠ 5× smaller.** Major transformer matrices scale ~quadratically
   with hidden width (a w→0.2w drop shrinks attention/MLP blocks up to ~25×),
   embeddings scale linearly, and other components differently — so "drop 80% of
   dimensions" and "5× smaller" are not the same claim. Every size claim is
   stated as an **explicit parameterisation** (which matrices shrink how, at what
   precision) AND verified as measured KOT-SIZE/2 figure-(1) bytes of the packed
   artifact — never inferred from a width fraction. Where the mechanism is better
   described as rank or parameter pruning, it is reframed and named as such. The
   maintainer's 5× target is restated as a BYTES target at matched index
   retention.
4. **Attention weights are not causal provenance** — inherited from §3.3; all
   H-DD attribution claims use ablation/patching, never attention maps.

- **P3-E-DD-0, the cheap CAUSAL GATE (new; runs before any arm experiment):**
  (1) identify the purported concept subspace/parameter set; (2) ablate or patch
  it on concept-relevant vs concept-irrelevant tasks — the effect must be
  selective; (3) test stability across layers, prompts, and donors (SmolLM2-135M
  + Pythia-160M); (4) show that **store reinjection specifically restores the
  ablated behaviour** (reinjection on NL tasks is NLB-gated per ASM-0814; the
  oracle-addressed version is an `oracle-diagnostic`); (5) only if 1–4 pass does
  structural pruning + distillation (P3-E-DD-1) run. Probe/ablation/eval
  workloads only — fits the free-compute pool [STIPULATED: ASM-0816].
- **P3-E-DD-1 (the arm experiment, updated):** arms at matched KOT-SIZE/2 bytes —
  (i) concept-aligned structural pruning + store, WITH matched recovery
  training/distillation; (ii) same, no store; (iii) random-subspace pruning of
  equal parameter count, same recovery budget (the decisive alignment control);
  (iv) **the strongest published-practice RETRAINED structured-pruning +
  knowledge-distillation baseline at equal bytes and equal recovery compute**
  (revision 1's pruning-without-recovery comparator was too weak — corrected);
  (v) donor unmodified (ceiling); each ± store. Primary endpoint: NON-INFERIORITY
  of arm (i) vs the pre-registered retention fraction of donor index — single
  one-sided CI vs the margin per §2.5(4), NOT TOST — AND superiority of (i) over
  (iii) and (iv); if (i) ≈ (iii)/(iv), alignment adds nothing over well-executed
  generic compression and H-DD's distinctive claim is dead even if compression
  succeeds generically. Dose-response swept {20, 40, 60, 80}% (the curve is the
  result; curves produced pre-W1 are DIAGNOSTIC, per §1.4).

Honest evidence status, stated plainly: still the programme's most aggressive
extrapolation (ASM-0804) — nothing measured links kernel concept vectors to any
model's internal subspaces, and measured coverage (§0) is far below "80% of a
model's dimensions correspond to encoded concepts". It stays in the portfolio
because its falsifier chain is now even cheaper (P3-E-DD-0 kills before any
pruning run) and a partial success directly serves W2.

### 3.6 Design-space summary table

| Family | Maintainer direction | Evidence status | Distinct falsifier cost |
|---|---|---|---|
| H-VL | (efficiency lineage) | supported (formal, confounded) | G1 coverage kill ~$0; R-1 test ~$0–100 |
| H-GNN-ST/KV/LF | "hybrid GNN" | seam supported; integration cautioned | ~$0–200, R-0/R-1, size×depth sweep |
| H-RULE-CD/KV/AD/ACT/HL | "rules built into the LLM + where" | cautioned (nsk1) / unmeasured | ~$0–200 for CD/KV rung |
| H-PS | (NL boundary, review-added) | cautioned (l3a-parse/a5-nl FAILs are its prior art) | G2/G3 on existing verticals, ~$0–150 |
| H-RB | (cross-cutting) | store side measured as upper bound only | rider on other experiments |
| H-GU | "train from ground up" | unmeasured | R-0 ≥3-point sweep, ~15–75 GPU-h |
| H-DD | "drop ~80% of dimensions" | unmeasured; boldest extrapolation (ASM-0804) | P3-E-DD-0 gate ~5–15 GPU-h; arms ~10–30 GPU-h |

---

## 4. The gate ladder (information-gaining gates × compute rungs)

Revision 1 organised progression by compute rung alone, which the review
correctly noted lets an architecture fail ambiguously (graph encoder? retrieval?
NL parse?). Revision 2 organises every family's progression around five
**information-gaining gates**, run cheapest-first, so a failure LOCALISES
[STIPULATED: ASM-0817]:

| Gate | Question | Input regime | Cost class | What a FAIL localises to |
|---|---|---|---|---|
| **G1 coverage-ceiling** | Can PERFECT oracle use of the store move the index by δ? (`Δ_max ≤ Σ_b w_b κ_b (1−a_b^cov)`) | paper/CPU: census + baseline accuracies | ~$0, no GPU | coverage — kill without touching the mechanism |
| **G2 oracle-interface** | With gold parses/subgraphs/record addresses, does the mechanism help at all? | ORACLE inputs; labelled `oracle-diagnostic`; NO W1 claim (ASM-0814) | cheap GPU | the mechanism itself (encoder, fusion, placement) |
| **G3 boundary-degradation** | How much of the G2 effect survives realistic NL mapping? | natural benchmark text through the NLB-gated front-end; the P3-D-ORACLE decomposition attributes the G2→G3 loss (parse vs retrieval vs execution vs generation) | cheap-moderate | the NL front-end / retrieval addressing |
| **G4 full-system-vs-frontier** | Does the whole system beat the resource-constrained frontier F(B_k)? (= a W1 attempt) | natural inputs, full framework, sealed eval | the rung's main spend | the competitive thesis at that rung |
| **G5 scaling** | Does the W1 margin hold or improve across ≥2 sizes? | as G4, two rungs | gated spend | scale-transfer |

Compute rungs remain as HOMES for the gates (they say where the compute comes
from, not what is learned):

| Rung | Params-equivalent (orientation only; the binding constraint is the budget vector B_k) | Compute home | Est. cost |
|---|---|---|---|
| **R-0** | 1–30M, TinyStories-class data | Local box + single free GPU (Modal/ARC) | ~$0 beyond free pool |
| **R-1** | 100–200M (SmolLM2-135M anchor) — the decisive cheap rung: every family's G1–G3 and first G4 | Oxford ARC / Modal academics; single-GPU jobs | ≤ ~50 GPU-h/family |
| **R-2** | 300–500M (SmolLM2-360M anchor) — G4 for R-1 survivors; the W2 sweep iff W1 passes here | ARC/Modal; AIRR Gateway if awarded | ~100–500 GPU-h total |
| **R-3** | 1–2B (SmolLM2-1.7B anchor) — G4/G5 at a size the outside world cares about; index version bump | AIRR Gateway 10k GPU-h class; TRC | gated: maintainer + secured allocation |
| **R-4** | 3–8B | second-wave grants (§6) | gated: explicit maintainer fork |

Rung/gate discipline: promotion requires the pre-registered primary of the
current gate met; a family failing the SAME gate at two consecutive rungs (or
failing G1/G2 outright, which are rung-independent) is closed at scope;
architectures may change between rungs — every change re-enters through
prereg-freeze; no silent drift. **Sequencing exemptions (per the review):**
P3-E-NLB-1 and all coverage censuses/G1 computations do NOT wait for index
calibration (P3-E-CAL) — they make no index claim and gate everything else, so
they run immediately; every G4 (W1-relevant) experiment DOES require P3-E-CAL
PASS plus the frozen KOT-FAIR/2 [STIPULATED: ASM-0817].

---

## 5. Phased, hierarchical work-breakdown (the beadable structure)

- DECISION: Phase-0 = TEN literature reviews + one direct-design task (P3-MF-0)
  are the top-level beads; each names the Phase-1 design beads it spawns on
  completion; each Phase-1 design bead spawns its Phase-2 experiment beads
  through prereg-freeze. Nothing below is created/frozen/run by this document
  [STIPULATED: ASM-0819, superseding ASM-0807].

Node types: **[LIT]** = lit-review-then-fan-out (literature-researcher agent);
**[DESIGN]** = direct design (Fable / experiment-designer); **[EXP]** =
pre-registered experiment (experiment-designer freezes → runner runs → analyst
reads out).

### Phase-0 — top-level beads (all parallel, no cross-dependencies)

Each [LIT] bead's deliverable: an epistemic-tagged report
(`reports/lit-p3-*.md`), every REVIEW-CITED reference from this document verified
at source or flagged, each prior failure judged capability-limited vs
fundamental, and the named design beads spawned with their opening questions
answered.

| Bead | Type | Priority | Scope — the specific questions it must answer | Spawns on completion |
|---|---|---|---|---|
| **P3-LR-EVAL** — evaluation + AI-index methodology | [LIT] | P0 | HELM multi-scenario/multi-metric construction; composite-index statistics (chance/ceiling normalisation, domain macro-averaging, variance/floor handling, when a scalar index is defensible at all); Open-LLM-Leaderboard-v2 design + small-model floors; contamination-detection practice + sealed-eval production (who, how, refresh cadence, LiveBench versioning discipline); proxy-rung validity (what R-0/R-1 results have/haven't predicted at 1B+); suitability + floors/ceilings of BLiMP/EWoK, CLUTRR, ProofWriter/RuleTaker, FOLIO, IFEval, MMLU-Pro, BBH/BBEH, GSM8K per rung; verify CLUTRR/LiveBench/HELM/OLLv2 citations at source | P3-D-INDEX (co-input with P3-MF-0), P3-D-SEAL, P3-D-POWER, P3-D-BASE (co) |
| **P3-LR-SYS** — lifecycle cost, systems benchmarking, storage/I-O economics | [LIT] | P0 | MLPerf inference scenarios + power methodology in operational detail (what we can implement on our hardware); latency-percentile/throughput/TTFT measurement practice; warm/cold-cache + startup accounting; hardware repeatability (run-to-run, day-to-day variance control); storage + network I/O economics; inference-volume-dependent optimal sizing (verify Sardana et al. at source); energy measurement (RAPL/NVML) pitfalls | P3-D-HW, P3-D-LIFE, P3-D-INDEX (cost-rig co-input) |
| **P3-LR-RAG** — RAG, structured retrieval, knowledge graphs, tool-using neural baselines | [LIT] | P0 | Strongest current small-model RAG/tool-use recipes (the G4 comparator to beat); structured/KG retrieval vs dense retrieval; retrieval-index size/cost accounting practice; optimised/adaptive test-time compute (verify the ICLR-2025 result at source) + learned verifiers as baseline components; what published RAG wins say about "typed store + retrieval" vs "kernel semantics" attribution | P3-D-RAGC, P3-D-FRONTIER, P3-D-GNN (co-input) |
| **P3-LR-PARSE** — semantic parsing, program synthesis, grammar induction, uncertainty + selective prediction | [LIT] | P0 | State of semantic parsing into executable forms at small model scale; NL→DSL program synthesis with execution feedback; grammar induction for closed grammars; calibrated abstention/selective prediction (risk-coverage curves, conformal methods) for parse confidence; why l3a-parse/a5-nl-CLASS failures happened in the literature and what fixed them (capability-limited vs fundamental per failure); paraphrase robustness methods | P3-D-NLB, P3-D-PS, P3-D-ORACLE (co) |
| **P3-LR-NTP** — neural theorem proving, differentiable logic, neural algorithmic reasoning, proof-trace distillation | [LIT] | P1 | What NTP/differentiable-logic/NAR methods actually beat matched neural baselines, at what scale, under what accounting; proof-trace distillation into small LMs (feeds H-GU variants); executor-in-the-loss training precedents; which of these transfer to a µs deterministic engine as the executor | P3-D-GU (co), P3-D-RULE (co), P3-D-PS (co) |
| **P3-LR-FUSE** — GNN–LLM fusion + neurosymbolic integration survey (absorbs rev-1 P3-LR-NSA + P3-LR-GNN) | [LIT] | P1 | Field map: neurosymbolic system taxonomies; what has beaten matched baselines anywhere and under what accounting; GraphToken/KBLaM/GNN-adapter lineages; graph-encoder scaling at small sizes; measured fusion-vs-text-serialisation results incl. graph-size/depth dependence (the §3.2 sweep's prior art); relational-benchmark practice | P3-D-GNN; any new H-* family found |
| **P3-LR-RULE** — rule-injection into transformers | [LIT] | P1 | Extends `reports/lit-llm-injection-priorart.md`: constrained/grammar decoding WITH executors (not just grammars); KV-memory injection; steering/activation edits; adapter-encoded procedures; bottleneck architectures; per-placement causal-provenance validation practice (what counts as evidence beyond attention maps) | P3-D-RULE |
| **P3-LR-SURG** — model compression, dimension/structured pruning, distillation + the EXACT invariances of transformer model surgery | [LIT] | P1 | Structured pruning + retrained-recovery + KD best practice (the (iv) comparator); rotation/absorb methods and their PROVEN invariance conditions per architecture component (norms, residual, heads, tied embeddings) — causal representation analysis; SAE/dictionary-feature geometry (overcompleteness, non-orthogonality) and interp-guided pruning attempts; published size-vs-capability curves 100M–2B; whether ANY prior work dropped semantically-identified parameters and backfilled from an external store (H-DD's closest prior art) | P3-D-DD |
| **P3-LR-STORE** — store authoring, maintenance, provenance + knowledge-update economics | [LIT] | P1 | Cost-per-record accounting practice for curated KBs; provenance + update/staleness economics (temporally-fresh facts, the sealed-eval store leg); human-review cost models; what KB-maintenance economics did to comparable past systems (expert systems, KGs) — capability-limited vs fundamental | P3-D-LIFE (co), P3-D-SEAL (store-leg co-input), feeds the coverage-growth feeder line |
| **P3-LR-TINY** — tiny-model training + small-scale scaling laws | [LIT] | P2 | TinyStories/BabyLM/nanoGPT-class recipes; compute-matched twin-training practice; multi-width/token-budget sweep design (the §3.5 direction protocol's prior art); what R-0-scale results have and have not predicted | P3-D-GU, P3-D-BASE (co) |
| **P3-MF-0** — measurement + fair-comparison framework draft | [DESIGN] | P0 | §2 executed as a draft: threat model, KOT-AI-INDEX/2 pins, KOT-SIZE/2 packing script + base-image freeze, KOT-COST/2 rig, KOT-LIFE/1 template, decontamination screener, sealed-eval protocol, frontier-builder spec, §2.5 analysis plan, calibration prereg | P3-D-THREAT, P3-D-INDEX (its freeze vehicle) |

### Phase-1 — design beads (each blocked by its named Phase-0 parents)

| Bead | Type | Priority | Blocked by | Deliverable | Spawns |
|---|---|---|---|---|---|
| **P3-D-THREAT** | [DESIGN] | P0 | P3-MF-0 (+P3-LR-EVAL co) | The frozen §2.0 resource/baseline threat model — enumerated gaming channels × mechanised counters × standing limitations | gates P3-D-INDEX freeze |
| **P3-D-INDEX** | [DESIGN] | P0 | P3-MF-0 + P3-LR-EVAL + P3-LR-SYS + P3-D-THREAT | Frozen KOT-FAIR/2: KOT-AI-INDEX/2 (domains, normalisation, pins) + KOT-SMOL-CONT/1 + KOT-SIZE/2 (incl. frozen base image) + KOT-COST/2 + KOT-LIFE/1 + §2.5 analysis plan + calibration prereg | P3-E-CAL |
| **P3-D-FRONTIER** | [DESIGN] | P0 | P3-LR-RAG + P3-LR-EVAL | The neural frontier-builder: per-budget baseline optimisation recipe (quantisation/pruning/distillation/retrieval/adaptive test-time compute), comparator pinning rule, F(B_k) construction protocol | feeds every G4 [EXP] |
| **P3-D-BASE** | [DESIGN] | P0 | P3-LR-EVAL + P3-LR-TINY + P3-LR-RAG | Baseline-set pins per rung + R-0 twin recipe + total-tuning-compute symmetry rules (§2.3) | feeds every [EXP] |
| **P3-D-POWER** | [DESIGN] | P0 | P3-LR-EVAL (+ coverage censuses, which run immediately) | The coverage × max-gain power analysis: G1 Δ_max computation per family × suite + the power/margin table (what κ each family needs for δ_k to be reachable) | G1 verdicts for H-VL/H-RULE/store-side H-DD; feeds P3-E-* preregs |
| **P3-D-RAGC** | [DESIGN] | P0 | P3-LR-RAG | The matched generic-RAG/tool-use control: same corpus, same retriever/index, same budgets spec + its factorial cells (§2.2(2)f) | control arm in every store-touching [EXP] |
| **P3-D-NLB** | [DESIGN] | P0 | **P3-LR-PARSE** (new blocker — do not repeat the measured parser failure blindly) | The NL front-end redesign that targets 0.90 retention + S2 fail-closed per vertical, with calibrated abstention; the gate instrument ASM-0814 points at | P3-E-NLB-1 |
| **P3-D-ORACLE** | [DESIGN] | P1 | P3-LR-PARSE | The oracle-to-NL error decomposition protocol: attributing G2→G3 loss across parse / retrieval-addressing / execution / generation, per experiment | G3 stage of every family [EXP] |
| **P3-D-HW** | [DESIGN] | P1 | P3-LR-SYS | Hardware repeatability + warm/cold-cache + startup/percentile measurement protocol (the KOT-COST/2 rig's operating manual) | gates P3-E-CAL |
| **P3-D-LIFE** | [DESIGN] | P1 | P3-LR-SYS + P3-LR-STORE | KOT-LIFE/1 amortisation model + logging hooks (tuning-compute audit trail, store-cost capture) | co-report in every G4 [EXP] |
| **P3-D-SEAL** | [DESIGN] | P1 | P3-LR-EVAL (+P3-LR-STORE co) | The independent sealed benchmark: producer (independent party / procedural generator), refresh + versioning cadence, temporally-fresh-facts store leg, consistency-gate shape | sealed leg of every G4 [EXP] |
| **P3-D-PS** | [DESIGN] | P1 | P3-LR-PARSE + P3-LR-NTP | H-PS concrete design: DSL, parser, calibrated-abstention policy, G2/G3 experiment shapes | P3-E-PS-1 |
| **P3-D-VL** | [DESIGN] | P1 | P3-D-POWER (G1 must not be dead) | H-VL productisation: loop + NL front-end integration + abstention policy + expanded G4 comparator set (§3.1) | P3-E-VL-1 |
| **P3-D-GNN** | [DESIGN] | P1 | P3-LR-FUSE + P3-LR-RAG | H-GNN designs + the size×depth sweep + six controls + four-stage instrumentation (§3.2) | P3-E-GNN-1 |
| **P3-D-RULE** | [DESIGN] | P1 | P3-LR-RULE + P3-LR-NTP | H-RULE placement designs, CD+KV first, causal-provenance instrumentation, Pareto endpoint (§3.3) | P3-E-RULE-1 |
| **P3-D-DD** | [DESIGN] | P1 | P3-LR-SURG | Invariance-group derivation per donor + P3-E-DD-0 causal gate + updated arm matrix with retrained-pruning+KD comparator + non-inferiority margins (§3.5) | P3-E-DD-0 → P3-E-DD-1 |
| **P3-D-GU** | [DESIGN] | P2 | P3-LR-TINY + P3-LR-NTP + P3-LR-FUSE | Ground-up R-0 architecture(s) + ≥3-point sweep protocol + variant staging (§3.5) | P3-E-GU-1 |

### Phase-2 — experiment beads (each: prereg-freeze → run → readout)

**Blocking rule (the measurement-first invariant):** every G4/W1-relevant [EXP]
is blocked by {P3-D-INDEX frozen, P3-D-THREAT, P3-D-BASE, P3-D-FRONTIER,
P3-D-HW, P3-D-RAGC, P3-E-CAL PASS}. **Exempt from P3-E-CAL:** P3-E-NLB-1, all
coverage censuses/G1 computations, and `oracle-diagnostic` G2 stages (they make
no index claim) — per §4's sequencing exemption. **Every natural-input
store-touching stage is blocked by P3-E-NLB-1 clearing its vertical, or runs
oracle-labelled with no W1 claim (ASM-0814).**

| Bead | Gate/Rung | Blocked by | Primary question |
|---|---|---|---|
| **P3-E-CAL** | — | P3-D-INDEX + P3-D-HW | Framework calibration on pure-neural models only (135M/360M/1.7B): ordering, variance, cost-rig repeatability; instrument gates, no architecture claim |
| **P3-E-NLB-1** | G3-instrument, R-1 verticals | P3-D-NLB | Does the redesigned front-end clear 0.90 retention + S2 fail-closed per vertical? (unblocks every natural-input store use) |
| **P3-E-PS-1** | G2→G3, R-1 | P3-D-PS (+P3-E-NLB-1 shares instrumentation) | Synthesised-parse retention vs oracle-parse ceiling + calibrated-abstention risk-coverage on the two verticals |
| **P3-E-VL-1** | G1→G4, R-1 | P3-D-VL + full G4 block (+P3-E-NLB-1 for the NL leg) | G1 Δ_max on paper first; then: does verify-retry move KOT-AI-INDEX/2 vs the frontier comparators (§3.1 set)? |
| **P3-E-GNN-1** | G2→G3, R-0/R-1 | P3-D-GNN (+G4 block for any index leg; NL-extracted-graph leg NLB-gated) | Fusion vs text-of-graph across the size×depth sweep with the six controls (ASM-0805 resolver) |
| **P3-E-RULE-1** | G2→G4, R-1 | P3-D-RULE + G4 block (NL legs NLB-gated) | CD+KV placements vs H-VL on Pareto frontiers (accuracy/coverage/latency-variance/resource) (ASM-0806 resolver) |
| **P3-E-DD-0** | causal gate, R-1 | P3-D-DD | The §3.5 five-step causal gate: selective ablation + store-reinjection restoration (oracle-addressed = oracle-diagnostic) |
| **P3-E-DD-1** | G2→G4, R-1 | P3-E-DD-0 PASS + G4 block | The updated arm matrix vs retrained pruning+KD (ASM-0804 resolver) |
| **P3-E-GU-1** | G2, R-0 | P3-D-GU + P3-D-BASE | Interface-present vs plain twins across ≥3 widths/token budgets: DIRECTION of the interface effect |
| **P3-E-SCALE-2** | G4(+G5 entry), R-2 | ≥1 Phase-2 survivor + maintainer gate + full G4 block | First W1 attempt vs F(B_2); the W2 Pareto sweep runs IFF W1 passes here (else its compression curves are DIAGNOSTIC) |

Dependency graph, flattened for the coordinator (arrows = "blocks"):

```
                         ┌─► P3-D-THREAT ─┐
P3-MF-0 ─────────────────┤                ├─► P3-D-INDEX ─► P3-E-CAL ─┐
P3-LR-EVAL ──────────────┴────────────────┘        ▲                  │
P3-LR-SYS ──► P3-D-HW ─────────────────────────────┘ (rig co-input)   │
P3-LR-SYS + P3-LR-STORE ──► P3-D-LIFE ──────────────────────────┐     │
P3-LR-EVAL (+P3-LR-STORE) ──► P3-D-SEAL ────────────────────────┤     │
P3-LR-RAG + P3-LR-EVAL ──► P3-D-FRONTIER ───────────────────────┤     │
P3-LR-EVAL + P3-LR-TINY + P3-LR-RAG ──► P3-D-BASE ──────────────┤     │
P3-LR-RAG ──► P3-D-RAGC ────────────────────────────────────────┤     │
P3-LR-EVAL ──► P3-D-POWER (G1 tables; censuses run immediately) ┤     │
        ══ the G4 BLOCK: all of the above + P3-E-CAL PASS ══════╪═════╧══
                                                                │
P3-LR-PARSE ──► P3-D-NLB ──► P3-E-NLB-1 ──► (every natural-input store leg)
P3-LR-PARSE ──► P3-D-ORACLE ──► (G3 stage of every family)
P3-LR-PARSE + P3-LR-NTP ──► P3-D-PS ──► P3-E-PS-1
P3-D-POWER ──► P3-D-VL ──► P3-E-VL-1 ──────────────┐
P3-LR-FUSE + P3-LR-RAG ──► P3-D-GNN ──► P3-E-GNN-1 ─┤
P3-LR-RULE + P3-LR-NTP ──► P3-D-RULE ─► P3-E-RULE-1 ┼─► P3-E-SCALE-2 (R-2, maintainer gate)
P3-LR-SURG ──► P3-D-DD ──► P3-E-DD-0 ──► P3-E-DD-1 ─┤
P3-LR-TINY + P3-LR-NTP + P3-LR-FUSE ─► P3-D-GU ─► P3-E-GU-1
   (G4 legs of VL/GNN/RULE/DD-1 additionally require the G4 BLOCK;
    NL legs additionally require P3-E-NLB-1; oracle legs run earlier, labelled)
```

Sizing note for the coordinator: the eleven Phase-0 beads are parallel and
independent. The coverage censuses + G1 Δ_max computations (inside P3-D-POWER)
and the P3-LR-PARSE→P3-D-NLB line are the schedule-critical paths — they can kill
or unblock the most downstream work — and neither waits for index calibration.

### What Phase-2 survivors spawn (Phase-3, named now, designed later)

R-2 promotion (P3-E-SCALE-2) → the first full W1 claim; a W1 PASS at any rung
spawns the W2 shrink programme (Pareto sweep beads per §1.4) + the G5 two-size
confirmation; R-3 requires the index-version design bead (KOT-AI-INDEX/3 scoping)
plus a secured GPU allocation (§6).

---

## 6. Compute, budget, and infrastructure (cheap-first)

- PREMISE: the free-compute pool documented for this programme spans Oxford ARC
  (free A100/H100/GH200, near-certain approval), AIRR Gateway (up to 10,000
  GPU-h), TPU Research Cloud, Modal for Academics (up to $10k serverless GPU),
  ~$1k-class inference-API credits, and an already-secured $100 Anyscale credit,
  with dollar ceilings explicitly not guarantees [LIT-BACKED:
  docs/next/free-compute-recon.md, consolidated 2026-07-10 — programme-internal
  recon, figures verified at their sources on that date].

Allocation policy by rung (all spend above the free pool is maintainer-gated):

- **Phase-0 + P3-MF-0 + P3-E-CAL:** local box (2 shared cores, `nice -n 10`,
  checkpointed — standing practice) + free API tiers. ~$0. Lit reviews are
  API/web-bound, not GPU-bound. G1 coverage computations are CPU-only.
- **R-0:** local box for symbolic side + evals; single free GPU (Modal/ARC) for
  the H-GU sweep. Inside the free pool.
- **R-1 (the decisive rung):** ARC + Modal academics; each family's falsifier is
  designed to fit ≤~50 GPU-h. The whole R-1 wave should fit inside ARC-free +
  Modal-credit capacity even if every family runs — and the G1/G2 gate structure
  means several families will be killed before spending their allocation.
- **Sealed eval:** the cheap default is a pinned procedural generator (local box);
  the independent-party variant costs coordination, not compute — P3-D-SEAL prices
  both.
- **R-2:** ARC/Modal continue; the AIRR Gateway application should be in flight
  during Phase-0 (its ~1-month award latency is the schedule-critical item, and
  applications cost nothing but form-filling).
- **R-3+:** hard-gated: requires a secured allocation (AIRR award or equivalent)
  AND a maintainer decision under K-P3v2's default (§7.1). No R-3 bead is created
  until both exist.
- **Operational discipline carried over:** Modal attached-run hygiene (explicit
  `modal app stop` after killing clients; nohup+setsid for long runs) per the
  standing programme memory; every run niced + checkpointed on the shared box.

Failure mode priced in: if no external GPU materialises, G1 (CPU-only), P3-E-DD-0
probes, and the H-VL/H-PS R-1 falsifiers remain feasible on ARC-free alone; the
programme degrades gracefully to its cheapest decisive tests rather than stalling.

---

## 7. Honest risks and kill criteria

### 7.1 Programme-level kill — K-P3v2 (quantitative, hardened)

Revision 1's kill contained a subjective escape hatch ("analysts attribute the
misses to fundamentals") and a soft default (open-ended maintainer fork). Both
are replaced [STIPULATED: ASM-0818; answers review "The programme-level kill is
too soft"].

- DECISION: **K-P3v2 (verbatim)** [STIPULATED: ASM-0818]. The competitiveness
  programme is KILLED — not forked, not re-scoped in place — if ANY of the
  following pre-registered quantitative conditions holds at its named checkpoint:
  1. **Coverage ceiling:** after the P3-D-POWER analysis (including any funded
     coverage-growth ingestion wave completed by the R-1 checkpoint), the
     perfect-oracle bound Δ_max < δ_1 for EVERY store-dependent family on the
     frozen R-1 suite — perfect use of the store cannot reach the margin, so no
     mechanism result can save it.
  2. **NL boundary:** P3-E-NLB-1 (and its redesigns) fails the 0.90 retention OR
     the S2 fail-closed safety gate on BOTH verticals after **N = 2 pre-registered
     redesign cycles** beyond the first attempt.
  3. **Frontier:** no family's G4 result exceeds the neural/RAG frontier F(B_k)
     at BOTH R-1 and R-2 (i.e. W1 fails everywhere through R-2 with the frontier
     comparators properly built).
  4. **Attribution collapse:** every measured family gain vanishes against the
     matched generic-store / generic-RAG controls (the win is retrieval + typed
     storage, available to any baseline, and is absorbed into the frontier).
  5. **Boundary non-survival:** every family's G2 (oracle-interface) gain fails
     to survive G3 (natural input) at the pre-registered retention margin, across
     the N = 2 NLB redesign cycles.
  6. **Lifecycle domination:** the KOT-LIFE/1 ledger shows S's total cost of
     ownership dominated by a frontier baseline at ALL THREE pinned amortisation
     volumes (10^3/10^6/10^9 queries) for every family that passed G4 — a
     "win" that no deployment volume can ever justify.
  **Default on kill:** the competitiveness programme TERMINATES; restarting
  requires a NEW proposal with new evidence or a new mechanism class — there is
  no open-ended maintainer fork. (The maintainer can of course overrule — but the
  DESIGN's default is termination, and an overrule is an explicit new decision on
  the record, not this document's escape hatch.) Surviving single mechanisms
  (e.g. a G2-positive fusion result) are handed back as SCOPED instruments with
  their envelopes, not as a continued competitiveness claim [STIPULATED:
  ASM-0818].

### 7.2 Named risks, each tied to current evidence

**R1 — the answer-key trap at programme scale (highest severity).** The whole
programme could "win" by encoding eval-adjacent content into stores. This is the
f2b confound (§2.2) writ large; the decontamination gate + factorial controls +
the SEALED post-freeze evaluation (§2.2a — new, because screening alone cannot
catch abstraction-level leakage or researcher adaptation) are the mitigation, and
the win-voiding rule is deliberately harsh.

**R2 — the coverage wall may bind before any architecture question does.**
Measured coverage against external benchmark material is approximately zero today
(0/1,550 define-lane census; g8 0/1,000; m0b 0.3542 on the *friendliest* corpus —
§0). Revision 2 turns this from a risk paragraph into the G1 GATE: the Δ_max
bound is computed on paper before any GPU spend, per family, and K-P3v2(1) makes
it a programme-kill condition. The coverage-growth/ingestion line
(`docs/next/coverage-growth-ingestion-plan.md`) is the feeder workstream, its
costs logged into KOT-LIFE/1. This remains the single most likely way Programme-3
dies, and it is inherited, not new.

**R3 — the NL boundary is inherited by every real-input claim.** Both measured
crossings failed, one dangerously (§0). Revision 2's answer is structural AND
dependency-encoded: the parser is inside the measured system (§1.1), P3-D-NLB is
blocked by the semantic-parsing lit-review (don't rebuild the failed parser
naively), P3-E-NLB-1 gates every natural-input store leg of every family
(ASM-0814), H-PS attacks the boundary directly with calibrated abstention, and
K-P3v2(2)/(5) kill the programme if the boundary won't yield. The a5-nl lesson
generalises: a wrong-but-confident symbolic answer with provenance attached is
WORSE than a refusal, so fail-closedness is a scored dimension of every
architecture (§3.3), not a nicety.

**R4 — integration may not follow delivery (the nsk1 lesson).** For H-GNN and
H-RULE-ACT/HL especially: nsk1 showed content can be delivered into the residual
stream at echo grade while rescuing nothing, and text delivery measured
net-harmful (§0). Mitigation: every fusion design carries a causal behavioural
endpoint on held-out items, never a delivery endpoint alone; the placement
ordering (§3.3) starts where the executor's work is delivered by construction
(engine-derived constrained decoding); the four-stage decomposition (§3.2)
localises delivery-vs-use failures.

**R5 — H-DD rests on an unmeasured correspondence AND previously on incorrect
surgery assumptions.** The §3.5 reformulation corrects the assumptions (invariance
group, SAE geometry, width-vs-bytes, provenance) and interposes the P3-E-DD-0
causal gate; nothing yet links kernel concept vectors to any model's internal
subspaces, and the target sits far beyond measured coverage. The risk is bounded
by the gate's cheapness; the distinctive claim dies cleanly if ablation is
non-selective, reinjection non-restorative, or (i) ≈ (iii)/(iv) — registered
resolution path on ASM-0804 as amended by ASM-0816.

**R6 — the index is gameable by suite choice; the frontier by comparator choice.**
Mitigations: suite + domains pinned in P3-D-INDEX before any architecture result
exists; the threat model (§2.0) enumerates the gaming channels; the
frontier-builder pins comparators at freeze; P3-E-CAL validates the instrument on
known-ordered models; the sealed suite (§2.2a) catches adaptation to the frozen
suite.

**R7 — small-scale findings may not transfer up the ladder.** R-0/R-1 kills could
discard architectures that only work at scale. Accepted deliberately as the price
of cheap-first; hedges: the H-GU ≥3-point direction protocol (a shrinking-negative
is killed, a growing-from-negative is promoted), the same-gate-two-rungs kill rule
(not one), the G5 two-size confirmation, and P3-LR-EVAL's proxy-rung-validity
question feeding margin design. Any claim about behaviour at unrun rungs is an
extrapolation and stays out of premises.

**R8 — relationship to the standing INCONCLUSIVE verdicts.** Programme-3 does not
assume either Programme-1/2 thesis true. If the correctness thesis eventually
resolves NOT-FEASIBLE (semantics unsound), Programme-3's stores degrade to "typed
records + checker" — which W1 can still legitimately win with (§0 re-aiming),
honestly labelled by the aligned-non-kernel + generic-RAG controls. If the
efficiency de-confound (knull / human f2b-transfer) resolves against kernel
content, H-VL's prior weakens sharply — and K-P3v2(4) already treats
attribution-collapse as a kill input. The verdict-moving pending items of the old
programme (knull ablation, f2b-transfer Stage-1, g2) remain independently valuable
and none is superseded by this document.

### 7.3 What this document does NOT claim (corrected)

No architecture herein is claimed likely to work; three of the seven families
start from measured cautions and two from nothing. The claims this document
actually makes are: the objective is now falsifiably operationalised at a
resource frontier (§1); the comparison has been made **auditable in several named
respects** — decontamination-screened, control-factored, threat-modelled,
sealed-eval-checked, lifecycle-priced — but it has NOT been shown capable of
being made fully fair: training-data contamination of closed baseline corpora,
lifecycle-cost incommensurability, baseline-search completeness, and residual
packaging/frontier gaming remain UNRESOLVED and are carried as standing
limitations on every W1 claim (§2.0); the design space is enumerated with
per-family cheap falsifiers (§3); and the work decomposes into a beadable
lit-review-first hierarchy (§5). Everything else is a hypothesis with a
registered tag and a priced test.

---

## Epistemic register (what this design relied on)

- **STIPULATED (revision 2, fresh block):** ASM-0810 (resource-frontier W1 +
  KOT-SIZE/2 + KOT-COST/2 + KOT-LIFE/1 + narrowed claim scope; supersedes-in-part
  ASM-0800); ASM-0811 (KOT-AI-INDEX/2 domain-structured index + continuity-index
  demotion + sealed secondary; supersedes-in-part ASM-0800(1)); ASM-0812
  (threat model, factorial controls, generic-RAG control, frontier-builder,
  tuning-compute symmetry, sealed eval; supersedes-in-part ASM-0801); ASM-0813
  (statistics: LCB>δ, FWER, hierarchical bootstrap, non-inferiority vs TOST);
  ASM-0814 (NLB-gates-all-natural-input-store-use + oracle-diagnostic labelling;
  strengthens ASM-0808(1)); ASM-0815 (H-PS family + per-family corrections:
  CD-transport, causal provenance, Pareto endpoint, GNN sweep rescope, H-GU
  direction protocol; extends ASM-0802); ASM-0816 (H-DD reformulation + P3-E-DD-0
  causal gate + retrained-pruning comparator; amends the ASM-0804 resolution
  path); ASM-0817 (G1–G5 gate ladder + Δ_max kill + W2-conditionality + CAL
  exemptions; supersedes-in-part ASM-0803); ASM-0818 (K-P3v2 quantitative kills +
  terminate default; supersedes-in-part ASM-0803's K-P3); ASM-0819 (revision-2
  WBS; supersedes ASM-0807).
- **STIPULATED (revision 1, still standing where not superseded):** ASM-0800–0803,
  ASM-0807–0808 as recorded; superseded-in-part relations are stated in the new
  entries' notes (registry is append-only).
- **EXTRAPOLATION (registered, never premises):** ASM-0804 (dimension-drop
  hypothesis, resolution path amended by ASM-0816), ASM-0805 (GNN-fusion
  advantage, resolver rescoped to the size×depth sweep), ASM-0806 (internal-rules
  savings, resolver rescoped to Pareto-frontier dominance).
- **MEASURED (restated strictly within their envelopes, §0):** the capstone
  verdicts and their constituent figures (l3a/a5, l3a-parse/a5-nl, f2b-replicate,
  g8, m0b via ASM-0001, nsk1 exploratory reads, a-e2-census upper bound,
  m0a-llmproxy precision).
- **REVIEW-CITED (design motivations pending source verification by the named
  P3-LR-* bead):** MLPerf inference + power methodology (→ P3-LR-SYS); Stanford
  HELM (→ P3-LR-EVAL); CLUTRR arXiv:1908.06177 (→ P3-LR-EVAL); LiveBench
  (→ P3-LR-EVAL); Open-LLM-Leaderboard-v2 (→ P3-LR-EVAL); Sardana et al. "Beyond
  Chinchilla-Optimal" (→ P3-LR-SYS); the ICLR-2025 adaptive test-time-compute
  result (→ P3-LR-RAG/P3-LR-EVAL). None is load-bearing for any premise here;
  each is load-bearing only for what its lit-review must verify.
- **LIT-BACKED:** the free-compute pool figures (docs/next/free-compute-recon.md,
  source-verified 2026-07-10).

This document changes no frozen object, no verdict, no audit, and no ASM outside
the fresh ASM-0810–0819 block.
