# Bulk kernel tiers — auto-generating definitional knowledge from fixed sources (rev 1)

**Status:** design decision, 2026-07-07, coordinator-authored. Mandate: the maintainer wants the kernel "as comprehensive as possible with as much definitional knowledge as you can produce", auto-generated from existing fixed sources where possible.
**Author:** Kern (Claude Fable 5).

## The honesty architecture (decided)

Auto-generation must not counterfeit understanding. The concept-hash design already provides the ladder (gist §3.1, `cdef:semanticStatus` inside the hash):

1. **Explicated** — hand-authored explications (the existing 54 + future). Never auto-generated (DeepNSM ≈ 24/100 — established in wave 1; unchanged).
2. **Molecule** — hand-authored under §3.5 gates (54 today, next-100 filed).
3. **AxiomsOnly** — *the bulk tier*: structural axioms extracted mechanically from a fixed source (taxonomy, dependency graph, dimension vector, formal definition), **no semantic-adequacy claim**, visibly second-class, upgradeable per-record later. This is where auto-generation is honest, and the gist designed it in on purpose.
4. **Formal sectors (profile-M / profile-P)** — a special case: here the *source is already definitional* (a Metamath definition IS the meaning; a dimension vector IS the structure), so mechanical extraction carries full definitional force, not AxiomsOnly's reduced claim.

**Provenance is mandatory per record:** `{source, sourceVersion/hash, extractorVersion/hash, extractionDate}` — a bulk record is an *assertion by an extractor about a source*, and must be re-derivable byte-identically.

## Sources (wave A, sized for this box: ≤1 GB working set per stream, 2 shared cores)

| Source | Sector | Mechanism | Expected yield |
|---|---|---|---|
| Metamath `set.mm` (~40 MB, single file, canonical token strings) | math (profile-M) | parse df-* definitions + dependency DAG → profile-M records (the sector design chose Metamath grounding for exactly this reason) | thousands of definitional records |
| Mathlib4 (Lean) | math | feasibility assessment + small sample only this box (extractions are GB-scale); route decision recorded | report + sample |
| QUDT vocabularies (RDF, ~tens of MB) | physics (profile-P) | derive exact dimension vectors + rational conversion factors for ALL quantity kinds/units; cross-validate against QUDT's own values and **flag QUDT's errors** (known to exist) rather than inherit them | ~2,000+ records |
| WordNet 3.1 (~30 MB) | lexical AxiomsOnly | synsets → AxiomsOnly records (hypernym/meronym/antonym axioms; gloss as *annotation*, never inside the hash-equivalent identity) | ~10⁵ records |
| SI Brochure / ISO-derived tables already in physics-v0 | physics | already done (constants exact-by-fiat) | — |

Rejected for now: Wikidata (world-layer facts, multi-GB, wrong tier), Wiktionary (prose definitions — explication territory, not mechanical), schema.org (ownership/drift is what this programme escapes; bridge later via annotations).

## Interactions (decided)

- **Vectors:** bulk tiers get identity + structure now, canonical vectors **on demand** (10⁵ × D=8192 fp16 ≈ 1.6 GB — not stored wholesale on this box; the encoder is deterministic so vectors are always re-derivable). The E-series pins are unaffected (frozen corpora).
- **Mapper/coverage:** bulk lexical records do NOT silently enter the mapper (that's a pre-registration surface); they inform the next M0b-style ceiling measurement as a separate "AxiomsOnly-reachable" band, clearly distinguished from Explicated coverage.
- **Governance:** each bulk tier is an *ingestion*, recorded with source version; re-ingestions are new snapshots (gist §8 semantics). Nothing here reopens profile-1.

## Verification bar (every stream)

Deterministic re-extraction (same source bytes → same records, byte-identical); structural validation gates (DAG acyclicity where claimed, sort/dimension checks where applicable); a ≥100-record random sample manually reviewed by the extracting agent with error rate reported; extractor unit tests. Failures are findings, not embarrassments.
