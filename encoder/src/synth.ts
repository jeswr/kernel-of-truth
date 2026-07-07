/**
 * Deterministic synthetic-explication generator + single-edit mutator for the
 * Phase-X property suites (poc-design.md X1: "every kernel-v0 explication and
 * a sample of synthetics, mutated by one operator flip / clause swap /
 * referent-index change / filler substitution").
 *
 * Determinism: everything is driven by an EXPLICIT caller seed through the
 * SHA-256 counter stream in det.ts (SeededRng) — no Math.random, identical
 * output on every platform. Generated explications are valid by construction
 * AND re-checked through the validation gates before being returned (fail
 * closed on generator bugs).
 *
 * GENERATOR VERSION: v2 (2026-07-07). v1 computed `canEmbedClause` once per
 * pred clause, but nested entity/SP generation could consume the remaining
 * clause budget before the quote/complement branches used that stale check —
 * overflowing the 32-clause cap at rare seeds (surfaced by the full X1 run,
 * ERR_CAP_CLAUSES). v2 consumes the budget ATOMICALLY at every embedding
 * site (`takeClause` / genQuote's own take), so the cap holds by
 * construction; see the 20k-seed regression test. v2's rng draw order
 * differs from v1, so synthetic corpora differ; the generator is OUTSIDE the
 * encoder content-hash pin (contentHash.ts covers {schema, algorithm, D,
 * codebook, weighting} only), and X0 goldens store ASTs inline, so both are
 * unaffected.
 */

import type {
  Clause,
  Explication,
  Filler,
  OpClause,
  PredClause,
  ReferentDecl,
  SP,
  SPHead,
  SPModifier,
} from './ast.js';
import { AST_SCHEMA, canonicalJson } from './ast.js';
import { SeededRng } from './det.js';
import {
  CAPS,
  DURATION_FILLERS,
  SP_DETERMINERS,
  SP_MODS,
  SP_QUANTIFIERS,
  SUBSTANTIVE_HEADS,
  type ExplicationFrame,
  type RefKind,
  type Role,
  type SPDeterminer,
  type SPQuantifier,
} from './lexicon.js';
import { validateExplication } from './validate.js';

export interface SynthOptions {
  /** Explicit seed (required; poc-design Phase X). */
  readonly seed: string;
  /** Top-level clause count (1..32; embedded clauses also draw on the global cap). */
  readonly topClauses: number;
  /** Target maximum structural depth (1..12); the first clause carries a depth spine. */
  readonly depth: number;
  /** Optional pool of concept ids to reference (requires vectors at encode time). */
  readonly conceptIds?: readonly string[];
}

interface GenCtx {
  readonly rng: SeededRng;
  readonly referents: ReferentDecl[];
  readonly introduced: number[]; // indices introduced so far, in document order (outer scope)
  clauseBudget: number;
  readonly conceptIds: readonly string[];
  inQuote: boolean;
}

const SOMEONE_HEADS = ['SOMEONE', 'PEOPLE'] as const;
const THING_HEADS = ['SOMETHING~THING', 'BODY', 'WORDS'] as const;
const TIME_HEADS = ['WHEN~TIME', 'MOMENT'] as const;
const PLACE_HEADS = ['WHERE~PLACE', 'SIDE'] as const;

function kindForHead(prime: string): RefKind {
  if ((SOMEONE_HEADS as readonly string[]).includes(prime) || prime === 'I' || prime === 'YOU') return 'SomeoneRef';
  if ((TIME_HEADS as readonly string[]).includes(prime)) return 'TimeRef';
  if ((PLACE_HEADS as readonly string[]).includes(prime)) return 'PlaceRef';
  if (prime === 'WORDS') return 'ClauseRef';
  return 'SomethingRef';
}

// ---------------------------------------------------------------------------
// Generator core.
//
// DEPTH DISCIPLINE: every generator function takes `dl` = the number of
// structural levels available for the node it generates, mirroring the
// validator's depth accounting EXACTLY (validate.ts): a clause's SP fillers
// sit one level below it (need dl >= 2 -> genSP(dl-1)); embedded clauses,
// quote bodies, temporal anchors and SP `restrictedBy`/`of` likewise consume
// one level. This makes SynthOptions.depth the true measured structural
// depth (X2 bins by it), not a loose target.
// ---------------------------------------------------------------------------

function genSP(ctx: GenCtx, dl: number, allowBind: boolean): SP {
  if (dl < 1) throw new Error('ERR_SYNTH: genSP called with no depth budget');
  const rng = ctx.rng;
  const headPrime = rng.pick(SUBSTANTIVE_HEADS);
  let head: SPHead = { kind: 'primeHead', prime: headPrime };
  if (dl >= 2 && rng.bool(0.15)) {
    // KIND/PART frame: of-SP sits one level deeper (validate.ts §4.3 walk).
    const of: SP = genSP(ctx, dl - 1, false);
    head = { kind: rng.bool(0.5) ? 'kindFrame' : 'partFrame', of };
  } else if (ctx.conceptIds.length > 0 && rng.bool(0.15)) {
    head = { kind: 'conceptHead', id: rng.pick(ctx.conceptIds) };
  } else if (ctx.introduced.length > 0 && rng.bool(0.2)) {
    head = { kind: 'refHead', index: rng.pick(ctx.introduced) };
  }
  const sp: {
    kind: 'sp';
    det?: SPDeterminer;
    quant?: SPQuantifier;
    mods?: SPModifier[];
    head: SPHead;
    restrictedBy?: Clause;
    bind?: number;
  } = { kind: 'sp', head };
  if (rng.bool(0.35)) sp.det = rng.pick(SP_DETERMINERS);
  if (sp.det === undefined && rng.bool(0.3)) sp.quant = rng.pick(SP_QUANTIFIERS);
  if (rng.bool(0.3)) {
    const mod: SPModifier = rng.bool(0.3)
      ? { mod: rng.pick(SP_MODS), intensifier: rng.bool(0.7) ? 'VERY' : 'MORE' }
      : { mod: rng.pick(SP_MODS) };
    sp.mods = [mod];
  }
  if (
    allowBind &&
    !ctx.inQuote &&
    head.kind === 'primeHead' &&
    ctx.referents.length < CAPS.maxReferents &&
    rng.bool(0.4)
  ) {
    const index = ctx.referents.length + 1;
    ctx.referents.push({ index, refKind: kindForHead(head.prime) });
    ctx.introduced.push(index);
    sp.bind = index;
  }
  if (dl >= 2 && rng.bool(0.15) && takeClause(ctx)) {
    sp.restrictedBy = genPredClause(ctx, dl - 1); // restricting clause one level deeper
  }
  return sp;
}

/** Entity filler: SP (needs dl >= 2), ref, concept, or indexical I/YOU. */
function genEntity(ctx: GenCtx, dl: number): Filler {
  const rng = ctx.rng;
  if (ctx.introduced.length > 0 && rng.bool(dl >= 2 ? 0.35 : 0.6)) {
    return { kind: 'ref', index: rng.pick(ctx.introduced) };
  }
  if (ctx.conceptIds.length > 0 && rng.bool(0.1)) {
    return { kind: 'concept', id: rng.pick(ctx.conceptIds) };
  }
  if (dl >= 2) return genSP(ctx, dl - 1, true);
  // No depth left for an SP: indexical entity filler (gist §4.5).
  return { kind: 'prime', prime: rng.bool(0.5) ? 'I' : 'YOU' };
}

/** Atomically consume one embedded-clause slot from the global 32-clause budget. */
function takeClause(ctx: GenCtx): boolean {
  if (ctx.clauseBudget < 1) return false;
  ctx.clauseBudget -= 1;
  return true;
}

/**
 * Quote body: clauses sit one level below the carrying clause (validate.ts).
 * Returns null when the clause budget is exhausted — the budget is taken
 * HERE, at consumption time, never against a caller's stale check (v2).
 */
function genQuote(ctx: GenCtx, dl: number): Filler | null {
  const rng = ctx.rng;
  const want = rng.bool(0.5) ? 1 : 2;
  const n = Math.min(ctx.clauseBudget, want);
  if (n < 1) return null;
  ctx.clauseBudget -= n;
  const wasInQuote = ctx.inQuote;
  ctx.inQuote = true;
  const clauses: Clause[] = [];
  for (let i = 0; i < n; i++) clauses.push(genPredClause(ctx, dl - 1));
  ctx.inQuote = wasInQuote;
  return { kind: 'quote', clauses };
}

function genTimeAdjunct(ctx: GenCtx, dl: number): Filler {
  const rng = ctx.rng;
  if (dl < 2 || rng.bool(0.4)) return { kind: 'prime', prime: 'NOW' };
  if (rng.bool(0.4)) {
    return {
      kind: 'temporal',
      op: rng.bool(0.5) ? 'AFTER' : 'BEFORE',
      anchor:
        rng.bool(0.6) || dl < 3
          ? { kind: 'prime', prime: 'NOW' }
          : { kind: 'sp', head: { kind: 'primeHead', prime: 'WHEN~TIME' }, det: 'THIS' },
    };
  }
  const timeRefs = ctx.referents.filter((r) => r.refKind === 'TimeRef' && ctx.introduced.includes(r.index));
  if (timeRefs.length > 0 && rng.bool(0.5)) return { kind: 'ref', index: rng.pick(timeRefs).index };
  return genSP(ctx, dl - 1, true);
}

function genPredClause(ctx: GenCtx, dl: number): PredClause {
  const rng = ctx.rng;
  const roles: Partial<Record<Role, Filler>> = {};
  // NOTE (v2): this is only an ADVISORY snapshot for predicate choice; every
  // embedding site below re-takes the budget atomically at consumption time
  // (nested entity/SP generation in between may spend it — the v1 overflow).
  const canEmbedClause = dl >= 2 && ctx.clauseBudget > 0; // embedded clause / quote body
  const canSP = dl >= 2;
  const preds: string[] = [
    'DO', 'DO', 'HAPPEN', 'MOVE', 'FEEL', 'SEE', 'HEAR', 'SAY',
    'BE-SOMEWHERE', 'THERE-IS', 'LIVE', 'DIE', 'THINK', 'WANT', "DON'T-WANT",
    ...(canSP ? ['BE-SPEC'] : []), // BE-SPEC attribute needs an SP
    ...(canEmbedClause ? ['KNOW', 'TRUE'] : []),
  ];
  const pred = rng.pick(preds);
  switch (pred) {
    case 'DO':
      roles.agent = genEntity(ctx, dl);
      if (rng.bool(0.7)) roles.undergoer = genEntity(ctx, dl);
      if (rng.bool(0.15)) roles.instrument = genEntity(ctx, Math.min(dl, 2));
      if (rng.bool(0.1)) roles.comitative = genEntity(ctx, Math.min(dl, 2));
      break;
    case 'HAPPEN':
      if (rng.bool(0.8)) roles.undergoer = genEntity(ctx, dl);
      break;
    case 'MOVE':
    case 'THERE-IS':
    case 'LIVE':
    case 'DIE':
      roles.undergoer = genEntity(ctx, dl);
      break;
    case 'THINK': {
      roles.experiencer = genEntity(ctx, dl);
      if (rng.bool(0.4)) roles.topic = genEntity(ctx, Math.min(dl, 2));
      if (dl >= 2 && rng.bool(0.4)) {
        const q = genQuote(ctx, dl); // takes the budget itself; null if spent
        if (q !== null) roles.quote = q;
      }
      break;
    }
    case 'KNOW':
      roles.experiencer = genEntity(ctx, dl);
      if (dl >= 2 && rng.bool(0.7) && takeClause(ctx)) {
        roles.complement = { kind: 'clause', clause: genPredClause(ctx, dl - 1) };
      } else if (rng.bool(0.5)) roles.topic = genEntity(ctx, Math.min(dl, 2));
      break;
    case 'WANT':
    case "DON'T-WANT":
      roles.experiencer = genEntity(ctx, dl);
      if (dl >= 2 && rng.bool(0.5) && takeClause(ctx)) {
        roles.complement = { kind: 'clause', clause: genPredClause(ctx, dl - 1) };
      } else {
        roles.complement = genEntity(ctx, Math.min(dl, 2));
      }
      break;
    case 'FEEL':
      roles.experiencer = genEntity(ctx, dl);
      if (rng.bool(0.7)) roles.attribute = { kind: 'prime', prime: rng.bool(0.5) ? 'GOOD' : 'BAD' };
      break;
    case 'SEE':
    case 'HEAR':
      roles.experiencer = genEntity(ctx, dl);
      roles.stimulus = genEntity(ctx, dl);
      break;
    case 'SAY': {
      roles.agent = genEntity(ctx, dl);
      if (rng.bool(0.3)) roles.addressee = genEntity(ctx, Math.min(dl, 2));
      let saidQuote = false;
      if (dl >= 2 && rng.bool(0.4)) {
        const q = genQuote(ctx, dl);
        if (q !== null) {
          roles.quote = q;
          saidQuote = true;
        }
      }
      if (!saidQuote && rng.bool(0.4)) roles.topic = genEntity(ctx, Math.min(dl, 2));
      break;
    }
    case 'TRUE': {
      const clauseRefs = ctx.referents.filter(
        (r) => r.refKind === 'ClauseRef' && ctx.introduced.includes(r.index),
      );
      if (clauseRefs.length > 0 && rng.bool(0.6)) {
        roles.undergoer = { kind: 'ref', index: rng.pick(clauseRefs).index };
      } else {
        const q = genQuote(ctx, dl);
        if (q !== null) {
          roles.undergoer = q;
        } else if (clauseRefs.length > 0) {
          roles.undergoer = { kind: 'ref', index: rng.pick(clauseRefs).index };
        } else {
          // Budget exhausted between predicate choice and here and no
          // ClauseRef in scope: TRUE cannot be realised — emit a budget-free
          // clause instead (valid by construction).
          return { type: 'pred', pred: 'HAPPEN', roles: { undergoer: genEntity(ctx, dl) } };
        }
      }
      break;
    }
    case 'BE-SOMEWHERE':
      roles.undergoer = genEntity(ctx, dl);
      roles.locus = canSP
        ? genSP(ctx, dl - 1, true)
        : ctx.introduced.length > 0
          ? { kind: 'ref', index: rng.pick(ctx.introduced) }
          : { kind: 'prime', prime: 'I' };
      break;
    case 'BE-SPEC':
      roles.undergoer = genEntity(ctx, dl);
      roles.attribute = genSP(ctx, dl - 1, false);
      break;
    default:
      throw new Error(`ERR_SYNTH: unhandled predicate ${pred}`);
  }
  // Adjuncts (kept within the depth budget).
  if (rng.bool(0.25)) roles.time = genTimeAdjunct(ctx, dl);
  if (rng.bool(0.12)) roles.duration = { kind: 'prime', prime: rng.pick(DURATION_FILLERS) };
  if (rng.bool(0.12)) {
    roles.place = !canSP || rng.bool(0.5) ? { kind: 'prime', prime: 'HERE' } : genSP(ctx, dl - 1, true);
  }
  if (rng.bool(0.08)) roles.manner = { kind: 'prime', prime: 'LIKE~AS~WAY' };
  return { type: 'pred', pred, roles };
}

function genOpClause(ctx: GenCtx, dl: number): OpClause {
  const rng = ctx.rng;
  // Budget checks and decrements below are ADJACENT (no nested generation in
  // between), so they are atomic in the takeClause sense.
  const two = dl >= 2 && ctx.clauseBudget >= 2 && rng.bool(0.4);
  if (two) {
    const op = rng.pick(['IF', 'BECAUSE', 'WHEN'] as const);
    ctx.clauseBudget -= 2;
    return { type: 'op', op, args: [genClause(ctx, dl - 1), genClause(ctx, dl - 1)] };
  }
  if (dl >= 2 && ctx.clauseBudget >= 1 && rng.bool(0.85)) {
    if (rng.bool(0.25)) {
      const op = rng.bool(0.5) ? 'AFTER' : 'BEFORE';
      ctx.clauseBudget -= 1;
      return { type: 'op', op, args: [{ kind: 'prime', prime: 'NOW' }, genClause(ctx, dl - 1)] };
    }
    const op = rng.pick(['NOT', 'CAN', 'MAYBE'] as const);
    ctx.clauseBudget -= 1;
    return { type: 'op', op, args: [genClause(ctx, dl - 1)] };
  }
  // Degenerate mod-scope operators (rare, but part of the closed grammar).
  if (rng.bool(0.5)) return { type: 'op', op: 'VERY', args: [{ kind: 'prime', prime: rng.pick(SP_MODS) }] };
  return { type: 'op', op: 'MORE', args: [{ kind: 'prime', prime: rng.pick(SP_MODS) }] };
}

function genClause(ctx: GenCtx, dl: number): Clause {
  if (dl >= 2 && ctx.clauseBudget >= 1 && ctx.rng.bool(0.3)) return genOpClause(ctx, dl);
  return genPredClause(ctx, dl);
}

/**
 * Depth spine: a chain of clause nesting reaching structural depth exactly
 * `depth` (wrappers use the frame-implicit referent 1 so intermediate levels
 * add no SP depth; the innermost clause is atomic-filler-only).
 */
function genSpine(ctx: GenCtx, depth: number): Clause {
  const rng = ctx.rng;
  if (depth <= 1) {
    // Innermost: atomic fillers only (structural depth = clause depth).
    const pick = rng.int(4);
    const ref1: Filler = { kind: 'ref', index: 1 };
    if (pick === 0) return { type: 'pred', pred: 'LIVE', roles: { undergoer: ref1 } };
    if (pick === 1) {
      return {
        type: 'pred',
        pred: 'FEEL',
        roles: { experiencer: ref1, attribute: { kind: 'prime', prime: rng.bool(0.5) ? 'GOOD' : 'BAD' } },
      };
    }
    if (pick === 2) return { type: 'pred', pred: 'SEE', roles: { experiencer: ref1, stimulus: { kind: 'prime', prime: 'YOU' } } };
    return { type: 'pred', pred: 'DO', roles: { agent: ref1, undergoer: { kind: 'prime', prime: 'I' } } };
  }
  ctx.clauseBudget -= 1;
  const choice = rng.int(3);
  if (choice === 0) {
    return { type: 'op', op: rng.pick(['NOT', 'CAN', 'MAYBE'] as const), args: [genSpine(ctx, depth - 1)] };
  }
  const pred = choice === 1 ? 'KNOW' : 'WANT';
  return {
    type: 'pred',
    pred,
    roles: {
      experiencer: { kind: 'ref', index: 1 },
      complement: { kind: 'clause', clause: genSpine(ctx, depth - 1) },
    },
  };
}

export function generateExplication(opts: SynthOptions): Explication {
  if (opts.topClauses < 1 || opts.topClauses > CAPS.maxClauses) {
    throw new Error(`ERR_SYNTH: topClauses must be 1..${CAPS.maxClauses}`);
  }
  if (opts.depth < 1 || opts.depth > CAPS.maxDepth) {
    throw new Error(`ERR_SYNTH: depth must be 1..${CAPS.maxDepth}`);
  }
  if (opts.depth - 1 > CAPS.maxClauses - opts.topClauses) {
    throw new Error(
      `ERR_SYNTH: depth ${opts.depth} needs ${opts.depth - 1} embedded clauses; only ${CAPS.maxClauses - opts.topClauses} available beside ${opts.topClauses} top clauses`,
    );
  }
  const rng = new SeededRng(opts.seed);
  const frame: ExplicationFrame = rng.bool(0.6)
    ? 'InstanceSchema'
    : rng.bool(0.5)
      ? 'WhenTrue'
      : 'RelationalSchema';
  const referents: ReferentDecl[] = [{ index: 1, refKind: rng.bool(0.4) ? 'SomeoneRef' : 'SomethingRef' }];
  const introduced = [1];
  if (frame === 'RelationalSchema') {
    referents.push({ index: 2, refKind: rng.bool(0.5) ? 'SomeoneRef' : 'SomethingRef' });
    introduced.push(2);
  }
  const ctx: GenCtx = {
    rng,
    referents,
    introduced,
    clauseBudget: CAPS.maxClauses - opts.topClauses, // embedded-clause budget
    conceptIds: opts.conceptIds ?? [],
    inQuote: false,
  };
  const clauses: Clause[] = [];
  // First clause carries the depth spine (consumes depth-1 embedded clauses).
  clauses.push(opts.depth > 1 ? genSpine(ctx, opts.depth) : genPredClause(ctx, 1));
  for (let i = 1; i < opts.topClauses; i++) {
    clauses.push(genClause(ctx, Math.max(1, Math.min(opts.depth, 3))));
  }
  const e: Explication = { schema: AST_SCHEMA, frame, referents, clauses };
  validateExplication(e); // fail closed on generator bugs
  return e;
}

// ---------------------------------------------------------------------------
// Single-edit mutator (X1 adversarial suite)
// ---------------------------------------------------------------------------

export type EditType = 'operator-flip' | 'clause-swap' | 'referent-index' | 'filler-substitution';

export interface Mutation {
  readonly mutant: Explication;
  readonly edit: EditType;
  /** Human-readable description of the specific edit, for the X1 report. */
  readonly detail: string;
}

type Mutable = { [k: string]: unknown };

interface CandidateEdit {
  readonly type: EditType;
  readonly detail: string;
  apply(root: Explication): void; // mutates a deep clone in place
}

function deepClone<T>(x: T): T {
  return JSON.parse(JSON.stringify(x)) as T;
}

/** Walk every node, calling visit with (node, containerPathDescription). */
function collectEdits(e: Explication, rng: SeededRng): CandidateEdit[] {
  const edits: CandidateEdit[] = [];
  const opFlips: Record<string, readonly string[]> = {
    NOT: ['CAN', 'MAYBE'],
    CAN: ['NOT', 'MAYBE'],
    MAYBE: ['NOT', 'CAN'],
    IF: ['BECAUSE', 'WHEN'],
    BECAUSE: ['IF', 'WHEN'],
    WHEN: ['IF', 'BECAUSE'],
    AFTER: ['BEFORE'],
    BEFORE: ['AFTER'],
    VERY: ['MORE'],
    MORE: ['VERY'],
  };
  const predFlips: Record<string, readonly string[]> = {
    SEE: ['HEAR'],
    HEAR: ['SEE'],
    WANT: ["DON'T-WANT"],
    "DON'T-WANT": ['WANT'],
    LIVE: ['DIE'],
    DIE: ['LIVE'],
    MOVE: ['THERE-IS'],
    'THERE-IS': ['MOVE'],
  };

  // Resolve a node inside a clone by path of keys/indices.
  const resolve = (root: unknown, path: (string | number)[]): Mutable => {
    let cur = root as Mutable;
    for (const k of path) cur = cur[k as string] as Mutable;
    return cur;
  };

  const visitFiller = (f: Filler, path: (string | number)[]): void => {
    switch (f.kind) {
      case 'sp':
        visitSP(f, path);
        return;
      case 'ref':
        edits.push({
          type: 'referent-index',
          detail: `ref ${f.index} at ${path.join('.')}`,
          apply(root) {
            const node = resolve(root, path);
            const declared = (root.referents as ReferentDecl[]).map((r) => r.index).filter((i) => i !== f.index);
            if (declared.length === 0) throw new Error('inapplicable');
            node.index = declared[rng.int(declared.length)]!;
          },
        });
        return;
      case 'prime': {
        const cls =
          (SP_MODS as readonly string[]).includes(f.prime) ? SP_MODS
          : (DURATION_FILLERS as readonly string[]).includes(f.prime) ? DURATION_FILLERS
          : null;
        if (cls !== null) {
          const alts = cls.filter((x) => x !== f.prime);
          edits.push({
            type: 'filler-substitution',
            detail: `prime ${f.prime} at ${path.join('.')}`,
            apply(root) {
              resolve(root, path).prime = alts[rng.int(alts.length)]!;
            },
          });
        }
        return;
      }
      case 'clause':
        visitClause(f.clause, [...path, 'clause']);
        return;
      case 'quote': {
        visitClauseList(f.clauses, [...path, 'clauses']);
        return;
      }
      case 'temporal': {
        edits.push({
          type: 'operator-flip',
          detail: `temporal ${f.op} at ${path.join('.')}`,
          apply(root) {
            const node = resolve(root, path);
            node.op = f.op === 'AFTER' ? 'BEFORE' : 'AFTER';
          },
        });
        if (f.anchor.kind === 'sp') visitSP(f.anchor, [...path, 'anchor']);
        return;
      }
      default:
        return;
    }
  };

  const visitSP = (sp: SP, path: (string | number)[]): void => {
    if (sp.head.kind === 'primeHead') {
      const alts = SUBSTANTIVE_HEADS.filter((h) => h !== (sp.head as { prime: string }).prime);
      edits.push({
        type: 'filler-substitution',
        detail: `head ${sp.head.prime} at ${path.join('.')}`,
        apply(root) {
          resolve(root, [...path, 'head']).prime = alts[rng.int(alts.length)]!;
        },
      });
    } else if (sp.head.kind === 'refHead') {
      const idx = sp.head.index;
      edits.push({
        type: 'referent-index',
        detail: `refHead ${idx} at ${path.join('.')}`,
        apply(root) {
          const declared = (root.referents as ReferentDecl[]).map((r) => r.index).filter((i) => i !== idx);
          if (declared.length === 0) throw new Error('inapplicable');
          resolve(root, [...path, 'head']).index = declared[rng.int(declared.length)]!;
        },
      });
    } else if (sp.head.kind === 'kindFrame' || sp.head.kind === 'partFrame') {
      const of = sp.head.of;
      if (of.kind === 'sp') visitSP(of, [...path, 'head', 'of']);
      else if (of.kind === 'ref') visitFiller(of, [...path, 'head', 'of']);
    }
    if (sp.det !== undefined) {
      const alts = SP_DETERMINERS.filter((d) => d !== sp.det);
      edits.push({
        type: 'filler-substitution',
        detail: `det ${sp.det} at ${path.join('.')}`,
        apply(root) {
          resolve(root, path).det = alts[rng.int(alts.length)]!;
        },
      });
    }
    if (sp.quant !== undefined) {
      const alts = SP_QUANTIFIERS.filter((q) => q !== sp.quant);
      edits.push({
        type: 'filler-substitution',
        detail: `quant ${sp.quant} at ${path.join('.')}`,
        apply(root) {
          resolve(root, path).quant = alts[rng.int(alts.length)]!;
        },
      });
    }
    for (const [i, m] of (sp.mods ?? []).entries()) {
      const alts = SP_MODS.filter((x) => x !== m.mod);
      edits.push({
        type: 'filler-substitution',
        detail: `mod ${m.mod} at ${path.join('.')}`,
        apply(root) {
          resolve(root, [...path, 'mods', i]).mod = alts[rng.int(alts.length)]!;
        },
      });
    }
    if (sp.restrictedBy !== undefined) visitClause(sp.restrictedBy, [...path, 'restrictedBy']);
  };

  const visitClause = (c: Clause, path: (string | number)[]): void => {
    if (c.type === 'pred') {
      const flips = predFlips[c.pred];
      if (flips !== undefined) {
        edits.push({
          type: 'filler-substitution',
          detail: `pred ${c.pred} at ${path.join('.')}`,
          apply(root) {
            resolve(root, path).pred = flips[rng.int(flips.length)]!;
          },
        });
      }
      for (const [role, f] of Object.entries(c.roles)) {
        if (f !== undefined) visitFiller(f as Filler, [...path, 'roles', role]);
      }
    } else {
      const flips = opFlips[c.op];
      if (flips !== undefined && flips.length > 0) {
        edits.push({
          type: 'operator-flip',
          detail: `op ${c.op} at ${path.join('.')}`,
          apply(root) {
            resolve(root, path).op = flips[rng.int(flips.length)]!;
          },
        });
      }
      for (const [i, a] of c.args.entries()) {
        if ('type' in a) visitClause(a, [...path, 'args', i]);
        else visitFiller(a, [...path, 'args', i]);
      }
    }
  };

  const visitClauseList = (clauses: readonly Clause[], path: (string | number)[]): void => {
    for (let i = 0; i + 1 < clauses.length; i++) {
      edits.push({
        type: 'clause-swap',
        detail: `swap clauses ${i} and ${i + 1} at ${path.join('.')}`,
        apply(root) {
          const list = resolve(root, path.slice(0, -1))[path[path.length - 1] as string] as Clause[];
          const t = list[i]!;
          list[i] = list[i + 1]!;
          list[i + 1] = t;
        },
      });
    }
    for (const [i, c] of clauses.entries()) visitClause(c, [...path, i]);
  };

  visitClauseList(e.clauses, ['clauses']);
  return edits;
}

/**
 * Apply exactly one validity-preserving single edit. Deterministic in
 * (explication, seed). Returns null if no applicable edit yields a valid,
 * different explication (rare; callers should skip such items and report).
 */
export function mutateExplication(e: Explication, seed: string): Mutation | null {
  const rng = new SeededRng(seed);
  const edits = collectEdits(e, rng);
  // Deterministic shuffle of candidate order.
  for (let i = edits.length - 1; i > 0; i--) {
    const j = rng.int(i + 1);
    const t = edits[i]!;
    edits[i] = edits[j]!;
    edits[j] = t;
  }
  const original = canonicalJson(e);
  for (const edit of edits) {
    const clone = deepClone(e);
    try {
      edit.apply(clone);
      if (canonicalJson(clone) === original) continue; // must differ
      validateExplication(clone); // must stay valid
      return { mutant: clone, edit: edit.type, detail: edit.detail };
    } catch {
      continue; // inapplicable or validity-breaking; try next
    }
  }
  return null;
}
