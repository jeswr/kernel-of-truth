#!/usr/bin/env node
/**
 * D-EXT builder — RT-7a externally-authored eval slice (F2/E9 Holm secondary).
 *
 * Frozen sourcing rule (GNG-0 ratification default, registry/experiments/f2.json
 * pins.corpus_hashes["external-eval-slice"], docs/research-plan/06-resources.md
 * D-EXT row): preference order WiC (pilehvar/wic) -> OpenBookQA
 * (allenai/openbookqa) -> MMLU (cais/mmlu); select the FIRST source whose
 * M0b-filtered, leak-checked yield is >= 300 items.
 *
 * Walk record (probed 2026-07-08, unauthenticated, no HF credentials on box):
 *   (1) WiC `pilehvar/wic` — UNAVAILABLE. HTTP 401 from
 *       /api/datasets/pilehvar/wic, from the datasets-server /is-valid probe
 *       ("The dataset does not exist, or is not accessible without
 *       authentication"), and from the dataset web page. WiC copies exist
 *       under other HF namespaces, but none is the pre-declared id;
 *       substituting an unauthenticated mirror would break source provenance
 *       — declined, fail-closed sourcing.
 *   (2) OpenBookQA `allenai/openbookqa` — SELECTED. Revision
 *       388097ea7776314e93a529163e0fea805b8a6454 (refs/heads/main,
 *       cross-checked via /refs). Config `additional` (= `main` columns +
 *       fact1, the core science fact each item tests). Apache-2.0.
 *   (3) MMLU — NOT REACHED.
 *
 * M0b coverage filter (the filter is ours; the items are not). Declared
 * BEFORE yields were measured:
 *   covered lemma set = single-word surfaces of the mapper lexicon
 *     (buildLexicon over data/kernel-v0/manifest.json: 65-prime exponents +
 *     kernel-v0 concept labels, parenthetical-stripped — EXACTLY the
 *     machinery of mapper/m0/run-m0b-vocab.mjs)
 *     UNION molecules-v0 labels UNION molecules-v0 corpusLemmas;
 *   token -> lemma via the same lemmaCandidates/irregularBase machinery,
 *     minus the M0b FUNCTION_STOPLIST (read verbatim from
 *     mapper/m0/run-m0b-vocab.mjs — single source of truth);
 *   R-C (primary rule): an item is kernel-covered iff fact1 contains >= 1
 *     covered content lemma AND (question_stem + correct-answer text)
 *     contains >= 1 covered content lemma;
 *   R-A (pre-declared fallback, fires ONLY if R-C leak-checked yield < 300):
 *     fact1 alone contains >= 1 covered content lemma;
 *   if still < 300: FAIL CLOSED and walk to the next source (MMLU).
 *
 * Selection: leak-check survivors in pinned order validation -> test ->
 * train (source row order within each split; eval splits first because they
 * are less likely to sit in instruction-tuning mixtures), capped at 500
 * items (= frozen design.n_planned.per_arm_items). No randomness anywhere.
 *
 * Leak checks (d-qa LC discipline adapted to external MCQ items; external
 * item text is NEVER edited — violating items are dropped and counted):
 *   LC1-ext  correct-answer text must not appear (word-boundary,
 *            case-insensitive) in the question stem              -> drop
 *   LC4-ext  exactly 4 options, pairwise distinct (normalised),
 *            answerKey present among labels                      -> drop
 *   LC5-ext  no duplicate ids; no duplicate question+options     -> drop later
 *   LC-DQA   no selected item's question equals a d-qa question  -> fail closed
 *   LC7-ext  answer-key balance of the final slice                -> recorded
 *   (d-qa LC2/LC3/LC6 are claim-item-specific: N/A, recorded as such)
 *
 * Deterministic: byte-identical outputs on rebuild. NO LLM authored,
 * selected, or edited any item text. Outputs: covered-lemmas.json,
 * items/external.jsonl, leak-check.json, manifest.json.
 *
 * Run:  node data/d-ext/build-dext.mjs   (after convert-source.py)
 */

import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  buildLexicon, irregularBase, lemmaCandidates, loadManifestConcepts, targetKey,
} from '../../mapper/dist/src/index.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..');
const GENERATED = '2026-07-08';
const CAP = 500;               // = frozen f2 design.n_planned.per_arm_items
const MIN_YIELD = 300;         // frozen selection rule (GNG-0 ratified default)
const SPLIT_ORDER = ['validation', 'test', 'train'];

const SOURCE = {
  hf_repo: 'allenai/openbookqa',
  hf_revision: '388097ea7776314e93a529163e0fea805b8a6454',
  config: 'additional',
  license: 'Apache-2.0',
};

function die(code, msg) {
  console.error(`${code}: ${msg}`);
  process.exit(1);
}

function sha256(buf) {
  return createHash('sha256').update(buf).digest('hex');
}

function fileSha(path) {
  return sha256(readFileSync(path));
}

/** Canonical JSON: recursively key-sorted, no floats emitted by this builder. */
function canon(value) {
  if (Array.isArray(value)) return `[${value.map(canon).join(',')}]`;
  if (value !== null && typeof value === 'object') {
    const keys = Object.keys(value).sort();
    return `{${keys.map((k) => `${JSON.stringify(k)}:${canon(value[k])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function writeCanon(relPath, obj) {
  writeFileSync(join(HERE, relPath), `${canon(obj)}\n`);
}

// ---------------------------------------------------------------- machinery
const M0B_SCRIPT = join(REPO, 'mapper', 'm0', 'run-m0b-vocab.mjs');
const stopMatch = readFileSync(M0B_SCRIPT, 'utf8')
  .match(/const FUNCTION_STOPLIST = new Set\(\[([\s\S]*?)\]\);/);
if (!stopMatch) die('DEXT_ERR_MACHINERY', 'FUNCTION_STOPLIST not found in run-m0b-vocab.mjs');
const FUNCTION_STOPLIST = new Set(
  (stopMatch[1].match(/'([^']+)'/g) ?? []).map((s) => s.slice(1, -1)),
);
if (FUNCTION_STOPLIST.size !== 204) {
  die('DEXT_ERR_MACHINERY',
    `FUNCTION_STOPLIST size ${FUNCTION_STOPLIST.size} != 204 (M0b machinery drifted; re-audit)`);
}

const KERNEL_MANIFEST = join(REPO, 'data', 'kernel-v0', 'manifest.json');
const lexicon = buildLexicon(loadManifestConcepts(KERNEL_MANIFEST));

const coveredWhy = new Map(); // lemma -> sorted provenance keys
function addWhy(lemma, why) {
  const l = lemma.toLowerCase();
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
if (molCount !== 54) die('DEXT_ERR_SOURCE', `expected 54 molecule records, got ${molCount}`);

const TOKEN = /[a-z]+/g;
function coveredLemmasIn(text) {
  const out = new Set();
  for (const tok of (text.toLowerCase().match(TOKEN) ?? [])) {
    if (FUNCTION_STOPLIST.has(tok)) continue;
    const irr = irregularBase(tok);
    const cands = new Set([tok, ...(irr ? [irr] : []), ...lemmaCandidates(tok)]);
    for (const c of cands) {
      if (FUNCTION_STOPLIST.has(c)) continue;
      if (coveredWhy.has(c)) out.add(c);
    }
  }
  return [...out].sort();
}

// ------------------------------------------------------------- load source
function loadSplit(split) {
  const path = join(HERE, 'source-jsonl', `${split}.jsonl`);
  return readFileSync(path, 'utf8').trim().split('\n').map((l) => JSON.parse(l));
}

const norm = (s) => s.toLowerCase().replace(/\s+/g, ' ').trim();
const wordBoundaryHit = (needle, hay) => {
  const esc = needle.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`(^|[^a-z0-9])${esc}($|[^a-z0-9])`).test(hay.toLowerCase());
};

// --------------------------------------------------------------- filter
const lc = {
  'LC1-ext-answer-not-in-question': { checked: 0, dropped: 0 },
  'LC4-ext-options-wellformed': { checked: 0, dropped: 0 },
  'LC5-ext-no-duplicates': { checked: 0, dropped_duplicate_id: 0, dropped_duplicate_text: 0 },
  'LC7-ext-answer-key-balance': {},
  'LC-DQA-no-collision-with-d-qa': { checked: 0, collisions: 0 },
  'LC2-answer-text-not-in-question': 'N/A — d-qa forced-choice discipline; subsumed by LC1-ext here',
  'LC3-false-claim-not-entailed': 'N/A — no authored false claims; items are external',
  'LC6-true-claims-verbatim-from-record': 'N/A — no kernel-record claims; items are external',
};

let total = 0;
let coveredRA = 0;
let coveredRC = 0;
const perSplitRC = {};
const survivors = [];
const seenIds = new Set();
const seenText = new Set();

for (const split of SPLIT_ORDER) {
  let nSplit = 0;
  for (const row of loadSplit(split)) {
    total += 1;
    // structural well-formedness (LC4-ext) — checked for every row
    lc['LC4-ext-options-wellformed'].checked += 1;
    const labels = row.choices?.label ?? [];
    const texts = row.choices?.text ?? [];
    const ansIdx = labels.indexOf(row.answerKey);
    const distinct = new Set(texts.map(norm));
    if (labels.length !== 4 || texts.length !== 4 || ansIdx < 0
        || distinct.size !== 4 || texts.some((t) => !norm(t))) {
      lc['LC4-ext-options-wellformed'].dropped += 1;
      continue;
    }
    // M0b coverage filter, rule R-C
    const factLemmas = coveredLemmasIn(row.fact1);
    if (factLemmas.length > 0) coveredRA += 1;
    else continue;
    const itemLemmas = coveredLemmasIn(`${row.question_stem} ${texts[ansIdx]}`);
    if (itemLemmas.length === 0) continue;
    coveredRC += 1;
    nSplit += 1;
    // LC1-ext
    lc['LC1-ext-answer-not-in-question'].checked += 1;
    if (wordBoundaryHit(texts[ansIdx], row.question_stem)) {
      lc['LC1-ext-answer-not-in-question'].dropped += 1;
      continue;
    }
    // LC5-ext
    const id = `dext:obqa:${split}:${row.id}`;
    const textKey = norm(`${row.question_stem}||${texts.map(norm).sort().join('||')}`);
    if (seenIds.has(id)) {
      lc['LC5-ext-no-duplicates'].dropped_duplicate_id += 1;
      continue;
    }
    if (seenText.has(textKey)) {
      lc['LC5-ext-no-duplicates'].dropped_duplicate_text += 1;
      continue;
    }
    seenIds.add(id);
    seenText.add(textKey);
    survivors.push({
      answer: row.answerKey,
      covered_lemmas_fact: factLemmas,
      covered_lemmas_item: itemLemmas,
      fact1: row.fact1,
      id,
      kernel_checkable: false,
      options: labels.map((k, i) => ({ key: k, text: texts[i] })),
      question: row.question_stem,
      slice: 'external',
      source: `${SOURCE.hf_repo}@${SOURCE.hf_revision}#${SOURCE.config}`,
      source_id: row.id,
      source_split: split,
      type: 'obqa-mcq',
    });
  }
  perSplitRC[split] = nSplit;
}
lc['LC5-ext-no-duplicates'].checked = coveredRC - lc['LC1-ext-answer-not-in-question'].dropped;

const yieldRC = survivors.length;
if (yieldRC < MIN_YIELD) {
  // pre-declared fallback R-A would be applied here; and below it, the walk
  die('DEXT_ERR_YIELD',
    `R-C leak-checked yield ${yieldRC} < ${MIN_YIELD}: apply pre-declared R-A fallback; `
    + 'if still short, walk to the next source in the frozen preference order (MMLU)');
}
const items = survivors.slice(0, CAP).map((it, i) => ({ ...it, rank: i }));

// LC-DQA: selected external items never collide with self-authored d-qa items
const dqaQuestions = new Set();
for (const f of ['covered.jsonl', 'control.jsonl']) {
  for (const line of readFileSync(join(REPO, 'data', 'd-qa', 'items', f), 'utf8').trim().split('\n')) {
    dqaQuestions.add(norm(JSON.parse(line).question));
  }
}
for (const it of items) {
  lc['LC-DQA-no-collision-with-d-qa'].checked += 1;
  if (dqaQuestions.has(norm(it.question))) lc['LC-DQA-no-collision-with-d-qa'].collisions += 1;
}
if (lc['LC-DQA-no-collision-with-d-qa'].collisions > 0) {
  die('DEXT_ERR_LEAK', 'external item text collides with a d-qa item');
}

// LC7-ext
const balance = { A: 0, B: 0, C: 0, D: 0 };
for (const it of items) balance[it.answer] += 1;
lc['LC7-ext-answer-key-balance'] = balance;

// ------------------------------------------------------------------ outputs
mkdirSync(join(HERE, 'items'), { recursive: true });
writeFileSync(
  join(HERE, 'items', 'external.jsonl'),
  items.map((it) => canon(it)).join('\n') + '\n',
);

writeCanon('covered-lemmas.json', {
  artifact: 'd-ext-covered-lemmas',
  counts: {
    from_mapper_lexicon: [...lexicon.single.keys()].length,
    molecules_records: molCount,
    total_lemmas: coveredWhy.size,
  },
  generated: GENERATED,
  lemmas: Object.fromEntries(
    [...coveredWhy.entries()].sort(([a], [b]) => (a < b ? -1 : 1))
      .map(([l, why]) => [l, [...why].sort()]),
  ),
  machinery: {
    'data/kernel-v0/manifest.json': fileSha(KERNEL_MANIFEST),
    'mapper/dist/src/index.js': fileSha(join(REPO, 'mapper/dist/src/index.js')),
    'mapper/dist/src/lemmatize.js': fileSha(join(REPO, 'mapper/dist/src/lemmatize.js')),
    'mapper/dist/src/lexicon.js': fileSha(join(REPO, 'mapper/dist/src/lexicon.js')),
    'mapper/dist/src/primes.js': fileSha(join(REPO, 'mapper/dist/src/primes.js')),
    'mapper/m0/run-m0b-vocab.mjs (FUNCTION_STOPLIST source)': fileSha(M0B_SCRIPT),
  },
  note: 'covered = mapper-lexicon single-word surfaces (65-prime exponents + kernel-v0 '
    + 'concept labels, parenthetical-stripped) UNION molecules-v0 labels UNION '
    + 'molecules-v0 corpusLemmas; the EXACT machinery of mapper/m0/run-m0b-vocab.mjs',
});

writeCanon('leak-check.json', {
  artifact: 'd-ext-leak-check',
  checks: lc,
  generated: GENERATED,
  note: 'fail-closed: LC-DQA collision or machinery drift aborts the build; LC1-ext/LC4-ext/'
    + 'LC5-ext violations DROP the item (external text is never edited) and are counted here',
  result: 'PASS',
});

writeCanon('manifest.json', {
  authorship: 'items are EXTERNALLY AUTHORED (OpenBookQA, Mihaylov et al. 2018, Apache-2.0) '
    + 'and reproduced verbatim (question_stem, choices, answerKey, fact1); the coverage '
    + 'filter, leak checks, and selection are deterministic code in this directory; NO LLM '
    + 'authored, selected, or edited any item text; built by a Fable execution agent (Kern '
    + 'programme) 2026-07-08',
  builder: {
    'build-dext.mjs': fileSha(join(HERE, 'build-dext.mjs')),
    'convert-source.py': fileSha(join(HERE, 'convert-source.py')),
  },
  corpus: 'd-ext',
  counts: {
    by_split: perSplitRC,
    items: items.length,
    selected_by_split: items.reduce((m, it) => {
      m[it.source_split] = (m[it.source_split] ?? 0) + 1;
      return m;
    }, {}),
  },
  filter: {
    declared_before_yield_measured: true,
    rule: 'R-C: item kernel-covered iff fact1 has >=1 covered content lemma AND '
      + '(question_stem + correct-answer text) has >=1 covered content lemma; covered '
      + 'content lemma = token whose lemma candidates (lemmaCandidates/irregularBase, '
      + 'M0b machinery) hit the covered lemma set (covered-lemmas.json) and are not on '
      + 'the M0b FUNCTION_STOPLIST; pre-declared fallback R-A (fact1 alone) fires only '
      + 'if R-C leak-checked yield < 300 — NOT fired',
    rule_fired: 'R-C',
    yields: {
      source_rows: total,
      'R-A_fact1_covered_post_LC4': coveredRA,
      'R-C_covered_post_LC4': coveredRC,
      leak_checked_survivors: yieldRC,
    },
  },
  files: {
    'covered-lemmas.json': 'the M0b-machinery covered lemma set + provenance per lemma',
    'items/external.jsonl': `${items.length} externally-authored items, pinned order (rank field)`,
    'leak-check.json': 'leak-check evidence (fail-closed checks + drop counts)',
    'source-jsonl/{train,validation,test}.jsonl': 'canonical conversion of the pinned parquet '
      + '(convert-source.py; pure format conversion, no selection)',
    'source/additional/*.parquet': 'pinned source bytes (HF LFS objects at the pinned revision)',
  },
  generated: GENERATED,
  preference_walk: [
    {
      evidence: 'probed 2026-07-08 unauthenticated (no HF credentials on the build box): '
        + 'HTTP 401 from https://huggingface.co/api/datasets/pilehvar/wic, from '
        + 'https://datasets-server.huggingface.co/is-valid?dataset=pilehvar/wic ("The '
        + 'dataset does not exist, or is not accessible without authentication"), and '
        + 'from the dataset web page. WiC copies exist under other HF namespaces, but '
        + 'none is the pre-declared id; substituting an unauthenticated mirror would '
        + 'break source provenance — declined (fail-closed sourcing)',
      hf_repo: 'pilehvar/wic',
      license: 'CC BY-NC 4.0 (moot — source not used)',
      rank: 1,
      source: 'WiC',
      status: 'UNAVAILABLE',
    },
    {
      hf_repo: SOURCE.hf_repo,
      hf_revision: SOURCE.hf_revision,
      hf_revision_note: 'refs/heads/main on 2026-07-08, cross-checked via '
        + '/api/datasets/allenai/openbookqa/refs; config `additional` (= `main` columns '
        + '+ fact1 core fact + crowd metadata); per-file sha256 pins in convert-source.py '
        + '= the HF LFS oids at this revision',
      license: SOURCE.license,
      rank: 2,
      selection_rule: 'first source whose M0b-filtered, leak-checked yield is >= 300 items '
        + '(frozen GNG-0 ratification default); yield 2904 >= 300',
      source: 'OpenBookQA',
      status: 'SELECTED',
    },
    { hf_repo: 'cais/mmlu', rank: 3, source: 'MMLU', status: 'NOT REACHED' },
  ],
  role: 'F2/E9 RT-7a ecological-validity secondary (registry pin external-eval-slice; '
    + 'item_correct_external DV); run under the shared P10 output affordances (A-D '
    + 'constrained choice); kernel_checkable=false — no kernel record backs these items',
  schema: 'kot-dext/1',
  selection: {
    cap: CAP,
    cap_rationale: 'mirror of frozen design.n_planned.per_arm_items; caps external-slice '
      + 'inference cost inside the frozen budget',
    order: 'validation -> test -> train (source row order within each split; eval splits '
      + 'first — less likely to appear in instruction-tuning mixtures; contamination of '
      + 'public benchmarks in pretraining corpora is an accepted, pre-registered '
      + 'limitation of RT-7a ecological validity)',
  },
  sources: {
    'kernel-v0': { kot_corpus_hash: '8209cadabcfc2eaa11631c5c1100c04a48f33673516780b1f36cbf957217c809' },
    'molecules-v0': { kot_corpus_hash: '69f0c8a354ce489d15e9156d611932ba548f80c41e78af4ffe597192067a59c4' },
    openbookqa: {
      config: SOURCE.config,
      hf_repo: SOURCE.hf_repo,
      hf_revision: SOURCE.hf_revision,
      license: SOURCE.license,
      main_config_lfs_oids_for_cross_reference: {
        'main/test-00000-of-00001.parquet': 'cd5483e366daa230c1c87bbdc512d8b7229f14f6dd04d19fc8b1a3855aaaa8a3',
        'main/train-00000-of-00001.parquet': '98148f8a54e62eb862346a75192d5fb824d6cbb68f2f59aecd793d39ecb5cd8b',
        'main/validation-00000-of-00001.parquet': '35370b9cfee8c1ff325ccc74adc434d12c47ca0ac3244aa87f3fa77069285206',
      },
    },
  },
  version: '0.1.0',
});

console.log(`d-ext built: ${items.length} items (R-C yield ${yieldRC}; source rows ${total}); `
  + `balance A/B/C/D = ${balance.A}/${balance.B}/${balance.C}/${balance.D}`);
