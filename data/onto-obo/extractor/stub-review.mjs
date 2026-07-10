#!/usr/bin/env node
/**
 * Reference-stub-tier audit (Extraction 6), the streaming complement to
 * sample-review.mjs. sample-review re-derives whole-file shards by loading the
 * source as a single string — impossible for the 662 MB NCBITaxon source (Node's
 * max string length). This auditor instead streams each stub-tier source ONCE
 * (O(subset) memory), collecting the source's name/def/obsolete for the subset
 * ids, and checks EVERY emitted stub (not a random sample — the tier is small):
 *   - label            == the source `name`
 *   - definition-presence matches the source `def:`
 *   - the source stanza is NOT obsolete
 *   - the emitted id is in the declared subset (foreign-filler-subset.json)
 *   - stub invariants: axioms == [] and no logicalDefinition/upgradeCandidate
 * Also asserts every declared subset id was emitted (no silent drop). Any mismatch
 * is an error; exit 0 iff 0 errors. Requires source/ present.
 *
 * Usage: nice -n 10 node data/onto-obo/extractor/stub-review.mjs
 */
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { streamStanzas } from './stream-obo.mjs';
import { tagMap } from './parse-obo.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(ROOT, 'source');

const manifest = JSON.parse(readFileSync(join(ROOT, 'manifest.json'), 'utf8'));
const subset = JSON.parse(readFileSync(join(ROOT, 'foreign-filler-subset.json'), 'utf8')).subsets;

// Stub-tier ontologies = those the manifest marks stubTier:true.
const stubOnts = Object.entries(manifest.ontologies)
  .filter(([, o]) => o.stubTier)
  .map(([id, o]) => ({ id, shard: o.shard, file: manifest.ontologies[id].purl.split('/').pop() }));

let errors = 0;
const log = [];
for (const { id, shard } of stubOnts) {
  const file = { CHEBI: 'chebi.obo', NCBITaxon: 'ncbitaxon.obo' }[id];
  const srcPath = join(SRC, file);
  if (!existsSync(srcPath)) throw new Error(`ERR_SOURCE_MISSING: ${file} (re-download per README)`);

  const emitted = new Map();
  for (const l of readFileSync(join(ROOT, shard), 'utf8').trim().split('\n')) {
    if (!l) continue;
    const r = JSON.parse(l);
    emitted.set(r.oboId, r);
  }
  const want = new Set(subset[id] || []);

  const srcTruth = new Map();
  streamStanzas(srcPath, {
    onStanza: (st) => {
      if (st.type !== 'Term') return;
      const m = tagMap(st);
      const idv = m.get('id');
      if (!idv || idv.length === 0) return;
      const oboId = idv[0].trim();
      if (!want.has(oboId)) return;
      srcTruth.set(oboId, {
        name: m.has('name') ? m.get('name')[0] : null,
        hasDef: m.has('def'),
        obsolete: (m.get('is_obsolete') || []).some((v) => v.trim() === 'true'),
      });
    },
  });

  for (const [oboId, rec] of emitted) {
    const problems = [];
    if (!want.has(oboId)) problems.push('emitted id not in declared subset');
    if (rec.axioms.length !== 0) problems.push(`non-empty axioms ${JSON.stringify(rec.axioms)}`);
    if (rec.logicalDefinition) problems.push('has logicalDefinition');
    if ('upgradeCandidate' in rec) problems.push('has upgradeCandidate');
    const s = srcTruth.get(oboId);
    if (!s) problems.push('not found in source');
    else {
      if (s.obsolete) problems.push('source obsolete but emitted');
      if ((s.name || null) !== (rec.annotations.label || null)) problems.push(`label "${rec.annotations.label}" != src "${s.name}"`);
      if (s.hasDef !== !!rec.annotations.definition) problems.push(`def presence rec ${!!rec.annotations.definition} vs src ${s.hasDef}`);
    }
    if (problems.length) { errors++; log.push(`${oboId}: ${problems.join('; ')}`); }
  }
  const missing = [...want].filter((x) => !emitted.has(x));
  if (missing.length) { errors += missing.length; log.push(`${id}: ${missing.length} subset ids NOT emitted -> ${missing.slice(0, 8).join(', ')}`); }
  console.log(`${id}: audited ${emitted.size} stubs (subset ${want.size}), missing=${missing.length}`);
}

console.log(`onto-obo stub-review: errors=${errors}`);
for (const e of log.slice(0, 30)) console.log('  ERR ' + e);
process.exit(errors === 0 ? 0 : 1);
