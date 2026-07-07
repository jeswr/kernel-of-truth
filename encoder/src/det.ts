/**
 * Deterministic primitives. NOTHING here is seeded by anything external:
 * all pseudo-randomness used by the ENCODER derives from SHA-256 over fixed,
 * versioned domain-separation labels (so "same input -> byte-identical
 * output" holds across runs and platforms). The synthetic GENERATOR takes an
 * explicit caller seed (poc-design Phase X) and routes it through the same
 * SHA-256 counter stream.
 *
 * Determinism guarantees relied on (documented per the encoder spec):
 *  - IEEE-754 float64 `+ - * /` and `Math.sqrt` are exactly specified
 *    (correctly rounded) and bit-identical everywhere.
 *  - SHA-256 (node:crypto) is bit-exact by definition.
 *  - Integer ops on Uint32/Float64Array indices are exact.
 * The only transcendental functions in the whole encoder are Math.cos/Math.sin
 * in fft.ts (see the note there).
 */

import { createHash } from 'node:crypto';

/** Versioned domain-separation prefix. Bump with ALGORITHM_VERSION. */
export const DET_DOMAIN = 'kot/enc/v1';

/**
 * Deterministic byte stream: block i = SHA-256(`${DET_DOMAIN}/${label}/${i}`).
 * Counter-mode construction (cf. NIST SP 800-90A CTR_DRBG shape; here used as
 * a public deterministic expander, not a secret-keyed DRBG).
 */
export class DetStream {
  private block = 0;
  private buf: Buffer = Buffer.alloc(0);
  private pos = 0;

  constructor(private readonly label: string) {}

  private refill(): void {
    this.buf = createHash('sha256').update(`${DET_DOMAIN}/${this.label}/${this.block}`).digest();
    this.block += 1;
    this.pos = 0;
  }

  nextByte(): number {
    if (this.pos >= this.buf.length) this.refill();
    return this.buf[this.pos++]!;
  }

  nextUint32(): number {
    return (
      (this.nextByte() << 24) | (this.nextByte() << 16) | (this.nextByte() << 8) | this.nextByte()
    ) >>> 0;
  }

  /** Uniform integer in [0, n) by rejection sampling (unbiased, deterministic). */
  nextBelow(n: number): number {
    if (!Number.isInteger(n) || n <= 0 || n > 0x100000000) {
      throw new Error(`ERR_DET_RANGE: nextBelow(${n})`);
    }
    const limit = Math.floor(0x100000000 / n) * n;
    let u = this.nextUint32();
    while (u >= limit) u = this.nextUint32();
    return u % n;
  }

  /** Uniform float64 in [0, 1) with 53 bits of precision. */
  nextFloat(): number {
    const hi = this.nextUint32() >>> 6; // 26 bits
    const lo = this.nextUint32() >>> 5; // 27 bits
    return (hi * 134217728 + lo) / 9007199254740992; // (hi*2^27 + lo) / 2^53
  }
}

/**
 * Deterministic permutation of [0, n) via Fisher-Yates driven by a DetStream.
 * Exactly unitary as a linear map; used for clause-position and
 * referent-declaration binding (architecture.md §1.2 "position permutation").
 */
export function detPermutation(label: string, n: number): Uint32Array {
  const stream = new DetStream(`perm/${label}`);
  const p = new Uint32Array(n);
  for (let i = 0; i < n; i++) p[i] = i;
  for (let i = n - 1; i > 0; i--) {
    const j = stream.nextBelow(i + 1);
    const t = p[i]!;
    p[i] = p[j]!;
    p[j] = t;
  }
  return p;
}

export function invertPermutation(p: Uint32Array): Uint32Array {
  const inv = new Uint32Array(p.length);
  for (let i = 0; i < p.length; i++) inv[p[i]!] = i;
  return inv;
}

export function applyPermutation(p: Uint32Array, v: Float64Array): Float64Array {
  const out = new Float64Array(v.length);
  // out[p[i]] = v[i]: permutation as a linear operator P with P e_i = e_{p(i)}.
  for (let i = 0; i < v.length; i++) out[p[i]!] = v[i]!;
  return out;
}

// ---------------------------------------------------------------------------
// fp16 round-trip (X1 noise floor, poc-design Phase X):
// IEEE-754 binary16 with round-to-nearest-even, implemented in integer
// arithmetic so it is bit-exact everywhere.
// ---------------------------------------------------------------------------

const f32 = new Float32Array(1);
const u32 = new Uint32Array(f32.buffer);

export function toFloat16Bits(value: number): number {
  f32[0] = value; // f64 -> f32 (correctly rounded per IEEE-754)
  const x = u32[0]!;
  const sign = (x >>> 16) & 0x8000;
  let exp = (x >>> 23) & 0xff;
  let mant = x & 0x7fffff;
  if (exp === 0xff) return sign | 0x7c00 | (mant !== 0 ? 0x200 : 0); // Inf/NaN
  // Rebias 127 -> 15
  let e16 = exp - 127 + 15;
  if (e16 >= 0x1f) return sign | 0x7c00; // overflow -> Inf
  if (e16 <= 0) {
    // subnormal half (or zero)
    if (e16 < -10) return sign;
    mant |= 0x800000; // implicit leading 1
    const shift = 14 - e16; // bits to drop to reach 10-bit mantissa
    const half = 1 << (shift - 1);
    let m = mant >>> shift;
    const rem = mant & ((1 << shift) - 1);
    if (rem > half || (rem === half && (m & 1) === 1)) m += 1; // RNE
    return sign | m;
  }
  // normal half: drop 13 mantissa bits with RNE
  let m = mant >>> 13;
  const rem = mant & 0x1fff;
  if (rem > 0x1000 || (rem === 0x1000 && (m & 1) === 1)) {
    m += 1;
    if (m === 0x400) {
      m = 0;
      e16 += 1;
      if (e16 >= 0x1f) return sign | 0x7c00;
    }
  }
  return sign | (e16 << 10) | m;
}

export function fromFloat16Bits(h: number): number {
  const sign = (h & 0x8000) !== 0 ? -1 : 1;
  const exp = (h >>> 10) & 0x1f;
  const mant = h & 0x3ff;
  if (exp === 0) return sign * mant * 2 ** -24;
  if (exp === 0x1f) return mant !== 0 ? Number.NaN : sign * Number.POSITIVE_INFINITY;
  return sign * (1024 + mant) * 2 ** (exp - 25);
}

export function fp16RoundTrip(v: Float64Array): Float64Array {
  const out = new Float64Array(v.length);
  for (let i = 0; i < v.length; i++) out[i] = fromFloat16Bits(toFloat16Bits(v[i]!));
  return out;
}

// ---------------------------------------------------------------------------
// Explicitly seeded PRNG for the synthetic generator (NOT used by the encoder).
// SHA-256 counter stream keyed by the caller's seed string: deterministic
// across platforms, unlike engine-dependent Math.random.
// ---------------------------------------------------------------------------

export class SeededRng {
  private readonly stream: DetStream;

  constructor(seed: string) {
    if (typeof seed !== 'string' || seed.length === 0) {
      throw new Error('ERR_SEED_REQUIRED: the synthetic generator requires an explicit seed string');
    }
    this.stream = new DetStream(`synth-seed/${seed}`);
  }

  int(belowN: number): number {
    return this.stream.nextBelow(belowN);
  }

  float(): number {
    return this.stream.nextFloat();
  }

  pick<T>(items: readonly T[]): T {
    if (items.length === 0) throw new Error('ERR_EMPTY_PICK');
    return items[this.int(items.length)]!;
  }

  bool(pTrue: number): boolean {
    return this.float() < pTrue;
  }
}
