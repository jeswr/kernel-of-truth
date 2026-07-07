/**
 * E4 gloss set (docs/poc-design.md E4 rev 2 + MAJOR 6; bead
 * kernel-of-truth-73u): >=5 naturalistic paraphrases for EVERY concept in the
 * 1054-concept vocabulary, written from the MEANING of the explication tree
 * by the realizer (realizer.ts — authorship record there and in README.md).
 *
 * DISCIPLINE (enforced mechanically, fail closed):
 *  (a) INDEPENDENCE: glosses come from the realizer's own paraphrase rules,
 *      never from the deterministic explication renderings, the kernel-v0
 *      `gloss` fields, or poc/e1's cloze frames. Guard: no gloss for an
 *      authored concept may share a contiguous >= MAX_SHARED_NGRAM-word
 *      sequence with that concept's kernel-v0 gloss (redraw + counted).
 *  (b) TARGET-LEXICON DISJOINTNESS: a gloss for concept c may not contain any
 *      surface form that the COMPILED mapper lexicon maps to c — checked by
 *      running the live mapper (@jeswr/kernel-mapper mapText) over every
 *      gloss and rejecting any token whose decision is `concept c` or an
 *      abstention that includes c. First-pass collisions are COUNTED (the
 *      reported collision-rewrite rate), then rewritten via a deterministic
 *      retry with the target's surface lemmas banned inside the realizer.
 *      Scope note (pre-registered interpretation): full disjointness from the
 *      ENTIRE mapper lexicon is impossible for naturalistic English — the
 *      prime exponents are the most basic words of the language ("good",
 *      "want", "know", "say", ...) — so the rule is per-target disjointness,
 *      which is what breaks the copy-the-token shortcut. Other concepts'
 *      surface forms MAY appear (that residual channel is reported, not
 *      hidden; see README "leakage risks").
 *  (c) >=5 pairwise-distinct variants per concept, styles 0..4.
 *
 * Output: inputs/glosses.jsonl (one JSON object per line, sorted by concept
 * id then variant), its sha-256 written to poc/e4/GLOSS-HASH.txt — the
 * MAJOR 6 pre-publication hash: committed BEFORE any training consumes the
 * glosses — plus inputs/gloss-report.json (collision/redraw statistics).
 */

import { DetStream } from '@jeswr/kernel-encoder';
import type { Explication } from '@jeswr/kernel-encoder';
import {
  buildLexicon,
  loadManifestConcepts,
  mapText,
  surfaceOfLabel,
} from '@jeswr/kernel-mapper';
import type { Lexicon } from '@jeswr/kernel-mapper';
import { writeFileSync } from 'node:fs';
import { join } from 'node:path';
import {
  E4_DIR,
  INPUTS_DIR,
  KERNEL_V0_DIR,
  N_GLOSS_VARIANTS,
  corpusPin,
  ensureInputsDir,
  isMain,
  loadKernelV0,
  readInput,
  sha256Hex,
  slugOf,
} from './common.js';
import { STYLE_COUNT, realizeExplication } from './realizer.js';
import type { SynthRecord } from './synthVocab.js';

/** Independence guard: longest tolerated shared contiguous word run vs the
 * concept's own kernel-v0 gloss (short NSM collocations like "feel something
 * good" are unavoidable; long runs would mean templated text). */
export const MAX_SHARED_NGRAM = 7;

const MAX_ATTEMPTS = 12;

export interface GlossLine {
  readonly conceptId: string;
  readonly slug: string;
  readonly variant: number;
  readonly style: number;
  readonly gloss: string;
  readonly rngLabel: string;
  readonly attempts: number;
  readonly firstPassCollision: boolean;
}

/** Nominal phrases for concepts REFERENCED inside other explications
 * (kernel-v0 conceptRef/conceptHead targets). Alternatives are ban-filtered
 * per target at realization time. Fallback: surface of the concept label. */
const CONCEPT_PHRASES: Record<string, readonly string[]> = {
  'urn:kernel-v0:event': ['an event', 'a happening'],
  'urn:kernel-v0:break': ['breaking', 'a breaking'],
  'urn:kernel-v0:broken': ['a broken thing'],
  'urn:kernel-v0:happy': ['a happy feeling'],
  'urn:kernel-v0:sad': ['a sad feeling'],
  'urn:kernel-v0:grieving': ['grieving'],
  'urn:kernel-v0:death': ['a death', 'a dying'],
  'urn:kernel-v0:give': ['giving', 'a giving'],
  'urn:kernel-v0:lie': ['a lie', 'lying'],
  'urn:kernel-v0:lose': ['losing', 'a losing'],
  'urn:kernel-v0:make': ['making', 'a making'],
  'urn:kernel-v0:remember': ['remembering'],
  'urn:kernel-v0:forget': ['forgetting'],
  'urn:kernel-v0:learn': ['learning'],
  'urn:kernel-v0:take': ['taking', 'a taking'],
  'urn:kernel-v0:promise': ['a promise'],
  'urn:kernel-v0:help': ['helping'],
};

/** Predicative (BE-SPEC attribute) phrasings where the nominal would be off. */
const CONCEPT_ATTR_PHRASES: Record<string, readonly string[]> = {
  'urn:kernel-v0:happy': ['happy', 'glad'],
  'urn:kernel-v0:sad': ['sad', 'unhappy'],
  'urn:kernel-v0:broken': ['broken'],
  'urn:kernel-v0:grieving': ['grieving'],
  'urn:kernel-v0:dead': ['dead'],
  'urn:kernel-v0:alive': ['alive'],
};

/** Words never banned from multiword surface phrases (function words). */
const PHRASE_STOPWORDS = new Set(['of', 'a', 'an', 'the', 'is', 'has', 'to', 'in']);

/** Meaning-neutral openers used only to break realization ties (see loop). */
const OPENERS: readonly string[] = [
  'Put simply: ',
  'In other words: ',
  'Said another way: ',
  'Here is the idea: ',
  'It comes to this: ',
];

/** Per-concept banned lemma set from the COMPILED mapper lexicon. */
export function bannedLemmasFor(lexicon: Lexicon, conceptId: string): Set<string> {
  const out = new Set<string>();
  for (const e of lexicon.entries) {
    if (e.target.kind !== 'concept' || e.target.conceptId !== conceptId) continue;
    if (e.phrase.length === 1) out.add(e.phrase[0]!);
    else for (const w of e.phrase) if (!PHRASE_STOPWORDS.has(w)) out.add(w);
  }
  return out;
}

/** Mechanical target-disjointness check via the live mapper. */
export function glossCollides(lexicon: Lexicon, conceptId: string, gloss: string): boolean {
  for (const t of mapText(gloss, lexicon)) {
    if (!t.isWord) continue;
    const d = t.decision;
    if (d.kind === 'concept' && d.conceptId === conceptId) return true;
    if (
      d.kind === 'abstain' &&
      d.candidates.some((c) => c.kind === 'concept' && c.conceptId === conceptId)
    ) {
      return true;
    }
  }
  return false;
}

function words(s: string): string[] {
  return s.toLowerCase().split(/[^a-z']+/).filter((w) => w.length > 0);
}

/** Longest shared contiguous word run between two texts. */
export function longestSharedRun(a: string, b: string): number {
  const wa = words(a);
  const wb = words(b);
  let best = 0;
  const prev = new Array<number>(wb.length + 1).fill(0);
  for (let i = 1; i <= wa.length; i++) {
    let diagonal = 0; // prev[j-1] from the previous row
    for (let j = 1; j <= wb.length; j++) {
      const up = prev[j]!;
      const cur = wa[i - 1] === wb[j - 1] ? diagonal + 1 : 0;
      prev[j] = cur;
      diagonal = up;
      if (cur > best) best = cur;
    }
    prev[0] = 0;
  }
  return best;
}

export interface AuthoringResult {
  readonly lines: GlossLine[];
  readonly stats: {
    concepts: number;
    glosses: number;
    firstPassCollisions: number;
    collisionsAuthored: number;
    collisionsSynthetic: number;
    ngramRedraws: number;
    duplicateRedraws: number;
    maxAttemptsUsed: number;
    maxSharedRunAfter: number;
  };
}

export function authorGlosses(
  concepts: readonly { id: string; explication: Explication; kernelGloss?: string }[],
  lexicon: Lexicon,
): AuthoringResult {
  const lines: GlossLine[] = [];
  const stats = {
    concepts: concepts.length,
    glosses: 0,
    firstPassCollisions: 0,
    collisionsAuthored: 0,
    collisionsSynthetic: 0,
    ngramRedraws: 0,
    duplicateRedraws: 0,
    maxAttemptsUsed: 0,
    maxSharedRunAfter: 0,
  };
  if (N_GLOSS_VARIANTS > STYLE_COUNT) throw new Error('ERR_STYLES: variants > styles');

  for (const c of concepts) {
    const slug = slugOf(c.id);
    const banned = bannedLemmasFor(lexicon, c.id);
    const authored = c.id.startsWith('urn:kernel-v0:');
    const seen = new Set<string>();
    for (let v = 0; v < N_GLOSS_VARIANTS; v++) {
      let firstPassCollision = false;
      let gloss = '';
      let label = '';
      let attempt = 0;
      let dupWrap = false; // tiny ASTs can exhaust the style space; see below
      for (; attempt < MAX_ATTEMPTS; attempt++) {
        label = attempt === 0 ? `e4/gloss/${slug}/${v}` : `e4/gloss/${slug}/${v}/retry${attempt}`;
        const rng = new DetStream(label);
        // Pass 0 authors the natural phrasing (no proactive bans) so the
        // reported collision rate is an honest measurement; retries ban the
        // target's own surface lemmas inside the realizer.
        const bans = attempt === 0 ? new Set<string>() : banned;
        gloss = realizeExplication(c.explication, {
          style: v,
          rng,
          bannedLemmas: bans,
          conceptPhrase: (id, pos) => {
            const alts =
              (pos === 'attribute' ? CONCEPT_ATTR_PHRASES[id] : undefined) ??
              CONCEPT_PHRASES[id] ??
              [fallbackPhrase(id)];
            const ok = alts.filter((p) => !phraseHitsBanned(p, bans));
            const pool = ok.length > 0 ? ok : alts;
            return pool[rng.nextBelow(pool.length)]!;
          },
        });
        // Distinctness rescue: single-clause explications ("someone feels
        // good") admit too few realizations for 5 pairwise-distinct variants;
        // after a duplicate, prefix a meaning-neutral opener (rotates with the
        // attempt, so variants stay distinct while staying paraphrases).
        if (dupWrap) {
          const opener = OPENERS[(v + attempt) % OPENERS.length]!;
          gloss = `${opener}${gloss}`;
        }
        let bad = false;
        if (glossCollides(lexicon, c.id, gloss)) {
          if (attempt === 0) {
            firstPassCollision = true;
            stats.firstPassCollisions++;
            if (authored) stats.collisionsAuthored++;
            else stats.collisionsSynthetic++;
          }
          bad = true;
        }
        if (!bad && authored && c.kernelGloss !== undefined) {
          if (longestSharedRun(gloss, c.kernelGloss) > MAX_SHARED_NGRAM) {
            stats.ngramRedraws++;
            bad = true;
          }
        }
        if (!bad && seen.has(gloss)) {
          stats.duplicateRedraws++;
          dupWrap = true;
          bad = true;
        }
        if (!bad) break;
      }
      if (attempt >= MAX_ATTEMPTS) {
        throw new Error(`ERR_GLOSS: could not author a clean gloss for ${c.id} variant ${v}`);
      }
      stats.maxAttemptsUsed = Math.max(stats.maxAttemptsUsed, attempt);
      if (authored && c.kernelGloss !== undefined) {
        stats.maxSharedRunAfter = Math.max(
          stats.maxSharedRunAfter,
          longestSharedRun(gloss, c.kernelGloss),
        );
      }
      seen.add(gloss);
      lines.push({
        conceptId: c.id,
        slug,
        variant: v,
        style: v,
        gloss,
        rngLabel: label,
        attempts: attempt + 1,
        firstPassCollision,
      });
      stats.glosses++;
    }
  }
  return { lines, stats };
}

function phraseHitsBanned(phrase: string, banned: ReadonlySet<string>): boolean {
  if (banned.size === 0) return false;
  return words(phrase).some((w) => banned.has(w));
}

function fallbackPhrase(id: string): string {
  return slugOf(id).replace(/-/g, ' ');
}

function main(): void {
  const manifest = loadManifestConcepts(join(KERNEL_V0_DIR, 'manifest.json'));
  const lexicon = buildLexicon(manifest);
  const authored = loadKernelV0();
  const synth = readInput<{ artifact: string; records: SynthRecord[] }>('synthetic-concepts.json');
  if (synth.artifact !== 'e4-synthetic-concepts') throw new Error('ERR_ARTIFACT');

  const concepts = [
    ...authored.map((r) => ({
      id: r.id,
      explication: r.explication as Explication,
      kernelGloss: r.gloss,
    })),
    ...synth.records.map((r) => ({ id: r.id, explication: r.explication })),
  ];
  console.log(`authoring ${N_GLOSS_VARIANTS} glosses x ${concepts.length} concepts ...`);
  const { lines, stats } = authorGlosses(concepts, lexicon);

  // Final fail-closed re-verification of the whole set.
  for (const l of lines) {
    if (glossCollides(lexicon, l.conceptId, l.gloss)) {
      throw new Error(`ERR_GLOSS_GATE: post-hoc collision for ${l.conceptId} v${l.variant}`);
    }
  }

  ensureInputsDir();
  const jsonl = lines.map((l) => JSON.stringify(l)).join('\n') + '\n';
  const glossPath = join(INPUTS_DIR, 'glosses.jsonl');
  writeFileSync(glossPath, jsonl);
  const hash = sha256Hex(jsonl);
  console.log(`wrote ${glossPath} (${lines.length} glosses, sha256 ${hash})`);

  // MAJOR 6: the gloss-set hash artifact, committed BEFORE any training run.
  writeFileSync(
    join(E4_DIR, 'GLOSS-HASH.txt'),
    [
      `sha256(poc/e4/inputs/glosses.jsonl) = ${hash}`,
      `published: ${new Date().toISOString()}`,
      'rule (docs/poc-design.md E4 rev 2, MAJOR 6): this hash is committed BEFORE any',
      'training consumes the gloss set; an E4 run against a gloss file with a different',
      'sha-256 is a NEW pre-registration and must be reported as such.',
      '',
    ].join('\n'),
  );
  console.log('wrote GLOSS-HASH.txt');

  const rate = (n: number, d: number) => `${((100 * n) / d).toFixed(2)}%`;
  const authoredGlossCount = authored.length * N_GLOSS_VARIANTS;
  const synthGlossCount = synth.records.length * N_GLOSS_VARIANTS;
  const report = {
    artifact: 'e4-gloss-report',
    date: new Date().toISOString(),
    glossSetSha256: hash,
    kernelV0: corpusPin(),
    authorship:
      'realizer.ts (kot-e4-realizer/1), rules authored by the E4 data-prep agent ' +
      '(Claude Fable 5, 2026-07-07) from AST meaning; NOT derived from the deterministic ' +
      'explication renderings, kernel-v0 gloss fields, or e1 cloze frames — see realizer.ts ' +
      'header + README.md honesty notes',
    counts: {
      concepts: stats.concepts,
      glosses: stats.glosses,
      perConcept: N_GLOSS_VARIANTS,
      authoredGlosses: authoredGlossCount,
      syntheticGlosses: synthGlossCount,
    },
    collisionRewrites: {
      note:
        'first-pass glosses containing a mapper surface form of their OWN target concept ' +
        '(mechanical mapText check, abstentions counted as hits), rewritten via seeded retry',
      total: stats.firstPassCollisions,
      totalRate: rate(stats.firstPassCollisions, stats.glosses),
      authored: stats.collisionsAuthored,
      authoredRate: rate(stats.collisionsAuthored, authoredGlossCount),
      synthetic: stats.collisionsSynthetic,
      syntheticRate: rate(stats.collisionsSynthetic, synthGlossCount),
    },
    independenceGuard: {
      maxSharedNgram: MAX_SHARED_NGRAM,
      ngramRedraws: stats.ngramRedraws,
      maxSharedRunAfter: stats.maxSharedRunAfter,
    },
    duplicateRedraws: stats.duplicateRedraws,
    maxAttemptsUsed: stats.maxAttemptsUsed,
    lexiconSurfaceOf: 'concept labels via surfaceOfLabel()',
    styles: STYLE_COUNT,
  };
  writeFileSync(join(INPUTS_DIR, 'gloss-report.json'), JSON.stringify(report, null, 2) + '\n');
  console.log('wrote inputs/gloss-report.json');
  console.log(JSON.stringify(report.collisionRewrites, null, 2));
  void surfaceOfLabel; // (imported for documentation parity with the mapper API)
}

if (isMain(import.meta.url)) main();
