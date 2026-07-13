# F1-K explication — mechanical improvements (i) + (iii): report

**Author:** designer-33 · **Governance:** benchmark-blind · deterministic · `$0` ·
no git · no registry write · no freeze · no spend · colibri naming · no handles.

Implements the two mechanical recommendations in
`poc/scale/f1k-explication/pilot-review.md` §5 that reduce the ~100-concept
authoring load and order the human-review queue, and that do **not** depend on
the pending AST-lossy maintainer ruling (§5(ii)). Output:
`candidate-pool-flagged.json` (the committed `candidate-pool.json` is **not**
mutated; two new derived fields are added to a fresh copy).

Eligible pool = the **2404** `greedy_disjoint_m8` disjoint-eligible WN-aligned
concepts. Both fields are written on every one of the
28818 candidate records; the boolean flag and the
crosswalk are *scoped to the eligible pool* (`lossy_ast_detail.scoped`).

---

## (i) `lossy-AST-suspected` pre-flag

**Mechanism.** For each candidate, isolate the *definitional core* of the aligned
WN-3.1 gloss (drop example clauses after `;`, quoted usage, and parenthetical
domain tags — §1.1(4)), remove stopwords and the concept's own lemma variants
(the circular / genus-name part), and score the remaining **differentia**
vocabulary against a **primes-coverable set**:

> primes-coverable = 65 NSM prime exponents + documented allolexes/genus heads
> (110 surface forms) ∪ endorsed
> molecules-v0 labels (54) ∪ endorsed
> kernel-v0 concept labels (54)
> = **213** coverable stems.

`lossy_ast_score` = fraction of differentia content words whose vocabulary lies
**outside** the primes-coverable set. This operationalises the pilot's
semantic-adequacy finding (§4): profile-1 "renders the genus/skeleton reliably
while dropping domain differentiae (painter, walls, money, moral law,
romantic)". A high score means the differentia leans on vocabulary the 65-prime
metalanguage cannot carry, so the `kot-ast/1` rendering will likely be *lossy*.

**Result.** `lossy_ast_suspected = (score ≥ 0.5)` marks
**2280 / 2404 (94.8%)** of the
eligible pool; the eligible-pool median score is **1.0**. That
near-total flag rate is itself the finding the pilot predicted — the QA-derived
WN long tail is dominated by domain/technical differentiae, so **lossy-AST, not
mechanical validity, is the binding constraint**. The *ordering* value therefore
lives in the continuous `lossy_ast_score`, not the boolean: sorting the review
queue by `lossy_ast_score` **ascending** puts the primes-coverable-differentia
concepts (fast, likely-faithful, low weakness-note risk) first and the
domain-heavy ones (need a carried weakness note, à la kernel-v0 `KNOWN-WEAK`)
last — reviewers hit the hard AST↔prose cases (question 4) deliberately.

**Nature of the proxy (honest).** This is a *source-gloss* proxy computed
*before* authoring; the pilot's 7/15 lossy verdict was a *post-authoring*
judgment on enriched glosses. The two correlate but are not identical: e.g.
`lover`'s WN gloss ("a person who loves someone or is loved by someone") is
fully primes-coverable at the source level (score 0) yet was judged lossy only
after the *romantic/sexual* differentia was authored in. Such residual cases are
exactly what the human gate exists to catch; the pre-flag orders the queue, it
does not replace the reviewer.

---

## (iii) OBO/SUMO crosswalk seeding → `verbatim-reuse-candidate`

**Mechanism.** Exact-normalized crosswalk of OBO class labels + EXACT synonyms
(genus-differentia `definition`) and SUMO class `documentation` onto the
eligible pool's WN-3.1 lemmas, then gate each match by a mechanical rendering of
the §1.1 scholarly-definition standard (non-circular; length band
15–100 words = *meets*, 8–140
= *nearly-meets*) plus a conservative **sense-agreement guard** (≥
1 shared content token between the WN gloss and the source
definition, so a coincidental homograph label match is dropped). The surviving
match is written as `verbatim_reuse_candidate` with `source`, `source_id`, the
matched lemma, tier, `definition`, and `definition_sha256`.

Per scale-track §3.5 this is a **review candidate**, not an endorsed merge
(`status: "review-candidate"`): label similarity may *propose* a reuse but a
human must confirm same-referent alignment (§1.2) before it enters F1-K.

**Result.** **186** eligible concepts gain a
verbatim-reuse candidate — vs the pilot's **0** from
the WN-only screen, confirming the pilot's §5(iii) prediction that OBO/SUMO would
supply the reuse the WN glosses cannot.

| Split | Count |
|---|---:|
| **Total eligible with a candidate** | **186** |
| by source — OBO | 91 |
| by source — SUMO | 95 |
| by tier — meets (15–100 w) | 137 |
| by tier — nearly-meets (8–14 w) | 49 |

The reuse is concentrated in the biology/chemistry (OBO) and upper-ontology
(SUMO) verticals of the tail, exactly where fresh NSM authoring is least
tractable and a reviewed formal definition is most valuable.

---

## Projected authoring-load reduction for the ~100 scale

The verbatim-reuse rate in the eligible pool is **7.7%**
(186/2404). Applied to the ~100-concept rebuild
that is a projected **~7.7 concepts** with a ready OBO/SUMO source definition
to reuse or lightly edit instead of authoring fresh.

- Pilot blended author-side effort ≈ **30–45 min/concept** (§4), dominated by the
  lossy `kot-ast/1` iterate-to-validate loop.
- A verbatim/near-verbatim source definition removes the *prose-authoring* leg
  (~5–15 min) and shrinks the sense-fixing leg for those ~7.7 concepts; on the
  design's `~60–90 fresh + 0–5 verbatim` projection this lifts the verbatim leg
  from ≈0 to **~7.7**, i.e. a **~7.7% reduction in fresh
  prose-authoring** across the scale (the `kot-ast/1` leg is unchanged — reuse
  helps the gloss, not the lossy-AST bottleneck, which is what improvement (i)
  triages).
- The two improvements compose: sort the queue by `lossy_ast_score` ascending,
  and within that surface the `verbatim_reuse_candidate` rows first — reviewers
  clear the fast, high-confidence, source-backed concepts before spending
  question-4 budget on the domain-heavy lossy tail.

---

## Self-check

- **(i) lossy_ast_suspected:** 2280 / 2404 eligible
  (94.8%) at threshold 0.5; median score
  1.0; queue ordered by continuous `lossy_ast_score`.
- **(iii) verbatim_reuse_candidate:** 186 eligible
  concepts — OBO 91, SUMO 95
  (meets 137, nearly-meets
  49); pilot WN-only was 0.
- **Projected reduction:** ~7.7/100 concepts reuse-seeded
  (~7.7% fewer fresh prose authorings).
- **Constraints honoured:** benchmark-blind · deterministic · `$0` · no git · no
  registry write · no freeze · no spend · colibri naming · no handles ·
  committed `candidate-pool.json` **not** mutated.
