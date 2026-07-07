/**
 * X4 on the AUTHORED kernel-v0 corpus (bead kernel-of-truth-138; poc-design
 * X4 / BLOCKER 1): for the two pre-registered fixed JL projections
 * (8192 -> 512, 8192 -> 576), (i) Spearman between the R^D and R^d RDMs over
 * the 54 authored concepts, (ii) the corpus adversarial single-edit margins
 * (X1-corpus's neighbour suite, same seed family => identical neighbour sets)
 * recomputed in R^d, with the fp16 floor restated in R^d.
 *
 * The projection is NOT re-derived: `jlProject` below is copied VERBATIM from
 * poc/harness/x4.ts (module-private there; importing would execute its
 * synthetic main()) — Achlioptas sign matrix, entries ±1/sqrt(d), signs drawn
 * from the encoder's deterministic SHA-256 stream under the PINNED labels
 * `jl/8192/512` and `jl/8192/576`, identical byte/bit consumption order.
 * Anyone can reproduce the matrices from those labels alone.
 *
 * Writes results/x4-kernel-v0-report.{json,md} — never x4-report.*.
 */

import {
  encodeConceptSet,
  encodeExplication,
  fp16RoundTrip,
  encoderContentHash,
  DetStream,
  type EditType,
} from '@jeswr/kernel-encoder';
import { angle, cosine, fmt, spearman, summarise } from '../harness/common.js';
import {
  corpusStamp,
  enumerateNeighbours,
  loadCorpus,
  slug,
  stampMd,
  writeCorpusReport,
} from './corpus-common.js';

/** Deterministic Achlioptas-style sign JL matrix, rows generated on the fly. (= harness/x4.ts) */
function jlProject(vectors: readonly Float64Array[], D: number, d: number): Float64Array[] {
  const outs = vectors.map(() => new Float64Array(d));
  const stream = new DetStream(`jl/${D}/${d}`);
  const scale = 1 / Math.sqrt(d);
  const row = new Float64Array(D);
  for (let r = 0; r < d; r++) {
    // 1 sign bit per entry, 8 per stream byte — fixed consumption order.
    for (let j = 0; j < D; j += 8) {
      const byte = stream.nextByte();
      for (let b = 0; b < 8 && j + b < D; b++) {
        row[j + b] = (byte >> b) & 1 ? scale : -scale;
      }
    }
    for (const [k, v] of vectors.entries()) {
      let s = 0;
      for (let j = 0; j < D; j++) s += row[j]! * v[j]!;
      outs[k]![r] = s;
    }
  }
  return outs;
}

interface PairRec {
  concept: string;
  edit: EditType;
  detail: string;
  angleD: number;
}

function main(): void {
  const corpus = loadCorpus();
  const D = 8192;
  const targets = [512, 576];
  console.log(`X4-corpus: ${corpus.docs.length} authored concepts, targets ${targets.join(', ')}`);

  const { vectors } = encodeConceptSet(corpus.defs);
  const ids = corpus.docs.map((d) => d.id);
  const originals = ids.map((id) => vectors.get(id)!);
  const fp16s = originals.map((v) => fp16RoundTrip(v));

  // --- adversarial pairs: X1-corpus's neighbour suite (same seed family) ---
  const pairRecs: PairRec[] = [];
  const projMutants: Record<number, Float64Array[]> = Object.fromEntries(targets.map((d) => [d, []]));
  const projPairOrig: Record<number, Float64Array[]> = Object.fromEntries(targets.map((d) => [d, []]));
  const BATCH = 64;
  let batchM: Float64Array[] = [];
  let batchO: Float64Array[] = [];
  const flush = (): void => {
    if (batchM.length === 0) return;
    for (const d of targets) {
      projMutants[d]!.push(...jlProject(batchM, D, d));
      projPairOrig[d]!.push(...jlProject(batchO, D, d));
    }
    batchM = [];
    batchO = [];
  };
  const t0 = Date.now();
  for (const doc of corpus.docs) {
    const v = vectors.get(doc.id)!;
    const set = enumerateNeighbours(doc.explication, doc.id);
    for (const nb of set.neighbours) {
      let vm: Float64Array;
      try {
        vm = encodeExplication(nb.mutant, { concepts: vectors });
      } catch {
        continue; // counted by X1-corpus; margins here mirror its successful encodes
      }
      pairRecs.push({ concept: doc.id, edit: nb.edit, detail: nb.detail, angleD: angle(v, vm) });
      batchM.push(vm);
      batchO.push(v);
      if (batchM.length >= BATCH) flush();
    }
    console.log(`  ${slug(doc.id)}: ${set.neighbours.length} neighbours (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  flush();

  // --- full-D reference numbers ---
  const rdmD: number[] = [];
  for (let i = 0; i < originals.length; i++) {
    for (let j = i + 1; j < originals.length; j++) rdmD.push(cosine(originals[i]!, originals[j]!));
  }
  const advD = pairRecs.map((p) => p.angleD);
  const floorD = Math.max(...originals.map((v, i) => angle(v, fp16s[i]!)));
  const minD = pairRecs.reduce((m, p) => (p.angleD < m.angleD ? p : m));

  // --- projections of originals + fp16 round-trips ---
  const results: Record<string, unknown> = {};
  for (const d of targets) {
    console.log(`X4-corpus: projecting originals to d=${d}`);
    const projO = jlProject(originals, D, d);
    const projF = jlProject(fp16s, D, d);
    const rdmd: number[] = [];
    for (let i = 0; i < projO.length; i++) {
      for (let j = i + 1; j < projO.length; j++) rdmd.push(cosine(projO[i]!, projO[j]!));
    }
    const rho = spearman(rdmD, rdmd);
    // Named minimum authored pair in R^d (is the R^D nearest pair preserved?).
    let minPd = { a: '', b: '', angle: Infinity };
    for (let i = 0; i < projO.length; i++) {
      for (let j = i + 1; j < projO.length; j++) {
        const a = angle(projO[i]!, projO[j]!);
        if (a < minPd.angle) minPd = { a: ids[i]!, b: ids[j]!, angle: a };
      }
    }
    const floord = Math.max(...projO.map((v, i) => angle(v, projF[i]!)));
    const advd = projMutants[d]!.map((vm, i) => angle(projPairOrig[d]![i]!, vm));
    let minIdx = 0;
    for (let i = 1; i < advd.length; i++) if (advd[i]! < advd[minIdx]!) minIdx = i;
    const minRec = pairRecs[minIdx]!;
    const ratio = advd[minIdx]! / floord;
    results[`${D}->${d}`] = {
      rdmSpearman: rho,
      adversarialMarginsRad: summarise(advd),
      minAdversarialRad: advd[minIdx],
      minAdversarialEdit: { concept: minRec.concept, edit: minRec.edit, detail: minRec.detail },
      minAuthoredPair: minPd,
      fp16FloorRad: floord,
      minToFloorRatio: ratio,
      verdictX1Criteria: ratio > 5 ? 'SUCCESS' : ratio < 2 ? 'FAILURE' : 'INCONCLUSIVE',
    };
    console.log(`  d=${d}: RDM Spearman ${fmt(rho)}, min adv ${fmt(advd[minIdx]!, 6)} rad = ${fmt(ratio, 1)}x floor`);
  }

  const stamp = corpusStamp(corpus, encoderContentHash());
  const json = {
    ...stamp,
    suite: 'X4-corpus: fixed JL projection distortion on authored kernel-v0',
    D,
    adversarialPairs: pairRecs.length,
    jlDerivation:
      'Achlioptas sign matrix, ±1/sqrt(d), signs from SHA-256 stream label jl/<D>/<d> (det.ts DET_DOMAIN) — pinned labels reused from harness/x4.ts, no new projections',
    fullD: {
      rdmPairs: rdmD.length,
      adversarialMarginsRad: summarise(advD),
      minAdversarialRad: minD.angleD,
      minAdversarialEdit: { concept: minD.concept, edit: minD.edit, detail: minD.detail },
      fp16FloorRad: floorD,
      minToFloorRatio: minD.angleD / floorD,
    },
    projections: results,
    note: 'E-series claims inherit these R^d numbers (poc-design rule 3). Neighbour suite = X1-corpus seed family x1c/<id>/<s>, deduped, saturation-sampled.',
  };
  const md = [
    '# X4 on kernel-v0 — fixed JL projection distortion',
    '',
    ...stampMd(stamp),
    `adversarial pairs: ${pairRecs.length} (X1-corpus single-edit neighbour suite); JL: ${json.jlDerivation}`,
    '',
    `Full-D reference: min adversarial angle ${fmt(minD.angleD, 6)} rad ` +
      `(\`${slug(minD.concept)}\`, ${minD.edit}); fp16 floor ${fmt(floorD, 6)} rad; ratio ${fmt(minD.angleD / floorD, 1)}x.`,
    '',
    '| projection | RDM Spearman | min adv angle (rad) | median adv angle | fp16 floor (rad) | min/floor | X1-criteria verdict |',
    '|---|---|---|---|---|---|---|',
    ...targets.map((d) => {
      const r = results[`${D}->${d}`] as {
        rdmSpearman: number;
        adversarialMarginsRad: { median: number };
        minAdversarialRad: number;
        fp16FloorRad: number;
        minToFloorRatio: number;
        verdictX1Criteria: string;
        minAdversarialEdit: { concept: string; edit: string };
      };
      return (
        `| ${D} -> ${d} | ${fmt(r.rdmSpearman)} | ${fmt(r.minAdversarialRad, 6)} ` +
        `(\`${slug(r.minAdversarialEdit.concept)}\`, ${r.minAdversarialEdit.edit}) | ${fmt(r.adversarialMarginsRad.median)} | ` +
        `${fmt(r.fp16FloorRad, 6)} | ${fmt(r.minToFloorRatio, 1)}x | ${r.verdictX1Criteria} |`
      );
    }),
    '',
    ...targets.map((d) => {
      const r = results[`${D}->${d}`] as { minAuthoredPair: { a: string; b: string; angle: number } };
      return `- min authored pair at d=${d}: \`${slug(r.minAuthoredPair.a)}\` <-> \`${slug(r.minAuthoredPair.b)}\` at ${fmt(r.minAuthoredPair.angle, 6)} rad`;
    }),
    '',
    `> ${json.note}`,
  ].join('\n');
  writeCorpusReport('x4-kernel-v0-report', json, md);
  console.log('X4-corpus done.');
}

main();
