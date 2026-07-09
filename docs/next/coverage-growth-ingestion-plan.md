# Coverage-growth ingestion plan — Fable sign-off on the structured-DB quick-wins

**Kernel of Truth programme — ingestion sign-off, ordered by checkability-growth value.**
Author: Kern (Fable design agent), for @jeswr. Date: 2026-07-09.
Bead: `kernel-of-truth-7fm`. Reviews: `docs/next/structured-db-scouting.md`
(Opus reconnaissance, 318 DBs / 12 domains, SPECULATIVE / pending-Fable-signoff).

Status: **DESIGN / SIGN-OFF document. Nothing here spends money, ingests bytes, or
freezes a registry entry.** It authorises Opus to run named ingestion pipelines
*in the stated order* once the per-source verify-before-ingest flags clear. Opus runs
the pipelines (pure execution); Fable owns the extractor design for every non-OBO
source. Binding constraints: `docs/kernel-design-directives.md` (§1 no-semantic-web-
legacy, §2 two value theses, §5 facts→world-layer). Epistemic tags:
**[MEASURED]** (registry/committed data), **[verified-in-repo]** (checked in this pass),
**[LIT/scout]** (scouting finding, re-verify before ingest), **[STIPULATED]** (design
choice), **[EXTRAPOLATION]** (hope, never a premise; none is load-bearing).

---

## 0. The one-paragraph answer, and the distinction that governs everything

The scouting catalogue lists ~33 open-licensed quick-wins. I sign off **the OBO
biomedical stack (8 sources) for immediate records-only execution**, **a Cost-1
bespoke-RDF-extractor wave (schema.org → CCO → CILI → a standards/finance SKOS pack →
NCIt → general thesauri → biomedical RDF) as Fable-design work**, and I hold back the
three ingestions that actually move benchmark κ_B (**ConceptNet, a curated science
world layer, a filtered Wikidata subset**) as *world-layer/query-grammar-gated* — they
are not quick-wins and cannot deliver κ_B as ingestion alone. The governing fact,
[MEASURED] and non-negotiable: **checkability is not vocabulary coverage.** An item is
`kernel_checkable` only when three legs coincide — (1) a canonical **record**, (2) a
**licensing axiom** in the sidecar, and (3) a **mapper parse** of the item into the
closed `kot-query/1` grammar's four operators (`unique`/`lookup`/`count`/`instance`).
Structured-DB ingestion supplies legs 1 and (often) 2. It never supplies leg 3, and it
cannot exceed the 4-op grammar or the engine's refusal of `subClassOf`
(`ERR_AXIOM_UNIMPLEMENTED`) [verified-in-repo `docs/design-l3a-rules-engine-oracle.md`
§3–4]. This is why d-ext measured **≈49% lemma-touch coexisting with 0% checkability**
on OpenBookQA [MEASURED `data/d-ext/manifest.json`], and why onto-obo's 42,565 records
bought only vocabulary-membership band 0.7841 (wn31 AxiomsOnly-reachable), *never
explicated coverage* [MEASURED `registry/verdicts/m0b.json`, per rung]. **Therefore
this plan prioritises what is realizable now — linter proposition-level coverage
(records-only, delivered by ingestion) — and marks, per source, which Tier-A benchmark
κ_B it is on the critical path for, and exactly what query-grammar / world-layer work
must land alongside for that κ_B to move.**

---

## 1. Two value axes, kept distinct (the sign-off is scored on both)

Per the bead's crucial instruction — grow **checkability**, not lemma-touch — every
candidate is scored on the two consumers, which have *different* sensitivities:

- **Axis A — linter proposition-level coverage (realizable NOW, records-only).** Every
  clean definitional record moves some proposition from lattice class **U** (out of
  coverage) toward **G+/G−** (checkable) on its covered domain
  (`docs/next/kernel-precision-linter.md` §3, §6 Stage 0/2). This consumer wants
  **breadth of clean definitional records** and is satisfied by ingestion alone. It is
  the coverage-growth that ingestion delivers immediately, with no grammar work.
- **Axis B — benchmark κ_B (realizable only with paired grammar + world-layer work).**
  N1-LB's LB-GATE needs measured `kernel_checkable` κ_B ≥ 0.10–0.20 on ≥2 Tier-A
  benchmarks (`docs/next/architecture-ladder.md` §10.4) [MEASURED design constraint].
  Ingestion is the necessary *substrate* for κ_B but is never sufficient; the sign-off
  marks each source's Tier-A critical path and the leg-3 work it waits on.

A source earns high sign-off priority when it scores on **both** axes cheaply. A source
that scores only on Axis A is still signed off (the linter is a live maintainer
direction) but sequenced by cost. A source whose *only* value is Axis B is held to
Wave C, because ingesting it before its grammar/world work exists banks no value and
incurs storage/maintenance drag.

---

## 2. Cost-model correction (cheapest-first depends on getting this right)

**The scouting doc's `rdf` = "near-zero cost" label is optimistic and I am overriding
it** [verified-in-repo]. There is **no generic RDF/OWL/SKOS extractor** in the repo.
Every RDF corpus ingested so far — QUDT, SUMO, FrameNet, WordNet-3.1 — used a
**bespoke, source-specific extractor** (`data/physics-qudt/tools/extract.mjs`,
`data/onto-sumo/extractor/`, etc.). A reusable turtle-*parsing* primitive exists
(`data/physics-qudt/tools/ttl.mjs`, 270 lines), but the record-mapping logic (which
OWL/SKOS shapes become which `kot` record fields, ownership dedup, identity boundary)
is per-source design work. True cost tiers:

| Cost tier | What it means | Who runs it | Sources |
|---|---|---|---|
| **Cost-0 — pure execution** | append to `data/onto-obo/extractor/extract.mjs` `ONTOLOGIES[]`, pin sha, run extract→validate→mint (the PATO/PO pattern) [verified-in-repo] | **Opus, post-signoff** | clean OBO sources only |
| **Cost-1 — bespoke RDF extractor** | new extractor per source; `ttl.mjs` primitive reusable; SKOS/OWL→`kot` mapping is Fable design | **Fable designs, Opus runs** | the RDF quick-wins |
| **Cost-2+ — bespoke new-format extractor** | CSV/XML/JSONL/API parser from scratch | Fable designs | everything `new` |

Consequence: the *genuinely* "pure execution like PATO/PO" set is **only the OBO
sources**. Every `rdf` quick-win is a Fable-design item (lighter than `new` because
`ttl.mjs` exists, but not free). The waves below are ordered accordingly.

---

## 3. THE SIGNED-OFF SET, ordered by checkability-growth value

### WAVE A — Cost-0 OBO stack · SIGN OFF FOR IMMEDIATE EXECUTION

Pure onto-obo append; licences all open/redistributable (record `provenance.license`,
the existing onto-obo pattern). **Axis-A value: dense genus-differentia definitional
records on biomedical/technical domains** — the linter's most defensible Stage-1
scoped-domain (technical/clinical precise writing). **Axis-B value: substrate for the
definitional-MMLU medical/bio subjects** (anatomy, clinical knowledge, medical
genetics, college biology/chemistry, nutrition) — *not* OpenBookQA/ARC-Easy (those are
grade-school, not deep-bio) and *not* WiC/CommonsenseQA (lexical/commonsense). Ordered
cheapest/highest-linter-value first:

| # | Source | Ext | Licence | Size | Axis A (linter domain) | Axis B (Tier-A) | Note |
|---|---|---|---|---|---|---|---|
| A1 | **OGMS** | obo | CC0 | ~200 | disease-upper scaffold | def-MMLU (clinical) | tiny → **pipeline smoke-test**; defines "disease" itself |
| A2 | **SO** | obo | CC BY 4.0 | ~2k | genomics | def-MMLU (med-genetics) | clean, small |
| A3 | **MONDO** | obo | CC BY 4.0 | ~25k | clinical/disease | def-MMLU (clinical, med-genetics) | best disease backbone; harmonises OMIM/Orphanet/DO |
| A4 | **HPO** | obo | open (attrib.) | ~18k | clinical phenotype | def-MMLU (clinical) | **verify exact licence text before ingest** [scout flag] |
| A5 | **PRO** | obo | CC BY 4.0 | 10Ks | proteomics | def-MMLU (college-bio) | fills protein-identity gap absent from mined set |
| A6 | **ChEBI** | obo | CC BY 4.0 | ~200k | chemistry | def-MMLU (college-chem) | **LARGE → chunk ingest**; sequence after small ones |
| A7 | **NCBITaxon** | obo | CC0 | ~2M | taxonomy/organism | def-MMLU (biology), BoolQ (org facts) | **VERY LARGE → chunk/filter**; sequence LAST |
| A8 | **DOID** | obo | CC0 | ~11k | disease | (subsumed) | **OPTIONAL** — largely absorbed by MONDO (A3); ingest only if MONDO's DO-derived slice proves insufficient; M-controversy at nosology margins [scout] |

**BLOCKED within Wave A — CL + UBERON.** Extractor-clean (0 throws) and high-value
(anatomy is the densest def-MMLU-anatomy + linter-anatomy substrate), but **do NOT
sign off for execution**: the pinned first-declarer `PREFIX_OWNER = {BFO,RO,GO}`
mis-owns 5,062 UBERON terms (genus-differentia replaced by empty stubs) and would emit
3,852 foreign-prefix stub records (incl. 731 CHEBI, 492 raw `http:` IRIs)
[verified-in-repo `data/onto-obo/README.md` §"CL and UBERON deferred"]. Gated on bead
**kernel-of-truth-4im** (ownership-logic update + foreign-stub emission policy). Because
their anatomy coverage is the highest-value biomedical add for *both* axes, **4im is a
priority unblock** — recommend bumping it ahead of most of Wave B. Ingest **CARO**
(tiny anatomy upper) *with* the CL/UBERON unblock, not before.

**Lower-priority cheap OBO adds (mark, do not prioritise):** IDO, SYMP, VO (CC0/CC BY,
small biomedical niche); FoodOn (CC BY — worth noting for nutrition-MMLU + linter food
domain); UniPathway (CC BY, metabolic). Sign off only as fill-in after A1–A7.

### WAVE B — Cost-1 bespoke RDF extractor · SIGN OFF DESIGN (Fable), then execution

Each needs a bespoke extractor (`ttl.mjs` primitive reusable). Ordered by realizable
linter-coverage value (breadth × precise-writing-market fit) with benchmark critical
paths flagged:

| # | Source | Ext | Licence | Axis A (linter) | Axis B (Tier-A) | Extractor note |
|---|---|---|---|---|---|---|
| B1 | **schema.org** | rdf (RDFS) | CC BY-SA 3.0 | **highest value/byte** — general top-level types; general propositions land here | BoolQ, def-MMLU | smallest/cleanest → **build the RDF-extractor pattern here first** |
| B2 | **CCO** | rdf (OWL) | BSD-3 | mid-level agent/event/artifact/info; extends mined BFO/RO beyond biomed | def-MMLU, BoolQ | BFO-aligned → bridges cleanly to onto-obo |
| B3 | **CILI** | rdf | CC0/CC BY | concept-identity backbone; NSM-adjacent | **WiC κ_B critical path** (cross-lingual sense anchor) | dedup/bridge for mined WordNet — coordinate with lexical-wn31 |
| B4 | **standards/finance SKOS pack** — ISCO/ESCO, CPC, ISIC (+Caliper family), FIBO, GLEIF-ELF | rdf (SKOS/OWL) | CC BY / MIT / CC0 / UN-open | **the linter's regulated/precise-writing market** (§9): occupations, patents, econ-activity, finance, legal-entity forms | def-MMLU (econ/business) | one SKOS extractor covers ISCO/ESCO/CPC/ISIC; FIBO/GLEIF-ELF are OWL. The **Stage-1 mode-S dogfood domain pack** |
| B5 | **NCIt** | rdf (OWL) | CC BY 4.0 | **real per-concept textual definitions** (rare) → best G+ grounding on biomedical prose | def-MMLU (clinical/onc) | larger extractor; dual OWL/OBO fit |
| B6 | **Getty AAT + LCSH** | rdf (SKOS) | ODC-By / PD | broad general/cultural concept breadth | def-MMLU (humanities), BoolQ | one SKOS extractor serves both (+ TGN/ULAN later) |
| B7 | **biomedical RDF — ORDO, MeSH, EFO, NDF-RT** | rdf | CC BY / CC0 / Apache / PD | completes disease/drug stack; EFO integrates MONDO/HPO/UBERON/CHEBI | def-MMLU (clinical/pharm) | ingest **after** Wave A (overlaps/integrates it); NDF-RT via BioPortal inferred edition [scout — verify] |
| B8 | **GeoSPARQL, UAT, IVOA** | rdf (OWL/SKOS) | OGC / CC BY-SA / IVOA | niche geo/astronomy upper ontologies | def-MMLU (astronomy) | low priority; small |

**FMA — sign off PARTIAL only.** The OBO PURL is a partial subset; the full FMA is a
separate UW distribution with its own licence [scout]. Ingest the CC-BY-clear partial
via the B-wave extractor; **do not ingest full FMA without licence verification.**
Share-alike sources (schema.org CC BY-SA, UAT CC BY-SA) go in their **own shards** with
SA provenance so a share-alike obligation never contaminates a CC-BY/CC0 shard.

### WAVE C — κ_B-unlock ingestions · HOLD (world-layer/query-grammar-gated, NOT quick-wins)

These are where benchmark κ_B actually grows — and precisely why they are **not**
records-only quick-wins. Each requires world-layer authoring and/or a query-grammar
op; ingesting the DB is necessary but the κ_B comes from the leg-3 work.

| Source | Tier-A κ_B target | Why held | Leg-3 work required before κ_B moves |
|---|---|---|---|
| **ConceptNet** (CC BY-SA 4.0, `new`, M-controversy) | **CommonsenseQA** (ConceptNet-derived by construction) — single highest benchmark-κ_B lever | crowd-noise filter + relational world layer + a `lookup`-op over commonsense relations + mapper parse of CQA stems | recommend as the **first world-layer-authoring pilot** *after* Axis-A value is banked |
| **Wikidata (filtered subset)** (CC0, rdf, M-controversy) | **BoolQ, TruthfulQA-mc** + broad world layer | vandalism/quality filter + subset selection + broad query grammar + world-layer authoring at scale | highest breadth, highest cost → latest |
| **curated science world layer for {OpenBookQA, ARC-Easy}** | the ladder §10.4 **named first LB-GATE pair** | **no single DB *is* grade-school science facts** — this is world-layer AUTHORING seeded from schema.org types + ChEBI/GO (bio slice) + haiku-mint (physics slice) | this is world-layer design, not ingestion; Wave A/B are prerequisites, not sufficient |

---

## 4. Which ingestion unlocks which Tier-A benchmark (the κ_B routing table)

| Tier-A benchmark | κ_B route (from ladder §10.4) | Signed-off DBs that feed it | Leg-3 work that must land alongside |
|---|---|---|---|
| **WiC** | definition/molecule growth, **no world layer** | CILI (B3), + dedup of mined WordNet/DBnary | genus-differentia **`define`-op** + mapper in-context sense resolution |
| **CommonsenseQA** | relational commonsense records | ConceptNet (Wave C) | `lookup`-op over commonsense relations + CQA-stem mapper parse + crowd-noise filter |
| **definitional MMLU** (anatomy, clinical, med-genetics, college bio/chem, nutrition, econ/business) | subject definitional records | **Wave A OBO stack** + CL/UBERON (4im) + NCIt(B5) + FMA-partial + standards pack (B4) | **`define`-op** (genus-differentia lookup) + `instance`/subsumption op |
| **OpenBookQA / ARC-Easy** | science-fact **world-layer** ingestion | schema.org (B1) + ChEBI/GO (bio slice) as world-layer seed | **curated science world layer (Wave C)** + `instance`/property op + `subClassOf` op |
| **BoolQ** | broad yes/no world facts | Wikidata subset (Wave C) + schema.org | broad world layer + `instance`/`lookup` + boolean |
| **TruthfulQA-mc** | authoritative records contradicting misconceptions | NCIt (B5) + Wikidata subset (Wave C) | G−-contradiction against records — hardest; latest |

**The cheapest κ_B lever, and it needs zero new ingestion:** a **genus-differentia
`define`-op** query-grammar extension over the `logicalDefinition` field that onto-obo
*already extracts* (9,303 GO logical defs + every OBO genus-differentia
[verified-in-repo `data/onto-obo/README.md`]). This turns already-committed records
checkable for WiC-style and definitional-MMLU "what is X / X is a Y that Zs" items with
**no new bytes ingested**. Recommend it as the **first grammar-op to design** (it has
the most existing substrate); Wave A/B then multiply its yield.

---

## 5. Cheapest-first execution sequence (the ordered runlist)

1. **Wave A OBO (pure execution, Opus):** A1 OGMS (smoke-test) → A2 SO → A3 MONDO →
   A4 HPO *(after licence-text verify)* → A5 PRO → A6 ChEBI *(chunk)* →
   A7 NCBITaxon *(chunk/filter)*. [A8 DOID optional; skip if MONDO's DO-slice suffices.]
2. **Unblock bead kernel-of-truth-4im** → CL + UBERON + CARO (pure execution once the
   ownership/foreign-stub logic is fixed).
3. **Design the genus-differentia `define`-op** (grammar work; FK-L3-3 family) — cheapest
   κ_B lever, exploits already-ingested onto-obo `logicalDefinition`; re-run the b-cov
   census (§10.1) after it lands to *measure* the κ_B delta on WiC/def-MMLU.
4. **Wave B RDF extractor (Fable design → Opus run):** B1 schema.org *(proves the
   pattern)* → B2 CCO → B3 CILI → B4 standards/finance SKOS pack → B5 NCIt →
   B6 AAT/LCSH → B7 biomedical RDF → B8 geo/astronomy.
5. **Wave C (gated on world-layer/query-grammar design, sequenced after Axis-A is
   banked):** ConceptNet → CommonsenseQA world-layer pilot → curated science world
   layer for {OpenBookQA, ARC-Easy} → filtered Wikidata subset.

Re-run the **b-cov census (Tier 0, ~$0)** after *every* wave — it is the covered-slice-
growth instrument (§10.1) and the only honest measure of whether a wave moved κ_B.

---

## 6. Licensing gates (only the signed set; landmines avoided by construction)

All signed-off sources are open/redistributable (CC BY / CC0 / BSD / MIT / Apache /
ODC-By / PD). Obligations to honour in `provenance.license` (the onto-obo pattern):

- **Attribution (CC BY):** ChEBI, MONDO, HPO, PRO, SO, NCIt, ORDO, EFO, AAT, TGN, ISCO/
  ESCO, CPC, ISIC. **Share-alike (CC BY-SA):** schema.org, UAT, ConceptNet — isolate in
  own shards. **CC0/PD/BSD/MIT:** OGMS, DOID, NCBITaxon, RO-family, CILI, LCSH, CCO,
  GLEIF-ELF, MeSH, NDF-RT, FIBO.
- **Verify-before-ingest flags:** HPO exact licence text (A4); FMA partial-vs-full (B-
  wave); NDF-RT BioPortal inferred edition (B7); CILI CC0-vs-CC-BY (B3).
- **Do NOT ingest (restricted — the signed set already avoids all of these):** SNOMED CT,
  UMLS, MedDRA, OMIM, DrugBank-full, GeneCards (**ToU forbids AI training**), ICD-11
  (**CC BY-ND, no derivatives — a vectorising kernel *is* a derivative**), KEGG,
  MetaCyc, COSMIC, Wolfram MathWorld. Per scouting §6.

---

## 7. What is records-only vs needs world-layer/query-grammar work (explicit)

- **Records-only — deliver Axis-A (linter) value now, ZERO κ_B by themselves:**
  **all of Wave A and Wave B.** Sign-off does not pretend these move any benchmark.
- **Need a query-grammar/engine op before their records become checkable:**
  - *genus-differentia definitional checkability* → the **`define`-op** (§4). Cheapest;
    most existing substrate; unlocks WiC/def-MMLU definitional slice for Wave A/B taxonomic
    records.
  - *is-a / subsumption checkability* → the engine's **`subClassOf`-op** (currently
    `ERR_AXIOM_UNIMPLEMENTED` [verified-in-repo]) + an "is X a kind of Y" mapper parse.
    Unlocks the instance/subsumption slice of every taxonomic DB for def-MMLU + BoolQ.
- **Need world-layer authoring (instance facts) before κ_B:** all of Wave C. `world-v0`
  is 598 hand/synthetic records [verified-in-repo `data/world-v0/`]; scaling it is the
  binding constraint per d-ext [MEASURED]. There is **no external-DB→world-layer
  ingestion pipeline yet** — building it is part of the Wave-C design, not a quick-win.

---

## 8. Register / bead additions (NOT written here — reported per constraint)

I did not touch `registry/ideas.jsonl` (concurrent-append hazard) or `kb/*`. Recommended
additions for the maintainer/Opus to file:

1. **Wave-A OBO ingestion beads** (one per source A1–A7, or one batch bead) — pure
   execution, depends on nothing but A4's licence-text verify.
2. **Bump priority of `kernel-of-truth-4im`** (CL/UBERON owner-dedup) — it gates the
   highest-value biomedical anatomy add; move ahead of most of Wave B.
3. **New bead: genus-differentia `define`-op grammar extension** (FK-L3-3 family) — the
   cheapest κ_B lever; exploits onto-obo `logicalDefinition`; no new ingestion.
4. **New bead: Wave-B RDF-extractor design** (schema.org first, proves the SKOS/OWL→`kot`
   mapping pattern; `ttl.mjs` reusable).
5. **New bead: ConceptNet→CommonsenseQA world-layer pilot** (Wave C, world-layer
   authoring + `lookup`-op) — the first benchmark-κ_B experiment, gated on Axis-A banked.
6. **Note for `idea-leaderboard-benchmark-eval` and `idea-kernel-precision-linter`:** this
   plan is their shared coverage-growth dependency (linter §6; ladder §10.4); the b-cov
   census re-run after each wave is the shared instrument.

---

## 9. Exact changed / created paths

- **Created:** `docs/next/coverage-growth-ingestion-plan.md` (this document).
- **Changed:** none. No extractor, registry, kb, world-layer, or frozen-file touched; no
  pipeline run; no git commit/push.

---

*Cross-references:* `docs/next/structured-db-scouting.md` (the reconnaissance catalogue);
`docs/next/architecture-ladder.md` §10 (N1-LB, LB-GATE, b-cov census, Tier-A triage);
`docs/next/kernel-precision-linter.md` §3/§6 (verdict lattice, coverage staircase);
`docs/design-l3a-rules-engine-oracle.md` §3–4 (kot-axiom/1 sidecar, kot-query/1 four
ops, `subClassOf` unimplemented); `data/onto-obo/README.md` (OBO extractor, PATO/PO
append pattern, CL/UBERON 4im block, logicalDefinition substrate);
`data/d-ext/manifest.json` (≈49% lemma-touch / 0% checkable [MEASURED]);
`registry/verdicts/m0b.json` (0.7841 membership-vs-coverage envelope [MEASURED]);
`data/world-v0/` (598-record world layer — the binding constraint);
`data/physics-qudt/tools/ttl.mjs` (reusable turtle-parse primitive).
