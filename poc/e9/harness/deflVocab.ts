/**
 * E9-defl scrambled-explication vocabulary (poc/e9/README.md pinned
 * construction; bead kernel-of-truth-xj2).
 *
 * For each of the 524 E5 concepts: ONE structure-matched, semantically
 * unrelated explication from the SAME seeded generator that built the E4/E5
 * synthetic vocabulary. Seed `e9/defl/<slug>` (+ `/retry<k>`); sizes matched
 * to the TRUE explication (generator params for synthetics; the pinned
 * authoredSizeProxy for the 54 authored — README J2/J3). Dedup against ALL
 * true ASTs and other scrambles, fail closed; every scramble re-validated.
 */

import {
  canonicalJson,
  generateExplication,
  validateExplication,
} from '@jeswr/kernel-encoder';
import type { Explication } from '@jeswr/kernel-encoder';
import {
  authoredSizeProxy,
  isMain,
  loadE4Synthetics,
  loadKernelV0,
  readE5Input,
  sha256Hex,
  slugOf,
  writeInput,
} from './common.js';

export interface DeflRecord {
  readonly id: string;          // the TRUE concept id this scramble replaces
  readonly seed: string;
  readonly topClauses: number;
  readonly depth: number;
  readonly sizeSource: 'generator-record' | 'authored-proxy';
  readonly retries: number;
  readonly astSha256: string;
  readonly explication: Explication;
}

interface E5Concepts {
  artifact: string;
  ids: string[];
  roles: string[];
  e4SyntheticsSha256: string;
}

export function buildDeflVocab(): {
  records: DeflRecord[];
  trueAstShas: Map<string, string>;
  e5ConceptsIds: string[];
  e4SyntheticsSha256: string;
} {
  const e5 = readE5Input<E5Concepts>('e5-concepts.json');
  if (e5.artifact !== 'e5-concepts') throw new Error('ERR_ARTIFACT: e5-concepts.json');
  const authored = loadKernelV0();
  const { records: synth, fileSha256 } = loadE4Synthetics();
  if (fileSha256 !== e5.e4SyntheticsSha256) {
    throw new Error('ERR_SYNTH_PIN: e4 synthetic-concepts.json sha changed since E5 selection');
  }
  const authoredById = new Map(authored.map((r) => [r.id, r]));
  const synthById = new Map(synth.map((r) => [r.id, r]));

  // True-AST shas (dedup universe) + per-concept size parameters.
  const trueAstShas = new Map<string, string>();
  const sizes = new Map<string, { topClauses: number; depth: number; sizeSource: DeflRecord['sizeSource'] }>();
  for (const id of e5.ids) {
    const syn = synthById.get(id);
    if (syn !== undefined) {
      trueAstShas.set(id, sha256Hex(canonicalJson(syn.explication)));
      sizes.set(id, { topClauses: syn.topClauses, depth: syn.depth, sizeSource: 'generator-record' });
      continue;
    }
    const au = authoredById.get(id);
    if (au === undefined) throw new Error(`ERR_CONCEPT: ${id} in neither kernel-v0 nor e4 synthetics`);
    const e = au.explication as Explication;
    trueAstShas.set(id, sha256Hex(canonicalJson(e)));
    sizes.set(id, { ...authoredSizeProxy(e as unknown as { clauses: unknown[] }), sizeSource: 'authored-proxy' });
  }

  const taken = new Set<string>(trueAstShas.values());
  const records: DeflRecord[] = [];
  for (const id of e5.ids) {
    const { topClauses, depth, sizeSource } = sizes.get(id)!;
    for (let attempt = 0; ; attempt++) {
      const seed = attempt === 0 ? `e9/defl/${slugOf(id)}` : `e9/defl/${slugOf(id)}/retry${attempt}`;
      const explication = generateExplication({ seed, topClauses, depth });
      validateExplication(explication); // fail closed at the artifact boundary
      const astSha256 = sha256Hex(canonicalJson(explication));
      if (taken.has(astSha256)) continue; // collision with a true AST or another scramble
      taken.add(astSha256);
      records.push({ id, seed, topClauses, depth, sizeSource, retries: attempt, astSha256, explication });
      break;
    }
  }
  return { records, trueAstShas, e5ConceptsIds: e5.ids, e4SyntheticsSha256: fileSha256 };
}

function main(): void {
  const { records, trueAstShas, e5ConceptsIds, e4SyntheticsSha256 } = buildDeflVocab();
  const retried = records.filter((r) => r.retries > 0).length;
  const bySource = { 'generator-record': 0, 'authored-proxy': 0 };
  for (const r of records) bySource[r.sizeSource]++;
  console.log(
    `built ${records.length} scrambles (${bySource['generator-record']} generator-exact, ` +
      `${bySource['authored-proxy']} authored-proxy; ${retried} needed retries)`,
  );
  writeInput('defl-concepts.json', {
    artifact: 'e9-defl-concepts',
    date: new Date().toISOString(),
    construction:
      'poc/e9/README.md pinned construction: seed e9/defl/<slug> (+/retry<k>), sizes matched to ' +
      'the TRUE explication (generator params for synthetics, authoredSizeProxy for authored — ' +
      'J2/J3); pure prime structures; dedup vs all true ASTs + other scrambles, fail closed',
    e4SyntheticsSha256,
    counts: { total: records.length, ...bySource, retried },
    ids: e5ConceptsIds,
    trueAstShas: Object.fromEntries(trueAstShas),
    records,
  });
}

if (isMain(import.meta.url)) main();
