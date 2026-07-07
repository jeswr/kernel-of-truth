# onto-framenet — FrameNet 1.7 frame metadata (AxiomsOnly, valency scaffold)

**1,221 frames + 2,070 typed frame relations** mechanically extracted from
Berkeley FrameNet 1.7. Each frame carries its **frame elements** — the
situation-type's argument/valency structure — with core/peripheral typing; the
relations carry **12,393 frame-element-to-frame-element mappings**. This is the
`AxiomsOnly` stratum of the bulk-kernel design, and the bulk source that maps
most directly onto profile-1's valency thinking (analysis below).

| file | records | what |
|---|---|---|
| `frames.jsonl` | 1,221 | frame + `frameElements` (name, coreType, feId — the valency skeleton, INSIDE identity); `definition`, FE-definitions, `lexicalUnits` (lemma+POS names) as annotations |
| `frame-relations.jsonl` | 2,070 | typed frame→frame edges with FE-to-FE mappings |

Frame elements by coreType: **Core 3,501**, Peripheral 5,023, Extra-Thematic
2,781, Core-Unexpressed 123 (11,428 total). 13,631 lexical-unit names.
Relation types: Inheritance 781, Using 556, ReFraming_Mapping 217, Subframe 131,
Perspective_on 127, Precedes 89, See_also 86, Causative_of 60, Inchoative_of 19,
Metaphor 4.

## Licence verdict — REDISTRIBUTABLE (CC BY 3.0), and the licensing boundary

**FrameNet 1.7 is licensed "Creative Commons Attribution 3.0 Unported"** (CC BY
3.0), author Collin F. Baker. Authoritative source: **NLTK's official
`nltk_data` `index.xml`** records `license="Creative Commons Attribution 3.0
Unported License"` for the `framenet_v17` package, and **our downloaded zip's
sha256 matches NLTK's recorded checksum** (`22f6aad6…`). CC BY 3.0 permits
copying, redistribution and derivative works with attribution — so derived
records are redistributable. (Note: FrameNet **1.5** was distributed
non-commercial-only; **1.7** was relicensed to CC BY 3.0 — we deliberately used
1.7.)

**The licensing boundary, recorded honestly:** the official FrameNet site
(`framenet.icsi.berkeley.edu`) gates its download behind a registration/request
form — a direct fetch of `fndata-1.7.zip` returns only a JS-app placeholder.
That form is a **courtesy tracker, not a licence restriction**: CC BY 3.0
already permits redistribution, which is precisely why NLTK can and does host a
public copy. We therefore obtained the data from **NLTK's authorized CC-BY
redistribution** and **did not circumvent the registration form**. We extract
only the freely-licensed **frame metadata** (frames + frame elements + frame
relations — exactly the "frame index + frame-to-frame relations" scoped for
this ingestion) and **do not redistribute the annotated corpus** (`lu/`,
`fulltext/` sentence data).

Attribution (recorded in every record's provenance and the manifest): *Baker,
Fillmore & Lowe (1998); Berkeley FrameNet, https://framenet.icsi.berkeley.edu,
CC BY 3.0.*

## The honesty architecture

`semanticStatus: "AxiomsOnly"`. Inside vs outside record identity:

- **Inside identity:** `frame`, `frameId`, and `frameElements` (name +
  `coreType` + feId). The FE structure is the frame's *argument skeleton* —
  genuinely structural, the analogue of a relation's argument list. For
  relations: `relationType`, `sub`/`super` frame refs, `feMappings`.
- **Outside identity, under `annotations`:** `definition` (frame prose def),
  `frameElementDefinitions`, `lexicalUnits` (the lemma.POS evokers — lexical
  realizations, treated like WordNet lemmas). Prose and lemmas never enter
  identity.
- **`provenance`** mandatory: dataset, obtained-via (NLTK CC-BY copy), pinned
  zip sha256, licence, extractor.

## Why FrameNet matters here — the valency mapping (the analysis)

profile-1 explications encode a concept's meaning as an NSM paraphrase over a
small set of **referents** (the arguments a predicate requires — `SomeoneRef`,
`SomethingRef` — in the `RelationalSchema`/`InstanceSchema` frames) plus adjunct
clauses for time, place and manner. The open problem for any *event* or
*relational* concept is: **what are its arguments, and which are obligatory?**
That is a valency question, and it is the single most labour-intensive part of
authoring a relational explication.

**FrameNet has already done that analysis, at scale, for 1,221 situation
types.** The mapping is close to one-to-one:

| profile-1 / kot-ast | FrameNet | 
|---|---|
| the situation a concept describes (`RelationalSchema` / event) | a **frame** |
| a referent / obligatory argument (numbered slot filled by SomeoneRef/SomethingRef) | a **Core** frame element (3,501 of them) |
| a time/place/manner **adjunct clause** (kot-ast admits only SP/ref/NOW/temporal-anchor time adjuncts, place clauses, manner) | a **Peripheral / Extra-Thematic** frame element (7,804 of them) |
| "this concept is a special case of that one, and here is how the participants correspond" | an **Inheritance** relation with its **FE-to-FE mapping** (781 relations, part of 12,393 FE maps) |
| the give/take, buy/sell **converse pairs** kernel-v0 handles by argument reordering | a **Perspective_on** pair over a neutral frame (127 relations) |
| the **before/after** temporal clauses in event explications | a **Precedes** relation (89) |
| the **break→broken**, cause-a-state pattern (causative event yielding a resultant state) | **Causative_of** / **Inchoative_of** relation types (60 / 19) |
| a molecule's dependency on a simpler concept as background | a **Using** (presupposition) relation (556) |

So a FrameNet frame + its Core FEs is precisely an **argument-structure axiom**
for a relational concept — the referent slots, pre-labelled with roles, with the
core/peripheral split already drawn. What FrameNet does **not** supply is the
NSM *body*: the FE roles are frame-specific labels (`Donor`, `Cook`, `Ingestor`),
not reductive paraphrases over semantic primes, and a frame is not a definition.
FrameNet is therefore a **valency scaffold, not an explication** — but it is the
richest bulk source of the one thing relational explications most need, and each
frame is an **upgrade candidate** toward a profile-1 `RelationalSchema`
explication: keep the FE slots as referents, author the NSM body by hand
(follow-up filed). This is a distinct, complementary upgrade path from OBO
genus-differentia (which upgrades *nominal* concepts): FrameNet upgrades *event
and relational* concepts.

## Source pin

FrameNet 1.7 via NLTK `framenet_v17.zip`, zip sha256
`22f6aad6fb799ba4dbed0440714e1118442ad7d7345351de37428581284f471c` (matches
NLTK index). Sources are **not** committed (`source/` gitignored).

## Files

`extractor/` — `parse-fn.mjs` (FrameNet XML reader), `extract.mjs`,
`sample-review.mjs`, `parse-fn.test.mjs` (Node ≥ 20, zero deps).
`validate.mjs` — source-free structural + reference-closure + manifest check.
`alignment-kernel-v0.json` — bridges to kernel-v0/molecules-v0.

## Verification results (2026-07-07 extraction)

- **Deterministic re-extraction:** two runs byte-identical (shard sha256s).
- **Structural validation** (`validate.mjs`): all gates pass. 1,221 unique
  frameIds; every FE has a valid coreType; every frame-relation's sub/super
  frame resolves to a frame record — **0 dangling refs**; frame prose is under
  `annotations`, never in identity; manifest counts / coreType histogram /
  relation-type histogram all reconcile.
- **Random-sample audit** (`sample-review.mjs 200 200 0xf00d`): 200 frames
  re-derived from source by an INDEPENDENT regex path (distinct from the
  extractor) comparing the frame name and the full (FE name, coreType) set —
  **0 errors**; 200 relations re-derived by an independent scan of
  `frRelation.xml` for sub/super frame ids — **0 errors**. (During development a
  frame-element self-closing-tag regex hazard was found via an FE-count
  cross-check against raw `<FE>` tags and fixed; the residual 3-tag gap was
  traced to `frame.xsl`, the stylesheet, correctly excluded — recorded per the
  verification bar.)
- **Parser unit tests:** `node --test data/onto-framenet/extractor/parse-fn.test.mjs`
  (6 tests: entity decode, attribute parse, definition cleaning, frame parse
  incl. self-closing FE, fail-closed on malformed FE, relation nesting).

## Regenerate

```bash
cd data/onto-framenet/source
curl -sSLO https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/framenet_v17.zip
# extract ONLY the frame metadata (not the annotated corpus lu/, fulltext/):
unzip -q framenet_v17.zip 'framenet_v17/frame/*' 'framenet_v17/frameIndex.xml' \
      'framenet_v17/frRelation.xml' 'framenet_v17/semTypes.xml' -d fndata
cd ../../..
nice -n 10 node data/onto-framenet/extractor/extract.mjs
node          data/onto-framenet/validate.mjs
nice -n 10 node data/onto-framenet/extractor/sample-review.mjs 200 200 0xf00d
node --test    data/onto-framenet/extractor/parse-fn.test.mjs
```
