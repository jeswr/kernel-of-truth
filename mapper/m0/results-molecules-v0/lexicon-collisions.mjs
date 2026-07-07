#!/usr/bin/env node
/**
 * Mapper-lexicon implication measurement for molecules-v0 (measured, not
 * guessed; the mapper DEFAULT is not changed — this builds a throwaway
 * lexicon in memory via the mapper's own buildLexicon and diffs ambiguity).
 *
 * Question: if the 54 molecules-v0 labels (and, secondarily, their synonym
 * surfaces from corpusLemmas) were added to the mapper lexicon, how many
 * surface phrases would become ambiguous (>1 distinct target), beyond the
 * ambiguity the kernel+prime lexicon already has?
 *
 * Usage: node mapper/m0/results-molecules-v0/lexicon-collisions.mjs
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildLexicon, loadManifestConcepts, targetKey } from '../../dist/src/index.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..', '..');

const kernel = loadManifestConcepts(join(REPO, 'data', 'kernel-v0', 'manifest.json'));
const molManifest = JSON.parse(
  readFileSync(join(REPO, 'data', 'molecules-v0', 'manifest.json'), 'utf8'),
);
const molLabels = molManifest.molecules.map((m) => ({ id: m.id, label: m.label }));
// synonym surfaces = corpusLemmas minus the label itself
const molSynonyms = molManifest.molecules.flatMap((m) =>
  m.corpusLemmas.filter((l) => l !== m.label).map((l) => ({ id: m.id, label: l })),
);

function ambiguity(lex) {
  const bySurface = new Map(); // surface phrase -> Set(targetKey)
  for (const e of lex.entries) {
    const s = e.phrase.join(' ');
    if (!bySurface.has(s)) bySurface.set(s, new Set());
    bySurface.get(s).add(targetKey(e.target));
  }
  const collisions = new Map();
  for (const [s, targets] of bySurface) {
    if (targets.size > 1) collisions.set(s, [...targets].sort());
  }
  return collisions;
}

const base = ambiguity(buildLexicon(kernel));
const withLabels = ambiguity(buildLexicon([...kernel, ...molLabels]));
const withAll = ambiguity(buildLexicon([...kernel, ...molLabels, ...molSynonyms]));

function diff(next, prev) {
  const out = {};
  for (const [s, targets] of next) {
    const before = prev.get(s);
    if (!before || before.length !== targets.length) out[s] = targets;
  }
  return out;
}

const report = {
  experiment: 'molecules-v0 mapper-lexicon collision measurement',
  date: '2026-07-07',
  method: 'mapper buildLexicon (dist) over kernel-v0 manifest + molecules-v0 manifest; a collision = one surface phrase with >1 distinct target; mapper default untouched',
  baselineKernelPrime: {
    entries: buildLexicon(kernel).entries.length,
    ambiguousSurfaces: base.size,
    surfaces: Object.fromEntries(base),
  },
  plusMoleculeLabels: {
    added: molLabels.length,
    ambiguousSurfaces: withLabels.size,
    newCollisions: diff(withLabels, base),
  },
  plusSynonymSurfaces: {
    added: molSynonyms.length,
    synonymSurfaces: molSynonyms.map((s) => `${s.label}->${s.id}`),
    ambiguousSurfaces: withAll.size,
    newCollisionsVsLabels: diff(withAll, withLabels),
  },
};

writeFileSync(join(HERE, 'lexicon-collisions.json'), `${JSON.stringify(report, null, 2)}\n`);
const nLabels = Object.keys(report.plusMoleculeLabels.newCollisions).length;
const nSyn = Object.keys(report.plusSynonymSurfaces.newCollisionsVsLabels).length;
console.log(`baseline ambiguous surfaces: ${base.size}`);
console.log(`+${molLabels.length} molecule labels: ${withLabels.size} ambiguous (${nLabels} new): ${JSON.stringify(report.plusMoleculeLabels.newCollisions)}`);
console.log(`+${molSynonyms.length} synonym surfaces: ${withAll.size} ambiguous (${nSyn} new vs labels): ${JSON.stringify(report.plusSynonymSurfaces.newCollisionsVsLabels)}`);
