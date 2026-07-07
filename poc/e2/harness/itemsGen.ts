/** Writes inputs/items.json — the published E2 item set (counts + exclusions). */

import { encoderContentHash } from '@jeswr/kernel-encoder';
import { corpusPin, writeInput } from './common.js';
import { buildItems } from './items.js';
import { loadCorpus } from './corpus.js';

function main(): void {
  const corpus = loadCorpus();
  const { allItemIds, probeItems, excludedIds } = buildItems(corpus.map((c) => c.id));
  const labels = new Map(corpus.map((c) => [c.id, c.label]));
  writeInput('items.json', {
    date: new Date().toISOString(),
    encoderContentHash: encoderContentHash(),
    corpusPin: corpusPin(),
    policy:
      'Pre-registered item set: explicated concepts only (kernel-v0 contains no bare primes, so the prime-block exclusion removes nothing). Multi-word labels have no single surface word to probe and are excluded from the word-probe analysis set; they remain in the shipped 54x54 kernel matrices. Tie policy: Spearman with average ranks for ties (mid-rank), identical in TS prep and python runner.',
    itemCountAll: allItemIds.length,
    itemCountAnalysis: probeItems.length,
    excluded: excludedIds.map((id) => ({ id, label: labels.get(id) ?? '', reason: 'multi-word label' })),
    items: probeItems.map((p) => ({ id: p.id, label: labels.get(p.id) ?? '', word: p.word, bank: p.bank })),
  });
}

main();
