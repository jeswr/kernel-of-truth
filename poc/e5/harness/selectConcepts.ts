/**
 * E5 concept selection (README O2; docs/poc-design.md E5 rev 2; bead
 * kernel-of-truth-c24).
 *
 * SEEN = all 54 authored kernel-v0 concepts + 446 synthetics; NONCE = 24
 * synthetics drawn from the structurally pre-filtered pool (depth >= 2 AND
 * topClauses >= 2 — pinned in README O2 BEFORE any run; the filter is on
 * pre-hoc AST structure only). Selection is seeded (DetStream labels
 * `e5/select/nonce`, `e5/select/seen`), nonces drawn FIRST, seen synthetics
 * from the remainder. Emits inputs/e5-concepts.json with the compositional
 * descriptive split (feature definition copied verbatim from E4).
 */

import type { Explication } from '@jeswr/kernel-encoder';
import {
  N_NONCE,
  N_SEEN_SYNTH,
  NONCE_MIN_DEPTH,
  NONCE_MIN_TOP_CLAUSES,
  corpusPin,
  featureSet,
  isMain,
  loadE4Synthetics,
  loadKernelV0,
  seededSample,
  slugOf,
  writeInput,
} from './common.js';

export const SELECT_NONCE_LABEL = 'e5/select/nonce';
export const SELECT_SEEN_LABEL = 'e5/select/seen';

export interface E5Concepts {
  artifact: 'e5-concepts';
  date: string;
  kernelV0: ReturnType<typeof corpusPin>;
  e4SyntheticsSha256: string;
  selection: {
    nonceLabel: string;
    seenLabel: string;
    nonceFilter: string;
    nonceFilterPoolSize: number;
  };
  counts: { seenAuthored: number; seenSynthetic: number; nonce: number; total: number };
  /** Row order of every vector table: seen authored (alphabetical), seen
   * synthetic (synth index order), nonce (synth index order). */
  ids: string[];
  roles: ('seen-authored' | 'seen-synthetic' | 'nonce')[];
  slugs: string[];
  composition: Record<
    string,
    { sharesStructureWithSeen: boolean; featureCoverage: number; features: number }
  >;
}

export function buildConcepts(): E5Concepts {
  const authored = loadKernelV0();
  const { records: synth, fileSha256 } = loadE4Synthetics();

  // ---- nonce pool: structural pre-filter (README O2, pinned) ---------------
  const pool = synth.filter(
    (r) => r.depth >= NONCE_MIN_DEPTH && r.topClauses >= NONCE_MIN_TOP_CLAUSES,
  );
  const nonce = seededSample(SELECT_NONCE_LABEL, pool.map((r) => r.id), N_NONCE)
    .slice()
    .sort();
  const nonceSet = new Set(nonce);

  // ---- seen synthetics: from ALL synthetics not chosen as nonces -----------
  const seenPool = synth.map((r) => r.id).filter((id) => !nonceSet.has(id));
  const seenSynth = seededSample(SELECT_SEEN_LABEL, seenPool, N_SEEN_SYNTH).slice().sort();

  const seenAuthored = authored.map((r) => r.id); // alphabetical by slug already
  const ids = [...seenAuthored, ...seenSynth, ...nonce];
  if (new Set(ids).size !== ids.length) throw new Error('ERR_IDS: duplicate concept ids');
  const roles: E5Concepts['roles'] = [
    ...seenAuthored.map(() => 'seen-authored' as const),
    ...seenSynth.map(() => 'seen-synthetic' as const),
    ...nonce.map(() => 'nonce' as const),
  ];

  // ---- compositional descriptive split (E4 feature definition, verbatim) ---
  const explications = new Map<string, Explication>();
  for (const r of authored) explications.set(r.id, r.explication as Explication);
  for (const r of synth) explications.set(r.id, r.explication);
  const seenFeatures = new Set<string>();
  for (const id of [...seenAuthored, ...seenSynth]) {
    for (const f of featureSet(explications.get(id)!)) seenFeatures.add(f);
  }
  const composition: E5Concepts['composition'] = {};
  for (const id of nonce) {
    const fs = featureSet(explications.get(id)!);
    let covered = 0;
    for (const f of fs) if (seenFeatures.has(f)) covered++;
    composition[id] = {
      sharesStructureWithSeen: covered === fs.size,
      featureCoverage: covered / fs.size,
      features: fs.size,
    };
  }

  return {
    artifact: 'e5-concepts',
    date: new Date().toISOString(),
    kernelV0: corpusPin(),
    e4SyntheticsSha256: fileSha256,
    selection: {
      nonceLabel: SELECT_NONCE_LABEL,
      seenLabel: SELECT_SEEN_LABEL,
      nonceFilter: `depth >= ${NONCE_MIN_DEPTH} AND topClauses >= ${NONCE_MIN_TOP_CLAUSES} (pre-hoc AST structure only; README O2)`,
      nonceFilterPoolSize: pool.length,
    },
    counts: {
      seenAuthored: seenAuthored.length,
      seenSynthetic: seenSynth.length,
      nonce: nonce.length,
      total: ids.length,
    },
    ids,
    roles,
    slugs: ids.map(slugOf),
    composition,
  };
}

function main(): void {
  const c = buildConcepts();
  const shared = Object.values(c.composition).filter((x) => x.sharesStructureWithSeen).length;
  console.log(
    `selected ${c.counts.total} concepts: ${c.counts.seenAuthored} authored + ` +
      `${c.counts.seenSynthetic} seen synthetic + ${c.counts.nonce} nonce ` +
      `(pool ${c.selection.nonceFilterPoolSize}; compositional shared ${shared}/${c.counts.nonce})`,
  );
  writeInput('e5-concepts.json', c);
}

if (isMain(import.meta.url)) main();
