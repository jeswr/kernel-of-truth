# onto-obo — OBO Foundry logical-definition tier (AxiomsOnly)

**96,192 records** mechanically extracted from twelve OBO Foundry ontologies
(ten logical-definition shards + two **reference-stub** shards, Extraction 6),
one JSONL line per class/relation, sharded by ontology. This is the
`AxiomsOnly` stratum of the bulk-kernel design (`docs/design-bulk-kernel.md`) —
but a **tier richer than WordNet hypernymy**: where the source carries an OBO
`intersection_of` genus-differentia, we extract the **logical definition** as a
structured axiom inside record identity, not just a taxonomy link.

| shard | ontology | records | logical defs | genus-differentia | source data-version | licence |
|---|---|---|---|---|---|---|
| `bfo.jsonl` | Basic Formal Ontology | 35 | 0 | 0 | 2019-08-26 | CC BY 4.0 |
| `ro.jsonl` | Relation Ontology | 693 | 0 | 0 | releases/2025-12-17 | CC0 1.0 |
| `go.jsonl` | Gene Ontology | 38,256 | 9,307 | **9,303** | releases/2026-06-15 | CC BY 4.0 |
| `pato.jsonl` | Phenotype And Trait Ontology | 1,883 | 0 | 0 | releases/2025-05-14 | CC BY 3.0 |
| `po.jsonl` | Plant Ontology | 1,670 | 81 | 81 | releases/2026-01-09 | CC BY 4.0 |
| `cl.jsonl` | Cell Ontology | 3,359 | 1,731 | **1,723** | releases/2026-06-08 | CC BY 4.0 |
| `uberon.jsonl` | Uber-anatomy Ontology | 15,153 | 5,670 | **5,670** | releases/2026-06-19 | CC BY 3.0 |
| `ogms.jsonl` | Ontology for General Medical Science | 117 | 0 | 0 | 2021-08-19 | CC BY 4.0 |
| `so.jsonl` | Sequence Ontology | 2,447 | 219 | **219** | 2024-11-18 | CC BY 4.0 |
| `mondo.jsonl` | Mondo Disease Ontology | 32,136 | 7,685 | **7,582** | releases/2026-07-06 | CC BY 4.0 |
| `chebi.jsonl` | ChEBI *(reference-stub tier)* | 41 | 0 | 0 | 253 | CC BY 4.0 |
| `ncbitaxon.jsonl` | NCBI Taxonomy *(reference-stub tier)* | 402 | 0 | 0 | 2026-05-13 | CC0 1.0 |
| **total** | | **96,192** | **24,693** | **24,578** | | |

The two **reference-stub** shards (Extraction 6) are NOT the logical-definition
tier: they carry the label(+prose def) of the exact foreign terms referenced as
genus-differentia *fillers* by MONDO/CL/UBERON, minted as label-only anchors so
those definitions resolve under the `define`-op. See **Extraction 6** below.

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
- **CL — CC BY 4.0.** Derived records may be redistributed with attribution to
  the Cell Ontology (`http://purl.obolibrary.org/obo/cl`). License asserted in
  the source header (`property_value: terms:license …/by/4.0/`).
- **UBERON — CC BY 3.0.** Derived records may be redistributed with attribution
  to UBERON (`http://purl.obolibrary.org/obo/uberon`). License asserted in the
  source header (`property_value: dcterms-license …/by/3.0/`).
- **OGMS — CC BY 4.0.** Derived records may be redistributed with attribution to
  the Ontology for General Medical Science (`http://purl.obolibrary.org/obo/ogms`).
  License asserted in the source header (`property_value: dcterms:license …/by/4.0/`).
- **SO — CC BY 4.0.** Derived records may be redistributed with attribution to
  the Sequence Ontology (`http://purl.obolibrary.org/obo/so`). SPDX from the OBO
  Foundry registry (no in-header licence line).
- **MONDO — CC BY 4.0.** Derived records may be redistributed with attribution to
  the Mondo Disease Ontology (`http://purl.obolibrary.org/obo/mondo`). SPDX from
  the OBO Foundry registry.
- **ChEBI — CC BY 4.0.** Derived records may be redistributed with attribution to
  ChEBI (`http://purl.obolibrary.org/obo/chebi`). License asserted in the source
  header (`property_value: terms:license …/by/4.0/`) and the OBO Foundry registry.
- **NCBITaxon — CC0 1.0.** Public-domain dedication; no restrictions on derived
  records. License asserted in the source header (`property_value: terms:license
  …/publicdomain/zero/1.0/`) and the OBO Foundry registry.

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

**Single canonical record per IRI (`PREFIX_OWNER` dedup).** OBO ontologies
re-declare imported terms as stubs (e.g. `BFO:0000002` continuant appears inside
`ro.obo`/`go.obo`; CL declares 5,062 UBERON stubs and UBERON declares 1,487 CL
stubs — a *mutual* import that no array order can dedup correctly). The extractor
assigns each IRI one canonical owner by **prefix-ownership**: the ontology whose
id-space names the CURIE prefix owns it if it declares it (CL owns `CL:*`, UBERON
owns `UBERON:*`, BFO owns `BFO:*` classes), else the first declarer in fixed
order (so BFO *relations* declared only in RO, e.g. `BFO:0000050`, stay owned by
RO). This makes the CL↔UBERON dedup symmetric and order-independent: each owns
its own id-space, the other's stub is dropped. (PATO/PO are intentionally left to
the first-declarer fallback so their frozen shards are unchanged.)

**Foreign-prefix stub policy.** An `[Term]`/`[Typedef]` whose CURIE prefix is
**not** one of the extracted ontologies — an import stub of an entity we do not
extract (`NCBITaxon`, `PR`, `CHEBI`, `HP`, `CLM`, `DHBA`, `MBA`, `COB`, `ENVO`,
`OBI`, … and raw `http:` IRIs) — carries no definitional content here, only a
label. It is **not emitted as a record**; it survives only as a *reference
target* (a stable placeholder `urn:onto-obo:<local>` inside owned records'
axioms/differentiae), exactly like the pre-existing external refs. This is what
keeps CL+UBERON from injecting ~3,852 identity-less foreign stub records; it also
retro-drops 15 such stubs that RO previously emitted (COB/ENVO/OBI/CHEBI/IAO/
OGMS/UPHENO), the only change to a pre-existing shard (RO 721 → 693: −15 foreign
stubs, −13 CL/UBERON stubs now owned by CL/UBERON). BFO/GO/PATO/PO shards are
byte-identical.

**Excluded:** obsolete terms (`is_obsolete: true`) — 10,084 in GO, 17 in RO,
919 in PATO, 134 in PO, 213 in CL, 1,097 in UBERON — carry no definitional
axioms and are counted, not emitted. BFO's core relations
are OWL-only in the 2020 release; they are captured here via RO's BFO-relation
Typedefs (the `bfo-2020.owl` sha is pinned in `manifest.json` for provenance
completeness but is not parsed — we do not hand-roll an RDF/XML parser).

## Source pins

PURLs and per-file sha256 in `manifest.json → sourceFiles`. Sources are **not**
committed (`source/` gitignored); re-download to regenerate (see below).

## Files

| file | what |
|---|---|
| `bfo/ro/go/pato/po/cl/uberon/ogms/so/mondo.jsonl` | the logical-definition records (one shard per ontology) |
| `chebi.jsonl`, `ncbitaxon.jsonl` | reference-stub tier (Extraction 6): label(+def)-only stubs for referenced foreign fillers |
| `foreign-filler-subset.json` | the mechanically-derived reference-stub ingestion subset + the full unresolved-filler diagnosis ledger (`collect-foreign-fillers.mjs`) |
| `minted-urns.jsonl` | `urn:kot:` identity URNs (stable-mode mint; see below) |
| `archive-mint-20260709-substitute-5ont/` | the superseded 5-ontology substitute-mode mint (42,565 URNs), preserved for provenance |
| `manifest.json` | per-ontology source pins, licences, counts, axiom/differentia histograms, extractor hash |
| `alignment-kernel-v0.json` | hand-reviewed bridge candidates: kernel-v0 + molecules-v0 → BFO/RO categories (confidence per link; annotation-layer only, not identity) |
| `extractor/` | `parse-obo.mjs` (OBO 1.4 parser), `extract.mjs`, `stream-obo.mjs` (chunk-ingest), `sample-review.mjs` (whole-file audit), `stub-review.mjs` (streaming reference-stub audit), `collect-foreign-fillers.mjs` (subset generator), `parse-obo.test.mjs`, `chunk-ingest.test.mjs` (Node ≥ 20, zero deps) |
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

## Extraction 3 — CL + UBERON added; mint switched to stable mode (2026-07-09)

CL (3,359 records, 1,723 genus-differentia) and UBERON (15,153 records, 5,670
genus-differentia) were added by (1) generalising `PREFIX_OWNER` to
prefix-ownership (`CL→CL`, `UBERON→UBERON`) so the CL↔UBERON mutual import dedups
symmetrically, and (2) a foreign-prefix-stub emission policy (see "Foreign-prefix
stub policy" above). These are extractor-logic changes; the parser is untouched.

Adding anatomy forced a **mint reference-mode change: `substitute → stable`**
(bead kernel-of-truth-4im, Fable). Once UBERON/CL are in, the axiom reference
graph is **not a DAG** — 662 non-trivial SCCs, the largest **1,142** UBERON/CL
terms, held together by symmetric `disjoint_from` + lateral `relationship`/
`part_of`/`develops_from` assertions that are *not* definitional. There is no
reverse-topological order, and the gist-s6 component cap (32) is far exceeded;
minting a 1,142-term component would spuriously entangle those identities. This
is exactly `lexical-wn31`'s situation, and the same resolution: **stable mode** —
refs kept as stable placeholder `urn:onto-obo:` ids, identity anchored on the
globally-unique `sourceId` (OBO id). This re-schemes all onto-obo URNs (a
generation bump, gist §8); the prior substitute-mode mint is preserved under
`archive-mint-20260709-substitute-5ont/`.

Mechanical checks on this run:

- **Deterministic re-extraction / re-mint:** shards + `minted-urns.jsonl`
  byte-identical across two runs. BFO/GO/PATO/PO shards byte-identical to
  extraction 2; RO 721 → 693 (−15 foreign stubs, −13 CL/UBERON stubs moved to
  their owners).
- **Structural validation** (`validate.mjs`): all gates pass. 61,049 unique ids;
  168,170 internal refs resolve; **1** dangling known-prefix ref (the same
  `RO:0002089 → BFO:0000060` upstream gap); 6,981 cross-ontology filler refs to
  ontologies we do not extract (PR, NCBITaxon, raw `https:` IRIs, CLM, FMA,
  CHEBI, …) — kept as stable placeholders, expected and allowed.
- **Sample audit** (`sample-review.mjs 400 0x0b0`, now covering all 7 shards):
  **0 errors** over 400 records (GO 257, UBERON 97, CL 21, PATO 9, PO 9, RO 6,
  BFO 1) re-derived from source by an independent stanza-block re-parse.
- **Parser unit tests:** 11/11 pass.
- **Mint** (`tools/mint`, `--corpus onto-obo`, stable mode): **61,049 minted,
  61,049 unique URNs, 0 duplicate-identity groups**, 801 unresolved (foreign) ref
  targets kept as placeholders. `corpusIdentityRoot 42bc0781…`.

## Extraction 4 — Wave-A OBO adds: OGMS + SO + MONDO (2026-07-09)

Coverage-growth plan Wave A (`docs/next/coverage-growth-ingestion-plan.md`, bead
`kernel-of-truth-dzi`): three clean CC BY 4.0 OBO sources appended to
`ONTOLOGIES[]` and `PREFIX_OWNER` (each owns its own id-space), same generic
OBO-1.4 extractor, **no parser-logic and no ownership-logic change**. Records-only
coverage (linter Axis-A); **ZERO κ_B by itself** — genus-differentia
checkability is unlocked separately by the `define`-op, not by this ingestion.

- **OGMS** (117 records, 0 logical defs) — upper clinical scaffold on BFO. CC BY 4.0
  (source header + registry).
- **SO** (2,447 records, 219 genus-differentia) — sequence types/features. CC BY 4.0
  (registry SPDX; no in-header licence line).
- **MONDO** (32,136 records, 7,582 genus-differentia) — disease backbone. CC BY 4.0
  (registry SPDX). Its HP/CHEBI/NCBITaxon/DOID/OMIM/Orphanet/etc. cross-refs stay as
  foreign-prefix placeholders (not emitted), including HP (held, see below).

Total **61,049 → 95,749 records** (+34,700). The seven pre-existing shards
(`bfo/ro/go/pato/po/cl/uberon.jsonl`) are **byte-identical** to extraction 3
(verified by sha256): the new prefixes (OGMS/SO/MONDO) were foreign before and no
existing ontology declares them, so no ownership moved. MONDO owns **5 BFO-2020
relation Typedefs** (`BFO:0000056/0000117/0000132/0000163/0000167`) that our pinned
class-only `bfo.obo` does not declare — the same documented first-declarer fallback
that already lets RO own `BFO:0000050` etc. (no `bfo.jsonl` overlap; 0 duplicates).

Mechanical checks on this run:

- **Deterministic re-extraction / re-mint:** all 10 shards + `minted-urns.jsonl` +
  `manifest.json` **byte-identical across two full extract→mint cycles**.
- **Structural validation** (`validate.mjs`): all gates pass. **95,749 unique ids,
  0 duplicate ids**; 235,377 internal refs resolve; backbone (`is_a`/genus) closure
  complete; 839 dangling-known-prefix non-backbone refs (obsolete/upstream-gap
  targets, counted not fatal — same class as the RO:0002089→BFO:0000060 gap);
  24,632 external cross-ontology filler refs (http/NCBITaxon/https/PR/HP/CHEBI/… )
  kept as stable placeholders, expected and allowed.
- **Sample audit** (`sample-review.mjs`, two seeds, 1,600 records total): **0 errors**
  across all 10 shards (new-shard coverage OGMS 4, SO 38, MONDO 520; remainder
  GO/UBERON/CL/PATO/PO/RO).
- **Parser unit tests:** 11/11 pass (unchanged parser).
- **Mint** (`tools/mint`, stable mode): **95,749 minted, 95,749 unique URNs, 0
  duplicate-identity groups**, 0 cyclic components, 9,431 unresolved (foreign) ref
  targets kept as placeholders. `corpusIdentityRoot e8a95e2d…` (generation bump from
  the 61,049-record `42bc0781…`).

**Held within Wave A (queued for Fable/maintainer, NOT ingested):**

- **HPO (HP)** — **licence hold.** Registry licence is a custom `"hpo"` label
  (`https://hpo.jax.org/app/license`), not a standard SPDX. The (Re)usable Data
  Project rates it **2.5/10 "Custom (restrictive)"**: redistribution "not clearly
  permitted", derivatives/modification "not permitted", with the explicit clause
  that "neither the content of the HPO file(s) nor the logical relationships
  embedded within the HPO file(s) be altered in any way." Because the kernel
  re-represents logical relationships into `kot-obo/1`, redistribution is **not
  clearly permitted** → escalated rather than improvised.
- **PRO (PR)** — **source hold.** `http://purl.obolibrary.org/obo/pr.obo` and every
  standard product URL 404; PRO is a multi-product distribution (full = millions of
  protein forms; plan expects ~10Ks) requiring a product/subset choice (curation)
  and a non-standard download path.
- **ChEBI** — ~~scale/mechanism hold~~ **RESOLVED in Extraction 6.** Chunk-ingested
  as a targeted reference-stub tier (41 referenced fillers only), not a whole-file
  ingest. CC BY 4.0.
- **NCBITaxon** — ~~scale + curation hold~~ **RESOLVED in Extraction 6.**
  Chunk-ingested as a targeted reference-stub tier (402 referenced fillers only); the
  subset is mechanically derived (referenced-by-corpus), not curated. CC0 1.0.

## Extraction 5 — differentia relations resolved to minted relation URNs (2026-07-09)

Bead `kernel-of-truth-8es` (define-op §3.3 successor). Each OBO `intersection_of`
differentia previously stored its relation as a **bare `property` shorthand**
string (`part_of`, `disease_has_location`, `has_quality`, …) or a CURIE
(`RO:0002104`). The extractor now **resolves that token to the canonical minted
relation record's stable `urn:onto-obo:` id at extraction time**, and each
differentia carries an added `relation` field alongside the retained `property`:

```json
"differentiae": [
  { "property": "disease_has_location", "relation": "urn:onto-obo:RO_0004026",
    "filler": "urn:onto-obo:UBERON_0000002" } ]
```

This **retires the define-op's pinned §3.3 GO+PO-only shorthand alias table**:
SO/MONDO differentia relations are no longer bound to a 10-value table built from
GO+PO. Resolution uses ONLY the sources' own Typedef/relation declarations
(`buildRelationResolver` in `extract.mjs`): a CURIE token → its own emitted
relation record; a bare shorthand → the RO/BFO IRI declared by the shorthand's
Typedef `xref:` when exactly one such xref is itself an emitted relation record,
else the shorthand's own emitted relation record (locally-defined relations with
no RO mapping, e.g. `predisposes_towards`). Fail-closed: `ERR_OBO_REL_AMBIGUOUS`
(never guess) / `ERR_OBO_REL_UNRESOLVED`. Relation resolution runs ONLY for
records we emit — a dropped foreign import stub whose differentia names a foreign
relation (e.g. a CL stub's `STATO:0000101`) is never resolved. `property` is kept
for provenance and for the pre-8es alias-table read path (so the define-op census
never regresses while the engine still reads the table).

**`relation` is INSIDE identity** (it lives in `logicalDefinition`), so this is a
new extraction + **re-mint** (generation bump). Only the six differentia-bearing
shards change; the four with no genus-differentia are **byte-identical** to
extraction 4.

- **Versioning:** `EXTRACTOR_VERSION`/`EXTRACTION_DATE` left pinned (`0.1.0` /
  `2026-07-07`) per the established pattern (extractions 2–4 held them constant
  through extractor-logic changes; `manifest.extractor.contentHash` carries the
  real code signal: `a053806d…`). This keeps `bfo/ro/pato/ogms.jsonl`
  byte-identical (their `sha256` pins unchanged) — MEASURED: `bfo` `c8451264…`,
  `ro` `0366c37b…`, `pato` `2a42efba…`, `ogms` `a599d6da…` unchanged; only
  `go/po/cl/uberon/so/mondo` shards changed.

Mechanical checks on this run [MEASURED 2026-07-09]:

- **Deterministic re-extraction / re-mint:** all 10 shards byte-identical across
  two `extract` runs; `minted-urns.jsonl` + `manifest.json` byte-identical across
  three re-mints (identical `identityRoot`).
- **Structural validation** (`validate.mjs`, now also gating that every
  differentia `relation` resolves to an emitted relation record): all gates pass.
  95,749 records / 95,749 unique ids; reference closure 235,377 internal, 839
  dangling-known-prefix (unchanged from extraction 4), 24,632 external.
- **Sample audit** (`sample-review.mjs`, two seeds `0x0b0`/`0x4d31`, 1,600 records,
  now also checking each differentia `relation` is an emitted relation record):
  **0 errors**.
- **Parser unit tests:** 12/12 (was 11; +1 for the resolved-relation shape).
- **Mint** (`tools/mint`, stable mode): **95,749 minted, 95,749 unique URNs, 0
  duplicate-identity groups, 0 cyclic components**, 9,431 unresolved (foreign) ref
  targets. `corpusIdentityRoot 1adab65e…` (generation bump from extraction 4's
  `e8a95e2d…`). No downstream artifact pins onto-obo genus-differentia `urn:kot:`
  URNs (verified repo-wide), so the URN churn is contained.

**Resolution audit** [MEASURED, independent of `extract.mjs`]: over all 161
distinct differentia relation tokens the resolver is 0-ambiguous / 0-unresolved,
and the 10 GO+PO shorthands resolve to EXACTLY the retired alias table's targets
(`part_of → BFO_0000050`, `regulates → RO_0002211`, …), so GO/PO define answers
are unchanged. Weighted by occurrence: 79 tokens resolve via `xref` (23,397
differentiae), 37 CURIE-self (3,454), 45 shorthand-self (670).

**What this unlocks** (a STANDALONE check reading the resolved `relation` via the
mint bridge — NOT the define-op census, which is Opus's to re-run and is gated on
the engine reading `relation` instead of the alias table, bead `-46f`):
resolvable genus-differentia definitions go **GO 9,307→9,307 (unchanged), SO
18→219 (fully unlocked), MONDO 103→3,744**; `fail_on_relation = 0` for SO and
MONDO (the relation-shorthand gap is fully closed). MONDO's residual 3,941
unresolved fail ONLY on foreign **fillers** (`http`/`NCBITaxon`/`HP`/`CHEBI`/… —
the separate Wave-A foreign-ontology ingestion gap, out of 8es scope), 0 on
relation or genus. The OLD-column figures (9,307 / 18 / 103) match the define-op
census RUN-LOG exactly, validating the method.

## Extraction 6 — targeted foreign-filler reference-stub tier: CHEBI + NCBITaxon (2026-07-10)

Bead: foreign-filler unlock (Fable). The `define`-op census [MEASURED
`poc/define-op-census/RUN-LOG.md`] showed **3,941 minted MONDO genus-differentia
definitions `ERR_DEFN_UNRESOLVED` on foreign FILLERS only** (0 on genus/relation):
the held cross-ontology ingestion gap. This extraction unlocks the subset of those
whose fillers come from **clean-licence, source-available OBO sources** — WITHOUT a
blind whole-ontology ingest and WITHOUT curation, by ingesting **only the exact
filler terms referenced** as a minimal **reference-stub tier**.

**Mechanism (extractor-logic change; parser untouched).** Two large sources are
added to `ONTOLOGIES[]` with `streamed:true` + `stubTier:true` + a
`subset:{policy:'id-list'}` whose ids are the mechanically-derived referenced
fillers (`data/onto-obo/foreign-filler-subset.json`, from
`collect-foreign-fillers.mjs`). Each is chunk-ingested (`stream-obo.mjs`, never
materialised) and emitted as a **label(+prose def)-only stub**
(`stanzaToStubRecord`): `axioms:[]`, no `logicalDefinition`, `kind:class`. Because
a stub carries **no is_a**, the subset need not be is_a-closed (no dangling
backbone — `validate.mjs` stays green), and the `define`-op resolves a filler
purely through the mint bridge, so a minted stub is exactly enough to unlock it.
`PREFIX_OWNER` gains `CHEBI`/`NCBITaxon`; a new `STUBTIER_PREFIXES` rule makes those
prefixes own their whole id-space so the pre-existing MONDO/CL/UBERON CHEBI/NCBITaxon
import stubs stay **dropped** (importedAlias) — the ten prior shards are byte-identical.

| source | licence | referenced fillers ingested | source size | data-version |
|---|---|---|---|---|
| **ChEBI** | CC BY 4.0 (source header + registry) | **41** (of 41 referenced; 0 obsolete/missing) | 271 MB | 253 |
| **NCBITaxon** | CC0 1.0 (source header + registry) | **402** (of 402 referenced; 0 obsolete/missing) | 662 MB | 2026-05-13 |

**MEASURED unlock (re-run `python3 poc/define-op-census/define_census.py`):**

| shard | population | checkable BEFORE | checkable AFTER | Δ |
|---|---|---|---|---|
| go.jsonl | 9,307 | 9,307 | 9,307 | 0 |
| so.jsonl | 219 | 219 | 219 | 0 |
| mondo.jsonl | 7,685 | 3,744 | **4,298** | **+554** |
| **TOTAL** | **17,211** | **13,270** | **13,824** | **+554** |

Checkable fraction **0.7710 → 0.8032** [MEASURED 2026-07-10]. The +554 equals
exactly NCBITaxon(515) + CHEBI(39), the per-concept single-blocking-prefix counts —
a MONDO definition unlocks only when ALL its foreign fillers resolve, so this is the
clean gain from these two prefixes (no double-counting).

**The full unresolved-filler ledger (why not the whole 3,941).** A per-concept
blocking analysis of the 3,941 (see `foreign-filler-subset.json →
diagnosisAllUnresolvedFillerPrefixes`); each MONDO definition unlocks only when its
ENTIRE foreign-filler set resolves:

| blocking prefix | distinct fillers | MONDO defs blocked (single-prefix) | disposition |
|---|---|---|---|
| `http:` (HGNC gene IRIs) | 2,034 | 2,450 | **out of OBO scope** — `http://identifiers.org/hgnc/*` is the HUGO gene registry, not an OBO; needs a bespoke non-OBO extractor (world/gene-layer track), NOT a filler ingest |
| HP | 91 | 442 (+62 in HP∩other sets) | **licence hold** — HPO custom restrictive licence forbids altering the logical relationships (Extraction 4); NOT ingestible even as a targeted subset |
| CHR | 173 | 318 | **held** — chromosome-band terms (`CHR:9606-chrXq28`) declared INLINE in mondo.obo (no clean standalone source; purl is a legacy OCLC redirect). Ownership-design decision (MONDO-sourced CHR tier), flagged not improvised |
| NCBITaxon | 402 | 515 | **INGESTED (this extraction)** |
| CHEBI | 41 | 39 | **INGESTED (this extraction)** |
| ECTO / NCIT / ENVO / MF / MAXO / NBO / HsapDv / MFOMD | 50 total | 114 total | **deferred tail** — small clean-licence OBOs (CC BY / CC0), cheap follow-ups; low marginal unlock each, enumerated for the coordinator |
| PR | 208 | 0 (in census shards) | not in go/so/mondo — PR fillers are in cl/uberon (non-census); source hold (404 / multi-product) stands |

So of the 3,941: **554 unlocked here**; ~2,511 are HGNC (separate track); ~504
involve HP (licence); 318 CHR (bundled/legacy); ~114 the small-OBO tail. The
task-premise number (~17,211) assumed the gap was mostly HP/CHEBI/NCBITaxon; the
MEASURED composition is dominated by HGNC genes + HP, which this bounded OBO-filler
ingest deliberately does not chase.

**Mechanical checks on this run [MEASURED 2026-07-10]:**

- **10 prior shards byte-identical** to Extraction 5 (sha256 vs git HEAD): bfo/ro/
  go/pato/po/cl/uberon/ogms/so/mondo all UNCHANGED. New shards: `chebi.jsonl` (41),
  `ncbitaxon.jsonl` (402).
- **Structural validation** (`validate.mjs`): all gates pass. **96,192 records,
  96,192 unique ids, 0 duplicate ids**; reference closure internal 238,539 (+3,162
  now resolve), **0 fatal backbone dangling**, 3,776 dangling-known-prefix
  (non-backbone, counted), 18,533 external.
- **Stub audit** (`stub-review.mjs`, streaming — sample-review can't string-load the
  662 MB source): **0 errors** over ALL 443 stubs (label + def-presence re-derived
  from source; empty-axioms / no-logicalDefinition invariants; 0 missing).
- **Sample audit** (`sample-review.mjs 400 0x0b0`, 10 whole-file shards): **0 errors**.
- **Parser + chunk-ingest tests**: parse-obo 12/12, chunk-ingest 7/7 (streaming ==
  whole-file equivalence preserved).
- **Deterministic re-mint** (`tools/mint`, stable mode, ×2): `minted-urns.jsonl` +
  `manifest.json` **byte-identical across two mints**. **96,192 minted, 96,192
  unique URNs, 0 duplicate-identity groups, 0 cyclic components**, 8,988 unresolved
  (foreign) ref targets (9,431 → 8,988: the 443 fillers now resolve).
  `corpusIdentityRoot 7ad7988f…` (generation bump from `1adab65e…`).
- Versioning: `EXTRACTOR_VERSION`/`EXTRACTION_DATE` left pinned (`0.1.0` /
  `2026-07-07`) per the established pattern; the real code signal is
  `manifest.extractor.contentHash`. The 10 prior shards' `sourceVersion` pins are
  unchanged, so their bytes are unchanged.

**Not the ChEBI/NCBITaxon domain tiers.** These shards are reference-target anchors,
NOT the ChEBI chemistry axioms or the NCBITaxon taxonomy backbone. Those richer,
is_a-closed tiers (the "shippable subset" of the `stream-obo.mjs` design note) remain
future work; this extraction deliberately stays minimal.

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
curl -sSLO http://purl.obolibrary.org/obo/cl.obo
curl -sSLO http://purl.obolibrary.org/obo/uberon.obo
curl -sSLO http://purl.obolibrary.org/obo/ogms.obo
curl -sSLO http://purl.obolibrary.org/obo/so.obo
curl -sSLO http://purl.obolibrary.org/obo/mondo.obo
curl -sSLO http://purl.obolibrary.org/obo/chebi.obo         # Extraction 6 (271 MB)
curl -sSLO http://purl.obolibrary.org/obo/ncbitaxon.obo     # Extraction 6 (662 MB)
cd ../../..
# regenerate the reference-stub subset from the committed shards (before extract, so the
# stubTier ONTOLOGIES read the current referenced-filler set):
node          data/onto-obo/extractor/collect-foreign-fillers.mjs
nice -n 10 node data/onto-obo/extractor/extract.mjs      # fails closed on sha mismatch
node          data/onto-obo/validate.mjs
nice -n 10 node data/onto-obo/extractor/sample-review.mjs 400 0x0b0   # 10 whole-file shards
nice -n 10 node data/onto-obo/extractor/stub-review.mjs              # chebi/ncbitaxon stubs
node --test    data/onto-obo/extractor/parse-obo.test.mjs
node --test    data/onto-obo/extractor/chunk-ingest.test.mjs
# re-mint (stable mode): writes minted-urns.jsonl + manifest minting block
nice -n 10 node tools/mint/dist/src/cli.js --data ./data --out /tmp/onto-canon --corpus onto-obo
# MEASURE define-op unlock:
python3 poc/define-op-census/define_census.py
```

Sources drift (RO/GO release monthly). A new download with a different sha will
fail closed at `ERR_SOURCE_HASH`; bump the pin in `extract.mjs` deliberately and
re-run all gates — a re-ingestion is a new snapshot (gist §8).
