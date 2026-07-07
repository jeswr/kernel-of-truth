/**
 * X4-q — geometry preservation of the toy-native re-encode (kot-enc-Bq/1)
 * vs the JL-projection path, on the authored kernel-v0 corpus (bead
 * kernel-of-truth-5xo; the X4-analogue of the variant's pre-registration).
 *
 * The two pre-registered ways to get kernel geometry into a d-dimensional
 * model (poc-design Common rule 3 / architecture.md §1.3):
 *   (i)  toy-native — re-encode at D = d (THIS variant);
 *   (ii) projected  — fixed seeded JL matrix R^8192 -> R^d.
 * For each d ∈ {512, 576} this harness reports RDM Spearman over the 54
 * authored concepts between all three geometries:
 *   rho(8192, native-d)   — how much of the full-D geometry the native
 *                           re-encode preserves;
 *   rho(JL-d,  native-d)  — how similar the two injection paths are to each
 *                           other (what E1 sees if it swaps paths);
 *   rho(8192, JL-d)       — the JL distortion baseline (= X4-corpus numbers,
 *                           recomputed here as a consistency check).
 * Both matter for interpreting E1: if native-d and JL-d disagree, E1 results
 * under path (i) do not transfer to path (ii) claims and vice versa.
 *
 * JL projection copied VERBATIM from poc/src/x4-corpus.ts (pinned labels
 * jl/8192/512, jl/8192/576 — no new projections). Writes
 * results/x4-q-report.{json,md}.
 */

import {
  encodeConceptSet,
  encodeConceptSetQ,
  encoderContentHash,
  encoderContentHashQ,
  ALGORITHM_VERSION_Q,
  DetStream,
} from '@jeswr/kernel-encoder';
import { angle, cosine, fmt, spearman, summarise } from '../harness/common.js';
import { loadCorpus, slug, writeCorpusReport } from './corpus-common.js';

/** Deterministic Achlioptas-style sign JL matrix, rows generated on the fly. (= x4-corpus.ts / harness/x4.ts) */
function jlProject(vectors: readonly Float64Array[], D: number, d: number): Float64Array[] {
  const outs = vectors.map(() => new Float64Array(d));
  const stream = new DetStream(`jl/${D}/${d}`);
  const scale = 1 / Math.sqrt(d);
  const row = new Float64Array(D);
  for (let r = 0; r < d; r++) {
    // 1 sign bit per entry, 8 per stream byte — fixed consumption order.
    for (let j = 0; j < D; j += 8) {
      const byte = stream.nextByte();
      for (let b = 0; b < 8 && j + b < D; b++) {
        row[j + b] = (byte >> b) & 1 ? scale : -scale;
      }
    }
    for (const [k, v] of vectors.entries()) {
      let s = 0;
      for (let j = 0; j < D; j++) s += row[j]! * v[j]!;
      outs[k]![r] = s;
    }
  }
  return outs;
}

function rdm(vecs: readonly Float64Array[]): number[] {
  const out: number[] = [];
  for (let i = 0; i < vecs.length; i++) {
    for (let j = i + 1; j < vecs.length; j++) out.push(cosine(vecs[i]!, vecs[j]!));
  }
  return out;
}

function main(): void {
  const corpus = loadCorpus();
  const D = 8192;
  const targets = [512, 576] as const;
  console.log(`X4-q: ${corpus.docs.length} authored concepts; native re-encode vs JL at d ∈ {${targets.join(', ')}}`);

  const ids = corpus.docs.map((d) => d.id);
  const base = encodeConceptSet(corpus.defs).vectors;
  const baseVecs = ids.map((id) => base.get(id)!);
  const rdmBase = rdm(baseVecs);

  const perDim: Record<string, unknown> = {};
  const mdRows: string[] = [];
  for (const d of targets) {
    console.log(`  d=${d}: native re-encode`);
    const native = encodeConceptSetQ(corpus.defs, { params: { D: d } }).vectors;
    const nativeVecs = ids.map((id) => native.get(id)!);
    const rdmNative = rdm(nativeVecs);
    console.log(`  d=${d}: JL projection`);
    const jlVecs = jlProject(baseVecs, D, d);
    const rdmJl = rdm(jlVecs);

    const rhoBaseNative = spearman(rdmBase, rdmNative);
    const rhoJlNative = spearman(rdmJl, rdmNative);
    const rhoBaseJl = spearman(rdmBase, rdmJl);

    // Named nearest authored pair in each geometry (is the D=8192 minimum preserved?).
    const minPairOf = (vecs: readonly Float64Array[]): { a: string; b: string; angle: number } => {
      let min = { a: '', b: '', angle: Infinity };
      for (let i = 0; i < vecs.length; i++) {
        for (let j = i + 1; j < vecs.length; j++) {
          const a = angle(vecs[i]!, vecs[j]!);
          if (a < min.angle) min = { a: ids[i]!, b: ids[j]!, angle: a };
        }
      }
      return min;
    };
    const minNative = minPairOf(nativeVecs);
    const minJl = minPairOf(jlVecs);

    // Absolute cosine deviation of the native re-encode from full-D geometry.
    const absDev = rdmNative.map((c, k) => Math.abs(c - rdmBase[k]!));

    perDim[String(d)] = {
      encoderContentHashQ: encoderContentHashQ({ D: d }),
      rdmPairs: rdmBase.length,
      rhoBaseNative,
      rhoJlNative,
      rhoBaseJl,
      minPairNative: minNative,
      minPairJl: minJl,
      nativeAbsCosDeviation: summarise(absDev),
    };
    mdRows.push(
      `| ${d} | ${fmt(rhoBaseNative)} | ${fmt(rhoJlNative)} | ${fmt(rhoBaseJl)} | ` +
        `\`${slug(minNative.a)}\`<->\`${slug(minNative.b)}\` @ ${fmt(minNative.angle, 4)} | ` +
        `\`${slug(minJl.a)}\`<->\`${slug(minJl.b)}\` @ ${fmt(minJl.angle, 4)} |`,
    );
    console.log(
      `  d=${d}: rho(8192,native)=${fmt(rhoBaseNative)}  rho(JL,native)=${fmt(rhoJlNative)}  rho(8192,JL)=${fmt(rhoBaseJl)}`,
    );
  }

  const json = {
    date: new Date().toISOString(),
    suite: 'X4-q: RDM geometry — toy-native re-encode vs full-D vs fixed JL projection (kernel-v0)',
    algorithmVersion: ALGORITHM_VERSION_Q,
    baseEncoderContentHash: encoderContentHash(),
    corpusManifestSha256: corpus.manifestSha256,
    corpusContentHash: corpus.corpusContentHash,
    jlDerivation:
      'Achlioptas sign matrix, +/-1/sqrt(d), signs from SHA-256 stream label jl/<D>/<d> (det.ts DET_DOMAIN) — pinned labels reused from harness/x4.ts, no new projections',
    note:
      'The native re-encode is a DIFFERENT function of the AST, not a compression of the 8192-D vector: rho(8192, native) < 1 reflects codebook-level geometry change (quasi-orthogonal atoms + shared-D binding), while rho(8192, JL) reflects pure metric distortion. E1 interpretation: path-(i) results transfer to path-(ii) only to the extent rho(JL, native) is high.',
    perDim,
  };
  const md = [
    '# X4-q — native re-encode vs JL projection geometry (kot-enc-Bq/1)',
    '',
    `date: ${json.date}`,
    `corpus: kernel-v0 — ${corpus.docs.length} concepts, content-hash \`${corpus.corpusContentHash}\``,
    `base encoder (D=8192): \`${json.baseEncoderContentHash}\`; JL: ${json.jlDerivation}`,
    '',
    '| d | rho(8192, native) | rho(JL, native) | rho(8192, JL) | min pair (native) | min pair (JL) |',
    '|---|---|---|---|---|---|',
    ...mdRows,
    '',
    ...targets.map((d) => {
      const r = perDim[String(d)] as { nativeAbsCosDeviation: { median: number; p95: number; max: number } };
      return `- d=${d}: |cos(native) - cos(8192)| over 1431 pairs: median ${fmt(r.nativeAbsCosDeviation.median)}, p95 ${fmt(r.nativeAbsCosDeviation.p95)}, max ${fmt(r.nativeAbsCosDeviation.max)}`;
    }),
    '',
    `> ${json.note}`,
  ].join('\n');
  writeCorpusReport('x4-q-report', json, md);
  console.log('X4-q done.');
}

main();
