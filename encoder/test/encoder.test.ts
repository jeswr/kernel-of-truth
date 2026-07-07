/**
 * Encoder property tests: determinism (byte-identity), unit norm, validation
 * gates fail closed, concept-set memoised recursion + cycle rejection,
 * content-hash sensitivity to the pinned parameters.
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import type { Explication } from '../src/ast.js';
import { AST_SCHEMA } from '../src/ast.js';
import {
  encodeExplication,
  encodeConceptSet,
} from '../src/encoder.js';
import { encoderContentHash } from '../src/contentHash.js';
import { generateExplication, mutateExplication } from '../src/synth.js';
import { validateExplication, GateError } from '../src/validate.js';

/** "someone sees something good" — a minimal hand-authored explication. */
const SEE_GOOD: Explication = {
  schema: AST_SCHEMA,
  frame: 'InstanceSchema',
  referents: [{ index: 1, refKind: 'SomeoneRef' }],
  clauses: [
    {
      type: 'pred',
      pred: 'SEE',
      roles: {
        experiencer: { kind: 'ref', index: 1 },
        stimulus: {
          kind: 'sp',
          quant: 'SOME',
          mods: [{ mod: 'GOOD' }],
          head: { kind: 'primeHead', prime: 'SOMETHING~THING' },
        },
      },
    },
  ],
};

function bytesOf(v: Float64Array): Buffer {
  const buf = Buffer.alloc(v.length * 8);
  for (let i = 0; i < v.length; i++) buf.writeDoubleLE(v[i]!, i * 8);
  return buf;
}

test('encoding is deterministic: byte-identical across runs', () => {
  const a = encodeExplication(SEE_GOOD);
  const b = encodeExplication(SEE_GOOD);
  assert.equal(bytesOf(a).equals(bytesOf(b)), true);
});

test('encoded vectors are unit norm', () => {
  const v = encodeExplication(SEE_GOOD);
  let s = 0;
  for (let i = 0; i < v.length; i++) s += v[i]! * v[i]!;
  assert.ok(Math.abs(s - 1) < 1e-12);
});

test('different explications produce different vectors (mutant margin > 0)', () => {
  const e = generateExplication({ seed: 'enc-margin', topClauses: 4, depth: 2 });
  const m = mutateExplication(e, 'enc-margin-mut');
  assert.ok(m !== null);
  const v1 = encodeExplication(e);
  const v2 = encodeExplication(m!.mutant);
  let d = 0;
  for (let i = 0; i < v1.length; i++) d += v1[i]! * v2[i]!;
  assert.ok(d < 1 - 1e-6, `mutant cosine ${d} must differ from 1`);
});

test('validation gates fail closed: unknown prime, bad arity, ref-before-introduction, caps', () => {
  const badPrime = { ...SEE_GOOD, clauses: [{ type: 'pred', pred: 'GLORP', roles: {} }] } as unknown as Explication;
  assert.throws(() => encodeExplication(badPrime), GateError);

  const badRef: Explication = {
    ...SEE_GOOD,
    clauses: [
      { type: 'pred', pred: 'SEE', roles: { experiencer: { kind: 'ref', index: 1 }, stimulus: { kind: 'ref', index: 2 } } },
    ],
  };
  assert.throws(() => encodeExplication(badRef), /ERR_REF_UNDECLARED/);

  const badArity: Explication = {
    ...SEE_GOOD,
    clauses: [{ type: 'op', op: 'IF', args: [{ type: 'pred', pred: 'HAPPEN', roles: {} }] }],
  };
  assert.throws(() => encodeExplication(badArity), /ERR_OP_ARITY/);

  const tooManyClauses: Explication = {
    ...SEE_GOOD,
    clauses: Array.from({ length: 33 }, () => ({ type: 'pred' as const, pred: 'HAPPEN', roles: {} })),
  };
  assert.throws(() => encodeExplication(tooManyClauses), /ERR_CAP_CLAUSES/);
});

test('required role missing fails closed', () => {
  const e: Explication = {
    ...SEE_GOOD,
    clauses: [{ type: 'pred', pred: 'SEE', roles: { experiencer: { kind: 'ref', index: 1 } } }],
  };
  assert.throws(() => encodeExplication(e), /ERR_ROLE_REQUIRED_MISSING/);
});

test('concept references: unresolved fails closed; resolved binds the referenced vector', () => {
  const withRef: Explication = {
    ...SEE_GOOD,
    clauses: [
      {
        type: 'pred',
        pred: 'SEE',
        roles: {
          experiencer: { kind: 'ref', index: 1 },
          stimulus: { kind: 'concept', id: 'urn:concept:test1' },
        },
      },
    ],
  };
  assert.throws(() => encodeExplication(withRef), /ERR_CONCEPT_UNRESOLVED/);
  const base = encodeExplication(SEE_GOOD);
  const concepts = new Map([['urn:concept:test1', base]]);
  const v = encodeExplication(withRef, { concepts });
  assert.equal(v.length, base.length);
});

test('encodeConceptSet: memoised recursion resolves DAGs, rejects cycles', () => {
  const leaf: Explication = SEE_GOOD;
  const mid: Explication = {
    ...SEE_GOOD,
    clauses: [
      {
        type: 'pred',
        pred: 'KNOW',
        roles: { experiencer: { kind: 'ref', index: 1 }, topic: { kind: 'concept', id: 'urn:concept:leaf' } },
      },
    ],
  };
  const defs = new Map<string, Explication>([
    ['urn:concept:leaf', leaf],
    ['urn:concept:mid', mid],
  ]);
  const { vectors } = encodeConceptSet(defs);
  assert.equal(vectors.size, 2);
  // Cycle: a -> b -> a
  const a: Explication = {
    ...SEE_GOOD,
    clauses: [
      { type: 'pred', pred: 'KNOW', roles: { experiencer: { kind: 'ref', index: 1 }, topic: { kind: 'concept', id: 'urn:concept:b' } } },
    ],
  };
  const b: Explication = {
    ...SEE_GOOD,
    clauses: [
      { type: 'pred', pred: 'KNOW', roles: { experiencer: { kind: 'ref', index: 1 }, topic: { kind: 'concept', id: 'urn:concept:a' } } },
    ],
  };
  assert.throws(
    () => encodeConceptSet(new Map([['urn:concept:a', a], ['urn:concept:b', b]])),
    /ERR_CYCLIC_CONCEPT_REF/,
  );
});

test('content hash: stable, and sensitive to D and weighting params', () => {
  const h1 = encoderContentHash();
  const h2 = encoderContentHash();
  assert.equal(h1, h2);
  assert.match(h1, /^[0-9a-f]{64}$/);
  const hD = encoderContentHash({ D: 16384 });
  assert.notEqual(h1, hD);
  const hW = encoderContentHash({ alphaStruct: 0.5 });
  assert.notEqual(h1, hW);
  const hN = encoderContentHash({ notBoost: 2 });
  assert.notEqual(h1, hN);
});

test('generator: valid by construction across a seed sweep; mutator preserves validity', () => {
  for (let s = 0; s < 25; s++) {
    const e = generateExplication({ seed: `gen-${s}`, topClauses: 1 + (s % 8), depth: 1 + (s % 5) });
    const stats = validateExplication(e);
    assert.ok(stats.clauseCount <= 32);
    assert.ok(stats.maxDepth <= 12);
    const m = mutateExplication(e, `mut-${s}`);
    if (m !== null) {
      validateExplication(m.mutant);
      assert.notEqual(JSON.stringify(m.mutant), JSON.stringify(e));
    }
  }
});

test('generator determinism: same seed -> same explication, same vector bytes', () => {
  const e1 = generateExplication({ seed: 'det-check', topClauses: 5, depth: 3 });
  const e2 = generateExplication({ seed: 'det-check', topClauses: 5, depth: 3 });
  assert.deepEqual(e1, e2);
  assert.equal(bytesOf(encodeExplication(e1)).equals(bytesOf(encodeExplication(e2))), true);
});
