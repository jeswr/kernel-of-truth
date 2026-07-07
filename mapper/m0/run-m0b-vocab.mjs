#!/usr/bin/env node
/**
 * M0b step 1 — extract the frequency-weighted content-word lemma vocabulary
 * from the TinyStories sample and emit the top-N list (default 500) with
 * classification hints, for human/agent classification into
 * {kernel | explicable | molecule | out-of-scope} (poc-design.md M0b).
 *
 * Usage: node mapper/m0/run-m0b-vocab.mjs <TinyStories-valid.txt> [outJson] [N]
 *
 * Content-word definition (pinned): word tokens minus the FUNCTION_STOPLIST
 * below (articles, determiners, pronouns incl. indefinites, prepositions,
 * conjunctions, auxiliaries/copula, negation, degree/discourse adverbs).
 * Several prime exponents (in, on, before, near, very, ...) are function
 * words and are deliberately excluded — M0b bounds CONTENT coverage; the
 * function-word slice is already counted in M0a.
 *
 * Lemma resolution per surface type: irregular-table candidate always folds;
 * a suffix-stripped candidate folds only when corpus-attested with count >=
 * max(5, 2% of the surface count) — the corpus itself is the dictionary, so
 * "wanted"->want folds but "flower" does not become "flow".
 *
 * Proper-name hint: fraction of occurrences that are capitalized mid-sentence.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { lemmaCandidates, irregularBase, buildLexicon, loadManifestConcepts, targetKey } from '../dist/src/index.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..');
const MANIFEST = join(REPO, 'data', 'kernel-v0', 'manifest.json');

const corpusPath = process.argv[2];
if (!corpusPath) {
  console.error('usage: run-m0b-vocab.mjs <TinyStories-valid.txt> [outJson] [N]');
  process.exit(1);
}
const outPath = process.argv[3] ?? join(HERE, 'results', 'm0b-vocab.json');
const N = Number(process.argv[4] ?? 500);

const FUNCTION_STOPLIST = new Set([
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

const raw = readFileSync(corpusPath, 'utf8').replaceAll('<|endoftext|>', ' . ');

/** Reduce a clitic-bearing token to its host ("didn't"->"did", "i'm"->"i"). */
const CL_SPECIAL = new Map([
  ["can't", 'can'], ["won't", 'will'], ["shan't", 'shall'], ["ain't", 'is'],
]);
function clHost(lower) {
  return CL_SPECIAL.get(lower) ?? lower.replace(/n't$|'(ll|re|ve|m|d|s)$/, '');
}

// counts over raw word tokens (no contraction expansion needed for vocab:
// clitics are function material by construction)
const counts = new Map(); // lower -> total
const midCap = new Map(); // lower -> capitalized-mid-sentence count
const WORD = /[A-Za-z]+(?:[’'][A-Za-z]+)*/g;
let prevEndsSentence = true;
let totalWordTokens = 0;
for (const m of raw.matchAll(/[A-Za-z]+(?:[’'][A-Za-z]+)*|[.!?"“”<|]+/g)) {
  const tok = m[0];
  if (!/[A-Za-z]/.test(tok)) {
    if (/[.!?<|]/.test(tok)) prevEndsSentence = true;
    continue;
  }
  const lower = tok.toLowerCase().replace(/[’']s?$/, '').replace(/’/g, "'");
  if (lower.length === 0) { prevEndsSentence = false; continue; }
  totalWordTokens += 1;
  counts.set(lower, (counts.get(lower) ?? 0) + 1);
  if (!prevEndsSentence && /^[A-Z]/.test(tok)) {
    midCap.set(lower, (midCap.get(lower) ?? 0) + 1);
  }
  prevEndsSentence = false;
}

// lemma resolution per type: first candidate after the surface form that is
// corpus-attested at >= max(5, 2% of surface count); else keep the surface.
// (Irregular-table bases like say<-said are massively attested, so they fold.)
function lemmaOf(word) {
  const irr = irregularBase(word);
  if (irr !== undefined) return irr; // table-driven, always fold
  const cands = lemmaCandidates(word);
  const own = counts.get(word) ?? 0;
  for (let k = 1; k < cands.length; k += 1) {
    const c = cands[k];
    const attested = counts.get(c) ?? 0;
    if (attested >= Math.max(5, 0.02 * own)) return c;
  }
  return cands[0];
}

const lemmaCounts = new Map();
const lemmaMidCap = new Map();
const lemmaSources = new Map(); // lemma -> {surface: count}
let contentMass = 0;
for (const [w, c] of counts) {
  if (FUNCTION_STOPLIST.has(w) || FUNCTION_STOPLIST.has(clHost(w))) continue;
  const l = lemmaOf(clHost(w));
  if (FUNCTION_STOPLIST.has(l)) continue;
  contentMass += c;
  lemmaCounts.set(l, (lemmaCounts.get(l) ?? 0) + c);
  lemmaMidCap.set(l, (lemmaMidCap.get(l) ?? 0) + (midCap.get(w) ?? 0));
  const src = lemmaSources.get(l) ?? {};
  src[w] = c;
  lemmaSources.set(l, src);
}

const lexicon = buildLexicon(loadManifestConcepts(MANIFEST));
const top = [...lemmaCounts.entries()].sort((a, b) => b[1] - a[1]).slice(0, N);
let cum = 0;
const rows = top.map(([lemma, count]) => {
  cum += count;
  const hits = lexicon.single.get(lemma) ?? [];
  return {
    lemma,
    count,
    pctOfContentMass: Math.round((count / contentMass) * 1e6) / 1e4,
    cumPct: Math.round((cum / contentMass) * 1e6) / 1e4,
    kernelHits: hits.map((h) => targetKey(h.target)),
    properNameScore: Math.round(((lemmaMidCap.get(lemma) ?? 0) / count) * 1000) / 1000,
    surfaces: lemmaSources.get(lemma),
  };
});

const out = {
  experiment: 'M0b-vocab',
  totalWordTokens,
  contentMass,
  pctContentOfAllWords: Math.round((contentMass / totalWordTokens) * 1e6) / 1e4,
  distinctContentLemmas: lemmaCounts.size,
  topN: N,
  topNMassPctOfContent: Math.round((cum / contentMass) * 1e6) / 1e4,
  rows,
};
writeFileSync(outPath, `${JSON.stringify(out, null, 2)}\n`);
console.log(
  `content mass ${contentMass}/${totalWordTokens} (${out.pctContentOfAllWords}%), ` +
  `${lemmaCounts.size} lemmas, top ${N} cover ${out.topNMassPctOfContent}% of content mass`,
);
