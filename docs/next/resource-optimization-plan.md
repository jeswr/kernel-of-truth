# N-R — Optimal resource usage: work taxonomy, reuse & composition, GPU-result reuse, reuse-maximising ordering

**Kernel of Truth programme — FABLE-OWNED DESIGN DELIVERABLE.**
Bead: `kernel-of-truth-utq` (maintainer-designated P0, Jesse 2026-07-09, incl. the
proactive-ordering refinement). Author: Kern (Fable design agent). Date: 2026-07-09.
Status: **AUTHORITATIVE for resource-usage policy** once committed; the mechanisms in
§1/§3/§5 are enforced through the files they land in (role files, practices doc,
`tools/registry/reuse-check.py`, `registry/artifact-ledger.jsonl`,
`registry/components.jsonl`). Changes to the *frozen honesty machinery* itself
(prereg-freeze / log-append / verdict-gen wiring) remain **maintainer-gated**
(P2 §7 item 3); those are enumerated as delta D9 in §5.
Binding constraints inherited: `docs/kernel-design-directives.md`,
`docs/next/opus-execution-practices.md`, `docs/next/research-engine.md` (engine laws §1.4),
the HONESTY-GUARD epistemic-tag discipline.

**Relation to the Opus reconnaissance.** `docs/next/reuse-ordering-analysis.md` was an
Opus recon pass, speculative on sequencing and on every "reuse is licensed" call. This
document validates, corrects, and supersedes it. Its file-level recon (dependency edges,
shared pins, logged outputs) checked out against the registry and logs; its sequencing
survives with corrections; **three of its reuse claims do not survive** (§0.1). Do not
cite the recon's ordering or reuse calls; cite this document.

---

## 0. What was validated and what was corrected

### 0.1 Corrections to the recon (each re-derived from the primary sources)

1. **"Per-item decodes" are not what is logged.** `results-log/*.jsonl` final-phase rows
   carry per-item **indicator/metric arrays** (`item_correct`, `item_correct_external`,
   `metric_vector`, extraction counts — verified across all 8 logs), **not raw decoded
   text**, and no raw generations are committed under `poc/`. So "consume another
   record's logged per-item decodes" is really "consume another record's logged per-item
   metric fields": a consumer's DV must be a pure function of fields the producer
   actually logged. This narrows the §3 opportunity set and creates the
   **superset-logging producer rule** (R-2, §3.5) — the single highest-leverage change
   this plan makes to future GPU runs.
2. **e9-full → e9-c is not decode-level reuse as drafted.** The recon called it "the
   strongest single opportunity: e9-c consumes e9-full's arm decodes". But
   `registry/experiments/e9-c.json` depends on corpora `d-ir`, `d-ir-n`, `d-ax` with
   record-level DVs (`record_caught`, `clean_record_flagged`), while e9-full runs on
   `d-qa`/`d-xif`/`d-ext` with item-level DVs. Different item universes ⇒ no output
   transfer as drafted. What "all E9-full arms" licenses today is **arm-implementation +
   harness + checkpoint reuse and same-session launch batching** (real, but tier-2 reuse
   per §3.3, not tier-3). Output-level reuse becomes available **only by design**: author
   d-ir's clean records as a declared subset of e9-full's evaluated records at e9-c's
   freeze (§3.4 worked example 2, and `registry/components.jsonl` `corpus-d-ir`).
3. **f2's null arms do not transfer to e9-full as claimed.** e9-full declares
   `gloss-dictionary-lookup` and `rag-with-citations` — different arm implementations
   from f2's `kernel-as-text` and `rag-over-text` (which were single-cell, single-seed
   R1 rows anyway). Name-level overlap between f2/f2b and e9-full is exactly:
   `model-alone` (R1/R2/R3 × 5 seeds), `gloss-self-verify-retry` (R1, incl. retry
   budgets), `extraction-instrument` (verified via
   `tools/registry/reuse-check.py check --record registry/experiments/e9-full.json`).
   Those are comparator cells, RC-gated per §3.4.
4. **The f2→f2b precedent must be split in two, and the split is the ruling's spine.**
   (a) `poc/f2/f2b-reanalysis.md` — a $0 re-analysis over `results-log/f2.jsonl`,
   correctly quarantined **EXPLORATORY** because its estimand (R1→R3 pairing) was chosen
   after unblinding; it could never flip a verdict. (b) `f2b-replicate` — a **fresh
   frozen experiment with a fresh run** on a fresh slice (d-qa-r), which is what made
   the finding confirmatory (PASS, cross-vendor CONFIRMED). The recon's framing "gap
   closure was free re-analysis" is true of (a) only. The generalisation is §3.4's
   RC-1/RC-4 distinction: *when the analysis was fixed relative to seeing the data*
   is the licensing variable — not who paid for the GPU.
5. **Registry hygiene found during validation:** `registry/ideas.jsonl` referenced a
   non-existent id `idea-a2-adapter-injection` in the `requires`/`dependencies` of the
   two 2026-07-09 maintainer-proposed ideas (the defined id is `idea-a2-adapter`).
   Corrected by appended last-line-wins entries (the registry's own convention).
   `idea-code-worldlayer-cpg` appears twice; the later `candidate` line is current —
   consistent with append-history semantics, no fix needed.

### 0.2 Validated as-is (spot-checked against registry/logs, not just the recon)

The frozen/draft ledger split (12 frozen-or-done incl. l3a/a5 PASS audited; 14 DRAFT);
`gate-t1` blocking 6 records; `d-ax` as the highest-reuse unbuilt corpus (g4 + e9-c +
axiom-expressivity leg); the f2 checkpoint revisions and arm×rung×seed matrix (88 rows,
verified); the l3a engine's requires-in-degree 6 in `ideas.jsonl`; the
`alternative_to`-share-one-bench structure of the encoder slots; L2c-lite's hard
precedence over L2a/L2b (`architecture-ladder.md` §6.1); S3 riding L2c-full's cap with
no independent spend (`kernel-introduction-schedule.md` S3: "deliberately parasitic",
+15–25% inside the cap).

---

## 1. Component (1) — WORK TAXONOMY: the Opus/Fable boundary as a per-task rubric

The maintainer's criterion is *maximise cheap-model throughput with zero loss of
experiment quality or potential*. The existing split (research-engine §3, the two Opus
role files) is correct but role-shaped; here it is made **task-shaped**: a test any
agent applies to any task in under a minute.

### 1.1 The two-test kernel (apply this first; the flowchart only elaborates it)

A task is **Opus-executable with zero quality loss** iff BOTH hold:

- **T1 — No open scientific degrees of freedom.** Every choice the task requires is
  either already made (frozen record, pinned pipeline, pinned prompts/schema, declared
  envelope) or is *scientifically inert* (cannot shift what is tested, how it is judged,
  or what is concluded). If the task requires choosing among options whose choice could
  move a result, an interpretation, or a future design — it is Fable's (or a registered
  fork).
- **T2 — Mechanically checkable failure.** The task's failure modes are detectable by
  lint/hash/gate/pin-mismatch (fail-closed), not by judgement. If doing it *badly* would
  be invisible to the tooling and visible only to expert review, it is Fable's.

Everything else in this section is T1/T2 applied to the programme's recurring task
shapes. When in doubt: T1 fails ⇒ Fable. The asymmetry is deliberate — misrouting
Fable-work to Opus costs experiment quality (unbounded); misrouting Opus-work to Fable
costs only quota (bounded).

### 1.2 The flowchart

```
START: a task T
│
Q1. Does T create/alter WHAT is tested or HOW it is judged?
    (hypotheses, arms, endpoints, kill criteria, margins, IV/DV sets,
     model-definition code, encoder/kernel-generation software, generation-agent
     prompts, schema, corpus RECIPES, SAP blocks)
    ├─ YES → FABLE (Designer/Statistician/Skeptic). STOP.
    └─ NO ↓
Q2. Does T interpret an outcome, promote an epistemic tag, write a conclusion,
    or rank/curate by importance? (assessment records, kill-chain reads,
    EXTRAPOLATION→MEASURED promotion, literature curation, topic selection)
    ├─ YES → FABLE (interpretive). STOP.
    └─ NO ↓
Q3. Is T's output a PURE FUNCTION of frozen/pinned inputs?
    (verdict-gen, report-gen, ledger/status regeneration, corpus-pin,
     reuse-check build, chain verification, count reporting)
    ├─ YES → OPUS; route to HAIKU if high-volume + fully mechanical. STOP.
    └─ NO ↓
Q4. Is T moving data/compute FORWARD through already-pinned machinery on more
    inputs? (lit-KB discover/triage/extract/embed with pinned prompts; pinned
    mint-pipeline variant expansion within ALGORITHM_VERSION; running a frozen
    RunSpec)
    ├─ YES → OPUS (experiment-runner / kb-pipeline-runner), boundary-check
    │        first, budget-capped, provenance mandatory. STOP.
    └─ NO ↓
Q5. Is T ops/infra whose choices are scientifically inert AND inside a declared
    envelope? (run-script authoring from a frozen RunSpec, Modal plumbing,
    monitoring, batching, container sizing, infra retries, spend tracking)
    ├─ YES → OPUS. Envelope absent for a needed parameter → STOP-AND-QUEUE
    │        for Fable (grey zone GZ-1). STOP.
    └─ NO → grey zone: apply T1/T2 explicitly; if either fails or is unclear,
            FABLE — and file the task shape as a new GZ fork below.
```

### 1.3 Grey zones, registered as explicit forks (directives §4 form)

| Fork | Task shape | Ruling + deciding criterion |
|---|---|---|
| **GZ-1** | Run-script needs an operational parameter the frozen record does not fix (batch size, container type, shard count) | OPUS iff a Fable-declared envelope exists and the parameter provably cannot alter logged metrics (throughput-only); otherwise STOP-AND-QUEUE. The experiment-runner role already half-states this; now binding via T1. |
| **GZ-2** | Exploratory re-analysis of logged data | Split: FABLE specifies the estimand (one committed paragraph, tagged); OPUS computes it mechanically; output lands quarantined `phase:"exploratory"`; FABLE interprets. Opus never picks *what* to explore (T1) and never writes what it *means*. |
| **GZ-3** | Reset-correct-refreeze corrections | OPUS may execute corrections that are mechanical regenerations (pin recompute, path fix) under the opus-execution-practices scope note; any correction touching arms/endpoints/margins/kill text is FABLE + re-freeze. Deciding test: does the diff touch a field `verdict-gen` reads? YES → Fable. |
| **GZ-4** | Backlog scoring (research-engine §2.7) | D and U stay two-Fable-scorer. **C** (cost normalisation from the tier ladder) and **L** (now derived mechanically from the reuse graph — §4.4) are OPUS-computable; a Fable scorer may override a computed L only with a written justification committed with the stub. |
| **GZ-5** | New `d-*` corpus | RECIPE (item authoring rules, planted-violation design, slice definitions) = FABLE; forward MINT of a pinned recipe = OPUS (kb-pipeline-runner boundary check applies). One corpus, two tasks — always split it. |
| **GZ-6** | Right-sizing a running/pending experiment (n, seeds, rungs) | FABLE-frozen envelope only; Opus may *shrink toward* the envelope floor for infra reasons, never below power (the decidability lint is the mechanical check, T2). |
| **GZ-7** | Prose that is not a conclusion (run-logs, commit messages, status notes) | OPUS, under the no-conclusions rule (state what ran, not what it means). Mechanical check: `claims-check` marker-line lint. |

### 1.4 Enforcement

The rubric is referenced from `.claude/agents/experiment-runner.md` (pre-spend gate
addition, §3.6 below) and `docs/next/opus-execution-practices.md` practice (5). The
flowchart is the *dispatch test* the Opus coordinator applies before assigning any
task to a runner role; a task that fails T1/T2 and was executed by Opus anyway is an
audit finding (engine retro item, research-engine §2.8).

---

## 2. Component (2) — ARCHITECTURE REUSE + COMPOSITION

### 2.1 The composition invariant (the design rule everything else serves)

Every experiment in this programme decomposes as:

```
experiment = SUBSTRATE (fixed, built once)
           × CORPUS (from the d-*/canonical pool)
           × ARM IMPLEMENTATIONS (from the arm library)
           × CHECKPOINTS (pinned model ladder R1..R4/T*)
           × ANALYSIS (P8 templates keyed on endpoint data shape)
```

**A new experiment must be expressible as a delta over these pools.** A proposal that
rebuilds a pool member (a second harness, a bespoke re-mint of an existing corpus, a
re-implementation of an existing arm, a re-download of pinned checkpoints) is a design
smell to be justified in the freeze or rejected at the step-6 skeptic attack. The
machine surface for the pools is **`registry/components.jsonl`** (kot-component/1; one
line per reusable component: kind, status built/unbuilt, where, consumers) — created
with this plan and maintained at every freeze (the freezing Fable agent adds/updates
lines for components the record produces or consumes; Opus regenerates counts, GZ-4
discipline).

### 2.2 The substrate (built; amortised; never rebuild)

Encoder construction-B (pin `40e8c8ba…`) · mint pipeline · `kernel-v0` /
`molecules-v0` / `lexical-wn31` canonical corpora · `f0-harness` + FLOP meter +
extraction instrument · R1/R2/R3 + PRM checkpoint revisions (in `results-log/f2.jsonl`
`pins_observed`) · l3a engine + a5 code oracle (both PASS, audited) · A2/E5 adapter
recipe + X4 projection · X0–X4 bench · mapper `a1-hybrid`. Full list with consumers:
`registry/components.jsonl`.

### 2.3 How `ideas.jsonl` slot/compatibility semantics map to build-sharing rules

- **`alternative_to` within one slot ⇒ one bench, N variants.** The encoder
  `binding-op` slot (construction-B / TPR-exact-shallow / WL-compressed-sensing) and
  the `similarity-decode` slot (polarity vs structural) are each evaluated by the same
  X0–X4 rig: testing a second variant costs the variant, not the rig. RULE: a slot
  variant's experiment record must pin the incumbent bench; a new bench for a slot that
  has one is a rejected build.
- **`requires` in-degree ⇒ build the hub once, before its dependents.** Measured hubs:
  `idea-l3a-oracle` (in-degree 6 + successors l3a-parse/l3a-cost, a5-llm/a5-nl) and
  `idea-a2-adapter` (l1b-dense-io, compositional-rollup, crosslingual-phrase-coverage).
  Both are already built — the rule's force is *forward*: no dependent may schedule a
  re-implementation, and an unbuilt hub outranks its dependents in ordering (§4).
- **`orthogonal_to` ⇒ cross-cutting axis: one sweep fixes the family's design points.**
  φ (L2c) is orthogonal to L1b/L2a/L2b: L2c-lite produces φ\* once; L2a/L2b/L1b consume
  it. σ (schedule) rides L2c-full (S3). RULE (hard precedence, inherited from
  architecture-ladder §6.1): **an axis experiment freezes and completes before any
  family member that would otherwise fix the axis silently.** Encoded as a dependency
  edge, not a priority preference (`l2c-phi-star-design-points` in components.jsonl).

### 2.4 The permutation-grid consequence

The idea registry's ~46 entries over ~15 slots imply a permutation space in the
hundreds; the pools reduce planned coverage to **~10 unbuilt components** (9 corpora +
the φ\* design points — see components.jsonl `status:"unbuilt"`), everything else being
recombination. The kernel-variant expansion split already enforces the same shape at
the kernel level (new schema/prompts = Fable design; within-version expansion = Opus
mint). This is the concrete answer to "cover the grid with a small set of building
blocks": the grid is covered when the unbuilt-component list is empty, not when N
bespoke experiments have each built their own world.

---

## 3. Component (3) — CROSS-EXPERIMENT GPU-RESULT REUSE

### 3.1 What actually exists (MEASURED, from the logs)

`registry/artifact-ledger.jsonl` (generated by `tools/registry/reuse-check.py build`;
117 final-phase rows across 8 producers) is now the authoritative inventory. The
economically significant assets: f2's 88-row A10 matrix (model-alone R1/R2/R3 × 5
seeds on 500 D-QA items; kernel-verify-retry R1/R2 × 5 seeds × retry budgets;
gloss-self-verify-retry R1; prm-verifier R1; self-consistency R1; cascades R1;
single-cell kernel-as-text / rag-over-text / int4 rows), f2b-replicate's 21-row A100
matrix on the fresh d-qa-r slice, and the deterministic CPU runs (l3a, a5, m0b, f1,
g6, g7). All eight producers are **unblinded** (verdicts exist) — so today every
retrospective reuse is RC-4-constrained; prospective (Case A) reuse becomes available
starting with the next freezes.

### 3.2 Reuse tiers (re-derived; tier 3 corrected per §0.1-1)

1. **Checkpoints + revisions — always reusable.** Identity is the revision pin.
2. **Harness + arm implementations + instruments — always reusable as code.** Identity
   is the harness manifest / arm config hash.
3. **Logged per-item metric fields — reusable AS DATA only under the RC conditions
   (§3.4).** Not "decodes": only the fields in the ledger row's `per_item_fields`
   exist. A consumer DV not computable from them requires a fresh run *no matter what
   the honesty ruling says* — which is why R-2 (superset logging + raw-output
   persistence) matters more than any single reuse.

### 3.3 THE RULING on the load-bearing honesty question

*Question: does the pre-registration / honesty discipline permit an experiment to
consume ANOTHER record's logged per-item outputs as its OWN arm output WITHOUT a fresh
run?*

**RULING: YES, conditionally — and the conditions are about when analysis choices were
fixed relative to seeing the data, never about who paid for the GPU.** Logged
final-phase rows are hash-chained, pin-stamped data. The discipline (P-1…P-3, P-10,
G-13) exists to prevent analysis choices conditioned on seen outcomes; it does not
sanctify re-computation of identical bits. A fresh run of a deterministic pipeline on
identical pins is a *checksum*, not new evidence; conversely, no quantity of fresh GPU
can launder an estimand chosen after unblinding. Three cases:

- **Case A — prospective consumption (fully confirmatory).** The consuming record
  freezes its reuse declaration BEFORE the producer's data exists. At consumer-freeze
  time nothing is conditioned on anything; the producer's rows land later and flow into
  the consumer's pinned analysis exactly like its own arms. This is pre-registration
  working as designed, one level up.
- **Case B — retrospective consumption of already-unblinded logs (comparator-only).**
  The producer's data has been analysed; any estimand chosen now is chosen knowing it.
  Reused rows may therefore serve only as **comparator/baseline/null arms**; the
  consumer's primary endpoint must contrast at least one freshly-run arm against them;
  the already-seen status is disclosed at freeze. (Knowing a baseline's value is not in
  itself corrupting — the programme publishes its verdicts internally — but a primary
  computed *entirely* over already-seen data is exploratory by construction, P-10/G-13:
  the f2b-reanalysis quarantine is the permanent precedent.)
- **Case C — verdict citation.** Consuming another record's *verdict* as a premise is
  the epistemic-tag system (MEASURED with scope), not data reuse; it licenses no arm.

**The six reuse conditions (RC-1…RC-6). ALL must hold; each maps to an existing
guardrail rather than inventing a new value:**

- **RC-1 — Freeze-declared, cell-complete consumption.** The consumer's frozen record
  names: producer id, producer `frozen_sha256`, the exact cell set (arm × rung × seed
  × config) consumed, the producer log rows' hashes, and the selection rule — which
  must be "all rows matching the declared config", never hand-picked rows or seeds
  (anti-cherry-pick; the G-2/G-13 family).
- **RC-2 — Exact-pin identity.** Corpus/slice hash (kot-corpus-hash/1), item set and
  order, model revision, arm implementation/config hash, seeds, decode parameters,
  harness manifest — identical between producer `pins_observed` and consumer pins.
  **Anything less is not reuse; it is a replication (fresh run) or a different
  experiment.** (This is why f2b-replicate was correctly a replication: fresh d-qa-r
  slice ⇒ RC-2 fails by design.)
- **RC-3 — DV computability + instrument-gate transfer.** Every consumer DV over
  reused rows is a pure function of the producer's logged `per_item_fields`; the
  producer's instrument gates were green for the consumed cells; the consumer's own
  instrument gates are re-evaluated over the reused rows (instrument failures score as
  instrument events in the consumer too — RT-3 carries across the reuse boundary).
- **RC-4 — Already-seen discipline** (Case B only): comparator arms only; ≥1 fresh arm
  in the primary contrast; `reused_arms_already_unblinded: true` disclosed in the
  record so the auditor prices selection risk.
- **RC-5 — Reuse-consistency instrument (the batch-effect gate).** When fresh arms
  will be contrasted against reused rows, the freeze declares a small overlap re-run
  (pre-declared cell + n ≥ 50 items) with a pre-declared agreement bound; a miss scores
  **INSTRUMENT-INVALID for the reused arms** — never hypothesis evidence. This converts
  "the old environment equals the new one" from a stipulation into a measurement.
  Waivable ONLY for deterministic CPU producers where bit-identity is directly
  checkable (the l3a/a5 engines log `deterministic_repeat_identical` [MEASURED:
  results-log/l3a.jsonl, results-log/a5.jsonl]; GPU inference stacks get no waiver).
- **RC-6 — Provenance + audit traversal; no verdict-as-data; per-link licensing.**
  Consumed rows are referenced in the consumer's log with {producer id, frozen_sha,
  seq range, row hashes}; `registry/audit-status.jsonl` notes the reuse; the consumer's
  Codex audit re-verifies the producer chain for the consumed rows. Reuse consumes
  logged rows, never a verdict; chained reuse (A←B←C) requires each link to satisfy
  RC-1…RC-6 independently.

DECISION: logged final-phase outputs may serve as a consuming record's arm data only under RC-1–RC-6 above, and a primary endpoint computed entirely over already-unblinded data is permanently exploratory [MEASURED: registry/verdicts/f2b-replicate.json — the confirmatory promotion required a fresh frozen run, while the same estimand over logged f2 data stayed quarantined per the poc/f2/f2b-reanalysis.md header; rails P-10/G-13 via docs/next/opus-execution-practices.md §4].

Until delta D9 lands (maintainer-gated), the *wire format* for RC-1/RC-6 is: the
consumer's frozen record pins the producer's log rows as input artifacts (path + sha +
seq range) in its pins/`depends_on`, and its pinned analysis script reads both logs.
This uses only existing freeze machinery. `kot-reg/2`'s open `artifact_hashes` map
(research-engine §1.5, delta D6) is the natural home and is a second reason to approve
D6.

### 3.4 The standing adjudications (applying RC-1…RC-6 to the named candidates)

1. **e9-full → e9-c.** As drafted: tier-2 reuse only (arms/harness/checkpoints +
   same-session batching — run them as one GPU session to share container spin-up and
   checkpoint loads). To get tier-3 reuse, e9-c's freeze must (i) be Case-A prospective
   (freeze before e9-full runs), (ii) declare d-ir clean records as a subset of
   e9-full's evaluated records, and (iii) require e9-full to log the per-item fields
   e9-c's DVs need (R-2). Worth doing: e9-c's cap is only $10, but the same pattern at
   f7 scale is worth thousands — establish it here where a mistake is cheap.
2. **f2 `model-alone` / `gloss-self-verify-retry` / `extraction-instrument` cells →
   e9-full.** Case B. Licensed as comparator arms iff e9-full's freeze pins the
   *identical* d-qa slice hash and item order (RC-2 — to be verified at freeze against
   `pins_observed.corpus_hashes.d-qa = ad756a7e…`), declares the reuse (RC-1), keeps
   its primary contrast on fresh arms (RC-4 — automatic: e9-full's primary is
   error-catch, computable only from fresh runs), and carries an RC-5 overlap cell.
   If the slice differs at all: fresh runs, no exception.
3. **f7 capstone (Tier-5, $10k cap).** DECISION: f7's default accounting is to consume each survivor's logged R1–R3 cells as Case-B comparator cells for the slope fit, pay GPU only for the added rungs (R4/T\*) plus one fresh full-arm overlap cell at R3 as the RC-5 instrument (~5% of matrix cost), and disclose both accountings (full re-run vs reuse) in the `--dry-plan` at gate-t5 for explicit maintainer ratification [STIPULATED: ASM-0010].
   The slope estimand and margins are already fixed in the DRAFT before any
   added-rung data exists, which is what keeps the mixed-rung fit honest.
4. **prm-verifier R1 decisions and f2's single-cell arms (kernel-as-text,
   rag-over-text, int4).** The five-seed prm-verifier cells are reusable Case-B
   comparators on the identical slice. The single-seed single-cell rows are **not**
   load-bearing reuse material (no seed variance); they may inform design, nothing
   else.
5. **Free re-analysis (the f2b-reanalysis pattern).** Always permitted, always
   exploratory, always quarantined — and now *scheduled* rather than incidental: §4's
   Wave R0 requires Fable to enumerate the open questions answerable from
   `registry/artifact-ledger.jsonl` before each GPU freeze wave (re-analyse before
   re-running, made proactive). Execution splits per GZ-2.

### 3.5 Producer-side rules (what every FUTURE GPU record must do)

- **R-1 — Ledger entry at close.** `reuse-check.py build` is re-run after every
  final-phase append (Opus Runner duty; pure function, T1-clean).
- **R-2 — Superset logging + raw-output persistence.** At freeze, the record declares
  per-item logged fields as the UNION of its own DVs and the DVs of every declared
  prospective consumer; and GPU runs persist **raw per-item model outputs** (decoded
  text) as content-addressed committed artifacts unless the freeze states why not
  (size/licence). Rationale: f2's re-analysis space was exactly its logged
  `item_correct` arrays — a few MB of raw text per run would have multiplied the free
  re-analysis space at ~zero cost against GPU dollars. This rule is cheap insurance
  purchased at design time.
- **R-3 — Reuse declaration is a freeze-time section.** Absence of a reuse check at
  freeze is a skeptic-attack finding (step 6); post-D9 it becomes a hard lint.

### 3.6 The PRE-SPEND GATE (enforced)

Before ANY launch, the Opus Runner runs:

```
python3 tools/registry/reuse-check.py check --record registry/experiments/<id>.json
# and, for ad-hoc cells:
python3 tools/registry/reuse-check.py check --arm <arm> --rung <rung> [--corpus <name>] --gate
```

and records the output in the run-log. A non-empty result → STOP; the coordinator/Fable
records a reuse decision (consume under RC / shrink the run / proceed-with-reason)
before any spend. Proceeding past a non-empty check without a recorded decision is a
gate violation (audit finding). Enforcement points, all edited with this plan:
`.claude/agents/experiment-runner.md` (MUST list), `docs/next/opus-execution-practices.md`
practice (5). The `kb-pipeline-runner` role is exempt (no GPU spend; its budget caps
already gate it).

---

## 4. Component (4) — PROACTIVE REUSE-MAXIMISING ORDERING

Principle (validated from the recon, now normative): **producers before consumers;
shared artefacts built once, early; never run a family member before its axis; never
pay for a cell the ledger already holds at identical pins.**

### 4.1 Wave R0 — landed with this plan ($0)

The mechanisms themselves (this doc, ledger, components registry, tool, role/practice
edits); reuse declarations + R-2 superset-logging written into the DRAFT freezes of
`e9-full`, `e9-c`, `f7` when they freeze; Fable enumerates the free-re-analysis
questions over the ledger before Wave 3 freezes.

### 4.2 Waves (execution order; validated/corrected from the recon)

- **Wave 1 — $0/CPU, no infra gate:** `l3a-parse`, `a5-nl` (successor legs over the
  PASSED, deterministic engines; they produce the parse-side instrument L1a and L3b
  consume) · build **`d-ax` (+`d-axn`)** — Fable recipe, Opus mint (GZ-5 split); 3
  consumers make d-ax the top unbuilt corpus · then `g5`, `g4` (R0, g2✓).
- **Wave 2 — the `gate-t1` / POST-F2-INFRA-OPEN decision** (maintainer, with a Fable
  recommendation memo). One decision unblocks e8-r, e9-full, f3, f4, f6. Nothing in
  Wave 3+ freezes before it.
- **Wave 3 — GPU correctness lane:** `e9-full` first (blocker for e9-c/f7/family-h0;
  R1/R2-cheap; maximal harness reuse) **with R-2 superset logging + raw-output
  persistence in its freeze**; build `d-ir`/`d-ir-n` (subset-of-e9-full design per
  §3.4-1); `e9-c` immediately after, same GPU session where feasible; `d-sae` →
  `e8-r` → `e8-d`.
- **Wave 4 — GPU efficiency lane:** `d-dom` first among corpora (2 consumers) → `f4` →
  `g1` (+`d-cb`); `d-gl` → `f3` → `f5` (f1✓ + `d-st`, gate-t4); `d-ts` → `f6`; **`f7`
  last**, under gate-t5 with the §3.4-3 reuse accounting in its dry-plan.
- **Wave 5 — meta:** `family-h0` → `a-h0` when the 8 members have verdicts.
- **Programme-2 rungs:** keep the ladder §6.1 order L3a✓ → L1a → L3b → L1b(=f3) →
  L2c-lite → L2a → L2b → L2c-full(+S3) → L3c, with L2c-lite→{L2a,L2b} as a hard
  dependency edge (not a preference) and S3 inside L2c-full's cap.

### 4.3 The recon's eight open questions — answered

1. **Honesty boundary:** ruled in §3.3 (conditional YES; RC-1…RC-6; Case A/B/C).
2. **e9↔f2 slice identity:** name-level only until e9-full's freeze pins the slice
   hash; adjudication 2 of §3.4 specifies the freeze-time check. Not assumed.
3. **e9-c "all E9-full arms" semantics:** ruled = arm-implementation reuse as drafted;
   output consumption only via the §3.4-1 prospective design. The e9-c freeze must
   state which, in RC-1 form.
4. **L2c-lite earlier vs later:** keep rank 5. The de-confounding value is fully
   captured by the hard precedence edge; pulling it ahead of the cheaper, independently
   decisive L1a/L3b buys nothing while L2a/L2b remain gated. DECISION [STIPULATED:
   ordering choice, this plan; revisit only if L2a/L2b are un-gated early].
5. **σ×φ accounting:** confirmed — S3 rides L2c-full's cap (+15–25%), no independent
   spend; S1/S2 gate which σ arms enter (kernel-introduction-schedule S3, verified).
6. **f7 scope:** deferred to gate-t5 by construction (it needs f4/f6 verdicts); the
   default reuse accounting is §3.4-3; the maintainer ratifies at the gate.
7. **Fold into L-score vs separate ordering:** **fold in** — see §4.4.
8. **Post-F2-FAIL re-ranking:** the efficiency lane stands. The F2 kill fired on a
   degenerate primary (R2-alone ≤ R1-alone denominator artifact) [MEASURED:
   registry/verdicts/f2.json + reports/auto/f2/analysis-output.json], and
   f2b-replicate then established, on a fresh slice with a shuffled-kernel control and
   a separation gate, verifier lift with genuine kernel content (primary effect 0.1507,
   lower95 0.1053; shuffled recovery ≤ 0; audit CONFIRMED) [MEASURED:
   registry/verdicts/f2b-replicate.json]. The verifier mechanism is alive in narrowed
   scope on the covered slice; nothing in the F2 outcome demotes f3/f4/f6, whose
   hypotheses do not route through the failed primary. (The full f2/f2b interpretive
   assessment remains a separate pending Fable deliverable; this paragraph rules only
   the *sequencing* consequence.)

### 4.4 Ordering mechanism: fold into the backlog L-score (with teeth)

DECISION: reuse-ordering FOLDS INTO the frozen scoring function of research-engine §2.7 rather than standing as a rival ordering — one prioritisation surface, no vibes fork; two orderings would let whichever is convenient be cited, the exact failure §2.7 exists to prevent [STIPULATED: ASM-0011].
Two amendments to §2.7 (edited there with this plan):

- **L is derived, not vibed:** L = 3 if the stub's work product is consumed by ≥2
  other pending records/candidates, 2 if exactly 1, 1 if 0 — read mechanically off
  `registry/components.jsonl` consumers + the artifact ledger; scorers override only
  with committed written justification (GZ-4).
- **Tie-break extension:** ties break cheapest-decisive-first, THEN
  **producers-before-consumers** (topological order on the declared reuse graph).

The §4.2 waves are then the *current instantiation* of the scored backlog (and the
Generation-2 slate proposal), not a second mechanism: when D3 (backlog scorer) lands,
re-scoring must reproduce this ordering or the discrepancy is itself a finding to
resolve at the generation boundary.

---

## 5. Enforcement ledger — what changed where, and what remains maintainer-gated

**Landed with this plan (no frozen-machinery change):**

| Mechanism | File |
|---|---|
| This plan (taxonomy §1, component map §2, reuse ruling §3, ordering §4) | `docs/next/resource-optimization-plan.md` |
| Artifact ledger (117 rows, 8 producers) | `registry/artifact-ledger.jsonl` |
| Component pool registry (25 components; 10 unbuilt) | `registry/components.jsonl` |
| Ledger builder + pre-spend gate tool | `tools/registry/reuse-check.py` |
| Pre-spend gate as a Runner MUST | `.claude/agents/experiment-runner.md` |
| Practice (5): pre-spend reuse gate | `docs/next/opus-execution-practices.md` |
| §2.7 L-derivation + tie-break; §5.1 deltas D8/D9 | `docs/next/research-engine.md` |
| Recon superseded-with-corrections notice | `docs/next/reuse-ordering-analysis.md` |
| ideas.jsonl dangling-ref correction (append, last-line-wins) | `registry/ideas.jsonl` |

**Maintainer-gated (P2 §7 item 3; the D7 precedent — standalone landed, wiring gated):**

- **D9:** `prereg-freeze`/`registry-check` refuse a record whose declared cells collide
  with the artifact ledger absent an RC-1 reuse block; first-class
  `reused_from` support in `log-append`/`verdict-gen`; `kot-reg/2` `artifact_hashes`
  as the reuse-pin home (strengthens the case for approving D6).

**For the maintainer to ratify with this plan:** the §3.3 ruling (RC-1…RC-6), the R-2
producer rule, the f7 default reuse accounting (§3.4-3), and the §4.4 fold-into-L-score
decision.
