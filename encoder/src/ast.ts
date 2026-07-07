/**
 * Explication AST — a typed, versioned JSON mirror of the profile-1
 * explication grammar (concept-hash-design.md §4). The AST covers exactly the
 * explication (frame + referents + ordered clause list); the wider definition
 * record (axioms, semantic status, annotation layer) is the identity layer's
 * business (gist §5) and is out of the vector encoder's scope by design
 * (architecture.md §1.1: the vector encodes the explication tree).
 */

import type {
  ExplicationFrame,
  Operator,
  RefKind,
  Role,
  SPDeterminer,
  SPMod,
  SPQuantifier,
  Intensifier,
} from './lexicon.js';

/** Schema identifier. Any change to the AST shape bumps this. */
export const AST_SCHEMA = 'kot-ast/1' as const;

// ---------------------------------------------------------------------------
// Fillers
// ---------------------------------------------------------------------------

/** Mention of an already-introduced discourse referent (gist §4.2: `[ cdef:ref n ]`). */
export interface RefMention {
  readonly kind: 'ref';
  readonly index: number; // 1-based, dense
}

/** Atomic prime filler (indexicals NOW/HERE/I/YOU, durations, GOOD/BAD attributes, mods over ops...). */
export interface PrimeFiller {
  readonly kind: 'prime';
  readonly prime: string; // validated against the 65-prime lexicon
}

/** Reference to a defined concept by id (`urn:concept:...`); binds that concept's canonical vector. */
export interface ConceptRef {
  readonly kind: 'concept';
  readonly id: string;
}

/** Embedded clause filler (KNOW/WANT complements, TRUE undergoer as ClauseRef alternative). */
export interface ClauseFiller {
  readonly kind: 'clause';
  readonly clause: Clause;
}

/**
 * Quote filler (gist §4.6 `cdef:quoteClauses`): an ordered clause list that
 * re-anchors indexicals (I = quoted thinker/speaker, NOW = quoted moment).
 * Quote-local referents (introduced by `bind` inside the quote) scope to the quote.
 */
export interface QuoteFiller {
  readonly kind: 'quote';
  readonly clauses: readonly Clause[];
}

/**
 * Temporal anchor filler (gist §4.5: AFTER/BEFORE "also usable as a
 * time-adjunct filler with anchor only"), e.g. time: AFTER(now).
 */
export interface TemporalAnchorFiller {
  readonly kind: 'temporal';
  readonly op: 'AFTER' | 'BEFORE';
  readonly anchor: SP | RefMention | PrimeFiller; // time SP / ref / NOW
}

export type Filler =
  | SP
  | RefMention
  | PrimeFiller
  | ConceptRef
  | ClauseFiller
  | QuoteFiller
  | TemporalAnchorFiller;

// ---------------------------------------------------------------------------
// Substantive phrases (gist §4.3)
// ---------------------------------------------------------------------------

/** `head p:KIND ; cdef:of <SP-or-conceptRef>` — likewise for PART. */
export interface KindPartHead {
  readonly kind: 'kindFrame' | 'partFrame';
  readonly of: SP | ConceptRef | RefMention;
}

export interface PrimeHead {
  readonly kind: 'primeHead';
  readonly prime: string; // a substantive prime
}

export interface RefHead {
  readonly kind: 'refHead';
  readonly index: number;
}

export interface ConceptHead {
  readonly kind: 'conceptHead';
  readonly id: string;
}

export type SPHead = PrimeHead | KindPartHead | RefHead | ConceptHead;

export interface SPModifier {
  readonly mod: SPMod; // GOOD | BAD | BIG | SMALL
  readonly intensifier?: Intensifier; // optionally under VERY / MORE
}

/** `SP := [det]? [quant]? [mod]* head [restrictedBy: clause]?` (gist §4.3). */
export interface SP {
  readonly kind: 'sp';
  readonly det?: SPDeterminer;
  readonly quant?: SPQuantifier;
  readonly mods?: readonly SPModifier[];
  readonly head: SPHead;
  readonly restrictedBy?: Clause;
  /** Introducing occurrence of referent `bind` (gist §4.2). */
  readonly bind?: number;
}

// ---------------------------------------------------------------------------
// Clauses (gist §4.4-§4.6)
// ---------------------------------------------------------------------------

export interface PredClause {
  readonly type: 'pred';
  readonly pred: string; // a predicate prime with a valency frame (gist §4.4)
  /** Role -> filler map; validated against the predicate's frame + adjuncts. */
  readonly roles: Readonly<Partial<Record<Role, Filler>>>;
}

/** Operator argument: clause for clause-arity ops; SP/ref/prime for anchors and mods. */
export type OpArg = Clause | SP | RefMention | PrimeFiller;

export interface OpClause {
  readonly type: 'op';
  readonly op: Operator;
  readonly args: readonly OpArg[]; // arity checked against OPERATOR_ARITY
}

export type Clause = PredClause | OpClause;

// ---------------------------------------------------------------------------
// Explication
// ---------------------------------------------------------------------------

export interface ReferentDecl {
  readonly index: number; // dense from 1
  readonly refKind: RefKind;
}

export interface Explication {
  readonly schema: typeof AST_SCHEMA;
  /** Typed explication frame (gist §4.6). Referent 1 (and 2 for RelationalSchema) is frame-implicit. */
  readonly frame: ExplicationFrame;
  readonly referents: readonly ReferentDecl[];
  readonly clauses: readonly Clause[]; // ordered (gist §4.6)
}

// ---------------------------------------------------------------------------
// Canonical JSON serialisation (deterministic key order) — used by tests,
// golden fixtures and the synthetic generator; NOT the identity layer's
// RDF canonical form.
// ---------------------------------------------------------------------------

export function canonicalJson(value: unknown): string {
  if (value === null || typeof value === 'number' || typeof value === 'boolean') {
    return JSON.stringify(value);
  }
  if (typeof value === 'string') return JSON.stringify(value);
  if (Array.isArray(value)) {
    return `[${value.map(canonicalJson).join(',')}]`;
  }
  if (typeof value === 'object') {
    const obj = value as Record<string, unknown>;
    const keys = Object.keys(obj)
      .filter((k) => obj[k] !== undefined)
      .sort();
    return `{${keys.map((k) => `${JSON.stringify(k)}:${canonicalJson(obj[k])}`).join(',')}}`;
  }
  throw new Error(`ERR_UNSERIALISABLE: cannot canonicalise value of type ${typeof value}`);
}
