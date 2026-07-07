/**
 * English surface-exponent lists for the 65 primes (NSM chart v20, 2022).
 *
 * The prime NAMES mirror encoder/src/lexicon.ts exactly (chart order,
 * `~`-joined allolex names) — a test cross-checks the two files so drift
 * fails loudly. The encoder file carries names only; the SURFACE exponent
 * phrases below (inflection variants, multiword phrases, contraction-expanded
 * forms) are mapper data, authored here with the decisions documented inline.
 *
 * Policy notes (load-bearing for M0a interpretation):
 * - Exponents are matched on contraction-EXPANDED, lowercased tokens
 *   (tokenize.ts): "don't want" arrives as ["do","not","want"].
 * - A surface form listed under >1 target (prime or concept) triggers the
 *   abstain-and-record ambiguity policy in mapper.ts — never silent choice.
 *   Deliberate double-listings: "little" (LITTLE~FEW quantifier per chart vs
 *   the SMALL-descriptor sense that dominates child-register English);
 *   copulas ("is"/"was"/...) under both BE-SOMEWHERE and BE-SPEC (English
 *   copula genuinely exponents both primes; WSD is out of scope for v0).
 * - NOT listed anywhere (documented gaps, they surface as unmapped mass):
 *   possessives "my"/"your" (case allolexes of I/YOU are limited to "me");
 *   "that"/"those" (English "that" is mostly a complementizer/relativizer —
 *   mapping it to THIS would be a large silent precision hole);
 *   bare "have" (possession is not a v20 prime beyond IS-MINE).
 */

export interface PrimeExponents {
  /** Canonical prime name, exactly as in encoder/src/lexicon.ts. */
  readonly name: string;
  /**
   * Surface exponent phrases, lowercase; multiword phrases are
   * space-separated token sequences over the expanded token stream.
   * Inflected forms are NOT listed for single words (the lemmatizer
   * produces base forms); they ARE listed for multiword phrases (phrases
   * match on surface tokens, not lemmas).
   */
  readonly exponents: readonly string[];
}

export const PRIME_EXPONENTS: readonly PrimeExponents[] = [
  // Substantives
  { name: 'I', exponents: ['i', 'me'] },
  { name: 'YOU', exponents: ['you'] },
  { name: 'SOMEONE', exponents: ['someone', 'somebody'] },
  { name: 'SOMETHING~THING', exponents: ['something', 'thing'] },
  { name: 'PEOPLE', exponents: ['people'] },
  { name: 'BODY', exponents: ['body'] },
  // Relational substantives
  { name: 'KIND', exponents: ['kind', 'kind of'] }, // bare "kind" also hits concept urn:kernel-v0:kind -> abstain
  { name: 'PART', exponents: ['part'] }, // "part of" (2-token) belongs to concept part-of; longest match wins
  // Determiners
  { name: 'THIS', exponents: ['this', 'these'] },
  { name: 'THE-SAME', exponents: ['the same', 'same'] },
  { name: 'OTHER~ELSE~ANOTHER', exponents: ['other', 'else', 'another'] },
  // Quantifiers
  { name: 'ONE', exponents: ['one'] },
  { name: 'TWO', exponents: ['two'] },
  { name: 'SOME', exponents: ['some'] },
  { name: 'ALL', exponents: ['all'] },
  { name: 'MUCH~MANY', exponents: ['much', 'many'] },
  { name: 'LITTLE~FEW', exponents: ['little', 'few'] }, // "little" double-listed under SMALL -> abstain
  // Evaluators
  { name: 'GOOD', exponents: ['good'] },
  { name: 'BAD', exponents: ['bad'] },
  // Descriptors
  { name: 'BIG', exponents: ['big'] },
  { name: 'SMALL', exponents: ['small', 'little'] },
  // Mental predicates
  { name: 'THINK', exponents: ['think'] },
  { name: 'KNOW', exponents: ['know'] },
  { name: 'WANT', exponents: ['want'] },
  {
    name: "DON'T-WANT",
    // Matched over contraction-expanded tokens; the three tense variants of
    // the auxiliary are enumerated because phrase matching is surface-level.
    exponents: ['do not want', 'does not want', 'did not want'],
  },
  { name: 'FEEL', exponents: ['feel'] },
  { name: 'SEE', exponents: ['see'] },
  { name: 'HEAR', exponents: ['hear'] },
  // Speech
  { name: 'SAY', exponents: ['say'] },
  { name: 'WORDS', exponents: ['word'] }, // lemmatizer folds "words" -> "word"
  { name: 'TRUE', exponents: ['true'] },
  // Actions, events, movement
  { name: 'DO', exponents: ['do'] }, // auxiliary vs main verb is undisambiguated -> known precision cost, measured in M0a
  { name: 'HAPPEN', exponents: ['happen'] },
  { name: 'MOVE', exponents: ['move'] },
  // Location, existence, specification, possession
  {
    name: 'BE-SOMEWHERE',
    // Bare copulas are double-listed with BE-SPEC (genuine polysemy -> abstain).
    exponents: ['is', 'are', 'am', 'was', 'were', 'be', 'been', 'being'],
  },
  {
    name: 'THERE-IS',
    // Phrase forms win over the ambiguous bare copula via longest-match.
    exponents: ['there is', 'there are', 'there was', 'there were'],
  },
  {
    name: 'BE-SPEC',
    exponents: ['is', 'are', 'am', 'was', 'were', 'be', 'been', 'being'],
  },
  { name: 'IS-MINE', exponents: ['mine'] },
  // Life and death
  { name: 'LIVE', exponents: ['live'] },
  { name: 'DIE', exponents: ['die'] },
  // Time
  { name: 'WHEN~TIME', exponents: ['when', 'time'] },
  { name: 'NOW', exponents: ['now'] },
  { name: 'BEFORE', exponents: ['before'] },
  { name: 'AFTER', exponents: ['after'] },
  { name: 'A-LONG-TIME', exponents: ['a long time'] },
  { name: 'A-SHORT-TIME', exponents: ['a short time'] },
  { name: 'FOR-SOME-TIME', exponents: ['for some time'] },
  { name: 'MOMENT', exponents: ['moment'] },
  // Space
  { name: 'WHERE~PLACE', exponents: ['where', 'place'] },
  { name: 'HERE', exponents: ['here'] },
  { name: 'ABOVE', exponents: ['above'] },
  { name: 'BELOW', exponents: ['below'] },
  { name: 'FAR', exponents: ['far'] },
  { name: 'NEAR', exponents: ['near'] }, // also concept urn:kernel-v0:near -> abstain
  { name: 'SIDE', exponents: ['side'] },
  { name: 'INSIDE', exponents: ['inside'] }, // also concept urn:kernel-v0:inside -> abstain
  { name: 'TOUCH', exponents: ['touch'] },
  // Logical concepts
  { name: 'NOT', exponents: ['not'] },
  { name: 'MAYBE', exponents: ['maybe'] },
  { name: 'CAN', exponents: ['can'] }, // "could" folds to "can" via the irregular table
  { name: 'BECAUSE', exponents: ['because'] },
  { name: 'IF', exponents: ['if'] },
  // Intensifier, augmentor
  { name: 'VERY', exponents: ['very'] },
  { name: 'MORE', exponents: ['more'] },
  // Similarity
  { name: 'LIKE~AS~WAY', exponents: ['like', 'as', 'way'] }, // English verb "like" (enjoy) is NOT the similarity prime -> known precision cost, measured in M0a
];

if (PRIME_EXPONENTS.length !== 65) {
  throw new Error(
    `ERR_PRIME_EXPONENTS_MISMATCH: expected 65 primes, got ${PRIME_EXPONENTS.length}`,
  );
}
