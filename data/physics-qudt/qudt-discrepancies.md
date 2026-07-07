# QUDT cross-validation findings — physics-qudt extraction audit

**Status:** findings report, 2026-07-07. Bead: `kernel-of-truth-4k2`. **This report is a headline deliverable of the extraction, not an appendix** (task mandate; docs/design-bulk-kernel.md verification bar: "failures are findings").
**Source audited:** QUDT public repo **v3.4.0** (commit `1137205617d03d3d5c8351ea58105b6719c5d6f0`, released 2026-06-25; file sha256s pinned in `manifest.json`).
**Method:** every emitted unit's conversion is **derived exactly** — BigInt rationals, π carried symbolically — from a curated atom table of primary conventions (`tools/atoms.mjs`, every entry cited) plus two mechanical rules (prefix scaling, factor-unit composition). QUDT's stated `conversionMultiplier`/`conversionOffset` floats are then compared against the derivation and classified, per value:

| class | meaning | count (of 2,413 checked multipliers) |
|---|---|---|
| **exact** | QUDT's decimal literal equals the exact rational, literally | 1,643 |
| **truncation** | QUDT's literal is the exact value correctly rounded at its own printed precision (half-ulp criterion) — benign float publication | 498 |
| **decimal-dust** | agrees with exact to ≥13 significant digits but the printed 30+-digit tail is arithmetic garbage (§3.3) | 200 |
| **DISCREPANCY** | disagrees with the exact value beyond its own printed precision — analysed below, every case | **72** |

Machine-readable detail for every row: `crosscheck.json`. Every one of the 72 discrepancies was adjudicated by hand; **all 72 are QUDT-side defects** (the derivation-side bugs the cross-check caught during development were fixed and are disclosed in §5 — that disclosure is part of the audit).

---

## 1. Individually-analysed findings (the interesting ones)

### 1.1 The faraday is exact since 2019; QUDT ships a 2002 measurement — `unit:F`
QUDT: `conversionMultiplier 96485.3399`. Since the 2019 SI redefinition, *e* and *N_A* are exact, so the faraday is **exact**: F = e·N_A = 1.602176634×10⁻¹⁹ × 6.02214076×10²³ C = **96 485.332 123 310 018 40 C** (our derivation, exact decimal). QUDT's 96485.3399 is the CODATA-2002-era measured value (rel. deviation 8.1×10⁻⁸ — ~5,000× larger than the value's printed precision implies). A consumer treating QUDT as authoritative inherits a pre-2019 constant. *(Also note: QUDT's `unit:F` is the faraday; the farad is `unit:FARAD` — an IRI trap we hit ourselves, §5.)*

### 1.2 The astronomical unit predates its own 2012 exact redefinition — `unit:AU`
QUDT: `149597870691.6` — the JPL DE405-era estimate. IAU 2012 Resolution B2 *defines* 1 au = **149 597 870 700 m exactly**. QUDT's value is not a rounding of the current definition (rel 5.6×10⁻¹¹, but the definition has *zero* uncertainty); it is a stale measured value.

### 1.3 A 1000× unit error — `unit:MOMME_Pearl`
QUDT: `conversionMultiplier 3.750` with kg-normal form ⇒ **3.75 kg**. The momme (Japanese pearl weight) is **3.75 g** (0.00375 kg). Grams pasted where kilograms were required: a full factor-of-1000 error, the largest in the corpus. (Related: `unit:MOMME_Textile` states 4.340 g with a pure-mass dimension vector — 4.34 is the *silk areal-density* constant in g/m², not a momme mass; unresolvable from the source, so we exclude it rather than guess. Both left unemitted or corrected-by-derivation; see exclusions.)

### 1.4 Eight real units published with `conversionMultiplier 0.0`
`SpeedOfLight` (a velocity unit whose value has been *exact* since 1983: 299 792 458 m/s — QUDT states **0.0**), `MegaEV-PER-SpeedOfLight` (momentum, MeV/c — exact since 2019: 5.344 285 992 678×10⁻²² kg·m/s), `OSM`, `MilliOSM`, `MilliOSM-PER-KiloGM`, `NCM`, `NCM_1ATM_0DEG_C_NL`, `OKTA`. A zero multiplier silently zeroes any quantity converted through it. Where an exact convention exists we derived it (e.g. NCM = 101325/(R·273.15) mol = 44.615 033 405 470 3… — *exactly* computable since 2019 because R = k_B·N_A is exact); our records carry the exact values, QUDT's zeros are flagged.

### 1.5 A multiplier inconsistent with its own factor decomposition — `unit:AC-FT_US`
QUDT declares factors `AC¹ · FT_US¹` and states `1233.48426566137344`. The exact value of *its own* composition (international acre × US survey foot) is 4046.8564224 × (1200/3937) = **1233.484 304 516 129 0…**. The stated value equals 4046.8564224 × 0.3048006 *exactly* — i.e. it was computed with the survey foot truncated to 7 digits, then printed to 18 significant digits. Diagnosis: false precision from a truncated intermediate.

### 1.6 Truncated-not-rounded — `TON_SHIPPING_UK`/`TON_SHIPPING_US`, `PK_UK`
Freight ton = 40 ft³ = **1.132 673 863 68 m³** exactly; QUDT states `1.1326` (correct rounding at that precision is 1.1327 — the value was *truncated*, not rounded). Imperial peck = 2 imperial gal = **0.009 092 18 m³ exactly** (terminating!); QUDT states `0.009092181` — one *fabricated* trailing digit beyond the exact value's end, propagated into all four PK_UK flow-rate compounds.

### 1.7 Dry barrel: statute vs quart-identity — `unit:BBL_US_DRY`
The US statute (15 U.S.C. §234) fixes the dry barrel at **7056 in³** = 0.115 627 123 584 m³. QUDT's `0.1156281989625` matches the *approximate* "105 dry quarts" identity (= 7056.065 625 in³ = 0.115 628 198 985… m³) — and even then disagrees with that identity's exact value in its 11th digit. Double defect: wrong basis, then imprecise arithmetic on it. We emit the statute value.

### 1.8 Integer dimension vectors stamped on fractional-dimension quantities
`unit:N-M-PER-W0dot5` (newton-metre per **square root** watt, the motor-constant unit) has true dimension L¹M^½T^(−½) — no integer vector exists — yet QUDT stamps `qkdv:A0E0L1I0M0H0T0D0` (= plain length) on both the unit and `quantitykind:MotorConstant`, while simultaneously giving the unit a factor `W^-0.5`. Internally inconsistent; excluded from our corpus (fractional exponents are a filed follow-up), and QUDT's integer stamp is flagged as an error.

### 1.9 A quantity kind labelled with the wrong concept — `quantitykind:LuminousIntensityDistribution`
Its only `rdfs:label` is **"Ion Concentration"@en** while its description says luminous intensity distribution (cd/klm). Copy-paste error in the source, found by the ≥100-record hand review (our record faithfully mirrors the label — annotation-level, identity unaffected).

### 1.10 Stale measured constants presented as plain numbers
`AMU`/`U`/`DA` (atomic mass constant): QUDT states 1.660 538 782 83×10⁻²⁷ kg — the **CODATA 2006** value (CODATA 2022: 1.660 539 068 92×10⁻²⁷). `CD_IT` ("International Candle"): 0.920 cd, which is the *Hefner* candle region (the historic international candle was ≈1.02 cd) — likely mislabelled. `PERMEABILITY_REL` states the pre-2019 exact 4π×10⁻⁷ for μ₀, which has been a *measured* quantity since 2019. All are excluded from our corpus as empirical/world-layer (kernel/world boundary), with the staleness noted here.

### 1.11 Unresolved conventions (left uncurated, honestly)
`HP_Boiler`: QUDT states 9809.5 W; the common convention 33 475 Btu_IT/h computes to 9810.554 W — no primary source found that yields 9809.5. `HP_H2O` (746.043 W), `MOHM` (1000 s/kg), `PERM_Metric` (10⁻¹²): no primary convention found; excluded rather than copied. These may be QUDT errors or obscure conventions — undecided, stated as such.

---

## 2. Family analyses (all remaining discrepancy rows)

### 2.1 Propagated rounded parents (≈60 of 72 rows)
QUDT evidently computes compound-unit multipliers from *already-rounded* parent values, then publishes 15–34 significant digits — false precision as a systematic practice:

- **BTU_TH family, 22 rows, rel ≈ 1.05×10⁻¹¹**: seed BTU_th = 1054.350 264 44 (11-digit rounding of the exact 4.184 × 453.59237 × 5/9 = 1054.350 264 448 888…) propagated into every thermochemical-Btu compound. Exhibit: `BTU_TH-PER-LB-DEG_R`, whose exact value is the *integer* 4184 (it is just cal_th/(g·K) rescaled), published by QUDT as `4184.000000044092117716975512617226`.
- **7-digit-gallon family** (`CUP`, `CUP_US`, `GI_US`(+4 compounds), `TBSP`, `TSP`, `OZ_VOL_US-PER-*`, rel ≈ 5.7×10⁻⁸…1.3×10⁻⁹): all match gal = 3.785412×10⁻³ (7 digits) divided down, e.g. TSP stated 4.928 921 87×10⁻⁶ = (3.785412e-3)/768 exactly; the exact value is 4.928 921 593 75×10⁻⁶.
- **Rounded-barrel family** (`BBL_US-PER-*`, `BBL_US_PET-PER-HR`, rel 3.2×10⁻⁸; `BBL_UK_PET-PER-*`, rel 3.1×10⁻⁷): compounds built on the rounded 0.1589873 / 0.1591132 instead of the exact 42-US-gal / 35-imp-gal values.
- **TON_FG family** (`TON_FG-HR`, `KiloW-PER-TON_FG`, rel 4.5×10⁻⁸): built on 3516.853 instead of the exact 12000·Btu_IT/3600 = 3516.852 842 06….
- **Limited-precision π** (`N-M-PER-ARCMIN`, `N-M-PER-MIN_Angle` rel 1.1×10⁻⁹; `LA_FT` rel 1.2×10⁻¹¹; `OHM-MIL_Circ-PER-FT` rel 4.1×10⁻⁸): π (or a π-derived parent) entered at 9–12 digits, output printed to 31+.
- Singletons of the same shape: `MI_US2` (squared a rounded survey mile), `PK_US_DRY-PER-DAY`, `GI_UK-PER-{DAY,HR}`, `OZ_F-IN`, `OZ_F-PER-IN3`, `AC-FT_US` (§1.5).

### 2.2 Zero-stated (8 rows) — §1.4.

### 2.3 Value-level errors (3 rows) — `MOMME_Pearl` (§1.3), `TON_SHIPPING_UK/US` (§1.6); plus `F`, `AU`, `BBL_US_DRY`, `PK_UK`(+4) counted in their sections.

### 2.4 Decimal-dust (200 values — a class, not individual findings)
QUDT publishes multipliers to up to 34 significant digits; in 200 cases the printed tail disagrees with the exact value below the 13th significant digit (e.g. `LB_F`: stated `4.448221615260499999999999999999998`, exact `4.4482216152605`). Harmless to any IEEE-double consumer; symptomatic of fixed-precision decimal arithmetic printing more digits than it is good for. Full list: `crosscheck.json#decimalDust`.

---

## 3. Where QUDT is clean (credit where due)

- **Dimension-vector machinery is internally consistent:** all **1,813** explicit `qudt:dimensionExponentFor*` properties match their qkdv IRI local names exactly; all **1,986** factor-unit dimensional compositions match the units' stated dimension vectors; the D-flag convention (D1 ⇔ zero vector) holds corpus-wide (the one true fractional case is §1.8). Our ℤ⁷ vectors therefore rest on a mechanically solid layer of the source.
- **All 33 prefix multipliers are exact** — the prefix errors documented by Keil & Schindler (2018) are fixed in v3.4.0.
- **The three `conversionOffset` values** (DEG_C, DEG_F, MilliDEG_C) are exactly correct under QUDT 3.x semantics `value_SI = (value + offset) × multiplier` — verified against our independently-derived affine maps (K = (°F + 459.67)·5/9, exactly 45967/180 + 5/9·x in our normal form).
- 1,643 multipliers (68%) are *literally exact* decimals of the true rational values.

## 4. Modelling observations (not extraction errors; noted from the hand review)

QUDT stamps `quantitykind:MagneticPolarization` with A/m (ISO 80000-6 defines magnetic polarisation in tesla), `quantitykind:MacroscopicCrossSection` with L² (ISO 80000-10: m⁻¹), `quantitykind:MagneticReluctivity` with E1 where dimensional algebra of H/B gives E2, and models `StochasticProcess`/`IncidenceProportion` as T⁻¹ rates. Our records mirror the source faithfully (AxiomsOnly: assertions *about the source*); these are flagged for the ISO 80000 alignment follow-up, not silently "fixed".

Also: **441 units** (15% of the vocabulary) are bound only to `quantitykind:Unknown` or other excluded placeholder kinds — a large modelling gap in the source (excluded here as `quantity-kind-excluded`).

## 5. What the cross-check caught on OUR side (disclosed)

The same pipeline caught five derivation-side bugs during development — fixed before emission, disclosed here because an audit that only reports the other side's errors is not an audit: (i) mmHg computed with g/cm³ not converted to kg/m³ (1000× off); (ii) `THM_US` initially set to 10⁵ Btu_IT — that is the *EC* therm; the US therm is 105 480 400 J exactly; (iii) `PT` initially curated as the DTP point (1/72 in) where QUDT means the printer's point (0.013837 in); (iv) `BBL_UK_PET` initially assumed 42 US gal — it is 35 imperial gal; (v) the **factor-lists-are-not-scale-decompositions trap**: for `POND`, `KIP_F`, `LA_FT`, `TON_Register`, `GAL_US_DRY` QUDT's `hasFactorUnit` describes only the *dimension*, and composing it for scale gives wrong values (e.g. pond ≠ 1 N) — each now derived from its primary convention instead. Every one of these surfaced as a cross-check discrepancy; none survived into the emitted records. **This is the empirical case for deriving and cross-checking rather than copying — in both directions.**

## 6. Pointers

Complete machine-readable rows: `crosscheck.json` (`discrepancies`, `decimalDust`, `truncations`, `otherFindings`); exclusion rules and every excluded id: `exclusions.json` + `README.md`; derivation audit trail: per-record `derivation` field in `units.jsonl`.
