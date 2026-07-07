/**
 * E5 vector tables at d = 576 via the PROJECTED path (README O1;
 * docs/poc-design.md Common rules 2-4, rule 3 path ii; bead
 * kernel-of-truth-c24).
 *
 * Encodes the 524-concept E5 set (inputs/e5-concepts.json) with kot-enc-B/1
 * at D=8192, VERIFYING the encoder content hash against the pre-registered
 * pin (fail closed), pushes every vector through the fixed X4 JL matrix
 * 8192->576 (jlProject copied VERBATIM from poc/harness/x4.ts — the exact
 * construction X4 measured distortion on), L2-normalises the projected rows
 * (README O1 operationalisation; pre-normalisation norms recorded), and
 * emits:
 *
 *   inputs/vectors/kernel-jl576.f32          — 524 x 576 float32 rows
 *   inputs/vectors/random-jl576-seed<s>.f32  — s in 0..4: unit-norm i.i.d.
 *                                              Gaussian rows (descriptive
 *                                              random-vector arm)
 *   inputs/vector-tables-manifest.json       — ids, pins, per-file sha-256,
 *                                              shuffled-control DERANGEMENTS
 *                                              per seed (Common rule 4).
 */

import {
  DEFAULT_PARAMS,
  encodeConceptSet,
  encoderContentHash,
} from '@jeswr/kernel-encoder';
import type { Explication } from '@jeswr/kernel-encoder';
import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import type { E5Concepts } from './selectConcepts.js';
import {
  D_FULL,
  D_MODEL,
  INPUTS_DIR,
  N_SEEDS,
  PINNED_B8192_HASH,
  isMain,
  jlProject,
  loadE4Synthetics,
  loadKernelV0,
  readInput,
  seededDerangement,
  seededGaussianRows,
  writeF32,
  writeInput,
} from './common.js';

function main(): void {
  // ---- encoder pin verification (Common rule 2) — FAIL CLOSED on mismatch --
  const hash = encoderContentHash();
  if (hash !== PINNED_B8192_HASH) {
    throw new Error(
      `ERR_ENCODER_PIN: kot-enc-B/1 content-hash ${hash} != pinned ${PINNED_B8192_HASH} ` +
        '(docs/poc-design.md Common rule 2) — any E-run against a different encoder hash is a NEW pre-registration',
    );
  }
  if (DEFAULT_PARAMS.D !== D_FULL) {
    throw new Error(`ERR_DIMENSION: DEFAULT_PARAMS.D=${DEFAULT_PARAMS.D} != ${D_FULL}`);
  }

  const concepts = readInput<E5Concepts>('e5-concepts.json');
  if (concepts.artifact !== 'e5-concepts') throw new Error('ERR_ARTIFACT: e5-concepts.json');

  const authored = loadKernelV0();
  const { records: synth, fileSha256 } = loadE4Synthetics();
  if (fileSha256 !== concepts.e4SyntheticsSha256) {
    throw new Error('ERR_SYNTH_PIN: e4 synthetic-concepts.json sha changed since selection');
  }
  const defs = new Map<string, Explication>();
  for (const r of authored) defs.set(r.id, r.explication as Explication);
  for (const r of synth) if (concepts.ids.includes(r.id)) defs.set(r.id, r.explication);

  console.log(`encoding ${defs.size} explications at D=${D_FULL} (kot-enc-B/1, reference DAG)`);
  const { vectors } = encodeConceptSet(defs);

  const fullD: Float64Array[] = concepts.ids.map((id) => {
    const v = vectors.get(id);
    if (v === undefined) throw new Error(`ERR_VECTOR: no vector for ${id}`);
    return v;
  });

  console.log(`JL-projecting ${fullD.length} vectors ${D_FULL} -> ${D_MODEL} (Achlioptas signs, stream jl/${D_FULL}/${D_MODEL})`);
  const proj = jlProject(fullD, D_FULL, D_MODEL);

  // ---- unit-normalise post-projection (README O1, flagged), record norms ---
  const preNorms = proj.map((v) => Math.sqrt(v.reduce((a, x) => a + x * x, 0)));
  const kernel = new Float32Array(concepts.ids.length * D_MODEL);
  proj.forEach((v, r) => {
    const n = preNorms[r]!;
    if (!(n > 0)) throw new Error(`ERR_NORM: zero-norm projection for row ${r}`);
    for (let c = 0; c < D_MODEL; c++) kernel[r * D_MODEL + c] = Math.fround(v[c]! / n);
  });

  const vecDir = join(INPUTS_DIR, 'vectors');
  mkdirSync(vecDir, { recursive: true });
  const kernelSha = writeF32(join(vecDir, `kernel-jl${D_MODEL}.f32`), kernel);

  // ---- shuffled-kernel derangements (Common rule 4; E4 construction) -------
  const shuffled: { seed: number; label: string; redraws: number; perm: number[] }[] = [];
  for (let s = 0; s < N_SEEDS; s++) {
    const { perm, label, redraws } = seededDerangement(`e5/shuffle/${s}`, concepts.ids.length);
    shuffled.push({ seed: s, label, redraws, perm });
  }

  // ---- random-vector tables (descriptive arm): unit-norm Gaussian rows -----
  const randomFiles: { seed: number; label: string; file: string; sha256: string }[] = [];
  for (let s = 0; s < N_SEEDS; s++) {
    const label = `e5/random/${s}`;
    const raw = seededGaussianRows(label, concepts.ids.length, D_MODEL, 1.0);
    for (let r = 0; r < concepts.ids.length; r++) {
      let sq = 0;
      for (let c = 0; c < D_MODEL; c++) sq += raw[r * D_MODEL + c]! ** 2;
      const n = Math.sqrt(sq);
      for (let c = 0; c < D_MODEL; c++) {
        raw[r * D_MODEL + c] = Math.fround(raw[r * D_MODEL + c]! / n);
      }
    }
    const file = `vectors/random-jl${D_MODEL}-seed${s}.f32`;
    const sha256 = writeF32(join(INPUTS_DIR, file), raw);
    randomFiles.push({ seed: s, label, file, sha256 });
  }

  const preNormArr = preNorms.map((n) => Number(n.toFixed(6)));
  writeInput('vector-tables-manifest.json', {
    artifact: 'e5-vector-tables',
    date: new Date().toISOString(),
    DFull: D_FULL,
    d: D_MODEL,
    rows: concepts.ids.length,
    algorithmVersion: 'kot-enc-B/1',
    encoderContentHash: hash,
    pinnedHash: PINNED_B8192_HASH,
    kernelV0: concepts.kernelV0,
    e4SyntheticsSha256: fileSha256,
    jlDerivation:
      'Achlioptas sign matrix, entries ±1/sqrt(d), signs from SHA-256 stream label jl/<D>/<d> ' +
      '(encoder det.ts DET_DOMAIN); verbatim copy of poc/harness/x4.ts jlProject — the projection ' +
      'X4 measured distortion on (Common rule 3: E-series claims inherit the R^d numbers: ' +
      'RDM Spearman 0.9608 synthetics / 0.9706 kernel-v0 at d=576)',
    layout:
      'row-major float32 little-endian (numpy dtype <f4), one row per concept, row order = ' +
      'e5-concepts.json ids (seen authored alphabetical, seen synthetic by index, nonce by index)',
    ids: concepts.ids,
    roles: concepts.roles,
    kernel: {
      file: `vectors/kernel-jl${D_MODEL}.f32`,
      sha256: kernelSha,
      note: 'rows unit-norm AFTER JL projection (README O1 operationalisation)',
      preProjectionNormPolicy: 'full-D kot-enc-B/1 output used as-is',
      postProjectionPreNormalisation: {
        min: Math.min(...preNormArr),
        max: Math.max(...preNormArr),
        mean: Number((preNormArr.reduce((a, b) => a + b, 0) / preNormArr.length).toFixed(6)),
      },
    },
    shuffled: shuffled.map((s) => ({
      ...s,
      note: 'row i of the shuffled table = kernel[perm[i]]; derangement (no fixed points) enforced; spans ALL 524 rows (README O4)',
    })),
    randomFrozen: randomFiles.map((r) => ({
      ...r,
      note: 'unit-norm i.i.d. Gaussian rows — DESCRIPTIVE arm only (README O4)',
    })),
    scalePolicy:
      'all tables are unit-norm rows consumed as ADAPTER INPUTS (not embedding rows); no load-time rescale',
  });
}

if (isMain(import.meta.url)) main();
