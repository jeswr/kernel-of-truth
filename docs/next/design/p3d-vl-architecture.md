# P3-D-VL: H-VL verifier-loop (small host + kernel verify/retry) architecture — GPT-5.6 DRAFT

> **STATUS: UNREVIEWED GPT-5.6 DRAFT.** 2026-07-19, Programme-3 Phase-1 (overflow-Fable). Crux-VALIDATED
> add-capability architecture (per #57 Phase-0). ARCHITECTURE + training + seams only; the win-condition
> (efficiency-W1 vs correctness-endpoint) + KOT-FAIR/2 eval-prereg are DEFERRED to the maintainer's #57
> re-weighting + the framework revision. NEXT: review gate -> Fable critique -> prereg. Not frozen.
> Source: poc/gpt56-review/p3d-vl-design/.

---

# H‑VL — small host + kernel verify/retry

> **Status:** PROPOSAL for the review gate and Fable critique. Not frozen, preregistered, scheduled, or evidence. This design does not resolve #57 or revise KOT‑FAIR/2.
>
> **Tags:** `[SV]` denotes a literature-dependent choice supported by the supplied reviews. Every new normative choice is marked `[STIPULATED — coordinator/Fable to ratify]`.

The parent fixes H‑VL’s outer form: small LM proposes, deterministic engine checks covered claims, failure triggers bounded retry or abstention, and the NL front end remains inside the measured product ([Programme‑3 §3.1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:614)). The crucial refinement is that the present kernel is not a general truth oracle or Lean-like proof checker. It is a deterministic typed query executor over an endorsed, snapshot-pinned store. “Verified” must therefore mean:

> The proposed typed value is exactly what the current kernel derives for the proposed formal query, under the endorsed definitions, axiom licences, world records, conflict rules, and store snapshot.

It does not mean that the formal query correctly expresses the user’s intent or that the endorsed store is externally true.

## 1. The loop

```text
natural request
    │
    ▼
NLB boundary admission: parse candidate q + calibrated confidence
    │
    ▼
small host proposes kot-vclaim/1 = {q, typed value, surface answer}
    │
    ▼
kernel verification wrapper
    ├── ACCEPT ───────► render/binding check ─► verified answer
    ├── REJECT ───────► typed feedback ───────► bounded host retry
    └── UNVERIFIABLE ─► reparse if justified; otherwise abstain/clarify
```

### Components and interfaces

| Component | Consumes | Emits | Responsibility |
|---|---|---|---|
| Boundary adapter | Natural request | `kot-query/1` candidate(s), parse confidence, ambiguity and coverage features | Treat NL as untrusted; enforce the NLB dependency |
| Retriever/address resolver | Formal query, frozen store snapshot | Relevant record IDs, licences, provenance, coverage status | Select authority-bearing records without changing their semantics |
| Small host | Request, formal candidate, previous typed error | Typed proposed value and user-facing surface | Proposal, repair and rendering—not final authority |
| Verification wrapper | Formal query, proposed typed value, frozen engine/store hashes | `ACCEPT`, `REJECT`, or `UNVERIFIABLE`, with typed code and witness | Compare the proposal with the deterministic engine result |
| Kernel engine | `kot-query/1`, endorsed definitions/axioms/world records | Canonical answer or named refusal, provenance and licence | Exact local execution and fail-closed refusal |
| Stop calibrator | Parse confidence, coverage, error history, attempt number, host uncertainty features | retry / abstain / clarify | Selective prediction; never self-consistency voting |
| Renderer/binding guard | Accepted typed value and surface answer | Final answer or `ERR_RENDER_MISMATCH` | Prevent the host from corrupting a checked result |

Natural-input operation remains blocked until the relevant NLB gate clears; otherwise the loop is explicitly an oracle-formal diagnostic with no real-input claim ([Programme‑3 §0](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:188)).

### `kot-vclaim/1`

`[STIPULATED — coordinator/Fable to ratify]`

```json
{
  "schema": "kot-vclaim/1",
  "request_id": "...",
  "attempt": 0,
  "query": { "...": "kot-query/1" },
  "candidate": {
    "value": "... typed JSON ...",
    "surface": "... user-facing answer ..."
  },
  "snapshot": {
    "engine_build": "sha256:...",
    "definitions": "sha256:...",
    "axioms": "sha256:...",
    "world": "sha256:..."
  },
  "parent_error": null
}
```

The orchestrator, not the host, supplies and checks the authoritative snapshot hashes. A host cannot select a more favourable store version.

### What the engine checks

The current engine validates the store at load time and answers five closed operations. Its formal semantics are already concrete:

- `unique`: an answer is licensed only by a functional or exact-one constraint; uniqueness is never inferred from one observed value.
- `lookup`: returns asserted values only; absence causes refusal because the store is not assumed complete.
- `count`: returns a count only under a matching exact-cardinality licence and only if the asserted count matches.
- `instance`: `true` requires an assertion; `false` requires a licensed disjointness derivation. Absence is not falsity.
- `define`: retrieves an endorsed one-level genus–differentia definition; `define` with a candidate uses exact structural set equality, not similarity or subsumption.

The engine also rejects queries touching functional, cardinality, disjointness, domain or range conflicts and attaches world-record provenance plus axiom licences to answers ([L3a engine semantics](/home/ec2-user/css/kernel/kernel-of-truth/docs/design-l3a-rules-engine-oracle.md:90), [current implementation](/home/ec2-user/css/kernel/kernel-of-truth/tools/axiom/kot_axiom.py:547)). Definition matching is exact over an endorsed definition object and fails closed on unresolved components ([define-op design](/home/ec2-user/css/kernel/kernel-of-truth/docs/design-kot-query-define-op.md:136)).

The wrapper adds one operation the current engine does not expose directly:

1. Run the engine on `query`.
2. If it returns an answer \(v^\*\), canonicalise the host’s typed value \(v\).
3. `ACCEPT` iff \(v=v^\*\), provenance is non-empty and valid, licences are non-empty and valid, and the surface answer round-trips to \(v\).
4. `REJECT` only when the formal substrate positively establishes a mismatch or malformed candidate.
5. `UNVERIFIABLE` when the engine lacks authority: unlicensed term, unknown entity, no record, unresolved definition, conflict or incomplete exact count.

This distinction matters: “not verified” is not synonymous with “false.”

### The µs engine’s role

The measured engine latency is 5.29–7.82 µs/query ([Programme‑3 cost premise](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:343)). Therefore:

- `[STIPULATED — coordinator/Fable to ratify]` H‑VL v0 performs one complete candidate-level engine call per attempt.
- `[SV]` It does not use per-token semantic masking. The NTP review found no precedent for that regime and assigns it to H‑RULE‑CD/H‑VL as a separate novel question ([NTP §6](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-ntp.md:387)).
- Engine cost must still be measured; the proposer’s generated tokens, parsing and retrieval are expected to dominate. µs checking removes a cost term but does not make retry free.
- The engine may generate training labels cheaply, but proof states, continuation sets and compiler-grade counterexamples require the NTP oracle/API gate before being assumed available ([NTP hand-off](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-ntp.md:492)).

## 2. Verify signal, feedback and stopping

### Verification result

`[STIPULATED — coordinator/Fable to ratify]`

```json
{
  "schema": "kot-vresult/1",
  "decision": "ACCEPT | REJECT | UNVERIFIABLE",
  "code": "KOT_OK | ERR_*",
  "retryable": true,
  "stage": "formalise | license | store | value | render",
  "witness": {
    "field_path": "...",
    "record_ids": [],
    "license_ids": [],
    "constraint": null
  },
  "canonical_value_digest": "sha256:...",
  "snapshot_digest": "sha256:...",
  "engine_latency_us": 0
}
```

Suggested grouping:

| Result | Representative inner codes | Default action |
|---|---|---|
| Retryable rejection | `ERR_BAD_QUERY`, `ERR_CANDIDATE_TYPE`, `ERR_VALUE_MISMATCH`, `ERR_RENDER_MISMATCH` | Feed error to host |
| Potentially reparsable | `ERR_TERM_UNLICENSED`, `ERR_UNKNOWN_ENTITY` | One reparse only if the boundary calibrator supports an alternative |
| Non-retryable unverifiable | `ERR_NO_RECORD`, `ERR_NO_DEFINITION`, `ERR_DEFN_UNRESOLVED`, `ERR_COUNT_MISMATCH` | Abstain |
| Integrity stop | `ERR_CONFLICT`, snapshot mismatch, engine/internal error | Immediate fail-closed abstention/escalation |

### Feedback channel

`[STIPULATED — coordinator/Fable to ratify] [SV]` The primary H‑VL feedback channel is prompt-serialized structured feedback:

```text
Verification failed.
code: ERR_VALUE_MISMATCH
stage: value
constraint: exact licensed result does not match the proposed typed value
witness: record w00127, licence rel-mother.json#0
Revise the formal query or typed value. Do not repeat the previous candidate.
```

This choice follows RLEF/Logic-LM/Goedel-style training to consume executor feedback across turns; RLEF is the direct retry-training precedent ([NTP §5](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-ntp.md:344)).

The feedback contract has three safeguards:

- The full canonical answer remains in a trusted orchestrator channel. The host receives a typed diagnostic and, where available, one minimal proof-local counterexample—not an unrestricted answer dump.
- A counterexample or proof trace is enabled only after the executor API gate demonstrates it deterministically. Otherwise the first implementation uses code, reason, record IDs and licence IDs only.
- Logit masks and residual-stream carrier injection are separate interface arms. They may not be silently substituted for prompt feedback.

A mandatory constant-feedback control replaces the diagnostic with `Rejected; answer again.` while preserving the same accept oracle, attempts and token budget. This separates feedback content from rejection sampling, following the non-vacuous verifier analysis ([RULES‑1‑D](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/rules-1-d-nonvacuous-verifier.md:140)).

### Retry budget

`[STIPULATED — coordinator/Fable to ratify]`

- Attempt 0 plus at most **two feedback-conditioned retries**: `K_retry = 2`, three total candidates.
- Stop early on a non-retryable code, a repeated identical canonical candidate, the same error code twice without a changed formal object, or stop-calibrator rejection.
- Run a diagnostic budget curve at `K_retry ∈ {0,1,2,4}`. The deployed point remains two retries unless separately ratified.
- Report attempt-0 and final outcomes separately. A gain confined to final outcomes is filtering/search until the typed-vs-constant-feedback contrast establishes feedback consumption.
- Never emit the last unverified candidate. Terminal states are verified answer, calibrated abstention, or clarification request.

### Selective stop policy

`[STIPULATED — coordinator/Fable to ratify] [SV]` A separately calibrated stop model estimates the probability that another attempt will produce both:

1. a boundary-admissible formalization; and
2. an engine-accepted typed answer.

Its features include error class, attempt number, parse confidence, coverage, previous candidate/error digests, host margin, and correction/regression history. Calibration, threshold selection and final evaluation use disjoint data.

Self-consistency is not a confidence signal: it cannot detect systematic confident-wrong answers such as a repeated ROLE_DIR inversion ([PARSE §4](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-parse.md:298)). An accepted answer must independently pass the boundary-admission threshold; engine acceptance alone is insufficient.

The threshold is intentionally not fixed here:

- Under an efficiency framing, it would trade extra retries and abstentions against index and resource cost.
- Under a correctness framing, it would be selected against a dangerous-wrong upper bound and then maximize coverage.

Choosing between those objectives belongs to #57.

## 3. Training

### Two product variants

1. **H‑VL‑F — frozen host.** The productised first rung: frozen small host, frozen parser configuration, frozen engine/store, prompt feedback and bounded retries. This isolates the inference-time architecture.

2. **H‑VL‑R — retry-trained host.** `[STIPULATED — coordinator/Fable to ratify] [SV]` Start from the same host and train it to interpret typed executor feedback. Host parameters or a declared adapter are trainable; the engine, store snapshot, verification wrapper, feedback templates and retry cap remain frozen during each training comparison.

H‑VL‑R must be compared with H‑VL‑F. Otherwise inference architecture and retry competence are bundled.

### Automatically generated training data

`[STIPULATED — coordinator/Fable to ratify] [SV]`

Generate formal tasks from the engine/store with known target query \(q^\*\), then generate controlled corruptions:

- wrong operation, subject, relation or direction;
- valid-but-wrong inverse/ROLE_DIR formalizations;
- malformed types and fields;
- unsupported/unlicensed queries;
- missing-record and conflict cases;
- wrong typed values;
- stale snapshot references;
- renderer corruption.

Each rollout records the first proposal, typed verifier response, repair attempts and terminal state. Splits are disjoint by rule template, composition, source, paraphrase family and depth. Valid-but-wrong formalizations are mandatory negatives so the model cannot learn “anything executable earns reward.”

No human label is needed on this generated covered substrate. Real natural inputs without generator-known \(q^\*\) do not become positive retry-training examples merely because the engine accepted their parse.

### Rungs

- **Data-filter/rejection-finetuning rung:** retain engine-accepted answer traces and successful reject→repair transitions; keep rejected traces as contrastive negatives. This is the best-evidenced shallow executor-training rung ([NTP §5](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-ntp.md:349)).
- **RLEF-style RL rung:** train over complete multi-turn retry trajectories using the deterministic result as reward.
- **Optional auto-PRM rung:** `[SV]` train a candidate-level process model from automatic engine labels, not per-token labels. Per-token semantic executor supervision has no established precedent here.

The matched learned-verifier comparator should use the literature-supplied recipe: a Cobbe-style outcome verifier plus a Math-Shepherd-style automatically labelled PRM, with no human-label budget and all training/build costs charged ([RAG §Q4](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-rag.md:229)).

### Reward

`[STIPULATED — coordinator/Fable to ratify]`

For generated training cases with known target \(q^\*\):

\[
R_{\text{task}} =
\begin{cases}
1,& \text{answerable and }q\equiv q^\*\text{ and verifier ACCEPTS}\\
1,& \text{generated unsupported/ambiguous case and system abstains}\\
0,& \text{otherwise}
\end{cases}
\]

Then:

\[
R = R_{\text{task}}
-\lambda_r N_{\text{retry}}
-\lambda_t N_{\text{generated tokens}}
-\lambda_c C_{\text{other measured resources}}.
\]

The verifier supplies all task labels. Cost coefficients and whether safety is a hard constraint or part of the scalar reward differ under the efficiency/correctness framing and remain for ratification after #57. Product serving always hard-blocks unverified emission regardless of the training reward.

## 4. Seams and failure modes

| Failure | What it would look like | Required isolation |
|---|---|---|
| **Confident-wrong false accept: ROLE_DIR** | Parser flips “what contains X” and “what X contains”; the wrong formal query is valid, executes and is accepted | G2 gold-query vs G3 NL-query decomposition; symmetric both-orientation challenge pairs; contrastive inverse checks; per-direction risk strata; boundary calibration. The engine cannot repair this class by itself ([PARSE §3](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-parse.md:259)). |
| **Validity, not correctness** | Candidate matches an endorsed store result, but the formalization or endorsed fact is wrong externally | External/sealed gold; valid-but-wrong program set; aligned typed-store `T*`; label permutation `P`; derangement `D`; provenance/source audits. Report formal soundness separately from end-to-end semantic correctness. |
| **Retry does not converge** | Same code repeats, repairs oscillate, coverage is exhausted, or later attempts regress | Attempt transition matrix; acceptance-by-attempt; repeated-error and regression rates; `Q0` one-shot, `Qsham` generic search, and typed-vs-constant feedback controls; calibrated early stop. |
| **Generic sampling mistaken for verification value** | Any selector or repeated sampling gets the same final lift | P3-D-THREAT’s `Q0`, `Qsham` and executor-bypass `E0` cells; compute-optimal sampling, self-consistency and learned verifier at matched realized budget ([P3-D-THREAT §3.8](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md:323)). |
| **Oracle filtering or answer leakage** | Verifier eliminates options until the answer is forced; feedback names the answer | Attempt-0 vs final; constant-feedback control; feedback information audit; direct engine→deterministic-render arm; prohibit retries that exhaust a finite option set. |
| **Verifier/store incompleteness misread as wrongness** | `ERR_NO_RECORD` or unlicensed terms are treated as candidate errors and repeatedly retried | Three-valued `ACCEPT/REJECT/UNVERIFIABLE` contract; G1 coverage ceiling first; covered/uncovered reporting; immediate abstention on non-correctable coverage errors. |
| **Symbolic-verifier immunity assumed** | Learned verifier decays at high budgets, and H‑VL is declared immune without measurement | Budget curve for symbolic and learned-verifier arms, reporting plateau, decay and dangerous-wrong rates. The literature explicitly says symbolic end-to-end immunity is unestablished ([RAG failure assessment](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-rag.md:340)). |
| **Renderer corrupts a checked result** | Formal value is correct but the final sentence reverses direction, polarity or entity | Typed-value/surface round-trip; deterministic renderer for closed answer types; optional host prose separated as unverified explanation; direct-render control. |
| **Reward hacking** | Model learns easy executable queries, over-abstains, or changes the intended claim to one the engine accepts | Reward requires \(q\equiv q^\*\) on generated training; valid-wrong negatives; held-out rules/compositions; abstention rewarded only on known unsupported cases. |
| **Kernel-specificity laundering** | Gain is really typed storage, retrieval, text delivery or generic tools | Mandatory `D`, `P`, `I`, `T*`, `R*`, kernel-as-text `X*`, `E0`, `Q0`, and `Qsham` cells. P3-D-THREAT treats the result as a contrast ledger, not an indivisible “kernel gain” ([six-way attribution](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md:357)). |

A mandatory direct engine→deterministic-render arm is especially important. On the currently covered query grammar, the engine often computes the answer rather than merely checking a proof. If direct rendering matches or beats verify/retry, the retry layer is unnecessary and the surviving product should be reclassified as an H‑PS/executor pipeline. H‑VL must be allowed to falsify itself at this seam.

The gate order remains G1 coverage ceiling → G2 oracle formalization → G3 NL degradation → G4 full system → G5 scale ([Programme‑3 §4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:854)). This proposal defines the architecture and control cells only; it does not define G4’s win endpoint.

## 5. Retrieve versus bake

The parent requires both store-on-disk/retrieval and baked/distilled settings to be measured for a surviving store-using design ([Programme‑3 §3.4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:743)).

For H‑VL the fork is asymmetric:

- The retry policy and common kernel knowledge may be baked into the host through data filtering/RLEF.
- Retrieved evidence and proof-local witnesses may be supplied only on demand.
- The authoritative endorsed store and deterministic checker cannot be completely baked away while retaining the H‑VL soundness contract. A host-only distilled system is a neural/H‑GU comparator, not an H‑VL verifier.
- `[STIPULATED — coordinator/Fable to ratify]` Report three points: frozen host + external checker; retry-trained host + external checker; trained host without checker. The last point measures how much behaviour distilled, but carries no formal soundness licence.

## 6. F1‑K connection

F1‑K supplies a concept-conditioned content carrier \(K_c\) and splices it into the MoE residual computation through ADD or REPLACE; it is a transport/integration mechanism ([F1‑K mechanism](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/glm52-followup-experiment.md:90)). Its primary carrier is a per-concept mean hidden-state offset derived from definition-present versus definition-absent contexts ([F1‑K carrier](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/glm52-followup-experiment.md:241)).

Therefore:

- **No: F1‑K’s carrier is not the H‑VL verifier at small scale.** It does not recompute a `kot-query/1` result or certify an output. F1‑K’s frozen experimental scorer is measurement infrastructure, not an inference-time soundness checker.
- **Yes: F1‑K’s splice is a reusable feedback-transport seam.** A combined arm could encode H‑VL’s typed error/witness as an F1‑K-style carrier and inject it internally rather than as prompt text.
- The external kernel engine remains the verifier in both prompt and carrier arms. If the carrier arm improves repair, that establishes an integration/transport result—not stronger soundness.
- `[STIPULATED — coordinator/Fable to ratify]` Any carrier-feedback experiment holds the engine, store, retry cap and semantic feedback payload fixed and varies only transport: prompt text vs residual carrier vs deranged/random/plain-text carrier controls.
- The closest existing small-host ancestor is f2b’s silent verify/resample loop, not F1‑K. H‑VL adds a real typed feedback channel, selective stopping, a non-vacuity control and formal execution rather than normalized answer-string matching.

# H‑VL architecture — compact final specification

- **Loop:** NLB-admitted formalization → small-host typed proposal → deterministic query execution and exact candidate comparison → typed feedback on correctable rejection → at most two retries → verified answer, abstention or clarification.
- **Verify signal:** three-valued `ACCEPT/REJECT/UNVERIFIABLE`; exact provenance/licence-bearing formal soundness relative to a pinned endorsed store; prompt-serialized typed feedback with a gated minimal witness; no self-consistency confidence.
- **Training:** frozen-host product rung, then data-filter and RLEF-style retry-trained rung; engine-generated formal targets and corruptions; automatic binary terminal reward plus measured retry/token cost; no human labels required for the covered retry-training substrate.
- **Seams/failures:** formalization versus execution, typed feedback versus constant rejection, execution versus post-hoc logging, one-shot versus generic search, host rendering versus direct deterministic rendering, external checker versus distilled host, and prompt versus F1‑K-style carrier transport.
- **F1‑K:** reuses the carrier/splice as a possible feedback transport; does not reuse F1‑K as the verifier. The runtime H‑VL verifier is the deterministic kernel engine.

# `[STIPULATED]` values for ratification

1. `kot-vclaim/1` and `kot-vresult/1` interfaces and snapshot binding.
2. Three-valued `ACCEPT/REJECT/UNVERIFIABLE` result contract.
3. Candidate-level engine checking, not per-token semantic masking, for H‑VL v0.
4. Prompt-serialized typed feedback; at most one proof-local witness after the API gate.
5. Attempt 0 plus `K_retry = 2` retries; diagnostic sweep `{0,1,2,4}`.
6. Immediate stop on conflict/integrity errors; no emission of an unverified final candidate.
7. Separately calibrated selective stop model with disjoint calibration/threshold/eval data.
8. H‑VL‑F frozen-host rung before H‑VL‑R retry-trained rung.
9. Engine/store/wrapper/feedback templates fixed while training the H‑VL‑R host.
10. Automatic reward defined by correct engine-accepted target or warranted abstention, minus measured retry/token/resource costs.
11. Mandatory typed-vs-constant-feedback, direct-render, executor-bypass, one-shot and generic-search controls.
12. Prompt-vs-F1‑K-carrier feedback as an optional transport-only factor.
13. Baked-only host is not licensed as H‑VL; it is a comparator without the soundness contract.

# Explicitly DEFERRED to #57 + the framework revision

- Whether the programme’s win condition remains efficiency W1, gains a separate correctness claim, uses correctness as a conjunctive gate, or adopts a correctness–coverage–cost Pareto axis.
- The correctness endpoint definitions, margins, rare-event sample sizes and challenge-set weights.
- The operating selective-prediction threshold and whether it is chosen for resource/index return or a dangerous-wrong upper bound.
- The cost coefficients in the RLEF reward and any framing-dependent retry-budget optimization.
- How abstention, harmless wrong and dangerous wrong enter the headline score.
- KOT‑FAIR/2/KOT‑AI index revisions, comparator-frontier pins, multiplicity plan, sealed-suite consistency rule and final factorial margins.
- The KOT‑FAIR/2 preregistration and KOT‑FAIR/2/P3‑D‑INDEX freeze.
- Any claim that H‑VL wins—on efficiency, correctness or kernel-specific attribution.