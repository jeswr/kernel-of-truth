import assert from 'node:assert/strict';
import { test } from 'node:test';
import { lemmaCandidates } from '../src/lemmatize.js';

test('surface form is always the first candidate', () => {
  assert.equal(lemmaCandidates('teacher')[0], 'teacher');
  assert.equal(lemmaCandidates('broken')[0], 'broken');
});

test('plural -s / -es / -ies', () => {
  assert.ok(lemmaCandidates('cats').includes('cat'));
  assert.ok(lemmaCandidates('boxes').includes('box'));
  assert.ok(lemmaCandidates('horses').includes('horse'));
  assert.ok(lemmaCandidates('memories').includes('memory'));
  assert.ok(lemmaCandidates('goes').includes('go'));
  assert.ok(!lemmaCandidates('miss').includes('mis'));
  assert.ok(!lemmaCandidates('this').includes('thi'));
});

test('past -ed with e-restoration and undoubling', () => {
  assert.ok(lemmaCandidates('jumped').includes('jump'));
  assert.ok(lemmaCandidates('liked').includes('like'));
  assert.ok(lemmaCandidates('patted').includes('pat'));
  assert.ok(lemmaCandidates('carried').includes('carry'));
});

test('progressive -ing with doubling rules', () => {
  assert.ok(lemmaCandidates('running').includes('run'));
  assert.ok(lemmaCandidates('making').includes('make'));
  assert.ok(lemmaCandidates('eating').includes('eat'));
  assert.ok(lemmaCandidates('telling').includes('tell'));
  assert.ok(!lemmaCandidates('telling').includes('tel'));
  assert.ok(lemmaCandidates('missing').includes('miss'));
});

test('comparative/superlative', () => {
  assert.ok(lemmaCandidates('bigger').includes('big'));
  assert.ok(lemmaCandidates('smallest').includes('small'));
  assert.ok(lemmaCandidates('happier').includes('happy'));
  assert.ok(lemmaCandidates('better').includes('good'));
  assert.ok(lemmaCandidates('worst').includes('bad'));
});

test('irregular verbs fold to base', () => {
  for (const [form, base] of [
    ['said', 'say'], ['saw', 'see'], ['felt', 'feel'], ['thought', 'think'],
    ['knew', 'know'], ['took', 'take'], ['gave', 'give'], ['found', 'find'],
    ['lost', 'lose'], ['made', 'make'], ['broke', 'break'], ['broken', 'break'],
    ['died', 'die'], ['was', 'be'], ['could', 'can'], ['heard', 'hear'],
  ] as const) {
    assert.ok(lemmaCandidates(form).includes(base), `${form} -> ${base}`);
  }
});

test('deliberate omissions hold', () => {
  // recline-"lay" must NOT fold to "lie" (kernel lie = the words)
  assert.ok(!lemmaCandidates('lay').includes('lie'));
  // PEOPLE is a prime exponent; never folded to person
  assert.ok(!lemmaCandidates('people').includes('person'));
});

test('no-strip guards common false stems', () => {
  assert.ok(!lemmaCandidates('thing').includes('th'));
  assert.ok(!lemmaCandidates('her').includes('h'));
  assert.ok(!lemmaCandidates('friend').includes('fri'));
  assert.ok(!lemmaCandidates('morning').includes('morn'));
});

test('deterministic: repeated calls agree', () => {
  assert.deepEqual(lemmaCandidates('running'), lemmaCandidates('running'));
});
