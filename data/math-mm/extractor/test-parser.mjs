// test-parser.mjs — unit tests for parse-mm.mjs against known Metamath
// constructs (metamath.pdf spec §4.1–§4.2; demo0.mm-style examples).
// Run: node --test data/math-mm/extractor/test-parser.mjs

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseMM, tokenize, MMParseError } from './parse-mm.mjs';

test('tokenizer: whitespace splitting and line numbers', () => {
  const toks = [...tokenize('a b\n  c\n\nd')];
  assert.deepEqual(toks, [
    { tok: 'a', line: 1 }, { tok: 'b', line: 1 },
    { tok: 'c', line: 2 }, { tok: 'd', line: 4 },
  ]);
});

test('comments are consumed and attached to the next assertion', () => {
  const db = `
    $c wff |- p $.
    $( This describes P. $)
    ax-P $a |- p $.
    ax-Q $a |- p $.
  `;
  const { assertions } = parseMM(db);
  assert.equal(assertions[0].comment, 'This describes P.');
  assert.equal(assertions[1].comment, null); // not inherited
});

test('nested comments are rejected (spec: comments may not nest)', () => {
  assert.throws(() => parseMM('$( a $( b $) $)'), (e) => e.code === 'ERR_MM_NESTED_COMMENT');
});

test('demo0-style database: $c/$v/$f/$e/$a and full proof skipping', () => {
  // Condensed from metamath.pdf demo0.mm
  const db = `
    $c 0 + = -> ( ) term wff |- $.
    $v t r s P Q $.
    tt $f term t $.
    tr $f term r $.
    ts $f term s $.
    wp $f wff P $.
    wq $f wff Q $.
    tze $a term 0 $.
    tpl $a term ( t + r ) $.
    weq $a wff t = r $.
    wim $a wff ( P -> Q ) $.
    a1 $a |- ( t = r -> ( t = s -> r = s ) ) $.
    a2 $a |- ( t + 0 ) = t $.
    \${
      min $e |- P $.
      maj $e |- ( P -> Q ) $.
      mp $a |- Q $.
    $}
    th1 $p |- t = t $=
      tt tze tpl tt weq tt tt weq tt a2 tt tze tpl
      tt weq tt tze tpl tt weq tt tt weq wim tt a2
      tt tze tpl tt tt a1 mp mp $.
  `;
  const { constants, assertions, stats } = parseMM(db);
  assert.ok(constants.has('term') && constants.has('|-'));
  const byLabel = Object.fromEntries(assertions.map((a) => [a.label, a]));

  // syntax former: typecode + symbols split, mandatory vars in first-occurrence order
  assert.equal(byLabel.tpl.typecode, 'term');
  assert.deepEqual(byLabel.tpl.symbols, ['(', 't', '+', 'r', ')']);
  assert.deepEqual(byLabel.tpl.mandatoryVars.map((v) => `${v.name}:${v.typecode}`), ['t:term', 'r:term']);

  // $e hypotheses are mandatory and bring their variables into the frame
  assert.deepEqual(byLabel.mp.symbols, ['Q']);
  assert.deepEqual(byLabel.mp.eHyps.map((e) => e.label), ['min', 'maj']);
  assert.deepEqual(byLabel.mp.mandatoryVars.map((v) => v.name), ['Q', 'P']);

  // $p: statement captured, proof skipped
  assert.equal(byLabel.th1.kind, 'p');
  assert.deepEqual(byLabel.th1.symbols, ['t', '=', 't']);
  assert.equal(stats.pProofsSkipped, 1);
});

test('compressed proofs are skipped', () => {
  const db = `
    $c wff |- p q $.
    wp $a wff p $.
    wq $a wff q $.
    ax1 $a |- p $.
    th2 $p |- p $= ( wp ax1 ) AB $.
    ax2 $a |- q $.
  `;
  const { assertions, stats } = parseMM(db);
  assert.equal(stats.pProofsSkipped, 1);
  assert.deepEqual(assertions.map((a) => a.label), ['wp', 'wq', 'ax1', 'th2', 'ax2']);
});

test('scoping: inner $v/$f/$e deactivate at $}; $e outside scope not mandatory', () => {
  const db = `
    $c wff |- p $.
    \${
      $v x $.
      wx $f wff x $.
      hyp $e |- x $.
      inner $a |- p $.
    $}
    outer $a |- p $.
  `;
  const { assertions } = parseMM(db);
  const byLabel = Object.fromEntries(assertions.map((a) => [a.label, a]));
  assert.deepEqual(byLabel.inner.eHyps.map((e) => e.label), ['hyp']);
  assert.deepEqual(byLabel.inner.mandatoryVars.map((v) => v.name), ['x']); // via $e
  assert.deepEqual(byLabel.outer.eHyps, []);
  assert.deepEqual(byLabel.outer.mandatoryVars, []);
});

test('$d: only pairs over mandatory variables are attached, canonically sorted', () => {
  const db = `
    $c wff |- $.
    $v x y z $.
    wx $f wff x $.
    wy $f wff y $.
    wz $f wff z $.
    $d z x y $.
    axd $a |- y x $.
  `;
  const { assertions } = parseMM(db);
  // z is not mandatory (not in statement, no $e): pairs (z,x),(z,y) dropped, (x,y) kept
  assert.deepEqual(assertions[0].dPairs, [['x', 'y']]);
  assert.deepEqual(assertions[0].mandatoryVars.map((v) => v.name), ['y', 'x']); // first-occurrence order
});

test('fail-closed errors: includes, dup labels, $c in inner scope, unknown var, unclosed scope', () => {
  assert.throws(() => parseMM('$[ other.mm $]'), (e) => e.code === 'ERR_MM_INCLUDE_UNSUPPORTED');
  assert.throws(() => parseMM('$c wff $. a $a wff $. a $a wff $.'), (e) => e.code === 'ERR_MM_DUP_LABEL');
  assert.throws(() => parseMM('${ $c wff $. $}'), (e) => e.code === 'ERR_MM_C_IN_INNER_SCOPE');
  assert.throws(() => parseMM('$c wff |- $. $v x $. a $a |- x $.'), (e) => e.code === 'ERR_MM_NO_FLOATING_HYP');
  assert.throws(() => parseMM('${ $v x $.'), (e) => e.code === 'ERR_MM_UNCLOSED_SCOPE');
  assert.throws(() => parseMM('$c a $. th $p $= x $.'), (e) => e.code === 'ERR_MM_P_EMPTY');
  assert.throws(() => parseMM('$c a $. th $p a $= x'), (e) => e.code === 'ERR_MM_UNCLOSED_PROOF');
});

test('undeclared symbol tokens in $a are constants-by-usage? NO — they are plain tokens; parser keeps them', () => {
  // Metamath spec requires all math symbols to be declared; a full verifier
  // rejects undeclared tokens. This extractor tolerates them as opaque tokens
  // ONLY in the sense that it does not resolve them as variables; set.mm is
  // verified upstream by many independent verifiers, so declaration checking
  // is not this tool's job. Documented behaviour, tested here.
  const { assertions } = parseMM('$c wff $. w $a wff undeclared-token $.');
  assert.deepEqual(assertions[0].symbols, ['undeclared-token']);
  assert.deepEqual(assertions[0].mandatoryVars, []);
});

test('$p without $= proof is rejected', () => {
  assert.throws(() => parseMM('$c wff p $. w $p wff p $.'), (e) => e.code === 'ERR_MM_P_WITHOUT_PROOF');
});
