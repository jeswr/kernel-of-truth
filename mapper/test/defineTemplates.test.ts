import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  parseDefineQuestion,
  PINNED_RELATION_IRI,
  REL_SURFACE_TO_SHORTHAND,
  type DefineIndex,
} from '../src/defineTemplates.js';

// Minted urn:kot: URNs (^urn:kot:[a-z2-7]{10,}$) for the fixture terms.
const MITO = 'urn:kot:mitochondrionaa';
const ORG = 'urn:kot:organelleaaaaaa';
const APOP = 'urn:kot:apoptosisaaaaaa';
const PROC = 'urn:kot:processaaaaaaaa';
const REGULATES = 'urn:kot:regulatesrelaaa';
const PARTOF = 'urn:kot:partofrelaaaaaa';

// A label that collides onto two distinct concepts (must ABSTAIN).
const CELL_A = 'urn:kot:cellconceptaaaa';
const CELL_B = 'urn:kot:cellanatomyaaaa';

function fixtureIndex(): DefineIndex {
  return {
    labelToUrns: new Map<string, readonly string[]>([
      ['mitochondrion', [MITO]],
      ['organelle', [ORG]],
      ['apoptosis', [APOP]],
      ['process', [PROC]],
      ['cell', [CELL_A, CELL_B]], // collision
    ]),
    relationUrns: new Map<string, string>([
      ['regulates', REGULATES],
      ['part_of', PARTOF],
    ]),
  };
}

test('DEFINE templates -> retrieve query', () => {
  const idx = fixtureIndex();
  for (const q of ['what is the mitochondrion?', 'define mitochondrion', 'the definition of mitochondrion']) {
    const p = parseDefineQuestion(q, idx);
    assert.equal(p.kind, 'query', q);
    if (p.kind === 'query') {
      assert.deepEqual(p.query, { op: 'define', subject: MITO });
    }
  }
});

test('DEFINE-MATCH (is <TERM> a <GENUS> that <REL> <FILLER>) -> candidate query', () => {
  const idx = fixtureIndex();
  const p = parseDefineQuestion('is apoptosis a process that regulates cell?', idx);
  // "cell" collides -> FILLER abstains
  assert.equal(p.kind, 'abstain');
  if (p.kind === 'abstain') assert.equal(p.slot, 'FILLER');

  const p2 = parseDefineQuestion('is mitochondrion a organelle that part of cell', idx);
  assert.equal(p2.kind, 'abstain'); // filler "cell" collides
});

test('DEFINE-MATCH resolves fully when no slot collides', () => {
  const idx = fixtureIndex();
  const p = parseDefineQuestion('is apoptosis a process that regulates organelle', idx);
  assert.equal(p.kind, 'query');
  if (p.kind === 'query') {
    assert.deepEqual(p.query, {
      op: 'define',
      subject: APOP,
      candidate: { genus: [PROC], differentiae: [{ relation: REGULATES, filler: ORG }] },
    });
  }
});

test('"<TERM> is defined as <GENUS> that <REL> <FILLER>" form', () => {
  const idx = fixtureIndex();
  const p = parseDefineQuestion('apoptosis is defined as process that regulates organelle', idx);
  assert.equal(p.kind, 'query');
  if (p.kind === 'query') {
    assert.equal(p.query.op, 'define');
    assert.equal(p.query.subject, APOP);
  }
});

test('option-stem "which term means ..." -> candidate (no subject)', () => {
  const idx = fixtureIndex();
  const p = parseDefineQuestion('which term means process that regulates organelle', idx);
  assert.equal(p.kind, 'candidate');
  if (p.kind === 'candidate') {
    assert.deepEqual(p.candidate, {
      genus: [PROC],
      differentiae: [{ relation: REGULATES, filler: ORG }],
    });
  }
});

test('abstain on a colliding TERM label (never silently pick)', () => {
  const idx = fixtureIndex();
  const p = parseDefineQuestion('define cell', idx);
  assert.equal(p.kind, 'abstain');
  if (p.kind === 'abstain') {
    assert.equal(p.slot, 'TERM');
    assert.deepEqual([...p.candidates].sort(), [CELL_B, CELL_A].sort());
  }
});

test('unmapped: unknown label, unpinned REL, no template', () => {
  const idx = fixtureIndex();
  assert.equal(parseDefineQuestion('what is dragon', idx).kind, 'unmapped'); // no label
  assert.equal(parseDefineQuestion('is apoptosis a process that frobnicates organelle', idx).kind, 'unmapped'); // REL not pinned
  assert.equal(parseDefineQuestion('the sky is blue', idx).kind, 'unmapped'); // no template
});

test('fail-closed: REL surface pinned but shorthand not minted -> unmapped', () => {
  // "part of" is a pinned surface, but relationUrns lacks nothing here; drop it
  // to prove the fail-closed path when the mint bridge has no URN for it.
  const idx: DefineIndex = {
    labelToUrns: new Map<string, readonly string[]>([
      ['apoptosis', [APOP]],
      ['process', [PROC]],
      ['organelle', [ORG]],
    ]),
    relationUrns: new Map<string, string>([['regulates', REGULATES]]), // no part_of
  };
  const p = parseDefineQuestion('is apoptosis a process that part of organelle', idx);
  assert.equal(p.kind, 'unmapped');
});

test('determinism: same input + index => byte-identical parse', () => {
  const idx = fixtureIndex();
  const a = parseDefineQuestion('is apoptosis a process that regulates organelle', idx);
  const b = parseDefineQuestion('is apoptosis a process that regulates organelle', idx);
  assert.deepEqual(a, b);
});

test('pinned tables: closed 10-value inventory, IRIs are urn:onto-obo', () => {
  assert.equal(Object.keys(PINNED_RELATION_IRI).length, 10);
  assert.equal(Object.keys(REL_SURFACE_TO_SHORTHAND).length, 10);
  for (const iri of Object.values(PINNED_RELATION_IRI)) {
    assert.ok(iri.startsWith('urn:onto-obo:'));
  }
  // every surface maps to a shorthand present in the IRI table
  for (const sh of Object.values(REL_SURFACE_TO_SHORTHAND)) {
    assert.ok(sh in PINNED_RELATION_IRI, sh);
  }
});
