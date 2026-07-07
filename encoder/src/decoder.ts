/**
 * Decoder: recursive unbinding + nearest-neighbour cleanup against a supplied
 * kernel lexicon, with per-step confidence reporting
 * (architecture.md §1.2 "Decoding"; deterministic-concept-vectors.md §7.3 B:
 * "decoding by recursive unbinding + cleanup"; §7.4(3): decodability is
 * always GIVEN THE KERNEL — the closed codebook + the concept-vector lexicon
 * ARE the cleanup memory).
 *
 * Mechanics:
 *  - Exact within-clause atoms are recovered by matched filtering against the
 *    orthonormal Hadamard codebook (dot products; crosstalk from sibling
 *    atoms is EXACTLY zero, from everything else ~N(0, 1/D)).
 *  - Structured children are recovered by conjugate-spectrum unbinding of the
 *    slot tag (the exact inverse of unitary binding, Plate 1995 §III) and
 *    recursive decode; the closed valency frames / operator classes tell the
 *    decoder WHICH structure types are licensed where.
 *  - Because the encoder is deterministic, every decoded element can be
 *    RE-ENCODED and its contribution subtracted (matching-pursuit peeling,
 *    cf. GrapHD's iterative decode, arXiv:2205.07826, and resonator-style
 *    cleanup, Frady/Kent/Olshausen/Sommer 2020). A few global refinement
 *    passes re-decode each top-level element against the residual of all the
 *    others; this is what makes depth > 2 recovery possible at D = 8192
 *    (X2 measures exactly where it stops).
 *  - After convergence, a residual-completion phase recovers deep OPTIONAL
 *    content whose in-decode presence signature is beneath the noise floor
 *    (kernel-of-truth-0kn): the converged AST is re-encoded and subtracted
 *    from v, leaving the missed content as nearly the only thing in the
 *    global residual; every empty optional site is probed there, and a
 *    candidate is accepted only if re-encoding the edited clause explains
 *    the residual strictly better (an exact matched-filter competition a
 *    phantom cannot win — its predicted contribution is absent from v).
 *
 * The decoder is fully deterministic. Thresholds are decoder heuristics
 * (DecodeOptions), NOT part of the encoder pin; the encoder content-hash is
 * unaffected by them.
 */

import type {
  Clause,
  Explication,
  Filler,
  OpArg,
  ReferentDecl,
  SP,
  SPHead,
  SPModifier,
} from './ast.js';
import { AST_SCHEMA, canonicalJson } from './ast.js';
import { applyPermutation } from './det.js';
import { fftReal, ifftToReal, spectrumMultiply } from './fft.js';
import { type CodebookBase, type EncoderParams, type SlotName } from './codebook.js';
import { INTENSIFIED_MODS } from './codebook.js';
import {
  CAPS,
  EXPLICATION_FRAMES,
  FRAME_BY_PRED,
  OPERATORS,
  OPERATOR_CLASS,
  PREDICATE_FRAMES,
  PRIMES,
  REF_KINDS,
  ROLES,
  ADJUNCT_ROLES,
  SP_MODS,
  SP_QUANTIFIERS,
  DURATION_FILLERS,
  type Operator,
  type Role,
  type SlotFillerKind,
  type RefKind,
  type ExplicationFrame,
} from './lexicon.js';
import { InternalEncoder, resolveParams, type EncodeOptions } from './encoder.js';
import { validateExplication } from './validate.js';

export interface DecodeStep {
  readonly path: string;
  readonly decision: string;
  readonly value: string;
  /** Selection margin (best vs runner-up ratio) or presence ratio, in [0, 1]. */
  readonly confidence: number;
}

export interface DecodeOptions extends EncodeOptions {
  /**
   * Absolute presence floor for matched-filter responses, in units of the
   * probed vector's norm. Default 5/sqrt(D) (≈ 5σ of the ~N(0, 1/D)
   * crosstalk noise on a unit vector — max over the ~130-candidate probe
   * sets stays below it with high probability, so phantom optional slots are
   * rare while true signals, once refinement has peeled the interference,
   * sit an order of magnitude above it).
   */
  readonly thetaAbs?: number;
  /** Global refinement passes (re-decode each element against the residual of the others). Default 3. */
  readonly refineIterations?: number;
}

export interface DecodeResult {
  readonly explication: Explication | null;
  /** True iff a complete AST was recovered AND it passes the validation gates. */
  readonly ok: boolean;
  readonly validationError?: string;
  readonly steps: readonly DecodeStep[];
  readonly minConfidence: number;
}

interface Pick {
  name: string;
  score: number;
  margin: number;
}

const PRED_NAMES = PREDICATE_FRAMES.map((f) => f.pred);
const PRIME_NAMES = PRIMES.map((p) => p.name);
const REF_FILLERS = Array.from({ length: CAPS.maxReferents }, (_, i) => `ref:${i + 1}`);
const HEAD_CANDIDATES = [...PRIME_NAMES.map((p) => `prime:${p}`), ...REF_FILLERS];
/** SP determiner primes (SOME-as-det shares the prime SOME's code; slot disambiguates). */
const DET_CANDIDATES = ['prime:THIS', 'prime:THE-SAME', 'prime:OTHER~ELSE~ANOTHER', 'prime:SOME'];

function dot(a: Float64Array, b: Float64Array): number {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i]! * b[i]!;
  return s;
}

function normalisedCopy(a: Float64Array): Float64Array | null {
  const n = Math.sqrt(dot(a, a));
  if (!(n > 0)) return null;
  const out = new Float64Array(a.length);
  for (let i = 0; i < a.length; i++) out[i] = a[i]! / n;
  return out;
}

type StructKind = 'sp' | 'clause' | 'quote' | 'concept' | 'temporal';

class Dec {
  readonly cb: CodebookBase;
  steps: DecodeStep[] = [];

  constructor(
    readonly params: EncoderParams,
    readonly concepts: ReadonlyMap<string, Float64Array> | undefined,
    readonly thetaAbs: number,
    readonly enc: InternalEncoder,
  ) {
    // Decode against the SAME codebook the encoder instance carries (exact
    // Hadamard by default; QuasiCodebook for the toy-native variant).
    this.cb = enc.cb;
  }

  step(path: string, decision: string, value: string, confidence: number): void {
    this.steps.push({ path, decision, value, confidence: Math.max(0, Math.min(1, confidence)) });
  }

  probe(u: Float64Array, slot: SlotName, filler: string): number {
    return dot(u, this.cb.boundAtom(slot, filler));
  }

  pickBest(u: Float64Array, slot: SlotName, fillers: readonly string[]): Pick {
    let best = -Infinity;
    let second = -Infinity;
    let name = fillers[0]!;
    for (const f of fillers) {
      const s = this.probe(u, slot, f);
      if (s > best) {
        second = best;
        best = s;
        name = f;
      } else if (s > second) second = s;
    }
    const margin = best > 0 ? Math.max(0, Math.min(1, (best - Math.max(second, 0)) / best)) : 0;
    return { name, score: best, margin };
  }

  /** Exact inverse of the encoder's cbind: conjugate unbinding, then unwhiten. */
  unbind(u: Float64Array, slot: SlotName): Float64Array {
    return this.cb.unspread(ifftToReal(spectrumMultiply(fftReal(u), this.cb.tagSpectrum(slot), true)));
  }

  /** Mirror of the encoder's cbind (whiten, then bind) — used for peeling. */
  bind(slot: SlotName, f: Float64Array): Float64Array {
    return ifftToReal(spectrumMultiply(fftReal(this.cb.spread(f)), this.cb.tagSpectrum(slot), false));
  }

  /** Subtract the projection of residual onto t; returns the coefficient. */
  peel(residual: Float64Array, t: Float64Array): number {
    const n2 = dot(t, t);
    if (!(n2 > 0)) return 0;
    const c = dot(residual, t) / n2;
    for (let i = 0; i < residual.length; i++) residual[i] = residual[i]! - c * t[i]!;
    return c;
  }

  reencodeFiller(f: Filler): Float64Array {
    return this.enc.encodeStructuredFiller(f);
  }

  // ----- structure signatures ------------------------------------------------

  spSignature(z: Float64Array): number {
    const head = this.pickBest(z, 'head', HEAD_CANDIDATES).score;
    const det = this.pickBest(z, 'det', DET_CANDIDATES).score;
    const bind = this.pickBest(z, 'bind', REF_FILLERS).score;
    return Math.max(head, det, bind);
  }

  clauseSignature(z: Float64Array): number {
    return Math.max(this.probe(z, 'ctype', 'tag:TAG:PRED'), this.probe(z, 'ctype', 'tag:TAG:OP'));
  }

  quoteSignature(z: Float64Array): number {
    return this.probe(z, 'ctype', 'tag:TAG:QUOTE');
  }

  temporalSignature(z: Float64Array): number {
    return Math.max(this.probe(z, 'op', 'op:AFTER'), this.probe(z, 'op', 'op:BEFORE'));
  }

  conceptSignature(z: Float64Array): number {
    if (this.concepts === undefined || this.concepts.size === 0) return -Infinity;
    let best = -Infinity;
    for (const v of this.concepts.values()) {
      const s = dot(z, v);
      if (s > best) best = s;
    }
    return best;
  }

  /** Concept signature at an SP node's head slot (for atomic-vs-concept competition). */
  conceptSignatureAt(residual: Float64Array): number {
    if (this.concepts === undefined || this.concepts.size === 0) return -Infinity;
    const zHead = normalisedCopy(this.unbind(residual, 'head'));
    return zHead === null ? -Infinity : this.conceptSignature(zHead);
  }

  conceptNN(z: Float64Array, path: string): { id: string; score: number; margin: number } | null {
    if (this.concepts === undefined || this.concepts.size === 0) return null;
    let best = -Infinity;
    let second = -Infinity;
    let bestId = '';
    for (const [id, v] of this.concepts) {
      const s = dot(z, v);
      if (s > best) {
        second = best;
        best = s;
        bestId = id;
      } else if (s > second) second = s;
    }
    const margin = best > 0 ? Math.max(0, Math.min(1, (best - Math.max(second, 0)) / best)) : 0;
    this.step(path, 'concept-nn', bestId, margin);
    return { id: bestId, score: best, margin };
  }

  // ----- recursive node decoders ---------------------------------------------

  /**
   * `assumePresent`: the caller knows (from the closed grammar) that a
   * structure MUST be here (required slot / operator arity), so the node's
   * own presence gate is replaced by best-effort argmax. Inner optional
   * content remains gated normally.
   */
  decodeSP(z: Float64Array, depth: number, path: string, assumePresent = false): SP | null {
    if (depth > CAPS.maxDepth) return null;
    const residual = Float64Array.from(z);
    const headAtomic = this.pickBest(residual, 'head', HEAD_CANDIDATES);
    let head: SPHead | null = null;
    /**
     * KIND/PART heads: the `of` target is resolved AFTER the sibling atomic
     * peels (det/quant/mods/bind). Bound atoms are exactly orthogonal, so the
     * deferral cannot change any atomic decision — but a structured of-target
     * is recovered by unbinding, and every unpeeled sibling atom's energy
     * turns into noise on that estimate (kernel-of-truth-sq2: the same
     * ordering effect at clause level caused the X2 depth-4x8 failure).
     */
    let pendingOfFrame: 'kindFrame' | 'partFrame' | null = null;
    let localScale = headAtomic.score;
    if (headAtomic.score >= this.thetaAbs || (assumePresent && headAtomic.score >= this.conceptSignatureAt(residual))) {
      const name = headAtomic.name;
      if (name.startsWith('ref:')) {
        head = { kind: 'refHead', index: Number(name.slice(4)) };
        this.peel(residual, this.cb.boundAtom('head', name));
      } else {
        const prime = name.slice(6);
        if (prime === 'KIND' || prime === 'PART') {
          pendingOfFrame = prime === 'KIND' ? 'kindFrame' : 'partFrame';
          this.peel(residual, this.cb.boundAtom('head', name));
        } else {
          head = { kind: 'primeHead', prime };
          this.peel(residual, this.cb.boundAtom('head', name));
        }
      }
      this.step(`${path}.head`, 'head', headAtomic.name, headAtomic.margin);
    } else {
      const zHead = normalisedCopy(this.unbind(residual, 'head'));
      const nn = zHead === null ? null : this.conceptNN(zHead, `${path}.head`);
      if (nn !== null && (nn.score >= this.thetaAbs || assumePresent)) {
        head = { kind: 'conceptHead', id: nn.id };
        localScale = this.pickBest(residual, 'det', DET_CANDIDATES).score; // fall back to sibling scale
        this.peel(residual, this.bind('head', this.concepts!.get(nn.id)!));
      } else if (assumePresent) {
        // Last resort: grammar guarantees a head; take the atomic argmax.
        head = headAtomic.name.startsWith('ref:')
          ? { kind: 'refHead', index: Number(headAtomic.name.slice(4)) }
          : { kind: 'primeHead', prime: headAtomic.name.slice(6) };
        this.peel(residual, this.cb.boundAtom('head', headAtomic.name));
        this.step(`${path}.head`, 'head-forced', headAtomic.name, 0);
      } else {
        this.step(`${path}.head`, 'no-head', '-', 0);
        return null;
      }
    }
    const thetaOpt = Math.max(this.thetaAbs, 0.4 * Math.max(localScale, this.thetaAbs));
    const det = this.pickBest(residual, 'det', DET_CANDIDATES);
    let detVal: SP['det'];
    if (det.score >= thetaOpt) {
      const prime = det.name.slice(6);
      detVal = (prime === 'SOME' ? 'SOME' : prime) as SP['det'];
      this.peel(residual, this.cb.boundAtom('det', det.name));
      this.step(`${path}.det`, 'det', det.name, det.margin);
    }
    const quant = this.pickBest(residual, 'quant', SP_QUANTIFIERS.map((q) => `prime:${q}`));
    let quantVal: SP['quant'];
    if (quant.score >= thetaOpt) {
      quantVal = quant.name.slice(6) as SP['quant'];
      this.peel(residual, this.cb.boundAtom('quant', quant.name));
      this.step(`${path}.quant`, 'quant', quant.name, quant.margin);
    }
    const mods: SPModifier[] = [];
    const modCandidates = [
      ...SP_MODS.map((m) => `prime:${m}`),
      ...INTENSIFIED_MODS.map((m) => `imod:${m}`),
    ];
    for (const cand of modCandidates) {
      const s = this.probe(residual, 'mod', cand);
      if (s >= thetaOpt) {
        if (cand.startsWith('prime:')) {
          mods.push({ mod: cand.slice(6) as SPModifier['mod'] });
        } else {
          const [intens, ...rest] = cand.slice(5).split('+');
          mods.push({ mod: rest.join('+') as SPModifier['mod'], intensifier: intens as 'VERY' | 'MORE' });
        }
        this.peel(residual, this.cb.boundAtom('mod', cand));
        this.step(`${path}.mods`, 'mod', cand, Math.min(1, Math.max(0, s / thetaOpt - 1)));
      }
    }
    const bind = this.pickBest(residual, 'bind', REF_FILLERS);
    let bindVal: number | undefined;
    if (bind.score >= thetaOpt) {
      bindVal = Number(bind.name.slice(4));
      this.peel(residual, this.cb.boundAtom('bind', bind.name));
      this.step(`${path}.bind`, 'bind', bind.name, bind.margin);
    }
    if (pendingOfFrame !== null) {
      // Deferred KIND/PART of-target (see note at the top of this method).
      let of: SP | { kind: 'concept'; id: string } | { kind: 'ref'; index: number } | null = null;
      const ofAtomic = this.pickBest(residual, 'of', REF_FILLERS);
      if (ofAtomic.score >= Math.max(this.thetaAbs, 0.4 * localScale)) {
        of = { kind: 'ref', index: Number(ofAtomic.name.slice(4)) };
        this.peel(residual, this.cb.boundAtom('of', ofAtomic.name));
        this.step(`${path}.head.of`, 'of-ref', ofAtomic.name, ofAtomic.margin);
      } else {
        const zOf = normalisedCopy(this.unbind(residual, 'of'));
        if (zOf !== null) {
          const spSig = this.spSignature(zOf);
          const ccSig = this.conceptSignature(zOf);
          if (ccSig >= Math.max(this.thetaAbs, spSig)) {
            const nn = this.conceptNN(zOf, `${path}.head.of`);
            if (nn !== null) of = { kind: 'concept', id: nn.id };
          } else if (spSig >= this.thetaAbs) {
            of = this.decodeSP(zOf, depth + 1, `${path}.head.of`);
          }
          if (of !== null) {
            // structured of-target (SP or concept): peel its bound contribution
            this.peel(residual, this.bind('of', this.reencodeFiller(of as Filler)));
          }
        }
      }
      if (of === null) {
        this.step(`${path}.head.of`, 'of-missing', '-', 0);
        return null; // a KIND/PART frame without its of-target cannot round-trip
      }
      head = { kind: pendingOfFrame, of };
    }
    if (head === null) return null; // unreachable: every accepting branch sets head or pendingOfFrame
    let restrictedBy: Clause | undefined;
    {
      const zR = normalisedCopy(this.unbind(residual, 'restrictedBy'));
      const rGate = Math.max(this.thetaAbs, 0.2 * Math.max(localScale, this.thetaAbs));
      if (zR !== null && this.clauseSignature(zR) >= rGate) {
        const c = this.decodeClause(zR, depth + 1, `${path}.restrictedBy`);
        if (c !== null) {
          restrictedBy = c;
          this.peel(residual, this.bind('restrictedBy', this.enc.encodeClause(c)));
        }
      }
    }
    return {
      kind: 'sp',
      ...(detVal !== undefined ? { det: detVal } : {}),
      ...(quantVal !== undefined ? { quant: quantVal } : {}),
      ...(mods.length > 0 ? { mods } : {}),
      head,
      ...(restrictedBy !== undefined ? { restrictedBy } : {}),
      ...(bindVal !== undefined ? { bind: bindVal } : {}),
    };
  }

  decodeTemporal(z: Float64Array, depth: number, path: string, assumePresent = false): Filler | null {
    const op = this.pickBest(z, 'op', ['op:AFTER', 'op:BEFORE']);
    if (op.score < this.thetaAbs && !assumePresent) return null;
    this.step(`${path}.op`, 'temporal-op', op.name, op.margin);
    const residual = Float64Array.from(z);
    this.peel(residual, this.cb.boundAtom('op', op.name));
    const opName = op.name.slice(3) as 'AFTER' | 'BEFORE';
    const atomic = this.pickBest(residual, 'arg0', ['prime:NOW', ...REF_FILLERS]);
    if (atomic.score >= Math.max(this.thetaAbs, 0.4 * op.score)) {
      this.step(`${path}.anchor`, 'anchor', atomic.name, atomic.margin);
      const anchor =
        atomic.name === 'prime:NOW'
          ? ({ kind: 'prime', prime: 'NOW' } as const)
          : ({ kind: 'ref', index: Number(atomic.name.slice(4)) } as const);
      return { kind: 'temporal', op: opName, anchor };
    }
    const zA = normalisedCopy(this.unbind(residual, 'arg0'));
    if (zA !== null && this.spSignature(zA) >= this.thetaAbs) {
      const sp = this.decodeSP(zA, depth + 1, `${path}.anchor`);
      if (sp !== null) return { kind: 'temporal', op: opName, anchor: sp };
    }
    this.step(`${path}.anchor`, 'anchor-missing', '-', 0);
    return null;
  }

  decodeQuote(z: Float64Array, depth: number, path: string, assumePresent = false): Filler | null {
    const sig = this.quoteSignature(z);
    if (sig < this.thetaAbs && !assumePresent) return null;
    const residual = Float64Array.from(z);
    this.peel(residual, this.cb.boundAtom('ctype', 'tag:TAG:QUOTE'));
    const clauses = this.decodeClauseList(residual, sig, depth, `${path}.clauses`);
    if (clauses.length === 0) return null;
    return { kind: 'quote', clauses };
  }

  /**
   * Decode a structured filler bound at `slot` of the node whose residual is
   * given; on success the child's contribution is peeled from the residual.
   */
  /**
   * `assumePresent`: presence guaranteed by the grammar (required slot /
   * operator arity) — no absolute gate; kinds are attempted in signature
   * order, best-effort.
   */
  decodeStructuredAt(
    residual: Float64Array,
    slot: SlotName,
    licensed: readonly StructKind[],
    depth: number,
    path: string,
    gate: number = this.thetaAbs,
    assumePresent = false,
  ): Filler | null {
    const zU = normalisedCopy(this.unbind(residual, slot));
    if (zU === null) return null;
    const scored = licensed
      .map((k) => ({
        kind: k,
        sig:
          k === 'sp' ? this.spSignature(zU)
          : k === 'clause' ? this.clauseSignature(zU)
          : k === 'quote' ? this.quoteSignature(zU)
          : k === 'temporal' ? this.temporalSignature(zU)
          : this.conceptSignature(zU),
      }))
      .sort((a, b) => b.sig - a.sig);
    for (const { kind, sig } of scored) {
      if (!assumePresent && sig < Math.max(this.thetaAbs, gate)) break;
      if (sig === -Infinity) break; // unavailable kind (no concept lexicon)
      let out: Filler | null = null;
      if (kind === 'sp') out = this.decodeSP(zU, depth + 1, path, assumePresent);
      else if (kind === 'clause') {
        const c = this.decodeClause(zU, depth + 1, path, assumePresent);
        out = c === null ? null : { kind: 'clause', clause: c };
      } else if (kind === 'quote') out = this.decodeQuote(zU, depth + 1, path, assumePresent);
      else if (kind === 'temporal') out = this.decodeTemporal(zU, depth + 1, path, assumePresent);
      else {
        const nn = this.conceptNN(zU, path);
        if (nn !== null && (nn.score >= this.thetaAbs || assumePresent)) out = { kind: 'concept', id: nn.id };
      }
      if (out !== null) {
        const rec = out.kind === 'clause' ? this.enc.encodeClause(out.clause) : this.reencodeFiller(out);
        this.peel(residual, this.bind(slot, rec));
        return out;
      }
    }
    return null;
  }

  /** Candidate sets licensed at a role slot; null = nothing licensed (unknown adjunct). */
  private roleCandidateSets(
    role: Role,
    kind: SlotFillerKind | 'adjunct',
  ): { atomicCands: readonly string[]; structured: readonly StructKind[] } | null {
    let atomicCands: readonly string[] = [];
    let structured: readonly StructKind[] = [];
    switch (kind) {
      case 'entity':
        atomicCands = ['prime:I', 'prime:YOU', ...REF_FILLERS];
        structured = ['sp', 'concept'];
        break;
      case 'clause':
        structured = ['clause'];
        break;
      case 'quote':
        structured = ['quote'];
        break;
      case 'attributeGoodBad':
        atomicCands = ['prime:GOOD', 'prime:BAD'];
        break;
      case 'attributeSpec':
        structured = ['sp', 'concept'];
        break;
      case 'clauseRefOrQuote':
        atomicCands = REF_FILLERS;
        structured = ['quote', 'clause'];
        break;
      case 'entityOrClause':
        atomicCands = ['prime:I', 'prime:YOU', ...REF_FILLERS];
        structured = ['sp', 'concept', 'clause'];
        break;
      case 'firstPerson':
        atomicCands = ['prime:I'];
        break;
      case 'adjunct':
        switch (role) {
          case 'time':
            atomicCands = ['prime:NOW', ...REF_FILLERS];
            structured = ['sp', 'temporal'];
            break;
          case 'duration':
            atomicCands = DURATION_FILLERS.map((d) => `prime:${d}`);
            structured = ['sp'];
            break;
          case 'place':
            atomicCands = ['prime:HERE', ...REF_FILLERS];
            structured = ['sp'];
            break;
          case 'manner':
            atomicCands = [...PRIME_NAMES.map((p) => `prime:${p}`), ...REF_FILLERS];
            structured = ['sp', 'concept'];
            break;
          default:
            return null;
        }
        break;
    }
    return { atomicCands, structured };
  }

  /**
   * Decode one role slot. `phase` implements the two-phase clause sweep
   * (kernel-of-truth-sq2 fix — see decodeClause):
   *  - 'atomic': commit an above-gate atomic filler, otherwise decide nothing
   *    (no peel, no step) — structured decoding is deferred so that EVERY
   *    committed atom is already out of the residual first.
   *  - 'full': the remaining work — atomic gate re-check (structured peels by
   *    earlier phase-2 roles shift scores slightly), structured decode, and
   *    the required-slot fallbacks.
   */
  decodeRole(
    residual: Float64Array,
    role: Role,
    kind: SlotFillerKind | 'adjunct',
    required: boolean,
    localScale: number,
    depth: number,
    path: string,
    phase: 'atomic' | 'full' = 'full',
  ): Filler | null {
    const sets = this.roleCandidateSets(role, kind);
    if (sets === null) return null;
    const { atomicCands, structured } = sets;
    const thetaOpt = Math.max(this.thetaAbs, 0.4 * localScale);
    const gate = required ? this.thetaAbs : thetaOpt;
    const toAtomic = (name: string): Filler =>
      name.startsWith('ref:')
        ? { kind: 'ref', index: Number(name.slice(4)) }
        : { kind: 'prime', prime: name.slice(6) };
    const atomicPick = atomicCands.length > 0 ? this.pickBest(residual, role, atomicCands) : null;
    if (atomicPick !== null && atomicPick.score >= gate) {
      this.peel(residual, this.cb.boundAtom(role, atomicPick.name));
      this.step(`${path}.${role}`, 'atomic', atomicPick.name, atomicPick.margin);
      return toAtomic(atomicPick.name);
    }
    if (phase === 'atomic') return null;
    if (structured.length > 0) {
      // Optional slots gate structured presence relative to the local signal
      // scale (phantom-SP protection). REQUIRED slots are grammar-guaranteed
      // present, so they decode by best-effort relative competition instead
      // of an absolute floor (the floor would turn deep-but-real content into
      // a certain failure).
      if (required && atomicPick !== null) {
        // Matched-filter competition ON A COMMON SCALE first: unbinding is
        // unitary, so structure signatures on the RAW (unnormalised) unbound
        // estimate are directly comparable with the atomic probe scores.
        // Without this, `assumePresent` fabricates a phantom SP even when the
        // sub-gate atomic argmax is the stronger hypothesis (the X2 depth-4x8
        // boundary failure, kernel-of-truth-sq2).
        const zRaw = this.unbind(residual, role);
        let rawSig = -Infinity;
        for (const k of structured) {
          const s =
            k === 'sp' ? this.spSignature(zRaw)
            : k === 'clause' ? this.clauseSignature(zRaw)
            : k === 'quote' ? this.quoteSignature(zRaw)
            : k === 'temporal' ? this.temporalSignature(zRaw)
            : this.conceptSignature(zRaw);
          if (s > rawSig) rawSig = s;
        }
        if (atomicPick.score >= rawSig) {
          this.peel(residual, this.cb.boundAtom(role, atomicPick.name));
          this.step(`${path}.${role}`, 'atomic-forced', atomicPick.name, 0);
          return toAtomic(atomicPick.name);
        }
      }
      const structGate = required ? this.thetaAbs : Math.max(this.thetaAbs, 0.2 * localScale);
      const f = this.decodeStructuredAt(residual, role, structured, depth, `${path}.${role}`, structGate, required);
      if (f !== null) return f;
    }
    if (required && atomicPick !== null) {
      // Last resort for a required slot: sub-threshold atomic argmax.
      this.peel(residual, this.cb.boundAtom(role, atomicPick.name));
      this.step(`${path}.${role}`, 'atomic-forced', atomicPick.name, 0);
      return toAtomic(atomicPick.name);
    }
    return null;
  }

  decodeClause(u: Float64Array, depth: number, path: string, assumePresent = false): Clause | null {
    if (depth > CAPS.maxDepth) return null;
    const tp = this.probe(u, 'ctype', 'tag:TAG:PRED');
    const to = this.probe(u, 'ctype', 'tag:TAG:OP');
    if (Math.max(tp, to) < this.thetaAbs && !assumePresent) {
      this.step(path, 'no-clause', '-', 0);
      return null;
    }
    const residual = Float64Array.from(u);
    if (tp >= to) {
      this.peel(residual, this.cb.boundAtom('ctype', 'tag:TAG:PRED'));
      const pred = this.pickBest(residual, 'pred', PRED_NAMES.map((p) => `prime:${p}`));
      this.step(path, 'pred', pred.name, pred.margin);
      this.peel(residual, this.cb.boundAtom('pred', pred.name));
      const predName = pred.name.slice(6);
      const frame = FRAME_BY_PRED.get(predName);
      if (frame === undefined) return null;
      const localScale = (tp + pred.score) / 2;
      const roles: Partial<Record<Role, Filler>> = {};
      // Two-phase role sweep (kernel-of-truth-sq2). Phase 1 commits every
      // above-gate ATOMIC filler across all roles before any structured
      // unbinding. Bound atoms are exactly orthogonal (Hadamard TPR), so the
      // reordering cannot change any atomic decision — but it keeps committed
      // atoms' energy out of every structured child estimate. Previously the
      // adjunct atoms (decoded last in ROLES order) stayed in the residual
      // while complement/quote were unbound, and that noise compounded down
      // deep chains (X2 depth-4x8: corr of a depth-4 clause estimate fell
      // 0.60 -> 0.15, pushing a true filler under the presence gate).
      const pending: { role: Role; kind: SlotFillerKind | 'adjunct'; required: boolean }[] = [];
      for (const role of ROLES) {
        const slot = frame.slots.find((sl) => sl.role === role);
        const isAdjunct = (ADJUNCT_ROLES as readonly string[]).includes(role);
        if (slot === undefined && !isAdjunct) continue;
        const kind = slot?.kind ?? 'adjunct';
        const required = slot?.required ?? false;
        const f = this.decodeRole(residual, role, kind, required, localScale, depth, path, 'atomic');
        if (f !== null) roles[role] = f;
        else pending.push({ role, kind, required });
      }
      // Phase 2: structured / sub-gate roles against the atom-free residual.
      for (const p of pending) {
        const f = this.decodeRole(residual, p.role, p.kind, p.required, localScale, depth, path, 'full');
        if (f !== null) roles[p.role] = f;
      }
      return { type: 'pred', pred: predName, roles };
    }
    this.peel(residual, this.cb.boundAtom('ctype', 'tag:TAG:OP'));
    const op = this.pickBest(residual, 'op', OPERATORS.map((o) => `op:${o}`));
    this.step(path, 'op', op.name, op.margin);
    this.peel(residual, this.cb.boundAtom('op', op.name));
    const opName = op.name.slice(3) as Operator;
    const cls = OPERATOR_CLASS[opName];
    const args: OpArg[] = [];
    const clauseArg = (slot: 'arg0' | 'arg1', p: string): boolean => {
      // Operator arity makes the clause argument grammar-guaranteed.
      const f = this.decodeStructuredAt(residual, slot, ['clause'], depth, p, this.thetaAbs, true);
      if (f === null || f.kind !== 'clause') return false;
      args.push(f.clause);
      return true;
    };
    switch (cls) {
      case 'clause1':
        if (!clauseArg('arg0', `${path}.args[0]`)) return null;
        break;
      case 'clause2':
        if (!clauseArg('arg0', `${path}.args[0]`)) return null;
        if (!clauseArg('arg1', `${path}.args[1]`)) return null;
        break;
      case 'compare2': {
        for (const [i, slot] of (['arg0', 'arg1'] as const).entries()) {
          const p = `${path}.args[${i}]`;
          const atomic = this.pickBest(residual, slot, REF_FILLERS);
          if (atomic.score >= Math.max(this.thetaAbs, 0.4 * op.score)) {
            args.push({ kind: 'ref', index: Number(atomic.name.slice(4)) });
            this.peel(residual, this.cb.boundAtom(slot, atomic.name));
            this.step(p, 'atomic', atomic.name, atomic.margin);
            continue;
          }
          const f = this.decodeStructuredAt(residual, slot, ['sp', 'clause', 'concept'], depth, p, this.thetaAbs, true);
          if (f === null) return null;
          args.push(f.kind === 'clause' ? f.clause : (f as OpArg));
        }
        break;
      }
      case 'temporal2': {
        const atomic = this.pickBest(residual, 'arg0', ['prime:NOW', ...REF_FILLERS]);
        if (atomic.score >= Math.max(this.thetaAbs, 0.4 * op.score)) {
          args.push(
            atomic.name === 'prime:NOW'
              ? { kind: 'prime', prime: 'NOW' }
              : { kind: 'ref', index: Number(atomic.name.slice(4)) },
          );
          this.peel(residual, this.cb.boundAtom('arg0', atomic.name));
          this.step(`${path}.args[0]`, 'anchor', atomic.name, atomic.margin);
        } else {
          const f = this.decodeStructuredAt(residual, 'arg0', ['sp'], depth, `${path}.args[0]`);
          if (f !== null) {
            args.push(f as OpArg);
          } else {
            // Anchor is required by the arity: sub-threshold atomic argmax.
            args.push(
              atomic.name === 'prime:NOW'
                ? { kind: 'prime', prime: 'NOW' }
                : { kind: 'ref', index: Number(atomic.name.slice(4)) },
            );
            this.peel(residual, this.cb.boundAtom('arg0', atomic.name));
            this.step(`${path}.args[0]`, 'anchor-forced', atomic.name, 0);
          }
        }
        if (!clauseArg('arg1', `${path}.args[1]`)) return null;
        break;
      }
      case 'overMod1': {
        // Required by arity: argmax over the closed candidate set.
        const m = this.pickBest(residual, 'arg0', SP_MODS.map((x) => `prime:${x}`));
        args.push({ kind: 'prime', prime: m.name.slice(6) });
        this.peel(residual, this.cb.boundAtom('arg0', m.name));
        this.step(`${path}.args[0]`, 'mod', m.name, m.margin);
        break;
      }
      case 'overModOrQuant1': {
        const cands = [...SP_MODS, ...SP_QUANTIFIERS].map((x) => `prime:${x}`);
        const m = this.pickBest(residual, 'arg0', cands);
        args.push({ kind: 'prime', prime: m.name.slice(6) });
        this.peel(residual, this.cb.boundAtom('arg0', m.name));
        this.step(`${path}.args[0]`, 'modOrQuant', m.name, m.margin);
        break;
      }
    }
    return { type: 'op', op: opName, args };
  }

  /** Decode an ordered clause list from a node residual (quote bodies). */
  decodeClauseList(residual: Float64Array, localScale: number, depth: number, path: string): Clause[] {
    const clauses: Clause[] = [];
    const recons: Float64Array[] = [];
    const coeffs: number[] = [];
    for (let i = 0; i < CAPS.maxClauses; i++) {
      const u = applyPermutation(this.cb.clausePermInv(i), residual);
      if (this.clauseSignature(u) < Math.max(this.thetaAbs, 0.2 * localScale)) break;
      // Presence is gated at the parent's scale; the recursive decode then
      // works on the normalised estimate so its own thresholds see unit scale.
      const uU = normalisedCopy(u);
      const c = uU === null ? null : this.decodeClause(uU, depth + 1, `${path}[${i}]`);
      if (c === null) break;
      clauses.push(c);
      const rec = applyPermutation(this.cb.clausePerm(i), this.enc.encodeClause(c));
      recons.push(rec);
      coeffs.push(this.peel(residual, rec));
    }
    // One local refinement pass (restore-self / peel-siblings), mirroring the
    // top-level global refinement: clause i was first decoded with clauses
    // i+1.. still in the residual as noise; re-decode each against the
    // residual of all the others (kernel-of-truth-sq2 — the sibling clause
    // of a depth-4 quote body cost ~35% of the deep clause's SNR in the X2
    // depth-4x8 boundary case).
    if (clauses.length > 1) {
      for (let i = 0; i < clauses.length; i++) {
        const restored = Float64Array.from(residual);
        const rec = recons[i]!;
        const c0 = coeffs[i]!;
        for (let j = 0; j < restored.length; j++) restored[j] = restored[j]! + c0 * rec[j]!;
        const uU = normalisedCopy(applyPermutation(this.cb.clausePermInv(i), restored));
        if (uU === null) continue;
        // Steps bookkeeping: a successful re-decode supersedes the first-pass
        // steps under this clause's path; a failed one leaves them untouched.
        const saved = this.steps;
        this.steps = [];
        const c = this.decodeClause(uU, depth + 1, `${path}[${i}]`);
        if (c === null) {
          this.steps = saved; // keep the first-pass decode (residual untouched)
          continue;
        }
        const pfx = `${path}[${i}]`;
        this.steps = [
          ...saved.filter((s) => s.path !== pfx && !s.path.startsWith(`${pfx}.`) && !s.path.startsWith(`${pfx}[`)),
          ...this.steps,
        ];
        clauses[i] = c;
        residual.set(restored);
        const rec2 = applyPermutation(this.cb.clausePerm(i), this.enc.encodeClause(c));
        recons[i] = rec2;
        coeffs[i] = this.peel(residual, rec2);
      }
    }
    return clauses;
  }

  // ----- residual completion (kernel-of-truth-0kn) ---------------------------

  /** Run `fn` with step recording suspended (candidate probing must not pollute the trace). */
  quiet<T>(fn: () => T): T {
    const saved = this.steps;
    this.steps = [];
    try {
      return fn();
    } finally {
      this.steps = saved;
    }
  }

  /**
   * Best-effort decode of ONE structured candidate from a normalised residual
   * estimate. Unlike decodeStructuredAt this never peels (the estimate is a
   * probe of the global residual, not a working buffer) and never assumes
   * presence: the residual at a truly-empty site is amplified white noise, on
   * which every signature stays under the 5-sigma floor.
   */
  private decodeStructuredCandidate(
    zn: Float64Array,
    licensed: readonly StructKind[],
    depth: number,
    path: string,
  ): Filler | null {
    let bestKind: StructKind | null = null;
    let bestSig = -Infinity;
    for (const k of licensed) {
      const s =
        k === 'sp' ? this.spSignature(zn)
        : k === 'clause' ? this.clauseSignature(zn)
        : k === 'quote' ? this.quoteSignature(zn)
        : k === 'temporal' ? this.temporalSignature(zn)
        : this.conceptSignature(zn);
      if (s > bestSig) {
        bestSig = s;
        bestKind = k;
      }
    }
    if (bestKind === null || bestSig < this.thetaAbs) return null;
    const kind = bestKind;
    return this.quiet(() => {
      if (kind === 'sp') return this.decodeSP(zn, depth + 1, path);
      if (kind === 'clause') {
        const c = this.decodeClause(zn, depth + 1, path);
        return c === null ? null : ({ kind: 'clause', clause: c } as Filler);
      }
      if (kind === 'quote') return this.decodeQuote(zn, depth + 1, path);
      if (kind === 'temporal') return this.decodeTemporal(zn, depth + 1, path);
      const nn = this.conceptNN(zn, path);
      return nn !== null && nn.score >= this.thetaAbs ? ({ kind: 'concept', id: nn.id } as Filler) : null;
    });
  }

  /**
   * Walk a DECODED clause alongside the matching estimate of the global
   * residual, generating insertion candidates for every EMPTY optional site
   * (unfilled optional roles/adjuncts; missing SP det/quant/mods/bind/
   * restrictedBy; missing trailing quote clauses). Candidates are only
   * GENERATED here; acceptance is decodeExplication's global matched-filter
   * test. `z` is the unnormalised residual estimate at this clause node;
   * `rebuild` lifts an edited node back to its top-level clause.
   */
  collectClauseCompletions(
    c: Clause,
    z: Float64Array,
    path: string,
    rebuild: (c2: Clause) => Clause,
    out: { clause: Clause; sitePath: string; desc: string }[],
    depth: number,
  ): void {
    if (depth > CAPS.maxDepth) return;
    if (c.type === 'pred') {
      const frame = FRAME_BY_PRED.get(c.pred);
      if (frame === undefined) return;
      for (const role of ROLES) {
        const slot = frame.slots.find((sl) => sl.role === role);
        const isAdjunct = (ADJUNCT_ROLES as readonly string[]).includes(role);
        if (slot === undefined && !isAdjunct) continue;
        const f = c.roles[role];
        const rolePath = `${path}.roles.${role}`;
        const zRole = this.unbind(z, role);
        const put = (f2: Filler): Clause => rebuild({ ...c, roles: { ...c.roles, [role]: f2 } });
        if (f !== undefined) {
          this.collectFillerCompletions(f, zRole, rolePath, put, out, depth);
          continue;
        }
        const sets = this.roleCandidateSets(role, slot?.kind ?? 'adjunct');
        if (sets === null) continue;
        const zn = normalisedCopy(zRole);
        if (zn === null) continue;
        if (sets.atomicCands.length > 0) {
          const a = this.pickBest(zn, role, sets.atomicCands);
          if (a.score >= this.thetaAbs) {
            const f2: Filler = a.name.startsWith('ref:')
              ? { kind: 'ref', index: Number(a.name.slice(4)) }
              : { kind: 'prime', prime: a.name.slice(6) };
            out.push({ clause: put(f2), sitePath: rolePath, desc: a.name });
          }
        }
        if (sets.structured.length > 0) {
          const fs = this.decodeStructuredCandidate(zn, sets.structured, depth, rolePath);
          if (fs !== null) out.push({ clause: put(fs), sitePath: rolePath, desc: fs.kind });
        }
      }
      return;
    }
    if (OPERATOR_CLASS[c.op] === undefined) return;
    for (const [i, arg] of c.args.entries()) {
      const slot: SlotName = i === 0 ? 'arg0' : 'arg1';
      const argPath = `${path}.args[${i}]`;
      const putArg = (a2: OpArg): Clause => rebuild({ ...c, args: c.args.map((a, j) => (j === i ? a2 : a)) });
      if ('type' in arg) {
        this.collectClauseCompletions(arg, this.unbind(z, slot), argPath, (c2) => putArg(c2), out, depth + 1);
      } else {
        this.collectFillerCompletions(arg, this.unbind(z, slot), argPath, (f2) => putArg(f2 as OpArg), out, depth);
      }
    }
  }

  collectFillerCompletions(
    f: Filler,
    z: Float64Array,
    path: string,
    rebuild: (f2: Filler) => Clause,
    out: { clause: Clause; sitePath: string; desc: string }[],
    depth: number,
  ): void {
    if (depth > CAPS.maxDepth) return;
    switch (f.kind) {
      case 'sp': {
        const zn = normalisedCopy(z);
        if (zn === null) return;
        if (f.det === undefined) {
          const det = this.pickBest(zn, 'det', DET_CANDIDATES);
          if (det.score >= this.thetaAbs) {
            const prime = det.name.slice(6);
            const detVal = (prime === 'SOME' ? 'SOME' : prime) as NonNullable<SP['det']>;
            out.push({ clause: rebuild({ ...f, det: detVal }), sitePath: `${path}.det`, desc: det.name });
          }
        }
        if (f.quant === undefined) {
          const q = this.pickBest(zn, 'quant', SP_QUANTIFIERS.map((x) => `prime:${x}`));
          if (q.score >= this.thetaAbs) {
            out.push({
              clause: rebuild({ ...f, quant: q.name.slice(6) as NonNullable<SP['quant']> }),
              sitePath: `${path}.quant`,
              desc: q.name,
            });
          }
        }
        if (f.bind === undefined) {
          const b = this.pickBest(zn, 'bind', REF_FILLERS);
          if (b.score >= this.thetaAbs) {
            out.push({
              clause: rebuild({ ...f, bind: Number(b.name.slice(4)) }),
              sitePath: `${path}.bind`,
              desc: b.name,
            });
          }
        }
        const have = new Set(
          (f.mods ?? []).map((m) => (m.intensifier === undefined ? `prime:${m.mod}` : `imod:${m.intensifier}+${m.mod}`)),
        );
        let bestMod: { name: string; score: number } | null = null;
        for (const cand of [...SP_MODS.map((m) => `prime:${m}`), ...INTENSIFIED_MODS.map((m) => `imod:${m}`)]) {
          if (have.has(cand)) continue;
          const s = this.probe(zn, 'mod', cand);
          if (s >= this.thetaAbs && (bestMod === null || s > bestMod.score)) bestMod = { name: cand, score: s };
        }
        if (bestMod !== null) {
          let m: SPModifier;
          if (bestMod.name.startsWith('prime:')) {
            m = { mod: bestMod.name.slice(6) as SPModifier['mod'] };
          } else {
            const [intens, ...rest] = bestMod.name.slice(5).split('+');
            m = { mod: rest.join('+') as SPModifier['mod'], intensifier: intens as 'VERY' | 'MORE' };
          }
          out.push({
            clause: rebuild({ ...f, mods: [...(f.mods ?? []), m] }),
            sitePath: `${path}.mods`,
            desc: bestMod.name,
          });
        }
        if (f.restrictedBy === undefined) {
          const zr = normalisedCopy(this.unbind(z, 'restrictedBy'));
          if (zr !== null && this.clauseSignature(zr) >= this.thetaAbs) {
            const c2 = this.quiet(() => this.decodeClause(zr, depth + 1, `${path}.restrictedBy`));
            if (c2 !== null) {
              out.push({ clause: rebuild({ ...f, restrictedBy: c2 }), sitePath: `${path}.restrictedBy`, desc: 'clause' });
            }
          }
        } else {
          this.collectClauseCompletions(
            f.restrictedBy,
            this.unbind(z, 'restrictedBy'),
            `${path}.restrictedBy`,
            (c2) => rebuild({ ...f, restrictedBy: c2 }),
            out,
            depth + 1,
          );
        }
        const h = f.head;
        if ((h.kind === 'kindFrame' || h.kind === 'partFrame') && h.of.kind === 'sp') {
          this.collectFillerCompletions(
            h.of,
            this.unbind(z, 'of'),
            `${path}.head.of`,
            (f2) => rebuild({ ...f, head: { ...h, of: f2 as SP } }),
            out,
            depth + 1,
          );
        }
        return;
      }
      case 'quote': {
        for (const [j, qc] of f.clauses.entries()) {
          this.collectClauseCompletions(
            qc,
            applyPermutation(this.cb.clausePermInv(j), z),
            `${path}.clauses[${j}]`,
            (c2) => rebuild({ ...f, clauses: f.clauses.map((x, k) => (k === j ? c2 : x)) }),
            out,
            depth + 1,
          );
        }
        const j = f.clauses.length;
        if (j < CAPS.maxClauses) {
          const zj = normalisedCopy(applyPermutation(this.cb.clausePermInv(j), z));
          if (zj !== null && this.clauseSignature(zj) >= this.thetaAbs) {
            const c2 = this.quiet(() => this.decodeClause(zj, depth + 1, `${path}.clauses[${j}]`));
            if (c2 !== null) {
              out.push({ clause: rebuild({ ...f, clauses: [...f.clauses, c2] }), sitePath: `${path}.clauses[${j}]`, desc: 'clause' });
            }
          }
        }
        return;
      }
      case 'temporal': {
        if (f.anchor.kind === 'sp') {
          this.collectFillerCompletions(
            f.anchor,
            this.unbind(z, 'arg0'),
            `${path}.anchor`,
            (f2) => rebuild({ ...f, anchor: f2 as SP }),
            out,
            depth + 1,
          );
        }
        return;
      }
      case 'clause':
        // Clause fillers are bound directly at the role tag: z IS the clause estimate.
        this.collectClauseCompletions(f.clause, z, `${path}.clause`, (c2) => rebuild({ kind: 'clause', clause: c2 }), out, depth + 1);
        return;
      default:
        return; // atomic fillers (prime/ref/concept) carry no optional sites
    }
  }
}

// ---------------------------------------------------------------------------
// Entry point with global refinement
// ---------------------------------------------------------------------------

interface PartialDecode {
  frame: ExplicationFrame;
  referents: ReferentDecl[];
  clauses: (Clause | null)[];
}

export function decodeExplication(v: Float64Array, opts?: DecodeOptions): DecodeResult {
  const params = resolveParams(opts?.params);
  return decodeWithEncoder(v, params, new InternalEncoder(params, opts?.concepts), opts);
}

/**
 * INTERNAL (used by the toy-native variant encoderQ.ts): decode against the
 * codebook carried by `enc`. `params` must already be validated by the
 * caller's resolve function and must match `enc.params`.
 */
export function decodeWithEncoder(
  v: Float64Array,
  params: EncoderParams,
  enc: InternalEncoder,
  opts?: DecodeOptions,
): DecodeResult {
  if (v.length !== params.D) {
    throw new Error(`ERR_DIMENSION: vector has D=${v.length}, decoder params D=${params.D}`);
  }
  const thetaAbs = opts?.thetaAbs ?? 5 / Math.sqrt(params.D);
  const refine = opts?.refineIterations ?? 3;
  const cb = enc.cb;

  let prior: PartialDecode | null = null;
  let dec = new Dec(params, opts?.concepts, thetaAbs, enc);
  let lastJson = '';

  for (let pass = 0; pass <= refine; pass++) {
    dec = new Dec(params, opts?.concepts, thetaAbs, enc);

    // Reconstructions of the prior pass's elements, keyed for restore/peel.
    const recons = new Map<string, Float64Array>();
    if (prior !== null) {
      recons.set('frame', cb.boundAtom('frame', `frame:${prior.frame}`));
      for (const r of prior.referents) {
        recons.set(
          `ref:${r.index}`,
          applyPermutation(cb.refdeclPerm(r.index), cb.boundAtom('refdecl', `refkind:${r.refKind}`)),
        );
      }
      for (const [i, c] of prior.clauses.entries()) {
        if (c !== null) recons.set(`clause:${i}`, applyPermutation(cb.clausePerm(i), enc.encodeClause(c)));
      }
    }
    // Global residual: v minus every prior reconstruction (projection coeffs kept).
    const residual = Float64Array.from(v);
    const coeff = new Map<string, number>();
    for (const [key, rec] of recons) coeff.set(key, dec.peel(residual, rec));

    /** Residual with element `key`'s own prior contribution restored. */
    const restore = (key: string): Float64Array => {
      const rec = recons.get(key);
      const u = Float64Array.from(residual);
      if (rec !== undefined) {
        const c = coeff.get(key)!;
        for (let i = 0; i < u.length; i++) u[i] = u[i]! + c * rec[i]!;
      }
      return u;
    };
    /** After re-decoding element `key`, replace its contribution in the residual. */
    const commit = (key: string, restored: Float64Array, newRec: Float64Array | null): void => {
      residual.set(restored);
      if (newRec !== null) dec.peel(residual, newRec);
    };

    // --- frame (always present) ---
    let u = restore('frame');
    const framePick = dec.pickBest(u, 'frame', EXPLICATION_FRAMES.map((f) => `frame:${f}`));
    const frame = framePick.name.slice(6) as ExplicationFrame;
    dec.step('$.frame', 'frame', framePick.name, framePick.margin);
    commit('frame', u, cb.boundAtom('frame', framePick.name));

    // --- referent declarations (per-index deterministic permutation) ---
    const referents: ReferentDecl[] = [];
    for (let n = 1; n <= CAPS.maxReferents; n++) {
      u = restore(`ref:${n}`);
      const un = applyPermutation(cb.refdeclPermInv(n), u);
      const kindPick = dec.pickBest(un, 'refdecl', REF_KINDS.map((k) => `refkind:${k}`));
      if (kindPick.score >= Math.max(thetaAbs, 0.4 * framePick.score)) {
        const refKind = kindPick.name.slice(8) as RefKind;
        referents.push({ index: n, refKind });
        dec.step(`$.referents[${n}]`, 'refkind', kindPick.name, kindPick.margin);
        commit(
          `ref:${n}`,
          u,
          applyPermutation(cb.refdeclPerm(n), cb.boundAtom('refdecl', `refkind:${refKind}`)),
        );
      } else {
        commit(`ref:${n}`, u, null);
      }
    }

    // --- ordered clauses ---
    const clauses: (Clause | null)[] = [];
    let sawAbsent = false;
    for (let i = 0; i < CAPS.maxClauses; i++) {
      const key = `clause:${i}`;
      u = restore(key);
      const ui = applyPermutation(cb.clausePermInv(i), u);
      const sig = dec.clauseSignature(ui);
      const present = sig >= Math.max(thetaAbs, 0.2 * framePick.score);
      if (!present) {
        commit(key, u, null);
        // Dense list: past the prior length, the first absence terminates the scan.
        if (i >= (prior?.clauses.length ?? 0)) {
          sawAbsent = true;
          break;
        }
        clauses.push(null);
        continue;
      }
      // Presence was gated at v's scale; decode on the normalised estimate so
      // the clause decoder's thresholds see unit scale (deep-child recovery
      // after refinement peeling depends on this).
      const uiU = normalisedCopy(ui);
      const c = uiU === null ? null : dec.decodeClause(uiU, 1, `$.clauses[${i}]`);
      clauses.push(c);
      commit(key, u, c === null ? null : applyPermutation(cb.clausePerm(i), enc.encodeClause(c)));
    }
    void sawAbsent;
    while (clauses.length > 0 && clauses[clauses.length - 1] === null) clauses.pop();

    prior = { frame, referents, clauses };
    const json = canonicalJson(prior as unknown as Record<string, unknown>);
    if (json === lastJson) break; // converged
    lastJson = json;
  }

  // --- residual completion (kernel-of-truth-0kn) ---
  // Deep OPTIONAL content can be undetectable in-decode: under quote>op
  // nesting the authored-corpus emotion trio's true SPs scored ~0.6x the
  // 5-sigma presence floor while PURE-NOISE slots at the same depth scored
  // higher — no local gate can separate them. But the encoder is
  // deterministic: everything the converged decode DID recover re-encodes
  // exactly, so after subtracting it from v the missed content is nearly the
  // only thing left in the global residual (measured 6-30x above the noise
  // floor at the missed sites for the corpus trio). Probe every empty
  // optional site of the decoded AST against that residual; accept the best
  // candidate edit only if the RE-ENCODED edited clause explains the
  // restored residual strictly better than the original — a global
  // matched-filter competition on exact reconstructions, which a phantom
  // cannot win because its predicted contribution is absent from v.
  if (prior !== null) {
    const maxEdits = 16;
    for (let editPass = 0; editPass < maxEdits; editPass++) {
      const p = prior;
      const clauseRecs = p.clauses.map((c, i) =>
        c === null ? null : applyPermutation(cb.clausePerm(i), enc.encodeClause(c)),
      );
      const residual = Float64Array.from(v);
      dec.peel(residual, cb.boundAtom('frame', `frame:${p.frame}`));
      for (const r of p.referents) {
        dec.peel(residual, applyPermutation(cb.refdeclPerm(r.index), cb.boundAtom('refdecl', `refkind:${r.refKind}`)));
      }
      const coeffs = clauseRecs.map((rec) => (rec === null ? 0 : dec.peel(residual, rec)));
      let res2 = 0;
      for (let k = 0; k < residual.length; k++) res2 += residual[k]! * residual[k]!;
      if (res2 <= 1e-10) break; // decode already explains v (exact up to float noise)
      const cands: { clauseIndex: number; clause: Clause; sitePath: string; desc: string }[] = [];
      for (const [i, c] of p.clauses.entries()) {
        if (c === null) continue;
        const zi = applyPermutation(cb.clausePermInv(i), residual);
        const local: { clause: Clause; sitePath: string; desc: string }[] = [];
        dec.collectClauseCompletions(c, zi, `$.clauses[${i}]`, (c2) => c2, local, 1);
        for (const cand of local) cands.push({ clauseIndex: i, ...cand });
      }
      if (cands.length === 0) break;
      let best: { cand: (typeof cands)[number]; errOld: number; errNew: number } | null = null;
      for (const cand of cands) {
        const rec = clauseRecs[cand.clauseIndex]!;
        // Restore clause i's own contribution: ri = residual + c0 * rec.
        const ri = Float64Array.from(residual);
        const c0 = coeffs[cand.clauseIndex]!;
        for (let k = 0; k < ri.length; k++) ri[k] = ri[k]! + c0 * rec[k]!;
        const errOf = (t: Float64Array): number => {
          const n2 = dot(t, t);
          const cf = n2 > 0 ? dot(ri, t) / n2 : 0;
          let e = 0;
          for (let k = 0; k < ri.length; k++) {
            const d = ri[k]! - cf * t[k]!;
            e += d * d;
          }
          return e;
        };
        const errOld = errOf(rec);
        const errNew = errOf(applyPermutation(cb.clausePerm(cand.clauseIndex), enc.encodeClause(cand.clause)));
        if (best === null || errOld - errNew > best.errOld - best.errNew) best = { cand, errOld, errNew };
      }
      // Accept only a decisive improvement (>=1% of the clause's residual
      // error, above float noise); phantoms sit at <=~0 improvement.
      if (best === null || !(best.errOld - best.errNew > Math.max(1e-10, 0.01 * best.errOld))) break;
      p.clauses[best.cand.clauseIndex] = best.cand.clause;
      dec.step(
        best.cand.sitePath,
        'residual-add',
        best.cand.desc,
        Math.max(0, Math.min(1, 1 - best.errNew / best.errOld)),
      );
    }
  }

  const clausesOut: Clause[] = [];
  let complete = prior !== null && prior.clauses.length > 0;
  for (const c of prior?.clauses ?? []) {
    if (c === null) complete = false;
    else clausesOut.push(c);
  }
  const expl: Explication | null =
    prior === null
      ? null
      : { schema: AST_SCHEMA, frame: prior.frame, referents: prior.referents, clauses: clausesOut };
  let ok = false;
  let validationError: string | undefined;
  if (expl !== null && complete) {
    try {
      validateExplication(expl);
      ok = true;
    } catch (err) {
      validationError = err instanceof Error ? err.message : String(err);
    }
  } else if (expl !== null) {
    validationError = 'ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode';
  }
  const minConfidence = dec.steps.reduce((m, s) => Math.min(m, s.confidence), 1);
  return {
    explication: expl,
    ok,
    ...(validationError !== undefined ? { validationError } : {}),
    steps: dec.steps,
    minConfidence,
  };
}
