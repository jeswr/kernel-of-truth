/**
 * Encoder content-hash — the pin required by poc-design.md Common rule 2
 * ("one encoder version ... its content hash is written into this file
 * before the first E-run") and architecture.md §3 (vectors keyed by
 * (encoder-version-hash, D, codebook-hash)).
 *
 * The hash covers everything that determines the input->vector map:
 * AST schema version, algorithm version (which pins traversal order,
 * binding ops and derivation labels), D, the full codebook row-assignment
 * table, the weighting parameters, and the deterministic-derivation domain.
 * Decoder thresholds are NOT included (they do not affect encoding).
 */

import { createHash } from 'node:crypto';
import { AST_SCHEMA, canonicalJson } from './ast.js';
import { DET_DOMAIN } from './det.js';
import { codebookTable, type EncoderParams } from './codebook.js';
import { ALGORITHM_VERSION, resolveParams } from './encoder.js';

export interface EncoderPin {
  readonly schemaVersion: typeof AST_SCHEMA;
  readonly algorithmVersion: typeof ALGORITHM_VERSION;
  readonly detDomain: string;
  readonly D: number;
  readonly weighting: { readonly alphaStruct: number; readonly notBoost: number };
  readonly codebook: Record<string, number>;
}

export function encoderPin(params?: Partial<EncoderParams>): EncoderPin {
  const p = resolveParams(params);
  return {
    schemaVersion: AST_SCHEMA,
    algorithmVersion: ALGORITHM_VERSION,
    detDomain: DET_DOMAIN,
    D: p.D,
    weighting: { alphaStruct: p.alphaStruct, notBoost: p.notBoost },
    codebook: codebookTable(),
  };
}

/** sha-256 (hex) over the canonical JSON serialisation of the pin. */
export function encoderContentHash(params?: Partial<EncoderParams>): string {
  return createHash('sha256').update(canonicalJson(encoderPin(params))).digest('hex');
}
