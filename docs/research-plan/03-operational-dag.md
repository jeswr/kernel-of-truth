# P3 — Operational DAG, automation boundary, execution harness, guardrails, timeline

**Status:** operational plan for maintainer sign-off, 2026-07-08 (rev 5 — agentic-pace
re-base per maintainer direction 2026-07-08: §5 timeline recompressed — agent development
is not the bottleneck; the long poles are human gates, GPU-run queues, and external
compute-access lead time; O-3 annotator sourcing DEFERRED (Amazon Mechanical Turk the
leading paid option, decided near the annotation stage); Tier-0 + Tier-1 spend AUTHORIZED
now, post-F2 infra/provider fields deferred to each tier's spend-gate (P6). rev 4 — verifier pass:
RT-7c `d-ir-n` natural-violation secondary corpus node added and wired into e9.inputs
(planted D-IR stays the powered primary; P1 HC2, P6 H-4); RT-18 M0 milestone slipped
Jul 15 → Jul 22; identity strings aligned to P2 §1.2 constraint 10 pseudonyms (RT-14).
rev 3 — P7 red-team
pre-freeze fixes applied: RT-1 STOP-AND-PUBLISH-UNDECIDED route + replication-buy cap, RT-3
extraction instrument gates + `10-model-record-interface.md`, RT-6 lineage semantics, RT-7
NICHE-SCOPE coverage gate + external eval slice, RT-8 canonical budget caps, RT-13
family-h0 Holm nodes, RT-4 g2 n=500. rev 2 — reconciled with the
final P2 backbone; adds the directives-§6 analysis nodes, the directives-§7 WRITE-PAPER and
EXPLAIN-BACK phases as first-class gated nodes, and the machine-parseable task list in §8).
Component P3 of the research plan (`docs/research-plan/`). Governed by
`docs/kernel-design-directives.md` (binding). Companion to `01-hypotheses-experiments.md`
(P1 — the hypothesis/experiment suite this document operationalises) and
`02-data-and-reporting.md` (P2 — the honesty backbone whose tools, paths, verdict vocabulary
and guardrail IDs G-1…G-14 are used here verbatim). P4 (skills + audit checklist) implements
the verbs named here.
**Author:** Fable planning agent (P3), for @jeswr. Coordination: sparq-org/sparq#1683.

Scope: this document turns P1's experiment suite into a fully-specified execution plan —
(1) the complete step+dependency DAG including the §6 statistical/extrapolation analysis
nodes and the §7 write-up + explainer-back nodes, (2) the automation-vs-human-gate boundary,
(3) the execution-harness design (Modal profile `jmwright-045` primary; AWS `poc/gpu/`
secondary), (4) the self-guardrails as enforceable operational rules, and (5) a phased
timeline with P1 §5/§6 go/no-go gates placed on calendar, ending at the paper and the
explainer-back.

Nothing here relaxes P1 or P2: every kill criterion, statistical rule, baseline requirement,
and scale-rung obligation in P1 is inherited verbatim; every record, freeze, log line and
verdict flows through P2's tools (`prereg-freeze`, `log-append`, `verdict-gen`,
`registry-check`). Where this document says "run experiment X", it means "run X exactly as
pre-registered in P1 §§1–4 and FROZEN in the P2 registry". RDF/OWL/SHACL/DL do not appear in
this plan except inside G1's comparison-lens arm (a statistical-baseline arm, per P1 HS1) —
no export tooling is scheduled; none is a milestone; nothing semantic-web-shaped is a
destination.

---

## 0. Conventions used by the DAG

### 0.1 Node grammar

Every node row is `ID | title | type | deps | output artifact`. IDs are stable, lowercase in
the machine-parseable list (§8), and are mirrored 1:1 into beads (`bd`) issues with
dependency edges (node `I-BEADS`); §8 is the source of truth, beads is the live tracker.
Node *doneness* is derived, never asserted (P2 §5.2): an experiment node is done iff
`registry/verdicts/<id>.json` exists with a terminal verdict AND the rendered report is
committed. **Lineage rule (P2 §1.4, RT-6):** where an experiment has been superseded
(`f2-rev2`, `supersedes: f2`), every gate, tree expression, and dossier reads the **latest
ID in the lineage**; the verdict object embeds the full lineage and dossiers render
predecessor verdicts adjacently; a FAIL→PASS flip requires the full adversarial audit plus
a red-team memo; a lineage is capped at 2 revisions — reaching the cap forces the
STOP-AND-PUBLISH-UNDECIDED treatment for that mechanism.

**Node types:**

| Type | Meaning |
|---|---|
| `AUTO` | Fully automatable; an agent executes it end-to-end with no human in the loop, within the standing budget caps and guardrails of §4. |
| `AUTO-GATE` | A machine-evaluated gate: a script evaluates pre-registered conditions (pins, budget, prior verdict objects) using the P2 §3.1 expression grammar over `registry/verdicts/*.json`, and **fails closed** — if the check cannot be evaluated, the gate is shut. No human needed when it passes. |
| `GATE-H` | Human gate. Named human (default: maintainer @jeswr) must act — budget approval, credential mint, annotation hours, sign-off, decision. The DAG **blocks** here; no agent may bypass, simulate, or assume the action. |
| `GATE-A` | Audit gate: automatable but **role-separated** — executed by an agent identity distinct from every agent that touched the run being audited (P2 G-6; §4 GR-6). Required to upgrade any `PASS-PENDING-AUDIT` to `PASS`. |

### 0.2 Per-experiment stage template (aligned 1:1 with P2's lifecycle)

Every experiment `X` expands to a standard stage chain. §8 lists every stage explicitly; the
tables in §1 list only deviations and cross-experiment edges.

```
X.reg      AUTO       author DRAFT record; `prereg-freeze` X's P2 registry entry (hypotheses,
                      arms incl. mandatory baselines, one primary endpoint, verdict_rules,
                      analysis-script hash, verbatim kill text, budget block, rungs, seeds);
                      frozen_sha256 into registry/frozen-index.json, externally timestamped
                      (P2 §1.1 post-step) — any later change is an amendment record (design
                      scope: valid only before the first final-phase run record — P2 §1.4)
                      or a NEW experiment id (P2 §1.4 lineage rules)
X.inputs   AUTO       build + hash-pin all inputs (corpora, arm artifacts, eval sets);
                      manifest shas match the frozen pins block
X.mock     AUTO       Modal transport smoke (--mock; ~pennies) — MANDATORY before any full
                      GPU run (GR-13 mock-first rule); R0 experiments skip this stage
X.run      AUTO       full pre-registered run under the harness of §3; arm × rung × seed
                      cells are LOG ROWS inside this stage (not DAG nodes) — completeness is
                      enforced by verdict-gen step 4 (INCOMPLETE-DATA on any missing cell)
X.log      AUTO       every run appended via `log-append` to results-log/<id>.jsonl
                      (hash-chained, append-only; raw metrics only per P2 §2.4) + artifacts
                      committed deliberately from results-incoming/ (never auto-pushed)
X.readout  AUTO       THE STATISTICAL-ANALYSIS NODE: `verdict-gen` verifies the frozen
                      record + chain, selects eligible runs, executes the PINNED analysis
                      script (no-network sandbox; effect sizes + CIs, Holm family, TOST for
                      any null, per P1 common rules), writes the `unblind` log line, then
                      evaluates the frozen verdict_rules — emitting PASS-PENDING-AUDIT /
                      FAIL / NULL / INCONCLUSIVE / INSTRUMENT-INVALID / INCOMPLETE-DATA
X.audit    GATE-A     role-separated adversarial re-derivation from pinned artifacts (P4
                      checklist; named exactly that — never "independent audit" — P2 G-6);
                      REQUIRED to upgrade PASS-PENDING-AUDIT → PASS; kills/nulls get a
                      lighter conformance audit (same identity-separation rule)
X.close    AUTO       re-run verdict-gen after the audit record; commit
                      registry/verdicts/<id>.json + reports/auto/<id>/verdict-<id>.md;
                      verdict quotes M0b coverage + rung + the P1 §4b extrapolation-envelope
                      row verbatim; negatives rendered at full prominence (P2 G-5)
```

Standard intra-template edges: `reg → inputs → (mock →) run → log → readout → audit → close`.
Analysis-only experiments (a-hs9/10/11, a-extrap-*, a-h0 — decided from OTHER experiments'
logs) use the reduced chain `reg → readout → audit → close`.

### 0.3 Roles (who executes which node type)

| Role | Identity | Executes |
|---|---|---|
| **Coordinator** | Opus main loop (Kern) | DAG scheduling, wave launch, deliberate commits, gate dossiers, maintainer comms. Never trains/grades an experiment itself; never spawns sub-sub-agents. |
| **Runner agents** | Fable subagents (≤5 concurrent, waves) | `AUTO` build/run/log nodes. A runner is bound to one experiment campaign at a time; pseudonymous identity string `runner-<n>` in every record (P2 §1.2 constraint 10, RT-14 — account bindings live only in the unhashed `registry/identity-map.json`). |
| **Auditor agent** | Fable subagent under a **distinct identity** from all runners of the audited campaign (`auditor-<n>`; for Tier ≥2 positives the pseudonym is bound to the backup Fable account in the identity-map for hard separation, O-5) | `GATE-A` nodes. Only an audit record can upgrade PASS-PENDING-AUDIT → PASS (P2 G-6). |
| **Writer agent** | Fable subagent, identity distinct from the auditor who reviews the paper (`writer-1`) | Owns the directives-§7 write-up nodes (r-final, paper.\*, xb.\*) — a first-class role, not an afterthought. |
| **Annotators** | Human (sourcing = open decision O-3) | Annotation slices inside G2/G3/G9/M0b (`GATE-H`). |
| **Maintainer** | @jeswr | All budget/credential/sign-off `GATE-H` nodes; GNG decisions; the audience of xb.deliver. |

---

## 1. The complete step + dependency DAG

Human-readable phase tables below; the normative, machine-parseable flat list with every
stage and dependency id is **§8** (that list, not these tables, is mirrored into beads).

### 1.1 Phase 0 — infrastructure & pre-registration freeze (R0, ~$0)

| ID | Node | Type | Deps | Output |
|---|---|---|---|---|
| I-REG | Build the P2 backbone: `registry/schema/` (kot-reg/1, kot-log/1, kot-amend/1, kot-audit/1, kot-verdict/1) + `tools/registry/{prereg-freeze, log-append, verdict-gen, registry-check}`; unit tests incl. the tamper fixture (edited mid-log line must fail the chain check) | AUTO | — | tools + schemas + tests green |
| I-HYP | Generate `registry/hypotheses.json` from P1 §8 (machine-readable hypothesis table; G-8 lint source) and freeze it | AUTO | I-REG | frozen hypotheses table |
| I-RETRO | Retro-import pre-P2 evidence (X0–X4, E1, E2, E5, E8, E9-defl, X1-grounding) as `retro:true` CLOSED records per P2 §5.4 — verdicts transcribed, never regenerated | AUTO | I-REG | retro records; complete status table |
| I-F0 | Build F0 accounting harness `poc/f0/` per `design-efficiency-track.md` §3: flop-meter (incl. verifier NN-cleanup ≈ \|lexicon\|·D MACs), total-system byte ledger, p50/p95 latency, $/query on pinned hardware, lifecycle-FLOP amortization (for HS9); unit tests | AUTO | — | `poc/f0/` + tests green |
| I-AUDIT | Build the P4 audit kit: re-run-from-pins checklist, auditor agent config, kot-audit/1 records wired into verdict-gen step 8 (only a CONFIRMED audit upgrades PASS) | AUTO | I-REG | `poc/audit/` + P4 doc |
| I-MODAL | Verify Modal credentials (profile `jmwright-045`, token in `~/.modal.toml`), rebuild pinned image from `requirements-image.txt`, inventory volumes (`kot-hf-cache`, `kot-e1-work`), run one `--mock` ping; escalate to CRED-GATE if token absent/expired | AUTO (CRED-GATE = GATE-H on failure) | — | transport-ready confirmation + image id |
| I-BUDGET | Initialise the budget ledger (`registry/budget.json`): per-tier hard caps (§4 GR-1 table), spend-to-date, worst-case-committed; deploy the cost-monitor loop (hourly); smoke-test the kill switches against a dummy ledger breach | GATE-H (cap values, O-1) then AUTO | — | ledger + monitor + tested kill switches |
| I-SKILLS | Package the reusable skills mandated by directives §3: `prereg`, `run-experiment`, `flop-meter`, `decode-verify`, `audit-result`, `report-gen` (wraps verdict-gen), plus the write-up skills `paper-claims` (claims-trace generator) and `explain-back` | AUTO | I-REG, I-F0 | `tools/skills/` |
| I-BEADS | Mirror the §8 task list into beads: one issue per node, `bd dep` edges, wave labels; re-synced on every verdict | AUTO | — | beads epic + tree |
| m0b.\* | Kernel-expressibility coverage (P1 §5 required gate): template chain; `.run` = % content-word token mass with a plausible profile-1 explication, stratified by domain, per-rung statement; `.audit` = auditor re-derivation **+ human spot-check of n=100 coverage judgments (GATE-H, ~2 h)**; **`m0b.gate`** (AUTO-GATE, RT-7) then evaluates the pre-declared **NICHE-SCOPE threshold** (maintainer sets X at GNG-0; default 20% of the target task family's content-word mass): coverage < X ⇒ every verdict template renders a NICHE-SCOPE banner and any frontier-pitch route must carry an explicit coverage-growth cost line — a gate with a consequence, not just disclosure | template (R0) + AUTO-GATE | m0b.reg ← I-REG | published, audited coverage number — restated in **every** later verdict (P2 G-7) — plus the evaluated NICHE-SCOPE gate record |
| family-h0.reg | Freeze the F-H0 cross-experiment Holm-family record (P8 C-3; P2 §5.4 `family-<name>.json` machinery): the **8 pre-declared members fixed at freeze**; members not read out (pruned tiers) scored as non-rejections — the family is never data-dependently selected. **a-h0 cannot freeze without this record** (RT-13) | AUTO | I-REG, I-HYP | frozen family record |
| a-h0.reg | Freeze the H0 disjunction-gate record: verdict_rules = the P1 §1 YES/NO patterns **plus the STOP-AND-PUBLISH-UNDECIDED pattern** (RT-1: no mechanism PASS ∧ H0-NO blocked because ≥1 member is INCONCLUSIVE / INSTRUMENT-INVALID after its single, pre-declared replication buy) encoded as P2 expressions over member verdict objects {hc1, hc2, he1…he6 experiment ids}; a repeated F6 instrument failure (after the pre-registered repair) is scored **undetermined-not-supporting** for H0-NO, never as support (RT-19); frozen rules linted against the family-h0 record (P8 C-3) at freeze | AUTO | I-REG, I-HYP, family-h0.reg | frozen h0 gate record |
| **GNG-0** | **Pre-registration freeze:** maintainer signs the registry root (frozen-index sha over all initially-freezable entries + caps) and sets the M0b NICHE-SCOPE threshold (RT-7). Conditional/late entries (e8d, f7, g5, d-st-dependent) freeze later under the same tooling; each later freeze is announced **with its frozen_sha256** on the coordination issue (the external timestamp witness — P2 §1.1). After GNG-0, any change to a frozen entry is an amendment (design scope: valid only before the first final-phase run record — P2 §1.4) or a new pre-registration under the lineage rules, reported as such | **GATE-H** | I-REG, I-HYP, I-RETRO, I-F0, I-AUDIT, I-BUDGET, I-SKILLS | signed freeze record in repo |

`m0b.run` needs only its own frozen entry (P2 G-1), so it proceeds in parallel with GNG-0;
its audited verdict is itself part of the GNG-0/M0 milestone. Freezing `f2` is the
acceptance test of the whole backbone (P2 §5.5).

### 1.2 Data & artifact authoring nodes (mostly Phase 1; all AUTO unless marked)

These are the "author corpus slice / mint URNs / encode vectors / build eval set" nodes.
Every output is hash-pinned and referenced from the consuming experiment's frozen `pins`.

| ID | Node | Type | Deps | Output |
|---|---|---|---|---|
| D-PI | Implement Π projector over explication structure (kernel-v0, 54 records) — G2's instrument | AUTO | GNG-0 | `tools/pi/` + derived-subsumption dump |
| D-AX | Author the working ~20-axiom set in kot-axiom/1 v0 (litmus human/parents/sex, kinship, disjointness batch, molecule-tier axioms); mint URNs; sidecar hash pinned | AUTO (+coordinator review) | GNG-0 | axiom sidecar v0 + sha |
| D-AXN | Author the SAME set in NSM-native AxiomSchema syntax, by two independent author-agents (G4 protocol) | AUTO | D-AX, g2.close (residue list) | dual-syntax corpus + effort logs |
| D-IR | Build seeded instance-record corpus ≥300 with planted cardinality/disjointness/domain violations at known rates (E9-C); generator seed + rates in the frozen entry | AUTO | D-AX | corpus + violation manifest sha |
| D-IR-N | Natural-violation **secondary** sub-corpus (P7 RT-7c; ships inside the E9-C pack): ≥100 naturally-occurring violation candidates mined from **revision-pinned SmolLM2 outputs** (135M/360M) generated under pinned prompts + seeds over the litmus + molecule-tier families; candidates surfaced by broad lexical/structural heuristics — **never by the axiom checker under test** (circularity guard); ground truth by **blind human adjudication** (GATE-H rider, ~2 h, inside the O-3 annotator hours); model ids, prompts, seeds, heuristics, and adjudicated labels all hash-pinned in the pack manifest. Pre-registered Holm-corrected SECONDARY in E9-C — planted D-IR stays the powered primary (P1 HC2, P6 H-4) | AUTO (+GATE-H adjudication rider) | D-AX | secondary sub-corpus + adjudicated labels + shas |
| D-QA | Build F2 definitional-QA eval set: kernel-covered slice + non-covered control slice, leak-checked; gloss corpus + RAG index for arms 2/3/6 | AUTO | m0b.run | eval set + index shas |
| D-XIF | Build the model↔verifier extraction interface + **held-out labelled extraction set** per `docs/research-plan/10-model-record-interface.md` (the S4-contract extension, RT-3): the extraction/decode path, identical output-format affordances for ALL arms, and extraction-failure accounting as **instrument events** (never hypothesis events) | AUTO | GNG-0 | interface impl + labelled set + shas |
| D-EXT | Externally-authored eval slice (RT-7a): definitional/consistency subset of an established public benchmark, filtered to kernel-covered concepts by M0b machinery (the filter is ours, the items are not) — pre-registered secondary in E9 and F2 | AUTO | m0b.run | external slice + sha |
| D-GL | Build F3 long-glossary task sets, d∈{4,16,64} in-context definitions; matched-token compressed/truncated text variants | AUTO | m0b.run | task sets + shas |
| D-DOM | Author F4 onboarding domain: ≥50 held-out concepts (explications validated, URNs minted, vectors encoded under pinned encoder `40e8c8ba…`, JL-projected per X4 pins); E5 adapter reused as-is | AUTO | GNG-0 | domain pack + shas |
| D-CB | Build G1 arm artifacts: (a) random-atom-codebook encoder fork (fresh orthonormal atom rows; own ALGORITHM_VERSION label + own X0-style goldens — a **fork label**, never mutating the pinned mainline), (b) Numberbatch vectors mapped through the same adapter protocol, (c) KGE/OWL2Vec\*-style embedding over the same concept graph (comparison lens only) | AUTO | D-DOM | 3 arm packs + shas |
| D-SAE | Obtain E8-R third-family **residual-stream, site-matched** SAE dictionaries (download if available; else fit — fitting cost inside E8 cap); seed-stability stratification per Paulo–Belrose | AUTO | GNG-0 | SAE packs + shas |
| D-ML | Crawl the 1,000-declaration random Mathlib sample for G8 | AUTO | — | sample + sha |
| D-TS | Build F6 scaffold corpus: concept-heavy distribution (E1 TinyStories pipeline reuse, parity-gated mapper port, 5 paired seeds) + the **explication-text-interleaved data arm** corpus | AUTO | GNG-0 | shard sets + shas |
| D-ST | Build F5 store corpora at 10³/10⁵/10⁶ records + byte-matched compressed text stores (zstd-JCS discipline from F1) | AUTO | f1.close, D-QA | stores + byte ledger |

### 1.3 Tier 0 — R0 experiments (this box, ~$0 + annotator hours)

Template stages apply (no `.mock`; `.run` is CPU on this box, `nice`d). Extra edges only:

| ID | Experiment (hypotheses) | Type notes | Extra deps | Gate/kill effect on the DAG |
|---|---|---|---|---|
| f1.\* | KOTK/2 byte/latency accounting vs best general-purpose-compressed gloss text; store scales 10³–10⁶ (HE5 byte premise) | all AUTO | f1.inputs ← I-F0 | f1 kill ⇒ D-ST/f5 branch **pruned** (GATE-T4 unsatisfiable); byte story dropped from every pitch |
| g3.\* | Semantics-pin annotation study, ~20 concepts × ~10 instances, necessity + sufficiency (HS3) | g3.annotate (= the run stage) is **GATE-H** (2 independent annotators, ~8–10 h); materials build AUTO | — | necessity >10% ⇒ HS2 auto-resolves sidecar-only ⇒ **g5 pruned**, Π demoted to lint |
| g2.\* | Π read-out soundness vs human gold; `promise ⊑ words` recovery; partition-residue check (HS2) | g2.gold = **GATE-H** (**n = 500 gold subsumption judgments**, decidability-powered for the 0.9 Wilson gate per the P2 freeze lint (RT-4); ~12 h, blind adjudication); g2.run ← D-PI | g2.readout ← g3.close (interpretation) | precision <0.9 ⇒ Π = lint; residue list still feeds D-AXN |
| g4.\* | Dual-syntax axiom authoring effort/error + LLM decode-legibility probe (HS4) | AUTO (small LLM $) | g4.inputs ← D-AX, D-AXN | selects axiom authoring surface; g6/g7 unblock |
| g5.\* | Encode-twice margins + RDM delta for axiom-in-vector (HS5) — **conditional**: runs only if HS2 lands Π-as-normative | AUTO | g5.reg ← g2.close(=Π-normative) | confirmation closes NF4; surprise ⇒ new pre-registration |
| g6.\* / g7.\* | Grammar-capacity static counts: AND-under-operator share; apply-clause cap/growth at bulk projection (HS6/HS7) | AUTO (deterministic counts, no test — P1 common rules) | g6.run, g7.run ← g4.run | numeric bounds decide grammar fragment; no downstream block |
| g8.\* | Lean-minting rates: fragment gate ≥1%, verified LLM location ≥80% top-5, round-trip fixed point (HS8) | AUTO ($0–10 API) | g8.inputs ← D-ML | below bounds ⇒ Metamath-only identity stands; independent — schedule opportunistically |
| g9.\* | Authoring capability gate vs DeepNSM-8B (HS-A): N≥50 machine-authored explications through the validator | g9.author AUTO; g9.review = **GATE-H** (blinded human review, ~4 h) | — | not-decisively-better ⇒ why-now weakened; every plan doc reverts authoring-cost estimates |

### 1.4 Tier 1 — F2, the pivot experiment (~$10–60)

| ID | Node | Type | Deps | Output |
|---|---|---|---|---|
| **GATE-T1** | Tier-1 launch gate (machine-checked): GNG-0 signed ∧ m0b.close published ∧ m0b.gate evaluated ∧ I-F0 tests green ∧ I-MODAL ready ∧ ledger worst-case(F2) ≤ Tier-1 cap | **AUTO-GATE** | GNG-0, m0b.close, m0b.gate, I-F0, I-MODAL, I-BUDGET | gate record |
| f2.reg | Freeze F2 entry (HE1 primary; HE2/HC3/HS12 riders; 9 arms + PRM arm + cascade arm 8 + in-decode gating arm + the **gloss-text self-verify + retry at matched budget** gate arm (RT-2: the text-self-check-gated cascade; HE1/HE2 PASS requires the kernel arm to BEAT this arm at matched FLOPs, not just RAG); retry sweep k∈{1,2,4}; rung pairs (R1,R2),(R2,R3)) — the P2 backbone's acceptance test | AUTO | I-REG, I-HYP | frozen entry sha |
| f2.inputs | Pin arm artifacts: PRM model choice (off-the-shelf small RM, matched inference FLOPs), int4-quantized 360M, cascade + logprob-gate + text-self-check-gate impls, verifier loop over the D-XIF extraction interface (X2 machinery, gap on the ledger), D-EXT external eval slice (secondary) | AUTO | f2.reg, D-QA, D-XIF, D-EXT | arm pack + shas |
| f2.mock / f2.iface / f2.run / f2.log / f2.readout / f2.audit / f2.close | Template + **`f2.iface` extraction-failure instrument gate** (RT-3, per `10-model-record-interface.md`): measured extraction-failure rate on the held-out labelled set must clear the frozen bound before any hypothesis read — failures are instrument events (`/gates/instrument_valid`), never hypothesis events, so the verifier arm can harvest neither free wins nor free losses. Then SmolLM2 135M/360M/1.7B, all arms, full metric vector V under F0 | template + AUTO-GATE | f2.mock ← GATE-T1; f2.iface ← f2.mock, D-XIF | HE1, HE2, HC3, HS12 verdicts |
| a-hs12 | Latency analysis, batch-1 + throughput modes (implementation pick; no kill — recorded as HS12 selection in f2 commentary) | AUTO | f2.log | HS12 selection |
| **GNG-1** | F2 pivot readout: the P1 Tier-1 gate text machine-evaluated over `registry/verdicts/f2.json`; maintainer notified with the dossier. F2 clean-kill at both rung pairs ⇒ efficiency thesis shrinks to M6+M4-verifiability (Tier-2/3 efficiency scope narrowed **automatically** in the registry); F2 PASS ⇒ Tier 2 funded aggressively | AUTO-GATE + maintainer notification (informational GATE-H, non-blocking for the Tier-2 correctness track) | f2.close | pivot record + scope update |

### 1.5 Tier 2 — E9-full + E9-C, F4+G1, E8-R→E8-D (~$70–260)

| ID | Experiment | Type notes | Extra deps | Gate/kill effect |
|---|---|---|---|---|
| e9.\* | E9-full: 6 arms (model-alone / RAG-with-citations / hash-pinned gloss dictionary / **gloss-text self-verify + retry at matched budget** (RT-2) / decode-verify / +repair-retry) + **E9-C** constraint arm + text-diff-checker arm + D-EXT external-slice secondary + **D-IR-N natural-violation secondary** (RT-7c: Holm-corrected secondary; planted D-IR stays the powered primary — P1 HC2, P6 H-4); rungs R1, R2 (R3 iff sign) (HC1, HC2, HS11-part). **HC1 PASS requires the kernel arm to BEAT the gloss-text self-verify + retry arm at matched FLOPs**, not just the passive dictionary or RAG. `e9.iface` extraction-failure instrument gate (RT-3, per `10-model-record-interface.md`) precedes any hypothesis read; extraction failures are instrument events, and all arms share the same output-format affordances | template + `e9.iface` AUTO-GATE; scoring by non-LLM rubric or leak-checked judge (E5 discipline) | e9.inputs ← D-IR, D-IR-N, D-QA, D-XIF, D-EXT; e9.mock ← GATE-T1; e9.iface ← e9.mock | e9 kill (incl. E9-C) kills the correctness product story; HC2 fail must name the failing stage (decode vs authoring vs checker) |
| f4.\* | Amortized concept-vocabulary onboarding: 5 arms incl. ToolkenGPT-protocol per-concept embeddings + in-context-text null; R1/R2/R3 (HE4) | template | f4.inputs ← D-DOM; f4.mock ← GATE-T1 | text-null win ⇒ M6 dead; with f2-kill ⇒ most H0-YES routes gone |
| g1.\* | HS1 arms riding on F4: random-atom codebook / Numberbatch / KGE lens; **2 families** (add Qwen2.5-0.5B) | template minus mock (shares F4 harness) | g1.inputs ← D-CB; g1.run ← f4.run (protocol + adapters) | Numberbatch or random-codebook parity ⇒ every performance claim narrows to governance, propagated by report-gen to ALL later verdict texts |
| e8r.\* | E8-R: site-matched residual-stream SAE, third family; sole primary = replication on the seed-stable subset (HC4 leg 1) | template | e8r.inputs ← D-SAE; e8r.mock ← GATE-T1 | fail both new pairs (p≥0.01 vs shuffled) ⇒ A6 shelved; **e8d pruned**; PIVOT route via A6 closes |
| e8d.\* | E8-D: cross-version semantic-regression detection, AUC vs linear-probe baseline (HC4 leg 2) — **conditional**; freezes only after e8r PASS | template minus mock (shares e8r harness) | e8d.reg ← e8r.close(=PASS) | probe parity ⇒ A6 = "alignment above chance, no downstream use" |

### 1.6 Tier 3 — F3, F6, and the Tiers-0–3 analysis nodes (~$100–340)

| ID | Experiment | Type notes | Extra deps | Gate/kill effect |
|---|---|---|---|---|
| f3.\* | Dense concept input: 7 arms (incl. matched-token text ×2, xRAG-style trained compressor at matched training budget, shuffled-kernel), d∈{4,16,64}, R1→R2→R3; **M2-output rider** (≤$20, expected-fail, loss-vs-compute slope) (HE3) | template | f3.inputs ← D-GL; f3.mock ← GATE-T1; f3.run reads f2 verdict (scope note only, non-blocking) | f3 kill ⇒ dense I/O retired for efficiency; **HS10 auto-resolves interface-side**; f5's injection-route input becomes "verifier-side only" |
| a-hs10.\* | Frontier comparison F3 vs F2 on same task family/budget under F0 §3.2 (HS10) | analysis chain (reg → readout → audit → close) over f2/f3 logs | a-hs10.readout ← f2.log, f3.log | HS10 verdict |
| f6.\* | Kernel scaffolding tokens-to-target at T0→T1: 5 paired seeds, arms incl. **explication-text-interleaved data arm**; E1 single-look rule. The pre-registered instrument check (trained arms must beat step-0 cloze before any between-arm read) is encoded as the first verdict_rule (INSTRUMENT-INVALID), not a separate node; the **instrument repair vs E1** (what changes + the instrument's own pass bar) is pre-registered inside f6.reg — a second INSTRUMENT-INVALID after the repair scores HE6 **undetermined-not-supporting** in a-h0 (never as support) and buys no further replication (RT-1/RT-19) (HE6) | template | f6.inputs ← D-TS; f6.mock ← GATE-T1 | f6 kill/text-parity ⇒ M3-vector dead ⇒ **HS13/E7 precondition unsatisfiable** (E7 slice of f7 pruned) |
| a-extrap-2.\* | **Directives-§6 extrapolation analysis, sign/direction level:** for every mechanism with ≥2 measured rungs after Tiers 0–3, fit the pre-registered trend, quote the P1 §4b envelope row verbatim, compare direction against the named literature anchors (Law 2, LCM/CALM penalty, RETRO range, Kaplan/Hoffmann discipline); emits the scale-language license per experiment (none / sign-only / slope) | analysis chain | a-extrap-2.readout ← all Tier-0–3 closes | envelope statements for the GNG-2 dossier; feeds paper.claims |
| family-h0.\* | F-H0 cross-experiment Holm family (P8 C-3, RT-13): analysis chain; the pinned script consumes member experiments' `analysis-output.json` by sha; the 8 pre-declared members fixed at freeze, non-read-out members scored as non-rejections | analysis chain | family-h0.readout ← f1, f2, e9, f3, f4, f6 closes | family-wise Holm decisions feeding a-h0 |
| a-h0.readout | Evaluate the frozen H0 disjunction gate over member verdict objects + the family-h0 Holm decisions (first evaluation; re-run at GNG-3) | AUTO | all Tier-0–3 closes; family-h0.close | h0 verdict (YES-pattern / NO-pattern / UNDECIDED / open) |
| **GNG-2** | **Global decision-tree evaluation** (P1 §6, first-match-from-top: TAKE-TO-FRONTIER-LAB / NARROW-AND-CONTINUE / PIVOT / KILL / **STOP-AND-PUBLISH-UNDECIDED**). The route is **computed** (P2 §5.2: the tree is verdict-object expressions), the dossier auto-prepared (every verdict + audit + kill text + M0b + envelopes + spend ledger); the maintainer ratifies or overrides — an override is itself a recorded decision. The UNDECIDED route (RT-1) fires when no mechanism PASS exists and the H0-NO pattern is blocked by an INCONCLUSIVE or repeated INSTRUMENT-INVALID after its replication buy: publish with the pre-computed decidability bands + a what-budget/n-would-decide statement. **Replication-buy cap (pre-declared):** at most one replication buy per experiment/gap, at most two programme-wide; "narrow-and-continue" is never invocable twice for the same missing evidence (GR-9) | **GATE-H** over AUTO-computed route | f1, g2–g9, f2, e9, f4, g1, e8r (e8d if run), f3, f6, m0b closes; a-extrap-2.close; a-h0.readout | signed GNG-2 record; routes Tier 4/5; PIVOT/KILL/UNDECIDED ⇒ write-up phase pulls forward (§5) |

### 1.7 Tier 4 — F5, double-gated (~$200–800)

| ID | Node | Type | Deps | Output |
|---|---|---|---|---|
| **GATE-T4** | Double gate: f1 verdict = byte premise PASS (≥2× vs compressed gloss text) ∧ f3 verdict settled (injection route fixed) ∧ maintainer budget approval $200–800 | **GATE-H** (approval) over AUTO-GATE (conditions) | f1.close, f3.close, GNG-2 | gate record |
| f5.\* | Store accuracy leg: Pythia-style controlled training at T1/T2, arms {kernel-store, byte-matched text-RAG, int4-quantized larger, distilled smaller, no-store}; hull test (HE5 full) | template; mock mandatory | f5.inputs ← D-ST, GATE-T4 | inside-hull ⇒ M4-as-architecture retired; no-store-only win filed as not-ours (Atlas/RETRO) |
| a-hs9.\* | Lifecycle crossover: F5-arm-2 vs F6-arm-1 at T2, matched lifecycle FLOPs, Q swept 10⁴–10⁸ (F0 amortization) (HS9) | analysis chain | a-hs9.readout ← f5.log, f6.log | HS9 verdict |
| a-hs11.\* | Structured-store-earns-place: F5 arms 2 vs 3 + E9-C text-diff-checker joint read (HS11) | analysis chain | a-hs11.readout ← f5.log, e9.log | HS11 verdict |

### 1.8 Tier 5 — F7 ≡ E7, maintainer-gated ($2–10k)

| ID | Node | Type | Deps | Output |
|---|---|---|---|---|
| **GATE-T5** | Maintainer sign-off on the $2–10k envelope (`budget.maintainer_signoff` required to freeze f7 at all — P2 G-11). Machine-checked preconditions: {f2, e9, f4, f6} verdicts all read out ∧ ≥1 mechanism alive ∧ GNG-2 = TAKE or NARROW. **Never started without explicit sign-off** (P1 §5) | **GATE-H** | f2.close, e9.close, f4.close, f6.close, GNG-2 | signed gate record |
| E7-PRE | HS13 precondition check: f6 toy/T1 vector-arm signal exists ∧ maintainer explicitly includes the E7 slice | AUTO-GATE + GATE-H rider | f6.close, GATE-T5 | E7 slice in/out |
| f7.\* | Freeze + run the survivors-only slope grid: HE7 Δ(cost-at-iso-accuracy) across ≥3 rungs (R1–R4/R5 inference; T0/T2/T3 training), HC5 verifier-lift slice (surviving HC1/HC2 arms at R3, R4), HS13/E7 slice iff E7-PRE open; R5/T3 rungs each carry their own worst-case cost line in the ledger before launch | template; f7.reg ← GATE-T5; mock mandatory | — | HE7/HC5(/HS13) verdicts |
| a-extrap-5.\* | **Directives-§6 extrapolation analysis, slope level:** WLS slope fits on log-params with 90% CIs per survivor; extrapolation statements at most one OOM past the top measured rung, direction-only unless the CI is tight; explicit comparison to published scaling-law discipline (Kaplan 2020 / Hoffmann 2022 as the cautionary anchors); the ONLY node that licenses scale adjectives (P2 G-12 "slope") | analysis chain | a-extrap-5.readout ← f7.close | per-finding extrapolation envelopes + uncertainty for GNG-3 and the paper |
| **GNG-3** | Final disposition per P1 §6 re-evaluation (computed route + maintainer ratification): frontier pitch scoped to survivors / narrow / pivot / kill / **stop-and-publish-undecided** (same RT-1 pattern and replication-buy cap as GNG-2); a positive HS13 triggers **immediate independent replication before any claim**; a-h0 re-evaluated (with the family-h0 Holm decisions) | **GATE-H** | f7.close (or GNG-2 route if Tier 5 declined), a-extrap-5.close (when Tier 5 ran) | disposition record |

### 1.9 Write-up & explainer-back — first-class, honesty-gated (directives §7)

Runs on EVERY route out of GNG-2/GNG-3, including PIVOT, KILL, and
STOP-AND-PUBLISH-UNDECIDED: a rigorous negative-results paper is a pre-declared success mode
of the programme, with the same node chain and the same gates; the UNDECIDED paper quotes
the pre-computed decidability bands and states what budget/n would decide the question
(honest and publishable — a first-class outcome in P9 §1.1's paper-type table). Owning role: Writer agent (§0.3). Reporting skills: `report-gen`, `paper-claims`,
`explain-back` (I-SKILLS).

| ID | Node | Type | Deps | Output |
|---|---|---|---|---|
| r-final | Auto-generate the evidence bundle from the registry + logs: `registry/status.json` table, every rendered verdict report, raw-log index, spend ledger, envelope table — the paper's reproducibility appendix, machine-derived, zero hand-written numbers | AUTO | GNG-3 (or GNG-2 on a PIVOT/KILL/UNDECIDED route that declines Tiers 4–5) | evidence bundle in-repo |
| paper.claims | `paper-claims`: machine claims-trace table — every claim the paper intends to make, each row = {claim text, experiment id, verdict-object sha, envelope row, kill-criterion text, scale-language license}. **A claim with no verdict-object trace cannot enter the manuscript** | AUTO | r-final, a-extrap-2.close (and a-extrap-5.close when Tier 5 ran) | claims table (committed) |
| paper.outline | Venue-format outline; results section enumerates **every** CLOSED experiment (positives and negatives at equal structural prominence — the results table is generated from `registry/status.json`, so omission is mechanical, visible, and forbidden) | AUTO | paper.claims | outline |
| paper.draft | Full manuscript, top-tier-venue standard (contribution framing, related work incl. the L1–L3 prior-art positioning and the Hyperdimensional-Probe differentiation, methods = pointers to frozen preregs, limitations = envelope table verbatim, negative results in abstract when they are the headline) | AUTO (Writer) | paper.outline | manuscript draft |
| paper.lint | **The honesty gate on the manuscript** (GR-15): `registry-check --citations` over the draft + claims-table cross-check — fails closed on: any claim without a trace row; PASS-PENDING-AUDIT cited as PASS; scale adjectives beyond the license field; a PASS mentioned without its verbatim kill text; any CLOSED experiment missing from the results table; any quoted number ≠ its verdict object | AUTO-GATE | paper.draft | lint-clean manuscript |
| paper.review | Adversarial internal review by the auditor identity (never the Writer): re-derives every quantitative statement from verdict objects; checks framing against P1 §6 anti-overselling guards; REFUTE ⇒ back to paper.draft with a committed review record | GATE-A | paper.lint | review record (CONFIRMED required) |
| paper.sign | Maintainer approval: manuscript, authorship (O-10), venue + timing (O-9) | **GATE-H** | paper.review | signed approval |
| paper.submit | Submission to the chosen venue (external action; external communication of results is GATE-H by GR-8) | **GATE-H** | paper.sign | submission record |
| xb.draft | `explain-back`: the accessible explainer for the maintainer, in the clearest possible plain language — what we found / what it means / what scale it holds at / go-no-go recommendation; one page + a Q&A appendix; every number carries its experiment id | AUTO (Writer) | paper.review | explainer draft |
| xb.lint | Same honesty gate as paper.lint (claims-trace + citations scan) — the explainer may simplify language, never claims | AUTO-GATE | xb.draft | lint-clean explainer |
| xb.deliver | Deliver the explainer to the maintainer + live Q&A; the maintainer's questions and the answers are appended to the explainer and committed (the directives make this a first-class node, not a courtesy) | **GATE-H** | xb.lint, paper.sign | delivered explainer + Q&A record |
| c-out | Close-out: Modal volume cleanup, credential revocation review, beads final sync, archive statement (repo = the complete reproducible record) | AUTO | xb.deliver | archived programme |

### 1.10 Cross-cutting hard orderings (P1 §5 + directives §7 as DAG edges)

```
f1.close             ≺ D-ST ≺ f5.inputs           # byte premise before store build
f3.close             ≺ GATE-T4 ≺ f5.inputs        # injection route before F5
g2.run, g3.annotate  ≺ g4.inputs ≺ g6.run, g7.run # fork chain
g3.close             ≺ g2.readout                 # semantics pin interprets Π
f6.close ∧ GATE-T5   ≺ E7-PRE ≺ f7 (E7 slice)     # A1-at-scale is double-gated
f2/e9/f4/f6 .close   ≺ GATE-T5                    # readouts before any F7 spend
m0b.close, m0b.gate  ≺ GATE-T1                    # coverage + NICHE-SCOPE gate before first GPU $
family-h0.reg        ≺ a-h0.reg                   # P8 C-3 Holm family frozen before the H0 gate freezes (RT-13)
family-h0.close      ≺ a-h0.readout               # cross-experiment Holm before any H0 read
d-xif ≺ f2.iface, e9.iface ≺ f2.run, e9.run       # extraction instrument gate before any correctness read (RT-3)
m0b.close            ≺ any external quotation     # (GR-9)
GNG-0                ≺ every X.run (m0b excepted; its freeze is GNG-0 input)
X.audit (CONFIRMED)  ≺ any PASS anywhere          # (GR-6 / P2 G-6)
a-extrap-*           ≺ any scale adjective in any document  # (GR-9 / P2 G-12)
paper.lint ∧ paper.review ≺ paper.sign ≺ paper.submit       # honesty before exposure
paper.sign           ≺ xb.deliver                 # explainer follows the write-up (directives §7)
r-final/paper/xb chain runs on EVERY GNG route, incl. PIVOT and KILL
```

Everything not ordered above parallelises, subject to the ≤5-concurrent-agent cap (§4 GR-3)
via the wave schedule in §5.

---

## 2. The automation boundary

**Fully automatable (AUTO / AUTO-GATE / GATE-A):** the P2 backbone build; F0; skills; all
data authoring and hash-pinning (D-\*); all registry freezes; all Modal mock + full runs;
log appends; every statistical readout (verdict-gen + pinned analysis scripts); the
extrapolation analyses (a-extrap-2/5); the H0 gate evaluation and the family-h0 Holm analysis; machine gates GATE-T1,
GNG-1's evaluation, E7-PRE's condition check, the m0b.gate NICHE-SCOPE evaluation, and the
f2.iface/e9.iface extraction-instrument gates; audits (role-separated but agent-executed);
the evidence bundle, claims table, manuscript draft, honesty lints, adversarial paper
review, and the explainer draft. An agent fleet can therefore take the programme from GNG-0
to (a) the GNG-2 dossier and (b) a lint-clean, adversarially-reviewed manuscript **without
any human action except the seven human-gate classes below** — that is the design goal.

**Human gates (GATE-H), exhaustively:**

| Gate class | Instances | Who | What exactly is needed |
|---|---|---|---|
| Budget-cap setting | I-BUDGET | maintainer | confirm/adjust the §4 GR-1 cap table (one message) |
| Pre-registration freeze | **GNG-0** | maintainer | sign the registry root sha (one commit approval) |
| Credential minting | CRED-GATE (inside I-MODAL, only if token invalid); any new AWS deploy key (Option A retired — should stay unneeded) | maintainer | `modal token new` pairing (~3 min); never stored in-repo |
| Annotation hours | g3.annotate (~8–10 h ×2 annotators), g2.gold (n = 500 judgments, ~12 h), g9.review (~4 h), m0b spot-check (~2 h), d-ir-n natural-violation adjudication (~2 h, blind — RT-7c) | annotators (sourcing = O-3) | ~30–40 total human-hours, blinded materials prepared by agents |
| Spend approvals | **GATE-T4** ($200–800), **GATE-T5** ($2–10k, the frontier-relevant tier), f7 R5/T3 rung riders | maintainer | explicit go, recorded in the registry (`budget.maintainer_signoff`) |
| Programme decisions | **GNG-2**, **GNG-3**, E7-PRE inclusion rider | maintainer | ratify (or overrule, on the record) the machine-computed route against the auto-prepared dossier |
| Write-up & external exposure | **paper.sign**, **paper.submit**, **xb.deliver**; any other external claim/pitch | maintainer | approve manuscript/authorship/venue; receive the explainer + Q&A; nothing leaves the repo without this class |

GNG-1 is deliberately **not blocking** for the Tier-2 correctness track: F2's outcome
re-scopes the efficiency claims automatically in the registry, and the maintainer is
notified, but e9/f4/e8r proceed either way (they answer the correctness question, which F2
cannot kill). This keeps the critical path human-free between GNG-0 and GNG-2.

**Boundary rule (binding):** no agent may perform, simulate, or assume the outcome of a
GATE-H node. A GATE-H with no recorded human action is CLOSED (fail-closed, GR-4), and every
node downstream of it is blocked — the scheduler must surface it, not route around it.

---

## 3. Execution harness design

### 3.1 Transport

**Primary: Modal, profile `jmwright-045`** (`poc/modal/` — validated pattern: E2/E5/E9
full runs + E1/E4 scaffold already landed under this profile). Serverless GPUs, no quota,
per-second billing. **Secondary:** the AWS pull path (`poc/gpu/`, Option B — no standing
credentials) if/when GPU quota lands (bead `kernel-of-truth-wve`); spot is cheaper for long
serial grids. Both transports run the SAME committed runners on the SAME committed inputs
into the same `results-incoming/` review flow — two transports, one analysis (established
discipline; nothing in a runner may branch on transport).

GPU profiles per campaign: T4 for inference-light (e9, f2 small rungs), A10G default for
training + 1.7B inference (f3/f4/f6/f5), fan-out via `starmap` exactly as `modal_e1e4.py`
does (15/25/35-way validated). R5/T3 rungs (f7 only) get a sized plan (`--dry-plan` first,
token-free) and their own ledger line before launch.

### 3.2 RunSpec — the launch contract

Every `X.run` materialises a RunSpec from the frozen registry entry; the harness **refuses
to launch** unless every field verifies (fail-closed, `ERR_*`):

```jsonc
{
  "registry_id": "f2",             // P2 entry
  "prereg_hash": "…",              // must equal frozen_sha256 in registry/frozen-index.json
                                   //   (P2 G-1; embedded in every log line)
  "encoder_hash": "40e8c8ba…",     // pinned; Bq-path runs quote their own pinned hash;
                                   //   NO decode-dependent claim on the Bq path
  "corpus_manifest_sha": "…",      // kernel-v0 manifest + campaign data manifests
  "arm_defs_sha": "…", "analysis_script_sha": "…",
  "staged_manifest": { "...": "sha256 per staged file, asserted IN-CONTAINER" },
  "image_id": "…", "gpu": "a10g", "modal_profile": "jmwright-045",
  "seeds": [0,1,2,3,4],            // registered seeds only (P2 G-14), paired across arms
  "timeout_min_per_call": 47,      // estimate ×1.5 + 5 min container overhead
  "worst_case_usd": 41.0,          // Σ calls × sized timeout × rate — checked vs ledger
  "tier": 1, "runner_agent_id": "runner-3"   // pseudonym only (P2 §1.2 constraint 10, RT-14)
}
```

### 3.3 Pinning (enforced, not aspirational)

- **In-container staged-manifest assertion** (existing `ERR_STAGING_MISMATCH` pattern):
  every script + input byte-hashed by the coordinator, re-hashed inside the container, run
  dies on mismatch. Campaign-specific pin gates follow the E4 pattern (`ERR_GLOSS_PIN`,
  `ERR_TABLES_PIN`) — e.g. e9 pins the gloss-dictionary + instance-record shas; f5 pins the
  store builds; g1 pins each codebook fork's own goldens.
- **Encoder pin:** any run whose encoder hash ≠ the registry entry's is refused, and
  `log-append` auto-demotes drifted-pin runs to `phase:"exploratory"` (P2 G-14 — kept, but
  can never count). Changing {schema, algorithm, D, codebook, weighting} = ALGORITHM_VERSION
  bump + deliberate X0 golden regeneration + Phase-X re-run + **new pre-registration**
  (house rule, inherited). The G1 random-atom fork is a parallel labelled encoder, never a
  mutation of the mainline.
- **Environment pin:** `requirements-image.txt` + recorded hydrated image id;
  `CUBLAS_WORKSPACE_CONFIG=:4096:8`; everything pre-registered as exact (DetStream shards,
  schedules, frozen-row bit-identity, paired-seed init) is asserted in-container per run —
  a frozen-row violation crashes that run (existing trainer behaviour, kept).

### 3.4 Logging & results flow (P2 is normative; this is the operational binding)

1. Per-stage **provenance sidecars** (`provenance/<runid>.json`): stage, argv, GPU seen,
   library versions, redacted env, rc, timestamps, the staged manifest (existing format).
2. Results land in `poc/<exp>/results-incoming/<UTC stamp>-modal/`; **never auto-committed**
   — the coordinator reviews and commits deliberately (X.log), including FAILED salvage dirs.
3. `X.log` appends **one line per run cell** to `results-log/<id>.jsonl` via
   `tools/registry/log-append` (hash-chained, schema-validated, prereg-hash-verified; raw
   metrics only — no derived statistics, P2 §2.4). Corrections are `supersede` records,
   valid only against `exit != "ok"` targets. Harnesses never write the file directly.
4. `X.readout` = `verdict-gen` (P2 §3.1, steps 1–9): chain verification, amendment overlay,
   eligibility filter, completeness gate, pinned analysis in a no-network sandbox, the
   `unblind` line, frozen verdict_rules, PASS→PASS-PENDING-AUDIT until audited. Reports are
   rendered from the fixed template only — hand-written summaries of results are banned from
   `docs/` verdict sections (`registry-check --citations` enforces).
5. Everything persists to `jeswr/kernel-of-truth` (this box is ephemeral); session-end push
   discipline per CLAUDE.md — plus `registry-check` green — is part of every runner's
   definition-of-done.

### 3.5 Retry / backoff / checkpoint

- **Infra failures** (preemption, OOM-kill by the platform, network, image pull): Modal
  function retries = 2, exponential backoff 30 s → 120 s; then the stage fails and salvage
  runs. At most **1 coordinator relaunch of a wedged app per 24 h** without human triage.
- **Scientific failures** (any `ERR_*` assertion, pin mismatch, frozen-row violation,
  instrument-check fail): **never retried automatically.** Salvage logs/partials to
  `<stamp>-modal-FAILED/` (existing collect-parity behaviour), the run is logged with its
  `exit` code (it stays in the chain forever), a bead is filed, human/coordinator triage.
  A rerun is a new log line; superseding a *successful* run is schema-invalid (P2 §2.2).
- **Checkpoint/resume:** per-campaign Modal Volumes (`kot-hf-cache` shared; `kot-<exp>-work`
  per campaign); training checkpoints at step-0/50%/100%; completed stages stamped on the
  Volume keyed on (argv, staged-bytes digest) — re-runs resume, never silently recompute
  under changed bytes (changed bytes ⇒ new stamp ⇒ full re-run). Volumes deleted at c-out
  (storage line in the ledger until then).
- **Timeout sizing:** per-call timeout = estimate ×1.5 + 5 min; app-level failsafe = Σ sized
  timeouts; worst-case $ = failsafe × rate, checked against the ledger **before** launch.

---

## 4. Guardrails — operational rules (GR-1 … GR-15)

Each rule states: enforcement mechanism → trigger → action. These are configuration and
code, not intentions; I-BUDGET/I-REG/I-SKILLS build the enforcing tooling before GNG-0.
Where a rule overlaps a P2 guardrail, the P2 mechanism (G-1…G-14) is the implementation and
is cited; P3 adds the operational triggers around it.

| # | Rule | Enforcement |
|---|---|---|
| **GR-1** | **Per-tier hard budget caps** (canonical table, RT-8 reconciliation — identical wherever a cap table appears, incl. P2 G-11 and P6 §4; maintainer confirms at I-BUDGET): Tier 0 ≤ $20 (API only) · Tier 1 ≤ $80 · Tier 2 ≤ $400 · Tier 3 ≤ $400 · cumulative Tiers 0–3 ≤ $900 · Tier 4 (F5) ≤ $900 · Tier 5 = maintainer-approved envelope ($2–10k). Worst-case Tiers 0–3 ≈ $760 < $900. **Freeze-time tier-sum lint:** Σ(frozen worst-cases in a tier) ≤ tier cap — `prereg-freeze` refuses a freeze that would break the sum, so a fully-utilised tier can never BUDGET-HALT mid-campaign by arithmetic. | Pre-launch: harness refuses any RunSpec whose worst_case_usd exceeds remaining tier headroom (`ERR_BUDGET`). In-flight: hourly cost monitor polls Modal spend + ledger; breach ⇒ **kill switch**: `modal app stop` on every live app in the tier + `poc/gpu/terminate.sh` for any AWS boxes + BUDGET-HALT status event in the log (P2 G-11) + bead filed + maintainer notified. Every container additionally carries its sized hard timeout (a wedged run self-caps). Resumption only via a dated ops amendment raising the cap. |
| **GR-2** | **Hash-pin enforcement.** No run without in-container staged-manifest + encoder + corpus + prereg-hash assertions; all fail closed with named `ERR_*` codes. Any pin change = new pre-registration, reported as such. | §3.3 mechanisms; P2 G-1/G-14: `log-append` embeds and verifies the prereg hash, demotes drifted-pin runs to exploratory; verdict-gen step 3 excludes them visibly. |
| **GR-3** | **≤5 concurrent agents, waves, no nested spawning.** Coordinators never spawn children-of-children; runner waves sized ≤5 (the fleet has been rate-limit-killed twice at higher concurrency). | Wave schedule in §5; coordinator launch discipline; beads wave labels; a runner that needs parallelism uses Modal `starmap` (containers, not agents). |
| **GR-4** | **Fail-closed gates.** A gate that cannot evaluate (missing verdict object, unreadable ledger, absent human record) is CLOSED. No silent fallbacks anywhere in harness code (house rule). | AUTO-GATE scripts return CLOSED on any exception; scheduler treats CLOSED = blocked; the shared expression evaluator (P2 §3.1 grammar) is the only gate semantics. |
| **GR-5** | **Negative-result honesty.** Every completed run appends to the chained log regardless of outcome; nulls require TOST to be called NULL (else INCONCLUSIVE); negative verdicts are rendered by the same template at the same prominence and the paper's results table enumerates every CLOSED experiment mechanically. | P2 G-5 + P2 §3.3 template; report-gen refuses to render a PASS without its verbatim kill-criterion text alongside (P1 §6 anti-overselling guard, mechanised); paper.lint re-checks at manuscript level (GR-15). |
| **GR-6** | **Run-vs-audit separation.** The agent identity that ran or built any part of an experiment never audits it; a computed PASS is PASS-PENDING-AUDIT until a CONFIRMED audit record by a distinct identity lands; audits re-derive the verdict from pinned artifacts, adversarially (leakage, tuning asymmetry, endpoint drift, arm-favouring bugs — P4 checklist). Positives get full audits; kills/nulls get conformance audits. The paper gets the same treatment (paper.review). Externally the property is reported as **role-separated re-derivation**, never "independent audit" (P2 G-6 naming discipline, RT-9); "independent" is reserved for maintainer-level audits and genuinely external replications. | P2 G-6 schema rule (`ERR_P2_SELF_AUDIT`: auditor ≠ every runner in the eligible log); agent ids in RunSpec + audit record; backup Fable account for hard identity separation (O-5). |
| **GR-7** | **Single-look / no endpoint drift.** Analysis scripts hashed at X.reg; the primary endpoint is computed once by the pinned script at X.readout (which writes the `unblind` line; note the **design-amendment cutoff is earlier** — the first `phase:"final"` run record, P2 §1.4/G-3, RT-5); any additional analysis is `phase:"exploratory"` (quarantined, uncitable) and can never flip a verdict. | P2 G-3/G-4/G-13: frozen analysis_script sha, amendment validity vs the first-final-run line, exploration quarantine + citation scanner. |
| **GR-8** | **No auto-commit of results from containers; no auto-push of claims.** Coordinator reviews and commits; external communication of any result is GATE-H (paper.submit / xb.deliver / ad-hoc pitches all included). | Existing transport behaviour; §2 gate class 7; GR-9/GR-15 lints upstream of any exposure. |
| **GR-9** | **Claim-discipline lints** (mechanised in report-gen + `registry-check --citations`): every quoted number carries rung + M0b coverage + comparison discipline — plus the **NICHE-SCOPE banner** whenever m0b.gate fired below the GNG-0 threshold (RT-7); scale adjectives require the "slope" license (≥3 rungs; 2 = sign only; 1 = nothing) computed into the verdict object; no strong-A1 restatement unless HS13 passed; **replication-buy cap** (RT-1): at most one replication buy per experiment/gap, at most two programme-wide, and "narrow-and-continue" never invocable twice for the same missing evidence; m0b.close ≺ any external quotation. | P2 G-7/G-12 + the citations scanner over `docs/` and `reports/`; a-extrap-* nodes are the only source of extrapolation statements. |
| **GR-10** | **Baseline-parity guard.** No arm may receive more tuning budget than its baselines (LR-selection and retry budgets are per-arm-symmetric by pre-registration); the audit checklist includes a tuning-asymmetry check. | Frozen arm defs (P2 G-8 lint: mandatory baselines incl. kernel-as-text present at freeze); GR-6 audit item; full per-run config in every log line makes asymmetry detectable. |
| **GR-11** | **Credential hygiene.** Modal token outside the repo (`~/.modal.toml`); provenance redaction (`redact_env`); rendered AWS user-data passes the credential-pattern refusal guard; no write deploy keys minted (Option A stays retired); annotator materials contain no credentials. | Existing validated mechanisms; CRED-GATE is the only mint path. |
| **GR-12** | **Persistence.** Every artifact (registry, logs, RunSpecs, results, audits, gate records, manuscript, explainer, the §8 list's beads mirror) lives in `jeswr/kernel-of-truth`; work is not done until pushed AND `registry-check` is green. | CLAUDE.md session protocol + P2 §5.3 (registry-check before git push); runner definition-of-done. |
| **GR-13** | **Mock-first.** No full GPU run without a same-day green `--mock` transport smoke of the same app + staged bytes. | Template edge X.mock ≺ X.run; harness checks the smoke stamp. |
| **GR-14** | **Kill-switch inventory** (documented, tested at I-BUDGET): `modal app stop <app-id>` per app; `modal token revoke` (nuclear, GATE-H); `poc/gpu/terminate.sh --yes` + per-launcher terminate one-liners for AWS; cost-monitor auto-invocation per GR-1; every launcher prints its own kill command at launch. | I-BUDGET deploys + smoke-tests the monitor against a dummy ledger breach. |
| **GR-15** | **Write-up honesty gate.** No manuscript, explainer, pitch, or external text advances past its lint node unless: every quantitative claim has a claims-table row tracing to a `registry/verdicts/<id>.json`; no PASS-PENDING-AUDIT is cited as PASS; every PASS travels with its verbatim kill text; scale language matches the license field; the results table enumerates every CLOSED experiment (negatives included); every extrapolation statement quotes its a-extrap-* envelope + uncertainty + licensing assumption. The explainer may simplify wording, never claims. | `registry-check --citations` extended over the manuscript + claims-table cross-check (paper.lint / xb.lint, fail-closed); paper.review re-derives adversarially; paper.sign/xb.deliver are GATE-H behind it. |

---

## 5. Phased timeline, waves, and milestones

Start: 2026-07-09. **Pacing basis (re-based 2026-07-08, maintainer direction): this
timeline is set at AGENTIC pace, not human development pace.** The earlier calendar
over-estimated on human dev speed; agent execution of build/run/analysis nodes takes
hours-to-days. **Agent development is not the bottleneck anywhere in this table.** The
long poles that actually set the calendar are: (1) **human gates** — GNG-0 signature,
annotator turnaround, spend approvals, paper sign-off; (2) **GPU-run wall-clock and
queues** (Modal fan-out validated at ≈5–6 h wall for an E1-class grid); (3) **external
compute-access lead time** for the frontier tier (ARC ~1–3 wk; AIRR Gateway ~1 mo
submission→access ⇒ ~Oct 2026 — P11 §§4–5). Milestones are therefore **criteria-gated,
not calendar-padded**: a phase exits when its gate conditions are green. Annotator-dependent
nodes (g3/g2/g9/m0b/d-ir-n) carry the largest scheduling variance — they are front-loaded
and off the GPU critical path; annotator sourcing itself is a DEFERRED decision (O-3:
Amazon Mechanical Turk the leading paid option, decided near the annotation stage). The
programme **ends at the paper and the explainer-back on every route**, including PIVOT/KILL.

| Phase | Agentic pace + waves (≤5 concurrent runners) | Long pole (what actually sets the date) | Exit milestone / gate |
|---|---|---|---|
| **P-0 Setup** | W0a: I-REG(+I-HYP,I-RETRO), I-F0, I-AUDIT, I-MODAL, I-BEADS · W0b: I-SKILLS, I-BUDGET, m0b chain (+m0b.gate), family-h0.reg, a-h0.reg, D-PI, D-AX — **agent build ≈ 2–3 days from Jul 09** | **GNG-0 signature** (maintainer review ~30–60 min, scheduled at maintainer convenience) | **M0 (criteria-gated, target ≈ Jul 12–14): GNG-0 signed; M0b published + audited; caps set; kill switches tested; f2 frozen as backbone acceptance test. Supersedes the RT-18 Jul-22 calendar slip — RT-18's quality bar survives as "every P-0 exit criterion green before signature", not as calendar padding** |
| **P-1 Tier-0 (R0)** | W1a: f1, g3 (materials→annotate), g8, g9.author, D-QA · W1b: g2 (gold + run), g9.review, D-GL, D-DOM, D-TS, D-XIF, D-EXT · W1c: g4 (after g2/g3), then g6, g7, g5 (cond.), D-AXN, D-CB, D-SAE, D-IR — **every agent-executable Tier-0 verdict within ≈1 day of GNG-0** | **Human annotation turnaround** (g3 ~8–10 h ×2, g2.gold ~12 h, g9.review ~4 h, m0b spot-check ~2 h) — the only thing that stretches M1 | **M1: agent-side Tier-0 closed ≈ GNG-0 +1 day (incl. the F1 byte premise); annotation-dependent verdicts (HS2/HS3/HS-A + m0b.audit) close on annotator turnaround — days if self-annotated, ~1–2 wk via a platform (O-3)** |
| **P-2 Tier-1** | W2: f2 chain (inputs → mock → run → log → readout → audit → close); GATE-T1 evaluates same-day once m0b closes | **The GPU run itself + the ≤$80 Tier-1 spend (AUTHORIZED 2026-07-08) — not dev time**; m0b.close's ~2 h human spot-check sits on GATE-T1 | **M2 = GNG-1 (≈ GNG-0 +3–5 days): F2 pivot readout; efficiency scope auto-updated; maintainer notified** |
| **P-3/P-4 Tiers 2–3** | W3a: e9 chain, f4 chain · W3b: g1 (rides f4), e8r chain · W3c: e8d (cond.) · W4a: f3 chain (incl. M2-output rider), a-hs10 · W4b: f6 chain · W4c: a-extrap-2, family-h0, a-h0.readout — each campaign ≈ 1–3 days wall; analysis nodes same-day behind the last close | **≈1–2 weeks total, gated MAINLY by human annotator turnaround** (d-ir-n adjudication ~2 h blind; g2/g3-dependent interpretation) **and GPU-run queues — not agent speed** | **M3+M4 (≈ GNG-0 +2–3 wk): all Tier-0–3 verdicts + audits closed; sign-level extrapolation envelopes computed — all Tier-0–3 evidence complete** |
| **GNG-2** | Route machine-computed + dossier auto-prepared same-day after the last Tier-3 close | **Maintainer ratification** | **M5 (≈ GNG-0 +2–3 wk, ~early-to-mid Aug 2026): maintainer ratifies TAKE / NARROW / PIVOT / KILL / STOP-AND-PUBLISH-UNDECIDED (P1 §6, first match from top). PIVOT/KILL/UNDECIDED ⇒ jump to P-7 (write-up pulls forward immediately)** |
| **P-5 Tier-4 (cond.)** | GATE-T4 → D-ST → f5 chain → a-hs9, a-hs11 — build + run ≈ a few days–1 wk wall (100–350 A100-h) | **GATE-T4 spend approval** (with the GNG-2 dossier) **+ the deferred Tier-4 provider decision** (Modal-paid vs ARC free path, ~1–3 wk onboarding lead — P11; provider field re-frozen at GATE-T4) | **M6 (≈ 1–2 wk after GATE-T4 opens): HE5-full, HS9, HS11 verdicts** |
| **P-6 Tier-5 (gated)** | GATE-T5 (+E7-PRE rider) → f7 chain (survivor slopes; HC5 slice; E7/HS13 slice iff open) → a-extrap-5 — grid ≈ days–2 wk wall once compute is in hand | **External compute-access lead time — the frontier tier's true long pole**: ARC ~1–3 wk; **AIRR Gateway ~1 mo submission→access ⇒ ~Oct 2026** (P11 N-7); GATE-T5 sign-off; provider field re-frozen at GATE-T5 (Modal-paid is faster but bills the $2–10k envelope) | **M7 (~Oct–Nov 2026 on the AIRR path; earlier only by paying Modal): HE7/HC5(/HS13) verdicts + slope-level envelopes — the only tier licensing scale adjectives / frontier pitch. GNG-3 within days of f7.close** |
| **P-7 Write-up** | Writer agent: r-final → paper.claims + paper.outline → paper.draft ≈ 2–4 agent-days; paper.lint + paper.review (auditor) ≈ 1–2 days per iteration — xb.draft in parallel after paper.lint | **paper.review iterations + paper.sign (maintainer)** | **M8: lint-clean, adversarially-CONFIRMED manuscript — days after GNG-3 (or days after GNG-2 on an early PIVOT/KILL/UNDECIDED route, ~late Aug–Sep 2026); every claim traced to a verdict object; negatives at full prominence** |
| **P-8 Sign-off, explainer-back, submission** | paper.sign (maintainer) → xb.lint → **xb.deliver** (explainer + live Q&A) → paper.submit at the O-9 venue window → c-out — ≈ 1 agent-day of work | **Maintainer sign-off, xb.deliver scheduling, and the O-9 venue window** — this calendar is entirely human/venue-set | **M9: explainer-back delivered and committed; submission executed at the chosen venue window; volumes cleaned; repo archived as the complete reproducible record** |

**Slack & failure routing.** Windows above are gate-relative, not calendar-padded: the
variance lives almost entirely in the human gates and queues (annotator turnaround in P-1;
maintainer availability at M0/GNG-2; ARC/AIRR access lead in P-5/P-6) — never in agent
development time. A Modal outage reroutes to the AWS pull path at +wall-clock, same
analysis. A decisive NO by GNG-2 costs ≈ $200–700 + ~30–40
annotator-hours and routes to P-7 immediately: the negative-results paper (full statistics,
raw logs, registry) + the explainer-back are produced with the SAME node chain, gates, and
prominence rules — that outcome is a *success* of the plan, per the directives, and is
budgeted and scheduled as first-class. A STOP-AND-PUBLISH-UNDECIDED route (RT-1) is
handled identically: it routes to P-7 with the decidability bands and a
what-budget/n-would-decide statement in the paper, rather than buying further replications
past the pre-declared cap.

**Standing agent map by phase:** P-0/P-1 = coordinator + 4–5 R0/build runners; P-2–P-4 =
coordinator + 2–3 campaign runners + 1 auditor (audits pipeline behind runs, never same
identity); P-5/P-6 = coordinator + 1–2 runners + 1 auditor; P-7/P-8 = coordinator + writer +
auditor (reviewer). The auditor identity never changes mid-campaign.

---

## 6. Open decisions for the maintainer (blocking items marked ●)

| # | Decision | Blocks | Default if unstated |
|---|---|---|---|
| O-1 ● | Confirm/adjust the GR-1 canonical cap table and the Tiers-0–3 pre-approved envelope (≤$900; worst-case ≈ $760) + Modal account spend limit alignment. **Partially resolved 2026-07-08: Tier-0 (~$0) + Tier-1 F2 (~$80, Modal) spend AUTHORIZED NOW; caps unchanged; post-F2 infra/provider fields deferred to each tier's spend-gate (P6)** | I-BUDGET → GNG-0 | table as written |
| O-2 ● | Sign GNG-0 (registry root sha) once I-REG lands | every X.run | — (hard block) |
| O-3 | Annotator sourcing for ~30–40 h (g3 ×2 annotators, g2 gold at n = 500 judgments, g9 blinded review, m0b spot-check, d-ir-n adjudication) — **DEFERRED (2026-07-08, maintainer direction): the decision is made near the annotation stage, once the blinded materials are build-complete. Amazon Mechanical Turk is the leading paid option** (fees inside the H-4 ≈$500–900 envelope); self + one colleague at $0 remains open | M1 annotation-dependent verdicts only (g2/g3/g9); agent-side Tier-0 unaffected | decide at the annotation stage; MTurk leading paid option; g3's second annotator must be a second human |
| O-4 | Modal-primary confirmation vs re-poking AWS quota (bead `kernel-of-truth-wve`) for spot savings on f5/f6/f7 training grids | none (transport swap is analysis-neutral) | Modal primary |
| O-5 | Auditor identity: same account with role separation vs the backup Fable account for hard separation | I-AUDIT config | backup account for Tier ≥2 positives and for paper.review |
| O-6 | GATE-T4 approval ($200–800) — decision due with the GNG-2 dossier (≈ GNG-0 +2–3 wk under the agentic timeline); the deferred Tier-4 infra/provider field (Modal-paid vs ARC) re-freezes here | f5 | — |
| O-7 | GATE-T5 approval ($2–10k) + E7-PRE inclusion rider — decision due when Tier-5 compute access lands (AIRR Gateway ~Oct 2026 — P11 N-7; earlier only on Modal-paid); the deferred Tier-5 infra/provider field re-freezes here | f7 | — |
| O-8 | G1 external-artifact licences fine to use as baselines (Numberbatch CC-BY-SA attribution; KGE training data) | D-CB | yes, attributed in reports |
| O-9 | Target venue + submission window for the paper (candidates by route: main-track ML venue for a mechanism PASS; interpretability venue on the A6 pivot; a rigorous negative-results/replication track on the KILL route) — decision due at paper.sign, provisional pick welcome at GNG-2 | paper.submit | nearest top-tier window ≥2 weeks after M8 |
| O-10 | Authorship & agent-contribution disclosure policy for the paper | paper.sign | maintainer sole human author; agent roles disclosed in contributions section |

---

## 7. Risks to the plan itself (operational, not scientific)

1. **Annotator latency** (P-1): mitigated by front-loading and keeping g2/g3/g9 off the GPU
   critical path; worst case, M1 slips without moving M2 (only the g4→g6/g7 chain and
   E9-C's interpretation depend on it).
2. **SAE availability for e8r** (D-SAE): if no site-matched residual-stream dictionaries
   exist for a suitable third family, fitting them dominates E8's $30–120 cap — the cap is
   sized for fitting, but a pathological family choice gets escalated rather than silently
   overspent (GR-1).
3. **Rate-limit fleet death**: historically triggered at >5 agents — GR-3 is load-bearing;
   waves never exceed 5 even when the DAG has more parallelism available.
4. **Cross-transport float non-reproducibility**: known and documented (torch makes no
   bit-promise across GPU/driver versions); everything pre-registered as exact is exact on
   both paths; audits re-derive statistics from shipped run outputs, not by retraining,
   except where the P4 checklist explicitly calls for a spot re-run.
5. **Scope creep via "one more arm"**: any arm not in the frozen registry entry is a new
   pre-registration (GR-2); the registry diff is the tripwire.
6. **Box loss**: everything persists to the repo (GR-12); Volumes are re-derivable from
   pinned inputs; the §8 list's beads mirror survives in-repo.
7. **Write-up drift under deadline pressure**: the lint + adversarial review + claims table
   make overselling mechanical to catch (GR-15), but a rushed venue deadline is the classic
   pressure point — M8 is placed ≥2 weeks before any target window, and O-9 explicitly
   allows slipping a venue cycle rather than the honesty gates.
8. **Registry/backbone bugs frozen in** (P2 R-4): analysis scripts ship with fixture tests
   required at freeze time; a post-unblinding bug fix is a superseding experiment id with
   the bug documented.

---

## 8. Machine-parseable task list (normative; mirrored 1:1 into beads)

Format, one node per line (the `#`-prefixed lines are comments):

```
id ; type ; deps (space-separated ids, "-" if none) ; title
```

Types: `AUTO`, `AUTO-GATE`, `GATE-H`, `GATE-A` (§0.1). `[cond]` in a title marks a node
that exists only if its guard verdict opens it. Within-experiment stage semantics are §0.2;
arm × rung × seed cells are log rows inside `.run`, enforced complete by verdict-gen.

```
# --- phase 0: infrastructure & freeze ---
i-reg        ; AUTO      ; -                                   ; build P2 backbone: schemas + prereg-freeze/log-append/verdict-gen/registry-check + tamper fixtures
i-hyp        ; AUTO      ; i-reg                               ; generate + freeze registry/hypotheses.json from P1 §8
i-retro      ; AUTO      ; i-reg                               ; retro-import X0-X4, E1/E2/E5/E8/E9-defl, X1-grounding as retro:true CLOSED records
i-f0         ; AUTO      ; -                                   ; build F0 accounting harness poc/f0/ (flop-meter, byte ledger, latency, $/query, amortization) + tests
i-audit      ; AUTO      ; i-reg                               ; build P4 audit kit: checklist, auditor config, audit-record wiring into verdict-gen
i-modal      ; AUTO      ; -                                   ; verify Modal profile jmwright-045, rebuild pinned image, inventory volumes, --mock ping
cred-gate    ; GATE-H    ; i-modal                             ; [cond] mint/refresh Modal token (only if i-modal finds it absent/expired)
i-budget     ; GATE-H    ; -                                   ; confirm GR-1 caps (O-1); init registry/budget.json; deploy + smoke-test cost monitor & kill switches
i-skills     ; AUTO      ; i-reg i-f0                          ; package skills: prereg, run-experiment, flop-meter, decode-verify, audit-result, report-gen, paper-claims, explain-back
i-beads      ; AUTO      ; -                                   ; mirror this list into beads with dep edges + wave labels
m0b.reg      ; AUTO      ; i-reg                               ; freeze M0b entry (kernel-expressibility coverage; required gate)
m0b.inputs   ; AUTO      ; m0b.reg                             ; pin representative corpus slice + stratification plan
m0b.run      ; AUTO      ; m0b.inputs                          ; coverage estimate: % content-word mass with plausible profile-1 explication, per rung
m0b.log      ; AUTO      ; m0b.run                             ; append coverage runs via log-append
m0b.readout  ; AUTO      ; m0b.log                             ; verdict-gen: pinned analysis + verdict rules
m0b.audit    ; GATE-A    ; m0b.readout                         ; auditor re-derivation + human spot-check n=100 (GATE-H rider, ~2h)
m0b.close    ; AUTO      ; m0b.audit                           ; publish coverage + rung; restated in every later verdict (P2 G-7)
m0b.gate     ; AUTO-GATE ; m0b.close gng-0                     ; NICHE-SCOPE coverage gate (RT-7): coverage < GNG-0-set threshold (default 20% of target-task content-word mass) => NICHE-SCOPE banner rendered in every verdict + frontier pitch requires explicit coverage-growth cost line
family-h0.reg ; AUTO     ; i-reg i-hyp                         ; freeze F-H0 cross-experiment Holm-family record (P8 C-3): 8 pre-declared members fixed at freeze; non-read-out members scored as non-rejections (never data-dependently selected)
a-h0.reg     ; AUTO      ; i-reg i-hyp family-h0.reg           ; freeze H0 disjunction-gate record (P1 §1 YES/NO patterns + STOP-AND-PUBLISH-UNDECIDED pattern as verdict-object expressions; repeated f6 INSTRUMENT-INVALID after the pre-registered repair scored undetermined-not-supporting for H0-NO, never support; rules linted against family-h0.reg at freeze)
gng-0        ; GATE-H    ; i-reg i-hyp i-retro i-f0 i-audit i-budget i-skills ; maintainer signs registry root sha (pre-registration freeze)

# --- data & artifact authoring ---
d-pi         ; AUTO      ; gng-0                               ; implement Pi projector over explication structure (kernel-v0, 54 records)
d-ax         ; AUTO      ; gng-0                               ; author ~20-axiom set in kot-axiom/1 v0; mint URNs; pin sidecar hash
d-axn        ; AUTO      ; d-ax g2.close                       ; author same set in NSM-native AxiomSchema syntax, 2 independent author-agents
d-ir         ; AUTO      ; d-ax                                ; seeded instance-record corpus >=300 with planted violations at known rates (E9-C)
d-ir-n       ; AUTO      ; d-ax                                ; natural-violation SECONDARY sub-corpus (RT-7c): >=100 candidates mined from revision-pinned SmolLM2 outputs under pinned prompts/seeds, surfaced by lexical/structural heuristics (never the axiom checker under test); blind human adjudication (GATE-H rider, ~2h, O-3 hours); model ids/prompts/seeds/heuristics/labels hash-pinned; pre-registered E9-C Holm secondary — planted d-ir stays the powered primary (P1 HC2, P6 H-4)
d-qa         ; AUTO      ; m0b.run                             ; F2 definitional-QA eval set + gloss corpus + RAG index, leak-checked
d-xif        ; AUTO      ; gng-0                               ; model<->verifier extraction interface + held-out labelled extraction set per docs/research-plan/10-model-record-interface.md (shared output-format affordances for ALL arms; extraction failures = instrument events)
d-ext        ; AUTO      ; m0b.run                             ; externally-authored eval slice: definitional/consistency subset of a public benchmark filtered to kernel-covered concepts via M0b machinery (pre-registered secondary in e9 + f2)
d-gl         ; AUTO      ; m0b.run                             ; F3 long-glossary task sets d in {4,16,64} + matched-token text variants
d-dom        ; AUTO      ; gng-0                               ; F4 onboarding domain: >=50 held-out concepts authored, URNs minted, vectors encoded (pinned encoder, X4 JL)
d-cb         ; AUTO      ; d-dom                               ; G1 arms: random-atom-codebook encoder fork (own goldens), Numberbatch pack, KGE lens pack
d-sae        ; AUTO      ; gng-0                               ; E8-R third-family residual-stream site-matched SAE dictionaries + seed-stability strata
d-ml         ; AUTO      ; -                                   ; crawl 1,000-declaration random Mathlib sample (G8)
d-ts         ; AUTO      ; gng-0                               ; F6 scaffold corpora: concept-heavy shards + explication-text-interleaved arm, 5 paired seeds
d-st         ; AUTO      ; f1.close d-qa                       ; F5 store corpora 10^3/10^5/10^6 + byte-matched compressed text stores

# --- tier 0 (R0, ~$0; no .mock) ---
f1.reg       ; AUTO      ; i-reg                               ; freeze F1 (HE5 byte premise)
f1.inputs    ; AUTO      ; f1.reg i-f0                         ; pin record sets + compression baselines (zstd-JCS)
f1.run       ; AUTO      ; f1.inputs gng-0                     ; byte/latency accounting vs compressed gloss text, store scales 10^3-10^6
f1.log       ; AUTO      ; f1.run                              ; log-append
f1.readout   ; AUTO      ; f1.log                              ; verdict-gen (deterministic byte/latency criteria)
f1.audit     ; GATE-A    ; f1.readout                          ; conformance/adversarial audit
f1.close     ; AUTO      ; f1.audit                            ; HE5-byte verdict; kill prunes d-st/f5 branch
g3.reg       ; AUTO      ; i-reg                               ; freeze G3 (HS3 semantics pin)
g3.inputs    ; AUTO      ; g3.reg                              ; build blinded annotation materials (~20 concepts x ~10 instances)
g3.annotate  ; GATE-H    ; g3.inputs gng-0                     ; 2 independent human annotators judge necessity + sufficiency (~8-10h each)
g3.log       ; AUTO      ; g3.annotate                         ; log-append annotation data
g3.readout   ; AUTO      ; g3.log                              ; verdict-gen: Wilson bounds vs 10% thresholds, kappa reported
g3.audit     ; GATE-A    ; g3.readout                          ; audit
g3.close     ; AUTO      ; g3.audit                            ; HS3 verdict; necessity-fail auto-resolves HS2 sidecar-only + prunes g5
g2.reg       ; AUTO      ; i-reg                               ; freeze G2 (HS2 Pi read-out soundness)
g2.inputs    ; AUTO      ; g2.reg d-pi                         ; derived-subsumption dump + scoring materials
g2.gold      ; GATE-H    ; g2.inputs                           ; human gold set: n = 500 subsumption judgments (~12h), blind adjudication — decidability-powered for the 0.9 Wilson gate (P2 freeze lint, RT-4)
g2.run       ; AUTO      ; g2.gold gng-0                       ; score Pi read-outs vs gold; promise/words recovery; partition-residue check
g2.log       ; AUTO      ; g2.run                              ; log-append
g2.readout   ; AUTO      ; g2.log g3.close                     ; verdict-gen: Wilson lower bound vs 0.9 precision; interpreted under HS3 outcome
g2.audit     ; GATE-A    ; g2.readout                          ; audit
g2.close     ; AUTO      ; g2.audit                            ; HS2 verdict; residue list feeds d-axn
g4.reg       ; AUTO      ; i-reg                               ; freeze G4 (HS4 axiom authoring surface)
g4.inputs    ; AUTO      ; g4.reg d-ax d-axn                   ; dual-syntax corpora + effort logs staged
g4.run       ; AUTO      ; g4.inputs gng-0                     ; authoring effort/error rates + LLM decode-legibility probe
g4.log       ; AUTO      ; g4.run                              ; log-append
g4.readout   ; AUTO      ; g4.log                              ; verdict-gen vs NF2 bounds
g4.audit     ; GATE-A    ; g4.readout                          ; audit
g4.close     ; AUTO      ; g4.audit                            ; HS4 verdict; selects axiom surface
g5.reg       ; AUTO      ; g2.close                            ; [cond: HS2 = Pi-normative] freeze G5 (HS5 constraints-out-of-vector confirm)
g5.run       ; AUTO      ; g5.reg                              ; encode-twice margins + RDM delta on axiom edits
g5.log       ; AUTO      ; g5.run                              ; log-append
g5.readout   ; AUTO      ; g5.log                              ; verdict-gen
g5.audit     ; GATE-A    ; g5.readout                          ; conformance audit
g5.close     ; AUTO      ; g5.audit                            ; HS5 verdict; surprise reversal => new pre-registration
g6.reg       ; AUTO      ; i-reg                               ; freeze G6 (HS6 AND-under-operator share; deterministic count)
g6.run       ; AUTO      ; g6.reg g4.run gng-0                 ; static counts over kernel-v0 + molecules-v0 + G4 axiom set
g6.log       ; AUTO      ; g6.run                              ; log-append
g6.readout   ; AUTO      ; g6.log                              ; verdict-gen (count thresholds, no test)
g6.audit     ; GATE-A    ; g6.readout                          ; conformance audit
g6.close     ; AUTO      ; g6.audit                            ; HS6 verdict
g7.reg       ; AUTO      ; i-reg                               ; freeze G7 (HS7 apply-clauses at bulk; deterministic count)
g7.run       ; AUTO      ; g7.reg g4.run gng-0                 ; cap-violation/clause-growth counts at bulk-scale projection
g7.log       ; AUTO      ; g7.run                              ; log-append
g7.readout   ; AUTO      ; g7.log                              ; verdict-gen
g7.audit     ; GATE-A    ; g7.readout                          ; conformance audit
g7.close     ; AUTO      ; g7.audit                            ; HS7 verdict
g8.reg       ; AUTO      ; i-reg                               ; freeze G8 (HS8 Lean minting rates)
g8.inputs    ; AUTO      ; g8.reg d-ml                         ; stage Mathlib sample + math-v0 overlaps
g8.run       ; AUTO      ; g8.inputs gng-0                     ; fragment rate, top-5 location rate, round-trip fixed point
g8.log       ; AUTO      ; g8.run                              ; log-append
g8.readout   ; AUTO      ; g8.log                              ; verdict-gen: Wilson bounds vs 1% / 80% gates
g8.audit     ; GATE-A    ; g8.readout                          ; audit
g8.close     ; AUTO      ; g8.audit                            ; HS8 verdict
g9.reg       ; AUTO      ; i-reg                               ; freeze G9 (HS-A authoring gate vs DeepNSM-8B)
g9.author    ; AUTO      ; g9.reg gng-0                        ; author N>=50 machine explications inside the validator loop
g9.review    ; GATE-H    ; g9.author                           ; blinded human review (~4h) on Baartmans metrics
g9.log       ; AUTO      ; g9.review                           ; log-append
g9.readout   ; AUTO      ; g9.log                              ; verdict-gen: Wilson lower bound vs DeepNSM point + 10
g9.audit     ; GATE-A    ; g9.readout                          ; audit
g9.close     ; AUTO      ; g9.audit                            ; HS-A verdict; fail rewrites why-now everywhere

# --- tier 1: the pivot ---
gate-t1      ; AUTO-GATE ; gng-0 m0b.close m0b.gate i-f0 i-modal i-budget ; tier-1 launch gate: freeze signed, coverage published + NICHE-SCOPE gate evaluated, harness green, transport ready, headroom ok
f2.reg       ; AUTO      ; i-reg i-hyp                         ; freeze F2 (HE1 primary; HE2/HC3/HS12 riders; 9 arms + PRM + cascade + in-decode gating + gloss-text self-verify + retry at matched budget (RT-2; HE1/HE2 PASS requires the kernel arm to BEAT it, not just RAG); backbone acceptance test)
f2.inputs    ; AUTO      ; f2.reg d-qa d-xif d-ext             ; pin arm artifacts: PRM, int4-360M, cascade + logprob gate + text-self-check gate, verifier loop over the d-xif extraction interface, external eval slice
f2.mock      ; AUTO      ; f2.inputs gate-t1                   ; Modal --mock transport smoke
f2.iface     ; AUTO-GATE ; f2.mock d-xif                       ; extraction-failure instrument gate (10-model-record-interface.md): failure rate on held-out labelled set <= frozen bound; failures scored as instrument events, never hypothesis events; all arms share output-format affordances
f2.run       ; AUTO      ; f2.iface                            ; full grid: SmolLM2 135M/360M/1.7B x arms x retry {1,2,4}, full metric vector V
f2.log       ; AUTO      ; f2.run                              ; log-append (one line per cell)
f2.readout   ; AUTO      ; f2.log                              ; verdict-gen: pinned analysis (paired bootstrap, Holm family, TOST), frozen verdict rules
f2.audit     ; GATE-A    ; f2.readout                          ; role-separated adversarial audit (full on any PASS)
f2.close     ; AUTO      ; f2.audit                            ; HE1/HE2/HC3/HS12 verdicts committed
a-hs12       ; AUTO      ; f2.log                              ; latency analysis batch-1 + throughput; HS12 implementation selection (no kill)
gng-1        ; AUTO-GATE ; f2.close                            ; pivot readout: P1 tier-1 gate text evaluated; maintainer notified; efficiency scope auto-updated (non-blocking for tier 2 correctness)

# --- tier 2 ---
e9.reg       ; AUTO      ; i-reg i-hyp                         ; freeze E9-full + E9-C (HC1, HC2, HS11-part): 6 arms (incl. gloss-text self-verify + retry at matched budget, RT-2) + constraint arm + text-diff-checker arm + d-ext external-slice + d-ir-n natural-violation Holm secondaries (RT-7; planted d-ir = powered primary); HC1 PASS requires the kernel arm to BEAT the self-verify arm at matched FLOPs
e9.inputs    ; AUTO      ; e9.reg d-ir d-ir-n d-qa d-xif d-ext ; pin gloss dictionary, RAG index, instance-record corpus + natural-violation secondary sub-corpus (d-ir-n), extraction interface + labelled set, external eval slice
e9.mock      ; AUTO      ; e9.inputs gate-t1                   ; --mock smoke
e9.iface     ; AUTO-GATE ; e9.mock d-xif                       ; extraction-failure instrument gate (10-model-record-interface.md): failure rate on held-out labelled set <= frozen bound; failures scored as instrument events, never hypothesis events; all arms share output-format affordances
e9.run       ; AUTO      ; e9.iface                            ; full run R1, R2 (R3 iff sign); non-LLM rubric / leak-checked judge
e9.log       ; AUTO      ; e9.run                              ; log-append
e9.readout   ; AUTO      ; e9.log                              ; verdict-gen: catch rates (Wilson), kernel-vs-self-verify comparison at matched FLOPs (HC1), 3x text-arm test, FP bound, per-class breakdown; fail names the failing stage
e9.audit     ; GATE-A    ; e9.readout                          ; audit
e9.close     ; AUTO      ; e9.audit                            ; HC1 + HC2 verdicts
f4.reg       ; AUTO      ; i-reg i-hyp                         ; freeze F4 (HE4): 5 arms incl. ToolkenGPT-protocol + in-context-text null; R1/R2/R3
f4.inputs    ; AUTO      ; f4.reg d-dom                        ; pin domain pack + LoRA baseline config
f4.mock      ; AUTO      ; f4.inputs gate-t1                   ; --mock smoke
f4.run       ; AUTO      ; f4.mock                             ; full run
f4.log       ; AUTO      ; f4.run                              ; log-append
f4.readout   ; AUTO      ; f4.log                              ; verdict-gen: 90%-of-LoRA / 10%-FLOPs bounds, text-parity kill via Wilson/TOST
f4.audit     ; GATE-A    ; f4.readout                          ; audit
f4.close     ; AUTO      ; f4.audit                            ; HE4 verdict
g1.reg       ; AUTO      ; i-reg i-hyp                         ; freeze G1 (HS1): random-atom codebook / Numberbatch / KGE-lens arms, 2 families
g1.inputs    ; AUTO      ; g1.reg d-cb                         ; pin the 3 arm packs incl. fork-encoder goldens
g1.run       ; AUTO      ; g1.inputs f4.run                    ; run G1 arms under the F4 protocol + second family (Qwen2.5-0.5B)
g1.log       ; AUTO      ; g1.run                              ; log-append
g1.readout   ; AUTO      ; g1.log                              ; verdict-gen vs F4 primary endpoint
g1.audit     ; GATE-A    ; g1.readout                          ; audit
g1.close     ; AUTO      ; g1.audit                            ; HS1 verdict; parity => all claims narrow to governance (propagated by report-gen)
e8r.reg      ; AUTO      ; i-reg i-hyp                         ; freeze E8-R (HC4 leg 1): site-matched residual-stream SAE, third family; sole primary = replication
e8r.inputs   ; AUTO      ; e8r.reg d-sae                       ; pin SAE dictionaries + seed-stable strata
e8r.mock     ; AUTO      ; e8r.inputs gate-t1                  ; --mock smoke
e8r.run      ; AUTO      ; e8r.mock                            ; correspondence vs shuffled-kernel + permutation nulls, both new pairs
e8r.log      ; AUTO      ; e8r.run                             ; log-append
e8r.readout  ; AUTO      ; e8r.log                             ; verdict-gen: permutation p per pair, Spearman rho + bootstrap CI
e8r.audit    ; GATE-A    ; e8r.readout                         ; audit
e8r.close    ; AUTO      ; e8r.audit                           ; HC4-leg-1 verdict; fail shelves A6 + prunes e8d
e8d.reg      ; AUTO      ; e8r.close                           ; [cond: e8r PASS] freeze E8-D (HC4 leg 2): semantic-regression detection vs linear probe
e8d.inputs   ; AUTO      ; e8d.reg                             ; pin version pairs + probe baseline
e8d.run      ; AUTO      ; e8d.inputs                          ; AUC comparison run (shares e8r harness)
e8d.log      ; AUTO      ; e8d.run                             ; log-append
e8d.readout  ; AUTO      ; e8d.log                             ; verdict-gen: DeLong test, dAUC >= 0.05 margin
e8d.audit    ; GATE-A    ; e8d.readout                         ; audit
e8d.close    ; AUTO      ; e8d.audit                           ; HC4 verdict complete

# --- tier 3 + tiers-0-3 analysis ---
f3.reg       ; AUTO      ; i-reg i-hyp                         ; freeze F3 (HE3): 7 arms, d in {4,16,64}, R1-R3, + M2-output rider (expected-fail, <=$20)
f3.inputs    ; AUTO      ; f3.reg d-gl                         ; pin task sets + trained-compressor arm at matched budget
f3.mock      ; AUTO      ; f3.inputs gate-t1                   ; --mock smoke
f3.run       ; AUTO      ; f3.mock                             ; full run (f2 verdict read as scope note only, non-blocking)
f3.log       ; AUTO      ; f3.run                              ; log-append
f3.readout   ; AUTO      ; f3.log                              ; verdict-gen: prompt-FLOPs/KV at parity, amortization at Q=10^6
f3.audit     ; GATE-A    ; f3.readout                          ; audit
f3.close     ; AUTO      ; f3.audit                            ; HE3 verdict; kill retires dense I/O for efficiency
a-hs10.reg   ; AUTO      ; i-reg i-hyp                         ; freeze A-HS10 (HS10): F3-vs-F2 frontier comparison under F0 §3.2
a-hs10.readout ; AUTO    ; a-hs10.reg f2.log f3.log            ; pinned comparison analysis over both logs
a-hs10.audit ; GATE-A    ; a-hs10.readout                      ; audit
a-hs10.close ; AUTO      ; a-hs10.audit                        ; HS10 verdict
f6.reg       ; AUTO      ; i-reg i-hyp                         ; freeze F6 (HE6): T0->T1, 5 paired seeds, text-scaffold arm; INSTRUMENT-INVALID rule first in verdict_rules + pre-registered instrument repair vs E1 with its own pass bar (repeated failure after repair => HE6 undetermined-not-supporting in a-h0, RT-19)
f6.inputs    ; AUTO      ; f6.reg d-ts                         ; pin shard sets + paired-seed schedule
f6.mock      ; AUTO      ; f6.inputs gate-t1                   ; --mock smoke
f6.run       ; AUTO      ; f6.mock                             ; full training grid; frozen-row bit-identity asserted in-container
f6.log       ; AUTO      ; f6.run                              ; log-append
f6.readout   ; AUTO      ; f6.log                              ; verdict-gen: instrument gate, then 0.8x tokens-to-target TOST vs trainable + text-arm parity
f6.audit     ; GATE-A    ; f6.readout                          ; audit
f6.close     ; AUTO      ; f6.audit                            ; HE6 verdict; kill/text-parity prunes E7/HS13 slice
a-extrap-2.reg ; AUTO    ; i-reg                               ; freeze sign-level extrapolation analysis (directives §6): trend fits + P1 §4b envelopes + literature anchors
a-extrap-2.readout ; AUTO ; a-extrap-2.reg f1.close g2.close g3.close g4.close g6.close g7.close g8.close g9.close f2.close e9.close f4.close g1.close e8r.close f3.close f6.close ; fit per-mechanism trends, emit scale-language licenses + envelope statements
a-extrap-2.audit ; GATE-A ; a-extrap-2.readout                 ; audit (statistics re-derived)
a-extrap-2.close ; AUTO  ; a-extrap-2.audit                    ; envelope statements committed for GNG-2 dossier + paper.claims
family-h0.readout ; AUTO ; family-h0.reg f1.close f2.close e9.close f3.close f4.close f6.close ; pinned Holm analysis across the 8 pre-declared members (consumes member analysis-output.json by sha; non-read-out members = non-rejections)
family-h0.audit ; GATE-A ; family-h0.readout                   ; audit (statistics re-derived)
family-h0.close ; AUTO   ; family-h0.audit                     ; F-H0 family-wise Holm decisions committed (input to a-h0.readout)
a-h0.readout ; AUTO      ; a-h0.reg family-h0.close f2.close e9.close f4.close f6.close a-extrap-2.close ; evaluate H0 disjunction gate over member verdict objects + family-h0 Holm decisions (re-run at gng-3); emits YES-pattern / NO-pattern / UNDECIDED / open
gng-2        ; GATE-H    ; a-h0.readout m0b.close m0b.gate f1.close g2.close g3.close g4.close g6.close g7.close g8.close g9.close f2.close e9.close f4.close g1.close e8r.close f3.close f6.close a-extrap-2.close ; global decision tree (computed route, auto dossier); maintainer ratifies TAKE/NARROW/PIVOT/KILL/STOP-AND-PUBLISH-UNDECIDED; replication-buy cap: one per gap, two programme-wide (RT-1); PIVOT/KILL/UNDECIDED => jump to r-final

# --- tier 4 (double-gated) ---
gate-t4      ; GATE-H    ; f1.close f3.close gng-2             ; approve $200-800 over machine conditions: F1 byte PASS + F3 injection route settled
f5.reg       ; AUTO      ; i-reg i-hyp gate-t4                 ; freeze F5 (HE5 full): T1/T2 controlled training, 5 store arms, hull test
f5.inputs    ; AUTO      ; f5.reg d-st                         ; pin store builds + byte-matched text stores
f5.mock      ; AUTO      ; f5.inputs                           ; --mock smoke (mandatory)
f5.run       ; AUTO      ; f5.mock                             ; full training + eval grid
f5.log       ; AUTO      ; f5.run                              ; log-append
f5.readout   ; AUTO      ; f5.log                              ; verdict-gen: Pareto-hull membership vs {text-RAG, int4, distilled}
f5.audit     ; GATE-A    ; f5.readout                          ; audit
f5.close     ; AUTO      ; f5.audit                            ; HE5-full verdict
a-hs9.reg    ; AUTO      ; i-reg i-hyp                         ; freeze A-HS9 (HS9): store-vs-scaffold lifecycle crossover at T2, Q swept 10^4-10^8
a-hs9.readout ; AUTO     ; a-hs9.reg f5.log f6.log             ; pinned amortization analysis
a-hs9.audit  ; GATE-A    ; a-hs9.readout                       ; audit
a-hs9.close  ; AUTO      ; a-hs9.audit                         ; HS9 verdict
a-hs11.reg   ; AUTO      ; i-reg i-hyp                         ; freeze A-HS11 (HS11): structured-store-earns-place joint read
a-hs11.readout ; AUTO    ; a-hs11.reg f5.log e9.log            ; pinned joint analysis (F5 arms 2v3 + E9-C text-diff arm)
a-hs11.audit ; GATE-A    ; a-hs11.readout                      ; audit
a-hs11.close ; AUTO      ; a-hs11.audit                        ; HS11 verdict

# --- tier 5 (maintainer-gated) ---
gate-t5      ; GATE-H    ; f2.close e9.close f4.close f6.close gng-2 ; sign off $2-10k envelope (budget.maintainer_signoff required to freeze f7 at all)
e7-pre       ; AUTO-GATE ; f6.close gate-t5                    ; HS13 precondition: f6 vector-arm signal exists AND maintainer includes E7 slice (GATE-H rider)
f7.reg       ; AUTO      ; i-reg i-hyp gate-t5                 ; freeze F7 (HE7 + HC5 slice; HS13/E7 slice iff e7-pre open): survivors-only slope grid, >=3 rungs
f7.inputs    ; AUTO      ; f7.reg                              ; pin survivor arms + R5/T3 sized plans (--dry-plan) + per-rung ledger lines
f7.mock      ; AUTO      ; f7.inputs                           ; --mock smoke (mandatory)
f7.run       ; AUTO      ; f7.mock                             ; slope grid runs
f7.log       ; AUTO      ; f7.run                              ; log-append
f7.readout   ; AUTO      ; f7.log                              ; verdict-gen: WLS slopes on log-params, 90% CIs, per-mechanism kill text
f7.audit     ; GATE-A    ; f7.readout                          ; audit (a positive HS13 additionally triggers immediate independent replication before any claim)
f7.close     ; AUTO      ; f7.audit                            ; HE7/HC5(/HS13) verdicts
a-extrap-5.reg ; AUTO    ; i-reg                               ; freeze slope-level extrapolation analysis (directives §6, Kaplan/Hoffmann discipline)
a-extrap-5.readout ; AUTO ; a-extrap-5.reg f7.close            ; per-survivor slope fits + <=1-OOM extrapolation statements + uncertainty + licensing assumptions
a-extrap-5.audit ; GATE-A ; a-extrap-5.readout                 ; audit
a-extrap-5.close ; AUTO  ; a-extrap-5.audit                    ; slope-level envelopes; the ONLY license for scale adjectives
gng-3        ; GATE-H    ; f7.close a-extrap-5.close           ; final disposition (computed route + ratification, incl. STOP-AND-PUBLISH-UNDECIDED under the same RT-1 pattern + replication-buy cap); a-h0 re-evaluated with family-h0 decisions; on tier-5-declined routes deps reduce to gng-2

# --- write-up & explainer-back (runs on EVERY route incl. PIVOT/KILL) ---
r-final      ; AUTO      ; gng-3                               ; auto-generate evidence bundle: status table, all verdict reports, raw-log index, ledger, envelope table (on PIVOT/KILL/UNDECIDED routes dep = gng-2)
paper.claims ; AUTO      ; r-final a-extrap-2.close            ; machine claims-trace table: claim -> verdict-object sha + envelope + kill text + scale license (a-extrap-5.close added when tier 5 ran)
paper.outline ; AUTO     ; paper.claims                        ; venue-format outline; results section enumerates EVERY closed experiment from registry/status.json
paper.draft  ; AUTO      ; paper.outline                       ; full manuscript (Writer agent), top-tier standard, honest incl. negatives; limitations = envelope table verbatim
paper.lint   ; AUTO-GATE ; paper.draft                         ; GR-15 honesty gate: registry-check --citations + claims-table cross-check; fail-closed
paper.review ; GATE-A    ; paper.lint                          ; adversarial internal review by auditor identity (never the Writer); REFUTE => back to paper.draft
paper.sign   ; GATE-H    ; paper.review                        ; maintainer approves manuscript + authorship (O-10) + venue/timing (O-9)
paper.submit ; GATE-H    ; paper.sign                          ; submission (external exposure; GR-8)
xb.draft     ; AUTO      ; paper.review                        ; explainer-back draft: what we found / what it means / what scale it holds at / go-no-go recommendation, plain language
xb.lint      ; AUTO-GATE ; xb.draft                            ; same honesty gate as paper.lint (simplify wording, never claims)
xb.deliver   ; GATE-H    ; xb.lint paper.sign                  ; deliver explainer to maintainer + live Q&A; Q&A appended and committed
c-out        ; AUTO      ; xb.deliver                          ; close-out: volume cleanup, credential revocation review, beads sync, archive statement
```

Coverage check (every P1 §8 registry row has a deciding node above): H0→a-h0 (+family-h0,
the P8 C-3 cross-experiment Holm family — a-h0 cannot freeze without it, RT-13);
HC1/HC2→e9; HC3/HE1/HE2/HS12→f2(+a-hs12); HC4→e8r/e8d; HC5/HE7/HS13→f7; HE3→f3; HE4→f4;
HE5→f1+f5; HE6→f6; HS1→g1; HS2→g2; HS3→g3; HS4→g4; HS5→g5; HS6→g6; HS7→g7; HS8→g8;
HS9→a-hs9; HS10→a-hs10; HS11→a-hs11; HS-A→g9; M0b→m0b (+m0b.gate, the NICHE-SCOPE
consequence gate, RT-7). Directives §6 → every X.readout + a-extrap-2/5; directives §7 →
paper.\* + xb.\* (first-class, honesty-gated, owned by the Writer role).
