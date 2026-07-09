#!/usr/bin/env node
/**
 * B-RT — roll-up/expansion round-trip property census artifact (Tier 0, $0;
 * bead kernel-of-truth-5iu; docs/next/io-compression-ideas.md §3.3, bar 100%).
 *
 * The canonical guard is the encoder test suite
 * (encoder/test/rollup-roundtrip.test.ts, runs under `cd encoder && npm test`).
 * This runner executes the same P1–P5 properties over the same strata and
 * persists the counts as a results JSON (the box is ephemeral; the repo is
 * the record). Any property violation exits non-zero — a FAILURE IS A BUG.
 *
 * Usage: node poc/compression-census/run-b-rt.mjs
 */
import { strict as assert } from 'node:assert';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  canonicalJson,
  CompositeDictionary,
  encodeExplication,
  generateExplication,
  mintCompositeUrn,
  mutateExplication,
  parseRendered,
  renderExplication,
  validateExplication,
  encoderContentHash,
} from '../../encoder/dist/src/index.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, 'results');

const DEPTHS = [1, 2, 3, 4, 6, 8, 12];
const TOP_CLAUSES = [1, 2, 4, 8, 16, 32];
const SEEDS_PER_CELL = 25;

const dict = new CompositeDictionary();
const perStratum = [];
let originals = 0;
let mutants = 0;
let nullMutations = 0;
let encodeChecks = 0;
const t0 = Date.now();

function props(e, label) {
  const urn1 = mintCompositeUrn(e);
  assert.equal(mintCompositeUrn(JSON.parse(JSON.stringify(e))), urn1, `${label}: P1 URN determinism`);
  assert.match(urn1, /^urn:kot:b[a-z2-7]+$/);
  assert.equal(dict.add(e), urn1, `${label}: P2 dictionary URN`);
  const entry = dict.expand(urn1);
  assert.equal(canonicalJson(entry.ast), canonicalJson(e), `${label}: P2 expansion identity`);
  const text = renderExplication(e);
  assert.equal(entry.renderedText, text, `${label}: P3 dictionary rendering`);
  const back = parseRendered(text);
  assert.equal(canonicalJson(back), canonicalJson(e), `${label}: P3 render->parse identity`);
  validateExplication(back);
  assert.equal(mintCompositeUrn(back), urn1, `${label}: P3 URN stability`);
  return urn1;
}

for (const depth of DEPTHS) {
  for (const topClauses of TOP_CLAUSES) {
    if (depth - 1 > 32 - topClauses) continue;
    const cell = { depth, topClauses, originals: 0, mutants: 0, nullMutations: 0 };
    for (let s = 0; s < SEEDS_PER_CELL; s++) {
      const seed = `b-rt/${depth}/${topClauses}/${s}`;
      const e = generateExplication({ seed, topClauses, depth });
      const label = `d=${depth} c=${topClauses} s=${s}`;
      const urn = props(e, label);
      originals++;
      cell.originals++;
      if (s === 0) {
        // P5: encode equivalence across the render->parse round trip
        const v1 = encodeExplication(e);
        const v2 = encodeExplication(parseRendered(renderExplication(e)));
        assert.deepEqual(Buffer.from(v1.buffer), Buffer.from(v2.buffer), `${label}: P5 encode equivalence`);
        encodeChecks++;
      }
      const m = mutateExplication(e, `${seed}/mut`);
      if (m === null) {
        nullMutations++;
        cell.nullMutations++;
        continue;
      }
      const urnMut = props(m.mutant, `${label} mutant`);
      assert.notEqual(urnMut, urn, `${label}: P4 mutant URN separation`);
      mutants++;
      cell.mutants++;
    }
    perStratum.push(cell);
  }
}

const report = {
  census: 'B-RT roll-up/expansion round-trip property suite (Tier 0)',
  bead: 'kernel-of-truth-5iu',
  design: 'docs/next/io-compression-ideas.md §3.3 (bar: 100% — any failure is a bug)',
  canonical_guard: 'encoder/test/rollup-roundtrip.test.ts (in the encoder npm test suite)',
  date: new Date().toISOString(),
  encoder_content_hash: encoderContentHash(),
  properties: {
    P1: 'URN determinism (mint twice + JSON round-trip)',
    P2: 'dictionary exact-by-id expansion identity',
    P3: 'render -> parse identity + URN stability + revalidation',
    P4: 'validity-preserving single edits move the content address',
    P5: 'encoded vectors byte-identical across the render->parse round trip (D=8192)',
  },
  strata: { depths: DEPTHS, topClauses: TOP_CLAUSES, seedsPerCell: SEEDS_PER_CELL, cells: perStratum.length },
  counts: {
    originals,
    mutants,
    null_mutations: nullMutations,
    unique_composites_in_dictionary: dict.size,
    encode_equivalence_checks: encodeChecks,
    items_checked: originals + mutants,
    failures: 0,
  },
  pass_rate: 1.0,
  runtime_seconds: (Date.now() - t0) / 1000,
  per_stratum: perStratum,
};

mkdirSync(OUT, { recursive: true });
writeFileSync(join(OUT, 'b-rt-roundtrip.json'), JSON.stringify(report, null, 2));
console.log(
  `B-RT PASS 100%: ${originals} originals + ${mutants} mutants (${nullMutations} null mutations) across ${perStratum.length} strata; ` +
    `${dict.size} unique composites; ${encodeChecks} encode-equivalence checks; ${report.runtime_seconds.toFixed(1)}s`,
);
console.log(`written: ${join(OUT, 'b-rt-roundtrip.json')}`);
