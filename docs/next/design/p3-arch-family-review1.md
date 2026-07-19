# Programme-3 Phase-1 architecture family — review 1 (soundness/coherence/gameability)

> **STATUS: REVIEW OUTPUT.** GPT-5.6 soundness review of the 4 crux-aligned Phase-1 drafts (P3-D-THREAT/VL/PS/GU),
> 2026-07-19. Verdict: sound core, NONE freeze-ready unchanged; **H-PS closest**. Two corrections: (1) the a5 failure
> is NOT a ROLE_DIR direction inversion — current diagnosis (docs/next/analysis/nlb-0a.md) = 0/43 orientation flips,
> all same-orientation operator substitutions, sometimes surface-underdetermined; (2) H-VL is NOT "the F1-K checker at
> small scale" (F1-K is an activation carrier/splice experiment; only the carrier-transport seam is reusable — remove
> that narrative). Promotion order: H-PS -> H-VL(after identity settled) -> H-GU(API-gate prereg only) -> THREAT
> (revise before it governs any). All 4 -> Fable now as proposals; prereg after #57/framework unblock. Add-capability
> discipline correctly applied. Source: poc/gpt56-review/p3arch-family-review/.

---

Overall verdict: the family has a sound core, but none of the four drafts is ready to freeze unchanged. H-PS is closest. H-VL is formally safe but largely redundant with H-PS under the current answer-producing engine. H-GU is coherent only conditional on a proof-state API that does not yet exist. THREAT has the right attribution dimensions, but several controls are not executable or causally clean for these architectures as written.

There is no backward-confidence-bound error analogous to the framework floor rule. There is, however, one definite factual error across the drafts: the repeated account of the measured a5 failure as a `ROLE_DIR` orientation inversion is now stale. The current diagnosis found 0/43 orientation flips; all were same-orientation operator substitutions, with cross-authored phrases that did not contain enough information to distinguish `contained-in` from `where-defined` ([nlb-0a.md:59](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/nlb-0a.md:59), [nlb-0a.md:65](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/nlb-0a.md:65), [nlb-0a.md:78](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/nlb-0a.md:78), [nlb-0a.md:219](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/nlb-0a.md:219)).

## H-VL — NEEDS-FIX

The formal soundness contract is good. The draft correctly limits “verified” to agreement with the pinned engine/store, explicitly excluding NL-intent correctness and external truth ([p3d-vl-architecture.md:17](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-vl-architecture.md:17)). Its `ACCEPT/REJECT/UNVERIFIABLE` distinction is appropriate, especially the rule that lack of authority is not falsity ([p3d-vl-architecture.md:93](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-vl-architecture.md:93)). The five stated engine operations also match the implementation: terminal lookup, unique, count, instance, and exact definition matching ([kot_axiom.py:547](/home/ec2-user/css/kernel/kernel-of-truth/tools/axiom/kot_axiom.py:547), [kot_axiom.py:611](/home/ec2-user/css/kernel/kernel-of-truth/tools/axiom/kot_axiom.py:611), [kot_axiom.py:683](/home/ec2-user/css/kernel/kernel-of-truth/tools/axiom/kot_axiom.py:683)).

The central problem is that this engine computes \(v^\*\), rather than merely checking a proof the host alone could produce. The wrapper runs the query, obtains the canonical answer, and compares the host value to it ([p3d-vl-architecture.md:93](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-vl-architecture.md:93)). Once \(q\) is trusted enough to execute, the cheaper and safer action is normally to render \(v^\*\) directly. The draft recognizes this and says a direct engine→renderer arm may reclassify the survivor as H-PS ([p3d-vl-architecture.md:275](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-vl-architecture.md:275)). That is not a minor ablation: under the current grammar it challenges H-VL’s architectural identity. Value mismatch retries repair something the engine can overwrite deterministically; semantic-query mistakes remain invisible because the wrong \(q\) can execute and be accepted.

The retry signal is also still gameable. The host can receive record and licence IDs, and the worked feedback example names an answer-supporting record ([p3d-vl-architecture.md:148](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-vl-architecture.md:148)). A typed-vs-constant-feedback contrast proves that feedback content mattered, but does not distinguish genuine diagnostic use from answer leakage. The existing programme record shows why this matters: finite-option retry can become oracle filtering, with a working verifier converging toward its own knowledge without host understanding ([rules1c-instrument-invalid-interpretation.md:125](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/rules1c-instrument-invalid-interpretation.md:125)). H-VL prohibits exhausting finite options in prose, but needs an executable entropy/leak gate and a blocking real-item non-vacuity pilot.

The training signal is almost correct. Requiring known \(q^\*\), semantic equivalence, and verifier acceptance prevents rewarding arbitrary executable programs ([p3d-vl-architecture.md:238](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-vl-architecture.md:238)). But “the verifier supplies all task labels” is inaccurate: the generator supplies \(q^\*\), answerability, and ambiguity labels. Likewise, the accepted-trace filtering rung must retain only target-matching accepted traces, not everything the engine accepts ([p3d-vl-architecture.md:228](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-vl-architecture.md:228)).

The measured-error discussion must be corrected: the draft repeatedly calls the a5 mechanism a direction inversion ([p3d-vl-architecture.md:188](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-vl-architecture.md:188), [p3d-vl-architecture.md:264](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-vl-architecture.md:264)). Direction inversions remain useful synthetic negatives, but the measured class is now same-orientation operator ambiguity, sometimes fundamentally underdetermined by the surface.

On F1-K, the draft is correct: F1-K is not an H-VL checker at small scale. It is an activation carrier/splice experiment, not an inference-time proof or query verifier ([p3d-vl-architecture.md:290](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-vl-architecture.md:290)). Only the carrier transport seam is reusable. Any programme narrative calling H-VL “F1-K as a small checker” should be removed.

Before preregistration, H-VL needs:

- A decision whether it checks claims the engine cannot directly answer, or collapses into H-PS for the present grammar.
- A direct engine→deterministic-render primary comparator.
- Target-matched rather than merely engine-accepted training filters.
- Non-answer-bearing diagnostics, an information/entropy audit, and a same-oracle sham-feedback arm.
- A blocking real-item pilot proving nonzero rejection, non-exhaustion, and actual formal-query repair.
- The corrected a5 ambiguity/operator-substitution failure family.

## H-PS — NEEDS-FIX, but closest to sound

H-PS is the cleanest match to the current engine. The model proposes a closed typed program; the engine executes it; the checked result is deterministically rendered ([p3d-ps-architecture.md:19](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md:19)). Its invariants correctly prevent program mutation after execution, provenance fabrication, or treating execution success as intent correctness ([p3d-ps-architecture.md:37](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md:37)). The statement that execution gives strong negative evidence but weak positive evidence about NL intent is exactly right ([p3d-ps-architecture.md:83](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md:83)).

Its training signal is also sounder than VL’s: it explicitly requires gold programs, semantic corruption families, answerability labels, and valid-but-wrong negatives, while admitting that the engine cannot label NL semantic equivalence ([p3d-ps-architecture.md:102](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md:102), [p3d-ps-architecture.md:128](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md:128)). Execution feedback is appropriately confined to invalid-program repair; semantic discrimination remains separately supervised ([p3d-ps-architecture.md:134](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md:134)).

Three fixes are load-bearing.

First, training stage 1 says to “correct the known `ROLE_DIR` table defect” ([p3d-ps-architecture.md:132](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md:132)). The current evidence says the a5 dangerous class was not a direction-table flip and was not fully repairable from the observed wording. The design needs same-orientation operator-substitution negatives, explicit annotation/corpus repair, and fail-closed handling where surface information is absent.

Second, the ambiguity rule is insufficient. The system groups successful programs by typed result, and only distinct results force clarification or abstention ([p3d-ps-architecture.md:85](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md:85)). Two semantically distinct parses can coincidentally return the same result. Execution-result agreement is therefore not evidence of a resolved meaning. Unresolved formal-meaning disagreement must trigger the risk gate even when all candidates share a result.

Third, trace machinery is presently conditional, not a current engine feature. The component and corpus specifications assume traces and trace hashes ([p3d-ps-architecture.md:55](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md:55), [p3d-ps-architecture.md:104](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md:104)), while the API gate correctly admits that these may not exist ([p3d-ps-architecture.md:214](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md:214)). Trace fields and losses should be removed from the required v1 contract and added only after that gate passes.

The feedback controls also need one extra factor: `Q0/Qsham` separate search quantity and selection, but do not isolate typed diagnostic content from a bare rejection. PS needs the same accept oracle with typed, constant, and information-matched sham diagnostics.

Finally, `E0` requires operational clarification. The proposer is prohibited from emitting a user-facing answer and the architecture forbids answers without engine success ([p3d-ps-architecture.md:39](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md:39), [p3d-ps-architecture.md:53](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md:53)). An executor-bypass product therefore abstains by construction. That is acceptable as a capability ablation, but it is not a symmetric end-to-end comparator unless program exactness is scored offline or a declared alternative answer path is supplied.

With those fixes, H-PS is sound enough for Fable and then preregistration once the framework blockers clear.

## H-GU — NEEDS-FIX

The conceptual training design is good. “Executor-in-the-loss” is correctly defined as discrete engine outcomes controlling data admission, targets, feedback, and rewards—not backpropagation through the engine ([p3d-gu-architecture.md:130](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md:130)). The T0–T5 ladder stages evidence sensibly, and the `Tr×E` grid cleanly separates internalized training benefit from runtime engine benefit ([p3d-gu-architecture.md:153](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md:153), [p3d-gu-architecture.md:204](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md:204)). T4’s prohibition on rewarding unpaired natural text is particularly important ([p3d-gu-architecture.md:190](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md:190)).

But this is not yet an architecture over the current KOT engine. GU assumes legal actions, proof states, state transitions, proof fragments, and terminal certificates ([p3d-gu-architecture.md:23](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md:23), [p3d-gu-architecture.md:88](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md:88)). The current engine accepts whole `kot-query/1` objects and returns terminal answers/refusals; it exposes no proof-search transition system. The draft acknowledges this through a blocking API gate ([p3d-gu-architecture.md:224](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md:224)), but the final handoff nevertheless adopts the full trace/filter/RLEF/RL recipe ([p3d-gu-architecture.md:320](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md:320)). Until the action DSL, state semantics, certificate condition, and search boundary exist, only the API-gate preregistration is ready.

There is also an internal authority conflict. The architectural claim says the retained engine is the sole formal answer authority ([p3d-gu-architecture.md:19](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md:19)), but the router may choose a “direct answer” path ([p3d-gu-architecture.md:122](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md:122)). Either direct answers must also receive engine certification, or they are outside H-GU’s licensed result set. Similarly, `AMBIGUOUS` belongs at the NL/router layer unless the formal task itself explicitly represents ambiguity; it should not be presented as an engine judgment.

T2 must bind admitted positives to the generator target. “Formally valid success” alone is vulnerable to accepting a valid proof/action sequence for the wrong formalization ([p3d-gu-architecture.md:172](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md:172)). The generator already records the target, so target-hash equality should be mandatory.

“No human labels” is defensible only for generator-pinned formal/synthetic training. It does not cover natural-input intent correctness, which the draft itself says the engine cannot establish ([p3d-gu-architecture.md:41](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md:41)). The heading and handoff should state that scope explicitly.

Before full preregistration GU needs:

- A demonstrated step-transition engine API and explicit action/state/certificate semantics.
- A statement-supply/diversity curve before RL spend.
- Removal or certification of the direct-answer route.
- Target-bound T2 filtering.
- Separate final-label-only, genuine-trace, shuffled/mismatched-trace, filter, feedback, and reward cells at matched task/token/compute exposure.
- A trajectory-level definition of `Q0/Qsham`; “first candidate” is undefined for multi-step proof search.

## P3-D-THREAT — NEEDS-FIX

THREAT is a strong attribution skeleton. Its motivated-operator threat model is realistic, it names the relevant packaging and answer-key games ([p3d-threat-factorial-controls.md:31](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md:31)), and its six-way contrast ledger correctly avoids forcing interacting effects into percentages ([p3d-threat-factorial-controls.md:357](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md:357)). `T`, `R`, `X`, `E0`, `Q0`, and `Qsham` are the right conceptual dimensions.

The architecture mapping is not yet sound enough:

| Factor | Verdict for VL/PS/GU |
|---|---|
| `D`/`I` | Under-specified. They replace retrieved bundles, but these engines execute a formal query against an authoritative global snapshot. Unless the authoritative query→store binding is also transformed, the engine path can remain unchanged. |
| `P` | Useful at the NL/schema binding seam, but not a test of whole-query engine semantics at G2. It needs architecture-specific parser/lexicon/action-vocabulary instantiation plus an equivariant-renaming positive control. |
| `G-*` | Relevant to GU and composition claims, but destructive shuffle alone proves necessity, not correct counterfactual following. |
| `T*` | Essential, but currently removes normalization, proof DAGs, and executable semantics together, so it is not a clean single factor. |
| `R*` | Coherent and mandatory, provided it receives equally strong parsing, calibration, and selective prediction. |
| `X*` | Conditional. VL already uses prompt-text feedback; PS largely connects engine output to a deterministic renderer. Neither makes a privileged neural-integration claim by default. |
| `E0/Q0/Qsham` | Necessary, but require family-specific units: complete claims for VL, programs for PS, and trajectories/actions for GU. |

The `D` construction operates on retrieved bundles ([p3d-threat-factorial-controls.md:98](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md:98)), whereas VL and PS send formal queries/programs plus a store snapshot to the engine. THREAT needs an executable treatment-boundary matrix stating whether each control mutates host-visible retrieval, entity/schema linking, the formal request, the authoritative store, engine results, or some combination.

`T*` currently changes too many things at once: it removes kernel normalization, dependency/proof DAGs, executable semantics, and inference rules ([p3d-threat-factorial-controls.md:223](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md:223)). Split this into:

- Aligned typed storage without execution.
- A schema-neutral generic interpreter over the same explicit rules.
- A matched precomputed-closure/result store where appropriate.
- The separate executor factor.

For `G-*`, recomputing whether answers follow the transformed world is merely requested as a report ([p3d-threat-factorial-controls.md:213](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md:213)). It should be a gate for any structural-reasoning claim. Otherwise a model can “pass” because a shuffle creates conflicts or missing coverage and triggers abstention. Transformed worlds must remain licensed, conflict-valid, and coverage-matched, with recomputed targets.

`X*` should not be in every core conjunction. THREAT currently includes it in `J_core` ([p3d-threat-factorial-controls.md:384](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md:384)). It is mandatory only when the claim names native/internal integration. A legitimate text-delivered deterministic-executor capability should not be killed merely because text and structured delivery tie.

Finally, THREAT lacks a common feedback-information factor. `Qsham` controls generic selection, not whether typed diagnostics leak answer information. Add same-oracle constant feedback, information-matched sham feedback, attempt-indexed outcomes, entropy/exhaustion limits, and a pre-freeze engagement pilot. It also needs an explicit train-time factorial spine for GU and trained VL/PS variants.

## Add-capability discipline

On framing, the drafts agree with the crux. None actually asserts that the literature establishes a matched-resource efficiency win:

- H-PS explicitly calls itself add-capability and denies a literature-backed matched-resource win ([p3d-ps-architecture.md:33](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-ps-architecture.md:33)).
- H-GU explicitly adopts the add-capability result and separates correctness from efficiency framing ([p3d-gu-architecture.md:13](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-gu-architecture.md:13)).
- H-VL defers the framing and correctly says µs checking only removes one cost term ([p3d-vl-architecture.md:103](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-vl-architecture.md:103)).

That matches the source audits: execution-feedback wins add an executor ([lit-p3-parse.md:244](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-parse.md:244)); prover systems add exact execution/checking absent from the neural baseline ([lit-p3-ntp.md:374](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-ntp.md:374)); and rule systems show the same pattern ([lit-p3-rule.md:363](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-p3-rule.md:363)).

The residual laundering risks are attributional, not rhetorical:

- Engine acceptance can still mean validity rather than NL correctness.
- Retry lift can still be answer leakage or oracle filtering.
- GU training lift can be synthetic curriculum or clean trace data rather than runtime engine use.
- VL can claim a verifier loop where direct engine rendering is the actual capability.
- A `T*` or `R*` match would leave a generic typed-executor/tool capability, not kernel-specific semantics.

## Cross-design verdict and promotion order

The designs do not yet share one component stack. VL uses a whole-query comparison wrapper; PS uses the current terminal executor; GU assumes a future transition/proof service. Their result schemas, feedback bandwidth, and abstention ownership differ. They should share:

- One NLB admission and semantic-risk contract.
- One terminal engine result schema: answer/refusal plus provenance/licence.
- A separate optional step-transition extension for GU.
- One renderer policy and one calibration protocol.
- One low-bandwidth diagnostic policy.
- Architecture-specific features added only through explicit ablations.

All four are worth sending to Fable now as proposals. For actual preregistration after #57/framework unblock:

1. **H-PS first.** It is the only design whose core maps directly onto the current engine. Fix the stale a5 mechanism, same-result ambiguity, trace gating, diagnostic-content control, and `E0` operationalization.

2. **H-VL second, only after its identity is settled.** Run the model-free/direct-render dominance check and a non-vacuity pilot first. If the host-value layer adds nothing, merge its useful retry/calibration machinery into H-PS.

3. **H-GU only as an API/statement-supply prereg initially.** Do not preregister T1–T5 as executable arms until the transition engine and proof semantics exist.

4. **THREAT must be revised before it can govern any of them.** Add family-specific treatment-boundary manifests, counterfactual-following gates, feedback/leak controls, train-time factorials, and conditional rather than universal use of `X`.

No reviewed files were modified.