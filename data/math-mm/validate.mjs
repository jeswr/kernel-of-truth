// validate.mjs — self-contained structural checker for the math-mm corpus.
// Re-checks everything checkable WITHOUT the 50 MB set.mm source:
//   - JSONL well-formedness, record shape, URN discipline
//   - reference resolution (every reference resolves to an emitted record)
//   - references == union(dependencies.syntax, dependencies.definitional)
//   - df<->former inverse links (definition.syntaxFormer / definedBy) agree
//   - graph: recompute SCCs; must be acyclic after condensing exactly the
//     SCCs listed in manifest.dag.nontrivialSccs (empirically: one 2-cycle,
//     set.mm's documented df-cleq/df-clel class bootstrap)
//   - depth histogram, max depth, counts, edge count vs manifest
//   - provenance block completeness + single (source, extractor) pin
// Byte-level re-extraction identity needs the pinned source; that gate lives
// in the extractor (run twice + diff), recorded in README.md.
// Run: node data/math-mm/validate.mjs   (exit 0 iff all gates pass)

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const fail = [];
const gate = (ok, msg) => { if (!ok) fail.push(msg); };

const manifest = JSON.parse(fs.readFileSync(path.join(dir, 'manifest.json'), 'utf8'));
const files = ['syntax.jsonl', 'definitions.jsonl', 'axioms.jsonl'];
const records = [];
for (const f of files) {
  const lines = fs.readFileSync(path.join(dir, f), 'utf8').trim().split('\n');
  gate(lines.length === manifest.files[f], `${f}: ${lines.length} lines != manifest ${manifest.files[f]}`);
  for (const l of lines) records.push({ file: f, rec: JSON.parse(l) });
}
gate(records.length === manifest.counts.records, `record count ${records.length} != manifest ${manifest.counts.records}`);

const byId = new Map();
const STATUS_OF_FILE = { 'syntax.jsonl': 'syntax-former', 'definitions.jsonl': 'definition', 'axioms.jsonl': 'axiom' };
const pins = new Set();
for (const { file, rec } of records) {
  const where = `${file}:${rec.label ?? '?'}`;
  gate(typeof rec.id === 'string' && rec.id === `urn:math-mm:${rec.label}`, `${where}: id/label URN mismatch`);
  gate(!byId.has(rec.id), `${where}: duplicate id`);
  byId.set(rec.id, rec);
  gate(rec.status === STATUS_OF_FILE[file], `${where}: status ${rec.status} in wrong file`);
  const d = rec.definition;
  gate(d && d.schema === manifest.schema && d.form === 'mm-canonical', `${where}: bad definition envelope`);
  gate(typeof d.typecode === 'string' && Array.isArray(d.symbols), `${where}: missing typecode/symbols`);
  gate(rec.status === 'syntax-former' ? d.typecode !== '|-' : d.typecode === '|-', `${where}: typecode/status mismatch`);
  gate(Array.isArray(d.variables) && d.variables.every((v) => typeof v.name === 'string' && ['wff', 'class', 'setvar'].includes(v.sort)), `${where}: bad variables/sorts`);
  const varNames = new Set(d.variables.map((v) => v.name));
  for (const s of d.symbols) {
    // every variable slot must be sorted; constants are free-form tokens
    if (varNames.has(s)) varNames.delete(s);
  }
  if (d.distinctVars) {
    const vn = new Set(d.variables.map((v) => v.name));
    gate(d.distinctVars.every(([a, b]) => vn.has(a) && vn.has(b) && a < b), `${where}: distinctVars not canonical over mandatory vars`);
  }
  if (rec.status === 'definition') {
    gate(typeof d.syntaxFormer === 'string', `${where}: definition without syntaxFormer`);
    gate((d.definiendum && d.definiens && ['<->', '='].includes(d.connective)) || d.irregularShape === true, `${where}: neither split nor irregularShape`);
    if (d.definiendum) {
      const joined = [...(d.connective === '<->' ? ['(', ...d.definiendum, '<->', ...d.definiens, ')'] : [...d.definiendum, '=', ...d.definiens])];
      gate(joined.join(' ') === d.symbols.join(' '), `${where}: definiendum+definiens do not reassemble to symbols`);
    }
  }
  const dep = rec.dependencies;
  gate(dep && Array.isArray(dep.syntax) && Array.isArray(dep.definitional), `${where}: missing dependencies`);
  const union = [...new Set([...dep.syntax, ...dep.definitional])].sort();
  gate(JSON.stringify(union) === JSON.stringify(rec.references), `${where}: references != union(dependencies)`);
  const p = rec.provenance;
  gate(p && p.source === manifest.source.repository && p.sourceVersion === manifest.source.commit
    && p.sourceSha256 === manifest.source.sha256 && p.extractorVersion === manifest.extractor.version
    && p.extractorHash === manifest.extractor.contentHash && p.extractionDate === manifest.extractionDate
    && Number.isInteger(p.sourceLine) && typeof p.mathbox === 'boolean', `${where}: provenance incomplete or unpinned`);
  pins.add(`${p?.sourceVersion}|${p?.extractorHash}|${p?.extractionDate}`);
}
gate(pins.size === 1, `provenance pins not uniform: ${pins.size} distinct`);

// reference resolution + inverse df/former links
for (const { rec } of records) {
  for (const ref of rec.references) gate(byId.has(ref), `${rec.label}: dangling reference ${ref}`);
  if (rec.status === 'definition') {
    const former = byId.get(rec.definition.syntaxFormer);
    gate(former !== undefined, `${rec.label}: dangling syntaxFormer`);
    if (former && former.definition.definedBy !== undefined) {
      gate(former.definition.definedBy === rec.id, `${rec.label}: former ${former.label} definedBy mismatch`);
    }
  }
  if (rec.status === 'syntax-former' && rec.definition.definedBy) {
    const df = byId.get(rec.definition.definedBy);
    gate(df !== undefined && df.definition.syntaxFormer === rec.id, `${rec.label}: definedBy inverse mismatch`);
  }
}

// graph: recompute SCCs (iterative Tarjan) and depths on the condensation
const labels = records.map(({ rec }) => rec.label);
const adj = new Map(records.map(({ rec }) => [rec.label, rec.references.map((r) => r.slice('urn:math-mm:'.length))]));
const sccOf = new Map(); const sccMembers = [];
{
  let counter = 0;
  const index = new Map(), low = new Map(), onStack = new Set(); const S = [];
  for (const root of labels) {
    if (index.has(root)) continue;
    const work = [[root, 0]];
    while (work.length) {
      const frame = work[work.length - 1]; const [v] = frame;
      if (frame[1] === 0) { index.set(v, counter); low.set(v, counter); counter++; S.push(v); onStack.add(v); }
      let recursed = false;
      const nbrs = adj.get(v);
      for (let i = frame[1]; i < nbrs.length; i++) {
        const w = nbrs[i];
        if (!index.has(w)) { frame[1] = i + 1; work.push([w, 0]); recursed = true; break; }
        if (onStack.has(w)) low.set(v, Math.min(low.get(v), index.get(w)));
      }
      if (recursed) continue;
      if (low.get(v) === index.get(v)) {
        const comp = [];
        for (;;) { const w = S.pop(); onStack.delete(w); sccOf.set(w, sccMembers.length); comp.push(w); if (w === v) break; }
        comp.sort(); sccMembers.push(comp);
      }
      work.pop();
      if (work.length) { const p = work[work.length - 1][0]; low.set(p, Math.min(low.get(p), low.get(v))); }
    }
  }
}
const nontrivial = sccMembers.filter((m) => m.length > 1).map((m) => JSON.stringify(m)).sort();
const manifestSccs = manifest.dag.nontrivialSccs.map((m) => JSON.stringify([...m].sort())).sort();
gate(JSON.stringify(nontrivial) === JSON.stringify(manifestSccs), `SCCs ${nontrivial} != manifest ${manifestSccs}`);
gate(manifest.dag.acyclic === (nontrivial.length === 0), 'manifest.dag.acyclic inconsistent with recomputed SCCs');
const sccDepth = new Array(sccMembers.length).fill(0);
for (let s = 0; s < sccMembers.length; s++) {
  let dmax = -1;
  for (const v of sccMembers[s]) for (const w of adj.get(v)) { const t = sccOf.get(w); if (t !== s) dmax = Math.max(dmax, sccDepth[t]); }
  sccDepth[s] = dmax + 1;
}
const hist = {};
let maxDepth = 0;
let edges = 0;
for (const l of labels) {
  const d = sccDepth[sccOf.get(l)];
  hist[d] = (hist[d] || 0) + 1;
  maxDepth = Math.max(maxDepth, d);
}
for (const { rec } of records) edges += rec.dependencies.syntax.length + rec.dependencies.definitional.length;
gate(maxDepth === manifest.dag.maxDepth, `maxDepth ${maxDepth} != manifest ${manifest.dag.maxDepth}`);
gate(JSON.stringify(hist) === JSON.stringify(manifest.dag.depthHistogram), 'depth histogram mismatch');
gate(edges === manifest.dag.edges, `edge count ${edges} != manifest ${manifest.dag.edges}`);

// counts by status
const n = { 'syntax-former': 0, definition: 0, axiom: 0 };
for (const { rec } of records) n[rec.status]++;
gate(n['syntax-former'] === manifest.counts.syntaxFormers && n.definition === manifest.counts.definitions && n.axiom === manifest.counts.axioms, 'status counts != manifest');

if (fail.length) {
  console.error(`FAIL: ${fail.length} gate(s):`);
  for (const f of fail.slice(0, 30)) console.error('  - ' + f);
  process.exit(1);
}
console.log(`OK: ${records.length} records, ${edges} edges, maxDepth ${maxDepth}, ${nontrivial.length} documented SCC(s); all gates pass.`);
