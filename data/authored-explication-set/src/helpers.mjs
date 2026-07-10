/**
 * g9.author — compact builder helpers for kot-ast/1 explications.
 *
 * Serialisation sugar ONLY: every helper maps 1:1 onto an AST node shape
 * defined in encoder/src/ast.ts; no defaults are invented and nothing is
 * inferred. The semantic content of each explication lives entirely in the
 * per-concept specs (batch-*.mjs), authored in-session by the fable-class
 * authoring arm (frozen g9 record: independent var arm=fable-class-authoring).
 */

/** Atomic prime filler. */
export const P = (prime) => ({ kind: 'prime', prime });
/** Mention of an introduced referent. */
export const R = (index) => ({ kind: 'ref', index });
/** Substantive phrase. Head: prime name string | head object (kindOf/partOf/refHead). */
export const sp = (head, o = {}) => ({
  kind: 'sp',
  ...o,
  head: typeof head === 'string' ? { kind: 'primeHead', prime: head } : head,
});
export const kindOf = (of) => ({ kind: 'kindFrame', of });
export const partOf = (of) => ({ kind: 'partFrame', of });
export const refHead = (index) => ({ kind: 'refHead', index });
/** Predicate clause. */
export const pred = (predName, roles) => ({ type: 'pred', pred: predName, roles });
/** Operator clause. */
export const op = (opName, ...args) => ({ type: 'op', op: opName, args });
/** Embedded-clause filler. */
export const clause = (c) => ({ kind: 'clause', clause: c });
/** Quote filler (indexicals re-anchor to the quoted thinker/speaker). */
export const quote = (...clauses) => ({ kind: 'quote', clauses });
/** Temporal-anchor adjunct fillers. */
export const tAfter = (anchor) => ({ kind: 'temporal', op: 'AFTER', anchor });
export const tBefore = (anchor) => ({ kind: 'temporal', op: 'BEFORE', anchor });
/** SP modifier. */
export const m = (mod, intensifier) => (intensifier ? { mod, intensifier } : { mod });
/** Referent declaration list from kind names, dense from 1. */
export const refs = (...kinds) => kinds.map((refKind, i) => ({ index: i + 1, refKind }));
/** Explication assembly. */
export const X = (frame, referents, ...clauses) => ({
  schema: 'kot-ast/1',
  frame,
  referents,
  clauses,
});

// Long prime-name shorthands (exact lexicon names).
export const THING = 'SOMETHING~THING';
export const TIME = 'WHEN~TIME';
export const PLACE = 'WHERE~PLACE';
export const OTHER = 'OTHER~ELSE~ANOTHER';
export const MANY = 'MUCH~MANY';
export const FEW = 'LITTLE~FEW';
