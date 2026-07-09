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
  {
    id: 'PATO',
    file: 'pato.obo',
    out: 'pato.jsonl',
    sha256: '9b65efdf7d8d96bafd54637041cc615404ac2c88608efbcf54efa0a369bb1f75',
    sourceName: 'Phenotype And Trait Ontology (PATO)',
    purl: 'http://purl.obolibrary.org/obo/pato.obo',
    license: 'CC BY 3.0',
    licenseUrl: 'https://creativecommons.org/licenses/by/3.0/',
    licenseVerdict: 'REDISTRIBUTABLE: CC BY 3.0 permits redistribution of derived records with attribution (Phenotype And Trait Ontology, http://purl.obolibrary.org/obo/pato). SPDX from the OBO Foundry registry (obofoundry.org/registry/ontologies.jsonld).',
    note: 'Quality ontology. data-version releases/2025-05-14. [Term] stanzas -> class records, [Typedef] -> relation records. Obsolete terms (is_obsolete:true) are excluded and counted. This release carries no intersection_of logical definitions (0 genus-differentia): is_a taxonomy + relationship axioms only. 5 PATO ids that also appear as import stubs in RO are owned by RO under the existing first-declarer dedup (RO precedes PATO in ONTOLOGIES).',
  },
  {
    id: 'PO',
    file: 'po.obo',
    out: 'po.jsonl',
    sha256: 'd90949737a9925bdb775ba7dd4a9521cb63ca4acd40211e4c7661655f379f4c9',
    sourceName: 'Plant Ontology (PO)',
    purl: 'http://purl.obolibrary.org/obo/po.obo',
    license: 'CC BY 4.0',
    licenseUrl: 'https://creativecommons.org/licenses/by/4.0/',
    licenseVerdict: 'REDISTRIBUTABLE: CC BY 4.0 permits redistribution of derived records with attribution (Plant Ontology, Planteome project, http://purl.obolibrary.org/obo/po). SPDX from the OBO Foundry registry (obofoundry.org/registry/ontologies.jsonld).',
    note: 'Plant anatomy + plant-structure-development-stage ontology. data-version releases/2026-01-09. [Term] stanzas -> class records, [Typedef] -> relation records. Obsolete terms (is_obsolete:true) are excluded and counted. 81 terms carry intersection_of genus-differentia logical definitions.',
  },
  {
    id: 'CL',
    file: 'cl.obo',
    out: 'cl.jsonl',
    sha256: '7e19b4aef8e7fe7720b0c4474c6a5b8713c904ea9ab7b7d5d96f2cb28b8fc51f',
    sourceName: 'Cell Ontology (CL)',
    purl: 'http://purl.obolibrary.org/obo/cl.obo',
    license: 'CC BY 4.0',
    licenseUrl: 'https://creativecommons.org/licenses/by/4.0/',
    licenseVerdict: 'REDISTRIBUTABLE: CC BY 4.0 permits redistribution of derived records with attribution (Cell Ontology, http://purl.obolibrary.org/obo/cl). License asserted in the source header (property_value: terms:license http://creativecommons.org/licenses/by/4.0/) and the OBO Foundry registry.',
    note: 'Cell types; rich genus-differentia (cell is_a + differentiae over part_of/has_part/capable_of etc.). data-version releases/2026-06-08. CL owns CL:* by prefix-ownership (PREFIX_OWNER), so its 5,062 UBERON import stubs and its foreign-prefix stubs (PR/CLM/DHBA/MBA/NCBITaxon/STATO/CP/IAO/COB/CHEBI/SO/raw-IRI) are NOT emitted here: UBERON stubs defer to UBERON, foreign stubs survive only as reference targets. Imported GO/RO/PATO/BFO stubs defer to their prefix owners.',
  },
  {
    id: 'UBERON',
    file: 'uberon.obo',
    out: 'uberon.jsonl',
    sha256: '7f06d8e8442008a67132a1599b652e86fe0c52d75c8d6bc5b0cc36a0031e6b3f',
    sourceName: 'Uber-anatomy Ontology (UBERON)',
    purl: 'http://purl.obolibrary.org/obo/uberon.obo',
    license: 'CC BY 3.0',
    licenseUrl: 'https://creativecommons.org/licenses/by/3.0/',
    licenseVerdict: 'REDISTRIBUTABLE: CC BY 3.0 permits redistribution of derived records with attribution (UBERON, http://purl.obolibrary.org/obo/uberon). License asserted in the source header (property_value: dcterms-license http://creativecommons.org/licenses/by/3.0/) and the OBO Foundry registry.',
    note: 'Multi-species anatomy; the target of GO part_of/occurs_in differentia and CL part_of differentia. data-version releases/2026-06-19. UBERON owns UBERON:* by prefix-ownership, so its 1,487 CL import stubs defer to CL and its foreign-prefix stubs survive only as reference targets. Loaded AFTER CL so the mutual-import dedup is symmetric (each owns its own id-space; array order is irrelevant to the outcome).',
  },
  {
    id: 'OGMS',
    file: 'ogms.obo',
    out: 'ogms.jsonl',
    sha256: 'e099f77e76ccbeeae03e95574f79785066d2a1e5231652595cdf75fb17ff9cbd',
    sourceName: 'Ontology for General Medical Science (OGMS)',
    purl: 'http://purl.obolibrary.org/obo/ogms.obo',
    license: 'CC BY 4.0',
    licenseUrl: 'https://creativecommons.org/licenses/by/4.0/',
    licenseVerdict: 'REDISTRIBUTABLE: CC BY 4.0 permits redistribution of derived records with attribution (Ontology for General Medical Science, http://purl.obolibrary.org/obo/ogms). Asserted in the source header (property_value: http://purl.org/dc/terms/license http://creativecommons.org/licenses/by/4.0/) and the OBO Foundry registry (obofoundry.org/registry/ontologies.jsonld).',
    note: 'Upper ontology of clinical medicine (disease, disorder, diagnosis, patient) built on BFO. data-version 2021-08-19. [Term] stanzas -> class records. OGMS owns OGMS:* by prefix-ownership (PREFIX_OWNER); imported BFO stubs defer to BFO; foreign-prefix import stubs are NOT emitted, surviving only as reference targets (foreign-stub policy). Obsolete terms (is_obsolete:true) excluded and counted.',
  },
  {
    id: 'SO',
    file: 'so.obo',
    out: 'so.jsonl',
    sha256: 'dde032d4c7cfb89a7013f2f8ab7420a8ef7dc469fbc2b0ffb38bef2a064a1d1f',
    sourceName: 'Sequence Ontology (SO)',
    purl: 'http://purl.obolibrary.org/obo/so.obo',
    license: 'CC BY 4.0',
    licenseUrl: 'https://creativecommons.org/licenses/by/4.0/',
    licenseVerdict: 'REDISTRIBUTABLE: CC BY 4.0 permits redistribution of derived records with attribution (Sequence Ontology / Sequence types and features ontology, http://purl.obolibrary.org/obo/so). SPDX from the OBO Foundry registry (obofoundry.org/registry/ontologies.jsonld).',
    note: 'Sequence types and features ontology (genomics). data-version 2024-11-18. [Term] -> class records, [Typedef] -> relation records (SO-local relations owned by SO; RO-shared relations defer to their first declarer). Obsolete terms (is_obsolete:true) excluded and counted. SO owns SO:* by prefix-ownership; foreign-prefix import stubs are NOT emitted, only referenced (foreign-stub policy).',
  },
  {
    id: 'MONDO',
    file: 'mondo.obo',
    out: 'mondo.jsonl',
    sha256: '75c51066741e04c0ec4751210911d29e17e16431ed2ba5b8a46fc6a37ff5b00e',
    sourceName: 'Mondo Disease Ontology (MONDO)',
    purl: 'http://purl.obolibrary.org/obo/mondo.obo',
    license: 'CC BY 4.0',
    licenseUrl: 'https://creativecommons.org/licenses/by/4.0/',
    licenseVerdict: 'REDISTRIBUTABLE: CC BY 4.0 permits redistribution of derived records with attribution (Mondo Disease Ontology, http://purl.obolibrary.org/obo/mondo). SPDX from the OBO Foundry registry (obofoundry.org/registry/ontologies.jsonld).',
    note: 'Disease backbone harmonising OMIM/Orphanet/DO/NCIt/etc. data-version releases/2026-07-06. [Term] -> class records, [Typedef] -> relation records. Obsolete terms (is_obsolete:true) excluded and counted. MONDO owns MONDO:* by prefix-ownership; imported BFO/RO/GO/PATO/PO/CL/UBERON stubs defer to their prefix owners; foreign-prefix import stubs (HP, CHEBI, NCBITaxon, DOID, OMIM, Orphanet, EFO, UMLS, raw IRIs, ...) are NOT emitted, only referenced (foreign-stub policy). HP references remain placeholder reference targets (HP held pending its custom-licence resolution).',
  },
];

function sha256(buf) {
  return createHash('sha256').update(buf).digest('hex');
}

/** Build one record from a [Term]/[Typedef] stanza, or null if to skip.
 * `resolveRel` (kernel-of-truth-8es) resolves a differentia `property` shorthand
 * to its canonical minted relation URN; when omitted (e.g. unit tests), the
 * differentia carries only the bare `property` string (pre-8es shape). */
export function stanzaToRecord(stanza, ont, provenance, resolveRel) {
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
      if (toks.length === 1) { genus.push(toUrn(toks[0])); continue; }
      // Differentia: keep the source `property` shorthand (provenance + the
      // pre-8es alias-table read path) AND resolve it to the canonical minted
      // relation URN at extraction time (kernel-of-truth-8es). This is what
      // retires the define-op's pinned §3.3 shorthand alias table: SO/MONDO
      // differentia relations are no longer bound to a GO+PO-only table.
      // Fail-closed: resolveRel throws (ERR_OBO_REL_*) on any token that does
      // not resolve to a minted relation record in the pinned shards.
      const property = toks[0];
      const filler = toUrn(toks[1]);
      differentiae.push(resolveRel
        ? { property, relation: resolveRel(property), filler }
        : { property, filler });
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

/**
 * Fixed CURIE-prefix -> owning-ontology id map (bare relation names have no
 * prefix). An ontology listed here owns its OWN id-space regardless of import
 * order: CL owns CL:*, UBERON owns UBERON:*. This is REQUIRED for ontologies
 * with heavy MUTUAL imports — CL declares 5,062 UBERON stub ids and UBERON
 * declares 1,487 CL stub ids, so no ONTOLOGIES array order makes plain
 * first-declarer dedup correct for both. Prefix-ownership breaks the tie by
 * id-space, not by order.
 *
 * PATO/PO are deliberately NOT listed: they shipped (commit caeb1a7) with a
 * handful of their ids owned by RO under first-declarer dedup, and those shards
 * + minted URNs are frozen; adding them here would silently re-own committed
 * records. Their own-prefix ids that no earlier ontology stubs are still owned
 * by PATO/PO via the first-declarer fallback below, unchanged.
 */
const PREFIX_OWNER = { BFO: 'BFO', RO: 'RO', GO: 'GO', CL: 'CL', UBERON: 'UBERON', OGMS: 'OGMS', SO: 'SO', MONDO: 'MONDO' };

/** Prefixes of the ontologies actually extracted (foreign-stub gate). */
const EXTRACTED_PREFIXES = new Set(ONTOLOGIES.map((o) => o.id));

/**
 * An OBO id is OWNABLE as a record iff it belongs to an extracted ontology:
 * a bare relation name (declared in-set as a Typedef, e.g. GO/PO local
 * relations) or a CURIE whose prefix names one of the extracted ontologies.
 * A CURIE with a FOREIGN prefix (NCBITaxon, PR, CHEBI, COB, ENVO, OBI, DHBA,
 * MBA, CLM, NBO, ...) or a raw http(s): IRI is an IMPORT STUB of an entity we
 * do not extract: it carries no definitional content here, only a label. Per
 * the foreign-stub policy it is NOT emitted as a record; it survives only as a
 * reference target (a stable placeholder urn:onto-obo:<local> inside owned
 * records' axioms/differentiae), exactly like the pre-existing external refs
 * (NCBITaxon, foaf, COB). This is what keeps CL+UBERON from injecting ~3,852
 * identity-less foreign stub records.
 */
function isOwnable(oboId) {
  const p = curiePrefix(oboId);
  if (p === '') return true; // bare in-set relation/term name
  return EXTRACTED_PREFIXES.has(p);
}

/**
 * Canonical owner of an OBO id: the ontology whose id-space matches the
 * CURIE prefix IF it declares the id (e.g. BFO:0000002 class -> BFO,
 * CL:0000540 -> CL even when RO/UBERON also stub it); else the first ontology
 * (fixed order) that declares it (e.g. BFO:0000050 relation is declared only in
 * RO, so RO owns it). This dedups OBO import stubs: the same IRI re-declared
 * across ontologies yields ONE canonical record.
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

/**
 * Build the differentia-relation resolver (kernel-of-truth-8es). Each OBO
 * `intersection_of` differentia names its relation by a bare shorthand
 * (`part_of`, `disease_has_location`, `has_quality`, ...) or a CURIE
 * (`RO:0002104`, `BFO:0000050`). This resolves that token to the canonical
 * minted relation record's stable `urn:onto-obo:` id AT EXTRACTION TIME, so the
 * define-op no longer needs its pinned §3.3 GO+PO-only shorthand alias table.
 *
 * Resolution uses ONLY the sources' own Typedef/relation declarations (no
 * hand-authored table):
 *   - a CURIE token       -> its own emitted relation record `toUrn(token)`.
 *   - a bare shorthand    -> the RO/BFO relation IRI declared by the shorthand's
 *       Typedef `xref:` (unioned across every ontology that declares the
 *       shorthand, in ONTOLOGIES order); when exactly one such xref is itself an
 *       emitted relation record, that IRI is canonical. Absent any such xref the
 *       shorthand's OWN emitted relation record is used (locally-defined
 *       relations with no RO mapping, e.g. `predisposes_towards`).
 * Fail-closed (matching the extractor's ERR_OBO_* discipline; the data must be
 * trusted over any table — memo §3.3):
 *   - >1 distinct xref-canonical relation -> ERR_OBO_REL_AMBIGUOUS (never guess).
 *   - no minted relation record at all    -> ERR_OBO_REL_UNRESOLVED.
 * `emittedRel` is exactly the set of relation records emitObology emits (Typedef,
 * non-obsolete, ownable, owned by the processing ontology) — i.e. exactly the
 * relations the mint will assign a urn:kot: URN.
 * MEASURED (2026-07-09, over all 161 distinct differentia tokens): 0 ambiguous,
 * 0 unresolved, and the 10 GO+PO shorthands resolve to EXACTLY the retired alias
 * table's targets (GO/PO define answers unchanged).
 */
function buildRelationResolver(loaded, owner) {
  const emittedRel = new Set();   // toUrn(id) of every emitted relation record
  const xrefsById = new Map();    // Typedef id -> [xref tokens], unioned in load order
  for (const { ont, stanzas } of loaded) {
    for (const st of stanzas) {
      if (st.type !== 'Typedef') continue;
      const m = tagMap(st);
      const idv = m.get('id');
      if (!idv || idv.length === 0) continue;
      if ((m.get('is_obsolete') || []).some((v) => v.trim() === 'true')) continue;
      const oboId = idv[0].trim();
      if (isOwnable(oboId) && owner.get(oboId) === ont.id) emittedRel.add(toUrn(oboId));
      if (!xrefsById.has(oboId)) xrefsById.set(oboId, []);
      const arr = xrefsById.get(oboId);
      for (const x of (m.get('xref') || []).map(stripIdValue)) if (!arr.includes(x)) arr.push(x);
    }
  }
  return function resolveRel(token) {
    if (isCurie(token)) {
      const u = toUrn(token);
      if (emittedRel.has(u)) return u;
      throw new Error(`ERR_OBO_REL_UNRESOLVED: differentia relation ${token} has no minted relation record`);
    }
    const cands = [];
    for (const x of (xrefsById.get(token) || [])) {
      if (!isCurie(x)) continue;
      const xu = toUrn(x);
      if (emittedRel.has(xu) && !cands.includes(xu)) cands.push(xu);
    }
    if (cands.length === 1) return cands[0];
    if (cands.length > 1) {
      throw new Error(`ERR_OBO_REL_AMBIGUOUS: shorthand ${token} maps to multiple minted relations [${cands.join(', ')}]`);
    }
    const u = toUrn(token);
    if (emittedRel.has(u)) return u;
    throw new Error(`ERR_OBO_REL_UNRESOLVED: differentia relation shorthand ${token} resolves to no minted relation record`);
  };
}

/** Emit one shard for an ontology, keeping only records it canonically owns. */
function emitOntology({ ont, provenance, stanzas, dataVersion }, owner, resolveRel) {
  const lines = [];
  const stats = {
    records: 0, classes: 0, relations: 0,
    withLogicalDef: 0, genusDifferentia: 0, obsoleteSkipped: 0,
    importedAliasesSkipped: 0, foreignStubsSkipped: 0, axiomsByRel: {}, differentiaProps: {},
  };
  const emittedUrns = new Set();
  for (const st of stanzas) {
    if (st.type !== 'Term' && st.type !== 'Typedef') continue;
    // Ownership pre-filter BEFORE building the record — and therefore before
    // fail-closed differentia-relation resolution (kernel-of-truth-8es). A
    // foreign-prefix import stub (NCBITaxon/PR/CHEBI/CLM/DHBA/MBA/raw IRIs/...)
    // or a non-owned re-declaration is dropped here (foreign-stub policy), so its
    // differentiae — which may name a foreign relation with NO minted record
    // (e.g. a dropped CL import stub whose differentia is `STATO:0000101`) — never
    // reach the resolver. Only records we actually emit get their relations
    // resolved, so the resolver's fail-closed throw guards emitted data exactly.
    const pm = tagMap(st);
    const pid = pm.get('id');
    if (!pid || pid.length === 0) continue;
    const poboId = pid[0].trim();
    const pObsolete = (pm.get('is_obsolete') || []).some((v) => v.trim() === 'true');
    if (!pObsolete) {
      if (!isOwnable(poboId)) { stats.foreignStubsSkipped++; continue; }
      if (owner.get(poboId) !== ont.id) { stats.importedAliasesSkipped++; continue; }
    }
    const r = stanzaToRecord(st, ont, provenance, resolveRel);
    if (!r) continue;
    if (r.obsolete) { stats.obsoleteSkipped++; continue; }
    const rec = r.record;
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
  const resolveRel = buildRelationResolver(loaded, owner);

  for (const ld of loaded) {
    const ont = ld.ont;
    const res = emitOntology(ld, owner, resolveRel);
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
