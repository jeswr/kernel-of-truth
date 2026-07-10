#!/usr/bin/env node
/**
 * A-E2 English m̂ sampler (Tier-0, r0-local-cpu; $0, no model calls).
 *
 * Per ASM-0461: "m-hat handling = sampled with the English-only a1-hybrid
 * mapper on English cells". This script runs the PINNED a1-hybrid mapper
 * (kernel-mapper (mapper/ package), policy SHADOWED_HYBRID_RECOMMENDED / A1_POLICY_SHA256
 * e13dc838…, kernel-v0 manifest) over each English candidate surface and
 * records the mapper's decision kind. The census (run-a-e2.py) derives m̂
 * from those kinds; the raw per-surface kind is emitted here so m̂ can be
 * re-derived under any rule without re-running the mapper.
 *
 * Operationalisation of m̂ (DISCLOSED, MEASURED-exploratory):
 *   m̂(s) = 0  iff the a1-hybrid mapper ABSTAINS on surface s (the surface
 *              collides with ≥2 lexicon exponents — the measured K-A4
 *              shadowing/polysemy failure mode, e.g. lie/right/take, broken/
 *              break, lost/lose);
 *   m̂(s) = 1  otherwise (concept | prime | none — resolvable, or no collision
 *              with the current 119-entry a1-hybrid lexicon).
 * CAVEAT (disclosed by the census): the a1-hybrid lexicon is small, so
 * collision-detection only fires for surfaces that clash with its 54 concepts
 * + 65 primes; polysemy invisible to that lexicon is NOT discounted. English
 * m̂ is therefore itself an UPPER bound on true mappable engagement (tighter
 * than membership only where a collision is detected).
 *
 * Usage: node compute-mhat.mjs <surfaces.txt> <out.jsonl>
 *   surfaces.txt: one surface per line (English wordfreq keys).
 */
import { readFileSync, writeFileSync, createWriteStream } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  buildLexicon,
  loadManifestConcepts,
  mapText,
  policyHash,
  SHADOWED_HYBRID_RECOMMENDED,
  A1_POLICY_SHA256,
  A1_PRESET_NAME,
} from '../../mapper/dist/src/index.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..');
const MANIFEST = join(REPO, 'data', 'kernel-v0', 'manifest.json');

const [, , surfacesPath, outPath] = process.argv;
if (!surfacesPath || !outPath) {
  console.error('usage: compute-mhat.mjs <surfaces.txt> <out.jsonl>');
  process.exit(1);
}

const lexicon = buildLexicon(loadManifestConcepts(MANIFEST));
const policy = SHADOWED_HYBRID_RECOMMENDED;
const ph = policyHash(policy);
if (ph !== A1_POLICY_SHA256) {
  console.error(`FAIL-CLOSED: a1-hybrid policy hash ${ph} != pin ${A1_POLICY_SHA256}`);
  process.exit(2);
}

const surfaces = readFileSync(surfacesPath, 'utf8').split('\n').filter((l) => l.length > 0);

// classify a surface by the mapper's decision over its content tokens.
// abstain if ANY content token abstains; else concept>prime>none precedence.
function classify(surface) {
  let anns;
  try {
    anns = mapText(surface, lexicon, policy);
  } catch (e) {
    return 'error';
  }
  const kinds = anns.map((t) => t.decision.kind);
  if (kinds.includes('abstain')) return 'abstain';
  if (kinds.includes('concept')) return 'concept';
  if (kinds.includes('prime')) return 'prime';
  return 'none';
}

const out = createWriteStream(outPath, { encoding: 'utf8' });
const counts = { concept: 0, prime: 0, abstain: 0, none: 0, error: 0 };
let n = 0;
for (const s of surfaces) {
  const kind = classify(s);
  counts[kind] = (counts[kind] ?? 0) + 1;
  out.write(JSON.stringify({ s, kind }) + '\n');
  n += 1;
}
out.end();

const meta = {
  script: 'poc/a-e2/compute-mhat.mjs',
  mapper_pkg: 'kernel-mapper (mapper/ package)@0.1.0',
  policy_preset: A1_PRESET_NAME,
  policy_sha256: ph,
  kernel_manifest: 'data/kernel-v0/manifest.json',
  surfaces_in: n,
  decision_kind_counts: counts,
};
writeFileSync(outPath.replace(/\.jsonl$/, '') + '.meta.json', JSON.stringify(meta, null, 2));
console.error('mhat done:', JSON.stringify(counts), 'n=', n);
