/**
 * X2 — decode depth (poc-design.md Phase X): exact-recovery rate by
 * (depth x clause-count) cell, n >= 30 per cell; synthetic cells cover the
 * shapes kernel v0 will occupy. Pre-registered success: 100% at depth <= 4.
 *
 * "depth" here is the requested clause-nesting depth of the generator's
 * spine; the report also records the measured structural depth (SPs inside
 * the deepest clause add one level). Exact recovery = canonical-JSON
 * equality of the decoded AST with the original.
 *
 * Checkpointed per cell.
 */

import {
  encodeExplication,
  decodeExplication,
  generateExplication,
  validateExplication,
  canonicalJson,
  encoderContentHash,
} from '@jeswr/kernel-encoder';
import {
  argValue,
  ensureDirs,
  fmt,
  loadCheckpoint,
  saveCheckpoint,
  writeReport,
} from './common.js';

interface CellResult {
  depth: number;
  topClauses: number;
  n: number;
  exact: number;
  okButWrong: number;
  failed: number;
  meanMinConfidence: number;
  meanMeasuredDepth: number;
  meanClauseNodes: number;
}

interface X2Checkpoint {
  nPerCell: number;
  cells: CellResult[];
}

const CHECKPOINT = 'x2-checkpoint.json';

function runCell(depth: number, topClauses: number, nPerCell: number): CellResult {
  let exact = 0;
  let okButWrong = 0;
  let failed = 0;
  let confSum = 0;
  let depthSum = 0;
  let clauseSum = 0;
  for (let i = 0; i < nPerCell; i++) {
    const ast = generateExplication({ seed: `x2/${depth}/${topClauses}/${i}`, topClauses, depth });
    const stats = validateExplication(ast);
    depthSum += stats.maxDepth;
    clauseSum += stats.clauseCount;
    const v = encodeExplication(ast);
    const r = decodeExplication(v);
    confSum += r.minConfidence;
    if (r.ok && canonicalJson(r.explication) === canonicalJson(ast)) exact++;
    else if (r.ok) okButWrong++;
    else failed++;
  }
  return {
    depth,
    topClauses,
    n: nPerCell,
    exact,
    okButWrong,
    failed,
    meanMinConfidence: confSum / nPerCell,
    meanMeasuredDepth: depthSum / nPerCell,
    meanClauseNodes: clauseSum / nPerCell,
  };
}

function main(): void {
  ensureDirs();
  const nPerCell = Number(argValue('--n') ?? 30);
  const depths = [1, 2, 3, 4, 5, 6];
  const clauseCounts = [1, 2, 4, 8];
  let ck = loadCheckpoint<X2Checkpoint>(CHECKPOINT);
  if (ck === null || ck.nPerCell !== nPerCell) ck = { nPerCell, cells: [] };
  const doneKey = new Set(ck.cells.map((c) => `${c.depth}/${c.topClauses}`));
  const t0 = Date.now();
  for (const depth of depths) {
    for (const tc of clauseCounts) {
      const key = `${depth}/${tc}`;
      if (doneKey.has(key)) continue;
      const cell = runCell(depth, tc, nPerCell);
      ck.cells.push(cell);
      saveCheckpoint(CHECKPOINT, ck);
      console.log(
        `cell depth=${depth} clauses=${tc}: exact ${cell.exact}/${cell.n} ` +
          `(measured depth ~${fmt(cell.meanMeasuredDepth, 1)}, ${((Date.now() - t0) / 1000).toFixed(0)}s elapsed)`,
      );
    }
  }
  // Success criterion: 100% exact at depth <= 4 (requested clause-nesting depth).
  const d4 = ck.cells.filter((c) => c.depth <= 4);
  const pass = d4.every((c) => c.exact === c.n);
  const json = {
    date: new Date().toISOString(),
    encoderContentHash: encoderContentHash(),
    nPerCell,
    criterion: '100% exact recovery at depth <= 4 (poc-design X2)',
    pass,
    cells: ck.cells,
  };
  const md = [
    '# X2 — decode recovery by (depth x clause-count) cell',
    '',
    `date: ${json.date}`,
    `encoder content-hash: \`${json.encoderContentHash}\``,
    `n per cell: ${nPerCell}; exact recovery = canonical-JSON equality; decoder defaults (3 refinement passes).`,
    '',
    `**Criterion (pre-registered): 100% at depth <= 4 -> ${pass ? 'PASS' : 'FAIL'}**`,
    '',
    '| depth (requested) | top clauses | exact | ok-but-wrong | failed | mean measured depth | mean clause nodes | mean min-confidence |',
    '|---|---|---|---|---|---|---|---|',
    ...ck.cells.map(
      (c) =>
        `| ${c.depth} | ${c.topClauses} | ${c.exact}/${c.n} | ${c.okButWrong} | ${c.failed} | ${fmt(c.meanMeasuredDepth, 1)} | ${fmt(c.meanClauseNodes, 1)} | ${fmt(c.meanMinConfidence, 3)} |`,
    ),
    '',
    '> Decoding is stated, per the construction, as recoverable GIVEN THE KERNEL',
    '> (codebook + lexicon as cleanup memory); depth beyond the SNR budget is',
    '> expected to degrade — that boundary is what this table maps.',
  ].join('\n');
  writeReport('x2-report', json, md);
  console.log(`X2 ${pass ? 'PASS' : 'FAIL'} (criterion: 100% exact at depth <= 4)`);
  process.exit(pass ? 0 : 1);
}

main();
