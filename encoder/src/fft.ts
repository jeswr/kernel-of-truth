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

/** Forward FFT of a real vector. */
export function fftReal(v: Float64Array): Complex64 {
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

/** Inverse FFT back to a real vector (imaginary parts discarded; they are
 * rounding-level for conjugate-symmetric spectra). */
export function ifftToReal(spec: Complex64): Float64Array {
  const re = Float64Array.from(spec.re);
  const im = Float64Array.from(spec.im);
  ifftInPlace(re, im);
  return re;
}
