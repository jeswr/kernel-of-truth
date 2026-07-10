# Design memo — `kot-query/1` `define`-op (genus-differentia definitional checkability)

**Status:** DESIGN MEMO. Nothing here spends money, ingests bytes, edits the
onto-obo extractor / `tools/mint`, freezes a registry entry, or writes
`registry/`. It specifies a fifth `kot-query/1` operator (`define`), its
licensing axiom, the mapper-parse leg, the soundness/leak envelope, and the
Opus implement-then-measure plan. Fable owns the design; Opus owns
implementation + the census MEASUREMENT.
**Author:** Kern (architecture-advisor, Fable agent), for @jeswr. Date: 2026-07-09.
**Bead:** the new P1 "Design kot-query/1 `define`-op" (the cheapest κ_B lever,
`docs/next/coverage-growth-ingestion-plan.md` §4/§5/§7, 7fm sign-off).
**Binding constraints:** `docs/kernel-design-directives.md` (§1 native formalism —
no RDF/OWL/SHACL/DL semantics imported; §2 two value theses; §5 strata separation);
`docs/design-constraint-layer.md` §3.3/§3.5 (the `kot-axiom/1` grammar + sidecar-
endorsement decision); `docs/design-l3a-rules-engine-oracle.md` §4 (the closed
`kot-query/1` grammar, licensing + fail-closed refusal codes this op extends);
`docs/next/architecture-ladder.md` §10 (N1-LB, the b-cov census that MEASURES the
delta). Epistemic tags per `docs/next/assumption-register.md`:
**[MEASURED]** (committed data / verified engine behaviour), **[verified-in-repo]**
(checked on disk in this pass, 2026-07-09), **[LIT-BACKED]**, **[STIPULATED]**
(design choice), **[EXTRAPOLATION]** (projection, never a premise, none load-bearing).

---

## 0. The one-paragraph answer, and the three-legs frame it must satisfy

The `define`-op adds **definitional retrieval + structural definitional-equality**
to the closed query grammar, over the genus-differentia `logicalDefinition` the
onto-obo extractor already carries inside record identity. It is the cheapest
checkability lever because it needs **zero new ingestion**: the substrate is
already committed and minted.

PREMISE: onto-obo already carries 9,303 GO genus-differentia logical definitions
  (9,307 `logicalDefinition` fields, 9,384 differentia-bearing across GO+PO), each a
  structured `{genus:[urn], differentiae:[{property, filler:urn}]}` object inside
  record identity, and every onto-obo record is minted to a `urn:kot:` URN via
  `data/onto-obo/minted-urns.jsonl`.
  [MEASURED: `data/onto-obo/README.md` counts; `grep -c logicalDefinition go.jsonl`
  = 9307; `data/onto-obo/minted-urns.jsonl` `{id → urn}` bridge, verified-in-repo 2026-07-09]

The governing fact from the ingestion plan is non-negotiable and shapes the whole
design: **checkability is three legs coinciding, not vocabulary coverage.**

PREMISE: an item is `kernel_checkable` only when (1) a canonical **record** backs
  the proposition, (2) a **licensing axiom** in the sidecar admits the answer, and
  (3) a **mapper parse** lands the item in the closed `kot-query/1` grammar; the four
  existing ops (`unique`/`lookup`/`count`/`instance`) never exceed the grammar or the
  engine's `subClassOf` refusal.
  [MEASURED: `docs/next/coverage-growth-ingestion-plan.md` §0; `tools/axiom/kot_axiom.py`
  `QUERY_OPS`, `ERR_AXIOM_UNIMPLEMENTED` on `subClassOf`, verified-in-repo]

This memo supplies leg 1 (the logicalDefinition record — already present), designs
leg 2 (a new `definitional` endorsement), and designs leg 3 (the define-question
mapper parse). It does **not** assert any κ_B number — that is what the b-cov
census MEASURES after Opus implements (§7).

---

## 1. The substrate, verified (leg 1 — the record already exists)

DECISION: the `define`-op operates over the onto-obo `logicalDefinition` object
  verbatim, resolved to `urn:kot:` URNs through the existing mint bridge — it invents
  no new record and touches no extractor.
  [MEASURED: verified-in-repo 2026-07-09 — `data/onto-obo/go.jsonl`, `data/onto-obo/minted-urns.jsonl`]

The committed shape of one logical definition (GO:0000018 *regulation of DNA recombination*):

```json
"logicalDefinition": {
  "form": "obo-genus-differentia",
  "operator": "intersection_of",
  "genus": ["urn:onto-obo:GO_0065007"],
  "differentiae": [ { "property": "regulates", "filler": "urn:onto-obo:GO_0006310" } ]
}
```

Two resolution facts govern the design:

- **Genus and filler are `urn:onto-obo:` class IRIs** and each has a minted
  `urn:kot:` URN in `minted-urns.jsonl` (`id → urn`). The engine's
  `CONCEPT_URN_RE` (`^urn:kot:[a-z2-7]{10,}$`) matches minted onto-obo URNs
  [verified-in-repo], so a resolved genus/filler is a first-class concept URN the
  grammar already accepts.
- **The differentia `property` is a bare OBO shorthand string** (`regulates`,
  `positively_regulates`, `negatively_regulates`, `part_of`, `occurs_in`,
  `has_part`, `happens_during`, `participates_in`, `has_participant`,
  `develops_from` — a **10-value closed histogram** over GO+PO differentiae)
  [MEASURED: histogram over `go.jsonl`+`po.jsonl`, verified-in-repo 2026-07-09],
  **not** a URN. It must be resolved to a relation-concept `urn:kot:` URN through a
  pinned alias table (§3.3). This is the one genuine resolution gap and it is
  bounded: ten shorthands cover the entire GO+PO differentia corpus.

---

## 2. The `define`-op grammar form (leg 3, gold-parse layer)

Two query forms under one op, both answered by **deterministic index lookup +
exact structural comparison** — no search, no similarity, so the X3 cosine ban is
trivially honoured (as with the four existing ops).

DECISION: `define` has exactly two shapes — DEFINE (retrieve the endorsed
  definition of a concept) and DEFINE-MATCH (test a candidate definition for exact
  structural equality against a concept's endorsed definition). No third shape; each
  addition is a grammar-version change.
  [STIPULATED: ASM-0015 — the closed two-shape design; see §8]

### 2.1 DEFINE — retrieve

```json
{ "op": "define", "subject": "urn:kot:<X>" }
```

- **Answer** (on license + record):
  ```json
  { "status": "answer",
    "value": { "form": "genus-differentia",
               "genus": ["urn:kot:<G>", ...],
               "differentiae": [ { "relation": "urn:kot:<R>", "filler": "urn:kot:<F>" }, ... ] },
    "provenance": ["<onto-obo record id backing X's logicalDefinition>"],
    "license":    ["<endorsement ref, e.g. defn-onto-obo-go#0>"] }
  ```
  The value is the concept's own stipulated definition, returned **at one level,
  verbatim** — genus set + the sorted, resolved differentia tuples. There is **no
  recursive expansion** of the genus's own definition and **no transitive closure**
  (that would be subsumption inference — refused, §6).
- **Refusals** (fail-closed, each a named code):
  - `ERR_BAD_QUERY` — malformed op/fields, or `subject` not a `urn:kot:` URN.
  - `ERR_TERM_UNLICENSED` — `subject` is not in the definitional endorsement's
    admitted set (its shard is not endorsed as a definitional-source).
  - `ERR_NO_DEFINITION` — `subject` is licensed but carries no `logicalDefinition`
    (the 33k+ GO terms with only `is_a`, and all of BFO/RO/PATO — most of the corpus).
  - `ERR_DEFN_UNRESOLVED` — a differentia `property` shorthand or a genus/filler
    IRI fails to resolve to a licensed `urn:kot:` URN under the pinned tables
    (fail-closed: a partially-resolvable definition is refused, never half-answered).

### 2.2 DEFINE-MATCH — verify a candidate definition

```json
{ "op": "define", "subject": "urn:kot:<X>",
  "candidate": { "genus": ["urn:kot:<G>", ...],
                 "differentiae": [ { "relation": "urn:kot:<R>", "filler": "urn:kot:<F>" }, ... ] } }
```

- **Answer**: `value: true` iff the canonicalised candidate tuple is **exactly
  structurally equal** to X's endorsed definition tuple; `value: false` otherwise.
  Canonicalisation: genus as a sorted URN set; differentiae as a sorted set of
  `(relation-URN, filler-URN)` pairs; equality is set-equality on both components
  (no ordering dependence, no partial credit, no subset match).
- **Why a licensed `false` is sound here — the load-bearing distinction from the
  four existing ops:**

  LOAD-BEARING: DEFINE-MATCH may license a definitive `false`, unlike
  `lookup`/`instance` which refuse on absence, because a `logicalDefinition` is a
  **closed, complete object about its own definiendum** (the whole endorsed
  definition of X), not an open set of world facts under CWA — so "candidate ≠ X's
  definition" is a licensed negative, not an incompleteness.
  [STIPULATED: ASM-0016 — definitional-closure licenses `false`; contrast the
  world-layer CWA-absence rule in `docs/design-l3a-rules-engine-oracle.md` §4]

  This is exactly the property that makes def-match MMLU items checkable: the
  correct option licenses `true`, the distractor options license `false`.
- **Refusals**: as §2.1, plus `ERR_BAD_QUERY` for a malformed `candidate`.

### 2.3 Engine surface (Opus implements; not edited here)

- `QUERY_OPS` gains `"define"`; the shape gate learns the two field sets
  (`{op,subject}` and `{op,subject,candidate}`).
- New refusal codes `ERR_NO_DEFINITION`, `ERR_DEFN_UNRESOLVED` join `REFUSAL_CODES`.
- The engine gains a **definitional index** `defn[urn:kot:X] → resolved tuple`
  built at load from the endorsed onto-obo shard(s) via the mint bridge + the
  alias table; unresolved definitions are dropped from the index and cause
  `ERR_DEFN_UNRESOLVED` on query (fail-closed), never silently omitted from an answer.
- Determinism house rule preserved: all sets sorted before emission.

---

## 3. The licensing axiom (leg 2 — a stratum-3 `definitional` endorsement)

The logicalDefinition lives in **stratum 2** (the onto-obo record's identity —
`docs/design-constraint-layer.md` §3.5 arg 4: "axioms constitutive of the
stipulated meaning may live inside identity — AxiomsOnly records"). But onto-obo
records carry `semanticStatus: "AxiomsOnly"` — **NO semantic-adequacy claim**
[MEASURED: `data/onto-obo/README.md` honesty architecture]. So the programme must
not treat every ingested logical definition as answer-authoritative by default. The
missing leg is an explicit **endorsement**: a governance act admitting a pinned
definitional substrate into the `define`-op's answerable set.

DECISION: the licensing axiom is a **stratum-3, corpus-scoped `definitional`
  endorsement record** — one sidecar record admits a pinned onto-obo shard's
  logicalDefinitions (by shard name + `sourceVersion` sha) as a definitional-source,
  with an optional per-concept override for contested definitions.
  [STIPULATED: ASM-0017 — corpus-scoped endorsement as the default granularity; see §8]

Rationale: 9,303 per-concept endorsement records buy nothing over one shard-scoped
record when the whole GO shard shares one provenance, one `semanticStatus`, one
licence, and one extraction sha — and a corpus-scoped endorsement keeps the
endorsement act legible and cheap (mirrors onto-obo's existing corpus-level
`provenance.license`). Per-concept override is retained because a federation may
wish to *dis*endorse a specific contested definition without dropping the shard.

### 3.1 Endorsement record shape (v0 sketch)

```json
{ "schema": "kot-axiom/1",
  "subject": "urn:kot:<minted onto-obo corpus-marker URN>",
  "constraints": [
    { "kind": "definitional",
      "form": "obo-genus-differentia",
      "source": { "corpus": "onto-obo", "shard": "go.jsonl",
                  "sourceVersion": "sha256:<pinned>" } } ] }
```

DECISION (subject convention — the pin the census flagged as open): the
  endorsement's `subject` is a **minted onto-obo corpus-marker URN** (one stable
  `urn:kot:` URN naming the endorsed corpus), NOT a per-concept URN and NOT the
  shard string. The endorsement's admitted set is keyed off `source.{corpus,shard,
  sourceVersion}` (shard membership), so `subject` names the endorsing governance
  act, is not consulted by the define-op index, and does not affect any coverage
  count; the per-concept-override case (§3, disendorsement) is the only path that
  ever puts a concept URN in `subject`, and it is out of scope for the corpus-scoped
  v0 records. This retires the `__PENDING_FABLE_SUBJECT_PIN__` fail-closed stub the
  census staged; the three v0 records (`defn-onto-obo-{go,so,mondo}.json`) each carry
  a minted corpus-marker URN and validate.
  [STIPULATED: ASM-0130 — endorsement subject = minted corpus-marker URN; registered
  2026-07-10 to close census boundary-stop #1; see §8/§10]

DECISION: `definitional` is a **new `kot-axiom/1` constraint kind**, added to
  `CONSTRAINT_KINDS` and `IMPLEMENTED_KINDS`; it is an *endorsement*, not an
  extension-constraint, and it is validated + consumed only by the `define`-op —
  it never enters the CWA store-validation pass over world-layer facts.
  [STIPULATED: ASM-0018 — `definitional` as an endorsement-kind disjoint from the
  extension-constraint kinds `{functional, cardinality, disjointWith, inverseOf,
  domain, range}`; see §8]

This keeps strata separation clean (directives §5): the **definition** is stratum 2
(in identity, in the vector/hash — verifier-not-in-the-vector is untouched: the
op reads the *record*, not the vector); the **endorsement** is stratum 3 (sidecar,
a governance act); **no world-layer (stratum 4) fact is involved at all** — the
`define`-op is the first `kot-query/1` op that answers from strata 2+3 with no
stratum-4 dependency. That is precisely why it needs no ingestion.

### 3.2 Why not fold it into the existing ops

`subClassOf` is refused (`ERR_AXIOM_UNIMPLEMENTED`) and the genus *is* an is-a edge
— so one might reach for a `subClassOf` op. That is the wrong move and §6 explains
why (it would smuggle DL subsumption). The `definitional` endorsement licenses
**retrieval of the stipulated definition and equality against it**, never a
subsumption inference, so it does not touch the `subClassOf` refusal.

### 3.3 The pinned relation-shorthand alias table (part of the licence machinery)

> **SUPERSEDED — successor implemented (bead `kernel-of-truth-8es`, committed
> `6bf9d72`; verified-in-repo 2026-07-10).** The "cleaner long-term fix" the
> DECISION at the foot of this section filed as a successor is now **DONE**: the
> onto-obo extractor (`data/onto-obo/extractor/extract.mjs`,
> `buildRelationResolver` / `resolveRel`) resolves each differentia `property`
> shorthand to its canonical minted relation `urn:onto-obo:` IRI **at extraction
> time**, derived purely from the sources' own Typedef `xref:` declarations
> (no hand-authored table), fail-closed (`ERR_OBO_REL_AMBIGUOUS`,
> `ERR_OBO_REL_UNRESOLVED`). Every minted onto-obo shard now carries a resolved
> `relation: urn:onto-obo:…` field per differentia (go/cl/mondo/po/so/uberon —
> verified-in-repo 2026-07-10), and the define-index reads that field first
> (bead `kernel-of-truth-o6pj`, `tools/axiom/kot_axiom.py`
> `_resolve_logical_definition`), keeping `PINNED_RELATION_ALIASES` below ONLY as
> a fail-closed fallback for a hypothetical pre-8es shard lacking the field — no
> longer the primary path. Because resolution is now source-driven rather than a
> GO+PO-only table, it is what unlocked SO/MONDO define-op resolution
> [MEASURED: define-op census RE-RUN post-8es, commit `f64ba35` — 13,270/17,211].
> The table below is retained verbatim as the frozen provenance of the ten GO+PO
> shorthands and their LIT-BACKED RO/BFO targets; it is **no longer the live
> resolution mechanism**. The §1 statement that a shorthand "must be resolved …
> through a pinned alias table (§3.3)" is superseded in the same way.

The differentia `property` shorthands must resolve to relation-concept `urn:kot:`
URNs. The extractor currently stores them as bare strings, so the `define`-op
carries a **closed, pinned alias table** — shorthand → the onto-obo relation
record's `urn:onto-obo:` IRI → its minted `urn:kot:` URN via the mint bridge:

| shorthand | relation IRI (RO/BFO) | count in GO+PO |
|---|---|---|
| `part_of` | `BFO:0000050` | 1,165 |
| `regulates` | `RO:0002211` (id `regulates`) | 2,915 |
| `positively_regulates` | `RO:0002213` | 2,586 |
| `negatively_regulates` | `RO:0002212` | 2,564 |
| `occurs_in` | `BFO:0000066` | 177 |
| `has_part` | `BFO:0000051` | 53 |
| `happens_during` | `RO:0002092` | 9 |
| `participates_in` | `RO:0000056` | 2 |
| `has_participant` | `RO:0000057` | 1 |
| `develops_from` | `RO:0002202` | 1 |

[MEASURED counts: histogram over `go.jsonl`+`po.jsonl`, verified-in-repo 2026-07-09.
The IRI mappings are the standard OBO relation shorthands — LIT-BACKED against the
OBO Relation Ontology; Opus MUST verify each shorthand resolves to a relation record
actually present + minted in the pinned onto-obo shards, and fail-closed
(`ERR_DEFN_UNRESOLVED`) on any that do not, rather than trusting this table.]

DECISION (filed as a successor, not done here): the cleaner long-term fix is to
resolve differentia `property` shorthands to relation IRIs **at extraction time**
in the onto-obo extractor (so the record carries `relation: urn:onto-obo:...`
instead of a bare string). That is another agent's turf (`kernel-of-truth-4im`
neighbourhood) — recommended, not performed here. Until then the pinned alias
table is the fail-closed bridge.
[SUPERSEDED / DONE 2026-07-10: implemented in bead `kernel-of-truth-8es`
(commit `6bf9d72`) exactly as described — the extractor now writes
`relation: urn:onto-obo:…` per differentia and this successor is no longer
pending. See the SUPERSEDED banner at the head of §3.3.]

---

## 4. How this makes a logicalDefinition record `kernel_checkable`

The three legs now coincide on a definitional item ("what is X / X is a Y that Zs /
which term means G that R F"):

| Leg | Supplied by | State |
|---|---|---|
| 1. canonical **record** | the onto-obo `logicalDefinition` (stratum 2, minted) | **already committed** [MEASURED] |
| 2. **licensing axiom** | the `definitional` corpus-scoped endorsement (stratum 3) | designed here (§3); Opus authors one record |
| 3. **mapper parse** | define-question template → `define` query (§5) | designed here (§5); Opus implements |

Before this op, an OpenBookQA/def-MMLU/WiC item touching an onto-obo term had legs
1 (sometimes) but **never legs 2 or 3** — the four ops have no way to consult a
definition — so `kernel_checkable = false`, exactly the d-ext datum (≈49%
lemma-touch coexisting with 0% checkable) [MEASURED: `data/d-ext/manifest.json`].
The `define`-op is the machinery that converts leg-1-present definitional items to
`kernel_checkable = true` **without ingesting a byte**.

Scope honesty, stated up front: the substrate is **biomedical** (GO/PO). The
def-MMLU biomedical subjects (college biology/chemistry, med-genetics, anatomy via
the CL/UBERON unblock) are the natural yield; **WiC is general-vocabulary and mostly
NOT biomedical**, so its `define`-checkable yield may be small or ~0.

The WiC / def-MMLU κ_B yield of the `define`-op is a projection, not a
measured quantity, and is resolved only by the b-cov census after implementation —
it is never a premise for building the op or for any downstream claim.
[EXTRAPOLATION: ASM-0019, `load_bearing:false`, resolution_path = b-cov census re-run §7]

---

## 5. The mapper-parse leg (define-question recognition)

Per the L3a stage-indictment rule, the NL/mapper leg is a **separate gated stage**
counted apart from gold-parse: κ_B^engine is reported for **gold-parse** (query
posed directly in the grammar) and **mapper-parse** (deterministic template
recognition) separately [MEASURED design constraint:
`docs/next/architecture-ladder.md` §10.1 + §8 item 14]. The `define`-op design
must specify both; §2 gave the gold-parse form, this section the mapper leg.

### 5.1 Two deterministic steps

The mapper (`mapper/src/mapper.ts`) is a deterministic phrase→concept transducer
whose first discipline is **ABSTAIN, never silently pick** on ambiguity
[verified-in-repo]. The define-question parse adds a thin template layer on top:

1. **Question-template recognition (closed set).** A small pinned set of surface
   templates, each mapping to a `define` shape:
   - DEFINE: `"what is <TERM>?"`, `"define <TERM>"`, `"the definition of <TERM>"`
     → `{op:"define", subject:URN(TERM)}`.
   - DEFINE-MATCH: `"is <TERM> a <GENUS> that <REL> <FILLER>?"`,
     `"<TERM> is defined as <GENUS> that <REL> <FILLER>"`, and the def-MMLU
     option-matching form `"which term means <GENUS> that <REL> <FILLER>"`
     (evaluated per option) → `{op:"define", subject:URN(TERM), candidate:{...}}`.
   Templates are a **closed, pinned inventory** (a grammar artefact, versioned);
   anything not matching a template is `unmapped` (no answer), never guessed.
2. **Concept resolution `TERM/GENUS/FILLER → urn:kot:`.** Resolution is
   **annotation-driven**: onto-obo `annotations.label` (and `synonyms`) form a
   label→URN index (labels are outside identity — mutable annotations — so using
   them for parsing never touches identity, the same Princeton-gloss boundary the
   mapper already respects). The mapper's existing rule holds verbatim: exactly one
   distinct URN for a label ⇒ map; **more than one ⇒ ABSTAIN** (label collisions
   are common across 40k terms and must never be silently resolved); zero ⇒ unmapped.
   `REL` resolves through the §3.3 alias table.

DECISION: the mapper leg reuses the existing abstain-and-record discipline verbatim
  and adds only a closed template inventory + an annotation-label index; it resolves
  no word sense and no ambiguous label, so a mapper-parse is emitted only when TERM,
  GENUS, REL, FILLER each resolve to exactly one URN.
  [STIPULATED: ASM-0020 — mapper-leg = closed templates + abstain-on-ambiguity; see §8]

### 5.2 The mapper risk the census will price

The mapper leg is where the loss lives: label ambiguity, template coverage, and
in-context sense resolution. The ladder already names this as "the risk the census
will price" for the {WiC, CommonsenseQA} route [MEASURED design note §10.4]. The
design does not estimate that loss — the census measures gold-parse vs mapper-parse
yield separately so the loss fraction is a MEASURED quantity, not a guess.

---

## 6. Soundness & leak constraints — staying kot-native (directives §1)

This is the load-bearing section. The `define`-op reads a construct
(`intersection_of` genus-differentia) whose *source* is an OWL `equivalentClass`
conjunction [MEASURED: `data/onto-obo/README.md`]. The design must import **zero OWL
semantics**. Six constraints, each fail-closed:

- **C1 — no subsumption inference; the `subClassOf` refusal is respected.**

  LOAD-BEARING: the `define`-op performs definitional **retrieval** and structural
  **equality** only — it never computes a subclass/genus transitive closure, never
  answers "is X a kind of Y", and never classifies an instance; the engine's
  `subClassOf` refusal (`ERR_AXIOM_UNIMPLEMENTED`) is untouched and unreachable
  through `define`.
  [MEASURED: `tools/axiom/kot_axiom.py` refuses `subClassOf`; the `define`
  index stores the genus as a *labelled component of the returned definition*, with
  no closure step anywhere in the design]

  The genus is returned as "the genus of X's definition is G", verbatim as onto-obo
  stipulates it — retrieval of stored definitional data, not reasoning over it.
  Answering "is X a Y" from the genus would be the refused subsumption op and is
  explicitly out of scope; if that capability is ever wanted it is a *separate*
  `subClassOf`-op design (`docs/design-l3a-rules-engine-oracle.md` §7 successor 4),
  not a reinterpretation of `define`.

- **C2 — no OWL/DL model theory.** No open-world reasoning, no classification, no
  entailment, no `equivalentClass` bidirectional inference. The only semantics are
  (a) lookup of a stored tuple and (b) exact set-equality of two tuples. This is a
  native kot operation over kot data; RDF/OWL is at most an explicitly-lossy export
  of the *definition record*, never a validation reference here (directives §1).

- **C3 — no similarity/cosine anywhere (X3 ban).** DEFINE-MATCH is exact structural
  set-equality, never overlap scoring, never nearest-definition. A candidate that
  shares the genus but differs in one differentia is `false`, full stop.

- **C4 — fail-closed resolution.** A definition with any unresolvable differentia
  shorthand, genus, or filler is dropped from the index and refused
  (`ERR_DEFN_UNRESOLVED`) — never half-answered. Uniqueness is never assumed from
  data; a term outside the endorsed shard is `ERR_TERM_UNLICENSED`.

- **C5 — definitional-collision is a census-side eligibility filter, not an engine
  hazard.** Two distinct concepts can share an identical genus-differentia tuple. For
  DEFINE-MATCH this is sound (the op answers "is this X's definition", which is
  well-defined per subject). But a def-MMLU *item* whose candidate definition matches
  ≥2 terms is genuinely ambiguous as a question; the census must drop such items from
  the checkable slice (a definitional-uniqueness precondition on item eligibility),
  keeping the op sound and the item honest. Filed as a census predicate, §7.

  **C5 operationalization (the exact census-side algorithm, so hu10 is a mechanical
  build).** The filter is computed over the SAME endorsed definitional index the
  engine builds (`defn[urn:kot:X] → {genus, differentiae}` from the union of endorsed
  shards; §2.3), with no new resolution path and no engine change:
  1. **Build the definitional inverse index once, at census load:**
     `inv[key] → sorted set of licensed concept URNs`, where
     `key = canonicalise(defn[X])` and `canonicalise` is EXACTLY the §2.2
     DEFINE-MATCH canonical form — genus as a sorted `urn:kot:` set, differentiae as a
     sorted set of `(relation-URN, filler-URN)` pairs — serialised deterministically
     (e.g. the sorted-tuple JSON) as the map key. Only resolved entries (`X ∈ defn`,
     i.e. not `defn_unresolved`/`ERR_NO_DEFINITION`) contribute; unresolved concepts
     are never a collision partner.
  2. **Per candidate-bearing item** (a def-MMLU stem / WiC option whose candidate
     definition resolves to a canonical tuple `key_item` via the mapper leg, §5):
     look up `n = |inv.get(key_item, ∅)|` — the number of DISTINCT licensed concepts
     whose endorsed definition is structurally set-equal to the item's candidate.
  3. **Eligibility:** the item is `define-checkable` only if `n == 1` (exactly one
     licensed concept bears that definition — the answer is unambiguous). `n ≥ 2` ⇒
     the item is definitionally ambiguous ⇒ **dropped from the checkable slice**
     (recorded as `INELIGIBLE_DEFN_COLLISION`, a census-eligibility exclusion, NOT an
     engine refusal — the engine's DEFINE-MATCH stays sound per subject, §2.2). `n == 0`
     is not a collision: it is the ordinary "candidate matches no licensed concept"
     case, handled by DEFINE-MATCH `false` / the item's own gold key, never by C5.
  This filter is a property of the *item set*, is deterministic given the endorsed
  index + census hash, and is reported in the census row (N dropped by C5) alongside
  N_checkable/N_total. It touches neither the engine nor the mapper — it is pure
  census instrumentation over the already-built index.
  [STIPULATED: ASM-0131 — C5 = inverse-index collision count over the §2.2 canonical
  form, drop iff `n ≥ 2`; registered 2026-07-10; owner hu10; see §8/§10]

- **C6 — endorsement ≠ adequacy.** The `definitional` endorsement admits a shard as a
  *definitional-source*; it makes no semantic-adequacy claim about GO's biology
  (onto-obo's `AxiomsOnly` honesty is preserved). What the op certifies is: "the
  endorsed canonical definition of X is exactly this tuple" — a checkable, provenance-
  carrying, licence-carrying fact about the *record*, not a claim that the record is
  biologically correct. Every answer carries `provenance` (record id) + `license`
  (endorsement ref), exactly as the four existing ops do.

---

## 7. The Opus implement-then-measure plan (Opus executes; never concludes)

Fable owns this design; Opus owns implementation + the census MEASUREMENT (the
Fable/Opus split — Opus runs and reports the mechanical verdict, never designs or
concludes). The census is the ONLY honest measure of whether the op moved κ_B.

### 7.1 Implement (Opus, pure execution of this design)

1. **Engine** (`tools/axiom/kot_axiom.py`): add `"define"` to `QUERY_OPS`; the
   two-shape gate; `ERR_NO_DEFINITION` + `ERR_DEFN_UNRESOLVED` to `REFUSAL_CODES`;
   the `definitional` kind to `CONSTRAINT_KINDS`+`IMPLEMENTED_KINDS` with its
   endorsement validation (disjoint from the CWA store pass); the definitional index
   builder (onto-obo shard + mint bridge + §3.3 alias table, fail-closed).
2. **Endorsement record**: author one `definitional` sidecar record per endorsed
   shard (GO first; PO trivially), pinning the shard sha. This is leg 2.
3. **Alias-table verification**: confirm each §3.3 shorthand resolves to a relation
   record present + minted in the pinned shards; fail-closed on any miss (do not
   trust the table — verify at source).
4. **Mapper leg** (`mapper/`): the closed define-question template inventory + the
   onto-obo `annotations.label`/`synonyms` label→URN index with abstain-on-collision;
   gold-parse and mapper-parse kept as separate code paths for separate census counts.
5. **Unit + determinism tests** in the house style: fail-closed codes exercised,
   byte-identical repeat, DEFINE-MATCH true/false/collision cases, unresolved-differentia
   refusal, `subClassOf`-refusal-untouched regression.

### 7.2 Measure (Opus, the b-cov census — the delta is MEASURED here, never asserted)

DECISION: the κ_B delta is established **only** by re-running the b-cov census
  (`docs/next/architecture-ladder.md` §10.1, Tier 0, ~$0, CPU-only, no model calls)
  over the Tier-A definitional benchmarks **before and after** the `define`-op lands,
  reporting κ_B^engine for gold-parse and mapper-parse **separately**, with the m0b
  envelope discipline (benchmark-indexed, restated verbatim, coverage-first).
  [MEASURED: design constraint — architecture-ladder.md §10.1/§10.5]

- **Benchmarks**: the census Tier-A definitional set — WiC and the definitional-MMLU
  biomedical subjects (college biology/chemistry, medical genetics, anatomy,
  clinical knowledge, nutrition), plus OpenBookQA as the pinned d-ext control point
  (its 0% checkable is the before-baseline).
- **Instrument additions**: the census gains a κ_B^engine `define`-lane (gold + mapper)
  and the §C5 definitional-uniqueness item-eligibility filter.
- **Outputs**: N_total, N_checkable, κ_B per benchmark × {gold, mapper}, census hash,
  kernel-corpus hashes, endorsement hash, mapper hash, grammar version — appended as
  a trajectory point keyed to this kernel version.

### 7.3 Honesty guardrails (binding on every number the run emits)

- No κ_B growth may be claimed until the census MEASURES it; the
  before/after delta is the deliverable, and any pre-census number is EXTRAPOLATION.
  [EXTRAPOLATION resolved by §7.2; the delta enters no conclusion until measured]
- Coverage-first reporting (§10.5): every κ_B carries N_checkable/N_total + census
  hash + kernel version in the same row; a bare covered-slice number re-classifies as
  EXTRAPOLATION (engine law 9).
- Selection-effect disclosure: the `define`-checkable slice is biomedical and
  non-random; a covered win is never representative of the benchmark.
- WiC-yield honesty: if the census prices WiC `define`-checkability at ~0 (the
  substrate/benchmark mismatch, §4), that is a MEASURED null reported with the same
  prominence as any positive — not a disappointment to bury.
- Instrument-validity: if the census predicate and the runtime engine disagree on any
  item, the census is INSTRUMENT-INVALID and is fixed, never reinterpreted (§10.3).

### 7.4 Kill / null conditions (pre-declared, so a null is legible)

- If the census yields < the LB-GATE floor (≥500 checkable on ≥2 benchmarks, §10.4)
  after the op + the Wave-A/CL-UBERON substrate lands, the `define`-op is a MEASURED
  Axis-A (linter) win with **no LB-GATE κ_B unlock yet** — reported as such, not
  inflated. The op is not "failed"; its benchmark reach is simply measured and small.
- If DEFINE-MATCH `false`-licensing proves unsound on audit (a licensed `false` that
  should have been a refusal), ASM-DEF-2 falls and the op reverts to DEFINE-only
  (retrieval) pending redesign — the co-vendor audit is the check.

---

## 8. Assumptions to register (reported per constraint — NOT written to `registry/`)

I did not touch `registry/assumptions.jsonl` or `registry/ideas.jsonl` (concurrency +
task constraint). Recommended entries for Opus/maintainer to file (ASM-ids are
placeholders; the register assigns real sequential ids):

- **ASM-DEF-1** [STIPULATED] — `define` is the closed two-shape op (DEFINE +
  DEFINE-MATCH); owner: grammar; rationale: minimal surface for definitional
  checkability; falls if a third definitional question-class is found unrepresentable.
- **ASM-DEF-2** [STIPULATED] — definitional-closure licenses a definitive `false` in
  DEFINE-MATCH (a logicalDefinition is complete about its definiendum, unlike CWA
  world facts); owner: engine semantics; the cross-vendor audit is the check.
- **ASM-DEF-3** [STIPULATED] — corpus-scoped `definitional` endorsement is the default
  licence granularity (per-concept override retained); owner: governance.
- **ASM-DEF-4** [STIPULATED] — `definitional` is an endorsement-kind disjoint from the
  extension-constraint kinds and never enters the CWA store-validation pass.
- **ASM-DEF-5** [EXTRAPOLATION, `load_bearing:false`] — the WiC/def-MMLU κ_B yield of
  the op; resolution_path = the b-cov census re-run (§7.2). NEVER a premise.
- **ASM-DEF-6** [STIPULATED] — the mapper leg is closed templates + annotation-label
  index + abstain-on-ambiguity (no sense resolution); owner: mapper; the census prices
  the gold-vs-mapper loss.
- **ASM-DEF-7 = ASM-0130** [STIPULATED, REGISTERED 2026-07-10] — endorsement `subject`
  is a minted onto-obo corpus-marker URN (§3.1); owner: governance/design; closes
  census boundary-stop #1.
- **ASM-DEF-8 = ASM-0131** [STIPULATED, REGISTERED 2026-07-10] — §C5 = inverse-index
  collision count over the §2.2 canonical form, item dropped iff `n ≥ 2` (§6 C5);
  owner: hu10 census; the audit is DEFINE-MATCH per-subject soundness (ASM-DEF-2).

Recommended bead/register additions (not filed here): (1) the `define`-op engine +
mapper implementation bead (Opus, this design); (2) a successor bead for the onto-obo
extractor to resolve differentia `property` shorthands to relation IRIs at extraction
time (removes the §3.3 alias table) — another agent's turf; (3) a note to
`idea-leaderboard-benchmark-eval` that the b-cov census gains a `define`-lane.

---

## 9. Exact changed / created paths

- **Created:** `docs/design-kot-query-define-op.md` (this memo).
- **Changed (original authoring pass):** none.
- **Changed (2026-07-10 finalization pass, §10):** this memo — §3.1 subject pin,
  §6 C5 operationalization, §8 addenda, this §9 line, §10; and
  `registry/assumptions.jsonl` — appended ASM-0130, ASM-0131 (append-only, reserved
  block). No extractor, `tools/mint`, `tools/axiom/kot_axiom.py`, mapper, world-layer,
  or endorsement file touched by this pass; no pipeline run; no git commit/push.

---

## 10. Finalization addendum (2026-07-10) — bead 57b closure, readiness for 46f

This pass answers the 57b question — *is the define-op design implementation-ready
for 46f to build against?* — and closes the two design pins the define-op census
(`registry/assessments/define-op-census.json`, 0.7710) flagged as Fable
boundary-stops. **Verdict: YES, implementation-ready.** Both the query-semantics leg
and the mapper leg were already precise enough that a mechanical build exists and
follows this memo (verified-in-repo 2026-07-10); the two remaining open items were
design-role pins, now closed here.

### 10.1 The two pins closed here (were the only open gaps)

- **Subject convention (§3.1) — CLOSED.** Endorsement `subject` = a minted onto-obo
  corpus-marker URN [STIPULATED: ASM-0130]. Retires the census's
  `__PENDING_FABLE_SUBJECT_PIN__` fail-closed stub (boundary-stop #1). The three v0
  records already carry a minted corpus-marker URN and validate.
- **§C5 uniqueness filter (§6 C5) — CLOSED.** Operationalized as an inverse-index
  collision count over the §2.2 canonical form, drop iff `n ≥ 2` [STIPULATED:
  ASM-0131]. This is a census-side (hu10) predicate; it needs no engine or mapper
  change. It unblocks hu10 (next in the 57b→46f→hu10→j3iq chain).

### 10.2 Drift reconciliation (§3.3 alias table vs beads 8es/o6pj)

The §3.3 pinned relation-shorthand alias table was designed as the fail-closed bridge
"until" the extractor resolves shorthands at extraction time. Beads 8es (extractor
writes a resolved `relation` field) and o6pj (engine reads it) have since landed. The
engine (`_resolve_logical_definition`) now **prefers the resolved `relation` field
and falls back to the §3.3 alias table** when absent — byte-identical for GO/PO,
and the resolved field is what unlocked SO/MONDO (0.5478→0.7710). Both the memo and
the built engine keep the alias table as the closed fallback, so this is a
compatible superset, not a contradiction — 46f builds against both paths exactly as
already coded. No design change required.

### 10.3 Readiness checklist (each item verified-in-repo 2026-07-10)

| Design element | Spec | Build state (evidence) | Ready |
|---|---|---|---|
| Query semantics — DEFINE / DEFINE-MATCH shapes, refusal codes | §2 | engine `_query_define`, `_canonicalise_candidate` (`tools/axiom/kot_axiom.py`) | YES |
| Definitional index + fail-closed resolution (C4) | §2.3/§3.3/§6 | `_build_definitional_index`, `_resolve_logical_definition` (resolved-`relation` + alias fallback) | YES |
| `definitional` endorsement kind (disjoint from CWA store pass) | §3 | `CONSTRAINT_KINDS`+`IMPLEMENTED_KINDS`, `load_definitional_endorsements` | YES |
| Endorsement subject convention | §3.1 + **ASM-0130** | 3 records in `data/axioms-definitional-v0/` carry minted corpus-marker URN | YES (pinned here) |
| Mapper leg — closed templates + label→URN index + abstain | §5 | `mapper/src/defineTemplates.ts` (`parseDefineQuestion`, `DefineIndex`, `DefineParse`), separate gold/mapper paths | YES |
| §C5 definitional-uniqueness item filter | §6 C5 + **ASM-0131** | census-side (hu10), algorithm now pinned; needs no engine/mapper change | YES (spec'd here) |
| Soundness/leak envelope (C1–C6, X3 ban, subClassOf refusal untouched) | §6 | engine comments cite §6; no closure/cosine anywhere | YES |
| Implement-then-measure plan (b-cov before/after, gold vs mapper) | §7 | 46f (build) → hu10 (census lane) | plan frozen |

Nothing in the query-semantics or mapper-leg specs requires further design work: 46f
is a mechanical build of §2/§3/§5, and hu10 a mechanical build of §6 C5 + §7.2.
Coordinator may close 57b and unblock 46f.

---

*Cross-references:* `docs/next/coverage-growth-ingestion-plan.md` §4/§5/§7 (the
define-op recommendation + three-legs finding, 7fm sign-off);
`docs/design-l3a-rules-engine-oracle.md` §4 (the four ops + refusal codes this op
extends); `tools/axiom/kot_axiom.py` (the engine `define` extends);
`docs/design-constraint-layer.md` §3.3/§3.5 (the `kot-axiom/1` grammar +
sidecar-endorsement decision); `data/onto-obo/README.md` (the logicalDefinition
substrate, `AxiomsOnly` honesty, CL/UBERON `4im` block);
`data/onto-obo/minted-urns.jsonl` (the `id → urn:kot:` mint bridge);
`docs/next/architecture-ladder.md` §10 (N1-LB, the b-cov census that MEASURES the
delta, LB-GATE, reporting discipline); `data/d-ext/manifest.json` (≈49% lemma-touch
/ 0% checkable — the before-baseline [MEASURED]); `mapper/src/mapper.ts` (the
abstain-on-ambiguity discipline the mapper leg reuses).
