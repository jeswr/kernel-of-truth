# Kernel construction methodology — proposal 99a, REVISION 5

> **REVISED DRAFT — NOT A MAINTAINER SUBMISSION AND NOT A PREREG FREEZE.
> NEXT = re-review of the Rev5 experimental design → if clean, the confirmatory
> experiment is PREREGISTRATION-SUITABLE → maintainer (decision on #59). Per the
> Rev4 re-review, adoption of the governance architecture for a bounded pilot is
> separately available NOW; adoption of anything beyond that pilot requires the
> Rev5 re-review AND the maintainer decision; nothing is registered, frozen,
> scheduled, or committed by this revision.**
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

This is a revised draft applying the cross-vendor re-review of Rev4 — next stage a
re-review of the Rev5 experimental design (if clean, the confirmatory experiment is
preregistration-suitable), then the maintainer decision on #59. It is not a final
ruling and not yet a maintainer submission.

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
> **text-superior — regardless of LCC — OR equivalent with lower lifecycle-cost
> composite (LCC, §4.8)** (the uniform text rule — Rev4, re-review residual 5: the
> Rev3 wording here appeared to require lower LCC even when text was superior,
> contradicting §4.8 row 3), text deflation dominates any graph result; if the text
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
  confidence bound — at node E3's final procedure-assigned level, never a fixed
  95% (Rev5/R5a) — of the paired per-concept difference > +0.08 on the fidelity
  composite; the isolated increment is **explicit graph materialisation/closure** —
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
  (UCT, §4.5; PROPOSED-PREREG-ROW-99A-R4a), **text-superior, OR equivalent at lower
  LCC** (matching §4.8 row 3: the superior zone fires regardless of LCC). The UCT
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
  (true effect zero) on the R4a statistic under the final R4b multiplicity
  procedure, with the same `INSTRUMENT-INVALID` consequence as the superiority
  contrast; and an **indeterminate-zone** T-source outcome **blocks constructed-arm
  adoption** (§4.8 row 4). If supported, adopt the text store for this scope — this
  outcome **dominates** all constructed-arm contrasts (§4.8).
  (PROPOSED-PREREG-ROW-99A-R3b, amended by R4a)
- **H-TEXT-FORMAT (format probe, non-dominant — Rev3, cross-vendor CRITICAL-2
  split):** the deterministic prose rendering T′ of the *same endorsed record* as the
  hierarchy winner is equivalent to the AST/vector formats on downstream
  comprehension, format handling, and consumer cost (Stage 2 only). Because T′
  renders the same record, its **Stage-1 fidelity equivalence is largely true by
  construction and is NEVER evidence that plain text replaces construction**; T′ is
  charged **all shared upstream construction/review costs** in the LCC, and its
  verdict governs only *what format the constructed record ships in* — never whether
  construction happens. (PROPOSED-PREREG-ROW-99A-R3b)
- **H-SHUFFLE (assignment):** correctly assigned representations beat within-stratum
  shuffled representations; **confirmed equivalence-to-shuffle** kills all
  construction-specific content claims at this scope (§4.8 row 2), while a merely
  indeterminate shuffle contrast blocks confirmatory advancement without killing
  (Rev4/R4e discipline).
- **H-HUMAN (cost realism):** neither drafter nor graph reduces blinded expert review time
  or the lifecycle-cost composite (LCC, §4.8) relative to the human-from-evidence arm E
  at matched fidelity.

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
   held-out source, reported separately and feeding no decision. This gives the
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
  passes its arm-level safety gate**; within it, a record that breaches a hard gate
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
  (H−T, A2-IR−T, A2−T, A1−T) are atomic members of node E2 and are covered by
  E2's ONE simultaneous confidence set (§4.6/R5a), so the four-zone decision
  read for the hierarchy-selected arm is valid **whatever the hierarchy
  selects**; no outcome-disjoint calibration split is needed and none is
  claimed. [STIPULATED — PROPOSED-PREREG-ROW-99A-R5b]
- **Secondary:** host balanced accuracy (Stage 2), per-concept macro-BA over the 3/3/3
  claims — explicitly a *consumer/compression* measurement, entangled with host
  comprehension, rendering, and truncation, and never a substitute for the primary.
- **Scoring is evaluator-run, never constructor-self-scored**; the denotational scorer is
  a deterministic program, self-tested exhaustively (gate 2).

Primary contrasts — every one an enumerated member of the §4.6 confirmatory family
(Rev4 restored A2−A1 and A1−A0/H-REVIEW to the family; Rev5 enumerates the family
ATOMICALLY — ten nodes, 95 atomic nulls, §4.6/R5a): H vs A2-IR
(explicit-materialisation/closure increment), A2-IR vs A2 (machine-readable-input
increment), A2 vs A1 (citation increment), A1 vs A0 (review increment, H-REVIEW),
best-constructed vs T (deflation, dominant — decided on the R4a UCT statistic), T′ vs
the winner's native formats (format, Stage 2 only), each vs its shuffle, and E vs the
best machine arm (cost realism).

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
  interval at its node's final procedure-assigned level (Rev5/R5a), never a fixed
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
  **Rev5 (R5a): every four-zone label is read from ONE two-sided confidence set
  at the deciding node's FINAL procedure-assigned level** (for E2, the one
  simultaneous four-contrast set) — the zone decision and the reported interval
  are the same object at the same confidence, which removes the Rev4 mismatch
  between operative 95% bounds and far-smaller graphical local levels
  ("matching confidence" is now automatic, not aspirational).
  (PROPOSED-PREREG-ROW-99A-R3d, amended by R4a/R4b, completed by R5a)
- **Confirmatory testing family — ATOMIC strong-FWER control (Rev4 skeleton
  completed in Rev5, re-review residual 1; this specification supersedes the R4b
  weight scheme):** the Rev4 procedure was a valid skeleton with two defects the
  re-review proved: E1–E8 were treated as elementary when they are composite
  (E1 held seven contrasts, E2/E3 several four-zone claims, E7 fidelity + cost,
  E8 multiple formats), and **every downstream node held positive initial alpha,
  so an indeterminate E1 did not mathematically block E2–E8** despite the stated
  gatekeeping intent. Rev5 replaces it with a fully enumerated closed procedure.

  **(1) Atomic null enumeration — 95 atomic one-sided nulls in ten nodes**
  (every directional and equivalence component, every arm-level safety gate,
  both H-HUMAN endpoint components, both format contrasts, every candidate-vs-T
  contrast, and the A0 canon-readiness components; every node's margins obey
  δ_node ≥ m_node per R4b; "gate(X)" is the arm-level safety-gate null
  H₀: gate-pass rate of arm X ≤ π₀ with π₀ pinned pre-freeze — its rejection
  CONFIRMS the arm clears its §4.5 safety gate):

  | Node (claim) | Atomic one-sided nulls | Within-node closed procedure | Release condition |
  |---|---|---|---|
  | **E1** — H-SHUFFLE validity (Stage 1) | for each arm a ∈ {A1, A2, A2-IR, B, H, T}, on Δ_a = a − S(a): sup (Δ_a ≤ +δ_S), inf (Δ_a ≥ −δ_S), eqL (Δ_a ≤ −m_S), eqU (Δ_a ≥ +m_S) — **24 nulls** | Holm over the six arms; per arm ONE two-sided CI at the Holm-assigned level reads the four-zone label (confirmed equivalence fires precedence row 2) | superiority confirmed for ALL six arms |
  | **E2** — H-TEXT-SOURCE (dominant) | for each candidate c ∈ {H, A2-IR, A2, A1}, the 4 zone nulls on Δ_c = c − T (natural-stratum UCT paired macro-BA) — **16 nulls** | ONE simultaneous confidence set over all four contrasts at the node level (pinned conservative default: Bonferroni split; a sharper joint method is a freeze-time pin); the DECISION is the zone of the §4.6-hierarchy-selected contrast, read from this same set — valid under any selection (R5b) | any non-indeterminate zone confirmed for the selected contrast |
  | **E3** — H-GRAPH | gate(H), gate(A2-IR) + 4 zone nulls on H − A2-IR (δ = +0.08, m = 0.05) — **6 nulls** | fixed sequence at the full node level: both gate nulls (intersection-union), then ONE CI four-zone | any zone other than indeterminate confirmed |
  | **E4** — input channel | gate(A2-IR), gate(A2) + 4 zone nulls on A2-IR − A2 — **6 nulls** | same as E3 | same |
  | **E5** — citation increment | gate(A2), gate(A1) + 4 zone nulls on A2 − A1 — **6 nulls** | same as E3 | same |
  | **E6** — review increment (H-REVIEW) | gate(A1), gate(A0) + 4 zone nulls on A1 − A0 — **6 nulls** | same as E3 (if a gate null fails to reject, the zone nulls stay untested and the contrast reports descriptively via the Level-1 gate-pass-rate difference, R4c) | same |
  | **E7** — H-HUMAN (cost realism) | gate(E); for each machine candidate c ∈ {H, A2-IR, A2, A1}: gate(c), fidelity eqL/eqU on E − c, cost null LCC_E − LCC_c ≥ 0 — **17 nulls** | fixed sequence: gate(E), then one simultaneous set over the four candidate blocks (Bonferroni default); per candidate the conjunctive claim is intersection-union over its four nulls; the DECISION is read for the hierarchy-selected candidate (fallback A1) — the E2 selective-inference device extended here, because E7's comparator is also outcome-selected (an enumeration-surfaced gap, fixed the same way) | the selected candidate's full conjunction rejects |
  | **E9** — A0 canon-readiness | gate(A0) + 4 zone nulls on A0 − S(A0) (δ = +0.05 ≥ m_S0, pinned) + precision null (unsupported-constraint precision ≤ 0.95) — **6 nulls** | fixed sequence: gate(A0), then ONE CI four-zone plus the precision null by intersection-union; advancement = gate + superiority + precision all rejected; kill only on confirmed equivalence (§4.8/R5d) | advancement conjunction rejects, or equivalence confirmed |
  | **E1b** — T′ shuffle validity (Stage 2) | 4 zone nulls on T′ − S(T′) — **4 nulls** | ONE CI four-zone | superiority confirmed |
  | **E8** — H-TEXT-FORMAT (Stage 2) | for each pinned native format f ∈ {AST rendering, vector-derived rendering}: eqL/eqU on T′ − f — **4 nulls**; the SINGLE pinned endpoint is Stage-2 host three-label macro-BA (consumer cost and format handling are descriptive only — this closes the "multiple formats/endpoints" ambiguity) | intersection-union over all four TOST nulls; T′ renders the SHIPPING record, so E8's estimand is post-selection **by definition** and needs no selection adjustment | all four reject |

  **(2) Initial weights and COMPLETE transition matrix** (all entries not shown
  are zero; entries are fractions of the releasing node's weight; fraction
  *values* are proposed and re-justifiable pre-freeze — the *structure* is NOT
  deferrable: all initial mass on E1, E1 → E2 the only edge out of E1, no edge
  bypassing E2). Initial weight vector: **w₀ = (E1: 1.00; all other nodes:
  0.00)** — gatekeeping is now mathematical: an unresolved E1 leaves every other
  node at local level zero, and an unresolved E2 leaves every downstream node at
  level zero, matching precedence rows 2 and 4. E1 gates the deflation claim too,
  deliberately: a family whose real-vs-shuffled contrasts are unresolved has not
  shown that ANY arm's artifact carries concept-specific signal, and §3.1's
  conditional-adoption default (the text store governs while construction is
  unearned) already covers that world without a confirmatory deflation claim.

  | From \ To | E2 | E3 | E4 | E5 | E6 | E7 | E9 | E1b | E8 |
  |---|---|---|---|---|---|---|---|---|---|
  | E1 | 1.00 | — | — | — | — | — | — | — | — |
  | E2 | — | 0.55 | 0.15 | 0.10 | 0.05 | 0.10 | 0.05 | — | — |
  | E3 | — | — | 1.00 | — | — | — | — | — | — |
  | E4 | — | — | — | 1.00 | — | — | — | — | — |
  | E5 | — | — | — | — | 0.50 | 0.50 | — | — | — |
  | E6 | — | — | — | — | — | 0.50 | 0.50 | — | — |
  | E7 | — | — | — | — | — | — | — | 1.00 | — |
  | E9 | — | — | — | — | — | — | — | 1.00 | — |
  | E1b | — | — | — | — | — | — | — | — | 1.00 |
  | E8 | — | 1.00 | — | — | — | — | — | — | — |

  **(3) Update algorithm (pinned):** total two-sided α = .05. Repeat: for every
  node j with current weight w(j) > 0, run its registered within-node closed
  procedure at local level w(j)·α; when a node's release condition newly fires,
  add w(j)·G(j,k) to every node k, set w(j) ← 0, and re-route edges through
  exhausted nodes by the standard graphical update rule; iterate until no new
  release fires. Weight reaching an already-released node re-propagates along
  its outgoing edges (so the E8 → E3 back-recycle is idle when E3 is resolved);
  weight reaching a node whose nulls can no longer be tested — a
  Stage-2-conditional node (E1b, E8) when Stage 2 never runs — **strands
  harmlessly**: conditioning is one-way and returns no alpha, so conditional
  execution cannot inflate error. Alpha moves ONLY on rejection of an atomic
  null at its procedure-assigned level, never on a "definitive classification".
  A node whose final weight is zero, or whose contrast lands indeterminate, is
  reported **descriptively only**, and nothing downstream regains confirmatory
  status from it; any node may instead be pre-declared exploratory at freeze,
  but a claim outside the pinned graph can never be reported as confirmatory.

  **(4) One confidence set per node:** every four-zone label is read from ONE
  two-sided confidence set at the node's FINAL procedure-assigned level (E2 and
  E7: the one simultaneous multi-candidate set), so the zone decision and the
  reported interval are the same object at the same confidence — equivalence =
  both TOST nulls rejected, superiority/inferiority = the corresponding
  δ-shifted null rejected, exactly as read off that set.

  **(5) Procedure-adjusted operative bounds:** every operative advancement,
  kill, or adoption threshold in this document that formerly read "95%
  confidence bound" — the §4.1/§4.6/§4.8 H-GRAPH bounds, the E9 A0
  canon-readiness bounds, every four-zone CI, every arm-level safety gate — is
  the bound at the relevant node's FINAL procedure-assigned level, never a
  fixed 95%. Exactly two families keep pinned standalone levels, both OUTSIDE
  the confirmatory family by construction: **§4.7 instrument gates** (failure
  yields `INSTRUMENT-INVALID`, never a confirmatory claim in either direction)
  and the **§4.6 selection-hierarchy rung bars** (SELECTION-ONLY devices: their
  level affects which arm is selected, never the validity of the E2/E7
  decisions, which the simultaneous candidate sets cover for every candidate).

  **(6) Sequential interaction:** the Stage-1 sequential boundary is
  **binding-futility-only with respect to confirmatory rejections** — no atomic
  null is rejected before its registered final analysis; early stopping
  (including the §7 Rung-0 rule) can only prevent rejections, so it is
  conservative for FWER, and its power cost is modelled exactly in the mandated
  simulation below. Early "superiority" stopping affects resource allocation
  only, never an early confirmatory rejection.

  **(7) Mandated simulation (freeze-blocking):** the freeze record must contain
  a simulation of THIS exact implementation — all 95 atomic nulls, the
  within-node procedures, the transition matrix, the binding-futility
  boundaries, and the Rung-0 rule — demonstrating (i) **strong FWER ≤ .05
  across a pinned grid of null configurations** (all nulls true; each single
  node's nulls false with the rest true; the full adoption-path configuration;
  and a pinned set of mixed configurations), and (ii) **adoption-path power**
  per the power bullet below. The Rev2 "T and/or T′" disjunction stays
  abolished — T (source) and T′ (format) are separate nodes with separate
  roles (§4.1); Holm correction remains for the fixed secondary family only
  and never licenses multiple primary/dominant claims.
  (PROPOSED-PREREG-ROW-99A-R3d, replaced by R4b, completed by R5a)
- **Decision thresholds:** advance H-GRAPH only if the H−A2-IR lower confidence bound
  **at node E3's final procedure-assigned level (Rev5/R5a)** exceeds +0.08 on the
  primary composite (the H−A2 total effect is reported only as
  its decomposition, §4.1); **advance ≠ kill** — killing requires a confirmed
  equivalence/inferiority zone or a fired futility boundary, never mere lack of
  superiority (§4.8, Rev4/R4e). The composite comparison is reached only through
  the R4c Level-1 hurdle (§4.5), whose arm-level safety gates are themselves
  enumerated atomic nulls inside each node (R5a). All gate thresholds that were
  bare points in the original (N ≤0.40; T−shuffled-T ≥0.20) become
  **pre-registered one-sided confidence-bound tests** (e.g. upper bound of N's BA
  below the leakage bound; lower bound of the T−S(T) difference above the
  sensitivity bound) — these are §4.7 INSTRUMENT gates at their own pinned
  standalone one-sided levels, explicitly OUTSIDE the confirmatory family
  (R5a item 5): their failure yields `INSTRUMENT-INVALID`, never a confirmatory
  claim.
- **Power (under the exact final analysis — Rev2 Finding 1a, rebuilt in Rev3 per
  cross-vendor MAJOR-5):** simulate before freeze from calibration data **under the
  exact final analysis model** — the crossed mixed-effects hierarchy above, the
  pre-registered sequential futility/superiority boundary, the winner-selection
  hierarchy, **and the full multiplicity procedure — in Rev5 the EXACT R5a atomic
  implementation (95 enumerated nulls, within-node closed procedures, the
  published transition matrix, binding-futility boundaries including the §7
  Rung-0 rule), reporting BOTH the strong-FWER grid and adoption-path power
  (R5a item 7)** — never under simplified concept-only resampling.
  Requirements: ≥90%
  power for the +0.08 superiority effect; **≥90% power for every registered
  equivalence test at its registered margin, stated at a specified true effect —
  normally zero** (the dominant H-TEXT-SOURCE contrast first — now on the R4a UCT
  statistic: an equivalence margin
  generically demands more information than a superiority margin at matched error
  rates, so the dominant hypothesis must never be the only unpowered one); and a
  simulated **joint power for the full adoption path** (probability that every family
  member on the adoption path reaches its definitive zone under the R4b procedure),
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
  structure not). **Rev5 (R5a item 5 / R5b): the rung bars are SELECTION-ONLY
  devices at a pinned selection level (one-sided 95%), explicitly
  non-confirmatory** — the hierarchy chooses the comparison arm but confirms
  nothing; the validity of the E2 (and E7) decisions under this outcome-dependent
  selection is secured by their ONE simultaneous confidence set over ALL
  candidates, which covers whichever arm the hierarchy selects.
  **Fallback:** if no arm clears any bar, best-arm := A1; T′ renders
  A1's endorsed records for the format contrast; and the **T-source deflation
  contrast still runs against A1** (it never depended on a constructed winner —
  Rev3 CRITICAL-2), so H-TEXT-SOURCE cannot silently vanish exactly when
  construction is weakest, the case where deflation is most likely true.
  Simultaneous confidence intervals reported; never selected post hoc on the same
  outcomes. (PROPOSED-PREREG-ROW-99A-R2i, completed by R5a/R5b)

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
    concept under two arms, that claim generators never labeled, and that gold
    labelers never saw the held-out source or any arm artifact. Any breach →
    `INSTRUMENT-INVALID` for the affected natural-UCT cells.
    [STIPULATED — PROPOSED-PREREG-ROW-99A-R5b]

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

Kill/selection rules (revised to the new endpoint and arms):

- **H-GRAPH three-outcome rule (Rev4, re-review residual 5 — replaces "kill H-GRAPH
  if H fails to beat A2-IR", which contradicted precedence row 9):** **ADVANCE**
  H-GRAPH only if H beats A2-IR by the primary rule; **KILL** H-GRAPH only under a
  confirmed four-zone **equivalence or inferiority** of H−A2-IR (the CI at node
  E3's procedure-assigned level — Rev5/R5a — wholly inside ±0.05, or its upper
  bound < −0.08) or a fired pre-registered **futility** boundary;
  an **indeterminate** H−A2-IR outcome neither advances nor kills (precedence
  row 9) — the hypothesis stands unadvanced. Lack of demonstrated superiority
  blocks advancement; it is never itself a kill. Retain citation-constrained
  drafting if A2 beats A1.
- **Unreviewed-drafting canon-readiness (same advance/kill/indeterminate discipline
  — Rev4/R4e; wording completed in Rev5, re-review residual 4):** A0 **advances
  toward canon-ready** only if its E9 advancement conjunction holds (§4.6/R5a):
  A0 beats its shuffle at margin +0.05, its unsupported-constraint precision
  lower bound is ≥ 0.95 (both bounds at E9's procedure-assigned level), AND its
  arm-level safety gate passes; it is **killed as canon-ready** only on confirmed
  equivalence-to-shuffle or a fired pre-registered futility boundary. **A
  breached hard gate (§4.5 arm-level safety-gate failure) is a CANNOT-ADVANCE
  outcome, never a registered kill** — Rev5 takes the re-review's
  cannot-advance branch, replacing the Rev4 wording that listed a hard-gate
  breach as a kill event, so the R4e taxonomy (kills only via confirmed
  equivalence/inferiority or futility) holds without exception; any other
  outcome is indeterminate-not-advanced. `ModelAuthored` candidate role survives
  in every case.
- **Retain direct compilation** if A2-IR/A2/A1 and H are equivalent under the four-zone
  rule within ±0.05 and the direct arm has lower measured LCC.
- **Deflate to text** iff the **T-source four-zone decision** (§4.6) is **text
  superior**, or **equivalent** with lower LCC (uncertainty-bounded and
  robustness-stable). **T′ can never trigger deflation** — it is a format probe whose
  Stage-1 fidelity is true by construction (Rev3, cross-vendor CRITICAL-2).
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
- **Human-cost verdict:** if E matches machine-arm fidelity within ±0.05 at lower LCC,
  neither drafter nor graph has earned its complexity for this sector.

**Precedence matrix (pre-registered; resolves every previously-unhandled ambiguous
outcome):** ordered highest-precedence first — a higher row's verdict dominates any
lower row's.

| Pr. | Outcome pattern | Verdict |
|---|---|---|
| 1 | Any gate of §4.7 fails | `INSTRUMENT-INVALID` — no substantive claim in either direction |
| 2 | Structured arms ≈ their shuffles | Representations carry no concept-specific evidence at this scope; all construction claims die |
| 3 | **T-source four-zone decision = text superior, OR equivalent with lower LCC (robustness-stable)** | **Text deflation. Dominates every constructed-arm victory — explicitly including "H beats A2-IR but T ≈ winner and lower LCC". T′ can never fire this row (format probe only — Rev3 CRITICAL-2)** |
| 4 | **T-source decision in the indeterminate zone, or deflation LCC `COST-INDETERMINATE`** (above all constructed-arm rows — Rev2 Finding 1b, re-anchored Rev3) | **Constructed-arm ADOPTION BLOCKED.** No deflation claim; fidelity contrasts are reported as findings only; no constructed arm is adopted; the single preregistered escalation (§4.6) is triggered with the T-contrast's power as its primary target; if still indeterminate after escalation, adoption stays withheld. An unheard text control never reroutes to "constructed-arm verdicts stand" |
| 5 | E matches machines within ±0.05, lower LCC | Human-from-evidence baseline verdict; machine construction unearned for this sector |
| 6 | H beats A2-IR by primary rule AND LCC non-dominated | H-GRAPH supported **and adoptable as an oracle-IR upper-bound mechanism result** (scoped to tested sectors, packet-local per §3.2; production graph-import additionally requires the realistic text→IR extraction test per R3a; reachable only below rows 3–4, i.e. the text control spoke and did not win) |
| 7 | H beats A2-IR semantically but is dominated on LCC | Split verdict: fidelity supported, adoption unearned; graph stays hypothesis pending cost reduction |
| 8 | Graph reduces error but increases review time | Split verdict per pre-pinned fidelity-vs-review-cost trade rule (pinned pre-freeze from calibration) |
| 9 | H−A2-IR lower CI ≤ +0.08 AND the ±0.05 equivalence zone is not reached (four-zone indeterminate) | **Indeterminate — reported as indeterminate**; no adoption, no kill; one preregistered escalation (§4.6) or verdict stands as indeterminate |
| 10 | Nonce and natural strata disagree | Primary (nonce) verdict stands **scoped to evidence-compilation** — **for constructed-arm contrasts only; the T-source decision is governed by its R4a natural-stratum UCT statistic, and the nonce parse-back/UCT upper bounds can never override it (Rev4)**; natural-stratum disagreement is a pre-registered generalisation failure, blocking any natural-language scope claim |
| 11 | Effects reverse across concept types or reviewers | Heterogeneity verdict: report per-stratum with interaction CI; no pooled adoption claim |

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

Every literature citation in this document is **supporting-only**. No load-bearing claim,
gate, margin, or verdict rests solely on an unverified citation; all rest on [MEASURED]
repository results plus [STIPULATED] design choices. Specifically:

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
   coverage over all four routes** at pinned level 1 − α₀ (Bonferroni α₀/4 as
   the pinned conservative default; any sharper joint method is a freeze-time
   pin; the α₀ value is a named freeze-time pin, the simultaneity structure is
   not deferrable). **Branch termination is permitted ONLY when U(r) < f for
   EVERY route r**, where f is the pinned futility threshold — the smallest
   screen-scale effect of interest, pinned pre-freeze; "maximum credible" is
   thereby a mathematical stopping bound, not a judgment call.
   **Sequential-error accounting (Rev5):** Rung-0 futility looks occur only at
   the pinned interim points of the registered sequential plan and are
   **binding-futility-only** — a Rung-0 stop can only terminate, never confirm,
   so it cannot inflate the §4.6 confirmatory FWER (it is conservative for
   Type I error); its entire cost is branch-loss risk, which the R5a mandated
   simulation models exactly (boundary, looks, α₀, f) so the freeze record
   quantifies it in the adoption-path power.
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
   R4d, formalised by R5c]
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

## 8. PROPOSED prereg rows (labels only — nothing registered)

All rows are PROPOSED only — nothing is registered, frozen, or scheduled by this document;
**no `ASM-<number>` ids are minted** (ids are assigned at prereg-freeze). Labels are
`99A`-prefixed to stay disjoint from the sibling revisions (THR-, GU-, VL-, H-PS rows).

### §8.0 Consolidated controlling table (established in Rev4, re-review residual 6; extended — not restructured — in Rev5) `[STIPULATED — PROPOSED-PREREG-ROW-99A-R4f]`

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
| R4a | AMENDED by R5b | UCT made executable: nine natural claims per sense at exactly 3/3/3 by generation-to-quota with a pinned missing-class fallback; generator/labeler role separation; consumer assignment/carryover/rendering/truncation/format-competence pins; comparator inference via E2's simultaneous candidate set |
| R4b | COMPLETED by R5a | atomic enumeration (95 nulls, ten nodes incl. E9 and E1b); ALL initial alpha on E1; complete transition matrix + update algorithm published; one confidence set per node at its final procedure-assigned level; every operative 95% threshold procedure-adjusted; strong-FWER grid + adoption-path power simulation mandated in the freeze record |
| R4c, R4f | OPERATIVE as written (R4f extended by this table's Rev5 rows) | — |
| R4d | FORMALISED by R5c | simultaneous one-sided upper prediction bounds U(r) on (unreviewed-r − T) + Δ_rev(r) over all four reviewed routes; termination only when every U(r) < f; binding-futility-only sequential accounting; pilot human cost credited; unboundable-increment prohibition retained |
| R4e | COMPLETED by R5d | a breached hard gate is a cannot-advance outcome, never a registered kill; §3.2 reads "fails to advance or is killed" |
| R5a–R5d | NEW (Rev5 rows below) | — |

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
  kill; §3.2's "fails" disambiguated]:** advance/kill/indeterminate law —
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

- **PROPOSED-PREREG-ROW-99A-R5a (residual 1, MAJOR):** atomic-FWER law — the
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
- **PROPOSED-PREREG-ROW-99A-R5b (residual 2, MAJOR):** UCT-executability law —
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
- **PROPOSED-PREREG-ROW-99A-R5c (residual 3, MAJOR):** rung-0-futility-bound law
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
the Rev4 zone-geometry constraint δ ≥ m (R4b)**; the R5a transition-matrix fraction
*values* and simultaneous-set critical constants (superseding "the R4b local alpha
weights"; the R5a *structure* — all initial mass on E1, E1 → E2 the sole exit edge,
no edge bypassing E2, the within-node closed procedures — is NOT deferrable) and the
UCT artifact/consumer budget values (structure and matched-budget rule not
deferrable); the R5b per-concept candidate cap (proposed 30), reserve-list contents,
near-duplicate similarity bound, and consumer-competence bound values (the
generation-to-quota structure, role separation, and fallback definition not
deferrable); the R5c α₀, futility threshold f, and interim-look schedule values
(the simultaneous-prediction-bound structure and the binding-futility-only rule not
deferrable); the E1/E9 shuffle-contrast margin values (m_S, δ_S, m_S0 — subject to
δ ≥ m) and the arm-level safety-gate bound π₀; the
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
advance/kill/indeterminate discipline, §8.0 consolidation), and every Rev5
structural repair (the atomic null enumeration with all-alpha-on-E1 gatekeeping
and one-confidence-set-per-node, procedure-adjusted operative bounds, the
generation-to-quota natural gold with generator/labeler separation, simultaneous
candidate-set comparator inference, the U(r) < f Rung-0 stopping bound with
binding-futility-only accounting and pilot cost crediting, and the
cannot-advance hard-gate taxonomy).

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

## Mandatory self-check — Revision 2 (historical record, retained verbatim; superseded by the Revision 5 self-check below)

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

## Mandatory self-check — Revision 3 (historical record, retained verbatim; superseded by the Revision 5 self-check below)

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

## Mandatory self-check — Revision 4 (historical record, retained verbatim; superseded by the Revision 5 self-check below)

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

## Mandatory self-check — Revision 5 (final section)

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
