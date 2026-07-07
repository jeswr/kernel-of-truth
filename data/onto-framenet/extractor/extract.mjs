#!/usr/bin/env node
/**
 * FrameNet 1.7 -> onto-framenet tier extractor (kernel-of-truth-cgh).
 *
 * Source: FrameNet 1.7, obtained via NLTK's PUBLIC, CC-BY-3.0 redistribution
 * (nltk_data framenet_v17.zip; sha256 matches NLTK's official index checksum).
 * We do NOT use the registration-gated official download and do NOT scrape
 * around it: the data licence (CC BY 3.0) explicitly permits redistribution,
 * which is exactly why NLTK can and does host it (see README + manifest for the
 * full licensing analysis).
 *
 * We extract ONLY the freely-licensed frame metadata the directive scopes:
 *   frames.jsonl          — frame + frame elements (the valency skeleton) +
 *                           lexical-unit NAMES; definition prose as annotation.
 *   frame-relations.jsonl — the 10 typed frame-to-frame relations with FE maps.
 * We do NOT redistribute the annotated corpus (lu/, fulltext/ sentence data).
 *
 * Honesty architecture: semanticStatus AxiomsOnly. The frame-element structure
 * (roles + core/peripheral typing) is INSIDE identity — it is the frame's
 * argument/valency skeleton. Definition prose, FE-definition prose and LU
 * lemmas are annotations OUTSIDE identity. provenance mandatory; deterministic.
 *
 * Usage: nice -n 10 node data/onto-framenet/extractor/extract.mjs
 */
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, existsSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseFrameFile, parseFrameRelations } from './parse-fn.mjs';

export const EXTRACTOR_NAME = 'kot-framenet-extractor';
export const EXTRACTOR_VERSION = '0.1.0';
export const EXTRACTION_DATE = '2026-07-07';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(ROOT, 'source');
const FN = join(SRC, 'fndata', 'framenet_v17');

export const SOURCE = {
  dataset: 'FrameNet 1.7 (Berkeley FrameNet Project, ICSI)',
  author: 'Collin F. Baker et al.',
  obtainedVia: 'NLTK public redistribution (github.com/nltk/nltk_data, packages/corpora/framenet_v17.zip)',
  zipSha256: '22f6aad6fb799ba4dbed0440714e1118442ad7d7345351de37428581284f471c',
  nltkIndexChecksumMatch: true,
  license: 'CC BY 3.0 Unported',
  licenseUrl: 'https://creativecommons.org/licenses/by/3.0/',
  licenseVerdict:
    'REDISTRIBUTABLE with attribution. FrameNet 1.7 is licensed "Creative Commons Attribution 3.0 Unported License" '
    + '(authoritative source: NLTK\'s official nltk_data index.xml package metadata for framenet_v17, author Collin F. Baker; '
    + 'our zip sha256 matches NLTK\'s recorded checksum). CC BY 3.0 permits copying, redistribution and derivative works with '
    + 'attribution to the Berkeley FrameNet Project. (NOTE: FrameNet 1.5 was non-commercial-only; 1.7 was relicensed to CC BY 3.0.)',
  licensingBoundary:
    'The official site (framenet.icsi.berkeley.edu) gates the download behind a registration/request form (direct fetches '
    + 'return a JS-app placeholder). That form is a courtesy tracker, NOT a licence restriction — the CC BY 3.0 licence permits '
    + 'redistribution. We therefore used NLTK\'s authorized public CC-BY copy and did not circumvent the form. We extract the '
    + 'freely-licensed frame metadata (frames + frame elements + frame relations) and deliberately exclude the annotated '
    + 'corpus (lu/, fulltext/).',
  attribution: 'Baker, Collin F., Charles J. Fillmore, and John B. Lowe (1998); FrameNet, https://framenet.icsi.berkeley.edu, CC BY 3.0.',
};

function sha256(buf) { return createHash('sha256').update(buf).digest('hex'); }
const urnFrame = (id) => `urn:onto-framenet:frame-${id}`;

function main() {
  if (!existsSync(FN)) {
    throw new Error('ERR_SOURCE_MISSING: source/fndata/framenet_v17 not found. '
      + 'Re-create per README: unzip the frame metadata from framenet_v17.zip.');
  }
  const provenance = {
    source: SOURCE.dataset,
    obtainedVia: SOURCE.obtainedVia,
    sourceVersion: `sha256:${SOURCE.zipSha256}`,
    license: SOURCE.license,
    extractor: EXTRACTOR_NAME,
    extractorVersion: EXTRACTOR_VERSION,
    extractionDate: EXTRACTION_DATE,
  };

  // ---- frames ----
  const frameDir = join(FN, 'frame');
  const files = readdirSync(frameDir).filter((f) => f.endsWith('.xml')).sort();
  const frameLines = [];
  const frameIds = new Set();
  const stats = {
    frames: 0, frameElements: 0, coreFEs: 0, lexicalUnits: 0,
    coreTypeCounts: {}, framesWithDefinition: 0,
  };
  for (const f of files) {
    const xml = readFileSync(join(frameDir, f), 'utf8');
    const p = parseFrameFile(xml);
    const annotations = {};
    if (p.definition) { annotations.definition = p.definition; stats.framesWithDefinition++; }
    if (Object.keys(p.feDefs).length) annotations.frameElementDefinitions = p.feDefs;
    if (p.lus.length) annotations.lexicalUnits = p.lus;
    const rec = {
      id: urnFrame(p.id),
      schema: 'kot-framenet/1',
      semanticStatus: 'AxiomsOnly',
      form: 'framenet-frame',
      frame: p.name,
      frameId: p.id,
      frameElements: p.fes,
      annotations,
      provenance,
    };
    frameLines.push(JSON.stringify(rec));
    frameIds.add(p.id);
    stats.frames++;
    stats.frameElements += p.fes.length;
    stats.lexicalUnits += p.lus.length;
    for (const fe of p.fes) {
      stats.coreTypeCounts[fe.coreType] = (stats.coreTypeCounts[fe.coreType] || 0) + 1;
      if (fe.coreType === 'Core') stats.coreFEs++;
    }
  }

  // ---- frame relations ----
  const relXml = readFileSync(join(FN, 'frRelation.xml'), 'utf8');
  const rels = parseFrameRelations(relXml);
  const relLines = [];
  const relStats = { relations: 0, byType: {}, feMappings: 0, danglingFrameRefs: 0 };
  for (const r of rels) {
    const rec = {
      id: `urn:onto-framenet:frel-${r.relId}`,
      schema: 'kot-framenet/1',
      semanticStatus: 'AxiomsOnly',
      form: 'framenet-frame-relation',
      relationType: r.relationType,
      sub: urnFrame(r.subFrameId), subFrame: r.subFrame, subFrameId: r.subFrameId,
      super: urnFrame(r.superFrameId), superFrame: r.superFrame, superFrameId: r.superFrameId,
      feMappings: r.feMappings,
      provenance,
    };
    relLines.push(JSON.stringify(rec));
    relStats.relations++;
    relStats.byType[r.relationType] = (relStats.byType[r.relationType] || 0) + 1;
    relStats.feMappings += r.feMappings.length;
    if (!frameIds.has(r.subFrameId)) relStats.danglingFrameRefs++;
    if (!frameIds.has(r.superFrameId)) relStats.danglingFrameRefs++;
  }

  const framesText = frameLines.join('\n') + '\n';
  const relsText = relLines.join('\n') + '\n';
  writeFileSync(join(ROOT, 'frames.jsonl'), framesText);
  writeFileSync(join(ROOT, 'frame-relations.jsonl'), relsText);

  const manifest = {
    corpus: 'onto-framenet',
    schema: 'kot-framenet/1',
    version: EXTRACTOR_VERSION,
    semanticStatus: 'AxiomsOnly',
    statusNote:
      'FrameNet 1.7 frame metadata: frames + frame elements (the valency skeleton, INSIDE identity) + frame-to-frame '
      + 'relations. Definition prose, FE-definition prose and lexical-unit lemmas are annotations OUTSIDE identity. '
      + 'The annotated corpus (lu/, fulltext/) is NOT extracted. NO semantic-adequacy claim; not a mapper surface.',
    source: SOURCE,
    extractor: {
      name: EXTRACTOR_NAME, version: EXTRACTOR_VERSION,
      files: ['parse-fn.mjs', 'extract.mjs'], contentHash: extractorContentHash(),
      hashRule: 'sha256 over concatenated bytes of listed files, in listed order',
    },
    extractionDate: EXTRACTION_DATE,
    files: { 'frames.jsonl': frameLines.length, 'frame-relations.jsonl': relLines.length },
    frameStats: stats,
    relationStats: relStats,
    shards: {
      'frames.jsonl': { records: frameLines.length, bytes: Buffer.byteLength(framesText), sha256: sha256(framesText) },
      'frame-relations.jsonl': { records: relLines.length, bytes: Buffer.byteLength(relsText), sha256: sha256(relsText) },
    },
  };
  writeFileSync(join(ROOT, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');

  console.log(`onto-framenet: ${stats.frames} frames, ${stats.frameElements} frame elements (${stats.coreFEs} Core), ${stats.lexicalUnits} lexical units`);
  console.log(`  coreType: ${Object.entries(stats.coreTypeCounts).map(([k, v]) => `${k}:${v}`).join(', ')}`);
  console.log(`  ${relStats.relations} frame relations, ${relStats.feMappings} FE mappings, dangling frame refs=${relStats.danglingFrameRefs}`);
  console.log(`  relation types: ${Object.entries(relStats.byType).map(([k, v]) => `${k}:${v}`).join(', ')}`);
}

export function extractorContentHash() {
  const here = dirname(fileURLToPath(import.meta.url));
  const h = createHash('sha256');
  for (const f of ['parse-fn.mjs', 'extract.mjs']) h.update(readFileSync(join(here, f)));
  return h.digest('hex');
}

if (import.meta.url === `file://${process.argv[1]}`) main();
