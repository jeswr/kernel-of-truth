/**
 * Shared utilities for the E9-defl prep harness (poc/e9/README.md; bead
 * kernel-of-truth-xj2). Self-contained per the house no-cross-import policy:
 * helpers are COPIED from poc/e5/harness/common.ts (itself the E4/E1 lineage)
 * with provenance noted, not imported across package boundaries.
 */

import { DetStream } from '@jeswr/kernel-encoder';
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import type { Explication } from '@jeswr/kernel-encoder';

export const E9_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
export const INPUTS_DIR = join(E9_DIR, 'inputs');
export const REPO_DIR = join(E9_DIR, '..', '..');
export const KERNEL_V0_DIR = join(REPO_DIR, 'data', 'kernel-v0');
export const E4_INPUTS_DIR = join(REPO_DIR, 'poc', 'e4', 'inputs');
export const E5_INPUTS_DIR = join(REPO_DIR, 'poc', 'e5', 'inputs');

/** Pinned kot-enc-B/1 @ D=8192 (Common rule 2; identical to poc/e5). */
export const PINNED_B8192_HASH =
  '40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c';

export const D_FULL = 8192;
export const D_MODEL = 576;
export const N_SEEDS = 5;

export function slugOf(id: string): string {
  return id.replace(/^urn:kernel-v0:/, '').replace(/^urn:kernel-e4:/, 'e4-');
}

export function isMain(importMetaUrl: string): boolean {
  const entry = process.argv[1];
  if (entry === undefined) return false;
  return (
    importMetaUrl === new URL(`file://${entry}`).href ||
    importMetaUrl.endsWith(entry.replace(/^.*\//, '/'))
  );
}

export function writeInput(name: string, json: unknown): string {
  mkdirSync(INPUTS_DIR, { recursive: true });
  const file = join(INPUTS_DIR, name);
  writeFileSync(file, JSON.stringify(json, null, 2) + '\n');
  console.log(`wrote ${file}`);
  return file;
}

export function readInput<T>(name: string): T {
  return JSON.parse(readFileSync(join(INPUTS_DIR, name), 'utf8')) as T;
}

export function readE5Input<T>(name: string): T {
  return JSON.parse(readFileSync(join(E5_INPUTS_DIR, name), 'utf8')) as T;
}

export function sha256Hex(data: Buffer | string): string {
  return createHash('sha256').update(data).digest('hex');
}

export function sha256File(path: string): string {
  return sha256Hex(readFileSync(path));
}

export interface KernelV0Record {
  readonly id: string;
  readonly label: string;
  readonly gloss: string;
  readonly explication: unknown;
}

/** kernel-v0 records, alphabetical (copied from poc/e5/harness/common.ts). */
export function loadKernelV0(): KernelV0Record[] {
  const dir = join(KERNEL_V0_DIR, 'concepts');
  const files = readdirSync(dir).filter((f) => f.endsWith('.json')).sort();
  return files.map((f) => JSON.parse(readFileSync(join(dir, f), 'utf8')) as KernelV0Record);
}

export interface SynthRecord {
  readonly id: string;
  readonly seed: string;
  readonly topClauses: number;
  readonly depth: number;
  readonly retries: number;
  readonly astSha256: string;
  readonly explication: Explication;
}

export function loadE4Synthetics(): { records: SynthRecord[]; fileSha256: string } {
  const path = join(E4_INPUTS_DIR, 'synthetic-concepts.json');
  const bytes = readFileSync(path);
  const j = JSON.parse(bytes.toString('utf8')) as { artifact: string; records: SynthRecord[] };
  if (j.artifact !== 'e4-synthetic-concepts') {
    throw new Error('ERR_ARTIFACT: poc/e4/inputs/synthetic-concepts.json artifact tag mismatch');
  }
  return { records: j.records, fileSha256: sha256Hex(bytes) };
}

// ---------------------------------------------------------------------------
// JL projection — VERBATIM copy of poc/harness/x4.ts jlProject (via
// poc/e5/harness/common.ts). Do not modify: the X4 distortion numbers only
// transfer if this construction is bit-identical.
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

export function writeF32(path: string, data: Float32Array): string {
  const buf = Buffer.alloc(data.length * 4);
  for (let i = 0; i < data.length; i++) buf.writeFloatLE(data[i]!, i * 4);
  writeFileSync(path, buf);
  console.log(`wrote ${path} (${buf.length} bytes)`);
  return sha256Hex(buf);
}

/**
 * Pinned proxy size metric for AUTHORED explications (README J2):
 * topClauses = clauses.length; depth = 1 for a flat explication, +1 per
 * clause-nesting level (a clause appearing as a filler / op arg / quote body
 * value), clamped to the generator's supported 1..5 — the convention under
 * which the authored histogram measures 1..3 (see e9-defl artifact).
 */
export function authoredSizeProxy(e: { clauses: unknown[] }): { topClauses: number; depth: number } {
  const depthOf = (node: unknown, d: number): number => {
    if (node === null || typeof node !== 'object') return d;
    if (Array.isArray(node)) {
      let m = d;
      for (const n of node) m = Math.max(m, depthOf(n, d));
      return m;
    }
    const o = node as Record<string, unknown>;
    let m = d;
    for (const v of Object.values(o)) {
      const isClause =
        v !== null && typeof v === 'object' && !Array.isArray(v) &&
        ((v as { type?: string }).type === 'pred' || (v as { type?: string }).type === 'op');
      m = Math.max(m, depthOf(v, isClause ? d + 1 : d));
    }
    return m;
  };
  const depth = Math.min(5, depthOf(e.clauses, 1));
  return { topClauses: e.clauses.length, depth };
}
