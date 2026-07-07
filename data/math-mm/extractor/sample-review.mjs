// sample-review.mjs — verification-bar tooling (design-bulk-kernel.md):
//
// 1. GLOBAL independent cross-check: for every emitted record, re-extract the
//    statement's token string from the raw set.mm bytes by direct text search
//    (a code path sharing nothing with parse-mm.mjs) and compare:
//    typecode + symbols, and the $e hypotheses' presence. Reports mismatches.
// 2. SEEDED 100-record sample for MANUAL review (mulberry32, seed fixed):
//    prints each sampled record's judgment-laden fields (classification,
//    definiendum/definiens split, syntax-former assignment, variable sorts,
//    definitional dependencies) next to the raw source slice, for eyeball
//    comparison. The mechanical check above covers token fidelity; the human
//    pass covers the fields where an extractor could be *plausibly wrong*.
//
// Usage: node sample-review.mjs --src /path/to/set.mm --data data/math-mm \
//          [--seed 20260707] [--n 100] [--batch 0]   (batch of 20; -1 = counts only)

import fs from 'node:fs';
import path from 'node:path';

const arg = (name, dflt) => {
  const i = process.argv.indexOf(`--${name}`);
  return i === -1 ? dflt : process.argv[i + 1];
};
const srcPath = arg('src'); const dataDir = arg('data');
const seed = Number(arg('seed', '20260707'));
const n = Number(arg('n', '100'));
const batch = Number(arg('batch', '-1'));

const src = fs.readFileSync(srcPath, 'utf8');
const records = [];
for (const f of ['syntax.jsonl', 'definitions.jsonl', 'axioms.jsonl']) {
  for (const l of fs.readFileSync(path.join(dataDir, f), 'utf8').trim().split('\n')) records.push(JSON.parse(l));
}

// ---------- 1. global independent token cross-check ----------
// Strip $( ... $) comments from the raw text (label occurrences inside
// comments — e.g. commented-out older statement versions near df-cvlat and
// df-lcdual — are not statements), then find "<ws><label><ws>$a<ws>" and take
// tokens to the next "$.". Independent of parse-mm.mjs internals.
const srcNoComments = (() => {
  const toks = src.split(/(\s+)/); // keep whitespace so offsets stay textual
  let depth = 0;
  const out = [];
  for (const t of toks) {
    if (t === '$(') { depth++; continue; }
    if (t === '$)') { depth--; continue; }
    if (depth === 0) out.push(t);
  }
  return out.join('');
})();
function rawStatement(label) {
  const re = new RegExp(`(^|\\s)${label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s+\\$a\\s`);
  const m = re.exec(srcNoComments);
  if (!m) return null;
  const start = m.index + m[0].length;
  const end = srcNoComments.indexOf('$.', start);
  if (end === -1) return null;
  return srcNoComments.slice(start, end).split(/\s+/).filter(Boolean);
}
let mismatches = 0;
for (const r of records) {
  const raw = rawStatement(r.label);
  const want = [r.definition.typecode, ...r.definition.symbols].join(' ');
  if (raw === null || raw.join(' ') !== want) {
    mismatches++;
    console.log(`TOKEN-MISMATCH ${r.label}:\n  raw:  ${raw ? raw.join(' ') : '(not found)'}\n  rec:  ${want}`);
  }
}
console.log(`[global cross-check] ${records.length} records, ${mismatches} token-string mismatches`);

// ---------- 2. seeded sample for manual review ----------
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rng = mulberry32(seed);
const idx = new Set();
while (idx.size < Math.min(n, records.length)) idx.add(Math.floor(rng() * records.length));
const sample = [...idx].sort((a, b) => a - b).map((i) => records[i]);

if (batch >= 0) {
  const lines = src.split('\n');
  const B = 20;
  for (const r of sample.slice(batch * B, batch * B + B)) {
    const d = r.definition;
    console.log('='.repeat(100));
    console.log(`${r.label}  [${r.status}]  line ${r.provenance.sourceLine}${r.provenance.mathbox ? '  MATHBOX' : ''}`);
    console.log(`  stmt: ${d.typecode} ${d.symbols.join(' ')}`);
    if (d.definiendum) console.log(`  split: [${d.definiendum.join(' ')}] ${d.connective} [${d.definiens.join(' ')}]`);
    if (d.irregularShape) console.log('  split: IRREGULAR (whole statement is payload)');
    if (d.syntaxFormer) console.log(`  former: ${d.syntaxFormer.replace('urn:math-mm:', '')}`);
    if (d.definedBy) console.log(`  definedBy: ${d.definedBy.replace('urn:math-mm:', '')}`);
    console.log(`  vars: ${d.variables.map((v) => `${v.name}:${v.sort}`).join(' ') || '(none)'}`);
    if (d.distinctVars) console.log(`  $d pairs: ${d.distinctVars.length}`);
    if (d.hypotheses) console.log(`  $e hyps: ${d.hypotheses.map((h) => h.label).join(' ')}`);
    console.log(`  def-deps: ${r.dependencies.definitional.map((u) => u.replace('urn:math-mm:', '')).join(' ') || '(none)'}`);
    console.log(`  syn-deps: ${r.dependencies.syntax.map((u) => u.replace('urn:math-mm:', '')).join(' ') || '(none)'}`);
    const l0 = r.provenance.sourceLine - 1;
    console.log('  --- source ---');
    for (let i = Math.max(0, l0 - 2); i <= Math.min(lines.length - 1, l0 + 4); i++) {
      console.log(`  ${i + 1}: ${lines[i]}`);
    }
  }
  console.log(`(batch ${batch}: records ${batch * B}..${Math.min(batch * B + B, sample.length) - 1} of ${sample.length})`);
}
