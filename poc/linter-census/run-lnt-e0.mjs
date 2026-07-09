#!/usr/bin/env node
/**
 * LNT-E0 — proposition-level conjunctive-coverage census + false-alarm floor
 * (docs/next/kernel-precision-linter.md §5, Tier 0, ~$0, r0-local-cpu).
 *
 * EPISTEMIC STATUS: EXPLORATORY feasibility instrument run — NOT
 * pre-registered, NOT a frozen kot-reg/1 experiment, and it can never flip
 * any verdict. Its numbers are tooling-level MEASUREMENTS (exact command +
 * committed output; deterministic census, no sampling, no RNG) whose scope
 * is EXACTLY the pinned corpus slices below. Nothing here extrapolates to
 * any other corpus (the m0b envelope discipline applies verbatim).
 *
 * Three pinned slices:
 *   llm-tinystories     the m0b-pinned corpus (TinyStories-valid): LLM-
 *                       generated text AND the corpus whose token-mass
 *                       coverage is the MEASURED 0.3542 @ molecules-v0
 *                       (registry/verdicts/m0b.json). The census (i) number —
 *                       proposition-level conjunctive coverage — lands here,
 *                       directly comparable to the token-mass number.
 *   llm-programme-docs  pinned programme-generated design docs (dogfood,
 *                       N-PL §6 Stage 0): LLM/agent-authored technical prose.
 *   clean-human         locally installed man pages (bash/grep/tar):
 *                       human-authored precise technical documentation —
 *                       the false-alarm-floor slice (ii). STIPULATED corpus
 *                       choice for this feasibility run; OFF the covered
 *                       domain (fine for the coverage-independent V/A floor;
 *                       U is info-only and never an alarm in mode P).
 *
 * (iii) V-rhetorical/V-tautology split: only the V-rhetorical half is
 * measurable at Stage 0 (V-tautology needs the explication normaliser).
 * Reported as such — a half-measurement, stated as a half-measurement.
 *
 * Instrument gates (reported, fail-visible):
 *   G1 rung monotonicity   kStrict <= kMember <= mol <= wn31 on every slice
 *   G2 m0a cross-check     flagless decision fractions on llm-tinystories
 *                          must reproduce the published M0a headline
 *                          (mapper/m0/results/m0a-report.json) to 4dp
 *
 * Usage:
 *   node poc/linter-census/run-lnt-e0.mjs [--tinystories=<path>] [--stories-limit=<n>] [--skip-tinystories]
 *
 * Output: results/lnt-e0-report.json (stable JSON) + results/lnt-e0-report.md
 */
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildLintContext, lintDocument, stableStringify } from '../../tools/lint/lib/lint.mjs';
import { mapText } from '../../mapper/dist/src/index.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..');

// ---- args -------------------------------------------------------------------
let tinystoriesPath = '/tmp/TinyStories-valid.txt';
let storiesLimit = Infinity;
let skipTinystories = false;
for (const arg of process.argv.slice(2)) {
  if (arg.startsWith('--tinystories=')) tinystoriesPath = arg.slice('--tinystories='.length);
  else if (arg.startsWith('--stories-limit=')) storiesLimit = Number(arg.slice('--stories-limit='.length));
  else if (arg === '--skip-tinystories') skipTinystories = true;
  else {
    console.error(`ERR_LNT_E0_USAGE: unknown arg ${arg}`);
    process.exit(2);
  }
}

// ---- pinned doc slices --------------------------------------------------------
const PROGRAMME_DOCS = [
  'README.md',
  'docs/architecture.md',
  'docs/kernel-design-directives.md',
  'docs/explainer-vectorisation.md',
  'docs/next/kernel-precision-linter.md',
  'reports/nsm-and-knowledge-injection.md',
];
const CLEAN_HUMAN_DIR = join(HERE, 'corpora', 'clean-human');
const CLEAN_HUMAN_FILES = ['bash.txt', 'grep.txt', 'tar.txt'];

// ---- aggregation ----------------------------------------------------------------
function newAgg() {
  return {
    documents: 0,
    chars: 0,
    sentences: 0,
    clauses: 0,
    propositions: 0,
    noContentClauses: 0,
    expandedWordTokens: 0,
    contentTokens: 0,
    decisions: { concept: 0, prime: 0, abstain: 0, none: 0 },
    contentBands: { 'kernel-v0': 0, 'kernel-v0-member': 0, 'molecules-v0': 0, 'wn31-aligned': 0, out: 0 },
    cov: {
      clause: { kStrict: 0, kMember: 0, mol: 0, wn31: 0, total: 0 },
      sentence: { kStrict: 0, kMember: 0, mol: 0, wn31: 0, total: 0 },
    },
    engagement: { M: 0, A: 0, 'U-mol': 0, 'U-wn31': 0, 'U-out': 0 },
    vFlaggedPropositions: 0,
    whollyVacuousClauses: 0,
    flagCounts: { V: { filler: 0, weasel: 0, hedge: 0, total: 0 }, A: 0 },
    sentencesWithWarn: 0,
    byPattern: new Map(),
    aSurfaces: new Map(),
    exampleFlags: [],
  };
}

function addDoc(agg, docId, { report, flags }) {
  agg.documents += 1;
  agg.chars += report.chars;
  agg.sentences += report.sentences;
  agg.clauses += report.clauses;
  agg.propositions += report.propositions;
  agg.noContentClauses += report.noContentClauses;
  agg.expandedWordTokens += report.tokens.expandedWordTokens;
  agg.contentTokens += report.tokens.contentTokens;
  for (const k of Object.keys(agg.decisions)) agg.decisions[k] += report.tokens.decisions[k];
  for (const k of Object.keys(agg.contentBands)) agg.contentBands[k] += report.tokens.contentBands[k];
  const pc = report.propositionCoverage;
  for (const [unit, keys] of [['clause', pc.clause], ['sentence', pc.sentence]]) {
    agg.cov[unit].total += keys.total;
    agg.cov[unit].kStrict += keys.kernelV0Strict.covered;
    agg.cov[unit].kMember += keys.kernelV0Member.covered;
    agg.cov[unit].mol += keys.moleculesV0.covered;
    agg.cov[unit].wn31 += keys.wn31Aligned.covered;
  }
  for (const k of Object.keys(agg.engagement)) agg.engagement[k] += report.engagement.classes[k];
  agg.vFlaggedPropositions += report.engagement.vFlaggedPropositions;
  agg.whollyVacuousClauses += report.engagement.whollyVacuousClauses;
  for (const c of ['filler', 'weasel', 'hedge', 'total']) agg.flagCounts.V[c] += report.flagCounts.V[c];
  agg.flagCounts.A += report.flagCounts.A;
  agg.sentencesWithWarn += report.rates.sentencesWithWarn;
  for (const f of flags) {
    if (f.class === 'V') agg.byPattern.set(f.patternId, (agg.byPattern.get(f.patternId) ?? 0) + 1);
    if (f.class === 'A') {
      const key = f.text.toLowerCase();
      agg.aSurfaces.set(key, (agg.aSurfaces.get(key) ?? 0) + 1);
    }
    if (agg.exampleFlags.length < 12) agg.exampleFlags.push({ doc: docId, class: f.class, ...(f.patternId ? { patternId: f.patternId } : {}), text: f.text, start: f.start });
  }
}

function finalize(agg) {
  const frac = (n, d) => (d > 0 ? Math.round((n / d) * 1e6) / 1e6 : null);
  const covOut = {};
  for (const unit of ['clause', 'sentence']) {
    const c = agg.cov[unit];
    covOut[unit] = {
      total: c.total,
      kernelV0Strict: { covered: c.kStrict, fraction: frac(c.kStrict, c.total) },
      kernelV0Member: { covered: c.kMember, fraction: frac(c.kMember, c.total) },
      moleculesV0: { covered: c.mol, fraction: frac(c.mol, c.total) },
      wn31Aligned: { covered: c.wn31, fraction: frac(c.wn31, c.total) },
    };
  }
  const monotone =
    agg.cov.clause.kStrict <= agg.cov.clause.kMember &&
    agg.cov.clause.kMember <= agg.cov.clause.mol &&
    agg.cov.clause.mol <= agg.cov.clause.wn31 &&
    agg.cov.sentence.kStrict <= agg.cov.sentence.kMember &&
    agg.cov.sentence.kMember <= agg.cov.sentence.mol &&
    agg.cov.sentence.mol <= agg.cov.sentence.wn31;
  return {
    documents: agg.documents,
    chars: agg.chars,
    sentences: agg.sentences,
    clauses: agg.clauses,
    propositions: agg.propositions,
    noContentClauses: agg.noContentClauses,
    tokens: {
      expandedWordTokens: agg.expandedWordTokens,
      contentTokens: agg.contentTokens,
      decisions: agg.decisions,
      decisionFractionsOfWordTokens: Object.fromEntries(
        Object.entries(agg.decisions).map(([k, v]) => [k, frac(v, agg.expandedWordTokens)]),
      ),
      contentBands: agg.contentBands,
      contentBandFractions: Object.fromEntries(
        Object.entries(agg.contentBands).map(([k, v]) => [k, frac(v, agg.contentTokens)]),
      ),
    },
    propositionCoverage: covOut,
    gateG1RungMonotonicity: monotone,
    engagement: {
      classes: agg.engagement,
      fractions: Object.fromEntries(Object.entries(agg.engagement).map(([k, v]) => [k, frac(v, agg.propositions)])),
      vFlaggedPropositions: agg.vFlaggedPropositions,
      vFlaggedPropositionFraction: frac(agg.vFlaggedPropositions, agg.propositions),
      whollyVacuousClauses: agg.whollyVacuousClauses,
    },
    falseAlarm: {
      flagCounts: agg.flagCounts,
      vPer1000Words: frac(agg.flagCounts.V.total * 1000, agg.expandedWordTokens),
      aPer1000Words: frac(agg.flagCounts.A * 1000, agg.expandedWordTokens),
      warnPer1000Words: frac((agg.flagCounts.V.total + agg.flagCounts.A) * 1000, agg.expandedWordTokens),
      sentencesWithWarn: agg.sentencesWithWarn,
      sentencesWithWarnFraction: frac(agg.sentencesWithWarn, agg.sentences),
    },
    vByPattern: Object.fromEntries([...agg.byPattern.entries()].sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1))),
    aTopSurfaces: Object.fromEntries(
      [...agg.aSurfaces.entries()].sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1)).slice(0, 25),
    ),
    exampleFlags: agg.exampleFlags,
  };
}

const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');

// ---- run ------------------------------------------------------------------------
console.error('loading lint context (kernel-v0 lexicon + molecules band + wn31 band)…');
const ctx = buildLintContext({ policyName: 'a1-hybrid', wn31: true });
const t0 = Date.now();
const slices = {};
const corpusPins = {};

// slice: llm-programme-docs (dogfood; markdown-stripped)
{
  const agg = newAgg();
  const perDoc = {};
  for (const rel of PROGRAMME_DOCS) {
    const raw = readFileSync(join(REPO, rel), 'utf8');
    const res = lintDocument(raw, ctx, { strip: 'markdown' });
    addDoc(agg, rel, res);
    perDoc[rel] = {
      sha256: sha256(raw),
      propositions: res.report.propositions,
      engagementFractions: res.report.engagement.fractions,
      flagCounts: res.report.flagCounts,
      warnPer1000Words: res.report.rates.warnPer1000Words,
    };
  }
  slices['llm-programme-docs'] = { ...finalize(agg), perDocument: perDoc };
  corpusPins['llm-programme-docs'] = {
    kind: 'programme-generated design docs (LLM/agent-authored), markdown-stripped',
    files: PROGRAMME_DOCS,
  };
  console.error(`llm-programme-docs done (${agg.documents} docs, ${agg.propositions} propositions)`);
}

// slice: clean-human (false-alarm floor)
{
  const agg = newAgg();
  const perDoc = {};
  for (const name of CLEAN_HUMAN_FILES) {
    const path = join(CLEAN_HUMAN_DIR, name);
    const raw = readFileSync(path, 'utf8');
    const res = lintDocument(raw, ctx, { strip: 'none' });
    addDoc(agg, name, res);
    perDoc[name] = {
      sha256: sha256(raw),
      propositions: res.report.propositions,
      flagCounts: res.report.flagCounts,
      warnPer1000Words: res.report.rates.warnPer1000Words,
      sentencesWithWarnFraction: res.report.rates.sentencesWithWarnFraction,
    };
  }
  slices['clean-human'] = { ...finalize(agg), perDocument: perDoc };
  corpusPins['clean-human'] = {
    kind: 'human-authored technical documentation (rendered man pages; prep-clean-human.sh)',
    files: CLEAN_HUMAN_FILES,
    note: 'STIPULATED corpus choice for this Tier-0 feasibility run; OFF the covered domain — valid for the coverage-independent V/A false-alarm floor only',
  };
  console.error(`clean-human done (${agg.documents} docs, ${agg.propositions} propositions)`);
}

// slice: llm-tinystories (the m0b-pinned corpus) + G2 flagless cross-check
let g2 = { skipped: true };
if (!skipTinystories) {
  const raw = readFileSync(tinystoriesPath, 'utf8');
  const stories = raw.split('<|endoftext|>').map((s) => s.trim()).filter((s) => s.length > 0);
  const limit = Math.min(stories.length, storiesLimit);
  const agg = newAgg();
  for (let i = 0; i < limit; i += 1) addDoc(agg, `story-${i}`, lintDocument(stories[i], ctx));
  slices['llm-tinystories'] = finalize(agg);
  corpusPins['llm-tinystories'] = {
    kind: 'LLM-generated stories (GPT-3.5/4-generated TinyStories; the m0b/m0a-pinned corpus)',
    path: tinystoriesPath,
    sha256: sha256(readFileSync(tinystoriesPath)),
    bytes: readFileSync(tinystoriesPath).length,
    stories: stories.length,
    storiesLinted: limit,
  };
  console.error(`llm-tinystories done (${limit} stories, ${agg.propositions} propositions)`);

  // G2: flagless decision fractions must reproduce the published M0a headline
  const m0a = JSON.parse(readFileSync(join(REPO, 'mapper', 'm0', 'results', 'm0a-report.json'), 'utf8'));
  const counts = { concept: 0, prime: 0, abstain: 0, none: 0 };
  let total = 0;
  for (let i = 0; i < limit; i += 1) {
    for (const t of mapText(stories[i], ctx.lexicon /* no policy: flagless v0.1.0 */)) {
      if (!t.isWord) continue;
      total += 1;
      counts[t.decision.kind] += 1;
    }
  }
  const pct = (n) => Math.round((n / total) * 1e6) / 1e4;
  const got = {
    pctMappedToConcepts: pct(counts.concept),
    pctMappedToPrimes: pct(counts.prime),
    pctMappedTotal: pct(counts.concept + counts.prime),
    pctAbstained: pct(counts.abstain),
    pctUnmapped: pct(counts.none),
  };
  const full = limit === stories.length;
  const deltas = Object.fromEntries(
    Object.keys(got).map((k) => [k, Math.round((got[k] - m0a.headline[k]) * 1e4) / 1e4]),
  );
  g2 = {
    skipped: false,
    comparable: full,
    published_m0a: m0a.headline,
    reproduced_flagless: got,
    deltas_pp: deltas,
    pass: full && Object.values(deltas).every((d) => Math.abs(d) < 0.005),
    note: full
      ? 'full-corpus flagless pass; deltas must be ~0 (identical mapText + identical token counting)'
      : `PARTIAL corpus (${limit}/${stories.length} stories) — cross-check indicative only`,
  };
  console.error(`G2 cross-check: pass=${g2.pass}`);
}

// ---- report ------------------------------------------------------------------------
const report = {
  schema: 'kot-lnt-e0-report/0',
  experiment: 'LNT-E0 (exploratory feasibility census; NOT pre-registered; cannot flip any verdict)',
  design: 'docs/next/kernel-precision-linter.md §5 LNT-E0 (i) census, (ii) false-alarm floor, (iii) half: V-rhetorical only',
  command: `node poc/linter-census/run-lnt-e0.mjs${skipTinystories ? ' --skip-tinystories' : ''}${Number.isFinite(storiesLimit) ? ` --stories-limit=${storiesLimit}` : ''}`,
  pins: ctx.pins,
  corpusPins,
  propositionProxy:
    'clause via deterministic segmentation (tools/lint/lib/segment.mjs); conjunctive over all content tokens (pinned M0b FUNCTION_STOPLIST); NO frame/grammar conjunct exists at Stage 0, so every coverage fraction is an UPPER BOUND on true proposition-level conjunctive coverage (LNT-F1 arm (a))',
  m0bAnchor:
    'token-mass coverage MEASURED 0.3542 @ molecules-v0 on TinyStories-valid, one incomplete kernel instance, corpus-indexed, extrapolates to no other corpus (registry/verdicts/m0b.json, envelope verbatim)',
  gates: { G1_rung_monotonicity_per_slice: Object.fromEntries(Object.entries(slices).map(([k, v]) => [k, v.gateG1RungMonotonicity])), G2_m0a_crosscheck: g2 },
  slices,
  runtimeSeconds: Math.round((Date.now() - t0) / 100) / 10,
};

mkdirSync(join(HERE, 'results'), { recursive: true });
writeFileSync(join(HERE, 'results', 'lnt-e0-report.json'), stableStringify(report));

// ---- markdown summary (rendered mechanically from the same objects) -----------
const P = (x, dp = 2) => (x === null || x === undefined ? 'n/a' : `${(x * 100).toFixed(dp)}%`);
const N = (x, dp = 3) => (x === null || x === undefined ? 'n/a' : x.toFixed(dp));
const md = [];
md.push('# LNT-E0 — proposition-coverage census + false-alarm floor (Tier 0, $0)');
md.push('');
md.push('**EPISTEMIC STATUS: EXPLORATORY feasibility run — NOT pre-registered; cannot flip any verdict.**');
md.push('All numbers are MEASURED at tooling level (deterministic census, no sampling, no RNG) with scope');
md.push('EXACTLY the pinned slices below; nothing extrapolates to any other corpus. Generated by');
md.push('`run-lnt-e0.mjs` (this file is render-only over `lnt-e0-report.json`).');
md.push('');
md.push(`Design: docs/next/kernel-precision-linter.md §5 LNT-E0. Pins: kot-lint ${ctx.pins.kotLintVersion}, mapper ${ctx.pins.mapperVersion} (policy ${ctx.pins.mapperPolicy} ${String(ctx.pins.mapperPolicySha256).slice(0, 8)}…), pattern lexicon ${ctx.pins.patternLexiconVersion} (${ctx.pins.patternCount} patterns, sha ${ctx.pins.patternLexiconSha256.slice(0, 8)}…), kernel-v0 manifest ${ctx.pins.kernelManifestSha256.slice(0, 8)}…`);
md.push('');
md.push('**Proposition proxy (declared instrument limitation):** clause via deterministic segmentation;');
md.push('covered = conjunctive over all content tokens (pinned M0b stoplist). NO frame/grammar conjunct');
md.push('exists at Stage 0, so every coverage fraction below is an **UPPER BOUND** on true proposition-level');
md.push('conjunctive coverage (LNT-F1 arm (a): deterministic parser only).');
md.push('');
md.push('## (i) Census — proposition-level conjunctive coverage');
md.push('');
md.push('| slice | propositions | kernel-v0 strict | kernel-v0 member | molecules-v0 | wn31 band (membership only) |');
md.push('|---|---|---|---|---|---|');
for (const [name, s] of Object.entries(slices)) {
  const c = s.propositionCoverage.clause;
  md.push(`| ${name} | ${c.total} | ${P(c.kernelV0Strict.fraction)} | ${P(c.kernelV0Member.fraction)} | ${P(c.moleculesV0.fraction)} | ${P(c.wn31Aligned.fraction)} |`);
}
md.push('');
md.push(`Anchor (MEASURED, registry/verdicts/m0b.json): token-mass coverage 0.3542 @ molecules-v0 on`);
md.push(`TinyStories-valid — the conjunctive proposition-level number above is the linter's engagement`);
md.push(`ceiling and is expected to sit far below it (N-PL §5 LNT-E0(i), §9.3).`);
md.push('');
md.push('## Engagement vectors (Stage-0 lattice projection; M = fully kernel-v0-mappable, groundedness NOT evaluated)');
md.push('');
md.push('| slice | M | A | U-mol | U-wn31 | U-out | V-flagged propositions |');
md.push('|---|---|---|---|---|---|---|');
for (const [name, s] of Object.entries(slices)) {
  const e = s.engagement.fractions;
  md.push(`| ${name} | ${P(e.M)} | ${P(e.A)} | ${P(e['U-mol'])} | ${P(e['U-wn31'])} | ${P(e['U-out'])} | ${P(s.engagement.vFlaggedPropositionFraction, 3)} |`);
}
md.push('');
md.push('## (ii) False-alarm floor (warn-severity flags; U is info-only, never an alarm in mode P)');
md.push('');
md.push('| slice | V/1000w | A/1000w | warn/1000w | sentences with >=1 warn |');
md.push('|---|---|---|---|---|');
for (const [name, s] of Object.entries(slices)) {
  const f = s.falseAlarm;
  md.push(`| ${name} | ${N(f.vPer1000Words)} | ${N(f.aPer1000Words)} | ${N(f.warnPer1000Words)} | ${P(f.sentencesWithWarnFraction, 3)} |`);
}
md.push('');
md.push('On `clean-human` (human-authored precise technical documentation) every warn flag is BY');
md.push('CONSTRUCTION counted as a false alarm — the floor. Per-pattern hit counts (all slices) are in');
md.push('the JSON (`vByPattern`, `aTopSurfaces`) so noisy patterns can be cut at prereg time by');
md.push('measurement, not argument.');
md.push('');
md.push('## (iii) V-rhetorical / V-tautology split — HALF-MEASURABLE at Stage 0');
md.push('');
md.push('V-tautology needs the explication normaliser (coverage-dependent; Stage 1+). Only the');
md.push('V-rhetorical (pattern-tier, coverage-independent) half is measured above. Stated as a');
md.push('half-measurement, per the census design.');
md.push('');
md.push('## Instrument gates');
md.push('');
md.push(`- G1 rung monotonicity (kStrict <= kMember <= molecules <= wn31, both units, every slice): ${Object.entries(report.gates.G1_rung_monotonicity_per_slice).map(([k, v]) => `${k}=${v}`).join(', ')}`);
if (g2.skipped) md.push('- G2 m0a cross-check: SKIPPED (no tinystories slice this run)');
else md.push(`- G2 m0a cross-check (flagless decision fractions vs published M0a headline): pass=${g2.pass}${g2.comparable ? '' : ' (PARTIAL corpus — indicative only)'}; deltas(pp)=${JSON.stringify(g2.deltas_pp)}`);
md.push('');
md.push(`Runtime ${report.runtimeSeconds}s on r0-local-cpu (2 shared cores, niced).`);
md.push('');
writeFileSync(join(HERE, 'results', 'lnt-e0-report.md'), `${md.join('\n')}\n`);
console.error(`report -> ${join(HERE, 'results', 'lnt-e0-report.json')} + .md (${report.runtimeSeconds}s)`);
