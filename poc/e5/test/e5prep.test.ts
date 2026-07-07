/**
 * E5 prep artifact gates (bead kernel-of-truth-c24). Fail-closed checks over
 * the COMMITTED inputs: pins, selection determinism, derangement validity,
 * vector-table integrity, item construction, zero-exposure guards, manifest
 * consistency. Mirrors poc/e4/test/e4prep.test.ts in spirit.
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { encoderContentHash } from '@jeswr/kernel-encoder';
import {
  D_MODEL,
  EVAL_STYLE,
  INPUTS_DIR,
  N_CANDIDATES,
  N_NONCE,
  N_SEEDS,
  N_SEEN_SYNTH,
  NONCE_MIN_DEPTH,
  NONCE_MIN_TOP_CLAUSES,
  PINNED_B8192_HASH,
  PINNED_GLOSS_HASH,
  loadE4Synthetics,
  loadGlosses,
  readInput,
  seededSample,
  sha256File,
  slugOf,
} from '../harness/common.js';
import { buildConcepts } from '../harness/selectConcepts.js';
import type { E5Concepts } from '../harness/selectConcepts.js';
import type { EvalItem, TrainItem } from '../harness/items.js';

interface ItemsFile {
  artifact: string;
  glossHash: string;
  counts: Record<string, number>;
  training: TrainItem[];
  seenEval: EvalItem[];
  nonceEval: EvalItem[];
}

interface VecManifest {
  artifact: string;
  rows: number;
  d: number;
  encoderContentHash: string;
  pinnedHash: string;
  ids: string[];
  roles: string[];
  kernel: { file: string; sha256: string };
  shuffled: { seed: number; perm: number[] }[];
  randomFrozen: { seed: number; file: string; sha256: string }[];
}

const concepts = readInput<E5Concepts>('e5-concepts.json');
const items = readInput<ItemsFile>('e5-items.json');
const vec = readInput<VecManifest>('vector-tables-manifest.json');
const manifest = readInput<Record<string, any>>('e5-manifest.json');

function readF32(rel: string, expectLen: number): Float32Array {
  const buf = readFileSync(join(INPUTS_DIR, rel));
  assert.equal(buf.length, expectLen * 4, `${rel} byte length`);
  const out = new Float32Array(expectLen);
  for (let i = 0; i < expectLen; i++) out[i] = buf.readFloatLE(i * 4);
  return out;
}

test('encoder pin: kot-enc-B/1 content hash matches the pre-registered pin', () => {
  assert.equal(encoderContentHash(), PINNED_B8192_HASH);
});

test('gloss pin: E4 gloss set loads under the published hash (fail closed)', () => {
  const g = loadGlosses(); // throws on pin mismatch
  assert.ok(g.size >= concepts.ids.length);
});

test('concept selection: counts, ordering, filter, determinism', () => {
  assert.equal(concepts.artifact, 'e5-concepts');
  assert.equal(concepts.counts.seenAuthored, 54);
  assert.equal(concepts.counts.seenSynthetic, N_SEEN_SYNTH);
  assert.equal(concepts.counts.nonce, N_NONCE);
  assert.equal(concepts.ids.length, 54 + N_SEEN_SYNTH + N_NONCE);
  assert.equal(new Set(concepts.ids).size, concepts.ids.length);
  assert.deepEqual(
    concepts.roles.slice(0, 54),
    Array(54).fill('seen-authored'),
  );
  // nonce structural pre-filter respected
  const { records } = loadE4Synthetics();
  const bySynthId = new Map(records.map((r) => [r.id, r]));
  const nonceIds = concepts.ids.filter((_, i) => concepts.roles[i] === 'nonce');
  for (const id of nonceIds) {
    const r = bySynthId.get(id);
    assert.ok(r, `nonce ${id} is synthetic`);
    assert.ok(r!.depth >= NONCE_MIN_DEPTH, `nonce ${id} depth`);
    assert.ok(r!.topClauses >= NONCE_MIN_TOP_CLAUSES, `nonce ${id} topClauses`);
  }
  // deterministic re-selection reproduces the committed artifact
  const rebuilt = buildConcepts();
  assert.deepEqual(rebuilt.ids, concepts.ids);
  assert.deepEqual(rebuilt.roles, concepts.roles);
  assert.deepEqual(rebuilt.composition, concepts.composition);
  // composition entries exist for every nonce
  for (const id of nonceIds) assert.ok(concepts.composition[id] !== undefined);
});

test('vector tables: pins, shas, unit norms, derangements', () => {
  assert.equal(vec.artifact, 'e5-vector-tables');
  assert.equal(vec.rows, concepts.ids.length);
  assert.equal(vec.d, D_MODEL);
  assert.equal(vec.encoderContentHash, PINNED_B8192_HASH);
  assert.equal(vec.pinnedHash, PINNED_B8192_HASH);
  assert.deepEqual(vec.ids, concepts.ids);
  assert.deepEqual(vec.roles, concepts.roles);

  assert.equal(sha256File(join(INPUTS_DIR, vec.kernel.file)), vec.kernel.sha256);
  const kernel = readF32(vec.kernel.file, vec.rows * vec.d);
  for (let r = 0; r < vec.rows; r++) {
    let sq = 0;
    for (let c = 0; c < vec.d; c++) sq += kernel[r * vec.d + c]! ** 2;
    assert.ok(Math.abs(Math.sqrt(sq) - 1) < 1e-3, `kernel row ${r} unit norm`);
  }

  assert.equal(vec.shuffled.length, N_SEEDS);
  for (const s of vec.shuffled) {
    assert.equal(s.perm.length, vec.rows);
    assert.equal(new Set(s.perm).size, vec.rows, 'bijection');
    assert.ok(s.perm.every((v, i) => v !== i), `seed ${s.seed} derangement (no fixed points)`);
  }

  assert.equal(vec.randomFrozen.length, N_SEEDS);
  for (const rf of vec.randomFrozen) {
    assert.equal(sha256File(join(INPUTS_DIR, rf.file)), rf.sha256);
    const t = readF32(rf.file, vec.rows * vec.d);
    for (let r = 0; r < vec.rows; r += 97) { // spot-check rows
      let sq = 0;
      for (let c = 0; c < vec.d; c++) sq += t[r * vec.d + c]! ** 2;
      assert.ok(Math.abs(Math.sqrt(sq) - 1) < 1e-3, `${rf.file} row ${r} unit norm`);
    }
  }
});

test('items: counts, candidates, seeded determinism', () => {
  assert.equal(items.artifact, 'e5-items');
  assert.equal(items.glossHash, PINNED_GLOSS_HASH);
  const nSeen = 54 + N_SEEN_SYNTH;
  assert.equal(items.training.length, nSeen * 4);
  assert.equal(items.counts.trainingVal, Math.round(nSeen * 4 * 0.1));
  assert.equal(items.seenEval.length, nSeen);
  assert.equal(items.nonceEval.length, N_NONCE * 5);

  const rowOf = new Map(concepts.ids.map((id, i) => [id, i]));
  const glosses = loadGlosses();
  const nonceIds = concepts.ids.filter((_, i) => concepts.roles[i] === 'nonce');
  const seenIds = concepts.ids.filter((_, i) => concepts.roles[i] !== 'nonce');
  const nonceSet = new Set(nonceIds);

  for (const it of [...items.seenEval, ...items.nonceEval]) {
    assert.equal(it.candidates.length, N_CANDIDATES);
    assert.equal(it.candidates[0]!.concept, it.concept, 'true gloss at index 0');
    assert.equal(it.row, rowOf.get(it.concept));
    const cs = it.candidates.map((c) => c.concept);
    assert.equal(new Set(cs).size, N_CANDIDATES, 'distinct candidates');
    for (const c of it.candidates) {
      assert.equal(c.gloss, glosses.get(c.concept)![it.style], 'gloss text = pinned gloss set, same style');
    }
  }
  for (const it of items.seenEval) {
    assert.equal(it.style, EVAL_STYLE);
    assert.ok(it.candidates.every((c) => !nonceSet.has(c.concept)), 'seen-eval candidates are seen concepts');
  }
  for (const it of items.nonceEval) {
    assert.ok(it.candidates.every((c) => nonceSet.has(c.concept)), 'nonce-eval candidates are nonces');
  }

  // seeded distractor determinism (spot-check a handful of items)
  for (const it of [items.seenEval[0]!, items.seenEval[123]!, items.nonceEval[0]!, items.nonceEval[57]!]) {
    const pool = (it.style === EVAL_STYLE && !nonceSet.has(it.concept) ? seenIds : nonceIds)
      .filter((x) => x !== it.concept);
    const expect = seededSample(it.candLabel, pool, N_CANDIDATES - 1);
    assert.deepEqual(it.candidates.slice(1).map((c) => c.concept), expect);
  }
});

test('zero-exposure guards over the committed artifacts (README O3)', () => {
  const nonceIds = new Set(concepts.ids.filter((_, i) => concepts.roles[i] === 'nonce'));
  const glosses = loadGlosses();
  const nonceGlossTexts: string[] = [];
  for (const id of nonceIds) for (let s = 0; s <= EVAL_STYLE; s++) nonceGlossTexts.push(glosses.get(id)![s]!);

  let trainInsideNonce = 0;
  for (const t of items.training) {
    assert.ok(!nonceIds.has(t.concept), 'no nonce concept in training');
    assert.notEqual(t.style, EVAL_STYLE, 'no eval style in training');
    for (const g of nonceGlossTexts) {
      // pinned guard directions (README O3): nonce gloss never in training
      assert.ok(t.gloss !== g && !t.gloss.includes(g), 'no nonce gloss text in training');
      if (g.includes(t.gloss)) trainInsideNonce++;
    }
  }
  assert.equal(
    trainInsideNonce,
    items.counts['trainGlossInsideNonceGlossContainments'],
    'descriptive containment count matches the committed artifact',
  );
});

test('pre-registration manifest: pins + statistics block', () => {
  assert.equal(manifest['artifact'], 'e5-manifest');
  assert.equal(manifest['pins']['encoderContentHash'], PINNED_B8192_HASH);
  assert.equal(manifest['pins']['glossHash'], PINNED_GLOSS_HASH);
  assert.equal(manifest['pins']['e4SyntheticsSha256'], concepts.e4SyntheticsSha256);
  assert.equal(manifest['pins']['itemsSha256'], sha256File(join(INPUTS_DIR, 'e5-items.json')));
  assert.equal(
    manifest['pins']['vectorTablesManifestSha256'],
    sha256File(join(INPUTS_DIR, 'vector-tables-manifest.json')),
  );
  assert.equal(manifest['model']['id'], 'HuggingFaceTB/SmolLM2-135M');
  assert.equal(manifest['model']['dModel'], D_MODEL);
  const stats = manifest['statistics'];
  assert.ok(String(stats['primaryEndpoint']).includes('one-sided exact sign-flip permutation over the 24 nonce-level paired differences'));
  assert.ok(String(stats['instrumentValidityGate']).includes('>= 4 of 5 seeds'));
  assert.ok(String(stats['successCriterion']).includes('true kernel > shuffled kernel on nonce-concept usage'));
  assert.ok(String(manifest['specVerbatim']).includes('n ≥ 20 nonce concepts; exact permutation test'));
  // slugs sanity for candidate labels
  assert.equal(slugOf('urn:kernel-e4:syn-0007'), 'e4-syn-0007');
});
