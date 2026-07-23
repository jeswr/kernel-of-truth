# Cross-vendor review (GPT-5.6 `gpt-5.6-sol`, xhigh) — S3 grounding-checker scoping (Rev1)

> Independent cross-vendor review of the S3 scoping doc (Rev1). Verdict NEEDS-REVISION;
> central finding = the design tests the constrained-decoding MECHANISM, not kernel-specific
> value (compiled admissible set erases provenance). All findings applied in Rev2 (arm M_N +
> PRECERT-S3-1 + C-MECH/C-KERN split). Committed for the record.
> Runner: poc/gpt56-review/run-review.sh (npx-pinned codex 0.144.1; global codex untouched).

---

Verdict: **NEEDS-REVISION**

The design can validly test whether hard, fact-conditioned decoding beats presenting the same facts as text. It cannot currently test whether the **kernel specifically** is load-bearing. That distinction is central, not semantic: the sampler consumes an admissible set, not the provenance or representation that produced it.

**Single most important correction:** split the thesis into:

1. **Mechanism claim:** a closed-world admissibility mask at the logits seam adds value over the same facts as text.
2. **Kernel-specific claim:** a mask compiled from the kernel outperforms the identical mechanism supplied by a matched non-kernel structured store.

Arm T addresses claim 1. No current arm addresses claim 2.

1. Kernel load-bearing versus substitutable

The empty-kernel argument in [§2.1](</home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/colibri-s3-grounding-checker-scoping.md:168>) proves only that the chosen mechanism needs a populated fact source. It does not prove that it needs this kernel.

At the compiler boundary, the causal chain is effectively:

`source → admissible set A(s,r,prefix) → token mask`

Once compiled, the sampler sees only `A`. A relational database, knowledge graph, JSON Schema with enums, ordinary ontology, or deterministic retrieval-backed allowlist could provide the same `A`. If a non-kernel source compiles to the same masks, its output distribution is identical by construction. Kernel provenance has been erased.

This is especially important because knull-v2 already established that an aligned non-kernel store can be equivalent to the kernel on a related checking seam ([interpretation](</home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/knull-v2-interpretation.md:21>)). Arm G is not the required comparator: it removes semantic constraints rather than replacing their source. Calling G “matched generic” therefore overstates what it controls.

Concrete fix: add `N`, a mask compiled through the identical compiler/checker from the strongest aligned non-kernel typed store or plain ontology, with matched coverage, admissibility-set size, bytes, authoring budget, and runtime accounting. Score `M_K − M_N` against gold independent of both stores. Pre-certify that the sources make different admissibility predictions; if they compile to identical sets, concede that sampler performance cannot identify kernel-specific value and narrow the claim to “structured-store admissibility is load-bearing.”

2. The priced falsifier

T is the correct binding control for the **mechanism-versus-text** claim. Prompt-side channel matching in [the arm table](</home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/colibri-s3-grounding-checker-scoping.md:301>) is substantially sound: M and T receive byte-identical facts, while only M gets the compiled mask.

But M−T bundles three effects:

- hard format enforcement;
- kernel-vocabulary restriction;
- record/axiom semantic restriction.

G helps separate generic format enforcement, but the “fraction of M−T recovered” rule is unstable when effects interact or M−T is small. A direct, margin-based `M > G` contrast is cleaner. For a kernel-specific result, `M_K > M_N` is also indispensable.

The kill wording also conflates “not banked” with “falsified.” If superiority does not fire, home status should indeed remain unbanked. But only registered equivalence or demonstrated harm licenses “the facts, not the mechanism, carry the value.” Otherwise the result is INCONCLUSIVE. The proposed TOST machinery recognizes this, but KILL-1 should use the same decision tree.

Concrete fix:

- Require the conjunction `M > T` and `M > G` for the semantic-mask claim.
- Require `M_K > M_N` for kernel-specific attribution.
- Distinguish PASS, licensed equivalence/harm, and INCONCLUSIVE.
- Define whether “3 points” is an observed-value floor plus a test against zero, or a test of `Δ > 3`; the current wording permits both readings.
- Match abstention availability, response grammar instructions, stopping rules, token budgets, seed handling, and arm-blind extraction/scoring.

3. Primary endpoint

Honesty-scored correctness is the right primary in principle. The prohibition on groundedness or well-formedness as P-strict primaries is correct: those are enforced properties, not evidence of useful correctness. Under P-consistent, groundedness can remain secondary.

However, the proposed endpoint omits the programme’s mandatory honesty-score safeguards. KOT-HON/1 requires λ to be pinned before outcomes, default λ=3 absent a declared harm ratio, S₂/S₅ sensitivity reporting, the full outcome vector, and an answer-rate co-floor or risk–coverage curve ([guard](</home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/honesty-first-scoring.md:198>)). Allowing the designer to choose −2…−5 without that discipline permits endpoint tuning and abstention gaming.

The endpoint is not automatically tautological, but the current non-degeneracy test is insufficient. “At least two admissible objects” does not establish a real correctness choice:

- both objects may be valid answers;
- one may be the only question-relevant or remotely plausible answer;
- the mask may force the answer before the nominal decision slot;
- engine-derived gold guarantees that gold is represented in the treatment’s own closure.

The last issue repeats the programme’s known oracle-favourable construction: a store checked against gold derived from itself measures answer-key adherence, not independent correctness.

Concrete fix: require, per item, at least one admissible gold answer and at least one admissible but independently certified incorrect answer, with all alternative valid answers included in the gold set. Add plausibility/token-length controls and verify that no earlier prefix forces gold. Use gold-label-independent adjudication where claiming correctness; otherwise rename the endpoint “closed-world store conformance.” Add the KOT-HON/1 coverage guard and pin λ before the pilot.

4. Deranged control and non-degeneracy

D is useful, but its current interpretation is too strong.

Under P-strict, if D is constructed to exclude gold, collapse is mechanically forced. That makes D an implementation/manipulation check: it verifies that the mask actually controls decoding and that scoring is not leaking around it. It does not independently demonstrate grounding or kernel specificity.

Under P-consistent, collapse does not follow. A deranged constraint set may still admit the gold and most unknown assertions. Failure to collapse could therefore mean insufficient derangement exposure, not an invalid primary instrument.

“Objects permuted within relation” and dose-exact counts are also insufficient. The permutation should preserve satisfiability, domain/range types, functionality/cardinality structure, inverse relations, closure size, per-item admissible-set cardinality, and approximate token-trie shape. Axiom objects cannot all be deranged under one undifferentiated rule.

Concrete fix: make D policy-specific and separate two gates:

- **First-stage derangement gate:** quantify mask disagreement, gold-exclusion or contradiction-flip rate, nonempty completability, cardinality matching, closure size, and consistency.
- **Implementation gate:** conditional on a certified first stage, verify that outputs obey D.

Use multiple seeded derangements. Do not require generic “D collapses” under P-consistent. A failed D first stage invalidates kernel-content attribution, but need not erase a separately valid generic constrained-decoding result.

5. Power and feasibility

The item-level power sketch is not defensible for the stated primary. The endpoint is paired asymmetric utility with abstentions, not paired binary correctness, so a McNemar discordance calculation is not the applicable variance model.

More importantly, the programme’s own F1-K result contradicts the implied 3-point power story. Its measured geometry needed `C=96, n=1,573` to obtain approximately 80% per-rung power at **4.09 points**; 3 points remained only the licensing floor ([power table](</home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/f1k-geometry-freeze-2026-07-15.md:33>)). A true effect exactly at an observed 3-point floor has approximately a 50% chance of clearing that floor even before other decision conditions.

“Power at item level with concept as a variance component” does not remove the cluster-count limitation. A random-effects assumption may model dependence, but additional items cannot manufacture independent concepts.

Concrete fix: use pilot-estimated paired utility differences and simulate the complete licensing rule under the actual concept count, unequal `m_c`, abstention transitions, policy multiplicity, and cluster covariance. Freeze a concept-level sign-flip/bootstrap or a justified hierarchical model. Power superiority and equivalence separately; the latter may be more demanding. Report the 80%-powered effect, not n alone.

The `$30–80` figure is plausible only as a provisional inference-compute budget. A current GCP `g2-standard-4` L4 VM is about `$0.707/hour`, so that budget buys roughly 42–113 GPU-hours before storage and operational overhead ([Google Cloud pricing](https://cloud.google.com/products/compute/pricing/accelerator-optimized)). But the current estimate omits long-prompt prefill, added policy/generic-store arms, repeated derangements or seeds, audits, and implementation time. Ordinary APIs also may not expose the required dynamic logits hook.

Concrete fix: call `$30–80` a lower-bound planning estimate, measure end-to-end `$ / paired item` during bring-up, enumerate the final arm/repetition count, and freeze a ceiling from that measurement.

6. P-strict versus P-consistent

Both semantics are coherent only within their stated limits:

- P-strict guarantees derivability from a pinned closed world, not factual truth. It can reject true but absent facts and risks turning evaluation into answer-key enforcement.
- P-consistent guarantees only “no detected violation under this finite axiom set.” It does not guarantee grounding and may admit arbitrary unknown claims.

Running both is useful, but not as symmetric confirmatory sub-arms where either win can bank the general seam. They target different error classes, require different items, and create multiplicity.

Concrete fix: make P-strict the confirmatory primary for the narrow closed-world mechanism claim, after fixing independent gold and effective non-degeneracy. Treat P-consistent/T-B as a separately powered secondary deployment study labelled “contradiction veto,” with its own exposure gate and D construction. Alternatively choose P-consistent as primary if deployment usefulness is the real question, but then withdraw grounding/correctness guarantees. If both remain confirmatory, specify multiplicity control and require a declared conjunction or hierarchy before outcomes.

7. Epistemic hygiene

The two explicit EXTRAPOLATION passages are properly marked and do not appear to serve as downstream premises.

Several other load-bearing claims are missing or misusing tags:

- The central “kernel is the program” conclusion in §2.1 is an untagged design interpretation—and currently unsupported as kernel-specific.
- “Can hit all four by construction” in §2.3 is both untagged and too strong. Deterministic scoring does not validate an answer key, item semantics, or source fidelity.
- “Microseconds and cannot be the bottleneck” is an unmeasured engineering forecast.
- The power and cost numbers are forecasts and should be EXTRAPOLATION, not merely STIPULATED estimates.
- “The scientific result is host-independent” is an untagged extrapolation. Mechanism portability does not imply treatment-effect portability; model compliance, tokenizer, and baseline strength are effect modifiers.

Concrete fix: retag these claims, replace “validated by construction” with explicit validation gates, and distinguish portable implementation from cross-host effect generalization. The self-check’s claim that every load-bearing statement is tagged should currently read FAIL.

Overall, the design contains a good logits-versus-text experiment and a sensible insistence on non-tautological correctness. Its present headline attribution is nevertheless one causal layer too strong: it tests the value of **structured closed-world constrained decoding**, not the distinctive value of the kernel that supplies the constraints.