/**
 * X2-q — decode REALITY CHECK for the toy-native variant kot-enc-Bq/1 at
 * D ∈ {512, 576} (bead kernel-of-truth-5xo). MEASUREMENT ONLY, NOT GATED:
 * the capacity arithmetic (DCV §7.2: robust decode needs D ≈ 4k-20k at the
 * capped structure budget) says full decode cannot survive at d_model; the
 * pre-registration scopes the toy-native path to "structure-derived content
 * vs content-free at matched D" and explicitly away from the capacity claim.
 * This harness measures what decode DOES achieve, for honesty, using the
 * same protocol as X2-corpus (exact recovery = canonical-JSON equality,
 * minimal + full-corpus cleanup lexicons) plus the D=8192 X2-corpus result
 * as the reference row. Broken decode here is an EXPECTED finding.
 *
 * Exit code is 0 regardless of rates. Writes results/x2-q-report.{json,md}.
 */

import {
  encodeConceptSetQ,
  decodeExplicationQ,
  validateExplication,
  canonicalJson,
  ALGORITHM_VERSION_Q,
  encoderContentHashQ,
} from '@jeswr/kernel-encoder';
import { fmt } from '../harness/common.js';
import { loadCorpus, slug, writeCorpusReport } from './corpus-common.js';

const DIMS = [512, 576] as const;

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
  console.log(`X2-q: decoding ${corpus.docs.length} authored concepts at D ∈ {${DIMS.join(', ')}} (UNGATED measurement)`);

  const perDim: Record<string, unknown> = {};
  const mdSections: string[] = [];

  for (const D of DIMS) {
    const { vectors } = encodeConceptSetQ(corpus.defs, { params: { D } });

    const runCondition = (
      condition: 'minimal' | 'full-corpus',
      lexiconFor: (doc: (typeof corpus.docs)[number]) => Map<string, Float64Array>,
    ): Row[] => {
      const rows: Row[] = [];
      const t0 = Date.now();
      for (const doc of corpus.docs) {
        const stats = validateExplication(doc.explication);
        const t = Date.now();
        const r = decodeExplicationQ(vectors.get(doc.id)!, { params: { D }, concepts: lexiconFor(doc) });
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
            : `decode failed: ${r.validationError ?? 'incomplete AST'}`;
        }
        rows.push(row);
        if (rows.length % 10 === 0) {
          console.log(`  [D=${D} ${condition}] ${rows.length}/${corpus.docs.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
        }
      }
      return rows;
    };

    console.log(`D=${D}, condition 1/2: minimal lexicon`);
    const minimal = runCondition('minimal', (doc) => new Map(doc.references.map((id) => [id, vectors.get(id)!])));
    console.log(`D=${D}, condition 2/2: full-corpus lexicon`);
    const fullCorpus = runCondition('full-corpus', (doc) => new Map([...vectors].filter(([id]) => id !== doc.id)));

    const analyse = (rows: Row[]) => {
      const exact = rows.filter((r) => r.exact).length;
      const ok = rows.filter((r) => r.ok).length;
      // exact rate by (depth, clause-count) cell — where decode dies is the
      // informative measurement at this D.
      const byCell: Record<string, { exact: number; total: number }> = {};
      for (const r of rows) {
        const key = `d${r.maxDepth}xc${r.clauseCount}`;
        byCell[key] = byCell[key] ?? { exact: 0, total: 0 };
        byCell[key].total++;
        if (r.exact) byCell[key].exact++;
      }
      const byDepth: Record<string, { exact: number; total: number }> = {};
      for (const r of rows) {
        const key = String(r.maxDepth);
        byDepth[key] = byDepth[key] ?? { exact: 0, total: 0 };
        byDepth[key].total++;
        if (r.exact) byDepth[key].exact++;
      }
      return { exact, ok, total: rows.length, byCell, byDepth, nonExact: rows.filter((r) => !r.exact) };
    };
    const aMin = analyse(minimal);
    const aFull = analyse(fullCorpus);
    perDim[String(D)] = {
      encoderContentHashQ: encoderContentHashQ({ D }),
      minimal: { exact: aMin.exact, ok: aMin.ok, total: aMin.total, byDepth: aMin.byDepth, byCell: aMin.byCell, rows: minimal },
      fullCorpus: { exact: aFull.exact, ok: aFull.ok, total: aFull.total, byDepth: aFull.byDepth, byCell: aFull.byCell, rows: fullCorpus },
    };

    const depthTable = (a: ReturnType<typeof analyse>): string[] =>
      Object.entries(a.byDepth)
        .sort(([x], [y]) => Number(x) - Number(y))
        .map(([d, c]) => `| ${d} | ${c.exact}/${c.total} |`);
    mdSections.push(
      `## D = ${D}`,
      '',
      `encoder content-hash: \`${encoderContentHashQ({ D })}\``,
      '',
      `- minimal lexicon: **${aMin.exact}/${aMin.total} exact** (${aMin.ok} validated)`,
      `- full-corpus lexicon: **${aFull.exact}/${aFull.total} exact** (${aFull.ok} validated)`,
      '',
      'Exact-recovery rate by authored max depth (minimal | full-corpus):',
      '',
      '| depth | minimal exact/total |',
      '|---|---|',
      ...depthTable(aMin),
      '',
      '| depth | full-corpus exact/total |',
      '|---|---|',
      ...depthTable(aFull),
      '',
      ...(aMin.nonExact.length > 0
        ? [
            `<details><summary>Non-exact under minimal lexicon (${aMin.nonExact.length})</summary>`,
            '',
            ...aMin.nonExact.slice(0, 60).map((r) => `- \`${slug(r.id)}\` (depth ${r.maxDepth}, ${r.clauseCount} clauses): ${r.failure}`),
            '',
            '</details>',
            '',
          ]
        : []),
    );
    console.log(`X2-q D=${D}: minimal ${aMin.exact}/${aMin.total} exact, full-corpus ${aFull.exact}/${aFull.total} exact`);
  }

  const json = {
    date: new Date().toISOString(),
    suite: 'X2-q: decode reality check at toy-native D (UNGATED measurement; pre-registration scopes toy-native away from the capacity/decode claim)',
    algorithmVersion: ALGORITHM_VERSION_Q,
    corpusManifestSha256: corpus.manifestSha256,
    corpusContentHash: corpus.corpusContentHash,
    gate: 'NONE — measurement only. Reference: X2-corpus at D=8192 (kot-enc-B/1) is 54/54 exact under both lexicon conditions (results/x2-kernel-v0-report.md).',
    decoderDefaults: '3 refinement passes, default thetaAbs = 5/sqrt(D)',
    perDim,
  };
  const md = [
    '# X2-q — decode reality check at toy-native D (kot-enc-Bq/1; UNGATED)',
    '',
    `date: ${json.date}`,
    `corpus: kernel-v0 — ${corpus.docs.length} concepts, content-hash \`${corpus.corpusContentHash}\``,
    '',
    '**No gate.** The capacity arithmetic (DCV §7.2) places robust full decode at',
    'D ≈ 4k-20k for the capped structure budget; at D = 512-576 the quasi-orthogonal',
    'crosstalk floor (~1/sqrt(D) per sibling term, QCERT report) makes deep exact',
    'recovery impossible by design. The numbers below quantify what survives.',
    `Reference row: D=8192 exact codebook achieves 54/54 + 54/54 (X2-corpus).`,
    '',
    ...mdSections,
    '> Protocol identical to X2-corpus: exact = canonical-JSON equality; minimal',
    '> lexicon = referenced ids only; full-corpus = all 53 others as cleanup',
    '> candidates. Decoder thresholds are heuristics, not part of the encoder pin.',
  ].join('\n');
  writeCorpusReport('x2-q-report', json, md);
  console.log('X2-q done (ungated).');
}

main();
