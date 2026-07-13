# SCALE-1 S1 — bounded first-ingest pre-registration: Wikidata "position" domain

**Role:** Fable build agent (designer-6), 2026-07-13. Increment-4 of the
large-kernel domain-balance track. This PINS the spec for a **bounded, single-domain**
first ingest that validates the full download→filter→type→decontaminate→emit
pipeline off-box (Modal CPU). It is **kernel machinery, not a verdicted
experiment** — no Law-1 freeze, no registry verdict. It touches no locked doc,
issues **no feasibility conclusion** (CORRECTNESS and EFFICIENCY remain
INCONCLUSIVE-PENDING, design §14), and writes no registry/git. Assumption
candidates: `poc/scale/asm-2191-2199.json`.

Epistemic tags: **[MEASURED]** committed bytes / live-endpoint snapshot;
**[STIPULATED]** a pinned build choice; **[EXTRAPOLATION]** a forward estimate +
resolution path.

---

## 1. Scope (bounded — ONE domain)

Validate the pipeline on the single richest measured non-biological domain,
**position** (`wd:Q4164871`), measured at **103,707 P279-backbone classes**
(WDQS 2026-07-13, `poc/scale/results/wdqs-counts.json`, ASM-2160). Not the full
domain portfolio; the remaining domains are gated on this pipeline validation +
the §6 go/no-go.

## 2. Pinned selection [STIPULATED]

- **Root:** `wd:Q4164871` (position). **Cap:** none for this validation — take the
  whole measured subtree (~103,707); a per-root cap is only introduced when
  combining domains to hit a balanced 100k target (out of scope here).
- **Membership rule K:** an item is a counted type-level concept iff it lies in
  `wdt:P279* wd:Q4164871` and is **not** the root itself. Every non-root member of
  a P279* closure has ≥1 outgoing P279 edge, so all satisfy the
  `data/onto-wikidata/p31-p279-ufo-crosswalk.json` membership rule (K=1 with P279
  ancestry). Named individuals (bare P31 subjects, no P279) are absent from a P279*
  subtree by construction.
- **Determinism:** WDQS pages are `ORDER BY ?item LIMIT 20000 OFFSET k`; the
  emitted records are sorted by QID; a `contentHash` is computed over the sorted
  (id, ufo-typing, decontam-status) tuples so the chunk is reproducible modulo
  live-endpoint drift (drift disclosed, exact pinning = dump).

## 3. Typing procedure [from the crosswalk, STIPULATED terminal]

Every position-subtree member is typed by the crosswalk's `position` root row:
`ontic_category = object`, `sortality = role`, `rigidity = anti-rigid`,
`denotation_level = type`. This is the ontology-grounded terminal (a position is a
role a person plays), reported separately from the source-asserted P279 chain and
audited by the design §4.3 human sample (Wikidata is its own stratum). For each
record we ALSO retain its raw P279 parents + P31 (instance-of) + label, so richer
multi-root typing is possible later without re-pulling. The reported UFO
distribution is expected to be dominated by object/role — that dominance is the
*validation* that the single-domain crosswalk applies, not a defect.

## 4. Decontamination [exact external-ID join, MEASURED index]

Against `poc/scale/out/wikidata-position/union-extid-index.json` (built on-box from
the local shards: 128,508 WordNet keys `<offset>-<pos>`, 41 ChEBI, 402 NCBITaxon,
32,097 MONDO, 14,977 UBERON, 3,338 CL). For each item, if `P8814` (normalized to
`<offset>-<pos>`), `P686`, `P685`, or `P5270` resolves to a union key → **crosswalk
merge** (not a new concept). Else → **new concept**. Counts of both are reported;
merges keep provenance. This yields the first real design §3.5
`exactly_crosswalked_clusters` datum for a non-bio domain.

## 5. Outputs

- **Full chunk** (all typed records) → Modal Volume `kot-scale-wikidata`
  (`/vol/position/concepts.jsonl`), off-box per the box-light constraint.
- **In-repo** (`poc/scale/results/wikidata-position/`): `manifest.json` (counts,
  UFO distribution, decontam split, external-ID coverage, contentHash, wall, cost)
  + a `sample.jsonl` (first 100 records) + retrieval note.
- Record schema `kot-wikidata/1`: `{id: urn:onto-wikidata:Q..., label, p279_parents,
  p31, external_ids, ckufo: {denotation_level, ontic_category, sortality,
  rigidity}, decontam: {status, matched_key}, provenance}`.

## 5b. Balanced ~100k rung — pre-registered per-domain caps [STIPULATED, before the fan-out]

Position alone (103,714) would be ~52% of a ~200k slice and dominate, violating
design §0 (exclude single-domain domination). Pinned caps for a genuinely
domain-balanced ~100k target, **no domain > 40%**, using the four reliably-countable
non-bio domains (WDQS-measured subtree sizes in parens):

| domain | root | subtree | **cap** | share of target |
|---|---|---:|---:|---:|
| position (role) | `Q4164871` | 103,707 | **35,000** | 36.2% |
| vehicle (object/kind) | `Q42889` | 63,292 | **30,000** | 31.1% |
| organization (social-object) | `Q43229` | 50,430 | **25,000** | 25.9% |
| occupation (role) | `Q28640` | 6,616 | **all (6,616)** | 6.8% |
| **balanced target** | | | **~96,616** | max 36.2% < 40% |

**Cap rule [STIPULATED]:** take the first N QIDs by ascending QID string —
deterministic and benchmark-blind (QID order is arbitrary w.r.t. any benchmark).
**Cost-saver:** vehicle/organization are ingested *capped* (only their first
30k/25k QIDs are property-fetched). Position is NOT re-run — the balanced slice
reuses the first 35,000 records of the existing full `/position/concepts.jsonl`
chunk (it is already QID-sorted), so the full 103,714 position domain is retained
as an asset while the balance metric uses the capped 35k. The census (§ below)
applies these caps uniformly to each domain's decontaminated new-count.

## 6. RESULT + go/no-go for the remaining domains [MEASURED 2026-07-13]

The run executed on Modal CPU (`cpu=2.0`) — box only orchestrated. Result
(`poc/scale/results/wikidata-position/manifest.json`, contentHash
`1aee3712…f516458`):

| metric | value |
|---|---:|
| typed position concepts | **103,714** |
| genuinely new (survived decontamination) | **103,362** |
| crosswalk-merges vs the union (all via P8814 WordNet) | **352** (0.34%) |
| external-ID coverage | P8814 352 · P686/P685/P5270 = 0 |
| UFO typing | 103,714 × object/role/anti-rigid (position terminal) |
| wall | 699.5 s (346 WDQS property batches) |
| **Modal cost** | **~$0.025** (full $0.0245 + 16.3 s smoke $0.0006; standard-rate cpu=2.0 + ≤4 GiB) |
| full chunk | Modal Volume `kot-scale-wikidata:/position/concepts.jsonl` (off-box) |

The 0.34% collision rate confirms ASM-2161's prediction: a non-biological domain
barely overlaps our bio-heavy union, so non-bio ingests add near-entirely new
concepts.

**GO/NO-GO — GO on the remaining domains, off-box, per the same harness.** At
~$0.025 per ~104k concepts (~$0.00024/1k), ingesting vehicle (63,292) +
organization (50,430) + occupation (6,616) to assemble a benchmark-blind ~100k
domain-balanced slice is **~2-4 more Modal runs, aggregate well under $5**.

## 7. MILESTONE — balanced ~100k rung COMPLETE [MEASURED 2026-07-13]

The three remaining domains were fanned across Modal in parallel (capped per §5b),
then the 4-source census (WordNet∪OBO∪SUMO∪Wikidata) re-run
(`poc/scale/results/scale-s1-census.json` → `domain_balance_v2_with_wikidata`,
contentHash `4bd461dd…c20d6b0a`).

| domain | root | typed | genuinely new | UFO terminal | wall |
|---|---|---:|---:|---|---:|
| position | Q4164871 | 103,714 (cap→35,000) | 103,362 | object/role/anti-rigid | 699.5 s |
| vehicle | Q42889 | 30,000 | 29,843 | object/kind/rigid | 105.3 s |
| organization | Q43229 | 25,000 | 24,842 | social-object/kind/rigid | 89.4 s |
| occupation | Q28640 | 6,615 | 6,415 | object/role/anti-rigid | 40.1 s |

**Domain-balanced typed-structured core** (source-asserted-UFO-typed: OBO
all-biology + the balanced Wikidata non-bio slice):

| component | count | share |
|---|---:|---:|
| biology (OBO, BFO-typed) | 95,201 | **49.77%** |
| position (Wikidata) | 35,000 | 18.30% |
| vehicle (Wikidata) | 29,843 | 15.60% |
| organization (Wikidata) | 24,842 | 12.99% |
| occupation (Wikidata) | 6,415 | 3.35% |
| **typed-structured core** | **191,301** | 100% |

**Biology share = 49.77%** (was ~100% all-OBO) → **clears the design §0 45-65%
domain-balance band: YES**. Biology is a plurality, not a dominator; the non-bio
side spans four domains. **Total Modal cost across all Wikidata ingests ≈ $0.033**
(increment-5 portion ≈ $0.008) — deep inside the $0-20 authority. Full chunks
off-box in Modal Volume `kot-scale-wikidata:/{position,vehicle,organization,occupation}/`.

**This is a clean stopping milestone.** Escalation toward millions-of-concepts /
full-UFO / causal-benchmark use (design §7) is a separate maintainer-direction
commitment, deliberately not undertaken this pass (ASM-2201/2202).

---

*No feasibility conclusion. This is machinery; ASM-2191..2202 are coordinator
registration actions.*
