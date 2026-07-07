import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  R, R1, rParse, rToString, rToApprox, rMul, rDiv, rPow, rAdd, rEq, rCmp, rAbs, rSub,
  P, pMul, pDiv, pPow, pEq, pApprox, PI_50,
} from '../rational.mjs';

test('fraction reduction and sign normalization', () => {
  assert.deepEqual(R(6n, -4n), { num: -3n, den: 2n });
  assert.deepEqual(R(0n, 7n), { num: 0n, den: 1n });
  assert.ok(rEq(rMul(R(5n, 9n), R(9n, 5n)), R1));
});

test('rParse: integer, decimal, exponent, fraction — exact', () => {
  assert.deepEqual(rParse('0.0254'), R(254n, 10000n));
  assert.deepEqual(rParse('1.602176634e-19'), R(1602176634n, 10n ** 28n));
  assert.deepEqual(rParse('45967/180'), R(45967n, 180n));
  assert.deepEqual(rParse('-3'), R(-3n));
  assert.throws(() => rParse('1,5'), /ERR_RAT_PARSE/);
  assert.throws(() => rParse('0x10'), /ERR_RAT_PARSE/);
});

test('rToString: canonical, round-trips through rParse (physics-v0 grammar)', () => {
  const cases = ['0.0254', '273.15', '5/9', '45967/180', '1', '-7', '101325', '0.45359237'];
  for (const s of cases) {
    const r = rParse(s);
    assert.ok(rEq(rParse(rToString(r)), r), `round-trip failed for ${s}`);
  }
  assert.equal(rToString(R(5n, 9n)), '5/9');           // non-terminating -> fraction
  assert.equal(rToString(R(254n, 10000n)), '0.0254');  // terminating -> decimal
  assert.equal(rToString(R(1n, 2n)), '0.5');
  assert.equal(rToString(R(10n ** 30n)), '1' + '0'.repeat(30));
});

test('affine composition: value_SI = x*scale + offset, exact', () => {
  // K = degF * 5/9 + 45967/180 ; 32 degF must be exactly 273.15 K
  const scale = R(5n, 9n), offset = R(45967n, 180n);
  const k = rAdd(rMul(R(32n), scale), offset);
  assert.ok(rEq(k, rParse('273.15')));
  // 212 degF = 373.15 K
  assert.ok(rEq(rAdd(rMul(R(212n), scale), offset), rParse('373.15')));
  // prefix-of-affine: milli-degC -> K: scale 1/1000, offset 273.15 (QUDT MilliDEG_C cross-check)
  const mScale = rMul(rParse('0.001'), R1), mOffset = rParse('273.15');
  assert.ok(rEq(rAdd(rMul(R(1000n), mScale), mOffset), rParse('274.15')));
});

test('rPow including negative exponents', () => {
  assert.ok(rEq(rPow(R(3n, 4n), -2), R(16n, 9n)));
  assert.ok(rEq(rPow(R(10n), 6), R(1000000n)));
  assert.ok(rEq(rPow(R(7n, 3n), 0), R1));
});

test('pi-tagged scalars: symbolic pi survives products/powers exactly', () => {
  const deg = P(R(1n, 180n), 1);              // degree -> rad: pi/180
  const perDeg = pPow(deg, -1);               // 180/pi
  assert.ok(pEq(pMul(deg, perDeg), P(R1, 0)));
  // rpm = rev/min = 2pi/60 = pi/30
  const rev = P(R(2n), 1), perMin = P(R(1n, 60n));
  assert.ok(pEq(pMul(rev, perMin), P(R(1n, 30n), 1)));
  // parsec = (648000/pi) au: pi exponent -1
  const pc = pDiv(P(R(648000n * 149597870700n)), P(R1, 1));
  assert.equal(pc.pi, -1);
});

test('pApprox matches known digits (report-side only)', () => {
  // pi/180 = 0.017453292519943295...
  const a = pApprox(P(R(1n, 180n), 1));
  assert.ok(rToApprox(a, 16).startsWith('1.745329251994329'));
  // PI_50 sanity vs independent digits
  assert.ok(rToApprox(PI_50, 20).startsWith('3.141592653589793238'));
});

test('rToApprox / rCmp / rAbs / rSub behave', () => {
  assert.equal(rToApprox(rParse('0.3048'), 5), '3.048e-1');
  assert.equal(rCmp(R(1n, 3n), R(1n, 2n)), -1);
  assert.ok(rEq(rAbs(R(-5n, 9n)), R(5n, 9n)));
  assert.ok(rEq(rSub(rParse('273.15'), rParse('0.15')), R(273n)));
});
