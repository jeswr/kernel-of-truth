# Design record — the constraint/axiom layer (formalism audit + design)

**Status:** design proposal, 2026-07-08. Answers the maintainer's standing worry about
the "OWL/constraint layer": is the kernel missing a logical-constraint formalism, and
if so what should it be?
**Author:** formalism-audit agent (Claude Fable 5), for @jeswr.
**Litmus example (maintainer's):** *"a human has exactly two parents, one male and one
female."*
**Inputs read:** encoder/src/{lexicon,ast,validate}.ts; data/kernel-v0/ (records +
README + minted-urns); data/molecules-v0/; data/lexical-wn31/, data/onto-obo/,
data/onto-sumo/ (bulk-tier record shapes + manifests); docs/design-hash-input.md,
docs/design-molecule-tier.md, docs/design-math-sector.md, docs/design-bulk-kernel.md,
docs/architecture.md; notes/mandate.md, notes/panel-kernel-design-review.md;
reports/sparq-estate.md; ../concept-gist/concept-hash-design.md (the external gist).
**Honesty contract:** [established] / [claimed] / [open] tags; every repo claim was
verified against the files on disk on 2026-07-08.

---

## 0. Summary of the answer

1. The kernel today has **no logical-constraint layer**: no kernel-v0 record carries an
   axiom (verified — zero `axioms` fields across all 54 records); molecules-v0 ships
   `axioms: []` on every record; the encoder scopes axioms out **by design**
   (encoder/src/ast.ts header). The OWL-ish axiom vocabulary
   (`subClassOf/…/disjointWith/restriction`) exists only in the external gist and is
   unimplemented and unconsumed in this repo. The litmus example has **no representable
   machine-checkable form today** (§1.4).
2. One important nuance the simple statement misses: the **bulk tiers minted this week
   do carry `axioms` arrays inside their content-hashed identity** (lexical-wn31:
   269,960 hypernym/meronym/antonym edges; onto-obo: `is_a`, `domain`, `range`,
   `inverse_of`, `disjoint_from`; onto-sumo: raw KIF including `=>` rules). These are
   hashed **structure with no pinned semantics and no checker** — a latent debt this
   design addresses (§2.3).
3. Judgement (§2): the absence is a **deliberate, documented scoping decision** at v0
   (mandate's explicit world-layer deferral; ast.ts scope note; molecule-tier rule-2
   deferral; panel verdict "RESIDUAL RISK ACCEPTED"), **not** an oversight — but it
   becomes a genuine **loss of formalism at exactly three pressure points**: the A5
   verifier tier's "meaning-level verification" claim, the world layer (whenever it
   stops being deferred), and the legal/regulatory/safety scope claim, whose vocabulary
   is constraint-shaped.
4. Design (§3): a **native closed axiom grammar `kot-axiom/1`** — a small typed JSON
   AST with SHACL-core-equivalent closed-world operational semantics, hashed under the
   programme's JCS discipline, projected deterministically to SHACL (and OWL 2 for
   interop), attached as **separately-hashed sidecar records that reference the concept
   URN** (identity of an Explicated concept does not change). A decisive technical fact
   drives the formalism choice: the litmus example is expressible in **no tractable
   OWL 2 profile** (EL/QL/RL all exclude exact/qualified cardinality) — only in full
   OWL 2 DL, whose open-world semantics cannot *check* an instance record anyway
   without closure gymnastics, at N2EXPTIME-complete reasoning cost. SHACL-shaped
   closed-world validation states it directly and checks it in linear-ish local passes,
   matching every fail-closed gate already in the estate.
5. Vectorisation coupling (§4): **verifier-not-in-the-vector.** Constraints must NOT be
   folded into the canonical concept vector. The X3 pathology is the proof-by-existing-
   measurement: a single deep NOT moves the vector ~1/s of its norm while inverting
   meaning; a `max 2 → max 3` edit would be geometrically negligible and semantically
   load-bearing. Constraints are discrete, machine-checkable objects; their entire
   value is checkability, which vector superposition destroys. The vector's URN is
   already the pointer; the snapshot binds URN → endorsed axiom set.
6. Hypothesis impact (§5): "can't-misunderstand" as originally stated is already
   [contradicted] (architecture.md §2 C1); its **surviving form — verification at the
   interface — requires this layer** to be more than structural for profile-1
   concepts. The constraint layer does **not** gate the E1–E4 kill chain (vector-level
   questions are unaffected), but E9's assurance-tier claims should gain a
   constraint-violation arm: it is the one delta that survives the panel's deflationary
   gloss-file baseline, because definition *text* cannot be cardinality-checked.

---

## 1. What is expressible today — the audit

### 1.1 The explication AST: a definitional scenario language, not an axiom language

The profile-1 explication grammar (gist §4; typed mirror `kot-ast/1` in
encoder/src/ast.ts) expresses exactly: a typed **frame** (`InstanceSchema` /
`WhenTrue` / `RelationalSchema`), a list of **indexed discourse referents** with kinds
(`SomeoneRef/SomethingRef/TimeRef/PlaceRef/ClauseRef`), and an **ordered clause list**
over the 65-prime lexicon — predicate clauses with closed valency frames, operator
clauses (`NOT/CAN/MAYBE/IF/BECAUSE/WHEN/LIKE/AFTER/BEFORE/VERY/MORE`), substantive
phrases with closed determiners/quantifiers/modifiers, quote re-anchoring, and
references to other concepts' URNs (encoder/src/lexicon.ts, encoder/src/ast.ts)
[established — by inspection].

Within that, the only constraint-*like* machinery that exists:

| Mechanism | What it constrains | Constraint class it approximates |
|---|---|---|
| **Valency frames** (lexicon.ts `PREDICATE_FRAMES`) | each predicate's roles: required/optional, filler kind (`entity/clause/quote/attributeGoodBad/firstPerson/…`); each role fillable **at most once** per clause | per-role **functionality** and a crude **range** (filler-kind sorting) — but over *explication syntax*, not over instances of the concept |
| **Referent kinds** (`RefKind`) | a referent is a someone/something/time/place/clause | a 5-sort **domain/range** discipline for the explication's own variables |
| **Frame types** | `RelationalSchema` fixes referents 1,2 = subject/object instances | an implicit domain/range *slot*, without the ability to say *which concept* the slots range over |
| **SP quantifiers** (`ONE/TWO/SOME/ALL/MUCH~MANY/LITTLE~FEW`) | quantity inside a scenario ("two someones") — used in the corpus (e.g. kind.json carries `quant: TWO`) | **cardinality as narrative content**, not as a checkable bound (see below) |
| **NOT / IF / CAN operators** | clause-level negation, conditionality, possibility inside the scenario | **negation/disjointness as narrative content** only |
| **Caps** (≤32 clauses/referents, depth ≤12) | record size | none (these are gate constraints on records, not on concept extensions) |

The load-bearing distinction, stated once and precisely:

> An **explication** is a *definitional* artifact: a canonical, stipulated scenario
> text answering "what does concept C mean?" (architecture.md §1.0's stipulative
> posture; gist §1 claim 3: adequacy "social, not proven"). An **axiom** is an
> *ontological* artifact: a claim about C's **extension** — "what must be true of
> every/any instance record asserted to be a C" — that a checker can evaluate against
> instance data and reject violations of.

Profile-1 can *say* "two someones did something; because of this, this someone is
alive" inside a `parent`/`birth` explication — the corpus's birth.json is in exactly
this register. That clause is **scene description**. Nothing consumes it as a bound:
there is no semantics under which a world-layer record listing three parents
*contradicts* it, no closed-world convention under which listing one parent *violates*
it, and no checker that would evaluate either. The SP quantifier `TWO` contributes
codebook atoms to a vector and bytes to a hash; it never contributes a **truth
condition** [established — no consumer exists anywhere in encoder/, poc/, mapper/,
tools/].

### 1.2 What is NOT expressible (the missing constraint classes)

Against the standard constraint inventory, profile-1 as implemented can state **none**
of the following *as machine-checkable claims about a concept's extension*:

1. **Cardinality** — min/max/exact, qualified or not ("exactly 2 parents"; "exactly 1
   male parent"). The gist's axiom vocabulary reserves `restriction` with
   "restriction cardinalities" in the literal whitelist (gist §5) and even pins a
   golden vector for a "cardinality-restriction bnode tree" (gist §12 vector 4) — but
   that machinery lives in `@jeswr/concept-hash` outside this repo, defines only how
   such an axiom would be *hashed*, never what it *means* or how it is *checked*, and
   no kernel-side record uses it.
2. **Domain/range** at concept granularity — "parent-of relates humans to humans."
   `RelationalSchema` gives typed *slots*; it cannot name the concept each slot ranges
   over. (The gist's `domain`/`range` axiom relations exist in the same
   specified-but-unconsumed state; onto-obo's ingestion carries 147 `domain` + 135
   `range` edges as inert data — §2.3.)
3. **Disjointness** — "nothing is both male and female (in the stipulated sense)."
   `disjointWith` is in the gist vocabulary and in 30 onto-obo `disjoint_from` edges;
   nothing evaluates it. Notably the **sparq estate already has a working consumer
   pattern** for exactly this: `DisjointnessOracle` mines `owl:disjointWith` /
   `owl:complementOf`, propagates through the subclass closure, and serves an
   answer-safe hard mask (reports/sparq-estate.md §1.1(d)) — machinery this design
   reuses at the decode/verify boundary (§4.3).
4. **Functionality / inverse-functionality** — "has-birth-mother has at most one
   value." Again sparq has the consumer shape: `shacl_priors.rs` maps `sh:maxCount 1`
   / `owl:FunctionalProperty` to `Cardinality::Functional` = one deterministic vector
   slot (sparq-estate.md §4) — but that is *lane layout*, not validation, and it lives
   in the neighbouring estate, not the kernel.
5. **Subclass as a checkable axiom** — kernel-v0 expresses class membership
   definitionally (kind-frame heads over concept refs, data/kernel-v0/README.md
   "kind-frame heads … for class membership"), which affects the *vector and hash*,
   not any subsumption check. The bulk tiers carry `hypernym`/`is_a` edges as inert
   identity payload.
6. **Property characteristics** (transitive, symmetric, inverse) — present in
   onto-obo's extraction (`transitive_over`, `inverse_of`, `holds_over_chain`), absent
   from any kernel formalism.

### 1.3 Where axiom-shaped things DO exist in the estate (the honest map)

| Location | Shape | Semantics? | Checker? | Consumed by? |
|---|---|---|---|---|
| Gist §5 axiom vocabulary (`cdef:rel ∈ {subClassOf, subPropertyOf, domain, range, disjointWith, metaType, propertyKind, restriction, bridgesTo}`) | RDF bnode axiom nodes inside the D1 hash boundary | **none pinned** (hashing rules only) | shape/caps gates only | nothing in this repo [established — panel 1.3 concurs] |
| kernel-v0 (54 records) | `{id,label,status,pattern?,gloss,notes?,references,explication}` — **no axioms field at all** | — | — | encoder, Phase-X, E-series |
| molecules-v0 (54 records) | `axioms: []`, `partialExplication: null` on every record (rule-2 deferral, design-molecule-tier.md §3) | — | — | mapper measurement only |
| lexical-wn31 (117,791 records, **minted `urn:kot:`**) | `kot-lex/1`: `axioms` **inside the identity payload** — hypernym/hyponym/meronym/antonym/similarTo/entailment/cause (269,960 edges) | none — manifest: "structural axioms … NO semantic-adequacy claim" | extractor validation only | pack-format prototypes (tools/pack/proto-kotk*) round-trip the bytes; nothing evaluates the edges |
| onto-obo (BFO/RO/GO) | `is_a`, `domain`, `range`, `inverse_of`, `transitive_over`, `disjoint_from`, `holds_over_chain` | none | none | nothing |
| onto-sumo | raw canonical KIF (`instance`, `subclass`, `=>` rules, `domain`…) | none (KIF preserved as strings) | none | nothing |
| **math sector** (profile-M, data/math-v0) | `AxiomDef` frame: closed `Prop`-sorted statements over a pinned FOL basis (design-math-sector.md §3.2) | **yes — the one real axiom semantics in the programme** (many-sorted FOL, basis in the profile bundle) | full sort/scope checker (validate.mjs) | validator; no proof layer (L1) |
| sparq (Rust estate) | SHACL/OWL priors: `sh:maxCount 1`/functional → one slot; `sh:in` → codebook; `owl:disjointWith` → oracle/masks | operational (lane layout + masking) | yes, fail-open per-predicate | sparq vector lanes, candidate masking |

The pattern: **hashing machinery for axioms exists; extraction machinery exists;
consumption semantics exist only in profile-M (for FOL statements) and in sparq (for
someone else's data model). The kernel's own concepts have neither axioms nor a
language to state them in.**

### 1.4 The litmus test, run honestly

*"A human has exactly two parents, one male and one female."* Decompose and check:

- **The concepts:** `human` — not in kernel-v0; `man/woman/mother/father/child` exist
  as molecules-v0 grounding notes (`urn:molecule-v0:*`, not encoder-referenceable —
  design-molecule-tier.md §4). `parent-of` — authorable today as a profile-1
  `RelationalSchema` explication (a scenario: "this someone did something before this
  other someone was alive; because of this, this other someone is alive…" — same
  register as birth.json). So the *definitional* halves are reachable or nearly so.
- **"exactly two":** unstatable. No construct expresses a bound; SP `TWO` is scene
  content (§1.1); "exactly" additionally requires a closed-world reading ("and no
  more") that no layer of the system defines. Even *narratively* smuggling "not more
  than two" via `NOT + MORE` clauses would produce bytes the encoder happily vectorises
  and nothing ever evaluates.
- **"one male and one female" (qualified cardinality):** doubly unstatable — needs the
  cardinality construct *and* class-qualified counting.
- **male/female disjointness:** unstatable. One can author disjoint-*looking*
  explications; no checker can use them to reject a record asserting both.
- **checking an instance:** there is no world layer to check (mandate: deferred) and
  no validation procedure to check it with.

**Verdict [established]: no representable machine-checkable form exists today, at any
layer of this repo.** The nearest artifacts are (a) a profile-1 scenario paraphrase
(definitional, uncheckable), and (b) a hypothetical gist-vocabulary axiom record
(hashable, semantics-free, and only in the external prototype).

---

## 2. Loss or scoping decision? — the judgement, with citations

### 2.1 It was decided, repeatedly and on the record

1. **The mandate defers the world layer explicitly**: "a larger layer above holds
   formally described world-facts … For now, assume facts in the world layer are true;
   qualification/accuracy handling is deferred by explicit decision" (notes/mandate.md,
   maintainer's framing). Constraints on instances are world-layer machinery; deferring
   the layer deferred its schema language.
2. **The encoder scoped axioms out by design**: "the wider definition record (axioms,
   semantic status, annotation layer) is the identity layer's business (gist §5) and is
   out of the vector encoder's scope by design" (encoder/src/ast.ts header).
3. **The molecule tier deferred partial explications and axioms**: "Rule 2 (partial
   explications) is deferred in v0 — records carry `axioms: []`" (design-molecule-tier.md §3).
4. **The design review examined exactly this and accepted the risk**: lens 1.3, "the
   ontology axiom vocabulary is OWL heritage with no current consumer" — verdict
   **RESIDUAL RISK ACCEPTED**, with the guard that AxiomsOnly records are never counted
   as "kernel concepts the LLM benefits from" (notes/panel-kernel-design-review.md).
   The same review convicted the *reflex* ("an ontology person reaches for subClassOf
   because ontologies are made of it; nothing in the E-series consumes it") while
   accepting the current scoping.
5. **The gist itself keeps semantics out of identity deliberately**: identity is the
   stated form; entailment-normalisation rejected (gist §13 Q1); the codegen companion
   treats OWL/SHACL as *projections* (gist §10).

So: **a deliberate scoping decision, not an accident.** The programme's own paper
trail is unusually clean on this.

### 2.2 …but it matures into a real loss at three pressure points

**(i) The surviving form of "can't-misunderstand."** C1 as stated is [contradicted];
what survives is *detectable and correctable at the interface* (architecture.md §2).
The A5 verifier's honest scope today is: "mechanical in the formal sectors
(dimensions, sorts), *structural* in profile-1, social for adequacy" (panel 2.5;
architecture.md §1.0 rev 3). Structural verification catches malformed explications
and hash mismatches; it cannot catch a *world-layer assertion that contradicts the
concept's stipulated shape* — three parents, a male mother, a bookmark archived by
nobody. Those are exactly the "meaning-level errors passage retrieval cannot catch"
that A5's pitch claims (architecture.md §4 A5 delta ii). Without a constraint layer,
that claim is only redeemable in profile-M/P. **For profile-1 concepts the claim is
currently unbacked** [established by §1.4].

**(ii) The world layer.** The moment world-layer records exist ("Jesse as a person:
birth, parents…" — the mandate's own example), they need a schema language, and every
candidate fact in the mandate's example sentence is constraint-shaped (birth: exactly
one; parents: exactly two, per the maintainer's own litmus). Deferring qualification
was decided; shipping a world layer with *no validation vocabulary at all* was not.

**(iii) The scope claim.** The kernel's declared sweet spot is
"definitional/abstract/relational vocabulary … legal, regulatory, safety, interop"
(architecture.md §3, panel O4). That register is *made of* stipulated constraints
("a valid consent record has exactly one data subject"; "these categories are mutually
exclusive"). A kernel that can stipulate meanings but not obligations covers half the
register it is pitched at.

**(iv) (Latent, new finding)** The bulk tiers have begun **hashing axiom structure
without pinned semantics**: 269,960 WordNet edges, OBO's `disjoint_from`/`domain`/
`range`, SUMO's `=>` rules are all inside minted `urn:kot:` identities today. That is
fixity of *reference* applied to relations whose *meaning* no artifact defines — the
exact "meaning-under-a-name" pattern in miniature, one layer up. Harmless while
nothing consumes them; a silent fork risk the day two consumers interpret `is_a`
differently. The constraint layer should pin the operational semantics these edges get
(or explicitly mark a corpus's axioms "structural edges, no logical semantics" — the
right answer for wn31's lexical relations, the wrong one for OBO's `disjoint_from`).

**Judgement: deliberate scoping at v0, correctly prioritised (nothing in the E1–E4
kill chain needs axioms); genuine formalism loss on the A5/world-layer/regulatory
axis, which is precisely the axis the programme's assurance pitch monetises. Build it
as a v1 sidecar layer — not because OWL-heritage completionism demands it, but because
the verifier tier's headline claim is unredeemable without it.**

---

## 3. The design: `kot-axiom/1` — a native closed axiom grammar

### 3.1 Requirements (inherited from the estate's own discipline)

R1. State: qualified/exact cardinality, domain/range, disjointness, functionality,
    subclass, inverse — the litmus example and its obvious neighbours.
R2. **Decidable, syntax-directed, linear-ish checking** — a validator, never a theorem
    prover, in the mint gate *and* in the instance checker (the profile-M requirement
    §2.1, verbatim).
R3. **Closed grammar + caps**, content-addressed under the JCS discipline
    (design-hash-input.md), fail-closed `ERR_*` gates (CLAUDE.md conventions).
R4. **Closed-world validation semantics** against declared record sets — the kernel
    validates *records*, never reality (mandate: world-layer truth is assumed;
    validation checks internal consistency of what is asserted).
R5. Deterministic **projections** to SHACL and OWL 2 for estate interop — projections,
    never the hash input (the design-hash-input.md posture, applied again).
R6. Attachment must not destabilise concept identity or the E-series pins.

### 3.2 Formalism comparison — why not OWL, why not raw SHACL, why native

**OWL 2 DL.** Expresses the litmus example elegantly:

```
SubClassOf( :Human  ObjectExactCardinality( 2 :hasParent :Human ) )
SubClassOf( :Human  ObjectExactCardinality( 1 :hasParent  ObjectIntersectionOf( :Human :Male ) ) )
SubClassOf( :Human  ObjectExactCardinality( 1 :hasParent  ObjectIntersectionOf( :Human :Female ) ) )
DisjointClasses( :Male :Female )
```

Three disqualifiers [established — standard results]:
(a) **Open-world semantics cannot check.** An instance listing one parent is not
inconsistent under OWL semantics — merely incomplete; detecting the violation requires
closure axioms or NAF bolted on, i.e. abandoning the semantics you imported OWL for.
Validation-shaped goals fit OWL like a glove on the wrong hand — this is the exact
mismatch that produced SHACL historically.
(b) **No tractable profile survives R1.** OWL 2 EL, QL and RL all exclude
exact/qualified cardinality (RL admits `maxCardinality 0/1` in superclass position
only). The litmus example forces **full OWL 2 DL**, where reasoning is
N2EXPTIME-complete (SROIQ) — a theorem prover in the gate, the precise thing
profile-M's Lean analysis (design-math-sector.md §2.4) already rejected once, for the
same reason.
(c) **Ecosystem, not kernel.** The panel's 1.1 finding applies verbatim: OWL-form
axioms would be a second serialisation with no computing consumer; the JCS decision
already demoted RDF to projection.

**SHACL (as the normative language).** SHACL-core states the example *directly* and
checks it under closed-world, per-focus-node semantics:

```turtle
:HumanShape a sh:NodeShape ; sh:targetClass :Human ;
  sh:property [ sh:path :hasParent ; sh:class :Human ;
                sh:minCount 2 ; sh:maxCount 2 ] ;
  sh:property [ sh:path :hasParent ;
                sh:qualifiedValueShape [ sh:class :Male ] ;
                sh:qualifiedMinCount 1 ; sh:qualifiedMaxCount 1 ] ;
  sh:property [ sh:path :hasParent ;
                sh:qualifiedValueShape [ sh:class :Female ] ;
                sh:qualifiedMinCount 1 ; sh:qualifiedMaxCount 1 ] .
:MaleShape a sh:NodeShape ; sh:targetClass :Male ; sh:not [ sh:class :Female ] .
```

`sh:qualifiedValueShape` + `qualifiedMin/MaxCount` is purpose-built for "one male,
one female"; validation is local and cheap; SHACL 1.2 Core is an active W3C
Recommendation-track Working Draft (June 2026 — [w3.org/TR/shacl12-core](https://www.w3.org/TR/shacl12-core/)),
and the maintainer's estate is already SHACL-dense (gist shape gates, sparq
`shacl_priors.rs`, the codegen SHACL projection, the separate SHACL-CS-1.2 programme).
But adopting *RDF-serialised SHACL as the normative, hashed form* would re-import
everything design-hash-input.md just removed: bnode-tree ceremony, a second
serialisation as the computed-over form, dual-validator drift (panel 1.1.4). It would
also admit SHACL's open-ended feature surface (SPARQL constraints, recursion —
undefined in SHACL 1.0 and a genuine semantic swamp) unless separately capped.

**SHACL-plus-DL hybrid** (OWL axioms for documentation/inference + SHACL for
validation): two normative semantics for one constraint is a standing divergence
surface — rejected for the same reason dual validators were.

**Decision [claimed, recommended]: a native closed axiom grammar, `kot-axiom/1` — a
typed JSON AST whose constructs are a curated subset of SHACL-core's semantics,
defined over `urn:kot:` concept references, hashed under the JCS+profile-header
discipline, with deterministic SHACL and OWL 2 projections.** This is the third
instance of the programme's established move (kot-ast/1 : profile-1 RDF form ::
pm-ast/1 : eventual RDF form :: **kot-axiom/1 : SHACL/OWL projections**), and the
panel's 1.1 logic transfers unchanged: the canonical form is the AST you compute over;
interop forms are projections.

### 3.3 The grammar (v0, normative sketch)

**Record envelope** (one record = one subject concept's constraint set):

```json
{
  "schema": "kot-axiom/1",
  "subject": "urn:kot:<concept>",
  "constraints": [ Constraint, ... ]
}
```

**Closed constraint inventory** (v0 — deliberately minimal; every addition is a
profile version change):

| Construct | Fields | Operational semantics (per instance record `x` asserted to be a `subject`) |
|---|---|---|
| `subClassOf` | `target` | every `x` must also validate against `target`'s constraint set; contributes the subclass closure used by `disjointWith` and qualifiers |
| `disjointWith` | `target` | `x` must not be asserted (directly or via subclass closure) an instance of `target` |
| `domain` | (subject is a relational concept) `target` | every asserted `subject(a,b)`: `a` must be asserted a `target` |
| `range` | `target` | every asserted `subject(a,b)`: `b` must be asserted a `target` |
| `inverseOf` | `target` | `subject(a,b)` ⟺ `target(b,a)` is checked both ways over the closed record set |
| `functional` | — | at most one asserted `subject(a, ·)` per `a` (sugar for `cardinality max 1` on the domain side) |
| `cardinality` | `path` (relational-concept URN), `direction` (`"forward"` \| `"inverse"`), `min?`, `max?`, `qualifier?` (concept URN) | count asserted path-edges from `x` (in the stated direction) whose far end is asserted a `qualifier` (or all edges if absent); require `min ≤ n ≤ max`; **exact k = min=max=k** |

**Caps (conformance-defining):** ≤ 32 constraints per record; ≤ 8 cardinality
constraints per path; qualifier nesting depth = 1 (a qualifier is a concept URN,
never an inline class expression — no boolean combinators in v0: intersection is
expressed by minting the intersection concept if genuinely needed, mirroring
profile-M's "schema instances minted per sort" austerity, L2); `min,max ≤ 64`; all
URNs decode-validated. **No negation-as-constraint, no property chains, no closed
`oneOf` in v0** — each is a recorded candidate for v1, none is needed by the litmus
class, and each expands the checking semantics nonlinearly.

**Semantics pinned as a validation procedure, not a model theory:**
`validate(recordSet, axiomSet) → { conformant | violations[] }` where `recordSet` is a
declared, closed set of world-layer assertions (the closure discipline — which
subclass/inverse closure is materialised first — is pinned in the profile bundle,
exactly as sparq materialises its RDFS/OWL-RL closure before vectorisation,
sparq-estate.md §1.1(f)). Complexity: per-focus-node local checks over a fixed closure
= linear-ish in assertions, no search [established for this construct set — it is a
strict subset of SHACL-core minus recursion]. Fail-closed `ERR_*` codes throughout.
**Stated honestly:** this is CWA validation of *asserted records*. It finds
contradictions and incompletenesses in what is written down; it never certifies
reality (the mandate's assumed-true deferral is untouched).

### 3.4 The litmus example, encoded

Assume minted concepts `human`, `has-parent` (child→parent relational concept, the
authoring-friendly direction; `parent-of` is its inverse), `male`, `female` (as
stipulated sex-classification concepts — see the honesty note below).

```json
{ "schema": "kot-axiom/1",
  "subject": "urn:kot:<human>",
  "constraints": [
    { "kind": "cardinality", "path": "urn:kot:<has-parent>",
      "direction": "forward", "min": 2, "max": 2,
      "qualifier": "urn:kot:<human>" },
    { "kind": "cardinality", "path": "urn:kot:<has-parent>",
      "direction": "forward", "min": 1, "max": 1,
      "qualifier": "urn:kot:<male>" },
    { "kind": "cardinality", "path": "urn:kot:<has-parent>",
      "direction": "forward", "min": 1, "max": 1,
      "qualifier": "urn:kot:<female>" } ] }

{ "schema": "kot-axiom/1",
  "subject": "urn:kot:<male>",
  "constraints": [ { "kind": "disjointWith", "target": "urn:kot:<female>" } ] }

{ "schema": "kot-axiom/1",
  "subject": "urn:kot:<has-parent>",
  "constraints": [
    { "kind": "domain",    "target": "urn:kot:<human>" },
    { "kind": "range",     "target": "urn:kot:<human>" },
    { "kind": "inverseOf", "target": "urn:kot:<parent-of>" } ] }
```

The SHACL projection is exactly the Turtle in §3.2; the OWL projection is exactly the
functional syntax in §3.2, emitted with a stated caveat that the OWL rendering is
documentation/interop (OWA) while the normative semantics is the kot-axiom validation
procedure (CWA). **Honesty note, load-bearing:** this axiom set is *contestable world
modelling* (adoptive parents, biological-vs-legal parenthood, intersex people are all
counterexamples under some readings). That is not a defect of the formalism — it is
the reason axioms belong under **endorsement governance and outside concept identity**
(§3.5): federations that stipulate differently endorse different axiom sets over the
*same* concept, instead of forking the concept.

### 3.5 Attachment and hashing: separately-hashed sidecar, identity unchanged

**Decision [claimed, recommended]:** a `kot-axiom/1` record is a **first-class,
content-addressed record with its own `urn:kot:` URN** (JCS + NFC + profile header
`kot-axiom/1\n`, per design-hash-input.md — the machinery applies unchanged since the
record is a small tree with URN references). It **references** the subject concept's
URN; the concept's identity payload is **not** touched. Binding is by **snapshot**:
the federation snapshot manifest (gist §8's lockfile object) carries
`{conceptUrn → [endorsed axiomRecordUrns]}` entries, and endorsement of an axiom set
is a governance act exactly like endorsement of a concept.

Why sidecar and not inside the concept hash — four arguments:

1. **Different change velocities, different disputes.** A concept's stipulated meaning
   ("what `human` means") and claims about its extension's structure ("how many
   parents humans have") evolve on different schedules and are contested by different
   communities. Folding axioms into identity makes every axiom revision a re-mint —
   the Merkle avalanche (gist §8) triggered by world-modelling churn — and makes every
   axiom disagreement a *fork of the concept itself*: two federations disagreeing
   about adoptive parents would mint two `human`s that no longer co-reference. Fixity
   of reference is the programme's one unconditional claim; axioms-inside-identity
   spends it on its most contestable content.
2. **The E-series and encoder pins survive untouched.** Concept URNs, canonical
   vectors, X0 goldens, minted-urns.jsonl — all unchanged (R6). Axioms-inside would
   re-mint all 54 kernel-v0 records the day the first axiom is authored.
3. **Precedent inside the estate.** Upgrade edges, endorsements, embedding tables and
   bridges are all "signed/content-addressed claims *about* a hash, outside it" (gist
   §8–§9). Axioms-about-extensions are the same species of claim. Note this is
   *stronger* than a mutable annotation: the axiom record is itself immutable and
   content-addressed; only the *binding* (which axiom set a federation endorses for a
   concept) is governance.
4. **Reconciliation with the gist's D1 boundary, stated precisely.** The gist puts
   `cdef:axiom` **inside** the hash. That remains correct for records whose axioms
   *are* their definition — the AxiomsOnly bulk tier (a WordNet synset's identity
   *is* its relational position; lexical-wn31 already ships this and it is right).
   The rule that harmonises both: **axioms constitutive of the stipulated meaning may
   live inside identity (AxiomsOnly records, and any author who deliberately wants a
   constraint to be meaning-constitutive); constraints on the extension of an
   Explicated concept live in the sidecar.** The author chooses at mint time which
   claim they are making; the profile makes the choice legible (`semanticStatus`
   already distinguishes the record classes). This is a *scoping* of the gist's
   device, not a contradiction of it — and it is PSS-visible turf: flag it on
   sparq#1683 alongside the JCS dual-hash question, since the gist's estate-side
   records would carry the same distinction.

**Consequence for the bulk-tier debt (§2.2-iv):** when kot-axiom/1 exists, onto-obo's
`domain/range/disjoint_from/inverse_of` edges get a deterministic lowering into
kot-axiom records (an extractor pass, provenance-stamped per design-bulk-kernel.md);
wn31's lexical relations are explicitly declared "structural edges, no kot-axiom
semantics" in the corpus README; SUMO's `=>` rules stay out of scope (rule territory,
not constraint territory — recorded, not smuggled).

---

## 4. Vectorisation coupling: verifier-not-in-the-vector

**Question:** should constraints be vectorised into `v(c)`, or kept as a
machine-checkable logical sidecar the vector merely points at?

**Answer [claimed, with the argument]: sidecar. Do not vectorise constraints. The
concept URN is already the pointer; no new vector machinery is warranted.**

1. **The geometry argument (from the programme's own measurements).** Construction B's
   similarity is structural overlap; X3 established that one deep NOT moves a vector
   ~1/s of its norm while inverting meaning (afraid↔NOT-afraid at cos 0.9999 —
   poc/results/x3, cited in panel 3.2), which is why cosine is banned downstream.
   Constraint content is the *worst possible* cargo for that geometry: `max: 2` vs
   `max: 3`, `disjointWith` present vs absent, `min` vs `max` are single-atom edits
   with total semantic inversions. Vectorised axioms would be bytes the geometry
   cannot honour — all of the X1/X3 pathology surface, none of the compositional
   payoff. The math sector already recorded the same conclusion for quantifier flips
   (design-math-sector.md §4 pathology 1).
2. **The checkability argument.** The entire value of a constraint is that a discrete
   procedure can evaluate it and *reject*. Superposing it into an 8192-dim vector
   converts an exact checker input into a noisy retrieval target — you would need to
   decode it back out (with confidence < 1) before you could check anything. The
   estate's own decode-direction architecture says it plainly: exact answers come from
   typed slots and fail-closed deductive gates, "never a cosine match"
   (sparq-estate.md §2, `ground()` + propose-then-verify). A verifier that lives
   *behind* the vector, keyed by the URN the vector's identity already carries, loses
   nothing and keeps exactness.
3. **The consumer argument.** No experiment in the programme gives an LM a mechanistic
   route from frozen constraint-geometry to constraint-obeying behaviour; the
   KG-injection literature the programme commissioned says taxonomy-shaped injections
   were "narrow, task-local … effectively abandoned"
   (reports/nsm-and-knowledge-injection.md §4, cited at panel 1.3); C4
   (internal rules-based inference) is [speculative] and explicitly repositioned
   *kernel-side*: "rules run kernel-side over explications and world-layer facts with
   the LM as proposer" (architecture.md §2 C4). The constraint layer is the first
   concrete instance of that repositioning: the LM proposes assertions; the kot-axiom
   validator disposes.
4. **The stability argument.** Axiom sets will churn (they are the contestable layer —
   §3.4's honesty note). If they were encoder inputs, every axiom revision would be an
   ALGORITHM_VERSION-adjacent event for the affected vectors, breaking "same
   definition ⇒ same vector" and the update-paradox posture (models pin kernel
   snapshots; architecture.md §2 O8). Keeping the vector a pure function of the
   *explication* preserves the one clean invariant the programme has.
5. **The steelman, priced.** If C4 ever revives (GNN-style soft inference over concept
   geometry), constraint-aware geometry might enable soft unification — at that point
   the right mechanism is a *separate, additively-composed constraint lane* (the sparq
   `SchemaHeader` partitioned-block discipline exists for exactly this), never mixing
   into the explication-derived vector. Decision deferred until any E-series evidence
   makes C4 non-speculative; recorded here so the future argument starts from the
   right design.

**The one legitimate vector-adjacent use of axioms, adopted:** decode/cleanup-time
**masking**. sparq's `DisjointnessOracle` pattern — propagate disjointness through the
subclass closure, hard-mask provably-disjoint candidates during nearest-neighbour
cleanup — transfers directly to the kernel's decoder (which already does cleanup
against the kernel lexicon, architecture.md §1.2). Constraints there act as a
*filter on discrete candidates*, consuming the sidecar at exactly the boundary where
vectors are being converted back into symbols. That is verifier-not-in-the-vector,
operationalised.

---

## 5. Implications for the hypothesis and the go/no-go structure

**Does "can't-misunderstand accuracy" require this layer?** In its original
inside-the-weights form — no, because that form is already [contradicted] regardless
(fixing a vector fixes a symbol, not its interpretation; architecture.md §2 C1). In
its **surviving form — misunderstanding made detectable and correctable at the
interface — yes, for profile-1, it does.** Without axioms, interface verification for
ordinary concepts tops out at structural checks (grammar, hash, referent discipline);
the "meaning-level" tier of the A5 claim is real only in profile-M/P (sorts,
dimensions). The constraint layer is what extends a *mechanical* verification stratum
to ordinary concepts: not adequacy (forever social), but **consistency of asserted
records with stipulated structure** — three-parents errors, category violations,
functional-property violations. It is the difference between a verifier that says
"this is well-formed" and one that says "this cannot be true as asserted, given what
you stipulated."

**Go/no-go impact, precisely:**

1. **The E1–E4 kill chain is untouched.** No vector-level question in it consumes
   axioms; nothing here blocks or reprioritises it. The constraint layer must NOT be
   allowed to delay the kill chain (build order: after arq minting and the E2
   re-analysis the panel ranked above everything).
2. **E9 gains its sharpest arm.** The panel's deflationary baseline (3.1: a
   hash-pinned gloss file captures most of the assurance pitch) is the standing threat
   to the A5 product story. Constraint-violation detection is the one delta *text
   cannot deflate*: a gloss file cannot count parents. Add to E9's design: a
   constraint-violation arm (seeded instance-record corpora with planted
   cardinality/disjointness/domain violations; measure what decode-verify+kot-axiom
   catches vs RAG-with-citations vs the gloss-file arm). If the kernel's assurance
   pitch survives anywhere, it survives here.
3. **A new honesty gate for the bulk tiers**: no external document may describe
   bulk-tier `axioms` arrays as logical constraints until they are lowered into
   kot-axiom/1 (or explicitly disclaimed per corpus) — the §2.2-iv debt, made a rule.
4. **Cost estimate [claimed]:** the v0 validator is a few hundred lines in the
   estate's house style (closed inventory + caps + fail-closed codes; the JCS mint
   path is already built; sparq's oracle/closure patterns are ports, not research).
   The expensive part is authoring axiom sets worth checking — which is world-layer
   work, correctly still deferred; the litmus family (human/parent/sex,
   bookmark/maker, promise/parties) suffices for E9.
5. **What this does not change:** the hypothesis's centre of gravity stays where the
   architecture put it — identity + verification at the interface as the durable
   product, vector-vocabulary claims pending the kill chain. The constraint layer
   strengthens the durable product; it neither rescues nor burdens the contested one.

---

## 6. Open questions (filed, not blockers)

1. **Closure discipline granularity** — which closures (subclass, inverse) are
   materialised before validation, and is the closure itself snapshot-pinned?
   (Proposed: RDFS-subclass + inverse only, pinned in the profile bundle; anything
   more is rule territory.)
2. **Gist reconciliation** — does PSS adopt the constitutive-vs-extension rule (§3.5
   arg 4) for estate-side records, or keep all axioms inside D1 with re-mint churn
   accepted? Belongs on sparq#1683 with the JCS dual-hash question.
3. **Qualifier expressiveness pressure** — how soon does v0's "qualifier = one concept
   URN, mint intersections explicitly" austerity hurt? (Watch the first ten real axiom
   sets; boolean combinators are a v1 decision with a real semantics cost.)
4. **Molecule-tier axioms** — molecules-v0's `axioms: []` placeholders: lower the
   obvious structural facts (mother subClassOf woman[m]-adjacent? disjointness among
   animal kinds?) once kot-axiom exists, or keep molecules axiom-free until the
   encoder can reference them at all (design-molecule-tier.md §4 blocks that first)?
5. **Deontic register** — the legal/regulatory scope claim eventually wants
   obligations ("must be retained for 7 years"), which are not CWA record constraints.
   Out of scope for kot-axiom; recorded so nobody stretches cardinality syntax into
   deontic logic by increments.

---

*Sources: repo files as cited inline (verified on disk 2026-07-08); W3C
[SHACL 1.2 Core WD](https://www.w3.org/TR/shacl12-core/) (Data Shapes WG, June 2026)
and [SHACL 1.0 REC](https://www.w3.org/TR/shacl/) (`sh:qualifiedValueShape`,
`sh:qualifiedMin/MaxCount`; recursion undefined in 1.0); OWL 2 Profiles (W3C REC —
EL/QL/RL cardinality exclusions; RL `maxCardinality 0/1`); SROIQ/OWL 2 DL complexity
N2EXPTIME-complete (Kazakov 2008 / OWL 2 Direct Semantics); Plate 1995 (HRR);
concept-hash-design.md §5–§8, §13; design-hash-input.md; design-math-sector.md §2–§4;
panel-kernel-design-review.md lenses 1.1, 1.3, 2.5, 3.1–3.3; reports/sparq-estate.md
§1, §2, §4.*
