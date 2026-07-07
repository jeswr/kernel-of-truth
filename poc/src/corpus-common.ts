/**
 * Shared corpus plumbing for the kernel-v0 re-runs of the Phase-X harnesses
 * (bead kernel-of-truth-138). NEW entry points on the AUTHORED corpus
 * (data/kernel-v0); the seeded-synthetic harnesses in poc/harness/*.ts are
 * left untouched and their reports/checkpoints are not written by anything
 * in poc/src/. Build with tsconfig.corpus.json (outDir dist-corpus/) so the
 * running dist/ tree is never recompiled underneath a live run.
 */

import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, readdirSync, renameSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  canonicalJson,
  mutateExplication,
  type EditType,
  type Explication,
} from '@jeswr/kernel-encoder';

// Compiled layout is poc/dist-corpus/src/*.js — poc/ is two levels up.
export const POC_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
export const RESULTS_DIR = join(POC_DIR, 'results');
export const CORPUS_DIR = join(POC_DIR, '..', 'data', 'kernel-v0');

export interface ConceptDoc {
  readonly id: string;
  readonly label: string;
  readonly status: string;
  readonly gloss: string;
  readonly notes?: string;
  readonly references: readonly string[];
  readonly explication: Explication;
}

export interface Corpus {
  readonly docs: readonly ConceptDoc[];
  readonly defs: ReadonlyMap<string, Explication>;
  readonly manifest: {
    readonly corpus: string;
    readonly encoderContentHash: string;
    readonly conceptCount: number;
    readonly referenceBearing: readonly string[];
    readonly knownWeak: readonly string[];
    readonly maxReferenceDepth: number;
  };
  /** sha256 over the manifest bytes. */
  readonly manifestSha256: string;
  /** sha256 over sorted "«file»:«sha256(file)»\n" lines of concepts/*.json + manifest.json. */
  readonly corpusContentHash: string;
}

export function loadCorpus(): Corpus {
  const manifestBytes = readFileSync(join(CORPUS_DIR, 'manifest.json'));
  const manifest = JSON.parse(manifestBytes.toString('utf8')) as Corpus['manifest'];
  const files = readdirSync(join(CORPUS_DIR, 'concepts'))
    .filter((f) => f.endsWith('.json'))
    .sort();
  const hasher = createHash('sha256');
  const docs: ConceptDoc[] = [];
  for (const f of files) {
    const bytes = readFileSync(join(CORPUS_DIR, 'concepts', f));
    hasher.update(`${f}:${createHash('sha256').update(bytes).digest('hex')}\n`);
    docs.push(JSON.parse(bytes.toString('utf8')) as ConceptDoc);
  }
  hasher.update(`manifest.json:${createHash('sha256').update(manifestBytes).digest('hex')}\n`);
  return {
    docs,
    defs: new Map(docs.map((d) => [d.id, d.explication])),
    manifest,
    manifestSha256: createHash('sha256').update(manifestBytes).digest('hex'),
    corpusContentHash: hasher.digest('hex'),
  };
}

export function slug(id: string): string {
  return id.replace('urn:kernel-v0:', '');
}

export interface Neighbour {
  readonly mutant: Explication;
  readonly edit: EditType;
  readonly detail: string;
  /** First seed index (of `x1c/<id>/<s>`) that produced this mutant. */
  readonly firstSeed: number;
}

export interface NeighbourSet {
  readonly neighbours: readonly Neighbour[];
  readonly seedsUsed: number;
  /** Last seed index at which a NEW distinct mutant appeared. */
  readonly lastNewSeed: number;
  /** True iff the stop was the saturation rule, not the hard seed cap. */
  readonly saturated: boolean;
}

/**
 * Enumerate the single-edit neighbours of an authored explication via the
 * encoder package's own seeded mutator (synth.ts mutateExplication — the same
 * edit model as X1: operator-flip / clause-swap / referent-index /
 * filler-substitution), deduped by canonical JSON. The mutator samples ONE
 * valid edit per seed, so exhaustiveness is empirical: we draw seeds until no
 * new distinct mutant has appeared for max(500, 4×distinct-so-far)
 * consecutive seeds (or the hard cap), and report saturation. Deterministic:
 * seed family `x1c/<concept-id>/<s>`.
 */
export function enumerateNeighbours(e: Explication, id: string, maxSeeds = 6000): NeighbourSet {
  const seen = new Map<string, Neighbour>();
  let lastNewSeed = -1;
  let s = 0;
  for (; s < maxSeeds; s++) {
    const window = Math.max(500, 4 * seen.size);
    if (s - lastNewSeed > window) break;
    const m = mutateExplication(e, `x1c/${id}/${s}`);
    if (m === null) continue;
    const key = canonicalJson(m.mutant);
    if (!seen.has(key)) {
      seen.set(key, { mutant: m.mutant, edit: m.edit, detail: m.detail, firstSeed: s });
      lastNewSeed = s;
    }
  }
  return {
    neighbours: [...seen.values()],
    seedsUsed: s,
    lastNewSeed,
    saturated: s < maxSeeds,
  };
}

/**
 * Checkpoint helpers anchored at poc/results/ (harness/common.js's
 * loadCheckpoint/saveCheckpoint resolve RESULTS_DIR relative to ITS compiled
 * location, which under dist-corpus/ would point at dist-corpus/results).
 */
export function loadCorpusCheckpoint<T>(name: string): T | null {
  try {
    return JSON.parse(readFileSync(join(RESULTS_DIR, name), 'utf8')) as T;
  } catch {
    return null; // absent or corrupt: start over (harness re-derives everything)
  }
}

export function saveCorpusCheckpoint(name: string, state: unknown): void {
  mkdirSync(RESULTS_DIR, { recursive: true });
  const file = join(RESULTS_DIR, name);
  writeFileSync(`${file}.tmp`, JSON.stringify(state));
  renameSync(`${file}.tmp`, file);
}

export function writeCorpusReport(baseName: string, json: unknown, markdown: string): void {
  mkdirSync(RESULTS_DIR, { recursive: true });
  writeFileSync(join(RESULTS_DIR, `${baseName}.json`), JSON.stringify(json, null, 2));
  writeFileSync(join(RESULTS_DIR, `${baseName}.md`), markdown);
  console.log(`wrote ${join(RESULTS_DIR, baseName)}.{json,md}`);
}

/** Report stamp shared by all four corpus reports. */
export function corpusStamp(corpus: Corpus, encoderContentHash: string): Record<string, unknown> {
  return {
    date: new Date().toISOString(),
    corpus: 'kernel-v0 (authored; research-grade, NOT federation-endorsed)',
    conceptCount: corpus.docs.length,
    encoderContentHash,
    manifestPinnedEncoderHash: corpus.manifest.encoderContentHash,
    encoderHashMatchesManifest: corpus.manifest.encoderContentHash === encoderContentHash,
    corpusManifestSha256: corpus.manifestSha256,
    corpusContentHash: corpus.corpusContentHash,
  };
}

export function stampMd(stamp: Record<string, unknown>): string[] {
  return [
    `date: ${String(stamp.date)}`,
    `corpus: ${String(stamp.corpus)} — ${String(stamp.conceptCount)} concepts`,
    `encoder content-hash: \`${String(stamp.encoderContentHash)}\` (matches manifest pin: ${String(stamp.encoderHashMatchesManifest)})`,
    `corpus manifest sha256: \`${String(stamp.corpusManifestSha256)}\``,
    `corpus content-hash (concepts/*.json + manifest): \`${String(stamp.corpusContentHash)}\``,
  ];
}
