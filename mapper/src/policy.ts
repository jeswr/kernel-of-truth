/**
 * Flag-gated ambiguity policies for the five shadowed concepts (bead
 * kernel-of-truth-30d). DEFAULT BEHAVIOUR IS UNCHANGED: `mapText`/`mapTokens`
 * without a policy argument behave byte-identically to v0.1.0 (pure
 * abstain-and-record). Nothing in this file activates unless a caller passes
 * a policy explicitly, and NO caller on E1's critical path does — adopting
 * any policy for E1 is a pre-registration amendment the coordinator signs.
 *
 * Background (M0a): five kernel-v0 concepts can NEVER map under the abstain
 * policy because every surface occurrence produces a >1-target candidate
 * set — broken/break (inflection), lost/lose (inflection), inside/INSIDE,
 * near/NEAR, kind/KIND (prime allolexes). Their frozen rows would receive no
 * training signal in E1, silently shrinking the tested concept set. The two
 * policies here are candidates (a) and (d) of the four designed in
 * m0/results/m0a-shadowed-policy.md.
 *
 * (a) Sense-priority tiers: a DECLARED list of rules, each keyed by the
 *     EXACT ambiguous decision set (sorted target keys) it resolves and
 *     naming a winner from that set. Exact-set keying fails closed: if a
 *     future lexicon change grows a collision set, the rule silently stops
 *     firing and the token abstains again (never resolves a set nobody
 *     declared). The declaration is content-addressed via `policyHash` so a
 *     lexicon artifact can pin exactly which resolution rules produced it.
 *
 * (d) Evaluated-set exclusion: `excludeConcepts` declares concepts REMOVED
 *     from the evaluated/reported concept universe. Mapper decisions are
 *     UNCHANGED (the concepts stay shadowed; their entries keep shadowing
 *     colliding targets); only measurement denominators and the declared
 *     E1 concept set shrink. The honest do-nothing option.
 *
 * Both declarations below are CANDIDATES, evidence-stamped from the
 * agent-judged 250-item shadowed sample (m0/shadowed-judgments.jsonl,
 * seed 0x5EED05; AGENT-JUDGED, pending human annotation).
 */

import { createHash } from 'node:crypto';
import type { Target } from './lexicon.js';
import { targetKey } from './lexicon.js';

export interface PriorityRule {
  /** Exact ambiguous decision set this rule resolves: SORTED target keys. */
  readonly decisionSet: readonly string[];
  /** Winning target key; must be a member of decisionSet (fail closed). */
  readonly winner: string;
  /** Measurement provenance for the rule (sample, precision, date). */
  readonly evidence: string;
}

export interface MapperPolicy {
  /** Short policy name; goes into reports next to the hash. */
  readonly name: string;
  /** Candidate policy (a): sense-priority tiers. */
  readonly priorityTiers?: readonly PriorityRule[];
  /**
   * Candidate policy (d): concept ids excluded from the EVALUATED set.
   * Ignored by the mapper itself (decisions unchanged) — consumed by
   * measurement/reporting (m0/run-m0a.mjs) and by E1's evaluated-set
   * declaration if adopted.
   */
  readonly excludeConcepts?: readonly string[];
}

/** Canonical JSON for content-addressing: sorted keys, sorted rule order. */
function canonicalPolicy(policy: MapperPolicy): string {
  const tiers = (policy.priorityTiers ?? [])
    .map((r) => ({
      decisionSet: [...r.decisionSet].sort(),
      winner: r.winner,
      evidence: r.evidence,
    }))
    .sort((a, b) => a.decisionSet.join('|').localeCompare(b.decisionSet.join('|')));
  return JSON.stringify({
    excludeConcepts: [...(policy.excludeConcepts ?? [])].sort(),
    name: policy.name,
    priorityTiers: tiers,
  });
}

/** SHA-256 content hash of the policy declaration (order-insensitive). */
export function policyHash(policy: MapperPolicy): string {
  return createHash('sha256').update(canonicalPolicy(policy), 'utf8').digest('hex');
}

function parseTargetKey(key: string): Target {
  return key.startsWith('prime:')
    ? { kind: 'prime', prime: key.slice('prime:'.length) }
    : { kind: 'concept', conceptId: key };
}

/** Compiled tier index: exact decision-set key -> winning target. */
export type PriorityIndex = ReadonlyMap<string, Target>;

export function decisionSetKey(targets: readonly Target[]): string {
  return targets.map(targetKey).sort().join('|');
}

/**
 * Validate + compile a policy's priority tiers. Fails closed (ERR_POLICY_*)
 * on a winner outside its decision set, a degenerate (<2) set, or duplicate
 * sets. Returns an empty index for a policy with no tiers.
 */
export function compilePriorityIndex(policy: MapperPolicy): PriorityIndex {
  const index = new Map<string, Target>();
  for (const rule of policy.priorityTiers ?? []) {
    const sorted = [...rule.decisionSet].sort();
    if (sorted.length < 2) {
      throw new Error(`ERR_POLICY_DEGENERATE_SET: [${sorted.join('|')}] in ${policy.name}`);
    }
    if (!sorted.includes(rule.winner)) {
      throw new Error(
        `ERR_POLICY_WINNER_NOT_IN_SET: ${rule.winner} not in [${sorted.join('|')}] (${policy.name})`,
      );
    }
    const key = sorted.join('|');
    if (index.has(key)) {
      throw new Error(`ERR_POLICY_DUPLICATE_SET: [${key}] declared twice in ${policy.name}`);
    }
    index.set(key, parseTargetKey(rule.winner));
  }
  return index;
}

// ---------------------------------------------------------------------------
// Candidate declarations (bead kernel-of-truth-30d). NOT defaults. Evidence
// fields cite the agent-judged 250-item sample (50 per shadowed concept,
// seed 0x5EED05, m0/shadowed-judgments.jsonl, 2026-07-07 — pending human
// annotation).
// ---------------------------------------------------------------------------

const EV = 'agent-judged 50-item sample, seed 0x5EED05, 2026-07-07 (pending human annotation)';

/**
 * (a), measured-defensible subset: only rules whose winner is sense-correct
 * in ≥86% of the sampled occurrences. inside/near: 50/50 spatial sense,
 * candidates sense-identical (prime and concept denote the same relation —
 * ontology duplication, not polysemy); concept-beats-prime so the frozen E1
 * rows receive the signal. broken: 43/50 stative (7/50 verbal perfect =
 * concept break). kind (49/50 'nice' = NO candidate) and lost (24 state /
 * 23 verb / 3 idiom — a coin flip) are deliberately ABSENT: no defensible
 * winner exists; they belong to the exclusion policy instead.
 */
export const SHADOWED_TIERS_MEASURED: MapperPolicy = {
  name: 'shadowed-tiers-measured',
  priorityTiers: [
    {
      decisionSet: ['prime:INSIDE', 'urn:kernel-v0:inside'],
      winner: 'urn:kernel-v0:inside',
      evidence: `50/50 spatial containment, candidates sense-identical; ${EV}`,
    },
    {
      decisionSet: ['prime:NEAR', 'urn:kernel-v0:near'],
      winner: 'urn:kernel-v0:near',
      evidence: `50/50 spatial proximity, candidates sense-identical; ${EV}`,
    },
    {
      decisionSet: ['urn:kernel-v0:break', 'urn:kernel-v0:broken'],
      winner: 'urn:kernel-v0:broken',
      evidence: `43/50 stative vs 7/50 verbal-perfect (86% precise); ${EV}`,
    },
  ],
};

/**
 * (a), naive all-five variant (concept-beats-prime / state-beats-event for
 * the full shadowed list). Implemented so its cost is MEASURED, not argued:
 * the sample shows kind would be ~2% sense-correct and lost ~48% — run under
 * this flag for the delta table, never proposed for adoption.
 */
export const SHADOWED_TIERS_ALL5: MapperPolicy = {
  name: 'shadowed-tiers-all5',
  priorityTiers: [
    ...SHADOWED_TIERS_MEASURED.priorityTiers!,
    {
      decisionSet: ['prime:KIND', 'urn:kernel-v0:kind'],
      winner: 'urn:kernel-v0:kind',
      evidence: `49/50 'nice' sense = NO candidate correct (~2% precise) — measured cost of the naive tier; ${EV}`,
    },
    {
      decisionSet: ['urn:kernel-v0:lose', 'urn:kernel-v0:lost'],
      winner: 'urn:kernel-v0:lost',
      evidence: `24/50 state vs 23/50 verb vs 3/50 idiom (~48% precise) — measured cost of the naive tier; ${EV}`,
    },
  ],
};

/** The five permanently shadowed concept ids (M0a zero-hit, collision-caused). */
export const SHADOWED_CONCEPTS: readonly string[] = [
  'urn:kernel-v0:broken',
  'urn:kernel-v0:inside',
  'urn:kernel-v0:kind',
  'urn:kernel-v0:lost',
  'urn:kernel-v0:near',
];

/** (d): leave shadowed, exclude all five from the evaluated set. */
export const SHADOWED_EXCLUDE_ALL5: MapperPolicy = {
  name: 'shadowed-exclude-all5',
  excludeConcepts: SHADOWED_CONCEPTS,
};

/**
 * Recommended hybrid: tiers where a winner is measured defensible
 * ({inside, near, broken}), exclusion for the two where none exists
 * ({kind, lost}). ADOPTED for E1 by pre-registration Amendment A1
 * (docs/poc-design.md Phase M, coordinator-signed 2026-07-07) under the
 * preset name `a1-hybrid` below.
 */
export const SHADOWED_HYBRID_RECOMMENDED: MapperPolicy = {
  name: 'shadowed-hybrid-recommended',
  priorityTiers: SHADOWED_TIERS_MEASURED.priorityTiers ?? [],
  excludeConcepts: ['urn:kernel-v0:kind', 'urn:kernel-v0:lost'],
};

// ---------------------------------------------------------------------------
// Amendment A1 (docs/poc-design.md Phase M, signed 2026-07-07): the adopted
// E1 policy, exposed as a named preset. The preset ALIASES the declaration
// above — it does not redeclare it — so the content hash quoted in the
// amendment stays the hash of the signed declaration. Nothing here changes
// default behaviour: `mapText`/`mapTokens` without a policy argument remain
// byte-identical to v0.1.0.
// ---------------------------------------------------------------------------

/** The policy sha256 quoted in Amendment A1 (`e13dc838…`). */
export const A1_POLICY_SHA256 =
  'e13dc838ac7df709588604f7eb445082ac6776bbc83ae0415456318db504d696';

/** Preset name adopted by Amendment A1 for every E1 data build. */
export const A1_PRESET_NAME = 'a1-hybrid';

/**
 * Named policy presets for CLI/build flags (`--policy <preset>`). `a1-hybrid`
 * is the Amendment-A1 adoption of SHADOWED_HYBRID_RECOMMENDED; the other
 * names match the m0 measurement flags (run-m0a.mjs).
 */
export const POLICY_PRESETS: Readonly<Record<string, MapperPolicy>> = {
  [A1_PRESET_NAME]: SHADOWED_HYBRID_RECOMMENDED,
  'tiers-measured': SHADOWED_TIERS_MEASURED,
  'tiers-all5': SHADOWED_TIERS_ALL5,
  'exclude-shadowed': SHADOWED_EXCLUDE_ALL5,
  'hybrid-recommended': SHADOWED_HYBRID_RECOMMENDED,
};

/**
 * Resolve a policy preset by name; fails closed on unknown names. For
 * `a1-hybrid` the resolved declaration's content hash is verified against
 * the amendment's pinned sha256 — drift in the signed declaration is an
 * ERR_POLICY_A1_DRIFT, never silently honoured.
 */
export function policyPreset(name: string): MapperPolicy {
  const policy = POLICY_PRESETS[name];
  if (policy === undefined) {
    throw new Error(
      `ERR_POLICY_UNKNOWN_PRESET: '${name}' (known: ${Object.keys(POLICY_PRESETS).join(' | ')})`,
    );
  }
  if (name === A1_PRESET_NAME && policyHash(policy) !== A1_POLICY_SHA256) {
    throw new Error(
      `ERR_POLICY_A1_DRIFT: preset '${name}' hashes to ${policyHash(policy)}, ` +
        `not the Amendment-A1 pin ${A1_POLICY_SHA256}`,
    );
  }
  return policy;
}
