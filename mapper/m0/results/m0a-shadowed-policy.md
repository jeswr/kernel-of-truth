# Shadowed-concept ambiguity policy — analysis + flag-gated measurement (bead kernel-of-truth-30d)

**Date:** 2026-07-07 · **Author:** mapper-policy agent (Claude Fable 5) · **Status: NEEDS COORDINATOR DECISION — nothing here is adopted.**
All flags default OFF; the flagless mapper is byte-identical to v0.1.0 (re-verified: flagless re-run reproduces
`m0a-report.json` on every decision-level key and `annotation-sample.jsonl` sha-identical). The mapper sits on E1's
critical path (poc/e1 pipeline carries a bit-exact port + parity fixture): **adopting any policy below is a
pre-registration amendment the coordinator must sign before the E1 run.** poc/e1 code is untouched.

## 1. The problem, characterised

Five kernel-v0 concepts can NEVER map under the abstain-on-ambiguity policy: every surface occurrence produces a
>1-target candidate set, so the frozen rows of these concepts would receive **zero substitution-training signal in
E1**, silently shrinking the tested concept set (M0a zero-hit list; the other 6 zero-hit concepts are mere
frequency zeros, not policy shadows). Corpus = TinyStories-valid (3.79M expanded word tokens, sha `94e43181…`,
same bytes as M0a and the E1 parity fixture).

| concept | collides with | collision type | surfaces (corpus count) | shadowed mass | collateral shadow |
|---|---|---|---|---|---|
| `broken` | concept `break` | irregular-inflection (surface `broken` + lemma broken→break) | broken (919) | 919 (0.024%) | none — `break` keeps 1,324 hits via break/broke/breaking |
| `lost` | concept `lose` | irregular-inflection (lost→lose) | lost (1,058) | 1,058 (0.028%) | none — `lose` keeps 267 hits |
| `inside` | prime INSIDE | prime-exponent identity | inside (4,153), insides (1) | 4,154 (0.110%) | **prime INSIDE also 0 hits** — both sides fully shadowed |
| `near` | prime NEAR | prime-exponent identity | near (1,164), nearest (13), nearer (8) | 1,185 (0.031%) | **prime NEAR also 0 hits** |
| `kind` | prime KIND | prime-exponent identity | kind (2,341), kinds (174), kinder (7), kindest (3) | 2,525 (0.067%) | prime KIND survives only via 2-token "kind of" (400 hits) |
| **total** | | | | **9,841 (0.26%)** | |

### Hand-judged sense distribution (50 occurrences per concept, seeded reservoir 0x5EED05)

**AGENT-JUDGED (single annotator, Claude Fable 5), PENDING HUMAN ANNOTATION** — items in `../shadowed-sample.jsonl`,
judgments + stated criteria in `../make-shadowed-judgments.py` / `../shadowed-judgments.jsonl`. 95% intervals are
exact Clopper-Pearson.

| concept | correct mapping in context | verdict |
|---|---|---|
| `broken` | 43/50 (86% [73–94%]) stative → concept **broken**; 7/50 (14%) verbal perfect (all "had broken …") → concept break | majority winner exists; a static tier mislabels ~14% (~129 tokens) |
| `lost` | 24/50 (48% [34–63%]) state → **lost**; 23/50 (46% [32–61%]) transitive lose-verb; 3/50 idioms (balance/way/grip) → neither | **coin flip — no defensible static winner** (either direction ≈52% wrong) |
| `inside` | 50/50 (100% [93–100%]) spatial containment; prime and concept **sense-identical** | not polysemy — ontology duplication; any winner is sense-correct |
| `near` | 50/50 (100% [93–100%]) spatial proximity; sense-identical | same: ontology duplication |
| `kind` | 49/50 (98% [89–100%]) = 'nice/caring' — matches **neither** candidate (kernel-v0 has no such concept); 1/50 sortal | a tier would inject ~98% wrong-sense signal (~2,475 tokens) into the frozen `kind` row |

Two distinct root causes, cleanly separated by the data: **(i)** inside/near (and kind-sortal) duplicate a prime's
meaning at the ontology level — the "collision" is a modelling redundancy, not word-sense ambiguity; **(ii)**
broken/lost/kind-'nice' are genuine surface polysemy, of which only broken has a usable majority sense.

## 2. Candidate policies and their auditability costs

**(a) Sense-priority tiers** — a DECLARED rule list, each rule keyed by the EXACT ambiguous decision set (sorted
target keys) and naming a winner from that set (`src/policy.ts`). Exact-set keying fails closed: a future lexicon
change that grows a collision set silently deactivates the rule (token abstains again). The declaration is
content-addressed (`policyHash`, SHA-256 over canonical JSON incl. evidence strings) for pinning in the lexicon
artifact. *Auditability cost:* low-moderate — the abstain invariant "the mapper never resolves sense" gains a
finite, hashed, per-rule-evidenced exception list; every resolved token carries `resolvedFrom` (the original
candidate set); E1 adoption requires porting rule application to the poc/e1 python mapper + regenerating the
lexicon artifact and parity fixture.

**(b) Rename/alias the concept label surfaces** (broken→"damaged", inside→"within", …) — zero mapper-logic change,
but changes the corpus the mapper sees. *Measured cost:* alias surfaces are 1–2 orders of magnitude rarer in
TinyStories (damaged 19 vs broken 919; within 19 vs inside 4,154; nearby 538 vs near 1,185; sort/sorts 248 —
partly verbal; misplaced 0) — it mostly trades "no signal" for "almost no signal". *Auditability cost:* highest —
concept labels live in `data/kernel-v0/manifest.json`, which is pinned in the pre-registration (Common rule 2);
editing kernel-v0 data is a new pre-registration, not an amendment, and desynchronises every existing artifact.

**(c) Context-window disambiguation rules** (deterministic POS-pattern gates). In-sample audit: a 1-token-left
gate `{had|has|have} broken → break` separates broken perfectly (7/7 vs 43/43); a copula/determiner gate for lost
reaches ~90% but misses "Are **you** lost", "we are **not** lost". *Auditability cost:* high — mapping stops being
a function of the surface form (breaks the one-form-one-decision property the E1 substitution audit and the M0a
`abstentionBySurface` accounting rely on), needs a rule language specified/hashed/ported bit-exactly, and each
corpus needs its own annotation pass to re-validate the gates. More coverage than (a) is available (lost becomes
resolvable), but not needed: (a)+(d) already covers everything except lost's 1,058 tokens (0.028%).

**(d) Leave shadowed + EXCLUDE from E1's evaluated set** — do nothing, honestly. Mapper decisions unchanged;
`excludeConcepts` shrinks the DECLARED evaluated concept universe (54→49) and the E1 stats must name the excluded
five. *Auditability cost:* zero mechanism, but a real scientific cost: 3/54 frozen rows (inside, near, kind =
prime-duplicates) never receive signal AND keep shadowing their primes' tokens; E1's "content beats shuffled
content" claim then quantifies over 49 concepts, stated. Note poc/e1 already restricts its primary endpoint to
concepts attested in all seeds — (d) merely converts that silent attestation filter into a named, pre-registered
exclusion for the five policy-shadowed concepts.

## 3. Measured deltas (flag-gated M0a re-runs; same corpus bytes; baseline = published M0a)

Implemented flags: `run-m0a.mjs --policy=tiers-measured | tiers-all5 | exclude-shadowed | hybrid-recommended`
(reports land in `m0a-policy-<name>.json`; the flagless baseline files are never rewritten). Declarations +
hashes in `src/policy.ts`.

| metric | baseline | (a) tiers-measured {inside,near,broken} | (a) tiers-all5 | (d) exclude-all5 | hybrid (a)+(d) |
|---|---|---|---|---|---|
| policy sha256 | — | `1b9201c0…` | `0524eb9a…` | `a115ec99…` | `e13dc838…` |
| concept-mapped mass | 3.111% | **3.276% (+0.165pp, +6,258 tok)** | 3.371% (+0.260pp, +9,841) | 3.111% (±0) | 3.276% (+0.165pp) |
| prime-mapped mass | 13.971% | 13.971% (±0) | 13.971% (±0) | ±0 | ±0 |
| abstained mass | 4.790% | 4.625% (−0.165pp) | 4.530% (−0.260pp) | ±0 | 4.625% |
| unmapped mass | 78.13% | ±0 | ±0 | ±0 | ±0 |
| zero-hit concepts | 11/54 | 8/54 | 6/54 | 6/**49** (excluded 5 named) | 6/**52** (kind, lost named) |
| est. wrong-sense mass injected | 0 | **~129 tok** (broken 14%) | **~3,154 tok** (kind ~2,475 + lost ~550 + broken ~129) | 0 | ~129 tok |
| sense-precision of newly mapped mass | — | ~97.9% | ~67.9% | — | ~97.9% |

New collisions introduced by tiers: **none** — verified exhaustively: the policy runs remove exactly the declared
abstention surfaces (inside/insides, near/nearer/nearest, broken; +kind/kinds/kinder/kindest, lost under all5),
add no abstention surface, and leave every other concept count, the full prime distribution, and the unmapped
distribution identical. Per-rule surface inventories are recorded in each report's `tierResolutions` block.
`tiers-all5` exists to measure the naive option's cost, not to propose it.

## 4. Recommendation (one option) and trade-offs

**Recommend the hybrid: (a) restricted to the measured-defensible list {inside→inside, near→near, broken→broken}
+ (d) for {kind, lost}** (`SHADOWED_HYBRID_RECOMMENDED`, sha `e13dc838…`). Rationale:

- inside/near: the tier is not doing word-sense disambiguation at all — the candidates are sense-identical
  (100% [93–100%] of sampled occurrences); concept-beats-prime routes the signal to the rows E1 actually freezes
  (primes are ordinary trainable vocab there). It also un-shadows 5,339 tokens that today feed neither side.
- broken: 86% majority winner; the ~129 mislabeled tokens are 2.1% of the newly mapped mass — better than the
  mapper's existing measured strict concept precision (82%), so the tier does not degrade the corpus E1 sees.
- kind: any tier injects ~98% wrong-sense signal into a frozen row — strictly worse than no signal for a content
  experiment; lost: 52% wrong either way. Exclusion is the only honest treatment for these two.
- vs pure (d): pure (d) is the conservative fallback (zero mapper change, zero new code on the critical path) and
  is fully implemented; it costs 3 recoverable concepts and leaves primes INSIDE/NEAR permanently shadowed too.
- (b) is a kernel-data change (new pre-registration, near-zero corpus mass); (c) buys only `lost` beyond the
  hybrid, at the highest audit cost.

| | hybrid (a)+(d) | pure (d) |
|---|---|---|
| E1 evaluated set | 52 declared | 49 declared |
| mapper change on E1 path | yes — python port + artifact + parity fixture regen | none |
| wrong-sense mass | ~129 tok (bounded ≤26.7% of 919 at 95%) | 0 |
| primes INSIDE/NEAR | still shadowed (their tokens now feed the twin concepts) | still shadowed, feed nothing |
| honest-labelling burden | tier list + hash + agent-judged caveat in E1 report | exclusion list in E1 report |

## 5. What the pre-registration amendment must say (coordinator drafts/signs)

1. Name the five policy-shadowed concepts and the mechanism (abstain-on-ambiguity + collision inventory above).
2. If hybrid: adopt `shadowed-hybrid-recommended` (sha `e13dc838…`) — declare the 3 tier rules with their
   agent-judged evidence (50-item samples, seed 0x5EED05, pending human annotation), the ~129-token wrong-sense
   bound for `broken`, and that `kind`+`lost` are excluded from E1's evaluated concept set (52 concepts).
   Require: python-port parity fixture regenerated under the policy BEFORE the E1 run; E1 report quotes the
   policy hash next to the mapper-lexicon artifact hash.
3. If pure (d): adopt `shadowed-exclude-all5` (sha `a115ec99…`) — E1's evaluated set is 49 concepts, the five
   named as excluded-by-policy (distinct from frequency-zero attestation drops), all headline claims restated
   over 49.
4. Either way: the M0a headline numbers remain the published flagless ones; policy-run numbers are quoted only
   with their policy hash; a human annotation pass over `shadowed-sample.jsonl` supersedes the agent judgments.

Reproduce: `node mapper/m0/run-shadowed-sample.mjs <corpus> mapper/m0 && python3 mapper/m0/make-shadowed-judgments.py`
then `node mapper/m0/run-m0a.mjs <corpus> mapper/m0 --policy=<name>`.
