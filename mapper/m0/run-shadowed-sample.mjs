#!/usr/bin/env node
/**
 * Shadowed-concept occurrence sampler (bead kernel-of-truth-30d).
 *
 * Five kernel-v0 concepts (broken, lost, inside, near, kind) can NEVER map
 * under the abstain policy: every surface occurrence produces a multi-target
 * candidate set (prime allolex or another concept's inflection), so the
 * abstain-and-record rule permanently shadows them (M0a zero-hit list).
 *
 * This script draws a deterministic 50-item reservoir sample PER SHADOWED
 * CONCEPT of exactly those abstained occurrences (candidate set keyed, so
 * inflected variants like "kinds"/"nearest" are included), with story
 * context, formatted for annotation. Judgments are authored separately
 * (make-shadowed-judgments.py — AGENT-JUDGED, pending human annotation, same
 * caveat discipline as M0a).
 *
 * Usage: node mapper/m0/run-shadowed-sample.mjs <TinyStories-valid.txt> [outDir]
 * Output: <outDir>/shadowed-sample.jsonl  (+ population counts on stdout)
 *
 * Seed 0x5EED05 (mulberry32), separate from the M0a sample seed 0xC0FFEE so
 * the two samples are independent draws.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildLexicon, loadManifestConcepts, mapText, targetKey } from '../dist/src/index.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..');
const MANIFEST = join(REPO, 'data', 'kernel-v0', 'manifest.json');

const corpusPath = process.argv[2];
if (!corpusPath) {
  console.error('usage: run-shadowed-sample.mjs <TinyStories-valid.txt> [outDir]');
  process.exit(1);
}
const outDir = process.argv[3] ?? HERE;

// Shadowed concept -> its full collision candidate set (sorted target keys).
// These sets are exactly what the mapper records on abstention; matching on
// the SET (not the surface) automatically includes inflected variants that
// reach the same candidates ("kinds", "kinder", "nearest", "insides", ...).
const SHADOWED = {
  'urn:kernel-v0:broken': ['urn:kernel-v0:break', 'urn:kernel-v0:broken'],
  'urn:kernel-v0:lost': ['urn:kernel-v0:lose', 'urn:kernel-v0:lost'],
  'urn:kernel-v0:inside': ['prime:INSIDE', 'urn:kernel-v0:inside'],
  'urn:kernel-v0:near': ['prime:NEAR', 'urn:kernel-v0:near'],
  'urn:kernel-v0:kind': ['prime:KIND', 'urn:kernel-v0:kind'],
};
const setKey = (keys) => [...keys].sort().join('|');
const bySet = new Map(Object.entries(SHADOWED).map(([c, s]) => [setKey(s), c]));

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
const rand = mulberry32(0x5eed05);
const CAP = 50;
const reservoirs = Object.fromEntries(
  Object.keys(SHADOWED).map((c) => [c, { items: [], seen: 0, surfaces: new Map() }]),
);

const lexicon = buildLexicon(loadManifestConcepts(MANIFEST));
const raw = readFileSync(corpusPath, 'utf8');
const stories = raw.split('<|endoftext|>').map((s) => s.trim()).filter((s) => s.length > 0);

for (let s = 0; s < stories.length; s += 1) {
  const text = stories[s];
  for (const t of mapText(text, lexicon)) {
    if (!t.isWord || t.decision.kind !== 'abstain' || t.phrasePos !== 0) continue;
    const k = setKey(t.decision.candidates.map(targetKey));
    const concept = bySet.get(k);
    if (concept === undefined) continue;
    const r = reservoirs[concept];
    r.seen += 1;
    r.surfaces.set(t.norm, (r.surfaces.get(t.norm) ?? 0) + 1);
    const item = {
      storyIndex: s,
      start: t.start,
      end: t.end,
      surface: t.surface,
      norm: t.norm,
      candidates: t.decision.candidates.map(targetKey).sort(),
      contextBefore: text.slice(Math.max(0, t.start - 100), t.start).replace(/\s+/g, ' '),
      contextAfter: text.slice(t.end, t.end + 100).replace(/\s+/g, ' '),
    };
    if (r.items.length < CAP) r.items.push(item);
    else {
      const j = Math.floor(rand() * r.seen);
      if (j < CAP) r.items[j] = item;
    }
  }
}

const lines = [];
const populations = {};
for (const [concept, r] of Object.entries(reservoirs)) {
  populations[concept] = {
    population: r.seen,
    sampled: r.items.length,
    bySurface: Object.fromEntries([...r.surfaces.entries()].sort((a, b) => b[1] - a[1])),
  };
  const short = concept.replace('urn:kernel-v0:', '');
  r.items.forEach((item, i) => {
    lines.push(
      JSON.stringify({
        itemId: `shadow-${short}-${String(i + 1).padStart(2, '0')}`,
        concept,
        ...item,
        instructions:
          'ANNOTATOR: name in trueTarget which candidate (if any) is the correct ' +
          'mapping of this token in context: one of the listed candidates, ' +
          '"either" (candidates denote the same contextual sense), or "neither" ' +
          '(contextual sense matches no candidate). Add a note for non-obvious calls.',
        trueTarget: '',
        note: '',
      }),
    );
  });
}
writeFileSync(join(outDir, 'shadowed-sample.jsonl'), `${lines.join('\n')}\n`);
console.log(JSON.stringify({ seed: '0x5EED05 (mulberry32)', cap: CAP, populations }, null, 2));
console.log(`items=${lines.length} -> ${join(outDir, 'shadowed-sample.jsonl')}`);
