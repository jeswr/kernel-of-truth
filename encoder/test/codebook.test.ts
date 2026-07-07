/**
 * Property tests for the deterministic codebook: EXACT orthonormality of the
 * Hadamard atom codebook in float64 (not just in exact arithmetic), exactness
 * of XOR binding, unitarity of tags and permutations. These are the
 * mathematical premises of construction B (report §7.3).
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  getCodebook,
  codebookTable,
  SLOT_TABLE,
  FILLER_TABLE,
  MIN_D,
  DEFAULT_PARAMS,
} from '../src/codebook.js';
import { detPermutation, invertPermutation, applyPermutation } from '../src/det.js';
import { fftReal, ifftToReal, spectrumMultiply } from '../src/fft.js';

const D = DEFAULT_PARAMS.D;
const cb = getCodebook(D);

function dot(a: Float64Array, b: Float64Array): number {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i]! * b[i]!;
  return s;
}

test('codebook table shape: 31 slots, 129 fillers, all indices unique and < MIN_D', () => {
  assert.equal(SLOT_TABLE.size, 31);
  assert.equal(FILLER_TABLE.size, 129);
  const table = codebookTable();
  const indices = Object.values(table);
  assert.equal(new Set(indices).size, indices.length, 'row indices must be unique');
  for (const i of indices) assert.ok(i > 0 && i < MIN_D);
});

test('Hadamard atoms are orthonormal to float64 rounding (< 1e-12)', () => {
  // Exactly orthonormal in exact arithmetic; float64 rounding of the 1/sqrt(D)
  // scale leaves ulp-level residue.
  const rows = [
    cb.boundAtom('agent', 'prime:SOMEONE'),
    cb.boundAtom('undergoer', 'prime:SOMEONE'),
    cb.boundAtom('agent', 'prime:SOMETHING~THING'),
    cb.boundAtom('pred', 'prime:DO'),
    cb.boundAtom('ctype', 'tag:TAG:PRED'),
    cb.boundAtom('frame', 'frame:InstanceSchema'),
    cb.boundAtom('refdecl', 'refkind:SomeoneRef'),
    cb.boundAtom('head', 'ref:32'),
  ];
  for (let i = 0; i < rows.length; i++) {
    for (let j = 0; j < rows.length; j++) {
      const d = dot(rows[i]!, rows[j]!);
      const want = i === j ? 1 : 0;
      assert.ok(Math.abs(d - want) < 1e-12, `dot(row${i}, row${j}) = ${d}, want ${want}`);
    }
  }
});

test('bound pairs are injective: distinct (slot, filler) -> distinct orthogonal rows', () => {
  const a = cb.boundAtom('agent', 'prime:I');
  const b = cb.boundAtom('experiencer', 'prime:I');
  const c = cb.boundAtom('agent', 'prime:YOU');
  assert.ok(Math.abs(dot(a, b)) < 1e-12);
  assert.ok(Math.abs(dot(a, c)) < 1e-12);
  assert.ok(Math.abs(dot(b, c)) < 1e-12);
});

test('tag spectra are unit-magnitude (exactly) and binding is unitary to FFT rounding', () => {
  const spec = cb.tagSpectrum('complement');
  for (let k = 0; k < D; k++) {
    const mag2 = spec.re[k]! * spec.re[k]! + spec.im[k]! * spec.im[k]!;
    assert.equal(mag2, 1, `spectrum magnitude at bin ${k} must be exactly 1`);
  }
  // Unitarity: |tag ⊛ v| = |v| up to FFT rounding.
  const v = cb.boundAtom('pred', 'prime:SEE');
  const bound = ifftToReal(spectrumMultiply(fftReal(v), spec, false));
  const n = Math.sqrt(dot(bound, bound));
  assert.ok(Math.abs(n - 1) < 1e-12, `norm after unitary binding = ${n}`);
  // Exact unbinding by conjugation.
  const un = ifftToReal(spectrumMultiply(fftReal(bound), spec, true));
  let maxErr = 0;
  for (let i = 0; i < D; i++) maxErr = Math.max(maxErr, Math.abs(un[i]! - v[i]!));
  assert.ok(maxErr < 1e-12, `unbind roundtrip error ${maxErr}`);
});

test('deterministic permutations: bijective, seedless-reproducible, invertible', () => {
  const p1 = detPermutation('clause/0', D);
  const p2 = detPermutation('clause/0', D);
  assert.deepEqual([...p1.slice(0, 32)], [...p2.slice(0, 32)]);
  assert.equal(new Set(p1).size, D);
  const inv = invertPermutation(p1);
  const v = cb.boundAtom('op', 'op:NOT');
  const roundtrip = applyPermutation(inv, applyPermutation(p1, v));
  for (let i = 0; i < D; i++) assert.equal(roundtrip[i], v[i]);
});

test('D below 8192 fails closed', () => {
  assert.throws(() => getCodebook(4096), /ERR_DIMENSION_TOO_SMALL/);
});
