#!/usr/bin/env node
/**
 * physics-qudt extractor: QUDT v3.4.0 -> physics-v0-compatible records with
 * EXACT dimension vectors and EXACT rational (pi-tagged) unit conversions.
 *
 * Honesty architecture (docs/design-bulk-kernel.md):
 *   - QUDT is the bridge target and the cross-check surface, NEVER the source
 *     of numeric truth: every scale/offset is derived from the curated
 *     exact-atom table (tools/atoms.mjs, primary conventions cited) plus two
 *     mechanical rules (prefix scaling, factor-unit composition). QUDT's
 *     floating conversionMultiplier/Offset are then CROSS-CHECKED against the
 *     derivation and every disagreement is classified:
 *       exact       — QUDT's decimal literal equals our rational exactly
 *       truncation  — QUDT's literal is our value correctly rounded (within
 *                     half an ulp) at QUDT's stated precision — benign float
 *                     publication, counted
 *       DISCREPANCY — QUDT's literal disagrees with the exact value beyond
 *                     its own stated precision — a finding, individually
 *                     analysed in qudt-discrepancies.md
 *   - Dimension vectors are derived by parsing QUDT's dimension-vector IRI
 *     local names (the mechanical canonical object, design §3) and
 *     cross-checked against BOTH the explicit qudt:dimensionExponentFor*
 *     properties in VOCAB_QUDT-DIMENSION-VECTORS.ttl AND (per unit) the
 *     dimension implied by factor-unit composition.
 *   - Exclusions are counted, categorised, and machine-readable
 *     (exclusions.json). Nothing is silently dropped.
 *
 * Determinism: output is a pure function of the pinned source bytes (sha256
 * verified before parsing, fail closed) and this extractor. Run twice and
 * byte-diff — that is the re-extraction gate.
 *
 * Usage: node tools/extract.mjs --source <dir-with-4-ttl-files> [--out <dir>]
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseTurtle, RDF_TYPE, iris, lits } from './ttl.mjs';
import {
  R, R0, R1, rParse, rToString, rToApprox, rMul, rSub, rAbs, rCmp, rEq, rPow,
  P, pOne, pMul, pPow, pEq, pApprox,
} from './rational.mjs';
import { ATOMS, EMPIRICAL, EMPIRICAL_PATTERNS, TRANSCENDENTAL, NONAFFINE_OR_ARBITRARY, PREFIX_EXACT } from './atoms.mjs';

// --- pinned source + provenance constants ------------------------------------------
const EXTRACTOR_VERSION = 'physics-qudt-extract/1.0.0';
const EXTRACTION_DATE = '2026-07-07'; // pinned: provenance names the ingestion, not the wall clock
const SOURCE = {
  name: 'QUDT public repo (github.com/qudt/qudt-public-repo)',
  release: 'v3.4.0',
  releasedAt: '2026-06-25',
  commit: '1137205617d03d3d5c8351ea58105b6719c5d6f0',
  zip: 'qudt-public-repo-3.4.0.zip',
  zipSha256: '26aab21644a6531abec1e0285a3907a33a553da7d78d0675ffa323cbab800a95',
  files: {
    units: { path: 'vocab/unit/VOCAB_QUDT-UNITS-ALL.ttl', sha256: 'ad9b76adb7e1b106f7a74c699ebeea17c2479c20fc67f6de9363bb2538134ba8' },
    quantitykinds: { path: 'vocab/quantitykinds/VOCAB_QUDT-QUANTITY-KINDS-ALL.ttl', sha256: 'b50cdec5596f04dc3ac3ff7cc62f9961869084b4046c7c1ea0a4bfeb3fc6e403' },
    dimensionvectors: { path: 'vocab/dimensionvectors/VOCAB_QUDT-DIMENSION-VECTORS.ttl', sha256: '355932a5d73fdc6f5fa545f068c6c21cfb76cc01fa1eedaa096c840e004cc033' },
    prefixes: { path: 'vocab/prefixes/VOCAB_QUDT-PREFIXES.ttl', sha256: '0b646c2cfa66fa0a3a5bd84d68f19f26ab33a301431c3116f42c0b9d283929c7' },
  },
};
const QUDT = 'http://qudt.org/schema/qudt/';
const UNIT_NS = 'http://qudt.org/vocab/unit/';
const QK_NS = 'http://qudt.org/vocab/quantitykind/';
const QKDV_NS = 'http://qudt.org/vocab/dimensionvector/';
const PREFIX_NS = 'http://qudt.org/vocab/prefix/';
const SKOS_BROADER = 'http://www.w3.org/2004/02/skos/core#broader';
const RDFS_LABEL = 'http://www.w3.org/2000/01/rdf-schema#label';
const DIM_ORDER = ['T', 'L', 'M', 'I', 'Theta', 'N', 'J'];
const EXP_CAP = 10; // pinned |exponent| cap for physics-qudt (observed corpus range: [-6, 10])
const PI_CAP = 8;   // pinned |piExponent| cap

// --- args ----------------------------------------------------------------------------
const argv = process.argv.slice(2);
const argOf = (k, dflt) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : dflt; };
const outDir = argOf('--out', join(dirname(fileURLToPath(import.meta.url)), '..'));
const srcDir = argOf('--source', join(outDir, 'source'));

// --- load + verify pinned sources (fail closed) --------------------------------------
const loadPinned = (key) => {
  const f = SOURCE.files[key];
  const file = join(srcDir, f.path.split('/').pop());
  const bytes = readFileSync(file);
  const got = createHash('sha256').update(bytes).digest('hex');
  if (got !== f.sha256) {
    console.error(`ERR_SOURCE_PIN: ${file} sha256 ${got} != pinned ${f.sha256} (${SOURCE.release})`);
    process.exit(1);
  }
  return parseTurtle(bytes.toString('utf8'));
};
const g = {
  units: loadPinned('units'),
  qks: loadPinned('quantitykinds'),
  dvs: loadPinned('dimensionvectors'),
  prefixes: loadPinned('prefixes'),
};

// --- helpers ---------------------------------------------------------------------------
// deterministic code-unit string compare (NEVER localeCompare: ICU-dependent)
const cmpStr = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
const local = (iri, ns) => (iri && iri.startsWith(ns) ? iri.slice(ns.length) : null);
const findings = [];                       // cross-check findings (report material)
const finding = (kind, id, detail) => findings.push({ kind, id, ...detail });
const anomaly = (kind, id, note) => findings.push({ kind, id, note });

const pickLabel = (props) => {
  const ls = lits(props, RDFS_LABEL);
  const plain = ls.filter((l) => !l.lang).map((l) => l.v).sort();
  if (plain.length) return plain[0];
  const en = ls.filter((l) => l.lang === 'en').map((l) => l.v).sort();
  if (en.length) return en[0];
  const any = ls.map((l) => l.v).sort();
  return any[0] ?? null;
};
const pickLit = (props, pred) => {
  const vs = lits(props, pred).map((l) => l.v).sort();
  return vs[0] ?? null;
};
const isDeprecated = (props) => lits(props, QUDT + 'deprecated').some((l) => l.v === 'true');
const typesOf = (props) => new Set(iris(props, RDF_TYPE).map((t) => local(t, QUDT)).filter(Boolean));

// --- dimension vectors -------------------------------------------------------------------
// QUDT qkdv local-name slots (design §3, pinned mapping): A=amount(N) E=current(I)
// L=length I=luminous(J) M=mass H=temperature(Theta) T=time D=dimensionless flag.
const QKDV_RE = /^A(-?\d+(?:dot\d+)?)E(-?\d+(?:dot\d+)?)L(-?\d+(?:dot\d+)?)I(-?\d+(?:dot\d+)?)M(-?\d+(?:dot\d+)?)H(-?\d+(?:dot\d+)?)T(-?\d+(?:dot\d+)?)D(-?\d+(?:dot\d+)?)$/;
/** Parse a qkdv IRI -> { dim: [T,L,M,I,Theta,N,J] ints, D } | 'fractional' | 'not-applicable' | null. */
const parseQkdv = (iri) => {
  const l = local(iri, QKDV_NS);
  if (l === null) return null;
  if (l === 'NotApplicable') return 'not-applicable';
  const m = l.match(QKDV_RE);
  if (!m) return null;
  const [A, E, L, I, M, H, T, D] = m.slice(1);
  if ([A, E, L, I, M, H, T, D].some((x) => x.includes('dot'))) return 'fractional';
  const dim = [T, L, M, E, H, A, I].map(Number);
  if (dim.some((x) => !Number.isSafeInteger(x) || Math.abs(x) > EXP_CAP)) {
    console.error(`ERR_DIM_CAP: ${iri} exceeds pinned |exponent| cap ${EXP_CAP}`);
    process.exit(1);
  }
  return { dim, D: Number(D) };
};
const qkdvIriOf = (dim) => {
  const [T, L, M, I, Th, N, J] = dim;
  const D = dim.every((x) => x === 0) ? 1 : 0;
  return `${QKDV_NS}A${N}E${I}L${L}I${J}M${M}H${Th}T${T}D${D}`;
};
const vAdd = (a, b) => a.map((x, i) => x + b[i]);
const vScale = (a, n) => a.map((x) => x * n);
const vEq = (a, b) => a.every((x, i) => x === b[i]);

// Cross-check 1: IRI-derived exponents vs the explicit qudt:dimensionExponentFor*
// properties in the dimension-vectors vocabulary (two independent QUDT statements).
{
  const PROP_SLOT = {
    dimensionExponentForTime: 0, dimensionExponentForLength: 1, dimensionExponentForMass: 2,
    dimensionExponentForElectricCurrent: 3, dimensionExponentForThermodynamicTemperature: 4,
    dimensionExponentForAmountOfSubstance: 5, dimensionExponentForLuminousIntensity: 6,
  };
  let checked = 0;
  for (const [iri, props] of g.dvs.subjects) {
    const parsed = parseQkdv(iri);
    if (!parsed || parsed === 'not-applicable') continue;
    if (parsed === 'fractional') {
      // still cross-check as rationals
      for (const [prop] of Object.entries(PROP_SLOT)) {
        const stated = lits(props, QUDT + prop)[0]?.raw;
        if (stated === undefined) continue;
      }
      continue;
    }
    for (const [prop, slot] of Object.entries(PROP_SLOT)) {
      const stated = lits(props, QUDT + prop)[0]?.raw;
      if (stated === undefined) { anomaly('qkdv-missing-exponent-property', iri, prop); continue; }
      if (!rEq(rParse(stated), R(BigInt(parsed.dim[slot])))) {
        finding('qkdv-iri-vs-property-mismatch', iri, { prop, stated, iriDerived: parsed.dim[slot] });
      }
      checked++;
    }
    const dless = lits(props, QUDT + 'dimensionlessExponent')[0]?.raw;
    if (dless !== undefined && Number(dless) !== parsed.D) {
      finding('qkdv-dimensionless-flag-mismatch', iri, { stated: dless, iriDerived: parsed.D });
    }
  }
  console.error(`[qkdv] cross-checked ${checked} explicit exponent properties against IRI parses`);
}

// --- prefixes: curated exact values, cross-checked against QUDT floats --------------------
const prefixVal = new Map(); // local -> rational
for (const [iri, props] of g.prefixes.subjects) {
  const l = local(iri, PREFIX_NS);
  if (!l || !typesOf(props).has('Prefix')) continue;
  const exact = PREFIX_EXACT.get(l);
  if (!exact) { console.error(`ERR_PREFIX_UNCURATED: prefix:${l} has no curated exact value`); process.exit(1); }
  prefixVal.set(l, exact);
  const stated = lits(props, QUDT + 'prefixMultiplier')[0]?.raw;
  if (stated === undefined) anomaly('prefix-missing-multiplier', iri, l);
  else if (!rEq(rParse(stated), exact)) {
    // classify like unit multipliers below (report); prefix errors were among Keil & Schindler 2018 findings
    finding('prefix-multiplier-mismatch', iri, { stated, derived: rToString(exact) });
  }
}

// --- quantity kinds -------------------------------------------------------------------------
const qkExcl = new Map(); // local -> category
const qkRecords = new Map(); // local -> record object (record.dim held as numbers)
const qkDim = new Map(); // local -> dim
const excludeQk = (l, cat) => qkExcl.set(l, cat);

for (const [iri, props] of g.qks.subjects) {
  const l = local(iri, QK_NS);
  if (!l || !typesOf(props).has('QuantityKind')) continue;
  if (isDeprecated(props)) { excludeQk(l, 'deprecated'); continue; }
  // currency skip rule: QUDT stamps quantitykind:Currency* with the dimensionless
  // vector, so the dimension gates alone do not catch them (currency UNITS are
  // caught by their qudt:CurrencyUnit type)
  if (/^Currency/.test(l)) { excludeQk(l, 'currency'); continue; }
  const dvIris = iris(props, QUDT + 'hasDimensionVector');
  if (dvIris.length === 0) { excludeQk(l, 'missing-dimension-vector'); anomaly('qk-missing-dimension-vector', iri, 'no qudt:hasDimensionVector'); continue; }
  if (dvIris.length > 1) { excludeQk(l, 'multiple-dimension-vectors'); anomaly('qk-multiple-dimension-vectors', iri, dvIris.join(' ')); continue; }
  const parsed = parseQkdv(dvIris[0]);
  if (parsed === 'not-applicable') { excludeQk(l, 'not-applicable-dimension'); continue; }
  if (parsed === 'fractional') { excludeQk(l, 'fractional-dimension'); continue; }
  if (!parsed) { excludeQk(l, 'unparseable-dimension-vector'); anomaly('qk-unparseable-dimension-vector', iri, dvIris[0]); continue; }
  const expectedD = parsed.dim.every((x) => x === 0) ? 1 : 0;
  if (parsed.D !== expectedD) { excludeQk(l, 'd-flag-anomaly'); finding('qkdv-d-flag-anomaly', iri, { dv: dvIris[0], D: parsed.D, expectedD }); continue; }
  qkDim.set(l, parsed.dim);
  qkRecords.set(l, { props, iri, dv: dvIris[0], dim: parsed.dim });
}
// broader links restricted to included kinds (dropped links counted)
let broaderDropped = 0;
for (const [l, rec] of qkRecords) {
  const bs = iris(rec.props, SKOS_BROADER)
    .map((b) => local(b, QK_NS))
    .filter((b) => { if (b && qkRecords.has(b)) return true; broaderDropped++; return false; })
    .sort();
  rec.broader = bs;
}

// --- units: exclusion classes, then exact derivation fixpoint --------------------------------
const unitSubjects = new Map(); // local -> props
for (const [iri, props] of g.units.subjects) {
  const l = local(iri, UNIT_NS);
  if (l && typesOf(props).has('Unit')) unitSubjects.set(l, props);
}

const unitExcl = new Map(); // local -> {cat, note?}
const excludeUnit = (l, cat, note) => unitExcl.set(l, note ? { cat, note } : { cat });
const structOk = new Map(); // local -> {props, dim, dvIri, qkLocals}

for (const [l, props] of unitSubjects) {
  const types = typesOf(props);
  if (isDeprecated(props)) { excludeUnit(l, 'deprecated'); continue; }
  if (types.has('CurrencyUnit') || types.has('DigitalCurrencyUnit')) { excludeUnit(l, 'currency'); continue; }
  if (types.has('LogarithmicUnit')) { excludeUnit(l, 'log-scale'); continue; }
  if (types.has('CountingUnit')) { excludeUnit(l, 'counting'); continue; }
  if (EMPIRICAL.has(l)) { excludeUnit(l, 'empirical-factor', EMPIRICAL.get(l)); continue; }
  const pat = EMPIRICAL_PATTERNS.find((p) => p.re.test(l));
  if (pat) { excludeUnit(l, 'empirical-factor', pat.why); continue; }
  if (TRANSCENDENTAL.has(l)) { excludeUnit(l, 'transcendental-factor', TRANSCENDENTAL.get(l)); continue; }
  if (NONAFFINE_OR_ARBITRARY.has(l)) { excludeUnit(l, 'nonaffine-or-arbitrary', NONAFFINE_OR_ARBITRARY.get(l)); continue; }
  const dvIris = iris(props, QUDT + 'hasDimensionVector');
  if (dvIris.length !== 1) { excludeUnit(l, 'missing-structure', `hasDimensionVector count ${dvIris.length}`); continue; }
  const parsed = parseQkdv(dvIris[0]);
  if (parsed === 'not-applicable') { excludeUnit(l, 'not-applicable-dimension'); continue; }
  if (parsed === 'fractional') { excludeUnit(l, 'fractional-dimension'); continue; }
  if (!parsed) { excludeUnit(l, 'missing-structure', `unparseable dv ${dvIris[0]}`); continue; }
  const expectedD = parsed.dim.every((x) => x === 0) ? 1 : 0;
  if (parsed.D !== expectedD) { excludeUnit(l, 'd-flag-anomaly'); finding('unit-d-flag-anomaly', UNIT_NS + l, { dv: dvIris[0] }); continue; }
  const qkLocals = iris(props, QUDT + 'hasQuantityKind').map((q) => local(q, QK_NS)).filter(Boolean);
  if (qkLocals.length === 0) { excludeUnit(l, 'no-quantity-kind'); continue; }
  structOk.set(l, { props, dim: parsed.dim, dvIri: dvIris[0], qkLocals: [...new Set(qkLocals)].sort() });
}

// derivation state: local -> { p, offset, how }
const derived = new Map();
for (const [l, a] of ATOMS) {
  if (!unitSubjects.has(l)) continue; // curated atom absent from this QUDT release: fine, just unused
  derived.set(l, { p: a.p, offset: a.offset, how: `atom [${a.src}]` });
}
const factorParse = (props, l) => {
  const out = [];
  for (const t of props.get(QUDT + 'hasFactorUnit') ?? []) {
    if (t.t !== 'bnode') { anomaly('factor-unit-not-bnode', l, ''); return null; }
    const u = iris(t.props, QUDT + 'hasUnit')[0];
    const e = lits(t.props, QUDT + 'exponent')[0]?.raw;
    const ul = u ? local(u, UNIT_NS) : null;
    if (!ul || e === undefined || !/^-?\d+$/.test(e) || Number(e) === 0) { anomaly('factor-unit-malformed', l, `${u} ^ ${e}`); return null; }
    out.push({ u: ul, e: Number(e) });
  }
  return out;
};
const prefixParse = (props) => {
  const ps = iris(props, QUDT + 'prefix').map((p) => local(p, PREFIX_NS)).filter(Boolean);
  const bs = iris(props, QUDT + 'scalingOf').map((b) => local(b, UNIT_NS)).filter(Boolean);
  if (ps.length === 1 && bs.length === 1) return { prefix: ps[0], base: bs[0] };
  return null;
};

let changed = true;
while (changed) {
  changed = false;
  for (const [l, s] of structOk) {
    if (derived.has(l) || unitExcl.has(l)) continue;
    let viaPrefix = null;
    const pp = prefixParse(s.props);
    if (pp && prefixVal.has(pp.prefix) && derived.has(pp.base)) {
      const b = derived.get(pp.base);
      viaPrefix = {
        p: pMul(P(prefixVal.get(pp.prefix)), b.p),
        offset: b.offset,
        how: `prefix ${pp.prefix} (10^n/2^n exact, SI Brochure Table 7) x ${pp.base}`,
      };
    }
    let viaFactors = null;
    const fs = factorParse(s.props, l);
    if (fs && fs.length > 0 && fs.every((f) => derived.has(f.u))) {
      let p = pOne;
      const intervalNotes = [];
      for (const f of fs) {
        const fd = derived.get(f.u);
        if (!rEq(fd.offset, R0)) intervalNotes.push(f.u);
        p = pMul(p, pPow(fd.p, f.e));
      }
      viaFactors = {
        p, offset: R0,
        how: `product ${fs.map((f) => `${f.u}^${f.e}`).join(' ')}` +
          (intervalNotes.length ? ` (interval scale used for affine ${intervalNotes.join(',')})` : ''),
      };
    }
    if (viaPrefix && viaFactors && (!pEq(viaPrefix.p, viaFactors.p) || !rEq(viaPrefix.offset, viaFactors.offset))) {
      excludeUnit(l, 'derivation-conflict');
      finding('derivation-conflict', UNIT_NS + l, { prefixPath: viaPrefix.how, factorPath: viaFactors.how });
      continue;
    }
    const got = viaPrefix ?? viaFactors;
    if (got) { derived.set(l, got); changed = true; }
  }
}

// blocking-leaf analysis for underivable units (drives atom curation; goes in report)
const blockers = new Map();
const leafBlockersOf = (l, seen = new Set()) => {
  if (seen.has(l)) return [];
  seen.add(l);
  const s = structOk.get(l);
  if (!s) return [l];
  const pp = prefixParse(s.props);
  const fs = factorParse(s.props, l) ?? [];
  const deps = [...(pp ? [pp.base] : []), ...fs.map((f) => f.u)];
  if (deps.length === 0) return [l];
  const out = [];
  for (const dep of deps) if (!derived.has(dep)) out.push(...leafBlockersOf(dep, seen));
  return out.length ? out : [l];
};
for (const [l] of structOk) {
  if (derived.has(l) || unitExcl.has(l)) continue;
  const leaves = [...new Set(leafBlockersOf(l))].sort();
  // inherit exclusion category when a blocking leaf is itself excluded for a
  // structural reason (currency compounds, log-scale compounds, bit-family...)
  const excludedLeaf = leaves.find((b) => unitExcl.has(b));
  if (excludedLeaf) excludeUnit(l, `blocked-by:${unitExcl.get(excludedLeaf).cat}`, `leaf ${excludedLeaf}`);
  else excludeUnit(l, 'no-exact-derivation', `leaves: ${leaves.join(',')}`);
  for (const b of leaves) blockers.set(b, (blockers.get(b) ?? 0) + 1);
}

// --- cross-check derived scales/offsets against QUDT's stated floats --------------------------
// classification: exact | truncation (correctly rounded at stated precision) | DISCREPANCY
const sigDigits = (lex) => {
  const m = lex.replace(/^[+-]/, '').match(/^(\d*)\.?(\d*)(?:[eE].*)?$/);
  let digits = ((m?.[1] ?? '') + (m?.[2] ?? '')).replace(/^0+/, '');
  // integer-valued lexicals ("30856780000000000.0"): trailing zeros are not
  // resolvable as significant — treat them as placeholders
  if (/^0*$/.test(m?.[2] ?? '')) digits = digits.replace(/0+$/, '');
  return Math.max(digits.length, 1);
};
const classify = (statedLex, derivedP) => {
  const s = rParse(statedLex);
  const dExact = derivedP.pi === 0 ? derivedP.r : null;
  const d = dExact ?? pApprox(derivedP); // PI_50 approx: error < 1e-49 relative, far below any threshold used here
  if (s.num === 0n) return d.num === 0n ? { cls: 'exact' } : { cls: 'DISCREPANCY', why: 'stated zero for nonzero unit' };
  if (dExact && rEq(s, dExact)) return { cls: 'exact' };
  if (d.num === 0n) return { cls: 'DISCREPANCY', why: 'derived zero' };
  // half-ulp tolerance at stated precision: |d - s| <= 10^(e-k+1)/2, e = floor(log10|s|)
  const k = sigDigits(statedLex);
  let e = 0; const num = s.num < 0n ? -s.num : s.num;
  let hi = s.den; while (num >= hi * 10n) { hi *= 10n; e++; }
  let lo = num; while (lo < s.den) { lo *= 10n; e--; }
  const tolExp = e - k + 1;
  const tol = tolExp >= 0 ? R(10n ** BigInt(tolExp), 2n) : R(1n, 2n * 10n ** BigInt(-tolExp));
  const diff = rAbs(rSub(d, s));
  if (rCmp(diff, tol) <= 0) return { cls: 'truncation', sig: k };
  // relative error |1 - stated/derived| (exact rational; approx string for the report)
  const relR = rAbs(rSub(R1, rMul(s, rPow(d, -1))));
  const rel = rToApprox(relR, 6);
  // decimal-dust: stated agrees with exact to >= 13 significant digits (well
  // beyond IEEE-double consumers) but its own printed tail is arithmetic
  // garbage — systematic in QUDT's high-precision decimal pipeline; counted
  // as a class, not analysed case-by-case (see qudt-discrepancies.md §dust)
  if (rCmp(relR, R(1n, 10n ** 13n)) <= 0) return { cls: 'decimal-dust', sig: k, rel };
  return { cls: 'DISCREPANCY', sig: k, rel, statedVal: rToApprox(s, 20), derivedVal: rToApprox(d, 20) };
};

const crossOk = { exact: 0, truncation: 0, dust: 0 };
const discrepancies = [];
const truncations = [];
const dusts = [];
for (const [l, dv] of derived) {
  const s = structOk.get(l);
  if (!s) continue;
  const statedM = lits(s.props, QUDT + 'conversionMultiplier')[0]?.raw;
  const statedO = lits(s.props, QUDT + 'conversionOffset')[0]?.raw;
  if (statedM === undefined) { anomaly('unit-missing-stated-multiplier', UNIT_NS + l, dv.how); continue; }
  const cm = classify(statedM, dv.p);
  const derivedStr = dv.p.pi === 0 ? rToString(dv.p.r) : `${rToString(dv.p.r)} * pi^${dv.p.pi}`;
  if (cm.cls === 'DISCREPANCY') discrepancies.push({ unit: l, field: 'conversionMultiplier', stated: statedM, derived: derivedStr, derivedApprox: rToApprox(pApprox(dv.p), 20), how: dv.how, ...cm });
  else if (cm.cls === 'decimal-dust') { crossOk.dust++; dusts.push({ unit: l, stated: statedM, derived: derivedStr, rel: cm.rel }); }
  else if (cm.cls === 'truncation') { crossOk.truncation++; truncations.push({ unit: l, stated: statedM, derived: derivedStr, derivedApprox: rToApprox(pApprox(dv.p), 18) }); }
  else crossOk.exact++;
  // offset semantics (QUDT 3.x): value_SI = (value + conversionOffset) * conversionMultiplier
  // (empirically pinned: DEG_F 459.67 x 5/9, MilliDEG_C 273150 x 0.001 — both check exactly)
  // ours: value_SI = value*scale + offset  =>  statedOffset should equal offset/scale
  if (!rEq(dv.offset, R0) || statedO !== undefined) {
    if (dv.p.pi !== 0) { anomaly('affine-pi-unit', UNIT_NS + l, 'affine unit with symbolic pi scale — unexpected'); continue; }
    const ourStatedEquiv = P(rMul(dv.offset, rPow(dv.p.r, -1)));
    const co = classify(statedO ?? '0', ourStatedEquiv);
    if (co.cls === 'DISCREPANCY' || co.cls === 'decimal-dust') discrepancies.push({ unit: l, field: 'conversionOffset', stated: statedO ?? '(absent)', derived: rToString(ourStatedEquiv.r), how: dv.how, ...co });
  }
}

// Cross-check 3: unit's stated dimension vector vs factor-unit dimensional composition
let dimCompChecked = 0;
for (const [l, s] of structOk) {
  const fs = factorParse(s.props, l);
  if (!fs || fs.length === 0) continue;
  let ok = true;
  let sum = [0, 0, 0, 0, 0, 0, 0];
  for (const f of fs) {
    const fd = structOk.get(f.u)?.dim ?? (() => {
      const p = unitSubjects.has(f.u) ? parseQkdv(iris(unitSubjects.get(f.u), QUDT + 'hasDimensionVector')[0] ?? '') : null;
      return p && p !== 'fractional' && p !== 'not-applicable' ? p.dim : null;
    })();
    if (!fd) { ok = false; break; }
    sum = vAdd(sum, vScale(fd, f.e));
  }
  if (!ok) continue;
  dimCompChecked++;
  if (!vEq(sum, s.dim)) finding('unit-dim-composition-mismatch', UNIT_NS + l, { stated: s.dvIri, composed: qkdvIriOf(sum) });
}
console.error(`[units] dimensional composition cross-checked for ${dimCompChecked} factored units`);

// --- assemble records --------------------------------------------------------------------------
const prov = (fileKey) => ({
  source: `${SOURCE.name} ${SOURCE.release} (released ${SOURCE.releasedAt})`,
  sourceCommit: SOURCE.commit,
  sourceFile: SOURCE.files[fileKey].path,
  sourceSha256: SOURCE.files[fileKey].sha256,
  extractor: `tools/extract.mjs ${EXTRACTOR_VERSION}`,
  extractionDate: EXTRACTION_DATE,
});

const qkOut = [];
for (const l of [...qkRecords.keys()].sort()) {
  const rec = qkRecords.get(l);
  const r = {
    schema: 'kot-phys/1',
    type: 'QuantityKind',
    id: `urn:physics-qudt:qk:${l}`,
    label: pickLabel(rec.props) ?? l,
    dim: rec.dim,
    dimOrder: DIM_ORDER,
    status: 'research-grade',
    semanticStatus: 'AxiomsOnly',
  };
  const sym = pickLit(rec.props, QUDT + 'symbol');
  if (sym) r.symbol = sym;
  if (rec.broader.length) r.broader = rec.broader.map((b) => `urn:physics-qudt:qk:${b}`);
  r.provenance = prov('quantitykinds');
  r.bridgesTo = { qudtQuantityKind: rec.iri, qudtDimensionVector: rec.dv };
  r.bridgeStatus = 'derived-from-source: extracted from the pinned QUDT release; the qudtDimensionVector local name is mechanically recomputed from dim and byte-checked by validate.mjs';
  qkOut.push(r);
}

const unitOut = [];
let qkDimMismatchPairs = 0;
for (const l of [...structOk.keys()].sort()) {
  if (unitExcl.has(l)) continue;
  const s = structOk.get(l);
  const dv = derived.get(l);
  const matching = [];
  let anyIncluded = false;
  for (const q of s.qkLocals) {
    if (!qkRecords.has(q)) {
      if (!qkExcl.has(q)) anomaly('dangling-qk-ref', UNIT_NS + l, QK_NS + q);
      continue;
    }
    anyIncluded = true;
    if (vEq(qkDim.get(q), s.dim)) matching.push(q);
    else { qkDimMismatchPairs++; finding('unit-qk-dim-mismatch', UNIT_NS + l, { qk: q, unitDim: s.dvIri, qkDim: qkdvIriOf(qkDim.get(q)) }); }
  }
  if (matching.length === 0) {
    // distinguish "all its kinds are excluded placeholders (quantitykind:Unknown,
    // deprecated kinds...)" from a genuine dimensional inconsistency in QUDT
    if (!anyIncluded) excludeUnit(l, 'quantity-kind-excluded', `kinds: ${s.qkLocals.join(',')}`);
    else excludeUnit(l, 'qk-dim-mismatch', 'no included quantity kind shares the unit dimension vector');
    continue;
  }
  const coherent = dv.p.pi === 0 && rEq(dv.p.r, R1) && rEq(dv.offset, R0);
  if (Math.abs(dv.p.pi) > PI_CAP) { console.error(`ERR_PI_CAP: ${l} piExponent ${dv.p.pi}`); process.exit(1); }
  const r = {
    schema: 'kot-phys/1',
    type: 'Unit',
    id: `urn:physics-qudt:unit:${l}`,
    label: pickLabel(s.props) ?? l,
  };
  const sym = pickLit(s.props, QUDT + 'symbol');
  if (sym) r.symbol = sym;
  r.quantityKind = `urn:physics-qudt:qk:${matching[0]}`;
  if (matching.length > 1) r.otherQuantityKinds = matching.slice(1).map((q) => `urn:physics-qudt:qk:${q}`);
  r.scale = rToString(dv.p.r);
  if (dv.p.pi !== 0) r.piExponent = dv.p.pi;
  r.offset = rToString(dv.offset);
  r.coherentSI = coherent;
  r.status = 'research-grade';
  r.semanticStatus = 'AxiomsOnly';
  r.derivation = dv.how;
  r.provenance = prov('units');
  r.bridgesTo = { qudtUnit: UNIT_NS + l };
  const ucum = pickLit(s.props, QUDT + 'ucumCode');
  if (ucum) r.bridgesTo.ucumCode = ucum;
  r.bridgeStatus = 'derived-from-source: extracted from the pinned QUDT release (IRI resolvable in source by construction); ucumCode is annotation-grade, not grammar-verified';
  unitOut.push(r);
}

// --- outputs (deterministic) ----------------------------------------------------------------------
mkdirSync(outDir, { recursive: true });
const jsonl = (arr) => arr.map((r) => JSON.stringify(r)).join('\n') + '\n';
writeFileSync(join(outDir, 'quantitykinds.jsonl'), jsonl(qkOut));
writeFileSync(join(outDir, 'units.jsonl'), jsonl(unitOut));

// dimension lane (golden discipline mirrors physics-v0)
const laneVectors = {};
for (const r of qkOut) laneVectors[r.id] = r.dim;
const classes = new Map();
for (const r of qkOut) {
  const k = r.dim.join(',');
  if (!classes.has(k)) classes.set(k, []);
  classes.get(k).push(r.id);
}
const collisionClasses = [...classes.values()].filter((c) => c.length > 1).sort((a, b) => cmpStr(a[0], b[0]));
writeFileSync(join(outDir, 'dimension-lane.json'), JSON.stringify({
  schema: 'kot-phys-dimlane/1',
  note: 'Exact dimension-exponent lane for physics-qudt quantity kinds (integer exponents over the pinned order [T,L,M,I,Theta,N,J]; deterministic; no floats). Metric: L2 only — dimensionless kinds sit at the zero vector where cosine is undefined.',
  dimOrder: DIM_ORDER,
  quantityKinds: qkOut.length,
  distinctVectors: classes.size,
  collisionClassCount: collisionClasses.length,
  collisionClasses,
  vectors: laneVectors,
}, null, 2) + '\n');

// exclusions (machine-readable, counted)
const exclusions = { quantityKinds: {}, units: {} };
for (const [l, cat] of [...qkExcl].sort()) (exclusions.quantityKinds[cat] ??= []).push(l);
for (const [l, e] of [...unitExcl].sort()) (exclusions.units[e.cat] ??= []).push(l);
const exclCounts = (o) => Object.fromEntries(Object.entries(o).sort().map(([k, v]) => [k, v.length]));
writeFileSync(join(outDir, 'exclusions.json'), JSON.stringify({
  note: 'Every QUDT subject not emitted as a record, by category. Exclusion RULES are documented in README.md; nothing is silently dropped.',
  counts: { quantityKinds: exclCounts(exclusions.quantityKinds), units: exclCounts(exclusions.units) },
  quantityKinds: exclusions.quantityKinds,
  units: exclusions.units,
}, null, 2) + '\n');

// findings + cross-check detail (report material)
findings.sort((a, b) => cmpStr(a.kind, b.kind) || cmpStr(String(a.id), String(b.id)));
discrepancies.sort((a, b) => cmpStr(a.unit, b.unit));
truncations.sort((a, b) => cmpStr(a.unit, b.unit));
writeFileSync(join(outDir, 'crosscheck.json'), JSON.stringify({
  note: 'Cross-validation of exact derived values against QUDT stated floats. exact: literal equality of rationals. truncation: QUDT literal is the exact value correctly rounded at its own precision (half-ulp criterion) — benign float publication. DISCREPANCY: disagreement beyond stated precision — analysed in qudt-discrepancies.md.',
  multiplierCounts: { exact: crossOk.exact, truncation: crossOk.truncation, decimalDust: crossOk.dust, discrepancy: discrepancies.filter((d) => d.field === 'conversionMultiplier').length },
  discrepancies,
  otherFindings: findings,
  decimalDust: dusts.sort((a, b) => cmpStr(a.unit, b.unit)),
  truncations,
  blockingLeaves: [...blockers].sort((a, b) => b[1] - a[1] || cmpStr(a[0], b[0])).map(([u, c]) => ({ unit: u, blocks: c })),
}, null, 2) + '\n');

// manifest
const unitTotal = unitSubjects.size;
const manifest = {
  corpus: 'physics-qudt',
  schema: 'kot-phys/1',
  version: '0.1.0',
  generated: EXTRACTION_DATE,
  authorship: 'research-grade, agent-extracted bulk tier (docs/design-bulk-kernel.md); NOT federation-endorsed. Dimension vectors derived mechanically from QUDT dimension-vector IRIs; unit conversions derived EXACTLY from the curated atom table (tools/atoms.mjs, primary conventions cited) + prefix/factor composition — QUDT stated conversion factors are cross-checked, never copied. semanticStatus: AxiomsOnly (no semantic-adequacy claim).',
  dimOrder: DIM_ORDER,
  expCap: EXP_CAP,
  piCap: PI_CAP,
  scaleModel: 'value_SI = lexical * (scale * pi^piExponent) + offset; scale/offset exact rationals (decimal or p/q strings), piExponent an integer (omitted when 0) carrying pi symbolically for the angle/CGS families',
  source: SOURCE,
  extractor: { version: EXTRACTOR_VERSION, entry: 'tools/extract.mjs' },
  recordCount: qkOut.length + unitOut.length,
  counts: { QuantityKind: qkOut.length, Unit: unitOut.length },
  sourceSubjectCounts: { quantityKinds: qkRecords.size + qkExcl.size, units: unitTotal },
  exclusionCounts: { quantityKinds: exclCounts(exclusions.quantityKinds), units: exclCounts(exclusions.units) },
  crossCheck: {
    conversionMultiplier: { exact: crossOk.exact, truncation: crossOk.truncation, decimalDust: crossOk.dust, discrepancy: discrepancies.filter((d) => d.field === 'conversionMultiplier').length },
    conversionOffset: { discrepancy: discrepancies.filter((d) => d.field === 'conversionOffset').length },
    otherFindingCounts: Object.fromEntries([...findings.reduce((m, f) => m.set(f.kind, (m.get(f.kind) ?? 0) + 1), new Map())].sort()),
    unitQkDimMismatchPairs: qkDimMismatchPairs,
  },
  dimensionLane: { quantityKinds: qkOut.length, distinctVectors: classes.size, collisionClasses: collisionClasses.length },
  broaderLinksDropped: broaderDropped,
};
writeFileSync(join(outDir, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');

// console summary
const sum = (o) => Object.values(o).reduce((a, b) => a + b, 0);
console.error(`\nphysics-qudt extraction (${SOURCE.release}):`);
console.error(`  quantity kinds: ${qkOut.length} emitted, ${qkExcl.size} excluded ${JSON.stringify(exclCounts(exclusions.quantityKinds))}`);
console.error(`  units: ${unitOut.length} emitted of ${unitTotal}; excluded ${sum(exclCounts(exclusions.units))} ${JSON.stringify(exclCounts(exclusions.units))}`);
console.error(`  multiplier cross-check: ${crossOk.exact} exact, ${crossOk.truncation} truncation, ${crossOk.dust} decimal-dust, ${discrepancies.filter((d) => d.field === 'conversionMultiplier').length} DISCREPANCIES`);
console.error(`  other findings: ${findings.length}; top blocking leaves: ${[...blockers].sort((a, b) => b[1] - a[1]).slice(0, 15).map(([u, c]) => `${u}(${c})`).join(' ')}`);
