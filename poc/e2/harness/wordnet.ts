/**
 * Minimal offline WordNet 3.1 reader over the `wordnet-db` npm package
 * (35 MB vendored via node_modules; well under the ~100 MB budget — the
 * "subset choice" of the brief is: full WordNet 3.1 database files, no
 * subsetting needed).
 *
 * Provides:
 *   - lemma lookup per POS (index.<pos>), with a tiny morphy-style
 *     detachment fallback for surface forms absent from the index
 *     (kernel-v0 needs exactly one: "archived" -> verb "archive");
 *   - a synset relation graph for path-based similarity. Edges (undirected,
 *     unit cost), documented in poc/e2/README.md:
 *       @  hypernym          @i instance hypernym
 *       ~  hyponym           ~i instance hyponym
 *       &  similar-to (adj)  =  attribute (noun<->adj)
 *       +  derivationally related form (lexical)
 *       \  pertainym / derived-from-adjective
 *       $  verb group
 *     Rationale (DEVIATION, flagged): NLTK path_similarity runs on the
 *     noun/verb hypernym taxonomies only and is UNDEFINED for adjectives —
 *     16 of E2's 51 items are adjectives. The extended relation graph keeps
 *     "path similarity" well-defined across the whole item set; the
 *     hypernym-only variant is emitted alongside for transparency.
 */

import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { createRequire } from 'node:module';

const require_ = createRequire(import.meta.url);

export const WN_POS = ['noun', 'verb', 'adj', 'adv'] as const;
export type WnPos = (typeof WN_POS)[number];

/** POS letters as used in data-file pointers -> file POS. `s` (satellite adj) shares data.adj. */
const POS_LETTER_TO_FILE: Record<string, WnPos> = { n: 'noun', v: 'verb', a: 'adj', s: 'adj', r: 'adv' };

export type SynsetKey = string; // `${posLetter-normalised-file}:${offset}` e.g. "noun:12345678"

export interface WordnetGraph {
  /** (pos, lemma) -> synset keys. */
  lookup(lemma: string, pos?: WnPos): SynsetKey[];
  /** All relation-graph neighbours (extended edge set). */
  neighbours(key: SynsetKey): readonly SynsetKey[];
  /** Hypernym-only neighbours (@, @i), directed upward. */
  hypernyms(key: SynsetKey): readonly SynsetKey[];
  readonly synsetCount: number;
}

const EXTENDED_SYMBOLS = new Set(['@', '@i', '~', '~i', '&', '=', '+', '\\', '$']);
const HYPERNYM_SYMBOLS = new Set(['@', '@i']);

function dictDir(): string {
  return join(require_.resolve('wordnet-db/package.json'), '..', 'dict');
}

export function loadWordnet(): WordnetGraph {
  const dir = dictDir();
  const index = new Map<string, string[]>(); // `${pos}:${lemma}` -> keys
  const adjacency = new Map<SynsetKey, SynsetKey[]>();
  const hyper = new Map<SynsetKey, SynsetKey[]>();
  let synsetCount = 0;

  for (const pos of WN_POS) {
    // ---- index.<pos>: lemma pos synset_cnt p_cnt [ptrs...] sense_cnt tagsense_cnt offsets...
    const idx = readFileSync(join(dir, `index.${pos}`), 'utf8');
    for (const line of idx.split('\n')) {
      if (line.startsWith(' ') || line.length === 0) continue;
      const parts = line.trim().split(/\s+/);
      const lemma = parts[0]!;
      const pCnt = Number(parts[3]);
      const offsets = parts.slice(6 + pCnt);
      index.set(
        `${pos}:${lemma}`,
        offsets.map((o) => `${pos}:${o}`),
      );
    }
    // ---- data.<pos>: offset lex_filenum ss_type w_cnt(word lex_id)* p_cnt (ptr...)* ...
    const data = readFileSync(join(dir, `data.${pos}`), 'utf8');
    for (const line of data.split('\n')) {
      if (line.startsWith(' ') || line.length === 0) continue;
      const parts = line.split(' ');
      const offset = parts[0]!;
      const key: SynsetKey = `${pos}:${offset}`;
      synsetCount++;
      const wCnt = parseInt(parts[3]!, 16);
      let i = 4 + wCnt * 2;
      const pCnt = Number(parts[i]);
      i += 1;
      const ext: SynsetKey[] = [];
      const hyp: SynsetKey[] = [];
      for (let p = 0; p < pCnt; p++) {
        const symbol = parts[i]!;
        const tOffset = parts[i + 1]!;
        const tPosLetter = parts[i + 2]!;
        i += 4; // symbol offset pos source/target
        const tFile = POS_LETTER_TO_FILE[tPosLetter];
        if (tFile === undefined) continue;
        const tKey: SynsetKey = `${tFile}:${tOffset}`;
        if (EXTENDED_SYMBOLS.has(symbol)) ext.push(tKey);
        if (HYPERNYM_SYMBOLS.has(symbol)) hyp.push(tKey);
      }
      if (ext.length > 0) adjacency.set(key, ext);
      if (hyp.length > 0) hyper.set(key, hyp);
    }
  }

  // Symmetrise the extended graph (pointers are stored on both synsets for
  // most relations, but lexical `+` and `\` are not always mirrored).
  for (const [k, ns] of [...adjacency.entries()]) {
    for (const n of ns) {
      const back = adjacency.get(n);
      if (back === undefined) adjacency.set(n, [k]);
      else if (!back.includes(k)) back.push(k);
    }
  }

  /** Tiny morphy-style detachment (only what the index lookup misses). */
  const DETACH: Record<WnPos, [string, string][]> = {
    noun: [['ses', 's'], ['es', ''], ['s', '']],
    verb: [['ies', 'y'], ['ed', 'e'], ['ed', ''], ['ing', 'e'], ['ing', ''], ['es', ''], ['s', '']],
    adj: [['er', ''], ['est', ''], ['er', 'e'], ['est', 'e']],
    adv: [],
  };

  const lookupOne = (lemma: string, pos: WnPos): SynsetKey[] => {
    const direct = index.get(`${pos}:${lemma}`);
    if (direct !== undefined) return direct;
    for (const [suffix, repl] of DETACH[pos]) {
      if (lemma.endsWith(suffix)) {
        const cand = index.get(`${pos}:${lemma.slice(0, lemma.length - suffix.length)}${repl}`);
        if (cand !== undefined) return cand;
      }
    }
    return [];
  };

  return {
    lookup: (lemma, pos) => {
      const poses = pos === undefined ? WN_POS : [pos];
      const out: SynsetKey[] = [];
      for (const p of poses) for (const k of lookupOne(lemma.toLowerCase(), p)) if (!out.includes(k)) out.push(k);
      return out;
    },
    neighbours: (key) => adjacency.get(key) ?? [],
    hypernyms: (key) => hyper.get(key) ?? [],
    synsetCount,
  };
}

/**
 * Shortest path length between any synset of A and any synset of B
 * (multi-source BFS over the given neighbour fn), capped. Returns Infinity
 * if no path within `maxDepth`.
 */
export function shortestPath(
  graph: WordnetGraph,
  from: readonly SynsetKey[],
  to: readonly SynsetKey[],
  maxDepth = 16,
): number {
  if (from.length === 0 || to.length === 0) return Infinity;
  const targets = new Set(to);
  for (const f of from) if (targets.has(f)) return 0;
  const visited = new Set<SynsetKey>(from);
  let frontier = [...from];
  for (let d = 1; d <= maxDepth; d++) {
    const next: SynsetKey[] = [];
    for (const k of frontier) {
      for (const n of graph.neighbours(k)) {
        if (visited.has(n)) continue;
        if (targets.has(n)) return d;
        visited.add(n);
        next.push(n);
      }
    }
    if (next.length === 0) return Infinity;
    frontier = next;
  }
  return Infinity;
}

/**
 * Upward hypernym closure with depths (BFS over @/@i), for the classical
 * common-subsumer path distance (secondary, NLTK-convention variant).
 */
export function upwardClosure(graph: WordnetGraph, from: readonly SynsetKey[]): Map<SynsetKey, number> {
  const depth = new Map<SynsetKey, number>();
  let frontier: SynsetKey[] = [];
  for (const k of from) {
    depth.set(k, 0);
    frontier.push(k);
  }
  let d = 0;
  while (frontier.length > 0) {
    d++;
    const next: SynsetKey[] = [];
    for (const k of frontier) {
      for (const h of graph.hypernyms(k)) {
        if (!depth.has(h)) {
          depth.set(h, d);
          next.push(h);
        }
      }
    }
    frontier = next;
  }
  return depth;
}

/**
 * Classical (NLTK-style) hypernym path distance between same-POS synset
 * sets: min over common subsumers of dA + dB, with a simulated per-POS fake
 * root joining taxonomy roots (fake-root path = depthToRoot(A) + 1 +
 * depthToRoot(B) + 1). Infinity when either side is empty.
 */
export function hypernymDistance(
  graph: WordnetGraph,
  a: readonly SynsetKey[],
  b: readonly SynsetKey[],
): number {
  if (a.length === 0 || b.length === 0) return Infinity;
  const ca = upwardClosure(graph, a);
  const cb = upwardClosure(graph, b);
  let best = Infinity;
  for (const [k, da] of ca) {
    const db = cb.get(k);
    if (db !== undefined && da + db < best) best = da + db;
  }
  // Simulated root: cheapest root-to-root hop. A synset is a root if it has
  // no hypernyms; its depth in the closure map is the distance to it.
  let minRootA = Infinity;
  for (const [k, da] of ca) if (graph.hypernyms(k).length === 0 && da < minRootA) minRootA = da;
  let minRootB = Infinity;
  for (const [k, db] of cb) if (graph.hypernyms(k).length === 0 && db < minRootB) minRootB = db;
  if (Number.isFinite(minRootA) && Number.isFinite(minRootB)) {
    best = Math.min(best, minRootA + 1 + minRootB + 1);
  }
  return best;
}

/** NLTK-convention path similarity: 1 / (1 + shortest path); 0 if unreachable. */
export function pathSimilarity(dist: number): number {
  return Number.isFinite(dist) ? 1 / (1 + dist) : 0;
}
