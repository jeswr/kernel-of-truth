#!/usr/bin/env node
/**
 * M0a — mapper measurement over a TinyStories sample (poc-design.md Phase M).
 *
 * Usage: node mapper/m0/run-m0a.mjs <TinyStories-valid.txt> [outDir] [--policy=<name>]
 *
 * Reads the plain-text split (stories separated by <|endoftext|>), runs the
 * v0 mapper over every story, and emits:
 *   - results/m0a-report.json     aggregate numbers (token mass, abstention,
 *                                 per-concept/per-prime hit distributions)
 *   - annotation-sample.jsonl     300-token stratified sample of mapper
 *                                 decisions, formatted for HUMAN annotation
 *                                 (judgment fields left empty)
 *
 * FLAG-GATED policy runs (bead kernel-of-truth-30d; NOT the default; the
 * published M0a numbers come from the flagless invocation, unchanged):
 * `--policy=` one of tiers-measured | tiers-all5 | exclude-shadowed |
 * hybrid-recommended (declarations + evidence in ../src/policy.ts). A policy
 * run writes results/m0a-policy-<name>.json ONLY (never overwrites the
 * baseline report, never rewrites annotation-sample.jsonl), stamps the
 * content-addressed policy hash, records per-rule tier resolutions
 * (count + surface inventory), and — for exclusion policies — reports
 * zero-hit concepts over the DECLARED evaluated set with the exclusions
 * named.
 *
 * Token-mass definition (pinned): one unit = one contraction-expanded word
 * token ("didn't" = do + not = 2 units); punctuation/number spans excluded.
 * Raw surface-word counts are reported alongside for transparency.
 *
 * Sampling: deterministic seeded reservoir per stratum (concept-mapped /
 * prime-mapped / abstained / unmapped; 100/100/50/50), seed 0xC0FFEE.
 * Stratum population sizes are in the report so precision/recall can be
 * reweighted to the corpus.
 */
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  buildLexicon,
  loadManifestConcepts,
  mapText,
  policyHash,
  SHADOWED_EXCLUDE_ALL5,
  SHADOWED_HYBRID_RECOMMENDED,
  SHADOWED_TIERS_ALL5,
  SHADOWED_TIERS_MEASURED,
  targetKey,
} from '../dist/src/index.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..');
const MANIFEST = join(REPO, 'data', 'kernel-v0', 'manifest.json');

const POLICIES = {
  'tiers-measured': SHADOWED_TIERS_MEASURED,
  'tiers-all5': SHADOWED_TIERS_ALL5,
  'exclude-shadowed': SHADOWED_EXCLUDE_ALL5,
  'hybrid-recommended': SHADOWED_HYBRID_RECOMMENDED,
};

const positional = [];
let policyName = null;
for (const arg of process.argv.slice(2)) {
  if (arg.startsWith('--policy=')) {
    policyName = arg.slice('--policy='.length);
    if (!(policyName in POLICIES)) {
      console.error(`unknown --policy=${policyName}; one of: ${Object.keys(POLICIES).join(' | ')}`);
      process.exit(1);
    }
  } else {
    positional.push(arg);
  }
}
const corpusPath = positional[0];
if (!corpusPath) {
  console.error('usage: run-m0a.mjs <TinyStories-valid.txt> [outDir] [--policy=<name>]');
  process.exit(1);
}
const outDir = positional[1] ?? HERE;
const policy = policyName === null ? undefined : POLICIES[policyName];
mkdirSync(join(outDir, 'results'), { recursive: true });

// --- deterministic PRNG (mulberry32) + per-stratum reservoir sampling -----
function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rand = mulberry32(0xc0ffee);

const STRATA = { concept: 100, prime: 100, abstain: 50, none: 50 };
const reservoirs = Object.fromEntries(
  Object.keys(STRATA).map((k) => [k, { items: [], seen: 0, cap: STRATA[k] }]),
);
function offer(stratum, item) {
  const r = reservoirs[stratum];
  r.seen += 1;
  if (r.items.length < r.cap) {
    r.items.push(item);
  } else {
    const j = Math.floor(rand() * r.seen);
    if (j < r.cap) r.items[j] = item;
  }
}

// --- corpus pass -----------------------------------------------------------
const lexicon = buildLexicon(loadManifestConcepts(MANIFEST));
const raw = readFileSync(corpusPath, 'utf8');
const stories = raw.split('<|endoftext|>').map((s) => s.trim()).filter((s) => s.length > 0);

const counts = {
  stories: stories.length,
  expandedWordTokens: 0,
  surfaceWordTokens: 0,
  nonWordSpans: 0,
  byDecision: { concept: 0, prime: 0, abstain: 0, none: 0 },
};
const conceptHits = new Map(); // conceptId -> expanded-token count
const primeHits = new Map(); // prime name -> expanded-token count
const abstainBySurface = new Map(); // norm -> { count, candidates }
const unmappedByLemma = new Map(); // lemma -> count
const tierResolutions = new Map(); // decision-set key -> { winner, count, bySurface }

for (let s = 0; s < stories.length; s += 1) {
  const text = stories[s];
  const anns = mapText(text, lexicon, policy);
  for (const t of anns) {
    if (!t.isWord) {
      counts.nonWordSpans += 1;
      continue;
    }
    counts.expandedWordTokens += 1;
    if (!t.isExpansion) counts.surfaceWordTokens += 1;
    const d = t.decision;
    counts.byDecision[d.kind] += 1;
    if (d.kind === 'concept') {
      conceptHits.set(d.conceptId, (conceptHits.get(d.conceptId) ?? 0) + 1);
    } else if (d.kind === 'prime') {
      primeHits.set(d.prime, (primeHits.get(d.prime) ?? 0) + 1);
    } else if (d.kind === 'abstain') {
      const rec = abstainBySurface.get(t.norm) ?? {
        count: 0,
        candidates: d.candidates.map(targetKey).sort(),
      };
      rec.count += 1;
      abstainBySurface.set(t.norm, rec);
    } else {
      unmappedByLemma.set(t.lemma, (unmappedByLemma.get(t.lemma) ?? 0) + 1);
    }
    // policy audit: token mass resolved by each declared tier rule
    if ((d.kind === 'concept' || d.kind === 'prime') && d.resolvedFrom !== undefined) {
      const key = d.resolvedFrom.map(targetKey).sort().join('|');
      const rec = tierResolutions.get(key) ?? {
        winner: d.kind === 'concept' ? d.conceptId : `prime:${d.prime}`,
        count: 0,
        bySurface: new Map(),
      };
      rec.count += 1;
      rec.bySurface.set(t.norm, (rec.bySurface.get(t.norm) ?? 0) + 1);
      tierResolutions.set(key, rec);
    }
    // sample only phrase heads / single tokens so one decision = one item;
    // skip expansion continuations that repeat the same surface span
    if (t.phrasePos === 0) {
      offer(d.kind, {
        storyIndex: s,
        start: t.start,
        end: t.end,
        surface: t.surface,
        norm: t.norm,
        lemma: t.lemma,
        phraseLen: t.phraseLen,
        decision:
          d.kind === 'concept'
            ? { kind: 'concept', target: d.conceptId }
            : d.kind === 'prime'
              ? { kind: 'prime', target: `prime:${d.prime}` }
              : d.kind === 'abstain'
                ? { kind: 'abstain', candidates: d.candidates.map(targetKey).sort() }
                : { kind: 'none' },
        contextBefore: text.slice(Math.max(0, t.start - 80), t.start).replace(/\s+/g, ' '),
        contextAfter: text.slice(t.end, t.end + 80).replace(/\s+/g, ' '),
      });
    }
  }
}

// --- report ----------------------------------------------------------------
const total = counts.expandedWordTokens;
const pct = (n) => Math.round((n / total) * 1e6) / 1e4; // 4dp percent
const sortDesc = (m) => [...m.entries()].sort((a, b) => b[1] - a[1]);

const allConceptIds = lexicon.entries
  .filter((e) => e.target.kind === 'concept')
  .map((e) => targetKey(e.target));
const uniqueConceptIds = [...new Set(allConceptIds)];
// (d) exclusion policies shrink the EVALUATED concept universe (declared,
// never silent); decisions upstream are untouched.
const excluded = new Set(policy?.excludeConcepts ?? []);
const evaluatedConceptIds = uniqueConceptIds.filter((id) => !excluded.has(id));
const zeroHitConcepts = evaluatedConceptIds.filter((id) => !conceptHits.has(id)).sort();

const report = {
  experiment: policy === undefined ? 'M0a' : `M0a-policy-${policy.name}`,
  ...(policy === undefined
    ? {}
    : {
        policy: {
          name: policy.name,
          sha256: policyHash(policy),
          declaration: policy,
          note:
            'FLAG-GATED policy run (bead kernel-of-truth-30d): NOT the published M0a; ' +
            'candidate pre-registration amendment pending coordinator decision.',
        },
      }),
  date: new Date().toISOString().slice(0, 10),
  corpus: {
    source: 'roneneldan/TinyStories TinyStories-valid.txt (HuggingFace, plain HTTP)',
    stories: counts.stories,
    bytes: raw.length,
  },
  tokenMassDefinition:
    'one unit = one contraction-expanded alphabetic word token; punctuation and numbers excluded',
  tokens: {
    expandedWordTokens: counts.expandedWordTokens,
    surfaceWordTokens: counts.surfaceWordTokens,
    nonWordSpans: counts.nonWordSpans,
  },
  headline: {
    pctMappedToConcepts: pct(counts.byDecision.concept),
    pctMappedToPrimes: pct(counts.byDecision.prime),
    pctMappedTotal: pct(counts.byDecision.concept + counts.byDecision.prime),
    pctAbstained: pct(counts.byDecision.abstain),
    pctUnmapped: pct(counts.byDecision.none),
  },
  decisions: counts.byDecision,
  conceptHitDistribution: Object.fromEntries(sortDesc(conceptHits)),
  // flagless reports keep the exact v0 schema; policy runs declare their universe
  ...(policy === undefined
    ? {}
    : {
        evaluatedConceptCount: evaluatedConceptIds.length,
        ...(excluded.size > 0 ? { excludedConcepts: [...excluded].sort() } : {}),
      }),
  zeroHitConcepts,
  zeroHitConceptCount: zeroHitConcepts.length,
  ...(tierResolutions.size > 0
    ? {
        tierResolutions: Object.fromEntries(
          [...tierResolutions.entries()].map(([k, v]) => [
            k,
            {
              winner: v.winner,
              count: v.count,
              bySurface: Object.fromEntries([...v.bySurface.entries()].sort((a, b) => b[1] - a[1])),
            },
          ]),
        ),
      }
    : {}),
  primeHitDistribution: Object.fromEntries(sortDesc(primeHits)),
  abstentionBySurface: Object.fromEntries(
    sortDesc(new Map([...abstainBySurface.entries()].map(([k, v]) => [k, v.count])))
      .map(([k, v]) => [k, { count: v, candidates: abstainBySurface.get(k).candidates }]),
  ),
  topUnmappedLemmas: Object.fromEntries(sortDesc(unmappedByLemma).slice(0, 60)),
  sampling: {
    seed: '0xC0FFEE (mulberry32), per-stratum reservoir',
    strata: Object.fromEntries(
      Object.entries(reservoirs).map(([k, r]) => [k, { sampled: r.items.length, population: r.seen }]),
    ),
  },
};

const reportName = policy === undefined ? 'm0a-report.json' : `m0a-policy-${policy.name}.json`;
writeFileSync(join(outDir, 'results', reportName), `${JSON.stringify(report, null, 2)}\n`);

// Policy runs never rewrite the baseline annotation sample: the 300-item
// sample belongs to the published flagless measurement.
if (policy !== undefined) {
  console.log(JSON.stringify(report.headline, null, 2));
  console.log(`policy=${policy.name} sha256=${policyHash(policy)}`);
  console.log(`stories=${counts.stories} tokens=${total} -> results/${reportName}`);
  process.exit(0);
}

// --- annotation sample (human-annotation format; judgment fields EMPTY) ----
const lines = [];
let itemId = 0;
for (const stratum of Object.keys(STRATA)) {
  for (const item of reservoirs[stratum].items) {
    itemId += 1;
    lines.push(
      JSON.stringify({
        itemId: `m0a-${String(itemId).padStart(3, '0')}`,
        stratum,
        ...item,
        instructions:
          'HUMAN ANNOTATOR: fill "judgment" with one of correct|incorrect|unclear. ' +
          'For mapped items: is the mapped target the meaning of this token in context? ' +
          'For abstain: would ANY single listed candidate have been correct (then name it in trueTarget)? ' +
          'For none: should this token have mapped to a kernel-v0 concept or prime (then name it in trueTarget)?',
        judgment: '',
        trueTarget: '',
        note: '',
      }),
    );
  }
}
writeFileSync(join(outDir, 'annotation-sample.jsonl'), `${lines.join('\n')}\n`);

console.log(JSON.stringify(report.headline, null, 2));
console.log(`stories=${counts.stories} tokens=${total}`);
console.log(`sample items=${itemId} -> ${join(outDir, 'annotation-sample.jsonl')}`);
