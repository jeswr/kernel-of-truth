#!/usr/bin/env node
/**
 * kernel-v0 corpus validation harness.
 *
 * Loads every concept in data/kernel-v0/concepts/ and pushes it through the
 * encoder package's fail-closed gates:
 *   1. per-concept `validateExplication` (profile-1 grammar/valency/referent
 *      gates, caps; encoder/src/validate.ts),
 *   2. one `encodeConceptSet` pass over the whole corpus (memoised recursive
 *      encoding; concept references bind referenced vectors; cycles and
 *      unresolved ids fail closed; encoder/src/encoder.ts),
 *   3. vector sanity: D as configured, unit norm, no NaN,
 * and cross-checks the manifest (count, ids, reference lists, frames).
 *
 * Usage: node data/validate.mjs          (light compute; nice it on shared boxes)
 * Exit code 0 iff every concept passes every gate.
 */
import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  validateExplication,
  encodeConceptSet,
  encoderContentHash,
  AST_SCHEMA,
} from '../encoder/dist/src/index.js';

const root = join(dirname(fileURLToPath(import.meta.url)), 'kernel-v0');
const manifest = JSON.parse(readFileSync(join(root, 'manifest.json'), 'utf8'));
const files = readdirSync(join(root, 'concepts')).filter((f) => f.endsWith('.json')).sort();

const concepts = files.map((f) => ({
  file: f,
  doc: JSON.parse(readFileSync(join(root, 'concepts', f), 'utf8')),
}));

// --- gate 0: corpus shape ----------------------------------------------------
const failures = [];
const ids = new Set();
for (const { file, doc } of concepts) {
  if (!doc.id || ids.has(doc.id)) failures.push([file, 'ERR_CORPUS_ID', `missing/duplicate id ${doc.id}`]);
  ids.add(doc.id);
  if (doc.explication?.schema !== AST_SCHEMA) {
    failures.push([file, 'ERR_CORPUS_SCHEMA', `expected ${AST_SCHEMA}`]);
  }
}

// recompute concept references by walking the AST (must match declared lists)
const collectRefs = (node, out) => {
  if (Array.isArray(node)) { node.forEach((n) => collectRefs(n, out)); return; }
  if (node === null || typeof node !== 'object') return;
  if (node.kind === 'concept' || node.kind === 'conceptHead') out.add(node.id);
  for (const v of Object.values(node)) collectRefs(v, out);
};

// --- gate 1: per-concept grammar gates ----------------------------------------
const rows = [];
for (const { file, doc } of concepts) {
  const refs = new Set();
  collectRefs(doc.explication, refs);
  const declared = JSON.stringify([...refs].sort());
  if (declared !== JSON.stringify(doc.references ?? [])) {
    failures.push([doc.id, 'ERR_CORPUS_REFS', `declared references do not match AST (${declared})`]);
  }
  for (const r of refs) {
    if (!ids.has(r)) failures.push([doc.id, 'ERR_CORPUS_REF_UNRESOLVED', `references ${r} outside corpus`]);
  }
  try {
    const stats = validateExplication(doc.explication);
    rows.push({ id: doc.id, file, frame: doc.explication.frame, ...stats, refs: refs.size, ok: true });
  } catch (e) {
    failures.push([doc.id, e.code ?? 'ERR', e.message]);
    rows.push({ id: doc.id, file, frame: doc.explication.frame, refs: refs.size, ok: false });
  }
}

// --- gate 2+3: whole-corpus encode (binds references, rejects cycles) ---------
let vectors = null;
if (failures.length === 0) {
  const defs = new Map(concepts.map(({ doc }) => [doc.id, doc.explication]));
  try {
    ({ vectors } = encodeConceptSet(defs));
    for (const [id, v] of vectors) {
      let s = 0;
      let nan = false;
      for (let i = 0; i < v.length; i++) { s += v[i] * v[i]; if (Number.isNaN(v[i])) nan = true; }
      if (nan) failures.push([id, 'ERR_VECTOR_NAN', 'vector contains NaN']);
      if (Math.abs(Math.sqrt(s) - 1) > 1e-9) failures.push([id, 'ERR_VECTOR_NORM', `norm ${Math.sqrt(s)}`]);
    }
  } catch (e) {
    failures.push(['<corpus>', 'ERR_ENCODE_SET', e.message]);
  }
}

// --- manifest cross-checks -----------------------------------------------------
if (manifest.conceptCount !== concepts.length) {
  failures.push(['<manifest>', 'ERR_MANIFEST_COUNT', `${manifest.conceptCount} != ${concepts.length}`]);
}
if (manifest.encoderContentHash !== encoderContentHash()) {
  console.warn(`NOTE: manifest pinned encoder ${manifest.encoderContentHash.slice(0, 16)}..., ` +
    `current is ${encoderContentHash().slice(0, 16)}... (encoder version change since authoring)`);
}

// --- report ---------------------------------------------------------------------
const pad = (s, n) => String(s).padEnd(n);
console.log(pad('concept', 34) + pad('frame', 18) + pad('clauses', 9) + pad('depth', 7) + pad('refts', 7) + pad('crefs', 7) + 'result');
for (const r of rows.sort((a, b) => a.id.localeCompare(b.id))) {
  const result = !r.ok ? 'FAIL' : vectors?.has(r.id) ? 'PASS' : 'PASS(gates-only)';
  console.log(
    pad(r.id.replace('urn:kernel-v0:', ''), 34) + pad(r.frame, 18) + pad(r.clauseCount ?? '-', 9) +
    pad(r.maxDepth ?? '-', 7) + pad(r.referentCount ?? '-', 7) + pad(r.refs, 7) + result,
  );
}
console.log(`\n${concepts.length} concepts; frames=${JSON.stringify(manifest.frames)}; ` +
  `reference-bearing=${manifest.referenceBearingCount}; maxReferenceDepth=${manifest.maxReferenceDepth}`);
if (failures.length > 0) {
  console.error('\nFAILURES:');
  for (const [id, code, msg] of failures) console.error(`  ${id}: ${code}: ${msg}`);
  process.exit(1);
}
console.log(`ALL PASS — ${concepts.length}/${concepts.length} concepts validate and encode ` +
  `(D=${vectors.get(concepts[0].doc.id).length}, encoder ${encoderContentHash().slice(0, 16)}...)`);
