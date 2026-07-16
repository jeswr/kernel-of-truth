#!/usr/bin/env node
/**
 * validate_shard.mjs — the bounded-shard validator leg of the acceptance
 * stack (spec §4.1 items 1-3, §7.1; ASM-2471/ASM-2477), REUSING the encoder
 * exactly as the explicator pipeline's validator loop does
 * (poc/scale/f1k-explication/validate_pilot.mjs pattern; encoder/dist is the
 * single pinned implementation — never re-typed).
 *
 * Per record: (1) validateExplication (fail-closed ERR_*); (2) catalog-closure
 * lint — every conceptHead/concept ref id must be in the pinned ref catalog
 * (kernel-v0 + molecules-v0), else ERR_REF_OUTSIDE_CATALOG (drafts are leaf
 * nodes of the reference DAG); (3) encodeConceptSet over the shard with the
 * catalog pre-resolved via opts.concepts, no-NaN/positive-norm sanity, then
 * vectors DROPPED (never stored wholesale).
 *
 * Also the P4a instrument: reports wallSec / recordsPerSec / maxRssBytes so
 * the representative B=1,000 shard benchmark is MEASURED, not assumed (§7.1).
 *
 * stdin/argv: --shard file.jsonl ({id, explication} per line) --out out.json
 */
import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  validateExplication,
  encodeConceptSet,
  encoderPin,
  AST_SCHEMA,
} from '../../../../encoder/dist/src/index.js';

const args = process.argv.slice(2);
const arg = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : undefined; };
const shardPath = arg('--shard');
const outPath = arg('--out');
if (!shardPath || !outPath) { console.error('usage: --shard f.jsonl --out r.json'); process.exit(2); }

const repo = join(dirname(fileURLToPath(import.meta.url)), '../../../..');

// ---- pinned ref catalog: kernel-v0 + molecules-v0 ids; kernel-v0 defs encode
const catalogIds = new Set();
const catalogDefs = new Map();
for (const [dir, sub] of [[join(repo, 'data/kernel-v0/concepts'), null],
                          [join(repo, 'data/molecules-v0/molecules'), null]]) {
  for (const f of readdirSync(dir).filter((f) => f.endsWith('.json')).sort()) {
    const doc = JSON.parse(readFileSync(join(dir, f), 'utf8'));
    catalogIds.add(doc.id);
    if (doc.explication?.schema === AST_SCHEMA) catalogDefs.set(doc.id, doc.explication);
  }
}

// encode the catalog ONCE (§7.1), inject via opts.concepts per shard
const t0 = process.hrtime.bigint();
const catalogVectors = encodeConceptSet(catalogDefs).vectors;
const catalogSec = Number(process.hrtime.bigint() - t0) / 1e9;

// ---- collect concept ids referenced by an explication (closure lint)
function refIds(node, out) {
  if (Array.isArray(node)) { node.forEach((n) => refIds(n, out)); return out; }
  if (node && typeof node === 'object') {
    if (node.kind === 'conceptHead' || node.kind === 'concept') out.add(node.id);
    for (const v of Object.values(node)) refIds(v, out);
  }
  return out;
}

const lines = readFileSync(shardPath, 'utf8').split('\n').filter((l) => l.trim());
const records = lines.map((l) => JSON.parse(l));
const perRecord = [];
const encodable = new Map();

const t1 = process.hrtime.bigint();
for (const rec of records) {
  try {
    if (rec.explication?.schema !== AST_SCHEMA) throw Object.assign(new Error('bad schema'), { code: 'ERR_SCHEMA' });
    const stats = validateExplication(rec.explication);
    const refs = refIds(rec.explication, new Set());
    const outside = [...refs].filter((id) => !catalogIds.has(id));
    if (outside.length) {
      // §4.1 item 2: closure enforced at the lint layer (validator accepts any nonempty id)
      throw Object.assign(new Error(`refs outside pinned catalog: ${outside.join(', ')}`), { code: 'ERR_REF_OUTSIDE_CATALOG' });
    }
    // drafts must be leaf nodes: only catalog refs, which opts.concepts resolves
    encodable.set(rec.id, rec.explication);
    perRecord.push({ id: rec.id, ok: true, stats });
  } catch (e) {
    perRecord.push({ id: rec.id, ok: false, code: e.code ?? 'ERR_VALIDATE', detail: String(e.message).slice(0, 200) });
  }
}

// ---- shard encode with catalog injected; vectors dropped after sanity (§7.1)
let encode = { attempted: encodable.size, sane: true, D: 0, failures: [] };
if (encodable.size > 0) {
  try {
    const { vectors } = encodeConceptSet(encodable, { concepts: catalogVectors });
    for (const [id, v] of vectors) {
      if (!encodable.has(id)) continue; // catalog copies
      encode.D = v.length;
      let norm = 0;
      for (const x of v) { if (Number.isNaN(x)) { encode.sane = false; encode.failures.push({ id, code: 'ERR_ENCODE_NAN' }); break; } norm += x * x; }
      if (!(norm > 0) || !Number.isFinite(norm)) { encode.sane = false; encode.failures.push({ id, code: 'ERR_ENCODE_NORM' }); }
    }
    // vectors go out of scope here — dropped, never persisted
  } catch (e) {
    encode.sane = false;
    encode.failures.push({ id: null, code: e.code ?? 'ERR_ENCODE', detail: String(e.message).slice(0, 200) });
  }
}
const wallSec = Number(process.hrtime.bigint() - t1) / 1e9;
if (!encode.sane) {
  // fail closed: mark every record that survived validation but sits in a
  // shard whose encode failed sanity, unless individually named
  const bad = new Set(encode.failures.map((f) => f.id));
  for (const r of perRecord) {
    if (r.ok && (bad.has(r.id) || bad.has(null))) { r.ok = false; r.code = 'ERR_ENCODE_SANITY'; }
  }
}

const result = {
  shard: shardPath,
  records: records.length,
  passed: perRecord.filter((r) => r.ok).length,
  perRecord,
  encode,
  timing: {
    wallSec,
    catalogEncodeSec: catalogSec,
    recordsPerSec: records.length / Math.max(wallSec, 1e-9),
    maxRssBytes: process.resourceUsage().maxRSS * 1024, // linux: maxRSS in KiB
  },
  encoderPin: encoderPin(),
};
writeFileSync(outPath, JSON.stringify(result, null, 1));
console.log(`OK shard=${records.length} pass=${result.passed} rps=${result.timing.recordsPerSec.toFixed(1)} rss=${(result.timing.maxRssBytes / 1048576).toFixed(0)}MiB`);
