# Cross-vendor review (GPT-5.6 gpt-5.6-sol, xhigh) — S3 grounding-checker prereg (Rev1)

> Verdict REVISE: 7 blocking + 2 flagged (δ_floor=+0.10 not forced/under-powered; static-grammar = narrow
> answer-span claim). All fixed in Rev2. Committed for the record. Runner: run-review.sh (codex 0.144.1).

---

# Verdict: **REVISE**

The crossed contrast is basically sound, and static GBNF can test a legitimately narrowed mask-at-the-answer-span claim. However, the margin rationale, executable power plan, inferential target, and opponent certification are not freeze-worthy yet.

## The two flagged items

1. **`δ_floor=+0.10` is not forced.**

Using the prereg’s own data generator, the cluster-level SE is about 0.0262. Independent re-simulation gives:

| C-MECH `δ_eq` | TOST power, 96×20 | TOST power, 54×36 |
|---:|---:|---:|
| .0750 | .771 | .751 |
| .0775 | .802 | .791 |
| .0800 | .830 | .820 |

Thus `.08/.0775` satisfies `δ_eq < δ_floor` and remains feasible at the stated ≥.75 gate. Under the pessimistic `τ=.10` case, `.08/.079` gives about .765 TOST power. Even keeping `δ_eq=.08`, a floor just above .08 satisfies the logical constraint. The claim that smaller floors are “not honestly powerable” is false; `+.10` is a minimum-important-effect judgment, not a mathematical consequence of TOST.

The choice materially raises the bar. Under the same simulation:

- True `μ=.12`: current `+.10` floor gives about **.61** conjunction power.
- With a `+.08` floor: about **.88**.
- At the current floor itself, C-MECH conjunction power is only about **.26**, not 50%.
- The current 80%-powered effect is indeed roughly `+.135`; with a `+.08` floor it is roughly `+.113`.

Realism is not established. Because M’s grammar is a subset of G’s and decoding is greedy, M can only improve over G when G selects a wrong option excluded by the mask. Therefore `+.135` requires at least 3.375% of all items to move wrong→correct, or 4.5% wrong→UNKNOWN. If G’s wrong rate is 5%, that means correcting 67.5% of its errors or abstaining on 90% of them. Yet GATE-0 floors only the **T-arm** wrong rate, not G’s mask-addressable error rate. Add a G-arm headroom/exposure gate and justify `+.10` as a substantive MIE—or lower it. See [margin rationale](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/s3-grounding-checker-prereg.md:330).

2. **Static per-item GBNF is valid only for the narrow answer-span claim.**

It does implement a real hard mask at the logits seam: with `(s,r)` fixed, a static grammar over the precomputed admissible objects has the same intended token-language as a dynamic hook that computes the same set at span entry.

But it tests **precomputed multiple-choice answer pruning**, not dynamic checking of model-emitted subjects, relations, or arbitrary assertions. A PASS supports:

> A per-item, store-derived closed-world answer allowlist improves fixed-slot answer selection.

It does not support a general “dynamic grounding checker” claim. The prereg partially acknowledges this at [§2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/s3-grounding-checker-prereg.md:101), so the estimand is salvageable, but every headline and readout must retain that boundary. The asserted static/dynamic equivalence should also become a mechanical prefix-by-prefix compiler-equivalence gate; it is currently a load-bearing assertion marked only as a stipulated implementation choice.

## Blocking revisions

1. **Repair the power artifact.** The pinned script’s `run()` contains no C=54 or `τ=.10` scenarios, so two published table rows are not reproducible from the cited hash. It also:

   - cites 54×36 = **1,944**, contradicting exactly `n=1,920`;
   - cannot represent unequal `m_c`;
   - uses df=95 critical values even for alternative cluster counts;
   - simulates a t-test surrogate, not the frozen sign-flip procedure;
   - cannot consume the realized disagreement layout or arm-level answer-rate floor;
   - cannot therefore perform the promised “same pinned simulation” G-P re-run.

   See [power table](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/s3-grounding-checker-prereg.md:411) and [simulation entry point](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/s3-prereg-power-sim.py:131).

2. **Define the inferential population and cluster weighting.** The claim is currently about an exhaustively evaluated frozen 1,920-item universe under deterministic greedy decoding. For that finite universe, Δ is known exactly; p-values require an unstated superpopulation or randomization basis. If inference is intended over OEWN items/concepts, pin that target and its sampling design. Also specify item-weighted versus equal-cluster estimands: these differ when `m_c` is unequal. Calling the Monte Carlo sign-flip test “exact” is unjustified without sign-exchangeability assumptions.

3. **Strengthen PRECERT/G-P.** The crossed 2×2 genuinely isolates mask source, but `ρ_item≥.25` plus disagreements in half the clusters does not guarantee the reported power. Disagreements may be concentrated in only 27 of 54 clusters, whereas the simulation spreads them iid across every cluster. G-P must simulate the frozen item×cluster disagreement table, or PRECERT needs stronger per-cluster dispersion floors. Also correct the dilution arithmetic: `+.05` corresponds to `+.167` per disagreement at ρ=.30 but **+.20** at the PRECERT floor ρ=.25; the `+.06` powered effect becomes **+.24** at ρ=.25. See [PRECERT](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/s3-grounding-checker-prereg.md:366).

4. **Make the opponent extension auditable.** PV5T is not conceptually a strawman: identical closure/compiler machinery, common gold, matched expressivity and blind authorship are the right design. But plain-v5-natural governs dictionary definitions, not the new typed fact/constraint layer. Before freeze, specify:

   - its typed schema and blind authoring prompt/inputs/order;
   - exact relation and constraint-family mappings;
   - realized closure conformance tests, not merely the same engine SHA;
   - source-quality gates for typed facts;
   - auditable “agentic-hours-equivalent” accounting.

   The current expressivity check can pass while the extension remains materially weaker. See [opponent specification](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/s3-grounding-checker-prereg.md:132).

5. **Fix GATE-0 estimation.** A 50-item pilot with at most one item per cluster cannot separately estimate `τ_cluster` from item variation, despite G-P requiring pilot-estimated τ and covariance. Either enlarge the pilot with within-cluster replication or pin a conservative variance-estimation rule.

6. **Finish KOT-HON operationalization.** The core is correctly applied: λ=3 pre-outcome, S₂/S₅, all-item denominator, silent/nonparse=wrong, answer-rate floor, and OEWN gold. But the risk–coverage curve lacks a pinned confidence/ranking score, and “reasoned versus reasonless” UNKNOWN lacks a classification rule.

7. **Family disjointness is incomplete.** Alibaba host/OpenAI N-author/Anthropic screens is useful, and final scoring is deterministic. But the kernel world-layer author’s model family is not pinned in the triad. If the explicator is Anthropic-family, the item-screen family overlaps one store author. Pin that family and make all veto screens store/source-blind, or use a disjoint seat.

## Items that pass

- The two mask simple effects hold context bytes fixed; their 50/50 average is a valid stipulated mask-source estimand. Interaction limits interpretation but does not confound identification.
- Store-independent OEWN gold avoids differential oracle favour. Eligibility conditional on gold being admissible under both stores does, however, restrict the claim to that common-covered slice and excludes false-negative mask harms.
- The ordered rule yields unique classifications. Superiority and equivalence are logically disjoint; harm and equivalence can overlap evidentially, but the pinned precedence resolves classification.
- No `[EXTRAPOLATION]` appears to be used as a downstream premise. The false “smaller floors are unpowerable” assertion and the unverified static/dynamic equivalence are the load-bearing tagging problems.

## Maintainer micro-decisions

- **M-1:** not scientifically load-bearing; operational authorization only.
- **M-2:** **load-bearing** to opponent fairness and must be resolved before freeze.
- **M-3:** **conditionally load-bearing**; using the fallback changes the host estimand and requires the full pilot/GATE-0/power sequence to be rerun before a new freeze.
- **M-4:** **load-bearing** to blindness and gold provenance. Reusing OEWN is defensible if the temporal/item-blind chain is certified, but it cannot remain an unresolved comfort decision at freeze.