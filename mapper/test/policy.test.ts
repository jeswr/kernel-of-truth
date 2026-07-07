/**
 * Flag-gated ambiguity-policy tests (bead kernel-of-truth-30d).
 *
 * The load-bearing property: NO policy argument = byte-identical v0.1.0
 * abstain-and-record behaviour. Tiers fire only on exactly declared decision
 * sets and fail closed on malformed declarations; exclusion policies never
 * touch decisions at all.
 */
import assert from 'node:assert/strict';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { buildLexicon, loadManifestConcepts, type Lexicon } from '../src/lexicon.js';
import { mapText, type AnnotatedToken, type Decision } from '../src/mapper.js';
import {
  A1_POLICY_SHA256,
  A1_PRESET_NAME,
  compilePriorityIndex,
  policyHash,
  policyPreset,
  SHADOWED_CONCEPTS,
  SHADOWED_EXCLUDE_ALL5,
  SHADOWED_HYBRID_RECOMMENDED,
  SHADOWED_TIERS_ALL5,
  SHADOWED_TIERS_MEASURED,
  type MapperPolicy,
} from '../src/policy.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..', '..');
const MANIFEST = join(REPO, 'data', 'kernel-v0', 'manifest.json');

function kernelLexicon(): Lexicon {
  return buildLexicon(loadManifestConcepts(MANIFEST));
}

function decisionOf(anns: readonly AnnotatedToken[], norm: string): Decision {
  const hit = anns.find((a) => a.isWord && a.norm === norm);
  assert.ok(hit !== undefined, `token ${norm} present`);
  return hit.decision;
}

const COLLISION_SENTENCES =
  'The toy was broken. She lost her way. He went inside the box near the tree. She was kind.';

test('no policy argument: shadowed collisions still abstain (v0.1.0 behaviour)', () => {
  const lex = kernelLexicon();
  const anns = mapText(COLLISION_SENTENCES, lex);
  for (const norm of ['broken', 'lost', 'inside', 'near', 'kind']) {
    assert.equal(decisionOf(anns, norm).kind, 'abstain', `${norm} abstains by default`);
  }
});

test('exclusion policy (d) never changes decisions', () => {
  const lex = kernelLexicon();
  const plain = mapText(COLLISION_SENTENCES, lex);
  const excluded = mapText(COLLISION_SENTENCES, lex, SHADOWED_EXCLUDE_ALL5);
  assert.deepEqual(excluded, plain, 'decisions byte-identical under exclude-all5');
  assert.equal(SHADOWED_CONCEPTS.length, 5);
});

test('measured tiers resolve inside/near/broken, leave kind/lost abstained', () => {
  const lex = kernelLexicon();
  const anns = mapText(COLLISION_SENTENCES, lex, SHADOWED_TIERS_MEASURED);
  const inside = decisionOf(anns, 'inside');
  assert.ok(inside.kind === 'concept' && inside.conceptId === 'urn:kernel-v0:inside');
  assert.deepEqual(
    inside.resolvedFrom?.map((t) => (t.kind === 'prime' ? `prime:${t.prime}` : t.conceptId)).sort(),
    ['prime:INSIDE', 'urn:kernel-v0:inside'],
    'resolvedFrom preserves the abstained candidate set for audit',
  );
  assert.equal(decisionOf(anns, 'near').kind, 'concept');
  assert.equal((decisionOf(anns, 'near') as { conceptId: string }).conceptId, 'urn:kernel-v0:near');
  assert.equal(
    (decisionOf(anns, 'broken') as { conceptId: string }).conceptId,
    'urn:kernel-v0:broken',
  );
  // no defensible winner declared -> still abstain
  assert.equal(decisionOf(anns, 'kind').kind, 'abstain');
  assert.equal(decisionOf(anns, 'lost').kind, 'abstain');
  // audit trail: resolvedFrom carries the original candidate set
  const broken = decisionOf(anns, 'broken');
  assert.ok(broken.kind === 'concept' && broken.resolvedFrom !== undefined);
  assert.equal(broken.resolvedFrom.length, 2);
});

test('tiers capture inflected variants reaching the same decision set', () => {
  const lex = kernelLexicon();
  const anns = mapText('the nearest rock; insides', lex, SHADOWED_TIERS_MEASURED);
  assert.equal((decisionOf(anns, 'nearest') as { conceptId: string }).conceptId, 'urn:kernel-v0:near');
  assert.equal((decisionOf(anns, 'insides') as { conceptId: string }).conceptId, 'urn:kernel-v0:inside');
});

test('all5 tiers additionally resolve kind and lost (measured-cost variant)', () => {
  const lex = kernelLexicon();
  const anns = mapText(COLLISION_SENTENCES, lex, SHADOWED_TIERS_ALL5);
  assert.equal((decisionOf(anns, 'kind') as { conceptId: string }).conceptId, 'urn:kernel-v0:kind');
  assert.equal((decisionOf(anns, 'lost') as { conceptId: string }).conceptId, 'urn:kernel-v0:lost');
});

test('tiers never touch UNDECLARED ambiguity (copulas, little) or unambiguous hits', () => {
  const lex = kernelLexicon();
  const anns = mapText('she was happy and a little sad; he broke it', lex, SHADOWED_TIERS_ALL5);
  assert.equal(decisionOf(anns, 'was').kind, 'abstain', 'copula still abstains');
  assert.equal(decisionOf(anns, 'little').kind, 'abstain', 'little/SMALL still abstains');
  assert.deepEqual(decisionOf(anns, 'happy'), { kind: 'concept', conceptId: 'urn:kernel-v0:happy' });
  assert.deepEqual(decisionOf(anns, 'broke'), { kind: 'concept', conceptId: 'urn:kernel-v0:break' });
});

test('exact-set keying fails closed: superset decision sets do not fire', () => {
  // Declare a rule for a 2-element subset of the copula set {BE-SOMEWHERE,
  // BE-SPEC}; the real copula set matches it exactly, so build a THIRD
  // colliding target by adding a fake concept labelled "was" — the grown set
  // must NOT be resolved by the 2-element rule.
  const concepts = [...loadManifestConcepts(MANIFEST), { id: 'urn:test:was', label: 'was' }];
  const lex = buildLexicon(concepts);
  const rule: MapperPolicy = {
    name: 'test-subset-rule',
    priorityTiers: [
      {
        decisionSet: ['prime:BE-SOMEWHERE', 'prime:BE-SPEC'],
        winner: 'prime:BE-SPEC',
        evidence: 'test',
      },
    ],
  };
  const anns = mapText('she was here', lex, rule);
  const d = decisionOf(anns, 'was');
  assert.equal(d.kind, 'abstain', 'grown collision set abstains despite subset rule');
  assert.equal((d as { candidates: readonly unknown[] }).candidates.length, 3);
});

test('malformed declarations fail closed with ERR_POLICY_*', () => {
  assert.throws(
    () =>
      compilePriorityIndex({
        name: 'bad-winner',
        priorityTiers: [{ decisionSet: ['a', 'b'], winner: 'c', evidence: '' }],
      }),
    /ERR_POLICY_WINNER_NOT_IN_SET/,
  );
  assert.throws(
    () =>
      compilePriorityIndex({
        name: 'degenerate',
        priorityTiers: [{ decisionSet: ['a'], winner: 'a', evidence: '' }],
      }),
    /ERR_POLICY_DEGENERATE_SET/,
  );
  assert.throws(
    () =>
      compilePriorityIndex({
        name: 'dup',
        priorityTiers: [
          { decisionSet: ['a', 'b'], winner: 'a', evidence: '' },
          { decisionSet: ['b', 'a'], winner: 'b', evidence: '' },
        ],
      }),
    /ERR_POLICY_DUPLICATE_SET/,
  );
});

test('Amendment A1 preset: a1-hybrid resolves to the signed declaration at the pinned hash', () => {
  const p = policyPreset(A1_PRESET_NAME);
  assert.equal(p, SHADOWED_HYBRID_RECOMMENDED, 'preset ALIASES the signed declaration');
  assert.equal(policyHash(p), A1_POLICY_SHA256);
  assert.ok(A1_POLICY_SHA256.startsWith('e13dc838'), 'pin matches the sha quoted in Amendment A1');
  // the adopted policy: tiers for {inside, near, broken}, exclusion for {kind, lost}
  const winners = (p.priorityTiers ?? []).map((r) => r.winner).sort();
  assert.deepEqual(winners, [
    'urn:kernel-v0:broken',
    'urn:kernel-v0:inside',
    'urn:kernel-v0:near',
  ]);
  assert.deepEqual([...(p.excludeConcepts ?? [])].sort(), [
    'urn:kernel-v0:kind',
    'urn:kernel-v0:lost',
  ]);
  // unknown presets fail closed
  assert.throws(() => policyPreset('no-such-preset'), /ERR_POLICY_UNKNOWN_PRESET/);
});

test('policyHash: content-addressed, order-insensitive, distinct per declaration', () => {
  const reordered: MapperPolicy = {
    name: SHADOWED_TIERS_MEASURED.name,
    priorityTiers: [...SHADOWED_TIERS_MEASURED.priorityTiers!].reverse().map((r) => ({
      ...r,
      decisionSet: [...r.decisionSet].reverse(),
    })),
  };
  assert.equal(policyHash(reordered), policyHash(SHADOWED_TIERS_MEASURED));
  const hashes = new Set(
    [
      SHADOWED_TIERS_MEASURED,
      SHADOWED_TIERS_ALL5,
      SHADOWED_EXCLUDE_ALL5,
      SHADOWED_HYBRID_RECOMMENDED,
    ].map(policyHash),
  );
  assert.equal(hashes.size, 4, 'declarations are distinct');
  // evidence text is part of the addressed content (changing the claimed
  // measurement changes the hash)
  const tampered: MapperPolicy = {
    name: SHADOWED_TIERS_MEASURED.name,
    priorityTiers: SHADOWED_TIERS_MEASURED.priorityTiers!.map((r, i) =>
      i === 0 ? { ...r, evidence: 'tampered' } : r,
    ),
  };
  assert.notEqual(policyHash(tampered), policyHash(SHADOWED_TIERS_MEASURED));
});
