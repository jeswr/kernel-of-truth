/**
 * X1 on the AUTHORED kernel-v0 corpus (bead kernel-of-truth-138; pre-registered
 * in docs/poc-design.md Phase X — "every kernel-v0 explication ... mutated by
 * one operator flip / clause swap / referent-index change / filler
 * substitution").
 *
 * Headline: min adversarial angle over ALL distinct single-edit neighbours of
 * each of the 54 authored explications (neighbours enumerated to saturation
 * via the encoder's own mutator; see corpus-common.ts enumerateNeighbours).
 * Plus: ALL authored-pair pairwise angles (54×53/2 = 1431) with the minimum
 * pair NAMED (the give/take/gift cluster is the expected minimum).
 *
 * Pre-registered criteria at D=8192 (identical to synthetic X1):
 *   success: min adversarial angle > 5x measured fp16 floor; failure: < 2x.
 *
 * Writes results/x1-kernel-v0-report.{json,md} + its own checkpoint — never
 * the synthetic run's x1-report.* / x1-checkpoint.json.
 */

import {
  encodeConceptSet,
  encodeExplication,
  fp16RoundTrip,
  encoderContentHash,
  type EditType,
} from '@jeswr/kernel-encoder';
import { angle, fmt, summarise } from '../harness/common.js';
import {
  corpusStamp,
  enumerateNeighbours,
  loadCorpus,
  loadCorpusCheckpoint,
  saveCorpusCheckpoint,
  slug,
  stampMd,
  writeCorpusReport,
} from './corpus-common.js';

interface ConceptMargins {
  id: string;
  neighbours: number;
  seedsUsed: number;
  lastNewSeed: number;
  saturated: boolean;
  encodeFailures: number;
  margins: { angle: number; edit: EditType; detail: string }[];
}

interface X1CorpusCheckpoint {
  corpusContentHash: string;
  perConcept: ConceptMargins[];
}

const CHECKPOINT = 'x1-kernel-v0-checkpoint.json';

function main(): void {
  const corpus = loadCorpus();
  console.log(`X1-corpus: ${corpus.docs.length} authored concepts (corpus ${corpus.corpusContentHash.slice(0, 16)}...)`);

  // Canonical vectors: one whole-corpus encode (reference DAG, memoised).
  const { vectors } = encodeConceptSet(corpus.defs);

  // fp16 round-trip floor over ALL authored vectors (the corpus leg of the
  // operational floor; cross-platform leg witnessed by X0 goldens).
  let floor = 0;
  let floorId = '';
  for (const [id, v] of vectors) {
    const a = angle(v, fp16RoundTrip(v));
    if (a > floor) {
      floor = a;
      floorId = id;
    }
  }
  console.log(`fp16 floor over corpus: ${fmt(floor, 6)} rad (worst: ${slug(floorId)})`);

  // --- adversarial: all distinct single-edit neighbours of every concept ---
  let ck = loadCorpusCheckpoint<X1CorpusCheckpoint>(CHECKPOINT);
  if (ck === null || ck.corpusContentHash !== corpus.corpusContentHash) {
    ck = { corpusContentHash: corpus.corpusContentHash, perConcept: [] };
  }
  const done = new Set(ck.perConcept.map((c) => c.id));
  const t0 = Date.now();
  for (const doc of corpus.docs) {
    if (done.has(doc.id)) continue;
    const set = enumerateNeighbours(doc.explication, doc.id);
    const v = vectors.get(doc.id)!;
    const rec: ConceptMargins = {
      id: doc.id,
      neighbours: set.neighbours.length,
      seedsUsed: set.seedsUsed,
      lastNewSeed: set.lastNewSeed,
      saturated: set.saturated,
      encodeFailures: 0,
      margins: [],
    };
    for (const nb of set.neighbours) {
      try {
        // Mutants of reference-bearing concepts still carry concept refs:
        // resolve against the corpus's canonical vectors.
        const vm = encodeExplication(nb.mutant, { concepts: vectors });
        rec.margins.push({ angle: angle(v, vm), edit: nb.edit, detail: nb.detail });
      } catch (e) {
        rec.encodeFailures++;
        console.error(`  encode failure for neighbour of ${slug(doc.id)}: ${(e as Error).message}`);
      }
    }
    ck.perConcept.push(rec);
    saveCorpusCheckpoint(CHECKPOINT, ck);
    console.log(
      `  ${slug(doc.id)}: ${rec.neighbours} neighbours (saturated=${rec.saturated}), ` +
        `min ${fmt(Math.min(...rec.margins.map((m) => m.angle)), 4)} rad ` +
        `(${((Date.now() - t0) / 1000).toFixed(0)}s)`,
    );
  }

  // --- all authored-pair pairwise angles (54×53/2) ---
  const ids = corpus.docs.map((d) => d.id);
  const pairAngles: { a: string; b: string; angle: number }[] = [];
  for (let i = 0; i < ids.length; i++) {
    for (let j = i + 1; j < ids.length; j++) {
      pairAngles.push({ a: ids[i]!, b: ids[j]!, angle: angle(vectors.get(ids[i]!)!, vectors.get(ids[j]!)!) });
    }
  }
  pairAngles.sort((x, y) => x.angle - y.angle);
  const minPair = pairAngles[0]!;

  // --- analysis ---
  const allMargins = ck.perConcept.flatMap((c) => c.margins);
  const minAdv = allMargins.reduce((m, x) => (x.angle < m.angle ? x : m));
  const minAdvConcept = ck.perConcept.find((c) => c.margins.includes(minAdv))!;
  const ratio = minAdv.angle / floor;
  const verdict = ratio > 5 ? 'SUCCESS' : ratio < 2 ? 'FAILURE' : 'INCONCLUSIVE';
  const byEdit: Record<string, ReturnType<typeof summarise>> = {};
  for (const edit of ['operator-flip', 'clause-swap', 'referent-index', 'filler-substitution'] as const) {
    const xs = allMargins.filter((m) => m.edit === edit).map((m) => m.angle);
    if (xs.length > 0) byEdit[edit] = summarise(xs);
  }
  const perConceptMin = ck.perConcept
    .map((c) => ({
      id: slug(c.id),
      neighbours: c.neighbours,
      saturated: c.saturated,
      minAngle: Math.min(...c.margins.map((m) => m.angle)),
    }))
    .sort((a, b) => a.minAngle - b.minAngle);

  const stamp = corpusStamp(corpus, encoderContentHash());
  const json = {
    ...stamp,
    suite: 'X1-corpus: adversarial single-edit margins + all-pairs distances on authored kernel-v0',
    fp16FloorRad: floor,
    fp16FloorWorstConcept: floorId,
    fp16FloorN: vectors.size,
    totalNeighbours: allMargins.length,
    neighbourEncodeFailures: ck.perConcept.reduce((s, c) => s + c.encodeFailures, 0),
    unsaturatedConcepts: ck.perConcept.filter((c) => !c.saturated).map((c) => c.id),
    minAdversarialRad: minAdv.angle,
    minAdversarialEdit: { concept: minAdvConcept.id, edit: minAdv.edit, detail: minAdv.detail },
    ratioToFloor: ratio,
    verdict,
    criteria: 'success > 5x floor; failure < 2x floor; else inconclusive (poc-design X1)',
    adversarialSummaryRad: summarise(allMargins.map((m) => m.angle)),
    byEdit,
    perConceptMin,
    pairwise: {
      pairs: pairAngles.length,
      minPair,
      top10Nearest: pairAngles.slice(0, 10),
      summaryRad: summarise(pairAngles.map((p) => p.angle)),
    },
  };
  const md = [
    '# X1 on kernel-v0 — adversarial single-edit margins + all authored pairs',
    '',
    ...stampMd(stamp),
    '',
    '## Headline',
    '',
    `- fp16 round-trip noise floor (max over all ${vectors.size} authored vectors): **${fmt(floor, 6)} rad** (worst: ${slug(floorId)})`,
    `- min adversarial single-edit angle over **${allMargins.length}** distinct neighbours: **${fmt(minAdv.angle, 6)} rad**`,
    `  (concept \`${slug(minAdvConcept.id)}\`, edit ${minAdv.edit}: ${minAdv.detail})`,
    `- ratio: **${fmt(ratio, 1)}x floor** -> **${verdict}** (pre-registered: success >5x, failure <2x)`,
    '',
    '## Adversarial angle distribution (radians)',
    '',
    '| suite | n | min | p1 | p5 | median | p95 | max |',
    '|---|---|---|---|---|---|---|---|',
    `| all | ${json.adversarialSummaryRad.n} | ${fmt(json.adversarialSummaryRad.min)} | ${fmt(json.adversarialSummaryRad.p1)} | ${fmt(json.adversarialSummaryRad.p5)} | ${fmt(json.adversarialSummaryRad.median)} | ${fmt(json.adversarialSummaryRad.p95)} | ${fmt(json.adversarialSummaryRad.max)} |`,
    ...Object.entries(byEdit).map(
      ([k, s]) => `| ${k} | ${s.n} | ${fmt(s.min)} | ${fmt(s.p1)} | ${fmt(s.p5)} | ${fmt(s.median)} | ${fmt(s.p95)} | ${fmt(s.max)} |`,
    ),
    '',
    '### 10 tightest per-concept minima',
    '',
    '| concept | neighbours | saturated | min angle (rad) | x floor |',
    '|---|---|---|---|---|',
    ...perConceptMin.slice(0, 10).map(
      (c) => `| ${c.id} | ${c.neighbours} | ${c.saturated} | ${fmt(c.minAngle, 6)} | ${fmt(c.minAngle / floor, 1)}x |`,
    ),
    '',
    '## All authored-pair distances (54x53/2 = 1431 pairs)',
    '',
    `- **minimum pair: \`${slug(minPair.a)}\` <-> \`${slug(minPair.b)}\` at ${fmt(minPair.angle, 6)} rad** (${fmt(minPair.angle / floor, 1)}x floor)`,
    `- pairwise distribution: min ${fmt(json.pairwise.summaryRad.min)}, median ${fmt(json.pairwise.summaryRad.median)}, max ${fmt(json.pairwise.summaryRad.max)} rad`,
    '',
    '| rank | pair | angle (rad) |',
    '|---|---|---|',
    ...pairAngles.slice(0, 10).map((p, i) => `| ${i + 1} | ${slug(p.a)} <-> ${slug(p.b)} | ${fmt(p.angle, 6)} |`),
    '',
    '> Neighbour sets are enumerated with the encoder package\'s own seeded mutator',
    '> (one valid single edit per seed), deduped by canonical JSON, sampled to',
    '> saturation (no new mutant for max(500, 4x|found|) consecutive seeds).',
    '> Exhaustiveness is therefore empirical, not proven; per-concept saturation',
    '> flags above. Cross-platform leg of the floor is witnessed by X0 goldens.',
  ].join('\n');
  writeCorpusReport('x1-kernel-v0-report', json, md);
  console.log(
    `X1-corpus ${verdict}: min adversarial ${fmt(minAdv.angle, 6)} rad = ${fmt(ratio, 1)}x floor; ` +
      `min pair ${slug(minPair.a)}<->${slug(minPair.b)} ${fmt(minPair.angle, 6)} rad`,
  );
}

main();
