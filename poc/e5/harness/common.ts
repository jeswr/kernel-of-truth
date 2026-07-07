/**
 * Shared utilities for the E5 prep harness (docs/poc-design.md Phase E, E5
 * rev 2; bead kernel-of-truth-c24).
 *
 * Self-contained on purpose (same policy as poc/e1/harness/common.ts,
 * poc/e2/harness/common.ts, poc/e4/harness/common.ts): the brief forbids
 * touching encoder/, mapper/, data/kernel-v0 and the other poc suites, so
 * the few duplicated helpers (corpusPin, sha256Hex, isMain, jlProject,
 * seededDerangement, featureSet) are COPIED here — each with its provenance
 * noted — rather than imported across package boundaries.
 */

import { DetStream } from '@jeswr/kernel-encoder';
import type { Clause, Explication, Filler, OpArg } from '@jeswr/kernel-encoder';
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Compiled layout is poc/e5/dist/harness/*.js, so poc/e5/ is two levels up.
export const E5_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
export const INPUTS_DIR = join(E5_DIR, 'inputs');
export const REPO_DIR = join(E5_DIR, '..', '..');
export const KERNEL_V0_DIR = join(REPO_DIR, 'data', 'kernel-v0');
export const E4_INPUTS_DIR = join(REPO_DIR, 'poc', 'e4', 'inputs');
export const E4_GLOSS_HASH_FILE = join(REPO_DIR, 'poc', 'e4', 'GLOSS-HASH.txt');

/**
 * The pinned kot-enc-B/1 content hash at D=8192 (docs/poc-design.md Common
 * rule 2, pinned 2026-07-07 before any E-run) — E5 uses the PROJECTED path
 * (rule 3, path ii): full-D vectors through the fixed X4 JL matrix. A
 * mismatch is an encoder version change and FAILS CLOSED.
 */
export const PINNED_B8192_HASH =
  '40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c';

/**
 * The E4 gloss-set hash, published 2026-07-07T06:43Z in poc/e4/GLOSS-HASH.txt
 * BEFORE any training consumed the gloss set (E4 rev 2, MAJOR 6). E5 reuses
 * the gloss set byte-identically and inherits the pin: consuming a gloss
 * file with any other sha-256 is a NEW pre-registration.
 */
export const PINNED_GLOSS_HASH =
  '36181f9b65090887d8af45c845abe122d12d6352b61a16bcaa68f9c3c5794e12';

/** Full encoder dimension (kot-enc-B/1). */
export const D_FULL = 8192;

/** JL target = SmolLM2-135M d_model (X4 pre-registered pair 8192->576). */
export const D_MODEL = 576;

/** Paired experiment seeds (Common rule 1). */
export const N_SEEDS = 5;

/** Seen concepts: all 54 authored kernel-v0 + 446 selected synthetics. */
export const N_SEEN_SYNTH = 446;

/** Nonce concepts (E5 rev 2 floor: n >= 20). */
export const N_NONCE = 24;

/** Gloss style variants used in TRAINING items (0-3); style 4 is eval-only. */
export const TRAIN_STYLES = [0, 1, 2, 3] as const;
export const EVAL_STYLE = 4;

/** Forced-choice candidates per eval item (1 true + 4 distractors). */
export const N_CANDIDATES = 5;

/** Fraction of training items held out as the LR-selection val set. */
export const VAL_FRACTION = 0.1;

/** Structural pre-filter for the nonce pool (pinned in README O2). */
export const NONCE_MIN_DEPTH = 2;
export const NONCE_MIN_TOP_CLAUSES = 2;

export function slugOf(id: string): string {
  return id.replace(/^urn:kernel-v0:/, '').replace(/^urn:kernel-e4:/, 'e4-');
}

export function ensureInputsDir(): void {
  mkdirSync(INPUTS_DIR, { recursive: true });
}

/** True when the module at `importMetaUrl` is the entry script (not an import). */
export function isMain(importMetaUrl: string): boolean {
  const entry = process.argv[1];
  if (entry === undefined) return false;
  return (
    importMetaUrl === new URL(`file://${entry}`).href ||
    importMetaUrl.endsWith(entry.replace(/^.*\//, '/'))
  );
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

export function sha256File(path: string): string {
  return sha256Hex(readFileSync(path));
}

/** Corpus pin for data/kernel-v0 — verbatim policy of poc/e1/harness/common.ts. */
export function corpusPin(): {
  manifestSha256: string;
  conceptsSha256: string;
  conceptCount: number;
} {
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

export interface KernelV0Record {
  readonly id: string;
  readonly label: string;
  readonly gloss: string;
  readonly explication: unknown;
}

/** Load the kernel-v0 concept records (read-only), alphabetical by filename/slug. */
export function loadKernelV0(): KernelV0Record[] {
  const dir = join(KERNEL_V0_DIR, 'concepts');
  const files = readdirSync(dir).filter((f) => f.endsWith('.json')).sort();
  return files.map((f) => JSON.parse(readFileSync(join(dir, f), 'utf8')) as KernelV0Record);
}

/** E4 synthetic-concept record shape (poc/e4/harness/synthVocab.ts). */
export interface SynthRecord {
  readonly id: string;
  readonly seed: string;
  readonly topClauses: number;
  readonly depth: number;
  readonly retries: number;
  readonly astSha256: string;
  readonly explication: Explication;
}

/** Load E4's committed synthetic vocabulary READ-ONLY, with its sha recorded. */
export function loadE4Synthetics(): { records: SynthRecord[]; fileSha256: string } {
  const path = join(E4_INPUTS_DIR, 'synthetic-concepts.json');
  const bytes = readFileSync(path);
  const j = JSON.parse(bytes.toString('utf8')) as { artifact: string; records: SynthRecord[] };
  if (j.artifact !== 'e4-synthetic-concepts') {
    throw new Error('ERR_ARTIFACT: poc/e4/inputs/synthetic-concepts.json artifact tag mismatch');
  }
  return { records: j.records, fileSha256: sha256Hex(bytes) };
}

export interface GlossRecord {
  readonly conceptId: string;
  readonly slug: string;
  readonly variant: number;
  readonly style: number;
  readonly gloss: string;
}

/**
 * Load E4's committed gloss set READ-ONLY, verifying the sha-256 against BOTH
 * the pinned constant above and the committed poc/e4/GLOSS-HASH.txt. FAIL
 * CLOSED on any mismatch (MAJOR 6 discipline, inherited).
 */
export function loadGlosses(): Map<string, string[]> {
  const path = join(E4_INPUTS_DIR, 'glosses.jsonl');
  const bytes = readFileSync(path);
  const sha = sha256Hex(bytes);
  if (sha !== PINNED_GLOSS_HASH) {
    throw new Error(`ERR_GLOSS_PIN: sha256(glosses.jsonl) ${sha} != pinned ${PINNED_GLOSS_HASH}`);
  }
  const published = readFileSync(E4_GLOSS_HASH_FILE, 'utf8');
  if (!published.includes(PINNED_GLOSS_HASH)) {
    throw new Error('ERR_GLOSS_PIN: poc/e4/GLOSS-HASH.txt does not contain the pinned hash');
  }
  const byConcept = new Map<string, string[]>();
  for (const line of bytes.toString('utf8').split('\n')) {
    if (line.trim() === '') continue;
    const rec = JSON.parse(line) as GlossRecord;
    const arr = byConcept.get(rec.conceptId) ?? [];
    arr[rec.style] = rec.gloss;
    byConcept.set(rec.conceptId, arr);
  }
  for (const [id, arr] of byConcept) {
    if (arr.length !== 5 || arr.some((g) => typeof g !== 'string' || g.length === 0)) {
      throw new Error(`ERR_GLOSS_SET: concept ${id} does not have exactly 5 style glosses`);
    }
  }
  return byConcept;
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

// ---------------------------------------------------------------------------
// Seeded derangement + seeded sample — copied from poc/e4/harness
// (vectorTables.ts / holdout.ts; poc/e1 construction): Fisher-Yates over
// DetStream `perm/<label>` with labelled redraws until no fixed points.
// ---------------------------------------------------------------------------

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

/** Seeded sample WITHOUT replacement via DetStream Fisher-Yates prefix
 * (verbatim construction of poc/e4/harness/holdout.ts seededSample). */
export function seededSample<T>(label: string, items: readonly T[], k: number): T[] {
  const stream = new DetStream(`perm/${label}`);
  const p = Array.from({ length: items.length }, (_, i) => i);
  for (let i = p.length - 1; i > 0; i--) {
    const j = stream.nextBelow(i + 1);
    const t = p[i]!;
    p[i] = p[j]!;
    p[j] = t;
  }
  return p.slice(0, k).map((i) => items[i]!);
}

/** Deterministic N(0, std^2) values via Box-Muller over DetStream (poc/e1
 * construction, copied from poc/e4/harness/vectorTables.ts). */
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

export function writeF32(path: string, data: Float32Array): string {
  // Explicit little-endian byte layout (manifest promises LE; numpy '<f4').
  const buf = Buffer.alloc(data.length * 4);
  for (let i = 0; i < data.length; i++) buf.writeFloatLE(data[i]!, i * 4);
  writeFileSync(path, buf);
  console.log(`wrote ${path} (${buf.length} bytes)`);
  return sha256Hex(buf);
}

// ---------------------------------------------------------------------------
// Compositional-split features — VERBATIM copy of poc/e4/harness/holdout.ts
// (pre-registered feature definition: {frame} + depth-1 clause skeletons over
// all clause nodes). Copied, not imported, per the no-cross-package policy;
// the E4 file remains the definition of record.
// ---------------------------------------------------------------------------

function fillerTag(f: Filler, d: number): string {
  switch (f.kind) {
    case 'sp':
      return 'sp';
    case 'ref':
      return 'ref';
    case 'prime':
      return 'pr';
    case 'concept':
      return 'c';
    case 'quote':
      return 'q';
    case 'clause':
      return d > 0 ? clauseSkel(f.clause, d - 1) : 'cl';
    case 'temporal':
      return 't';
    default:
      return 'x';
  }
}

function opArgTag(a: OpArg, d: number): string {
  if ((a as Clause).type === 'pred' || (a as Clause).type === 'op') {
    return d > 0 ? clauseSkel(a as Clause, d - 1) : 'cl';
  }
  return fillerTag(a as Filler, d);
}

export function clauseSkel(c: Clause, d: number): string {
  if (c.type === 'pred') {
    const roles = Object.entries(c.roles)
      .map(([role, f]) => `${role}:${fillerTag(f as Filler, d)}`)
      .sort()
      .join(',');
    return `P(${c.pred}|${roles})`;
  }
  return `O(${c.op}|${c.args.map((a) => opArgTag(a, d)).join(',')})`;
}

function allClauses(e: Explication): Clause[] {
  const out: Clause[] = [];
  const visit = (n: unknown): void => {
    if (n === null || typeof n !== 'object') return;
    if (Array.isArray(n)) {
      n.forEach(visit);
      return;
    }
    const o = n as Record<string, unknown>;
    if (o['type'] === 'pred' || o['type'] === 'op') out.push(o as unknown as Clause);
    Object.values(o).forEach(visit);
  };
  visit(e.clauses);
  return out;
}

export function featureSet(e: Explication): Set<string> {
  const out = new Set<string>([`F(${e.frame})`]);
  for (const c of allClauses(e)) out.add(clauseSkel(c, 1));
  return out;
}
