export { PRIME_EXPONENTS, type PrimeExponents } from './primes.js';
export { tokenize, type Token } from './tokenize.js';
export { lemmaCandidates, irregularBase } from './lemmatize.js';
export {
  buildLexicon,
  conceptEntries,
  loadManifestConcepts,
  surfaceOfLabel,
  targetKey,
  type ConceptLabel,
  type Lexicon,
  type LexiconEntry,
  type Target,
} from './lexicon.js';
export {
  mapText,
  mapTokens,
  type AnnotatedToken,
  type Decision,
} from './mapper.js';
export {
  A1_POLICY_SHA256,
  A1_PRESET_NAME,
  compilePriorityIndex,
  decisionSetKey,
  POLICY_PRESETS,
  policyHash,
  policyPreset,
  SHADOWED_CONCEPTS,
  SHADOWED_EXCLUDE_ALL5,
  SHADOWED_HYBRID_RECOMMENDED,
  SHADOWED_TIERS_ALL5,
  SHADOWED_TIERS_MEASURED,
  type MapperPolicy,
  type PriorityIndex,
  type PriorityRule,
} from './policy.js';
