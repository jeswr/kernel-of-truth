#!/usr/bin/env node
/**
 * Bridge analysis tooling (kernel-of-truth-4m1 step 5).
 *
 * Modes:
 *   candidates <lemma[:pos]> ...   list sense-ordered synset candidates
 *                                  (index-file order = frequency order)
 *                                  with glosses, for hand-review;
 *   validate                       check alignment-kernel-v0.json (targets
 *                                  exist; lemma appears in target synset),
 *                                  then compute the semantic-reachability
 *                                  curve: # synsets within k hypernym-graph
 *                                  hops (hypernym/hyponym + instance
 *                                  variants, traversed undirected) of any
 *                                  anchored synset, k=1..5. Writes
 *                                  reachability-report.json.
 *
 * The alignment file itself is HAND-AUTHORED (each entry carries a
 * confidence and note) — mechanical lemma lookup proposes, an agent
 * disposes. Alignments are annotations OUTSIDE both records' identity.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseIndexLine, isHeaderLine, synsetId } from './parse.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DICT = join(ROOT, 'source', 'dict');
const SHARD_FOR_POS = { n: 'noun', v: 'verb', a: 'adj', r: 'adv' };

function loadRecords() {
  const byId = new Map();
  for (const shard of Object.values(SHARD_FOR_POS)) {
    for (const line of readFileSync(join(ROOT, `synsets-${shard}.jsonl`), 'utf8').split('\n')) {
      if (line === '') continue;
      const r = JSON.parse(line);
      byId.set(r.id, r);
    }
  }
  return byId;
}

function loadIndex() {
  const idx = new Map(); // "lemma:pos" -> [synset ids, sense order]
  for (const [pos, shard] of Object.entries(SHARD_FOR_POS)) {
    for (const line of readFileSync(join(DICT, `index.${shard}`), 'utf8').split('\n')) {
      if (line === '' || isHeaderLine(line)) continue;
      const e = parseIndexLine(line);
      idx.set(`${e.lemma}:${pos}`, e.offsets.map((o) => synsetId(pos, o)));
    }
  }
  return idx;
}

const mode = process.argv[2];

if (mode === 'candidates') {
  const byId = loadRecords();
  const idx = loadIndex();
  for (const arg of process.argv.slice(3)) {
    const [lemma, posFilter] = arg.split(':');
    const key = lemma.toLowerCase().replace(/ /g, '_');
    console.log(`\n== ${arg} ==`);
    for (const pos of posFilter ? [posFilter] : ['n', 'v', 'a', 'r']) {
      for (const [i, id] of (idx.get(`${key}:${pos}`) ?? []).entries()) {
        const r = byId.get(id);
        console.log(`  ${pos}#${i + 1} ${id} [${r.ssType}] {${r.annotations.lemmas.join(', ')}}: ${r.annotations.gloss.slice(0, 150)}`);
      }
    }
  }
  process.exit(0);
}

if (mode !== 'validate') {
  console.error('usage: align.mjs candidates <lemma[:pos]>... | align.mjs validate');
  process.exit(2);
}

const byId = loadRecords();
const alignment = JSON.parse(
  readFileSync(join(ROOT, 'alignment-kernel-v0.json'), 'utf8'),
);

let bad = 0;
const anchors = new Set();
for (const a of alignment.alignments) {
  const r = byId.get(a.synset);
  if (!r) {
    console.error(`ERR_ALIGN_TARGET: ${a.concept} -> ${a.synset} does not exist`);
    bad += 1;
    continue;
  }
  const lemmas = r.annotations.lemmas.map((l) => l.toLowerCase());
  if (!lemmas.includes(a.lemma.toLowerCase().replace(/ /g, '_'))) {
    console.error(`ERR_ALIGN_LEMMA: ${a.concept}: '${a.lemma}' not in ${a.synset} {${lemmas.join(', ')}}`);
    bad += 1;
    continue;
  }
  anchors.add(a.synset);
}
if (bad > 0) process.exit(1);

// ---- semantic reachability ------------------------------------------------
// Undirected hypernym-graph adjacency (hypernym/hyponym + instance forms).
const TAXO = new Set(['hypernym', 'hyponym', 'instanceHypernym', 'instanceHyponym']);
const adj = new Map();
for (const [id, r] of byId) {
  for (const ax of r.axioms) {
    if (!TAXO.has(ax.rel)) continue;
    if (!adj.has(id)) adj.set(id, []);
    adj.get(id).push(ax.target);
  }
}

const K_MAX = 5;
const dist = new Map([...anchors].map((a) => [a, 0]));
let frontier = [...anchors];
const curve = [];
for (let k = 1; k <= K_MAX; k++) {
  const next = [];
  for (const v of frontier) {
    for (const w of adj.get(v) ?? []) {
      if (!dist.has(w)) { dist.set(w, k); next.push(w); }
    }
  }
  frontier = next;
  curve.push({
    k,
    withinK: dist.size,
    pct: Number(((dist.size / byId.size) * 100).toFixed(2)),
  });
}

// POS breakdown at k=5 (adj/adv have no hypernyms: only reachable if anchored).
const posAtK5 = {};
for (const id of dist.keys()) {
  const pos = byId.get(id).pos;
  posAtK5[pos] = (posAtK5[pos] ?? 0) + 1;
}

const report = {
  anchors: anchors.size,
  alignments: alignment.alignments.length,
  confidence: {
    high: alignment.alignments.filter((a) => a.confidence >= 0.85).length,
    medium: alignment.alignments.filter((a) => a.confidence >= 0.6 && a.confidence < 0.85).length,
    low: alignment.alignments.filter((a) => a.confidence < 0.6).length,
  },
  unalignedConcepts: alignment.unaligned.map((u) => u.concept),
  totalSynsets: byId.size,
  edgeRelation: 'hypernym/hyponym (+instance forms), undirected',
  reachability: curve,
  posBreakdownAtK5: posAtK5,
};
writeFileSync(
  join(ROOT, 'reachability-report.json'),
  JSON.stringify(report, null, 2) + '\n',
);
console.log(JSON.stringify(report, null, 2));
