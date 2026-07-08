# Description logic from NSM first principles + the Lean losslessness round-trip

**Status:** design record, 2026-07-08. Deep first-principles study: does ontology-grade
logic *emerge* from the kernel's own foundations, or must it be bolted on — and is the
kernel lossless with respect to Lean modulo naming?
**Author:** F3 design agent (Claude Fable 5), for @jeswr.
**Relation to the sibling record:** `docs/design-constraint-layer.md` (F1) designs the
generic constraint/axiom layer (kot-axiom/1, SHACL-core closed-world semantics, sidecar
records, verifier-not-in-the-vector). This document deliberately does **not** re-do that
work. Its angle is the opposite direction: start from the 65 primes and the kot-ast/1
grammar and *derive* the description-logic constructors bottom-up; measure how much
ontology structure is already latent in the explications the kernel ships; assess whether
DL is even the right tool; and work the Lean-foundations and losslessness questions the
maintainer posed. Where the two documents meet (the sidecar slot), the join is marked
explicitly (§7 fork F2).
**Inputs read (all verified on disk 2026-07-08):** encoder/src/{lexicon,ast}.ts;
data/kernel-v0/concepts/{event,promise}.json; docs/design-{molecule-tier,math-sector,
lean-route,hash-input,constraint-layer}.md; docs/architecture.md;
notes/{mandate,panel-kernel-design-review}.md; reports/{deterministic-concept-vectors,
sparq-estate}.md; ../concept-gist/concept-hash-design.md (external gist).
**Honesty contract:** [established] / [claimed] / [open]. Standing directive honoured in
§7: where confidence is low the answer is a *fork with a deciding experiment*, not a
guess.

---

## 0. Summary of findings

1. **A large, specific fragment of SROIQ builds directly from the primes** (§2): ⊓,
   ∃R.C, clause-level ¬, per-sort ⊤, definitional role composition, inverse-by-swap, and
   cardinalities up to **exactly 2** are constructible from the existing grammar — most
   of them are *already how explications work*. What does not build: disjunction (no OR
   prime — a known, deliberate NSM absence), counting ≥ 3 (NSM's numerals stop at TWO),
   nominals (no individuals in the kernel — by design), and free-standing role axioms
   (no record frame to put them in). The maintainer's litmus axiom ("a human has exactly
   two parents, one male and one female") sits **exactly at the edge of NSM's native
   counting power** and is expressible today given ~3 semantic pins and one small grammar
   extension (§2.4).
2. **The emergence verdict (§3): read out what emerges; bolt on only the residue.** An
   ∃-conjunctive Horn-style TBox skeleton (classification-clause subsumptions, frame
   domain/range, existential role restrictions, composition-by-referent-chaining) is
   mechanically derivable from existing records with no new machinery — promise.json's
   first clause *is* `promise ⊑ words`. Disjointness, upper-bound cardinalities, and
   inclusion-only role axioms are genuinely new content and belong in F1's sidecar.
   Confidence: high on the partition itself; low on whether the read-out should be
   normative — that is fork F1 (§7).
3. **DL is the wrong home, the right interchange (§4).** The explication grammar is a
   frame-semantic scenario formalism whose logic-shaped fragment happens to land in the
   tractable Horn/EL design region; its native content (CAN, BEFORE/AFTER, BECAUSE,
   KNOW/THINK with clause complements, quotes) exceeds SROIQ in exactly the directions
   DL cannot follow. The best formal lens for what emerges is **existential rules
   (TGDs)**, with OWL as a lossy projection for interop and SHACL-CW (F1) for checking.
4. **NSM reaches gloss-grade, not mechanics-grade, CIC (§5.1).** Type≈KIND,
   typing≈BE-SPEC, function≈deterministic-disposition script, proof≈"because of this,
   people can know it is true" — all honestly explicable. Binding (Pi/lambda),
   reduction (defeq), universes and induction-as-least-fixpoint are unreachable; the
   attempt independently re-derives the two grounds on which design-math-sector §2.4
   rejected CIC (the **binding wall** and the **computation wall**).
5. **The Lean round-trip is lossless modulo naming — but only inside the honest
   fragment, and the LLM's role is one-shot and self-certifying (§5.3).** Because the
   forward map (Lean statement → canonical name-free kernel content) is deterministic,
   any LLM-recovered name can be *verified by hash equality* (re-run the forward map on
   the candidate; compare URNs). The LLM is a bridge-builder, not a runtime dependency:
   locate once, verify, persist as a signed annotation, deterministic ever after. What
   is unrecoverable without the name: namespace placement, notation, formulation
   variants collapsed by canonicalisation, proofs, attributes. This is exactly why Lean
   mints no id and Metamath carries identity: identity can live only where the
   round-trip has a fixed point, and Metamath's canonical token strings have one while
   Lean's elaboration layers do not (design-lean-route §2).
6. **Four homes for "axioms" (§6):** profile bundle (constitutive of the formalism) /
   concept records (definitional) / axiom sidecar (endorsed laws) / world layer (ground
   facts). The litmus axiom is an endorsed **law**, not a definition — a human with
   three genetic parents would still be human — so folding it into `human`'s hash would
   be a category error the current architecture correctly avoids.
7. **Seven design forks with deciding experiments (§7).**

---

## 1. Raw material: what the kernel's foundations actually provide

From `encoder/src/lexicon.ts` [established, by inspection]:

- **Logical primes:** NOT (58), MAYBE (59), CAN (60), BECAUSE (61), IF (62).
- **Quantifier primes:** ONE, TWO, SOME, ALL, MUCH~MANY, LITTLE~FEW (12–17). Exact
  numerals stop at TWO — a load-bearing fact for §2.3.
- **Determiners:** THIS, THE-SAME, OTHER~ELSE~ANOTHER — identity (THE-SAME) and
  distinctness (OTHER) are *primes*, which is what makes counting-by-referents possible.
- **Relational substantives:** KIND, PART — the subsumption and mereology hooks.
- **Operators (closed, arity-checked):** NOT/CAN/MAYBE (1: clause), IF/BECAUSE/WHEN (2:
  clause, clause), LIKE (2), AFTER/BEFORE (2: anchor, scope), VERY/MORE (1). Note
  `MORE` is classed `overModOrQuant1` — licensed **over quantifiers** by gist §4.5.
- **Valency frames:** 19 predicate frames over a closed 17-role inventory, each slot
  typed by `SlotFillerKind` — frame-level domain/range constraints, already enforced.
- **Explication frames:** InstanceSchema (referent 1 := *an arbitrary instance*),
  WhenTrue (boolean property), RelationalSchema (referents 1, 2 := subject, object).
  The frames carry **generic/universal force**: an InstanceSchema explication speaks of
  *any* instance — this is where a TBox axiom's leading ∀ already lives (gist §4.6).
- **Referents:** ≤32 flat, DRT-style, indexed, each with exactly one introducing
  occurrence (`bind`). Under standard DRT semantics, main-box discourse referents are
  **existentially quantified** [established, DRT] — so referent introduction *is* ∃.
- **SPs:** `[det]? [quant]? [mod]* head [restrictedBy: clause]?` — a guarded, one-clause
  restriction mechanism; heads may be substantive primes, KIND/PART frames, referent
  mentions, or **defined-concept refs** (ast.ts `ConceptHead`).

Two structural facts from `encoder/src/ast.ts` that constrain everything below
[established, by inspection]:

- **The one-clause argument rule.** Operator arguments (`OpArg`) and `restrictedBy` take
  exactly **one clause**. Conjunction exists only as top-level clause juxtaposition.
  There is no AND *under* an operator — the single most consequential gap for logic
  read-out (§2.2, fork F5).
- **No predicate position for defined concepts.** `PredClause.pred` must be a prime with
  a valency frame; RelationalSchema concepts can be *defined* but not *applied* with
  explicit argument binding inside another explication (§2.4, extension X5).

**The semantic-reading precondition.** NSM explications are canonical scenario scripts,
not necessary-and-sufficient conditions (panel-kernel-design-review §2.5); the kernel's
posture is stipulative (architecture.md §1.0 rev 3). Every "maps to DL" claim below is
therefore conditional on a **stipulated classical reading** of the operators involved.
Those stipulations are enumerated as pins P1–P7 (§2.5) and their cost is priced in fork
F2 — they are the honest price of reading logic out of a natural-semantic grammar.

---

## 2. Part A — the SROIQ constructor inventory, built from primes

### 2.1 The mapping table

Verdict legend: **NATIVE** = constructible in kot-ast/1 today, and (where noted) already
the working practice of shipped records; **PIN** = constructible given a semantic pin
from §2.5 (no grammar change); **EXT** = requires a named grammar extension (§2.6);
**SPLIT** = part native, part sidecar; **NO — BY DESIGN** = deliberately out of the
definitional layer.

| # | DL constructor | Construction from primes / kot-ast | Verdict |
|---|---|---|---|
| 1 | **C ⊓ D** (conjunction) | Clause juxtaposition: two classification clauses on referent 1, e.g. `BE-SPEC(u:ref1, attr:KIND-of C)` + `BE-SPEC(u:ref1, attr:KIND-of D)`. Every multi-clause explication is already a ⊓. Caveat: clause order is identity-bearing (gist §13 Q1; design-math-sector §3.4), so ⊓ is **non-commutative at the identity layer** — C⊓D and D⊓C mint distinct hashes; semantic commutativity is `sameConceptAs` annotation business. | **NATIVE** (ordered) |
| 2 | **C ⊔ D** (disjunction) | No OR prime — a deliberate NSM absence (canonical explications avoid disjunction; epistemic alternatives use MAYBE/CAN). Routes: (a) classical `IF(NOT(C(x)), D(x))` under pin P1; (b) `CAN(C(x))` + `CAN(D(x))` — strictly weaker (possibility of each disjunct, no exhaustiveness), and the exhaustiveness repair `NOT(CAN(NOT C ∧ NOT D))` hits the one-clause argument rule. | **PIN (P1)**, else **EXT (X1)**; genuinely alien to NSM |
| 3 | **¬C** (negation) | `NOT(clause)` is native (event.json clause 2 uses it). Complement-*as-a-concept* — an InstanceSchema whose only content is `NOT(BE-SPEC(ref1, KIND-of C))` — is grammar-legal but anti-idiomatic (NSM scripts are positive) and geometrically near-invisible (X3: one NOT ≈ cos 0.9999). | **NATIVE** (clause level); complement-concepts degenerate-legal |
| 4 | **⊤ / ⊥** | The kernel is **many-sorted at the top**: bare SOMEONE / SOMETHING~THING / TIME / PLACE heads and the five refKinds are per-sort ⊤s. A single global ⊤ = the union of sorts — blocked by missing ⊔. ⊥ = any contradictory pair (`THERE-IS(ref1)` + `NOT(THERE-IS(ref1))`); no falsum constant (same as math-v0 L4), so infinitely many non-identical ⊥s mint distinct hashes — ⊥ exists but is **not canonical**. | per-sort ⊤ **NATIVE**; global ⊤, canonical ⊥ absent |
| 5 | **∃R.C** (existential restriction) | **The grammar's core mechanism.** A `bind`-introduced referent in a role slot + restricting clauses = ∃y.(R(x,y) ∧ C(y)). Shipped practice: promise.json's agent (`SOMEONE, bind 2`), event.json's time (`SOME TIME, bind 2` = `event ⊑ ∃happensAt.Time`). DRT referent semantics supplies the ∃ [established]. | **NATIVE** — already ubiquitous |
| 6 | **∀R.C** (universal restriction) | `quant: ALL` SP + `restrictedBy` (the R-clause) as subject of a C-clause: "all someones who R this one are C". Two costs: (a) NSM's ALL needs the distributive pin P3; (b) the one-clause rules cap both R and C at one clause each — **complex C must be a minted concept referenced by `ConceptHead`**. The caps thereby force DL's own named-concept discipline: complex fillers get names. | **PIN (P3)** + naming discipline |
| 7 | **≥n / ≤n / =n R.C** (qualified number restrictions) | n ≤ 2: referent-counting with the distinctness prime. ≥1: one bound referent. ≥2: second referent with `det: OTHER` under pin P4. **≤2: `NOT(THERE-IS(SP{det:OTHER, head:SOMEONE, restrictedBy: R-clause}))`** — "there is no one *else* who Rs x" — pins P2+P4+P5. =2 = the conjunction of both. This is precisely how Minimal English says it, which is strong evidence the construction is NSM-honest, not a trick. n ≥ 3: NSM's numerals end at TWO. Routes: (a) `MORE(TWO)` as SP quantifier — **licensed by gist §4.5 (`MORE` over quant) but unrepresentable in kot-ast/1**, whose `SP.quant` admits only the bare enum (ast.ts line 117) — a one-field extension X4a; (b) cross-profile numeral refs to math-v0 (`urn:math-v0:three` — the counting tower NSM lacks, profile-M has) — X4b; (c) referent-chains with O(n²) distinctness clauses — cap-hostile. | n ≤ 2 **PIN (P2,P4,P5,P6)**; n ≥ 3 **EXT (X4)** |
| 8 | **{a}** (nominals) | No individuals exist in the kernel. I/YOU/NOW/HERE are *indexicals* (re-anchored inside quotes — promise.json), not rigid designators; THIS is deictic. Individuals are world-layer by mandate ("Jesse as a person" — notes/mandate.md). Refusing nominals also refuses the SHOIN/SROIQ complexity cliff they cause. | **NO — BY DESIGN** (world layer) |
| 9 | **R⁻** (inverse roles) | For RelationalSchema concepts: mint the mirror record (referents 1, 2 swapped in every clause). The *converse-ness* of the pair is then **mechanically checkable** — swap-referents-1-2, canonicalise, compare — so `inverseOf` can be a *derived, verified annotation* rather than an authored axiom. Valency roles (agent, undergoer…) have no inverses and need none: they are grammatical functions, not ontology relations. | **NATIVE** (by mirror-mint) + read-out annotation |
| 10 | **R ⊑ S** (role hierarchy) | By-construction case: R's explication references S (`ConceptHead`) or includes S's clause set — subsumption is readable from reference structure / clause-multiset inclusion up to referent renaming (structural subsumption, the EL classification move). General semantic subsumption = reasoning, never at mint; sidecar/reasoner territory. | **SPLIT**: syntactic read-out native; semantic = sidecar |
| 11 | **R∘S ⊑ T** (role composition) | Definitional composition is native **referent chaining**: grandparentOf's body = "there is someone z; x is a parent of z; z is a parent of y". That defines T *as* the composition (≡, stronger than ⊑). Inclusion-only composition (composition implies T, T means more) is a genuine axiom the definitional layer cannot carry. Note: composition is what drives SROIQ's regularity conditions and complexity; the kernel's definitional form is harmless because nothing reasons at mint. | **SPLIT**: ≡-composition native; ⊑-only = sidecar |
| 12 | **Trans(R)** | Logically: curried IF — `IF(R(x,y), IF(R(y,z), R(x,z)))` — classical currying under P1 evades the one-clause rule. Architecturally: a transitivity statement defines no concept, so it has no legal frame today; it needs either the AxiomSchema frame (X3 — the NSM-native rendering of F1's sidecar slot) or, where transitivity is *constitutive* (ABOVE), a self-referential clause inside the concept's own explication — legal, the gist's SCC machinery (§6 steps 6–9) exists precisely for self/mutual reference. | **PIN (P1) + EXT (X3)**; constitutive case native via SCC |
| 13 | **Func(R)** (≤1 R.⊤) | The n=1 instance of row 7's ≤ construction: "there is no one else who Rs x". | **PIN** (as row 7) |
| 14 | **Refl(R) / global role properties** | `ALL` + `THE-SAME` under X3 ("everyone is R to the same one, i.e. to themselves" needs THE-SAME as second argument). Statable; same homelessness as row 12. | **PIN + EXT (X3)** |

**Aggregate verdict [claimed]:** of the SROIQ inventory, the kernel natively owns the
**∃-conjunctive core plus small counting** (rows 1, 3–5, 7≤2, 9, 10-syntactic,
11-definitional) — roughly the Horn-EL⁺⁺ neighbourhood extended with guarded negation
and exactly-≤2 — and *cannot* own disjunction, large counting, nominals, or free-standing
role axioms without pins/extensions. It is striking, and worth saying plainly, that
NSM's discourse-driven expressive humility lands the grammar **inside the tractable
fragment region that the DL community spent two decades isolating on purpose** (EL/Horn:
no ⊔, no unbounded counting → PTIME classification). The kernel did not choose
tractability; its natural-semantic discipline chose it for free.

### 2.2 The one recurring wall

Disjunction (row 2), upper cardinality bounds beyond the OTHER-trick (row 7), and
non-curried conditionals all fail at the same point: **operators take one clause**
(ast.ts `OpArg`; gist §4.5 arities). Everything else in the logic read-out is native or
pin-only. This localises the entire "NSM can't do logic" objection to a single grammar
degree of freedom — which is what makes fork F5 (§7) cheap to decide: count how often
real axioms need AND-under-operator before paying an encoder version bump for it.

### 2.3 Where the counting power comes from — and where it ends

The n≤2 constructions work because NSM supplies, as *primes*, exactly the three
ingredients of finite FO counting: existence (referent binding), **distinctness**
(OTHER~ELSE~ANOTHER), and **identity** (THE-SAME). They end at 2 because NSM's exact
numerals end at TWO [established, chart v20]. The natural continuation is not to grow
profile-1 but to **cross-reference profile-M's numeral tower** (three → two → one,
data/math-v0) — the math sector holds the counting infrastructure NSM lacks, and
cross-profile URN reference is already legal (design-math-sector §3.5). That the
maintainer's litmus axiom needs exactly n=2 — the last number NSM can count to — is a
happy accident worth not relying on: the *next* such axiom ("insects have six legs")
falls off the cliff immediately.

### 2.4 Worked encodings

Notation: compressed kot-ast/1; `[Xn]`/`[Pn]` marks the extension/pin a line depends on.
All three records are research-grade demonstrations of *constructor shape*; their
adequacy as definitions is stipulative and unendorsed, per the standing posture.

**(a) A role: `parentOf` — RelationalSchema (legal today).**
Gloss: *"this someone [y] lives because this other someone [x] did something before y
lived."* (Biological-parent reading; deliberately coarse — the sexed refinements exist
as molecules mother/father in data/molecules-v0.)

```jsonc
{ "schema": "kot-ast/1", "frame": "RelationalSchema",   // ref1 = x (parent), ref2 = y (child), frame-implicit
  "referents": [ { "index": 3, "refKind": "TimeRef" } ],
  "clauses": [
    // "x did something at some time t; because of this, y lives"
    { "type": "op", "op": "BECAUSE", "args": [
        { "type": "pred", "pred": "DO", "roles": {
            "agent": { "kind": "ref", "index": 1 },
            "undergoer": { "kind": "sp", "head": { "kind": "primeHead", "prime": "SOMETHING~THING" }, "quant": "SOME" },
            "time": { "kind": "sp", "head": { "kind": "primeHead", "prime": "WHEN~TIME" }, "det": "SOME", "bind": 3 } } },
        { "type": "pred", "pred": "LIVE", "roles": { "undergoer": { "kind": "ref", "index": 2 } } } ] },
    // "after t, y lives" (the doing precedes the living)
    { "type": "op", "op": "AFTER", "args": [
        { "kind": "ref", "index": 3 },
        { "type": "pred", "pred": "LIVE", "roles": { "undergoer": { "kind": "ref", "index": 2 } } } ] } ] }
```

DL shadow: `parentOf` gets domain/range **for free** from the frame (RelationalSchema
over two SomeoneRefs ⇒ domain ⊑ Person-sort, range ⊑ Person-sort) — row-10 read-out.

**(b) A concept: `human` — InstanceSchema (legal today).**
Gloss: *"someone of the kind 'people'; there is a body; it is part of this someone;
this someone can die."*

```jsonc
{ "schema": "kot-ast/1", "frame": "InstanceSchema",     // ref1 = an arbitrary instance
  "referents": [ { "index": 2, "refKind": "SomethingRef" } ],
  "clauses": [
    // ⊑-clause: "this someone is one of people"        → human ⊑ People-kind (read-out)
    { "type": "pred", "pred": "BE-SPEC", "roles": {
        "undergoer": { "kind": "ref", "index": 1 },
        "attribute": { "kind": "sp", "head": { "kind": "kindFrame",
            "of": { "kind": "sp", "head": { "kind": "primeHead", "prime": "PEOPLE" } } } } } },
    // ∃-clause: "there is a body; it is a part of this someone"  → human ⊑ ∃hasPart.Body (read-out)
    { "type": "pred", "pred": "BE-SPEC", "roles": {
        "undergoer": { "kind": "sp", "head": { "kind": "primeHead", "prime": "BODY" }, "bind": 2 },
        "attribute": { "kind": "sp", "head": { "kind": "partFrame", "of": { "kind": "ref", "index": 1 } } } } },
    // modal residue — outside DL, native to the grammar: "this someone can die"
    { "type": "op", "op": "CAN", "args": [
        { "type": "pred", "pred": "DIE", "roles": { "undergoer": { "kind": "ref", "index": 1 } } } ] } ] }
```

**(c) The litmus rule: "a human has exactly two parents, one male and one female."**
NSM reading (which is how a Minimal-English speaker would actually say it): *"someone is
a parent of this someone; someone else is a parent of this someone; there is no one else
who is a parent of this someone; the first is a man; the other is a woman."*

```jsonc
{ "schema": "kot-ast/1+X3", "frame": "AxiomSchema",      // [X3] subject: urn:kot:human; ref1 = an arbitrary human (P7)
  "subject": "urn:kot:human",
  "referents": [ { "index": 2, "refKind": "SomeoneRef" }, { "index": 3, "refKind": "SomeoneRef" } ],
  "clauses": [
    // ≥1: "someone is a parent of this someone"
    { "type": "apply", "concept": "urn:kot:parentOf",    // [X5] apply-clause
      "args": { "1": { "kind": "sp", "head": { "kind": "primeHead", "prime": "SOMEONE" }, "bind": 2 },
                 "2": { "kind": "ref", "index": 1 } } },
    // ≥2: "someone ELSE is a parent of this someone"    — distinctness via det OTHER [P4]
    { "type": "apply", "concept": "urn:kot:parentOf",
      "args": { "1": { "kind": "sp", "head": { "kind": "primeHead", "prime": "OTHER~ELSE~ANOTHER" /* det, abbreviated */ }, "bind": 3 },
                 "2": { "kind": "ref", "index": 1 } } },
    // ≤2: "there is NO ONE ELSE who is a parent of this someone" [P2, P4, P5]
    { "type": "op", "op": "NOT", "args": [
        { "type": "pred", "pred": "THERE-IS", "roles": {
            "undergoer": { "kind": "sp", "det": "OTHER~ELSE~ANOTHER", "head": { "kind": "primeHead", "prime": "SOMEONE" },
              "restrictedBy": { "type": "apply", "concept": "urn:kot:parentOf",
                                 "args": { "1": "self" /* [P5] */, "2": { "kind": "ref", "index": 1 } } } } } } ] },
    // typing: "one is a man, the other is a woman" — molecule refs [m]
    { "type": "pred", "pred": "BE-SPEC", "roles": { "undergoer": { "kind": "ref", "index": 2 },
        "attribute": { "kind": "sp", "head": { "kind": "kindFrame", "of": { "kind": "concept", "id": "urn:molecule-v0:man" } } } } },
    { "type": "pred", "pred": "BE-SPEC", "roles": { "undergoer": { "kind": "ref", "index": 3 },
        "attribute": { "kind": "sp", "head": { "kind": "kindFrame", "of": { "kind": "concept", "id": "urn:molecule-v0:woman" } } } } } ] }
```

Dependency audit of (c), stated honestly:

- **[X3] AxiomSchema** — the record is about `human` without being `human`'s definition;
  no legal frame exists today. The today-legal alternative is inlining these clauses
  into `human`'s InstanceSchema — which **changes human's identity hash** and makes
  two-parenthood *constitutive of the concept*. That is exactly the definition-vs-law
  category error §6 analyses; X3 (or F1's kot-axiom/1 sidecar — fork F2) exists to avoid
  it.
- **[X5] apply-clause** — without it, `parentOf`'s body must be inlined at each use.
  Inlining is possible here (the BECAUSE body is a single op-clause, so it fits
  `restrictedBy`'s one-clause budget), so the rule is expressible **today** with pins
  only — but inlining burns the structure budget the capacity math depends on
  (deterministic-concept-vectors §7.4 warns that inlining referenced definitions "burns
  the budget quadratically fast") and defeats compositionality-by-reference. X5 is the
  single highest-value grammar extension this analysis surfaces.
- **Molecule refs** — `urn:molecule-v0:{man,woman}` exist but are not yet encodable as
  ConceptRefs (no pinned molecule-vector derivation; design-molecule-tier §4.2).
- **Pins P2, P4, P5** (§2.5).

And the honest caveat about *content*: as §6 argues, this rule is a world-layer law (a
biological regularity with real edge cases — gamete donation, mitochondrial-donation
three-parent cases, cloning), not an analytic truth. The encoding above demonstrates
*expressive power*; it does not recommend endorsing the axiom.

### 2.5 The pins (profile-1L: a stipulated classical reading, packaged)

Reading logic out of profile-1 requires pinning classical semantics for a handful of
primes/constructions. Bundle them as one content-addressed semantics document
("profile-1L") so the stipulation is explicit, versioned, and opt-in:

| Pin | Statement | Cost |
|---|---|---|
| P1 | IF = material implication (enables ⊔ via `IF(NOT a, b)`, Trans via currying) | Largest departure: natural-language conditionals are not material [established, semantics literature]. Only needed for rows 2, 12. |
| P2 | NOT over THERE-IS = classical non-existence within the schema's scope | Mild; matches event.json's NOT usage. |
| P3 | ALL = distributive universal, clause-scoped | NSM's ALL is arguably generic/collective; distributivity is a stipulation. |
| P4 | det OTHER = distinct from **every** previously introduced same-refKind referent in scope | Formalises existing practice (promise.json's addressee: `det OTHER, bind 3` = "someone else"). |
| P5 | In a `restrictedBy` pred/apply clause, a designated `self` marker denotes the restricted SP | Pure convention; today's only restrictedBy examples are op-clauses with implicit subjects (gist §3.4 "some time after now"). |
| P6 | ONE/TWO in quant position = exact cardinals (not "at least") | NSM-consistent; needed for =n readings. |
| P7 | Frame generic force: InstanceSchema/WhenTrue/RelationalSchema/AxiomSchema quantify universally over their implicit referents | Already the gist's own reading ("referent 1 := an *arbitrary* instance", §4.6); P7 just makes it load-bearing. |

### 2.6 The extensions (named, priced, not recommended yet)

- **X1 — ClauseGroup** (n-ary AND as an operator argument): unlocks ⊔ via de Morgan and
  non-OTHER ≤n. Encoder + identity version change (AST shape change ⇒ ALGORITHM_VERSION
  bump, X0 regen). Decide via fork F5.
- **X2 — profile-1L pins document** (§2.5): no grammar change; a semantics artifact.
- **X3 — AxiomSchema frame**: a fourth frame whose subject is a concept URN and whose
  referents are generic. This is the NSM-*native* filling of the sidecar slot F1
  designed; it is profile-1's analogue of profile-M's `AxiomDef` (design-math-sector
  §3.2), which already proves the record-class works. Fork F2 decides whether it or
  kot-axiom/1 carries the residue axioms.
- **X4 — counting beyond two**: (a) admit `MORE`-wrapped quantifiers in `SP.quant`
  (already licensed by gist §4.5; a one-field AST change), or (b) numeral fillers by
  cross-profile reference to math-v0. Decide when an n≥3 axiom actually arrives.
- **X5 — apply-clause** for RelationalSchema (and WhenTrue) concepts: argument binding
  against the frame's declared signature. Highest-value extension (capacity argument,
  §2.4); still an encoder version change. Fork F6.

---

## 3. Part B — the emergence question

### 3.1 What the shipped records already say, read as logic

Working only from the two worked records [established, by inspection of the JSON]:

**promise.json.** Clause 1 — `BE-SPEC(ref1, attr: SP{head WORDS})` — *is* a subsumption
assertion: `promise ⊑ words-stuff`. Clause 2 introduces two role successors
existentially (`SOMEONE bind 2`, `SOMEONE det OTHER bind 3`): `promise ⊑ ∃saidBy.Person
⊓ ∃saidTo.Person`, with the sayer≠addressee distinctness carried by `det OTHER` (P4's
evidence base). The quote clauses are propositional-attitude content with indexical
re-anchoring — no DL has this; it is native here.

**event.json.** Clause 1: `event ⊑ ∃happensAt.Time` (a bind-introduced SOME-time — a
textbook ∃R.C). Clause 2: `AFTER(t, NOT(HAPPEN(x)))` — a *temporal* axiom (cessation),
expressible in temporal DLs only. Clause 3: `CAN(KNOW(PEOPLE, …))` — epistemic modality
over an attitude — beyond SROIQ entirely. Meanwhile the gist's fuller Event record
(§3.3) carries `subClassOf ConcreteIndividual` and `disjointWith Endurant` as *explicit
axioms* — **neither is derivable from the explication**. That single record is the
emergence result in miniature: role restrictions emerge; taxonomy placement and
disjointness do not.

### 3.2 The partition, stated precisely

**(i) Read-out — DL semantics extractable from existing explications with no new
machinery** [claimed, mechanically checkable]:

1. **Subsumption from classification clauses**: `BE-SPEC(ref1, attr: KIND-of C / SP-head
   H)` ⇒ `Self ⊑ C/H`. NSM explications canonically open with a category clause, so
   coverage should be high (measured in fork F1's experiment).
2. **Subsumption from reference structure**: `ConceptHead`/`ConceptRef` uses give
   definitional-dependency edges; the subset that sits in classification position is
   `subClassOf`; the rest is `references` (already exported per record).
3. **Domain/range at sort granularity**: frame type + refKind declarations (Relational-
   Schema over SomeoneRef × SomethingRef ⇒ domain Person-sort, range Thing-sort);
   valency `SlotFillerKind`s do the same one level down — sparq's shacl_priors already
   consumes exactly this shape of information (reports/sparq-estate §4).
4. **Existential role restrictions**: every bind-introduced referent in a role slot with
   its restricting clauses ⇒ `Self ⊑ ∃role.(restriction)`.
5. **Definitional role composition**: referent chains across clauses ⇒ `R ≡ S∘T`-style
   definitions.
6. **Inverse pairs**: mechanical swap-1-2 structural comparison (§2.1 row 9).

Call this deterministic projection **Π: explication → TBox skeleton**. Π is *syntactic*,
linear, and fail-closed — the same gate discipline as everything else in the estate.

**(ii) Genuinely new — requires the axiom layer** [claimed]:

1. **Disjointness** (the gist Event/Endurant case; sparq's DisjointnessOracle *mines*
   `owl:disjointWith`, it does not derive it). In principle two explications could be
   proven contradictory, but real explications almost never make the contradiction
   syntactic.
2. **Upper cardinality bounds** — no shipped record has one; the ≤ constructions of
   §2.1 require pins and (usually) X3/X5.
3. **Inclusion-only role axioms and global role properties** (rows 11–14) — no frame to
   hold them.
4. **Checking semantics** — an explication *defines*; it does not *validate* instance
   data. Closed-world validation semantics is F1's kot-axiom/1 territory, unchanged.

### 3.3 Position

**Read out the skeleton; bolt on only the residue; never restate in the sidecar what
the explication already says.** The last clause is the important one: if `promise ⊑
words` is derivable from clause 1, an authored sidecar axiom repeating it is a standing
divergence surface (the dual-validator drift pattern the panel already flagged at §1.1
of the design review). The sidecar (F1) should carry the (ii)-list only, and the
snapshot should record Π's output as *derived, regenerable* annotations — exactly the
codegen-projector posture (gist §10: snapshot → OWL/SHACL projections).

**Confidence, stated per the standing directive:**

- That Π is *mechanically derivable* and the (i)/(ii) partition is as stated: **high
  (~0.85)** — it is an inspection-level claim about a closed grammar.
- That Π's output is *sound and useful* (produces subsumptions a human would endorse;
  supports classification that matches gold judgements): **low-medium (~0.5)** — never
  measured; scenario-script clauses may project subsumptions that are typicality, not
  necessity (the §1 semantic-reading caveat biting back). **Fork F1.**
- What to do with the modal/temporal residue (drop, or reify as guarded context atoms):
  **uncertain** — part of F1's experiment design.
- Whether Π should be *normative* (identity-adjacent, gate-checked for consistency with
  the sidecar) or *advisory* (a derived annotation): **uncertain** — also fork F1.

---

## 4. Part C — is DL the right tool for upper-ontology concepts over an NSM base?

Framed as the formalism's fit to three distinct jobs the kernel actually has:

**Job 1: defining concepts.** The explication grammar is a **frame-semantic scenario
formalism** — valency frames, roles, scripts, attitudes, quotes. DL cannot host most of
this content: CAN/MAYBE (modality), BEFORE/AFTER/WHEN (time), BECAUSE (causation),
KNOW/THINK/WANT with clause complements (attitudes), quote re-anchoring
(hyperintensionality). Every one of these is *load-bearing* in the shipped records
(§3.1). Translating explications *into* SROIQ would be a lossy flattening of exactly
the content NSM exists to carry; the panel's frame-semantics lens (§2.4) already
concluded the concept grain is frames, not word-sized class expressions. **Verdict: the
raw explication grammar keeps the definitional job.** No change.

**Job 2: stating and checking constraints over concepts.** Here the candidates:

| Formalism | Fit | Killer objection |
|---|---|---|
| OWL 2 DL (SROIQ) | Standard; reasoners; interop | Open-world — cannot *check* a record without closure gymnastics; N2EXPTIME; and no tractable profile expresses the litmus axiom (F1 §0.4 [established]) |
| OWL 2 EL/QL/RL | Tractable | Cannot express exact/qualified cardinality — fails the litmus case outright |
| SHACL-core CW | Checking is its native semantics; linear-ish; fail-closed | Not a definitional language; no entailment — which is fine, because defining is Job 1 |
| **Existential rules (TGDs/Datalog±)** | Π's output *is* a TGD set (∀x C(x) → ∃ȳ conj); chase-based reasoning; guarded fragments decidable; closed-world-friendly | ≤n needs (disjunctive) EGDs — the counting cases get ugly; tooling less commodity than OWL |
| Full FOL / type theory | Expressive | Undecidable checking; typechecker-in-the-mint-gate already rejected (design-math-sector §2.4) |
| Conceptual spaces | Graded, geometric | That is the *vector* layer's job, and X3 shows the current geometry cannot be trusted with meaning-bearing distinctions [established] |

**Verdict [claimed]:** the natural formal *home* of what emerges from explications is
**existential rules**, not DL — an InstanceSchema explication under P7 is literally a
TGD. DL (OWL 2) is the right **projection target** for interop with the estate and the
world (codegen, sparq), and SHACL-CW is the right **checking semantics** (F1's
conclusion, reached independently here from the emergence direction). Decidability — the
classic argument *for* DL — carries almost no weight in this architecture, because
nothing reasons at mint: identity is syntactic, gates are linear, and reasoning (if it
ever happens) is an offline consumer.

**Job 3: serving the LLM programme.** The honest open question: **no E-series
experiment consumes any of this** (panel §1.3: the axiom vocabulary has "no current
consumer"; the KG-injection literature is negative on taxonomy injection). The
possibility that the entire constraint layer is estate/interop value with zero LLM value
must remain a legal outcome — it is priced into forks F1/F2's kill criteria rather than
argued away here.

**Where the literature genuinely does not decide:** whether scenario-script definitions
(frames) or class-expression definitions (DL) yield better *machine-usable* upper
ontologies is a decades-old unresolved split (FrameNet/gUFO-prose vs BFO/DL-axioms) —
both traditions survive because they answer different queries. The kernel's two-layer
answer (scripts define; a projected skeleton + sidecar constrains) is a hypothesis, not
a settled synthesis: fork F1/F2's experiments are its test.

---

## 5. Part D — Lean base constructs, deterministic facts, and the losslessness round-trip

### 5.1 Can NSM build up to CIC's base constructs?

Attempted honestly, construct by construct. "GLOSS-GRADE" = an honest profile-1
explication of what the thing *is* exists (upper-ontology altitude); "UNREACHABLE" = the
formal mechanics cannot be carried by the grammar at any altitude.

| CIC construct | Best NSM build-up | Verdict |
|---|---|---|
| type | KIND (prime): "something of one kind; many things can be of this kind" | GLOSS-GRADE — KIND is genuinely the closest prime to "type" |
| judgment `t : T` | `BE-SPEC(t, attr: KIND-of T)` — the grammar has a *typing judgment* built in | GLOSS-GRADE, structurally faithful |
| function `A → B` | deterministic-disposition script: "this something can do something like this: when there is one thing of kind A, because of this there is one thing of kind B; if the A-thing is the same, the B-thing is the same" — extensionality via THE-SAME | GLOSS-GRADE; **no abstraction/application syntax** |
| Π-type (dependent) | the covariation is barely sayable ("the kind of the B-thing can be other when the A-thing is other") but **binding-in-types has no referent analogue**: profile-1 referents are flat, term-level, existential (gist §4.2); there is no binder | UNREACHABLE |
| Σ-type / pair | "something with two parts" (PART) | GLOSS-GRADE; profile-M has `Pair` natively |
| inductive types | base + step are sayable as script; **leastness** ("nothing else is of this kind") requires quantifying over kinds — and KIND is not a legal bare SP head (lexicon.ts SUBSTANTIVE_HEADS excludes it), so quantification over kinds is grammatically blocked | UNREACHABLE — matches profile-M needing `Set(N)` to state induction |
| universes | "a kind of kinds" — the gufo:Kind second-orderness strain (gist §3.3-iii), representable as one more concept record by punning | GLOSS-GRADE; stratification UNREACHABLE |
| propositions-as-types | proposition: "something someone can say; it can be true; it can be not true" (SAY/WORDS/TRUE/CAN — all primes); proof: "because there is this something, people can know that this is true" (BECAUSE/KNOW/TRUE) | both GLOSS-GRADE — surprisingly good; the *identification* P ≅ Type is a stipulated bridge annotation, not derivable |
| definitional vs propositional equality | THE-SAME covers identity talk; the def/prop split is a fact about *computation* (reduction), and NSM has no computation notion (DO is agentive action, not evaluation) | UNREACHABLE |

**The two walls [claimed]:** everything unreachable fails at one of two points — the
**binding wall** (flat existential discourse referents vs genuine binders; exactly the
line at which design-math-sector §3.4 had to introduce de Bruijn machinery) and the
**computation wall** (no reduction/evaluation notion in the prime inventory; defeq is a
computational fact). These are independently re-derived here from the NSM side, and they
are precisely the two grounds on which §2.4 of the math-sector design rejected CIC as an
identity substrate. The build-up attempt thus *confirms* the existing architecture
rather than revising it: NSM supplies the ontological gloss layer for logic/type-theory
vocabulary (valuable as `nsmBridge` records — several math-v0 records already carry
exactly this, both flagged KNOWN-WEAK); profile-M supplies the minimum formalism with
binders; CIC stays outside the identity layer.

### 5.2 Deterministic fact generation — three grades

1. **Axioms/definitions: yes, done.** The pinned basis table *is* the deterministic
   generator; math-v0's 6 AxiomDef + 9 Primitive records are its output [established].
2. **Ground decidable facts: yes, deterministic and gate-checkable, but low-value.** A
   pinned enumeration schedule (e.g. all `add(m,n) = k` for m,n ≤ N) plus the primrec
   evaluator makes every record self-verifying at the gate (evaluate both sides). But
   the unary-numeral depth wall (design-math-sector §4.2) caps N absurdly low, and the
   LM-arithmetic evidence (§1.5 there) says frozen math-fact vectors will not move
   calculation. Their only honest use is as **E-series probe targets with
   machine-checkable ground truth** (math-sector §5.2).
3. **Theorems: only with a proof layer, and the deterministic route is
   Metamath-shaped.** Proof-carrying records verified by a tiny substitution kernel
   (the ≥12-independent-verifiers property, math-sector §1.1) keep the mint gate a
   checker. Lean cannot play this role: verifying a Lean proof term means running the
   full kernel (conversion, universes) in the gate — the trusted-base expansion already
   rejected. Lean's theorem mass therefore enters as `lean-ref/1` annotations and
   bridge targets only (design-lean-route decision 1–2) — this document finds no reason
   to reopen that, and §5.3 strengthens it.

### 5.3 The losslessness round-trip (the crux)

**Setup.** The kernel deliberately drops the *name* of a Lean declaration — the
maintainer: "this is exactly the point." Forward map **F**: named Lean axiom/definition
→ canonical, name-free kernel content. Backward map **B**: kernel content + an LLM that
*locates* where that content is defined in Lean + a deterministic reconstruction script
→ the original axiom text. Question: is the kernel lossless under B∘F, modulo naming?

**The protocol, designed precisely:**

*Forward (F), deterministic:*
1. Extract the declaration's statement at `(mathlibCommit, name)` (ntp-toolkit layer).
2. **Fragment gate:** does the statement land inside profile-M's closed grammar
   (two-sorted PA fragment, closed formers, caps)? If **no** → `lean-ref/1` annotation
   only, **no id minted** — the status quo, now with a mechanical reason attached. If
   **yes** → continue.
3. Translate to `pm-ast/1`: de Bruijn canonicalisation; every referenced constant
   resolved **through the bridge table** to its kernel URN (missing bridge → recurse or
   abstain). The name `name` is recorded *only* in a signed bridge annotation
   `urn:kot:… ↔ (mathlibCommit, name)` — outside the hash, petname discipline (gist §7).
4. NFC + JCS canonical bytes → `urn:kot:` id (docs/design-hash-input.md).

*Backward (B):*
1. **Bridge lookup first.** If the bridge annotation exists, the name is recovered by
   table lookup — deterministic, no LLM involved.
2. **LLM locator only on bridge miss:** render the kernel record to notation-neutral
   statement text (a deterministic renderer over the closed pm-ast grammar —
   mechanically feasible for the same reason the gist's template renderer is, §9);
   the LLM searches Mathlib (LeanSearch/loogle-class tools or plain grep) and proposes
   candidate `(commit, name)` pairs.
3. **The verification gate — the step that makes the LLM safe:** run **F on each
   candidate**. If `F(candidate) = K` — *hash equality* — the location is **proven**
   correct; persist it as a signed bridge annotation (one-shot: the LLM never runs for
   this concept again). If no candidate verifies, fail closed. Because F is
   deterministic, B's correctness is *checkable*, not trusted: **content-addressing
   turns LLM retrieval into a verifiable operation.** The LLM can fail to find; it
   cannot silently mislocate.
4. **Reconstruction:** given `(commit, name)`, the original bytes come from the
   archived source span (byte-identical — the provenance archive design-lean-route
   already requires); or, nameless, a Lean renderer over the kernel record emits a
   statement that **re-elaborates at the pinned commit** to a term whose F-image equals
   K (content-identical, never byte-identical: variable names, notation, implicit-
   argument display are gone by design).

**The verdict, stated exactly [claimed]:**

- Within the fragment gate, **B∘F is the identity on canonical content**: the kernel
  preserves the statement's mathematical structure modulo alpha (de Bruijn), names
  (URN-substituted), and notation — and nothing else was inside the hash boundary to
  lose. In that precise sense the kernel **is lossless modulo naming**. The fixed point
  of the round-trip is the canonical form, not the source bytes — which is the correct
  fixed point, and the same one Unison and Metamath chose.
- **Preserved without the name:** the full definitional closure (referenced concepts
  travel as URNs, recursively — the content is *self-contained* in a way the named form
  never was). **Recoverable with verification:** the name/module placement (LLM +
  F-check). **Unrecoverable without the name, and honestly so:** Mathlib's namespace
  organisation; which of several defeq-equal formulations Mathlib happened to write (F
  canonicalises one; the variant is gone); proofs (never entered — statements only);
  attributes, docstrings (annotation layer by design).
- **The load-bearing qualifier: the fragment gate.** For the overwhelming majority of
  Mathlib (dependent types, typeclasses, universes), F does not exist honestly at any
  layer — source is context-dependent, pretty-printing is a rendering, kernel terms are
  defeq-unstable (design-lean-route §2 [established]). There the round-trip question
  does not arise, and identity correctly stays with `(mathlibCommit, name)` anchors.
- **Why Lean mints no id, restated through this lens:** an id may only be minted where a
  deterministic F exists; Metamath's F is total over set.mm (statements already *are*
  canonical context-free token strings — the round-trip fixed point exists trivially),
  Lean's F is partial (the fragment) — so Metamath carries math identity and Lean rides
  as annotation. Dropping the name is not a loss the LLM papers over; dropping the name
  is what *makes* the content ownerless and canonical, and the name comes back as a
  verifiable petname. The maintainer's "exactly the point" is, on this analysis,
  correct — with the fragment gate as the honest boundary of the claim.

**Measurement (fork F3's experiment, pre-registerable now):** (i) fragment-gate pass
rate on a random 1,000-declaration Mathlib sample (expectation: low single digits %);
(ii) LLM location accuracy on the ~dozen math-v0 records with genuine Mathlib
counterparts + the in-fragment slice of the 70-record lean sample — top-1/top-5
candidate rate, then **F-verified** rate; (iii) round-trip content-fixed-point rate
F(B(K)) = K; (iv) re-elaboration success of rendered statements at the pinned commit.

---

## 6. The axiom layer and the world layer — the four homes

The litmus example forces the question this section answers: *where do axioms live?*
The analysis of §§2–5 yields a four-way partition, each with a different identity and
revision discipline:

1. **The profile bundle** — axioms *constitutive of a formalism* (profile-M's Peano
   basis; profile-1L's pins if adopted). Frozen inside the profile hash; changing one is
   a new profile. Lean's `propext`/`Classical.choice` correspond to *this* stratum, not
   to concept records.
2. **Concept records** — *definitional* content: what a concept means, inside its
   identity hash. `event ⊑ ∃happensAt.Time` lives here because it is what "event"
   *says*.
3. **The axiom sidecar** (F1's kot-axiom/1, or X3's AxiomSchema — fork F2) — *endorsed
   laws*: general, quantified statements over kernel vocabulary whose truth is
   empirical or conventional, versioned and endorsable separately, checkable against
   instance data. The litmus rule lives here: two-parenthood is a biological regularity
   with living counterexamples, not part of what "human" means. Folding it into the
   definition would make edge-case humans *definitionally* non-human — the exact kind
   of silent semantic legislation content-addressing exists to make visible.
4. **The world layer** — *ground facts* about individuals ("Jesse's parents are …"),
   assumed-true per the mandate's explicit deferral; nominals (§2.1 row 8) live here
   and only here.

The strata are distinguished by **quantificational character**: definitions are generic
schemas over an arbitrary instance (P7); sidecar laws are explicitly quantified
statements *about* named concepts; world facts are ground. The DL analogy — TBox
definitions / TBox general axioms / ABox — maps cleanly, with the profile bundle as the
meta-level DL itself. Mathematical theorems, when a proof layer exists, are stratum-3
objects whose "endorsement" is a machine-checkable proof — the one place where the
social act of endorsement collapses into verification (design-math-sector §5.1's
epistemic win, relocated).

The vector-layer corollary, agreeing with F1 from an independent direction: strata 3–4
must stay **out of the canonical vector** (verifier-not-in-the-vector). This analysis
adds the emergence nuance: stratum-2 content *is* in the vector already (classification
clauses, ∃-structure — Π reads out what the encoder binds in), so the real fork is only
about the residue, and X3-style geometric encoding of `NOT(THERE-IS(...))` cardinality
clauses would inherit exactly the X3-measured NOT-invisibility pathology. Fork F4 prices
the remaining uncertainty.

---

## 7. Part E — design forks and deciding experiments

Per the standing directive: where §§2–6 could not decide, the answer is a fork. Each
fork: options / why uncertain / deciding experiment / metric + kill criterion.

**F1 — Read-out-DL (Π-projection) vs bolt-on-only.**
*Options:* (a) implement Π (§3.2) as a deterministic projector; sidecar carries only the
residue; Π output is regenerable annotation. (b) All axioms authored in the sidecar;
explications stay logic-opaque. (c) Π as *normative* (gate-checks sidecar⊥Π
consistency).
*Uncertain because:* Π's soundness on scenario-script clauses is unmeasured — scripts
may encode typicality, and Π would promote it to necessity.
*Experiment:* implement Π over kernel-v0 (54 records) + the gist walkthroughs; emit OWL;
(i) compare derived axioms against the gist's hand-authored ones on the walkthrough
records (does Π recover `promise ⊑ words`? it cannot recover `event disjointWith
endurant` — confirming the partition); (ii) reasoner-classify and score derived
subsumptions against a human gold set over the 54 concepts.
*Metric / kill:* precision of derived subsumptions vs gold. **Kill for (a)/(c): precision
< 0.9** (unsound read-outs ⇒ Π cannot be trusted as more than lint); kill for (c)
additionally if Π and any endorsed sidecar axiom conflict on the v0 corpus.

**F2 — NSM-native axiom syntax (X3 + pins) vs kot-axiom/1 (F1's design) for the residue.**
*Options:* (a) AxiomSchema in the explication grammar — one grammar, NSM-legible,
requires profile-1L pins; (b) kot-axiom/1 sidecar — checkable today, SHACL-CW semantics,
second language; (c) both, with a deterministic X3→kot-axiom/1 lowering (NSM as
authoring surface, SHACL as checking form).
*Uncertain because:* the pins stipulate classical readings of natural-semantic primes —
authoring-error and reviewer-dispute rates unknown; conversely a second language has its
own divergence surface.
*Experiment:* author the same 20-axiom set (litmus + kinship + a disjointness batch from
gufo/gist) in both syntaxes with two independent authors each; measure authoring error
rate (validator-caught + review-caught), record size, and LLM decode-legibility (can a
model translate each form back to accurate English — the A5 consumption mode).
*Metric / kill:* **kill for (a) if it needs > 2× authoring effort or the pins produce
unresolved semantic disputes among reviewers**; kill for (b) if its axioms are
systematically mistranslated by the decode-legibility probe while (a)'s are not.

**F3 — Lean-derived facts minted into the kernel vs Metamath-only identity.**
*Options:* (a) status quo: Metamath grounds identity; Lean = lean-ref annotations +
verified bridges (§5.3's protocol); (b) mint in-fragment Lean statements through F;
(c) no theorem mass at all (definitions only).
*Uncertain because:* the fragment size is unmeasured, LLM location accuracy is
unmeasured, and no E-series consumer of theorem mass exists yet.
*Experiment:* the §5.3 measurement — fragment-gate rate on 1,000 random Mathlib
declarations; F-verified LLM location rate on math-v0's Mathlib-overlapping records;
round-trip fixed-point rate.
*Metric / kill:* **kill for (b) if fragment rate < 1% or verified-location < 80% top-5
on the easy set**; kill for the bridge programme generally if F-verification almost
never confirms LLM candidates (the locator would then be decoration, not
infrastructure).

**F4 — Constraints vectorised vs constraints as verifiable sidecar.**
*Options:* (a) fold projected-axiom content into v(c); (b) vectors stay
explication-only; constraints are discrete checkable objects (F1's
verifier-not-in-the-vector).
*Uncertain because:* barely — X3's measured NOT-invisibility plus §6's stratum argument
near-decide (b); the open sliver is whether *any* consumer (E8-style) benefits from
geometric axiom presence.
*Experiment:* encode kernel-v0 twice (with/without a projected-axiom pseudo-clause
block); run X1-style single-edit margins on axiom edits (`max 2 → max 3`) and an
E2-style RDM delta.
*Metric / kill:* **if axiom-block inclusion worsens single-edit margins (expected, per
X3 logic) and adds no RDM signal, (b) is confirmed and the fork closes.** Low priority;
run only if fork F1 lands on (a)/(c).

**F5 — The AND-under-operator gap: extend (X1) vs curry/pins vs prohibit.**
*Options:* (a) ClauseGroup node in kot-ast/2 (encoder + identity version bump); (b) live
with currying (P1) and OTHER-tricks; (c) declare the native fragment ∃-conjunctive-only
and leave ⊔/≤n(n≥3) to the sidecar exclusively.
*Uncertain because:* the extension's cost is concrete (version bump, X0 regen, re-mint)
while its demand is unmeasured.
*Experiment:* over fork F2's 20-axiom set + the residue axioms F1's experiment surfaces,
count the fraction inexpressible without AND-under-operator.
*Metric / kill:* **if < 20% need it and all are sidecar-expressible, choose (c)** and
close; revisit only on a concrete blocked axiom class.

**F6 — Apply-clause (X5) vs inline-only relational reuse.**
*Options:* (a) add apply-clauses bound against RelationalSchema signatures (kot-ast/2);
(b) keep inlining defining clauses.
*Uncertain because:* inlining is known to burn the structure budget
(deterministic-concept-vectors §7.4) but the *actual* frequency of relational reuse in
authored corpora is unmeasured.
*Experiment:* static count over kernel-v0 + molecules-v0 + the F2 axiom set: how many
records inline what a RelationalSchema reference could carry; project depth/clause-cap
pressure at bulk scale under both options.
*Metric / kill:* **if inlining forces cap violations or >1.5× clause growth on > 10% of
records at bulk scale, (a) wins**; if reuse is rare, defer X5 with F5.

**F7 — The semantics pin for explications: necessary-conditions vs equivalence vs
defeasible-script.**
*Options:* Π (and any DL read-out) is sound only under a pinned reading: (a) explication
= necessary conditions (`C ⊑ Π(C)` — safe direction for read-out); (b) equivalence
(`C ≡ Π(C)` — licenses instance classification, much stronger); (c) defeasible script
(no sound read-out; Π is lint only).
*Uncertain because:* NSM's own theory says (c); the stipulative posture permits (a) or
(b) but nobody has measured which stipulation survives contact with instances.
*Experiment:* for ~20 concepts × ~10 instance descriptions (world-layer-shaped test
data), have independent annotators judge necessity violations (an instance of C failing
Π(C)) and sufficiency violations (a non-C satisfying Π(C)).
*Metric / kill:* **kill (b) if sufficiency failures > 10%; kill (a) if necessity
failures > 10%** — in which case (c) stands and fork F1 resolves to bolt-on
automatically.

Sequencing note: F1 and F7 are the upstream pair (cheap, this box, no GPU); F2 depends
on F1's residue list; F3 is independent and pre-registerable now; F5/F6 wait on F2's
counts; F4 runs only if needed. None requires the ~5-agent cap to be exceeded or a
rented box except F3(i)'s Mathlib sample crawl (fallback route already specced in
design-lean-route §5.2).

---

*Primary sources — repo: encoder/src/lexicon.ts, encoder/src/ast.ts,
data/kernel-v0/concepts/{event,promise}.json, data/molecules-v0, data/math-v0,
docs/design-{math-sector,lean-route,molecule-tier,hash-input,constraint-layer}.md,
docs/architecture.md §1–§4, reports/deterministic-concept-vectors.md §7,
reports/sparq-estate.md §4, notes/panel-kernel-design-review.md,
../concept-gist/concept-hash-design.md §3–§6, §13. External anchors (all previously
cited in-repo): W3C OWL 2 profiles (EL/QL/RL cardinality exclusions — via
design-constraint-layer.md); DRT referent semantics (Kamp/Heim, standard); Goddard &
Wierzbicka chart v20 (2022); Unison hashing docs; Metamath/set.mm; Carneiro MM0
(arXiv:1910.10703); design-lean-route.md's Mathlib route survey [measured 2026-07-07].*
