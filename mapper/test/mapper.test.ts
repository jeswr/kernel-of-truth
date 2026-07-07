import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { PRIME_EXPONENTS } from '../src/primes.js';
import {
  buildLexicon,
  loadManifestConcepts,
  surfaceOfLabel,
  targetKey,
  type Lexicon,
} from '../src/lexicon.js';
import { mapText, type AnnotatedToken, type Decision } from '../src/mapper.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..', '..');
const MANIFEST = join(REPO, 'data', 'kernel-v0', 'manifest.json');
const ENCODER_LEXICON = join(REPO, 'encoder', 'src', 'lexicon.ts');

function kernelLexicon(): Lexicon {
  return buildLexicon(loadManifestConcepts(MANIFEST));
}

function words(anns: readonly AnnotatedToken[]): AnnotatedToken[] {
  return anns.filter((a) => a.isWord);
}

function decisionOf(anns: readonly AnnotatedToken[], norm: string): Decision {
  const hit = anns.find((a) => a.isWord && a.norm === norm);
  assert.ok(hit !== undefined, `token ${norm} present`);
  return hit.decision;
}

test('prime names stay in sync with encoder/src/lexicon.ts', () => {
  const src = readFileSync(ENCODER_LEXICON, 'utf8');
  const names: string[] = [];
  const re = /p\(\s*(['"])((?:\\.|(?!\1).)*)\1\s*,/g;
  for (let m = re.exec(src); m !== null; m = re.exec(src)) {
    names.push(m[2]!.replace(/\\'/g, "'"));
  }
  assert.equal(names.length, 65, 'encoder chart has 65 primes');
  assert.deepEqual(
    PRIME_EXPONENTS.map((p) => p.name),
    names,
    'mapper exponent table order/names must mirror the encoder chart',
  );
});

test('label surface stripping', () => {
  assert.equal(surfaceOfLabel('lie (the words)'), 'lie');
  assert.equal(surfaceOfLabel('maker of (X is the maker of Y)'), 'maker of');
  assert.equal(surfaceOfLabel('happy'), 'happy');
});

test('lexicon compiles: 54 concepts, all primes reachable, ambiguity preserved', () => {
  const lex = kernelLexicon();
  const conceptIds = new Set(
    lex.entries.filter((e) => e.target.kind === 'concept').map((e) => targetKey(e.target)),
  );
  assert.equal(conceptIds.size, 54);
  const primeNames = new Set(
    lex.entries.filter((e) => e.target.kind === 'prime')
      .map((e) => (e.target.kind === 'prime' ? e.target.prime : '')),
  );
  assert.equal(primeNames.size, 65);
  // ambiguity preserved, never compiled away
  const kindTargets = new Set(
    lex.single.get('kind')!.map((e) => targetKey(e.target)),
  );
  assert.deepEqual([...kindTargets].sort(), ['prime:KIND', 'urn:kernel-v0:kind']);
});

test('single-word concept and prime mapping', () => {
  const lex = kernelLexicon();
  const anns = mapText('She was happy because you gave her a gift.', lex);
  assert.deepEqual(decisionOf(anns, 'happy'), {
    kind: 'concept',
    conceptId: 'urn:kernel-v0:happy',
  });
  assert.deepEqual(decisionOf(anns, 'because'), { kind: 'prime', prime: 'BECAUSE' });
  assert.deepEqual(decisionOf(anns, 'you'), { kind: 'prime', prime: 'YOU' });
  assert.deepEqual(decisionOf(anns, 'gift'), {
    kind: 'concept',
    conceptId: 'urn:kernel-v0:gift',
  });
  // inflected concept verb via irregular lemma
  assert.deepEqual(decisionOf(anns, 'gave'), {
    kind: 'concept',
    conceptId: 'urn:kernel-v0:give',
  });
  // "her" is unmapped (documented possessive gap)
  assert.deepEqual(decisionOf(anns, 'her'), { kind: 'none' });
});

test('lemmatized prime mapping', () => {
  const lex = kernelLexicon();
  const anns = mapText('He wanted more; he thought about it and said words.', lex);
  assert.deepEqual(decisionOf(anns, 'wanted'), { kind: 'prime', prime: 'WANT' });
  assert.deepEqual(decisionOf(anns, 'thought'), { kind: 'prime', prime: 'THINK' });
  assert.deepEqual(decisionOf(anns, 'said'), { kind: 'prime', prime: 'SAY' });
  assert.deepEqual(decisionOf(anns, 'words'), { kind: 'prime', prime: 'WORDS' });
  const wordsTok = anns.find((a) => a.norm === 'words');
  assert.equal(wordsTok!.lemma, 'word');
});

test('multiword longest-match-first', () => {
  const lex = kernelLexicon();
  // "a long time" must win over single-token "time" (WHEN~TIME)
  const anns = mapText('They played for a long time.', lex);
  const timeTok = anns.find((a) => a.norm === 'time')!;
  assert.deepEqual(timeTok.decision, { kind: 'prime', prime: 'A-LONG-TIME' });
  assert.equal(timeTok.phraseLen, 3);
  assert.equal(timeTok.phrasePos, 2);
  // "part of" -> concept part-of, not prime PART
  const anns2 = mapText('The wheel is part of the car.', lex);
  assert.deepEqual(decisionOf(anns2, 'part'), {
    kind: 'concept',
    conceptId: 'urn:kernel-v0:part-of',
  });
  // bare "part" -> prime PART
  const anns3 = mapText('He ate a part.', lex);
  assert.deepEqual(decisionOf(anns3, 'part'), { kind: 'prime', prime: 'PART' });
  // contraction-expanded phrase: "didn't want" -> DON'T-WANT
  const anns4 = mapText("She didn't want to go.", lex);
  const wantTok = anns4.find((a) => a.norm === 'want')!;
  assert.deepEqual(wantTok.decision, { kind: 'prime', prime: "DON'T-WANT" });
  assert.equal(wantTok.phraseLen, 3);
});

test('abstain-and-record: prime/concept collisions', () => {
  const lex = kernelLexicon();
  // "kind": prime KIND vs concept kind
  const d1 = decisionOf(mapText('She was a kind girl.', lex), 'kind');
  assert.equal(d1.kind, 'abstain');
  assert.deepEqual(
    (d1.kind === 'abstain' ? d1.candidates : []).map(targetKey).sort(),
    ['prime:KIND', 'urn:kernel-v0:kind'],
  );
  // "near": prime NEAR vs concept near; "inside" likewise
  assert.equal(decisionOf(mapText('The dog sat near the tree.', lex), 'near').kind, 'abstain');
  assert.equal(decisionOf(mapText('It was inside the box.', lex), 'inside').kind, 'abstain');
  // but "kind of" (phrase) is unambiguous -> prime KIND
  const d2 = decisionOf(mapText('It is a kind of bird.', lex), 'kind');
  assert.deepEqual(d2, { kind: 'prime', prime: 'KIND' });
});

test('abstain-and-record: surface/lemma collisions', () => {
  const lex = kernelLexicon();
  // "broken": surface concept broken + lemma break -> abstain
  const d1 = decisionOf(mapText('The toy was broken.', lex), 'broken');
  assert.equal(d1.kind, 'abstain');
  assert.deepEqual(
    (d1.kind === 'abstain' ? d1.candidates : []).map(targetKey).sort(),
    ['urn:kernel-v0:break', 'urn:kernel-v0:broken'],
  );
  // "lost": surface concept lost + irregular lemma lose -> abstain
  const d2 = decisionOf(mapText('She lost her doll.', lex), 'lost');
  assert.equal(d2.kind, 'abstain');
  // unambiguous inflection maps: "broke" -> break only
  assert.deepEqual(decisionOf(mapText('He broke the cup.', lex), 'broke'), {
    kind: 'concept',
    conceptId: 'urn:kernel-v0:break',
  });
});

test('abstain-and-record: copulas and "little"', () => {
  const lex = kernelLexicon();
  const d1 = decisionOf(mapText('The cat was small.', lex), 'was');
  assert.equal(d1.kind, 'abstain'); // BE-SOMEWHERE vs BE-SPEC
  const d2 = decisionOf(mapText('A little girl smiled.', lex), 'little');
  assert.equal(d2.kind, 'abstain'); // LITTLE~FEW vs SMALL
  // "there was" phrase resolves the copula -> THERE-IS
  const anns = mapText('Once there was a dragon.', lex);
  const thereTok = anns.find((a) => a.norm === 'there')!;
  assert.deepEqual(thereTok.decision, { kind: 'prime', prime: 'THERE-IS' });
});

test('unmapped words annotate as none', () => {
  const lex = kernelLexicon();
  const anns = mapText('The purple elephant trumpeted loudly.', lex);
  for (const norm of ['purple', 'elephant', 'trumpeted', 'loudly']) {
    assert.deepEqual(decisionOf(anns, norm), { kind: 'none' });
  }
});

test('annotated stream is suitable for E1 augmentation: spans + determinism', () => {
  const lex = kernelLexicon();
  const text = "Tim's friend didn't want the broken toy; he was sad for a long time.";
  const a = mapText(text, lex);
  const b = mapText(text, lex);
  assert.deepEqual(a, b, 'deterministic');
  for (const t of a) {
    assert.equal(text.slice(t.start, t.end), t.surface, 'span reconstructs surface');
  }
  // every word token carries a decision object of a known kind
  for (const t of words(a)) {
    assert.ok(['concept', 'prime', 'abstain', 'none'].includes(t.decision.kind));
  }
});
