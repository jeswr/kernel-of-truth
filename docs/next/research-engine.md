# N-B — The Research Engine: reusable, self-maintaining scientific-method machinery

**Kernel of Truth programme — next-direction seed, Pillar B.**
Author: Kern (Fable design agent). Date: 2026-07-08.
Status: **DESIGN/PLANNING document.** No GPU spend; no registry entry is amended here.
Everything proposed below becomes real only through the existing rails (`prereg-freeze`
for anything that runs; maintainer sign-off for anything that changes the honesty
machinery itself — P2 §7 item 3). Binding constraints: `docs/kernel-design-directives.md`
(esp. §3 operationalisable-scientific-method, §4 don't-guess-test, §6 honest stats,
§7 write-up-first-class, §8 cross-vendor auditor).
Companion: `docs/next/arch-survey.md` (N0 — the architecture space this engine will
consume as candidates).

**Purpose in one sentence.** Generalise the honesty/registry machinery built for the
current programme (P1–P11, `registry/`, `tools/registry/`, the Codex/GPT-5.5 audit) into
a **reusable research engine**: a fixed procedure that turns *any* candidate
neurosymbolic architecture into a pre-registered, kill-criterioned, honestly-analysed,
cross-vendor-audited experiment — plus a **self-maintaining loop** that mechanically
turns every verdict into the next prioritised questions, so the programme never again
needs a bespoke eleven-component planning build to ask its next question.

---

## 0. What is being generalised — the instance/engine split

The current research plan (docs/research-plan/00–11) is a **single-instance product**:
eleven documents, ~190 DAG nodes, built by a fleet of Fable agents over days, to test one
architecture family (the NSM kernel's seams A1/A2/A5/A6/M4). Almost all of its machinery
is already architecture-agnostic; the kernel-specific content is a thin layer on top.
The engine is the quotient — keep the rails, parameterise the content.

### 0.1 Inventory: what is already reusable as-is

| Asset | Where | Why it generalises unchanged |
|---|---|---|
| Registry schemas (`kot-reg/1`, `kot-log/1`, `kot-amend/1`, `kot-audit/1`, `kot-verdict/1`) | `registry/schema/` | They encode *scientific-method invariants* (one primary endpoint, exhaustive verdict rules, TOST-gated NULLs, hash-chained raw log, run≠audit), not kernel semantics. Nothing NSM-shaped is in them. |
| Write-path tools (`prereg-freeze`, `log-append`, `verdict-gen`, `report-gen`, `registry-check`) | `tools/registry/` | Pure functions over the schemas above. `verdict-gen`'s expression grammar (P2 §3.1) is deliberately content-blind. |
| The 14 honesty guardrails G-1…G-14 + threat table | P2 §4 | Each names a *dishonesty pattern* (goalpost-moving, re-roll-until-pass, self-audit, p-hacking, scale overclaim) — none is architecture-specific. |
| The SAP template + primary-test decision table + IUT/Holm/TOST/power rules | P8 §1 | Keyed on **endpoint data shape** (paired binary, rate-vs-threshold, hull membership, slope…), not on what produced the data. |
| Scale-extrapolation methodology (≥3 rungs, functional forms, published-anchor comparison, 1-OOM cap, scale-language license) | P8 §2, P2 G-12 | Any architecture claim faces the same scale question. |
| The per-experiment stage template `reg → inputs → (mock →) run → log → readout → audit → close` | P3 §0.2 | Already instantiated 20+ times; the stage chain is the engine's unit of execution. |
| Role roster + separation matrix (run≠audit, write≠grade, sole-committer) | P5 §§1–2 | Identity discipline, not content. Cross-vendor audit (Codex/GPT-5.5 via `codex` CLI) per directives §8. |
| Audit kit + cross-vendor audit protocol | P4 S6, `registry/audits/` | Re-run-from-pins is content-blind; already exercised (f1 CONFIRMED cross-vendor). |
| Modal/AWS harness discipline (RunSpec, staged-manifest assertion, mock-first, budget ledger) | P3 §3 | Transport, not science. |
| Write-up machinery (claims manifest, `--paper` lint, banned-spin vocabulary, explainer-back template) | P2 §5.5, P9 | Claims-trace-to-verdict-object is the invariant; the paper's topic is a parameter. |

### 0.2 Inventory: what is instance content (must become parameters)

| Instance content | Current form | Engine parameterisation |
|---|---|---|
| The hypothesis suite (H0/HC/HE/HS) | `registry/hypotheses.json`, frozen from P1 §8 | Per-candidate hypothesis blocks appended under a namespace (`<candidate>/<h-id>`); the file becomes a versioned union (§1.3 step 3). |
| Kernel-specific pins (`encoder_hash`, `corpus_hashes` names) | `kot-reg/1` `pins` block | Generalise to an open `artifact_hashes` map + the invariant "every identity-bearing input is hash-pinned" (§1.5 — the only schema change needed, `kot-reg/2`). |
| The coverage gate (m0b, G-7) | Hard-wired kernel-expressibility coverage | Generalise to `instrument_gates[]`: every candidate declares its own validity instruments (coverage, extraction-failure rate, instrument-check) that must be green before any hypothesis read — the RT-3/RT-7 lesson made structural. |
| The global decision tree (TAKE/NARROW/PIVOT/KILL/UNDECIDED) | a-h0 + GNG-2/3, hand-derived in P1 §6 | A fixed 5-route **template** instantiated per candidate and per generation (§2.5) — exhaustiveness by construction (catch-all route), the RT-1 lesson made structural. |
| The tiered kill-tree (cheapest-decisive-first, budget caps) | P1 §5 tiers 0–5 | The **budget-ladder pattern**: every candidate declares its own rungs with caps; the ordering rule (cheapest decisive spend first) is engine-fixed. |
| The mandatory baseline set (kernel-as-text null + 4 industrial baselines) | G-8 lint against P1's table | Generalised baseline law (§1.4): every candidate must beat *its own content rendered as text* at matched budget + the strongest relevant industrial baseline — the Law-2 lesson made structural. |
| The ~190-node DAG | P3 §8 hand-assembled | Generated: candidate record + stage template + declared dependencies ⇒ DAG nodes + beads issues (`dag-gen`, §5 delta D4). |

**The claim this section licenses:** a new architecture experiment needs *zero* new
honesty machinery. It needs a filled-in template (§1), and the engine needs five small
build deltas (§5) to make the filling-in mechanical.

---

## 1. Deliverable (a) — the reusable scientific-method PROCEDURE

### 1.1 The unit of work: a CANDIDATE

A **candidate** is one architecture/mechanism/seam with a falsifiable value claim —
the granularity at which things are proposed, tested, promoted, and retired. Current
examples at this granularity: "verifier-offload buys parameters" (F2/HE1), "dense concept
input beats matched-token text" (F3/HE3), "kernel↔SAE label space beats a linear probe"
(E8-D/HC4). A candidate is *not* a whole programme; a programme is a portfolio of
candidates sharing the rails.

Candidate lifecycle (single-direction, mirroring the P2 experiment lifecycle one level up):

```
PROPOSED → SCOPED → REGISTERED → RUNNING → DECIDED → { PROMOTED | RETIRED | PARKED }
                                                        (PROMOTED candidates re-enter
                                                         as new rung/generalisation
                                                         candidates — §2.3)
```

Each lives at `candidates/<id>/` (repo-persistent; the box is ephemeral) with a fixed
file set — the template below. Status transitions are recorded in
`candidates/<id>/status.jsonl` (append-only, same discipline as everything else).

### 1.2 The candidate template (the "filled-in template, not a bespoke build")

```
candidates/<id>/
  claim.md            # 1 page, fixed headings (§1.3 step 1)
  prior-art.md        # lit-scan output + novelty statement (§1.3 step 2)
  hypotheses.json     # namespaced hypothesis block(s) (§1.3 step 3)
  experiment-draft/   # DRAFT kot-reg records, one per decisive experiment (§1.3 step 4)
  forks.json          # registered design forks: options + deciding experiment + kill (§1.3 step 5)
  assessment/         # post-verdict assessment records land here (§2.1)
  status.jsonl
```

### 1.3 The procedure, step by step (idea → frozen experiment)

Target friction: **≤1 Fable-agent-day from PROPOSED to freeze-ready** for a candidate
whose experiment fits existing harnesses; the engine's own kill criterion (§5.2) tests
this.

**Step 1 — Claim (PROPOSED).** Write `claim.md` under fixed headings, each mandatory:

- *Mechanism* — what computes what, where (one paragraph + one diagram-as-text).
- *Seam cell* — which interface-locality cell it occupies (text / own-activations /
  trained-bridge / external-engine — N0 §1.4 Law 1). A raw-foreign-coordinates cell
  claim must be explicitly budgeted as a falsification (the A1 lesson).
- *Value thesis* — which of the two theses (correctness / efficiency, directives §2)
  it serves, stated as a measurable delta on the full metric vector V.
- *The text-null answer* — one paragraph: why would this beat its own content rendered
  as text at matched budget? (Law 2.) A candidate with no credible answer may still be
  SCOPED — but only as a cheap pre-declared falsification, never as a build-out.
- *Kill sketch* — the observation that would kill it, in one sentence (sharpened into
  the frozen kill criterion at step 4).

**Step 2 — Prior-art check.** Run the `lit-scan` skill (delta D5, §5): targeted search
for (i) the mechanism under other names, (ii) published nulls/penalties (the LCM/CALM
scaling-penalty pattern — reports/lit-llm-injection-priorart.md L3), (iii) the strongest
published baseline. Output `prior-art.md` with citations; a candidate that re-tests a
published TOST-quality null must say why (different regime, different instrument) or be
retired at this step. This step is what keeps the engine from re-running the literature.

**Step 3 — Hypotheses.** Write `hypotheses.json`: each hypothesis gets a namespaced ID
(`<candidate>/H1`), a falsifiable statement, the deciding experiment ID, and the
baseline set. On SCOPED→REGISTERED these are appended to the frozen union
`registry/hypotheses.json` (versioned append, never edit — the G-8 lint source grows
monotonically).

**Step 4 — Decisive experiment record(s).** Instantiate `kot-reg` DRAFT record(s) in
`experiment-draft/`. Everything here is the *existing* schema discipline; the template
supplies defaults and the lints refuse omissions:

1. IVs with full level sets; DVs with unit + direction; scale rungs from the standing
   model ladder (≥2 rungs to run, ≥3 for any slope claim).
2. **Baselines (generalised G-8):** the candidate's own content-as-text null (mandatory,
   always) + the strongest relevant industrial baseline(s) from the standing menu
   {RAG-over-text, self-verify+retry at matched budget, matched-compute sampling,
   distillation, quantized/smaller-model-alone, linear probe} — selected per claim type,
   linted at freeze against the hypothesis block.
3. **Exactly one primary endpoint**; secondaries in one Holm family; SAP instantiated
   from the P8 §1.9 template by data shape (the P8 §1.1 decision table already covers
   every endpoint shape used so far); power computed before freeze (decidability lint).
4. **Verdict rules**, ordered, first-match-wins, ending in the mandatory
   `INCONCLUSIVE` catch-all; `INSTRUMENT-INVALID` rules for every declared instrument
   gate; kill criterion verbatim; extrapolation envelope verbatim.
5. **Instrument gates** (generalised G-7/RT-3): every instrument between the model and
   the metric (extraction interface, coverage filter, judge, annotation protocol) is
   named, has its own validity bound, and failures score as instrument events, never
   hypothesis events.
6. Budget block within the candidate's declared rung caps; pins for every
   identity-bearing artifact (`artifact_hashes`, §1.5).

**Step 5 — Forks.** Every design uncertainty inside the candidate is registered in
`forks.json` as `{options, why-uncertain, deciding-experiment, kill-criterion}`
(directives §4). A fork is either decided by an arm inside the decisive experiment or
spawns its own cheap experiment record — it is never silently picked.

**Step 6 — Pre-freeze attack (SCOPED gate).** The Skeptic role (P5 R7) attacks the
draft: strawman baselines, leakage paths, undecidable gates, missing instrument gates —
the RT-2/RT-3/RT-4 failure classes as a checklist. Freeze is blocked without the attack
memo. The Codex red-team (R10) is invoked here only for candidates whose worst-case
spend exceeds the Tier-2-equivalent cap (cheap candidates get the Fable skeptic only —
friction control).

**Step 7 — Freeze (REGISTERED).** `prereg-freeze` exactly as today: schema + lints,
frozen_sha256 into `frozen-index.json`, external timestamp (coordination issue / OSF).
From here the experiment *is* a current-programme experiment: mock → run → log →
readout → audit → close, all on the existing tools, with the Codex/GPT-5.5 audit
required to upgrade any PASS.

**Step 8 — Close and assess.** `verdict-gen` + `report-gen` emit the verdict object and
rendered report; then the §2 loop takes over — the assessment record is mandatory
(the DAG's close predicate for a candidate includes it).

### 1.4 Engine-fixed laws (the non-negotiable core any candidate inherits)

These are the current programme's hard-won invariants, promoted from "this plan's
rules" to "the engine's physics" — a candidate that cannot live with them is out of
scope for this engine, by design:

1. **Freeze before run; append never edit; verdict = f(frozen record, log).** (P2 P-1…P-3)
2. **Text-null law:** every mechanism arm faces its own content as text at matched
   budget. (Law 2; RT-2)
3. **Instrument gates precede hypothesis reads;** instrument failures are never
   hypothesis evidence in either direction. (RT-3/RT-19)
4. **Run ≠ audit, cross-vendor;** PASS-PENDING-AUDIT until Codex confirms. (G-6, §8)
5. **Negatives at equal prominence; every route ends in a publishable document.** (G-5, §7)
6. **One primary endpoint; Holm family for secondaries; TOST for nulls; power before
   freeze; scale language licensed by measured rungs only.** (P8; G-10/G-12)
7. **Budget caps with fail-closed halts; cheapest-decisive-first ordering.** (G-11; P1 §5)
8. **2-revision lineage cap; one replication buy per experiment, two per generation;**
   then STOP-AND-PUBLISH-UNDECIDED. (RT-1/RT-6)

### 1.5 The one schema change: `kot-reg/2` (proposed, maintainer-gated)

`kot-reg/1` hard-codes two kernel-instance fields. Proposed generalisation (backwards
compatible; P2 §7 item 3 makes this a maintainer-approved versioned amendment):

- `pins.encoder_hash` + named corpus fields → `pins.artifact_hashes: {<name>: sha256}`
  (open map) + lint "non-empty, and every artifact referenced by IV/DV definitions
  appears". kot-reg/1 records remain valid (their fields map into the map).
- `coverage_requirement` (m0b-specific) → `instrument_gates: [{id, metric_pointer,
  bound, source_experiment}]` — m0b becomes one instance; extraction-failure gates
  (f2.iface/e9.iface pattern) become declared members instead of DAG special cases.
- Add `candidate: "<id>"` (namespace link) and `generation: <n>` (§2.5).

Nothing else changes; `verdict-gen`, `log-append`, and the guardrails are untouched.

---

## 2. Deliverable (b) — the OUTCOME-ASSESSMENT → NEXT-STEP loop

This is what makes the engine self-maintaining: a completed experiment's verdict is
never a dead end — it is *input* to a mechanical assessment that emits the next
questions, re-scores the backlog, and updates the portfolio, on rails, with the same
honesty discipline as the experiments themselves.

### 2.1 The post-verdict ASSESSMENT record (`kot-assess/1`, delta D1)

After every `X.close`, a mandatory assessment record is produced at
`candidates/<id>/assessment/<exp-id>.json` (and the candidate's DAG close predicate
requires it). Drafted by the Statistician role from the verdict object, attacked by the
Skeptic, committed by the Coordinator — three identities, same separation discipline.

```jsonc
{
  "schema_version": "kot-assess/1",
  "experiment": "f2",
  "candidate": "verifier-offload",
  "verdict_ref": {"path": "registry/verdicts/f2.json", "sha256": "…"},
  "surprise": "expected-fail|expected-pass|surprise-fail|surprise-pass|undecided",
                       // vs the prereg prior stated in claim.md — surprises are the
                       // highest-information outcomes and auto-raise backlog priority
                       // of everything they touch
  "forks_resolved": [{"fork": "HS12", "resolution": "…", "basis": "verdict|commentary"}],
  "mechanism_state": "alive|dead|parked",   // per the candidate's mini-tree (§2.4)
  "questions_opened": [                      // each becomes a backlog stub (§2.2)
    {"stub_id": "…", "question": "…", "kind": "rung-extension|generalisation|
      falsification|instrument|new-candidate", "est_cost_usd": 0, "est_agent_days": 0,
      "blocking": ["<candidate-ids or gates it informs>"]}
  ],
  "ledger_updates": [                        // §2.6 known-results ledger entries
    {"kind": "null-bound|pass|kill|instrument-fact", "statement": "…", "scope": "…"}
  ],
  "tree_impact": "…"                         // which routes/gates changed state
}
```

Hard rule inherited from the citation scanner: `questions_opened` and `ledger_updates`
may not overstate the verdict — the assessment is scanned by `registry-check
--citations` like any prose. The assessment *interprets*; it cannot *upgrade*.

### 2.2 Verdict → action mapping (mechanical defaults; deviations are recorded decisions)

| Verdict | Mandatory actions (engine defaults) |
|---|---|
| **PASS** (audit-confirmed) | (1) Candidate → PROMOTED for that claim scope. (2) Auto-generate the three standard follow-on stubs: **rung-extension** (next scale rung — a PASS at 2 rungs wants its slope), **falsification-hardening** (the strongest surviving rival baseline re-matched — attack your winner), **absorption probe** for injected mechanisms (does the benefit survive fine-tuning of the host? — the InstructRetro expectation, N0 Law 3). (3) Ledger entry. (4) Any dependent gates re-evaluated. |
| **FAIL** (kill criterion met) | (1) Mechanism → RETIRED at that claim scope; DAG descendants pruned automatically (the f1-kill-prunes-F5 pattern, generalised). (2) Failure-mode tag from the closed taxonomy {effect-absent, baseline-wins, cost-dominated, instrument-limited-scope} — the tag determines whether any narrower re-scope stub is *permitted* (only `instrument-limited-scope` licenses one, and it counts against the 2-revision lineage cap). (3) Negative-results write-up node opens (every route ends in a paper). (4) Ledger entry so no future candidate silently re-proposes it. |
| **NULL** (TOST-bounded) | As FAIL, plus the equivalence bound itself is the ledger entry ("X ≈ text within d=0.5 at R1–R2") — future candidates whose claim.md contradicts a ledger null are flagged at step 2 (§1.3) automatically. |
| **INCONCLUSIVE** | One replication buy iff pre-declared and unused (engine law 8); the buy must change what the power analysis says was underpowered (n, seeds, rung), not re-roll. After the buy: STOP-AND-PUBLISH-UNDECIDED — candidate → PARKED with an explicit **reopen condition** (budget, model availability, instrument fix) recorded in `status.jsonl`. Parked ≠ retired: a parked candidate re-enters the backlog automatically when its reopen condition is met. |
| **INSTRUMENT-INVALID** | Pre-registered repair once; second failure scores undetermined-not-supporting for every gate the experiment feeds (RT-19 generalised) and opens an **instrument stub** — instrument work is first-class backlog content, not overhead. |
| **INCOMPLETE-DATA / BUDGET-HALT** | Coordinator decision recorded: resume via ops amendment, or close INCOMPLETE and treat as INCONCLUSIVE for routing. |

### 2.3 Promotion and retirement (portfolio semantics)

- **PROMOTED** is always *scoped*: "PASS for claim C at rungs R, coverage slice S" —
  the verdict object's own scope fields, never wider. Promotion unlocks (i) citation of
  the result in pitches/papers (with kill text adjacent, as today), (ii) the follow-on
  stubs above, (iii) eligibility as a *component* of composite candidates (e.g. a
  promoted verifier seam inside a cascade candidate).
- **RETIRED** is also scoped, with the failure tag. Retirement of a mechanism does not
  retire its instruments or artifacts — those return to the shared pool (the D-* nodes'
  outputs are engine assets).
- **Attack-your-winners rule (anti-confirmation guard):** the backlog must at all times
  contain ≥1 open falsification stub against some PROMOTED result, and each generation
  must run at least one. A portfolio that only extends winners is degenerating; this
  rule is checked at every generation boundary (§2.5).

### 2.4 The go/no-go tree, generalised

The RT-1 lesson: hand-built decision trees are non-exhaustive exactly at the messy
outcomes. The engine therefore fixes the route template once and *generates* trees:

- **Per-candidate mini-tree** (generated from the template at REGISTERED):
  `PROMOTE (PASS pattern) → NARROW (partial pattern: pass without slope/scope — fund
  exactly the missing piece, once) → PIVOT (dead for thesis A but a pre-named secondary
  use survives) → RETIRE (kill/null pattern) → PARK-UNDECIDED (catch-all)` —
  exhaustive by construction because the last route is a catch-all, machine-evaluated as
  P2 §3.1 expressions over the candidate's verdict objects.
- **Programme-level tree per generation** (§2.5): the same five routes over the
  generation's candidate mini-tree outputs, with a Holm family across the generation's
  primary endpoints (the family-h0 pattern generalised: `family-gen-<n>`, members fixed
  at generation freeze, non-read-out members scored as non-rejections). The
  programme-level tree is frozen *before* the generation's first final-phase run.

### 2.5 Generations — the engine's outer clock

The engine runs in **generations**: a batch of candidates frozen together, run as waves
under the concurrency cap, closed together. (The current programme is retroactively
Generation 1.) A generation boundary is the engine's synchronisation point:

1. All member experiments CLOSED (or PARKED by rule) + assessments committed.
2. `family-gen-<n>` Holm readout; programme-level tree evaluated (computed route).
3. **Backlog re-scoring** (§2.7) over: carried stubs + assessment-opened stubs +
   lit-scan stubs + maintainer submissions + the red-team's mandatory
   "strongest-rival" proposal (Codex must propose the candidate most likely to *beat*
   the portfolio's best mechanism — adversarial idea generation, not just adversarial
   review).
4. **Generation dossier** to the maintainer (GATE-H, the GNG-2 pattern): routes,
   verdicts with kill texts, spend ledger, the proposed next-generation slate (top-k
   backlog by score, k sized to budget), and the explainer-back. Maintainer ratifies or
   reorders — an override is a recorded decision.
5. **Engine retro** (§2.8).

Cadence target: a generation ≈ 2–4 weeks at agentic pace (the long poles remain human
gates, GPU queues, annotation — P3 §5's finding carries over). Between boundaries the
inner loop is event-driven: verdict lands → assessment within one session → affected
stubs re-scored immediately; a surprise verdict may pull the boundary forward.

### 2.6 The known-results LEDGER (institutional memory, delta D2)

`registry/ledger.jsonl` — append-only, one line per assessed fact: passes (scoped),
kills, TOST bounds, instrument facts (e.g. "X3: raw kernel-cosine banned", "X4: JL
8192→512 preserves RDM ρ≈0.97"). Steps 1–2 of the candidate procedure lint new
`claim.md`s against the ledger: proposing something a ledger null already bounds, or
building on a retired mechanism, is flagged mechanically. This is the piece that makes
the engine *cumulative* — the current programme holds this knowledge in prose
(arch-survey §1.3's one-screen ledger is exactly this table, hand-built); the engine
makes it a machine surface.

### 2.7 The BACKLOG mechanism (prioritisation without vibes)

`backlog/` in-repo, mirrored to beads (`bd`) as the live tracker — one stub per open
question, from the sources in §2.5 step 3. Priority is a **pre-declared scoring
function**, frozen like everything else, so prioritisation cannot be quietly steered:

```
score = (D × U × L) / max(C, C_floor)
  D — decision relevance (1–5): how many live routes/gates does the answer move?
      (5 = moves the programme-level route; 1 = curiosity)
  U — uncertainty (1–5): 5 = genuine coin-flip under stated priors + ledger;
      1 = literature or ledger effectively decides it already
  L — leverage/reusability (1–3): does the work product (instrument, corpus,
      harness) serve other candidates?
  C — cost: worst-case USD + agent-days, normalised to the tier ladder; C_floor
      prevents division-by-~0 favouring trivia
```

Discipline (same separation pattern as verdicts): D/U/L are scored **independently by
two Fable agents** with a one-line justification each; disagreement >1 point goes to
the Coordinator with both justifications on record; scores + justifications are
committed with the stub. Ties break **cheapest-decisive-first** (the kill-tree
economics, engine-fixed). Two standing overrides, both pre-declared: (i) an
instrument-invalid stub blocking a live candidate outranks its score; (ii) the
attack-your-winners rule (§2.3) guarantees one falsification slot per generation.
The scoring rubric itself may only change at a generation boundary, by recorded
amendment — a Goodhart guard on the engine's own objective.

### 2.8 Self-maintenance of the engine itself

- **The engine is versioned and frozen like an experiment.** This document (once
  ratified) + the schemas + the scoring rubric are the engine spec; changes are dated,
  signed amendments with maintainer approval (the P2 §7 "freeze of the freeze
  machinery" rule extended to the loop).
- **Engine retro at every generation boundary,** run by the cross-vendor red-team
  (R10): did any guardrail get worked around? Which lints fired/never fired? Where was
  friction spent (time-to-freeze per candidate — measured, see §5.2)? Findings are
  RT-numbered and land as engine amendments or tooling stubs — the engine red-teams
  itself on the same cadence it red-teams the science.
- **Health invariants checked in CI** (extend `registry-check`): every CLOSED
  experiment has an assessment; every PROMOTED/RETIRED state has a verdict path; the
  backlog has ≥1 falsification stub; no candidate exceeds its lineage cap; ledger
  append-only.

---

## 3. Deliverable (c) — roles and cadence

The P5 roster carries over intact (it was already designed content-blind); the engine
adds the loop duties. Identities, separation matrix, and the ≤5-concurrent /
waves / no-grandchildren rules are unchanged (P5 C-4; the fleet was rate-limit-killed
twice above 5).

| Role | Model | Engine duties (added to P5 duties) |
|---|---|---|
| **Coordinator (Kern)** | Opus main loop | Owns the outer clock: wave launch, generation boundaries, backlog custody (commits scores, breaks ties), dossiers, all deliberate commits. Still never runs/grades/audits/writes. |
| **Designer / Scoper** | Fable | Steps 1–5 of the candidate procedure (claim, prior-art, hypotheses, experiment draft, forks); composite-candidate design. Distinct identity per candidate where separation demands. |
| **Runner** | Fable | X.inputs/mock/run — unchanged. |
| **Statistician** | Fable | SAP blocks, readouts, extrapolation analyses — unchanged; + drafts assessment records (§2.1) and backlog D/U/L scores (one of the two independent scorers). |
| **Skeptic** | Fable | Pre-freeze attack memos (step 6); attacks assessment drafts; second independent backlog scorer. |
| **Bulk / Registrar** | Haiku | Log custody, chain verification, status/ledger regeneration, beads mirror, volume corpus drafting — mechanical, high-volume, never self-certifying. |
| **Auditor / Red-team** | **Codex/GPT-5.5** (`codex` CLI, cross-vendor) | X.audit (only path to PASS); paper.review; generation-boundary engine retro; the mandatory strongest-rival candidate proposal per generation. |
| **Maintainer (@jeswr)** | human | Unchanged seven gate classes (P3 §2): budget caps, freezes/sign-offs, credentials, annotation, spend, programme decisions (now = generation dossiers), external exposure. Design goal preserved: the engine runs gate-to-gate with no other human action. |

**Cadence summary.**
Inner loop: event-driven — verdict → assessment (≤1 session) → stub re-scoring.
Waves: ≤5 agents, launched by the Coordinator per the generation slate.
Generation boundary: every 2–4 weeks or on slate completion / surprise verdict —
Holm readout, tree evaluation, backlog re-score, maintainer dossier, engine retro.
Standing heartbeat: weekly one-screen status to the maintainer (from `status.json` +
ledger — generated, not written).

---

## 4. Positioning against current literature (why this engine, not an off-the-shelf one)

Autonomous-research systems now exist end-to-end: **AI Scientist**
(arXiv:2408.06292, 2024; v2 arXiv:2504.08066, 2025), **Agent Laboratory**
(arXiv:2501.04227, 2025), **AgentRxiv** (arXiv:2503.18102, 2025) — idea → experiment →
paper pipelines. Their documented weakness is exactly the part this engine hardens:
they generate and self-review, but nothing prevents post-hoc reframing, there is no
pre-registration, no append-only raw log, and review is same-model self-grading; human
studies of LLM-generated research (Si et al., arXiv:2409.04109, 2024) found novelty
without matching rigor/feasibility. **Curie** (arXiv:2502.16069, 2025) is the closest in
spirit — an explicit "experimental rigor engine" (intra/inter-agent rigor modules) — but
it enforces *procedural* reliability, not *pre-registered inferential honesty*: no
frozen kill criteria, no pure-function verdicts, no TOST-gated nulls, no cross-vendor
audit. On the human-science side, **REFORMS** (arXiv:2308.07832; Science Advances 2024)
and pre-registration-for-predictive-modeling proposals (arXiv:2311.18807, 2023) define
the reporting/prereg standard — as checklists for humans. This engine's differentiator
is the combination: the REFORMS/prereg standard **mechanised as fail-closed tooling**
(P2's threat table), executed by an agent fleet with **cross-vendor adversarial audit**,
and closed into a **self-maintaining verdict→backlog loop**. That combination is, to the
best of the step-2-style search run for this document (2026-07-08), not published as a
working system — which also means the engine itself is a publishable methods
contribution alongside whatever science it produces (a P9-route paper).

---

## 5. Bootstrap plan, cost, and the engine's own kill criterion

### 5.1 Build deltas (everything else already exists)

| # | Delta | Est. effort | Notes |
|---|---|---|---|
| D1 | `kot-assess/1` schema + `assess-gen` tool (drafts the record from a verdict object; Statistician completes) | ~0.5 agent-day | stdlib-only, same conventions |
| D2 | `registry/ledger.jsonl` + ledger lint in `registry-check` + one-time backfill from the current verdicts/arch-survey §1.3 | ~0.5 agent-day | backfill is transcription, `retro:true`-style |
| D3 | Candidate template dir + `candidate-new` scaffold skill + backlog scorer (rubric file + two-scorer protocol) | ~0.5 agent-day | |
| D4 | `dag-gen`: candidate record + stage template → DAG nodes + beads issues (replaces hand-assembling P3 §8 for new work) | ~1 agent-day | the biggest friction win |
| D5 | `lit-scan` skill (step-2 search protocol + citation-tagged output format, per N0's [search]/[memory] convention) | ~0.5 agent-day | |
| D6 | `kot-reg/2` (pins map + instrument_gates + candidate/generation fields) | ~0.5 agent-day | **maintainer-gated** (P2 §7 item 3) |

Total ≈ 3–3.5 agent-days, ~$0 compute, R0-tier. Nothing blocks the currently-running
F2 pivot; D1–D3 can land before F2 closes so its verdict is the first to flow through
the loop (the natural acceptance test, mirroring "freezing f2 was the backbone's
acceptance test").

### 5.2 The engine as its own testable fork (directives §4 applied to ourselves)

Low confidence is honestly placed on two design choices; both are framed as testable
forks with kill criteria, measured over the next two generations:

- **Fork ENG-1 — friction claim.** *Hypothesis:* a new candidate whose experiment fits
  existing harnesses goes PROPOSED → freeze-ready in ≤1 Fable-agent-day and ≤2 calendar
  days, measured from `status.jsonl` timestamps, for ≥3 of the first 4 post-F2
  candidates. *Kill:* if it takes >2 agent-days median, the template is a bespoke build
  in disguise — redesign the template (options: thinner mandatory set for Tier-0-scale
  candidates; or accept that scoping is irreducibly ~2 days and re-cost the cadence).
- **Fork ENG-2 — scoring rubric vs coordinator judgement.** *Hypothesis:* the D×U×L/C
  rubric's top-3 picks match the maintainer-ratified slate in ≥2 of the first 3
  generation boundaries (i.e. the rubric encodes, not replaces, judgement). *Kill:* if
  the maintainer consistently overrides, the rubric is theatre — replace with recorded
  free-form coordinator ranking + mandatory written justification (cheaper honesty),
  keeping only the two standing overrides.

### 5.3 Open decisions for the maintainer

1. **Ratify the engine spec** (this document) as the standing procedure — it then
   freezes and changes only by amendment (§2.8).
2. **Approve `kot-reg/2`** (D6) — the only change touching the honesty schemas.
3. **Generation budget envelope pattern:** confirm that each generation dossier carries
   its own spend ask (the GATE-T4/T5 pattern generalised), with the standing tier caps
   as per-candidate defaults.
4. **Confirm the red-team's strongest-rival duty** for Codex (one candidate proposal
   per generation) — it changes Codex's role from pure reviewer to adversarial
   contributor; the separation matrix still bars it from running/grading what it
   proposed (a proposal it authored is scoped/frozen by Fable designers, and its audit
   assignment goes to a different auditor pseudonym).
5. **Cadence ack:** 2–4-week generations with a weekly one-screen heartbeat.

---

*Sources for §4: [Curie (arXiv:2502.16069)](https://arxiv.org/abs/2502.16069),
[AgentRxiv (arXiv:2503.18102)](https://arxiv.org/abs/2503.18102),
[REFORMS (arXiv:2308.07832)](https://arxiv.org/abs/2308.07832) /
[Science Advances version](https://www.science.org/doi/10.1126/sciadv.adk3452),
[Pre-registration for Predictive Modeling (arXiv:2311.18807)](https://arxiv.org/abs/2311.18807);
AI Scientist (arXiv:2408.06292/2504.08066), Agent Laboratory (arXiv:2501.04227) and
Si et al. (arXiv:2409.04109) carried from author knowledge of the 2024–2025 literature,
consistent with the search results above.*
