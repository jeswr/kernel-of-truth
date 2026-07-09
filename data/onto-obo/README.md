# onto-obo — OBO Foundry logical-definition tier (AxiomsOnly, from BFO / RO / GO)

**42,565 records** mechanically extracted from five OBO Foundry ontologies,
one JSONL line per class/relation, sharded by ontology. This is the
`AxiomsOnly` stratum of the bulk-kernel design (`docs/design-bulk-kernel.md`) —
but a **tier richer than WordNet hypernymy**: where the source carries an OBO
`intersection_of` genus-differentia, we extract the **logical definition** as a
structured axiom inside record identity, not just a taxonomy link.

| shard | ontology | records | logical defs | genus-differentia | source data-version | licence |
|---|---|---|---|---|---|---|
| `bfo.jsonl` | Basic Formal Ontology | 35 | 0 | 0 | 2019-08-26 | CC BY 4.0 |
| `ro.jsonl` | Relation Ontology | 721 | 0 | 0 | releases/2025-12-17 | CC0 1.0 |
| `go.jsonl` | Gene Ontology | 38,256 | 9,307 | **9,303** | releases/2026-06-15 | CC BY 4.0 |
| `pato.jsonl` | Phenotype And Trait Ontology | 1,883 | 0 | 0 | releases/2025-05-14 | CC BY 3.0 |
| `po.jsonl` | Plant Ontology | 1,670 | 81 | 81 | releases/2026-01-09 | CC BY 4.0 |
| **total** | | **42,565** | **9,388** | **9,384** | | |

**The headline:** 9,303 GO terms carry a machine-extractable genus-differentia
definition ("X = *genus* that *rel* *filler*", e.g. *regulation of DNA
recombination* = *biological regulation* that *regulates* *DNA recombination*).
These are genuine definitions, not glosses — and the only bulk source with that
property. Each is flagged `upgradeCandidate: true`: they are the **upgrade path
to profile-1 structured explications** (follow-up filed).

## Licence verdicts (recorded per source; all REDISTRIBUTABLE)

- **BFO — CC BY 4.0.** Derived records may be redistributed with attribution to
  the Basic Formal Ontology and its authors (`http://purl.obolibrary.org/obo/bfo`).
  (The "BSD license" in BFO's remark applies to *build code*, not the ontology.)
- **RO — CC0 1.0.** Public-domain dedication; no restrictions on derived records.
- **GO — CC BY 4.0.** Derived records may be redistributed with attribution to
  the Gene Ontology Consortium (`http://geneontology.org`).
- **PATO — CC BY 3.0.** Derived records may be redistributed with attribution to
  the Phenotype And Trait Ontology (`http://purl.obolibrary.org/obo/pato`).
- **PO — CC BY 4.0.** Derived records may be redistributed with attribution to
  the Plant Ontology / Planteome project (`http://purl.obolibrary.org/obo/po`).

Authoritative SPDX from the OBO Foundry registry
(`obofoundry.org/registry/ontologies.jsonld`), recorded in `manifest.json` and
in every record's `provenance.license`.

## The honesty architecture

Same as `data/lexical-wn31` (gist §3.1): every record carries
`semanticStatus: "AxiomsOnly"` — structural axioms only, NO semantic-adequacy
claim. What is **inside** vs **outside** record identity here:

- **Inside identity:** `schema`, `semanticStatus`, `ontology`, `kind`
  (`class`/`relation`), `oboId`, `axioms` (typed edges to other records), the
  `logicalDefinition` (genus + differentiae — this IS structural/formal, a
  mechanical definition), and relation `characteristics` (`is_transitive`, …).
- **Outside identity, under `annotations`:** `label` (rdfs:label), `definition`
  (the prose OBO `def:` text, or BFO's `IAO:0000600` *elucidation*),
  `definitionXrefs`, `synonyms`, `namespace`, `comment`, `xrefs`, `subsets`.
  **Textual definitions and labels NEVER enter identity** — the same
  Princeton-gloss boundary as WordNet: a prose def is a mutable annotation.
- **`provenance`** (mandatory): source, PURL, pinned `sourceVersion` sha256,
  licence, extractor name/version, pinned extraction date.

Why is the logical definition inside identity when the textual one is not? The
OBO `intersection_of` construct is a formal OWL `equivalentClass` conjunction —
mechanically derived, not authored prose. It is exactly the *formal-sector*
situation of the design (§honesty-architecture item 4): the source is already
definitional. But because these are OBO logical definitions and not profile-1
explications, the record stays `AxiomsOnly` and marks itself an upgrade
candidate rather than claiming explicated status.

## What is extracted

- **Classes** (`[Term]`): `is_a`, `relationship: <prop> <target>`,
  `disjoint_from`, `union_of`, and the `intersection_of` genus-differentia →
  `logicalDefinition`.
- **Relations** (`[Typedef]`, mostly RO): `is_a`, `inverse_of`, `domain`,
  `range`, `transitive_over`, `holds_over_chain`, `disjoint_from`, and boolean
  `characteristics`.
- GO's top differentia relations: `regulates` (2,915), `positively_regulates`
  (2,586), `negatively_regulates` (2,564), `part_of` (1,088), `occurs_in`
  (177). These relation slots are precisely profile-1 valency thinking made
  mechanical.

**Single canonical record per IRI.** OBO ontologies re-declare imported terms
(e.g. `BFO:0000002` continuant appears as a stub inside `ro.obo` and `go.obo`).
The extractor assigns each IRI one canonical owner — the ontology whose id-space
matches its CURIE prefix if it declares it, else the first declarer (so BFO
*relations* declared only in RO, e.g. `BFO:0000050`, are owned by RO). 20
RO import-aliases were deduped this way.

**Excluded:** obsolete terms (`is_obsolete: true`) — 10,084 in GO, 17 in RO —
carry no definitional axioms and are counted, not emitted. BFO's core relations
are OWL-only in the 2020 release; they are captured here via RO's BFO-relation
Typedefs (the `bfo-2020.owl` sha is pinned in `manifest.json` for provenance
completeness but is not parsed — we do not hand-roll an RDF/XML parser).

## Source pins

PURLs and per-file sha256 in `manifest.json → sourceFiles`. Sources are **not**
committed (`source/` gitignored); re-download to regenerate (see below).

## Files

| file | what |
|---|---|
| `bfo.jsonl` / `ro.jsonl` / `go.jsonl` | the records |
| `manifest.json` | per-ontology source pins, licences, counts, axiom/differentia histograms, extractor hash |
| `alignment-kernel-v0.json` | hand-reviewed bridge candidates: kernel-v0 + molecules-v0 → BFO/RO categories (confidence per link; annotation-layer only, not identity) |
| `extractor/` | `parse-obo.mjs` (OBO 1.4 parser), `extract.mjs`, `sample-review.mjs`, `parse-obo.test.mjs` (Node ≥ 20, zero deps) |
| `validate.mjs` | source-free structural + reference-closure + manifest re-check |

## Verification results (2026-07-07 extraction)

- **Deterministic re-extraction:** two runs byte-identical (shard sha256s).
- **Structural validation** (`validate.mjs`): all gates pass. 39,012 unique
  ids; reference closure — 94,226 internal refs resolve; **1** dangling
  known-prefix ref (`RO:0002089 holds_over_chain → BFO:0000060`, a relation not
  declared in the pinned sources — an honest upstream gap, not an extraction
  bug; not a taxonomy-backbone break so not fatal); 8 cross-ontology fillers to
  ontologies we did not extract (NCBITaxon, COB, foaf) — expected and allowed.
- **Random-sample audit** (`sample-review.mjs 150 0x4d31`): 150 records
  re-derived from the owning source by an independent stanza-block scan +
  hand-rolled re-parse — **0 errors (0.00%)**. The random draw is GO-dominated
  (149 GO, 1 RO) by corpus proportion; a supplementary **full** re-derivation of
  all 35 BFO + all 721 RO records was also **0 errors**.
- **Parser unit tests:** `node --test data/onto-obo/extractor/parse-obo.test.mjs`
  (11 tests: id normalisation, escaping, genus-differentia assembly, Typedef
  axioms, obsolete handling).

## Extraction 2 — PATO + PO added (2026-07-09)

PATO (1,883 records) and PO (1,670 records, 81 genus-differentia) were appended
to `ONTOLOGIES[]` (same generic OBO-1.4 extractor, no parser-logic change). BFO,
RO and GO shards are byte-identical to extraction 1 (their sha256 pins and record
sets are unchanged — the new ontologies add no BFO/RO/GO ownership overlap beyond
the 5 PATO ids that RO already imported and owns). Mechanical checks on this run:

- **Deterministic re-extraction:** two runs byte-identical (`pato.jsonl`,
  `po.jsonl`, `manifest.json` sha256s match).
- **Structural validation** (`validate.mjs`): all gates pass. 42,565 unique ids;
  reference closure — 100,057 internal refs resolve; **1** dangling known-prefix
  ref (the same `RO:0002089 → BFO:0000060` upstream gap); 10 cross-ontology
  fillers (NCBITaxon:6, foaf:2, COB:2).
- **Sample audit** (`sample-review.mjs 150 0x4d31`): 0 errors (GO-dominated draw).
- **Mint** (`tools/mint`, `--corpus onto-obo`): 42,565 minted, 42,565 unique URNs,
  0 duplicate-identity groups.

**CL and UBERON deferred (owner-dedup decision needed).** CL and UBERON parse
cleanly with the same extractor (0 throws), but they mutually re-declare each
other's terms as import stubs (CL declares 5,062 UBERON ids; UBERON declares
1,487 CL ids) and carry thousands of foreign-prefix `[Term]` stubs (PR, CHEBI,
NCBITaxon, DHBA, MBA, CLM, plus raw `http:` IRIs). With the pinned first-declarer
owner-dedup (`PREFIX_OWNER = {BFO, RO, GO}`), ingesting them as-is would mis-own
5,062 UBERON terms (their genus-differentia definitions replaced by empty stubs)
and emit 3,852 foreign-prefix stub records into onto-obo (incl. 731 CHEBI —
explicitly out of scope — and 492 `http:` IRIs). Correct handling needs a
`PREFIX_OWNER` ownership-logic update plus a foreign-prefix-stub emission policy —
a design/curation decision, filed back to the maintainer (bead
kernel-of-truth-4im). Both licences are permissive (CL CC BY 4.0, UBERON CC BY
3.0), so the block is dedup logic, not licensing.

## The bridge (alignment-kernel-v0.json)

kernel-v0 already targets gUFO (`gufo:Event`, `gufo:Kind`), which is
BFO-aligned. Obvious categorial bridges (annotation-layer, per-link confidence):
`kernel-v0:event → BFO:0000015 process / BFO:0000003 occurrent` (high — the
directive's named anchor); `part_of → BFO:0000050`, `has_part → BFO:0000051`
(high); `cause → RO:0002411 causally upstream of` (medium); material/living
molecules → `BFO:0000030 object`, body-part molecules → `BFO:0000024 fiat object
part`, activity-verb molecules → `BFO:0000015 process` (medium). These are
categorial correspondences ("this NSM concept falls under this BFO category"),
not sameConceptAs claims, and nothing enters the mapper.

## Regenerate

```bash
cd data/onto-obo/source
curl -sSLO http://purl.obolibrary.org/obo/bfo.obo
curl -sSLo bfo-2020.owl http://purl.obolibrary.org/obo/bfo/2020/bfo-core.owl
curl -sSLO http://purl.obolibrary.org/obo/ro.obo
curl -sSLO http://purl.obolibrary.org/obo/go.obo
curl -sSLO http://purl.obolibrary.org/obo/pato.obo
curl -sSLO http://purl.obolibrary.org/obo/po.obo
cd ../../..
nice -n 10 node data/onto-obo/extractor/extract.mjs      # fails closed on sha mismatch
node          data/onto-obo/validate.mjs
nice -n 10 node data/onto-obo/extractor/sample-review.mjs 150 0x4d31
node --test    data/onto-obo/extractor/parse-obo.test.mjs
```

Sources drift (RO/GO release monthly). A new download with a different sha will
fail closed at `ERR_SOURCE_HASH`; bump the pin in `extract.mjs` deliberately and
re-run all gates — a re-ingestion is a new snapshot (gist §8).
