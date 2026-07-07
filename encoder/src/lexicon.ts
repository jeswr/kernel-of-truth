/**
 * The 65-prime lexicon (NSM chart v20, 2022) plus the closed structural
 * inventories of the profile-1 explication grammar.
 *
 * Source of truth: concept-hash-design.md (the gist) §4.1 (lexicon,
 * categories, chart order), §4.2 (referent kinds), §4.4 (predicate valency
 * frames + closed role inventory), §4.5 (operators + arities), §4.6 (frames).
 *
 * These inventories are COMPLETE and CLOSED per gist §4 ("The inventories
 * below ... are complete and closed"). Any change to this file is an encoder
 * version change and moves the encoder content-hash (architecture.md §1.2,
 * poc-design.md Common rule 2).
 */

/** Prime categories, gist §4.1 chart order. */
export const PRIME_CATEGORIES = [
  'substantive',
  'relational-substantive',
  'determiner',
  'quantifier',
  'evaluator',
  'descriptor',
  'mental-predicate',
  'speech',
  'action-event-movement',
  'location-existence-specification-possession',
  'life-death',
  'time',
  'space',
  'logical',
  'intensifier-augmentor',
  'similarity',
] as const;
export type PrimeCategory = (typeof PRIME_CATEGORIES)[number];

export interface PrimeRecord {
  /** Canonical prime name (primary exponent, allolexes joined with `~`). */
  readonly name: string;
  readonly category: PrimeCategory;
  /** 1-based position in the chart (v20, 2022), category-major order per gist §4.1. */
  readonly chartIndex: number;
  readonly chartEdition: 'v20-2022';
}

function p(name: string, category: PrimeCategory, chartIndex: number): PrimeRecord {
  return { name, category, chartIndex, chartEdition: 'v20-2022' };
}

/**
 * The 65 primes, in chart order (gist §4.1). chartIndex is the 1-based
 * position in this listing; the listing order is the gist's category-major
 * chart order and is load-bearing for codebook row assignment (codebook.ts).
 */
export const PRIMES: readonly PrimeRecord[] = [
  // Substantives
  p('I', 'substantive', 1),
  p('YOU', 'substantive', 2),
  p('SOMEONE', 'substantive', 3),
  p('SOMETHING~THING', 'substantive', 4),
  p('PEOPLE', 'substantive', 5),
  p('BODY', 'substantive', 6),
  // Relational substantives
  p('KIND', 'relational-substantive', 7),
  p('PART', 'relational-substantive', 8),
  // Determiners
  p('THIS', 'determiner', 9),
  p('THE-SAME', 'determiner', 10),
  p('OTHER~ELSE~ANOTHER', 'determiner', 11),
  // Quantifiers
  p('ONE', 'quantifier', 12),
  p('TWO', 'quantifier', 13),
  p('SOME', 'quantifier', 14),
  p('ALL', 'quantifier', 15),
  p('MUCH~MANY', 'quantifier', 16),
  p('LITTLE~FEW', 'quantifier', 17),
  // Evaluators
  p('GOOD', 'evaluator', 18),
  p('BAD', 'evaluator', 19),
  // Descriptors
  p('BIG', 'descriptor', 20),
  p('SMALL', 'descriptor', 21),
  // Mental predicates
  p('THINK', 'mental-predicate', 22),
  p('KNOW', 'mental-predicate', 23),
  p('WANT', 'mental-predicate', 24),
  p("DON'T-WANT", 'mental-predicate', 25),
  p('FEEL', 'mental-predicate', 26),
  p('SEE', 'mental-predicate', 27),
  p('HEAR', 'mental-predicate', 28),
  // Speech
  p('SAY', 'speech', 29),
  p('WORDS', 'speech', 30),
  p('TRUE', 'speech', 31),
  // Actions, events, movement
  p('DO', 'action-event-movement', 32),
  p('HAPPEN', 'action-event-movement', 33),
  p('MOVE', 'action-event-movement', 34),
  // Location, existence, specification, possession
  p('BE-SOMEWHERE', 'location-existence-specification-possession', 35),
  p('THERE-IS', 'location-existence-specification-possession', 36),
  p('BE-SPEC', 'location-existence-specification-possession', 37),
  p('IS-MINE', 'location-existence-specification-possession', 38),
  // Life and death
  p('LIVE', 'life-death', 39),
  p('DIE', 'life-death', 40),
  // Time
  p('WHEN~TIME', 'time', 41),
  p('NOW', 'time', 42),
  p('BEFORE', 'time', 43),
  p('AFTER', 'time', 44),
  p('A-LONG-TIME', 'time', 45),
  p('A-SHORT-TIME', 'time', 46),
  p('FOR-SOME-TIME', 'time', 47),
  p('MOMENT', 'time', 48),
  // Space
  p('WHERE~PLACE', 'space', 49),
  p('HERE', 'space', 50),
  p('ABOVE', 'space', 51),
  p('BELOW', 'space', 52),
  p('FAR', 'space', 53),
  p('NEAR', 'space', 54),
  p('SIDE', 'space', 55),
  p('INSIDE', 'space', 56),
  p('TOUCH', 'space', 57),
  // Logical concepts
  p('NOT', 'logical', 58),
  p('MAYBE', 'logical', 59),
  p('CAN', 'logical', 60),
  p('BECAUSE', 'logical', 61),
  p('IF', 'logical', 62),
  // Intensifier, augmentor
  p('VERY', 'intensifier-augmentor', 63),
  p('MORE', 'intensifier-augmentor', 64),
  // Similarity
  p('LIKE~AS~WAY', 'similarity', 65),
];

export type PrimeName = string; // validated against PRIME_BY_NAME at the gates

export const PRIME_BY_NAME: ReadonlyMap<string, PrimeRecord> = new Map(
  PRIMES.map((r) => [r.name, r]),
);

if (PRIMES.length !== 65) {
  // Load-time invariant; a 65-prime lexicon is definitional (gist §4.1).
  throw new Error(`ERR_PRIME_LEXICON_MISMATCH: expected 65 primes, got ${PRIMES.length}`);
}

// ---------------------------------------------------------------------------
// Roles (gist §4.4, closed): 13 core + 4 adjuncts.
// ---------------------------------------------------------------------------

export const CORE_ROLES = [
  'agent',
  'undergoer',
  'experiencer',
  'stimulus',
  'addressee',
  'topic',
  'quote',
  'complement',
  'attribute',
  'locus',
  'possessor',
  'instrument',
  'comitative',
] as const;
export const ADJUNCT_ROLES = ['time', 'duration', 'place', 'manner'] as const;
export const ROLES = [...CORE_ROLES, ...ADJUNCT_ROLES] as const;
export type Role = (typeof ROLES)[number];

// ---------------------------------------------------------------------------
// Predicate valency frames (gist §4.4, closed; slots marked req/opt).
// `slotKinds` constrains what may fill the slot (validate.ts enforces).
// ---------------------------------------------------------------------------

export type SlotFillerKind =
  | 'entity' // SP / ref / concept ref
  | 'clause' // an embedded clause
  | 'quote' // a quote clause list
  | 'attributeGoodBad' // GOOD or BAD only (FEEL attribute)
  | 'attributeSpec' // SP / KIND-frame (BE-SPEC attribute)
  | 'clauseRefOrQuote' // TRUE undergoer
  | 'entityOrClause' // WANT complement: clause or SP
  | 'firstPerson'; // IS-MINE possessor: I only (first-person anchoring, gist §4.4)

export interface SlotSpec {
  readonly role: Role;
  readonly required: boolean;
  readonly kind: SlotFillerKind;
}

export interface PredicateFrame {
  readonly pred: string; // prime name
  readonly slots: readonly SlotSpec[];
}

const s = (role: Role, required: boolean, kind: SlotFillerKind): SlotSpec => ({
  role,
  required,
  kind,
});

/** Gist §4.4, verbatim inventory. All predicates additionally admit the four adjunct roles. */
export const PREDICATE_FRAMES: readonly PredicateFrame[] = [
  { pred: 'DO', slots: [s('agent', true, 'entity'), s('undergoer', false, 'entity'), s('instrument', false, 'entity'), s('comitative', false, 'entity')] },
  { pred: 'HAPPEN', slots: [s('undergoer', false, 'entity')] },
  { pred: 'MOVE', slots: [s('undergoer', true, 'entity')] },
  { pred: 'THINK', slots: [s('experiencer', true, 'entity'), s('topic', false, 'entity'), s('quote', false, 'quote')] },
  { pred: 'KNOW', slots: [s('experiencer', true, 'entity'), s('topic', false, 'entity'), s('complement', false, 'clause')] },
  { pred: 'WANT', slots: [s('experiencer', true, 'entity'), s('complement', true, 'entityOrClause')] },
  { pred: "DON'T-WANT", slots: [s('experiencer', true, 'entity'), s('complement', true, 'entityOrClause')] },
  { pred: 'FEEL', slots: [s('experiencer', true, 'entity'), s('attribute', false, 'attributeGoodBad')] },
  { pred: 'SEE', slots: [s('experiencer', true, 'entity'), s('stimulus', true, 'entity')] },
  { pred: 'HEAR', slots: [s('experiencer', true, 'entity'), s('stimulus', true, 'entity')] },
  { pred: 'SAY', slots: [s('agent', true, 'entity'), s('addressee', false, 'entity'), s('topic', false, 'entity'), s('quote', false, 'quote')] },
  { pred: 'WORDS', slots: [] }, // head-only (SP head); as a predicate frame it takes no core slots
  { pred: 'TRUE', slots: [s('undergoer', true, 'clauseRefOrQuote')] },
  { pred: 'BE-SOMEWHERE', slots: [s('undergoer', true, 'entity'), s('locus', true, 'entity')] },
  { pred: 'THERE-IS', slots: [s('undergoer', true, 'entity')] },
  { pred: 'BE-SPEC', slots: [s('undergoer', true, 'entity'), s('attribute', true, 'attributeSpec')] },
  { pred: 'IS-MINE', slots: [s('undergoer', true, 'entity'), s('possessor', true, 'firstPerson')] },
  { pred: 'LIVE', slots: [s('undergoer', true, 'entity')] },
  { pred: 'DIE', slots: [s('undergoer', true, 'entity')] },
];

export const FRAME_BY_PRED: ReadonlyMap<string, PredicateFrame> = new Map(
  PREDICATE_FRAMES.map((f) => [f.pred, f]),
);

// ---------------------------------------------------------------------------
// Operators (gist §4.5, closed, with arities).
// ---------------------------------------------------------------------------

export const OPERATORS = [
  'NOT', // 1: clause
  'CAN', // 1: clause
  'MAYBE', // 1: clause
  'IF', // 2: antecedent, consequent
  'BECAUSE', // 2: cause, effect
  'WHEN', // 2: time-clause, main
  'LIKE', // 2: comparandum, target
  'AFTER', // 2: anchor (time SP/ref/NOW), scope; anchor-only as time-adjunct filler
  'BEFORE', // 2: same as AFTER
  'VERY', // 1: over mod
  'MORE', // 1: comparative over mod/quant
] as const;
export type Operator = (typeof OPERATORS)[number];

export type OperatorArgClass =
  | 'clause1' // NOT / CAN / MAYBE
  | 'clause2' // IF / BECAUSE / WHEN
  | 'compare2' // LIKE (comparandum, target: SP or clause)
  | 'temporal2' // AFTER / BEFORE (anchor, scope)
  | 'overMod1' // VERY
  | 'overModOrQuant1'; // MORE

export const OPERATOR_CLASS: Readonly<Record<Operator, OperatorArgClass>> = {
  NOT: 'clause1',
  CAN: 'clause1',
  MAYBE: 'clause1',
  IF: 'clause2',
  BECAUSE: 'clause2',
  WHEN: 'clause2',
  LIKE: 'compare2',
  AFTER: 'temporal2',
  BEFORE: 'temporal2',
  VERY: 'overMod1',
  MORE: 'overModOrQuant1',
};

export const OPERATOR_ARITY: Readonly<Record<Operator, 1 | 2>> = {
  NOT: 1, CAN: 1, MAYBE: 1, VERY: 1, MORE: 1,
  IF: 2, BECAUSE: 2, WHEN: 2, LIKE: 2, AFTER: 2, BEFORE: 2,
};

// ---------------------------------------------------------------------------
// Explication frames (gist §4.6) and referent kinds (gist §4.2).
// ---------------------------------------------------------------------------

export const EXPLICATION_FRAMES = ['InstanceSchema', 'WhenTrue', 'RelationalSchema'] as const;
export type ExplicationFrame = (typeof EXPLICATION_FRAMES)[number];

export const REF_KINDS = ['SomeoneRef', 'SomethingRef', 'TimeRef', 'PlaceRef', 'ClauseRef'] as const;
export type RefKind = (typeof REF_KINDS)[number];

// ---------------------------------------------------------------------------
// Closed sub-inventories used by substantive phrases (gist §4.3, §4.5).
// ---------------------------------------------------------------------------

/** SP determiners (gist §4.3). `SOME` here is SOME-as-det. */
export const SP_DETERMINERS = ['THIS', 'THE-SAME', 'OTHER~ELSE~ANOTHER', 'SOME'] as const;
export type SPDeterminer = (typeof SP_DETERMINERS)[number];

export const SP_QUANTIFIERS = ['ONE', 'TWO', 'SOME', 'ALL', 'MUCH~MANY', 'LITTLE~FEW'] as const;
export type SPQuantifier = (typeof SP_QUANTIFIERS)[number];

export const SP_MODS = ['GOOD', 'BAD', 'BIG', 'SMALL'] as const;
export type SPMod = (typeof SP_MODS)[number];

export const INTENSIFIERS = ['VERY', 'MORE'] as const;
export type Intensifier = (typeof INTENSIFIERS)[number];

/** Substantive primes usable as bare SP heads (gist §4.3: "a substantive prime"). */
export const SUBSTANTIVE_HEADS = [
  'I', 'YOU', 'SOMEONE', 'SOMETHING~THING', 'PEOPLE', 'BODY', 'WORDS',
  'WHEN~TIME', 'WHERE~PLACE', 'MOMENT', 'SIDE',
] as const;

/** Indexical fillers, 0-ary (gist §4.5). These are primes used as atomic fillers. */
export const INDEXICAL_FILLERS = ['NOW', 'HERE', 'I', 'YOU'] as const;
export type IndexicalFiller = (typeof INDEXICAL_FILLERS)[number];

/** Duration fillers (gist §4.5). Primes used as atomic fillers of the duration adjunct. */
export const DURATION_FILLERS = ['A-LONG-TIME', 'A-SHORT-TIME', 'FOR-SOME-TIME', 'MOMENT'] as const;
export type DurationFiller = (typeof DURATION_FILLERS)[number];

// ---------------------------------------------------------------------------
// Profile-1 caps that bind the encoder (gist §5 table; architecture.md §1.1).
// The clause/referent caps are load-bearing for the capacity bounds
// (deterministic-concept-vectors.md §7.2: s ~ 100-200 bound terms).
// ---------------------------------------------------------------------------

export const CAPS = {
  maxClauses: 32, // incl. quote clauses
  maxReferents: 32,
  maxDepth: 12, // structural nesting depth, list spines excluded
} as const;
