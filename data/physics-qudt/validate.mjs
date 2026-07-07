#!/usr/bin/env node
/**
 * physics-qudt corpus validation harness — extends the physics-v0 gate
 * pattern (data/physics-v0/validate.mjs) to the bulk QUDT-derived corpus.
 * Self-contained, zero deps; ALL definitional arithmetic is exact
 * (BigInt integer 7-vectors; BigInt-rational scale/offset; pi symbolic
 * as an integer exponent). Fail closed with ERR_* codes, exit 1.
 *
 * Gates:
 *   0. corpus shape: JSONL parse, schema, id uniqueness, manifest counts
 *   1. quantity kinds: dim is an exact integer 7-vector (|e| <= expCap),
 *      dimOrder pinned; the asserted QUDT dimension-vector IRI is RECOMPUTED
 *      from dim and must byte-match (mechanical bridge, checked); broader
 *      refs resolve to included kinds
 *   2. units: quantityKind (+otherQuantityKinds) resolve and share one exact
 *      dimension vector; scale/offset parse as exact rationals (floats are a
 *      grammar error by construction); piExponent an integer (|k| <= piCap);
 *      scale > 0; coherentSI <=> (scale=1, offset=0, piExponent=0);
 *      offset != 0 only on the thermodynamic-temperature dimension vector
 *      (dimension-based generalisation of the v0 affine gate)
 *   3. dimension lane: recompute dimension-lane.json and byte-compare
 *      (golden discipline; --write to regenerate deliberately)
 *   4. physics-v0 continuity: every physics-v0 QuantityKind must map into
 *      this corpus via its bridgesTo.qudtQuantityKind, with the SAME exact
 *      dimension vector; the 10 physics-v0 defining relations must
 *      dimension-check EXACTLY against the enlarged (bridge-mapped) set
 *   5. checker integrity: an ill-typed equation must fail; a flipped
 *      exponent must trip the qkdv-IRI recomputation (in-memory self-tests)
 *
 * Usage: node data/physics-qudt/validate.mjs [--write]
 */
import { readFileSync, readdirSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const v0root = join(root, '..', 'physics-v0');
const SCHEMA = 'kot-phys/1';
const DIM_ORDER = ['T', 'L', 'M', 'I', 'Theta', 'N', 'J'];
const failures = [];
const fail = (id, code, msg) => failures.push([id, code, msg]);
// deterministic code-unit string compare (matches the extractor; never localeCompare)
const cmpStr = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

// --- exact rational arithmetic (BigInt) — same grammar as physics-v0 ----------
const bgcd = (a, b) => { a = a < 0n ? -a : a; b = b < 0n ? -b : b; while (b) [a, b] = [b, a % b]; return a; };
const rat = (num, den = 1n) => {
  if (den === 0n) throw new Error('zero denominator');
  if (den < 0n) { num = -num; den = -den; }
  const g = bgcd(num, den) || 1n;
  return { num: num / g, den: den / g };
};
const parseRat = (s) => {
  if (typeof s !== 'string') throw new Error(`rational must be a string, got ${typeof s}`);
  const frac = s.match(/^(-?\d+)\/(\d+)$/);
  if (frac) return rat(BigInt(frac[1]), BigInt(frac[2]));
  const dec = s.match(/^(-?)(\d+)(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/);
  if (!dec) throw new Error(`not an exact-rational literal: ${JSON.stringify(s)}`);
  const [, sign, ip, fp = '', exp = '0'] = dec;
  const num = BigInt(ip + fp) * (sign === '-' ? -1n : 1n);
  const e = BigInt(exp) - BigInt(fp.length);
  return e >= 0n ? rat(num * 10n ** e) : rat(num, 10n ** -e);
};
const ratEq = (a, b) => a.num === b.num && a.den === b.den;
const RAT_ONE = rat(1n);
const RAT_ZERO = rat(0n);

// --- load manifest + records ----------------------------------------------------
const manifest = JSON.parse(readFileSync(join(root, 'manifest.json'), 'utf8'));
const EXP_CAP = BigInt(manifest.expCap);
const PI_CAP = manifest.piCap;
const loadJsonl = (f) => readFileSync(join(root, f), 'utf8').trimEnd().split('\n').map((line, i) => {
  try { return JSON.parse(line); } catch { fail(`${f}:${i + 1}`, 'ERR_JSONL', 'unparseable line'); return null; }
}).filter(Boolean);
const qks = loadJsonl('quantitykinds.jsonl');
const units = loadJsonl('units.jsonl');

const records = new Map();
for (const r of [...qks, ...units]) {
  if (r.schema !== SCHEMA) fail(r.id, 'ERR_SCHEMA', `expected ${SCHEMA}`);
  if (!r.id || records.has(r.id)) fail(r.id ?? '<none>', 'ERR_DUP_ID', 'missing/duplicate id');
  if (!r.provenance?.sourceSha256 || !r.provenance?.extractor || !r.provenance?.extractionDate) {
    fail(r.id, 'ERR_PROVENANCE', 'bulk records must carry a full provenance block (design-bulk-kernel.md)');
  }
  if (r.semanticStatus !== 'AxiomsOnly') fail(r.id, 'ERR_SEMSTATUS', 'bulk tier records are AxiomsOnly');
  records.set(r.id, r);
}
if (manifest.recordCount !== records.size) fail('<manifest>', 'ERR_MANIFEST_COUNT', `${manifest.recordCount} != ${records.size}`);
if (manifest.counts.QuantityKind !== qks.length) fail('<manifest>', 'ERR_MANIFEST_QK', `${manifest.counts.QuantityKind} != ${qks.length}`);
if (manifest.counts.Unit !== units.length) fail('<manifest>', 'ERR_MANIFEST_UNIT', `${manifest.counts.Unit} != ${units.length}`);

// --- gate 1: quantity kinds ------------------------------------------------------
const vecOf = (arr, id) => {
  if (!Array.isArray(arr) || arr.length !== 7) { fail(id, 'ERR_DIM_SHAPE', 'dim must be a 7-array'); return null; }
  const v = [];
  for (const x of arr) {
    if (typeof x !== 'number' || !Number.isSafeInteger(x)) { fail(id, 'ERR_DIM_INT', `non-integer exponent ${x}`); return null; }
    const b = BigInt(x);
    if (b > EXP_CAP || b < -EXP_CAP) { fail(id, 'ERR_DIM_CAP', `|exponent| > ${EXP_CAP}`); return null; }
    v.push(b);
  }
  return v;
};
const vEq = (a, b) => a.every((x, i) => x === b[i]);
// QUDT slot mapping pinned in design-physics-sector.md §3: A=N E=I L=L I=J M=M H=Theta T=T.
const qkdvIri = (v) => {
  const [T, L, M, I, Th, N, J] = v;
  const D = v.every((x) => x === 0n) ? 1 : 0;
  return `http://qudt.org/vocab/dimensionvector/A${N}E${I}L${L}I${J}M${M}H${Th}T${T}D${D}`;
};
const qkDim = new Map();
for (const qk of qks) {
  if (qk.type !== 'QuantityKind') fail(qk.id, 'ERR_TYPE', qk.type);
  const v = vecOf(qk.dim, qk.id);
  if (!v) continue;
  qkDim.set(qk.id, v);
  if (JSON.stringify(qk.dimOrder) !== JSON.stringify(DIM_ORDER)) fail(qk.id, 'ERR_DIM_ORDER', 'dimOrder must equal the pinned order');
  const asserted = qk.bridgesTo?.qudtDimensionVector;
  if (!asserted) fail(qk.id, 'ERR_BRIDGE', 'missing qudtDimensionVector bridge');
  else if (asserted !== qkdvIri(v)) fail(qk.id, 'ERR_QKDV_MISMATCH', `asserted ${asserted} != derived ${qkdvIri(v)}`);
  if (!qk.bridgesTo?.qudtQuantityKind) fail(qk.id, 'ERR_BRIDGE', 'missing qudtQuantityKind bridge');
  for (const b of qk.broader ?? []) {
    if (!qkDimAll(b)) fail(qk.id, 'ERR_BROADER_REF', `broader ${b} unresolved`);
  }
}
function qkDimAll(id) { return records.has(id) && records.get(id).type === 'QuantityKind'; }

// --- gate 2: units -----------------------------------------------------------------
const THETA = [0n, 0n, 0n, 0n, 1n, 0n, 0n];
for (const u of units) {
  if (u.type !== 'Unit') fail(u.id, 'ERR_TYPE', u.type);
  const kinds = [u.quantityKind, ...(u.otherQuantityKinds ?? [])];
  let dim = null;
  for (const k of kinds) {
    const v = qkDim.get(k);
    if (!v) { fail(u.id, 'ERR_REF', `quantityKind ${k} unresolved`); continue; }
    if (dim === null) dim = v;
    else if (!vEq(dim, v)) fail(u.id, 'ERR_UNIT_KIND_DIM', `kinds of one unit must share one exact dimension vector (${k} differs)`);
  }
  let scale, offset;
  try { scale = parseRat(u.scale); offset = parseRat(u.offset); }
  catch (e) { fail(u.id, 'ERR_RATIONAL', e.message); continue; }
  const pi = u.piExponent ?? 0;
  if (!Number.isSafeInteger(pi) || Math.abs(pi) > PI_CAP) fail(u.id, 'ERR_PI_EXP', `piExponent must be an integer with |k| <= ${PI_CAP}`);
  if (pi === 0 && 'piExponent' in u) fail(u.id, 'ERR_PI_ZERO', 'piExponent 0 must be omitted (canonical form)');
  if (scale.num <= 0n) fail(u.id, 'ERR_SCALE_SIGN', 'scale must be positive');
  const coherent = ratEq(scale, RAT_ONE) && ratEq(offset, RAT_ZERO) && pi === 0;
  if (Boolean(u.coherentSI) !== coherent) fail(u.id, 'ERR_COHERENT_FLAG', `coherentSI=${u.coherentSI} but scale=${u.scale} offset=${u.offset} pi=${pi}`);
  if (!ratEq(offset, RAT_ZERO)) {
    if (!dim || !vEq(dim, THETA)) fail(u.id, 'ERR_AFFINE_KIND', 'affine (offset != 0) units admitted only on the thermodynamic-temperature dimension');
    if (pi !== 0) fail(u.id, 'ERR_AFFINE_PI', 'affine units must have piExponent 0');
  }
  if (!u.bridgesTo?.qudtUnit) fail(u.id, 'ERR_BRIDGE', 'missing qudtUnit bridge');
  if (!u.derivation) fail(u.id, 'ERR_DERIVATION', 'unit records must carry their derivation audit trail');
}

// --- gate 3: dimension lane golden ---------------------------------------------------
{
  const laneVectors = {};
  for (const qk of [...qks].sort((a, b) => cmpStr(a.id, b.id))) laneVectors[qk.id] = qk.dim;
  const classes = new Map();
  for (const [id, dim] of Object.entries(laneVectors)) {
    const k = dim.join(',');
    if (!classes.has(k)) classes.set(k, []);
    classes.get(k).push(id);
  }
  const collisionClasses = [...classes.values()].filter((c) => c.length > 1).sort((a, b) => cmpStr(a[0], b[0]));
  const lane = {
    schema: 'kot-phys-dimlane/1',
    note: 'Exact dimension-exponent lane for physics-qudt quantity kinds (integer exponents over the pinned order [T,L,M,I,Theta,N,J]; deterministic; no floats). Metric: L2 only — dimensionless kinds sit at the zero vector where cosine is undefined.',
    dimOrder: DIM_ORDER,
    quantityKinds: Object.keys(laneVectors).length,
    distinctVectors: classes.size,
    collisionClassCount: collisionClasses.length,
    collisionClasses,
    vectors: laneVectors,
  };
  const laneBytes = JSON.stringify(lane, null, 2) + '\n';
  const lanePath = join(root, 'dimension-lane.json');
  if (process.argv.includes('--write') || !existsSync(lanePath)) writeFileSync(lanePath, laneBytes);
  else if (readFileSync(lanePath, 'utf8') !== laneBytes) fail('<lane>', 'ERR_LANE_GOLDEN', 'dimension-lane.json does not match recomputation');
  if (manifest.dimensionLane.distinctVectors !== classes.size) fail('<manifest>', 'ERR_MANIFEST_LANE', 'distinctVectors mismatch');
}

// --- gate 4: physics-v0 continuity (the 10 defining relations, enlarged set) -----------
{
  // index physics-qudt kinds by their QUDT IRI
  const byQudtIri = new Map();
  for (const qk of qks) byQudtIri.set(qk.bridgesTo.qudtQuantityKind, qk);
  // load physics-v0 kinds, constants, equations
  const v0 = { qk: new Map(), constants: new Map(), eqs: [] };
  for (const f of readdirSync(join(v0root, 'quantitykinds')).filter((x) => x.endsWith('.json')).sort()) {
    const doc = JSON.parse(readFileSync(join(v0root, 'quantitykinds', f), 'utf8'));
    v0.qk.set(doc.id, doc);
  }
  for (const f of readdirSync(join(v0root, 'constants')).filter((x) => x.endsWith('.json')).sort()) {
    const doc = JSON.parse(readFileSync(join(v0root, 'constants', f), 'utf8'));
    v0.constants.set(doc.id, doc);
  }
  for (const f of readdirSync(join(v0root, 'equations')).filter((x) => x.endsWith('.json')).sort()) {
    v0.eqs.push(JSON.parse(readFileSync(join(v0root, 'equations', f), 'utf8')));
  }
  // map every v0 kind into the enlarged set; dims must agree EXACTLY
  const mappedDim = new Map(); // v0 qk id -> BigInt vector from the ENLARGED corpus
  let mapped = 0;
  for (const [id, doc] of v0.qk) {
    const iri = doc.bridgesTo?.qudtQuantityKind;
    const target = iri ? byQudtIri.get(iri) : null;
    if (!target) { fail(id, 'ERR_V0_UNMAPPED', `no physics-qudt record bridges to ${iri}`); continue; }
    const enlarged = qkDim.get(target.id);
    const v0dim = vecOf(doc.dim, id);
    if (!v0dim || !enlarged) continue;
    if (!vEq(v0dim, enlarged)) { fail(id, 'ERR_V0_DIM_DRIFT', `v0 dim [${v0dim}] != enlarged ${target.id} dim [${enlarged}]`); continue; }
    mappedDim.set(id, enlarged);
    mapped++;
  }
  // dimension-check the 10 v0 equations against the ENLARGED vectors
  const ZERO7 = [0n, 0n, 0n, 0n, 0n, 0n, 0n];
  const vAdd = (a, b) => a.map((x, i) => x + b[i]);
  const vScale = (a, n) => a.map((x) => x * n);
  const dimOf = (node, depth = 0) => {
    if (depth > 8) throw { code: 'ERR_EQ_DEPTH', message: 'expression deeper than cap 8' };
    switch (node?.kind) {
      case 'quantity': {
        const v = mappedDim.get(node.ref);
        if (!v) throw { code: 'ERR_EQ_REF', message: `quantity ref ${node.ref} not mapped into physics-qudt` };
        return v;
      }
      case 'constant': {
        const c = v0.constants.get(node.ref);
        const v = c && mappedDim.get(c.quantityKind);
        if (!v) throw { code: 'ERR_EQ_REF', message: `constant ref ${node.ref} not mapped` };
        return v;
      }
      case 'scalar': parseRat(node.value); return ZERO7;
      case 'product': return node.factors.map((f) => dimOf(f, depth + 1)).reduce(vAdd);
      case 'power': {
        if (!Number.isSafeInteger(node.exponent) || node.exponent === 0) throw { code: 'ERR_EQ_GRAMMAR', message: 'bad exponent' };
        return vScale(dimOf(node.base, depth + 1), BigInt(node.exponent));
      }
      case 'sum': {
        const dims = node.terms.map((t) => dimOf(t, depth + 1));
        for (const d of dims) if (!vEq(d, dims[0])) throw { code: 'ERR_EQ_SUM_DIM', message: 'mixed-dimension sum' };
        return dims[0];
      }
      default: throw { code: 'ERR_EQ_GRAMMAR', message: `unknown node ${JSON.stringify(node?.kind)}` };
    }
  };
  let eqPass = 0;
  for (const eq of v0.eqs) {
    try {
      const l = dimOf(eq.lhs), r = dimOf(eq.rhs);
      if (vEq(l, r)) eqPass++;
      else fail(eq.id, 'ERR_EQ_DIM', `dim(lhs)=[${l}] != dim(rhs)=[${r}] against the enlarged set`);
    } catch (e) { fail(eq.id, e.code ?? 'ERR_EQ', e.message); }
  }
  console.log(`physics-v0 continuity: ${mapped}/${v0.qk.size} kinds mapped into the enlarged set with identical exact vectors; ` +
    `${eqPass}/${v0.eqs.length} defining relations dimension-check EXACTLY against physics-qudt vectors`);
  if (eqPass !== v0.eqs.length) fail('<v0-eqs>', 'ERR_V0_EQS', `${eqPass}/${v0.eqs.length}`);

  // gate 5a: negative self-test — an ill-typed equation (E = m*c) MUST fail
  try {
    const bad = {
      lhs: { kind: 'quantity', ref: 'urn:physics-v0:qk:energy' },
      rhs: { kind: 'product', factors: [{ kind: 'quantity', ref: 'urn:physics-v0:qk:mass' }, { kind: 'constant', ref: 'urn:physics-v0:const:speed-of-light' }] },
    };
    if (vEq(dimOf(bad.lhs), dimOf(bad.rhs))) fail('<self-test>', 'ERR_SELFTEST_NEG', 'ill-typed E=m*c passed against the enlarged set');
  } catch (e) { fail('<self-test>', 'ERR_SELFTEST_NEG', `self-test could not evaluate: ${e.message}`); }
}

// --- gate 5b: checker integrity — a flipped exponent must trip the qkdv recomputation --
{
  const probe = qks.find((q) => q.dim.some((x) => x !== 0));
  const v = vecOf(probe.dim, probe.id);
  v[0] += 1n;
  if (qkdvIri(v) === probe.bridgesTo.qudtDimensionVector) fail('<self-test>', 'ERR_SELFTEST_QKDV', 'flipped exponent did not change the recomputed qkdv IRI');
}

// --- report -------------------------------------------------------------------------------
console.log(`${records.size} records: ${qks.length} QuantityKind, ${units.length} Unit (source pin: ${manifest.source.release} ${manifest.source.commit.slice(0, 12)})`);
console.log(`dimension lane: ${manifest.dimensionLane.quantityKinds} kinds -> ${manifest.dimensionLane.distinctVectors} distinct exact vectors, ${manifest.dimensionLane.collisionClasses} collision classes (dimensional identity != semantic identity, by design)`);
if (failures.length > 0) {
  console.error('\nFAILURES:');
  for (const [id, code, msg] of failures) console.error(`  ${id}: ${code}: ${msg}`);
  process.exit(1);
}
console.log('ALL PASS — exact-arithmetic gates, qkdv recomputation byte-check, lane golden, v0 continuity (10/10 equations), self-tests green.');
