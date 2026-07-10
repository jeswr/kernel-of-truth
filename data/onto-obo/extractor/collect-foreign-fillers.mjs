#!/usr/bin/env node
/**
 * Collect the TARGETED foreign-filler ingestion subset (bead: foreign-filler
 * unlock). Scans the committed onto-obo shards for the DISTINCT foreign-prefix
 * terms referenced as `logicalDefinition.differentiae[].filler` that do NOT
 * resolve to an already-emitted record, and writes the exact per-prefix id-list
 * the streamed subset-filter ingests (`data/onto-obo/foreign-filler-subset.json`).
 *
 * This is the "referenced-by-corpus" seed set the stream-obo.mjs design note
 * leaves as a curation decision: here it is NOT a curation choice but a MECHANICAL
 * derivation — exactly the terms whose absence blocks a genus-differentia
 * definition from resolving under the define-op. The subset is a pure function of
 * the committed shard bytes (sha256 recorded), hence deterministic + re-derivable.
 *
 * Scope: only prefixes with (a) a clean redistributable licence and (b) an
 * available source are emitted as an ingestion subset. HP (restrictive licence)
 * and raw `http:` (HGNC gene registry — a non-OBO bespoke-extractor track) are
 * DIAGNOSED and counted here but NOT ingested (see README "Extraction 6").
 *
 * Run: node data/onto-obo/extractor/collect-foreign-fillers.mjs
 */
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

// Prefixes we ACTUALLY ingest as a streamed reference-stub tier (clean licence +
// available source). Kept in sync with the `stubTier` ONTOLOGIES entries in
// extract.mjs. Everything else referenced is diagnosed but not ingested.
const INGEST_PREFIXES = ['CHEBI', 'NCBITaxon'];

const shardFiles = readdirSync(ROOT).filter((f) => f.endsWith('.jsonl') && f !== 'minted-urns.jsonl');

const emitted = new Set();
const records = [];
const shardSha = {};
for (const f of shardFiles.sort()) {
  const text = readFileSync(join(ROOT, f), 'utf8');
  shardSha[f] = 'sha256:' + createHash('sha256').update(text).digest('hex');
  for (const line of text.trim().split('\n')) {
    if (!line) continue;
    const r = JSON.parse(line);
    emitted.add(r.id);
    records.push(r);
  }
}

const toCurie = (urn) => urn.replace(/^urn:onto-obo:/, '').replace(/_/, ':');
const prefixOf = (curie) => { const i = curie.indexOf(':'); return i < 0 ? '(bare)' : curie.slice(0, i); };

// Distinct UNRESOLVED differentia fillers, by prefix.
const byPrefix = {};       // prefix -> Set(curie)
const occByPrefix = {};    // prefix -> occurrence count
for (const r of records) {
  if (!r.logicalDefinition) continue;
  for (const d of r.logicalDefinition.differentiae || []) {
    if (emitted.has(d.filler)) continue;
    const curie = toCurie(d.filler);
    const p = prefixOf(curie);
    (byPrefix[p] ??= new Set()).add(curie);
    occByPrefix[p] = (occByPrefix[p] || 0) + 1;
  }
}

const diagnosis = {};
for (const p of Object.keys(byPrefix).sort()) {
  diagnosis[p] = { distinct: byPrefix[p].size, occurrences: occByPrefix[p], ingested: INGEST_PREFIXES.includes(p) };
}

const subsets = {};
for (const p of INGEST_PREFIXES) {
  subsets[p] = [...(byPrefix[p] || new Set())].sort();
}

const out = {
  _note:
    'TARGETED foreign-filler ingestion subset for the onto-obo reference-stub tier. '
    + 'Mechanically derived (referenced-by-corpus): the exact foreign-prefix terms referenced '
    + 'as genus-differentia fillers that do not already resolve to an emitted record. '
    + 'Consumed by extract.mjs (stubTier ONTOLOGIES entries) as the streamed subset id-list. '
    + 'Regenerate: node data/onto-obo/extractor/collect-foreign-fillers.mjs.',
  generatedFromShards: shardSha,
  ingestPrefixes: INGEST_PREFIXES,
  diagnosisAllUnresolvedFillerPrefixes: diagnosis,
  subsets,
  counts: Object.fromEntries(INGEST_PREFIXES.map((p) => [p, subsets[p].length])),
};
writeFileSync(join(ROOT, 'foreign-filler-subset.json'), JSON.stringify(out, null, 2) + '\n');

console.log('foreign-filler-subset.json written.');
for (const p of Object.keys(diagnosis)) {
  const d = diagnosis[p];
  console.log(`  ${p.padEnd(12)} distinct=${String(d.distinct).padStart(5)} occ=${String(d.occurrences).padStart(5)} ingested=${d.ingested}`);
}
console.log('ingest subset sizes:', JSON.stringify(out.counts));
