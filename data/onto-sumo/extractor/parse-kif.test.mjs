/**
 * Unit tests for the SUO-KIF reader + canonicaliser.
 * Run: node --test data/onto-sumo/extractor/parse-kif.test.mjs
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { tokenize, parseKif, canonical, op, isTerm, mentionedTerms } from './parse-kif.mjs';

test('tokenize skips comments but not inside strings', () => {
  const toks = tokenize('(documentation Foo EnglishLanguage "a ; not a comment") ; real comment\n(subclass A B)');
  const forms = parseKif('(documentation Foo EnglishLanguage "a ; not a comment") ; real comment\n(subclass A B)');
  assert.equal(forms.length, 2);
  assert.equal(forms[0].list[3].str, 'a ; not a comment');
});

test('canonical is a fixed point over re-parse', () => {
  const src = '(=>\n (instance ?X Human)\n (attribute ?X Living))';
  const c1 = canonical(parseKif(src)[0]);
  const c2 = canonical(parseKif(c1)[0]);
  assert.equal(c1, c2);
  assert.equal(c1, '(=> (instance ?X Human) (attribute ?X Living))');
});

test('string escapes round-trip', () => {
  const src = '(documentation X EnglishLanguage "line1\\nline2 with \\"quote\\"")';
  const form = parseKif(src)[0];
  assert.equal(form.list[3].str, 'line1\nline2 with "quote"');
  const c = canonical(form);
  // re-parsing the canonical yields the same string content
  assert.equal(parseKif(c)[0].list[3].str, 'line1\nline2 with "quote"');
});

test('op returns head atom', () => {
  assert.equal(op(parseKif('(subclass A B)')[0]), 'subclass');
  assert.equal(op(parseKif('((f x) y)')[0]), null); // head is a list
});

test('isTerm rejects variables, row-vars, numbers', () => {
  assert.ok(isTerm('Human'));
  assert.ok(isTerm('subclass'));
  assert.ok(!isTerm('?X'));
  assert.ok(!isTerm('@ROW'));
  assert.ok(!isTerm('3.14'));
  assert.ok(!isTerm('-2'));
});

test('mentionedTerms excludes logical ops and variables', () => {
  const m = mentionedTerms(parseKif('(=> (instance ?X Human) (and (attribute ?X Living) (not (equal ?X Foo))))')[0]);
  assert.ok(m.has('instance'));
  assert.ok(m.has('Human'));
  assert.ok(m.has('attribute'));
  assert.ok(m.has('Living'));
  assert.ok(m.has('Foo'));
  assert.ok(!m.has('and'));
  assert.ok(!m.has('not'));
  assert.ok(!m.has('equal'));
  assert.ok(!m.has('?X'));
});

test('unbalanced parens fail closed', () => {
  assert.throws(() => parseKif('(subclass A'), /ERR_KIF_PAREN/);
  assert.throws(() => parseKif('(subclass A))'), /ERR_KIF_PAREN/);
});

test('unterminated string fails closed', () => {
  assert.throws(() => tokenize('(documentation X EL "unterminated'), /ERR_KIF_STRING/);
});
