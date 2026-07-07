/**
 * Shared utilities for the E1 prep harness (docs/poc-design.md Phase E, E1;
 * bead kernel-of-truth-bk0).
 *
 * Self-contained on purpose (same policy as poc/e2/harness/common.ts): the
 * brief forbids touching encoder/, mapper/ internals, poc/e2 and the Phase-X
 * harnesses, so the few duplicated helpers (corpusPin, sha256Hex, isMain)
 * are copied here rather than imported across package boundaries.
 */

import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Compiled layout is poc/e1/dist/harness/*.js, so poc/e1/ is two levels up.
export const E1_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
export const INPUTS_DIR = join(E1_DIR, 'inputs');
export const REPO_DIR = join(E1_DIR, '..', '..');
export const KERNEL_V0_DIR = join(REPO_DIR, 'data', 'kernel-v0');
export const MAPPER_DIR = join(REPO_DIR, 'mapper');

/**
 * The pinned kot-enc-Bq/1 content hash at D=512 (docs/poc-design.md Common
 * rule 2, pinned 2026-07-07 before any E-run). Every vector-table artifact is
 * verified against this at generation time and stamped with it; a mismatch is
 * an encoder version change and FAILS CLOSED (new pre-registration required).
 */
export const PINNED_BQ512_HASH =
  '3492799ed73b49a612bebca920421041edd31d7bd4098bcf55da52df127ab9ee';

/** E1 model dimension: d_model = 512, chosen to use the pinned Bq@512 hash. */
export const E1_D_MODEL = 512;

/**
 * Documented trainable-arm embedding init distribution (Common rule 4:
 * random-frozen is "i.i.d., norm-matched to the trainable arm's init
 * distribution"). GPT-2 initialisation: N(0, 0.02^2) per element.
 */
export const INIT_STD = 0.02;

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

/** Corpus pin for data/kernel-v0 — verbatim policy of poc/e2/harness/common.ts. */
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

/** Provenance stamp for mapper-derived artifacts: package version + source hashes. */
export function mapperPin(): { version: string; srcSha256: Record<string, string> } {
  const pkg = JSON.parse(readFileSync(join(MAPPER_DIR, 'package.json'), 'utf8')) as {
    version: string;
  };
  const src: Record<string, string> = {};
  // policy.ts joined the pin under Amendment A1 (the a1-hybrid preset sits on
  // E1's critical path).
  for (const f of [
    'lexicon.ts',
    'lemmatize.ts',
    'tokenize.ts',
    'mapper.ts',
    'primes.ts',
    'policy.ts',
  ]) {
    src[f] = sha256Hex(readFileSync(join(MAPPER_DIR, 'src', f)));
  }
  return { version: pkg.version, srcSha256: src };
}

export interface ConceptRecord {
  readonly id: string;
  readonly label: string;
  readonly gloss: string;
}

/** Load the kernel-v0 concept records (read-only), alphabetical by filename/slug. */
export function loadConcepts(): ConceptRecord[] {
  const dir = join(KERNEL_V0_DIR, 'concepts');
  const files = readdirSync(dir).filter((f) => f.endsWith('.json')).sort();
  return files.map((f) => JSON.parse(readFileSync(join(dir, f), 'utf8')) as ConceptRecord);
}

export function slugOf(id: string): string {
  return id.replace(/^urn:kernel-v0:/, '');
}
