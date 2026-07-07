/**
 * X1-q — adversarial single-edit margins for the toy-native variant
 * kot-enc-Bq/1 at D ∈ {512, 576} (bead kernel-of-truth-5xo).
 *
 * Pre-registered bars RESTATED for the variant (same criteria as poc-design
 * X1, floors measured at NATIVE D):
 *   success: min adversarial angle > 5x measured fp16 floor at that D;
 *   failure: < 2x; else inconclusive.
 * Two suites per D:
 *   corpus  — every kernel-v0 explication's distinct single-edit neighbours,
 *             enumerated to saturation with the SAME seed family as X1-corpus
 *             (x1c/<id>/<s>; corpus-common.ts enumerateNeighbours), margins
 *             re-encoded natively at D. THIS is the bead's gate suite.
 *   synth   — n=500 seeded synthetics (harness/x1.ts seed families x1/<i>,
 *             x1mut/<i>, same shape mixture), reported alongside.
 * fp16 floor per suite: max angular self-distance under fp16 round-trip over
 * the suite's originals (corpus: all 54; synth: first 200) — the operational
 * floor definition of poc-design X1 at native D. Cross-platform leg is
 * witnessed by the X0-q goldens.
 *
 * Tighter margins than D=8192 are EXPECTED findings to quantify (the
 * quasi-orthogonal crosstalk floor is nonzero); this harness measures, the
 * verdict line states the pre-registered bar verbatim.
 *
 * Writes results/x1-q-report.{json,md} + checkpoint x1-q-checkpoint.json —
 * never the synthetic run's x1-report / x1-checkpoint files nor the corpus
 * run's x1-kernel-v0 files (the live x1:full process owns those).
 */

import {
  encodeConceptSetQ,
  encodeExplicationQ,
  generateExplication,
  mutateExplication,
  fp16RoundTrip,
  encoderContentHashQ,
  ALGORITHM_VERSION_Q,
  type EditType,
} from '@jeswr/kernel-encoder';
import { angle, fmt, summarise } from '../harness/common.js';
import {
  enumerateNeighbours,
  loadCorpus,
  loadCorpusCheckpoint,
  saveCorpusCheckpoint,
  slug,
  writeCorpusReport,
} from './corpus-common.js';

const DIMS = [512, 576] as const;
const SYNTH_N = 500;
const CHECKPOINT = 'x1-q-checkpoint.json';

interface Margin {
  angle: number;
  edit: EditType;
  detail: string;
}

interface ConceptMarginsQ {
  id: string;
  neighbours: number;
  seedsUsed: number;
  lastNewSeed: number;
  saturated: boolean;
  encodeFailures: number;
  /** margins keyed by D */
  margins: Record<string, Margin[]>;
}

interface X1QCheckpoint {
  corpusContentHash: string;
  perConcept: ConceptMarginsQ[];
}

/** = harness/x1.ts corpusShape: deterministic mixture over clause-count/depth. */
function corpusShape(i: number): { topClauses: number; depth: number } {
  const tc = [1, 2, 3, 4, 6, 8, 12, 16][i % 8]!;
  const dep = [1, 2, 2, 3, 3, 4, 5, 2][Math.floor(i / 8) % 8]!;
  return { topClauses: tc, depth: dep };
}

function verdictOf(ratio: number): string {
  return ratio > 5 ? 'SUCCESS' : ratio < 2 ? 'FAILURE' : 'INCONCLUSIVE';
}

function main(): void {
  const corpus = loadCorpus();
  console.log(`X1-q: ${corpus.docs.length} authored concepts at D ∈ {${DIMS.join(', ')}}`);

  // Native canonical vectors + corpus fp16 floors per D.
  const vectorsByD = new Map<number, Map<string, Float64Array>>();
  const corpusFloor: Record<string, { floor: number; worst: string }> = {};
  for (const D of DIMS) {
    const { vectors } = encodeConceptSetQ(corpus.defs, { params: { D } });
    vectorsByD.set(D, vectors);
    let floor = 0;
    let worst = '';
    for (const [id, v] of vectors) {
      const a = angle(v, fp16RoundTrip(v));
      if (a > floor) {
        floor = a;
        worst = id;
      }
    }
    corpusFloor[String(D)] = { floor, worst };
    console.log(`  D=${D}: corpus fp16 floor ${fmt(floor, 6)} rad (worst: ${slug(worst)})`);
  }

  // --- corpus suite: distinct single-edit neighbours, margins at each D ---
  let ck = loadCorpusCheckpoint<X1QCheckpoint>(CHECKPOINT);
  if (ck === null || ck.corpusContentHash !== corpus.corpusContentHash) {
    ck = { corpusContentHash: corpus.corpusContentHash, perConcept: [] };
  }
  const done = new Set(ck.perConcept.map((c) => c.id));
  const t0 = Date.now();
  for (const doc of corpus.docs) {
    if (done.has(doc.id)) continue;
    const set = enumerateNeighbours(doc.explication, doc.id);
    const rec: ConceptMarginsQ = {
      id: doc.id,
      neighbours: set.neighbours.length,
      seedsUsed: set.seedsUsed,
      lastNewSeed: set.lastNewSeed,
      saturated: set.saturated,
      encodeFailures: 0,
      margins: Object.fromEntries(DIMS.map((D) => [String(D), []])),
    };
    for (const nb of set.neighbours) {
      for (const D of DIMS) {
        const vectors = vectorsByD.get(D)!;
        try {
          const vm = encodeExplicationQ(nb.mutant, { params: { D }, concepts: vectors });
          rec.margins[String(D)]!.push({
            angle: angle(vectors.get(doc.id)!, vm),
            edit: nb.edit,
            detail: nb.detail,
          });
        } catch (e) {
          rec.encodeFailures++;
          console.error(`  encode failure (D=${D}) for neighbour of ${slug(doc.id)}: ${(e as Error).message}`);
        }
      }
    }
    ck.perConcept.push(rec);
    saveCorpusCheckpoint(CHECKPOINT, ck);
    console.log(
      `  ${slug(doc.id)}: ${rec.neighbours} neighbours (saturated=${rec.saturated}), min ` +
        DIMS.map((D) => `${fmt(Math.min(...rec.margins[String(D)]!.map((m) => m.angle)), 4)}@${D}`).join(' ') +
        ` (${((Date.now() - t0) / 1000).toFixed(0)}s)`,
    );
  }

  // --- synthetic suite: n=500, seed families of harness/x1.ts ---
  console.log(`X1-q: synthetic suite n=${SYNTH_N}`);
  const synth: Record<string, { margins: Margin[]; floor: number; floorN: number; skipped: number }> =
    Object.fromEntries(DIMS.map((D) => [String(D), { margins: [], floor: 0, floorN: 0, skipped: 0 }]));
  for (let i = 0; i < SYNTH_N; i++) {
    const { topClauses, depth } = corpusShape(i);
    const ast = generateExplication({ seed: `x1/${i}`, topClauses, depth });
    const mut = mutateExplication(ast, `x1mut/${i}`);
    for (const D of DIMS) {
      const s = synth[String(D)]!;
      if (mut === null) {
        s.skipped++;
        continue;
      }
      const v = encodeExplicationQ(ast, { params: { D } });
      const vm = encodeExplicationQ(mut.mutant, { params: { D } });
      s.margins.push({ angle: angle(v, vm), edit: mut.edit, detail: mut.detail });
      if (s.floorN < 200) {
        s.floor = Math.max(s.floor, angle(v, fp16RoundTrip(v)));
        s.floorN++;
      }
    }
    if ((i + 1) % 100 === 0) console.log(`  synth ${i + 1}/${SYNTH_N} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }

  // --- analysis + report ---
  const perDim: Record<string, unknown> = {};
  const mdSections: string[] = [];
  for (const D of DIMS) {
    const dKey = String(D);
    const allMargins = ck.perConcept.flatMap((c) => c.margins[dKey]!);
    const minAdv = allMargins.reduce((m, x) => (x.angle < m.angle ? x : m));
    const minAdvConcept = ck.perConcept.find((c) => c.margins[dKey]!.includes(minAdv))!;
    const floor = corpusFloor[dKey]!.floor;
    const ratio = minAdv.angle / floor;
    const verdict = verdictOf(ratio);
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
        minAngle: Math.min(...c.margins[dKey]!.map((m) => m.angle)),
      }))
      .sort((a, b) => a.minAngle - b.minAngle);

    // all authored pairs at native D
    const vectors = vectorsByD.get(D)!;
    const ids = corpus.docs.map((d) => d.id);
    const pairAngles: { a: string; b: string; angle: number }[] = [];
    for (let i = 0; i < ids.length; i++) {
      for (let j = i + 1; j < ids.length; j++) {
        pairAngles.push({ a: ids[i]!, b: ids[j]!, angle: angle(vectors.get(ids[i]!)!, vectors.get(ids[j]!)!) });
      }
    }
    pairAngles.sort((x, y) => x.angle - y.angle);

    const s = synth[dKey]!;
    const sMin = s.margins.reduce((m, x) => (x.angle < m.angle ? x : m));
    const sRatio = sMin.angle / s.floor;

    perDim[dKey] = {
      encoderContentHashQ: encoderContentHashQ({ D }),
      corpus: {
        fp16FloorRad: floor,
        fp16FloorWorstConcept: corpusFloor[dKey]!.worst,
        totalNeighbours: allMargins.length,
        minAdversarialRad: minAdv.angle,
        minAdversarialEdit: { concept: minAdvConcept.id, edit: minAdv.edit, detail: minAdv.detail },
        ratioToFloor: ratio,
        verdict,
        adversarialSummaryRad: summarise(allMargins.map((m) => m.angle)),
        byEdit,
        perConceptMin10: perConceptMin.slice(0, 10),
        pairwise: {
          pairs: pairAngles.length,
          minPair: pairAngles[0],
          top5Nearest: pairAngles.slice(0, 5),
          summaryRad: summarise(pairAngles.map((p) => p.angle)),
        },
      },
      synthetic: {
        n: s.margins.length,
        skippedNoEdit: s.skipped,
        fp16FloorRad: s.floor,
        fp16FloorN: s.floorN,
        minAdversarialRad: sMin.angle,
        ratioToFloor: sRatio,
        verdict: verdictOf(sRatio),
        adversarialSummaryRad: summarise(s.margins.map((m) => m.angle)),
      },
    };

    const cSum = summarise(allMargins.map((m) => m.angle));
    const sSum = summarise(s.margins.map((m) => m.angle));
    mdSections.push(
      `## D = ${D}`,
      '',
      `encoder content-hash: \`${encoderContentHashQ({ D })}\``,
      '',
      `- corpus fp16 floor (max over 54 authored vectors at D=${D}): **${fmt(floor, 6)} rad** (worst: ${slug(corpusFloor[dKey]!.worst)})`,
      `- min corpus adversarial angle over **${allMargins.length}** neighbours: **${fmt(minAdv.angle, 6)} rad** ` +
        `(\`${slug(minAdvConcept.id)}\`, ${minAdv.edit}: ${minAdv.detail})`,
      `- ratio: **${fmt(ratio, 1)}x floor** -> **${verdict}** (pre-registered: success >5x, failure <2x)`,
      `- synthetics (n=${s.margins.length}): floor ${fmt(s.floor, 6)} rad, min ${fmt(sMin.angle, 6)} rad = ${fmt(sRatio, 1)}x -> ${verdictOf(sRatio)}`,
      `- min authored pair: \`${slug(pairAngles[0]!.a)}\` <-> \`${slug(pairAngles[0]!.b)}\` at ${fmt(pairAngles[0]!.angle, 6)} rad`,
      '',
      '| suite | n | min | p1 | p5 | median | p95 | max |',
      '|---|---|---|---|---|---|---|---|',
      `| corpus | ${cSum.n} | ${fmt(cSum.min)} | ${fmt(cSum.p1)} | ${fmt(cSum.p5)} | ${fmt(cSum.median)} | ${fmt(cSum.p95)} | ${fmt(cSum.max)} |`,
      ...Object.entries(byEdit).map(
        ([k, x]) => `| corpus/${k} | ${x.n} | ${fmt(x.min)} | ${fmt(x.p1)} | ${fmt(x.p5)} | ${fmt(x.median)} | ${fmt(x.p95)} | ${fmt(x.max)} |`,
      ),
      `| synthetic | ${sSum.n} | ${fmt(sSum.min)} | ${fmt(sSum.p1)} | ${fmt(sSum.p5)} | ${fmt(sSum.median)} | ${fmt(sSum.p95)} | ${fmt(sSum.max)} |`,
      '',
      '### 5 tightest per-concept minima',
      '',
      '| concept | neighbours | saturated | min angle (rad) | x floor |',
      '|---|---|---|---|---|',
      ...perConceptMin.slice(0, 5).map(
        (c) => `| ${c.id} | ${c.neighbours} | ${c.saturated} | ${fmt(c.minAngle, 6)} | ${fmt(c.minAngle / floor, 1)}x |`,
      ),
      '',
    );
  }

  const json = {
    date: new Date().toISOString(),
    suite: 'X1-q: adversarial single-edit margins at toy-native D (corpus + n=500 synthetics)',
    algorithmVersion: ALGORITHM_VERSION_Q,
    corpusManifestSha256: corpus.manifestSha256,
    corpusContentHash: corpus.corpusContentHash,
    criteria: 'per D: success > 5x fp16 floor at that D; failure < 2x; else inconclusive (poc-design X1 restated for kot-enc-Bq/1)',
    gateSuite: 'corpus (bead kernel-of-truth-5xo closes only on corpus verdict SUCCESS at both D)',
    unsaturatedConcepts: ck.perConcept.filter((c) => !c.saturated).map((c) => c.id),
    encodeFailures: ck.perConcept.reduce((s, c) => s + c.encodeFailures, 0),
    perDim,
  };
  const md = [
    '# X1-q — adversarial margins at toy-native D (kot-enc-Bq/1)',
    '',
    `date: ${json.date}`,
    `corpus: kernel-v0 — ${corpus.docs.length} concepts, content-hash \`${corpus.corpusContentHash}\``,
    `criteria: ${json.criteria}`,
    '',
    ...mdSections,
    '> Neighbour suite: encoder-package mutator, seed family x1c/<id>/<s>, deduped,',
    '> saturation-sampled (identical AST suite to X1-corpus at D=8192, so margins',
    '> are directly comparable across encoders). Synthetics: harness/x1.ts seed',
    '> families x1/<i>, x1mut/<i>. Cross-platform floor leg: X0-q goldens.',
  ].join('\n');
  writeCorpusReport('x1-q-report', json, md);
  for (const D of DIMS) {
    const p = perDim[String(D)] as { corpus: { minAdversarialRad: number; ratioToFloor: number; verdict: string } };
    console.log(
      `X1-q D=${D} ${p.corpus.verdict}: min corpus adversarial ${fmt(p.corpus.minAdversarialRad, 6)} rad = ${fmt(p.corpus.ratioToFloor, 1)}x floor`,
    );
  }
}

main();
