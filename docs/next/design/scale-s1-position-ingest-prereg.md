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

## 6. Go/no-go for the remaining domains

Reported after the run in `poc/scale/results/wikidata-position/manifest.json` and
ASM-2195: given the measured per-domain wall + Modal cost for position (~103k
classes), extrapolate the cost of ingesting vehicle/organization/occupation/… to a
balanced 100k target, with a GO/NO-GO recommendation and whether it stays inside
the $0-20 standing authority.

---

*No feasibility conclusion. This is machinery pre-registration; ASM-2191..2196 are
coordinator registration actions.*
