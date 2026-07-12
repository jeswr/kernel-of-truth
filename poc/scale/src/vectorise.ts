/**
 * SCALE-1 S0 stage 3 — deterministic bulk vectorisation, `kot-enc-import/0-poc`.
 *
 * WHY NOT construction B directly: the exact kot-enc-B/1 codebook is a CLOSED
 * 31-slot × 129-filler inventory over profile-1 explication ASTs; AxiomsOnly
 * WordNet records have no AST, arbitrary relation/target labels cannot get
 * mutually orthogonal Hadamard rows, and the imported graph is not a DAG
 * (design §6.1). Per design §6.3 bulk imports get a SEPARATE deterministic
 * vectoriser. This file is an exploratory PoC instantiation of §6.3 built on
 * the encoder package's DetStream (same SHA-256 determinism substrate as
 * kot-enc-B/1 and kot-enc-Bq/1). It is NOT a pinned encoder version.
 *
 * Construction (pinned in VECTORISER_SPEC, hash = vectoriserPin(D)):
 *   h0(c) = normalize( Σ_axioms 1.0·atom(`ax/<rel>/<target>`)      [sorted]
 *                    + 0.25·atom(`lexfile/<lexFile>`)
 *                    [+ 0.5·atom(`lemma/<l>`) in the *lex store only] )
 *   h1(c) = normalize( 1.0·h0(c)
 *                    + (1/√(1+degW)) Σ_within-subset relSign(rel) ⊙ h0(target) )
 *   one synchronous round; cycles/SCCs need no DAG (design §6.3 step 7).
 *   External (out-of-subset) targets contribute only their h0 joint atom.
 *
 * Stores produced (row order = URN-sorted concepts.jsonl; fp32-LE chunks of
 * 512 rows; canonical arithmetic is fp64 in-process — fp32 persistence is a
 * deployment cache, disclosed):
 *   canon8192            D=8192 canonical
 *   proj512 / proj576    X4 Achlioptas JL of canon8192 (labels jl/8192/<d>,
 *                        byte-identical stream to poc/harness/x4.ts)
 *   native512/native576  same construction natively at D∈{512,576}
 *   native512lex         native512 + optional lexical block (§6.2)
 *
 * FFT count: ZERO. This path uses elementwise sign binding, not circular
 * convolution — the §1.2 two-FFTs-per-structured-child cost model applies to
 * construction B explications, NOT to bulk import. Measured cost here is
 * SHA-256 atom expansion + O(D) accumulates per axiom.
 *
 * Checkpointing: per-chunk .bin files with byte-size guards + sha256 manifest;
 * a re-run resumes at the first incomplete store/chunk. `--verify` recomputes
 * chunk 0 of every store and byte-compares against the manifest.
 */

import { join } from 'node:path';
import { createHash } from 'node:crypto';
import {
  CHUNK,
  chunkComplete,
  ensureDir,
  fillAtom,
  loadConcepts,
  loadRows,
  normalizeInPlace,
  nowMs,
  outDirFor,
  readJson,
  relSigns,
  storeBytes,
  storeDir,
  targetN,
  vectoriserPin,
  writeChunk,
  writeJson,
  VECTORISER_SPEC,
  type LexRecord,
} from './common.js';
import { DetStream } from '@jeswr/kernel-encoder';

interface PreppedConcept {
  row: number;
  urn: string;
  tokens: { label: string; weight: number }[]; // sorted, without lemma block
  lemmaTokens: { label: string; weight: number }[];
  withinEdges: { rel: string; targetRow: number }[]; // sorted by (rel, targetRow)
  droppedWordPointers: number;
}

function prep(concepts: LexRecord[]): { prepped: PreppedConcept[]; droppedWordPointers: number } {
  const rowOf = new Map<string, number>();
  concepts.forEach((c, i) => rowOf.set(c.id, i));
  let dropped = 0;
  const prepped = concepts.map((c, i) => {
    const axTokens = c.axioms
      .map((a) => {
        if (a.srcWord !== undefined || a.tgtWord !== undefined) dropped++;
        return `ax/${a.rel}/${a.target}`;
      })
      .sort();
    const tokens = [
      ...axTokens.map((t) => ({ label: t, weight: 1.0 })),
      { label: `lexfile/${c.annotations.lexFile}`, weight: 0.25 },
    ];
    const lemmaTokens = [...c.annotations.lemmas]
      .sort()
      .map((l) => ({ label: `lemma/${l}`, weight: 0.5 }));
    const withinEdges = c.axioms
      .filter((a) => rowOf.has(a.target))
      .map((a) => ({ rel: a.rel, targetRow: rowOf.get(a.target)! }))
      .sort((x, y) => (x.rel < y.rel ? -1 : x.rel > y.rel ? 1 : x.targetRow - y.targetRow));
    return { row: i, urn: c.id, tokens, lemmaTokens, withinEdges, droppedWordPointers: 0 };
  });
  return { prepped, droppedWordPointers: dropped };
}

interface StoreTiming {
  store: string;
  D: number;
  wallSeconds: number;
  h0Seconds: number;
  roundSeconds: number;
  jlSeconds: number;
  atomsGenerated: number;
  sha256BlocksForAtoms: number;
  fftCount: 0;
  usPerConceptEncode: number;
  bytesOnDisk: number;
  chunkSha256: string[];
}

/** Deterministic Achlioptas JL matrix rows (X4 labels/consumption), as flat Float64Array(d*D). */
function jlMatrix(D: number, d: number): Float64Array {
  const stream = new DetStream(`jl/${D}/${d}`);
  const scale = 1 / Math.sqrt(d);
  const m = new Float64Array(d * D);
  for (let r = 0; r < d; r++) {
    for (let j = 0; j < D; j += 8) {
      const byte = stream.nextByte();
      for (let b = 0; b < 8 && j + b < D; b++) {
        m[r * D + j + b] = (byte >> b) & 1 ? scale : -scale;
      }
    }
  }
  return m;
}

interface RunSpec {
  store: string;
  D: number;
  lex?: boolean;
  projTargets?: { store: string; d: number }[];
}

const RUNS: RunSpec[] = [
  { store: 'canon8192', D: 8192, projTargets: [{ store: 'proj512', d: 512 }, { store: 'proj576', d: 576 }] },
  { store: 'native512', D: 512 },
  { store: 'native576', D: 576 },
  { store: 'native512lex', D: 512, lex: true },
];

function computeH0(prepped: PreppedConcept[], D: number, lex: boolean, counters: { atoms: number }): Float64Array {
  const n = prepped.length;
  const h0 = new Float64Array(n * D);
  const atomBuf = new Float64Array(D);
  for (const p of prepped) {
    const base = p.row * D;
    const toks = lex ? [...p.tokens, ...p.lemmaTokens] : p.tokens;
    for (const t of toks) {
      fillAtom(atomBuf, D, `scale-import/atom/${D}/${t.label}`);
      counters.atoms++;
      const w = t.weight;
      for (let j = 0; j < D; j++) h0[base + j]! += w * atomBuf[j]!;
    }
    const view = h0.subarray(base, base + D);
    normalizeInPlace(view);
  }
  return h0;
}

/** h1 for rows [r0, r1) given full h0; returns fp64 rows. */
function computeH1Rows(
  prepped: PreppedConcept[],
  h0: Float64Array,
  D: number,
  r0: number,
  r1: number,
  relSignCache: Map<string, Int8Array>,
): Float64Array {
  const out = new Float64Array((r1 - r0) * D);
  for (let i = r0; i < r1; i++) {
    const p = prepped[i]!;
    const dst = (i - r0) * D;
    const selfBase = i * D;
    for (let j = 0; j < D; j++) out[dst + j] = h0[selfBase + j]!; // selfWeight = 1.0
    const deg = p.withinEdges.length;
    if (deg > 0) {
      const w = 1 / Math.sqrt(1 + deg);
      for (const e of p.withinEdges) {
        let signs = relSignCache.get(e.rel);
        if (signs === undefined) {
          signs = relSigns(D, e.rel);
          relSignCache.set(e.rel, signs);
        }
        const nb = e.targetRow * D;
        for (let j = 0; j < D; j++) out[dst + j]! += w * signs[j]! * h0[nb + j]!;
      }
    }
    normalizeInPlace(out.subarray(dst, dst + D));
  }
  return out;
}

function sha256Of(f32: Float32Array): string {
  return createHash('sha256').update(Buffer.from(f32.buffer, f32.byteOffset, f32.byteLength)).digest('hex');
}

function runStore(
  n: number,
  prepped: PreppedConcept[],
  spec: RunSpec,
  verifyOnly: boolean,
): { timings: StoreTiming[]; verified?: Record<string, boolean> } {
  const D = spec.D;
  const dirs = [storeDir(n, spec.store), ...(spec.projTargets ?? []).map((t) => storeDir(n, t.store))];
  dirs.forEach(ensureDir);
  const nChunks = Math.ceil(n / CHUNK);

  const t0 = nowMs();
  const counters = { atoms: 0 };
  const h0 = computeH0(prepped, D, spec.lex ?? false, counters);
  const tH0 = nowMs();

  const jl = (spec.projTargets ?? []).map((t) => ({ ...t, m: jlMatrix(D, t.d) }));
  const relSignCache = new Map<string, Int8Array>();
  let roundMs = 0;
  let jlMs = 0;
  const shas: Record<string, string[]> = Object.fromEntries(
    [spec.store, ...(spec.projTargets ?? []).map((t) => t.store)].map((s) => [s, []]),
  );
  const verified: Record<string, boolean> = {};

  const chunkEnd = verifyOnly ? 1 : nChunks;
  for (let c = 0; c < chunkEnd; c++) {
    const r0 = c * CHUNK;
    const r1 = Math.min(n, r0 + CHUNK);
    const rows = r1 - r0;
    const allDone =
      chunkComplete(storeDir(n, spec.store), c, rows, D) &&
      (spec.projTargets ?? []).every((t) => chunkComplete(storeDir(n, t.store), c, rows, t.d));
    if (allDone && !verifyOnly) {
      // resume: recompute nothing; sha recorded from the bytes already on disk
      shas[spec.store]!.push(sha256Of(loadRows(n, spec.store, D, r0, r1)));
      for (const t of spec.projTargets ?? []) shas[t.store]!.push(sha256Of(loadRows(n, t.store, t.d, r0, r1)));
      continue;
    }
    const ta = nowMs();
    const h1 = computeH1Rows(prepped, h0, D, r0, r1, relSignCache);
    roundMs += nowMs() - ta;

    const f32 = new Float32Array(rows * D);
    for (let k = 0; k < rows * D; k++) f32[k] = h1[k]!;
    if (verifyOnly) {
      const manifest = readJson<{ stores: Record<string, { chunkSha256: string[] }> }>(
        join(outDirFor(n), 'vec', 'manifest.json'),
      );
      verified[spec.store] = manifest?.stores[spec.store]?.chunkSha256[0] === sha256Of(f32);
    } else {
      writeChunk(storeDir(n, spec.store), c, f32);
      shas[spec.store]!.push(sha256Of(f32));
    }

    const tb = nowMs();
    for (const t of jl) {
      const proj = new Float64Array(rows * t.d);
      for (let i = 0; i < rows; i++) {
        const vBase = i * D;
        for (let r = 0; r < t.d; r++) {
          let s = 0;
          const mBase = r * D;
          for (let j = 0; j < D; j++) s += t.m[mBase + j]! * h1[vBase + j]!;
          proj[i * t.d + r] = s;
        }
      }
      const pf32 = new Float32Array(rows * t.d);
      for (let k = 0; k < rows * t.d; k++) pf32[k] = proj[k]!;
      if (verifyOnly) {
        const manifest = readJson<{ stores: Record<string, { chunkSha256: string[] }> }>(
          join(outDirFor(n), 'vec', 'manifest.json'),
        );
        verified[t.store] = manifest?.stores[t.store]?.chunkSha256[0] === sha256Of(pf32);
      } else {
        writeChunk(storeDir(n, t.store), c, pf32);
        shas[t.store]!.push(sha256Of(pf32));
      }
    }
    jlMs += nowMs() - tb;
    if (c % 4 === 3 || c === chunkEnd - 1) {
      console.log(`  ${spec.store}: chunk ${c + 1}/${chunkEnd} (${((nowMs() - t0) / 1000).toFixed(1)}s)`);
    }
  }

  const wall = (nowMs() - t0) / 1000;
  const blocksPerAtom = Math.ceil(D / 8 / 32);
  const mkTiming = (store: string, d: number): StoreTiming => ({
    store,
    D: d,
    wallSeconds: wall,
    h0Seconds: (tH0 - t0) / 1000,
    roundSeconds: roundMs / 1000,
    jlSeconds: jlMs / 1000,
    atomsGenerated: counters.atoms,
    sha256BlocksForAtoms: counters.atoms * blocksPerAtom,
    fftCount: 0,
    usPerConceptEncode: (wall * 1e6) / n,
    bytesOnDisk: verifyOnly ? 0 : storeBytes(n, store),
    chunkSha256: shas[store] ?? [],
  });
  const timings = [mkTiming(spec.store, D), ...(spec.projTargets ?? []).map((t) => mkTiming(t.store, t.d))];
  return verifyOnly ? { timings, verified } : { timings };
}

function main(): void {
  const n = targetN();
  const verify = process.argv.includes('--verify');
  const concepts = loadConcepts(n);
  if (concepts.length !== n) throw new Error(`ERR_VEC_COUNT: concepts.jsonl has ${concepts.length} != ${n}`);
  const { prepped, droppedWordPointers } = prep(concepts);
  const withinEdgeTotal = prepped.reduce((a, p) => a + p.withinEdges.length, 0);
  const axiomTotal = prepped.reduce((a, p) => a + p.tokens.length - 1, 0);
  console.log(
    `vectorise: n=${n}, axioms=${axiomTotal}, within-subset edges=${withinEdgeTotal} ` +
      `(${((100 * withinEdgeTotal) / Math.max(1, axiomTotal)).toFixed(1)}% of axiom targets in-subset), verify=${verify}`,
  );

  const allTimings: StoreTiming[] = [];
  const verifyResults: Record<string, boolean> = {};
  for (const spec of RUNS) {
    console.log(`store ${spec.store} (D=${spec.D}${spec.lex ? ', +lexical block' : ''})...`);
    const res = runStore(n, prepped, spec, verify);
    allTimings.push(...res.timings);
    Object.assign(verifyResults, res.verified ?? {});
  }

  if (verify) {
    const ok = Object.values(verifyResults).every(Boolean);
    writeJson(join(outDirFor(n), 'vec', 'verify-report.json'), {
      determinismByteCheck: verifyResults,
      allByteIdentical: ok,
      note: 'chunk 0 of every store recomputed from scratch in this process and sha256-compared to the persisted manifest',
    });
    console.log('verify:', JSON.stringify(verifyResults), ok ? 'ALL BYTE-IDENTICAL' : 'MISMATCH');
    if (!ok) process.exitCode = 1;
    return;
  }

  const report = {
    stage: 'vectorise',
    epistemicStatus:
      'MEASURED costs of an EXPLORATORY §6.3 PoC vectoriser (kot-enc-import/0-poc). NOT construction B, NOT a pinned encoder version; numbers do not transfer to kot-enc-B/1. No feasibility conclusion.',
    vectoriser: VECTORISER_SPEC,
    pins: Object.fromEntries([512, 576, 8192].map((d) => [d, vectoriserPin(d)])),
    n,
    axiomTokens: axiomTotal,
    withinSubsetEdges: withinEdgeTotal,
    externalTargetShare: 1 - withinEdgeTotal / Math.max(1, axiomTotal),
    wordLevelPointersDropped: droppedWordPointers,
    discardedAxiomKinds: 'none — every axiom row becomes a token; word-level (srcWord/tgtWord) anchoring is dropped from the token label (disclosed, §6.3 step 9)',
    stores: Object.fromEntries(allTimings.map((t) => [t.store, t])),
  };
  writeJson(join(outDirFor(n), 'vec', 'manifest.json'), report);
  console.log(
    'vectorise done:',
    allTimings.map((t) => `${t.store} ${t.wallSeconds.toFixed(1)}s ${(t.bytesOnDisk / 1e6).toFixed(1)}MB`).join('; '),
  );
}

main();
