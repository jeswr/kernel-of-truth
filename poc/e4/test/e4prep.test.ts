/**
 * E4 prep artifact gates (bead kernel-of-truth-73u). These re-verify the
 * COMMITTED artifacts, not the generators' bookkeeping: encoder pin,
 * synthetic-explication validity, vector-table integrity, gloss discipline
 * (target-lexicon disjointness + independence n-gram gate + distinctness +
 * published hash), and the holdout pre-registration manifest.
 */

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { test } from 'node:test';
import {
  DetStream,
  canonicalJson,
  encoderContentHashQ,
  validateExplication,
} from '@jeswr/kernel-encoder';
import type { Explication } from '@jeswr/kernel-encoder';
import { buildLexicon, loadManifestConcepts } from '@jeswr/kernel-mapper';
import {
  E4_DIR,
  E4_D_MODEL,
  INPUTS_DIR,
  KERNEL_V0_DIR,
  N_GLOSS_VARIANTS,
  N_SYNTH,
  PINNED_BQ512_HASH,
  TIER2_SIZE,
  loadKernelV0,
  readInput,
  sha256Hex,
} from '../harness/common.js';
import { generateSynthRecord } from '../harness/synthVocab.js';
import type { SynthRecord } from '../harness/synthVocab.js';
import { glossCollides, longestSharedRun, MAX_SHARED_NGRAM } from '../harness/glosses.js';
import type { GlossLine } from '../harness/glosses.js';
import { realizeExplication } from '../harness/realizer.js';
import { featureSet } from '../harness/holdout.js';

const synth = readInput<{ artifact: string; records: SynthRecord[] }>('synthetic-concepts.json');
const vman = readInput<{
  rows: number;
  D: number;
  pinnedHash: string;
  encoderContentHashQ: string;
  ids: string[];
  kernel: { file: string; sha256: string };
  randomFrozen: { file: string; sha256: string }[];
  shuffled: { seed: number; perm: number[] }[];
}>('vector-tables-manifest.json');
const glossLines: GlossLine[] = readFileSync(join(INPUTS_DIR, 'glosses.jsonl'), 'utf8')
  .trim()
  .split('\n')
  .map((l) => JSON.parse(l) as GlossLine);

test('encoder pin: live kot-enc-Bq/1@512 hash equals the pre-registered pin', () => {
  assert.equal(encoderContentHashQ({ D: E4_D_MODEL }), PINNED_BQ512_HASH);
  assert.equal(vman.pinnedHash, PINNED_BQ512_HASH);
  assert.equal(vman.encoderContentHashQ, PINNED_BQ512_HASH);
});

test('synthetic vocabulary: 1000 unique, gate-valid, deterministically regenerable', () => {
  assert.equal(synth.records.length, N_SYNTH);
  const ids = new Set(synth.records.map((r) => r.id));
  assert.equal(ids.size, N_SYNTH);
  const hashes = new Set<string>();
  for (const r of synth.records) {
    validateExplication(r.explication); // fail closed on any invalid AST
    const h = sha256Hex(canonicalJson(r.explication));
    assert.equal(h, r.astSha256, `${r.id} astSha256 drift`);
    assert.ok(!hashes.has(h), `${r.id} duplicate AST`);
    hashes.add(h);
  }
  // Seed-scheme determinism: regenerate a few records from scratch.
  for (const i of [0, 1, 499, 999]) {
    const taken = new Set(synth.records.slice(0, i).map((r) => r.astSha256));
    const rec = generateSynthRecord(i, taken);
    assert.equal(rec.astSha256, synth.records[i]!.astSha256, `record ${i} not reproducible`);
  }
});

test('vector tables: manifest hashes match files; kernel rows unit-norm; derangements', () => {
  assert.equal(vman.rows, 54 + N_SYNTH);
  assert.equal(vman.D, E4_D_MODEL);
  assert.equal(vman.ids.length, vman.rows);
  const kbuf = readFileSync(join(INPUTS_DIR, vman.kernel.file));
  assert.equal(sha256Hex(kbuf), vman.kernel.sha256, 'kernel .f32 sha drift');
  assert.equal(kbuf.length, vman.rows * vman.D * 4);
  // Sample rows: unit norm (fp32 storage tolerance).
  for (const r of [0, 53, 54, vman.rows - 1]) {
    let n = 0;
    for (let c = 0; c < vman.D; c++) {
      const x = kbuf.readFloatLE((r * vman.D + c) * 4);
      n += x * x;
    }
    assert.ok(Math.abs(Math.sqrt(n) - 1) < 1e-5, `row ${r} norm ${Math.sqrt(n)}`);
  }
  for (const f of vman.randomFrozen) {
    assert.equal(sha256Hex(readFileSync(join(INPUTS_DIR, f.file))), f.sha256, `${f.file} sha`);
  }
  for (const s of vman.shuffled) {
    const seen = new Set(s.perm);
    assert.equal(seen.size, vman.rows);
    assert.ok(s.perm.every((v, i) => v !== i), `seed ${s.seed} has a fixed point`);
  }
});

test('glosses: >=5 distinct per concept, published hash matches file', () => {
  const jsonl = readFileSync(join(INPUTS_DIR, 'glosses.jsonl'), 'utf8');
  const published = /= ([0-9a-f]{64})/.exec(
    readFileSync(join(E4_DIR, 'GLOSS-HASH.txt'), 'utf8'),
  )?.[1];
  assert.equal(sha256Hex(jsonl), published, 'GLOSS-HASH.txt out of date vs glosses.jsonl');

  const byConcept = new Map<string, GlossLine[]>();
  for (const l of glossLines) {
    const arr = byConcept.get(l.conceptId) ?? [];
    arr.push(l);
    byConcept.set(l.conceptId, arr);
  }
  assert.equal(byConcept.size, 54 + N_SYNTH);
  for (const [id, arr] of byConcept) {
    assert.ok(arr.length >= N_GLOSS_VARIANTS, `${id}: ${arr.length} glosses`);
    assert.equal(new Set(arr.map((g) => g.gloss)).size, arr.length, `${id}: duplicate glosses`);
    // Minimal synthetic ASTs (e.g. a single HAPPEN clause) legitimately
    // realize as two-word glosses ("I happen."); only the empty/one-word
    // case would indicate a realizer fault.
    for (const g of arr) assert.ok(g.gloss.split(' ').length >= 2, `${id}: degenerate gloss`);
  }
});

test('glosses: full mechanical target-lexicon disjointness re-check (mapper mapText)', () => {
  const lexicon = buildLexicon(loadManifestConcepts(join(KERNEL_V0_DIR, 'manifest.json')));
  for (const l of glossLines) {
    assert.ok(
      !glossCollides(lexicon, l.conceptId, l.gloss),
      `${l.conceptId} v${l.variant}: gloss contains its own mapper surface form`,
    );
  }
});

test('glosses: independence n-gram gate vs kernel-v0 gloss fields', () => {
  const byId = new Map(loadKernelV0().map((r) => [r.id, r.gloss]));
  let worst = 0;
  for (const l of glossLines) {
    const kg = byId.get(l.conceptId);
    if (kg === undefined) continue; // synthetic: no kernel-v0 gloss exists
    const run = longestSharedRun(l.gloss, kg);
    worst = Math.max(worst, run);
    assert.ok(
      run <= MAX_SHARED_NGRAM,
      `${l.conceptId} v${l.variant}: shares a ${run}-word run with the kernel-v0 gloss`,
    );
  }
  assert.ok(worst > 0); // sanity: the metric is actually measuring something
});

test('realizer: deterministic in (explication, style, label)', () => {
  const rec = synth.records[123]!;
  const mk = () =>
    realizeExplication(rec.explication, {
      style: 2,
      rng: new DetStream('e4/determinism-test'),
      bannedLemmas: new Set(),
      conceptPhrase: (id) => id,
    });
  assert.equal(mk(), mk());
});

test('holdout manifest: tiers, splits and stats spec are complete and consistent', () => {
  const m = readInput<{
    inputs: { glossesSha256: string; syntheticConceptsSha256: string };
    vocab: { total: number };
    tiers: {
      tier1: { ids: string[]; count: number };
      tier2: { ids: string[]; count: number };
      train: { count: number };
    };
    evalGlossVariant: Record<string, number>;
    composition: { labels: Record<string, { sharesStructureWithSeen: boolean }> };
    statistics: {
      candidateSetSize: number;
      chance: { top1: number; top10: number };
      primaryEndpoint: string;
      controlFloorCheck: string;
    };
    exposurePolicy: { linesPerConcept: number };
  }>('holdout-manifest.json');

  assert.equal(m.vocab.total, 54 + N_SYNTH);
  assert.equal(
    m.inputs.glossesSha256,
    sha256Hex(readFileSync(join(INPUTS_DIR, 'glosses.jsonl'), 'utf8')),
    'holdout manifest built against a different gloss set',
  );
  const t1 = new Set(m.tiers.tier1.ids);
  const t2 = new Set(m.tiers.tier2.ids);
  assert.equal(t2.size, TIER2_SIZE);
  assert.ok(m.tiers.tier2.ids.every((id) => id.startsWith('urn:kernel-e4:')), 'tier2 must be synthetic');
  assert.equal([...t1].filter((id) => t2.has(id)).length, 0, 'tiers overlap');
  assert.equal(m.tiers.tier1.count + m.tiers.tier2.count + m.tiers.train.count, m.vocab.total);
  assert.ok(Math.abs(m.tiers.tier1.count - 0.2 * m.vocab.total) <= 1, 'tier1 not ~20%');
  assert.equal(Object.keys(m.evalGlossVariant).length, m.tiers.train.count);
  for (const v of Object.values(m.evalGlossVariant)) assert.ok(v >= 0 && v < N_GLOSS_VARIANTS);
  for (const id of [...t1, ...t2]) {
    assert.ok(m.composition.labels[id] !== undefined, `${id} missing compositional label`);
  }
  assert.equal(m.statistics.candidateSetSize, m.vocab.total);
  assert.ok(Math.abs(m.statistics.chance.top10 - 10 / m.vocab.total) < 1e-12);
  assert.match(m.statistics.primaryEndpoint, /tier-2 top-1/);
  assert.match(m.statistics.controlFloorCheck, /empirical chance/);
  assert.equal(m.exposurePolicy.linesPerConcept, 20);
});

test('compositional features: skeleton function is stable and non-trivial', () => {
  const a = featureSet(synth.records[0]!.explication);
  const b = featureSet(synth.records[0]!.explication);
  assert.deepEqual([...a].sort(), [...b].sort());
  const other = featureSet(synth.records[1]!.explication as Explication);
  assert.notDeepEqual([...a].sort(), [...other].sort());
});
