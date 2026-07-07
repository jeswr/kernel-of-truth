/**
 * Deterministic word tokenizer with contraction expansion.
 *
 * Rules (all deterministic, no dictionary):
 * - Lowercase for the normalized form; original surface retained.
 * - Word = run of ASCII letters plus internal apostrophes (' or U+2019).
 * - Contraction expansion (so multiword prime phrases like "do not want"
 *   match): n't -> "not"; 'll -> "will"; 're -> "are"; 've -> "have";
 *   'm -> "am"; 'd -> "would" (undisambiguated had/would — neither is a
 *   lexicon target, so the choice is inert); special-cases "won't" ->
 *   will not, "can't"/"cannot" -> can not, "ain't" -> is not,
 *   "let's" -> let us.
 * - Pronoun/wh + 's -> pronoun + "is" (it's, that's, he's, she's, there's,
 *   what's, who's, where's, here's). Other <word>'s is treated as
 *   possessive/plural-possessive: the 's is dropped and the base kept
 *   (deterministic; possessive vs copula on common nouns is undisambiguated
 *   — documented limitation).
 * - Numbers and non-letter runs are non-word tokens (kept for offsets,
 *   excluded from token mass).
 *
 * Expanded tokens report the SAME surface span (isExpansion marks the
 * synthetic continuation tokens) so token-mass accounting can count either
 * surface words or expanded words; M0a counts surface words.
 */

export interface Token {
  /** Original surface text of the span this token came from. */
  readonly surface: string;
  /** Lowercased, contraction-expanded word form ('' for non-words). */
  readonly norm: string;
  /** Character offset of the span start in the input. */
  readonly start: number;
  /** Character offset one past the span end. */
  readonly end: number;
  /** True for alphabetic word tokens (mapper input); false for punctuation/number spans. */
  readonly isWord: boolean;
  /**
   * True when this token is the 2nd+ piece of a contraction expansion
   * ("don't" -> do + not: "not" has isExpansion=true). Surface-word counts
   * skip expansion continuations.
   */
  readonly isExpansion: boolean;
}

const APOSTROPHE = /[’']/g;

const PRONOUN_S_IS = new Set([
  'it', 'that', 'he', 'she', 'there', 'what', 'who', 'where', 'here', 'this',
]);

/** Fully irregular contraction expansions (post-lowercase, straight apostrophe). */
const SPECIAL: ReadonlyMap<string, readonly string[]> = new Map([
  ["won't", ['will', 'not']],
  ["can't", ['can', 'not']],
  ['cannot', ['can', 'not']],
  ["shan't", ['shall', 'not']],
  ["ain't", ['is', 'not']],
  ["let's", ['let', 'us']],
  ["o'clock", ['oclock']],
]);

function expandWord(lower: string): readonly string[] {
  const special = SPECIAL.get(lower);
  if (special !== undefined) return special;
  if (lower.endsWith("n't") && lower.length > 3) {
    return [lower.slice(0, -3), 'not'];
  }
  if (lower.endsWith("'ll") && lower.length > 3) return [lower.slice(0, -3), 'will'];
  if (lower.endsWith("'re") && lower.length > 3) return [lower.slice(0, -3), 'are'];
  if (lower.endsWith("'ve") && lower.length > 3) return [lower.slice(0, -3), 'have'];
  if (lower.endsWith("'m") && lower.length > 2) return [lower.slice(0, -2), 'am'];
  if (lower.endsWith("'d") && lower.length > 2) return [lower.slice(0, -2), 'would'];
  if (lower.endsWith("'s") && lower.length > 2) {
    const base = lower.slice(0, -2);
    if (PRONOUN_S_IS.has(base)) return [base, 'is'];
    return [base]; // possessive: drop the clitic (documented limitation)
  }
  if (lower.endsWith("'") && lower.length > 1) return [lower.slice(0, -1)]; // trailing possessive apostrophe (dogs')
  return [lower];
}

const WORD_RE = /[A-Za-z]+(?:[’'][A-Za-z]+)*/y;
const NONSPACE_RE = /[^\sA-Za-z]+/y;

/** Tokenize `text` into word and non-word tokens (see module doc for rules). */
export function tokenize(text: string): Token[] {
  const out: Token[] = [];
  let i = 0;
  const n = text.length;
  while (i < n) {
    const ch = text[i]!;
    if (/\s/.test(ch)) {
      i += 1;
      continue;
    }
    WORD_RE.lastIndex = i;
    const wm = WORD_RE.exec(text);
    if (wm !== null && wm.index === i) {
      const surface = wm[0];
      const lower = surface.toLowerCase().replace(APOSTROPHE, "'");
      const parts = expandWord(lower);
      for (let p = 0; p < parts.length; p += 1) {
        out.push({
          surface,
          norm: parts[p]!,
          start: i,
          end: i + surface.length,
          isWord: true,
          isExpansion: p > 0,
        });
      }
      i += surface.length;
      continue;
    }
    NONSPACE_RE.lastIndex = i;
    const nm = NONSPACE_RE.exec(text);
    if (nm !== null && nm.index === i) {
      const surface = nm[0];
      out.push({
        surface,
        norm: '',
        start: i,
        end: i + surface.length,
        isWord: false,
        isExpansion: false,
      });
      i += surface.length;
      continue;
    }
    i += 1; // unreachable safety
  }
  return out;
}
