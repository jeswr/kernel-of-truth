/**
 * Chunk-ingest (streaming) equivalence + determinism proof (kernel-of-truth-1mv0).
 *
 * The large-OBO chunk-ingest mechanism must produce output BYTE-IDENTICAL to the
 * frozen whole-file path — otherwise it is a different extractor, not a memory
 * optimisation. This suite pins that on a BOUNDED sample (no ChEBI/NCBITaxon
 * full-ingest; that is a separate Opus run):
 *
 *   1. streamStanzas ≡ parseObo   — the streaming tokeniser yields byte-identical
 *      stanzas + header, on a synthetic fixture AND on a real slice of a committed
 *      source (skipped only if source/ is absent).
 *   2. streaming emit ≡ whole-file emit — for the SAME input + owner/resolver
 *      context, emitOntologyStreaming writes a shard byte-identical (sha256) to
 *      emitOntology, exercising PREFIX_OWNER ownership, the foreign-stub gate,
 *      8es differentia-relation resolution, obsolete-skip, and dup-detection.
 *   3. determinism — two streaming runs of the same input are byte-identical.
 *   4. subset filter — the pre-scan and the emit apply the SAME predicate, so the
 *      emitted set is exactly the ids that pass, and re-runs are byte-identical.
 *
 * Run: node --test data/onto-obo/extractor/chunk-ingest.test.mjs
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, existsSync, mkdtempSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
import { parseObo } from './parse-obo.mjs';
import { streamStanzas, makeSubsetFilter } from './stream-obo.mjs';
import {
  computeOwners, buildRelationResolver, emitOntology,
  prescanStreamed, emitOntologyStreaming,
} from './extract.mjs';

const sha = (s) => createHash('sha256').update(s).digest('hex');
const SRC = join(dirname(fileURLToPath(import.meta.url)), '..', 'source');

/**
 * Synthetic "streamed ontology" fixture. Uses the real extracted prefix `SO`
 * (so isOwnable/PREFIX_OWNER treat it as ownable) with a high, non-colliding
 * id block. Exercises every path the large-OBO ingest hits:
 *   - is_a taxonomy backbone (SO_9990001 <- SO_9990002 <- ...)
 *   - intersection_of genus + differentia, differentia relation resolved via a
 *     Typedef xref (part_of -> BFO:0000050, the 8es xref-canonical path) and via
 *     shorthand-self (has_part with no minted xref -> its own relation record)
 *   - a relation Typedef with a boolean characteristic
 *   - an obsolete term (excluded + counted)
 *   - a FOREIGN-prefix import stub (PR:*) — not emitted, only referenced
 *   - annotations outside identity (name/def/synonym)
 */
const FIXTURE = [
  'format-version: 1.2',
  'data-version: fixture/2026-07-09',
  '',
  '[Term]',
  'id: SO:9990001',
  'name: apex feature',
  'def: "A synthetic root feature." [FIX:1]',
  '',
  '[Term]',
  'id: SO:9990002',
  'name: mid feature',
  'namespace: fixture',
  'is_a: SO:9990001 ! apex feature',
  'synonym: "middle feature" EXACT []',
  '',
  '[Term]',
  'id: SO:9990003',
  'name: leaf feature',
  'def: "A leaf that is part of a mid feature." [FIX:2]',
  'is_a: SO:9990002 ! mid feature',
  'intersection_of: SO:9990002 ! mid feature',
  'intersection_of: part_of SO:9990001 ! apex feature',
  'relationship: part_of SO:9990001 ! apex feature',
  '',
  '[Term]',
  'id: SO:9990004',
  'name: composite feature',
  'is_a: SO:9990002 ! mid feature',
  'intersection_of: SO:9990002 ! mid feature',
  'intersection_of: has_part SO:9990003 ! leaf feature',
  '',
  '[Term]',
  'id: SO:9990005',
  'name: obsolete feature',
  'is_obsolete: true',
  '',
  '[Term]',
  'id: PR:000900',
  'name: foreign protein stub',
  'is_a: SO:9990001 ! apex feature',
  '',
  '[Typedef]',
  'id: BFO:0000050',
  'name: part of',
  '',
  '[Typedef]',
  'id: part_of',
  'name: part of',
  'xref: BFO:0000050',
  'is_transitive: true',
  '',
  '[Typedef]',
  'id: has_part',
  'name: has part',
  'is_transitive: true',
  '',
].join('\n') + '\n';

function makeOnt(overrides = {}) {
  return {
    id: 'SO',
    file: 'fixture.obo',
    out: 'fixture.jsonl',
    sourceName: 'Chunk-ingest fixture',
    purl: 'urn:fixture',
    license: 'CC0 1.0',
    ...overrides,
  };
}

// Build the whole-file (in-memory) shard for a fixture text + ont, into outPath.
function emitWholeFile(text, ont, outPath) {
  const { header, stanzas } = parseObo(text);
  const dataVersion = (header.find(([t]) => t === 'data-version') || [])[1] || null;
  // Mirror loadOntology's provenance EXACTLY (same fields/order) so the only
  // thing under test is the record bytes, not the harness.
  const provenance = {
    source: ont.sourceName,
    sourcePurl: ont.purl,
    sourceVersion: `sha256:${ont.sha256}`,
    license: ont.license,
    extractor: 'kot-obo-extractor', extractorVersion: '0.1.0', extractionDate: '2026-07-07',
  };
  const loaded = { ont, provenance, stanzas, dataVersion };
  const owner = computeOwners([loaded]);
  const resolveRel = buildRelationResolver([loaded], owner);
  return emitOntology(loaded, owner, resolveRel, outPath);
}

// Build the streaming shard for a fixture on disk (ont.sourcePath) into outPath.
function emitStreaming(ont, outPath) {
  const sm = prescanStreamed(ont);
  const owner = computeOwners([sm.declEntry]);
  const resolveRel = buildRelationResolver([sm.declEntry], owner);
  return emitOntologyStreaming(sm, owner, resolveRel, outPath);
}

test('streamStanzas ≡ parseObo on the synthetic fixture', () => {
  const dir = mkdtempSync(join(tmpdir(), 'kot-chunk-'));
  try {
    const p = join(dir, 'fx.obo');
    writeFileSync(p, FIXTURE);
    const { header, stanzas } = parseObo(FIXTURE);
    const streamed = [];
    let streamedHeader = null;
    streamStanzas(p, { onStanza: (s) => streamed.push(s), onHeader: (h) => { streamedHeader = h; } });
    assert.deepEqual(streamedHeader, header, 'header differs');
    assert.deepEqual(streamed, stanzas, 'stanza stream differs from parseObo');
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('streamStanzas ≡ parseObo on a real committed-source slice', () => {
  // Use whichever small source is present; slice to keep it bounded.
  const candidates = ['ogms.obo', 'ro.obo', 'so.obo', 'cl.obo'];
  const found = candidates.map((f) => join(SRC, f)).find(existsSync);
  if (!found) { console.log('  (skip: no source/ file present)'); return; }
  const dir = mkdtempSync(join(tmpdir(), 'kot-chunk-'));
  try {
    const full = readFileSync(found, 'utf8');
    // First ~4000 lines, trimmed to end on a stanza boundary (blank line).
    const lines = full.split('\n').slice(0, 4000);
    while (lines.length && lines[lines.length - 1].trim() !== '') lines.pop();
    const slice = lines.join('\n') + '\n';
    const p = join(dir, 'slice.obo');
    writeFileSync(p, slice);
    const { header, stanzas } = parseObo(slice);
    const streamed = [];
    let streamedHeader = null;
    streamStanzas(p, { onStanza: (s) => streamed.push(s), onHeader: (h) => { streamedHeader = h; } });
    assert.deepEqual(streamedHeader, header);
    assert.deepEqual(streamed, stanzas);
    assert.ok(stanzas.length > 5, 'slice should hold several stanzas');
    console.log(`  real slice ${found.split('/').pop()}: ${stanzas.length} stanzas identical`);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('streamStanzas hash equals sha256(file bytes)', () => {
  const dir = mkdtempSync(join(tmpdir(), 'kot-chunk-'));
  try {
    const p = join(dir, 'fx.obo');
    writeFileSync(p, FIXTURE);
    const h = createHash('sha256');
    streamStanzas(p, { onStanza: () => {}, hash: h });
    assert.equal(h.digest('hex'), sha(Buffer.from(FIXTURE)), 'streamed hash != file sha256');
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('streaming emit ≡ whole-file emit (byte-identical shard + stats)', () => {
  const dir = mkdtempSync(join(tmpdir(), 'kot-chunk-'));
  try {
    const p = join(dir, 'fx.obo');
    writeFileSync(p, FIXTURE);
    const ont = makeOnt({ sha256: sha(Buffer.from(FIXTURE)), sourcePath: p });

    const wholeOut = join(dir, 'whole.jsonl');
    const streamOut = join(dir, 'stream.jsonl');
    const wf = emitWholeFile(FIXTURE, ont, wholeOut);
    const sf = emitStreaming(ont, streamOut);

    const wholeBytes = readFileSync(wholeOut);
    const streamBytes = readFileSync(streamOut);
    assert.equal(streamBytes.toString('utf8'), wholeBytes.toString('utf8'), 'shard bytes differ');
    assert.equal(sf.shard.sha256, wf.shard.sha256, 'shard sha256 differs');
    assert.equal(sf.shard.bytes, wf.shard.bytes, 'shard byte count differs');
    // Stats parity on the fields the manifest carries.
    for (const k of ['records', 'classes', 'relations', 'withLogicalDef',
      'genusDifferentia', 'obsoleteSkipped', 'foreignStubsSkipped']) {
      assert.equal(sf.stats[k], wf.stats[k], `stat ${k} differs`);
    }
    // Sanity on what the fixture must produce: 4 classes + 3 relations = 7 records,
    // 1 obsolete skipped, 1 foreign PR stub skipped, 2 genus-differentia.
    assert.equal(wf.stats.records, 7);
    assert.equal(wf.stats.classes, 4);
    assert.equal(wf.stats.relations, 3);
    assert.equal(wf.stats.obsoleteSkipped, 1);
    assert.equal(wf.stats.foreignStubsSkipped, 1);
    assert.equal(wf.stats.genusDifferentia, 2);
    // 8es: differentia relations resolved to emitted relation URNs.
    const recs = streamBytes.toString('utf8').trim().split('\n').map((l) => JSON.parse(l));
    const leaf = recs.find((r) => r.oboId === 'SO:9990003');
    assert.equal(leaf.logicalDefinition.differentiae[0].relation, 'urn:onto-obo:BFO_0000050');
    const comp = recs.find((r) => r.oboId === 'SO:9990004');
    assert.equal(comp.logicalDefinition.differentiae[0].relation, 'urn:onto-obo:has_part');
    // The foreign stub is NOT emitted; the apex/mid/leaf/composite classes ARE.
    assert.ok(!recs.some((r) => r.oboId === 'PR:000900'));
    assert.ok(recs.some((r) => r.oboId === 'SO:9990001'));
    console.log(`  streaming shard sha256 == whole-file: ${sf.shard.sha256.slice(0, 16)}… (${sf.shard.records} records)`);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('streaming emit is deterministic (two runs byte-identical)', () => {
  const dir = mkdtempSync(join(tmpdir(), 'kot-chunk-'));
  try {
    const p = join(dir, 'fx.obo');
    writeFileSync(p, FIXTURE);
    const ont = makeOnt({ sha256: sha(Buffer.from(FIXTURE)), sourcePath: p });
    const a = emitStreaming(ont, join(dir, 'a.jsonl'));
    const b = emitStreaming(ont, join(dir, 'b.jsonl'));
    assert.equal(a.shard.sha256, b.shard.sha256, 'non-deterministic shard');
    assert.equal(readFileSync(join(dir, 'a.jsonl'), 'utf8'), readFileSync(join(dir, 'b.jsonl'), 'utf8'));
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('prescan hash mismatch fails closed (ERR_SOURCE_HASH)', () => {
  const dir = mkdtempSync(join(tmpdir(), 'kot-chunk-'));
  try {
    const p = join(dir, 'fx.obo');
    writeFileSync(p, FIXTURE);
    const bad = makeOnt({ sha256: '0'.repeat(64), sourcePath: p });
    assert.throws(() => prescanStreamed(bad), /ERR_SOURCE_HASH/);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('subset filter: pre-scan and emit agree, deterministically', () => {
  const dir = mkdtempSync(join(tmpdir(), 'kot-chunk-'));
  try {
    const p = join(dir, 'fx.obo');
    writeFileSync(p, FIXTURE);
    // Keep only ODD SO ids (9990001, 9990003) — demonstration filter (NOT is_a-closed;
    // a shippable subset must be, see stream-obo.mjs makeSubsetFilter note).
    const subset = { policy: 'numeric-mod', mod: 2, eq: 1 };
    const ont = makeOnt({ sha256: sha(Buffer.from(FIXTURE)), sourcePath: p, subset });

    const out = join(dir, 'filtered.jsonl');
    const res = emitStreaming(ont, out);
    const recs = readFileSync(out, 'utf8').trim().split('\n').filter(Boolean).map((l) => JSON.parse(l));
    const keep = makeSubsetFilter(subset);
    // Every emitted id passes the predicate (relations are always retained;
    // classes must pass the term predicate); every excluded class id is absent.
    for (const r of recs) {
      const type = r.kind === 'relation' ? 'Typedef' : 'Term';
      assert.ok(keep({ oboId: r.oboId, type }), `emitted a filtered id ${r.oboId}`);
    }
    assert.ok(recs.some((r) => r.oboId === 'SO:9990001'));
    assert.ok(recs.some((r) => r.oboId === 'SO:9990003'));
    assert.ok(!recs.some((r) => r.oboId === 'SO:9990002'), 'even id leaked past the filter');
    assert.ok(!recs.some((r) => r.oboId === 'SO:9990004'));
    assert.ok(res.stats.subsetFilteredSkipped >= 2, 'filtered-skip count too low');
    // Determinism under the filter.
    const res2 = emitStreaming(ont, join(dir, 'filtered2.jsonl'));
    assert.equal(res.shard.sha256, res2.shard.sha256);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});
