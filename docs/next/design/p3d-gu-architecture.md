# P3-D-GU: H-GU proof-trace-distillation + executor-in-the-loss architecture — REVISED PROPOSAL (Revision 1)

> **STATUS: REVISED PROPOSAL — NOT A PREREG FREEZE.** 2026-07-19, Programme-3 Phase-1 (overflow-Fable).
> Revision 1 applies the six load-bearing fixes from the independent GPT-5.6 soundness review
> ([p3-arch-family-review1.md §H-GU](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3-arch-family-review1.md): "NEEDS-FIX") to the prior unreviewed GPT-5.6 draft.
> **ONLY the step-transition API-gate (+ statement-supply) preregistration is ready now. The full
> trace/filter/RLEF/RL recipe is CONDITIONAL on that API gate passing and is NOT adopted by this
> revision** — the current engine accepts whole `kot-query/1` objects and returns terminal
> answers/refusals; it exposes no proof-search transition system. Crux-VALIDATED add-capability
> architecture (per #57 Phase-0). ARCHITECTURE + training + seams only; the win-condition
> (efficiency-W1 vs correctness-endpoint) + KOT-FAIR/2 eval-prereg are DEFERRED to the maintainer's
> #57 re-weighting + the framework revision. **Any prereg-freeze WAITS on the #57
> framework-adjudication decision AND the framework blockers (P3-D-THREAT revision among them, per
> review 1); nothing here is frozen, registered, scheduled, or committed.**
> See "## Revision 1 — review fixes applied" for the itemised changes.
> Source: poc/gpt56-review/p3d-gu-design/ + review-1 fixes.

> **Tags:** the prior draft's `[SV]` markers are mapped to the programme's four-tag scheme:
> `[LIT-BACKED]` = literature-dependent choice supported by the supplied reviews; `[MEASURED: ref]`
> = observed fact with source; `[STIPULATED]` = design choice awaiting ratification;
> `[EXTRAPOLATION]` = forward claim beyond measurement (deliberately unused in this revision —
> forward performance statements are absent pending #57).

---

# H-GU proof-trace distillation + executor-in-the-loss

Status: **REVISED PROPOSAL (post-review-1) for the coordinator.** Text/specification only; nothing is frozen, preregistered, scheduled, or registered. It accepts #57’s Phase-0 crux result as an input: H-GU is an **ADD-CAPABILITY** architecture in which the deterministic engine supplies exact execution/checking that the neural host structurally lacks. It does not decide whether success is framed as efficiency-W1 or as a correctness endpoint, and it makes **no matched-resource superiority claim**.

The proposal instantiates [H-GU](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:752), reuses the inference topology of [H-VL](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:614) (itself under identity revision per review 1), and inherits the causal-control definitions of [P3-D-THREAT](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md:96) **conditionally** — THREAT is itself a review-1 NEEDS-FIX and must be revised before it governs any GU arm `[STIPULATED]`.

## 0. Scope decision: what is prereg-ready NOW vs conditional `[STIPULATED — review-1 fix 1; PROPOSED-PREREG-ROW-GU-R1a/GU-R1b]`

Review 1’s central finding is **adopted and made load-bearing**: as previously drafted, H-GU was not yet an architecture over the current KOT engine. The draft assumed legal-action sets, proof states, state transitions, proof fragments, and terminal step certificates. The current engine accepts whole `kot-query/1` objects and returns terminal answers/refusals over five terminal operations (lookup, unique, count, instance, exact definition matching) `[MEASURED:` [review 1 §H-VL/§H-GU](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3-arch-family-review1.md)`, tools/axiom/kot_axiom.py]`; it exposes **no proof-search transition system**. µs terminal checking is **not** evidence that step-level APIs exist.

Consequences (all `[STIPULATED]`):

1. **Prereg-ready NOW — the ONLY part:** the blocking **step-transition API gate** (§6.0, PROPOSED-PREREG-ROW-GU-R1a) and the **statement-supply/diversity curve** (§6.0b, PROPOSED-PREREG-ROW-GU-R1b). Nothing else in this document may enter a prereg-freeze before that gate has demonstrably passed.
2. **CONDITIONAL — not adopted by this revision:** every component and training arm that consumes step-level artifacts — the trace compiler, the deterministic search controller’s per-step validation loop, T1 proof-trace distillation, T2 executor-filtered bootstrapping, T3 RLEF, T4 engine-reward RL, T5 hard-state supervision, the step-level loss terms of §3, and the `Tr×E` grid rows that require them. Sections 2–5 and 7 are retained as a **conditional design record**: the conceptual training design was reviewed as sound (executor-in-the-loss = discrete engine outcomes controlling admission/targets/feedback/rewards; T0–T5 ladder; `Tr×E` grid), but none of it is executable, preregistrable, or adopted until the demonstrated step-transition API + explicit action/state/certificate/search-boundary semantics exist.
3. **Fallback if the gate fails:** H-GU either waits on deliberate engine-side interface work (an engine change, subject to the engine’s own versioning discipline — not assumed here), or its terminal-only residue is handled by the H-PS whole-program family; H-GU is **not** silently downgraded into a whole-query recipe while keeping step-level claims or names.

## 1. Architectural claim

H-GU is not “distil the engine until the engine can be removed.” It is:

> Train a small model from step 0 to propose engine-readable actions, consume exact engine feedback, and abstain when the engine cannot certify a result; retain the engine at inference as the sole formal answer authority over its covered grammar.

The engine contributes (items marked ▷ are step-level and CONDITIONAL on the §6.0 API gate `[STIPULATED — review-1 fix 1]`):

- exact terminal validation (current) and ▷ state transitions;
- ▷ legal-action or continuation sets, where demonstrated to exist;
- ▷ proof traces and step certificates;
- deterministic error codes;
- final accept/reject decisions;
- a no-human-label data filter and training reward — **scope: generator-pinned formal/synthetic training only** (§4 preamble) `[STIPULATED — review-1 fix 5]`.

The model contributes:

- natural-language parsing, subject to the NLB gate;
- formal action/subgoal proposal;
- ranking of candidate actions;
- consumption of engine diagnostics across retries;
- selective routing among the **symbolic path, clarification, and abstention only** — there is no uncertified direct-answer path (§2.6) `[STIPULATED — review-1 fix 2]`;
- constrained verbalization of certified results.

The engine does **not** establish that an NL parse matches the user’s intent, resolve genuine ambiguity, supply open-world truth, or guarantee renderer fidelity. It is sound only relative to the submitted formal statement, frozen rules, and covered grammar.

### 1.1 Answer authority (single, engine-only) `[STIPULATED — review-1 fix 2; PROPOSED-PREREG-ROW-GU-R1c]`

The retained engine is the **sole formal answer authority**. Review 1 found the prior draft internally inconsistent: the router offered a “direct answer” path while the claim above asserted sole engine authority. **Resolution — the direct-answer route is REMOVED.** H-GU’s licensed result set consists exclusively of engine-certified results; the only non-engine-certified user-facing outputs are fail-closed clarification requests and abstentions. A host-generated answer that bypasses engine certification is outside H-GU’s licensed result set by definition and is scored as a violation if emitted. The alternative resolution (certifying direct answers through the engine) is rejected because it would either duplicate the symbolic path or create a second answer authority, violating the architectural claim — the same rationale under which the sibling H-PS revision rejected an alternative answer path (H-PS PROPOSED-PREREG-ROW-R1d).

## 2. Components and data flow *(conditional design record — see §0; not adopted until the API gate passes)*

```text
natural input
    │
    ▼
untrusted NLB parser + confidence gate ──(unresolved ambiguity: AMBIGUOUS verdict lives HERE)
    │ TaskEnvelope / candidate formal meanings
    ▼
small from-scratch policy LM ──proposed action──► deterministic orchestrator
    ▲                                                   │
    │ structured diagnostic / state                     ▼
    └──────────────────────────────────────────── deterministic engine
                                                        │
                                      certified result / proof / OUT_OF_SCOPE
                                                        ▼
                              constrained renderer + equivalence re-check
                                                        │
                                        certified answer │ clarification │ abstain
```

The training plane shares the same engine protocol:

```text
seeded curriculum generator (records intended formal target + target_hash)
    │
    ▼
engine enumeration / execution
    │ exact states, steps, certificates            [▷ CONDITIONAL on API gate]
    ▼
trace compiler ──► single-step distillation corpus [▷ CONDITIONAL]
    │
host-generated candidates ──► engine filter + MANDATORY target_hash equality ──► verified replay buffer
    │
failed candidate + diagnostic + later success ──► RLEF correction corpus      [▷ CONDITIONAL]
    │
on-policy candidate ──► terminal engine reward ──► policy-gradient update     [▷ CONDITIONAL]
```

### Required components

1. **Seeded curriculum generator**

   Generates formal tasks with controlled rule depth, branching, polarity, distractor density, proof multiplicity, relation composition, and paraphrase provenance. The generator records the intended formal target and its `target_hash`, so an engine-valid solution to the wrong formalization cannot be mislabeled correct during synthetic training (§4 T2 makes this binding mandatory `[STIPULATED — review-1 fix 4]`).

2. **Deterministic engine service** ▷ *(step-level surface CONDITIONAL on the §6.0 API gate)*

   A versioned, fail-closed service. It must **demonstrably** expose more than final checking before the corresponding training arm exists — the API gate, not this document, establishes that.

   Proposed reply schema (`[STIPULATED]` — a four-status ENGINE schema; see below for `AMBIGUOUS`):

   - `VALID_STEP` ▷
   - `SOLVED`
   - `REJECT`
   - `OUT_OF_SCOPE`

   `AMBIGUOUS` is **not an engine status** `[STIPULATED — review-1 fix 3]`. Ambiguity is an NL/router-layer verdict: the engine receives a single well-formed formal object and judges it; it cannot judge that the *user* was ambiguous. An `AMBIGUOUS` engine status would be admissible only if a future formal task language explicitly represents ambiguity inside the formal object itself — no such representation exists or is proposed here. The router/NLB layer owns the AMBIGUOUS verdict (unresolved parser ambiguity, contradictory surviving candidate meanings) and resolves it fail-closed to clarification or abstention.

   Each reply carries state and request hashes, provenance, engine version, charged runtime, and — where applicable and demonstrated — a proof fragment or certificate. Rejection diagnostics must not leak the gold next action or answer.

3. **Trace compiler** ▷ *(CONDITIONAL)*

   Converts engine activity into immutable single-step records:

   ```text
   (task_hash, target_hash, state_hash, proposed_action, engine_status,
    next_state_hash, diagnostic_code, terminal_certificate,
    generator_family, depth, branching, seed)
   ```

   Splits are made by proof skeleton, generator family, source family, and rule composition — not by random trace rows — to prevent near-duplicate leakage.

4. **Small policy LM**

   Trained from scratch with the symbolic vocabulary and typed event interface present from step 0. Its native output is an action in the engine’s closed DSL — a DSL whose existence and semantics are exactly what the API gate must demonstrate — not an unconstrained natural-language proof.

5. **Deterministic orchestration/search controller** ▷ *(step-loop CONDITIONAL)*

   Owns the frontier, duplicate-state suppression, budgets, and termination. The LM proposes or ranks actions; the engine validates transitions. This follows the PrOntoQA lesson that step production is more learnable than proof planning. `[LIT-BACKED]`

6. **Router and abstention policy** `[STIPULATED — review-1 fixes 2+3]`

   Chooses among **symbolic path, clarification, or abstention** — the direct-answer route is removed (§1.1). Engine `OUT_OF_SCOPE`, unresolved parser ambiguity (the router-level AMBIGUOUS verdict), budget exhaustion, contradictory candidate meanings, or failed renderer verification force clarification or abstention.

7. **Certified-result renderer**

   Closed-form answers use deterministic rendering. If free text is unavoidable, the result is rendered from a typed certified object and then reparsed or equivalence-checked. Failure returns the canonical result or abstains; an unchecked LM rendering must never overwrite the certified answer.

## 3. Executor-in-the-loss: precise meaning *(conditional design record — see §0)*

The engine is discrete and is not differentiated through. “Executor-in-the-loss” means that engine outcomes determine example admission, targets, feedback observations, and scalar rewards:

\[
L_\theta =
\lambda_{\text{step}}L_{\text{step}}
+\lambda_{\text{feedback}}L_{\text{feedback}}
+\lambda_{\text{state}}L_{\text{state}}
+\lambda_{\text{route}}L_{\text{route}}
-\lambda_{\text{RL}}\mathbb{E}_{a\sim\pi_\theta}[R_E(a)].
\]

Only the terms active in the registered arm are enabled; this is not initially trained as one bundled recipe. Every step-level term (`L_step`, `L_feedback` over per-step diagnostics, `L_state`) is CONDITIONAL on the §6.0 API gate `[STIPULATED — review-1 fix 1]`.

- `L_step`: next verified action, trained one step at a time rather than as whole-proof imitation. `[LIT-BACKED]` ▷
- `L_feedback`: correction after a rejected proposal and non-answer-bearing diagnostic. ▷
- `L_state`: optional exact-state or legal-action supervision, gated on the engine API. ▷
- `L_route`: solve versus abstain labels from generator-known solvability and engine coverage.
- `R_E`: terminal certificate reward, obtained through a score-function/policy-gradient estimator with the engine treated as `stop_gradient`. ▷ (trajectory semantics require the demonstrated search boundary)

Literal differentiable-executor approaches — semantic loss, black-box differentiation, DeepProbLog/Scallop-style layers — are not in the Phase-1 core. No ≥100M-LM precedent was found, and they do not transfer directly to a discrete engine. `[LIT-BACKED]`

## 4. Training ladder: no human labels — **scope: generator-pinned formal/synthetic training only** `[STIPULATED — review-1 fix 5]`

**Scope statement (load-bearing):** “no human labels” is defensible ONLY for training items whose intended formal target is generator-pinned (synthetic or oracle-formal, `target_hash` recorded at generation). It does **not** cover natural-input intent correctness: whether an NL parse matches the user’s intended meaning is exactly what this document says the engine cannot establish (§1), and no engine signal substitutes for that label. Any future natural-input training or evaluation arm re-acquires an intent-labeling obligation that this ladder does not discharge.

*The whole ladder T1–T5 is a conditional design record (§0): none of it is adopted or preregistrable before the §6.0 API gate passes. T0 is definable against the current engine but is only meaningful as the matched baseline of a gated arm.*

### T0 — matched neural baseline

The host receives the same formal problems, final-answer supervision, architecture budget, and training compute, but no proof traces, engine filtering, diagnostics, state supervision, or engine reward. Stronger compute-optimal allocation of the saved trace tokens is allowed. (T0 doubles as the **final-label-only cell** of §4a.)

### T1 — proof-trace distillation ▷

Train on engine-generated, iterative single-step traces. `[LIT-BACKED]` ProofWriter/LoGiPT support the single-step trace shape; SimpleLogic, PrOntoQA, and Faith-and-Fate require shortcut-sensitive evaluation rather than assuming that trace imitation creates a reasoner.

Mandatory shifts include:

- proof-depth extrapolation;
- branching and rule-prior shifts within the same problem space;
- held-out relation compositions;
- renamed concepts and identifiers;
- paraphrase-source shifts;
- multiple training seeds.

### T2 — executor-filtered bootstrapping ▷ `[STIPULATED — review-1 fix 4; PROPOSED-PREREG-ROW-GU-R1d]`

The model samples actions or traces. Admission to the positive replay buffer requires the CONJUNCTION of:

1. **formal validity/success** — the engine certifies the action sequence terminally; AND
2. **target binding — MANDATORY:** the certified outcome’s target hash equals the generator-recorded `target_hash` for the task.

“Formally valid success” alone is explicitly insufficient: it would admit a valid proof/action sequence for the WRONG formalization, poisoning the buffer with fluent mis-formalizations that the filter was supposed to exclude. Engine-valid but target-mismatching successes are retained only as contrastive negatives/feedback contexts, never as positives. Failed actions likewise remain available as negative/feedback contexts.

This transfers the expert-iteration, STaR, and ReST-EM rung. `[LIT-BACKED]` It improves filter precision on covered formal statements but does not repair wrong formalizations.

### T3 — RLEF retry training ▷

Construct trajectories of:

```text
proposal → engine rejection/diagnostic → corrected proposal → certificate (target-bound per T2)
```

Train the host to consume the same feedback protocol used at inference. RLEF is the direct precedent for learning feedback consumption rather than merely adding retry after training. `[LIT-BACKED]`

Diagnostics are typed and deliberately low-bandwidth. A diagnostic may identify an error class or violated constraint but may not reveal the answer-bearing record or correct next action.

### T4 — engine-reward RL ▷

Run on-policy sampling with terminal engine reward. No human preference model and no learned correctness judge are used.

RL is restricted initially to synthetic or oracle-formal items whose intended target is generator-pinned (the §4 scope statement), with reward conditioned on T2’s target binding. Applying engine reward directly to unpaired natural text is prohibited: it would reward a valid proof of a confidently wrong parse.

**Blocking precondition — statement supply:** no RL spend before the §6.0b statement-supply/diversity curve is measured and shows the generator can sustain the registered RL exposure without collapse into near-duplicates `[STIPULATED — review-1 fix 6; PROPOSED-PREREG-ROW-GU-R1b]`.

Cost, retries, and engine calls are represented as explicit constrained resources. They must not be hidden inside a reward coefficient and omitted from KOT-COST/KOT-LIFE.

### T5 — hard state interface ▷

A Discrete-NAR-style state-supervised arm is admitted only if the engine demonstrably emits canonical intermediate states and legal-action sets. `[LIT-BACKED]` It is an interface-maximal experimental arm, not an assumption about the present engine.

At R-0, T1–T5 run as separately attributable additions. A cumulative full recipe is built only from promoted components, with drop-one cells retained at R-1.

### 4a. Mandatory training-attribution cells `[STIPULATED — review-1 fix 6; PROPOSED-PREREG-ROW-GU-R1e]`

Any train-time attribution claim requires the following SEPARATE cells at **matched task, token, and compute exposure** (matched item counts, matched total training tokens including trace/diagnostic tokens replaced by length-matched filler where absent, matched optimizer budget):

| Cell | Content | Isolates |
|---|---|---|
| `C-label` | final-label-only supervision (= T0) | baseline |
| `C-trace` | genuine aligned traces (T1) | trace content |
| `C-shuf` | shuffled/mismatched traces: (a) step-order-shuffled within task; (b) trace–task mismatched pairing — both sub-variants required | token/format/curriculum-volume effects vs aligned content |
| `C-filter` | executor-filtered admission only (T2, target-bound) | admission filtering |
| `C-feedback` | rejection + typed diagnostic contexts only (T3) | feedback consumption |
| `C-reward` | terminal engine reward only (T4) | reward signal |

A gain claimed for any mechanism must beat its matched control cell (in particular `C-trace` must beat BOTH `C-shuf` sub-variants), not merely `C-label`. No cell may be inferred from another’s run; each is separately trained and separately seeded.

**Trajectory-level `Q0`/`Qsham` (fix 6):** for multi-step proof search, “first candidate” is undefined, so the sampling/selection unit is the **complete trajectory** — the full action sequence from the initial task state to termination under the frozen controller and budget. `[STIPULATED]`

- `Q0` = exactly **one trajectory per item**: one action proposal per visited state, no trajectory restarts, no trajectory-level reranking or resampling.
- `Qsham` = the full registered trajectory budget (multiple trajectories/restarts allowed), but trajectory **selection is engine-outcome-blind** (sham selection signal, information-matched to the real selection channel); within-trajectory diagnostics in the sham arm are information-matched shams per the §7 leak controls.
- The full system = the same trajectory budget as `Qsham` with genuine engine-outcome selection.

Credit for “engine-guided search” requires full > `Qsham` > (or =) `Q0` at the claim-relevant margins; full ≈ `Qsham` credits generic search quantity only.

## 5. Train-time versus inference-time causality *(conditional design record — see §0)*

The minimum causal grid is:

| | Inference engine bypassed `E0` | Inference engine active `E1` |
|---|---|---|
| Training engine signal absent `Tr0` | neural-only baseline | raw add-executor system |
| Training engine signal present `Tr1` | distilled/internalized system | full H-GU system |

This identifies four different claims:

- `Tr1,E0 − Tr0,E0`: proof-trace/filter/reward learning without runtime execution;
- `Tr0,E1 − Tr0,E0`: raw inference-time executor capability;
- `Tr1,E1 − Tr1,E0`: causal runtime engine contribution after training;
- the difference of those executor effects: whether feedback training teaches the model to use the engine more effectively.

`E0` follows the P3-D-THREAT executor-bypass definition (as revised — THREAT is itself under revision): engine work is still performed and charged but its result cannot affect generation or selection. A family-specific train-time extension, `TrE0`, similarly makes the same engine calls but prevents outcomes from controlling filtering, feedback, or reward. The §4a cells refine `Tr1` into separately attributable mechanism cells.

Without this grid, a successful distilled model could be mislabeled an executor win, or a runtime engine win could be mislabeled proof-trace internalization.

## 6. Gate ladder

### 6.0 Blocking pre-G1 step-transition API gate — **the ONLY prereg-ready item** `[STIPULATED — review-1 fix 1; PROPOSED-PREREG-ROW-GU-R1a]`

Before ANY step-level arm may be preregistered, a blocking gate must demonstrate, against the versioned engine actually deployed (not a mock, not this document’s schema):

1. a closed, documented **action DSL** the host can emit;
2. explicit **proof-state semantics**: canonical state objects with stable hashes;
3. a **transition function**: `(state, action) → (next_state | REJECT)` with deterministic replay;
4. a **certificate condition**: what terminal object certifies `SOLVED`, and its verification procedure;
5. an explicit **search boundary**: which of frontier management, duplicate suppression, and termination the engine owns versus the orchestrator;
6. **legal-action/continuation enumeration** where a T5-style arm is selected;
7. per-step **diagnostic codes** satisfying the non-answer-bearing constraint.

Missing functionality blocks the dependent arm — a missing interface removes the feature; it never becomes an asserted capability. µs terminal checking is not evidence any of these exist. **Until this gate passes, the full trace/filter/RLEF/RL recipe of §§2–5 and the T1–T5 ladder are conditional design record only and MUST NOT be preregistered as executable arms.**

### 6.0b Statement-supply/diversity curve — prereg-ready companion `[STIPULATED — review-1 fix 6; PROPOSED-PREREG-ROW-GU-R1b]`

Also preregistrable now (it exercises only the generator + terminal engine): measure the seeded generator’s statement-supply and diversity curve — unique tasks, unique proof skeletons, and inter-task near-duplicate rate as a function of generation budget, per generator family. This curve is a **blocking precondition for any RL spend** (§4 T4) and calibrates the matched curriculum-volume controls of §4a. A plateauing supply curve must not later be attributed to model scale or executor properties (§7).

### 6.1 Programme ladder *(conditional on §6.0 for all step-level content)*

- **G1 coverage ceiling:** determine whether perfect engine use can affect enough items to matter. Under efficiency-W1, use the existing `Δ_max` calculation. Under a correctness framing, the corresponding correctness–coverage envelope remains for #57/framework.
- **G2 oracle interface:** use gold formal inputs. Test trace learning, engine reward, state use, shift robustness, and the `Tr×E` grid. This is `oracle-diagnostic`, not W1.
- **G3 boundary degradation:** introduce the NLB parser, calibrated abstention, and stage-wise oracle ablations. Report parse, addressing, execution, search, and renderer losses separately.
- **G4 full system:** compare against the frozen frontier and all P3-D-THREAT arms (as revised).
- **G5 scale:** test whether the interface effect grows, remains flat, or shrinks across the registered sweep.

A flat or shrinking matched-resource effect kills the efficiency interpretation. It does not erase a separately established covered-scope correctness capability.

## 7. Seams, failure modes, and causal controls *(conditional design record; THREAT factor definitions apply as revised)*

| Seam / failure mode | Required P3-D-THREAT isolation | Consequence |
|---|---|---|
| Trace content is aligned by chance | `D`, `P`, `I` + §4a `C-shuf` | Failure against any kills aligned-content/semantic attribution |
| Model matches linearized proof patterns rather than rule structure | `G-edge`, `G-rel`, `G-adv` plus depth/composition shifts | Robustness to attacks kills structural-reasoning wording |
| Extra trace tokens or cleaner data—not engine semantics—cause the gain | `I`, `TrE0`, §4a matched-exposure cells, strongest compute-matched T0 allocation | Credit only generic data/curriculum |
| Engine runs but does not affect behavior | `E0` with trajectory-level `Q0` in both cells | No deterministic-execution claim |
| Retry/search is ordinary best-of-k sampling | trajectory-level `Q0`, `Qsham` (§4a) | Credit generic search unless full beats `Qsham` |
| Diagnostics leak the correct answer | `TrE0` with matched sham diagnostics; trajectory-level `Qsham` | RLEF claim invalid if low-information sham performs similarly |
| Valid proof of the wrong formalization admitted as positive | T2 `target_hash` binding (mandatory) | Buffer/RL poisoning; any T2+ claim invalid without the binding |
| Typed records or generic tools are sufficient | `T*` (as split by the THREAT revision) | Credit aligned typed storage/tooling, not kernel semantics |
| Conventional retrieval supplies the same capability | `R*` | W1 fails against the RAG/tool frontier |
| Native symbolic tokens add nothing over text | `X*` (conditional per THREAT revision) | Credit engine information delivered as text, not native integration |
| Proof graph/topology is ornamental | `G-edge`, `G-rel`, `G-adv` | No graph/rule-composition claim |
| Engine certifies the wrong NL formalization | `P` and `D` stress meaning/address alignment; G2→G3 oracle decomposition | Engine correctness survives only at formal scope; real-input claim blocked |
| Renderer corrupts a certified result | `X` instantiated with canonical-result text, plus a family-specific deterministic-renderer cell | Free-form renderer is removed or forced to abstain |
| Calibrator misses confident inversions | `P`, symmetric inverse tests, and strongest `R/T` selective baseline | No S2 claim from average calibration alone |
| Engine coverage is too narrow | G1 and comparison with `R*` | Kill before training or scope the result to the covered slice |
| Engine-generated statement supply plateaus | §6.0b supply/diversity curve; `I` and matched curriculum-volume controls | Do not attribute saturation to model scale or executor speed; no RL spend past the measured supply |
| Train-time and inference-time engine effects interact | `Tr×E`, plus semantics×executor and integration×executor interactions | Report the interaction; do not allocate it post hoc |

The core engine claim therefore requires, at minimum:

\[
F>D,P,I,T^*,R^*,X^*,E0,Q0,Qsham
\]

at the claim-relevant margins (with `Q0`/`Qsham` defined at trajectory level per §4a), plus all three `G-*` attacks whenever proof/rule structure is named. No large contrast against one arm compensates for failure against another.

## 8. Selective prediction seam

Selective prediction is part of the system, not an evaluation afterthought. `[LIT-BACKED]`

Report the whole risk–coverage curve and freeze the operating threshold before final evaluation. Confidence inputs may include parser uncertainty, engine coverage state, candidate disagreement, retry count, proof depth, and renderer verification—but engine acceptance alone is not a confidence score for intended NL meaning.

Conformal or risk-controlled calibration must be tested under disjoint phrasing sources. Exchangeability failure and systematic confident inversion are explicit failure strata. The exact dangerous-wrong definition, threshold, confidence bound, and rare-event sample size remain deferred.

## 9. Connection to the F1-K correctness thesis

F1-K is an **activation carrier/splice experiment**, not an inference-time proof or query verifier (review-1 header correction); only analogy-level question mapping is intended here — no F1-K machinery, seam, or result is inherited. F1-K’s current deflator ladder asks whether:

- **K-1:** injected content beats the unmodified host;
- **K-2:** true concept alignment beats dose-matched derangement;
- **K-3:** kernel-authored content beats a matched plain-dictionary null.

That ladder is specified in the [F1-K design](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/glm52-followup-experiment.md:274). H-GU addresses the broader correctness question at a different seam:

| F1-K question | H-GU analogue |
|---|---|
| Does added content help? | `Tr1,E0` versus `Tr0,E0` |
| Does true alignment matter? | `D`, `P`, and `I` |
| Is the effect kernel-specific? | Full system versus `T*`, supported by `R*` |
| Does a privileged internal seam help? | Native typed interface versus `X*` |
| Is deterministic execution itself causal? | `E1` versus `E0`, absent from the F1-K carrier test |
| Does training teach engine use? | `Tr×E` interaction and RLEF drop-one arm |

Thus H-GU can support the correctness thesis in the following narrow form:

> On the covered formal slice, a small host trained to use an external deterministic engine produces more engine-certified, semantically correct outcomes—or fewer accepted soundness violations—than the same host without access to engine outcomes, at stated coverage and cost.

It cannot inherit an F1-K result, prove that kernel explications outperform dictionaries, prove natural-language intent correctness, or claim general intelligence. If `T*` matches the kernel system, the add-capability result may remain real but is attributed to a generic typed executor rather than kernel-specific semantics. If `E0` matches the full system, the result is trace distillation/internalization, not an inference-time engine capability.

## 10. Framing fork retained

Under the **efficiency-W1 framing**:

- full KOT-SIZE/KOT-COST/KOT-LIFE accounting binds;
- `R*` is a frontier comparator;
- the ≥3-point scale-direction sweep is decisive;
- flat-negative or shrinking interface effects kill the efficiency reading;
- engine speed is credited only for the cost term it actually removes.

Under the **correctness-endpoint framing**:

- engine-certified correctness, dangerous-wrong probability, selective risk, coverage, provenance-backed soundness violations, and end-to-end semantics become candidate endpoints;
- the executor may establish a valuable add-capability even without improving a matched-resource index;
- coverage and cost remain part of the claim rather than disappearing.

This proposal chooses neither framing. In BOTH framings H-GU remains an add-capability architecture: no matched-resource superiority is asserted anywhere in this document.

## Review-gate hand-off

### Adopted NOW (the only adoption)

`[STIPULATED — review-1 fix 1]` Adopt ONLY:

1. the blocking **pre-G1 step-transition API gate** (§6.0) as the sole prereg-ready H-GU item (PROPOSED-PREREG-ROW-GU-R1a); and
2. the **statement-supply/diversity curve** measurement (§6.0b) as its prereg-ready companion and RL-spend precondition (PROPOSED-PREREG-ROW-GU-R1b).

### Adopted CONDITIONALLY — on the §6.0 gate passing, and NOT before

`[STIPULATED — review-1 fix 1]` Conditional on the demonstrated step-transition API (action DSL + state semantics + transition function + certificate condition + search boundary), adopt **H-GU/PTD-EIL** as a from-scratch small policy LM with a typed symbolic interface present from step 0, trained through single-step proof-trace distillation, target-bound executor-filtered self-training, RLEF correction trajectories, and terminal engine reward — with the §4a attribution cells and trajectory-level `Q0`/`Qsham`. Retain the deterministic engine at inference as the sole formal answer authority (no uncertified direct-answer route, §1.1). Use a deterministic controller for bounded search and a fail-closed renderer/clarification/abstention layer. The prior draft’s unconditional adoption of this full recipe is **withdrawn**.

The “no human labels” property of the conditional training plane is scoped to generator-pinned formal/synthetic training only; it does not cover natural-input intent correctness `[STIPULATED — review-1 fix 5]`.

### `[STIPULATED — coordinator/Fable to ratify]` values *(values marked ▷ are conditional on the §6.0 gate)*

- `[STIPULATED — coordinator/Fable to ratify]` ▷ Initial width sweep: approximately 30M, 70M, and 135M trainable parameters, with matched from-scratch baselines at each width.
- `[STIPULATED — coordinator/Fable to ratify]` ▷ Start with three training seeds per cell; increase before output inspection if power calibration requires it.
- `[STIPULATED — coordinator/Fable to ratify]` ▷ Train on proof depths 1–4 and branching 1–3; reserve depths 5, 6, and 8 plus branching 4–6 for extrapolation tests.
- `[STIPULATED — coordinator/Fable to ratify]` ▷ Maximum four trajectories per inference item at R-0/R-1; `Q0` receives exactly one trajectory and `Qsham` the same maximum four with engine-outcome-blind selection (trajectory-level definitions per §4a).
- `[STIPULATED — coordinator/Fable to ratify]` ▷ Use terminal binary engine certification, target-bound per T2, as the RL correctness reward; no human reward, learned correctness judge, or engine-only RL on unpaired natural inputs; no RL spend before the §6.0b supply curve.
- `[STIPULATED — coordinator/Fable to ratify]` Rejection diagnostics use the four-status ENGINE schema of §2.2 (`VALID_STEP`/`SOLVED`/`REJECT`/`OUT_OF_SCOPE`; `AMBIGUOUS` is router-layer only) and may not contain an answer-bearing record or gold next action.
- `[STIPULATED — coordinator/Fable to ratify]` ▷ Run the `Tr0/Tr1 × E0/E1` grid with the §4a mechanism cells (`C-label`/`C-trace`/`C-shuf`/`C-filter`/`C-feedback`/`C-reward`) at matched task/token/compute exposure; isolate each addition before combining.
- `[STIPULATED — coordinator/Fable to ratify]` Use at least three disjoint phrasing sources for G3 calibration/evaluation and report source-specific risk–coverage curves.
- `[STIPULATED — coordinator/Fable to ratify]` Inherit P3-D-THREAT’s SHA-256 seed derivation, five initial perturbation replicates, no rerolling, equal byte entitlement without padding, and public-plus-sealed control execution — as amended by the pending THREAT revision (a framework blocker).
- `[STIPULATED — coordinator/Fable to ratify]` Under efficiency-W1 only, inherit `δ_attr,k = δ_k`; no correctness-specific margin is proposed here.

### DEFERRED to #57 and the framework revision

- Whether correctness is a second success claim, a conjunctive W1 gate, or a correctness–coverage–cost Pareto axis.
- The efficiency-W1 versus correctness-endpoint win condition.
- KOT-FAIR/2 and KOT-AI-INDEX/2 evaluation preregistration, comparator freeze, weights, multiplicity, and sealed-evaluation protocol.
- Correctness margins, S2 definition, selective-risk operating point, coverage threshold, confidence rule, and rare-event sample sizes.
- Any change to F1-K/K-3’s verdict-bearing role resulting from #57’s correctness re-weighting.
- Promotion beyond R-1/R-2 and any W1/W2 claim.

## PROPOSED prereg rows (labels only — nothing registered)

All rows are PROPOSED only — nothing is registered, frozen, or scheduled; no `ASM-<number>` ids are minted here (those are assigned at prereg-freeze). Labels are `GU-`prefixed to stay disjoint from the sibling H-PS (`PROPOSED-PREREG-ROW-R1a…e`) and H-VL (`PROPOSED-PREREG-ROW-VL-R1a…e`) revisions.

- **PROPOSED-PREREG-ROW-GU-R1a:** step-transition API-gate law — the blocking pre-G1 gate of §6.0 (demonstrated action DSL, canonical state semantics, deterministic transition function, certificate condition, explicit search boundary, non-answer-bearing per-step diagnostics; legal-action enumeration where a T5 arm is selected) is the ONLY prereg-ready H-GU item; the full trace/filter/RLEF/RL recipe (T1–T5, §§2–5) is CONDITIONAL on this gate and MUST NOT be preregistered as executable arms before it passes; a missing interface removes the feature, it never becomes an asserted capability. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-GU-R1b:** statement-supply law — the seeded generator’s statement-supply/diversity curve (unique tasks, unique proof skeletons, near-duplicate rate vs generation budget, per family) is measured and preregistered before any RL spend; RL exposure may not exceed the measured non-collapsed supply; supply plateaus are never attributed to model scale or executor properties. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-GU-R1c:** answer-authority law — the retained engine is the sole formal answer authority; the direct-answer route is removed; H-GU’s licensed result set = engine-certified results only, plus fail-closed clarification/abstention; any uncertified host answer is a scored violation; `AMBIGUOUS` is an NL/router-layer verdict, never an engine status (engine schema is four-status), admissible engine-side only if a future formal task language explicitly represents ambiguity. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-GU-R1d:** T2 target-binding law — admission to any positive replay buffer, RLEF success terminus, or RL reward requires engine certification AND `target_hash` equality with the generator-recorded intended target; engine-valid target-mismatching successes are contrastive negatives only; “formally valid success” alone never admits a positive. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-GU-R1e:** training-attribution law — any train-time mechanism claim requires the separate `C-label`/`C-trace`/`C-shuf`(both sub-variants)/`C-filter`/`C-feedback`/`C-reward` cells at matched task/token/compute exposure, separately trained and seeded; and `Q0`/`Qsham` are defined at TRAJECTORY level (one complete trajectory per item for `Q0`; engine-outcome-blind selection over the matched trajectory budget for `Qsham`) — “first candidate” is undefined for multi-step proof search. `[STIPULATED]`

## Revision 1 — review fixes applied

Authoritative source: [p3-arch-family-review1.md §H-GU](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3-arch-family-review1.md) + the review header’s cross-draft corrections.

1. **Central re-scope (not yet an architecture over the current engine) — ADOPTED.** New §0 makes the gap load-bearing: the current engine is terminal-only (`kot-query/1` in, answer/refusal out; no proof-search transition system); ONLY the §6.0 API gate + §6.0b statement-supply curve are prereg-ready now; the full trace/filter/RLEF/RL recipe — previously adopted unconditionally in the hand-off — is withdrawn from adoption and made explicitly CONDITIONAL on the gate; §§2–5/7 re-labelled conditional design record; the §6.0 gate expanded into a seven-point demonstrated-artifact checklist; hand-off split into “Adopted NOW” vs “Adopted CONDITIONALLY”. (PROPOSED-PREREG-ROW-GU-R1a/R1b)
2. **Authority conflict (direct-answer route) — ADOPTED (removal option declared).** §1.1: the direct-answer route is removed; licensed result set = engine-certified results + fail-closed clarification/abstention only; the certification alternative is explicitly rejected (it would duplicate the symbolic path or create a second answer authority — mirroring H-PS R1d’s rationale). §1 model contributions and §2.6 router updated accordingly. (PROPOSED-PREREG-ROW-GU-R1c)
3. **`AMBIGUOUS` placement — ADOPTED.** Removed from the engine reply schema (now four-status); ambiguity is owned by the NL/router layer and resolves fail-closed to clarification/abstention; an engine-side status is admissible only if a future formal task language explicitly represents ambiguity (none exists or is proposed). Stipulated diagnostic value updated from “five-status” to “four-status”. (PROPOSED-PREREG-ROW-GU-R1c)
4. **T2 target-binding — ADOPTED.** `target_hash` equality with the generator-recorded target is MANDATORY for positive admission (and propagated to the RLEF success terminus and RL reward); engine-valid target-mismatching successes demoted to contrastive negatives; `target_hash` added to the trace-record schema; new seam-table row for wrong-formalization buffer poisoning. (PROPOSED-PREREG-ROW-GU-R1d)
5. **“No human labels” scope — ADOPTED.** §4 heading and a load-bearing scope statement restrict the property to generator-pinned formal/synthetic training; natural-input intent correctness is explicitly NOT covered (consistent with §1’s own statement that the engine cannot establish it); restated in the hand-off. No PROPOSED row needed — it is a scope statement, not a new gate.
6. **Attribution cells + trajectory-level `Q0`/`Qsham` + supply curve — ADOPTED.** New §4a: six separate cells (final-label-only / genuine-trace / shuffled-AND-mismatched-trace / filter / feedback / reward) at matched task/token/compute exposure, each separately trained/seeded, with `C-trace` required to beat both `C-shuf` sub-variants; trajectory-level `Q0`/`Qsham` definitions (whole-trajectory unit; engine-outcome-blind sham selection); §6.0b statement-supply/diversity curve required before any RL spend, wired into T4 and the seam table. (PROPOSED-PREREG-ROW-GU-R1b/R1e)

Cross-draft corrections from the review header: the stale-a5/`ROLE_DIR` correction does not apply (this draft never cited the a5 mechanism); the F1-K correction is applied in §9 (F1-K stated as an activation carrier/splice experiment; analogy-level mapping only, no inheritance). `[SV]` tags mapped to the programme four-tag scheme (header note). Add-capability framing re-affirmed in §10 and the status header.

## MANDATORY self-check (Revision 1)

1. **All 6 review issues addressed?** YES — itemised above: re-scope (§0, §6.0, hand-off), authority conflict (§1.1), AMBIGUOUS placement (§2.2), T2 target-binding (§4 T2), no-human-labels scope (§4 preamble), attribution cells + trajectory-level `Q0`/`Qsham` + supply curve (§4a, §6.0b).
2. **Full trace/RL recipe explicitly gated on the non-existent step-transition API?** YES — §0 item 2, the ▷ markers throughout §§1–5, the seven-point §6.0 gate, the “Adopted CONDITIONALLY” hand-off block, and PROPOSED-PREREG-ROW-GU-R1a all state the recipe is conditional and NOT adopted now; the prior unconditional adoption is explicitly withdrawn.
3. **Every load-bearing claim tagged?** YES — literature-derived choices carry `[LIT-BACKED]` (mapped from the prior draft’s `[SV]`); the terminal-only engine fact carries `[MEASURED]` with source (review 1 / kot_axiom.py); all design choices carry `[STIPULATED]`; `[EXTRAPOLATION]` is deliberately unused (no forward performance claims pending #57).
4. **No `[MEASURED]` on a choice?** YES — `[MEASURED]` appears only on the observed engine surface (whole-query terminal answers/refusals, five terminal operations, no transition system); every prescription derived from it (the gate, the re-scope, the conditional labelling) is `[STIPULATED]`.
5. **No @handle/account strings?** YES — none present.
6. **No `ASM-<number>` ids minted?** YES — only `PROPOSED-PREREG-ROW-GU-R1a…e` labels; the PROPOSED-rows section states ids are assigned at prereg-freeze.
7. **Nothing committed/registered/frozen?** YES — status header and hand-off state nothing is frozen, registered, scheduled, or committed; this file edit is the only change; no repository issue/experiment state was touched.
8. **Add-capability framing intact?** YES — §1 status line, §10 closing statement, and the review-1 finding that H-GU “explicitly adopts the add-capability result” are preserved; no matched-resource superiority claim is asserted anywhere.

No repository files other than this document, no issue state, and no experiment records were changed.
