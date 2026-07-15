#!/usr/bin/env node
/**
 * build_manifest.mjs -- assembles the S5 referenceable-lexicon manifest
 * (poc/scale/molecule-aug/DESIGN.md §3.3.6, lexicon/PLAN.md).
 *
 * Does, fail-closed:
 *   1. verify the running encoder's content hash equals the kernel-v0 pin
 *      (no ALGORITHM_VERSION bump allowed in the cheap tier, DESIGN §9);
 *   2. load the 54 kernel-v0 records + the 31 bridge records (exact PLAN list,
 *      urn:molaug-v0 namespace, record shape, AST-adequacy self-flag);
 *   3. reference policy per bridge record: references == AST concept ids
 *      (sorted), <=8, no self-ref, targets = kernel-v0 ids + STRICTLY EARLIER
 *      bridge rows only (PLAN topological order);
 *   4. encode ALL 85 explications in one encodeConceptSet pass; every vector
 *      must be D=8192, unit-norm, NaN-free;
 *   5. anti-leakage gate (DESIGN §3.4): no lexicon slug collides with any of
 *      the 100 consensus-100 eval-concept slugs (lemma collisions are
 *      reported as warnings); the Stage-2 held-out sample is checked too when
 *      s5-run/stage2-heldout.json exists;
 *   6. emit manifest.json (per-record sha256, lexiconSetHash = sha256 of the
 *      sorted "id:sha256" lines over all 85, encoder content hash) and
 *      listing.txt (85 lines "id — label: first-sentence gloss", sorted by id)
 *      so the S5 prompt and the manifest can never drift apart.
 *
 * usage: node lexicon/build_manifest.mjs   (from poc/scale/molecule-aug/)
 * Exit 0 iff everything gates green. Author: fable (lead designer/explicator).
 */
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  validateExplication,
  encodeConceptSet,
  encoderContentHash,
  AST_SCHEMA,
} from '../../../../encoder/dist/src/index.js';

const HERE = dirname(fileURLToPath(import.meta.url)); // .../molecule-aug/lexicon
const ROOT = join(HERE, '../../../..');
const KV0 = join(ROOT, 'data/kernel-v0');
const C100 = join(ROOT, 'poc/scale/consensus-100/concepts-100.json');
const HELDOUT = join(HERE, '../s5-run/stage2-heldout.json');
const FRESH3 = join(HERE, '../s5-run/stage3-fresh.json'); // DESIGN-v2 §4.3
const MAX_REFS = 8;

// PLAN.md topological authoring order (frozen design artefact; do not reorder).
const PLAN_ORDER = [
  'money', 'surface', 'hot', 'material', 'group', 'fight', 'measure', 'kill',
  'animal', 'eat', 'food', 'grow', 'name', 'write', 'own', 'ill', 'man',
  'woman', 'sex', 'work', 'status', 'authority', 'law', 'country',
  'institution', 'duty', 'worth', 'tool', 'machine', 'art', 'game',
];

const sha256 = (b) => createHash('sha256').update(b).digest('hex');
const die = (msg) => { console.error(`BUILD_MANIFEST_ABORT: ${msg}`); process.exit(1); };
// Frozen slug rule (concept-def-prompt.md §2 / define_concept.py slugify).
const slugify = (s) => s.toLowerCase().replace(/['’]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');

function conceptIds(node, acc) {
  if (node === null || typeof node !== 'object') return acc;
  if (Array.isArray(node)) { for (const x of node) conceptIds(x, acc); return acc; }
  if ((node.kind === 'concept' || node.kind === 'conceptHead') && typeof node.id === 'string') acc.add(node.id);
  for (const v of Object.values(node)) conceptIds(v, acc);
  return acc;
}

// -- 1. encoder pin -----------------------------------------------------------
const kv0Manifest = JSON.parse(readFileSync(join(KV0, 'manifest.json'), 'utf8'));
const liveHash = encoderContentHash();
if (liveHash !== kv0Manifest.encoderContentHash) {
  die(`encoder content hash ${liveHash} != kernel-v0 pin ${kv0Manifest.encoderContentHash} -- ` +
      'the cheap tier requires the pinned encoder (DESIGN.md §9); rebuild/downgrade before assembling the lexicon');
}

// -- 2. load records ----------------------------------------------------------
const entries = []; // {id, label, gloss, file(abs), rel, raw, doc, tier}
for (const c of kv0Manifest.concepts) {
  const abs = join(KV0, c.file);
  const raw = readFileSync(abs, 'utf8');
  const doc = JSON.parse(raw);
  if (doc.id !== c.id) die(`kernel-v0 manifest/file id mismatch: ${c.id} vs ${doc.id}`);
  entries.push({ id: doc.id, label: doc.label, gloss: doc.gloss, rel: `data/kernel-v0/${c.file}`, raw, doc, tier: 'kernel-v0' });
}
if (entries.length !== 54) die(`expected 54 kernel-v0 records, got ${entries.length}`);

const REQUIRED_FIELDS = ['id', 'label', 'status', 'pattern', 'gloss', 'notes', 'references', 'explication'];
const bridgeIds = PLAN_ORDER.map((s) => `urn:molaug-v0:${s}`);
const selfFlags = {};
for (const [i, slug] of PLAN_ORDER.entries()) {
  const abs = join(HERE, 'records', `${slug}.json`);
  if (!existsSync(abs)) die(`bridge record missing: records/${slug}.json (PLAN row ${i + 1})`);
  const raw = readFileSync(abs, 'utf8');
  const doc = JSON.parse(raw);
  const id = `urn:molaug-v0:${slug}`;
  if (doc.id !== id) die(`${slug}: id ${doc.id} != ${id}`);
  for (const f of REQUIRED_FIELDS) if (!(f in doc)) die(`${slug}: missing field '${f}'`);
  const extra = Object.keys(doc).filter((k) => !REQUIRED_FIELDS.includes(k));
  if (extra.length) die(`${slug}: unknown fields ${extra} (kernel-v0 record shape, PLAN.md §1.2)`);
  // DESIGN-v2 §4.2: after proxy adjudication the coordinator relabels bridges.
  const OK_STATUS = ['research-grade', 'provisional/model-authored (proxy-adjudicated)'];
  if (!OK_STATUS.includes(doc.status)) die(`${slug}: status ${doc.status} not in ${JSON.stringify(OK_STATUS)}`);
  const m = /^AST adequacy: (faithful|lossy) — /.exec(doc.notes || '');
  if (!m) die(`${slug}: notes must begin 'AST adequacy: faithful — ' or 'AST adequacy: lossy — '`);
  selfFlags[id] = m[1];
  if (!doc.label.startsWith(slug)) die(`${slug}: label '${doc.label}' must begin with the slug word`);
  if (doc.explication?.schema !== AST_SCHEMA) die(`${slug}: explication.schema != ${AST_SCHEMA}`);
  validateExplication(doc.explication); // throws (fail-closed) on grammar errors

  // -- 3. reference policy + topology --
  const mentioned = [...conceptIds(doc.explication, new Set())].sort();
  const declared = Array.isArray(doc.references) ? [...doc.references].sort() : null;
  if (declared === null || JSON.stringify(declared) !== JSON.stringify(mentioned)) {
    die(`${slug}: references ${JSON.stringify(declared)} != AST concept ids ${JSON.stringify(mentioned)}`);
  }
  if (mentioned.includes(id)) die(`${slug}: self-reference`);
  if (mentioned.length > MAX_REFS) die(`${slug}: ${mentioned.length} refs > cap ${MAX_REFS}`);
  const earlier = new Set(bridgeIds.slice(0, i));
  for (const r of mentioned) {
    const isKv0 = r.startsWith('urn:kernel-v0:') && entries.some((e) => e.id === r);
    if (!isKv0 && !earlier.has(r)) {
      die(`${slug}: reference '${r}' is neither a kernel-v0 id nor a STRICTLY EARLIER bridge row (PLAN topological order)`);
    }
  }
  entries.push({ id, label: doc.label, gloss: doc.gloss, rel: `poc/scale/molecule-aug/lexicon/records/${slug}.json`, raw, doc, tier: 'molaug-v0' });
}
if (entries.length !== 85) die(`expected 85 lexicon records, got ${entries.length}`);

// -- 4. one-pass encode of the whole DAG --------------------------------------
const defs = new Map(entries.map((e) => [e.id, e.doc.explication]));
const { vectors } = encodeConceptSet(defs);
for (const e of entries) {
  const v = vectors.get(e.id);
  if (!v || v.length !== 8192) die(`${e.id}: no D=8192 vector`);
  if (v.some((x) => Number.isNaN(x))) die(`${e.id}: NaN in vector`);
  const norm = Math.sqrt(v.reduce((a, x) => a + x * x, 0));
  if (Math.abs(norm - 1) > 1e-6) die(`${e.id}: norm ${norm} not unit`);
}

// -- 5. anti-leakage slug gate -------------------------------------------------
const lexSlugs = new Map(entries.map((e) => [e.id.split(':').pop(), e.id]));
const evalSets = [{ name: 'consensus-100', rows: JSON.parse(readFileSync(C100, 'utf8')).concepts }];
if (existsSync(HELDOUT)) {
  evalSets.push({ name: 'stage2-heldout', rows: JSON.parse(readFileSync(HELDOUT, 'utf8')).concepts });
}
if (existsSync(FRESH3)) { // v2 fresh PRIMARY sample (DESIGN-v2 §4.3 anti-leakage re-run)
  evalSets.push({ name: 'stage3-fresh', rows: JSON.parse(readFileSync(FRESH3, 'utf8')).concepts });
}
const warnings = [];
for (const { name, rows } of evalSets) {
  for (const r of rows) {
    const slug = slugify(r.concept);
    if (lexSlugs.has(slug)) die(`eval-concept slug collision (${name}): '${r.concept}' -> ${lexSlugs.get(slug)}`);
    for (const lemma of r.lemmas || []) {
      const ls = slugify(lemma);
      if (lexSlugs.has(ls)) warnings.push(`lemma-level near-collision (${name}): '${r.concept}' lemma '${lemma}' matches ${lexSlugs.get(ls)}`);
    }
  }
}

// -- 6. emit -------------------------------------------------------------------
const recordsOut = entries.map((e) => ({
  id: e.id, tier: e.tier, label: e.label, file: e.rel, sha256: sha256(e.raw),
  references: [...conceptIds(e.doc.explication, new Set())].sort(),
  ...(e.tier === 'molaug-v0' ? { astAdequacySelfFlag: selfFlags[e.id] } : {}),
}));
const lexiconSetHash = sha256(recordsOut.map((r) => `${r.id}:${r.sha256}`).sort().join('\n'));
const manifest = {
  corpus: 'molaug-v0 referenceable lexicon (S5)',
  design: 'poc/scale/molecule-aug/DESIGN.md §3; lexicon/PLAN.md',
  generated: new Date().toISOString(),
  encoderContentHash: liveHash,
  kernelV0ManifestSha256: sha256(readFileSync(join(KV0, 'manifest.json'))),
  conceptCount: entries.length,
  bridgeCount: PLAN_ORDER.length,
  bridgeSelfFlags: {
    faithful: Object.values(selfFlags).filter((x) => x === 'faithful').length,
    lossy: Object.values(selfFlags).filter((x) => x === 'lossy').length,
  },
  planOrder: PLAN_ORDER,
  lexiconSetHash,
  slugCollisionGate: { checked: evalSets.map((s) => s.name), collisions: 0, lemmaWarnings: warnings },
  records: recordsOut,
};
writeFileSync(join(HERE, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');

const firstSentence = (g) => {
  const i = g.indexOf('. ');
  return i === -1 ? g.trim() : g.slice(0, i + 1).trim();
};
const listing = entries
  .slice()
  .sort((a, b) => (a.id < b.id ? -1 : 1))
  .map((e) => `${e.id} — ${e.label}: ${firstSentence(e.gloss)}`)
  .join('\n') + '\n';
writeFileSync(join(HERE, 'listing.txt'), listing);

for (const w of warnings) console.error(`WARN: ${w}`);
console.log(JSON.stringify({
  ok: true, conceptCount: entries.length, bridgeCount: PLAN_ORDER.length,
  bridgeSelfFlags: manifest.bridgeSelfFlags, encoderContentHash: liveHash,
  lexiconSetHash, listingLines: listing.trimEnd().split('\n').length,
  lemmaWarnings: warnings.length,
}, null, 1));
