#!/usr/bin/env node
/**
 * onto-sumo corpus validator — source-free re-checks (byte re-extraction
 * identity lives in the extractor: run twice + diff, recorded in README.md).
 *
 * Gates:
 *   - JSONL well-formedness; axiom/term record shape; provenance completeness.
 *   - axioms.jsonl: unique ids; every kif RE-PARSES and is a canonical
 *     FIXED POINT (canonical(parse(kif)) === kif) — proves the stored string
 *     is well-formed SUO-KIF and our serialisation is idempotent.
 *   - terms.jsonl: unique ids; id === urn:onto-sumo:<term>; asSubject > 0;
 *     kind in the allowed set.
 *   - definitionalAxiomRefs resolve to <=> axioms whose definienda include the
 *     term (the syntactic-definition back-link is sound).
 *   - declaration subjects resolve to a term record; dangling reported.
 *   - manifest cross-check: counts, shard sha256 (recomputed).
 *
 * Run: node data/onto-sumo/validate.mjs   (exit 0 iff all gates pass)
 */
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { parseKif, canonical } from './extractor/parse-kif.mjs';

const dir = dirname(fileURLToPath(import.meta.url));
const fail = [];
const gate = (ok, msg) => { if (!ok) fail.push(msg); };
const manifest = JSON.parse(readFileSync(join(dir, 'manifest.json'), 'utf8'));

function loadShard(name) {
  const text = readFileSync(join(dir, name), 'utf8');
  const lines = text.trim().split('\n');
  gate(lines.length === manifest.files[name], `${name}: ${lines.length} lines != manifest ${manifest.files[name]}`);
  const sha = createHash('sha256').update(text).digest('hex');
  gate(sha === manifest.shards[name].sha256, `${name}: sha256 mismatch vs manifest`);
  return lines.map((l) => JSON.parse(l));
}

const axioms = loadShard('axioms.jsonl');
const terms = loadShard('terms.jsonl');

// axioms ------------------------------------------------------------------
const axById = new Map();
let roundTripFail = 0;
for (const a of axioms) {
  const where = a.id;
  gate(a.schema === 'kot-sumo/1', `${where}: bad schema`);
  gate(a.semanticStatus === 'AxiomsOnly', `${where}: bad semanticStatus`);
  gate(a.form === 'sumo-kif-canonical', `${where}: bad form`);
  gate(typeof a.kif === 'string' && a.kif.length > 0, `${where}: empty kif`);
  gate(Array.isArray(a.terms), `${where}: terms not array`);
  gate(a.provenance && a.provenance.commit === manifest.source.commit, `${where}: provenance pin != manifest`);
  gate(!axById.has(a.id), `${where}: duplicate axiom id`);
  axById.set(a.id, a);
  // fixed-point re-parse
  try {
    const forms = parseKif(a.kif);
    if (forms.length !== 1 || canonical(forms[0]) !== a.kif) { roundTripFail++; fail.push(`${where}: kif not a canonical fixed point`); }
  } catch (e) { roundTripFail++; fail.push(`${where}: kif re-parse threw ${e.message}`); }
}

// terms -------------------------------------------------------------------
const KINDS = new Set(['class', 'relation', 'attribute', 'function', 'instance', 'term']);
const termSet = new Set();
for (const t of terms) {
  const where = t.term;
  gate(t.schema === 'kot-sumo/1', `${where}: bad schema`);
  gate(t.semanticStatus === 'AxiomsOnly', `${where}: bad semanticStatus`);
  gate(t.id === `urn:onto-sumo:${t.term}`, `${where}: id != urn:onto-sumo:term`);
  gate(KINDS.has(t.kind), `${where}: bad kind ${t.kind}`);
  gate(Array.isArray(t.axioms), `${where}: axioms not array`);
  gate(t.axiomStats && t.axiomStats.asSubject > 0, `${where}: asSubject not > 0`);
  gate(!termSet.has(t.term), `${where}: duplicate term`);
  termSet.add(t.term);
  gate(t.provenance && t.provenance.commit === manifest.source.commit, `${where}: provenance pin`);
}

// definitional back-links sound ------------------------------------------
let defLinks = 0;
for (const t of terms) {
  for (const ref of t.definitionalAxiomRefs || []) {
    defLinks++;
    const a = axById.get(ref);
    gate(a, `${t.term}: definitionalAxiomRef ${ref} unresolved`);
    if (a) {
      gate(a.operator === '<=>', `${t.term}: def ref ${ref} is not <=>`);
      gate(a.definienda && a.definienda.includes(t.term), `${t.term}: def ref ${ref} definienda missing term`);
    }
  }
}

// declaration subjects resolve -------------------------------------------
let danglingSubjects = 0;
const DECL = new Set(['instance', 'subclass', 'subrelation', 'subAttribute', 'domain', 'domainSubclass', 'range', 'rangeSubclass', 'documentation', 'partition', 'disjointDecomposition']);
for (const a of axioms) {
  if (a.subject && DECL.has(a.operator)) {
    if (!termSet.has(a.subject)) danglingSubjects++;
  }
}

// totals ------------------------------------------------------------------
gate(axioms.length === manifest.shards['axioms.jsonl'].records, `axiom count mismatch`);
gate(terms.length === manifest.shards['terms.jsonl'].records, `term count mismatch`);

console.log(`onto-sumo validate: ${axioms.length} axioms, ${terms.length} terms`);
console.log(`  kif fixed-point re-parse failures: ${roundTripFail}`);
console.log(`  definitional back-links checked: ${defLinks}; declaration subjects not resolving to a term record: ${danglingSubjects}`);
if (fail.length) {
  console.error(`\nFAIL (${fail.length}):`);
  for (const f of fail.slice(0, 40)) console.error('  - ' + f);
  process.exit(1);
}
console.log('OK: all gates passed');
