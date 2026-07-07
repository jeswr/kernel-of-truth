/**
 * Kernel-side E2 input: pairwise cosine similarity over the 54 kernel-v0
 * concepts' encoder vectors, at full D=8192 AND through the two
 * pre-registered fixed JL projections (8192->512, 8192->576; Common rule 3 /
 * X4). Writes inputs/kernel-rdm.json stamped with the encoder content-hash
 * and the corpus pin.
 *
 * Convention: matrices are SIMILARITY matrices (cosine; unit diagonal), not
 * dissimilarities. All Spearman comparisons downstream are convention-free up
 * to sign; the runner states the convention in its outputs.
 */

import { DEFAULT_PARAMS, encodeConceptSet, encoderContentHash } from '@jeswr/kernel-encoder';
import type { Explication } from '@jeswr/kernel-encoder';
import { corpusPin, cosine, jlProject, similarityMatrix, writeInput } from './common.js';
import { loadCorpus } from './corpus.js';
import { buildItems } from './items.js';

function main(): void {
  const corpus = loadCorpus();
  const defs = new Map<string, Explication>(corpus.map((c) => [c.id, c.explication]));
  console.log(`encoding ${defs.size} concepts at D=${DEFAULT_PARAMS.D} (reference DAG via encodeConceptSet)`);
  const { vectors } = encodeConceptSet(defs);

  const { allItemIds, probeItems, excludedIds } = buildItems(corpus.map((c) => c.id));
  const vecs = allItemIds.map((id) => {
    const v = vectors.get(id);
    if (v === undefined) throw new Error(`no vector for ${id}`);
    return v;
  });

  const D = DEFAULT_PARAMS.D;
  const n = vecs.length;
  const simFull = similarityMatrix(n, (i, j) => cosine(vecs[i]!, vecs[j]!));

  const projections: Record<string, { d: number; similarity: number[][] }> = {};
  for (const d of [512, 576]) {
    console.log(`JL-projecting ${n} vectors ${D} -> ${d} (Achlioptas signs, stream jl/${D}/${d})`);
    const proj = jlProject(vecs, D, d);
    projections[`jl${d}`] = { d, similarity: similarityMatrix(n, (i, j) => cosine(proj[i]!, proj[j]!)) };
  }

  writeInput('kernel-rdm.json', {
    date: new Date().toISOString(),
    encoderContentHash: encoderContentHash(),
    corpusPin: corpusPin(),
    D,
    convention: 'similarity (pairwise cosine, unit diagonal); item order = ids[] (alphabetical by slug)',
    jlDerivation:
      'Achlioptas sign matrix, entries ±1/sqrt(d), signs from SHA-256 stream label jl/<D>/<d> (encoder det.ts DET_DOMAIN); verbatim copy of poc/harness/x4.ts jlProject — the projection X4 measured distortion on (Common rule 3: E-series claims inherit the R^d numbers)',
    ids: allItemIds,
    excludedFromAnalysis: excludedIds,
    analysisIds: probeItems.map((p) => p.id),
    full: { D, similarity: simFull },
    projections,
  });
}

main();
