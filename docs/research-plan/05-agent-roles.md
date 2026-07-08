# P5 — Specialised agent roles + DAG placement

**Status:** operational role plan for maintainer sign-off, 2026-07-08 (rev 2 — E1: R8
Results-Auditor and R10 Red-Team moved to the cross-vendor Codex/GPT-5.5 auditor invoked
via the `codex` CLI, per maintainer decision, superseding the backup-Fable-account plan;
O-P5-1 resolved. **Timeline note 2026-07-08:** the calendar dates in the phase-staffing
table are pre-recompression; the agentic-pace re-base (P3 §5) applies — phase windows are
gate-relative (Tier-0 ≈ GNG-0 +1 day agent-side; F2 ≈ GNG-0 +3–5 days; Tiers 2–3 ≈ +1–2 wk
on annotator turnaround; Tier 5 ~Oct 2026 on the compute-access lead). Role assignments and
wave structure unchanged).
Component P5 of the research plan (`docs/research-plan/`). Governed by
`docs/kernel-design-directives.md` (binding — esp. §3 "specialised AGENT ROLE definitions,
and a map of which role is needed at which stage", §6 honest statistics, §7 write-up as
first-class). Companion to `01-hypotheses-experiments.md` (P1), `02-data-and-reporting.md`
(P2 — identity strings and guardrails G-1…G-14 used verbatim), `03-operational-dag.md`
(P3 — node IDs, stage template §0.2, guardrails GR-1…GR-15, wave schedule §5 used verbatim).
P4 (`04-skills.md`, skills + audit checklist) is not yet written; this document binds to the
skill verbs fixed by directives §3 and P3 node I-SKILLS (`prereg`, `run-experiment`,
`flop-meter`, `decode-verify`, `audit-result`, `report-gen`, `paper-claims`, `explain-back`)
and must be re-linted against P4 when it lands (a rename there is a mechanical update here).
**Author:** Fable planning agent (P5), for @jeswr. Coordination: sparq-org/sparq#1683.

Scope: (1) the full specialised-role roster — purpose, model tier, skills/tools,
inputs/outputs, guardrail enforced, per role; (2) the identity & separation matrix that
mechanises the honesty rules ("the agent that runs never audits; the agent that writes never
grades"); (3) the DAG-stage → role placement map over P3 §8's node list; (4) the
concurrency/wave plan inside the ≤5-agent cap; (5) ready-to-commit `.claude/agents/*.md`
skeletons for the four highest-traffic roles.

Nothing here relaxes P2/P3. Where this document and P3 §0.3 both speak, this document is the
finer-grained elaboration of the same four base identities (Coordinator, Runner, Auditor,
Writer) — it splits them into specialised roles without changing any separation rule, and it
never exceeds the concurrency cap P3 GR-3 sets.

---

## 0. Binding constraints the roster must satisfy

| # | Constraint | Source |
|---|---|---|
| C-1 | Opus main loop **coordinates only**: schedules, launches waves, commits deliberately, prepares gate dossiers, talks to the maintainer. It never trains, runs, grades, audits, or writes the paper. | P3 §0.3; maintainer working mode |
| C-2 | Design, implementation, analysis, and writing are delegated to **Fable** subagents; auditing/red-teaming is delegated to the cross-vendor **Codex/GPT-5.5** auditor (`codex` CLI) per the 2026-07-08 maintainer decision. | maintainer working mode; E1 auditor decision |
| C-3 | Bulk, low-judgement generation (volume corpus drafting, mechanical log custody) goes to **Haiku** subagents. | task directive |
| C-4 | **≤5 concurrent subagents** at all times; agents are launched in waves; **no agent spawns children** (no grandchildren — a role needing parallelism uses Modal `starmap` containers, which are not agents). | P3 GR-3; fleet was rate-limit-killed twice above 5 |
| C-5 | **Run ≠ audit:** the agent identity that ran or built any part of an experiment never audits it; a computed PASS stays PASS-PENDING-AUDIT until a CONFIRMED audit by a distinct identity. | P2 G-6; P3 GR-6 |
| C-6 | **Write ≠ grade:** the agent writing the paper/explainer never executes `verdict-gen`, never audits, and never authors an analysis script; every number it uses comes from a committed verdict object via the claims table. | directives §7; P3 GR-15 |
| C-7 | Every record-writing action carries a stable **agent identity string** (`kern/<tier>-<role>-<n>` or `codex-gpt5.5/…` for the cross-vendor auditor/red-team identities), asserted at write time and cross-checked by the P2 G-6 schema rule. | P2 §2.2/§4 |
| C-8 | GATE-H nodes are human-only; no role performs, simulates, or assumes them. Roles only *prepare dossiers* for them. | P3 §2 boundary rule |
| C-9 | Nothing semantic-web-shaped is any role's target or reference; the Explicator authors in the native NSM-derived formalism only. | directives §1 |

---

## 1. Role roster

### 1.1 Overview table

| # | Role | Identity string(s) | Model tier | Primary DAG surface | Headline guardrail it enforces |
|---|---|---|---|---|---|
| R1 | **Coordinator "Kern"** | `kern/opus-coordinator` | Opus (main loop, not a subagent) | scheduling, wave launch, gate dossiers, deliberate commits, maintainer comms | GR-3 cap, GR-4 fail-closed gates, GR-8 no auto-push |
| R2 | **Explicator** | `kern/fable-explicator-<n>` | Fable | D-AX, D-AXN, D-DOM, g9.author, kernel/molecule curation, m0b judgement inputs | directive §1 native formalism; pin-on-author (GR-2) |
| R3 | **Experiment-Runner** | `kern/fable-runner-<n>` | Fable | X.inputs, X.mock, X.run for every campaign; I-* infrastructure builds | GR-2 pins, GR-13 mock-first, G-14 registered seeds |
| R4 | **Data-Registrar** | `kern/haiku-registrar-1` | Haiku | X.log appends, chain verification, frozen-index custody, r-final bundle, beads mirror | G-1/G-2 append-only tamper-evident log |
| R5 | **Efficiency-Profiler** | `kern/fable-profiler-1` | Fable | I-F0 build+ownership, metric-vector V instrumentation, RunSpec cost sizing, lifecycle amortization inputs | G-9 full metric vector; GR-1 worst-case-$ sizing |
| R6 | **Statistician / Analyst** | `kern/fable-stats-1` | Fable | SAP blocks at every X.reg; X.readout (verdict-gen); a-hs9/10/11/12; a-extrap-2/5; a-h0 | directives §6 wholesale: G-3/G-4/G-10 frozen analysis, G-12 scale-language license |
| R7 | **Adversarial-Verifier / Skeptic** | `kern/fable-verifier-1` | Fable | pre-freeze attacks on every draft registry entry; D-* leak/parity checks; instrument-check design | GR-10 baseline parity; leakage found *before* spend |
| R8 | **Results-Auditor** | `codex-gpt5.5/auditor-<n>` — Codex/GPT-5.5 via the `codex` CLI (O-5, resolved: second-vendor auditor) | Codex (GPT-5.5) — cross-vendor | every X.audit (GATE-A); paper.review | G-6/GR-6 run-vs-audit separation, now **cross-vendor**; only path to PASS |
| R9 | **Scientific-Writer** | `kern/fable-writer-1` | Fable | paper.claims → paper.outline → paper.draft; xb.draft | GR-15 claims-trace discipline; C-6 write≠grade |
| R10 | **Red-Team / Frontier-Skeptic** | `codex-gpt5.5/redteam-1` — Codex/GPT-5.5 via the `codex` CLI | Codex (GPT-5.5) — cross-vendor | GNG-2/GNG-3 dossier stress-tests; pre-submission hostile mock review; any frontier pitch | P1 §6 anti-overselling guards, adversarially applied |
| R11 | **Bulk-Generator** | `kern/haiku-bulkgen-<n>` | Haiku | volume drafting inside D-IR/D-QA/D-GL/D-TS (templates + seeds pinned by others) | never self-certifies; all output re-validated upstream |

Eleven roles, four base identities (P3 §0.3): R2/R3/R5/R6/R7 are specialisations of the
*runner* identity class, R8/R10 of the *auditor* class, R9 of the *writer* class, R1 is the
coordinator. The separation matrix (§2) is defined over identities, not role names, so the
specialisation cannot weaken any P2/P3 rule. **The auditor class (R8/R10) is cross-vendor**
(maintainer decision, 2026-07-08): it runs on OpenAI Codex/GPT-5.5 invoked via the `codex`
CLI, not on any Anthropic account — a *different vendor and model family* from every
`kern/*` identity, which is materially stronger independence than the previously planned
backup-Claude-account separation.

### 1.2 Role cards

Each card: purpose · model tier + why · skills/tools · inputs → outputs · guardrail enforced
(and on whom) · explicit MUST-NOTs.

---

**R1 — Coordinator "Kern"** (Opus main loop)

- **Purpose:** the only scheduler. Reads the beads mirror of P3 §8, opens waves within the
  cap, materialises RunSpecs *administratively* (hands them to runners; never executes),
  reviews `results-incoming/` and performs every deliberate commit (GR-8), assembles GATE-H
  dossiers (GNG-0/1/2/3, GATE-T4/T5, paper.sign, xb.deliver), files beads, notifies the
  maintainer, runs the AUTO-GATE evaluator scripts (the *scripts* decide; Kern only invokes
  and obeys fail-closed CLOSED results).
- **Model tier:** Opus — long-horizon multi-session judgement, low token volume, no
  experiment content generation.
- **Skills/tools:** `bd` (beads), git, Task-spawn (one level only), Monitor, `registry-check`,
  the gate-expression evaluator, budget-ledger reader, `report-gen` (render-only).
- **Inputs → outputs:** verdict objects, gate records, ledger, beads state → wave launches,
  commits, dossiers, maintainer messages, status syncs.
- **Guardrails enforced:** GR-3 (never >5 live subagents; kills the newest launch on breach),
  GR-4 (treats any unevaluable gate as CLOSED), GR-8 (nothing external leaves without a
  GATE-H record), GR-1 in-flight (owns the kill-switch inventory GR-14).
- **MUST NOT:** execute any X.run/X.readout/X.audit; edit any registry/log file directly
  (only via the tools it invokes for commit staging); spawn a subagent that spawns subagents;
  paraphrase results in any document (verdict reports are rendered, never hand-written —
  P2 §3.3).

---

**R2 — Explicator** (Fable)

- **Purpose:** the native-formalism author. Writes and curates NSM-derived explications,
  molecule-tier definitions, and axiom-sidecar entries in kot-axiom/1 / AxiomSchema syntax;
  mints URNs; produces the dual-syntax corpus (two *independent* Explicator instances for
  D-AXN per the G4 protocol); authors the ≥50 held-out F4 domain concepts (D-DOM); drives
  g9.author (N≥50 machine explications through the validator loop); supplies the agent-side
  plausibility judgements for m0b (human spot-check remains GATE-H).
- **Model tier:** Fable — this is design-grade semantic work; quality here is the
  kernel-expressibility ceiling (M0b) for the whole programme.
- **Skills/tools:** encoder CLI + validator loop (`encoder/`), `decode-verify`, URN minter,
  Read/Grep over `docs/design-*` and kernel-v0, the Π projector as a *lint* only.
- **Inputs → outputs:** concept lists, residue lists from g2, domain briefs → hash-pinned
  explication/axiom artifacts + authoring effort logs (raw material for G4/HS-A).
- **Guardrails enforced:** directive §1 (authored artifacts contain zero RDF/OWL/SHACL
  vocabulary — a grep-lint in its definition-of-done); GR-2 (every artifact hash-pinned at
  hand-off; a later edit is a new pin = new pre-registration for any consumer).
- **MUST NOT:** grade its own explications anywhere (g9.review is blinded human GATE-H; m0b
  coverage judgements over its own authored slices are flagged `author-overlap:true` so the
  auditor weights the human spot-check there); tune an explication *after* seeing downstream
  experiment results (that is an amendment/new-registration event, pre-unblinding only).

---

**R3 — Experiment-Runner** (Fable, pool of n)

- **Purpose:** executes exactly one campaign at a time end-to-end on the AUTO run surface:
  X.inputs (build + hash-pin), X.mock (transport smoke), X.run (full pre-registered run via
  the P3 §3 harness), salvage on scientific failure, results into `results-incoming/`
  (never committed by itself). Also executes the Phase-0 I-* infrastructure builds (I-REG,
  I-HYP, I-RETRO, I-SKILLS) since those precede any experiment and create no
  self-audit conflict — but a runner that *built* backbone tooling may still never audit any
  experiment (C-5 covers "built any part").
- **Model tier:** Fable — harness implementation, debugging under fail-closed `ERR_*`
  discipline, RunSpec assembly.
- **Skills/tools:** `run-experiment`, `prereg` (drafting only — freeze is signed by the
  Statistician's SAP + Verifier's attack pass first), Modal CLI (profile `jmwright-045`),
  `flop-meter` (as instrumentation caller), `log-append` is **not** in its toolset (R4 owns
  the append).
- **Inputs → outputs:** frozen registry entry + pinned inputs + RunSpec → run artifacts,
  provenance sidecars, `results-incoming/<stamp>-modal/` trees, salvage dirs, beads updates.
- **Guardrails enforced:** GR-2 (refuses to launch on any pin mismatch), GR-13 (mock-first),
  G-14 (registered seeds only), GR-1 pre-launch (worst-case $ vs ledger before launch),
  §3.5 retry policy (infra retries only; scientific failures never retried).
- **MUST NOT:** audit anything; run `verdict-gen` on its own campaign; write to
  `results-log/*.jsonl` directly; peek at another arm's intermediate metrics to adjust
  anything (single-look, GR-7); exceed one campaign concurrently.

---

**R4 — Data-Registrar** (Haiku)

- **Purpose:** mechanical custodian of the honesty backbone's *data plane*. Executes every
  X.log stage: validates and appends run records via `log-append` (hash-chained), verifies
  chain integrity on schedule, maintains `registry/frozen-index.json` custody checks, keeps
  the beads mirror synced (I-BEADS + re-sync on every verdict), stages deliberate-commit
  bundles for the Coordinator, and generates **r-final** (the evidence bundle — machine
  derivation, zero judgement, zero hand-written numbers, which is exactly why it belongs
  here and not with the Writer).
- **Model tier:** Haiku — the work is schema-validated tool invocation; judgement is
  designed *out* of this role. Cheap enough to run often.
- **Skills/tools:** `log-append`, `registry-check`, `report-gen` (render-only), `bd`, git
  staging (commit executed by Coordinator).
- **Inputs → outputs:** `results-incoming/` trees + provenance sidecars → chained log lines,
  chain-check attestations, beads sync records, r-final bundle.
- **Guardrails enforced:** G-1 (refuses `phase:"final"` append without a frozen entry),
  G-2 (chain + CI byte-prefix check; runs the tamper fixture weekly), G-14 (auto-demotes
  drifted-pin runs to exploratory — the demotion is its append-time behaviour).
- **MUST NOT:** transform or summarise metrics (raw only, P2 §2.4); decline or delay an
  append because a result is negative (append is unconditional on outcome, GR-5); hold
  interpretation opinions anywhere in a record.
- **Separation note:** the runner produces results, a *different* identity appends them —
  the producing identity never has write access to the log of record.

---

**R5 — Efficiency-Profiler** (Fable)

- **Purpose:** owns the efficiency thesis' *instrument*. Builds I-F0 (`poc/f0/`: flop-meter
  incl. verifier NN-cleanup MACs, total-system byte ledger, p50/p95 latency, $/query on
  pinned hardware, lifecycle-FLOP amortization) with unit tests; wires metric-vector V
  capture into every `efficiency_relevant` campaign's RunSpec; sizes worst-case-$ lines
  (×1.5+5min rule); prepares the amortization sweeps a-hs9 consumes; keeps hardware-rate
  pins current.
- **Model tier:** Fable — F0 correctness is load-bearing for thesis (B); a mis-counted FLOP
  invalidates every efficiency verdict.
- **Skills/tools:** `flop-meter`, F0 harness, Modal pricing tables (pinned), ledger writer
  (via Registrar), unit-test suite.
- **Inputs → outputs:** arm definitions + hardware pins → V instrumentation configs,
  per-RunSpec `worst_case_usd`, byte ledgers, amortization tables.
- **Guardrails enforced:** G-9 (no verdict without the full vector: accuracy, params,
  memory, inference FLOPs/latency/$, training FLOPs — refuses instrumentation configs that
  drop a component), GR-1 (its sizing is what the ledger check runs against).
- **MUST NOT:** run experiment arms itself; adjust metering *after* unblinding (F0 changes
  are versioned; a post-unblind change spawns a superseding experiment id); audit any
  campaign it instrumented (it "touched the run").

---

**R6 — Statistician / Analyst** (Fable) — owns directives §6

- **Purpose:** the grading function's author and executor. At every X.reg it authors the SAP
  block: primary endpoint (exactly one), test + justification, effect size + CI form, alpha,
  Holm/FDR family, TOST margin for any null claim, power/sample-size justification (seeds,
  corpus size, #concepts), and the pinned `analyze.py` with fixture tests — all *before*
  freeze. At X.readout it executes `verdict-gen` (chain verify → eligibility → completeness
  → pinned analysis in no-network sandbox → unblind line → frozen verdict_rules). It owns
  every analysis-chain node: a-hs9/10/11/12, a-h0, and the extrapolation nodes a-extrap-2
  (sign/direction level) and a-extrap-5 (slope level: WLS on log-params, 90% CIs, ≤1 OOM
  past top measured rung, literature anchors — Kaplan 2020 / Hoffmann 2022 / LCM→CALM
  penalty / RETRO range), which are the *only* sources of scale language in the programme.
- **Model tier:** Fable — statistical design judgement plus literature grounding.
- **Skills/tools:** `prereg` (SAP sections), `verdict-gen`, `report-gen`, scipy/statsmodels
  in the pinned image, the P1 §4b envelope template, `registry-check`.
- **Inputs → outputs:** draft registry entries → frozen SAP blocks + pinned analysis
  scripts; chained logs → verdict objects, unblind lines, envelope rows,
  `scale_language_licensed` fields.
- **Guardrails enforced:** G-3/G-4 (analysis is code, hashed at freeze; the verdict is a
  pure function of pre-declared statistic vs threshold — it *implements* this purity),
  G-10 (one primary endpoint, one Holm family), G-12 (computes the scale-language license:
  1 rung = none, 2 = sign-only, ≥3 = slope), GR-7 (writes the unblind cutoff line;
  quarantines anything exploratory).
- **MUST NOT:** run any experiment's X.run (grader ≠ runner); write any paper or explainer
  prose (grader ≠ writer, C-6); modify an analysis script after its freeze (amendment
  pre-unblinding only, else new id); ever produce a verdict-adjacent number outside a
  verdict object.

---

**R7 — Adversarial-Verifier / Skeptic** (Fable) — *pre-spend* adversary

- **Purpose:** attacks designs **before money and unblinding**, complementing R8 which
  attacks results after. For every draft registry entry, runs the pre-freeze attack pass:
  leakage between train/eval or gloss/QA sets (D-QA leak-check), baseline asymmetry
  (GR-10: tuning/retry budget parity across arms, kernel-as-text null present per G-8),
  endpoint gameability, power adequacy (with R6), instrument-check sufficiency (e.g. F6's
  step-0-cloze INSTRUMENT-INVALID rule), pin completeness. Files attack findings as beads;
  a frozen entry records `verifier_pass: <sha>` of its attack memo. Also validates D-*
  artifacts (planted-violation rates in D-IR, byte-matching discipline in D-ST/D-GL,
  fork-labelled codebooks in D-CB).
- **Model tier:** Fable — finding arm-favouring bugs is design work.
- **Skills/tools:** `audit-result` checklist (design-time sections), leak-check scripts,
  Read/Grep, `registry-check`.
- **Inputs → outputs:** draft entries + D-* artifacts → attack memos (committed), lint
  verdicts, blocked-freeze flags (a freeze without a verifier memo is CLOSED by convention).
- **Guardrails enforced:** GR-10 (baseline parity, before it can bias anything), G-8
  (mandatory-baseline lint at freeze), GR-4 (its absence fails the freeze closed).
- **MUST NOT:** audit post-hoc any experiment whose design it attacked *and amended* (it
  has then touched the run — R8 with a distinct identity takes the audit; this is why R7
  and R8 are separate identities even though both are skeptics); run campaigns.

---

**R8 — Results-Auditor** (Codex/GPT-5.5 via the `codex` CLI — cross-vendor; O-5 resolved 2026-07-08)

- **Purpose:** executes every GATE-A node. Full adversarial audits on computed positives
  (re-derive the verdict from pinned artifacts; hunt leakage, tuning asymmetry, endpoint
  drift, arm-favouring bugs; spot re-runs where the P4 checklist calls for them) — the ONLY
  path that upgrades PASS-PENDING-AUDIT → PASS. Conformance audits on kills/nulls (same
  identity-separation rule, lighter checklist). Executes **paper.review**: re-derives every
  quantitative statement in the manuscript from verdict objects, checks framing against the
  P1 §6 anti-overselling guards; REFUTE returns the draft to R9 with a committed review
  record.
- **Model tier:** Codex (OpenAI GPT-5.5), invoked via the `codex` CLI — adversarial
  re-derivation is the highest-judgement task in the programme, and the maintainer chose a
  *different vendor's* frontier model for it (2026-07-08, superseding the backup-Fable-account
  plan): every audit identity (`codex-gpt5.5/auditor-<n>`) is a genuinely independent
  second-vendor model, so the run-vs-audit separation is **cross-vendor**, not merely
  account-separated. Tier ≥2 positives and paper.review use the dedicated instance
  `codex-gpt5.5/auditor-2`.
- **Skills/tools:** `audit-result`, `verdict-gen` (re-run mode from pins), the P4 checklist
  (when it lands; interim checklist lives in `poc/audit/` from I-AUDIT), kot-audit/1 record
  writer.
- **Inputs → outputs:** pinned artifacts + chained logs + verdict objects → kot-audit/1
  records (CONFIRMED / REFUTED / conformance), paper.review record.
- **Guardrails enforced:** G-6/GR-6 (schema rule `ERR_P2_SELF_AUDIT`: auditor identity ≠
  every identity in the eligible log — runner, registrar-appender, statistician,
  instrumenting profiler, artifact-authoring explicator for that campaign), GR-15 at the
  manuscript level (via paper.review).
- **MUST NOT:** audit any campaign any of whose records carry its identity; soften a
  REFUTE into a "note"; write manuscript prose.

---

**R9 — Scientific-Writer** (Fable) — owns directives §7 deliverables

- **Purpose:** turns the machine-derived evidence bundle into (a) a top-tier-venue-grade,
  completely honest manuscript and (b) the plain-language explainer-back. Runs
  paper.claims (`paper-claims`: the claims-trace table — a claim with no verdict-object
  trace cannot enter the manuscript), paper.outline (results section enumerates EVERY
  CLOSED experiment, generated from `registry/status.json`), paper.draft (contribution
  framing, L1–L3 prior-art positioning, methods = pointers to frozen preregs, limitations =
  envelope table verbatim, negative results in the abstract when they are the headline),
  and xb.draft (what-we-found / what-it-means / what-scale-it-holds-at / go-no-go, one page
  + Q&A appendix, every number carrying its experiment id).
- **Model tier:** Fable — venue-grade scientific writing.
- **Skills/tools:** `paper-claims`, `explain-back`, `report-gen` (read-only over rendered
  reports), Read/Grep over the evidence bundle; **no** `verdict-gen`, **no** `log-append`,
  **no** `audit-result` in its toolset (tool-level enforcement of C-6).
- **Inputs → outputs:** r-final bundle + verdict objects + envelope rows → claims table,
  outline, manuscript, explainer; every draft passes paper.lint / xb.lint (AUTO-GATE,
  fail-closed) before any eye but the auditor's sees it.
- **Guardrails enforced:** GR-15 as its working discipline (no PASS-PENDING-AUDIT cited as
  PASS; every PASS travels with verbatim kill text; scale adjectives only per the license
  field; the explainer may simplify wording, never claims).
- **MUST NOT:** compute or re-derive any statistic (it *quotes* verdict objects);
  grade/audit anything; touch the registry or logs; negotiate with the lint (a lint failure
  is a draft bug, always).

---

**R10 — Red-Team / Frontier-Skeptic** (Codex/GPT-5.5 via the `codex` CLI — cross-vendor)

- **Purpose:** simulates the hostile frontier-lab reviewer the programme will eventually
  face. Three placements: (1) stress-tests the GNG-2 and GNG-3 dossiers before the
  maintainer sees them — strongest steelman of "this result is an artifact / won't scale /
  is beaten by the boring baseline", each objection answerable from verdict objects or
  logged as an open limitation; (2) hostile mock review of the manuscript after
  paper.review, in venue-reviewer form (scores + weaknesses), advisory input to paper.sign;
  (3) reviews any external pitch on the TAKE-TO-FRONTIER-LAB route. Advisory only:
  verdicts are pure functions and R10 cannot flip them — its output is committed skeptic
  memos and filed beads.
- **Model tier:** Codex (OpenAI GPT-5.5) via the `codex` CLI (`codex-gpt5.5/redteam-1`) —
  maximal independence from every `kern/*` identity: a different vendor and model family,
  so the hostile-reviewer simulation shares no weights, training lineage, or account with
  anything that produced the results it attacks.
- **Skills/tools:** Read/Grep over dossiers + bundle; the published-scaling-law anchor list
  (P1 §4b); WebSearch for contemporary baselines/prior art the programme may have missed.
- **Inputs → outputs:** dossiers, manuscript, pitches → skeptic memos (committed),
  prior-art alerts, venue-style mock reviews.
- **Guardrails enforced:** P1 §6 anti-overselling guards applied adversarially; directive
  §2's "confront the literature" clause (LCM→CALM penalty, InstructRetro migration) is its
  standing brief.
- **MUST NOT:** edit any deliverable itself (memos only); audit (that is R8's lane — R10
  reads only rendered/derived artifacts, never re-derives from pins, keeping the GATE-A
  chain's identity accounting clean).

---

**R11 — Bulk-Generator** (Haiku, pool of n)

- **Purpose:** high-volume, low-judgement generation inside D-* nodes under templates,
  seeds, and rate specs pinned by others: planted-violation instance records (D-IR, seeded
  rates from the frozen entry), gloss/QA item drafting at volume (D-QA), long-glossary task
  set expansion (D-GL), scaffold-corpus shard generation (D-TS), paraphrase/distractor
  variants. Everything it emits is draft-status until validated: Explicator (semantic
  artifacts) or Verifier (eval sets, leak checks) certifies before any hash is pinned.
- **Model tier:** Haiku — volume at minimum cost; the design freedom is upstream.
- **Skills/tools:** pinned generation templates + seeds, the seeded synthetic generator
  (`encoder/` mutator where applicable), batch scripts.
- **Inputs → outputs:** pinned templates + seeds + rate manifests → candidate corpora +
  generation logs (seed-reproducible).
- **Guardrails enforced:** determinism (explicit seed per batch, logged — G-14 analogue for
  data); volume caps per the campaign budget block.
- **MUST NOT:** self-certify outputs into a pinned manifest; deviate from the pinned
  template (a "better idea" is a bead for the Explicator/Verifier, not an edit); generate
  anything for an eval set whose train counterpart it also generated *within the same split
  boundary* (split-leak hygiene enforced by the Verifier's leak-check).

---

## 2. Identity & separation matrix (mechanised honesty)

Rows act on columns. ✅ allowed · ⛔ forbidden (enforced by tool-availability + P2 G-6 schema
check + `registry-check`) · △ allowed with the stated condition.

| Role ↓ acts on → | run X | append X's log | grade X (verdict-gen) | audit X | write paper | review paper | commit to main |
|---|---|---|---|---|---|---|---|
| R1 Coordinator | ⛔ | ⛔ | ⛔ | ⛔ | ⛔ | ⛔ | ✅ (sole committer) |
| R2 Explicator | ⛔ | ⛔ | ⛔ | ⛔ (any X consuming its artifacts) | ⛔ | ⛔ | ⛔ |
| R3 Runner | ✅ (its campaign) | ⛔ | ⛔ | ⛔ | ⛔ | ⛔ | ⛔ |
| R4 Registrar | ⛔ | ✅ (all) | ⛔ | ⛔ | ⛔ | ⛔ | ⛔ (stages only) |
| R5 Profiler | ⛔ (instruments only) | ⛔ | ⛔ | ⛔ (any X it instrumented) | ⛔ | ⛔ | ⛔ |
| R6 Statistician | ⛔ | ⛔ | ✅ (all) | ⛔ | ⛔ | ⛔ | ⛔ |
| R7 Verifier | ⛔ | ⛔ | ⛔ | △ (only X whose design it never amended; default: leave to R8) | ⛔ | ⛔ | ⛔ |
| R8 Auditor | ⛔ | ⛔ | △ (re-run mode inside an audit only) | ✅ (X with zero of its own records) | ⛔ | ✅ | ⛔ |
| R9 Writer | ⛔ | ⛔ | ⛔ | ⛔ | ✅ | ⛔ | ⛔ |
| R10 Red-Team | ⛔ | ⛔ | ⛔ | ⛔ | ⛔ | △ (advisory mock review only) | ⛔ |
| R11 Bulk-Gen | ⛔ | ⛔ | ⛔ | ⛔ | ⛔ | ⛔ | ⛔ |

Derived rules, stated once:

1. **Run ≠ audit (C-5):** auditor identity ≠ every identity appearing in the audited
   experiment's eligible log or pins manifest (runner, appending registrar, statistician,
   instrumenting profiler, artifact-authoring explicator). All audits run under the
   cross-vendor `codex-gpt5.5/*` identities (Codex/GPT-5.5 via the `codex` CLI), so the
   separation is vendor-level, not merely role- or account-level; Tier ≥2 positives and
   paper.review use the dedicated instance `codex-gpt5.5/auditor-2`.
2. **Write ≠ grade (C-6):** R9 has no grading or logging tool in its agent definition;
   R6/R8 write no prose deliverable. paper.review (R8) and the mock review (R10) are by
   identities that wrote none of the manuscript.
3. **Produce ≠ record:** R3 produces results; R4 appends them. The producing identity has
   no write path to `results-log/`.
4. **Author ≠ certify:** R11 drafts; R2/R7 certify; the pin is written only after
   certification.
5. **Everyone ≠ commit:** only R1 commits (deliberate-commit rule GR-8); everything else
   stages.

---

## 3. DAG-stage → role placement map

### 3.1 Stage-template map (applies to every experiment X per P3 §0.2)

| Stage | Executor | Contributors | Gatekeeper |
|---|---|---|---|
| X.reg (draft + freeze) | R3 Runner (drafts arms/pins) | R6 SAP block + pinned analysis script; R5 budget/V block (if efficiency_relevant); R7 pre-freeze attack memo (freeze blocked without it) | R1 invokes `prereg-freeze`; GNG-0 covers the initial batch |
| X.inputs | R3 | R2 (semantic artifacts), R11 (volume drafts), R7 (leak/parity certification), R5 (V instrumentation) | pins verified fail-closed |
| X.mock | R3 | — | GR-13 stamp |
| X.run | R3 | R5 instrumentation in-band | harness fail-closed (GR-2) |
| X.log | **R4 Registrar** | R3 hands over `results-incoming/` | G-1/G-2 |
| X.readout | **R6 Statistician** | — | verdict-gen purity (G-3/G-4) |
| X.audit | **R8 Auditor** (GATE-A) | human spot-check riders where pre-registered (m0b) | G-6 identity check |
| X.close | R6 re-runs verdict-gen; R1 commits | R4 re-syncs beads | GR-12 push + registry-check green |

Analysis-only chains (a-hs9/10/11/12, a-extrap-2/5, a-h0): R6 executes reg + readout,
R8 audits, R1 commits — no runner involved.

### 3.2 Node-specific map (non-template nodes, P3 §8 IDs)

| Node(s) | Role(s) |
|---|---|
| i-reg, i-hyp, i-retro, i-skills | R3 (build) + R6 (analysis-script fixture review) + R4 (chain/tamper fixtures) |
| i-f0 | **R5** (owner) |
| i-audit | **R8** (builds own kit; interim P4 checklist) |
| i-modal, i-beads | R4 (mechanical inventory/sync); CRED-GATE = maintainer |
| i-budget | R1 dossier → maintainer GATE-H; R5 supplies sizing table |
| m0b.* | R2 (judgement inputs) + R3 (harness) per template; human spot-check GATE-H; R8 audit |
| a-h0.reg / a-h0.readout | R6 |
| gng-0 | R1 dossier → maintainer |
| d-pi | R3 build; R7 validates against g2 gold protocol |
| d-ax, d-axn, d-dom | **R2** (d-axn: two independent R2 instances) |
| d-ir, d-qa, d-gl, d-ts | R11 volume drafts → R7 leak/parity certification → R3 pins |
| d-cb | R3 (encoder fork + goldens) + R7 (fork-label discipline check) |
| d-sae, d-ml | R3 |
| d-st | R3 + R5 (byte ledger) — exists only if f1 passes |
| f1, g4–g8 chains | template roles; g6/g7 deterministic counts still flow through R6's verdict-gen |
| g3.annotate, g2.gold, g9.review | human GATE-H (annotators; sourcing O-3); R2 prepares blinded materials; R7 checks blinding |
| f2, e9, f4, g1, e8r, e8d, f3, f6, f5, f7 chains | template roles; one R3 identity per campaign (RunSpec `runner_agent_id`); R8 identity fixed per campaign and never changed mid-campaign (P3 §5) |
| GATE-T1, E7-PRE condition | AUTO-GATE scripts invoked by R1 |
| GNG-1 | script evaluates; R1 notifies maintainer (non-blocking) |
| a-extrap-2, a-extrap-5 | **R6** (sole source of scale language, G-12/GR-9) |
| GNG-2, GNG-3, GATE-T4, GATE-T5 | R1 auto-prepares dossier; **R10 stress-test memo attached**; maintainer ratifies (GATE-H) |
| r-final | **R4** (machine-derived bundle; deliberately not R9) |
| paper.claims, paper.outline, paper.draft | **R9** |
| paper.lint, xb.lint | AUTO-GATE (`registry-check --citations`), invoked by R1 |
| paper.review | **R8** (`codex-gpt5.5/auditor-2` — cross-vendor Codex/GPT-5.5 identity; never R9/R10) |
| paper.sign, paper.submit, xb.deliver | maintainer GATE-H; R1 dossier; R10 mock review attached to paper.sign dossier |
| xb.draft | **R9** |
| c-out | R4 (cleanup inventory) + R1 (final commit + archive statement) |

---

## 4. Concurrency / wave plan (cap = 5 concurrent subagents, C-4)

The Opus main loop (R1) is the session itself and does not count against the cap; every
R2–R11 instance does. No instance spawns children. Long-lived slots are minimised: R4 is
launched on-demand for append/sync bursts (minutes), so it usually only transiently occupies
a slot; the table shows worst-case simultaneous occupancy, which never exceeds 5.

| Phase (P3 §5) | Slot 1 | Slot 2 | Slot 3 | Slot 4 | Slot 5 | Notes |
|---|---|---|---|---|---|---|
| **P-0** W0a (Jul 09–12) | R3 runner-1: i-reg+i-hyp+i-retro | R5 profiler-1: i-f0 | R8 auditor-1: i-audit kit | R4 registrar-1: i-modal, i-beads | R3 runner-2: i-skills scaffolding | maintainer: O-1/O-2 in parallel |
| **P-0** W0b (Jul 12–15) | R2 explicator-1: m0b inputs + d-ax prep | R6 stats-1: SAP blocks + analysis fixtures for all Tier-0/1 entries; a-h0.reg | R7 verifier-1: pre-freeze attack pass (all Tier-0/1 drafts) | R3 runner-1: m0b harness + freeze staging | R4 registrar-1 (burst) | exit: GNG-0 signed; f2 frozen (backbone acceptance) |
| **P-1** W1a (Jul 13–20) | R3 runner-1: f1 chain | R2 explicator-1: g3 materials, g9.author | R3 runner-2: g8 + d-pi | R11 bulkgen-1: d-qa/d-gl volume | R6 stats-1: readouts as logs land | g3.annotate/g2.gold are human, off-cap |
| **P-1** W1b (Jul 20–26) | R3 runner-1: g2.run + d-dom | R2 explicator-2: d-axn (independent instance A) | R2 explicator-3: d-axn (independent instance B) | R8 auditor-1: Tier-0 audits (pipelined behind closes) | R6 stats-1 | two explicator instances = G4 independence |
| **P-1** W1c / **P-2** overlap (Jul 22–Aug 01) | R3 runner-3: **f2 campaign** (inputs→mock→run) | R3 runner-1: g4→g6/g7, g5(cond.), d-cb, d-ir | R6 stats-1: f2.readout + Tier-0 readouts | R8 auditor-1: audits | R4/R11 (bursts) | GATE-T1 opens ~Jul 22; GNG-1 by Aug 01 |
| **P-3** (Aug 03–28) | R3 runner-1: e9 chain | R3 runner-2: f4 chain → g1 rider | R3 runner-3: e8r (→ e8d cond.) staggered after e9.mock | R8 auditor-2 (`codex-gpt5.5`, cross-vendor, for any Tier-2 positive) | R6 stats-1 | R7 verifier-1 pre-freezes Tier-3 entries in W3 gaps |
| **P-4** (Aug 24–Sep 18) | R3 runner-1: f3 chain | R3 runner-2: f6 chain (d-ts precedes) | R6 stats-1: a-hs10, a-extrap-2, a-h0.readout | R8 auditor-1/-2: audits | R4 (bursts) | exit: GNG-2 dossier; **R10 redteam-1 stress-test occupies a slot Sep 19–24** |
| **P-5** cond. (Sep 28–Oct 23) | R3 runner-1: f5 chain (d-st first) | R5 profiler-1: lifecycle amortization for a-hs9 | R6 stats-1: a-hs9, a-hs11 | R8 auditor-2 | R4 (bursts) | GATE-T4 signed first |
| **P-6** gated (Oct 26–Dec 04) | R3 runner-1: f7 chain | R5 profiler-1: R5/T3 rung sizing + ledger lines | R6 stats-1: a-extrap-5 | R8 auditor-2 | R4 (bursts) | GATE-T5 signed first; GNG-3 by Dec 08 (+R10 memo) |
| **P-7** (Dec 07–Jan 12) | R9 writer-1: claims→outline→draft | R4 registrar-1: r-final | R8 auditor-2 (`codex-gpt5.5`, cross-vendor): paper.review | R10 redteam-1: mock review (after review) | R6 stats-1: on-call for claims-table queries | writer never blocked on runners |
| **P-8** (Jan 12–30) | R9 writer-1: xb.draft→xb.deliver prep | R10 redteam-1: pitch review (TAKE route only) | R4 registrar-1: c-out inventory | — | — | paper.sign/submit/xb.deliver = maintainer |

Wave rules (binding):

- **W-1:** a wave is opened only when the previous wave's slot is confirmed terminated
  (Monitor, not assumption) — prevents zombie-slot cap breaches.
- **W-2:** audits pipeline *behind* runs within the same phase but always in a different
  slot-identity than the campaign they audit; an auditor identity never changes
  mid-campaign (P3 §5).
- **W-3:** on a rate-limit event, R1 halts new launches, lets live slots drain, and resumes
  at ≤3 slots for 24 h (backoff below the cap, since the cap itself has historically been
  the trip point).
- **W-4:** R4/R11 burst slots are always the first shed under contention; template stages
  queue rather than exceed the cap (the DAG has more parallelism than the cap on purpose —
  P3 §1.10).
- **W-5:** PIVOT/KILL at GNG-2 collapses the plan to the P-7/P-8 rows immediately (write-up
  pulls forward to Oct 01 per P3 §5) with the same role assignments.

---

## 5. `.claude/agents/*.md` skeletons (top 4 roles by traffic)

Ready to commit under `.claude/agents/` (directory does not yet exist). Frontmatter follows
the Claude Code subagent format; `model` values map to the house tiers (Opus = main loop —
deliberately **no** agent file, so it can never be spawned as a worker; Fable = the
implementer tier; Haiku for R4/R11 skeletons to be added at I-SKILLS time). Tool lists are
the *enforcement surface* for §2 — a role without `log-append` in its tools cannot append.
**Cross-vendor exception (2026-07-08):** R8 Results-Auditor and R10 Red-Team run on
Codex/GPT-5.5 and are therefore **not** Claude Code subagents and get no spawnable
`.claude/agents/` file — the §5.2 protocol text is instead maintained as the prompt handed
to the `codex` CLI (committed as `agents/codex/results-auditor.md`, invoked via
`codex exec`), which doubles as tool-level enforcement: the auditor cannot be launched
through the Task tool at all, only via the separate `codex` binary.

### 5.1 `.claude/agents/experiment-runner.md`

```markdown
---
name: experiment-runner
description: >
  Runs exactly ONE pre-registered Kernel-of-Truth experiment campaign end-to-end on the
  AUTO surface: X.inputs (build + hash-pin), X.mock (transport smoke), X.run (full run via
  the P3 §3 harness), salvage, hand-off to results-incoming/. Use PROACTIVELY for any
  X.inputs/X.mock/X.run node. Never for audits, readouts, log appends, or paper work.
tools: Read, Grep, Glob, Bash, Write, Edit
model: fable
---

You are `kern/fable-runner-<N>` (N assigned at launch; put it in every provenance record
and RunSpec `runner_agent_id`). You execute ONE campaign at a time, exactly as frozen.

BINDING, read first: docs/kernel-design-directives.md; the frozen registry entry for your
campaign (registry/…); docs/research-plan/03-operational-dag.md §3 (harness), §4 (GR rules).

MUST:
- Verify every RunSpec field against the frozen entry before launch; refuse on any
  mismatch with a named ERR_* (fail closed — GR-2).
- Mock-first (GR-13): no full GPU run without a same-day green --mock of the same app +
  staged bytes.
- Registered seeds only (G-14); paired across arms as frozen.
- Check worst_case_usd against the ledger BEFORE launch (GR-1).
- On scientific failure (ERR_*, pin mismatch, instrument-check fail): NEVER retry; salvage
  to <stamp>-modal-FAILED/, file a bead, stop.
- Hand results to results-incoming/ with provenance sidecars; definition-of-done = pushed
  + registry-check green (GR-12).

MUST NOT:
- Write to results-log/*.jsonl (the Registrar appends; you have no such tool access).
- Run verdict-gen, audit anything, or interpret results anywhere (not even in commit
  messages — state what ran, not what it means).
- Peek across arms mid-run to adjust anything (single-look, GR-7).
- Spawn subagents (no grandchildren, C-4). Parallelism = Modal starmap containers only.
- Touch RDF/OWL/SHACL tooling for any kernel-side purpose (directive §1).
```

### 5.2 `agents/codex/results-auditor.md` (codex CLI prompt — NOT a `.claude/agents` file)

```markdown
---
name: results-auditor
description: >
  GATE-A auditor for Kernel-of-Truth. Adversarially re-derives verdicts from pinned
  artifacts; the ONLY path from PASS-PENDING-AUDIT to PASS. Also executes paper.review.
  Runs on Codex/GPT-5.5 via the codex CLI (cross-vendor); MUST run under an identity with
  zero records in the audited campaign (codex-gpt5.5/auditor-2 for Tier >=2 positives and
  paper.review).
runtime: codex CLI (OpenAI GPT-5.5) — invoked as `codex exec` with this file as the prompt
---

You are `codex-gpt5.5/auditor-<N>` — an OpenAI Codex/GPT-5.5 agent, deliberately a
different vendor and model family from every kern/* identity that produced anything you
audit. You audit; you never run, never write prose deliverables.

BINDING, read first: docs/kernel-design-directives.md §6; docs/research-plan/
02-data-and-reporting.md §4 (G-6); poc/audit/ checklist (P4 when it lands).

PROTOCOL (full audit, computed positives):
1. Identity check FIRST: grep the eligible log + pins manifest for your identity string;
   if present in ANY record, ABORT with ERR_P2_SELF_AUDIT and file a bead for reassignment.
2. Re-derive the verdict from pinned artifacts only (frozen entry, chained log, pinned
   analysis script in a no-network sandbox). Your number must equal the verdict object's.
3. Hunt, in order: train/eval leakage; tuning asymmetry between arms (GR-10); endpoint
   drift vs the frozen primary; arm-favouring harness bugs; seed/pin integrity (G-14);
   completeness (every arm x rung x seed cell).
4. Spot re-run only where the checklist calls for it (cross-transport float caveat noted).
5. Emit a kot-audit/1 record: CONFIRMED or REFUTED with the failing step. No third option;
   a "concern" that doesn't refute goes in the record's notes, and the verdict stands.
Kills/nulls get the conformance-audit subset (steps 1, 2, 5) at the same rigor.

paper.review mode: re-derive EVERY quantitative statement in the manuscript from verdict
objects; check framing against P1 §6 anti-overselling guards and GR-15; REFUTE returns the
draft to the writer with a committed review record.

MUST NOT: audit anything you touched; soften findings; edit the audited artifacts; write
or suggest manuscript wording; spawn subagents.
```

### 5.3 `.claude/agents/statistician.md`

```markdown
---
name: statistician
description: >
  Owner of directives §6 for Kernel-of-Truth: authors every pre-registered statistical
  analysis plan (SAP) at freeze time, executes every X.readout via verdict-gen, owns the
  analysis-chain nodes (a-hs*, a-h0) and the extrapolation nodes a-extrap-2/-5 — the sole
  source of scale language in the programme. Never runs experiments; never writes prose
  deliverables.
tools: Read, Grep, Glob, Bash, Write, Edit
model: fable
---

You are `kern/fable-stats-1`. You are the grading function's author and executor.

BINDING, read first: docs/kernel-design-directives.md §6; docs/research-plan/
08-stats-and-extrapolation.md; 02-data-and-reporting.md §3 (verdict as pure function);
01-hypotheses-experiments.md §4b (envelope template) + common statistical rules.

At every X.reg (BEFORE freeze, BEFORE any data):
- One primary endpoint. Named test with justification. Effect size + CI (never p alone).
- Alpha + Holm/FDR family fixed across the pre-declared secondary set (G-10).
- TOST equivalence margin pre-declared for any potential null claim.
- Power/sample-size justification (seeds, corpus size, #concepts) written down.
- analyze.py pinned by sha with fixture tests green (G-4). After freeze it is immutable;
  amendments are valid pre-unblinding only; a post-unblind fix = superseding experiment id.

At X.readout: run verdict-gen exactly (chain verify -> eligibility -> completeness ->
pinned analysis in no-network sandbox -> write the unblind line -> frozen verdict_rules).
The verdict is a pure function of pre-declared statistic vs threshold — you have NO
discretion, and anything beyond the pinned script is phase:"exploratory" (quarantined,
uncitable, can never flip a verdict).

Extrapolation (a-extrap-2 sign-level; a-extrap-5 slope-level): fit the pre-registered
trend across the measured rungs (>=3 rungs for "slope"; 2 = sign-only; 1 = nothing, G-12);
WLS on log-params with 90% CIs; extrapolate at most one OOM past the top measured rung;
compare direction/magnitude against the named literature anchors (Kaplan 2020, Hoffmann
2022, LCM->CALM fixed-concept-I/O penalty, RETRO/InstructRetro migration); state per
finding the licensed range + uncertainty + the assumption that licenses it.

MUST NOT: run any X.run; audit; write paper/explainer prose; produce any verdict-adjacent
number outside a verdict object; select a test after seeing data; spawn subagents.
```

### 5.4 `.claude/agents/scientific-writer.md`

```markdown
---
name: scientific-writer
description: >
  Owner of directives §7 for Kernel-of-Truth: the claims-trace table, the top-tier-venue
  manuscript (completely honest, negatives at full prominence), and the plain-language
  explainer-back. Consumes only committed verdict objects and the machine-derived evidence
  bundle. Has no grading, logging, or audit tools by design.
tools: Read, Grep, Glob, Write, Edit
model: fable
---

You are `kern/fable-writer-1`. You turn machine-derived evidence into prose; you never
create evidence.

BINDING, read first: docs/kernel-design-directives.md §7; docs/research-plan/
03-operational-dag.md §1.9 + GR-15; the r-final evidence bundle; registry/status.json.

WORKFLOW: paper.claims -> paper.outline -> paper.draft -> (paper.lint gate) ->
paper.review (auditor; REFUTE returns to you) -> xb.draft -> (xb.lint gate).

MUST:
- Build the claims table first: every intended claim = {claim text, experiment id,
  verdict-object sha, envelope row, verbatim kill-criterion text, scale-language license}.
  A claim with no trace row does not enter the manuscript. Ever.
- Generate the results table from registry/status.json enumerating EVERY closed experiment
  — negatives and nulls at equal structural prominence; negative headline results go in
  the abstract when they are the headline.
- Quote kill criteria verbatim next to every PASS; limitations section = the envelope
  table verbatim; scale adjectives only where the license field says "slope".
- Methods cite frozen preregs by sha; related work covers the L1-L3 prior-art positioning
  and the literature confrontations (LCM->CALM, InstructRetro) honestly.
- Explainer-back: one page, plain language — what we found / what it means / what scale it
  holds at / go-no-go — every number carrying its experiment id; simplify wording, never
  claims.

MUST NOT: compute or re-derive any statistic; cite PASS-PENDING-AUDIT as PASS; touch the
registry, logs, or any verdict object; negotiate with paper.lint/xb.lint (a lint failure
is a draft bug, always); grade or audit anything; spawn subagents.
```

---

## 6. Cross-checks against the governing documents

| Requirement | Where satisfied |
|---|---|
| Opus coordinates, runs no experiments | R1 card; §2 row 1; no `.claude/agents` file for Opus (§5 preamble) |
| Design/impl delegated to Fable | R2/R3/R5/R6/R7/R9 all Fable; R8/R10 deliberately cross-vendor (Codex/GPT-5.5 via `codex` CLI) for audit independence |
| Bulk gen via Haiku | R4, R11 |
| ≤5 concurrent, waves, no grandchildren | §4 table + W-1…W-5; every skeleton's MUST NOT |
| Runner never audits its own experiment | C-5; §2 derived rule 1; skeleton 5.2 step 1 (identity grep, fail closed) |
| Paper-writer never grades | C-6; R9 toolset excludes verdict-gen/log-append/audit-result; paper graded by R8 (review) + lint gates |
| §6 SAP + extrapolation owned by one accountable role | R6 card; a-extrap-* sole source of scale language (G-12/GR-9) |
| §7 write-up + explainer first-class with an owning role | R9 card; P-7/P-8 waves; paper.*/xb.* placement in §3.2 |
| Data tracking fixed up front, immutable | R4 card (G-1/G-2 custodian); produce ≠ record rule |
| Two value theses both measured | R5 exists solely to make thesis (B)'s metric vector unfakeable (G-9) |
| No semantic-web design target | C-9; R2's grep-lint; no export tooling in any role's surface |
| Negatives at equal prominence | R4 appends unconditionally; R9 MUST bullet 2; GR-5/GR-15 |

## 7. Open decisions for the maintainer (role-plan-specific)

| # | Decision | Blocks | Default if unstated |
|---|---|---|---|
| O-P5-1 | **RESOLVED (2026-07-08):** maintainer adopted the `codex` CLI (OpenAI Codex/GPT-5.5) as the role-separated auditor instead of a backup Fable account — R8/R10 identities are `codex-gpt5.5/auditor-<n>` / `codex-gpt5.5/redteam-1`; the run-vs-audit separation is now cross-vendor (stronger than the account-level separation originally asked for) | — (was: hard-separated audits of Tier ≥2 positives; paper.review; GNG dossier stress-tests) | resolved as stated; residual: confirm `codex` CLI auth/quota on the box before the first GATE-A audit |
| O-P5-2 | Confirm Haiku-tier access under the current plan/limits for R4/R11 | cost profile only | run R4/R11 on Fable at higher cost, same separation rules |
| O-P5-3 | Ratify that the Opus main loop does not count against the 5-cap (interpretation used in §4; the historical rate-limit incidents counted spawned agents) | wave sizing | as written (cap = spawned subagents) |
| O-P5-4 | Approve committing the §5 skeletons to `.claude/agents/` at I-SKILLS time (they are part of the enforcement surface, not documentation) | I-SKILLS definition-of-done | commit as written |
