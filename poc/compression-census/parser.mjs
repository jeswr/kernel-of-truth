/**
 * B-E0 census instrument — deterministic maximal-parseable-fragment parser
 * over mapper-annotated English text (idea B roll-up engagement census,
 * docs/next/io-compression-ideas.md §3.7 B-E0; bead kernel-of-truth-5iu).
 *
 * SCOPE HONESTY (binding on every number this instrument produces): this is
 * a CONSERVATIVE, fail-closed v0 parser. It recognises exactly the closed
 * kot-ast/1 grammar patterns listed below and ABSTAINS on everything else
 * (design rule io-compression-ideas.md §3.1: "the deterministic parser
 * either produces a valid capped AST ... or abstains and the text passes
 * through untouched. There is no approximate roll-up path"). Engagement
 * measured with it is engagement OF THIS INSTRUMENT on THIS corpus under
 * THIS kernel instance — not "the grammar's" engagement ceiling, and not any
 * other corpus's. Every lossy surface convention is marked [STIPULATED].
 *
 * Layering: content words resolve through the PINNED mapper
 * (@jeswr/kernel-mapper, abstain-on-ambiguity inherited unchanged per
 * io-compression-ideas.md §2.1); the closed-class syntax below (copulas,
 * the 19 predicate-prime verb inflections, operators, articles, pronouns)
 * is this instrument's own closed table, since the mapper deliberately
 * abstains on copula polysemy and does not do syntax.
 *
 * Recognised patterns (reporting strata pre-named in the design doc):
 *   is-a           : "X is (not) (a|an) Y", "X is a kind/part of Y",
 *                    "there is X" (BE-SPEC / kind-part frames / THERE-IS)
 *   clause-AND     : "C1 and C2 (and C3 ...)" — clause sequencing, incl.
 *                    subject-elided C2 via referent binding
 *   operator-cmplx : not / can / cannot / maybe / if..then / because / when
 *                    (NOT, CAN, MAYBE, IF, BECAUSE, WHEN); will -> AFTER@NOW
 *                    and past tense -> BEFORE@NOW as time adjuncts
 *   simple-clause  : a single closed-frame predicate clause (DO, HAPPEN,
 *                    MOVE, THINK*, KNOW, WANT, DON'T-WANT, FEEL, SEE, HEAR,
 *                    SAY, LIVE†, DIE, BE-SOMEWHERE(here), THERE-IS, BE-SPEC)
 *
 * OR-forfeit (the §3.1 decision number): a span that would parse but for a
 * disjunctive connective — clause-level ("C1 or C2", both sides parse) and
 * NP-level ("A or B" inside an otherwise-parsing NP) counted separately.
 *
 * Deliberate fail-closed conventions ([STIPULATED], each surfaced in the
 * abstain-cause histogram so the forfeited mass is visible):
 *   - 3rd-person pronouns / possessives abstain (anaphora is not losslessly
 *     expressible in a self-contained composite);
 *   - bare plurals abstain (plural licensed only under an explicit
 *     quantifier: two/some/all/many/few);
 *   - open-class adjectives abstain as SP modifiers (SP mods are the closed
 *     GOOD/BAD/BIG/SMALL set only);
 *   - "the": STRICT profile abstains; PERMISSIVE-DET maps the/that/those ->
 *     det THIS (a flagged, LOSSY definiteness convention — reported as a
 *     separate census cell, never merged with STRICT);
 *   - articles a/an are consumed as the SP indefinite-singular default;
 *   - past tense -> time BEFORE@NOW, "will" -> time AFTER@NOW (adjunct
 *     convention); progressive/perfect aspect abstains;
 *   - "live"+locative abstains (LIVE is the life-death prime, not "reside");
 *   - quoted speech abstains (quote re-anchoring out of v0 scope).
 */

const PAST = 'past';
const PRES = 'pres';

/** Closed inflection table for the predicate-prime verbs (v0). */
const VERB_TABLE = new Map([
  ['do', { pred: 'DO', tense: PRES }],
  ['does', { pred: 'DO', tense: PRES }],
  ['did', { pred: 'DO', tense: PAST }],
  ['happen', { pred: 'HAPPEN', tense: PRES }],
  ['happens', { pred: 'HAPPEN', tense: PRES }],
  ['happened', { pred: 'HAPPEN', tense: PAST }],
  ['move', { pred: 'MOVE', tense: PRES }],
  ['moves', { pred: 'MOVE', tense: PRES }],
  ['moved', { pred: 'MOVE', tense: PAST }],
  ['think', { pred: 'THINK', tense: PRES }],
  ['thinks', { pred: 'THINK', tense: PRES }],
  ['thought', { pred: 'THINK', tense: PAST }],
  ['know', { pred: 'KNOW', tense: PRES }],
  ['knows', { pred: 'KNOW', tense: PRES }],
  ['knew', { pred: 'KNOW', tense: PAST }],
  ['want', { pred: 'WANT', tense: PRES }],
  ['wants', { pred: 'WANT', tense: PRES }],
  ['wanted', { pred: 'WANT', tense: PAST }],
  ['feel', { pred: 'FEEL', tense: PRES }],
  ['feels', { pred: 'FEEL', tense: PRES }],
  ['felt', { pred: 'FEEL', tense: PAST }],
  ['see', { pred: 'SEE', tense: PRES }],
  ['sees', { pred: 'SEE', tense: PRES }],
  ['saw', { pred: 'SEE', tense: PAST }],
  ['hear', { pred: 'HEAR', tense: PRES }],
  ['hears', { pred: 'HEAR', tense: PRES }],
  ['heard', { pred: 'HEAR', tense: PAST }],
  ['say', { pred: 'SAY', tense: PRES }],
  ['says', { pred: 'SAY', tense: PRES }],
  ['said', { pred: 'SAY', tense: PAST }],
  ['live', { pred: 'LIVE', tense: PRES }],
  ['lives', { pred: 'LIVE', tense: PRES }],
  ['lived', { pred: 'LIVE', tense: PAST }],
  ['die', { pred: 'DIE', tense: PRES }],
  ['dies', { pred: 'DIE', tense: PRES }],
  ['died', { pred: 'DIE', tense: PAST }],
]);

const COPULA = new Map([
  ['is', PRES],
  ['am', PRES],
  ['are', PRES],
  ['was', PAST],
  ['were', PAST],
]);

/** Locative prepositions that trigger the LIVE sense guard / dangling-PP end. */
const PREPOSITIONS = new Set([
  'in', 'on', 'at', 'to', 'with', 'into', 'onto', 'under', 'over', 'from',
  'of', 'by', 'for', 'about', 'around', 'through', 'near', 'behind', 'up',
  'down', 'out', 'off', 'inside', 'outside', 'above', 'below', 'across',
]);

const PRONOUN_ABSTAIN = new Set([
  'he', 'she', 'it', 'they', 'we', 'him', 'her', 'them', 'us',
  'his', 'hers', 'its', 'their', 'theirs', 'our', 'ours', 'my', 'your',
]);

const QUANT_WORDS = new Map([
  ['one', 'ONE'],
  ['two', 'TWO'],
  ['some', 'SOME'],
  ['all', 'ALL'],
  ['many', 'MUCH~MANY'],
  ['much', 'MUCH~MANY'],
  ['few', 'LITTLE~FEW'],
]);

const MOD_WORDS = new Map([
  ['good', 'GOOD'],
  ['bad', 'BAD'],
  ['big', 'BIG'],
  ['small', 'SMALL'],
]);

/** Fixed prime heads reachable without the mapper (closed indexicals etc.). */
const FIXED_NP = new Map([
  ['i', { kind: 'prime', prime: 'I' }],
  ['me', { kind: 'prime', prime: 'I' }],
  ['you', { kind: 'prime', prime: 'YOU' }],
]);

const FIXED_HEADS = new Map([
  ['someone', 'SOMEONE'],
  ['somebody', 'SOMEONE'],
  ['something', 'SOMETHING~THING'],
  ['people', 'PEOPLE'],
]);

/** Substantive primes usable as bare SP heads (encoder lexicon.ts). */
const SUBSTANTIVE_HEADS = new Set([
  'I', 'YOU', 'SOMEONE', 'SOMETHING~THING', 'PEOPLE', 'BODY', 'WORDS',
  'WHEN~TIME', 'WHERE~PLACE', 'MOMENT', 'SIDE',
]);

/**
 * A parse failure with a census cause code. Codes are the abstain-cause
 * histogram of the report; they are diagnostics, not DVs.
 */
class Abstain extends Error {
  constructor(cause) {
    super(cause);
    this.cause_ = cause;
  }
}
const abstain = (cause) => {
  throw new Abstain(cause);
};

/**
 * Parser state over ONE sentence: `toks` = mapper AnnotatedTokens (word and
 * non-word), `i` = cursor over positions. All methods deterministic.
 */
class SentenceParser {
  /**
   * @param toks   mapper AnnotatedToken[] for the sentence
   * @param profile 'strict' | 'permissive-det'
   */
  constructor(toks, profile) {
    this.toks = toks;
    this.profile = profile;
    this.i = 0;
    this.referents = []; // ReferentDecl beyond the frame-implicit x1
    this.orForfeits = []; // {level:'clause'|'np', fromTok, toTok}
    this.subjectRef = null; // {index, filler} for elided-subject conjuncts
  }

  peekWord(k = 0) {
    let j = this.i;
    let seen = 0;
    while (j < this.toks.length) {
      const t = this.toks[j];
      if (t.isWord) {
        if (seen === k) return { tok: t, pos: j };
        seen++;
      } else if (t.surface.trim() !== ',' && /[.!?;:]/.test(t.surface)) {
        return undefined; // clause-final punctuation blocks lookahead
      }
      j++;
    }
    return undefined;
  }

  /** Advance to and consume the next word token; fail on punctuation other than comma. */
  nextWord() {
    while (this.i < this.toks.length) {
      const t = this.toks[this.i];
      if (t.isWord) {
        this.i++;
        return t;
      }
      if (t.surface.trim() === ',' || t.surface.trim() === '') {
        this.i++;
        continue;
      }
      abstain('punctuation-break');
    }
    abstain('sentence-end');
  }

  atComma() {
    let j = this.i;
    while (j < this.toks.length && !this.toks[j].isWord) {
      if (this.toks[j].surface.trim() === ',') return true;
      j++;
    }
    return false;
  }

  skipCommas() {
    while (this.i < this.toks.length && !this.toks[this.i].isWord) {
      const s = this.toks[this.i].surface.trim();
      if (s === ',' || s === '') this.i++;
      else break;
    }
  }

  /** True when nothing but non-clause-material remains (sentence exhausted). */
  exhausted() {
    for (let j = this.i; j < this.toks.length; j++) {
      if (this.toks[j].isWord) return false;
    }
    return true;
  }

  // -------------------------------------------------------------------------
  // NP -> SP
  // -------------------------------------------------------------------------

  /**
   * Parse a substantive phrase. Returns an SP or fixed prime filler
   * ({kind:'prime',prime:'I'|'YOU'}). Fail-closed per header conventions.
   */
  parseNP({ allowBind = false } = {}) {
    const first = this.peekWord(0);
    if (first === undefined) abstain('sentence-end');
    const w0 = first.tok.norm;

    if (FIXED_NP.has(w0)) {
      this.nextWord();
      return FIXED_NP.get(w0);
    }
    if (PRONOUN_ABSTAIN.has(w0)) abstain('pronoun-anaphor');
    if (w0 === 'everyone' || w0 === 'everybody') {
      this.nextWord();
      return { kind: 'sp', quant: 'ALL', head: { kind: 'primeHead', prime: 'SOMEONE' } };
    }
    if (w0 === 'everything') {
      this.nextWord();
      return { kind: 'sp', quant: 'ALL', head: { kind: 'primeHead', prime: 'SOMETHING~THING' } };
    }

    let det;
    let quant;
    const mods = [];
    let sawArticle = false;

    // determiner / article / quantifier / closed-mod prefix loop
    for (;;) {
      const p = this.peekWord(0);
      if (p === undefined) abstain('sentence-end');
      const w = p.tok.norm;
      if (w === 'a' || w === 'an') {
        // [STIPULATED] indefinite article consumed as the SP indefinite-
        // singular default (no det/quant emitted).
        this.nextWord();
        sawArticle = true;
        continue;
      }
      if (w === 'the') {
        const nx = this.peekWord(1);
        if (nx !== undefined && nx.tok.norm === 'same') {
          this.nextWord();
          this.nextWord();
          if (det !== undefined) abstain('double-determiner');
          det = 'THE-SAME';
          continue;
        }
        if (this.profile === 'permissive-det') {
          // [STIPULATED, LOSSY] definite article -> det THIS (permissive cell only)
          this.nextWord();
          if (det === undefined) det = 'THIS';
          continue;
        }
        abstain('definite-article');
      }
      if (w === 'this' || w === 'these') {
        this.nextWord();
        if (det !== undefined) abstain('double-determiner');
        det = 'THIS';
        continue;
      }
      if (w === 'that' || w === 'those') {
        if (this.profile === 'permissive-det') {
          this.nextWord();
          if (det !== undefined) abstain('double-determiner');
          det = 'THIS'; // [STIPULATED, LOSSY] distal -> THIS (permissive only)
          continue;
        }
        abstain('that-demonstrative');
      }
      if (w === 'other' || w === 'another') {
        this.nextWord();
        if (det !== undefined) abstain('double-determiner');
        det = 'OTHER~ELSE~ANOTHER';
        continue;
      }
      if (QUANT_WORDS.has(w) && quant === undefined && det === undefined && !sawArticle) {
        this.nextWord();
        quant = QUANT_WORDS.get(w);
        continue;
      }
      if (w === 'very' || w === 'more') {
        const nx = this.peekWord(1);
        if (nx !== undefined && MOD_WORDS.has(nx.tok.norm)) {
          this.nextWord();
          const mw = this.nextWord();
          this.pushMod(mods, { mod: MOD_WORDS.get(mw.norm), intensifier: w === 'very' ? 'VERY' : 'MORE' });
          continue;
        }
        abstain('unsupported-modifier');
      }
      if (MOD_WORDS.has(w)) {
        // closed mod — but only if a head candidate follows (else it is
        // predicative: "the dog is big" handled by the copula path)
        const nx = this.peekWord(1);
        if (nx === undefined) abstain('sentence-end');
        this.nextWord();
        this.pushMod(mods, { mod: MOD_WORDS.get(w) });
        continue;
      }
      if (w === 'little') abstain('little-ambiguous'); // LITTLE~FEW vs SMALL (mapper double-listing)
      break;
    }

    // head word: resolve via the pinned mapper annotation
    const headP = this.peekWord(0);
    if (headP === undefined) abstain('sentence-end');
    const headTok = headP.tok;
    const w = headTok.norm;

    // kind-of / part-of frames: "kind of Y" / "part of Y"
    if ((w === 'kind' || w === 'part') && this.peekWord(1)?.tok.norm === 'of') {
      this.nextWord();
      this.nextWord();
      const inner = this.parseNP({});
      if (inner.kind === 'prime') abstain('kindpart-of-indexical');
      return {
        kind: 'sp',
        ...(det !== undefined ? { det } : {}),
        ...(quant !== undefined ? { quant } : {}),
        ...(mods.length > 0 ? { mods } : {}),
        head: { kind: w === 'kind' ? 'kindFrame' : 'partFrame', of: inner },
      };
    }

    if (FIXED_HEADS.has(w)) {
      this.nextWord();
      this.checkNpOr();
      const sp = {
        kind: 'sp',
        ...(det !== undefined ? { det } : {}),
        ...(quant !== undefined ? { quant } : {}),
        ...(mods.length > 0 ? { mods } : {}),
        head: { kind: 'primeHead', prime: FIXED_HEADS.get(w) },
      };
      return this.maybeBind(sp, allowBind, 'prime');
    }

    const d = headTok.decision;
    if (d.kind === 'abstain') abstain('mapper-abstain');
    if (d.kind === 'none') abstain('unmapped-word');
    if (d.kind === 'prime') {
      if (!SUBSTANTIVE_HEADS.has(d.prime)) abstain('prime-not-substantive-head');
      this.consumePhrase(headTok);
      this.checkNpOr();
      const sp = {
        kind: 'sp',
        ...(det !== undefined ? { det } : {}),
        ...(quant !== undefined ? { quant } : {}),
        ...(mods.length > 0 ? { mods } : {}),
        head: { kind: 'primeHead', prime: d.prime },
      };
      return this.maybeBind(sp, allowBind, 'prime');
    }
    // concept head
    const plural = this.isPluralSurface(headTok);
    if (plural && quant === undefined) abstain('bare-plural'); // [STIPULATED] plural licensed by explicit quantifier only
    this.consumePhrase(headTok);
    this.checkNpOr();
    const sp = {
      kind: 'sp',
      ...(det !== undefined ? { det } : {}),
      ...(quant !== undefined ? { quant } : {}),
      ...(mods.length > 0 ? { mods } : {}),
      head: { kind: 'conceptHead', id: d.conceptId },
    };
    return this.maybeBind(sp, allowBind, 'concept');
  }

  /**
   * NP-level OR-forfeit probe (head just parsed, next word 'or').
   * Disambiguation order: if a full CLAUSE parses after 'or', the
   * disjunction is clause-level — return normally and let parseFragment's
   * connective loop record it. If only an NP parses, the disjunction is
   * inside the SP — record the NP-level forfeit and abstain (no SP
   * coordination exists at v0). If neither parses, the NP simply ends.
   */
  checkNpOr() {
    const p = this.peekWord(0);
    if (p === undefined || p.tok.norm !== 'or') return;
    const from = this.i;
    const save = this.snapshot();
    let clauseParses = false;
    try {
      this.nextWord(); // 'or'
      this.parseClause();
      clauseParses = true;
    } catch (e) {
      if (!(e instanceof Abstain)) throw e;
    }
    this.restore(save);
    if (clauseParses) return; // clause-level: handled by the connective loop
    let forfeit = null;
    try {
      this.nextWord(); // 'or'
      this.parseNP({});
      forfeit = { level: 'np', fromTok: from, toTok: this.i };
    } catch (e) {
      if (!(e instanceof Abstain)) throw e;
    }
    this.restore(save);
    if (forfeit !== null) {
      this.orForfeits.push(forfeit); // survives the restore
      abstain('np-or'); // disjunction inside an SP is not expressible at v0
    }
    // 'or' followed by nothing parseable: the NP ends cleanly before it.
  }

  /**
   * Duplicate (intensifier+mod) pairs cannot round-trip (validate.ts
   * ERR_SP_MOD: doubled superposition weight) — "big big dog" abstains.
   */
  pushMod(mods, m) {
    const key = `${m.intensifier ?? ''}+${m.mod}`;
    if (mods.some((x) => `${x.intensifier ?? ''}+${x.mod}` === key)) abstain('duplicate-modifier');
    mods.push(m);
  }

  /** Multi-token mapper phrases consume all their tokens. */
  consumePhrase(tok) {
    const len = tok.phraseLen ?? 1;
    let consumed = 0;
    while (consumed < len) {
      const t = this.nextWord();
      consumed += 1;
      if (t.phraseLen !== len) break; // defensive; mapper phrases are contiguous
    }
  }

  isPluralSurface(tok) {
    // CONSERVATIVE [STIPULATED]: any inflected surface in head position
    // (surface != mapped lemma) is treated as plural/inflected and requires
    // an explicit quantifier licence — irregular plurals (children/mice)
    // included, at the cost of some false positives.
    return tok.norm !== tok.lemma;
  }

  /** Bind the subject SP to a referent for elided-subject conjuncts. */
  maybeBind(sp, allowBind, headClass) {
    if (!allowBind) return sp;
    const index = 2 + this.referents.length; // x1 is frame-implicit
    if (index > 32) abstain('referent-cap');
    const refKind =
      headClass === 'prime' && (sp.head.prime === 'SOMEONE' || sp.head.prime === 'PEOPLE')
        ? 'SomeoneRef'
        : 'SomethingRef'; // [STIPULATED] concept heads default to SomethingRef
    // bind lazily: only attach when an elided conjunct actually references it
    return { ...sp, __pendingBind: { index, refKind } };
  }

  snapshot() {
    return { i: this.i, refs: this.referents.length, forfeits: this.orForfeits.length };
  }
  restore(s) {
    this.i = s.i;
    this.referents.length = s.refs;
    this.orForfeits.length = s.forfeits;
  }

  // -------------------------------------------------------------------------
  // Clause parsing
  // -------------------------------------------------------------------------

  /** Wrap tense into the clause's time adjunct ([STIPULATED] convention). */
  applyTense(clause, tense, future) {
    if (clause.type !== 'pred') return clause;
    if (future) {
      if (clause.roles.time !== undefined) abstain('time-adjunct-conflict');
      return { ...clause, roles: { ...clause.roles, time: { kind: 'temporal', op: 'AFTER', anchor: { kind: 'prime', prime: 'NOW' } } } };
    }
    if (tense === PAST) {
      if (clause.roles.time !== undefined) abstain('time-adjunct-conflict');
      return { ...clause, roles: { ...clause.roles, time: { kind: 'temporal', op: 'BEFORE', anchor: { kind: 'prime', prime: 'NOW' } } } };
    }
    return clause;
  }

  /**
   * Parse one core clause: subject NP + verb group + complements.
   * `subject` (optional) = pre-parsed subject filler for elided conjuncts.
   */
  parseClause(subject = null) {
    let subj = subject;
    if (subj === null) {
      // "there is/was X" existential
      const p0 = this.peekWord(0);
      if (p0 !== undefined && p0.tok.norm === 'there') {
        const p1 = this.peekWord(1);
        if (p1 !== undefined && COPULA.has(p1.tok.norm)) {
          this.nextWord();
          const cop = this.nextWord();
          let neg = false;
          if (this.peekWord(0)?.tok.norm === 'not') {
            this.nextWord();
            neg = true;
          }
          const np = this.parseNP({});
          let clause = { type: 'pred', pred: 'THERE-IS', roles: { undergoer: np } };
          clause = this.applyTense(clause, COPULA.get(cop.norm), false);
          return neg ? { type: 'op', op: 'NOT', args: [clause] } : clause;
        }
      }
      subj = this.parseNP({ allowBind: true });
    }

    // verb group: [will] [can] [not] V | copula [not]
    let future = false;
    let canOp = false;
    let negOp = false;

    let vp = this.peekWord(0);
    if (vp === undefined) abstain('no-verb');
    if (vp.tok.norm === 'will') {
      this.nextWord();
      future = true;
      vp = this.peekWord(0);
      if (vp === undefined) abstain('no-verb');
    }
    if (vp.tok.norm === 'can') {
      this.nextWord();
      canOp = true;
      vp = this.peekWord(0);
      if (vp === undefined) abstain('no-verb');
    }
    if (vp.tok.norm === 'not') {
      if (!canOp && !future) abstain('bare-not'); // "not" needs do-support or modal here
      this.nextWord();
      negOp = true;
      vp = this.peekWord(0);
      if (vp === undefined) abstain('no-verb');
    }

    const vw = vp.tok.norm;

    // Copula path
    if (COPULA.has(vw)) {
      if (canOp || future) abstain('modal-copula'); // "can be", "will be" out of v0
      this.nextWord();
      let neg = false;
      if (this.peekWord(0)?.tok.norm === 'not') {
        this.nextWord();
        neg = true;
      }
      const clause = this.parseCopulaComplement(subj, COPULA.get(vw));
      return neg ? { type: 'op', op: 'NOT', args: [clause] } : clause;
    }

    // do-support: do/does/did + not + V — with the DON'T-WANT special case
    // (a prime of its own; NOT(WANT) would misrepresent the NSM inventory)
    let tenseOverride = null;
    let dontWant = false;
    if ((vw === 'do' || vw === 'does' || vw === 'did') && this.peekWord(1)?.tok.norm === 'not') {
      const mainV = this.peekWord(2);
      const aux = this.nextWord();
      this.nextWord(); // not
      tenseOverride = VERB_TABLE.get(aux.norm).tense;
      if (mainV !== undefined && VERB_TABLE.get(mainV.tok.norm)?.pred === 'WANT') {
        dontWant = true; // consume as the DON'T-WANT predicate prime
      } else {
        negOp = true;
      }
      vp = this.peekWord(0);
      if (vp === undefined) abstain('no-verb');
    }

    const entry = VERB_TABLE.get(vp.tok.norm);
    if (entry === undefined) {
      // open-class verb (runs, played, ...) — not a predicate prime
      abstain('open-class-verb');
    }
    this.nextWord();
    const tense = tenseOverride ?? (canOp || future ? PRES : entry.tense);
    if ((canOp || future) && entry.tense === PAST) abstain('modal-past-verb');

    const pred = dontWant ? "DON'T-WANT" : entry.pred;
    let clause = this.parsePredComplements(subj, pred);
    clause = this.applyTense(clause, tense, future);
    if (canOp) clause = { type: 'op', op: 'CAN', args: [clause] };
    if (negOp) clause = { type: 'op', op: 'NOT', args: [clause] };
    return clause;
  }

  /** Copula complements: kind/part-of, NP (BE-SPEC), here (BE-SOMEWHERE). */
  parseCopulaComplement(subj, tense) {
    const p = this.peekWord(0);
    if (p === undefined) abstain('copula-no-complement');
    const w = p.tok.norm;
    if (w === 'here') {
      // BE-SOMEWHERE's locus core slot takes entities only (validate.ts
      // slotKindAccepts); HERE is licensed for the place ADJUNCT, not the
      // locus. "X is here" is therefore not expressible at v0 — abstain.
      abstain('copula-locative-unsupported');
    }
    if (MOD_WORDS.has(w) && (this.peekWord(1) === undefined || !this.wordContinuesNp(1))) {
      // "X is good/big" — bare closed-mod predication has no valid AST shape
      // (BE-SPEC attribute must be an SP/KIND-frame/concept)
      abstain('bare-mod-predication');
    }
    const np = this.parseNP({});
    if (np.kind === 'prime') abstain('copula-indexical-attribute'); // "X is you" out of v0
    const clause = { type: 'pred', pred: 'BE-SPEC', roles: { undergoer: subj, attribute: np } };
    return this.applyTense(clause, tense, false);
  }

  wordContinuesNp(k) {
    const p = this.peekWord(k);
    if (p === undefined) return false;
    const w = p.tok.norm;
    return !PREPOSITIONS.has(w) && w !== 'and' && w !== 'or' && w !== 'because';
  }

  /** Non-copula predicate complements, per the closed valency frames. */
  parsePredComplements(subj, pred) {
    const roles = {};
    const nextIsNp = () => {
      const p = this.peekWord(0);
      if (p === undefined) return false;
      const w = p.tok.norm;
      if (PREPOSITIONS.has(w) || w === 'and' || w === 'or' || w === 'because' || w === 'when' || w === 'if' || w === 'then' || w === 'so' || w === 'but') return false;
      if (COPULA.has(w) || VERB_TABLE.has(w) || w === 'will' || w === 'can' || w === 'not') return false;
      return true;
    };

    switch (pred) {
      case 'DO': {
        roles.agent = subj;
        if (nextIsNp()) roles.undergoer = this.parseNP({});
        break;
      }
      case 'HAPPEN': {
        roles.undergoer = subj; // "X happened"
        break;
      }
      case 'MOVE':
      case 'DIE': {
        roles.undergoer = subj;
        if (nextIsNp()) abstain('unexpected-object');
        break;
      }
      case 'LIVE': {
        // sense guard: LIVE is the life-death prime; "lived in/at ..." is the
        // reside sense and must not be mapped
        const p = this.peekWord(0);
        if (p !== undefined && PREPOSITIONS.has(p.tok.norm)) abstain('live-sense-guard');
        if (nextIsNp()) abstain('unexpected-object');
        roles.undergoer = subj;
        break;
      }
      case 'THINK': {
        roles.experiencer = subj;
        const p = this.peekWord(0);
        if (p !== undefined && (p.tok.norm === 'that' || p.tok.norm === 'about')) abstain('think-complement-unsupported');
        if (nextIsNp()) abstain('think-complement-unsupported');
        break;
      }
      case 'KNOW': {
        roles.experiencer = subj;
        const p = this.peekWord(0);
        if (p !== undefined && p.tok.norm === 'that' && this.peekWord(1) !== undefined) {
          this.nextWord();
          roles.complement = { kind: 'clause', clause: this.parseClause() };
        } else if (nextIsNp()) {
          roles.topic = this.parseNP({});
        }
        break;
      }
      case 'WANT':
      case "DON'T-WANT": {
        roles.experiencer = subj;
        const p = this.peekWord(0);
        if (p !== undefined && p.tok.norm === 'to') {
          this.nextWord();
          // infinitival complement: elided subject = matrix subject (coreference
          // via referent binding when the subject is bindable)
          const inner = this.parseElidedClause(subj);
          roles.complement = { kind: 'clause', clause: inner.clause };
          roles.experiencer = inner.subject; // possibly rebound with bind
        } else {
          roles.complement = this.parseNP({});
        }
        break;
      }
      case 'FEEL': {
        roles.experiencer = subj;
        const p = this.peekWord(0);
        if (p === undefined) abstain('feel-no-attribute');
        const w = p.tok.norm;
        if (w === 'good' || w === 'bad') {
          this.nextWord();
          roles.attribute = { kind: 'prime', prime: w === 'good' ? 'GOOD' : 'BAD' };
        } else {
          abstain('feel-attribute-unsupported');
        }
        break;
      }
      case 'SEE':
      case 'HEAR': {
        roles.experiencer = subj;
        roles.stimulus = this.parseNP({});
        break;
      }
      case 'SAY': {
        roles.agent = subj;
        const p = this.peekWord(0);
        if (p !== undefined && nextIsNp()) abstain('say-complement-unsupported');
        // quoted speech abstains upstream (quote punctuation breaks the clause)
        break;
      }
      default:
        abstain('unsupported-predicate');
    }
    return { type: 'pred', pred, roles };
  }

  /**
   * Elided-subject embedded clause ("wanted to see the dog"): the matrix
   * subject is re-used. If it is a bindable SP, bind it to a referent and
   * reference it from the inner clause (exact coreference); indexicals (I/
   * YOU) are simply repeated (they are indexical, not anaphoric).
   */
  parseElidedClause(subj) {
    if (subj.kind === 'prime') {
      const clause = this.parseClauseWithSubject({ kind: 'prime', prime: subj.prime });
      return { clause, subject: subj };
    }
    if (subj.kind === 'ref') {
      // already a bound referent (nested elision): reuse the ref directly
      const clause = this.parseClauseWithSubject({ kind: 'ref', index: subj.index });
      return { clause, subject: subj };
    }
    // bind the matrix subject
    const pending = subj.__pendingBind;
    if (pending === undefined) abstain('elided-subject-unbindable');
    const { __pendingBind, ...spBase } = subj;
    const bound = { ...spBase, bind: pending.index };
    this.referents.push({ index: pending.index, refKind: pending.refKind });
    const clause = this.parseClauseWithSubject({ kind: 'ref', index: pending.index });
    return { clause, subject: bound };
  }

  parseClauseWithSubject(subjFiller) {
    return this.parseClause(subjFiller);
  }

  // -------------------------------------------------------------------------
  // Connective layer (fragment = connective complex over clauses)
  // -------------------------------------------------------------------------

  /**
   * Parse a maximal fragment starting at the cursor. Returns
   * { clauses, referents } (clauses = top-level clause list of the composite).
   */
  parseFragment() {
    const p0 = this.peekWord(0);
    if (p0 === undefined) abstain('sentence-end');
    const w0 = p0.tok.norm;

    // leading operators
    if (w0 === 'maybe') {
      this.nextWord();
      const c = this.parseClause();
      return [{ type: 'op', op: 'MAYBE', args: [c] }];
    }
    if (w0 === 'if') {
      this.nextWord();
      const a = this.parseClause();
      this.skipCommas();
      if (this.peekWord(0)?.tok.norm === 'then') this.nextWord();
      const b = this.parseClause();
      return [{ type: 'op', op: 'IF', args: [a, b] }];
    }
    if (w0 === 'when') {
      this.nextWord();
      const a = this.parseClause();
      this.skipCommas();
      const b = this.parseClause();
      return [{ type: 'op', op: 'WHEN', args: [a, b] }];
    }
    if (w0 === 'because') {
      this.nextWord();
      const a = this.parseClause();
      this.skipCommas();
      const b = this.parseClause();
      return [{ type: 'op', op: 'BECAUSE', args: [a, b] }];
    }

    // clause chain: C1 (and C2)* | C1 because C2 | C1 or C2 (forfeit)
    const first = this.parseClause();
    const clauses = [first];
    let lastSubjectSp = null; // for elided conjunct subjects
    for (;;) {
      this.skipCommas();
      const p = this.peekWord(0);
      if (p === undefined) break;
      const w = p.tok.norm;
      if (w === 'and') {
        const save = this.snapshot();
        try {
          this.nextWord();
          clauses.push(this.parseClause());
          continue;
        } catch (e) {
          if (!(e instanceof Abstain)) throw e;
          this.restore(save);
          break; // maximal fragment ends before the un-parseable conjunct
        }
      }
      if (w === 'because' && clauses.length === 1) {
        // trailing cause: "C1 because C2" -> BECAUSE(cause=C2, effect=C1)
        const save = this.snapshot();
        try {
          this.nextWord();
          const cause = this.parseClause();
          const effect = clauses.pop();
          clauses.push({ type: 'op', op: 'BECAUSE', args: [cause, effect] });
          continue;
        } catch (e) {
          if (!(e instanceof Abstain)) throw e;
          this.restore(save);
          clauses.length = 1; // effect clause stays as the lone fragment clause
          break;
        }
      }
      if (w === 'or') {
        // clause-level OR-forfeit probe (io-compression-ideas.md §3.1): the
        // span would have joined the fragment but for the missing operator.
        const from = this.i;
        const save = this.snapshot();
        let forfeit = null;
        try {
          this.nextWord();
          this.parseClause();
          forfeit = { level: 'clause', fromTok: from, toTok: this.i };
        } catch (e) {
          if (!(e instanceof Abstain)) throw e;
        }
        this.restore(save);
        if (forfeit !== null) this.orForfeits.push(forfeit);
        break;
      }
      break;
    }
    void lastSubjectSp;
    return clauses;
  }
}

/** Strip parser-internal annotations (pending binds) from an AST fragment. */
function stripPending(node) {
  if (Array.isArray(node)) return node.map(stripPending);
  if (node !== null && typeof node === 'object') {
    const out = {};
    for (const k of Object.keys(node)) {
      if (k === '__pendingBind') continue;
      out[k] = stripPending(node[k]);
    }
    return out;
  }
  return node;
}

/** Classify a fragment into the pre-named reporting strata. */
export function classifyFragment(clauses) {
  const hasOp = (c) => {
    if (c.type === 'op') return true;
    for (const f of Object.values(c.roles ?? {})) {
      if (f !== undefined && f.kind === 'clause' && hasOp(f.clause)) return true;
    }
    return false;
  };
  if (clauses.some(hasOp)) return 'operator-complex';
  if (clauses.length >= 2) return 'clause-AND';
  const c = clauses[0];
  if (c.type === 'pred' && (c.pred === 'BE-SPEC' || c.pred === 'THERE-IS')) return 'is-a';
  return 'simple-clause';
}

/**
 * Census scan of ONE sentence (mapper-annotated tokens). Greedy left-to-right:
 * at each word position attempt a maximal fragment; on failure record the
 * blocking cause and advance one word token.
 *
 * Returns { fragments, orForfeits, causes } where each fragment carries the
 * kot-ast/1 explication (InstanceSchema wrapper, referent x1 frame-implicit
 * [STIPULATED wrapper convention for invented composites]) and its span
 * word-token counts (expanded + surface, m0a conventions).
 */
export function scanSentence(toks, profile) {
  const fragments = [];
  const orForfeits = [];
  const forfeitSeen = new Set(); // dedupe across overlapping scan attempts
  const causes = new Map();
  let pos = 0;
  const bump = (cause) => causes.set(cause, (causes.get(cause) ?? 0) + 1);
  const addForfeits = (list) => {
    for (const f of list) {
      const key = `${f.level}:${f.fromTok}`;
      if (forfeitSeen.has(key)) continue;
      forfeitSeen.add(key);
      orForfeits.push(f);
    }
  };

  while (pos < toks.length) {
    if (!toks[pos].isWord) {
      pos++;
      continue;
    }
    const parser = new SentenceParser(toks, profile);
    parser.i = pos;
    try {
      const startTok = pos;
      const clauses = stripPending(parser.parseFragment());
      const endTok = parser.i;
      const referents = [{ index: 1, refKind: 'SomethingRef' }, ...parser.referents];
      const explication = {
        schema: 'kot-ast/1',
        frame: 'InstanceSchema',
        referents,
        clauses,
      };
      let expandedWords = 0;
      let surfaceWords = 0;
      let chars = 0;
      for (let j = startTok; j < endTok; j++) {
        const t = toks[j];
        if (t.isWord) {
          expandedWords++;
          if (!t.isExpansion) surfaceWords++;
        }
        chars += t.end - t.start;
      }
      fragments.push({
        explication,
        stratum: classifyFragment(clauses),
        startTok,
        endTok,
        expandedWords,
        surfaceWords,
        chars,
        clauseCount: clauses.length,
      });
      addForfeits(parser.orForfeits);
      pos = endTok > pos ? endTok : pos + 1;
    } catch (e) {
      if (!(e instanceof Abstain)) throw e;
      bump(e.cause_);
      addForfeits(parser.orForfeits);
      pos++;
    }
  }

  // annotate forfeit token masses
  const forfeits = orForfeits.map((f) => {
    let words = 0;
    for (let j = f.fromTok; j < f.toTok; j++) if (toks[j].isWord) words++;
    return { level: f.level, words };
  });

  return { fragments, orForfeits: forfeits, causes };
}
