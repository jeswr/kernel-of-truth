/**
 * kot-lint vocabulary bands — rung membership per the M0b census definitions
 * (tools/experiments/m0b_instrument.py; analysis/m0b.py LADDER):
 *
 *   kernel-v0      mapper decision concept|prime (operational: the mapper can
 *                  actually resolve the surface form), or — for MEMBERSHIP —
 *                  an abstention (all abstention candidates are kernel targets).
 *   molecules-v0   kernel-v0 membership OR lemma in any committed molecule
 *                  record's corpusLemmas (data/molecules-v0/molecules/*.json).
 *   wn31-aligned   molecules-v0 membership OR lemma equals a single-word
 *                  lowercase lemma of any data/lexical-wn31 synset. This band
 *                  is VOCABULARY MEMBERSHIP ONLY (AxiomsOnly-reachable), never
 *                  explicated coverage — binding phrasing from the m0b verdict
 *                  (registry/verdicts/m0b.json sec-by-rung note) and N-PL §6.
 *
 * Lint vocabulary honesty (N-PL §9.6, binding): out-of-band content is
 * "out of kernel coverage / unverifiable-here", NEVER "hallucination".
 */
import { createHash } from 'node:crypto';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

/**
 * FUNCTION_STOPLIST — copied VERBATIM from mapper/m0/run-m0b-vocab.mjs (the
 * pinned M0b content-word definition; provenance
 * data/task-family-tinystories/README.md). Content-word token := isWord
 * mapper token whose norm is NOT in this set. Keep byte-identical to the
 * source generator; any change is a census-definition change and must be
 * re-pinned.
 */
export const FUNCTION_STOPLIST = new Set([
  // articles, determiners, quantifier-determiners
  'the', 'a', 'an', 'this', 'that', 'these', 'those', 'some', 'any', 'no',
  'every', 'each', 'all', 'both', 'either', 'neither', 'such', 'another',
  'other', 'others', 'own', 'same', 'few', 'many', 'much', 'more', 'most',
  'several', 'lot', 'lots',
  // pronouns (incl. indefinites, which are prime exponents but not content)
  'i', 'me', 'my', 'mine', 'myself', 'you', 'your', 'yours', 'yourself',
  'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it',
  'its', 'itself', 'we', 'us', 'our', 'ours', 'ourselves', 'they', 'them',
  'their', 'theirs', 'themselves', 'who', 'whom', 'whose', 'which', 'what',
  'someone', 'somebody', 'something', 'anything', 'everything', 'nothing',
  'anyone', 'anybody', 'everyone', 'everybody', 'somewhere', 'anywhere',
  'everywhere', 'nowhere', 'whoever', 'whatever',
  // prepositions / particles
  'to', 'of', 'in', 'on', 'at', 'by', 'with', 'from', 'for', 'as', 'into',
  'onto', 'about', 'over', 'under', 'up', 'down', 'out', 'off', 'through',
  'between', 'behind', 'after', 'before', 'during', 'without', 'within',
  'along', 'around', 'across', 'upon', 'near', 'against', 'toward',
  'towards', 'past', 'until', 'till', 'above', 'below', 'beside', 'inside',
  'outside', 'underneath', 'among',
  // conjunctions / complementizers / wh-adverbs
  'and', 'or', 'but', 'so', 'because', 'if', 'when', 'while', 'than',
  'then', 'where', 'why', 'how', 'whether', 'unless', 'although', 'though',
  // auxiliaries / copula / modals (incl. lemmatized bases)
  'be', 'is', 'are', 'am', 'was', 'were', 'been', 'being', 'have', 'has',
  'had', 'having', 'do', 'does', 'did', 'done', 'doing', 'will', 'would',
  'can', 'could', 'shall', 'should', 'may', 'might', 'must', 'cannot',
  'let', 'lets',
  // negation, degree, discourse adverbs
  'not', 'too', 'very', 'quite', 'really', 'just', 'only', 'also', 'again',
  'always', 'never', 'ever', 'soon', 'now', 'here', 'there', 'still',
  'even', 'yet', 'almost', 'maybe', 'perhaps', 'together', 'away', 'back',
  'else', 'once', 'twice', 'instead', 'anymore', 'ok', 'okay',
]);

const WN31_FILES = ['synsets-noun.jsonl', 'synsets-verb.jsonl', 'synsets-adj.jsonl', 'synsets-adv.jsonl'];

export function sha256File(path) {
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

/** molecules-v0 band: lowercased corpusLemmas of every committed molecule
 * record (same extraction as m0b_instrument.py). Fails closed if empty. */
export function loadMoleculeLemmas(repoRoot) {
  const dir = join(repoRoot, 'data', 'molecules-v0', 'molecules');
  const files = readdirSync(dir).filter((f) => f.endsWith('.json')).sort();
  if (files.length === 0) throw new Error('ERR_LINT_VOCAB: no molecule records under data/molecules-v0/molecules/');
  const lemmas = new Set();
  for (const f of files) {
    const rec = JSON.parse(readFileSync(join(dir, f), 'utf8'));
    for (const lemma of rec.corpusLemmas ?? []) lemmas.add(lemma.trim().toLowerCase());
  }
  return lemmas;
}

/** wn31-aligned band: single-word lowercase synset lemmas (multi-word lemmas
 * excluded by definition — m0b_instrument.py). ~166k strings; load once. */
export function loadWn31Lemmas(repoRoot) {
  const lemmas = new Set();
  for (const name of WN31_FILES) {
    const path = join(repoRoot, 'data', 'lexical-wn31', name);
    const raw = readFileSync(path, 'utf8');
    let from = 0;
    while (from < raw.length) {
      let to = raw.indexOf('\n', from);
      if (to === -1) to = raw.length;
      const line = raw.slice(from, to).trim();
      from = to + 1;
      if (line.length === 0) continue;
      const rec = JSON.parse(line);
      for (const lemma of rec.annotations?.lemmas ?? []) {
        const l = lemma.trim().toLowerCase();
        if (l.length > 0 && !l.includes('_') && !l.includes(' ')) lemmas.add(l);
      }
    }
  }
  if (lemmas.size === 0) throw new Error('ERR_LINT_VOCAB: wn31 lemma set is empty');
  return lemmas;
}
