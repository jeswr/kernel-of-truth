#!/usr/bin/env node
/**
 * OBO Foundry -> onto-obo AxiomsOnly tier extractor (kernel-of-truth-cgh).
 *
 * Sources (source/, gitignored; re-download per README):
 *   bfo.obo  Basic Formal Ontology (foundational upper ontology; classes)
 *   ro.obo   Relation Ontology (the relation vocabulary OBO ontologies share)
 *   go.obo   Gene Ontology (domain exemplar; heavy genus-differentia logic)
 *
 * Honesty architecture (docs/design-bulk-kernel.md; gist §3.1):
 *   - semanticStatus: AxiomsOnly — structural axioms mechanically extracted
 *     from a fixed source; NO semantic-adequacy claim.
 *   - identity surface = {schema, semanticStatus, ontology, kind, oboId,
 *     axioms, logicalDefinition?, characteristics?}. The LOGICAL definition
 *     (OBO intersection_of genus-differentia) IS structural and lives INSIDE
 *     identity — a genuine mechanically-extractable definition, a tier richer
 *     than WordNet hypernymy, and an explicit UPGRADE CANDIDATE toward a
 *     profile-1 structured explication (upgradeCandidate:true).
 *   - textual `definition` (the prose def annotation), `label`, `synonyms`,
 *     `namespace`, `xrefs` live under "annotations", OUTSIDE identity — the
 *     same mutable Princeton-gloss-style stratum the hash boundary excludes.
 *   - provenance mandatory per record; extraction is byte-deterministic
 *     (extractionDate pinned; bump with EXTRACTOR_VERSION).
 *
 * Fail-closed: each source file's sha256 must match its pin (ERR_SOURCE_HASH);
 * malformed OBO lines throw (parse-obo.mjs ERR_OBO_*).
 *
 * Usage: nice -n 10 node data/onto-obo/extractor/extract.mjs
 */
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  parseObo, tagMap, toUrn, isCurie, curiePrefix, stripIdValue,
  parseDef, parseSynonym, parseQuoted, ID_TAGS, BOOL_TAGS,
} from './parse-obo.mjs';

/**
 * Pull the literal of a property_value line with the given predicate, e.g.
 * `IAO:0000600 "A continuant is ..." xsd:string {mods}` -> "A continuant...".
 * Returns null if the predicate does not match or the value is not a literal.
 */
function propValueLiteral(v, predicate) {
  const sp = v.indexOf(' ');
  if (sp < 0) return null;
  if (v.slice(0, sp).trim() !== predicate) return null;
  const rest = v.slice(sp + 1).trim();
  if (rest[0] !== '"') return null;
  return parseQuoted(rest).text;
}

export const EXTRACTOR_NAME = 'kot-obo-extractor';
export const EXTRACTOR_VERSION = '0.1.0';
export const EXTRACTION_DATE = '2026-07-07';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(ROOT, 'source');

/** Per-ontology config; sha256 pins fail closed on source drift. */
export const ONTOLOGIES = [
  {
    id: 'BFO',
    file: 'bfo.obo',
    out: 'bfo.jsonl',
    sha256: 'a2510be533829ef988330f4a01cd43ccf7881bdb167cf801bad21611cc04b2ae',
    sourceName: 'Basic Formal Ontology (OBO Foundry canonical serialization)',
    purl: 'http://purl.obolibrary.org/obo/bfo.obo',
    license: 'CC BY 4.0',
    licenseUrl: 'https://creativecommons.org/licenses/by/4.0/',
    licenseVerdict: 'REDISTRIBUTABLE: CC BY 4.0 permits redistribution of derived records with attribution (Basic Formal Ontology, its authors, http://purl.obolibrary.org/obo/bfo).',
    note: 'OBO serialization is class-only (data-version 2019-08-26); BFO 2020\'s core RELATIONS are serialized in OWL only and are captured here via RO\'s BFO-relation Typedefs (BFO:0000050 etc.). bfo-2020.owl sha256 recorded for provenance completeness (not parsed).',
    extra: { 'bfo-2020.owl': 'af81eb7144c3d3db3a2d2beabff9dd299b14a91dc69cc84e663ca91e0c98039c' },
  },
  {
    id: 'RO',
    file: 'ro.obo',
    out: 'ro.jsonl',
    sha256: 'e34a2ea60fc15114edd4494c912ac0558ae51d31a1e5d62c6c0db0dac9e90449',
    sourceName: 'Relation Ontology (RO)',
    purl: 'http://purl.obolibrary.org/obo/ro.obo',
    license: 'CC0 1.0',
    licenseUrl: 'https://creativecommons.org/publicdomain/zero/1.0/',
    licenseVerdict: 'REDISTRIBUTABLE: CC0 1.0 is a public-domain dedication; no restrictions on derived records.',
    note: 'The relation vocabulary used across OBO. [Typedef] stanzas -> relation records (kind:"relation") with inverse_of/domain/range/transitive_over/holds_over_chain axioms and boolean characteristics; [Term] stanzas -> class records.',
  },
  {
    id: 'GO',
    file: 'go.obo',
    out: 'go.jsonl',
    sha256: 'f6a7004c2ee92896691359aa211c418aa1f9430a5906d7913af67afeda05e34c',
    sourceName: 'Gene Ontology (GO)',
    purl: 'http://purl.obolibrary.org/obo/go.obo',
    license: 'CC BY 4.0',
    licenseUrl: 'https://creativecommons.org/licenses/by/4.0/',
    licenseVerdict: 'REDISTRIBUTABLE: CC BY 4.0 permits redistribution of derived records with attribution (Gene Ontology Consortium, http://geneontology.org).',
    note: 'Domain exemplar chosen for its heavy genus-differentia logical definitions (intersection_of). Obsolete terms (is_obsolete:true) are excluded from records and counted; they carry no definitional axioms.',
  },
];

function sha256(buf) {
  return createHash('sha256').update(buf).digest('hex');
}

/** Build one record from a [Term]/[Typedef] stanza, or null if to skip. */
export function stanzaToRecord(stanza, ont, provenance) {
  const m = tagMap(stanza);
  const idVals = m.get('id');
  if (!idVals || idVals.length === 0) return null; // e.g. a spurious stanza
  const oboId = idVals[0].trim();
  const kind = stanza.type === 'Typedef' ? 'relation' : 'class';

  // Obsolete terms carry no definitional content: exclude, count upstream.
  if ((m.get('is_obsolete') || []).some((v) => v.trim() === 'true')) {
    return { obsolete: true, oboId };
  }

  const axioms = [];
  for (const v of m.get('is_a') || []) {
    axioms.push({ rel: 'is_a', target: toUrn(stripIdValue(v)) });
  }
  for (const v of m.get('relationship') || []) {
    const body = stripIdValue(v);
    const toks = body.split(/\s+/);
    if (toks.length < 2) throw new Error(`ERR_OBO_REL: relationship needs prop+target: ${v}`);
    axioms.push({ rel: 'relationship', property: toks[0], target: toUrn(toks[1]) });
  }
  for (const v of m.get('disjoint_from') || []) {
    axioms.push({ rel: 'disjoint_from', target: toUrn(stripIdValue(v)) });
  }
  for (const v of m.get('union_of') || []) {
    axioms.push({ rel: 'union_of', target: toUrn(stripIdValue(v)) });
  }
  // Relation-only structural axioms.
  for (const tag of ['inverse_of', 'domain', 'range', 'transitive_over']) {
    for (const v of m.get(tag) || []) {
      axioms.push({ rel: tag, target: toUrn(stripIdValue(v)) });
    }
  }
  for (const v of m.get('holds_over_chain') || []) {
    const chain = stripIdValue(v).split(/\s+/).map(toUrn);
    axioms.push({ rel: 'holds_over_chain', chain });
  }

  // Boolean relation characteristics (structural).
  const characteristics = [];
  for (const t of BOOL_TAGS) {
    if (t === 'is_obsolete' || t === 'is_metadata_tag' || t === 'is_class_level') continue;
    if ((m.get(t) || []).some((v) => v.trim() === 'true')) characteristics.push(t);
  }

  // Logical definition (OBO intersection_of = OWL equivalentClass conjunction).
  let logicalDefinition = null;
  const iof = m.get('intersection_of') || [];
  if (iof.length > 0) {
    const genus = [];
    const differentiae = [];
    for (const v of iof) {
      const body = stripIdValue(v);
      const toks = body.split(/\s+/);
      if (toks.length === 1) genus.push(toUrn(toks[0]));
      else differentiae.push({ property: toks[0], filler: toUrn(toks[1]) });
    }
    logicalDefinition = {
      form: 'obo-genus-differentia',
      operator: 'intersection_of',
      genus,
      differentiae,
    };
  }
  const genusDifferentia = !!(logicalDefinition
    && logicalDefinition.genus.length >= 1
    && logicalDefinition.differentiae.length >= 1);

  // Annotations (OUTSIDE identity).
  const annotations = {};
  if (m.has('name')) annotations.label = m.get('name')[0];
  if (m.has('namespace')) annotations.namespace = m.get('namespace')[0];
  if (m.has('def')) {
    const d = parseDef(m.get('def')[0]);
    annotations.definition = d.text;
    if (d.xrefs.length) annotations.definitionXrefs = d.xrefs;
  } else {
    // BFO carries textual definitions as IAO:0000600 "elucidation"
    // property_values rather than def: tags. Capture the first one.
    for (const v of m.get('property_value') || []) {
      const lit = propValueLiteral(v, 'IAO:0000600');
      if (lit) {
        annotations.definition = lit;
        annotations.definitionSource = 'IAO:0000600 (elucidation)';
        break;
      }
    }
  }
  if (m.has('comment')) annotations.comment = m.get('comment')[0];
  const syns = (m.get('synonym') || []).map(parseSynonym);
  if (syns.length) annotations.synonyms = syns;
  const xrefs = (m.get('xref') || []).map(stripIdValue);
  if (xrefs.length) annotations.xrefs = xrefs;
  const subsets = (m.get('subset') || []).map((v) => v.trim());
  if (subsets.length) annotations.subsets = subsets;
  const altIds = (m.get('alt_id') || []).map((v) => stripIdValue(v));
  if (altIds.length) annotations.altIds = altIds;

  const rec = {
    id: toUrn(oboId),
    schema: 'kot-obo/1',
    semanticStatus: 'AxiomsOnly',
    ontology: ont.id,
    kind,
    oboId,
    axioms,
  };
  if (characteristics.length) rec.characteristics = characteristics;
  if (logicalDefinition) {
    rec.logicalDefinition = logicalDefinition;
    // Genus-differentia definitions are the upgrade path to profile-1
    // structured explications (docs/design-bulk-kernel.md; follow-up filed).
    rec.upgradeCandidate = genusDifferentia;
  }
  rec.annotations = annotations;
  rec.provenance = provenance;
  return { record: rec, genusDifferentia, hasLogicalDef: !!logicalDefinition, kind };
}

/** Read + hash-verify + parse a source ontology into stanzas. */
function loadOntology(ont) {
  const path = join(SRC, ont.file);
  if (!existsSync(path)) {
    throw new Error(`ERR_SOURCE_MISSING: ${ont.file} not in source/ (re-download per README)`);
  }
  const buf = readFileSync(path);
  const gotSha = sha256(buf);
  if (gotSha !== ont.sha256) {
    throw new Error(`ERR_SOURCE_HASH: ${ont.file} sha256 ${gotSha} != pin ${ont.sha256}`);
  }
  const provenance = {
    source: ont.sourceName,
    sourcePurl: ont.purl,
    sourceVersion: `sha256:${ont.sha256}`,
    license: ont.license,
    extractor: EXTRACTOR_NAME,
    extractorVersion: EXTRACTOR_VERSION,
    extractionDate: EXTRACTION_DATE,
  };
  const { header, stanzas } = parseObo(buf.toString('utf8'));
  const dataVersion = (header.find(([t]) => t === 'data-version') || [])[1] || null;
  return { ont, provenance, stanzas, dataVersion };
}

/** Fixed prefix -> owning-ontology id map (bare relation names have no prefix). */
const PREFIX_OWNER = { BFO: 'BFO', RO: 'RO', GO: 'GO' };

/**
 * Canonical owner of an OBO id: the ontology whose id-space matches the
 * CURIE prefix IF it declares the id (e.g. BFO:0000002 class -> BFO); else the
 * first ontology (fixed order) that declares it (e.g. BFO:0000050 relation is
 * declared only in RO, so RO owns it). This dedups OBO import stubs: the same
 * IRI re-declared across ontologies yields ONE canonical record.
 */
function computeOwners(loaded) {
  const declaredBy = new Map(); // oboId -> [ontId in fixed order]
  for (const { ont, stanzas } of loaded) {
    for (const st of stanzas) {
      if (st.type !== 'Term' && st.type !== 'Typedef') continue;
      const m = tagMap(st);
      const idv = m.get('id');
      if (!idv) continue;
      if ((m.get('is_obsolete') || []).some((v) => v.trim() === 'true')) continue;
      const oboId = idv[0].trim();
      if (!declaredBy.has(oboId)) declaredBy.set(oboId, []);
      const arr = declaredBy.get(oboId);
      if (!arr.includes(ont.id)) arr.push(ont.id);
    }
  }
  const owner = new Map();
  for (const [oboId, declarers] of declaredBy) {
    const prefixOwner = PREFIX_OWNER[curiePrefix(oboId)];
    owner.set(oboId, (prefixOwner && declarers.includes(prefixOwner)) ? prefixOwner : declarers[0]);
  }
  return owner;
}

/** Emit one shard for an ontology, keeping only records it canonically owns. */
function emitOntology({ ont, provenance, stanzas, dataVersion }, owner) {
  const lines = [];
  const stats = {
    records: 0, classes: 0, relations: 0,
    withLogicalDef: 0, genusDifferentia: 0, obsoleteSkipped: 0,
    importedAliasesSkipped: 0, axiomsByRel: {}, differentiaProps: {},
  };
  const emittedUrns = new Set();
  for (const st of stanzas) {
    if (st.type !== 'Term' && st.type !== 'Typedef') continue;
    const r = stanzaToRecord(st, ont, provenance);
    if (!r) continue;
    if (r.obsolete) { stats.obsoleteSkipped++; continue; }
    const rec = r.record;
    // Skip records owned by another ontology (OBO import stub of a foreign IRI).
    if (owner.get(rec.oboId) !== ont.id) { stats.importedAliasesSkipped++; continue; }
    if (emittedUrns.has(rec.id)) {
      throw new Error(`ERR_OBO_DUP: duplicate id ${rec.oboId} in ${ont.file}`);
    }
    emittedUrns.add(rec.id);
    lines.push(JSON.stringify(rec));
    stats.records++;
    if (r.kind === 'relation') stats.relations++; else stats.classes++;
    if (r.hasLogicalDef) stats.withLogicalDef++;
    if (r.genusDifferentia) stats.genusDifferentia++;
    for (const ax of rec.axioms) {
      stats.axiomsByRel[ax.rel] = (stats.axiomsByRel[ax.rel] || 0) + 1;
    }
    if (rec.logicalDefinition) {
      for (const d of rec.logicalDefinition.differentiae) {
        stats.differentiaProps[d.property] = (stats.differentiaProps[d.property] || 0) + 1;
      }
    }
  }
  const outText = lines.join('\n') + '\n';
  writeFileSync(join(ROOT, ont.out), outText);
  const shard = { records: stats.records, bytes: Buffer.byteLength(outText), sha256: sha256(outText) };
  return { stats, shard, dataVersion, emittedUrns, provenance };
}

function main() {
  const perOntology = {};
  const shards = {};
  const sourceFiles = {};
  let totalRecords = 0;
  const results = {};

  const loaded = ONTOLOGIES.map(loadOntology);
  const owner = computeOwners(loaded);

  for (const ld of loaded) {
    const ont = ld.ont;
    const res = emitOntology(ld, owner);
    results[ont.id] = res;
    shards[ont.out] = res.shard;
    sourceFiles[ont.file] = `sha256:${ont.sha256}`;
    if (ont.extra) for (const [k, v] of Object.entries(ont.extra)) sourceFiles[k] = `sha256:${v}`;
    totalRecords += res.stats.records;
    // top differentia properties
    const topDiff = Object.entries(res.stats.differentiaProps)
      .sort((a, b) => b[1] - a[1]).slice(0, 15);
    perOntology[ont.id] = {
      sourceName: ont.sourceName,
      purl: ont.purl,
      sourceVersion: `sha256:${ont.sha256}`,
      dataVersion: res.dataVersion,
      license: ont.license,
      licenseUrl: ont.licenseUrl,
      licenseVerdict: ont.licenseVerdict,
      note: ont.note,
      shard: ont.out,
      counts: res.stats,
      topDifferentiaProperties: topDiff,
    };
  }

  const manifest = {
    corpus: 'onto-obo',
    schema: 'kot-obo/1',
    version: EXTRACTOR_VERSION,
    semanticStatus: 'AxiomsOnly',
    statusNote:
      'Structural axioms mechanically extracted from fixed OBO Foundry sources; NO semantic-adequacy claim. '
      + 'The LOGICAL definition (intersection_of genus-differentia) is inside record identity (a genuine mechanical '
      + 'definition, a tier richer than WordNet hypernymy) and flagged upgradeCandidate:true — the upgrade path to a '
      + 'profile-1 structured explication (docs/design-bulk-kernel.md). Textual definitions/labels/synonyms are '
      + 'annotations OUTSIDE identity. Not a mapper/pre-registration surface.',
    extractor: {
      name: EXTRACTOR_NAME,
      version: EXTRACTOR_VERSION,
      files: ['parse-obo.mjs', 'extract.mjs'],
      contentHash: extractorContentHash(),
      hashRule: 'sha256 over concatenated bytes of listed files, in listed order',
    },
    extractionDate: EXTRACTION_DATE,
    ontologies: perOntology,
    sourceFiles,
    shards,
    totals: {
      records: totalRecords,
      withLogicalDef: Object.values(results).reduce((a, r) => a + r.stats.withLogicalDef, 0),
      genusDifferentia: Object.values(results).reduce((a, r) => a + r.stats.genusDifferentia, 0),
      bytes: Object.values(shards).reduce((a, s) => a + s.bytes, 0),
    },
  };
  writeFileSync(join(ROOT, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');

  const t = manifest.totals;
  console.log(`onto-obo: ${t.records} records across ${ONTOLOGIES.length} ontologies`);
  for (const ont of ONTOLOGIES) {
    const c = perOntology[ont.id].counts;
    console.log(`  ${ont.id}: ${c.records} records (${c.classes} class, ${c.relations} rel), `
      + `logicalDef=${c.withLogicalDef}, genus-differentia=${c.genusDifferentia}, obsoleteSkipped=${c.obsoleteSkipped}`);
  }
  console.log(`  TOTAL logical definitions: ${t.withLogicalDef}; genus-differentia: ${t.genusDifferentia}`);
}

export function extractorContentHash() {
  const here = dirname(fileURLToPath(import.meta.url));
  const h = createHash('sha256');
  for (const f of ['parse-obo.mjs', 'extract.mjs']) h.update(readFileSync(join(here, f)));
  return h.digest('hex');
}

if (import.meta.url === `file://${process.argv[1]}`) main();
