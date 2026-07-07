/**
 * E5 item construction + THE pre-registration manifest (README O3/O5;
 * docs/poc-design.md E5 rev 2; bead kernel-of-truth-c24).
 *
 * Consumes inputs/e5-concepts.json + E4's hash-published gloss set
 * (fail-closed pin) and emits:
 *
 *   inputs/e5-items.json     — training items (styles 0-3, seen concepts,
 *                              seeded 10% val flags), seen validity items
 *                              (style 4, 5-way), nonce items (styles 0-4,
 *                              5-way) with seeded distractor assignments.
 *   inputs/e5-manifest.json  — pins, task/adapter/training spec, and the
 *                              pre-registered statistics block the runner
 *                              quotes VERBATIM in its verdict.
 *
 * Zero-exposure guards (README O3) are asserted here mechanically and fail
 * closed; the prep tests re-assert them over the committed artifacts and the
 * runner re-asserts them at load.
 */

import {
  EVAL_STYLE,
  N_CANDIDATES,
  N_SEEDS,
  PINNED_B8192_HASH,
  PINNED_GLOSS_HASH,
  TRAIN_STYLES,
  VAL_FRACTION,
  isMain,
  loadGlosses,
  readInput,
  seededSample,
  sha256File,
  slugOf,
  writeInput,
} from './common.js';
import type { E5Concepts } from './selectConcepts.js';
import { join } from 'node:path';
import { INPUTS_DIR, D_MODEL } from './common.js';

export interface TrainItem {
  concept: string;
  row: number;
  style: number;
  gloss: string;
  val: boolean;
}

export interface EvalItem {
  concept: string;
  row: number;
  style: number;
  /** Candidate glosses; index 0 is the true gloss (scoring is order-free). */
  candidates: { concept: string; gloss: string }[];
  candLabel: string;
}

function main(): void {
  const concepts = readInput<E5Concepts>('e5-concepts.json');
  if (concepts.artifact !== 'e5-concepts') throw new Error('ERR_ARTIFACT: e5-concepts.json');
  const glosses = loadGlosses(); // fail-closed gloss pin (MAJOR 6, inherited)

  const rowOf = new Map(concepts.ids.map((id, i) => [id, i]));
  const seenIds = concepts.ids.filter((_, i) => concepts.roles[i] !== 'nonce');
  const nonceIds = concepts.ids.filter((_, i) => concepts.roles[i] === 'nonce');

  const glossOf = (id: string, style: number): string => {
    const g = glosses.get(id)?.[style];
    if (g === undefined) throw new Error(`ERR_GLOSS: missing gloss ${id} style ${style}`);
    return g;
  };

  // ---- training corpus: seen concepts x styles 0-3 -------------------------
  const training: TrainItem[] = [];
  for (const id of seenIds) {
    for (const style of TRAIN_STYLES) {
      training.push({ concept: id, row: rowOf.get(id)!, style, gloss: glossOf(id, style), val: false });
    }
  }
  const nVal = Math.round(training.length * VAL_FRACTION);
  const valIdx = seededSample(
    'e5/valsplit',
    training.map((_, i) => i),
    nVal,
  );
  for (const i of valIdx) training[i]!.val = true;

  // ---- seen validity items: style 4, 5-way among seen concepts -------------
  const seenEval: EvalItem[] = seenIds.map((id) => {
    const candLabel = `e5/seencand/${slugOf(id)}`;
    const others = seededSample(candLabel, seenIds.filter((x) => x !== id), N_CANDIDATES - 1);
    return {
      concept: id,
      row: rowOf.get(id)!,
      style: EVAL_STYLE,
      candidates: [
        { concept: id, gloss: glossOf(id, EVAL_STYLE) },
        ...others.map((o) => ({ concept: o, gloss: glossOf(o, EVAL_STYLE) })),
      ],
      candLabel,
    };
  });

  // ---- nonce items (PRIMARY): styles 0-4, 5-way among nonces ---------------
  const nonceEval: EvalItem[] = [];
  for (const id of nonceIds) {
    for (let style = 0; style <= EVAL_STYLE; style++) {
      const candLabel = `e5/noncecand/${slugOf(id)}/${style}`;
      const others = seededSample(candLabel, nonceIds.filter((x) => x !== id), N_CANDIDATES - 1);
      nonceEval.push({
        concept: id,
        row: rowOf.get(id)!,
        style,
        candidates: [
          { concept: id, gloss: glossOf(id, style) },
          ...others.map((o) => ({ concept: o, gloss: glossOf(o, style) })),
        ],
        candLabel,
      });
    }
  }

  // ---- zero-exposure guards (README O3) — FAIL CLOSED ----------------------
  const nonceSet = new Set(nonceIds);
  for (const t of training) {
    if (nonceSet.has(t.concept)) throw new Error(`ERR_LEAK: nonce ${t.concept} in training`);
    if (t.style === EVAL_STYLE) throw new Error('ERR_LEAK: eval style in training');
  }
  // Pinned guard directions (README O3): a nonce gloss may NEVER appear in
  // training (equality or as a substring of a training gloss). The reverse —
  // a short seen-concept gloss occurring as a clause INSIDE a longer nonce
  // gloss — is compositional realizer sharing (identical across arms, and
  // exactly what the compositional split measures); it is COUNTED and
  // reported, not forbidden.
  const nonceGlossTexts: string[] = [];
  for (const id of nonceIds) for (let s = 0; s <= EVAL_STYLE; s++) nonceGlossTexts.push(glossOf(id, s));
  let trainInsideNonce = 0;
  for (const t of training) {
    for (const g of nonceGlossTexts) {
      if (t.gloss === g || t.gloss.includes(g)) {
        throw new Error(`ERR_LEAK: nonce gloss text appears in training (concept ${t.concept})`);
      }
      if (g.includes(t.gloss)) trainInsideNonce++;
    }
  }

  const itemsPath = writeInput('e5-items.json', {
    artifact: 'e5-items',
    date: new Date().toISOString(),
    glossHash: PINNED_GLOSS_HASH,
    counts: {
      training: training.length,
      trainingVal: training.filter((t) => t.val).length,
      seenEval: seenEval.length,
      nonceEval: nonceEval.length,
      nonces: nonceIds.length,
      candidatesPerItem: N_CANDIDATES,
      trainGlossInsideNonceGlossContainments: trainInsideNonce,
    },
    training,
    seenEval,
    nonceEval,
  });

  // ---- THE pre-registration manifest ---------------------------------------
  const vecManifestPath = join(INPUTS_DIR, 'vector-tables-manifest.json');
  writeInput('e5-manifest.json', {
    artifact: 'e5-manifest',
    date: new Date().toISOString(),
    spec: 'docs/poc-design.md E5 rev 2 (MINOR 23) + poc/e5/README.md pinned operationalisations O1-O6',
    specVerbatim:
      'E5 — adapter + shuffled-kernel control (3–6 GPU-h). Rev 2 (MINOR 23): n ≥ 20 nonce ' +
      'concepts; exact permutation test, α=0.05; scoring by a fixed non-LLM rubric (slot-filling ' +
      'accuracy against the nonce\'s explication) or a leak-checked judge (judge prompt contains ' +
      'no explications). Success: true kernel > shuffled kernel on nonce-concept usage.',
    pins: {
      encoderContentHash: PINNED_B8192_HASH,
      glossHash: PINNED_GLOSS_HASH,
      e4SyntheticsSha256: concepts.e4SyntheticsSha256,
      kernelV0: concepts.kernelV0,
      itemsSha256: sha256File(itemsPath),
      vectorTablesManifestSha256: sha256File(vecManifestPath),
    },
    model: {
      id: 'HuggingFaceTB/SmolLM2-135M',
      dModel: D_MODEL,
      frozen: 'ALL model parameters frozen (eval mode, no grad); the adapter is the only trainable component',
      precision: 'fp32 (TF32 matmul allowed, recorded in results)',
    },
    adapter: {
      form: 'single shared affine map y = W k + b, W in R^{576 x d_model}, b in R^{d_model}',
      init:
        'W ~ N(0, sigma^2) with sigma = std of the frozen embedding-matrix entries (measured at ' +
        'run time, recorded); b = mean embedding row; seeded per experiment seed, IDENTICAL ' +
        'across arms (Common rule 1 pairing)',
      injection:
        'one input-embedding position ([SLOT]) carries the adapter output; the concept surface ' +
        'form appears nowhere; no vocab surgery; the nonce token is never emitted',
    },
    frame: {
      prefix: 'The word',
      suffix: ' means:',
      candidatePrefix: ' ',
      bos: true,
      tokenCap: 192,
      note: 'tokens(prefix) ++ [SLOT] ++ tokens(suffix) ++ tokens(candidatePrefix + gloss); identical in training and eval, identical across arms',
    },
    training: {
      lossTokens: 'cross-entropy on the gloss tokens only',
      batch: 32,
      steps: 2000,
      warmupSteps: 100,
      schedule: 'linear warmup 100 steps then cosine decay to 0.1x',
      gradClip: 1.0,
      optimizer: 'AdamW, betas 0.9/0.999, eps 1e-8, weight decay 0',
      dataOrder: 'seeded shuffle per epoch, function of the seed index only (identical across arms)',
      lrRule:
        'Common rule 5: per-arm sweep on seed 0 only, lrs {3e-4, 1e-3, 3e-3} at half budget ' +
        '(1000 steps), best by val cross-entropy, then fixed for all 5 seeds of that arm',
      lrSweep: [3e-4, 1e-3, 3e-3],
      sweepSteps: 1000,
    },
    seeds: Array.from({ length: N_SEEDS }, (_, s) => s),
    arms: {
      trueKernel: 'row i -> kernel vector of concept i (inputs/vectors/kernel-jl576.f32)',
      shuffledKernel:
        'row i -> kernel[perm_s[i]], perm_s = seeded derangement of ALL 524 rows per ' +
        'vector-tables-manifest (same spectrum, assignment destroyed; Common rule 4)',
      randomVector: 'row i -> unit-norm i.i.d. Gaussian (DESCRIPTIVE ONLY; no inferential claim)',
    },
    scoring: {
      rubric:
        'FIXED NON-LLM RUBRIC (the spec\'s first option): candidate score = mean per-token ' +
        'log-probability of the candidate gloss tokens under the frozen model given the frame + ' +
        'injected embedding; prediction = argmax over the 5 candidates; exact float ties score ' +
        'as incorrect. "Slot-filling accuracy against the nonce\'s explication" = the definition ' +
        'slot must be filled with the realizer gloss of the nonce\'s OWN explication rather than ' +
        'a competing explication\'s gloss. No LLM judge exists anywhere in E5.',
      chance: 1 / N_CANDIDATES,
    },
    statistics: {
      primaryEndpoint:
        'nonce slot-filling accuracy, true-kernel vs shuffled-kernel: per nonce j, d_j = mean ' +
        'over the 5 paired seeds of (acc_true[s,j] - acc_shuffled[s,j]) over that nonce\'s 5 ' +
        'items; one-sided exact sign-flip permutation over the 24 nonce-level paired differences ' +
        '(statistic = sum_j d_j; full 2^24 enumeration, exact integer-lattice convolution; p ' +
        'includes the observed assignment), alpha = 0.05. Operationalises the spec\'s "n >= 20 ' +
        'nonce concepts; exact permutation test, alpha=0.05" with the nonce as the permutation ' +
        'unit. Pinned caveat: nonce-level differences share the 5 trained adapter pairs; the ' +
        'seed-level secondary treats the training run as the unit.',
      instrumentValidityGate:
        'the TRUE arm must beat chance on the SEEN validity items in >= 4 of 5 seeds (per-seed ' +
        'one-sided exact binomial vs 0.2 over 500 items, p < 0.05); otherwise the run is ' +
        'INSTRUMENT-INVALID (neither success nor null), no primary claim in either direction ' +
        '(the E1 step-0 lesson)',
      secondaryEndpoints: [
        'one-sided exact paired sign-flip over the 5 paired seed-mean nonce accuracies, true vs ' +
          'shuffled, Holm-corrected (m=1; min attainable p = 1/32)',
      ],
      descriptive: [
        'random-arm accuracies',
        'step-0 (untrained-adapter) accuracies for all arms',
        'shuffled/random seen-item accuracies',
        'per-item score margins',
        'compositional shared/novel nonce split (feature definition verbatim from poc/e4/harness/holdout.ts)',
        'per-seed and per-nonce tables',
      ],
      successCriterion:
        'SUCCESS (spec, verbatim): "true kernel > shuffled kernel on nonce-concept usage" = the ' +
        'primary test rejects at alpha=0.05 with positive mean difference AND the validity gate ' +
        'passed. Non-rejection with the gate passed = NULL (no TOST equivalence bound is ' +
        'pre-registered for E5). Gate failed = INSTRUMENT-INVALID.',
      noHotControlRule:
        'no shuffled-arm hot-control invalidation is pre-registered: an above-chance shuffled arm ' +
        'is legitimate here (frame/style regularities are shared by both arms); the contrast ' +
        'itself is the control',
      nonceExclusionRule: 'NONE: all 24 nonces enter the primary; no post-hoc exclusion of any kind',
    },
    scopeLimits:
      'README O6 / Common rule 6: single model, single basis, toy scale, realizer-English glosses, ' +
      'synthetic clean domain; a positive is an A2 statement only and does not establish code ' +
      'uniqueness, scale behaviour, or anything about A1',
  });
}

if (isMain(import.meta.url)) main();
