/**
 * E4 synthetic concept vocabulary (docs/poc-design.md E4 rev 2, panel O7:
 * "Concept vocabulary scaled to >=10^3 (synthetic capped explications ...
 * reused as emission targets)"; bead kernel-of-truth-73u).
 *
 * Generates N_SYNTH = 1000 valid capped explications through the encoder's
 * SEEDED generator (encoder/src/synth.ts, generator v2) and writes
 * inputs/synthetic-concepts.json. Every explication:
 *   - is produced from the DOCUMENTED seed scheme below (fully reproducible),
 *   - passes the encoder validation gates (validateExplication; the generator
 *     re-checks internally, we re-check here anyway — fail closed),
 *   - is deduplicated by canonical-JSON sha-256 (a duplicate triggers a
 *     deterministic labelled retry, recorded in the artifact).
 *
 * SEED SCHEME (pre-registered): for i in 0..999, seed = `e4/synth/<i>` (or
 * `e4/synth/<i>/retry<k>` after k dedup collisions); structural size is drawn
 * from DetStream(`e4/size/<i>`): topClauses = 1 + nextBelow(4) in 1..4,
 * depth = 1 + nextBelow(5) in 1..5. No conceptIds pool is passed: synthetic
 * explications are PURE PRIME structures. Rationale (recorded, load-bearing
 * for tier 2): a synthetic explication that referenced kernel-v0 concepts
 * would import corpus-attested material into "zero-exposure" targets and
 * couple synthetic glosses to authored-concept surface forms.
 *
 * The 54 authored kernel-v0 concepts are NOT duplicated here; consumers
 * combine data/kernel-v0 (pinned) + this file into the ~1054-concept vocab.
 */

import { canonicalJson, generateExplication, validateExplication, DetStream } from '@jeswr/kernel-encoder';
import type { Explication } from '@jeswr/kernel-encoder';
import {
  N_SYNTH,
  corpusPin,
  isMain,
  sha256Hex,
  synthId,
  writeInput,
} from './common.js';

export interface SynthRecord {
  readonly id: string;
  readonly seed: string;
  readonly topClauses: number;
  readonly depth: number;
  readonly retries: number;
  readonly astSha256: string;
  readonly explication: Explication;
}

/** Generate record i of the synthetic vocabulary (deterministic; exported for tests). */
export function generateSynthRecord(i: number, taken: Set<string>): SynthRecord {
  const size = new DetStream(`e4/size/${i}`);
  const topClauses = 1 + size.nextBelow(4);
  const depth = 1 + size.nextBelow(5);
  for (let attempt = 0; ; attempt++) {
    const seed = attempt === 0 ? `e4/synth/${i}` : `e4/synth/${i}/retry${attempt}`;
    const explication = generateExplication({ seed, topClauses, depth });
    // Fail closed on generator bugs (the generator validates internally; this
    // re-check keeps the gate at the artifact boundary — CLAUDE.md policy).
    validateExplication(explication);
    const astSha256 = sha256Hex(canonicalJson(explication));
    if (!taken.has(astSha256)) {
      taken.add(astSha256);
      return { id: synthId(i), seed, topClauses, depth, retries: attempt, astSha256, explication };
    }
  }
}

function main(): void {
  const taken = new Set<string>();
  const records: SynthRecord[] = [];
  let retried = 0;
  for (let i = 0; i < N_SYNTH; i++) {
    const rec = generateSynthRecord(i, taken);
    if (rec.retries > 0) retried++;
    records.push(rec);
    if (i % 200 === 199) console.log(`generated ${i + 1}/${N_SYNTH}`);
  }
  const depthHist: Record<string, number> = {};
  for (const r of records) {
    const k = `d${r.depth}/c${r.topClauses}`;
    depthHist[k] = (depthHist[k] ?? 0) + 1;
  }
  writeInput('synthetic-concepts.json', {
    artifact: 'e4-synthetic-concepts',
    date: new Date().toISOString(),
    generator: 'encoder synth.ts v2 (see GENERATOR VERSION note there)',
    seedScheme:
      'seed = e4/synth/<i> (+ /retry<k> on canonical-AST dedup collision); ' +
      'topClauses = 1 + DetStream(e4/size/<i>).nextBelow(4); depth = 1 + nextBelow(5); ' +
      'no conceptIds pool (pure prime structures — see file header rationale)',
    count: records.length,
    dedupRetriedItems: retried,
    sizeHistogram: depthHist,
    kernelV0: corpusPin(),
    note:
      'the 54 authored kernel-v0 concepts are combined with this file by consumers; ' +
      'total E4 concept vocabulary = 54 + 1000 = 1054',
    records,
  });
}

if (isMain(import.meta.url)) main();
