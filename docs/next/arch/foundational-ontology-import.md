# Foundational-ontology import as the type/axiom source — design doc

**Status: PROVISIONAL design doc** (designer-1, 2026-07-11). Written for maintainer
issue #20. It answers two maintainer questions — (1) how kernel-v0's Π-readout rules
were derived and why they over-constrain, and (2) whether we can auto-generate the
type/inference layer from a foundational ontology such as UFO — and states a
recommendation with decision points. **No feasibility conclusion on either value
thesis is stated or implied anywhere in this document; verdicts belong to the
maintainer and the review gate.** All epistemic tags are provisional. New assumptions
are emitted as a JSON array in the disjoint block `PROPOSED-ASM-1210..1229` (Appendix)
for central registration by the coordinator; this document writes nothing to
`registry/assumptions.jsonl`. Cross-references to `PROPOSED-ASM-112x/116x` are to the
RULES-1 world-model doc's own pending block (`docs/next/arch/world-model-rules-engine.md`).

---

## 1. How kernel-v0's Π-rules were derived, and why they over-constrain (maintainer Q1)

### 1.1 Where the typed claims come from — template-read, not reasoned

PREMISE: The Π-readout rules R1 (subClassOf), R3 (domain/range), R4 (existential) are a deterministic **syntactic projection** of two hand-authored fields in each concept's NSM explication — nothing is inferred or per-axiom authored [MEASURED: poc/g2/pi-project.py sha256 dd166410…; docs/design-dl-from-nsm-and-lean-reconstruction.md §3.2 lines 350-369].

- **R3 (the dominant failure).** For every relational concept, Π copies the two
  hand-authored `refKind` tags on the two referents through a **fixed 4-way table**
  (`SomethingRef→Thing-sort`, `SomeoneRef→Person-sort`, `TimeRef→Time-sort`,
  `PlaceRef→Place-sort`) and emits a domain/range claim; the clause logic is not
  consulted [MEASURED: poc/g2/pi-project.py:69-70, R3 block :192-203]. The renderer then
  **universally quantifies** the tag as a necessity: "In every case of 'X believes Y' …
  Y is a thing (something — not a person, not a place, not a time)" [MEASURED:
  poc/g2/build-materials.py:40-45 sort strings, :124-128 render].
- **R1 (subClassOf).** Read off the top-level `BE-SPEC` classification clause; the
  target class is whatever prime/concept the author put in the attribute head [MEASURED:
  poc/g2/pi-project.py:173-190].
- **R4 (existential).** Read off every `bind`-introduced slot-filler in a veridical
  clause [MEASURED: poc/g2/pi-project.py:120-155, :205-218].

So the answer to "hand-authored, template-read, or inferred?" is **template-read off
hand-authored structure**: the axioms are a syntactic re-serialisation of the `refKind`
tags and the classification/bind clauses, through a fixed sort table, with a
universal-necessity reading bolted on at render time. The 5-sort `refKind` discipline
is a system-wide commitment, not a g2 artefact [MEASURED: encoder/src/lexicon.ts:284
`REF_KINDS`; docs/design-constraint-layer.md:89].

### 1.2 Why they over-constrain — a representation error, not per-concept sloppiness

PREMISE: A blind cross-family LLM-proxy judge pair endorsed only 33/84 = 0.39 of the Π-derived claims as sound against ordinary meaning, with the failure overwhelmingly in R3 (R1 7/8, R3 5/42, R4 21/34 by the primary judge; the both-judges-concordant bracket is lower still at 24/84) [MEASURED: poc/g2/result.json sha256 96a23be5…; docs/next/interpretations/g2.md §1]. Two compounding design decisions cause it:

1. **The 4 sorts are treated as mutually disjoint.** `Thing-sort` renders literally as
   "a thing (something — not a person, not a place, not a time)"; there is no union type
   [MEASURED: poc/g2/build-materials.py:41; docs/design-dl-from-nsm-and-lean-reconstruction.md:140].
   So any argument the author tagged `SomethingRef` is forced to *exclude* persons.
2. **The `refKind` captures the prototypical filler, but the readout makes it
   necessary** ("In *every* case … X *is* …").

LOAD-BEARING: The root cause is the *readout*, not the definitions — Π re-purposes a bookkeeping tag (the `refKind` on the explication's *own variables*) [MEASURED: docs/design-constraint-layer.md:89] as an *ontological necessary type*, forces it through a 4-sort mutually-disjoint lattice, then universally quantifies it; NSM's `SOMETHING` prime is deliberately broad and routinely ranges over people, so `SomethingRef → "not a person"` is a category error introduced by the sort table plus rendering, not by the concept author [MEASURED: poc/g2/labels-proxy.jsonl per-rule counts].

Concrete misses: *believe Y → not a person* (you can believe a person); *break X → a
person* (a storm breaks a window); *find / lose / remember / take Y → not a person*
(you find a friend, lose your mother). This is the classic **selectional-restriction
error**: the field established decades ago that selectional restrictions are
*preferences*, not hard constraints [LIT-BACKED: Wilks 1975, preference semantics].

DECISION D-Q1: The over-constraint splits cleanly by rule and is mostly *intrinsic to
the current representation*, not fixable by better per-concept authoring — the R1 slice
(one bookmark misclassification) is a local authoring fix, but the R3 slice (37 of the
51 misses) needs a richer sort system (unions, agent types, subsumption) and a
defeasible reading, i.e. a change of approach, not of authoring; the R4 slice is the
pre-registered typicality-vs-necessity gap [STIPULATED: PROPOSED-ASM-1210].

This is exactly why the maintainer's UFO question lands: a researched foundational
ontology supplies the *layer-1* piece the home-grown 4-disjoint-sort readout lacks — a
proper sort lattice with role/phase/rigidity discipline. The genuine, defeasible
per-argument typing is a *layer-2* need that foundational ontologies do not themselves
supply (they carry almost no per-concept argument content, §2.1); it must come from
lexical/corpus resources (SUMO/WordNet, VerbNet/FrameNet). The choice is not "author
more carefully" but "replace the home-grown 4-sort typing with a researched layer-1
anchor plus corpus-grounded layer-2 soft typing."

---

## 2. Foundational-ontology and lexical-resource comparison (maintainer Q2)

### 2.1 The distinction that governs the whole answer

There are **two different things** the question conflates, and they live in different
resources:

- **Layer 1 — a type *system* / meta-schema** (kind vs role vs phase, object vs event
  vs quality, part-of, participation). This is what **UFO/BFO/DOLCE** provide. It is the
  *framework* our R1/R3/R4 rules should be *expressed in*, but it contains almost no
  domain content — it will never say "believe takes a proposition."
- **Layer 2 — per-concept content** ("believe → object is a Proposition", "person IsA
  Agent"). This lives in **SUMO+WordNet, VerbNet/FrameNet selectional restrictions,
  schema.org, ConceptNet, Wikidata** — not in the foundational ontologies.

Π currently does *both at once* (a UFO-style category scheme plus hand-authored
per-concept argument types), and the 0.39-sound failures are almost entirely in layer 2.
Foundational ontologies fix layer 1 cleanly; only SUMO/lexical resources touch layer 2.

### 2.2 Comparison table (license + coverage + fit)

Epistemic caption: the size, license, mapping, and estate-presence claims in this table
are empirical — [MEASURED] only for the local `data/*` paths and manifest license
verdicts cited; external size/license/mapping figures are [LIT-BACKED at
documentation strength] and must be re-verified at source before any load-bearing use.

| Resource | What it defines | Machine form + size | License — derive/redistribute? | Fixes over-constraint? | In estate? |
|---|---|---|---|---|---|
| **gUFO** (lightweight UFO) | Sortal/rigidity taxonomy: kind, subkind, role, phase, category, relator, mode, quality, event, situation; part-whole | OWL 2 DL, ~51 classes; reasoner-loadable | **CC BY 4.0** — cleanest | Best layer-1 fit (sortal/role/phase); no domain content to be wrong | kernel-v0 already *targets* `gufo:Event`, `gufo:Kind`; gUFO itself not yet ingested |
| **BFO 2020** (ISO/IEC 21838-2) | Continuant/occurrent; quality, role, disposition, process, temporal region; ~36 classes | OWL2 + CLIF | **CC BY 4.0** | Good, ISO-blessed; coarser on roles; relations deliberately very general | **Already ingested** `data/onto-obo/bfo.jsonl` (CC BY 4.0) |
| **DOLCE / DUL** | Endurant/perdurant/quality/abstract; participation; DnS | OWL (DUL ≈ 79 classes) | **Ambiguous** on classic files — redistribution risk | Rich on qualities; same coarseness at argument positions | No |
| **SUMO (+MILO)** | Full upper+mid; **relations carry domain/range argument axioms**; mapped to all of WordNet | SUO-KIF + TPTP; ~25k terms / ~80k axioms | IEEE "free"; extensions GPL — **estate verdict: REDISTRIBUTABLE with IEEE attribution** | Only resource touching layer 2 at scale; argument types broader than ours → reduces over-constraint | **Already ingested** `data/onto-sumo/` (Merge+MILO) |
| **WordNet / OEWN** | Noun+verb hypernym hierarchy; ~118k noun synsets | DB / RDF / LMF | Princeton free; **OEWN = CC BY 4.0** | Subsumption (R1) + type/instance; no verb argument typing | **Partial:** WordNet 3.1 structural extraction present as the separate lexical tier `data/lexical-wn31/` (AxiomsOnly stratum), but it is NOT an ontology-import input, and the **SUMO↔WordNet mapping asset is NOT loaded** (openly licensed; would need adding + pinning) |
| **VerbNet / FrameNet** | **Per-verb thematic roles + selectional restrictions (+animate/+human)** — the direct analog of what Π does | VerbNet XML; FrameNet frames | VerbNet permissive academic; **FrameNet = CC BY 3.0** | The tightest fix: corpus-grounded, *looser/better-calibrated* than our guesses | FrameNet **already ingested** `data/onto-framenet/` (CC BY 3.0) |
| **schema.org** | 823 types with `domainIncludes`/`rangeIncludes` (weak, non-logical) | RDFa/JSON-LD | **CC BY-SA 3.0** — copyleft (share-alike isolation) | Web-scale, coarse; intentionally non-constraining | No |
| **ConceptNet 5.5** | ~36 relations, commonsense IsA/typing | CSV/JSON + embeddings | **CC BY-SA 4.0** — copyleft | Broad but noisy; not logically typed | No |
| **Wikidata** | P31/P279 + subject/value-type constraints | RDF/SPARQL | **CC0** — most permissive | Huge subsumption + soft type constraints; uneven coverage | No |

LOAD-BEARING (the estate is further along than the question assumes): a foundational
ontology is **already in the kernel's world layer** — BFO+RO (`data/onto-obo`) is the
RULES-1 pre-registered second vertical, and kernel-v0's own records already carry gUFO
category URIs with hand-checked (non-endorsed, annotation-layer) bridge files
`data/onto-obo/alignment-kernel-v0.json` and `data/onto-sumo/alignment-kernel-v0.json`
[MEASURED: data/onto-obo/, data/onto-sumo/, data/kernel-v0/concepts/{event,kind}.json].
So this is not a greenfield "should we?" — it is "should we promote an already-present
anchor into the type/axiom source, and how."

---

## 3. Auto-generation feasibility read (maintainer Q2, continued)

### 3.1 What it SAVES

PREMISE: The typed backbone we currently hand-author and that g2 measured as unsound — subsumption (WordNet hypernymy), upper sortal typing (gUFO/BFO), predicate domain/range candidates (schema.org/VerbNet) — is a mature, decades-old research product (OntoWordNet "Sweetening WordNet with DOLCE"; gUFO; OntoLex-Lemon; VerbNet selectional restrictions), and the inference rules (subclass transitivity, domain/range typing, property chains) are standard OWL-RL/RDFS already implemented and conformance-tested in the sparq stack [LIT-BACKED: OntoWordNet, Gangemi et al.; gUFO nemo-ufes.github.io/gufo, 2019]; the engine reuse is [MEASURED: reports/sparq-estate.md §4]. Importing them replaces our home-grown scheme with a peer-reviewed one, **reducing the annotation burden** of authoring a type layer from scratch — but it does NOT eliminate the validation or alignment cost: sense alignment to our concept set, authored endorsement, licensing review, and a fresh g2-style soundness gate (PROPOSED-ASM-1217) all remain, so "saving the compute of validating typing" would overstate it. It could also loosen the "grow to 500+" type-layer blocker: a WordNet-aligned typed DAG *could* supply ~100k+ typed concepts — noting that while a WordNet 3.1 structural extraction exists as the lexical tier `data/lexical-wn31/`, the SUMO↔WordNet mapping needed for that alignment is not loaded (§5.2 further qualifies this against `kernel_checkable`).

### 3.2 What it CANNOT replace

LOAD-BEARING: Auto-generation swaps the *formal scaffolding*, not the value-carrying artifacts, and three things stay ours [MEASURED: registry/verdicts/f2b-transfer.json; DECONF-A1 verdict]:

- **The authored NSM explications.** Auto-verbalisation (NaturalOWL/SWAT) produces
  templated, mechanical English ("a begin is a perdurant that…"), which is below the
  hard scholarly definition bar and is exactly the artifact measured as *transferring
  value* (f2b-t +0.25) [MEASURED: registry/verdicts/f2b-transfer.json]. So imported
  axioms cannot become the definitions; they sit *beneath* them.
- **The NSM-grounding thesis.** gUFO/BFO/WordNet are built on foundational categories,
  not the ~65 NSM primes; NSM explication is documented as resisting automation. Import
  is *orthogonal* to grounding — it changes the scaffolding, not the grounding claim
  [LIT-BACKED: Natural Semantic Metalanguage, reductive-paraphrase has no strict formal rules].
- **The vector layer is already inert, which *helps* here.** DECONF-A1 measured the
  runtime vector machinery extensionally reproducible (C_dec = 1.0), so the formal
  layer's live value has moved to (i) authored prose that transfers and (ii)
  deterministic inference over axioms; auto-generation does not threaten (ii) — it
  *feeds* it [MEASURED: registry/verdicts (DECONF-A1)].

### 3.3 The risks

- **The over-constraint does not vanish automatically.** Foundational ontologies encode
  *hard* disjointness; compiling imported domain/range as `rdfs:domain`/`rdfs:range`
  reproduces the exact g2 failure. The fix exists on both sides: the resources ship a
  **soft form** (schema.org `domainIncludes`, VerbNet *preferences*), and RULES-1 supplies
  the *classification hook* for keeping soft typing out of hard entailment — the
  `regime ∈ {owl-rl, horn-def, policy}` tag. To be precise: `regime=policy` is an
  epistemic/provenance classification, not an implementation of soft typing — a genuine
  soft-typing consumer (defeasible preference representation, confidence ordering,
  exception handling, and a decision rule for how preferences rank or lint) still has to
  be built on top of it. Route imported domain/range to the **policy/soft regime, never
  owl-rl**, and treat the advisory consumer as new work, not existing machinery
  [STIPULATED: cross-ref PROPOSED-ASM-1162 (RULES-1)].
- **Honest trade-off on soundness.** Foundational domain/range constraints are *general*
  (Entity/Continuant), so they score high on "sound vs ordinary meaning" precisely
  because they barely constrain; they will not reproduce Π's *specific* typed claims. You
  buy soundness/recall at the cost of precision/informativeness. Only VerbNet selectional
  restrictions offer specificity *with* empirical grounding.
- **Alignment to our concept set is real work.** NSM primes/molecules are more
  abstract than WordNet senses; verb/perdurant alignment (the kernel's hardest cases:
  believe, begin) is the *least mature* part of the prior art and needs a
  sense-disambiguation step that is error-prone and not 1:1.
- **Licensing.** gUFO / BFO / OEWN clean (CC BY 4.0); Wikidata / RO clean (CC0); SUMO
  IEEE-permissive (estate verdict REDISTRIBUTABLE with attribution); FrameNet CC BY 3.0;
  schema.org / ConceptNet **CC BY-SA** (copyleft — must be isolated in their own shard or
  they force the derived layer to ShareAlike); DOLCE ambiguous (verify before use)
  [MEASURED: data/onto-sumo/manifest.json, data/onto-framenet/manifest.json,
  data/onto-obo/manifest.json license verdicts].
- **Thesis-dilution / control risk.** If the type layer is imported, the kernel's
  distinctiveness reduces to "authored NSM prose + a standard ontology," which makes the
  knull-style control (issue #6) and the c5 knull-sourced-rules ablation more
  load-bearing: an imported-ontology type layer is a strong, cheap baseline the kernel
  must beat to claim kernel-specific value [MEASURED: cross-ref RULES-1 D15,
  PROPOSED-ASM-1138].

DECISION D-FEAS: Auto-generation is **PARTLY VIABLE with a clean split** — it replaces
the formal type/subsumption/domain-range layer and the inference rules, and it does not
replace the authored explications or the grounding thesis; given DECONF-A1 and the
rules-engine pivot, the formal layer's role is now "axiom source for the engine," which
is precisely where auto-import is strongest [STIPULATED: PROPOSED-ASM-1213].

---

## 4. How it slots into RULES-1 and into "grow the kernel" (maintainer's two live threads)

### 4.1 Into the RULES-1 world-model + rules-engine (as the TBox/axiom source)

PREMISE: RULES-1's C1 compiler already compiles *endorsed* `kot-axiom/1` records into an OWL-RL TBox + Horn rules, and its engine already consumes OWL/RDFS; its pre-registered second vertical `data/onto-obo/` is BFO-aligned (a foundational ontology) with real RO property chains [MEASURED: docs/next/arch/world-model-rules-engine.md §C1, §MD-1 table, PROPOSED-ASM-1125]. So a foundational-ontology TBox can be consumed by the existing engine **only in its explicitly profile-checked executable subset**: gUFO is an OWL 2 DL artifact, so what "drops in" to the current RL/Horn engine is a validated RL-compatible projection of it, not the ontology wholesale — the profile check is an actual OWL 2 RL validation step, not relation-name inspection [LIT-BACKED: W3C OWL 2 Profiles]. Kernel domain axioms then specialise gUFO/BFO classes (`kot:X rdfs:subClassOf gufo:…`), inheriting the **OWL-visible axioms only** (e.g. asserted disjointness). UFO's rigidity/anti-rigidity metaproperties are modal and are NOT enforced by the RDF/OWL rendering (the companion expressivity analysis §2.6 records exactly this); they remain annotation/validation-level discipline unless a modal formalism is deliberately adopted under the expressivity-justification protocol. "Inherits validated rigidity" is therefore not available at this seam.

DECISION D-RULES: Adopt the foundational-ontology import as an **AUGMENTATION of the C1
axiom source**, not a replacement of the engine and not a replacement of authored
endorsement — imported axioms are curated/endorsed (the `axioms-definitional-v0`
precedent), imported domain/range is routed to the policy/soft regime (never
`rdfs:domain`/`rdfs:range`), and existential heads still refuse rather than mint
individuals. This is the pattern RULES-1 already intends for the OBO vertical; the change
is that the *foundational* tier becomes the explicit type anchor for the *kinship/family*
vertical too, not only the biomedical one [STIPULATED: PROPOSED-ASM-1214; cross-ref
PROPOSED-ASM-1162, PROPOSED-ASM-1126].

RULES-1 as designed **does not change its architecture** — same worlds, same arms, same
endpoints, same kill rules. What changes is one input: some TBox rows now carry a
`gufo:`/`bfo:` parent and a `regime=policy` tag on imported domain/range. The engine, the
proof-carrying readout, and the certificate are untouched.

### 4.2 Into "grow the kernel to 500+" (g2 option B)

PREMISE: The g2 instrument gate needs the Π dump to yield ≥500 judgeable items, but Π reads *authored explications*, and the coverage-growth plan's governing fact is that **checkability is not vocabulary coverage** — an item is `kernel_checkable` only when a record, a licensing axiom, AND a mapper parse into the closed 4-op grammar coincide; structured-DB import supplies the first two, never the third [MEASURED: docs/next/coverage-growth-ingestion-plan.md §0; registry/verdicts/m0b.json].

DECISION D-GROW: Foundational-ontology import **loosens the type-layer growth blocker
but does not by itself satisfy the g2 n≥500 Pi-soundness gate** — it supplies a large
typed backbone (legs 1-2) that makes a sounder type layer available, but the Pi-soundness
count still requires either authored explication growth or a maintainer re-size of the
gate to the attainable dump. Import is complementary to option B, not a substitute for
it [STIPULATED: PROPOSED-ASM-1215].

---

## 5. Recommendation and decision points for the maintainer

### 5.1 The governing constraint (why this is "anchor," not "destination")

LOAD-BEARING: The programme directive is explicit that **RDF/OWL/SHACL/DL are NOT design targets, NOT validation references, and NOT a destination** — at most an optional, lossy *export* projection; meaning lives in the native kernel formalism, and the litmus axiom ("a human has exactly two parents, one male, one female") is expressible in the NSM-pinned form but in no tractable OWL profile [MEASURED: docs/kernel-design-directives.md §1]. This bounds the recommendation: we adopt a
foundational ontology as a **type/axiom anchor and soft-typing + comparator source**,
*not* as the authoritative meaning layer. The kernel's identity, vectorisation, and axiom
formalism stay native; the import is a curated, endorsed, downstream-anchored input to
the rules engine.

### 5.2 Recommendation

DECISION D-REC (primary): **Adopt gUFO (CC BY 4.0) for the layer-1 type/meta-scaffold —
which kernel-v0 already targets, noting gUFO itself is NOT yet loaded and needs a pinned
ingestion — and source the layer-2 per-concept content from SUMO (ingested) plus
VerbNet/FrameNet selectional restrictions (FrameNet frame metadata ingested; VerbNet not
loaded), routed to the RULES-1 policy/soft regime.** Precision on estate state: the
component corpora SUMO (`data/onto-sumo/`) and FrameNet (`data/onto-framenet/`) are
loaded, and a WordNet 3.1 structural extraction exists as the separate lexical tier
(`data/lexical-wn31/`); but the **SUMO↔WordNet mapping asset is not loaded**, the
ingested FrameNet tier is frame metadata/relations (not a demonstrated VerbNet-style
selectional-restriction layer), and the cross-resource alignment plus the executable
soft-typing extraction remain unbuilt — all openly licensed, all needing deliberate
adding/pinning, not reuse. BFO (already ingested, CC BY 4.0, ISO-standard) is the
drop-in alternative for layer 1 if ISO interoperability is valued over gUFO's richer
role/phase distinctions; since BFO is already in the estate and gUFO's categories are
BFO-aligned, the cheapest path is **BFO-now, gUFO-when-ingested**, treating them as the
same anchor family [STIPULATED: PROPOSED-ASM-1211].

DECISION D-REC (content + fix): **Source per-concept argument typing from SUMO+WordNet
(coverage) and VerbNet/FrameNet selectional restrictions (the over-constraint fix, being
corpus-grounded and defeasible), compiled into the policy/soft regime, never
`rdfs:domain`/`rdfs:range`** [STIPULATED: PROPOSED-ASM-1212].

DECISION D-REC (mode): **Hybrid, not blind auto-import.** Import supplies *candidate*
type anchors and soft argument-typing; C1's authored-endorsement discipline stays — a
human/agent endorses each imported axiom with a cited warrant. Auto-import for recall,
endorsement for authority [STIPULATED: PROPOSED-ASM-1214].

DECISION D-REC (RULES-1 impact): **RULES-1's architecture does not change.** Only the C1
axiom source gains an imported upper module and a `regime=policy` route for imported
domain/range. No new engine, no new endpoints, no new kill rules [STIPULATED:
PROPOSED-ASM-1214].

DECISION D-REC (falsifiable gate): Before adopting the import for the *type* layer,
**re-run the g2-style soundness proxy on the imported + soft-regime typing and confirm
the over-constraint drops** (imported/soft sound-rate materially above the 0.39 baseline);
this is the check that decides whether the import is worth carrying [STIPULATED:
PROPOSED-ASM-1217]. The expectation that it *will* drop is directional only and load-bearing
for nothing [EXTRAPOLATION: PROPOSED-ASM-1218 resolves via the 1217 re-run].

### 5.3 Decision points the maintainer must settle

1. **Anchor family:** gUFO (ingest new, richest for our role/phase needs) vs BFO
   (already ingested, ISO-standard, coarser). Recommendation: BFO-now / gUFO-later, one
   family. [PROPOSED-ASM-1211]
2. **Content source + license posture:** SUMO+FrameNet (ingested, redistributable) plus
   WordNet (structural extraction present as `data/lexical-wn31/`; the SUMO↔WordNet
   mapping NOT loaded, openly licensed, would need adding) as the layer-2 source. Do we
   also pull VerbNet (not loaded; verify license) and
   accept schema.org/ConceptNet *only* under share-alike shard isolation, or exclude the
   copyleft sources entirely? [PROPOSED-ASM-1212, PROPOSED-ASM-1216]
3. **Authority boundary:** confirm the import is anchor/soft-typing/comparator only, with
   authored NSM explications remaining the sole meaning layer (directive §1). Does the
   maintainer want the import to ever become an *authoritative* type source, or stay a
   downstream anchor? [PROPOSED-ASM-1211, directive §1]
4. **RULES-1 sequencing:** fold the foundational anchor into the *kinship* vertical of
   RULES-1 now, or keep it confined to the OBO second vertical as already planned?
   [PROPOSED-ASM-1214]
5. **Gate for adoption:** accept the g2-style re-run as the go/no-go for replacing the
   home-grown 4-sort typing? [PROPOSED-ASM-1217]

**NO feasibility conclusion on either value thesis is drawn here.** This document
recommends a *source of type/axioms*; whether the kernel-plus-engine delivers correctness
or efficiency remains RULES-1's and the maintainer's to measure, gated behind the c5
knull-sourced-rules control that this import makes more load-bearing (§3.3).

---

## Self-check gate

- No feasibility conclusion on either thesis is stated or implied; all tags provisional.
- Every premise / decision / load-bearing marker line carries an epistemic tag with a
  backing ref on its single (unwrapped) physical line; no marker line rests on an
  EXTRAPOLATION; the one EXTRAPOLATION (over-constraint drop) is non-load-bearing prose
  pointing to the PROPOSED-ASM-1217 re-run as its resolver.
- New assumptions confined to the disjoint block `PROPOSED-ASM-1210..1218` (Appendix);
  registry untouched; the coordinator registers.
- Cross-references to `PROPOSED-ASM-112x/116x/1138/1162` are to the RULES-1 doc's own
  pending block, in the estate's established pending-registration pattern.
- No account-handle strings anywhere; bare package/ontology names only.
- `claims-check` was run before returning; the only violations are the expected
  `ERR_ASM_UNKNOWN_ID` on the not-yet-registered `PROPOSED-ASM-*` ids (this block plus the
  RULES-1 cross-references) — matching the world-model-rules-engine.md precedent — with
  zero untagged-premise, zero extrapolation-premise, and zero missing-backing findings.

---

## Appendix — Proposed ASM rows (PROPOSED-ASM-1210..1218)

Emitted for central registration by the coordinator; this document does not write to
`registry/assumptions.jsonl`.

```json
[
  {"id":"PROPOSED-ASM-1210","tag":"STIPULATED","claim":"The g2 Pi over-constraint (33/84 = 0.39 sound; failure concentrated in R3, 5/42) is diagnosed as a REPRESENTATION error, not per-concept authoring error: Pi re-purposes the refKind bookkeeping tag on the explication's own variables as a hard, universally-quantified, mutually-disjoint NECESSARY argument type, forcing NSM's broad SOMETHING prime to exclude persons. The R1 slice (bookmark) is a local authoring fix; the R3 slice (37 of 51 misses) is intrinsic to the 4-disjoint-sort readout; the R4 slice is the pre-registered typicality-vs-necessity gap. This is the classic selectional-restriction-as-hard-constraint error.","backing_ref":"poc/g2/pi-project.py:69-70,192-203; poc/g2/build-materials.py:40-45,124-128; poc/g2/result.json sha256 96a23be5; docs/design-constraint-layer.md:89; Wilks 1975 preference semantics","rationale":"Names the root cause so the remedy is scoped as 'replace the home-grown 4-sort typing', not 'author more carefully'; distinguishes the fixable authoring slice from the intrinsic representation slice.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Selectional restrictions are preferences not constraints (Wilks 1975) is LIT-BACKED; the g2 rates are MEASURED; the diagnosis synthesising them is the stipulated call."},
  {"id":"PROPOSED-ASM-1211","tag":"STIPULATED","claim":"Adopt a foundational ontology as the layer-1 type/meta ANCHOR and soft-typing + comparator source, NOT as the kernel's authoritative meaning formalism (directive-1 no-semantic-web-legacy preserved: meaning stays native NSM; the import is a downstream-anchored, curated, endorsed input). Primary pick gUFO (CC BY 4.0, which kernel-v0 already targets via gufo:Event/gufo:Kind); BFO (already ingested data/onto-obo, CC BY 4.0, ISO/IEC 21838-2) is the drop-in alternative and the cheapest immediate anchor since it is present and gUFO is BFO-aligned -> BFO-now / gUFO-later, one anchor family.","backing_ref":"docs/kernel-design-directives.md#1; data/onto-obo/bfo.jsonl; data/kernel-v0/concepts/{event,kind}.json; data/onto-obo/alignment-kernel-v0.json; nemo-ufes.github.io/gufo (gUFO, 2019)","rationale":"Foundational ontologies supply the sort lattice / role-phase distinctions the 4-disjoint-sort readout lacks; anchoring (not adopting-as-meaning) is what keeps directive-1 satisfied; BFO's prior ingestion + kernel-v0's existing gUFO targeting make this the lowest-cost path.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Anchor/comparator posture, not destination; directive-1 bounds it."},
  {"id":"PROPOSED-ASM-1212","tag":"STIPULATED","claim":"Source layer-2 per-concept argument typing from SUMO (ingested, REDISTRIBUTABLE with IEEE attribution) plus WordNet for coverage (WordNet 3.1 structural extraction present as the lexical tier data/lexical-wn31/, but the SUMO<->WordNet mapping asset is NOT loaded and would need adding + pinning) and VerbNet/FrameNet selectional restrictions (the over-constraint fix, being corpus-grounded and defeasible; FrameNet frame METADATA ingested CC BY 3.0 — not a demonstrated selectional-restriction layer; VerbNet not loaded), compiled into the RULES-1 policy/soft regime and NEVER as rdfs:domain/rdfs:range. The alignment and executable soft-typing extraction remain unbuilt. Foundational ontologies alone cannot supply per-concept argument types (they are domain-empty by design).","backing_ref":"data/onto-sumo/manifest.json (license verdict); data/lexical-wn31/manifest.json (AxiomsOnly stratum); data/onto-framenet/manifest.json; VerbNet selectional restrictions; cross-ref PROPOSED-ASM-1162 (RULES-1 regime tag)","rationale":"The 0.39 failure is a layer-2 (argument-typing) problem; only SUMO/WordNet/VerbNet/FrameNet touch it, and only their SOFT forms avoid reproducing the hard-disjointness error.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Soft regime routing is the classification hook; the advisory consumer (preference ranking/lint) is new work per section 3.3. Cross-ref RULES-1 PROPOSED-ASM-1162."},
  {"id":"PROPOSED-ASM-1213","tag":"STIPULATED","claim":"Auto-generation from foundational + lexical resources is PARTLY VIABLE with a clean split: it replaces the formal type/subsumption/domain-range layer and the inference rules (standard OWL-RL/RDFS, already conformance-tested in sparq), and it does NOT replace (a) the authored NSM explications (mechanical auto-verbalisation is below the scholarly bar and is the f2b-t value-carrying artifact) nor (b) the NSM-grounding thesis (resources are not prime-built). Given DECONF-A1's inert vector runtime and the rules-engine pivot, the formal layer's role is now axiom-source-for-the-engine, which is exactly where auto-import is strongest.","backing_ref":"registry/verdicts/f2b-transfer.json; DECONF-A1 verdict (C_dec=1.0); reports/sparq-estate.md §4; OntoWordNet (Gangemi et al.); gUFO 2019","rationale":"Separates what import saves (annotation + compute on the unsound formal layer) from what stays ours (transferring prose + grounding), so the recommendation neither over- nor under-claims.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"No feasibility conclusion on the theses; this scopes the SOURCE only."},
  {"id":"PROPOSED-ASM-1214","tag":"STIPULATED","claim":"Slot-in to RULES-1 is AUGMENT-not-replace: the foundational-ontology TBox imports as an upper module in the C1 compiler (kernel domain axioms specialise gufo:/bfo: classes), imported domain/range routes to the policy/soft regime, existential heads still refuse entity minting, and every imported axiom is curated/endorsed on the axioms-definitional-v0 precedent (auto-import for recall, endorsement for authority). RULES-1's architecture, worlds, arms, endpoints, and kill rules are UNCHANGED; only one input (some TBox rows gain a gufo:/bfo: parent + regime=policy) changes.","backing_ref":"docs/next/arch/world-model-rules-engine.md §C1, MD-1 table, PROPOSED-ASM-1125/1126/1162","rationale":"The OBO/BFO second vertical already proves this pattern in-estate; making the foundational tier the explicit anchor for the kinship vertical too is an input change, not an architecture change, so it inherits RULES-1's validation unchanged.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Cross-refs RULES-1 pending block; no engine change."},
  {"id":"PROPOSED-ASM-1215","tag":"STIPULATED","claim":"Foundational-ontology import LOOSENS the 'grow to 500+' (g2 option B) type-layer blocker but does NOT by itself satisfy the g2 n>=500 Pi-soundness gate: import supplies a large typed backbone (legs 1-2 of kernel_checkable: record + licensing axiom) but never leg 3 (mapper parse into the closed 4-op grammar), and the Pi-soundness count reads AUTHORED explications, so >=500 judgeable Pi items still needs authored growth or a maintainer gate re-size. Import is complementary to option B, not a substitute.","backing_ref":"docs/next/coverage-growth-ingestion-plan.md §0; registry/verdicts/m0b.json; docs/next/interpretations/g2.md §2","rationale":"Prevents the false inference that importing 100k+ typed concepts auto-clears the g2 instrument gate; checkability is not vocabulary coverage.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"Ties the import to both live threads honestly."},
  {"id":"PROPOSED-ASM-1216","tag":"STIPULATED","claim":"License posture for any redistributed derived kernel: gUFO / BFO / OEWN clean (CC BY 4.0, attribution); RO / Wikidata clean (CC0); SUMO redistributable with IEEE attribution (estate verdict); FrameNet CC BY 3.0; schema.org / ConceptNet are CC BY-SA copyleft and MUST be isolated in their own share-alike shard or excluded; DOLCE license ambiguous on classic files (verify before use). Per-shard license isolation is estate policy and a redistribution precondition.","backing_ref":"data/onto-sumo/manifest.json; data/onto-framenet/manifest.json; data/onto-obo/manifest.json license verdicts","rationale":"A derived kernel's redistribution is only as clean as its dirtiest incorporated shard; copyleft contamination is a non-starter for a permissive kernel unless shard-isolated.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"The already-ingested shards carry REDISTRIBUTABLE verdicts; the copyleft/ambiguous ones need the isolation/verify decision."},
  {"id":"PROPOSED-ASM-1217","tag":"STIPULATED","claim":"Adoption of the import for the TYPE layer is gated on a falsifiable check: re-run the g2-style soundness proxy on the imported + soft-regime typing and require the sound-rate to rise materially above the 0.39 home-grown baseline; if it does not, the import is not worth carrying for typing and the home-grown scheme's demotion is not licensed by this route.","backing_ref":"poc/g2/result.json sha256 96a23be5; analysis/g2.py; docs/next/interpretations/g2.md","rationale":"Makes the whole recommendation empirically decidable rather than argued; reuses the exact instrument that measured the over-constraint so the comparison is like-for-like.","load_bearing":true,"status":"open","owner":"designer-1","date":"2026-07-11","notes":"The go/no-go gate for replacing the 4-sort typing."},
  {"id":"PROPOSED-ASM-1218","tag":"EXTRAPOLATION","claim":"Directional expectation only (never a premise): importing corpus-grounded SOFT selectional restrictions (schema.org domainIncludes, VerbNet preferences) in place of the hard 4-disjoint-sort universal readout will RAISE the g2-style sound-rate above 0.39, because the imported constraints are built as defeasible expectations rather than necessities and thus stop excluding the persons ordinary usage allows.","backing_ref":"resolved by the PROPOSED-ASM-1217 g2-style re-run on imported+soft-regime typing","rationale":"","load_bearing":false,"resolution_path":"the PROPOSED-ASM-1217 g2-style soundness re-run on imported + soft-regime typing converts this to MEASURED (rise confirmed) or refutes it (no rise).","status":"open","owner":"designer-1","date":"2026-07-11","notes":"Load-bearing for nothing; interpretive colour pending the 1217 re-run."}
]
```
