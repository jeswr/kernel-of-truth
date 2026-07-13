#!/usr/bin/env node
/**
 * Validate the kernel-v1 PILOT explications against the encoder's fail-closed
 * gates (per-record validateExplication + whole-corpus encodeConceptSet +
 * vector sanity), exactly as §1.1's mechanical check requires — but pointed at
 * data/kernel-v1-pilot/ (design says parameterize data/validate.mjs with
 * --kernel; here we do it out-of-tree so the pilot touches nothing else).
 */
import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  validateExplication,
  encodeConceptSet,
  AST_SCHEMA,
} from '../../../encoder/dist/src/index.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '../../../data/kernel-v1-pilot');
const dir = join(root, 'concepts');
const files = readdirSync(dir).filter((f) => f.endsWith('.json')).sort();
const concepts = files.map((f) => ({ file: f, doc: JSON.parse(readFileSync(join(dir, f), 'utf8')) }));

let pass = 0;
const rows = [];
for (const { file, doc } of concepts) {
  try {
    if (doc.explication?.schema !== AST_SCHEMA) throw new Error(`bad schema`);
    const stats = validateExplication(doc.explication);
    rows.push([file, 'OK', `clauses=${stats.clauseCount} depth=${stats.maxDepth} refs=${stats.referentCount}`]);
    pass++;
  } catch (e) {
    rows.push([file, 'FAIL', `${e.code ?? ''} ${e.message}`]);
  }
}

// whole-corpus encode (no cross-refs in the pilot, but exercises the encoder)
let encodeStatus = 'OK';
try {
  const defs = new Map(concepts.map(({ doc }) => [doc.id, doc.explication]));
  const { vectors } = encodeConceptSet(defs);
  const D = vectors.get(concepts[0].doc.id)?.length ?? 0;
  for (const [, v] of vectors) {
    if (v.some((x) => Number.isNaN(x))) throw new Error('NaN in vector');
    const norm = Math.sqrt(v.reduce((a, x) => a + x * x, 0));
    if (!(norm > 0) || !Number.isFinite(norm)) throw new Error('bad norm');
  }
  encodeStatus = `OK (D=${D}, ${vectors.size} vectors, finite + positive-norm)`;
} catch (e) {
  encodeStatus = `FAIL ${e.code ?? ''} ${e.message}`;
}

for (const [f, s, d] of rows) console.log(`${s === 'OK' ? '✓' : '✗'} ${f.padEnd(22)} ${s}  ${d}`);
console.log(`\nvalidateExplication: ${pass}/${concepts.length} pass`);
console.log(`encodeConceptSet:    ${encodeStatus}`);
process.exit(pass === concepts.length && encodeStatus.startsWith('OK') ? 0 : 1);
