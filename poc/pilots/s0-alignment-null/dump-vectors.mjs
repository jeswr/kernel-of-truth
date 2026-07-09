// S0 pilot (EXPLORATORY, unregistered): dump a seeded synthetic concept-vector
// panel at D=8192 for the Procrustes alignment-null calibration.
//
// Uses the pinned encoder (kot-enc-B/1, ALGORITHM_VERSION from the package) and
// the Phase-X seeded synthetic generator (poc-design.md Phase X discipline:
// explicit seeds; the encoder itself is unseeded). NOT a registry experiment;
// results feed docs/next/kernel-introduction-schedule.md §S0 as design-pilot
// evidence only.
import { generateExplication, encodeExplication, encoderPin, ALGORITHM_VERSION } from '@jeswr/kernel-encoder';
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const OUT = dirname(fileURLToPath(import.meta.url));
const N = 130;               // panel size: 2x the 65-prime lexicon scale
const D = 8192;              // encoder default (MIN_D)
const SEED_PREFIX = 's0-alignment-null-2026-07-09';

const meta = { n: N, d: D, seedPrefix: SEED_PREFIX, algorithmVersion: ALGORITHM_VERSION, pin: encoderPin(), rows: [] };
const buf = Buffer.alloc(N * D * 8);
let row = 0;
for (let i = 0; i < N; i++) {
  // Spread structural complexity the way X2 cells do: depth 1..4, clauses 1..8.
  const depth = 1 + (i % 4);
  const topClauses = 1 + (i % 8);
  const seed = `${SEED_PREFIX}/${i}`;
  const e = generateExplication({ seed, topClauses, depth });
  const v = encodeExplication(e); // canonical unit vector, Float64Array(D)
  for (let j = 0; j < D; j++) buf.writeDoubleLE(v[j], (row * D + j) * 8);
  meta.rows.push({ i, seed, depth, topClauses });
  row++;
}
mkdirSync(OUT, { recursive: true });
writeFileSync(join(OUT, 'vectors-f64.bin'), buf);
writeFileSync(join(OUT, 'vectors-meta.json'), JSON.stringify(meta, null, 2));
console.log(`wrote ${N}x${D} f64 panel; encoder ${ALGORITHM_VERSION}; hash pin:`, meta.pin.contentHash ?? meta.pin);
