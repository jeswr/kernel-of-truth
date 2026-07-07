#!/usr/bin/env node
/**
 * onto-framenet corpus validator — source-free re-checks (byte re-extraction
 * identity lives in the extractor: run twice + diff, recorded in README.md).
 *
 * Gates:
 *   - frames.jsonl: record shape; unique frameId; id === urn frame-<id>;
 *     frameElements array of {name, coreType∈{Core,Peripheral,Extra-Thematic,
 *     Core-Unexpressed}, feId}; provenance completeness.
 *   - frame-relations.jsonl: record shape; relationType ∈ the 10 FrameNet
 *     types; sub/super urns well-formed; reference closure — every sub/super
 *     frameId resolves to a frame record (0 dangling).
 *   - manifest cross-check: counts, coreType histogram, relation-type
 *     histogram, shard sha256 (recomputed).
 *
 * Run: node data/onto-framenet/validate.mjs   (exit 0 iff all gates pass)
 */
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

const dir = dirname(fileURLToPath(import.meta.url));
const fail = [];
const gate = (ok, msg) => { if (!ok) fail.push(msg); };
const manifest = JSON.parse(readFileSync(join(dir, 'manifest.json'), 'utf8'));

function loadShard(name) {
  const text = readFileSync(join(dir, name), 'utf8');
  const lines = text.trim().split('\n');
  gate(lines.length === manifest.files[name], `${name}: ${lines.length} lines != manifest ${manifest.files[name]}`);
  gate(createHash('sha256').update(text).digest('hex') === manifest.shards[name].sha256, `${name}: sha256 mismatch`);
  return lines.map((l) => JSON.parse(l));
}

const CORE_TYPES = new Set(['Core', 'Peripheral', 'Extra-Thematic', 'Core-Unexpressed']);
const REL_TYPES = new Set(['Inheritance', 'Using', 'Subframe', 'Perspective_on', 'Precedes', 'Inchoative_of', 'Causative_of', 'See_also', 'ReFraming_Mapping', 'Metaphor']);

const frames = loadShard('frames.jsonl');
const relations = loadShard('frame-relations.jsonl');

const frameIds = new Set();
const coreTypeCounts = {};
let coreFEs = 0, feTotal = 0, luTotal = 0;
for (const f of frames) {
  const w = f.frame;
  gate(f.schema === 'kot-framenet/1', `${w}: bad schema`);
  gate(f.semanticStatus === 'AxiomsOnly', `${w}: bad semanticStatus`);
  gate(f.form === 'framenet-frame', `${w}: bad form`);
  gate(f.id === `urn:onto-framenet:frame-${f.frameId}`, `${w}: id != urn frame-<id>`);
  gate(!frameIds.has(f.frameId), `${w}: duplicate frameId ${f.frameId}`);
  frameIds.add(f.frameId);
  gate(Array.isArray(f.frameElements), `${w}: frameElements not array`);
  for (const fe of f.frameElements) {
    gate(typeof fe.name === 'string' && CORE_TYPES.has(fe.coreType) && Number.isInteger(fe.feId), `${w}: bad FE ${JSON.stringify(fe)}`);
    coreTypeCounts[fe.coreType] = (coreTypeCounts[fe.coreType] || 0) + 1;
    if (fe.coreType === 'Core') coreFEs++;
    feTotal++;
  }
  luTotal += (f.annotations.lexicalUnits || []).length;
  // definition prose must be OUTSIDE identity
  gate(!('definition' in f), `${w}: definition must be under annotations, not identity`);
  const p = f.provenance || {};
  gate(p.source && p.license === 'CC BY 3.0 Unported' && p.extractor, `${w}: incomplete provenance / wrong licence`);
}

const relTypeCounts = {};
let feMappings = 0, dangling = 0;
for (const r of relations) {
  const w = r.id;
  gate(r.schema === 'kot-framenet/1' && r.form === 'framenet-frame-relation', `${w}: bad schema/form`);
  gate(REL_TYPES.has(r.relationType), `${w}: bad relationType ${r.relationType}`);
  gate(r.sub === `urn:onto-framenet:frame-${r.subFrameId}`, `${w}: sub urn mismatch`);
  gate(r.super === `urn:onto-framenet:frame-${r.superFrameId}`, `${w}: super urn mismatch`);
  if (!frameIds.has(r.subFrameId)) dangling++;
  if (!frameIds.has(r.superFrameId)) dangling++;
  relTypeCounts[r.relationType] = (relTypeCounts[r.relationType] || 0) + 1;
  feMappings += r.feMappings.length;
}
gate(dangling === 0, `${dangling} dangling frame references in relations`);

// manifest cross-check
const fs2 = manifest.frameStats;
gate(frames.length === fs2.frames, `frame count ${frames.length} != manifest ${fs2.frames}`);
gate(coreFEs === fs2.coreFEs, `coreFE ${coreFEs} != manifest ${fs2.coreFEs}`);
gate(feTotal === fs2.frameElements, `FE total ${feTotal} != manifest ${fs2.frameElements}`);
gate(relations.length === manifest.relationStats.relations, `relation count mismatch`);
gate(feMappings === manifest.relationStats.feMappings, `FE mapping count mismatch`);
for (const [k, v] of Object.entries(coreTypeCounts)) gate(v === fs2.coreTypeCounts[k], `coreType ${k}: ${v} != manifest ${fs2.coreTypeCounts[k]}`);
for (const [k, v] of Object.entries(relTypeCounts)) gate(v === manifest.relationStats.byType[k], `relType ${k}: ${v} != manifest ${manifest.relationStats.byType[k]}`);

console.log(`onto-framenet validate: ${frames.length} frames (${feTotal} FEs, ${coreFEs} Core, ${luTotal} LUs), ${relations.length} relations (${feMappings} FE maps)`);
console.log(`  reference closure: ${dangling} dangling frame refs`);
if (fail.length) {
  console.error(`\nFAIL (${fail.length}):`);
  for (const f of fail.slice(0, 40)) console.error('  - ' + f);
  process.exit(1);
}
console.log('OK: all gates passed');
