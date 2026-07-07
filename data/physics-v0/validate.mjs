#!/usr/bin/env node
/**
 * physics-v0 corpus validation harness + dimension-lane prototype.
 *
 * Self-contained (zero deps, node:fs only). ALL definitional arithmetic is
 * exact: dimension exponent vectors are BigInt integer 7-vectors; unit
 * scale/offset and constant values are exact rationals (BigInt num/den)
 * parsed from decimal or "p/q" strings. No floats touch definitional
 * content anywhere in this file (house rule; cf. encoder/ conventions:
 * "no silent fallbacks; fail closed with ERR_* codes").
 *
 * Gates:
 *   0. corpus shape: schema/type/id uniqueness, file/manifest cross-check
 *   1. dimensions: 7 records, pinned order [T,L,M,I,Theta,N,J], indices 0..6
 *   2. quantity kinds: dim is an exact integer 7-vector (|e| <= 8);
 *      coherentSIUnit (if present) resolves, matches kind, and is coherent;
 *      asserted QUDT dimension-vector IRI is recomputed from dim and must
 *      byte-match (the bridge local name is mechanical, so it is CHECKED)
 *   3. units: quantityKind resolves; scale/offset parse as exact rationals;
 *      coherentSI <=> (scale == 1 and offset == 0); offset != 0 only on the
 *      thermodynamic-temperature kind in v0 (affine family)
 *   4. constants: value parses exactly; quantityKind + coherentSIUnit resolve
 *      and agree; unit is coherent (constants are stated in coherent SI)
 *   5. equations: closed grammar (quantity|constant|scalar|product|power|sum),
 *      integer exponents, exact-rational scalars; dim(lhs) == dim(rhs) exactly
 *   6. checker integrity (self-tests): a deliberately ill-typed equation
 *      (E = m·c) MUST fail; sum accepts equal-dim summands and MUST reject
 *      mixed-dim summands (sum is in the grammar; unexercised by v0 records)
 *   7. dimension lane: emit exact per-quantity-kind exponent vectors to
 *      dimension-lane.json (golden discipline: byte-compare unless --write),
 *      and report the injectivity/collision-class structure honestly.
 *
 * Usage: node data/physics-v0/validate.mjs [--write]
 * Exit 0 iff every gate passes.
 */
import { readFileSync, readdirSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const SCHEMA = 'kot-phys/1';
const DIM_ORDER = ['T', 'L', 'M', 'I', 'Theta', 'N', 'J'];
const EXP_CAP = 8n; // pinned |exponent| cap for v0 (all corpus values are within [-3, 4])
const failures = [];
const fail = (id, code, msg) => failures.push([id, code, msg]);

// --- exact rational arithmetic (BigInt) --------------------------------------
const bgcd = (a, b) => { a = a < 0n ? -a : a; b = b < 0n ? -b : b; while (b) [a, b] = [b, a % b]; return a; };
const rat = (num, den = 1n) => {
  if (den === 0n) throw new Error('zero denominator');
  if (den < 0n) { num = -num; den = -den; }
  const g = bgcd(num, den) || 1n;
  return { num: num / g, den: den / g };
};
/** Parse an exact-rational string: integer, decimal, decimal-exponent, or "p/q". */
const parseRat = (s) => {
  if (typeof s !== 'string') throw new Error(`rational must be a string, got ${typeof s}`);
  const frac = s.match(/^(-?\d+)\/(\d+)$/);
  if (frac) return rat(BigInt(frac[1]), BigInt(frac[2]));
  const dec = s.match(/^(-?)(\d+)(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/);
  if (!dec) throw new Error(`not an exact-rational literal: ${JSON.stringify(s)}`);
  const [, sign, ip, fp = '', exp = '0'] = dec;
  let num = BigInt(ip + fp) * (sign === '-' ? -1n : 1n);
  let e = BigInt(exp) - BigInt(fp.length);
  return e >= 0n ? rat(num * 10n ** e) : rat(num, 10n ** -e);
};
const ratEq = (a, b) => a.num === b.num && a.den === b.den;
const RAT_ONE = rat(1n);
const RAT_ZERO = rat(0n);

// --- exact integer 7-vectors --------------------------------------------------
const vecOf = (arr, id) => {
  if (!Array.isArray(arr) || arr.length !== 7) { fail(id, 'ERR_DIM_SHAPE', `dim must be a 7-array`); return null; }
  const v = [];
  for (const x of arr) {
    if (typeof x !== 'number' || !Number.isSafeInteger(x)) { fail(id, 'ERR_DIM_INT', `non-integer exponent ${x}`); return null; }
    const b = BigInt(x);
    if (b > EXP_CAP || b < -EXP_CAP) { fail(id, 'ERR_DIM_CAP', `|exponent| > ${EXP_CAP}`); return null; }
    v.push(b);
  }
  return v;
};
const vAdd = (a, b) => a.map((x, i) => x + b[i]);
const vScale = (a, n) => a.map((x) => x * n);
const vEq = (a, b) => a.every((x, i) => x === b[i]);
const vKey = (v) => v.join(',');
const ZERO7 = [0n, 0n, 0n, 0n, 0n, 0n, 0n];

// QUDT dimension-vector IRI local name, mechanically derived from [T,L,M,I,Theta,N,J].
// QUDT slots: A=amount(N) E=current(I) L=length I=luminous(J) M=mass H=temp(Theta) T=time D=dimensionless.
const qkdvIri = (v) => {
  const [T, L, M, I, Th, N, J] = v;
  const D = v.every((x) => x === 0n) ? 1 : 0;
  return `http://qudt.org/vocab/dimensionvector/A${N}E${I}L${L}I${J}M${M}H${Th}T${T}D${D}`;
};

// --- load corpus ---------------------------------------------------------------
const manifest = JSON.parse(readFileSync(join(root, 'manifest.json'), 'utf8'));
const subdirs = ['dimensions', 'quantitykinds', 'units', 'constants', 'equations'];
const records = new Map(); // id -> record
const byType = { BaseDimension: [], QuantityKind: [], Unit: [], DefiningConstant: [], DefiningRelation: [] };
for (const sub of subdirs) {
  for (const f of readdirSync(join(root, sub)).filter((x) => x.endsWith('.json')).sort()) {
    const doc = JSON.parse(readFileSync(join(root, sub, f), 'utf8'));
    if (doc.schema !== SCHEMA) fail(`${sub}/${f}`, 'ERR_SCHEMA', `expected ${SCHEMA}`);
    if (!doc.id || records.has(doc.id)) fail(`${sub}/${f}`, 'ERR_DUP_ID', `missing/duplicate id ${doc.id}`);
    if (!byType[doc.type]) fail(doc.id, 'ERR_TYPE', `unknown type ${doc.type}`);
    else byType[doc.type].push(doc);
    records.set(doc.id, doc);
  }
}

// --- gate 1: base dimensions ---------------------------------------------------
if (byType.BaseDimension.length !== 7) fail('<dims>', 'ERR_DIM_COUNT', `${byType.BaseDimension.length} != 7`);
const dimByIndex = [...byType.BaseDimension].sort((a, b) => a.index - b.index);
dimByIndex.forEach((d, i) => {
  if (d.index !== i) fail(d.id, 'ERR_DIM_INDEX', `indices must be exactly 0..6`);
  if (d.symbol !== DIM_ORDER[i]) fail(d.id, 'ERR_DIM_ORDER', `symbol ${d.symbol} at index ${i}, pinned order is ${DIM_ORDER}`);
  if (!records.has(d.siBaseUnit)) fail(d.id, 'ERR_REF', `siBaseUnit ${d.siBaseUnit} unresolved`);
});

// --- gate 2: quantity kinds ------------------------------------------------------
const qkDim = new Map(); // id -> BigInt 7-vector
for (const qk of byType.QuantityKind) {
  const v = vecOf(qk.dim, qk.id);
  if (!v) continue;
  qkDim.set(qk.id, v);
  if (JSON.stringify(qk.dimOrder) !== JSON.stringify(DIM_ORDER)) fail(qk.id, 'ERR_DIM_ORDER', 'dimOrder must equal the pinned order');
  const asserted = qk.bridgesTo?.qudtDimensionVector;
  if (asserted && asserted !== qkdvIri(v)) fail(qk.id, 'ERR_QKDV_MISMATCH', `asserted ${asserted} != derived ${qkdvIri(v)}`);
  if (qk.coherentSIUnit) {
    const u = records.get(qk.coherentSIUnit);
    if (!u || u.type !== 'Unit') fail(qk.id, 'ERR_REF', `coherentSIUnit ${qk.coherentSIUnit} unresolved`);
    else {
      if (u.quantityKind !== qk.id) fail(qk.id, 'ERR_QK_UNIT_KIND', `unit ${u.id} has quantityKind ${u.quantityKind}`);
      if (!u.coherentSI) fail(qk.id, 'ERR_QK_UNIT_COHERENT', `coherentSIUnit ${u.id} is not coherent`);
    }
  }
}

// --- gate 3: units ----------------------------------------------------------------
for (const u of byType.Unit) {
  const qk = records.get(u.quantityKind);
  if (!qk || qk.type !== 'QuantityKind') { fail(u.id, 'ERR_REF', `quantityKind ${u.quantityKind} unresolved`); continue; }
  let scale, offset;
  try { scale = parseRat(u.scale); offset = parseRat(u.offset); }
  catch (e) { fail(u.id, 'ERR_RATIONAL', e.message); continue; }
  if (scale.num <= 0n) fail(u.id, 'ERR_SCALE_SIGN', 'scale must be positive');
  const coherent = ratEq(scale, RAT_ONE) && ratEq(offset, RAT_ZERO);
  if (Boolean(u.coherentSI) !== coherent) fail(u.id, 'ERR_COHERENT_FLAG', `coherentSI=${u.coherentSI} but scale=${u.scale} offset=${u.offset}`);
  if (!ratEq(offset, RAT_ZERO) && u.quantityKind !== 'urn:physics-v0:qk:thermodynamic-temperature') {
    fail(u.id, 'ERR_AFFINE_KIND', 'v0 admits affine (offset != 0) units only on thermodynamic-temperature');
  }
}

// --- gate 4: defining constants -----------------------------------------------------
for (const c of byType.DefiningConstant) {
  try { parseRat(c.value); } catch (e) { fail(c.id, 'ERR_RATIONAL', e.message); }
  const qk = records.get(c.quantityKind);
  if (!qk || qk.type !== 'QuantityKind') fail(c.id, 'ERR_REF', `quantityKind ${c.quantityKind} unresolved`);
  const u = records.get(c.coherentSIUnit);
  if (!u || u.type !== 'Unit') fail(c.id, 'ERR_REF', `coherentSIUnit ${c.coherentSIUnit} unresolved`);
  else {
    if (u.quantityKind !== c.quantityKind) fail(c.id, 'ERR_CONST_UNIT_KIND', `unit kind ${u.quantityKind} != constant kind ${c.quantityKind}`);
    if (!u.coherentSI) fail(c.id, 'ERR_CONST_UNIT_COHERENT', 'defining-constant values are stated in coherent SI units');
  }
  if (c.status !== 'exact-by-definition') fail(c.id, 'ERR_CONST_STATUS', 'defining constants are exact-by-definition (SI 2019)');
}

// --- gate 5: equation grammar + exact dimension inference ----------------------------
const NODE_KINDS = new Set(['quantity', 'constant', 'scalar', 'product', 'power', 'sum']);
/** dim: QExpr -> BigInt 7-vector; throws {code, message} on any violation. */
const dimOf = (node, depth = 0) => {
  if (depth > 8) throw { code: 'ERR_EQ_DEPTH', message: 'expression deeper than cap 8' };
  if (node === null || typeof node !== 'object' || !NODE_KINDS.has(node.kind)) {
    throw { code: 'ERR_EQ_GRAMMAR', message: `unknown node ${JSON.stringify(node?.kind)}` };
  }
  switch (node.kind) {
    case 'quantity': {
      const v = qkDim.get(node.ref);
      if (!v) throw { code: 'ERR_EQ_REF', message: `quantity ref ${node.ref} unresolved` };
      return v;
    }
    case 'constant': {
      const c = records.get(node.ref);
      if (!c || c.type !== 'DefiningConstant') throw { code: 'ERR_EQ_REF', message: `constant ref ${node.ref} unresolved` };
      const v = qkDim.get(c.quantityKind);
      if (!v) throw { code: 'ERR_EQ_REF', message: `constant ${node.ref} has unresolved quantityKind` };
      return v;
    }
    case 'scalar':
      parseRat(node.value); // must be an exact rational literal
      return ZERO7;
    case 'product': {
      if (!Array.isArray(node.factors) || node.factors.length < 2) throw { code: 'ERR_EQ_GRAMMAR', message: 'product needs >= 2 factors' };
      return node.factors.map((f) => dimOf(f, depth + 1)).reduce(vAdd);
    }
    case 'power': {
      if (typeof node.exponent !== 'number' || !Number.isSafeInteger(node.exponent) || node.exponent === 0) {
        throw { code: 'ERR_EQ_GRAMMAR', message: 'power exponent must be a nonzero integer (rational exponents are out of v0)' };
      }
      return vScale(dimOf(node.base, depth + 1), BigInt(node.exponent));
    }
    case 'sum': {
      if (!Array.isArray(node.terms) || node.terms.length < 2) throw { code: 'ERR_EQ_GRAMMAR', message: 'sum needs >= 2 terms' };
      const dims = node.terms.map((t) => dimOf(t, depth + 1));
      for (const d of dims) if (!vEq(d, dims[0])) throw { code: 'ERR_EQ_SUM_DIM', message: 'sum terms must share one exact dimension vector' };
      return dims[0];
    }
  }
};
const eqRows = [];
for (const eq of byType.DefiningRelation) {
  try {
    const l = dimOf(eq.lhs);
    const r = dimOf(eq.rhs);
    const ok = vEq(l, r);
    if (!ok) fail(eq.id, 'ERR_EQ_DIM', `dim(lhs)=[${l}] != dim(rhs)=[${r}]`);
    eqRows.push({ id: eq.id, statement: eq.statement, dim: `[${l.join(' ')}]`, ok });
  } catch (e) {
    fail(eq.id, e.code ?? 'ERR_EQ', e.message);
    eqRows.push({ id: eq.id, statement: eq.statement, dim: '-', ok: false });
  }
}

// --- gate 6: checker integrity (negative + sum self-tests) ----------------------------
// A checker that cannot reject is not a checker. These MUST fail/behave as stated.
{
  const Q = (s) => ({ kind: 'quantity', ref: `urn:physics-v0:qk:${s}` });
  // 6a. ill-typed: E = m·c (missing one power of velocity) must NOT dimension-check
  const bad = { lhs: Q('energy'), rhs: { kind: 'product', factors: [Q('mass'), { kind: 'constant', ref: 'urn:physics-v0:const:speed-of-light' }] } };
  if (vEq(dimOf(bad.lhs), dimOf(bad.rhs))) fail('<self-test>', 'ERR_SELFTEST_NEG', 'ill-typed E=m·c passed the dimension check');
  // 6b. sum of equal dims accepted: v_total = v1 + v2 (both velocity)
  try { dimOf({ kind: 'sum', terms: [Q('velocity'), Q('velocity')] }); }
  catch { fail('<self-test>', 'ERR_SELFTEST_SUM_OK', 'equal-dim sum was rejected'); }
  // 6c. mixed-dim sum rejected: velocity + energy
  let rejected = false;
  try { dimOf({ kind: 'sum', terms: [Q('velocity'), Q('energy')] }); } catch { rejected = true; }
  if (!rejected) fail('<self-test>', 'ERR_SELFTEST_SUM_BAD', 'mixed-dim sum was accepted');
}

// --- gate 7: dimension-lane emission (golden discipline) --------------------------------
const laneVectors = {};
for (const id of [...qkDim.keys()].sort()) laneVectors[id] = qkDim.get(id).map((x) => Number(x));
const classes = new Map();
for (const [id, v] of [...qkDim.entries()].sort()) {
  const key = vKey(v);
  if (!classes.has(key)) classes.set(key, []);
  classes.get(key).push(id);
}
const collisionClasses = [...classes.values()].filter((c) => c.length > 1).sort((a, b) => a[0].localeCompare(b[0]));
const lane = {
  schema: 'kot-phys-dimlane/1',
  note: 'Exact dimension-exponent lane for physics-v0 quantity kinds. Integer exponents over the pinned order; deterministic by construction (no seeds, no floats, no training). Metric: L2 only — the zero vector (dimensionless kinds) makes cosine undefined.',
  dimOrder: DIM_ORDER,
  quantityKinds: Object.keys(laneVectors).length,
  distinctVectors: classes.size,
  collisionClasses,
  vectors: laneVectors,
};
const laneBytes = JSON.stringify(lane, null, 2) + '\n';
const lanePath = join(root, 'dimension-lane.json');
if (process.argv.includes('--write') || !existsSync(lanePath)) {
  writeFileSync(lanePath, laneBytes);
  console.log(`wrote ${lanePath}`);
} else if (readFileSync(lanePath, 'utf8') !== laneBytes) {
  fail('<lane>', 'ERR_LANE_GOLDEN', 'dimension-lane.json does not match recomputation (use --write on a deliberate change)');
}

// --- manifest cross-checks ---------------------------------------------------------------
if (manifest.recordCount !== records.size) fail('<manifest>', 'ERR_MANIFEST_COUNT', `${manifest.recordCount} != ${records.size}`);
for (const e of manifest.records ?? []) if (!records.has(e.id)) fail('<manifest>', 'ERR_MANIFEST_ID', `${e.id} listed but not on disk`);
for (const t of Object.keys(byType)) {
  if ((manifest.counts?.[t] ?? 0) !== byType[t].length) fail('<manifest>', 'ERR_MANIFEST_TYPE_COUNT', `${t}: ${manifest.counts?.[t]} != ${byType[t].length}`);
}
if (JSON.stringify(manifest.collisionClasses?.map((c) => [...c].sort()).sort()) !==
    JSON.stringify(collisionClasses.map((c) => [...c].sort()).sort())) {
  fail('<manifest>', 'ERR_MANIFEST_COLLISIONS', 'declared collision classes do not match recomputation');
}

// --- report -------------------------------------------------------------------------------
const pad = (s, n) => String(s).padEnd(n);
console.log(pad('equation', 44) + pad('statement', 16) + pad('dim [T L M I Th N J]', 24) + 'dimension-check');
for (const r of eqRows) {
  console.log(pad(r.id.replace('urn:physics-v0:eq:', ''), 44) + pad(r.statement, 16) + pad(r.dim, 24) + (r.ok ? 'EXACT-PASS' : 'FAIL'));
}
console.log(`\n${records.size} records: ${Object.entries(manifest.counts).map(([k, v]) => `${v} ${k}`).join(', ')}`);
console.log(`dimension lane: ${lane.quantityKinds} quantity kinds -> ${lane.distinctVectors} distinct exact vectors; ` +
  `${collisionClasses.length} collision classes (expected, honest): ${collisionClasses.map((c) => c.map((x) => x.split(':').pop()).join('~')).join('; ')}`);
if (failures.length > 0) {
  console.error('\nFAILURES:');
  for (const [id, code, msg] of failures) console.error(`  ${id}: ${code}: ${msg}`);
  process.exit(1);
}
console.log(`ALL PASS — ${byType.DefiningRelation.length}/${byType.DefiningRelation.length} defining relations dimension-check exactly; ` +
  `self-tests (negative + sum accept/reject) green; lane golden matches.`);
