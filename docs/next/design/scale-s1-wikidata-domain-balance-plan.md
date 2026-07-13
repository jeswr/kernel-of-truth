# SCALE-1 S1 — Wikidata domain-balance acquisition + typing plan (SCOPE ONLY)

**Role:** Fable build agent (builder-scale-s1), 2026-07-13. Increment-2 companion
to `docs/next/design/scale-s1-multisource-census.md`. This is a **plan, not a
run** — it does NOT download a dump this tick (a 1-2 CPU-day operation). It scopes
the concrete acquisition + typing + decontamination path to a **domain-balanced**
100k rung. It touches no locked design doc, issues **no feasibility conclusion**
(CORRECTNESS and EFFICIENCY remain INCONCLUSIVE-PENDING, design §14), and writes
no registry.

Assumption candidates: `poc/scale/asm-2050-2059.json` (ASM-2059). Epistemic tags:
**[MEASURED]** committed bytes this tick; **[LIT-BACKED]** published grounding;
**[STIPULATED]** a build choice; **[EXTRAPOLATION]** a forward estimate with its
resolution path named, never a premise.

---

## 0. Why Wikidata, and the exact gap it fills

The increment-1/2 census [MEASURED, `poc/scale/results/scale-s1-census.json`]:
the local source-asserted-typed mass is **100% biological** (all of OBO; OBO =
45.8% of the 207,733-record union), and after the BFO bridge OBO is 99.99%
UFO-typed but still entirely biology. WordNet supplies broad common vocabulary but
**0% source-asserted** structure. So the union can reach 100k *by size* but fails
design §0's **domain-balanced** count (which must exclude single-domain
domination): a bio-heavy kernel covers open-domain benchmarks (MMLU, and thus the
KaE / F1-K n_min=240 coverage gate) only sparsely.

Wikidata is the design §3.1 CC0 source that closes this: it carries a broad,
cross-domain **class layer** (artifacts, occupations/roles, social entities,
activities/events, abstract objects, geographic/administrative types) with
source-linked P279 (subclass-of) structure, and — critically — **explicit external
IDs to exactly our existing sources**, which makes decontamination an exact join
rather than fuzzy matching.

## 1. Which slice (NOT the full 110M-item dump)

**Do not** ingest the full Wikidata (~110M items, most of them named
individuals). Ingest only the **class layer**:

- **Definition of a counted class** [STIPULATED]: an item that is the object of at
  least one `P279` (subclass of) statement, OR that has ≥1 `P279` outgoing edge,
  OR is used as the value of `P31` (instance of) by ≥ K items (a "type used as a
  type"). Named individuals — items that only ever appear as the *subject* of P31
  and never in the P279 hierarchy — are **excluded** and do NOT count toward the
  concept headline (design §0: named entities belong in the world ABox).
- **Acquisition mechanism, cheapest first:**
  1. **wdumper / targeted entity-dump** (preferred, ~GB not ~100GB): a
     server-side filtered dump specifying the class layer (P279 participants) with
     only the properties we need (labels, P279, P31, external-ID properties). This
     avoids parsing the full `latest-all.json.bz2` (~1.5 TB uncompressed).
  2. **WDQS paged SPARQL** for the class-root subtrees (§2) — fine for counting and
     for ≤ a few ×10⁵ items, subject to WDQS timeout paging.
  3. Full **`latest-truthy.nt.gz`** (~50-100 GB compressed) only if 1-2 prove
     insufficient — the 1-2 CPU-day path the coordinator flagged; kept as fallback.
- **Properties to retain:** `label/altLabel` (en), `P279` (subclass of), `P31`
  (instance of), and the external-ID properties in §3.

## 2. How many non-biological concepts it adds [EXTRAPOLATION — resolution path: WDQS count queries; load_bearing=false]

Planning bands (to be replaced by measured WDQS counts before any ingest commit):

- Wikidata's full class layer (P279 participants) is on the order of **~2-3M
  items** [EXTRAPOLATION].
- Excluding the biology already covered locally (organism `Q7239` subtree ≈ taxa;
  chemical compound `Q11173` ≈ ChEBI; disease `Q12136` ≈ MONDO; gene/protein) and
  excluding pure administrative/geographic individuals, the **non-biological
  reusable class** count is on the order of **~1M** [EXTRAPOLATION].
- For a **domain-balanced 100k rung**, the target is a benchmark-blind slice of
  **~50,000-100,000 non-biological classes** spread across UFO categories, e.g.
  subtrees of: physical object `Q223557` (→ object), occurrence/event `Q1190554`
  (→ event), profession/role `Q28640` and position `Q4164871` (→ role),
  organization/social group (→ social-object), artifact/product (→ object),
  activity `Q1914636` (→ event), quality/property (→ quality), and
  region/geographic-feature type (→ region). Exact Q-roots and per-root caps are a
  pre-registered §4-of-census-plan build choice.

**Net effect on domain balance:** adding ~50-100k non-biological classes drops the
biology share of a ~110k+ typed-structured core from ~100% to roughly **45-65%**
[EXTRAPOLATION], and — more importantly — makes the count survive design §0's
"exclude single-domain domination" test, which the current union fails.

## 3. P31/P279 → UFO typing crosswalk

Wikidata has no native BFO, but its top ontology crosswalks cleanly to the CK-UFO
`ontic_category`/`sortality` fields via a small pinned root→UFO table (the
Wikidata analogue of the BFO bridge in `data/onto-obo/bfo-bridge.json`):

| Wikidata mechanism | CK-UFO consequence | cascade step |
|---|---|---|
| `P279` (subclass of) | type-level `is_a` edge; feeds the closure | structural |
| `P31` (instance of) a *non-metaclass* | `denotation_level = individual` → EXCLUDED from concept count | 1 |
| `P279*` reaches physical object `Q223557` / concrete object | `ontic_category = object`, `sortality = kind` candidate | 1-2 (imported commitment via root crosswalk) |
| `P279*` reaches occurrence/event `Q1190554`, activity `Q1914636` | `ontic_category = event` | 1-2 |
| `P279*` reaches profession `Q28640` / position `Q4164871` / role class | `ontic_category = object`, `sortality = role`, `rigidity = anti-rigid` candidate | 1-2 |
| `P279*` reaches organization/social-group root | `ontic_category = social-object` | 1-2 |
| `P279*` reaches quality/attribute/property root | `ontic_category = quality` | 1-2 |
| `P1963` (properties for this type), constraint statements | argument/selectional candidates (soft, never hard domain/range) | 4 |

The root→UFO table is [STIPULATED, ontology-grounded] exactly like the OBO
`ONTOLOGY_ROOT_CATEGORY` fallback and the BFO bridge's 2 STIPULATED rows: the
choice of UFO category for each Wikidata root is a build decision, reported
separately from any BFO-reached source-assertion, and audited by the design §4.3
stratified human sample (Wikidata gets its own stratum). Wikidata's own P279 chain
IS source-asserted structure; only the terminal root→UFO label is stipulated.

## 4. Decontamination against the existing 207,733-record union — an EXACT join

Wikidata carries external-ID properties pointing at precisely our sources, so
cross-source duplicates are removed by an **exact identifier join**, not fuzzy
matching (this is the §3.5 "exactly crosswalked clusters" machinery, finally with
real crosswalk fuel):

| Wikidata property | resolves duplicate against | action |
|---|---|---|
| `P8814` (WordNet 3.1 Synset ID) | `data/lexical-wn31` | merge into the existing WN cluster; do not double-count |
| `P686` (ChEBI ID) | `data/onto-obo` CHEBI | merge |
| `P685` (NCBI taxonomy ID) | `data/onto-obo` NCBITaxon | merge (taxa) |
| `P5270` (MONDO ID) | `data/onto-obo` MONDO | merge |
| `P686`/`P594`/GO xrefs, `P1554` UBERON, `P7963` Cell Ontology ID | OBO shards | merge |
| `P2926` InterPro, `P352` UniProt (individuals) | — | EXCLUDE (named individuals) |

Procedure [STIPULATED]: (1) pull the class slice; (2) for each item, if any
external-ID property resolves to an existing union record, mark it a **crosswalk
merge** (adds provenance + possibly a UFO commitment to the existing record, does
NOT add a new concept); (3) items with NO resolving external ID and passing the
class-layer test are **new non-biological concepts**; (4) report the design §3.5
four counts (raw / exactly-crosswalked / type-level / fully-resolved) with the
Wikidata shard's CC0 license manifest. This finally lets the census emit a real
`exactly_crosswalked_clusters` number instead of the current "NOT COMPUTED".

## 5. Storage / compute estimate

| item | estimate | tag |
|---|---|---|
| class-slice acquisition (wdumper filtered dump) | ~1-5 GB download; ~2-8 CPU-h extract | [EXTRAPOLATION] |
| (fallback) full truthy dump | ~50-100 GB; 1-2 CPU-days | [EXTRAPOLATION] |
| stored class records (100k jsonl, kot-wikidata/1 schema like kot-obo/1) | ~50-150 MB | [DERIVED from OBO record sizes] |
| decontamination exact-ID join over 207,733 existing + ~100k Wikidata | minutes (hash join) | [EXTRAPOLATION] |
| re-run census.ts over the 4-source union | ~4 s (as now, +1 source) | [MEASURED analogue: current 3.6 s] |
| $ cloud-equivalent | ~$0-20 (bandwidth + CPU-h; no GPU) | [EXTRAPOLATION] |

Well inside the design §8 S1 band (200-2,000 CPU-h; $200-1,000). The dominant real
cost remains, per design §10, the crosswalk engineering and the §4.3 human audit —
not compute.

## 6. Sequence (this plan is step 3 of the census-plan's 7-step S1 sequence)

1-2 (done): census + BFO bridge — `scale-s1-multisource-census.md`.
3 (this doc, scoped): acquire the Wikidata class slice; add the root→UFO table;
run the exact-ID decontamination; re-run `census.ts` (extended with a Wikidata
loader) to MEASURE the added non-biological concept count and the new biology
share. **First measurable sub-increment:** a WDQS *count-only* query of each
class-root subtree (no dump, seconds) to replace the §2 [EXTRAPOLATION] bands with
measured counts before committing the ingest — the same "measure before you build"
discipline as the census itself.

## 7. Claim caps

- **Does (once run):** delivers the design §0 domain-balance requirement; supplies
  the first real `exactly_crosswalked_clusters` count via exact external-ID joins;
  gives open-domain (non-biological) concept coverage that the KaE / F1-K n_min=240
  MMLU gate needs to move off a hand-picked coverage island (ASM-2055).
- **Does NOT:** make any correctness/efficiency claim; measure typing PRECISION
  (the Wikidata stratum joins the §4.3 human audit); count named individuals as
  concepts; reach the ≥1M scale the SCALE-GROUND-1M flagship needs — this is the
  100k domain-balance step, not the thesis test.

---

*No feasibility conclusion. ASM-2059 in `poc/scale/asm-2050-2059.json` is a
coordinator registration action; this document only cites it.*
