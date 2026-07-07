#!/usr/bin/env node
/**
 * math-v0 corpus validation harness (profile-M v0, pm-ast/1).
 *
 * Self-contained (zero deps) implementation of the profile-M v0 gates from
 * docs/design-math-sector.md §3:
 *   1. corpus shape: unique ids, pm-ast/1 schema, closed frame inventory;
 *   2. grammar: closed node-kind inventory, closed primitive table, frame
 *      field shapes;
 *   3. sorts: a full checker for the §3.2 typing obligations (de Bruijn
 *      contexts; eq/member/pair/comprehension rules; RecursiveFunctionDef
 *      base/step contexts — primitive recursion, guarded by construction);
 *   4. binding: de Bruijn scope (index < depth), vacuous-binder rejection
 *      for forall/exists/comprehension (§3.4);
 *   5. caps (§3.3): nodes ≤256, binder depth ≤12, params ≤6, sort depth ≤4,
 *      refs ≤16;
 *   6. references: recomputed-from-AST vs declared, resolution, DAG only,
 *      reference depth;
 *   7. NSM bridges: shape always; prime names + explication legality checked
 *      against the profile-1 encoder (encoder/dist) WHEN BUILT, else
 *      warn-and-skip (the pm-ast gates above never depend on the encoder);
 *   8. manifest cross-checks.
 *
 * Vector encoding is deliberately NOT performed: the construction B-M encoder
 * variant is a filed follow-up (design §4), so unlike data/validate.mjs this
 * harness pins no encoder content-hash.
 *
 * Usage: node data/math-v0/validate.mjs        Exit 0 iff all records pass.
 */
import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const manifest = JSON.parse(readFileSync(join(root, 'manifest.json'), 'utf8'));
const files = readdirSync(join(root, 'concepts')).filter((f) => f.endsWith('.json')).sort();
const failures = [];
const fail = (id, code, msg) => failures.push([id, code, msg]);

// --- profile-M v0 closed inventories (design §2.2, §3.2, §3.3) -------------
const FRAMES = ['Primitive', 'AxiomDef', 'TermDef', 'PredicateDef', 'RecursiveFunctionDef'];
const PRIMITIVES = [
  'natural-number', 'zero', 'successor', 'equality', 'set-membership',
  'set-of', 'ordered-pair', 'pair-first', 'pair-second',
];
const STATUSES = ['primitive', 'axiom', 'core', 'sketch'];
const CAPS = { maxNodes: 256, maxBinderDepth: 12, maxParams: 6, maxSortDepth: 4, maxRefs: 16 };

// --- sorts -----------------------------------------------------------------
const isN = (s) => s === 'N';
function sortDepth(s) {
  if (isN(s)) return 0;
  if (s && s.kind === 'Set') return 1 + sortDepth(s.of);
  if (s && s.kind === 'Pair') return 1 + Math.max(sortDepth(s.fst), sortDepth(s.snd));
  return NaN;
}
function sortValid(s) { return !Number.isNaN(sortDepth(s)); }
function sortEq(a, b) {
  if (isN(a) || isN(b)) return a === b;
  if (a.kind !== b.kind) return false;
  if (a.kind === 'Set') return sortEq(a.of, b.of);
  return sortEq(a.fst, b.fst) && sortEq(a.snd, b.snd);
}
const showSort = (s) => (isN(s) ? 'N' : s.kind === 'Set' ? `Set(${showSort(s.of)})` : `Pair(${showSort(s.fst)},${showSort(s.snd)})`);
const PROP = Symbol('Prop');

// --- signatures of const-referenceable concepts ------------------------------
const docs = files.map((f) => ({ file: f, doc: JSON.parse(readFileSync(join(root, 'concepts', f), 'utf8')) }));
const byId = new Map(docs.map(({ doc }) => [doc.id, doc]));
function signatureOf(id) {
  const d = byId.get(id);
  if (!d) return null;
  const def = d.definition;
  if (def.frame === 'TermDef' || def.frame === 'RecursiveFunctionDef') {
    return { params: def.params ?? [], result: def.resultSort };
  }
  if (def.frame === 'PredicateDef') return { params: def.params, result: PROP };
  return { unreferenceable: def.frame }; // Primitive (a grammar former), AxiomDef (not a term)
}

// --- term checker ------------------------------------------------------------
// ctx: array of sorts, index 0 = innermost binder. Returns sort | PROP | null.
function checkTerm(id, t, ctx, state, path) {
  state.nodes += 1;
  if (state.nodes > CAPS.maxNodes) { fail(id, 'ERR_CAP_NODES', `> ${CAPS.maxNodes} term nodes`); return null; }
  if (t === null || typeof t !== 'object' || Array.isArray(t)) { fail(id, 'ERR_NODE_SHAPE', `${path}: not an object`); return null; }
  const sub = (u, p) => checkTerm(id, u, ctx, state, p);
  switch (t.kind) {
    case 'var': {
      if (!Number.isInteger(t.index) || t.index < 0) { fail(id, 'ERR_VAR_INDEX', `${path}: bad index`); return null; }
      if (t.index >= ctx.length) { fail(id, 'ERR_VAR_SCOPE', `${path}: de Bruijn index ${t.index} exceeds binder depth ${ctx.length}`); return null; }
      state.used.add(ctx.length - 1 - t.index); // absolute binder id, for vacuity checks
      return ctx[t.index];
    }
    case 'zero': return 'N';
    case 'succ': {
      const a = sub(t.arg, `${path}.arg`);
      if (a !== null && !(a !== PROP && isN(a))) fail(id, 'ERR_SORT', `${path}: succ needs N, got ${a === PROP ? 'Prop' : showSort(a)}`);
      return 'N';
    }
    case 'eq': {
      const l = sub(t.left, `${path}.left`); const r = sub(t.right, `${path}.right`);
      if (l === PROP || r === PROP) { fail(id, 'ERR_SORT', `${path}: eq over Prop is not licensed (use iff)`); return PROP; }
      if (l !== null && r !== null && !sortEq(l, r)) fail(id, 'ERR_SORT', `${path}: eq operands differ (${showSort(l)} vs ${showSort(r)})`);
      return PROP;
    }
    case 'member': {
      const e = sub(t.element, `${path}.element`); const s = sub(t.set, `${path}.set`);
      if (s !== null && (s === PROP || isN(s) || s.kind !== 'Set')) fail(id, 'ERR_SORT', `${path}: member's set operand is not a Set sort`);
      else if (e !== null && s !== null && (e === PROP || !sortEq(s.of, e))) fail(id, 'ERR_SORT', `${path}: member element/set sort mismatch`);
      return PROP;
    }
    case 'pair': {
      const a = sub(t.fst, `${path}.fst`); const b = sub(t.snd, `${path}.snd`);
      if (a === null || b === null || a === PROP || b === PROP) { if (a === PROP || b === PROP) fail(id, 'ERR_SORT', `${path}: pair over Prop`); return null; }
      return { kind: 'Pair', fst: a, snd: b };
    }
    case 'fst': case 'snd': {
      const a = sub(t.arg, `${path}.arg`);
      if (a === null) return null;
      if (a === PROP || isN(a) || a.kind !== 'Pair') { fail(id, 'ERR_SORT', `${path}: ${t.kind} needs a Pair sort`); return null; }
      return t.kind === 'fst' ? a.fst : a.snd;
    }
    case 'not': {
      const a = sub(t.arg, `${path}.arg`);
      if (a !== null && a !== PROP) fail(id, 'ERR_SORT', `${path}: not over non-Prop`);
      return PROP;
    }
    case 'and': case 'or': case 'implies': case 'iff': {
      for (const side of ['left', 'right']) {
        const a = sub(t[side], `${path}.${side}`);
        if (a !== null && a !== PROP) fail(id, 'ERR_SORT', `${path}.${side}: ${t.kind} over non-Prop`);
      }
      return PROP;
    }
    case 'forall': case 'exists': case 'comprehension': {
      if (!sortValid(t.sort)) { fail(id, 'ERR_SORT_FORM', `${path}: invalid binder sort`); return null; }
      if (sortDepth(t.sort) > CAPS.maxSortDepth) fail(id, 'ERR_CAP_SORT_DEPTH', `${path}: sort depth > ${CAPS.maxSortDepth}`);
      if (ctx.length + 1 > CAPS.maxBinderDepth) fail(id, 'ERR_CAP_BINDER_DEPTH', `${path}: binder depth > ${CAPS.maxBinderDepth}`);
      const binderId = ctx.length; // absolute id of this binder
      const body = checkTerm(id, t.body, [t.sort, ...ctx], state, `${path}.body`);
      if (body !== null && body !== PROP) fail(id, 'ERR_SORT', `${path}.body: binder body must be Prop`);
      if (!state.used.has(binderId)) fail(id, 'ERR_VACUOUS_BINDER', `${path}: ${t.kind} binds no occurrence (design §3.4)`);
      state.used.delete(binderId);
      return t.kind === 'comprehension' ? { kind: 'Set', of: t.sort } : PROP;
    }
    case 'const': {
      if (typeof t.ref !== 'string' || !t.ref.startsWith('urn:math-v0:')) { fail(id, 'ERR_REF_FORM', `${path}: bad ref '${t.ref}'`); return null; }
      state.refs.add(t.ref);
      const sig = signatureOf(t.ref);
      if (sig === null) { fail(id, 'ERR_REF_UNRESOLVED', `${path}: ${t.ref} not in corpus`); return null; }
      if (sig.unreferenceable) { fail(id, 'ERR_REF_FRAME', `${path}: ${t.ref} is a ${sig.unreferenceable} record and cannot be const-applied`); return null; }
      const args = Array.isArray(t.args) ? t.args : (fail(id, 'ERR_NODE_SHAPE', `${path}: const.args must be an array`), []);
      if (args.length !== sig.params.length) fail(id, 'ERR_ARITY', `${path}: ${t.ref} expects ${sig.params.length} args, got ${args.length}`);
      args.forEach((a, i) => {
        const got = sub(a, `${path}.args[${i}]`);
        const want = sig.params[i];
        if (got !== null && want !== undefined && (got === PROP || !sortEq(got, want))) {
          fail(id, 'ERR_SORT', `${path}.args[${i}]: expected ${showSort(want)}, got ${got === PROP ? 'Prop' : showSort(got)}`);
        }
      });
      return sig.result;
    }
    default:
      fail(id, 'ERR_NODE_KIND', `${path}: unknown node kind '${t.kind}'`);
      return null;
  }
}

function checkParams(id, params, where) {
  if (!Array.isArray(params)) { fail(id, 'ERR_FRAME_SHAPE', `${where}: params must be an array`); return false; }
  if (params.length > CAPS.maxParams) fail(id, 'ERR_CAP_PARAMS', `${where}: > ${CAPS.maxParams} params`);
  let ok = true;
  params.forEach((p, i) => {
    if (!sortValid(p)) { fail(id, 'ERR_SORT_FORM', `${where}.params[${i}]: invalid sort`); ok = false; }
    else if (sortDepth(p) > CAPS.maxSortDepth) fail(id, 'ERR_CAP_SORT_DEPTH', `${where}.params[${i}]`);
  });
  return ok;
}
// params pushed left→right: last param = de Bruijn index 0.
const paramCtx = (params) => [...params].reverse();

// --- gate 0+1+2: per-record shape, grammar, sorts ----------------------------
const ids = new Set();
const rows = [];
for (const { file, doc } of docs) {
  const id = doc.id ?? `<${file}>`;
  if (!doc.id || ids.has(doc.id)) fail(id, 'ERR_CORPUS_ID', `missing/duplicate id in ${file}`);
  ids.add(doc.id);
  if (!STATUSES.includes(doc.status)) fail(id, 'ERR_CORPUS_STATUS', `unknown status '${doc.status}'`);
  const def = doc.definition;
  if (!def || def.schema !== 'pm-ast/1') { fail(id, 'ERR_CORPUS_SCHEMA', 'definition.schema must be pm-ast/1'); continue; }
  if (!FRAMES.includes(def.frame)) { fail(id, 'ERR_FRAME', `unknown frame '${def.frame}'`); continue; }

  const state = { nodes: 0, refs: new Set(), used: new Set() };
  switch (def.frame) {
    case 'Primitive':
      if (!PRIMITIVES.includes(def.primitive)) fail(id, 'ERR_PRIMITIVE_UNKNOWN', `'${def.primitive}' not in the closed basis table`);
      if (def.definiens || def.statement || def.params) fail(id, 'ERR_FRAME_SHAPE', 'Primitive records carry no definition tree');
      break;
    case 'AxiomDef': {
      const s = checkTerm(id, def.statement, [], state, 'statement');
      if (s !== null && s !== PROP) fail(id, 'ERR_SORT', 'axiom statement must be a closed Prop term');
      for (const c of doc.characterizes ?? []) {
        if (!byId.has(c)) fail(id, 'ERR_CHARACTERIZES', `${c} not in corpus`);
      }
      break;
    }
    case 'TermDef': {
      if (!checkParams(id, def.params ?? [], 'TermDef')) break;
      if (!sortValid(def.resultSort)) { fail(id, 'ERR_SORT_FORM', 'TermDef.resultSort invalid'); break; }
      const s = checkTerm(id, def.definiens, paramCtx(def.params ?? []), state, 'definiens');
      if (s !== null && (s === PROP || !sortEq(s, def.resultSort))) {
        fail(id, 'ERR_SORT', `definiens : ${s === PROP ? 'Prop' : showSort(s)} but resultSort is ${showSort(def.resultSort)}`);
      }
      break;
    }
    case 'PredicateDef': {
      if (!Array.isArray(def.params) || def.params.length < 1) { fail(id, 'ERR_FRAME_SHAPE', 'PredicateDef needs ≥1 param'); break; }
      if (!checkParams(id, def.params, 'PredicateDef')) break;
      const s = checkTerm(id, def.definiens, paramCtx(def.params), state, 'definiens');
      if (s !== null && s !== PROP) fail(id, 'ERR_SORT', 'PredicateDef definiens must be Prop');
      break;
    }
    case 'RecursiveFunctionDef': {
      if (!Array.isArray(def.params) || def.params.length < 1 || !isN(def.params[def.params.length - 1])) {
        fail(id, 'ERR_FRAME_SHAPE', 'RecursiveFunctionDef recurses on its last param, which must be N'); break;
      }
      if (!checkParams(id, def.params, 'RecursiveFunctionDef')) break;
      if (!sortValid(def.resultSort)) { fail(id, 'ERR_SORT_FORM', 'resultSort invalid'); break; }
      const front = def.params.slice(0, -1);
      const b = checkTerm(id, def.baseCase, paramCtx(front), state, 'baseCase');
      if (b !== null && (b === PROP || !sortEq(b, def.resultSort))) fail(id, 'ERR_SORT', 'baseCase sort ≠ resultSort');
      // step context: front params, then n : N (index 1), then rec : resultSort (index 0)
      const s = checkTerm(id, def.stepCase, [def.resultSort, 'N', ...paramCtx(front)], state, 'stepCase');
      if (s !== null && (s === PROP || !sortEq(s, def.resultSort))) fail(id, 'ERR_SORT', 'stepCase sort ≠ resultSort');
      break;
    }
  }

  // references: recomputed vs declared; caps
  if (state.refs.size > CAPS.maxRefs) fail(id, 'ERR_CAP_REFS', `> ${CAPS.maxRefs} concept references`);
  const declared = JSON.stringify([...(doc.references ?? [])].sort());
  const walked = JSON.stringify([...state.refs].sort());
  if (declared !== walked) fail(id, 'ERR_CORPUS_REFS', `declared references ${declared} ≠ AST walk ${walked}`);
  rows.push({ id, file, frame: def.frame, status: doc.status, nodes: state.nodes, refs: state.refs.size, bridge: doc.nsmBridge?.kind ?? '-' });
}

// --- gate 3: reference DAG + depth ------------------------------------------
const depths = new Map();
function refDepth(id, stack = []) {
  if (depths.has(id)) return depths.get(id);
  if (stack.includes(id)) { fail(id, 'ERR_REF_CYCLE', `reference cycle: ${[...stack, id].join(' -> ')}`); return 0; }
  const doc = byId.get(id);
  const refs = doc?.references ?? [];
  const d = refs.length === 0 ? 0 : 1 + Math.max(...refs.map((r) => (byId.has(r) ? refDepth(r, [...stack, id]) : 0)));
  depths.set(id, d);
  return d;
}
let maxDepth = 0; let maxDepthId = null;
for (const { doc } of docs) { const d = refDepth(doc.id); if (d > maxDepth) { maxDepth = d; maxDepthId = doc.id; } }

// --- gate 4: NSM bridges ------------------------------------------------------
let encoderApi = null;
try {
  encoderApi = await import('../../encoder/dist/src/index.js');
} catch {
  console.warn('NOTE: encoder/dist not built — NSM bridge prime-name/explication legality checks SKIPPED (shape checks still run).');
  console.warn('      Build with: (cd encoder && npm install && npm run build)');
}
const primeNames = encoderApi ? new Set(encoderApi.PRIMES.map((p) => p.name)) : null;
for (const { doc } of docs) {
  const b = doc.nsmBridge;
  if (!b || !['prime', 'explication', 'none'].includes(b.kind)) { fail(doc.id, 'ERR_BRIDGE', 'nsmBridge must be prime|explication|none'); continue; }
  if (typeof b.note !== 'string' || b.note.length === 0) fail(doc.id, 'ERR_BRIDGE', 'every nsmBridge carries an honest note');
  if (b.kind === 'prime') {
    if (primeNames && !primeNames.has(b.prime)) fail(doc.id, 'ERR_BRIDGE_PRIME', `'${b.prime}' is not a 65-prime lexicon name`);
    if (!primeNames && typeof b.prime !== 'string') fail(doc.id, 'ERR_BRIDGE_PRIME', 'prime bridge missing prime name');
  }
  if (b.kind === 'explication') {
    if (!b.explication || b.explication.schema !== 'kot-ast/1') fail(doc.id, 'ERR_BRIDGE', 'explication bridge must carry a kot-ast/1 record');
    else if (encoderApi) {
      try { encoderApi.validateExplication(b.explication); }
      catch (e) { fail(doc.id, e.code ?? 'ERR_BRIDGE_EXPLICATION', `profile-1 gate rejected bridge explication: ${e.message}`); }
    }
    if (!/KNOWN-WEAK/.test(b.note)) fail(doc.id, 'ERR_BRIDGE', 'explication bridges are research-grade and must say KNOWN-WEAK in the note');
  }
}

// --- gate 5: manifest cross-checks --------------------------------------------
if (manifest.conceptCount !== docs.length) fail('<manifest>', 'ERR_MANIFEST_COUNT', `${manifest.conceptCount} ≠ ${docs.length}`);
const frameTally = {};
for (const r of rows) frameTally[r.frame] = (frameTally[r.frame] ?? 0) + 1;
const sortedObj = (o) => JSON.stringify(Object.fromEntries(Object.entries(o).sort()));
if (sortedObj(manifest.frames) !== sortedObj(frameTally)) fail('<manifest>', 'ERR_MANIFEST_FRAMES', `frames ${sortedObj(manifest.frames)} ≠ tally ${sortedObj(frameTally)}`);
const refBearing = docs.filter(({ doc }) => (doc.references ?? []).length > 0).map(({ doc }) => doc.id);
if (manifest.referenceBearingCount !== refBearing.length) fail('<manifest>', 'ERR_MANIFEST_REFS', `referenceBearingCount ${manifest.referenceBearingCount} ≠ ${refBearing.length}`);
if (JSON.stringify([...manifest.referenceBearing].sort()) !== JSON.stringify(refBearing.sort())) fail('<manifest>', 'ERR_MANIFEST_REFS', 'referenceBearing list mismatch');
if (manifest.maxReferenceDepth !== maxDepth) fail('<manifest>', 'ERR_MANIFEST_DEPTH', `maxReferenceDepth ${manifest.maxReferenceDepth} ≠ computed ${maxDepth} (witness ${maxDepthId})`);
for (const m of manifest.concepts ?? []) {
  if (!byId.has(m.id)) fail('<manifest>', 'ERR_MANIFEST_ID', `${m.id} listed but not on disk`);
}

// --- report --------------------------------------------------------------------
const pad = (s, n) => String(s).padEnd(n);
console.log(pad('concept', 30) + pad('frame', 24) + pad('status', 11) + pad('nodes', 7) + pad('crefs', 7) + pad('bridge', 13) + 'result');
for (const r of rows.sort((a, b) => a.id.localeCompare(b.id))) {
  const bad = failures.some(([fid]) => fid === r.id);
  console.log(pad(r.id.replace('urn:math-v0:', ''), 30) + pad(r.frame, 24) + pad(r.status, 11) + pad(r.nodes, 7) + pad(r.refs, 7) + pad(r.bridge, 13) + (bad ? 'FAIL' : 'PASS'));
}
console.log(`\n${docs.length} concepts; frames=${JSON.stringify(frameTally)}; reference-bearing=${refBearing.length}; maxReferenceDepth=${maxDepth} (${maxDepthId})`);
if (failures.length > 0) {
  console.error('\nFAILURES:');
  for (const [id, code, msg] of failures) console.error(`  ${id}: ${code}: ${msg}`);
  process.exit(1);
}
console.log(`ALL PASS — ${docs.length}/${docs.length} records validate (pm-ast/1 gates${encoderApi ? ' + profile-1 bridge gates' : '; bridge deep-checks skipped'}). Vector encoding: not performed (design §4 follow-up).`);
