/**
 * Deterministic record->text renderer + exact inverse parser — canonical-form
 * v0 for the invented-composite dictionary and the roll-up round-trip
 * property suite (idea B, docs/next/io-compression-ideas.md §3.3; shared-seat
 * artefact with the precision-linter rewrite mode, docs/next/kernel-precision-linter.md
 * §8.2).
 *
 * STIPULATED (surface form): this is a compact keyword surface ("canonical-form
 * v0"), one canonical rendering per AST shape, chosen for exact invertibility.
 * A Minimal-English-readable template surface may replace it later without
 * touching the property being guarded here: parseRendered(renderExplication(e))
 * must be the IDENTITY on every valid kot-ast/1 explication (bar: 100% — any
 * failure is a bug, io-compression-ideas.md §3.3).
 *
 * Surface grammar (canonical-form v0):
 *
 *   explication := frameword ' refs[' refdecl (',' refdecl)* '] { ' clauses ' }'
 *   frameword   := 'instance' | 'when-true' | 'relational'
 *   refdecl     := 'x' INT ':' ('someone'|'something'|'time'|'place'|'clause')
 *   clauses     := clause (' ; ' clause)*
 *   clause      := '@' opword '(' oparg (', ' oparg)* ')'          -- OpClause
 *                | predword '(' role '=' filler (', ' ...)* ')'    -- PredClause
 *                | predword '()'                                   -- no roles
 *   oparg       := clause | filler
 *   filler      := sp | 'x' INT | '#' PRIME | '<' id '>' | '{ ' clause ' }'
 *                | 'q{ ' clause (' ; ' clause)* ' }'
 *                | ('after'|'before') '@' (sp | 'x' INT | '#' PRIME)
 *   sp          := '[' ('d:' det ' ')? ('q:' quant ' ')? ('m:' mod ' ')* head
 *                  (' !' INT)? (' | ' clause)? ']'
 *   head        := PRIME | 'x' INT | '<' id '>'
 *                | ('kind-of'|'part-of') '(' (sp | 'x' INT | '<' id '>') ')'
 *
 * PRIME names appear verbatim (uppercase, may contain ~ ' -); all keywords
 * are lowercase, so the two never collide. Concept ids appear inside <...>
 * with '\' and '>' backslash-escaped. Everything fails closed (ERR_RENDER_* /
 * ERR_PARSE_*): no silent fallbacks, per the programme quality bar.
 */

import type {
  Clause,
  Explication,
  Filler,
  OpArg,
  OpClause,
  PredClause,
  ReferentDecl,
  SP,
  SPHead,
  SPModifier,
} from './ast.js';
import { AST_SCHEMA } from './ast.js';
import {
  OPERATORS,
  PRIME_BY_NAME,
  PREDICATE_FRAMES,
  ROLES,
  SP_DETERMINERS,
  SP_MODS,
  SP_QUANTIFIERS,
  type ExplicationFrame,
  type Operator,
  type RefKind,
  type Role,
  type SPDeterminer,
  type SPMod,
  type SPQuantifier,
} from './lexicon.js';

// ---------------------------------------------------------------------------
// Closed word tables (renderer direction = value->word; parser inverts them).
// ---------------------------------------------------------------------------

const FRAME_WORD: Readonly<Record<ExplicationFrame, string>> = {
  InstanceSchema: 'instance',
  WhenTrue: 'when-true',
  RelationalSchema: 'relational',
};

const REFKIND_WORD: Readonly<Record<RefKind, string>> = {
  SomeoneRef: 'someone',
  SomethingRef: 'something',
  TimeRef: 'time',
  PlaceRef: 'place',
  ClauseRef: 'clause',
};

const DET_WORD: Readonly<Record<SPDeterminer, string>> = {
  THIS: 'this',
  'THE-SAME': 'the-same',
  'OTHER~ELSE~ANOTHER': 'other',
  SOME: 'some',
};

const QUANT_WORD: Readonly<Record<SPQuantifier, string>> = {
  ONE: 'one',
  TWO: 'two',
  SOME: 'some',
  ALL: 'all',
  'MUCH~MANY': 'many',
  'LITTLE~FEW': 'few',
};

const MOD_WORD: Readonly<Record<SPMod, string>> = {
  GOOD: 'good',
  BAD: 'bad',
  BIG: 'big',
  SMALL: 'small',
};

/** Lowercased operator / predicate keywords (names are already unambiguous). */
const OP_WORD = new Map<Operator, string>(OPERATORS.map((op) => [op, op.toLowerCase()]));
const PRED_WORD = new Map<string, string>(PREDICATE_FRAMES.map((f) => [f.pred, f.pred.toLowerCase()]));

function invert<K extends string>(rec: Readonly<Record<K, string>>): Map<string, K> {
  const m = new Map<string, K>();
  for (const k of Object.keys(rec) as K[]) {
    const w = rec[k];
    if (m.has(w)) throw new Error(`ERR_RENDER_TABLE: duplicate surface word '${w}'`);
    m.set(w, k);
  }
  return m;
}

const WORD_FRAME = invert(FRAME_WORD);
const WORD_REFKIND = invert(REFKIND_WORD);
const WORD_DET = invert(DET_WORD);
const WORD_QUANT = invert(QUANT_WORD);
const WORD_MOD = invert(MOD_WORD);
const WORD_OP = new Map<string, Operator>([...OP_WORD].map(([k, v]) => [v, k]));
const WORD_PRED = new Map<string, string>([...PRED_WORD].map(([k, v]) => [v, k]));

// ---------------------------------------------------------------------------
// Renderer
// ---------------------------------------------------------------------------

const err = (code: string, detail: string): never => {
  throw new Error(`${code}: ${detail}`);
};

function escapeId(id: string): string {
  return id.replace(/\\/g, '\\\\').replace(/>/g, '\\>');
}

function renderSPHead(h: SPHead): string {
  switch (h.kind) {
    case 'primeHead':
      return h.prime;
    case 'refHead':
      return `x${h.index}`;
    case 'conceptHead':
      return `<${escapeId(h.id)}>`;
    case 'kindFrame':
    case 'partFrame': {
      const kw = h.kind === 'kindFrame' ? 'kind-of' : 'part-of';
      const of = h.of;
      const inner =
        of.kind === 'sp' ? renderSP(of) : of.kind === 'ref' ? `x${of.index}` : `<${escapeId(of.id)}>`;
      return `${kw}(${inner})`;
    }
    default:
      return err('ERR_RENDER_HEAD', `unknown SP head kind '${(h as { kind: string }).kind}'`);
  }
}

function renderMod(m: SPModifier): string {
  const base = MOD_WORD[m.mod] ?? err('ERR_RENDER_MOD', `unknown mod '${m.mod}'`);
  if (m.intensifier === undefined) return `m:${base}`;
  return `m:${m.intensifier === 'VERY' ? 'very' : 'more'}.${base}`;
}

function renderSP(sp: SP): string {
  const parts: string[] = [];
  if (sp.det !== undefined) parts.push(`d:${DET_WORD[sp.det] ?? err('ERR_RENDER_DET', sp.det)}`);
  if (sp.quant !== undefined) parts.push(`q:${QUANT_WORD[sp.quant] ?? err('ERR_RENDER_QUANT', sp.quant)}`);
  for (const m of sp.mods ?? []) parts.push(renderMod(m));
  parts.push(renderSPHead(sp.head));
  if (sp.bind !== undefined) parts.push(`!${sp.bind}`);
  let body = parts.join(' ');
  if (sp.restrictedBy !== undefined) body += ` | ${renderClause(sp.restrictedBy)}`;
  return `[${body}]`;
}

function renderFiller(f: Filler): string {
  switch (f.kind) {
    case 'sp':
      return renderSP(f);
    case 'ref':
      return `x${f.index}`;
    case 'prime':
      return `#${f.prime}`;
    case 'concept':
      return `<${escapeId(f.id)}>`;
    case 'clause':
      return `{ ${renderClause(f.clause)} }`;
    case 'quote':
      return `q{ ${f.clauses.map(renderClause).join(' ; ')} }`;
    case 'temporal': {
      const a = f.anchor;
      const anchor = a.kind === 'sp' ? renderSP(a) : a.kind === 'ref' ? `x${a.index}` : `#${a.prime}`;
      return `${f.op === 'AFTER' ? 'after' : 'before'}@${anchor}`;
    }
    default:
      return err('ERR_RENDER_FILLER', `unknown filler kind '${(f as { kind: string }).kind}'`);
  }
}

function renderOpArg(a: OpArg): string {
  return 'type' in a ? renderClause(a) : renderFiller(a);
}

function renderClause(c: Clause): string {
  if (c.type === 'op') {
    const w = OP_WORD.get(c.op) ?? err('ERR_RENDER_OP', `unknown operator '${c.op}'`);
    return `@${w}(${c.args.map(renderOpArg).join(', ')})`;
  }
  if (c.type === 'pred') {
    const w = PRED_WORD.get(c.pred) ?? err('ERR_RENDER_PRED', `unknown predicate '${c.pred}'`);
    // Canonical role order = the fixed ROLES order (lexicon.ts), matching the
    // validator's deterministic walk.
    const parts: string[] = [];
    for (const role of ROLES) {
      const f = c.roles[role];
      if (f === undefined) continue;
      parts.push(`${role}=${renderFiller(f)}`);
    }
    return `${w}(${parts.join(', ')})`;
  }
  return err('ERR_RENDER_CLAUSE', `unknown clause type '${(c as { type: string }).type}'`);
}

/** Render a valid explication to canonical-form v0 text (deterministic). */
export function renderExplication(e: Explication): string {
  const frame = FRAME_WORD[e.frame] ?? err('ERR_RENDER_FRAME', String(e.frame));
  const refs = e.referents
    .map((r) => `x${r.index}:${REFKIND_WORD[r.refKind] ?? err('ERR_RENDER_REFKIND', r.refKind)}`)
    .join(',');
  const clauses = e.clauses.map(renderClause).join(' ; ');
  return `${frame} refs[${refs}] { ${clauses} }`;
}

// ---------------------------------------------------------------------------
// Tokenizer (parser direction)
// ---------------------------------------------------------------------------

type Tok =
  | { readonly t: 'punct'; readonly v: string }
  | { readonly t: 'word'; readonly v: string }
  | { readonly t: 'id'; readonly v: string }; // concept id, already unescaped

const PUNCT = new Set(['{', '}', '[', ']', '(', ')', ',', ';', '=', '!', '|', '@', '#', ':']);
const WORD_RE = /[A-Za-z0-9'~.\-]/;

function tokenize(text: string): Tok[] {
  const toks: Tok[] = [];
  let i = 0;
  while (i < text.length) {
    const ch = text[i]!;
    if (ch === ' ' || ch === '\t' || ch === '\n' || ch === '\r') {
      i++;
      continue;
    }
    if (ch === '<') {
      // Concept id: raw until unescaped '>'.
      i++;
      let id = '';
      let closed = false;
      while (i < text.length) {
        const c = text[i]!;
        if (c === '\\') {
          const n = text[i + 1];
          if (n !== '\\' && n !== '>') err('ERR_PARSE_ID', `bad escape '\\${n ?? ''}' at ${i}`);
          id += n!;
          i += 2;
          continue;
        }
        if (c === '>') {
          closed = true;
          i++;
          break;
        }
        id += c;
        i++;
      }
      if (!closed) err('ERR_PARSE_ID', 'unterminated concept id');
      toks.push({ t: 'id', v: id });
      continue;
    }
    if (PUNCT.has(ch)) {
      toks.push({ t: 'punct', v: ch });
      i++;
      continue;
    }
    if (WORD_RE.test(ch)) {
      let w = '';
      while (i < text.length && WORD_RE.test(text[i]!)) {
        w += text[i]!;
        i++;
      }
      toks.push({ t: 'word', v: w });
      continue;
    }
    err('ERR_PARSE_CHAR', `unexpected character '${ch}' at offset ${i}`);
  }
  return toks;
}

// ---------------------------------------------------------------------------
// Recursive-descent parser (exact inverse of the renderer above)
// ---------------------------------------------------------------------------

class P {
  private pos = 0;
  constructor(private readonly toks: Tok[]) {}

  peek(k = 0): Tok | undefined {
    return this.toks[this.pos + k];
  }
  next(): Tok {
    const t = this.toks[this.pos];
    if (t === undefined) err('ERR_PARSE_EOF', 'unexpected end of input');
    this.pos++;
    return t!;
  }
  expectPunct(v: string): void {
    const t = this.next();
    if (t.t !== 'punct' || t.v !== v) err('ERR_PARSE_EXPECT', `expected '${v}', got '${t.v}'`);
  }
  expectWord(): string {
    const t = this.next();
    if (t.t !== 'word') err('ERR_PARSE_EXPECT', `expected word, got '${t.v}'`);
    return t.v;
  }
  atEnd(): boolean {
    return this.pos >= this.toks.length;
  }

  /** 'x' INT word -> referent index. */
  refIndex(w: string): number {
    if (!/^x[0-9]+$/.test(w)) err('ERR_PARSE_REF', `expected xN, got '${w}'`);
    return Number(w.slice(1));
  }

  isRefWord(w: string): boolean {
    return /^x[0-9]+$/.test(w);
  }

  /** A prime name surface: uppercase verbatim, validated against the lexicon. */
  primeName(w: string): string {
    if (!PRIME_BY_NAME.has(w)) err('ERR_PARSE_PRIME', `'${w}' is not a prime name`);
    return w;
  }

  parseExplication(): Explication {
    const frameWord = this.expectWord();
    const frame = WORD_FRAME.get(frameWord) ?? err('ERR_PARSE_FRAME', `unknown frame '${frameWord}'`);
    const refsKw = this.expectWord();
    if (refsKw !== 'refs') err('ERR_PARSE_EXPECT', `expected 'refs', got '${refsKw}'`);
    this.expectPunct('[');
    const referents: ReferentDecl[] = [];
    if (!(this.peek()?.t === 'punct' && this.peek()?.v === ']')) {
      for (;;) {
        const xw = this.expectWord();
        const index = this.refIndex(xw);
        this.expectPunct(':');
        const kw = this.expectWord();
        const refKind = WORD_REFKIND.get(kw) ?? err('ERR_PARSE_REFKIND', `unknown referent kind '${kw}'`);
        referents.push({ index, refKind });
        const t = this.next();
        if (t.t === 'punct' && t.v === ']') break;
        if (!(t.t === 'punct' && t.v === ',')) err('ERR_PARSE_EXPECT', `expected ',' or ']', got '${t.v}'`);
      }
    } else {
      this.next(); // consume ']'
    }
    this.expectPunct('{');
    const clauses: Clause[] = [this.parseClause()];
    for (;;) {
      const t = this.next();
      if (t.t === 'punct' && t.v === '}') break;
      if (!(t.t === 'punct' && t.v === ';')) err('ERR_PARSE_EXPECT', `expected ';' or '}', got '${t.v}'`);
      clauses.push(this.parseClause());
    }
    if (!this.atEnd()) err('ERR_PARSE_TRAILING', `trailing input after explication`);
    return { schema: AST_SCHEMA, frame, referents, clauses };
  }

  parseClause(): Clause {
    const t = this.peek();
    if (t === undefined) err('ERR_PARSE_EOF', 'expected clause');
    if (t!.t === 'punct' && t!.v === '@') {
      this.next();
      const w = this.expectWord();
      const op = WORD_OP.get(w) ?? err('ERR_PARSE_OP', `unknown operator '${w}'`);
      this.expectPunct('(');
      const args: OpArg[] = [this.parseOpArg()];
      for (;;) {
        const n = this.next();
        if (n.t === 'punct' && n.v === ')') break;
        if (!(n.t === 'punct' && n.v === ',')) err('ERR_PARSE_EXPECT', `expected ',' or ')', got '${n.v}'`);
        args.push(this.parseOpArg());
      }
      const c: OpClause = { type: 'op', op, args };
      return c;
    }
    if (t!.t === 'word') {
      const w = this.expectWord();
      const pred = WORD_PRED.get(w) ?? err('ERR_PARSE_PRED', `unknown predicate '${w}'`);
      this.expectPunct('(');
      const roles: Partial<Record<Role, Filler>> = {};
      if (this.peek()?.t === 'punct' && this.peek()?.v === ')') {
        this.next();
        const c: PredClause = { type: 'pred', pred, roles };
        return c;
      }
      for (;;) {
        const rw = this.expectWord();
        if (!(ROLES as readonly string[]).includes(rw)) err('ERR_PARSE_ROLE', `unknown role '${rw}'`);
        this.expectPunct('=');
        const f = this.parseFiller();
        if (roles[rw as Role] !== undefined) err('ERR_PARSE_ROLE', `duplicate role '${rw}'`);
        roles[rw as Role] = f;
        const n = this.next();
        if (n.t === 'punct' && n.v === ')') break;
        if (!(n.t === 'punct' && n.v === ',')) err('ERR_PARSE_EXPECT', `expected ',' or ')', got '${n.v}'`);
      }
      const c: PredClause = { type: 'pred', pred, roles };
      return c;
    }
    return err('ERR_PARSE_CLAUSE', `unexpected token '${t!.v}'`);
  }

  /** OpArg: clause if '@' or predword '('; else an SP/ref/prime filler (ast.ts OpArg). */
  parseOpArg(): OpArg {
    const t = this.peek();
    if (t === undefined) err('ERR_PARSE_EOF', 'expected op argument');
    if (t!.t === 'punct' && t!.v === '@') return this.parseClause();
    if (t!.t === 'word') {
      const nxt = this.peek(1);
      const isCall = nxt?.t === 'punct' && nxt.v === '(';
      const isTemporal = (t!.v === 'after' || t!.v === 'before') && nxt?.t === 'punct' && nxt.v === '@';
      if (isCall && WORD_PRED.has(t!.v) && !isTemporal) return this.parseClause();
    }
    const f = this.parseFiller();
    // ast.ts: OpArg = Clause | SP | RefMention | PrimeFiller — nothing else.
    if (f.kind !== 'sp' && f.kind !== 'ref' && f.kind !== 'prime') {
      err('ERR_PARSE_OPARG', `filler kind '${f.kind}' is not a valid operator argument`);
    }
    return f as OpArg;
  }

  parseFiller(): Filler {
    const t = this.peek();
    if (t === undefined) err('ERR_PARSE_EOF', 'expected filler');
    if (t!.t === 'id') {
      this.next();
      return { kind: 'concept', id: t!.v };
    }
    if (t!.t === 'punct') {
      if (t!.v === '[') return this.parseSP();
      if (t!.v === '#') {
        this.next();
        const w = this.expectWord();
        return { kind: 'prime', prime: this.primeName(w) };
      }
      if (t!.v === '{') {
        this.next();
        const clause = this.parseClause();
        this.expectPunct('}');
        return { kind: 'clause', clause };
      }
      return err('ERR_PARSE_FILLER', `unexpected '${t!.v}'`);
    }
    // word cases: q{...} quote, after@/before@ temporal, xN ref
    const w = t!.v;
    const nxt = this.peek(1);
    if (w === 'q' && nxt?.t === 'punct' && nxt.v === '{') {
      this.next();
      this.next();
      const clauses: Clause[] = [this.parseClause()];
      for (;;) {
        const n = this.next();
        if (n.t === 'punct' && n.v === '}') break;
        if (!(n.t === 'punct' && n.v === ';')) err('ERR_PARSE_EXPECT', `expected ';' or '}', got '${n.v}'`);
        clauses.push(this.parseClause());
      }
      return { kind: 'quote', clauses };
    }
    if ((w === 'after' || w === 'before') && nxt?.t === 'punct' && nxt.v === '@') {
      this.next();
      this.next();
      const op = w === 'after' ? 'AFTER' : 'BEFORE';
      const a = this.peek();
      if (a === undefined) err('ERR_PARSE_EOF', 'expected temporal anchor');
      if (a!.t === 'punct' && a!.v === '[') return { kind: 'temporal', op, anchor: this.parseSP() };
      if (a!.t === 'punct' && a!.v === '#') {
        this.next();
        const pw = this.expectWord();
        return { kind: 'temporal', op, anchor: { kind: 'prime', prime: this.primeName(pw) } };
      }
      if (a!.t === 'word' && this.isRefWord(a!.v)) {
        this.next();
        return { kind: 'temporal', op, anchor: { kind: 'ref', index: this.refIndex(a!.v) } };
      }
      return err('ERR_PARSE_TEMPORAL', `bad temporal anchor '${a!.v}'`);
    }
    if (this.isRefWord(w)) {
      this.next();
      return { kind: 'ref', index: this.refIndex(w) };
    }
    return err('ERR_PARSE_FILLER', `unexpected word '${w}'`);
  }

  parseSP(): SP {
    this.expectPunct('[');
    let det: SPDeterminer | undefined;
    let quant: SPQuantifier | undefined;
    const mods: SPModifier[] = [];
    // d: / q: / m: markers — each is word + ':' + word.
    for (;;) {
      const t = this.peek();
      const c = this.peek(1);
      if (
        t?.t === 'word' &&
        (t.v === 'd' || t.v === 'q' || t.v === 'm') &&
        c?.t === 'punct' &&
        c.v === ':'
      ) {
        this.next();
        this.next();
        const w = this.expectWord();
        if (t.v === 'd') {
          if (det !== undefined) err('ERR_PARSE_SP', 'duplicate determiner');
          det = WORD_DET.get(w) ?? err('ERR_PARSE_SP', `unknown determiner '${w}'`);
        } else if (t.v === 'q') {
          if (quant !== undefined) err('ERR_PARSE_SP', 'duplicate quantifier');
          quant = WORD_QUANT.get(w) ?? err('ERR_PARSE_SP', `unknown quantifier '${w}'`);
        } else {
          // m:good | m:very.good | m:more.good
          const dot = w.indexOf('.');
          if (dot === -1) {
            const mod = WORD_MOD.get(w) ?? err('ERR_PARSE_SP', `unknown mod '${w}'`);
            mods.push({ mod });
          } else {
            const intw = w.slice(0, dot);
            const modw = w.slice(dot + 1);
            const mod = WORD_MOD.get(modw) ?? err('ERR_PARSE_SP', `unknown mod '${modw}'`);
            if (intw !== 'very' && intw !== 'more') err('ERR_PARSE_SP', `unknown intensifier '${intw}'`);
            mods.push({ mod, intensifier: intw === 'very' ? 'VERY' : 'MORE' });
          }
        }
        continue;
      }
      break;
    }
    // head
    const t = this.peek();
    if (t === undefined) err('ERR_PARSE_EOF', 'expected SP head');
    let head: SPHead;
    if (t!.t === 'id') {
      this.next();
      head = { kind: 'conceptHead', id: t!.v };
    } else if (t!.t === 'word' && (t!.v === 'kind-of' || t!.v === 'part-of')) {
      const kw = t!.v;
      this.next();
      this.expectPunct('(');
      const a = this.peek();
      if (a === undefined) err('ERR_PARSE_EOF', 'expected kind/part of-target');
      let of: SP | { kind: 'concept'; id: string } | { kind: 'ref'; index: number };
      if (a!.t === 'punct' && a!.v === '[') of = this.parseSP();
      else if (a!.t === 'id') {
        this.next();
        of = { kind: 'concept', id: a!.v };
      } else if (a!.t === 'word' && this.isRefWord(a!.v)) {
        this.next();
        of = { kind: 'ref', index: this.refIndex(a!.v) };
      } else {
        return err('ERR_PARSE_SP', `bad kind/part of-target '${a!.v}'`);
      }
      this.expectPunct(')');
      head = { kind: kw === 'kind-of' ? 'kindFrame' : 'partFrame', of };
    } else if (t!.t === 'word' && this.isRefWord(t!.v)) {
      this.next();
      head = { kind: 'refHead', index: this.refIndex(t!.v) };
    } else if (t!.t === 'word') {
      this.next();
      head = { kind: 'primeHead', prime: this.primeName(t!.v) };
    } else {
      return err('ERR_PARSE_SP', `bad SP head '${t!.v}'`);
    }
    // optional bind
    let bind: number | undefined;
    if (this.peek()?.t === 'punct' && this.peek()?.v === '!') {
      this.next();
      const w = this.expectWord();
      if (!/^[0-9]+$/.test(w)) err('ERR_PARSE_SP', `bad bind index '${w}'`);
      bind = Number(w);
    }
    // optional restrictedBy
    let restrictedBy: Clause | undefined;
    if (this.peek()?.t === 'punct' && this.peek()?.v === '|') {
      this.next();
      restrictedBy = this.parseClause();
    }
    this.expectPunct(']');
    const sp: {
      kind: 'sp';
      det?: SPDeterminer;
      quant?: SPQuantifier;
      mods?: SPModifier[];
      head: SPHead;
      restrictedBy?: Clause;
      bind?: number;
    } = { kind: 'sp', head };
    if (det !== undefined) sp.det = det;
    if (quant !== undefined) sp.quant = quant;
    if (mods.length > 0) sp.mods = mods;
    if (bind !== undefined) sp.bind = bind;
    if (restrictedBy !== undefined) sp.restrictedBy = restrictedBy;
    return sp;
  }
}

/**
 * Parse canonical-form v0 text back to a kot-ast/1 explication. Exact inverse
 * of renderExplication on valid explications; anything else fails closed.
 */
export function parseRendered(text: string): Explication {
  return new P(tokenize(text)).parseExplication();
}
