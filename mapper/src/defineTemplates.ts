/**
 * define-question mapper leg (docs/design-kot-query-define-op.md §5 — the FROZEN
 * memo). A thin, CLOSED template layer that recognises definitional questions and
 * emits a `define` kot-query/1 query (subject / candidate) for the Python engine
 * (tools/axiom/kot_axiom.py) to answer. Kept as a SEPARATE code path from
 * gold-parse so the b-cov census counts gold-parse vs mapper-parse yield
 * separately (memo §5, §7.2); this module owns the mapper-parse leg only.
 *
 * Two disciplines, inherited verbatim from mapper.ts:
 *  - ABSTAIN, never silently pick. TERM/GENUS/FILLER resolve through an injected
 *    onto-obo annotation-label index (labels are mutable annotations, OUTSIDE
 *    concept identity — the same Princeton-gloss boundary the prime mapper
 *    respects). Exactly one distinct urn:kot: URN for a label => map; more than
 *    one => ABSTAIN (label collisions are common across ~40k terms); zero =>
 *    unmapped. No word-sense resolution anywhere.
 *  - Fail-closed. REL resolves through the pinned §3.3 relation-shorthand table;
 *    a surface REL not in the closed inventory, or a shorthand not present in the
 *    injected resolved alias map, is `unmapped` (never guessed).
 *
 * The template inventory + the REL surface inventory are CLOSED, PINNED grammar
 * artefacts (versioned). Anything not matching is `unmapped`. This module invents
 * no word sense and resolves no ambiguous label; a mapper-parse query is emitted
 * only when every slot resolves to exactly one URN. The template-precision loss
 * (non-greedy TERM/GENUS boundaries, single-differentia surface coverage) is the
 * "risk the census will price" (memo §5.2) — measured there, never estimated here.
 */

/**
 * PINNED §3.3 relation-shorthand -> OBO relation IRI. MIRRORS
 * PINNED_RELATION_ALIASES in tools/axiom/kot_axiom.py and MUST stay byte-in-sync
 * with it (closed 10-value inventory over the whole GO+PO differentia corpus).
 * Exported for a cross-language sync check; resolution to a urn:kot: URN needs
 * the mint bridge and is supplied to this module via DefineIndex.relationUrns.
 */
export const PINNED_RELATION_IRI: Readonly<Record<string, string>> = {
  part_of: 'urn:onto-obo:BFO_0000050',
  regulates: 'urn:onto-obo:RO_0002211',
  positively_regulates: 'urn:onto-obo:RO_0002213',
  negatively_regulates: 'urn:onto-obo:RO_0002212',
  occurs_in: 'urn:onto-obo:BFO_0000066',
  has_part: 'urn:onto-obo:BFO_0000051',
  happens_during: 'urn:onto-obo:RO_0002092',
  participates_in: 'urn:onto-obo:RO_0000056',
  has_participant: 'urn:onto-obo:RO_0000057',
  develops_from: 'urn:onto-obo:RO_0002202',
};

/**
 * PINNED closed surface-phrase -> shorthand inventory (one bare surface per
 * shorthand; the leading "is"/"a" of a template is consumed before the REL span).
 */
export const REL_SURFACE_TO_SHORTHAND: Readonly<Record<string, string>> = {
  regulates: 'regulates',
  'positively regulates': 'positively_regulates',
  'negatively regulates': 'negatively_regulates',
  'part of': 'part_of',
  'occurs in': 'occurs_in',
  'has part': 'has_part',
  'happens during': 'happens_during',
  'participates in': 'participates_in',
  'has participant': 'has_participant',
  'develops from': 'develops_from',
};

export interface DefineDifferentia {
  readonly relation: string;
  readonly filler: string;
}

export interface DefineCandidate {
  readonly genus: readonly string[];
  readonly differentiae: readonly DefineDifferentia[];
}

export type DefineQuery =
  | { readonly op: 'define'; readonly subject: string }
  | { readonly op: 'define'; readonly subject: string; readonly candidate: DefineCandidate };

export type DefineParse =
  /** A DEFINE or DEFINE-MATCH query ready for the engine. */
  | { readonly kind: 'query'; readonly template: string; readonly query: DefineQuery }
  /** An option-stem parse ("which term means ...") — pair with each option's URN. */
  | { readonly kind: 'candidate'; readonly template: string; readonly candidate: DefineCandidate }
  /** A slot resolved to >1 distinct URN — abstain, never pick (memo §5.1). */
  | { readonly kind: 'abstain'; readonly slot: string; readonly surface: string; readonly candidates: readonly string[] }
  /** No template matched, or a slot resolved to zero / an unpinned REL. */
  | { readonly kind: 'unmapped'; readonly reason: string };

/** Injected resolution tables (built by the census; kept out of this package). */
export interface DefineIndex {
  /** Normalized onto-obo label / synonym -> distinct urn:kot: URNs (>1 => collision). */
  readonly labelToUrns: ReadonlyMap<string, readonly string[]>;
  /** Resolved §3.3 alias table: OBO relation shorthand -> urn:kot: URN. */
  readonly relationUrns: ReadonlyMap<string, string>;
}

const DEFINE_TEMPLATES: ReadonlyArray<readonly [string, RegExp]> = [
  ['what-is', /^what is (.+)$/],
  ['define', /^define (.+)$/],
  ['definition-of', /^the definition of (.+)$/],
];

const MATCH_TEMPLATES: ReadonlyArray<readonly [string, RegExp]> = [
  ['is-a-that', /^is (.+?) a (.+?) that (.+)$/],
  ['defined-as', /^(.+?) is defined as (.+?) that (.+)$/],
];

const STEM_TEMPLATE = /^which term means (.+?) that (.+)$/;

/** Leading articles stripped as a fallback if the raw label span misses (closed). */
const ARTICLES: readonly string[] = ['the ', 'an ', 'a '];

type LabelRes =
  | { readonly kind: 'urn'; readonly urn: string }
  | { readonly kind: 'abstain'; readonly urns: readonly string[] }
  | { readonly kind: 'none' };

type CandRes =
  | { readonly kind: 'ok'; readonly candidate: DefineCandidate }
  | { readonly kind: 'abstain'; readonly slot: string; readonly surface: string; readonly candidates: readonly string[] }
  | { readonly kind: 'unmapped'; readonly reason: string };

function normalize(text: string): string {
  return text
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/[?.!]+$/, '')
    .trim();
}

function resolveLabel(surfaceRaw: string, index: DefineIndex): LabelRes {
  const surface = surfaceRaw.trim();
  let urns = index.labelToUrns.get(surface);
  if (urns === undefined) {
    for (const art of ARTICLES) {
      if (surface.startsWith(art)) {
        const hit = index.labelToUrns.get(surface.slice(art.length));
        if (hit !== undefined) {
          urns = hit;
          break;
        }
      }
    }
  }
  if (urns === undefined || urns.length === 0) return { kind: 'none' };
  const distinct = [...new Set(urns)].sort();
  if (distinct.length > 1) return { kind: 'abstain', urns: distinct };
  return { kind: 'urn', urn: distinct[0]! };
}

/** Split "<REL> <FILLER>" using the closed REL inventory (longest surface first). */
function resolveRelTail(tail: string): { readonly shorthand: string; readonly filler: string } | null {
  const surfaces = Object.keys(REL_SURFACE_TO_SHORTHAND).sort((a, b) => b.length - a.length);
  for (const s of surfaces) {
    if (tail.startsWith(s + ' ')) {
      const filler = tail.slice(s.length + 1).trim();
      if (filler.length > 0) return { shorthand: REL_SURFACE_TO_SHORTHAND[s]!, filler };
    }
  }
  return null;
}

function buildCandidate(genusSurf: string, tail: string, index: DefineIndex): CandRes {
  const g = resolveLabel(genusSurf, index);
  if (g.kind === 'abstain') return { kind: 'abstain', slot: 'GENUS', surface: genusSurf, candidates: g.urns };
  if (g.kind === 'none') return { kind: 'unmapped', reason: `GENUS unresolved: ${genusSurf}` };
  const rel = resolveRelTail(tail);
  if (rel === null) return { kind: 'unmapped', reason: `REL not a pinned shorthand: ${tail}` };
  const relUrn = index.relationUrns.get(rel.shorthand);
  if (relUrn === undefined) return { kind: 'unmapped', reason: `REL shorthand not minted: ${rel.shorthand}` };
  const f = resolveLabel(rel.filler, index);
  if (f.kind === 'abstain') return { kind: 'abstain', slot: 'FILLER', surface: rel.filler, candidates: f.urns };
  if (f.kind === 'none') return { kind: 'unmapped', reason: `FILLER unresolved: ${rel.filler}` };
  return {
    kind: 'ok',
    candidate: { genus: [g.urn], differentiae: [{ relation: relUrn, filler: f.urn }] },
  };
}

/**
 * Recognise a definitional question and emit a `define` parse. Deterministic:
 * same input + index => same output. Never resolves an ambiguous label or an
 * unpinned REL; abstains / reports unmapped instead (memo §5.1).
 */
export function parseDefineQuestion(text: string, index: DefineIndex): DefineParse {
  const norm = normalize(text);

  // DEFINE (retrieve)
  for (const [name, re] of DEFINE_TEMPLATES) {
    const m = re.exec(norm);
    if (m !== null) {
      const term = m[1]!.trim();
      const t = resolveLabel(term, index);
      if (t.kind === 'urn') return { kind: 'query', template: name, query: { op: 'define', subject: t.urn } };
      if (t.kind === 'abstain') return { kind: 'abstain', slot: 'TERM', surface: term, candidates: t.urns };
      return { kind: 'unmapped', reason: `TERM unresolved: ${term}` };
    }
  }

  // DEFINE-MATCH (subject-bearing)
  for (const [name, re] of MATCH_TEMPLATES) {
    const m = re.exec(norm);
    if (m !== null) {
      const term = m[1]!.trim();
      const cand = buildCandidate(m[2]!.trim(), m[3]!.trim(), index);
      if (cand.kind !== 'ok') return cand;
      const t = resolveLabel(term, index);
      if (t.kind === 'abstain') return { kind: 'abstain', slot: 'TERM', surface: term, candidates: t.urns };
      if (t.kind === 'none') return { kind: 'unmapped', reason: `TERM unresolved: ${term}` };
      return {
        kind: 'query',
        template: name,
        query: { op: 'define', subject: t.urn, candidate: cand.candidate },
      };
    }
  }

  // Option-stem form ("which term means <GENUS> that <REL> <FILLER>"): no subject;
  // the caller pairs the candidate with each option's URN (DEFINE-MATCH per option).
  const sm = STEM_TEMPLATE.exec(norm);
  if (sm !== null) {
    const cand = buildCandidate(sm[1]!.trim(), sm[2]!.trim(), index);
    if (cand.kind !== 'ok') return cand;
    return { kind: 'candidate', template: 'which-term-means', candidate: cand.candidate };
  }

  return { kind: 'unmapped', reason: 'no template matched' };
}
