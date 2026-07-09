/**
 * kot-lint core — Stage-0 mode-P lint (docs/next/kernel-precision-linter.md
 * §6 Stage 0): the COVERAGE-INDEPENDENT usable classes only.
 *
 *   V-rhetorical  deterministic filler/weasel/hedge patterns  -> warn
 *   A ambiguous   mapper abstentions (candidates listed)      -> warn
 *   U coverage    per-token vocabulary-band annotation        -> info
 *
 * NOT here, by design (Stage 1+, needs the checker/renderer/coverage):
 * G+/G− decode-verify against canonical records, V-tautology explication
 * normalisation, mode S quarantine, mode R rewrite. The engagement vector
 * therefore reports the Stage-0 PROJECTION of the N-PL §3.2 lattice:
 * {M, A, U-*} plus orthogonal V flags — class M means "fully
 * kernel-v0-mappable; groundedness NOT evaluated at Stage 0", never G+.
 *
 * Determinism (S5): same text + same pinned inputs -> byte-identical report.
 * No RNG, no timestamps inside report bodies, stable key order via
 * stableStringify.
 */
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  buildLexicon,
  loadManifestConcepts,
  lemmaCandidates,
  mapText,
  policyHash,
  policyPreset,
  targetKey,
} from '../../../mapper/dist/src/index.js';
import { segmentSentences, segmentClauses, stripMarkdown } from './segment.mjs';
import { compilePatterns, matchVacuityPatterns, patternLexiconSha256, PATTERN_LEXICON, PATTERN_LEXICON_VERSION } from './patterns.mjs';
import { FUNCTION_STOPLIST, loadMoleculeLemmas, loadWn31Lemmas, sha256File } from './vocab.mjs';

export const KOT_LINT_VERSION = '0.1.0';
const HERE = dirname(fileURLToPath(import.meta.url));
export const REPO_ROOT = join(HERE, '..', '..', '..');

/**
 * Build the shared lint context (load once, lint many documents).
 * policyName: 'a1-hybrid' (default; N-PL §2 S2 names the signed a1-hybrid
 * preset as the linter's mapper preset) or 'none' (v0.1.0 abstain-and-record).
 * wn31: load the wn31-aligned membership band (~166k lemmas; a few seconds).
 */
export function buildLintContext({ policyName = 'a1-hybrid', wn31 = true, repoRoot = REPO_ROOT } = {}) {
  const manifestPath = join(repoRoot, 'data', 'kernel-v0', 'manifest.json');
  const lexicon = buildLexicon(loadManifestConcepts(manifestPath));
  const policy = policyName === 'none' ? undefined : policyPreset(policyName);
  const molLemmas = loadMoleculeLemmas(repoRoot);
  const wn31Lemmas = wn31 ? loadWn31Lemmas(repoRoot) : null;
  const mapperVersion = JSON.parse(readFileSync(join(repoRoot, 'mapper', 'package.json'), 'utf8')).version;
  const pins = {
    kotLintVersion: KOT_LINT_VERSION,
    mapperVersion,
    mapperPolicy: policy === undefined ? 'none' : policy.name,
    mapperPolicySha256: policy === undefined ? null : policyHash(policy),
    kernelManifestSha256: sha256File(manifestPath),
    moleculesManifestSha256: sha256File(join(repoRoot, 'data', 'molecules-v0', 'manifest.json')),
    wn31ManifestSha256: wn31 ? sha256File(join(repoRoot, 'data', 'lexical-wn31', 'manifest.json')) : null,
    patternLexiconVersion: PATTERN_LEXICON_VERSION,
    patternLexiconSha256: patternLexiconSha256(),
    patternCount: PATTERN_LEXICON.length,
  };
  return { lexicon, policy, molLemmas, wn31Lemmas, compiled: compilePatterns(), pins };
}

/** Vocabulary band of one content token (m0b rung ladder; vocab.mjs).
 * Returns 'kernel-v0' | 'kernel-v0-member' | 'molecules-v0' | 'wn31-aligned' | 'out'. */
function tokenBand(t, ctx) {
  const d = t.decision;
  if (d.kind === 'concept' || d.kind === 'prime') return 'kernel-v0';
  if (d.kind === 'abstain') return 'kernel-v0-member'; // in-vocabulary, sense-unresolved
  const cands = new Set([t.norm, t.lemma, ...lemmaCandidates(t.norm)]);
  for (const c of cands) if (ctx.molLemmas.has(c)) return 'molecules-v0';
  if (ctx.wn31Lemmas !== null) {
    for (const c of cands) if (ctx.wn31Lemmas.has(c)) return 'wn31-aligned';
  }
  return 'out';
}

const BAND_RANK = { 'kernel-v0': 0, 'kernel-v0-member': 1, 'molecules-v0': 2, 'wn31-aligned': 3, out: 4 };

/** Conjunctive coverage of a token group at each rung (unit = clause or
 * sentence). Membership rungs are monotone by construction. */
function groupCoverage(contentBands) {
  const worst = contentBands.reduce((m, b) => Math.max(m, BAND_RANK[b]), 0);
  return {
    kStrict: contentBands.length > 0 && worst === 0, // every content token mapper-resolved
    kMember: contentBands.length > 0 && worst <= 1, // + abstentions count as in-vocabulary
    mol: contentBands.length > 0 && worst <= 2,
    wn31: contentBands.length > 0 && worst <= 3,
  };
}

/**
 * Lint one document. Returns {report, flags}. `report` is aggregate-only and
 * deterministic; flags carry offsets into the (possibly stripped) text —
 * stripping is offset-preserving, so offsets always index the ORIGINAL file.
 */
export function lintDocument(rawText, ctx, { strip = 'none', collectTokens = false } = {}) {
  const text = strip === 'markdown' ? stripMarkdown(rawText) : rawText;
  const anns = mapText(text, ctx.lexicon, ctx.policy);
  const words = anns.filter((t) => t.isWord);
  const sentences = segmentSentences(text);

  const flags = [];
  const counts = {
    expandedWordTokens: 0,
    contentTokens: 0,
    decisions: { concept: 0, prime: 0, abstain: 0, none: 0 },
    contentBands: { 'kernel-v0': 0, 'kernel-v0-member': 0, 'molecules-v0': 0, 'wn31-aligned': 0, out: 0 },
    flagCounts: { V: { filler: 0, weasel: 0, hedge: 0, total: 0 }, A: 0 },
  };
  const cov = {
    clause: { kStrict: 0, kMember: 0, mol: 0, wn31: 0, total: 0 },
    sentence: { kStrict: 0, kMember: 0, mol: 0, wn31: 0, total: 0 },
  };
  const engagement = { M: 0, A: 0, 'U-mol': 0, 'U-wn31': 0, 'U-out': 0 };
  let noContentClauses = 0;
  let vFlaggedPropositions = 0;
  let whollyVacuousClauses = 0;
  let sentencesWithWarn = 0;
  const contentLenPerProposition = [];
  const tokenAnnotations = collectTokens ? [] : null;

  // token-level tallies (m0a-comparable: every expanded word token counts)
  const bandByToken = new Map(); // word index -> band (content tokens only)
  for (let w = 0; w < words.length; w += 1) {
    const t = words[w];
    counts.expandedWordTokens += 1;
    counts.decisions[t.decision.kind] += 1;
    if (!FUNCTION_STOPLIST.has(t.norm)) {
      counts.contentTokens += 1;
      const band = tokenBand(t, ctx);
      counts.contentBands[band] += 1;
      bandByToken.set(w, band);
      if (tokenAnnotations !== null) {
        tokenAnnotations.push({ surface: t.surface, norm: t.norm, start: t.start, end: t.end, band });
      }
    }
    // A-flags: one per abstained phrase head, CONTENT tokens only.
    // Declared Stage-0 operationalisation: function-word abstentions (copula
    // is/was collisions etc.) are lexicon artifacts, not imprecise content
    // wording — flagging every copula would be pure alarm noise (the Bessey
    // lesson N-PL §1.1). They stay visible in tokens.decisions.abstain.
    if (t.decision.kind === 'abstain' && t.phrasePos === 0 && !FUNCTION_STOPLIST.has(t.norm)) {
      counts.flagCounts.A += 1;
      flags.push({
        class: 'A',
        severity: 'warn',
        message: `ambiguous: "${t.surface}" has ${t.decision.candidates.length} kernel candidates (sense unresolved)`,
        candidates: t.decision.candidates.map(targetKey).sort(),
        start: t.start,
        end: t.end,
        text: t.surface,
      });
    }
  }

  // sentence/clause pass
  let wIdx = 0;
  for (const s of sentences) {
    // word tokens inside this sentence (words are in stream order)
    const sTokens = [];
    const sIdx = [];
    while (wIdx < words.length && words[wIdx].start < s.end) {
      if (words[wIdx].start >= s.start) {
        sTokens.push(words[wIdx]);
        sIdx.push(wIdx);
      }
      wIdx += 1;
    }
    if (sTokens.length === 0) continue;

    // V-rhetorical pattern matching over the sentence's word stream
    const vHits = matchVacuityPatterns(text, sTokens, ctx.compiled);
    for (const h of vHits) {
      counts.flagCounts.V[h.category] += 1;
      counts.flagCounts.V.total += 1;
      flags.push({
        class: 'V',
        severity: 'warn',
        message: `vacuous (${h.category}): "${h.text}" carries no checkable content`,
        patternId: h.id,
        start: h.start,
        end: h.end,
        text: h.text,
      });
    }
    const sentenceHasWarn =
      vHits.length > 0 ||
      sTokens.some((t) => t.decision.kind === 'abstain' && !FUNCTION_STOPLIST.has(t.norm));
    if (sentenceHasWarn) sentencesWithWarn += 1;

    // sentence-level conjunctive coverage
    const sBands = sIdx.filter((w) => bandByToken.has(w)).map((w) => bandByToken.get(w));
    if (sBands.length > 0) {
      const c = groupCoverage(sBands);
      cov.sentence.total += 1;
      if (c.kStrict) cov.sentence.kStrict += 1;
      if (c.kMember) cov.sentence.kMember += 1;
      if (c.mol) cov.sentence.mol += 1;
      if (c.wn31) cov.sentence.wn31 += 1;
    }

    // clause-level (the proposition proxy)
    const idxOf = new Map();
    for (let k = 0; k < sTokens.length; k += 1) idxOf.set(sTokens[k], sIdx[k]);
    const clauses = segmentClauses(text, sTokens);
    for (const clause of clauses) {
      const cBands = [];
      for (const t of clause) {
        const w = idxOf.get(t);
        if (bandByToken.has(w)) cBands.push(bandByToken.get(w));
      }
      if (cBands.length === 0) {
        noContentClauses += 1;
        continue;
      }
      const c = groupCoverage(cBands);
      cov.clause.total += 1;
      contentLenPerProposition.push(cBands.length);
      if (c.kStrict) cov.clause.kStrict += 1;
      if (c.kMember) cov.clause.kMember += 1;
      if (c.mol) cov.clause.mol += 1;
      if (c.wn31) cov.clause.wn31 += 1;
      // Stage-0 lattice projection (one primary class per proposition)
      const worst = cBands.reduce((m, b) => Math.max(m, BAND_RANK[b]), 0);
      if (worst === 0) engagement.M += 1;
      else if (worst === 1) engagement.A += 1;
      else if (worst === 2) engagement['U-mol'] += 1;
      else if (worst === 3) engagement['U-wn31'] += 1;
      else engagement['U-out'] += 1;
      // orthogonal V annotation on the clause
      const cStart = clause[0].start;
      const cEnd = clause[clause.length - 1].end;
      const overlapping = vHits.filter((h) => h.start < cEnd && h.end > cStart);
      if (overlapping.length > 0) {
        vFlaggedPropositions += 1;
        const covered = clause.filter(
          (t) => !FUNCTION_STOPLIST.has(t.norm) && overlapping.some((h) => t.start >= h.start && t.end <= h.end),
        ).length;
        if (covered === cBands.length) whollyVacuousClauses += 1;
      }
    }
  }

  flags.sort((a, b) => a.start - b.start || a.end - b.end || (a.class < b.class ? -1 : 1));
  contentLenPerProposition.sort((a, b) => a - b);
  const pct = (num, den) => (den > 0 ? Math.round((num / den) * 1e6) / 1e6 : null);
  const q = (p) =>
    contentLenPerProposition.length > 0
      ? contentLenPerProposition[Math.min(contentLenPerProposition.length - 1, Math.floor(p * contentLenPerProposition.length))]
      : null;

  const propositions = cov.clause.total;
  const report = {
    chars: text.length,
    sentences: sentences.length,
    clauses: propositions + noContentClauses,
    propositions, // clauses with >=1 content token (the census denominator)
    noContentClauses,
    tokens: {
      expandedWordTokens: counts.expandedWordTokens,
      contentTokens: counts.contentTokens,
      decisions: counts.decisions,
      contentBands: counts.contentBands,
    },
    propositionCoverage: {
      unitDefinition:
        'clause = deterministic proposition proxy (segment.mjs); covered = CONJUNCTIVE over all content tokens in the unit; NO frame/grammar conjunct at Stage 0, so all fractions are UPPER BOUNDS on full proposition-level conjunctive coverage',
      clause: {
        total: cov.clause.total,
        kernelV0Strict: { covered: cov.clause.kStrict, fraction: pct(cov.clause.kStrict, cov.clause.total) },
        kernelV0Member: { covered: cov.clause.kMember, fraction: pct(cov.clause.kMember, cov.clause.total) },
        moleculesV0: { covered: cov.clause.mol, fraction: pct(cov.clause.mol, cov.clause.total) },
        wn31Aligned: { covered: cov.clause.wn31, fraction: pct(cov.clause.wn31, cov.clause.total) },
      },
      sentence: {
        total: cov.sentence.total,
        kernelV0Strict: { covered: cov.sentence.kStrict, fraction: pct(cov.sentence.kStrict, cov.sentence.total) },
        kernelV0Member: { covered: cov.sentence.kMember, fraction: pct(cov.sentence.kMember, cov.sentence.total) },
        moleculesV0: { covered: cov.sentence.mol, fraction: pct(cov.sentence.mol, cov.sentence.total) },
        wn31Aligned: { covered: cov.sentence.wn31, fraction: pct(cov.sentence.wn31, cov.sentence.total) },
      },
    },
    engagement: {
      classes: engagement,
      fractions: Object.fromEntries(Object.entries(engagement).map(([k, v]) => [k, pct(v, propositions)])),
      note: 'Stage-0 projection of the N-PL §3.2 lattice: M = fully kernel-v0-mappable (groundedness NOT evaluated); G+/G-/V-tautology require Stage-1 machinery',
      vFlaggedPropositions,
      whollyVacuousClauses,
    },
    flagCounts: counts.flagCounts,
    rates: {
      vPer1000Words: pct(counts.flagCounts.V.total * 1000, counts.expandedWordTokens),
      aPer1000Words: pct(counts.flagCounts.A * 1000, counts.expandedWordTokens),
      warnPer1000Words: pct((counts.flagCounts.V.total + counts.flagCounts.A) * 1000, counts.expandedWordTokens),
      sentencesWithWarn,
      sentencesWithWarnFraction: pct(sentencesWithWarn, sentences.length),
    },
    propositionContentLength: {
      mean: pct(contentLenPerProposition.reduce((a, b) => a + b, 0), contentLenPerProposition.length),
      p50: q(0.5),
      p90: q(0.9),
    },
  };
  return { report, flags, tokenAnnotations };
}

/** Deterministic JSON: recursively sorted keys, LF-terminated. */
export function stableStringify(value, indent = 2) {
  const sortValue = (v) => {
    if (Array.isArray(v)) return v.map(sortValue);
    if (v !== null && typeof v === 'object') {
      return Object.fromEntries(Object.keys(v).sort().map((k) => [k, sortValue(v[k])]));
    }
    return v;
  };
  return `${JSON.stringify(sortValue(value), null, indent)}\n`;
}

/** offset -> {line, col} (1-based) for CLI display. */
export function lineColConverter(text) {
  const starts = [0];
  for (let i = 0; i < text.length; i += 1) if (text[i] === '\n') starts.push(i + 1);
  return (offset) => {
    let lo = 0;
    let hi = starts.length - 1;
    while (lo < hi) {
      const mid = (lo + hi + 1) >> 1;
      if (starts[mid] <= offset) lo = mid;
      else hi = mid - 1;
    }
    return { line: lo + 1, col: offset - starts[lo] + 1 };
  };
}
