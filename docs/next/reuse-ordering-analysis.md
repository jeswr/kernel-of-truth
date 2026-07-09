# Reuse-maximising ordering of pending work — reconnaissance draft

> **STATUS: SUPERSEDED (2026-07-09).** Fable validated this recon with corrections
> and issued the authoritative plan: `docs/next/resource-optimization-plan.md`
> (bead kernel-of-truth-utq). Material corrections there (§0.1): logs hold per-item
> METRIC ARRAYS, not decodes; e9-full→e9-c is arm-implementation reuse (different
> corpora), not decode reuse, unless designed in at freeze; f2's null arms are not
> config-identical to e9-full's; the §5 honesty question is RULED (conditional yes,
> RC-1..RC-6). Do NOT cite this draft's ordering or reuse calls — cite the plan.
> Kept for the audit trail only.
>
> **Original status: SPECULATIVE / DRAFT / PENDING FABLE VALIDATION.**
> This is an **Opus reconnaissance** pass, not a committed plan. Per
> `docs/next/opus-execution-practices.md` §4, an Opus agent writes no conclusive
> interpretation and makes no strategic decision: **the ordering and every "reuse
> is licensed" call below is Fable's to validate and own.** What is factual here is
> the file-level reconnaissance (dependency edges, shared pins, logged GPU
> outputs); what is speculative is the *proposed sequencing* and the *reuse
> opportunities* inferred from it. Nothing here freezes a record or changes the
> registry. Feeds the P0 resource-optimization plan.
>
> Reconnaissance date: 2026-07-09. Inputs read: `registry/experiments/*.json`,
> `registry/ideas.jsonl`, `registry/status.json`, `registry/frozen-index.json`,
> `results-log/*.jsonl`, `registry/verdicts/*.json`,
> `docs/next/architecture-ladder.md`, `docs/next/research-engine.md`,
> `docs/kernel-design-directives.md`, `docs/next/opus-execution-practices.md`,
> `docs/next/kernel-introduction-schedule.md`, `tools/mint/`, `data/`, `dist/`.

---

## 0. Scope and the two reuse fronts

The maintainer wants pending work **ordered to maximise reuse proactively** —
built into the sequencing, not applied as a retroactive gate — on two fronts:

- **Architecture reuse**: one build (kernel/encoder/model block, corpus, harness,
  engine, adapter) that covers many planned experiments/variants.
- **Cross-experiment GPU-result reuse**: one expensive logged output (arm × seed ×
  decode × checkpoint) consumed by several pending experiments instead of re-run.
  The precedent is **F2 → f2b-replicate**: the gap-closure was a *free re-analysis
  over already-logged data* (`results-log/f2.jsonl`), not a fresh GPU spend.

Two reuse levers already exist in the machinery and this draft should *feed*, not
replace, them:
- the backlog scoring function `score = (D×U×L)/max(C,C_floor)` where **L =
  leverage/reusability (1–3): does the work product serve other candidates?**
  (`docs/next/research-engine.md` §2.7);
- the ladder's own **cheapest-decisive-first** rule and the note that L2c-lite must
  precede L2a/L2b or "re-import the confound" (`architecture-ladder.md` §6.1).

This document makes the reuse structure that those levers price *explicit and
enumerated*.

---

## 1. Dependency map of pending work

### 1.1 Ledger of experiment records (`registry/status.json`, `frozen-index.json`)

FROZEN / done (12): `m0b`(PASS), `f1`(PASS), `f2`(**FAIL**), `f2b-replicate`(PASS),
`a5`(PASS), `l3a`(PASS), `g2`, `g3`, `g6`(INCONCLUSIVE), `g7`(FAIL), `g8`, `g9`.

DRAFT / pending (14): `a-h0`, `family-h0`, `e8-d`, `e8-r`, `e9-c`, `e9-full`,
`f3`, `f4`, `f5`, `f6`, `f7`, `g1`, `g4`, `g5`.

Registered-as-successor, not yet own records (4): `a5-llm`, `a5-nl` (← `a5`);
`l3a-cost`, `l3a-parse` (← `l3a`).

### 1.2 Node classes in the dependency graph

Beyond experiment→experiment edges, `depends_on` carries three non-experiment
classes that dominate the critical path:

- **Infra gates** — `gate-t1` (Tier-1, = `POST-F2-INFRA-OPEN`), `gate-t4`,
  `gate-t5`. `gate-t1` blocks **6** records (`e8-r, e9-full, f3, f4, f6`, and F2
  itself). This is a single **programme-level maintainer/Fable decision**, not
  per-experiment work — but it gates the entire GPU phase.
- **Data-prep corpora** `d-*`. Present in `data/` (built): `d-qa`, `d-qa-r`,
  `d-xif`, `d-ext`, plus `axioms-v0`/`code-axioms-v0`, `math-*` (for `d-ml`).
  **Not yet built** (block their consumers): `d-ax`, `d-axn`, `d-gl`, `d-dom`,
  `d-st`, `d-ts`, `d-cb`, `d-sae`, `d-ir`, `d-ir-n`. Note `d-ax` is referenced by
  **two** records (`g4`, `e9-c`) — the highest-reuse unbuilt corpus.
- **Infra/meta nodes** — `f0-harness` (3 refs; effectively all f-experiments),
  `i-reg`, `i-hyp` (registry/hypothesis scaffolding for `family-h0`/`a-h0`).

### 1.3 Dependency edges (experiment + successor layer)

```
m0b ─────────────► e9-full, f2, f2b, f3, f4        (coverage gate; DONE/PASS)
f0-harness ──────► f1, f2, f2b, (all f-*)           (harness; DONE)
f2 (FAIL) ───────► f2b(done), f3, f7
d-qa,d-xif,d-ext ► e9-full, f2(done), f2b(done)
gate-t1 ─────────► e8-r, e9-full, f3, f4, f6        (POST-F2-INFRA-OPEN)

e9-full ─┬───────► e9-c        (e9-c arms = "ALL e9-full arms" + 1)
         └───────► f7
d-ir,d-ir-n,d-ax ► e9-c
e8-r ────────────► e8-d
d-sae ───────────► e8-r
d-gl ────────────► f3 ────────► f5 ───► (gate-t4)
d-dom ───────────► f4 ─┬──────► g1     (+ d-cb)
                       └──────► f7
d-ts ────────────► f6 ────────► f7 (gate-t5, Tier-5 $10k capstone)
f1 (PASS) ───────► f5
g2 (FROZEN) ─┬───► g4  (+ d-ax,d-axn)
             └───► g5
l3a (PASS) ──────► l3a-cost, l3a-parse   (successors; l3a-cost = Tier-1 GPU)
a5 (PASS) ───────► a5-llm, a5-nl         (successors; a5-llm = GPU)
family-h0 ───────► a-h0                  (terminal disjunction meta-gate)
{e9-full,e9-c,f2,f3,f4,f1/f5,f6} ─► family-h0 (8 fixed members HC1,HC2,HE1..HE6)
```

**Terminal / capstone nodes:** `a-h0` (needs all family-h0 members) and `f7`
(needs f2✓, e9-full, f4, f6) are the two sinks. Everything else feeds them.

**Roots that unblock the most:** `e9-full` (feeds e9-c, f7, family-h0),
`f4` (feeds g1, f7, family-h0), and the infra gate `gate-t1`.

---

## 2. Architecture-reuse map (build one → cover many)

Mined from idea `slots` + `compatibility.requires`/`alternative_to` in
`registry/ideas.jsonl`, the ladder rungs in `docs/next/architecture-ladder.md`, and
the shared basis/mint/corpora/harness on disk.

### 2.1 Shared substrate (already built — reused by *every* experiment)

| Shared block | Where | Reused by |
|---|---|---|
| **65-prime encoder** (construction-B, pin `40e8c8ba…`) | `encoder/`, `idea-construction-b` (MEASURED) | every record pins the same `encoder_hash` |
| **Mint pipeline** (JCS→merkle→content-hash) | `tools/mint/src/` | every corpus in `dist/canonical/*.canonical.jsonl` |
| **kernel-v0 corpus** (one pinned hash) | `data/kernel-v0`, `dist/canonical/kernel-v0.canonical.jsonl` | present in ~all records' `pins.corpus_hashes` |
| **molecules-v0 / lexical-wn31** | `dist/canonical/` | molecules in f2/f3/f4/f5/f6/f7/e8-r/e9/g1/g5; wn31 in f1/f5/g6/g7/m0b |
| **f0-harness + FLOP-meter + extraction-instrument** | `poc/f0`, `poc/f2` | f1/f2/f2b done, reused by f3/f4/f5/f6/f7/e8/e9 |

The single biggest architecture-reuse fact: **the encoder + mint + kernel-v0 +
GPU harness are one-time builds already amortised across the whole programme.** A
new experiment adds a corpus and arms, not a substrate.

### 2.2 Idea-graph hubs (`requires` in-degree — one build unlocks a family)

- **`idea-a2-adapter`** (L0, **MEASURED**, E5 PASS; `seam/adapter` +
  `model/embedding-tokenisation`). Required by `idea-l1b-dense-io`,
  `idea-compositional-rollup-invented-concepts`,
  `idea-crosslingual-phrase-coverage-io-compression` (via `a2-adapter-injection`).
  → **Adapter trained once; content-transfer property reused by L1b, L2c-lite, and
  the in-tokenisation-normalisation ideas.** Ladder cites A2/E5 machinery as the
  hook for both L1b and L2c-lite (`architecture-ladder.md` §3.2, §4.3).
- **`idea-l3a-oracle`** (L3a, **MEASURED** via `l3a` PASS; `seam/rules-engine` +
  `kernel/axiom-layer` + `kernel/world-layer`). Required by `idea-l3b-routed-hybrid`,
  `idea-l3c-engine-in-decode` (transitive), `idea-symbolic-inference-between-layers`,
  `idea-inter-layer-loop-trainingfree`, `idea-vsa-engine-internals`,
  `idea-code-worldlayer-cpg`. **In-degree 6.** → **The engine artefact (kot-axiom
  engine + world-layer index), already built and PASSED at L3a and exercised on
  code by `a5`, is the highest-leverage shared build: it is reused by the entire L3
  family AND four model-internal ideas.** Its own deps `idea-axiom-expressivity` +
  `idea-worldlayer-population` are the corpus/authoring legs (FK-L3-2 route).
- **`idea-inter-layer-loop-trainingfree`** → required by `idea-coconut-engine-loop`
  (L4), `idea-kernel-keyed-steering-dict`.
- Smaller hubs: `idea-vocab-extensions` → `idea-structured-data-parser`;
  `idea-structural-decode-similarity` → `idea-symbolic-inference-between-layers`;
  `idea-polarity-similarity` → `idea-vsa-engine-internals`.

### 2.3 The encoder binding-op slot — mutually-exclusive variants share one bench

`idea-construction-b`, `idea-tpr-exact-shallow`, `idea-wl-compressed-sensing` are
`alternative_to` each other in the **same slot** (`encoder/binding-op/replace`). A
single decode/margin bench (the X0–X4 harness) evaluates all three; testing one
variant reuses the entire evaluation rig for the others. Same pattern for
`similarity-decode` (`idea-polarity-similarity` vs `idea-structural-decode-similarity`).

### 2.4 The cross-cutting φ / σ axis — one sweep fixes three rungs

`idea-l2c-phi-fixedness` (L2c) is `orthogonal_to` `idea-l1b-dense-io`,
`idea-l2a-bottleneck`, `idea-l2b-memory-layer` — i.e. a **cross-cutting dose axis
over all three**. Per `architecture-ladder.md` §6.1, running L2a/L2b at an unswept
φ "re-imports the confound L2c exists to remove." → **L2c-lite produces the φ\*
design points consumed by L2a, L2b, and L1b: one sweep, three rungs' design points
fixed.** And the schedule axis σ (`kernel-introduction-schedule.md` §5, S3) "extends
L2c… NOT a new spend" — **σ×φ shares the L2c-full training run** (S3 is an amendment
to L2c-full, not a separate experiment).

### 2.5 Corpus/oracle sharing across the correctness lane

- **`d-ax` axiom corpus** feeds `g4` **and** `e9-c` **and** the L3a axiom-expressivity
  leg — build once, three consumers.
- **`l3a`/`a5` engine** (PASS) is the oracle both `l3a-cost`/`l3a-parse` and
  `a5-llm`/`a5-nl` successors consume; `idea-code-worldlayer-cpg` (code world-layer,
  L3a) reuses the same engine on the code corpus already staged in
  `data/code-world-v0`, `data/code-axioms-v0`.

---

## 3. GPU-result-reuse map (produce the expensive output once)

### 3.1 What is already logged and reusable (`results-log/`)

The **F2 modal run** (`results-log/f2.jsonl`, 88 records, A10 GPU) is the programme's
one large paid GPU asset. It pins and caches four model checkpoints by exact
revision and logs **per-item** correctness (`metrics.item_correct.*`), which is what
made the f2b re-analysis free:

- `pins_observed.model_revisions`: **SmolLM2-135M** (R1) `@12fd25f7`, **360M** (R2)
  `@a10cc151`, **1.7B** (R3) `@31b70e2e`, **Skywork-o1-PRM-1.5B** (prm) `@98d69606`.
- Arm × rung × seed matrix actually logged:
  - `model-alone` at **R1, R2, R3 × 5 seeds** (the text-only null across the full
    scale ladder — the most broadly reusable output);
  - `kernel-verify-retry` R1×5, R2×5; `gloss-self-verify-retry` R1×5;
    `prm-verifier` R1×5; `self-consistency-flop-matched` R1×5;
  - `kernel-as-text` R1, `rag-over-text` R1, `int4-quantized` R2,
    `extraction-instrument` R1/R2, four `cascade-*` gated arms R1.

**f2b-replicate** (`results-log/f2b-replicate.jsonl`) already demonstrated the reuse
pattern: same checkpoints + harness, fresh D-QA-R slice (3 seeds), one new arm
(`shuffled-kernel-verify-retry`). Verdict PASS.

### 3.2 Reuse tiers (what transfers, and the honesty boundary)

Ordered from safest to most judgement-dependent:

1. **Checkpoints + revisions (always reusable).** SmolLM2 135M/360M/1.7B + Skywork
   PRM are downloaded and revision-pinned. **Every** GPU record at R1/R2/R3
   (`f3, f4, f5→T, f6, f7, e8, e9, g1, l3a-cost, a5-llm`) reuses them — no re-fetch,
   identical revision. *Produce-once already done.*
2. **Harness + arm implementations (always reusable as code).** `f0-harness`,
   FLOP-meter, extraction-instrument, and the coded arms (`kernel-verify-retry`,
   `gloss-self-verify-retry`, `prm-verifier`, `self-consistency`, `kernel-as-text`,
   `rag-over-text`, `shuffled-kernel`) are validated in f2/f2b. Every f-experiment
   rides this harness rather than rebuilding it.
3. **Per-item decode logs (reusable AS DATA only when slice+model+seed+decode-config
   are identical).** This is the f2→f2b lever generalised, and the honesty boundary:
   a logged decode substitutes for a re-run **iff** the corpus pin, model revision,
   arm config, and seed match exactly; otherwise it is a *replication*, not a reuse.
   Candidates flagged for Fable to adjudicate in §5.

### 3.3 "Produce once, consume by several" — the prospective candidates

- **e9-full → e9-c (the strongest single opportunity).** `e9-c`'s arms are declared
  as *"all E9-full arms including gloss-text-self-verify-retry"* + one
  (`text-diff-checker-over-gloss`). Both are R1/R2 on overlapping corpora
  (`kernel-v0, molecules-v0, gloss/extraction sets`). → **Run e9-full once; e9-c
  consumes e9-full's arm decodes and adds only the axiom-instance + diff arm.** This
  is F2→f2b applied *before* the spend, not after.
- **f2's `model-alone` R1/R2/R3 decodes** are the `smaller-model-alone` /
  `larger-model-alone` reference arm named by `f2b` (already reused), `f4`, `f5`.
  Where the slice matches D-QA, they substitute for a re-run; where it differs
  (f3/f4/f5 use d-gl/d-dom/d-st) only the checkpoint+harness reuse holds.
- **f2's `extraction-instrument` + `kernel-as-text` + `rag-over-text`** are the exact
  null arms `e9-full` re-declares; if `e9-full`'s slice ⊆ f2's D-QA/gloss slice,
  these decodes transfer directly (Fable to confirm slice identity).
- **f7 (capstone) re-runs "each survivor's own frozen baseline set at added rungs."**
  → It should consume each survivor's *already-logged* R1/R2/R3 decodes and pay GPU
  **only for the added R4/T-rungs**, not re-run the whole matrix.
- **prm-verifier R1 decodes** = the HC3 trained-PRM comparator, reusable by any
  matched-FLOP verifier comparison (f2b already reused it).

---

## 4. Draft reuse-maximising ordering (SPECULATIVE)

Principle: **front-load the broadly-reusable producers so their outputs exist before
the many consumers; never run a consumer that would re-import a confound or
re-compute a shared output.** Contrast with a naive per-experiment
cheapest-decisive-first order, which would (a) run e9-c independently of e9-full and
pay twice for shared arms, (b) run L2a/L2b before the φ sweep and re-import the L2c
confound, (c) re-run model-alone baselines each f-experiment already has cached, and
(d) rebuild the engine per L3 rung.

### Wave 0 — already produced (amortised; do not rebuild)
Encoder + mint + `kernel-v0`; `f0-harness` + F2 GPU checkpoints/arms/**per-item
decodes**; `l3a` engine (PASS) + `a5` code-oracle (PASS); the R0 g-family structure
results. *These are the shared producers everything below consumes.*

### Wave 1 — CPU/$0 consumers of the built oracles (no infra gate)
Runs now, independent of `POST-F2-INFRA-OPEN`; each reuses an already-PASSED oracle:
- **`l3a-parse`, `a5-nl`** (mapper/NL legs) — reuse the l3a/a5 engine + gold-parse;
  produce the parse-side instrument L1a and L3b later reuse.
- **`g5`** (← g2✓, R0), then **`g4`** (← g2✓, R0) — g4 needs **`d-ax`**, so build
  `d-ax` here because `e9-c` and the L3a axiom leg reuse it (build-once, 3 consumers).

### Wave 2 — the infra decision (Fable/maintainer)
**`POST-F2-INFRA-OPEN` / `gate-t1`.** One decision unblocks 6 records. Not "work" but
the gate that sequences all of Wave 3. Owned by Fable/maintainer.

### Wave 3 — GPU correctness lane, shared-producer-first
1. **`e9-full` FIRST** among GPU records: it is a blocker (e9-c, f7, family-h0), it
   is R1/R2 (cheaper than R3/R4), and it maximally reuses F2's D-QA/gloss/extraction
   machinery. Its arm decodes are the inputs e9-c consumes.
2. **`e9-c`** immediately after — consumes e9-full's arms; adds only axiom-instance +
   diff arms (build `d-ir`, `d-ir-n` first; `d-ax` from Wave 1).
3. **`e8-r` → `e8-d`** (SAE lane; build `d-sae` first; e8-d gated on e8-r passing).

### Wave 4 — GPU efficiency lane, respecting f→f edges
1. Build corpora `d-gl`, `d-dom`, `d-ts` (each feeds one f-experiment; `d-dom` also
   feeds g1, so highest reuse of the three).
2. **`f4`** (← d-dom) → unblocks **`g1`** (+ d-cb) and feeds f7.
3. **`f3`** (← d-gl) → unblocks **`f5`** (+ f1✓, d-st, gate-t4).
4. **`f6`** (← d-ts).
5. **`f7` LAST** (Tier-5, $10k capstone): consume each survivor's logged R1/R2/R3
   decodes; pay GPU only for the added R4/T-rungs.

### Wave 5 — meta-gate
**`family-h0` → `a-h0`** once its 8 members (HC1,HC2,HE1–HE6 = e9-full, e9-c, f2✓,
f3, f4, f1✓/f5, f6) have verdicts. Terminal by construction.

### Programme-2 ladder rungs (POST-F2-INFRA + maintainer; `architecture-ladder.md` §6.1)
Order **L3a✓ → L1a → L3b → L1b(=f3) → L2c-lite → L2a → L2b → L2c-full → L3c**, with
the reuse edges made explicit:
- **L3b, L3c** reuse the built L3a **engine** + the F2 **harness** (no rebuild).
- **L1b** rides **f3** (= HE3) and the **A2/E5 adapter**.
- **L2c-lite** runs **before** L2a/L2b to produce φ\* (else confound re-imported);
  **L2c-full** carries σ×φ as a shared run (S3 amendment, not a new spend).
- **L1a** reuses the mapper/parse leg produced in Wave 1 (`l3a-parse`/`a5-nl`).

### Highest-leverage "produce once, reuse N times" (ranked)
1. **L3a/a5 engine artefact** → L3b, L3c, a5-llm/l3a-cost, + 4 model-internal ideas
   (in-degree 6). *Built; keep reusing, do not re-implement per rung.*
2. **F2 checkpoints + harness + arms** → all 8+ GPU records. *Built; the reuse is in
   not rebuilding.*
3. **e9-full arm decodes → e9-c** (superset arms) — one GPU spend, second near-free.
4. **L2c-lite φ\* sweep** → design points for L2a, L2b, L1b (+ σ×φ shares L2c-full).
5. **kernel-v0 + encoder + mint** → every experiment. *Built.*
6. **`d-ax` axiom corpus** → g4 + e9-c + L3a axiom leg.
7. **f2 `model-alone` R1/R2/R3 decodes** → reference arm for f2b (done), f4/f5, and
   f7's added-rung reuse.

---

## 5. Open questions / judgement calls left to Fable

These are the decisions this reconnaissance deliberately does **not** make:

1. **The honesty boundary on cross-experiment decode reuse.** f2b was a *fresh
   replication*, not a pure reuse of f2's decodes. Does the pre-registration /
   run-vs-audit discipline (`opus-execution-practices.md`; directives §3) permit an
   experiment to *consume another record's logged per-item decodes as its own arm
   output* without a fresh committed run — and if so, under what provenance stamp?
   This gates the entire §3.3 opportunity set. **Fable owns.**
2. **Slice identity for e9-full/e9-c ↔ f2.** Is e9-full's evaluation slice a subset
   of F2's D-QA/gloss/extraction slice at identical pins, so f2's
   extraction-instrument / kernel-as-text / rag-over-text decodes transfer directly?
   Requires reading the frozen slice definitions, not just corpus names.
3. **e9-c "all E9-full arms" semantics.** Does the registry intend e9-c to *consume*
   e9-full's outputs, or *re-run* the same arms under a distinct pin? The wording
   supports consumption; the freeze must state which.
4. **Ordering L2c-lite earlier vs later.** §6.1 places it at rank 5, but its
   de-confounding value for L2a/L2b might justify pulling it forward if the interp
   lane is prioritised. Reuse argues *earlier* (produce φ\* before its consumers);
   cost argues *after* the inference-only rungs. Fable's call.
5. **σ×φ shared-run accounting.** Confirm S3 genuinely rides the L2c-full training
   run with no separate spend, and that the shared-run design does not confound σ
   with φ (`kernel-introduction-schedule.md` §5–6).
6. **f7 scope this generation.** Tier-5, $10k. Is the capstone in-scope now, or
   deferred — and if run, is the "added-rungs-only" GPU-reuse accounting (§3.3)
   acceptable, or must survivors be re-run whole for a clean capstone?
7. **Reconcile with the backlog L-score, not replace it.** The engine already prices
   reusability via `L` in `score=(D×U×L)/max(C,C_floor)` (`research-engine.md` §2.7).
   Should this map feed per-stub L-scores (mechanical, auditable) rather than stand
   as a separate ordering? That keeps reuse inside the frozen scoring rubric.
8. **Post-F2-FAIL re-ranking.** F2's primary FAILed (f2b recovered a narrower
   non-inferiority claim). Per §6.2 the F2 verdict re-ranks the ladder; the
   ordering above assumes the efficiency lane still runs. Whether the FAIL demotes
   parts of Wave 4 is an interpretive call reserved for Fable.
