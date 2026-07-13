# SCALE-1 S1 (100k rung) — multi-source concept census + UFO-typing-yield probe

date: 2026-07-13 · script: `poc/scale/src/census.ts` · full JSON: `scale-s1-census.json` · wall: 2.8s

**Epistemic status.** Exploratory S1-preparation pilot over LOCAL bytes
(`data/lexical-wn31`, `data/onto-obo`, `data/onto-sumo`). It measures **YIELD**
(records that CAN carry a source-asserted / candidate UFO value), **NOT
PRECISION** (whether those values are correct — that needs the design §4.3
stratified human audit, which this does not perform and does not substitute
for). No encoder version, no goldens, no registry write. **NO feasibility
conclusion; CORRECTNESS and EFFICIENCY remain INCONCLUSIVE-PENDING (design §14).**

## Answers the two measured S0 blockers for the 100k rung

### §2.3 — selection-rule exhaustion (tag_cnt floored at 27,210 < 100k)

| §3.5 count | value |
|---|---|
| raw source records (WN+OBO+SUMO) | 217,688 |
| type-level clusters — UNMERGED union upper bound | 207,733 |
| — WordNet type-level (non-instance) | 110,049 |
| — OBO classes | 95,201 |
| — SUMO classes | 2,483 |
| clears 100k before cross-source merge? | **YES** |

The union headroom is >100k; the exhausted
tag_cnt rule floored at 27,210. **The selection-rule blocker is retired by the
portfolio** — but the count above is an UNMERGED upper bound (cross-source
duplicates not yet merged; exact source↔source crosswalk is S1 step-3
engineering). Exactly-crosswalked and fully-resolved counts are deliberately
NOT COMPUTED here (they need dedup engineering / human endorsement).

### §0 domain balance

OBO is entirely biological → biology share of the union = **45.83%**;
largest single ontology = GO (38,256,
18.42%). NCBITaxon is only 402 records locally, so
single-*taxonomy* domination is NOT the local risk; single-*domain* (biology) is.
**A domain-balanced 100k needs a non-biological structured source (Wikidata class
subset, §3.1) that is not yet local** — the one missing ingredient flagged.

### §2.1 — WordNet-only gave 0% identity / 0% dependence / 0% source-asserted ontic

| field | WordNet-only (S0) | multi-source yield (this probe) |
|---|---|---|
| source-asserted ontic_category | 0% | OBO is_a*→BFO: **95,189 (99.99%)**; SUMO subclass*: 2,482 (66.99%) |
| ontology-grounded ontic (STIPULATED fallback) | 0% | OBO: 10 (0.01%) |
| identity-provider candidate | 0% | OBO genus-differentia: **24,693 (25.94%)** |
| dependence candidate | 0% | OBO RO relationship edges: **46,755 (49.11%)** |
| argument/selectional typing | 0% | SUMO domain/range: 713 |

OBO BFO-reached category distribution (with bridge): {"event":24555,"object":23476,"region":691,"disposition":42106,"quality":13,"mode":1929,"role":2,"proposition":2417}.

### Increment 2 — BFO-bridge lift (source-asserted ontic FLOOR raised)

The increment-1 floor (56.7%) was set by the local **subset-only** extractor,
which dropped each ontology's root→BFO edge (GO's three roots, SO's four,
CHEBI/NCBITaxon orphan subsets, MONDO:injury, OGMS→IAO/OBI). Loading the pinned
bridge `data/onto-obo/bfo-bridge.json` (14 rows; LIT-BACKED per row —
recovered source assertions, 2 STIPULATED for MONDO:injury + NCBITaxon) raises the
source-asserted ontic yield:

| | count | % of OBO classes |
|---|---:|---:|
| increment 1 (no bridge) | 54,018 | 56.74% |
| **increment 2 (with bridge)** | **95,189** | **99.99%** |
| bridge-recovered (delta) | 41,171 | 43.25% |
| still no anchor (even with bridge) | 12 | 0.01% |

Still-unreached by ontology: {"BFO":2,"OGMS":4,"RO":3,"UBERON":3} — the 10
residue that types only via the STIPULATED ontology-grounded fallback.

**Interpretation (YIELD, not PRECISION).** A source-asserted ontic yield of
99.99% (up from 56.74%),
a nonzero identity-provider-candidate yield (genus), and a nonzero
dependence-candidate yield (RO) show the portfolio has an **evidential path** to
exactly the UFO fields WordNet-only lacked entirely. Whether those candidates are
**correct** at the §4.3 0.95 bar is a **separate human-audit measurement** this
probe does not perform. The bridge RECOVERS structure the source ontologies
assert but the extractor dropped — not new science.

## What this increment does and does not license

- **Does:** retires §2.3 (union has >100k headroom); raises the §2.1
  source-asserted ontic yield to 99.99% via the BFO
  bridge; demonstrates §2.1 has a nonzero evidential path via OBO/SUMO
  (identity/dependence off 0%); gives the first §3.5-shaped four-count skeleton
  and the domain-balance gap (needs Wikidata — see
  `docs/next/design/scale-s1-wikidata-domain-balance-plan.md`).
- **Does NOT:** compute exact post-merge type-level clusters (needs S1 dedup
  engineering); measure typing PRECISION (needs §4.3 human audit); make any
  correctness/efficiency claim; touch construction B or any registered verdict.

ASM candidates for the coordinator: `poc/scale/asm-2050-2059.json`.
