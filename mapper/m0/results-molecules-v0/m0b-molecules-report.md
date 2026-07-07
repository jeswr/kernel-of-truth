# Molecule-tier coverage delta — M0b re-classified with molecules-v0

**Date:** 2026-07-07 · **Caveat:** AGENT-JUDGED single-annotator
reclassification (Claude Fable 5) of the m0b `molecule` class only; criteria
stated in `classify-molecules-v0.py`; same epistemic status as m0b itself
(class boundaries ±few points). The committed m0b results
(`../results/m0b-report.{json,md}`) are untouched inputs.

**Inputs:** m0b top-500 content-lemma classification (TinyStories validation
split, content mass 1.71M tokens = 45.55% of all word tokens, top-500 = 80.35%
of content mass) + `data/molecules-v0` (54 molecules, all passing the §3.5
mechanical gate in `data/molecules-v0/validate.mjs`).

## Headline (% of top-500 content mass)

| class | m0b | now |
|---|---|---|
| kernel (lexicon + synonym) | 28.4 | 28.4 (unchanged) |
| plausibly profile-1-explicable | 29.8 | 29.8 (unchanged) |
| **molecule-v0 direct** (label 13.2 + synonym 3.4) | — | **16.6** |
| **explicable-with-molecules (clear)** | — | **12.9** |
| explicable-with-molecules (borderline) | — | 1.5 |
| still molecule-gated | **33.0** | **2.1** |
| out-of-scope | 8.9 | 8.9 (unchanged) |

## The new ceiling

| ceiling | content mass (top-500) | all-token (×45.55% content share) |
|---|---|---|
| old (m0b) | 58.2% | **26.5%** |
| + 54 molecules, direct only | 74.7% | 34.0% |
| **+ transitive (clear)** | **87.6%** | **39.9%** |
| + transitive (borderline band) | 89.1% | 40.6% |

- The 54 molecules directly unlock **50.3% of the molecule-gated mass**;
  counting concepts that become profile-1-explicable *given* the molecules
  (the transitive tier the escape hatch exists for), **89.3%** (93.7% with
  the borderline band).
- All-token ceiling moves from **~26% to ~40%** under the m0b convention
  (same caveats: TinyStories is the deliberately favourable domain; the
  19.65% content long tail is unclassified and skews concrete/named; the
  ceiling is expressibility, not mapper performance).
- The transitive tier is the leverage story: **hand** alone makes ~20
  manual-action lemmas explicable (pick/hold/grab/throw/catch/pull/push/…),
  **water** ~12 (swim/wet/dry/rain/river/lake/pond/sea/ice/drink/wash/splash),
  **house/child/tree** similar. This is the "molecules can then be referenced
  by future explications" effect, measured.

## What is still gated (2.1 points of top-500 mass)

Animal kinds (butterfly, mouse, duck, frog, lion, elephant, monkey, squirrel,
bee, fox), food kinds (cake, cookies, candy, apple, carrot, soup, juice,
fruit, cream, sweet), remaining colors (yellow, green, white, pink, brown),
calendar `year`, sensory kinds (smell, fluffy, shape), royalty/story
institutions (princess, fairy), and the polysemous light verb `set`. These
are next-100 material — each is cheap (one grounding note) but individually
worth ≤0.13% of mass; the steep part of the frequency curve is spent.

## Mapper-lexicon implication (measured, default untouched)

`lexicon-collisions.mjs`, using the mapper's own `buildLexicon`:

- baseline (kernel-v0 + prime exponents): 12 ambiguous surfaces (known:
  kind, little, copulas, near, inside, …)
- **+54 molecule labels: 0 new ambiguous surfaces (12 → 12)**
- +10 synonym surfaces (mom/mommy/mum/mama, dad/daddy, kid, lady, hop,
  bunny): 0 new

Adding molecules-v0 to the mapper lexicon is collision-free at the surface
level; the integration decision (and precision measurement à la M0a) is a
coordinator call — see the filed bead. Sense caveats that are NOT surface
collisions and would need the M0a false-friend treatment: `close` (near-sense
vs shut-sense), `light` (not-heavy sense), `cold` (illness sense), `run`
(operate sense) — all noted per-record in `data/molecules-v0`.

## Judgement calls that move the number most

1. **mother/father minted as molecules** (not derived from woman+birth):
   NSM molecule status is about use-as-unit, not primitiveness; the
   mom-cluster alone is 2.5% of content mass. Either way it counts toward
   the ceiling; the call affects tier attribution only.
2. **Functional artifacts classified transitively, not minted** (toy, room,
   door, bed, chair, window…): where function exhausts identity, explication
   is the honest tier. Minting them instead would shift ~6 points from
   transitive-clear to direct without changing the ceiling.
3. **hop→jump, bunny→rabbit, kid→child, lady→woman synonyms** (3.4 points
   direct): parallel to m0b's kernel-synonym class; hop is the weakest.
4. The borderline band (1.5 points) is reported separately and never merged.

Reproduce: `node data/molecules-v0/validate.mjs`, then in this directory
`python3 classify-molecules-v0.py && node lexicon-collisions.mjs` (the m0b
vocab step is unchanged — the reclassification consumes the committed m0b
report, so no corpus re-run is needed).
