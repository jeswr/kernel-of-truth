/** det.ts primitives: stream reproducibility, fp16 round-trip, rejection sampling. */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  DetStream,
  SeededRng,
  toFloat16Bits,
  fromFloat16Bits,
  fp16RoundTrip,
} from '../src/det.js';

test('DetStream is reproducible and label-separated', () => {
  const a1 = new DetStream('x');
  const a2 = new DetStream('x');
  const b = new DetStream('y');
  const s1 = Array.from({ length: 16 }, () => a1.nextUint32());
  const s2 = Array.from({ length: 16 }, () => a2.nextUint32());
  const s3 = Array.from({ length: 16 }, () => b.nextUint32());
  assert.deepEqual(s1, s2);
  assert.notDeepEqual(s1, s3);
});

test('nextBelow is in range and rejects invalid n', () => {
  const s = new DetStream('range');
  for (let i = 0; i < 1000; i++) {
    const v = s.nextBelow(7);
    assert.ok(v >= 0 && v < 7);
  }
  assert.throws(() => s.nextBelow(0), /ERR_DET_RANGE/);
});

test('SeededRng requires an explicit seed', () => {
  assert.throws(() => new SeededRng(''), /ERR_SEED_REQUIRED/);
});

test('fp16: exact on representable values, RNE rounding, subnormals, specials', () => {
  for (const v of [0, 1, -1, 0.5, 0.25, 1.5, 2048, -0.099975585937]) {
    const rt = fromFloat16Bits(toFloat16Bits(v));
    const rt2 = fromFloat16Bits(toFloat16Bits(rt));
    assert.equal(rt, rt2, `fp16 must be idempotent for ${v}`);
  }
  assert.equal(fromFloat16Bits(toFloat16Bits(1)), 1);
  assert.equal(fromFloat16Bits(toFloat16Bits(65504)), 65504); // max half
  assert.equal(fromFloat16Bits(toFloat16Bits(1e6)), Infinity); // overflow
  assert.equal(fromFloat16Bits(toFloat16Bits(6e-8)), 5.960464477539063e-8); // subnormal
  assert.ok(Number.isNaN(fromFloat16Bits(toFloat16Bits(NaN))));
  // relative error bound for normal range: 2^-11
  const s = new DetStream('fp16');
  for (let i = 0; i < 2000; i++) {
    const v = (s.nextFloat() - 0.5) * 2;
    const rt = fromFloat16Bits(toFloat16Bits(v));
    assert.ok(Math.abs(rt - v) <= Math.max(Math.abs(v) * 2 ** -11, 2 ** -24), `fp16 error too big at ${v}`);
  }
});

test('fp16RoundTrip preserves vector shape with bounded angular error', () => {
  const s = new DetStream('fp16vec');
  const D = 8192;
  const v = new Float64Array(D);
  let n = 0;
  for (let i = 0; i < D; i++) {
    v[i] = s.nextFloat() - 0.5;
    n += v[i]! * v[i]!;
  }
  n = Math.sqrt(n);
  for (let i = 0; i < D; i++) v[i] = v[i]! / n;
  const rt = fp16RoundTrip(v);
  let d = 0;
  let n2 = 0;
  for (let i = 0; i < D; i++) {
    d += v[i]! * rt[i]!;
    n2 += rt[i]! * rt[i]!;
  }
  const cos = d / Math.sqrt(n2);
  assert.ok(cos > 0.999999, `fp16 roundtrip cosine ${cos}`);
});
