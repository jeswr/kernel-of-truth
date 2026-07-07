/**
 * Tests for the E1 TS prep harness (bead kernel-of-truth-bk0):
 * artifact integrity, encoder-pin verification, control-table properties,
 * template split determinism + leak checks, and the transcription
 * cross-check against poc/e2/harness/items.ts (read-only).
 */

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import {
  buildLexicon,
  irregularBase,
  lemmaCandidates,
  loadManifestConcepts,
  mapText,
} from '@jeswr/kernel-mapper';
import { encoderContentHashQ } from '@jeswr/kernel-encoder';
import {
  E1_D_MODEL,
  INIT_STD,
  KERNEL_V0_DIR,
  PINNED_BQ512_HASH,
  REPO_DIR,
  loadConcepts,
  readInput,
  slugOf,
} from '../harness/common.js';
import { seededDerangement, seededGaussianRows } from '../harness/vectorTables.js';
import {
  CONCEPT_BANK,
  DEFINITIONAL_TYPES,
  PROBE_TYPES,
  seededSplit,
} from '../harness/templates.js';
import { decisionLine } from '../harness/lexiconArtifact.js';

interface LexArtifact {
  artifact: string;
  entries: { phrase: string[]; target: { kind: string; prime?: string; conceptId?: string }; source: string }[];
  lemmatizer: { irregular: Record<string, string>; noStrip: string[] };
  tokenizer: { special: Record<string, string[]>; pronounSIs: string[] };
}

interface VecArtifact {
  D: number;
  encoderContentHashQ: string;
  pinnedHash: string;
  initStd: number;
  frozenScale: number;
  ids: string[];
  kernel: number[][];
  shuffled: { seed: number; perm: number[] }[];
  randomFrozen: { seed: number; rows: number[][] }[];
}

test('encoder pin: kot-enc-Bq/1@512 hash matches the poc-design.md pin', () => {
  assert.equal(encoderContentHashQ({ D: E1_D_MODEL }), PINNED_BQ512_HASH);
});

test('mapper-lexicon artifact: entries match the live mapper, tables verified', () => {
  const art = readInput<LexArtifact>('mapper-lexicon.json');
  assert.equal(art.artifact, 'e1-mapper-lexicon');
  const live = buildLexicon(loadManifestConcepts(join(KERNEL_V0_DIR, 'manifest.json')));
  assert.equal(art.entries.length, live.entries.length);
  for (let i = 0; i < live.entries.length; i++) {
    assert.deepEqual(art.entries[i]!.phrase, live.entries[i]!.phrase);
    assert.deepEqual(art.entries[i]!.target, live.entries[i]!.target);
  }
  // transcribed tables agree with exported mapper behaviour (spot + exhaustive)
  for (const [k, v] of Object.entries(art.lemmatizer.irregular)) {
    assert.equal(irregularBase(k), v, `irregular ${k}`);
  }
  assert.equal(irregularBase('went'), 'go');
  assert.deepEqual(lemmaCandidates('running'), ['running', 'runn', 'runne', 'run']);
});

test('parity fixture: stream hash + lemma table present and self-consistent', () => {
  const fx = readInput<{
    decisionStreamSha256: string;
    lemmaTable: Record<string, string[]>;
    counts: { wordTokens: number };
    sampleAnnotations: string[][];
  }>('mapper-parity-fixture.json');
  assert.match(fx.decisionStreamSha256, /^[0-9a-f]{64}$/);
  assert.ok(fx.counts.wordTokens > 3_000_000);
  assert.ok(Object.keys(fx.lemmaTable).length > 10_000);
  for (const [w, cands] of Object.entries(fx.lemmaTable).slice(0, 500)) {
    assert.deepEqual(lemmaCandidates(w), cands, `lemmaTable ${w}`);
  }
  assert.ok(fx.sampleAnnotations.length === 25);
});

test('decisionLine format matches the python contract', () => {
  const lex = buildLexicon(loadManifestConcepts(join(KERNEL_V0_DIR, 'manifest.json')));
  const anns = mapText('The happy teacher said hello.', lex).filter((t) => t.isWord);
  const lines = anns.map(decisionLine);
  assert.deepEqual(lines, [
    'the|none||1|0',
    'happy|concept|urn:kernel-v0:happy|1|0',
    'teacher|concept|urn:kernel-v0:teacher|1|0',
    'said|prime|prime:SAY|1|0',
    'hello|none||1|0',
  ]);
});

test('vector tables: pin stamped, unit-norm kernel rows, derangements, dims', () => {
  const vt = readInput<VecArtifact>('vector-tables-d512.json');
  assert.equal(vt.D, E1_D_MODEL);
  assert.equal(vt.encoderContentHashQ, PINNED_BQ512_HASH);
  assert.equal(vt.pinnedHash, PINNED_BQ512_HASH);
  assert.equal(vt.initStd, INIT_STD);
  assert.ok(Math.abs(vt.frozenScale - INIT_STD * Math.sqrt(E1_D_MODEL)) < 1e-12);
  assert.equal(vt.ids.length, 54);
  assert.deepEqual(vt.ids, [...vt.ids].sort());
  assert.equal(vt.kernel.length, 54);
  for (const row of vt.kernel) {
    assert.equal(row.length, E1_D_MODEL);
    const n = Math.sqrt(row.reduce((a, x) => a + x * x, 0));
    assert.ok(Math.abs(n - 1) < 1e-6, `kernel row norm ${n}`);
  }
  assert.equal(vt.shuffled.length, 5);
  for (const s of vt.shuffled) {
    assert.equal(s.perm.length, 54);
    assert.deepEqual([...s.perm].sort((a, b) => a - b), Array.from({ length: 54 }, (_, i) => i));
    assert.ok(s.perm.every((v, i) => v !== i), `seed ${s.seed} not a derangement`);
  }
  assert.equal(vt.randomFrozen.length, 5);
  for (const r of vt.randomFrozen) {
    assert.equal(r.rows.length, 54);
    assert.equal(r.rows[0]!.length, E1_D_MODEL);
  }
  // norm-matching sanity: mean random row norm within 5% of frozenScale
  const mean =
    vt.randomFrozen[0]!.rows.reduce((a, r) => a + Math.sqrt(r.reduce((x, y) => x + y * y, 0)), 0) / 54;
  assert.ok(Math.abs(mean - vt.frozenScale) / vt.frozenScale < 0.05);
});

test('seeded generators are deterministic and seed-distinct', () => {
  const a = seededDerangement('e1/shuffle/0', 54);
  const b = seededDerangement('e1/shuffle/0', 54);
  assert.deepEqual(a, b);
  const c = seededDerangement('e1/shuffle/1', 54);
  assert.notDeepEqual(a.perm, c.perm);
  const g1 = seededGaussianRows('e1/randfrozen/0', 3, 16, 0.02);
  const g2 = seededGaussianRows('e1/randfrozen/0', 3, 16, 0.02);
  assert.deepEqual(g1, g2);
});

test('templates: slots, split halves, bank coverage, leak-free', () => {
  assert.equal(DEFINITIONAL_TYPES.length, 16);
  for (const f of DEFINITIONAL_TYPES) {
    assert.equal(f.split('{c}').length, 2, f);
    assert.equal(f.split('{gloss}').length, 2, f);
    assert.ok(f.indexOf('{gloss}') < f.indexOf('{c}'), f);
  }
  const split = seededSplit('e1/templates/def-heldout', 16);
  assert.equal(split.first.length, 8);
  assert.equal(split.second.length, 8);
  assert.deepEqual(
    [...split.first, ...split.second].sort((a, b) => a - b),
    Array.from({ length: 16 }, (_, i) => i),
  );
  // determinism
  assert.deepEqual(seededSplit('e1/templates/def-heldout', 16), split);

  const concepts = loadConcepts();
  assert.equal(concepts.length, 54);
  for (const c of concepts) {
    const bank = CONCEPT_BANK[slugOf(c.id)];
    assert.ok(bank !== undefined, `no bank for ${c.id}`);
    assert.ok(PROBE_TYPES[bank].length === 8);
    assert.ok(c.gloss.length > 10, `gloss missing for ${c.id}`);
  }

  // committed artifact agrees with the module
  const art = readInput<{
    definitional: { types: string[]; split: { dev: number[]; heldOut: number[] } };
    concepts: { slug: string }[];
  }>('cloze-templates.json');
  assert.deepEqual(art.definitional.types, DEFINITIONAL_TYPES);
  assert.deepEqual(art.definitional.split.dev, split.first);
  assert.deepEqual(art.definitional.split.heldOut, split.second);
  assert.equal(art.concepts.length, 54);

  // leak check: no frame word maps to a concept / abstains with one
  const lex = buildLexicon(loadManifestConcepts(join(KERNEL_V0_DIR, 'manifest.json')));
  const frames = [...DEFINITIONAL_TYPES, ...Object.values(PROBE_TYPES).flat()];
  for (const frame of frames) {
    const text = frame.replace(/\{c\}/g, ' ').replace(/\{gloss\}/g, ' ');
    for (const t of mapText(text, lex)) {
      if (!t.isWord) continue;
      const d = t.decision;
      assert.notEqual(d.kind, 'concept', `${t.norm} in '${frame}'`);
      if (d.kind === 'abstain') {
        assert.ok(
          d.candidates.every((c) => c.kind !== 'concept'),
          `${t.norm} abstains with concept candidate in '${frame}'`,
        );
      }
    }
  }
});

test('CONCEPT_BANK transcription matches poc/e2/harness/items.ts (read-only)', () => {
  const src = readFileSync(join(REPO_DIR, 'poc', 'e2', 'harness', 'items.ts'), 'utf8');
  const re = /^\s*(?:'([a-z-]+)'|([a-z]+)):\s*\['([a-z-]+)',\s*'(\w+)'\]/gm;
  const e2: Record<string, string> = {};
  let m: RegExpExecArray | null;
  while ((m = re.exec(src)) !== null) {
    e2[m[1] ?? m[2]!] = m[4]!;
  }
  assert.ok(Object.keys(e2).length >= 51, `parsed only ${Object.keys(e2).length} e2 PROBE entries`);
  for (const [slug, bank] of Object.entries(e2)) {
    assert.equal(CONCEPT_BANK[slug], bank, `bank mismatch for ${slug}`);
  }
  // the three multiword concepts are e1-only additions
  for (const s of ['has-part', 'maker-of', 'part-of']) {
    assert.equal(CONCEPT_BANK[s], 'rel');
  }
});
