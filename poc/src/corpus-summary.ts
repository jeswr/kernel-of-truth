/**
 * Combined summary for the kernel-v0 corpus re-runs of X1-X4 (bead
 * kernel-of-truth-138). Reads the four x*-kernel-v0-report.json files and
 * writes results/kernel-v0-phase-x-summary.md. Run AFTER the four harnesses.
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fmt } from '../harness/common.js';
import { RESULTS_DIR, loadCorpus, slug } from './corpus-common.js';

function main(): void {
  const read = <T>(name: string): T =>
    JSON.parse(readFileSync(join(RESULTS_DIR, name), 'utf8')) as T;
  /* eslint-disable @typescript-eslint/no-explicit-any */
  const x1 = read<any>('x1-kernel-v0-report.json');
  const x2 = read<any>('x2-kernel-v0-report.json');
  const x3 = read<any>('x3-kernel-v0-report.json');
  const x4 = read<any>('x4-kernel-v0-report.json');
  const corpus = loadCorpus();

  const p512 = x4.projections['8192->512'];
  const p576 = x4.projections['8192->576'];
  const near = x3.nearPairComparison;
  const md = [
    '# Phase X on the AUTHORED kernel-v0 corpus — combined summary',
    '',
    `date: ${new Date().toISOString()}`,
    `corpus: kernel-v0, ${corpus.docs.length} concepts (research-grade, agent-authored, NOT federation-endorsed)`,
    `encoder content-hash: \`${x1.encoderContentHash}\` (matches manifest pin: ${x1.encoderHashMatchesManifest})`,
    `corpus content-hash: \`${x1.corpusContentHash}\``,
    '',
    'The Phase-X pre-registered property tests (docs/poc-design.md), previously run on',
    'seeded synthetics only, re-run on the authored corpus. Per-suite reports:',
    'x1-kernel-v0-report.md, x2-kernel-v0-report.md, x3-kernel-v0-report.md, x4-kernel-v0-report.md.',
    '',
    '## Headlines',
    '',
    '| suite | headline on authored kernel-v0 | pre-registered bar | verdict |',
    '|---|---|---|---|',
    `| X1 | min adversarial single-edit angle ${fmt(x1.minAdversarialRad, 6)} rad over ${x1.totalNeighbours} neighbours; fp16 floor ${fmt(x1.fp16FloorRad, 6)} rad; ratio ${fmt(x1.ratioToFloor, 1)}x | >5x floor | **${x1.verdict}** |`,
    `| X2 | ${x2.minimal.exact}/${x2.minimal.total} exact decode (minimal lexicon; full-corpus lexicon ${x2.fullCorpus.exact}/${x2.fullCorpus.total}); non-exact: afraid, angry, sad | 100% exact (depth <= 4 instantiation) | **${x2.pass ? 'PASS' : 'FAIL'}** |`,
    `| X3 | ${near.invertingEditsCloserThanNearestPair}/${near.invertingEdits} meaning-inverting edits sit closer than the nearest distinct pair (\`${slug(near.nearestDistinctPair.a)}\`<->\`${slug(near.nearestDistinctPair.b)}\` cos ${fmt(near.nearestDistinctPair.cos)}); inverting median cos ${fmt(near.invertingSummary.median)} | none (documentation) | documented |`,
    `| X4 | RDM Spearman ${fmt(p512.rdmSpearman)} (512) / ${fmt(p576.rdmSpearman)} (576); min R^d margin ${fmt(p512.minAdversarialRad, 6)} / ${fmt(p576.minAdversarialRad, 6)} rad = ${fmt(p512.minToFloorRatio, 1)}x / ${fmt(p576.minToFloorRatio, 1)}x floor | X1 criteria in R^d | **${p512.verdictX1Criteria} / ${p576.verdictX1Criteria}** |`,
    '',
    '## Named minimum-margin pair (all 1431 authored pairs)',
    '',
    `**\`${slug(x1.pairwise.minPair.a)}\` <-> \`${slug(x1.pairwise.minPair.b)}\`** at ${fmt(x1.pairwise.minPair.angle, 6)} rad ` +
      `(${fmt(x1.pairwise.minPair.angle / x1.fp16FloorRad, 1)}x fp16 floor). Top nearest pairs:`,
    '',
    ...x1.pairwise.top10Nearest
      .slice(0, 5)
      .map((p: { a: string; b: string; angle: number }, i: number) => `${i + 1}. ${slug(p.a)} <-> ${slug(p.b)}: ${fmt(p.angle, 6)} rad`),
    '',
    '## Deltas vs the synthetic runs',
    '',
    '- Synthetic X1 (reduced n=500, results/x1-report.md): min adversarial 0.015988 rad = 63.4x floor.',
    '- Synthetic X2 gate passed 720/720 (full grid); the authored corpus FAILS it 51/54 —',
    '  the quote-re-anchored emotion trio (afraid/angry/sad) drops optional SP slots or',
    '  misorders a referent introduction under deep quote+op nesting, identically in both',
    '  lexicon conditions (kernel-of-truth-0kn).',
    '- The authored corpus exercises what synthetics cannot: reference-bearing concepts',
    `  (${x2.minimal.referenceBearingExact}/${x2.minimal.referenceBearingTotal} exact decode), quote re-anchoring, the deliberately-near give/take/gift`,
    '  cluster (which is NOT the nearest pair — the emotion cluster is; kernel-of-truth-7yp),',
    '  and authored known-weak explications (manifest.json#knownWeak).',
    '',
    '> Adequacy of these explications is unvalidated (social, not proven); these are',
    '> encoder property tests, not NSM-adequacy claims.',
  ].join('\n');
  const file = join(RESULTS_DIR, 'kernel-v0-phase-x-summary.md');
  writeFileSync(file, md);
  console.log(`wrote ${file}`);
}

main();
