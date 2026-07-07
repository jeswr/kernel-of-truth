/**
 * X4 — projection distortion (poc-design.md Phase X, BLOCKER 1; dimension
 * policy of architecture.md §1.3): for each pre-registered (D, d) pair,
 * ONE fixed, seedless, deterministic JL projection (Achlioptas sign matrix,
 * entries ±1/sqrt(d), signs from the SHA-256 stream `jl/<D>/<d>` — published
 * by construction, reproducible by anyone from this source).
 *
 * Measured: (i) Spearman between the R^D and R^d RDMs on the corpus
 * (kernel v0 once authored; synthetics here); (ii) X1's adversarial
 * single-edit margins recomputed in R^d. Pre-registered pairs:
 * (8192 -> 512) and (8192 -> 576). These R^d numbers, not the D=8192 ones,
 * are what E-series claims inherit.
 */

import {
  encodeExplication,
  generateExplication,
  mutateExplication,
  fp16RoundTrip,
  encoderContentHash,
  DetStream,
} from '@jeswr/kernel-encoder';
import {
  angle,
  argValue,
  cosine,
  ensureDirs,
  fmt,
  spearman,
  summarise,
  writeReport,
} from './common.js';

/** Deterministic Achlioptas-style sign JL matrix, rows generated on the fly. */
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

function main(): void {
  ensureDirs();
  const D = 8192;
  const n = Number(argValue('--n') ?? 300);
  const targets = [512, 576];

  // Corpus: reuse the X1 seed family (same shapes) + single-edit mutants.
  console.log(`X4: encoding ${n} originals + mutants at D=${D}`);
  const originals: Float64Array[] = [];
  const pairs: { v: Float64Array; vm: Float64Array; edit: string }[] = [];
  for (let i = 0; i < n; i++) {
    const tc = [1, 2, 3, 4, 6, 8, 12, 16][i % 8]!;
    const dep = [1, 2, 2, 3, 3, 4, 5, 2][Math.floor(i / 8) % 8]!;
    const ast = generateExplication({ seed: `x1/${i}`, topClauses: tc, depth: dep });
    const v = encodeExplication(ast);
    originals.push(v);
    const mut = mutateExplication(ast, `x1mut/${i}`);
    if (mut !== null) pairs.push({ v, vm: encodeExplication(mut.mutant), edit: mut.edit });
  }
  // Full-D reference numbers.
  const rdmD: number[] = [];
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) rdmD.push(cosine(originals[i]!, originals[j]!));
  }
  const advD = pairs.map((p) => angle(p.v, p.vm));
  const floorD = Math.max(...originals.slice(0, 100).map((v) => angle(v, fp16RoundTrip(v))));

  const results: Record<string, unknown> = {};
  for (const d of targets) {
    console.log(`X4: projecting to d=${d}`);
    const projO = jlProject(originals, D, d);
    const projPairsV = jlProject(pairs.map((p) => p.v), D, d);
    const projPairsM = jlProject(pairs.map((p) => p.vm), D, d);
    const rdmd: number[] = [];
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) rdmd.push(cosine(projO[i]!, projO[j]!));
    }
    const rho = spearman(rdmD, rdmd);
    const advd = projPairsV.map((v, i) => angle(v, projPairsM[i]!));
    const floord = Math.max(...projO.slice(0, 100).map((v, i) => angle(v, jlProject([fp16RoundTrip(originals[i]!)], D, d)[0]!)));
    results[`${D}->${d}`] = {
      rdmSpearman: rho,
      adversarialMarginsRad: summarise(advd),
      minAdversarialRad: Math.min(...advd),
      fp16FloorRad: floord,
      minToFloorRatio: Math.min(...advd) / floord,
    };
    console.log(`  d=${d}: RDM Spearman ${fmt(rho)}, min adv ${fmt(Math.min(...advd))} rad`);
  }

  const json = {
    date: new Date().toISOString(),
    encoderContentHash: encoderContentHash(),
    D,
    n,
    pairs: pairs.length,
    jlDerivation: 'Achlioptas sign matrix, ±1/sqrt(d), signs from SHA-256 stream label jl/<D>/<d> (det.ts DET_DOMAIN)',
    fullD: {
      adversarialMarginsRad: summarise(advD),
      minAdversarialRad: Math.min(...advD),
      fp16FloorRad: floorD,
    },
    projections: results,
    note: 'synthetic corpus; re-run on kernel v0 when authored. E-series claims inherit the R^d numbers (poc-design rule 3).',
  };
  const md = [
    '# X4 — fixed JL projection distortion',
    '',
    `date: ${json.date}`,
    `encoder content-hash: \`${json.encoderContentHash}\``,
    `corpus: ${n} synthetics (${pairs.length} adversarial pairs); JL: ${json.jlDerivation}`,
    '',
    `Full-D reference: min adversarial angle ${fmt(json.fullD.minAdversarialRad, 6)} rad; fp16 floor ${fmt(json.fullD.fp16FloorRad, 6)} rad.`,
    '',
    '| projection | RDM Spearman | min adv angle (rad) | median adv angle | fp16 floor (rad) | min/floor |',
    '|---|---|---|---|---|---|',
    ...targets.map((d) => {
      const r = results[`${D}->${d}`] as {
        rdmSpearman: number;
        adversarialMarginsRad: { median: number };
        minAdversarialRad: number;
        fp16FloorRad: number;
        minToFloorRatio: number;
      };
      return `| ${D} -> ${d} | ${fmt(r.rdmSpearman)} | ${fmt(r.minAdversarialRad, 6)} | ${fmt(r.adversarialMarginsRad.median)} | ${fmt(r.fp16FloorRad, 6)} | ${fmt(r.minToFloorRatio, 1)}x |`;
    }),
    '',
    `> ${json.note}`,
  ].join('\n');
  writeReport('x4-report', json, md);
  console.log('X4 done.');
}

main();
