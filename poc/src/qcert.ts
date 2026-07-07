/**
 * QCERT — offline coherence certification of the quasi-orthogonal toy-native
 * codebook (kot-enc-Bq/1, bead kernel-of-truth-5xo; codebookQ.ts documents
 * the construction decision).
 *
 * Pre-registered deliverable: max AND distribution of pairwise |cos| at each
 * toy-native D ∈ {512, 576} over
 *   (a) ALL constructible bound-pair atoms (31 slots x 129 fillers = 3,999 —
 *       the full analogue of the 13-bit Hadamard row space), and
 *   (b) the REALISED bound-pair codes actually used when encoding the
 *       authored kernel-v0 corpus (fresh QuasiCodebook instance, its atom
 *       cache after exactly one corpus encode = the realised set),
 * compared against the DCV §7 coherence scales: the quasi-orthogonal
 * mu ≈ sqrt(ln m / D) typical-pair scale (§7.2), the random-codebook
 * expected maximum ≈ sqrt(2 ln P)/sqrt(D) over P pairs, and the Welch lower
 * bound sqrt((m-D)/(D(m-1))) that NO m-vector codebook can beat. Reference
 * point stated for contrast: the exact D=8192 Hadamard codebook has measured
 * pairwise |cos| < 1e-12 (encoder/test/codebook.test.ts) — the variant's
 * crosstalk floor is nonzero BY CONSTRUCTION and this report quantifies it.
 *
 * Writes results/qcert-report.{json,md}. Touches nothing of the live
 * synthetic X1 run (new outputs only).
 */

import {
  QuasiCodebook,
  allAtomPairs,
  encodeConceptSetWith,
  resolveParamsQ,
  encoderContentHashQ,
  encoderContentHash,
  ALGORITHM_VERSION_Q,
} from '@jeswr/kernel-encoder';
import { fmt, percentile } from '../harness/common.js';
import { loadCorpus, writeCorpusReport, type Corpus } from './corpus-common.js';

const DIMS = [512, 576] as const;

function dot(a: Float64Array, b: Float64Array): number {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i]! * b[i]!;
  return s;
}

interface CoherenceStats {
  atoms: number;
  pairs: number;
  maxAbsCos: number;
  maxPair: { a: string; b: string };
  /** percentiles of |cos| over all pairs */
  p50: number;
  p90: number;
  p99: number;
  p999: number;
  mean: number;
  /** count above the 5-sigma matched-filter design floor 5/sqrt(D) */
  above5Sigma: number;
}

/** Pairwise |cos| stats over a named atom set (exact percentiles via typed-array sort). */
function coherence(names: string[], vecs: Float64Array[], D: number): CoherenceStats {
  const m = vecs.length;
  const nPairs = (m * (m - 1)) / 2;
  const abs = new Float64Array(nPairs);
  let k = 0;
  let maxV = -1;
  let maxI = 0;
  let maxJ = 1;
  let sum = 0;
  let above = 0;
  const fiveSigma = 5 / Math.sqrt(D);
  for (let i = 0; i < m; i++) {
    const vi = vecs[i]!;
    for (let j = i + 1; j < m; j++) {
      const c = Math.abs(dot(vi, vecs[j]!));
      abs[k++] = c;
      sum += c;
      if (c > maxV) {
        maxV = c;
        maxI = i;
        maxJ = j;
      }
      if (c >= fiveSigma) above++;
    }
  }
  abs.sort();
  const sorted = abs as unknown as readonly number[];
  return {
    atoms: m,
    pairs: nPairs,
    maxAbsCos: maxV,
    maxPair: { a: names[maxI]!, b: names[maxJ]! },
    p50: percentile(sorted, 0.5),
    p90: percentile(sorted, 0.9),
    p99: percentile(sorted, 0.99),
    p999: percentile(sorted, 0.999),
    mean: sum / nPairs,
    above5Sigma: above,
  };
}

function bounds(m: number, D: number): Record<string, number> {
  const pairs = (m * (m - 1)) / 2;
  return {
    // Vacuous (0) when m <= D: that many vectors fit exactly orthogonally in
    // principle — just not via a label-deterministic construction over the
    // FULL atom space, which is what the variant pins.
    welchLowerBound: m <= D ? 0 : Math.sqrt((m - D) / (D * (m - 1))),
    dcvTypicalPairScale: Math.sqrt(Math.log(m) / D), // DCV §7.2 mu ≈ sqrt(ln m / D)
    randomExpectedMax: Math.sqrt((2 * Math.log(pairs)) / D), // E[max of P ~N(0,1/D)]
    fiveSigmaDesignFloor: 5 / Math.sqrt(D),
  };
}

function realisedAtoms(corpus: Corpus, D: number): { names: string[]; vecs: Float64Array[] } {
  // Fresh instance => atom cache after one corpus encode IS the realised set.
  const cb = new QuasiCodebook(D);
  encodeConceptSetWith(corpus.defs, resolveParamsQ({ D }), cb);
  const used = cb.usedAtoms().sort((x, y) => `${x.slot}|${x.filler}`.localeCompare(`${y.slot}|${y.filler}`));
  return {
    names: used.map((u) => `${u.slot}|${u.filler}`),
    vecs: used.map((u) => cb.boundAtom(u.slot, u.filler)),
  };
}

function main(): void {
  const corpus = loadCorpus();
  const t0 = Date.now();
  const perDim: Record<string, unknown> = {};
  const mdRows: string[] = [];

  for (const D of DIMS) {
    console.log(`qcert: D=${D} — full atom space`);
    const pairsAll = allAtomPairs();
    const cbFull = new QuasiCodebook(D);
    const namesAll = pairsAll.map((p) => `${p.slot}|${p.filler}`);
    const vecsAll = pairsAll.map((p) => cbFull.boundAtom(p.slot, p.filler));
    const full = coherence(namesAll, vecsAll, D);
    console.log(
      `  full space: ${full.atoms} atoms, max |cos| ${fmt(full.maxAbsCos)} (${((Date.now() - t0) / 1000).toFixed(0)}s)`,
    );

    console.log(`qcert: D=${D} — corpus-realised atoms`);
    const real = realisedAtoms(corpus, D);
    const realised = coherence(real.names, real.vecs, D);
    console.log(`  realised: ${realised.atoms} atoms, max |cos| ${fmt(realised.maxAbsCos)}`);

    perDim[String(D)] = {
      encoderContentHashQ: encoderContentHashQ({ D }),
      fullSpace: { ...full, bounds: bounds(full.atoms, D) },
      corpusRealised: { ...realised, bounds: bounds(realised.atoms, D) },
    };
    for (const [label, s] of [
      ['full space', full],
      ['corpus-realised', realised],
    ] as const) {
      const b = bounds(s.atoms, D);
      mdRows.push(
        `| ${D} | ${label} | ${s.atoms} | ${s.pairs} | **${fmt(s.maxAbsCos)}** | ${fmt(s.p50)} | ${fmt(s.p99)} | ${fmt(
          s.p999,
        )} | ${fmt(b.welchLowerBound!)} | ${fmt(b.dcvTypicalPairScale!)} | ${fmt(b.randomExpectedMax!)} | ${s.above5Sigma} |`,
      );
    }
  }

  const json = {
    date: new Date().toISOString(),
    suite: 'QCERT: offline coherence certification of the quasi-orthogonal toy-native codebook',
    algorithmVersion: ALGORITHM_VERSION_Q,
    baseEncoderContentHash: encoderContentHash(),
    corpusManifestSha256: corpus.manifestSha256,
    corpusContentHash: corpus.corpusContentHash,
    construction:
      'independent Rademacher(+/-1/sqrt(D)) atoms per (slot,filler), signs from SHA-256 stream label qatom/<D>/<slotId>/<fillerId> (codebookQ.ts; alternatives considered there)',
    exactReference:
      'D=8192 Hadamard codebook pairwise |cos| < 1e-12 measured (encoder/test/codebook.test.ts) — exact orthogonality is unavailable below 2^13 and the variant floor is nonzero by construction',
    perDim,
  };
  const md = [
    '# QCERT — quasi-orthogonal codebook coherence certification (kot-enc-Bq/1)',
    '',
    `date: ${json.date}`,
    `algorithm: ${ALGORITHM_VERSION_Q}; construction: ${json.construction}`,
    `corpus: kernel-v0, content-hash \`${corpus.corpusContentHash}\``,
    ...DIMS.map(
      (D) =>
        `encoder content-hash @ D=${D}: \`${(perDim[String(D)] as { encoderContentHashQ: string }).encoderContentHashQ}\``,
    ),
    '',
    '## Pairwise |cos| (coherence) — measured vs reference scales',
    '',
    '| D | atom set | atoms | pairs | max | p50 | p99 | p99.9 | Welch LB | sqrt(ln m/D) | E[max] random | pairs >= 5/sqrt(D) |',
    '|---|---|---|---|---|---|---|---|---|---|---|---|',
    ...mdRows,
    '',
    '- **Welch LB**: no m-vector codebook in R^D can have max coherence below this; the gap to it is the price of a label-deterministic random construction.',
    '- **sqrt(ln m/D)**: DCV §7.2 typical-pair quasi-orthogonal scale.',
    '- **E[max] random**: expected maximum of P ~ N(0, 1/D) pairs — the concentration target; measured max should sit near it (certifies no pathological pair).',
    '- **pairs >= 5/sqrt(D)**: pairs at/above the decoder matched-filter 5-sigma design floor — each such pair is a potential cleanup confusion; the exact D=8192 codebook has zero.',
    '',
    `> ${json.exactReference}`,
    '',
    '> Realised set = atom cache of a fresh QuasiCodebook after encoding the',
    '> 54-concept corpus (encodeConceptSetWith). Single-edit mutants stay within',
    '> the same closed atom inventory except for fillers absent from the corpus;',
    '> the FULL-space row above covers every atom any capped explication can use.',
  ].join('\n');
  writeCorpusReport('qcert-report', json, md);
  console.log(`qcert done in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}

main();
