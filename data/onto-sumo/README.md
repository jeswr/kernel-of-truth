# onto-sumo — SUMO SUO-KIF axiom tier (AxiomsOnly / sumo-kif-canonical)

**15,595 KIF axioms + 3,705 declared terms** mechanically extracted from SUMO
(the Suggested Upper Merged Ontology), from `Merge.kif` (upper ontology) and
`Mid-level-ontology.kif` (MILO). This is the `AxiomsOnly` stratum of the
bulk-kernel design, in the mm-canonical style of `data/math-mm`: we emit each
SUO-KIF statement as a **canonical one-line string** and a **declared-term
inventory** with structured declaration axioms — **no semantic translation**.

| file | records | what |
|---|---|---|
| `axioms.jsonl` | 15,595 | every top-level KIF statement, `form: "sumo-kif-canonical"`, with `operator`, canonical `kif`, mentioned `terms`, declaration `subject`, and (for `<=>`) `definienda` |
| `terms.jsonl` | 3,705 | the term inventory: `kind` (class 2,483 / relation 746 / instance 328 / attribute 146), structured `axioms` (subclass/instance/subrelation/subAttribute/domain/range/partition/disjoint), `annotations` (documentation, label), `axiomStats`, and `definitionalAxiomRefs` |

Top axiom forms: `documentation` 3,637, `=>` 3,089, `subclass` 2,947,
`instance` 1,751, `domain` 1,327, `termFormat` 664, `subrelation` 216,
`range` 144. Per file: Merge 5,486 axioms, MILO 10,109.

## Licence verdict — REDISTRIBUTABLE (IEEE SUMO licence, attribution)

The IEEE licence header in each `.kif` grants a *"perpetual, non-exclusive,
royalty-free, world-wide right and license to copy, publish and distribute the
Document in any way, and to prepare derivative works … provided that the IEEE is
appropriately acknowledged as the source and copyright owner."* Derived records
may therefore be **redistributed with IEEE attribution**. It is **not** public
domain — IEEE remains the copyright holder (verdict + full quote in
`manifest.json → source.licenseVerdict` and every record's provenance).

## The honesty architecture

`semanticStatus: "AxiomsOnly"` — canonical strings + structural declaration
axioms only, **no semantic-adequacy claim**, no attempt to translate SUO-KIF
into profile-1. Inside vs outside record identity:

- **Inside identity:** the canonical `kif` string, `operator`, `terms`,
  `subject`, `definienda` (axiom records); `term`, `kind`, structured `axioms`,
  `definitionalAxiomRefs` (term records).
- **Outside identity, under `annotations`:** `documentation` (the SUMO English
  doc prose) and `label` (the `termFormat` display string). Prose docs are
  mutable annotations — never inside identity.
- **`provenance`** mandatory: SUMO repo + pinned commit + licence + extractor.

## SUMO's definitional axioms

SUMO's `<=>` biconditionals are its genuinely-definitional statements —
analogous to a set.mm `df-*`. Each term record links the biconditionals that
**syntactically define** it (`definitionalAxiomRefs`), detected by a narrow,
purely syntactic pattern — `(<=> (instance ?x T) …)` (defines class `T`) or
`(<=> (T …) …)` (defines relation/function `T`) — so a predicate merely
*mentioned* inside a compound side is never miscounted as a definition.
**48 terms** carry such a definition, e.g.

```
NegativeRealNumber ⟺ (and (lessThan ?N 0) (instance ?N RealNumber))
```

Unlike OBO genus-differentia, these are full first-order formulae; they are
**not** clean structured-explication upgrade candidates (an upgrade would need
the semantic translation the programme forbids at bulk scale). Recorded as such.

## Subset rule (stated)

`Merge.kif` + `Mid-level-ontology.kif` only — SUMO's language-independent upper
+ mid-level definitional core, where the axioms live. The ~100 domain `.kif`
files (Cars, Hotel, Medicine, …) are **out of scope** for this ingestion
(follow-up filed). This is why one structured-axiom target dangles
(`FabricIron subclass HouseUtilityAppliance` — `HouseUtilityAppliance` lives in
a domain file): an honest, counted cross-file gap, not an extraction error.

## Source pin

SUMO `github.com/ontologyportal/sumo` @ commit
`ceb2954bccf98b3d113ea82797493a2b92b3e987`; per-file sha256 in
`manifest.json → sourceFiles`. Sources are **not** committed (`source/`
gitignored).

## Files

`extractor/` — `parse-kif.mjs` (SUO-KIF reader + canonicaliser),
`extract.mjs`, `sample-review.mjs`, `parse-kif.test.mjs` (Node ≥ 20, zero deps).
`validate.mjs` — source-free structural + fixed-point re-parse check.
`alignment-kernel-v0.json` — bridges to kernel-v0/molecules-v0.

## Verification results (2026-07-07 extraction)

- **Deterministic re-extraction:** two runs byte-identical (shard sha256s).
- **Structural validation** (`validate.mjs`): all gates pass. Every one of the
  15,595 canonical `kif` strings **re-parses and is a canonical fixed point**
  (`canonical(parse(kif)) === kif`) — 0 failures — proving well-formed SUO-KIF
  and idempotent serialisation. All 66 `definitionalAxiomRefs` resolve to `<=>`
  axioms whose `definienda` include the term. 0 declaration subjects fail to
  resolve to a term record.
- **Random-sample audit** (`sample-review.mjs 200 400 0x5107`): 200 axioms
  re-derived from source by re-reading the `.kif` and taking the ordinal-th
  form (canonical must match) — **0 errors**; 400 term documentations
  re-extracted by an INDEPENDENT, comment-aware, hand-rolled quoted-string scan
  (not the S-expr parser) — **0 errors**. The audit initially surfaced two real
  issues — SUMO ships some duplicate `documentation` statements (fixed the
  extractor to deterministically keep the first English one) and some
  `;;`-commented-out duplicates (fixed the audit scanner to respect KIF
  comments) — both resolved; recorded here per the verification bar ("failures
  are findings").
- **Parser unit tests:** `node --test data/onto-sumo/extractor/parse-kif.test.mjs`
  (8 tests: comment handling, canonical fixed point, escape round-trip,
  mention/logical-op filtering, fail-closed on unbalanced parens / unterminated
  strings).

## The bridge (alignment-kernel-v0.json)

`kernel-v0:event → SUMO Process` (high), `part_of → part`, `cause → causes`
(high), `believe → believes` (medium); molecule bridges to `Human`, `Animal`,
`Plant` (high), `Artifact` / `SelfConnectedObject` (medium), and body-motion
molecules to `BodyMotion`/specific processes (medium). Categorial
correspondences only; nothing enters the mapper.

## Regenerate

```bash
cd data/onto-sumo/source
curl -sSLO https://raw.githubusercontent.com/ontologyportal/sumo/ceb2954bccf98b3d113ea82797493a2b92b3e987/Merge.kif
curl -sSLO https://raw.githubusercontent.com/ontologyportal/sumo/ceb2954bccf98b3d113ea82797493a2b92b3e987/Mid-level-ontology.kif
cd ../../..
nice -n 10 node data/onto-sumo/extractor/extract.mjs        # fails closed on sha mismatch
node          data/onto-sumo/validate.mjs
nice -n 10 node data/onto-sumo/extractor/sample-review.mjs 200 400 0x5107
node --test    data/onto-sumo/extractor/parse-kif.test.mjs
```
