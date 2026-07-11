# P3-E-DECONF-0 — DECONF/1: the aligned-generic-store deconfound (experiment design, rev-B)

> **Status: [EXP-DESIGN] deliverable of the round-1 steering (docs/next/analysis/
> round1-steering.md, "run the cheap decisive kills now" item (b), bead-to-be
> P3-E-DECONF-0). Nothing here is frozen, pre-registered, scheduled, or run; no
> verdict, audit, frozen object, or registered ruling is touched. The design's
> original assumption entries are REGISTERED in the append-only block
> **ASM-0960…ASM-0966**; this revision's amendments are carried as
> **PROPOSED-ASM-1010…ASM-1017** (disjoint block ASM-1010–1019 requested for
> this bead; the coordinator registers them at commit — this document edits no
> registry file). Author: Fable, chief-architect (designer role), 2026-07-11.**
>
> **REVISION B (this document): the GPT-5.6 review-gate revision.** The
> standing external review (poc/gpt56-review/rev-deconfb-20260711/
> last-message.json) ruled the rev-A draft "not ready to freeze as written":
> A1's claim was overstated, Stage B's acceptance signal smuggled the aligned
> record back in via the item URN, the statistics and KOT-FAIR slotting did not
> match the ratified RAGC framework, and the resource accounting was
> incomplete. Every concern is addressed in the body below and cross-indexed
> in the closing "GPT-5.6 review-gate response" section. The core direction is
> unchanged: A1 cheap equivalence certificate + A2 portability audit + Stage-B
> generic-store deconfound.
>
> **Provenance of the question.** Both independent round-1 subjective analyses
> named, in nearly identical words, the programme's single biggest risk: *the
> kernel's distinctive semantics contribute nothing beyond what a generic typed
> store + executor + generic tool/RAG baseline already provide* — and both named
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
> docs/next/design/RAGC.md (arm inventory GR-A/GR-C/GR-D, the frozen GR-D
> acceptance-signal menu §5.2, the ratified f2b-de-confound statistics §8.4,
> ASM-0920–0927/0950–0957); docs/next/design/MF0.md §8.5 (framework-owned
> content-type cells, ASM-0891); docs/next/lit/RAG.md (P3-LR-RAG);
> poc/gpt56-review/rev-deconfb-20260711/last-message.json (the review this
> revision answers).
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = a programme registry
> verdict/assessment/artifact restated strictly inside its envelope;
> `[LIT-BACKED: lit-review §]` = an external fact verified at primary source by a
> completed Phase-0 lit review, cited through that review; `[STIPULATED: id]` = a
> design choice made here or inherited from a registered stipulation (every
> design CHOICE in this document is STIPULATED, not MEASURED, unless a
> measurement is cited); `[EXTRAPOLATION: id]` = a registered forward
> projection, never a premise; `[PROPOSED-ASM-101x]` = a revision-B amendment
> awaiting coordinator registration.

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
- SCOPE PREMISE (review-mandated): external adjudication breaks the
  MEMBERSHIP-GOLD circularity only. It does NOT remove the item-generation
  circularity (items are rendered from the kernel's own records) or the
  store-addressing circularity (every item pins the record that answers it).
  Every Stage-B verdict therefore retains the **self-authored /
  kernel-covered / oracle-addressed-slice rider** verbatim (§5.2, §6)
  [STIPULATED: PROPOSED-ASM-1017].

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
store lacks". That is decidable by exhaustive enumeration plus trajectory
replay on a CPU, at ~$0 marginal compute (§3). What that decision procedure IS
— an equivalence/regression certificate over a projection of the kernel's own
strings, not a competitive generic-store experiment — is stated precisely in
§3.0 [STIPULATED: PROPOSED-ASM-1010].

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
  **A1** (CPU, ~$0 marginal compute): the aligned-generic-store
  extensional-equivalence CERTIFICATE on the f2b verify-retry mechanism;
  **A2** (CPU, ~$0 marginal compute; engineering effort logged per §8): the
  generic-typed-store + generic-executor PORTABILITY AUDIT of the a5-llm
  engine leg (the conventional-substrate control that assessment names as
  missing); **B** (single small GPU run, ≤ ~3 GPU-h / ≤ ~$25): a cheap
  lexical-retrieval generic baseline (BM25 precursor — NOT RAGC's "strong
  generic RAG baseline", see §2.3) through the IDENTICAL verify-retry
  topology on the SAME externally-adjudicated items, isolating alignment
  itself as the last unshared ingredient. Claim licences, gates and
  does-not-amend clauses per the registered contract
  [STIPULATED: ASM-0960 as amended by PROPOSED-ASM-1014].

Ownership map (no duplication):

| Cell | Factorial owner | DECONF's relation |
|---|---|---|
| A1 aligned generic answer-key store | MF0 §8.5 content-type cell (e) "aligned-non-kernel store" (ASM-0891) | DECONF instantiates the STRUCTURE-MINIMAL member (opaque-string projection, zero authoring); knull-v2 owns the authored-content members (plain/nonce) |
| A2 generic executor | RAGC GR-C (ASM-0924/0954) | DECONF runs the right-sized precursor on the pinned a5-llm slice; the full manifest cell supersedes it when built |
| B generic RAG + matched retry | RAGC GR-A / GR-D (ASM-0920/0924/0955) | DECONF runs right-sized lexical PRECURSORS at the f2b scope, adopting the FRONT/1 §5 parity mechanics (ASM-0853) that apply and choosing its GR-D acceptance signal FROM the frozen ASM-0924/0955 menu (§5.1); superseded by the RAGC manifest cells at any G4/W1 use |

**Gate placement (corrected per review; supersedes rev-A's wording)**
[STIPULATED: PROPOSED-ASM-1014]:

- **A1/A2 are NOT G1.** G1 is specifically the coverage-ceiling Δ_max
  calculation (programme §4 gate ladder; ASM-0817). A1/A2 are **CPU
  attribution DIAGNOSTICS that sit BEFORE the gate ladder**: they qualify the
  interpretation of already-measured results and feed riders/verdict-inputs;
  they occupy no gate rung and unlock none.
- **Stage B is a formal / oracle-addressed G2-class DIAGNOSTIC** on the
  covered slice — never a W1 claim, never a G4 experiment; the RAGC manifest
  owns those uses.
- **NL discipline, stated correctly:** Stage B DOES contain English — the
  templated item questions and the retrieved rendered records are English
  text. Stage B is exempt from the NLB gate **because it is an
  oracle-addressed / formal covered-slice G2 diagnostic** (the evidence class
  of RAGC §8.3, ASM-0814/0808 applied), NOT because "no natural-language input
  exists" — rev-A's wording to that effect was wrong and is withdrawn here
  and at §5.3.
- No cell licenses any competitiveness sentence.

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

Consequence (a determinism statement, not a hypothesis), **stated at its true
scope** [STIPULATED: PROPOSED-ASM-1010, narrowing rev-A's "every future
output" claim per the review]: if a substitute store S′ yields the SAME
check() decision as the kernel store on every reachable (item, admissible
answer, verifier-state) triple, then every output, per-item correctness bit,
endpoint, and verdict of every run of **the pinned harness+checker version,
over the pinned item corpora and closed option-scoring output space, under the
pinned initialization procedure and the content-hashed store version** is
invariant under kernel→S′ substitution. "Future" runs are covered ONLY
insofar as they re-pin those identical hashes; any change to harness, checker,
schema, output space, init procedure, or store version voids the lemma and
requires an A1 re-run (§7.1). The lemma quantifies over the checker, not over
model scale: the only measured model context on this line is the pinned
R-1/SmolLM2-135M revision, and **no extrapolation to the 100M–2B rung range is
licensed by anything in this design**. The deconfound therefore does not need
to re-run any model to decide the runtime channel: it needs to measure
decision concordance over the FULL reachable decision space (closed answer
sets: ≤4 options or yes/no per item) PLUS the logged trajectories and
initialization-order state (§3.1). That is Stage A1.

---

## 2. The generic stores (all derivation, no authoring)

### 2.1 GS-A — the aligned generic answer-key store (Stage A1/B)

- DECISION: GS-A is a **mechanical field projection** of the pinned kernel-v0 /
  molecules-v0 store onto exactly the read-set of `check()`. **Keying and
  schema, pinned exactly (supersedes rev-A's "four-column row")**
  [STIPULATED: ASM-0961 as amended by PROPOSED-ASM-1011]:
  - one row per covered record, **primary key = `urn`** (the checker's
    `_load` key), carrying `{urn, record_path, record_sha256, label,
    canonical_text, claims[]}` where `canonical_text` is `rec["gloss"]`
    stripped, else `render_plain(rec["groundingNote"])` — byte-for-byte the
    pinned KernelVerifier._load rule — and `claims[]` = `segments(canonical_text)`;
  - the **term-lookup map** is keyed by `label.lower()` and built in the SAME
    traversal order as `KernelVerifier.index_labels(items)` over the pinned
    corpus order (the map is load-order dependent: later loads overwrite);
  - **duplicate-label / collision semantics:** the derivation script
    enumerates all lowercased-label collisions in the covered set; if any
    exist, GS-A replicates the checker's later-load-wins overwrite exactly and
    the collision list is a published artifact of the derivation (an empty
    list is asserted, not assumed);
  - every byte is copied verbatim from the kernel's own records; all NSM
    structure (explication trees, primes, vectors, types, provenance frames,
    engine hooks) is DELETED. Derivation is one deterministic seed-free
    script, content-hashed; the row set is coverage-identical and
    alignment-identical to the kernel store by construction (same urn /
    record_path / record_sha256 pins the items already carry).
- Why this is runnable today when knull-v2 is not: GS-A **authors nothing** —
  it contains no new prose, so the maintainer language-quality gate on authored
  control stores (the knull plain-arm ruling) has no object here; the
  quality-gate applies to authored aligned stores (knull-v2's plain arm), not
  to a byte-projection of the kernel's own strings [STIPULATED: ASM-0961; the
  ruling itself is ASM-0700/ASM-0703, untouched].
- What GS-A operationalises — **and what it does NOT** [STIPULATED:
  PROPOSED-ASM-1010]: it operationalises the reviews' phrase "a plain aligned
  answer-key" as the STRUCTURE-MINIMAL member of the MF0 §8.5 content-type
  family (cell (e) direction): same coverage, same alignment, none of the
  kernel's structural semantics. Because its strings ARE the kernel's own
  answer-bearing strings, GS-A is NOT "independently generic content" — it
  cannot and does not test whether generic content reproduces anything; that
  is knull-v2's authored-content question. GS-A tests only whether the
  checker READS anything beyond these strings.

### 2.2 GS-C — the generic typed store + generic executor (Stage A2)

- DECISION: the a5 code-vertical typed world (the no-LLM deterministically
  extracted records the a5 engine runs on) loaded into the RAGC-pinned generic
  deterministic engine — SQLite with a pinned recursive-CTE query library (the
  GR-C default, ASM-0924/0954) — exposing `lookup / neighbors / check` over the
  same typed content; query library version-pinned and content-hashed
  [STIPULATED: ASM-0963, adopting the ASM-0924 executor default].
- **Licence shape, stated up front** [STIPULATED: PROPOSED-ASM-1016]: the
  query semantics live in the BESPOKE, published query library, not in SQLite
  itself. A2 therefore demonstrates (at most) **conventional-runtime
  PORTABILITY** — "the engine's covered behaviour is reproducible by a
  published query library hosted on a stock conventional engine" — and never
  the sentence "SQLite supplies equivalent semantics".

### 2.3 GS-R — the generic lexical tool/RAG store (Stage B)

- DECISION: BM25 over the pinned common text serialisation of the SAME store
  records (the existing deterministic renderer — the serialisation ASM-0922
  pins), index bytes charged, retrieved context injected through the harness's
  existing context_docs path at a pinned retrieved-token cap (§5.1 parity
  note) [STIPULATED: ASM-0964 as amended by PROPOSED-ASM-1012; LIT-BACKED:
  RAG.md §6.2 — BM25 as the robust zero-shot lexical baseline, BEIR,
  arXiv:2104.08663, NeurIPS 2021].
- **Baseline-strength correction (review concern; supersedes rev-A's
  "strong")** [STIPULATED: PROPOSED-ASM-1014]: BM25-only is a **cheap lexical
  PRECURSOR**. RAGC's "strong generic RAG baseline" requires shared
  BM25+dense retrieval and native cells (ASM-0922/0923); no dense embedder is
  added at this right-size. Stage B's licence space therefore NEVER contains
  "no strong generic baseline reproduces it" — only "the pinned lexical
  precursor at matched budget does / does not" (§5.2, §9.4). The RAGC
  manifest owns the strong-baseline cells.

---

## 3. Stage A1 — the extensional-equivalence certificate (~$0 marginal compute, CPU)

### 3.0 What A1 is — and is not (licence narrowed per review)

[STIPULATED: PROPOSED-ASM-1010]

A1 is an **executable EQUIVALENCE / REGRESSION CERTIFICATE** over an exact
projection of kernel-authored answer strings. GS-A copies the exact
answer-bearing kernel strings and runs the same check semantics, so
concordance is *nearly true by construction*. Precisely because of that, A1
is:

- **NOT a falsifiable test of independently-generic content** (that is
  knull-v2's authored-content channel);
- **NOT a competitive generic-store experiment** (that is Stage B and the
  RAGC manifest);
- **NOT G1** (G1 is the coverage-ceiling Δ_max calculation; A1 is a
  pre-ladder CPU attribution diagnostic, §0).

The single narrow proposition A1 decides, and the only one:

> **The pinned F2 runtime checker uses no information beyond the projected
> urn-keyed label/gloss/claim answer key.**

Scope: the pinned harness+checker version, the three pinned item corpora, the
closed option-scoring output space, the pinned initialization procedure, and
the content-hashed store version; measured model context R-1/135M only; **no
extrapolation to the 100M–2B rung range is licensed** (§1).

### 3.1 Procedure

- DECISION: **(a) full decision-grid enumeration** — for each of the three
  pinned item corpora (d-qa 650, d-qa-r 1000, d-qa-t 360; corpus hashes as
  pinned in the f2b-replicate / f2b-transfer records) × every admissible
  answer in the item's closed answer space (each MC option; yes and no for
  claim items) × both verifier variants (true map; the seed-pinned shuffled
  derangement, replayed with the same recorded permutation applied to GS-A
  rows) — compute the decision triple (extract_ok, decidable, consistent)
  under (i) the pinned KernelVerifier over the kernel store and (ii) the same
  checker class over GS-A. Grid size ≤ ~16k decision pairs (2,010 items × ≤4
  answers × 2 variants); pure string ops; minutes on the local box at
  nice -n 10 [STIPULATED: ASM-0962].
- DECISION: **(b) initialization/order-state enumeration** (new in rev-B, per
  review) [STIPULATED: PROPOSED-ASM-1011]: the checker's term-lookup map
  (`_by_label`) is built lazily in item-traversal order and later loads
  overwrite earlier ones — checker state is therefore ORDER-DEPENDENT. A1
  (i) pins the traversal order to the pinned corpus order via
  `index_labels(items)`, (ii) enumerates all lowercased-label collisions in
  the covered set and publishes the list (asserting emptiness rather than
  assuming it), and (iii) runs the grid under BOTH the eager
  (index_labels-first) and lazy (per-item) initialization orders, requiring
  concordance under both.
- DECISION: **(c) logged-trajectory replay** (new in rev-B, per review)
  [STIPULATED: PROPOSED-ASM-1011]: replay every logged (item, attempt,
  answer) trajectory from the pinned f2b-replicate run logs (all arms that
  consulted a verifier, both true and shuffled) through both checkers IN
  SEQUENCE, requiring decision-for-decision concordance including the evolving
  lazy-load state — this catches stateful effects that per-pair grid
  enumeration structurally cannot. The set of replayed trajectories and their
  log hashes are pinned at freeze.

### 3.2 Metric and decision rule

- DECISION: the primary statistic is **C_dec = concordant decision triples /
  total (grid ∪ replay ∪ init-order) evaluations** — an exhaustive COUNT over
  the full reachable decision space, so it carries no sampling error and no
  confidence interval; the pre-registered reading [STIPULATED: ASM-0962 as
  amended by PROPOSED-ASM-1010]:
  - **C_dec = 1.0 ⇒ verdict-input KERNEL-RUNTIME-STRUCTURE-INERT (the
    certificate half).** What this PROVES: the kernel's structural fields
    (explication trees, primes, vectors, types, provenance frames, engine
    hooks) are **runtime-inert under the pinned topology** — the checker reads
    nothing beyond the urn-keyed answer-key projection. By §1 (at §1's stated
    scope) the projection reproduces every pinned-scope F2-line endpoint
    VERBATIM: the reproduction statistic is `R_repro = lift(GS-A) /
    lift(kernel) ≡ 1.0` identically over the pinned corpora/hashes, including
    f2b-transfer stage-2's external-gold endpoints IF stage 2 runs at the same
    pins. What this does **NOT** prove: that kernel-authored content is
    generic (GS-A's strings ARE kernel-authored — the content channel is
    knull-v2's), or anything about other topologies, other harness versions,
    or the 100M–2B rung range. The kernel-SPECIFIC **runtime** claim on the
    F2 line is dead at this scope, at zero marginal model spend.
  - **C_dec < 1.0 ⇒ TRIAGE FIRST; semantic credit only after exclusion.** A
    discordance does NOT by itself establish a "kernel-semantics runtime
    channel" — the base rates favour mundane causes. Every discordant triple
    is emitted and triaged through the pinned ladder, in order, each cause
    excluded by a named test before the next is considered
    [STIPULATED: PROPOSED-ASM-1010]:
    1. **projection/adapter bug** (GS-A derivation or the A1 harness shim) —
       test: independent re-derivation + field-level byte diff on the
       discordant rows;
    2. **incomplete read-set** (check() reads a field the projection dropped)
       — test: instrumented checker traces field accesses on the discordant
       pairs;
    3. **initialization-order difference** (label-map overwrite divergence) —
       test: §3.1(b) eager/lazy comparison localises it;
    4. **schema mismatch** (normalisation, segmentation, or key drift) —
       test: norm_text/segments round-trip comparison on the discordant rows.
    Only a residual surviving ALL four exclusions may be labelled
    **KERNEL-RUNTIME-CHANNEL-CANDIDATE** — a candidate, not a finding; it is
    classified by check-path (def-match / term-match / claim /
    shuffled-composition), any candidate lying on a trajectory reachable by a
    logged run raises a flag on the f2b-replicate interpretation (flag only —
    the frozen verdict is untouched), and Stage B adds the kernel-verify arm
    back (§5.1's conditional arm) so the channel is priced end-to-end.
- Falsifiability, stated honestly: C_dec = 1.0 is the EXPECTED outcome — the
  strip is a projection onto check()'s read-set, and the knull M-V map already
  measured the vector/AST fields inert (3456/3456) [MEASURED:
  registry/experiments/knull.json map M-V]. The residual falsification room is
  real but narrow: the term-for-definition path (`shown_definition`), the
  claim-polarity membership path, the shuffled-map composition, the
  order-dependent label map, and any unnoticed engine consultation inside the
  checker would each surface as discordance. The registered expectation is
  EXTRAPOLATION ASM-0966 (non-load-bearing, resolved by the run itself); the
  VALUE of the stage does not depend on surprise — see §3.3.

### 3.3 Why this is worth registering even if the outcome is expected

The assessment's circularity reading is currently an ANALYTIC argument attached
to a does_not_license note; programme discipline treats analytic readings and
measured facts differently, and two external reviews have now demanded this
deconfound be EXECUTED rather than argued (round1-steering item 5; the
GPT-5.6 subjective analysis: "the cheap aligned-store control should not
wait"). Stage A1 converts "a generic aligned answer-key WOULD reproduce it"
into "the answer-key projection DOES reproduce it, bit-for-bit, measured over
the exhaustive decision space, the logged trajectories, and both
initialization orders" — a registered, citable, audit-checkable CERTIFICATE
that (a) every pinned-scope F2-line claim must carry (§7), (b) re-scopes the
headline language mechanically (§6), and (c) does so without spending the GPU
budget, the human-annotation queue, or the knull quality-gate path that block
every other deconfound. The review-gate concurs on exactly this point ("the
core A1 result is sound, cheap, and worth running… sound to implement and run
A1 immediately once its licence is narrowed") [STIPULATED: ASM-0962;
PROPOSED-ASM-1010].

---

## 4. Stage A2 — the generic-executor portability audit of the a5-llm engine leg (~$0 marginal compute, CPU; engineering effort logged)

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
- DECISION: **conformance-first decision rule (rev-B, per review — supersedes
  rev-A's symmetric 0.99 branch)** [STIPULATED: PROPOSED-ASM-1016]:
  - **Precondition for ANY engine-side reading:** the query library ships with
    a published **grammar-conformance suite** — every production of the
    kot-query-code/1 grammar covered by at least one passing conformance test
    against the grammar spec — and the suite must PASS before either branch
    below is read. Full library source + suite are published with the readout
    (the anti-weak-control requirement, mirroring ASM-0922).
  - **A_exec ≥ 0.99 (conformance suite passed)** ⇒ verdict-input
    ENGINE-GENERIC-AT-SCOPE: the a5-llm PASS's licensed sentence is confirmed
    AS its ceiling ("a deterministic engine over its own extracted typed
    records…"), now with the conventional-substrate arm measured rather than
    argued. Licence shape per §2.2: this demonstrates conventional-runtime
    PORTABILITY of the covered behaviour — it never licenses "SQLite supplies
    equivalent semantics" (the semantics live in the published library).
  - **A_exec < 0.99** ⇒ the verdict is **LIBRARY-INCOMPLETE by default**: an
    under-built query library fakes engine-distinctiveness, so every
    non-reproduced class is first checked against the grammar spec and the
    conformance suite is extended until the class is either (i) reproduced
    (implementation datum, no engine claim) or (ii) shown to require semantics
    OUTSIDE the grammar-conformant library's expressible space. Only class
    (ii) residuals — enumerated, classified, published — may be labelled
    **ENGINE-DISTINCTIVE-RESIDUAL-CANDIDATE** (the first candidate
    engine-specific runtime datum in the registry, worth its own follow-up
    bead). No headline either way.
- Effort accounting (rev-B, per review): rev-A's "roughly a day of
  implementation" is withdrawn as unsupported; the library + conformance-suite
  implementation effort is LOGGED (person-hours / agent-sessions) and reported
  on the stage's lifecycle ledger row (§8) — A2 is compute-cheap, not
  cost-free [STIPULATED: PROPOSED-ASM-1015].

---

## 5. Stage B — the generic lexical baseline through the identical topology, on external gold (GPU, right-sized, G2-class diagnostic)

Stage A1 settles what the ALIGNED answer-key projection does (everything, at
its pinned scope). The live question it cannot settle: is the ALIGNMENT itself
the load-bearing ingredient, or would a generic lexical-retrieval baseline —
same snapshot, same budgets, NO item-aligned key — reproduce the lift too?
f2b-replicate never ran a generic-RAG arm [MEASURED:
registry/experiments/f2b-replicate.json dropped_arms — RAG dropped at
right-size; the F2 confirmatory readings stand at F2's scope], and both
reviews name that the missing first-class rival.

### 5.1 Arms (all at rung R1 = the pinned SmolLM2-135M revision; 250-item d-qa-t eval prefix; 3 seeds; k = 4)

| Arm | Definition | Cell lineage |
|---|---|---|
| R1-alone | attempt-0 only, no store, no retrieval | the shared floor |
| GS-A-verify-retry | the §2.1 generic store behind the UNCHANGED verify-retry loop | MF0 cell-(e) structure-minimal member; equals the kernel arm bit-for-bit iff A1 C_dec = 1.0 on d-qa-t |
| GR-A-lite (RAG-alone) | BM25 top-j rendered records injected via context_docs, attempt-0 | RAGC GR-A lexical precursor |
| GR-D-lite (RAG + generic retry) | GR-A-lite wrapped in the SAME loop shape — same k, same resample rule, same abstain-on-exhaustion — with acceptance = the §5.1.1 self-consistency signal (RAGC menu item (i)); retrieval per the §5.1.2 non-oracular contract | RAGC GR-D lexical precursor |
| kernel-verify-retry (CONDITIONAL) | added back ONLY if A1 found any reachable post-triage discordance on d-qa-t; otherwise NOT run — the GS-A arm carries both readings under measured identity | fail-closed conditional |

#### 5.1.1 The GR-D-lite acceptance signal (rev-B — replaces rev-A's gloss-self-check, which is WITHDRAWN)

[STIPULATED: PROPOSED-ASM-1012]

- **Withdrawal + why:** rev-A specified "the harness's existing gloss-self-check
  over the retrieved text". The review found this doubly invalid: (i) the
  existing implementation (`run_self_verify_retry`, poc/f2b/runner/
  f2b_runner.py — `gloss = gloss_by_urn.get(it["urn"])`) selects the
  **item-aligned gloss via the item URN** and reuses it unchanged — a direct
  oracle leak that smuggles the aligned record back into the generic arm; and
  (ii) "gloss self-check over retrieved text" is **not in RAGC's frozen GR-D
  acceptance-signal menu** (ASM-0924 menu / ASM-0955 discipline: (i)
  self-consistency at a pinned threshold; (ii) a disciplined small learned
  outcome verifier; (iii) tool-execution success). Both defects are cured by
  withdrawing the signal entirely, not by patching it.
- **Chosen signal — menu item (i), self-consistency (SA-class, FRONT/1 §4.2
  semantics); plain adoption of the frozen menu, NO amendment to ASM-0924/0955
  needed or claimed:** at each retry attempt, after the candidate answer is
  produced, draw **m = 3** additional independent samples of the SAME item
  with the SAME retrieved context (seeds via the existing det_u scheme
  extended over (arm, item id, seed, attempt, probe_index) — pinned at
  freeze); **accept iff ≥ 2 of the 3 probes agree with the candidate answer**
  (pinned threshold 2/3; exactly ONE signal per instantiation, no sweeps, per
  ASM-0924). Reject ⇒ resample per the shared loop shape;
  abstain-on-exhaustion identical to the other retry arms.
- **Why not menu items (ii)/(iii), disclosed:** (iii) execution success has no
  object here — MC/yes-no items expose no executable surface at this
  vertical; (ii) a learned verifier is excluded at this right-size (its
  ASM-0955 training/split/calibration discipline plus training compute
  exceeds the diagnostic's scope) — the RAGC manifest owns both cells.
- **Acceptance prompt + parser, concrete for both item types:** there is no
  free-text parsing anywhere — the answer space is closed and every probe is
  scored by the harness's existing constrained option-scoring: MC items score
  the pinned option keys, yes/no claim items score {yes, no}; "agreement" is
  exact key equality. The probe prompt is the arm's own answer prompt
  (identical frames + item + retrieved context), NOT a new judging template —
  self-consistency is agreement among answers, not a graded critique.
- **Calibration + cost reporting:** per-arm co-reported at readout —
  acceptance rate, abstention rate, attempt-count distribution, per-attempt
  agreement histogram (0/3…3/3); an accept-everything or reject-everything
  signal must be visible (ASM-0955's co-report rule, adopted). Every probe
  generation is charged to the arm's ledger row (tokens + FLOPs + latency):
  the m probes per accept-test are the arm's verifier-cost analogue and enter
  the §8 lifecycle table; worst case ≤ 5 attempts × (1 + 3) = 20 generations
  per item.

#### 5.1.2 The retrieval contract (rev-B — non-oracular by construction)

[STIPULATED: PROPOSED-ASM-1012]

- **Query construction:** the BM25 query is derived SOLELY from model-visible
  question text — for MC items, the rendered question string plus the option
  texts exactly as they appear in the prompt (pinned concatenation order);
  for yes/no claim items, the rendered question string plus the claim text.
  The query function NEVER reads `urn`, `record_path`, `record_sha256`, the
  membership answer or any gold field, the item `id`, the `type` tag, or any
  hidden item metadata. The query-construction function is published and
  hash-pinned, and the runner asserts a **leak check** at run time: the query
  string must be reconstructible from the prompt-visible bytes of the item
  alone (fail closed, ERR_QUERY_LEAK).
- **Zero / one / multiple retrieved records:** score all indexed rendered
  records; take top-j by BM25 score with j floating to fill the pinned
  retrieved-token cap; ties broken by pinned lexicographic document-id order.
  Zero positive-score hits ⇒ the arm proceeds with EMPTY context (no
  fallback, no re-query), and the zero-hit count is a mandatory readout
  disclosure. One hit ⇒ that record alone. Retrieval hit@j against the item's
  pinned record is co-reported for the RAG arms (diagnostic only — the pinned
  record identity is used in SCORING the diagnostic, never in constructing
  the query or context).
- **Token-cap parity, worded correctly (review item):** the pinned
  retrieved-token cap is the same ALLOWED EVIDENCE BUDGET wherever evidence
  applies — it binds the retrieval arms (GR-A-lite, GR-D-lite); the
  R1-alone floor and the answer-key-verifier arms (GS-A, conditional kernel)
  retrieve zero tokens BY DESIGN and are not "capped at zero" by parity
  failure.

- DECISION: scoring — every endpoint on the pinned blind external-adjudication
  gold (the d-adj-t labels stage 1 just produced), item-for-item the same
  250-item externally-labelled eval prefix, seeds, decoding, prompt frames, and
  token discipline as the frozen f2b-transfer stage-2 design, so the two
  experiments' cells are diagnostically comparable (comparability is a labelled
  DIAGNOSTIC, never verdict-bearing across records); DECONF-B consumes NO
  logged cell of any frozen record — every arm is a fresh run under this
  design's own (future) prereg [STIPULATED: ASM-0964].
- DECISION: parity mechanics, adopted right-sized from the registered rules
  rather than re-invented: one evidence budget per §5.1.2 (ASM-0923's
  token-not-object matching); generator checkpoint / decoding / stop
  discipline / abstention semantics identical across arms with only the
  evidence slot varying (ASM-0924); BM25 index bytes and build compute
  reported on the arm's ledger row (ASM-0853 Rule 5 / ASM-0925 shape).
  Deviations from the full RAGC inventory (no dense cell, no PS/RD
  perturbation cells, no GR-B/GR-C arm here) are DISCLOSED right-sizing, and
  every such cell remains owned by the RAGC manifest for any later G4 use
  [STIPULATED: ASM-0964].

### 5.2 Endpoints, statistics, decision rules (rev-B — RAGC §8.4 machinery adopted; the point-ratio rule is WITHDRAWN)

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
- DECISION: **primary contrast** — the ABSOLUTE PAIRED difference (RAGC §8.4's
  ratified shape, right-sized to this instantiation; the rev-A point-ratio
  rule `recovery_RAG ≥ 0.70` is WITHDRAWN — a noisy point estimate feeds no
  attribution-collapse kill) [STIPULATED: PROPOSED-ASM-1013]:

  **Δ_align = acc_ext(GS-A-verify-retry) − acc_ext(GR-D-lite)**, paired
  item-level on the shared 250-item × 3-seed grid, programme §2.5 machinery
  (paired BCa bootstrap B = 10,000, PRNG seed pinned at freeze), with the
  pre-registered branches:
  - **COLLAPSE-INPUT (TOST equivalence):** |Δ_align| within δ_eq = 0.05
    absolute — 90% CI entirely inside the band ⇒
    ATTRIBUTION-COLLAPSE-AT-SCOPE: the lexical-precursor generic loop
    reproduces the aligned-key arm within the equivalence margin WITHOUT the
    aligned key; this is the measured input to the K-P3v2(4)
    attribution-collapse kill at this scope (and at this scope only — the
    programme-level kill still requires the RAGC manifest cells).
  - **ALIGNMENT-SPECIFIC (superiority):** LCB95(Δ_align) > δ_sup = 0.05 ⇒ the
    lift requires the item-aligned deterministic acceptance; combined with A1
    (the answer-key projection is checker-sufficient), the licensed sentence
    becomes exactly: *verify-retry against an item-aligned deterministic
    answer key lifts a 135M host on this self-authored kernel-covered
    oracle-addressed slice; the kernel is one way to AUTHOR such a key; no
    kernel-specific runtime contribution is measured* — routing all remaining
    kernel value to the authoring/economics legs (knull-v2 content, A-F0 mint
    cost).
  - **Neither:** INCONCLUSIVE-UNDERPOWERED, disclosed; no attribution
    sentence in either direction.
- DECISION: **power target** — n is sized by the P3-D-POWER machinery to
  ≥ 0.90 power for a true Δ_align = 0.10 under the paired analysis and the
  realised FWER family; if the 250-item d-adj-t prefix cannot support it, the
  externally-adjudicated eval set is enlarged BEFORE freeze (324 endorsed
  labels exist; further stage-1-protocol adjudication is the named enlargement
  path) or the experiment does not freeze [STIPULATED: PROPOSED-ASM-1013].
- DECISION: **FWER discipline** — Holm correction over the named contrast
  family, pre-registered at freeze: {primary Δ_align; bridge lift; GR-D-lite −
  GR-A-lite (loop pricing, the ASM-0926 contrast right-sized); GS-A-verify-
  retry − GR-A-lite}. Secondary contrasts are reported, never headlined
  [STIPULATED: PROPOSED-ASM-1013].
- DECISION: the ratio `recovery_RAG = lift_ext(GR-D-lite) /
  lift_ext(GS-A-verify-retry)` is DEMOTED to a descriptive diagnostic — it is
  statistically unstable near the bridge floor and is never verdict-bearing;
  it is reported with both lifts and no threshold [STIPULATED:
  PROPOSED-ASM-1013].
- DECISION: reporting requirements — full contrast vector (never the headline
  alone), retrieval hit@j + zero-hit count for the RAG arms, acceptance/
  abstention calibration per §5.1.1, per-type breakdown descriptive-only,
  every verdict sentence naming the arm that licenses it (the ASM-0926
  discipline, right-sized), and **every Stage-B verdict sentence carrying the
  §0 rider verbatim**: *self-authored items, kernel-covered slice,
  oracle-addressed store; external adjudication removes membership-gold
  circularity, not item-generation or store-addressing circularity*
  [STIPULATED: ASM-0964; PROPOSED-ASM-1017].

### 5.3 What Stage B deliberately does not measure

No R3/1.7B arm (the efficiency non-inferiority against R3 on external gold is
f2b-transfer's frozen endpoint, not re-litigated here); no PRM arm (HC3 closed
at its size class in f2b-replicate); no scaling reading (R-1/135M only — no
extrapolation to the 100M–2B rung range, §1); no coverage claim (all items are
kernel-covered by construction; the mandatory disclosure rides every readout:
kernel-expressibility coverage 0.3542 at rung molecules-v0, measured by m0b on
one incomplete kernel-v0 instance, NOT general coverage). **NL discipline,
corrected wording (supersedes rev-A's "no NL input anywhere")**: Stage B DOES
contain English — the templated item questions and retrieved rendered records
are English text; Stage B is exempt from the NLB gate because it is an
oracle-addressed / formal covered-slice **G2 diagnostic** (RAGC §8.3 evidence
class; ASM-0814/0808 applied), not because natural language is absent. The NL
wall itself (free NL input) is l3a-parse/a5-nl territory and untouched
[STIPULATED: ASM-0964 as amended by PROPOSED-ASM-1014].

---

## 6. Verdict semantics for the whole experiment (equal prominence, pre-registered)

- DECISION: DECONF/1's verdict object carries THREE independent readings, one
  per stage, each with its licensed sentence and its kill wiring; no stage's
  outcome is promoted into another's scope; **every Stage-B row additionally
  carries the §0 self-authored/kernel-covered/oracle-addressed rider verbatim**
  [STIPULATED: ASM-0965 as amended by PROPOSED-ASM-1013/1014/1016/1017]:

| Stage outcome | Verdict input | Licensed consequence (mandatory narration) |
|---|---|---|
| A1 C_dec = 1.0 | KERNEL-RUNTIME-STRUCTURE-INERT | every pinned-scope F2-line claim henceforth carries the invariance lemma at §1's stated scope: "the store's runtime role is an aligned deterministic answer key; all F2-line endpoints at the pinned harness/checker/output-space/init/store hashes are invariant under replacement of the kernel store by its urn-keyed answer-key projection"; headline language re-scopes to "aligned deterministic answer-key + retry" pending knull-v2 on the content channel; kernel-authored content is NOT thereby shown generic |
| A1 C_dec < 1.0, cause excluded by §3.2 triage (bug/read-set/init/schema) | A1-IMPLEMENTATION-DIVERGENCE | fix, re-derive, re-run A1; no semantic sentence of any kind |
| A1 C_dec < 1.0, residual survives all four exclusions | KERNEL-RUNTIME-CHANNEL-CANDIDATE | candidate only; discordance classes published; f2b-line interpretation flagged where reachable; Stage B runs the conditional kernel arm; follow-up bead to confirm or kill the candidate |
| A2 A_exec ≥ 0.99 (conformance suite passed) | ENGINE-GENERIC-AT-SCOPE | the a5-llm does_not_license ceiling is measured, not argued; reading = conventional-runtime PORTABILITY via the published library — never "SQLite supplies equivalent semantics"; a5-llm narration unchanged (it already claims no more) but now closed against the missing-control objection |
| A2 A_exec < 0.99, class not shown grammar-external | LIBRARY-INCOMPLETE | implementation datum; conformance suite extended; no engine claim |
| A2 A_exec < 0.99, residual class proven grammar-external | ENGINE-DISTINCTIVE-RESIDUAL-CANDIDATE | the residual class is the first CANDIDATE engine-specific runtime datum; follow-up design bead recommended; no headline |
| B TOST: \|Δ_align\| ≤ 0.05 (90% CI in band) | ATTRIBUTION-COLLAPSE-AT-SCOPE (+ rider) | K-P3v2(4) input at this scope; F2-line survives only as generic lexical retrieval + self-consistency retry at matched budget; programme-level kill still needs RAGC manifest cells |
| B LCB95(Δ_align) > 0.05 | ALIGNMENT-SPECIFIC (+ rider) | the deconfound's constructive outcome: value = the aligned key; kernel = one authoring route; runtime distinctiveness: none measured (from A1) |
| B neither branch | INCONCLUSIVE-UNDERPOWERED (+ rider) | disclosed; no attribution sentence either way |
| B bridge/instrument gate failure | INSTRUMENT-INVALID-at-B | nothing attributed; A1/A2 stand; inconsistency with any landed f2b-transfer stage-2 read is flagged for investigation |

- DECISION: the deflationary outcomes get EQUAL prominence with any positive —
  the knull discipline verbatim; and the rescue paths for kernel-specific value
  are named IN the verdict so the outcome cannot be spun: (i) authored-content
  superiority (knull-v2 PASS-CONTENT), (ii) authoring economics (A-F0), (iii)
  any A1/A2 post-triage residual candidate. None of these is licensed by
  DECONF; each is where DECONF's deflationary outcome says to look next
  [STIPULATED: ASM-0965].

---

## 7. How DECONF slots into KOT-FAIR/2 (corrected per review)

1. **The invariance lemma as a standing rider.** On A1 = 1.0, the lemma of §6
   row 1 attaches to every F2-line consuming claim exactly as the coverage
   disclosure does today — a mandatory one-line rider AT §1'S STATED SCOPE
   (pinned harness/checker/output-space/init/store hashes; R-1 context only),
   enforced at readout review, until and unless a later measurement (knull-v2
   content channel, an A1 re-run after any store/checker version change)
   modifies it. Any change to the checker, harness, schema, output space,
   initialization procedure, or store version invalidates the lemma and
   requires an A1 re-run (the audit is minutes of CPU, so this is cheap
   insurance, mirroring the encoder content-hash discipline)
   [STIPULATED: ASM-0965 as amended by PROPOSED-ASM-1010].
2. **Ladder position (corrected).** A1/A2 are **pre-ladder CPU attribution
   diagnostics** — NOT G1 (G1 is the coverage-ceiling Δ_max calculation) and
   not any other gate rung; they occupy no rung and unlock none. Stage B is a
   **formal / oracle-addressed G2-class diagnostic** on the covered slice —
   not W1, not G4 [STIPULATED: PROPOSED-ASM-1014, superseding rev-A's
   "G1-class/census" wording in ASM-0960].
3. **K-P3v2(4) wiring.** Stage B's paired-Δ/TOST contrast is the right-sized
   first instance of the S − GR-D contrast family that ASM-0926/ASM-0957 wire
   into the attribution-collapse kill, now in the RAGC §8.4 ratified
   statistical shape; DECONF feeds that kill AT THIS SCOPE only — the
   programme-level kill still requires the RAGC manifest cells at G4
   [STIPULATED: ASM-0965; PROPOSED-ASM-1013].
4. **Relation to the frozen F2 line.** DECONF amends nothing: f2b-replicate's
   PASS, f2b-transfer's frozen design and stage-1 PASS, knull's frozen record
   and knull-v2's draft all stand byte-identical; DECONF adds the deconfound
   readings their own assessments called for [STIPULATED: ASM-0960].
5. **Relation to the RAGC/FRONT machinery.** DECONF's cells are declared
   right-sized PRECURSORS: they adopt the applicable registered parity rules
   (ASM-0853/0923/0924/0925/0926) and choose the GR-D acceptance signal FROM
   the frozen ASM-0924/0955 menu (§5.1.1 — plain adoption, no amendment)
   without waiting for the manifest infrastructure, per the steering's
   freeze-scaffolding/measure-now directive; when the RAGC manifest lands, its
   cells supersede these for all G4/W1 use and DECONF's readings remain valid
   at their own scope [STIPULATED: ASM-0960; PROPOSED-ASM-1012].

---

## 8. Compute + lifecycle plan (cheap-first, worked; full accounting per review)

Planning estimates, never measurements [STIPULATED: ASM-0964 as amended by
PROPOSED-ASM-1015]. **Lifecycle rule (rev-B): "$0" is never written without
qualification — the honest phrase is "$0 MARGINAL COMPUTE", and every stage
reports the full lifecycle ledger row below at readout.**

**Per-stage lifecycle ledger (mandatory readout columns, all stages):**
model tokens + self-check/probe tokens (in/out, per arm); model FLOPs
(2·n_active·tokens convention, per arm, probes included); total artifact
bytes (store projections, BM25 index, query library + conformance suite,
logs, discordance files); peak RSS per process; latency distribution
(per-query p50/p95 + wall-clock); BM25 index build CPU-seconds; query-library
+ conformance-suite implementation/build effort (logged person-hours /
agent-sessions); store-derivation effort (script authoring + run time).

- **A1: ~$0 marginal compute.** ≤ ~16k grid decision-pairs + logged-trajectory
  replay + dual-init-order pass, pure string ops + one store-projection
  script; local box, nice -n 10, minutes to hours including harness plumbing;
  no model, no GPU, no API. Lifecycle costs: derivation-script effort +
  artifact bytes (GS-A projection + discordance/collision files), logged.
  Runnable the day the (post-review) prereg freezes.
- **A2: ~$0 marginal compute; the cost is engineering, logged not waved.**
  SQLite + a pinned CTE query library over the a5 typed world; 977 queries
  execute in seconds; the query library + grammar-conformance suite are
  published, reviewable artifacts (the anti-weak-control requirement) and
  their implementation effort is a ledger line (rev-A's "roughly a day" is
  withdrawn as unsupported — §4).
- **B: ≤ ~3 GPU-h, ≤ ~$25, Modal, one container.** ~250 items × 3 seeds ×
  worst-case (1 + 5 + 1 + 20) generations/item across the four arms at
  135M-class option-scoring throughput (GR-D-lite's ≤20 = ≤5 attempts × (1
  answer + 3 self-consistency probes), all charged); BM25 build is CPU
  (build seconds + index bytes on the ledger). Co-schedulable with the
  f2b-transfer stage-2 campaign (same image, same corpus assets) without
  touching that record's run; inside the standing free-pool/Tier-0
  authorization, with prereg-freeze + runner-role separation (designer never
  runs/grades) exactly as knull pins it. Spend stop: exhaustion before the
  primary readout = scientific stop + salvage per house rules, no retry.
- Sequencing: A1 → (A2 ∥ B). A1 first because its outcome decides B's
  conditional kernel arm and licenses B's arm-sharing economy; A2 is
  independent and can fill CPU time while B waits for its freeze.

---

## 9. Honest limits of this design

1. **A1 is a certificate, not a discovery instrument.** It decides one narrow
   proposition (§3.0) about the pinned checker's read-set; concordance is
   nearly true by construction because GS-A copies the kernel's own
   answer-bearing strings. A C_dec = 1.0 outcome says nothing about
   authored-content value (knull-v2's question), authoring economics (A-F0),
   consumption channels (A-E2), any future architecture whose coupling is not
   answer→check→resample, or any model scale beyond the pinned R-1 context.
   The lemma it licenses is scoped to the pinned
   harness/checker/output-space/init/store hashes.
2. **A1's expected outcome is known-direction.** Registered as EXTRAPOLATION
   ASM-0966 (non-load-bearing); the stage's value is conversion of an analytic
   claim into a measured, riding, re-checkable certificate — §3.3 — not
   surprise. Discordance, if any, is presumed implementation-caused until the
   §3.2 triage ladder excludes all four mundane causes.
3. **A2's generic executor can be under-built, and its licence is
   portability.** The counters are the mandatory grammar-conformance suite
   (pass required before ANY engine-side reading), publication of the full
   query library, LIBRARY-INCOMPLETE as the default sub-0.99 verdict, and the
   §2.2 portability-not-SQLite-semantics licence cap; residuals are
   classified candidates, never headlines.
4. **B is one lexical retriever, one menu acceptance signal, one vertical,
   250 items, R-1 only.** "No generic signal reproduces it" and "no strong
   generic baseline reproduces it" are BOTH outside B's licence space — only
   "BM25 lexical retrieval + pinned self-consistency acceptance at matched
   budget does / does not"; the RAGC menu and manifest own every wider claim.
   B's external-gold scoring inherits the d-adj-t protocol's own limits
   (single human judge-1 + fallback judge sourcing as disclosed in the
   f2b-transfer record) — and external adjudication removes membership-gold
   circularity only: the self-authored/kernel-covered/oracle-addressed rider
   stays on every B verdict (§0, §5.2).
5. **Cross-record comparability is diagnostic only.** Bit-level agreement
   between DECONF-B's GS-A arm and f2b-transfer stage-2's kernel arm is
   expected under A1 identity but can be broken by cross-container numeric
   nondeterminism; it is read as a diagnostic, never as an endpoint.
6. **Thresholds (0.99 A_exec; δ_eq = δ_sup = 0.05; +0.05 bridge; 2/3
   self-consistency; m = 3; token caps) are stipulated planning values**,
   maintainer-adjustable at prereg freeze; δ_eq/δ_sup deliberately reuse RAGC
   §8.4's ratified margins so the programme's de-confound statistics stay
   commensurable (the rev-A 0.70/0.30 ratio convention is retired with the
   ratio rule itself).

---

## 10. Assumption entries

### 10.1 Registered (rev-A block, unchanged ids; amended clauses noted)

Fresh append-only block ASM-0960–0979 (this bead); entries 0967–0979 remain
free.

| Registered id | Scope | Rev-B status |
|---|---|---|
| **ASM-0960** | DECONF contract: two-channel decomposition, stage inventory A1/A2/B, claim licences, does-not-amend clauses, precursor/supersession relations (§0, §7) | gate-placement clause superseded by PROPOSED-ASM-1014 |
| **ASM-0961** | GS-A derivation rule: mechanical projection onto the check() read-set; zero authored prose; deterministic pinned script + content hash (§2.1) | keying/collision/init clauses tightened by PROPOSED-ASM-1011 |
| **ASM-0962** | Stage A1 semantics: exhaustive decision-grid enumeration, C_dec counting statistic (no CI), value-independent-of-surprise rationale (§3) | licence + discordance semantics superseded by PROPOSED-ASM-1010; procedure extended by PROPOSED-ASM-1011 |
| **ASM-0963** | Stage A2: GS-C = a5 typed world in pinned SQLite + published CTE query library; endpoints A_exec + acc_generic on the pinned 977-query slice (§4) | decision-rule branch superseded by PROPOSED-ASM-1016 |
| **ASM-0964** | Stage B: arm set, external-gold scoring on the pinned d-adj-t labels, fresh-runs rule, right-sized parity adoption, instrument + bridge gates, reporting requirements, compute caps (§5, §8) | acceptance signal superseded by PROPOSED-ASM-1012; statistics superseded by PROPOSED-ASM-1013; NL wording by PROPOSED-ASM-1014; accounting by PROPOSED-ASM-1015 |
| **ASM-0965** | Verdict + wiring: three independent stage readings, equal-prominence deflationary outcomes, invariance-lemma rider rule, K-P3v2(4) mapping (§6, §7) | verdict rows updated per PROPOSED-ASM-1010/1013/1016/1017 |
| **ASM-0966** | EXTRAPOLATION (non-load-bearing): expected A1 outcome C_dec = 1.0; resolved by the stage-A1 run itself | unchanged |

### 10.2 PROPOSED-ASM (rev-B; disjoint block ASM-1010–1019; the coordinator registers these at commit — this document edits no registry file; 1018–1019 remain free)

| Proposed id | Scope |
|---|---|
| **PROPOSED-ASM-1010** | A1 licence narrowing: A1 is an executable equivalence/regression certificate over an exact projection of kernel-authored answer strings — not a test of independently-generic content, not G1; C_dec = 1.0 reads as structural-field runtime-inertness at the pinned scope (never "kernel content is generic"); C_dec < 1.0 triggers the four-step implementation-cause triage ladder (projection bug / incomplete read-set / init-order / schema) before any semantic-candidate label; the §1 invariance lemma is scoped to pinned harness/checker/output-space/init/store hashes; R-1/135M context only, no extrapolation to 100M–2B (§1, §3.0, §3.2). Amends ASM-0962 |
| **PROPOSED-ASM-1011** | GS-A keying + state contract: primary key = urn with record_path/record_sha256 pins; canonical_text/claims per the pinned _load rule; lowercased-label map built in the pinned index_labels traversal order with later-load-wins replicated and all collisions enumerated + published; A1 procedure extended with dual-initialization-order enumeration and logged-trajectory replay (pinned log hashes) (§2.1, §3.1). Amends ASM-0961/0962 |
| **PROPOSED-ASM-1012** | GR-D-lite acceptance + retrieval contract: rev-A's gloss-self-check WITHDRAWN (oracle leak via it["urn"]; not in the frozen menu); acceptance = RAGC menu item (i) self-consistency, m = 3 probes, ≥2/3 agreement, closed-space option-scoring parser, one signal, no sweeps, calibration + probe-cost co-reported (plain adoption of ASM-0924/0955, no amendment); retrieval query from model-visible question text only with run-time leak check (ERR_QUERY_LEAK), pinned zero/one/multiple-hit behaviour, evidence-budget parity worded as allowed-budget-where-applicable (§5.1.1, §5.1.2). Amends ASM-0964 |
| **PROPOSED-ASM-1013** | Stage-B statistics: primary = absolute paired Δ_align with RAGC §8.4 machinery — TOST equivalence at δ_eq = 0.05 (collapse input), LCB95 > δ_sup = 0.05 (alignment-specific), else inconclusive; power ≥ 0.90 at Δ = 0.10 sized before freeze (enlarge the adjudicated set or do not freeze); Holm FWER over the named contrast family; the recovery_RAG ratio demoted to a non-verdict-bearing descriptive diagnostic (§5.2). Amends ASM-0964/0965; replaces the 0.70/0.30 point-ratio rule |
| **PROPOSED-ASM-1014** | KOT-FAIR slotting + NL wording correction: A1/A2 = pre-ladder CPU attribution diagnostics (not G1); Stage B = formal/oracle-addressed covered-slice G2 diagnostic (not W1/G4); BM25-only = cheap lexical precursor, never "strong generic RAG baseline"; Stage B contains English and is NLB-exempt by evidence class, not by NL absence (§0, §2.3, §5.3, §7.2). Amends ASM-0960/0964/0965 |
| **PROPOSED-ASM-1015** | Lifecycle-accounting contract: "$0" always qualified as "$0 marginal compute"; mandatory per-stage ledger — model/probe tokens + FLOPs, artifact bytes, peak RSS, latency distribution, BM25 build CPU, query-library + conformance-suite implementation effort (logged), store-derivation effort (§8). Amends ASM-0964 |
| **PROPOSED-ASM-1016** | A2 conformance-first rule + portability licence: published grammar-conformance suite must pass before any engine-side reading; A_exec < 0.99 defaults to LIBRARY-INCOMPLETE, with ENGINE-DISTINCTIVE-RESIDUAL-CANDIDATE only for residual classes proven outside the grammar-conformant library's expressible space; A2's positive reading is conventional-runtime portability via the published library, never "SQLite supplies equivalent semantics" (§2.2, §4). Amends ASM-0963 |
| **PROPOSED-ASM-1017** | Stage-B verdict rider: every B verdict sentence carries verbatim "self-authored items, kernel-covered slice, oracle-addressed store; external adjudication removes membership-gold circularity, not item-generation or store-addressing circularity" (§0, §5.2, §6). Amends ASM-0965 |

---

## 11. Beads this design spawns (recommendation — the coordinator creates them; no bd operation is performed by this document)

```
P3-E-DECONF-0   [task, P0]  Freeze + run DECONF/1 stages A1/A2 (CPU, ~$0
    marginal compute) per this rev-B design; emit the two verdict-inputs +
    the invariance-lemma certificate artifacts (discordance file, collision
    list, store projection hash, trajectory-replay log, conformance suite).
    The steering already names this bead; stage A1 is the first
    "cheap decisive kill" of the ratified next-wave list.
P3-E-DECONF-B   [task, P1]  Prereg + freeze + run Stage B (single GPU run,
    <= ~3 GPU-h) once A1 reads out AND the P3-D-POWER sizing confirms the
    Δ_align power target on the available adjudicated items; co-schedule
    with the f2b-transfer stage-2 campaign; runner-role separation per the
    knull pattern.
Dependency edges: P3-E-DECONF-B blocked-by P3-E-DECONF-0 (conditional arm
    rule) + the d-adj-t label pin (already produced by f2b-transfer stage 1)
    + the power sizing (PROPOSED-ASM-1013).
```

---

## Epistemic register (what this design relied on)

- **STIPULATED (registered block ASM-0960…ASM-0966 + proposed block
  PROPOSED-ASM-1010…1017):** every design choice above; none is evidence
  about any store, engine, or thesis. Inherited binding stipulations
  consumed: ASM-0853 (matched-retrieval rules), ASM-0922/0923/0924/0925/0926
  + ASM-0954/0955/0957 (RAGC mechanics incl. the frozen GR-D signal menu and
  the §8.4 ratified de-confound statistics, adopted right-sized), ASM-0891
  (MF0 cell ownership), ASM-0700/0703 (the knull plain-arm ruling, untouched),
  ASM-0812/0813/0814 (controls, statistics, oracle labelling), ASM-0817
  (gate ladder incl. G1 = coverage-ceiling).
- **MEASURED (restated strictly inside their envelopes):** f2b-replicate PASS
  +0.1507 / LB +0.1053 / cost 0.103 / shuffled ~0 and its does_not_license
  ceiling; the f2b-transfer stage-1 endorsement A = 0.9784 (LB 0.9606, gates
  valid; artifact poc/f2b-transfer/judge-1-results/stage1-analysis.json,
  results-log append pending); the knull M-V map 3456/3456; a5-llm PASS
  +0.6602 with its no-conventional-substrate ceiling; the harness mechanism
  facts read from poc/f2b/runner/f2b_runner.py at its pin (incl. the
  urn-keyed _load, the order-dependent _by_label map, and
  run_self_verify_retry's gloss_by_urn[it["urn"]] selection — the rev-A
  oracle leak); m0b coverage 0.3542 (corpus-indexed, restated only as the
  mandatory disclosure).
- **LIT-BACKED (through completed Phase-0 reviews):** BM25 as the mandatory
  lexical baseline (BEIR, arXiv:2104.08663, NeurIPS 2021, via RAG.md §6.2);
  the matched-control no-precedent finding and accounting rules consumed via
  RAG.md §3/§6 as already registered in ASM-0853/0920-0927; the
  self-consistency and verifier-discipline menu provenance via RAG.md §5
  as registered in ASM-0955.
- **EXTRAPOLATION:** exactly one, ASM-0966 (expected A1 outcome),
  non-load-bearing, resolved by the run; no premise or decision in this
  document rests on it.

This document changes no frozen object, no verdict, no audit, no ruling, and
no registry file; ASM-0960–0966 were registered with rev-A, and the rev-B
amendments are carried as PROPOSED-ASM-1010–1017 for coordinator registration.
No git, bd, or kb-sync operation is performed.

---

## GPT-5.6 review-gate response (rev-deconfb-20260711)

Point-by-point mapping of every review concern to its disposition in this
revision. Review source: poc/gpt56-review/rev-deconfb-20260711/
last-message.json. No concern is deferred; all are addressed in-body.

| # | Review concern | Disposition in rev-B |
|---|---|---|
| 1 (ranked #2) | A1 overstated: it is an equivalence/regression certificate over an exact projection of kernel-authored strings, not a falsifiable test of independently-generic content; discordance ≠ kernel semantics | §3.0 states the certificate framing and the single narrow proposition A1 decides; §3.2 narrows C_dec = 1.0 to "structural fields runtime-inert under the pinned topology" and explicitly denies the "kernel content is generic" reading; C_dec < 1.0 now enters a mandatory four-cause implementation triage (projection bug / incomplete read-set / init-order / schema mismatch), each excluded by a named test, before any KERNEL-RUNTIME-CHANNEL-CANDIDATE label; §6 verdict table split accordingly [PROPOSED-ASM-1010] |
| 2 | Scope to R-1/135M; no extrapolation to 100M–2B | §1, §3.0, §5.3, §9.1/9.4: lemma scoped to pinned hashes; measured model context R-1/135M only; extrapolation to the rung range explicitly unlicensed [PROPOSED-ASM-1010] |
| 3 (ranked #1) | Stage-B oracle leak: the existing gloss-self-check selects the aligned gloss via it["urn"] (f2b_runner.py run_self_verify_retry) — smuggles the aligned record into GR-D; no non-oracular retrieval/acceptance contract | §5.1.1 WITHDRAWS the gloss-self-check (leak named at source) and replaces it with RAGC menu item (i) self-consistency (m = 3, ≥2/3, pinned); §5.1.2 pins the retrieval query to model-visible question text only (never urn/record_path/gold/id/type/metadata) with a fail-closed run-time leak check, plus pinned zero/one/multiple-hit behaviour; acceptance prompt + parser concrete for MC and yes/no (closed-space option scoring, exact key agreement); calibration (acceptance/abstention/agreement histogram) + probe-generation cost mandatorily co-reported [PROPOSED-ASM-1012] |
| 4 | "Gloss self-check over retrieved text" not in RAGC's frozen GR-D menu — pick a menu signal or register an amendment | Menu item (i) self-consistency chosen — plain adoption of ASM-0924/0955, no amendment needed or claimed; items (ii)/(iii) excluded with stated reasons (§5.1.1) [PROPOSED-ASM-1012] |
| 5 (ranked #3a) | A1/A2 mislabelled G1; B mislabelled; slotting must match KOT-FAIR/2 | §0 + §7.2: A1/A2 = pre-ladder CPU attribution diagnostics (G1 is specifically the coverage-ceiling Δ_max calc); B = formal/oracle-addressed covered-slice G2 diagnostic, never W1/G4 [PROPOSED-ASM-1014] |
| 6 (ranked #3b) | BM25-only is not a "strong generic RAG baseline" under RAGC | §2.3 + §0 + §9.4: renamed cheap lexical PRECURSOR throughout; "strong baseline" sentences removed from the licence space; RAGC manifest owns BM25+dense/native cells [PROPOSED-ASM-1014] |
| 7 | NL-discipline wording wrong at the two flagged spots — Stage B does contain English | §0 gate-placement block and §5.3 rewritten: exemption is by evidence class (oracle-addressed/formal covered-slice G2 diagnostic), not by NL absence; rev-A wording explicitly withdrawn [PROPOSED-ASM-1014] |
| 8 (ranked #3c) | Point-only recovery_RAG ≥ 0.70 collapse rule too weak; conflicts with RAGC §8.4's ratified paired Δ/TOST/LCB/power/FWER | §5.2 replaces it wholesale: primary = absolute paired Δ_align, TOST at δ_eq = 0.05 / LCB95 > δ_sup = 0.05 / inconclusive branch; power ≥ 0.90 at Δ = 0.10 sized pre-freeze (enlarge adjudicated set or do not freeze); Holm FWER over the named family; recovery ratio demoted to non-verdict-bearing descriptive diagnostic [PROPOSED-ASM-1013] |
| 9 | Accounting incomplete; "$0" unqualified | §8 lifecycle ledger: model/probe tokens + FLOPs, artifact bytes, peak RSS, latency distribution, BM25 build CPU, query-library + conformance-suite implementation effort (logged; "roughly a day" withdrawn), store-derivation effort; "$0" always written "$0 marginal compute" [PROPOSED-ASM-1015] |
| 10 | "Four-column row" wrong — checker keys by urn/record_path; pin duplicate-label/collision semantics | §2.1: schema re-pinned with primary key = urn + record_path/record_sha256; lowercased-label map order + later-load-wins replicated; collisions enumerated + published, emptiness asserted not assumed [PROPOSED-ASM-1011] |
| 11 | "Every future output" too broad | §1 + §6 row 1 + §7.1: lemma narrowed to pinned harness/checker version, closed option-scoring output space, pinned init procedure, store version; "future" only under identical re-pins [PROPOSED-ASM-1010] |
| 12 | A1 must enumerate init/order state + replay logged trajectories | §3.1(b) dual-initialization-order enumeration of the order-dependent _by_label map; §3.1(c) decision-for-decision replay of all logged f2b-replicate verifier trajectories with pinned log hashes [PROPOSED-ASM-1011] |
| 13 | A2's <0.99 ⇒ engine-distinctive branch invalid without conformance proof | §4: grammar-conformance suite required to PASS before any engine-side reading; sub-0.99 default verdict LIBRARY-INCOMPLETE; candidate label only for residual classes proven grammar-external [PROPOSED-ASM-1016] |
| 14 | A2 shows conventional-runtime portability, not SQLite-equivalent semantics | §2.2 + §4 + §6: licence capped to portability via the published library; the SQLite-semantics sentence explicitly barred [PROPOSED-ASM-1016] |
| 15 | Token-cap wording: same allowed evidence budget where applicable; alone/answer-key arms retrieve zero | §5.1.2 final bullet: cap = allowed evidence budget binding the retrieval arms; zero-retrieval arms are zero by design, not by parity [PROPOSED-ASM-1012] |
| 16 | External adjudication breaks membership-gold circularity only; every B verdict retains the self-authored/kernel-covered/oracle-addressed rider | §0 scope premise + §5.2 reporting rule + §6 rider column: the rider rides every B verdict verbatim [PROPOSED-ASM-1017] |
| 17 | Recovery ratio statistically awkward near bridge floor | Ratio demoted to descriptive-only, never verdict-bearing (§5.2) [PROPOSED-ASM-1013] |
| 18 | Commit as draft; do not freeze/drive Stage B as written; run A1 once licence narrowed; A2 secondary after conformance + lifecycle contract | Adopted: this document remains [EXP-DESIGN] (nothing frozen); A1 licence narrowed (rows 1–2, 10–12) and first in sequence; Stage B redesigned (rows 3–8, 15–16) and additionally gated on the power sizing before freeze (§11 dependency edges); A2 strengthened per rows 13–14 and its effort logged per row 9 |

**Self-check gate (run before finishing, per the revision instructions):**
(a) A1's claim is narrowed to an equivalence certificate — §3.0/§3.2 ✔;
(b) the Stage-B retrieval query is provably non-oracular (model-visible text
only + fail-closed leak check) — §5.1.2 ✔; (c) statistics use RAGC's paired
Δ/TOST/LCB/power/FWER, not a point ratio — §5.2 ✔; (d) KOT-FAIR slotting
corrected (pre-ladder diagnostics; B = G2 diagnostic; BM25 = lexical
precursor; NLB wording fixed) — §0/§2.3/§5.3/§7 ✔; (e) epistemic tags present
on every claim (STIPULATED/MEASURED/LIT-BACKED/EXTRAPOLATION; design choices
STIPULATED throughout) ✔; (f) new assumptions confined to PROPOSED-ASM-1010…
1017 within the disjoint 1010–1019 block, doc-body only, no registry edit ✔.
