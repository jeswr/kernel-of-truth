/**
 * X2 on the AUTHORED kernel-v0 corpus (bead kernel-of-truth-138): exact decode
 * of all 54 concepts, GIVEN THE KERNEL, under TWO cleanup-lexicon conditions:
 *
 *   minimal — the concept lexicon contains exactly the ids the explication
 *     references (empty for the 36 non-reference-bearing concepts). This is
 *     the corpus instantiation of the synthetic X2 setting and of the
 *     encodeConceptSet contract (references resolve against the corpus).
 *   full-corpus — all OTHER 53 canonical vectors supplied as the lexicon
 *     (self excluded so recovery cannot lean on the target's own vector).
 *     Harder: every decode step's atomic-vs-concept competition now sees 53
 *     candidate attractors, including deliberately-near concepts.
 *
 * Exact recovery = canonical-JSON equality with the authored AST. The
 * inherited criterion (synthetic X2: 100% exact at depth <= 4) is applied to
 * the MINIMAL condition; the full-corpus condition is reported as a
 * measurement of cleanup-lexicon interference (a false-attractor pathology,
 * kin to X3's documentation duty).
 *
 * Writes results/x2-kernel-v0-report.{json,md} — never x2-report.*.
 */

import {
  encodeConceptSet,
  decodeExplication,
  validateExplication,
  canonicalJson,
  encoderContentHash,
} from '@jeswr/kernel-encoder';
import { fmt } from '../harness/common.js';
import { corpusStamp, loadCorpus, slug, stampMd, writeCorpusReport } from './corpus-common.js';

interface Row {
  id: string;
  frame: string;
  clauseCount: number;
  maxDepth: number;
  conceptRefs: number;
  exact: boolean;
  ok: boolean;
  minConfidence: number;
  ms: number;
  failure?: string;
}

function main(): void {
  const corpus = loadCorpus();
  console.log(`X2-corpus: decoding ${corpus.docs.length} authored concepts (minimal + full-corpus lexicons)`);
  const { vectors } = encodeConceptSet(corpus.defs);

  const runCondition = (
    condition: 'minimal' | 'full-corpus',
    lexiconFor: (doc: (typeof corpus.docs)[number]) => Map<string, Float64Array>,
  ): Row[] => {
    const rows: Row[] = [];
    const t0 = Date.now();
    for (const doc of corpus.docs) {
      const stats = validateExplication(doc.explication);
      const t = Date.now();
      const r = decodeExplication(vectors.get(doc.id)!, { concepts: lexiconFor(doc) });
      const ms = Date.now() - t;
      const exact = r.ok && canonicalJson(r.explication!) === canonicalJson(doc.explication);
      const row: Row = {
        id: doc.id,
        frame: doc.explication.frame,
        clauseCount: stats.clauseCount,
        maxDepth: stats.maxDepth,
        conceptRefs: doc.references.length,
        exact,
        ok: r.ok,
        minConfidence: r.minConfidence,
        ms,
      };
      if (!exact) {
        row.failure = r.ok
          ? 'ok-but-wrong: decoded AST validates but differs from authored AST'
          : `decode failed: ${r.validationError ?? 'incomplete AST'}; lowest-confidence step: ${JSON.stringify(
              r.steps.reduce((m, s) => (s.confidence < m.confidence ? s : m), r.steps[0]!),
            )}`;
        console.error(`  [${condition}] NON-EXACT ${slug(doc.id)}: ${row.failure}`);
      }
      rows.push(row);
      if (rows.length % 10 === 0) {
        console.log(`  [${condition}] ${rows.length}/${corpus.docs.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
      }
    }
    return rows;
  };

  console.log('condition 1/2: minimal lexicon (referenced ids only — the pre-registered X2 setting)');
  const minimal = runCondition('minimal', (doc) => new Map(doc.references.map((id) => [id, vectors.get(id)!])));
  console.log('condition 2/2: full-corpus lexicon (all 53 others; interference measurement)');
  const fullCorpus = runCondition('full-corpus', (doc) => new Map([...vectors].filter(([id]) => id !== doc.id)));

  const analyse = (rows: Row[]) => {
    const exact = rows.filter((r) => r.exact).length;
    const refBearing = rows.filter((r) => r.conceptRefs > 0);
    const minConf = rows.reduce((m, r) => Math.min(m, r.minConfidence), Infinity);
    return {
      exact,
      total: rows.length,
      pass: exact === rows.length,
      referenceBearingExact: refBearing.filter((r) => r.exact).length,
      referenceBearingTotal: refBearing.length,
      minConfidence: minConf,
      minConfidenceConcept: rows.find((r) => r.minConfidence === minConf)!.id,
      nonExact: rows.filter((r) => !r.exact),
    };
  };
  const aMin = analyse(minimal);
  const aFull = analyse(fullCorpus);

  const stamp = corpusStamp(corpus, encoderContentHash());
  const json = {
    ...stamp,
    suite: 'X2-corpus: exact decode of all authored concepts (minimal + full-corpus cleanup lexicons)',
    criterion:
      '54/54 exact under the MINIMAL lexicon (corpus instantiation of poc-design X2: 100% at depth <= 4); full-corpus condition is an interference measurement',
    pass: aMin.pass,
    minimal: { ...aMin, nonExact: undefined, rows: minimal },
    fullCorpus: { ...aFull, nonExact: undefined, rows: fullCorpus },
    decoderDefaults: '3 refinement passes, default thetaAbs',
  };
  const condTable = (rows: Row[]): string[] => [
    '| concept | frame | clauses | depth | crefs | exact | min-conf | ms |',
    '|---|---|---|---|---|---|---|---|',
    ...rows.map(
      (r) =>
        `| ${slug(r.id)} | ${r.frame} | ${r.clauseCount} | ${r.maxDepth} | ${r.conceptRefs} | ` +
        `${r.exact ? 'yes' : '**NO**'} | ${fmt(r.minConfidence, 3)} | ${r.ms} |`,
    ),
  ];
  const md = [
    '# X2 on kernel-v0 — exact decode (minimal vs full-corpus cleanup lexicon)',
    '',
    ...stampMd(stamp),
    '',
    `**Criterion (minimal lexicon): 54/54 exact -> ${aMin.pass ? 'PASS' : 'FAIL'}** ` +
      `(${aMin.exact}/${aMin.total} exact; reference-bearing ${aMin.referenceBearingExact}/${aMin.referenceBearingTotal}; ` +
      `min confidence ${fmt(aMin.minConfidence, 3)} at \`${slug(aMin.minConfidenceConcept)}\`)`,
    '',
    `Full-corpus lexicon (all 53 others as cleanup candidates): ${aFull.exact}/${aFull.total} exact ` +
      `(reference-bearing ${aFull.referenceBearingExact}/${aFull.referenceBearingTotal}; ` +
      `min confidence ${fmt(aFull.minConfidence, 3)}). The gap between the two conditions measures`,
    'cleanup-lexicon interference: extra corpus vectors acting as false attractors during',
    "the decoder's atomic-vs-concept competitions. Exact = canonical-JSON equality.",
    '',
    '## Minimal lexicon (pre-registered setting)',
    '',
    ...condTable(minimal),
    '',
    ...(aMin.nonExact.length > 0
      ? ['### Non-exact (minimal)', '', ...aMin.nonExact.map((r) => `- \`${slug(r.id)}\`: ${r.failure}`), '']
      : []),
    '## Full-corpus lexicon (interference measurement)',
    '',
    ...condTable(fullCorpus),
    '',
    ...(aFull.nonExact.length > 0
      ? ['### Non-exact (full-corpus)', '', ...aFull.nonExact.map((r) => `- \`${slug(r.id)}\`: ${r.failure}`), '']
      : []),
    '> Decoding is stated, per the construction, as recoverable GIVEN THE KERNEL',
    '> (codebook + concept lexicon as cleanup memory). Confidence = selection',
    '> margin (best vs runner-up) or presence ratio per decode step.',
  ].join('\n');
  writeCorpusReport('x2-kernel-v0-report', json, md);
  console.log(
    `X2-corpus ${aMin.pass ? 'PASS' : 'FAIL'} (minimal ${aMin.exact}/${aMin.total}; full-corpus ${aFull.exact}/${aFull.total})`,
  );
  process.exitCode = aMin.pass ? 0 : 1;
}

main();
