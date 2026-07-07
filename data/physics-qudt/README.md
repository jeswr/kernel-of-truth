# physics-qudt — bulk physics tier extracted from QUDT v3.4.0

Scales `data/physics-v0/` to the full QUDT vocabulary under the bulk-kernel
honesty architecture (docs/design-bulk-kernel.md; docs/design-physics-sector.md).
**QUDT is the bridge target and the cross-check surface, never the numeric
authority**: every value here is derived exactly and QUDT's stated floats are
audited against the derivation — the audit is a headline deliverable
(**`qudt-discrepancies.md`**: 72 discrepancies, all adjudicated).

## Contents

| file | what |
|---|---|
| `quantitykinds.jsonl` | 1,098 QuantityKind records (one JSON per line, sorted by id) |
| `units.jsonl` | 1,972 Unit records |
| `manifest.json` | counts, source pins (release/commit/sha256), exclusion counts, cross-check summary |
| `dimension-lane.json` | exact ℤ⁷ exponent lane golden (1,098 kinds → 175 distinct vectors, 108 collision classes) |
| `exclusions.json` | every non-emitted QUDT subject, by category (machine-readable) |
| `crosscheck.json` | full cross-validation rows (exact/truncation/dust/discrepancy + findings) |
| `qudt-discrepancies.md` | **the audit report** — every mismatch analysed |
| `review-sample.json` | seeded 105-record hand-review verdicts + error rate |
| `validate.mjs` | extended validation gates (see below) |
| `tools/` | extractor pipeline + unit tests |

## Record shapes

physics-v0-compatible (`kot-phys/1`) with bulk-tier extensions:

- **QuantityKind** `{id, label, dim: Z^7 over [T,L,M,I,Theta,N,J], dimOrder, symbol?, broader?, status, semanticStatus: "AxiomsOnly", provenance, bridgesTo{qudtQuantityKind, qudtDimensionVector}}`. The `dim` vector is parsed mechanically from QUDT's dimension-vector IRI local name (slot mapping pinned in docs/design-physics-sector.md §3) and cross-checked against QUDT's explicit exponent properties; the bridge IRI is *recomputed from `dim` and byte-checked* by `validate.mjs`.
- **Unit** `{…, quantityKind, otherQuantityKinds?, scale, piExponent?, offset, coherentSI, derivation, provenance, bridgesTo{qudtUnit, ucumCode?}}` with the exact affine map `value_SI = lexical · (scale · π^piExponent) + offset`. Scale/offset are exact rationals (decimal or `p/q` strings — floats are a grammar error); **π is carried symbolically** as an integer exponent so the angle family (degree = π/180 rad) and CGS families (oersted = 250/π A/m, parsec = 648000·au/π) stay exact. `derivation` is the human-readable audit trail (atom citation, prefix chain, or factor product). Primary `quantityKind` is the code-unit-first *dimension-matching* included kind — a mechanical choice, not a semantic ranking; the full matching set is retained.
- **Provenance** (mandatory per record): source release + commit + per-file sha256, extractor version, pinned extraction date. Records are re-derivable byte-identically from the pinned source (verified: two fresh extraction runs byte-identical).

Exactness enters through `tools/atoms.mjs`: a curated table of ~190 exact
conversion atoms, each citing the primary convention that makes the number
exact (SI Brochure, 1959 International Yard & Pound Agreement, IAU
resolutions, UCUM conventional exacts, US statute, CGS relations via exact
c, …). Everything else is composed mechanically (SI/binary prefixes as exact
10^n/2^n; `qudt:hasFactorUnit` products with exponents; both paths checked
against each other when both exist). QUDT's `conversionMultiplier` is **never**
copied.

## Exclusion rules (counted; ids in `exclusions.json`)

Of 1,218 quantity kinds: 83 deprecated, 32 `NotApplicable` dimension, 3 currency
(`Currency*` — QUDT stamps them dimensionless, so a name rule is needed),
2 fractional-exponent dimension vectors (follow-up), → **1,098 emitted**.

Of 2,925 units: 85 deprecated; 183 currency + 3 digital-currency (typed) and 19
blocked-by-currency compounds; 35 counting units (+18 blocked); 5 logarithmic
(typed) + 7 blocked (log-scale is out of the affine-rational normal form —
design §4.3); 5 information units + 48 blocked (QUDT normalises bits to nats
via ln 2 — transcendental; follow-up filed); 41 empirical-factor (measured
world-layer values: dalton/CODATA, Planck units, sidereal times,
temperature-qualified liquid columns, …) + 1 blocked; 47 non-affine or
arbitrary scales (pH, Beaufort, Richter, Baume/Brix/API, IU, …; each with a
note) + 14 blocked; 441 bound only to `quantitykind:Unknown`-class kinds;
1 `NotApplicable` + 3 fractional dimension; → **1,972 emitted**.
Nothing is dropped silently; every category is machine-readable with per-unit notes.

## Validation (`node data/physics-qudt/validate.mjs`)

Exact-arithmetic gates, all fail-closed ERR_*: record shape + provenance +
manifest counts; ℤ⁷ vectors (|e| ≤ 10 pinned); **qkdv-IRI recomputation
byte-check** per kind; unit kind-set dimensional consistency; exact
scale/offset grammar; `coherentSI ⇔ (1, 0, π⁰)`; affine offsets only on the
temperature dimension; dimension-lane golden byte-compare; **physics-v0
continuity** (all 31 v0 kinds map by bridge IRI into the enlarged set with
identical exact vectors; the 10 v0 defining relations dimension-check exactly
against the enlarged vectors); negative + mutation self-tests (a flipped
exponent trips ERR_QKDV_MISMATCH + ERR_LANE_GOLDEN — verified).

## Reproducing

```bash
node data/physics-qudt/tools/fetch-source.mjs      # downloads + sha256-verifies the pinned release into tools/../source/
node data/physics-qudt/tools/extract.mjs --source data/physics-qudt/source
node data/physics-qudt/validate.mjs
node --test data/physics-qudt/tools/test/          # parser + rational/affine unit tests
node data/physics-qudt/tools/sample-review.mjs     # regenerate the seeded review sheet
```

Sources (≈6 MB of TTL) are not committed; they are pinned by sha256 in
`manifest.json` and `tools/extract.mjs` (fail-closed on mismatch).

## Honest limits

- `semanticStatus: AxiomsOnly` — records assert *what QUDT structurally says*
  plus exact conversion values; no semantic-adequacy claim. QUDT's own
  modelling choices are mirrored, not fixed (observed oddities listed in
  qudt-discrepancies.md §4; ISO 80000 alignment is a filed follow-up).
- Dimensional identity ≠ semantic identity: 108 collision classes, declared.
- The atom table is curation and can be wrong — that is why every atom is
  cross-checked against QUDT and every mismatch adjudicated in the report
  (5 of our own bugs were caught this way during development, disclosed in §5).
- Hand review: 105-record seeded sample (45 kinds + 60 units), verdicts in
  `review-sample.json`. Extraction errors found: 0; one corpus-level rule gap
  (currency kinds initially included) found and fixed during review.
