/**
 * Exact rational arithmetic (BigInt) + pi-tagged scalars for physics-qudt.
 *
 * House rule (data/physics-v0/validate.mjs, encoder/ conventions): NO floats
 * touch definitional content. A unit scale here is  q * pi^k  with q an exact
 * BigInt rational and k a (usually zero) integer — pi enters exactly for the
 * angle family (degree = pi/180 rad; SI Brochure 9th ed. Table 8) and CGS
 * magnetic units (oersted = 250/pi A/m), and is carried SYMBOLICALLY, never
 * as a float. Floats appear only in the cross-check REPORT (classifying
 * QUDT's stated float factors), never in emitted records.
 */

// --- rationals ----------------------------------------------------------------
const bgcd = (a, b) => { a = a < 0n ? -a : a; b = b < 0n ? -b : b; while (b) [a, b] = [b, a % b]; return a; };

export const R = (num, den = 1n) => {
  if (typeof num === 'number') { if (!Number.isSafeInteger(num)) throw new Error('ERR_RAT_FLOAT: non-integer number'); num = BigInt(num); }
  if (typeof den === 'number') { if (!Number.isSafeInteger(den)) throw new Error('ERR_RAT_FLOAT: non-integer number'); den = BigInt(den); }
  if (den === 0n) throw new Error('ERR_RAT_ZERO_DEN: zero denominator');
  if (den < 0n) { num = -num; den = -den; }
  const g = bgcd(num, den) || 1n;
  return { num: num / g, den: den / g };
};
export const rAdd = (a, b) => R(a.num * b.den + b.num * a.den, a.den * b.den);
export const rSub = (a, b) => R(a.num * b.den - b.num * a.den, a.den * b.den);
export const rMul = (a, b) => R(a.num * b.num, a.den * b.den);
export const rDiv = (a, b) => { if (b.num === 0n) throw new Error('ERR_RAT_DIV0: division by zero'); return R(a.num * b.den, a.den * b.num); };
export const rNeg = (a) => R(-a.num, a.den);
export const rAbs = (a) => R(a.num < 0n ? -a.num : a.num, a.den);
export const rEq = (a, b) => a.num === b.num && a.den === b.den;
export const rCmp = (a, b) => { const d = a.num * b.den - b.num * a.den; return d < 0n ? -1 : d > 0n ? 1 : 0; };
export const rPow = (a, e) => {
  if (!Number.isSafeInteger(e)) throw new Error('ERR_RAT_POW: exponent must be an integer');
  if (e === 0) return R(1n);
  const p = e < 0 ? rDiv(R(1n), a) : a;
  const k = Math.abs(e);
  let out = R(1n);
  for (let i = 0; i < k; i++) out = rMul(out, p);
  return out;
};
export const R0 = R(0n);
export const R1 = R(1n);

/** Parse an exact-rational string: integer, decimal, decimal-exponent, or "p/q".
 *  (Same grammar as data/physics-v0/validate.mjs parseRat — kept compatible.) */
export const rParse = (s) => {
  if (typeof s !== 'string') throw new Error(`ERR_RAT_PARSE: rational must be a string, got ${typeof s}`);
  const frac = s.match(/^(-?\d+)\/(\d+)$/);
  if (frac) return R(BigInt(frac[1]), BigInt(frac[2]));
  const dec = s.match(/^(-?)(\d+)(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/);
  if (!dec) throw new Error(`ERR_RAT_PARSE: not an exact-rational literal: ${JSON.stringify(s)}`);
  const [, sign, ip, fp = '', exp = '0'] = dec;
  const num = BigInt(ip + fp) * (sign === '-' ? -1n : 1n);
  const e = BigInt(exp) - BigInt(fp.length);
  return e >= 0n ? R(num * 10n ** e) : R(num, 10n ** -e);
};

/** Canonical string form, round-trips exactly through rParse (and through
 *  physics-v0's parseRat): integer | terminating decimal | "p/q". */
export const rToString = (r) => {
  if (r.den === 1n) return r.num.toString();
  // terminating decimal iff den = 2^a * 5^b
  let d = r.den, a = 0n, b = 0n;
  while (d % 2n === 0n) { d /= 2n; a++; }
  while (d % 5n === 0n) { d /= 5n; b++; }
  if (d === 1n) {
    const k = a > b ? a : b; // scale to 10^k
    const scaled = (r.num < 0n ? -r.num : r.num) * 10n ** k / r.den;
    const s = scaled.toString().padStart(Number(k) + 1, '0');
    const ip = s.slice(0, s.length - Number(k)) || '0';
    const fp = s.slice(s.length - Number(k)).replace(/0+$/, '');
    return `${r.num < 0n ? '-' : ''}${ip}${fp ? '.' + fp : ''}`;
  }
  return `${r.num}/${r.den}`;
};

/** Decimal approximation to `sig` significant digits, truncated (REPORT USE ONLY). */
export const rToApprox = (r, sig = 17) => {
  if (r.num === 0n) return '0';
  const neg = r.num < 0n;
  const num = neg ? -r.num : r.num;
  const den = r.den;
  // find exponent e with 10^e <= num/den < 10^(e+1)
  let e = 0;
  let hi = den;
  while (num >= hi * 10n) { hi *= 10n; e++; }
  let lo = num;
  while (lo < den) { lo *= 10n; e--; }
  // digits = floor(num/den * 10^(sig-1-e))
  const shift = BigInt(sig - 1 - e);
  const scaled = shift >= 0n ? num * 10n ** shift : num / 10n ** -shift;
  let digits = (scaled / den).toString();
  if (digits.length > sig) { digits = digits.slice(0, sig); e++; } // overflow guard
  const mant = digits.length > 1 ? `${digits[0]}.${digits.slice(1).replace(/0+$/, '') || '0'}` : digits;
  return `${neg ? '-' : ''}${mant}e${e}`;
};

// --- pi-tagged scalars: q * pi^k ------------------------------------------------
// pi to 50 decimal digits (report-side approximation only; the SYMBOL is exact).
// Source: well-established constant; 50 digits are vastly beyond any QUDT float.
export const PI_50 = rParse('3.14159265358979323846264338327950288419716939937511');

export const P = (r, pi = 0) => {
  if (!Number.isSafeInteger(pi)) throw new Error('ERR_PI_EXP: pi exponent must be an integer');
  return { r, pi: r.num === 0n ? 0 : pi };
};
export const pOne = P(R1);
export const pMul = (a, b) => P(rMul(a.r, b.r), a.pi + b.pi);
export const pDiv = (a, b) => P(rDiv(a.r, b.r), a.pi - b.pi);
export const pPow = (a, e) => P(rPow(a.r, e), a.pi * e);
export const pEq = (a, b) => rEq(a.r, b.r) && a.pi === b.pi;
/** Rational approximation of q * pi^k via PI_50 (report/classification only). */
export const pApprox = (a) => rMul(a.r, rPow(PI_50, a.pi));
