# Kernel construction methodology — proposal 99a, REVISION 3

> **REVISED DRAFT — NOT A MAINTAINER SUBMISSION AND NOT A PREREG FREEZE.
> NEXT = re-review of the Rev3 experimental design → maintainer (decision on #59).
> Adoption of anything beyond a governance-architecture pilot requires that re-review
> AND the maintainer decision; nothing is registered, frozen, scheduled, or committed
> by this revision.**
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
> `PROPOSED-PREREG-ROW-99A-R2a…m` (Rev2, one per critique finding), and
> `PROPOSED-PREREG-ROW-99A-R3a…i` (Rev3, one per cross-vendor finding); **no
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

This is a revised draft applying the cross-vendor review of Rev2 — next stage a
re-review of the revised experimental design, then the maintainer decision on #59. It
is not a final ruling and not yet a maintainer submission.

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
   **decision/provenance hash**; the **semantic identity** (semantic-content hash) is
   altered **only when the selected normative content changes**. A new source or
   endorsement that leaves the selected normative content unchanged changes the
   decision/evidence-release identity, never the concept.
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
> the text store is equivalent-or-superior to the best constructed arm under the §4.6
> four-zone rule and lower on the lifecycle-cost composite (LCC, §4.8), text
> deflation dominates any graph result; if the text contrast lands in the
> indeterminate zone, constructed-arm adoption is blocked** (precedence matrix, §4.8,
> rows 3–4).

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
lossless machine-readable input, does graph topology/closure add anything" — it is
**never** evidence about production graph-import performance, which would additionally
require a realistic, error-prone text→IR extraction test (out of scope for KBUILD-0 and
listed as a binding extrapolation cap in §6). [STIPULATED — PROPOSED-PREREG-ROW-99A-R3a]

Direction-of-travel note (rescoped in Rev2 per critique Finding 5c): if H-GRAPH fails but
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
  packet-relative construction fidelity by the pre-registered margin (lower 95%
  confidence bound of the paired per-concept difference > +0.08 on the fidelity
  composite). **H vs A2-IR is the only graph-isolating contrast**; the Rev2 contrast
  H vs A2 confounded the graph with an oracle-quality parse/normalisation channel and
  survives only as the decomposition (H−A2) = (H−A2-IR) + (A2-IR−A2). The whole
  B/H/A2-IR family is an oracle-IR **upper-bound mechanism test** (§3.2); no
  production graph-import claim follows from it. (PROPOSED-PREREG-ROW-99A-R3a)
- **H-REVIEW:** matched independent review (A1 vs A0) improves fidelity — isolates the
  gate's value independent of any graph.
- **H-TEXT-SOURCE (deflation, dominant — Rev3, cross-vendor CRITICAL-2 split):** the
  **independently governed plain-text store** (arm T, §4.3 — governed by the same
  endorsement machinery but never passing through structured-record construction, and
  never depending on any constructed arm's output) is, under the §4.6 **four-zone
  rule** on the **common estimand** — the three-valued packet-relative
  claim/denotation task of §4.5, scored by the same deterministic procedure for every
  arm — **text-superior, or equivalent at lower LCC** (matching §4.8 row 3: the
  superior zone fires regardless of LCC). This is the **only**
  hypothesis that can license "structured-record construction can be avoided".
  **Because it is the dominant hypothesis it is powered like one (Rev2, critique
  Finding 1a — retained):** the §4.6 power rule requires ≥90% power at its
  registered margin (true effect zero), under the same `INSTRUMENT-INVALID`
  consequence as the superiority contrast; and an **indeterminate-zone** T-source
  outcome **blocks constructed-arm adoption** (§4.8 row 4). If supported, adopt the
  text store for this scope — this outcome **dominates** all constructed-arm
  contrasts (§4.8). (PROPOSED-PREREG-ROW-99A-R3b)
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
  shuffled representations; failure kills all construction-specific content claims at
  this scope.
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
   **separate renderer families**, §4.7 gate 5); positive/negative/boundary exemplars;
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
2. **Confirmatory: 48 natural, ambiguity-rich senses.** Two pinned build sources to
   constructors; gold claims from an independent held-out source plus two blinded human
   annotators and adjudication. Tests transfer to ordinary lexical material; cannot rescue
   a failed primary.
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
  isolates the lossless machine-readable-input channel; **H − A2-IR isolates graph
  topology/closure**; A2-IR − A2 measures the input-channel increment on its own.
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
  with the oracle-IR label on B/H/A2-IR**; the **decision-grade T-source comparison**
  therefore rests on (i) the natural stratum's independent claim task plus
  evidence-adequacy review and (ii) the Stage-2 common consumer at pinned token
  budgets. T is charged only its own governance costs in the LCC, never any
  structured-construction cost. (PROPOSED-PREREG-ROW-99A-R3b)
- **T′ — content-matched plain rendering (format probe ONLY — Rev3, cross-vendor
  CRITICAL-2):** a deterministic plain-prose rendering of the *same endorsed record*
  produced by the winning constructed arm, separating semantic content from
  schema/format (review-1 §3). T′ serves **H-TEXT-FORMAT only**: its Stage-1 fidelity
  is largely true by construction, it presupposes the record was already constructed
  and endorsed, and it is charged **all shared upstream construction/review costs** in
  the LCC. A T′ fidelity equivalence is never deflation evidence — that is T's job.
- **S — shuffled controls:** independent permutation of the concept↔representation mapping
  for A1, A2, A2-IR, B, H, T, T′ within sense-type and token-length strata; bytes, token
  budgets, format unchanged.
- **N — no-context control:** claim only.

Method (c) remains excluded as a construction arm (a target model's internals cannot
independently define post-registration nonce concepts); SAE alignment runs descriptively
after construction, per §3.1 step 6.

### 4.4 Stage sequencing and consumer `[STIPULATED — review-1 fix 4]`

- **Stage 1 (primary, no host):** score every arm directly against the three-valued
  packet-relative target of §4.5 (exact hidden rules only on fully-identifying
  packets — Rev3, cross-vendor CRITICAL-3). Co-primary observables: construction fidelity, the
  lifecycle-cost composite (LCC, §4.8), blinded-review metrics (agreement with CI, edit
  distance, review minutes, adjudication rate). A **pre-registered sequential
  futility/superiority boundary** allows stopping arms early. Stage 1 is itself entered
  via the machine-only Rung 0 screen (§7 — Rev2, critique Finding 12), which can kill
  the branch before the human endorsement apparatus is stood up.
- **Stage 2 (secondary, conditional):** the host/text-compression evaluation runs **only
  if** Stage 1 shows the relevant constructed arm has incremental semantic fidelity or
  review-cost benefit. Host: smallest model from a preregistered local ladder passing the
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
- **Primary composite (per concept) — NON-COMPENSATORY (Rev3, cross-vendor MAJOR-6):**
  pre-registered component metrics remain unsupported-content rate,
  contradicted-content rate, omission rate, boundary-error rate, and abstention
  miscalibration — but the composite ranks only among records that first pass **hard
  minimum gates** on unsupported, contradicted, omitted, and abstention-miscalibrated
  content (each bound pinned pre-freeze; a breach fails the record outright — no
  fatal unsupported assertion can be compensated by excellence elsewhere). Component
  weights are **frozen from externally justified grounds and calibration data
  disjoint from outcome data, before any outcome unblinding**, and component-wise
  sensitivity of every verdict is reported. (PROPOSED-PREREG-ROW-99A-R3f)
- **Common estimand across ALL arms (Rev3, cross-vendor CRITICAL-2):** every arm —
  constructed, human, and text — is scored against the same three-valued
  packet-relative target by the same deterministic procedure: typed records by direct
  denotation; text arms via the gate-1 deterministic parse-back (with the
  nonce-stratum oracle-parse upper-bound caveat stated at arm T, §4.3). **No arm has
  a private endpoint**, which is what gives the dominant T-source contrast a common
  estimand.
- **Secondary:** host balanced accuracy (Stage 2), per-concept macro-BA over the 3/3/3
  claims — explicitly a *consumer/compression* measurement, entangled with host
  comprehension, rendering, and truncation, and never a substitute for the primary.
- **Scoring is evaluator-run, never constructor-self-scored**; the denotational scorer is
  a deterministic program, self-tested exhaustively (gate 2).

Primary contrasts, in the fixed ordered family of §4.6: H vs A2-IR (graph increment),
A2-IR vs A2 (machine-readable-input increment), A2 vs A1 (citation increment), A1 vs A0
(review increment), best-constructed vs T (deflation, dominant), T′ vs the winner's
native formats (format, Stage 2 only), each vs its shuffle, and E vs the best machine
arm (cost realism).

### 4.6 Statistics `[STIPULATED — review-1 fix 4; PROPOSED-PREREG-ROW-99A-R1h]`

- **Unit:** concept (resampling and permutation at concept level); paired contrasts.
- **Exchangeability:** sign-flip permutation validity is secured by design — randomised
  arm-material assignment where applicable and **randomised reviewer assignment**;
  reviewers are crossed and blinded, and **no reviewer sees competing records for the
  same concept**.
- **Analysis (crossed hierarchy — Rev3, cross-vendor MAJOR-5):** the primary inference
  model matches the design's actual crossed hierarchy: **concept and
  author-seed/model-snapshot as crossed random factors** (multiple seeds per arm),
  **reviewer as a random factor** on every review-based endpoint; **renderer families
  and the pinned host are declared FIXED levels, and every claim is narrowed
  accordingly** ("under the pinned renderer families and snapshots") — never
  generalised over unsampled levels. Concept-only resampling is abolished as the sole
  inference; 10,000 paired sign permutations at concept level are retained as a
  supplementary robustness check. Two-sided α=.05, BCa 95% CI and effect size
  reported throughout; equivalence claims by the four-zone rule below, never by
  non-significance. (PROPOSED-PREREG-ROW-99A-R3e)
- **Four-zone decision rule for the text contrast (replaces TOST-only — Rev3,
  cross-vendor MAJOR-4):** for the constructed-minus-text fidelity difference with
  registered equivalence margin ±m and superiority threshold δ (both pinned
  pre-freeze from substantive interchangeability grounds): CI wholly inside ±m →
  **equivalent**; lower bound > +δ → **constructed superior**; upper bound < −δ →
  **text superior**; otherwise → **indeterminate, and constructed-arm adoption is
  blocked** (§4.8 row 4). Failure of an equivalence test is never read as
  non-equivalence, and never as constructed superiority.
  (PROPOSED-PREREG-ROW-99A-R3d)
- **Confirmatory testing family (ordered, with alpha allocation — Rev3, cross-vendor
  MAJOR-4):** the confirmatory claims form one **fixed-sequence gatekeeping family**,
  tested in this pre-registered order, each at full α=.05 only while every earlier
  member has reached a definitive (non-indeterminate) zone: (1) H-SHUFFLE validity
  contrasts (preconditions); (2) H-TEXT-SOURCE four-zone decision (dominant);
  (3) H-GRAPH (H − A2-IR); (4) the A2-IR − A2 input-channel contrast; (5) H-HUMAN;
  (6) H-TEXT-FORMAT (Stage 2). The moment a member lands indeterminate, all later
  members lose confirmatory status and are reported descriptively only. The Rev2
  "T and/or T′" disjunction is abolished — T (source) and T′ (format) are separate
  family members with separate roles (§4.1). Holm correction remains for the fixed
  secondary family only and never licenses multiple primary/dominant claims.
  (PROPOSED-PREREG-ROW-99A-R3d)
- **Decision thresholds:** advance H-GRAPH only if the H−A2-IR lower confidence bound
  exceeds +0.08 on the primary composite (the H−A2 total effect is reported only as
  its decomposition, §4.1). All gate thresholds that were bare points in
  the original (N ≤0.40; T−shuffled-T ≥0.20) become **pre-registered one-sided 95%
  confidence-bound tests** (e.g. upper bound of N's BA below the leakage bound; lower
  bound of the T−S(T) difference above the sensitivity bound).
- **Power (under the exact final analysis — Rev2 Finding 1a, rebuilt in Rev3 per
  cross-vendor MAJOR-5):** simulate before freeze from calibration data **under the
  exact final analysis model** — the crossed mixed-effects hierarchy above, the
  pre-registered sequential futility/superiority boundary, and the winner-selection
  hierarchy — never under simplified concept-only resampling. Requirements: ≥90%
  power for the +0.08 superiority effect; **≥90% power for every registered
  equivalence test at its registered margin, stated at a specified true effect —
  normally zero** (the dominant H-TEXT-SOURCE contrast first: an equivalence margin
  generically demands more information than a superiority margin at matched error
  rates, so the dominant hypothesis must never be the only unpowered one); and a
  simulated **joint power for the full adoption path** (probability that every family
  member on the adoption path reaches its definitive zone), reported in the freeze
  record. One preregistered escalation to a maximum of 160 nonce concepts.
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
  re-anchored in Rev3 per cross-vendor CRITICAL-1):** "best constructed arm" for the
  text contrasts is determined by a **fixed pre-registered comparison hierarchy**
  with each rung's bar and comparator defined: H clears iff the H−A2-IR lower 95%
  confidence bound exceeds +0.08 (the primary rule); otherwise A2-IR clears iff the
  A2-IR−A2 lower bound exceeds its pinned input-channel margin; otherwise A2 clears
  iff the A2−A1 lower bound exceeds its pinned citation-increment margin; otherwise
  A1 clears iff the A1−A0 lower bound exceeds its pinned review-increment margin
  (all increment margins pinned pre-freeze from calibration — values deferrable,
  structure not). **Fallback:** if no arm clears any bar, best-arm := A1; T′ renders
  A1's endorsed records for the format contrast; and the **T-source deflation
  contrast still runs against A1** (it never depended on a constructed winner —
  Rev3 CRITICAL-2), so H-TEXT-SOURCE cannot silently vanish exactly when
  construction is weakest, the case where deflation is most likely true.
  Simultaneous confidence intervals reported; never selected post hoc on the same
  outcomes. (PROPOSED-PREREG-ROW-99A-R2i)

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

- **Kill H-GRAPH** if H fails to beat A2-IR by the primary rule (Rev3, cross-vendor
  CRITICAL-1); retain citation-constrained drafting if A2 beats A1.
- **Kill unreviewed drafting as canon-ready** if A0 fails to beat its shuffle by lower
  confidence bound +0.05, or if its unsupported-constraint precision has a 95% lower
  bound below 0.95; `ModelAuthored` candidate role survives.
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
| 10 | Nonce and natural strata disagree | Primary (nonce) verdict stands **scoped to evidence-compilation**; natural-stratum disagreement is a pre-registered generalisation failure, blocking any natural-language scope claim |
| 11 | Effects reverse across concept types or reviewers | Heterogeneity verdict: report per-stratum with interaction CI; no pooled adoption claim |

Row ordering is load-bearing (Rev2): the inconclusive-text row sat at position 9 in
Rev1, *below* the constructed-arm verdict rows, so an underpowered text control let "H
beats A2" advance via row 5 — the exact back-door the demotion was supposed to close. It
now sits at position 4, above every constructed-arm verdict. [STIPULATED —
PROPOSED-PREREG-ROW-99A-R2a]

Cost: deterministic preprocessing, a few hundred drafter calls, a bounded human review and
human-authoring exercise, and — only if Stage 2 triggers — under a GPU-day of small-model
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
- **Open empirical (this is what KBUILD-0 buys):** H-GRAPH (graph topology/closure
  increment over the flat-IR control, oracle-IR upper bound); the A2-IR−A2
  machine-readable-input increment; H-REVIEW (value of the gate); H-TEXT-SOURCE (text
  deflation at this scope) and H-TEXT-FORMAT (shipping format); H-HUMAN (whether
  machine construction reduces expert cost); transfer from nonce compilation to
  natural senses; sector generalisation beyond formal/lexical.
- **Binding extrapolation caps (Rev3 — the cross-vendor review's residual-risk list,
  each cap load-bearing and enforced in the named section):** oracle-IR graph
  performance is never production graph-import performance (§3.2/R3a); unreviewed
  Rung-0 results never terminate the reviewed route without the conditional-futility
  rule (§7/R3h); the one-revision-cycle cost is never full lifecycle evidence
  (§4.8/R3f); nonce compilation results never extend to natural concepts or
  dictionary-scale convergence beyond the confirmatory stratum (§4.2/R2e).
  [STIPULATED]
- **Philosophical (not decidable by any experiment here, and not claimed):** whether any
  symbol-anchored record is "grounded" in the strong referential sense; whether
  convention-constituted concepts need grounding at all (§1.1 separates these so the
  empirical programme does not pretend to answer them).

## 7. Sequenced experimental programme (cheapest-most-decision-relevant first)

Each rung: question / method / pass-fail / cost / decision-unblocked. Rungs are
[STIPULATED] proposals; none is registered.

0. **Rung 0 — machine-only screen (new — Rev2, critique Finding 12).** Q: do the two
   cheapest potential branch-killers fire before any human apparatus exists?
   "Cheapest-first" must count the human machinery, not GPU cost only. M: arms A0,
   unreviewed-A2 (A2 minus endorsement), B, T, S, N — evaluator-scored against the exact
   rules; no reviewers, no endorsement protocol, no arm E; pre-registered sequential
   futility boundary. P/F (scope-limited — Rev3, cross-vendor MAJOR-8): preliminary
   forms of precedence rows 2 (structured ≈ shuffles) and 3 (text-deflation signal),
   evaluated on **unreviewed routes only**. Rung 0 can kill *unreviewed* routes
   outright (A0 and unreviewed-A2 as canon candidates), but it can **never by itself
   kill the reviewed methodology** — H-REVIEW explicitly hypothesises that review
   changes fidelity, so extrapolating unreviewed futility to the reviewed route is
   invalid. Killing the whole branch from Rung 0 additionally requires a
   **conservative conditional-futility calculation**: take the maximum credible
   review increment Δ_rev from an **independent review-calibration pilot** (Δ_rev
   pinned before Rung-0 unblinding), and kill the branch only if
   best-unreviewed-arm + Δ_rev still lands inside the futility region; otherwise the
   mandated next step is a **small reviewed pilot**, not termination. Rung 0 can
   never support adoption (its arms are unreviewed). Cost: drafter calls +
   deterministic evaluation only; no humans, no GPU. Unblocks: standing up the
   endorsement apparatus (reviewer calibration, crossed review, arm E training) only if
   the branch survives.
   [STIPULATED — PROPOSED-PREREG-ROW-99A-R2l, scope-limited by R3h]
1. **Rung 1 — KBUILD-0 Stage 1 (construction fidelity, no host; entered only via
   Rung 0).** Q: does graph or
   citation discipline or review improve packet-relative record fidelity over the pinned drafter,
   and does anything beat text/human baselines? M: §4.3 arms, §4.5 primary, §4.7 gates,
   §4.8 matrix, sequential boundary. P/F: §4.8. Cost: drafter calls + bounded human
   exercise, no GPU. Unblocks: the construction-substrate choice (drafter-only vs
   citation-constrained vs graph vs text vs human) for the next kernel build.
2. **Rung 2 — KBUILD-0 Stage 2 (host/compression), conditional on Rung 1.** Q: do
   fidelity gains survive a small independent consumer at fixed token budgets? M: §4.4.
   P/F: §4.6 thresholds + gates 5–6. Cost: <1 GPU-day. Unblocks: the contextual-
   compression claim scoped to the chosen substrate.
3. **Rung 3 — natural-sense confirmatory stratum readout.** Q: does the nonce result
   transfer to ambiguity-rich natural senses? M: §4.2 stratum 2. P/F: precedence row 10.
   Cost: annotation + adjudication only. Unblocks: any natural-language scope wording.
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

- **PROPOSED-PREREG-ROW-99A-R1a (amended in Rev2):** independent-endorsement law — an
  endorsement counts for promotion only under §1.2's six recorded conditions (role
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
- **PROPOSED-PREREG-ROW-99A-R1d:** graph-demotion law — the graph constraint is
  hypothesis H-GRAPH, tested via the H-vs-A2 citation-only ablation and subordinate to
  the plain-text controls per the §4.8 precedence matrix; it may not be written as a
  recommendation anywhere upstream of a passing KBUILD-0. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R1e:** arm-completeness law — KBUILD-0 must include A2
  (citation-only, no graph), E (human-from-evidence), and T′ (content-matched plain
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
- **PROPOSED-PREREG-ROW-99A-R2b:** human-floor endorsement law (Finding 2) — promotion
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
- **PROPOSED-PREREG-ROW-99A-R2l:** machine-first law (Finding 12) — Rung 0 (machine-only
  arms, evaluator-scored, sequential futility boundary) precedes standing up the
  endorsement apparatus; Rung 0 can kill the branch but can never support adoption.
  [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R2m:** property-test-enforcement law (Finding 13) — every
  promotion/status assertion carries a machine-checkable `property-test-cited` field;
  a registry lint flags any status change citing a test that does not match the
  property claimed. [STIPULATED]

Rev3 rows (one per cross-vendor finding, referenced by the review's own numbering —
CRITICAL-1…3, MAJOR-4…8, MINOR-9):

- **PROPOSED-PREREG-ROW-99A-R3a (CRITICAL-1):** graph-isolation law — the
  graph-isolating contrast is H vs the flat-IR control A2-IR (same atoms/relations in
  non-graph form; matched raw evidence, prompt, token/compute budget, endorsement
  protocol, and reviewer visibility); H vs A2 is reported only as the decomposition
  (H−A2-IR) + (A2-IR−A2); the oracle-IR B/H/A2-IR family is an explicitly labelled
  upper-bound mechanism test and licenses no production graph-import claim without a
  realistic text→IR extraction test. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R3b (CRITICAL-2):** text-estimand law — the deflation
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
- **PROPOSED-PREREG-ROW-99A-R3d (MAJOR-4):** zone-and-family law — the text contrast
  is decided by the pre-registered four-zone CI rule (equivalent /
  constructed-superior / text-superior / indeterminate-blocks-adoption); the
  confirmatory claims form one fixed-sequence gatekeeping family with declared alpha
  allocation (shuffle → T-source → H-GRAPH → input-channel → H-HUMAN → T-format);
  equivalence-test failure is never read as non-equivalence or superiority.
  [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R3e (MAJOR-5):** analysis-fidelity law — inference uses
  the crossed concept × author-seed/snapshot × (reviewer) hierarchy with
  renderer/host as narrowed fixed levels; power is simulated under the exact final
  analysis model including the sequential boundary and winner hierarchy; equivalence
  power is stated at a specified true effect (normally zero); joint adoption-path
  power is reported; an equivalence margin may never be widened to reach power — the
  remedies are design change or `INSTRUMENT-INVALID` termination. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R3f (MAJOR-6):** non-compensatory-composite law — hard
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
- **PROPOSED-PREREG-ROW-99A-R3h (MAJOR-8):** rung-0-scope law — Rung 0 kills
  unreviewed routes only; branch termination additionally requires the conservative
  conditional-futility rule using the pinned maximum credible review increment from
  an independent pilot; otherwise the mandated next step is a small reviewed pilot,
  not termination. [STIPULATED]
- **PROPOSED-PREREG-ROW-99A-R3i (MINOR-9):** identity-separation law — every
  selection-input change alters the decision/provenance hash; semantic identity is
  altered only when the selected normative content changes. [STIPULATED]

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
arguments, never from power feasibility (Rev3, cross-vendor MAJOR-5)**; the
fidelity-composite *weighting values* and LCC *weight/price values* — **now frozen from
externally justified, outcome-disjoint grounds before unblinding, inside the
non-compensatory-gates + declared-prices + robustness-sweep structure (Rev3, MAJOR-6)**;
the row-8 fidelity-vs-review-cost trade rule; arm-E *recruitment logistics*; the Rung-0
Δ_rev value (pinned from the independent review-calibration pilot before Rung-0
unblinding). NOT deferred (structural): the per-equivalence-test power requirement, the
row-4 adoption block, the LCC structure, the arm-E calibration counter-measure, and
every Rev3 structural repair (A2-IR arm, three-valued target, T-source/T-format split,
four-zone rule, ordered family, crossed-hierarchy analysis, hard minimum gates,
two-human floor + anchoring protection, Rung-0 scope limit).

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

## Mandatory self-check — Revision 2 (historical record, retained verbatim; superseded by the Revision 3 self-check below)

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

## Mandatory self-check — Revision 3 (final section)

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
