#!/usr/bin/env node
/**
 * g9.author build + mechanical-validator step (frozen record registry/experiments/g9.json;
 * DAG node g9.author: "author N>=50 machine explications inside the validator loop").
 *
 * Consumes the authored per-concept specs (src/batch-*.mjs, 50 concepts = the frozen
 * seed-0 selection in selection/selected-50.json) and emits, deterministically:
 *
 *   concepts/<slug>.json        the authored explication set (kot-ast/1 docs)
 *   review/sheets.json          BLINDED review sheets for g9.review (GATE-H): dataset
 *                               fields needed by the Baartmans et al. substitutability /
 *                               cross-translatability review + our candidate explication
 *                               text; the dataset's own reference explication and the
 *                               authoring notes are NEVER included (selection-manifest
 *                               blinding rule). Sheet order = seed-0 Fisher-Yates.
 *   review/sheet-key.json       unblinding key (sheet_id -> slug/datasetId), for scoring
 *                               AFTER review only.
 *   validation/validator-report.json   per-concept mechanical gate results
 *   validation/mechanical-summary.json mechanical (legality-leg) metrics + the pinned
 *                               DeepNSM-8B comparison. MECHANICAL CEILING ONLY: the
 *                               composite metric additionally requires g9.review.
 *   validation/loop-log.jsonl   append-only trace of validator-loop iterations.
 *
 * Mechanical gates (the machine-checkable "legality" leg of the composite bar):
 *   1. validateExplication — profile-1 grammar/valency/referent gates (encoder/src/validate.ts)
 *   2. encodeExplication + vector sanity (unit norm, no NaN) — encodability under the
 *      pinned encoder (frozen pins.encoder_hash must match encoderContentHash()).
 * Substitutability + cross-translatability are HUMAN-REVIEW metrics (Baartmans et al.,
 * arXiv:2505.11764, definitions reused as-is) — scored at g9.review, never here.
 *
 * Wilson bound: one-sided 95% score bound, z = 1.645 (P8 C-1), same formula as the
 * pinned analysis/g9.py. Float64 end-to-end, no rounding before comparison (P8 C-7).
 */
import { readFileSync, writeFileSync, mkdirSync, appendFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const require = createRequire(import.meta.url);
const enc = require('../../../encoder/dist/src/index.js');

// Frozen pins (registry/experiments/g9.json) — fail closed on drift.
const FROZEN_ENCODER_HASH = '40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c';
// DeepNSM-8B published composite point estimate, as pinned in the frozen record
// (design.arms_mandatory_baselines: "~24/100 self-metric") and in the pinned
// analysis/g9.py input contract (deepnsm_published_point_x100 = 24).
const DEEPNSM_PUBLISHED_POINT = 0.24;
const MARGIN = 0.10; // pre-defined margin substituting for CI overlap (kill criterion verbatim)
const Z = 1.645; // one-sided alpha=0.05 (P8 C-1), identical to analysis/g9.py

if (enc.encoderContentHash() !== FROZEN_ENCODER_HASH) {
  console.error(`ERR_ENCODER_PIN: encoder ${enc.encoderContentHash()} != frozen ${FROZEN_ENCODER_HASH}`);
  process.exit(1);
}

// --- load authored specs + frozen selection ---------------------------------
const batches = ['a', 'b', 'c', 'd', 'e'];
const specs = [];
for (const b of batches) {
  const mod = await import(`./batch-${b}.mjs`);
  for (const s of mod.default) specs.push({ ...s, batch: b });
}
const selection = JSON.parse(readFileSync(join(root, 'selection', 'selected-50.json'), 'utf8'));
const manifest = JSON.parse(readFileSync(join(root, 'selection', 'selection-manifest.json'), 'utf8'));
const rowById = new Map(selection.map((r) => [r.id, r]));

const specIds = specs.map((s) => s.datasetId).sort((x, y) => x - y);
const selIds = [...manifest.selected_ids].sort((x, y) => x - y);
if (JSON.stringify(specIds) !== JSON.stringify(selIds)) {
  console.error('ERR_SELECTION_MISMATCH: authored datasetIds != frozen seed-0 selection');
  process.exit(1);
}
if (new Set(specs.map((s) => s.slug)).size !== specs.length) {
  console.error('ERR_DUP_SLUG');
  process.exit(1);
}
for (const s of specs) {
  if (typeof s.gloss !== 'string' || s.gloss.length < 20) {
    console.error(`ERR_MISSING_GLOSS: ${s.slug}`);
    process.exit(1);
  }
}

// --- mechanical gates --------------------------------------------------------
const rows = [];
let nLegal = 0;
let nEncodeOk = 0;
for (const s of specs.sort((a, b) => a.slug.localeCompare(b.slug))) {
  const row = {
    id: `urn:g9-author:${s.slug}`, slug: s.slug, datasetId: s.datasetId,
    word: rowById.get(s.datasetId).word, frame: s.explication.frame,
    legal: false, encode_ok: false, errors: [],
  };
  try {
    const stats = enc.validateExplication(s.explication);
    Object.assign(row, stats);
    row.legal = true;
    nLegal += 1;
  } catch (e) {
    row.errors.push({ gate: 'validateExplication', code: e.code ?? 'ERR', message: e.message });
  }
  if (row.legal) {
    try {
      const v = enc.encodeExplication(s.explication);
      let ss = 0; let nan = false;
      for (let i = 0; i < v.length; i++) { ss += v[i] * v[i]; if (Number.isNaN(v[i])) nan = true; }
      const norm = Math.sqrt(ss);
      if (nan) throw Object.assign(new Error('vector contains NaN'), { code: 'ERR_VECTOR_NAN' });
      if (Math.abs(norm - 1) > 1e-9) throw Object.assign(new Error(`norm ${norm}`), { code: 'ERR_VECTOR_NORM' });
      row.encode_ok = true;
      row.dim = v.length;
      nEncodeOk += 1;
    } catch (e) {
      row.errors.push({ gate: 'encodeExplication', code: e.code ?? 'ERR', message: e.message });
    }
  }
  rows.push(row);
}
const nPass = rows.filter((r) => r.legal && r.encode_ok).length;

// --- validator-loop trace ----------------------------------------------------
const ensureDir = (d) => mkdirSync(join(root, d), { recursive: true });
ensureDir('validation');
appendFileSync(join(root, 'validation', 'loop-log.jsonl'), JSON.stringify({
  ts: new Date().toISOString(), n: rows.length, n_legal: nLegal, n_encode_ok: nEncodeOk,
  n_mechanical_pass: nPass,
  failures: rows.filter((r) => r.errors.length).map((r) => ({ slug: r.slug, errors: r.errors })),
}) + '\n');

// --- write the authored concept docs ------------------------------------------
ensureDir('concepts');
for (const s of specs) {
  const doc = {
    id: `urn:g9-author:${s.slug}`,
    datasetId: s.datasetId,
    word: rowById.get(s.datasetId).word,
    label: s.label,
    status: 'g9-authored',
    arm: 'fable-class-authoring',
    gloss: s.gloss,
    ...(s.notes ? { notes: s.notes } : {}),
    references: [],
    explication: s.explication,
  };
  writeFileSync(join(root, 'concepts', `${s.slug}.json`), JSON.stringify(doc, null, 2) + '\n');
}

// --- blinded review sheets (g9.review inputs) ----------------------------------
// seed-0 Fisher-Yates over slug-sorted order; mulberry32 PRNG (recorded here for audit).
ensureDir('review');
const mulberry32 = (a) => () => {
  a |= 0; a = (a + 0x6D2B79F5) | 0;
  let t = Math.imul(a ^ (a >>> 15), 1 | a);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const rng = mulberry32(0);
const order = specs.map((_, i) => i);
for (let i = order.length - 1; i > 0; i--) {
  const j = Math.floor(rng() * (i + 1));
  [order[i], order[j]] = [order[j], order[i]];
}
const sheets = order.map((idx, k) => {
  const s = specs[idx];
  const r = rowById.get(s.datasetId);
  return {
    sheet_id: k + 1,
    word: r.word,
    def: r.def,
    syn: r.syn,
    examples: r.examples,
    ambig_examples: r.ambig_examples,
    candidate_explication: s.gloss,
  };
});
writeFileSync(join(root, 'review', 'sheets.json'), JSON.stringify({
  _instructions: 'BLINDED materials for g9.review (GATE-H, ~4h): score each candidate explication on the Baartmans et al. (arXiv:2505.11764, DeepNSM) metric definitions REUSED AS-IS — substitutability (does the explication substitute for the word in the examples / for <UNK> in ambig_examples?) and cross-translatability, plus a legality spot-check. The dataset reference explication and all authoring notes are withheld from this file by design (selection-manifest blinding rule) and must not be consulted before scoring. The review-stage owner administers the questionnaire per the published metric definitions; this file only carries the blinded materials.',
  sheet_order: 'seed-0 mulberry32 Fisher-Yates over slug-sorted concepts (src/build.mjs)',
  n_sheets: sheets.length,
  sheets,
}, null, 2) + '\n');
writeFileSync(join(root, 'review', 'sheet-key.json'), JSON.stringify({
  _note: 'UNBLINDING KEY — for scoring after g9.review only; never shown with the sheets.',
  key: order.map((idx, k) => ({ sheet_id: k + 1, slug: specs[idx].slug, datasetId: specs[idx].datasetId })),
}, null, 2) + '\n');

// --- validator report + mechanical summary --------------------------------------
const wilson = (p, n) => {
  if (n <= 0) return [0, 1];
  const z2 = Z * Z;
  const centre = p + z2 / (2 * n);
  const spread = Z * Math.sqrt(p * (1 - p) / n + z2 / (4 * n * n));
  return [(centre - spread) / (1 + z2 / n), (centre + spread) / (1 + z2 / n)];
};
writeFileSync(join(root, 'validation', 'validator-report.json'), JSON.stringify({
  schema: 'g9-validator-report/1',
  node: 'g9.author',
  encoder_hash: enc.encoderContentHash(),
  gates: ['validateExplication (profile-1 grammar/valency/referent gates)', 'encodeExplication + unit-norm/NaN sanity'],
  n_explications: rows.length,
  n_legal: nLegal,
  n_encode_ok: nEncodeOk,
  n_mechanical_pass: nPass,
  concepts: rows,
}, null, 2) + '\n');

const thr = DEEPNSM_PUBLISHED_POINT + MARGIN;
const rate = nPass / rows.length;
const [lb, ub] = wilson(rate, rows.length);
// Review-stage bar pre-computation (P8 §1.6 decidability discipline): the smallest
// review-composite pass count k whose Wilson LB clears the margin, and the largest
// k still in the FAIL region (Wilson UB < threshold); between them = INCONCLUSIVE band.
let kMinPass = null; let kMaxFail = null;
for (let k = 0; k <= rows.length; k++) {
  const [klb, kub] = wilson(k / rows.length, rows.length);
  if (kMinPass === null && klb >= thr) kMinPass = k;
  if (kub < thr) kMaxFail = k;
}
writeFileSync(join(root, 'validation', 'mechanical-summary.json'), JSON.stringify({
  schema: 'g9-mechanical-summary/1',
  node: 'g9.author',
  epistemic_status: 'MEASURED (mechanical legality leg only). NOT the composite endpoint: the composite validator bar additionally requires substitutability + cross-translatability from g9.review (GATE-H, blinded human review). blinded_review_done=0 at this node, so /gates/instrument_valid is FALSE by construction and NO verdict is claimable here. The mechanical pass rate is an UPPER BOUND on the composite rate (an explication failing the mechanical gates cannot pass the composite bar).',
  arm: 'fable-class-authoring',
  n_explications: rows.length,
  n_mechanical_pass: nPass,
  mechanical_pass_rate: rate,
  mechanical_ceiling_wilson_lb: lb,
  mechanical_ceiling_wilson_ub: ub,
  pinned_comparison: {
    baseline: 'deepnsm-8b-published-point-estimate',
    deepnsm_published_point: DEEPNSM_PUBLISHED_POINT,
    source: 'registry/experiments/g9.json design.arms_mandatory_baselines + analysis/g9.py input contract (deepnsm_published_point_x100=24); published point, CIs unavailable (P7 RT-16 deferred)',
    margin: MARGIN,
    margin_threshold: thr,
    mechanical_ceiling_clears_margin: lb >= thr,
    note: 'mechanical_ceiling_clears_margin only says the gate REMAINS REACHABLE after the mechanical leg; the verdict-bearing test runs on the post-review composite counts through the pinned analysis/g9.py.',
  },
  review_stage_bar: {
    n: rows.length,
    z: Z,
    k_min_composite_pass_for_PASS: kMinPass,
    k_max_composite_pass_for_FAIL: kMaxFail,
    inconclusive_band: [kMaxFail === null ? 0 : kMaxFail + 1, kMinPass === null ? rows.length : kMinPass - 1],
    detectable_alternative: 'reliable clearance of 0.34 at n=50 needs true composite rate >~0.54 (frozen record n_planned.detectable_alternative; expected rate 0.60 declared)',
  },
  encoder_hash: enc.encoderContentHash(),
}, null, 2) + '\n');

// --- console readout -------------------------------------------------------------
console.log(`g9.author build: ${rows.length} concepts; legal ${nLegal}/${rows.length}; encode-ok ${nEncodeOk}/${rows.length}; mechanical pass ${nPass}/${rows.length}`);
console.log(`mechanical ceiling: rate ${rate.toFixed(4)}, Wilson(z=1.645) [${lb.toFixed(4)}, ${ub.toFixed(4)}] vs margin threshold ${thr.toFixed(2)} (pinned DeepNSM point ${DEEPNSM_PUBLISHED_POINT} + ${MARGIN})`);
console.log(`review bar at n=${rows.length}: PASS needs >=${kMinPass} composite passes; FAIL locked at <=${kMaxFail}; INCONCLUSIVE between.`);
for (const r of rows.filter((x) => x.errors.length)) {
  for (const e of r.errors) console.log(`  FAIL ${r.slug}: [${e.gate}] ${e.code}: ${e.message}`);
}
process.exit(rows.length === nPass ? 0 : 1);
