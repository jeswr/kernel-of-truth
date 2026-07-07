/**
 * E4 gloss realizer: explication AST -> naturalistic English paraphrase
 * (docs/poc-design.md E4 rev 2, MAJOR 6; bead kernel-of-truth-73u).
 *
 * AUTHORSHIP RECORD (load-bearing; also in poc/e4/README.md): these
 * paraphrase rules — the per-predicate/operator phrasings, the five style
 * profiles, the referent-naming scheme, the lexical alternative sets — were
 * written by the E4 data-prep agent (Claude Fable 5, session of 2026-07-07)
 * from the MEANING of the AST node types as specified in
 * docs/architecture.md / the encoder's ast.ts, NOT by templating either
 * (a) the encoder/decoder's deterministic clause renderings, or (b) the
 * kernel-v0 `gloss` fields, or (c) poc/e1's cloze template frames. No string
 * in this file was copied from those sources. What this does and does NOT
 * guarantee is discussed in README.md ("Independent authorship — honesty
 * notes"): the same organisation-of-rules is still ONE author and one
 * procedure; independence here means lexical/syntactic independence from the
 * training-side renderings, mechanically spot-checked (n-gram gate +
 * target-lexicon disjointness), not authorship by a second party.
 *
 * Interface contract: deterministic in (explication, style, rng label,
 * banned set). Realizes EVERY node type the grammar admits (all 19
 * predicate frames, all 11 operators, SP det/quant/mods/kind/part/
 * restrictedBy/bind, quotes with indexical re-anchoring, temporal anchors,
 * referent chains) — fail closed (ERR_REALIZE) on anything else.
 */

import { DetStream } from '@jeswr/kernel-encoder';
import type {
  Clause,
  Explication,
  Filler,
  OpArg,
  OpClause,
  PredClause,
  RefKind,
  SP,
} from '@jeswr/kernel-encoder';
import { lemmaCandidates } from '@jeswr/kernel-mapper';

export const STYLE_COUNT = 5;

export interface RealizeOptions {
  /** Style profile 0..4 (register/syntax/lexis family). */
  readonly style: number;
  /** Seeded choice stream (label carries concept/variant/retry salt). */
  readonly rng: DetStream;
  /**
   * Lemmas that may NOT appear in the output (the target concept's own
   * mapper-lexicon surface forms; empty on the first authoring pass —
   * collisions are counted and rewritten with this set populated).
   */
  readonly bannedLemmas: ReadonlySet<string>;
  /** Referenced-concept id -> English phrase; position selects nominal
   * ('entity') vs predicative ('attribute', e.g. BE-SPEC) phrasing. */
  readonly conceptPhrase: (id: string, pos: 'entity' | 'attribute') => string;
}

// ---------------------------------------------------------------------------
// Style profiles. Each provides naming for the frame-implicit referents,
// clause connectors and quote mode; lexical variety within a style comes from
// the alternative sets below (rng-picked, ban-filtered).
// ---------------------------------------------------------------------------

interface StyleDef {
  readonly quote: 'direct' | 'indirect';
  /** [intro, later] naming for referent 1 by kind. */
  readonly r1Someone: readonly [string, string];
  readonly r1Thing: readonly [string, string];
  /** Sentence connectors (joined between top-level clauses). */
  readonly joiners: readonly string[];
  /** Lead-in options per frame (may include ''). */
  readonly leadWhenTrue: readonly string[];
  readonly leadInstance: readonly string[];
  readonly leadRelational: readonly string[];
  /** Whether referent-1 "they"-agreement applies (style 4). */
  readonly r1Plural: boolean;
  /** Second person referent 1 (style 1). */
  readonly r1SecondPerson: boolean;
}

const STYLES: readonly StyleDef[] = [
  {
    // 0: plain declarative
    quote: 'direct',
    r1Someone: ['someone', 'this person'],
    r1Thing: ['something', 'this thing'],
    joiners: ['. ', '. ', '. '],
    leadWhenTrue: ['', 'things are like this: '],
    leadInstance: ['', ''],
    leadRelational: [''],
    r1Plural: false,
    r1SecondPerson: false,
  },
  {
    // 1: second-person, conversational
    quote: 'indirect',
    r1Someone: ['you', 'you'],
    r1Thing: ['something', 'it'],
    joiners: ['. ', ', and ', '. '],
    leadWhenTrue: ['', 'it goes like this: '],
    leadInstance: [''],
    leadRelational: [''],
    r1Plural: false,
    r1SecondPerson: true,
  },
  {
    // 2: definitional, slightly formal
    quote: 'indirect',
    r1Someone: ['a person', 'the person'],
    r1Thing: ['a thing', 'the thing'],
    joiners: ['. ', '. Also, ', '. '],
    leadWhenTrue: ['the situation is this: ', ''],
    leadInstance: ['', 'this is about a person or a thing: '],
    leadRelational: ['this is about two of them: ', ''],
    r1Plural: false,
    r1SecondPerson: false,
  },
  {
    // 3: narrative / storybook
    quote: 'direct',
    r1Someone: ['a certain person', 'that person'],
    r1Thing: ['a certain thing', 'that thing'],
    joiners: ['. ', '. Then ', '. '],
    leadWhenTrue: ['picture this: ', ''],
    leadInstance: [''],
    leadRelational: [''],
    r1Plural: false,
    r1SecondPerson: false,
  },
  {
    // 4: compact, pronoun-heavy
    quote: 'indirect',
    r1Someone: ['someone', 'they'],
    r1Thing: ['something', 'it'],
    joiners: ['; ', '; ', '; '],
    leadWhenTrue: [''],
    leadInstance: [''],
    leadRelational: [''],
    r1Plural: true, // "they feel", not "they feels"
    r1SecondPerson: false,
  },
];

// ---------------------------------------------------------------------------
// Lexical alternative sets (simple-register English on purpose: the E1 model
// vocabulary is TinyStories word-level; fancy words would just become <unk>).
// ---------------------------------------------------------------------------

interface Verb {
  readonly base: string;
  readonly s: string;
}

const V = (base: string, s?: string): Verb => ({ base, s: s ?? `${base}s` });

const VERBS: Record<string, readonly Verb[]> = {
  THINK: [V('think'), V('have the thought', 'has the thought')],
  KNOW: [V('know')],
  WANT: [V('want'), V('wish', 'wishes'), V('would like', 'would like')],
  FEEL: [V('feel')],
  SEE: [V('see')],
  HEAR: [V('hear')],
  SAY: [V('say')],
  DO: [V('do', 'does')],
  HAPPEN: [V('happen'), V('take place', 'takes place')],
  MOVE: [V('move')],
  LIVE: [V('live')],
  WANT_NP: [V('want'), V('would like', 'would like')], // "wish <NP>" is off; entity complements only
  DIE: [V('die')],
};

const ADJ: Record<string, readonly string[]> = {
  GOOD: ['good', 'nice'],
  BAD: ['bad', 'not nice'],
  BIG: ['big', 'large'],
  SMALL: ['small', 'little'],
};
const ADJ_MORE: Record<string, string> = {
  GOOD: 'better',
  BAD: 'worse',
  BIG: 'bigger',
  SMALL: 'smaller',
};

const NOUN: Record<string, readonly [string, string][]> = {
  // head prime -> [singular, plural] alternatives
  SOMEONE: [['someone', 'people'], ['a person', 'people'], ['somebody', 'people']],
  PEOPLE: [['people', 'people']],
  'SOMETHING~THING': [['something', 'things'], ['a thing', 'things']],
  BODY: [['a body', 'bodies']],
  WORDS: [['words', 'words'], ['some words', 'words']],
  'WHEN~TIME': [['a time', 'times']],
  MOMENT: [['a moment', 'moments']],
  'WHERE~PLACE': [['a place', 'places'], ['somewhere', 'places']],
  SIDE: [['a side', 'sides']],
  I: [['me', 'me']],
  YOU: [['you', 'you']],
};

/** Bare noun (no article) for det/quant composition. */
const BARE: Record<string, readonly [string, string][]> = {
  SOMEONE: [['person', 'people']],
  PEOPLE: [['people', 'people']],
  'SOMETHING~THING': [['thing', 'things']],
  BODY: [['body', 'bodies']],
  WORDS: [['words', 'words']],
  'WHEN~TIME': [['time', 'times']],
  MOMENT: [['moment', 'moments']],
  'WHERE~PLACE': [['place', 'places']],
  SIDE: [['side', 'sides']],
};

const DET: Record<string, readonly string[]> = {
  THIS: ['this'],
  'THE-SAME': ['the same'],
  'OTHER~ELSE~ANOTHER': ['another', 'a different'],
  SOME: ['some'],
};

const QUANT: Record<string, readonly string[]> = {
  ONE: ['one'],
  TWO: ['two'],
  SOME: ['some'],
  ALL: ['all'],
  'MUCH~MANY': ['many', 'lots of'],
  'LITTLE~FEW': ['only a few', 'not many'],
};

const PLURAL_QUANT = new Set(['TWO', 'SOME', 'ALL', 'MUCH~MANY', 'LITTLE~FEW']);

const KIND_OF: readonly string[] = ['a kind of', 'a type of', 'a sort of'];
const PART_OF: readonly string[] = ['a part of', 'a piece of', 'one part of'];

const DURATION: Record<string, readonly string[]> = {
  'A-LONG-TIME': ['for a long time', 'for ages'],
  'A-SHORT-TIME': ['for a short time', 'for a little while'],
  'FOR-SOME-TIME': ['for some time', 'for a while'],
  MOMENT: ['for a moment'],
};

// Referent naming sequences by kind (slot 0 is the style-specific referent 1;
// these cover bound referents and referent 2+). [intro, later].
const REF_NAMES: Record<RefKind, readonly [string, string][]> = {
  SomeoneRef: [
    ['someone', 'this person'],
    ['someone else', 'the other person'],
    ['a third person', 'the third person'],
    ['a fourth person', 'the fourth person'],
  ],
  SomethingRef: [
    ['something', 'this thing'],
    ['something else', 'the other thing'],
    ['a third thing', 'the third thing'],
    ['a fourth thing', 'the fourth thing'],
  ],
  TimeRef: [
    ['a time', 'this time'],
    ['another time', 'the other time'],
    ['a third time', 'the third time'],
  ],
  PlaceRef: [
    ['a place', 'this place'],
    ['another place', 'the other place'],
    ['a third place', 'the third place'],
  ],
  ClauseRef: [
    ['some words', 'those words'],
    ['other words', 'the other words'],
    ['more words', 'the third words'],
  ],
};

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

interface RefState {
  readonly kind: RefKind;
  readonly intro: string;
  readonly later: string;
  mentioned: boolean;
  /** Agreement per form: style 4's r1 is "someone" (sg) then "they" (pl);
   * a plural introducing SP ("all people", bind n) is plural in both. */
  introPlural: boolean;
  laterPlural: boolean;
  /** Mutable: a plural binding SP swaps the later name ("those things"). */
  later2: string;
  readonly person: 1 | 2 | 3;
}

const PLURAL_LATER: Record<RefKind, string> = {
  SomeoneRef: 'those people',
  SomethingRef: 'those things',
  TimeRef: 'those times',
  PlaceRef: 'those places',
  ClauseRef: 'those words',
};

interface Ctx {
  readonly rng: DetStream;
  readonly style: StyleDef;
  readonly bannedLemmas: ReadonlySet<string>;
  readonly conceptPhrase: (id: string, pos: 'entity' | 'attribute') => string;
  readonly refs: Map<number, RefState>;
  readonly kindCounts: Map<RefKind, number>;
  quoteDepth: number;
  quoteMode: 'direct' | 'indirect';
  /** Referring expression for the quoted thinker/speaker (indirect quotes). */
  speaker: NP | null;
  /** Identity key of the current clause's subject (reflexive coreference). */
  subjKey: string | null;
}

interface NP {
  readonly text: string;
  readonly plural: boolean;
  readonly person: 1 | 2 | 3;
  /** Identity key for subject-control collapse ('ref:3' | 'prime:I' | null). */
  readonly key: string | null;
}

function banned(ctx: Ctx, phrase: string): boolean {
  if (ctx.bannedLemmas.size === 0) return false;
  for (const w of phrase.toLowerCase().split(/[^a-z']+/)) {
    if (w.length === 0) continue;
    for (const cand of lemmaCandidates(w)) {
      if (ctx.bannedLemmas.has(cand)) return true;
    }
  }
  return false;
}

function pick(ctx: Ctx, alts: readonly string[]): string {
  const ok = alts.filter((a) => !banned(ctx, a));
  const pool = ok.length > 0 ? ok : alts; // final mapper gate catches the residue
  return pool[ctx.rng.nextBelow(pool.length)]!;
}

function pickVerb(ctx: Ctx, pred: string): Verb {
  const alts = VERBS[pred];
  if (alts === undefined) throw new Error(`ERR_REALIZE: no verb table for ${pred}`);
  const ok = alts.filter((v) => !banned(ctx, v.base) && !banned(ctx, v.s));
  const pool = ok.length > 0 ? ok : alts;
  return pool[ctx.rng.nextBelow(pool.length)]!;
}

function finite(v: Verb, np: NP): string {
  return np.person === 3 && !np.plural ? v.s : v.base;
}

function copula(np: NP): string {
  if (np.person === 1 && !np.plural) return 'am';
  return np.person === 3 && !np.plural ? 'is' : 'are';
}

// ---------------------------------------------------------------------------
// Referents
// ---------------------------------------------------------------------------

function registerRef(ctx: Ctx, index: number, kind: RefKind, style?: StyleDef): void {
  if (ctx.refs.has(index)) return;
  const slot = ctx.kindCounts.get(kind) ?? 0;
  ctx.kindCounts.set(kind, slot + 1);
  let intro: string;
  let later: string;
  let introPlural = false;
  let laterPlural = false;
  let person: 1 | 2 | 3 = 3;
  if (style !== undefined && slot === 0 && (kind === 'SomeoneRef' || kind === 'SomethingRef')) {
    [intro, later] = kind === 'SomeoneRef' ? style.r1Someone : style.r1Thing;
    if (kind === 'SomeoneRef' && style.r1SecondPerson) person = 2;
    if (kind === 'SomeoneRef' && style.r1Plural) laterPlural = true; // "someone ... they feel"
  } else {
    const seq = REF_NAMES[kind];
    const chosen = seq[Math.min(slot, seq.length - 1)]!;
    intro = slot < seq.length ? chosen[0] : `thing number ${slot + 1}`;
    later = slot < seq.length ? chosen[1] : `thing number ${slot + 1}`;
    if (kind === 'ClauseRef') introPlural = laterPlural = true; // "those words are..."
  }
  ctx.refs.set(index, {
    kind,
    intro,
    later,
    mentioned: false,
    introPlural,
    laterPlural,
    later2: later,
    person,
  });
}

function mentionRef(ctx: Ctx, index: number): NP {
  const st = ctx.refs.get(index);
  if (st === undefined) {
    // Quote-local or undeclared referent: fail closed rather than hallucinate.
    throw new Error(`ERR_REALIZE: mention of unregistered referent ${index}`);
  }
  const useIntro = !st.mentioned;
  st.mentioned = true;
  return {
    text: useIntro ? st.intro : st.later2,
    plural: useIntro ? st.introPlural : st.laterPlural,
    person: st.person,
    key: `ref:${index}`,
  };
}

// ---------------------------------------------------------------------------
// Entities / SPs
// ---------------------------------------------------------------------------

function primeEntity(ctx: Ctx, prime: string, subject: boolean): NP {
  if (prime === 'I') {
    if (ctx.quoteDepth > 0 && ctx.quoteMode === 'indirect' && ctx.speaker !== null) {
      return ctx.speaker; // re-anchored: I = the quoted thinker
    }
    return { text: subject ? 'I' : 'me', plural: false, person: 1, key: 'prime:I' };
  }
  if (prime === 'YOU') return { text: 'you', plural: false, person: 2, key: 'prime:YOU' };
  if (prime === 'NOW') return { text: nowText(ctx), plural: false, person: 3, key: 'prime:NOW' };
  if (prime === 'HERE') return { text: 'here', plural: false, person: 3, key: 'prime:HERE' };
  const nouns = NOUN[prime];
  if (nouns !== undefined) {
    const alts = nouns.map((n) => n[0]);
    return { text: pick(ctx, alts), plural: prime === 'PEOPLE' || prime === 'WORDS', person: 3, key: null };
  }
  throw new Error(`ERR_REALIZE: prime entity ${prime}`);
}

function nowText(ctx: Ctx): string {
  return ctx.quoteDepth > 0 && ctx.quoteMode === 'indirect'
    ? pick(ctx, ['at that moment', 'right then'])
    : pick(ctx, ['now', 'right now']);
}

function conceptNP(ctx: Ctx, id: string): NP {
  return { text: ctx.conceptPhrase(id, 'entity'), plural: false, person: 3, key: `concept:${id}` };
}

function realizeEntity(ctx: Ctx, f: Filler, subject: boolean): NP {
  let np: NP;
  switch (f.kind) {
    case 'ref': {
      // Same-clause subject coreference reads as a reflexive ("X sees
      // themselves"), not as a fresh anaphor ("X sees the other person").
      if (!subject && ctx.subjKey !== null && ctx.subjKey === `ref:${f.index}`) {
        const st = ctx.refs.get(f.index);
        if (st !== undefined) {
          st.mentioned = true;
          const refl =
            st.kind === 'SomeoneRef' ? (st.person === 2 ? 'yourself' : 'themselves') : 'itself';
          return { text: refl, plural: st.laterPlural, person: st.person, key: `ref:${f.index}` };
        }
      }
      np = mentionRef(ctx, f.index);
      break;
    }
    case 'prime':
      np = primeEntity(ctx, f.prime, subject);
      break;
    case 'concept':
      np = conceptNP(ctx, f.id);
      break;
    case 'sp':
      np = realizeSP(ctx, f);
      break;
    default:
      throw new Error(`ERR_REALIZE: entity filler kind ${f.kind}`);
  }
  if (subject) ctx.subjKey = np.key;
  return np;
}

function nounFor(ctx: Ctx, prime: string, plural: boolean, bare: boolean): string {
  const table = bare ? BARE[prime] : NOUN[prime];
  if (table === undefined) throw new Error(`ERR_REALIZE: noun for head prime ${prime}`);
  const alts = table.map((n) => (plural ? n[1] : n[0]));
  return pick(ctx, [...new Set(alts)]);
}

function realizeSP(ctx: Ctx, sp: SP): NP {
  const plural =
    (sp.quant !== undefined && PLURAL_QUANT.has(sp.quant)) ||
    (sp.head.kind === 'primeHead' && (sp.head.prime === 'PEOPLE' || sp.head.prime === 'WORDS'));

  // bind introduces a discourse referent; register BEFORE restrictedBy so the
  // restricting clause can reference it (with the SP's own agreement).
  if (sp.bind !== undefined) {
    const kind: RefKind =
      sp.head.kind === 'primeHead' ? kindOfHead(sp.head.prime) : 'SomethingRef';
    registerRef(ctx, sp.bind, kind);
    const st = ctx.refs.get(sp.bind)!;
    if (st.mentioned) {
      // Safety net: the referent was already mentioned anaphorically before
      // its binding SP is realized (should not happen — the IF/BECAUSE/WHEN
      // flip guard forbids the ordering that causes it) — keep COREFERENCE
      // over SP decoration: emit the anaphoric name (+ any restriction).
      let text = st.later2;
      if (sp.restrictedBy !== undefined) {
        text = `${text} ${realizeRelative(ctx, sp.restrictedBy, sp.bind, spIsPerson(sp))}`;
      }
      return { text, plural: st.laterPlural, person: st.person, key: `ref:${sp.bind}` };
    }
    st.mentioned = true; // this SP *is* the introducing mention
    st.introPlural = st.laterPlural = plural;
    if (plural) st.later2 = PLURAL_LATER[kind]; // "some things ... those things"
  }

  // modifiers
  const modText = (sp.mods ?? [])
    .map((m) => {
      const alts = ADJ[m.mod];
      if (alts === undefined) throw new Error(`ERR_REALIZE: SP mod ${m.mod}`);
      if (m.intensifier === 'MORE') return ADJ_MORE[m.mod]!;
      const adj = pick(ctx, alts);
      return m.intensifier === 'VERY' ? `${pick(ctx, ['very', 'really'])} ${adj}` : adj;
    })
    .join(' ');

  let text: string;
  switch (sp.head.kind) {
    case 'primeHead': {
      const p = sp.head.prime;
      if (sp.det !== undefined || sp.quant !== undefined || modText !== '') {
        // Plural-aware determiners: "other/different people", "these things".
        const detAlts =
          sp.det === 'OTHER~ELSE~ANOTHER' && plural
            ? ['other', 'different']
            : sp.det === 'THIS' && plural
              ? ['these']
              : sp.det !== undefined
                ? DET[sp.det] ?? [sp.det.toLowerCase()]
                : null;
        const detTxt =
          detAlts !== null
            ? pick(ctx, detAlts)
            : sp.quant !== undefined
              ? pick(ctx, QUANT[sp.quant] ?? [sp.quant.toLowerCase()])
              : '';
        const bare = BARE[p];
        if (bare !== undefined) {
          const noun = nounFor(ctx, p, plural, true);
          const core = [detTxt, modText, noun].filter((s) => s !== '').join(' ');
          // "one good thing" / "this person" / "good things" (no det) —
          // bare-plural without det/quant gets no article; bare-singular does.
          text =
            detTxt === '' && !plural
              ? `${article(core)} ${core}`
              : core;
        } else {
          // I / YOU as heads take no det morphology; fold mods copularly.
          const base = primeEntity(ctx, p, false).text;
          text = modText === '' ? base : `${base}, who ${copula({ text: base, plural: false, person: p === 'I' ? 1 : 2, key: null })} ${modText},`;
        }
      } else {
        text = nounFor(ctx, p, plural, false);
      }
      break;
    }
    case 'kindFrame':
    case 'partFrame': {
      const ofNP = realizeOf(ctx, sp.head.of);
      const frame = pick(ctx, sp.head.kind === 'kindFrame' ? KIND_OF : PART_OF);
      const withMods = modText === '' ? frame : frame.replace(/^(a|one) /, `$1 ${modText} `);
      const detTxt = sp.det !== undefined ? pick(ctx, DET[sp.det] ?? []) : '';
      let core = `${withMods} ${ofNP.text}`;
      if (detTxt !== '') core = core.replace(/^(a|one) /, `${detTxt} `).replace(/^(kind|type|sort|part|piece)/, `$1`);
      text = core;
      break;
    }
    case 'refHead': {
      const np = mentionRef(ctx, sp.head.index);
      text = modText === '' ? np.text : `${np.text}, which is ${modText},`;
      return { text, plural: np.plural, person: np.person, key: np.key };
    }
    case 'conceptHead': {
      const np = conceptNP(ctx, sp.head.id);
      text = modText === '' ? np.text : `${modText} ${np.text}`;
      break;
    }
    default:
      throw new Error(`ERR_REALIZE: SP head`);
  }

  if (sp.restrictedBy !== undefined) {
    const rel = realizeRelative(ctx, sp.restrictedBy, sp.bind, spIsPerson(sp));
    text = `${text} ${rel}`;
  }
  return { text, plural, person: 3, key: sp.bind !== undefined ? `ref:${sp.bind}` : null };
}

function spIsPerson(sp: SP): boolean {
  return (
    sp.head.kind === 'primeHead' &&
    ['SOMEONE', 'PEOPLE', 'I', 'YOU'].includes(sp.head.prime)
  );
}

function kindOfHead(prime: string): RefKind {
  if (['SOMEONE', 'PEOPLE', 'I', 'YOU'].includes(prime)) return 'SomeoneRef';
  if (['WHEN~TIME', 'MOMENT'].includes(prime)) return 'TimeRef';
  if (['WHERE~PLACE', 'SIDE'].includes(prime)) return 'PlaceRef';
  if (prime === 'WORDS') return 'ClauseRef';
  return 'SomethingRef';
}

function realizeOf(ctx: Ctx, of: SP | { kind: 'concept'; id: string } | { kind: 'ref'; index: number }): NP {
  if (of.kind === 'sp') return realizeSP(ctx, of);
  if (of.kind === 'concept') return conceptNP(ctx, of.id);
  return mentionRef(ctx, of.index);
}

function article(phrase: string): string {
  return /^[aeiou]/.test(phrase) ? 'an' : 'a';
}

/** Relative clause for SP.restrictedBy: "who/that <VP>" when the restricting
 * clause is predicated of the bound referent, else "such that <clause>". */
function realizeRelative(ctx: Ctx, clause: Clause, bind: number | undefined, person: boolean): string {
  if (clause.type === 'pred' && bind !== undefined) {
    const subjF = subjectFiller(clause);
    if (subjF !== null && subjF.kind === 'ref' && subjF.index === bind) {
      // predRealize realizes the subject internally (bookkeeping/rng); only
      // the VP is emitted — the SP head itself is the relative's subject.
      const parts = predRealize(ctx, clause);
      return `${person ? pick(ctx, ['who', 'that']) : 'that'} ${parts.vp('finite')}`;
    }
  }
  return `such that ${realizeClause(ctx, clause)}`;
}

// ---------------------------------------------------------------------------
// Adjuncts
// ---------------------------------------------------------------------------

function timeAdjunct(ctx: Ctx, f: Filler): string {
  switch (f.kind) {
    case 'prime':
      if (f.prime === 'NOW') return nowText(ctx);
      throw new Error(`ERR_REALIZE: time prime ${f.prime}`);
    case 'temporal': {
      const anchor =
        f.anchor.kind === 'prime'
          ? f.anchor.prime === 'NOW'
            ? null // "after now" reads badly; use adverb forms below
            : primeEntity(ctx, f.anchor.prime, false).text
          : f.anchor.kind === 'ref'
            ? mentionRef(ctx, f.anchor.index).text
            : realizeSP(ctx, f.anchor).text;
      if (anchor === null) {
        return f.op === 'AFTER'
          ? pick(ctx, ['after this', 'later on', 'afterwards'])
          : pick(ctx, ['before now', 'earlier', 'before this moment']);
      }
      return `${f.op === 'AFTER' ? 'after' : 'before'} ${anchor}`;
    }
    case 'ref':
      return `at ${mentionRef(ctx, f.index).text}`;
    case 'sp':
      return `at ${realizeSP(ctx, f).text}`;
    default:
      throw new Error(`ERR_REALIZE: time adjunct kind ${f.kind}`);
  }
}

function adjunctTail(ctx: Ctx, roles: PredClause['roles']): string {
  const parts: string[] = [];
  if (roles.time !== undefined) parts.push(timeAdjunct(ctx, roles.time));
  if (roles.duration !== undefined) {
    if (roles.duration.kind !== 'prime') throw new Error('ERR_REALIZE: duration filler');
    parts.push(pick(ctx, DURATION[roles.duration.prime] ?? []));
  }
  if (roles.place !== undefined) {
    if (roles.place.kind === 'prime' && roles.place.prime === 'HERE') parts.push('here');
    else parts.push(`at ${realizeEntity(ctx, roles.place, false).text}`);
  }
  if (roles.manner !== undefined) parts.push(pick(ctx, ['like this', 'in this way']));
  return parts.length === 0 ? '' : ` ${parts.join(' ')}`;
}

// ---------------------------------------------------------------------------
// Predicates
// ---------------------------------------------------------------------------

interface PredRealization {
  readonly subj: NP;
  /** VP in a given form; adjuncts already appended. */
  vp(form: 'finite' | 'base'): string;
}

/**
 * Realize a predicate clause into subject + VP. Returns null only for the
 * omitSubjectKey mode when the clause's subject is not that key.
 */
function predRealize(ctx: Ctx, c: PredClause): PredRealization {
  ctx.subjKey = null; // set by the handler's own subject realization
  const r = c.roles;
  const need = (f: Filler | undefined, what: string): Filler => {
    if (f === undefined) throw new Error(`ERR_REALIZE: ${c.pred} missing ${what}`);
    return f;
  };
  // NOTE: the adjunct tail is realized ONCE, at construction time and AFTER
  // the case handler built its complements (textual order ~ realization order,
  // so referent intro/later forms track the sentence), and the vp() closure is
  // then PURE — callers may invoke it twice (e.g. the NOT branch probes the
  // finite form) without consuming rng draws or re-mentioning referents.
  const simple = (subj: NP, mk: (v: 'finite' | 'base') => string): PredRealization => {
    const tailText = adjunctTail(ctx, r);
    return { subj, vp: (form) => `${mk(form)}${tailText}` };
  };
  const verbal = (subj: NP, pred: string, complement: string): PredRealization => {
    const v = pickVerb(ctx, pred);
    return simple(subj, (form) => `${form === 'finite' ? finite(v, subj) : v.base}${complement}`);
  };

  switch (c.pred) {
    case 'DO': {
      const subj = realizeEntity(ctx, need(r.agent, 'agent'), true);
      let comp = r.undergoer !== undefined ? ` ${objText(ctx, r.undergoer)}` : ' things';
      if (r.instrument !== undefined) {
        comp += ` ${pick(ctx, ['with', 'using'])} ${objText(ctx, r.instrument)}`;
      }
      if (r.comitative !== undefined) comp += ` together with ${objText(ctx, r.comitative)}`;
      return verbal(subj, 'DO', comp);
    }
    case 'HAPPEN': {
      const subj =
        r.undergoer !== undefined
          ? realizeEntity(ctx, r.undergoer, true)
          : ({ text: 'something', plural: false, person: 3, key: null } as NP);
      return verbal(subj, 'HAPPEN', '');
    }
    case 'MOVE':
      return verbal(realizeEntity(ctx, need(r.undergoer, 'undergoer'), true), 'MOVE', '');
    case 'LIVE':
      return verbal(realizeEntity(ctx, need(r.undergoer, 'undergoer'), true), 'LIVE', '');
    case 'DIE':
      return verbal(realizeEntity(ctx, need(r.undergoer, 'undergoer'), true), 'DIE', '');
    case 'FEEL': {
      const subj = realizeEntity(ctx, need(r.experiencer, 'experiencer'), true);
      let comp: string;
      if (r.attribute !== undefined) {
        if (r.attribute.kind !== 'prime') throw new Error('ERR_REALIZE: FEEL attribute');
        comp = ` ${pick(ctx, ADJ[r.attribute.prime] ?? [])}`;
        if (comp === ' ') throw new Error(`ERR_REALIZE: FEEL attribute ${r.attribute.prime}`);
      } else {
        comp = ' something';
      }
      return verbal(subj, 'FEEL', comp);
    }
    case 'SEE':
    case 'HEAR': {
      const subj = realizeEntity(ctx, need(r.experiencer, 'experiencer'), true);
      return verbal(subj, c.pred, ` ${objText(ctx, need(r.stimulus, 'stimulus'))}`);
    }
    case 'THINK': {
      const subj = realizeEntity(ctx, need(r.experiencer, 'experiencer'), true);
      if (r.quote !== undefined) {
        if (r.quote.kind !== 'quote') throw new Error('ERR_REALIZE: THINK quote');
        return quotePred(ctx, subj, 'THINK', r.quote.clauses, r);
      }
      const comp = r.topic !== undefined ? ` about ${objText(ctx, r.topic)}` : ' about things';
      return verbal(subj, 'THINK', comp);
    }
    case 'KNOW': {
      const subj = realizeEntity(ctx, need(r.experiencer, 'experiencer'), true);
      if (r.complement !== undefined) {
        if (r.complement.kind !== 'clause') throw new Error('ERR_REALIZE: KNOW complement');
        const sub = realizeClause(ctx, r.complement.clause);
        return verbal(subj, 'KNOW', ` that ${sub}`);
      }
      const comp = r.topic !== undefined ? ` ${objText(ctx, r.topic)}` : ' things';
      return verbal(subj, 'KNOW', comp);
    }
    case 'WANT':
    case "DON'T-WANT": {
      const subj = realizeEntity(ctx, need(r.experiencer, 'experiencer'), true);
      const comp = need(r.complement, 'complement');
      const neg = c.pred === "DON'T-WANT";
      // "wish <NP>" is not English; entity complements use want/would-like only.
      const v = pickVerb(ctx, comp.kind === 'clause' ? 'WANT' : 'WANT_NP');
      const mk = (wanted: string) =>
        simple(subj, (form) => {
          if (!neg) return `${form === 'finite' ? finite(v, subj) : v.base}${wanted}`;
          const fin = `${doNot(subj)} want${wanted}`;
          return form === 'finite' ? fin : `not want${wanted}`;
        });
      if (comp.kind === 'clause') {
        const inner = infinitival(ctx, comp.clause, subj);
        return mk(` ${inner}`);
      }
      if (comp.kind === 'quote') throw new Error('ERR_REALIZE: WANT quote complement');
      return mk(` ${objText(ctx, comp)}`);
    }
    case 'SAY': {
      const subj = realizeEntity(ctx, need(r.agent, 'agent'), true);
      const addr = r.addressee !== undefined ? ` to ${objText(ctx, r.addressee)}` : '';
      if (r.quote !== undefined) {
        if (r.quote.kind !== 'quote') throw new Error('ERR_REALIZE: SAY quote');
        return quotePred(ctx, subj, 'SAY', r.quote.clauses, r, addr);
      }
      const topic = r.topic !== undefined ? ` something about ${objText(ctx, r.topic)}` : ' something';
      return verbal(subj, 'SAY', `${topic}${addr}`);
    }
    case 'TRUE': {
      const u = need(r.undergoer, 'undergoer');
      if (u.kind === 'ref') {
        const np = mentionRef(ctx, u.index);
        return simple(np, (form) => (form === 'finite' ? `${copula(np)} true` : 'be true'));
      }
      if (u.kind === 'quote') {
        const inner = u.clauses.map((cl) => realizeClause(ctx, cl)).join(', and ');
        const np: NP = { text: 'it', plural: false, person: 3, key: null };
        return simple(np, (form) => (form === 'finite' ? `is true that ${inner}` : `be true that ${inner}`));
      }
      throw new Error('ERR_REALIZE: TRUE undergoer');
    }
    case 'BE-SOMEWHERE': {
      const subj = realizeEntity(ctx, need(r.undergoer, 'undergoer'), true);
      const locus = need(r.locus, 'locus');
      const where =
        locus.kind === 'prime' && locus.prime === 'HERE'
          ? 'here'
          : locus.kind === 'sp' && spIsPerson(locus)
            ? `where ${realizeSP(ctx, locus).text} is`
            : `at ${objText(ctx, locus)}`;
      return simple(subj, (form) => (form === 'finite' ? `${copula(subj)} ${where}` : `be ${where}`));
    }
    case 'THERE-IS': {
      const u = realizeEntity(ctx, need(r.undergoer, 'undergoer'), false);
      const np: NP = { text: 'there', plural: u.plural, person: 3, key: null };
      return simple(np, (form) =>
        form === 'finite' ? `${u.plural ? 'are' : 'is'} ${u.text}` : `be ${u.text}`,
      );
    }
    case 'BE-SPEC': {
      const subj = realizeEntity(ctx, need(r.undergoer, 'undergoer'), true);
      const a = need(r.attribute, 'attribute');
      let attr: string;
      if (a.kind === 'sp') attr = realizeSP(ctx, a).text;
      else if (a.kind === 'concept') attr = ctx.conceptPhrase(a.id, 'attribute');
      else throw new Error('ERR_REALIZE: BE-SPEC attribute');
      return simple(subj, (form) => (form === 'finite' ? `${copula(subj)} ${attr}` : `be ${attr}`));
    }
    case 'IS-MINE': {
      const subj = realizeEntity(ctx, need(r.undergoer, 'undergoer'), true);
      const mine = pick(ctx, ['mine', 'my own']);
      return simple(subj, (form) =>
        form === 'finite' ? `${copula(subj)} ${mine}` : `belong to me`,
      );
    }
    case 'WORDS': {
      const np: NP = { text: 'there', plural: true, person: 3, key: null };
      return simple(np, (form) => (form === 'finite' ? 'are words' : 'be words'));
    }
    default:
      throw new Error(`ERR_REALIZE: predicate ${c.pred}`);
  }
}

function objText(ctx: Ctx, f: Filler): string {
  return realizeEntity(ctx, f, false).text;
}

function doNot(subj: NP): string {
  return subj.person === 3 && !subj.plural ? 'does not' : 'do not';
}

/** "wants TO <vp>" / "wants <np> to <vp>" — subject-control collapse. */
function infinitival(ctx: Ctx, clause: Clause, controller: NP): string {
  if (clause.type === 'pred') {
    const subjF = subjectFiller(clause);
    const controlled = subjF !== null && fillerKey(ctx, subjF) === controller.key
      && controller.key !== null;
    const parts = predRealize(ctx, clause);
    // Control: the complement subject is the wanter — VP only ("wants to go").
    // predRealize still realized the subject internally (rng determinism, ref
    // mention bookkeeping); its text is simply not emitted here.
    return controlled ? `to ${parts.vp('base')}` : `${parts.subj.text} to ${parts.vp('base')}`;
  }
  // NOT over a controlled pred collapses to "wants not to <vp>"; every other
  // operator complement is realized as a finite paraphrase ("wants this: ...").
  if (clause.op === 'NOT' && clause.args.length === 1 && isClause(clause.args[0]!)) {
    const inner = infinitival(ctx, clause.args[0] as Clause, controller);
    if (inner.startsWith('to ')) return `not ${inner}`;
    return `this: ${realizeOpAsClause(ctx, clause)}`;
  }
  return `this: ${realizeClause(ctx, clause)}`;
}

function realizeOpAsClause(ctx: Ctx, c: OpClause): string {
  return realizeOp(ctx, c);
}

function subjectFiller(c: PredClause): Filler | null {
  const r = c.roles;
  return r.agent ?? r.experiencer ?? r.undergoer ?? null;
}

function fillerKey(_ctx: Ctx, f: Filler): string | null {
  if (f.kind === 'ref') return `ref:${f.index}`;
  if (f.kind === 'prime') return `prime:${f.prime}`;
  return null;
}

// ---------------------------------------------------------------------------
// Quotes (gist §4.6 re-anchoring: I = quoted thinker, NOW = quoted moment)
// ---------------------------------------------------------------------------

function quoteUsesYou(clauses: readonly Clause[]): boolean {
  let found = false;
  const walk = (n: unknown): void => {
    if (found || n === null || typeof n !== 'object') return;
    if (Array.isArray(n)) {
      n.forEach(walk);
      return;
    }
    const o = n as Record<string, unknown>;
    if (o['kind'] === 'prime' && o['prime'] === 'YOU') found = true;
    Object.values(o).forEach(walk);
  };
  clauses.forEach(walk);
  return found;
}

function quotePred(
  ctx: Ctx,
  subj: NP,
  pred: 'THINK' | 'SAY',
  clauses: readonly Clause[],
  _roles: PredClause['roles'],
  addr = '',
): PredRealization {
  // Indirect mode re-anchors I -> the thinker; a quote that itself uses YOU
  // (the quoted addressee) cannot be re-anchored faithfully -> force direct.
  const mode: 'direct' | 'indirect' =
    ctx.style.quote === 'indirect' && !quoteUsesYou(clauses) ? 'indirect' : 'direct';
  const prevDepth = ctx.quoteDepth;
  const prevMode = ctx.quoteMode;
  const prevSpeaker = ctx.speaker;
  ctx.quoteDepth += 1;
  ctx.quoteMode = mode;
  // Re-anchored "I" inside an INDIRECT quote must use the thinker's LATER
  // (anaphoric) form — the thinker was just mentioned as the matrix subject.
  let speaker = subj;
  if (subj.key !== null && subj.key.startsWith('ref:')) {
    const st = ctx.refs.get(Number(subj.key.slice(4)));
    if (st !== undefined) {
      speaker = { text: st.later, plural: st.laterPlural, person: st.person, key: subj.key };
    }
  }
  ctx.speaker = speaker;

  const bodyParts = clauses.map((cl) => realizeClause(ctx, cl));
  const body = mode === 'direct' ? bodyParts.join('; ') : bodyParts.join(', and that ');

  ctx.quoteDepth = prevDepth;
  ctx.quoteMode = prevMode;
  ctx.speaker = prevSpeaker;

  const verbs =
    pred === 'THINK'
      ? mode === 'direct'
        ? [V('think'), V('say to themselves', 'says to themselves')]
        : [V('think'), V('believe')]
      : [V('say')];
  const okVerbs = verbs.filter((v) => !banned(ctx, v.base) && !banned(ctx, v.s));
  const pool = okVerbs.length > 0 ? okVerbs : verbs;
  const v = pool[ctx.rng.nextBelow(pool.length)]!;
  const tail = adjunctTail(ctx, _roles);
  return {
    subj,
    vp: (form) => {
      const head = form === 'finite' ? finite(v, subj) : v.base;
      return mode === 'direct'
        ? `${head}${addr}: "${body}"${tail}`
        : `${head}${addr} that ${body}${tail}`;
    },
  };
}

// ---------------------------------------------------------------------------
// Clauses & operators
// ---------------------------------------------------------------------------

function isClause(a: OpArg): a is Clause {
  return (a as Clause).type === 'pred' || (a as Clause).type === 'op';
}

/** True if the subtree introduces (binds) any referent. */
function hasBind(n: unknown): boolean {
  if (n === null || typeof n !== 'object') return false;
  if (Array.isArray(n)) return n.some(hasBind);
  const o = n as Record<string, unknown>;
  if (typeof o['bind'] === 'number') return true;
  return Object.values(o).some(hasBind);
}

export function realizeClause(ctx: Ctx, c: Clause): string {
  if (c.type === 'pred') {
    const parts = predRealize(ctx, c);
    return `${parts.subj.text} ${parts.vp('finite')}`.replace(/\s+/g, ' ').trim();
  }
  return realizeOp(ctx, c);
}

function realizeOp(ctx: Ctx, c: OpClause): string {
  const args = c.args;
  switch (c.op) {
    case 'NOT': {
      const a = args[0]!;
      if (isClause(a) && a.type === 'pred' && a.pred !== "DON'T-WANT") {
        // (NOT over DON'T-WANT would yield "does not not want"; that case
        // falls through to the "it is not true that" wrapping below.)
        const parts = predRealize(ctx, a);
        const fin = parts.vp('finite');
        // copular/existential negation: "is X" -> "is not X"; else aux "does not".
        if (/^(is|are|am) /.test(fin)) {
          return `${parts.subj.text} ${fin.replace(/^(is|are|am) /, '$1 not ')}`;
        }
        return `${parts.subj.text} ${doNot(parts.subj)} ${parts.vp('base')}`;
      }
      if (isClause(a) && a.type === 'op' && a.op === 'CAN' && isClause(a.args[0]!) && (a.args[0] as Clause).type === 'pred') {
        const parts = predRealize(ctx, a.args[0] as PredClause);
        return `${parts.subj.text} cannot ${parts.vp('base')}`;
      }
      if (isClause(a)) return `${pick(ctx, ['it is not true that', 'it is not the case that'])} ${realizeClause(ctx, a)}`;
      throw new Error('ERR_REALIZE: NOT arg');
    }
    case 'CAN': {
      const a = args[0]!;
      if (isClause(a) && a.type === 'pred') {
        const parts = predRealize(ctx, a);
        const aux = pick(ctx, ['can', 'is able to']);
        if (aux === 'is able to' && (parts.subj.plural || parts.subj.person !== 3)) {
          return `${parts.subj.text} can ${parts.vp('base')}`;
        }
        return `${parts.subj.text} ${aux} ${parts.vp('base')}`;
      }
      if (isClause(a)) return `it can be that ${realizeClause(ctx, a)}`;
      throw new Error('ERR_REALIZE: CAN arg');
    }
    case 'MAYBE': {
      const a = args[0]!;
      if (isClause(a)) return `${pick(ctx, ['maybe', 'it may be that'])} ${realizeClause(ctx, a)}`;
      throw new Error('ERR_REALIZE: MAYBE arg');
    }
    case 'IF':
    case 'BECAUSE':
    case 'WHEN': {
      // BECAUSE(A, B): A is the ground/cause, B the consequence (kernel-v0
      // 'cause': BECAUSE(X happens, Y happens) = "because X happens, Y
      // happens"); IF(A, B) = if A then B; WHEN(A, B) = when A, B.
      // The clause order is DRAWN FIRST and the clauses realized in TEXTUAL
      // order, so referent intro/later forms track the reader's view.
      const [a, b] = [args[0]!, args[1]!];
      if (!isClause(a) || !isClause(b)) throw new Error(`ERR_REALIZE: ${c.op} args`);
      const conj = c.op === 'IF' ? 'if' : c.op === 'BECAUSE' ? 'because' : 'when';
      // A flip may not move a referent-INTRODUCING SP (bind) after an
      // anaphoric mention of that referent — forbid flips whenever either arm
      // binds (declared frame referents are pre-registered, so registration
      // state cannot distinguish the hazardous case; be conservative).
      const forward = hasBind(a) || hasBind(b) ? true : ctx.rng.nextBelow(2) === 0;
      if (forward) {
        const fa = realizeClause(ctx, a);
        const fb = realizeClause(ctx, b);
        return c.op === 'IF' ? `if ${fa}, then ${fb}` : `${conj} ${fa}, ${fb}`;
      }
      const fb = realizeClause(ctx, b);
      const fa = realizeClause(ctx, a);
      return `${fb} ${conj} ${fa}`;
    }
    case 'AFTER':
    case 'BEFORE': {
      // Temporal2: args[0] = anchor (entity), args[1] = clause holding after/before it.
      const [anchor, cl] = [args[0]!, args[1]!];
      if (!isClause(cl)) throw new Error(`ERR_REALIZE: ${c.op} clause arg`);
      const fc = realizeClause(ctx, cl);
      let anchorText: string | null;
      if (!isClause(anchor) && anchor.kind === 'prime' && anchor.prime === 'NOW') anchorText = null;
      else if (!isClause(anchor)) anchorText = realizeEntity(ctx, anchor as Filler, false).text;
      else throw new Error(`ERR_REALIZE: ${c.op} anchor arg`);
      if (anchorText === null) {
        const adv =
          c.op === 'AFTER'
            ? pick(ctx, ['after this', 'later on'])
            : pick(ctx, ['before now', 'earlier']);
        return `${adv}, ${fc}`;
      }
      // Varied anchored forms (also thins accidental n-gram runs against the
      // kernel-v0 glosses, which invariably write "after this time ...").
      const pattern =
        c.op === 'AFTER'
          ? pick(ctx, ['after {a},', 'once {a} has passed,', 'from {a} on,'])
          : pick(ctx, ['before {a},', 'earlier than {a},']);
      return `${pattern.replace('{a}', anchorText)} ${fc}`;
    }
    case 'LIKE': {
      const [a, b] = [args[0]!, args[1]!];
      const ta = isClause(a) ? realizeClause(ctx, a) : realizeEntity(ctx, a as Filler, true).text;
      const tb = isClause(b) ? `how it is when ${realizeClause(ctx, b)}` : realizeEntity(ctx, b as Filler, false).text;
      return `${ta} is like ${tb}`;
    }
    case 'VERY':
    case 'MORE': {
      const a = args[0]!;
      if (!isClause(a) && a.kind === 'prime') {
        const adjs = ADJ[a.prime];
        if (adjs === undefined) throw new Error(`ERR_REALIZE: ${c.op} over ${a.prime}`);
        const adj = c.op === 'MORE' ? ADJ_MORE[a.prime]! : `very ${pick(ctx, adjs)}`;
        return `something is ${adj}`;
      }
      throw new Error(`ERR_REALIZE: ${c.op} arg`);
    }
    default:
      throw new Error(`ERR_REALIZE: operator ${(c as OpClause).op}`);
  }
}

// ---------------------------------------------------------------------------
// Top level
// ---------------------------------------------------------------------------

export function realizeExplication(e: Explication, opts: RealizeOptions): string {
  const style = STYLES[opts.style];
  if (style === undefined) throw new Error(`ERR_REALIZE: style ${opts.style}`);
  const ctx: Ctx = {
    rng: opts.rng,
    style,
    bannedLemmas: opts.bannedLemmas,
    conceptPhrase: opts.conceptPhrase,
    refs: new Map(),
    kindCounts: new Map(),
    quoteDepth: 0,
    quoteMode: 'direct',
    speaker: null,
    subjKey: null,
  };
  // Frame-implicit referents first (declaration order), styled naming for r1.
  for (const decl of e.referents) {
    registerRef(ctx, decl.index, decl.refKind, decl.index === 1 ? style : undefined);
  }

  const lead =
    e.frame === 'WhenTrue'
      ? pick(ctx, style.leadWhenTrue)
      : e.frame === 'RelationalSchema'
        ? pick(ctx, style.leadRelational)
        : pick(ctx, style.leadInstance);

  const parts = e.clauses.map((c) => realizeClause(ctx, c));
  let out = lead;
  parts.forEach((p, i) => {
    if (i === 0) out += p;
    else out += `${style.joiners[ctx.rng.nextBelow(style.joiners.length)]!}${p}`;
  });
  // Sentence-case after '. ' joins; keep quoted bodies untouched otherwise.
  out = out.replace(/\s+/g, ' ').trim();
  out = out.charAt(0).toUpperCase() + out.slice(1);
  out = out.replace(/([.!?] )([a-z])/g, (_m, a: string, b: string) => a + b.toUpperCase());
  if (!/[.!?"]$/.test(out)) out += '.';
  return out;
}
