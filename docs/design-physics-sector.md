# Physics sector — dimensional-analysis layer design + v0 corpus

**Status:** design record, 2026-07-07. Bead: `kernel-of-truth-kf9`.
**Author:** physics-sector agent (Claude Fable 5), for @jeswr.
**Mandate anchor:** the maintainer explicitly names physical units as an admissible non-NSM concept basis (notes/mandate.md, "Maintainer's framing notes": *"Not locked into NSM: other concept bases are admissible where needed (foundational mathematics, physical units)"*).
**Honesty contract:** claims tagged **[established]** / **[claimed]** / **[speculative]**; negative structure (confounders, limits) reported at full strength.
**Artifacts:** `data/physics-v0/` (83 records + `validate.mjs` + emitted `dimension-lane.json`); this document.

---

## 0. Executive summary

The SI dimension system is a 7-dimensional exact vector space: every physical quantity kind carries a vector of integer dimension exponents over (T, L, M, I, Θ, N, J), products of quantities add vectors, powers scale them, and two quantities are dimensionally compatible iff their vectors are equal — **dimensional analysis is exact integer linear algebra** [established — this is the content of the Buckingham-π / dimensional-homogeneity formalism; SI Brochure 9th ed. (BIPM 2019) §2.3.3 defines the seven base dimensions, ISO 80000-1 the ISQ]. That gives the physics sector something no other kernel sector has: a concept family whose semantic backbone embeds into a vector lane **provably exactly, with zero training, zero seeds, and zero floats** — the strongest deterministic-semantic-geometry story anywhere in the kernel.

Since the 2019 SI revision, the seven defining constants (ΔνCs, c, h, e, k_B, N_A, K_cd) are **exact by fiat** — their numeric values are definitions, not measurements [established — SI Brochure 9th ed., Table 1]. They are kernel material par excellence: definitional, drift-free, small. Every *other* constant (G, m_e, α, …) is a measured world-layer fact with uncertainty and stays out of the kernel by the same boundary the mandate already draws for world-facts.

**Day-one runnable result:** the v0 corpus ships 83 records and a self-contained exact-arithmetic checker; all 10 defining-relation equations (F = m·a through E_k = ½·m·v²) **dimension-check exactly** (integer-vector equality, BigInt arithmetic), the checker's negative self-test (an ill-typed E = m·c) fails as required, and a single flipped exponent in one record trips 5 independent gates. Bridging target: **QUDT**, via the sanctioned `bridgesTo` pattern (§3).

---

## 1. The dimension-vector layer

### 1.1 The mathematical object

Fix the base-dimension order **[T, L, M, I, Θ, N, J]** (time, length, mass, electric current, thermodynamic temperature, amount of substance, luminous intensity — SI Brochure Table 3 order; pinned in every record as `dimOrder`, ASCII `Theta` for Θ). Then:

- A **quantity kind** carries `dim ∈ Z^7` — e.g. force = [−2, 1, 1, 0, 0, 0, 0] (kg·m·s⁻²).
- **Multiplication of quantities = vector addition**; **integer powers = scalar multiplication**; **addition of quantities is defined only within one vector** (dimensional homogeneity). This is a group homomorphism from the multiplicative group of quantity dimensions onto (Z^7, +) [established].
- A **unit** is an exact affine map onto the quantity kind's coherent SI unit: `value_SI = lexical·scale + offset`, scale/offset exact rationals. Coherent SI units are exactly the (scale=1, offset=0) points. This is precisely sparq's `units.rs` normal form (§2).
- A **defining relation** (F = m·a) is a typed equation tree over quantity-kind and constant refs whose two sides must have equal dimension vectors — a decidable, exact check (§4.4).

All of this is exact integer/rational arithmetic. In v0 the exponents are integers with |e| ≤ 8 pinned as a cap (corpus range is [−3, 4]). **Honest scope note:** QUDT admits *rational* dimension exponents (e.g. `T-2dot5` in dimension-vector IRIs for spectral quantities) [established — QUDT dimension-vector vocabulary, dot-encoding for fractional exponents]; v0 restricts to integers and flags rational exponents as an admissible extension under the same exact-arithmetic discipline (follow-up, §7).

### 1.2 The dimension lane in the encoder — typed-lane discipline

The estate precedent is sparq's structured-row discipline: a node vector is a partitioned object of contiguous typed `Block`s, each carrying `(encoder tag, metric tag, offset, width)`, with a metric-correctness guard making "cosine on a non-Euclidean block" a detectable error (reports/sparq-estate.md §1.1(c), `encode.rs:532-709`); and its **QUDT unit normaliser**: a curated affine table to canonical SI per QuantityKind, unknown/compound units failing closed — *never* treated as dimensionless — with quantity kind as a routing slot "so a length never shares a block with a mass" (reports/sparq-estate.md §1.1(b), `units.rs:103-208, 44-76, 173-178`). The physics sector adopts both disciplines wholesale.

**The lane (prototyped in v0, `dimension-lane.json`):** for every quantity-kind record, the exact 7-integer exponent vector, emitted deterministically (sorted ids, golden-file byte-compare on every validate run). Properties, all checked:

- **Exactness/determinism** [established, runnable]: derived from record content only; no seeds, no floats, no fit corpus. Same record → same lane bytes, byte-for-byte.
- **Compositional correctness** [established, runnable]: lane(a·b) = lane(a) + lane(b) and lane(aⁿ) = n·lane(a) hold *exactly* — this is what makes the 10-equation dimension check a real correctness result rather than a similarity anecdote.
- **Injectivity, stated honestly** [established, runnable]: the map quantity-kind → vector is **not** injective and cannot be: 31 v0 kinds → 27 distinct vectors, 4 collision classes (§1.3).

**Integration into the kernel encoder (design, not yet built — follow-up bead):** the dimension lane becomes one typed block of a physics concept's canonical vector, concatenated/bound with the relational (explication-derived) part exactly as construction B binds its clause lanes (docs/architecture.md §1.2). Concretely: per-component encoding over the pinned exponent range via thermometer codes with **profile-pinned breakpoints** (sparq's `NumericEncoder` with the fit-free adaptation named in reports/sparq-estate.md §6 "Adaptable" item 4), block tagged `dim-exponent/1`, metric **L2 only** — cosine is undefined at the zero vector (all dimensionless kinds sit at the origin), so the metric tag is load-bearing, not decorative. Unit records additionally carry (scale, offset); the exact rationals stay in the record (identity layer), while the *geometry* lane for scale uses log10(scale) under a pinned-breakpoint thermometer — an explicitly approximate-but-deterministic block, floats admissible there because it is geometry, never identity. Any change to lane layout or breakpoints is an encoder version change (ALGORITHM_VERSION bump + golden regeneration, per encoder/ conventions).

### 1.3 What similarity in dimension space means — and does not mean

**Means** [established]: L2/L1 distance between exponent vectors measures *dimensional relatedness* — velocity and acceleration differ by exactly one power of T (distance 1 in L1); energy and power likewise. Dimensional neighbourhoods are real, exact, and useful for unit-sanity routing (a candidate unit for a force slot must land on [−2,1,1,0,0,0,0], full stop — a slot match, never a cosine threshold, mirroring sparq's enum-codebook posture).

**Does NOT mean** [established — the recorded confounders]: dimensional identity is not semantic identity. The v0 corpus deliberately contains all four classic collision classes and declares them in `manifest.json#collisionClasses`:

1. **torque ~ energy** — both M·L²·T⁻². The SI itself refuses the identification: torque's coherent unit is named newton-metre, *not* joule (SI Brochure §2.3.4). v0 deliberately ships no newton-metre unit record to avoid implying joule-equivalence.
2. **action ~ angular-momentum** — both M·L²·T⁻¹ (J·s).
3. **entropy ~ heat-capacity** — both M·L²·T⁻²·Θ⁻¹ (J/K); k_B's quantity-kind assignment (entropy) is flagged as conventional in its record.
4. **luminous-flux ~ luminous-intensity** — lm = cd·sr and the steradian is dimensionless.

Plus the degenerate class: **every dimensionless quantity kind collides at the zero vector** (plane-angle in v0; also solid angle, refractive index, mole fractions… as the corpus grows). Consequences drawn: the dimension lane **alone** can never be a concept's identity or its full geometry — it is one exact typed block *bound with* the relational/explication part, which is precisely what separates torque from energy (their defining relations differ: τ = r × F is a cross product; W = F·d a scalar product — profile-P trees give them different relational content even though the v0 dimension check, correctly, cannot tell them apart; the `work-force-displacement` record says so in its notes). This is the same "structural overlap ≠ semantic similarity" honesty the kernel already practises (docs/architecture.md §1.2 known weaknesses), instantiated with physics' own canonical counterexamples.

---

## 2. Estate precedent: sparq `units.rs`

Cited as the design's ancestor, per the tasking: sparq-vectors' QUDT unit normalisation is **a curated affine table (`canonical = lexical·factor + offset`) to canonical SI per QuantityKind; unknown/compound units fail closed (`None`, never treated as dimensionless); quantity kind is a routing slot so a length never shares a block with a mass** (reports/sparq-estate.md §1.1(b), citing `crates/sparq-vectors/src/units.rs:103-208, 180-200, 44-76, 173-178`) [established — code on disk, surveyed read-only]. What physics-v0 adds over that precedent: (a) the affine table's *content* becomes content-addressed kernel records instead of a curated in-crate table; (b) coefficients are exact rationals, not f64 (`5/9` is not a float); (c) the quantity-kind routing slot generalises into the full exponent-vector lane; (d) the fail-closed posture is inherited — `validate.mjs` rejects unknown refs, non-rational literals, non-integer exponents, off-kind affine offsets, and grammar violations with ERR_* codes, exit 1.

---

## 3. Source ontologies: QUDT vs UCUM vs OM2 — survey and choice

Survey (web, 2026-07-07; sources at end of section):

| | **QUDT** | **UCUM** | **OM2** |
|---|---|---|---|
| Nature | OWL ontology suite: quantity kinds, units, **first-class dimension-vector resources** (`qkdv:` namespace) | Code system + grammar for unit *expressions*; not an ontology (no quantity-kind layer, no IRIs per concept) | OWL 2 ontology, ~1,300 units, quantities/dimensions/application areas |
| Dimension model | Every unit and quantity kind links to a `QuantityKindDimensionVector` whose IRI *is* the exponent tuple (e.g. `A0E0L1I0M0H0T-2D0` = L·T⁻²); exponent properties now *inferred from the IRI local name at build* — i.e. QUDT itself treats the vector as the canonical object | None (dimensions derivable from the grammar, not addressable) | Has dimension modelling with SI exponents, honest to note — but not IRI-mechanical the way qkdv is |
| Conversion | `conversionMultiplier`(+offset) per unit → affine SI normalisation | Grammar-computable | Factor + SI-unit link per unit |
| Known defects | **Documented factor errors**: Keil & Schindler 2018 found wrong factors in three conversions and two prefixes, plus reasoner-breaking type conflicts [established — SWJ 10.3233/SW-180310]. Actively maintained public repo since | Rules-based; no semantic layer to bridge concepts to | Fewer documented defects; smaller ecosystem overlap with this estate |
| Estate precedent | **sparq `units.rs` is already keyed on QUDT QuantityKinds** (§2); sparq's `grounding.rs` recognises the `qudt:numericValue`+`qudt:unit` shape (reports/sparq-estate.md §2) | none | none |

**Choice: QUDT is the bridging target**, via the `bridgesTo` pattern — the one sanctioned external-IRI-in-hash case, established for XSD datatypes in concept-hash-design.md §7 ("XSD datatypes get thin bridge concepts (e.g. `c:xsd-boolean`: axioms = `bridgesTo <…XMLSchema#boolean>`) — the one sanctioned external-IRI-in-hash case, since XSD lexical spaces are the substrate the record format itself stands on"). The physics parallel is exact: QUDT's dimension-vector IRIs are the substrate the *interop* stands on, and they are **mechanically derivable from our own exponent vectors** — `validate.mjs` recomputes every asserted `qkdv:` IRI from `dim` and byte-compares (the QUDT slot mapping is pinned: A=N, E=I, L=L, I=J, M=M, H=Θ, T=T, D=dimensionless flag — note the traps: QUDT's `I` is *luminous intensity*, not current; `H` is temperature). Reasons, ranked:

1. **Structural match** — QUDT is the only candidate whose canonical object *is* our canonical object (the dimension vector as an addressable resource with a mechanical IRI). Bridging is arithmetic, not curation.
2. **Estate precedent** — sparq already normalises through QUDT quantity kinds (§2); one bridging target across the estate.
3. **Adoption/maintenance** — active public repo, releases; broad LOD usage.

**With two recorded caveats:** (i) **bridge for identity, never for values** — QUDT's documented factor errors mean every definitional number in physics-v0 is re-derived from the SI Brochure (primary source) and no numeric content is imported from QUDT; the bridge asserts *this record ↔ that IRI*, nothing more. (ii) All `bridgesTo` IRIs in v0 are marked `asserted-unverified` — asserted from documentation knowledge, not yet verified by dereference; the verification harness is a filed follow-up (fail-closed: an unresolvable or shape-mismatched bridge IRI kills the bridge annotation, not the record). Profile-P as a whole rides the **permissionless-profiles** rule (concept-hash-design.md §8): minting a physics profile is permissionless — a new content-addressed bundle hash + header string; *adoption* is federation endorsement, same governance as everything else.

**UCUM is retained at the annotation level**: unit records carry `ucumCode` (e.g. `Cel`, `[degF]`, `eV`) because UCUM is the deployed lingua franca of the biomedical/interchange world; but it cannot be the bridge target — it has no per-concept IRIs and no quantity-kind layer to bridge *to*. **OM2 rejected** as target, honestly: it does model dimensions with exponents and is well-built [established — Rijgersberg et al., SWJ]; the decision rides on QUDT's mechanical dimension-vector IRIs and the estate precedent, not on any OM2 defect. An OM2 bridge can be added later as annotations by anyone (Mode-A discipline; concept-hash-design.md §7 legacy bridging).

Sources: [qudt.org](https://qudt.org/), [QUDT schema doc](https://www.qudt.org/doc/DOC_SCHEMA-QUDT.html), [QUDT dimension-vectors vocabulary](https://www.qudt.org/doc/2023/09/DOC_VOCAB-QUANTITY-KIND-DIMENSION-VECTORS-v2.1.html), [qudt-public-repo releases](https://github.com/qudt/qudt-public-repo/releases) (dot-encoded fractional exponents; exponent properties inferred from IRI local names), [Winston, "The QUDT System for Dimensional Analysis and Unit Conversions"](https://donnywinston.com/posts/the-qudt-system-for-dimensional-analysis-and-unit-conversions/), [Keil & Schindler 2018, "Comparison and evaluation of ontologies for units of measurement", Semantic Web 10.3233/SW-180310](https://journals.sagepub.com/doi/10.3233/SW-180310), [UCUM in RDF (cdt:ucum), Lefrançois & Zimmermann](https://hal.science/hal-01885337/document), [OM repo](https://github.com/HajoRijgersberg/OM), [SI Brochure 9th ed., BIPM 2019](https://www.bipm.org/en/publications/si-brochure).

---

## 4. Records taxonomy (`kot-phys/1`)

Five record types; ids `urn:physics-v0:<kind>:<slug>` (placeholder URNs — content-address minting is the concept-hash pipeline's job). Authoring follows kernel-v0 house patterns: per-record `status`, `notes` for known weaknesses, manifest cross-checks, fail-closed validation.

### 4.1 BaseDimension (7)

The ISQ base dimensions, pinned order [T, L, M, I, Θ, N, J] with `index` 0–6 and the SI base unit ref. These are the profile-P leaf layer — the physics analogue of the prime records: by hypothesis not further definable *within the profile* (the SI defines them operationally via the defining constants; that operational content lives in the constants' records, not here).

### 4.2 QuantityKind (31)

`{id, label, dim: Z^7, dimOrder, coherentSIUnit?, nsmGloss?, notes?, bridgesTo{qudtQuantityKind?, qudtDimensionVector}}`. Spans base kinds through velocity, force, energy, action, the electrical family, entropy, and the photometric family — including, deliberately, all four confounder pairs (§1.3). `coherentSIUnit` is optional (torque's is deliberately absent, §1.3) and must resolve to a coherent unit of the same kind (checked). **NSM glosses:** 12 records carry `nsmGloss` — prose in mostly-prime vocabulary ("something moves; after some time it is in another place; this is how far the other place is for how much time" — velocity), each stamped `research-grade prose gloss …; NOT a profile-1 explication; adequacy unvalidated`. Honesty: these are bridge material toward future profile-1 explications, included where a gloss seemed genuinely defensible and omitted where it did not (no gloss for electric-current: NSM has no honest path to it).

### 4.3 Unit (28)

`{id, label, symbol, quantityKind, scale, offset, coherentSI, bridgesTo{qudtUnit?, ucumCode?}}` — an exact affine map `value_SI = lexical·scale + offset` (sparq normal form, §2). Scale/offset grammar: exact decimal strings (`"273.15"`, `"1.602176634e-19"`) or integer fractions (`"5/9"`, `"45967/180"`); parsed to BigInt rationals; **floats are a validation error by construction**. 25 coherent units (the 7 base, 12 named derived, 6 compound coherent like m·s⁻¹ and J·K⁻¹ needed as constants' units); 3 non-coherent exhibits: **degree-celsius** (offset 273.15 — the affine exemplar), **degree-fahrenheit** (scale 5/9, offset 45967/180 — exercises non-terminating-decimal exactness), **electronvolt** (scale 1.602176634×10⁻¹⁹ — *exact* since SI 2019 because e is exact: a non-coherent unit whose factor is nonetheless definitional). v0 rules, checked: `coherentSI ⇔ (scale=1 ∧ offset=0)`; affine offsets admitted only on thermodynamic-temperature. **Log-scale units (dB, pH, magnitudes) are flagged out of v0**: they are not affine maps and need a `logScale` record extension with its own exact base/reference semantics (follow-up).

### 4.4 DefiningConstant (7)

ΔνCs, c, h, e, k_B, N_A, K_cd — `{value (exact decimal string), quantityKind, coherentSIUnit, status: "exact-by-definition", source: SI Brochure Table 1}`. **The kernel/world boundary, kept sharp:** these seven are definitions — the 2019 SI *defines* the second, metre, kilogram, ampere, kelvin, mole and candela by fixing these numbers [established]. Every record carries the boundary statement verbatim: measured constants (G, m_e, α, …) carry uncertainty and are **world-layer facts, deliberately excluded**. k_B's kind-assignment (entropy vs heat-capacity — same vector) is flagged conventional in its record.

### 4.5 DefiningRelation (10) — the closed equation grammar (profile-P's core)

```
Equation   := { lhs: QExpr, rhs: QExpr }        # semantics: dim(lhs) == dim(rhs), exactly
QExpr      := { kind: "quantity", ref }          # dim = the kind's vector
            | { kind: "constant", ref }          # dim = the constant's kind's vector
            | { kind: "scalar",   value }        # exact rational literal; dim = 0⃗
            | { kind: "product",  factors[≥2] }  # dim = Σ dim(factorᵢ)
            | { kind: "power",    base, exponent } # nonzero integer; dim = n·dim(base)
            | { kind: "sum",      terms[≥2] }    # all terms one exact vector, else ERR
```

Closed (six node kinds, no extension point), depth-capped (8), integer exponents only in v0 (rational exponents flagged, §1.1). Dimension inference is a ~40-line exact fold (`validate.mjs` `dimOf`). The 10 v0 relations: F = m·a, p = m·v, E = F·l (torque-confounder exhibit), p = F/A, Q = I·t, R = V/I (definitional reading — the ohm as V/A, *not* an empirical linearity claim; recorded in notes), E = h·ν, E = m·c², E = k_B·T (the relation through which fixing k_B fixes the kelvin), E_k = ½·m·v² (scalar exhibit). `sum` is spec'd and enforced (accept/reject self-tests) but unexercised by v0 records — defining relations at this tier don't need it; kinematics-tier model equations will.

**Result (runnable, day one)** [established]: `node data/physics-v0/validate.mjs` → **10/10 relations EXACT-PASS** (BigInt vector equality); the negative self-test (E = m·c) fails as required; a hand-mutated exponent in `force.json` trips 5 independent gates (ERR_QKDV_MISMATCH + 3× ERR_EQ_DIM + ERR_LANE_GOLDEN) and exits 1 — verified, then reverted. This is the profile-P claim in miniature: **a defining relation must dimension-check exactly, and the checker can actually reject.**

---

## 5. What physics buys the LLM-kernel story

1. **Unit-sanity verification at the interface (A5-shaped)** [established mechanism, unmeasured benefit]: dimensional-consistency checking of model outputs is *decidable, exact, and cheap* — parse an emitted quantity/equation against kernel records, fold the tree, compare integer vectors. This is exactly the architecture-A5 decode-verify loop (docs/architecture.md §4) with a verifier that is not heuristic: a model that emits "energy in newtons" or sums a length with a time is caught by arithmetic, not by another model's opinion. It composes with sparq's fail-closed posture: unknown unit → reject, never assume dimensionless.
2. **Physics word-problem probes for the E-series** [speculative until run]: dimension-typed problems generate label-free correctness signals (does the model's answer carry the dimensionally forced unit?) — probe candidates for E-series harnesses, filed as a follow-up bead, not claimed as results.
3. **The exactness exhibit for the pitch** [established]: for every other sector, "deterministic semantic geometry" is a constructed claim with measured margins; for the dimension lane it is a *theorem about the domain* (the exponent map is a homomorphism). The weakest link is honestly placed: the lane is exact, but it is one lane — semantic identity still needs the relational part (§1.3).

**The limits, stated at full strength:** the kernel holds **definitions and dimensional structure, not empirical dynamics**. Dimension-checking is necessary, never sufficient (E = m·v² checks; the ½ is invisible; torque passes wherever energy does). Defining relations are definitional readings (R = V/I defines the ohm; it does not assert material linearity). Nothing here claims a model *understands* force — the claim is that reference to these definitions cannot drift and violations of dimensional structure are mechanically detectable. Empirical physics (values of measured constants, dynamics, material laws) is world-layer or out of scope entirely.

---

## 6. v0 corpus summary

83 records: 7 BaseDimension + 31 QuantityKind + 28 Unit + 7 DefiningConstant + 10 DefiningRelation. Dimension lane: 31 kinds → 27 distinct exact vectors; 4 declared collision classes. Validation: self-contained `validate.mjs`, zero deps, all-BigInt definitional arithmetic, golden-file lane discipline, checker-integrity self-tests. All gates green at commit. Known weaknesses, listed: bridges asserted-unverified; NSM glosses research-grade prose; quantity-kind *selection* is a curation judgement (no completeness claim); log-scale units and rational exponents excluded; no profile-P content-addressed bundle exists yet (ids are placeholders).

## 7. Follow-ups (filed as beads)

1. **Profile-P encoder integration** — dimension lane as a typed block in the kernel encoder (pinned-breakpoint thermometer over exponents, L2 metric tag, log-scale geometry lane for unit scale), ALGORITHM_VERSION bump + goldens; plus the log-scale/rational-exponent record extensions.
2. **Unit-conversion + bridge verification harness** — exact affine conversion checks across the unit table; dereference-verify every `bridgesTo` IRI (guarded-fetch discipline), fail-closed; UCUM codes checked against the UCUM grammar.
3. **Physics probes for the E-series** — dimensional-consistency probes of model outputs + a dimension-typed word-problem set, pre-registered in the poc-design style before any run.
