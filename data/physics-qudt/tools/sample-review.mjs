#!/usr/bin/env node
/**
 * Deterministic random-sample selector for the physics-qudt hand review
 * (verification bar: >=100-record random sample manually reviewed, error
 * rate reported — docs/design-bulk-kernel.md).
 *
 * Seeded PRNG (mulberry32, pinned seed) over the emitted records, so the
 * sample is reproducible from the corpus alone. Emits a review sheet to
 * stdout: one block per sampled record with the emitted record and the
 * cross-check-relevant QUDT stated values (from crosscheck material where
 * applicable). The human verdicts live in review-sample.json.
 *
 * Usage: node tools/sample-review.mjs [--qk 45] [--units 60]
 */
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const SEED = 0x6b6f7451; // 'kotQ' — pinned
const mulberry32 = (a) => () => {
  a |= 0; a = (a + 0x6d2b79f5) | 0;
  let t = Math.imul(a ^ (a >>> 15), 1 | a);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const argv = process.argv.slice(2);
const argOf = (k, dflt) => { const i = argv.indexOf(k); return i >= 0 ? Number(argv[i + 1]) : dflt; };
const nQk = argOf('--qk', 45);
const nUnit = argOf('--units', 60);

const loadJsonl = (f) => readFileSync(join(root, f), 'utf8').trimEnd().split('\n').map((l) => JSON.parse(l));
const qks = loadJsonl('quantitykinds.jsonl');
const units = loadJsonl('units.jsonl');

// deterministic sample without replacement (Fisher-Yates prefix)
const sample = (arr, n, rnd) => {
  const a = [...arr];
  for (let i = 0; i < Math.min(n, a.length); i++) {
    const j = i + Math.floor(rnd() * (a.length - i));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a.slice(0, n);
};
const rnd = mulberry32(SEED);
const qkSample = sample(qks, nQk, rnd);
const unitSample = sample(units, nUnit, rnd);

console.log(`# physics-qudt review sample (seed 0x${SEED.toString(16)}): ${qkSample.length} QuantityKind + ${unitSample.length} Unit = ${qkSample.length + unitSample.length}\n`);
for (const r of qkSample) {
  console.log(`## QK ${r.id}`);
  console.log(`   label=${JSON.stringify(r.label)} dim=[${r.dim}] (order T,L,M,I,Theta,N,J)`);
  console.log(`   qkdv=${r.bridgesTo.qudtDimensionVector}`);
  if (r.broader) console.log(`   broader=${r.broader.map((b) => b.split(':').pop()).join(', ')}`);
  console.log();
}
for (const r of unitSample) {
  console.log(`## UNIT ${r.id}`);
  console.log(`   label=${JSON.stringify(r.label)} symbol=${JSON.stringify(r.symbol ?? null)} kind=${r.quantityKind.split(':').pop()}`);
  console.log(`   scale=${r.scale}${r.piExponent ? ` * pi^${r.piExponent}` : ''} offset=${r.offset} coherentSI=${r.coherentSI}`);
  console.log(`   derivation: ${r.derivation}`);
  console.log(`   ucum=${JSON.stringify(r.bridgesTo.ucumCode ?? null)}`);
  console.log();
}
