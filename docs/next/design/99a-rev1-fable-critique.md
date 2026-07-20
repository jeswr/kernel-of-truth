# Fable independent adversarial critique — 99a Revision 1

> **Critique of `docs/next/design/kernel-construction-methodology-proposal-99a.md` (Rev1,
> 2026-07-20), performed as the bead's prescribed next stage (Fable independent critique →
> source-verify [SV] → maintainer). Analysis only: nothing edited, committed, registered,
> frozen, or run. Proposed items referenced as `PROPOSED-CRIT-*`; no `ASM-<number>` ids
> minted. The Rev1 was treated as third-party work; the GPT-5.6 review
> (`poc/gpt56-review/99a-proposal-review/last-message.json`) and every load-bearing
> [MEASURED] citation in Rev1 were independently re-read at source before this critique.**

Tag discipline for this critique's own load-bearing claims:
[MEASURED] — checked in this repository during this critique, file cited.
[LIT-BACKED] — external literature (used nowhere load-bearing below).
[STIPULATED] — my design/judgement call.
[EXTRAPOLATION] — direction-only, never a premise.

## Verdict

**NEEDS-REV2-THEN-SOURCE-VERIFY.**

Rev1 genuinely landed the five review fixes — I checked each against the review text and
the proposal body, and none is merely claimed (§"What Rev1 got right"). But the revision
introduces one structural defect the review did not anticipate (the text-deflation
dominance it advertises is statistically unenforced — Finding 1), leaves the maintainer's
circularity worry re-enterable through the endorsement gate itself (Finding 2), and
presents its prior-setting evidence one-sidedly (Finding 4). These are targeted repairs,
not a redesign: the three-property separation, the A2 ablation, the precedence-matrix
idea, and the verified-proposer frame all survive this critique.

## Findings

### Finding 1 — CRITICAL — The precedence matrix's text-deflation dominance is structurally unenforced; row 9 is a back-door for H-GRAPH

**Claim under attack:** §4.8 row 3 ("text deflation dominates every constructed-arm
victory") plus the self-check assertion that H-GRAPH is "subordinate to arms T/T′."

**Why it is wrong/weak.** Dominance on paper is only dominance if the dominant row can
actually fire. Four design choices jointly make row 3 the *hardest* verdict to reach:

1. **Power asymmetry [MEASURED: §4.6 text].** The power requirement ("≥90% power for the
   +0.08 effect") is pinned *only* for the H−A2 superiority contrast. No power target
   exists anywhere for the H-TEXT ±0.03 TOST or the ±0.05 retention TOST. A ±0.03
   equivalence margin generically demands substantially more information than a +0.08
   superiority margin at matched error rates; a study sized for the latter will
   predictably leave the former inconclusive. [STIPULATED — standard power arithmetic;
   exact ratio depends on the composite's variance, which is precisely why it must be in
   the pre-freeze simulation.]
2. **Margin asymmetry [MEASURED: §4.1/§4.8].** The *dominant* hypothesis is held to the
   *tightest* margin in the document (±0.03), while constructed-arm retention gets ±0.05
   and the graph win needs only +0.08. Tighter TOST = harder to prove equivalence = the
   deck is stacked against the verdict the proposal claims dominates.
3. **Conjunctive cheapness [MEASURED: §4.8 kill rule].** Deflation requires T′/T cheaper
   "in authoring, tokens, FLOPs, **and** maintenance" — a four-way conjunction in which
   "maintenance" is not measurable within KBUILD-0's horizon at all. One stipulated-
   ambiguous axis blocks deflation forever.
4. **The row-9 reroute [MEASURED: §4.8 row 9].** When T/T′ equivalence is inconclusive —
   the *expected* outcome under (1)–(3) — "constructed-arm verdicts stand scoped." So H
   can be reported "H-GRAPH supported" via row 5 not because it beat the text control but
   because the text control was never given the power to speak. That is exactly the
   back-door the demotion was supposed to close.

**Failure scenario.** 96 concepts sized for +0.08; H−A2 lower CI = +0.09; T′-vs-H TOST
inconclusive at ±0.03 (CI [−0.06, +0.01]); maintenance cost "unclear." Matrix output:
row 5, "H-GRAPH supported (scoped)." K-NULL's lesson — the cheap control dominates —
never got tested with teeth, yet the graph route advances.

**Concrete fix (PROPOSED-CRIT-1).** (a) Extend the §4.6 power simulation to require ≥90%
power for the H-TEXT TOST at its registered margin, with the same INSTRUMENT-INVALID rule
at unreachable power (or widen the deflation margin to ±0.05 with justification — but then
say so and accept the symmetry). (b) Change row 9's consequence: inconclusive T-equivalence
blocks *adoption* of any constructed arm (fidelity results reported, adoption withheld,
one preregistered escalation targeted at the T-contrast), instead of letting constructed
verdicts stand. (c) Replace the four-axis conjunction with a single pre-pinned
lifecycle-cost composite measurable within the study, with "maintenance" either
operationalised (e.g. cost of one pinned revision cycle) or dropped from the decision rule
and reported descriptively.

### Finding 2 — MAJOR — The §1.2 endorsement gate admits promotion on model endorsements alone; the maintainer's circularity worry re-enters at the decisive gate

**Claim under attack:** §1.2 condition 5: "a model endorsement can never be the **sole**
endorsement for promotion above `ModelAuthored`."

**Why it is weak.** "Never sole" is satisfied by **two** model endorsers from two
different families with zero human or institutional endorsement. [MEASURED: §1.2 text —
no clause requires any non-model endorser.] The proposal itself concedes, in §2 row (c),
that "cross-model consensus can still reflect shared training data" — but that caveat is
never carried into §1.2, where it matters most. Cross-family separation buys role
independence and idiom independence; it does not buy prior independence, because frontier
families are trained on heavily overlapping corpora. [STIPULATED — and Rev1's own §2(c)
cell asserts the same.] So the operative anti-circularity mechanism — the independent
gate that makes the drafter a "verified proposer" rather than a "source of truth" — can
degenerate into models agreeing with models. That is precisely the maintainer's "the model
just spits out what it thinks things should be like" worry, one level up.

**Failure scenario.** Sol drafts a record; two cross-family models (evidence-blind,
role-independent, threshold met) endorse the fluent-but-subtly-wrong clause that all three
families share as a corpus prior. Promotion above `ModelAuthored` occurs with no human in
the loop; the record is now "canonical" under §1.1 test 1.

**Concrete fix (PROPOSED-CRIT-2).** Add to §1.2 condition 5: promotion above
`ModelAuthored` requires at least one qualified **human or sector-authority** endorsement
(or, for formal-sector records, a mechanical proof/model-check); model endorsements can
raise confidence and force abstention but never jointly suffice. Carry the shared-corpus
correlation caveat from §2(c) into §1.2 explicitly.

### Finding 3 — MAJOR — The canonicality operational test is vacuous-or-false under the softened reproducibility rule

**Claim under attack:** §1.1 test 1: "re-running the procedure on the pinned inputs
returns the same record identity (per the softened reproducibility rule, §1.3)."

**Why it is wrong.** §1.3 criterion 4 (correctly) concedes that stochastic LLM steps are
not re-runnable to the same bytes and softens to captured-output reproducibility. But the
canonicality test *inherits* that softening by reference, which leaves it with no content
for any construction path containing a stochastic step: if "re-running" means
re-generating, the test is false by the proposal's own criterion 4; if it means replaying
the captured transcript, the test is trivially satisfied by *any* hash-pinned accepted
output whatsoever, and "exactly one record" is a tautology of pinning, not a property of
the procedure. [MEASURED: §1.1/§1.3 texts.] The review demanded distinct, operational
tests; test 1 as written is not operational — it cannot fail.

**Concrete fix (PROPOSED-CRIT-3).** Split generation from selection. The *generation*
step may be stochastic and captured-reproducible (criterion 4 as written). The
*selection/promotion* step — the map from (candidate set, evidence packet, endorsement
objects) to the one normative record — must be a **deterministic, replayable function**,
and the canonicality test applies to *that* function: same candidates + same endorsements
→ same selected record, byte-checked. This preserves the softening where it is honest and
restores falsifiability where canonicality lives.

### Finding 4 — MAJOR — One-sided evidence curation in §0b, and an untagged extrapolation on the K-NULL bridge

**Claims under attack:** §0b's five prior-setting rows; §3.2's "K-NULL strengthens that
objection with repository data"; self-check item 6 ("no [MEASURED] on a choice").

**Why it is weak.** The [MEASURED] *numbers* all check out — I verified each at source
(K-NULL 0.565×, plain nominally more accurate, TOST within 0.05 SEOI
[MEASURED: `docs/next/analysis/knull-ufo-dual-model-reconcile-fable.md` A1]; Framework-G
13/50 [MEASURED: `data/haiku-tier/s1-experiments/s1-report.md`]; X1 enrichment ≈1.01,
p≈0.58 [MEASURED: `reports/lit-primitives-grounding-priorart.md` §6]; E8 ρ=.386/.360,
p=.0001, ext1 not replicated [MEASURED: E8 verdict + ext1 JSON]). Three problems remain:

1. **The K-NULL bridge is an untagged [EXTRAPOLATION].** knull-v2's own reconcile
   quarantines its scope: the tested mechanism "consumes only the canonical answer
   string," and the record explicitly "says nothing about mechanisms that actually
   *consume* content (entailment-style checking, rules-line inference, transfer)"
   [MEASURED: reconcile A1]. KBUILD-0 Stage 2 scores ENTAILED/CONTRADICTED/UNDERDETERMINED
   claims against evidence — an entailment-style, content-consuming mechanism, i.e.
   exactly what the K-NULL envelope excludes. Rev1 does carry the mechanism sentence, but
   then §3.2 still uses K-NULL as the load-bearing motivator that plain text "plausibly
   dominates" in the *construction* setting. The numbers are [MEASURED]; the transfer of
   the dominance conclusion across the mechanism envelope is [EXTRAPOLATION] and must be
   tagged as such (Rev1's self-check claims [EXTRAPOLATION] appears exactly once — that
   count is wrong once this bridge is tagged honestly). Also: the 0.565× figure is
   "descriptive by design under ASM-1085" [MEASURED: reconcile A1] — a caveat the proposal
   drops.
2. **RULES-2 is omitted.** The repository's one [MEASURED] pro-content datum — RULES-2
   PASS, audit CONFIRMED, primary LB +0.316, content-drivenness secondary passed
   [MEASURED: `registry/verdicts/rules-2.json`] — does not appear in §0b, §6, or anywhere.
   Its own claim cap ("engine-materialised entailments derivable from EITHER rules
   source…, NEVER kernel-specific value") means it is *not* a kernel vindication, but a
   prior-setting section that includes every deflationary measured result and excludes
   the one content-matters result (with its cap) is curated, not honest. The reconcile
   doc itself states the "content can matter" half is "carried entirely by RULES-2"
   [MEASURED: reconcile A1].
3. **The X1 null is cited above its own source's weight.** The prior-art report reads its
   own enrichment null as a **ceiling/saturation artifact** ("when ~97% of eligible
   content words are in the Core, no subset can be 'enriched'") and classes the specific
   null INSTRUMENT-LIMITED [MEASURED: `reports/lit-primitives-grounding-priorart.md`
   §6/§ summary table]. Rev1 presents it flatly as "dictionary structure did not
   independently ratify NSM primes" — true as stated, but the instrument could not have
   detected ratification, which is a materially weaker datum than the sentence implies.

**Concrete fix (PROPOSED-CRIT-4).** Add RULES-2 (with its cap verbatim) to §0b and §6;
tag the §3.2 K-NULL→construction bridge [EXTRAPOLATION] (it may still motivate the
demotion — motivating a *hypothesis* with an extrapolation is legitimate; presenting it
as "[MEASURED] repository data strengthening the objection" is not); carry the
descriptive-by-design status of 0.565× and the X1 ceiling-artifact caveat inline.

### Finding 5 — MAJOR — H-GRAPH as operationalised cannot test the methodology (b) it purports to decide; arm B is under-defined on nonce packets

**Claim under attack:** §3.2/§4.3 (arm B, arm H) and the §3.2 direction note that on
H-GRAPH failure "the programme … drops graph construction entirely."

**Why it is weak.** Methodology (b) as characterised in §2 is dictionary-**scale**
convergence: grounding kernels, MinSets, FCA lattices over thousands of interlinked
human-authored sense entries. In KBUILD-0, each nonce packet contains three synthetic
renderings of one micro-world rule; a "deterministic sense graph" over that material is a
packet-local toy with none of the structure (large-N convergence, cycle census,
cross-source reconciliation) that makes (b) interesting. [MEASURED: §4.2/§4.3 texts.]
What does a "dictionary graph" over three same-rule renderings even contain — and under
what frozen extraction rule? Arm B is not constructible as described without answering
this, and whatever the answer is, H-vs-A2 then measures "does a packet-local relation
digest help compilation," not "does dictionary-graph convergence constrain construction."
A clean H-vs-A2 null therefore cannot license "drop graph construction entirely," and a
win cannot license the (b) route either. [STIPULATED]

**Concrete fix (PROPOSED-CRIT-5).** (a) Specify arm B's extraction rule on packet
material concretely, or admit arm B is only meaningful on the natural stratum (where real
dictionary structure exists) and scope it there. (b) Rescope H-GRAPH's verdict wording to
"packet-local graph constraint during compilation"; state explicitly that (b)'s
discovery/inventory/audit roles (§2 row b, "Proposed role") are untouched by any KBUILD-0
outcome. (c) Delete or rescope the "drops graph construction entirely" direction note —
even flagged [EXTRAPOLATION], its scope is wrong, not just its certainty.

### Finding 6 — MAJOR — The PACKET-IDENTIFIABILITY gate's "deterministic checker" is under-specified and in tension with the renderer-separation gate

**Claim under attack:** §4.7 gate 1 ("a deterministic checker verifies, per claim, that
the packet's **rendered evidence** entails/contradicts/underdetermines the claim") and
its interaction with gate 3 (separate renderer families) and gate 2 (10% paraphrase audit
at ≥95%).

**Why it is weak.** A deterministic checker of entailment over *free natural-language
renderings* does not exist; gate 8 (correctly) bars LLMs from gold-adjacent judgements,
so the checker must operate on a typed intermediate representation upstream of rendering.
But then the gate certifies that the packet's *intended semantics* determine the label —
not that the *text the constructors actually see* does. The only guard on the
semantics→text step is gate 2's 10% sampled paraphrase audit at a 95% bar, so up to ~5%
misrendered items on a 10% sample can pass, and a rendering-loss item is semantically
identifiable yet textually underdetermined: constructors are then scored wrong for
correct packet-relative abstention — the exact failure the gate was built to prevent,
one layer down. Conversely, if the renderings are made template-rigid enough for a truly
text-level deterministic check, gate 3's "separate renderer families" and template-motif
bounds become fig leaves, because rigid templates force motif overlap. The two gates
fight; the proposal doesn't say which one wins. [STIPULATED — from the gate texts,
§4.7 1–3.]

**Concrete fix (PROPOSED-CRIT-6).** State the checker's operating level explicitly: a
shared typed IR consumed by all renderer families, plus a **100% machine-verifiable
round-trip** (render → parse-back → IR-equality) on all claim-bearing evidence — not a
10% sample — with round-trip failure an INSTRUMENT-INVALID rendering defect, and gate 2's
human paraphrase audit retained for naturalness only. Then re-state gate 3's overlap
bounds as constraints on the renderers *given* round-trip success.

### Finding 7 — MAJOR — The demotion logic is applied asymmetrically: the governance architecture is "adopted" on the same evidence posture for which the graph was demoted

**Claim under attack:** §3.1 "Adopt an evidence-anchored, independently endorsed
governance architecture" (echoed in §2 row d: "**Adopted** as the governance
architecture").

**Why it is weak.** The review's demotion principle was: a recommendation whose own
strongest objection (a cheaper plain-text control) plausibly dominates it must be a
hypothesis, not a recommendation. That principle applies with equal measured force to the
record-construction enterprise as a whole: K-NULL found the kernel store *weakly
dominated* by a plain dictionary on both axes at its scope [MEASURED: reconcile A1
efficiency paragraph], and H-TEXT/row 3 exists precisely because plain text may dominate
the *best* constructed arm. Yet Rev1 demotes only the graph and "adopts" the
record+endorsement architecture. Possible defence: adoption is a governance choice made
for auditability/provenance/forkability reasons, not an empirical efficiency claim — but
§3.1 never says that, and criterion 8 explicitly makes efficiency an end-to-end Pareto
requirement the architecture has not met. As written, the proposal is vulnerable to the
same review it just absorbed. [STIPULATED]

**Concrete fix (PROPOSED-CRIT-7).** Either (a) mark §3.1 **conditionally adopted pending
the H-TEXT outcome** (adoption language survives only sectors where row 3 does not fire),
or (b) state the non-empirical grounds (provenance, audit, fork-governance, licensing)
on which the architecture is adopted *regardless* of the efficiency verdict, and concede
in §3.1 that on criterion-8 grounds it currently stands unearned. Either is honest; the
current wording is neither.

### Finding 8 — MAJOR — Two production circularity channels are unaddressed: evidence-packet assembly and the adequacy auditor

**Claim under attack:** §3.1 step 2 ("Assemble an evidence packet") and §1.1 test 2
("an evaluator-run … audit").

**Why it is weak.** (a) *Who assembles the packet is unspecified.* In KBUILD-0 the
generator makes packets, so the question is moot there — but the adopted architecture is
for production, where evidence *selection* is the widest circularity channel: a model (or
model-assisted operator) choosing which quotes enter the packet imports the model's prior
even when every selected source is human-authored, and §1.2's role-independence
conditions bind endorsers, not packet assemblers. (b) *The evidence-adequacy auditor is
unbound.* §1.1 test 2's audit is neither a gold label nor an endorsement decision, so
neither gate 8 nor §1.2 constrains it; a same-family model could run the adequacy audit
without violating any stated rule. [MEASURED: absence verified against §1.1, §1.2, §3.1,
§4.7 texts.]

**Concrete fix (PROPOSED-CRIT-8).** Extend §1.2's role-independence conditions to two
further roles: packet assembler (assembly procedure pinned; assembler ≠ drafter family;
selection provenance recorded, including candidate sources *rejected*) and adequacy
auditor (cross-family and evidence-blind-to-downstream-tests, same as endorsers).

### Finding 9 — MINOR — The fixed comparison hierarchy is under-specified

§4.6: "H → A2 → A1, first that clears **its own superiority bar**" — the bar for each
rung is never defined (superiority over what: A2, A1, A0 respectively? by which margin?),
and T′ ("rendering of the same endorsed record produced by the **winning** constructed
arm") is undefined when no arm clears any bar. [MEASURED: §4.6/§4.3 texts.]
**Fix:** define each rung's bar and comparator explicitly, and pin the fallback (e.g. "if
no arm clears, best-arm := A1 and T′ renders A1's records; deflation contrast still
runs") so H-TEXT cannot silently vanish exactly when construction is weakest — the case
where deflation is most likely true.

### Finding 10 — MINOR — Arm E carries a named-nowhere schema-familiarity confound, and "expert" is ill-defined for nonce micro-worlds

The drafter is pipeline-tuned to emit the typed record schema; human experts author it
cold under the same time budget (§4.3 E). E's fidelity ceiling and the H-HUMAN/row-4
verdict are therefore biased against humans by tooling familiarity, not semantic ability
— and row 4 sits *above* row 5 in precedence, so this bias can flip the headline verdict
in either direction. Also, sector expertise (§1.2 condition 2) has no meaning for
synthetic nonce concepts; the E-arm competence rubric needs its own definition.
[STIPULATED] Rev1 flags E-arm logistics as deferred — deferral of recruitment detail is
legitimate, but the *bias direction* must be named and countered in the design now.
**Fix:** pre-registered schema training + calibration exercises to a pinned proficiency
bar before E's scored authoring; report E fidelity both raw and post-calibration; define
E-arm competence as demonstrated calibration performance, not domain credentials.

### Finding 11 — MINOR — Gate 8 does not require renderer families to be disjoint from the drafter family

Gate 3 separates evidence-renderers from claim-renderers; gate 8 separates
drafter/host/auditor. Nothing prevents packet evidence being rendered by the drafter's
own family, letting A-arms benefit from same-family idiom familiarity — a small but free
leak, and exactly the "recognise its own idiom" failure mode §2 row (a) warns about.
[MEASURED: §4.7 gates 3/8 texts.] **Fix:** add renderer-families ⊥ drafter family (and ⊥
host family) to gate 8's pairwise-disjointness rule.

### Finding 12 — MINOR — "Cheapest-first" counts GPU cost only; a machine-only Rung 0 could kill the branch before the endorsement apparatus is stood up

Rung 1 bundles the human machinery (endorsement protocol, reviewer-reliability
calibration, crossed review, arm E authoring) with contrasts that need none of it. The
two cheapest potential branch-killers — row 2 (structured arms ≈ shuffles) and a
preliminary text-deflation signal — are computable from unreviewed machine arms plus the
deterministic evaluator alone. [STIPULATED] **Fix:** add Rung 0: A0, unreviewed-A2, B, T,
S, N, evaluator-scored, sequential futility boundary; proceed to the reviewed arms only
if Rung 0 survives rows 2–3 in preliminary form. This is the review's own
cheapest-first principle applied one step further than Rev1 took it.

### Finding 13 — MINOR — The no-cross-evidencing rule (R1b) has no enforcement mechanism

"No claim in this programme may use one property's test as evidence for another" is
declared a law but nothing operationalises it — no record field binding each promotion
decision to the test it cites, no audit/lint over claims. As-is it is an exhortation.
(For the record, pressing on the reciprocal worry: I found no place where the
*canonical* test smuggles grounding — its failure mode is vacuity, Finding 3, not
smuggling; and the nonce stratum's collapse of adequacy into groundedness is by
construction and honestly scoped in §4.2.) [MEASURED: §1.1/§4.2 texts.] **Fix:** require
every promotion/status assertion to carry a machine-checkable `property-test-cited`
field, and add a registry lint that flags any status change citing a test not matching
the property claimed.

## What Rev1 got right

Checked against the review text, not just Rev1's self-report — all five fixes are
genuinely landed, not merely claimed:

- The three-property separation (§1.1) is real and the tests are *distinct in kind*
  (governance procedure / clause-evidence audit / non-constructor world contact); my
  Findings 3 and 13 are repairs to test 1's falsifiability and the rule's enforcement,
  not to the separation itself.
- §1.2 operationalises endorsement along exactly the five axes the review demanded;
  Finding 2 is a loophole in condition 5, not a missing structure.
- The graph demotion is textually honest and complete: no upstream section still words
  the graph as a recommendation (I searched); H-GRAPH, A2, and R1d are consistent.
- KBUILD-0 absorbed every review item: A2, E, T′, packet-identifiability, leakage
  audits, oracle-rendering, adversarial packets, sector separation, Stage-1-first,
  denotational primary, 3/3/3, CI-bound gates, expanded power components, seeds, crossed
  reviewers, coverage split, rewritten independence gate, fixed hierarchy, 11-row matrix.
  The honest scope note (§4.2 — compilation, not grounding) is exactly the concession
  the review's §3 demanded and is stated without weaseling.
- §5 correctly strips the [SV] literature of load-bearing status, including the
  attribution caveat; I verified no gate or margin rests on a lit citation.
- The [MEASURED] figures I re-checked at source (K-NULL, Framework-G 13/50, X1
  enrichment, E8) are all numerically accurate as cited.

## Recommended next step

**Rev2 before source-verify.** The [SV] sweep should not run yet, because Finding 4
changes *which* claims are load-bearing (the K-NULL bridge becomes a tagged
extrapolation; RULES-2 and its cap enter the evidence base and belong in the [SV]-adjacent
verification scope). Order of work:

1. Rev2 applies Findings 1–8 (Finding 1 is blocking: the proposal's headline honesty
   claim — text deflation dominates — is currently not true of its own design). Findings
   9–13 may be folded in cheaply or explicitly deferred to pre-freeze with a named
   deferral list.
2. On the Rev1-flagged residuals: the +0.08/±0.03/±0.05 *values*, the fidelity-composite
   weighting, and the row-7 trade rule are legitimately deferrable to pre-freeze
   calibration — but the ±0.03-TOST *power requirement* (Finding 1a) and the row-9
   consequence (Finding 1b) are structural and cannot be deferred; arm-E logistics may
   defer recruitment detail but not the schema-familiarity counter-measure (Finding 10).
3. Then source-verify [SV] per the banner, then maintainer.

---

## Self-check

1. **Genuinely adversarial, not deferential?** YES — the critique attacks Rev1's own new
   structure (the precedence matrix it is proudest of is Finding 1, CRITICAL), re-derived
   every load-bearing [MEASURED] citation at source rather than trusting them, surfaced
   omitted countervailing evidence (RULES-2) the prior review also missed, and applied
   the review's demotion logic *against* the part of the proposal the review endorsed
   (Finding 7).
2. **Every finding has a concrete fix?** YES — each finding ends with a
   `PROPOSED-CRIT-*` or inline **Fix** stating the specific change.
3. **No @handle/account strings?** YES — models/roles referenced by model or pipeline
   name only.
4. **No `ASM-<number>` minted?** YES — only `PROPOSED-CRIT-1…8` labels; pre-existing
   ASM ids appear only inside verbatim quotes of existing registry records.
5. **Nothing committed/registered/frozen/run?** YES — this file is the only write; no
   git operations, no registry writes, no runs, no schedules.
6. **Proposal file NOT edited?** YES —
   `kernel-construction-methodology-proposal-99a.md` was read only.
