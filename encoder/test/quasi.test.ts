/**
 * Property tests for the toy-native quasi-orthogonal variant kot-enc-Bq/1
 * (codebookQ.ts, encoderQ.ts; bead kernel-of-truth-5xo) and the Bluestein
 * chirp-z FFT path that serves D = 576.
 *
 * The variant's pre-registered Phase-X bars are exercised by the poc/src
 * harnesses (x0-q/x1-q/x2-q/x4-q, qcert); this suite pins the mathematical
 * premises: determinism, unit norms, fail-closed gates, unitarity of binding
 * on the Bluestein path, the base-encoder pin staying untouched, and the
 * hash separation between the two encoder versions.
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { AST_SCHEMA, type Explication } from '../src/ast.js';
import { fftReal, ifftToReal, spectrumMultiply } from '../src/fft.js';
import { QuasiCodebook, getQuasiCodebook, QUASI_DIMS, allAtomPairs } from '../src/codebookQ.js';
import {
  encodeExplicationQ,
  decodeExplicationQ,
  encodeConceptSetQ,
  resolveParamsQ,
  ALGORITHM_VERSION_Q,
} from '../src/encoderQ.js';
import { encodeExplication, ALGORITHM_VERSION } from '../src/encoder.js';
import { encoderContentHash, encoderContentHashQ } from '../src/contentHash.js';
import { generateExplication, mutateExplication } from '../src/synth.js';
import { canonicalJson } from '../src/ast.js';

/** The kot-enc-B/1 pin (poc-design Common rule 2, pinned 2026-07-07). */
const PINNED_BASE_HASH = '40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c';

function dot(a: Float64Array, b: Float64Array): number {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i]! * b[i]!;
  return s;
}

const AST: Explication = {
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

test('base encoder pin is untouched by the variant refactor (kot-enc-B/1 content-hash)', () => {
  assert.equal(ALGORITHM_VERSION, 'kot-enc-B/1');
  assert.equal(encoderContentHash(), PINNED_BASE_HASH);
});

test('variant content-hashes: own ALGORITHM_VERSION, one hash per D, all distinct from base', () => {
  assert.equal(ALGORITHM_VERSION_Q, 'kot-enc-Bq/1');
  const h512 = encoderContentHashQ({ D: 512 });
  const h576 = encoderContentHashQ({ D: 576 });
  assert.notEqual(h512, h576);
  assert.notEqual(h512, PINNED_BASE_HASH);
  assert.notEqual(h576, PINNED_BASE_HASH);
  assert.match(h512, /^[0-9a-f]{64}$/);
});

test('Bluestein DFT at n=576 matches the naive DFT and inverts exactly', () => {
  const n = 576;
  const v = new Float64Array(n);
  for (let i = 0; i < n; i++) v[i] = Math.sin(i * 0.7) + 0.3 * Math.cos(i * 1.3);
  const spec = fftReal(v);
  for (const k of [0, 1, 17, 287, 288, 575]) {
    let re = 0;
    let im = 0;
    for (let j = 0; j < n; j++) {
      const a = (-2 * Math.PI * j * k) / n;
      re += v[j]! * Math.cos(a);
      im += v[j]! * Math.sin(a);
    }
    assert.ok(Math.abs(re - spec.re[k]!) < 1e-9, `re[${k}]`);
    assert.ok(Math.abs(im - spec.im[k]!) < 1e-9, `im[${k}]`);
  }
  const back = ifftToReal(spec);
  for (let i = 0; i < n; i++) assert.ok(Math.abs(back[i]! - v[i]!) < 1e-12);
});

test('circular-convolution binding is unitary and exactly invertible on the Bluestein path (D=576)', () => {
  const cb = getQuasiCodebook(576);
  const f = cb.boundAtom('head', 'prime:GOOD');
  const bound = ifftToReal(spectrumMultiply(fftReal(cb.spread(f)), cb.tagSpectrum('agent'), false));
  // Unit-magnitude tag spectrum => norm preserved (up to Bluestein rounding).
  assert.ok(Math.abs(Math.sqrt(dot(bound, bound)) - 1) < 1e-10, 'binding must preserve norm');
  // Conjugate unbinding + unwhitening recovers the filler.
  const rec = cb.unspread(ifftToReal(spectrumMultiply(fftReal(bound), cb.tagSpectrum('agent'), true)));
  let err = 0;
  for (let i = 0; i < rec.length; i++) err = Math.max(err, Math.abs(rec[i]! - f[i]!));
  assert.ok(err < 1e-10, `unbinding residual ${err}`);
});

test('quasi atoms: deterministic across instances, unit norm, low pairwise coherence on a sample', () => {
  for (const D of QUASI_DIMS) {
    const a = new QuasiCodebook(D);
    const b = new QuasiCodebook(D);
    const pairs = allAtomPairs();
    assert.equal(pairs.length, 31 * 129);
    // Deterministic sample of atoms spread across the table.
    const sample = pairs.filter((_, i) => i % 157 === 0);
    const atoms = sample.map((p) => a.boundAtom(p.slot, p.filler));
    for (const [i, p] of sample.entries()) {
      const v = atoms[i]!;
      const v2 = b.boundAtom(p.slot, p.filler);
      assert.deepEqual(Buffer.from(v.buffer).equals(Buffer.from(v2.buffer)), true, 'atom determinism');
      assert.ok(Math.abs(dot(v, v) - 1) < 1e-12, 'unit norm');
    }
    let maxAbsCos = 0;
    for (let i = 0; i < atoms.length; i++) {
      for (let j = i + 1; j < atoms.length; j++) {
        maxAbsCos = Math.max(maxAbsCos, Math.abs(dot(atoms[i]!, atoms[j]!)));
      }
    }
    // Quasi-orthogonal, NOT orthogonal: strictly positive crosstalk, but well
    // under 6*sigma = 6/sqrt(D) for this ~26-atom sample (full-space max is
    // certified offline by poc qcert with the pre-registered comparison).
    assert.ok(maxAbsCos > 0, 'crosstalk floor is nonzero by construction');
    assert.ok(maxAbsCos < 6 / Math.sqrt(D), `sample coherence ${maxAbsCos} at D=${D}`);
  }
});

test('quasi codebook fails closed: unknown names, non-pre-registered dimensions', () => {
  const cb = getQuasiCodebook(512);
  assert.throws(() => cb.boundAtom('head', 'prime:NOPE'), /ERR_CODEBOOK_FILLER/);
  assert.throws(() => new QuasiCodebook(1024), /ERR_QUASI_DIMENSION/);
  assert.throws(() => new QuasiCodebook(8192), /ERR_QUASI_DIMENSION/);
  assert.throws(() => resolveParamsQ({ D: 100 }), /ERR_QUASI_DIMENSION/);
  assert.throws(() => resolveParamsQ({ alphaStruct: 0 }), /ERR_PARAM/);
});

test('encodeExplicationQ: byte-deterministic, unit norm, D-native length, distinct from single-edit mutant', () => {
  for (const D of QUASI_DIMS) {
    const v1 = encodeExplicationQ(AST, { params: { D } });
    const v2 = encodeExplicationQ(AST, { params: { D } });
    assert.equal(v1.length, D);
    assert.deepEqual(Buffer.from(v1.buffer).equals(Buffer.from(v2.buffer)), true);
    assert.ok(Math.abs(dot(v1, v1) - 1) < 1e-12);
    const mut = mutateExplication(AST, `quasi-test/${D}`);
    assert.notEqual(mut, null);
    const vm = encodeExplicationQ(mut!.mutant, { params: { D } });
    const cos = dot(v1, vm);
    assert.ok(cos < 1 - 1e-6, `mutant must be geometrically distinct (cos=${cos})`);
  }
});

test('variant and base encoders are different maps (not a projection of each other)', () => {
  const v8192 = encodeExplication(AST);
  const v512 = encodeExplicationQ(AST, { params: { D: 512 } });
  assert.equal(v8192.length, 8192);
  assert.equal(v512.length, 512);
  // The variant is a re-encode, not a truncation of the base vector.
  let same = true;
  for (let i = 0; i < 512; i++) if (v512[i] !== v8192[i]) same = false;
  assert.equal(same, false);
});

test('encodeConceptSetQ resolves reference DAGs at native D; decodeExplicationQ round-trips a shallow AST (measurement, not a gate)', () => {
  const leaf: Explication = {
    schema: AST_SCHEMA,
    frame: 'InstanceSchema',
    referents: [{ index: 1, refKind: 'SomethingRef' }],
    clauses: [{ type: 'pred', pred: 'THERE-IS', roles: { undergoer: { kind: 'ref', index: 1 } } }],
  };
  const mid: Explication = {
    schema: AST_SCHEMA,
    frame: 'InstanceSchema',
    referents: [{ index: 1, refKind: 'SomeoneRef' }],
    clauses: [
      {
        type: 'pred',
        pred: 'KNOW',
        roles: { experiencer: { kind: 'ref', index: 1 }, topic: { kind: 'concept', id: 'urn:concept:q-leaf' } },
      },
    ],
  };
  for (const D of QUASI_DIMS) {
    const { vectors } = encodeConceptSetQ(
      new Map([
        ['urn:concept:q-leaf', leaf],
        ['urn:concept:q-mid', mid],
      ]),
      { params: { D } },
    );
    assert.equal(vectors.get('urn:concept:q-leaf')!.length, D);
    assert.equal(vectors.get('urn:concept:q-mid')!.length, D);
    // Decode reality check on a SHALLOW example only: the pre-registration
    // scopes full decode away from toy-native D (codebookQ.ts header). A
    // 1-clause explication sits far above the coherent-crosstalk floor and
    // must still round-trip; deeper shapes are measured (ungated) by X2-q.
    const r = decodeExplicationQ(vectors.get('urn:concept:q-leaf')!, { params: { D } });
    assert.equal(r.ok, true, `shallow decode at D=${D} should validate`);
    assert.equal(canonicalJson(r.explication!), canonicalJson(leaf), `shallow decode at D=${D} should be exact`);
  }
});

test('variant on synthetic shapes: deterministic and dimension-consistent across the generator', () => {
  for (const D of QUASI_DIMS) {
    for (const [tc, dep] of [
      [1, 1],
      [4, 3],
      [8, 2],
    ] as const) {
      const ast = generateExplication({ seed: `quasi/${D}/${tc}/${dep}`, topClauses: tc, depth: dep });
      const v = encodeExplicationQ(ast, { params: { D } });
      const v2 = encodeExplicationQ(ast, { params: { D } });
      assert.equal(v.length, D);
      assert.deepEqual(Buffer.from(v.buffer).equals(Buffer.from(v2.buffer)), true);
    }
  }
});
