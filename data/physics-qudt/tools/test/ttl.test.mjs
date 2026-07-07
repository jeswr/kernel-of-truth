import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseTurtle, RDF_TYPE, iris, lits } from '../ttl.mjs';

test('prefixes, subject blocks, a-verb, object lists', () => {
  const { subjects } = parseTurtle(`
@prefix ex: <http://ex.org/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
ex:A
  a qudt:Unit, qudt:DerivedUnit ;
  qudt:symbol "m" ;
  ex:ref ex:B ;
  ex:ref ex:C .
`);
  const a = subjects.get('http://ex.org/A');
  assert.deepEqual(iris(a, RDF_TYPE), ['http://qudt.org/schema/qudt/Unit', 'http://qudt.org/schema/qudt/DerivedUnit']);
  assert.deepEqual(iris(a, 'http://ex.org/ref'), ['http://ex.org/B', 'http://ex.org/C']);
  assert.equal(lits(a, 'http://qudt.org/schema/qudt/symbol')[0].v, 'm');
});

test('numeric literals keep raw lexical form and classify datatype', () => {
  const { subjects } = parseTurtle(`@prefix ex: <http://e/> .
ex:U ex:m 0.0174532925199433 ; ex:sn 1.0E-3 ; ex:i -42 ; ex:b true .`);
  const u = subjects.get('http://e/U');
  assert.equal(lits(u, 'http://e/m')[0].raw, '0.0174532925199433');
  assert.equal(lits(u, 'http://e/m')[0].dt, 'http://www.w3.org/2001/XMLSchema#decimal');
  assert.equal(lits(u, 'http://e/sn')[0].dt, 'http://www.w3.org/2001/XMLSchema#double');
  assert.equal(lits(u, 'http://e/i')[0].raw, '-42');
  assert.equal(lits(u, 'http://e/b')[0].v, 'true');
});

test('strings: escapes, langs, datatypes, long strings with quotes+backslashes', () => {
  const { subjects } = parseTurtle(`@prefix ex: <http://e/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
ex:S ex:p "a\\"b\\\\c" ; ex:q "Grad"@de ; ex:r """multi
line \\"with\\" $\\\\frac{1}{2}$"""^^qudt:LatexString ; ex:s "x.y" .`);
  const s = subjects.get('http://e/S');
  assert.equal(lits(s, 'http://e/p')[0].v, 'a"b\\c');
  assert.equal(lits(s, 'http://e/q')[0].lang, 'de');
  const r = lits(s, 'http://e/r')[0];
  assert.ok(r.v.includes('line "with" $\\frac{1}{2}$'));
  assert.equal(r.dt, 'http://qudt.org/schema/qudt/LatexString');
});

test('blank-node property lists (QUDT factor units), trailing semicolons', () => {
  const { subjects } = parseTurtle(`@prefix ex: <http://e/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
unit:X
  qudt:hasFactorUnit [
    a qudt:FactorUnit ;
    qudt:exponent -2 ;
    qudt:hasUnit unit:FT ;
  ] ;
  qudt:hasFactorUnit [
    qudt:exponent 1 ;
    qudt:hasUnit unit:LB ;
  ] .`);
  const x = subjects.get('http://qudt.org/vocab/unit/X');
  const fus = x.get('http://qudt.org/schema/qudt/hasFactorUnit');
  assert.equal(fus.length, 2);
  assert.equal(fus[0].t, 'bnode');
  assert.equal(lits(fus[0].props, 'http://qudt.org/schema/qudt/exponent')[0].raw, '-2');
  assert.deepEqual(iris(fus[1].props, 'http://qudt.org/schema/qudt/hasUnit'), ['http://qudt.org/vocab/unit/LB']);
});

test('comments outside strings; # inside strings preserved', () => {
  const { subjects } = parseTurtle(`@prefix ex: <http://e/> . # trailing
# full-line comment
ex:A ex:p "keep # this" . # another`);
  assert.equal(lits(subjects.get('http://e/A'), 'http://e/p')[0].v, 'keep # this');
});

test('pname local names: dots inside kept, trailing dot is the terminator', () => {
  const { subjects } = parseTurtle(`@prefix ex: <http://e/> .
ex:A ex:p ex:B.C.`);
  assert.deepEqual(iris(subjects.get('http://e/A'), 'http://e/p'), ['http://e/B.C']);
});

test('fail closed: collections, undeclared prefix, unterminated string', () => {
  assert.throws(() => parseTurtle('@prefix ex: <http://e/> .\nex:A ex:p (1 2) .'), /ERR_TTL_COLLECTION/);
  assert.throws(() => parseTurtle('ex:A ex:p ex:B .'), /ERR_TTL_PREFIX/);
  assert.throws(() => parseTurtle('@prefix ex: <http://e/> .\nex:A ex:p "x .'), /ERR_TTL_STR/);
});
