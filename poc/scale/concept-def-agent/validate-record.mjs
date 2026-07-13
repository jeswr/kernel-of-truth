#!/usr/bin/env node
/**
 * validate-record.mjs -- mechanical gate for ONE kernel-v1 record produced by
 * the concept-def agent: the pilot's validateExplication path (grammar /
 * valency / referent discipline / caps) + a single-concept encodeConceptSet
 * (D=8192, finite, positive-norm), exactly as validate_pilot.mjs does for the
 * pilot corpus (poc/scale/f1k-explication/validate_pilot.mjs), pointed at one
 * file. Prints a single JSON line; exit 0 iff the record passes.
 *
 * usage: node validate-record.mjs <record.json>
 */
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  validateExplication,
  encodeConceptSet,
  AST_SCHEMA,
} from '../../../encoder/dist/src/index.js';

const out = (o, code) => {
  console.log(JSON.stringify(o));
  process.exit(code);
};

const path = process.argv[2];
if (!path) out({ ok: false, code: 'ERR_USAGE', error: 'usage: validate-record.mjs <record.json>' }, 2);

let doc;
try {
  doc = JSON.parse(readFileSync(path, 'utf8'));
} catch (e) {
  out({ ok: false, code: 'ERR_JSON', error: e.message }, 1);
}

try {
  if (doc.explication?.schema !== AST_SCHEMA) {
    throw Object.assign(new Error(`explication.schema must be '${AST_SCHEMA}'`), { code: 'ERR_SCHEMA' });
  }
  const stats = validateExplication(doc.explication);
  const { vectors } = encodeConceptSet(new Map([[doc.id, doc.explication]]));
  const v = vectors.get(doc.id);
  if (!v) throw Object.assign(new Error('no vector produced'), { code: 'ERR_ENCODE' });
  if (v.some((x) => Number.isNaN(x))) throw Object.assign(new Error('NaN in vector'), { code: 'ERR_ENCODE' });
  const norm = Math.sqrt(v.reduce((a, x) => a + x * x, 0));
  if (!(norm > 0) || !Number.isFinite(norm)) throw Object.assign(new Error('bad norm'), { code: 'ERR_ENCODE' });
  out({ ok: true, stats, D: v.length, norm }, 0);
} catch (e) {
  out({ ok: false, code: e.code ?? null, error: e.message }, 1);
}
