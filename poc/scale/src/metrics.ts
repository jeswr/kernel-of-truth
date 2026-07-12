/**
 * SCALE-1 S0 stage 4 — measured metrics at the first rung vs design predictions.
 *
 * Measures (design refs in parens):
 *  (a) per-concept encode cost + storage (from vec/manifest.json; §1.2, §6.4);
 *  (b) max-cosine collision/margin: full O(n²) NN pass at proj512/proj576
 *      with per-pair structural classification (edge / shared-target /
 *      disjoint), plain NN at native512 and native512lex; sampled NN at
 *      canon8192 — compared against the §6.5 Gaussian-crosstalk curve
 *      E[max spurious cos over m] ≈ √(2·ln m / D)  (≈0.046 at m=10⁴, D=8192);
 *  (c) duplicate censuses: exact vector duplicates AND structural duplicates
 *      (identical token multisets) — §6.5 "structurally indistinguishable
 *      AxiomsOnly records";
 *  (d) X4 RDM-Spearman re-measure on a 1,000-concept deterministic sample:
 *      RDM(canon8192) vs RDM(proj512/proj576/native512/native576) — design
 *      cites 0.9718 / 0.9706 at 54 kernel-v0 concepts.
 *
 * Every heavy step checkpoints a JSON intermediate under out/n<N>/metrics/
 * and is skipped on re-run. Single-threaded; callers nice -n 10.
 *
 * EPISTEMIC STATUS: MEASURED numbers for the EXPLORATORY kot-enc-import/0-poc
 * vectoriser on a STIPULATED WordNet subset. Not construction B, not a
 * pre-registered Phase-X result, no feasibility conclusion.
 */

import { createHash } from 'node:crypto';
import { existsSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import {
  ensureDir,
  fmt,
  loadConcepts,
  loadRows,
  loadStore,
  nowMs,
  outDirFor,
  readJson,
  RESULTS_DIR,
  spearman,
  summarise,
  targetN,
  writeJson,
  type DistributionSummary,
  type LexRecord,
} from './common.js';

const CURVE = (m: number, D: number): number => Math.sqrt((2 * Math.log(m)) / D);

interface Ctx {
  n: number;
  concepts: LexRecord[];
  mdir: string;
  adjacency: Set<number>[]; // row -> set of neighbor rows (either direction)
  targetIds: Int32Array[]; // row -> sorted axiom-target ids (interned)
  tokenHash: string[]; // row -> sha of sorted token multiset (structural identity)
  lexFileId: Int32Array; // row -> interned lexFile id (shared lexfile token ⇒ correlated vectors)
  zeroAxiomRows: number;
}

function buildCtx(n: number): Ctx {
  const concepts = loadConcepts(n);
  const rowOf = new Map<string, number>();
  concepts.forEach((c, i) => rowOf.set(c.id, i));
  const adjacency: Set<number>[] = concepts.map(() => new Set());
  const intern = new Map<string, number>();
  const targetIds: Int32Array[] = [];
  const tokenHash: string[] = [];
  concepts.forEach((c, i) => {
    const ids: number[] = [];
    for (const a of c.axioms) {
      const j = rowOf.get(a.target);
      if (j !== undefined) {
        adjacency[i]!.add(j);
        adjacency[j]!.add(i);
      }
      let id = intern.get(a.target);
      if (id === undefined) {
        id = intern.size;
        intern.set(a.target, id);
      }
      ids.push(id);
    }
    targetIds.push(Int32Array.from([...new Set(ids)].sort((a, b) => a - b)));
    const toks = [...c.axioms.map((a) => `ax/${a.rel}/${a.target}`), `lexfile/${c.annotations.lexFile}`].sort();
    tokenHash.push(createHash('sha256').update(toks.join(' ')).digest('hex'));
  });
  const lexIntern = new Map<string, number>();
  const lexFileId = new Int32Array(concepts.length);
  let zeroAxiomRows = 0;
  concepts.forEach((c, i) => {
    const lf = c.annotations.lexFile;
    let id = lexIntern.get(lf);
    if (id === undefined) {
      id = lexIntern.size;
      lexIntern.set(lf, id);
    }
    lexFileId[i] = id;
    if (c.axioms.length === 0) zeroAxiomRows++;
  });
  const mdir = join(outDirFor(n), 'metrics');
  ensureDir(mdir);
  return { n, concepts, mdir, adjacency, targetIds, tokenHash, lexFileId, zeroAxiomRows };
}

function sharedTarget(a: Int32Array, b: Int32Array): boolean {
  let i = 0;
  let j = 0;
  while (i < a.length && j < b.length) {
    const d = a[i]! - b[j]!;
    if (d === 0) return true;
    if (d < 0) i++;
    else j++;
  }
  return false;
}

/** Load a store as unit-normalised Float64Array rows. */
function loadUnit(n: number, store: string, D: number): Float64Array {
  const f32 = loadStore(n, store, D);
  const out = new Float64Array(n * D);
  for (let i = 0; i < n; i++) {
    let s = 0;
    const base = i * D;
    for (let j = 0; j < D; j++) {
      const x = f32[base + j]!;
      out[base + j] = x;
      s += x * x;
    }
    const nm = Math.sqrt(s);
    for (let j = 0; j < D; j++) out[base + j]! /= nm;
  }
  return out;
}

interface NnResult {
  store: string;
  D: number;
  classified: boolean;
  wallSeconds: number;
  nnAll: DistributionSummary;
  nnDisjoint?: DistributionSummary;
  disjointPairSigma?: number;
  disjointPairMax?: number;
  disjointPairCount?: number;
  pairsAbove: Record<string, number>;
  exactDuplicateRows: number;
  predictedCurveAtM: number;
  predictedSigma: number;
}

/**
 * Full O(n²) NN pass. If classified, also tracks per-concept max cosine over
 * DISJOINT pairs (no direct edge, no shared axiom target) plus the disjoint
 * pair-cosine moments (streamed; no O(n²) array kept).
 */
function nnPass(ctx: Ctx, store: string, D: number, classified: boolean): NnResult {
  const file = join(ctx.mdir, `nn-${store}.json`);
  const hit = readJson<NnResult>(file);
  if (hit !== null) return hit;
  const t0 = nowMs();
  const n = ctx.n;
  const V = loadUnit(n, store, D);
  const nnAll = new Float64Array(n).fill(-2);
  const nnDis = classified ? new Float64Array(n).fill(-2) : null;
  let disSum = 0;
  let disSum2 = 0;
  let disMax = -2;
  let disCount = 0;
  const thresholds = [0.99, 0.999, 0.9999];
  const above = [0, 0, 0];
  let dupRows = 0;
  for (let i = 0; i < n; i++) {
    const bi = i * D;
    const adj = ctx.adjacency[i]!;
    const ti = ctx.targetIds[i]!;
    for (let j = i + 1; j < n; j++) {
      const bj = j * D;
      let s = 0;
      for (let k = 0; k < D; k++) s += V[bi + k]! * V[bj + k]!;
      if (s > nnAll[i]!) nnAll[i] = s;
      if (s > nnAll[j]!) nnAll[j] = s;
      if (s > thresholds[0]!) {
        above[0] = above[0]! + 1;
        if (s > thresholds[1]!) above[1] = above[1]! + 1;
        if (s > thresholds[2]!) {
          above[2] = above[2]! + 1;
          if (ctx.tokenHash[i] === ctx.tokenHash[j]) dupRows++;
        }
      }
      if (nnDis !== null) {
        // disjoint = no direct edge, no shared axiom target, DIFFERENT lexFile
        // (shared lexfile tokens put a deterministic additive floor under the
        // pair cosine; excluded so the class compares cleanly to N(0, 1/D)).
        const related =
          ctx.lexFileId[i] === ctx.lexFileId[j] || adj.has(j) || sharedTarget(ti, ctx.targetIds[j]!);
        if (!related) {
          disSum += s;
          disSum2 += s * s;
          disCount++;
          if (s > disMax) disMax = s;
          if (s > nnDis[i]!) nnDis[i] = s;
          if (s > nnDis[j]!) nnDis[j] = s;
        }
      }
    }
    if (i % 1000 === 999) console.log(`  nn ${store}: row ${i + 1}/${n} (${((nowMs() - t0) / 1000).toFixed(0)}s)`);
  }
  const disMean = disCount > 0 ? disSum / disCount : NaN;
  const res: NnResult = {
    store,
    D,
    classified,
    wallSeconds: (nowMs() - t0) / 1000,
    nnAll: summarise([...nnAll]),
    ...(nnDis !== null
      ? {
          nnDisjoint: summarise([...nnDis].filter((x) => x > -2)),
          disjointPairSigma: Math.sqrt(Math.max(0, disSum2 / disCount - disMean * disMean)),
          disjointPairMax: disMax,
          disjointPairCount: disCount,
        }
      : {}),
    pairsAbove: { '>0.99': above[0]!, '>0.999': above[1]!, '>0.9999': above[2]! },
    exactDuplicateRows: dupRows,
    predictedCurveAtM: CURVE(n, D),
    predictedSigma: 1 / Math.sqrt(D),
  };
  writeJson(file, res);
  return res;
}

/** Deterministic sample rows: stride over the URN-sorted row order. */
function sampleRows(n: number, k: number): number[] {
  const stride = n / k;
  const rows: number[] = [];
  for (let i = 0; i < k; i++) rows.push(Math.min(n - 1, Math.floor(i * stride)));
  return [...new Set(rows)];
}

interface SampleResult {
  sampleSize: number;
  pairCount: number;
  canonNnAll: DistributionSummary;
  canonNnDisjoint: DistributionSummary;
  canonDisjointSigma: number;
  canonDisjointMax: number;
  canonPredictedSigma: number;
  canonPredictedCurveAtSample: number;
  canonPredictedCurveAt1e4: number;
  rdmSpearman: Record<string, number>;
  /** Spearman restricted to pairs with canon cosine > 0.05 (structure-bearing pairs). */
  rdmSpearmanTopPairs: Record<string, number>;
  topPairCount: number;
  /** Within-sample NN preservation: fraction of sample concepts whose canon-NN is the store-NN (recall@1) / within store top-10 (recall@10). */
  nnRecallAt1: Record<string, number>;
  nnRecallAt10: Record<string, number>;
  /** recall@1/@10 restricted to sample concepts whose canon NN cosine > 0.05 (structure-bearing NN). */
  nnRecallAt1Strong: Record<string, number>;
  nnRecallAt10Strong: Record<string, number>;
  strongNnCount: number;
  wallSeconds: number;
}

function sampleAnalysis(ctx: Ctx, stores: { store: string; D: number }[]): SampleResult {
  const file = join(ctx.mdir, 'sample-analysis.json');
  const hit = readJson<SampleResult>(file);
  if (hit !== null) return hit;
  const t0 = nowMs();
  const n = ctx.n;
  const rows = sampleRows(n, Math.min(1000, n));
  const k = rows.length;
  const D0 = 8192;

  // canon8192 sample rows (unit-normalised)
  const canon = new Float64Array(k * D0);
  for (let a = 0; a < k; a++) {
    const r = rows[a]!;
    const f32 = loadRows(n, 'canon8192', D0, r, r + 1);
    let s = 0;
    for (let j = 0; j < D0; j++) {
      canon[a * D0 + j] = f32[j]!;
      s += f32[j]! * f32[j]!;
    }
    const nm = Math.sqrt(s);
    for (let j = 0; j < D0; j++) canon[a * D0 + j]! /= nm;
  }

  // pair classification + canon RDM
  const pairCount = (k * (k - 1)) / 2;
  const canonRdm = new Float64Array(pairCount);
  const disjoint = new Uint8Array(pairCount);
  const nnAll = new Float64Array(k).fill(-2);
  const nnDis = new Float64Array(k).fill(-2);
  let disSum = 0;
  let disSum2 = 0;
  let disMax = -2;
  let disCount = 0;
  let p = 0;
  for (let a = 0; a < k; a++) {
    const i = rows[a]!;
    for (let b = a + 1; b < k; b++, p++) {
      const j = rows[b]!;
      let s = 0;
      const ba = a * D0;
      const bb = b * D0;
      for (let x = 0; x < D0; x++) s += canon[ba + x]! * canon[bb + x]!;
      canonRdm[p] = s;
      if (s > nnAll[a]!) nnAll[a] = s;
      if (s > nnAll[b]!) nnAll[b] = s;
      const related =
        ctx.lexFileId[i] === ctx.lexFileId[j] ||
        ctx.adjacency[i]!.has(j) ||
        sharedTarget(ctx.targetIds[i]!, ctx.targetIds[j]!);
      if (!related) {
        disjoint[p] = 1;
        disSum += s;
        disSum2 += s * s;
        disCount++;
        if (s > disMax) disMax = s;
        if (s > nnDis[a]!) nnDis[a] = s;
        if (s > nnDis[b]!) nnDis[b] = s;
      }
    }
  }
  const disMean = disSum / Math.max(1, disCount);

  // canon within-sample NN index per sample row (for recall@k)
  const pairIndex = (a: number, b: number): number => {
    // index of (a<b) in the packed upper-triangular order used above
    return a * k - (a * (a + 1)) / 2 + (b - a - 1);
  };
  const canonNnIdx = new Int32Array(k).fill(-1);
  const canonNnCos = new Float64Array(k).fill(-2);
  {
    for (let a = 0; a < k; a++) {
      for (let b = a + 1; b < k; b++) {
        const s = canonRdm[pairIndex(a, b)]!;
        if (s > canonNnCos[a]!) {
          canonNnCos[a] = s;
          canonNnIdx[a] = b;
        }
        if (s > canonNnCos[b]!) {
          canonNnCos[b] = s;
          canonNnIdx[b] = a;
        }
      }
    }
  }
  const TOP_COS = 0.05;
  const topIdx: number[] = [];
  for (let q = 0; q < pairCount; q++) if (canonRdm[q]! > TOP_COS) topIdx.push(q);

  // RDMs of the projected/native stores on the same sample pairs → Spearman
  const rdmSpearman: Record<string, number> = {};
  const rdmSpearmanTopPairs: Record<string, number> = {};
  const nnRecallAt1: Record<string, number> = {};
  const nnRecallAt10: Record<string, number> = {};
  const nnRecallAt1Strong: Record<string, number> = {};
  const nnRecallAt10Strong: Record<string, number> = {};
  let strongNnCount = 0;
  for (const { store, D } of stores) {
    const sub = new Float64Array(k * D);
    for (let a = 0; a < k; a++) {
      const r = rows[a]!;
      const f32 = loadRows(n, store, D, r, r + 1);
      let s = 0;
      for (let j = 0; j < D; j++) {
        sub[a * D + j] = f32[j]!;
        s += f32[j]! * f32[j]!;
      }
      const nm = Math.sqrt(s);
      for (let j = 0; j < D; j++) sub[a * D + j]! /= nm;
    }
    const rdm = new Float64Array(pairCount);
    let q = 0;
    for (let a = 0; a < k; a++) {
      for (let b = a + 1; b < k; b++, q++) {
        let s = 0;
        const ba = a * D;
        const bb = b * D;
        for (let x = 0; x < D; x++) s += sub[ba + x]! * sub[bb + x]!;
        rdm[q] = s;
      }
    }
    rdmSpearman[store] = spearman([...canonRdm], [...rdm]);
    rdmSpearmanTopPairs[store] =
      topIdx.length >= 2
        ? spearman(topIdx.map((q) => canonRdm[q]!), topIdx.map((q) => rdm[q]!))
        : NaN;
    // recall@1/@10: store-side top-10 within the sample vs canon NN
    let hit1 = 0;
    let hit10 = 0;
    let hit1s = 0;
    let hit10s = 0;
    let strong = 0;
    for (let a = 0; a < k; a++) {
      const target = canonNnIdx[a]!;
      if (target < 0) continue;
      const isStrong = canonNnCos[a]! > TOP_COS;
      if (isStrong) strong++;
      const scored: { b: number; s: number }[] = [];
      for (let b = 0; b < k; b++) {
        if (b === a) continue;
        const q = a < b ? pairIndex(a, b) : pairIndex(b, a);
        scored.push({ b, s: rdm[q]! });
      }
      scored.sort((x, y) => y.s - x.s);
      const h1 = scored[0]!.b === target;
      const h10 = scored.slice(0, 10).some((e) => e.b === target);
      if (h1) hit1++;
      if (h10) hit10++;
      if (isStrong && h1) hit1s++;
      if (isStrong && h10) hit10s++;
    }
    nnRecallAt1[store] = hit1 / k;
    nnRecallAt10[store] = hit10 / k;
    nnRecallAt1Strong[store] = strong > 0 ? hit1s / strong : NaN;
    nnRecallAt10Strong[store] = strong > 0 ? hit10s / strong : NaN;
    strongNnCount = strong;
    console.log(
      `  ${store}: RDM Spearman ${fmt(rdmSpearman[store]!)} (top-pairs>${TOP_COS}: ${fmt(rdmSpearmanTopPairs[store]!)}), ` +
        `recall@1 ${fmt(nnRecallAt1[store]!, 3)} (strong-NN: ${fmt(nnRecallAt1Strong[store]!, 3)} over ${strong}), recall@10 ${fmt(nnRecallAt10[store]!, 3)} (strong ${fmt(nnRecallAt10Strong[store]!, 3)})`,
    );
  }

  const res: SampleResult = {
    sampleSize: k,
    pairCount,
    canonNnAll: summarise([...nnAll]),
    canonNnDisjoint: summarise([...nnDis].filter((x) => x > -2)),
    canonDisjointSigma: Math.sqrt(Math.max(0, disSum2 / Math.max(1, disCount) - disMean * disMean)),
    canonDisjointMax: disMax,
    canonPredictedSigma: 1 / Math.sqrt(D0),
    canonPredictedCurveAtSample: CURVE(k, D0),
    canonPredictedCurveAt1e4: CURVE(1e4, D0),
    rdmSpearman,
    rdmSpearmanTopPairs,
    topPairCount: topIdx.length,
    nnRecallAt1,
    nnRecallAt10,
    nnRecallAt1Strong,
    nnRecallAt10Strong,
    strongNnCount,
    wallSeconds: (nowMs() - t0) / 1000,
  };
  writeJson(file, res);
  return res;
}

function structuralDuplicateCensus(ctx: Ctx): { groups: number; rowsInGroups: number; largestGroup: number; example: string[] } {
  const byHash = new Map<string, number[]>();
  ctx.tokenHash.forEach((h, i) => {
    const arr = byHash.get(h);
    if (arr) arr.push(i);
    else byHash.set(h, [i]);
  });
  const dupGroups = [...byHash.values()].filter((g) => g.length > 1);
  const largest = dupGroups.reduce((a, g) => Math.max(a, g.length), 0);
  const exampleGroup = dupGroups.sort((a, b) => b.length - a.length)[0] ?? [];
  return {
    groups: dupGroups.length,
    rowsInGroups: dupGroups.reduce((a, g) => a + g.length, 0),
    largestGroup: largest,
    example: exampleGroup.slice(0, 5).map((i) => `${ctx.concepts[i]!.id} (${ctx.concepts[i]!.annotations.lemmas[0] ?? '?'})`),
  };
}

function main(): void {
  const n = targetN();
  const t0 = nowMs();
  const ctx = buildCtx(n);
  const vec = readJson<Record<string, unknown>>(join(outDirFor(n), 'vec', 'manifest.json'));
  const ingest = readJson<Record<string, unknown>>(join(outDirFor(n), 'ingest-report.json'));
  const typing = readJson<Record<string, unknown>>(join(outDirFor(n), 'typing-report.json'));
  if (!vec || !ingest || !typing) throw new Error('ERR_METRICS_MISSING_STAGE: run ingest/typing/vectorise first');

  console.log('metrics: structural duplicate census...');
  const structDup = structuralDuplicateCensus(ctx);

  console.log('metrics: NN passes...');
  const nnProj512 = nnPass(ctx, 'proj512', 512, true);
  const nnProj576 = nnPass(ctx, 'proj576', 576, true);
  const nnNative512 = nnPass(ctx, 'native512', 512, false);
  const nnLex = nnPass(ctx, 'native512lex', 512, false);

  console.log('metrics: canon8192 sample + RDM Spearman...');
  const sample = sampleAnalysis(ctx, [
    { store: 'proj512', D: 512 },
    { store: 'proj576', D: 576 },
    { store: 'native512', D: 512 },
    { store: 'native576', D: 576 },
    { store: 'native512lex', D: 512 },
  ]);

  // ---- storage table (measured + derived) ----
  const stores = (vec.stores ?? {}) as Record<string, { D: number; bytesOnDisk: number; wallSeconds: number; usPerConceptEncode: number; atomsGenerated: number; fftCount: number }>;
  const storage = Object.fromEntries(
    Object.entries(stores).map(([s, t]) => [
      s,
      {
        D: t.D,
        fp32MeasuredMB: +(t.bytesOnDisk / 1e6).toFixed(2),
        fp64DerivedMB: +((t.bytesOnDisk * 2) / 1e6).toFixed(2),
        fp16DerivedMB: +(t.bytesOnDisk / 2 / 1e6).toFixed(2),
      },
    ]),
  );
  // §6.4 design row at D=8192 fp64 for 10k: 0.66 GB
  const canonFp64GB = (stores['canon8192']?.bytesOnDisk ?? 0) * 2 / 1e9;

  // ---- predicted vs measured margin table ----
  const marginTable = [nnProj512, nnProj576].map((r) => ({
    store: r.store,
    D: r.D,
    predicted_sigma_1_over_sqrtD: +r.predictedSigma.toFixed(4),
    measured_sigma_disjoint: +(r.disjointPairSigma ?? NaN).toFixed(4),
    predicted_maxSpurious_sqrt2lnm_over_D: +r.predictedCurveAtM.toFixed(4),
    measured_median_perConcept_maxDisjoint: +(r.nnDisjoint?.median ?? NaN).toFixed(4),
    measured_max_disjoint_pair: +(r.disjointPairMax ?? NaN).toFixed(4),
    measured_median_perConcept_maxANY: +r.nnAll.median.toFixed(4),
    measured_p95_perConcept_maxANY: +r.nnAll.p95.toFixed(4),
  }));
  const canonMargin = {
    store: 'canon8192 (1k deterministic sample)',
    D: 8192,
    predicted_sigma: +(1 / Math.sqrt(8192)).toFixed(5),
    measured_sigma_disjoint: +sample.canonDisjointSigma.toFixed(5),
    predicted_maxSpurious_at_sampleM: +sample.canonPredictedCurveAtSample.toFixed(4),
    predicted_maxSpurious_at_1e4_designQuote_0046: +sample.canonPredictedCurveAt1e4.toFixed(4),
    measured_median_perConcept_maxDisjoint: +sample.canonNnDisjoint.median.toFixed(4),
    measured_max_disjoint_pair: +sample.canonDisjointMax.toFixed(4),
    measured_median_perConcept_maxANY: +sample.canonNnAll.median.toFixed(4),
  };

  // ---- extrapolation reads (computed) ----
  const encodeSPerConcept = (stores['canon8192']?.wallSeconds ?? NaN) / n;
  const nnSeconds10k = nnProj512.wallSeconds;
  const extrapolation = {
    encodeCpuHours: {
      perConceptSecondsCanon8192_inclJL: +encodeSPerConcept.toFixed(4),
      at100k: +((encodeSPerConcept * 1e5) / 3600).toFixed(2),
      at1M: +((encodeSPerConcept * 1e6) / 3600).toFixed(1),
      designBandS1CpuHours: '200-2000 (all stages, not just vectorisation)',
      designBandS2CpuHours: '2k-20k',
    },
    exactNnCleanupWallHours_Onsquared: {
      at10k_measuredSeconds: +nnSeconds10k.toFixed(0),
      at100k_hours: +((nnSeconds10k * 100) / 3600).toFixed(1),
      at1M_hours: +((nnSeconds10k * 10000) / 3600).toFixed(0),
      note: 'O(m²) exact scan; this is the §6.5 decoder-cleanup/retrieval analogue — ANN + the ≥0.99 exact-vs-ANN recall gate becomes MANDATORY between 100k and 1M',
    },
    storageGB_fp16_dense8192: { at10k: +(canonFp64GB / 4).toFixed(3), at100k: +((canonFp64GB / 4) * 10).toFixed(2), at1M: +((canonFp64GB / 4) * 100).toFixed(1), design6_4: '0.16 / 1.64 / 16.38' },
  };

  const report = {
    title: 'SCALE-1 S0 first rung — measured metrics at n=' + n,
    date: new Date().toISOString(),
    epistemicStatus: [
      'MEASURED: every number in the tables below is a direct local measurement of this pipeline.',
      'STIPULATED: subset selection rule, lexFile→UFO crosswalk, anchor lists, kot-enc-import/0-poc construction and its weights.',
      'EXTRAPOLATION: all 100k/1M projections; to be measured, never a premise.',
      'NO FEASIBILITY CONCLUSION: S0 qualifies machinery only (design §8, §14). Correctness/efficiency remain INCONCLUSIVE-PENDING.',
      'NOT construction B: these vectors are NOT kot-enc-B/1 outputs; nothing here touches the pinned encoder or its goldens.',
    ],
    ingestSummary: ingest,
    typingSplit: {
      importedVsInferred: (typing as { importedVsInferredSplit?: unknown }).importedVsInferredSplit,
      onticOutcomes: (typing as { onticCategoryOutcomes?: unknown }).onticCategoryOutcomes,
      sortalityOutcomes: (typing as { sortalityOutcomes?: unknown }).sortalityOutcomes,
    },
    encodeCost: Object.fromEntries(
      Object.entries(stores).map(([s, t]) => [
        s,
        { D: t.D, wallSeconds: t.wallSeconds, usPerConcept: Math.round(t.usPerConceptEncode), atoms: t.atomsGenerated, fftCount: t.fftCount },
      ]),
    ),
    storage,
    marginPredictedVsMeasured: {
      disjointClassDefinition:
        'pair with no direct axiom edge, no shared axiom target, and DIFFERENT lexFile — the class the §6.5 independent-vector Gaussian model actually describes; related/shared-token pairs are reported separately under max-ANY',
      projected: marginTable,
      canon8192Sample: canonMargin,
    },
    duplicates: {
      zeroAxiomRecords: ctx.zeroAxiomRows,
      structuralTokenMultisets: structDup,
      vectorPairsAboveCos: { proj512: nnProj512.pairsAbove, proj576: nnProj576.pairsAbove, native512: nnNative512.pairsAbove, native512lex: nnLex.pairsAbove },
      note: '§6.5 collision class 2: structurally indistinguishable AxiomsOnly records legitimately share a semantic block — the honest margin killer at this rung is DUPLICATE STRUCTURE, not Gaussian crosstalk.',
    },
    lexicalBlockEffect: {
      native512_nnMedian: +nnNative512.nnAll.median.toFixed(4),
      native512lex_nnMedian: +nnLex.nnAll.median.toFixed(4),
      native512_pairsAbove999: nnNative512.pairsAbove['>0.999'],
      native512lex_pairsAbove999: nnLex.pairsAbove['>0.999'],
      note: 'optional §6.2 lexical block (lemma tokens, w=0.5) as a duplicate-splitting probe; lemmas are OUTSIDE record identity, so this is a deployment-profile experiment, not a record-identity change',
    },
    rdmSpearmanVsCanon8192: sample.rdmSpearman,
    x4Calibration: {
      designCitedAtKernelV0_54concepts: { proj512: 0.9718, proj576: 0.9706 },
      remeasuredHere_globalRdm: sample.rdmSpearman,
      remeasuredHere_topPairsOnly: sample.rdmSpearmanTopPairs,
      topPairCount: sample.topPairCount,
      nnRecallAt1: sample.nnRecallAt1,
      nnRecallAt10: sample.nnRecallAt10,
      nnRecallAt1StrongNN: sample.nnRecallAt1Strong,
      nnRecallAt10StrongNN: sample.nnRecallAt10Strong,
      strongNnCount: sample.strongNnCount,
      sampleSize: sample.sampleSize,
      readNote:
        'global RDM Spearman on a bulk-import store is dominated by the near-zero disjoint-pair noise floor (σ≈1/√8192≈0.011), which any D-reduction re-randomises — the kernel-v0 0.97 calibration does NOT transfer to bulk-import RDMs at this scale. Structure-bearing pairs (canon cos>0.05) and NN retrieval preservation are the operationally relevant fidelity numbers.',
    },
    nnDetails: { proj512: nnProj512, proj576: nnProj576, native512: nnNative512, native512lex: nnLex, canonSample: sample },
    extrapolation,
    wallSecondsMetricsStage: +((nowMs() - t0) / 1000).toFixed(1),
  };

  const base = `scale-s0-n${n}-report`;
  ensureDir(RESULTS_DIR);
  writeJson(join(RESULTS_DIR, `${base}.json`), report);
  writeFileSync(join(RESULTS_DIR, `${base}.md`), renderMd(report));
  console.log(`metrics done → ${join(RESULTS_DIR, base)}.{json,md}`);
}

function renderMd(r: Record<string, any>): string {
  const m = r.marginPredictedVsMeasured;
  const lines: string[] = [
    `# ${r.title}`,
    '',
    `date: ${r.date}`,
    '',
    '## Epistemic status',
    ...r.epistemicStatus.map((s: string) => `- ${s}`),
    '',
    '## Ingest',
    `- rule: ${r.ingestSummary.selectionRule}`,
    `- selected n=${r.ingestSummary.n} of ${r.ingestSummary.totalSynsets} synsets; boundary tag_cnt=${r.ingestSummary.boundaryTagCnt}; pos mix ${JSON.stringify(r.ingestSummary.posMix)}`,
    `- axioms: ${r.ingestSummary.axiomTotal} (${r.ingestSummary.axiomsPerConceptMean.toFixed(2)}/concept)`,
    '',
    '## UFO typing — imported vs inferred split',
    '',
    '| field | source-asserted | rule-inferred | soft-candidate | underdetermined |',
    '|---|---|---|---|---|',
    ...Object.entries(r.typingSplit.importedVsInferred as Record<string, Record<string, string>>).map(
      ([f, s]) => `| ${f} | ${s['source-asserted']} | ${s['rule-inferred']} | ${s['soft-candidate']} | ${s['underdetermined']} |`,
    ),
    '',
    '## Encode cost (measured)',
    '',
    '| store | D | wall s | µs/concept | atoms | FFTs |',
    '|---|---|---|---|---|---|',
    ...Object.entries(r.encodeCost as Record<string, any>).map(
      ([s, t]) => `| ${s} | ${t.D} | ${t.wallSeconds.toFixed(1)} | ${t.usPerConcept} | ${t.atoms} | ${t.fftCount} |`,
    ),
    '',
    '## Storage (measured fp32 on disk; fp64/fp16 derived)',
    '',
    '| store | D | fp32 MB | fp64 MB | fp16 MB |',
    '|---|---|---|---|---|',
    ...Object.entries(r.storage as Record<string, any>).map(
      ([s, t]) => `| ${s} | ${t.D} | ${t.fp32MeasuredMB} | ${t.fp64DerivedMB} | ${t.fp16DerivedMB} |`,
    ),
    '',
    '## Collision / margin — predicted (§6.5 √(2·ln m/D)) vs measured',
    '',
    '| store | D | pred σ | meas σ (disjoint) | pred max-spurious | meas median per-concept max-DISJOINT | meas max disjoint pair | meas median per-concept max-ANY | meas p95 max-ANY |',
    '|---|---|---|---|---|---|---|---|---|',
    ...m.projected.map(
      (t: any) =>
        `| ${t.store} | ${t.D} | ${t.predicted_sigma_1_over_sqrtD} | ${t.measured_sigma_disjoint} | ${t.predicted_maxSpurious_sqrt2lnm_over_D} | ${t.measured_median_perConcept_maxDisjoint} | ${t.measured_max_disjoint_pair} | ${t.measured_median_perConcept_maxANY} | ${t.measured_p95_perConcept_maxANY} |`,
    ),
    '',
    `canon8192 (1k sample): pred σ ${m.canon8192Sample.predicted_sigma}, meas σ ${m.canon8192Sample.measured_sigma_disjoint}; pred max-spurious @sample ${m.canon8192Sample.predicted_maxSpurious_at_sampleM} (design quotes ≈0.046 @m=10⁴ → formula gives ${m.canon8192Sample.predicted_maxSpurious_at_1e4_designQuote_0046}); meas median per-concept max-disjoint ${m.canon8192Sample.measured_median_perConcept_maxDisjoint}; meas max disjoint pair ${m.canon8192Sample.measured_max_disjoint_pair}; meas median max-ANY ${m.canon8192Sample.measured_median_perConcept_maxANY}.`,
    '',
    '## Duplicate census (§6.5 collision class 2)',
    `- structural duplicate groups (identical token multisets): ${r.duplicates.structuralTokenMultisets.groups} groups covering ${r.duplicates.structuralTokenMultisets.rowsInGroups} records; largest group ${r.duplicates.structuralTokenMultisets.largestGroup} (e.g. ${r.duplicates.structuralTokenMultisets.example.join('; ')})`,
    `- vector pairs above cosine thresholds: proj512 ${JSON.stringify(r.duplicates.vectorPairsAboveCos.proj512)}; native512lex ${JSON.stringify(r.duplicates.vectorPairsAboveCos.native512lex)}`,
    `- ${r.duplicates.note}`,
    '',
    '## X4 RDM-Spearman re-measure (design cites 0.9718 / 0.9706 at 54 concepts)',
    '',
    '| store | global RDM Spearman | top-pairs (cos>0.05) Spearman | NN recall@1 (all / strong-NN) | NN recall@10 (all / strong-NN) |',
    '|---|---|---|---|---|',
    ...Object.entries(r.rdmSpearmanVsCanon8192 as Record<string, number>).map(
      ([s, v]) =>
        `| ${s} | ${fmt(v)} | ${fmt(r.x4Calibration.remeasuredHere_topPairsOnly[s])} | ${fmt(r.x4Calibration.nnRecallAt1[s], 3)} / ${fmt(r.x4Calibration.nnRecallAt1StrongNN[s], 3)} | ${fmt(r.x4Calibration.nnRecallAt10[s], 3)} / ${fmt(r.x4Calibration.nnRecallAt10StrongNN[s], 3)} |`,
    ),
    '',
    `top-pair count: ${r.x4Calibration.topPairCount} of ${r.nnDetails.canonSample.pairCount} sample pairs. ${r.x4Calibration.readNote}`,
    '',
    '## Extrapolation (EXTRAPOLATION tags; to be measured, never premises)',
    '```json',
    JSON.stringify(r.extrapolation, null, 2),
    '```',
  ];
  return lines.join('\n');
}

main();
