# P3-D-VL: H-VL verifier-loop — REVISED PROPOSAL (Revision 1): re-scoped as an H-PS ablation/variant family

> **STATUS: REVISED PROPOSAL — NOT A PREREG FREEZE.** 2026-07-19, Programme-3 Phase-1 (overflow-Fable).
> Revision 1 applies the load-bearing fixes from the independent GPT-5.6 soundness review
> ([p3-arch-family-review1.md §H-VL](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3-arch-family-review1.md): "NEEDS-FIX … formally safe but largely redundant
> with H-PS under the current answer-producing engine") to the prior unreviewed GPT-5.6 draft.
> **IDENTITY DECISION (Revision 1, §0): under the current terminal query grammar H-VL is
> RECLASSIFIED as an ablation/variant family of H-PS** — direct engine→deterministic-render is the
> primary arm; the propose-value+verify loop is an ablation that must earn its keep — with a
> precise, testable re-instatement condition for a future check-not-compute grammar.
> ARCHITECTURE + training + seams only; the win-condition (efficiency-W1 vs correctness-endpoint)
> + KOT-FAIR/2 eval-prereg are DEFERRED to the maintainer's #57 re-weighting + the framework revision.
> **Any prereg-freeze WAITS on the #57 framework-adjudication decision AND the framework blockers
> (P3-D-THREAT revision among them, per review 1); nothing here is frozen, registered, scheduled,
> or committed.** See "## Revision 1 — review fixes applied" for the itemised changes.
> Source: poc/gpt56-review/p3d-vl-design/ + review-1 fixes.

---

# H‑VL — small host + kernel verify/retry (re-scoped)

> **Status:** REVISED PROPOSAL (post-review-1) for the coordinator. Text/specification only; nothing is frozen, preregistered, scheduled, or evidence. This design does not resolve #57 or revise KOT‑FAIR/2.
>
> **Tags:** the prior draft's `[SV]` markers are mapped to the programme's four-tag scheme: `[LIT-BACKED]` = literature-dependent choice supported by the supplied reviews; `[MEASURED: ref]` = observed fact with source; `[STIPULATED]` = design choice awaiting ratification; `[EXTRAPOLATION]` = forward claim beyond measurement (deliberately unused in this revision — forward performance statements are absent pending #57).

The parent fixed H‑VL's outer form as: small LM proposes, deterministic engine checks covered claims, failure triggers bounded retry or abstention, with the NL front end inside the measured product ([Programme‑3 §3.1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:614)). Review 1 established that this form, over the *current* engine, does not have a distinct architectural identity — resolved explicitly in §0 below. The sound parts of the original contract are retained unchanged:

> "Verified" means: the proposed typed value is exactly what the current kernel derives for the proposed formal query, under the endorsed definitions, axiom licences, world records, conflict rules, and store snapshot.

It does not mean that the formal query correctly expresses the user's intent or that the endorsed store is externally true. Lack of authority is not falsity: the result contract stays three-valued (`ACCEPT/REJECT/UNVERIFIABLE`).

## 0. Identity decision `[STIPULATED — review-1 fix 1; PROPOSED-PREREG-ROW-VL-R1a]`

The review's central finding: the H‑VL wrapper *computes* \(v^\*\) rather than merely *checking* a proof the host alone could produce — it runs the query, obtains the canonical answer, and compares. Once \(q\) is trusted enough to execute, rendering \(v^\*\) directly is cheaper and safer, i.e. H‑PS. The prior draft admitted the direct-render arm might reclassify the survivor but left the identity unresolved. Revision 1 resolves it. The decision test, its application, and the outcome:

### 0.1 The check-not-compute test

An architecture earns a distinct *verifier* identity (as opposed to an *executor* identity) only if there exists a covered claim class where the engine can verify a host-supplied (value + justification) pair **strictly cheaper or strictly safer** than it can compute the value itself — a genuine verify/compute asymmetry, e.g. a search problem whose witness is cheap to check but expensive to find, or a claim class where the engine lacks the authority to *derive* a value but can *check* a supplied witness against licences. `[STIPULATED]`

### 0.2 Application to the current engine

Every covered operation is terminal and deterministic: `unique`, `lookup`, `count`, `instance`, and exact `define` matching ([L3a engine semantics](/home/ec2-user/css/kernel/kernel-of-truth/docs/design-l3a-rules-engine-oracle.md:90), [current implementation](/home/ec2-user/css/kernel/kernel-of-truth/tools/axiom/kot_axiom.py:547)). On this grammar:

- **Checking is never cheaper.** The wrapper's first step *is* the computation: it must derive \(v^\*\) before it can compare (§1.3). Engine execution costs 5.29–7.82 µs/query `[MEASURED:` [Programme‑3 cost premise](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:343)`]` — there is no search step a host-supplied witness could skip. Even `define`-with-candidate retrieves the endorsed definition object before its exact structural comparison ([define-op design](/home/ec2-user/css/kernel/kernel-of-truth/docs/design-kot-query-define-op.md:136)): compute-then-compare, not check-without-compute.
- **Checking is never safer.** `ACCEPT` requires \(v=v^\*\), so the emitted typed content is fully determined by \(v^\*\) regardless of what the host proposed; the host's value proposal adds a corruption/leak surface (value grinding against the compare oracle, renderer mismatch, retry gaming — §2.3) while removing no computation and licensing no additional content. The only host contribution to the output is the surface string, which H‑PS's checked renderer already governs under a round-trip invariant.
- **The failure the loop cannot see is the one that matters.** Value-mismatch retries repair something the engine can overwrite deterministically; semantic-query mistakes — the measured dangerous class (§2.2, §4) — execute and are accepted, because the wrong \(q\) is valid. The verify loop adds repair exactly where repair is worthless and adds nothing where it is needed.

### 0.3 Decision: reclassify (option b) — with a testable re-instatement condition

**H‑VL is re-scoped, under the current grammar, as an ablation/variant family of H‑PS.** Concretely:

1. **The primary arm is H‑PS:** NLB-admitted formalization → engine execution → calibrated risk gate → deterministic checked-result renderer, per [p3d-ps-architecture.md](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md) (Revision 1). Direct engine→deterministic-render is the *default*, not a control.
2. **The propose-value+verify loop survives only as ablation arm `A‑VL` inside the H‑PS control family:** identical NLB admission, engine, store snapshot, and renderer; the sole delta is that the host proposes a typed value which the wrapper compares against \(v^\*\) before rendering, with the bounded typed-feedback retry loop of §2. `A‑VL` must demonstrate a measured advantage over direct render on some reported endpoint coordinate (e.g. renderer-corruption detection, calibration features from the compare signal) to justify its extra surface; the pre-registered expectation is that it does not. H‑VL is thereby allowed to falsify itself at this seam — now with the burden of proof inverted.
3. **The transferable machinery merges into H‑PS** rather than dying with the identity: the three-valued `ACCEPT/REJECT/UNVERIFIABLE` result contract with lack-of-authority-≠-falsity (offered to the family-shared terminal engine result schema that review 1's cross-design section requests), the `kot-vresult/1` typed error taxonomy, the selective stop calibrator, the retry-budget curve protocol, and the leak-gated diagnostic channel (§2.3) — the last aligning with and strengthening H‑PS's `Qdiag` factor.
4. **Re-instatement condition `[STIPULATED]`:** H‑VL is re-opened as a distinct architecture if and only if a concrete engine capability gate demonstrates a covered claim class passing the §0.1 test — e.g. a future multi-step derivation/proof grammar (post the H‑GU step-transition API gate, which does not currently exist per review 1 §H-GU) where the host supplies a derivation the engine checks without search, or a claim class where the engine can check a witness against licences but lacks authority to derive the value unaided. The demonstration must be an executable API-gate artefact, not prose. Until then, no programme narrative may present H‑VL as a live distinct architecture.

This is stated as a decision, not hedged: for the present grammar the answer to "what gives H‑VL a distinct, non-H‑PS identity?" is **nothing** — and the useful response is to keep its machinery and drop its claim to a separate architectural slot.

## 1. The loop (retained as the `A‑VL` ablation specification)

The remainder of this document specifies the `A‑VL` arm and its controls. Everything below inherits §0: this is an ablation spec inside the H‑PS family, not a freestanding architecture.

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

**Primary comparator (mandatory, run in every campaign that runs `A‑VL`):** the direct engine→deterministic-render arm — identical admission, engine, snapshot, and renderer, no host value proposal, no retry loop. Per §0 this is the H‑PS default, and `A‑VL` is measured *against* it. `[STIPULATED — review-1 fix 1]`

### Components and interfaces

| Component | Consumes | Emits | Responsibility |
|---|---|---|---|
| Boundary adapter | Natural request | `kot-query/1` candidate(s), parse confidence, ambiguity and coverage features | Treat NL as untrusted; enforce the NLB dependency |
| Retriever/address resolver | Formal query, frozen store snapshot | Relevant record IDs, licences, provenance, coverage status — **to the orchestrator/ledger only, never to the host channel (§2.3)** | Select authority-bearing records without changing their semantics |
| Small host | Request, formal candidate, previous typed error | Typed proposed value and user-facing surface | Proposal, repair and rendering—not final authority |
| Verification wrapper | Formal query, proposed typed value, frozen engine/store hashes | `ACCEPT`, `REJECT`, or `UNVERIFIABLE`, with typed code and leak-gated witness | Compare the proposal with the deterministic engine result |
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
2. If it returns an answer \(v^\*\), canonicalise the host's typed value \(v\).
3. `ACCEPT` iff \(v=v^\*\), provenance is non-empty and valid, licences are non-empty and valid, and the surface answer round-trips to \(v\).
4. `REJECT` only when the formal substrate positively establishes a mismatch or malformed candidate.
5. `UNVERIFIABLE` when the engine lacks authority: unlicensed term, unknown entity, no record, unresolved definition, conflict or incomplete exact count.

Step 1 is why §0 resolves as it does: the check *contains* the computation. This distinction between REJECT and UNVERIFIABLE still matters and is retained: "not verified" is not synonymous with "false."

### The µs engine's role

The measured engine latency is 5.29–7.82 µs/query `[MEASURED:` [Programme‑3 cost premise](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:343)`]`. Therefore:

- `[STIPULATED — coordinator/Fable to ratify]` `A‑VL` performs one complete candidate-level engine call per attempt.
- `[LIT-BACKED]` It does not use per-token semantic masking. The NTP review found no precedent for that regime and assigns it to H‑RULE‑CD/H‑VL as a separate novel question ([NTP §6](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-ntp.md:387)).
- Engine cost must still be measured; the proposer's generated tokens, parsing and retrieval are expected to dominate. µs checking removes a cost term but does not make retry free — and per §0.2 it also removes the "checking is cheaper" identity defence.
- The engine may generate training labels cheaply, but proof states, continuation sets and compiler-grade counterexamples require the NTP oracle/API gate before being assumed available ([NTP hand-off](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-ntp.md:492)).

## 2. Verify signal, feedback and stopping

### 2.1 Verification result

`[STIPULATED — coordinator/Fable to ratify]`

```json
{
  "schema": "kot-vresult/1",
  "decision": "ACCEPT | REJECT | UNVERIFIABLE",
  "code": "KOT_OK | ERR_*",
  "retryable": true,
  "stage": "formalise | license | store | value | render",
  "host_visible": {
    "field_path": "...",
    "constraint_class": "..."
  },
  "ledger_only": {
    "record_ids": [],
    "license_ids": [],
    "canonical_value_digest": "sha256:...",
    "constraint": null
  },
  "snapshot_digest": "sha256:...",
  "engine_latency_us": 0
}
```

**Revision-1 change `[STIPULATED — review-1 fix 2]`:** the witness is split. `host_visible` carries only the offending field path and a constraint *class* drawn from a closed non-answer-bearing vocabulary. Record IDs, licence IDs, the canonical-value digest, and constraint payloads are `ledger_only` — trusted orchestrator channel, audit ledger, never the host. (A host-visible value digest would itself be a grind oracle: a host can enumerate candidate values and test digests offline. The prior draft's flat `witness{record_ids, license_ids}` is withdrawn.)

Suggested grouping:

| Result | Representative inner codes | Default action |
|---|---|---|
| Retryable rejection | `ERR_BAD_QUERY`, `ERR_CANDIDATE_TYPE`, `ERR_VALUE_MISMATCH`, `ERR_RENDER_MISMATCH` | Feed leak-gated error to host |
| Potentially reparsable | `ERR_TERM_UNLICENSED`, `ERR_UNKNOWN_ENTITY` | One reparse only if the boundary calibrator supports an alternative |
| Non-retryable unverifiable | `ERR_NO_RECORD`, `ERR_NO_DEFINITION`, `ERR_DEFN_UNRESOLVED`, `ERR_COUNT_MISMATCH` | Abstain |
| Integrity stop | `ERR_CONFLICT`, snapshot mismatch, engine/internal error | Immediate fail-closed abstention/escalation |

### 2.2 Feedback channel

`[STIPULATED — coordinator/Fable to ratify] [LIT-BACKED]` The primary `A‑VL` feedback channel is prompt-serialized structured feedback. Revised worked example (non-answer-bearing — compare the prior draft's example, which named an answer-supporting record and licence and is withdrawn `[STIPULATED — review-1 fix 2]`):

```text
Verification failed.
code: ERR_VALUE_MISMATCH
stage: value
field_path: candidate.value
constraint_class: exact-licensed-result-mismatch
Revise the formal query or typed value. Do not repeat the previous candidate.
```

This choice follows RLEF/Logic-LM/Goedel-style training to consume executor feedback across turns; RLEF is the direct retry-training precedent ([NTP §5](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-ntp.md:344)).

The feedback contract safeguards:

- The full canonical answer, record/licence IDs, value digests, and any store content remain in the trusted orchestrator/ledger channel only. The host receives a typed diagnostic from the closed `host_visible` vocabulary — never record IDs, never licence IDs, never a value digest.
- A proof-local counterexample or trace is enabled only after the executor API gate demonstrates it deterministically, AND only if it passes the §2.3 leak budget. Otherwise the implementation uses code, stage, field path and constraint class only.
- Logit masks and residual-stream carrier injection are separate interface arms. They may not be silently substituted for prompt feedback.

**Diagnostic-content factor `[STIPULATED — review-1 fix 2]`:** three arms under one IDENTICAL accept oracle (same engine, same acceptance decisions), matching the sibling H‑PS `Qdiag` convention:

- `Qdiag-typed` — real typed diagnostics (the deployment configuration above);
- `Qdiag-const` — every rejection returns one constant uninformative token (`Rejected; answer again.`), same oracle, attempts and token budget;
- `Qdiag-sham` — information-matched sham diagnostics: messages drawn from the true diagnostic vocabulary with matched marginal frequency, length, and entropy, permuted across items so they are decoupled from the actual failure.

A "feedback helped" claim requires BOTH `Qdiag-typed` > `Qdiag-const` AND `Qdiag-typed` > `Qdiag-sham`. A typed-vs-constant contrast alone (the prior draft's only control) proves content mattered but does not distinguish genuine diagnostic use from answer leakage — the review's point — and neither contrast alone survives the leak audit below; all three are required together with §2.3.

### 2.3 Executable entropy/leak gate `[STIPULATED — review-1 fix 2; PROPOSED-PREREG-ROW-VL-R1b]`

The programme's own record shows why prose prohibitions are insufficient: in rules-1c, a finite-option retry against a working accept/reject oracle reduces to rejection sampling that converges to the verifier's own knowledge without host understanding, and at a closed 2-option surface *non-vacuous and non-leaking are jointly unsatisfiable* — any informative rejection conveys the whole answer bit by elimination, while the leak guard in place was lexical and blind to the combinatorial channel ([rules1c instrument-invalid interpretation](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/rules1c-instrument-invalid-interpretation.md:125)). `A‑VL` therefore carries an *executable* gate, not a prose rule:

1. **Closed diagnostic vocabulary.** The `host_visible` payload is generated only from the enumerated {code × stage × field-path-type × constraint-class} vocabulary, pinned at campaign registration. Any string outside the vocabulary in the host channel is fail-closed/`INSTRUMENT-INVALID`.
2. **Per-item elimination audit.** For every item the harness computes, per attempt, the feasible-answer-set reduction implied by the rejection: leaked bits ≤ \(\log_2(|S_t|/|S_{t+1}|)\), where \(S_t\) is the feasible candidate set consistent with the item's type/coverage and all feedback received through attempt \(t\). Cumulative leaked bits per item must stay under a registered budget \(B_{\text{leak}}\); violation invalidates the item's stratum, fail-closed.
3. **Retry-eligibility entropy floor.** An item is retry-eligible only if its feasible answer space exceeds a registered floor \(H_{\min}\) such that worst-case elimination over all `K_retry` attempts leaves ≥1 bit of residual uncertainty. Closed small-option surfaces (the rules1c n=2 degeneracy) are retry-INELIGIBLE by construction: attempt-0 answer or abstain, no feedback loop.
4. **Exhaustion prohibition, executable.** If the feasible option set is finite and \(|S_0| \le K_{\text{retry}}+1\), the loop is not entered (subsumed by 3, stated separately because it is the exact rules1c failure shape). Any observed run in which the attempt sequence enumerates the feasible set is flagged in the ledger and invalidates the item.

The numeric values of \(B_{\text{leak}}\) and \(H_{\min}\) are prereg-freeze parameters, not fixed here.

### 2.4 Blocking real-item non-vacuity pilot `[STIPULATED — review-1 fix 2; PROPOSED-PREREG-ROW-VL-R1c]`

Before any registered retry campaign (training or evaluation) may launch, a pilot on **real items** (not generator-synthetic ones) must go green on all of:

1. **Nonzero rejection:** the verifier rejects at least one real hand-simulated-wrong and at least one organically proposed candidate — a verifier that never rejects is vacuous (the rules1c pre-freeze lesson: the engagement signature was visible in pilot rows before launch, and the launch proceeded because no such check was mandatory `[MEASURED:` [rules1c §1.1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/rules1c-instrument-invalid-interpretation.md:100)`]`).
2. **Non-exhaustion:** zero pilot items exhibit the exhaustion signature of §2.3(4).
3. **Actual formal-query repair:** among reject→accept transitions, a registered minimum fraction must change the *formal object* (the query \(q\) or the typed structure), not merely resample the value; on generator-known probes seeded into the pilot, the change must move toward \(q^\*\), not just away from the rejected candidate.
4. **Feedback engagement:** the `Qdiag-typed` and `Qdiag-const` arms must differ at the behavioural level (attempt distributions, not endpoint scores) — identical attempt traces across arms mean the feedback channel is dead, exactly the rules1c A3≡c1 signature.

This pilot is BLOCKING: no green pilot, no campaign. Its thresholds are prereg-freeze parameters.

### 2.5 Retry budget

`[STIPULATED — coordinator/Fable to ratify]`

- Attempt 0 plus at most **two feedback-conditioned retries**: `K_retry = 2`, three total candidates.
- Stop early on a non-retryable code, a repeated identical canonical candidate, the same error code twice without a changed formal object, stop-calibrator rejection, or any §2.3 gate trip.
- Run a diagnostic budget curve at `K_retry ∈ {0,1,2,4}`. The deployed point remains two retries unless separately ratified.
- Report attempt-0 and final outcomes separately. A gain confined to final outcomes is filtering/search until the full `Qdiag-typed/const/sham` factor (§2.2) plus the leak audit (§2.3) establish feedback consumption; the typed-vs-constant contrast alone is insufficient `[STIPULATED — review-1 fix 2]`.
- Never emit the last unverified candidate. Terminal states are verified answer, calibrated abstention, or clarification request.

### 2.6 Selective stop policy

`[STIPULATED — coordinator/Fable to ratify] [LIT-BACKED]` A separately calibrated stop model estimates the probability that another attempt will produce both:

1. a boundary-admissible formalization; and
2. an engine-accepted typed answer.

Its features include error class, attempt number, parse confidence, coverage, previous candidate/error digests, host margin, and correction/regression history. Calibration, threshold selection and final evaluation use disjoint data.

Self-consistency is not a confidence signal: it cannot detect systematic confident-wrong answers ([PARSE §4](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-parse.md:298)) — such as a repeated **same-orientation operator substitution**, the measured a5 dangerous class: 0/43 dangerous-wrongs were orientation/direction flips; all were same-orientation operator substitutions within the containment/definition frame-group (gold `contained-in` parsed as `where-defined` and conversely), a subset surface-underdetermined `[MEASURED: docs/next/analysis/nlb-0a.md §1]`. (The prior draft's "repeated ROLE_DIR inversion" example was STALE and is withdrawn `[review-1 cross-draft correction]`.)

The threshold is intentionally not fixed here:

- Under an efficiency framing, it would trade extra retries and abstentions against index and resource cost.
- Under a correctness framing, it would be selected against a dangerous-wrong upper bound and then maximize coverage.

Choosing between those objectives belongs to #57.

## 3. Training

### 3.1 Two variants

1. **`A‑VL‑F` — frozen host.** Frozen small host, frozen parser configuration, frozen engine/store, leak-gated prompt feedback and bounded retries. This isolates the inference-time ablation.

2. **`A‑VL‑R` — retry-trained host.** `[STIPULATED — coordinator/Fable to ratify] [LIT-BACKED]` Start from the same host and train it to interpret typed executor feedback. Host parameters or a declared adapter are trainable; the engine, store snapshot, verification wrapper, feedback templates and retry cap remain frozen during each training comparison.

`A‑VL‑R` must be compared with `A‑VL‑F`, and both against the direct-render primary arm (§0.3). Otherwise inference architecture and retry competence are bundled.

### 3.2 Automatically generated training data

`[STIPULATED — coordinator/Fable to ratify] [LIT-BACKED]`

Generate formal tasks from the engine/store with known target query \(q^\*\), then generate controlled corruptions:

- wrong operation, subject or relation;
- **same-orientation operator substitutions as the PRIMARY valid-but-wrong family** (the measured a5 dangerous class: container-asks over the same entity, `contained-in` vs `where-defined`; 0/43 orientation flips `[MEASURED: docs/next/analysis/nlb-0a.md §1]`) `[STIPULATED — review-1 fix 4]`;
- direction-inverted / inverse-relation formalizations **only as clearly-labelled synthetic negatives** — they are a synthetic instance of the valid-but-wrong hazard, not the measured class `[STIPULATED — review-1 fix 4]`;
- surface-underdetermined items (wording contains no information discriminating the candidate operators, per the measured cross-authored a5 surfaces `[MEASURED: nlb-0a.md §1]`) whose gold target is fail-closed clarification/abstention, never either operator;
- malformed types and fields;
- unsupported/unlicensed queries;
- missing-record and conflict cases;
- wrong typed values;
- stale snapshot references;
- renderer corruption.

Each rollout records the first proposal, typed verifier response, repair attempts and terminal state. Splits are disjoint by rule template, composition, source, paraphrase family and depth. Valid-but-wrong formalizations are mandatory negatives so the model cannot learn "anything executable earns reward."

No human label is needed on this generated covered substrate. Real natural inputs without generator-known \(q^\*\) do not become positive retry-training examples merely because the engine accepted their parse.

### 3.3 Label provenance `[STIPULATED — review-1 fix 3; PROPOSED-PREREG-ROW-VL-R1d]`

The prior draft's sentence "the verifier supplies all task labels" was INACCURATE and is withdrawn. Correct statement:

- **The generator supplies** \(q^\*\), the answerability label, and the ambiguity label.
- **The verifier/engine supplies** only acceptance decisions (`ACCEPT/REJECT/UNVERIFIABLE`) and typed error codes — it cannot label whether an accepted query expresses the intended meaning.

### 3.4 Rungs

- **Data-filter/rejection-finetuning rung:** retain engine-accepted answer traces **only where the accepted query is semantically equivalent to the generator target (\(q \equiv q^\*\))**, and reject→repair transitions **only where they terminate in a target-matching accept**. Engine-accepted but target-mismatching traces are valid-but-wrong contrastive negatives, never positives — retaining "everything the engine accepts" would train exactly the valid-but-wrong hazard `[STIPULATED — review-1 fix 3]`. This is the best-evidenced shallow executor-training rung ([NTP §5](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-ntp.md:349)).
- **RLEF-style RL rung:** train over complete multi-turn retry trajectories using the deterministic result as reward.
- **Optional auto-PRM rung:** `[LIT-BACKED]` train a candidate-level process model from automatic engine labels, not per-token labels. Per-token semantic executor supervision has no established precedent here.

The matched learned-verifier comparator should use the literature-supplied recipe: a Cobbe-style outcome verifier plus a Math-Shepherd-style automatically labelled PRM, with no human-label budget and all training/build costs charged ([RAG §Q4](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-rag.md:229)).

### 3.5 Reward

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

Label provenance is per §3.3: the generator supplies \(q^\*\) and the answerability/ambiguity labels that make \(R_{\text{task}}\) computable; the verifier contributes only the ACCEPT decision. Cost coefficients and whether safety is a hard constraint or part of the scalar reward differ under the efficiency/correctness framing and remain for ratification after #57. Product serving always hard-blocks unverified emission regardless of the training reward.

## 4. Seams and failure modes

| Failure | What it would look like | Required isolation |
|---|---|---|
| **Confident-wrong false accept: same-orientation operator substitution** (measured a5 class `[MEASURED: nlb-0a.md §1]`) | Parser substitutes `where-defined` for `contained-in` (or conversely) over the same entity, same orientation; the wrong formal query is valid, executes and is accepted; a subset of surfaces is underdetermined | G2 gold-query vs G3 NL-query decomposition; operator-substitution challenge pairs as the primary family; clearly-labelled synthetic direction-inversion pairs as a secondary family; fail-closed handling of surface-underdetermined items; per-operator risk strata; boundary calibration. The engine cannot repair this class by itself ([PARSE §3](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-parse.md:259)); per §0.2 the verify loop cannot see it either. |
| **Validity, not correctness** | Candidate matches an endorsed store result, but the formalization or endorsed fact is wrong externally | External/sealed gold; valid-but-wrong program set; aligned typed-store `T*`; label permutation `P`; derangement `D`; provenance/source audits. Report formal soundness separately from end-to-end semantic correctness. |
| **Retry does not converge** | Same code repeats, repairs oscillate, coverage is exhausted, or later attempts regress | Attempt transition matrix; acceptance-by-attempt; repeated-error and regression rates; `Q0` one-shot, `Qsham` generic search, and full `Qdiag-typed/const/sham` controls; calibrated early stop. |
| **Generic sampling mistaken for verification value** | Any selector or repeated sampling gets the same final lift | P3-D-THREAT's `Q0`, `Qsham` and executor-bypass `E0` cells; compute-optimal sampling, self-consistency and learned verifier at matched realized budget ([P3-D-THREAT §3.8](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md:323)). |
| **Oracle filtering or answer leakage** | Verifier eliminates options until the answer is forced; feedback names or implies the answer | The §2.3 executable entropy/leak gate (closed vocabulary, elimination audit, entropy floor, exhaustion prohibition); §2.4 blocking pilot; `Qdiag-sham`; attempt-0 vs final; the direct engine→deterministic-render primary arm; ledger-only witness split (§2.1). Programme precedent: rules1c's leak–vacuity dilemma and exhaustion degeneracy ([rules1c](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/rules1c-instrument-invalid-interpretation.md:125)). |
| **Verifier/store incompleteness misread as wrongness** | `ERR_NO_RECORD` or unlicensed terms are treated as candidate errors and repeatedly retried | Three-valued `ACCEPT/REJECT/UNVERIFIABLE` contract; G1 coverage ceiling first; covered/uncovered reporting; immediate abstention on non-correctable coverage errors. |
| **Symbolic-verifier immunity assumed** | Learned verifier decays at high budgets, and the verify loop is declared immune without measurement | Budget curve for symbolic and learned-verifier arms, reporting plateau, decay and dangerous-wrong rates. The literature explicitly says symbolic end-to-end immunity is unestablished ([RAG failure assessment](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-rag.md:340)). |
| **Renderer corrupts a checked result** | Formal value is correct but the final sentence reverses direction, polarity or entity | Typed-value/surface round-trip; deterministic renderer for closed answer types; optional host prose separated as unverified explanation; direct-render primary arm. (If `A‑VL` earns any keep, this is its most plausible seam — the compare signal as a renderer-corruption detector — and must be measured as a named coordinate, not assumed.) |
| **Reward hacking** | Model learns easy executable queries, over-abstains, or changes the intended claim to one the engine accepts | Reward requires \(q\equiv q^\*\) on generated training; target-matching trace filter (§3.4); valid-wrong negatives; held-out rules/compositions; abstention rewarded only on known unsupported cases. |
| **Kernel-specificity laundering** | Gain is really typed storage, retrieval, text delivery or generic tools | Mandatory `D`, `P`, `I`, `T*`, `R*`, kernel-as-text `X*`, `E0`, `Q0`, and `Qsham` cells. P3-D-THREAT treats the result as a contrast ledger, not an indivisible "kernel gain" ([six-way attribution](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md:357)). |

Per §0, the direct engine→deterministic-render arm is no longer merely "especially important": it is the PRIMARY arm, and `A‑VL` is the ablation measured against it. The prior draft's framing ("H‑VL must be allowed to falsify itself at this seam") is superseded by the stronger Revision-1 position: the falsification presumption now runs the other way.

The gate order remains G1 coverage ceiling → G2 oracle formalization → G3 NL degradation → G4 full system → G5 scale ([Programme‑3 §4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:854)). This proposal defines the ablation and control cells only; it does not define G4's win endpoint.

## 5. Retrieve versus bake

The parent requires both store-on-disk/retrieval and baked/distilled settings to be measured for a surviving store-using design ([Programme‑3 §3.4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:743)). For the `A‑VL` ablation the fork is asymmetric:

- The retry policy and common kernel knowledge may be baked into the host through data filtering/RLEF.
- Retrieved evidence may be supplied only on demand — and only into the ledger channel, never past the §2.3 gate.
- The authoritative endorsed store and deterministic engine cannot be baked away while retaining the soundness contract. A host-only distilled system is a neural/H‑GU comparator, not a verified arm.
- `[STIPULATED — coordinator/Fable to ratify]` Report three points: frozen host + external engine; retry-trained host + external engine; trained host without engine. The last point measures how much behaviour distilled, but carries no formal soundness licence.

## 6. F1‑K connection

F1‑K supplies a concept-conditioned content carrier \(K_c\) and splices it into the MoE residual computation through ADD or REPLACE; it is a transport/integration mechanism ([F1‑K mechanism](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/glm52-followup-experiment.md:90)). Its primary carrier is a per-concept mean hidden-state offset derived from definition-present versus definition-absent contexts ([F1‑K carrier](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/glm52-followup-experiment.md:241)).

Review 1 confirmed the prior draft's position here and mandated its programme-wide adoption `[review-1 fix 5]`:

- **F1‑K is NOT "the H‑VL checker at small scale," and no programme narrative may say so.** F1‑K is an activation carrier/splice *experiment* — it does not recompute a `kot-query/1` result, certify an output, or act as an inference-time proof/query verifier. Its frozen experimental scorer is measurement infrastructure, not a soundness checker. Any surviving "H‑VL = F1‑K as a small checker" framing anywhere in the programme record is to be treated as stale and removed on contact.
- **Only the carrier-transport seam is reusable.** Under the §0 reclassification it transfers to the H‑PS family: an optional transport-only factor on the diagnostic channel — encode the typed error payload as an F1‑K-style carrier and inject it internally rather than as prompt text.
- The external kernel engine remains the authority in both prompt and carrier arms. If the carrier arm improves repair, that is an integration/transport result — not stronger soundness.
- `[STIPULATED — coordinator/Fable to ratify]` Any carrier-feedback experiment holds the engine, store, retry cap and semantic feedback payload fixed and varies only transport: prompt text vs residual carrier vs deranged/random/plain-text carrier controls. The carrier payload passes the SAME §2.3 leak budget as the prompt payload — internal transport is not a leak exemption.
- The closest existing small-host ancestor of the retry loop is f2b's silent verify/resample loop, not F1‑K. `A‑VL` adds a real typed feedback channel, selective stopping, non-vacuity controls and formal execution rather than normalized answer-string matching.

# Compact final specification (Revision 1)

- **Identity:** under the current terminal grammar, H‑VL is an ablation/variant family of H‑PS (§0). Primary arm: direct engine→deterministic-render (H‑PS). Ablation arm `A‑VL`: host value proposal + compare + leak-gated bounded retry. Re-instatement as a distinct architecture only on an executable demonstration of a check-cheaper-or-safer-than-compute claim class.
- **Verify signal:** three-valued `ACCEPT/REJECT/UNVERIFIABLE`; exact provenance/licence-bearing formal soundness relative to a pinned endorsed store; "verified" = agreement with the pinned engine/store, never NL-intent or external truth; lack of authority is not falsity. Offered to the family-shared terminal engine result schema.
- **Feedback:** closed non-answer-bearing diagnostic vocabulary; witness split host-visible vs ledger-only; executable entropy/leak gate (elimination audit, entropy floor, exhaustion prohibition); blocking real-item non-vacuity pilot; `Qdiag-typed/const/sham` under one accept oracle.
- **Training:** generator supplies \(q^\*\)/answerability/ambiguity labels, verifier supplies acceptance only; target-matching trace filter; same-orientation operator substitutions as primary valid-but-wrong family, direction inversions synthetic-only; automatic terminal reward minus measured retry/token cost.
- **Seams/failures:** formalization versus execution, typed versus constant versus information-matched sham feedback, execution versus post-hoc logging, one-shot versus generic search, host rendering versus direct deterministic rendering (primary), external engine versus distilled host, and prompt versus F1‑K-style carrier transport (leak-gated).
- **F1‑K:** reuses the carrier/splice as a possible leak-gated feedback transport within the H‑PS family; is never the verifier; "F1‑K = small checker" narratives are removed.

# `[STIPULATED]` values for ratification

1. §0 identity decision: reclassification of H‑VL as an H‑PS ablation/variant family under the current grammar; direct render primary; `A‑VL` ablation; executable re-instatement condition. (PROPOSED-PREREG-ROW-VL-R1a)
2. `kot-vclaim/1` and revised `kot-vresult/1` (host-visible/ledger-only witness split) interfaces and snapshot binding.
3. Three-valued `ACCEPT/REJECT/UNVERIFIABLE` result contract, offered to the family-shared terminal result schema.
4. Candidate-level engine checking, not per-token semantic masking, for `A‑VL` v0.
5. Prompt-serialized typed feedback restricted to the closed non-answer-bearing vocabulary; record/licence IDs and value digests ledger-only; at most one proof-local witness after the API gate AND under the leak budget. (PROPOSED-PREREG-ROW-VL-R1b)
6. Executable entropy/leak gate: elimination audit with budget \(B_{\text{leak}}\), retry-eligibility floor \(H_{\min}\), exhaustion prohibition; violations fail-closed/`INSTRUMENT-INVALID`. (PROPOSED-PREREG-ROW-VL-R1b)
7. Blocking real-item non-vacuity pilot (nonzero rejection, non-exhaustion, formal-query repair, behavioural feedback engagement) before any registered retry campaign. (PROPOSED-PREREG-ROW-VL-R1c)
8. Attempt 0 plus `K_retry = 2` retries; diagnostic sweep `{0,1,2,4}`; early stop on §2.3 gate trips.
9. Immediate stop on conflict/integrity errors; no emission of an unverified final candidate.
10. Separately calibrated selective stop model with disjoint calibration/threshold/eval data.
11. `A‑VL‑F` frozen-host rung before `A‑VL‑R` retry-trained rung; both compared against the direct-render primary arm.
12. Engine/store/wrapper/feedback templates fixed while training the `A‑VL‑R` host; label provenance per §3.3 (generator supplies task labels; verifier supplies acceptance only); target-matching accepted-trace filter. (PROPOSED-PREREG-ROW-VL-R1d)
13. Automatic reward defined by target-matching engine-accepted answer or warranted abstention, minus measured retry/token/resource costs.
14. Mandatory `Qdiag-typed/const/sham` (one accept oracle), direct-render (primary), executor-bypass, one-shot and generic-search controls.
15. a5 corruption-family law: same-orientation operator substitution primary; direction inversions clearly-labelled synthetic negatives only; surface-underdetermined items fail-closed. (PROPOSED-PREREG-ROW-VL-R1e)
16. Prompt-vs-F1‑K-carrier feedback as an optional transport-only factor, under the same leak budget.
17. Baked-only host is not a verified arm; it is a comparator without the soundness contract.

## PROPOSED-ASM block (doc note only; registry NOT edited)

All rows below are PROPOSED only — nothing registered; no `ASM-<number>` ids are minted here (those are assigned at prereg-freeze). Labels are `VL-`prefixed to stay disjoint from the sibling H‑PS revision's `PROPOSED-PREREG-ROW-R1a…e`.

- **PROPOSED-PREREG-ROW-VL-R1a:** identity law — under the current terminal five-op grammar, H‑VL has no distinct check-not-compute seam (the wrapper's check contains the computation of \(v^\*\)); H‑VL is re-scoped as an H‑PS ablation/variant family (direct engine→deterministic-render primary; `A‑VL` propose-value+verify ablation); re-instatement as a distinct architecture requires an executable API-gate demonstration of a covered claim class where verifying a host-supplied value+justification is strictly cheaper or safer than engine computation. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-VL-R1b:** feedback leak law — host-visible diagnostics restricted to a closed non-answer-bearing vocabulary (no record IDs, no licence IDs, no value digests; those are ledger-only); executable entropy/leak gate with per-item elimination audit (budget \(B_{\text{leak}}\)), retry-eligibility entropy floor \(H_{\min}\), and finite-option exhaustion prohibition; any violation is fail-closed/`INSTRUMENT-INVALID` (per the rules1c leak–vacuity/exhaustion precedent). `[STIPULATED]`
- **PROPOSED-PREREG-ROW-VL-R1c:** non-vacuity pilot law — a blocking real-item pilot (nonzero rejection, non-exhaustion, genuine formal-query repair toward \(q^\*\) on seeded probes, behavioural typed-vs-constant engagement difference) must go green before any registered retry campaign launches. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-VL-R1d:** label-provenance law — the generator supplies \(q^\*\), answerability, and ambiguity labels; the verifier supplies acceptance decisions and typed codes only; the accepted-trace filtering rung retains only target-matching (\(q \equiv q^\*\)) accepted traces and target-matching reject→repair transitions; engine-accepted target-mismatching traces are contrastive negatives only. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-VL-R1e:** a5 corruption-family law — same-orientation operator-substitution negatives are the primary valid-but-wrong family (per the measured 0/43-orientation-flip diagnosis `[MEASURED: nlb-0a.md §1]`); surface-underdetermined items are fail-closed (gold = clarification/abstention); direction inversions are clearly-labelled synthetic negatives only (mirrors the sibling H‑PS PROPOSED-PREREG-ROW-R1e). `[STIPULATED]`

# Explicitly DEFERRED to #57 + the framework revision

- Whether the programme's win condition remains efficiency W1, gains a separate correctness claim, uses correctness as a conjunctive gate, or adopts a correctness–coverage–cost Pareto axis.
- The correctness endpoint definitions, margins, rare-event sample sizes and challenge-set weights.
- The operating selective-prediction threshold and whether it is chosen for resource/index return or a dangerous-wrong upper bound.
- The numeric \(B_{\text{leak}}\), \(H_{\min}\), and pilot thresholds (prereg-freeze parameters).
- The cost coefficients in the RLEF reward and any framing-dependent retry-budget optimization.
- How abstention, harmless wrong and dangerous wrong enter the headline score.
- KOT‑FAIR/2/KOT‑AI index revisions, comparator-frontier pins, multiplicity plan, sealed-suite consistency rule and final factorial margins.
- The KOT‑FAIR/2 preregistration and KOT‑FAIR/2/P3‑D‑INDEX freeze.
- Any claim that `A‑VL` (or the H‑PS family) wins — on efficiency, correctness or kernel-specific attribution.

## Revision 1 — review fixes applied

Per [p3-arch-family-review1.md §H‑VL](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3-arch-family-review1.md) (verdict: NEEDS-FIX; "formally safe but largely redundant with H-PS under the current answer-producing engine") plus the review header's cross-draft corrections. This revision produces a REVISED PROPOSAL only; prereg-freeze waits on the #57 framework-adjudication decision + the framework blockers.

1. **Identity decision — ADOPTED, option (b) declared.** New §0 states the check-not-compute test, applies it to the current five-op terminal engine (the wrapper's check *contains* the computation; at 5.29–7.82 µs there is no verify/compute asymmetry; a host value proposal adds a corruption/leak surface while licensing nothing), and RECLASSIFIES H‑VL as an H‑PS ablation/variant family: direct engine→deterministic-render is the primary arm, the propose-value+verify loop survives only as ablation `A‑VL` with the burden of proof inverted, and the transferable machinery (three-valued contract, vresult taxonomy, stop calibrator, leak-gated diagnostics) merges into H‑PS. A precise executable re-instatement condition is recorded instead of a hedge. Option (a) — a distinct check-not-compute seam under the current grammar — was examined and rejected: no covered claim class passes the test, including `define`-with-candidate (compute-then-compare). The review-praised sound parts are retained verbatim in spirit: "verified" = agreement with the pinned engine/store (not NL-intent, not external truth), `ACCEPT/REJECT/UNVERIFIABLE`, lack-of-authority-is-not-falsity. (PROPOSED-PREREG-ROW-VL-R1a)
2. **Gameable retry signal — ADOPTED.** Record/licence IDs and value digests removed from the host channel entirely (`kot-vresult/1` witness split into `host_visible` closed-vocabulary payload vs `ledger_only`); the worked feedback example no longer names an answer-supporting record; added the §2.3 executable entropy/leak gate (closed vocabulary, per-item elimination audit under \(B_{\text{leak}}\), retry-eligibility entropy floor \(H_{\min}\), executable exhaustion prohibition) citing the programme's rules1c leak–vacuity and oracle-filtering lesson; added the §2.4 blocking real-item non-vacuity pilot (nonzero rejection, non-exhaustion, genuine formal-query repair, behavioural engagement); upgraded the lone typed-vs-constant control to the full `Qdiag-typed/const/sham` factor under one identical accept oracle, matching the sibling H‑PS convention. (PROPOSED-PREREG-ROW-VL-R1b, -VL-R1c)
3. **Training signal — ADOPTED.** "The verifier supplies all task labels" withdrawn as inaccurate; §3.3 states the correct provenance (generator supplies \(q^\*\)/answerability/ambiguity; verifier supplies acceptance only), propagated into the reward section. The filtering rung now retains only target-matching (\(q \equiv q^\*\)) accepted traces and target-matching reject→repair transitions; engine-accepted target-mismatching traces are contrastive negatives only. (PROPOSED-PREREG-ROW-VL-R1d)
4. **a5 correction (cross-draft) — ADOPTED.** The "repeated ROLE_DIR inversion" account (§2.6) and the ROLE_DIR seam row (§4) are withdrawn as STALE and replaced by the measured class: 0/43 orientation flips; all same-orientation operator substitutions inside the containment/definition frame-group, a subset surface-underdetermined `[MEASURED: docs/next/analysis/nlb-0a.md §1]`. The training corruption list (§3.2) now makes operator substitution the PRIMARY valid-but-wrong family, adds surface-underdetermined fail-closed items, and demotes direction inversions to clearly-labelled synthetic negatives. (PROPOSED-PREREG-ROW-VL-R1e)
5. **F1‑K narrative (cross-draft) — ADOPTED (already-correct content retained and strengthened).** The review confirmed the prior draft's §6 was right that F1‑K is not the H‑VL checker at small scale; Revision 1 keeps that, adds the programme-wide removal mandate for any "H‑VL = F1‑K as a small checker" framing, re-scopes the reusable carrier-transport seam to the H‑PS family per §0, and subjects carrier-transported feedback to the same §2.3 leak budget (internal transport is not a leak exemption).

Additionally (discipline, not a numbered review fix): the draft's `[SV]` markers were mapped to the programme's four-tag scheme as `[LIT-BACKED]`; measured facts carry `[MEASURED]` with source; every design choice carries `[STIPULATED]`; `[EXTRAPOLATION]` is deliberately unused (no forward performance claims pending #57). The add-capability framing is intact and is now inherited from H‑PS: the engine adds exact execution/licensing the neural baseline lacks; no matched-resource superiority is claimed; µs checking removes one cost term only.

No repository files other than this design document were changed; nothing was committed, registered, frozen, scheduled, or executed.

## Self-check (mandatory, appended per revision instructions)

1. **All five issues addressed, including an explicit identity decision?** YES — the identity decision is §0 (option (b): reclassify as H‑PS ablation/variant family, with the check-not-compute test stated, applied, and an executable re-instatement condition — not papered over); fixes 2–5 per "Revision 1" items 2–5, each naming the edited sections and its PROPOSED row. The review-praised sound parts (verified = agreement with pinned engine/store; three-valued contract; lack-of-authority ≠ falsity) are retained.
2. **Every load-bearing claim tagged?** YES — literature-derived choices carry `[LIT-BACKED]`; the a5 diagnosis, engine latency, and rules1c pilot facts carry `[MEASURED]` with sources; all design choices carry `[STIPULATED]` (§0 decision, stipulated values 1–17, PROPOSED rows); `[EXTRAPOLATION]` claims are deliberately absent.
3. **No `[MEASURED]` on a choice?** YES — `[MEASURED]` appears only on the nlb-0a diagnosis (0/43 flips, operator-substitution buckets, cross-authored surfaces), the µs engine latency, and the rules1c pilot-row fact; every prescription derived from them (reclassification, leak gate, pilot, corruption families) is `[STIPULATED]`.
4. **No @handle/account strings?** YES — checked; none present.
5. **Nothing committed/registered/frozen?** YES — this file edited in place only; registry untouched; no git operations, no runs, no goldens, no schedules; freeze explicitly waits on #57 + the framework blockers (header + Revision-1 preamble).
6. **No `ASM-<number>` ids minted?** YES — all new rows use `PROPOSED-PREREG-ROW-VL-R1a…e`; existing `ASM-*` ids are referenced nowhere in new normative text (the nlb-0a citation cites the document, not an ASM row).
7. **Add-capability framing intact, matched-resource superiority NOT claimed?** YES — the framing is inherited from the H‑PS primary arm; §1 ("The µs engine's role") retains "µs checking removes a cost term but does not make retry free"; no efficiency/correctness win is claimed anywhere ("Explicitly DEFERRED" retains the no-win-claim clause, now covering `A‑VL` and the family).
