/**
 * Unit tests for the WordNet 3.1 db-file parser.
 * Fixture lines are verbatim from wn3.1 dict files
 * (sha256 3f7d8be8ef6ecc7167d39b10d66954ec734280b5bdcd57f7d9eafe429d11c22a).
 * Run: node --test data/lexical-wn31/extractor/
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  parseDataLine, parseIndexLine, isHeaderLine, synsetId, AXIOM_RELS,
} from './parse.mjs';

const ENTITY =
  '00001740 03 n 01 entity 0 003 ~ 00001930 n 0000 ~ 00002137 n 0000 ~ 04431553 n 0000 | that which is perceived or known or inferred to have its own distinct existence (living or nonliving)  ';

test('noun line: entity (root)', () => {
  const s = parseDataLine(ENTITY);
  assert.equal(s.offset, '00001740');
  assert.equal(s.ssType, 'n');
  assert.equal(s.lexFile, 'noun.Tops');
  assert.deepEqual(s.words, [{ lemma: 'entity', marker: null, lexId: 0 }]);
  assert.equal(s.pointers.length, 3);
  assert.deepEqual(s.pointers[0], {
    sym: '~', offset: '00001930', pos: 'n', srcWord: 0, tgtWord: 0,
  });
  assert.ok(s.gloss.startsWith('that which is perceived'));
  assert.ok(!s.gloss.endsWith(' '), 'trailing whitespace trimmed');
});

const BREATHE =
  '00001740 29 v 04 breathe 0 take_a_breath 0 respire 0 suspire 3 021 * 00005041 v 0000 * 00004227 v 0000 + 03121972 a 0301 + 00832852 n 0303 + 04087945 n 0301 + 00257960 n 0105 + 00832852 n 0101 ^ 00004227 v 0103 ^ 00005041 v 0103 $ 00002325 v 0000 $ 00002573 v 0000 ~ 00002573 v 0000 ~ 00002724 v 0000 ~ 00002942 v 0000 ~ 00003826 v 0000 ~ 00004032 v 0000 ~ 00004227 v 0000 ~ 00005041 v 0000 ~ 00006697 v 0000 ~ 00007328 v 0000 ~ 00017024 v 0000 02 + 02 00 + 08 00 | draw air into, and expel out of, the lungs; "I can breathe better when the air is clean"; "The patient is respiring"  ';

test('verb line: breathe (multiword, frames, entailment)', () => {
  const s = parseDataLine(BREATHE);
  assert.equal(s.ssType, 'v');
  assert.equal(s.lexFile, 'verb.body');
  assert.equal(s.words.length, 4);
  assert.deepEqual(s.words[1], { lemma: 'take_a_breath', marker: null, lexId: 0 });
  assert.deepEqual(s.words[3], { lemma: 'suspire', marker: null, lexId: 3 });
  assert.equal(s.pointers.length, 21);
  assert.equal(s.pointers.filter((p) => p.sym === '*').length, 2);
  // frames: `02 + 02 00 + 08 00`
  assert.deepEqual(s.frames, [{ frame: 2, word: 0 }, { frame: 8, word: 0 }]);
  assert.ok(s.gloss.includes('"The patient is respiring"'));
});

const ABLE =
  '00001740 00 a 01 able 0 005 = 05207437 n 0000 = 05624029 n 0000 + 05624029 n 0101 + 05207437 n 0101 ! 00002098 a 0101 | (usually followed by `to\') having the necessary means or skill or know-how or authority to do something; "able to swim"  ';

test('adj line: able (lexical antonym word numbers)', () => {
  const s = parseDataLine(ABLE);
  assert.equal(s.ssType, 'a');
  const ant = s.pointers.find((p) => p.sym === '!');
  assert.deepEqual(ant, {
    sym: '!', offset: '00002098', pos: 'a', srcWord: 1, tgtWord: 1,
  });
});

// Satellite synset with an (a) syntactic marker on a word, from data.adj.
const SATELLITE =
  '00006032 00 s 02 emergent 0 emerging(a) 0 001 & 00005599 a 0000 | coming into existence; "an emergent republic"  ';

test('adj satellite: ss_type s, marker split, similar-to head', () => {
  const s = parseDataLine(SATELLITE);
  assert.equal(s.ssType, 's');
  assert.deepEqual(s.words[1], { lemma: 'emerging', marker: 'a', lexId: 0 });
  assert.deepEqual(s.pointers, [
    { sym: '&', offset: '00005599', pos: 'a', srcWord: 0, tgtWord: 0 },
  ]);
});

test('instance hypernym pointer symbol maps distinctly', () => {
  const line =
    '08975106 15 n 01 Aachen 0 002 @i 08652937 n 0000 #p 08853304 n 0000 | a city in western Germany  ';
  const s = parseDataLine(line);
  assert.equal(AXIOM_RELS[s.pointers[0].sym], 'instanceHypernym');
  assert.equal(AXIOM_RELS[s.pointers[1].sym], 'partHolonym');
});

test('fail-closed: truncated pointer list', () => {
  const bad =
    '00001740 03 n 01 entity 0 003 ~ 00001930 n 0000 | gloss';
  assert.throws(() => parseDataLine(bad), /ERR_WN_/);
});

test('fail-closed: trailing junk', () => {
  const bad =
    '00001740 03 n 01 entity 0 001 ~ 00001930 n 0000 junk | gloss';
  assert.throws(() => parseDataLine(bad), /ERR_WN_TRAILING/);
});

test('fail-closed: missing gloss separator', () => {
  assert.throws(
    () => parseDataLine('00001740 03 n 01 entity 0 000'),
    /ERR_WN_NO_GLOSS/,
  );
});

test('index line: sense-ordered offsets', () => {
  const line = 'friend n 5 3 @ ~ #m 5 3 10148305 09908301 09romm14 10787674 09908742';
  // deliberately malformed offset above must throw…
  assert.throws(() => parseIndexLine(line), /ERR_WN_IDX_OFFSETS/);
  const ok = 'friend n 5 3 @ ~ #m 5 3 10148305 09908301 10328123 10787674 09908742';
  const e = parseIndexLine(ok);
  assert.equal(e.lemma, 'friend');
  assert.equal(e.pos, 'n');
  assert.deepEqual(e.offsets, [
    '10148305', '09908301', '10328123', '10787674', '09908742',
  ]);
});

test('header detection + id scheme', () => {
  assert.ok(isHeaderLine('  1 This software and database is being provided'));
  assert.ok(!isHeaderLine(ENTITY));
  assert.equal(synsetId('a', '00006032'), 'urn:lexical-wn31:a-00006032');
});
