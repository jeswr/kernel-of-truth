/**
 * Radix-2 iterative FFT (decimation-in-time, Cooley-Tukey), self-contained —
 * no dependencies, fixed operation order.
 *
 * Used for the cross-clause unitary circular-convolution binding
 * (architecture.md §1.2; deterministic-concept-vectors.md §7.3 construction B:
 * "unitary circular-convolution binding (no depth-variance growth
 * [Plate, IEEE TNN 6(3) 1995, §VIII-C])").
 *
 * DETERMINISM NOTE (operation-order guarantee relied on): all arithmetic is
 * IEEE-754 float64 with a fixed order of operations, so results are
 * bit-identical across runs. Twiddle factors use Math.cos/Math.sin — the only
 * transcendental calls in the encoder. V8 (all Node.js platforms) implements
 * them with a single software fdlibm port, so values are bit-identical across
 * OS/CPU for a given engine; this is asserted operationally by the X0
 * golden-vector suite rather than assumed silently. Twiddles are cached per
 * size after first computation (computation itself is deterministic, caching
 * cannot change values).
 */

export interface Complex64 {
  re: Float64Array;
  im: Float64Array;
}

const twiddleCache = new Map<number, { cos: Float64Array; sin: Float64Array }>();

function twiddles(n: number): { cos: Float64Array; sin: Float64Array } {
  const hit = twiddleCache.get(n);
  if (hit !== undefined) return hit;
  const cos = new Float64Array(n / 2);
  const sin = new Float64Array(n / 2);
  for (let k = 0; k < n / 2; k++) {
    const ang = (-2 * Math.PI * k) / n;
    cos[k] = Math.cos(ang);
    sin[k] = Math.sin(ang);
  }
  const entry = { cos, sin };
  twiddleCache.set(n, entry);
  return entry;
}

function bitReverseInPlace(re: Float64Array, im: Float64Array): void {
  const n = re.length;
  for (let i = 1, j = 0; i < n; i++) {
    let bit = n >> 1;
    for (; (j & bit) !== 0; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) {
      let t = re[i]!; re[i] = re[j]!; re[j] = t;
      t = im[i]!; im[i] = im[j]!; im[j] = t;
    }
  }
}

export function assertPowerOfTwo(n: number, what: string): void {
  if (!Number.isInteger(n) || n < 2 || (n & (n - 1)) !== 0) {
    throw new Error(`ERR_NOT_POWER_OF_TWO: ${what} must be a power of two, got ${n}`);
  }
}

export function isPowerOfTwo(n: number): boolean {
  return Number.isInteger(n) && n >= 2 && (n & (n - 1)) === 0;
}

// ---------------------------------------------------------------------------
// Arbitrary-length DFT via Bluestein's chirp-z algorithm (Bluestein 1970,
// IEEE Trans. Audio Electroacoust. 18(4)) — needed by the toy-native
// quasi-orthogonal variant (encoderQ.ts) whose D is the host model's d_model,
// e.g. 576 = 2^6 * 3^2, which the radix-2 path cannot serve. The length-n DFT
// is rewritten as a length-m (power-of-two, m >= 2n-1) circular convolution
// with a chirp, computed by the exact radix-2 kernel above:
//   y[k] = c[k] * sum_j (x[j] c[j]) conj(c)[k-j],  c[j] = exp(-i*pi*j^2/n),
// using j^2 mod 2n (exact integer arithmetic) so chirp angles stay small.
// DETERMINISM: same fixed-operation-order / Math.cos-Math.sin caveat as the
// twiddle factors above; asserted operationally by the variant's X0-q
// golden-vector suite. Chirp and conj-chirp spectra are cached per n.
// Numerical note: unlike the exact radix-2 path this route costs ~1e-13
// relative rounding per transform — far beneath the variant's quasi-
// orthogonal crosstalk floor (~1/sqrt(D) ~ 4e-2), and every encoder node is
// re-normalised after superposition anyway.
// ---------------------------------------------------------------------------

interface BluesteinPlan {
  m: number;
  cRe: Float64Array; // chirp c[j] = exp(-i*pi*j^2/n), j < n
  cIm: Float64Array;
  bRe: Float64Array; // FFT_m of the wrapped conjugate chirp
  bIm: Float64Array;
}

const bluesteinCache = new Map<number, BluesteinPlan>();

function bluesteinPlan(n: number): BluesteinPlan {
  const hit = bluesteinCache.get(n);
  if (hit !== undefined) return hit;
  let m = 1;
  while (m < 2 * n - 1) m <<= 1;
  const cRe = new Float64Array(n);
  const cIm = new Float64Array(n);
  const bRe = new Float64Array(m);
  const bIm = new Float64Array(m);
  const twoN = 2 * n;
  for (let j = 0; j < n; j++) {
    const ang = (-Math.PI * ((j * j) % twoN)) / n;
    cRe[j] = Math.cos(ang);
    cIm[j] = Math.sin(ang);
    bRe[j] = cRe[j]!;
    bIm[j] = -cIm[j]!; // conj chirp
    if (j > 0) {
      bRe[m - j] = bRe[j]!;
      bIm[m - j] = bIm[j]!;
    }
  }
  fftInPlace(bRe, bIm);
  const plan: BluesteinPlan = { m, cRe, cIm, bRe, bIm };
  bluesteinCache.set(n, plan);
  return plan;
}

/** Length-n forward DFT (no scaling) of a complex input, any n >= 2, via Bluestein. */
function bluesteinDft(reIn: Float64Array, imIn: Float64Array): Complex64 {
  const n = reIn.length;
  const p = bluesteinPlan(n);
  const are = new Float64Array(p.m);
  const aim = new Float64Array(p.m);
  for (let j = 0; j < n; j++) {
    are[j] = reIn[j]! * p.cRe[j]! - imIn[j]! * p.cIm[j]!;
    aim[j] = reIn[j]! * p.cIm[j]! + imIn[j]! * p.cRe[j]!;
  }
  fftInPlace(are, aim);
  for (let k = 0; k < p.m; k++) {
    const r = are[k]! * p.bRe[k]! - aim[k]! * p.bIm[k]!;
    const i = are[k]! * p.bIm[k]! + aim[k]! * p.bRe[k]!;
    are[k] = r;
    aim[k] = i;
  }
  ifftInPlace(are, aim);
  const re = new Float64Array(n);
  const im = new Float64Array(n);
  for (let k = 0; k < n; k++) {
    re[k] = are[k]! * p.cRe[k]! - aim[k]! * p.cIm[k]!;
    im[k] = are[k]! * p.cIm[k]! + aim[k]! * p.cRe[k]!;
  }
  return { re, im };
}

/** In-place forward FFT. */
export function fftInPlace(re: Float64Array, im: Float64Array): void {
  const n = re.length;
  assertPowerOfTwo(n, 'FFT size');
  bitReverseInPlace(re, im);
  const { cos, sin } = twiddles(n);
  for (let len = 2; len <= n; len <<= 1) {
    const half = len >> 1;
    const step = n / len;
    for (let i = 0; i < n; i += len) {
      for (let k = 0; k < half; k++) {
        const tw = k * step;
        const wr = cos[tw]!;
        const wi = sin[tw]!;
        const a = i + k;
        const b = a + half;
        const xr = re[b]! * wr - im[b]! * wi;
        const xi = re[b]! * wi + im[b]! * wr;
        re[b] = re[a]! - xr;
        im[b] = im[a]! - xi;
        re[a] = re[a]! + xr;
        im[a] = im[a]! + xi;
      }
    }
  }
}

/** In-place inverse FFT (conjugate method; includes the 1/n scaling). */
export function ifftInPlace(re: Float64Array, im: Float64Array): void {
  const n = re.length;
  for (let i = 0; i < n; i++) im[i] = -im[i]!;
  fftInPlace(re, im);
  const inv = 1 / n;
  for (let i = 0; i < n; i++) {
    re[i] = re[i]! * inv;
    im[i] = -im[i]! * inv;
  }
}

/** Forward DFT of a real vector: exact radix-2 FFT for power-of-two lengths
 * (bit-identical to encoder v0 kot-enc-B/1), Bluestein chirp-z otherwise. */
export function fftReal(v: Float64Array): Complex64 {
  if (!isPowerOfTwo(v.length)) return bluesteinDft(v, new Float64Array(v.length));
  const re = Float64Array.from(v);
  const im = new Float64Array(v.length);
  fftInPlace(re, im);
  return { re, im };
}

/**
 * Multiply spectra pointwise: (a.re + i a.im) * (b.re + i b.im). If conjB,
 * uses conj(b) — the exact unbinding (correlation) for unitary b, since for
 * unit-magnitude spectra conj = inverse (Plate 1995 §III: involution
 * approximate inverse becomes exact in the unitary case).
 */
export function spectrumMultiply(a: Complex64, b: Complex64, conjB: boolean): Complex64 {
  const n = a.re.length;
  if (b.re.length !== n) throw new Error('ERR_SPECTRUM_LENGTH');
  const re = new Float64Array(n);
  const im = new Float64Array(n);
  const sgn = conjB ? -1 : 1;
  for (let i = 0; i < n; i++) {
    const br = b.re[i]!;
    const bi = sgn * b.im[i]!;
    re[i] = a.re[i]! * br - a.im[i]! * bi;
    im[i] = a.re[i]! * bi + a.im[i]! * br;
  }
  return { re, im };
}

/** Inverse DFT back to a real vector (imaginary parts discarded; they are
 * rounding-level for conjugate-symmetric spectra). Radix-2 for power-of-two
 * lengths; Bluestein via IDFT(x) = conj(DFT(conj(x)))/n otherwise. */
export function ifftToReal(spec: Complex64): Float64Array {
  const n = spec.re.length;
  if (!isPowerOfTwo(n)) {
    const negIm = new Float64Array(n);
    for (let i = 0; i < n; i++) negIm[i] = -spec.im[i]!;
    const y = bluesteinDft(spec.re, negIm);
    const out = new Float64Array(n);
    const inv = 1 / n;
    for (let i = 0; i < n; i++) out[i] = y.re[i]! * inv;
    return out;
  }
  const re = Float64Array.from(spec.re);
  const im = Float64Array.from(spec.im);
  ifftInPlace(re, im);
  return re;
}
