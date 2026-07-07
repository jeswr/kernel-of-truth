/**
 * Baseline 1 — word-embedding cosine RDM (docs/poc-design.md E2 primary
 * criterion: "word2vec cosine" relatedness baseline).
 *
 * Operationalisation (published; DEVIATION note): the pre-registration
 * names "word2vec cosine"; the prep brief instructs a small pretrained
 * embedding slice ("e.g. GloVe 6B.50d ... download only what's needed").
 * We use GloVe 6B **100d** (the streamable first member of the official
 * archive — see scripts/fetch-glove-slice.sh; cosine relatedness is the
 * quantity of interest, not the training algorithm or dimension). The
 * 51-word slice is committed for reproducibility (PDDL licence).
 */

import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { encoderContentHash } from '@jeswr/kernel-encoder';
import { INPUTS_DIR, corpusPin, cosine, isMain, similarityMatrix, writeInput } from './common.js';
import { loadCorpus } from './corpus.js';
import { buildItems } from './items.js';

export function loadEmbeddingSlice(file: string): Map<string, Float64Array> {
  const out = new Map<string, Float64Array>();
  for (const line of readFileSync(file, 'utf8').split('\n')) {
    if (line.length === 0) continue;
    const parts = line.split(' ');
    out.set(parts[0]!, Float64Array.from(parts.slice(1).map(Number)));
  }
  return out;
}

function main(): void {
  const corpus = loadCorpus();
  const { probeItems } = buildItems(corpus.map((c) => c.id));
  const slice = loadEmbeddingSlice(join(INPUTS_DIR, 'glove-slice-100d.txt'));
  const vecs = probeItems.map((p) => {
    const v = slice.get(p.word);
    if (v === undefined || v.length !== 100) throw new Error(`no 100d embedding for '${p.word}' — re-run fetch-glove`);
    return v;
  });
  const sim = similarityMatrix(vecs.length, (i, j) => cosine(vecs[i]!, vecs[j]!));
  writeInput('baseline-word2vec.json', {
    date: new Date().toISOString(),
    encoderContentHash: encoderContentHash(),
    corpusPin: corpusPin(),
    source:
      'GloVe 6B 100d (Wikipedia 2014 + Gigaword 5, 400k vocab, PDDL), 51-word slice committed at inputs/glove-slice-100d.txt. DEVIATION note: pre-registration says "word2vec cosine"; GloVe cosine used as the small-footprint pretrained-embedding operationalisation (flagged in poc/e2/README.md).',
    convention: 'similarity (cosine, unit diagonal); item order = ids[]',
    ids: probeItems.map((p) => p.id),
    words: probeItems.map((p) => p.word),
    similarity: sim,
  });
}

if (isMain(import.meta.url)) main();
