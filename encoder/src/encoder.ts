/**
 * Construction-B encoder (deterministic-concept-vectors.md §7.3 B;
 * architecture.md §1.2): a two-level TPR/VSA encoder.
 *
 *  - WITHIN a clause: exact Hadamard TPR binding over the exactly orthonormal
 *    Sylvester-Hadamard codebook (codebook.ts) — zero crosstalk, exact
 *    unbinding, no seeds, no training.
 *  - ACROSS clauses / depth: unitary circular-convolution binding (HRR with
 *    unit-magnitude quarter-phase spectra; Plate IEEE TNN 6(3) 1995, with the
 *    unitary restriction that keeps variance depth-stable, §VIII-C) +
 *    deterministic position permutations (det.ts) + superposition with the
 *    pinned weighting parameters (EncoderParams; architecture.md §1.2
 *    weakness (2)).
 *  - Concept references bind the REFERENCED concept's own canonical vector
 *    ("reference-not-inline keeps the structure budget at s ≈ 100-200 bound
 *    terms", report §7.2) — memoised recursive encoding over a concept set.
 *
 * DETERMINISM: no RNG anywhere; all pseudo-random structure is derived from
 * SHA-256 over fixed labels (det.ts). Superposition is accumulated in a
 * single fixed traversal order (frame term, referent declarations by index,
 * clauses by position; within a clause: ctype, pred/op identity, then roles
 * in the pinned ROLES/arg order; within an SP: det, quant, mods in list
 * order, head, of, bind, restrictedBy). Float64 addition is not associative,
 * so THIS ORDER IS PART OF THE ALGORITHM and is pinned by ALGORITHM_VERSION
 * in the content hash. Same input -> byte-identical Float64Array on every
 * platform (see fft.ts for the single documented transcendental-function
 * caveat, guarded by X0 golden vectors).
 */

import type {
  Clause,
  Explication,
  Filler,
  OpArg,
  PredClause,
  OpClause,
  QuoteFiller,
  SP,
  TemporalAnchorFiller,
} from './ast.js';
import { applyPermutation } from './det.js';
import { fftReal, ifftToReal, spectrumMultiply } from './fft.js';
import {
  CodebookBase,
  DEFAULT_PARAMS,
  checkParams,
  getCodebook,
  type EncoderParams,
  type SlotName,
} from './codebook.js';
import { ROLES } from './lexicon.js';
import { validateExplication } from './validate.js';

export const ALGORITHM_VERSION = 'kot-enc-B/1';

export interface EncodeOptions {
  readonly params?: Partial<EncoderParams>;
  /**
   * Resolved concept lexicon: concept id -> canonical unit vector at D.
   * Required iff the explication contains concept references; a reference to
   * a missing id fails closed (ERR_CONCEPT_UNRESOLVED).
   */
  readonly concepts?: ReadonlyMap<string, Float64Array>;
}

export function resolveParams(partial?: Partial<EncoderParams>): EncoderParams {
  const params: EncoderParams = { ...DEFAULT_PARAMS, ...(partial ?? {}) };
  checkParams(params);
  return params;
}

/**
 * The construction-B encoding engine. INTERNAL: bypasses the validation
 * gates (the public entry point `encodeExplication` runs them first). The
 * decoder also uses this class to re-encode partially decoded fragments for
 * reconstruction peeling — such fragments may be invalid mid-decode, which is
 * why this class must not validate.
 */
export class InternalEncoder {
  readonly cb: CodebookBase;

  constructor(
    readonly params: EncoderParams,
    readonly concepts: ReadonlyMap<string, Float64Array> | undefined,
    cb?: CodebookBase,
  ) {
    // Default: the exact Hadamard codebook of construction B (kot-enc-B/1).
    // The toy-native variant (encoderQ.ts) injects a QuasiCodebook instead;
    // traversal, binding operators and weighting are shared unchanged.
    this.cb = cb ?? getCodebook(params.D);
  }

  /** v += w * t, fixed loop order. */
  private acc(v: Float64Array, t: Float64Array, w: number): void {
    for (let i = 0; i < v.length; i++) v[i] = v[i]! + w * t[i]!;
  }

  /** Normalise to unit norm; a zero vector fails closed (cannot happen for valid ASTs). */
  private unit(v: Float64Array, what: string): Float64Array {
    let s = 0;
    for (let i = 0; i < v.length; i++) s += v[i]! * v[i]!;
    if (!(s > 0)) throw new Error(`ERR_ZERO_VECTOR: ${what} produced a zero vector`);
    const inv = 1 / Math.sqrt(s);
    for (let i = 0; i < v.length; i++) v[i] = v[i]! * inv;
    return v;
  }

  /**
   * Unitary circular-convolution binding: tag_slot ⊛ W(f), via FFT, where W
   * is the deterministic spectral whitener (codebook.ts `spread`) that makes
   * Walsh-atom superpositions spectrally flat before the DFT-diagonal
   * convolution — without it, sparse Walsh spectra alias across slot tags.
   */
  private cbind(slot: SlotName, f: Float64Array): Float64Array {
    const spec = fftReal(this.cb.spread(f));
    const bound = spectrumMultiply(spec, this.cb.tagSpectrum(slot), false);
    return ifftToReal(bound);
  }

  /** Weight applied to a clause term at its superposition point (polarity hook, X3). */
  private clauseWeight(c: Clause): number {
    return c.type === 'op' && c.op === 'NOT' ? this.params.notBoost : 1;
  }

  conceptVector(id: string): Float64Array {
    const v = this.concepts?.get(id);
    if (v === undefined) {
      throw new Error(`ERR_CONCEPT_UNRESOLVED: concept '${id}' is not in the supplied concept lexicon`);
    }
    if (v.length !== this.params.D) {
      throw new Error(`ERR_CONCEPT_DIMENSION: concept '${id}' has D=${v.length}, encoder D=${this.params.D}`);
    }
    return v;
  }

  /** Atomic filler -> exact Hadamard atom name, or undefined if structured. */
  private atomicFillerName(f: Filler): string | undefined {
    if (f.kind === 'prime') return `prime:${f.prime}`;
    if (f.kind === 'ref') return `ref:${f.index}`;
    return undefined;
  }

  /** Encode any structured filler to a unit vector. */
  encodeStructuredFiller(f: Filler): Float64Array {
    switch (f.kind) {
      case 'sp':
        return this.encodeSP(f);
      case 'clause':
        return this.encodeClause(f.clause);
      case 'quote':
        return this.encodeQuote(f);
      case 'concept':
        return this.conceptVector(f.id);
      case 'temporal':
        return this.encodeTemporal(f);
      default:
        throw new Error(`ERR_INTERNAL: filler kind '${f.kind}' is not structured`);
    }
  }

  /**
   * Add one role/slot filler to an accumulating node vector:
   * exact atom for atomic fillers, unitary convolution for structured ones.
   */
  private accFiller(v: Float64Array, slot: SlotName, f: Filler): void {
    const atomic = this.atomicFillerName(f);
    if (atomic !== undefined) {
      this.acc(v, this.cb.boundAtom(slot, atomic), 1);
      return;
    }
    let w = this.params.alphaStruct;
    if (f.kind === 'clause') w *= this.clauseWeight(f.clause);
    this.acc(v, this.cbind(slot, this.encodeStructuredFiller(f)), w);
  }

  encodeSP(sp: SP): Float64Array {
    const v = new Float64Array(this.params.D);
    if (sp.det !== undefined) {
      // SOME-as-det shares the prime SOME's code; det vs quant slot disambiguates.
      const detPrime = sp.det === 'SOME' ? 'SOME' : sp.det;
      this.acc(v, this.cb.boundAtom('det', `prime:${detPrime}`), 1);
    }
    if (sp.quant !== undefined) this.acc(v, this.cb.boundAtom('quant', `prime:${sp.quant}`), 1);
    for (const m of sp.mods ?? []) {
      const filler = m.intensifier === undefined ? `prime:${m.mod}` : `imod:${m.intensifier}+${m.mod}`;
      this.acc(v, this.cb.boundAtom('mod', filler), 1);
    }
    const h = sp.head;
    switch (h.kind) {
      case 'primeHead':
        this.acc(v, this.cb.boundAtom('head', `prime:${h.prime}`), 1);
        break;
      case 'refHead':
        this.acc(v, this.cb.boundAtom('head', `ref:${h.index}`), 1);
        break;
      case 'conceptHead':
        this.acc(v, this.cbind('head', this.conceptVector(h.id)), this.params.alphaStruct);
        break;
      case 'kindFrame':
      case 'partFrame': {
        this.acc(v, this.cb.boundAtom('head', `prime:${h.kind === 'kindFrame' ? 'KIND' : 'PART'}`), 1);
        const of = h.of;
        if (of.kind === 'ref') this.acc(v, this.cb.boundAtom('of', `ref:${of.index}`), 1);
        else if (of.kind === 'concept') this.acc(v, this.cbind('of', this.conceptVector(of.id)), this.params.alphaStruct);
        else this.acc(v, this.cbind('of', this.encodeSP(of)), this.params.alphaStruct);
        break;
      }
    }
    if (sp.bind !== undefined) this.acc(v, this.cb.boundAtom('bind', `ref:${sp.bind}`), 1);
    if (sp.restrictedBy !== undefined) {
      this.acc(
        v,
        this.cbind('restrictedBy', this.encodeClause(sp.restrictedBy)),
        this.params.alphaStruct * this.clauseWeight(sp.restrictedBy),
      );
    }
    return this.unit(v, 'SP');
  }

  private encodeTemporal(f: TemporalAnchorFiller): Float64Array {
    const v = new Float64Array(this.params.D);
    this.acc(v, this.cb.boundAtom('op', `op:${f.op}`), 1);
    const a = f.anchor;
    if (a.kind === 'prime') this.acc(v, this.cb.boundAtom('arg0', `prime:${a.prime}`), 1);
    else if (a.kind === 'ref') this.acc(v, this.cb.boundAtom('arg0', `ref:${a.index}`), 1);
    else this.acc(v, this.cbind('arg0', this.encodeSP(a)), this.params.alphaStruct);
    return this.unit(v, 'temporal anchor');
  }

  /** Ordered clause list -> superposition of position-permuted clause vectors. */
  private encodeClauseList(clauses: readonly Clause[], v: Float64Array): void {
    for (const [i, c] of clauses.entries()) {
      const cv = this.encodeClause(c);
      this.acc(v, applyPermutation(this.cb.clausePerm(i), cv), this.clauseWeight(c));
    }
  }

  private encodeQuote(q: QuoteFiller): Float64Array {
    const v = new Float64Array(this.params.D);
    this.acc(v, this.cb.boundAtom('ctype', 'tag:TAG:QUOTE'), 1);
    this.encodeClauseList(q.clauses, v);
    return this.unit(v, 'quote');
  }

  encodeClause(c: Clause): Float64Array {
    return c.type === 'pred' ? this.encodePredClause(c) : this.encodeOpClause(c);
  }

  private encodePredClause(c: PredClause): Float64Array {
    const v = new Float64Array(this.params.D);
    this.acc(v, this.cb.boundAtom('ctype', 'tag:TAG:PRED'), 1);
    this.acc(v, this.cb.boundAtom('pred', `prime:${c.pred}`), 1);
    for (const role of ROLES) {
      const f = c.roles[role];
      if (f === undefined) continue;
      this.accFiller(v, role, f);
    }
    return this.unit(v, `pred clause ${c.pred}`);
  }

  private encodeOpArg(v: Float64Array, slot: 'arg0' | 'arg1', arg: OpArg): void {
    if ('type' in arg) {
      // clause argument
      this.acc(
        v,
        this.cbind(slot, this.encodeClause(arg)),
        this.params.alphaStruct * this.clauseWeight(arg),
      );
      return;
    }
    this.accFiller(v, slot, arg);
  }

  private encodeOpClause(c: OpClause): Float64Array {
    const v = new Float64Array(this.params.D);
    this.acc(v, this.cb.boundAtom('ctype', 'tag:TAG:OP'), 1);
    this.acc(v, this.cb.boundAtom('op', `op:${c.op}`), 1);
    this.encodeOpArg(v, 'arg0', c.args[0]!);
    if (c.args.length > 1) this.encodeOpArg(v, 'arg1', c.args[1]!);
    return this.unit(v, `op clause ${c.op}`);
  }

  encodeExplication(e: Explication): Float64Array {
    const v = new Float64Array(this.params.D);
    // 1. Frame term (gist §4.6).
    this.acc(v, this.cb.boundAtom('frame', `frame:${e.frame}`), 1);
    // 2. Referent declarations: kind atom under the per-index deterministic
    //    permutation ρ_n (exactly unitary; see codebook.ts header — the
    //    (index x kind) product space exceeds the 13-bit exact-atom budget,
    //    so this level uses permutation binding instead of Hadamard XOR).
    for (const r of e.referents) {
      const kindAtom = this.cb.boundAtom('refdecl', `refkind:${r.refKind}`);
      this.acc(v, applyPermutation(this.cb.refdeclPerm(r.index), kindAtom), 1);
    }
    // 3. Ordered clauses under position permutations π_i.
    this.encodeClauseList(e.clauses, v);
    return this.unit(v, 'explication');
  }
}

/**
 * Encode a validated explication to its canonical unit vector at D.
 * Validation gates run first and fail closed.
 */
export function encodeExplication(e: Explication, opts?: EncodeOptions): Float64Array {
  validateExplication(e);
  const params = resolveParams(opts?.params);
  return new InternalEncoder(params, opts?.concepts).encodeExplication(e);
}

// ---------------------------------------------------------------------------
// Memoised recursive encoding over a concept set (architecture.md §1.2:
// "concept references bind the referenced concept's own canonical vector").
// ---------------------------------------------------------------------------

function collectConceptRefs(e: Explication): Set<string> {
  const ids = new Set<string>();
  const walkFiller = (f: Filler): void => {
    switch (f.kind) {
      case 'concept': ids.add(f.id); return;
      case 'sp': walkSP(f); return;
      case 'clause': walkClause(f.clause); return;
      case 'quote': f.clauses.forEach(walkClause); return;
      case 'temporal': if (f.anchor.kind === 'sp') walkSP(f.anchor); return;
      default: return;
    }
  };
  const walkSP = (sp: SP): void => {
    const h = sp.head;
    if (h.kind === 'conceptHead') ids.add(h.id);
    else if (h.kind === 'kindFrame' || h.kind === 'partFrame') {
      if (h.of.kind === 'concept') ids.add(h.of.id);
      else if (h.of.kind === 'sp') walkSP(h.of);
    }
    if (sp.restrictedBy !== undefined) walkClause(sp.restrictedBy);
  };
  const walkClause = (c: Clause): void => {
    if (c.type === 'pred') {
      for (const role of ROLES) {
        const f = c.roles[role];
        if (f !== undefined) walkFiller(f);
      }
    } else {
      for (const a of c.args) {
        if ('type' in a) walkClause(a);
        else walkFiller(a);
      }
    }
  };
  e.clauses.forEach(walkClause);
  return ids;
}

export interface ConceptSetResult {
  /** Concept id -> canonical unit vector at D. */
  readonly vectors: Map<string, Float64Array>;
}

/**
 * Encode a set of concept definitions with cross-references, memoised.
 * References must form a DAG over the set (plus optional pre-resolved
 * external vectors); cycles fail closed — fixed-point encoding of cyclic
 * definitions (gist cap: SCC size <= 32 at the HASH layer) is not defined
 * for encoder v0 and is tracked as follow-up work.
 */
export function encodeConceptSet(
  defs: ReadonlyMap<string, Explication>,
  opts?: EncodeOptions,
): ConceptSetResult {
  return encodeConceptSetWith(defs, resolveParams(opts?.params), undefined, opts);
}

/**
 * INTERNAL (used by the toy-native variant encoderQ.ts and by certification
 * harnesses that need to inject a fresh codebook instance): memoised
 * reference-DAG concept-set encoding against an explicit codebook. `params`
 * must already be validated by the caller's resolve function.
 */
export function encodeConceptSetWith(
  defs: ReadonlyMap<string, Explication>,
  params: EncoderParams,
  cb: CodebookBase | undefined,
  opts?: EncodeOptions,
): ConceptSetResult {
  const resolved = new Map<string, Float64Array>(opts?.concepts ?? []);
  const inProgress = new Set<string>();

  const resolve = (id: string, chain: string[]): void => {
    if (resolved.has(id)) return;
    const def = defs.get(id);
    if (def === undefined) {
      throw new Error(
        `ERR_CONCEPT_UNRESOLVED: '${id}' (via ${chain.join(' -> ') || 'root'}) is neither defined nor pre-resolved`,
      );
    }
    if (inProgress.has(id)) {
      throw new Error(`ERR_CYCLIC_CONCEPT_REF: ${[...chain, id].join(' -> ')} (encoder v0 requires a reference DAG)`);
    }
    inProgress.add(id);
    validateExplication(def);
    for (const dep of [...collectConceptRefs(def)].sort()) resolve(dep, [...chain, id]);
    const enc = new InternalEncoder(params, resolved, cb);
    resolved.set(id, enc.encodeExplication(def));
    inProgress.delete(id);
  };

  for (const id of [...defs.keys()].sort()) resolve(id, []);
  return { vectors: resolved };
}
