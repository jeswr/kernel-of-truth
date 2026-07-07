/**
 * Shared utilities for the Phase-X harnesses (docs/poc-design.md Phase X).
 * Box constraints respected: everything runs single-threaded, blockwise, with
 * JSON checkpoints under poc/results/ so interrupted runs resume; callers are
 * `nice`d via the npm scripts.
 */

import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync, existsSync, renameSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Compiled layout is poc/dist/*.js (tsconfig rootDir=harness), so poc/ is one level up.
export const POC_DIR = join(dirname(fileURLToPath(import.meta.url)), '..');
export const RESULTS_DIR = join(POC_DIR, 'results');
export const FIXTURES_DIR = join(POC_DIR, 'fixtures');

export function ensureDirs(): void {
  mkdirSync(RESULTS_DIR, { recursive: true });
  mkdirSync(FIXTURES_DIR, { recursive: true });
}

export function dot(a: Float64Array, b: Float64Array): number {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i]! * b[i]!;
  return s;
}

export function norm(a: Float64Array): number {
  return Math.sqrt(dot(a, a));
}

/** Angle between vectors in radians (numerically clamped). */
export function angle(a: Float64Array, b: Float64Array): number {
  const c = dot(a, b) / (norm(a) * norm(b));
  return Math.acos(Math.max(-1, Math.min(1, c)));
}

export function cosine(a: Float64Array, b: Float64Array): number {
  return dot(a, b) / (norm(a) * norm(b));
}

/** Canonical little-endian byte serialisation of a vector (X0 golden discipline). */
export function vectorBytes(v: Float64Array): Buffer {
  const buf = Buffer.alloc(v.length * 8);
  for (let i = 0; i < v.length; i++) buf.writeDoubleLE(v[i]!, i * 8);
  return buf;
}

export function vectorSha256(v: Float64Array): string {
  return createHash('sha256').update(vectorBytes(v)).digest('hex');
}

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
  p1: number;
  p5: number;
  p25: number;
  median: number;
  p75: number;
  p95: number;
  p99: number;
  max: number;
  mean: number;
}

export function summarise(values: readonly number[]): DistributionSummary {
  const s = [...values].sort((a, b) => a - b);
  const mean = s.reduce((a, b) => a + b, 0) / Math.max(1, s.length);
  return {
    n: s.length,
    min: s[0] ?? NaN,
    p1: percentile(s, 0.01),
    p5: percentile(s, 0.05),
    p25: percentile(s, 0.25),
    median: percentile(s, 0.5),
    p75: percentile(s, 0.75),
    p95: percentile(s, 0.95),
    p99: percentile(s, 0.99),
    max: s[s.length - 1] ?? NaN,
    mean,
  };
}

/** Spearman rank correlation (average ranks for ties). */
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
// Checkpointing (blockwise resume)
// ---------------------------------------------------------------------------

export function loadCheckpoint<T>(name: string): T | null {
  const file = join(RESULTS_DIR, name);
  if (!existsSync(file)) return null;
  try {
    return JSON.parse(readFileSync(file, 'utf8')) as T;
  } catch {
    return null; // corrupt checkpoint: start over (harness re-derives everything)
  }
}

export function saveCheckpoint(name: string, state: unknown): void {
  const file = join(RESULTS_DIR, name);
  const tmp = `${file}.tmp`;
  writeFileSync(tmp, JSON.stringify(state));
  renameSync(tmp, file);
}

export function writeReport(baseName: string, json: unknown, markdown: string): void {
  ensureDirs();
  writeFileSync(join(RESULTS_DIR, `${baseName}.json`), JSON.stringify(json, null, 2));
  writeFileSync(join(RESULTS_DIR, `${baseName}.md`), markdown);
  console.log(`wrote ${join(RESULTS_DIR, baseName)}.{json,md}`);
}

export function argValue(flag: string): string | undefined {
  const i = process.argv.indexOf(flag);
  return i >= 0 ? process.argv[i + 1] : undefined;
}

export function hasFlag(flag: string): boolean {
  return process.argv.includes(flag);
}

export function fmt(x: number, digits = 4): string {
  return Number.isFinite(x) ? x.toFixed(digits) : String(x);
}
