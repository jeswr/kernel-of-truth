/**
 * Decoder property tests: exact round-trip on hand-authored and shallow
 * synthetic explications, concept-reference cleanup against a lexicon,
 * confidence reporting. (Depth/clause-count sweep is X2's job.)
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import type { Explication } from '../src/ast.js';
import { AST_SCHEMA, canonicalJson } from '../src/ast.js';
import { encodeExplication, encodeConceptSet } from '../src/encoder.js';
import { decodeExplication } from '../src/decoder.js';
import { generateExplication } from '../src/synth.js';

const SIMPLE: Explication = {
  schema: AST_SCHEMA,
  frame: 'InstanceSchema',
  referents: [{ index: 1, refKind: 'SomeoneRef' }],
  clauses: [
    {
      type: 'pred',
      pred: 'WANT',
      roles: {
        experiencer: { kind: 'ref', index: 1 },
        complement: {
          kind: 'clause',
          clause: {
            type: 'pred',
            pred: 'SEE',
            roles: {
              experiencer: { kind: 'ref', index: 1 },
              stimulus: { kind: 'sp', det: 'THE-SAME', head: { kind: 'primeHead', prime: 'SOMETHING~THING' } },
            },
          },
        },
      },
    },
    { type: 'op', op: 'NOT', args: [{ type: 'pred', pred: 'DIE', roles: { undergoer: { kind: 'ref', index: 1 } } }] },
  ],
};

test('round-trip: hand-authored explication decodes exactly', () => {
  const v = encodeExplication(SIMPLE);
  const r = decodeExplication(v);
  assert.equal(r.ok, true, r.validationError);
  assert.equal(canonicalJson(r.explication), canonicalJson(SIMPLE));
  assert.ok(r.minConfidence > 0);
  assert.ok(r.steps.length > 0);
});

test('round-trip: shallow synthetics decode exactly (seeds 0..9)', () => {
  for (let s = 0; s < 10; s++) {
    const e = generateExplication({ seed: `dec-rt-${s}`, topClauses: 2 + (s % 3), depth: 2 });
    const v = encodeExplication(e);
    const r = decodeExplication(v);
    assert.equal(r.ok, true, `seed ${s}: ${r.validationError}`);
    assert.equal(canonicalJson(r.explication), canonicalJson(e), `seed ${s} mismatch`);
  }
});

test('concept references decode via nearest-neighbour cleanup against the lexicon', () => {
  const leaf = generateExplication({ seed: 'dec-leaf', topClauses: 2, depth: 1 });
  const defs = new Map([['urn:concept:leaf', leaf]]);
  const { vectors } = encodeConceptSet(defs);
  const withRef: Explication = {
    schema: AST_SCHEMA,
    frame: 'InstanceSchema',
    referents: [{ index: 1, refKind: 'SomeoneRef' }],
    clauses: [
      {
        type: 'pred',
        pred: 'KNOW',
        roles: { experiencer: { kind: 'ref', index: 1 }, topic: { kind: 'concept', id: 'urn:concept:leaf' } },
      },
    ],
  };
  const v = encodeExplication(withRef, { concepts: vectors });
  const r = decodeExplication(v, { concepts: vectors });
  assert.equal(r.ok, true, r.validationError);
  assert.equal(canonicalJson(r.explication), canonicalJson(withRef));
});

test('decoding a noise vector yields no phantom explication marked ok', () => {
  // A pure-noise vector must not decode to ok=true with clauses.
  const D = 8192;
  const v = new Float64Array(D);
  // deterministic pseudo-noise
  let x = 12345;
  for (let i = 0; i < D; i++) {
    x = (x * 1103515245 + 12345) & 0x7fffffff;
    v[i] = (x / 0x7fffffff - 0.5) / Math.sqrt(D / 12);
  }
  const r = decodeExplication(v);
  assert.equal(r.ok, false);
});

test('dimension mismatch fails closed', () => {
  assert.throws(() => decodeExplication(new Float64Array(1024)), /ERR_DIMENSION/);
});
