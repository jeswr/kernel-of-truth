/**
 * Frequency-matched random-word candidate pools (docs/poc-design.md E2
 * primary criterion: "frequency-matched random word sets must fall below
 * the kernel set (kernel rho > 95th percentile of k=100 random sets)").
 *
 * Published construction:
 *   - Frequency proxy: rank in the GloVe 6B vocabulary (ordered by corpus
 *     frequency in Wikipedia 2014 + Gigaword 5); ranks shipped at
 *     inputs/glove-ranks-top100k.txt by scripts/fetch-glove-slice.sh.
 *   - For each probe item with rank r: candidates are vocabulary words with
 *     rank in the geometric band [r/2, 2r] (clipped to top-100k), purely
 *     alphabetic, length >= 2, not a probe word, not a template word, and
 *     WordNet-attested in the item's bank POS (items.ts BANK_WORDNET_POS) —
 *     so a random set substitutes grammatically into the SAME context bank.
 *   - The `prep` bank is a closed class WordNet does not index; its pool is
 *     a hand-listed set of English locative prepositions (frequency-matched
 *     only loosely within the closed class — DEVIATION, flagged).
 *   - Up to 80 candidates per item, ordered by |log(rank/r)| (closest
 *     frequency first). The GPU runner draws k=100 sets with a fixed seed,
 *     one candidate per item, no duplicates within a set, restricted to the
 *     per-model in-vocab survivors.
 */

import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { encoderContentHash } from '@jeswr/kernel-encoder';
import { INPUTS_DIR, corpusPin, isMain, writeInput } from './common.js';
import { loadCorpus } from './corpus.js';
import { BANK_WORDNET_POS, buildItems } from './items.js';
import { TEMPLATE_BANKS } from './contexts.js';
import { loadWordnet } from './wordnet.js';
import type { WnPos } from './wordnet.js';

const POOL_SIZE = 80;

/** Closed-class locative pool for the `prep` bank (WordNet indexes no prepositions). */
export const PREP_POOL: readonly string[] = [
  'above', 'below', 'under', 'over', 'behind', 'beside', 'beyond', 'within',
  'outside', 'against', 'across', 'along', 'around', 'between', 'among',
  'beneath', 'past', 'through', 'toward', 'towards', 'upon', 'onto', 'by',
  'at', 'in',
];

function main(): void {
  const corpus = loadCorpus();
  const { probeItems } = buildItems(corpus.map((c) => c.id));
  const wn = loadWordnet();

  const ranksTxt = readFileSync(join(INPUTS_DIR, 'glove-ranks-top100k.txt'), 'utf8');
  const rankOf = new Map<string, number>();
  const byRank: string[] = [];
  for (const line of ranksTxt.split('\n')) {
    if (line.length === 0) continue;
    const [r, w] = line.split(' ');
    rankOf.set(w!, Number(r));
    byRank.push(w!);
  }
  const meta = JSON.parse(readFileSync(join(INPUTS_DIR, 'glove-slice-meta.json'), 'utf8')) as {
    ranks: Record<string, number>;
  };

  const probeWords = new Set(probeItems.map((p) => p.word));
  const templateWords = new Set<string>();
  for (const bank of Object.values(TEMPLATE_BANKS)) {
    for (const t of bank) {
      for (const tok of t.toLowerCase().replace('{w}', ' ').split(/[^a-z']+/)) {
        if (tok.length > 0) templateWords.add(tok);
      }
    }
  }

  const eligible = (w: string, poses: readonly string[]): boolean => {
    if (!/^[a-z]{2,}$/.test(w)) return false;
    if (probeWords.has(w) || templateWords.has(w)) return false;
    return poses.some((p) => wn.lookup(w, p as WnPos).length > 0);
  };

  const pools: Record<string, { rank: number; candidates: string[] }> = {};
  const thin: string[] = [];
  for (const item of probeItems) {
    const r = meta.ranks[item.word] ?? rankOf.get(item.word);
    if (r === undefined) throw new Error(`no GloVe rank for '${item.word}'`);
    let candidates: string[];
    if (item.bank === 'prep') {
      candidates = PREP_POOL.filter((w) => !probeWords.has(w)).sort(
        (a, b) =>
          Math.abs(Math.log((rankOf.get(a) ?? 1e9) / r)) - Math.abs(Math.log((rankOf.get(b) ?? 1e9) / r)),
      );
    } else {
      const lo = Math.max(1, Math.floor(r / 2));
      const hi = Math.min(byRank.length, r * 2);
      const poses = BANK_WORDNET_POS[item.bank];
      candidates = [];
      for (let rr = lo; rr <= hi; rr++) {
        const w = byRank[rr - 1]!;
        if (eligible(w, poses)) candidates.push(w);
      }
      candidates.sort((a, b) => Math.abs(Math.log(rankOf.get(a)! / r)) - Math.abs(Math.log(rankOf.get(b)! / r)));
      candidates = candidates.slice(0, POOL_SIZE);
    }
    if (candidates.length < 20) thin.push(`${item.word} (${candidates.length})`);
    pools[item.word] = { rank: r, candidates };
  }
  if (thin.length > 0) console.warn(`THIN POOLS (<20 candidates): ${thin.join(', ')}`);

  writeInput('freq-matched-pools.json', {
    date: new Date().toISOString(),
    encoderContentHash: encoderContentHash(),
    corpusPin: corpusPin(),
    construction:
      'per-item candidates: GloVe-6B rank band [r/2, 2r] (top-100k), alphabetic, len>=2, not probe/template word, WordNet-attested in the bank POS; <=80 per item ordered by |log(rank/r)|; prep bank = closed-class hand list (DEVIATION: loose frequency match within closed class, flagged). Runner draws k=100 sets, fixed seed, no within-set duplicates, per-model in-vocab filtered.',
    frequencyProxy: 'GloVe 6B vocabulary rank (corpus-frequency ordered), inputs/glove-ranks-top100k.txt',
    poolSize: POOL_SIZE,
    kSets: 100,
    thinPools: thin,
    pools,
  });
}

if (isMain(import.meta.url)) main();
