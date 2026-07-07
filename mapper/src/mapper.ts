/**
 * Phrase->concept mapper v0: deterministic transducer from English text to
 * kernel references (architecture.md section 3.2 — deterministic lexicon
 * primary; poc-design.md Phase M).
 *
 * Matching algorithm, per word-token position (deterministic, no
 * backtracking):
 * 1. MULTIWORD, longest-match-first: try lexicon phrases of length
 *    maxPhraseLen..2 over the normalized token stream (phrases never cross
 *    non-word tokens). If the longest matching length has exactly one
 *    target, map and consume the phrase; if it has >1 distinct targets,
 *    ABSTAIN over the phrase span (never silently pick).
 * 2. SINGLE TOKEN: collect targets over the ordered lemma-candidate list
 *    (surface form first — lemmatize.ts). The candidate UNION is the
 *    decision set: exactly one distinct target -> map; more than one ->
 *    ABSTAIN and record all candidates ("broken" hits concept broken via
 *    surface AND concept break via lemma -> abstain); zero -> unmapped.
 *
 * Abstention is a first-class outcome (pre-registered rate in M0a): the
 * mapper NEVER resolves word-sense or surface/lemma collisions. Downstream
 * consumers (E1 augmentation) receive the annotated stream and do their own
 * stochastic substitution — the mapper only annotates.
 */

import { lemmaCandidates } from './lemmatize.js';
import type { Lexicon, Target } from './lexicon.js';
import { targetKey } from './lexicon.js';
import { tokenize, type Token } from './tokenize.js';

export type Decision =
  | { readonly kind: 'concept'; readonly conceptId: string }
  | { readonly kind: 'prime'; readonly prime: string }
  | { readonly kind: 'abstain'; readonly candidates: readonly Target[] }
  | { readonly kind: 'none' };

export interface AnnotatedToken {
  /** Original surface text. */
  readonly surface: string;
  /** Normalized (lowercased, contraction-expanded) form; '' for non-words. */
  readonly norm: string;
  /** Best lemma: first lemma candidate that hit the lexicon, else the first candidate (= surface). */
  readonly lemma: string;
  readonly start: number;
  readonly end: number;
  readonly isWord: boolean;
  readonly isExpansion: boolean;
  readonly decision: Decision;
  /** Length in stream tokens of the phrase match this token belongs to (1 for single). */
  readonly phraseLen: number;
  /** 0 for the phrase head (or any single token); >0 marks continuation tokens of a multiword match. */
  readonly phrasePos: number;
}

const NONE: Decision = { kind: 'none' };

function decideFromTargets(targets: readonly Target[]): Decision {
  if (targets.length === 0) return NONE;
  if (targets.length === 1) {
    const t = targets[0]!;
    return t.kind === 'prime'
      ? { kind: 'prime', prime: t.prime }
      : { kind: 'concept', conceptId: t.conceptId };
  }
  return { kind: 'abstain', candidates: targets };
}

function uniqueTargets(targets: readonly Target[]): Target[] {
  const seen = new Set<string>();
  const out: Target[] = [];
  for (const t of targets) {
    const k = targetKey(t);
    if (seen.has(k)) continue;
    seen.add(k);
    out.push(t);
  }
  return out;
}

/** Map pre-tokenized tokens (exposed for tests); use mapText for strings. */
export function mapTokens(tokens: readonly Token[], lexicon: Lexicon): AnnotatedToken[] {
  const out: AnnotatedToken[] = [];
  let i = 0;
  while (i < tokens.length) {
    const tok = tokens[i]!;
    if (!tok.isWord) {
      out.push({ ...tok, lemma: '', decision: NONE, phraseLen: 1, phrasePos: 0 });
      i += 1;
      continue;
    }

    // 1. multiword, longest-match-first
    const heads = lexicon.multiword.get(tok.norm);
    let matched = false;
    if (heads !== undefined) {
      let bestLen = 0;
      let bestTargets: Target[] = [];
      for (const entry of heads) {
        // entries are sorted longest first; stop collecting once a shorter
        // length appears after a match was found at a longer length
        if (bestLen > 0 && entry.phrase.length < bestLen) break;
        const len = entry.phrase.length;
        if (i + len > tokens.length) continue;
        let ok = true;
        for (let k = 1; k < len; k += 1) {
          const t = tokens[i + k]!;
          if (!t.isWord || t.norm !== entry.phrase[k]) {
            ok = false;
            break;
          }
        }
        if (ok) {
          bestLen = len;
          bestTargets.push(entry.target);
        }
      }
      if (bestLen > 0) {
        const decision = decideFromTargets(uniqueTargets(bestTargets));
        for (let k = 0; k < bestLen; k += 1) {
          const t = tokens[i + k]!;
          out.push({
            ...t,
            lemma: t.norm,
            decision,
            phraseLen: bestLen,
            phrasePos: k,
          });
        }
        i += bestLen;
        matched = true;
      }
    }
    if (matched) continue;

    // 2. single token over lemma candidates
    const candidates = lemmaCandidates(tok.norm);
    const targets: Target[] = [];
    let lemma = candidates[0]!;
    let lemmaFixed = false;
    for (const cand of candidates) {
      const hits = lexicon.single.get(cand);
      if (hits === undefined) continue;
      if (!lemmaFixed) {
        lemma = cand;
        lemmaFixed = true;
      }
      for (const h of hits) targets.push(h.target);
    }
    out.push({
      ...tok,
      lemma,
      decision: decideFromTargets(uniqueTargets(targets)),
      phraseLen: 1,
      phrasePos: 0,
    });
    i += 1;
  }
  return out;
}

/** Annotate `text` against `lexicon`. Deterministic: same input, same output. */
export function mapText(text: string, lexicon: Lexicon): AnnotatedToken[] {
  return mapTokens(tokenize(text), lexicon);
}
