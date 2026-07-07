/**
 * E4 vector tables at d_model = 512 (docs/poc-design.md E4 + Common rules
 * 2-4, toy-native path (i); bead kernel-of-truth-73u).
 *
 * Encodes the FULL 1054-concept vocabulary (54 authored kernel-v0 + 1000
 * synthetic from inputs/synthetic-concepts.json) with kot-enc-Bq/1 at D=512,
 * VERIFYING the encoder content hash against the pre-registered pin (fail
 * closed), and emits:
 *
 *   inputs/vectors/kernel-d512.f32          — 1054 x 512 float32 rows
 *                                             (little-endian, row-major,
 *                                             unit-norm), row order = the ids
 *                                             list in the manifest.
 *   inputs/vectors/random-d512-seed<s>.f32  — s in 0..4: i.i.d. N(0, 0.02^2)
 *                                             rows (norm-matched to the
 *                                             trainable-arm init, Common
 *                                             rule 4), Box-Muller over
 *                                             DetStream — bit-reproducible.
 *   inputs/vector-tables-manifest.json      — ids, pins, per-file sha-256,
 *                                             shuffled-control DERANGEMENTS
 *                                             (BLOCKER 2 control) per seed,
 *                                             scale policy.
 *
 * Float32 binaries (not JSON) because 6 tables x 1054 x 512 floats would be
 * a ~65 MB JSON artifact; the .f32 files are ~2.2 MB each and their sha-256
 * is pinned in the manifest, which is what the tests and the GPU runner
 * verify. Row values are Math.fround()ed before writing, so JSON/binary
 * round-trips agree bit-exactly with numpy float32 loads.
 *
 * SCALE POLICY (identical to poc/e1, applied by the E4 runner at load time):
 * kernel/shuffled rows are unit-norm here and multiplied by
 * frozenScale = INIT_STD * sqrt(D) at load; random rows are stored at their
 * natural N(0, INIT_STD^2) draw. The primary E4 contrast (kernel vs
 * shuffled) is norm-identical under any choice.
 */

import {
  DetStream,
  QUASI_DIMS,
  encodeConceptSetQ,
  encoderContentHashQ,
} from '@jeswr/kernel-encoder';
import type { Explication } from '@jeswr/kernel-encoder';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import {
  E4_D_MODEL,
  INIT_STD,
  INPUTS_DIR,
  N_SEEDS,
  PINNED_BQ512_HASH,
  corpusPin,
  isMain,
  loadKernelV0,
  readInput,
  sha256Hex,
  slugOf,
  writeInput,
} from './common.js';
import type { SynthRecord } from './synthVocab.js';

/** Seeded derangement of [0,n) — same construction as poc/e1 (Fisher-Yates + labelled redraws). */
export function seededDerangement(
  baseLabel: string,
  n: number,
): { perm: number[]; label: string; redraws: number } {
  for (let attempt = 0; ; attempt++) {
    const label = attempt === 0 ? baseLabel : `${baseLabel}/retry${attempt}`;
    const stream = new DetStream(`perm/${label}`);
    const p = Array.from({ length: n }, (_, i) => i);
    for (let i = n - 1; i > 0; i--) {
      const j = stream.nextBelow(i + 1);
      const t = p[i]!;
      p[i] = p[j]!;
      p[j] = t;
    }
    if (p.every((v, i) => v !== i)) return { perm: p, label, redraws: attempt };
  }
}

/** Deterministic N(0, std^2) rows via Box-Muller over DetStream (poc/e1 construction). */
export function seededGaussianRows(
  label: string,
  rows: number,
  cols: number,
  std: number,
): Float32Array {
  const stream = new DetStream(label);
  const out = new Float32Array(rows * cols);
  let spare: number | null = null;
  const next = (): number => {
    if (spare !== null) {
      const v = spare;
      spare = null;
      return v;
    }
    const u1 = 1 - stream.nextFloat();
    const u2 = stream.nextFloat();
    const r = Math.sqrt(-2 * Math.log(u1));
    spare = r * Math.sin(2 * Math.PI * u2);
    return r * Math.cos(2 * Math.PI * u2);
  };
  for (let i = 0; i < out.length; i++) out[i] = Math.fround(next() * std);
  return out;
}

function writeF32(path: string, data: Float32Array): string {
  // Explicit little-endian byte layout (x86/ARM LE both write LE here, but be
  // deliberate: the manifest promises LE and numpy reads '<f4').
  const buf = Buffer.alloc(data.length * 4);
  for (let i = 0; i < data.length; i++) buf.writeFloatLE(data[i]!, i * 4);
  writeFileSync(path, buf);
  console.log(`wrote ${path} (${buf.length} bytes)`);
  return sha256Hex(buf);
}

function main(): void {
  const D = E4_D_MODEL;
  if (!(QUASI_DIMS as readonly number[]).includes(D)) {
    throw new Error(`ERR_DIMENSION: E4 d_model=${D} is not a pre-registered toy-native dimension`);
  }

  // ---- encoder pin verification (Common rule 2) — FAIL CLOSED on mismatch --
  const hash = encoderContentHashQ({ D });
  if (hash !== PINNED_BQ512_HASH) {
    throw new Error(
      `ERR_ENCODER_PIN: kot-enc-Bq/1@${D} content-hash ${hash} != pinned ${PINNED_BQ512_HASH} ` +
        '(docs/poc-design.md Common rule 2) — any E-run against a different encoder hash is a NEW pre-registration',
    );
  }

  // ---- assemble the 1054-concept vocabulary -------------------------------
  const authored = loadKernelV0(); // alphabetical by slug
  const synth = readInput<{ artifact: string; records: SynthRecord[] }>('synthetic-concepts.json');
  if (synth.artifact !== 'e4-synthetic-concepts') throw new Error('ERR_ARTIFACT: synthetic-concepts.json');
  const defs = new Map<string, Explication>();
  for (const rec of authored) defs.set(rec.id, rec.explication as Explication);
  for (const rec of synth.records) defs.set(rec.id, rec.explication);
  // Order: authored (alphabetical) first, then synthetic in index order —
  // matches the candidate-token layout the emission builder produces.
  const ids = [...authored.map((r) => r.id), ...synth.records.map((r) => r.id)];
  if (new Set(ids).size !== ids.length) throw new Error('ERR_IDS: duplicate concept ids');
  console.log(`encoding ${ids.length} concepts at D=${D} (kot-enc-Bq/1, encodeConceptSetQ)`);
  const { vectors } = encodeConceptSetQ(defs, { params: { D } });

  const kernel = new Float32Array(ids.length * D);
  ids.forEach((id, r) => {
    const v = vectors.get(id);
    if (v === undefined) throw new Error(`ERR_VECTOR: no vector for ${id}`);
    const n = Math.sqrt(v.reduce((a, x) => a + x * x, 0));
    if (Math.abs(n - 1) > 1e-9) throw new Error(`ERR_NORM: ${id} has norm ${n}, expected unit`);
    for (let c = 0; c < D; c++) kernel[r * D + c] = Math.fround(v[c]!);
  });

  const vecDir = join(INPUTS_DIR, 'vectors');
  mkdirSync(vecDir, { recursive: true });
  const kernelSha = writeF32(join(vecDir, 'kernel-d512.f32'), kernel);

  // ---- controls ------------------------------------------------------------
  const shuffled: { seed: number; label: string; redraws: number; perm: number[] }[] = [];
  for (let s = 0; s < N_SEEDS; s++) {
    const { perm, label, redraws } = seededDerangement(`e4/shuffle/${s}`, ids.length);
    shuffled.push({ seed: s, label, redraws, perm });
  }
  const randomFiles: { seed: number; label: string; file: string; sha256: string }[] = [];
  for (let s = 0; s < N_SEEDS; s++) {
    const label = `e4/randfrozen/${s}`;
    const rows = seededGaussianRows(label, ids.length, D, INIT_STD);
    const file = `vectors/random-d512-seed${s}.f32`;
    const sha256 = writeF32(join(INPUTS_DIR, file), rows);
    randomFiles.push({ seed: s, label, file, sha256 });
  }

  const frozenScale = INIT_STD * Math.sqrt(D);
  writeInput('vector-tables-manifest.json', {
    artifact: 'e4-vector-tables',
    date: new Date().toISOString(),
    D,
    rows: ids.length,
    algorithmVersion: 'kot-enc-Bq/1',
    encoderContentHashQ: hash,
    pinnedHash: PINNED_BQ512_HASH,
    kernelV0: corpusPin(),
    syntheticConcepts: { count: synth.records.length },
    layout:
      'row-major float32 little-endian (numpy dtype <f4), one row per concept, ' +
      'row order = the `ids` list below (authored alphabetical, then synthetic by index)',
    ids,
    slugs: ids.map(slugOf),
    kernel: { file: 'vectors/kernel-d512.f32', sha256: kernelSha, note: 'unit-norm rows' },
    shuffled: shuffled.map((s) => ({
      ...s,
      note: 'row i of the shuffled table = kernel[perm[i]]; derangement (no fixed points) enforced',
    })),
    randomFrozen: randomFiles,
    initStd: INIT_STD,
    frozenScale,
    scalePolicy:
      `kernel/shuffled rows are unit-norm here and are multiplied by frozenScale = ` +
      `initStd*sqrt(D) = ${frozenScale} at load time by the E4 runner so all arms' concept rows ` +
      `share the trainable-init norm scale (poc/e1 policy); randomFrozen rows are stored at ` +
      `their natural N(0, initStd^2) draw (norm-matched in distribution, not per-row)`,
  });
}

if (isMain(import.meta.url)) main();
