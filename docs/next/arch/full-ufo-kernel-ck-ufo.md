# Candidate proposal: CK-UFO — a full-UFO Concept Kernel

Epistemic tags used throughout:

- **[DERIVED]** — follows from the requested repository documents or inspected SPARQ implementation.
- **[STIPULATED]** — a proposed architecture, interface, rule, threshold, or sequencing decision.
- **[EXTRAPOLATION]** — an empirical expectation to be tested; never a premise.

This proposal makes no feasibility conclusion about either programme thesis. CORRECTNESS and EFFICIENCY remain **INCONCLUSIVE-PENDING**.

## 1. The architecture

### 1.1 Architectural position

**[STIPULATED]** CK-UFO is a neurosymbolic concept kernel in which:

1. authored NSM explications remain the human-auditable meaning and warrant layer;
2. full UFO supplies the formal ontological commitments, including its modal and identity-bearing content;
3. RDF 1.2 quoted triples and reifiers carry propositions without asserting them;
4. an explicit finite-world execution profile checks the tractable part of those commitments;
5. a specialised UFO-aware vector layer proposes and ranks candidates;
6. the symbolic engine remains authoritative for acceptance, rejection, derivation, and refusal.

The core flow is:

```text
Authored NSM explication
        │
        ▼
Authored ontological bridge judgment
        │
        ├── full-UFO reference commitment
        │       modality, identity, dependence, relators, events
        │
        └── executable projection
                OWL-RL → safe Horn → closed validation
                         │
                         ▼
RDF 1.2 proposition/world model ──► UFO-aware concept vectors
                         │                  │
                         │                  ▼
                         └────────► candidate proposer
                                            │
                                            ▼
                                  full-UFO checking engine
                                            │
                         proof / violation / underdetermined
                                            │
                                            ▼
                                  host integration or answer
```

**[DERIVED]** This retains the NSM–UFO bridge’s correct asymmetry: NSM can provide intelligible evidence for a classification, but it cannot by itself supply predicate quantification, modal rigidity, identity criteria, inherence, qua-individuals, or relator mereology.

**[STIPULATED]** “Fully grounded in UFO” therefore means that every identity-bearing concept record must state its place in the full UFO theory and retain the reference commitment even where the executable engine implements only a bounded profile. It does not mean that RDF or the finite checker becomes a complete decision procedure for reference UFO.

### 1.2 Kernel record

**[STIPULATED]** Each concept receives a versioned `ck-ufo/1` sidecar with at least these fields:

```text
concept identifier
source explication hash
bridge status: proposed | endorsed | underdetermined | rejected
denotation level: type | individual | relation | proposition
ontological category
sortality status
rigidity status
identity provider
identity criterion
dependence commitments
relator/qua pattern, if applicable
event/participation pattern, if applicable
disposition pattern, if applicable
reference-UFO formula or pattern identifier
executable projection
non-executable residue
provenance and endorsement
```

**[STIPULATED]** The ontology category is not a single `gufo:` label. It is a structured commitment spanning the full tree:

```text
Entity
├── Endurant
│   ├── Substantial / Object
│   └── Moment / Trope
│       ├── Quality
│       ├── Mode
│       │   └── Disposition
│       └── Relator
│           └── Qua-individual participation parts
└── Perdurant
    └── Event
        ├── atomic / complex
        ├── temporal parts
        ├── participation
        └── disposition manifestation
```

The corresponding type-level profile includes:

```text
Sortal
├── Kind
├── Subkind
├── Role
└── Phase

Non-sortal
├── Category
├── Mixin
├── RoleMixin
└── PhaseMixin
```

**[STIPULATED]** Rigidity, anti-rigidity, semi-rigidity, sortality, identity provision, dependence, and conditioning are first-class fields, not comments inferred from class names.

### 1.3 Modal and identity semantics

**[STIPULATED]** The executable modal carrier follows the finite UFO-SN3 approach:

```text
holds(world, proposition)
notHolds(world, proposition)
existsAt(individual, world)
accessible(world, otherWorld)
closedFor(world, scope)
sameContinuant(recordA, recordB)
violation(kind, evidence...)
```

A type membership proposition is carried without asserting it globally:

```turtle
:membershipRecord
    rdf:reifies <<( :alice rdf:type :Student )>> ;
    ufo:holdsIn :world1 .
```

**[STIPULATED]** The checker gives the meta-properties distinct operational meanings:

- A rigid type requires membership to persist across accessible worlds in which the same continuant exists.
- An anti-rigid type requires a supplied accessible counter-situation in which the individual exists but does not instantiate the type.
- Failure to find such a counter-situation is a violation only when the applicable modal scope is explicitly closed.
- A Role is anti-rigid and relationally conditioned.
- A Phase is anti-rigid and intrinsically conditioned.
- A Mixin or semi-rigid type requires both essential and contingent witness patterns.
- A Kind supplies an identity principle; a Role or Phase inherits rather than replaces it.

**[DERIVED]** This is necessarily bounded execution. In an open RDF graph, absence of a counterworld is not evidence of rigidity or a violation of anti-rigidity.

**[STIPULATED]** Identity criteria have three representations:

1. a reference-level UFO criterion, possibly outside the executable fragment;
2. a safe executable criterion over existing named terms, such as an endorsed key or range-restricted rule;
3. a vector feature used only for candidate retrieval.

Only the second may derive `sameContinuant`. It should not emit `owl:sameAs` unless genuine RDF denotational identity is intended.

**[DERIVED]** This distinction prevents accidental collapse of temporal stages, situation-specific records, qua-individuals, or two representations of one continuant.

### 1.4 Relators and qua-individuals

**[STIPULATED]** Material relations such as employment, marriage, ownership, commitment, or treatment are not represented solely as binary edges. The kernel represents:

- the relator individual;
- the entities it mediates;
- the participant-specific qua-individuals;
- their bearers;
- external existential dependence;
- the founding event, where applicable;
- the material relation projected from the relator;
- the situations in which the relator exists.

The binary edge remains available as a derived projection:

```text
Relator(R)
∧ RelatorType(R, Employment)
∧ Mediates(R, Person)
∧ Mediates(R, Organisation)
→ employedBy(Person, Organisation)
```

**[STIPULATED]** The reverse implication is not automatic. A binary edge alone is insufficient evidence to invent a relator, qua-individuals, or founding event.

This yields several checks unavailable in the current stack:

- a relator cannot exist in a represented world while a mediated participant is absent;
- participant-specific rights, claims, duties, or qualities attach to the appropriate qua-individual;
- two equal-looking binary relations can remain distinct because they arise from distinct relators;
- termination or replacement of a role need not change the bearer’s Kind identity.

### 1.5 Moments, dispositions, and events

**[STIPULATED]** Qualities, modes, dispositions, relators, and events are separate vector and rule categories rather than flat nodes.

A disposition record includes:

```text
disposition individual
bearer
disposition type
trigger proposition or situation
activation situation
manifestation event
possible non-manifestation
dependence and provenance
```

The checker may derive:

```text
inheresIn(disposition, bearer)
→ existentiallyDependsOn(disposition, bearer)

triggerCondition(disposition, proposition)
∧ holds(world, proposition)
→ activatedIn(disposition, world)

manifestsIn(disposition, event)
→ manifestationOf(event, disposition)
```

**[STIPULATED]** Activation does not entail manifestation unless an endorsed rule explicitly licenses it. This preserves the distinction between possessing a disposition, encountering its trigger, and manifesting it.

**[STIPULATED]** Events are first-class perdurants with temporal parts and participation records. An object’s grammatical appearance in an NSM clause is not automatically UFO participation; participation must be asserted or derived through the applicable event/disposition pattern.

### 1.6 Vector architecture

**[STIPULATED]** A CK-UFO concept vector is a typed bundle, not one undifferentiated KGE row:

| Block | Encodes |
|---|---|
| NSM block | Existing deterministic explication structure, roles, fillers, operators, and recursive concept references |
| Ontic-category block | Endurant/object, moment/trope, perdurant/event, type/individual/relation/proposition distinctions |
| Taxonomy block | Kind/Subkind/Role/Phase/Category/Mixin hierarchy |
| Modal block | Rigidity, anti-rigidity, semi-rigidity, conditioning, accessible-world witness profile |
| Identity block | Identity provider, criterion family, cross-situation `sameContinuant` evidence |
| Dependence block | Inherence, existential dependence, external dependence, mediation |
| Relator block | Relator–qua–bearer incidence and material-relation projection |
| Event block | Participation, temporal parts, causation, trigger/activation/manifestation structure |
| Proposition block | Quoted triple content and reifier-specific situation, attitude, norm, and provenance context |
| Evidence block | Endorsement, proof regime, assurance, source quality, and executable/reference boundary |

**[STIPULATED]** Missing blocks carry explicit masks. They are not silently replaced by zero vectors, because “not supplied,” “not applicable,” and “known false” are semantically different.

**[STIPULATED]** Retrieval uses weighted block fusion. The symbolic checker then applies hard constraints only from endorsed commitments. Imported selectional preferences remain soft and must never become hard domain/range masks.

**[STIPULATED]** A quoted triple has two vector objects:

- a proposition-content vector, composed structurally from subject, predicate, and object;
- one or more reifier vectors carrying world, belief, norm, provenance, confidence, or temporal context.

This permits two agents to believe the same proposition, or the same proposition to hold in one situation and fail in another, without duplicating or globally asserting its content.

### 1.7 Checking and host integration

**[STIPULATED]** The checking engine has ordered, visible regimes:

1. `owl-rl`: structural closure;
2. `horn-def`: safe, positive UFO rules over existing terms;
3. `ufo-modal`: bounded situation/world rules;
4. `validation`: stratified missing-witness, partition, distinctness, and cardinality checks over declared closed scopes;
5. `policy`: explicitly local covering, completeness, or advisory decisions;
6. `reference-only`: commitments preserved but not executed.

Every proof node records its regime, rule, premises, source bridge record, and explication hash.

**[STIPULATED]** The result type is four-valued:

```text
ENTAILED
CONTRADICTED
UNDERDETERMINED
OUT-OF-PROFILE
```

`UNDERDETERMINED` means the adopted logic lacks sufficient facts. `OUT-OF-PROFILE` means the reference commitment exceeds the selected execution layer. Neither may be converted into a negative answer.

**[STIPULATED]** Neural components may propose alignments, candidate propositions, relators, identity matches, or retrieval order. They never license an entailment. The engine admits a proposal only if it has a valid proof or passes the applicable consistency and validation gates.

### 1.8 What CK-UFO buys over the current stack

**[DERIVED]** The current stack combines NSM meaning, gUFO taxonomy, a proof-carrying rules engine, and aligned authored content. Its gUFO component supplies useful class labels and hierarchy but not executable modal identity semantics.

CK-UFO adds:

- executable finite-world rigidity and anti-rigidity checks;
- identity-provider and cross-situation identity discipline;
- explicit object/event/trope separation;
- relators and qua-individuals instead of reducing every relationship to a binary edge;
- disposition/trigger/manifestation distinctions;
- quoted propositional content that is not accidentally asserted;
- structured refusal when a reference-UFO commitment exceeds the executable profile;
- vector blocks aligned with these distinctions rather than a flat KGE.

**[EXTRAPOLATION]** The primary possible correctness mechanism is rejection of ontologically impossible candidates: Role treated as Kind, event treated as object, trope treated as bearer, relator collapsed into a binary edge, identity merged across incompatible criteria, or quoted belief treated as fact.

**[EXTRAPOLATION]** The possible efficiency mechanism is earlier candidate pruning: type- and category-valid negative sampling, modality-aware retrieval, relator incidence filters, and identity-provider masks may reduce neural candidates and verification work at fixed recall.

**[STIPULATED]** The architecture targets both theses, but asymmetrically:

- CORRECTNESS is the primary target through better candidate admissibility, validation, and proof.
- EFFICIENCY is a conditional secondary target through candidate reduction and symbolic offload.

No positive result on either target is assumed.

## 2. Required upstream SPARQ work

### 2.1 Current quoted-triple support

**[DERIVED]** `sparq-core` already represents RDF 1.2 triple terms structurally as dictionary terms containing component IDs. Its RDF loaders handle triple terms, reifiers, annotations, nesting bounds, persistence, reconstruction, and fingerprint stability.

**[DERIVED]** The crate named `sparq-parse` is chiefly a compression/streaming utility; RDF syntax handling relevant here is in `sparq-core`, while SPARQL 1.2 term patterns arrive through the query algebra dependency.

**[DERIVED]** The SPARQL algebra exposes quoted-triple term variants, but the QL rewriter deliberately rejects them as outside DL-Lite scope.

**[DERIVED]** EL and DL likewise do not treat triple terms as ordinary individuals, classes, or object properties. That fail-closed boundary is appropriate and should remain.

**[DERIVED]** The generic RDFS/OWL materializers can carry a triple-term ID as an opaque object in ordinary triples, but they cannot inspect, bind, or construct its subject/predicate/object components.

**[DERIVED]** The N3 engine supports quoted formulae and lists, but its rule `Term` enum has no RDF 1.2 triple-term variant. The compiled rules path accepts dictionary-representable leaf constants and rejects structural formula/list constants; it has no structural quoted-triple pattern operation.

Thus SPARQ can store quoted propositions, but it cannot yet execute rules such as:

```text
?r rdf:reifies <<(?s ?p ?o)>>
∧ ?r ufo:holdsIn ?w
→ holds(?w, triple(?s, ?p, ?o))
```

### 2.2 Inference over quoted triples

**[STIPULATED]** Add a structural triple-term variant to the N3/rule term model:

```text
Triple(subjectTerm, predicateTerm, objectTerm)
```

Required machinery:

- parser support for RDF 1.2 `<<( … )>>` in facts, rule bodies, and range-restricted heads;
- recursive `is_ground`, substitution, unification, hashing, rendering, and proof serialization;
- nested-term depth limits aligned with `sparq-core`;
- constant binding to an existing dictionary triple term;
- structural matching in which component variables bind independently;
- safe head construction using `Dict::intern_triple_ids` only after all components are bound;
- explicit prevention of quotation leakage: matching a triple term never asserts its component triple;
- proof nodes that distinguish “matched quoted content” from “matched an asserted triple.”

**[STIPULATED]** The compiled engine should lower structural terms through virtual decomposition and construction operations:

```text
DecomposeTriple(term, subject, predicate, object)
ConstructTriple(subject, predicate, object, term)
```

A body pattern becomes a join against a virtual `tripleTermParts` relation backed by the dictionary. A head construction is permitted only when all three components are already bound to valid RDF term kinds.

**[STIPULATED]** No fresh worlds, relators, events, or proposition contents are generated. Constructing the canonical triple-term ID from already-bound components is acceptable; inventing unbound semantic witnesses is not.

**[STIPULATED]** Add conformance tests for:

- a quoted proposition not being asserted;
- variable binding inside a triple term;
- nested triple terms;
- multiple reifiers of one proposition;
- construction in a range-restricted rule head;
- invalid predicate/component kinds;
- depth-budget refusal;
- proof-tree preservation;
- text N3 versus compiled-rule parity.

**[STIPULATED]** QL, EL, and DL should retain their current quoted-term refusals. UFO-SN3 belongs in `sparq-reason` as a separate composite profile; forcing modal propositions into DL-Lite, EL, or OWL-DL would not supply UFO’s modal semantics.

**Effort: L.** Approximately 4–8 engineering weeks including compiled/text parity, explanation support, incremental behavior, fuzzing, and conformance.

### 2.3 Vectorisation over quoted triples

**[DERIVED]** Current vector fingerprinting understands nested triple terms, but the KGE evaluation path treats only IRIs and blank nodes as entities. Triple-term nodes are therefore excluded from candidate pools and ordinary link-prediction targets.

**[DERIVED]** Current provenance weighting reads confidence, assurance, and lineage from the positive triple’s head. It does not follow `rdf:reifies` from a reifier to the quoted proposition it qualifies.

**[STIPULATED]** Introduce a non-asserting incidence normalization for vector construction:

```text
QuotedContent Q
Q --qtSubject--> S
Q --qtPredicate--> P
Q --qtObject--> O

Reifier R --rdf:reifies--> Q
R --holdsIn / believedBy / confidence / provenance--> context
```

These incidence edges exist only in the vectorization view. They must not enter the ontology closure as claims that the quoted triple holds.

Required work:

- include triple terms as a distinct vector node class;
- recursively compose a proposition vector from its three components plus a quotation marker;
- maintain separate content and reifier embeddings;
- allow multiple reifiers to share one content vector while retaining different contextual vectors;
- make provenance weighting reifier-aware;
- support proposition/world and proposition/attitude prediction tasks;
- split train/test by proposition content as well as reifier ID to prevent alternate-reifier leakage;
- exclude quoted propositions from physical-object candidate pools;
- add reconstruction and non-assertion metrics.

**[STIPULATED]** A useful default composition is:

```text
Q = f(subject, predicate, object, quotation-role) + learned residual
R = g(Q, reifier type, world, source, attitude, assurance)
```

The composed component keeps unseen proposition contents representable; the residual captures learned graph regularities.

**Effort: M.** Approximately 2–4 engineering weeks after the triple-term contract is stable. Reifier-aware provenance and leakage-safe evaluation are the likely cost drivers.

### 2.4 Specialised full-UFO vectorisation

**[DERIVED]** The present synthetic gUFO slice distinguishes Kind, Role, and Phase only through ordinary typed triples. The `gufo_prior` field in the evaluation harness is currently always false: the specialised prior is an exposed but unimplemented ablation axis.

**[DERIVED]** Current structure-aware vectorisation supplies RDFS/OWL closure, declared and observed domain/range constraints, type-constrained negatives, taxonomy geometry, disjointness, SHACL priors, and PROV-O-style weights. This is a suitable extension pattern, but it is not yet full-UFO vectorisation.

**[STIPULATED]** A full-UFO encoder adds:

- an ontic-category mask separating objects, events, moments, types, propositions, and relators;
- rigidity and anti-rigidity features derived from explicit world witnesses;
- identity-provider embeddings and contrastive `sameContinuant` training pairs;
- Role-versus-Phase conditioning features;
- phase-partition and disjointness structure;
- relator/qua-individual hypergraph incidence;
- inherence and existential-dependence edges;
- disposition trigger, activation, and manifestation structure;
- event participation and temporal-part features;
- proof-regime and endorsement weights.

Specialised losses or sampling rules may include:

- taxonomy preservation for Kind/Subkind hierarchy;
- cross-world invariance for rigid membership;
- explicit counterworld contrast for anti-rigid membership;
- identity consistency across situation records;
- relator reconstruction from its qua parts and mediated participants;
- material-relation projection reconstruction;
- event/disposition sequence consistency;
- category-valid corruption only.

**[STIPULATED]** Soft lexical selectional restrictions must remain a separate advisory block. They must not be merged with endorsed UFO constraints, because the current programme’s hard-typing failure arose from treating preferences as necessities.

A plain KGE differs fundamentally:

- it treats all nodes and edges as comparable latent objects;
- it has no necessary-versus-contingent membership operator;
- it has no identity-provider semantics;
- it flattens relators into edges or undifferentiated nodes;
- it cannot distinguish quoted content from asserted content without an explicit representation;
- it can rank ontologically impossible candidates highly.

The UFO-aware embedding remains approximate retrieval machinery. It cannot replace the checker.

**Effort: L.** Approximately 4–8 engineering weeks after a gold task set exists. Without a gold set, this work would be architecture-driven feature construction with no adoption gate.

### 2.5 Sequencing

**[STIPULATED]** Use this order:

| Sequence | Work | Effort | Gate |
|---|---|---:|---|
| 0 | Freeze the CK-UFO record, proposition normalization, and evaluation schema | S | Two independent worked examples per UFO family |
| 1 | Build an ordinary-node normalization adapter and minimal rule modules | S–M | Run the cheapest experiment below |
| 2 | If the checker shows attributable lift, freeze the native triple-term inference contract | S | Parser/store/rule semantics agreed |
| 3 | Implement quoted-triple inference in `sparq-reason` | L | Text/compiled parity and non-assertion conformance |
| 4 | Implement quoted-triple vectorisation and reifier-aware provenance | M | Reconstruction and leakage gates |
| 5 | Implement the full-UFO vector prior behind an on/off ablation | L | Paired held-out lift at fixed soundness |
| 6 | Consider host integration only after the symbolic and retrieval endpoints pass | M | No change to active RULES-1 inputs |

**[STIPULATED]** The ordinary-node adapter in sequence 1 is not the destination. It is a cheap experimental normal form that lets the architecture be tested without first paying for native quoted-term inference.

## 3. Cheapest decisive experiment

### 3.1 Question

**[STIPULATED]** The first experiment asks:

> Given the same authored NSM meanings, aligned content, and structured world facts, does adding full-UFO modal, identity, relator, moment, disposition, and event checking improve the correctness of accept/reject/underdetermined decisions over the current gUFO-plus-rules stack?

It does not ask whether full UFO improves natural-language parsing, host-model reasoning, or programme-wide efficiency.

### 3.2 Dataset

**[STIPULATED]** Build 144–192 structured cases, balanced across six families:

1. Kind/Role/Phase and rigidity;
2. cross-world identity criteria;
3. object/event/trope classification;
4. relator and qua-individual dependence;
5. disposition, trigger, and manifestation;
6. events, participation, and temporal parts.

Each case contains:

- a finite set of explicit worlds or situations;
- accessibility and existence facts;
- asserted and explicitly false quoted propositions;
- one candidate conclusion;
- gold disposition: `ENTAILED`, `CONTRADICTED`, or `UNDERDETERMINED`;
- a minimal gold proof or violation explanation;
- a near-miss companion differing by one load-bearing fact.

**[STIPULATED]** Gold should be authored independently of the implementation and reconciled by two UFO-competent reviewers. Cases written by the rule author alone are insufficient because they risk making the rules trivially correct by construction.

### 3.3 Arms

| Arm | Contents | Purpose |
|---|---|---|
| A0 | Current NSM + gUFO taxonomy + existing rules engine + aligned content | Current-stack baseline |
| A1 | Representation-matched null: same proposition/reifier/world node count and graph budget, but no full-UFO rules | Controls for added structure and data volume |
| A2 | Full-UFO checker with current vector/candidate ordering | Isolates symbolic modal/identity/relator value |
| A3 | A2 with one UFO module removed per family | Attribution control |
| A4 | Full-UFO checker plus specialised UFO vectors | Gated follow-on for retrieval efficiency |

**[STIPULATED]** A0 receives the gUFO projection of each case. A1–A4 receive the full representation. A1 is essential: otherwise improvement could be attributed merely to more explicit nodes or more textual information.

### 3.4 Endpoints

**Primary correctness endpoint**

**[STIPULATED]** Paired exact disposition accuracy over held-out cases:

```text
correct ENTAILED / CONTRADICTED / UNDERDETERMINED classification
```

Supporting endpoints:

- dangerous false-accept rate;
- unsupported rejection rate;
- underdetermination calibration;
- proof validity;
- family-level exactness;
- counterfactual sensitivity on the near-miss pairs;
- failure-code correctness;
- module-removal attribution.

**Go rule**

**[STIPULATED]** Proceed to native upstream implementation only if A2:

- exceeds A0 by at least 10 percentage points;
- has a one-sided paired 95% lower bound above zero;
- does not increase dangerous false acceptance;
- produces valid proof/violation records on at least 98% of its non-refusal decisions;
- retains at least 80% judgeable coverage;
- beats A1, so graph enrichment alone does not explain the result;
- loses the relevant family-specific gain when the corresponding A3 module is removed.

**No-go rule**

**[STIPULATED]** Do not build the native full stack if:

- A2 does not beat A0;
- A1 matches A2;
- gains arise only by converting underdetermined cases into unsupported hard answers;
- proof validity fails;
- module removal does not affect the purported mechanism;
- results depend on closing scopes that the input does not legitimately declare closed.

### 3.5 Efficiency follow-on

**[STIPULATED]** Only after the correctness gate, run A2 versus A4 on candidate-retrieval tasks with the same gold answer and candidate universe.

Measure:

- candidates inspected before the first licensed answer;
- recall at fixed candidate budget;
- reasoner calls;
- p50/p95 latency;
- vector memory;
- closure and index build cost.

A provisional efficiency go rule is at least a 25% reduction in candidates inspected or 20% reduction in p95 end-to-end latency, with non-inferior exactness and dangerous-error rate.

### 3.6 Cost

**[EXTRAPOLATION]** The symbolic experiment is a medium effort: roughly 1–3 engineering weeks plus several reviewer-days, with negligible compute cost and no required GPU. The expensive part is credible gold and counterexample authoring.

**[EXTRAPOLATION]** The A4 vector follow-on is another medium effort and should remain below low hundreds of dollars in compute on the existing shallow-KGE harness. Native production implementation is large even if the experiment is cheap.

## 4. Honest feasibility and risk

### 4.1 Principal difficulties

**[DERIVED]** Full UFO is not merely a richer taxonomy. Its load-bearing content is modal, identity-theoretic, dependence-based, and partly higher-order. Any RDF implementation that retains only class names recreates gUFO’s central limitation.

**[DERIVED]** A finite-world checker can validate supplied witnesses but cannot prove unrestricted reference-UFO rigidity, anti-rigidity, counterfactual disposition semantics, arbitrary identity criteria, unrestricted fusion, or general modal/deontic validity.

**[STIPULATED]** The architecture must therefore expose three boundaries on every commitment:

```text
reference-UFO
executable finite profile
reference-only residue
```

**[DERIVED]** Identity criteria are usually domain commitments, not something the foundational ontology can supply automatically. A Person, Corporation, Contract, Disease episode, and Software process may require different criteria. Incorrect identity rules are more dangerous than missing ones because they can merge records and contaminate all downstream inference.

**[DERIVED]** Relators and qua-individuals expand the graph substantially. That expansion may improve explanation and validation, or it may impose annotation and runtime costs without affecting any task endpoint.

**[DERIVED]** Specialised embeddings can appear successful merely because hard masks encode the answer space. Efficiency reporting must distinguish neural ranking from symbolic elimination and report candidate-set sizes.

**[DERIVED]** Modal validation is particularly vulnerable to illegitimate closure. “No counterworld was supplied” must never become “no counterworld exists” unless the scope is explicitly declared complete.

**[DERIVED]** An authored benchmark can become circular if the same people write the UFO rules, examples, and gold. Independent reconciliation and module-removal controls are load-bearing.

**[DERIVED]** Current vector type constraints combine declared and observed domain/range information. That is useful for KGE sampling but dangerous for ordinary meaning if observed preferences acquire hard ontological authority.

### 4.2 Dead-end conditions

**[STIPULATED]** Treat the direction as a dead end for this programme if any of the following holds:

- the full-UFO checker does not improve held-out disposition accuracy over A0 and A1;
- nearly all gains come from extra authored facts rather than inference;
- credible use cases cannot supply accessible worlds, identity evidence, relators, or closed scopes;
- reviewer agreement on the UFO mappings is too low for a stable kernel;
- the system mostly abstains where the current stack already answers;
- specialised vectors do not improve retrieval after checker value is established;
- graph and authoring cost dominates the saved model or verification work;
- full-UFO rules cannot remain modular, proof-carrying, and fail-closed;
- the architecture requires silently treating bounded finite validation as reference-UFO theorem proving.

### 4.3 Start now or defer

**[DERIVED]** RULES-1 host lift and g2-import are the programme’s current immediate evidence gates. RULES-1 has established CPU-side non-inertness but not host benefit or kernel-specific rule-source value. g2-import is built but unrun and addresses the current hard-typing failure more directly.

**[STIPULATED]** Do not modify, delay, or widen either active experiment to incorporate CK-UFO. Doing so would change their inputs and weaken attribution.

**[STIPULATED]** Start only a thin CK-UFO spike now:

- freeze the record schema;
- author a small gold set;
- implement the ordinary-node proposition adapter;
- implement minimal modal/identity/relator rules;
- run the CPU-only A0–A3 experiment.

This is useful parallel preparation because it tests the distinctive full-UFO mechanism without requiring native SPARQ changes.

**[STIPULATED]** Defer native quoted-triple inference, reifier-aware KGE work, and the specialised full-UFO encoder until the CPU experiment passes and the active RULES-1/g2-import evidence is read.

**[EXTRAPOLATION]** This staged posture has the best information-to-cost ratio: it spends first on whether full UFO changes decisions, not on whether SPARQ can elegantly implement an architecture whose task value remains unknown.

## Closing position

**[STIPULATED]** CK-UFO is a coherent candidate architecture because it places full UFO exactly where the current stack is weakest: modal membership, identity, dependence, relators, qua-individuals, moments, dispositions, and events. It preserves NSM as authored meaning, uses vectors for proposal and ordering, and gives final authority to a bounded, proof-carrying checker.

**[DERIVED]** The required SPARQ substrate is partly present: RDF 1.2 triple terms are stored correctly, the rules engine already supplies OWL-RL/N3/Datalog components, and the vector estate already has closure, taxonomy, SHACL, provenance, KGE, and ablation seams. Native structural inference and learning over quoted terms, and a genuine UFO prior, are missing.

**[STIPULATED]** The justified action now is the bounded CPU experiment and schema spike, not immediate construction of the full upstream stack.

CORRECTNESS and EFFICIENCY remain **INCONCLUSIVE-PENDING**.