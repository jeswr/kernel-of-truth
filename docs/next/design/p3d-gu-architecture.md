# P3-D-GU: H-GU proof-trace-distillation + executor-in-the-loss architecture — GPT-5.6 DRAFT

> **STATUS: UNREVIEWED GPT-5.6 DRAFT.** 2026-07-19, Programme-3 Phase-1 (overflow-Fable). Crux-VALIDATED
> add-capability architecture (per #57 Phase-0). ARCHITECTURE + training + seams only; the win-condition
> (efficiency-W1 vs correctness-endpoint) + KOT-FAIR/2 eval-prereg are DEFERRED to the maintainer's #57
> re-weighting + the framework revision. NEXT: review gate -> Fable critique -> prereg. Not frozen.
> Source: poc/gpt56-review/p3d-gu-design/.

---

# H-GU proof-trace distillation + executor-in-the-loss

Status: **PROPOSAL for review gate and Fable**. It accepts #57’s Phase-0 crux result as an input: H-GU is an **ADD-CAPABILITY** architecture in which the deterministic engine supplies exact execution/checking that the neural host structurally lacks. It does not decide whether success is framed as efficiency-W1 or as a correctness endpoint.

The proposal instantiates [H-GU](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:752), reuses the inference topology of [H-VL](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:614), and follows the causal controls in [P3-D-THREAT](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md:96).

## 1. Architectural claim

H-GU is not “distil the engine until the engine can be removed.” It is:

> Train a small model from step 0 to propose engine-readable actions, consume exact engine feedback, and abstain when the engine cannot certify a result; retain the engine at inference as the sole formal answer authority over its covered grammar.

The engine contributes:

- exact validation and state transitions;
- legal-action or continuation sets, where available;
- proof traces and certificates;
- deterministic error codes;
- final accept/reject/abstain decisions;
- a no-human-label data filter and training reward.

The model contributes:

- natural-language parsing, subject to the NLB gate;
- formal action/subgoal proposal;
- ranking of candidate actions;
- consumption of engine diagnostics across retries;
- selective routing between direct, symbolic, and abstain paths;
- constrained verbalization of certified results.

The engine does **not** establish that an NL parse matches the user’s intent, resolve genuine ambiguity, supply open-world truth, or guarantee renderer fidelity. It is sound only relative to the submitted formal statement, frozen rules, and covered grammar.

## 2. Components and data flow

```text
natural input
    │
    ▼
untrusted NLB parser + confidence gate
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
                                                  answer or abstain
```

The training plane shares the same engine protocol:

```text
seeded curriculum generator
    │
    ▼
engine enumeration / execution
    │ exact states, steps, certificates
    ▼
trace compiler ──► single-step distillation corpus
    │
host-generated candidates ──► engine filter ──► verified replay buffer
    │
failed candidate + diagnostic + later success ──► RLEF correction corpus
    │
on-policy candidate ──► terminal engine reward ──► policy-gradient update
```

### Required components

1. **Seeded curriculum generator**

   Generates formal tasks with controlled rule depth, branching, polarity, distractor density, proof multiplicity, relation composition, and paraphrase provenance. The generator records the intended formal target, so an engine-valid solution to the wrong formalization cannot be mislabeled correct during synthetic training.

2. **Deterministic engine service**

   A versioned, fail-closed service. It must expose more than final checking before the corresponding training arm exists.

   Proposed reply schema:

   - `VALID_STEP`
   - `SOLVED`
   - `REJECT`
   - `OUT_OF_SCOPE`
   - `AMBIGUOUS`

   Each reply carries state and request hashes, provenance, engine version, charged runtime, and—where applicable—a proof fragment or certificate. Rejection diagnostics must not leak the gold next action or answer.

3. **Trace compiler**

   Converts engine activity into immutable single-step records:

   ```text
   (task_hash, state_hash, proposed_action, engine_status,
    next_state_hash, diagnostic_code, terminal_certificate,
    generator_family, depth, branching, seed)
   ```

   Splits are made by proof skeleton, generator family, source family, and rule composition—not by random trace rows—to prevent near-duplicate leakage.

4. **Small policy LM**

   Trained from scratch with the symbolic vocabulary and typed event interface present from step 0. Its native output is an action in the engine’s closed DSL, not an unconstrained natural-language proof.

5. **Deterministic orchestration/search controller**

   Owns the frontier, duplicate-state suppression, budgets, and termination. The LM proposes or ranks actions; the engine validates transitions. This follows the PrOntoQA lesson that step production is more learnable than proof planning. `[SV]`

6. **Router and abstention policy**

   Chooses among direct answer, symbolic path, clarification, or abstention. Engine `OUT_OF_SCOPE`, unresolved parser ambiguity, budget exhaustion, contradictory candidate meanings, or failed renderer verification force abstention.

7. **Certified-result renderer**

   Closed-form answers use deterministic rendering. If free text is unavoidable, the result is rendered from a typed certified object and then reparsed or equivalence-checked. Failure returns the canonical result or abstains; an unchecked LM rendering must never overwrite the certified answer.

## 3. Executor-in-the-loss: precise meaning

The engine is discrete and is not differentiated through. “Executor-in-the-loss” means that engine outcomes determine example admission, targets, feedback observations, and scalar rewards:

\[
L_\theta =
\lambda_{\text{step}}L_{\text{step}}
+\lambda_{\text{feedback}}L_{\text{feedback}}
+\lambda_{\text{state}}L_{\text{state}}
+\lambda_{\text{route}}L_{\text{route}}
-\lambda_{\text{RL}}\mathbb{E}_{a\sim\pi_\theta}[R_E(a)].
\]

Only the terms active in the registered arm are enabled; this is not initially trained as one bundled recipe.

- `L_step`: next verified action, trained one step at a time rather than as whole-proof imitation. `[SV]`
- `L_feedback`: correction after a rejected proposal and non-answer-bearing diagnostic.
- `L_state`: optional exact-state or legal-action supervision, gated on the engine API.
- `L_route`: solve versus abstain labels from generator-known solvability and engine coverage.
- `R_E`: terminal certificate reward, obtained through a score-function/policy-gradient estimator with the engine treated as `stop_gradient`.

Literal differentiable-executor approaches—semantic loss, black-box differentiation, DeepProbLog/Scallop-style layers—are not in the Phase-1 core. No ≥100M-LM precedent was found, and they do not transfer directly to a discrete engine. `[SV]`

## 4. Training ladder: no human labels

### T0 — matched neural baseline

The host receives the same formal problems, final-answer supervision, architecture budget, and training compute, but no proof traces, engine filtering, diagnostics, state supervision, or engine reward. Stronger compute-optimal allocation of the saved trace tokens is allowed.

### T1 — proof-trace distillation

Train on engine-generated, iterative single-step traces. `[SV]` ProofWriter/LoGiPT support the single-step trace shape; SimpleLogic, PrOntoQA, and Faith-and-Fate require shortcut-sensitive evaluation rather than assuming that trace imitation creates a reasoner.

Mandatory shifts include:

- proof-depth extrapolation;
- branching and rule-prior shifts within the same problem space;
- held-out relation compositions;
- renamed concepts and identifiers;
- paraphrase-source shifts;
- multiple training seeds.

### T2 — executor-filtered bootstrapping

The model samples actions or traces. The engine admits only formally valid successes to the positive replay buffer; failed actions remain available as negative/feedback contexts.

This transfers the expert-iteration, STaR, and ReST-EM rung. `[SV]` It improves filter precision on covered formal statements but does not repair wrong formalizations.

### T3 — RLEF retry training

Construct trajectories of:

```text
proposal → engine rejection/diagnostic → corrected proposal → certificate
```

Train the host to consume the same feedback protocol used at inference. RLEF is the direct precedent for learning feedback consumption rather than merely adding retry after training. `[SV]`

Diagnostics are typed and deliberately low-bandwidth. A diagnostic may identify an error class or violated constraint but may not reveal the answer-bearing record or correct next action.

### T4 — engine-reward RL

Run on-policy sampling with terminal engine reward. No human preference model and no learned correctness judge are used.

RL is restricted initially to synthetic or oracle-formal items whose intended target is generator-pinned. Applying engine reward directly to unpaired natural text is prohibited: it would reward a valid proof of a confidently wrong parse.

Cost, retries, and engine calls are represented as explicit constrained resources. They must not be hidden inside a reward coefficient and omitted from KOT-COST/KOT-LIFE.

### T5 — hard state interface

A Discrete-NAR-style state-supervised arm is admitted only if the engine demonstrably emits canonical intermediate states and legal-action sets. `[SV]` It is an interface-maximal experimental arm, not an assumption about the present engine.

At R-0, T1–T5 run as separately attributable additions. A cumulative full recipe is built only from promoted components, with drop-one cells retained at R-1.

## 5. Train-time versus inference-time causality

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

`E0` follows the P3-D-THREAT executor-bypass definition: engine work is still performed and charged but its result cannot affect generation or selection. A family-specific train-time extension, `TrE0`, similarly makes the same engine calls but prevents outcomes from controlling filtering, feedback, or reward.

Without this grid, a successful distilled model could be mislabeled an executor win, or a runtime engine win could be mislabeled proof-trace internalization.

## 6. Gate ladder

A blocking **pre-G1 API gate** first demonstrates that the engine emits every artifact consumed by the selected arms: proof states, transitions, legal-action sets, trace steps, diagnostics, and certificates. Missing functionality blocks only the dependent arm; µs final checking is not evidence those APIs exist.

Then apply the programme ladder:

- **G1 coverage ceiling:** determine whether perfect engine use can affect enough items to matter. Under efficiency-W1, use the existing `Δ_max` calculation. Under a correctness framing, the corresponding correctness–coverage envelope remains for #57/framework.
- **G2 oracle interface:** use gold formal inputs. Test trace learning, engine reward, state use, shift robustness, and the `Tr×E` grid. This is `oracle-diagnostic`, not W1.
- **G3 boundary degradation:** introduce the NLB parser, calibrated abstention, and stage-wise oracle ablations. Report parse, addressing, execution, search, and renderer losses separately.
- **G4 full system:** compare against the frozen frontier and all P3-D-THREAT arms.
- **G5 scale:** test whether the interface effect grows, remains flat, or shrinks across the registered sweep.

A flat or shrinking matched-resource effect kills the efficiency interpretation. It does not erase a separately established covered-scope correctness capability.

## 7. Seams, failure modes, and causal controls

| Seam / failure mode | Required P3-D-THREAT isolation | Consequence |
|---|---|---|
| Trace content is aligned by chance | `D`, `P`, `I` | Failure against any kills aligned-content/semantic attribution |
| Model matches linearized proof patterns rather than rule structure | `G-edge`, `G-rel`, `G-adv` plus depth/composition shifts | Robustness to attacks kills structural-reasoning wording |
| Extra trace tokens or cleaner data—not engine semantics—cause the gain | `I`, `TrE0`, strongest compute-matched T0 allocation | Credit only generic data/curriculum |
| Engine runs but does not affect behavior | `E0` with `Q0` in both cells | No deterministic-execution claim |
| Retry is ordinary best-of-k sampling | `Q0`, `Qsham` | Credit generic search unless full beats `Qsham` |
| Diagnostics leak the correct answer | `TrE0` with matched sham diagnostics; `Qsham` | RLEF claim invalid if low-information sham performs similarly |
| Typed records or generic tools are sufficient | `T*` | Credit aligned typed storage/tooling, not kernel semantics |
| Conventional retrieval supplies the same capability | `R*` | W1 fails against the RAG/tool frontier |
| Native symbolic tokens add nothing over text | `X*` | Credit engine information delivered as text, not native integration |
| Proof graph/topology is ornamental | `G-edge`, `G-rel`, `G-adv` | No graph/rule-composition claim |
| Engine certifies the wrong NL formalization | `P` and `D` stress meaning/address alignment; G2→G3 oracle decomposition | Engine correctness survives only at formal scope; real-input claim blocked |
| Renderer corrupts a certified result | `X` instantiated with canonical-result text, plus a family-specific deterministic-renderer cell | Free-form renderer is removed or forced to abstain |
| Calibrator misses confident inversions | `P`, symmetric inverse tests, and strongest `R/T` selective baseline | No S2 claim from average calibration alone |
| Engine coverage is too narrow | G1 and comparison with `R*` | Kill before training or scope the result to the covered slice |
| Engine-generated statement supply plateaus | `I` and matched curriculum-volume controls | Do not attribute saturation to model scale or executor speed |
| Train-time and inference-time engine effects interact | `Tr×E`, plus semantics×executor and integration×executor interactions | Report the interaction; do not allocate it post hoc |

The core engine claim therefore requires, at minimum:

\[
F>D,P,I,T^*,R^*,X^*,E0,Q0,Qsham
\]

at the claim-relevant margins, plus all three `G-*` attacks whenever proof/rule structure is named. No large contrast against one arm compensates for failure against another.

## 8. Selective prediction seam

Selective prediction is part of the system, not an evaluation afterthought. `[SV]`

Report the whole risk–coverage curve and freeze the operating threshold before final evaluation. Confidence inputs may include parser uncertainty, engine coverage state, candidate disagreement, retry count, proof depth, and renderer verification—but engine acceptance alone is not a confidence score for intended NL meaning.

Conformal or risk-controlled calibration must be tested under disjoint phrasing sources. Exchangeability failure and systematic confident inversion are explicit failure strata. The exact dangerous-wrong definition, threshold, confidence bound, and rare-event sample size remain deferred.

## 9. Connection to the F1-K correctness thesis

F1-K’s current deflator ladder asks whether:

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

This proposal chooses neither framing.

## Review-gate hand-off

### Architecture

Adopt **H-GU/PTD-EIL** as a from-scratch small policy LM with a typed symbolic interface present from step 0, trained through single-step proof-trace distillation, executor-filtered self-training, RLEF correction trajectories, and terminal engine reward. Retain the deterministic engine at inference as the sole formal answer authority. Use a deterministic controller for bounded search and a fail-closed renderer/abstention layer.

### `[STIPULATED — coordinator/Fable to ratify]` values

- `[STIPULATED — coordinator/Fable to ratify]` Initial width sweep: approximately 30M, 70M, and 135M trainable parameters, with matched from-scratch baselines at each width.
- `[STIPULATED — coordinator/Fable to ratify]` Start with three training seeds per cell; increase before output inspection if power calibration requires it.
- `[STIPULATED — coordinator/Fable to ratify]` Train on proof depths 1–4 and branching 1–3; reserve depths 5, 6, and 8 plus branching 4–6 for extrapolation tests.
- `[STIPULATED — coordinator/Fable to ratify]` Maximum four model proposals per inference item at R-0/R-1; `Q0` receives one and `Qsham` the same maximum four.
- `[STIPULATED — coordinator/Fable to ratify]` Use terminal binary engine certification as the RL correctness reward; no human reward, learned correctness judge, or engine-only RL on unpaired natural inputs.
- `[STIPULATED — coordinator/Fable to ratify]` Rejection diagnostics use the five-status schema above and may not contain an answer-bearing record or gold next action.
- `[STIPULATED — coordinator/Fable to ratify]` Run the `Tr0/Tr1 × E0/E1` grid and separately isolate trace, filter, RLEF, RL, and hard-state additions before combining them.
- `[STIPULATED — coordinator/Fable to ratify]` Use at least three disjoint phrasing sources for G3 calibration/evaluation and report source-specific risk–coverage curves.
- `[STIPULATED — coordinator/Fable to ratify]` Inherit P3-D-THREAT’s SHA-256 seed derivation, five initial perturbation replicates, no rerolling, equal byte entitlement without padding, and public-plus-sealed control execution.
- `[STIPULATED — coordinator/Fable to ratify]` Under efficiency-W1 only, inherit `δ_attr,k = δ_k`; no correctness-specific margin is proposed here.

### DEFERRED to #57 and the framework revision

- Whether correctness is a second success claim, a conjunctive W1 gate, or a correctness–coverage–cost Pareto axis.
- The efficiency-W1 versus correctness-endpoint win condition.
- KOT-FAIR/2 and KOT-AI-INDEX/2 evaluation preregistration, comparator freeze, weights, multiplicity, and sealed-evaluation protocol.
- Correctness margins, S2 definition, selective-risk operating point, coverage threshold, confidence rule, and rare-event sample sizes.
- Any change to F1-K/K-3’s verdict-bearing role resulting from #57’s correctness re-weighting.
- Promotion beyond R-1/R-2 and any W1/W2 claim.

No repository files, issue state, or experiment records were changed.