#!/usr/bin/env node
/**
 * B-E0 instrument self-test ($0 mock gate): canonical example sentences per
 * recognised pattern, checked for (i) expected engagement shape, (ii) every
 * emitted fragment passing the encoder validation gates, minting a URN, and
 * surviving the render->parse round trip. Green REQUIRED before the corpus
 * census runs (freeze-discipline: a census with a broken instrument measures
 * nothing).
 *
 * Usage: node poc/compression-census/test-parser.mjs
 */
import { strict as assert } from 'node:assert';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildLexicon, loadManifestConcepts, mapText } from '../../mapper/dist/src/index.js';
import {
  validateExplication,
  mintCompositeUrn,
  renderExplication,
  parseRendered,
  canonicalJson,
} from '../../encoder/dist/src/index.js';
import { readFileSync } from 'node:fs';
import { scanSentence, classifyFragment } from './parser.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..');

// Combined lexicon: kernel-v0 concepts + molecules-v0 labels/synonyms
// (the molecules-v0-rung instrument, m0b continuity; the established
// combination convention of mapper/m0/results-molecules-v0/lexicon-collisions.mjs).
const kernel = loadManifestConcepts(join(REPO, 'data', 'kernel-v0', 'manifest.json'));
const molManifest = JSON.parse(readFileSync(join(REPO, 'data', 'molecules-v0', 'manifest.json'), 'utf8'));
const molLabels = molManifest.molecules.map((m) => ({ id: m.id, label: m.label }));
const molSynonyms = molManifest.molecules.flatMap((m) =>
  (m.corpusLemmas ?? []).filter((l) => l !== m.label).map((l) => ({ id: m.id, label: l })),
);
const lexicon = buildLexicon([...kernel, ...molLabels, ...molSynonyms]);

function scan(text, profile = 'strict') {
  const toks = mapText(text, lexicon);
  return scanSentence(toks, profile);
}

function checkFragments(res, label) {
  for (const f of res.fragments) {
    validateExplication(f.explication); // throws on any gate error
    const urn = mintCompositeUrn(f.explication);
    assert.match(urn, /^urn:kot:b[a-z2-7]+$/, `${label}: URN`);
    const back = parseRendered(renderExplication(f.explication));
    assert.equal(canonicalJson(back), canonicalJson(f.explication), `${label}: render round-trip`);
  }
}

let n = 0;
const t = (label, fn) => {
  n++;
  try {
    fn();
    console.log(`ok ${n} - ${label}`);
  } catch (e) {
    console.error(`FAIL ${n} - ${label}\n${e.stack}`);
    process.exitCode = 1;
  }
};

// A concept-covered content word is needed; kernel-v0/molecules-v0 cover
// e.g. water/dog/... — resolve a few at runtime so fixtures track the kernel.
const probe = (word) => {
  const toks = mapText(word, lexicon);
  return toks[0]?.decision.kind === 'concept';
};
const covered = ['water', 'dog', 'cat', 'house', 'fire'].filter(probe);
console.log(`# covered probe words available: ${covered.join(', ') || '(none)'}`);
assert.ok(covered.length >= 1, 'need at least one covered content word for fixtures');
const W = covered[0]; // e.g. 'water'

t('is-a: "someone sees the water" strict abstains on "the"', () => {
  const res = scan(`someone sees the ${W}`, 'strict');
  assert.equal(res.fragments.filter((f) => f.expandedWords >= 2).length, 0);
  assert.ok(res.causes.has('definite-article'), `causes: ${[...res.causes.keys()]}`);
});

t('permissive-det parses "someone sees the water"', () => {
  const res = scan(`someone sees the ${W}`, 'permissive-det');
  assert.equal(res.fragments.length, 1);
  const f = res.fragments[0];
  assert.equal(f.stratum, 'simple-clause');
  assert.equal(f.expandedWords, 4);
  assert.equal(f.explication.clauses[0].pred, 'SEE');
  checkFragments(res, 'permissive');
});

t('is-a: "something is a kind of water"', () => {
  const res = scan(`something is a kind of ${W}`, 'strict');
  assert.equal(res.fragments.length, 1);
  const f = res.fragments[0];
  assert.equal(f.stratum, 'is-a');
  const c = f.explication.clauses[0];
  assert.equal(c.pred, 'BE-SPEC');
  assert.equal(c.roles.attribute.head.kind, 'kindFrame');
  checkFragments(res, 'kind-of');
});

t('there-is: "there is water here"? (bare THERE-IS)', () => {
  const res = scan(`there is ${W}`, 'strict');
  assert.equal(res.fragments.length, 1);
  assert.equal(res.fragments[0].stratum, 'is-a');
  assert.equal(res.fragments[0].explication.clauses[0].pred, 'THERE-IS');
  checkFragments(res, 'there-is');
});

t('clause-AND: "someone sees water and someone hears water"', () => {
  const res = scan(`someone sees ${W} and someone hears ${W}`, 'strict');
  assert.equal(res.fragments.length, 1);
  const f = res.fragments[0];
  assert.equal(f.stratum, 'clause-AND');
  assert.equal(f.clauseCount, 2);
  checkFragments(res, 'and');
});

t('operator-complex: negation via do-support ("someone did not see water")', () => {
  const res = scan(`someone did not see ${W}`, 'strict');
  assert.equal(res.fragments.length, 1);
  const f = res.fragments[0];
  assert.equal(f.stratum, 'operator-complex');
  assert.equal(f.explication.clauses[0].op, 'NOT');
  checkFragments(res, 'not');
});

t("don't-want maps to the DON'T-WANT prime, not NOT(WANT)", () => {
  const res = scan(`someone does not want ${W}`, 'strict');
  assert.equal(res.fragments.length, 1);
  const c = res.fragments[0].explication.clauses[0];
  assert.equal(c.type, 'pred');
  assert.equal(c.pred, "DON'T-WANT");
  checkFragments(res, 'dont-want');
});

t('operator-complex: "if someone sees water, someone can hear water"', () => {
  const res = scan(`if someone sees ${W}, someone can hear ${W}`, 'strict');
  assert.equal(res.fragments.length, 1);
  const c = res.fragments[0].explication.clauses[0];
  assert.equal(c.op, 'IF');
  assert.equal(c.args[1].op, 'CAN');
  checkFragments(res, 'if-can');
});

t('because: "someone died because someone saw water" (cause,effect order)', () => {
  const res = scan(`someone died because someone saw ${W}`, 'strict');
  assert.equal(res.fragments.length, 1);
  const c = res.fragments[0].explication.clauses[0];
  assert.equal(c.op, 'BECAUSE');
  assert.equal(c.args[0].type, 'pred'); // cause = saw-clause
  assert.equal(c.args[1].roles.time.op, 'BEFORE'); // effect past tense
  checkFragments(res, 'because');
});

t('tense: past -> BEFORE@NOW adjunct; "will" -> AFTER@NOW', () => {
  const res1 = scan(`someone saw ${W}`, 'strict');
  assert.equal(res1.fragments[0].explication.clauses[0].roles.time.op, 'BEFORE');
  const res2 = scan(`someone will see ${W}`, 'strict');
  assert.equal(res2.fragments[0].explication.clauses[0].roles.time.op, 'AFTER');
  checkFragments(res1, 'past');
  checkFragments(res2, 'future');
});

t('WANT + infinitival complement binds coreferent subject', () => {
  const res = scan(`someone wants to see ${W}`, 'strict');
  assert.equal(res.fragments.length, 1);
  const e = res.fragments[0].explication;
  const c = e.clauses[0];
  assert.equal(c.pred, 'WANT');
  assert.equal(c.roles.experiencer.bind, 2);
  assert.equal(c.roles.complement.clause.roles.experiencer.index, 2);
  assert.equal(e.referents.length, 2);
  checkFragments(res, 'want-to');
});

t('OR-forfeit (clause level): "someone sees water or someone hears water"', () => {
  const res = scan(`someone sees ${W} or someone hears ${W}`, 'strict');
  // each disjunct still rolls on its own; the JOINT span is the forfeit
  assert.equal(res.fragments.length, 2);
  assert.equal(res.orForfeits.filter((f) => f.level === 'clause').length, 1);
  checkFragments(res, 'or-clause');
});

t('OR-forfeit (NP level) abstains the clause and records the forfeit', () => {
  const second = covered[1] ?? W;
  const res = scan(`someone sees ${W} or ${second}`, 'strict');
  assert.equal(res.fragments.filter((f) => f.expandedWords >= 3).length, 0);
  assert.equal(res.orForfeits.filter((f) => f.level === 'np').length, 1);
  assert.ok(res.causes.has('np-or'));
});

t('pronoun anaphora abstains', () => {
  const res = scan(`she sees ${W}`, 'strict');
  assert.equal(res.fragments.filter((f) => f.startTok === 0).length, 0);
  assert.ok(res.causes.has('pronoun-anaphor'));
});

t('open-class verbs abstain', () => {
  const res = scan('someone jumped', 'strict');
  assert.equal(res.fragments.length, 0);
  assert.ok(res.causes.has('open-class-verb'));
});

t('live sense guard: "someone lived in a house" abstains', () => {
  const res = scan('someone lived in a house', 'strict');
  assert.equal(res.fragments.filter((f) => f.explication.clauses[0]?.pred === 'LIVE').length, 0);
  assert.ok(res.causes.has('live-sense-guard'));
});

t('bare plural abstains; quantified plural parses', () => {
  if (!probe('dog')) {
    console.log('  # skip: dog not covered in this kernel instance');
    return;
  }
  const res1 = scan('someone sees dogs', 'strict');
  assert.ok(res1.causes.has('bare-plural'));
  const res2 = scan('someone sees two dogs', 'strict');
  assert.equal(res2.fragments.length, 1);
  assert.equal(res2.fragments[0].explication.clauses[0].roles.stimulus.quant, 'TWO');
  checkFragments(res2, 'plural');
});

t('classifyFragment strata are as pre-named', () => {
  assert.equal(classifyFragment([{ type: 'op', op: 'NOT', args: [] }]), 'operator-complex');
  assert.equal(classifyFragment([{ type: 'pred', pred: 'DO', roles: {} }, { type: 'pred', pred: 'DO', roles: {} }]), 'clause-AND');
  assert.equal(classifyFragment([{ type: 'pred', pred: 'BE-SPEC', roles: {} }]), 'is-a');
  assert.equal(classifyFragment([{ type: 'pred', pred: 'SEE', roles: {} }]), 'simple-clause');
});

t('maximal-prefix fragment: trailing PP ends the fragment, clause still rolls', () => {
  const res = scan(`someone saw ${W} in a house`, 'strict');
  assert.equal(res.fragments.length, 1);
  assert.equal(res.fragments[0].expandedWords, 3); // "someone saw water"
  checkFragments(res, 'prefix-maximal');
});

console.log(`# self-test done: ${n} cases`);
