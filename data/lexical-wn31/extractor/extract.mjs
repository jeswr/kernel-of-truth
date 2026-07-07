#!/usr/bin/env node
/**
 * WordNet 3.1 -> lexical AxiomsOnly tier extractor (kernel-of-truth-4m1).
 *
 * Reads data.{noun,verb,adj,adv} from source/dict/, emits one JSONL record
 * per synset into synsets-{noun,verb,adj,adv}.jsonl, plus manifest.json.
 *
 * Honesty architecture (docs/design-bulk-kernel.md; gist SS3.1):
 *   - semanticStatus: AxiomsOnly — structural axioms only, NO
 *     semantic-adequacy claim.
 *   - identity surface of a record = {schema, semanticStatus, pos, ssType,
 *     axioms}; lemmas and glosses live under "annotations", OUTSIDE
 *     identity — they never enter any hash-equivalent boundary.
 *   - provenance mandatory per record; extraction is byte-deterministic:
 *     same source bytes -> byte-identical output (extractionDate is a
 *     pinned constant, bumped only with EXTRACTOR_VERSION).
 *
 * Fail-closed: source tarball sha256 must match the pin (ERR_SOURCE_HASH);
 * any malformed line aborts the run (parse.mjs ERR_WN_*).
 *
 * Usage: nice -n 10 node data/lexical-wn31/extractor/extract.mjs
 */
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  parseDataLine, parseIndexLine, isHeaderLine, synsetId, AXIOM_RELS,
} from './parse.mjs';

export const EXTRACTOR_NAME = 'kot-wn31-extractor';
export const EXTRACTOR_VERSION = '0.1.0';
/** Pinned so re-extraction is byte-identical; bump with EXTRACTOR_VERSION. */
export const EXTRACTION_DATE = '2026-07-07';
/** sha256 of wn3.1.dict.tar.gz (Princeton, wordnetcode.princeton.edu). */
export const SOURCE_SHA256 =
  '3f7d8be8ef6ecc7167d39b10d66954ec734280b5bdcd57f7d9eafe429d11c22a';
export const SOURCE_NAME = 'WordNet 3.1 dict (wn3.1.dict.tar.gz, Princeton University)';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DICT = join(ROOT, 'source', 'dict');

/** file pos letter per db file; adj file holds ss_type a AND s. */
const FILES = [
  { name: 'noun', pos: 'n' },
  { name: 'verb', pos: 'v' },
  { name: 'adj', pos: 'a' },
  { name: 'adv', pos: 'r' },
];

const PROVENANCE = {
  source: SOURCE_NAME,
  sourceVersion: `sha256:${SOURCE_SHA256}`,
  extractor: EXTRACTOR_NAME,
  extractorVersion: EXTRACTOR_VERSION,
  extractionDate: EXTRACTION_DATE,
};

function sha256(buf) {
  return createHash('sha256').update(buf).digest('hex');
}

export function buildRecord(parsed, filePos) {
  const axioms = [];
  for (const p of parsed.pointers) {
    const rel = AXIOM_RELS[p.sym];
    if (!rel) continue; // out-of-scope pointer kinds: filed as follow-ups
    const ax = { rel, target: synsetId(p.pos, p.offset) };
    if (p.srcWord !== 0 || p.tgtWord !== 0) {
      // lexical pointer (antonym): word numbers index annotations.lemmas
      // (1-based) in source and target synsets — structural indices only,
      // no lexical content inside the axiom.
      ax.srcWord = p.srcWord;
      ax.tgtWord = p.tgtWord;
    }
    axioms.push(ax);
  }
  const annotations = {
    lemmas: parsed.words.map((w) => w.lemma),
    gloss: parsed.gloss,
    lexFile: parsed.lexFile,
  };
  const markers = parsed.words.filter((w) => w.marker);
  if (markers.length > 0) {
    annotations.markers = Object.fromEntries(
      markers.map((w) => [w.lemma, w.marker]),
    );
  }
  return {
    id: synsetId(filePos, parsed.offset),
    schema: 'kot-lex/1',
    semanticStatus: 'AxiomsOnly',
    pos: filePos,
    ssType: parsed.ssType,
    axioms,
    annotations,
    provenance: PROVENANCE,
  };
}

function main() {
  // 1. Fail-closed source pin.
  const tarball = join(ROOT, 'source', 'wn3.1.dict.tar.gz');
  if (!existsSync(tarball) || !existsSync(DICT)) {
    console.error(
      'ERR_SOURCE_MISSING: download https://wordnetcode.princeton.edu/wn3.1.dict.tar.gz '
      + 'into data/lexical-wn31/source/ and extract it there (tar xzf).',
    );
    process.exit(1);
  }
  const gotHash = sha256(readFileSync(tarball));
  if (gotHash !== SOURCE_SHA256) {
    console.error(`ERR_SOURCE_HASH: expected ${SOURCE_SHA256}, got ${gotHash}`);
    process.exit(1);
  }

  const manifest = {
    corpus: 'lexical-wn31',
    schema: 'kot-lex/1',
    version: EXTRACTOR_VERSION,
    semanticStatus: 'AxiomsOnly',
    statusNote:
      'Structural axioms mechanically extracted from a fixed source; NO '
      + 'semantic-adequacy claim. Glosses and lemmas are annotations OUTSIDE '
      + 'record identity. Not a mapper/pre-registration surface '
      + '(docs/design-bulk-kernel.md).',
    provenance: PROVENANCE,
    sourceFiles: {},
    synsetCounts: {},
    ssTypeCounts: {},
    axiomCounts: {},
    totals: { synsets: 0, axioms: 0, bytes: 0 },
    shards: {},
    indexConsistency: {},
  };

  for (const { name, pos } of FILES) {
    const dataPath = join(DICT, `data.${name}`);
    const raw = readFileSync(dataPath, 'utf8');
    manifest.sourceFiles[`data.${name}`] = `sha256:${sha256(raw)}`;

    const lines = raw.split('\n');
    const records = [];
    const offsets = new Set();
    for (const line of lines) {
      if (line === '' || isHeaderLine(line)) continue;
      const parsed = parseDataLine(line);
      offsets.add(parsed.offset);
      const rec = buildRecord(parsed, pos);
      records.push(rec);
      manifest.ssTypeCounts[parsed.ssType] =
        (manifest.ssTypeCounts[parsed.ssType] ?? 0) + 1;
      for (const ax of rec.axioms) {
        manifest.axiomCounts[ax.rel] = (manifest.axiomCounts[ax.rel] ?? 0) + 1;
        manifest.totals.axioms += 1;
      }
    }
    records.sort((a, b) => (a.id < b.id ? -1 : 1));
    const jsonl = records.map((r) => JSON.stringify(r)).join('\n') + '\n';
    const shardName = `synsets-${name}.jsonl`;
    writeFileSync(join(ROOT, shardName), jsonl);
    manifest.synsetCounts[name] = records.length;
    manifest.totals.synsets += records.length;
    manifest.totals.bytes += Buffer.byteLength(jsonl);
    manifest.shards[shardName] = {
      records: records.length,
      bytes: Buffer.byteLength(jsonl),
      sha256: sha256(jsonl),
    };

    // Index-file cross-check: every index offset resolves to a data record,
    // and every data record surfaces through at least one index lemma.
    const idxRaw = readFileSync(join(DICT, `index.${name}`), 'utf8');
    manifest.sourceFiles[`index.${name}`] = `sha256:${sha256(idxRaw)}`;
    const indexed = new Set();
    let idxEntries = 0;
    let danglingIdx = 0;
    for (const line of idxRaw.split('\n')) {
      if (line === '' || isHeaderLine(line)) continue;
      const e = parseIndexLine(line);
      idxEntries += 1;
      for (const off of e.offsets) {
        if (offsets.has(off)) indexed.add(off);
        else danglingIdx += 1;
      }
    }
    manifest.indexConsistency[name] = {
      indexLemmaEntries: idxEntries,
      indexOffsetsDangling: danglingIdx,
      synsetsNotInIndex: offsets.size - indexed.size,
    };
  }

  writeFileSync(
    join(ROOT, 'manifest.json'),
    JSON.stringify(manifest, null, 2) + '\n',
  );
  console.log(JSON.stringify({
    synsets: manifest.totals.synsets,
    axioms: manifest.totals.axioms,
    bytes: manifest.totals.bytes,
    perPos: manifest.synsetCounts,
    perRel: manifest.axiomCounts,
    indexConsistency: manifest.indexConsistency,
  }, null, 2));
}

// Run only when invoked directly (buildRecord is imported by sample-check).
if (process.argv[1] === fileURLToPath(import.meta.url)) main();
