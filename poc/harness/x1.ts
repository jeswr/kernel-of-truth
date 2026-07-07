/**
 * X1 — margins, adversarial-first (poc-design.md Phase X, rev 2 MAJOR 17/18).
 *
 * Headline: the angle distribution over the SINGLE-EDIT-NEIGHBOUR suite
 * (operator flip / clause swap / referent-index change / filler substitution
 * via the seeded mutator). Secondary: min pairwise angle over random
 * synthetics ("near-vacuous, reported for completeness"). Noise floor,
 * operationally defined: max angular self-distance under an fp16 round-trip
 * (cross-platform re-encode is witnessed by X0's committed goldens; this box
 * measures the fp16 leg).
 *
 * Pre-registered criteria at D=8192:
 *   success: min adversarial angle > 5x floor; failure: < 2x; else inconclusive.
 *
 * Kernel-v0 data does not exist yet (concept authoring is a separate stream),
 * so the suite runs on the synthetic corpus only — stated here per the
 * no-silent-caveats rule; the harness re-runs unchanged once kernel v0 lands.
 *
 * Blockwise + checkpointed: resumes from poc/results/x1-checkpoint.json.
 * Reduced default n=500; full run: `npm run x1:full` (n=10^4, full pairwise).
 */

import {
  canonicalJson,
  encodeExplication,
  generateExplication,
  mutateExplication,
  fp16RoundTrip,
  encoderContentHash,
  type EditType,
} from '@jeswr/kernel-encoder';
import {
  angle,
  argValue,
  ensureDirs,
  fmt,
  loadCheckpoint,
  saveCheckpoint,
  summarise,
  writeReport,
} from './common.js';

interface X1Checkpoint {
  n: number;
  done: number;
  adversarial: { angle: number; edit: EditType; seedIdx: number }[];
  fpFloorAngles: number[];
  skipped: number;
}

const CHECKPOINT = 'x1-checkpoint.json';
const BLOCK = 25;

function corpusShape(i: number): { topClauses: number; depth: number } {
  // Deterministic mixture over clause-count/depth shapes.
  const tc = [1, 2, 3, 4, 6, 8, 12, 16][i % 8]!;
  const dep = [1, 2, 2, 3, 3, 4, 5, 2][Math.floor(i / 8) % 8]!;
  return { topClauses: tc, depth: dep };
}

function main(): void {
  ensureDirs();
  const n = Number(argValue('--n') ?? 500);
  const pairsMode = argValue('--pairs') ?? (n <= 1000 ? 'full' : 'sample');
  const fpFloorN = Math.min(n, 200);

  let ck = loadCheckpoint<X1Checkpoint>(CHECKPOINT);
  if (ck === null || ck.n !== n) {
    ck = { n, done: 0, adversarial: [], fpFloorAngles: [], skipped: 0 };
  }
  console.log(`X1: n=${n}, resuming at ${ck.done}`);

  // --- adversarial single-edit suite (blockwise) ---
  const t0 = Date.now();
  while (ck.done < n) {
    const end = Math.min(ck.done + BLOCK, n);
    for (let i = ck.done; i < end; i++) {
      const { topClauses, depth } = corpusShape(i);
      const ast = generateExplication({ seed: `x1/${i}`, topClauses, depth });
      const mut = mutateExplication(ast, `x1mut/${i}`);
      if (mut === null) {
        ck.skipped++;
        continue;
      }
      const v = encodeExplication(ast);
      const vm = encodeExplication(mut.mutant);
      ck.adversarial.push({ angle: angle(v, vm), edit: mut.edit, seedIdx: i });
      if (ck.fpFloorAngles.length < fpFloorN) {
        ck.fpFloorAngles.push(angle(v, fp16RoundTrip(v)));
      }
    }
    ck.done = end;
    saveCheckpoint(CHECKPOINT, ck);
    if (ck.done % 100 === 0 || ck.done === n) {
      const rate = ck.done / ((Date.now() - t0) / 1000);
      console.log(`  adversarial ${ck.done}/${n} (${rate.toFixed(1)}/s incl. resume skew)`);
    }
  }

  // --- secondary: min pairwise angle over DISTINCT random explications ---
  // Injectivity is a claim about distinct explications; the small-shape region
  // of the synthetic space is finite, so the corpus can contain exact AST
  // duplicates (angle 0 by identity, not by collision) — those are deduped
  // and counted instead.
  const pairCount = pairsMode === 'full' ? n : Math.min(n, 2000);
  console.log(`X1: pairwise scan over ${pairCount} vectors (${pairsMode})`);
  const vecs: Float64Array[] = [];
  const asts: string[] = [];
  for (let i = 0; i < pairCount; i++) {
    const { topClauses, depth } = corpusShape(i);
    const ast = generateExplication({ seed: `x1/${i}`, topClauses, depth });
    asts.push(canonicalJson(ast));
    vecs.push(encodeExplication(ast));
  }
  let minPair = Infinity;
  let minPairIdx: [number, number] = [-1, -1];
  let duplicateAstPairs = 0;
  for (let i = 0; i < vecs.length; i++) {
    for (let j = i + 1; j < vecs.length; j++) {
      if (asts[i] === asts[j]) {
        duplicateAstPairs++;
        continue;
      }
      const a = angle(vecs[i]!, vecs[j]!);
      if (a < minPair) {
        minPair = a;
        minPairIdx = [i, j];
      }
    }
    if (i % 200 === 0 && i > 0) console.log(`  pair scan row ${i}/${vecs.length}`);
  }

  // --- analysis ---
  const floor = Math.max(...ck.fpFloorAngles);
  const allAngles = ck.adversarial.map((a) => a.angle);
  const minAdv = Math.min(...allAngles);
  const overall = summarise(allAngles);
  const byEdit: Record<string, ReturnType<typeof summarise>> = {};
  for (const edit of ['operator-flip', 'clause-swap', 'referent-index', 'filler-substitution'] as const) {
    const xs = ck.adversarial.filter((a) => a.edit === edit).map((a) => a.angle);
    if (xs.length > 0) byEdit[edit] = summarise(xs);
  }
  const ratio = minAdv / floor;
  const verdict = ratio > 5 ? 'SUCCESS' : ratio < 2 ? 'FAILURE' : 'INCONCLUSIVE';

  const json = {
    date: new Date().toISOString(),
    encoderContentHash: encoderContentHash(),
    n,
    reduced: n < 10000,
    skippedNoEdit: ck.skipped,
    fp16FloorRad: floor,
    fp16FloorN: ck.fpFloorAngles.length,
    minAdversarialRad: minAdv,
    ratioToFloor: ratio,
    verdict,
    criteria: 'success > 5x floor; failure < 2x floor; else inconclusive (poc-design X1)',
    adversarialSummaryRad: overall,
    byEdit,
    secondary: {
      pairVectors: pairCount,
      minPairwiseAngleRad: minPair,
      minPairIdx,
      duplicateAstPairs,
    },
    note: 'synthetic corpus only; kernel-v0 explications not yet authored (separate stream). Cross-platform leg of the floor is witnessed by X0 goldens.',
  };
  const md = [
    '# X1 — adversarial single-edit margin suite',
    '',
    `date: ${json.date}`,
    `encoder content-hash: \`${json.encoderContentHash}\``,
    `n = ${n}${json.reduced ? ' (REDUCED run; full pre-registered run is n=10^4 via `npm run x1:full`)' : ''}, skipped (no applicable edit): ${ck.skipped}`,
    '',
    '## Headline',
    '',
    `- fp16 round-trip noise floor (max over ${ck.fpFloorAngles.length} vectors): **${fmt(floor, 6)} rad**`,
    `- min adversarial single-edit angle: **${fmt(minAdv, 6)} rad**`,
    `- ratio: **${fmt(ratio, 1)}x floor** -> **${verdict}** (success >5x, failure <2x)`,
    '',
    '## Adversarial angle distribution (radians)',
    '',
    '| suite | n | min | p1 | p5 | median | p95 | max |',
    '|---|---|---|---|---|---|---|---|',
    `| all | ${overall.n} | ${fmt(overall.min)} | ${fmt(overall.p1)} | ${fmt(overall.p5)} | ${fmt(overall.median)} | ${fmt(overall.p95)} | ${fmt(overall.max)} |`,
    ...Object.entries(byEdit).map(
      ([k, s]) => `| ${k} | ${s.n} | ${fmt(s.min)} | ${fmt(s.p1)} | ${fmt(s.p5)} | ${fmt(s.median)} | ${fmt(s.p95)} | ${fmt(s.max)} |`,
    ),
    '',
    '## Secondary (near-vacuous, for completeness)',
    '',
    `- min pairwise angle over ${pairCount} random synthetics (distinct ASTs): ${fmt(minPair)} rad (pair ${minPairIdx.join(', ')}); exact-duplicate AST pairs excluded: ${duplicateAstPairs}`,
    '',
    `> ${json.note}`,
  ].join('\n');
  writeReport('x1-report', json, md);
  console.log(`X1 ${verdict}: min adversarial ${fmt(minAdv, 6)} rad = ${fmt(ratio, 1)}x floor (${fmt(floor, 6)})`);
}

main();
