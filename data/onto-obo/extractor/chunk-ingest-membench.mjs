#!/usr/bin/env node
/**
 * Chunk-ingest memory benchmark (kernel-of-truth-1mv0). Demonstrates WHY the
 * streaming path exists: the whole-file path holds the entire parsed stanza graph
 * (N objects, each a tags[] of [tag,value] pairs) PLUS an N-line record-JSON array
 * before it writes — a per-term constant ~10-30x the raw bytes, which is what
 * OOMs ChEBI (~160k) / NCBITaxon (~2.5M) on the 2-core / 7.6 GB box. The streaming
 * path holds only lightweight per-id metadata (id strings) + the emitted-id dup
 * set, and writes incrementally. Both are O(N) in memory; the streaming CONSTANT
 * is far smaller — that is the difference between a bounded run and an OOM.
 *
 * Each phase runs in its OWN process so peak RSS is clean (RSS is a high-water
 * mark that does not fall after GC). With no --phase, this orchestrates the grid.
 *
 * Usage (bounded; keep N modest on the shared box):
 *   nice -n 10 node data/onto-obo/extractor/chunk-ingest-membench.mjs [N] [2N]
 *   node data/onto-obo/extractor/chunk-ingest-membench.mjs --phase stream --n 30000 --file /tmp/x.obo
 */
import { writeFileSync, rmSync, mkdtempSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { parseObo } from './parse-obo.mjs';
import {
  computeOwners, buildRelationResolver, emitOntology,
  prescanStreamed, emitOntologyStreaming,
} from './extract.mjs';

const SELF = fileURLToPath(import.meta.url);

/** Deterministic synthetic OBO: N SO:* terms, is_a chain, every 3rd a genus-
 *  differentia (part_of), 3 relation Typedefs. Structurally ChEBI/NCBITaxon-like. */
function genFixture(n) {
  const out = ['format-version: 1.2', 'data-version: membench/1', ''];
  out.push('[Typedef]', 'id: BFO:0000050', 'name: part of', '');
  out.push('[Typedef]', 'id: part_of', 'name: part of', 'xref: BFO:0000050', 'is_transitive: true', '');
  out.push('[Typedef]', 'id: has_part', 'name: has part', 'is_transitive: true', '');
  for (let i = 1; i <= n; i++) {
    const id = 'SO:' + String(7000000 + i).padStart(7, '0');
    out.push('[Term]', `id: ${id}`, `name: synthetic feature ${i}`,
      `def: "Synthetic feature number ${i} for the memory benchmark." [MEM:${i}]`);
    if (i > 1) out.push(`is_a: SO:${String(7000000 + i - 1).padStart(7, '0')} ! prev`);
    if (i % 3 === 0 && i > 1) {
      out.push(`intersection_of: SO:${String(7000000 + i - 1).padStart(7, '0')} ! genus`);
      out.push(`intersection_of: part_of SO:7000001 ! apex`);
    }
    out.push('');
  }
  return out.join('\n') + '\n';
}

function sampledPeakRss(fn) {
  let peak = process.memoryUsage().rss;
  const t = setInterval(() => { const r = process.memoryUsage().rss; if (r > peak) peak = r; }, 15);
  try { fn(); } finally { clearInterval(t); }
  peak = Math.max(peak, process.memoryUsage().rss);
  return peak;
}

const ONT = {
  id: 'SO', file: 'membench.obo', out: 'membench.jsonl',
  sourceName: 'membench', purl: 'urn:membench', license: 'CC0 1.0',
};

function runPhase(phase, n, file, outFile) {
  const text = phase === 'whole' ? readFileSync(file, 'utf8') : null;
  const peak = sampledPeakRss(() => {
    if (phase === 'whole') {
      const { header, stanzas } = parseObo(text);
      const dataVersion = (header.find(([t]) => t === 'data-version') || [])[1] || null;
      const provenance = { source: 'membench', sourcePurl: 'urn:membench', sourceVersion: 'sha256:x',
        license: 'CC0 1.0', extractor: 'kot-obo-extractor', extractorVersion: '0.1.0', extractionDate: '2026-07-07' };
      const loaded = { ont: ONT, provenance, stanzas, dataVersion };
      const owner = computeOwners([loaded]);
      const resolveRel = buildRelationResolver([loaded], owner);
      emitOntology(loaded, owner, resolveRel, outFile);
    } else {
      const ont = { ...ONT, sourcePath: file }; // no sha pin in bench
      const sm = prescanStreamed(ont);
      const owner = computeOwners([sm.declEntry]);
      const resolveRel = buildRelationResolver([sm.declEntry], owner);
      emitOntologyStreaming(sm, owner, resolveRel, outFile);
    }
  });
  process.stdout.write(`PEAK_RSS_MB=${(peak / 1048576).toFixed(1)}\n`);
}

function arg(flag) { const i = process.argv.indexOf(flag); return i >= 0 ? process.argv[i + 1] : null; }

if (arg('--phase')) {
  runPhase(arg('--phase'), Number(arg('--n')), arg('--file'), arg('--out'));
} else {
  const sizes = [Number(process.argv[2] || 30000), Number(process.argv[3] || 60000)];
  const dir = mkdtempSync(join(tmpdir(), 'kot-membench-'));
  try {
    console.log(`chunk-ingest membench (node ${process.version}); peak RSS via 15ms sampling, one process per phase\n`);
    console.log('  N        raw MB   whole-file peak MB   streaming peak MB   ratio');
    for (const n of sizes) {
      const f = join(dir, `fx-${n}.obo`);
      const text = genFixture(n);
      writeFileSync(f, text);
      const rawMb = Buffer.byteLength(text) / 1048576;
      const run = (phase) => {
        const o = join(dir, `out-${phase}-${n}.jsonl`);
        const s = execFileSync('node', [SELF, '--phase', phase, '--n', String(n), '--file', f, '--out', o], { encoding: 'utf8' });
        return Number((s.match(/PEAK_RSS_MB=([\d.]+)/) || [])[1]);
      };
      const whole = run('whole');
      const stream = run('stream');
      console.log(`  ${String(n).padEnd(8)} ${rawMb.toFixed(1).padStart(6)}   ${whole.toFixed(1).padStart(18)}   ${stream.toFixed(1).padStart(17)}   ${(whole / stream).toFixed(2)}x`);
    }
    console.log('\n  Both are O(N); the streaming constant is far smaller (no full stanza graph,');
    console.log('  no accumulated record-JSON array), which is what turns an OOM into a bounded run.');
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}
