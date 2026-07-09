/**
 * B-RT — roll-up / expansion round-trip property suite (Tier 0, $0).
 *
 * Pre-declared bar: 100% (docs/next/io-compression-ideas.md §3.3 — "any
 * failure is a bug, not a result"; contrast the linter's ≥0.95 renderer bar).
 * Census node B-RT of bead kernel-of-truth-5iu; the X1-suite pattern
 * (seeded generator + validity-preserving mutator), depth × clause-count
 * stratified.
 *
 * Properties, per stratified original AND per single-edit mutant:
 *   P1  URN determinism: mintCompositeUrn twice -> byte-identical URN, and
 *       the URN is stable under a JSON serialise/parse cycle of the AST.
 *   P2  Dictionary round-trip (exact-by-id): add -> expand -> canonicalJson
 *       identical; re-minting the expanded AST yields the same URN.
 *   P3  Renderer round-trip: parseRendered(renderExplication(ast)) is the
 *       IDENTITY (canonicalJson equality), the re-parsed AST re-validates,
 *       and its URN is unchanged.
 *   P4  Content addressing separates edits: a validity-preserving single
 *       edit yields a DIFFERENT URN (identical URNs would collapse distinct
 *       composites in the dictionary).
 *   P5  Encode equivalence (subsample): encodeExplication of the original
 *       and of the render->parse round-tripped AST are byte-identical
 *       Float64Arrays (X0 determinism carried through the round trip).
 *
 * Strata: depth ∈ {1,2,3,4,6,8,12} × topClauses ∈ {1,2,4,8,16,32}, feasible
 * combos only (synth.ts feasibility: depth-1 ≤ 32-topClauses), SEEDS_PER_CELL
 * seeded originals per cell + one mutant each (mutator may return null on
 * rare edit-free items; those are counted and reported, X1 convention).
 */

import { strict as assert } from 'node:assert';
import { test } from 'node:test';
import { canonicalJson, type Explication } from '../src/ast.js';
import { encodeExplication } from '../src/encoder.js';
import { generateExplication, mutateExplication } from '../src/synth.js';
import { validateExplication } from '../src/validate.js';
import { CompositeDictionary, mintCompositeUrn } from '../src/rollup.js';
import { parseRendered, renderExplication } from '../src/render.js';

const DEPTHS = [1, 2, 3, 4, 6, 8, 12] as const;
const TOP_CLAUSES = [1, 2, 4, 8, 16, 32] as const;
const SEEDS_PER_CELL = 25;

interface Cell {
  readonly depth: number;
  readonly topClauses: number;
}

const cells: Cell[] = [];
for (const depth of DEPTHS) {
  for (const topClauses of TOP_CLAUSES) {
    if (depth - 1 <= 32 - topClauses) cells.push({ depth, topClauses });
  }
}

function roundTripProperties(e: Explication, label: string, dict: CompositeDictionary): string {
  // P1 — URN determinism.
  const urn1 = mintCompositeUrn(e);
  const urn2 = mintCompositeUrn(JSON.parse(JSON.stringify(e)) as Explication);
  assert.equal(urn1, urn2, `${label}: URN not deterministic under JSON round-trip`);
  assert.match(urn1, /^urn:kot:b[a-z2-7]+$/, `${label}: URN shape`);

  // P2 — dictionary exact-by-id round trip.
  const urn3 = dict.add(e);
  assert.equal(urn3, urn1, `${label}: dictionary minted a different URN`);
  const entry = dict.expand(urn1);
  assert.equal(canonicalJson(entry.ast), canonicalJson(e), `${label}: dictionary expansion differs`);
  assert.equal(mintCompositeUrn(entry.ast), urn1, `${label}: expanded AST re-mints differently`);

  // P3 — renderer round trip (the load-bearing property).
  const text = renderExplication(e);
  assert.equal(entry.renderedText, text, `${label}: dictionary rendering differs from renderer`);
  const back = parseRendered(text);
  assert.equal(canonicalJson(back), canonicalJson(e), `${label}: render->parse is not the identity\n${text}`);
  validateExplication(back);
  assert.equal(mintCompositeUrn(back), urn1, `${label}: URN moved across render->parse`);

  return urn1;
}

test('B-RT: roll-up round-trip over generator+mutator strata (bar: 100%)', () => {
  const dict = new CompositeDictionary();
  let originals = 0;
  let mutants = 0;
  let nullMutations = 0;
  const encodeChecks: Explication[] = [];

  for (const cell of cells) {
    for (let s = 0; s < SEEDS_PER_CELL; s++) {
      const seed = `b-rt/${cell.depth}/${cell.topClauses}/${s}`;
      const e = generateExplication({ seed, topClauses: cell.topClauses, depth: cell.depth });
      const label = `cell d=${cell.depth} c=${cell.topClauses} seed=${s}`;
      const urnOrig = roundTripProperties(e, label, dict);
      originals++;
      if (s === 0) encodeChecks.push(e); // one per cell for P5

      const m = mutateExplication(e, `${seed}/mut`);
      if (m === null) {
        nullMutations++;
        continue;
      }
      const urnMut = roundTripProperties(m.mutant, `${label} mutant(${m.edit})`, dict);
      mutants++;
      // P4 — single edits must move the content address.
      assert.notEqual(urnMut, urnOrig, `${label}: mutant (${m.detail}) collides with original URN`);
    }
  }

  // P5 — encode equivalence on the per-cell subsample (D=8192 default).
  for (const e of encodeChecks) {
    const text = renderExplication(e);
    const back = parseRendered(text);
    const v1 = encodeExplication(e);
    const v2 = encodeExplication(back);
    assert.equal(v1.length, v2.length, 'encode length mismatch');
    assert.deepEqual(
      Buffer.from(v1.buffer, v1.byteOffset, v1.byteLength),
      Buffer.from(v2.buffer, v2.byteOffset, v2.byteLength),
      'encoded vectors differ across render->parse round trip',
    );
  }

  // Census bookkeeping (asserted so the suite reports its own scope).
  assert.ok(originals >= 900, `expected >=900 originals, got ${originals}`);
  assert.ok(mutants > 0, 'no mutants exercised');
  console.log(
    `B-RT scope: ${cells.length} strata × ${SEEDS_PER_CELL} seeds = ${originals} originals, ` +
      `${mutants} mutants (${nullMutations} null mutations), ${dict.size} unique composites, ` +
      `${encodeChecks.length} encode-equivalence checks @ D=8192`,
  );
});

test('B-RT: dictionary fails closed on unknown URN', () => {
  const dict = new CompositeDictionary();
  assert.throws(() => dict.expand('urn:kot:bunknown'), /ERR_DICT_UNKNOWN_URN/);
});

test('B-RT: renderer fails closed on non-canonical input', () => {
  assert.throws(() => parseRendered('instance refs[x1:someone] { frobnicate(agent=x1) }'), /ERR_PARSE_PRED/);
  assert.throws(() => parseRendered('instance refs[x1:someone] { do(agent=x1) } trailing'), /ERR_PARSE_TRAILING/);
  assert.throws(() => parseRendered(''), /ERR_PARSE_EOF/);
});
