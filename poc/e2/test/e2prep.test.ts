/** Tests for the E2 prep harness (node:test). */

import { strict as assert } from 'node:assert';
import { test } from 'node:test';
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { DEFAULT_PARAMS, encodeExplication, generateExplication } from '@jeswr/kernel-encoder';
import {
  INPUTS_DIR,
  corpusPin,
  cosine,
  jlProject,
  offDiagonal,
  similarityMatrix,
  spearman,
} from '../harness/common.js';
import { buildItems, EXCLUDED_MULTIWORD } from '../harness/items.js';
import { loadCorpus } from '../harness/corpus.js';
import { deriveGlossWords, jaccard, surfaceWords } from '../harness/glossRdm.js';
import { TEMPLATE_BANKS, checkNoProbeWordLeak, instantiate } from '../harness/contexts.js';
import { hypernymDistance, loadWordnet, pathSimilarity, shortestPath } from '../harness/wordnet.js';

// ---------------------------------------------------------------------------
// stats
// ---------------------------------------------------------------------------

test('spearman: perfect monotone = 1, reversed = -1, ties averaged', () => {
  assert.equal(spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1);
  assert.equal(spearman([1, 2, 3, 4], [40, 30, 20, 10]), -1);
  // ties: known value against hand-computed mid-rank result
  const r = spearman([1, 1, 2, 3], [1, 2, 3, 4]);
  assert.ok(Math.abs(r - 0.9486832980505138) < 1e-12, `got ${r}`);
});

test('similarityMatrix + offDiagonal shapes', () => {
  const m = similarityMatrix(4, (i, j) => i + j);
  assert.equal(m.length, 4);
  assert.equal(m[1]![3], m[3]![1]);
  assert.equal(m[2]![2], 1);
  assert.equal(offDiagonal(m).length, 6);
});

// ---------------------------------------------------------------------------
// JL projection (must be bit-identical to poc/harness/x4.ts's construction)
// ---------------------------------------------------------------------------

test('jlProject is deterministic and roughly angle-preserving', () => {
  const D = DEFAULT_PARAMS.D;
  const vecs = [0, 1, 2, 3, 4].map((i) =>
    encodeExplication(generateExplication({ seed: `e2test/${i}`, topClauses: 2, depth: 2 })),
  );
  const a = jlProject(vecs, D, 512);
  const b = jlProject(vecs, D, 512);
  for (let i = 0; i < vecs.length; i++) assert.deepEqual([...a[i]!], [...b[i]!]);
  // RDM correlation between full-D and projected must be high (X4 measured ~>0.9)
  const full = offDiagonal(similarityMatrix(vecs.length, (i, j) => cosine(vecs[i]!, vecs[j]!)));
  const proj = offDiagonal(similarityMatrix(vecs.length, (i, j) => cosine(a[i]!, a[j]!)));
  assert.ok(spearman(full, proj) > 0.7, `spearman ${spearman(full, proj)}`);
});

// ---------------------------------------------------------------------------
// items
// ---------------------------------------------------------------------------

test('item registry: 54 corpus ids -> 51 probe items + 3 published exclusions', () => {
  const corpus = loadCorpus();
  const { allItemIds, probeItems, excludedIds } = buildItems(corpus.map((c) => c.id));
  assert.equal(allItemIds.length, 54);
  assert.equal(probeItems.length, 51);
  assert.equal(excludedIds.length, EXCLUDED_MULTIWORD.length);
  for (const p of probeItems) assert.ok(!p.word.includes(' ') && !p.word.includes('-'), p.word);
});

// ---------------------------------------------------------------------------
// gloss derivation
// ---------------------------------------------------------------------------

test('surfaceWords normalisation', () => {
  assert.deepEqual(surfaceWords('SOMETHING~THING'), ['something']);
  assert.deepEqual(surfaceWords("DON'T-WANT"), ["don't", 'want']);
  assert.deepEqual(surfaceWords('THE-SAME'), ['the', 'same']);
  assert.deepEqual(surfaceWords('OTHER~ELSE~ANOTHER'), ['other']);
});

test('deriveGlossWords on kernel-v0 afraid matches its explication surface', () => {
  const corpus = loadCorpus();
  const afraid = corpus.find((c) => c.id === 'urn:kernel-v0:afraid')!;
  const words = deriveGlossWords(afraid.explication);
  // From the AST: BECAUSE(THINK(quote: CAN(HAPPEN ...VERY BAD... AFTER NOW), DON'T-WANT, MAYBE(HAPPEN)), FEEL BAD)
  for (const w of ['because', 'think', 'can', 'happen', 'very', 'bad', 'after', 'now', "don't", 'want', 'maybe', 'feel', 'someone', 'something', 'some', 'i']) {
    assert.ok(words.has(w), `missing '${w}' in ${[...words].sort()}`);
  }
  assert.ok(!words.has('afraid'), 'gloss must not contain the label itself');
});

test('jaccard', () => {
  assert.equal(jaccard(new Set(['a', 'b']), new Set(['b', 'c'])), 1 / 3);
  assert.equal(jaccard(new Set(), new Set()), 0);
});

// ---------------------------------------------------------------------------
// contexts
// ---------------------------------------------------------------------------

test('template banks: 24 templates each, single {w}, no probe-word leak', () => {
  const corpus = loadCorpus();
  const { probeItems } = buildItems(corpus.map((c) => c.id));
  const probeWords = probeItems.map((p) => p.word);
  for (const [bank, templates] of Object.entries(TEMPLATE_BANKS)) {
    assert.ok(templates.length >= 20, `${bank} has ${templates.length} < 20 templates`);
    checkNoProbeWordLeak(templates, probeWords);
    for (const t of templates) assert.equal(t.split('{w}').length - 1, 1, t);
  }
});

test('instantiate records the exact character span', () => {
  const c = instantiate('The cat was {w} the box.', 'inside');
  assert.equal(c.text, 'The cat was inside the box.');
  assert.equal(c.text.slice(c.charStart, c.charEnd), 'inside');
});

test('checkNoProbeWordLeak fails closed', () => {
  assert.throws(() => checkNoProbeWordLeak(['I want to break {w}.'], ['break']));
});

// ---------------------------------------------------------------------------
// wordnet
// ---------------------------------------------------------------------------

test('wordnet: lookup, morphy fallback, path similarities', () => {
  const wn = loadWordnet();
  assert.ok(wn.synsetCount > 100000);
  assert.ok(wn.lookup('happy', 'adj').length > 0);
  assert.ok(wn.lookup('archived').length > 0, 'morphy fallback archived->archive');
  // identical word: distance 0, sim 1
  const cat = wn.lookup('cat', 'noun');
  assert.equal(pathSimilarity(shortestPath(wn, cat, cat)), 1);
  // dog~cat closer than dog~celebration in the hypernym taxonomy
  const dog = wn.lookup('dog', 'noun');
  const celebration = wn.lookup('celebration', 'noun');
  const dCat = hypernymDistance(wn, dog, cat);
  const dCel = hypernymDistance(wn, dog, celebration);
  assert.ok(dCat < dCel, `d(dog,cat)=${dCat} !< d(dog,celebration)=${dCel}`);
  // extended graph reaches adjectives
  assert.ok(Number.isFinite(shortestPath(wn, wn.lookup('happy'), wn.lookup('sad'))));
});

// ---------------------------------------------------------------------------
// generated inputs (integration; requires `npm run inputs` to have run)
// ---------------------------------------------------------------------------

test('generated inputs exist, agree on pins and item order', (t) => {
  const files = [
    'items.json',
    'kernel-rdm.json',
    'baseline-gloss.json',
    'baseline-wordnet.json',
    'baseline-word2vec.json',
    'contexts.json',
    'freq-matched-pools.json',
  ];
  if (!files.every((f) => existsSync(join(INPUTS_DIR, f)))) {
    t.skip('inputs not generated yet (run npm run inputs)');
    return;
  }
  const read = (f: string): any => JSON.parse(readFileSync(join(INPUTS_DIR, f), 'utf8'));
  const arts = Object.fromEntries(files.map((f) => [f, read(f)]));
  const pin = corpusPin();
  const enc = arts['items.json'].encoderContentHash;
  for (const [name, a] of Object.entries(arts)) {
    assert.equal(a.encoderContentHash, enc, `${name} encoder hash`);
    assert.deepEqual(a.corpusPin, pin, `${name} corpus pin`);
  }
  const ids = arts['items.json'].items.map((i: any) => i.id);
  assert.equal(ids.length, 51);
  for (const f of ['baseline-gloss.json', 'baseline-wordnet.json', 'baseline-word2vec.json']) {
    assert.deepEqual(arts[f].ids, ids, `${f} item order`);
    const m = arts[f].similarity;
    assert.equal(m.length, 51);
    for (let i = 0; i < 51; i++) {
      assert.equal(m[i][i], 1, `${f} diagonal`);
      for (let j = 0; j < 51; j++) {
        assert.ok(Math.abs(m[i][j] - m[j][i]) < 1e-12, `${f} symmetry`);
        assert.ok(m[i][j] >= -1 - 1e-9 && m[i][j] <= 1 + 1e-9, `${f} range`);
      }
    }
  }
  assert.deepEqual(arts['kernel-rdm.json'].analysisIds, ids);
  assert.equal(arts['kernel-rdm.json'].ids.length, 54);
  assert.equal(arts['kernel-rdm.json'].projections.jl512.similarity.length, 54);
  // contexts: every probe word has >=20 contexts containing the word at the span
  const ctx = arts['contexts.json'];
  for (const it of arts['items.json'].items) {
    const list = ctx.perWord[it.word];
    assert.ok(list.length >= 20, `${it.word} has ${list.length} contexts`);
    for (const c of list) assert.equal(c.text.slice(c.charStart, c.charEnd), it.word);
  }
  // pools: every item has candidates, none equal to a probe word
  const pools = arts['freq-matched-pools.json'].pools;
  const probeSet = new Set(ids.map((_: string, k: number) => arts['items.json'].items[k].word));
  for (const it of arts['items.json'].items) {
    const pool = pools[it.word];
    assert.ok(pool.candidates.length >= 20, `${it.word} pool ${pool.candidates.length}`);
    for (const c of pool.candidates) assert.ok(!probeSet.has(c), `pool leak ${c}`);
  }
});
