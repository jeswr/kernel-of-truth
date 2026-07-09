#!/usr/bin/env node
/**
 * onto-obo random-sample audit. Seeded PRNG picks N emitted records; each is
 * re-derived from its OWNING source OBO file by an INDEPENDENT access path — a
 * raw stanza-block scan for `id: <oboId>` + a hand-rolled re-parse — and the
 * key fields (label, definition presence, is_a target set, genus/differentia)
 * are compared with the emitted record. Any mismatch is an error; the error
 * rate is printed. Requires source/ present.
 *
 * Usage: nice -n 10 node data/onto-obo/extractor/sample-review.mjs [N] [seedHex]
 */
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { toUrn, stripIdValue } from './parse-obo.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(ROOT, 'source');
const N = parseInt(process.argv[2] || '150', 10);
const SEED = process.argv[3] || '0x0b0';

// mulberry32 deterministic PRNG (same family as the wn31 audit).
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const FILE_OF = { BFO: 'bfo.obo', RO: 'ro.obo', GO: 'go.obo', PATO: 'pato.obo', PO: 'po.obo', CL: 'cl.obo', UBERON: 'uberon.obo', OGMS: 'ogms.obo', SO: 'so.obo', MONDO: 'mondo.obo' };
const SHARD_OF = { BFO: 'bfo.jsonl', RO: 'ro.jsonl', GO: 'go.jsonl', PATO: 'pato.jsonl', PO: 'po.jsonl', CL: 'cl.jsonl', UBERON: 'uberon.jsonl', OGMS: 'ogms.jsonl', SO: 'so.jsonl', MONDO: 'mondo.jsonl' };

// Load emitted records.
const records = [];
for (const shard of Object.values(SHARD_OF)) {
  for (const l of readFileSync(join(ROOT, shard), 'utf8').trim().split('\n')) records.push(JSON.parse(l));
}
// kernel-of-truth-8es: the set of emitted relation record ids — every resolved
// differentia `relation` URN must land in this set (checked per sampled record).
const emittedRelIds = new Set(records.filter((r) => r.kind === 'relation').map((r) => r.id));

// Independent raw-block extraction of a stanza by oboId from a source file.
function rawStanza(text, oboId) {
  const lines = text.split('\n');
  let start = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim() === `id: ${oboId}`) {
      // walk back to the stanza header
      let j = i;
      while (j >= 0 && lines[j].trim() !== '') j--;
      start = j + 1;
      break;
    }
  }
  if (start < 0) return null;
  const block = [];
  for (let i = start; i < lines.length; i++) {
    if (lines[i].trim() === '') break;
    block.push(lines[i]);
  }
  return block;
}

function rawParse(block) {
  const name = [];
  const is_a = [];
  const iof = [];
  let hasDef = false, obsolete = false;
  let hasElucidation = false;
  for (const raw of block) {
    const line = raw.endsWith('\r') ? raw.slice(0, -1) : raw;
    const ci = line.indexOf(':');
    if (ci < 0) continue;
    const tag = line.slice(0, ci).trim();
    const val = line.slice(ci + 1).trim();
    if (tag === 'name') name.push(val);
    else if (tag === 'is_a') is_a.push(toUrn(stripIdValue(val)));
    else if (tag === 'intersection_of') iof.push(stripIdValue(val));
    else if (tag === 'def') hasDef = true;
    else if (tag === 'is_obsolete' && val === 'true') obsolete = true;
    else if (tag === 'property_value' && val.startsWith('IAO:0000600 ')) hasElucidation = true;
  }
  // genus/differentia from iof
  const genus = []; const differentiae = [];
  for (const v of iof) {
    const toks = v.split(/\s+/);
    if (toks.length === 1) genus.push(toUrn(toks[0]));
    else differentiae.push(`${toks[0]}|${toUrn(toks[1])}`);
  }
  return { name: name[0], is_a: new Set(is_a), genus: new Set(genus), differentiae: new Set(differentiae), hasDef, hasElucidation, obsolete };
}

const srcCache = {};
function srcText(ontId) {
  if (!srcCache[ontId]) {
    const p = join(SRC, FILE_OF[ontId]);
    if (!existsSync(p)) throw new Error(`ERR_SOURCE_MISSING: ${FILE_OF[ontId]} (re-download per README)`);
    srcCache[ontId] = readFileSync(p, 'utf8');
  }
  return srcCache[ontId];
}

// Seeded sample.
const rng = mulberry32(parseInt(SEED, 16) >>> 0);
const idx = records.map((_, i) => i);
for (let i = idx.length - 1; i > 0; i--) {
  const j = Math.floor(rng() * (i + 1));
  [idx[i], idx[j]] = [idx[j], idx[i]];
}
const sample = idx.slice(0, Math.min(N, idx.length)).map((i) => records[i]);

let errors = 0;
const errLog = [];
const setEq = (a, b) => a.size === b.size && [...a].every((x) => b.has(x));
for (const rec of sample) {
  const text = srcText(rec.ontology);
  const block = rawStanza(text, rec.oboId);
  if (!block) { errors++; errLog.push(`${rec.oboId}: not found in ${FILE_OF[rec.ontology]}`); continue; }
  const p = rawParse(block);
  const problems = [];
  if (p.obsolete) problems.push('source marks obsolete but record emitted');
  if ((p.name || null) !== (rec.annotations.label || null)) problems.push(`label "${rec.annotations.label}" != source name "${p.name}"`);
  const recIsA = new Set(rec.axioms.filter((a) => a.rel === 'is_a').map((a) => a.target));
  if (!setEq(recIsA, p.is_a)) problems.push(`is_a mismatch: rec ${[...recIsA]} vs src ${[...p.is_a]}`);
  const recGenus = new Set(rec.logicalDefinition ? rec.logicalDefinition.genus : []);
  if (!setEq(recGenus, p.genus)) problems.push('genus mismatch');
  const recDiff = new Set(rec.logicalDefinition ? rec.logicalDefinition.differentiae.map((d) => `${d.property}|${d.filler}`) : []);
  if (!setEq(recDiff, p.differentiae)) problems.push('differentia mismatch');
  // 8es: every differentia's resolved `relation` URN must reference an emitted relation record.
  if (rec.logicalDefinition) {
    for (const d of rec.logicalDefinition.differentiae) {
      if (typeof d.relation !== 'string' || !emittedRelIds.has(d.relation)) {
        problems.push(`differentia relation ${d.relation} not an emitted relation record`);
      }
    }
  }
  const recHasDef = !!rec.annotations.definition;
  const srcHasDef = p.hasDef || p.hasElucidation;
  if (recHasDef !== srcHasDef) problems.push(`definition presence: rec ${recHasDef} vs src ${srcHasDef}`);
  if (problems.length) { errors++; errLog.push(`${rec.oboId}: ${problems.join('; ')}`); }
}

const rate = ((errors / sample.length) * 100).toFixed(2);
console.log(`onto-obo sample audit: N=${sample.length} (seed ${SEED}), errors=${errors} (${rate}%)`);
const byOnt = {};
for (const r of sample) byOnt[r.ontology] = (byOnt[r.ontology] || 0) + 1;
console.log(`  sample by ontology: ${Object.entries(byOnt).map(([k, v]) => `${k}:${v}`).join(', ')}`);
for (const e of errLog.slice(0, 20)) console.log('  ERR ' + e);
process.exit(errors === 0 ? 0 : 1);
