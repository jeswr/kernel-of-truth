/**
 * Fail-closed validation gates for the explication AST, mirroring the
 * profile-1 grammar checks (concept-hash-design.md §4.2-§4.7, §5 caps).
 *
 * Everything here throws GateError with a stable error code and an AST path;
 * there are no silent fallbacks (programme quality bar). The encoder refuses
 * any explication that does not pass these gates.
 */

import type {
  Clause,
  Explication,
  Filler,
  OpArg,
  PredClause,
  OpClause,
  SP,
  SPHead,
} from './ast.js';
import { AST_SCHEMA } from './ast.js';
import {
  CAPS,
  DURATION_FILLERS,
  EXPLICATION_FRAMES,
  FRAME_BY_PRED,
  OPERATOR_ARITY,
  OPERATOR_CLASS,
  PRIME_BY_NAME,
  REF_KINDS,
  ROLES,
  ADJUNCT_ROLES,
  SP_DETERMINERS,
  SP_MODS,
  SP_QUANTIFIERS,
  INTENSIFIERS,
  type Role,
  type SlotFillerKind,
} from './lexicon.js';

export class GateError extends Error {
  constructor(
    readonly code: string,
    readonly path: string,
    detail: string,
  ) {
    super(`${code} at ${path}: ${detail}`);
    this.name = 'GateError';
  }
}

const fail = (code: string, path: string, detail: string): never => {
  throw new GateError(code, path, detail);
};

interface Scope {
  readonly introduced: Set<number>;
  readonly isQuote: boolean;
}

interface Ctx {
  readonly declared: Map<number, string>; // index -> refKind
  readonly scopes: Scope[]; // stack; introductions visible in own + outer scopes
  readonly introducedAnywhere: Set<number>;
  clauseCount: number;
}

function canSee(ctx: Ctx, index: number): boolean {
  return ctx.scopes.some((s) => s.introduced.has(index));
}

function introduce(ctx: Ctx, index: number, path: string): void {
  if (!ctx.declared.has(index)) {
    fail('ERR_BIND_UNDECLARED', path, `bind ${index} has no referent declaration`);
  }
  if (ctx.introducedAnywhere.has(index)) {
    fail('ERR_BIND_DUPLICATE', path, `referent ${index} has more than one introducing occurrence`);
  }
  ctx.introducedAnywhere.add(index);
  const top = ctx.scopes[ctx.scopes.length - 1];
  if (top === undefined) fail('ERR_INTERNAL', path, 'empty scope stack');
  top!.introduced.add(index);
}

function checkRefMention(ctx: Ctx, index: number, path: string): void {
  if (!Number.isInteger(index) || index < 1) {
    fail('ERR_REF_INDEX', path, `referent index must be a positive integer, got ${index}`);
  }
  if (!ctx.declared.has(index)) {
    fail('ERR_REF_UNDECLARED', path, `ref ${index} is not declared`);
  }
  if (!canSee(ctx, index)) {
    // gist §4.2: "A cdef:ref to an undeclared or not-yet-introduced index is a gate error."
    fail('ERR_REF_NOT_INTRODUCED', path, `ref ${index} used before its introducing occurrence (or out of quote scope)`);
  }
}

function checkPrime(name: string, path: string): void {
  if (!PRIME_BY_NAME.has(name)) {
    fail('ERR_PRIME_UNKNOWN', path, `'${name}' is not in the 65-prime lexicon`);
  }
}

const maxDepthSeen = { value: 0 };

function depthCheck(depth: number, path: string): void {
  if (depth > CAPS.maxDepth) {
    fail('ERR_CAP_DEPTH', path, `structural nesting depth ${depth} exceeds cap ${CAPS.maxDepth}`);
  }
  if (depth > maxDepthSeen.value) maxDepthSeen.value = depth;
}

// ---------------------------------------------------------------------------
// SP validation (gist §4.3)
// ---------------------------------------------------------------------------

function validateSPHead(ctx: Ctx, head: SPHead, depth: number, path: string): void {
  switch (head.kind) {
    case 'primeHead':
      checkPrime(head.prime, `${path}.prime`);
      return;
    case 'refHead':
      checkRefMention(ctx, head.index, `${path}.index`);
      return;
    case 'conceptHead':
      if (typeof head.id !== 'string' || head.id.length === 0) {
        fail('ERR_CONCEPT_REF', path, 'concept head must carry a non-empty id');
      }
      return;
    case 'kindFrame':
    case 'partFrame': {
      const of = head.of;
      if (of.kind === 'sp') validateSP(ctx, of, depth + 1, `${path}.of`);
      else if (of.kind === 'ref') checkRefMention(ctx, of.index, `${path}.of`);
      else if (of.kind === 'concept') {
        if (typeof of.id !== 'string' || of.id.length === 0) {
          fail('ERR_CONCEPT_REF', `${path}.of`, 'concept ref must carry a non-empty id');
        }
      } else fail('ERR_SP_HEAD', `${path}.of`, 'KIND/PART of-target must be SP, ref or concept ref');
      return;
    }
    default:
      fail('ERR_SP_HEAD', path, `unknown SP head kind '${(head as { kind: string }).kind}'`);
  }
}

function validateSP(ctx: Ctx, sp: SP, depth: number, path: string): void {
  depthCheck(depth, path);
  if (sp.bind !== undefined) {
    // Introduce on entry so a restrictedBy clause may mention the referent it introduces.
    introduce(ctx, sp.bind, `${path}.bind`);
  }
  if (sp.det !== undefined && !(SP_DETERMINERS as readonly string[]).includes(sp.det)) {
    fail('ERR_SP_DET', `${path}.det`, `'${sp.det}' is not an SP determiner`);
  }
  if (sp.quant !== undefined && !(SP_QUANTIFIERS as readonly string[]).includes(sp.quant)) {
    fail('ERR_SP_QUANT', `${path}.quant`, `'${sp.quant}' is not an SP quantifier`);
  }
  const seenMods = new Set<string>();
  for (const [i, m] of (sp.mods ?? []).entries()) {
    if (!(SP_MODS as readonly string[]).includes(m.mod)) {
      fail('ERR_SP_MOD', `${path}.mods[${i}]`, `'${m.mod}' is not an SP modifier`);
    }
    if (m.intensifier !== undefined && !(INTENSIFIERS as readonly string[]).includes(m.intensifier)) {
      fail('ERR_SP_MOD', `${path}.mods[${i}]`, `'${m.intensifier}' is not an intensifier`);
    }
    const key = `${m.intensifier ?? ''}+${m.mod}`;
    if (seenMods.has(key)) {
      // Duplicate mod entries would encode as a doubled superposition weight
      // and cannot round-trip; the grammar gains nothing from them.
      fail('ERR_SP_MOD', `${path}.mods[${i}]`, `duplicate modifier '${key}'`);
    }
    seenMods.add(key);
  }
  validateSPHead(ctx, sp.head, depth, `${path}.head`);
  if (sp.restrictedBy !== undefined) {
    validateClause(ctx, sp.restrictedBy, depth + 1, `${path}.restrictedBy`);
  }
}

// ---------------------------------------------------------------------------
// Filler / slot-kind validation (gist §4.4)
// ---------------------------------------------------------------------------

function validateFiller(ctx: Ctx, f: Filler, depth: number, path: string): void {
  switch (f.kind) {
    case 'sp':
      validateSP(ctx, f, depth + 1, path);
      return;
    case 'ref':
      checkRefMention(ctx, f.index, path);
      return;
    case 'prime':
      checkPrime(f.prime, path);
      return;
    case 'concept':
      if (typeof f.id !== 'string' || f.id.length === 0) {
        fail('ERR_CONCEPT_REF', path, 'concept ref must carry a non-empty id');
      }
      return;
    case 'clause':
      validateClause(ctx, f.clause, depth + 1, `${path}.clause`);
      return;
    case 'quote': {
      depthCheck(depth + 1, path);
      ctx.scopes.push({ introduced: new Set(), isQuote: true });
      for (const [i, c] of f.clauses.entries()) {
        validateClause(ctx, c, depth + 1, `${path}.clauses[${i}]`);
      }
      ctx.scopes.pop();
      return;
    }
    case 'temporal': {
      depthCheck(depth + 1, path);
      if (f.op !== 'AFTER' && f.op !== 'BEFORE') {
        fail('ERR_TEMPORAL_ANCHOR', path, `temporal filler op must be AFTER or BEFORE, got '${f.op}'`);
      }
      const a = f.anchor;
      if (a.kind === 'sp') validateSP(ctx, a, depth + 1, `${path}.anchor`);
      else if (a.kind === 'ref') checkRefMention(ctx, a.index, `${path}.anchor`);
      else if (a.kind === 'prime') {
        if (a.prime !== 'NOW') {
          // gist §4.5: anchor is "a time SP/ref/NOW"
          fail('ERR_TEMPORAL_ANCHOR', `${path}.anchor`, `atomic temporal anchor must be NOW, got '${a.prime}'`);
        }
      } else fail('ERR_TEMPORAL_ANCHOR', `${path}.anchor`, 'anchor must be SP, ref or NOW');
      return;
    }
    default:
      fail('ERR_FILLER', path, `unknown filler kind '${(f as { kind: string }).kind}'`);
  }
}

function slotKindAccepts(kind: SlotFillerKind, f: Filler, path: string): void {
  // Indexical fillers I/YOU are licensed 0-ary entity fillers (gist §4.5).
  const isIndexicalEntity = f.kind === 'prime' && (f.prime === 'I' || f.prime === 'YOU');
  const isEntity = f.kind === 'sp' || f.kind === 'ref' || f.kind === 'concept' || isIndexicalEntity;
  switch (kind) {
    case 'entity':
      if (!isEntity) fail('ERR_SLOT_KIND', path, `slot takes SP/ref/concept/I/YOU, got '${f.kind}'`);
      return;
    case 'clause':
      if (f.kind !== 'clause') fail('ERR_SLOT_KIND', path, `slot takes a clause, got '${f.kind}'`);
      return;
    case 'quote':
      if (f.kind !== 'quote') fail('ERR_SLOT_KIND', path, `slot takes a quote, got '${f.kind}'`);
      return;
    case 'attributeGoodBad':
      if (f.kind !== 'prime' || (f.prime !== 'GOOD' && f.prime !== 'BAD')) {
        fail('ERR_SLOT_KIND', path, 'FEEL attribute must be GOOD or BAD (gist §4.4)');
      }
      return;
    case 'attributeSpec':
      if (!(f.kind === 'sp' || f.kind === 'concept')) {
        fail('ERR_SLOT_KIND', path, 'BE-SPEC attribute must be an SP/KIND-frame or concept ref');
      }
      return;
    case 'clauseRefOrQuote':
      if (!(f.kind === 'ref' || f.kind === 'quote' || f.kind === 'clause')) {
        fail('ERR_SLOT_KIND', path, 'TRUE undergoer must be a ClauseRef or quote (gist §4.4)');
      }
      return;
    case 'entityOrClause':
      if (!(isEntity || f.kind === 'clause')) {
        fail('ERR_SLOT_KIND', path, `slot takes clause or SP, got '${f.kind}'`);
      }
      return;
    case 'firstPerson':
      // gist §4.4: IS-MINE possessor is I only (first-person anchored per NSM).
      if (!(f.kind === 'prime' && f.prime === 'I')) {
        fail('ERR_SLOT_KIND', path, 'IS-MINE possessor must be I (first-person anchoring, gist §4.4)');
      }
      return;
    default:
      fail('ERR_SLOT_KIND', path, `unknown slot kind '${kind satisfies never}'`);
  }
}

function validateAdjunct(ctx: Ctx, role: Role, f: Filler, depth: number, path: string): void {
  switch (role) {
    case 'time':
      if (!(f.kind === 'sp' || f.kind === 'ref' || f.kind === 'temporal' || (f.kind === 'prime' && f.prime === 'NOW'))) {
        fail('ERR_SLOT_KIND', path, `time adjunct must be SP/ref/NOW/temporal-anchor, got '${f.kind}'`);
      }
      break;
    case 'duration':
      if (!(f.kind === 'prime' && (DURATION_FILLERS as readonly string[]).includes(f.prime)) && f.kind !== 'sp') {
        fail('ERR_SLOT_KIND', path, 'duration adjunct must be a duration filler prime or SP (gist §4.5)');
      }
      break;
    case 'place':
      if (!(f.kind === 'sp' || f.kind === 'ref' || (f.kind === 'prime' && f.prime === 'HERE'))) {
        fail('ERR_SLOT_KIND', path, `place adjunct must be SP/ref/HERE, got '${f.kind}'`);
      }
      break;
    case 'manner':
      if (!(f.kind === 'sp' || f.kind === 'ref' || f.kind === 'prime' || f.kind === 'concept')) {
        fail('ERR_SLOT_KIND', path, `manner adjunct must be SP/ref/prime/concept, got '${f.kind}'`);
      }
      break;
    default:
      fail('ERR_ROLE_UNKNOWN', path, `'${role}' is not an adjunct role`);
  }
  validateFiller(ctx, f, depth, path);
}

// ---------------------------------------------------------------------------
// Clause validation
// ---------------------------------------------------------------------------

function validatePredClause(ctx: Ctx, c: PredClause, depth: number, path: string): void {
  const frame = FRAME_BY_PRED.get(c.pred);
  if (frame === undefined) {
    fail('ERR_PRED_UNKNOWN', `${path}.pred`, `'${c.pred}' has no predicate valency frame (gist §4.4)`);
    return;
  }
  const roleNames = Object.keys(c.roles) as Role[];
  for (const r of roleNames) {
    if (!(ROLES as readonly string[]).includes(r)) {
      fail('ERR_ROLE_UNKNOWN', `${path}.roles.${r}`, `'${r}' is not in the closed role inventory`);
    }
  }
  // Required slots present; present slots licensed by the frame or adjuncts.
  for (const slot of frame.slots) {
    if (slot.required && c.roles[slot.role] === undefined) {
      fail('ERR_ROLE_REQUIRED_MISSING', path, `predicate ${c.pred} requires role '${slot.role}'`);
    }
  }
  // Deterministic canonical walk order: the fixed ROLES order (lexicon.ts).
  for (const role of ROLES) {
    const f = c.roles[role];
    if (f === undefined) continue;
    const rolePath = `${path}.roles.${role}`;
    const slot = frame.slots.find((sl) => sl.role === role);
    if (slot !== undefined) {
      slotKindAccepts(slot.kind, f, rolePath);
      validateFiller(ctx, f, depth, rolePath);
    } else if ((ADJUNCT_ROLES as readonly string[]).includes(role)) {
      validateAdjunct(ctx, role, f, depth, rolePath);
    } else {
      fail('ERR_ROLE_NOT_IN_FRAME', rolePath, `role '${role}' is not licensed by ${c.pred}'s frame`);
    }
  }
}

function validateOpClause(ctx: Ctx, c: OpClause, depth: number, path: string): void {
  const arity = OPERATOR_ARITY[c.op];
  if (arity === undefined) {
    fail('ERR_OP_UNKNOWN', `${path}.op`, `'${c.op}' is not in the closed operator inventory (gist §4.5)`);
    return;
  }
  if (c.args.length !== arity) {
    fail('ERR_OP_ARITY', path, `${c.op} takes ${arity} argument(s), got ${c.args.length}`);
  }
  const cls = OPERATOR_CLASS[c.op];
  const argOk = (arg: OpArg, want: 'clause' | 'entity' | 'anchor' | 'mod' | 'modOrQuant', p: string): void => {
    const isClause = 'type' in arg;
    switch (want) {
      case 'clause':
        if (!isClause) fail('ERR_OP_ARG_KIND', p, `${c.op} argument must be a clause`);
        validateClause(ctx, arg as Clause, depth + 1, p);
        return;
      case 'entity': // LIKE comparandum/target: SP, ref or clause
        if (isClause) validateClause(ctx, arg as Clause, depth + 1, p);
        else validateFiller(ctx, arg as Filler, depth, p);
        return;
      case 'anchor': {
        if (isClause) fail('ERR_OP_ARG_KIND', p, `${c.op} anchor must be a time SP/ref/NOW`);
        const a = arg as Filler;
        if (a.kind === 'prime' && a.prime !== 'NOW') {
          fail('ERR_OP_ARG_KIND', p, `atomic temporal anchor must be NOW, got '${a.prime}'`);
        }
        if (!(a.kind === 'sp' || a.kind === 'ref' || a.kind === 'prime')) {
          fail('ERR_OP_ARG_KIND', p, 'anchor must be a time SP/ref/NOW');
        }
        validateFiller(ctx, a, depth, p);
        return;
      }
      case 'mod':
        if (isClause || (arg as Filler).kind !== 'prime' || !(SP_MODS as readonly string[]).includes((arg as { prime: string }).prime)) {
          fail('ERR_OP_ARG_KIND', p, `${c.op} scopes over a mod (GOOD/BAD/BIG/SMALL)`);
        }
        return;
      case 'modOrQuant': {
        const prime = !isClause && (arg as Filler).kind === 'prime' ? (arg as { prime: string }).prime : undefined;
        if (
          prime === undefined ||
          !((SP_MODS as readonly string[]).includes(prime) || (SP_QUANTIFIERS as readonly string[]).includes(prime))
        ) {
          fail('ERR_OP_ARG_KIND', p, 'MORE scopes over a mod or quantifier');
        }
        return;
      }
    }
  };
  const a0 = c.args[0]!;
  switch (cls) {
    case 'clause1':
      argOk(a0, 'clause', `${path}.args[0]`);
      break;
    case 'clause2':
      argOk(a0, 'clause', `${path}.args[0]`);
      argOk(c.args[1]!, 'clause', `${path}.args[1]`);
      break;
    case 'compare2':
      argOk(a0, 'entity', `${path}.args[0]`);
      argOk(c.args[1]!, 'entity', `${path}.args[1]`);
      break;
    case 'temporal2':
      argOk(a0, 'anchor', `${path}.args[0]`);
      argOk(c.args[1]!, 'clause', `${path}.args[1]`);
      break;
    case 'overMod1':
      argOk(a0, 'mod', `${path}.args[0]`);
      break;
    case 'overModOrQuant1':
      argOk(a0, 'modOrQuant', `${path}.args[0]`);
      break;
  }
}

function validateClause(ctx: Ctx, c: Clause, depth: number, path: string): void {
  ctx.clauseCount += 1;
  if (ctx.clauseCount > CAPS.maxClauses) {
    fail('ERR_CAP_CLAUSES', path, `explication exceeds ${CAPS.maxClauses} clauses (incl. quote/embedded clauses)`);
  }
  depthCheck(depth, path);
  if (c.type === 'pred') validatePredClause(ctx, c, depth, path);
  else if (c.type === 'op') validateOpClause(ctx, c, depth, path);
  else fail('ERR_CLAUSE_TYPE', path, `unknown clause type '${(c as { type: string }).type}'`);
}

// ---------------------------------------------------------------------------
// Explication validation (entry point)
// ---------------------------------------------------------------------------

export interface ValidationStats {
  readonly clauseCount: number; // all clause nodes, incl. quote/embedded
  readonly maxDepth: number;
  readonly referentCount: number;
}

export function validateExplication(e: Explication): ValidationStats {
  const path = '$';
  if (e.schema !== AST_SCHEMA) {
    fail('ERR_SCHEMA', `${path}.schema`, `expected '${AST_SCHEMA}', got '${String(e.schema)}'`);
  }
  if (!(EXPLICATION_FRAMES as readonly string[]).includes(e.frame)) {
    fail('ERR_FRAME', `${path}.frame`, `'${e.frame}' is not an explication frame (gist §4.6)`);
  }
  if (!Array.isArray(e.clauses) || e.clauses.length === 0) {
    fail('ERR_EMPTY', `${path}.clauses`, 'an explication must have at least one clause');
  }
  // Referent declarations: dense from 1, ≤32, closed kinds (gist §4.2).
  if (e.referents.length > CAPS.maxReferents) {
    fail('ERR_CAP_REFERENTS', `${path}.referents`, `${e.referents.length} referents exceeds cap ${CAPS.maxReferents}`);
  }
  const declared = new Map<number, string>();
  for (const [i, r] of e.referents.entries()) {
    if (r.index !== i + 1) {
      fail('ERR_REFERENT_INDICES', `${path}.referents[${i}]`, `indices must be dense from 1; expected ${i + 1}, got ${r.index}`);
    }
    if (!(REF_KINDS as readonly string[]).includes(r.refKind)) {
      fail('ERR_REF_KIND', `${path}.referents[${i}]`, `'${r.refKind}' is not a referent kind`);
    }
    declared.set(r.index, r.refKind);
  }
  const implicitCount = e.frame === 'RelationalSchema' ? 2 : 1;
  if (e.referents.length < implicitCount) {
    fail('ERR_REFERENT_INDICES', `${path}.referents`, `frame ${e.frame} implies ${implicitCount} referent(s); declare them (gist §4.6)`);
  }
  const ctx: Ctx = {
    declared,
    scopes: [{ introduced: new Set(), isQuote: false }],
    introducedAnywhere: new Set(),
    clauseCount: 0,
  };
  // Frame-implicit referents are introduced by the frame itself (gist §4.2).
  for (let i = 1; i <= implicitCount; i++) {
    ctx.introducedAnywhere.add(i);
    ctx.scopes[0]!.introduced.add(i);
  }
  maxDepthSeen.value = 0;
  for (const [i, c] of e.clauses.entries()) {
    validateClause(ctx, c, 1, `${path}.clauses[${i}]`);
  }
  // Every declared referent must have an introducing occurrence (gist §4.2).
  for (const idx of declared.keys()) {
    if (!ctx.introducedAnywhere.has(idx)) {
      fail('ERR_REF_NEVER_INTRODUCED', `${path}.referents`, `referent ${idx} declared but never introduced`);
    }
  }
  return {
    clauseCount: ctx.clauseCount,
    maxDepth: maxDepthSeen.value,
    referentCount: e.referents.length,
  };
}
