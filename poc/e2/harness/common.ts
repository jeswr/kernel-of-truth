/**
 * Shared utilities for the E2 prep harness (docs/poc-design.md Phase E, E2).
 *
 * Self-contained on purpose: the brief for kernel-of-truth-9ml forbids
 * touching the other poc harnesses, so the few helpers shared with
 * poc/harness/common.ts are duplicated here (and `jlProject` is a verbatim
 * copy of poc/harness/x4.ts's — the SAME fixed, seedless JL construction the
 * X4 distortion numbers were measured on; E-series claims inherit those
 * numbers per Common rule 3).
 */

import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { DetStream } from '@jeswr/kernel-encoder';

// Compiled layout is poc/e2/dist/harness/*.js, so poc/e2/ is two levels up.
export const E2_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
export const INPUTS_DIR = join(E2_DIR, 'inputs');
export const REPO_DIR = join(E2_DIR, '..', '..');
export const KERNEL_V0_DIR = join(REPO_DIR, 'data', 'kernel-v0');

export function ensureInputsDir(): void {
  mkdirSync(INPUTS_DIR, { recursive: true });
}

/** True when the module at `importMetaUrl` is the entry script (not an import). */
export function isMain(importMetaUrl: string): boolean {
  const entry = process.argv[1];
  if (entry === undefined) return false;
  return importMetaUrl === new URL(`file://${entry}`).href || importMetaUrl.endsWith(entry.replace(/^.*\//, '/'));
}

export function writeInput(name: string, json: unknown): string {
  ensureInputsDir();
  const file = join(INPUTS_DIR, name);
  writeFileSync(file, JSON.stringify(json, null, 2) + '\n');
  console.log(`wrote ${file}`);
  return file;
}

export function readInput<T>(name: string): T {
  return JSON.parse(readFileSync(join(INPUTS_DIR, name), 'utf8')) as T;
}

export function sha256Hex(data: Buffer | string): string {
  return createHash('sha256').update(data).digest('hex');
}

/**
 * Corpus pin for data/kernel-v0: sha256 of manifest.json bytes, plus a
 * combined content hash over every concepts/*.json (sorted by filename,
 * each entry hashed as `<filename>\n<bytes>`). Stamped into every input
 * artefact so a corpus edit invalidates them visibly.
 */
export function corpusPin(): { manifestSha256: string; conceptsSha256: string; conceptCount: number } {
  const manifest = readFileSync(join(KERNEL_V0_DIR, 'manifest.json'));
  const dir = join(KERNEL_V0_DIR, 'concepts');
  const files = readdirSync(dir).filter((f) => f.endsWith('.json')).sort();
  const h = createHash('sha256');
  for (const f of files) {
    h.update(f);
    h.update('\n');
    h.update(readFileSync(join(dir, f)));
  }
  return {
    manifestSha256: sha256Hex(manifest),
    conceptsSha256: h.digest('hex'),
    conceptCount: files.length,
  };
}

// ---------------------------------------------------------------------------
// Linear algebra / stats
// ---------------------------------------------------------------------------

export function dot(a: Float64Array, b: Float64Array): number {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i]! * b[i]!;
  return s;
}

export function norm(a: Float64Array): number {
  return Math.sqrt(dot(a, a));
}

export function cosine(a: Float64Array, b: Float64Array): number {
  return dot(a, b) / (norm(a) * norm(b));
}

/** Full symmetric similarity matrix (unit diagonal) from a similarity fn. */
export function similarityMatrix(n: number, sim: (i: number, j: number) => number): number[][] {
  const m: number[][] = Array.from({ length: n }, () => new Array<number>(n).fill(0));
  for (let i = 0; i < n; i++) {
    m[i]![i] = 1;
    for (let j = i + 1; j < n; j++) {
      const s = sim(i, j);
      m[i]![j] = s;
      m[j]![i] = s;
    }
  }
  return m;
}

/** Lower-triangle off-diagonal vector (i<j order), the RSA comparison vector. */
export function offDiagonal(m: readonly (readonly number[])[]): number[] {
  const out: number[] = [];
  for (let i = 0; i < m.length; i++) {
    for (let j = i + 1; j < m.length; j++) out.push(m[i]![j]!);
  }
  return out;
}

/** Spearman rank correlation (average ranks for ties) — mirror of poc/harness/common.ts. */
export function spearman(x: readonly number[], y: readonly number[]): number {
  if (x.length !== y.length || x.length < 2) throw new Error('spearman: length mismatch');
  const rank = (v: readonly number[]): number[] => {
    const idx = v.map((_, i) => i).sort((a, b) => v[a]! - v[b]!);
    const r = new Array<number>(v.length);
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
  const mx = rx.reduce((a, b) => a + b, 0) / rx.length;
  const my = ry.reduce((a, b) => a + b, 0) / ry.length;
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

// ---------------------------------------------------------------------------
// JL projection — VERBATIM copy of poc/harness/x4.ts jlProject (Common rule 3:
// one fixed, seedless, deterministic Achlioptas sign matrix per (D, d) pair,
// signs from the SHA-256 stream `jl/<D>/<d>`). Do not modify: the X4
// distortion numbers only transfer if this construction is bit-identical.
// ---------------------------------------------------------------------------

export function jlProject(vectors: readonly Float64Array[], D: number, d: number): Float64Array[] {
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
