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
