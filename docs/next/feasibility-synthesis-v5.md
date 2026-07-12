# Cross-experiment feasibility synthesis v5 — after CASC-0′, the RULES-1 certificate, and the ontology build

## Status, scope, and tags

- **Status:** synthesis update, not an audit. This document supersedes `docs/next/feasibility-synthesis-v4.md` as the standing cross-experiment picture. It changes no frozen record, verdict, audit, result log, or registered assumption.
- **Scope:** both programme theses—**CORRECTNESS** and **EFFICIENCY**—after the CASC-0′ result, the registered RULES-1 CPU certificate, the UFO-in-RDF-1.2 expressibility work, and construction of the ontology-import go/no-go.
- **Central discipline:** neither thesis receives a feasibility conclusion here. Registered verdicts, certificate results, proxy evidence, architecture verdicts, shipped engineering artifacts, pending campaigns, and synthesis-level interpretations remain separate.
- **Riders:** every f2b/DECONF claim retains its self-authored, kernel-covered, oracle-addressed and scale-bounded riders; every CASC-0′ claim retains its self-authored `d-casc0`, engine-derived-gold, constrained-answer, stock-checkpoint and static-prompting rider; every g2/g2-import gold-dependent claim remains proxy-only until human reconciliation.

Epistemic tags used below:

- **[MEASURED, VERDICT-GRADE]** — registered observation supporting a mechanical verdict.
- **[MEASURED-CERTIFICATE, PASSED PRECONDITION]** — deterministic RULES-1 CPU result whose registered certificate gate passed; not the ungraded GPU host result and not a programme verdict.
- **[PROVISIONAL-ON-LLM-PROXY]** — measured against proxy labels whose direction relative to reconciled human judgment remains unproven.
- **[ARCHITECTURE-VERDICT]** — scoped representational or engineering conclusion, not evidence for either programme thesis.
- **[ENGINEERING-SHIPPED]** — an implementation, experiment package, or draft PR exists; this does not imply empirical success.
- **[STIPULATED]** — frozen scope, registered rule, or adopted design decision.
- **[DERIVED]** — direct application of an existing decision rule to measured facts.
- **[INTERPRETIVE]** — this synthesis’s composition of evidence.
- **[IN-FLIGHT, UNGRADED]** — execution has not yet produced a licensed grade.
- **[BUILT, NOT RUN]** — the instrument and materials exist, but no non-mock experimental result has landed.
- **[EXTRAPOLATION]** — direction-only and never a premise.

---

## 0. Governing sentence

> **LOAD-BEARING:** The programme has two different correctness-direction positives: an audit-confirmed authored-content lift through an item-aligned acceptance interface, and a passed CPU certificate showing that a deterministic rules engine derives correct entailed decisions that stated lookup cannot reproduce. The first has no measured kernel-specific runtime residue; the second establishes rules-machinery non-inertness only because its host-lift campaign is ungraded and its `knull` rules-source ablation remains pending. CASC-0′ adds adverse descriptive evidence for static prompted naturalisation but no valid M2 hypothesis verdict. The imported-soft-typing route is now executable but untested. CORRECTNESS and EFFICIENCY therefore both remain **INCONCLUSIVE-PENDING**. **[INTERPRETIVE composition of measured constituents]** [STIPULATED: ASM-1380]

Three value locations must remain distinct:

1. **Authored content:** f2b-transfer and DECONF-B show that an aligned, answer-bearing artifact can improve a small host on externally adjudicated gold. **[MEASURED, VERDICT-GRADE; f2b/DECONF riders]**
2. **Rules-engine computation:** RULES-1 shows that genuine closure can add correct entailed decisions beyond stated lookup. **[MEASURED-CERTIFICATE, PASSED PRECONDITION; gold-parsed-world and closed-inventory riders]**
3. **Ontology and representation infrastructure:** UFO-SN3 and the g2-import build show that a bounded ontology-backed rules direction is expressible and implementable. They do not yet show that imported typing is sound, useful to a host, or efficient. **[ARCHITECTURE-VERDICT + ENGINEERING-SHIPPED]**

Conflating these would turn an authored-key result into a kernel-runtime claim, a CPU certificate into host lift, or an implementation artifact into empirical success.

---

## 1. What changed after v4

### 1.1 CASC-0′ landed as INSTRUMENT-INVALID

**[MEASURED, VERDICT-GRADE]** `registry/verdicts/casc-0.json` records **INSTRUMENT-INVALID**. Engagement and headroom passed, but the TTC purchased-compute deflator missed its registered relative-FLOPs band: measured mismatch **0.3537**, above the **0.30** threshold, at capped integer `N = 9`. Size separation also failed, leaving the non-inferiority co-primary unevaluable. **CASC rider.**

**[MEASURED]** The observed static verifier-off interactions contained no positive M2 sign:

- gloss interaction: **+0.0033**, one-sided 95% BCa LCB **−0.0467**, Holm-family \(p=0.4827\);
- plain interaction: **−0.0333**, LCB **−0.1067**, \(p=0.7911\);
- `primary_reject=false`;
- `tost_m2_null=false`.

**[DERIVED]** The licensed sentence is:

> At the static prompted CASC-0′ scope, no positive M2 sign appears in the observed raw interactions, but TTC mismatch prevents a valid overall adjudication and the registered NULL test did not pass. **[MEASURED + DERIVED; CASC rider]**

It is therefore incorrect to report either “M2 works” or “M2 is null.”

**[MEASURED]** Kernel-style gloss and plain typed dialect were TOST-equivalent at R2 with the verifier on: difference **+0.0044**, interval **[−0.0222,+0.0311]** inside the registered ±0.05 band. The non-fatal K3′ attribution rule therefore removes kernel-content attribution at this static-medium scope. **CASC rider.**

**[INTERPRETIVE]** The TTC miss is re-runnable rather than evidence of fundamental cost-matching impossibility. The registered band was marked DRAFT and the deflator was quantised by capped integer majority-vote counts. A new preregistration could use finer stochastic allocation or a justified wider band.

**[STIPULATED]** Repairing TTC matching alone would not reverse the present raw estimates, cure the failed separation gate, or retroactively convert this run into PASS or NULL. A rerun is warranted only if clean adjudication of the static M2 claim remains decision-critical.

### 1.2 RULES-1’s CPU certificate is now a passed correctness-direction result

**[MEASURED-CERTIFICATE, PASSED PRECONDITION]** The registered CPU rerun reports:

- stated-cell \(C_{\text{dec}} = 1.0\), **1,716/1,716**;
- entailed-cell \(C_{\text{dec}} = 0.0\), **0/3,680** reproducible by the stated-fact projection;
- third-party CLUTRR correctness **858/858**, Wilson-LB95 **0.9955**, above the 0.98 bar;
- held-out world-v0 E1 correctness **248/248**, Wilson-LB95 **0.9847**, with kernel-authored gold disclosed;
- insufficient-premise refusal **100/100**;
- definition-removal, targeted-mutation, coherent label-swap and meaning-preserving no-op counterfactuals behaved as predicted;
- deterministic double-run payload hashes matched;
- SPARQ and the differential twin agreed on closure for **1,207/1,207** conformance cases;
- local CPU execution cost was below two seconds and approximately $0.

The exact claim cap is:

> The RULES-1 rules engine is non-inert on the measured entailed-cell closure and is exact against the tested third-party CLUTRR gold. **[MEASURED-CERTIFICATE, PASSED PRECONDITION]**

This is a real correctness-direction positive. It establishes that the engine computes answer-relevant consequences that flat lookup over stated facts cannot reproduce.

It does **not** establish:

- host-model lift—the GPU A3-versus-A1 endpoint is **[IN-FLIGHT, UNGRADED]**;
- any EFFICIENCY-thesis positive;
- kernel-specific value—the phase-2 `knull` rules-source ablation remains pending;
- that NSM/kernel definitions are uniquely required to author the rules;
- natural-input reach—the worlds are gold-parsed;
- generality outside the closed kinship/world inventory;
- small-model parity with the 1.7B host;
- end-to-end cost advantage;
- a programme feasibility verdict.

**[DERIVED]** “RULES-1 PASS” must therefore be read as “the CPU certificate gate passed,” not “the complete host-level RULES-1 experiment passed.” The host-lift campaign has not yet been graded.

### 1.3 UFO-in-RDF-1.2 is YES-WITH-EXTENSION

**[ARCHITECTURE-VERDICT]** `docs/next/arch/ufo-rdf12-expressibility.md` gives the verdict **YES-WITH-EXTENSION**:

- all surveyed UFO constructs are representable using RDF resources, RDF 1.2 quoted triples/reifiers, N3 formulae, OWL vocabulary and SHACL-style validation;
- bare RDF/OWL-RL does not supply the required possible-world, satisfaction, identity, causal, intentional or deontic semantics;
- the required extension is **UFO-SN3**, a finite, situation-scoped, function-free and range-restricted N3/Datalog profile over OWL-RL;
- positive materialisation over finite terms terminates; fixed-ruleset data complexity is polynomial;
- finite closed-scope validation is decidable under the declared restrictions.

**[ENGINEERING-SHIPPED]** A bounded SPARQ reference implementation and draft-PR artifact have shipped, covering representative UFO-A, UFO-B and UFO-C constructs through explicit proposition nodes, supplied worlds and range-restricted N3 rules.

**[STIPULATED RIDER]** UFO-SN3 is an executable finite-world profile, not a complete decision procedure for reference UFO. It does not decide unrestricted quantified modal or deontic validity, arbitrary executable identity criteria, unrestricted existential mereology, general counterfactual causation, or defeasible normative conflict. Its v1 implementation also does not claim native RDF-star quoted-triple matching or negation-as-failure missing-witness validation.

**[DERIVED]** The result removes “RDF cannot represent statements about statements” as an architectural blocker and demonstrates an implementable decidable profile. It supplies no measured evidence that the imported ontology improves ordinary-meaning soundness, host accuracy, natural-input reach, or economic efficiency.

### 1.4 The ontology-import pivot is built but unrun

**[ENGINEERING-SHIPPED]** The ontology-import direction now has:

- pinned BFO, SUMO and FrameNet sources;
- `kot-ont-bridge/1` and soft-type candidate artifacts;
- fixed A0–A3 materials over the same 84 g2 slots;
- non-vacuity and forbidden-hard-effect controls;
- a runner, analysis path, probes and mock decision cases;
- a `g2-import` registration object.

**[BUILT, NOT RUN]** No non-mock g2-import result has landed. The registration remains DRAFT, so no GO, NO-GO, soundness improvement, source-attribution or adoption claim is licensed.

The planned arms are:

- **A0:** frozen Π baseline, **33/84 = 0.3929**;
- **A1:** BFO-only breadth/vacuity control;
- **A2:** BFO plus SUMO soft typing;
- **A3:** BFO plus SUMO plus FrameNet soft typing.

All imported cross-layer statements are non-binding preferences. Missing, underdetermined, invalid, vacuous or abstained slots score zero. A3 must reach at least **34/84**, retain at least **67/84** non-vacuous outputs and at least **34/42** non-vacuous R3 outputs, while satisfying the proxy-instrument gates. **[STIPULATED design; PROVISIONAL-ON-LLM-PROXY]**

**[STIPULATED]** Even a proxy GO would license only bounded promotion of an advisory rank/lint/explain shard. Permanent scientific adoption remains subject to a later two-human independent panel and blind reconciliation.

---

## 2. The cross-experiment through-line

### 2.1 What remains measured in authored content

**[MEASURED, VERDICT-GRADE]** f2b-transfer established:

- external endorsement **320/333 = 0.9610**;
- external-gold lift of 135M plus aligned verify-retry over 135M alone: **+0.2507**;
- shuffled-content and gloss-self-verification controls passed;
- all instrument gates valid;
- `noninferiority_vs_r3=false`.

**[MEASURED, VERDICT-GRADE]** DECONF-B located the same mechanism more precisely:

- aligned-store contrast \(\Delta_{\text{align}} = +0.2697\);
- aligned-store bridge lift over model alone **+0.285**, LB95 **+0.255**;
- GS-A and kernel-arm accuracy both **0.678**;
- GS-A–kernel identity fraction **1.0**;
- pinned BM25 retrieval/self-consistency alternatives remained near **0.41**.

The exact surviving account is:

> A kernel-authored, item-aligned answer key is externally useful to a 135M host through a thin deterministic verify-retry interface; no kernel-specific runtime increment is measured at that seam. **[MEASURED + DERIVED; f2b/DECONF riders]**

The kernel is demonstrated as one author of useful content. Independent authoring equivalence, kernel necessity, mint cost and maintenance economics remain unresolved.

### 2.2 What is emerging in the rules-engine/ontology direction

**[MEASURED-CERTIFICATE, PASSED PRECONDITION]** RULES-1 shows that deterministic closure can add correct decisions beyond stored lookup.

**[MEASURED + PROVISIONAL-ON-LLM-PROXY]** g2 shows that the existing hand-authored hard type readout has an adverse ordinary-meaning signal:

- primary precision **33/84 = 0.3929**;
- pair-concordant **24/84 = 0.2857**;
- pair-union **38/84 = 0.4524**;
- pair stability \(\kappa = 0.6430\);
- mechanical verdict **INSTRUMENT-INVALID** because **84 < 500**.

The deterministic Π machinery worked; the adverse signal concerns the ordinary-meaning soundness of its universally quantified, mutually disjoint type claims. **[MEASURED + INTERPRETIVE diagnosis]**

**[ARCHITECTURE-VERDICT]** UFO-SN3 shows that a richer, bounded, situation-aware ontology layer is representable and executable without pretending to decide unrestricted modal UFO.

**[BUILT, NOT RUN]** g2-import turns the proposed repair into a falsifiable experiment: preserve native authored NSM meaning, import a typed scaffold, route uncertain argument typing as soft preference, and score the result against the same 84-slot ordinary-meaning estimand.

The coherent direction is therefore:

> preserve authored meaning and warrants; move useful answer-bearing content into aligned stores; express worlds and axioms explicitly; use deterministic proof-carrying inference for genuine entailment; import ontology-backed typing only as provenance-bearing soft preference unless separately endorsed as hard; refuse outside proved scope. **[INTERPRETIVE + STIPULATED DESIGN]**

This is an emerging architecture, not an established feasibility result.

### 2.3 What CASC-0′ removes from the through-line

**[MEASURED + DERIVED]** CASC-0′ supplies no positive support for the claim that static kernel-style or plain structured prompting disproportionately helps the smaller stock reasoner. It also finds kernel-style gloss equivalent to the plain typed dialect at its attribution endpoint.

**[INTERPRETIVE]** This coheres with the authored-content account: measured value currently appears in correct item-aligned content and, separately, in actual rule closure—not in checker-side kernel structure or static prompted naturalisation.

**[STIPULATED]** Because CASC-0′ is instrument-invalid, this coherence is descriptive. It cannot be upgraded into a clean M2 NULL or a general rejection of learned naturalisation, tuning, other renderers, other scales, or real-input front ends.

---

## 3. CORRECTNESS thesis

> **STATE, not verdict: INCONCLUSIVE-PENDING.** CORRECTNESS now has measured positives for externally useful authored content and for non-inert deterministic entailment machinery. It still lacks kernel-specific attribution for the rules source, a graded host-lift result, human-valid typing reconciliation, natural-input success, and broad coverage.

### 3.1 MEASURED-positive

- Authored-content endorsement: **320/333 = 0.9610** on the covered rendered slice. **[MEASURED, VERDICT-GRADE; f2b rider]**
- Authored-content end-task lift: **+0.2507** over the 135M host on independently adjudicated gold. **[MEASURED, VERDICT-GRADE; f2b rider]**
- Alignment-specific bridge: aligned verify-retry **0.678** versus model alone **0.393** and registered lexical/self-consistency alternatives near **0.41**. **[MEASURED, VERDICT-GRADE; DECONF rider]**
- Rules-engine non-inertness: entailed-cell \(C_{\text{dec}}=0.0\) while stated-cell \(C_{\text{dec}}=1.0\). **[MEASURED-CERTIFICATE, PASSED PRECONDITION]**
- Third-party rule soundness: **858/858** against CLUTRR gold, Wilson-LB95 **0.9955**. **[MEASURED-CERTIFICATE, PASSED PRECONDITION]**
- Counterfactual and fail-closed behaviour: removal, mutation, label swap, no-op and insufficient-premise controls behaved as registered. **[MEASURED-CERTIFICATE, PASSED PRECONDITION]**

### 3.2 Architecture-enabling, but not thesis-positive

- UFO-in-RDF-1.2: **YES-WITH-EXTENSION** through the bounded UFO-SN3 profile. **[ARCHITECTURE-VERDICT]**
- UFO-SN3 reference implementation and draft PR shipped. **[ENGINEERING-SHIPPED]**
- Ontology-backed soft-typing experiment package built. **[BUILT, NOT RUN]**

These reduce implementation uncertainty. They do not show that the ontology mappings are correct, that soft typing beats Π, or that any host benefits.

### 3.3 Measured-deflationary or adverse

- No F2 kernel-runtime residue: DECONF-A1 \(C_{\text{dec}}=1.0\); DECONF-B GS-A–kernel identity **1.0**. **[MEASURED]**
- No static M2 sign in CASC-0′’s raw interactions, with kernel-style gloss equivalent to plain typed dialect at R2. **[MEASURED; CASC rider]**
- Natural-input boundaries remain failed or unresolved at their standing scopes. **[MEASURED within source envelopes; conjunction INTERPRETIVE]**
- Coverage remains **0.3542 at molecules-v0** on one incomplete kernel-v0 instance. **[MEASURED]**
- g2’s proxy signal remains strongly adverse to hard Π typing. **[MEASURED + PROVISIONAL-ON-LLM-PROXY]**

### 3.4 What remains INCONCLUSIVE-PENDING

- Whether RULES-1 derivations improve host accuracy: GPU result ungraded.
- Whether the rule source has kernel-specific value: `knull` ablation pending.
- Whether imported soft typing improves ordinary-meaning soundness: g2-import unrun.
- Whether proxy conclusions survive human reconciliation.
- Whether independently authored non-kernel content matches the useful kernel-authored key.
- Whether a natural-input front end can populate the world/rules layer safely.
- Whether coverage can expand without sacrificing endorsement, proof, or honest refusal.
- Whether the closed rule inventory generalises beyond the tested kinship/world cells.

### 3.5 Exact bearing of RULES-1

RULES-1 changes CORRECTNESS from “useful authored lookup only” to “useful authored lookup plus demonstrated genuine entailment.”

It does not yet connect that entailment to a model-level end task. Until the GPU grade lands, the following stronger statements remain unlicensed:

- “the host benefits from the engine”;
- “the kernel’s rules are load-bearing”;
- “the engine enables a smaller model”;
- “RULES-1 establishes programme correctness.”

The licensed statement remains:

> Correct, proof-carrying rules-engine computation beyond stated lookup exists at the measured certificate scope. **[MEASURED-CERTIFICATE, PASSED PRECONDITION]**

---

## 4. EFFICIENCY thesis

> **STATE, not verdict: INCONCLUSIVE-PENDING.** Aligned verifier offload is measured-positive. Model replacement, rules-assisted host lift, static-medium shrinkage and end-to-end economic advantage remain unestablished.

### 4.1 MEASURED-positive mechanism

- A 135M host gains **+0.2507** from aligned verify-retry over itself on external gold. **[MEASURED, VERDICT-GRADE; f2b rider]**
- DECONF-B reproduces an aligned-store bridge lift of **+0.285**, LB95 **+0.255**. **[MEASURED, VERDICT-GRADE; DECONF rider]**
- The aligned store beats the registered BM25/self-consistency alternatives at matched retry budget. **[MEASURED]**

The licensed efficiency mechanism is:

> A small host can convert retries into external-gold accuracy when supplied with a cheap deterministic acceptance interface over an item-aligned authored key. **[MEASURED at the registered scopes]**

### 4.2 Not established or adverse

- `noninferiority_vs_r3=false`: 135M plus verifier was not shown to match 1.7B. **[MEASURED]**
- No kernel-specific runtime increment is measured at the F2 seam. **[MEASURED]**
- CASC-0′ contains no positive M2 interaction sign, but its TTC gate failure prevents either a clean NULL or a valid cost-matched M2 verdict. **[MEASURED + DERIVED; CASC rider]**
- Natural-input, renderer, routing, mint, maintenance and coverage-adjusted costs remain outside the positive ledger.

### 4.3 What RULES-1 contributes—and does not contribute

**[MEASURED]** The rules computation is locally cheap: the CPU certificate completed below two seconds at approximately $0.

That is an enabling cost fact, not an EFFICIENCY-thesis result. The engine may be cheap and still add no host accuracy.

Until the GPU grade lands, RULES-1 establishes none of:

- positive host lift;
- efficient conversion of retries into correct final answers;
- small-model parity or non-inferiority;
- reduced total model or system cost;
- favourable authoring economics.

Accordingly, RULES-1 remains a correctness-direction positive only. **[DERIVED]**

### 4.4 Current efficiency shape

**[INTERPRETIVE]** The evidence supports **functional compression** more strongly than **model replacement**:

- authored answer-bearing content can be moved into a deterministic acceptance store;
- a rules engine can cheaply compute additional closure;
- neither result yet shows that the combined system replaces a larger model or reduces lifecycle cost.

CASC-0′ weakens the static prompted-medium route descriptively but does not close it cleanly. The RULES-1 GPU grade is now the nearest direct resolver of whether genuine entailment produces model-level value.

---

## 5. Current cross-experiment picture

### 5.1 Established at scope

- Kernel-authored content can be externally endorsed and useful. **[DERIVED from MEASURED]**
- Its F2 runtime effect is carried by item-aligned answer-bearing content. **[DERIVED from MEASURED]**
- A projected generic aligned store reproduces the kernel arm exactly on the DECONF-B grid. **[MEASURED]**
- A deterministic rules engine can correctly derive decisions absent from stated lookup. **[MEASURED-CERTIFICATE, PASSED PRECONDITION]**
- Static prompted CASC-0′ interactions contain no positive M2 sign. **[MEASURED; CASC rider]**
- The current hard Π typing is not validated and has a strongly adverse proxy-soundness signal. **[MEASURED + PROVISIONAL-ON-LLM-PROXY]**
- A bounded decidable UFO-SN3 execution profile is architecturally viable and has a reference implementation artifact. **[ARCHITECTURE-VERDICT + ENGINEERING-SHIPPED]**

### 5.2 Not established

- That the kernel is uniquely capable of authoring the useful answer key.
- That kernel/NSM-authored rules outperform `knull` or imported controls.
- That RULES-1 raises host accuracy.
- That imported soft typing improves g2 soundness.
- That proxy results agree directionally with reconciled human gold.
- That structured media permit stock-model shrinkage.
- That either architecture crosses natural-input boundaries.
- That either architecture covers enough real workloads.
- That either architecture is efficient after authoring, routing, retries and maintenance are charged.

### 5.3 Neutral synthesis

**[INTERPRETIVE]** The evidence no longer supports treating the programme as one monolithic kernel mechanism. It supports a modular investigation:

```text
authored meaning and warrants
        ↓
aligned answer-bearing content + explicit worlds
        ↓
deterministic acceptance and proof-carrying inference
        ↓
soft imported typing for ranking/lint where ordinary meaning is defeasible
        ↓
fail-closed host integration
```

The measured value currently resides in authored content and rules-engine computation. Kernel-specific runtime structure and static prompted naturalisation have no positive measured residue at their tested seams. Whether kernel-specific authoring remains necessary is still an experimental question.

---

## 6. Remaining critical path

### 6.1 Immediate evidence gates

1. **Grade the RULES-1 host-lift campaign.**  
   The A3-versus-A1 GPU endpoint must report against third-party CLUTRR gold, with shuffled-rule recovery and extraction/instrument gates intact. Until then, engine non-inertness does not become host usefulness. **[IN-FLIGHT, UNGRADED]**

2. **Run g2-import.**  
   Freeze the built A0–A3 package and obtain a real non-mock outcome. A proxy GO must beat **33/84**, clear non-vacuity and instrument gates, and remain restricted to advisory soft typing. **[BUILT, NOT RUN; PROVISIONAL-ON-LLM-PROXY]**

3. **Complete the human-gold reconciliations.**  
   The original g2 84-item panel remains the authority for HS2 and Π demotion. If g2-import produces a GO-shaped proxy result, its later two-human independent panel must govern permanent scientific adoption. Proxy labels must remain quarantined from those annotators. **[STIPULATED authority rule]**

4. **Run the `knull` rules-source ablation after the host endpoint warrants it.**  
   A positive host result without this comparison establishes rules-assisted value, not kernel-specific value. **[PENDING ATTRIBUTION]**

### 6.2 Thesis-grade requirements beyond the immediate gates

For a defensible **CORRECTNESS** verdict, the programme still needs:

- graded host benefit from entailed facts;
- human-valid typing soundness;
- rules-source/content attribution;
- a natural-input path with retention and dangerous-error controls;
- coverage growth with endorsement and refusal discipline.

For a defensible **EFFICIENCY** verdict, it additionally needs:

- a measured accuracy–cost comparison against the larger host;
- mint, review, versioning and ontology-alignment costs;
- routing, retry, latency and maintenance costs;
- coverage-adjusted system value;
- either a cleanly rerun M2 adjudication if static naturalisation remains load-bearing, or an explicit decision to retire that route.

**[INTERPRETIVE]** CASC-0′ does not automatically enter the immediate rerun queue. Its rerun becomes critical only if the static M2 claim remains necessary to the intended efficiency thesis.

---

## 7. Bottom line

**LOAD-BEARING:** CORRECTNESS remains **INCONCLUSIVE-PENDING**. It has a verdict-grade authored-content positive and a passed machinery-non-inertness certificate. It does not yet have graded rules-assisted host lift, kernel-specific rules attribution, human-valid repaired typing, natural-input success, or broad coverage. **[DERIVED state summary]** [STIPULATED: ASM-1380]

**LOAD-BEARING:** EFFICIENCY remains **INCONCLUSIVE-PENDING**. Aligned verifier offload is measured-positive, but small-model parity is not established; RULES-1 is not yet an efficiency positive; CASC-0′ supplies no valid M2 verdict; and lifecycle economics remain unpriced. **[DERIVED state summary]** [STIPULATED: ASM-1380]

**LOAD-BEARING:** UFO-SN3 and the ontology-import build make the architecture direction more concrete, not more proven. The next evidence events are the RULES-1 host grade, the g2-import result, and the human-gold reconciliations. No feasibility conclusion beyond these scoped statements is licensed. [STIPULATED: ASM-1383]

---

## Epistemic register

- **MEASURED, verdict-grade:** f2b-transfer PASS and audit confirmation; external lift +0.2507; endorsement 320/333; noninferiority false; DECONF-B PASS and audit confirmation; \(\Delta_{\text{align}}=+0.2697\); bridge lift +0.285; GS-A–kernel identity 1.0.
- **MEASURED-CERTIFICATE, PASSED PRECONDITION:** RULES-1 stated \(C_{\text{dec}}=1.0\), entailed \(C_{\text{dec}}=0.0\), CLUTRR 858/858, refusal/counterfactual/determinism gates, and SPARQ–twin agreement 1,207/1,207.
- **IN-FLIGHT, UNGRADED:** RULES-1 GPU host-lift campaign; no host or efficiency claim inferred.
- **MEASURED INSTRUMENT-INVALID:** CASC-0′ TTC mismatch and failed separation; raw no-positive-M2 interactions; no clean NULL; re-runnable design issue.
- **MEASURED INSTRUMENT-INVALID + PROVISIONAL-ON-LLM-PROXY:** g2’s 84-item result, adverse soundness bracket and stable proxy pair.
- **ARCHITECTURE-VERDICT:** UFO-in-RDF-1.2 YES-WITH-EXTENSION and bounded decidability of the declared UFO-SN3 profile.
- **ENGINEERING-SHIPPED:** UFO-SN3 reference implementation/draft PR and the ontology-import experiment package.
- **BUILT, NOT RUN:** g2-import; no empirical import verdict.
- **INTERPRETIVE:** the authored-content/rules-engine distinction, functional-compression reading and modular through-line.
- **EXTRAPOLATION:** any expectation that imported typing will improve g2, that RULES-1 will lift the host, or that the architecture will cross natural-input and economic boundaries.

---

## Proposed assumptions for coordinator registration

```json
[
  {
    "id": "PROPOSED-ASM-1380",
    "tag": "STIPULATED",
    "claim": "Feasibility-synthesis-v5 thesis state: CORRECTNESS and EFFICIENCY both remain INCONCLUSIVE-PENDING. The registered f2b-transfer and DECONF-B positives establish externally useful aligned authored content at their scoped seams; the passed RULES-1 CPU certificate establishes rules-engine machinery non-inertness only. No programme feasibility conclusion follows.",
    "backing_ref": "docs/next/feasibility-synthesis-v5.md; registry/verdicts/deconf-b.json; registry/verdicts/f2b-transfer.json; poc/rules-1/RESULT.md",
    "rationale": "Records the post-v4 cross-experiment state without converting mechanism or certificate results into thesis verdicts.",
    "load_bearing": true,
    "status": "open",
    "owner": "synthesis-agent",
    "date": "2026-07-12",
    "notes": "Every use carries the source experiments' coverage, self-authorship, addressing, scale, input and gold-provenance riders."
  },
  {
    "id": "PROPOSED-ASM-1381",
    "tag": "STIPULATED",
    "claim": "RULES-1 claim cap after the registered CPU rerun: stated-cell C_dec=1.0, entailed-cell C_dec=0.0, CLUTRR 858/858 with Wilson-LB95 0.9955, and the passed counterfactual/conformance gates establish correctness-direction machinery non-inertness. They do not establish host-model lift, efficiency, natural-input reach, scale transfer or kernel-specific value. The GPU host campaign is ungraded and kernel-specific attribution remains pending the phase-2 knull rules-source ablation.",
    "backing_ref": "poc/rules-1/RESULT.md; registry/experiments/rules-1.json",
    "rationale": "Prevents the passed certificate precondition from being reported as a pass of the ungraded host-level experiment.",
    "load_bearing": true,
    "status": "open",
    "owner": "synthesis-agent",
    "date": "2026-07-12",
    "notes": "The certificate is a real measurement; 'RULES-1 PASS' must name the CPU certificate rather than imply a complete programme verdict."
  },
  {
    "id": "PROPOSED-ASM-1382",
    "tag": "STIPULATED",
    "claim": "CASC-0-prime reading: the registered verdict is INSTRUMENT-INVALID because the TTC purchased-compute mismatch 0.3537 exceeded the frozen 0.30 band; size separation also failed. The observed gloss and plain interactions contain no positive M2 sign, but tost_m2_null=false and no overall M2 hypothesis verdict is licensed. Kernel-style gloss is equivalent to plain typed dialect at the registered R2 attribution endpoint. The instrument is re-runnable under a new preregistration if clean static adjudication remains decision-critical.",
    "backing_ref": "registry/verdicts/casc-0.json; docs/next/interpretations/casc-0.md",
    "rationale": "Keeps the adverse raw sign visible without converting an instrument-invalid run into a NULL or general naturalisation failure.",
    "load_bearing": true,
    "status": "open",
    "owner": "synthesis-agent",
    "date": "2026-07-12",
    "notes": "All uses retain the self-authored corpus, engine-derived gold, constrained answer surface, stock-checkpoint and static-prompting rider."
  },
  {
    "id": "PROPOSED-ASM-1383",
    "tag": "STIPULATED",
    "claim": "UFO-in-RDF-1.2 architecture verdict: every surveyed UFO construct is representable, and the finite situation-scoped range-restricted UFO-SN3 profile over OWL-RL supplies a terminating decidable executable fragment. The shipped reference implementation and draft PR are architecture-enabling artifacts, not evidence for programme correctness or efficiency. No claim extends to unrestricted modal/deontic validity, arbitrary identity formulae, unrestricted existential mereology, native RDF-star matching or full reference-UFO conformance.",
    "backing_ref": "docs/next/arch/ufo-rdf12-expressibility.md; crates/sparq-conformance/tests/ufo_sn3/ (reference impl, sparq PR 2013)",
    "rationale": "Records the corrected expressibility result and shipped implementation while preserving the finite-profile boundary.",
    "load_bearing": true,
    "status": "open",
    "owner": "synthesis-agent",
    "date": "2026-07-12",
    "notes": "Tagged ARCHITECTURE-VERDICT plus ENGINEERING-SHIPPED in the synthesis."
  },
  {
    "id": "PROPOSED-ASM-1384",
    "tag": "STIPULATED",
    "claim": "Ontology-import state: the BFO/SUMO/FrameNet soft-typing g2-import instrument, candidate materials, controls and runner are built, but no non-mock run has landed. No soundness improvement, GO, source-attribution or adoption claim is licensed before the frozen A0-A3 experiment reports. Any proxy GO licenses at most a bounded non-binding advisory shard and remains subject to later two-human blind reconciliation for permanent scientific adoption.",
    "backing_ref": "docs/next/design/ontology-import-plan.md; registry/experiments/g2-import.json; poc/ontology-import-g2/",
    "rationale": "Separates executable readiness from empirical success and preserves human authority.",
    "load_bearing": true,
    "status": "open",
    "owner": "synthesis-agent",
    "date": "2026-07-12",
    "notes": "Every gold-dependent g2-import result remains PROVISIONAL-ON-LLM-PROXY."
  },
  {
    "id": "PROPOSED-ASM-1385",
    "tag": "EXTRAPOLATION",
    "claim": "Direction-only cross-experiment pointer: the accumulated evidence favours investigating authored meaning and warrants plus aligned stores, explicit worlds, deterministic proof-carrying inference, imported non-binding soft typing and fail-closed refusal. This is not an established architecture and is load-bearing for no thesis verdict.",
    "backing_ref": "docs/next/feasibility-synthesis-v5.md sections 2 and 5",
    "rationale": "Makes the emerging through-line explicit without treating a conjunction of heterogeneous evidence as a measured result.",
    "load_bearing": false,
    "resolution_path": "RULES-1 host-lift grade; phase-2 knull rules-source ablation; frozen g2-import run; original g2 and any GO-shaped g2-import human reconciliations; natural-input and lifecycle-cost gates",
    "status": "open",
    "owner": "synthesis-agent",
    "date": "2026-07-12",
    "notes": "Never a premise."
  }
]
```

*Supersede this synthesis when the RULES-1 host grade, g2-import result, relevant human-gold reconciliation, or `knull` rules-source ablation lands; do not silently edit its evidence state.*