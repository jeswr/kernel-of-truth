# Kernel construction methodology — proposal 99a, REVISION 9

> **REVISED DRAFT — NOT A MAINTAINER SUBMISSION AND NOT A PREREG FREEZE.
> STATUS PER THE MAINTAINER'S #59 RATIFICATION (2026-07-21): the verified-proposer
> GOVERNANCE ARCHITECTURE is ADOPTED for a bounded pilot; for the confirmatory
> experiment, the MULTIPLICITY PROCEDURE is VALID — confirmed by the
> cross-vendor re-review of Rev6 (`docs/next/design/99a-rev6-xvendor-review.md`:
> "the standard 12-node graphical design is suitable to carry forward").
> Revision 7 supplied the two specification-level prerequisites that re-review
> made binding: the per-component ANALYSIS LEDGER (§4.6/R7a) and the CORRECTED
> SIM-SPEC (## SIM-SPEC, R7e). Revision 8 applies the SEVEN before-build
> corrections of the focused cross-vendor spot-check of Rev7
> (`docs/next/design/99a-rev7-simspec-spotcheck.md` — all DGM↔ledger
> consistency and spec-completeness items, NOT design changes), making the
> SIM-SPEC BUILD-READY. The (B) MOCK BUILD has since RUN
> (`poc/99a-sim/`): it validated the procedure (global-null familywise
> rejection 0.000, strong-FWER cell 0.010 CP-UB 0.0196 ≤ 0.055; zero
> design ambiguity in the confirmatory core — its A3 note) and, exactly as
> the S9 clause intends, routed ONE genuine spec defect back to design
> (A4: the S4.4 gate-calibration battery fails under the truncation-to-0
> dependence plug-in) — FIXED here as Revision 9/R9a. NEXT = the (B)
> executor re-runs the 4-cell gate-calibration mock against the R9a test
> (verify ≤ 1.25·γ) → full (B) run → re-review of the simulation
> RESULTS → preregistration. Nothing is registered, frozen,
> scheduled, or committed by this revision.**
>
> Revision 8 produced 2026-07-21 (Fable), applying the **cross-vendor GPT-5.6
> focused spot-check of Rev7's SIM-SPEC + analysis ledger**
> (`docs/next/design/99a-rev7-simspec-spotcheck.md`, verdict **TARGETED FIX
> NEEDED — 7 before-build corrections, all DGM↔ledger consistency and
> spec-completeness, NOT design changes**; the spot-check CONFIRMED-FIXED the
> Rev7 programmatic truth engine, the Monte-Carlo acceptance rule, the
> transfer circularity/adverse-direction, the gate-threshold orientation, the
> Philox/grid pins, and the Rung-0 outer Welch/nesting). Rev8 is the FINAL
> before-build pass — the graphical procedure, the 12-claim ledger, the
> weights, the transition matrix, the IUT compositions, the multiplicity
> update algorithm, and the downgrade ledger are **UNCHANGED**: (i) **ONE
> data representation** — the DGM now generates ARM-SIDE LONG-FORM
> observations Y = α_a + b_i + (ab)_{a,i} + v_s + (av)_{a,s} + u_k/w_r + ε,
> the exact registered crossed models are fitted to them, reviewer and
> consumer factors are consistent between generation and fit (reviewer on
> review-based endpoints per §4.6), and the reviewer/consumer
> assignment-rotation algorithms are PUBLISHED as explicit formulas (R8a);
> (ii) the **mixed-model inference pinned exactly** — REML with the
> nonnegativity boundary, expected-information covariance, and the
> Giesbrecht–Burns Satterthwaite formula, plus ONE named reference
> implementation with exact versions (R 4.4.1 + lme4 1.1-35.5 + lmerTest
> 3.1-3, ddf = Satterthwaite) and a pinned fixture equivalence check — the
> Rev7 "closed-form ANOVA vs generic REML" latitude is DELETED (R8b);
> (iii) the **gate test and its DGM replaced together** by a
> model-consistent crossed-binary procedure — a latent-probit
> moment-statistic with a parametric-bootstrap p-value under the pinned
> thresholded-Gaussian working model, with fully specified latent
> covariance, marginal-π mapping, test statistic, CI inversion,
> fitting-failure handling, and a MANDATED calibration battery
> (demonstrated level control); the impossible cross-stratum gate/contrast
> intended-correlation claim is resolved (dropped with an honest
> disclosure; the within-stratum adversarial pairing for C-GRAPH is
> preserved through the shared nonce concept layer) (R8c); (iv) the
> **bounded-Beta regime re-defined as a centered, unit-variance CONCEPT
> random effect applied BEFORE the S4.1 scaling** — no second outcome
> marginal, θ_j enters once (R8d); (v) the **§4.8 operational layer
> completed** — E-arm fidelity, per-arm component cost vectors,
> review-time, and cost-dominance variables added to the DGM, exact
> algorithms pinned for §4.8 rows 2 and 5–9, the row-2 shuffle-equivalence
> margin pinned, and the LCC robustness sweep REBUILT on actual PRICE
> VECTORS applied to per-arm component cost vectors so the cost decision
> can genuinely reverse sign (the sign-invariant positive-scalar sweep
> w·L̂ is retired); P1's estimand now INCLUDES the LCC filter — it is the
> deflation-ADOPTION power, stated (R8e); (vi) **Rung-0 implementation
> pins** — the integer look-size table, n_max identified with the
> configured nonce budget, the route-dataset and pilot-estimate joint
> covariance pinned, an explicit F10 termination acceptance rule + output
> declared, and ν_D(ℓ,r) computed by the R8b-pinned Satterthwaite
> implementation (R8f); (vii) **reproducibility pins** — exact
> NumPy/SciPy/Python versions, zero-based configuration and replication
> indices, and named RNG substreams with pinned draw ordering (R8g). New
> prereg rows continue the series as `PROPOSED-PREREG-ROW-99A-R8a…g`.
>
> Revision 9 produced 2026-07-21 (Fable), a FOCUSED single-defect fix from the
> (B) simulation build's defect report (`poc/99a-sim/SPEC-DEFECTS.md` item A4):
> the mock build [MEASURED] the mandated S4.4 gate-calibration battery FAILING
> at the component level (~0.075 realised rejection at γ = 0.025 vs the
> ≤ 1.25·γ = 0.031 bar) because the spec-mandated per-replication HARD
> TRUNCATION-TO-0 of the small seed/reviewer dependence estimates biases the
> null-boundary parametric bootstrap toward UNDER-dispersion — the
> anti-conservative direction. Rev9 replaces that truncation, in the null
> bootstrap ONLY, with a pinned CONSERVATIVE seed/reviewer dependence floor
> (ρ_floor = 0.15 = 1.5× the S3 planning fractions), so dependence
> mis-estimation errs toward OVER-dispersion (the super-uniform direction),
> and adds mandatory dispersion diagnostics to the battery (R9a). The same
> mock validated everything else it exercised: global-null familywise
> rejection 0.000 (CP-UB 0.005), strong-FWER cell 0.010 (CP-UB 0.0196
> ≤ 0.055), and the 12-node procedure / IUT-TOST / truth functions / grid
> coded with zero design ambiguity — so **NOTHING else changes**: the
> graphical procedure, the 12-claim ledger, weights, transition matrix,
> update algorithm, IUT/TOST compositions, margins, truth functions, and
> grid are byte-preserved. New prereg row: `PROPOSED-PREREG-ROW-99A-R9a`.
> NEXT = the (B) executor re-runs the 4-cell gate-calibration mock against
> the R9a test to verify ≤ 1.25·γ before committing to the full run.
>
> Revision 7 produced 2026-07-21 (Fable), applying the **cross-vendor GPT-5.6
> re-review of Rev6** (`docs/next/design/99a-rev6-xvendor-review.md`, verdict
> **targeted revision needed — NOT material redesign; THE MULTIPLICITY
> PROCEDURE IS NOW VALID** — Bretz 2009 correctly applied to elementary nulls,
> IUT/TOST valid, the recurring Rev5 defect "genuinely gone", Rung-0
> route-by-look Bonferroni correct, H-TEXT-FORMAT selection sound) **plus the
> four binding citation conditions of the multiplicity-citation source
> verification** (`docs/next/design/99a-rev6-citation-sv.md`, ALL-HOLD). Rev7
> is a targeted SPECIFICATION repair — the graphical procedure, the 12-claim
> ledger, the transition matrix, and the claim structure are **UNCHANGED**:
> (i) a per-component **analysis ledger** making every inferential definition
> executable (estimand stratum, observational unit, seed aggregation, model
> formula, estimator, denominator df, one-sided p, matching confidence-bound
> inversion), with the exact-binomial gate tests REPLACED by a
> crossed-design-valid test and the threshold wording corrected to "every
> confirmatory DECISION bound" (R7a); (ii) the deflation branch RENAMED
> everywhere to its accurate one-sided form — "T is noninferior to every
> candidate within m_T and has lower LCC" — with the LCC conclusion pinned as
> an operational-policy filter, never a confirmatory component (R7b);
> (iii) Rung-0's Welch–Satterthwaite formula and component degrees of freedom
> pinned exactly, the transfer bound's conditionality stated (an
> assumption/sensitivity envelope, not distribution-free), and NESTED interim
> observations mandated in the simulation (R7c); (iv) the C-FMT target stratum
> pinned (natural senses) and the H-TEXT-FORMAT result described as
> selection-valid graphical TESTING — no simultaneous-CI procedure is claimed
> (R7d); (v) the **SIM-SPEC rewritten** to simulate the FULL claimed pipeline
> (hierarchy selection, Stage-1 binding futility, Stage-2 trigger, LCC
> robustness, operational kills, crossed author-seed/reviewer/consumer
> effects), with claim truth derived PROGRAMMATICALLY from the same hypothesis
> functions the testing engine uses (the hand-maintained true-null ledger and
> its F4–F9 errors are retired), the b(r) circularity/direction, gate-copula
> sign, generator pin, and 70-cell grid fixed, and ONE coherent Monte-Carlo
> acceptance rule (exact one-sided bounds against pre-declared tolerances with
> separated planning targets) (R7e); (vi) the four `[SV]` citation conditions
> folded in: restricted-combination closure documented, component p-values
> stated super-uniform, IUT conjunctive nulls stated CONSERVATIVE (size ≤ α;
> exact α reserved for TOST components only) (R7f). New prereg rows continue
> the series as `PROPOSED-PREREG-ROW-99A-R7a…f`.
>
> Revision 6 produced 2026-07-21 (Fable), applying the maintainer-ratified (#59)
> design-strategy decision taken after the **cross-vendor GPT-5.6 re-review of
> Rev5** (`docs/next/design/99a-rev5-xvendor-review.md`, verdict **targeted
> revision needed — NOT prereg-suitable**: the non-statistical design has
> CONVERGED; the blockers are confined to the multiplicity/FWER machinery). The
> maintainer explicitly authorised SIMPLIFYING the confirmatory-claim structure
> to reach a provably valid procedure, and Rev6 takes that latitude in full:
> (i) the Rev5 bespoke atomic-graphical matrix (95 nulls in ten composite
> nodes) is **REPLACED by a 12-claim graphical procedure on ELEMENTARY
> hypotheses** in the sense of Bretz, Maurer, Brannath & Posch (2009), whose
> published strong-FWER theorem is cited and whose stated conditions are
> verified item-by-item in §4.6/R6a; the re-review's recurring defect —
> transferring full family weight while true elementary nulls remain — is
> **structurally impossible** in Rev6 because every graph node IS one
> elementary null (R6a); (ii) the simplification's price is stated openly:
> the input-channel, citation, and review increments (Rev5 nodes E4/E5/E6),
> H-HUMAN (E7), A0 canon-readiness (E9), T′-shuffle (E1b), and every
> equivalence-KILL direction are **downgraded from confirmatory to
> descriptive/operational**, each with an itemised justification (R6b);
> (iii) Rung-0 futility now covers **repeated interim looks** via an explicit
> route-by-look alpha-spending rule with the exact pilot-to-campaign transfer
> model and bound formula (§7/R6c); (iv) **H-TEXT-FORMAT names its single
> confirmatory endpoint** (Stage-2 host three-label macro-BA), with every
> candidate-arm × format contrast covered simultaneously INSIDE the
> confirmatory family, and the descriptive external-truth label gains a bound
> producer role (§4.1/§4.2/R6d); (v) the mandated FWER/power simulation is
> specified to implementation readiness in the self-contained **## SIM-SPEC**
> section (R6e). Everything the Rev5 re-review confirmed resolved — UCT
> executability, early-node gatekeeping, kill wording, Rung-0 substance — is
> **preserved untouched**. New prereg rows continue the series as
> `PROPOSED-PREREG-ROW-99A-R6a…e`.
>
> Revision 5 produced 2026-07-21 (Fable), applying the residual findings of the
> **cross-vendor GPT-5.6 RE-REVIEW of Rev4**
> (`docs/next/design/99a-rev4-xvendor-review.md`, verdict **targeted revision
> needed (converging)**; the reviewer confirms — for the third consecutive pass —
> that the governance architecture is sound to adopt for a bounded pilot, and
> states that after the four targeted fixes "the experiment should be suitable
> for preregistration": 3 MAJOR + 1 MINOR residuals, ALL applied and itemised in
> "## Revision 5 — Rev4-re-review residuals applied" below). Rev5 is the FINAL
> statistical/operational-specification pass, not a redesign: (i) **atomic
> strong-FWER control** — all 95 atomic confirmatory nulls enumerated in ten
> nodes, the complete transition matrix and update algorithm published, ALL
> initial alpha on the validity node E1 so gatekeeping is mathematical (an
> unresolved E1 leaves every other node at level zero), every four-zone label
> read from ONE node-level simultaneous confidence set at its final
> procedure-assigned level, every operative 95% threshold replaced by its
> procedure-adjusted bound, and BOTH strong-FWER behaviour and adoption-path
> power simulated under that exact implementation (R5a); (ii) **UCT
> executability completed** — natural claim count and class allocation pinned
> (nine claims, exactly 3/3/3 by generation-to-quota, with a pinned
> missing-class fallback), held-out-source-exposed claim GENERATORS separated
> from packet-only gold LABELERS, consumer assignment / carryover / rendering /
> truncation / format-competence pinned, and comparator selection made
> inferentially valid by covering every candidate-vs-T UCT contrast in E2's one
> simultaneous confidence set (R5b); (iii) **Rung-0 conditional futility
> formalised** — a simultaneous one-sided upper prediction bound per reviewed
> route on (unreviewed-route − T) + Δ_rev(route), termination permitted only
> when every bound lies in the futility region, binding-futility-only
> sequential-error accounting, the calibration pilot's human cost explicitly
> credited, and the "before any human apparatus" wording reconciled (R5c);
> (iv) the **kill-rule wording sweep finished** — a breached hard gate is a
> cannot-advance outcome, never a registered kill, and §3.2 reads "fails to
> advance or is killed" (R5d). Everything the Rev4 re-review marked resolved —
> the unconditional UCT as dominant decision task, packet-relative labeling,
> δ ≥ m zone geometry, the hurdle endpoint, and the §8.0 controlling table — is
> **preserved untouched**. New prereg rows continue the series as
> `PROPOSED-PREREG-ROW-99A-R5a…d`.
>
> Revision 4 produced 2026-07-21 (Fable), applying the residual findings of the
> **cross-vendor GPT-5.6 RE-REVIEW of Rev3**
> (`docs/next/design/99a-rev3-xvendor-review.md`, verdict **targeted revision needed
> (converging)**: Rev3 fully resolved 7 of 10 prior findings — ALL preserved intact
> here — leaving 1 ADOPTION-BLOCKER + 4 MAJOR + 1 MINOR residuals, ALL applied and
> itemised in "## Revision 4 — Rev3-re-review residuals applied" below). Rev4 is a
> TARGETED repair, not a redesign: (i) one **unconditional, executable T-source
> decision endpoint** — the held-out claim task with a single decision statistic and
> a packet-relative natural-stratum target (R4a); (ii) a **valid FWER procedure**
> (graphical gatekeeping with local alpha weights and explicit recycling) over the
> enumerated confirmatory claims, with δ ≥ m making the four zones non-overlapping
> and power re-simulated under the final procedure (R4b); (iii) a mathematically
> complete **hurdle/lexicographic non-compensatory endpoint** (R4c); (iv) Rung-0
> futility extended to unreviewed A2-IR/H on **route-specific differential review
> increments** (R4d); (v) **advance/kill/indeterminate** reconciled with the
> precedence matrix and the text rule stated uniformly as "text superior, OR
> equivalent with lower LCC" (R4e); (vi) §8 consolidated into one controlling table
> with stale rows amended in place (R4f); plus the re-review's C1 claim-narrowing
> note (graph isolation = **explicit graph materialisation/closure**). New prereg
> rows continue the series as `PROPOSED-PREREG-ROW-99A-R4a…f`.
>
> Revision 3 produced 2026-07-21 (Fable), applying the **cross-vendor GPT-5.6 review of
> Rev2** (`docs/next/design/99a-rev2-xvendor-review.md`, verdict **conditionally sound,
> not freeze-ready**: 3 CRITICAL + 6 MAJOR + 1 MINOR findings, ALL applied — itemised in
> "## Revision 3 — cross-vendor findings applied" below). The cross-vendor gate surfaced
> estimand/control defects the same-vendor loop missed: the H-vs-A2 graph contrast was
> confounded by an oracle-IR input channel (CRITICAL-1), the dominant text-deflation
> comparison lacked a common estimand — T′ was true-by-construction (CRITICAL-2), and
> the exact hidden-rule primary endpoint conflicted with correct packet-relative
> abstention (CRITICAL-3). All three are repaired here. The reviewer's endorsed
> architecture — verified-proposer governance; canonicality / evidence-adequacy /
> empirical-truth separation; deterministic vector as derived-only; human/authority
> promotion floor; A2 citation-only ablation; graph demoted to a falsifiable
> sector-scoped hypothesis; conservative ≥90%-per-equivalence-test power +
> inconclusive-blocks-adoption; two-sided evidence — is **preserved intact**. New
> prereg rows continue the series as `PROPOSED-PREREG-ROW-99A-R3a…i`.
>
> Revision 2 produced 2026-07-20 (Fable), applying the independent adversarial critique of
> Rev1 (`docs/next/design/99a-rev1-fable-critique.md`, verdict
> **NEEDS-REV2-THEN-SOURCE-VERIFY**; 1 CRITICAL, 7 MAJOR, 5 MINOR — all 13 findings
> applied, itemised in "## Revision 2 — critique fixes applied" below). Rev2 completed the
> prescribed critique loop; it was then source-verified (`99a-rev2-sv-report.md`,
> `99a-rev2-sv-report-extlit.md` — all load-bearing citations confirmed) and cross-vendor
> reviewed, producing this Revision 3.
>
> Revision 1 was produced 2026-07-20 (Fable), applying the independent GPT-5.6 soundness review
> (`poc/gpt56-review/99a-proposal-review/last-message.json`, verdict **NEEDS-FIX**) to the
> original overflow-lane draft of 2026-07-19 (`poc/gpt56-review/99a-kernel-methodology/`).
> The review's core rulings, all applied here: the **semantic-record-first / vector-derived
> reframing is SOUND and retained**; the endorsement/canonicality criteria are operationalised;
> the **graph-constraint recommendation is DEMOTED to a pre-registered hypothesis** (its own
> strongest objection — a plain-text-equivalent-cheaper K-NULL-style control — plausibly
> dominates it); KBUILD-0 is repaired (decisive citation-only-no-graph ablation,
> human-from-evidence arm, packet-identifiability gate, template-leakage audits, exact
> construction-fidelity as the PRIMARY endpoint, fixed statistics, precedence matrix); and
> the `[SV]` literature is marked supporting-only, never load-bearing.
>
> Nothing here is registered, frozen, scheduled, or committed by this revision. All prereg
> rows are PROPOSED only, labelled `PROPOSED-PREREG-ROW-99A-R1a…j` (Rev1),
> `PROPOSED-PREREG-ROW-99A-R2a…m` (Rev2, one per critique finding),
> `PROPOSED-PREREG-ROW-99A-R3a…i` (Rev3, one per cross-vendor finding),
> `PROPOSED-PREREG-ROW-99A-R4a…f` (Rev4, one per re-review residual), and
> `PROPOSED-PREREG-ROW-99A-R5a…d` (Rev5, one per Rev4-re-review residual); **no
> `ASM-<number>` ids are minted** (ids are assigned at prereg-freeze; sibling Phase-1
> revisions use the same convention). Review packaging note, acknowledged: the review file `last-message.json` is
> Markdown content in a `.json` wrapper — cosmetic only.

Tag discipline (applies to every load-bearing claim below):

- **[MEASURED]** — directly checked in this repository (result files cited inline).
- **[LIT-BACKED]** — rests on external literature; every such tag here also carries `[SV]`
  and a resolvable backing. The source-verify sweep is now COMPLETE
  (`99a-rev2-sv-report.md`, `99a-rev2-sv-report-extlit.md`: all four supporting
  literature claims and both load-bearing repository citations confirmed); the
  material nevertheless remains **supporting-only, never load-bearing** by design
  (§5 / fix 5).
- **[STIPULATED]** — a design or policy choice. Every design choice in this document is
  [STIPULATED], never [MEASURED].
- **[EXTRAPOLATION]** — direction-only; may motivate a *hypothesis* (§3.2) but is never
  used as a premise for any conclusion, verdict, or gate.

---

# Methodology proposal: build the canon from evidence, not from a model

This is a revised draft applying the cross-vendor re-review of Rev6 (procedure
confirmed VALID; specification residuals applied here as Revision 7) and the
multiplicity-citation source verification — next stage is task (B): build and
run the ## SIM-SPEC FWER/power simulation, then a re-review of its results,
then preregistration. It is not a final ruling and not yet a maintainer
submission.

**Bottom line (retained from the original, per review §1):** choose a specific hybrid
*governance architecture*, but change what is called "canonical." The canonical object is an
independently endorsed, evidence-anchored **semantic record**; the deterministic vector is a
**derived encoding** of that record. The kernel drafter proposes or compiles records,
dictionary graphs *may* constrain and audit them (now a hypothesis, §3, not a
recommendation), and model internals validate or bridge them — they never decide their
meaning. [STIPULATED]

The load-bearing question this proposal answers: is LLM-generation (a model emitting NSM
explications) the right way to construct the kernel, versus (b) dictionary-graph +
convergence / grounding-kernels, (c) extraction from model internals (SAE /
dictionary-learning), (d) principled hybrids — and is LLM-generation legitimate as a
**verified proposer** versus circular as a **source of truth**? Answer (unchanged in
direction, now properly hedged): legitimate as a verified proposer under an independent
gate; circular as a source of truth. [STIPULATED — argued from the [MEASURED] evidence
below; the graph increment specifically is an open empirical hypothesis, §3.]

## 0. Consistency with the maintainer's #56 ruling (drafter ≠ authority)

The maintainer has since chosen GPT-5.6/Sol (the pinned largekern-10k pipeline,
`docs/next/design/gpt56-draft-pipeline-large-kernel.md`) as THE kernel drafter, retiring the
Haiku Framework-G drafter. This revision treats that as what it is: a **draft-step model
choice, not a canonical-authority change**. [STIPULATED]

- Sol output is still `ModelAuthored` and still requires the independent semantic gate
  (§2 step 5) before promotion. "Sol drafts it" resolves *which model proposes*; it does
  not resolve — and must not be read as resolving — the canonical / evidence-adequate /
  grounded question of §1. [STIPULATED]
- Throughout this document, "the drafter" means the pinned drafter of record at run time
  (currently the largekern-10k Sol pipeline). Framework-G/Haiku figures are retained below
  strictly as [MEASURED] historical evidence about LLM-drafting behaviour, not as the
  pipeline under test.
- The full hybrid/graph/gate methodology question, and the ModelAuthored-still-needs-a-gate
  rigor, stand unchanged under #56.

## 0b. Repository evidence that should set the prior

- The current encoder already makes the right architectural separation: a typed explication
  is deterministically encoded by a pinned, training-free TPR/VSA construction; the vector
  is reproducible and decodable only given the kernel lexicon. This establishes
  **representation determinism, not semantic correctness**. [MEASURED:
  `docs/architecture.md` §1, `encoder/README.md`]
- The historical Haiku pipeline was more defensible than "the LLM simply invents meanings":
  pinned Wiktionary/Wikipedia inputs, mechanical gate errors fed back once, provenance
  preserved, and output correctly labelled `ModelAuthored` below endorsed tiers. Stage 1
  produced 13 legal records from 50 concepts (26% concept yield); semantic fidelity was
  assessed only by a single-agent indicative review. [MEASURED:
  `data/haiku-tier/s1-experiments/s1-report.md`, `data/haiku-tier/modelauthored-schema.md`]
- The programme's own dictionary-grounding test found 50/51 evaluable NSM primes in the
  WordNet Core, but a frequency-matched null was already ~97% Core; enrichment ≈1.01,
  p≈0.58. Dictionary structure did **not** independently ratify NSM primes — **with the
  source's own limitation carried inline (Rev2, critique Finding 4):** the source report
  reads this null as a ceiling/saturation artifact (when ~97% of eligible content words
  are already in the Core, no subset can be "enriched") and classes it
  INSTRUMENT-LIMITED; the instrument could not have detected ratification, so this is a
  weak datum, not a refutation. [MEASURED: `reports/lit-primitives-grounding-priorart.md`
  §6 and its summary table]
- E8 found kernel–SAE correspondence for GPT-2↔Pythia-160M (primary ρ=.386, partial ρ=.360,
  both permutation p=.0001) but the two SmolLM2-involving pairs did not replicate. One
  positive pair, not a model-independent canonical geometry (hook-site mismatch is a real
  confound). [MEASURED: `poc/e8/results-incoming/20260707-131303-modal/verdict-e8.md`,
  `poc/e8/results-incoming/20260707-143903-ext1-modal/results-e8-ext1.json`]
- **K-NULL sets the deflationary prior for §3 — within its mechanism envelope:** kernel
  and aligned plain-dictionary stores were equivalent within the registered margin; the
  concise plain store was nominally more accurate and used ~0.565× the verifier-side
  FLOPs (a figure that is **descriptive by design** in the pinned reconcile record, not
  a registered endpoint — caveat carried inline per critique Finding 4). The tested
  mechanism consumed aligned answer strings, not vectors or explication structure, and
  the reconcile explicitly says nothing about mechanisms that *consume* content
  (entailment-style checking, rules-line inference, transfer). [MEASURED:
  `docs/next/analysis/knull-ufo-dual-model-reconcile-fable.md`]
- **RULES-2 is the repository's one MEASURED "content-matters" datum and belongs in this
  prior (added in Rev2; critique Finding 4):** verdict PASS, cross-vendor audit
  CONFIRMED (2026-07-12); primary lift lower bound +0.316; the content-drivenness
  secondary passed (a forced-flip deranged closure did not retain the lift). Its own
  permanent claim cap is carried with it and caps it here too: any rules-2 result is
  "engine-materialised entailments (derivable from EITHER rules source on this closed
  inventory) are internalisable by a small host", **NEVER** "kernel-specific value"
  (registered-cap wording quoted with its registry ids elided). So RULES-2 shows content
  can matter on the rules line while vindicating nothing kernel-specific — and the
  K-NULL reconcile itself states that the "content can matter" half of the programme's
  evidence is carried entirely by RULES-2. [MEASURED: `registry/verdicts/rules-2.json`;
  `docs/next/analysis/knull-ufo-dual-model-reconcile-fable.md`]

These results do not say "the kernel is useless." They say determinism, source provenance,
graph convergence, and model alignment are **four different properties** and must not
masquerade as semantic grounding — and the evidence base is two-sided: the deflationary
rows (K-NULL, X1-as-limited, E8) coexist with the one capped content-matters row
(RULES-2), and a prior set from only one side would be curated, not honest. [STIPULATED —
interpretation of the [MEASURED] rows above]

## 1. Canonicality and grounding criteria (operationalised)

### 1.1 Three properties, three distinct tests `[STIPULATED — review-1 fix 2; PROPOSED-PREREG-ROW-99A-R1b]`

The original draft conflated three notions. They are separated here, each with its own
operational test; a record can hold any subset, and the record's status field must say
which:

1. **Canonical** — *selected as the normative record by a declared authority and
   procedure.* Operational test (generation/selection split — Rev2, critique Finding 3):
   the *generation* of candidate records may be stochastic and is held only to §1.3
   criterion 4 (captured-reproducible, measured-stable). The *selection/promotion* step
   — the map from (candidate set, evidence packet, endorsement objects) to the one
   normative record for (authority A, profile P, version t, sense s) — must be a
   **deterministic, replayable function**: re-running it on the same pinned candidates
   and endorsement objects returns the byte-identical selected record. Identity effects
   of input changes are split to match the two-hash design of §1.3 criterion 3 (Rev3,
   cross-vendor MINOR-9 — the Rev2 wording "changing any input changes the selection
   identity" conflicted with that design): **every** selection-input change (new
   source, new endorsement, changed procedure or tie-break) must alter the
   **evidence-release hash** (the §1.3 criterion-3 pin — Rev4 canonical term, per the
   re-review's terminology note: "decision/provenance hash" and "evidence-release
   hash" named ONE object and the synonym is retired; §8.0); the **semantic
   identity** (semantic-content hash) is altered **only when the selected normative
   content changes**. A new source or endorsement that leaves the selected normative
   content unchanged changes the evidence-release identity, never the concept.
   `[PROPOSED-PREREG-ROW-99A-R3i]` This test can fail — a selection procedure with
   discretion, hidden state, or non-replayable tie-breaks is not canonical-capable — and
   it is *not* satisfied merely by hash-pinning whatever output was accepted.
   Canonicality is a **governance fact**; it makes no claim
   about truth. A legal or institutional definition can be fully canonical when "true" is
   not even the appropriate test. `[PROPOSED-PREREG-ROW-99A-R2c]`
2. **Evidence-adequate** — *faithful to specified independent evidence.* Operational test:
   every semantic clause of the record cites resolvable evidence anchors; an
   evaluator-run (never constructor-self-scored) audit — the auditor being a **bound
   role**: cross-family with the drafter and evidence-blind to downstream test material,
   per §1.2 condition 6 (Rev2, critique Finding 8) — finds no unsupported clause, no
   contradicted clause, and abstention wherever the pinned evidence underdetermines the
   content. Scored as: unsupported-clause rate, contradicted-clause rate, calibrated
   abstention.
3. **Empirically grounded / true** — *supported by operational or observational contact
   with the relevant world.* Operational test: the record's denotation is checked against
   a measurement/decision procedure or independently labelled examples and
   counterexamples whose labels did not pass through the constructor. Consensus cannot
   confer this property; conversely its absence does not defeat canonicality for
   convention-constituted concepts.

No claim in this programme may use one property's test as evidence for another property.
[STIPULATED]

**Enforcement (Rev2, critique Finding 13):** the no-cross-evidencing rule is not left as
an exhortation. Every promotion or status assertion must carry a machine-checkable
`property-test-cited` field naming the §1.1 test it relies on, and a registry lint flags
any status change citing a test that does not match the property claimed.
[STIPULATED — PROPOSED-PREREG-ROW-99A-R2m]

### 1.2 Independent endorsement, operationalised `[STIPULATED — review-1 fix 2; PROPOSED-PREREG-ROW-99A-R1a]`

Independent endorsement is not inherently circular merely because endorsers are humans or
models: independence is about **roles, evidence, incentives, and information — not
biological versus artificial agency** (review §1). An endorsement counts as *independent*
for promotion only if all of the following are satisfied and recorded on the endorsement
object:

1. **Role independence:** the endorser is none of — the constructor (drafter model or its
   operator), an author of the pinned sources, the evaluated host model, an author of any
   gold labels, or a downstream beneficiary of the record's promotion. Model endorsers must
   additionally be from a different model family than the drafter and than any evaluated
   host, and must be evidence-blind to downstream test material.
2. **Competence and conflicts:** endorser competence for the record's sector is declared
   against a pinned rubric; conflicts of interest are declared; an endorser with an
   undeclared conflict invalidates the endorsement, not the record.
3. **Sampling, number, threshold, uncertainty:** the number of endorsers, how they are
   sampled/assigned, the agreement threshold, and the uncertainty rule (what agreement
   level counts as promotion vs abstention) are fixed **before** any endorser sees any
   candidate record. Agreement is reported with its uncertainty (e.g. a chance-corrected
   agreement statistic with a CI), never as a bare count.
4. **Disagreement handling:** on failure to reach threshold, the outcome is one of —
   explicit **fork** (both records recorded with disjoint identities), **abstention**
   (record stays `ModelAuthored`), **appeal** (one recorded round to a pre-named
   adjudicator), or **authority ruling** (for institutionally-anchored sectors only). No
   silent averaging or synthesis of disagreeing endorsements.
5. **Model-as-reviewer conditions (strengthened — Rev2, critique Finding 2):** a model
   may endorse only under (1)'s cross-family and evidence-blind conditions. Model
   endorsements can raise confidence and can force abstention, but **can never jointly
   suffice for promotion above `ModelAuthored`, in any number**. Cross-family separation
   buys role and idiom independence, not *prior* independence: frontier model families
   are trained on heavily overlapping corpora, so the §2 row (c) caveat — cross-model
   consensus can still reflect shared training data — applies here, at the decisive
   gate; "two cross-family models agree" is exactly the maintainer's circularity worry
   one level up. Promotion above `ModelAuthored` therefore additionally requires a
   human/authority floor — **strengthened in Rev3 (cross-vendor MAJOR-7: one human
   plus many correlated models is an anti-circularity minimum, not strong
   reliability): for ordinary lexical and empirical records the floor is at least TWO
   independently sampled qualified human endorsers, or one declared sector-authoritative
   body**; for other sectors the Rev2 ≥1-qualified-human-or-authority floor remains
   the absolute minimum; and for formal-sector records only, a machine-checked
   proof/model-check against the record's pinned axioms may substitute.
   [STIPULATED — PROPOSED-PREREG-ROW-99A-R2b, strengthened by R3g]
6. **Bound adjacent roles (new — Rev2, critique Finding 8):** the same role-independence
   discipline binds two production roles that are neither endorsers nor gold authors:
   (i) the **evidence-packet assembler** — the assembly procedure is pinned, the
   assembler is not the drafter model or its family, and selection provenance is
   recorded including candidate sources considered and *rejected* (evidence selection is
   the widest circularity channel: a model or model-assisted operator choosing which
   quotes enter the packet imports the model's prior even when every selected source is
   human-authored); (ii) the **evidence-adequacy auditor** (§1.1 test 2) — cross-family
   with the drafter and evidence-blind to downstream test material, exactly as endorsers
   are. [STIPULATED — PROPOSED-PREREG-ROW-99A-R2h]
7. **Anchoring and source-selection protection (new — Rev3, cross-vendor MAJOR-7):**
   (i) **Evidence-only pre-judgments:** every endorser and evidence-adequacy auditor
   first records **evidence-only, clause-level judgments from the packet alone —
   before seeing the candidate record**; these pre-judgments are hashed and pinned;
   the candidate is shown only afterwards, and the final endorsement is scored
   against the pre-candidate judgments, with divergences explained on the endorsement
   object (this bounds proposal anchoring, which reviewer visibility of the candidate
   otherwise permits). (ii) **Drafter-assisted source selection is PROHIBITED:**
   neither the drafter model nor any model of its family may propose, rank, filter,
   or summarise candidate sources for the evidence packet — extending condition 6(i)
   from "the assembler is not the drafter family" to the selection *process* itself.
   (iii) **Pinned sampling frame + dual assembly audit:** packet assembly draws from
   a pinned source sampling frame, and a pre-registered audit sample of packets is
   assembled twice by independent assemblers, with divergence reported as an
   assembly-reliability statistic. (iv) **KBUILD-0 endorsement is HUMAN-ONLY** in
   every reviewed arm, even though production permits (never-sufficient, condition 5)
   model endorsements — the experiment must not inherit the correlated-model
   confidence channel it is designed to test around.
   [STIPULATED — PROPOSED-PREREG-ROW-99A-R3g]

### 1.3 The nine criteria (revised)

A useful definition for this programme is:

> A concept representation is **canonical** only relative to a declared **sense, profile,
> authority, and version**, when a public procedure selects one normative record;
> **evidence-adequate** only when independently anchored evidence supports it; and every
> downstream encoding is reproducibly derived from it.

Write the canonical semantic record as

K_{A,P,t}(s) = (sense key, scope, typed constraints, examples, counterexamples,
dependencies, status)

where A is the authority or endorsement community, P the semantic profile, t the version,
s the sense — not merely a lemma. The vector is v = Encode_h(K_{A,P,t}(s)). A deterministic
encoder can make v canonical **relative to K**; it cannot make K true. [STIPULATED]

The criteria, with revision-1 changes marked:

1. **Sense and authority are explicit.** "Bank" without a sense is not a canonical concept.
   "Canonical for whom?" must have an answer: a standards body, domain community,
   language-use panel, formal theory, or named federation. [STIPULATED]
2. **The evidential chain terminates outside the constructor and evaluated model.**
   Acceptable anchors by sector — formal: axioms/definitions/proofs; operational:
   measurement or decision procedures; observational: independently labelled examples and
   counterexamples; institutional: an identified legal/scientific/standards authority;
   ordinary lexical: independently collected usage judgements and contrast cases.
   Dictionary prose is source evidence, but by itself is not referential grounding; the
   Harnad symbol-grounding "merry-go-round" characterisation is consistent with this but
   the criterion does not rest on it. [STIPULATED; supporting-only [LIT-BACKED][SV]]
3. **Evidence provenance is complete but distinct from semantic identity.** Two pins: a
   semantic-content hash over normative scope and constraints; an evidence-release hash
   over source revisions, anchors, derivation logs, and endorsements. Provenance and world
   facts do not silently become definitional content. [STIPULATED]
4. **Construction is captured-reproducible and measured-stable** `[revised — review-1 fix
   2; PROPOSED-PREREG-ROW-99A-R1c]`. The original "same pinned inputs and policy must
   yield the same candidate" is generally **false for API-hosted stochastic LLM steps**
   and is softened to what a possibly-stochastic construction step can actually deliver:
   (i) **captured-output reproducibility** — the accepted candidate's bytes, the full
   derivation transcript, and all inputs are hash-pinned, so the *derivation* is exactly
   replayable as a record even when the generative step is not re-runnable to the same
   bytes; (ii) **derivation hashes** — changing source set, parser, prompt, model, graph
   policy, or reviewer decision creates a new derivation/version identity; (iii)
   **rerunnable distributions and measured stability** — where the step is stochastic,
   re-sampling under the pinned policy is permitted and the **stability of the semantic
   content across re-samples, permissible paraphrases, and author models is a measured
   quantity** reported with the record, not an assumption. Deterministic stages (graph
   closure, encoder) remain held to byte-identity. [STIPULATED]
5. **Adequacy includes exclusions and uncertainty.** A record must say what does not count
   and where it abstains. Minimal negation, scope, polysemy, and near-neighbour
   counterexamples are load-bearing because the current encoder's raw geometry can treat a
   meaning-inverting edit as small [MEASURED — X1 margin evidence lineage;
   `docs/poc-design.md` Phase X]. [STIPULATED]
6. **Dependencies are auditable.** References resolve; cycles terminate in independently
   anchored records or are explicitly marked mutually stipulative. Graph reachability alone
   is not grounding. [STIPULATED]
7. **Correctness utility is independent and claim-specific.** A kernel can check whether a
   claim uses a concept consistently with an endorsed definition; it cannot establish
   "Alice is X" without world-layer evidence about Alice. Gold labels must not be generated
   from the same record the verifier consults. [STIPULATED]
8. **Efficiency is an end-to-end Pareto claim.** Count authoring and review cost, source
   acquisition, mapper errors, storage, context tokens, model parameters, FLOPs, latency,
   and accuracy. A construction earns the efficiency thesis only if it beats hash-pinned
   definition text, smaller-model-alone, and other strong controls — not merely an empty
   prompt. K-NULL is the standing warning here. [STIPULATED; K-NULL figures [MEASURED]]
9. **The method has a real way to lose.** Unsupported clauses, source conflicts, poor
   cross-source stability, failure against shuffled mappings, equivalence with plain text,
   and excessive review cost must all be capable of killing or demoting it. [STIPULATED]

These nine criteria are a **checklist, not a complete or non-circular definition** of
canonicality (review §1); §1.1's three-way separation carries the definitional weight.

## 2. Comparison of methodologies (a)–(d)

All entries in the table are [STIPULATED] assessments informed by the [MEASURED] rows of
§0b; literature-derived cells are supporting-only [LIT-BACKED][SV] and no row's verdict
rests on them (§5).

| Method | Where it bottoms out | Canonicality | Coverage, scale, cost | Falsifiability | Strongest failure mode | Proposed role |
|---|---|---|---|---|---|---|
| **(a) LLM-generated NSM explications** | Weak version: the model's learned distribution. Current repository version: pinned dictionary prose plus the model's translation of it. Neither is an independent referential anchor. | A pinned prompt/model makes the procedure inspectable, but semantic output is sensitive to sense choice, prompt, model revision, stochasticity, and repair. Mechanical legality does not imply adequacy. | Potentially broad and cheap per draft. Framework G yielded only 26% legal records in its 50-concept test [MEASURED]; semantic review becomes the likely dominant cost. | Strong if evaluated on post-cutoff nonce concepts, held-out authorities, humans, or deterministic gold. Weak or circular if a correlated LLM endorses fluent NSM-shaped output. | Fluent completion can overwrite source meaning, hide unsupported distinctions, or thin out during gate repair; the same model family can "recognise" its own idiom and fabricate validation. | **Salvageable as a compiler/proposal generator — a verified proposer. Not admissible as the canonical authority.** `ModelAuthored` is the right status (unchanged by #56, §0). |
| **(b) Dictionary graph + convergence/FCA** | Human-authored dictionary definitions and relations extracted from them: source convention, not objects or observations. | Highly reproducible once dictionaries, sense segmentation, extraction rules, edge direction, convergence rule, and tie policy are pinned — but conditional on those choices. Published dictionary studies reportedly find a ~10% Grounding Kernel and many alternative ~1% MinSets (non-uniqueness matters) [LIT-BACKED][SV — supporting-only]. An FCA lattice is unique up to isomorphism given a fixed formal context, but prose-to-incidence mapping and attribute scaling remain construction choices [LIT-BACKED][SV — supporting-only]. | Excellent lexical coverage after source/licensing and word-sense work. Deterministic recomputation cheap; high-quality relation extraction and source reconciliation are not. | Good: source holdouts, edge perturbations, alternative dictionaries, sense-level replication, downstream claim tasks. Self-reconstruction of the originating dictionary is not a valid external test. | A fixpoint can make circular prose stable without making it grounded; shared dictionary conventions or errors can converge. SCCs and MinSets identify compressibility and dependencies, not meaning or truth. | **Use for sense inventory, stable-relation discovery, molecule prioritisation, conflict detection, cycle auditing. As a *construction constraint*: a pre-registered HYPOTHESIS only (§3), not the final semantic authority and not a recommended requirement.** |
| **(c) Extract from model internals / SAEs** | The model's training data, objectives, architecture, and behaviour: grounded in what the model represents, not in what is correct. | Poor as a universal canon: learned dictionaries are subject to permutations, rotations, feature splitting/absorption, seed and site dependence; the recent SAE literature reports substantial non-identifiability and instability [LIT-BACKED][SV — supporting-only; the repository's own E8 one-positive-pair-two-nulls picture is the [MEASURED] basis]. | Broad implicit coverage, but requires model access, activations, SAE fitting, feature matching, labels. Per-model extraction scales poorly as a universal registry. | Strong if tested cross-seed, cross-site, cross-family, on held-out models and causal downstream tasks. Weak if an SAE from the target model certifies that same model's claims. | It can canonise the model's own errors and biases; "faithful to this model" confused with "true"; cross-model consensus can still reflect shared training data. | **Behavioural validation and adapter target; ALSO admissible upstream for sense discovery, coverage-gap detection, candidate generation, and causal diagnostics — provided external evidence governs promotion** (review §2 softening). **Never** use target-model internals to author or certify the definition that will verify that same model. |
| **(d) Principled hybrid (governance architecture)** | Multiple pinned human sources plus at least one operational, observational, institutional, formal, or usage anchor; an LLM compiles; independent endorsement (§1.2) decides. Whether a *graph constraint* belongs in the loop is the §3 hypothesis. | Canonical relative to a named authority/profile/version. Deterministic stages byte-reproducible; stochastic stages captured-reproducible + measured-stable (§1.3 crit. 4); disagreements become explicit forks or revisions, never hidden averaging. | More expensive per promoted record because review is real. Scale comes from tiering: unreviewed bulk stays `AxiomsOnly`/`ModelAuthored`; only reviewed records enter the canon. | Best of the four: source holdout, graph perturbation, nonce concepts, counterexamples, reviewer agreement, text nulls, shuffles, held-out-model validation attack different links. | Consensus can launder shared source bias; governance can become slow or political; review cost may erase any compression benefit — and **plain pinned text may dominate the whole construction on K-NULL evidence** (§3). | **Adopted as the governance architecture on stated non-empirical governance grounds; the constructed-record store is only conditionally adopted pending H-TEXT-SOURCE (§3.1 — Rev2, critique Finding 7; renamed Rev3).** The graph-constrained variant is **not recommended — it is hypothesis H-GRAPH (§3), to be tested against the citation-only and plain-text controls.** |

Two direct answers follow (unchanged in substance):

- **Is (a) fatally circular?** No — not when the LLM is a constrained translator from
  independently pinned evidence and its output is independently adjudicated (§1.2). Yes —
  for the canonicality claim — if the LLM's latent beliefs are the authority or if
  correlated models provide the only adequacy judgement. [STIPULATED]
- **Does (b) escape circularity?** Qualified per review §2: dictionary-graph convergence
  **does not, by convergence alone, establish external grounding**. It removes dependence
  on one generative model and reproducibly exposes source-relative lexical convention,
  dependency structure, and compressibility — real benefits, just not external truth. It
  does not manufacture a referent or make one of many possible MinSets uniquely semantic.
  [STIPULATED; the local prior-art report itself draws this distinction — [MEASURED]:
  `reports/lit-primitives-grounding-priorart.md`]

## 3. Adopted governance architecture; graph constraint DEMOTED to hypothesis `[STIPULATED — review-1 fix 3; PROPOSED-PREREG-ROW-99A-R1d]`

### 3.1 What is adopted, and on what grounds (a proposal, not a registration)

Adopt **an evidence-anchored, independently endorsed governance architecture** — with the
basis of adoption made explicit (Rev2, critique Finding 7), so §3.2's demotion logic is
applied to this section symmetrically rather than only to the graph:

- The **governance architecture itself** (records with provenance, independent
  endorsement, explicit forks, evidence-release pinning) is adopted on **non-empirical
  governance grounds** — auditability, provenance, fork-governance, and licensing
  hygiene — which hold regardless of any efficiency verdict. [STIPULATED]
- The **constructed-record store as what the canon ships** (versus a hash-pinned
  plain-text store governed by the *same* endorsement machinery) is only **conditionally
  adopted pending the H-TEXT-SOURCE outcome (Rev3 naming)**. On §1.3 criterion-8 efficiency grounds it
  currently stands **unearned**: K-NULL found the kernel store weakly dominated by a
  plain dictionary at its tested scope [MEASURED: §0b]. If precedence row 3 fires for a
  sector — or the text control remains unheard (row 4, §4.8) — adoption of constructed
  records is withheld for that sector and the endorsement machinery governs the text
  store instead. [STIPULATED — PROPOSED-PREREG-ROW-99A-R2g]

The six steps of the architecture:

1. **Declare the unit.** Records per sense; profile, domain, language, authority, and
   intended verification scope fixed first.
2. **Assemble an evidence packet.** Multiple independently pinned sources where available,
   plus at least one non-constructor anchor appropriate to the sector; record source
   conflicts instead of silently synthesising them. **Packet assembly is a bound role
   per §1.2 condition 6 (Rev2, critique Finding 8):** pinned assembly procedure,
   assembler not of the drafter's family, and full selection provenance recorded —
   including candidate sources considered and rejected. **Rev3 (cross-vendor
   MAJOR-7): drafter-assisted source selection is prohibited outright, assembly draws
   from a pinned sampling frame, and an audit sample is dual-assembled by independent
   assemblers per §1.2 condition 7.**
3. **Use the pinned drafter as a compiler** (per #56 currently Sol/largekern-10k; §0). The
   drafter may propose the `kot-ast` record; every semantic clause must cite one or more
   evidence anchors; unsupported clauses fail; source conflicts force abstention or an
   explicit adjudication request. Mechanical validator feedback remains useful.
4. **Apply the independent semantic gate of §1.2.** Reviewers see evidence, examples,
   counterexamples, and the proposed record — never downstream test gold. Promotion
   requires the §1.2 threshold or recorded adjudication. Unreviewed output stays
   `ModelAuthored`; deterministic source-only relations may stay `AxiomsOnly`.
5. **Derive identity and geometry only after promotion.** Hash the normative content;
   separately pin the evidence release; then run the current deterministic encoder.
   Changing the endorsed record changes concept identity/vector; changing only provenance
   changes the evidence release.
6. **Use model internals downstream — and upstream only as discovery.** E8-style SAE
   alignment tests whether the canon predicts model representations and provides per-model
   adapters/regression instruments; SAE-derived material may propose senses or flag
   coverage gaps, but never feeds canonical content without new external evidence.

All six steps are [STIPULATED] design choices, none is [MEASURED], and none is registered
by this document.

### 3.2 What is DEMOTED: the graph constraint is hypothesis H-GRAPH, not a recommendation

The original draft *recommended* inserting a dictionary-derived evidence graph (§2 row b)
as a mandatory constraint between packet and drafter. The review is right that this cannot
be a recommendation, because **its own strongest objection plausibly dominates it**:

- The original conceded that matched-review direct LLM construction may be equivalent and
  cheaper, in which case the graph should be removed. [STIPULATED — original §3 objection]
- **K-NULL *motivates* that objection — as a tagged extrapolation, not as measurement
  (Rev2, critique Finding 4):** the figures are [MEASURED] (plain aligned text
  equivalent within the registered margin, nominally more accurate, ~0.565× verifier
  FLOPs — descriptive-by-design in the pinned reconcile record, §0b), but K-NULL's
  tested mechanism consumed aligned answer strings only, and its own reconcile
  quarantines it from mechanisms that *consume* content (entailment-style checking) —
  which is exactly what KBUILD-0 scores. Carrying K-NULL's dominance conclusion across
  that mechanism envelope into the *construction* setting is therefore
  **[EXTRAPOLATION]** — legitimate for motivating the demotion of a recommendation to a
  hypothesis, never usable as support for any verdict or gate. RULES-2 (§0b) stands as
  the capped counterweight: content can matter, never kernel-specifically.
  (PROPOSED-PREREG-ROW-99A-R2d)
- KBUILD-0 as originally designed could not even isolate the graph: H differed from A1 by
  the graph AND clause-level citation discipline AND changed prompting/abstention, so any
  H−A1 advantage was confounded (review §2). The decisive ablation is citation-only
  without a graph (§4, arm A2).

**Therefore:** the defensible wording is — *preferred governance architecture (§3.1);
graph constraint a pre-registered empirical hypothesis*:

> **H-GRAPH [PROPOSED-PREREG-ROW-99A-R1d, hypothesis — NOT a recommendation; contrast
> re-anchored in Rev3 per cross-vendor CRITICAL-1]:** relative to the **flat-IR
> control (arm A2-IR — same atoms and relations as H's graph input, in flat non-graph
> form; §4.3)** under the identical endorsement protocol, adding the deterministic
> **packet-local** graph constraint (arm H) improves packet-relative construction
> fidelity (primary endpoint, §4.5) or reduces semantic error or blinded-review cost,
> by the pre-registered margins. The Rev2 contrast H vs A2 is retained only as the
> decomposable total effect (H−A2) = (H−A2-IR) + (A2-IR−A2), whose second component
> is a machine-readable-input increment, not a graph increment. H-GRAPH is **tested
> against, and subordinate to, the K-NULL-style plain-text control (arm T, the
> independently governed text store; T′ is a format probe only — Rev3 CRITICAL-2): if
> the T-source four-zone decision (§4.6, on the R4a decision statistic) is
> **text-superior — regardless of LCC — OR T noninferior to every candidate
> within m_T with lower lifecycle-cost composite (LCC, §4.8)** (the uniform text
> rule — Rev4, re-review residual 5: the Rev3 wording here appeared to require
> lower LCC even when text was superior, contradicting §4.8 row 3; the second
> branch RENAMED in Rev7 per the Rev6 re-review §2 — its confirmatory content,
> C-DEF-NSUP, is one-sided noninferiority of T, not two-sided equivalence),
> text deflation dominates any graph result; if the text
> contrast lands in the indeterminate zone, constructed-arm adoption is blocked**
> (precedence matrix, §4.8, rows 3–4).

**Scope of H-GRAPH (Rev2, critique Finding 5):** on the nonce stratum, arm B/H's graph
is necessarily a **packet-local relation digest**, not dictionary-scale convergence: a
KBUILD-0 packet contains three renderings of one micro-world rule, with none of the
large-N convergence, cycle-census, or cross-source-reconciliation structure that makes
methodology (b) interesting. H-GRAPH's verdict is therefore worded as "does a
packet-local graph constraint during compilation help," and only the natural stratum
(where real dictionary structure exists) speaks — confirmatorily, never rescuing a
failed primary — to dictionary-scale constraint. Methodology (b)'s
discovery/inventory/audit roles (§2 row b, "Proposed role") are **untouched by any
KBUILD-0 outcome**. [STIPULATED — PROPOSED-PREREG-ROW-99A-R2e]

**Oracle-IR upper-bound label (Rev3, cross-vendor CRITICAL-1):** because the nonce-stratum
graph (and the A2-IR flat control) are derived from the generator-side shared typed IR
rather than from a realistic text→IR extraction pipeline, the entire B/H/A2-IR family is
an explicitly labelled **upper-bound mechanism test**. A positive H result means "given
lossless machine-readable input, does **explicit graph materialisation/closure** add
anything" — narrowed in Rev4 per the re-review's C1 note: the flat A2-IR list of typed
relations still contains **reconstructible topology**, so H−A2-IR isolates explicitly
materialising and closing the graph, never "relational information versus none" — and it
is **never** evidence about production graph-import performance, which would additionally
require a realistic, error-prone text→IR extraction test (out of scope for KBUILD-0 and
listed as a binding extrapolation cap in §6). [STIPULATED — PROPOSED-PREREG-ROW-99A-R3a]

Direction-of-travel note (rescoped in Rev2 per critique Finding 5c; wording completed
in Rev5, re-review residual 4 — "fails" was ambiguous between the R4e outcomes): if
H-GRAPH **fails to advance or is killed** (§4.8 three-outcome rule) but
citation discipline alone (A2 vs A1) shows the benefit, the programme keeps
citation-constrained drafting and drops the graph constraint **from the compilation loop
for the tested sectors** — (b)'s discovery, inventory, and audit roles are unaffected.
[EXTRAPOLATION — direction-only, decides nothing]

## 4. KBUILD-0 (revised): cheap, decisive construction experiment

Test construction methodology before another scale build. Two-stage, cheapest-first
(review §5): **Stage 1 scores every arm directly against the three-valued
packet-relative target of §4.5 (exact hidden rules only on fully-identifying packets —
Rev3, cross-vendor CRITICAL-3) with no host model at all**; the host/compression
evaluation runs only if Stage 1 earns it.

### 4.1 Hypotheses

- **H-GRAPH (primary; demoted-to-hypothesis form, §3.2; graph-isolating contrast
  re-anchored — Rev3, cross-vendor CRITICAL-1):** graph-constrained H beats the
  **flat-IR control A2-IR** (identical atoms/relations in non-graph form, §4.3) on
  packet-relative construction fidelity by the pre-registered margin (lower
  confidence bound — at claim C-GRAPH's final procedure-assigned level, never a
  fixed 95% (Rev6/R6a; formerly Rev5's node E3) — of the paired per-concept
  difference > +0.08 on the fidelity composite, jointly with both arms'
  safety-gate components inside the same intersection-union claim (R6a); the isolated increment is **explicit graph materialisation/closure** —
  Rev4 C1 narrowing, §3.2). **H vs A2-IR is the only graph-isolating contrast**; the Rev2 contrast
  H vs A2 confounded the graph with an oracle-quality parse/normalisation channel and
  survives only as the decomposition (H−A2) = (H−A2-IR) + (A2-IR−A2). The whole
  B/H/A2-IR family is an oracle-IR **upper-bound mechanism test** (§3.2); no
  production graph-import claim follows from it. (PROPOSED-PREREG-ROW-99A-R3a)
- **H-REVIEW:** matched independent review (A1 vs A0) improves fidelity — isolates the
  gate's value independent of any graph.
- **H-TEXT-SOURCE (deflation, dominant — Rev3 CRITICAL-2 split; decision endpoint
  made unconditional and executable in Rev4, re-review residual 1 —
  ADOPTION-BLOCKER):** the **independently governed plain-text store** (arm T, §4.3
  — governed by the same endorsement machinery but never passing through
  structured-record construction, and never depending on any constructed arm's
  output) is, under the §4.6 **four-zone rule** applied to the **single
  pre-registered decision statistic of the unconditional held-out claim task**
  (UCT, §4.5; PROPOSED-PREREG-ROW-99A-R4a), **text-superior, OR noninferior to
  every candidate within m_T with lower LCC** (branch renamed in Rev7 per the
  Rev6 re-review §2: the confirmatory content of the second branch is
  C-DEF-NSUP — one-sided noninferiority of T, never two-sided equivalence;
  matching §4.8 row 3: the superior zone fires regardless of LCC, and the LCC
  clause is an operational-policy filter, §4.6/R7b). The UCT
  runs **unconditionally**: it is part of Stage 1, uses the **same blinded
  consumers and identical artifact/consumer budgets for T and every constructed
  arm**, and never depends on Stage 2 or on any constructed arm showing benefit —
  removing the Rev3 conditionality under which the dominant text comparison could
  lose its realistic common consumer precisely when construction was weakest. The
  nonce-stratum oracle parse-back comparison is retained as an **explicitly
  secondary upper bound, never the decision**. This is the **only** hypothesis that
  can license "structured-record construction can be avoided". **Because it is the
  dominant hypothesis it is powered like one (Rev2, critique Finding 1a —
  retained):** the §4.6 power rule requires ≥90% power at its registered margin
  (true effect zero) on the R4a statistic under the final R6a multiplicity
  procedure (the confirmatory content of the four-zone read is carried by the
  enumerated one-sided claims C-DEF-NSUP / C-DEF-SUP / C-CON-SUP-c — §4.6/R6a;
  the four-zone label itself is the operational read-out), with the same
  `INSTRUMENT-INVALID` consequence as the superiority
  contrast; and an **indeterminate-zone** T-source outcome **blocks constructed-arm
  adoption** (§4.8 row 4). If supported, adopt the text store for this scope — this
  outcome **dominates** all constructed-arm contrasts (§4.8).
  (PROPOSED-PREREG-ROW-99A-R3b, amended by R4a)
- **H-TEXT-FORMAT (format probe, non-dominant — Rev3, cross-vendor CRITICAL-2
  split; SINGLE confirmatory endpoint named in Rev6 per the Rev5 re-review's
  MAJOR-new finding):** the deterministic prose rendering T′ of the *same
  endorsed record* as the hierarchy winner is equivalent to the record's native
  formats (AST rendering; vector-derived rendering) on **exactly ONE
  confirmatory endpoint: Stage-2 host three-label macro balanced accuracy on
  the NATURAL stratum** — the C-FMT target stratum is pinned here explicitly
  (Rev7/R7d, closing the Rev6 re-review §4 gap: SIM-SPEC assumed natural
  concepts while the claim ledger did not say so) — (claims C-FMT-c,
  §4.6/R6a; equivalence margin m_F pinned pre-freeze; Stage 2 only).
  Format-handling behaviour and consumer cost are **descriptive only** —
  the earlier wording that listed them beside the endpoint is deleted (R6d).
  Selection validity is by simultaneous coverage, not conditioning: the
  confirmatory family contains one format claim per candidate arm (so EVERY
  candidate-arm × format contrast is pre-registered at a pre-assigned level),
  and the claim read out for the hierarchy winner is therefore valid whatever
  the hierarchy selects — no post-selection adjustment is needed and none is
  claimed (§4.6/R6a). **What this establishes is SELECTION-VALID GRAPHICAL
  HYPOTHESIS TESTING — familywise-valid claim decisions under arbitrary
  correlation with Stage-1 selection — and nothing more: no compatible
  SIMULTANEOUS confidence-interval procedure is constructed or claimed;
  per-claim one-sided bounds reported at data-dependent final local levels
  are claim-level test inversions, not a simultaneous confidence set
  (Rev7/R7d, per the Rev6 re-review §4).** Because T′
  renders the same record, its **Stage-1 fidelity equivalence is largely true by
  construction and is NEVER evidence that plain text replaces construction**; T′ is
  charged **all shared upstream construction/review costs** in the LCC, and its
  verdict governs only *what format the constructed record ships in* — never whether
  construction happens. (PROPOSED-PREREG-ROW-99A-R3b)
- **H-SHUFFLE (assignment):** correctly assigned representations beat within-stratum
  shuffled representations (confirmatory direction: the C-VAL validity
  conjunction, §4.6/R6a); an **operational equivalence-to-shuffle read** kills
  all construction-specific content claims at this scope (§4.8 row 2 — an
  operational kill per the §4.8 Rev6 note, not a confirmatory no-effect
  claim), while a merely
  indeterminate shuffle contrast blocks confirmatory advancement without killing
  (Rev4/R4e discipline).
- **H-HUMAN (cost realism; DESCRIPTIVE from Rev6 — R6b):** neither drafter nor graph reduces blinded expert review time
  or the lifecycle-cost composite (LCC, §4.8) relative to the human-from-evidence arm E
  at matched fidelity. Tested descriptively in KBUILD-0; retains a conservative
  operational adoption-blocking role via §4.8 row 5 (a block, not a
  confirmatory claim).

All margins are [STIPULATED] smallest-effects-of-interest, to be justified against
calibration data before any freeze; nothing here is frozen.

### 4.2 Evaluation set

Two preregistered strata (role-separated authors, reviewers, host operators, auditors):

1. **Primary: 96 post-registration nonce senses.** Finite micro-worlds with exact hidden
   truth conditions built from existing representable predicates, relations, negation,
   scope, and molecule references; random nonce labels assigned after generation.
   **The generator's rule grammar — the finite hypothesis space of rules it can emit —
   is pinned pre-freeze; §4.5's packet-relative target quantifies over exactly the
   grammar rules consistent with the published packet (Rev3, cross-vendor
   CRITICAL-3).**
   Constructors receive: three independently rendered source descriptions (from
   **separate renderer families**, §4.7 gate 3 — cross-reference corrected in Rev4,
   re-review residual 6; it formerly pointed to gate 5); positive/negative/boundary exemplars;
   source authority/provenance labels. Held back: the generating rule and **nine claims
   per concept, three per label** (`ENTAILED`/`CONTRADICTED`/`UNDERDETERMINED`) — the
   original "eight balanced across three labels" was arithmetically impossible per
   concept and is replaced by the exact 3/3/3 allocation, with the multiclass
   balanced-accuracy formula (unweighted mean of the three per-label recalls) pinned in
   the prereg. `[STIPULATED — review-1 fix 4; PROPOSED-PREREG-ROW-99A-R1h]`
   **Honest scope note (review §3):** because evidence and claims derive from the same
   generating rule over familiar predicates, this stratum tests **faithful
   evidence-to-record compilation** (synthetic rule induction + compression) — which is
   exactly the target capability — and does **not** decide external grounding or
   natural-concept construction. Claims from this stratum are capped accordingly.
2. **Confirmatory for constructed-arm contrasts; DECISION-GRADE for the T-source
   contrast (Rev4, re-review residual 1): 48 natural, ambiguity-rich senses.** Two
   pinned build sources to constructors — these constitute the stratum's **published
   build packet**. Held-out claims are generated from an independent held-out source
   plus two blinded human annotators and adjudication, and every claim carries **two
   gold labels**: (i) the **decision-grade packet-relative label** —
   `ENTAILED`/`CONTRADICTED`/`UNDERDETERMINED` **relative to the published build
   packet's supported content**, adjudicated by the blinded annotators from the
   packet alone; the held-out source is used for claim *generation* and for label
   (ii) only, **never to mark packet-unsupported content as known** (a claim true
   per the held-out source but unsupported by the packet is `UNDERDETERMINED`
   packet-relatively); and (ii) a descriptive **external-truth label** from the
   held-out source, reported separately and feeding no decision — produced, per
   Rev6 (R6d; the Rev5 re-review's nonblocking cleanup: this label previously
   had no permitted producer, since source-exposed generators may not label and
   packet-only gold labelers may not see the held-out source), by a **bound
   source-exposed descriptive-labeler role**: annotators who see the held-out
   source and the claims but never the packet-relative gold, any arm artifact,
   or any consumer session, and who are role-disjoint from the claim
   generators, the packet-only gold labelers, the adjudicator, and every
   constructing/endorsing/consuming role; access-logged like the other bound
   roles (§4.7 gate 11 iii), their output feeds ONLY the descriptive
   external-truth report. This gives the
   natural stratum the same three-valued packet-relative target as §4.5 without
   requiring a deterministic natural-language parse-back. Constructed-arm contrasts
   here remain confirmatory transfer tests and cannot rescue a failed nonce
   primary; **the H-TEXT-SOURCE decision statistic, by contrast, lives on this
   stratum by design** (the §4.5 UCT) — decision-grade for the text contrast only,
   never a rescue channel for any constructed-arm contrast.
   [STIPULATED — PROPOSED-PREREG-ROW-99A-R4a]
   **Natural-gold executability pins (Rev5, re-review residual 2 — the Rev4 text
   left per-concept three-class balanced accuracy undefined when a natural
   concept lacked a claim in some gold class):** each natural sense carries
   **nine held-out claims, exactly three per packet-relative gold class**
   (`ENTAILED`/`CONTRADICTED`/`UNDERDETERMINED`) — the same 3/3/3 allocation as
   the nonce stratum, guaranteed **by generation-to-quota**: (i) *generator/labeler
   separation* — held-out-source-exposed claim **generators** are a bound role,
   disjoint from every labeling, adjudicating, consuming, constructing, and
   endorsing role; they alone see the held-out source and they never assign a
   gold label; the packet-only gold **labelers** (the two blinded annotators plus
   a third packet-only adjudicator) never see the held-out source or any arm's
   artifact. (ii) *Sampling and exclusion rules* — generators produce candidate
   claims in pinned batches; pinned mechanical screens (single-proposition form,
   grammaticality, a pinned near-duplicate similarity bound) apply BEFORE any
   labeling; labelers then assign the packet-relative label independently under a
   pinned majority rule, with the adjudicator resolving disagreements and
   three-way splits; generation continues until every class holds three claims,
   under a pinned per-concept candidate cap (proposed 30, re-justifiable at
   freeze); a concept whose cap is reached before quota is replaced from a
   pre-registered reserve list **before any arm artifact is drawn** — an
   outcome-independent, gold-side rule, so no arm-outcome channel exists.
   (iii) *Missing-class fallback (pinned)* — if post-freeze adjudication ever
   leaves a gold class empty for some concept, per-concept macro-BA is defined as
   the unweighted mean recall over the **non-empty** gold classes; the concept is
   flagged and counted in the report and is **never excluded** — the gold is
   arm-independent, so the fallback is byte-identical across arms inside every
   paired contrast and cannot bias a between-arm difference. (iv) *Reliability* —
   chance-corrected labeler agreement is gated by §4.7 gate 11.
   [STIPULATED — PROPOSED-PREREG-ROW-99A-R5b]
3. **Adversarial packet subset (new; review §5):** within each stratum, a preregistered
   fraction of packets contains conflicting sources, insufficient evidence
   (gold-underdetermined), tempting unsupported clauses, and anti-prior cases. These are
   where evidence constraints must earn their cost; abstention behaviour on these packets
   is scored, not excused — **against the §4.5 three-valued packet-relative target, never
   against exact hidden-rule equivalence (Rev3, cross-vendor CRITICAL-3: a method cannot
   both refrain from guessing and exactly reproduce a rule the packet underdetermines).**

**Sector verdicts are separate** (review §5): synthetic formal micro-worlds and ordinary
lexical senses do not decide institutional, observational, or operational construction;
the report must scope its verdict to the sectors actually tested. [STIPULATED]

### 4.3 Construction arms `[STIPULATED — review-1 fix 4; PROPOSED-PREREG-ROW-99A-R1e]`

All constructors receive identical evidence packets and output the same typed record
schema. "Drafter" = the pinned drafter of record (§0).

- **A0 — current pinned pipeline, unreviewed:** drafter + one validator-error-fed repair,
  no semantic editing. Illegal output and abstention stay in the denominator as
  **substantive method failures** (§4.7 gate 7).
- **A1 — reviewed direct drafting:** A0 followed by the fixed §1.2 endorsement protocol
  and reviewer time budget shared by all reviewed arms.
- **A2 — citation-constrained direct drafting, NO graph (new; the decisive graph
  ablation):** direct drafter construction with clause-level evidence pointers,
  unsupported-clause rejection, and the identical conflict/abstention rules as H — but no
  evidence graph. Same endorsement protocol as A1/H. The Rev2 claim "H vs A2 is the only
  contrast that isolates the graph" is **superseded in Rev3 (cross-vendor CRITICAL-1):
  H vs A2 confounds the graph with an oracle-quality machine-readable input channel;
  the graph-isolating contrast is H vs A2-IR below.**
- **A2-IR — flat-IR control, NO graph (new — Rev3, cross-vendor CRITICAL-1):**
  identical to A2 except the constructor additionally receives **the same atoms and
  relations that arm H's graph is built from, in flat, non-graph form** — an unordered
  list of the packet IR's typed predicates, molecule references, exemplar entities,
  typed relations, negation and scope operators, with **no closure, no topology, no
  adjacency structure**. Raw evidence, prompt scaffold, token/compute budget,
  endorsement protocol, and reviewer visibility are **matched to H exactly**. A2-IR
  isolates the lossless machine-readable-input channel; **H − A2-IR isolates
  explicit graph materialisation/closure** (narrowed in Rev4 per the re-review's C1
  note: a flat list of typed relations still contains **reconstructible topology**,
  so the contrast isolates materialising/closing the graph, not the presence of
  relational information per se); A2-IR − A2 measures the input-channel increment on its own.
  Like B/H, A2-IR draws on the generator-side IR and therefore carries the §3.2
  oracle-IR upper-bound label. (PROPOSED-PREREG-ROW-99A-R3a)
- **B — graph only (packet-local on the nonce stratum — Rev2, critique Finding 5a):**
  on nonce packets the graph is constructed by a **frozen extraction rule over the
  packet's shared typed IR** (§4.7 gate 1): nodes are the IR's predicates, molecule
  references, and exemplar entities; edges are the IR's typed relations, negation, and
  scope operators; frozen closure/fixpoint; rendered without generative semantic
  additions. On the natural stratum, B is the real dictionary sense-graph
  (source-supported signed relations under a frozen rule). B's nonce-stratum verdict is
  explicitly a packet-local-digest verdict, never a dictionary-convergence verdict
  (§3.2 scope; PROPOSED-PREREG-ROW-99A-R2e).
- **H — graph-constrained hybrid:** B's evidence graph → drafter compilation with
  clause-level evidence pointers → the matched endorsement protocol.
- **E — human/expert-from-evidence (new):** blinded human experts author the typed record
  from the identical packet under the same time budget. Since endorsement may dominate
  cost, the study must test whether the drafter or the graph actually reduces expert
  work; E also anchors the achievable-fidelity ceiling and the LCC comparison.
  **Schema-familiarity counter-measure (structural, NOT deferrable — Rev2, critique
  Finding 10):** the drafter is pipeline-tuned to the record schema; humans authoring it
  cold would be scored down for tooling unfamiliarity, not semantic ability — and
  precedence row 5 (human baseline) sits above the graph row, so this bias could flip
  the headline verdict in either direction. Therefore: pre-registered schema training
  plus calibration exercises to a **pinned proficiency bar** before any scored
  authoring; E fidelity reported both raw and post-calibration; and "expert" for nonce
  micro-worlds is **defined as demonstrated calibration performance, not domain
  credentials** (§1.2 sector competence has no meaning for synthetic nonce concepts).
  Recruitment logistics remain deferrable to pre-freeze; this counter-measure does not.
  (PROPOSED-PREREG-ROW-99A-R2j)
- **T — independently governed plain-text store (T-source; redefined — Rev3,
  cross-vendor CRITICAL-2):** hash-pinned source text (the packet's rendered
  descriptions plus pinned source definitions), **governed by the same endorsement
  machinery** (a human endorser attests the pinned text's evidence adequacy under
  §1.2 without authoring or editing any structured record) and **independent of every
  constructed arm's output**. No graph, AST, vector, or generated explication. T is
  scored on the §4.5 common estimand by the same procedure as every other arm: on the
  nonce stratum via the gate-1 deterministic text→IR parse-back — which is itself
  oracle-quality, so nonce-stratum T fidelity is labelled an **upper bound, symmetric
  with the oracle-IR label on B/H/A2-IR, and is never the T-source decision**; the
  **decision-grade T-source comparison is the unconditional held-out claim task**
  (UCT, §4.5 — Rev4, re-review residual 1): the same blinded consumers and identical
  artifact/consumer budgets for T and every constructed arm, unconditional on
  Stage 2 and on every other Stage-1 outcome. T is charged only its own governance
  costs in the LCC, never any structured-construction cost.
  (PROPOSED-PREREG-ROW-99A-R3b, amended by R4a)
- **T′ — content-matched plain rendering (format probe ONLY — Rev3, cross-vendor
  CRITICAL-2):** a deterministic plain-prose rendering of the *same endorsed record*
  produced by the winning constructed arm, separating semantic content from
  schema/format (review-1 §3). T′ serves **H-TEXT-FORMAT only**: its Stage-1 fidelity
  is largely true by construction, it presupposes the record was already constructed
  and endorsed, and it is charged **all shared upstream construction/review costs** in
  the LCC. A T′ fidelity equivalence is never deflation evidence — that is T's job.
- **S — shuffled controls:** independent permutation of the concept↔representation mapping
  for A0, A1, A2, A2-IR, B, H, T, T′ within sense-type and token-length strata; bytes, token
  budgets, format unchanged. (A0 added in Rev5: the R5a atomic enumeration exposed that
  the §4.8 A0 canon-readiness rule and Rung 0 referenced an A0 shuffle this list lacked —
  a consistency repair, not a design change.)
- **N — no-context control:** claim only.

Method (c) remains excluded as a construction arm (a target model's internals cannot
independently define post-registration nonce concepts); SAE alignment runs descriptively
after construction, per §3.1 step 6.

### 4.4 Stage sequencing and consumer `[STIPULATED — review-1 fix 4]`

- **Stage 1 (primary, no host):** score every arm directly against the three-valued
  packet-relative target of §4.5 (exact hidden rules only on fully-identifying
  packets — Rev3, cross-vendor CRITICAL-3). Co-primary observables: construction fidelity, the
  lifecycle-cost composite (LCC, §4.8), blinded-review metrics (agreement with CI, edit
  distance, review minutes, adjudication rate). **Stage 1 also contains the
  unconditional held-out claim task (UCT, §4.5 — Rev4, re-review residual 1):
  blinded human consumers (no host model) answer the held-out claims from each
  arm's artifact under identical pinned budgets; the UCT runs for every arm in both
  strata regardless of any other Stage-1 outcome and supplies the sole T-source
  decision statistic.** A **pre-registered sequential
  futility/superiority boundary** allows stopping arms early — **but never gates or
  stops the UCT or arm T (R4a)**. Stage 1 is itself entered
  via the machine-only Rung 0 screen (§7 — Rev2, critique Finding 12), which can kill
  the branch before the human endorsement apparatus is stood up.
- **Stage 2 (secondary, conditional):** the host/text-compression evaluation runs **only
  if** Stage 1 shows the relevant constructed arm has incremental semantic fidelity or
  review-cost benefit. **The T-source decision never depends on Stage 2 (Rev4):
  Stage-2 host results are secondary/confirmatory for the text contrast, whose
  decision endpoint is the unconditional Stage-1 UCT (§4.5/R4a).** Host: smallest model from a preregistered local ladder passing the
  calibration gate (starting from the pinned SmolLM2-135M-Instruct), from a different
  family than the drafter, no training or adapters; three fixed labels by
  log-probability scoring; 256-token primary evidence ceiling with 64/128/256 secondary
  compression curves under frozen truncation/ranking rules. Host competence must be
  demonstrated on an **exact-rule oracle rendered in every arm's format** (§4.7 gate 6),
  so the reader gate cannot silently select a T-friendly host. Vector bytes, AST bytes,
  and rendered tokens are all reported; no vector-efficiency claim may be inferred from a
  text-only consumer.

### 4.5 Primary endpoint: packet-relative construction fidelity `[STIPULATED — review-1 fix 4; PROPOSED-PREREG-ROW-99A-R1g, redefined by R3c per cross-vendor CRITICAL-3]`

The Rev2 endpoint required the record extension to equal the concealed full-rule
extension *while also rewarding abstention* — impossible on deliberately underdetermined
packets. The endpoint is therefore **three-valued and packet-relative**:

- **Formal target (per concept — Rev3, cross-vendor CRITICAL-3):** let R(packet) be the
  set of rules in the pinned generator rule grammar (§4.2) consistent with the
  published packet. For each cell of the enumerated micro-world (and each held-out
  claim), the target is **TRUE** if it holds under *every* rule in R(packet),
  **FALSE** if it holds under *none*, and **UNKNOWN** otherwise. R(packet) is
  machine-enumerable over the finite pinned grammar; the enumeration is part of the
  deterministic scorer and self-tested exhaustively (gate 2).
- **Fully-identifying packets** (|R(packet)| = 1 up to extensional equivalence — a
  machine-checked property): the packet-relative target coincides with the hidden
  rule, and **exact hidden-rule equivalence applies there and only there**.
- **Underdetermined packets** (including the whole adversarial subset): scored on
  **supported-content fidelity** (agreement on TRUE/FALSE cells) and **abstention
  calibration** (behaviour on UNKNOWN cells), **reported separately**; exact
  hidden-rule equivalence is never demanded of them.
- **Primary composite — NON-COMPENSATORY, completed as a HURDLE/LEXICOGRAPHIC
  estimand (Rev3 MAJOR-6; made mathematically complete in Rev4, re-review
  residual 3):** pre-registered component metrics remain unsupported-content rate,
  contradicted-content rate, omission rate, boundary-error rate, and abstention
  miscalibration, guarded by **hard minimum gates** on unsupported, contradicted,
  omitted, and abstention-miscalibrated content (each bound pinned pre-freeze; a
  breach fails the record outright — no fatal unsupported assertion can be
  compensated by excellence elsewhere). The estimand is two-level:
  **(Level 1 — hurdle)** each arm's **gate-pass rate** — the fraction of its
  concepts whose record passes ALL hard gates, with **every record retained in the
  denominator**: construction failures, illegal output, and gate-breaching records
  all count as failures, never excluded — is compared between arms with
  paired-difference confidence bounds, and each arm must clear a pre-pinned
  **arm-level safety gate** (gate-pass-rate lower confidence bound ≥ a pinned
  pre-freeze threshold). **(Level 2 — composite)** the composite fidelity
  comparison for a contrast is confirmatory **only after every arm in the contrast
  passes its arm-level safety gate** — in Rev6 this precondition is carried
  INSIDE each composite-endpoint confirmatory claim as explicit safety-gate
  intersection-union components (§4.6/R6a: a claim's rejection asserts the
  contrast AND its governing gates jointly), which also resolves the Rev5
  re-review's which-gates-govern-which-contrast ledger defect; **shuffle
  contrasts are exempt from the every-arm-gate precondition BY DESIGN** (stated
  explicitly in Rev6, previously implicit): the shuffled comparator is expected
  to breach hard gates, and floor imputation keeps the paired estimand defined
  without requiring it to pass any gate; within Level 2, a record that breaches a hard gate
  is **scored at the registered composite floor (the pinned worst value), never
  dropped**, so every paired per-concept difference — explicitly including H−A2-IR
  when either record breaches a hard gate, previously undefined — is defined on
  every concept. An arm that fails its safety gate cannot advance or be adopted;
  contrasts involving it are reported descriptively, with the Level-1
  gate-pass-rate difference as the reported statistic. Component weights are
  **frozen from externally justified grounds and calibration data disjoint from
  outcome data, before any outcome unblinding**, and component-wise sensitivity of
  every verdict is reported. (PROPOSED-PREREG-ROW-99A-R3f, completed by R4c)
- **Common estimand across ALL arms (Rev3, cross-vendor CRITICAL-2):** every arm —
  constructed, human, and text — is scored against the same three-valued
  packet-relative target by the same deterministic procedure: typed records by direct
  denotation; text arms via the gate-1 deterministic parse-back (with the
  nonce-stratum oracle-parse upper-bound caveat stated at arm T, §4.3). **No arm has
  a private endpoint.** The dominant T-source contrast is additionally given its own
  executable common decision endpoint — the unconditional held-out claim task below
  (Rev4, re-review residual 1) — because the natural stratum has no deterministic
  parse-back and the nonce parse-back is an upper bound, not a decision.
- **T-source decision endpoint — the unconditional held-out claim task (UCT; new —
  Rev4, re-review residual 1, ADOPTION-BLOCKER):** blinded human consumers —
  arm-blind, and disjoint from constructors, endorsers, gold annotators, and
  adjudicators — receive one arm's artifact per session (the record rendered in its
  native shipping format, or T's pinned text) under an **identical pinned artifact
  token budget and consumer time budget for every arm, T included**, and answer the
  held-out claims (`ENTAILED`/`CONTRADICTED`/`UNDERDETERMINED`), scored against the
  **packet-relative gold**: nonce claims against the R(packet) three-valued target
  above; natural claims against the §4.2 decision-grade packet-relative label (the
  held-out source generates claims and supplies the descriptive external-truth
  label only — it never marks packet-unsupported content as known). The UCT runs
  **unconditionally for every arm in both strata**: it depends neither on Stage 2,
  nor on the sequential boundary's constructed-arm decisions, nor on any
  constructed arm showing benefit. **ONE statistic feeds the four-zone T-source
  decision (§4.6): the paired per-concept difference in three-label macro balanced
  accuracy (the pinned §4.2 multiclass-BA formula) on the natural-stratum UCT,
  between the §4.6-hierarchy comparison arm (fallback A1) and T**, analysed under
  the §4.6 crossed model with consumer as an additional crossed random factor.
  Declared secondary upper bounds — reported, never the decision: the nonce-stratum
  UCT difference, the nonce deterministic parse-back fidelity difference, and (only
  if Stage 2 runs) the host claim-task difference.
  [STIPULATED — PROPOSED-PREREG-ROW-99A-R4a]
- **UCT execution pins (Rev5, re-review residual 2 — the operational detail that
  made the Rev4 UCT not-yet-executable):** (i) *Consumer assignment and carryover
  protection:* consumers are assigned to concept × arm cells by a pinned balanced
  incomplete design with a registered assignment seed fixed at freeze; **no
  consumer ever answers claims for the same concept under two different arms**,
  session order is randomised within consumer, and consumer is a crossed random
  factor in the analysis (§4.6) — carryover is excluded by design, not modelled
  away. (ii) *Rendering and truncation:* every artifact is produced by its arm's
  pinned deterministic renderer and cut to the identical pinned token budget by
  ONE frozen truncation rule shared by all arms; a failed or illegal construction
  enters its UCT sessions as the arm's actual output (or the registered
  empty-artifact placeholder) and is **never excluded** — mirroring the R4c
  denominator rule; evaluator-side rendering breakage is instrument failure per
  gate 7, never silent attrition. (iii) *Format-competence check:* before any
  scored session, every consumer must pass a calibration battery of exact-rule
  oracle artifacts rendered in EVERY arm's format (the human mirror of gate 6)
  against a pinned per-format competence bound; failures are excluded before
  unblinding, outcome-independently — so the consumer pool cannot silently
  favour the text format, and the check is itself gated (§4.7 gate 11).
  (iv) *Comparator selection inference:* the comparison arm is selected by the
  outcome-dependent §4.6 hierarchy, so a single selected-arm CI is not
  automatically valid; of the re-review's two permitted repairs Rev5 takes the
  **simultaneous-inference branch** — all four candidate-vs-T UCT contrasts
  (H−T, A2-IR−T, A2−T, A1−T) are pre-registered members of the confirmatory
  family (Rev6: the four elementary claims C-CON-SUP-c at Bonferroni-split
  local levels, plus all four contrasts as components of the C-DEF-NSUP /
  C-DEF-SUP conjunctions — §4.6/R6a, superseding Rev5's node-E2 device), so the
  decision read for the hierarchy-selected arm is valid **whatever the
  hierarchy selects**; no outcome-disjoint calibration split is needed and none
  is claimed. [STIPULATED — PROPOSED-PREREG-ROW-99A-R5b, amended by R6a]
- **Secondary:** host balanced accuracy (Stage 2), per-concept macro-BA over the 3/3/3
  claims — explicitly a *consumer/compression* measurement, entangled with host
  comprehension, rendering, and truncation, and never a substitute for the primary.
- **Scoring is evaluator-run, never constructor-self-scored**; the denotational scorer is
  a deterministic program, self-tested exhaustively (gate 2).

Primary contrasts — confirmatory status per the Rev6 elementary family
(§4.6/R6a; the Rev5 ten-node/95-null enumeration is superseded, and the Rev4
restoration of A2−A1 and A1−A0 to the confirmatory family is deliberately
reversed under the maintainer-sanctioned #59 simplification). **CONFIRMATORY:**
every candidate-vs-T UCT contrast (deflation, dominant — the C-DEF-NSUP /
C-DEF-SUP conjunctions and the C-CON-SUP-c block, decided on the R4a UCT
statistic), H vs A2-IR (explicit-materialisation/closure increment — C-GRAPH,
with both safety gates as components), each decision-path arm vs its shuffle
(the C-VAL validity conjunction), and T′ vs the shipping record's native
formats on the single Stage-2 endpoint (C-FMT-c). **DESCRIPTIVE from Rev6
(downgraded with stated justification — R6b):** A2-IR vs A2
(machine-readable-input increment), A2 vs A1 (citation increment), A1 vs A0
(review increment, H-REVIEW), E vs the best machine arm (H-HUMAN cost realism —
retains a conservative operational blocking role, §4.8), A0 canon-readiness,
and the T′-shuffle contrast.

### 4.6 Statistics `[STIPULATED — review-1 fix 4; PROPOSED-PREREG-ROW-99A-R1h]`

- **Unit:** concept (resampling and permutation at concept level); paired contrasts.
- **Exchangeability:** sign-flip permutation validity is secured by design — randomised
  arm-material assignment where applicable and **randomised reviewer assignment**;
  reviewers are crossed and blinded, and **no reviewer sees competing records for the
  same concept**.
- **Analysis (crossed hierarchy — Rev3, cross-vendor MAJOR-5):** the primary inference
  model matches the design's actual crossed hierarchy: **concept and
  author-seed/model-snapshot as crossed random factors** (multiple seeds per arm),
  **reviewer as a random factor** on every review-based endpoint, **and UCT
  consumer as a crossed random factor on the claim-task endpoint (Rev4/R4a)**;
  **renderer families
  and the pinned host are declared FIXED levels, and every claim is narrowed
  accordingly** ("under the pinned renderer families and snapshots") — never
  generalised over unsampled levels. Concept-only resampling is abolished as the sole
  inference; 10,000 paired sign permutations at concept level are retained as a
  supplementary robustness check. Two-sided total α=.05; BCa CIs and effect sizes
  reported throughout — descriptive intervals at 95%, but **every DECISION
  bound at its claim's final procedure-assigned level (Rev6/R6a), never a fixed
  95%**; equivalence claims by the four-zone rule below, never by
  non-significance. (PROPOSED-PREREG-ROW-99A-R3e)
- **Four-zone decision rule for the text contrast (replaces TOST-only — Rev3,
  cross-vendor MAJOR-4):** for the constructed-minus-text fidelity difference with
  registered equivalence margin ±m and superiority threshold δ (both pinned
  pre-freeze from substantive interchangeability grounds): CI wholly inside ±m →
  **equivalent**; lower bound > +δ → **constructed superior**; upper bound < −δ →
  **text superior**; otherwise → **indeterminate, and constructed-arm adoption is
  blocked** (§4.8 row 4). Failure of an equivalence test is never read as
  non-equivalence, and never as constructed superiority. **Zone geometry (Rev4,
  re-review residual 2): δ ≥ m is REQUIRED for every four-zone contrast** (pinned
  at freeze) — it makes the four zones mutually exclusive, since a CI whose lower
  bound exceeds +δ ≥ m cannot lie wholly inside ±m (symmetrically for the text
  side); for completeness the formal precedence superiority/inferiority >
  equivalence is declared, though unreachable under δ ≥ m. The rule applies to the
  T-source contrast **on the R4a UCT decision statistic**, and, with
  (m = ±0.05, δ = +0.08), to the H−A2-IR graph contrast (precedence row 9).
  **Rev6 (R6a): the four-zone rule is retained as the OPERATIONAL decision
  layer, but confirmatory status attaches ONLY to the enumerated one-sided and
  union claims of the R6a elementary family.** Each confirmatory rejection is
  read as the corresponding one-sided bound at the claim's final
  procedure-assigned level; the full four-zone label — including the
  equivalence and inferiority directions that are no longer in the family — is
  additionally reported from a nominal two-sided 95% CI explicitly labelled
  descriptive/operational. Operational zones map to claims as follows:
  constructed-superior ⇔ C-CON-SUP-(selected) rejected; text-superior ⇔
  C-DEF-SUP rejected; the deflation trigger's **"T noninferior to every
  candidate within m_T with lower LCC" branch** (renamed from "equivalent
  with lower LCC" in Rev7 per the Rev6 re-review §2 — the branch is one-sided
  noninferiority of T, not two-sided equivalence) ⇔ C-DEF-NSUP rejected ("no
  candidate beats T by m_T", the scientifically operative direction for
  deflation; full two-sided equivalence remains a descriptive read) PLUS the
  §4.8 LCC rule. **LCC role, pinned (Rev7/R7b):** the lower-LCC conclusion is
  an OPERATIONAL-POLICY FILTER, not a confirmatory component — its null and
  p-value are deliberately NOT inside the C-DEF-NSUP IUT; the LCC clause can
  only WITHHOLD the deflation adoption that C-DEF-NSUP's rejection would
  otherwise license (an uncertainty-bounded, robustness-swept descriptive
  read per §4.8, `COST-INDETERMINATE` on any sweep reversal), so it creates
  no positive confirmatory rejection and cannot inflate FWER; the
  confirmatory content of row 3's second branch is exactly C-DEF-NSUP.
  Indeterminate ⇔ no relevant rejection, and adoption stays blocked — a
  non-claim consuming no alpha.
  (PROPOSED-PREREG-ROW-99A-R3d, amended by R4a/R4b/R5a, simplified by R6a)
- **Confirmatory testing family — provably valid ELEMENTARY-claim graphical
  procedure (Rev6/R6a; maintainer-ratified simplification #59; REPLACES the
  Rev5 ten-node/95-null atomic-graphical matrix):** three cross-vendor reviews
  proved the same defect in successive versions of the ambitious procedure —
  graph nodes were COMPOSITE families (four-zone bundles, gate bundles), and a
  node released its ENTIRE weight on any decisive rejection even though true
  elementary nulls remained inside it, an operation no cited theorem licenses.
  Rev6 removes the defect **structurally** rather than patching it: **every
  node of the graph is ONE elementary hypothesis** — a single null with a
  single valid p-value — so "partial rejection of a node" cannot exist, and
  weight moves only on rejection of the releasing node's own null, which is
  exactly the operation the cited theorem proves valid. Union nulls
  (conjunctive claims) are single hypotheses tested by intersection-union
  tests. The price is a smaller confirmatory family; the downgrades are
  itemised in (6) below and sanctioned by #59.

  **(1) The claim ledger — 12 elementary confirmatory claims (42 one-sided
  components over 24 distinct parameters).** Notation: Δ^UCT_c = paired
  per-concept difference (c − T), c ∈ {H, A2-IR, A2, A1}, in three-label
  macro-BA on the natural-stratum UCT (the R4a statistic, per candidate);
  Δ^SH_a = paired per-concept difference (a − S(a)) on the endpoint named in
  the table; Δ^G = paired per-concept difference (H − A2-IR) on the nonce
  primary composite (floor-imputed per R4c); π_a = arm a's §4.5 gate-pass
  rate; Δ^F_{c,f} = paired per-concept difference (T′(c) − f(c)) in Stage-2
  host three-label macro-BA, f ∈ {AST rendering, vector-derived rendering}.
  Margins (all freeze-time pins; proposed planning values in SIM-SPEC §S3):
  δ_S (shuffle superiority), m_T and δ_T with δ_T ≥ m_T (T-contrast),
  δ_G = +0.08 (graph), m_F (format equivalence), π₀ (safety-gate floor).
  Every component is one-sided; a UNION null is rejected only when EVERY
  component's one-sided p-value is ≤ the claim's current local level
  (intersection-union test, IUT: the claim's p-value is the maximum of its
  component p-values — a valid p-value for the union null with no internal
  alpha-splitting `[LIT-BACKED — Berger 1982, "Multiparameter hypothesis
  testing and acceptance sampling", Technometrics 24(4):295–300; Berger & Hsu
  1996, Statistical Science 11(4):283–319 for the TOST/equivalence case;
  source-verify at freeze per §5]`). Single-component claims are ordinary
  one-sided tests. Rejection of a gate component CONFIRMS the arm clears its
  §4.5 safety gate (component null H₀: π_a ≤ π₀). **Size discipline
  (Rev7/R7f, per the citation-`[SV]` conditions):** the IUT is a VALID
  level-γ test of the union null but is CONSERVATIVE — its size is ≤ γ, and
  no exact-size claim is made for any conjunctive claim null in this family;
  exact size = γ holds ONLY for the individual TOST component pairs inside
  the C-FMT-c claims (Berger & Hsu 1996: the two one-sided component tests),
  never for the C-FMT-c union nulls themselves, nor for C-VAL, C-DEF-NSUP,
  C-DEF-SUP, C-CON-SUP-c, or C-GRAPH. Every COMPONENT p-value must be valid —
  super-uniform under its component null, P(p ≤ u) ≤ u for all u — under the
  R7a analysis-ledger definitions below; no independence between components
  is needed or assumed.

  | # | Claim | H₀ (union of one-sided components) | Rejection confirms |
  |---|---|---|---|
  | 1 | **C-VAL** (validity conjunction) | ∪ over 7 components: Δ^SH_a ≤ δ_S for a ∈ {T, A1, A2, A2-IR, H} on the natural-stratum UCT macro-BA, and for a ∈ {H, A2-IR} on the nonce primary composite | every decision-path arm carries concept-specific signal on its claim-relevant endpoint. C-VAL gates the WHOLE family — deliberately including deflation: a family whose real-vs-shuffled contrasts are unresolved has shown no artifact signal, and §3.1's conditional-adoption default (text governs while construction is unearned) already covers that world without a confirmatory claim |
  | 2 | **C-DEF-NSUP** (deflation, noninferiority-of-T) | ∪_c {Δ^UCT_c ≥ m_T} — 4 components | no candidate beats T by margin m_T; with the §4.8 LCC rule (an operational-policy filter, NOT an IUT component — R7b) this fires deflation row 3's "T noninferior to every candidate within m_T with lower LCC" branch (the one-sided direction is the scientifically operative one for deflation — nothing meaningfully better than the text store exists; renamed from "equivalent with lower LCC" in Rev7) |
  | 3 | **C-DEF-SUP** (deflation, strict) | ∪_c {Δ^UCT_c ≥ −δ_T} — 4 components | T strictly superior to EVERY candidate → deflation regardless of LCC; its rejection region is nested inside C-DEF-NSUP's (same statistics, stricter bounds, δ_T ≥ m_T), so the fixed C-DEF-NSUP → C-DEF-SUP sub-sequence loses no power |
  | 4–7 | **C-CON-SUP-c**, one claim per c ∈ {H, A2-IR, A2, A1} | {Δ^UCT_c ≤ δ_T} ∪ {π_c ≤ π₀} — 2 components each | candidate c beats T at margin δ_T AND clears its safety gate — the constructed-adoption trigger. The four claims form the simultaneous candidate block (Bonferroni-split local levels via the graph weights), so the read-out for the hierarchy-selected candidate is pre-registered whatever the hierarchy selects (the R5b simultaneous-inference device, now in elementary form) |
  | 8 | **C-GRAPH** (H-GRAPH advancement) | {Δ^G ≤ δ_G} ∪ {π_H ≤ π₀} ∪ {π_A2-IR ≤ π₀} — 3 components | explicit graph materialisation/closure beats the flat-IR control at +0.08 with both arms safety-gate-cleared (oracle-IR upper-bound mechanism claim, §3.2 scope) |
  | 9–12 | **C-FMT-c**, one claim per c ∈ {H, A2-IR, A2, A1} | ∪_f {Δ^F_{c,f} ≥ m_F} ∪ ∪_f {Δ^F_{c,f} ≤ −m_F} — 4 components each (the TOST pairs for both formats) | T′(c) equivalent to BOTH native formats of c's shipping record on the SINGLE Stage-2 endpoint → prose shipping licensed. One claim per candidate = every candidate-arm × format contrast covered simultaneously (H-TEXT-FORMAT selection validity, R6d). Testable only if Stage 2 runs (weight strands harmlessly otherwise, item 4) |

  **Parameter ledger (unique — closing the Rev5 duplication/coverage defect):**
  24 distinct parameters: 7 shuffle contrasts, 4 UCT candidate contrasts, 1
  graph composite contrast, 4 gate-pass rates (π_H, π_A2-IR, π_A2, π_A1), 8
  format contrasts. A parameter (π_H, say, or Δ^UCT_c) may appear as a
  component of several claims exactly as any shared parameter may: components
  bear NO alpha — FWER control is over the 12 CLAIMS, each a single
  well-defined null hypothesis. Gates are therefore not separate alpha-bearing
  hypotheses "counted repeatedly"; each confirmatory claim simply names, as
  IUT components, the gates that govern IT (§4.5). Arms B, T, T′, A0, E, and
  the shuffles bear no gate components because no Rev6 confirmatory claim
  asserts their record quality: B, A0, and E are descriptive from Rev6 (item
  6); T has no constructed record; T′ inherits its record's gates through the
  upstream C-CON-SUP-c; shuffles are exempt by design (§4.5). Every
  component's endpoint and stratum are pinned in the table — no shuffle
  contrast is endpoint-ambiguous (the Rev5 E1 defect).

  **(1b) ANALYSIS LEDGER — executable inferential definition for EVERY
  component (NEW in Rev7/R7a; the Rev6 re-review §1 concrete fix;
  COMPLETED in Rev8/R8a–R8c — one arm-side representation shared with the
  SIM-SPEC DGM, exact inference pins with a named reference
  implementation, published rotations, and the replaced crossed-binary
  gate test; all [STIPULATED]).** The Rev6 wording "model-based one-sided p + BCa" was not an
  executable inferential definition; this ledger replaces it. **Generic
  definitions shared by every continuous component:** let θ̂ be the REML
  estimate of the component's contrast θ from its family's pinned mixed model
  below, SE(θ̂) its model-based standard error, and ν̂ the **Satterthwaite
  denominator degrees of freedom** for that contrast (Satterthwaite is the
  ONE pinned df method — no alternative is permitted). **Exact inference
  pins (NEW in Rev8/R8b — "REML + Satterthwaite" alone is not a unique
  algorithm for crossed models; these pins close it):** (a) *estimator:*
  REML = the maximizer of the standard Gaussian restricted log-likelihood
  over the variance components of the family's pinned model, subject to the
  **nonnegativity boundary constraint** σ²_m ≥ 0 for every component
  (boundary solutions are retained as-is — no refitting with the component
  removed, no negative estimates); (b) *fixed effects and SE:* θ̂ and
  SE(θ̂) are the generalized-least-squares estimate and model-based
  standard error at the REML variance estimates; (c) *variance-component
  covariance:* the asymptotic covariance matrix of the variance-component
  estimates is the inverse of the EXPECTED (REML) information matrix
  I_mn = ½·tr(P Z_m Z_mᵀ P Z_n Z_nᵀ) (P the usual REML projection matrix),
  with rows/columns of components estimated on the zero boundary retained;
  (d) *Satterthwaite formula (Giesbrecht–Burns):*
  ν̂ = 2·[Var̂(θ̂)]² / (gᵀ Ĉ g), where g is the gradient of Var(θ̂) with
  respect to the variance-component vector evaluated at the REML estimate
  and Ĉ the covariance from (c) `[LIT-BACKED — Giesbrecht F.G. & Burns
  J.C., "Two-stage analysis based on a mixed model: large-sample
  asymptotic theory and small-sample simulation results", Biometrics
  41(2):477–486 (1985); Satterthwaite F.E., Biometrics Bulletin 2:110–114
  (1946); supporting-only per §5 — the load-bearing check is the reference
  implementation + SIM verification]`; (e) *ONE named reference
  implementation (the executable definition of (a)–(d)):* **R 4.4.1 with
  lme4 v1.1-35.5 (`lmer`, REML = TRUE, default bobyqa/Nelder-Mead
  optimizer settings) and lmerTest v3.1-3 (ddf method "Satterthwaite",
  one-degree contrast tests via `contest1D`)** `[LIT-BACKED — Kuznetsova
  A., Brockhoff P.B., Christensen R.H.B., "lmerTest package: tests in
  linear mixed effects models", Journal of Statistical Software 82(13),
  2017; supporting-only]`; any other implementation (the SIM-SPEC engine,
  the production analysis software) is admissible ONLY if it reproduces
  the reference implementation on the pinned S4.2 fixture within the
  pinned tolerances (|Δθ̂| ≤ 1e−7 absolute; relative SE difference
  ≤ 1e−5; relative ν̂ difference ≤ 1e−3; |Δp| ≤ 1e−6). For an upper component
  null H₀: θ ≥ θ₀ the one-sided p-value is p = F_{t,ν̂}((θ̂ − θ₀)/SE(θ̂));
  for a lower component null H₀: θ ≤ θ₀ it is
  p = 1 − F_{t,ν̂}((θ̂ − θ₀)/SE(θ̂)). **Matching confidence-bound inversion
  (exact test–CI duality, pinned):** at local level γ, an upper null is
  rejected iff the one-sided 1−γ upper bound U = θ̂ + t_{1−γ,ν̂}·SE(θ̂)
  satisfies U < θ₀; a lower null is rejected iff the one-sided 1−γ lower
  bound L = θ̂ − t_{1−γ,ν̂}·SE(θ̂) satisfies L > θ₀ — the reported
  claim-level bound IS the inversion of the deciding test at the claim's
  final procedure-assigned level, never a differently-constructed interval.
  **BCa is retired from every confirmatory decision**: BCa intervals remain
  descriptive reporting only. **Seed aggregation rule (uniform):** no
  pre-averaging anywhere — every observational unit enters its model and
  seeds/consumers are marginalised only through the fitted model. **Software
  (Rev8/R8b):** the NAMED reference implementation in pin (e) above is the
  executable oracle for these definitions; the SIM-SPEC §S2/§S4 engine and
  the production analysis software (pinned at freeze) must each reproduce it
  on the pinned S4.2 fixture within the pinned tolerances.
  Per-family ledger:

  - **(A) UCT contrast components** — Δ^UCT_c (c ∈ {H, A2-IR, A2, A1};
    components of C-DEF-NSUP, C-DEF-SUP, C-CON-SUP-c) and the five
    natural-stratum C-VAL shuffle components Δ^SH_a (a ∈ {T, A1, A2, A2-IR,
    H}). *Estimand population/stratum:* mean paired difference in three-label
    macro-BA (c − T, resp. a − S(a)) over the natural-sense population
    represented by the pinned §4.2 stratum-2 sample, marginal over the pinned
    author-seed distribution and the consumer population, narrowed to the
    pinned renderer families/snapshots (fixed levels). *Observational unit:*
    one scored UCT consumer session Y_{a,i,s,k} (arm a, concept i, author-seed
    s, consumer k) — ARM-SIDE LONG FORM; the DGM generates and the analysis
    fits this SAME representation (Rev8/R8a). *Model formula:*
    Y = α_a + b_i + (ab)_{a,i} + v_s + (av)_{a,s} + u_k + ε, with concept
    b_i, concept×arm (ab)_{a,i}, author-seed v_s, seed×arm (av)_{a,s}, and
    consumer u_k independent random intercepts and arm α_a fixed
    (the (av) term completes the R7a formula: the Rev7 difference-form
    "v_s" was implicitly the seed×contrast interaction, which the arm-side
    model represents as (av) — R8a); θ = α_c − α_T (resp. α_a − α_{S(a)}).
    NO reviewer term: the UCT endpoint is consumer-scored, not
    review-scored — reviewer influence on record content is carried by
    (ab)/residual, stated. *Consumer assignment-rotation (PUBLISHED —
    Rev8/R8a; formerly "pinned" without an algorithm):* index the UCT arms
    0…9 in the fixed order (T, A1, A2, A2-IR, H, S(T), S(A1), S(A2),
    S(A2-IR), S(H)) and the concepts 0…I−1; record (a, i, s) is scored by
    consumer **k(a, i, s) = (uct_arm_index(a) + i) mod n_consumers**
    (independent of s). Properties (each load-bearing and checkable): every
    record scored in exactly one session; for fixed i distinct arms map to
    distinct consumers, so no consumer answers one concept under two arms
    (the §4.5 constraint); with n_consumers | I (24 | 48 and 24 | 96 ✓)
    every consumer scores exactly I/n_consumers concepts × n_seeds sessions
    per arm, so consumer effects cancel EXACTLY in every arm contrast;
    same-(a,i) seed variants share a consumer, which the §4.5 constraint
    permits (cross-arm exposure is what it forbids) and whose campaign-side
    carryover handling remains the unchanged R5b pins. *Estimator/df/p/
    bound:* the R8b exact inference pins; generic definitions at
    θ₀ ∈ {m_T, −δ_T, δ_T, δ_S} per the claim table.
  - **(B) Nonce-composite components** — Δ^G (C-GRAPH), the two nonce
    C-VAL shuffle components, and (descriptive/selection-only, same fit)
    the rung increments and the E-arm contrast Δ^E. *Estimand:* mean paired
    per-record difference in the §4.5 floor-imputed primary composite
    (H − A2-IR, resp. a − S(a)) over the nonce-concept population, marginal
    over the pinned seed distribution and the reviewer pool. *Observational
    unit:* one record-level composite score Y_{a,i,s} (arm a, concept i,
    author-seed s) — ARM-SIDE LONG FORM (Rev8/R8a; the Rev7 record-pair
    difference d_{i,s} is RETIRED as the fitted unit because it cannot
    represent the crossed reviewer factor, whose assignments do not cancel
    pairwise); seeds are MATCHED across arms (one pinned seed list), so
    every contrast is estimated from exact within-(i,s) pairing inside the
    one fit. *Model:* Y = α_a + b_i + (ab)_{a,i} + v_s + (av)_{a,s} +
    w_{r(a,i)} + ε, with reviewer w_r a crossed random intercept defined on
    REVIEWED arm-records only (arms A1, A2, A2-IR, H; structurally absent —
    a zero column, not a zero-variance level — on A0, E, T-side, and
    shuffle records, which are unreviewed/exempt by design §4.5); this
    implements §4.6's "reviewer modelled on review-based endpoints"
    consistently with the DGM (R8a). *Reviewer assignment-rotation
    (PUBLISHED — R8a):* index the reviewed arms 0…3 in the fixed order
    (A1, A2, A2-IR, H); the reviewer of every record of (arm a, concept i)
    is **r(a, i) = (rev_arm_index(a) + i) mod n_reviewers**. Properties:
    for fixed i distinct reviewed arms map to distinct reviewers (no
    reviewer sees competing records of one concept); with
    n_reviewers | n_nonce (8 | 96 and 8 | 160 ✓ — n_reviewers is re-pinned
    6 → 8 in S3 for exactly this balance, logged reason there) every
    reviewer reviews equally many records per arm, so reviewer effects
    cancel exactly in every reviewed-vs-reviewed contrast (e.g. Δ^G).
    *Estimator/df/p/bound:* the R8b pins; generic definitions at
    θ₀ ∈ {δ_G, δ_S}.
  - **(C) Gate components** — π_a (a ∈ {H, A2-IR, A2, A1}); **REPLACED
    AGAIN in Rev8/R8c**: the Rev7 linear-probability Gaussian LMM with
    REML/Satterthwaite t calibration applied to Bernoulli indicators does
    NOT deliver the super-uniformity the graphical procedure requires
    (Gaussian-residual t calibration does not follow for thresholded-normal
    binary data — the spot-check §5 finding), and is retired together with
    its under-specified DGM. (The Rev7 grounds for retiring the exact
    binomial stand unchanged: record-level indicators are not iid under
    crossed effects.) *Estimand population/stratum (unchanged from R7a):*
    π_a is the marginal record-level probability that arm a's record passes
    ALL §4.5 hard gates, over the PRIMARY (nonce) stratum's concept
    population and the pinned seed distribution; the natural-stratum
    gate-pass rate is reported descriptively only. *Observational unit:*
    one record's pass indicator g_{a,i,s} ∈ {0,1} — never collapsed to a
    concept-level indicator. *Working latent model ([STIPULATED] — shared
    IDENTICALLY by this test and the SIM-SPEC S4.4 DGM, closing the
    model/test mismatch):* g_{a,i,s} = 1{Z_{a,i,s} > Φ⁻¹(1 − π_a)} with
    standard-normal latents whose correlation is
    Corr(Z, Z′) = ρ_c·1[same concept] + ρ_s·1[same seed] +
    ρ_r·1[same reviewer r(a,i)] for distinct records (nonnegative
    dependence parameters; reviewer per the family-B rotation — the gate
    indicator is a review-based endpoint, so reviewer is modelled, R8a);
    marginal-π mapping: P(g = 1) = π_a exactly, by construction of the
    threshold. *Test (preregistered crossed-binary procedure):* statistic
    T_gate = π̂_a = mean of g over the arm's I·S records. Nuisance
    estimation (pinned): with π̄ = π̂_a, estimate pairwise concordances by
    class — Q̂_cr over same-concept pairs (which under the rotation always
    share the reviewer), Q̂_r over same-reviewer/different-concept/
    different-seed pairs, Q̂_s over same-seed/different-reviewer/
    different-concept pairs; invert each through the bivariate-normal
    orthant probability P₁₁(ρ; π̄) = P(Z₁ > z, Z₂ > z), z = Φ⁻¹(1 − π̄)
    (monotone in ρ; bisection to |Δρ| ≤ 1e−6) to get ρ̂_r (from Q̂_r),
    ρ̂_c = max(0, ρ̂_cr − ρ̂_r) (from Q̂_cr), ρ̂_s (from Q̂_s) (all pins
    [STIPULATED]). *Conservative bootstrap plug-in (REPLACES the Rev8
    truncate-to-0 plug-in — Rev9/R9a):* the dependence triple fed to the
    null bootstrap is the FLOORED triple ρ̃, built from ρ̂ by the pinned
    order (i) FLOOR the two small-cluster components —
    ρ̃_s = max(ρ̂_s, ρ_floor), ρ̃_r = max(ρ̂_r, ρ_floor) with
    **ρ_floor = 0.15** [STIPULATED — 1.5× the S3 planning fractions
    f_seed = f_reviewer = 0.10; consistency rule: any freeze-time re-pin
    of f_seed or f_reviewer above ρ_floor/1.5 re-pins ρ_floor to 1.5× the
    new fraction and re-runs the S4.4 battery]; ρ̃_c = ρ̂_c (no concept
    floor — asymmetry rationale below); (ii) clip each component into
    [0, 0.98]; (iii) if ρ̃_c + ρ̃_s + ρ̃_r > 0.98, rescale proportionally
    to sum 0.98. *Why a floor, and why only on seed/reviewer
    ([MEASURED] defect + [STIPULATED] remedy):* the (B) mock build
    measured (`poc/99a-sim/SPEC-DEFECTS.md` A4) that the Rev8 rule —
    per-replication hard truncation of a no-root/negative concordance
    excess to 0, fed directly to the bootstrap — biases the SMALL
    dependence components downward per replication (their noisy
    concordances often dip below the independence floor), UNDER-dispersing
    the null bootstrap and inflating rejection (~0.075 at γ = 0.025 vs
    the 0.031 bar), while the same bootstrap fed the TRUE dependence is
    well-calibrated; a downward-biased dependence plug-in is exactly the
    anti-conservative direction, because the bootstrap null's dispersion
    — and hence its rejection threshold — is monotone INCREASING in every
    dependence component (each pair-class covariance
    P₁₁(ρ; π₀) − π₀² increases in ρ at the fixed exact marginal π₀).
    The floor makes small-dependence mis-estimation err toward
    OVER-dispersion (the super-uniform direction) precisely on the two
    components that (a) dominate Var(π̂) — π̂ averages over only n_seeds
    = 3 seed and n_reviewers = 8 reviewer clusters, so their dependence
    terms carry O(1/S) and O(1/n_rev) weight vs O(1/I) for concept — and
    (b) are per-replication near-inestimable for the same reason (few
    exchangeable clusters ⇒ concordance noise straddles the truncation
    boundary at small true dependence). The concept component keeps the
    adaptive point estimate: at the S3 planning fraction 0.50 it sits far
    from the truncation boundary, rests on hundreds of same-concept
    pairs, and its Var(π̂) contribution is O(1/I) — its estimation noise
    was measured immaterial to the dispersion failure. Above the floor
    the estimate is used as-is (adaptivity to strong dependence
    retained). *p-value (parametric bootstrap at the null boundary):*
    draw B_boot = 999 bootstrap datasets from the working latent model
    with marginal EXACTLY π₀ and the FLOORED (ρ̃_c, ρ̃_s, ρ̃_r) (R9a) —
    directly as
    Z* = √ρ̃_c·b*_i + √ρ̃_s·v*_s + √ρ̃_r·w*_{r(a,i)} +
    √(1 − ρ̃_c − ρ̃_s − ρ̃_r)·e*, all components iid standard normal — and
    compute p = (1 + #{π̂*_b ≥ π̂_a}) / (B_boot + 1), the exact-validity
    Monte-Carlo form `[LIT-BACKED — Davison A.C. & Hinkley D.V., Bootstrap
    Methods and their Application, CUP 1997, §4.2.5 (parametric-bootstrap
    p-values) and the (1+#)/(B+1) Monte-Carlo test construction (Barnard
    1963, JRSS-B 25:294); supporting-only per §5 — the load-bearing
    evidence is the mandated calibration battery below]`; the composite
    null π_a < π₀ makes the boundary test conservative. Reject the lower
    null H₀: π_a ≤ π₀ at local level γ iff p ≤ γ. *CI inversion (exact
    test–CI duality, campaign analysis):* the reported claim-level lower
    bound is the largest π₀′ with p(π₀′) ≤ γ, found by bisection over π₀′
    to tolerance 1e−4 (each candidate re-running the bootstrap on its own
    pinned substream; the floored ρ̃ is computed ONCE from the data and
    reused at every candidate π₀′ — dependence estimation never touches
    π₀, R9a). *Fitting-failure handling (pinned):* an empty
    concordance class is impossible under the pinned design; if a
    concordance inversion has no root in [0, 0.98] (Q̂ below the
    independence value), set that POINT estimate ρ̂ = 0 — harmless since
    Rev9: for the seed/reviewer components the floor then binds (a zero
    read never reaches the bootstrap), and for concept the O(1/I)
    dispersion weight makes it immaterial (R9a); the bootstrap itself
    cannot fail. *Validity posture of the floored test (honest
    statement — R9a):* with KNOWN dependence the null-boundary
    Monte-Carlo p is exactly super-uniform by exchangeability (the
    retained (1+#)/(B+1) construction, [LIT-BACKED] as cited above,
    supporting-only per §5); with estimated dependence the floor turns
    the measured failure mode (dependence understated ⇒ under-dispersed
    null ⇒ anti-conservative) into its conservative mirror — whenever
    true seed/reviewer dependence ≤ ρ_floor the bootstrap null is
    over-dispersed by the dispersion monotonicity above, the
    super-uniform direction (a [STIPULATED] working-model argument) —
    and the composite null π_a < π₀ keeps the boundary test conservative
    in its interior; finite-sample level control remains DEMONSTRATED by
    the battery, never assumed. Scope disclosure: the battery stresses
    the floor-binding regime (true seed/reviewer dependence at the S3
    planning fractions, below the floor) — exactly the regime the A4
    measurement identified as failing; for above-floor truth the plug-in
    is adaptive and sits away from the truncation boundary (where its
    mean-concordance inversion was [MEASURED] unbiased —
    `poc/99a-sim/SPEC-DEFECTS.md` A4), a disclosed scope statement, not
    a demonstration. *Calibration (demonstrated level control —
    mandatory):* the SIM-SPEC gate-calibration battery (S4.4) runs this
    exact FLOORED test (R9a) at π_a = π₀ across the pinned dependence
    grid and ACCEPTANCE requires the realised component rejection rate's
    exact one-sided 95% upper bound ≤ 1.25·γ at both audited γ levels —
    level control is DEMONSTRATED, not assumed — with the S4.4 mandatory
    dispersion diagnostics reported alongside (R9a); B_boot's
    granularity 1/(B_boot+1) = 0.001 resolves the smallest procedure
    local level (0.00625). The Rev7 LPM caveat text and its
    cluster-bootstrap robustness read are retired with the LPM test.
  - **(D) Format components** — Δ^F_{c,f} (TOST pairs of C-FMT-c).
    *Estimand:* mean paired per-record difference in Stage-2 host three-label
    macro-BA (T′(c) − f(c)) on the NATURAL stratum (the pinned C-FMT target
    stratum — §4.1/R7d), marginal over the pinned seed distribution, under
    the pinned host (fixed level). *Observational unit:* one host-evaluation
    score Y_{g,i,s} of format version g ∈ {T′(c), AST(c), VEC(c)} — ARM-SIDE
    LONG FORM over format versions (Rev8/R8a). *Model:*
    Y = α_g + b_i + (gb)_{g,i} + v_s + (gv)_{g,s} + ε (host-scored: no
    reviewer, no consumer — stated); θ = α_{T′(c)} − α_{f(c)}.
    *Estimator/df/p/bound:* the R8b pins; generic definitions at
    θ₀ ∈ {m_F, −m_F} — the two one-sided TOST components.

  **Validity status of the component p-values (honest statement):** under
  each component null the continuous-family t-based p-values are
  super-uniform under the [STIPULATED] working model (Gaussian random
  effects and residuals), and the gate-family parametric-bootstrap p-values
  are asymptotically exact at the null boundary under the [STIPULATED]
  thresholded-Gaussian working model (conservative in its interior), with
  finite-sample level control DEMONSTRATED by the mandated S4.4 calibration
  battery (Rev8/R8c); those model assumptions are exactly what the
  supplementary sign-permutation robustness read and the SIM-SPEC
  finite-sample verification (including the bounded-Beta regime) exist to
  probe. No independence between components is assumed anywhere (the
  graphical procedure needs none).

  **(2) The procedure and its cited validity proof.** The 12 claims are
  tested by the graphical multiple-test procedure of Bretz, Maurer, Brannath
  & Posch `[LIT-BACKED — Bretz F., Maurer W., Brannath W., Posch M., "A
  graphical approach to sequentially rejective multiple test procedures",
  Statistics in Medicine 28(4):586–604 (2009): the sequentially rejective
  graphical procedure with nonnegative initial weights summing to ≤ 1,
  nonnegative transition weights with zero diagonal and row sums ≤ 1, and the
  standard weight-update algorithm is a shortcut of a CLOSED TESTING
  procedure (Marcus, Peritz & Gabriel 1976, Biometrika 63(3):655–660) with
  weighted-Bonferroni intersection tests, and controls the familywise error
  rate in the STRONG sense at level α under arbitrary dependence between the
  test statistics; source-verification of both papers is a pre-freeze
  obligation under §5's rule — the procedure is load-bearing and is the ONE
  deliberate exception to §5's supporting-only posture, which is why its
  conditions are also re-verified item-by-item here and its behaviour is
  additionally simulated (SIM-SPEC)]`. **Condition-by-condition verification
  for this design:** (i) every graph node is ONE elementary hypothesis with a
  valid (super-uniform) level-γ p-value — every component's executable
  definition is the R7a ANALYSIS LEDGER in (1b) above (one-sided t from the
  registered crossed mixed model with Satterthwaite df and exact test–CI
  duality; gate components by the ledger's crossed-binary latent-probit
  parametric-bootstrap test with demonstrated level control — the exact
  binomial was RETIRED in Rev7 and the interim linear-probability LMM in
  Rev8/R8c; supplementary sign-permutation as a robustness read); union nulls via the
  IUT maximum, valid regardless of dependence (Berger 1982; CONSERVATIVE,
  size ≤ γ — R7f); (ii) initial weights are nonnegative and sum to 1
  (all mass on C-VAL); (iii) the transition matrix in (3) has nonnegative
  entries, zero diagonal, and every row sums to ≤ 1; (iv) the update rule in
  (4) is exactly the cited paper's algorithm; (v) weighted Bonferroni needs
  no dependence model, so the crossed random-effects correlation structure
  cannot invalidate the level — it only costs power, which SIM-SPEC
  quantifies; (vi) **combination structure documented (Rev7/R7f, per the
  citation-`[SV]` binding condition):** this 12-claim family has RESTRICTED
  combinations, not free combination — logical implications among the nulls
  exist and are recorded here: C-DEF-NSUP's null true (∃c: Δ^UCT_c ≥ m_T)
  IMPLIES C-DEF-SUP's null true (that Δ^UCT_c ≥ m_T > −δ_T); C-DEF-NSUP's
  null FALSE (∀c: Δ^UCT_c < m_T ≤ δ_T) IMPLIES every C-CON-SUP-c contrast
  null true; and each C-FMT-c's four components share two parameters
  pairwise (a TOST pair cannot have both members false). The graphical
  procedure's strong-FWER control is UNAFFECTED: the closed-testing shortcut
  applies a level-α weighted-Bonferroni test to EVERY intersection
  hypothesis, including intersections that are infeasible under the
  restrictions, so restrictions can only add conservatism, never
  anticonservatism — consistent with (and covered by) the no-exact-size
  discipline of R7f; no restricted-combination weight-sharpening (which
  COULD exploit the implications) is used or claimed. **Why the three-review recurring defect is structurally
  impossible here:** a true elementary null can never "remain behind" inside
  a released node, because a node IS one elementary null; if that null is
  true, its rejection — the only weight-releasing event — is itself the
  FWER-controlled error already counted by the closed-testing proof.
  Directions NOT in the family (inferiority reads, equivalence-kill reads,
  the item-6 downgraded contrasts) receive no confirmatory status, so no
  alpha is ever transferred on their behalf.

  **(3) Initial weights and COMPLETE transition matrix** (fraction VALUES are
  proposed and re-justifiable pre-freeze — under the cited theorem ANY
  nonnegative matrix with zero diagonal and row sums ≤ 1 preserves validity,
  so freeze-time tuning is provably safe; the STRUCTURE — all initial mass on
  C-VAL, C-VAL the only source node, no edge bypassing it — is NOT
  deferrable). Initial weight vector: **w₀ = (C-VAL: 1.00; all other claims:
  0.00)** — gatekeeping is mathematical: while C-VAL is unrejected, every
  other claim has local level zero, matching precedence rows 2 and 4. Entries
  not shown are zero.

  | From \ To | C-DEF-NSUP | C-DEF-SUP | C-CON-SUP-H | C-CON-SUP-A2IR | C-CON-SUP-A2 | C-CON-SUP-A1 | C-GRAPH | C-FMT-(same c) |
  |---|---|---|---|---|---|---|---|---|
  | C-VAL | 0.50 | — | 0.125 | 0.125 | 0.125 | 0.125 | — | — |
  | C-DEF-NSUP | — | 1.00 | — | — | — | — | — | — |
  | C-DEF-SUP | — | — | — | — | — | — | 1.00 | — |
  | C-CON-SUP-c (each of the four) | — | — | — | — | — | — | 0.50 | 0.50 |
  | C-GRAPH | — | — | — | — | — | — | — | — |
  | C-FMT-c (each of the four) | — | — | — | — | — | — | — | — |

  Edge rationale (all [STIPULATED]): C-VAL gates everything; the released
  alpha splits 50/50 between the deflation chain (C-DEF-NSUP → C-DEF-SUP)
  and the four-claim adoption block, because deflation is the dominant
  hypothesis while adoption is the multi-candidate side; C-GRAPH is reachable
  from BOTH worlds (strict deflation, and any candidate's adoption) because
  H-vs-A2-IR is a mechanism question that stays scientifically meaningful
  under deflation; each C-FMT-c receives weight only through ITS candidate's
  adoption claim (format is moot when text ships); C-GRAPH and the C-FMT-c
  are terminal — their weight strands on rejection, a deliberate simplicity
  choice (adding outgoing edges later is a valid freeze-time refinement under
  the theorem, never a structural change).

  **(4) Update algorithm (pinned; = the cited paper's algorithm):** total
  α = .05. Repeat: for every claim j with current weight w(j) > 0, test its
  null at local level w(j)·α (IUT claims: reject iff EVERY component's
  one-sided p ≤ w(j)·α); when claim j is newly rejected, add w(j)·G(j,k) to
  every claim k, set w(j) ← 0, delete j from the graph, and re-normalise the
  remaining edges by the standard graphical update rule; iterate until no new
  rejection fires. Alpha moves ONLY on rejection of a claim's own single null
  at its assigned local level — never on a "definitive classification",
  never on a zone label. Weight reaching a claim whose null can no longer be
  tested — a C-FMT-c when Stage 2 never runs — **strands harmlessly**: an
  untested null is never rejected, so conditional execution can only forgo
  rejections, never inflate error. A claim left unrejected is reported
  **descriptively only**, and nothing downstream of it regains confirmatory
  status; a claim outside this pinned 12-claim family can never be reported
  as confirmatory.

  **(5) Procedure-adjusted CONFIRMATORY DECISION bounds (wording corrected
  in Rev7/R7a per the Rev6 re-review §1 — "every confirmatory decision
  bound", NOT "every operative bound"):** every **confirmatory decision**
  bound in this document that formerly read "95% confidence bound" — the
  §4.1/§4.8 H-GRAPH advancement bound, every candidate-vs-T decision bound,
  every gate component — is the one-sided bound at the deciding claim's
  FINAL procedure-assigned level w_final·α, reported alongside the rejection
  as the claim-level confidence statement (the (1b) test–CI inversion; a
  claim-level statement, never a simultaneous confidence set — R7d). NOT
  every OPERATIVE threshold is procedure-adjusted, and this is deliberate
  and FWER-valid: **operational kills use nominal 95%, hierarchy selection
  uses one-sided 95%, and instrument gates use pinned standalone levels —
  none of these creates a positive confirmatory rejection** (kills and
  blocks only withhold or retract claims and adoption; selection only
  chooses WHICH pre-registered claim is read out; gate failure yields
  `INSTRUMENT-INVALID`, a no-claim outcome) — which is exactly why their
  exclusion from the procedure-adjusted family cannot inflate the
  confirmatory FWER. All descriptive/operational reads — four-zone labels,
  kill rules, and every item-6 downgraded contrast — use nominal 95%
  intervals explicitly labelled non-confirmatory (§4.8 Rev6 note). Exactly
  two families keep pinned standalone levels, both OUTSIDE the confirmatory
  family by construction:
  **§4.7 instrument gates** (failure yields `INSTRUMENT-INVALID`, never a
  confirmatory claim in either direction) and the **§4.6
  selection-hierarchy rung bars** (SELECTION-ONLY devices: their level
  affects which arm is selected, never the validity of the candidate-block
  decisions, which pre-registration of every candidate's claims covers).
  Holm correction remains for the fixed SECONDARY descriptive family only
  (a reporting courtesy at nominal levels) and never licenses any
  primary/dominant claim — unchanged from Rev3/R3d.

  **(6) Downgrade ledger (maintainer-sanctioned #59; every simplified,
  dropped, or downgraded claim explicit and justified — R6b; all
  [STIPULATED]):**
  - **A2-IR − A2 (input channel) and A2 − A1 (citation increment):
    confirmatory → DESCRIPTIVE.** Neither sits on the adoption path (adoption
    consumes only a candidate's own C-CON-SUP-c, whatever mechanism produced
    the candidate) nor on the deflation decision; they inform mechanism
    decomposition and future design only. Their confirmatory status is
    precisely what forced the unprovable ten-node composite machinery.
  - **A1 − A0 (H-REVIEW): confirmatory → DESCRIPTIVE.** H-REVIEW keeps its
    §4.1 hypothesis status; its KBUILD-0 read is descriptive, and a dedicated
    confirmatory test may be pre-registered in a follow-up experiment. (This
    openly reverses the Rev4 restoration, under #59.)
  - **H-HUMAN (E vs machines, Rev5 node E7): confirmatory → DESCRIPTIVE plus
    a conservative operational block.** Its only decision role is to BLOCK
    machine adoption (precedence row 5); blocking on a descriptive read is
    conservative with respect to false adoption, and no decision rule needs a
    positive confirmatory human-superiority claim. §4.8 row 5 fires
    operationally.
  - **A0 canon-readiness (Rev5 node E9): confirmatory →
    DESCRIPTIVE/EXPLORATORY.** KBUILD-0 can no longer CONFIRM A0 canon-ready;
    advancement toward canon-ready now requires its own future pre-registered
    test (§4.8 amended accordingly).
  - **T′-shuffle (Rev5 node E1b): confirmatory → DESCRIPTIVE** — a Stage-2
    instrument sanity read; §4.7 gates 5–6 already guard the Stage-2
    instrument with `INSTRUMENT-INVALID` teeth.
  - **Every equivalence/inferiority KILL direction (equivalence-to-shuffle,
    H ≈ A2-IR, text-inferiority): confirmatory → OPERATIONAL.** Kills and
    blocks only withhold or retract claims and adoption — they cannot create
    a false positive scientific claim, so removing them from the Type-I
    family is conservative; their cost is wrongly killed branches
    (power/branch loss), which SIM-SPEC quantifies. The report must label
    every fired kill "operational, descriptive-evidence", never a confirmed
    no-effect finding (§4.8 Rev6 note).
  - **Not downgraded:** the dominant deflation decision (C-DEF chain),
    constructed adoption (C-CON-SUP block), H-GRAPH advancement (C-GRAPH),
    validity gating (C-VAL), and the single-endpoint format claim (C-FMT
    block) — exactly the set of claims any §4.8 ADOPTION or ADVANCEMENT rule
    consumes. The Rev2 "T and/or T′" disjunction stays abolished — T
    (source) and T′ (format) remain separate claims with separate roles.

  **(7) Sequential interaction:** the Stage-1 sequential boundary and the §7
  Rung-0 rule remain **binding-futility-only with respect to confirmatory
  rejections** — no claim is rejected except at its single registered final
  analysis; interim looks can only remove future rejection opportunities, so
  early stopping is conservative for FWER, and its power cost is modelled
  exactly in SIM-SPEC. Early "superiority" stopping affects resource
  allocation only, never an early confirmatory rejection.

  **(8) Mandated simulation (freeze-blocking; specification COMPLETE in the
  ## SIM-SPEC section — R6e, REWRITTEN by R7e per the Rev6 re-review §5:
  full-pipeline DGM, programmatic truth derivation, coherent Monte-Carlo
  acceptance rule):** the freeze record must contain the run
  artifacts of the ## SIM-SPEC protocol executed against THIS exact
  implementation — the 12-claim family, IUT compositions, transition matrix,
  update algorithm, binding-futility boundaries including the §7/R6c
  route-by-look Rung-0 rule, hierarchy selection, and Stage-2 conditionality
  — demonstrating (i) **strong FWER ≤ .05 across the SIM-SPEC feasible
  null-configuration grid** within its Monte-Carlo error bound, and (ii) the
  **deflation-path and adoption-path power targets**. Per the Rev5 re-review
  this is a preregistration ACCEPTANCE ARTIFACT: it must be BUILT and RUN
  (task (B)) before any freeze, never merely declared "pinned at freeze".
  The infeasible Rev5 grid entry ("each single node's nulls false") is
  superseded: SIM-SPEC enumerates only FEASIBLE configurations — each
  parameter takes one true value, so no impossible
  superiority-and-inferiority-both-false state can be expressed.
  (PROPOSED-PREREG-ROW-99A-R3d, replaced by R4b, completed by R5a, superseded
  by R6a)
- **Decision thresholds:** advance H-GRAPH only on **rejection of claim
  C-GRAPH (Rev6/R6a)** — the H−A2-IR one-sided bound at the claim's final
  procedure-assigned level exceeds +0.08 on the primary composite JOINTLY with
  both safety-gate components (the H−A2 total effect is reported only as
  its decomposition, §4.1); **advance ≠ kill** — killing requires an
  operational equivalence/inferiority read or a fired futility boundary, never
  mere lack of superiority (§4.8, Rev4/R4e as re-labelled by R6b). The
  composite comparison is reached only through
  the R4c Level-1 hurdle (§4.5), whose arm-level safety gates are explicit
  IUT components inside the R6a claims. All gate thresholds that were
  bare points in the original (N ≤0.40; T−shuffled-T ≥0.20) become
  **pre-registered one-sided confidence-bound tests** (e.g. upper bound of N's BA
  below the leakage bound; lower bound of the T−S(T) difference above the
  sensitivity bound) — these are §4.7 INSTRUMENT gates at their own pinned
  standalone one-sided levels, explicitly OUTSIDE the confirmatory family
  (R6a item 5): their failure yields `INSTRUMENT-INVALID`, never a confirmatory
  claim.
- **Power (under the exact final analysis — Rev2 Finding 1a, rebuilt in Rev3 per
  cross-vendor MAJOR-5):** simulate before freeze from calibration data **under the
  exact final analysis model** — the crossed mixed-effects hierarchy above, the
  pre-registered sequential futility/superiority boundary, the winner-selection
  hierarchy, **and the full multiplicity procedure — in Rev6 the EXACT R6a
  implementation (the 12-claim elementary family, IUT compositions, the
  published transition matrix, binding-futility boundaries including the
  §7/R6c route-by-look Rung-0 rule), reporting BOTH the strong-FWER grid and
  the path-power targets per the ## SIM-SPEC protocol (R6e, rewritten by
  R7e: full-pipeline DGM, programmatic truth, coherent exact-bound
  acceptance with separated planning targets)** — never under
  simplified concept-only resampling.
  Requirements: ≥90%
  power for the +0.08 superiority effect; **≥90% power for every registered
  equivalence-type claim at its registered margin, stated at a specified true
  effect — normally zero** (the dominant deflation claim C-DEF-NSUP first —
  on the R4a UCT statistic at true effect zero for every candidate; and the
  C-FMT-c format equivalence at true effect zero: an equivalence-type margin
  generically demands more information than a superiority margin at matched error
  rates, so the dominant hypothesis must never be the only unpowered one); and a
  simulated **joint power for the full adoption path** (probability that every
  claim on the adoption path — C-VAL, the selected C-CON-SUP-c, C-GRAPH —
  rejects under the R6a procedure),
  reported in the freeze
  record. One preregistered escalation to a maximum of 160 nonce concepts **and 96
  natural senses (the natural escalation added in Rev4: the T-source decision
  statistic lives on the natural stratum, so its power target must be reachable
  there)**.
  **An equivalence margin may NEVER be widened because power is unreachable** —
  margins derive only from substantive-interchangeability arguments pinned
  pre-freeze; if a registered test cannot reach 90% power at the 160-concept maximum,
  the remedies are design change (more seeds/measurements per concept, variance
  reduction) or termination as `INSTRUMENT-INVALID` — never margin widening, never
  run-and-hope. The Rev2 clause permitting pre-freeze widening "to at most ±0.05" is
  **deleted as power-driven margin drift** (cross-vendor MAJOR-5).
  (PROPOSED-PREREG-ROW-99A-R2a, amended by R3e)
- **Generality over the pipeline, not one draw:** multiple author seeds/model snapshots
  per arm (count pinned pre-freeze); conclusions attach to the pinned pipeline
  *distribution* per §1.3 criterion 4, not to a single stochastic draw.
- **Selection-bias fix (hierarchy fully specified — Rev2, critique Finding 9; rungs
  re-anchored in Rev3 per cross-vendor CRITICAL-1; inference under selection made
  valid in Rev5 per re-review residual 2):** "best constructed arm" for the
  text contrasts is determined by a **fixed pre-registered comparison hierarchy**
  with each rung's bar and comparator defined: H clears iff the H−A2-IR lower
  confidence bound exceeds +0.08 (the primary rule); otherwise A2-IR clears iff the
  A2-IR−A2 lower bound exceeds its pinned input-channel margin; otherwise A2 clears
  iff the A2−A1 lower bound exceeds its pinned citation-increment margin; otherwise
  A1 clears iff the A1−A0 lower bound exceeds its pinned review-increment margin
  (all increment margins pinned pre-freeze from calibration — values deferrable,
  structure not). **Rev5/Rev6: the rung bars are SELECTION-ONLY
  devices at a pinned selection level (one-sided 95%), explicitly
  non-confirmatory** — the hierarchy chooses the comparison arm but confirms
  nothing; the validity of the candidate-vs-T decisions under this
  outcome-dependent selection is secured by pre-registering EVERY candidate's
  claims in the R6a family (the C-CON-SUP block at Bonferroni-split local
  levels; the C-DEF conjunctions over all candidates; the per-candidate
  C-FMT-c claims), which covers whichever arm the hierarchy selects; the
  Rev5 E7 simultaneous-set device is retired with H-HUMAN's downgrade to
  descriptive (R6b).
  **Fallback:** if no arm clears any bar, best-arm := A1; T′ renders
  A1's endorsed records for the format contrast; and the **T-source deflation
  contrast still runs against A1** (it never depended on a constructed winner —
  Rev3 CRITICAL-2), so H-TEXT-SOURCE cannot silently vanish exactly when
  construction is weakest, the case where deflation is most likely true
  (indeed the C-DEF conjunctions run over ALL candidates regardless of
  selection). Simultaneous coverage reported; never selected post hoc on the
  same outcomes. (PROPOSED-PREREG-ROW-99A-R2i, completed by R5a/R5b,
  elementary form by R6a)

### 4.7 Instrument gates `[STIPULATED — review-1 fix 4; PROPOSED-PREREG-ROW-99A-R1f]`

Failure of any gate yields `INSTRUMENT-INVALID`, not a substantive null:

1. **PACKET-IDENTIFIABILITY gate (operating level specified — Rev2, critique Finding
   6):** every scored label must be logically determined by the published packet alone,
   with `UNDERDETERMINED` defined **relative to what the packet supports, not what the
   concealed rule says**. A deterministic checker of entailment over free natural
   language does not exist, and no LLM may fill the role (gate 8), so the checker's
   operating level is stated: **a shared typed IR consumed by all renderer families**.
   Per claim, the deterministic checker verifies over the IR that the packet's evidence
   entails/contradicts/underdetermines the claim **as the gold label says**. The
   semantics→text step is then guarded not by sampling but by a **100% machine-verified
   round-trip on all claim-bearing evidence: render → deterministic parse-back →
   IR-equality**; any round-trip failure is an `INSTRUMENT-INVALID` rendering defect
   (this closes the gap where a rendering-loss item is semantically identifiable yet
   textually underdetermined and a constructor is scored wrong for correct
   packet-relative abstention). Gate 2's human paraphrase audit is retained for
   **naturalness only**, no longer as the identifiability guard. Gate 3's
   renderer-family separation and motif-overlap bounds are constraints on renderers
   **given** round-trip success: renderers must vary surface form while preserving
   parse-back, and a renderer family that can satisfy round-trip only through template
   rigidity that busts the gate-3 bounds **fails gate 3** — the gates compose,
   identifiability wins any declared conflict, and the conflict itself is reported.
   Claims failing the IR check are regenerated before freeze; a post-freeze failure
   invalidates the instrument. Without this gate a model can earn credit by guessing the
   hidden generator from prior/template cues. (PROPOSED-PREREG-ROW-99A-R2f)
2. **Gold gate:** the micro-world engine passes exhaustive rule/claim self-tests —
   including the §4.5 R(packet) enumeration over the pinned rule grammar (Rev3); a
   blinded 10% human paraphrase audit reaches ≥95% — scoring **naturalness/readability
   only** (identifiability is gate 1's 100% round-trip, not this sample — Rev2,
   critique Finding 6).
3. **Template/lexical-leakage audits (new):** evidence renderers and claim renderers come
   from **separate renderer families**; pre-registered lexical-overlap and template-motif
   statistics between packet text and claim text must stay under pinned bounds (the
   no-context control N cannot detect evidence-to-gold template leakage, so this is
   audited directly).
4. **Leakage gate:** N's balanced accuracy stays below the chance-region bound by the
   §4.6 confidence-bound rule; nonce labels and gold-rule hashes are created after
   preregistration and withheld from every constructor and reviewer.
5. **Reader-competence + assignment-sensitivity gates (Stage 2):** on calibration
   concepts, real T clears its one-sided lower bound (BA ≥0.70) and beats shuffled T by
   the confidence-bound version of the 0.20 margin.
6. **Oracle-rendering gate (new, Stage 2):** an exact-rule oracle record is rendered in
   **every arm's format**; the selected host must demonstrate competence on each format,
   so host selection cannot favour one representation.
7. **Coverage gate — evaluator vs constructor separated (fix):** every selected item and
   every construction failure stays in the denominator; no post-outcome attrition.
   **Invalid constructor output (e.g. A0 illegality — measured Framework-G legal yield
   was 13/50 [MEASURED]) is a substantive method failure and scores against the arm.
   Broken evaluator parsing/rendering is instrument failure** (≥99% evaluator-side
   parse/render success required, else `INSTRUMENT-INVALID` for the affected cells).
   Self-scoring of coverage by the constructing arm is prohibited.
8. **Independence gate (rewritten; extended in Rev2):** no LLM supplies **gold labels or
   endorsement decisions**; the Stage-2 host supplies predictions only (that is its
   role, not a breach); drafter model, host model, and auditing model are from pairwise
   different families; **and every renderer family (evidence and claim renderers alike)
   is disjoint from both the drafter family and the host family** (critique Finding 11
   — otherwise A-arms get a free same-family-idiom leak, exactly the "recognise its own
   idiom" failure mode §2 row (a) warns about; PROPOSED-PREREG-ROW-99A-R2k); reviewer
   independence per §1.2.
9. **Reviewer-reliability gate (new):** chance-corrected reviewer agreement on
   calibration records must clear a pinned bound with its CI, else the endorsement
   instrument — not the constructions — is invalid.
10. **Access/prereg-integrity gate (new):** any breach of preregistration or access
    controls (constructor or reviewer exposure to gold, rule hashes, or competing
    records) → `INSTRUMENT-INVALID`.
11. **UCT instrument gate (new — Rev5, re-review residual 2):** (i) chance-corrected
    packet-only labeler agreement on the natural-stratum gold clears a pinned bound
    with its CI — failure invalidates the natural-UCT instrument as a whole;
    (ii) every scored consumer passed the pinned per-format competence battery
    (§4.5 UCT execution pins) before unblinding; (iii) assignment/carryover
    integrity holds — access logs verify that no consumer answered the same
    concept under two arms, that claim generators never labeled, that gold
    labelers never saw the held-out source or any arm artifact, and that the
    Rev6 source-exposed descriptive labelers (§4.2/R6d) never saw the
    packet-relative gold, any arm artifact, or any consumer session. Any
    breach → `INSTRUMENT-INVALID` for the affected natural-UCT cells.
    [STIPULATED — PROPOSED-PREREG-ROW-99A-R5b, extended by R6d]

### 4.8 Kill rules, ambiguity handling, and precedence matrix `[STIPULATED — review-1 fix 4; PROPOSED-PREREG-ROW-99A-R1i]`

**Lifecycle-cost composite (LCC) — replaces the four-axis cheapness conjunction (Rev2,
critique Finding 1c; hardened in Rev3 per cross-vendor MAJOR-6):** a single pre-pinned
composite, every component **measurable
within the study**: authoring cost (drafter tokens/calls or human minutes), review cost
(blinded minutes + adjudication events), consumer cost (rendered tokens and, in Stage 2
only, verifier FLOPs), storage bytes, and the maintenance component, which is **named
the "one-revision-cycle cost" (ORC)** — the measured cost of one pinned revision cycle
(a pre-registered single-edit source change propagated through each arm's pipeline to a
re-endorsed record) — **and is never cited as evidence of full lifecycle cost** (Rev3,
cross-vendor MAJOR-6). Rev3 hardening of the composite's decision use (all
[STIPULATED — PROPOSED-PREREG-ROW-99A-R3f]):

- **Declared prices:** heterogeneous resources (human minutes, tokens, FLOPs, bytes,
  ORC) are converted using **declared prices/shadow prices pinned pre-freeze**, with
  the price sheet published in the freeze record — never implicit exchange rates.
- **Consistent shared-cost allocation:** shared upstream costs are allocated under a
  pinned allocation rule applied identically to every arm — in particular **T′ is
  charged all shared construction/review costs of the record it renders, and T is
  charged only its own governance costs** (CRITICAL-2).
- **Uncertainty and robustness:** every LCC-based decision reports an **uncertainty
  bound on the cost difference** and a **robustness sweep across a pre-registered set
  of plausible weight/price vectors**; a decision that reverses anywhere in the sweep
  is reported **`COST-INDETERMINATE`** and treated as indeterminate in the precedence
  matrix — never resolved by the point weights.

Component weights are pinned pre-freeze from externally justified grounds before any
outcome unblinding (the *weighting values* are a named deferrable; the composite's
*structure*, prices-declared rule, allocation rule, and robustness sweep are not). Any
maintenance consideration beyond the ORC proxy is reported descriptively and is
**excluded from every decision rule** — a conjunction containing an unmeasurable axis
can block deflation forever and is abolished. "Cheaper"/"lower cost" in this section
always means "lower LCC under the declared prices, robustness-stable".
[STIPULATED — PROPOSED-PREREG-ROW-99A-R2a, hardened by R3f]

**Rev6 epistemic-status note (R6b — governs every rule and matrix row below):**
kills, blocks, and cannot-advance outcomes are **OPERATIONAL decisions**, read
from the descriptive four-zone labels at nominal two-sided 95%; they are
deliberately NOT confirmatory FWER-protected claims. A kill/stop/block only
withholds or retracts claims and adoption — it cannot create a false positive
scientific claim — so removing kills from the confirmatory family is
conservative for Type-I error; its cost is wrongly killed branches, quantified
in the SIM-SPEC power grid. The report must label every fired kill
"operational, descriptive-evidence" and may never present it as a confirmed
no-effect/equivalence finding. The positive confirmatory claims are exactly
the §4.6/R6a 12-claim family; every ADOPTION or ADVANCEMENT rule below
consumes only R6a rejections. [STIPULATED — PROPOSED-PREREG-ROW-99A-R6b]

Kill/selection rules (revised to the new endpoint and arms):

- **H-GRAPH three-outcome rule (Rev4, re-review residual 5 — replaces "kill H-GRAPH
  if H fails to beat A2-IR", which contradicted precedence row 9):** **ADVANCE**
  H-GRAPH only on rejection of claim C-GRAPH (§4.6/R6a); **KILL** H-GRAPH only
  under an operational four-zone **equivalence or inferiority** read of
  H−A2-IR (the descriptive two-sided 95% CI — an OPERATIONAL kill per the Rev6
  note above, not a confirmatory claim — wholly inside ±0.05, or its upper
  bound < −0.08) or a fired pre-registered **futility** boundary;
  an **indeterminate** H−A2-IR outcome neither advances nor kills (precedence
  row 9) — the hypothesis stands unadvanced. Lack of demonstrated superiority
  blocks advancement; it is never itself a kill. Retain citation-constrained
  drafting if A2 beats A1.
- **Unreviewed-drafting canon-readiness (same advance/kill/indeterminate discipline
  — Rev4/R4e; wording completed in Rev5; DOWNGRADED to descriptive/exploratory
  in Rev6 — R6b):** the A0 canon-readiness read (A0 beats its shuffle at
  margin +0.05, unsupported-constraint precision lower bound ≥ 0.95, arm-level
  safety gate — all at nominal descriptive levels) is **reported only**;
  KBUILD-0 can no longer CONFIRM A0 canon-ready, and advancement toward
  canon-ready requires its own future pre-registered test. A0 is **killed as
  canon-ready** (operationally, per the Rev6 note) only on an operational
  equivalence-to-shuffle read or a fired pre-registered futility boundary. **A
  breached hard gate (§4.5 arm-level safety-gate failure) is a CANNOT-ADVANCE
  outcome, never a registered kill** — Rev5 takes the re-review's
  cannot-advance branch, replacing the Rev4 wording that listed a hard-gate
  breach as a kill event, so the R4e taxonomy (kills only via confirmed
  equivalence/inferiority or futility) holds without exception; any other
  outcome is indeterminate-not-advanced. `ModelAuthored` candidate role survives
  in every case.
- **Retain direct compilation** if A2-IR/A2/A1 and H are equivalent under the four-zone
  rule within ±0.05 and the direct arm has lower measured LCC.
- **Deflate to text** iff the **T-source decision** (§4.6) is **text
  superior** (C-DEF-SUP rejected), or **T noninferior to every candidate
  within m_T** (C-DEF-NSUP rejected — the branch renamed in Rev7/R7b: it is
  one-sided noninferiority of T, never two-sided equivalence) with lower LCC
  (uncertainty-bounded and robustness-stable — an operational-policy filter
  outside the IUT, §4.6/R7b). **T′ can never trigger deflation** — it is a
  format probe whose Stage-1 fidelity is true by construction (Rev3,
  cross-vendor CRITICAL-2).
- **Format verdict (new — Rev3, cross-vendor CRITICAL-2):** if T′ is equivalent to the
  winner's AST/vector formats under the Stage-2 consumers, the constructed record may
  *ship* prose-rendered; this is a format choice about an already-constructed record,
  never evidence that construction is avoidable.
- **Adoption-blocking rule (Rev2, critique Finding 1b; re-anchored Rev3):** an
  **indeterminate-zone** T-source outcome (or `COST-INDETERMINATE` on the deflation
  LCC) blocks **adoption** of any constructed arm (precedence row 4): fidelity
  contrasts are reported as findings, adoption is withheld, and the single preregistered
  escalation (§4.6) is triggered with the T-contrast's power as its primary target.
- **Kill all construction-specific content claims at this scope** if correctly assigned
  structured arms are equivalent to their shuffles.
- **Efficiency verdict is separate** and passes only under the end-to-end Pareto rule of
  §1.3 criterion 8.
- **Human-cost verdict (descriptive/operational from Rev6 — R6b):** if E
  matches machine-arm fidelity within ±0.05 at lower LCC on the descriptive
  read (uncertainty-bounded, robustness-stable), neither drafter nor graph has
  earned its complexity for this sector — an operational adoption BLOCK, not a
  confirmatory claim.

**Precedence matrix (pre-registered; resolves every previously-unhandled ambiguous
outcome):** ordered highest-precedence first — a higher row's verdict dominates any
lower row's.

| Pr. | Outcome pattern | Verdict |
|---|---|---|
| 1 | Any gate of §4.7 fails | `INSTRUMENT-INVALID` — no substantive claim in either direction |
| 2 | Structured arms ≈ their shuffles | Representations carry no concept-specific evidence at this scope; all construction claims die |
| 3 | **T-source decision = text superior (C-DEF-SUP), OR T noninferior to every candidate within m_T (C-DEF-NSUP) with lower LCC (robustness-stable; operational-policy filter — R7b)** | **Text deflation. Dominates every constructed-arm victory — explicitly including "H beats A2-IR but T noninferior to the winner at lower LCC". T′ can never fire this row (format probe only — Rev3 CRITICAL-2)** |
| 4 | **T-source decision in the indeterminate zone, or deflation LCC `COST-INDETERMINATE`** (above all constructed-arm rows — Rev2 Finding 1b, re-anchored Rev3) | **Constructed-arm ADOPTION BLOCKED.** No deflation claim; fidelity contrasts are reported as findings only; no constructed arm is adopted; the single preregistered escalation (§4.6) is triggered with the T-contrast's power as its primary target; if still indeterminate after escalation, adoption stays withheld. An unheard text control never reroutes to "constructed-arm verdicts stand" |
| 5 | E matches machines within ±0.05, lower LCC | Human-from-evidence baseline verdict; machine construction unearned for this sector |
| 6 | H beats A2-IR by primary rule AND LCC non-dominated | H-GRAPH supported **and adoptable as an oracle-IR upper-bound mechanism result** (scoped to tested sectors, packet-local per §3.2; production graph-import additionally requires the realistic text→IR extraction test per R3a; reachable only below rows 3–4, i.e. the text control spoke and did not win) |
| 7 | H beats A2-IR semantically but is dominated on LCC | Split verdict: fidelity supported, adoption unearned; graph stays hypothesis pending cost reduction |
| 8 | Graph reduces error but increases review time | Split verdict per pre-pinned fidelity-vs-review-cost trade rule (pinned pre-freeze from calibration) |
| 9 | H−A2-IR lower CI ≤ +0.08 AND the ±0.05 equivalence zone is not reached (four-zone indeterminate) | **Indeterminate — reported as indeterminate**; no adoption, no kill; one preregistered escalation (§4.6) or verdict stands as indeterminate |
| 10 | Nonce and natural strata disagree | Primary (nonce) verdict stands **scoped to evidence-compilation** — **for constructed-arm contrasts only; the T-source decision is governed by its R4a natural-stratum UCT statistic, and the nonce parse-back/UCT upper bounds can never override it (Rev4)**; natural-stratum disagreement is a pre-registered generalisation failure, blocking any natural-language scope claim |
| 11 | Effects reverse across concept types or reviewers | Heterogeneity verdict: report per-stratum with interaction CI; no pooled adoption claim |

**Rev6 row-to-claim mapping (R6a/R6b):** row 1 is unchanged (`INSTRUMENT-INVALID`
outranks everything). Row 2 and every equivalence-kill reading fire
OPERATIONALLY on descriptive four-zone reads (Rev6 note above). Row 3 fires on
rejection of C-DEF-SUP, or on rejection of C-DEF-NSUP — "T noninferior to
every candidate within m_T", the Rev7/R7b renaming — plus the LCC rule
(robustness-stable; an operational-policy filter outside the IUT, never a
confirmatory component). Row 4 is the no-rejection state — a non-claim consuming
no alpha; adoption stays blocked. Row 5 is a conservative operational block on
the descriptive H-HUMAN read (downgraded, R6b). Rows 6–9 consume C-GRAPH
(advancement) or operational reads (kills/indeterminacy) exactly per the Rev6
note. Rows 10–11 are reporting rules, unchanged. [STIPULATED]

**Rev8 operational-row pins (R8e — closing the spot-check's "claimed
operational decisions lack simulated inputs and exact algorithms"):**
(i) the **row-2 shuffle-equivalence margin is pinned at ±0.05**
(m_sheq = 0.05, planning default): row 2 fires iff, for EVERY candidate arm
a ∈ {A1, A2, A2-IR, H}, the descriptive two-sided 95% CI of its
natural-stratum shuffle contrast Δ^SH_a lies wholly inside ±m_sheq;
(ii) rows 5–9 are computed by the EXACT algorithms pinned in SIM-SPEC S4.9
(the normative operational-layer algorithms), over the DGM variables added
there for exactly this purpose — the E-arm fidelity contrast Δ^E, the
per-arm component COST VECTORS with their measurement noise, the
review-time component, and the price-vector cost-dominance reads; (iii) the
robustness sweep above is executed over the pinned set of PRICE VECTORS
applied to the per-arm component cost vectors (S4.9) — never over positive
scalar multiples of a single cost difference, which could not reverse sign
and therefore could never produce the `COST-INDETERMINATE` outcome this
matrix registers. [STIPULATED — PROPOSED-PREREG-ROW-99A-R8e]

Row ordering is load-bearing (Rev2): the inconclusive-text row sat at position 9 in
Rev1, *below* the constructed-arm verdict rows, so an underpowered text control let "H
beats A2" advance via row 5 — the exact back-door the demotion was supposed to close. It
now sits at position 4, above every constructed-arm verdict. [STIPULATED —
PROPOSED-PREREG-ROW-99A-R2a]

Cost: deterministic preprocessing, a few hundred drafter calls, a bounded human review,
human-authoring, and blinded claim-task consumer exercise (the R4a UCT sessions), and —
only if Stage 2 triggers — under a GPU-day of small-model
inference. Stage 1 spends no host inference at all. [STIPULATED]

## 5. Literature status: supporting-only, never load-bearing `[STIPULATED — review-1 fix 5; PROPOSED-PREREG-ROW-99A-R1j]`

Every literature citation in this document is **supporting-only**, with **ONE
deliberate, named Rev6 exception**: the multiplicity procedure's validity
citations (§4.6/R6a — Bretz, Maurer, Brannath & Posch 2009; Marcus, Peritz &
Gabriel 1976; Berger 1982; Berger & Hsu 1996) are **load-bearing by design**,
because the maintainer-ratified #59 decision requires a STANDARD, CITED
procedure with a known strong-FWER proof in place of bespoke theory. The
exception is triple-guarded: (i) the cited theorem's conditions are
re-verified item-by-item in this document (§4.6/R6a item 2), (ii) the
citations must pass the pre-freeze `[SV]` source-verification sweep before
any freeze, and (iii) the implemented procedure's behaviour must additionally
pass the ## SIM-SPEC simulation — so no verdict ever rests on the citation
ALONE. All other citations remain supporting-only: no other load-bearing
claim, gate, margin, or verdict rests solely on a citation; all rest on
[MEASURED] repository results plus [STIPULATED] design choices. Specifically:

- **~10% Grounding Kernel / ~1% alternative MinSets** [LIT-BACKED][SV]: illustrative of
  non-uniqueness only. The conclusion that dictionary convergence alone is not external
  grounding does not depend on these figures (and locally they are attributed to the
  Blondin-Massé / Vincent-Lamarre dictionary studies, not to Harnad 1990 —
  `reports/lit-primitives-grounding-priorart.md` [MEASURED]).
- **FCA lattice uniqueness up to isomorphism** [LIT-BACKED][SV]: a steelman for B's
  conditional reproducibility; if wrong or inapplicable to prose-extracted/scaled
  contexts, B is less attractive — the governance architecture is unaffected.
- **SAE non-identifiability/instability** [LIT-BACKED][SV]: supporting; even perfectly
  stable SAEs would show what a model represents, not what is correct; the [MEASURED]
  E8 one-positive-pair picture carries the local weight.
- **Harnad symbol-grounding distinction** [LIT-BACKED][SV]: conceptually important to the
  vocabulary; no gate or margin depends on it.

The `[SV]` verifications are now **COMPLETE** (Rev3 update): the repository sweep
(`docs/next/design/99a-rev2-sv-report.md`) confirmed both load-bearing repository
citations — the RULES-2 verdict with its verbatim claim cap
(`registry/verdicts/rules-2.json`) and the K-NULL reconcile's mechanism-envelope and
descriptive-by-design sentences
(`docs/next/analysis/knull-ufo-dual-model-reconcile-fable.md`) — and the external sweep
(`docs/next/design/99a-rev2-sv-report-extlit.md`) cleared all four supporting literature
claims; the cross-vendor review independently re-confirmed the citations. The
[LIT-BACKED] material nevertheless **remains supporting-only by design**: no gate,
margin, or verdict rests on it.

## 6. Honest uncertainty map

- **Settled by repository measurement [MEASURED]:** representation determinism ≠ semantic
  correctness (encoder); dictionary Core membership does not enrich NSM primes over a
  frequency-matched null (an INSTRUMENT-LIMITED ceiling null per its own source, §0b);
  plain aligned text matched the kernel store at ~0.565× verifier FLOPs (descriptive by
  design) in K-NULL's tested answer-string mechanism; **RULES-2's rules-line lift is
  content-driven (PASS, audit CONFIRMED, primary LB +0.316) under its permanent
  never-kernel-specific cap (§0b — Rev2, critique Finding 4)**; E8 has one positive
  cross-model pair and two non-replications; Framework-G legal yield was 13/50.
- **Settled by literature (pending [SV], supporting-only):** dictionary grounding-kernel
  non-uniqueness; FCA conditional uniqueness; SAE instability reports.
- **Open empirical (this is what KBUILD-0 buys):** H-GRAPH (explicit graph
  materialisation/closure increment over the flat-IR control — Rev4 C1 narrowing —
  oracle-IR upper bound); the A2-IR−A2
  machine-readable-input increment; H-REVIEW (value of the gate); H-TEXT-SOURCE (text
  deflation at this scope) and H-TEXT-FORMAT (shipping format); H-HUMAN (whether
  machine construction reduces expert cost); transfer from nonce compilation to
  natural senses; sector generalisation beyond formal/lexical.
- **Binding extrapolation caps (Rev3 — the cross-vendor review's residual-risk list,
  each cap load-bearing and enforced in the named section):** oracle-IR graph
  performance is never production graph-import performance (§3.2/R3a); unreviewed
  Rung-0 results never terminate the reviewed route without the conditional-futility
  rule (§7/R3h, completed by R4d, formalised as a simultaneous upper-bound stopping
  rule by R5c); the one-revision-cycle cost is never full lifecycle evidence
  (§4.8/R3f); nonce compilation results never extend to natural concepts or
  dictionary-scale convergence beyond the confirmatory stratum (§4.2/R2e); and the
  nonce oracle parse-back (and nonce UCT) are never the T-source decision — the
  decision statistic is the natural-stratum unconditional held-out claim task
  (§4.5/R4a, Rev4).
  [STIPULATED]
- **Philosophical (not decidable by any experiment here, and not claimed):** whether any
  symbol-anchored record is "grounded" in the strong referential sense; whether
  convention-constituted concepts need grounding at all (§1.1 separates these so the
  empirical programme does not pretend to answer them).

## 7. Sequenced experimental programme (cheapest-most-decision-relevant first)

Each rung: question / method / pass-fail / cost / decision-unblocked. Rungs are
[STIPULATED] proposals; none is registered.

0. **Rung 0 — machine-only screen (new — Rev2, critique Finding 12).** Q: do the two
   cheapest potential branch-killers fire before the **full human endorsement
   apparatus is stood up**? (Rev5 wording reconciliation, re-review residual 3: the
   earlier "before any human apparatus exists" contradicted the review-calibration
   pilot, which IS a small human exercise — the pilot is the one human component
   Rung 0 requires, and its cost is explicitly credited below.)
   "Cheapest-first" must count the human machinery, not GPU cost only. M: arms A0,
   unreviewed-A2 (A2 minus endorsement), **unreviewed-A2-IR and unreviewed-H (both
   "minus endorsement" — added in Rev4, re-review residual 4: without them the
   futility bound could not cover the IR/graph routes or the graph–drafter
   interaction)**, B, T, S, N — evaluator-scored against the exact
   rules; no reviewers, no endorsement protocol, no arm E; pre-registered sequential
   futility boundary. P/F (scope-limited — Rev3, cross-vendor MAJOR-8): preliminary
   forms of precedence rows 2 (structured ≈ shuffles) and 3 (text-deflation signal —
   the Rung-0 signal is the nonce parse-back **upper bound, a screen only, never the
   R4a T-source decision**),
   evaluated on **unreviewed routes only**. Rung 0 can kill *unreviewed* routes
   outright (A0, unreviewed-A2, unreviewed-A2-IR, and unreviewed-H as canon
   candidates), but it can **never by itself
   kill the reviewed methodology** — H-REVIEW explicitly hypothesises that review
   changes fidelity, so extrapolating unreviewed futility to the reviewed route is
   invalid. Killing the whole branch from Rung 0 additionally requires the
   **formal conditional-futility bound (Rev4 structure per residual 4; formalised
   as a mathematical stopping rule in Rev5, re-review residual 3 — "maximum
   credible" was not yet a bound):** for **every** reviewed route
   r ∈ {A1, A2, A2-IR, H} define

   > θ(r) = (unreviewed-r − T) + Δ_rev(r)

   where (unreviewed-r − T) is the Rung-0 evaluator-scored paired contrast on the
   nonce parse-back screen statistic, and Δ_rev(r) is route r's **maximum
   credible DIFFERENTIAL review increment relative to T**, estimated **with its
   uncertainty** from the **independent review-calibration pilot** (all pilot
   estimates pinned before Rung-0 unblinding). Compute for each route a
   **one-sided upper PREDICTION bound U(r) on θ(r)** that propagates BOTH
   uncertainty sources — the Rung-0 contrast's sampling uncertainty under the
   §4.6 crossed model narrowed to Rung-0's factors (concept × author-seed; no
   reviewer/consumer factors exist yet), and the pilot's estimation-PLUS-transfer
   uncertainty for Δ_rev(r) (a prediction bound, not merely a confidence bound,
   because the pilot's setting is not the campaign's) — with **simultaneous
   coverage over all four routes AND all interim looks** (Rev6/R6c; the Rev5
   Bonferroni α₀/4 covered routes only, which the Rev5 re-review correctly
   flagged as not validating the 1 − α₀ futility bound under repeated looks).
   **Route-by-look alpha-spending rule (R6c, pinned):** Rung-0 futility is
   evaluated at **L pinned interim looks** (L and the look times/information
   fractions are freeze-time pins; proposed default L = 3 at 40% / 70% / 100%
   of the Rung-0 concept budget n_max, which is IDENTIFIED with the
   configured nonce-stratum concept budget — n_nonce, or n_nonce⁺ under
   escalation — Rev8/R8f; **integer look sizes pinned by the rounding rule
   n_ℓ = ⌈φ_ℓ · n_max⌉ with the exact look-count table: n_max = 96 →
   (n₁, n₂, n₃) = (39, 68, 96); n_max = 160 → (64, 112, 160)**, closing the
   non-integer 40%/70% ambiguity); at look ℓ each route's bound U_ℓ(r) is
   computed at per-test level **α₀/(4·L)** — Bonferroni over the 4 routes × L
   looks, the pinned conservative default requiring no dependence model (any
   sharper group-sequential spending function is a freeze-time pin; the α₀
   value is a named freeze-time pin; the routes × looks simultaneity STRUCTURE
   is not deferrable). By the union bound the whole futility SEQUENCE has
   simultaneous coverage ≥ 1 − α₀: P(∃ ℓ, r: U_ℓ(r) < θ(r)) ≤ 4L · α₀/(4L)
   = α₀, so a fired termination asserts "every θ(r) < f" with simultaneous
   confidence 1 − α₀ across all looks and routes — the claimed bound now
   VALID under repeated looks.
   **Pilot-to-campaign transfer model and bound formula (R6c, pinned —
   replacing "propagates estimation-plus-transfer uncertainty" with an
   executable algorithm; the model is [STIPULATED] and stress-tested in
   SIM-SPEC §S6):** model the campaign review increment as
   Δ_rev(r) = δ_p(r) + b(r), where δ_p(r) is the pilot-estimated differential
   review increment (estimate Δ̂_rev(r), standard error s_p(r), from n_p
   pilot concepts under the pilot's paired design) and b(r) is the
   pilot-to-campaign transfer shift, bounded |b(r)| ≤ B(r) by the pinned
   deterministic **transfer envelope**
   B(r) = (κ_pool + κ_mix + κ_budget) · max(|Δ̂_rev(r)|, Δ_min), with
   κ_pool (reviewer-pool spread), κ_mix (concept-mix shift), κ_budget
   (time-budget ratio), and the floor Δ_min all pinned pre-freeze from the
   pilot design record. Then, with D̂_ℓ(r) the Rung-0 paired contrast
   estimate at look ℓ (on n_ℓ concepts, standard error SE_ℓ(r) from the §4.6
   crossed model narrowed to Rung-0's factors), the bound is

   > U_ℓ(r) = D̂_ℓ(r) + Δ̂_rev(r) + B(r)
   >          + t_{1 − α₀/(4L), ν̂(ℓ,r)} · sqrt( SE_ℓ(r)² + s_p(r)² )

   with ν̂(ℓ,r) the Welch–Satterthwaite degrees of freedom over the two
   variance components, **pinned exactly (Rev7/R7c — the formula and its
   component degrees of freedom, previously named but not written):**

   > ν̂(ℓ,r) = ( SE_ℓ(r)² + s_p(r)² )²
   >          / ( SE_ℓ(r)⁴ / ν_D(ℓ,r)  +  s_p(r)⁴ / ν_p ),

   where ν_D(ℓ,r) is the Satterthwaite denominator df of the Rung-0 contrast
   estimate D̂_ℓ(r) from the §4.6 crossed model narrowed to Rung-0's factors
   (concept × author-seed; planning value n_ℓ − 1 when the seed variance
   component is negligible, but the fitted Satterthwaite value is what is
   used, **computed by the R8b-pinned inference — the §4.6/(1b) exact REML/
   Giesbrecht–Burns pins and named reference implementation; Rev8/R8f closes
   the "unspecified mixed-model Satterthwaite" residual**), and
   ν_p = n_p − 1 is the pilot's df for s_p(r). Coverage argument:
   the deterministic envelope B(r) absorbs the transfer bias b(r); the t-term
   covers both estimation uncertainties at level 1 − α₀/(4L); hence
   P(θ(r) ≤ U_ℓ(r)) ≥ 1 − α₀/(4L) per (ℓ, r) under the stipulated working
   model, and the union bound gives the sequence-level guarantee above.
   **Conditionality statement (Rev7/R7c, per the Rev6 re-review §3 — stated,
   not buried):** the transfer bound is CONDITIONAL on (i) the deterministic
   assumption |b(r)| ≤ B(r), (ii) independence of pilot and campaign
   estimation errors, and (iii) correct calibration of the stated t/Welch
   approximation; it is NOT distribution-free, and B(r) is an
   assumption/sensitivity ENVELOPE — a stipulated design bound stress-tested
   in SIM-SPEC — never statistically learned coverage. The route-by-look
   Bonferroni itself (the union bound over 4·L per-test bounds) needs no
   dependence model; only the per-(ℓ,r) coverage is model-conditional.
   **Nested-interims requirement (Rev7/R7c, binding on task (B)):** the
   SIM-SPEC simulation must generate NESTED interim observations — look ℓ's
   estimate D̂_ℓ(r) is computed from the cumulative first n_ℓ concepts of ONE
   accruing dataset per replication, so consecutive looks share data exactly
   as the real monitoring sequence does — never independent per-look
   estimates. If any κ (or Δ_min) cannot be credibly
   pinned, Δ_rev(r) is UNBOUNDABLE and whole-branch termination is prohibited
   (rule retained verbatim below). **Branch termination is permitted ONLY at a
   pinned look ℓ with U_ℓ(r) < f for EVERY route r**, where f is the pinned
   futility threshold — the smallest screen-scale effect of interest, pinned
   pre-freeze; "maximum credible" is thereby a mathematical stopping bound
   valid across the whole monitoring sequence, not a judgment call.
   **Sequential-error accounting (Rev5, look-completed by R6c):** Rung-0
   futility looks occur only at
   the pinned interim points of the registered sequential plan and are
   **binding-futility-only** — a Rung-0 stop can only terminate, never confirm,
   so it cannot inflate the §4.6 confirmatory FWER (it is conservative for
   Type I error); its entire cost is branch-loss risk, which the ## SIM-SPEC
   simulation models exactly (boundary, looks L, α₀, f, the transfer envelope)
   so the freeze record quantifies it in the adoption-path power.
   **Human-cost crediting (Rev5):** the review-calibration pilot is a bounded
   HUMAN exercise; its blinded-review minutes and adjudication events are
   measured, charged to the branch's Rung-0 ledger, and reported in the Rung-0
   record — the pilot's cost is counted, never waved through as "machine-only".
   If any route's Δ_rev(r) cannot be credibly bounded by the pilot (pilot
   reliability failure or an unboundable transfer term), **whole-branch
   termination is PROHIBITED** and survivors always advance; in every non-kill
   case the mandated next step is a **small reviewed pilot**, not termination.
   Rung 0 can
   never support adoption (its arms are unreviewed). Cost: drafter calls +
   deterministic evaluation + the credited review-calibration pilot's bounded
   human minutes; no other humans, no GPU. Unblocks: standing up the FULL
   endorsement apparatus (reviewer calibration at scale, crossed review, arm E
   training) only if the branch survives.
   [STIPULATED — PROPOSED-PREREG-ROW-99A-R2l, scope-limited by R3h, completed by
   R4d, formalised by R5c, look-extended by R6c]
1. **Rung 1 — KBUILD-0 Stage 1 (construction fidelity, no host; entered only via
   Rung 0).** Q: does graph or
   citation discipline or review improve packet-relative record fidelity over the pinned drafter,
   and does anything beat text/human baselines? M: §4.3 arms, §4.5 primary **plus the
   unconditional held-out claim task (UCT, §4.5/R4a — both strata, unconditional;
   the natural-stratum gold annotation and blinded consumer sessions run here)**,
   §4.7 gates,
   §4.8 matrix, sequential boundary (which never gates the UCT or arm T). P/F: §4.8;
   **the T-source decision statistic is read here, on the natural-stratum UCT**.
   Cost: drafter calls + bounded human
   exercise (annotation, adjudication, UCT consumers), no GPU. Unblocks: the
   construction-substrate choice (drafter-only vs
   citation-constrained vs graph vs text vs human) for the next kernel build.
2. **Rung 2 — KBUILD-0 Stage 2 (host/compression), conditional on Rung 1.** Q: do
   fidelity gains survive a small independent consumer at fixed token budgets? M: §4.4.
   P/F: §4.6 thresholds + gates 5–6. Cost: <1 GPU-day. Unblocks: the contextual-
   compression claim scoped to the chosen substrate.
3. **Rung 3 — natural-sense confirmatory stratum readout.** Q: do the
   **constructed-arm** nonce results transfer to ambiguity-rich natural senses? (The
   T-source decision was already taken at Rung 1 on this stratum's UCT — Rev4.)
   M: §4.2 stratum 2 (its gold annotation and UCT consumer sessions already ran in
   Rung 1). P/F: precedence row 10 (as amended in Rev4).
   Cost: incremental analysis only. Unblocks: any natural-language scope wording.
4. **Rung 4 — E10-fix (order-invariance).** ONE rung, deliberately **downstream of the
   substrate choice**: re-testing order-invariance of the encoder-side representation
   only makes sense once Rungs 1–3 have fixed *which* construction's records feed the
   encoder. Q/M/P-F/cost: per the standing E10-fix design, unchanged here. Unblocks:
   encoder-geometry claims for the chosen substrate.
5. **Rung 5 — sector extension (institutional/operational/observational packets).** Q: do
   the Rung-1 verdicts hold outside formal/lexical sectors? Only designed after Rungs
   1–3 report. Unblocks: any general construction-methodology ruling.

## SIM-SPEC — FWER/power simulation protocol (Rev7/R7e, before-build corrections Rev8/R8a–g, A4 gate-calibration fix Rev9/R9a — the task-(B) acceptance artifact, maintainer-ratified #59)

This section is the complete, self-contained specification of the mandated
FWER/power simulation (§4.6/R6a item 8), **REWRITTEN in Rev7 per the Rev6
re-review §5**: the simulation now generates the FULL claimed pipeline
(hierarchy selection, Stage-1 binding futility, the Stage-2 execution
trigger, LCC robustness decisions, operational kills, and crossed
author-seed/reviewer/consumer effects — the Rev6 S4 one-sample concept-level
t-tests are REPLACED by the registered crossed-model analysis); claim truth
is derived PROGRAMMATICALLY from the same hypothesis functions the testing
engine uses (the Rev6 hand-maintained true-null column, with its F4/F5/F6/F7/
F8/F9 errors, is retired); the b(r) circularity, adverse-direction, and
gate-copula-sign defects are fixed; the generator, grid count, and expansion
order are pinned; and the Monte-Carlo acceptance rule is made coherent. It is
written so that an executor can implement it as code **without further design
input**: every model, parameter, configuration, criterion, seed rule, and
output format is pinned here (values marked *planning default* are
re-justifiable at prereg-freeze from calibration data; the executor
implements them as configuration inputs, not constants). **Rev8 applies the
seven before-build corrections of the Rev7 spot-check
(`docs/next/design/99a-rev7-simspec-spotcheck.md`): the DGM and the §4.6
analysis ledger now share ONE arm-side long-form representation with
published rotations (S4.1/R8a); the mixed-model inference is exactly pinned
with a named reference implementation (S4.2/R8b); the gate test and its DGM
are replaced together by a calibrated crossed-binary procedure and the
cross-stratum intended-correlation claim is resolved (S4.4/R8c); the
bounded-Beta regime is a pre-scaling concept random effect (S4.3/R8d); the
operational layer carries its DGM variables and exact row algorithms with a
price-vector cost sweep (S4.9/R8e); Rung-0 gets integer looks, joint
route/pilot covariance, and an explicit F10 criterion (S4.8, S6/R8f); and
versions/indices/substreams are pinned (S2/R8g).** Task (B) builds and
runs this protocol; its run artifacts are a preregistration ACCEPTANCE
ARTIFACT — the experiment cannot freeze without them. Everything in this
section is [STIPULATED — PROPOSED-PREREG-ROW-99A-R7e, superseding R6e, as
corrected by PROPOSED-PREREG-ROW-99A-R8a…g] unless tagged otherwise.
Nothing here is run, registered, or frozen by this document.

### S1. Object under test

The simulation exercises the EXACT §4.6/R6a implementation, end to end:

1. the 12-claim elementary family (claim ledger, §4.6/R6a item 1) with its
   IUT compositions (claim p-value = max of component one-sided p-values),
   every component computed per the §4.6/R7a ANALYSIS LEDGER as corrected
   by R8a–R8c (arm-side crossed mixed-model t with the R8b-pinned
   REML/Satterthwaite inference; the R8c latent-probit parametric-bootstrap
   gate test — NOT one-sample concept-level t-tests, NOT exact binomial,
   NOT the retired Gaussian linear-probability LMM);
2. initial weights w₀ = (C-VAL: 1.0, else 0) and the §4.6/R6a item-3
   transition matrix, updated by the §4.6/R6a item-4 algorithm (the graphical
   procedure of Bretz et al. 2009), total α = 0.05;
3. the selection hierarchy (§4.6 rung bars at one-sided 95%, selection-only)
   producing the selected candidate c* from the SIMULATED rung-increment
   contrasts (S4.5), with fallback A1;
4. the Stage-2 execution trigger (S4.7 — endogenous: Stage 2 executes iff at
   least one C-CON-SUP-c is rejected; C-FMT-c testable only then, weight
   stranding otherwise);
5. the Stage-1 binding-futility boundary (S4.6 — pinned algorithm) and the
   §7/R6c Rung-0 route-by-look rule with NESTED interim observations (S4.8;
   L looks, per-test level α₀/(4L), the U_ℓ(r) formula with the pinned
   transfer envelope and the pinned Welch–Satterthwaite df);
6. the operational layer (four-zone descriptive reads at nominal two-sided
   95%, the LCC uncertainty/robustness decision, kill/block rules) —
   simulated to drive path decisions and reported as path frequencies, but
   ERRORS ARE COUNTED ONLY ON THE 12 CONFIRMATORY CLAIMS, AT CLAIM LEVEL
   (the proof's error unit; operational reads cannot create confirmatory
   Type-I errors by construction, and the simulation verifies exactly the
   quantity the theorem bounds).

**Truth engine (binding):** a single shared code module defines the 12
hypothesis functions null_j(θ) over the complete parameter vector θ (S5);
the SAME module is imported by (a) the testing engine, whose components test
exactly these nulls, and (b) the per-cell truth derivation, which computes
the error-counting set {j : null_j(θ_cell) = TRUE} programmatically. No
hand-maintained truth column exists anywhere in the configuration tables or
the code. The FWER estimand per configuration: the probability that AT LEAST
ONE claim j with null_j(θ_cell) = TRUE is rejected by the full pipeline. The
power estimands are the path probabilities in S7.

### S2. Software, determinism, and seeds

- **Language/libraries (exact versions pinned — Rev8/R8g):** CPython
  **3.12.x**; `numpy == 2.1.3` (PRNG: `numpy.random.Generator` over
  **Philox** — the ONE pinned generator (Rev7: "Philox or PCG64" did not
  pin a reproducible generator) — via `SeedSequence`); `scipy == 1.14.1`
  (`scipy.stats` for t quantiles, the bivariate-normal orthant
  probabilities of the S4.4 gate test, and the exact (Clopper–Pearson)
  binomial bounds used in S6/S7 acceptance). No other numerical
  dependencies in the replication loop. **Reference-implementation stack
  (fixture check ONLY, never in the replication loop — R8b):** R 4.4.1 +
  lme4 v1.1-35.5 + lmerTest v3.1-3 (ddf = "Satterthwaite"), per §4.6/(1b)
  pin (e). A version bump of any pinned library is a logged re-pin
  requiring a fixture re-verification, never a silent upgrade.
- **RNG discipline (substreams and draw ordering pinned — Rev8/R8g):** ONE
  pinned base seed `BASE_SEED = 990_066_001` (registered here; a
  freeze-time re-pin is permitted only with a logged reason). Stream per
  (configuration, replication):
  `SeedSequence([BASE_SEED, config_index, replication_index])` — so any
  single replication is reproducible in isolation, results are independent of
  execution order and parallelism, and checkpoint/resume cannot change any
  draw. **Both `config_index` and `replication_index` are ZERO-BASED
  integers** (`replication_index` ∈ {0, …, R−1}). `config_index` is
  assigned by the EXACT expansion order pinned in S6/S7 (Rev7: previously
  unpinned) and recorded in the mandatory resolved configuration table
  (S8), which is the normative index→cell mapping. **Named substreams:**
  each per-replication SeedSequence is split ONCE by `.spawn(13)` into the
  fixed-purpose children (zero-based spawn order, normative): 0
  `natural-concept-layer` (the natural-stratum concept-layer copula draws),
  1 `nonce-concept-layer` (nonce-stratum concept layer + gate concept
  dimensions), 2 `seed-effects` (v_s and (av)_{a,s}, both strata), 3
  `reviewer-effects`, 4 `consumer-effects`, 5 `residuals-natural`, 6
  `residuals-nonce`, 7 `gate-noise` (gate seed/reviewer/record latents), 8
  `stage2-format-data`, 9 `rung0-dataset`, 10 `pilot-estimates`, 11
  `cost-noise` (S4.9 cost-vector measurement noise), 12 `gate-bootstrap`
  (the S4.4 parametric-bootstrap draws, consumed gate-by-gate in arm-index
  order). **Draw ordering within every substream (normative):** loop order
  dimension-major → concept ascending → seed ascending → arm ascending
  (format version ascending for stream 8; route ascending for stream 9;
  bootstrap replicate-major for stream 12), each vector drawn in one
  contiguous call — so any reimplementation reproduces draws bit-exactly.
- **Determinism check:** the report must include a re-run of 100 pinned
  (config, rep) pairs verifying bit-identical rejection vectors.
- **Compute etiquette (this box):** `nice -n 10`, ≤ 2 workers, checkpoint
  every 500 replications per config to a resumable JSON state file (repo
  convention for compute-heavy harnesses).

### S3. Pinned parameters (planning defaults; freeze-repinnable as config)

| Symbol | Meaning | Planning default |
|---|---|---|
| α | total FWER level | 0.05 |
| δ_S | shuffle superiority margin | 0.10 |
| m_T / δ_T | T-contrast noninferiority / superiority margins (δ_T ≥ m_T) | 0.05 / 0.08 |
| δ_G | graph superiority margin | 0.08 |
| m_F | format equivalence margin | 0.05 |
| π₀ | safety-gate floor (gate-pass rate) | 0.60 |
| n_nat / n_nat⁺ | natural concepts, base / escalated | 48 / 96 |
| n_nonce / n_nonce⁺ | nonce concepts, base / escalated | 96 / 160 |
| σ_UCT | total SD of per-record paired UCT macro-BA differences | 0.15 |
| σ_comp | total SD of per-record paired composite differences | 0.20 |
| σ_F | total SD of per-record paired Stage-2 host macro-BA differences | 0.10 |
| f_concept / f_seed / f_reviewer / f_consumer / f_resid | variance-fraction decomposition of each family's total paired-difference variance (S4.1; families lacking a layer fold its fraction into f_resid) | 0.50 / 0.10 / 0.10 / 0.10 / 0.20 |
| n_seeds | author seeds per arm (ONE matched list shared by all arms) | 3 |
| n_consumers / n_reviewers | UCT consumer pool / reviewer pool (rotation algorithms PUBLISHED in §4.6/(1b) and S4.1 — R8a; n_reviewers re-pinned 6 → 8 in Rev8, logged reason: 8 divides every simulated nonce level (96, 160) so the rotation is exactly balanced and reviewer effects cancel exactly in every reviewed contrast; 24 divides both natural levels (48, 96) likewise) | 24 / 8 |
| ρ | concept-layer copula correlation regimes (S4.3 — applied to the cross-family/gate concept-layer correlations AND the within-family exchangeable arm-effect correlation; the R8a arm-side reinterpretation of the Rev7 contrast-level ρ) | {0.0, 0.1, 0.5, 0.8} |
| ρ_w / ρ_b | block-sensitivity regime within-/between-block correlation | 0.8 / 0.3 |
| r_IR / r_cit / r_rev | true rung-increment contrasts (A2-IR−A2, A2−A1, A1−A0; nonce composite scale) | 0.10 each |
| m_IR / m_cit / m_rev | rung-bar increment margins (selection hierarchy) | 0.05 each |
| α₀ / L / f | Rung-0 futility level / looks / threshold | 0.05 / 3 (at 40/70/100% via the §7/R8f integer look table: n_max = 96 → 39/68/96; 160 → 64/112/160) / 0.05 |
| n_p | pilot concepts for Δ_rev estimation | 12 |
| σ_pilot | pilot per-concept SD (s_p = σ_pilot/√n_p) | 0.20 |
| κ_pool, κ_mix, κ_budget, Δ_min | transfer envelope constants | 0.25, 0.25, 0.10, 0.02 |
| d₀(r) / δ_p₀(r) / s_b | Rung-0 true screen contrast / true pilot increment / transfer-shift sign, defaults | +0.20 / +0.05 / 0 |
| σ_scr | Rung-0 screen-scale total paired-difference SD (identified: = σ_comp — R8f) | 0.20 |
| ρ_p | pilot-estimate cross-route correlation (shared pilot concepts/reviewers; exchangeable Σ_p = s_p²·[(1−ρ_p)I₄ + ρ_p J₄] — R8f) | 0.5 |
| selection level | rung-bar one-sided selection level | 0.95 |
| κ_a | TRUE per-arm component cost vectors, 5 components (authoring, review, consumer, storage, ORC) in pinned price-sheet units — the S4.9 table (R8e; replaces the scalar λ_LCC) | S4.9 table |
| σ_κ | per-component cost measurement SD vector (S4.9) | (0.1, 0.2, 0.1, 0.02, 0.2) |
| P_price | pinned robustness PRICE-VECTOR set (5 vectors, S4.9 — applied to component cost vectors so the cost decision can genuinely reverse sign; replaces the sign-invariant scalar multiplier set W — R8e) | S4.9 table |
| Δ^E | true E-arm fidelity contrast (E − best machine arm, nonce composite scale — R8e) | −0.10 |
| m_sheq | §4.8 row-2 shuffle-equivalence margin (R8e) | 0.05 |
| B_boot | gate-test parametric-bootstrap replicates (R8c) | 999 |
| τ_term0 | F10 Rung-0 false-termination acceptance tolerance (exact one-sided 95% upper bound vs the α₀ = .05 guarantee — R8f) | 0.055 |
| stage2_mode | Stage-2 execution mode: `endogenous` (S4.7 trigger) or `forced-off` (stranding check) | endogenous |

### S4. Data-generating model and pipeline algorithm (working model, [STIPULATED]; Rev7 rewrite, Rev8 arm-side unification)

The Rev6 S4 simulated at per-concept paired-difference level and analysed by
one-sample concept-level t-tests; Rev7 replaced the analysis but still
GENERATED contrast-level differences d[i,s,j], which cannot reconstruct the
arm-level model, the concept×arm effects, or the consumer/reviewer
assignments the ledger registers (the spot-check §1 defect). **Rev8/R8a
replaces the generator: per replication the DGM produces ARM-SIDE LONG-FORM
observations — the SAME representation every §4.6/(1b) ledger model is
fitted to** — and the testing engine runs the ledger analyses plus the full
decision pipeline in order (S4.8 → S4.2–S4.7).

**S4.1 Arm-side crossed-effects generation (records and sessions —
Rev8/R8a rewrite).** *Families, arms, endpoints:*
- **Natural stratum** (n_nat concepts): the **UCT family** (endpoint UCT
  three-label macro-BA, total-difference SD σ_UCT) over the 10 arms
  indexed 0…9 in the fixed order (T, A1, A2, A2-IR, H, S(T), S(A1),
  S(A2), S(A2-IR), S(H)); and, only when Stage 2 executes (S4.7), the
  **format family** (Stage-2 host macro-BA, SD σ_F) over the 3 format
  versions per candidate c, indexed (T′(c), AST(c), VEC(c)).
- **Nonce stratum** (n_nonce concepts): the **composite family** (§4.5
  floor-imputed primary composite, SD σ_comp) over the 8 arms indexed 0…7
  in the fixed order (A0, A1, A2, A2-IR, H, E, S(H), S(A2-IR)); plus the 4
  **gate concept dimensions** (S4.4) and the Rung-0 screen dataset (S4.8).
A concept belongs to ONE stratum; cross-stratum correlation is 0 (its
consequence for the gate/contrast pairing is stated honestly in S4.4).

*Generation formula (every family):* the observation on record (a, i, s)
— seeds MATCHED across arms, one pinned seed list — is

> Y_{a,i,s(,k)} = μ_a + b_i + √(f_concept/2)·σ_j·C_i[a]
>              + v_s + (av)_{a,s} [+ w_{r(a,i)}] [+ u_{k(a,i,s)}] + ε,

with: **arm means μ_a** fixed by the cell's parameter vector through the
pinned anchors — UCT family: μ_T = 0, μ_c = Δ^UCT_c (c the candidates),
μ_{S(a)} = μ_a − Δ^SH_a; composite family: μ_{A0} = 0, μ_{A1} = r_rev,
μ_{A2} = r_rev + r_cit, μ_{A2-IR} = r_rev + r_cit + r_IR,
μ_H = μ_{A2-IR} + Δ^G, μ_{S(a)} = μ_a − Δ^SH_a (nonce shuffles),
μ_E = max(μ_{A0}, μ_{A1}, μ_{A2}, μ_{A2-IR}, μ_H) + Δ^E; format family:
μ_{T′(c)} = 0, μ_{f(c)} = −Δ^F_{c,f} — so every registered contrast equals
its parameter exactly; **concept main b_i ~ N(0, f_concept·σ_j²)** per
family, drawn independently of the arm coordinates (it cancels in every
registered contrast; independence pinned, stated); **concept×arm
coordinates C_i[a]** from the stratum's concept-layer copula (S4.3), unit
marginal variance, within-family EXCHANGEABLE correlation ρ and
cross-family/gate correlation per regime, scaled by √(f_concept/2)·σ_j;
**seed main v_s ~ N(0, f_seed·σ_j²)** (cancels in contrasts; pinned) and
**seed×arm (av)_{a,s} ~ N(0, (f_seed/2)·σ_j²)** iid (n_seeds seeds shared
across concepts — the crossed structure; the Rev7 difference-form "v_s[j]"
was this interaction); **reviewer w_{r(a,i)} ~ N(0, (f_reviewer/2)·σ_j²)**
on REVIEWED composite-family arm-records only (arms A1, A2, A2-IR, H),
assigned by the PUBLISHED rotation **r(a, i) = (rev_arm_index(a) + i) mod
n_reviewers** (reviewed arms indexed 0…3 as (A1, A2, A2-IR, H); no
reviewer sees competing records of one concept; exactly balanced because
n_reviewers | n_nonce); **consumer u_{k(a,i,s)} ~ N(0,
(f_consumer/2)·σ_j²)** on UCT-family sessions only, assigned by the
PUBLISHED rotation **k(a, i, s) = (uct_arm_index(a) + i) mod n_consumers**
(each record scored in exactly one session; no consumer answers one
concept under two arms; exactly balanced because n_consumers | n_nat);
**residual ε ~ N(0, σ²_ε(a))** with the layer-folding rule (the Rev7 rule,
arm-side form): σ²_ε(a) = (f_resid + [missing-layer fractions])·σ_j²/2 —
UCT family: (f_resid + f_reviewer)·σ_j²/2 for every record; composite
family: (f_resid + f_consumer)·σ_j²/2 for reviewed arm-records and
(f_resid + f_consumer + f_reviewer)·σ_j²/2 for unreviewed ones; format
family: (f_resid + f_reviewer + f_consumer)·σ_j²/2 — so the implied total
per-pair difference variance equals σ_j² for EVERY registered contrast
(the report must state the implied per-contrast difference SD; it equals
σ_j by construction).

*Working-model closure (why the ρ regimes remain well-defined arm-side —
R8a, stated):* exchangeable-at-ρ arm coordinates decompose into a shared
concept component (absorbed by b_i in the fitted model) plus iid
idiosyncratic concept×arm parts — observationally inside the registered
model class, so every component's marginal calibration is preserved while
ρ modulates the cross-family/gate joint dependence (the FWER stressor) and
shifts concept-main vs concept×arm variance within families;
within-family cross-contrast dependence is the structural pattern implied
by shared arm effects (e.g. correlation ½ between two candidate-vs-T
contrasts), which the retired contrast-level generator could not
represent. Both rotation tables (consumer and reviewer, per n-level) are
emitted with the S8 configuration artifact.

**S4.2 Registered-analysis implementation (the ledger at sim scale — Rev8/
R8b: exact inference pinned; the Rev7 "closed-form ANOVA vs generic REML"
latitude is DELETED):** per replication the engine performs the ledger fits
on the arm-side data: ONE UCT-family fit (all 10 arms — yielding all four
Δ^UCT_c and all five natural Δ^SH_a components), ONE composite-family fit
(all 8 arms — yielding Δ^G, both nonce shuffle components, the three rung
increments, and Δ^E), the per-candidate format-family fits when Stage 2
executes, the four S4.4 gate tests, and the S4.8 Rung-0 fits at each look.
Every continuous component's θ̂, SE, ν̂, p, and bound are DEFINED by the
§4.6/(1b) R8b pins — REML with the nonnegativity boundary,
expected-information covariance, the Giesbrecht–Burns Satterthwaite
formula, and the named reference implementation (R 4.4.1 + lme4 1.1-35.5 +
lmerTest 3.1-3, ddf = "Satterthwaite") as the executable oracle. The sim
engine may use ANY numerically exact algorithm for those pinned estimators
(the per-cell design matrices are FIXED across replications, so
precomputed-structure methods are available — an implementation note, not
latitude about the estimator), SUBJECT to the mandatory **fixture
equivalence check**: on a pinned fixture of 50 replications (config_index
0, replication_index 0–49) × every ledger family, the engine must match
the reference implementation within |Δθ̂| ≤ 1e−7, relative SE ≤ 1e−5,
relative ν̂ ≤ 1e−3, |Δp| ≤ 1e−6; the fixture report is an S8 deliverable
and a breach halts the build (an S9 reportable defect, never a locally
relaxed tolerance). **Fit-failure handling (pinned):** if the REML
optimization fails to converge, retry once from the pinned second start
(all variance components equal at σ_j²/(number of components)); if it
still fails, the affected components are NOT rejected for that replication
and the failure is counted; acceptance requires a per-cell fit-failure
rate ≤ 0.1%, reported per cell. For two pinned configs (F2 and P1) the
supplementary 2,000-flip sign-permutation p-value is also computed on
5,000 replications and its rejection concordance with the model-based p
reported (tolerance: ≤ 1% discordant rejections; a breach is reported, not
silently accepted).

**S4.3 Concept-layer copula and regimes (Rev8: coordinates are ARM-SIDE
concept×arm effects, and bounded-Beta is a PRE-SCALING concept random
effect — R8a/R8d).** The concept-layer coordinate vector per stratum
concept i is: natural stratum — the 10 UCT-family arm coordinates C_i[a]
(plus, per candidate, the 3 format-family coordinates when Stage 2
executes, generated under the same rules from substream 8); nonce stratum
— the 8 composite-family arm coordinates plus the 4 gate concept
dimensions (S4.4). Gaussian regime: the coordinate vector ~ N(0, R) with R
pinned entrywise: correlation ρ between every pair of coordinates —
within-family (the exchangeable arm-effect correlation), cross-family
within the stratum, and between the gate dimensions and every nonce
coordinate; cross-stratum entries 0 (S4.1). Block regime (membership
updated to the arm-side coordinates — same three blocks): Block 1
(natural) = the 10 UCT-family coordinates; Block 2 (nonce) = the 8
composite-family coordinates + the 4 gate dimensions; Block 3 (Stage-2) =
the format-family coordinates; within-block correlation ρ_w = 0.8,
between-block ρ_b = 0.3 applying only within a stratum (blocks 1 and 3;
block 2 is the other stratum, correlation 0). **Bounded-Beta regime
(REDEFINED in Rev8/R8d — the Rev7 mapping to a full outcome marginal with
mean θ_j and SD σ_j double-added θ_j and re-scaled σ_j when substituted
into S4.1, and is retired):** draw the SAME Gaussian coordinate vector
Y ~ N(0, R), set U = Φ(Y) coordinate-wise, and replace each coordinate by
the **centered, unit-variance standardized-Beta transform**
C̃ = (F_Beta⁻¹(U; a₀, b₀) − m₀)/s₀, with ONE pinned shape pair
(a₀, b₀) = (2, 5) for every coordinate ([STIPULATED] skew-stress choice)
and m₀ = a₀/(a₀+b₀), s₀ = √(a₀b₀/((a₀+b₀)²(a₀+b₀+1))) its exact Beta
mean/SD — so C̃ has mean 0 and variance 1 EXACTLY and enters S4.1 through
the ordinary √(f_concept/2)·σ_j scaling, with θ entering ONCE through
μ_a; the bounded-Beta regime is therefore a skewed/bounded CONCEPT random
effect, not a second outcome marginal. R is the COPULA correlation; the
report discloses the realised product-moment correlations (an
approximation to ρ, stated, never silent).

**S4.4 Gate outcomes and gate test (REPLACED TOGETHER in Rev8/R8c — the
Rev7 pairing of a Gaussian LMM t-test with thresholded-normal Bernoulli
data was not level-valid, and its "correlated at ρ" prose gave no joint
formula).** *DGM (exact joint formula):* per candidate arm a ∈ {A1, A2,
A2-IR, H} and primary-stratum record (i, s), the pass indicator is

> g_{a,i,s} = 1{ Z_{a,i,s} > Φ⁻¹(1 − π_a) },  with
> Z_{a,i,s} = √f_concept·G_i[a] + √f_seed·v^g_s[a]
>           + √f_reviewer·w^g_{r(a,i)} + √(1 − f_concept − f_seed −
>             f_reviewer)·e_{a,i,s},

where G_i[a] is arm a's GATE CONCEPT DIMENSION — a member of the S4.3
nonce-stratum copula, correlated at the config's ρ (Gaussian regime; per
block rules in the block regime) with every composite-family coordinate
and with the other gate dimensions — v^g_s[a], w^g (reviewer per the
PUBLISHED family-B rotation r(a,i) — gate indicators are review-based
endpoints, so the reviewer layer is present in generation AND in the
test's working covariance, R8a), and e all iid standard normal (streams 1
and 7). Marginal-π mapping: P(g_{a,i,s} = 1) = π_a EXACTLY. (Bounded-Beta
regime pin: when G_i[a] is the S4.3 standardized-Beta concept coordinate,
Z is no longer exactly Gaussian, so the threshold is re-calibrated —
t_a := the exact numerical (1 − π_a)-quantile of Z's distribution,
computed once per cell by 10⁷ pinned Monte-Carlo draws on the dedicated
PER-CELL calibration stream SeedSequence([BASE_SEED, config_index,
999_999_999]) before any replication runs — keeping the marginal mapping
EXACT while the dependence shape supplies the stress; [STIPULATED].) The implied
within-arm latent covariance is exactly the ledger-C working model with
ρ_c = f_concept, ρ_s = f_seed, ρ_r = f_reviewer — **the DGM and the
registered test share ONE model by construction.** *Orientation
(retained from Rev7):* with this threshold orientation and positive ρ,
gate PASSES co-occur with HIGH composite contrasts through the shared
NONCE concept layer — the adversarial direction for C-GRAPH's IUT
({Δ^G ≤ δ_G} ∪ {π_H ≤ π₀} ∪ {π_A2-IR ≤ π₀}: a true gate null passes
exactly when Δ^G is spuriously high). *Cross-stratum honesty (R8c —
resolving the Rev7 contradiction):* the C-CON-SUP-c IUT pairs a
NATURAL-stratum contrast (Δ^UCT_c) with a NONCE-stratum gate (π_c); since
cross-stratum correlation is 0 (S4.1), these two components are
INDEPENDENT under the pinned DGM — the Rev7 claim that the concept layer
makes THAT pairing adversarial could not arise and is WITHDRAWN
(independence lies between the benign and adversarial extremes; the
within-stratum adversarial pairing above is what the DGM stresses, and
the FWER acceptance rule verifies the claim-level bound under the DGM as
pinned — a disclosed scope statement, not a silent assumption). *Test:*
each π_a is tested by the §4.6/(1b) family-C latent-probit
parametric-bootstrap procedure EXACTLY as pinned there (moment statistic
π̂_a; concordance-class inversion for the POINT (ρ̂_c, ρ̂_s, ρ̂_r);
the FLOORED bootstrap plug-in ρ̃ — ρ̃_s = max(ρ̂_s, ρ_floor),
ρ̃_r = max(ρ̂_r, ρ_floor), ρ̃_c = ρ̂_c, ρ_floor = 0.15, then
clip/rescale in the pinned order (Rev9/R9a); B_boot = 999
bootstrap draws from the null-boundary latent model at ρ̃ on substream
12; p = (1 + #{π̂* ≥ π̂})/(B_boot + 1)). The Rev8 rule that fed the
per-replication truncated-to-0 estimates straight to the bootstrap is
RETIRED: the (B) mock [MEASURED] it anti-conservative (SPEC-DEFECTS A4 —
component rejection ~0.075 at γ = 0.025 vs the 0.031 bar; bootstrap-null
sd 0.059–0.072 vs true π̂ sd 0.084; well-calibrated when fed the true
dependence). *Gate-calibration battery
(mandatory — the demonstrated-level-control obligation):* a dedicated
run of the FLOORED gate test (R9a) ALONE at π_a = π₀ for all four arms,
over the 4
cells {ρ ∈ {0.1, 0.8}} × {n_nonce ∈ {96, 160}}, Gaussian regime,
R = 40,000, with rejection audited at BOTH pinned levels γ ∈ {0.025,
0.00625} (the procedure's typical local levels); **ACCEPT iff every
(cell, arm, γ) realised rejection rate's exact one-sided 95% upper bound
is ≤ 1.25·γ.** *Mandatory dispersion diagnostics (R9a — reported, not
gated):* per (cell, arm) the battery report MUST include (i) the
empirical SD of π̂_a across the R replications, (ii) the mean
bootstrap-null SD of π̂* across replications, and their ratio
(mechanism check: the R9a fix predicts ratio ≥ 1 — a persistent ratio
< 1 in any cell is a REPORTED flag that the mechanism argument failed
even if the rate bar passes, routed back to design per S9, never
silently accepted); (iii) the floor-binding rates
P(ρ̂_s < ρ_floor), P(ρ̂_r < ρ_floor) and the quartiles of each ρ̃
component (discloses how often the floor, vs the adaptive estimate, is
operative). These 4 calibration cells sit OUTSIDE the S6 74-cell FWER
grid; their config_index values continue the S7 counter (S6 expansion
order note) and their results are an S8 deliverable. Battery scope
(disclosed): all 4 cells share the S3 within-arm dependence truth
(f_concept, f_seed, f_reviewer) = (0.50, 0.10, 0.10) — the
floor-binding regime the A4 measurement identified as failing; the
ρ_floor consistency rule in §4.6/(1b)(C) forces a battery re-run if the
planning fractions are ever re-pinned upward.

**S4.5 Hierarchy selection.** From the full Stage-1 data compute the rung
bounds per §4.6 (one-sided 95% lower bounds from the S4.2 analyses): H
clears iff LB(Δ^G) > δ_G; else A2-IR clears iff LB(r_IR) > m_IR; else A2
iff LB(r_cit) > m_cit; else A1 iff LB(r_rev) > m_rev; fallback c* = A1.
Futility-dropped candidates (S4.6) are skipped. Selection affects ONLY the
operational four-zone read-out and path/power estimands — all 12 claims are
tested regardless (pre-registered simultaneous coverage).

**S4.6 Stage-1 binding-futility boundary (pinned algorithm — previously
absent).** ONE interim look at 50% of each stratum's concepts (planning
default; freeze-repinnable; interim size = ⌈0.5·n⌉ per stratum — integer
rule as in §7/R8f). At the look: (i) per candidate c, if the nominal
one-sided 95% MOMENT-BASED Wald upper bound on π_c lies BELOW π₀ —
π̂_c + 1.645·SE_mom(π̂_c), with the moment variance formula pinned as
SE_mom(π̂)² = (1/N²)·[N·π̂(1−π̂) + Σ_q N_q·(P₁₁(ρ̂_q; π̂) − π̂²)] over the
distinct-record pair classes q of the ledger-C latent covariance, using
the SAME floored dependence ρ̃ as the ledger-C bootstrap (Rev9/R9a —
one shared dependence treatment; the floors only ADD nonnegative
covariance terms, so they WIDEN this bound, preserving its conservative
binding-futility direction)
(same-concept: ρ̃_c + ρ̃_r; same-reviewer/different-concept/different-seed:
ρ̃_r; same-seed/different-reviewer: ρ̃_s; same-seed/same-reviewer:
ρ̃_s + ρ̃_r), N_q the design pair counts, P₁₁(ρ; π̂) the bivariate-normal
orthant probability at threshold Φ⁻¹(1 − π̂), and each negative
concordance-excess term truncated at 0 in the POINT estimates (widening
only) — (pinned in Rev8:
futility is a binding-futility-only OPERATIONAL read, so the cheap nominal
moment bound is used here, never the confirmatory bootstrap test),
candidate c is futility-dropped: C-CON-SUP-c and
C-FMT-c become unrejectable for this replication (their nulls are simply
never rejected — removing rejection opportunities only), and c is excluded
from S4.5 selection; (ii) if the nominal one-sided 95% upper bound on Δ^G
lies below δ_G, the graph branch is futility-stopped: C-GRAPH becomes
unrejectable. The UCT and arm T are NEVER gated by this boundary (§7 Rung-1
pin), so the C-VAL and C-DEF claims are unaffected and always reach their
single registered final analysis on full data. Every drop is
binding-futility-only: it can only forgo rejections, hence is conservative
for FWER (its cost appears in the S7 power/branch-loss figures).

**S4.7 Stage-2 execution trigger (endogenous).** Run the graphical update
(§4.6 item 4) over the Stage-1-testable claims (all except C-FMT-c) to a
fixed point. Stage 2 EXECUTES iff at least one C-CON-SUP-c was rejected
(constructed adoption realised — the §4.4 "Stage 1 earns it" rule in
pinned form). If executed: generate the Stage-2 format data (natural
stratum, S4.1 family D), compute the C-FMT component p-values, and CONTINUE
the same graphical update (weights that flowed to C-FMT-c become usable;
iterate to a new fixed point). If not executed, C-FMT weight strands
harmlessly (§4.6 item 4). `stage2_mode = forced-off` overrides the trigger
to NEVER execute (used by F7 to verify stranding: the run must show ZERO
format rejections).

**S4.8 Rung-0 layer (CIRCULARITY AND DIRECTION FIXED in Rev7; NESTED
interims).** Config parameters per route r: true screen contrast d₀(r), true
pilot-setting increment δ_p₀(r), and the transfer-shift sign s_b ∈ {−1, 0,
+1}. Define the TRUE envelope from TRUE quantities —
B*(r) = (κ_pool + κ_mix + κ_budget)·max(|δ_p₀(r)|, Δ_min) — and the true
transfer shift b(r) = s_b·B*(r); the true campaign increment is
Δ_rev,true(r) = δ_p₀(r) + b(r) and θ_true(r) = d₀(r) + Δ_rev,true(r). This
REMOVES the Rev6 circularity (the true shift no longer references the random
plug-in envelope). **Pilot estimates (joint distribution pinned —
Rev8/R8f):** the four pilot estimates are drawn JOINTLY,
(Δ̂_rev(A1), …, Δ̂_rev(H)) ~ N₄(δ_p₀, Σ_p) with
Σ_p = s_p²·[(1 − ρ_p)·I₄ + ρ_p·J₄] and ρ_p = 0.5 (shared pilot
concepts/reviewers across routes; [STIPULATED]) — unbiased for the
PILOT-setting increments, as in the field — and the PROCEDURE computes its
plug-in envelope B(r) from Δ̂_rev(r) per the §7 registered formula (so the
simulation honestly measures how often the random plug-in envelope fails
to cover the true shift; the per-route envelope-coverage rate is a
mandatory report figure). The ADVERSE direction for false termination is
s_b = +1 (the campaign increment is HIGHER than the pilot suggests, so the
procedure UNDERESTIMATES θ(r) and may falsely stop) — P6 and F10 use
s_b = +1; the Rev6 choice b = −B in P6 is retired as the benign direction.
**NESTED interims and joint route correlation (§7/R7c, joint structure
pinned — Rev8/R8f):** per replication generate ONE accruing ARM-SIDE
Rung-0 dataset — n_max = the cell's configured nonce budget (n_nonce or
n_nonce⁺; the §7 identification) concepts × n_seeds records for the FIVE
Rung-0 arms (T, unreviewed-A1, unreviewed-A2, unreviewed-A2-IR,
unreviewed-H; no reviewer layer exists at Rung 0), on the nonce screen
scale σ_scr = σ_comp with concept main, concept×arm, seed main, seed×arm,
and residual effects at the S4.1 fractions (reviewer and consumer
fractions folded into the residual, S4.1 rule; substream 9; generated
INDEPENDENT of the campaign-stage data — its own substream, a disclosed
simplification: the screen set is a separate draw from the nonce
population) — so the four
route contrasts D̂_ℓ(r) = mean(Y_r − Y_T) share the T-arm data and the
concept layer, giving the pinned joint route correlation BY CONSTRUCTION
(≈ 0.5 between routes under the default fractions; the realised value is
implied by the pinned components, disclosed in the report, never a free
knob). At look ℓ compute D̂_ℓ(r), SE_ℓ(r), and the fitted Satterthwaite
ν_D(ℓ,r) — via the R8b-pinned inference on the Rung-0 arm-side model —
from the cumulative first n_ℓ concepts, with the **integer look sizes of
the §7 table (n_max = 96 → 39/68/96; n_max = 160 → 64/112/160)**; apply
the §7 U_ℓ(r) rule with the pinned Welch–Satterthwaite df at each pinned
look; whole-branch termination iff at some look EVERY route's
U_ℓ(r) < f. A terminated replication tests no confirmatory claim
(conservative; counted in branch-loss). **F10 termination acceptance rule
(DECLARED — Rev8/R8f; F10 previously claimed to check the α₀ guarantee
without a criterion):** in every F10 cell (θ_true(r) = f for all routes —
the futility boundary, where a termination is the guarded error), compute
the realised whole-branch termination rate and its exact one-sided 95%
(Clopper–Pearson) UPPER bound; **ACCEPT iff that upper bound ≤ τ_term0 =
0.055** (the α₀ = .05 guarantee plus the same +.005 tolerance logic as
τ_FWER); the per-cell termination count, bound, and pass/fail flag are
mandatory fields of the S8 FWER output.

**S4.9 Operational layer (drives paths, never errors — REBUILT in
Rev8/R8e: the DGM now carries every variable §4.8 rows 2 and 5–9 consume,
with exact algorithms; the Rev7 scalar sweep w·L̂, which could never
reverse sign, is RETIRED).** Four-zone labels from nominal two-sided 95%
CIs on the S4.2 fits.

*Cost model (price vectors × component cost vectors):* each arm
a ∈ {T, A0, A1, A2, A2-IR, H, E} has a TRUE component cost vector κ_a over
the §4.8 LCC components (authoring, review, consumer, storage, ORC), in
pinned price-sheet units — planning defaults ([STIPULATED]):
κ_T = (2, 0, 3, 2, 1); κ_A0 = (4, 0, 3, 1, 2); κ_A1 = (4, 6, 3, 1, 2);
κ_A2 = (5, 6, 3, 1, 2); κ_A2-IR = (6, 7, 3, 1, 2); κ_H = (8, 10, 3, 2, 3);
κ_E = (12, 4, 3, 1, 2). Measured costs per replication:
κ̂_a = κ_a + η_a, η_a ~ N(0, diag(σ_κ²)) independent across arms and
components (substream 11; σ_κ per S3). Pinned price-vector set
P_price ([STIPULATED]): p⁽¹⁾ = (1, 1, 1, 1, 1) (declared base prices),
p⁽²⁾ = (1, 2.5, 1, 1, 1) (review-expensive), p⁽³⁾ = (1, 0.4, 1, 1, 1)
(review-cheap), p⁽⁴⁾ = (3, 0.5, 1, 1, 1) (authoring-expensive),
p⁽⁵⁾ = (0.5, 1, 2.5, 1, 2.5) (consumer/maintenance-expensive). For an
ordered arm pair (x, y) and price vector p the cost-difference statistic
is D̂(x,y;p) = p·(κ̂_x − κ̂_y), with SE(p) = √(2·Σ_m p_m²·σ_κ,m²);
because prices act per COMPONENT on vector-valued differences, the
decision statistic genuinely CAN reverse sign across the sweep (e.g. the
default κ_E − κ_H flips between p⁽¹⁾ and p⁽⁴⁾) — the capability the
retired scalar sweep lacked. *Cost reads (pinned):* "x lower-LCC than y,
robustness-stable" iff D̂(x,y;p) + 1.645·SE(p) < 0 for EVERY p ∈ P_price;
"x LCC-dominated by y" iff D̂(x,y;p) − 1.645·SE(p) > 0 for EVERY p;
otherwise the pair's read is `COST-INDETERMINATE`.

*Exact §4.8 row algorithms (the normative operational-layer definitions —
R8e):*
- **Row 2 (structured ≈ shuffles):** fires iff for EVERY candidate arm
  a ∈ {A1, A2, A2-IR, H} the two-sided 95% CI of Δ^SH_a (natural-stratum
  UCT fit) lies wholly inside ±m_sheq (= 0.05, the pinned
  shuffle-equivalence margin).
- **Row 3 LCC clause (deflation filter):** pair (T, c*) with c* the S4.5
  selected candidate; "T lower-LCC, robustness-stable" per the cost read
  above; `COST-INDETERMINATE` blocks the C-DEF-NSUP-branch adoption
  (§4.8 row 4 path).
- **Row 5 (human-from-evidence block):** fires iff the two-sided 95% CI of
  the E − c* contrast (composite-family fit; the Δ^E dimension) lies
  wholly inside ±0.05 AND E is lower-LCC robustness-stable vs c*.
- **Row 6 (H advancement, LCC non-dominated):** C-GRAPH rejected AND NOT
  (H LCC-dominated by A2-IR).
- **Row 7 (split verdict):** C-GRAPH rejected AND H LCC-dominated by
  A2-IR.
- **Row 8 (fidelity vs review time):** C-GRAPH rejected AND the
  review-time component increases —
  (κ̂_H − κ̂_A2-IR)_review − 1.645·√2·σ_κ,review > 0; the SIM reports the
  row-8 firing frequency (the fidelity-vs-review-cost trade rule itself
  remains a pre-freeze pin from calibration, §4.8).
- **Row 9 (four-zone indeterminate):** the descriptive H − A2-IR read has
  lower CI bound ≤ +0.08 AND its CI not wholly inside ±0.05.
Deflation is ADOPTED (path estimand) iff C-DEF-SUP is rejected, or
C-DEF-NSUP is rejected AND the row-3 LCC read is stable-T-cheaper (§4.8
row 3; the LCC clause is the R7b operational-policy filter — it never
touches claim-level error counting). All kill/block/row flags are
reported as per-cell frequencies.

### S5. Complete parameter vector and programmatic truth derivation

A configuration cell assigns ONE true value to EVERY parameter of the
complete vector θ = (the 24 registered parameters: 7 shuffle contrasts, 4
Δ^UCT_c, Δ^G, 4 π_a, 8 Δ^F_{c,f}) ⊕ (the auxiliary pipeline parameters:
r_IR, r_cit, r_rev; Δ^E; d₀(r), δ_p₀(r), s_b; the S4.9 cost table
{κ_a, σ_κ, P_price}; stage2_mode; ρ; regime; n-level — Rev8/R8e replaces
the scalar λ_LCC with the cost table). Cells are stated below as OVERRIDES of the pinned defaults (S3 +
S6 preamble); the resolved full vector per cell is written to the S8
configuration table — no cell is ever specified by a prose phrase alone
(the Rev6 F5 "contrasts deep-false" defect). Claim truth is NEVER stated in
the config tables: the truth engine (S1) computes {j : null_j(θ) TRUE} from
the hypothesis functions —

> null_CVAL(θ) = ∃a: Δ^SH_a ≤ δ_S;  null_CDEFNSUP(θ) = ∃c: Δ^UCT_c ≥ m_T;
> null_CDEFSUP(θ) = ∃c: Δ^UCT_c ≥ −δ_T;
> null_CCONSUP-c(θ) = (Δ^UCT_c ≤ δ_T) ∨ (π_c ≤ π₀);
> null_CGRAPH(θ) = (Δ^G ≤ δ_G) ∨ (π_H ≤ π₀) ∨ (π_A2-IR ≤ π₀);
> null_CFMT-c(θ) = ∃f: |Δ^F_{c,f}| ≥ m_F

— the SAME functions the testing engine's components target. This
mechanically repairs the Rev6 hand-ledger errors flagged by the re-review:
in F4, Δ^UCT = −0.15 for the other candidates makes ALL FOUR C-CON-SUP
nulls true (not only C-CON-SUP-H); in F8 and F9 all four C-CON-SUP nulls
are true; in F6/F7-style adoption worlds a candidate with Δ^UCT_c > δ_T ≥
m_T makes BOTH C-DEF nulls true alongside the format nulls; and no
infeasible state is expressible because truth is a function of one
parameter assignment.

### S6. FWER configuration grid

Defaults unless overridden (the complete default vector; S5): shuffle
contrasts 0.30 (deep signal), Δ^UCT_c = −0.15 for all c (T comfortably ahead
— deflation world), Δ^G = 0.16, π_a = 0.85, Δ^F_{c,f} = 0, rung increments
(r_IR, r_cit, r_rev) = (0.10, 0.10, 0.10), Δ^E = −0.10, Rung-0 far from
futility (d₀(r) = +0.20, δ_p₀(r) = +0.05, s_b = 0), the S4.9 default cost
table (T robustly cheapest under every pinned price vector),
stage2_mode = endogenous. "Boundary" = the parameter sits exactly on its
component's null boundary (least favorable within the null). The former
"True claim-nulls" column is DELETED (Rev7): the error-counting set of every
cell is derived programmatically by the S5 truth engine and published in the
S8 configuration table as a computed output, never authored by hand.

| Config | Parameter overrides (everything else per the default vector) |
|---|---|
| F1 | all 7 shuffle components at δ_S (C-VAL boundary); Δ^UCT_c = +0.16 all c, π_a = 0.85 (adoption-friendly downstream) |
| F2 | Δ^UCT_c = m_T for all c (C-DEF-NSUP least-favorable) |
| F3 | Δ^UCT_c = δ_T for all c (all C-CON-SUP contrast boundaries); Δ^G = δ_G (C-GRAPH boundary) |
| F4 | Δ^UCT_H = δ_T; Δ^UCT_{A2-IR,A2,A1} = −0.15; Δ^G = δ_G; π_H = π₀ (gate boundary) |
| F5 | Δ^UCT_H = Δ^UCT_A2-IR = +0.16; Δ^UCT_{A2,A1} = +0.04; Δ^G = +0.16; π_H = π_A2-IR = π₀ (gate boundaries); π_{A2,A1} = 0.85 (the Rev6 prose "contrasts deep-false" made explicit as a full assignment) |
| F6 | Δ^UCT_H = +0.16; Δ^UCT_{A2-IR,A2,A1} = +0.04; π_a = 0.85; all Δ^F_{c,f} = m_F (C-FMT boundaries); stage2_mode = endogenous (an adoption-TRUE world so the trigger actually fires and the format boundaries are exercised — the Rev6 "adoption path deep-false + Stage 2 executed" combination is impossible under the endogenous trigger and is retired) |
| F7 | as F6 but stage2_mode = forced-off (stranding check: the run must record ZERO format rejections) |
| F8 | Δ^UCT_c = −δ_T for all c (C-DEF-SUP least-favorable) |
| F9 | selection stress: Δ^UCT_H = Δ^UCT_A2-IR = δ_T (near-tied winners); Δ^UCT_{A2,A1} = −0.15; Δ^G = 0 |
| F10 | Rung-0 interplay: d₀(r) and δ_p₀(r) set so θ_true(r) = f for every route (futility boundary: d₀(r) = f − δ_p₀(r) − B*(r) with δ_p₀(r) = +0.05), s_b = +1 (adverse); campaign params as F3 — also checks the §7 futility guarantee via the S4.8 F10 TERMINATION ACCEPTANCE RULE (exact one-sided 95% upper bound on the whole-branch termination rate ≤ τ_term0 = 0.055 — R8f; a declared criterion with a declared output, not a check without one) |
| F11 | global near-null: Δ^UCT_c = m_T all c, shuffles at δ_S, Δ^G = δ_G, π_a = π₀ all a, Δ^F = m_F (every parameter at its most adversarial feasible value) |

**Grid expansion and cell count (pinned exactly — Rev7; the Rev6 "≈ 60" was
wrong):** F1: ρ ∈ {0.0, 0.1, 0.5, 0.8} × regime ∈ {Gaussian, bounded-Beta}
× base n = 8 cells. F2, F3, F11: the same ρ × regime spread × BOTH
(n_nat, n_nonce) levels = 16 cells each = 48. F4–F10: ρ ∈ {0.1, 0.8} ×
Gaussian × base n = 2 cells each = 14. **Primary total = 8 + 48 + 14 = 70
cells.** Block-sensitivity add-on (now specified, S4.3): F1, F2, F3, F11 ×
block-R regime (ρ_w/ρ_b) × Gaussian marginals × base n = 4 further cells.
**Grand total = 74 cells.** The reduced spread for F4–F10 is a pinned,
disclosed scope choice (no silent cap). **Expansion order (pins
config_index and hence every seed):** enumerate FWER cells first, in the
nested loop order — config row (F1…F11, listed order) → n-level (base, then
escalated where applicable) → regime (Gaussian, bounded-Beta, then block-R
where applicable) → ρ (ascending) — assigning config_index = 0, 1, 2, … in
encounter order (zero-based — R8g); S7 power cells continue the same
counter in the S7 expansion order, and the 4 S4.4 gate-calibration cells
continue it after the S7 cells (order: ρ ascending, then n_nonce
ascending). The S8 resolved configuration table (index → complete
vector → derived truth set) is normative and MUST be emitted before any
replication runs.

**Replications and acceptance criterion (ONE coherent Monte-Carlo rule —
Rev7; replacing the Rev6 "p̂ ≤ .05 AND CP-upper ≤ .055 (+ separate
.05+2SE)" rule, which fails ~half of correct runs when true FWER = .05):**
R = 40,000 per cell (Monte-Carlo SE ≤ 0.0011 at true rate 0.05). Per cell
compute the realised FWER count and its **exact one-sided (Clopper–Pearson)
95% UPPER confidence bound**. **ACCEPT iff, for EVERY cell, that upper
bound ≤ τ_FWER = 0.055** (the pre-declared tolerance). There is NO point-
estimate condition and NO separate ±2SE threshold. Separation argument
(pinned rationale): at true FWER = .05 the upper bound concentrates near
.0518 < .055, so a correct implementation passes each cell with probability
≈ 1 (and the procedure is expected to be conservative below .05, adding
margin); a materially inflated cell (true FWER ≳ .055) fails with
probability ≥ ~.5, rising steeply. Any failing cell is treated as an
IMPLEMENTATION DEFECT or working-model anti-conservatism: halt, diagnose,
fix, re-run the ENTIRE grid under the same seeds, and log the cycle in the
run artifact. The simulation verifies the implementation and the
working-model finite-sample behaviour; it is never the validity argument
itself.

### S7. Power configuration grid

Same default vector and override discipline as S6 (complete resolved vectors
in the S8 table; truth sets derived, never authored).

| Config | Parameter overrides | Target |
|---|---|---|
| P1 — deflation-ADOPTION path (dominant) | Δ^UCT_c = 0 for all c (the registered "true effect zero" for the noninferiority-type claim); S4.9 default cost table (T robustly cheaper) | floored: P(C-VAL ∧ C-DEF-NSUP reject ∧ the S4.9 row-3 LCC read = stable-T-cheaper) — **Rev8/R8e takes the INCLUDE-LCC branch of the spot-check's either/or: P1 is the deflation-ADOPTION power (the §4.8 row-3 event actually firing), stated; the confirmatory-only probability P(C-VAL ∧ C-DEF-NSUP) is reported alongside** — see acceptance rule |
| P2 — strict deflation | Δ^UCT_c = −0.16 for all c | P(C-DEF-SUP rejects) reported (no floor) |
| P3 — constructed-adoption path | Δ^UCT_H = +0.16, Δ^UCT_{A2-IR,A2,A1} = +0.04; Δ^G = +0.16; π_a = 0.85 | floored: P(C-VAL ∧ C-CON-SUP-H ∧ C-GRAPH all reject) |
| P4 — format claim | P3 overrides + Δ^F_{H,f} = 0 both formats (stage2_mode endogenous — Stage 2 fires when adoption is realised) | floored: P(C-FMT-H rejects \| C-CON-SUP-H rejected), joint probability also reported |
| P5 — fallback-selection world | r_IR = r_cit = r_rev = 0 (no candidate clears any rung bar → fallback A1); Δ^UCT_A1 = +0.16, Δ^UCT_{H,A2-IR,A2} = +0.04; π_a = 0.85 | P(C-CON-SUP-A1 rejects) reported |
| P6 — Rung-0 false-termination risk | P3 overrides at the Rung-0 layer: d₀(r) = +0.10, δ_p₀(r) = +0.05, **s_b = +1** (the ADVERSE direction — Rev7 correction: the campaign increment exceeds the pilot estimate, so U(r) underestimates θ(r) and false termination is most likely; the Rev6 b = −B was the benign direction) | tolerance-bounded: P(whole-branch termination) — see acceptance rule |

Each P-config at ρ ∈ {0.1, 0.5, 0.8}, both sample-size levels, Gaussian
regime (expansion order: config row → n-level → ρ ascending, continuing the
S6 config_index counter); R = 10,000 per cell (SE ≤ 0.005 near the floors).

**Acceptance criterion (the SAME coherent one-sided-exact-bound rule as S6 —
Rev7):** for every floored cell compute the **exact one-sided
(Clopper–Pearson) 95% LOWER confidence bound** on the path probability;
**ACCEPT iff, at the escalated sample-size level, every floored lower bound
≥ 0.90** (base-level results reported alongside). For P6 compute the **exact
one-sided 95% UPPER bound** on the termination probability; **ACCEPT iff
≤ τ_term = 0.025**. **Planning-target separation (pinned):** the design and
its escalation are sized so that PLANNING point targets are ≥ 0.92 for every
floored path and ≤ 0.015 for false termination — separated from the
acceptance boundaries (0.90 / 0.025) by ≥ 4 Monte-Carlo SEs at R = 10,000,
so a correctly sized design passes with probability ≈ 1 and the rule never
fails ~half of borderline-correct runs (the Rev6 defect). A missed floor is
a design signal routed per §4.6's power rule (design change or
`INSTRUMENT-INVALID` — never margin widening). Rung-0 branch-loss, Stage-1
futility drop rates, Stage-2 trigger rates, selection distribution over
candidates, LCC `COST-INDETERMINATE` rates, and the per-route
envelope-coverage rate (S4.8) are reported for every P-cell (the §7/R6c
accounting plus the R7e pipeline diagnostics).

### S8. Outputs (task (B) deliverables)

- `poc/results/99a-r8-simspec-config.json`: the NORMATIVE resolved
  configuration table — config_index → complete parameter vector → the
  truth-engine-derived set {j : null_j(θ) TRUE} — PLUS the consumer and
  reviewer rotation tables per n-level (R8a) — emitted and hashed BEFORE
  any replication runs (the truth sets are computed outputs; any hand edit
  to this file invalidates the run).
- `poc/results/99a-r8-simspec-fixture.json`: the S4.2 fixture-equivalence
  report — engine vs the named reference implementation (R 4.4.1 + lme4
  1.1-35.5 + lmerTest 3.1-3) per family, with the realised |Δθ̂|/SE/ν̂/p
  deltas against the pinned tolerances (R8b); emitted before the grid runs.
- `poc/results/99a-r8-simspec-fwer.json` + `.md`: per cell — config_index,
  parameter-vector hash, R, per-claim rejection counts, realised FWER count,
  the exact one-sided 95% upper bound, pass/fail against τ_FWER, the F10
  cells' whole-branch termination count/upper bound/pass-fail against
  τ_term0 (R8f), fit-failure rates, wall-clock, seed material.
- `poc/results/99a-r8-simspec-power.json` + `.md`: per cell — path
  probabilities with exact one-sided bounds (P1 both with and without the
  LCC filter — R8e), pass/fail against the S7 floors/tolerance,
  branch-loss, futility/trigger/selection/LCC-read/envelope diagnostics.
- `poc/results/99a-r8-simspec-gatecal.json` + `.md`: the S4.4
  gate-calibration battery — per (cell, arm, γ) realised rejection rates
  with exact upper bounds and pass/fail against 1.25·γ (R8c), PLUS the
  R9a mandatory dispersion diagnostics per (cell, arm): empirical SD of
  π̂ across replications, mean bootstrap-null SD and their ratio, the
  floor-binding rates for ρ̂_s and ρ̂_r, and the quartiles of each ρ̃
  component.
- A summary markdown table mapping EVERY acceptance criterion (S2
  determinism check, S4.2 fixture-equivalence and permutation-concordance
  tolerances, S4.4 gate-calibration bounds, S6 FWER bound, the S4.8/F10
  termination bound, S7 power bounds, F7 zero-format-rejection stranding
  check, the S4.2 fit-failure ceiling) to pass/fail — the artifact the
  freeze record embeds and the re-review audits.

### S9. Executor latitude (exhaustive)

The (B) executor MAY choose: vectorisation/parallelisation strategy,
checkpoint file layout, progress logging, and any NUMERICALLY EXACT
algorithm for the R8b-pinned estimators (e.g. exploiting the per-cell
fixed design structure), subject to the mandatory S4.2 fixture-equivalence
verification against the named reference implementation — the Rev7
"closed-form ANOVA vs generic REML" either/or is DELETED (R8b).
The executor may NOT change: any margin, weight, edge, formula, test
definition, hypothesis function, configuration value, seed rule, replication
count, or acceptance criterion — and may NOT duplicate the truth engine (one
shared module, imported by both the testing engine and the truth derivation,
is mandatory) — such changes come back to design. Discovery of an ambiguity
in this spec is itself a reportable design defect, not a judgment call to
make locally.

## 8. PROPOSED prereg rows (labels only — nothing registered)

All rows are PROPOSED only — nothing is registered, frozen, or scheduled by this document;
**no `ASM-<number>` ids are minted** (ids are assigned at prereg-freeze). Labels are
`99A`-prefixed to stay disjoint from the sibling revisions (THR-, GU-, VL-, H-PS rows).

### §8.0 Consolidated controlling table (established in Rev4, re-review residual 6; extended — not restructured — in Rev5, Rev6, and Rev7) `[STIPULATED — PROPOSED-PREREG-ROW-99A-R4f]`

**This table CONTROLS.** The R1/R2/R3 row lists below are retained as the historical
series with every stale row amended in place; on any conflict between a row's original
text and this table (or a named in-place amendment), the table and amendment govern.
Two terminology rulings (re-review residual 6): (i) the pin formerly written both
"decision/provenance hash" and "evidence-release hash" is ONE object with ONE canonical
name — the **evidence-release hash** (§1.3 criterion 3); the synonym is retired.
(ii) The §4.2 renderer-family cross-reference reads §4.7 **gate 3** (it formerly
pointed to gate 5).

| Row(s) | Status in Rev4 | Controlling content |
|---|---|---|
| R1a | AMENDED | §1.2 has SEVEN recorded conditions (condition 7 added by R3g); "six" in the original row text is stale |
| R1b, R1c, R1f, R1h, R1i, R1j | OPERATIVE as written | — |
| R1d | SUPERSEDED (contrast) | graph-demotion law stands, but the ablation is H vs **A2-IR** (R3a; Rev4-narrowed to explicit graph materialisation/closure); H vs A2 survives only as a decomposition |
| R1e | AMENDED | arm completeness additionally requires **A2-IR** (R3a) and the unconditional held-out claim task instrumentation (R4a) |
| R1g | OPERATIVE as redefined by R3c, completed by R4c | hurdle/lexicographic non-compensatory endpoint |
| R2a | OPERATIVE as amended by R3b/R3d/R3e, R4a/R4b | four-zone decision on the R4a UCT statistic under the R4b multiplicity procedure |
| R2b | AMENDED by R3g | the one-human floor is the absolute minimum for non-lexical/empirical sectors ONLY; ordinary lexical/empirical promotion requires ≥2 independent qualified humans or a declared authority |
| R2c–R2k, R2m | OPERATIVE as written (R2i as re-anchored by R3a) | — |
| R2l | AMENDED by R3h + R4d | Rung 0 kills unreviewed routes only; "can kill the branch" in the original row text is stale — branch termination requires the R4d differential conditional-futility rule, else the small reviewed pilot is mandatory |
| R3a | AMENDED (Rev4 C1 narrowing) | H−A2-IR isolates **explicit graph materialisation/closure** — a flat typed-relation list still contains reconstructible topology |
| R3b | AMENDED by R4a | the T-source decision endpoint is the unconditional held-out claim task; nonce parse-back is a secondary upper bound |
| R3c, R3g | OPERATIVE as written | — |
| R3d | REPLACED by R4b | fixed-sequence-at-full-α deleted; graphical gatekeeping with local alpha weights + explicit recycling; δ ≥ m required, zones mutually exclusive |
| R3e | OPERATIVE, power re-simulated under R4b | — |
| R3f | COMPLETED by R4c | gate-pass rates first (all failures in the denominator), composite only after arm-level safety gates, gate-breaching records floor-imputed, never dropped |
| R3h | COMPLETED by R4d | futility on route-specific maximum credible DIFFERENTIAL review increments vs T over {A1, A2, A2-IR, H}; any unboundable increment prohibits whole-branch termination |
| R3i | OPERATIVE (canonical term: evidence-release hash) | — |
| R4a | AMENDED by R5b (comparator-inference device re-based by R6a) | UCT made executable: nine natural claims per sense at exactly 3/3/3 by generation-to-quota with a pinned missing-class fallback; generator/labeler role separation; consumer assignment/carryover/rendering/truncation/format-competence pins; comparator inference via pre-registration of every candidate's claims (Rev6: the C-CON-SUP block + C-DEF conjunctions) |
| R4b | COMPLETED by R5a; SUPERSEDED by R6a | the Rev5 95-null/ten-node atomic-graphical matrix is retired; the confirmatory family is the R6a 12-claim ELEMENTARY family tested by the cited Bretz et al. 2009 graphical procedure (conditions verified in §4.6/R6a item 2); every operative threshold procedure-adjusted; strong-FWER grid + path-power simulation mandated per ## SIM-SPEC |
| R4c, R4f | OPERATIVE as written (R4f extended by this table's Rev5 and Rev6 rows) | — |
| R4d | FORMALISED by R5c, LOOK-EXTENDED by R6c | simultaneous one-sided upper prediction bounds U_ℓ(r) on (unreviewed-r − T) + Δ_rev(r) over all four reviewed routes AND all L pinned looks at per-test level α₀/(4L); explicit transfer model Δ_rev(r) = δ_p(r) + b(r) with pinned envelope B(r); termination only when every U_ℓ(r) < f at a pinned look; binding-futility-only sequential accounting; pilot human cost credited; unboundable-increment prohibition retained |
| R4e | COMPLETED by R5d; kill taxonomy re-labelled OPERATIONAL by R6b; text branch RENAMED by R7b | a breached hard gate is a cannot-advance outcome, never a registered kill; kills fire on operational descriptive reads, never as confirmatory no-effect claims (§4.8 Rev6 note); the uniform text rule now reads "text superior, OR T noninferior to every candidate within m_T with lower LCC" everywhere — the original "equivalent with lower LCC" wording is stale (Rev7/R7b: the branch is one-sided noninferiority of T, and the LCC clause is an operational-policy filter outside the IUT) |
| R5a | REPLACED by R6a | the ten-node/95-null matrix operated composite nodes and transferred full node weight while true elementary nulls remained (Rev5 re-review, BLOCKING); superseded by the R6a elementary-claim procedure with cited proof |
| R5b | AMENDED by R6a/R6d | UCT executability pins stand unchanged; comparator selection inference now runs through the C-CON-SUP Bonferroni block and the C-DEF conjunctions (elementary form); the descriptive external-truth label gains its bound source-exposed descriptive-labeler producer role |
| R5c | LOOK-EXTENDED by R6c | route-by-look α₀/(4L) spending; explicit pilot-to-campaign transfer model and U_ℓ(r) bound formula |
| R5d | OPERATIVE as written (kill events re-labelled operational per R6b) | — |
| R6a | AMENDED by R7a/R7f | the 12-claim elementary family, weights, transition matrix, and update algorithm stand UNCHANGED (procedure confirmed VALID by the Rev6 re-review); component p-values made executable by the R7a analysis ledger (exact-binomial gate tests REPLACED by the crossed-design-valid test); "every operative bound" re-worded to "every confirmatory DECISION bound"; restricted-combination closure documented and IUT conservatism (size ≤ α; exact α reserved for TOST components) recorded per R7f |
| R6b | OPERATIVE as written (branch naming per R7b) | — |
| R6c | COMPLETED by R7c | exact Welch–Satterthwaite formula and component degrees of freedom pinned; the transfer bound's conditionality stated (assumption/sensitivity envelope — conditional on \|b(r)\| ≤ B(r), pilot/campaign independence, and t/Welch calibration; not distribution-free); NESTED interim observations mandated in the simulation |
| R6d | COMPLETED by R7d | C-FMT target stratum pinned (natural senses); the H-TEXT-FORMAT result is selection-valid graphical TESTING — no compatible simultaneous-CI procedure is constructed or claimed |
| R6e | SUPERSEDED by R7e | the Rev6 SIM-SPEC did not simulate the claimed procedure (one-sample concept-level t-tests; missing hierarchy/futility/trigger/LCC/crossed-effect variables), hand-maintained a wrong true-null ledger (F4–F9), contained the b(r) circularity, adverse-direction, and gate-copula-sign defects, left the generator/grid underpinned, and used a statistically unstable acceptance rule; the R7e rewrite governs |
| R7a | AMENDED by R8a/R8b/R8c | the analysis-ledger law stands; Rev8 completes it: ONE arm-side long-form representation shared with the DGM, the (av) seed×arm term made explicit, reviewer modelled on review-based endpoints with the PUBLISHED rotation algorithms, exact REML/Satterthwaite inference pins with the named reference implementation (R 4.4.1 + lme4 1.1-35.5 + lmerTest 3.1-3), and the gate components tested by the R8c crossed-binary latent-probit parametric-bootstrap procedure — the interim Rev7 linear-probability LMM gate test is RETIRED (not level-valid on Bernoulli indicators) |
| R7b, R7c, R7d, R7f | OPERATIVE as written (R7c's ν_D now computed by the R8b-pinned implementation; §7 look sizes integerised by R8f) | — |
| R7e | AMENDED by R8a–R8g | the simulation-correctness law stands; Rev8 applies the spot-check's seven before-build corrections: arm-side DGM↔ledger unification, pinned inference + fixture check, replaced gate test/DGM with calibration battery + cross-stratum resolution, pre-scaling bounded-Beta concept RE, operational-layer variables/algorithms with price-vector LCC and the P1 include-LCC estimand, Rung-0 integer looks/joint covariance/F10 criterion, and version/index/substream pins |
| R7a–R7f | NEW in Rev7 (rows below), as amended above | — |
| R8a, R8b, R8d–R8g | NEW (Rev8 rows below) | — |
| R8c | NEW (Rev8 row below); AMENDED by R9a | the crossed-binary gate test, its shared DGM, and the 4-cell battery stand; the null-bootstrap dependence plug-in is the R9a FLOORED triple (ρ̃_s = max(ρ̂_s, 0.15), ρ̃_r = max(ρ̂_r, 0.15), ρ̃_c = ρ̂_c) — the Rev8 rule feeding per-replication truncated-to-0 estimates to the bootstrap is retired as mock-measured anti-conservative (SPEC-DEFECTS A4) |
| R9a | NEW (Rev9 row below) | — |

- **PROPOSED-PREREG-ROW-99A-R1a (amended in Rev2) [AMENDED in Rev4 — see §8.0: §1.2
  has SEVEN conditions since R3g added condition 7]:** independent-endorsement law — an
  endorsement counts for promotion only under §1.2's recorded conditions (role
  independence incl. cross-family/evidence-blind model reviewers; competence/COI;
  pre-fixed sampling, number, threshold, uncertainty;
  fork/abstain/appeal/authority-ruling disagreement handling; model endorsements never
  jointly sufficient with a human/authority floor per R2b; bound
  packet-assembler/adequacy-auditor roles per R2h). [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R1b:** three-property separation law — canonical,
  evidence-adequate, and empirically-grounded are distinct record statuses with the
  distinct operational tests of §1.1; no property's test may evidence another. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R1c:** reproducibility law — stochastic construction steps
  are held to captured-output reproducibility + derivation hashes + measured cross-sample
  /paraphrase/model stability; only deterministic stages are held to byte-identity.
  [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R1d [SUPERSEDED contrast — see §8.0/R3a: the ablation is
  H vs A2-IR (Rev4-narrowed to explicit graph materialisation/closure); H vs A2
  survives only as a decomposition]:** graph-demotion law — the graph constraint is
  hypothesis H-GRAPH, subordinate to
  the plain-text controls per the §4.8 precedence matrix; it may not be written as a
  recommendation anywhere upstream of a passing KBUILD-0. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R1e [AMENDED in Rev4 — see §8.0: A2-IR (R3a) and the R4a
  UCT instrumentation are also required]:** arm-completeness law — KBUILD-0 must include A2
  (citation-only, no graph), A2-IR (flat-IR control), E (human-from-evidence), and T′
  (content-matched plain
  rendering) alongside A0/A1/B/H/T/S/N; absence of any invalidates the design.
  [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R1f:** identifiability-and-leakage law — the
  PACKET-IDENTIFIABILITY gate (labels determined by the packet; UNDERDETERMINED defined
  packet-relative) and template/lexical-leakage audits (separate renderer families,
  pinned overlap bounds) are `INSTRUMENT-INVALID` gates. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R1g (redefined by R3c):** primary-endpoint law —
  packet-relative construction fidelity (denotational comparison against the
  three-valued packet-relative target, evaluator-scored, with
  unsupported/omission/boundary/abstention components; exact hidden-rule equivalence
  only on fully-identifying packets) is PRIMARY; host balanced accuracy is secondary
  and conditional (Stage 2). [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R1h:** statistics law — 3/3/3 claim allocation with pinned
  multiclass-BA formula; confidence-bound (never point) gate thresholds; power
  simulation incl. seed/renderer/reviewer/within-concept variance with a hard
  `INSTRUMENT-INVALID` at unreachable power; multiple author seeds; crossed blinded
  reviewers with no same-concept competing exposure; fixed comparison hierarchy for
  "best constructed arm"; constructor-vs-evaluator coverage separation; rewritten
  independence gate. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R1i:** precedence law — the §4.8 matrix is pre-registered in
  full; text deflation (row 3) dominates any constructed-arm victory; indeterminate
  outcomes are reported as indeterminate, never resolved post hoc. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R1j:** literature-status law — [LIT-BACKED][SV] material is
  supporting-only; no gate, margin, or verdict may rest solely on an unverified
  citation; [EXTRAPOLATION] is direction-only and never a premise. [STIPULATED]

Rev2 rows (one per critique finding, in finding order):

- **PROPOSED-PREREG-ROW-99A-R2a (amended by R3b/R3d/R3e):** deflation-enforcement law
  (Finding 1) — every registered equivalence test (the dominant H-TEXT-SOURCE contrast
  first) is powered ≥90% at its registered margin under the same `INSTRUMENT-INVALID`
  rule as the superiority contrast; an indeterminate-zone T-source outcome BLOCKS
  constructed-arm adoption (§4.8 row 4, placed above every constructed-arm verdict
  row; decided by the R3d four-zone rule, with T′ excluded per R3b); the deflation
  decision uses the single measurable lifecycle-cost composite (LCC), never a
  multi-axis conjunction containing an unmeasurable axis. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R2b [AMENDED by R3g — see §8.0: ordinary lexical/empirical
  promotion requires ≥2 independent qualified humans or a declared authority; the
  one-human floor is the absolute minimum for other sectors only]:** human-floor endorsement law (Finding 2) — promotion
  above `ModelAuthored` requires at least one qualified human or sector-authority
  endorsement (or, for formal-sector records, a machine-checked proof/model-check
  against pinned axioms); model endorsements are never jointly sufficient in any
  number. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R2c:** canonical-selection law (Finding 3) — candidate
  generation may be stochastic (captured-reproducible per R1c); the selection/promotion
  map from (candidates, evidence packet, endorsement objects) to the one normative
  record is a deterministic, replayable, byte-checked function; §1.1's canonicality
  test applies to that function and can fail. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R2d:** two-sided-evidence law (Finding 4) — the
  prior-setting evidence base includes RULES-2 with its never-kernel-specific cap
  alongside the deflationary rows; the K-NULL→construction bridge is tagged
  [EXTRAPOLATION] across the mechanism envelope and may motivate hypotheses only;
  instrument-limited nulls (the X1 ceiling) and descriptive-by-design figures (0.565×)
  carry their limitations inline. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R2e:** graph-scope law (Finding 5) — on the nonce stratum,
  arm B/H is a packet-local relation digest over the shared typed IR under a frozen
  extraction rule; H-GRAPH verdicts are worded packet-local; dictionary-scale
  methodology-(b) claims are confined to the natural stratum; (b)'s
  discovery/inventory/audit roles are untouched by any KBUILD-0 outcome. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R2f:** identifiability-mechanism law (Finding 6) — the
  PACKET-IDENTIFIABILITY checker operates on the shared typed IR; all claim-bearing
  evidence passes a 100% machine-verified render→parse-back→IR-equality round-trip
  (failure = `INSTRUMENT-INVALID` rendering defect); the human paraphrase audit scores
  naturalness only; gate-3 overlap bounds constrain renderers given round-trip success,
  with identifiability winning declared conflicts. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R2g:** symmetric-adoption law (Finding 7) — the governance
  architecture is adopted on stated non-empirical governance grounds; the
  constructed-record store is conditionally adopted pending H-TEXT-SOURCE, stands unearned on
  criterion-8 efficiency grounds, and is withheld per sector wherever §4.8 rows 3–4
  fire. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R2h:** production-role law (Finding 8) — evidence-packet
  assembler and evidence-adequacy auditor are bound roles: pinned assembly procedure,
  assembler not of the drafter family, selection provenance recorded incl. rejected
  sources; auditor cross-family and evidence-blind, as endorsers. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R2i (re-anchored by R3a):** hierarchy-completeness law
  (Finding 9) — each comparison-hierarchy rung has a defined bar and comparator
  (H−A2-IR > +0.08; A2-IR−A2, A2−A1 and A1−A0 against pinned pre-freeze increment
  margins); on no-clear the fallback is best-arm := A1 with T′ rendering A1's records
  for the format contrast, and the T-source deflation contrast always runs.
  [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R2j:** human-arm-fairness law (Finding 10) — arm E receives
  pre-registered schema training and calibration to a pinned proficiency bar before any
  scored authoring; E fidelity is reported raw and post-calibration; nonce-sector
  "expert" is defined as demonstrated calibration performance, not domain credentials.
  [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R2k:** renderer-disjointness law (Finding 11) — every
  renderer family is disjoint from both the drafter family and the host family
  (extends gate 8's pairwise-disjointness rule). [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R2l [AMENDED by R3h + R4d — see §8.0: Rung 0 kills
  unreviewed routes only; "can kill the branch" is stale — branch termination is
  governed by the R4d differential conditional-futility rule]:** machine-first law (Finding 12) — Rung 0 (machine-only
  arms, evaluator-scored, sequential futility boundary) precedes standing up the
  endorsement apparatus; Rung 0 can never support adoption.
  [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R2m:** property-test-enforcement law (Finding 13) — every
  promotion/status assertion carries a machine-checkable `property-test-cited` field;
  a registry lint flags any status change citing a test that does not match the
  property claimed. [STIPULATED]

Rev3 rows (one per cross-vendor finding, referenced by the review's own numbering —
CRITICAL-1…3, MAJOR-4…8, MINOR-9):

- **PROPOSED-PREREG-ROW-99A-R3a (CRITICAL-1) [AMENDED in Rev4 — C1 narrowing: the
  isolated increment is explicit graph materialisation/closure; a flat typed-relation
  list still contains reconstructible topology]:** graph-isolation law — the
  graph-isolating contrast is H vs the flat-IR control A2-IR (same atoms/relations in
  non-graph form; matched raw evidence, prompt, token/compute budget, endorsement
  protocol, and reviewer visibility); H vs A2 is reported only as the decomposition
  (H−A2-IR) + (A2-IR−A2); the oracle-IR B/H/A2-IR family is an explicitly labelled
  upper-bound mechanism test and licenses no production graph-import claim without a
  realistic text→IR extraction test. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R3b (CRITICAL-2) [AMENDED by R4a — the T-source decision
  endpoint is the unconditional held-out claim task; the nonce parse-back is a
  secondary upper bound]:** text-estimand law — the deflation
  hypothesis splits into H-TEXT-SOURCE (independently governed plain-text store,
  scored on the common three-valued packet-relative estimand, dominant) and
  H-TEXT-FORMAT (T′ format probe, Stage-2 only); T′ is charged all shared upstream
  construction/review costs, T only its own governance costs; a T′ Stage-1 fidelity
  equivalence is never evidence that plain text replaces construction. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R3c (CRITICAL-3):** packet-relative target law — the
  primary target is three-valued (TRUE under every packet-consistent rule of the
  pinned generator grammar / FALSE under every / else UNKNOWN); exact hidden-rule
  equivalence applies only to machine-checked fully-identifying packets;
  supported-content fidelity and abstention calibration are reported separately on
  underdetermined packets. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R3d (MAJOR-4) [REPLACED by R4b — see §8.0: the
  fixed-sequence-at-full-α procedure was invalid; the R4b graphical gatekeeping
  procedure controls FWER, with δ ≥ m zone geometry]:** zone-and-family law — the text contrast
  is decided by the pre-registered four-zone CI rule (equivalent /
  constructed-superior / text-superior / indeterminate-blocks-adoption);
  equivalence-test failure is never read as non-equivalence or superiority.
  [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R3e (MAJOR-5):** analysis-fidelity law — inference uses
  the crossed concept × author-seed/snapshot × (reviewer) hierarchy with
  renderer/host as narrowed fixed levels; power is simulated under the exact final
  analysis model including the sequential boundary and winner hierarchy; equivalence
  power is stated at a specified true effect (normally zero); joint adoption-path
  power is reported; an equivalence margin may never be widened to reach power — the
  remedies are design change or `INSTRUMENT-INVALID` termination. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R3f (MAJOR-6) [COMPLETED by R4c — see §8.0: hurdle
  gate-pass-rate level added; gate-breaching records floor-imputed, never dropped]:** non-compensatory-composite law — hard
  minimum gates on unsupported / contradicted / omitted / abstention-miscalibrated
  content precede any composite ranking; composite weights are frozen from
  outcome-disjoint, externally justified grounds before unblinding, with component
  sensitivity reported; the LCC uses declared prices/shadow prices, consistent
  shared-cost allocation, uncertainty-bounded cost differences, and a robustness
  sweep (any reversal ⇒ `COST-INDETERMINATE`); the maintenance term is the
  one-revision-cycle cost, never full-lifecycle evidence. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R3g (MAJOR-7):** anchoring-protection law — promotion of
  ordinary lexical/empirical records requires ≥2 independently sampled qualified
  human endorsers or a declared authoritative body; endorsers/auditors record
  evidence-only clause judgments before seeing any candidate; drafter-assisted
  source selection is prohibited; packet assembly uses a pinned sampling frame with
  dual independent assembly on an audit sample; KBUILD-0 endorsement is human-only.
  [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R3h (MAJOR-8) [COMPLETED by R4d — see §8.0: differential
  increments per route vs T over {A1, A2, A2-IR, H}; unreviewed A2-IR/H added to the
  Rung-0 arm set]:** rung-0-scope law — Rung 0 kills
  unreviewed routes only; branch termination additionally requires the conservative
  conditional-futility rule using the pinned maximum credible review increment from
  an independent pilot; otherwise the mandated next step is a small reviewed pilot,
  not termination. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R3i (MINOR-9) [Terminology, Rev4 — canonical name:
  evidence-release hash; "decision/provenance hash" retired as a synonym]:**
  identity-separation law — every
  selection-input change alters the evidence-release hash; semantic identity is
  altered only when the selected normative content changes. [STIPULATED]

Rev4 rows (one per Rev3-re-review residual, in the re-review's priority order):

- **PROPOSED-PREREG-ROW-99A-R4a (re-review residual 1, ADOPTION-BLOCKER)
  [AMENDED by R5b — see §8.0: claim count/allocation, generator/labeler split,
  consumer pins, and comparator selection inference added]:**
  T-source-estimand law — the T-source decision endpoint is the **unconditional
  held-out claim task (UCT)**: the same blinded consumers and identical
  artifact/consumer budgets for T and every constructed arm; run in Stage 1 for
  every arm in both strata, unconditional on Stage 2, on the sequential boundary,
  and on every other outcome; natural-stratum gold is packet-relative
  (`ENTAILED`/`CONTRADICTED`/`UNDERDETERMINED` relative to the published build
  packet; the held-out source generates claims and supplies a descriptive
  external-truth label only, never marking packet-unsupported content as known);
  **ONE decision statistic** — the paired per-concept three-label macro-BA
  difference on the natural-stratum UCT between the §4.6-hierarchy comparison arm
  (fallback A1) and T — feeds the four-zone rule; the nonce oracle parse-back (and
  nonce UCT) are explicitly secondary upper bounds. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R4b (residual 2) [COMPLETED by R5a — see §8.0: the
  Rev4 node-level weight scheme (positive initial alpha on every node) is
  superseded by the atomic enumeration with all initial alpha on E1]:** FWER law
  — the elementary
  confirmatory claims E1–E8 are enumerated (A2−A1 and A1−A0/H-REVIEW restored to
  the family) and tested under a graphical gatekeeping procedure with pinned local
  alpha weights and explicit recycling; Holm inside E1's plural shuffle contrasts;
  alpha propagates only on rejection of a null at its assigned local level, never
  on a "definitive classification"; δ ≥ m for every four-zone contrast so the
  zones are mutually exclusive; power is re-simulated under this exact procedure.
  [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R4c (residual 3):** hurdle-estimand law — Level 1
  compares arm gate-pass rates with confidence bounds, with ALL
  failed/illegal/gate-breaching records retained in the denominator, against a
  pinned arm-level safety gate; the Level-2 composite comparison is confirmatory
  only after every arm in the contrast passes its safety gate, with gate-breaching
  records scored at the registered composite floor and never dropped, so every
  paired contrast (including H−A2-IR) is defined on every concept. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R4d (residual 4) [FORMALISED by R5c — see §8.0:
  "maximum credible … still lands inside the futility region" is now the
  simultaneous upper-prediction-bound stopping rule U(r) < f]:** rung-0-completeness law — Rung 0
  additionally observes unreviewed A2-IR and unreviewed H; whole-branch
  termination requires, for EVERY route in {A1, A2, A2-IR, H}, that
  unreviewed-route plus its pinned maximum credible DIFFERENTIAL review increment
  vs T remains inside the futility region; any unboundable increment prohibits
  whole-branch termination; survivors always advance to the small reviewed pilot.
  [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R4e (residual 5) [COMPLETED by R5d — see §8.0: the
  §4.8 unreviewed-drafting rule's hard-gate outcome is cannot-advance, never a
  kill; §3.2's "fails" disambiguated] [AMENDED by R7b — see §8.0: the uniform
  text rule now reads "text superior, OR T noninferior to every candidate
  within m_T with lower LCC"; the "equivalent with lower LCC" wording below is
  stale]:** advance/kill/indeterminate law —
  a hypothesis or route is killed only under a confirmed equivalence/inferiority
  zone or a fired futility boundary; lack of demonstrated superiority only blocks
  advancement; indeterminate outcomes neither advance nor kill; the text rule
  reads identically everywhere: "text superior, OR equivalent with lower LCC".
  [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R4f (residual 6):** consolidation law — §8.0 is the
  single controlling prereg table; stale rows are amended in place and any
  conflict resolves to §8.0; the canonical hash term is "evidence-release hash";
  the §4.2 renderer-family cross-reference reads §4.7 gate 3. [STIPULATED]

Rev5 rows (one per Rev4-re-review residual, in the re-review's priority order):

- **PROPOSED-PREREG-ROW-99A-R5a (residual 1, MAJOR) [REPLACED by R6a — see
  §8.0: the composite-node matrix transferred full node weight while true
  elementary nulls remained; the R6a elementary-claim procedure supersedes
  it]:** atomic-FWER law — the
  confirmatory family is the pinned set of 95 enumerated atomic one-sided nulls
  in ten nodes (E1–E9 plus E1b; §4.6 table), tested by the pinned closed
  graphical procedure: ALL initial alpha on validity node E1 (gatekeeping is
  mathematical — an unresolved E1, or an unresolved E2, leaves every downstream
  node at local level zero); the complete transition matrix and update algorithm
  are published in §4.6; within-node closed procedures are pinned (Holm across
  E1's arms; ONE simultaneous multi-candidate set in E2 and E7 — which also
  carries selection inference for the outcome-dependent comparison arm;
  fixed-sequence safety-gates-then-zone in E3–E6/E9; intersection-union in
  E7/E8/E9); every four-zone label is read from ONE confidence set at the node's
  FINAL procedure-assigned level; every operative advancement/kill/adoption
  threshold uses its procedure-adjusted (never fixed-95%) bound, with §4.7
  instrument gates and the selection-hierarchy rung bars explicitly OUTSIDE the
  family; the sequential boundary is binding-futility-only for confirmatory
  rejections; and the freeze record must contain the mandated simulation of this
  exact implementation showing strong FWER ≤ .05 across the pinned
  null-configuration grid AND adoption-path power. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R5b (residual 2, MAJOR) [AMENDED by R6a/R6d — see
  §8.0: selection inference now via the C-CON-SUP block and C-DEF
  conjunctions; external-truth label producer role added]:** UCT-executability law —
  natural gold is nine claims per sense at exactly three per packet-relative
  class, achieved by generation-to-quota under pinned mechanical screens and a
  pinned per-concept candidate cap, with a pre-registered reserve-list
  replacement rule (outcome-independent, gold-side) and a pinned missing-class
  macro-BA fallback (unweighted mean recall over non-empty classes; concepts
  flagged, never excluded); held-out-source-exposed claim GENERATORS are
  role-disjoint from packet-only gold LABELERS (two blinded annotators plus a
  packet-only adjudicator under a pinned majority rule, agreement gated by §4.7
  gate 11); consumer assignment is a pinned balanced design with a registered
  seed and no same-concept-two-arms exposure; one frozen rendering/truncation
  rule for all arms; failed artifacts enter as-is, never excluded; a pinned
  per-format consumer competence battery precedes scoring; and comparator
  selection inference is by inclusion of every candidate-vs-T UCT contrast in
  E2's simultaneous confidence set (the simultaneous-inference branch of the
  re-review's either/or). [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R5c (residual 3, MAJOR) [LOOK-EXTENDED by R6c —
  see §8.0: route-by-look α₀/(4L) spending; explicit transfer model and
  U_ℓ(r) formula]:** rung-0-futility-bound law
  — whole-branch termination requires simultaneous (level 1 − α₀,
  Bonferroni-default) one-sided upper PREDICTION bounds U(r) on
  (unreviewed-r − T) + Δ_rev(r) for every route r ∈ {A1, A2, A2-IR, H},
  propagating both Rung-0 sampling uncertainty and the calibration pilot's
  estimation-plus-transfer uncertainty, with termination permitted only when
  every U(r) lies below the pinned futility threshold f; futility looks only at
  pinned interim points, binding-futility-only (conservative for confirmatory
  FWER), and modelled exactly in the R5a mandated simulation; the
  review-calibration pilot's human cost is measured, charged to the Rung-0
  ledger, and reported, with Rung 0 worded as preceding the FULL endorsement
  apparatus (the pilot being its one credited human exercise); if any Δ_rev(r)
  cannot be credibly bounded, whole-branch termination is prohibited and the
  small reviewed pilot is mandatory. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R5d (residual 4, MINOR):** kill-taxonomy wording law
  — registered kill events are exactly: a confirmed equivalence or inferiority
  zone, or a fired pre-registered futility boundary; a breached hard gate
  (arm-level safety-gate failure) is everywhere a CANNOT-ADVANCE outcome, never
  a registered kill; §3.2's direction note reads "fails to advance or is
  killed"; no other kill wording exists in this document. [STIPULATED]

Rev6 rows (maintainer-ratified #59: valid multiplicity procedure + simulation
specification):

- **PROPOSED-PREREG-ROW-99A-R6a [AMENDED by R7a/R7f — see §8.0: component
  p-values via the R7a analysis ledger (exact-binomial gates replaced);
  "every operative bound" reads "every confirmatory DECISION bound";
  restricted-combination closure and IUT conservatism documented]:**
  elementary-procedure law — the confirmatory
  family is EXACTLY the 12 elementary claims of the §4.6/R6a ledger (C-VAL;
  C-DEF-NSUP; C-DEF-SUP; C-CON-SUP-c and C-FMT-c for c ∈ {H, A2-IR, A2, A1};
  C-GRAPH), each a single null hypothesis with a single valid p-value
  (one-sided components under the registered analysis; union nulls by
  intersection-union, p = max of components), tested by the graphical
  procedure of Bretz, Maurer, Brannath & Posch (2009) with all initial weight
  on C-VAL and the published §4.6/R6a transition matrix and update algorithm;
  strong FWER ≤ .05 holds by the cited closed-testing theorem (Marcus, Peritz
  & Gabriel 1976), whose conditions are verified item-by-item in §4.6/R6a
  item 2 (both citations to be source-verified at freeze); weight moves only
  on rejection of a node's own single null, so no composite-node
  weight-release defect can exist; every operative bound is the deciding
  claim's procedure-assigned one-sided bound; instrument gates and rung bars
  stay outside the family. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R6b:** downgrade-ledger law — the following are
  DESCRIPTIVE (never confirmatory) in KBUILD-0, per the maintainer-sanctioned
  #59 simplification: A2-IR−A2, A2−A1, A1−A0 (H-REVIEW), H-HUMAN (E-vs-machine
  — retaining a conservative operational adoption block), A0 canon-readiness,
  and the T′-shuffle contrast; and every equivalence/inferiority KILL
  direction is OPERATIONAL (descriptive-evidence reads at nominal 95%, labelled
  as such), never a confirmed no-effect finding; the report must carry these
  labels verbatim, and no downgraded contrast may be promoted back without a
  new pre-registered test. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R6c:** rung-0-looks law — Rung-0 futility bounds
  are computed at L pinned looks with per-test level α₀/(4L) (routes × looks
  Bonferroni; sharper spending a freeze-time pin, the simultaneity structure
  not deferrable), using the pinned transfer model Δ_rev(r) = δ_p(r) + b(r),
  |b(r)| ≤ B(r) = (κ_pool + κ_mix + κ_budget)·max(|Δ̂_rev(r)|, Δ_min), and the
  §7/R6c U_ℓ(r) formula (Welch–Satterthwaite df); termination only at a pinned
  look with every U_ℓ(r) < f; any unpinnable κ renders the increment
  unboundable and prohibits whole-branch termination. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R6d:** format-endpoint law — H-TEXT-FORMAT's
  single confirmatory endpoint is Stage-2 host three-label macro-BA (format
  handling and consumer cost descriptive only); selection validity is by
  simultaneous coverage — one C-FMT-c claim per candidate arm covering every
  candidate × format contrast, each reachable only through its own
  candidate's adoption claim; the descriptive external-truth label is
  produced by the bound source-exposed descriptive-labeler role (§4.2),
  role-disjoint from generators, gold labelers, adjudicator, and all
  constructing/endorsing/consuming roles. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R6e [SUPERSEDED by R7e — see §8.0: the Rev6
  SIM-SPEC did not simulate the claimed procedure, hand-maintained a wrong
  true-null ledger, and used a statistically unstable acceptance rule; the
  R7e rewrite governs]:** simulation-protocol law — the ## SIM-SPEC
  section is the complete, binding specification of the freeze-blocking
  FWER/power simulation (task (B)); its acceptance criteria (every feasible
  null cell: FWER point estimate ≤ .05 with Clopper–Pearson upper limit
  ≤ .055 at R = 40,000; deflation-path and adoption-path power floors ≥ .90 at
  R = 10,000; determinism and permutation-concordance checks) must PASS in
  the freeze record; executor latitude is exactly SIM-SPEC §S9; any spec
  ambiguity is a reportable design defect, never a local judgment call.
  [STIPULATED]

Rev7 rows (one per Rev6-re-review residual group plus the citation-`[SV]`
conditions):

- **PROPOSED-PREREG-ROW-99A-R7a [AMENDED by R8a/R8b/R8c — see §8.0: the
  ledger is completed on the arm-side representation with published
  rotations and exact inference pins; the interim linear-probability LMM
  gate test named below is RETIRED for the R8c crossed-binary
  latent-probit parametric-bootstrap procedure]:** analysis-ledger law — every confirmatory
  component's inference is EXECUTABLY defined by the §4.6/R7a analysis
  ledger: estimand population/stratum, observational unit, seed-aggregation
  rule (no pre-averaging; marginalisation only through the fitted model),
  model formula, REML estimation, Satterthwaite denominator degrees of
  freedom, the one-sided p-value formula, and the EXACT matching
  confidence-bound inversion (test–CI duality at the claim's final
  procedure-assigned level); BCa intervals are descriptive only; the gate
  components are tested by the preregistered crossed-design-valid
  linear-probability mixed-model test — the exact one-sided binomial
  (Clopper–Pearson) gate test is RETIRED because record-level gate
  indicators are not iid under crossed concept/author-seed effects; the
  gate estimand's stratum and unit are pinned (primary-stratum record-level
  pass probability); and the threshold rule reads "every CONFIRMATORY
  DECISION bound uses graphical procedure-adjusted levels" — operational
  kills (nominal 95%), hierarchy selection (one-sided 95%), and instrument
  gates (standalone) create no positive confirmatory rejections, which is
  why their separation is FWER-valid. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R7b:** deflation-branch-naming law — the second
  deflation branch is named, EVERYWHERE it appears (hypothesis text,
  four-zone mapping, kill rules, precedence matrix, row-to-claim mapping),
  "T is noninferior to every candidate within m_T and has lower LCC" — its
  confirmatory content is exactly the one-sided noninferiority conjunction
  C-DEF-NSUP, never a two-sided equivalence claim; the lower-LCC conclusion
  is an OPERATIONAL-POLICY FILTER outside the IUT (it can only withhold the
  deflation adoption a C-DEF-NSUP rejection would license, and creates no
  positive confirmatory rejection); full two-sided equivalence remains a
  descriptive read only. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R7c:** rung-0-precision law — the §7 bound uses
  the EXACT pinned Welch–Satterthwaite formula
  ν̂(ℓ,r) = (SE_ℓ² + s_p²)² / (SE_ℓ⁴/ν_D(ℓ,r) + s_p⁴/ν_p) with ν_D(ℓ,r)
  the fitted Satterthwaite df of the Rung-0 crossed-model contrast and
  ν_p = n_p − 1; the transfer bound is stated as CONDITIONAL on
  |b(r)| ≤ B(r), pilot/campaign error independence, and t/Welch calibration
  (an assumption/sensitivity envelope, never distribution-free coverage);
  and the simulation MUST generate nested interim observations (cumulative
  accrual across looks), never independent per-look estimates. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R7d:** format-stratum-and-inference law — the
  C-FMT-c confirmatory endpoint's target stratum is pinned as the NATURAL
  stratum (matching the SIM-SPEC working model); the H-TEXT-FORMAT result
  is described exclusively as SELECTION-VALID GRAPHICAL HYPOTHESIS TESTING;
  no compatible simultaneous confidence-interval procedure is constructed
  or claimed, and per-claim bounds at final local levels are labelled
  claim-level test inversions. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R7e [AMENDED by R8a–R8g — see §8.0: the seven
  spot-check before-build corrections applied; the R8-corrected SIM-SPEC
  text governs]:** simulation-correctness law (supersedes
  R6e) — the ## SIM-SPEC simulation must (i) simulate the FULL claimed
  pipeline: the R7a ledger analyses (crossed mixed models — never
  one-sample concept-level t-tests or exact binomial), hierarchy-rung
  selection with fallback, the pinned Stage-1 binding-futility boundary,
  the endogenous Stage-2 execution trigger with weight stranding, LCC
  uncertainty/robustness decisions, operational kill/block reads, and
  crossed author-seed/reviewer/consumer effects, with errors counted at
  claim level; (ii) derive every cell's true-null set PROGRAMMATICALLY from
  the single shared hypothesis-function module also used by the testing
  engine — no hand-maintained truth column may exist; (iii) implement the
  corrected Rung-0 DGM (true envelope B*(r) from true quantities — no
  b(r)/B(r) circularity; adverse direction s_b = +1 for false-termination
  cells; nested interims), the corrected gate-copula orientation (passes
  co-occur with HIGH contrasts), the fully specified bounded-Beta copula
  and block-correlation structure, the ONE pinned generator (Philox), and
  the pinned 70-primary + 4-block-sensitivity cell grid with pinned
  expansion order and config_index→seed mapping; and (iv) apply ONE
  coherent Monte-Carlo acceptance rule — exact one-sided 95% UPPER bound on
  realised FWER ≤ .055 per cell, exact one-sided 95% LOWER bound ≥ .90 per
  floored power path (upper bound ≤ .025 for false termination), planning
  targets separated from the acceptance boundaries — with no point-estimate
  or ±2SE side conditions. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R7f:** citation-conditions law (folding in the
  multiplicity-citation `[SV]` verdicts) — the prereg documents the
  12-claim family's RESTRICTED-combination structure (the recorded logical
  implications among nulls) and relies on closed testing's per-intersection
  level-α property, which restrictions can only make conservative; every
  component p-value is stated and verified as valid/super-uniform under its
  null (no independence assumed); the conjunctive IUT claim nulls are
  stated CONSERVATIVE (size ≤ α) — exact size = α is claimed ONLY for the
  TOST component pairs (Berger & Hsu 1996), never for any union null; and
  no restricted-combination weight-sharpening is used. [STIPULATED]

Rev8 rows (one per spot-check before-build correction, in correction order):

- **PROPOSED-PREREG-ROW-99A-R8a:** one-representation law — the SIM-SPEC
  DGM and the §4.6 analysis ledger use ONE identical data representation:
  arm-side long-form observations
  Y = α_a + b_i + (ab)_{a,i} + v_s + (av)_{a,s} [+ u_k][+ w_r] + ε, with
  the registered crossed models fitted EXACTLY to the generated data;
  reviewer and consumer factors appear consistently in generation and fit
  (reviewer on review-based endpoints — the composite family and the gate
  latents; consumer on UCT sessions; each absence stated, its variance
  fraction folded into the residual); and the consumer and reviewer
  assignment rotations are PUBLISHED as explicit algorithms
  (k(a,i,s) = (uct_arm_index(a) + i) mod n_consumers;
  r(a,i) = (rev_arm_index(a) + i) mod n_reviewers) with their balance and
  no-competing-exposure properties stated and their tables emitted with
  the configuration artifact. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R8b:** pinned-inference law — "REML +
  Satterthwaite" is completed to a unique algorithm: REML with the
  nonnegativity boundary, GLS fixed effects, expected-information
  variance-component covariance, and the Giesbrecht–Burns Satterthwaite
  formula, with ONE named reference implementation at exact versions
  (R 4.4.1 + lme4 1.1-35.5 + lmerTest 3.1-3, ddf = "Satterthwaite") as the
  executable definition; every other implementation must match it on the
  pinned fixture within the pinned tolerances (|Δθ̂| ≤ 1e−7, rel. SE
  ≤ 1e−5, rel. ν̂ ≤ 1e−3, |Δp| ≤ 1e−6); no unspecified closed-form-vs-
  generic latitude exists anywhere. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R8c [AMENDED in Rev9 — see §8.0/R9a: the
  per-replication hard truncation-to-0 dependence plug-in is replaced by
  the conservative seed/reviewer floor in the bootstrap null]:**
  gate-test-validity law — gate
  components are tested by the ledger-C crossed-binary procedure: a
  latent-probit working model SHARED IDENTICALLY with the S4.4 DGM
  (thresholded Gaussian; covariance ρ_c/ρ_s/ρ_r over
  concept/seed/reviewer sharing; exact marginal-π mapping), the
  moment-statistic parametric-bootstrap p-value (B_boot = 999,
  (1+#)/(B+1) form), CI by test inversion, pinned nuisance
  estimation/truncation and failure handling, and MANDATED demonstrated
  level control (the gate-calibration battery with exact-bound
  acceptance); the Gaussian linear-probability LMM t-test on Bernoulli
  indicators is retired as not level-valid. The cross-stratum
  gate/contrast intended-correlation claim is WITHDRAWN: under the pinned
  DGM the C-CON-SUP gate and contrast components are independent
  (cross-stratum correlation 0, disclosed); the within-stratum
  adversarial pairing for C-GRAPH is preserved through the shared nonce
  concept layer. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R8d:** bounded-Beta-regime law — the
  bounded-Beta stress regime is a CENTERED, UNIT-VARIANCE concept random
  effect (standardized-Beta transform, one pinned shape pair, applied
  BEFORE the S4.1 scaling), never a second full outcome marginal; θ_j
  enters the DGM exactly once, through the arm means. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R8e:** operational-completeness law — every
  §4.8 precedence row consumed by the SIM has its DGM variables (Δ^E,
  per-arm component cost vectors with measurement noise, review-time
  component) and an EXACT pinned algorithm (rows 2 and 5–9, S4.9); the
  row-2 shuffle-equivalence margin is pinned (±0.05); LCC robustness is
  decided by PRICE VECTORS applied to component COST VECTORS — a sweep
  that can genuinely reverse sign — never by positive scalar multiples of
  a single cost difference; and P1 is the deflation-ADOPTION power,
  INCLUDING the row-3 LCC filter in its estimand (the confirmatory-only
  probability reported alongside). [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R8f:** rung-0-implementation law — integer
  look sizes by the pinned rule n_ℓ = ⌈φ_ℓ·n_max⌉ with the published
  look-count table (96 → 39/68/96; 160 → 64/112/160) and n_max identified
  with the configured nonce budget; the four route contrasts computed
  from ONE shared arm-side accruing dataset (joint correlation pinned by
  construction) and the four pilot estimates drawn jointly with pinned
  exchangeable covariance (ρ_p = 0.5); ν_D(ℓ,r) computed by the
  R8b-pinned Satterthwaite implementation; and F10 carries a DECLARED
  termination acceptance rule and output (exact one-sided 95% upper bound
  on the whole-branch termination rate ≤ τ_term0 = 0.055). [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R8g:** reproducibility law — exact pinned
  versions (CPython 3.12.x, numpy 2.1.3, scipy 1.14.1; reference stack
  R 4.4.1 + lme4 1.1-35.5 + lmerTest 3.1-3), zero-based configuration and
  replication indices, and the named 13-substream RNG layout with pinned
  spawn order and within-stream draw ordering; any version bump is a
  logged re-pin with fixture re-verification. [STIPULATED]

Rev9 row (one, for the single (B)-build defect A4):

- **PROPOSED-PREREG-ROW-99A-R9a:** gate-dependence-conservatism law —
  the ledger-C/S4.4 null-boundary parametric bootstrap NEVER consumes a
  dependence estimate that hard-truncation has biased toward
  independence: the bootstrap plug-in is the FLOORED triple
  ρ̃_s = max(ρ̂_s, ρ_floor), ρ̃_r = max(ρ̂_r, ρ_floor), ρ̃_c = ρ̂_c with
  ρ_floor = 0.15 (pinned = 1.5× the S3 planning fractions
  f_seed = f_reviewer = 0.10; re-pinning either fraction above
  ρ_floor/1.5 re-pins the floor to 1.5× the new fraction and re-runs the
  battery), applied in the pinned order floor → clip [0, 0.98] →
  proportional rescale to sum ≤ 0.98; small-dependence mis-estimation
  therefore errs toward OVER-dispersion of the bootstrap null (the
  super-uniform direction, by monotonicity of every pair-class
  covariance in ρ at the exact marginal π₀), never toward the
  mock-measured anti-conservative under-dispersion; the S4.4 battery
  audits the FLOORED test at both γ levels against the unchanged
  ≤ 1.25·γ exact-bound acceptance and MUST report the R9a dispersion
  diagnostics (empirical vs mean bootstrap-null SD of π̂ with ratio,
  floor-binding rates, ρ̃ quartiles); the S4.6 futility moment SE uses
  the same floored ρ̃ (widening-only, conservative direction
  preserved). [STIPULATED]

## Revision 1 — review fixes applied

Itemisation against the five review fixes (authoritative fix text:
`poc/gpt56-review/99a-proposal-review/last-message.json`):

1. **Keep the sound semantic-record-first reframing — ADOPTED.** The frame is retained
   verbatim in intent (§ "Bottom line", §1.3 definition, §3.1); the review's confirmation
   that it matches the implemented encoder architecture is recorded in §0b.
2. **Operationalise the criteria — ADOPTED.** Independent endorsement operationalised
   with five recorded conditions (§1.2, 99A-R1a; Rev2 strengthened condition 5 and added
   a sixth — see "Revision 2" items 2 and 8); canonical vs evidence-adequate vs
   grounded separated with three distinct operational tests and a no-cross-evidencing
   rule (§1.1, 99A-R1b); criterion-4 reproducibility softened to captured-output +
   derivation hashes + measured stability for stochastic steps, byte-identity retained
   for deterministic stages (§1.3 crit. 4, 99A-R1c).
3. **Demote graph-constraint to a pre-registered hypothesis — ADOPTED.** §3 now adopts
   only the governance architecture; the graph is hypothesis H-GRAPH (99A-R1d), argued
   from its own strongest objection plus the [MEASURED] K-NULL
   plain-text-equivalent-cheaper result, tested via the H-vs-A2 ablation and
   subordinate to text deflation in the precedence matrix. The §2 table's (b)/(d) rows
   and the (b) circularity answer are re-worded per the review ("does not, by
   convergence alone, establish external grounding").
4. **KBUILD-0 fixes — ADOPTED, with one modification.** Added: A2 citation-only-no-graph
   (decisive ablation), E human-from-evidence, T′ content-matched plain rendering,
   PACKET-IDENTIFIABILITY gate, template/lexical-leakage audits, exact-rule
   oracle-rendering gate, adversarial packets, sector-verdict separation, sequential
   boundary, and the review's cheaper Stage-1-first sequencing (records scored directly
   against exact rules; host evaluation conditional). Primary endpoint switched to exact
   construction fidelity with host-BA secondary (99A-R1g). Statistics repaired: 3/3/3
   claims replacing the impossible 8-across-3; CI-bound gate thresholds; expanded power
   simulation with hard invalidity at unreachable power; multiple author seeds; crossed
   blinded reviewers; evaluator-vs-constructor coverage separation (A0 illegality =
   substantive failure); rewritten independence gate; fixed-hierarchy selection replacing
   post-hoc "best arm" (99A-R1h). Full precedence/ambiguity matrix added, with text
   deflation dominating (99A-R1i). *Modification:* the review's SAE-role softening is
   also folded into §2(c)/§3.1 step 6 (upstream discovery admissible under
   external-evidence-governed promotion) — adjacent to fix 4's scope but part of the same
   review and adopted for consistency.
5. **[SV] literature non-load-bearing — ADOPTED.** §5 (99A-R1j) marks every citation
   supporting-only, records the review's attribution caveat (dictionary-study figures ≠
   Harnad 1990), and bars load-bearing use pending source verification. No rebuttals were
   necessary: no review point was found wrong; the single modification (SAE-role
   consistency) extends fix 4 rather than disputing it.

Consistency with #56 is handled in §0: Sol as drafter is a draft-step choice; Sol output
remains `ModelAuthored`; the independent gate and the full methodology question stand.

## Revision 2 — critique fixes applied

Itemisation against the 13 findings of the independent adversarial critique
(`docs/next/design/99a-rev1-fable-critique.md`, verdict NEEDS-REV2-THEN-SOURCE-VERIFY;
1 CRITICAL, 7 MAJOR, 5 MINOR). The surviving architecture — three-property split, A2
citation-only ablation, precedence-matrix concept, verified-proposer frame — is retained
unchanged; every item below is a targeted repair, not a redesign.

1. **(CRITICAL) Deflation dominance unenforced — ADOPTED, all three parts.** (a) §4.6:
   ≥90% power required for *every* registered TOST at its registered margin — the
   dominant H-TEXT ±0.03 first — under the same `INSTRUMENT-INVALID` rule as the +0.08
   superiority contrast (pre-freeze widening to at most ±0.05 permitted only with the
   symmetry loss stated openly). (b) Inconclusive T/T′ equivalence now BLOCKS
   constructed-arm adoption: the row moved from precedence position 9 to position 4,
   above every constructed-arm verdict row; escalation retargeted at the T-contrast;
   "constructed-arm verdicts stand" deleted. (c) The four-axis cheapness conjunction is
   replaced by the single measurable lifecycle-cost composite (LCC, §4.8), maintenance
   operationalised as one pinned revision cycle, everything beyond it descriptive-only.
   (R2a)
2. **Model-only promotion loophole — ADOPTED.** §1.2 condition 5: promotion above
   `ModelAuthored` requires ≥1 qualified human or sector-authority endorsement
   (formal sector: mechanical proof/model-check); model endorsements never jointly
   suffice in any number; the §2(c) shared-training-corpus caveat is carried into §1.2
   where it matters. (R2b)
3. **Canonicality test vacuous-or-false — ADOPTED.** §1.1 test 1 splits generation
   (stochastic, captured-reproducible per §1.3 crit. 4) from selection/promotion (a
   deterministic, replayable, byte-checked function); the test applies to the selection
   function and can now fail. (R2c)
4. **One-sided §0b curation + untagged K-NULL bridge — ADOPTED.** RULES-2 added to §0b
   and §6 with its never-kernel-specific cap; the §3.2 K-NULL→construction bridge
   re-worded from "strengthens with repository data" to "motivates" and tagged
   [EXTRAPOLATION] across knull-v2's mechanism envelope; 0.565× carries its
   descriptive-by-design status; the X1 null carries its source's
   ceiling/INSTRUMENT-LIMITED caveat inline. (R2d)
5. **H-GRAPH cannot test methodology (b); arm B under-defined — ADOPTED.** Arm B's
   nonce-stratum extraction rule specified (frozen rule over the shared typed IR of
   §4.7 gate 1); H-GRAPH verdicts re-worded packet-local; dictionary-scale (b) confined
   to the natural stratum; (b)'s discovery/inventory/audit roles declared untouched by
   any KBUILD-0 outcome; the "drops graph construction entirely" direction note
   rescoped. (R2e)
6. **PACKET-IDENTIFIABILITY checker under-specified — ADOPTED.** Checker operates on a
   shared typed IR; 100% machine-verified render→parse-back→IR-equality round-trip on
   all claim-bearing evidence (failure = `INSTRUMENT-INVALID`); gate-2 paraphrase audit
   demoted to naturalness-only; gate-3 bounds restated as given-round-trip constraints
   with identifiability winning declared conflicts. (R2f)
7. **Asymmetric demotion logic — ADOPTED WITH MODIFICATION (both halves of the
   critique's either/or fix).** §3.1 states the non-empirical governance grounds on
   which the architecture is adopted regardless of the efficiency verdict (option b),
   concedes the constructed-record store stands unearned on criterion-8 grounds, AND
   makes constructed-record adoption conditional on the H-TEXT outcome per sector
   (option a's conditional element) — both are needed because Finding 1b independently
   requires adoption to be blockable by the text control. §2 row (d) re-worded to
   match. (R2g)
8. **Production circularity channels — ADOPTED.** §1.2 condition 6 binds the
   evidence-packet assembler (pinned procedure, non-drafter-family, provenance incl.
   rejected sources) and the adequacy auditor (cross-family, evidence-blind); §3.1
   step 2 and §1.1 test 2 carry the binding. (R2h)
9. **Comparison hierarchy under-specified — ADOPTED.** Each rung's bar and comparator
   defined (H−A2 > +0.08; A2−A1 and A1−A0 against pinned pre-freeze increment margins);
   fallback best-arm := A1 with T′ rendering A1's records; the deflation contrast
   always runs. (R2i)
10. **Arm-E schema-familiarity confound — ADOPTED.** The structural counter-measure is
    in §4.3 and marked non-deferrable: pinned-bar schema training/calibration before
    scored authoring; raw + post-calibration reporting; nonce "expert" defined as
    demonstrated calibration performance. Recruitment logistics remain deferred. (R2j)
11. **Renderer families vs drafter family — ADOPTED.** Gate 8 extended: every renderer
    family disjoint from both the drafter family and the host family. (R2k)
12. **Machine-only Rung 0 — ADOPTED.** §7 Rung 0 added (A0, unreviewed-A2, B, T, S, N;
    evaluator-scored; sequential futility boundary; can kill, never adopt) ahead of
    standing up the endorsement apparatus; §4.4 references it. (R2l)
13. **R1b enforcement — ADOPTED.** Machine-checkable `property-test-cited` field on
    every promotion/status assertion plus a registry lint for mismatches (§1.1). (R2m)

No finding is rebutted. The single modification of detail is finding 7, where Rev2 takes
both halves of the critique's either/or fix for consistency with finding 1b.

**Named deferral list (pre-freeze, per the critique's own ruling; constrained further
in Rev3):** the specific margin *values* (+0.08 / ±0.03 / ±0.05 and the four-zone
superiority threshold δ) — **now derivable only from substantive-interchangeability
arguments, never from power feasibility (Rev3, cross-vendor MAJOR-5), and subject to
the Rev4 zone-geometry constraint δ ≥ m (R4b)**; the R6a transition-matrix fraction
*values* (superseding "the R5a fractions"; validity holds for ANY nonnegative
zero-diagonal matrix with row sums ≤ 1 per the cited theorem, so the *values* are
safely deferrable — the R6a *structure*: the 12-claim elementary ledger, all
initial mass on C-VAL, C-VAL the sole source, the IUT compositions, is NOT
deferrable) and the
UCT artifact/consumer budget values (structure and matched-budget rule not
deferrable); the R5b per-concept candidate cap (proposed 30), reserve-list contents,
near-duplicate similarity bound, and consumer-competence bound values (the
generation-to-quota structure, role separation, and fallback definition not
deferrable); the R5c/R6c α₀, futility threshold f, look count L and interim-look
schedule values, and transfer-envelope constants (κ_pool, κ_mix, κ_budget, Δ_min)
(the routes × looks simultaneity structure, the U_ℓ(r) bound form, and the
binding-futility-only rule not
deferrable); the shuffle-contrast margin value δ_S, the format margin m_F, and
the arm-level safety-gate bound π₀; the
fidelity-composite *weighting values* and LCC *weight/price values* — **now frozen from
externally justified, outcome-disjoint grounds before unblinding, inside the
non-compensatory-gates + declared-prices + robustness-sweep structure (Rev3, MAJOR-6)**;
the row-8 fidelity-vs-review-cost trade rule; arm-E *recruitment logistics*; the Rung-0
Δ_rev value (pinned from the independent review-calibration pilot before Rung-0
unblinding). NOT deferred (structural): the per-equivalence-test power requirement, the
row-4 adoption block, the LCC structure, the arm-E calibration counter-measure, and
every Rev3 structural repair (A2-IR arm, three-valued target, T-source/T-format split,
four-zone rule, confirmatory family, crossed-hierarchy analysis, hard minimum gates,
two-human floor + anchoring protection, Rung-0 scope limit), every Rev4
structural repair (unconditional UCT decision endpoint, graphical multiplicity
procedure with δ ≥ m, hurdle estimand, differential Rung-0 futility, the
advance/kill/indeterminate discipline, §8.0 consolidation), every Rev5
structural repair that survives Rev6 (procedure-adjusted operative bounds, the
generation-to-quota natural gold with generator/labeler separation, simultaneous
comparator-selection coverage, the Rung-0 stopping-bound form with
binding-futility-only accounting and pilot cost crediting, and the
cannot-advance hard-gate taxonomy — the Rev5 95-null enumeration itself is
superseded by R6a), and every Rev6 structural repair (the 12-claim elementary
family with all-alpha-on-C-VAL gatekeeping and the cited-procedure conditions,
the R6b downgrade ledger and operational-kill labelling, the routes × looks
futility simultaneity with the pinned transfer-model form, the single
H-TEXT-FORMAT endpoint with per-candidate simultaneous format claims, and the
SIM-SPEC acceptance criteria).

## Revision 3 — cross-vendor findings applied

Itemisation against the cross-vendor GPT-5.6 review of Rev2
(`docs/next/design/99a-rev2-xvendor-review.md`; the review's verbatim output numbers
its findings 1–9, with item 6 covering both decision composites — the coordinator's
3 CRITICAL + 6 MAJOR + 1 MINOR count splits item 6 into its fidelity-composite and LCC
halves, and both halves are itemised below). What the reviewer endorsed is preserved
intact: the verified-proposer governance architecture with its
canonicality/evidence-adequacy/empirical-truth separation, the deterministic vector as
derived-only, the human/authority promotion floor, A2 as the citation-only ablation,
the graph demoted to a falsifiable sector-scoped hypothesis, the conservative
≥90%-per-equivalence-test power rule with inconclusive-blocks-adoption, and the
two-sided evidence base.

1. **(CRITICAL-1) H vs A2 does not cleanly isolate the graph — ADOPTED.** New flat-IR
   control arm A2-IR (same atoms/relations as H's graph input, non-graph form; matched
   evidence, prompt, budget, endorsement, reviewer visibility); H−A2-IR is the sole
   graph-isolating contrast; H−A2 survives only as the decomposition
   (H−A2-IR)+(A2-IR−A2); the whole B/H/A2-IR family is labelled an oracle-IR
   upper-bound mechanism test barring any production graph-import claim without a
   realistic text→IR extraction test (§3.2, §4.1, §4.3, §4.6, §4.8; R3a). Of the
   review's either/or fix, the A2-IR-control branch was chosen; the
   same-realistic-pipeline branch is noted as the requirement any future production
   graph-import claim must meet.
2. **(CRITICAL-2) Text-deflation comparison lacked a common estimand — ADOPTED.**
   H-TEXT split into H-TEXT-SOURCE (independently governed plain-text store T, scored
   on the common three-valued packet-relative estimand, decided by the four-zone rule,
   dominant) and H-TEXT-FORMAT (T′ prose rendering of the winner's own record, Stage-2
   comprehension/format/consumer cost only); T′ charged all shared upstream
   construction/review costs, barred from ever triggering deflation; T charged only its
   own governance costs; the nonce-stratum oracle-parse caveat for T stated openly
   (§4.1, §4.3, §4.5, §4.8; R3b).
3. **(CRITICAL-3) Exact hidden-rule equivalence conflicted with correct abstention —
   ADOPTED.** Formal three-valued packet-relative target defined over the pinned
   generator rule grammar (TRUE under every packet-consistent rule / FALSE under every
   / else UNKNOWN, machine-enumerable); exact hidden-rule equivalence confined to
   machine-checked fully-identifying packets; supported-content fidelity and abstention
   calibration reported separately on underdetermined packets (§4.2, §4.5; R3c).
4. **(MAJOR-4) TOST-only decision rule — ADOPTED.** Pre-registered four-zone CI rule
   (equivalent / constructed-superior / text-superior / indeterminate-blocks-adoption);
   "T and/or T′" abolished; one fixed-sequence gatekeeping family with declared alpha
   allocation across shuffle → T-source → H-GRAPH → input-channel → H-HUMAN → T-format;
   Holm confined to secondaries (§4.6; R3d).
5. **(MAJOR-5) Power analysis did not support the claimed estimand — ADOPTED.** Crossed
   concept × seed/snapshot × reviewer mixed-effects analysis with renderer/host as
   narrowed fixed levels; power simulated under the exact final analysis model incl.
   sequential boundary and winner hierarchy; equivalence power at true effect zero;
   joint adoption-path power reported; the Rev2 "widen to at most ±0.05" clause DELETED
   — margins may never be widened to reach power (§4.6; R3e).
6. **(MAJOR-6a, fidelity composite) — ADOPTED.** Packet-relative fidelity made
   non-compensatory: hard minimum gates on unsupported/contradicted/omitted/
   abstention-miscalibrated content precede any composite ranking; weights frozen from
   externally justified, outcome-disjoint grounds before unblinding; component
   sensitivity reported (§4.5; R3f).
7. **(MAJOR-6b, LCC) — ADOPTED.** Declared prices/shadow prices, consistent shared-cost
   allocation (T′ carries upstream costs), uncertainty bounds on cost differences,
   robustness sweep with `COST-INDETERMINATE` on reversal; maintenance term renamed
   "one-revision-cycle cost", never full-lifecycle evidence (§4.8; R3f).
8. **(MAJOR-7) Production independence gate — ADOPTED.** ≥2 independently sampled
   qualified humans or a declared authority for ordinary lexical/empirical promotion;
   evidence-only clause judgments recorded before candidate exposure; drafter-assisted
   source selection prohibited; pinned sampling frame + dual independent packet
   assembly on an audit sample; KBUILD-0 endorsement clarified human-only
   (§1.2 conditions 5/7, §3.1 step 2; R3g).
9. **(MAJOR-8) Rung 0 could kill the reviewed route from unreviewed arms — ADOPTED.**
   Rung 0 now kills unreviewed routes only; branch termination requires the
   conservative conditional-futility rule with the pinned maximum credible review
   increment Δ_rev from an independent pilot, else a small reviewed pilot is mandated
   (§7; R3h).
10. **(MINOR-9) Selection identity vs two-hash design — ADOPTED.** Every
    selection-input change alters the decision/provenance hash; semantic identity
    changes only when the selected normative content changes (§1.1 test 1; R3i).

No finding is rebutted; findings 1 and 4–9 are adopted as prescribed, finding 1 via the
review's own A2-IR branch of its either/or fix (recorded above as the single
choice-of-branch modification).

## Revision 4 — Rev3-re-review residuals applied

Itemisation against the cross-vendor GPT-5.6 re-review of Rev3
(`docs/next/design/99a-rev3-xvendor-review.md`, verdict **targeted revision needed
(converging)**). Everything the re-review's crosswalk marked RESOLVED — the A2-IR
graph-isolation repair, the crossed-hierarchy analysis/power design, the LCC, the
production-independence gate, the identity/hash separation, the three-valued nonce
target, and the T/T′ split — is **preserved untouched**; every item below is a
targeted repair, not a redesign.

1. **(ADOPTION-BLOCKER) Natural-stratum T-source estimand unspecified — ADOPTED.**
   The **unconditional held-out claim task (UCT)** is now the T-source decision
   endpoint: the same blinded consumers and identical artifact/consumer budgets for
   T and every constructed arm, run in Stage 1 for every arm in both strata
   regardless of any other outcome (the Stage-2 conditionality is removed from the
   text decision, closing the channel by which the dominant comparison lost its
   common consumer exactly when construction was weakest); natural
   TRUE/FALSE/UNKNOWN is defined **relative to the published build packet**, with
   the held-out source confined to claim generation and a descriptive
   external-truth label, never labelling packet-unsupported content as known; **ONE
   decision statistic** (the natural-stratum paired per-concept macro-BA difference)
   feeds the four-zone rule; the nonce oracle parse-back is an explicitly secondary
   upper bound (§4.1, §4.2, §4.3, §4.4, §4.5, §7; R4a).
2. **(MAJOR) Confirmatory-family FWER control invalid — ADOPTED.** The
   fixed-sequence-at-full-α rule is deleted as invalid; the elementary confirmatory
   claims E1–E8 are enumerated, with A2−A1 and A1−A0/H-REVIEW **restored** to the
   family (§4.5 called them primary; the Rev3 family omitted them); a **graphical
   gatekeeping procedure with pinned local alpha weights and explicit recycling**
   controls FWER, with Holm inside E1's plural shuffle contrasts and alpha moving
   only on null rejection at the assigned local level; **δ ≥ m is required** so the
   four zones cannot overlap; the power simulation is re-run under the final
   multiplicity procedure (§4.6; R4b).
3. **(MAJOR) Non-compensatory endpoint mathematically incomplete — ADOPTED.**
   Hurdle/lexicographic estimand preregistered: Level 1 compares gate-pass rates
   with confidence bounds, retaining ALL failed records in the denominator, against
   a pinned arm-level safety gate; the Level-2 composite comparison is permitted
   only after every arm in the contrast passes its safety gate, with gate-breaching
   records scored at the registered composite floor and never dropped — H−A2-IR is
   now defined when either record breaches a hard gate (§4.5; R4c).
4. **(MAJOR) Rung-0 conditional futility incomplete — ADOPTED.** Unreviewed A2-IR
   and unreviewed H added to the Rung-0 arm set; whole-branch termination now
   requires every route in {A1, A2, A2-IR, H} to remain futile after adding its
   route-specific **maximum credible DIFFERENTIAL review increment vs T**; any
   unboundable increment prohibits whole-branch termination; survivors always
   advance to the small reviewed pilot (§7; R4d).
5. **(MAJOR) Kill vs precedence contradiction — ADOPTED.**
   Advance/kill/indeterminate separated: H-GRAPH (and unreviewed-drafting
   canon-readiness) are killed only on confirmed equivalence/inferiority or a fired
   futility boundary; lack of superiority merely blocks advancement, matching
   precedence row 9; the §3.2 text rule corrected to "text superior, OR equivalent
   with lower LCC", now uniform with §4.1 and §4.8 row 3 (§3.2, §4.6, §4.8; R4e).
6. **(MINOR) Stale normative rows and references — ADOPTED.** §8.0 published as the
   single consolidated controlling table; R1a/R1d/R1e/R2b/R2l/R3a/R3b/R3d/R3f/R3h/R3i
   amended, superseded, replaced, or completed in place; one canonical term
   ("evidence-release hash", decision/provenance-hash synonym retired); the §4.2
   renderer-family cross-reference corrected from gate 5 to gate 3 (§1.1, §4.2, §8;
   R4f).
7. **(Crosswalk C1 note) Graph-isolation claim narrowed — ADOPTED.** H−A2-IR is
   worded everywhere as isolating **explicit graph materialisation/closure**,
   because a flat list of typed relations still contains reconstructible topology
   (§3.2, §4.1, §4.3, §6; R3a as amended).

No residual is rebutted. One specification choice is recorded openly under
residual 1: the re-review permitted "one statistic OR a declared conjunctive
hierarchy", and Rev4 takes the **single-statistic** branch (natural-stratum UCT
paired macro-BA), with the nonce parse-back, nonce UCT, and conditional Stage-2 host
measurements all declared secondary upper bounds — adopted-as-prescribed in
substance, with the branch choice the only discretionary element. [STIPULATED]

## Revision 5 — Rev4-re-review residuals applied

Itemisation against the cross-vendor GPT-5.6 re-review of Rev4
(`docs/next/design/99a-rev4-xvendor-review.md`, verdict **targeted revision needed
(converging)**; the reviewer states that after these four targeted fixes "the
experiment should be suitable for preregistration"). Everything the re-review
listed as confirmed strengths — the natural-stratum UCT as the dominant decision
task, packet-relative `ENTAILED`/`CONTRADICTED`/`UNDERDETERMINED` labeling, the
δ ≥ m non-overlapping zone geometry, the hurdle endpoint with every failed record
retained, the repaired kill/text-cost wording, and the §8.0 controlling table — is
**preserved untouched**; every item below is statistical/operational
specification, not redesign.

1. **(MAJOR) Strong FWER control not demonstrated — ADOPTED.** All 95 atomic
   one-sided nulls enumerated in ten nodes (§4.6 table): every directional and
   equivalence component of every four-zone contrast, every arm-level safety
   gate, both H-HUMAN endpoint components (fidelity TOST pair + cost null), both
   H-TEXT-FORMAT format contrasts on ONE pinned endpoint, all four
   candidate-vs-T contrasts, and the A0 canon-readiness components. The complete
   transition matrix and update algorithm are published; **all initial alpha
   sits on E1**, so an indeterminate E1 now mathematically blocks E2–E8 (the
   Rev4 defect of positive downstream initial alpha is removed) and an
   unresolved E2 blocks every constructed-arm node, matching precedence rows
   2/4. Every zone is read from ONE node-level simultaneous confidence set at
   its final procedure-assigned level; every operative 95% threshold (§4.1,
   §4.6 thresholds and hierarchy, §4.8 kill bounds, E9) is replaced by its
   procedure-adjusted bound, with instrument gates and selection-rung bars
   explicitly outside the family; the freeze record must simulate BOTH strong
   FWER over a pinned null-configuration grid AND adoption-path power under the
   exact implementation (§4.1, §4.5, §4.6, §4.8; R5a).
2. **(MAJOR) UCT estimand + selection inference incomplete — ADOPTED
   (simultaneous-inference branch).** (a) Natural claim count and class
   allocation pinned: nine claims per sense at exactly 3/3/3 by
   generation-to-quota under pinned screens/cap with reserve-list replacement,
   plus a pinned missing-class macro-BA fallback (mean recall over non-empty
   classes; arm-independent, no exclusions); sampling/exclusion rules and the
   two-annotator-plus-adjudicator protocol pinned, agreement gated by new §4.7
   gate 11. (b) Held-out-source-exposed claim GENERATORS separated from
   packet-only gold LABELERS as bound, access-logged roles. (c) Consumer
   assignment (balanced design, registered seed, never two arms of one
   concept), carryover protection, one frozen rendering/truncation rule,
   failed-artifact floor-entry, and a per-format consumer competence battery
   all pinned. (d) Of the review's either/or, Rev5 takes the
   **simultaneous-inference branch**: every candidate-vs-T UCT contrast is an
   E2 atomic member covered by ONE simultaneous confidence set, so the
   four-zone decision for the hierarchy-selected arm is valid under any
   selection — no outcome-disjoint calibration data of decision grade exists
   pre-freeze, and the simultaneous set needs none. The enumeration also
   surfaced and fixed the same selection gap in E7's machine comparator
   (same device); E8 needs no adjustment because its estimand is the shipping
   record, post-selection by definition (§4.2, §4.5, §4.6, §4.7; R5b).
3. **(MAJOR) Rung-0 conditional futility not a mathematical bound — ADOPTED.**
   θ(r) = (unreviewed-r − T) + Δ_rev(r) is defined per reviewed route; a
   one-sided upper PREDICTION bound U(r) propagates both Rung-0 sampling and
   pilot estimation-plus-transfer uncertainty, simultaneous over all four
   routes at level 1 − α₀ (Bonferroni default); termination permitted ONLY when
   every U(r) < f (pinned futility threshold); looks only at pinned interim
   points, binding-futility-only — conservative for confirmatory FWER, with the
   branch-loss cost modelled exactly in the R5a mandated simulation; the
   calibration pilot's human minutes are measured, charged to the Rung-0
   ledger, and reported; the "before any human apparatus exists" wording is
   reconciled to "before the FULL endorsement apparatus is stood up", the pilot
   being Rung 0's one credited human exercise; the fallback prohibiting
   whole-branch termination when any Δ_rev(r) is unboundable is retained
   verbatim (§7; R5c).
4. **(MINOR) Kill-rule wording sweep — ADOPTED (cannot-advance branch).** The
   §4.8 unreviewed-drafting rule no longer lists a breached hard gate as a kill
   event: a hard-gate breach is a CANNOT-ADVANCE outcome, preserving the R4e
   taxonomy (kills only via confirmed equivalence/inferiority or fired
   futility) without exception; §3.2's "if H-GRAPH fails" now reads "fails to
   advance or is killed"; the sweep found no other ambiguous kill wording
   (§3.2, §4.8; R5d).

No residual is rebutted. Two branch choices are recorded openly: residual 2
permitted outcome-disjoint calibration selection OR simultaneous/selective
inference over all candidate-vs-T contrasts — Rev5 takes the simultaneous branch
(stated rationale above); residual 4 permitted registering hard-gate breach as an
allowed kill event OR re-labelling it cannot-advance — Rev5 takes the
cannot-advance branch (it leaves the R4e kill taxonomy unchanged rather than
widening it). One consistency repair surfaced by the atomic enumeration is
recorded: §4.3's shuffle-control list S now includes A0, which the §4.8 A0 rule
and Rung 0 always presupposed (E9/R5a). [STIPULATED]

## Revision 6 — valid multiplicity procedure + simulation spec (maintainer-ratified #59)

Itemisation against the cross-vendor GPT-5.6 re-review of Rev5
(`docs/next/design/99a-rev5-xvendor-review.md`, verdict **targeted revision
needed — NOT prereg-suitable**; blockers confined to the multiplicity/FWER
machinery) and the maintainer's #59 ratification (2026-07-21), which
(a) ADOPTED the verified-proposer governance architecture for a bounded pilot,
and (b) authorised SIMPLIFYING the confirmatory-claim structure to reach a
provably valid procedure, with the simulation specification as this
revision's deliverable and the simulation BUILD+RUN as a separate task (B).
Everything the Rev5 re-review confirmed resolved — UCT executability
(3/3/3 quota, generator/labeler separation, consumer pins, E2-style
simultaneous selection coverage), early-node gatekeeping, kill wording, and
Rung-0 substance — is **preserved untouched**.

1. **(BLOCKING 1 — the atomic strong-FWER procedure was not valid) —
   RESOLVED BY SANCTIONED SIMPLIFICATION (R6a).** Three consecutive reviews
   proved the same defect: composite graph nodes released their ENTIRE weight
   on any decisive zone while true elementary nulls remained inside them — an
   operation no cited theorem licenses. Rev6 stops patching and removes the
   defect structurally: the confirmatory family is reduced to **12 elementary
   claims** (each ONE null, ONE valid p-value; conjunctive claims are single
   union nulls tested by intersection-union — Berger 1982, no internal alpha
   splitting), tested by the **cited graphical procedure of Bretz, Maurer,
   Brannath & Posch (2009)**, a closed-testing shortcut (Marcus, Peritz &
   Gabriel 1976) controlling strong FWER at α = .05 under arbitrary
   dependence. Its conditions — elementary nodes with valid p-values,
   nonnegative initial weights summing to 1, transition rows summing to ≤ 1
   with zero diagonal, the paper's own update algorithm — are verified
   item-by-item in §4.6/R6a item 2. The reviewer's specific defects
   dissolve: no node can be partially rejected (nodes are elementary); the
   safety-gate ledger is unique (gates are named IUT components of the claims
   they govern, bearing no alpha themselves; §4.5 states the shuffle-arm gate
   exemption explicitly); every shuffle component's endpoint/stratum is
   pinned in the claim table; the Rev5 "Holm-assigned per-arm CI" device is
   deleted with the composite E1 node. Every operative 95% threshold is the
   deciding claim's procedure-assigned one-sided bound; four-zone labels
   remain as the operational/descriptive layer only.
2. **(Sanctioned downgrades — the price of validity, stated openly, R6b).**
   Confirmatory → descriptive: A2-IR−A2, A2−A1, A1−A0 (H-REVIEW), H-HUMAN
   (conservative operational adoption block retained), A0 canon-readiness,
   T′-shuffle. Confirmatory → operational: every equivalence/inferiority
   KILL direction (kills only withhold/retract — conservative for Type-I
   error; branch-loss cost quantified in SIM-SPEC). Justifications inline in
   §4.6/R6a item 6. The deflation decision, constructed adoption, H-GRAPH
   advancement, validity gating, and the single-endpoint format claim remain
   confirmatory — the complete set any §4.8 adoption/advancement rule
   consumes. The deflation trigger's confirmatory content is the one-sided
   noninferiority-of-T conjunction C-DEF-NSUP (the operative direction),
   with strict superiority C-DEF-SUP nested after it.
3. **(BLOCKING 3 — Rung-0 not valid across sequential looks) — ADOPTED
   (route-by-look branch, R6c).** Of the re-review's either/or, Rev6 takes
   the explicit **route-by-look alpha-spending rule**: L pinned looks,
   per-test level α₀/(4L), union-bound simultaneous coverage 1 − α₀ across
   all looks and routes; plus the exact pilot-to-campaign transfer model
   (Δ_rev(r) = δ_p(r) + b(r), |b(r)| ≤ B(r) with the pinned κ-envelope) and
   the executable U_ℓ(r) bound formula with Welch–Satterthwaite df — 
   "propagates estimation-plus-transfer uncertainty" is now an algorithm.
   The unboundable-increment prohibition is retained verbatim.
4. **(MAJOR-new — H-TEXT-FORMAT selection-sensitive and endpoint-inconsistent)
   — ADOPTED (simultaneous-coverage branch, R6d).** §4.1 now names ONLY
   Stage-2 host three-label macro-BA as the confirmatory endpoint
   (comprehension-adjacent format handling and consumer cost are descriptive);
   of the re-review's three permitted repairs Rev6 takes **simultaneous
   coverage of every candidate-arm × format contrast** — one C-FMT-c claim
   per candidate inside the confirmatory family, reachable only through that
   candidate's own adoption claim — so the read-out for the hierarchy winner
   is pre-registered under any selection, with no conditional-inference
   machinery needed. The "post-selection by definition" argument is no longer
   load-bearing anywhere.
5. **(Nonblocking — descriptive external-truth label had no producer) —
   ADOPTED (R6d).** §4.2 adds the bound, access-logged **source-exposed
   descriptive-labeler role**, disjoint from generators, packet-only gold
   labelers, the adjudicator, and all constructing/endorsing/consuming roles;
   its output feeds only the descriptive external-truth report.
6. **(BLOCKING 2 — the FWER/power simulation unbuilt) — SPECIFIED TO
   IMPLEMENTATION READINESS (R6e; build+run = task (B)).** The self-contained
   ## SIM-SPEC section pins: the exact object under test (the full R6a
   pipeline incl. selection, Stage-2 conditionality, futility layers);
   software, seed discipline (base seed + per-(config, rep) SeedSequence
   streams), and determinism checks; the working data-generating model
   (contrast-level Gaussian with copula-linked gates, plus a bounded-Beta
   sensitivity regime) and the registered-analysis implementation; a FEASIBLE
   null-configuration grid (the Rev5 infeasible "single node's nulls false"
   entry is superseded — configs assign one true value per parameter, so
   infeasible zone combinations are unrepresentable), including boundary,
   mixed-gate, selection-stress, Stage-2-on/off, and Rung-0-interplay cells
   across four correlation regimes; replication counts (40,000/cell FWER,
   10,000/cell power) with the Monte-Carlo error bound and the exact
   acceptance criteria; power targets (deflation path ≥ .90 at true effect
   zero; adoption path ≥ .90; format ≥ .90; false-termination ≤ .02); output
   file formats; and an exhaustive executor-latitude clause.

No finding is rebutted. Two branch choices are recorded openly: the
re-review's blocking item 1 permitted a genuinely atomic graphical/closed
procedure OR a formally cited family-gatekeeping procedure — Rev6 delivers
the first, made trivial by shrinking the family (the maintainer-sanctioned
route); blocking item 3 permitted an anytime-valid sequence OR an explicit
route-by-look allocation — Rev6 takes route-by-look (no new machinery, valid
without dependence assumptions). [STIPULATED]

## Revision 7 — Rev6-re-review + citation-SV residuals applied

Itemisation against the cross-vendor GPT-5.6 re-review of Rev6
(`docs/next/design/99a-rev6-xvendor-review.md`, verdict **targeted revision
needed — NOT material redesign; the multiplicity procedure is NOW VALID**:
Bretz 2009 correctly applied to elementary nulls, IUT/TOST valid, the
recurring Rev5 defect "genuinely gone", Rung-0 route-by-look Bonferroni
correct, H-TEXT-FORMAT selection valid for familywise claim decisions;
"once those targeted defects are corrected, the standard 12-node graphical
design is suitable to carry forward") and the multiplicity-citation source
verification (`docs/next/design/99a-rev6-citation-sv.md`, ALL-HOLD with four
binding conditions). Rev7 is a targeted SPECIFICATION repair: **the
graphical procedure, the 12-claim ledger, the initial weights, the
transition matrix, the update algorithm, and the claim structure are
UNCHANGED** — everything the re-review marked valid (the procedure, IUT/TOST,
the Rung-0 route-by-look Bonferroni, H-TEXT-FORMAT selection, the downgrade
ledger) is preserved untouched.

1. **(Re-review §1 — component p-values not yet established as valid) —
   RESOLVED (R7a).** §4.6 gains the item-(1b) ANALYSIS LEDGER: for every
   component family — UCT contrasts, nonce-composite contrasts, gate rates,
   format contrasts — the estimand population/stratum, observational unit,
   seed-aggregation rule, model formula, REML estimator, Satterthwaite
   denominator df, one-sided p-value formula, and the exact matching
   confidence-bound inversion are pinned; "model-based one-sided p + BCa" is
   replaced (BCa demoted to descriptive reporting). The exact-binomial gate
   issue is resolved by the REPLACE branch of the re-review's either/or:
   record-level gate indicators are not iid under crossed concept/seed
   effects, so the Clopper–Pearson test is retired for a preregistered
   crossed-design-valid linear-probability mixed-model test, with the gate
   estimand's stratum (primary/nonce) and unit (record) pinned. The
   threshold wording is corrected in item (5): "every CONFIRMATORY DECISION
   bound" uses procedure-adjusted levels — operational kills (nominal 95%),
   hierarchy selection (one-sided 95%), and instrument gates (standalone)
   create no positive confirmatory rejections, which is exactly why the
   separation is FWER-valid, and the text now says so.
2. **(Re-review §2 — C-DEF-NSUP is noninferiority, not equivalence; LCC role
   unstated) — RESOLVED (R7b).** The branch is renamed EVERYWHERE — §3.2,
   §4.1 (H-TEXT-SOURCE), the §4.6 four-zone mapping and claim ledger, the
   §4.8 deflate-to-text rule, precedence row 3, and the row-to-claim mapping
   — to "T is noninferior to every candidate within m_T and has lower LCC";
   the LCC conclusion is pinned as an OPERATIONAL-POLICY FILTER outside the
   IUT (it can only withhold adoption, never create a confirmatory
   rejection); two-sided equivalence remains descriptive only. The
   historical R4e wording is amended in place via §8.0.
3. **(Re-review §3 — Rung-0: pin Welch df; conditionality; nested interims)
   — RESOLVED (R7c).** §7 pins the exact Welch–Satterthwaite formula with
   component df (ν_D(ℓ,r) fitted Satterthwaite; ν_p = n_p − 1); states the
   transfer bound as conditional on |b(r)| ≤ B(r), pilot/campaign error
   independence, and t/Welch calibration — an assumption/sensitivity
   envelope, not distribution-free; and mandates NESTED interim
   observations in the simulation (cumulative accrual, S4.8). The
   route-by-look Bonferroni itself is retained unchanged (confirmed valid).
4. **(Re-review §4 — C-FMT stratum; simultaneous-CI overclaim) — RESOLVED
   (R7d).** §4.1 pins the C-FMT target stratum as the NATURAL stratum
   (matching SIM-SPEC), and describes the H-TEXT-FORMAT result as
   SELECTION-VALID GRAPHICAL HYPOTHESIS TESTING; §4.6 item (5) labels
   per-claim final-level bounds as claim-level test inversions — no
   compatible simultaneous-CI procedure is constructed or claimed.
5. **(Re-review §5 — SIM-SPEC blocking defects) — RESOLVED BY REWRITE
   (R7e, the principal Rev7 change).** The ## SIM-SPEC section is rewritten:
   (i) the DGM/algorithm generates the FULL claimed pipeline — crossed
   author-seed/reviewer/consumer effects with the R7a ledger analyses
   replacing the one-sample t-tests (S4.1–S4.2), hierarchy-rung selection
   from simulated rung increments (S4.5), a pinned Stage-1 binding-futility
   boundary (S4.6), the endogenous Stage-2 execution trigger with stranding
   (S4.7), LCC uncertainty/robustness decisions and operational kills
   (S4.9) — with errors counted at claim level; (ii) claim truth is derived
   PROGRAMMATICALLY from the single shared hypothesis-function module the
   testing engine also uses (S1/S5); the hand-maintained true-null column is
   deleted and its F4/F5/F6/F7/F8/F9 errors are moot (F5 and F6 get explicit
   full parameter assignments; F6's impossible "adoption deep-false + Stage 2
   executed" combination is replaced by an adoption-true world; F7 keeps a
   forced-off override purely as a stranding check); (iii) implementability:
   the b(r) = ±B(r) circularity is removed via the true envelope B*(r)
   computed from true quantities, P6/F10 use the ADVERSE direction s_b = +1,
   the gate-copula orientation is reversed so passes co-occur with HIGH
   contrasts, the bounded-Beta copula and block-correlation construction and
   membership are fully specified, the generator is pinned to Philox alone,
   and the grid is pinned at 70 primary + 4 block-sensitivity cells with an
   exact expansion order fixing config_index→seed; (iv) ONE coherent
   Monte-Carlo acceptance rule: exact one-sided 95% upper bound on realised
   FWER ≤ .055 per cell; exact one-sided 95% lower bound ≥ .90 per floored
   power path and upper bound ≤ .025 for false termination; planning targets
   (≥ .92 / ≤ .015) separated from the acceptance boundaries; the "p̂ ≤ .05"
   and ".05 + 2SE" conditions are deleted.
6. **(Citation-`[SV]` conditions) — FOLDED IN (R7f).** §4.6 item (2) gains
   condition (vi): the family's RESTRICTED-combination structure is
   documented (the logical implications among nulls recorded), with validity
   resting on closed testing's per-intersection level-α property
   (restrictions add only conservatism; no weight-sharpening is used);
   item (1) states component super-uniformity as the validity requirement
   and the IUT's conservatism (size ≤ α) explicitly, reserving exact
   size = α for the TOST component pairs only.

No finding is rebutted. The one deliberate judgement call recorded openly:
for the exact-binomial gate issue the re-review offered "justify iid OR
replace" — Rev7 REPLACES (the iid justification would have required
collapsing seeds into concept-level indicators and defending independence
across a shared seed list, a weaker and less honest route than testing at
the record level under the crossed model the design already registers).
[STIPULATED]

## Revision 8 — SIM-SPEC before-build corrections applied

Itemisation against the cross-vendor GPT-5.6 focused spot-check of Rev7
(`docs/next/design/99a-rev7-simspec-spotcheck.md`, verdict **TARGETED FIX
NEEDED**; scope = SIM-SPEC + analysis ledger only — the spot-check
explicitly did NOT re-audit the confirmed-valid multiplicity procedure,
and CONFIRMED-FIXED the Rev7 programmatic truth engine (§2), the
Monte-Carlo acceptance rule (§4), the transfer circularity/adverse
direction, gate-threshold orientation, Philox pin, and 70+4 grid (§3),
and the Rung-0 outer Welch/nesting (§6)). Rev8 applies the spot-check's
seven "Concrete correction required" items — algorithms, variables, and
dependence definitions, per its own closing ruling "not legitimate
freeze-time deferrals" — and NOTHING else. **The graphical procedure, the
12-claim ledger, the initial weights, the transition matrix, the update
algorithm, the IUT compositions, the margins, and the downgrade ledger
are UNCHANGED.**

1. **(Correction 1 — one identical data representation; reviewer/consumer
   consistency; rotations) — RESOLVED (R8a).** S4.1 is rewritten to
   generate ARM-SIDE LONG-FORM observations
   Y = μ_a + b_i + (ab)_{a,i} + v_s + (av)_{a,s} [+ u_k][+ w_r] + ε per
   family, with arm means anchored so every registered contrast equals its
   cell parameter exactly; the §4.6/(1b) ledger families A, B, and D are
   restated on the SAME representation (family B's fitted unit changes
   from the record-pair difference to the arm-side record score — the
   difference form could not represent the crossed reviewer factor, whose
   assignments do not cancel pairwise; family A gains the previously
   implicit (av) seed×arm term). Reviewer is modelled on review-based
   endpoints (composite family + gate latents) in BOTH generation and
   fit; consumer on UCT sessions in both; every absent layer is stated
   with its variance fraction folded into the residual (the Rev7 folding
   rule, arm-side form — implied per-contrast difference SD = σ_j
   preserved and disclosed). The rotations are PUBLISHED:
   k(a,i,s) = (uct_arm_index(a) + i) mod n_consumers and
   r(a,i) = (rev_arm_index(a) + i) mod n_reviewers, with fixed arm-index
   tables, proved constraint properties (one session per record; no
   consumer/reviewer sees one concept under competing arms; exact balance
   because the pool sizes divide every simulated n-level — n_reviewers
   re-pinned 6 → 8 for exactly this, logged in S3), and tables emitted
   with the S8 configuration artifact. The ρ regimes are restated on the
   arm-side concept layer (within-family exchangeable + cross-family/gate
   correlation) with the working-model-closure argument stated — the
   arm-level model, concept×arm effects, and consumer assignment the
   spot-check found unreconstructible are now generated directly.
2. **(Correction 2 — exact mixed-model inference) — RESOLVED (R8b).**
   §4.6/(1b) gains the exact pins: REML with the nonnegativity boundary,
   GLS fixed effects, expected-information covariance
   I_mn = ½·tr(P Z_m Z_mᵀ P Z_n Z_nᵀ), and the Giesbrecht–Burns
   Satterthwaite formula ν̂ = 2·Var̂(θ̂)²/(gᵀĈg) — PLUS the named
   reference implementation at exact versions (R 4.4.1, lme4 1.1-35.5,
   lmerTest 3.1-3, ddf = "Satterthwaite") as the executable definition.
   S4.2's "unspecified closed-form ANOVA vs unspecified generic REML"
   latitude is DELETED: the sim engine may use any numerically exact
   algorithm for the pinned estimators, gated by the mandatory fixture
   equivalence check at pinned tolerances (|Δθ̂| ≤ 1e−7, rel. SE ≤ 1e−5,
   rel. ν̂ ≤ 1e−3, |Δp| ≤ 1e−6), with pinned fit-failure handling and a
   per-cell failure-rate ceiling; S9 is updated to match.
3. **(Correction 3 — valid crossed-binary gate test; cross-stratum
   contradiction) — RESOLVED (R8c).** The Rev7 Gaussian
   linear-probability LMM t-test is RETIRED (Gaussian-residual t
   calibration does not deliver super-uniformity on thresholded-normal
   Bernoulli data) and the gate test and DGM are replaced TOGETHER by one
   shared latent model: S4.4 pins the exact joint thresholded-Gaussian
   formula (concept/seed/reviewer components at the S4.1 fractions; gate
   concept dimensions inside the nonce copula; exact marginal-π mapping),
   and ledger family C tests π_a by the latent-probit moment statistic
   with a parametric-bootstrap p-value at the null boundary (B_boot =
   999, the exact-validity (1+#)/(B+1) form, concordance-class nuisance
   estimation with pinned inversion/truncation/failure handling, CI by
   bisection test-inversion), with level control DEMONSTRATED by the
   mandated 4-cell gate-calibration battery under an exact-bound
   acceptance criterion — never assumed. The cross-stratum contradiction
   is resolved by the spot-check's second branch: the claim that the
   concept layer makes the C-CON-SUP gate/contrast pairing adversarial is
   WITHDRAWN (those components are independent under the pinned DGM —
   cross-stratum correlation 0 — disclosed, with independence noted as
   intermediate between the benign and adversarial extremes); the
   within-stratum adversarial pairing for C-GRAPH is preserved and
   stated. Stage-1 interim futility gets a pinned cheap moment-based
   Wald bound (operational, binding-futility-only).
4. **(Correction 4 — bounded-Beta) — RESOLVED (R8d).** S4.3's
   bounded-Beta regime is redefined as a CENTERED, UNIT-VARIANCE
   standardized-Beta transform of the concept-layer coordinates (one
   pinned shape pair (2, 5)), applied BEFORE the √(f_concept/2)·σ_j
   scaling; θ_j enters once through μ_a. The Rev7 outcome-marginal
   mapping (mean θ_j, SD σ_j — double-adding θ_j and re-scaling σ_j) is
   retired.
5. **(Correction 5 — operational variables, row algorithms, price
   vectors, P1) — RESOLVED (R8e).** The DGM gains Δ^E (E-arm fidelity, a
   composite-family arm), per-arm 5-component TRUE cost vectors κ_a with
   measurement noise, and the review-time component; S4.9 pins EXACT
   algorithms for §4.8 rows 2 and 5–9 (row-2 margin ±0.05 pinned; §4.8
   carries the matching R8e pin note); the LCC decision is a robustness
   sweep of PRICE VECTORS applied to component COST-VECTOR differences —
   D̂(x,y;p) = p·(κ̂_x − κ̂_y) — which genuinely can and (for the pinned
   default E-vs-H pair) does reverse sign across the sweep, replacing
   the sign-invariant scalar w·L̂; and P1 takes the INCLUDE-LCC branch:
   it is the deflation-ADOPTION power (C-VAL ∧ C-DEF-NSUP ∧
   stable-T-cheaper), stated, with the confirmatory-only probability
   reported alongside.
6. **(Correction 6 — Rung-0 pins) — RESOLVED (R8f).** §7 pins the
   integer look rule n_ℓ = ⌈φ_ℓ·n_max⌉ with the explicit look-count
   table (96 → 39/68/96; 160 → 64/112/160) and identifies n_max with the
   configured nonce budget; S4.8 generates ONE shared arm-side accruing
   Rung-0 dataset (five arms, shared T and concept layer) so the four
   route contrasts' joint correlation is pinned by construction, and
   draws the four pilot estimates jointly with pinned exchangeable
   covariance (ρ_p = 0.5); ν_D(ℓ,r) is computed by the R8b-pinned
   Satterthwaite implementation; and F10 declares its termination
   acceptance rule and output (exact one-sided 95% upper bound on the
   whole-branch termination rate ≤ τ_term0 = 0.055, mandatory fields in
   the FWER artifact).
7. **(Correction 7 — reproducibility) — RESOLVED (R8g).** S2 pins
   CPython 3.12.x, numpy 2.1.3, scipy 1.14.1 (and the R reference stack
   for the fixture check only), declares config and replication indices
   ZERO-BASED, and pins the named 13-substream `.spawn(13)` layout with
   fixed purposes, spawn order, and within-stream draw ordering, so a
   reimplementation reproduces every draw bit-exactly; version bumps are
   logged re-pins with fixture re-verification.

No finding is rebutted. Two consistency consequences are recorded openly
rather than silently absorbed: (i) restating ledger families B/D on the
arm-side unit and adding the (av) term is the spot-check's own preferred
branch ("preferably arm-side long-form observations") — estimands,
margins, claims, and the procedure are untouched; (ii) n_reviewers moves
6 → 8 (an S3 planning default, not a procedure constant) so the published
reviewer rotation is exactly balanced at every simulated n-level — the
alternative (unbalanced rotation) would have broken the exact-cancellation
property the closed inference relies on. [STIPULATED]

## Revision 9 — A4 gate-calibration fix

Focused single-defect revision from the (B) simulation build
(`poc/99a-sim/SPEC-DEFECTS.md`, item A4 — the ONE genuine spec defect the
build surfaced; its A3 note records that the 12-claim procedure, weights,
transition matrix, update algorithm, IUT/TOST composition, truth
functions, grid expansion, and seed system were all codeable with ZERO
remaining design decisions, and the mock validated FWER control:
global-null familywise rejection 0.000 with CP-UB 0.005; strong-FWER cell
0.010 with CP-UB 0.0196 ≤ τ_FWER = 0.055). Rev9 changes NOTHING outside
the A4 surface.

1. **The defect ([MEASURED] — mock build, gate-cal cell ρ = 0.1,
   n_nonce = 96, π_a = π₀ = 0.60, R = 1,200, all four arms).** The
   mandated S4.4 gate-calibration battery FAILS at the component level
   under the Rev8 test as written: realised rejection ~0.075 at
   γ = 0.025 (bar ≤ 1.25·γ = 0.031) and ~0.04 at γ = 0.00625 (bar
   0.0078). The implementer isolated the mechanism: the concordance
   estimators are UNBIASED (mean concordances match the theoretical
   orthant probabilities at the true (ρ_c, ρ_s, ρ_r) = (0.5, 0.1, 0.1)
   to 3 dp), but the Rev8-mandated PER-REPLICATION hard truncation of a
   no-root inversion to ρ̂ = 0, fed directly to the bootstrap, biases
   the SMALL components (ρ_s, ρ_r = 0.1, just above the independence
   floor) downward per replication — their noisy concordances often dip
   below the floor — so the null-boundary bootstrap is UNDER-dispersed
   (sd 0.059–0.072 vs the true π̂ sd 0.084) and the observed π̂ looks
   too extreme too often. Fed the TRUE dependence, the same bootstrap is
   well-calibrated (sd 0.091 ≥ 0.084). Claim-level FWER still held
   ≤ 0.055 in every tested cell (the IUT conjunction tempers the
   inflation), but F5 shows it propagating (familywise 0.037, CP-UB
   0.052) — eating the margin — and the battery is a MANDATORY S8
   acceptance criterion that fails as pinned.

2. **The fix (R9a — [STIPULATED] design choice; the implementer's
   suggested direction, option (a)):** the bootstrap-null dependence
   plug-in becomes the CONSERVATIVE FLOORED triple
   ρ̃ = (ρ̂_c, max(ρ̂_s, ρ_floor), max(ρ̂_r, ρ_floor)),
   ρ_floor = 0.15 = 1.5× the S3 planning fractions
   f_seed = f_reviewer = 0.10 (with the pinned consistency rule: any
   upward re-pin of those fractions re-pins the floor and re-runs the
   battery), applied in the pinned order floor → clip [0, 0.98] →
   proportional rescale to sum ≤ 0.98. The point-estimation pins
   (concordance classes, orthant inversion, no-root → 0, the
   ρ̂_c = max(0, ρ̂_cr − ρ̂_r) decomposition) are UNCHANGED — only what
   the bootstrap consumes changes. The S4.6 futility moment SE uses the
   same ρ̃ (one shared dependence treatment; floors only widen that
   bound, preserving its conservative binding-futility direction).
   §4.6/(1b)(C), S4.4, S4.6, S8, and §8 are updated together; a
   mandatory dispersion-diagnostics block is added to the battery
   report.

3. **Why this removes the downward bias while keeping super-uniform
   validity.** The bootstrap null's dispersion — hence its rejection
   threshold — is monotone INCREASING in every dependence component
   (each pair-class covariance P₁₁(ρ; π₀) − π₀² increases in ρ at the
   exact marginal π₀, which the construction fixes for every ρ). The
   Rev8 truncation therefore erred in the uniquely harmful direction:
   dependence understated ⇒ null under-dispersed ⇒ anti-conservative.
   The floor inverts the sign of the error: whenever true seed/reviewer
   dependence ≤ ρ_floor (the battery's regime, and the design's
   anticipated regime with a 50% margin), the bootstrap null is
   at-least-truth dispersed ⇒ over-rejection becomes under-rejection —
   the super-uniform direction. With KNOWN dependence the (1+#)/(B+1)
   Monte-Carlo p is exactly super-uniform by exchangeability
   ([LIT-BACKED] — the retained Barnard 1963 / Davison & Hinkley 1997
   citations, supporting-only per §5); the composite null π_a < π₀
   keeps the boundary test conservative in its interior; and
   finite-sample level control remains DEMONSTRATED by the battery,
   never assumed — the document's standing epistemic posture for this
   test, unchanged. Above the floor the estimate is used as-is, and the
   scope of the demonstration (floor-binding regime) is disclosed in
   §4.6/(1b)(C) and S4.4 rather than silently assumed away.

4. **Why the battery should now pass its ≤ 1.25·γ bar at all 4 cells
   (mechanistic argument).** The dispersion deficit was carried by the
   two floored components: π̂ averages over only n_seeds = 3 seed and
   n_reviewers = 8 reviewer clusters, so the same-seed and same-reviewer
   pair classes dominate Var(π̂) (O(1/S) and O(1/n_rev) weight), while
   the concept term is O(1/I) (I = 96 or 160) — which is exactly why
   collapsing ρ̂_s, ρ̂_r to 0 crushed the bootstrap sd to 0.059–0.072
   vs 0.084 while leaving ρ̂_c noise immaterial. With the floor, the
   dominant terms enter the bootstrap at ≥ 0.15 > the true 0.10 in
   every replication, so the bootstrap null's sd is ≥ the
   true-dependence sd essentially always — and the mock already
   [MEASURED] that the true-dependence bootstrap is well-calibrated with
   margin (sd 0.091 vs 0.084). Per-replication thresholds therefore sit
   at or above their well-calibrated values ⇒ realised rejection ≤ γ
   with room under the 1.25·γ bar. All four battery cells share the
   same within-arm dependence truth (0.50, 0.10, 0.10) — the cells vary
   only the copula ρ and n_nonce, neither of which enters the within-arm
   gate covariance — so the argument covers all 4 cells uniformly.
   [EXTRAPOLATION — direction-only: this argues the full R = 40,000
   battery will pass; it motivates the executor's re-run and is not
   used as a premise anywhere — the battery itself remains the
   demonstration and the acceptance criterion.]

5. **What is deliberately untouched (everything the (B) build
   validated).** The graphical procedure, the 12-claim ledger, initial
   weights, transition matrix, update algorithm, IUT/TOST compositions,
   margins, truth functions, hypothesis functions, the S6 74-cell FWER
   grid and S7 power grid (the battery stays 4 cells, outside the FWER
   grid), the DGM formulas, seeds/substreams, and every other acceptance
   criterion are byte-unchanged. The battery's ≤ 1.25·γ exact-bound
   acceptance rule is numerically unchanged; it now audits the floored
   test and carries the mandatory dispersion diagnostics.

6. **Next step (executor).** Re-run the 4-cell gate-calibration mock
   against the R9a floored test and verify every (cell, arm, γ)
   realised rate's CP upper bound ≤ 1.25·γ, with the diagnostics
   showing mean bootstrap-null SD ≥ empirical SD of π̂ — BEFORE
   committing to the full R = 40,000 run. A failure is a reportable
   design defect per S9, routed back — never resolved locally.

## Mandatory self-check — Revision 2 (historical record, retained verbatim; superseded by the Revision 8 self-check below)

1. **All 13 critique findings addressed?** YES — itemised in "Revision 2" above with
   section anchors and row labels R2a…m (one per finding); none rebutted; the deferral
   list contains only the critique's own legitimately-deferrable items.
2. **Finding-1 three-part fix landed?** YES — (a) §4.6: every registered TOST, the
   dominant H-TEXT ±0.03 first, powered ≥90% under the same `INSTRUMENT-INVALID` rule
   as the superiority contrast; (b) §4.8 row 4: inconclusive T/T′ equivalence BLOCKS
   constructed-arm adoption, placed above every constructed-arm verdict row, escalation
   retargeted at the T-contrast; (c) §4.8 LCC: single measurable lifecycle composite
   replaces the four-axis conjunction, maintenance operationalised as one pinned
   revision cycle, the remainder descriptive-only and excluded from decision rules.
3. **§1.2 no longer promotes on model-only endorsements?** YES — condition 5 requires
   ≥1 qualified human or sector-authority endorsement (or formal-sector mechanical
   proof/model-check); model endorsements are never jointly sufficient in any number
   (R2b), with the shared-corpus caveat stated at the gate.
4. **RULES-2 in the evidence base + K-NULL bridge tagged [EXTRAPOLATION]?** YES — §0b
   and §6 carry RULES-2 (PASS, audit CONFIRMED, primary LB +0.316) with its
   never-kernel-specific cap; §3.2's K-NULL→construction bridge is tagged
   [EXTRAPOLATION] across the mechanism envelope and demoted from "strengthens with
   repository data" to "motivates".
5. **Every load-bearing claim tagged?** YES — [MEASURED] only with repository file
   citations; [STIPULATED] on every design choice/criterion/gate/margin/law/rung;
   [LIT-BACKED][SV] supporting-only; [EXTRAPOLATION] appears twice (§3.2 K-NULL bridge;
   §3.2 direction note) — both motivation-/direction-only, never a premise for any
   verdict or gate.
6. **No [MEASURED] on a choice?** YES — re-checked after every Rev2 edit: each
   [MEASURED] tag anchors a repository result file; the K-NULL→construction bridge
   specifically is now [EXTRAPOLATION], repairing the Rev1 defect the critique caught;
   all new Rev2 laws, gates, and composites carry [STIPULATED].
7. **No @handle/account strings?** YES — models, pipelines, and roles are referred to
   by model/pipeline/role names only (Sol/GPT-5.6, largekern-10k, Haiku Framework-G);
   no @-handles or account identifiers appear.
8. **No `ASM-<number>` minted?** YES — only `PROPOSED-PREREG-ROW-99A-R1a…j` and
   `…-R2a…m` labels; §8 states ids are assigned at prereg-freeze; the RULES-2 cap is
   quoted with its registry ids elided rather than reproduced.
9. **Nothing committed / registered / frozen?** YES — this is an in-place edit of the
   design document only; no git operations, no registry writes, no prereg-freeze, no
   runs launched; the top banner marks it NOT a maintainer submission and NOT a prereg
   freeze, with NEXT = source-verify [SV] → maintainer (the critique loop is complete).

## Mandatory self-check — Revision 3 (historical record, retained verbatim; superseded by the Revision 8 self-check below)

1. **All 3 CRITICALs fully resolved?** YES — (CRITICAL-1) the graph-isolation control
   is added: arm A2-IR (§4.3) receives H's atoms/relations in flat non-graph form with
   matched evidence/prompt/budget/reviewer visibility; H−A2-IR is the sole
   graph-isolating contrast (§4.1, §4.6, §4.8), and the oracle-IR family is labelled an
   upper-bound mechanism test barring production graph-import claims (§3.2, R3a).
   (CRITICAL-2) text deflation is split into H-TEXT-FORMAT (T′, format probe, charged
   all shared upstream construction/review costs, barred from deflation verdicts) and
   H-TEXT-SOURCE (T, independently governed plain-text store), with a **common
   estimand** — every arm scored against the same three-valued packet-relative target
   by the same deterministic procedure (§4.5), the nonce oracle-parse caveat declared,
   and decision-grade T-source evidence anchored on the natural stratum + Stage-2
   common consumer (§4.3, R3b). (CRITICAL-3) the three-valued packet-relative target is
   formally defined over the pinned generator rule grammar (TRUE under every
   packet-consistent rule / FALSE under every / else UNKNOWN); exact hidden-rule
   equivalence is confined to machine-checked fully-identifying packets;
   supported-content fidelity and abstention calibration are reported separately on
   underdetermined packets (§4.2, §4.5, R3c).
2. **All 6 MAJOR + 1 MINOR applied?** YES — four-zone CI rule + ordered gatekeeping
   family with alpha allocation (§4.6, R3d); crossed-hierarchy analysis + power under
   the exact final model, joint adoption-path power, equivalence power at true effect
   zero, and the Rev2 margin-widening clause deleted (§4.6, R3e); non-compensatory
   fidelity gates + outcome-disjoint frozen weights + declared-price,
   uncertainty-bounded, robustness-swept LCC with the maintenance term renamed
   "one-revision-cycle cost" (§4.5, §4.8, R3f); ≥2-human/authority floor,
   evidence-only pre-judgments, drafter-assisted source selection prohibited, pinned
   sampling frame + dual assembly audit, KBUILD-0 human-only endorsement (§1.2, R3g);
   Rung 0 scope-limited with the conservative conditional-futility rule (§7, R3h);
   decision/provenance-hash vs semantic-identity separation (§1.1, R3i). Itemised with
   dispositions in "## Revision 3 — cross-vendor findings applied"; none rebutted.
3. **Governance architecture preserved intact?** YES — the three-property separation
   (§1.1), verified-proposer frame (§2/§3), deterministic-vector-as-derived-only
   (§1.3/§3.1 step 5), human/authority promotion floor (§1.2 — strengthened, not
   weakened), A2 citation-only ablation (§4.3), graph-as-falsifiable-hypothesis
   (§3.2), ≥90%-per-equivalence-test power + inconclusive-blocks-adoption (§4.6/§4.8
   row 4), and the two-sided §0b evidence base are all unchanged in substance; every
   Rev3 edit tightens controls or estimands without moving semantic authority toward
   any model.
4. **Every load-bearing claim tagged; no [EXTRAPOLATION] as a premise?** YES —
   [MEASURED] only with repository citations; every design choice (including all Rev3
   arms, targets, rules, and laws) is [STIPULATED]; [LIT-BACKED] claims carry
   resolvable backings and are supporting-only (source-verify complete,
   `99a-rev2-sv-report.md` / `-extlit.md`); [EXTRAPOLATION] appears only in §3.2's
   motivation and direction notes, and §6 now lists the reviewer's residual
   extrapolation risks as binding caps — none is a premise for any conclusion,
   verdict, or gate.
5. **No @handle/account strings?** YES — models, pipelines, and roles are referred to
   by model/pipeline/role names only; no @-handles or account identifiers appear.
6. **No `ASM-<number>` minted?** YES — only `PROPOSED-PREREG-ROW-99A-R1a…j`,
   `…-R2a…m`, and the new `…-R3a…i`; ids are assigned at prereg-freeze; the review's
   findings are referenced by its own CRITICAL/MAJOR/MINOR numbering.
7. **Nothing committed / registered / frozen?** YES — in-place edit of this proposal
   document only (the review file untouched); no git operations, no registry writes,
   no prereg-freeze, no runs; the top banner marks this a REVISED DRAFT with NEXT =
   re-review of the Rev3 experimental design → maintainer decision on #59, and states
   that adoption requires that re-review plus the maintainer decision.

## Mandatory self-check — Revision 4 (historical record, retained verbatim; superseded by the Revision 8 self-check below)

1. **T-source adoption-blocker resolved with one unconditional common estimand?**
   YES — the unconditional held-out claim task (UCT) is the T-source decision
   endpoint (§4.5/R4a): same blinded consumers, identical artifact/consumer budgets
   for T and every constructed arm; runs in Stage 1 for every arm in both strata,
   ungated by the sequential boundary and independent of Stage 2 (§4.4); natural
   TRUE/FALSE/UNKNOWN defined relative to the published build packet with the
   held-out source confined to claim generation + a descriptive external-truth
   label (§4.2); ONE decision statistic (natural-stratum paired per-concept
   macro-BA difference, comparison arm per the §4.6 hierarchy with fallback A1)
   feeds the four-zone rule; nonce oracle parse-back explicitly secondary (§4.3,
   §6, §7 Rung 0/1).
2. **FWER procedure valid + zones non-overlapping + power re-simulated?** YES —
   §4.6: fixed-sequence-at-full-α deleted; E1–E8 enumerated (A2−A1 and
   A1−A0/H-REVIEW restored); graphical gatekeeping with pinned local weights and
   explicit recycling edges; Holm within E1's plural shuffle contrasts; alpha moves
   only on rejection of a null at its assigned local level; δ ≥ m required for
   every four-zone contrast (verified consistent with the H−A2-IR margins:
   δ = +0.08 ≥ m = 0.05), making the zones mutually exclusive; the power bullet
   mandates re-simulation under the exact final multiplicity procedure (R4b).
3. **Non-compensatory endpoint mathematically complete?** YES — §4.5/R4c: Level-1
   gate-pass-rate hurdle with ALL failed/illegal/gate-breaching records in the
   denominator and a pinned arm-level safety gate; Level-2 composite only after
   every arm in the contrast passes; gate-breaching records floor-imputed, never
   dropped, so every paired per-concept difference — including H−A2-IR with a
   breaching record — is defined on every concept; no undefined estimand remains.
4. **Rung-0 covers A2-IR + H on a differential increment?** YES — §7 Rung 0/R4d:
   unreviewed-A2-IR and unreviewed-H added to the arm set; branch termination
   requires unreviewed-r + Δ_rev(r) futile **relative to T for every route
   r ∈ {A1, A2, A2-IR, H}**, with all Δ_rev(r) pinned from the independent
   review-calibration pilot before unblinding; any unboundable Δ_rev(r) prohibits
   whole-branch termination; survivors always advance to the small reviewed pilot.
5. **Kill/precedence/text-rule consistent everywhere?** YES — swept: the §4.8
   H-GRAPH rule is three-outcome (advance / kill only on confirmed
   equivalence-or-inferiority or futility / indeterminate = row 9, no kill); the
   unreviewed-drafting rule uses the same discipline; the text rule reads
   "text superior, OR equivalent with lower LCC" identically in §3.2 (corrected),
   §4.1 H-TEXT-SOURCE, the §4.8 deflate-to-text rule, and precedence row 3; row 10
   amended so nonce results can never override the R4a T-source decision.
6. **§8 consolidated + stale rows superseded?** YES — §8.0 is the single
   controlling table (conflicts resolve to it); R1a (six→seven conditions), R1d
   (H-vs-A2 → H-vs-A2-IR), R1e (A2-IR + UCT added), R2b (≥2-human floor per R3g),
   R2l (Rung 0 kills unreviewed routes only), R3a/R3b/R3d/R3f/R3h/R3i amended,
   replaced, or completed in place; canonical term "evidence-release hash" applied
   in §1.1 and R3i; §4.2 renderer-family cross-reference corrected to gate 3.
7. **Every load-bearing claim tagged; no [EXTRAPOLATION] as a premise?** YES —
   every Rev4 design choice (UCT, R4b procedure and weights, hurdle estimand,
   differential futility, three-outcome rules, consolidation) is [STIPULATED];
   [MEASURED] tags still anchor only repository result files; [LIT-BACKED][SV]
   remains supporting-only; [EXTRAPOLATION] still appears only in §3.2's
   motivation/direction notes and the §6 binding caps — never as a premise for any
   conclusion, verdict, or gate.
8. **No @handle/account strings?** YES — models, pipelines, and roles are referred
   to by model/pipeline/role names only; no @-handles or account identifiers were
   introduced in Rev4.
9. **No `ASM-<number>` minted?** YES — only `PROPOSED-PREREG-ROW-99A-R1a…j`,
   `…-R2a…m`, `…-R3a…i`, and the new `…-R4a…f`; ids are assigned at prereg-freeze;
   the re-review's findings are referenced by its own residual numbering.
10. **Nothing committed / registered / frozen?** YES — in-place edit of this
    proposal document only (the review file untouched); no git operations, no
    registry writes, no prereg-freeze, no runs launched; the banner marks this a
    REVISED DRAFT with NEXT = re-review of the Rev4 experimental design →
    maintainer decision on #59, and states that adoption of anything beyond the
    governance-architecture pilot requires that re-review AND the maintainer
    decision.

## Mandatory self-check — Revision 5 (historical record, retained verbatim; superseded by the Revision 8 self-check below)

1. **Every atomic null enumerated + complete transition matrix +
   procedure-adjusted bounds + FWER/power re-simulated?** YES — §4.6/R5a: 95
   atomic one-sided nulls tabulated across ten nodes, covering every
   directional/equivalence component, every arm-level safety gate, both H-HUMAN
   endpoint components, both format contrasts on one pinned endpoint, all four
   candidate-vs-T contrasts, and A0 canon-readiness; the initial weight vector
   (all mass on E1) and the complete transition matrix are published with the
   pinned update algorithm and within-node closed procedures; an indeterminate
   E1 now mathematically blocks every downstream node (the re-review's
   positive-initial-alpha defect is gone); every four-zone label is read from
   ONE confidence set at the node's final procedure-assigned level; every
   operative 95% threshold is replaced (§4.1 H-GRAPH, §4.6 decision thresholds,
   §4.6 hierarchy re-labelled selection-only, §4.8 kill bounds, E9 bounds),
   with instrument gates and rung bars explicitly outside the family; §4.6
   item 7 makes the strong-FWER grid + adoption-path power simulation
   freeze-blocking under the exact implementation.
2. **UCT executable (claim count/class allocation pinned, generator/labeler
   split, comparator inference valid)?** YES — §4.2: nine natural claims per
   sense at exactly 3/3/3 by generation-to-quota with pinned screens, cap,
   reserve-list replacement, and the pinned missing-class fallback (mean recall
   over non-empty classes; arm-independent; no exclusions); generators
   (source-exposed) are role-disjoint and access-logged from packet-only
   labelers with a pinned adjudication rule; §4.5 UCT execution pins fix
   consumer assignment/carryover, one frozen rendering/truncation rule,
   failed-artifact floor-entry, and the per-format competence battery; §4.7
   gate 11 gates the instrument; comparator inference is valid for ANY
   hierarchy outcome via E2's (and E7's) simultaneous candidate set.
3. **Rung-0 futility a formal simultaneous bound with sequential-error
   accounting?** YES — §7/R5c: U(r) is a one-sided upper prediction bound on
   θ(r) = (unreviewed-r − T) + Δ_rev(r), simultaneous over all four reviewed
   routes at 1 − α₀ (Bonferroni default), propagating both Rung-0 sampling and
   pilot estimation-plus-transfer uncertainty; termination only when every
   U(r) < f; looks at pinned interim points, binding-futility-only
   (conservative for confirmatory FWER) and modelled in the R5a simulation;
   the pilot's human cost is measured, charged, and reported; the
   human-apparatus wording is reconciled; the unboundable-increment
   prohibition is retained verbatim.
4. **Kill-wording consistent everywhere?** YES — swept the full document: kills
   occur ONLY via confirmed equivalence/inferiority zones or fired futility
   boundaries (R4e as completed by R5d); the §4.8 unreviewed-drafting rule's
   hard-gate breach is now CANNOT-ADVANCE, never a kill; §3.2 reads "fails to
   advance or is killed"; precedence rows 2/9, the H-GRAPH three-outcome rule,
   and the H-SHUFFLE bullet all conform; no other ambiguous "fails"/"kill"
   wording remains in an operative rule.
5. **Resolved items undisturbed?** YES — the UCT remains the dominant,
   unconditional T-source decision task with the single R4a statistic;
   packet-relative labeling is untouched (the held-out source still never marks
   packet-unsupported content as known); δ ≥ m zone geometry stands; the R4c
   hurdle endpoint stands (its safety gates are now also enumerated nulls —
   an addition, not an alteration); §8.0 remains the single controlling table,
   extended with Rev5 rows, never restructured.
6. **Every load-bearing claim tagged; no [EXTRAPOLATION] as a premise?** YES —
   every Rev5 design choice (atomic family, weights/matrix, UCT pins, gate 11,
   U(r) bound, kill taxonomy, deferral updates) is [STIPULATED]; [MEASURED]
   tags still anchor only repository result files; [LIT-BACKED][SV] remains
   supporting-only (the graphical-procedure and prediction-bound machinery is
   deliberately stated as stipulated design verified by the mandated
   simulation, not by literature authority); [EXTRAPOLATION] appears only in
   §3.2's motivation/direction notes and the §6 binding caps — never as a
   premise for any conclusion, verdict, or gate.
7. **No @handle/account strings?** YES — models, pipelines, and roles are
   referred to by model/pipeline/role names only; no @-handles or account
   identifiers were introduced in Rev5.
8. **No `ASM-<number>` minted?** YES — only `PROPOSED-PREREG-ROW-99A-R1a…j`,
   `…-R2a…m`, `…-R3a…i`, `…-R4a…f`, and the new `…-R5a…d`; ids are assigned at
   prereg-freeze; the re-review's findings are referenced by its own
   MAJOR/MINOR numbering.
9. **Nothing committed / registered / frozen?** YES — in-place edit of this
   proposal document only (the review file untouched); no git operations, no
   registry writes, no prereg-freeze, no runs launched; the banner marks this a
   REVISED DRAFT with NEXT = re-review of the Rev5 experimental design → if
   clean, preregistration-suitable → maintainer decision on #59, and records
   that governance-architecture adoption for a bounded pilot is separately
   available now per the Rev4 re-review.

## Mandatory self-check — Revision 6 (historical record, retained verbatim; superseded by the Revision 8 self-check below)

1. **Is the multiplicity procedure provably valid on ATOMIC nulls, with no
   full-family-weight-transfer-while-true-nulls-remain defect?** YES — 
   §4.6/R6a: the family is 12 ELEMENTARY claims (each one null, one valid
   p-value; union nulls by intersection-union with p = max of components —
   Berger 1982; TOST case per Berger & Hsu 1996), tested by the graphical
   procedure of Bretz, Maurer, Brannath & Posch (2009), a closed-testing
   shortcut (Marcus, Peritz & Gabriel 1976) with a published strong-FWER
   theorem valid under arbitrary dependence; its stated conditions
   (elementary nodes with valid p-values; initial weights ≥ 0 summing to 1;
   transition rows ≥ 0 summing to ≤ 1 with zero diagonal; the paper's update
   algorithm) are verified item-by-item in §4.6/R6a item 2. The defect is
   structurally impossible: a node IS one elementary null, so weight moves
   only on rejection of that null — if it is true, that rejection is itself
   the counted, controlled error; no composite node exists to be partially
   rejected. The gate ledger is unique (gates are alpha-free IUT components
   of the claims they govern; shuffle-arm exemption stated in §4.5); every
   component's endpoint/stratum is pinned in the claim table.
2. **Is every simplified/dropped/downgraded claim explicit and justified?**
   YES — the §4.6/R6a item-6 downgrade ledger (mirrored in R6b and the
   Revision 6 itemisation): A2-IR−A2, A2−A1, A1−A0/H-REVIEW, H-HUMAN, A0
   canon-readiness, and T′-shuffle to descriptive (each with its
   not-on-the-adoption-path / conservative-block justification; the Rev4
   restoration of A2−A1 and A1−A0 openly reversed under #59); every
   equivalence/inferiority KILL direction to operational (kills only
   withhold/retract — conservative for Type-I error; branch-loss cost
   quantified in SIM-SPEC); §4.5's contrast list, §4.8's rules/matrix
   mapping, and §8.0 all updated consistently; the maintainer sanctioned
   exactly this simplification in #59.
3. **Does Rung-0 cover sequential looks with a concrete bound?** YES — §7/R6c:
   route-by-look spending at per-test level α₀/(4L) over L pinned looks
   (union-bound simultaneous coverage 1 − α₀ across all looks × routes), the
   explicit transfer model Δ_rev(r) = δ_p(r) + b(r) with |b(r)| ≤ B(r) =
   (κ_pool + κ_mix + κ_budget)·max(|Δ̂_rev(r)|, Δ_min), and the executable
   bound U_ℓ(r) = D̂_ℓ(r) + Δ̂_rev(r) + B(r) + t·√(SE_ℓ² + s_p²) with
   Welch–Satterthwaite df; termination only at a pinned look with every
   U_ℓ(r) < f; unboundable-increment prohibition retained verbatim;
   binding-futility-only, so confirmatory FWER is untouched.
4. **Does H-TEXT-FORMAT name a single confirmatory endpoint with valid
   selection inference?** YES — §4.1: the endpoint is Stage-2 host
   three-label macro-BA ONLY (format handling and consumer cost descriptive);
   selection validity by simultaneous coverage — one C-FMT-c claim per
   candidate arm (every candidate × format contrast pre-registered at a
   pre-assigned level, reachable through that candidate's own adoption
   claim), valid under any hierarchy selection; the descriptive
   external-truth label has its bound source-exposed descriptive-labeler
   producer role (§4.2/R6d).
5. **Is the SIM-SPEC implementable without further design?** YES — the
   ## SIM-SPEC section pins the object under test (the full R6a pipeline
   including selection, Stage-2 conditionality, and both futility layers),
   language/libraries, base seed and per-(config, rep) stream rule,
   determinism checks, the contrast-level DGP with copula-linked gates and a
   bounded-Beta sensitivity regime, the registered-analysis implementation
   (t-based components, exact binomial gates, permutation-concordance
   subcheck with tolerance), a feasible-by-construction null grid (F1–F11 ×
   correlation × model regimes; the infeasible Rev5 grid entry superseded),
   power grid P1–P6 with floors, replication counts with Monte-Carlo error
   bounds (40,000 / 10,000), exact acceptance criteria (p̂ ≤ .05 AND
   Clopper–Pearson upper ≤ .055 per cell; floors ≥ .90; false-termination
   ≤ .02), output file names/formats, and an exhaustive executor-latitude
   clause (§S9) that routes any ambiguity back to design. An executor can
   code it directly; running it is task (B).
6. **Every load-bearing claim tagged; no [EXTRAPOLATION] as a premise?** YES —
   every Rev6 design choice (claim ledger, weights/matrix, downgrade ledger,
   look rule, transfer envelope, SIM-SPEC contents) is [STIPULATED]; the
   multiplicity procedure's validity is [LIT-BACKED] with full citations
   (Bretz et al. 2009; Marcus et al. 1976; Berger 1982; Berger & Hsu 1996)
   and flagged for pre-freeze source-verification under §5 — the one
   deliberate load-bearing-literature exception, stated as such, with
   conditions re-verified in-document and behaviour additionally simulated;
   [MEASURED] tags still anchor only repository results; [EXTRAPOLATION]
   appears only in §3.2 motivation notes and §6 caps, never as a premise.
7. **No @handle/account strings?** YES — models, pipelines, reviewers, and
   roles are referred to by model/pipeline/role names only; the new citations
   use author surnames and journal references only.
8. **No `ASM-<number>` minted?** YES — only `PROPOSED-PREREG-ROW-99A-R1a…j`,
   `…-R2a…m`, `…-R3a…i`, `…-R4a…f`, `…-R5a…d`, and the new `…-R6a…e`; ids are
   assigned at prereg-freeze.
9. **Nothing committed / registered / frozen / run?** YES — in-place edit of
   this proposal document only (the review file untouched); no git
   operations, no registry writes, no prereg-freeze, no simulation runs
   launched (SIM-SPEC is a specification; its execution is task (B)); the
   banner records the #59 status — governance architecture ADOPTED for a
   bounded pilot; confirmatory experiment: valid procedure locked + SIM-SPEC
   ready → (B) simulation build → re-review → prereg.

## Mandatory self-check — Revision 7 (historical record, retained verbatim; superseded by the Revision 8 self-check below)

1. **Is the analysis ledger complete and EXECUTABLE for every component?**
   YES — §4.6 item (1b): four component families (UCT contrasts,
   nonce-composite contrasts, gate rates, format contrasts), each with
   estimand population/stratum, observational unit, seed-aggregation rule
   (no pre-averaging), model formula, REML estimator, Satterthwaite
   denominator df (the ONE pinned method), the generic one-sided p-value
   formulas, and the exact matching confidence-bound inversion (test–CI
   duality at the claim's final local level); BCa demoted to descriptive;
   the SIM-SPEC reference implementation named as the executable oracle
   with a freeze-time software cross-check.
2. **Exact-binomial vs crossed design resolved?** YES — by REPLACEMENT
   (ledger family C): record-level gate indicators are not iid under
   crossed concept/author-seed effects, so Clopper–Pearson is retired for
   the preregistered linear-probability mixed-model test with concept and
   seed crossed random intercepts; gate estimand stratum (primary/nonce)
   and unit (record, never a collapsed concept-level indicator) pinned; the
   LPM boundedness caveat and its descriptive bootstrap robustness read
   stated; the SIM verifies finite-sample level. The judgement call
   (replace, not justify-iid) is recorded openly in the Revision 7 section.
3. **C-DEF-NSUP branch renamed everywhere + LCC role stated?** YES —
   renamed to "T is noninferior to every candidate within m_T and has lower
   LCC" in §3.2, §4.1, the §4.6 four-zone mapping and claim-ledger row 2,
   the §4.8 deflate-to-text rule, precedence row 3, and the row-to-claim
   mapping; the historical R4e row amended via §8.0. LCC pinned as an
   operational-policy filter OUTSIDE the IUT (withholds adoption only; no
   positive confirmatory rejection; hence FWER-neutral) — §4.6/R7b.
4. **Rung-0 Welch/df pinned + nested interims mandated?** YES — §7/R7c: the
   exact ν̂(ℓ,r) formula with ν_D(ℓ,r) (fitted Satterthwaite) and
   ν_p = n_p − 1; the conditionality statement (|b(r)| ≤ B(r),
   pilot/campaign independence, t/Welch calibration — an envelope, not
   distribution-free); nested cumulative interims mandated and implemented
   in SIM-SPEC S4.8.
5. **Does the SIM-SPEC simulate the FULL claimed pipeline?** YES — S4:
   crossed author-seed/reviewer/consumer generation (S4.1), the R7a ledger
   analyses replacing one-sample t-tests and exact binomial (S4.2),
   hierarchy-rung selection with fallback A1 from simulated rung increments
   (S4.5), the pinned Stage-1 binding-futility boundary (S4.6), the
   endogenous Stage-2 trigger with stranding and a forced-off override for
   the F7 check (S4.7), the corrected Rung-0 layer with nested interims
   (S4.8), and the LCC/four-zone/kill operational layer (S4.9); errors
   counted ONLY at claim level on the 12 claims (S1).
6. **Claim truth derived programmatically; F4–F9 errors gone?** YES — S1/S5:
   one shared hypothesis-function module (null_j(θ) written out) imported by
   both the testing engine and the truth derivation; the hand truth column
   is DELETED from all config tables (truth sets are computed outputs in the
   S8 normative config file, hashed before any replication); F4/F8/F9's
   all-four-C-CON-SUP truth, F6/F7's C-DEF-null truth, and F5's explicit
   full parameter assignment all fall out mechanically and are noted in S5;
   F6's impossible "adoption deep-false + Stage 2 executed" combination is
   replaced by an adoption-true world.
7. **b(r) circularity/direction, copula sign, generator, grid fixed?** YES —
   S4.8: B*(r) from TRUE quantities (no circular reference to the random
   plug-in envelope; the plug-in's coverage is now a measured output);
   s_b = +1 pinned as the adverse direction in P6 and F10. S4.4: gate
   passes co-occur with HIGH contrasts (orientation reversed, stated).
   S4.3: bounded-Beta copula with explicit moment-matching formulas and
   pinned block membership (ρ_w = 0.8 / ρ_b = 0.3). S2: Philox alone.
   S6: 70 primary + 4 block-sensitivity = 74 cells with the exact expansion
   order pinning config_index → SeedSequence.
8. **Coherent MC acceptance rule?** YES — S6/S7: ONE rule — exact one-sided
   95% Clopper–Pearson UPPER bound on realised FWER ≤ τ_FWER = .055 per
   cell; exact one-sided 95% LOWER bound ≥ .90 per floored power path;
   upper bound ≤ τ_term = .025 for false termination; planning targets
   (≥ .92 / ≤ .015) separated ≥ 4 MC-SEs from the boundaries; the "p̂ ≤ .05"
   point condition and the separate ".05 + 2SE" threshold are deleted
   everywhere in the operative spec (they survive only inside the
   superseded R6e historical row, marked as such).
9. **Closure documented + IUT conservatism respected?** YES — §4.6 item (2)
   condition (vi): restricted combinations recorded with the specific
   implications; validity via closed testing's per-intersection level-α
   property (restrictions add conservatism only; no weight-sharpening
   claimed); item (1): component p-values required super-uniform; IUT size
   ≤ α stated, exact α reserved for TOST component pairs only — matching
   all four binding `[SV]` conditions (R7f).
10. **Procedure/claim structure UNCHANGED?** YES — the 12-claim ledger, all
    margins/notation, initial weights (all mass on C-VAL), the transition
    matrix, the update algorithm, the IUT compositions, the downgrade
    ledger, the Rung-0 route-by-look Bonferroni, and the H-TEXT-FORMAT
    simultaneous-coverage device are byte-preserved apart from the R7a/R7b/
    R7d wording clarifications the re-review itself required; no node,
    edge, weight, margin, or hypothesis was added, removed, or re-routed.
11. **Every load-bearing claim tagged; no [EXTRAPOLATION] as a premise?**
    YES — every Rev7 addition (analysis ledger, gate-test replacement,
    naming, Welch pins, SIM-SPEC rewrite, acceptance rule, closure note) is
    [STIPULATED]; the procedure's validity remains the one [LIT-BACKED]
    load-bearing exception with its four citations and pre-freeze `[SV]`
    obligation (now with the citation-SV conditions folded in);
    [EXTRAPOLATION] appears only in §3.2 motivation notes and §6 caps.
12. **No @handle/account strings; no `ASM-<number>` minted?** YES — roles
    and models by name only; new rows are exactly
    `PROPOSED-PREREG-ROW-99A-R7a…f`; ids are assigned at prereg-freeze.
13. **Nothing committed / registered / frozen / run?** YES — in-place edit
    of this proposal document only (both review files untouched); no git
    operations, no registry writes, no prereg-freeze, no simulation
    launched (SIM-SPEC execution is task (B)); the banner records the #59
    status — governance architecture ADOPTED for the bounded pilot;
    confirmatory experiment: procedure VALID (Rev6 re-review) + analysis
    ledger + corrected SIM-SPEC (Rev7) → (B) simulation build+run →
    re-review of results → preregistration.

## Mandatory self-check — Revision 8 (historical record, retained verbatim; extended — not replaced — by the focused Revision 9 self-check below)

1. **DGM and ledger share ONE data representation, reviewer/consumer
   consistent, rotations published?** YES — S4.1 generates arm-side
   long-form Y = μ_a + b_i + (ab)_{a,i} + v_s + (av)_{a,s} [+ u_k][+ w_r]
   + ε and the §4.6/(1b) families A/B/D are stated and fitted on exactly
   that representation (family B moved off the pairwise-difference unit;
   the (av) term made explicit in both); reviewer appears in generation
   AND fit on the review-based endpoints (composite family, gate latents)
   and nowhere else, consumer on UCT sessions in both, every absence
   stated with its fraction folded into the residual; the rotation
   ALGORITHMS are published with fixed arm-index tables —
   k(a,i,s) = (uct_arm_index(a) + i) mod 24,
   r(a,i) = (rev_arm_index(a) + i) mod 8 — with constraint/balance
   properties proved in-text and tables emitted in the S8 config artifact
   (R8a).
2. **Exact mixed-model inference pinned?** YES — §4.6/(1b) pins
   estimator (REML, nonnegativity boundary), covariance
   (expected-information), the Giesbrecht–Burns Satterthwaite formula,
   AND the named reference implementation with exact versions (R 4.4.1 +
   lme4 1.1-35.5 + lmerTest 3.1-3, ddf = "Satterthwaite"); S4.2 deletes
   the closed-form-vs-generic latitude, pins the fixture equivalence
   tolerances (|Δθ̂| ≤ 1e−7, rel. SE ≤ 1e−5, rel. ν̂ ≤ 1e−3,
   |Δp| ≤ 1e−6), and pins fit-failure handling with a per-cell ceiling;
   S9 matches (R8b).
3. **Gate test a valid crossed-binary procedure with demonstrated level
   control; cross-stratum correlation resolved?** YES — ledger C and
   S4.4 now share ONE thresholded-Gaussian latent model (exact joint
   formula, marginal-π mapping); the test is the moment-statistic
   parametric bootstrap at the null boundary (B_boot = 999, (1+#)/(B+1),
   pinned nuisance estimation/truncation/failures, CI by bisection
   inversion, [LIT-BACKED] Davison & Hinkley 1997 supporting-only), with
   level control DEMONSTRATED via the mandated 4-cell calibration battery
   under an exact-bound acceptance rule; the Gaussian LPM t-test is
   retired; the C-CON-SUP cross-stratum intended-correlation claim is
   WITHDRAWN with an honest independence disclosure, and the C-GRAPH
   within-stratum adversarial pairing is preserved (R8c).
4. **Bounded-Beta a pre-scaling concept RE?** YES — S4.3: standardized
   Beta(2, 5) transform of the concept-layer coordinates, exactly mean-0
   variance-1, applied BEFORE the √(f_concept/2)·σ_j scaling; θ_j enters
   once through μ_a; the Rev7 outcome-marginal mapping is retired (R8d).
5. **§4.8 rows 2/5–9 have exact algorithms; LCC can reverse sign?** YES —
   S4.9 pins the per-arm cost vectors κ_a with measurement noise, the
   5-vector price set, the pair statistics D̂(x,y;p) = p·(κ̂_x − κ̂_y)
   with lower-LCC/dominated/`COST-INDETERMINATE` reads, and one exact
   algorithm per row (row 2 at the pinned ±0.05 shuffle-equivalence
   margin; rows 5–9 on Δ^E, cost dominance, and the review-time
   component); component-wise prices on vector differences genuinely
   reverse sign (the default E-vs-H pair flips across the sweep); §4.8
   carries the matching R8e note; P1's estimand INCLUDES the LCC filter
   and is named the deflation-ADOPTION power, with the confirmatory-only
   probability reported alongside — the include-LCC branch, stated (R8e).
6. **Rung-0 integer looks, route/pilot covariance, F10 criterion
   pinned?** YES — §7: n_ℓ = ⌈φ_ℓ·n_max⌉ with the explicit table
   (96 → 39/68/96; 160 → 64/112/160) and n_max ≡ the configured nonce
   budget; S4.8: one shared five-arm accruing dataset pins the route
   joint correlation by construction, pilot estimates drawn
   N₄(δ_p₀, s_p²[(1−ρ_p)I + ρ_p J]) with ρ_p = 0.5; ν_D(ℓ,r) via the
   R8b-pinned implementation; F10's declared rule: exact one-sided 95%
   upper bound on whole-branch termination ≤ τ_term0 = 0.055, with
   mandatory output fields (R8f).
7. **Versions/indices/substreams pinned?** YES — S2: CPython 3.12.x,
   numpy 2.1.3, scipy 1.14.1, R reference stack fixture-only; zero-based
   config_index and replication_index; the named 13-substream spawn
   layout with pinned purposes and draw ordering; logged-re-pin rule for
   any version bump (R8g).
8. **Multiplicity procedure and claim structure UNCHANGED?** YES — the
   12-claim ledger, all margins, the initial weights (all mass on
   C-VAL), the transition matrix, the update algorithm, the IUT
   compositions, the restricted-combination documentation, and the
   downgrade ledger are byte-preserved; Rev8 touched ONLY the §4.6/(1b)
   analysis ledger (whose completion the spot-check itself ordered), one
   §4.6 item-2(i) test-name reference, §4.8's operational pins, §7's
   implementation pins, and the SIM-SPEC; no node, edge, weight, margin,
   claim, or hypothesis was added, removed, or re-routed; the S6 grid
   remains 70 + 4 = 74 cells (the gate-calibration battery is a separate,
   disclosed battery outside the FWER grid).
9. **Four epistemic tags disciplined; no [EXTRAPOLATION] as premise?**
   YES — every Rev8 addition is [STIPULATED] (design choices), with two
   new resolvable [LIT-BACKED] supports (Giesbrecht & Burns 1985 +
   Satterthwaite 1946 + Kuznetsova et al. 2017 for the pinned df
   machinery; Davison & Hinkley 1997/Barnard 1963 for
   parametric-bootstrap test validity), each explicitly supporting-only
   per §5 with the load-bearing weight on the reference implementation
   and the DEMONSTRATED calibration; no [EXTRAPOLATION] is used as a
   premise anywhere in the additions.
10. **No @handle/account strings; no `ASM-<number>` minted?** YES — roles
    and models by name only; new rows are exactly
    `PROPOSED-PREREG-ROW-99A-R8a…g`; ids are assigned at prereg-freeze.
11. **Nothing committed / registered / frozen / run?** YES — in-place
    edit of this proposal document only (the spot-check file untouched);
    no git operations, no registry writes, no freeze, no simulation
    launched; the banner records the #59 status — governance
    architecture ADOPTED for the bounded pilot; confirmatory experiment:
    procedure VALID + SIM-SPEC now BUILD-READY → (B) the coordinator
    builds + runs → re-review of RESULTS → preregistration.
12. **Could an implementer now code the SIM-SPEC with zero remaining
    design decisions?** YES, to this revision's best determination:
    every generator (S4.1 formulas + rotations + S4.3 copula/regimes +
    S4.4 gate latents + S4.8 Rung-0 + S4.9 costs), every fitted model
    and its exact estimator/df/p/bound definition (R8b pins + named
    reference oracle), every test including the binary gate procedure,
    every decision rule (selection, futility with its pinned interim
    bound, trigger, operational rows), every constant (S3 + S4.9
    tables), every seed/substream/draw-order rule, every acceptance
    criterion (FWER, power, F10 termination, gate calibration, fixture
    equivalence, determinism, fit-failure ceiling, stranding), and every
    output artifact are pinned; remaining executor choices are
    explicitly non-semantic (vectorisation, checkpointing, logging, any
    numerically exact algorithm under the fixture gate). Implementation
    is the FINAL consistency test: any ambiguity discovered in the build
    is, by S9, a reportable design defect routed back — never a local
    judgment call.

## Mandatory self-check — Revision 9 (final section)

1. **Does the estimator/bootstrap-null still downward-bias small
   dependence?** NO — the bootstrap now consumes the FLOORED triple ρ̃
   (seed/reviewer components never below ρ_floor = 0.15 > the S3
   planning fractions 0.10), so the mock-measured failure path
   (per-replication truncation-to-0 → under-dispersed null) cannot
   reach the bootstrap for the two components that dominate Var(π̂);
   the point-estimation pins (including no-root → 0) are retained but
   feed only the floored plug-in, and the residual unfloored component
   (concept) carries O(1/I) dispersion weight, [MEASURED] immaterial to
   the defect (`poc/99a-sim/SPEC-DEFECTS.md` A4).
2. **Does the gate test stay a valid super-uniform-under-H₀ level-γ
   test?** YES, on the document's standing posture, now in the
   conservative direction: exact super-uniformity with known dependence
   (the retained (1+#)/(B+1) Monte-Carlo construction, [LIT-BACKED]
   Barnard 1963 / Davison & Hinkley 1997, supporting-only per §5);
   dispersion monotonicity in every dependence component at the exact
   marginal π₀ means the floor turns dependence mis-estimation into
   OVER-dispersion of the null whenever true seed/reviewer dependence
   ≤ ρ_floor ([STIPULATED] working-model argument, disclosed scope);
   the composite null π_a < π₀ keeps the boundary test conservative in
   its interior; finite-sample level control remains DEMONSTRATED by
   the mandatory battery, never assumed.
3. **Does the S4.4 battery now pass its ≤ 1.25·γ bar — argued
   mechanistically?** YES (Revision 9 item 4): the dispersion deficit
   was carried entirely by the floored components (3 seed / 8 reviewer
   clusters ⇒ dominant O(1/S), O(1/n_rev) variance weight); with the
   floor ≥ 1.5× the true fractions in all four cells (which share the
   within-arm truth (0.50, 0.10, 0.10) — the cells vary only copula ρ
   and n_nonce, neither entering the within-arm gate covariance), the
   bootstrap sd is restored to at-least the true-dependence sd, which
   the mock [MEASURED] well-calibrated with margin (0.091 vs 0.084);
   the full-R pass expectation is tagged [EXTRAPOLATION —
   direction-only, motivating the mandated executor re-run, never a
   premise]; the battery itself remains the acceptance criterion, with
   new mandatory dispersion diagnostics to expose any residual
   mechanism failure.
4. **Nothing else changed — procedure byte-unchanged?** YES — the
   12-claim ledger, initial weights, transition matrix, update
   algorithm, IUT/TOST compositions, margins, truth functions, S5/S6/S7
   grids (battery stays 4 cells outside the FWER grid), DGM formulas,
   seed/substream system, and every other acceptance criterion are
   byte-preserved; Rev9 touched ONLY: the banner/status text, the
   SIM-SPEC heading tag, §4.6/(1b)(C)'s plug-in/failure-handling/
   calibration text, S4.4's test/battery text, S4.6's moment-SE
   dependence reference (same floored ρ̃, widening-only), the S8
   gatecal deliverable fields, §8.0 table + R8c row annotation + the
   new R9a row, and the Revision 9 / self-check sections.
5. **Four epistemic tags disciplined?** YES — [MEASURED] for the mock
   build's A4 measurements (cited to `poc/99a-sim/SPEC-DEFECTS.md`),
   [STIPULATED] for the floor value/order/consistency rule and the
   monotonicity working-model argument, [LIT-BACKED] only re-citing the
   already-source-verified Barnard/Davison–Hinkley basis
   (supporting-only per §5 — no new external citations minted), and
   [EXTRAPOLATION] exactly once (the full-R pass expectation),
   direction-only and never a premise.
6. **No @handle/account strings; no `ASM-<number>` minted?** YES —
   roles by name only; the single new row is exactly
   `PROPOSED-PREREG-ROW-99A-R9a`; ids are assigned at prereg-freeze.
7. **Nothing committed / registered / frozen / run?** YES — in-place
   edit of this proposal document only; `poc/99a-sim/SPEC-DEFECTS.md`
   untouched; no git operations, no registry writes, no freeze, no
   simulation launched; the mandated next step (the executor's 4-cell
   gate-calibration mock re-run against the R9a test, verifying
   ≤ 1.25·γ before the full run) is recorded, not performed.
