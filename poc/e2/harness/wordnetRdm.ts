/**
 * Baseline 2 — WordNet path-similarity RDM (docs/poc-design.md E2 primary
 * criterion: "WordNet path" relatedness baseline). Full WordNet 3.1 database
 * files vendored via the `wordnet-db` npm package (35 MB << 100 MB budget).
 *
 * PRIMARY matrix: path similarity 1/(1+d) with d = shortest path over the
 * extended relation graph (hypernym/hyponym/instance, similar-to, attribute,
 * derivationally-related, pertainym, verb-group; see harness/wordnet.ts),
 * max over all synset pairs of the two surface words (all POS pooled —
 * relatedness, not sense-disambiguated), depth cap 16 (sim < 0.06 beyond),
 * sim = 0 when unreachable.
 *
 * DEVIATION (flagged here + README): classical NLTK path_similarity is
 * undefined for adjectives (16/51 items) and across POS; a strictly
 * classical matrix would have >30% missing cells. The extended graph is the
 * published primary; the classical same-POS hypernym variant (simulated
 * root) is emitted alongside with its coverage mask.
 */

import { encoderContentHash } from '@jeswr/kernel-encoder';
import { corpusPin, similarityMatrix, writeInput } from './common.js';
import { loadCorpus } from './corpus.js';
import { buildItems } from './items.js';
import { hypernymDistance, loadWordnet, pathSimilarity, shortestPath } from './wordnet.js';
import type { SynsetKey } from './wordnet.js';

function main(): void {
  const corpus = loadCorpus();
  const { probeItems } = buildItems(corpus.map((c) => c.id));
  console.log('loading WordNet 3.1 (wordnet-db)...');
  const wn = loadWordnet();
  console.log(`  ${wn.synsetCount} synsets`);

  const senses: SynsetKey[][] = probeItems.map((p) => wn.lookup(p.word));
  const missing = probeItems.filter((_, i) => senses[i]!.length === 0).map((p) => p.word);
  if (missing.length > 0) {
    // Fail loudly: coverage was verified at authoring time (only "archived"
    // needed the morphy fallback). A miss here means the item set changed.
    throw new Error(`WordNet lookup failed for: ${missing.join(', ')}`);
  }

  const n = probeItems.length;
  console.log(`computing ${(n * (n - 1)) / 2} pairwise extended-graph shortest paths...`);
  const distances: number[][] = Array.from({ length: n }, () => new Array<number>(n).fill(0));
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const d = shortestPath(wn, senses[i]!, senses[j]!, 16);
      distances[i]![j] = d;
      distances[j]![i] = d;
    }
    if ((i + 1) % 10 === 0) console.log(`  row ${i + 1}/${n}`);
  }
  const sim = similarityMatrix(n, (i, j) => pathSimilarity(distances[i]![j]!));

  // Classical same-POS hypernym variant (secondary): noun and verb synsets
  // only, per-POS taxonomy with simulated root, max similarity across the
  // two POS taxonomies; null where either word lacks noun+verb synsets.
  const classical: (number | null)[][] = Array.from({ length: n }, () => new Array<number | null>(n).fill(null));
  const nvSenses = (w: string, pos: 'noun' | 'verb'): SynsetKey[] => wn.lookup(w, pos);
  for (let i = 0; i < n; i++) {
    classical[i]![i] = 1;
    for (let j = i + 1; j < n; j++) {
      let best: number | null = null;
      for (const pos of ['noun', 'verb'] as const) {
        const a = nvSenses(probeItems[i]!.word, pos);
        const b = nvSenses(probeItems[j]!.word, pos);
        if (a.length === 0 || b.length === 0) continue;
        const s = pathSimilarity(hypernymDistance(wn, a, b));
        if (best === null || s > best) best = s;
      }
      classical[i]![j] = best;
      classical[j]![i] = best;
    }
  }
  const classicalDefined = classical.flat().filter((v) => v !== null).length;

  const unreachable: string[] = [];
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      if (!Number.isFinite(distances[i]![j]!)) unreachable.push(`${probeItems[i]!.word}~${probeItems[j]!.word}`);
    }
  }

  writeInput('baseline-wordnet.json', {
    date: new Date().toISOString(),
    encoderContentHash: encoderContentHash(),
    corpusPin: corpusPin(),
    source: 'WordNet 3.1 via wordnet-db@3.1.14 (npm), full database files (35 MB)',
    derivation:
      'PRIMARY: 1/(1+d), d = shortest path over extended relation graph (@,@i,~,~i,&,=,+,\\,$), max over all synset pairs, all POS pooled, depth cap 16, 0 if unreachable. DEVIATION from classical NLTK path_similarity flagged: classical is undefined for adjectives (16/51 items); classical same-POS hypernym variant published alongside (classicalSimilarity, null = undefined).',
    convention: 'similarity (unit diagonal); item order = ids[]',
    ids: probeItems.map((p) => p.id),
    words: probeItems.map((p) => p.word),
    lemmaFallbacks: { archived: 'archive (morphy detachment; surface form absent from index files)' },
    senseCounts: Object.fromEntries(probeItems.map((p, i) => [p.word, senses[i]!.length])),
    unreachablePairs: unreachable,
    similarity: sim,
    classicalSimilarity: classical,
    classicalCoverage: `${classicalDefined}/${n * n} cells defined`,
  });
}

main();
