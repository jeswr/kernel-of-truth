# P3-D-PS: H-PS NL->program-synthesis architecture — REVISED PROPOSAL (Revision 1)

> **STATUS: REVISED PROPOSAL — NOT A PREREG FREEZE.** 2026-07-19, Programme-3 Phase-1 (overflow-Fable).
> Revision 1 applies the five load-bearing fixes from the independent GPT-5.6 soundness review
> ([p3-arch-family-review1.md §H-PS](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3-arch-family-review1.md): "NEEDS-FIX, but closest to sound") to the prior
> unreviewed GPT-5.6 draft. Crux-VALIDATED add-capability architecture (per #57 Phase-0).
> ARCHITECTURE + training + seams only; the win-condition (efficiency-W1 vs correctness-endpoint)
> + KOT-FAIR/2 eval-prereg are DEFERRED to the maintainer's #57 re-weighting + the framework revision.
> **Any prereg-freeze WAITS on the #57 framework-adjudication decision AND the framework blockers
> (P3-D-THREAT revision among them, per review 1); nothing here is frozen, registered, scheduled,
> or committed.** See "## Revision 1 — review fixes applied" for the itemised changes.
> Source: poc/gpt56-review/p3d-ps-design/ + review-1 fixes.

---

# H‑PS/1 — NL→program synthesis architecture proposal

**Status:** REVISED PROPOSAL (post-review-1) for the coordinator. Text/specification only; nothing is frozen, preregistered, scheduled, or registered.

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

This is an add-capability architecture: the engine supplies exact execution, formal licensing, fail-closed error states, and provenance that the neural parser does not possess (derivation traces: conditional — only if the pre-G2 API gate proves the engine emits them; a missing interface removes the feature, it is never asserted `[STIPULATED — review-1 fix 3]`). `[LIT-BACKED]` Execution-guided decoding, execution-based selection, and trained verification establish this architectural shape, but do not establish a fully matched-resource efficiency win. Grammar constraints establish validity, not semantic correctness.

### Required invariants

1. No answer may be emitted without an `EngineResult(status=answer)`.
2. Every emitted value must be a pure, round-trip-checkable rendering of the engine’s typed value.
3. Provenance, licences, and derivation references originate only from the engine.
4. A program changed after execution must be recompiled and re-executed.
5. Unresolved formal-meaning disagreement — multiple surviving programs with distinct canonical program identities (`program_hash` inequality after canonical serialization) — triggers the semantic-risk gate (clarification or abstention) **even when every candidate returns the same typed result**. Two semantically distinct parses can coincidentally return the same result on the current store, so execution-result agreement is never evidence of resolved meaning; distinct typed results trigger the gate a fortiori. `[STIPULATED — review-1 fix 2; PROPOSED-PREREG-ROW-R1a]`
6. Execution success is never treated as evidence that the program captures the user’s intended meaning.
7. The engine remains present at deployment; LoGiPT-style emulation may assist proposal and ranking but never replaces execution in the primary architecture.

## 2. Components and interfaces

| Component | Interface | Contract |
|---|---|---|
| Boundary router | `NLRequest{text, locale, source_class, context_hash}` | Preserves original text; tries deterministic template/trie/lexicon path before learned fallback. |
| Entity linker | spans → typed URNs plus alternatives and margins | Ambiguous, missing, or type-incompatible bindings remain explicit; it never silently chooses a low-margin entity. |
| Program proposer | request → ranked `ParseProposal[]` | Emits canonical-utterance and DSL candidates, scores, bindings, operator/direction choices, and OOD/ambiguity features. It cannot emit the user-facing answer. (Predicted trace steps: CONDITIONAL, post-API-gate only — not v1.) |
| Grammar decoder/compiler | proposal → `CompiledProgram` or named refusal | Enforces the closed grammar, arity, types, allowed operators, direction vocabulary, canonical serialization, and tokenizer-mask fidelity. |
| Engine adapter | `EngineRequest{program, store_hash}` → `EngineResult` | Executes against pinned store/axiom snapshots. Returns typed value or named error, provenance, and licences. (`trace_mode` and trace hashes: CONDITIONAL, post-API-gate only — the current engine is not established to emit traces `[STIPULATED — review-1 fix 3; PROPOSED-PREREG-ROW-R1b]`.) |
| Feedback controller | proposals + diagnostics → repaired proposals | Uses bounded rounds. Diagnostics expose error class and offending field/type, not hidden gold answers. |
| Trace-emulation head (CONDITIONAL — post-API-gate only, NOT v1) | request/program prefix → predicted next engine state/action | LoGiPT-style auxiliary head for proposal/ranking, admissible only after the pre-G2 API gate proves the engine emits traces. If admitted, the real trace remains authoritative. |
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
6. Group successful programs by canonical program identity (`program_hash`), **not** by typed result. Typed-result agreement across distinct canonical programs is recorded as a risk feature; it is never disambiguation evidence. `[STIPULATED — review-1 fix 2]`
7. Apply the semantic-risk gate. It MUST fire on unresolved formal-meaning disagreement (more than one surviving canonical program) even when all candidates share one typed result; distinct typed results force it a fortiori. Coincidental result agreement between semantically distinct parses is an explicitly modelled hazard, not a resolution.
8. Render or abstain.

Partial execution and engine-derived legal-next-token masking are a later interface enhancement, not an assumption. The NTP review correctly requires an API gate first: µs final checking does not prove that the current engine emits partial states, continuation sets, or usable compiler diagnostics. `[LIT-BACKED]`

Execution feedback supplies strong **negative** evidence—invalid program, bad type, missing licence, contradiction, no record—but weak positive evidence about NL intent. A semantically wrong program can execute perfectly: the measured a5 dangerous class was **same-orientation operator substitution** (gold `contained-in` parsed as `where-defined` and conversely, over the same entity; 0/43 were orientation/direction flips, and a subset is surface-underdetermined) `[MEASURED: docs/next/analysis/nlb-0a.md §1]`. Direction-inverted programs are a synthetic instance of the same valid-but-wrong hazard, not the measured class.

## 4. Training signal

### 4.1 Training corpus

Each supervised example should carry:

```text
NL utterance x
canonical utterance c*
gold DSL program p*
typed result r*
provenance/licence witnesses
answerability/ambiguity label
semantic corruption family
```

Engine traces (τ\*) and trace hashes are **excluded from the required v1 corpus contract**: traces are conditional on an engine capability the pre-G2 API gate (§7) has not yet established, and the gate itself admits they may not exist. Trace fields join the corpus only after that gate passes `[STIPULATED — review-1 fix 3; PROPOSED-PREREG-ROW-R1b]`.

Training material should include:

- paraphrase-diverse utterances and canonical-utterance factoring; `[LIT-BACKED]`
- registered aliases and synonym resources for entity/schema linking; `[LIT-BACKED]`
- every operator and both orientations of every directional relation;
- held-out operator compositions and proof depths;
- ambiguity and unanswerability cases whose correct target is clarification or abstention;
- hard valid-but-wrong negatives, with **same-orientation operator substitution** as the primary family (the measured a5 dangerous class: 0/43 orientation flips; all container-ask operator substitutions such as `contained-in` vs `where-defined` `[MEASURED: docs/next/analysis/nlb-0a.md §1]`), plus argument swap, inverse-relation substitution, wrong-but-type-compatible entity, and scope/quantifier corruption; direction reversals are admitted only as **clearly labelled synthetic negatives** — they are not the measured class `[STIPULATED — review-1 fix 1]`;
- surface-underdetermined items (the wording contains no information discriminating the candidate operators, per the measured cross-authored a5 surfaces `[MEASURED: nlb-0a.md §1]`) whose gold target is fail-closed clarification/abstention, never either operator;
- invalid programs generated by syntax, type, arity, licensing, and entity corruptions;
- source-disjoint phrasing shifts and Dr.Spider-style perturbation families. `[LIT-BACKED]`

Engine execution may label formal validity (and, conditionally after the pre-G2 API gate, produce traces). It cannot by itself label whether a valid program expresses the intended NL meaning; that signal must come from gold generation, independently specified transformations, or adjudication.

### 4.2 Training stages

1. **Deterministic repairs first.** (The prior draft's instruction to "correct the known `ROLE_DIR` table defect" was STALE and is withdrawn: the measured a5 dangerous class was not a direction-table flip and was not fully repairable from the observed wording — 0/43 orientation flips; all same-orientation operator substitutions, a subset surface-underdetermined `[MEASURED: docs/next/analysis/nlb-0a.md §1]`.) Stage 1 requires, per that diagnosis `[STIPULATED — review-1 fix 1; PROPOSED-PREREG-ROW-R1e]`:
   - **same-orientation operator-substitution negatives** as the primary deterministic-repair and evaluation target (e.g. `contained-in` vs `where-defined` container-asks over the same entity);
   - **explicit annotation/corpus repair** of the crossed container-ask surfaces: a recorded annotation-guideline decision mapping each surface form to one operator, applied consistently across all phrasing sources (the measured DEV/EVAL cross-authoring is a corpus defect, not a parser defect);
   - **fail-closed handling where surface information is absent**: frame/operator-selection evidence absent, conflicting, or non-discriminating → no parse (clarification/abstention), never a precedence default — generalizing the NLB fail-closed law (nlb-0a.md §7, ASM-1090-PROPOSED).

   Both orientations of every directional relation remain explicit, and fail-closed defaults are preserved regardless of learned-parser choice. Direction-inversion repairs are retained only against **synthetic negatives, clearly labelled as synthetic**.

2. **Program SFT.** Train exact canonical-program generation with auxiliary operator, direction, entity-binding, and type losses. `[LIT-BACKED]` A small fine-tuned seq2seq or intent-plus-slot parser with constrained decoding is the best-supported first shape.

3. **Contrastive semantic training.** For each gold program, score same-orientation operator-substituted (the measured class `[MEASURED: nlb-0a.md §1]`), argument-swapped, and clearly-labelled synthetic direction-inverted valid programs as hard negatives. This directly targets the class that grammar and execution cannot catch. Surface-underdetermined items are NEVER trained toward either operator: their gold target is fail-closed clarification/abstention, unless prior corpus repair has made them determinate `[STIPULATED — review-1 fix 1]`.

4. **Execution-feedback refinement.** Train `diagnostic + failed program → repaired program`, and optionally verifier-based candidate ranking. Invalid-program filtering is engine-supervised; valid-but-wrong discrimination remains semantically supervised.

5. **LoGiPT-style trace emulation — CONDITIONAL, post-API-gate only; NOT part of the required v1 training contract.** This stage exists only if the pre-G2 API gate (§7) proves the engine emits traces `[STIPULATED — review-1 fix 3]`. If admitted: train iterative single-step prediction of engine states/actions, rather than whole-trace free generation. `[LIT-BACKED]` LoGiPT/ProofWriter support trace emulation as a learning signal, while the shortcut literature requires held-out rule-prior, branching, composition, and depth tests. The emulator is a proposal aid only.

6. **Selective-risk training.** Train a separate risk model or calibrated head using semantic correctness, ambiguity, same-orientation operator-substitution and (synthetic) direction-inversion, OOD, entity-margin, surviving-canonical-program-disagreement (per invariant 5 — not merely result-disagreement), and engine-diagnostic features. Abstention-aware loss is admissible. `[LIT-BACKED]`

7. **Threshold calibration.** Keep model selection, calibrator fitting, operating-threshold selection, and final evaluation disjoint. Calibration and evaluation phrasing sources must also be disjoint.

A suitable symbolic loss decomposition for the required v1 contract is:

\[
L=L_{\text{program}}+\lambda_bL_{\text{binding}}+\lambda_dL_{\text{direction}}
+\lambda_cL_{\text{contrast}}+\lambda_rL_{\text{repair}}
+\lambda_sL_{\text{selective}}.
\]

A trace term \(\lambda_tL_{\text{trace}}\) is **not** in the v1 contract; it becomes admissible only after the pre-G2 API gate proves the engine emits traces `[STIPULATED — review-1 fix 3; PROPOSED-PREREG-ROW-R1b]`.

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

The risk score must not be self-consistency alone. `[LIT-BACKED]` Self-consistency cannot detect a model that is completely confident in the same wrong answer; conformal guarantees also depend on exchangeability. Candidate agreement may be one feature, but systematic inverse and same-orientation operator-substitution tests, semantic margins, ambiguity/OOD signals, source-shift stress, and independently labelled valid-but-wrong cases are load-bearing. Per invariant 5, typed-result agreement across distinct surviving canonical programs is itself a risk-raising feature, never a risk-lowering one `[STIPULATED — review-1 fix 2]`.

When the calibration source is outside its validated envelope, the system must report that the formal guarantee is unavailable and use the frozen fail-closed action rather than silently extrapolating it.

## 6. Seams, failure modes, and P3‑D‑THREAT controls

| Seam | Failure mode | Control arm that localises it | Claim consequence |
|---|---|---|---|
| NL→operator/direction | Confident same-orientation operator substitution (the measured a5 class `[MEASURED: nlb-0a.md §1]`) or synthetic direction inversion produces a valid wrong program | `P`, plus `D`; conditional `G-rel` for relation-composition claims | If meaning permutation, operator substitution, or direction corruption does not hurt, semantic binding is not causally established. |
| Entity/store addressing | Answer-key alignment or retrieval happens to expose the answer | `D`, `I`, `T*`, `R*` | A surviving result may be retrieval or typed-store value, not kernel semantics. |
| Grammar decoder | Apparent gain is only well-formed output | `E0` with the identical grammar mask and `Q0` | Separates grammar-validity gain from engine-result use. |
| Deterministic engine | Engine runs but does not causally affect the answer | `E0`, with retry disabled in both cells (capability ablation, offline-scored — see `E0` operationalization below) | Execution attribution requires the executor-on versus bypass contrast. |
| Retry/search controller | Gain is merely more samples or retries | `Q0`, `Qsham` | Separates total search from kernel-verdict-conditioned selection. |
| Diagnostic content | "Feedback helped" is really bare rejection signal or answer leakage | `Qdiag-typed` / `Qdiag-const` / `Qdiag-sham` (same accept oracle in all three; see below) | Separates typed diagnostic content from mere rejection and from generic message statistics; leakage audit guards the channel. |
| LoGiPT trace head (CONDITIONAL — only if the pre-G2 API gate admits traces) | Model shortcuts on trace templates; engine is redundant | `E0`, `P`, `D`, plus an H‑PS-specific no-trace-training ablation | If `E0` matches, inference-retained execution earns no endpoint credit even if trace training helps. |
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

### Diagnostic-content factor (`Qdiag`) `[STIPULATED — review-1 fix 4; PROPOSED-PREREG-ROW-R1c]`

`Q0`/`Qsham` separate search quantity from kernel-verdict-conditioned selection, but do not isolate **what the typed diagnostic message contributes beyond a bare rejection**. H‑PS therefore adds a diagnostic-content factor holding the accept oracle IDENTICAL across all three arms (same engine, same acceptance decisions):

- `Qdiag-typed` — real typed diagnostics (error class + offending field/type), the deployment configuration;
- `Qdiag-const` — every rejection returns one constant, uninformative token (rejection signal only);
- `Qdiag-sham` — **information-matched sham diagnostics**: messages drawn from the true diagnostic vocabulary with matched marginal frequency, length, and entropy, but permuted across items so they are decoupled from the actual failure (message statistics preserved, item-specific content destroyed).

A "feedback helped" claim requires BOTH `Qdiag-typed` > `Qdiag-const` (content beyond bare rejection) AND `Qdiag-typed` > `Qdiag-sham` (item-specific content, not generic message statistics). Diagnostics must remain non-answer-bearing — no gold values and no record/licence identifiers sufficient to reconstruct the answer — under an explicit information/leak budget on the diagnostic channel, audited in the ledger; a budget violation is fail-closed/`INSTRUMENT-INVALID`. Without this factor, a retry lift could be explained by mere rejection signal, oracle filtering over finite options, or answer leakage `[LIT-BACKED: the programme's rules1c oracle-filtering precedent, cited in review 1]`.

### `E0` operationalization `[STIPULATED — review-1 fix 5; PROPOSED-PREREG-ROW-R1d]`

Under the required invariants the proposer cannot emit a user-facing answer (§2) and no answer may be emitted without `EngineResult(status=answer)` (invariant 1), so the executor-bypass arm `E0` **abstains by construction** on the end-to-end answer endpoint. `E0` is therefore admitted as a **capability ablation only**, NOT as a symmetric end-to-end comparator. The declared resolution (choosing explicitly between the review's two admissible options):

- **Chosen: offline program-exactness scoring.** The `E0` arm's surviving compiled programs are scored offline by the harness against gold — canonical-bytes/`program_hash` equality to \(p^\*\), plus typed-result equality computed offline by harness-side execution whose output is never shown to the arm. \(\Delta_{\text{exec}}\) is read as (a) a program-exactness/coverage contrast at the proposal seam plus (b) the end-to-end coverage collapse, reported as separate vector coordinates — never as an end-to-end "`E0` loses" scalar.
- **Rejected: an alternative answer path for `E0`.** Supplying `E0` a bypass answer route would create a second answer authority, violating invariant 1 and contaminating the ablation. The symmetric end-to-end comparator role belongs to the separately-resourced `R*` baseline (with equally strong parsing, calibration, and selective prediction), not to `E0`.

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
| Provenance | No proof follows merely from a logit lift | Engine licence for the formal program (derivation trace: conditional, post-API-gate) |

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

Adopt H‑PS/1 as a two-tier NL compiler whose learned component proposes typed programs, whose retained deterministic engine is the formal answer authority, whose LoGiPT-style trace head is auxiliary and CONDITIONAL (post-API-gate only, not v1), and whose calibrated controller may answer only through a checked, round-trip-safe rendering.

### `[STIPULATED — coordinator/Fable to ratify]` values

1. `[STIPULATED — coordinator/Fable to ratify]` First verticals use a versioned thin envelope over `kot-query/1` and `kot-query-code/1`; no open-ended code generation.
2. `[STIPULATED — coordinator/Fable to ratify]` Use a deterministic template/trie/lexicon fast path followed by a 135M learned fallback at R‑1; 360M is the next-rung fallback, not silently substituted.
3. `[STIPULATED — coordinator/Fable to ratify]` Bound inference initially to eight program candidates and two diagnostic repair rounds.
4. `[STIPULATED — coordinator/Fable to ratify]` Unresolved formal-meaning disagreement — more than one surviving canonical program (`program_hash` inequality) — forces the semantic-risk gate even when all candidates share one typed result; distinct typed results force it a fortiori; candidate majority is never answer authority; execution-result agreement is never disambiguation evidence.
5. `[STIPULATED — coordinator/Fable to ratify]` Retain the real engine at inference in every deployable H‑PS arm; emulation-only is diagnostic.
6. `[STIPULATED — coordinator/Fable to ratify]` Default to deterministic rendering; a learned renderer is admissible only behind exact typed-value and provenance round-trip checks.
7. `[STIPULATED — coordinator/Fable to ratify]` Use at least three disjoint-source phrasings per semantic item across calibration/evaluation construction.
8. `[STIPULATED — coordinator/Fable to ratify]` Carry the inherited NLB operating point—retention ≥0.90 and S2 dangerous-wrong ≤2% per vertical—as a G3 instrument target, not yet as a Programme‑3 success claim.
9. `[STIPULATED — coordinator/Fable to ratify]` Use the P3‑D‑THREAT seed derivation and five initial perturbation replicates, increased only by pre-output power analysis.
10. `[STIPULATED — coordinator/Fable to ratify]` Treat any renderer mismatch, missing required control, unavailable engine interface, diagnostic-channel leak-budget violation, or calibration-envelope violation as fail-closed/`INSTRUMENT-INVALID`.
11. `[STIPULATED — coordinator/Fable to ratify]` a5-class repair law: same-orientation operator-substitution negatives are the primary valid-but-wrong family; the crossed container-ask surfaces get explicit annotation/corpus repair; surface-underdetermined items are fail-closed (gold target = clarification/abstention); direction inversions are synthetic negatives only, clearly labelled.
12. `[STIPULATED — coordinator/Fable to ratify]` Trace fields, `trace_mode`, trace hashes, the trace-emulation head, and \(\lambda_tL_{\text{trace}}\) are excluded from the required v1 contract; each is admissible only after the pre-G2 API gate proves the engine emits it.
13. `[STIPULATED — coordinator/Fable to ratify]` Any "feedback helped" claim requires the `Qdiag-typed/const/sham` factor under one identical accept oracle, with non-answer-bearing diagnostics and an audited information/leak budget.
14. `[STIPULATED — coordinator/Fable to ratify]` `E0` is a capability ablation scored by offline program exactness (never shown to the arm); no alternative answer path is supplied in v1; the symmetric end-to-end comparator is `R*`.

### DEFERRED to #57 and the framework revision

- Whether correctness is a second claim, a conjunctive W1 gate, or a correctness–coverage–cost Pareto axis.
- Which correctness endpoint is primary and whether unconditional dangerous-wrong or selective risk is licensing.
- Correctness margins, rare-event sample sizes, confidence procedures, multiplicity family, and sealed-suite consistency rule.
- Whether the inherited 0.90/2% G3 point becomes a framework success threshold.
- The final KOT‑FAIR/2 comparator roster, index weights, resource budgets, and G4/G5 preregistration.
- Any scalarization of the correctness endpoint vector or reuse of \(\delta_k\) as a correctness attribution margin.

## PROPOSED-ASM block (doc note only; registry NOT edited)

Registry max at drafting time: ASM-2524. All rows below are PROPOSED only — nothing registered.

- **PROPOSED-PREREG-ROW-R1a:** H‑PS v1 ambiguity law — the semantic-risk gate fires on unresolved formal-meaning disagreement measured by canonical-program identity (`program_hash`), not by typed-result identity; typed-result agreement across distinct surviving programs is a risk feature only, never disambiguation evidence (execution-result agreement is not evidence of resolved meaning). `[STIPULATED]`
- **PROPOSED-PREREG-ROW-R1b:** H‑PS trace machinery (corpus τ\*, `trace_mode`, trace hashes, trace-emulation head, \(\lambda_tL_{\text{trace}}\)) is conditional on the pre-G2 API gate proving the current engine emits it; excluded from the required v1 contract; a missing interface removes the feature, it never becomes an asserted capability. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-R1c:** any H‑PS "feedback helped" claim requires the `Qdiag-typed/const/sham` diagnostic-content factor under one identical accept oracle, with non-answer-bearing diagnostics and an audited information/leak budget; violation is fail-closed/`INSTRUMENT-INVALID`. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-R1d:** `E0` is a capability ablation, not a symmetric end-to-end comparator; it is scored by offline program exactness (canonical-bytes equality to \(p^\*\) + harness-side typed-result equality, never shown to the arm); no alternative answer path in v1; the symmetric comparator role belongs to `R*`. `[STIPULATED]`
- **PROPOSED-PREREG-ROW-R1e:** H‑PS a5-class repair law — same-orientation operator-substitution negatives are the primary valid-but-wrong family (per the measured 0/43-orientation-flip diagnosis, nlb-0a.md §1); crossed container-ask surfaces receive explicit annotation/corpus repair; surface-underdetermined items are fail-closed (gold = clarification/abstention); direction inversions are clearly-labelled synthetic negatives only (generalizes nlb-0a's ASM-1090-PROPOSED to H‑PS). `[STIPULATED]`

## Revision 1 — review fixes applied

Per [p3-arch-family-review1.md §H‑PS](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3-arch-family-review1.md) (verdict: NEEDS-FIX, closest to sound). This revision produces a REVISED PROPOSAL only; prereg-freeze waits on the #57 framework-adjudication decision + the framework blockers.

1. **a5 fix — ADOPTED.** The stale "correct the known `ROLE_DIR` table defect" instruction is withdrawn from training stage 1. Replaced with same-orientation operator-substitution negatives (primary family), explicit annotation/corpus repair of the crossed container-ask surfaces, and fail-closed handling where surface information is absent, per the measured diagnosis (0/43 orientation flips `[MEASURED: nlb-0a.md §1]`). Direction inversions retained only as clearly-labelled synthetic negatives. Propagated to §3, §4.1 negatives, §4.2 stages 1/3, §5 features, the §6 seam table, and handoff value 11. (PROPOSED-PREREG-ROW-R1e)
2. **Ambiguity rule — ADOPTED.** Invariant 5, loop steps 6–7, §5, and handoff value 4 now gate on unresolved formal-meaning disagreement measured by canonical-program identity, firing even when all candidates share a typed result; execution-result agreement is explicitly not evidence of resolved meaning. (PROPOSED-PREREG-ROW-R1a)
3. **Trace machinery — ADOPTED.** Trace fields, `trace_mode`, trace hashes, the trace-emulation head, corpus τ\*, and \(\lambda_tL_{\text{trace}}\) removed from the required v1 contract (§2 table, §4.1, §4.2 stage 5, loss decomposition, handoff value 12); each returns only after the pre-G2 API gate proves the engine emits it. (PROPOSED-PREREG-ROW-R1b)
4. **Feedback controls — ADOPTED.** Added the `Qdiag-typed/const/sham` diagnostic-content factor under one identical accept oracle, with information-matched sham construction, non-answer-bearing diagnostics, and an audited leak budget; a "feedback helped" claim now requires beating BOTH the constant and the information-matched sham arms. (PROPOSED-PREREG-ROW-R1c)
5. **E0 operational clarification — ADOPTED (option declared).** `E0` is stated to abstain by construction and is admitted as a capability ablation only. Declared option: **program exactness scored offline** (harness-side, never shown to the arm); the alternative-answer-path option is explicitly rejected because it would create a second answer authority and violate invariant 1; the symmetric end-to-end comparator duty is assigned to `R*`. (PROPOSED-PREREG-ROW-R1d)

Additionally (discipline, not a numbered review fix): the draft's `[SV]` markers were mapped to the programme's four-tag scheme as `[LIT-BACKED]`; new measured facts carry `[MEASURED]` with source; every new design choice carries `[STIPULATED]`. The sound invariants the review praised are unchanged or strengthened: no program mutation post-execution (invariant 4), no provenance fabrication (invariant 3), execution-success ≠ intent-correctness (invariant 6), and the strong-negative/weak-positive evidence asymmetry (§3). The add-capability framing is intact: H‑PS adds an exact-execution capability the baseline lacks; no matched-resource efficiency win is claimed (§1, §9).

No repository files other than this design document were changed; nothing was committed, registered, frozen, scheduled, or executed.

## Self-check (mandatory, appended per revision instructions)

1. **All five fixes addressed?** YES — see "Revision 1" items 1–5; each names the sections edited and its PROPOSED-ASM row. Fix 1: §4.2 stage 1 no longer mentions repairing `ROLE_DIR` as the dangerous-class fix; fix 2: invariant 5 + loop steps 6–7 gate on program identity; fix 3: no trace field, trace loss, or trace head remains in the required v1 contract (all remaining mentions are marked CONDITIONAL, post-API-gate); fix 4: `Qdiag` factor defined in §6 with both required inequalities; fix 5: `E0` scoring option explicitly declared (offline program exactness) and the alternative explicitly rejected.
2. **Every load-bearing claim tagged?** YES — literature-derived claims carry `[LIT-BACKED]`, measured a5/l3a facts carry `[MEASURED: nlb-0a.md §1]`, all design choices carry `[STIPULATED]` (handoff values 1–14, new invariant text, `Qdiag`/`E0` sections, PROPOSED-ASM rows); no `[EXTRAPOLATION]` claims are made in this revision — forward performance statements are deliberately absent pending #57.
3. **No `[MEASURED]` on a choice?** YES — `[MEASURED]` appears only on the nlb-0a diagnosis facts (0/43 flips, operator-substitution buckets, cross-authored surfaces); every prescription derived from them is tagged `[STIPULATED]`.
4. **No @handle/account strings?** YES — checked; none present.
5. **Nothing committed/registered/frozen?** YES — this file edited in place only; registry untouched (assumption rows are PROPOSED-only); no git operations, no runs, no goldens, no schedules.
6. **Add-capability framing intact, matched-resource superiority NOT claimed?** YES — §1 retains "does not establish a fully matched-resource efficiency win"; §9 retains "The literature supplies no prior that it will"; the `E0` clarification and `R*` comparator assignment reinforce, not weaken, this framing.