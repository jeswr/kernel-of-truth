# P3-E-DECONF-0 — DECONF/1: the aligned-generic-store deconfound (experiment design)

> **Status: [EXP-DESIGN] deliverable of the round-1 steering (docs/next/analysis/
> round1-steering.md, "run the cheap decisive kills now" item (b), bead-to-be
> P3-E-DECONF-0). Nothing here is frozen, pre-registered, scheduled, or run; no
> verdict, audit, frozen object, or registered ruling is touched. The design's
> assumption entries are REGISTERED in the fresh append-only block
> **ASM-0960…ASM-0966** (block ASM-0960–0979 assigned to this bead; 0967–0979
> remain free).** Author: Fable, chief-architect role (`kern/fable-designer`),
> 2026-07-11. This design goes through the standing external (GPT-5.6-class)
> review before any prereg freeze.
>
> **Provenance of the question.** Both independent round-1 subjective analyses
> named, in nearly identical words, the programme's single biggest risk: *the
> kernel's distinctive semantics contribute nothing beyond what a generic typed
> store + executor + strong tool/RAG baseline already provide* — and both named
> the **aligned-generic-store deconfound** the highest-value early experiment
> (docs/next/analysis/round1-fable-subjective.md §3.1 item 2;
> poc/gpt56-review/round1-subjective/last-message.json §3 item 2 and closing
> lines; synthesised in round1-steering.md convergence items 5 and the
> recommended-kills list). This document is that experiment.
>
> **Blocked-by inputs, read in full at source:** docs/next/analysis/
> round1-steering.md; docs/next/feasibility-synthesis.md (§0–§2, §5);
> registry/experiments/f2b-replicate.json + registry/assessments/f2b-replicate
> does_not_license (as restated in the synthesis §2); registry/experiments/
> f2b-transfer.json + poc/f2b-transfer/judge-1-results/stage1-analysis.json;
> registry/experiments/knull.json (FROZEN v1) + knull-v2.json (DRAFT);
> poc/f2b/runner/f2b_runner.py (the pinned mechanism source);
> docs/next/design/FRONT.md §5 (ASM-0853 matched-retrieval rules);
> docs/next/design/RAGC.md (arm inventory GR-A/GR-C/GR-D, ASM-0920–0927);
> docs/next/design/MF0.md §8.5 (framework-owned content-type cells, ASM-0891);
> docs/next/lit/RAG.md (P3-LR-RAG).
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = a programme registry
> verdict/assessment/artifact restated strictly inside its envelope;
> `[LIT-BACKED: lit-review §]` = an external fact verified at primary source by a
> completed Phase-0 lit review, cited through that review; `[STIPULATED: id]` = a
> design choice made here or inherited from a registered stipulation;
> `[EXTRAPOLATION: id]` = a registered forward projection, never a premise.

---

## 0. Contract: the question, split where the mechanism splits it

The confound to cut, in the registry's own words: the one audited end-task
positive is *correct-alignment-specific, not shown kernel-content-specific* — "a
generic aligned answer-key + retry would reproduce it" — and its de-confound is
unrun.

- PREMISE: f2b-replicate PASSED — SmolLM2-135M + kernel-verify-retry (k=4) beats
  SmolLM2-1.7B-alone by +0.1507 absolute (one-sided 95% BCa LB +0.1053) at
  cost_ratio_vs_R3 = 0.103; the seed-pinned derangement recovers ~0 of the lift
  (point −0.021); the kernel arm beat gloss-self-verify (0.4893), the trained
  Skywork PRM-1.5B (0.5267), and the passive kernel-as-text null (0.4920)
  [MEASURED: registry/verdicts/f2b-replicate.json, audit CONFIRMED, restated per
  feasibility-synthesis §2].
- PREMISE: the lift's attribution ceiling is set by its own assessment — the
  verifier accepts iff the answer string-equals the canonical record while gold
  was DEFINED by that same equality, so the shuffled control provably cannot
  discriminate NSM content from correct record↔item alignment; nothing measured
  distinguishes the kernel store from ANY typed store + checker
  [MEASURED: registry/assessments/f2b-replicate.json does_not_license, adopted
  verbatim by feasibility-synthesis §2].
- PREMISE: the f2b-transfer stage-1 endorsement gate has just READ OUT and
  PASSED: blind external adjudication endorses the membership gold at
  A = 0.9784 (317/324 resolved pairs; one-sided 95% Wilson LB 0.9606 ≥ 0.70 bar;
  raw two-judge agreement 0.90; n_adjudicated 360; unresolved 36 ≤ 15% cap;
  adjudication_valid = true) — the definitional-circularity kill (d) did NOT
  fire, stage 2 is licensed, and 324 externally-labelled kernel-covered items
  now EXIST as a pinned scoring asset
  [MEASURED: poc/f2b-transfer/judge-1-results/stage1-analysis.json;
  registry/experiments/f2b-transfer.json stage-1 endorsement gate; the stage-1
  results-log append is runner-role work in flight].

The deconfound question — *is the lift kernel-specific or
generic-aligned-store-structural?* — decomposes along the measured mechanism
into two channels that need different experiments, only one of which is blocked:

**Channel 1 — the RUNTIME channel (this experiment).** In the verify-retry
topology the store content NEVER enters any prompt: the retry loop is
answer → deterministic check → reject → resample, and the store acts *only*
through `verifier.check()`, a pure normalised-string-equality / set-membership
function over three fields of the canonical record (definition text, term
label, claim list).

- PREMISE: the above is a code-level fact of the pinned harness —
  `run_verify_retry` calls `answer_once` (prompt = frames + item only, no
  record bytes) then `verify_answer` (IF-C extract then `verifier.check`), and
  the knull map M-V measured 3456/3456 verifier decisions bitwise-identical
  after stripping all non-gloss record fields [MEASURED:
  poc/f2b/runner/f2b_runner.py at the f2b-replicate harness pin (functions
  build_prompt, answer_once, run_verify_retry, verify_answer,
  KernelVerifier.check); registry/experiments/knull.json map M-V assumption].

So the runtime question is not "does NSM content help the model" — the model
never sees it — but "does the check function read ANYTHING a generic aligned
store lacks". That is decidable by exhaustive enumeration on a CPU, at ~$0
(§3).

**Channel 2 — the AUTHORED-CONTENT channel (knull-v2's, NOT this experiment).**
When surfaces are REGENERATED from each store (items and answers re-rendered
from NSM vs plain-dictionary vs nonce content), store content does reach the
model through the items themselves; that is the knull/knull-v2 K-NULL ablation
— FROZEN (v1) / DRAFT (v2), currently blocked on the maintainer-ratified
plain-arm quality-gate rewrite [MEASURED: registry/experiments/knull.json
status FROZEN + knull-v2.json status DRAFT; STIPULATED: ASM-0700/ASM-0703 the
ruling]. DECONF deliberately does NOT touch that channel, does not amend
knull/knull-v2, and is runnable NOW precisely because its generic store
requires ZERO authored prose (§2).

- DECISION: DECONF/1 is therefore staged cheap-first as three cells —
  **A1** (CPU, ~$0): the aligned-generic-store extensional-equivalence audit on
  the f2b verify-retry mechanism; **A2** (CPU, ~$0): the generic-typed-store +
  generic-executor reproduction of the a5-llm engine leg (the conventional-
  substrate control that assessment names as missing); **B** (single small GPU
  run, ≤ ~2 GPU-h / ≤ ~$15): the strong generic tool/RAG baseline through the
  IDENTICAL verify-retry topology on the SAME externally-adjudicated items,
  isolating alignment itself as the last unshared ingredient. Claim licences,
  gates and does-not-amend clauses per the registered contract
  [STIPULATED: ASM-0960].

Ownership map (no duplication):

| Cell | Factorial owner | DECONF's relation |
|---|---|---|
| A1 aligned generic answer-key store | MF0 §8.5 content-type cell (e) "aligned-non-kernel store" (ASM-0891) | DECONF instantiates the STRUCTURE-MINIMAL member (opaque-string projection, zero authoring); knull-v2 owns the authored-content members (plain/nonce) |
| A2 generic executor | RAGC GR-C (ASM-0924) | DECONF runs the right-sized precursor on the pinned a5-llm slice; the full manifest cell supersedes it when built |
| B generic RAG + matched retry | RAGC GR-A / GR-D (ASM-0920/0924) | DECONF runs right-sized precursors at the f2b scope, adopting the FRONT/1 §5 parity mechanics (ASM-0853) that apply; superseded by the RAGC manifest cells at any G4/W1 use |

Gate placement: A1/A2 are census/diagnostic-class (G1-class, CPU, no model);
B is a G2-class attribution experiment on the covered slice — no cell here is a
W1 claim, nothing is NLB-gated (no natural-language input exists anywhere in
this design), and no cell licenses any competitiveness sentence
[STIPULATED: ASM-0960].

---

## 1. The mechanism fact the whole design leans on (stated once, precisely)

For every arm f2b-replicate and f2b-transfer run or plan, the pipeline is a
deterministic function of (models, items, seeds, store) in which the store is
consulted ONLY through `check(record_extracted_from_answer, item)` — accept /
reject / abstain — and through nothing else: no store bytes in any prompt, no
store-dependent decoding, no store-dependent seed arithmetic [MEASURED:
poc/f2b/runner/f2b_runner.py at the pinned f2b-replicate harness manifest —
build_prompt takes (frames, item, context_docs) and the verify arms pass no
context_docs; resampling is det_u over (arm, item id, seed, attempt) only].

Consequence (a determinism statement, not a hypothesis): if a substitute store
S′ yields the SAME check() decision as the kernel store on every (item,
admissible answer) pair, then every output, every per-item correctness bit,
every endpoint, and every verdict of every run of this topology — past AND
future, membership-gold or external-gold — is invariant under kernel→S′
substitution. The deconfound therefore does not need to re-run any model to
decide the runtime channel: it needs to measure decision concordance over the
FULL reachable decision space, which is finite and small (closed answer sets:
≤4 options or yes/no per item). That is Stage A1.

---

## 2. The generic stores (all derivation, no authoring)

### 2.1 GS-A — the aligned generic answer-key store (Stage A1/B)

- DECISION: GS-A is a **mechanical field projection** of the pinned kernel-v0 /
  molecules-v0 store onto exactly the read-set of `check()`: per covered
  concept, the four-column row `{concept_id, term_label(s), canonical_text,
  claims[]}` — every byte copied verbatim from the kernel's own records, all
  NSM structure (explication trees, primes, vectors, types, provenance frames,
  engine hooks) DELETED. Derivation is one deterministic seed-free script,
  content-hashed; the row set is coverage-identical and alignment-identical to
  the kernel store by construction (same record_path keys the items already
  pin) [STIPULATED: ASM-0961].
- Why this is runnable today when knull-v2 is not: GS-A **authors nothing** —
  it contains no new prose, so the maintainer language-quality gate on authored
  control stores (the knull plain-arm ruling) has no object here; the
  quality-gate applies to authored aligned stores (knull-v2's plain arm), not
  to a byte-projection of the kernel's own strings [STIPULATED: ASM-0961; the
  ruling itself is ASM-0700/ASM-0703, untouched].
- What GS-A operationalises: the exact phrase both reviews used — "a plain
  aligned answer-key". It is the STRUCTURE-MINIMAL member of the MF0 §8.5
  content-type family (cell (e) direction): same coverage, same alignment, none
  of the kernel's semantics [STIPULATED: ASM-0961].

### 2.2 GS-C — the generic typed store + generic executor (Stage A2)

- DECISION: the a5 code-vertical typed world (the no-LLM deterministically
  extracted records the a5 engine runs on) loaded into the RAGC-pinned generic
  deterministic engine — SQLite with a pinned recursive-CTE query library (the
  GR-C default, ASM-0924) — exposing `lookup / neighbors / check` over the same
  typed content; query library version-pinned and content-hashed
  [STIPULATED: ASM-0963, adopting the ASM-0924 executor default].

### 2.3 GS-R — the strong generic tool/RAG store (Stage B)

- DECISION: BM25 over the pinned common text serialisation of the SAME store
  records (the existing deterministic renderer — the serialisation ASM-0922
  pins), index bytes charged, retrieved context injected through the harness's
  existing context_docs path at a pinned retrieved-token cap identical across
  arms; BM25 is the mandatory lexical cell and a dense embedder is NOT added at
  this right-size (disclosed; the RAGC manifest owns the dense cell)
  [STIPULATED: ASM-0964; LIT-BACKED: RAG.md §6.2 — BM25 as the robust zero-shot
  lexical baseline, BEIR, arXiv:2104.08663, NeurIPS 2021].

---

## 3. Stage A1 — the extensional-equivalence audit (the cheapest falsifier, ~$0, CPU)

### 3.1 Procedure

- DECISION: enumerate the FULL decision grid — for each of the three pinned
  item corpora (d-qa 650, d-qa-r 1000, d-qa-t 360; corpus hashes as pinned in
  the f2b-replicate / f2b-transfer records) × every admissible answer in the
  item's closed answer space (each MC option; yes and no for claim items) ×
  both verifier variants (true map; the seed-pinned shuffled derangement,
  replayed with the same recorded permutation applied to GS-A rows) — compute
  the decision triple (extract_ok, decidable, consistent) under (i) the pinned
  KernelVerifier over the kernel store and (ii) the same checker class over
  GS-A. Grid size ≤ ~16k decision pairs (2,010 items × ≤4 answers × 2
  variants); pure string ops; minutes on the local box at nice -n 10
  [STIPULATED: ASM-0962].

### 3.2 Metric and decision rule

- DECISION: the primary statistic is **C_dec = concordant decision triples /
  total grid size** — an exhaustive COUNT over the full reachable decision
  space, so it carries no sampling error and no confidence interval; the
  pre-registered reading [STIPULATED: ASM-0962]:
  - **C_dec = 1.0 ⇒ verdict-input KERNEL-RUNTIME-GENERIC (the deflationary
    half).** By §1 determinism, the generic aligned answer-key store reproduces
    every F2-line endpoint VERBATIM: the reproduction statistic the steering
    asked for is `R_repro = lift(GS-A) / lift(kernel) ≡ 1.0` identically — the
    measured +0.1507, its CIs, the shuffled-control readings, and every future
    output of the same topology (including f2b-transfer stage-2's external-gold
    endpoints when they run) are bit-for-bit invariant under kernel → GS-A
    substitution. The kernel-SPECIFIC runtime claim on the F2 line is dead at
    this scope, at zero model spend.
  - **C_dec < 1.0 ⇒ a runtime kernel channel EXISTS.** Every discordant (item,
    answer, variant) triple is emitted and classified by check-path (def-match
    / term-match / claim / shuffled-composition); a discordance lying on a
    trajectory reachable by any logged run additionally raises a flag on the
    f2b-replicate interpretation (flag only — the frozen verdict is untouched).
    The discordance classes become the measured definition of "what the kernel
    semantics do at runtime" and Stage B adds the kernel-verify arm back
    (§5.1's conditional arm) so the channel is priced end-to-end.
- Falsifiability, stated honestly: C_dec = 1.0 is the EXPECTED outcome — the
  strip is a projection onto check()'s read-set, and the knull M-V map already
  measured the vector/AST fields inert (3456/3456) [MEASURED:
  registry/experiments/knull.json map M-V]. The residual falsification room is
  real but narrow: the term-for-definition path (`shown_definition`), the
  claim-polarity membership path, the shuffled-map composition, and any
  unnoticed engine consultation inside the checker would each surface as
  discordance. The registered expectation is EXTRAPOLATION ASM-0966
  (non-load-bearing, resolved by the run itself); the VALUE of the stage does
  not depend on surprise — see §3.3.

### 3.3 Why this is worth registering even if the outcome is expected

The assessment's circularity reading is currently an ANALYTIC argument attached
to a does_not_license note; programme discipline treats analytic readings and
measured facts differently, and two external reviews have now demanded this
deconfound be EXECUTED rather than argued (round1-steering item 5; the
GPT-5.6 subjective analysis: "the cheap aligned-store control should not
wait"). Stage A1 converts "a generic aligned answer-key WOULD reproduce it"
into "a generic aligned answer-key DOES reproduce it, bit-for-bit, measured
over the exhaustive decision space" — a registered, citable, audit-checkable
fact that (a) every future F2-line claim must carry (§7), (b) re-scopes the
headline language mechanically (§6), and (c) does so without spending the GPU
budget, the human-annotation queue, or the knull quality-gate path that block
every other deconfound [STIPULATED: ASM-0962].

---

## 4. Stage A2 — the generic-executor reproduction of the a5-llm engine leg (~$0, CPU)

- PREMISE: a5-llm PASSED as a substrate comparison — deterministic engine
  conj 1.0 vs best gate-valid LLM cell 0.3398 (+0.6602, LB +0.6346) at
  cost_ratio_min 22,836× — and its own assessment caps the reading: there was
  NO conventional-substrate arm, so "nothing distinguishes the kot-axiom kernel
  from ANY typed store + checker" [MEASURED: registry/verdicts/a5-llm.json PASS
  and registry/assessments/a5-llm.json does_not_license, restated per
  feasibility-synthesis §1].
- DECISION: Stage A2 supplies that missing arm at its cheapest honest size: the
  pinned 977-query kot-query-code/1 slice is run against GS-C (§2.2 — the same
  typed world in SQLite + pinned query library), CPU-only, and read on two
  endpoints: **A_exec** = exact-output agreement with the kot-axiom engine's
  answers on the same queries, and **acc_generic** = correctness against the
  pinned slice gold; per-query wall-clock co-reported (no cost claim tested)
  [STIPULATED: ASM-0963].
- DECISION: decision rule — A_exec ≥ 0.99 AND acc_generic point-equal to the
  engine's covered accuracy at the slice's resolution ⇒ verdict-input
  ENGINE-GENERIC-AT-SCOPE: the a5-llm PASS's licensed sentence is confirmed AS
  its ceiling ("a deterministic engine over its own extracted typed records…"),
  now with the generic-substrate arm measured rather than argued; the kernel
  ENGINE's distinctive contribution on this slice is bounded by the (1 −
  A_exec) residual, which is enumerated and classified (expressiveness gaps in
  SQL/CTE vs engine semantics are the interesting class and are reported as
  such, not hidden). A_exec materially < 0.99 ⇒ the engine does measurable work
  a generic executor does not reproduce — the first positive
  engine-distinctiveness datum in the registry, worth its own follow-up
  [STIPULATED: ASM-0963]. Failure-shape honesty: an UNDER-BUILT query library
  fakes engine-distinctiveness, so A2 inherits the anti-weak-control counter —
  the library is built to reproduce the QUERY GRAMMAR spec, its full source is
  published with the readout, and any non-reproduced class is checked against
  the grammar before being credited to "engine semantics"
  [STIPULATED: ASM-0963, mirroring the ASM-0922 anti-weak-control rule].

---

## 5. Stage B — the strong generic baseline through the identical topology, on external gold (GPU, right-sized)

Stage A1 settles what the ALIGNED generic store does (everything). The live
question it cannot settle: is the ALIGNMENT itself the load-bearing ingredient,
or would a strong generic tool/RAG baseline — same snapshot, same budgets, NO
item-aligned key — reproduce the lift too? f2b-replicate never ran a generic-RAG
arm [MEASURED: registry/experiments/f2b-replicate.json dropped_arms — RAG
dropped at right-size; the F2 confirmatory readings stand at F2's scope], and
both reviews name that the missing first-class rival.

### 5.1 Arms (all at rung R1 = the pinned SmolLM2-135M revision; 250-item d-qa-t eval prefix; 3 seeds; k = 4)

| Arm | Definition | Cell lineage |
|---|---|---|
| R1-alone | attempt-0 only, no store, no retrieval | the shared floor |
| GS-A-verify-retry | the §2.1 generic store behind the UNCHANGED verify-retry loop | MF0 cell-(e) structure-minimal member; equals the kernel arm bit-for-bit iff A1 C_dec = 1.0 on d-qa-t |
| GR-A-lite (RAG-alone) | BM25 top-j rendered records injected via context_docs, attempt-0 | RAGC GR-A precursor |
| GR-D-lite (RAG + generic retry) | GR-A-lite wrapped in the SAME loop shape — same k, same resample rule, same abstain-on-exhaustion — with the pinned GENERIC acceptance signal (the harness's existing gloss-self-check over the RETRIEVED text, i.e. acceptance consults retrieval, never the aligned key) | RAGC GR-D precursor |
| kernel-verify-retry (CONDITIONAL) | added back ONLY if A1 found any reachable discordance on d-qa-t; otherwise NOT run — the GS-A arm carries both readings under measured identity | fail-closed conditional |

- DECISION: scoring — every endpoint on the pinned blind external-adjudication
  gold (the d-adj-t labels stage 1 just produced), item-for-item the same
  250-item externally-labelled eval prefix, seeds, decoding, prompt frames, and
  token discipline as the frozen f2b-transfer stage-2 design, so the two
  experiments' cells are diagnostically comparable (comparability is a labelled
  DIAGNOSTIC, never verdict-bearing across records); DECONF-B consumes NO
  logged cell of any frozen record — every arm is a fresh run under this
  design's own (future) prereg [STIPULATED: ASM-0964].
- DECISION: parity mechanics, adopted right-sized from the registered rules
  rather than re-invented: one retrieved-token cap identical across arms with j
  floating to fill it (ASM-0923's token-not-object matching); generator
  checkpoint / decoding / stop discipline / abstention semantics identical
  across arms with only the evidence slot varying (ASM-0924); BM25 index bytes
  and build compute reported on the arm's ledger row (ASM-0853 Rule 5 / ASM-0925
  shape). Deviations from the full RAGC inventory (no dense cell, no PS/RD
  perturbation cells, no GR-B/GR-C arm here) are DISCLOSED right-sizing, and
  every such cell remains owned by the RAGC manifest for any later G4 use
  [STIPULATED: ASM-0964].

### 5.2 Endpoints, statistics, decision rules

- DECISION: instrument gates first, all inherited shapes: P10 extraction gate;
  the RT-7a engagement gate on every retry arm (decidable_fraction ≥ 0.95 for
  the GS-A arm; attempt-0 rejection in [0.05, 0.95]; ≥1 final ≠ attempt-0);
  headroom gate acc_ext(R1-alone) ≤ 0.85; plus the **bridge gate** (knull's
  pattern): lift_ext(GS-A-verify-retry over R1-alone) one-sided 95% BCa LB
  above +0.05 — if the aligned-store lift does not reproduce on external gold
  there is nothing to attribute and the verdict is INSTRUMENT-INVALID-at-B
  (Stage A1's result stands regardless; and if f2b-transfer stage-2 has read
  out by then, a bridge failure here against a stage-2 success is a flagged
  inconsistency to investigate, not silently absorbed) [STIPULATED: ASM-0964].
- DECISION: primary endpoint — **recovery_RAG = lift_ext(GR-D-lite) /
  lift_ext(GS-A-verify-retry)**, both lifts over the shared R1-alone floor,
  paired item-level BCa bootstrap (B = 10,000, PRNG seed pinned at freeze), with
  the pre-registered readings [STIPULATED: ASM-0964]:
  - **recovery_RAG point ≥ 0.70** ⇒ ATTRIBUTION-COLLAPSE-AT-SCOPE: the strong
    generic baseline reproduces the lift WITHOUT the aligned key — even
    alignment is not the distinctive ingredient; this is the direct measured
    input to the K-P3v2(4) attribution-collapse kill at this scope, and the
    F2-line efficiency story survives only as "retrieval + retry at matched
    budget".
  - **recovery_RAG one-sided 95% BCa UB < 0.30 AND Δ_align =
    lift_ext(GS-A-verify-retry) − lift_ext(GR-D-lite) LB > 0** ⇒
    ALIGNMENT-SPECIFIC: the lift requires the item-aligned deterministic
    acceptance; combined with A1 (the aligned store is kernel-agnostic), the
    licensed sentence becomes exactly: *verify-retry against an item-aligned
    deterministic answer key lifts a 135M host on this slice; the kernel is one
    way to AUTHOR such a key; no kernel-specific runtime contribution is
    measured* — routing all remaining kernel value to the authoring/economics
    legs (knull-v2 content, A-F0 mint cost).
  - **between** ⇒ PARTIAL, reported with both bounds, no collapse call either
    way; secondary readout GR-A-lite (retrieval alone, no retry) prices how
    much of any recovery is retrieval vs loop shape (the GR-D − GR-A contrast
    of ASM-0926, right-sized).
- DECISION: reporting requirements — full contrast vector (never the headline
  alone), retrieval hit@j against the item's pinned record co-reported for the
  RAG arms, per-type breakdown descriptive-only, every verdict sentence naming
  the arm that licenses it (the ASM-0926 discipline, right-sized)
  [STIPULATED: ASM-0964].

### 5.3 What Stage B deliberately does not measure

No R3/1.7B arm (the efficiency non-inferiority against R3 on external gold is
f2b-transfer's frozen endpoint, not re-litigated here); no PRM arm (HC3 closed
at its size class in f2b-replicate); no NL input anywhere (all items are the
kernel-rendered templated surfaces — the NL wall is l3a-parse/a5-nl territory
and untouched); no coverage claim (all items are kernel-covered by
construction; the mandatory disclosure rides every readout: kernel-
expressibility coverage 0.3542 at rung molecules-v0, measured by m0b on one
incomplete kernel-v0 instance, NOT general coverage) [STIPULATED: ASM-0964].

---

## 6. Verdict semantics for the whole experiment (equal prominence, pre-registered)

- DECISION: DECONF/1's verdict object carries THREE independent readings, one
  per stage, each with its licensed sentence and its kill wiring; no stage's
  outcome is promoted into another's scope [STIPULATED: ASM-0965]:

| Stage outcome | Verdict input | Licensed consequence (mandatory narration) |
|---|---|---|
| A1 C_dec = 1.0 | KERNEL-RUNTIME-GENERIC | every F2-line claim henceforth carries the invariance lemma: "the store's runtime role is an aligned deterministic answer key; all measured F2-line endpoints are invariant under replacement of the kernel store by its four-column projection"; headline language re-scopes to "aligned deterministic answer-key + retry" pending knull-v2 on the content channel |
| A1 C_dec < 1.0 | KERNEL-RUNTIME-CHANNEL-FOUND | discordance classes published; f2b-line interpretation flagged where reachable; Stage B runs the conditional kernel arm |
| A2 A_exec ≥ 0.99 | ENGINE-GENERIC-AT-SCOPE | the a5-llm does_not_license ceiling is measured, not argued; a5-llm narration unchanged (it already claims no more) but now closed against the missing-control objection |
| A2 A_exec < 0.99 | ENGINE-DISTINCTIVE-RESIDUAL | the residual class is the first measured engine-specific runtime datum; follow-up design bead recommended |
| B recovery_RAG ≥ 0.70 (point) | ATTRIBUTION-COLLAPSE-AT-SCOPE | K-P3v2(4) input at this scope; F2-line survives only as generic retrieval + retry |
| B recovery UB < 0.30 ∧ Δ_align LB > 0 | ALIGNMENT-SPECIFIC | the deconfound's constructive outcome: value = the aligned key; kernel = one authoring route; runtime distinctiveness: none measured (from A1) |
| B bridge/instrument gate failure | INSTRUMENT-INVALID-at-B | nothing attributed; A1/A2 stand; inconsistency with any landed f2b-transfer stage-2 read is flagged for investigation |

- DECISION: the deflationary outcomes get EQUAL prominence with any positive —
  the knull discipline verbatim; and the rescue paths for kernel-specific value
  are named IN the verdict so the outcome cannot be spun: (i) authored-content
  superiority (knull-v2 PASS-CONTENT), (ii) authoring economics (A-F0), (iii)
  any A1/A2 discordance residual. None of these is licensed by DECONF; each is
  where DECONF's deflationary outcome says to look next
  [STIPULATED: ASM-0965].

---

## 7. How DECONF slots into KOT-FAIR/2

1. **The invariance lemma as a standing rider.** On A1 = 1.0, the lemma of §6
   row 1 attaches to every F2-line consuming claim exactly as the coverage
   disclosure does today — a mandatory one-line rider, enforced at readout
   review, until and unless a later measurement (knull-v2 content channel, an
   A1 re-run after any store/checker version change) modifies it. Any change to
   the checker or store schema invalidates the lemma and requires an A1 re-run
   (the audit is minutes of CPU, so this is cheap insurance, mirroring the
   encoder content-hash discipline) [STIPULATED: ASM-0965].
2. **K-P3v2(4) wiring.** Stage B's contrasts are the right-sized first instance
   of the S − GR-A / S − GR-D contrast family that ASM-0926 wires into the
   attribution-collapse kill; DECONF feeds that kill AT THIS SCOPE only — the
   programme-level kill still requires the RAGC manifest cells at G4
   [STIPULATED: ASM-0965].
3. **Relation to the frozen F2 line.** DECONF amends nothing: f2b-replicate's
   PASS, f2b-transfer's frozen design and stage-1 PASS, knull's frozen record
   and knull-v2's draft all stand byte-identical; DECONF adds the deconfound
   readings their own assessments called for [STIPULATED: ASM-0960].
4. **Relation to the RAGC/FRONT machinery.** DECONF's cells are declared
   right-sized PRECURSORS: they adopt the applicable registered parity rules
   (ASM-0853/0923/0924/0925/0926) without waiting for the manifest
   infrastructure, per the steering's freeze-scaffolding/measure-now
   directive; when the RAGC manifest lands, its cells supersede these for all
   G4/W1 use and DECONF's readings remain valid at their own scope
   [STIPULATED: ASM-0960].

---

## 8. Compute plan (cheap-first, worked)

Planning estimates, never measurements [STIPULATED: ASM-0964]:

- **A1: ~$0.** ≤ ~16k decision-pair evaluations of pure string ops + one
  4-column store projection script; local box, nice -n 10, minutes to hours
  including harness plumbing; no model, no GPU, no API. Runnable the day the
  (post-review) prereg freezes.
- **A2: ~$0 compute; the cost is engineering.** SQLite + a pinned CTE query
  library over the a5 typed world; 977 queries execute in seconds; the query
  library is roughly a day of implementation and is itself a published,
  reviewable artifact (the anti-weak-control requirement).
- **B: ≤ ~2 GPU-h, ≤ ~$15, Modal, one container.** ~250 items × 3 seeds ×
  (1 + ≤5 + 1 + ≤10) generations/item across the four arms at 135M-class
  option-scoring throughput; BM25 build is CPU. Co-schedulable with the
  f2b-transfer stage-2 campaign (same image, same corpus assets) without
  touching that record's run; inside the standing free-pool/Tier-0
  authorization, with prereg-freeze + runner-role separation (designer never
  runs/grades) exactly as knull pins it.
- Sequencing: A1 → (A2 ∥ B). A1 first because its outcome decides B's
  conditional kernel arm and licenses B's arm-sharing economy; A2 is
  independent and can fill CPU time while B waits for its freeze.

---

## 9. Honest limits of this design

1. **A1 can only close the runtime channel.** A C_dec = 1.0 outcome says
   nothing about authored-content value (knull-v2's question), authoring
   economics (A-F0), consumption channels (A-E2), or any future architecture
   whose coupling is not answer→check→resample. The lemma it licenses is
   scoped to THIS checker/store version pair by content hash.
2. **A1's expected outcome is known-direction.** Registered as EXTRAPOLATION
   ASM-0966 (non-load-bearing); the stage's value is conversion of an analytic
   claim into a measured, riding, re-checkable fact — §3.3 — not surprise.
3. **A2's generic executor can be under-built.** The counter is publication of
   the full query library + grammar-conformance check before any
   "engine-distinctive" credit; residuals are classified, not headline-ified.
4. **B is one retriever, one acceptance signal, one vertical, 250 items.**
   "No generic signal reproduces it" is NOT in B's licence space — only "BM25
   retrieval + the pinned generic self-check at matched budget does not";
   the RAGC menu owns the wider claim. B's external-gold scoring inherits the
   d-adj-t protocol's own limits (single human judge-1 + fallback judge
   sourcing as disclosed in the f2b-transfer record).
5. **Cross-record comparability is diagnostic only.** Bit-level agreement
   between DECONF-B's GS-A arm and f2b-transfer stage-2's kernel arm is
   expected under A1 identity but can be broken by cross-container numeric
   nondeterminism; it is read as a diagnostic, never as an endpoint.
6. **Thresholds (0.99, 0.70/0.30, +0.05 bridge, token caps) are stipulated
   planning values**, maintainer-adjustable at prereg freeze; the 0.30/0.70
   recovery bounds deliberately reuse the f2b shuffled-control convention so
   the programme's recovery statistics stay commensurable.

---

## 10. Registered assumption entries

Fresh append-only block ASM-0960–0979 (this bead); entries 0967–0979 remain
free.

| Registered id | Scope |
|---|---|
| **ASM-0960** | DECONF contract: two-channel decomposition (runtime vs authored-content), stage inventory A1/A2/B with claim licences and gate placement, does-not-amend clauses, precursor/supersession relation to knull/knull-v2/f2b-transfer/RAGC/MF0 (§0, §7) |
| **ASM-0961** | GS-A derivation rule: mechanical four-column projection of the kernel store onto the check() read-set; zero authored prose (hence outside the ASM-0700 quality-gate's object class); deterministic pinned script + content hash; coverage/alignment identity by construction (§2.1) |
| **ASM-0962** | Stage A1 semantics: exhaustive decision-grid enumeration, C_dec counting statistic (no CI), the store-substitution invariance licensing rule at C_dec = 1.0, discordance classification + reachable-trajectory flag protocol, and the value-independent-of-surprise registration rationale (§3) |
| **ASM-0963** | Stage A2: GS-C = a5 typed world in pinned SQLite + published CTE query library; endpoints A_exec + acc_generic on the pinned 977-query slice; 0.99 decision rule; anti-weak-control publication + grammar-conformance requirement (§4) |
| **ASM-0964** | Stage B: arm set (R1-alone, GS-A-verify-retry, GR-A-lite, GR-D-lite, conditional kernel arm), external-gold scoring on the pinned d-adj-t labels, fresh-runs rule, right-sized parity adoption (token cap, generator parity, ledger rows), instrument + bridge gates, recovery_RAG/Δ_align endpoints with 0.70/0.30 rules, reporting requirements, compute caps + planning constants (§5, §8) |
| **ASM-0965** | Verdict + wiring: three independent stage readings with equal-prominence deflationary outcomes and named rescue paths; the invariance-lemma rider rule incl. re-run-on-version-change; K-P3v2(4) input mapping at scope (§6, §7) |
| **ASM-0966** | EXTRAPOLATION (non-load-bearing): expected A1 outcome C_dec = 1.0; resolved by the stage-A1 run itself |

---

## 11. Beads this design spawns (recommendation — the coordinator creates them; no bd operation is performed by this document)

```
P3-E-DECONF-0   [task, P0]  Freeze + run DECONF/1 stages A1/A2 (CPU, ~$0) per
    this design after external review; emit the two verdict-inputs + the
    invariance-lemma artifact (discordance file, store projection hash).
    The steering already names this bead; stage A1 is the first
    "cheap decisive kill" of the ratified next-wave list.
P3-E-DECONF-B   [task, P1]  Prereg + freeze + run Stage B (single GPU run,
    <= ~2 GPU-h) once A1 reads out; co-schedule with the f2b-transfer
    stage-2 campaign; runner-role separation per the knull pattern.
Dependency edges: P3-E-DECONF-B blocked-by P3-E-DECONF-0 (conditional arm
    rule) + the d-adj-t label pin (already produced by f2b-transfer stage 1).
```

---

## Epistemic register (what this design relied on)

- **STIPULATED (registered block ASM-0960…ASM-0966):** every design choice
  above; none is evidence about any store, engine, or thesis. Inherited binding
  stipulations consumed: ASM-0853 (matched-retrieval rules), ASM-0922/0923/
  0924/0925/0926 (RAGC mechanics, adopted right-sized), ASM-0891 (MF0 cell
  ownership), ASM-0700/0703 (the knull plain-arm ruling, untouched), ASM-0812/
  0813/0814 (controls, statistics, oracle labelling).
- **MEASURED (restated strictly inside their envelopes):** f2b-replicate PASS
  +0.1507 / LB +0.1053 / cost 0.103 / shuffled ~0 and its does_not_license
  ceiling; the f2b-transfer stage-1 endorsement A = 0.9784 (LB 0.9606, gates
  valid; artifact poc/f2b-transfer/judge-1-results/stage1-analysis.json,
  results-log append pending); the knull M-V map 3456/3456; a5-llm PASS
  +0.6602 with its no-conventional-substrate ceiling; the harness mechanism
  facts read from poc/f2b/runner/f2b_runner.py at its pin; m0b coverage 0.3542
  (corpus-indexed, restated only as the mandatory disclosure).
- **LIT-BACKED (through completed Phase-0 reviews):** BM25 as the mandatory
  lexical baseline (BEIR, arXiv:2104.08663, NeurIPS 2021, via RAG.md §6.2);
  the matched-control no-precedent finding and accounting rules consumed via
  RAG.md §3/§6 as already registered in ASM-0853/0920-0927.
- **EXTRAPOLATION:** exactly one, ASM-0966 (expected A1 outcome),
  non-load-bearing, resolved by the run; no premise or decision in this
  document rests on it.

This document changes no frozen object, no verdict, no audit, no ruling; its
seven assumption entries are REGISTERED in registry/assumptions.jsonl
(append-only block ASM-0960–0966) by this design. No git, bd, or kb-sync
operation is performed.
