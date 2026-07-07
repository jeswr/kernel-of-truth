/**
 * QUASI-ORTHOGONAL codebook for the toy-native encoder variant kot-enc-Bq/1
 * (bead kernel-of-truth-5xo; architecture.md §1.3 dimension policy, path (i)).
 *
 * WHY THIS EXISTS. The exact construction-B codebook (codebook.ts) assigns
 * every (slot, filler) bound pair its own Sylvester-Hadamard row via the
 * disjoint bit fields (slotId << 8) | fillerId — 5 + 8 = 13 index bits, so it
 * needs D >= 2^13 = 8192 and fails closed below that. The toy-native path
 * re-encodes the kernel AT the host model's embedding width (D = 512 for the
 * E1 toy, D = 576 for SmolLM2-135M), where the ~200 closed atoms x 31 slots
 * of bound-pair space (31 x 129 = 3,999 constructible pairs) cannot be
 * mutually exactly orthogonal (max D orthogonal vectors in R^D). The variant
 * therefore uses a deterministic QUASI-orthogonal codebook and certifies its
 * coherence offline (poc/src/qcert.ts), per the pre-registration.
 *
 * THE CONSTRUCTION (the substantive design decision):
 * each (slot, filler) pair gets an independent deterministic Rademacher code
 *   atom[i] = ±1/sqrt(D),  signs from the SHA-256 counter stream
 *   label `qatom/<D>/<slotId>/<fillerId>` (det.ts DetStream; ids are the
 *   pinned codebook-table ids, the same ids that formed the Hadamard row
 *   index at D=8192).
 * Properties: exactly unit norm up to one sqrt rounding; bit-exact across
 * platforms (integer sign draws; no transcendentals); label-addressable
 * (anyone can regenerate any atom from the pin alone). Pairwise coherence:
 * distinct atoms are independent sign vectors, so cos = (1/D)·sum of D
 * Rademacher products, sub-Gaussian with sigma = 1/sqrt(D); over m atoms the
 * expected maximum of the m(m-1)/2 pairs is ~ sqrt(4·ln(m)/D) — the
 * quasi-orthogonal mu ≈ sqrt(ln m / D) regime of
 * reports/deterministic-concept-vectors.md §7.2, measured and reported (max
 * AND distribution, over all 3,999 constructible atoms and over the
 * corpus-realised subset) by the offline certification harness.
 *
 * ALTERNATIVES CONSIDERED AND REJECTED:
 *  - Truncated partial Hadamard (keep the 13-bit row index, take the first D
 *    columns): catastrophic — Sylvester row r restricted to columns 0..D-1
 *    depends only on r mod D (H[r][j] = (-1)^popcount(r & j) and j < D only
 *    exercises the low log2(D) bits of r), so rows sharing low bits become
 *    IDENTICAL (coherence 1.0). Fails harder than random, not better.
 *  - Row-sampled D x D Hadamard: only D exactly-orthogonal atoms available
 *    (512 < 3,999), and D = 576 is not a Hadamard order served by Sylvester.
 *  - Kerdock / Delsarte-Goethals mutually-unbiased-bases codebooks: certified
 *    mu = 1/sqrt(D) for up to ~D^2/2 codewords — but they exist for length
 *    2^m with m EVEN; 512 = 2^9 (m odd) misses, 576 is not a power of two.
 *  - Alltop / chirp codebooks (mu = 1/sqrt(D)): require prime length (and are
 *    complex-valued); 512 and 576 are not prime.
 *  - Numerically-optimised Grassmannian packings: not label-deterministic, no
 *    closed form to pin in a content hash, and at m/D ≈ 7-8 the achievable
 *    gain over seeded random is marginal while auditability is lost.
 * So no structured construction certifiably beats seeded random AT THESE TWO
 * DIMENSIONS; the seeded-sign construction is chosen for bit-exactness,
 * auditability, and matched-filter decode compatibility.
 *
 * WHAT IS LOST vs D = 8192 (stated plainly, per the pre-registration):
 *  - EXACT UNBINDING IS GONE. XOR-closure of the Hadamard group no longer
 *    exists; within-clause decode is matched filtering against a coherent
 *    dictionary, so every sibling term leaks ~1/sqrt(D) crosstalk instead of
 *    exactly zero.
 *  - THE CROSSTALK FLOOR IS NONZERO. A clause superposing s terms carries
 *    signal-to-crosstalk ~ sqrt(D/s) per matched filter; at D = 512-576 and
 *    s ≈ 5-30 that is ~4-10, vs effectively infinite (1e-15 crosstalk) in the
 *    exact codebook. Full-depth decode of the capped explication space
 *    CANNOT survive at this D (DCV §7.2: robust decode needs D ≈ 4k-20k);
 *    the variant is scoped to E1/E4's "structure-derived content vs
 *    content-free at matched D" question, explicitly NOT the capacity story.
 *    Decode is measured and reported for honesty (X2-q) but NOT gated.
 *
 * Everything else — unitary tag spectra, spectral whitener, clause-position
 * and referent permutations, traversal order, weighting — is inherited
 * unchanged from CodebookBase / InternalEncoder (same AST -> vector pipeline;
 * circular convolution at D = 576 runs on the Bluestein chirp-z path in
 * fft.ts because 576 is not a power of two).
 */

import { DetStream } from './det.js';
import { CodebookBase, SLOT_TABLE, FILLER_TABLE, type SlotName } from './codebook.js';

/**
 * The two pre-registered toy-native dimensions (architecture.md §1.3 path
 * (i)): 512 = the E1 toy's d_model, 576 = SmolLM2-135M's d_model. Any other
 * dimension is a NEW pre-registration (poc-design Common rule 2) and fails
 * closed here.
 */
export const QUASI_DIMS = [512, 576] as const;

export class QuasiCodebook extends CodebookBase {
  private readonly atomCache = new Map<string, Float64Array>();

  constructor(D: number) {
    if (!(QUASI_DIMS as readonly number[]).includes(D)) {
      throw new Error(
        `ERR_QUASI_DIMENSION: D=${D} is not a pre-registered toy-native dimension ` +
          `(${QUASI_DIMS.join(', ')}); other dimensions are a new pre-registration (poc-design Common rule 2)`,
      );
    }
    super(D);
  }

  /**
   * Quasi-orthogonal bound atom for (slot, filler): deterministic Rademacher
   * code, signs from SHA-256 label `qatom/<D>/<slotId>/<fillerId>`. Unknown
   * slot/filler names fail closed exactly as in the exact codebook.
   */
  boundAtom(slot: SlotName, filler: string): Float64Array {
    const key = `${slot}|${filler}`;
    const hit = this.atomCache.get(key);
    if (hit !== undefined) return hit;
    const sId = this.slotId(slot);
    const fId = this.fillerId(filler);
    const stream = new DetStream(`qatom/${this.D}/${sId}/${fId}`);
    const v = new Float64Array(this.D);
    const scale = 1 / Math.sqrt(this.D);
    for (let i = 0; i < this.D; i++) v[i] = stream.nextBelow(2) === 0 ? scale : -scale;
    this.atomCache.set(key, v);
    return v;
  }

  /**
   * The (slot, filler) pairs this instance has actually constructed — on a
   * fresh instance that encoded exactly one corpus, this IS the realised
   * bound-pair code set the offline coherence certification must cover.
   */
  usedAtoms(): { slot: SlotName; filler: string }[] {
    return [...this.atomCache.keys()].map((k) => {
      const [slot, filler] = k.split('|');
      return { slot: slot as SlotName, filler: filler! };
    });
  }
}

/** Enumerate every constructible (slot, filler) pair: the full atom space. */
export function allAtomPairs(): { slot: SlotName; filler: string }[] {
  const out: { slot: SlotName; filler: string }[] = [];
  for (const slot of SLOT_TABLE.keys()) {
    for (const filler of FILLER_TABLE.keys()) out.push({ slot: slot as SlotName, filler });
  }
  return out;
}

const quasiCache = new Map<number, QuasiCodebook>();

export function getQuasiCodebook(D: number): QuasiCodebook {
  const hit = quasiCache.get(D);
  if (hit !== undefined) return hit;
  const cb = new QuasiCodebook(D);
  quasiCache.set(D, cb);
  return cb;
}
