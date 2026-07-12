#!/usr/bin/env node
/**
 * DDC T0 ops — kernel-side asset builder (docs/next/design/DDC.md §2.2/§2.3;
 * T0 stage row §6; ASM-1651 corpus recipe, ASM-1700 probe construction;
 * T0 build stipulations emitted as PROPOSED-ASM-1790..1799,
 * poc/ddc/asm-1790-1799.json).
 *
 * Produces (deterministic, re-runnable, $0):
 *   <out>/committed-renders.jsonl   one row per committed concept record:
 *       {kind: "prime"|"kernel-v0"|"molecules-v0", id, text}
 *       - primes: the chart-order lexicon name verbatim (the same token that
 *         appears in canonical-form v0 renders);
 *       - kernel-v0: renderExplication over the committed kot-ast/1 record;
 *       - molecules-v0: the committed groundingNote (NSM-controlled gloss) —
 *         molecules carry NO explication AST (partialExplication: null in
 *         every committed record), so they contribute CORPUS TEXT only and
 *         are NEVER probe-paired (the §2.3 pairing needs a canonical
 *         encoder vector; n = 119 = 65 primes + 54 kernel-v0).
 *   <out>/synth-pool.jsonl          seeded generateExplication expansion
 *       across the house depth x clause-count mixture (poc/src/x1-q.ts
 *       corpusShape, reused verbatim), seed strings "ddc-kstatic|0|<i>"
 *       (ASM-1651 seed 0): {i, topClauses, depth, text}. The python
 *       assembler applies the <=256-token cap (donor tokenizer) +
 *       exact-duplicate dedup and cuts the corpus at N=4096.
 *   data/ddc-probe-fixture-v1/probe-fixture.json   the §2.3 carrier-
 *       controlled probe fixture (schema kot-ddc-probe-fixture/1, the
 *       g0_runner.py documented schema), vectors at kot-enc-Bq/1 D=576,
 *       built TWICE in-process; determinism.sha_run1/sha_run2 = sha256 over
 *       the canonical JSON of the payload WITHOUT the determinism block
 *       (gate /gates/probe_fixture_deterministic).
 *   <out>/mc-report.json            minimal-contrast construction report
 *       (committed-pair detection + synthetic top-up disclosure).
 *
 * Probe fixture construction, stated exactly:
 *   - concepts: 65 primes (class "prime", canonical vector = the
 *     quasi-orthogonal 'head'-slot atom for the prime name — the concept's
 *     own codebook atom; structure-free, so bag_vector = vector) +
 *     54 kernel-v0 explications (class "kernel-v0", canonical vector =
 *     encodeConceptSetQ at D=576 over the committed reference DAG;
 *     bag_vector = unit-normalised prime-multiset superposition of
 *     'head'-slot atoms with concept references recursively expanded —
 *     roles, clause order, and depth deleted, §2.3 criterion 4) +
 *     30 synthetic minimal-contrast pairs (60 concepts, class
 *     "synthetic-minimal-contrast": seeded generateExplication bases +
 *     mutateExplication single edits — operator-flip / clause-swap /
 *     referent-index / filler-substitution, exactly the §2.3 "one prime,
 *     role, clause order, depth, or polarity" edit family). Committed
 *     records contain no single-edit pairs (detector below reports the
 *     count), so the stratum must be synthetic for §2.3 criterion 3 to be
 *     non-degenerate; the harness houses the stratum in SEL by
 *     intersection (g0_runner.stage_stats).
 *   - carriers: P=4 fixed templates x 2 seeded render variants per concept
 *     (ASM-1700). Variant 0 = canonical text. Variant 1 = clause-rotated
 *     render (rotation offset 1 + sha256("ddc-probe-rot|<id>") mod (C-1))
 *     for multi-clause explications; the trailing allolex for '~'-named
 *     primes; else the canonical text duplicated (disclosed count).
 *   - empty_carriers: the 4 templates with the rendering slot empty.
 *
 * Zero network. Everything fails closed. This module states NO feasibility
 * conclusion.
 */

import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..', '..', '..');
const ENC = join(ROOT, 'encoder', 'dist', 'src', 'index.js');

const {
  PRIMES,
  PRIME_BY_NAME,
  canonicalJson,
  renderExplication,
  generateExplication,
  mutateExplication,
  encodeConceptSetQ,
  getQuasiCodebook,
  validateExplication,
} = await import(ENC);

const D = 576; // SmolLM2-135M d_model; kot-enc-Bq/1 native dimension (§2.3)
const N_SYNTH_POOL = 6000; // candidate pool; python cuts at N=4096 (ASM-1651)
const N_MC_PAIRS = 30; // synthetic minimal-contrast pairs (PROPOSED-ASM-1792)

// P=4 fixed carrier templates (ASM-1700; PROPOSED-ASM-1791). %s = rendering.
const CARRIER_TEMPLATES = [
  '%s',
  'The defined concept means: %s',
  'Definition: %s\n->',
  'Here is a definition: %s\nWhat concept does this define?',
];

function sha256(text) {
  return createHash('sha256').update(text, 'utf8').digest('hex');
}

function detInt(label) {
  return parseInt(sha256(label).slice(0, 12), 16);
}

function die(code, msg) {
  console.error(`${code}: ${msg}`);
  process.exit(1);
}

// --------------------------------------------------------------------------
// committed records
// --------------------------------------------------------------------------

function loadKernelV0() {
  const dir = join(ROOT, 'data', 'kernel-v0', 'concepts');
  const out = [];
  for (const f of readdirSync(dir).filter((f) => f.endsWith('.json')).sort()) {
    const rec = JSON.parse(readFileSync(join(dir, f), 'utf8'));
    if (!rec.explication) die('ERR_T0_RECORD', `${f} has no explication`);
    out.push(rec);
  }
  if (out.length !== 54) die('ERR_T0_RECORD', `kernel-v0 count ${out.length} != 54`);
  return out;
}

function loadMolecules() {
  const dir = join(ROOT, 'data', 'molecules-v0', 'molecules');
  const out = [];
  for (const f of readdirSync(dir).filter((f) => f.endsWith('.json')).sort()) {
    const rec = JSON.parse(readFileSync(join(dir, f), 'utf8'));
    if (rec.explication || rec.partialExplication) {
      die('ERR_T0_RECORD',
        `${f} carries an explication — the molecules-are-text-only premise `
        + 'of this builder is broken; re-decide the probe inventory');
    }
    if (!rec.groundingNote) die('ERR_T0_RECORD', `${f} has no groundingNote`);
    out.push(rec);
  }
  if (out.length !== 54) die('ERR_T0_RECORD', `molecules count ${out.length} != 54`);
  return out;
}

// --------------------------------------------------------------------------
// bag-of-primes multiset (roles, clause order, depth deleted; §2.3 crit. 4)
// --------------------------------------------------------------------------

function bagPrimes(expl, defsById, counts, seen) {
  for (const cl of expl.clauses) bagClause(cl, defsById, counts, seen);
}

function addPrime(name, counts) {
  if (PRIME_BY_NAME.has(name)) counts.set(name, (counts.get(name) || 0) + 1);
}

function bagFiller(f, defsById, counts, seen) {
  if (!f || typeof f !== 'object') return;
  switch (f.kind) {
    case 'prime': addPrime(f.prime, counts); break;
    case 'sp': bagSP(f, defsById, counts, seen); break;
    case 'concept': bagConcept(f.id, defsById, counts, seen); break;
    case 'clause': bagClause(f.clause, defsById, counts, seen); break;
    case 'quote':
      for (const c of f.clauses) bagClause(c, defsById, counts, seen);
      break;
    case 'temporal':
      addPrime(f.op, counts);
      bagFiller(f.anchor, defsById, counts, seen);
      break;
    case 'ref': break; // structure (referent identity), deleted
    default: break;
  }
}

function bagSP(sp, defsById, counts, seen) {
  if (sp.det) addPrime(sp.det, counts);
  if (sp.quant) addPrime(sp.quant, counts);
  for (const m of sp.mods || []) {
    addPrime(m.mod, counts);
    if (m.intensifier) addPrime(m.intensifier, counts);
  }
  const h = sp.head;
  if (h.kind === 'primeHead') addPrime(h.prime, counts);
  else if (h.kind === 'conceptHead') bagConcept(h.id, defsById, counts, seen);
  else if (h.kind === 'kindFrame' || h.kind === 'partFrame') {
    bagFiller(h.of, defsById, counts, seen);
  }
  if (sp.restrictedBy) bagClause(sp.restrictedBy, defsById, counts, seen);
}

function bagConcept(id, defsById, counts, seen) {
  // recursive expansion of concept references (closure of the bag)
  if (seen.has(id)) return;
  seen.add(id);
  const e = defsById.get(id);
  if (!e) die('ERR_T0_BAG', `unresolved concept reference ${id}`);
  bagPrimes(e, defsById, counts, seen);
}

function bagClause(cl, defsById, counts, seen) {
  if (cl.type === 'pred') {
    addPrime(cl.pred, counts);
    for (const f of Object.values(cl.roles || {})) {
      bagFiller(f, defsById, counts, seen);
    }
  } else if (cl.type === 'op') {
    addPrime(cl.op, counts);
    for (const a of cl.args || []) {
      if (a && a.type) bagClause(a, defsById, counts, seen);
      else bagFiller(a, defsById, counts, seen);
    }
  }
}

function bagVector(expl, defsById, qcb) {
  const counts = new Map();
  bagPrimes(expl, defsById, counts, new Set());
  if (counts.size === 0) die('ERR_T0_BAG', 'empty prime multiset');
  const v = new Float64Array(D);
  for (const [name, c] of [...counts.entries()].sort()) {
    const atom = qcb.boundAtom('head', `prime:${name}`);
    for (let i = 0; i < D; i++) v[i] += c * atom[i];
  }
  let norm = 0;
  for (let i = 0; i < D; i++) norm += v[i] * v[i];
  norm = Math.sqrt(norm);
  if (!(norm > 0)) die('ERR_T0_BAG', 'zero-norm bag vector');
  for (let i = 0; i < D; i++) v[i] /= norm;
  return v;
}

// --------------------------------------------------------------------------
// render variants (ASM-1700 "seeded render variants"; PROPOSED-ASM-1791)
// --------------------------------------------------------------------------

function rotatedRender(expl, id) {
  const C = expl.clauses.length;
  if (C < 2) return null;
  const r = 1 + (detInt(`ddc-probe-rot|${id}`) % (C - 1));
  const rotated = {
    schema: expl.schema,
    frame: expl.frame,
    referents: expl.referents,
    clauses: [...expl.clauses.slice(r), ...expl.clauses.slice(0, r)],
  };
  try {
    validateExplication(rotated);
    return renderExplication(rotated);
  } catch {
    return null; // fall back to duplicate canonical (disclosed)
  }
}

function primeVariant(name) {
  if (!name.includes('~')) return null;
  const parts = name.split('~');
  return parts[parts.length - 1];
}

// --------------------------------------------------------------------------
// minimal-contrast: committed-pair detector + synthetic top-up
// --------------------------------------------------------------------------

function clauseTokens(cl) {
  return canonicalJson(cl).split(/[^A-Za-z0-9~'+-]+/).filter((t) => t);
}

function detectCommittedPairs(records) {
  const found = [];
  for (let a = 0; a < records.length; a++) {
    for (let b = a + 1; b < records.length; b++) {
      const ea = records[a].explication;
      const eb = records[b].explication;
      if (ea.frame !== eb.frame) continue;
      if (canonicalJson(ea.referents) !== canonicalJson(eb.referents)) continue;
      const ca = ea.clauses.map((c) => canonicalJson(c));
      const cb = eb.clauses.map((c) => canonicalJson(c));
      if (ca.length === cb.length
          && canonicalJson([...ca].sort()) === canonicalJson([...cb].sort())
          && canonicalJson(ca) !== canonicalJson(cb)) {
        found.push([records[a].id, records[b].id, 'clause-order']);
        continue;
      }
      if (ca.length !== cb.length) continue;
      const diffs = [];
      for (let i = 0; i < ca.length; i++) if (ca[i] !== cb[i]) diffs.push(i);
      if (diffs.length !== 1) continue;
      const ta = clauseTokens(ea.clauses[diffs[0]]);
      const tb = clauseTokens(eb.clauses[diffs[0]]);
      if (ta.length === tb.length
          && ta.filter((t, i) => t !== tb[i]).length === 1) {
        found.push([records[a].id, records[b].id, 'single-token']);
      }
    }
  }
  return found;
}

function synthMcPairs(defsById, qcb, encodeOne) {
  const pairs = [];
  const concepts = [];
  const editCounts = {};
  let k = 0;
  let tried = 0;
  const TC = [2, 3, 4];
  const DEP = [2, 3];
  while (pairs.length < N_MC_PAIRS && tried < 500) {
    const seed = `ddc-mc|0|${tried}`;
    tried += 1;
    let base;
    try {
      base = generateExplication({
        seed,
        topClauses: TC[tried % TC.length],
        depth: DEP[tried % DEP.length],
      });
    } catch {
      continue;
    }
    const mut = mutateExplication(base, `ddc-mc-edit|0|${tried}`);
    if (!mut) continue;
    let vBase;
    let vMut;
    let rBase;
    let rMut;
    try {
      vBase = encodeOne(base);
      vMut = encodeOne(mut.mutant);
      rBase = renderExplication(base);
      rMut = renderExplication(mut.mutant);
    } catch {
      continue;
    }
    if (rBase === rMut) continue;
    const idBase = `ddc-mc-${String(k).padStart(2, '0')}-base`;
    const idMut = `ddc-mc-${String(k).padStart(2, '0')}-mut`;
    concepts.push(
      { id: idBase, cls: 'synthetic-minimal-contrast', expl: base, v: vBase },
      { id: idMut, cls: 'synthetic-minimal-contrast', expl: mut.mutant, v: vMut },
    );
    pairs.push([idBase, idMut]);
    editCounts[mut.edit] = (editCounts[mut.edit] || 0) + 1;
    k += 1;
  }
  if (pairs.length < N_MC_PAIRS) {
    die('ERR_T0_MC', `only ${pairs.length}/${N_MC_PAIRS} synthetic pairs `
      + `after ${tried} attempts`);
  }
  return { pairs, concepts, editCounts, tried };
}

// --------------------------------------------------------------------------
// fixture payload (built twice for the determinism gate)
// --------------------------------------------------------------------------

function buildPayload() {
  const kernel = loadKernelV0();
  const qcb = getQuasiCodebook(D);

  // canonical vectors for the committed reference DAG at D=576
  const defs = new Map(kernel.map((r) => [r.id, r.explication]));
  const { vectors } = encodeConceptSetQ(defs, { params: { D } });
  const defsById = defs;
  const encodeOne = (expl) => {
    const tmp = new Map([['__mc__', expl]]);
    return encodeConceptSetQ(tmp, { params: { D } }).vectors.get('__mc__');
  };

  const concepts = [];
  let duplicateVariantCount = 0;

  const pushConcept = (id, cls, canonicalText, variantText, vector, bag) => {
    const v1 = variantText || canonicalText;
    if (!variantText) duplicateVariantCount += 1;
    const carriers = CARRIER_TEMPLATES.map((t) => [
      t.replace('%s', canonicalText),
      t.replace('%s', v1),
    ]);
    concepts.push({
      id,
      class: cls,
      vector: Array.from(vector),
      bag_vector: Array.from(bag),
      carriers,
    });
  };

  for (const p of PRIMES) {
    const atom = qcb.boundAtom('head', `prime:${p.name}`);
    pushConcept(`prime:${p.name}`, 'prime', p.name, primeVariant(p.name),
      atom, atom);
  }
  for (const r of kernel) {
    const v = vectors.get(r.id);
    if (!v) die('ERR_T0_ENCODE', `no vector for ${r.id}`);
    pushConcept(r.id, 'kernel-v0', renderExplication(r.explication),
      rotatedRender(r.explication, r.id), v,
      bagVector(r.explication, defsById, qcb));
  }

  const committedPairs = detectCommittedPairs(kernel);
  const mc = synthMcPairs(defsById, qcb, encodeOne);
  for (const c of mc.concepts) {
    pushConcept(c.id, c.cls, renderExplication(c.expl),
      rotatedRender(c.expl, c.id), c.v,
      bagVector(c.expl, defsById, qcb));
  }
  const mcPairs = [
    ...committedPairs.map(([a, b]) => [a, b]),
    ...mc.pairs,
  ];

  const payload = {
    schema: 'kot-ddc-probe-fixture/1',
    encoder: 'kot-enc-Bq/1 D=576 (encoder/dist committed build)',
    carrier_templates: CARRIER_TEMPLATES,
    empty_carriers: CARRIER_TEMPLATES.map((t) => t.replace('%s', '')),
    concepts,
    minimal_contrast_pairs: mcPairs,
    build_disclosure: {
      n_prime: PRIMES.length,
      n_kernel_v0: kernel.length,
      n_synthetic_minimal_contrast: mc.concepts.length,
      committed_single_edit_pairs_detected: committedPairs,
      synthetic_pair_edit_types: mc.editCounts,
      synthetic_pair_attempts: mc.tried,
      duplicate_render_variant_count: duplicateVariantCount,
      variant_rule: 'v0 = canonical; v1 = clause-rotated render '
        + '(1 + sha256("ddc-probe-rot|<id>") mod (C-1)) for multi-clause '
        + 'explications, trailing allolex for ~-named primes, else v0 '
        + 'duplicated',
      bag_rule: 'unit-normalised prime-multiset superposition of '
        + "quasi-codebook 'head'-slot atoms; concept references expanded "
        + 'recursively; roles/clause-order/depth deleted (criterion 4). '
        + 'Prime concepts: bag_vector == vector (an atom has no structure '
        + 'to destroy) — such concepts can only ever admit as lexical.',
      builder: 'poc/ddc/t0/build_kernel_assets.mjs',
    },
  };
  return payload;
}

// --------------------------------------------------------------------------
// main
// --------------------------------------------------------------------------

const outDir = process.argv[2];
if (!outDir) die('ERR_T0_ARGS', 'usage: build_kernel_assets.mjs <out-dir>');
mkdirSync(outDir, { recursive: true });

// 1) committed renders
const kernel = loadKernelV0();
const molecules = loadMolecules();
const committedLines = [];
for (const p of PRIMES) {
  committedLines.push({ kind: 'prime', id: `prime:${p.name}`, text: p.name });
}
for (const r of kernel) {
  committedLines.push({
    kind: 'kernel-v0', id: r.id, text: renderExplication(r.explication),
  });
}
for (const m of molecules) {
  committedLines.push({ kind: 'molecules-v0', id: m.id, text: m.groundingNote });
}
writeFileSync(join(outDir, 'committed-renders.jsonl'),
  committedLines.map((r) => JSON.stringify(r)).join('\n') + '\n');
console.log(`committed renders: ${committedLines.length} `
  + `(${PRIMES.length} primes + ${kernel.length} kernel-v0 + `
  + `${molecules.length} molecules)`);

// 2) synthetic K-static pool (house depth x clause mixture, x1-q corpusShape)
const TC_GRID = [1, 2, 3, 4, 6, 8, 12, 16];
const DEP_GRID = [1, 2, 2, 3, 3, 4, 5, 2];
const synthRows = [];
let genFailures = 0;
for (let i = 0; synthRows.length < N_SYNTH_POOL && i < N_SYNTH_POOL * 2; i++) {
  const topClauses = TC_GRID[i % 8];
  const depth = DEP_GRID[Math.floor(i / 8) % 8];
  try {
    const ast = generateExplication({
      seed: `ddc-kstatic|0|${i}`, topClauses, depth,
    });
    synthRows.push({ i, topClauses, depth, text: renderExplication(ast) });
  } catch {
    genFailures += 1;
  }
}
writeFileSync(join(outDir, 'synth-pool.jsonl'),
  synthRows.map((r) => JSON.stringify(r)).join('\n') + '\n');
console.log(`synth pool: ${synthRows.length} rows (${genFailures} generator `
  + 'failures skipped)');

// 3) probe fixture — built twice; determinism shas embedded
const p1 = buildPayload();
const p2 = buildPayload();
const sha1 = sha256(canonicalJson(p1));
const sha2 = sha256(canonicalJson(p2));
if (sha1 !== sha2) die('ERR_T0_DETERMINISM', `${sha1} != ${sha2}`);
const fixture = { ...p1, determinism: { sha_run1: sha1, sha_run2: sha2 } };
const fixDir = join(ROOT, 'data', 'ddc-probe-fixture-v1');
mkdirSync(fixDir, { recursive: true });
writeFileSync(join(fixDir, 'probe-fixture.json'),
  JSON.stringify(fixture, null, 1) + '\n');
console.log(`probe fixture: ${p1.concepts.length} concepts `
  + `(sha_run1 == sha_run2 == ${sha1.slice(0, 16)}...) -> ${fixDir}`);

// 4) mc report
writeFileSync(join(outDir, 'mc-report.json'), JSON.stringify({
  committed_single_edit_pairs: p1.build_disclosure
    .committed_single_edit_pairs_detected,
  synthetic_pairs: p1.minimal_contrast_pairs.length
    - p1.build_disclosure.committed_single_edit_pairs_detected.length,
  edit_types: p1.build_disclosure.synthetic_pair_edit_types,
}, null, 1) + '\n');
console.log('done');
