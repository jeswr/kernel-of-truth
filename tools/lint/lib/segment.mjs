/**
 * kot-lint segmentation — deterministic, offset-preserving sentence and
 * clause segmentation (N-PL pipeline stage S1, docs/next/kernel-precision-linter.md §2).
 *
 * Everything here is rule-based and seedless: same text -> same spans, byte
 * for byte (the S5 determinism contract). The clause is the Stage-0
 * PROPOSITION PROXY (LNT-F1 arm (a), deterministic parser only): no syntactic
 * parse exists at Stage 0, so "proposition" is approximated by a clause split
 * on hard punctuation + a closed connective list. The proxy's crudeness is a
 * declared instrument limitation of the LNT-E0 census, not a hidden one —
 * unit-length distributions are reported so reviewers can judge it.
 */

/** Abbreviations that do NOT end a sentence when followed by '.' (lowercased,
 * dot-free). Single letters (initials, and the g/e of e.g./i.e.) are handled
 * by the single-letter rule below. Closed list, deterministic. */
const ABBREV = new Set([
  'mr', 'mrs', 'ms', 'dr', 'prof', 'st', 'etc', 'vs', 'cf', 'al', 'fig',
  'sec', 'inc', 'ltd', 'jr', 'sr', 'dept', 'approx', 'ca', 'no', 'nos',
  'eq', 'ch', 'pp', 'ed', 'eds', 'vol', 'rev',
]);

/**
 * Split `text` into sentence spans [{start, end}] (end exclusive).
 * Breaks at: [.!?]+ (with optional closing quotes/brackets) followed by
 * whitespace, unless the preceding word is a known abbreviation or a single
 * letter; at paragraph breaks (blank lines); and at end of text.
 */
export function segmentSentences(text) {
  const spans = [];
  const n = text.length;
  let start = 0;
  let i = 0;
  const isSpace = (c) => c === ' ' || c === '\t' || c === '\n' || c === '\r';
  while (i < n) {
    const c = text[i];
    // paragraph break: newline, optional spaces, newline
    if (c === '\n') {
      let j = i + 1;
      while (j < n && (text[j] === ' ' || text[j] === '\t' || text[j] === '\r')) j += 1;
      if (j < n && text[j] === '\n') {
        if (trimmedNonEmpty(text, start, i)) spans.push({ start, end: i });
        while (j < n && isSpace(text[j])) j += 1;
        start = j;
        i = j;
        continue;
      }
    }
    if (c === '.' || c === '!' || c === '?') {
      // consume the terminator run + closing quotes/brackets
      let j = i;
      while (j < n && (text[j] === '.' || text[j] === '!' || text[j] === '?')) j += 1;
      while (j < n && '"\'’”)]}'.includes(text[j])) j += 1;
      const atEnd = j >= n;
      const followedBySpace = !atEnd && isSpace(text[j]);
      if (atEnd || followedBySpace) {
        // look back at the word immediately before the terminator run
        let w = i - 1;
        while (w >= 0 && /[A-Za-z]/.test(text[w])) w -= 1;
        const word = text.slice(w + 1, i).toLowerCase();
        const isAbbrev =
          text[i] === '.' &&
          word.length > 0 &&
          (word.length === 1 || ABBREV.has(word));
        if (!isAbbrev) {
          if (trimmedNonEmpty(text, start, j)) spans.push({ start, end: j });
          let k = j;
          while (k < n && isSpace(text[k])) k += 1;
          start = k;
          i = k;
          continue;
        }
      }
      i = j;
      continue;
    }
    i += 1;
  }
  if (trimmedNonEmpty(text, start, n)) spans.push({ start, end: n });
  return spans;
}

function trimmedNonEmpty(text, a, b) {
  for (let i = a; i < b; i += 1) if (/\S/.test(text[i])) return true;
  return false;
}

/** Clause-boundary connectives. A new clause starts AT a subordinator token,
 * or AT a coordinator token that is preceded by a comma within the same
 * sentence ("She ran, and he followed"). NP coordination without a comma
 * ("cats and dogs") is deliberately NOT split. Closed lists, deterministic. */
const SUBORDINATORS = new Set([
  'because', 'although', 'though', 'unless', 'while', 'whereas', 'since',
  'if', 'when',
]);
const COORDINATORS = new Set(['and', 'but', 'or', 'so', 'then']);
/** Hard punctuation that always separates clauses when it appears between
 * two word tokens: ; : em/en dash, double hyphen. */
const HARD_PUNCT = /[;:—–]|--/;

/**
 * Split one sentence's word tokens into clause groups (the proposition
 * proxy). `tokens` = mapper AnnotatedTokens with isWord===true, in stream
 * order, all lying inside the sentence span. Returns an array of arrays of
 * tokens (never empty groups).
 */
export function segmentClauses(text, tokens) {
  const groups = [];
  let current = [];
  for (let i = 0; i < tokens.length; i += 1) {
    const t = tokens[i];
    let boundary = false;
    if (i > 0) {
      const gap = text.slice(tokens[i - 1].end, t.start);
      if (HARD_PUNCT.test(gap)) boundary = true;
      else if (COORDINATORS.has(t.norm) && gap.includes(',')) boundary = true;
      else if (SUBORDINATORS.has(t.norm)) boundary = true;
    }
    if (boundary && current.length > 0) {
      groups.push(current);
      current = [];
    }
    current.push(t);
  }
  if (current.length > 0) groups.push(current);
  return groups;
}

/**
 * Offset-preserving markdown de-formatting: every removed character is
 * replaced by a space, so all downstream offsets index the ORIGINAL text.
 * Removes fenced code blocks, inline code spans, markdown table rows,
 * heading/list/blockquote markers, link targets (keeps link text), bare
 * URLs, and emphasis markers. Deterministic.
 */
export function stripMarkdown(text) {
  const blank = (m) => ' '.repeat(m.length);
  let out = text;
  out = out.replace(/```[\s\S]*?(```|$)/g, blank); // fenced code blocks
  out = out.replace(/`[^`\n]*`/g, blank); // inline code spans
  out = out.replace(/^[ \t]*\|.*$/gm, blank); // table rows
  out = out.replace(/^[ \t]{4,}\S.*$/gm, blank); // indented code lines
  out = out.replace(/!\[[^\]]*\]\([^)]*\)/g, blank); // images
  // links: keep the label AT ITS ORIGINAL OFFSET (the leading '[' becomes a
  // space), blank the '](target)' tail
  out = out.replace(/\[([^\]]*)\]\(([^)]*)\)/g, (m, label) => ` ${label}${' '.repeat(m.length - label.length - 1)}`);
  out = out.replace(/https?:\/\/\S+/g, blank); // bare URLs
  out = out.replace(/^[ \t]*#{1,6}[ \t]/gm, blank); // heading markers
  out = out.replace(/^[ \t]*(?:[-*+]|\d+\.)[ \t]/gm, blank); // list bullets
  out = out.replace(/^[ \t]*>+[ \t]?/gm, blank); // blockquotes
  out = out.replace(/[*_]{1,3}(?=\S)|(?<=\S)[*_]{1,3}/g, blank); // emphasis
  return out;
}
