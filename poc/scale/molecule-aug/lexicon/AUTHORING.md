# Bridge-record authoring provenance (Tier A-1, 31 records)

**Author:** fable (lead designer/explicator role), hand-authored 2026-07-14 in a
single build session. No account handles; role names only (repo convention).
**Method:** each record was authored directly against the kot-ast/1 grammar
(`concept-def-prompt.md` §3 as the grammar reference; kernel-v0 records as
style precedent) and gated through `validate-record-ref.mjs` in the PLAN.md
topological order, so every reference resolved against the already-saved
lexicon at authoring time. All 31 passed the gate (grammar + reference policy
+ full-DAG encode, unit-norm D=8192) — first-pass green, zero gate iterations
needed. `build_manifest.mjs` re-verifies the whole 85-id set in one
`encodeConceptSet` pass and pins `lexiconSetHash`.

**Bridge-record status is `research-grade`** (kernel-v0 convention), NOT
federation-endorsed; adequacy self-flags are the author's severe self-judgment
per DESIGN.md §3.3.4 (admission-as-endorsement: lossy bridge records are
admissible — the point is factoring residual loss into one audited place).

## Self-flag tally (13 faithful / 18 lossy)

| flag | records |
|---|---|
| faithful (13) | surface, kill, animal, food, grow, name, write, own, ill, woman, institution, tool, machine |
| lossy (18) | money, hot, material, group, fight, measure, eat, man, sex, work, status, authority, law, country, duty, worth, art, game |

Recurring, honestly flagged loss patterns (each named in the record's `notes`):
deontic *must* (law, duty) rendered as known conditional sanction/judgment;
graded magnitude (hot, measure, worth) not renderable; institutionhood (money,
work, authority, country) approximated as knowing/wanting/obeying regularities;
social rank (status) via an ABOVE metaphor scoped inside a THINK quote;
body-to-bearer linkage approximate throughout (same KNOWN-WEAK as kernel-v0
`alive`); eat/drink underdetermined (no mouth molecule); man defined negatively
(cannot-bear-children kind), mirroring molecules-v0's woman-first rule.

## Devices standardized across the tier (for reviewer orientation)

- **Agentive event-kind reference:** `DO(agent X, undergoer Y, manner {concept C})`
  — "X does a C-type act on Y" (money, work, worth, own, material, tool, art, food).
- **Genus by reference:** BE-SPEC attribute = kindFrame over a concept ref
  (machine→tool, institution→group, status→group, worth→money).
- **Third-party possession:** CAN(SAY(quote[IS-MINE …])) — kernel give/take idiom.
- **Normative judgment:** THINK quote with BE-SPEC attribute = concept
  `urn:kernel-v0:right` / `urn:kernel-v0:wrong` (authority, own, duty).
- **Conduct-per-rule:** `manner` = the rule-words ref or a law-kind SP (law,
  institution, game).

## Maintainer spot-check (DESIGN §3.3.5 / PLAN gate 5 — REQUIRED before any S5 generation)

Stipulated pick, highest-leverage and most-contestable — all under
`poc/scale/molecule-aug/lexicon/records/`:

1. `money.json`  2. `law.json`  3. `status.json`  4. `sex.json`  5. `art.json`

## Disclosures

- Anti-leakage slug gate: **zero collisions** with the 100 consensus-100 eval
  slugs (mechanically asserted by `build_manifest.mjs`). One lemma-level
  near-collision is disclosed, not a gate failure: eval concept *initiation*
  (WN sense "an act that sets in motion / founding") lists lemma
  `institution`; the bridge record `urn:molaug-v0:institution` is the
  organization sense. Judges see synset-fixed inputs, so sense collision risk
  is low; flagged for the maintainer's attention.
- `mods [GOOD, intensifier MORE]` (game) and `[BIG, intensifier MORE]` (grow)
  are used as comparative approximations; the comparative object ("than the
  others"/"than before") is carried by context, and each record's notes say so.
