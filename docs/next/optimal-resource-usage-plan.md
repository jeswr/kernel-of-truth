# N-R2 — Optimal resource usage under COMPUTE ABUNDANCE (work taxonomy · GPU-result reuse · parallelisation schedule)

**Kernel of Truth programme — FABLE-OWNED PLANNING DELIVERABLE.**
Bead: `kernel-of-truth-utq` (maintainer-designated P0). Author: Fable planning agent.
Date: 2026-07-11 (evening state — post f2b-transfer Stage-2 run, post DECONF-A1
COMPLETE, post CODEVERT-G0, post g3 human-Pass-A, post g2 proxy-seat run).
Status: **PLANNING document.** Nothing here is pre-registered, frozen, or spent;
every run below still passes its own gates (prereg-freeze, reuse-check `--gate`,
spend sign-off, role separation). Companion to
`docs/next/resource-optimization-plan.md` (N-R) — N-R's work taxonomy (§1),
composition invariant (§2), reuse ruling status (§3: permissive half **DEFERRED,
unratified**; restrictive half live), and ordering laws (§4) remain **binding**;
this document does not amend them. What changed and why this document exists:
the resource posture inverted. N-R was written for GPU-scarcity (~$1/run economics);
the programme now holds **4 Modal GPU accounts (spend-freely-within-cap) and
~4–5 agents running continuously per worker account per 5-hour window**
[STIPULATED: maintainer's abundance directive, this bead], and has been
**under-utilising both**. This plan says exactly where that capacity buys verdict
movement — and, honestly, where it cannot.

**Tag convention:** `[MEASURED: ref]` = registry/verdict/artifact fact restated
inside its envelope · `[STIPULATED: ref]` = design/planning choice or maintainer
directive · `[EXTRAPOLATION]` = forward projection, never a premise ·
`[DESIGN-GATED]` / `[RESULT-GATED]` / `[HUMAN-GATED]` / `[MAINTAINER-GATED]` =
the *kind* of gate currently blocking a line.

---

## 0. The honest headline: what abundance can and cannot buy

1. **The binding constraint on both thesis verdicts is NOT GPU compute.** The
   capstone says it in terms: "The binding constraint on both verdicts is not
   compute — it is human annotation (f2b-transfer, g2 gold, human g9/M0a), one
   API key (A-F0), input-material generation (g3), and one cheap ablation
   (knull, after its control rewrite)" [MEASURED: docs/next/feasibility-synthesis.md §6].
   Every GPU experiment this programme has run cost $0.30–$30; f2b-transfer
   Stage-2's whole 15-cell campaign was ~0.14 GPU-h [MEASURED:
   scratchpad/f2b-stage2-build.result dry-plan]. Total *genuine* GPU demand over
   the next ~2 weeks is ≈ **80–100 GPU-h** (§3.4) — roughly what ONE of the four
   Modal accounts can carry. Bursting GPU beyond the freeze pipeline's output is
   busy-work by construction, and this plan refuses to schedule it.
2. **What abundance CAN buy, in order:** (a) **latency collapse on the feeder
   pipeline** — the store-authoring, phrasing-corpora, harness-build, audit,
   registration, and freeze work that gates every GPU cell can run as 8–12
   concurrent agent lanes instead of a serial trickle; (b) **the one genuinely
   GPU-shaped line** (NLB-1 parser fine-tune, ≤50 GPU-h, the correctness crux);
   (c) **speculative-parallel pre-staging** (mocks, dry-plans, pilot trainings,
   harness builds) under the standing directive — cheap (<$10 GPU each),
   expected-to-succeed, result-gated [STIPULATED: standing speculative-parallel
   directive as restated in this bead]; (d) **cross-vendor audit throughput**
   (the Stage-2 Codex Gate-A audit is the single highest verdict-movement item
   on the board and costs zero GPU).
3. **What abundance CANNOT buy:** the human-gated affirmative legs. g3's sole
   adjudicator is human Pass B + A2 [MEASURED: docs/next/analysis/g3-result.md];
   g2's human seats, GATE-H (human g9), human M0a, and any further judge-1
   rounds are annotator-hours, not agent-hours. The GPT-5.6 proxy seats for
   g2/g3 have ALREADY been run and are at their licence ceiling — a weak proxy
   "can neither fire nor discharge the kill" [MEASURED:
   docs/next/interpretations/g3-llmproxy-v3.md]. **Spending more proxy calls on
   already-proxied seats is busy-work and is excluded.** The round-2 steering
   risk stands: without the human legs the verdict degrades into
   FAIL-by-attrition [MEASURED: docs/next/analysis/round2-steering.md decision A].
4. **Design throughput is deliberately NOT scaled up.** Round-2 steering:
   "STOP further design/review cycles… design has converged; it lacks results"
   [MEASURED: round2-steering.md item 5]. The only design work scheduled here is
   the *specific* design work that unblocks a named run (Stage-B power sizing,
   knull store, CASC-0 critique response, CODEVERT re-scope memo) — no new
   architecture rounds, no new review panels beyond the ones already owed.

---

## 1. Work taxonomy — everything genuinely ready + genuinely valuable, ranked by verdict-movement-per-unit-resource

Rank = (how far the item moves one of the two INCONCLUSIVE-PENDING theses, per
capstone §3 reversal analysis) ÷ (scarce resource consumed: annotator-hours >
maintainer decisions > agent-hours > GPU dollars, in that order of scarcity).
Lane tags: **[GPU]** Modal · **[ANNOT]** annotation/adjudication (GPT-5.6-proxy
or cross-vendor where licensed; human where not) · **[FABLE]** design/interp ·
**[OPUS]** mechanical execution per N-R §1 taxonomy.

| # | Item | Lane | Cost | Gate state | Verdict movement |
|---|---|---|---|---|---|
| 1 | **f2b-transfer Stage-2 Codex Gate-A audit** | [ANNOT] cross-vendor | agent-hours, $0 GPU | RESULT ready — verdict is PASS-PENDING-AUDIT [MEASURED: scratchpad/f2b-transfer-stage2-interp / interpretations/f2b-transfer-stage2.md] | **Highest on the board.** Confirmation converts the +0.2507 external-gold lift into the programme's first ground-truth-independent end-task positive and forces the capstone's "ZERO audited end-task wins" sentence to be revised (kernel-AUTHORED attribution). Disconfirmation voids the interp. Either way: verdict-moving at zero GPU. |
| 2 | **knull-v2: finish the plain-dictionary store → quality gate → freeze → GPU ablation** | [FABLE]+[ANNOT] authoring/gate, then [GPU] run | authoring agent-hours + 4–6 GPU-h ≈ $15–30 [MEASURED: investigation-launch-manifest §B] | DESIGN-GATED on the store (v2 rewrite in flight: `poc/knull/inputs-v2/`, `quality-gate-v2/`); ablation itself FROZEN-unrun (knull v1 frozen; v2 DRAFT) | **The efficiency de-confound.** Decides whether the +0.1507 is kernel-content or generic aligned-key [MEASURED: capstone §5]. Post-CASC framing makes it MORE decisive (which dialect), not less [MEASURED: scratchpad/cascade-arch.result]. |
| 3 | **DECONF Stage B (generic lexical store through the identical topology, external gold)** | [FABLE] power-sizing + freeze, then [GPU] run | ≤3 GPU-h, ≤$25 [MEASURED: design/DECONF.md §8] | DESIGN-GATED: blocked-by A1 readout (**done**, C_dec=1.0 → conditional kernel arm NOT needed, GS-A carries both readings) + d-adj-t label pin (**done**, Stage-1) + PROPOSED-ASM-1013 power sizing (**open**) + prereg-freeze | With #2 it brackets the attribution question from both sides: kernel-content (knull) and alignment-vs-generic-retrieval (Stage B). Direct answer to both round-1 subjective analyses' #1 risk. |
| 4 | **DECONF A1 registration + registered re-run** | [OPUS]+[FABLE] | ~$0 CPU | DESIGN-GATED on coordinator registering PROPOSED-ASM-1010–1017 + the registered re-run of the (currently EXPLORATORY pre-freeze) certificate [MEASURED: interpretations/deconf-a1.md] | Converts C_dec=1.0 / KERNEL-RUNTIME-STRUCTURE-INERT from exploratory certificate into registered evidence the f2b-line interpretations can lean on. Cheap, mechanical, high hygiene value. |
| 5 | **NLB-0 pilot (both legs) → NLB-1 freeze** — the NL-boundary crux (bead dt3w lineage: l3a-parse/a5-nl FAILs → FK-NLB-3 re-entry) | 0-A: [OPUS] CPU; 0-B: [GPU]+[ANNOT] | 0-A ~$0 CPU ~2 agent-days; 0-B ≤$25 API + ≤5 GPU-h; then NLB-1 ≤~50 GPU-h incl. fine-tune [MEASURED: design/NLB.md §7.5] | DESIGN authorized as design-phase diagnostic (rev-2 post-GPT-5.6); NLB-1 itself needs experiment-designer freeze after the screen | Correctness crux leg (a): "an NL-reaching parser" is one of the two decisive unrun legs [MEASURED: capstone §5]. Also the **largest genuine GPU sink on the board** — the only line where the Modal budget is structurally useful at scale. |
| 6 | **f2b-errors (frozen) run over Stage-2 output** | [OPUS] | ~$0 CPU | RESULT-GATED — record IS frozen (`registry/frozen-index.json` f2b-errors d5c8e70b…) and Stage-2 cells now exist; R-2 taxonomy fields were staged into the Stage-2 harness [MEASURED: investigation-launch-manifest §A + frozen-index] | Refine-tier: error taxonomy on the flagship positive; free. Run before anything perturbs Stage-2 artifacts. |
| 7 | **CASC-0 (six-arm cascade diagnostic)** | [FABLE] critique-response + prereg, then [GPU] | ≤~15 free GPU-h + ~$25 [MEASURED: scratchpad/cascade-arch.result] | DESIGN-GATED: GPT-5.6 external critique of CASC/1 + coordinator synthesis + prereg-freeze still pending; K3 dialect-attribution arm couples to knull-v2 material | Medium EV, honestly disclosed: G2-class, oracle-inbound-flattered, cannot license the WIN (G4-only) [MEASURED: cascade-arch.result, ASM-1039 discipline]. Worth its ~$25 because K1/K2 kills are cheap and structural. |
| 8 | **CODEVERT re-scope memo → maintainer decision → (if (c)) PY-STAT/2 bounded-dataflow spike** | [FABLE] memo; spike [OPUS] CPU | memo agent-hours; spike ~$0 CPU | MAINTAINER-GATED: re-scope-or-drop is an explicit maintainer decision (options a–d), each re-entering the external review gate; **do NOT authorize the 70–130h G1 annotation for the full-8-family design** [MEASURED: interpretations/codevert-g0.md] | G0 measured κ 0.4361 [0.3610, 0.5364] below the 0.5 floor, kill structural ('*' unknown call edges), forward/lexical subset at κ~0.72, dataflow headroom 0.54–0.92. The memo is cheap and the decision unblocks (or honestly kills) the code-vertical-primary bet. |
| 9 | **POWER-rig prerequisites (frozen index pin, oracle census wiring, covered baselines, eligibility registrations)** | [OPUS]+[FABLE] | agent-hours, $0 | DESIGN-GATED per POWER rev-2 downgrade [MEASURED: design/POWER.md header] | Unblocks G1 Δ_max verdicts programme-wide AND supplies the Δ_align sizing that gates Stage B's freeze (#3). Pure feeder work — exactly what abundant agent-hours are for. |
| 10 | **A-F0 mint economics** | [MAINTAINER] | one API key; ~$0 GPU | KEY-GATED, frozen-unrun [MEASURED: capstone §2] | Refine-tier (prices the mint-cost side). One maintainer ping; keep on the supply list, not on an agent lane. |
| 11 | **Capstone + interpretation refresh wave** (post-audit, post-knull, post-Stage-B) | [FABLE] | agent-hours | RESULT-GATED on #1–#3 | The synthesis that actually moves the standing verdict text; scheduled, not improvised. |
| — | **Human-gated legs (g2 human seats, g3 Pass B/A2, GATE-H g9, human M0a, further judge-1 rounds)** | [HUMAN] | annotator-hours | HUMAN-GATED | Verdict-moving but **not purchasable with this budget**. Current provisional directions: g3 necessity FAIL-row matches at hybrid human-q1×proxy-q2 (LB 0.1848 > 0.10, direction invariant across 4 mappings) [MEASURED: analysis/g3-result.md]; g2 ran today on dual proxy seats (`poc/g2/runs/20260711T191317Z/`, judge-pA GPT-5.6-Sol / judge-pB Haiku-4.5) — done-provisional, human confirmation pending. The deliverable owed here is the maintainer's **annotation-portfolio ranking** (round-2 decision A), not more compute. |

**Explicitly excluded as busy-work** [STIPULATED, this plan]: re-running proxy
judges on already-proxied seats; any scale-sweep extension of DECONF/knull/f2b
beyond the ≤1.7B envelope without a fresh design gate (the 100M–2B extrapolation
is explicitly out of every current envelope); new architecture/design review
rounds (round-2 steering item 5); general-index oracle census, H-DD, deep
placements, proof-search consumers (round-2 drop list); nsk1 continuation ahead
of its ladder-exhaustion doc; any GPU cell whose record is not frozen and whose
freeze is not on this list.

---

## 2. Architecture + GPU-result reuse — what we do NOT re-pay for

Standing law first: **the reuse-PERMISSIVE half of N-R §3 is DEFERRED/unratified**
— no `reused_from` consumption of logged rows as arm data; fresh-runs-only is the
norm; `reuse-check.py check --gate` (exit-3 fail-closed) is MANDATORY before any
paid launch [MEASURED: resource-optimization-plan.md §3.0/§3.6]. All eight
producers are unblinded, so row-level reuse would be RC-4-constrained even if
ratified. The economically real reuse is therefore **tier-1/tier-2 (checkpoints,
harnesses, arms, corpora, images, stores) + co-scheduling** — and at this
programme's GPU prices that is where nearly all the money is anyway. Concrete
opportunities, each verified against current artifacts:

1. **The f2b Modal image + harness is the shared substrate for four upcoming GPU
   runs.** knull's frozen ask is literally "1× A100-40GB Modal (f2b image)"
   [MEASURED: investigation-launch-manifest §B]; DECONF Stage B is declared
   "co-schedulable with the f2b-transfer stage-2 campaign (same image, same
   corpus assets)" [MEASURED: design/DECONF.md §8]; CASC-0's MONO/CASC arms are
   135M/1.7B-class option-scoring cells of the same shape. RULE: batch same-image
   runs into shared Modal sessions per account to amortise container spin-up +
   checkpoint pulls (N-R §3.4-1 tier-2 batching), and observe the
   `modal app stop ap-<id>` hygiene memory on every attached run.
2. **Pinned checkpoints never re-download per experiment.** R1 SmolLM2-135M (and
   R3 1.7B) pinned revisions in `results-log/f2.jsonl pins_observed` serve Stage
   B, knull, CASC-0, and NLB-1's host side. Identity = revision pin (N-R §3.2
   tier-1).
3. **The Stage-1 human adjudication (d-adj-t labels) is the reusable external
   gold.** Already pinned and consumed by Stage-2's dual scoring; Stage B scores
   on the same pinned d-adj-t labels by design [MEASURED: DECONF ASM-0964].
   That 360-item human-judged asset is the single most expensive artifact the
   programme owns — every new formal-slice experiment should check whether its
   endpoint can be expressed over it before commissioning new adjudication.
4. **DECONF A1's GS-A store projection (sha 4a28f7fa…) IS Stage B's GS-A arm.**
   Built, hash-pinned, certificate-complete — Stage B consumes the artifact, not
   a rebuild; and because C_dec = 1.0, the conditional kernel-verify arm is
   dropped, saving ~1/5 of Stage B's cells [MEASURED: interpretations/deconf-a1.md
   + DECONF §5.1 conditional-arm rule].
5. **f2b-errors consumes Stage-2's logged output at $0** — the R-2
   superset-logging rule working exactly as designed: taxonomy fields were
   staged into the Stage-2 harness before the run, the record froze before
   unblind, so the taxonomy read is confirmatory-standing, not quarantined.
   This is the programme's first realized R-2 payoff; cite it when arguing R-2
   fields into future freezes.
6. **The l3a kot-axiom engine binary is byte-identical across verticals** (l3a →
   a5 → NLB executor → CASC-0's checked-seam islands → any PY-STAT spike's
   reference engine) [MEASURED: registry/verdicts/a5.json byte-identity]. No
   dependent line may schedule a re-implementation (N-R §2.3 hub rule).
7. **CODEVERT G0's census infrastructure is extractor-independent by design** —
   the 16,722 frozen queries, repos.lock, 6.05 MB packed store, and probe suite
   [MEASURED: scratchpad/codevert-g0.result] are the ready-made bench for ANY
   re-scoped G1 universe or PY-STAT/2 spike: testing a second extractor variant
   costs the variant, not the rig (N-R §2.3 `alternative_to` rule).
8. **NLB reuses the blind-phrasing corpora + five-role separation machinery**
   from l3a-parse/a5-nl (the dt3w identity-separation protocol) as its
   evaluation substrate, with rev-2's corrected corpus arithmetic; the paid part
   of NLB-0-B is new synthetic training data, not re-authoring evaluation
   phrasings [MEASURED: design/NLB.md §7].
9. **knull ↔ CASC-0 material coupling:** the knull-v2 plain/aligned stores double
   as CASC-0's dialect-control and renderer material [MEASURED:
   cascade-arch.result "knull = dialect control + renderer material"] — author
   once under knull's quality gate, consume twice, with the CASC-0 freeze
   declaring the shared pin.
10. **Free re-analysis before re-running (N-R §3.4-5, Wave-R0 duty):** before
    each freeze below, Fable enumerates what is answerable from
    `registry/artifact-ledger.jsonl` + Stage-2's persisted rows at $0
    (quarantined-exploratory, GZ-2 split). Standing candidates: Stage-2
    verifier_engagement descriptives; dual-scoring gap decomposition; the
    codevert ablation surface already computed in `poc/codevert-g0/results/`.

---

## 3. Parallelisation schedule — what should be running CONCURRENTLY, right now

### 3.1 Lane map (4 Modal accounts M1–M4; worker-account agent pools A–D)

**Running NOW, in parallel (no gate violated):**

| Lane | Work | Resource | Why now |
|---|---|---|---|
| A1 | **Codex Gate-A audit of Stage-2** (taxonomy #1) | cross-vendor agent, $0 GPU | Result ready; everything downstream (capstone revision, f2b-errors interp context) waits on it |
| A2 | **f2b-errors run over Stage-2 cells** (#6) | box CPU, $0 | Frozen + inputs exist; minutes of compute |
| A3 | **DECONF A1 registration + registered re-run** (#4) | box CPU, $0 | Mechanical; coordinator-owned appends |
| B1 | **knull-v2 store completion** — finish inputs-v2 authoring through `quality-gate-v2` + GPT-5.6 blind quality check (#2, feeder) | Fable/explicator + proxy-gate agents | The single gate on the efficiency de-confound; parallelise per-entry authoring across agents, gate serially |
| B2 | **Stage-B power sizing (PROPOSED-ASM-1013) + POWER prerequisites** (#3 feeder, #9) | Fable + Opus agents, $0 | Gates the Stage-B freeze; index-pin/census wiring is embarrassingly parallel agent work |
| B3 | **NLB-0-A ROLE_DIR repair + both-orientation tests** (#5 leg A) | box CPU (niced, 2 shared cores), ~2 agent-days | $0, Tier-0, no freeze needed (design-phase diagnostic); directly attacks the a5-nl S2 dangerous-wrong source |
| C1 | **CASC-0: GPT-5.6 external critique** of CASC/1 (#7 feeder) | proxy agent | Named next step; attack surfaces already flagged (M2-vs-nsk1, G1 routing-mass bound, oracle-inbound disclosure) |
| C2 | **CODEVERT re-scope memo** for the maintainer (a/b/c/d options + costs) (#8) | Fable agent | Unblocks a maintainer decision that is currently stalling the #1-ranked annotation line (stale ranking flagged in the G0 interp) |
| D1 | **Speculative-parallel pre-staging** (§3.3) | Modal M2–M4, <$10 total | Standing directive; keeps GPU lanes hot for the moment each freeze lands |

**Genuinely gate-blocked (do NOT start; listed with the gate KIND):**

| Work | Blocked on | Kind |
|---|---|---|
| knull ablation GPU run | plain store completion + v2 freeze | DESIGN (content + freeze) |
| DECONF Stage B GPU run | power sizing + prereg-freeze | DESIGN (statistics) |
| CASC-0 GPU run | critique → synthesis → prereg-freeze | DESIGN (external review) |
| NLB-0-B GPU leg | synthetic training-set build + pilot-parser spec conformance | DESIGN (materials) — cheap enough to speculative-parallel once materials exist |
| NLB-1 (≤50 GPU-h) | NLB-0 screen result + experiment-designer freeze | RESULT (NLB-0) then DESIGN |
| CODEVERT G1 (any universe) / PY-STAT/2 spike | maintainer re-scope decision (+ external review re-entry) | MAINTAINER |
| f7-class capstone anything | gate-t5; far out of scope | MAINTAINER |
| g2/g3/g9/M0a human confirmation | annotator availability + portfolio ratification | HUMAN |
| Capstone refresh | Stage-2 audit outcome (+ knull/Stage-B if landed) | RESULT |

### 3.2 Sequencing logic (producers before consumers, N-R §4)

```
NOW ──► A1 audit ─────────────────────────────► capstone refresh (D-lane, Fable)
    ──► B1 knull store ──► knull freeze ──► M1: knull ablation (4–6 GPU-h)
    ──► B2 power sizing ─► StageB freeze ─► M2: Stage B (≤3 GPU-h, same image/session family)
    ──► C1 critique ─► synthesis ─► CASC-0 freeze ─► M3: CASC-0 (≤15 GPU-h; consumes knull stores)
    ──► B3 NLB-0-A (CPU) ─┐
    ──► materials build ──┴► M4: NLB-0-B (≤5 GPU-h) ─► NLB-1 freeze ─► M-any: NLB-1 (≤50 GPU-h)
```
knull before CASC-0 (store producer→consumer); A1-audit before capstone; Stage B
independent of knull (different question, shared image — co-schedule, don't
serialise). Every M-launch: `reuse-check.py check --record … --gate` first,
`modal app stop` after, nohup+setsid per the standing memory.

### 3.3 Speculative-parallel slate (standing directive: <$10 GPU each, expected-to-succeed, result-gated)

All of these run NOW on M2–M4 without waiting for their consuming decision;
worst case on a design change is <$10 + small rework, disclosed per item:

- **Stage-B mock + Modal dry-plan** on the staged f2b image ($<1) — arms are
  rev-B-stable; only the power-sized n can shift.
- **knull runner mock + dry-plan** against the v1-frozen harness ($<1) — the v2
  delta is store content, not harness shape.
- **CASC-0 harness skeleton + mock** for the six paired arms ($0 GPU) — critique
  may rename arms; harness re-plumb is hours, and the build-first pattern just
  paid off on Stage-2 (runner built before freeze, ran same-day).
- **NLB-0-B smallest-config pilot-parser training run** (~$5–8 GPU) once the
  synthetic set exists — explicitly a design-phase diagnostic with its own ≤5
  GPU-h authorization, so this is inside-scope rather than truly speculative.
- **NOT speculative-parallel:** any scored/final-phase cell of an unfrozen
  record (that is a gate violation, not a speculation), and any NLB-1 fine-tune
  cell before the NLB-0 screen reads out (the screen exists precisely to stop
  that spend).

### 3.4 Budget arithmetic + the honest thinness disclosure

Near-term genuine GPU demand [EXTRAPOLATION, planning estimate]: mocks/dry-plans
<1 GPU-h · Stage B ≤3 · knull 4–6 · NLB-0-B ≤5 · CASC-0 ≤15 · NLB-1 ≤50 ≈
**≤80 GPU-h ≈ $150–250 over ~2 weeks** — under 4-account capacity by an order of
magnitude. Agent-hour demand is the opposite: the feeder lanes (A1–C2) can absorb
**8–12 concurrent agents productively**; beyond that the marginal agent has no
genuine task and the pipeline is **thin by design** — the steering already ruled
that more design/review agents produce convergence certificates, not information.
If all four freezes land this week, the four Modal accounts are each carrying one
result-producing run with head-room; if they don't, the idle GPU is the honest
state and must not be back-filled with unregistered sweeps. The two levers that
would genuinely raise the ceiling are both non-compute: the maintainer's
annotation-portfolio ratification (round-2 decision A) and the CODEVERT re-scope
decision — this plan's C2/A-lane outputs exist to make both decisions cheap.

---

## 4. Eight-line summary (mirrored to scratchpad/resourceplan.result)

1. GPU is not the binding constraint: total genuine near-term demand ≈ ≤80 GPU-h / $150–250 — one account's worth; the capstone-named binders are annotation, freezes, one store, one key.
2. Rank-1 spend is $0 GPU: run the Codex Gate-A audit of f2b-transfer Stage-2 now — it converts the pending flagship positive and forces the capstone revision.
3. Rank-2/3 bracket the +0.1507 attribution: knull-v2 (finish plain store → freeze → 4–6 GPU-h ablation) and DECONF Stage B (power-size → freeze → ≤3 GPU-h) — both design-gated on feeder work, not results.
4. The only structurally GPU-shaped line is the NL-boundary crux: NLB-0-A (CPU, now) + NLB-0-B (≤5 GPU-h pilot) → NLB-1 (≤50 GPU-h fine-tune), correctness leg (a).
5. Reuse is tier-1/2, not row-level (permissive reuse stays unratified): one f2b image/session family serves Stage B + knull + CASC-0; d-adj-t human labels, GS-A projection, l3a engine binary, codevert census rig, and knull↔CASC-0 stores are the concrete no-repay assets; f2b-errors reads Stage-2 rows at $0 (R-2 payoff, frozen pre-unblind).
6. Run concurrently now: Stage-2 audit ∥ f2b-errors ∥ DECONF-A1 registration ∥ knull store authoring ∥ Stage-B power sizing ∥ NLB-0-A ∥ CASC-0 critique ∥ CODEVERT re-scope memo ∥ speculative-parallel mocks/dry-plans (<$10 total, result-gated).
7. Genuinely blocked (kind): knull run (DESIGN-store), Stage B (DESIGN-stats), CASC-0 (DESIGN-review), NLB-1 (RESULT: NLB-0), CODEVERT G1/PY-STAT-2 (MAINTAINER), g2/g3/g9/M0a confirmation (HUMAN) — and proxy re-runs on already-proxied seats are excluded as busy-work.
8. Honest thinness: feeder lanes saturate at ~8–12 concurrent agents; beyond the four freezes there is no registered GPU work, and idle capacity must stay idle rather than be filled with out-of-envelope sweeps — the real ceiling-raisers are the maintainer's annotation-portfolio and CODEVERT re-scope decisions, which this plan's memos make cheap.
