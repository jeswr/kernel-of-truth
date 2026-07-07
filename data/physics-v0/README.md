# physics-v0 — the dimensional-analysis corpus

83 records in the `kot-phys/1` JSON schema: the physics sector's v0 kernel
material — base dimensions, quantity kinds with exact dimension-exponent
vectors, units as exact affine maps, the seven SI defining constants, and
defining relations as typed equation trees. Design record:
`docs/design-physics-sector.md`.

## What this is — and is not

**The definitional content is exact; the authorship is research-grade.** Every
dimension vector, unit scale/offset, and defining-constant value is exact
integer/rational arithmetic re-derived from the SI Brochure 9th ed. (BIPM
2019) — no floats anywhere in definitional content, and no numeric value
copied from QUDT (which has documented factor errors; Keil & Schindler 2018).
But the corpus is agent-authored and NOT federation-endorsed: quantity-kind
selection, NSM glosses, and `bridgesTo` IRIs are research-grade. Bridge IRIs
are explicitly `asserted-unverified` (dereference verification is a filed
follow-up); NSM glosses are prose in mostly-prime vocabulary, NOT profile-1
explications.

Record ids (`urn:physics-v0:<kind>:<slug>`) are **placeholder URNs**, not
content-address hashes — minting real `urn:concept:` identities is the
concept-hash pipeline's job, out of scope here.

## Contents

- `dimensions/` (7) — the ISQ base dimensions, pinned order
  `[T, L, M, I, Theta, N, J]` (SI Brochure Table 3 order).
- `quantitykinds/` (31) — each carries `dim`: an exact integer 7-vector of
  dimension exponents, an optional coherent-SI-unit ref, and QUDT bridges
  (`bridgesTo` pattern per concept-hash-design.md §7).
- `units/` (28) — each a `(scale, offset)` exact-rational affine map onto the
  quantity kind's coherent SI unit (sparq `units.rs` normal form): 25 coherent
  (scale 1, offset 0), plus degree-celsius (offset `273.15`), degree-fahrenheit
  (scale `5/9`, offset `45967/180`), electronvolt (scale `1.602176634e-19`,
  exact since SI 2019). Log-scale units (dB, pH) are out of v0 by design.
- `constants/` (7) — ΔνCs, c, h, e, k_B, N_A, K_cd: exact by definition since
  the 2019 SI (Brochure Table 1). Measured constants (G, m_e, α) are
  world-layer facts with uncertainty and are deliberately excluded.
- `equations/` (10) — defining relations (F = m·a … E_k = ½·m·v²) as typed
  trees in the closed profile-P equation grammar
  (quantity | constant | scalar | product | power | sum).
- `dimension-lane.json` — the emitted exact dimension-exponent lane for all 31
  quantity kinds (golden file, byte-compared on every validate run).
- `manifest.json` — counts, pinned dimension order, declared collision classes.

## Honest structure worth knowing

- **Collision classes (4):** energy~torque, action~angular-momentum,
  entropy~heat-capacity, luminous-flux~luminous-intensity share dimension
  vectors. Dimensional identity is NOT semantic identity; the corpus records
  the confounders instead of hiding them.
- **The zero vector** (plane-angle; all dimensionless kinds) makes cosine
  undefined — the lane is L2-tagged, never cosine.
- **Dimension checking is necessary, not sufficient:** the ½ in E_k = ½·m·v²
  is invisible to it (E = m·v² also checks). Recorded in the equation's notes.

## Validation

```sh
node data/physics-v0/validate.mjs           # exit 0 iff every gate passes
node data/physics-v0/validate.mjs --write   # regenerate dimension-lane.json (deliberate change only)
```

Self-contained (zero deps, exact BigInt arithmetic). Gates: corpus shape,
pinned dimension order, exact vectors with the QUDT dimension-vector IRI
recomputed and byte-compared, affine-unit rules, constant exactness, equation
grammar + exact dimension check on all 10 relations, checker-integrity
self-tests (an ill-typed E = m·c MUST fail; sum accept/reject), lane golden.
A single flipped exponent in one record trips 5 independent gates (tested).
