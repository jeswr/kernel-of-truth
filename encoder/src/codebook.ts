/**
 * The deterministic codebook for construction B
 * (deterministic-concept-vectors.md §7.3; architecture.md §1.2).
 *
 * WITHIN-CLAUSE, EXACT LEVEL — Sylvester-Hadamard rows.
 * The ~200 closed atoms are assigned rows of the D x D Sylvester-Hadamard
 * matrix H (H[i][j] = (-1)^popcount(i & j), i.e. the characters of (Z/2)^log2(D)),
 * scaled by 1/sqrt(D): an EXACTLY orthonormal deterministic codebook — no
 * seeds, no training (report §7.3 construction B "exact TPR over orthonormal
 * role/prime codes (deterministic Hadamard/DFT codebook)").
 *
 * Role-filler binding at this level is the elementwise (Hadamard) product,
 * which for Sylvester rows is the group operation on characters:
 *   row(a) ∘ row(b) ∘ sqrt(D) = row(a XOR b).
 * Binding therefore never leaves the codebook, unbinding is EXACT
 * (self-inverse), and crosstalk between distinct bound pairs is EXACTLY zero —
 * this is the compressed tensor-product binding of matched-filter TPR
 * (Smolensky 1990 AIJ 46) restricted to the character group, cf. VSA
 * "MAP" binding (Gayler, arXiv:cs/0412059) over an orthogonal codebook.
 *
 * INJECTIVITY OF BOUND PAIRS — bit-field index layout.
 * XOR binding aliases pairs whose index-XORs collide. We eliminate that
 * exactly by giving slots and fillers disjoint bit fields:
 *   row index = (slotId << FILLER_BITS) | fillerId,
 *   slotId  in 1..31  (5 bits;  0 = "bare filler"),
 *   fillerId in 1..255 (8 bits; 0 = "bare slot").
 * Every (slot, filler) pair then maps to a UNIQUE Hadamard row, all rows
 * mutually exactly orthogonal. This requires D >= 2^13 = 8192; smaller D
 * fails closed (the toy-native re-encode path of architecture.md §1.3 needs a
 * different construction and is out of scope for encoder v0).
 *
 * Numerical note: rows are exactly orthonormal in exact arithmetic; in
 * float64 the scaled entries ±1/sqrt(D) are rounded, so measured dot products
 * of distinct rows are 0 to within a few ulps (observed < 1e-15 at D=8192,
 * asserted < 1e-12 in test/codebook.test.ts) — 13+ orders of magnitude below
 * the smallest signal coefficient, i.e. crosstalk-free for every practical
 * purpose of the capacity analysis (report §7.2).
 *
 * ACROSS CLAUSES / DEPTH, UNITARY LEVEL — see encoder.ts: circular
 * convolution with unit-magnitude-spectrum tags (defined here), plus
 * deterministic position permutations (det.ts).
 */

import { DetStream, detPermutation, invertPermutation } from './det.js';
import { assertPowerOfTwo, type Complex64 } from './fft.js';
import {
  OPERATORS,
  EXPLICATION_FRAMES,
  REF_KINDS,
  PRIMES,
  ROLES,
  CAPS,
} from './lexicon.js';

export const FILLER_BITS = 8;
export const SLOT_BITS = 5;
export const MIN_D = 1 << (FILLER_BITS + SLOT_BITS); // 8192

// ---------------------------------------------------------------------------
// Slot table (5-bit field). Exactly 31 slots; the order below is pinned and
// participates in the encoder content-hash.
// ---------------------------------------------------------------------------

export const SLOTS = [
  ...ROLES, // 17 role slots (13 core + 4 adjuncts), gist §4.4
  'det', // SP determiner (gist §4.3)
  'quant', // SP quantifier
  'mod', // SP modifier
  'head', // SP head
  'of', // KIND/PART-frame of-target
  'restrictedBy', // SP restricting clause
  'bind', // SP introducing occurrence -> referent index
  'arg0', // operator argument 0
  'arg1', // operator argument 1
  'ctype', // clause-type tag (pred / op / quote-wrapper)
  'pred', // predicate prime
  'op', // operator identity
  'frame', // explication frame
  'refdecl', // referent declaration (kind under per-index permutation)
] as const;
export type SlotName = (typeof SLOTS)[number];

if ((SLOTS as readonly string[]).length !== 31) {
  throw new Error(`ERR_CODEBOOK: slot inventory must have 31 entries, got ${SLOTS.length}`);
}

// ---------------------------------------------------------------------------
// Filler table (8-bit field). Pinned assignment:
//   1..65    the 65 primes, by chartIndex (lexicon.ts, chart v20 2022 order)
//   66..76   operators OP:*, in OPERATORS order (gist §4.5)
//   77..79   explication frames, in EXPLICATION_FRAMES order (gist §4.6)
//   80..84   referent kinds, in REF_KINDS order (gist §4.2)
//   85..87   structural tags TAG:PRED, TAG:OP, TAG:QUOTE
//   88..97   intensified-mod combinations INTENS:{VERY,MORE}+{GOOD,BAD,BIG,SMALL}
//            and MORE+{MUCH~MANY,LITTLE~FEW} (closed set implied by gist
//            §4.3 "mod optionally under VERY/MORE" + §4.5 MORE over quant;
//            realised as dedicated atoms so the exact level never XORs two
//            filler codes together)
//   98..129  referent indices REF:1..REF:32 (CAPS.maxReferents)
// ---------------------------------------------------------------------------

export const INTENSIFIED_MODS = [
  'VERY+GOOD', 'VERY+BAD', 'VERY+BIG', 'VERY+SMALL',
  'MORE+GOOD', 'MORE+BAD', 'MORE+BIG', 'MORE+SMALL',
  'MORE+MUCH~MANY', 'MORE+LITTLE~FEW',
] as const;

export const STRUCT_TAGS = ['TAG:PRED', 'TAG:OP', 'TAG:QUOTE'] as const;

function buildFillerTable(): Map<string, number> {
  const t = new Map<string, number>();
  let id = 1;
  for (const prime of PRIMES) t.set(`prime:${prime.name}`, id++); // 1..65
  for (const op of OPERATORS) t.set(`op:${op}`, id++); // 66..76
  for (const f of EXPLICATION_FRAMES) t.set(`frame:${f}`, id++); // 77..79
  for (const k of REF_KINDS) t.set(`refkind:${k}`, id++); // 80..84
  for (const tag of STRUCT_TAGS) t.set(`tag:${tag}`, id++); // 85..87
  for (const m of INTENSIFIED_MODS) t.set(`imod:${m}`, id++); // 88..97
  for (let n = 1; n <= CAPS.maxReferents; n++) t.set(`ref:${n}`, id++); // 98..129
  if (id - 1 > 255) throw new Error(`ERR_CODEBOOK: ${id - 1} fillers exceed the 8-bit field`);
  return t;
}

export const FILLER_TABLE: ReadonlyMap<string, number> = buildFillerTable();
export const SLOT_TABLE: ReadonlyMap<string, number> = new Map(
  SLOTS.map((name, i) => [name, i + 1]), // slot ids 1..31
);

/**
 * The pinned codebook table as plain data: every named atom -> Hadamard row
 * index. This object is serialised into the encoder content-hash
 * (contentHash.ts), satisfying poc-design Common rule 2.
 */
export function codebookTable(): Record<string, number> {
  const out: Record<string, number> = {};
  for (const [name, id] of SLOT_TABLE) out[`slot:${name}`] = id << FILLER_BITS;
  for (const [name, id] of FILLER_TABLE) out[name] = id;
  return out;
}

// ---------------------------------------------------------------------------
// Hadamard rows
// ---------------------------------------------------------------------------

function popcount32(x: number): number {
  x -= (x >> 1) & 0x55555555;
  x = (x & 0x33333333) + ((x >> 2) & 0x33333333);
  x = (x + (x >> 4)) & 0x0f0f0f0f;
  return (x * 0x01010101) >> 24;
}

export interface EncoderParams {
  /** Vector dimension; power of two, >= 8192 (default 8192; architecture.md §1.3). */
  readonly D: number;
  /**
   * Superposition weight of structured (convolution-bound) child terms
   * relative to weight-1 exact atomic terms, applied before normalisation.
   * THE pinned free parameter of architecture.md §1.2 weakness (2)
   * ("superposition weighting is a free parameter ... pinned by content-hash
   * per encoder version and measured in X3"). Default 1.0.
   */
  readonly alphaStruct: number;
  /**
   * Weight multiplier for NOT-operator clause terms at their superposition
   * point — the polarity-aware weighting hook for X3 (architecture.md §1.2
   * weakness (1): polarity/similarity pathology mitigations). Default 1.0
   * (= plain construction B).
   */
  readonly notBoost: number;
}

export const DEFAULT_PARAMS: EncoderParams = Object.freeze({
  D: 8192,
  alphaStruct: 1.0,
  notBoost: 1.0,
});

export function checkParams(params: EncoderParams): void {
  assertPowerOfTwo(params.D, 'D');
  if (params.D < MIN_D) {
    throw new Error(
      `ERR_DIMENSION_TOO_SMALL: D=${params.D} < ${MIN_D}; the exact Hadamard level needs ` +
        `${SLOT_BITS}+${FILLER_BITS} index bits (architecture.md §1.3 toy-native re-encode is a separate construction)`,
    );
  }
  if (!(params.alphaStruct > 0) || !Number.isFinite(params.alphaStruct)) {
    throw new Error(`ERR_PARAM: alphaStruct must be finite and > 0, got ${params.alphaStruct}`);
  }
  if (!(params.notBoost > 0) || !Number.isFinite(params.notBoost)) {
    throw new Error(`ERR_PARAM: notBoost must be finite and > 0, got ${params.notBoost}`);
  }
}

/**
 * All deterministic structure shared by encoder and decoder for a given D.
 * Construction involves no seeds and no input data; instances are cached per D.
 */
export class Codebook {
  readonly D: number;
  private readonly rowCache = new Map<number, Float64Array>();
  private readonly tagCache = new Map<string, Complex64>();
  private readonly clausePerms: Uint32Array[] = [];
  private readonly clausePermInvs: Uint32Array[] = [];
  private readonly refdeclPerms: Uint32Array[] = [];
  private readonly refdeclPermInvs: Uint32Array[] = [];
  private readonly spreadPerm: Uint32Array;
  private readonly spreadPermInv: Uint32Array;
  private readonly spreadSign: Float64Array;

  constructor(D: number) {
    assertPowerOfTwo(D, 'D');
    if (D < MIN_D) throw new Error(`ERR_DIMENSION_TOO_SMALL: D=${D} < ${MIN_D}`);
    this.D = D;
    for (let i = 0; i < CAPS.maxClauses; i++) {
      const p = detPermutation(`clause/${i}`, D);
      this.clausePerms.push(p);
      this.clausePermInvs.push(invertPermutation(p));
    }
    for (let n = 1; n <= CAPS.maxReferents; n++) {
      const p = detPermutation(`refdecl/${n}`, D);
      this.refdeclPerms.push(p);
      this.refdeclPermInvs.push(invertPermutation(p));
    }
    this.spreadPerm = detPermutation('spread', D);
    this.spreadPermInv = invertPermutation(this.spreadPerm);
    const signStream = new DetStream('spread-sign');
    this.spreadSign = new Float64Array(D);
    for (let i = 0; i < D; i++) this.spreadSign[i] = signStream.nextBelow(2) === 0 ? 1 : -1;
  }

  /**
   * SPECTRAL WHITENER (part of the binding operator, pinned by
   * ALGORITHM_VERSION): a deterministic signed permutation
   * W x = P (s ∘ x), applied to every structured filler BEFORE circular-
   * convolution binding, and inverted after unbinding.
   *
   * Why it exists: Sylvester-Hadamard rows are Walsh functions, whose DFT
   * energy is CONCENTRATED (~90% in ~130 of 8192 bins, measured). Circular
   * convolution is diagonal in the DFT basis, so without whitening two
   * different slot tags alias sparse-spectrum atoms into each other with
   * crosstalk up to ~0.4 instead of the ~1/sqrt(D) the capacity analysis
   * assumes (Plate 1995 assumes i.i.d.-like, spectrally flat vectors;
   * Frady et al. 2018's bits/dim results likewise). W makes any codebook
   * superposition spectrally flat w.h.p. while being exactly unitary
   * (a signed permutation), exactly invertible, and float-error-free.
   */
  spread(v: Float64Array): Float64Array {
    const out = new Float64Array(v.length);
    for (let i = 0; i < v.length; i++) out[this.spreadPerm[i]!] = this.spreadSign[i]! * v[i]!;
    return out;
  }

  unspread(v: Float64Array): Float64Array {
    const out = new Float64Array(v.length);
    for (let i = 0; i < v.length; i++) out[i] = this.spreadSign[i]! * v[this.spreadPerm[i]!]!;
    return out;
  }

  /** Sylvester-Hadamard row `index`, scaled to unit norm. Cached. */
  row(index: number): Float64Array {
    if (!Number.isInteger(index) || index < 0 || index >= this.D) {
      throw new Error(`ERR_CODEBOOK_INDEX: row ${index} out of range for D=${this.D}`);
    }
    const hit = this.rowCache.get(index);
    if (hit !== undefined) return hit;
    const v = new Float64Array(this.D);
    const scale = 1 / Math.sqrt(this.D);
    for (let j = 0; j < this.D; j++) {
      v[j] = (popcount32(index & j) & 1) === 1 ? -scale : scale;
    }
    this.rowCache.set(index, v);
    return v;
  }

  private slotId(slot: SlotName): number {
    const id = SLOT_TABLE.get(slot);
    if (id === undefined) throw new Error(`ERR_CODEBOOK_SLOT: unknown slot '${slot}'`);
    return id;
  }

  private fillerId(filler: string): number {
    const id = FILLER_TABLE.get(filler);
    if (id === undefined) throw new Error(`ERR_CODEBOOK_FILLER: unknown filler '${filler}'`);
    return id;
  }

  /**
   * Exact bound atom for (slot, filler): row((slotId << 8) | fillerId).
   * This IS the within-clause TPR binding (see module header).
   */
  boundAtom(slot: SlotName, filler: string): Float64Array {
    return this.row((this.slotId(slot) << FILLER_BITS) | this.fillerId(filler));
  }

  /**
   * Unitary tag spectrum for a slot binding STRUCTURED fillers: quarter-phase
   * ({±1, ±i}) unit-magnitude spectrum with conjugate symmetry (real time
   * domain), phases drawn from the deterministic SHA-256 stream
   * `tag/<slot>`. Unit-magnitude spectra make circular-convolution binding
   * exactly unitary (Plate 1995; the NeurIPS-2021 unit-magnitude-projection
   * fix, deterministic-concept-vectors.md §8) — depth-stable variance, exact
   * unbinding by conjugation. Quarter phases are exactly representable in
   * float64, so tag construction itself involves no rounding.
   */
  tagSpectrum(slot: SlotName): Complex64 {
    const hit = this.tagCache.get(slot);
    if (hit !== undefined) return hit;
    const D = this.D;
    const stream = new DetStream(`tag/${slot}`);
    const re = new Float64Array(D);
    const im = new Float64Array(D);
    re[0] = stream.nextBelow(2) === 0 ? 1 : -1; // DC (real for real vectors)
    re[D / 2] = stream.nextBelow(2) === 0 ? 1 : -1; // Nyquist
    for (let k = 1; k < D / 2; k++) {
      const q = stream.nextBelow(4); // quarter phase
      const pr = q === 0 ? 1 : q === 2 ? -1 : 0;
      const pi = q === 1 ? 1 : q === 3 ? -1 : 0;
      re[k] = pr;
      im[k] = pi;
      re[D - k] = pr; // conjugate symmetry
      im[D - k] = -pi;
    }
    const spec = { re, im };
    this.tagCache.set(slot, spec);
    return spec;
  }

  /** Deterministic position permutation for clause-list index i (0-based). */
  clausePerm(i: number): Uint32Array {
    const p = this.clausePerms[i];
    if (p === undefined) throw new Error(`ERR_CLAUSE_INDEX: ${i} exceeds cap ${CAPS.maxClauses}`);
    return p;
  }

  clausePermInv(i: number): Uint32Array {
    const p = this.clausePermInvs[i];
    if (p === undefined) throw new Error(`ERR_CLAUSE_INDEX: ${i} exceeds cap ${CAPS.maxClauses}`);
    return p;
  }

  /** Deterministic permutation for referent declaration n (1-based). */
  refdeclPerm(n: number): Uint32Array {
    const p = this.refdeclPerms[n - 1];
    if (p === undefined) throw new Error(`ERR_REF_INDEX: ${n} exceeds cap ${CAPS.maxReferents}`);
    return p;
  }

  refdeclPermInv(n: number): Uint32Array {
    const p = this.refdeclPermInvs[n - 1];
    if (p === undefined) throw new Error(`ERR_REF_INDEX: ${n} exceeds cap ${CAPS.maxReferents}`);
    return p;
  }
}

const codebookCache = new Map<number, Codebook>();

export function getCodebook(D: number): Codebook {
  const hit = codebookCache.get(D);
  if (hit !== undefined) return hit;
  const cb = new Codebook(D);
  codebookCache.set(D, cb);
  return cb;
}
