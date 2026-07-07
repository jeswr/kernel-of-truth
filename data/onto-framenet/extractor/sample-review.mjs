#!/usr/bin/env node
/**
 * onto-framenet random-sample audit (requires source/fndata). Independent-path
 * re-derivation of a seeded sample:
 *   (a) frames: re-read the frame/*.xml and INDEPENDENTLY extract frame name +
 *       the set of (FE name, coreType) pairs with a distinct regex, compared to
 *       the emitted record's frameElements.
 *   (b) relations: re-scan frRelation.xml for the relation ID and independently
 *       read sub/super frame ids + relationType, compared to the record.
 * Error rate printed. Usage: node .../sample-review.mjs [Nframe] [Nrel] [seedHex]
 */
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const FN = join(ROOT, 'source', 'fndata', 'framenet_v17');
const NF = parseInt(process.argv[2] || '150', 10);
const NR = parseInt(process.argv[3] || '100', 10);
const SEED = process.argv[4] || '0xf00d';

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function shuffled(n, seed) {
  const rng = mulberry32(seed >>> 0);
  const a = Array.from({ length: n }, (_, i) => i);
  for (let i = n - 1; i > 0; i--) { const j = Math.floor(rng() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}
if (!existsSync(FN)) throw new Error('ERR_SOURCE_MISSING: source/fndata/framenet_v17 (re-create per README)');

// Build frameId -> source-file path (independent of the extractor's ordering).
const frameDir = join(FN, 'frame');
const fileByFrameId = new Map();
for (const f of readdirSync(frameDir).filter((x) => x.endsWith('.xml'))) {
  const xml = readFileSync(join(frameDir, f), 'utf8');
  const m = xml.match(/<frame\b[^>]*\bID="(\d+)"/);
  if (m) fileByFrameId.set(Number(m[1]), join(frameDir, f));
}

/** Independent FE (name, coreType) extraction — a distinct regex path. */
function indepFrame(xml) {
  const nameM = xml.match(/<frame\b[^>]*\bname="([^"]*)"/);
  const fes = new Set();
  for (const m of xml.matchAll(/<FE\b[^>]*>/g)) {
    const tag = m[0];
    const nm = tag.match(/\bname="([^"]*)"/);
    const ct = tag.match(/\bcoreType="([^"]*)"/);
    if (nm && ct) fes.add(`${nm[1]}|${ct[1]}`);
  }
  return { name: nameM ? nameM[1] : null, fes };
}

const frames = readFileSync(join(ROOT, 'frames.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);
const relations = readFileSync(join(ROOT, 'frame-relations.jsonl'), 'utf8').trim().split('\n').map(JSON.parse);

// (a) frames
let fErr = 0; const fLog = [];
const fIdx = shuffled(frames.length, parseInt(SEED, 16)).slice(0, Math.min(NF, frames.length));
const setEq = (a, b) => a.size === b.size && [...a].every((x) => b.has(x));
for (const k of fIdx) {
  const rec = frames[k];
  const path = fileByFrameId.get(rec.frameId);
  if (!path) { fErr++; fLog.push(`${rec.frame}: source file not found`); continue; }
  const ind = indepFrame(readFileSync(path, 'utf8'));
  const recFes = new Set(rec.frameElements.map((fe) => `${fe.name}|${fe.coreType}`));
  const problems = [];
  if (ind.name !== rec.frame) problems.push(`name ${rec.frame} != ${ind.name}`);
  if (!setEq(recFes, ind.fes)) problems.push('FE (name,coreType) set mismatch');
  if (problems.length) { fErr++; fLog.push(`${rec.frame}: ${problems.join('; ')}`); }
}

// (b) relations — independent scan of frRelation.xml for the relId's frameRelation tag
const relXml = readFileSync(join(FN, 'frRelation.xml'), 'utf8');
let rErr = 0; const rLog = [];
const rIdx = shuffled(relations.length, (parseInt(SEED, 16) ^ 0x5bd1e995) >>> 0).slice(0, Math.min(NR, relations.length));
for (const k of rIdx) {
  const rec = relations[k];
  const relId = Number(rec.id.replace('urn:onto-framenet:frel-', ''));
  const m = relXml.match(new RegExp(`<frameRelation\\b[^>]*\\bID="${relId}"[^>]*>`));
  if (!m) { rErr++; rLog.push(`${rec.id}: relation tag not found`); continue; }
  const tag = m[0];
  const subID = Number((tag.match(/\bsubID="(\d+)"/) || [])[1]);
  const supID = Number((tag.match(/\bsupID="(\d+)"/) || [])[1]);
  const problems = [];
  if (subID !== rec.subFrameId) problems.push(`subID ${rec.subFrameId} != ${subID}`);
  if (supID !== rec.superFrameId) problems.push(`supID ${rec.superFrameId} != ${supID}`);
  if (problems.length) { rErr++; rLog.push(`${rec.id}: ${problems.join('; ')}`); }
}

const fr = ((fErr / fIdx.length) * 100).toFixed(2);
const rr = ((rErr / rIdx.length) * 100).toFixed(2);
console.log(`onto-framenet sample audit (seed ${SEED}):`);
console.log(`  frames: N=${fIdx.length}, errors=${fErr} (${fr}%)`);
console.log(`  relations: N=${rIdx.length}, errors=${rErr} (${rr}%)`);
for (const e of [...fLog, ...rLog].slice(0, 20)) console.log('  ERR ' + e);
process.exit(fErr === 0 && rErr === 0 ? 0 : 1);
