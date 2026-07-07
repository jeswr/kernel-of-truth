#!/usr/bin/env node
/**
 * Random-sample verification of emitted records against the SOURCE, via an
 * independent access path (verification bar, docs/design-bulk-kernel.md).
 *
 * Independence from the extractor:
 *   - records are located in the source by BYTE OFFSET (a WordNet synset
 *     offset is the byte offset of its line in the data file) — the
 *     extractor never uses seeks, it splits lines;
 *   - fields are re-derived here with separate string logic, not
 *     parse.mjs.
 * Sample: >=100 synsets, seeded PRNG (mulberry32, seed 0x4d31) so the
 * sample itself is reproducible.
 *
 * Checks per sampled synset: id/offset agreement, ss_type, lemma list
 * (markers stripped), gloss byte-equality, and the full multiset of
 * extracted axiom (rel, target[, srcWord, tgtWord]) tuples.
 *
 * Usage: nice -n 10 node data/lexical-wn31/extractor/sample-check.mjs [n]
 */
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DICT = join(ROOT, 'source', 'dict');
const N = parseInt(process.argv[2] ?? '100', 10);

function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Same rel table as the extractor — this is the SPEC of what an axiom is,
// shared by definition, not an implementation detail under test.
const RELS = {
  '@': 'hypernym', '@i': 'instanceHypernym',
  '~': 'hyponym', '~i': 'instanceHyponym',
  '#m': 'memberHolonym', '#s': 'substanceHolonym', '#p': 'partHolonym',
  '%m': 'memberMeronym', '%s': 'substanceMeronym', '%p': 'partMeronym',
  '!': 'antonym', '*': 'entailment', '>': 'cause', '&': 'similarTo',
};

const SHARD_FOR_POS = { n: 'noun', v: 'verb', a: 'adj', r: 'adv' };

// Load all emitted records (id -> record) and per-pos id lists.
const byId = new Map();
for (const shard of Object.values(SHARD_FOR_POS)) {
  for (const line of readFileSync(join(ROOT, `synsets-${shard}.jsonl`), 'utf8').split('\n')) {
    if (line === '') continue;
    const r = JSON.parse(line);
    byId.set(r.id, r);
  }
}
const ids = [...byId.keys()].sort();

// Seeded sample without replacement.
const rand = mulberry32(0x4d31);
const chosen = new Set();
while (chosen.size < Math.min(N, ids.length)) {
  chosen.add(ids[Math.floor(rand() * ids.length)]);
}

// Raw source buffers for byte-offset access.
const rawBuf = Object.fromEntries(
  Object.entries(SHARD_FOR_POS).map(([pos, shard]) => [
    pos, readFileSync(join(DICT, `data.${shard}`)),
  ]),
);

/** Independent field extraction from one raw line, by string surgery. */
function independentParse(lineStr) {
  const [lhs, ...glossParts] = lineStr.split(' | ');
  const gloss = glossParts.join(' | ').replace(/\s+$/, '');
  const t = lhs.trim().split(/\s+/);
  const ssType = t[2];
  const wCnt = parseInt(t[3], 16);
  const lemmas = [];
  for (let w = 0; w < wCnt; w++) {
    lemmas.push(t[4 + 2 * w].replace(/\((p|a|ip)\)$/, ''));
  }
  let k = 4 + 2 * wCnt;
  const pCnt = parseInt(t[k], 10);
  k += 1;
  const axioms = [];
  for (let p = 0; p < pCnt; p++) {
    const [sym, off, pos, st] = t.slice(k, k + 4);
    k += 4;
    const rel = RELS[sym];
    if (!rel) continue;
    const ax = { rel, target: `urn:lexical-wn31:${pos}-${off}` };
    if (st !== '0000') {
      ax.srcWord = parseInt(st.slice(0, 2), 16);
      ax.tgtWord = parseInt(st.slice(2), 16);
    }
    axioms.push(ax);
  }
  return { ssType, lemmas, gloss, axioms };
}

let checked = 0;
let errors = 0;
const failures = [];
for (const id of [...chosen].sort()) {
  const rec = byId.get(id);
  const m = id.match(/^urn:lexical-wn31:([nvar])-(\d{8})$/);
  const [, pos, offset] = m;
  const buf = rawBuf[pos];
  const start = parseInt(offset, 10); // synset_offset IS the byte offset
  const nl = buf.indexOf(0x0a, start);
  const lineStr = buf.subarray(start, nl === -1 ? buf.length : nl).toString('utf8');

  const problems = [];
  if (!lineStr.startsWith(offset + ' ')) {
    problems.push(`byte-offset seek did not land on record (got: ${lineStr.slice(0, 20)})`);
  } else {
    const ind = independentParse(lineStr);
    if (ind.ssType !== rec.ssType) problems.push(`ssType ${rec.ssType} != ${ind.ssType}`);
    if (JSON.stringify(ind.lemmas) !== JSON.stringify(rec.annotations.lemmas)) {
      problems.push(`lemmas ${JSON.stringify(rec.annotations.lemmas)} != ${JSON.stringify(ind.lemmas)}`);
    }
    if (ind.gloss !== rec.annotations.gloss) problems.push('gloss mismatch');
    if (JSON.stringify(ind.axioms) !== JSON.stringify(rec.axioms)) {
      problems.push(`axioms mismatch: rec=${JSON.stringify(rec.axioms)} src=${JSON.stringify(ind.axioms)}`);
    }
  }
  checked += 1;
  if (problems.length > 0) {
    errors += 1;
    failures.push({ id, problems });
  }
}

console.log(JSON.stringify({
  sampled: checked,
  seed: '0x4d31',
  errors,
  errorRate: `${((errors / checked) * 100).toFixed(2)}%`,
  failures,
}, null, 2));
process.exit(errors > 0 ? 1 : 0);
