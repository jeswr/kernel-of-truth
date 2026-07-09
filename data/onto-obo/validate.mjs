#!/usr/bin/env node
/**
 * onto-obo corpus validator — re-checks everything checkable WITHOUT the OBO
 * sources (byte-level re-extraction identity lives in the extractor: run twice
 * + diff shard sha256, recorded in README.md).
 *
 * Gates:
 *   - JSONL well-formedness; record shape (schema, semanticStatus, ontology,
 *     kind, oboId, axioms); id == toUrn(oboId); no duplicate ids across shards.
 *   - reference closure: is_a targets whose CURIE prefix is one of our three
 *     ontologies MUST resolve to an emitted record (taxonomy backbone
 *     complete); cross-ontology fillers (CHEBI/CL/PO/...) are allowed and
 *     merely counted.
 *   - logicalDefinition shape + upgradeCandidate consistency.
 *   - provenance completeness (single pin per ontology).
 *   - manifest cross-check: per-ontology counts, shard sha256 (recomputed),
 *     totals (records / withLogicalDef / genusDifferentia).
 *
 * Run: node data/onto-obo/validate.mjs   (exit 0 iff all gates pass)
 */
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { toUrn, curiePrefix } from './extractor/parse-obo.mjs';

const dir = dirname(fileURLToPath(import.meta.url));
const fail = [];
const gate = (ok, msg) => { if (!ok) fail.push(msg); };

const manifest = JSON.parse(readFileSync(join(dir, 'manifest.json'), 'utf8'));
const OUR = new Set(Object.keys(manifest.ontologies)); // {BFO, RO, GO}

const byId = new Map();
const records = [];
const shardText = {};
for (const [id, ont] of Object.entries(manifest.ontologies)) {
  const shard = ont.shard;
  const text = readFileSync(join(dir, shard), 'utf8');
  shardText[shard] = text;
  const lines = text.trim().split('\n');
  gate(lines.length === ont.counts.records,
    `${shard}: ${lines.length} lines != manifest counts.records ${ont.counts.records}`);
  let classes = 0, relations = 0, logicalDef = 0, gd = 0;
  for (const l of lines) {
    let rec;
    try { rec = JSON.parse(l); } catch (e) { fail.push(`${shard}: bad JSON: ${l.slice(0, 80)}`); continue; }
    const where = `${shard}:${rec.oboId}`;
    gate(rec.schema === 'kot-obo/1', `${where}: schema != kot-obo/1`);
    gate(rec.semanticStatus === 'AxiomsOnly', `${where}: semanticStatus != AxiomsOnly`);
    gate(rec.ontology === id, `${where}: ontology field ${rec.ontology} != ${id}`);
    gate(rec.kind === 'class' || rec.kind === 'relation', `${where}: bad kind ${rec.kind}`);
    gate(rec.id === toUrn(rec.oboId), `${where}: id ${rec.id} != toUrn(oboId)`);
    gate(!byId.has(rec.id), `${where}: duplicate id across corpus`);
    byId.set(rec.id, rec);
    gate(Array.isArray(rec.axioms), `${where}: axioms not array`);
    // provenance
    const p = rec.provenance || {};
    gate(p.source && p.sourceVersion && p.extractor && p.extractorVersion && p.extractionDate,
      `${where}: incomplete provenance`);
    gate(p.sourceVersion === ont.sourceVersion, `${where}: provenance pin != manifest`);
    // logical definition
    if (rec.logicalDefinition) {
      logicalDef++;
      const ld = rec.logicalDefinition;
      gate(ld.form === 'obo-genus-differentia', `${where}: bad logicalDefinition.form`);
      gate(Array.isArray(ld.genus) && Array.isArray(ld.differentiae),
        `${where}: logicalDefinition genus/differentiae not arrays`);
      for (const d of ld.differentiae) {
        gate(typeof d.property === 'string' && typeof d.filler === 'string',
          `${where}: bad differentia shape`);
        // kernel-of-truth-8es: each differentia carries a resolved relation URN
        // (source shorthand -> canonical minted relation). Format here; the
        // resolves-to-an-emitted-relation-record gate is in reference-closure.
        gate(typeof d.relation === 'string' && d.relation.startsWith('urn:onto-obo:'),
          `${where}: differentia missing resolved relation URN`);
      }
      const isGd = ld.genus.length >= 1 && ld.differentiae.length >= 1;
      if (isGd) gd++;
      gate(rec.upgradeCandidate === isGd,
        `${where}: upgradeCandidate ${rec.upgradeCandidate} != genus-differentia ${isGd}`);
    } else {
      gate(!('upgradeCandidate' in rec), `${where}: upgradeCandidate without logicalDefinition`);
    }
    if (rec.kind === 'relation') relations++; else classes++;
    records.push(rec);
  }
  gate(classes === ont.counts.classes, `${id}: classes ${classes} != manifest ${ont.counts.classes}`);
  gate(relations === ont.counts.relations, `${id}: relations ${relations} != manifest ${ont.counts.relations}`);
  gate(logicalDef === ont.counts.withLogicalDef, `${id}: logicalDef ${logicalDef} != manifest ${ont.counts.withLogicalDef}`);
  gate(gd === ont.counts.genusDifferentia, `${id}: genus-differentia ${gd} != manifest ${ont.counts.genusDifferentia}`);
  // shard sha256 recompute
  const sha = createHash('sha256').update(text).digest('hex');
  gate(sha === manifest.shards[shard].sha256, `${shard}: sha256 mismatch vs manifest`);
}

// reference closure --------------------------------------------------------
let internalOk = 0, danglingKnown = 0, externalRefs = 0;
const externalByPrefix = {};
const checkTarget = (target, rel, where, backbone) => {
  const oboId = target.replace(/^urn:onto-obo:/, '').replace(/_/, ':');
  const prefix = curiePrefix(oboId);
  if (byId.has(target)) { internalOk++; return; }
  if (OUR.has(prefix)) {
    // a same-family reference that did not resolve
    if (backbone) { danglingKnown++; fail.push(`${where}: ${rel} target ${target} (known prefix) unresolved`); }
    else { danglingKnown++; }
  } else {
    externalRefs++;
    externalByPrefix[prefix || '(bare)'] = (externalByPrefix[prefix || '(bare)'] || 0) + 1;
  }
};
for (const rec of records) {
  const where = rec.oboId;
  for (const ax of rec.axioms) {
    if (ax.target) checkTarget(ax.target, ax.rel, where, ax.rel === 'is_a');
    if (ax.chain) for (const c of ax.chain) checkTarget(c, ax.rel, where, false);
  }
  if (rec.logicalDefinition) {
    for (const g of rec.logicalDefinition.genus) checkTarget(g, 'genus', where, true);
    for (const d of rec.logicalDefinition.differentiae) {
      checkTarget(d.filler, 'differentia', where, false);
      // kernel-of-truth-8es: the resolved relation MUST be an emitted relation
      // record (fail-closed; this is the retired alias table verified at source).
      const rel = byId.get(d.relation);
      gate(rel && rel.kind === 'relation',
        `${where}: differentia relation ${d.relation} is not an emitted relation record`);
    }
  }
}

// totals -------------------------------------------------------------------
gate(records.length === manifest.totals.records, `total records ${records.length} != manifest ${manifest.totals.records}`);

console.log(`onto-obo validate: ${records.length} records, ${byId.size} unique ids`);
console.log(`  reference closure: internal=${internalOk}, dangling-known-prefix=${danglingKnown}, external-cross-ontology=${externalRefs}`);
console.log(`  external prefixes: ${Object.entries(externalByPrefix).sort((a, b) => b[1] - a[1]).slice(0, 12).map(([k, v]) => `${k}:${v}`).join(', ')}`);
if (fail.length) {
  console.error(`\nFAIL (${fail.length}):`);
  for (const f of fail.slice(0, 40)) console.error('  - ' + f);
  process.exit(1);
}
console.log('OK: all gates passed');
