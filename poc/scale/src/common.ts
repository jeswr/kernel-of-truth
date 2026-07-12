/**
 * SCALE-1 / S0 first-rung shared utilities (poc/scale).
 *
 * EPISTEMIC STATUS: exploratory engineering pilot for the SCALE-1 track
 * (docs/next/design/large-kernel-scale-track.md §8 stage S0). NOT a
 * pre-registered Phase-X harness, NOT an encoder version, and licenses NO
 * feasibility conclusion. Everything here is deterministic and re-runnable;
 * paths, weights and labels are pinned in VECTORISER_SPEC below.
 *
 * Box constraints (2 shared cores, ~3 GB free RAM): single-threaded,
 * blockwise, fp32 on disk, chunked checkpoints; callers are `nice -n 10`'d
 * via poc/package.json scripts.
 */

import { createHash } from 'node:crypto';
import {
  existsSync,
  mkdirSync,
  readFileSync,
  renameSync,
  writeFileSync,
  readdirSync,
  statSync,
  openSync,
  readSync,
  closeSync,
} from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { DetStream } from '@jeswr/kernel-encoder';

// Compiled layout is poc/scale/dist/*.js → poc/scale is one level up, poc two, repo three.
export const SCALE_DIR = join(dirname(fileURLToPath(import.meta.url)), '..');
export const POC_DIR = join(SCALE_DIR, '..');
export const REPO_DIR = join(POC_DIR, '..');
export const WN_DIR = join(REPO_DIR, 'data', 'lexical-wn31');
export const OUT_DIR = join(SCALE_DIR, 'out');
export const RESULTS_DIR = join(SCALE_DIR, 'results');

export function outDirFor(n: number): string {
  return join(OUT_DIR, `n${n}`);
}

export function ensureDir(p: string): void {
  mkdirSync(p, { recursive: true });
}

// ---------------------------------------------------------------------------
// Pinned vectoriser spec — kot-enc-import/0-poc
// ---------------------------------------------------------------------------
// An exploratory instantiation of design §6.3 (deterministic signed codes from
// SHA-256 labels + one fixed synchronous neighborhood round), built on the
// encoder package's DetStream primitive (same SHA-256 counter-stream
// determinism guarantees as kot-enc-B/1 and kot-enc-Bq/1). It is NOT a pinned
// encoder version: no ALGORITHM_VERSION bump, no X0 goldens; construction B's
// exact zero-crosstalk property is NOT claimed (see codebookQ.ts "WHAT IS
// LOST" — the same 1/sqrt(D) coherent-crosstalk regime applies here).
export const VECTORISER_SPEC = Object.freeze({
  name: 'kot-enc-import/0-poc',
  basis: 'design §6.3 steps 1-9; atoms = deterministic Rademacher ±1/√D, signs bit-packed (8/byte, LSB-first) from encoder DetStream',
  atomLabel: 'scale-import/atom/<D>/<token>',
  relsignLabel: 'scale-import/relsign/<D>/<rel>',
  featureTokens: {
    axiom: { token: 'ax/<rel>/<target-urn>', weight: 1.0 },
    lexfile: { token: 'lexfile/<lexFile>', weight: 0.25 },
    // pos/ssType tokens deliberately EXCLUDED from the semantic block: shared
    // coarse tokens would put an O(1/k) additive cosine floor under every
    // same-POS pair (§6.3 step 8's "identity codes outside the similarity
    // block", generalised to coarse features).
    lemma: { token: 'lemma/<lemma>', weight: 0.5, note: 'OPTIONAL lexical block (§6.2); only in the *lex secondary store — lemmas are annotations OUTSIDE record identity' },
  },
  rounds: 1,
  selfWeight: 1.0,
  degreeNorm: '1/sqrt(1+degWithin)  (within-subset axiom neighbors only; external targets contribute only their h0 joint atom)',
  aggregationOrder: 'axioms sorted by (rel, target) byte order before summation; float64 accumulation; h0 and h1 unit-normalised',
  jl: 'X4 Achlioptas sign matrix, ±1/sqrt(d), signs from DetStream label jl/<D>/<d> — IDENTICAL labels/consumption to poc/harness/x4.ts for comparability',
});

export function vectoriserPin(D: number): string {
  return createHash('sha256')
    .update(JSON.stringify({ spec: VECTORISER_SPEC, D }))
    .digest('hex');
}

// ---------------------------------------------------------------------------
// WordNet 3.1 loading (data/lexical-wn31, kot-lex/1 records)
// ---------------------------------------------------------------------------

export interface Axiom {
  rel: string;
  target: string;
  srcWord?: number;
  tgtWord?: number;
}

export interface LexRecord {
  id: string;
  pos: string;
  ssType: string;
  axioms: Axiom[];
  annotations: { lemmas: string[]; gloss: string; lexFile: string };
}

const POS_FILES = ['synsets-noun.jsonl', 'synsets-verb.jsonl', 'synsets-adj.jsonl', 'synsets-adv.jsonl'];

export function loadAllSynsets(): Map<string, LexRecord> {
  const map = new Map<string, LexRecord>();
  for (const f of POS_FILES) {
    const text = readFileSync(join(WN_DIR, f), 'utf8');
    let start = 0;
    while (start < text.length) {
      let end = text.indexOf('\n', start);
      if (end === -1) end = text.length;
      const line = text.slice(start, end);
      start = end + 1;
      if (line.trim().length === 0) continue;
      const rec = JSON.parse(line) as LexRecord;
      map.set(rec.id, rec);
    }
  }
  return map;
}

export function loadConcepts(n: number): LexRecord[] {
  const file = join(outDirFor(n), 'concepts.jsonl');
  return readFileSync(file, 'utf8')
    .split('\n')
    .filter((l) => l.trim().length > 0)
    .map((l) => JSON.parse(l) as LexRecord);
}

// ---------------------------------------------------------------------------
// Deterministic Rademacher atoms (bit-packed sign consumption, X4 style)
// ---------------------------------------------------------------------------

/** Fill `out` with a ±1/√D Rademacher atom for `label` (LSB-first bits, 8 signs/byte). */
export function fillAtom(out: Float64Array, D: number, label: string): void {
  const stream = new DetStream(label);
  const scale = 1 / Math.sqrt(D);
  for (let j = 0; j < D; j += 8) {
    const byte = stream.nextByte();
    for (let b = 0; b < 8 && j + b < D; b++) {
      out[j + b] = (byte >> b) & 1 ? scale : -scale;
    }
  }
}

/** ±1 sign diagonal for a relation label (unitary elementwise binding operator). */
export function relSigns(D: number, rel: string): Int8Array {
  const stream = new DetStream(`scale-import/relsign/${D}/${rel}`);
  const out = new Int8Array(D);
  for (let j = 0; j < D; j += 8) {
    const byte = stream.nextByte();
    for (let b = 0; b < 8 && j + b < D; b++) {
      out[j + b] = (byte >> b) & 1 ? 1 : -1;
    }
  }
  return out;
}

// ---------------------------------------------------------------------------
// Vector math
// ---------------------------------------------------------------------------

export function normalizeInPlace(v: Float64Array): void {
  let s = 0;
  for (let i = 0; i < v.length; i++) s += v[i]! * v[i]!;
  const n = Math.sqrt(s);
  if (n === 0) throw new Error('ERR_ZERO_VECTOR: record produced an all-zero semantic block');
  for (let i = 0; i < v.length; i++) v[i]! /= n;
}

// ---------------------------------------------------------------------------
// fp32 chunked vector stores (checkpointed, resumable)
// ---------------------------------------------------------------------------

export const CHUNK = 512; // concepts per chunk file

export interface StoreMeta {
  store: string;
  D: number;
  n: number;
  chunk: number;
  vectoriserPin: string;
  dtype: 'fp32-le';
}

export function storeDir(n: number, store: string): string {
  return join(outDirFor(n), 'vec', store);
}

export function chunkPath(dir: string, c: number): string {
  return join(dir, `chunk-${String(c).padStart(4, '0')}.bin`);
}

export function chunkComplete(dir: string, c: number, rows: number, D: number): boolean {
  const p = chunkPath(dir, c);
  return existsSync(p) && statSync(p).size === rows * D * 4;
}

export function writeChunk(dir: string, c: number, data: Float32Array): void {
  const p = chunkPath(dir, c);
  const tmp = `${p}.tmp`;
  writeFileSync(tmp, Buffer.from(data.buffer, data.byteOffset, data.byteLength));
  renameSync(tmp, p);
}

/** Load rows [r0, r1) of a store into a Float32Array (row-major, D columns). */
export function loadRows(n: number, store: string, D: number, r0: number, r1: number): Float32Array {
  const dir = storeDir(n, store);
  const out = new Float32Array((r1 - r0) * D);
  for (let c = Math.floor(r0 / CHUNK); c * CHUNK < r1; c++) {
    const rows = Math.min(CHUNK, n - c * CHUNK);
    const fd = openSync(chunkPath(dir, c), 'r');
    const buf = Buffer.alloc(rows * D * 4);
    readSync(fd, buf, 0, buf.length, 0);
    closeSync(fd);
    const chunkArr = new Float32Array(buf.buffer, buf.byteOffset, rows * D);
    const lo = Math.max(r0, c * CHUNK);
    const hi = Math.min(r1, c * CHUNK + rows);
    out.set(chunkArr.subarray((lo - c * CHUNK) * D, (hi - c * CHUNK) * D), (lo - r0) * D);
  }
  return out;
}

export function loadStore(n: number, store: string, D: number): Float32Array {
  return loadRows(n, store, D, 0, n);
}

export function storeBytes(n: number, store: string): number {
  const dir = storeDir(n, store);
  return readdirSync(dir)
    .filter((f) => f.endsWith('.bin'))
    .reduce((a, f) => a + statSync(join(dir, f)).size, 0);
}

// ---------------------------------------------------------------------------
// Stats / misc (mirrors poc/harness/common.ts; duplicated to keep the Phase-X
// harness untouched by this exploratory track)
// ---------------------------------------------------------------------------

export function percentile(sorted: readonly number[], p: number): number {
  if (sorted.length === 0) return NaN;
  const idx = (sorted.length - 1) * p;
  const lo = Math.floor(idx);
  const hi = Math.ceil(idx);
  const w = idx - lo;
  return sorted[lo]! * (1 - w) + sorted[hi]! * w;
}

export interface DistributionSummary {
  n: number;
  min: number;
  p5: number;
  p25: number;
  median: number;
  p75: number;
  p95: number;
  p99: number;
  max: number;
  mean: number;
  sd: number;
}

export function summarise(values: readonly number[]): DistributionSummary {
  const s = [...values].sort((a, b) => a - b);
  const mean = s.reduce((a, b) => a + b, 0) / Math.max(1, s.length);
  const sd = Math.sqrt(s.reduce((a, b) => a + (b - mean) * (b - mean), 0) / Math.max(1, s.length - 1));
  return {
    n: s.length,
    min: s[0] ?? NaN,
    p5: percentile(s, 0.05),
    p25: percentile(s, 0.25),
    median: percentile(s, 0.5),
    p75: percentile(s, 0.75),
    p95: percentile(s, 0.95),
    p99: percentile(s, 0.99),
    max: s[s.length - 1] ?? NaN,
    mean,
    sd,
  };
}

/** Spearman rank correlation (average ranks for ties). */
export function spearman(x: readonly number[], y: readonly number[]): number {
  if (x.length !== y.length || x.length < 2) throw new Error('spearman: length mismatch');
  const rank = (v: readonly number[]): Float64Array => {
    const idx = Array.from(v.keys()).sort((a, b) => v[a]! - v[b]!);
    const r = new Float64Array(v.length);
    let i = 0;
    while (i < idx.length) {
      let j = i;
      while (j + 1 < idx.length && v[idx[j + 1]!] === v[idx[i]!]) j++;
      const avg = (i + j) / 2 + 1;
      for (let k = i; k <= j; k++) r[idx[k]!] = avg;
      i = j + 1;
    }
    return r;
  };
  const rx = rank(x);
  const ry = rank(y);
  let mx = 0;
  let my = 0;
  for (let i = 0; i < rx.length; i++) {
    mx += rx[i]!;
    my += ry[i]!;
  }
  mx /= rx.length;
  my /= ry.length;
  let num = 0;
  let dx = 0;
  let dy = 0;
  for (let i = 0; i < rx.length; i++) {
    const a = rx[i]! - mx;
    const b = ry[i]! - my;
    num += a * b;
    dx += a * a;
    dy += b * b;
  }
  return num / Math.sqrt(dx * dy);
}

export function writeJson(path: string, value: unknown): void {
  const tmp = `${path}.tmp`;
  writeFileSync(tmp, JSON.stringify(value, null, 2));
  renameSync(tmp, path);
}

export function readJson<T>(path: string): T | null {
  if (!existsSync(path)) return null;
  try {
    return JSON.parse(readFileSync(path, 'utf8')) as T;
  } catch {
    return null;
  }
}

export function argValue(flag: string): string | undefined {
  const i = process.argv.indexOf(flag);
  return i >= 0 ? process.argv[i + 1] : undefined;
}

export function targetN(): number {
  return Number(argValue('--n') ?? 10000);
}

export function fmt(x: number, digits = 4): string {
  return Number.isFinite(x) ? x.toFixed(digits) : String(x);
}

export function nowMs(): number {
  return Number(process.hrtime.bigint() / 1000n) / 1000;
}
