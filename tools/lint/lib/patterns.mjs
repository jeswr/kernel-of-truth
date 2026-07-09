/**
 * kot-lint V-rhetorical pattern lexicon v0 — LNT-F3 arm (a): deterministic
 * pattern-tier vacuity detection (docs/next/kernel-precision-linter.md §3.2
 * class V, §7 LNT-F3). This is the COVERAGE-INDEPENDENT half of the vacuity
 * class: discourse filler, unattributed ("weasel") attribution, and vague
 * hedging templates, matched as literal token sequences over the mapper's
 * normalized (lowercased, contraction-expanded) word-token stream.
 *
 * V-tautology (content that parses but reduces to nothing after explication
 * normalisation) is NOT implementable at Stage 0 — it needs kernel coverage
 * + the explication normaliser — and is deliberately absent (N-PL §3.2
 * consequence 3; the LNT-E0(iii) split is therefore only half-measurable
 * now, stated as such in the census report).
 *
 * Design discipline (Bessey/Coverity false-positive lesson, N-PL §1.1
 * [memory-tagged in N-PL — not re-asserted here]): patterns are literal and
 * conservative; per-pattern hit counts are reported per corpus slice by
 * LNT-E0 so noisy patterns are identified by MEASUREMENT and can be cut at
 * prereg time, not argued about.
 *
 * Pattern syntax: space-separated normalized tokens; a trailing '?' marks an
 * optional token. Matching is longest-match-first at each position over
 * CONSECUTIVE word tokens (no intervening punctuation), case-insensitive via
 * the mapper's norm field. The lexicon is content-hashed (sha256 over the
 * canonical JSON) and the hash is pinned into every lint report (S5).
 */
import { createHash } from 'node:crypto';

export const PATTERN_LEXICON_VERSION = '0.1.0';

/** id, category (filler | weasel | hedge), pattern. Closed list. */
export const PATTERN_LEXICON = [
  // --- filler: discourse/meta filler with zero propositional content -------
  { id: 'fill-important-note', category: 'filler', pattern: 'it is important to note that?' },
  { id: 'fill-important-remember', category: 'filler', pattern: 'it is important to remember that?' },
  { id: 'fill-important-understand', category: 'filler', pattern: 'it is important to understand that?' },
  { id: 'fill-should-be-noted', category: 'filler', pattern: 'it should be noted that?' },
  { id: 'fill-worth-noting', category: 'filler', pattern: 'it is worth noting that?' },
  { id: 'fill-interesting-note', category: 'filler', pattern: 'it is interesting to note that?' },
  { id: 'fill-goes-without-saying', category: 'filler', pattern: 'it goes without saying that?' },
  { id: 'fill-needless-to-say', category: 'filler', pattern: 'needless to say' },
  { id: 'fill-matter-of-fact', category: 'filler', pattern: 'as a matter of fact' },
  { id: 'fill-fact-of-matter', category: 'filler', pattern: 'the fact of the matter is that?' },
  { id: 'fill-end-of-day', category: 'filler', pattern: 'at the end of the day' },
  { id: 'fill-said-and-done', category: 'filler', pattern: 'when all is said and done' },
  { id: 'fill-intents-purposes', category: 'filler', pattern: 'for all intents and purposes' },
  { id: 'fill-day-and-age', category: 'filler', pattern: 'in this day and age' },
  { id: 'fill-first-foremost', category: 'filler', pattern: 'first and foremost' },
  { id: 'fill-last-not-least', category: 'filler', pattern: 'last but not least' },
  { id: 'fill-as-you-can-see', category: 'filler', pattern: 'as you can see' },
  { id: 'fill-as-we-all-know', category: 'filler', pattern: 'as we all know' },
  { id: 'fill-as-everyone-knows', category: 'filler', pattern: 'as everyone knows' },
  { id: 'fill-well-known', category: 'filler', pattern: 'as is well known' },
  { id: 'fill-no-secret', category: 'filler', pattern: 'it is no secret that' },
  { id: 'fill-to-be-honest', category: 'filler', pattern: 'to be honest' },
  { id: 'fill-to-be-fair', category: 'filler', pattern: 'to be fair' },
  { id: 'fill-put-simply', category: 'filler', pattern: 'to put it simply' },
  { id: 'fill-simply-put', category: 'filler', pattern: 'simply put' },
  { id: 'fill-very-real-sense', category: 'filler', pattern: 'in a very real sense' },
  { id: 'fill-point-in-time', category: 'filler', pattern: 'at this point in time' },
  { id: 'fill-final-analysis', category: 'filler', pattern: 'in the final analysis' },
  { id: 'fill-all-considered', category: 'filler', pattern: 'all things considered' },
  { id: 'fill-is-what-it-is', category: 'filler', pattern: 'it is what it is' },
  { id: 'fill-each-and-every', category: 'filler', pattern: 'each and every' },

  // --- weasel: attribution/quantification with no groundable complement ----
  { id: 'wea-many-experts-believe', category: 'weasel', pattern: 'many experts believe' },
  { id: 'wea-experts-believe', category: 'weasel', pattern: 'experts believe' },
  { id: 'wea-experts-agree', category: 'weasel', pattern: 'experts agree' },
  { id: 'wea-experts-say', category: 'weasel', pattern: 'experts say' },
  { id: 'wea-some-people-say', category: 'weasel', pattern: 'some people say' },
  { id: 'wea-some-people-believe', category: 'weasel', pattern: 'some people believe' },
  { id: 'wea-many-people-believe', category: 'weasel', pattern: 'many people believe' },
  { id: 'wea-many-people-think', category: 'weasel', pattern: 'many people think' },
  { id: 'wea-some-say', category: 'weasel', pattern: 'some say' },
  { id: 'wea-some-argue', category: 'weasel', pattern: 'some argue' },
  { id: 'wea-some-believe', category: 'weasel', pattern: 'some believe' },
  { id: 'wea-many-believe', category: 'weasel', pattern: 'many believe' },
  { id: 'wea-widely-believed', category: 'weasel', pattern: 'it is widely believed' },
  { id: 'wea-often-said', category: 'weasel', pattern: 'it is often said' },
  { id: 'wea-generally-accepted', category: 'weasel', pattern: 'it is generally accepted' },
  { id: 'wea-commonly-believed', category: 'weasel', pattern: 'it is commonly believed' },
  { id: 'wea-been-suggested', category: 'weasel', pattern: 'it has been suggested' },
  { id: 'wea-thought-that', category: 'weasel', pattern: 'it is thought that' },
  { id: 'wea-believed-that', category: 'weasel', pattern: 'it is believed that' },
  { id: 'wea-studies-show', category: 'weasel', pattern: 'studies show' },
  { id: 'wea-studies-shown', category: 'weasel', pattern: 'studies have shown' },
  { id: 'wea-research-shows', category: 'weasel', pattern: 'research shows' },
  { id: 'wea-research-shown', category: 'weasel', pattern: 'research has shown' },
  { id: 'wea-research-suggests', category: 'weasel', pattern: 'research suggests' },
  { id: 'wea-critics-say', category: 'weasel', pattern: 'critics say' },
  { id: 'wea-history-tells', category: 'weasel', pattern: 'history tells us' },
  { id: 'wea-a-number-of', category: 'weasel', pattern: 'a number of' },

  // --- hedge: vague degree/extent with no groundable complement ------------
  { id: 'hdg-some-extent', category: 'hedge', pattern: 'to some extent' },
  { id: 'hdg-certain-extent', category: 'hedge', pattern: 'to a certain extent' },
  { id: 'hdg-in-some-sense', category: 'hedge', pattern: 'in some sense' },
  { id: 'hdg-in-a-sense', category: 'hedge', pattern: 'in a sense' },
  { id: 'hdg-in-many-ways', category: 'hedge', pattern: 'in many ways' },
  { id: 'hdg-in-some-ways', category: 'hedge', pattern: 'in some ways' },
  { id: 'hdg-somewhat-of-a', category: 'hedge', pattern: 'somewhat of a' },
  { id: 'hdg-something-of-a', category: 'hedge', pattern: 'something of a' },
  { id: 'hdg-more-often-than-not', category: 'hedge', pattern: 'more often than not' },
  { id: 'hdg-at-some-level', category: 'hedge', pattern: 'at some level' },
  { id: 'hdg-on-some-level', category: 'hedge', pattern: 'on some level' },
  { id: 'hdg-most-part', category: 'hedge', pattern: 'for the most part' },
  { id: 'hdg-by-and-large', category: 'hedge', pattern: 'by and large' },
  { id: 'hdg-generally-speaking', category: 'hedge', pattern: 'generally speaking' },
  { id: 'hdg-broadly-speaking', category: 'hedge', pattern: 'broadly speaking' },
  { id: 'hdg-relatively-speaking', category: 'hedge', pattern: 'relatively speaking' },
  { id: 'hdg-arguably', category: 'hedge', pattern: 'arguably' },
];

/** sha256 over the canonical JSON of the lexicon (sorted-key objects in
 * declared order) — pinned into every report. */
export function patternLexiconSha256() {
  const canonical = JSON.stringify(
    PATTERN_LEXICON.map((p) => ({ category: p.category, id: p.id, pattern: p.pattern })),
  );
  return createHash('sha256').update(`${PATTERN_LEXICON_VERSION}\n${canonical}`).digest('hex');
}

/** Compile to token-sequence matchers, indexed by first token. */
export function compilePatterns(lexicon = PATTERN_LEXICON) {
  const byFirst = new Map();
  for (const p of lexicon) {
    const toks = p.pattern.split(' ').map((t) =>
      t.endsWith('?') ? { tok: t.slice(0, -1), optional: true } : { tok: t, optional: false },
    );
    if (toks[0].optional) throw new Error(`ERR_LINT_PATTERN: first token optional in ${p.id}`);
    const list = byFirst.get(toks[0].tok) ?? [];
    list.push({ id: p.id, category: p.category, pattern: p.pattern, toks });
    byFirst.set(toks[0].tok, list);
  }
  // longest-first so the longest pattern wins at each position
  for (const list of byFirst.values()) list.sort((a, b) => b.toks.length - a.toks.length || (a.id < b.id ? -1 : 1));
  return byFirst;
}

/**
 * Match compiled patterns over one sentence's word tokens (mapper
 * AnnotatedTokens, isWord===true, stream order). Tokens must be CONSECUTIVE
 * in the word stream (any intervening word breaks a match; intervening
 * punctuation between adjacent word tokens is tolerated only for commas —
 * conservative). Non-overlapping, leftmost-longest. Returns
 * [{id, category, pattern, start, end, text}].
 */
export function matchVacuityPatterns(text, tokens, compiled) {
  const hits = [];
  let i = 0;
  while (i < tokens.length) {
    const cands = compiled.get(tokens[i].norm);
    let matched = null;
    if (cands !== undefined) {
      for (const p of cands) {
        const end = tryMatch(text, tokens, i, p.toks);
        if (end !== -1) {
          matched = { p, endIdx: end };
          break; // lists are longest-first
        }
      }
    }
    if (matched !== null) {
      const startTok = tokens[i];
      const endTok = tokens[matched.endIdx];
      hits.push({
        id: matched.p.id,
        category: matched.p.category,
        pattern: matched.p.pattern,
        start: startTok.start,
        end: endTok.end,
        text: text.slice(startTok.start, endTok.end),
        tokenSpan: [i, matched.endIdx],
      });
      i = matched.endIdx + 1;
    } else {
      i += 1;
    }
  }
  return hits;
}

/** Try to match `toks` at word index `i`; returns last matched word index or -1. */
function tryMatch(text, tokens, i, toks) {
  let ti = i;
  for (let k = 0; k < toks.length; k += 1) {
    const spec = toks[k];
    const t = tokens[ti];
    const gapOk =
      ti === i ||
      /^[\s,]*$/.test(text.slice(tokens[ti - 1].end, t === undefined ? tokens[ti - 1].end : t.start));
    if (t !== undefined && gapOk && t.norm === spec.tok) {
      ti += 1;
    } else if (!spec.optional) {
      return -1;
    }
  }
  return ti - 1 >= i ? ti - 1 : -1;
}
