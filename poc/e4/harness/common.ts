/**
 * Shared utilities for the E4 prep harness (docs/poc-design.md Phase E, E4
 * rev 2; bead kernel-of-truth-73u).
 *
 * Self-contained on purpose (same policy as poc/e1/harness/common.ts and
 * poc/e2/harness/common.ts): the brief forbids touching encoder/, mapper/
 * internals, data/kernel-v0 and poc/e1, so the few duplicated helpers
 * (corpusPin, sha256Hex, isMain) are copied here rather than imported across
 * package boundaries.
 */

import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Compiled layout is poc/e4/dist/harness/*.js, so poc/e4/ is two levels up.
export const E4_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
export const INPUTS_DIR = join(E4_DIR, 'inputs');
export const REPO_DIR = join(E4_DIR, '..', '..');
export const KERNEL_V0_DIR = join(REPO_DIR, 'data', 'kernel-v0');
export const MAPPER_DIR = join(REPO_DIR, 'mapper');

/**
 * The pinned kot-enc-Bq/1 content hash at D=512 (docs/poc-design.md Common
 * rule 2, pinned 2026-07-07 before any E-run) — the SAME pin poc/e1 uses
 * (toy-native dimension policy, path (i): E1/E4 share d_model = 512). Every
 * vector-table artifact is verified against this at generation time and
 * stamped with it; a mismatch is an encoder version change and FAILS CLOSED.
 */
export const PINNED_BQ512_HASH =
  '3492799ed73b49a612bebca920421041edd31d7bd4098bcf55da52df127ab9ee';

/** E4 model dimension = E1's d_model (the E4 run fine-tunes the E1 model). */
export const E4_D_MODEL = 512;

/** Trainable-arm embedding init distribution — identical to poc/e1 (GPT-2 init). */
export const INIT_STD = 0.02;

/** Number of paired experiment seeds (Common rule 1; matches E1's N_SEEDS). */
export const N_SEEDS = 5;

/** Synthetic vocabulary size (E4 rev 2: concept vocabulary scaled to >=10^3). */
export const N_SYNTH = 1000;

/** Gloss variants authored per concept (E4 rev 2: >=5 per held-out concept). */
export const N_GLOSS_VARIANTS = 5;

/** Tier-1 holdout fraction of the full vocabulary (E4 rev 2: ~20%). */
export const TIER1_FRACTION = 0.2;

/** Tier-2 size (E4 rev 2: ~10 concepts fully excluded from ALL training text). */
export const TIER2_SIZE = 10;

/** Synthetic concept id/slug scheme. Slug feeds the ⟦c:<slug>⟧ token format. */
export function synthId(i: number): string {
  return `urn:kernel-e4:syn-${String(i).padStart(4, '0')}`;
}

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
