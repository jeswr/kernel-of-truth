/**
 * SCALE-1 S0 stage 2 — full CK-UFO sidecar typing (ck-ufo-scale/1 shape,
 * design §2.3) via the design §4.1 deterministic classification cascade.
 *
 * HONESTY HEADER (the imported-vs-inferred split, stated up front):
 * WordNet 3.1 asserts NO native UFO commitments. The ONLY source-asserted
 * UFO-relevant structure is the instance flag (instanceHypernym, introduced
 * by Princeton in WN 2.1) → denotation_level=individual. EVERYTHING ELSE in
 * these sidecars is cascade stage-3/4 inference by pinned rules over source
 * structure (lexicographer files + hypernym closure), or `underdetermined`.
 * Per design §4.3, `underdetermined` is measured, not treated as an error.
 *
 * Cascade stages used here (design §4.1):
 *   1. explicit imported commitment  → instanceHypernym only.
 *   2. endorsed crosswalk            → none exist for WordNet; unused.
 *   3. rule inference (hard)         → pinned lexFile→category crosswalk rows
 *                                       marked 'hard'; kind/rigidity rules.
 *   4. soft candidate                → role/phase/relator anchor-closure rules
 *                                       and contentious lexFile rows.
 *   5. underdetermined               → default.
 *
 * All rules are pure functions of the pinned lexical-wn31 extraction; anchor
 * synsets are resolved deterministically and pinned in the output report.
 * The lexFile→UFO crosswalk itself is [STIPULATED], not source truth.
 *
 * Output: out/n<N>/ufo.jsonl + out/n<N>/typing-report.json.
 */

import { writeFileSync } from 'node:fs';
import { join } from 'node:path';
import {
  ensureDir,
  loadAllSynsets,
  loadConcepts,
  nowMs,
  outDirFor,
  targetN,
  writeJson,
  type LexRecord,
} from './common.js';

type Status = 'source-asserted' | 'rule-inferred' | 'soft-candidate' | 'underdetermined';

interface Field {
  value: string;
  status: Status;
  warrant: string[];
}

// --- Pinned lexFile → ontic_category crosswalk [STIPULATED] -----------------
// 'hard' rows become rule-inferred commitments; 'soft' rows become candidates.
const LEXFILE_CATEGORY: Record<string, { cat: string; grade: 'hard' | 'soft' }> = {
  'noun.animal': { cat: 'object', grade: 'hard' },
  'noun.plant': { cat: 'object', grade: 'hard' },
  'noun.person': { cat: 'object', grade: 'hard' },
  'noun.object': { cat: 'object', grade: 'hard' },
  'noun.body': { cat: 'object', grade: 'hard' },
  'noun.food': { cat: 'object', grade: 'hard' },
  'noun.substance': { cat: 'object', grade: 'hard' },
  'noun.artifact': { cat: 'object', grade: 'hard' },
  'noun.group': { cat: 'object', grade: 'soft' }, // collectives; social-object contention
  'noun.location': { cat: 'object', grade: 'soft' }, // vs region; contested
  'noun.event': { cat: 'event', grade: 'hard' },
  'noun.act': { cat: 'event', grade: 'hard' },
  'noun.process': { cat: 'event', grade: 'hard' },
  'noun.phenomenon': { cat: 'event', grade: 'soft' },
  'noun.attribute': { cat: 'quality', grade: 'hard' },
  'noun.shape': { cat: 'quality', grade: 'soft' },
  'noun.state': { cat: 'mode', grade: 'soft' },
  'noun.feeling': { cat: 'mode', grade: 'soft' },
  'noun.motive': { cat: 'mode', grade: 'soft' },
  'noun.cognition': { cat: 'mode', grade: 'soft' },
  'noun.relation': { cat: 'relator', grade: 'soft' },
  'noun.communication': { cat: 'social-object', grade: 'soft' },
  'noun.possession': { cat: 'social-object', grade: 'soft' },
  'noun.quantity': { cat: 'region', grade: 'soft' }, // UFO quality regions/quantities
  'noun.time': { cat: 'region', grade: 'soft' },
  // noun.Tops → underdetermined (absent from table)
};

// verbs: event hard, except stative → mode soft (states, not occurrents)
// adjectives (a/s): quality soft (many are relational/modal, not quality universals)
// adverbs: underdetermined

// --- Pinned anchor lemma lists for Role/Phase candidates [STIPULATED] -------
const ROLE_ANCHOR_LEMMAS = [
  'worker', 'professional', 'leader', 'expert', 'relative',
  'participant', 'contestant', 'communicator', 'entertainer', 'creator',
];
const PHASE_ANCHOR_LEMMAS = ['juvenile', 'adult', 'young', 'larva', 'embryo', 'adolescent'];
const ANCHOR_LEXFILES = new Set(['noun.person', 'noun.animal', 'noun.Tops']);

const KIND_LEXFILES = new Set([
  'noun.animal', 'noun.plant', 'noun.substance', 'noun.body',
  'noun.artifact', 'noun.food', 'noun.object',
]);

function subtreeSizes(all: Map<string, LexRecord>): Map<string, number> {
  // Iterative post-order over hyponym edges; WordNet noun hyponymy is a DAG
  // (multiple inheritance exists), so memoised DFS counts reachable sets
  // approximately (sum over children double-counts shared descendants — fine:
  // only used to RANK anchor candidates deterministically).
  const memo = new Map<string, number>();
  const size = (urn: string): number => {
    const hit = memo.get(urn);
    if (hit !== undefined) return hit;
    memo.set(urn, 1); // cycle guard (defensive; hyponymy should be acyclic)
    const rec = all.get(urn);
    let s = 1;
    if (rec) {
      for (const a of rec.axioms) {
        if (a.rel === 'hyponym' && all.has(a.target)) s += size(a.target);
      }
    }
    memo.set(urn, s);
    return s;
  };
  for (const urn of all.keys()) size(urn);
  return memo;
}

function resolveAnchors(
  all: Map<string, LexRecord>,
  sizes: Map<string, number>,
  lemmas: readonly string[],
): Map<string, string> {
  // lemma → URN of the noun synset in ANCHOR_LEXFILES containing that lemma
  // with the LARGEST hyponym subtree; ties broken by URN ASC. Deterministic.
  const resolved = new Map<string, string>();
  for (const lemma of lemmas) {
    let best: { urn: string; size: number } | null = null;
    for (const [urn, rec] of all) {
      if (!urn.includes(':n-')) continue;
      if (!ANCHOR_LEXFILES.has(rec.annotations.lexFile)) continue;
      if (!rec.annotations.lemmas.some((l) => l.toLowerCase() === lemma)) continue;
      const s = sizes.get(urn) ?? 1;
      if (best === null || s > best.size || (s === best.size && urn < best.urn)) best = { urn, size: s };
    }
    if (best !== null) resolved.set(lemma, best.urn);
  }
  return resolved;
}

/** Set of all hypernym/instanceHypernym ancestors of urn in the full graph. */
function ancestors(all: Map<string, LexRecord>, urn: string): Set<string> {
  const seen = new Set<string>();
  const stack = [urn];
  while (stack.length > 0) {
    const u = stack.pop()!;
    const rec = all.get(u);
    if (!rec) continue;
    for (const a of rec.axioms) {
      if ((a.rel === 'hypernym' || a.rel === 'instanceHypernym') && !seen.has(a.target)) {
        seen.add(a.target);
        stack.push(a.target);
      }
    }
  }
  return seen;
}

const U = (warrant: string[] = []): Field => ({ value: 'underdetermined', status: 'underdetermined', warrant });

function main(): void {
  const n = targetN();
  const t0 = nowMs();
  const outDir = outDirFor(n);
  ensureDir(outDir);

  const all = loadAllSynsets();
  const concepts = loadConcepts(n);
  const sizes = subtreeSizes(all);
  const roleAnchors = resolveAnchors(all, sizes, ROLE_ANCHOR_LEMMAS);
  const phaseAnchors = resolveAnchors(all, sizes, PHASE_ANCHOR_LEMMAS);
  const roleAnchorSet = new Set(roleAnchors.values());
  const phaseAnchorSet = new Set(phaseAnchors.values());

  const lines: string[] = [];
  const split: Record<string, Record<Status, number>> = {};
  const bump = (field: string, s: Status): void => {
    split[field] ??= { 'source-asserted': 0, 'rule-inferred': 0, 'soft-candidate': 0, underdetermined: 0 };
    split[field]![s]++;
  };
  const catCounts: Record<string, number> = {};
  const sortCounts: Record<string, number> = {};

  for (const rec of concepts) {
    const lexFile = rec.annotations.lexFile;
    const isInstance = rec.axioms.some((a) => a.rel === 'instanceHypernym');
    const anc = ancestors(all, rec.id);

    // denotation_level — the ONLY field with any source-asserted values.
    const denotation: Field = isInstance
      ? { value: 'individual', status: 'source-asserted', warrant: ['wn31:instanceHypernym'] }
      : { value: 'type', status: 'rule-inferred', warrant: ['rule:non-instance-synset⇒type (WordNet does not assert typehood)'] };

    // ontic_category
    let ontic: Field;
    if (rec.pos === 'v') {
      ontic = lexFile === 'verb.stative'
        ? { value: 'mode', status: 'soft-candidate', warrant: ['rule:verb.stative⇒state/mode candidate'] }
        : { value: 'event', status: 'rule-inferred', warrant: [`rule:verb-synset(${lexFile})⇒event [STIPULATED crosswalk]`] };
    } else if (rec.pos === 'a') {
      ontic = { value: 'quality', status: 'soft-candidate', warrant: ['rule:adjective⇒quality candidate (relational/modal adjectives not separable from structure)'] };
    } else if (rec.pos === 'r') {
      ontic = U(['adverb: no UFO category rule']);
    } else {
      const row = LEXFILE_CATEGORY[lexFile];
      ontic = row
        ? {
            value: row.cat,
            status: row.grade === 'hard' ? 'rule-inferred' : 'soft-candidate',
            warrant: [`crosswalk:${lexFile}→${row.cat} (${row.grade}) [STIPULATED]`],
          }
        : U([`no crosswalk row for ${lexFile}`]);
    }

    // sortality
    let sortality: Field;
    if (isInstance) {
      sortality = { value: 'non-sortal', status: 'rule-inferred', warrant: ['rule:individual-denotation⇒not-a-sortal-universal'] };
    } else if (rec.pos === 'n' && [...phaseAnchorSet].some((a) => anc.has(a) || a === rec.id)) {
      sortality = { value: 'phase', status: 'soft-candidate', warrant: ['rule:hyponym-of-phase-anchor [STIPULATED anchors]'] };
    } else if (rec.pos === 'n' && [...roleAnchorSet].some((a) => anc.has(a) || a === rec.id)) {
      sortality = { value: 'role', status: 'soft-candidate', warrant: ['rule:hyponym-of-role-anchor [STIPULATED anchors]'] };
    } else if (rec.pos === 'n' && KIND_LEXFILES.has(lexFile)) {
      sortality = { value: 'kind', status: 'rule-inferred', warrant: [`rule:${lexFile}∈KIND_LEXFILES∧¬instance⇒kind [STIPULATED]`] };
    } else {
      sortality = U(['WordNet structure cannot separate kind/role/phase here']);
    }

    // rigidity — derived from sortality at matching confidence.
    let rigidity: Field;
    if (sortality.value === 'kind') rigidity = { value: 'rigid', status: 'rule-inferred', warrant: ['rule:kind⇒rigid'] };
    else if (sortality.value === 'role' || sortality.value === 'phase')
      rigidity = { value: 'anti-rigid', status: 'soft-candidate', warrant: [`rule:${sortality.value}-candidate⇒anti-rigid candidate`] };
    else rigidity = U();

    // identity / dependence — WordNet supplies neither; underdetermined across the board.
    const identity = U(['WordNet provides no identity criteria']);
    const dependence = U(['WordNet provides no dependence axioms (antonym/similarTo are lexical)']);

    const relatorPattern: Field =
      ontic.value === 'relator'
        ? { value: 'relator-candidate-unmediated', status: 'soft-candidate', warrant: ['noun.relation: mediation structure absent from source'] }
        : U();
    const eventPattern: Field =
      ontic.value === 'event' && ontic.status === 'rule-inferred'
        ? { value: 'occurrent-candidate', status: 'soft-candidate', warrant: ['no participant/valency structure in WordNet'] }
        : U();

    bump('denotation_level', denotation.status);
    bump('ontic_category', ontic.status);
    bump('sortality', sortality.status);
    bump('rigidity', rigidity.status);
    bump('identity', identity.status);
    bump('dependence', dependence.status);
    catCounts[`${ontic.value}/${ontic.status}`] = (catCounts[`${ontic.value}/${ontic.status}`] ?? 0) + 1;
    sortCounts[`${sortality.value}/${sortality.status}`] = (sortCounts[`${sortality.value}/${sortality.status}`] ?? 0) + 1;

    lines.push(
      JSON.stringify({
        schema: 'ck-ufo-scale/1',
        concept: rec.id,
        source_record: 'kot-lex/1 (data/lexical-wn31; content-addressed via source pin in its manifest)',
        denotation_level: denotation,
        ontic_category: ontic,
        sortality,
        rigidity,
        identity: { provider: identity.value, status: identity.status, warrant: identity.warrant },
        dependence: { inheres_in: [], existentially_depends_on: [], externally_depends_on: [], status: dependence.status, warrant: dependence.warrant },
        relator_pattern: relatorPattern,
        event_pattern: eventPattern,
        disposition_pattern: U(['no dispositional evidence in WordNet']),
        reference_ufo_commitment: 'ck-ufo-scale/1 candidate layer only; NOT endorsed',
        provenance: { cascade: 'design §4.1 stages 1/3/4/5', typer: 'poc/scale typing.ts', deterministic: true },
        review: { status: 'unreviewed', note: 'S0 pilot; no human audit sample yet' },
      }),
    );
  }

  writeFileSync(join(outDir, 'ufo.jsonl'), lines.join('\n') + '\n');

  const total = concepts.length;
  const pct = (x: number): string => ((100 * x) / total).toFixed(2) + '%';
  const splitPct = Object.fromEntries(
    Object.entries(split).map(([f, s]) => [
      f,
      Object.fromEntries(Object.entries(s).map(([k, v]) => [k, `${v} (${pct(v)})`])),
    ]),
  );
  const report = {
    stage: 'typing',
    epistemicStatus:
      'MEASURED split over STIPULATED rules. Imported (source-asserted) UFO structure in WordNet = the instance flag ONLY; all category/sortal/rigidity values are inferred candidates or underdetermined. No human audit yet (design §4.3 audit is a later-rung gate).',
    n: total,
    importedVsInferredSplit: splitPct,
    onticCategoryOutcomes: catCounts,
    sortalityOutcomes: sortCounts,
    roleAnchorsResolved: Object.fromEntries(roleAnchors),
    phaseAnchorsResolved: Object.fromEntries(phaseAnchors),
    crosswalk: LEXFILE_CATEGORY,
    wallSeconds: (nowMs() - t0) / 1000,
  };
  writeJson(join(outDir, 'typing-report.json'), report);
  console.log(`typing: ${total} sidecars; split:`, JSON.stringify(splitPct, null, 1).slice(0, 1200));
}

main();
