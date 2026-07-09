#!/usr/bin/env node
/**
 * kot-lint mechanics self-test ($0, no corpus): planted-defect fixtures +
 * determinism + monotonicity. Run: node tools/lint/test/selftest.mjs
 * Exits nonzero on any failure (fail-closed).
 */
import assert from 'node:assert/strict';
import { buildLintContext, lintDocument, stableStringify } from '../lib/lint.mjs';
import { segmentSentences, segmentClauses, stripMarkdown } from '../lib/segment.mjs';

const ctx = buildLintContext({ policyName: 'a1-hybrid', wn31: false });

// --- segmentation ------------------------------------------------------------
{
  const text = 'The cat sat. It was happy! Dr. Smith saw it, e.g. at home. New one here.';
  const spans = segmentSentences(text);
  assert.equal(spans.length, 4, `expected 4 sentences, got ${spans.length}: ${JSON.stringify(spans.map((s) => text.slice(s.start, s.end)))}`);
  assert.equal(text.slice(spans[2].start, spans[2].end), 'Dr. Smith saw it, e.g. at home.');
}
{
  const md = 'A [link](http://x.example/y) and `code` here.\n\n```\nblock\n```\n\nEnd.';
  const stripped = stripMarkdown(md);
  assert.equal(stripped.length, md.length, 'stripMarkdown must preserve length');
  assert.ok(stripped.includes('link'), 'link label kept');
  assert.equal(stripped.indexOf('link'), md.indexOf('link'), 'link label offset preserved');
  assert.ok(!stripped.includes('http'), 'link target blanked');
  assert.ok(!stripped.includes('block'), 'fenced code blanked');
}

// --- V-rhetorical flags -------------------------------------------------------
{
  const text =
    'It is important to note that the cat sat. Many experts believe the dog ran. To some extent the bird sang. The child played.';
  const { report, flags } = lintDocument(text, ctx);
  const v = flags.filter((f) => f.class === 'V');
  assert.equal(report.flagCounts.V.filler, 1, 'filler pattern fires once');
  assert.equal(report.flagCounts.V.weasel, 1, 'weasel pattern fires once');
  assert.equal(report.flagCounts.V.hedge, 1, 'hedge pattern fires once');
  assert.equal(v.length, 3);
  assert.ok(v[0].text.toLowerCase().startsWith('it is important to note that'), `optional-token match: ${v[0].text}`);
  // clean last sentence carries no V flag
  assert.ok(v.every((f) => f.start < text.indexOf('The child')), 'no V flag on the clean sentence');
}
// contraction-expanded match: "it's" == "it is"
{
  const { report } = lintDocument("It's important to note that the cat sat.", ctx);
  assert.equal(report.flagCounts.V.filler, 1, 'pattern matches through contraction expansion');
}

// --- A flags (mapper abstention) ---------------------------------------------
{
  const { report, flags } = lintDocument('She was kind to the small animal.', ctx);
  const a = flags.filter((f) => f.class === 'A');
  assert.ok(report.flagCounts.A >= 1, 'abstention flag fires (kind)');
  assert.ok(a.some((f) => f.text.toLowerCase() === 'kind'), 'kind is flagged ambiguous under a1-hybrid (excluded, not tier-resolved)');
  assert.ok(a.every((f) => Array.isArray(f.candidates) && f.candidates.length > 1));
}

// --- engagement + coverage monotonicity ---------------------------------------
{
  const text =
    'The small cat sat inside the big box. The quantum chromodynamics lagrangian is renormalizable. She was kind.';
  const { report } = lintDocument(text, ctx);
  const c = report.propositionCoverage.clause;
  assert.ok(c.kernelV0Strict.covered <= c.kernelV0Member.covered, 'kStrict <= kMember');
  assert.ok(c.kernelV0Member.covered <= c.moleculesV0.covered, 'kMember <= mol');
  assert.ok(c.moleculesV0.covered <= c.wn31Aligned.covered, 'mol <= wn31');
  const eng = report.engagement.classes;
  assert.equal(
    eng.M + eng.A + eng['U-mol'] + eng['U-wn31'] + eng['U-out'],
    report.propositions,
    'engagement classes partition propositions',
  );
}

// --- determinism (S5): byte-identical reports ---------------------------------
{
  const text = 'It is important to note that the small cat sat inside the box, and the dog ran because it was happy.';
  const a = lintDocument(text, ctx);
  const b = lintDocument(text, ctx);
  assert.equal(
    stableStringify({ report: a.report, flags: a.flags }),
    stableStringify({ report: b.report, flags: b.flags }),
    'same text + same pins -> byte-identical report',
  );
}

// --- clause proxy ---------------------------------------------------------------
{
  const text = 'The cat sat, and the dog ran because it was happy; the bird sang.';
  const spans = segmentSentences(text);
  assert.equal(spans.length, 1);
  // reuse lint to count propositions: ", and" split + "because" split + ";" split
  const { report } = lintDocument(text, ctx);
  assert.equal(report.clauses, 4, `expected 4 clauses, got ${report.clauses}`);
}

console.log('kot-lint selftest OK (all assertions passed; wn31 band not loaded — band membership exercised at mol rung only)');
