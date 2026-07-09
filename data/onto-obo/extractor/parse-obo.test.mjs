/**
 * Unit tests for the OBO parser + record assembly.
 * Run: node --test data/onto-obo/extractor/parse-obo.test.mjs
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  parseObo, tagMap, toUrn, isCurie, curiePrefix, stripIdValue,
  parseQuoted, parseXrefs, parseDef, parseSynonym,
} from './parse-obo.mjs';
import { stanzaToRecord } from './extract.mjs';

const PROV = { source: 's', sourceVersion: 'sha256:x', extractor: 'e', extractorVersion: '0', extractionDate: 'd' };
const ONT = { id: 'GO' };

test('toUrn normalises CURIEs and bare names', () => {
  assert.equal(toUrn('GO:0000018'), 'urn:onto-obo:GO_0000018');
  assert.equal(toUrn('regulates'), 'urn:onto-obo:regulates');
  assert.equal(toUrn('BFO:0000050'), 'urn:onto-obo:BFO_0000050');
});

test('curiePrefix / isCurie', () => {
  assert.equal(curiePrefix('GO:0000018'), 'GO');
  assert.equal(curiePrefix('regulates'), '');
  assert.ok(isCurie('RO:0002211'));
  assert.ok(!isCurie('regulates'));
});

test('stripIdValue drops " ! label" and {mods}', () => {
  assert.equal(stripIdValue('GO:0048308 ! organelle inheritance'), 'GO:0048308');
  assert.equal(stripIdValue('BFO:0000050 BFO:0000002 {all_only="true"} ! part of'), 'BFO:0000050 BFO:0000002');
  assert.equal(stripIdValue('regulates GO:0006310 ! DNA recombination'), 'regulates GO:0006310');
});

test('parseQuoted honours escapes', () => {
  const q = parseQuoted('"a \\"b\\" c\\nd" [x]');
  assert.equal(q.text, 'a "b" c\nd');
  assert.equal(q.rest, '[x]');
  assert.equal(parseQuoted('no quote'), null);
  assert.throws(() => parseQuoted('"unterminated'), /ERR_OBO_QUOTE/);
});

test('parseDef / parseXrefs', () => {
  const d = parseDef('"The distribution of X." [GOC:mcc, PMID:10873824]');
  assert.equal(d.text, 'The distribution of X.');
  assert.deepEqual(d.xrefs, ['GOC:mcc', 'PMID:10873824']);
  assert.deepEqual(parseXrefs('[]'), []);
  assert.deepEqual(parseDef('"no xrefs" []').xrefs, []);
});

test('parseSynonym extracts text + scope', () => {
  const s = parseSynonym('"mitochondrial inheritance" EXACT []');
  assert.equal(s.text, 'mitochondrial inheritance');
  assert.equal(s.scope, 'EXACT');
});

test('parseObo splits header and stanzas', () => {
  const text = [
    'format-version: 1.2',
    'data-version: releases/2026-06-15',
    '',
    '[Term]',
    'id: GO:0000001',
    'name: mitochondrion inheritance',
    'is_a: GO:0048308 ! organelle inheritance',
    '',
    '[Typedef]',
    'id: part_of',
    'is_transitive: true',
  ].join('\n');
  const { header, stanzas } = parseObo(text);
  assert.equal(header.length, 2);
  assert.equal(stanzas.length, 2);
  assert.equal(stanzas[0].type, 'Term');
  assert.equal(stanzas[1].type, 'Typedef');
  const m = tagMap(stanzas[0]);
  assert.equal(m.get('name')[0], 'mitochondrion inheritance');
});

test('stanzaToRecord builds genus-differentia logical definition', () => {
  const text = [
    '[Term]',
    'id: GO:0000018',
    'name: regulation of DNA recombination',
    'namespace: biological_process',
    'def: "Any process that modulates DNA recombination." [GOC:curators]',
    'is_a: GO:0051052 ! regulation of DNA metabolic process',
    'intersection_of: GO:0065007 ! biological regulation',
    'intersection_of: regulates GO:0006310 ! DNA recombination',
    'relationship: regulates GO:0006310 ! DNA recombination',
  ].join('\n');
  const st = parseObo(text).stanzas[0];
  const { record, genusDifferentia } = stanzaToRecord(st, ONT, PROV);
  assert.equal(record.id, 'urn:onto-obo:GO_0000018');
  assert.equal(record.kind, 'class');
  assert.equal(genusDifferentia, true);
  assert.equal(record.upgradeCandidate, true);
  assert.deepEqual(record.logicalDefinition.genus, ['urn:onto-obo:GO_0065007']);
  assert.deepEqual(record.logicalDefinition.differentiae, [
    { property: 'regulates', filler: 'urn:onto-obo:GO_0006310' },
  ]);
  // is_a + relationship in axioms; textual def OUTSIDE identity in annotations
  assert.ok(record.axioms.some((a) => a.rel === 'is_a' && a.target === 'urn:onto-obo:GO_0051052'));
  assert.ok(record.axioms.some((a) => a.rel === 'relationship' && a.property === 'regulates'));
  assert.equal(record.annotations.definition, 'Any process that modulates DNA recombination.');
  assert.equal('definition' in record, false); // never inside identity
});

test('stanzaToRecord: resolveRel adds a resolved relation URN to each differentia (8es)', () => {
  const text = [
    '[Term]',
    'id: GO:0000018',
    'name: regulation of DNA recombination',
    'intersection_of: GO:0065007 ! biological regulation',
    'intersection_of: regulates GO:0006310 ! DNA recombination',
  ].join('\n');
  const st = parseObo(text).stanzas[0];
  // stub resolver: shorthand -> canonical minted relation URN (as the real
  // buildRelationResolver would via the RO/BFO xref).
  const resolveRel = (tok) => ({ regulates: 'urn:onto-obo:RO_0002211' }[tok]
    ?? (() => { throw new Error('ERR_OBO_REL_UNRESOLVED: ' + tok); })());
  const { record } = stanzaToRecord(st, ONT, PROV, resolveRel);
  assert.deepEqual(record.logicalDefinition.differentiae, [
    { property: 'regulates', relation: 'urn:onto-obo:RO_0002211', filler: 'urn:onto-obo:GO_0006310' },
  ]);
  // without a resolver the pre-8es shape (no `relation`) is preserved
  const { record: bare } = stanzaToRecord(st, ONT, PROV);
  assert.deepEqual(bare.logicalDefinition.differentiae, [
    { property: 'regulates', filler: 'urn:onto-obo:GO_0006310' },
  ]);
});

test('stanzaToRecord: genus-only intersection is not genus-differentia', () => {
  const text = [
    '[Term]',
    'id: GO:0000002',
    'name: x',
    'intersection_of: GO:0000003 ! a',
    'intersection_of: GO:0000004 ! b',
  ].join('\n');
  const st = parseObo(text).stanzas[0];
  const { record, genusDifferentia } = stanzaToRecord(st, ONT, PROV);
  assert.equal(genusDifferentia, false);
  assert.equal(record.upgradeCandidate, false);
  assert.equal(record.logicalDefinition.genus.length, 2);
  assert.equal(record.logicalDefinition.differentiae.length, 0);
});

test('stanzaToRecord: Typedef relation axioms + characteristics', () => {
  const text = [
    '[Typedef]',
    'id: BFO:0000054',
    'name: realized in',
    'domain: BFO:0000017 ! realizable entity',
    'range: BFO:0000015 ! process',
    'inverse_of: BFO:0000055 ! realizes',
    'is_transitive: true',
    'holds_over_chain: RO:0002131 RO:0002131 ! x',
  ].join('\n');
  const st = parseObo(text).stanzas[0];
  const { record, kind } = stanzaToRecord(st, { id: 'RO' }, PROV);
  assert.equal(kind, 'relation');
  assert.ok(record.axioms.some((a) => a.rel === 'domain' && a.target === 'urn:onto-obo:BFO_0000017'));
  assert.ok(record.axioms.some((a) => a.rel === 'range' && a.target === 'urn:onto-obo:BFO_0000015'));
  assert.ok(record.axioms.some((a) => a.rel === 'inverse_of' && a.target === 'urn:onto-obo:BFO_0000055'));
  const chain = record.axioms.find((a) => a.rel === 'holds_over_chain');
  assert.deepEqual(chain.chain, ['urn:onto-obo:RO_0002131', 'urn:onto-obo:RO_0002131']);
  assert.ok(record.characteristics.includes('is_transitive'));
});

test('stanzaToRecord: obsolete term is flagged for exclusion', () => {
  const text = ['[Term]', 'id: GO:0000000', 'name: obsolete x', 'is_obsolete: true'].join('\n');
  const st = parseObo(text).stanzas[0];
  const r = stanzaToRecord(st, ONT, PROV);
  assert.equal(r.obsolete, true);
});
