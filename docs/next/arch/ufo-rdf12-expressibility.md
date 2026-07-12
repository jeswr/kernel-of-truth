VERDICT: YES-WITH-EXTENSION. [plausible]
Every surveyed UFO construct is representable using RDF 1.2 quoted triples/reifiers, N3 formulae, OWL vocabulary, and SHACL shapes. [well-established]
The required extension is UFO-SN3: a finite, situation-scoped, range-restricted N3/Datalog profile over OWL-RL. [plausible]
UFO-SN3 gives explicit semantics to worlds, quoted propositions, accessibility, existence, identity criteria, and closed validation scopes. [plausible]
Its positive materialization and stratified finite validation are terminating and decidable; fixed-rule data complexity is polynomial. [well-established]
It does not make unrestricted quantified modal/deontic FOL, arbitrary identity formulae, or unrestricted existential mereology decidable. [well-established]
GO: build a bounded SPARQ reference implementation covering a representative fragment of UFO-A, UFO-B, and UFO-C. [plausible]
GO: open it as a DRAFT PR, explicitly labeled an executable finite-world profile rather than a complete decision procedure for reference UFO. [plausible]

# UFO in RDF 1.2: Expressibility Verdict and SPARQ Reference-Implementation Plan

## Status and scope

[well-established] This synthesis incorporates the four research outputs on [UFO-A substantials](../../../poc/gpt56-review/ufo-a-subst/last-message.json), [UFO-A moments](../../../poc/gpt56-review/ufo-a-moments/last-message.json), [UFO-B/C](../../../poc/gpt56-review/ufo-bc/last-message.json), and [RDF 1.2 rules](../../../poc/gpt56-review/rdf12-rules/last-message.json), together with the [SPARQ estate report](../../../reports/sparq-estate.md) and [NSM–UFO bridge](nsm-ufo-bridge.md).

[well-established] The binding correction is accepted: statements about statements are expressible through RDF 1.1 reification, N3 quoted formulae, and RDF 1.2 quoted triples and reifiers.

[well-established] The remaining boundary concerns the entailment regime assigned to quoted propositions, situations, possible worlds, identity criteria, norms, and closed-data validation—not whether RDF can carry them.

## 1. The verdict

**YES-WITH-EXTENSION. [plausible]**

[well-established] Every surveyed UFO construct can be encoded as RDF resources, triples, quoted triples, reifiers, formulae, lists, graphs, and datatype values.

[well-established] OWL can supply structural class and property consequences, while SHACL can express many closed-data cardinality, distinctness, partition, and record-completeness checks.

[well-established] Bare RDF 1.2 does not assign possible-world, situation-satisfaction, causal, intentional, or deontic semantics to those encodings.

[well-established] OWL-RL plus positive Horn N3 also cannot detect missing modal witnesses, derive violations from absence, or generate all entities demanded by unrestricted existential axioms.

[plausible] A small extension—UFO-SN3—closes the practical gap for finite, explicitly represented situations while retaining termination and decidability.

### Verdict boundaries

| Question | Answer |
|---|---|
| Can RDF represent every surveyed UFO entity, type, meta-property, relation, proposition, and rule object? | **Yes.** [well-established] |
| Can statements about statements be represented without asserting their content? | **Yes.** [well-established] RDF 1.2 triple terms and N3 formulae can remain quoted, while a separate reifier can carry provenance, belief, norm, or situation metadata. |
| Can OWL-RL alone execute full rigidity, anti-rigidity, dependence, disposition, identity, and normative semantics? | **No.** [well-established] |
| Can OWL-RL plus UFO-SN3 execute a representative finite-world UFO profile? | **Yes.** [plausible] |
| Does UFO-SN3 decide unrestricted reference-UFO modal or deontic validity? | **No.** [well-established] |
| Does that limitation make the representational verdict partial? | **No.** [plausible] The constructs and their axioms remain expressible; the limitation concerns complete, decidable reasoning over unrestricted models. |

[plausible] Accordingly, “YES-WITH-EXTENSION” means complete representational coverage plus decidable execution for a declared finite-world profile.

[well-established] It does not mean that every arbitrary first-order modal formula, existential mereological theory, or user-defined identity criterion has become decidable.

## 2. The minimal extension: UFO-SN3

### 2.1 Definition

[plausible] **UFO-SN3** is a situation-scoped, range-restricted N3/Datalog profile layered over OWL-RL.

[plausible] Its semantic carrier consists of:

```text
holds(W, P)          proposition or formula P obtains in situation W
notHolds(W, P)       P is explicitly false in W
existsAt(X, W)       individual X exists in W
accessible(W, V)     V is accessible from W
closedFor(W, S)      situation W is complete for validation scope S
sameContinuant(X,Y)  X and Y represent the same persisting individual
violation(K, ...)    an integrity obligation of kind K has failed
```

[plausible] A proposition may be encoded by an RDF 1.2 triple term and reifier:

```turtle
:membership1
    rdf:reifies <<( :alice rdf:type :Person )>> ;
    ufo:holdsIn :world1 .
```

[plausible] Compound content may instead be represented by an N3 quoted formula related to a situation through `ufo:holds`.

[well-established] Quoting a triple or formula must not assert its content in the surrounding graph.

### 2.2 Rule restrictions

[plausible] The materialization stratum is function-free, range-restricted, and positive.

[plausible] It creates no fresh blank nodes, formulae, events, worlds, or identifiers.

[plausible] Identity rules may merge existing terms through finite union-find or congruence closure.

[plausible] A separate validation stratum admits stratified negation and bounded distinct-value counting only inside scopes explicitly declared finite and closed.

[plausible] Anti-rigidity, minimum cardinality, existential dependence, and semi-rigidity are checked against supplied witnesses rather than satisfied by unconstrained witness generation.

[well-established] Under open-world RDF semantics, absence of a fact is not falsity; therefore no negative validation may run unless its applicable scope is explicitly closed.

### 2.3 Representative rules

[plausible] The following abstract rules define the intended semantics and can be compiled to SPARQ’s supported N3/RIF representation.

```text
# Inherence entails existential dependence.
InheresIn(M,B)
→ ExistentiallyDependsOn(M,B).

# A dependent cannot exist in a represented world without its dependency.
ExistentiallyDependsOn(X,Y) ∧ ExistsAt(X,W)
→ ExistsAt(Y,W).

# Rigidity propagates membership while the individual continues to exist.
Rigid(T) ∧ Accessible(W,V) ∧ ExistsAt(X,V)
∧ Holds(W, type(X,T))
→ Holds(V, type(X,T)).

# A supplied explicit counterworld witnesses contingent membership.
Holds(W, type(X,T)) ∧ Accessible(W,V)
∧ ExistsAt(X,V) ∧ NotHolds(V, type(X,T))
→ ContingentFor(T,X).

# A closed search with no counterworld is a rigidity violation for an anti-rigid type.
AntiRigid(T) ∧ Holds(W, type(X,T))
∧ ClosedFor(W, modalMembership(T))
∧ not ContingentFor(T,X)
→ Violation(missingAntiRigidityWitness,T,X).

# Type-governed operational identity.
IdentityKey(T,P)
∧ Holds(W, type(X,T)) ∧ Holds(W, type(Y,T))
∧ Holds(W, value(X,P,K)) ∧ Holds(W, value(Y,P,K))
→ SameContinuant(X,Y).

# A relator depends on each entity it mediates.
Relator(R) ∧ Mediates(R,X) ∧ ExistsAt(R,W)
→ ExistsAt(X,W).

# Trigger satisfaction activates a disposition.
Disposition(D) ∧ TriggerCondition(D,C) ∧ Holds(W,C)
→ ActivatedIn(D,W).

# Normalize manifestation direction.
ManifestsIn(D,E)
→ ManifestationOf(E,D).

# Project a material relationship from a relator.
Relator(R) ∧ RelatorType(R,Marriage)
∧ Mediates(R,X) ∧ Mediates(R,Y) ∧ Different(X,Y)
→ Holds(W, spouseOf(X,Y)).

# A currently applicable norm creates an obligation record already named in the data.
Norm(N) ∧ Condition(N,C) ∧ Consequent(N,Q)
∧ Holds(W,C) ∧ ObligationRecord(O,N,W)
→ ActiveObligation(O,Q,W).
```

[well-established] The last rule deliberately requires a supplied obligation record.

[well-established] Automatically inventing an unbounded number of commitments, manifestations, fusions, or possible worlds would leave function-free Datalog and require a separately selected existential-rule fragment.

### 2.4 Decidability

[well-established] Positive function-free Datalog over finite RDF terms reaches a finite fixpoint.

[well-established] Equality over existing terms only merges a finite set of equivalence classes.

[well-established] Stratified negation over finite, explicitly closed scopes is decidable.

[well-established] Bounded counts over an explicitly finite graph are decidable.

[well-established] For a fixed UFO-SN3 ruleset, positive materialization has polynomial data complexity.

[well-established] Unrestricted N3 with term generation, unrestricted existential rules, arbitrary built-ins, or network access does not inherit that guarantee.

[well-established] General first-order modal or deontic validity and arbitrary quantified identity formulae are not decidable in general.

[plausible] Guarded or weakly acyclic existential rules could later be offered as a separate profile, but they are not part of the minimal reference implementation.

### 2.5 Fit to SPARQ

[well-established] The SPARQ estate already contains OWL-RL preprocessing, N3 reasoning, a range-restricted monotone RIF-Core front end, formula-scope tests, and a SHACL/OWL verification gate.

[plausible] UFO-SN3 therefore fits SPARQ as an additional named entailment and validation profile rather than as a new general-purpose theorem prover.

[plausible] The required engine additions are:

- [plausible] normalization of RDF 1.2 reifiers and N3 formulae into stable internal proposition identifiers;
- [plausible] a situation-indexed `holds` lookup and rule-head operation;
- [plausible] equality-generating or `sameContinuant` rule heads over existing terms;
- [plausible] explicit closed-scope declarations;
- [plausible] stratified missing-witness and bounded-count validation;
- [plausible] proof records distinguishing OWL-RL entailment, UFO-SN3 materialization, and closed-scope validation.

[plausible] `sameContinuant` should be preferred for cross-situation identity unless true RDF denotational identity is intended.

[well-established] Uncontrolled use of `owl:sameAs` could incorrectly collapse situation records, temporal stages, or representations of one continuant.

## 3. Per-family expressibility summary

| Family | RDF/OWL carrier | Additional executable semantics | Verdict |
|---|---|---|---|
| A-substantials: Kind and Subkind | [well-established] Classes, subclass axioms, identity-provider resources, rigidity annotations, keys, and SHACL cardinalities are directly representable. | [plausible] UFO-SN3 checks world-indexed rigidity and identity-provider inheritance. | **Expressible; executable with extension.** [plausible] |
| A-substantials: Role and Phase | [well-established] Role/phase classes, inherited identity providers, relational or intrinsic conditions, and phase partitions are representable. | [plausible] Closed finite-world witness checking supplies anti-rigidity; OWL/SHACL supplies structural partition checks. | **Expressible; executable with extension.** [plausible] |
| A-substantials: Category, RoleMixin, Mixin | [well-established] Non-sortality, rigidity annotations, subtype/provider relationships, and conditioning relations are representable. | [plausible] Semi-rigidity requires at least one essential and one contingent instance witness; RoleMixin requires relational-dependence checks across providers. | **Expressible; executable with extension.** [plausible] |
| Identity and rigidity meta-properties | [well-established] Criteria, providers, keys, quoted rules, and modal annotations can be represented as first-class resources. | [plausible] Range-restricted criteria, explicit situations, equality over existing terms, and closed modal validation are required. | **Expressible; decidable for the declared profile.** [plausible] |
| A-moments: Quality and quale | [well-established] A quality, bearer, quale, quality structure, dimension, coordinate, and region can all be ordinary RDF resources. | [plausible] Known projections and metrics need authored relations or deterministic built-ins. | **Expressible; computation is profile-specific.** [plausible] |
| A-moments: Mode and disposition | [well-established] Modes, triggers, activations, and manifestations can be reified without asserting quoted trigger content. | [plausible] Dependence propagation and trigger satisfaction fit UFO-SN3; unrestricted counterfactual disposition semantics does not fit OWL-RL alone. | **Expressible; executable with extension.** [plausible] |
| A-moments: Relator and qua-individual | [well-established] Relators, mediation, qua-parts, bearers, external dependencies, and material-relation propositions are representable. | [plausible] Dependence, distinct-participant, and projection rules fit UFO-SN3; unrestricted fusion axioms do not. | **Expressible; bounded fragment executable.** [plausible] |
| Inherence and existential dependence | [well-established] Both relations are directly statable in RDF. | [plausible] World-indexed existence propagation and missing-dependency validation require UFO-SN3 and closed scopes. | **Expressible; executable with extension.** [plausible] |
| B: Events and participation | [well-established] Events, intervals, participation records, participant roles, and disposition manifestations are ordinary RDF n-ary structures. | [plausible] Temporal ordering, projections, and safe participation rules fit OWL-RL plus UFO-SN3. | **Expressible and tractably executable.** [plausible] |
| B: Temporal parts and event mereology | [well-established] Part relations, overlap, atomicity, and supplied fusion nodes are representable. | [plausible] Transitivity and finite validation are tractable; arbitrary existence-of-fusion axioms require existential rules or supplied witnesses. | **Expressible; bounded fragment executable.** [plausible] |
| B: Causation and situations | [well-established] Causal-relation and situation nodes can reference quoted propositions or formulae. | [plausible] Situation satisfaction and accessibility require UFO-SN3; counterfactual causation requires an authored counterfactual theory. | **Expressible; semantics is extension-defined.** [plausible] |
| C: Agents and social objects | [well-established] Agents, physical/social objects, communities, recognition, and founding acts are ordinary RDF structures. | [plausible] Recognition and dependence consequences fit safe rules. | **Expressible and executable.** [plausible] |
| C: Beliefs, goals, and intentions | [well-established] RDF 1.2 reifiers and N3 formulae represent propositional content without asserting it. | [plausible] Satisfaction, closure, justification, and intention-to-action consequences require authored rules. | **Expressible; semantics is ruleset-specific.** [plausible] |
| C: Commitments, claims, and social relators | [well-established] Debtor, creditor, content, counterpart, status, and founding-event records are representable. | [plausible] Lifecycle, fulfillment, violation, and discharge fit finite rules and validation when their event and situation data are complete. | **Expressible; executable with extension.** [plausible] |
| C: Norms and normative descriptions | [well-established] Conditions, consequents, modalities, priorities, recognition, and quoted content are representable. | [plausible] Positive norms fit safe rules; defeasible priorities and violation by absence require stratified validation or a separately declared ASP-like profile. | **Expressible; bounded normative profile executable.** [plausible] |
| C: Delegation and social roles | [well-established] Delegator, delegatee, authority, content, context, role holding, interval, and revocation events are representable. | [plausible] Transfer rules fit UFO-SN3 when resulting records are supplied or deterministically named; anti-rigidity uses modal witness checks. | **Expressible; executable with extension.** [plausible] |

## 4. Reference-implementation plan for SPARQ

### 4.1 Deliverables

#### A. RDF 1.2 encoding vocabulary

[plausible] Add a versioned vocabulary package, provisionally `ufo-rdf12/0.1`, containing:

- [plausible] core classes for situations, propositions, reifiers, identity criteria, identity providers, modal properties, moments, events, social entities, and validation results;
- [plausible] properties including `holdsIn`, `falseIn`, `existsIn`, `accessible`, `closedFor`, `identityProvider`, `identityCriterion`, `sameContinuant`, `inheresIn`, `externallyDependsOn`, `mediates`, `manifestsIn`, `condition`, and `content`;
- [plausible] OWL-RL axioms for safe taxonomic, inverse, domain/range, disjointness, and property-chain consequences;
- [plausible] SHACL shapes for required bearers, identity providers, relator participants, paired commitments/claims, partitions, distinctness, and declared closed scopes;
- [plausible] examples in Turtle/TriG/N3 showing RDF 1.2 reifiers and equivalent normalized `holds` records.

[plausible] The vocabulary should distinguish descriptive annotations from executable commitments.

[plausible] A type marked `ufo:Rigid` should not acquire modal consequences unless the UFO-SN3 profile is selected.

#### B. UFO-SN3 engine profile

[plausible] Add a named `ufo-sn3` profile to `sparq-reason` with three ordered regimes:

1. [plausible] **OWL-RL closure:** structural class, property, and equality consequences.
2. [plausible] **UFO-SN3 materialization:** positive situation-scoped rules over existing terms.
3. [plausible] **UFO-SN3 validation:** stratified missing-witness, distinctness, and bounded-cardinality checks over declared closed scopes.

[plausible] Each derived fact or violation should record its regime and premises.

[plausible] Validation findings must not be silently promoted into OWL entailments.

#### C. Ruleset modules

[plausible] Ship small, reviewable rule modules rather than one monolithic theory:

- [plausible] `subst.n3`: rigidity, anti-rigidity witnesses, phases, roles, sortality, and identity-provider checks;
- [plausible] `moments.n3`: inherence, dependence, dispositions, relators, and qua-individual projections;
- [plausible] `events.n3`: participation, manifestation, temporal parts, and event mereology;
- [plausible] `social.n3`: beliefs, goals, intentions, commitments, claims, norms, and delegation;
- [plausible] `validation.n3` or equivalent compiled constraints: closed-scope counterexamples and missing witnesses.

[plausible] Each module should declare whether it is monotone materialization, closed validation, or reference-only documentation.

### 4.2 Representative conformance suite

[plausible] The initial suite should demonstrate:

| Test group | Required demonstration |
|---|---|
| Quotation | [well-established] A quoted belief, trigger, or norm consequent is not asserted merely because it is quoted. |
| Reifier normalization | [plausible] RDF 1.2 reifier and supported N3 formula encodings normalize to equivalent proposition records. |
| Kind | [plausible] Membership propagates across an accessible world while the individual exists; an explicit contrary fact yields a rigidity violation. |
| Role | [plausible] Every role instance has a supplied accessible counter-situation; absence is a violation only when the applicable scope is closed. |
| Phase | [plausible] Phase alternatives are disjoint and complete under an explicitly declared finite partition. |
| Mixin | [plausible] Semi-rigidity succeeds only with both essential and contingent instance witnesses. |
| Identity | [plausible] A range-restricted identity criterion derives `sameContinuant`; it does not collapse unrelated situation records. |
| Quality | [plausible] Quality, bearer, quale, structure, and coordinate remain distinct nodes. |
| Dependence | [plausible] A mode’s existence entails its bearer’s existence; an explicit missing bearer in a closed world is reported. |
| Disposition | [plausible] A quoted trigger activates a disposition and links a supplied manifestation event. |
| Relator | [plausible] A relator mediates distinct participants, depends on them, and projects a material relation. |
| Event | [plausible] Participation and temporal-part rules materialize expected consequences without making causation globally transitive. |
| Belief | [well-established] Believing a proposition does not entail that proposition in the enclosing world. |
| Commitment and claim | [plausible] A supplied pair shares content and progresses through active, fulfilled, violated, or discharged states. |
| Norm | [plausible] A satisfied condition activates a supplied obligation; an absent obligation is not silently invented. |
| Open/closed boundary | [well-established] Missing data produces no negative conclusion in an open scope and may produce a validation result in a declared closed scope. |
| Termination | [plausible] The finite fixture reaches a stable fixpoint and a second materialization pass adds no triples. |
| Proof provenance | [plausible] Every consequence records whether it came from OWL-RL, UFO-SN3 materialization, or closed validation. |

### 4.3 Representative UFO fragment

[plausible] The first draft should cover one coherent scenario rather than isolated vocabulary examples.

[plausible] A suitable fixture is an employment scenario containing:

- [plausible] `Person` as a Kind with an operational identity key;
- [plausible] `Employee` as a Role inheriting identity from `Person`;
- [plausible] an employment Relator with employee/employer qua-individuals;
- [plausible] a commitment and matching claim with quoted content;
- [plausible] a work event manifesting an intention or disposition;
- [plausible] two accessible situations demonstrating role acquisition and cessation;
- [plausible] one deliberately invalid closed situation for each major validation rule.

[plausible] This scenario exercises A-substantials, A-moments, B-events, C-social entities, quotation, identity, rigidity, dependence, and validation within one bounded graph.

### 4.4 Draft-PR sequence

[plausible] A reviewable draft PR should be staged as follows:

1. [plausible] Add the vocabulary, examples, profile specification, and golden RDF fixtures.
2. [plausible] Add proposition/reifier normalization and situation-indexed `holds`.
3. [plausible] Add the positive UFO-SN3 materialization modules.
4. [plausible] Add closed-scope validation and bounded witness checks.
5. [plausible] Add proof-regime labels and the conformance matrix.
6. [plausible] Document unsupported reference-UFO consequences and extension safety restrictions.
7. [plausible] Run the existing OWL-RL, N3, formula-scope, SHACL, and regression suites alongside the new fixtures.

[plausible] The draft PR should avoid claiming complete UFO conformance until an independent UFO modeler reviews the vocabulary mappings and rule obligations.

## 5. Feasibility and GO/NO-GO

**GO. [plausible]**

[well-established] SPARQ already has the central architectural components: OWL-RL closure, N3 rules, formula-scope support, finite graph processing, and SHACL/OWL verification.

[plausible] The remaining implementation is bounded enough for a reference profile and draft PR.

[plausible] The highest-risk engine work is situation-indexed quoted-formula handling, followed by stratified closed-scope validation and proof provenance across regimes.

[plausible] These risks justify a draft PR and explicit experimental profile label, not a no-go verdict.

[well-established] A production claim of complete reference-UFO reasoning would be unsupported because unrestricted modal/deontic validity, arbitrary identity formulae, and unrestricted existential mereology remain outside the decidable profile.

## 6. Residual boundaries and non-claims

[well-established] UFO-SN3 does not quantify over unrepresented possible worlds.

[well-established] A finite declared frame validates only the represented model and its declared completeness assumptions.

[well-established] Arbitrary identity criteria are representable as quoted formulae but executable in this profile only when compiled to range-restricted rules or supported deterministic built-ins.

[well-established] Minimum cardinalities, manifestations, obligations, fusions, and possible worlds require supplied or deterministically bounded witnesses.

[well-established] Unrestricted existential generation is outside the minimal extension.

[well-established] Counterfactual causation requires a selected counterfactual semantics and is not obtained merely by adding `accessible`.

[well-established] Defeasible normative conflicts require a declared non-monotonic policy such as stratified priorities or a separate ASP-like regime.

[well-established] RDF named graphs alone do not establish that a graph name denotes a situation or that its triples are true in that situation.

[plausible] UFO-SN3 supplies that commitment through an explicit `holds` relation rather than relying on raw dataset syntax.

[well-established] These are limits on the executable profile, not residual failures to represent UFO constructs.

## 7. Fallback issue

[plausible] No fallback issue is required for the present GO decision.

[plausible] If implementation discovers that SPARQ cannot preserve quoted formula identity across parsing, indexing, rule heads, and proof serialization, the fallback issue should be:

> **Add stable proposition-term support to `sparq-reason`.** [plausible] Define canonical identifiers for RDF 1.2 triple terms and N3 quoted formulae; preserve asserted-versus-quoted status; expose situation-indexed lookup and rule-head insertion; serialize proof premises without asserting quoted content; and add round-trip conformance tests. [plausible]

[plausible] If closed-scope validation cannot be added without changing the monotone reasoner’s contract, it should remain a separate validation pass rather than being simulated through unsound negation in OWL-RL or positive N3.

## 8. Final recommendation

[plausible] Build and open the SPARQ reference implementation as a DRAFT PR.

[plausible] Name the profile UFO-SN3 and define its finite-world, closed-scope, range-restricted semantics before merging engine changes.

[plausible] Treat RDF 1.2 as the representation carrier, OWL-RL as the structural entailment layer, UFO-SN3 as the situation-scoped rule layer, and SHACL or equivalent finite validation as the constraint layer.

[well-established] Preserve a visible distinction between reference UFO, executable UFO-SN3, and local closed-world policy.

[well-established] The corrected conclusion is that RDF has no statements-about-statements barrier.

[well-established] The genuine boundary is complete reasoning over unrestricted modal, identity, existential, causal, and deontic theories.