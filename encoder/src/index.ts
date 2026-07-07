/**
 * @jeswr/kernel-encoder — Kernel of Truth encoder v0.
 *
 * Deterministic, training-free explication -> vector encoder
 * (construction B of reports/deterministic-concept-vectors.md §7.3;
 * spec: docs/architecture.md §1), with decoder, content-hash pin,
 * profile-1 lexicon data, and a seeded synthetic-explication generator.
 */

export {
  PRIMES,
  PRIME_BY_NAME,
  PRIME_CATEGORIES,
  ROLES,
  CORE_ROLES,
  ADJUNCT_ROLES,
  PREDICATE_FRAMES,
  FRAME_BY_PRED,
  OPERATORS,
  OPERATOR_ARITY,
  OPERATOR_CLASS,
  EXPLICATION_FRAMES,
  REF_KINDS,
  SP_DETERMINERS,
  SP_QUANTIFIERS,
  SP_MODS,
  INTENSIFIERS,
  SUBSTANTIVE_HEADS,
  INDEXICAL_FILLERS,
  DURATION_FILLERS,
  CAPS,
} from './lexicon.js';
export type {
  PrimeRecord,
  PrimeCategory,
  Role,
  Operator,
  OperatorArgClass,
  ExplicationFrame,
  RefKind,
  SPDeterminer,
  SPQuantifier,
  SPMod,
  Intensifier,
  PredicateFrame,
  SlotSpec,
  SlotFillerKind,
} from './lexicon.js';

export { AST_SCHEMA, canonicalJson } from './ast.js';
export type {
  Explication,
  Clause,
  PredClause,
  OpClause,
  OpArg,
  Filler,
  SP,
  SPHead,
  SPModifier,
  PrimeHead,
  RefHead,
  ConceptHead,
  KindPartHead,
  RefMention,
  PrimeFiller,
  ConceptRef,
  ClauseFiller,
  QuoteFiller,
  TemporalAnchorFiller,
  ReferentDecl,
} from './ast.js';

export { validateExplication, GateError } from './validate.js';
export type { ValidationStats } from './validate.js';

export {
  DEFAULT_PARAMS,
  MIN_D,
  SLOTS,
  SLOT_TABLE,
  FILLER_TABLE,
  INTENSIFIED_MODS,
  STRUCT_TAGS,
  codebookTable,
  getCodebook,
  Codebook,
  CodebookBase,
} from './codebook.js';
export type { EncoderParams, SlotName } from './codebook.js';

export {
  ALGORITHM_VERSION,
  encodeExplication,
  encodeConceptSet,
  encodeConceptSetWith,
  resolveParams,
} from './encoder.js';
export type { EncodeOptions, ConceptSetResult } from './encoder.js';

export { decodeExplication } from './decoder.js';
export type { DecodeOptions, DecodeResult, DecodeStep } from './decoder.js';

export { encoderContentHash, encoderPin, encoderContentHashQ, encoderPinQ } from './contentHash.js';
export type { EncoderPin, EncoderPinQ } from './contentHash.js';

// Toy-native quasi-orthogonal variant kot-enc-Bq/1 (architecture.md §1.3
// path (i); bead kernel-of-truth-5xo). A separate pre-registration with its
// own content-hash per D; the kot-enc-B/1 D=8192 pin above is untouched.
export { QUASI_DIMS, QuasiCodebook, getQuasiCodebook, allAtomPairs } from './codebookQ.js';
export {
  ALGORITHM_VERSION_Q,
  DEFAULT_PARAMS_Q,
  encodeExplicationQ,
  encodeConceptSetQ,
  decodeExplicationQ,
  resolveParamsQ,
} from './encoderQ.js';

export {
  generateExplication,
  mutateExplication,
} from './synth.js';
export type { SynthOptions, Mutation, EditType } from './synth.js';

export {
  DetStream,
  SeededRng,
  detPermutation,
  invertPermutation,
  applyPermutation,
  fp16RoundTrip,
  toFloat16Bits,
  fromFloat16Bits,
  DET_DOMAIN,
} from './det.js';

export { fftReal, ifftToReal, spectrumMultiply } from './fft.js';
export type { Complex64 } from './fft.js';
