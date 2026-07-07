/**
 * E4 two-tier holdout + compositional split + statistical pre-registration
 * (docs/poc-design.md E4 rev 2, MAJOR 7 / BLOCKER 3; bead kernel-of-truth-73u).
 *
 * Emits inputs/holdout-manifest.json — THE pre-registration artifact tying
 * together, before any training run:
 *   - tier-2: 10 concepts fully excluded from ALL training text (drawn from
 *     the SYNTHETIC set only, so the E1 corpus is untouched: synthetic tokens
 *     never occur in TinyStories, and the emission builder refuses to emit
 *     them anywhere);
 *   - tier-1: 20% of the remaining vocabulary (stratified authored/synthetic
 *     by proportion), held out of emission supervision; their tokens still
 *     appear in training text (authored: E1 corpus substitution; all tier-1:
 *     meaning-free exposure lines — see exposure policy below);
 *   - a seeded eval-gloss split for TRAINING concepts (1 of 5 variants held
 *     out as the seen-concept eval item);
 *   - the compositional split labels (shares-structure-with-seen vs not),
 *     computed from explication feature overlap as defined below;
 *   - the exact statistical test parameters (candidate set size, chance
 *     rates, Fisher/permutation spec, control-floor check).
 *
 * All draws are DetStream-labelled (documented inline) and reproducible.
 */

import { DetStream } from '@jeswr/kernel-encoder';
import type { Clause, Explication, Filler, OpArg } from '@jeswr/kernel-encoder';
import {
  N_GLOSS_VARIANTS,
  N_SEEDS,
  TIER1_FRACTION,
  TIER2_SIZE,
  corpusPin,
  isMain,
  loadKernelV0,
  readInput,
  sha256File,
  slugOf,
  writeInput,
} from './common.js';
import { join } from 'node:path';
import { INPUTS_DIR } from './common.js';
import type { SynthRecord } from './synthVocab.js';

// ---------------------------------------------------------------------------
// Compositional-split features (pre-registered definition).
//
// A concept's STRUCTURE FEATURE SET is the set of depth-limited clause
// skeletons over every clause node in its explication tree (including
// embedded clauses, quote bodies and restricting clauses):
//   skel(pred clause, d) = P(pred | role:tag, ...) with roles sorted; tag is
//     the filler kind (sp/ref/prime/concept/quote/temporal), except clause
//     fillers, which recurse while d > 0 and are 'cl' at d = 0;
//   skel(op clause, d)   = O(op | argtag, ...) with clause args recursing.
// Depth limit d = 1 (a clause signature sees its children's shapes but not
// grandchildren's).
//
// A held-out concept SHARES STRUCTURE with the seen set iff EVERY feature in
// its set occurs in the union of the training concepts' feature sets; the
// continuous coverage fraction is reported alongside. This is the split the
// E4 report must break accuracy down by (the compositional-generalisation
// claim Palatucci-2009/DeViSE-style zero-shot does not test).
// ---------------------------------------------------------------------------

function fillerTag(f: Filler, d: number): string {
  switch (f.kind) {
    case 'sp':
      return 'sp';
    case 'ref':
      return 'ref';
    case 'prime':
      return 'pr';
    case 'concept':
      return 'c';
    case 'quote':
      return 'q';
    case 'clause':
      return d > 0 ? clauseSkel(f.clause, d - 1) : 'cl';
    case 'temporal':
      return 't';
    default:
      return 'x';
  }
}

function opArgTag(a: OpArg, d: number): string {
  if ((a as Clause).type === 'pred' || (a as Clause).type === 'op') {
    return d > 0 ? clauseSkel(a as Clause, d - 1) : 'cl';
  }
  return fillerTag(a as Filler, d);
}

export function clauseSkel(c: Clause, d: number): string {
  if (c.type === 'pred') {
    const roles = Object.entries(c.roles)
      .map(([role, f]) => `${role}:${fillerTag(f as Filler, d)}`)
      .sort()
      .join(',');
    return `P(${c.pred}|${roles})`;
  }
  return `O(${c.op}|${c.args.map((a) => opArgTag(a, d)).join(',')})`;
}

/** All clause nodes in the tree (top level, embedded, quotes, restrictions). */
function allClauses(e: Explication): Clause[] {
  const out: Clause[] = [];
  const visit = (n: unknown): void => {
    if (n === null || typeof n !== 'object') return;
    if (Array.isArray(n)) {
      n.forEach(visit);
      return;
    }
    const o = n as Record<string, unknown>;
    if (o['type'] === 'pred' || o['type'] === 'op') out.push(o as unknown as Clause);
    Object.values(o).forEach(visit);
  };
  visit(e.clauses);
  return out;
}

export function featureSet(e: Explication): Set<string> {
  const out = new Set<string>([`F(${e.frame})`]);
  for (const c of allClauses(e)) out.add(clauseSkel(c, 1));
  return out;
}

/** Seeded sample WITHOUT replacement via DetStream Fisher-Yates prefix. */
function seededSample<T>(label: string, items: readonly T[], k: number): T[] {
  const stream = new DetStream(`perm/${label}`);
  const p = Array.from({ length: items.length }, (_, i) => i);
  for (let i = p.length - 1; i > 0; i--) {
    const j = stream.nextBelow(i + 1);
    const t = p[i]!;
    p[i] = p[j]!;
    p[j] = t;
  }
  return p.slice(0, k).map((i) => items[i]!);
}

function main(): void {
  const authored = loadKernelV0();
  const synth = readInput<{ artifact: string; records: SynthRecord[] }>('synthetic-concepts.json');
  if (synth.artifact !== 'e4-synthetic-concepts') throw new Error('ERR_ARTIFACT');

  const authoredIds = authored.map((r) => r.id);
  const synthIds = synth.records.map((r) => r.id);
  const allIds = [...authoredIds, ...synthIds];
  const explications = new Map<string, Explication>();
  for (const r of authored) explications.set(r.id, r.explication as Explication);
  for (const r of synth.records) explications.set(r.id, r.explication);

  // ---- tier 2: 10 synthetic concepts, zero exposure anywhere --------------
  const tier2 = seededSample('e4/tier2', synthIds, TIER2_SIZE).sort();
  const tier2Set = new Set(tier2);

  // ---- tier 1: 20% of the FULL vocab, stratified, disjoint from tier 2 ----
  const tier1Total = Math.round(TIER1_FRACTION * allIds.length); // 211
  const tier1Authored = Math.round((authoredIds.length / allIds.length) * tier1Total); // 11
  const tier1Synthetic = tier1Total - tier1Authored; // 200
  const synthPool = synthIds.filter((id) => !tier2Set.has(id));
  const tier1 = [
    ...seededSample('e4/tier1/authored', authoredIds, tier1Authored),
    ...seededSample('e4/tier1/synthetic', synthPool, tier1Synthetic),
  ].sort();
  const tier1Set = new Set(tier1);

  const train = allIds.filter((id) => !tier1Set.has(id) && !tier2Set.has(id)).sort();
  const trainSet = new Set(train);

  // ---- eval-gloss split for training concepts -----------------------------
  // variant DetStream('e4/evalgloss/<slug>').nextBelow(5) is the held-out
  // (eval) gloss of each TRAINING concept; held-out concepts use ALL 5
  // variants as eval items.
  const evalGlossVariant: Record<string, number> = {};
  for (const id of train) {
    evalGlossVariant[id] = new DetStream(`e4/evalgloss/${slugOf(id)}`).nextBelow(N_GLOSS_VARIANTS);
  }

  // ---- compositional split -------------------------------------------------
  const seenFeatures = new Set<string>();
  for (const id of train) for (const f of featureSet(explications.get(id)!)) seenFeatures.add(f);
  const composition: Record<
    string,
    { sharesStructureWithSeen: boolean; featureCoverage: number; features: number }
  > = {};
  for (const id of [...tier1, ...tier2]) {
    const fs = featureSet(explications.get(id)!);
    let covered = 0;
    for (const f of fs) if (seenFeatures.has(f)) covered++;
    composition[id] = {
      sharesStructureWithSeen: covered === fs.size,
      featureCoverage: covered / fs.size,
      features: fs.size,
    };
  }
  const sharedCount = Object.values(composition).filter((c) => c.sharesStructureWithSeen).length;

  const candidateSetSize = allIds.length; // 1054

  writeInput('holdout-manifest.json', {
    artifact: 'e4-holdout-manifest',
    date: new Date().toISOString(),
    kernelV0: corpusPin(),
    inputs: {
      syntheticConceptsSha256: sha256File(join(INPUTS_DIR, 'synthetic-concepts.json')),
      glossesSha256: sha256File(join(INPUTS_DIR, 'glosses.jsonl')),
      vectorManifestSha256: sha256File(join(INPUTS_DIR, 'vector-tables-manifest.json')),
    },
    vocab: {
      total: candidateSetSize,
      authored: authoredIds.length,
      synthetic: synthIds.length,
      order: 'authored (alphabetical) then synthetic by index — matches vector-tables-manifest ids',
    },
    seeds: {
      tier2: 'perm/e4/tier2 (DetStream Fisher-Yates prefix over synthetic ids)',
      tier1: 'perm/e4/tier1/authored + perm/e4/tier1/synthetic (stratified)',
      evalGloss: 'e4/evalgloss/<slug> nextBelow(5)',
    },
    tiers: {
      tier1: {
        note:
          'held out of emission supervision (no gloss->token examples in training); tokens DO ' +
          'appear in training text: authored members via E1 corpus substitution, and ALL tier-1 ' +
          'members via meaning-free exposure lines (exposure policy below)',
        count: tier1.length,
        authored: tier1.filter((id) => id.startsWith('urn:kernel-v0:')).length,
        synthetic: tier1.filter((id) => !id.startsWith('urn:kernel-v0:')).length,
        ids: tier1,
      },
      tier2: {
        note:
          'the zero-exposure tier ("cheapest decisive result"): rows exist in the embedding, ' +
          'but the tokens appear in NO training text of any kind — no emission examples, no ' +
          'exposure lines, and (synthetic-only, by construction) never in the E1 corpus. The ' +
          'emission builder fails closed if a tier-2 token would be emitted into a train shard.',
        count: tier2.length,
        ids: tier2,
      },
      train: { count: train.length },
    },
    exposurePolicy: {
      note:
        'exposure lines are meaning-free carrier sentences containing a concept token but no ' +
        'gloss content. They are emitted for BOTH train and tier-1 concepts (identical count ' +
        'per concept) so that "appears in exposure lines" carries ZERO information about ' +
        'holdout status — otherwise the model could learn exposure-only => never a target, an ' +
        'anti-signal against tier-1. Tier-2 gets none.',
      linesPerConcept: 20,
      framesAuthoredIn: 'pipeline/build_emission.py CARRIER_FRAMES (committed before training)',
      seed: 'e4/exposure/<seed>/<slug>',
    },
    evalGlossVariant,
    composition: {
      definition:
        'feature set = {frame} + depth-1 clause skeletons over all clause nodes (see ' +
        'harness/holdout.ts header); sharesStructureWithSeen = ALL features attested in the ' +
        'union of TRAIN concepts\' feature sets; featureCoverage = attested fraction (reported ' +
        'as a covariate). Accuracy is reported separately for shared vs novel subsets in both ' +
        'tiers — this is the compositional-generalisation readout that Palatucci 2009 (semantic ' +
        'output codes) and Frome 2013 (DeViSE) style zero-shot, with learned/distributional ' +
        'label embeddings, does not license.',
      sharedCount,
      novelCount: tier1.length + tier2.length - sharedCount,
      labels: composition,
    },
    statistics: {
      candidateSet:
        'concept tokens ONLY (all 1054 rows; BLOCKER 3) — scoring restricted to these logits',
      candidateSetSize,
      chance: {
        top1: 1 / candidateSetSize,
        top10: 10 / candidateSetSize,
        note: 'poc-design E4: "chance = 10/|C|" is the top-10 figure; top-1 chance = 1/|C|',
      },
      arms: {
        kernel: 'E1 kernel-frozen model + kernel rows for the 1000 new concepts (frozen)',
        shuffledKernel:
          'same, with the concept<->vector assignment deranged per vector-tables-manifest ' +
          '(the EMPIRICAL CHANCE FLOOR — BLOCKER 3)',
        randomFrozen: 'descriptive secondary arm',
      },
      pairedSeeds: N_SEEDS,
      primaryEndpoint:
        'tier-2 top-1 accuracy over the candidate set, kernel vs shuffled-kernel, one-sided ' +
        'exact paired sign-flip permutation across the 5 paired seeds, alpha = 0.05 (min ' +
        'attainable p = 1/32; Common rule 1 pairing)',
      secondaryEndpoints: [
        'tier-2 top-10 accuracy (same test)',
        'tier-1 top-1 and top-10 accuracy (same test)',
        'per-seed one-sided Fisher exact on pooled item counts (tier-2: 50 gloss-items/arm; ' +
          'tier-1: 1055 items/arm), Holm-corrected over seeds',
        'compositional subsets (shared vs novel): descriptive accuracies, no inferential claim',
      ],
      controlFloorCheck:
        'the shuffled-kernel arm must sit at empirical chance: pooled tier-2 accuracy inside ' +
        'the exact binomial 95% CI of 1/1054 — otherwise the control itself carries signal and ' +
        'the run is reported as invalid, not as a positive',
      advanceRule:
        'poc-design MAJOR 16: "credible" requires tier-2 success PLUS replication in a second ' +
        'model family; a single tier-1 positive triggers nothing',
    },
    trainingDataRule:
      'MAJOR 6: emission training may only consume the gloss file whose sha-256 equals ' +
      'GLOSS-HASH.txt (committed before any training); build_emission.py verifies this and ' +
      'fails closed',
  });
  console.log(
    `tiers: train ${train.length}, tier1 ${tier1.length} (authored ${
      tier1.filter((id) => id.startsWith('urn:kernel-v0:')).length
    }), tier2 ${tier2.length}; composition shared ${sharedCount}/${tier1.length + tier2.length}`,
  );
}

if (isMain(import.meta.url)) main();
