/** FFT correctness: roundtrip, Parseval, convolution theorem vs naive O(n^2). */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fftReal, ifftToReal, spectrumMultiply, fftInPlace } from '../src/fft.js';
import { DetStream } from '../src/det.js';

function randVec(n: number, label: string): Float64Array {
  const s = new DetStream(`test/${label}`);
  const v = new Float64Array(n);
  for (let i = 0; i < n; i++) v[i] = s.nextFloat() * 2 - 1;
  return v;
}

test('FFT/IFFT roundtrip is identity to ~1e-13', () => {
  const v = randVec(1024, 'fft-roundtrip');
  const back = ifftToReal(fftReal(v));
  let maxErr = 0;
  for (let i = 0; i < v.length; i++) maxErr = Math.max(maxErr, Math.abs(back[i]! - v[i]!));
  assert.ok(maxErr < 1e-13, `roundtrip error ${maxErr}`);
});

test('Parseval: |FFT(v)|^2 = n |v|^2', () => {
  const v = randVec(512, 'parseval');
  const spec = fftReal(v);
  let e1 = 0;
  for (let i = 0; i < v.length; i++) e1 += v[i]! * v[i]!;
  let e2 = 0;
  for (let i = 0; i < v.length; i++) e2 += spec.re[i]! * spec.re[i]! + spec.im[i]! * spec.im[i]!;
  assert.ok(Math.abs(e2 / v.length - e1) < 1e-10);
});

test('convolution theorem matches naive circular convolution', () => {
  const n = 256;
  const a = randVec(n, 'conv-a');
  const b = randVec(n, 'conv-b');
  const viaFft = ifftToReal(spectrumMultiply(fftReal(a), fftReal(b), false));
  const naive = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    let s = 0;
    for (let j = 0; j < n; j++) s += a[j]! * b[(i - j + n) % n]!;
    naive[i] = s;
  }
  let maxErr = 0;
  for (let i = 0; i < n; i++) maxErr = Math.max(maxErr, Math.abs(viaFft[i]! - naive[i]!));
  assert.ok(maxErr < 1e-10, `convolution mismatch ${maxErr}`);
});

test('non-power-of-two size fails closed', () => {
  const re = new Float64Array(100);
  const im = new Float64Array(100);
  assert.throws(() => fftInPlace(re, im), /ERR_NOT_POWER_OF_TWO/);
});
