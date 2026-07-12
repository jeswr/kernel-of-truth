/**
 * SCALE-1 S0 stage 1 — INGEST a principled ~10k WordNet 3.1 subset.
 *
 * SELECTION RULE (disclosed, deterministic, re-runnable):
 *   Rank every WordNet 3.1 synset by its summed SemCor sense tag count from
 *   the source `index.sense` file (4th field, tag_cnt, summed over all sense
 *   keys mapping to the synset). Take the top N by (tag_cnt DESC, urn ASC).
 *   Ties at the cut boundary are resolved purely lexicographically by URN, so
 *   the subset is a pure function of the pinned source tarball + N.
 *
 * WHY THIS RULE: "top-frequency / core-coverage" per the build brief — SemCor
 * tag counts are the only *source-provided* frequency signal inside the
 * pinned WordNet distribution (no external corpus dependency). [STIPULATED]
 * Known bias: SemCor is a 1990s balanced corpus; the subset over-represents
 * common nouns/verbs and under-represents technical vocabulary. Disclosed,
 * not corrected.
 *
 * Output: out/n<N>/concepts.jsonl (kot-lex/1 records, URN-sorted) +
 *         out/n<N>/ingest-report.json (rule, counts, boundary, pos mix).
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import {
  WN_DIR,
  ensureDir,
  loadAllSynsets,
  nowMs,
  outDirFor,
  targetN,
  writeJson,
} from './common.js';

const SS_TYPE_TO_URN_POS: Record<string, string> = {
  '1': 'n',
  '2': 'v',
  '3': 'a',
  '4': 'r',
  '5': 'a', // adjective satellites share data.adj offsets → a- URNs
};

function main(): void {
  const n = targetN();
  const t0 = nowMs();
  const outDir = outDirFor(n);
  ensureDir(outDir);

  // 1. Sum tag counts per synset URN from index.sense.
  const senseIndex = readFileSync(join(WN_DIR, 'source', 'dict', 'index.sense'), 'utf8');
  const tagCnt = new Map<string, number>();
  let senseLines = 0;
  for (const line of senseIndex.split('\n')) {
    if (line.length === 0) continue;
    senseLines++;
    const parts = line.split(' ');
    if (parts.length < 4) continue;
    const key = parts[0]!;
    const pct = key.indexOf('%');
    const ssType = key[pct + 1]!;
    const pos = SS_TYPE_TO_URN_POS[ssType];
    if (pos === undefined) throw new Error(`ERR_INGEST_SSTYPE: unknown ss_type in sense key ${key}`);
    const urn = `urn:lexical-wn31:${pos}-${parts[1]!}`;
    const cnt = Number(parts[3]!);
    if (!Number.isFinite(cnt)) throw new Error(`ERR_INGEST_TAGCNT: ${line}`);
    tagCnt.set(urn, (tagCnt.get(urn) ?? 0) + cnt);
  }

  // 2. Load full synset store; verify every sense-index URN resolves.
  const all = loadAllSynsets();
  let unresolved = 0;
  for (const urn of tagCnt.keys()) if (!all.has(urn)) unresolved++;
  if (unresolved > 0) {
    // Fail closed: the selection rule must be a pure function of the pinned extraction.
    throw new Error(`ERR_INGEST_UNRESOLVED: ${unresolved} index.sense synsets missing from lexical-wn31 JSONL`);
  }

  // 3. Rank and cut.
  const ranked = [...all.keys()]
    .map((urn) => ({ urn, cnt: tagCnt.get(urn) ?? 0 }))
    .sort((a, b) => (b.cnt - a.cnt) || (a.urn < b.urn ? -1 : a.urn > b.urn ? 1 : 0));
  if (ranked.length < n) throw new Error(`ERR_INGEST_TOO_FEW: ${ranked.length} < ${n}`);
  const selected = ranked.slice(0, n);
  const boundary = selected[n - 1]!;
  const nonzero = ranked.filter((r) => r.cnt > 0).length;

  // 4. Write concepts.jsonl URN-sorted (byte-deterministic output order).
  const urns = selected.map((s) => s.urn).sort();
  const lines = urns.map((u) => JSON.stringify(all.get(u)!));
  writeFileSync(join(outDir, 'concepts.jsonl'), lines.join('\n') + '\n');

  // 5. Report.
  const posMix: Record<string, number> = {};
  const ssMix: Record<string, number> = {};
  const lexFileMix: Record<string, number> = {};
  let zeroCnt = 0;
  let axiomTotal = 0;
  for (const u of urns) {
    const r = all.get(u)!;
    posMix[r.pos] = (posMix[r.pos] ?? 0) + 1;
    ssMix[r.ssType] = (ssMix[r.ssType] ?? 0) + 1;
    lexFileMix[r.annotations.lexFile] = (lexFileMix[r.annotations.lexFile] ?? 0) + 1;
    if ((tagCnt.get(u) ?? 0) === 0) zeroCnt++;
    axiomTotal += r.axioms.length;
  }
  const report = {
    stage: 'ingest',
    epistemicStatus: 'MEASURED (mechanical counts) over a STIPULATED selection rule; exploratory S0 pilot, no feasibility conclusion',
    selectionRule:
      'top-N WordNet 3.1 synsets by summed SemCor tag_cnt from source index.sense; ties (tag_cnt, then URN ASC); pure function of pinned source + N',
    selectionBias:
      'SemCor-derived frequency: over-represents 1990s balanced-corpus common vocabulary; under-represents technical/tail senses. Disclosed, not corrected.',
    n,
    totalSynsets: all.size,
    senseIndexLines: senseLines,
    synsetsWithNonzeroTagCnt: nonzero,
    selectedWithZeroTagCnt: zeroCnt,
    boundaryTagCnt: boundary.cnt,
    boundaryUrn: boundary.urn,
    posMix,
    ssTypeMix: ssMix,
    lexFileMixTop: Object.fromEntries(
      Object.entries(lexFileMix).sort((a, b) => b[1] - a[1]).slice(0, 20),
    ),
    axiomTotal,
    axiomsPerConceptMean: axiomTotal / n,
    wallSeconds: (nowMs() - t0) / 1000,
  };
  writeJson(join(outDir, 'ingest-report.json'), report);
  console.log(
    `ingest: n=${n} of ${all.size} synsets; nonzero-tagcnt pool=${nonzero}; boundary tag_cnt=${boundary.cnt}; ` +
      `axioms=${axiomTotal} (${(axiomTotal / n).toFixed(2)}/concept); ${report.wallSeconds.toFixed(1)}s`,
  );
}

main();
