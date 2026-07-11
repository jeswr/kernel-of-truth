# P3-D-FRONTIER — FRONT/1: the neural frontier-builder (Phase-1 design, revision 2)

> **Status: Phase-1 [DESIGN] deliverable of Programme-3 (bead kernel-of-truth-s55r.16,
> P3-D-FRONTIER), REVISION 2 (2026-07-11): revised against the independent GPT-5.6
> external review `poc/gpt56-review/rev-dFRONT-20260711/last-message.json`, whose
> three ranked corrections (matched-RAG contract, resource closure, F-CAL
> decisiveness + G4 wiring) and eight further technical findings are each applied
> below (change-map in §12). Nothing here is frozen, pre-registered, scheduled, or
> run; no verdict, audit, or frozen object is touched. The design's assumption
> entries are now REGISTERED: revision 1's provisional ids P3F-A1…P3F-A5 are
> retired and replaced by registry entries **ASM-0850…ASM-0854** (fresh block
> ASM-0850–0879, claimed after the concurrent rev-dMF0 / KOT-DECOMP revision waves
> consumed 0820–0849; append-only, no collision).** Author: Fable, chief-architect
> role (`kern/fable-designer`), 2026-07-11.
>
> **Blocked-by inputs, read in full at source:**
> `docs/next/programme-3-neurosymbolic-architecture.md` (revision 2) — §1.4 W1/W2,
> §2.3 the frontier-builder clause (ASM-0812), §2.0 threat model, §2.5 statistics,
> §4 gate ladder, §5 the P3-D-FRONTIER row ("per-budget baseline optimisation
> recipe, comparator pinning rule, F(B_k) construction protocol; feeds every G4
> [EXP]"); `docs/next/lit/RAG.md` (P3-LR-RAG) — §1 recipes, §3 accounting, §4–§5
> test-time-compute + verifier envelopes, §6 attribution rules 1–5, §7–§8 the OPEN
> items flagged for this bead; `docs/next/lit/EVAL.md` (P3-LR-EVAL) — §2/§5
> normalisation + proxy-rung corrections, §7 the tempered clause-(iv) reading,
> §9 P3-D-BASE hand-off; `docs/next/feasibility-synthesis.md` — the binding
> measured walls (§0–§2). **Revision 2 additionally consumes:** `docs/next/lit/
> SURG.md` (P3-LR-SURG, now landed — the review's finding that it was wrongly
> described as in-flight is corrected, §2.2) and `docs/next/lit/SYS.md` §2–§3 +
> `docs/next/design/MF0.md` §8.1 (the energy measurability rule, §1.1).
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = a programme registry
> verdict/assessment restated strictly inside its envelope; `[LIT-BACKED: lit-review
> §]` = an external fact verified at primary source by a completed Phase-0 lit
> review, cited through that review; `[STIPULATED: id]` = a design choice made here
> (every design CHOICE is STIPULATED — nothing below smuggles an extrapolation as a
> premise); `[EXTRAPOLATION: id]` = a registered forward projection, never a
> premise.

---

## 0. Contract: what the frontier-builder is, and is not

The frontier-builder is the **standing instrument that constructs F(B_k)** — the
pre-registered, reproducible comparator set, and the measured **staircase/Pareto
envelope**, that any Programme-3 candidate system S must beat under W1 at budget
vector B_k [STIPULATED: ASM-0850, operationalising ASM-0812 clause "the comparator
set F(B_k) is built by a standing neural frontier-builder"]. It is one of the
frozen artifacts of KOT-FAIR/2 (programme §2.4 "the frontier-builder spec +
comparator pinning rule") and it **feeds every G4 [EXP]** (programme §5 Phase-2
blocking rule; the dependency enforcement this revision adds is §8).

What it is NOT, with the owning bead named:

| Not this | Owner |
|---|---|
| The index (suite, normalisation, analysis plan) | P3-D-INDEX |
| The measurement rig (hardware repeatability, warm/cold, energy counters) | P3-D-HW |
| The per-rung donor/twin **pins** (named model+revision list, twin recipe) | P3-D-BASE — FRONT defines the enumeration RULE (§2.1); BASE pins the roster |
| The factorial attribution control cells (derangement, label-permutation, …) | P3-D-RAGC — FRONT resolves the five shared matched-retrieval rules (§5) as binding defaults RAGC inherits |
| The candidate system S or any architecture family | P3-D-VL/GNN/RULE/PS/DD/GU |

Relation to the measured walls, stated up front:

- PREMISE: the programme has ZERO audited end-task wins over the kernel-as-text
  null attributable to kernel content; both value theses stand INCONCLUSIVE-PENDING
  [MEASURED: docs/next/feasibility-synthesis.md §0]. The frontier-builder exists to
  make any FUTURE win claim survivable: W1 is only as strong as the frontier it
  beats.
- PREMISE: both measured NL crossings of the kernel front-end FAILED (l3a-parse
  47.6% retention; a5-nl 41.6% + S2 dangerous-wrong fired) [MEASURED:
  registry/verdicts/l3a-parse.json + a5-nl.json]. Consequence for THIS design: the
  frontier's comparators consume natural benchmark text natively and are NEVER
  gated by NLB — the NL wall is the KERNEL side's cost, and the frontier must not
  be weakened to share it (§6).
- PREMISE: this 28-source sweep found no published 100M–2B retrieval/tool-use win
  that survives a deployment-bytes-inclusive, matched-total-resource ledger
  ("none found here", not "none exists") [LIT-BACKED: RAG.md §1 synthesis,
  28 sources fetched at primary venue 2026-07-11]. The frontier we must build is
  therefore genuinely NOVEL accounting: it is constructed, not cited
  [STIPULATED: ASM-0812, executed here; ASM-0850].

---

## 1. Objects: budget vectors, F(B_k), and the envelope

### 1.1 The budget-vector grammar

Per W1 (programme §1.4), a budget vector is
`B_k = (bytes_max, p95_latency_max, energy_per_query_max, mem_max)` where:

- `bytes_max` = KOT-SIZE/2 figure-(1) canonically-packed minimal artifact bytes
  (model + tokenizer + any store/index/verifier/selector/retriever weights + engine
  + anything beyond the frozen base image; remote dependencies count or the claim
  is void, per ASM-0810);
- `p95_latency_max` = end-to-end p95 per query under the pinned P3-D-HW
  concurrency distribution, warm AND cold both admissible-checked;
- `energy_per_query_max` = whole-run integrated energy / queries (NVML/RAPL
  counters per KOT-COST/2(d)) — a **conditional component under ONE fail-closed
  rule** [STIPULATED: ASM-0850, adopting MF0 §8.1's measurable-else-MISSING clause
  and SYS.md §2's admissibility rule as a single binding rule; answers the
  review's energy contradiction]: energy is always REPORTED per arm with its
  declared measurement boundary, or MISSING where no counter exists (never
  modeled from TDP or utilisation); it is a BINDING admissibility component of
  B_k only where every compared arm carries a measurement at the SAME declared
  boundary, same instrument class, same rig; a MISSING or boundary-mismatched
  cell excludes the energy dimension from that comparison (disclosed in the
  consuming prereg and verdict) and B_k binds on the remaining components. On the
  pool as currently surveyed, CPU-side RAPL is absent on the local box and energy
  cells are GPU-NVML-boundary at best [LIT-BACKED: SYS.md §2–§3, measured-locally
  section, 2026-07-10];
- `mem_max` = (peak accelerator memory, host RSS) pair.

All four components are measured by the P3-D-HW rig; the builder consumes that rig,
it does not define it [STIPULATED: ASM-0850].

### 1.2 The budget derivation rule (the anti-budget-shopping counter)

- DECISION: **one primary budget vector per rung**, derived mechanically from the
  rung's named anchor model and pinned at RUNG ENTRY, before any candidate system
  S is measured at that rung: `B_k := the anchor's own measured resource vector`
  — bytes = the anchor's canonically-packed bf16 bytes; latency/energy/memory =
  the anchor's measured figures on the pinned rig under the pinned index-suite
  workload, at multiplier ×1.0 on every component [STIPULATED: ASM-0810
  operationalised; ASM-0850]. Rung
  anchors are the programme's existing orientation anchors (R-1 = SmolLM2-135M,
  R-2 = SmolLM2-360M, R-3 = SmolLM2-1.7B; programme §4), pinned as name+revision
  by P3-D-BASE.
- DECISION: additional budget vectors at a rung (e.g. a tighter-bytes point for
  W2 shrink work) may be registered ONLY before any S candidate is measured at
  that rung; after first S measurement, the budget set at that rung is immutable
  for that index version. If S does not fit B_k, S fails ADMISSIBILITY — there is
  no post-hoc budget inflation, and no "S defines its own budget" path
  [STIPULATED: ASM-0810/ASM-0812 operationalised; ASM-0850; counters the
  threat-model "budget shopping" channel, programme §2.0].
- Rationale (why anchor-derived, not S-derived): deriving B_k from S's measured
  resources would let S's packaging choices move the goalposts — the review's
  band-gaming concern in new clothes. Anchor-derived budgets are computable before
  any architecture exists and are exactly what "comparably-resourced" means to an
  outside reader [STIPULATED: ASM-0850].

### 1.3 F(B_k) and the envelope — formal semantics

- **F(B_k)** = the set of comparator systems C such that (i) C is built by this
  builder from the pinned search space (§2–§4) or nominated per §7.2, (ii) C is
  ADMISSIBLE (fits every component of B_k, warm and cold, measured under
  KOT-SIZE/2 + KOT-COST/2, energy per the §1.1 boundary rule), and (iii) C is
  pinned (config hash, weights hash, seeds, decoding params, index hash, verifier
  hash) at frontier freeze [STIPULATED: ASM-0851].
- **The envelope** = the full **resource-VECTOR** frontier, never a scalarised
  "cost" axis [STIPULATED: ASM-0851; corrects the review's "index vs cost"
  scalarisation defect]: published as (a) the **non-dominated set computed in the
  full KOT-COST/2 resource space** and (b) explicitly **named 2-D projections** —
  (index × bytes), (index × p95 latency), (index × peak accelerator memory), and
  (index × energy) only where the §1.1 energy rule makes that dimension binding —
  over ALL measured points, admissible and not, dominated and not, with the
  Pareto subset and B_k marked on each projection. W1 = S significantly above the
  envelope at its budget (programme §1.4 reporting rule). Dominated and
  inadmissible points are REPORTED, never silently dropped (no-silent-caps rule).
- **Statistics interface** (consumes P3-D-INDEX's §2.5 analysis plan, does not
  define it): W1's test is simultaneous `LCB95(INDEX(S) − INDEX(C)) > δ_k` over
  every C ∈ F(B_k), FWER-controlled (programme §2.5(2)). Since the index is
  scalar, S must in particular beat the arg-max comparator; a max-t-type
  simultaneous procedure can exploit the positive dependence induced by the
  paired design (same items, paired predictions) — but **no claim is made here
  that the power loss from a large F is negligible**: that would require a
  covariance argument this design does not own [STIPULATED: ASM-0851; retracts
  revision 1's unsupported "loses little power however large F is" claim, per the
  review]. Instead: the analysis plan estimates the joint covariance across
  comparators via the hierarchical bootstrap (programme §2.5(3)), and P3-D-POWER
  sizes each experiment under the realised |F(B_k)| multiplicity. A rich frontier
  raises the bar for S — conservative against false wins; its power price is
  measured at design time, not assumed away.
- **Version discipline:** F(B_k) is content-hashed at freeze. Any change —
  adding a comparator, re-tuning one, a new external model release — is a frontier
  VERSION bump that re-baselines W1 at that rung; nothing folds in silently
  (mirrors the encoder ALGORITHM_VERSION discipline and LiveBench release
  discipline) [STIPULATED: ASM-0851].

---

## 2. The comparator search space (ASM-0812's five clauses made concrete)

The search space is a **pinned grid**, not an open-ended search — completeness is
bounded and DISCLOSED (§7.3), never claimed.

### 2.1 C1 — pure-neural donors (enumeration rule; P3-D-BASE pins names)

- DECISION: eligibility rule — open weights, redistributable licence sufficient
  for evaluation, pinned name + revision (HF commit hash), tokenizer + any chat
  template included in bytes, base AND instruct variants where both exist.
  Eligibility is decided by **measured packed bytes under the transform grid**,
  never by parameter count (a 2.6B model whose Q3 quantisation fits bytes_max is
  eligible; a 1B model that doesn't fit isn't) [STIPULATED: ASM-0812(i)
  operationalised; ASM-0851]. The S0 analytic screen never substitutes for
  packing near the budget line (§3, S0 rule).
- Candidate roster to hand P3-D-BASE (candidates, not pins): SmolLM2-135M/360M/
  1.7B (±instruct), Qwen2.5-0.5B/1.5B (±instruct), Llama-3.2-1B (±instruct),
  Pythia-160M/410M/1B/1.4B, OLMo-2-1B-class, plus any stronger open release that
  appears before freeze via the nomination window (§7.2). Anchor caveats carried
  from P3-LR-TINY: released anchors are heavily overtrained (SmolLM2-1.7B ~6,470
  tok/param) and are PINS, never twins [LIT-BACKED: TINY.md §2/§9].

### 2.2 C2 — budget-optimising transforms

- **Quantisation ladder (cheap, CPU/1-GPU):** pinned method×level grid —
  llama.cpp k-quants {Q8_0, Q5_K_M, Q4_K_M, Q3_K_M} and one calibration-based
  int4 (GPTQ or AWQ, one pinned tool+version) — applied to every C1 donor whose
  quantised bytes fit bytes_max. Tool versions and conversion scripts pinned;
  quantisation is symmetric across arms per §1.2's standing rule (programme §1.2:
  "if the neurosymbolic arm quantises, every comparator gets the same best-effort
  quantisation") [STIPULATED: ASM-0851].
- **Structured pruning + recovery (P3-LR-SURG is LANDED and incorporated —
  revision 1 wrongly described it as in-flight; corrected per the review):**
  depth/width structured pruning at pinned fractions {12.5%, 25%, 50%} WITH
  retrained recovery inside the tuning budget T_k (§3.3). The candidate recipe is
  SURG's practice frontier: **Minitron-class joint width (± depth) pruning with
  KD retraining and teacher correction, recovery data re-mixed
  Sheared-LLaMA-style** [LIT-BACKED: SURG.md §1 (arXiv:2407.14679 + 2408.11796 +
  2310.06694, 2024)]. Two SURG warnings are BINDING here: (a) **small donors have
  less prunable slack** — SliceGPT retains ~99% zero-shot at 25% slicing on
  66–70B donors but only ~90% on Phi-2 (2.7B); published big-model retention
  figures are never extrapolated down to our 135M–1.7B donors [LIT-BACKED:
  SURG.md §1 (arXiv:2401.15024, ICLR 2024)]; (b) whether R-1-scale recovery
  budgets fall inside KD's winning regime is an UNRESOLVED calculation — the
  distillation-scaling-law computation at actual donor scale (and/or a
  KD-vs-continued-pretraining recovery pilot) is required before the recovery
  mode is pinned [LIT-BACKED: SURG.md §1 (arXiv:2502.08606, 2025)]. Consequence:
  pruned entries remain **OPTIONAL grid members, never load-bearing for a
  frontier freeze**, until an R-1 pilot benchmark of the candidate recipe on the
  actual 135M/160M-class donors passes and the scaling-law calculation is done
  (the same pilot P3-D-DD needs; co-scheduled) [STIPULATED: ASM-0851].
- **Distillation:** teacher→student KD from an in-roster larger donor into a
  budget-fitting student, capped by T_k. Expensive; eligible at R-2+ only unless
  free-pool compute allows at R-1 [STIPULATED: ASM-0851].

### 2.3 C3 — neural + retrieval (RAG / tool-use)

Three distinct arm types, all built on a **pinned standard harness** (FlashRAG-class;
release pinned at freeze — the v1/v2 count discrepancy lesson) [LIT-BACKED:
RAG.md §3]:

- **(a) The matched-corpus, matched-retriever RAG arm — the §2.3(iii) CONTRACT
  cell (mandatory whenever S uses a store):** same pinned source snapshot as S's
  store, **same pinned retriever+index** (the §5 Rule-2 SHARED/MATCHED cell:
  BM25 + one pinned small dense embedder; embedder weights + index bytes charged
  to bytes_max), same byte budgets, built under the five matched-retrieval rules
  of §5. This arm is simultaneously a **REQUIRED member of F(B_k)** and the
  strongest attribution control — KOT-FAIR/2 verbatim: "SAME corpus, SAME
  retriever/index, SAME budgets as the kernel arm" (programme §2.3(iii), MF0
  §8.2(iii)); it is never replaced by the native cell [STIPULATED: ASM-0853;
  corrects revision 1, which wrongly excluded the shared cell from the frontier —
  the review's ranked concern 1].
- **(b) The native-retrieval arm (additional strongest-system frontier point):**
  each architecture retrieves the way it natively does at the same budgets — the
  §5 Rule-2 NATIVE cell. For the RAG comparator this means the builder's best
  in-budget retriever choice [STIPULATED: ASM-0853].
- **(c) The free-corpus RAG arm (pure frontier point):** the builder may choose
  ANY corpus/datastore for the baseline, scaled to fill the remaining byte budget
  (the datastore-scaling lever: datastore size improves performance monotonically
  [LIT-BACKED: RAG.md §1, MassiveDS]) — because W1's frontier is "the best
  baseline that fits the budget", not "the baseline that mirrors S". Index bytes,
  build compute, and embedder bytes all charged [STIPULATED: ASM-0851].
- **Adaptive retrieval** (retrieve-only-when-needed, popularity/confidence-
  thresholded) is in the grid — it improved accuracy while CUTTING cost in the
  one directly-relevant published result [LIT-BACKED: RAG.md §1, Mallen].
- **Tool-use cells:** a function-calling fine-tune (APIGen-style verified
  synthetic data direction) enters only where the index suite has tool-relevant
  components; any separately trained selector (the TinyAgent DeBERTa lesson) is
  charged bytes + build compute [LIT-BACKED: RAG.md §1; STIPULATED: ASM-0851].

### 2.4 C4 — adaptive test-time compute (the executable recipe: §4)

### 2.5 C5 — from-scratch twins

Required only where S itself trains from scratch (H-GU); recipe and pins are
P3-D-BASE/P3-LR-TINY property (isoFLOP placement, same-data-same-order, ≥3 paired
seeds); the builder only ADMITS the twin into F(B_k) and measures it under the
common ledger [STIPULATED: ASM-0851].

### 2.6 Composition rule (counted, not guessed)

Transforms compose along a pinned lattice: {C1 donor} × {quant level} × {± C3
retrieval} × {± C4 TTC policy}; pruning/distillation entries compose with quant
only. The R-1 arithmetic the review asked for [STIPULATED: ASM-0851]:
~14 roster donors × 5 quantisation levels (incl. none) = ~70 static bases;
byte-filtering at the R-1 anchor budget leaves ~20–30; × retrieval cells
{none, matched-shared, free-corpus} (≤3) × TTC {off, ladder} (2) ⇒ **≤ ~180
composed candidates** entering S1, plus ≤ ~12 optional pruned/distilled entries.
"Low hundreds" is this product, and §3's staged screen plus §10's worked
GPU-hour arithmetic keep measurement inside the free-compute pool.

---

## 3. The builder procedure (seven stages S0–S6, executable)

The pipeline below is the buildable artifact this bead specifies; P3-T-FRONT-IMPL
(§13) implements it. (Revision 1 miscounted "six stages" for S0–S6; corrected.)

```
S0 ENUMERATE   roster × transform lattice → static candidate list; compute packed
               bytes ANALYTICALLY as an estimate only. DROP on the estimate ONLY
               when estimate > bytes_max × κ_pack (pre-registered safety factor,
               proposed κ_pack = 1.25); every candidate within the factor is
               CANONICALLY PACKED (the one KOT-SIZE/2 script) and excluded only
               on measured bytes. All drops LOGGED with their basis.
S1 SCREEN      dev mini-suite (pinned ~10% stratified subset of the dev split)
               → cheap dev-index proxy per candidate; successive halving keeps
               top half per family, ≥2 rounds. Screen noise is bounded by the
               F-CAL A4 challenger gate (§8): a true-best discarded here can
               resurface as a challenger.
S2 OPTIMISE    survivors get metered tuning inside T_k (§3.3): decoding params,
               retrieval k / thresholds, TTC policy params, recovery training
               for pruned entries — FIXED selection rule (§3.2) under ESTIMATED
               admissibility (bytes measured by packing; latency/energy/memory
               via a pinned cheap estimator — S3's rig figures do not exist yet),
               all spend logged.
S3 MEASURE     full dev-split run under KOT-SIZE/2 + KOT-COST/2 on the P3-D-HW
               rig, warm + cold, pinned concurrency + output-length discipline.
S4 ADMIT       filter against every component of B_k on MEASURED figures (energy
               per the §1.1 boundary rule) → F(B_k) candidate set. If a family's
               S2-selected config FAILS measured admissibility, selection FALLS
               BACK to that family's best admissible config from the S2 ledger
               (re-measured at S3 discipline) — never re-opened search.
S5 ENVELOPE    full-vector non-dominated set + the §1.3 named 2-D projections
               over ALL measured points; dominated + inadmissible points
               reported; B_k marked.
S6 PIN         freeze F(B_k): config/weights/index/verifier hashes, seeds,
               decoding params, the full builder log → content hash → the
               frontier version for that rung.
```

### 3.1 Dev split (leakage discipline)

- DECISION: all builder selection runs on a **dev split disjoint from the frozen
  index suite AND from every sealed release by construction** (sealed items are
  produced post-freeze and never touch the builder; ASM-0812). The dev split is
  pinned by P3-D-INDEX alongside the suite; the builder never sees a frozen-suite
  or sealed item [STIPULATED: ASM-0812 executed; ASM-0851].

### 3.2 The fixed selection rule

- DECISION: per candidate family, select the config maximising the **dev-split
  estimate of KOT-AI-INDEX/2 restricted to that rung's above-floor components**
  (the floor/exclusion criterion registered from P3-E-CAL calibration data, per
  EVAL's correction — components may not be dropped post hoc), subject to
  ESTIMATED admissibility at S2 and MEASURED admissibility at S4 (the two-step
  ordering is deliberate — the review's ordering defect: S2 cannot consult
  measurements S3 has not yet produced, so S2 screens on the pinned estimator
  and S4 owns the measured filter with the fall-back selection rule of §3's S4
  line); ties broken by lower measured cost vector (lexicographic: energy where
  the §1.1 rule makes it comparable, then p95). Near-floor MC components are
  excluded from the SELECTION metric because their signal is noise near chance
  [LIT-BACKED: EVAL.md §5 (Schaeffer arXiv:2304.15004, 2023)] — they remain in
  the frozen-suite MEASUREMENT of the final comparators [STIPULATED: ASM-0812
  fixed-selection-rule clause executed; ASM-0851].

### 3.3 Total-tuning-compute symmetry (the T_k meter, dimensionally closed)

- DECISION: tuning symmetry binds on **total tuning compute actually spent**,
  metered as a **RESOURCE VECTOR with separately capped components** — `T_k =
  (accelerator-hours, CPU-core-hours)`, each logged per arm into KOT-LIFE/1 —
  NOT config counts (ASM-0812; data-matched ≠ compute-matched [LIT-BACKED:
  EVAL.md §7 (BabyLM-2 findings arXiv:2412.05149, 2024)]), and NOT a GPU-hour
  scalar (revision 1 capped GPU-hours only, leaving CPU-heavy indexing/search
  logged but uncapped — the review's dimensional-closure defect, corrected)
  [STIPULATED: ASM-0812 tuning-symmetry operationalised; ASM-0852].
- DECISION: the unit of "an arm" is **mechanical, not judgemental** [STIPULATED:
  ASM-0852; answers the review's family-multiplication defect]: an arm is one row
  of the **arm table** — a closed, enumerated list of ledger keys registered at
  rung entry alongside B_k. R-1 comparator keys: {C1-quant, C2-prune, C2-distil,
  C3-RAG-matched, C3-RAG-free, C4-TTC} (six; no C5 key at R-1 — H-GU is an R-0
  family; a C5-twin key exists only at rungs where a from-scratch S is live),
  plus one key for S. Every tuning/search/recovery/verifier-training job carries
  exactly one key before launch; a job not attributable to a key is billed to
  the largest-spend arm (fail-closed); **adding a row to the arm table after rung
  entry is a frontier VERSION bump** — family boundaries cannot silently multiply
  allowance. Each arm (and S) spends ≤ T_k per component; total comparator tuning
  is bounded by |arm table| × T_k by construction; the meter is the builder's own
  job-level accounting, audit-trailed. Proposed values, maintainer-adjustable at
  KOT-FAIR/2 freeze and reconciled against §10's rung totals: **T_1 = (4 GPU-h,
  40 CPU-core-h)/arm; T_2 = (20 GPU-h, 200 CPU-core-h)/arm; T_3 = (80 GPU-h,
  600 CPU-core-h)/arm**; R-0 arms run inside the free pool with the same logging
  [STIPULATED: ASM-0852]. An S that spends more than T_k has not won (ASM-0812
  verbatim); a comparator arm that exhausts T_k freezes at its best logged config.
- Donor pretraining compute is INHERITED and declared on the lifecycle ledger
  (KOT-LIFE/1), never netted out and never counted against T_k — symmetric, since
  S's families also start from donors [STIPULATED: ASM-0852].

---

## 4. The adaptive test-time-compute recipe (resolving RAG.md's five OPEN items)

The lit-review verdict this section answers: "'implement Snell-style' is not yet
an executable baseline recipe" [LIT-BACKED: RAG.md §4/§7.6/§8]. The verified
envelope it must respect: the >4× and 14× findings are separate, conditional,
PaLM-2/MATH-scale results with the verifier's training compute off their ledger;
nothing is measured in our band or off math [LIT-BACKED: RAG.md §4 + EVAL.md §7].
Clause (iv) accordingly reads "mandatory to CONSIDER, include where
task-appropriate and budget-feasible" [LIT-BACKED: EVAL.md §9].

1. **Budgeted difficulty estimator [STIPULATED: ASM-0852].** Default estimator:
   **self-charging agreement escalation** — draw n₀ = 4 samples; if the majority
   answer's agreement ≥ a pinned threshold τ, stop and emit it; else escalate to
   the next stage of the policy ladder. "Agreement" is defined per component
   class (item 2) — it exists only where canonicalisation exists. The estimator
   IS the first stage of the policy, so its compute is charged to the arm's
   per-query cost by construction — there is no free oracle difficulty label. A
   trained router (small logistic head on sample-agreement + logprob features)
   is an OPTIONAL grid member, its training charged to T_k and its weights to
   bytes_max.
2. **Aggregation semantics per component class [STIPULATED: ASM-0852; answers
   the review's undefined-semantics finding].** Every index component is pinned
   to one class by P3-D-INDEX at freeze; the ladder is executable only through
   this map — "per-domain calibration" alone is not aggregation semantics:

   | Class | Components | Agreement / aggregation | Eligible policies |
   |---|---|---|---|
   | **SA** (short-answer / MC / extractive) | canonicalisable answers | canonicalise via the suite's own pinned normaliser; agreement = modal share of canonicalised answers; majority vote well-defined | full ladder P0–P3 |
   | **OG** (open generation / instruction following) | no canonical answer equivalence | majority vote UNDEFINED — never used; the estimator's agreement stage is replaced by a pinned mean-logprob confidence proxy; selection among samples ONLY by verifier/PRM score (the verifier IS the aggregation) | P0, P2, P3 (P1 self-consistency ineligible) |
   | **LL** (LM-loss / perplexity) | deterministic single computation | TTC does not apply | P0 always |
   | Abstention (any class) | — | the benchmark's abstention token is emitted only where the index scores an abstention channel (per P3-D-INDEX); otherwise the P0 answer is emitted | — |

3. **Eligible policy ladder per budget rung [STIPULATED: ASM-0852].**

   | Stage | Policy | Enters the grid iff |
   |---|---|---|
   | P0 | greedy / single sample | always |
   | P1 | self-consistency@N, N ∈ {4, 16, 64} adaptive | SA components only; per-query cost fits B_k latency/energy |
   | P2 | best-of-N + OUTCOME verifier (Cobbe-style) | verifier trains within T_k AND verifier bytes fit bytes_max |
   | P3 | PRM-weighted BoN / beam (Math-Shepherd-style auto-labels, no human-label budget) | as P2; PRM auto-labelling compute also inside T_k |

   Off-the-shelf open PRMs (e.g. the Skywork-PRM-1.5B class f2b already ran
   [MEASURED: registry/verdicts/f2b-replicate.json comparator]) are eligible
   ONLY where their bytes fit bytes_max — at the R-1 anchor budget
   (135M-class bytes) a 1.5B PRM is inadmissible by arithmetic; the R-1 P2/P3
   verifier is necessarily small and trained within T_k [STIPULATED: ASM-0852].
4. **Verifier build costs on the ledger [STIPULATED: ASM-0852].** Verifier/PRM
   training + auto-labelling compute → KOT-LIFE/1 (the ledger's cautionary-tale
   clause [LIT-BACKED: EVAL.md §7]); verifier weights → KOT-SIZE/2 figure (1);
   verifier inference → KOT-COST/2 per query. No component is free.
5. **Base-success ≈ 0 fallback [STIPULATED: ASM-0852].** If stage-1 confidence is
   below a pinned floor τ₀ (SA: no two samples agree at n₀ AND max logprob below
   a pinned percentile; OG: the logprob proxy below its pinned percentile), the
   policy falls back to P0 (emit best single sample, or the abstention token per
   item 2's abstention rule) and spends nothing further — encoding the measured
   edge that test-time compute does not rescue items the base model cannot touch
   [LIT-BACKED: RAG.md §4, Snell envelope].
6. **Non-math calibration gate [STIPULATED: ASM-0852].** Before any TTC arm
   enters a frozen F(B_k): a calibration measurement (co-scheduled with
   P3-E-CAL, same pinned harness) runs the policy ladder vs P0 on the DEV split
   per index DOMAIN × component CLASS. A TTC policy enters the frontier only in
   domain×class cells where its dev-split gain over P0 has LCB95 > 0 at that
   rung; elsewhere the arm freezes as P0. The Snell >4×/14× figures are never
   assumed to transfer — transfer to our band and suite is measured or the arm
   stays out [EXTRAPOLATION-barrier made explicit; LIT-BACKED: RAG.md §7.6].
7. **Large-budget decay reporting [STIPULATED: ASM-0852].** For every P2/P3 arm
   the builder publishes the full N-sweep curve (N ∈ {1, 4, 16, 64} within
   budget). If verifier-guided performance declines at high N (the scaling-flaws
   shape — shown for the tested verifiers, not universal [LIT-BACKED: RAG.md
   §4]), the frozen config takes the arg-max N (the selection rule already does
   this) and the decay curve is published beside the frontier. Symmetric honesty
   clause: the symbolic verifier's claimed immunity to this decay on its covered
   slice is a claim P3-E-VL-1 must measure, never a premise here [LIT-BACKED:
   RAG.md §5].

---

## 5. The matched-retrieval rules (resolving RAG.md §6's five OPEN rules)

These five rules had "no published precedent" and were left open by the lit
review [LIT-BACKED: RAG.md §7.1]. They are resolved here as **binding defaults**
because the frontier's own matched-corpus arm (§2.3a) cannot be built without
them; **P3-D-RAGC inherits them verbatim and instantiates the factorial cells on
top; it may refine a rule only by registered amendment, never silently**
[STIPULATED: ASM-0853].

**Rule 1 — source-content derivation + information-parity criterion.** One pinned
source snapshot (content hash) per vertical/corpus. Each arm's indexed objects are
derived by a **pinned, automated, seed-pinned derivation script** (kernel records
via the standing mint pipeline version; passages via a pinned chunker
(size/overlap pinned); triples via a pinned extractor; tool schemas via a pinned
generator) — human curation inside a derivation is permitted only if its hours are
logged to KOT-LIFE/1 and disclosed. Parity is enforced as four MEASURED checks,
and no further: (a) **source parity** — every arm's derivation consumes the
identical snapshot, no arm-specific extra sources; (b) **byte cap parity** — every
arm's packed indexed-object bytes ≤ the same store-byte allocation within B_k
(equal cap, not forced-equal usage); (c) **screen parity** — the §2.2
decontamination screen applies to every arm's derived objects identically;
(d) **effort disclosure** — authoring/curation/build compute per arm co-reported
(no fudged exchange rate, consistent with KOT-LIFE/1's no-common-unit rule).
Residual honesty line, carried verbatim on every consuming claim: *information
parity beyond these four checks cannot be certified — converting one snapshot
into different object types changes the retrieval problem itself; this is a
standing limitation, not a solved problem* [STIPULATED: ASM-0853; the RAG.md §6.1
scope finding adopted].

**Rule 2 — the shared/matched cell vs the native cell (CORRECTED per the
2026-07-11 external review, ranked concern 1).** Two mandatory cells, **BOTH
members of F(B_k) whenever S uses a store**, each with a distinct claim licence
[STIPULATED: ASM-0853; ASM-0812(iii) executed verbatim]:

- the **SHARED/MATCHED cell** — one pinned retriever+index (the §2.3a cells:
  BM25 + one pinned small dense embedder) over the SAME pinned corpus snapshot
  at the SAME budgets, run over a common text serialisation of every arm's
  objects — **is the programme's stipulated §2.3(iii) control** ("SAME corpus,
  SAME retriever/index, SAME budgets as the kernel arm") and is a **REQUIRED
  member of the W1 control set AND of F(B_k)**: a W1 claim that has not beaten
  this cell is void. Claim licence: content-representation attribution at fixed
  retrieval, plus frontier membership. Its structural handicap for arms whose
  native retrieval is not dense-over-text is DISCLOSED beside its result — it is
  never grounds for excluding the cell (revision 1 used exactly that argument to
  demote this cell to an instrument, contradicting the binding KOT-FAIR/2
  contract; corrected).
- the **NATIVE cell** — each arm retrieves the way its architecture natively
  does (kernel addressing for S; the RAG arm's best in-budget retriever) under
  the same resource budgets — **ADDITIONALLY enters F(B_k)** as the
  strongest-system frontier point. Claim licence: "the best each architecture
  can do at the budget". It supplements the shared/matched cell; it never
  replaces it.

Every consuming prereg names which cell licenses which sentence.

**Rule 3 — retrieved-token/context budgets + ordering parity.** Pinned per rung:
max retrieved tokens per query (identical across arms), max context length,
context assembly order = retrieval-score-descending (no arm may hand-place gold
material at context edges — the position confound), and a position-shuffle
control cell lives in RAGC's factorial [LIT-BACKED: RAG.md §6.4,
Lost-in-the-Middle; STIPULATED: ASM-0853].

**Rule 4 — generator / executor / retry / tuning parity.** Where the comparison
is store-vs-store (matched-corpus arm vs S), the generator checkpoint, decoding
parameters, retry budget (same max-k), abstention accounting, and tool-executor
semantics are IDENTICAL across arms; tuning ≤ T_k per arm (§3.3). Where the
comparison is whole-system frontier (free-corpus arm), the generator may differ —
that arm's licence is "a better baseline exists at this budget", not attribution
[STIPULATED: ASM-0853].

**Rule 5 — construction leakage + authoring effort.** Every construction pass
(embedding sweeps, LLM extraction, selector training — the TinyAgent DeBERTa
lesson [LIT-BACKED: RAG.md §1]) is booked as build compute in KOT-LIFE/1 and its
artifacts' bytes in KOT-SIZE/2 figures (1)/(5) on EVERY arm identically.
Order-of-operations rule: derivation/construction pipelines are frozen
(content-hashed) BEFORE any frozen-suite item is drawn; the §2.2 decontamination
screen applies to construction INPUTS as well as outputs; a store or index whose
construction post-dates suite exposure is VOID for W1 use [STIPULATED: ASM-0853].

---

## 6. NL-boundary discipline (no smuggled oracle)

- DECISION: every frontier comparator consumes **natural benchmark text** — the
  NL-input integrity rule (ASM-0808) applies to comparators exactly as to S.
  Pure-neural and RAG arms satisfy this natively: their NL handling is part of
  their measured product, exactly as S's parser is part of S's
  [STIPULATED: ASM-0808 applied to comparators; ASM-0851].
- DECISION: the frontier NEVER receives gold parses, gold subgraphs, gold record
  addresses, or gold passages. One labelled exception class exists for
  DECOMPOSITION only: an `oracle-diagnostic` comparator (e.g. gold-passage
  injection as a retrieval ceiling) may be built for a G2/G3 analysis, is
  labelled per ASM-0814, **never enters F(B_k)**, and licenses no W1 claim
  [STIPULATED: ASM-0814 applied; ASM-0851].
- Asymmetry, stated so nobody "fixes" it later: the NLB gate (P3-E-NLB-1) binds
  KERNEL-store addressing from natural input — a measured wall of the kernel
  front-end [MEASURED: l3a-parse/a5-nl FAILs] — and does NOT bind the frontier's
  baselines. Weakening the frontier to share the kernel's wall would fake
  exactly the win W1 exists to make honest [STIPULATED: ASM-0851].

---

## 7. Threat-model counters implemented in the builder (feeds P3-D-THREAT)

### 7.1 Inherited channels, with their mechanised counters here

| Gaming channel (programme §2.0) | Counter in this design |
|---|---|
| Budget shopping | §1.2: anchor-derived B_k pinned at rung entry, immutable after first S measurement |
| Comparator dodging | §2 pinned enumeration rule + §7.2 nomination window; frontier version bump forced by any post-freeze release |
| Warm-cache-only reporting | §1.1/§3 S3: warm AND cold both measured and both admissibility-checked (P3-D-HW) |
| Batch-size shopping | pinned concurrency distribution (KOT-COST/2(g)) in every S3 measurement |
| Output-length inflation/deflation | pinned max-token + stop discipline per benchmark (KOT-COST/2(j)) |
| Tuning asymmetry | §3.3 T_k resource-vector meter, per-arm over the closed arm table, audit-trailed in KOT-LIFE/1 |
| Packaging games | all bytes via the ONE canonical packing script (KOT-SIZE/2), frozen base image; S0's analytic screen never substitutes for packing near the budget line |

### 7.2 The nomination window (comparator-dodging counter, concrete)

- DECISION: from frontier-build start until frontier freeze, ANY party (maintainer,
  reviewer, external referee) may nominate an open reproducible system or config
  for F(B_k); the builder must either admit it (measure under the common ledger)
  or publish a one-line refusal reason (licence, irreproducibility, static byte
  infeasibility). Post-freeze nominations queue for the next frontier version
  [STIPULATED: ASM-0812 comparator-pinning clause extended; ASM-0851].

### 7.3 The NEW channel this design must name: weak-builder gaming

The party building S also builds S's opponents — under-optimising the frontier
manufactures a fake W1 win. This is the frontier-side mirror of the answer-key
trap, and it gets first-class treatment:

- DECISION: five counters [STIPULATED: ASM-0812 threat-model extension;
  ASM-0854]:
  1. **Blinded challenger/regret gate (F-CAL A4, §8) — the decisive counter:**
     after the builder freezes its search result, independently nominated strong
     configurations are evaluated under the same dev budget; the builder's
     selected frontier must match or beat the best challenger within a fixed ε.
     Directly falsifies an under-searched frontier (and bounds S1 screening
     noise).
  2. **External-reproduction acceptance tests (F-CAL A2, §8):** pinned transforms
     must reproduce published reference behaviour (e.g. quantisation retention
     for a same-class model/method) within a pre-registered tolerance — a builder
     that cannot match known results cannot certify a frontier.
  3. **Full search disclosure:** every builder run publishes the complete config
     log — candidates enumerated, dropped (and why), compute spent per arm — the
     no-silent-caps rule applied to the search itself.
  4. **External referee pass:** the frozen frontier spec + build log goes through
     the standing GPT-5.6-class external review before any W1 experiment freezes
     against it.
  5. **Open nomination (§7.2)** — outsiders can strengthen the frontier we would
     be tempted to weaken.
- Honesty line carried on every W1 claim regardless: **baseline-search
  completeness remains a standing limitation** (programme §7.3) — W1's licensed
  claim is already narrowed to "every pre-registered, reproducible open comparator
  SEARCHED under budget B_k", never a universal [STIPULATED: ASM-0810 restated,
  not new].

---

## 8. Validation and falsifiability of the builder itself (F-CAL)

The builder is an INSTRUMENT and gets instrument gates before it judges anything
— the same discipline P3-E-CAL applies to the index. New experiment bead
**P3-E-FCAL** (co-scheduled with P3-E-CAL, same free-pool compute class; §13),
pre-registered with these acceptance criteria [STIPULATED: ASM-0854]:

- **A1 — monotonicity SMOKE TEST (necessary, NOT decisive):** at the R-1 anchor
  budget, the builder's best optimised entry must satisfy dev-index(best) ≥
  dev-index(naive anchor baseline) with LCB95 of the difference > −ε_A1 (a
  pre-registered non-inferiority margin; single one-sided CI per §2.5(4)). A
  builder whose "optimised" frontier loses to the untouched anchor is broken.
  Honest scope, per the review: the untouched anchor is itself available to the
  builder, so passing A1 is near-tautological — A1 catches plumbing breakage
  only; decisiveness against a weak builder lives in A4.
- **A2 — external reproduction:** for two pinned (model, quantisation-method)
  pairs with published retention figures, the builder's measured retention falls
  within a pre-registered tolerance band of the published figure. Catches silent
  tooling breakage AND crude weak-builder gaming (§7.3), but tests plumbing, not
  search strength.
- **A3 — repeatability:** two independent builder runs (different seeds, same
  grid) produce envelopes agreeing within a pre-registered band (dev-index ± ε_A3
  at each budget point) and select the same frozen configs or documented ties.
  An unstable selection rule cannot be frozen. (Repeatability, not decisiveness.)
- **A4 — blinded challenger/regret gate (the DECISIVE gate; added on review —
  A1–A3 alone can all pass on a consistently weak, under-searched frontier):**
  after the builder freezes its search result at a rung, a small challenger set
  (proposed n = 5–10 configurations) is nominated by parties independent of that
  builder run (maintainer + external referee + any §7.2 nominator), **blind to
  the builder's selected configs**, drawn from published recipes/leaderboards
  and from candidates the S1 screen discarded. Each challenger is evaluated ONCE
  under the same rung dev budget on the same rig. **PASS iff
  dev-index(builder's selected frontier best) ≥ dev-index(best challenger) −
  ε_A4** (pre-registered regret margin). A challenger win by more than ε_A4
  falsifies the frontier as under-searched; the challenger is admitted, the
  search defect is diagnosed, and one repair cycle is allowed. This gate also
  bounds the S1 screening-noise risk: a true-best comparator discarded by noisy
  successive halving on the 10% proxy resurfaces as a challenger
  [STIPULATED: ASM-0854].
- **Kill / fail-closed rule:** if A1, A2 or A4 fails after one pre-registered
  repair cycle, **no W1 experiment may cite F(B_k)** — every G4 [EXP] stays
  blocked (the builder fails closed, ERR-style, like everything else in this
  programme). A3 failure forces selection-rule redesign before freeze.
- **Dependency enforcement (closing the review's G4 wiring gap):** the
  fail-closed rule above is prose until it is a dependency. The programme's §5
  Phase-2 blocking rule currently requires P3-D-FRONTIER but neither
  P3-T-FRONT-IMPL nor P3-E-FCAL. DECISION: a **required registered amendment to
  the programme §5 G4 blocking set adds P3-T-FRONT-IMPL (implemented builder)
  and P3-E-FCAL PASS** alongside P3-D-FRONTIER, and the bead graph carries the
  corresponding `bd dep add` edges (§13). Until that amendment lands, no G4
  prereg may freeze [STIPULATED: ASM-0854].

Falsifiability of the design as a whole: FRONT/1 is falsified as an instrument by
its own F-CAL gates (A4 by construction can fail against outside nominations);
the frontier it produces is falsified per rung by W1's own test; and the design's
central stipulation — that a best-effort-optimised, honestly-ledgered baseline
frontier at 100M–2B is CONSTRUCTIBLE inside the available compute (free pool
through R-2; a secured allocation at R-3, §10) — is falsified if the §10 budget
is exhausted before A1–A4 pass [STIPULATED: ASM-0854].

---

## 9. What the frontier-builder consumes and emits (interface table)

| Interface | Direction | Contract |
|---|---|---|
| P3-D-INDEX (KOT-AI-INDEX/2, dev split, analysis plan) | consumes | dev split + floor/exclusion criteria + FWER procedure + comparator-covariance estimation + per-component class map (§4.2); builder never defines index content |
| P3-D-HW (KOT-COST/2 rig) | consumes | all S3 measurements on the pinned rig, warm/cold protocol, energy boundary labels (§1.1) |
| P3-D-BASE | consumes | pinned donor roster + twin recipe (C1/C5); FRONT supplies the enumeration rule + T_k values |
| P3-D-RAGC | emits | §5 rules 1–5 as binding defaults (Rule 2 as corrected); RAGC instantiates factorial cells, amends only by registered change |
| P3-D-THREAT | emits | §7 counters incl. the new weak-builder channel + its five counters |
| KOT-LIFE/1 (P3-D-LIFE) | emits | per-arm tuning meter (resource vector, arm table), build compute, authoring hours, verifier training |
| Every G4 [EXP] | emits | the frozen, versioned F(B_k) + envelope + build log |
| Programme §5 G4 blocking set | emits (required amendment) | P3-T-FRONT-IMPL + P3-E-FCAL PASS enter every G4 [EXP] blocked-by set (§8; ASM-0854) |
| P3-E-CAL | co-runs | F-CAL A1–A4 + the §4.6 TTC non-math calibration gate share the calibration campaign |

---

## 10. Compute plan (worked arithmetic; conditional at R-3, cheap-first)

- PREMISE: the free pool spans ARC, AIRR Gateway (application in flight per
  programme §6), TRC, Modal-for-Academics, ~$1k API credits [LIT-BACKED:
  docs/next/free-compute-recon.md, source-verified 2026-07-10, via programme §6].
- Worked arithmetic (planning estimates, not commitments; final at KOT-FAIR/2
  freeze; the throughput assumption — a 135M–360M-class model decodes ≥ ~1,000
  tok/s on one modern free-pool GPU — is replaced by measured P3-E-CAL figures)
  [STIPULATED: ASM-0854]:
  - **S1 screen (R-1):** ≤ ~180 candidates (§2.6) × ~150 mini-suite items ×
    ~256 output tokens ≈ 7M tokens round 1; halving shrinks later rounds; ≥2
    rounds ≈ **≤ ~4 GPU-h** + CPU-side BM25/packing (inside the CPU caps).
  - **S3 measurement (R-1):** ≤ ~24 admitted configs × ~1,500 dev items ×
    ≤ ~1,024 tokens/query (TTC escalation bounded: expected samples/query ≤ ~6
    at the τ defaults; worst-case N = 64 on ≤ ~10% of items by the §4.5 floor)
    ≈ ≤ ~40M tokens, warm + cold ≈ **≤ ~12 GPU-h**.
  - **Tuning (R-1):** arm table = 6 comparator arms (§3.3) × T_1 accelerator
    component 4 GPU-h = **≤ 24 GPU-h** (+ 6 × 40 CPU-core-h).
  - **R-1 builder total worst case ≈ 4 + 12 + 24 = ≤ ~40 GPU-h** — the cap now
    closes arithmetically (revision 1's 5 × 25 GPU-h/arm inside a 40 GPU-h total
    could not; the review's reconciliation defect, corrected). The builder is a
    SHARED instrument: this total sits beside, not inside, the per-family
    ≤ ~50 GPU-h experiment discipline of programme §4.
  - **R-2:** 6 arms × T_2 = 20 GPU-h = 120 GPU-h tuning + ~30 GPU-h
    screen/measure (≈3–4× R-1 per-token cost at 360M-class) = **≤ ~150 GPU-h
    total**, AIRR/ARC.
  - **R-3 (the tier revision 1 omitted — the review's missing-T₃ defect):**
    6 arms × T_3 = 80 GPU-h = 480 GPU-h tuning + ~120 GPU-h measurement =
    **≤ ~600 GPU-h builder total**, feasible ONLY inside a secured
    AIRR-Gateway/TRC-class allocation (programme §4: R-3 is maintainer- and
    allocation-gated). If no allocation materialises, the R-3 frontier does not
    freeze and every R-3 W1 claim stays blocked (fail-closed) — **the 100M–2B
    span is thereby CONDITIONAL and disclosed, never assumed**
    [STIPULATED: ASM-0854].
- Cost structure by stage: quantisation + packing are CPU/single-GPU trivial;
  RAG index builds are CPU + one embed pass; the dominant spend is (a) TTC
  evaluation (bounded by the N ≤ 64 cap and the dev mini-suite screen) and
  (b) recovery training for pruned entries (bounded by T_k, and OPTIONAL until
  the §2.2 pilot passes). Energy cells on the current pool are GPU-NVML-boundary
  at best, CPU-side MISSING (§1.1 rule). Local-box work (packing, byte
  accounting, envelope extraction, logs) is `nice -n 10` + checkpointed per
  standing practice; Modal runs follow the attached-run hygiene memory (explicit
  `modal app stop`, nohup+setsid).
- Graceful degradation: if no external GPU materialises, the C1×quantisation
  frontier + BM25 RAG arm + P1 self-consistency TTC are all CPU-or-single-free-GPU
  feasible — a valid (weaker, disclosed) frontier version can still freeze; P2/P3
  and pruning entries wait [STIPULATED: ASM-0854].

---

## 11. Honest limits of this design (carried on every consuming claim)

1. **Search completeness is not certifiable** — disclosed, bounded, refereed,
   never claimed (§7.3; programme §7.3 verbatim).
2. **Information parity across object representations is not fully certifiable**
   — four measured checks + disclosure, residual asymmetry named (§5 rule 1).
3. **Closed-corpus contamination of donor baselines is unauditable** — carried
   symmetrically per ASM-0812(1); the Oren logprob test is available for open
   donors via P3-D-SEAL's toolbox [LIT-BACKED: EVAL.md §4].
4. **TTC transfer to our band/suite is unmeasured until the §4.6 gate runs** —
   no Snell figure is ever a premise.
5. **T_k values and rung cost envelopes are stipulated planning numbers**, fixed
   finally at KOT-FAIR/2 freeze with maintainer sign-off; the §10 arithmetic
   closes on today's throughput assumption and is re-derived from P3-E-CAL
   measurements.
6. **A1–A3 are not decisive against a weak builder** — decisiveness rests on the
   A4 challenger gate plus open nomination and the external referee pass; a
   challenger pool that no one populates weakens A4, which is why nomination
   custody sits with the maintainer + external referee (§8).
7. **The energy dimension of B_k is non-binding by default** (§1.1 boundary
   rule): frontier claims are bytes/latency/memory-binding everywhere,
   energy-binding only on rigs where every compared arm shares a measurement
   boundary. R-3 buildability is CONDITIONAL on a secured allocation (§10).

---

## 12. Registered assumption entries + review change-map

Revision 1's provisional in-doc ids are retired; the register now carries
(append-only, block ASM-0850–0879):

| Registered id | Replaces | Scope |
|---|---|---|
| **ASM-0850** | P3F-A1 | budget-vector grammar incl. the one fail-closed energy rule (§1.1); anchor-derived one-primary-budget-per-rung; immutability; admissibility-not-inflation (§1.2) |
| **ASM-0851** | P3F-A2 | F(B_k) semantics; full-vector envelope reporting; corrected statistics interface; κ_pack packing rule; SURG-informed grid; counted lattice; seven-stage pipeline with estimated-screen→measured-fallback; leakage + selection rules; NL rules; nomination window (§1.3, §2, §3.1–3.2, §6, §7.2) |
| **ASM-0852** | P3F-A3 (+-T) | TTC recipe incl. per-class aggregation semantics (§4); T_k resource-vector meter + mechanical arm table + reconciled values (§3.3) |
| **ASM-0853** | P3F-A4 | matched-retrieval rules 1–5 with Rule 2 corrected: shared/matched cell REQUIRED in W1 control set + F(B_k); native cell additional (§2.3, §5) |
| **ASM-0854** | P3F-A5 (+annex) | F-CAL A1–A4 incl. the blinded challenger/regret gate; fail-closed + G4 dependency-enforcement amendment; closed compute arithmetic incl. R-3 (§7.3, §8, §10) |

Change-map: review point → revision-2 change:

| Review finding | Change here |
|---|---|
| Ranked 1: matched-RAG control contradicts KOT-FAIR/2 | §5 Rule 2 + §2.3(a) rewritten: shared/matched cell is a required F(B_k)/W1-control member; native cell additional (ASM-0853) |
| Ranked 2: T_k not dimensionally closed; "family" vague | §3.3: T_k = (GPU-h, CPU-core-h) vector, separately capped; mechanical closed arm table (ASM-0852) |
| Ranked 2: 5×25 GPU-h vs ≤40 total; R-2 conflict; no T₃/R-3 | §10 worked arithmetic closes each rung; T_1/T_2 revalued; R-3 tier added, allocation-conditional (ASM-0852/0854) |
| Ranked 2: energy universally binding vs MF0 missing-allowed | §1.1: one fail-closed boundary rule (report-always, bind-only-same-boundary) adopting MF0 §8.1 + SYS.md §2 (ASM-0850) |
| Ranked 3: F-CAL not decisive | §8 A4 blinded challenger/regret gate; A1 relabelled smoke test; kill rule covers A4 (ASM-0854) |
| Ranked 3: G4 block lacks FCAL/IMPL dependency | §8 dependency-enforcement amendment + §13 dep edges (ASM-0854) |
| "Six stages" miscount | §3 heading: seven stages S0–S6 |
| S0 analytic-bytes exclusion | §3 S0: κ_pack safety factor; near-budget candidates packed before exclusion (ASM-0851) |
| S2 selects on unmeasured admissibility | §3 S2/S4 + §3.2: estimated screen at S2, measured filter + fall-back selection at S4 (ASM-0851) |
| "Index vs cost" scalarises the vector | §1.3: named 2-D projections + full-space non-dominated set (ASM-0851) |
| Unsupported max-t power claim | §1.3: claim retracted; covariance estimated, P3-D-POWER sizes multiplicity (ASM-0851) |
| TTC semantics undefined off short answers | §4.2: per-component-class aggregation semantics table (ASM-0852) |
| "Low hundreds" lacked arithmetic | §2.6 counted lattice; §10 candidate×item×token×repetition arithmetic (ASM-0851/0854) |
| SURG described as in-flight though landed | header + §2.2: SURG findings (recipe, small-model warnings, scaling-law calculation, pilot gate) incorporated (ASM-0851) |

---

## 13. Beads this design spawns (recommendation — the coordinator creates them)

```bash
bd create --title="P3-E-FCAL: frontier-builder instrument gates (A1 smoke / A2 external reproduction / A3 repeatability / A4 blinded challenger-regret), co-scheduled with P3-E-CAL" \
  --type=task --priority=1 \
  --description="From docs/next/design/FRONT.md §8 (ASM-0854). Pre-registers and runs the builder acceptance tests on pure-neural material only; A4 challenger set nominated blind by maintainer + external referee (custody rule §8/§11.6); fail-closed: A1/A2/A4 failure blocks every G4 [EXP] from citing F(B_k). Free-pool compute class. Also hosts the §4.6 TTC non-math calibration gate." \
  --notes="Blocked by P3-T-FRONT-IMPL + P3-D-INDEX (dev split) + P3-D-HW (rig). experiment-designer freezes; runner runs; analyst reads out."
bd create --title="P3-T-FRONT-IMPL: implement the frontier-builder pipeline (S0-S6: enumerate/screen/optimise/measure/admit/envelope/pin + T_k resource-vector meter + arm-table ledger + build log)" \
  --type=task --priority=1 \
  --description="From docs/next/design/FRONT.md §3. Buildable harness: packing+quantisation grid (κ_pack rule), FlashRAG-pinned retrieval arms (shared/matched + native + free-corpus cells), TTC policy ladder w/ per-class aggregation semantics + self-charging estimator, metered tuning ledger (GPU-h + CPU-core-h per arm-table key) into KOT-LIFE/1, full-vector envelope extraction, content-hash pinning. Keep OUT of encoder/; lives with the Phase-X-style harness code." \
  --notes="CPU/single-GPU first (graceful-degradation path §10); Modal hygiene per standing memory."
# dependencies after creation:
bd dep add <P3-E-FCAL-id> <P3-T-FRONT-IMPL-id>
# G4 dependency enforcement (ASM-0854; requires the §8 programme amendment):
# for each G4/W1-relevant [EXP] bead (P3-E-VL-1, P3-E-RULE-1, P3-E-DD-1, P3-E-SCALE-2, ...):
bd dep add <G4-EXP-id> <P3-E-FCAL-id>
bd dep add <G4-EXP-id> <P3-T-FRONT-IMPL-id>
# and record that P3-D-RAGC (kernel-of-truth-s55r.15) consumes FRONT.md §5 (ASM-0853) as binding defaults
```

No other new beads: the frontier's consumers (every G4 [EXP], P3-E-CAL,
P3-D-RAGC, P3-D-BASE, P3-D-THREAT) already exist or are already named in the
programme WBS. The programme §5 blocking-set amendment (§8) is a coordinator
action on the programme doc + registry, not a bead this design can execute.

---

## Epistemic register (what this design relied on)

- **STIPULATED (registered block ASM-0850…ASM-0854):** every design choice
  above; each is a scoping/mechanism decision, none is evidence for any
  architecture family or for either value thesis.
- **MEASURED (restated strictly inside their envelopes):** the zero-audited-wins
  null + INCONCLUSIVE-PENDING verdicts (feasibility-synthesis §0–§2); the NL
  boundary FAILs l3a-parse 47.6% / a5-nl 41.6% + S2 (registry/verdicts/*); the
  f2b-replicate comparator shape incl. Skywork-PRM-1.5B 0.5267 (alignment-
  confounded, formal-only).
- **LIT-BACKED (through the three completed Phase-0 reviews consumed here,
  verified at source 2026-07-11):** the no-bytes-honest-published-win sweep
  reading, MassiveDS datastore scaling, Mallen adaptive retrieval, FlashRAG
  version pin, the Snell ICLR-2025 envelope, scaling-flaws decay scope,
  Cobbe/Math-Shepherd verifier recipes, TinyAgent selector lesson (RAG.md
  §§1–5); clause-(iv) consider-not-mandate, data-vs-compute-matched, near-floor
  MC instability, Oren test availability (EVAL.md §§2–9); Minitron/Sheared-LLaMA
  recovery recipes, SliceGPT small-model degradation, the distillation
  scaling-law regime caveat (SURG.md §1); the RAPL-absence + measurement-boundary
  findings (SYS.md §§2–3); anchor-overtraining + twin recipe (TINY.md §§2, 9 —
  interface only).
- **EXTRAPOLATION:** none used as a premise. The only forward projections in
  scope (TTC transfer to our band; pruned-entry value) are gated behind the §4.6
  calibration gate and §2.2's pilot-gated optional-member rule respectively.

This document changes no frozen object, no verdict, no audit; its five
assumption entries are REGISTERED in registry/assumptions.jsonl (append-only
block ASM-0850–0854) by this revision.
