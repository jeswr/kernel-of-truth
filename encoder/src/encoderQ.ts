/**
 * Toy-native encoder variant `kot-enc-Bq/1` (bead kernel-of-truth-5xo):
 * construction B re-instantiated at the host model's native dimension
 * D ∈ {512, 576} over the QUASI-ORTHOGONAL codebook of codebookQ.ts.
 *
 * This is architecture.md §1.3 dimension-policy PATH (i) — the kernel
 * re-encoded natively at D = d_model for E1/E4, which "tests structure-derived
 * content vs content-free at matched D, NOT the capacity story". Everything
 * except the atom codebook is construction B verbatim (shared
 * InternalEncoder): whitened unitary circular-convolution binding across
 * clauses/depth (Bluestein chirp-z FFT at D = 576, radix-2 at 512),
 * deterministic position/referent permutations, pinned superposition
 * weighting, identical traversal order.
 *
 * By poc-design Common rule 2 this is a NEW pre-registration: it has its own
 * ALGORITHM_VERSION and its own content-hash per D (contentHash.ts
 * encoderContentHashQ), its own X0 golden fixture, and its own Phase-X bars
 * (restated in poc/src/x0-q.ts / x1-q.ts). The kot-enc-B/1 pin at D=8192 is
 * untouched.
 */

import type { Explication } from './ast.js';
import { DEFAULT_PARAMS, type EncoderParams } from './codebook.js';
import { QUASI_DIMS, getQuasiCodebook } from './codebookQ.js';
import {
  InternalEncoder,
  encodeConceptSetWith,
  type ConceptSetResult,
  type EncodeOptions,
} from './encoder.js';
import { decodeWithEncoder, type DecodeOptions, type DecodeResult } from './decoder.js';
import { validateExplication } from './validate.js';

export const ALGORITHM_VERSION_Q = 'kot-enc-Bq/1';

/** Default toy-native parameters: D = 512 (the E1 toy's d_model); weighting inherited. */
export const DEFAULT_PARAMS_Q: EncoderParams = Object.freeze({
  D: 512,
  alphaStruct: DEFAULT_PARAMS.alphaStruct,
  notBoost: DEFAULT_PARAMS.notBoost,
});

export function checkParamsQ(params: EncoderParams): void {
  if (!(QUASI_DIMS as readonly number[]).includes(params.D)) {
    throw new Error(
      `ERR_QUASI_DIMENSION: D=${params.D} is not a pre-registered toy-native dimension ` +
        `(${QUASI_DIMS.join(', ')}); other dimensions are a new pre-registration (poc-design Common rule 2)`,
    );
  }
  if (!(params.alphaStruct > 0) || !Number.isFinite(params.alphaStruct)) {
    throw new Error(`ERR_PARAM: alphaStruct must be finite and > 0, got ${params.alphaStruct}`);
  }
  if (!(params.notBoost > 0) || !Number.isFinite(params.notBoost)) {
    throw new Error(`ERR_PARAM: notBoost must be finite and > 0, got ${params.notBoost}`);
  }
}

export function resolveParamsQ(partial?: Partial<EncoderParams>): EncoderParams {
  const params: EncoderParams = { ...DEFAULT_PARAMS_Q, ...(partial ?? {}) };
  checkParamsQ(params);
  return params;
}

/**
 * Encode a validated explication to its canonical unit vector at toy-native D.
 * Validation gates run first and fail closed (same gates as encodeExplication).
 */
export function encodeExplicationQ(e: Explication, opts?: EncodeOptions): Float64Array {
  validateExplication(e);
  const params = resolveParamsQ(opts?.params);
  return new InternalEncoder(params, opts?.concepts, getQuasiCodebook(params.D)).encodeExplication(e);
}

/** Memoised reference-DAG concept-set encoding at toy-native D (= encodeConceptSet). */
export function encodeConceptSetQ(
  defs: ReadonlyMap<string, Explication>,
  opts?: EncodeOptions,
): ConceptSetResult {
  const params = resolveParamsQ(opts?.params);
  return encodeConceptSetWith(defs, params, getQuasiCodebook(params.D), opts);
}

/**
 * Decode at toy-native D. MEASUREMENT ONLY — the capacity math (DCV §7.2)
 * says full decode of the capped explication space cannot survive at
 * D = 512-576; X2-q reports what it does achieve, ungated (codebookQ.ts
 * header, "WHAT IS LOST"). Matched filtering now runs against a coherent
 * dictionary: sibling crosstalk ~ 1/sqrt(D) per term instead of exactly 0.
 */
export function decodeExplicationQ(v: Float64Array, opts?: DecodeOptions): DecodeResult {
  const params = resolveParamsQ(opts?.params);
  return decodeWithEncoder(
    v,
    params,
    new InternalEncoder(params, opts?.concepts, getQuasiCodebook(params.D)),
    opts,
  );
}
