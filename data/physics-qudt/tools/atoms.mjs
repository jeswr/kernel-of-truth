/**
 * Curated exact-atom table for the physics-qudt extraction.
 *
 * This is where exactness ENTERS the derivation: every entry is an exact
 * affine map to the coherent SI unit of its dimension,
 *     value_SI = lexical * (scale * pi^piExp) + offset,
 * with scale/offset exact BigInt rationals and pi carried symbolically
 * (rational.mjs P-scalars). Every entry cites the PRIMARY convention that
 * makes the number exact-by-definition. QUDT's floating conversionMultiplier
 * is NEVER the source of any value here — QUDT is cross-checked against this
 * table by the extractor, per the sector design (docs/design-physics-sector.md
 * §3: "bridge for identity, never for values"; Keil & Schindler 2018
 * documented QUDT factor errors).
 *
 * Everything NOT in this table is either derived mechanically (prefix rule,
 * factor-unit composition — see extract.mjs) or excluded with a counted
 * reason. EMPIRICAL lists units whose factor is a MEASURED quantity
 * (world-layer by the kernel/world boundary, docs/design-physics-sector.md
 * §4.4) — they are excluded, never approximated.
 *
 * Keys are QUDT unit-IRI local names (http://qudt.org/vocab/unit/<KEY>).
 */
import { R, R1, R0, rParse as d, rMul, rDiv, rPow, P } from './rational.mjs';

// --- building blocks (exact, cited at point of use below) ----------------------
const IN = d('0.0254');                    // international inch: 1959 Int'l Yard & Pound Agreement
const FT = rMul(IN, R(12n));               // 0.3048 m
const YD = rMul(FT, R(3n));                // 0.9144 m
const MI = rMul(FT, R(5280n));             // 1609.344 m
const FT_US = R(1200n, 3937n);             // US survey foot: US Metric Act 1866 / NIST HB44
const LB = d('0.45359237');                // avoirdupois pound: 1959 Int'l Yard & Pound Agreement
const G_N = d('9.80665');                  // standard gravity: 3rd CGPM (1901), conventional exact
const LBF = rMul(LB, G_N);                 // 4.4482216152605 N
const GAL_US = rMul(R(231n), rPow(IN, 3)); // US gallon: 231 in^3 (NIST HB44 App. C)
const GAL_UK = d('0.00454609');            // imperial gallon: UK Weights & Measures Act 1985
const CAL_TH = d('4.184');                 // thermochemical calorie: conventional exact (NIST SP811 B.8)
const CAL_IT = d('4.1868');                // IT calorie: 5th Int'l Conf. on Properties of Steam (1956)
const DEGF_K = R(5n, 9n);                  // Fahrenheit/Rankine interval
const BTU_IT = rMul(rMul(CAL_IT, rMul(LB, R(1000n))), DEGF_K); // = 1055.05585262 J exactly (ISO 80000-5 value)
const BTU_TH = rMul(rMul(CAL_TH, rMul(LB, R(1000n))), DEGF_K); // thermochemical Btu (exact fraction, non-terminating)
const MMHG = rMul(rMul(d('13595.1'), G_N), d('0.001')); // conventional mercury column: 13595.1 kg/m^3 x g_n x 1mm = 133.322387415 Pa (BIPM SI Brochure 8th ed. Table 9)
const JYR = R(31557600n);                  // Julian year 365.25 d (IAU; UCUM 'a_j')
const AU = R(149597870700n);               // astronomical unit: IAU 2012 Resolution B2, exact
const C_LIGHT = R(299792458n);             // c exact (SI 2019)
const LIGHTYEAR = rMul(C_LIGHT, JYR);      // c x Julian year = 9460730472580800 m (IAU)
const STATC = rDiv(d('0.1'), C_LIGHT);     // CGS-ESU charge: statcoulomb = (0.1/c) C, exact via exact c
const IN_HG = rMul(MMHG, d('25.4'));       // conventional inch of mercury = 25.4 mmHg = 3386.388640341 Pa exact
const DRY_QT = rMul(d('67.200625'), rPow(IN, 3)); // US dry quart = bushel/32

const src = {
  si: 'SI Brochure 9th ed. (BIPM 2019): coherent SI unit, scale 1 by definition',
  siTable8: 'SI Brochure 9th ed. Table 8 (non-SI units accepted for use with the SI)',
  yp1959: 'International Yard and Pound Agreement (1959); NIST Handbook 44 App. C',
  cgs: 'CGS-SI relation, exact power of ten (SI Brochure 9th ed. §4; NIST SP811 B.8)',
  cgpm1901: '3rd CGPM (1901): standard gravity g_n = 9.80665 m/s^2, conventional exact',
  ucum: 'UCUM v2.1 §31-§44 conventional exact value',
  nist811: 'NIST SP811 App. B.8, conventional exact value',
};

// --- the table ------------------------------------------------------------------
// { p?: P-scalar (default P(R1)), offset?: rational (default 0), src: citation }
export const ATOMS = new Map(Object.entries({
  // SI base units (scale 1 by definition)
  M: { src: src.si }, KiloGM: { src: src.si }, SEC: { src: src.si }, A: { src: src.si },
  K: { src: src.si }, MOL: { src: src.si }, CD: { src: src.si },
  // SI named derived coherent units (scale 1 by definition)
  RAD: { src: src.si }, SR: { src: src.si }, HZ: { src: src.si }, N: { src: src.si },
  PA: { src: src.si }, J: { src: src.si }, W: { src: src.si }, C: { src: src.si },
  V: { src: src.si }, FARAD: { src: src.si /* NB: QUDT unit:F is the FARADAY, not the farad — see F below */ }, OHM: { src: src.si },
  S: { src: src.si /* siemens */ }, WB: { src: src.si }, T: { src: src.si }, H: { src: src.si /* henry */ },
  LM: { src: src.si }, LX: { src: src.si }, BQ: { src: src.si }, GRAY: { src: src.si },
  SV: { src: src.si }, KAT: { src: src.si },
  VA: { src: 'volt-ampere: coherent SI product unit (apparent power), scale 1 by construction' },
  VAR: { src: 'volt-ampere reactive: coherent SI product unit (reactive power), scale 1 by construction' },
  // chemistry conventions
  MOL_LB: { p: P(rMul(LB, R(1000n))), src: 'pound-mole = 453.59237 mol exact (lb/g ratio, 1959 agreement)' },
  EQ: { src: 'equivalent = 1 mol (charge-equivalent amount; UCUM eq), conventional' },
  // counting seed for compounds (NUM itself is a CountingUnit and stays excluded as a record)
  NUM: { src: 'pure number = 1 (dimensionless), definition; seeds number-density/frequency compounds' },
  // faraday: exact since SI 2019 (e and N_A both exact)
  F: { p: P(rMul(d('1.602176634e-19'), d('6.02214076e23'))), src: 'faraday = e x N_A = 96485.33212331001840 C exact (SI Brochure 9th ed. Table 1: e, N_A exact since 2019)' },
  // affine temperature scales
  DEG_C: { offset: d('273.15'), src: 'SI Brochure 9th ed. §2.3.1: t/degC = T/K - 273.15, exact' },
  DEG_F: { p: P(DEGF_K), offset: rMul(d('459.67'), DEGF_K), src: 'NIST SP811 B.8: T/K = (t/degF + 459.67)/1.8, exact convention' },
  DEG_R: { p: P(DEGF_K), src: 'NIST SP811 B.8: Rankine, T/K = (T/degR)/1.8, exact convention' },
  // SI-accepted non-SI (Table 8) + gram
  GM: { p: P(d('0.001')), src: src.si },
  MIN: { p: P(R(60n)), src: src.siTable8 },
  HR: { p: P(R(3600n)), src: src.siTable8 },
  DAY: { p: P(R(86400n)), src: src.siTable8 },
  WK: { p: P(R(604800n)), src: 'week = 7 d (calendar convention; UCUM wk)' },
  YR: { p: P(JYR), src: 'Julian year = 365.25 d (IAU convention; UCUM annum a = a_j)' },
  YR_TROPICAL: { p: P(d('31556925.216')), src: 'tropical year = 365.24219 d, UCUM a_t conventional exact' },
  MO: { p: P(d('2551442.976')), src: 'mean synodic month = 29.53059 d, UCUM mo_s conventional exact' },
  DEG: { p: P(R(1n, 180n), 1), src: 'SI Brochure 9th ed. Table 8: 1 deg = (pi/180) rad, exact (pi symbolic)' },
  ARCMIN: { p: P(R(1n, 10800n), 1), src: 'SI Brochure 9th ed. Table 8: (pi/10800) rad' },
  ARCSEC: { p: P(R(1n, 648000n), 1), src: 'SI Brochure 9th ed. Table 8: (pi/648000) rad' },
  HA: { p: P(R(10000n)), src: src.siTable8 },
  L: { p: P(d('0.001')), src: src.siTable8 },
  TONNE: { p: P(R(1000n)), src: src.siTable8 },
  AU: { p: P(AU), src: 'IAU 2012 Resolution B2: 1 au = 149 597 870 700 m, exact' },
  EV: { p: P(d('1.602176634e-19')), src: 'SI Brochure 9th ed. Table 1/8: e exact since 2019, so 1 eV = 1.602176634e-19 J exact' },
  // other angle conventions
  GON: { p: P(R(1n, 200n), 1), src: 'gon/grad = (pi/200) rad, definition (ISO 80000-3)' },
  GRAD: { p: P(R(1n, 200n), 1), src: 'gon/grad = (pi/200) rad, definition (ISO 80000-3)' },
  REV: { p: P(R(2n), 1), src: 'revolution = 2 pi rad, definition' },
  MIL: { p: P(R(1n, 3200n), 1), src: 'NATO angular mil: 6400 mil = 2 pi rad, definition' },
  // CGS mechanical (exact powers of ten)
  DYN: { p: P(d('1e-5')), src: src.cgs }, ERG: { p: P(d('1e-7')), src: src.cgs },
  GALILEO: { p: P(d('0.01')), src: src.cgs }, POISE: { p: P(d('0.1')), src: src.cgs },
  ST: { p: P(d('1e-4')), src: src.cgs /* stokes */ }, KY: { p: P(R(100n)), src: src.cgs /* kayser 1/cm */ },
  // CGS electromagnetic (Gaussian/EMU; exact, some with symbolic pi)
  Gs: { p: P(d('1e-4')), src: src.cgs /* gauss */ }, MX: { p: P(d('1e-8')), src: src.cgs /* maxwell */ },
  OERSTED: { p: P(R(250n), -1), src: 'CGS-EMU: 1 Oe = (1000/(4 pi)) A/m, exact with symbolic pi (NIST SP811 B.8)' },
  GI: { p: P(R(5n, 2n), -1), src: 'CGS-EMU gilbert: (10/(4 pi)) A, exact with symbolic pi' },
  BIOT: { p: P(R(10n)), src: 'CGS-EMU biot (abampere) = 10 A, exact' },
  // CGS photometric
  STILB: { p: P(R(10000n)), src: src.cgs }, PHOT: { p: P(R(10000n)), src: src.cgs },
  LA: { p: P(R(10000n), -1), src: 'lambert = (1e4/pi) cd/m^2, definition (NIST SP811 B.8)' },
  // lengths
  ANGSTROM: { p: P(d('1e-10')), src: src.nist811 },
  MicroM6: undefined, // never an atom; guard against accidental additions
  IN: { p: P(IN), src: src.yp1959 }, FT: { p: P(FT), src: src.yp1959 }, YD: { p: P(YD), src: src.yp1959 },
  MI: { p: P(MI), src: src.yp1959 }, FATH: { p: P(rMul(FT, R(6n))), src: 'fathom = 6 ft (international), UCUM fth_i' },
  ROD: { p: P(rMul(FT, R(33n, 2n))), src: 'rod = 16.5 ft (international foot)' },
  CH: { p: P(rMul(FT, R(66n))), src: 'chain = 66 ft (international foot)' },
  FUR: { p: P(rMul(FT, R(660n))), src: 'furlong = 660 ft (international foot)' },
  FT_US: { p: P(FT_US), src: 'US survey foot = 1200/3937 m (NIST HB44; deprecated 2023 but exact)' },
  MI_US: { p: P(rMul(FT_US, R(5280n))), src: 'US survey mile = 5280 survey ft' },
  MI_N: { p: P(R(1852n)), src: 'international nautical mile = 1852 m (1st Int. Extraordinary Hydrographic Conf. 1929)' },
  KN: { p: P(R(1852n, 3600n)), src: 'knot = 1 nmi/h = 1852/3600 m/s, exact' },
  PT: { p: P(rMul(d('0.013837'), IN)), src: "printer's point = 0.013837 in exactly (UCUM [pnt] conventional; matches QUDT's intent per its ucumCode/value)" },
  MilliIN: { p: P(rMul(IN, d('0.001'))), src: 'mil/thou = 1e-3 in (follows from 1959 inch)' },
  LY: { p: P(LIGHTYEAR), src: 'light year = c x Julian year = 9 460 730 472 580 800 m, exact (c exact SI 2019; IAU)' },
  PARSEC: { p: P(rMul(R(648000n), AU), -1), src: 'parsec = (648000/pi) au, IAU 2015 Resolution B2, exact with symbolic pi' },
  // areas
  AC: { p: P(rMul(R(43560n), rPow(FT, 2))), src: 'international acre = 43560 ft^2 = 4046.8564224 m^2 (1959 foot)' },
  BARN: { p: P(d('1e-28')), src: 'barn = 1e-28 m^2, definition (SI Brochure 9th ed. Table 8, 8th ed.)' },
  // masses
  TON_Metric: { p: P(R(1000n)), src: 'metric ton = 1000 kg (= tonne, SI Brochure Table 8)' },
  LB: { p: P(LB), src: src.yp1959 },
  OZ: { p: P(rDiv(LB, R(16n))), src: 'avoirdupois ounce = lb/16 (1959 agreement)' },
  GRAIN: { p: P(rDiv(LB, R(7000n))), src: 'grain = lb/7000 = 64.79891 mg exact (1959 agreement)' },
  DWT: { p: P(rMul(rDiv(LB, R(7000n)), R(24n))), src: 'pennyweight = 24 grains' },
  OZ_TROY: { p: P(rMul(rDiv(LB, R(7000n)), R(480n))), src: 'troy ounce = 480 grains = 31.1034768 g exact' },
  LB_T: { p: P(rMul(rDiv(LB, R(7000n)), R(5760n))), src: 'troy pound = 5760 grains' },
  CARAT: { p: P(d('0.0002')), src: 'metric carat = 200 mg (4th CGPM 1907)' },
  TON_SHORT: { p: P(rMul(LB, R(2000n))), src: 'short ton = 2000 lb (US customary)' },
  TON_LONG: { p: P(rMul(LB, R(2240n))), src: 'long ton = 2240 lb (imperial)' },
  TON_UK: { p: P(rMul(LB, R(2240n))), src: 'UK (long) ton = 2240 lb' },
  TON_US: { p: P(rMul(LB, R(2000n))), src: 'US (short) ton = 2000 lb' },
  SLUG: { p: P(rDiv(LBF, FT)), src: 'slug = lbf s^2/ft (exact from 1959 lb, g_n, 1959 ft)' },
  // force
  LB_F: { p: P(LBF), src: 'pound-force = lb x g_n (1959 agreement + 3rd CGPM 1901), exact' },
  KIP: { p: P(rMul(LBF, R(1000n))), src: 'kip = 1000 lbf' },
  KIP_F: { p: P(rMul(LBF, R(1000n))), src: 'kip(-force) = 1000 lbf exact (QUDT factor list [LB_F^1] is dimensional only — see discrepancy report)' },
  KiloGM_F: { p: P(G_N), src: 'kilogram-force = g_n N (3rd CGPM 1901), exact' },
  GM_F: { p: P(rMul(G_N, d('0.001'))), src: 'gram-force = g_n x 1e-3 N' },
  POND: { p: P(rMul(G_N, d('0.001'))), src: 'pond = gram-force = g_n x 1e-3 N exact (QUDT factor list [N^1] is dimensional only)' },
  PDL: { p: P(rMul(LB, FT)), src: 'poundal = lb ft/s^2 = 0.138254954376 N exact' },
  OZ_F: { p: P(rDiv(LBF, R(16n))), src: 'ounce-force = lbf/16' },
  // acceleration
  G: { p: P(G_N), src: src.cgpm1901 },
  // pressure
  BAR: { p: P(R(100000n)), src: src.siTable8 },
  ATM: { p: P(R(101325n)), src: 'standard atmosphere = 101325 Pa, exact (10th CGPM 1954)' },
  TORR: { p: P(R(101325n, 760n)), src: 'torr = atm/760, exact (definition)' },
  MilliM_HG: { p: P(MMHG), src: 'conventional mmHg = 13595.1 kg/m^3 x g_n x 1 mm = 133.322387415 Pa (BIPM SI Brochure 8th ed. Table 9)' },
  PSI: { p: P(rDiv(LBF, rPow(IN, 2))), src: 'psi = lbf/in^2, exact from 1959+1901 conventions' },
  // energy
  CAL_TH: { p: P(CAL_TH), src: 'thermochemical calorie = 4.184 J exact (NIST SP811 B.8)' },
  CAL_IT: { p: P(CAL_IT), src: 'IT calorie = 4.1868 J exact (5th Int. Conf. Properties of Steam 1956; ISO 80000-5)' },
  KiloCAL: { p: P(rMul(CAL_TH, R(1000n))), src: 'kilocalorie (thermochemical) = 4184 J exact — QUDT states 4184.0, i.e. treats kcal as kcal_th' },
  BTU_IT: { p: P(BTU_IT), src: 'IT Btu = cal_IT x (lb/g) x (5/9) = 1055.05585262 J exact (ISO 80000-5)' },
  BTU_TH: { p: P(BTU_TH), src: 'thermochemical Btu = cal_th x (lb/g) x (5/9), exact fraction' },
  THM_US: { p: P(R(105480400n)), src: 'US therm = 1.054804e8 J exactly (US legal definition; NIST SP811 B.8)' },
  THM_EEC: { p: P(rMul(BTU_IT, R(100000n))), src: 'EC therm = 1e5 Btu_IT = 105505585.262 J exact (QUDT ucumCode 100000.[Btu_IT])' },
  // power
  HP: { p: P(rMul(rMul(R(550n), FT), LBF)), src: 'mechanical horsepower = 550 ft lbf/s = 745.69987158227022 W exact' },
  HP_Electric: { p: P(R(746n)), src: 'electric horsepower = 746 W, definition' },
  HP_Metric: { p: P(rMul(R(75n), G_N)), src: 'metric horsepower = 75 kgf m/s = 735.49875 W exact' },
  // radiometry / radioactivity (conventional exacts)
  CI: { p: P(d('3.7e10')), src: 'curie = 3.7e10 Bq, definition (NIST SP811 B.8)' },
  R: { p: P(d('2.58e-4')), src: 'roentgen = 2.58e-4 C/kg, definition (NIST SP811 B.8)' },
  RAD_R: { p: P(d('0.01')), src: 'rad (absorbed dose) = 0.01 Gy, definition' },
  REM: { p: P(d('0.01')), src: 'rem = 0.01 Sv, definition' },
  // photometry
  FC: { p: P(rDiv(R1, rPow(FT, 2))), src: 'footcandle = lm/ft^2, exact from 1959 foot' },
  FT_LA: { p: P(rDiv(R1, rPow(FT, 2)), -1), src: 'footlambert = (1/pi) cd/ft^2, exact with symbolic pi' },
  LA_FT: { p: P(rDiv(R1, rPow(FT, 2)), -1), src: 'footlambert = (1/pi) cd/ft^2, exact with symbolic pi (QUDT factor list [CD^1 FT^-2] omits the 1/pi)' },
  // volumes
  GAL_US: { p: P(GAL_US), src: 'US gallon = 231 in^3 (NIST HB44 App. C), exact' },
  QT_US: { p: P(rDiv(GAL_US, R(4n))), src: 'US quart = gal/4' },
  PINT_US: { p: P(rDiv(GAL_US, R(8n))), src: 'US pint = gal/8' },
  CUP_US: { p: P(rDiv(GAL_US, R(16n))), src: 'US cup = gal/16' },
  OZ_VOL_US: { p: P(rDiv(GAL_US, R(128n))), src: 'US fluid ounce = gal/128' },
  GAL_UK: { p: P(GAL_UK), src: 'imperial gallon = 4.54609 L exact (UK Weights and Measures Act 1985)' },
  QT_UK: { p: P(rDiv(GAL_UK, R(4n))), src: 'imperial quart = gal_uk/4' },
  PINT_UK: { p: P(rDiv(GAL_UK, R(8n))), src: 'imperial pint = gal_uk/8' },
  OZ_VOL_UK: { p: P(rDiv(GAL_UK, R(160n))), src: 'imperial fluid ounce = gal_uk/160' },
  BU_US: { p: P(rMul(d('2150.42'), rPow(IN, 3))), src: 'US bushel = 2150.42 in^3 (Winchester bushel, US statute), exact' },
  BBL: { p: P(rMul(R(42n), GAL_US)), src: 'petroleum barrel = 42 US gal, exact (US statute)' },
  BBL_US_PET: { p: P(rMul(R(42n), GAL_US)), src: 'petroleum barrel = 42 US gal, exact (US statute)' },
  BBL_UK_PET: { p: P(rMul(R(35n), GAL_UK)), src: 'UK petroleum barrel = 35 imperial gal = 0.15911315 m^3 exact' },
  CORD: { p: P(rMul(R(128n), rPow(FT, 3))), src: 'cord = 128 ft^3, definition' },
  BU_UK: { p: P(rMul(R(8n), GAL_UK)), src: 'imperial bushel = 8 imperial gal (UK Weights and Measures Act)' },
  PK_UK: { p: P(rMul(R(2n), GAL_UK)), src: 'imperial peck = 2 imperial gal' },
  GI_UK: { p: P(rDiv(GAL_UK, R(32n))), src: 'imperial gill = gal_uk/32' },
  GI_US: { p: P(rDiv(GAL_US, R(32n))), src: 'US gill = gal_us/32' },
  BU_US_DRY: { p: P(rMul(d('2150.42'), rPow(IN, 3))), src: 'US (dry) bushel = 2150.42 in^3 (Winchester bushel, US statute), exact' },
  GAL_US_DRY: { p: P(rMul(d('268.8025'), rPow(IN, 3))), src: 'US dry gallon = bushel/8 = 268.8025 in^3 exact' },
  PK_US_DRY: { p: P(rMul(d('537.605'), rPow(IN, 3))), src: 'US peck = bushel/4 = 537.605 in^3 exact' },
  QT_US_DRY: { p: P(rMul(d('67.200625'), rPow(IN, 3))), src: 'US dry quart = bushel/32 = 67.200625 in^3 exact' },
  PT_US_DRY: { p: P(rMul(d('33.6003125'), rPow(IN, 3))), src: 'US dry pint = bushel/64 = 33.6003125 in^3 exact' },
  // dimensionless ratios (exact by definition)
  UNITLESS: { src: 'dimensionless unity' },
  PERCENT: { p: P(d('0.01')), src: 'percent = 1/100, definition' },
  PPM: { p: P(d('1e-6')), src: 'part per million, definition' },
  PPB: { p: P(d('1e-9')), src: 'part per billion (short scale), definition' },
  PPTH: { p: P(d('0.001')), src: 'part per thousand, definition' },
  PPTR: { p: P(d('1e-12')), src: 'part per trillion (short scale), definition' },
  PERMILLE: { p: P(d('0.001')), src: 'per mille = 1/1000, definition' },
  PPTM: { p: P(d('1e-7')), src: 'part per ten million, definition' },
  PPT: { p: P(d('1e-12')), src: 'part per trillion (short scale), definition (QUDT ucum [ppt])' },
  PPT_VOL: { p: P(d('1e-12')), src: 'part per trillion by volume, definition' },
  PPQ: { p: P(d('1e-15')), src: 'part per quadrillion (short scale), definition' },
  SUSCEPTIBILITY_ELEC: { src: 'electric susceptibility: dimensionless unity, definition' },
  SUSCEPTIBILITY_MAG: { src: 'magnetic susceptibility: dimensionless unity, definition' },
  // aliases of SI/accepted units under other QUDT names
  GAUSS: { p: P(d('1e-4')), src: src.cgs },
  MHO: { src: 'mho = siemens, scale 1 (historic name)' },
  AT: { src: 'ampere-turn = 1 A (magnetomotive force), definition' },
  MI_UK: { p: P(MI), src: 'imperial mile = international mile = 1609.344 m (1959 agreement)' },
  LB_M: { p: P(LB), src: src.yp1959 },
  MIN_Angle: { p: P(R(1n, 10800n), 1), src: 'SI Brochure 9th ed. Table 8: arcminute = (pi/10800) rad' },
  SEC_Angle: { p: P(R(1n, 648000n), 1), src: 'SI Brochure 9th ed. Table 8: arcsecond = (pi/648000) rad' },
  GAL_IMP: { p: P(GAL_UK), src: 'imperial gallon = 4.54609 L exact (UK Weights and Measures Act 1985)' },
  PINT: { p: P(rDiv(GAL_UK, R(8n))), src: 'imperial pint = gal_uk/8 (QUDT ucum [pt_br])' },
  ARE: { p: P(R(100n)), src: 'are = 100 m^2, definition' },
  STR: { p: P(R1), src: 'stere = 1 m^3, definition' },
  BAR_A: { p: P(R(100000n)), src: 'bar (absolute pressure reading) = 1e5 Pa' },
  DeciBAR: { p: P(R(10000n)), src: 'decibar = 1e4 Pa (bar = 1e5 Pa, SI Brochure Table 8)' },
  YR_Common: { p: P(R(31536000n)), src: 'common calendar year = 365 d' },
  YR_Metrology: { p: P(JYR), src: 'metrology/Julian year = 365.25 d' },
  SH: { p: P(d('1e-8')), src: 'shake = 10 ns, definition' },
  R_man: { p: P(d('0.01')), src: 'rem (roentgen equivalent man) = 0.01 Sv, definition' },
  PicoCI: { p: P(d('0.037')), src: 'picocurie = 1e-12 x 3.7e10 Bq = 0.037 Bq exact' },
  // CGS-ESU (statunits) via exact c — Gaussian conventions, all exact
  C_Stat: { p: P(STATC), src: 'statcoulomb = (0.1/c) C exact (CGS-ESU; c exact since 1983/2019)' },
  A_Stat: { p: P(STATC), src: 'statampere = statcoulomb/s = (0.1/c) A exact (CGS-ESU)' },
  V_Stat: { p: P(rMul(C_LIGHT, d('1e-6'))), src: 'statvolt = c x 1e-6 V = 299.792458 V exact (CGS-ESU)' },
  H_Stat: { p: P(rMul(rPow(C_LIGHT, 2), d('1e-5'))), src: 'stathenry = c^2 x 1e-5 H exact (CGS-ESU)' },
  S_Stat: { p: P(rDiv(d('1e5'), rPow(C_LIGHT, 2))), src: 'statsiemens = 1e5/c^2 S exact (CGS-ESU)' },
  // CGS-EMU (abunits) — exact powers of ten
  A_Ab: { p: P(R(10n)), src: 'abampere = 10 A exact (CGS-EMU)' },
  C_Ab: { p: P(R(10n)), src: 'abcoulomb = 10 C exact (CGS-EMU)' },
  V_Ab: { p: P(d('1e-8')), src: 'abvolt = 1e-8 V exact (CGS-EMU)' },
  FARAD_Ab: { p: P(d('1e9')), src: 'abfarad = 1e9 F exact (CGS-EMU)' },
  S_Ab: { p: P(d('1e9')), src: 'absiemens = 1e9 S exact (CGS-EMU)' },
  T_Ab: { p: P(d('1e-4')), src: 'abtesla = gauss = 1e-4 T exact (CGS-EMU)' },
  UnitPole: { p: P(d('4e-8'), 1), src: 'unit magnetic pole = 4 pi x 1e-8 Wb exact (CGS-EMU, symbolic pi)' },
  MIL_Circ: { p: P(rMul(R(1n, 4n), rPow(rMul(IN, d('0.001')), 2)), 1), src: 'circular mil = (pi/4) x (1e-3 in)^2 exact (symbolic pi)' },
  // more mass/force conventions
  TON: { p: P(rMul(LB, R(2000n))), src: 'short ton = 2000 lb (US customary; QUDT ucum ston_av)' },
  TON_F_US: { p: P(rMul(LBF, R(2000n))), src: 'short ton-force = 2000 lbf exact' },
  Stone_UK: { p: P(rMul(LB, R(14n))), src: 'stone = 14 lb exact' },
  Quarter_UK: { p: P(rMul(LB, R(28n))), src: 'quarter (UK mass) = 28 lb exact' },
  PFUND: { p: P(d('0.5')), src: 'German Pfund (metric) = 0.5 kg, convention' },
  ZOLL: { p: P(IN), src: 'Zoll = international inch = 0.0254 m' },
  TON_Assay: { p: P(R(7n, 240n)), src: 'assay ton (short) = (short ton / troy oz) mg = 14e6/480 mg = 7/240 kg exact' },
  TON_SHIPPING_US: { p: P(rMul(R(40n), rPow(FT, 3))), src: 'shipping/freight (measurement) ton = 40 ft^3 exact convention' },
  TON_Register: { p: P(rMul(R(100n), rPow(FT, 3))), src: 'register ton = 100 ft^3 exact (QUDT factor list [FT^3] is dimensional only)' },
  TON_SHIPPING_UK: { p: P(rMul(R(40n), rPow(FT, 3))), src: 'shipping/freight (measurement) ton = 40 ft^3 (QUDT states the 40 ft^3 value for the UK entry too; UK shipping ton is 42 ft^3 in some sources — see discrepancy report)' },
  // pressure heads (conventional densities x g_n, exact)
  ATM_T: { p: P(rMul(G_N, R(10000n))), src: 'technical atmosphere = 1 kgf/cm^2 = 98066.5 Pa exact' },
  CentiM_H2O: { p: P(rMul(rMul(R(1000n), G_N), d('0.01'))), src: 'conventional cm of water = 1000 kg/m^3 x g_n x 1 cm = 98.0665 Pa exact' },
  MilliM_H2O: { p: P(rMul(rMul(R(1000n), G_N), d('0.001'))), src: 'conventional mm of water = 9.80665 Pa exact' },
  IN_HG: { p: P(IN_HG), src: 'conventional inch of mercury = 25.4 mmHg = 3386.388640341 Pa exact' },
  IN_H2O: { p: P(rMul(rMul(R(1000n), G_N), IN)), src: 'conventional inch of water = 1000 kg/m^3 x g_n x 1 in = 249.08891 Pa exact' },
  // permeation / permeability
  DARCY: { p: P(rDiv(R1, d('1.01325e12'))), src: 'darcy = (cP cm^3/s / cm^2)/(atm/cm) = 1e-5/1.01325e7 m^2 = 9.86923266716e-13 m^2 exact (via exact atm)' },
  BREWSTER: { p: P(d('1e-12')), src: 'brewster = 1e-12 m^2/N, definition' },
  PERM_US: { p: P(rDiv(rDiv(LB, R(7000n)), rMul(rMul(R(3600n), rPow(FT, 2)), IN_HG))), src: 'US perm = grain/(h ft^2 inHg), exact from grain/1959 ft/conventional inHg = 5.72135e-11 kg/(Pa s m^2)' },
  // energy conventions (UCUM conventional exacts + composites)
  CAL_15DEG_C: { p: P(d('4.18580')), src: '15 degC calorie = 4.18580 J (UCUM cal_[15] conventional exact)' },
  CAL_20DEG_C: { p: P(d('4.18190')), src: '20 degC calorie = 4.18190 J (UCUM cal_[20] conventional exact)' },
  CAL_MEAN: { p: P(d('4.19002')), src: 'mean calorie = 4.19002 J (UCUM cal_m conventional exact)' },
  BTU_MEAN: { p: P(d('1055.87')), src: 'mean Btu = 1055.87 J (UCUM [Btu_m] conventional exact)' },
  BTU_39DEG_F: { p: P(d('1059.67')), src: '39 degF Btu = 1059.67 J (UCUM [Btu_39] conventional exact)' },
  BTU_59DEG_F: { p: P(d('1054.80')), src: '59 degF Btu = 1054.80 J (UCUM [Btu_59] conventional exact)' },
  BTU_60DEG_F: { p: P(d('1054.68')), src: '60 degF Btu = 1054.68 J (UCUM [Btu_60] conventional exact)' },
  THERM_US: { p: P(R(105480400n)), src: 'US therm = 1.054804e8 J exactly (US legal definition; NIST SP811 B.8)' },
  THERM_EC: { p: P(rMul(BTU_IT, R(100000n))), src: 'EC therm = 1e5 Btu_IT = 105505585.262 J exact' },
  QUAD: { p: P(rMul(BTU_IT, d('1e15'))), src: 'quad = 1e15 Btu_IT exact convention' },
  TOE: { p: P(rMul(CAL_IT, d('1e10'))), src: 'tonne of oil equivalent = 1e7 kcal_IT = 4.1868e10 J exact (IEA)' },
  TonEnergy: { p: P(rMul(CAL_TH, d('1e9'))), src: 'ton (of TNT) energy = 1 Gcal_th = 4.184e9 J exact convention' },
  TON_FG: { p: P(rDiv(rMul(BTU_IT, R(12000n)), R(3600n))), src: 'ton of refrigeration = 12000 Btu_IT/h = 3516.85284206... W exact' },
  PFERDESTAERKE: { p: P(rMul(R(75n), G_N)), src: 'Pferdestaerke (metric horsepower) = 75 kgf m/s = 735.49875 W exact' },
  ENZ: { p: P(R(1n, 60000000n)), src: 'enzyme unit = 1 umol/min = 1e-6/60 mol/s exact' },
  OSM: { src: 'osmole = 1 mol of osmotically active entities, convention (QUDT states 0.0 — see discrepancy report)' },
  SpeedOfLight: { p: P(C_LIGHT), src: 'speed-of-light velocity unit = 299792458 m/s exact (SI 2019; QUDT states 0.0 — see discrepancy report)' },
  // volumes (kitchen/dry/US statute)
  TBSP: { p: P(rDiv(GAL_US, R(256n))), src: 'US tablespoon = gal_us/256 (= fl oz/2) exact' },
  TSP: { p: P(rDiv(GAL_US, R(768n))), src: 'US teaspoon = gal_us/768 exact' },
  PINT_US_DRY: { p: P(rMul(d('33.6003125'), rPow(IN, 3))), src: 'US dry pint = bushel/64 = 33.6003125 in^3 exact' },
  BBL_US_DRY: { p: P(rMul(R(7056n), rPow(IN, 3))), src: 'US dry barrel = 7056 in^3 (15 USC 234); QUDT evidently used the approximate 105-dry-quart identity — see discrepancy report' },
  STANDARD: { p: P(rMul(R(165n), rPow(FT, 3))), src: 'standard (timber) = 165 ft^3 (= 1980 board feet) exact' },
  // acoustics
  RAYL: { p: P(R(10n)), src: 'rayl (CGS) = 10 Pa s/m exact' },
  RAYL_MKS: { src: 'rayl (MKS) = 1 Pa s/m, definition' },
  RHE: { p: P(R(10n)), src: 'rhe = 1/poise = 10 1/(Pa s) exact' },
  TEX: { p: P(d('1e-6')), src: 'tex = 1 g/km = 1e-6 kg/m, definition' },
  DENIER: { p: P(R(1n, 9000000n)), src: 'denier = 1 g/9 km = 1/9e6 kg/m, definition' },
  PT_BIG: { p: P(rDiv(IN, R(72n))), src: 'big (DTP) point = 1/72 in exact' },
  PCA: { p: P(rDiv(IN, R(6n))), src: 'pica (DTP) = 1/6 in exact — QUDT states the DTP value 0.0042333 despite its [pca] (printer) ucum annotation; value followed, annotation distrusted' },
  // wave 3: remaining exactly-derivable leaves
  BBL_US: { p: P(rMul(R(42n), GAL_US)), src: 'US barrel (QUDT ucum [bbl_us]) = 42 US gal exact' },
  CHAIN: { p: P(rMul(FT, R(66n))), src: 'chain = 66 ft (international foot)' },
  CHAIN_US: { p: P(rMul(FT_US, R(66n))), src: 'US survey chain = 66 survey ft' },
  CLO: { p: P(d('0.155')), src: 'clo = 0.155 K m^2/W, definition (ISO 9920)' },
  CP: { src: 'modern candlepower = 1 cd, convention (QUDT states 1.0)' },
  CUP: { p: P(rDiv(GAL_US, R(16n))), src: 'US customary cup = gal_us/16 (QUDT ucum [cup_us])' },
  CWT_LONG: { p: P(rMul(LB, R(112n))), src: 'long hundredweight = 112 lb exact' },
  CWT_SHORT: { p: P(rMul(LB, R(100n))), src: 'short hundredweight = 100 lb exact' },
  Hundredweight_UK: { p: P(rMul(LB, R(112n))), src: 'UK hundredweight = 112 lb exact' },
  Hundredweight_US: { p: P(rMul(LB, R(100n))), src: 'US hundredweight = 100 lb exact' },
  CentiM_HG: { p: P(rMul(MMHG, R(10n))), src: 'conventional cm of mercury = 10 mmHg = 1333.22387415 Pa exact' },
  CentiM_HG_0DEG_C: { p: P(rMul(MMHG, R(10n))), src: 'cm of mercury (0 degC) = conventional cmHg (the conventional mercury density 13595.1 kg/m^3 is the 0 degC value)' },
  DEBYE: { p: P(rMul(STATC, d('1e-20'))), src: 'debye = 1e-18 statC cm = 1e-21/c C m exact (via exact c)' },
  DIOPTER: { src: 'dioptre = 1/m, scale 1, definition' },
  DRAM_UK: { p: P(rMul(rDiv(LB, R(7000n)), R(60n))), src: 'apothecaries dram ([dr_ap]) = 60 grains exact' },
  DRAM_US: { p: P(rDiv(LB, R(256n))), src: 'avoirdupois dram ([dr_av]) = lb/256 = 1.7718451953125 g exact' },
  DU: { p: P(rDiv(d('1.01325'), rMul(d('8.31446261815324'), d('273.15')))), src: 'Dobson unit = 0.01 mm ozone column at STP = (101325 x 1e-5)/(R x 273.15) mol/m^2 exact (R = k_B N_A exact since SI 2019)' },
  NCM: { p: P(rDiv(R(101325n), rMul(d('8.31446261815324'), d('273.15')))), src: 'normal cubic metre = 101325/(R x 273.15) = 44.6150334... mol exact (R exact since SI 2019; QUDT states 0.0 — see discrepancy report)' },
  NCM_1ATM_0DEG_C_NL: { p: P(rDiv(R(101325n), rMul(d('8.31446261815324'), d('273.15')))), src: 'normal cubic metre (0 degC, 1 atm) = 44.6150334... mol exact' },
  E: { p: P(d('1.602176634e-19')), src: 'elementary-charge unit = 1.602176634e-19 C exact (SI 2019)' },
  ElementaryCharge: { p: P(d('1.602176634e-19')), src: 'elementary-charge unit = 1.602176634e-19 C exact (SI 2019)' },
  ERLANG: { src: 'erlang = dimensionless traffic intensity, scale 1, definition' },
  FA: { p: P(R(4n), 1), src: 'fractional area = full sphere solid-angle factor 4 pi (QUDT states 12.5663706), symbolic pi' },
  FBM: { p: P(rMul(R(144n), rPow(IN, 3))), src: 'board foot = 144 in^3 exact' },
  FM: { p: P(d('1e-15')), src: 'fermi = 1e-15 m, definition' },
  FR: { p: P(STATC), src: 'franklin = statcoulomb = (0.1/c) C exact' },
  FRACTION: { src: 'fraction = dimensionless ratio, scale 1' },
  FT_H2O: { p: P(rMul(rMul(R(1000n), G_N), FT)), src: 'conventional foot of water = 1000 kg/m^3 x g_n x 1 ft = 2989.06692 Pa exact' },
  FT_HG: { p: P(rMul(MMHG, d('304.8'))), src: 'conventional foot of mercury = 304.8 mmHg exact' },
  GAMMA: { p: P(d('1e-9')), src: 'gamma = 1e-9 T exact (CGS)' },
  GAUGE_FR: { p: P(R(1n, 3000n)), src: 'French (Charriere) gauge = 1/3 mm exact convention' },
  GA_Charriere: { p: P(R(1n, 3000n)), src: 'Charriere gauge = 1/3 mm exact convention' },
  HP_Brake: { p: P(rMul(rMul(R(550n), FT), LBF)), src: 'brake horsepower = mechanical horsepower = 550 ft lbf/s exact' },
  H_Ab: { p: P(d('1e-9')), src: 'abhenry = 1e-9 H exact (CGS-EMU)' },
  OHM_Ab: { p: P(d('1e-9')), src: 'abohm = 1e-9 ohm exact (CGS-EMU)' },
  OHM_Stat: { p: P(rMul(rPow(C_LIGHT, 2), d('1e-5'))), src: 'statohm = c^2 x 1e-5 ohm exact (CGS-ESU)' },
  MHO_Stat: { p: P(rDiv(d('1e5'), rPow(C_LIGHT, 2))), src: 'statmho = 1e5/c^2 S exact (CGS-ESU)' },
  FARAD_Stat: { p: P(rDiv(d('1e5'), rPow(C_LIGHT, 2))), src: 'statfarad = 1e5/c^2 F exact (CGS-ESU)' },
  KiloCAL_Mean: { p: P(d('4190.02')), src: 'mean kilocalorie = 1000 x 4.19002 J (UCUM cal_m conventional exact)' },
  KiloPA_A: { p: P(R(1000n)), src: 'kilopascal (absolute reading) = 1000 Pa' },
  LANGLEY: { p: P(rMul(CAL_TH, R(10000n))), src: 'langley = cal_th/cm^2 = 41840 J/m^2 exact' },
  MIL_Angle: { p: P(R(1n, 3200n), 1), src: 'NATO angular mil = 2 pi/6400 rad, symbolic pi' },
  MIL_Length: { p: P(rMul(IN, d('0.001'))), src: 'mil (thou) = 1e-3 in exact' },
  MilLength: { p: P(rMul(IN, d('0.001'))), src: 'mil (thou) = 1e-3 in exact' },
  MOMME_Pearl: { p: P(d('0.00375')), src: 'momme = 3.75 g exact (Japanese pearl trade convention; QUDT states 3.750, a 1000x error — see discrepancy report)' },
  MO_MeanGREGORIAN: { p: P(R(2629746n)), src: 'mean Gregorian month = 365.2425 d / 12 = 2629746 s exact (calendar arithmetic)' },
  MO_MeanJulian: { p: P(R(2629800n)), src: 'mean Julian month = 365.25 d / 12 = 2629800 s exact' },
  MO_Synodic: { p: P(d('2551442.976')), src: 'mean synodic month = 29.53059 d, UCUM mo_s conventional exact' },
  M_H2O: { p: P(rMul(R(1000n), G_N)), src: 'conventional metre of water = 1000 kg/m^3 x g_n x 1 m = 9806.65 Pa exact' },
  MilliM_HGA: { p: P(MMHG), src: 'mmHg (absolute reading) = conventional mmHg = 133.322387415 Pa exact' },
  OKTA: { p: P(R(1n, 8n)), src: 'okta = 1/8 of sky cover, definition (QUDT states 0.0 — see discrepancy report)' },
  OZ_M: { p: P(rDiv(LB, R(16n))), src: 'avoirdupois ounce = lb/16 (1959 agreement)' },
  PENNYWEIGHT: { p: P(rMul(rDiv(LB, R(7000n)), R(24n))), src: 'pennyweight = 24 grains exact' },
  PERCENT_RH: { p: P(d('0.01')), src: 'percent relative humidity = 1/100 (dimensionless ratio)' },
}).filter(([, v]) => v !== undefined).map(([k, v]) => [k, { p: v.p ?? P(R1), offset: v.offset ?? R0, src: v.src }]));

/**
 * Units whose QUDT-normal-form factor is TRANSCENDENTAL and not pi-shaped:
 * QUDT normalizes information units to nats, so bit carries conversion factor
 * ln 2 = 0.6931... — not representable in the affine-rational (pi-tagged)
 * normal form. Excluded pending a symbolic-log record extension (follow-up
 * bead); compounds built on these leaves inherit the exclusion.
 */
export const TRANSCENDENTAL = new Map(Object.entries({
  BIT: 'QUDT normalizes information to nats: stated conversionMultiplier ln 2 = 0.693147...; a bit-coherent normal form would be exact but disagrees with QUDT wholesale — needs its own design decision, filed as follow-up',
  SHANNON: 'information unit (= 1 bit); QUDT nat normal form carries ln 2 — excluded with the bit family',
  NAT: 'information unit; excluded with the bit family pending the information-units design decision',
  HART: 'hartley (= log2(10) bit); QUDT nat normal form carries ln 10 — excluded with the bit family',
  BAN: 'ban (= hartley); QUDT nat normal form carries ln 10 — excluded with the bit family',
}));

/**
 * Curated exclusions: arbitrary, ill-defined, or non-affine units where no
 * exact affine map to coherent SI exists even in principle (or QUDT's own
 * modelling is internally inconsistent — see qudt-discrepancies.md).
 */
export const NONAFFINE_OR_ARBITRARY = new Map(Object.entries({
  IU: 'international unit: arbitrary biological activity, substance-dependent; no fixed SI value exists (QUDT states 0.0)',
  FLOPS: 'floating-point operations per second: counting-family rate (operation is a count, not an SI quantity)',
  BAUD: 'baud: symbols per second — counting-family rate',
  RPK: 'reads per kilobase: bioinformatics counting-family ratio',
  BFT: 'Beaufort number: empirical nonlinear wind scale — not an affine map',
  RichterMagnitude: 'Richter magnitude: logarithmic empirical scale — not an affine map',
  PSU: 'practical salinity unit: empirical conductivity-ratio scale — not an affine map',
  PHON: 'phon: psychoacoustic loudness level (logarithmic, frequency-weighted) — not an affine map',
  SON: 'sone: psychoacoustic loudness (power-law of phon) — not an affine map',
  AWG: 'American wire gauge: discrete inverse-logarithmic gauge scale — not an affine map',
  SPF: 'sun protection factor: empirical biological ratio — not a fixed SI map',
  PIXEL_AREA: 'pixel area: device-dependent, no fixed SI value (QUDT states 0.0)',
  SPIN_QUANTUM_NUMBER: 'spin quantum number: a pure quantum label; QUDT states 0.0',
  PERMEABILITY_EM_REL: 'QUDT models this dimensionless susceptibility-like unit with ucumCode [mu_0] but multiplier 1.0 — internally inconsistent; see discrepancy report',
  SCF: 'standard cubic foot (gas amount): depends on a declared reference state; QUDT gives no consistent state (see SCM entries)',
  SCM: 'standard cubic metre (gas amount): QUDT states 42.3105 mol, which matches ~15 degC, while its 0 degC-labelled variant states the same number — internally inconsistent',
  SCM_1ATM_0DEG_C: 'labelled 0 degC but states the ~15 degC molar value 42.3105 — internally inconsistent with its own label (ideal gas at 0 degC, 1 atm is 44.615 mol/m^3)',
  SCM_1ATM_15DEG_C_ISO: 'QUDT states multiplier 0.0',
  SCM_1ATM_15DEG_C_NL: 'QUDT states multiplier 0.0',
  PERM_Metric: 'metric perm: definitions vary across sources (QUDT states 1e-12 kg/(Pa s m^2) without a resolvable convention); left uncurated',
  DEGREE_API: 'degree API: reciprocal-density scale (141.5/SG - 131.5) — not an affine map',
  DEGREE_BAUME: 'degree Baume: reciprocal-density scale — not an affine map',
  DEGREE_BAUME_US_HEAVY: 'degree Baume (US heavy): reciprocal-density scale — not an affine map',
  DEGREE_BAUME_US_LIGHT: 'degree Baume (US light): reciprocal-density scale — not an affine map',
  DEGREE_BALLING: 'degree Balling: empirical sugar-content density scale — not an affine map',
  DEGREE_BRIX: 'degree Brix: empirical sugar-content density scale — not an affine map',
  DEGREE_OECHSLE: 'degree Oechsle: empirical must-density scale — not an affine map',
  DEGREE_PLATO: 'degree Plato: empirical extract-density scale — not an affine map',
  DEGREE_TWADDELL: 'degree Twaddell: affine in specific gravity, not in any SI quantity — not an affine SI map',
  DEG_C_GROWING_CEREAL: 'growing-degree index: contextual agronomic accumulation, not a fixed affine SI map',
  MACH: 'Mach number: ratio to local sound speed (state-dependent) — not a fixed affine map',
  MESH: 'mesh count: sieve grading scale — not an affine SI map',
  NTU: 'nephelometric turbidity unit: instrument-defined arbitrary scale',
  GR: 'grade: QUDT states 0.0 with dimensionless vector; no resolvable definition',
  MOHM: 'mohm (mechanical mobile ohm): QUDT states 1000.0 s/kg; no primary convention found to derive it — left uncurated',
  MOMME_Textile: 'textile momme: QUDT states 4.340 g with a pure-mass dimension — 4.34 is the silk AREAL-density constant (g/m^2), while momme as a mass is 3.75 g; definition unresolvable from the source — see discrepancy report',
  HP_Boiler: 'boiler horsepower: the common convention (33475 Btu_IT/h) computes to 9810.554 W, QUDT states 9809.5 W; no primary source resolves the difference — left uncurated (see discrepancy report)',
  HP_H2O: 'water/hydraulic horsepower: QUDT states 746.043 W; no primary convention found — left uncurated',
  KiloINDIV: 'thousand individuals: counting-family',
  MegaINDIV: 'million individuals: counting-family',
  PH: 'pH: negative decadic logarithm of activity — log-scale, named out of scope in docs/design-physics-sector.md §4.3',
  DeciB_A: 'A-weighted decibel: logarithmic (and frequency-weighted) — log-scale family',
  DeciB_C: 'C-weighted decibel: logarithmic — log-scale family',
  DeciB_ISO: 'ISO-weighted decibel: logarithmic — log-scale family',
  DeciB_M: 'dBm: logarithmic (referenced to 1 mW) — log-scale family',
  DeciB_Z: 'Z-weighted decibel: logarithmic — log-scale family',
  'N-M-PER-W0dot5': 'newton metre per SQUARE ROOT watt: true dimension is fractional (L^1 M^(1/2) T^(-1/2)); QUDT stamps the integer vector L1 and factor exponent -0.5 — internally inconsistent, see discrepancy report',
}));

/**
 * Units whose SI factor is a MEASURED quantity — world-layer facts under the
 * kernel/world boundary (docs/design-physics-sector.md §4.4). Excluded, never
 * approximated. Keyed by QUDT local name; value = why it is empirical.
 */
export const EMPIRICAL = new Map(Object.entries({
  AMU: 'atomic mass constant: CODATA measured (QUDT states the 2006 CODATA value 1.66053878283e-27 kg; current CODATA 2022 is 1.66053906892e-27 kg)',
  U: 'atomic mass constant (dalton alias): CODATA measured',
  DA: 'dalton: CODATA measured',
  KiloDA: 'kilodalton: CODATA measured base',
  MegaDA: 'megadalton: CODATA measured base',
  MilliDA: 'millidalton: CODATA measured base',
  SolarMass: 'solar mass: astronomical measurement (G M_sun known far better than either factor, but kg value is measured)',
  YR_Sidereal: 'sidereal year: astronomical measurement, epoch-dependent',
  CD_IT: 'historic international candle: empirical photometric standard (QUDT states 0.920 cd, which is the Hefner-candle region; the international candle was ~1.02 cd — see discrepancy report)',
  HK: 'Hefner candle: empirical historic photometric standard (~0.92 cd, measured)',
  E_h: 'hartree energy: CODATA measured (atomic-unit system)',
  EarthMass: 'Earth mass: astronomical measurement',
  LunarMass: 'lunar mass: astronomical measurement',
  PERMITTIVITY_REL: 'vacuum permittivity as a unit: measured since the 2019 SI (no longer exactly 1/(mu_0 c^2) with exact mu_0)',
  PERMEABILITY_REL: 'vacuum permeability as a unit: measured since the 2019 SI (QUDT still states the pre-2019 exact 4 pi x 1e-7 — see discrepancy report)',
}));
/** Local-name patterns treated as EMPIRICAL (natural-unit systems built on measured constants). */
export const EMPIRICAL_PATTERNS = [
  { re: /^Planck/, why: 'Planck-unit system: built on measured G (CODATA), world-layer' },
  { re: /_Sidereal$/, why: 'sidereal time unit: astronomical measurement, epoch-dependent' },
  { re: /(_4DEG_C|_39dot2DEG_F|_60DEG_F|_32DEG_F)$/, why: 'temperature-qualified liquid-column unit: depends on measured density at that temperature (only the CONVENTIONAL columns are exact)' },
];

/** SI decimal prefixes (exact powers of ten) + IEC binary prefixes (exact
 *  powers of two). Source: SI Brochure 9th ed. Table 7 (incl. 2022 CGPM
 *  additions ronna/quetta); IEC 80000-13 for binary. Keyed by QUDT
 *  prefix-IRI local name. */
export const PREFIX_EXACT = new Map(Object.entries({
  Quetta: 30, Ronna: 27, Yotta: 24, Zetta: 21, Exa: 18, Peta: 15, Tera: 12, Giga: 9, Mega: 6,
  Kilo: 3, Hecto: 2, Deca: 1, Deka: 1, Deci: -1, Centi: -2, Milli: -3, Micro: -6, Nano: -9,
  Pico: -12, Femto: -15, Atto: -18, Zepto: -21, Yocto: -24, Ronto: -27, Quecto: -30,
}).map(([k, e]) => [k, rPow(R(10n), e)]));
for (const [k, e] of Object.entries({ Kibi: 10, Mebi: 20, Gibi: 30, Tebi: 40, Pebi: 50, Exbi: 60, Zebi: 70, Yobi: 80 })) {
  PREFIX_EXACT.set(k, rPow(R(2n), e));
}
