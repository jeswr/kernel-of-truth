#!/usr/bin/env node
/**
 * Structure checks over the emitted lexical-wn31 shards (NOT over parser
 * memory — this validates the committed artifact):
 *   1. reference closure: every axiom target id exists as a record;
 *   2. reciprocity: hypernym<->hyponym, instance variants, meronym<->holonym
 *      pairs, antonym symmetry, similarTo symmetry (reported, not fatal —
 *      asymmetry in the source is a finding);
 *   3. hypernym cycle detection (Tarjan SCC) for nouns and verbs; WordNet
 *      has shipped cycles in some versions — cycles are REPORTED AND
 *      RECORDED, never silently broken (design-bulk-kernel.md);
 *   4. taxonomy depth stats (BFS down from hypernym-less roots).
 * Writes structure-report.json; exit 1 only on closure failure.
 *
 * Usage: nice -n 10 node data/lexical-wn31/extractor/structure-check.mjs
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SHARDS = ['noun', 'verb', 'adj', 'adv'];

const RECIPROCAL = {
  hypernym: 'hyponym',
  hyponym: 'hypernym',
  instanceHypernym: 'instanceHyponym',
  instanceHyponym: 'instanceHypernym',
  partMeronym: 'partHolonym',
  partHolonym: 'partMeronym',
  memberMeronym: 'memberHolonym',
  memberHolonym: 'memberMeronym',
  substanceMeronym: 'substanceHolonym',
  substanceHolonym: 'substanceMeronym',
  antonym: 'antonym',
  similarTo: 'similarTo',
  // entailment and cause are directed with no reciprocal in the source
};

// ---- load ----------------------------------------------------------------
const records = new Map(); // id -> { pos, axioms }
for (const s of SHARDS) {
  for (const line of readFileSync(join(ROOT, `synsets-${s}.jsonl`), 'utf8').split('\n')) {
    if (line === '') continue;
    const r = JSON.parse(line);
    records.set(r.id, { pos: r.pos, ssType: r.ssType, axioms: r.axioms });
  }
}

// ---- 1. reference closure -------------------------------------------------
let axiomTotal = 0;
const danglingTargets = [];
// edge set for reciprocity: rel -> Set("src>tgt")
const edgeSets = new Map();
for (const [id, r] of records) {
  for (const ax of r.axioms) {
    axiomTotal += 1;
    if (!records.has(ax.target)) {
      danglingTargets.push({ from: id, rel: ax.rel, target: ax.target });
    }
    if (!edgeSets.has(ax.rel)) edgeSets.set(ax.rel, new Set());
    edgeSets.get(ax.rel).add(`${id}>${ax.target}`);
  }
}

// ---- 2. reciprocity --------------------------------------------------------
const reciprocity = {};
for (const [rel, inverse] of Object.entries(RECIPROCAL)) {
  const fwd = edgeSets.get(rel) ?? new Set();
  const inv = edgeSets.get(inverse) ?? new Set();
  let missing = 0;
  const examples = [];
  for (const e of fwd) {
    const [a, b] = e.split('>');
    if (!inv.has(`${b}>${a}`)) {
      missing += 1;
      if (examples.length < 5) examples.push({ from: a, rel, target: b });
    }
  }
  reciprocity[rel] = { edges: fwd.size, missingInverse: missing, examples };
}

// ---- 3. hypernym cycles (Tarjan SCC, iterative) ----------------------------
function hypernymCycles(pos) {
  const ids = [];
  const index = new Map();
  for (const [id, r] of records) {
    if (r.pos === pos) { index.set(id, ids.length); ids.push(id); }
  }
  const adj = ids.map(() => []);
  for (const [id, r] of records) {
    if (r.pos !== pos) continue;
    for (const ax of r.axioms) {
      if ((ax.rel === 'hypernym' || ax.rel === 'instanceHypernym')
          && index.has(ax.target)) {
        adj[index.get(id)].push(index.get(ax.target));
      }
    }
  }
  const n = ids.length;
  const idx = new Int32Array(n).fill(-1);
  const low = new Int32Array(n);
  const onStack = new Uint8Array(n);
  const stack = [];
  let counter = 0;
  const sccs = [];
  for (let s = 0; s < n; s++) {
    if (idx[s] !== -1) continue;
    // iterative Tarjan
    const work = [[s, 0]];
    while (work.length > 0) {
      const frame = work[work.length - 1];
      const [v] = frame;
      if (frame[1] === 0) {
        idx[v] = low[v] = counter++;
        stack.push(v); onStack[v] = 1;
      }
      let advanced = false;
      while (frame[1] < adj[v].length) {
        const w = adj[v][frame[1]++];
        if (idx[w] === -1) { work.push([w, 0]); advanced = true; break; }
        if (onStack[w]) low[v] = Math.min(low[v], idx[w]);
      }
      if (advanced) continue;
      if (low[v] === idx[v]) {
        const comp = [];
        for (;;) {
          const w = stack.pop(); onStack[w] = 0; comp.push(w);
          if (w === v) break;
        }
        if (comp.length > 1) sccs.push(comp.map((i) => ids[i]));
      }
      work.pop();
      if (work.length > 0) {
        const [p] = work[work.length - 1];
        low[p] = Math.min(low[p], low[v]);
      }
    }
  }
  // self-loops are cycles too
  for (const [id, r] of records) {
    if (r.pos !== pos) continue;
    for (const ax of r.axioms) {
      if ((ax.rel === 'hypernym' || ax.rel === 'instanceHypernym') && ax.target === id) {
        sccs.push([id]);
      }
    }
  }
  return sccs;
}

// ---- 4. depth stats (BFS from hypernym-less roots via hyponym edges) -------
function depthStats(pos) {
  const hasHypernym = new Set();
  const down = new Map(); // id -> [child ids]
  const all = [];
  for (const [id, r] of records) {
    if (r.pos !== pos) continue;
    all.push(id);
    for (const ax of r.axioms) {
      if (ax.rel === 'hypernym' || ax.rel === 'instanceHypernym') hasHypernym.add(id);
      if (ax.rel === 'hyponym' || ax.rel === 'instanceHyponym') {
        if (!down.has(id)) down.set(id, []);
        down.get(id).push(ax.target);
      }
    }
  }
  const roots = all.filter((id) => !hasHypernym.has(id));
  const depth = new Map(roots.map((r) => [r, 0]));
  const queue = [...roots];
  let head = 0;
  let maxDepth = 0;
  let sum = 0;
  while (head < queue.length) {
    const v = queue[head++];
    const d = depth.get(v);
    maxDepth = Math.max(maxDepth, d);
    sum += d;
    for (const c of down.get(v) ?? []) {
      if (!depth.has(c)) { depth.set(c, d + 1); queue.push(c); }
    }
  }
  return {
    synsets: all.length,
    roots: roots.length,
    reachedFromRoots: depth.size,
    unreachable: all.length - depth.size,
    maxDepth,
    meanDepth: Number((sum / Math.max(depth.size, 1)).toFixed(3)),
  };
}

const report = {
  generated: 'structure-check.mjs @ lexical-wn31 v0.1.0',
  totals: { records: records.size, axioms: axiomTotal },
  referenceClosure: {
    danglingTargets: danglingTargets.length,
    examples: danglingTargets.slice(0, 10),
  },
  reciprocity,
  hypernymCycles: {
    noun: hypernymCycles('n'),
    verb: hypernymCycles('v'),
  },
  depth: {
    noun: depthStats('n'),
    verb: depthStats('v'),
  },
};

writeFileSync(
  join(ROOT, 'structure-report.json'),
  JSON.stringify(report, null, 2) + '\n',
);
const summary = {
  records: records.size,
  axioms: axiomTotal,
  dangling: danglingTargets.length,
  nounCycles: report.hypernymCycles.noun.length,
  verbCycles: report.hypernymCycles.verb.length,
  reciprocityMisses: Object.fromEntries(
    Object.entries(reciprocity)
      .filter(([, v]) => v.missingInverse > 0)
      .map(([k, v]) => [k, v.missingInverse]),
  ),
  depth: report.depth,
};
console.log(JSON.stringify(summary, null, 2));
if (danglingTargets.length > 0) {
  console.error('ERR_REFERENCE_CLOSURE: dangling axiom targets');
  process.exit(1);
}
