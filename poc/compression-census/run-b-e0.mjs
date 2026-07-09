#!/usr/bin/env node
/**
 * B-E0 — roll-up engagement census (Tier 0, ~$0, r0-local-cpu; bead
 * kernel-of-truth-5iu; docs/next/io-compression-ideas.md §3.7).
 *
 * Deterministic, no model calls. Measures, over a pinned corpus, what the
 * fail-closed roll-up instrument (parser.mjs) actually ENGAGES:
 *   - fraction of corpus word-token mass inside maximal parseable fragments
 *     (the idea's live-or-die number, §3.6), by stratum
 *     {is-a, clause-AND, operator-complex, simple-clause};
 *   - the per-span savings distribution (t_span expanded word tokens -> one
 *     concept token; savings counted only for t_span >= 2);
 *   - the OR-forfeit count + token mass (clause-level / NP-level) — the
 *     measured case for/against an OR grammar extension (§3.1);
 *   - composite dedupe statistics (unique URNs vs occurrences — sizes the
 *     global dictionary, §3.2);
 *   - the abstain-cause histogram (diagnostic; where the mass is lost);
 *   - an encodability spot-check: the first N unique composites are encoded
 *     (construction B, D=8192) and timed.
 *
 * CELLS: {mapper policy: default(v0.1.0) | a1-hybrid} × {parser profile:
 * strict | permissive-det}. Cells are reported SEPARATELY — permissive-det
 * carries a flagged lossy determiner convention and must never be merged
 * with strict (parser.mjs header).
 *
 * SCOPE (restate with every number): TinyStories-valid (the deliberately
 * favourable ~1.5k-lemma domain; m0b envelope — extrapolates to NO other
 * corpus), kernel instance = kernel-v0 + molecules-v0 labels+synonyms
 * (m0b-continuity instrument), THIS conservative v0 parser. The design doc's
 * second census corpus (an instruction/QA corpus, [STIPULATED at freeze])
 * is NOT run here: none is available locally.
 *
 * NOT measurable here: host-BPE-token savings (the §1.5 accounting needs the
 * pinned host tokenizers — R1 SmolLM2 + one R4-family — which are not on
 * this box; word-token and character spans are reported instead).
 *
 * Usage: node poc/compression-census/run-b-e0.mjs <TinyStories-valid.txt> [--limit=N]
 */
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  buildLexicon,
  loadManifestConcepts,
  mapText,
  policyPreset,
} from '../../mapper/dist/src/index.js';
import {
  encodeExplication,
  mintCompositeUrn,
  renderExplication,
  SeededRng,
} from '../../encoder/dist/src/index.js';
import { scanSentence } from './parser.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..');
const OUT = join(HERE, 'results');

// Pinned corpus identity (mapper/m0/results/m0a-shadowed-policy.md: corpus
// sha 94e43181…; fail closed on drift).
const CORPUS_SHA256 = '94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4';

const args = process.argv.slice(2);
const corpusPath = args.find((a) => !a.startsWith('--'));
const limitArg = args.find((a) => a.startsWith('--limit='));
const limit = limitArg ? Number(limitArg.slice('--limit='.length)) : Infinity;
if (!corpusPath) {
  console.error('usage: run-b-e0.mjs <TinyStories-valid.txt> [--limit=N]');
  process.exit(1);
}

const raw = readFileSync(corpusPath, 'utf8');
const sha = createHash('sha256').update(raw).digest('hex');
if (sha !== CORPUS_SHA256) {
  console.error(`ERR_CORPUS_SHA: expected ${CORPUS_SHA256}, got ${sha}`);
  process.exit(1);
}

// Lexicon: kernel-v0 + molecules-v0 labels+synonyms (m0b molecules-v0 rung).
const kernel = loadManifestConcepts(join(REPO, 'data', 'kernel-v0', 'manifest.json'));
const molManifest = JSON.parse(readFileSync(join(REPO, 'data', 'molecules-v0', 'manifest.json'), 'utf8'));
const molLabels = molManifest.molecules.map((m) => ({ id: m.id, label: m.label }));
const molSynonyms = molManifest.molecules.flatMap((m) =>
  (m.corpusLemmas ?? []).filter((l) => l !== m.label).map((l) => ({ id: m.id, label: l })),
);
const lexicon = buildLexicon([...kernel, ...molLabels, ...molSynonyms]);

const stories = raw
  .split('<|endoftext|>')
  .map((s) => s.trim())
  .filter((s) => s.length > 0)
  .slice(0, Number.isFinite(limit) ? limit : undefined);

const POLICIES = [
  { name: 'default-v0.1.0', policy: undefined },
  { name: 'a1-hybrid', policy: policyPreset('a1-hybrid') },
];
const PROFILES = ['strict', 'permissive-det'];

/** Split a mapper-annotated token array into sentences at .!?; punctuation. */
function splitSentences(toks) {
  const out = [];
  let cur = [];
  for (const t of toks) {
    cur.push(t);
    if (!t.isWord && /[.!?;]/.test(t.surface)) {
      out.push(cur);
      cur = [];
    }
  }
  if (cur.length > 0) out.push(cur);
  return out;
}

function newCell() {
  return {
    sentences: 0,
    expandedWords: 0,
    surfaceWords: 0,
    fragments: 0,
    fragmentsGe2: 0,
    engagedExpandedWords: 0, // Σ t_span over fragments with t_span >= 2
    engagedSurfaceWords: 0,
    engagedChars: 0,
    size1Fragments: 0,
    savingsWords: 0, // Σ (t_span - 1) over fragments with t_span >= 2
    spanHist: new Map(), // t_span -> count (t_span >= 2)
    fullSentenceFragments: 0,
    strata: new Map(), // stratum -> {count, words, savings}
    orForfeits: { clause: { count: 0, words: 0 }, np: { count: 0, words: 0 } },
    causes: new Map(),
    dict: new Map(), // urn -> {count, words, stratum, ast?}
    uniqueAstSample: [],
    parserInvalid: new Map(), // gate error code -> count (instrument bugs; target 0)
  };
}

const cells = new Map();
for (const p of POLICIES) for (const pr of PROFILES) cells.set(`${p.name}/${pr}`, newCell());

const t0 = Date.now();
let storyCount = 0;
for (const story of stories) {
  storyCount++;
  for (const pol of POLICIES) {
    const annotated = mapText(story, lexicon, pol.policy);
    const sentences = splitSentences(annotated);
    for (const profile of PROFILES) {
      const cell = cells.get(`${pol.name}/${profile}`);
      for (const sent of sentences) {
        let expanded = 0;
        let surface = 0;
        for (const t of sent) {
          if (t.isWord) {
            expanded++;
            if (!t.isExpansion) surface++;
          }
        }
        if (expanded === 0) continue;
        cell.sentences++;
        cell.expandedWords += expanded;
        cell.surfaceWords += surface;

        const res = scanSentence(sent, profile);
        for (const f of res.fragments) {
          // Gate check FIRST: an emitted fragment the validator rejects is an
          // INSTRUMENT BUG — counted loudly, excluded from every statistic,
          // and the run is marked non-clean (target: zero).
          let urn;
          try {
            urn = mintCompositeUrn(f.explication);
          } catch (e) {
            const code = e?.code ?? 'ERR_UNKNOWN';
            cell.parserInvalid.set(code, (cell.parserInvalid.get(code) ?? 0) + 1);
            continue;
          }
          cell.fragments++;
          if (f.expandedWords < 2) {
            cell.size1Fragments++;
            continue;
          }
          cell.fragmentsGe2++;
          cell.engagedExpandedWords += f.expandedWords;
          cell.engagedSurfaceWords += f.surfaceWords;
          cell.engagedChars += f.chars;
          cell.savingsWords += f.expandedWords - 1;
          cell.spanHist.set(f.expandedWords, (cell.spanHist.get(f.expandedWords) ?? 0) + 1);
          if (f.expandedWords === expanded) cell.fullSentenceFragments++;
          const s = cell.strata.get(f.stratum) ?? { count: 0, words: 0, savings: 0 };
          s.count++;
          s.words += f.expandedWords;
          s.savings += f.expandedWords - 1;
          cell.strata.set(f.stratum, s);
          // dedupe / dictionary stats
          const d = cell.dict.get(urn);
          if (d === undefined) {
            cell.dict.set(urn, {
              count: 1,
              words: f.expandedWords,
              stratum: f.stratum,
              // canonical-form v0 rendering kept for the first uniques so the
              // top-composites table is human-inspectable
              render: cell.dict.size < 500 ? renderExplication(f.explication) : undefined,
            });
            if (cell.uniqueAstSample.length < 50) cell.uniqueAstSample.push(f.explication);
          } else {
            d.count++;
          }
        }
        for (const ff of res.orForfeits) {
          const slot = cell.orForfeits[ff.level];
          slot.count++;
          slot.words += ff.words;
        }
        for (const [c, k] of res.causes) cell.causes.set(c, (cell.causes.get(c) ?? 0) + k);
      }
    }
  }
  if (storyCount % 2000 === 0) {
    console.error(`  ... ${storyCount}/${stories.length} stories (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
}

// Encodability spot-check per cell (unique-AST sample, construction B
// D=8192). Concept references are bound to DETERMINISTIC STUB vectors
// (SeededRng rademacher per URN): this checks STRUCTURAL encodability
// (shapes, caps, binding paths) — the algebra binds any D-vector uniformly,
// so real kernel vectors substitute without changing the code path.
function collectConceptIds(node, out) {
  if (Array.isArray(node)) {
    for (const x of node) collectConceptIds(x, out);
  } else if (node !== null && typeof node === 'object') {
    if ((node.kind === 'concept' || node.kind === 'conceptHead') && typeof node.id === 'string') out.add(node.id);
    for (const v of Object.values(node)) collectConceptIds(v, out);
  }
}
function stubVector(id) {
  const rng = new SeededRng(`b-e0-census-stub/${id}`);
  const v = new Float64Array(8192);
  for (let i = 0; i < v.length; i++) v[i] = rng.bool(0.5) ? 1 : -1;
  return v;
}
for (const [name, cell] of cells) {
  const ids = new Set();
  for (const ast of cell.uniqueAstSample) collectConceptIds(ast, ids);
  const concepts = new Map([...ids].map((id) => [id, stubVector(id)]));
  const t1 = Date.now();
  let enc = 0;
  for (const ast of cell.uniqueAstSample) {
    const v = encodeExplication(ast, { concepts });
    if (v.length !== 8192) throw new Error('ERR_ENCODE_DIM');
    enc++;
  }
  cell.encodeSample = { n: enc, ms: Date.now() - t1, concept_vectors: 'deterministic stubs (structural check)' };
  void name;
}

function cellReport(cell) {
  const topComposites = [...cell.dict.entries()]
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 20)
    .map(([urn, d]) => ({ urn, count: d.count, words: d.words, stratum: d.stratum, render: d.render }));
  const spanHist = [...cell.spanHist.entries()].sort((a, b) => a[0] - b[0]);
  const totalOccurrences = [...cell.dict.values()].reduce((a, d) => a + d.count, 0);
  const spans = [];
  for (const [span, count] of spanHist) for (let i = 0; i < count; i++) spans.push(span);
  const pct = (q) => (spans.length === 0 ? null : spans[Math.min(spans.length - 1, Math.floor(q * spans.length))]);
  return {
    sentences: cell.sentences,
    expandedWords: cell.expandedWords,
    surfaceWords: cell.surfaceWords,
    fragments_total: cell.fragments,
    fragments_span_ge2: cell.fragmentsGe2,
    fragments_span1_flat: cell.size1Fragments,
    engagement_fraction_expandedWords: cell.expandedWords > 0 ? cell.engagedExpandedWords / cell.expandedWords : 0,
    engagement_fraction_surfaceWords: cell.surfaceWords > 0 ? cell.engagedSurfaceWords / cell.surfaceWords : 0,
    engaged_expandedWords: cell.engagedExpandedWords,
    savings_words_total: cell.savingsWords,
    savings_fraction_expandedWords: cell.expandedWords > 0 ? cell.savingsWords / cell.expandedWords : 0,
    span_distribution: { histogram: spanHist, mean: spans.length ? spans.reduce((a, b) => a + b, 0) / spans.length : null, p50: pct(0.5), p90: pct(0.9), max: spans.length ? spans[spans.length - 1] : null },
    full_sentence_fragments: cell.fullSentenceFragments,
    strata: Object.fromEntries([...cell.strata.entries()].map(([k, v]) => [k, { ...v, savings_fraction_expandedWords: cell.expandedWords > 0 ? v.savings / cell.expandedWords : 0 }])),
    or_forfeit: {
      clause: { ...cell.orForfeits.clause, words_fraction: cell.expandedWords > 0 ? cell.orForfeits.clause.words / cell.expandedWords : 0 },
      np: { ...cell.orForfeits.np, words_fraction: cell.expandedWords > 0 ? cell.orForfeits.np.words / cell.expandedWords : 0 },
    },
    dedupe: {
      unique_urns: cell.dict.size,
      occurrences_span_ge2_plus_span1_unique_basis: totalOccurrences,
      dedupe_ratio: cell.dict.size > 0 ? totalOccurrences / cell.dict.size : null,
      top_composites: topComposites,
    },
    abstain_causes: Object.fromEntries([...cell.causes.entries()].sort((a, b) => b[1] - a[1])),
    parser_invalid_fragments: Object.fromEntries(cell.parserInvalid.entries()),
    encode_sample: cell.encodeSample,
  };
}
const instrumentBugTotal = [...cells.values()].reduce(
  (a, c) => a + [...c.parserInvalid.values()].reduce((x, y) => x + y, 0),
  0,
);

const report = {
  census: 'B-E0 roll-up engagement census (Tier 0)',
  bead: 'kernel-of-truth-5iu',
  design: 'docs/next/io-compression-ideas.md §3.7 B-E0; instrument conventions in poc/compression-census/parser.mjs header',
  date: new Date().toISOString(),
  corpus: {
    file: corpusPath,
    sha256: sha,
    source: 'roneneldan/TinyStories TinyStories-valid.txt (m0a/m0b pinned corpus)',
    stories: storyCount,
    limited: Number.isFinite(limit) ? limit : null,
  },
  kernel_instance: {
    lexicon: 'kernel-v0 concepts + molecules-v0 labels+corpusLemmas synonyms (m0b molecules-v0-rung continuity)',
    kernel_v0_concepts: kernel.length,
    molecules_v0: molLabels.length,
    lexicon_entries: lexicon.entries.length,
  },
  scope_honesty: [
    'MEASURED on TinyStories-valid ONLY (deliberately favourable ~1.5k-lemma domain; m0b envelope: extrapolates to NO other corpus or kernel state).',
    'Engagement is engagement OF THIS conservative fail-closed v0 instrument (parser.mjs conventions), not a grammar ceiling.',
    'permissive-det cells carry a flagged LOSSY determiner convention (the/that/those -> THIS) and are reported separately, never merged.',
    'Host-BPE token savings NOT measurable locally (no pinned host tokenizer on box); spans are word-token and character denominated.',
    'Second census corpus (instruction/QA, stipulated at freeze) not run: none available locally.',
  ],
  savings_definition: 'one composite concept token replaces a fragment of t_span expanded word tokens; savings = t_span - 1, counted only for t_span >= 2; engagement fraction = engaged expanded word mass / total expanded word mass (m0a token-mass conventions)',
  cells: Object.fromEntries([...cells.entries()].map(([k, c]) => [k, cellReport(c)])),
  instrument_bug_fragments_total: instrumentBugTotal,
  clean_run: instrumentBugTotal === 0,
  runtime_seconds: (Date.now() - t0) / 1000,
};
if (instrumentBugTotal > 0) {
  console.error(`WARNING: ${instrumentBugTotal} gate-rejected fragments (instrument bugs) — census NOT clean; fix parser and re-run`);
}

mkdirSync(OUT, { recursive: true });
const jsonPath = join(OUT, 'b-e0-tinystories.json');
writeFileSync(jsonPath, JSON.stringify(report, null, 2));

// small md companion (auto-generated projection of the JSON)
const md = [];
md.push('# B-E0 roll-up engagement census — TinyStories-valid (Tier 0, $0)');
md.push('');
md.push(`Auto-generated by run-b-e0.mjs on ${report.date}. Data: b-e0-tinystories.json.`);
md.push(`Corpus sha256 \`${sha.slice(0, 8)}…\` (m0a pin), ${storyCount} stories. Instrument + conventions: parser.mjs.`);
md.push(`Clean run: ${report.clean_run} (${report.instrument_bug_fragments_total} gate-rejected fragments).`);
md.push('');
md.push('Scope honesty: ' + report.scope_honesty.join(' '));
md.push('');
md.push('| cell (policy/profile) | sentences | word tokens | engagement (expanded-word mass) | savings fraction | OR-forfeit (clause n / mass) | OR-forfeit (np n / mass) | unique URNs | dedupe ratio |');
md.push('|---|---|---|---|---|---|---|---|---|');
for (const [k, c] of Object.entries(report.cells)) {
  md.push(
    `| ${k} | ${c.sentences} | ${c.expandedWords} | ${(c.engagement_fraction_expandedWords * 100).toFixed(3)}% | ${(c.savings_fraction_expandedWords * 100).toFixed(3)}% | ${c.or_forfeit.clause.count} / ${(c.or_forfeit.clause.words_fraction * 100).toFixed(4)}% | ${c.or_forfeit.np.count} / ${(c.or_forfeit.np.words_fraction * 100).toFixed(4)}% | ${c.dedupe.unique_urns} | ${c.dedupe.dedupe_ratio === null ? 'n/a' : c.dedupe.dedupe_ratio.toFixed(2)} |`,
  );
}
md.push('');
md.push('Strata (per cell, savings fraction of corpus word mass):');
for (const [k, c] of Object.entries(report.cells)) {
  md.push(`- **${k}**: ` + Object.entries(c.strata).map(([s, v]) => `${s} n=${v.count} savings=${(v.savings_fraction_expandedWords * 100).toFixed(4)}%`).join('; '));
}
md.push('');
md.push('Top abstain causes (a1-hybrid/strict): ' + Object.entries(report.cells['a1-hybrid/strict'].abstain_causes).slice(0, 10).map(([c, n]) => `${c}=${n}`).join(', '));
writeFileSync(join(OUT, 'b-e0-tinystories.md'), md.join('\n') + '\n');

console.log(JSON.stringify({
  stories: storyCount,
  runtime_s: report.runtime_seconds,
  headline: Object.fromEntries(Object.entries(report.cells).map(([k, c]) => [k, {
    engagement: c.engagement_fraction_expandedWords,
    savings: c.savings_fraction_expandedWords,
    or_clause: c.or_forfeit.clause.count,
    or_np: c.or_forfeit.np.count,
    unique: c.dedupe.unique_urns,
  }])),
}, null, 2));
console.log(`written: ${jsonPath}`);
