import assert from 'node:assert/strict';
import { test } from 'node:test';
import { tokenize } from '../src/tokenize.js';

function norms(text: string): string[] {
  return tokenize(text).filter((t) => t.isWord).map((t) => t.norm);
}

test('basic words lowercase, punctuation split off', () => {
  assert.deepEqual(norms('The cat sat.'), ['the', 'cat', 'sat']);
  const toks = tokenize('The cat sat.');
  assert.equal(toks[toks.length - 1]!.isWord, false);
});

test('contraction expansion', () => {
  assert.deepEqual(norms("don't want"), ['do', 'not', 'want']);
  assert.deepEqual(norms("didn't"), ['did', 'not']);
  assert.deepEqual(norms("won't"), ['will', 'not']);
  assert.deepEqual(norms("can't"), ['can', 'not']);
  assert.deepEqual(norms("it's"), ['it', 'is']);
  assert.deepEqual(norms("let's"), ['let', 'us']);
  assert.deepEqual(norms("I'm"), ['i', 'am']);
  assert.deepEqual(norms("they'll"), ['they', 'will']);
});

test('noun possessive drops clitic', () => {
  assert.deepEqual(norms("Lily's toy"), ['lily', 'toy']);
});

test('expansion continuation flagged, surface span preserved', () => {
  const toks = tokenize("don't");
  assert.equal(toks.length, 2);
  assert.equal(toks[0]!.isExpansion, false);
  assert.equal(toks[1]!.isExpansion, true);
  assert.equal(toks[0]!.surface, "don't");
  assert.equal(toks[1]!.surface, "don't");
  assert.equal(toks[0]!.start, toks[1]!.start);
});

test('curly apostrophes normalized', () => {
  assert.deepEqual(norms('don’t'), ['do', 'not']);
});

test('numbers are non-word tokens', () => {
  const toks = tokenize('I have 3 cats');
  assert.deepEqual(toks.filter((t) => !t.isWord).map((t) => t.surface), ['3']);
});

test('offsets reconstruct surfaces', () => {
  const text = "Tom's dog didn't bark!";
  for (const t of tokenize(text)) {
    assert.equal(text.slice(t.start, t.end), t.surface);
  }
});
