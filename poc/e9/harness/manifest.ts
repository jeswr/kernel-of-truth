/**
 * E9-defl pre-registration manifest (poc/e9/README.md; bead
 * kernel-of-truth-xj2) — THE artifact the runner quotes verbatim. Pins every
 * consumed file (E5 inputs READ-ONLY + the new deflationary table) by sha-256
 * and freezes the statistics/outcome strings.
 */

import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import {
  D_MODEL,
  E5_INPUTS_DIR,
  INPUTS_DIR,
  N_SEEDS,
  PINNED_B8192_HASH,
  REPO_DIR,
  isMain,
  readE5Input,
  sha256File,
  writeInput,
} from './common.js';

/** The committed E5 run this experiment compares drift against (descriptive). */
const E5_RUN_DIR = join(REPO_DIR, 'poc', 'e5', 'results-incoming', '20260707-140918-modal');

function main(): void {
  const e5Manifest = readE5Input<Record<string, any>>('e5-manifest.json');

  // Descriptive drift reference: per arm-seed accuracies of the committed E5
  // run (a repo fact, staged as an input so the runner can report drift).
  const e5Results = JSON.parse(
    readFileSync(join(E5_RUN_DIR, 'results-e5.json'), 'utf8'),
  ) as Record<string, any>;
  const e5Summary: Record<string, { nonceAcc: number; seenAcc: number }> = {};
  for (const [key, v] of Object.entries(e5Results['armSeed'] as Record<string, any>)) {
    if (key.startsWith('true-') || key.startsWith('shuffled-')) {
      e5Summary[key] = { nonceAcc: v['nonceAcc'], seenAcc: v['seenAcc'] };
    }
  }
  writeInput('e5-committed-summary.json', {
    artifact: 'e9-e5-committed-summary',
    source: 'poc/e5/results-incoming/20260707-140918-modal/results-e5.json (committed)',
    outcome: e5Results['outcome'],
    armSeed: e5Summary,
  });

  writeInput('e9-manifest.json', {
    artifact: 'e9-manifest',
    date: new Date().toISOString(),
    spec:
      'poc/e9/README.md (NEW pre-registration, 2026-07-07, coordinator-directed): deflationary ' +
      'control kernel on the E5 instrument. NOT poc-design.md E9 (decode-verify vs RAG, phase 2), ' +
      'which remains pre-registered and untouched.',
    question:
      'Is the kernel\'s signal specifically the semantic content of the explications, or would ' +
      'ANY consistent structured deterministic vector set do?',
    deflationPrinciple:
      'The kernel machinery\'s marginal value over its own deflation is measured, never asserted. ' +
      '(docs/poc-design.md E9 rev 3 sentence; notes/panel-kernel-design-review.md §3.1)',
    pins: {
      encoderContentHash: PINNED_B8192_HASH,
      e5ManifestSha256: sha256File(join(E5_INPUTS_DIR, 'e5-manifest.json')),
      e5ItemsSha256: sha256File(join(E5_INPUTS_DIR, 'e5-items.json')),
      e5ConceptsSha256: sha256File(join(E5_INPUTS_DIR, 'e5-concepts.json')),
      e5VectorTablesManifestSha256: sha256File(join(E5_INPUTS_DIR, 'vector-tables-manifest.json')),
      e5KernelF32Sha256: sha256File(join(E5_INPUTS_DIR, 'vectors', `kernel-jl${D_MODEL}.f32`)),
      deflConceptsSha256: sha256File(join(INPUTS_DIR, 'defl-concepts.json')),
      deflTablesManifestSha256: sha256File(join(INPUTS_DIR, 'defl-tables-manifest.json')),
      deflF32Sha256: sha256File(join(INPUTS_DIR, 'vectors', `defl-jl${D_MODEL}.f32`)),
      e5CommittedSummarySha256: sha256File(join(INPUTS_DIR, 'e5-committed-summary.json')),
      glossHash: e5Manifest['pins']['glossHash'],
    },
    instrument:
      'poc/e5 byte-identical (J4): same frozen SmolLM2-135M, adapter form/init/budget/LR rule, ' +
      'training/val/seen-validity/nonce items, glosses, 5 paired seeds, scoring rubric. poc/e5 ' +
      'runner code imported READ-ONLY (the poc/e4-reuses-stats_e1 precedent).',
    model: e5Manifest['model'],
    adapter: e5Manifest['adapter'],
    frame: e5Manifest['frame'],
    training: e5Manifest['training'],
    scoring: e5Manifest['scoring'],
    seeds: Array.from({ length: N_SEEDS }, (_, s) => s),
    arms: {
      trueKernel: 'row i -> E5 kernel vector of concept i (poc/e5 table, sha-pinned)',
      shuffledKernel: 'row i -> E5 kernel[perm_s[i]] (poc/e5 derangements, per seed)',
      deflKernel:
        'row i -> vector of the structure-matched semantically-scrambled explication for ' +
        'concept i (inputs/vectors/defl-jl576.f32; construction pinned in README + ' +
        'defl-concepts.json; same table for all seeds)',
      note: 'E5\'s random arm dropped (J5); true/shuffled re-run fresh alongside defl in ONE run (J6)',
    },
    statistics: {
      instrumentValidityGate:
        'the TRUE arm must beat chance on the SEEN validity items in >= 4 of 5 seeds (per-seed ' +
        'one-sided exact binomial vs 0.2 over 500 items, p < 0.05); otherwise the run is ' +
        'INSTRUMENT-INVALID (neither success nor null), no primary claim in either direction',
      primaryEndpoint:
        'nonce slot-filling accuracy, true-kernel vs defl-kernel: per nonce j, d_j = mean over ' +
        'the 5 paired seeds of (acc_true[s,j] - acc_defl[s,j]) over that nonce\'s 5 items; ' +
        'one-sided exact sign-flip permutation over the 24 nonce-level paired differences ' +
        '(statistic = sum_j d_j; full 2^24 enumeration, exact integer-lattice convolution; p ' +
        'includes the observed assignment), alpha = 0.05. This is the marginal value of kernel ' +
        'content over its structural deflation, measured. Pinned caveat: nonce-level differences ' +
        'share the 5 trained adapter pairs; S2 treats the training run as the unit.',
      secondaryEndpoints: [
        'S1: defl-kernel vs shuffled-kernel, same nonce-level one-sided test (defl > shuffled) — ' +
          'does the structural channel carry ANY transfer? Holm-corrected, m=2',
        'S2: seed-level one-sided exact paired sign-flip over the 5 per-seed mean nonce-accuracy ' +
          'differences, true vs defl (min attainable p = 1/32), Holm-corrected, m=2',
      ],
      outcomes:
        'gate failed => INSTRUMENT-INVALID; primary rejects => PASS (marginal value of content ' +
        'shown on this instrument); primary non-reject AND S1 rejects => DEFLATED (a ' +
        'semantics-scrambled structured code reproduces the transfer; every external quote of ' +
        'E5 must carry this); primary non-reject AND S1 non-reject => AMBIGUOUS-NULL (no ' +
        'measurable separation; power follow-up filed). All reported verbatim with full tables.',
      descriptive: [
        'recovered fraction (defl - shuffled)/(true - shuffled), per seed and pooled',
        'drift of rerun true/shuffled numbers vs poc/e5 committed run (replication datum)',
        'defl seen-validity accuracy',
        'compositional shared/novel nonce splits',
        'per-nonce and per-seed tables; margins; step-0 accuracies',
      ],
      inheritedPins:
        'no nonce exclusions; no post-hoc arms; exact float ties score as incorrect (E5 pins)',
    },
    scopeLimits:
      'poc/e5 README O6 verbatim, plus: a PASS shows content-specificity relative to THIS ' +
      'deflation (shape-matched scrambled explications); it does not exclude every conceivable ' +
      'non-semantic channel and does not upgrade any A1 claim.',
  });
}

if (isMain(import.meta.url)) main();
