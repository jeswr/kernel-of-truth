/**
 * E8 extension 2 — kernel-side RDMs for the 1,054-concept E4 vocabulary
 * (pre-registration: poc/e8/README.md §Extension 2, fixed before this file
 * was written).
 *
 * Path discipline (Common rule 3): E8 uses the PROJECTED path. The E4 vector
 * tables are kot-enc-Bq/1 @ D=512 (toy-native) and are NOT used here. This
 * harness re-encodes all 1,054 concepts (54 kernel-v0 + 1,000 synthetic pure
 * prime structures from poc/e4/inputs/synthetic-concepts.json) at D=8192
 * with the PINNED kot-enc-B/1 encoder — content hash asserted, fail closed —
 * and projects through the SAME fixed Achlioptas JL streams jl/8192/512 and
 * jl/8192/576.
 *
 * `jlProject`, `cosine` are VERBATIM copies of poc/e2/harness/common.ts's
 * (which are themselves verbatim copies of poc/harness/x4.ts's — the exact
 * construction the X4 distortion numbers were measured on). Duplicated
 * rather than imported per the E2 harness's own self-containment note.
 *
 * Output (poc/e8/scale/out/): rdm-full.f32 / rdm-jl512.f32 / rdm-jl576.f32
 * (row-major n x n float32 similarity matrices) + kernel-rdm-scale-meta.json
 * (ids, order, pins). Distortion (full vs jl512/jl576 RDM Spearman over the
 * 1,054) is computed by poc/e8/build_inputs.py --scale from these binaries
 * and published in the scale manifest.
 */

import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  DEFAULT_PARAMS,
  DetStream,
  encodeConceptSet,
  encoderContentHash,
  validateExplication,
} from '@jeswr/kernel-encoder';
import type { Explication } from '@jeswr/kernel-encoder';

const HERE = dirname(fileURLToPath(import.meta.url)); // poc/e8/scale/dist
const SCALE_DIR = join(HERE, '..');
const REPO_DIR = join(SCALE_DIR, '..', '..', '..');
const KERNEL_V0_DIR = join(REPO_DIR, 'data', 'kernel-v0');
const SYNTH_PATH = join(REPO_DIR, 'poc', 'e4', 'inputs', 'synthetic-concepts.json');
const OUT_DIR = join(SCALE_DIR, 'out');

// PINNED (docs/poc-design.md Common rule 2): kot-enc-B/1 @ D=8192.
const PINNED_ENCODER_HASH = '40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c';

function sha256Hex(data: Buffer | string): string {
  return createHash('sha256').update(data).digest('hex');
}

function cosine(a: Float64Array, b: Float64Array): number {
  let dot = 0;
  let na = 0;
  let nb = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i]! * b[i]!;
    na += a[i]! * a[i]!;
    nb += b[i]! * b[i]!;
  }
  const den = Math.sqrt(na) * Math.sqrt(nb);
  return den > 0 ? dot / den : 0;
}

// VERBATIM copy of poc/e2/harness/common.ts jlProject (itself verbatim from
// poc/harness/x4.ts; Common rule 3 — E-series claims inherit X4's numbers).
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

function rdmF32(vecs: readonly Float64Array[]): Float32Array {
  const n = vecs.length;
  const out = new Float32Array(n * n);
  for (let i = 0; i < n; i++) {
    out[i * n + i] = 1;
    for (let j = i + 1; j < n; j++) {
      const s = cosine(vecs[i]!, vecs[j]!);
      out[i * n + j] = s;
      out[j * n + i] = s;
    }
  }
  return out;
}

function main(): void {
  const encHash = encoderContentHash(DEFAULT_PARAMS);
  if (encHash !== PINNED_ENCODER_HASH) {
    throw new Error(`ERR_ENCODER_PIN: content hash ${encHash} != pinned ${PINNED_ENCODER_HASH}`);
  }
  if (DEFAULT_PARAMS.D !== 8192) {
    throw new Error(`ERR_ENCODER_PIN: DEFAULT_PARAMS.D=${DEFAULT_PARAMS.D} != 8192`);
  }

  // ---- kernel-v0 (54, reference DAG) ----
  const conceptsDir = join(KERNEL_V0_DIR, 'concepts');
  const files = readdirSync(conceptsDir).filter((f) => f.endsWith('.json')).sort();
  const defs = new Map<string, Explication>();
  for (const f of files) {
    const rec = JSON.parse(readFileSync(join(conceptsDir, f), 'utf8')) as {
      id: string;
      explication: Explication;
    };
    defs.set(rec.id, rec.explication);
  }
  const nKernel = defs.size;

  // ---- synthetic 1,000 (pure prime structures; sha re-asserted per record) ----
  const synthRaw = readFileSync(SYNTH_PATH);
  const synth = JSON.parse(synthRaw.toString()) as {
    count: number;
    records: { id: string; astSha256: string; explication: Explication }[];
  };
  if (synth.records.length !== synth.count) {
    throw new Error(`ERR_SYNTH: records ${synth.records.length} != count ${synth.count}`);
  }
  for (const rec of synth.records) {
    validateExplication(rec.explication);
    if (defs.has(rec.id)) throw new Error(`ERR_SYNTH: duplicate id ${rec.id}`);
    defs.set(rec.id, rec.explication);
  }
  const ids = [...defs.keys()];
  console.log(`encoding ${ids.length} concepts (${nKernel} kernel-v0 + ${synth.records.length} synthetic) at D=8192`);

  const t0 = Date.now();
  const { vectors } = encodeConceptSet(defs);
  console.log(`encoded in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  const vecs = ids.map((id) => {
    const v = vectors.get(id);
    if (v === undefined) throw new Error(`no vector for ${id}`);
    return v;
  });

  mkdirSync(OUT_DIR, { recursive: true });
  const filesOut: Record<string, { file: string; sha256: string }> = {};
  const writeRdm = (name: string, vv: readonly Float64Array[]): void => {
    const m = rdmF32(vv);
    const buf = Buffer.from(m.buffer, m.byteOffset, m.byteLength);
    const file = `rdm-${name}.f32`;
    writeFileSync(join(OUT_DIR, file), buf);
    filesOut[name] = { file, sha256: sha256Hex(buf) };
    console.log(`wrote ${file} (${(buf.length / 1e6).toFixed(1)} MB) sha256 ${filesOut[name]!.sha256.slice(0, 12)}…`);
  };

  writeRdm('full', vecs);
  for (const d of [512, 576]) {
    const t1 = Date.now();
    const proj = jlProject(vecs, 8192, d);
    console.log(`JL 8192->${d} in ${((Date.now() - t1) / 1000).toFixed(1)}s`);
    writeRdm(`jl${d}`, proj);
  }

  const meta = {
    artifact: 'e8-kernel-rdm-scale',
    date: new Date().toISOString(),
    designPin: 'poc/e8/README.md §Extension 2 (pre-registered before this harness was written)',
    encoderContentHash: encHash,
    D: 8192,
    n: ids.length,
    idOrder: 'kernel-v0 concepts (file-sorted, as data/kernel-v0/concepts) then synthetic records in file order',
    ids,
    layout: 'row-major n x n float32 cosine SIMILARITY (unit diagonal), little-endian',
    jlDerivation:
      'Achlioptas sign matrix, ±1/sqrt(d), signs from SHA-256 stream label jl/<D>/<d> — verbatim x4.ts construction',
    sources: {
      kernelV0ConceptFiles: files.length,
      syntheticConcepts: {
        path: 'poc/e4/inputs/synthetic-concepts.json',
        sha256: sha256Hex(synthRaw),
        count: synth.records.length,
      },
    },
    rdms: filesOut,
  };
  writeFileSync(join(OUT_DIR, 'kernel-rdm-scale-meta.json'), JSON.stringify(meta, null, 2) + '\n');
  console.log(`wrote kernel-rdm-scale-meta.json (n=${ids.length})`);
}

main();
