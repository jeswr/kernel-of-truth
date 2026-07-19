# P3-D-PS: H-PS NL->program-synthesis architecture — GPT-5.6 DRAFT

> **STATUS: UNREVIEWED GPT-5.6 DRAFT.** 2026-07-19, Programme-3 Phase-1 (overflow-Fable). Crux-VALIDATED
> add-capability architecture (per #57 Phase-0). ARCHITECTURE + training + seams only; the win-condition
> (efficiency-W1 vs correctness-endpoint) + KOT-FAIR/2 eval-prereg are DEFERRED to the maintainer's #57
> re-weighting + the framework revision. NEXT: review gate -> Fable critique -> prereg. Not frozen.
> Source: poc/gpt56-review/p3d-ps-design/.

---

# H‑PS/1 — NL→program synthesis architecture proposal

**Status:** PROPOSAL for the review gate and Fable. Text/specification only; nothing is frozen, preregistered, scheduled, or changed in the repository.

This proposal instantiates the H‑PS family described in [Programme‑3 §3.3a](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:717), follows the [G1–G5 gate ladder](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/programme-3-neurosymbolic-architecture.md:854), adopts the add-capability conclusion of [P3‑LR‑PARSE](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-parse.md:209), and uses the control definitions in [P3‑D‑THREAT](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md:96).

## 1. Architectural decision

H‑PS/1 is a fail-closed compiler–executor system:

```text
natural input
  → deterministic fast path / entity linking
  → learned, grammar-constrained program proposer
  → canonical DSL compiler + static checks
  → bounded execute–diagnose–repair loop
  → retained deterministic engine
  → calibrated risk gate
  → deterministic checked-result renderer
  → answer | clarification | abstention
```

The model is an **untrusted program proposer**. The deterministic engine is the **formal answer authority** for covered programs. The renderer may express the engine’s typed result but may not alter it.

This is an add-capability architecture: the engine supplies exact execution, formal licensing, fail-closed error states, provenance, and derivation traces that the neural parser does not possess. `[SV]` Execution-guided decoding, execution-based selection, and trained verification establish this architectural shape, but do not establish a fully matched-resource efficiency win. Grammar constraints establish validity, not semantic correctness.

### Required invariants

1. No answer may be emitted without an `EngineResult(status=answer)`.
2. Every emitted value must be a pure, round-trip-checkable rendering of the engine’s typed value.
3. Provenance, licences, and derivation references originate only from the engine.
4. A program changed after execution must be recompiled and re-executed.
5. Multiple surviving programs that produce distinct typed results cause clarification or abstention.
6. Execution success is never treated as evidence that the program captures the user’s intended meaning.
7. The engine remains present at deployment; LoGiPT-style emulation may assist proposal and ranking but never replaces execution in the primary architecture.

## 2. Components and interfaces

| Component | Interface | Contract |
|---|---|---|
| Boundary router | `NLRequest{text, locale, source_class, context_hash}` | Preserves original text; tries deterministic template/trie/lexicon path before learned fallback. |
| Entity linker | spans → typed URNs plus alternatives and margins | Ambiguous, missing, or type-incompatible bindings remain explicit; it never silently chooses a low-margin entity. |
| Program proposer | request → ranked `ParseProposal[]` | Emits canonical-utterance and DSL candidates, scores, bindings, operator/direction choices, OOD/ambiguity features, and optional predicted trace steps. It cannot emit the user-facing answer. |
| Grammar decoder/compiler | proposal → `CompiledProgram` or named refusal | Enforces the closed grammar, arity, types, allowed operators, direction vocabulary, canonical serialization, and tokenizer-mask fidelity. |
| Engine adapter | `EngineRequest{program, store_hash, trace_mode}` → `EngineResult` | Executes against pinned store/axiom snapshots. Returns typed value or named error, provenance, licences, and trace hash. |
| Feedback controller | proposals + diagnostics → repaired proposals | Uses bounded rounds. Diagnostics expose error class and offending field/type, not hidden gold answers. |
| Trace-emulation head | request/program prefix → predicted next engine state/action | LoGiPT-style auxiliary head for proposal/ranking. The real trace remains authoritative. |
| Risk controller | all parser/compiler/engine features → `Decision` | Returns `answer`, `clarify`, or `abstain`, plus frozen threshold id, risk score, calibration stratum, and reason codes. |
| Checked renderer | typed result → surface answer | Prefer deterministic templates. Any learned paraphraser must pass exact typed-value round-trip and provenance-preservation checks. |
| Audit ledger | every boundary artifact | Records hashes, candidates, static failures, engine calls, retries, decision, cost, and final rendering without exposing hidden evaluation material. |

### DSL

The first implementation should use a thin versioned envelope over the existing `kot-query/1` and `kot-query-code/1` grammars, whose licensing and refusal semantics are already explicit in [the L3a engine design](/home/ec2-user/css/kernel/kernel-of-truth/docs/design-l3a-rules-engine-oracle.md:90).

A compiled program contains at least:

```text
grammar_version
vertical
operator
typed_arguments
relation
direction
expected_return_type
canonical_program_bytes
program_hash
binding_witnesses
```

Free-form code, implicit coercions, undeclared operators, and untyped arguments are outside H‑PS/1.

## 3. Execution-feedback loop

The minimum viable loop works on complete candidate programs:

1. Generate constrained candidates.
2. Compile and reject syntax/type/licensing failures.
3. Execute surviving candidates.
4. Feed normalized engine diagnostics into a bounded repair step.
5. Recompile and re-execute repairs.
6. Group successful programs by canonical typed result.
7. Apply the semantic-risk gate.
8. Render or abstain.

Partial execution and engine-derived legal-next-token masking are a later interface enhancement, not an assumption. The NTP review correctly requires an API gate first: µs final checking does not prove that the current engine emits partial states, continuation sets, or usable compiler diagnostics. `[SV]`

Execution feedback supplies strong **negative** evidence—invalid program, bad type, missing licence, contradiction, no record—but weak positive evidence about NL intent. A direction-inverted, semantically wrong program can execute perfectly.

## 4. Training signal

### 4.1 Training corpus

Each supervised example should carry:

```text
NL utterance x
canonical utterance c*
gold DSL program p*
engine trace τ*
typed result r*
provenance/licence witnesses
answerability/ambiguity label
semantic corruption family
```

Training material should include:

- paraphrase-diverse utterances and canonical-utterance factoring; `[SV]`
- registered aliases and synonym resources for entity/schema linking; `[SV]`
- every operator and both orientations of every directional relation;
- held-out operator compositions and proof depths;
- ambiguity and unanswerability cases whose correct target is clarification or abstention;
- hard valid-but-wrong negatives: direction reversal, argument swap, inverse-relation substitution, operator swap, wrong-but-type-compatible entity, and scope/quantifier corruption;
- invalid programs generated by syntax, type, arity, licensing, and entity corruptions;
- source-disjoint phrasing shifts and Dr.Spider-style perturbation families. `[SV]`

Engine execution may label formal validity and produce traces. It cannot by itself label whether a valid program expresses the intended NL meaning; that signal must come from gold generation, independently specified transformations, or adjudication.

### 4.2 Training stages

1. **Deterministic repairs first.** Correct the known `ROLE_DIR` table defect, make both orientations explicit, and preserve fail-closed defaults regardless of learned-parser choice.

2. **Program SFT.** Train exact canonical-program generation with auxiliary operator, direction, entity-binding, and type losses. `[SV]` A small fine-tuned seq2seq or intent-plus-slot parser with constrained decoding is the best-supported first shape.

3. **Contrastive semantic training.** For each gold program, score direction-inverted and argument-swapped valid programs as hard negatives. This directly targets the class that grammar and execution cannot catch.

4. **Execution-feedback refinement.** Train `diagnostic + failed program → repaired program`, and optionally verifier-based candidate ranking. Invalid-program filtering is engine-supervised; valid-but-wrong discrimination remains semantically supervised.

5. **LoGiPT-style trace emulation.** Train iterative single-step prediction of engine states/actions, rather than whole-trace free generation. `[SV]` LoGiPT/ProofWriter support trace emulation as a learning signal, while the shortcut literature requires held-out rule-prior, branching, composition, and depth tests. The emulator is a proposal aid only.

6. **Selective-risk training.** Train a separate risk model or calibrated head using semantic correctness, ambiguity, direction-inversion, OOD, entity-margin, result-disagreement, and engine-diagnostic features. Abstention-aware loss is admissible. `[SV]`

7. **Threshold calibration.** Keep model selection, calibrator fitting, operating-threshold selection, and final evaluation disjoint. Calibration and evaluation phrasing sources must also be disjoint.

A suitable symbolic loss decomposition is:

\[
L=L_{\text{program}}+\lambda_bL_{\text{binding}}+\lambda_dL_{\text{direction}}
+\lambda_cL_{\text{contrast}}+\lambda_rL_{\text{repair}}
+\lambda_tL_{\text{trace}}+\lambda_sL_{\text{selective}}.
\]

The \(\lambda\) values are dev-selected under the same tuning-compute ceiling as comparator systems; no coefficients are fixed here.

## 5. Calibrated abstention and S2

Define a dangerous wrong operationally as:

\[
DW = \text{answered} \land \text{semantically wrong}
     \land \text{provenance/licence presented}.
\]

The architecture must emit enough information to report all of:

- answer coverage;
- unconditional \(P(DW)\);
- selective \(P(DW\mid answered)\);
- ordinary end-to-end semantic correctness;
- accepted formal-soundness violations;
- the entire risk–coverage curve and AUACC;
- per-operator, direction, relation, ambiguity, and phrasing-source strata.

No combined correctness scalar is proposed.

The risk score must not be self-consistency alone. `[SV]` Self-consistency cannot detect a model that is completely confident in the same wrong answer; conformal guarantees also depend on exchangeability. Candidate agreement may be one feature, but systematic inverse tests, semantic margins, ambiguity/OOD signals, source-shift stress, and independently labelled valid-but-wrong cases are load-bearing.

When the calibration source is outside its validated envelope, the system must report that the formal guarantee is unavailable and use the frozen fail-closed action rather than silently extrapolating it.

## 6. Seams, failure modes, and P3‑D‑THREAT controls

| Seam | Failure mode | Control arm that localises it | Claim consequence |
|---|---|---|---|
| NL→operator/direction | Confident direction inversion produces a valid wrong program | `P`, plus `D`; conditional `G-rel` for relation-composition claims | If meaning permutation or direction corruption does not hurt, semantic binding is not causally established. |
| Entity/store addressing | Answer-key alignment or retrieval happens to expose the answer | `D`, `I`, `T*`, `R*` | A surviving result may be retrieval or typed-store value, not kernel semantics. |
| Grammar decoder | Apparent gain is only well-formed output | `E0` with the identical grammar mask and `Q0` | Separates grammar-validity gain from engine-result use. |
| Deterministic engine | Engine runs but does not causally affect the answer | `E0`, with retry disabled in both cells | Execution attribution requires the executor-on versus bypass contrast. |
| Retry/search controller | Gain is merely more samples or retries | `Q0`, `Qsham` | Separates total search from kernel-verdict-conditioned selection. |
| LoGiPT trace head | Model shortcuts on trace templates; engine is redundant | `E0`, `P`, `D`, plus an H‑PS-specific no-trace-training ablation | If `E0` matches, inference-retained execution earns no endpoint credit even if trace training helps. |
| Kernel semantics | Generic typed lookup/filter/join supplies the same result | `T*` | Attribute to aligned typed storage/generic tools, not kernel semantics. |
| Same evidence through generic tools | Conventional RAG/tool-use plus selective prediction matches H‑PS | `R*` | W1 cannot pass against the frontier; any correctness result is generic-tool-labelled. |
| Checked-result delivery | Native structured result adds nothing over text delivery | `X*` | No native integration claim; engine information may still matter. |
| Renderer | Surface generation corrupts a checked result | Hard round-trip invariant; `X*` diagnoses text-interface sensitivity | Any mismatch is `INSTRUMENT-INVALID`, not an architecture error bar. |
| Abstention/calibration | Confident-wrong survives calibration or shift | `P`/`D` semantic corruptions and the selective-prediction `R*` baseline | No S2/fail-closed claim; average parser accuracy cannot rescue it. |
| Graph/rule composition | Model follows text or labels rather than topology | `G-edge`, `G-rel`, `G-adv` when such a claim is made | Structure/topology wording is killed if any required contrast fails. |

The central executor factorial is:

\[
\Delta_{\text{exec}}
 =Y(K,E1,Q0)-Y(K,E0,Q0)
\]

\[
\Delta_{\text{retry}}=Y(F)-Y(Q0),\qquad
\Delta_{\text{conditioned-search}}=Y(F)-Y(Qsham).
\]

Until #57 is resolved, \(Y\) is a **reported endpoint vector**, not a scalarized verdict: coverage, semantic correctness, dangerous-wrong risk, accepted soundness violations, and resource coordinates are contrasted separately.

## 7. Gate-ladder placement

- **Pre-G2 API gate:** prove the engine emits every interface the architecture intends to consume. Missing traces or legal-continuation APIs remove that feature; they do not become asserted capabilities.
- **G1:** compute the coverage ceiling before parser or GPU spend. H‑PS cannot correct uncovered questions.
- **G2 oracle-interface:** gold program → compiler → engine → risk gate → renderer. Run `E0/Q0/Qsham/X*` here. This isolates executor, search, and rendering without NL confounding; it remains `oracle-diagnostic`.
- **G3 boundary-degradation:** replace gold programs with NL synthesis. Report oracle-to-synthesized loss separately for entity linking, operator/direction, serialization, execution, risk gating, and rendering. This is the P3‑E‑NLB/P3‑E‑PS seam.
- **G4/G5:** full frontier and scaling claims await #57 and KOT‑FAIR/2.

## 8. Connection to F1‑K

The current [F1‑K record](/home/ec2-user/css/kernel/kernel-of-truth/registry/experiments/f1k.json:1) asks whether a training-free, concept-gated internal carrier improves QA correctness over the unmodified model, dose-exact derangements, and a plain-dictionary carrier. H‑PS asks whether an external deterministic executor, reached through NL→DSL, produces safer and more correct accepted answers.

| Dimension | F1‑K | H‑PS |
|---|---|---|
| Add-capability seam | Internal activation carrier | External compiler/executor authority |
| Neural component | End-task answer scorer | Untrusted program proposer |
| Correctness mechanism | Grounded content changes logits | Checked execution and fail-closed refusal |
| Main causal controls | Base, derangement, dictionary | `E0`, `Q0`, `Qsham`, `P/D/I`, `T*`, `R*`, `X*` |
| Principal risk | Carrier identity/structure may not matter | Valid-but-wrong formalization may execute perfectly |
| Provenance | No proof follows merely from a logit lift | Engine licence and derivation trace for the formal program |

They are complementary tests of the broad correctness thesis, not substitutes:

- F1‑K positive/H‑PS negative localizes failure to the NL/program/execution/rendering path.
- H‑PS positive/F1‑K negative supports external exact authority, not internal carrier value.
- If `E0` fails but `T*` matches, deterministic execution matters while kernel-specific semantics do not.
- If both are positive, each licenses only its own seam and control ladder.
- H‑PS must not inherit F1‑K’s margins, power, or carrier claim.

## 9. The unresolved framing

Under an **efficiency-W1 framing**, the engine, parser, retries, store, and renderer are all charged; H‑PS must beat the strongest admissible neural/RAG/tool frontier, including `R*`. The literature supplies no prior that it will.

Under a **correctness-endpoint framing**, the same architecture and controls remain, but dangerous-wrong, accepted soundness violations, semantic correctness, coverage, and cost could become a second claim, conjunctive gate, or Pareto axes.

This proposal does not choose between them.

## Review-gate handoff

### Architecture

Adopt H‑PS/1 as a two-tier NL compiler whose learned component proposes typed programs, whose retained deterministic engine is the formal answer authority, whose LoGiPT-style trace head is auxiliary, and whose calibrated controller may answer only through a checked, round-trip-safe rendering.

### `[STIPULATED — coordinator/Fable to ratify]` values

1. `[STIPULATED — coordinator/Fable to ratify]` First verticals use a versioned thin envelope over `kot-query/1` and `kot-query-code/1`; no open-ended code generation.
2. `[STIPULATED — coordinator/Fable to ratify]` Use a deterministic template/trie/lexicon fast path followed by a 135M learned fallback at R‑1; 360M is the next-rung fallback, not silently substituted.
3. `[STIPULATED — coordinator/Fable to ratify]` Bound inference initially to eight program candidates and two diagnostic repair rounds.
4. `[STIPULATED — coordinator/Fable to ratify]` Distinct successful typed results force clarification or abstention; candidate majority is never answer authority.
5. `[STIPULATED — coordinator/Fable to ratify]` Retain the real engine at inference in every deployable H‑PS arm; emulation-only is diagnostic.
6. `[STIPULATED — coordinator/Fable to ratify]` Default to deterministic rendering; a learned renderer is admissible only behind exact typed-value and provenance round-trip checks.
7. `[STIPULATED — coordinator/Fable to ratify]` Use at least three disjoint-source phrasings per semantic item across calibration/evaluation construction.
8. `[STIPULATED — coordinator/Fable to ratify]` Carry the inherited NLB operating point—retention ≥0.90 and S2 dangerous-wrong ≤2% per vertical—as a G3 instrument target, not yet as a Programme‑3 success claim.
9. `[STIPULATED — coordinator/Fable to ratify]` Use the P3‑D‑THREAT seed derivation and five initial perturbation replicates, increased only by pre-output power analysis.
10. `[STIPULATED — coordinator/Fable to ratify]` Treat any renderer mismatch, missing required control, unavailable engine interface, or calibration-envelope violation as fail-closed/`INSTRUMENT-INVALID`.

### DEFERRED to #57 and the framework revision

- Whether correctness is a second claim, a conjunctive W1 gate, or a correctness–coverage–cost Pareto axis.
- Which correctness endpoint is primary and whether unconditional dangerous-wrong or selective risk is licensing.
- Correctness margins, rare-event sample sizes, confidence procedures, multiplicity family, and sealed-suite consistency rule.
- Whether the inherited 0.90/2% G3 point becomes a framework success threshold.
- The final KOT‑FAIR/2 comparator roster, index weights, resource budgets, and G4/G5 preregistration.
- Any scalarization of the correctness endpoint vector or reuse of \(\delta_k\) as a correctness attribution margin.

No repository files were changed.