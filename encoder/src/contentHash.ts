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
import { ALGORITHM_VERSION_Q, resolveParamsQ } from './encoderQ.js';

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

// ---------------------------------------------------------------------------
// Toy-native quasi-orthogonal variant kot-enc-Bq/1 (encoderQ.ts; a NEW
// pre-registration per poc-design Common rule 2 — its hashes are pinned into
// poc-design.md by the coordinator, separately from the kot-enc-B/1 pin).
// The pin additionally covers the atom-derivation rule (the codebook is no
// longer a row-index table but a labelled seeded construction) and the
// arbitrary-length binding transform. One hash per D: Bq/1@512 and Bq/1@576
// are distinct encoders.
// ---------------------------------------------------------------------------

export interface EncoderPinQ extends Omit<EncoderPin, 'algorithmVersion'> {
  readonly algorithmVersion: typeof ALGORITHM_VERSION_Q;
  /** How each (slot, filler) atom is derived from the pinned table ids. */
  readonly atomDerivation: string;
  /** The cross-clause binding transform (D-dependent FFT route). */
  readonly binding: string;
}

export function encoderPinQ(params?: Partial<EncoderParams>): EncoderPinQ {
  const p = resolveParamsQ(params);
  return {
    schemaVersion: AST_SCHEMA,
    algorithmVersion: ALGORITHM_VERSION_Q,
    detDomain: DET_DOMAIN,
    D: p.D,
    weighting: { alphaStruct: p.alphaStruct, notBoost: p.notBoost },
    codebook: codebookTable(),
    atomDerivation:
      'rademacher(+/-1/sqrt(D)) signs from DetStream label qatom/<D>/<slotId>/<fillerId>; slotId = codebook-table slot entry >> 8, fillerId = codebook-table filler entry',
    binding:
      'unitary circular convolution, quarter-phase tag spectra; radix-2 FFT for power-of-two D, Bluestein chirp-z otherwise',
  };
}

/** sha-256 (hex) over the canonical JSON serialisation of the variant pin. */
export function encoderContentHashQ(params?: Partial<EncoderParams>): string {
  return createHash('sha256').update(canonicalJson(encoderPinQ(params))).digest('hex');
}
