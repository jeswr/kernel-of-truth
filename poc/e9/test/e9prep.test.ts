/**
 * E9-defl prep artifact gates (bead kernel-of-truth-xj2). Fail-closed checks
 * over the COMMITTED inputs: pins, scramble dedup vs true ASTs, size
 * matching, table integrity, selection determinism, manifest consistency.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { canonicalJson, encoderContentHash, validateExplication } from '@jeswr/kernel-encoder';
import {
  D_MODEL,
  E5_INPUTS_DIR,
  INPUTS_DIR,
  PINNED_B8192_HASH,
  authoredSizeProxy,
  loadE4Synthetics,
  loadKernelV0,
  readInput,
  sha256File,
  sha256Hex,
} from '../harness/common.js';
import { buildDeflVocab } from '../harness/deflVocab.js';
import type { DeflRecord } from '../harness/deflVocab.js';

const defl = readInput<{
  artifact: string;
  ids: string[];
  trueAstShas: Record<string, string>;
  records: DeflRecord[];
  e4SyntheticsSha256: string;
}>('defl-concepts.json');
const tables = readInput<Record<string, any>>('defl-tables-manifest.json');
const manifest = readInput<Record<string, any>>('e9-manifest.json');

test('encoder pin matches the pre-registered hash', () => {
  assert.equal(encoderContentHash(), PINNED_B8192_HASH);
});

test('scrambles: counts, row order, dedup, validity, size matching', () => {
  assert.equal(defl.artifact, 'e9-defl-concepts');
  assert.equal(defl.records.length, 524);
  const e5c = JSON.parse(readFileSync(join(E5_INPUTS_DIR, 'e5-concepts.json'), 'utf8'));
  assert.deepEqual(defl.ids, e5c.ids, 'row order = E5 ids');
  assert.deepEqual(defl.records.map((r) => r.id), e5c.ids, 'one scramble per concept, in order');

  const trueShas = new Set(Object.values(defl.trueAstShas));
  const scrambleShas = new Set<string>();
  const { records: synth } = loadE4Synthetics();
  const synthById = new Map(synth.map((r) => [r.id, r]));
  const authoredById = new Map(loadKernelV0().map((r) => [r.id, r]));

  for (const r of defl.records) {
    // recorded sha is the canonical sha, differs from EVERY true AST, unique
    assert.equal(sha256Hex(canonicalJson(r.explication)), r.astSha256);
    assert.ok(!trueShas.has(r.astSha256), `scramble for ${r.id} collides with a true AST`);
    assert.ok(!scrambleShas.has(r.astSha256), `duplicate scramble ${r.id}`);
    scrambleShas.add(r.astSha256);
    validateExplication(r.explication); // gates still pass
    // size matching (pinned J2)
    const syn = synthById.get(r.id);
    if (syn !== undefined) {
      assert.equal(r.sizeSource, 'generator-record');
      assert.equal(r.topClauses, syn.topClauses);
      assert.equal(r.depth, syn.depth);
    } else {
      const au = authoredById.get(r.id)!;
      const proxy = authoredSizeProxy(au.explication as { clauses: unknown[] });
      assert.equal(r.sizeSource, 'authored-proxy');
      assert.equal(r.topClauses, proxy.topClauses);
      assert.equal(r.depth, proxy.depth);
    }
  }
});

test('scramble generation is deterministic (rebuild reproduces the artifact)', () => {
  const rebuilt = buildDeflVocab();
  assert.deepEqual(
    rebuilt.records.map((r) => [r.id, r.seed, r.retries, r.astSha256]),
    defl.records.map((r) => [r.id, r.seed, r.retries, r.astSha256]),
  );
});

test('defl vector table: sha, shape, unit norms', () => {
  assert.equal(tables['artifact'], 'e9-defl-tables');
  assert.equal(tables['rows'], 524);
  assert.equal(tables['d'], D_MODEL);
  assert.equal(tables['encoderContentHash'], PINNED_B8192_HASH);
  assert.deepEqual(tables['ids'], defl.ids);
  const file = join(INPUTS_DIR, tables['defl']['file']);
  assert.equal(sha256File(file), tables['defl']['sha256']);
  const buf = readFileSync(file);
  assert.equal(buf.length, 524 * D_MODEL * 4);
  for (let r = 0; r < 524; r += 41) {
    let sq = 0;
    for (let c = 0; c < D_MODEL; c++) sq += buf.readFloatLE((r * D_MODEL + c) * 4) ** 2;
    assert.ok(Math.abs(Math.sqrt(sq) - 1) < 1e-3, `row ${r} unit norm`);
  }
});

test('e9-manifest: every pin recomputes; statistics strings present', () => {
  assert.equal(manifest['artifact'], 'e9-manifest');
  const pins = manifest['pins'];
  const expects: [string, string][] = [
    ['e5ManifestSha256', join(E5_INPUTS_DIR, 'e5-manifest.json')],
    ['e5ItemsSha256', join(E5_INPUTS_DIR, 'e5-items.json')],
    ['e5ConceptsSha256', join(E5_INPUTS_DIR, 'e5-concepts.json')],
    ['e5VectorTablesManifestSha256', join(E5_INPUTS_DIR, 'vector-tables-manifest.json')],
    ['e5KernelF32Sha256', join(E5_INPUTS_DIR, 'vectors', 'kernel-jl576.f32')],
    ['deflConceptsSha256', join(INPUTS_DIR, 'defl-concepts.json')],
    ['deflTablesManifestSha256', join(INPUTS_DIR, 'defl-tables-manifest.json')],
    ['deflF32Sha256', join(INPUTS_DIR, 'vectors', 'defl-jl576.f32')],
    ['e5CommittedSummarySha256', join(INPUTS_DIR, 'e5-committed-summary.json')],
  ];
  for (const [key, path] of expects) assert.equal(sha256File(path), pins[key], key);
  assert.equal(pins['encoderContentHash'], PINNED_B8192_HASH);
  const stats = manifest['statistics'];
  assert.ok(String(stats['primaryEndpoint']).includes('true-kernel vs defl-kernel'));
  assert.ok(String(stats['outcomes']).includes('DEFLATED'));
  assert.ok(String(stats['outcomes']).includes('AMBIGUOUS-NULL'));
  assert.ok(String(manifest['spec']).includes('NOT poc-design.md E9'));
  // the E5 committed summary really is the committed E5 run
  const sum = readInput<Record<string, any>>('e5-committed-summary.json');
  assert.equal(sum['outcome'], 'PASS');
  assert.ok(Object.keys(sum['armSeed']).length === 10); // true+shuffled x 5 seeds
});
