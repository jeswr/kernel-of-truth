#!/usr/bin/env node
/**
 * P3-X-SIEVE-CENSUS (best-effort) — the lemma-touch UPPER SIEVE coverage census.
 *
 * WHAT THIS IS. POWER.md §2.1(a) names the "lemma-touch upper sieve" as the ONE
 * mechanical, genuinely-cheap (CPU-only, no human annotation) census tier that
 * can license an UNCONDITIONAL coverage-ceiling kill: it marks an item covered
 * iff ANY kernel/world-layer lemma is touched by the item's surface content. It
 * strictly OVER-counts coverage, so
 *
 *     kappa_mapper-parse  <=  kappa_oracle  <=  kappa_upper-sieve       (POWER.md §2.1)
 *
 * and since Delta_max is monotone increasing in kappa, the sieve gives the
 * LARGEST defensible Delta_max. A kill that fires even under the sieve is
 * coverage-sound with no annotation (POWER.md §2.1(a), §3.3). Conversely, if the
 * sieve coverage is materially non-zero, NO sound kill fires on that slice.
 *
 * MACHINERY REUSE (byte-for-byte the d-ext / m0b covered-lemma set). This script
 * imports the SAME mapper primitives (buildLexicon, loadManifestConcepts,
 * lemmaCandidates, irregularBase, targetKey) and the SAME M0b FUNCTION_STOPLIST
 * and molecules-v0 corpusLemmas that data/d-ext/build-dext.mjs uses, so the
 * covered-lemma vocabulary here is identical to the audited d-ext build
 * (190 lemmas = 126 mapper-lexicon + 54 molecules records + labels). The store
 * is kernel-v0 + molecules-v0 (the m0b instance of 2026-07-08).
 *
 * CENSUS (not a selection). d-ext used this machinery to SELECT covered items;
 * here we COUNT them exhaustively per benchmark. The sieve predicate on an item
 * is: surface(item) contains >= 1 covered content lemma, where surface = the
 * item text AS PRESENTED (question stem + every answer-choice text). This is the
 * loosest, most over-counting reading (no gold parse, no endorsement, no
 * uniqueness filter, no correct-answer restriction) — exactly the upper sieve.
 *
 * OUTPUT: poc/coverage-census/sieve-census.json — per-benchmark n_total,
 * touched_count, kappa_upper_sieve; deterministic (no RNG, no clock input).
 *
 * Tag: [MEASURED] counts; [STIPULATED] the surface = question+choices choice.
 */
import { createHash } from 'node:crypto';
import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  buildLexicon, irregularBase, lemmaCandidates, loadManifestConcepts, targetKey,
} from '../../mapper/dist/src/index.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..');

function die(code, msg) { console.error(`${code}: ${msg}`); process.exit(1); }
function sha256(buf) { return createHash('sha256').update(buf).digest('hex'); }

// ---- covered-lemma set: identical machinery to data/d-ext/build-dext.mjs ----
const M0B_SCRIPT = join(REPO, 'mapper', 'm0', 'run-m0b-vocab.mjs');
const stopMatch = readFileSync(M0B_SCRIPT, 'utf8')
  .match(/const FUNCTION_STOPLIST = new Set\(\[([\s\S]*?)\]\);/);
if (!stopMatch) die('SIEVE_ERR_MACHINERY', 'FUNCTION_STOPLIST not found in run-m0b-vocab.mjs');
const FUNCTION_STOPLIST = new Set(
  (stopMatch[1].match(/'([^']+)'/g) ?? []).map((s) => s.slice(1, -1)),
);
if (FUNCTION_STOPLIST.size !== 204) {
  die('SIEVE_ERR_MACHINERY',
    `FUNCTION_STOPLIST size ${FUNCTION_STOPLIST.size} != 204 (m0b machinery drifted)`);
}

const KERNEL_MANIFEST = join(REPO, 'data', 'kernel-v0', 'manifest.json');
const lexicon = buildLexicon(loadManifestConcepts(KERNEL_MANIFEST));
const coveredWhy = new Map();
function addWhy(lemma, why) {
  const l = String(lemma).toLowerCase();
  if (!coveredWhy.has(l)) coveredWhy.set(l, new Set());
  coveredWhy.get(l).add(why);
}
for (const [lemma, entries] of lexicon.single) {
  for (const e of entries) addWhy(lemma, `mapper-lexicon:${targetKey(e.target)}`);
}
const MOL_DIR = join(REPO, 'data', 'molecules-v0', 'molecules');
let molCount = 0;
for (const name of readdirSync(MOL_DIR).sort()) {
  if (!name.endsWith('.json')) continue;
  molCount += 1;
  const rec = JSON.parse(readFileSync(join(MOL_DIR, name), 'utf8'));
  addWhy(rec.label, `molecules-v0:label:${rec.id}`);
  for (const w of rec.corpusLemmas ?? []) addWhy(w, `molecules-v0:corpusLemma:${rec.id}`);
}
if (molCount !== 54) die('SIEVE_ERR_SOURCE', `expected 54 molecule records, got ${molCount}`);

const TOKEN = /[a-z]+/g;
function coveredLemmasIn(text) {
  const out = new Set();
  for (const tok of (String(text).toLowerCase().match(TOKEN) ?? [])) {
    if (FUNCTION_STOPLIST.has(tok)) continue;
    const irr = irregularBase(tok);
    const cands = new Set([tok, ...(irr ? [irr] : []), ...lemmaCandidates(tok)]);
    for (const c of cands) {
      if (FUNCTION_STOPLIST.has(c)) continue;
      if (coveredWhy.has(c)) out.add(c);
    }
  }
  return out;
}

// -------------------------------- benchmark loaders (surface = question+choices)
function loadOBQA() {
  // OpenBookQA-test: the 500-item test split (matches b-cov-define-lane denom).
  const path = join(REPO, 'data', 'd-ext', 'source-jsonl', 'test.jsonl');
  return readFileSync(path, 'utf8').trim().split('\n').map((l) => {
    const r = JSON.parse(l);
    const surface = `${r.question_stem} ${(r.choices?.text ?? []).join(' ')}`;
    return { id: r.id, surface };
  });
}
function loadMMLU(subjectFile) {
  const path = join(REPO, 'poc', 'b-cov-define-lane', 'data', subjectFile);
  return readFileSync(path, 'utf8').trim().split('\n').map((l, i) => {
    const r = JSON.parse(l);
    const surface = `${r.question} ${(r.choices ?? []).join(' ')}`;
    return { id: `${subjectFile}:${i}`, surface };
  });
}

const BENCHMARKS = [
  { name: 'OpenBookQA-test', domain: 'D3', load: loadOBQA },
  { name: 'MMLU-college_biology-test', domain: 'D3', load: () => loadMMLU('mmlu-college_biology-test.jsonl') },
  { name: 'MMLU-college_chemistry-test', domain: 'D3', load: () => loadMMLU('mmlu-college_chemistry-test.jsonl') },
  { name: 'MMLU-medical_genetics-test', domain: 'D3', load: () => loadMMLU('mmlu-medical_genetics-test.jsonl') },
  { name: 'MMLU-anatomy-test', domain: 'D3', load: () => loadMMLU('mmlu-anatomy-test.jsonl') },
  { name: 'MMLU-clinical_knowledge-test', domain: 'D3', load: () => loadMMLU('mmlu-clinical_knowledge-test.jsonl') },
  { name: 'MMLU-nutrition-test', domain: 'D3', load: () => loadMMLU('mmlu-nutrition-test.jsonl') },
];

const results = [];
for (const b of BENCHMARKS) {
  const items = b.load();
  let touched = 0;
  let sumLemmaTypes = 0;
  for (const it of items) {
    const cov = coveredLemmasIn(it.surface);
    if (cov.size > 0) touched += 1;
    sumLemmaTypes += cov.size;
  }
  results.push({
    benchmark: b.name, domain: b.domain,
    n_total: items.length, touched_count: touched,
    kappa_upper_sieve: items.length ? touched / items.length : 0,
    mean_covered_lemma_types_per_item: items.length ? sumLemmaTypes / items.length : 0,
  });
}

const out = {
  artifact: 'P3-X-SIEVE-CENSUS (best-effort) — lemma-touch upper-sieve coverage census',
  epistemic_tag: 'MEASURED (counts); STIPULATED (surface = question stem + choice texts)',
  coverage_lane: 'upper-sieve',
  census_mode: 'exhaustive',
  sieve_predicate: 'item covered iff (question_stem + all choice texts) contains >= 1 covered content lemma (m0b lemmaCandidates/irregularBase, minus FUNCTION_STOPLIST)',
  store: {
    kernel: 'kernel-v0 (data/kernel-v0/manifest.json)',
    molecules: 'molecules-v0 (54 records)',
    covered_lemma_types: coveredWhy.size,
    stoplist_size: FUNCTION_STOPLIST.size,
    machinery: 'mapper/dist buildLexicon+lemmaCandidates+irregularBase (identical to data/d-ext/build-dext.mjs)',
  },
  benchmarks: results,
  totals: {
    n_total: results.reduce((a, r) => a + r.n_total, 0),
    touched_count: results.reduce((a, r) => a + r.touched_count, 0),
  },
};
out.totals.kappa_upper_sieve_pooled = out.totals.touched_count / out.totals.n_total;
const outPath = join(HERE, 'sieve-census.json');
writeFileSync(outPath, `${JSON.stringify(out, null, 2)}\n`);
console.log(`covered_lemma_types=${coveredWhy.size} stoplist=${FUNCTION_STOPLIST.size}`);
for (const r of results) {
  console.log(`${r.benchmark.padEnd(30)} D3  n=${String(r.n_total).padStart(4)}  touched=${String(r.touched_count).padStart(4)}  kappa_sieve=${r.kappa_upper_sieve.toFixed(4)}  mean_lemmas/item=${r.mean_covered_lemma_types_per_item.toFixed(2)}`);
}
console.log(`POOLED  n=${out.totals.n_total}  touched=${out.totals.touched_count}  kappa_sieve=${out.totals.kappa_upper_sieve_pooled.toFixed(4)}`);
console.log(`[wrote ${outPath}] sha256=${sha256(readFileSync(outPath))}`);
