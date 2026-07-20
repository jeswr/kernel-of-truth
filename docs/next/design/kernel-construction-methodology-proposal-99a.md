# Kernel construction methodology — proposal 99a, REVISION 1

> **REVISED PROPOSAL — NOT A MAINTAINER SUBMISSION AND NOT A PREREG FREEZE.
> NEXT = Fable independent critique → source-verify [SV] the load-bearing lit → THEN maintainer.**
>
> Revision 1 produced 2026-07-20 (Fable), applying the independent GPT-5.6 soundness review
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
> rows are PROPOSED only, labelled `PROPOSED-PREREG-ROW-99A-R1a…j`; **no `ASM-<number>` ids
> are minted** (ids are assigned at prereg-freeze; sibling Phase-1 revisions use the same
> convention). Review packaging note, acknowledged: the review file `last-message.json` is
> Markdown content in a `.json` wrapper — cosmetic only.

Tag discipline (applies to every load-bearing claim below):

- **[MEASURED]** — directly checked in this repository (result files cited inline).
- **[LIT-BACKED]** — rests on external literature; every such tag here also carries `[SV]`
  (source-verification pending) and is **supporting-only, never load-bearing** (§5 / fix 5).
- **[STIPULATED]** — a design or policy choice. Every design choice in this document is
  [STIPULATED], never [MEASURED].
- **[EXTRAPOLATION]** — direction-only; never used as a premise for any conclusion or gate.

---

# Methodology proposal: build the canon from evidence, not from a model

This is a revised draft for Fable's independent critique, not a final ruling and not a
recommendation packet for the maintainer.

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
  p≈0.58. Dictionary structure did **not** independently ratify NSM primes. [MEASURED:
  `reports/lit-primitives-grounding-priorart.md` §6]
- E8 found kernel–SAE correspondence for GPT-2↔Pythia-160M (primary ρ=.386, partial ρ=.360,
  both permutation p=.0001) but the two SmolLM2-involving pairs did not replicate. One
  positive pair, not a model-independent canonical geometry (hook-site mismatch is a real
  confound). [MEASURED: `poc/e8/results-incoming/20260707-131303-modal/verdict-e8.md`,
  `poc/e8/results-incoming/20260707-143903-ext1-modal/results-e8-ext1.json`]
- **K-NULL is directly load-bearing for §3:** kernel and aligned plain-dictionary stores
  were equivalent within the registered margin; the concise plain store was nominally more
  accurate and used ~0.565× the verifier-side FLOPs. The tested mechanism consumed aligned
  answer strings, not vectors or explication structure. [MEASURED:
  `docs/next/analysis/knull-ufo-dual-model-reconcile-fable.md`]

These results do not say "the kernel is useless." They say determinism, source provenance,
graph convergence, and model alignment are **four different properties** and must not
masquerade as semantic grounding. [STIPULATED — interpretation of the [MEASURED] rows above]

## 1. Canonicality and grounding criteria (operationalised)

### 1.1 Three properties, three distinct tests `[STIPULATED — review-1 fix 2; PROPOSED-PREREG-ROW-99A-R1b]`

The original draft conflated three notions. They are separated here, each with its own
operational test; a record can hold any subset, and the record's status field must say
which:

1. **Canonical** — *selected as the normative record by a declared authority and
   procedure.* Operational test: given (authority A, profile P, version t, sense s), a
   public, pinned selection procedure returns exactly one record, and re-running the
   procedure on the pinned inputs returns the same record identity (per the softened
   reproducibility rule, §1.3). Canonicality is a **governance fact**; it makes no claim
   about truth. A legal or institutional definition can be fully canonical when "true" is
   not even the appropriate test.
2. **Evidence-adequate** — *faithful to specified independent evidence.* Operational test:
   every semantic clause of the record cites resolvable evidence anchors; an
   evaluator-run (never constructor-self-scored) audit finds no unsupported clause, no
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
5. **Model-as-reviewer conditions:** a model may endorse only under (1)'s cross-family and
   evidence-blind conditions, and a model endorsement can never be the sole endorsement
   for promotion above `ModelAuthored`. [STIPULATED]

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
| **(d) Principled hybrid (governance architecture)** | Multiple pinned human sources plus at least one operational, observational, institutional, formal, or usage anchor; an LLM compiles; independent endorsement (§1.2) decides. Whether a *graph constraint* belongs in the loop is the §3 hypothesis. | Canonical relative to a named authority/profile/version. Deterministic stages byte-reproducible; stochastic stages captured-reproducible + measured-stable (§1.3 crit. 4); disagreements become explicit forks or revisions, never hidden averaging. | More expensive per promoted record because review is real. Scale comes from tiering: unreviewed bulk stays `AxiomsOnly`/`ModelAuthored`; only reviewed records enter the canon. | Best of the four: source holdout, graph perturbation, nonce concepts, counterexamples, reviewer agreement, text nulls, shuffles, held-out-model validation attack different links. | Consensus can launder shared source bias; governance can become slow or political; review cost may erase any compression benefit — and **plain pinned text may dominate the whole construction on K-NULL evidence** (§3). | **Adopted as the governance architecture** (evidence-anchored + independently endorsed). The graph-constrained variant is **not recommended — it is hypothesis H-GRAPH (§3), to be tested against the citation-only and plain-text controls.** |

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

### 3.1 What is adopted (as a proposal for critique, not a registration)

Adopt **an evidence-anchored, independently endorsed governance architecture**:

1. **Declare the unit.** Records per sense; profile, domain, language, authority, and
   intended verification scope fixed first.
2. **Assemble an evidence packet.** Multiple independently pinned sources where available,
   plus at least one non-constructor anchor appropriate to the sector; record source
   conflicts instead of silently synthesising them.
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
- **K-NULL strengthens that objection with repository data:** plain aligned text was
  equivalent within the registered margin, nominally more accurate, at ~0.565× verifier
  FLOPs [MEASURED]. A plain-text-equivalent-cheaper control therefore plausibly dominates
  the graph-constrained construction on the graph's *own* efficiency-and-adequacy terms.
- KBUILD-0 as originally designed could not even isolate the graph: H differed from A1 by
  the graph AND clause-level citation discipline AND changed prompting/abstention, so any
  H−A1 advantage was confounded (review §2). The decisive ablation is citation-only
  without a graph (§4, arm A2).

**Therefore:** the defensible wording is — *preferred governance architecture (§3.1);
graph constraint a pre-registered empirical hypothesis*:

> **H-GRAPH [PROPOSED-PREREG-ROW-99A-R1d, hypothesis — NOT a recommendation]:** relative
> to citation-constrained direct-drafter construction (arm A2) under the identical
> endorsement protocol, adding the deterministic sense-graph constraint (arm H) improves
> exact construction fidelity (primary endpoint, §4.5) or reduces semantic error or
> blinded-review cost, by the pre-registered margins — **tested against, and subordinate
> to, the K-NULL-style plain-text controls (arms T and T′): if the plain-text control is
> equivalent to the best constructed arm and cheaper end-to-end, text deflation dominates
> any graph result** (precedence matrix, §4.8).

Direction-of-travel note: if H-GRAPH fails but citation discipline alone (A2 vs A1) shows
the benefit, the programme keeps citation-constrained drafting and drops graph
construction entirely. [EXTRAPOLATION — direction-only, decides nothing]

## 4. KBUILD-0 (revised): cheap, decisive construction experiment

Test construction methodology before another scale build. Two-stage, cheapest-first
(review §5): **Stage 1 scores typed records directly against exact hidden rules with no
host model at all**; the host/compression evaluation runs only if Stage 1 earns it.

### 4.1 Hypotheses

- **H-GRAPH (primary; demoted-to-hypothesis form, §3.2):** graph-constrained H beats
  citation-only A2 on exact construction fidelity by the pre-registered margin
  (lower 95% confidence bound of the paired per-concept difference > +0.08 on the
  fidelity composite).
- **H-REVIEW:** matched independent review (A1 vs A0) improves fidelity — isolates the
  gate's value independent of any graph.
- **H-TEXT (deflation, dominant):** the best constructed arm under the pre-registered
  hierarchy (§4.6) is TOST-equivalent to the content-matched plain rendering T′ and/or
  hash-pinned source text T within ±0.03 while costing more end-to-end. If supported,
  adopt the text store for this scope — this outcome **dominates** all constructed-arm
  contrasts (§4.8).
- **H-SHUFFLE (assignment):** correctly assigned representations beat within-stratum
  shuffled representations; failure kills all construction-specific content claims at
  this scope.
- **H-HUMAN (cost realism):** neither drafter nor graph reduces blinded expert review time
  or lifecycle cost relative to the human-from-evidence arm E at matched fidelity.

All margins are [STIPULATED] smallest-effects-of-interest, to be justified against
calibration data before any freeze; nothing here is frozen.

### 4.2 Evaluation set

Two preregistered strata (role-separated authors, reviewers, host operators, auditors):

1. **Primary: 96 post-registration nonce senses.** Finite micro-worlds with exact hidden
   truth conditions built from existing representable predicates, relations, negation,
   scope, and molecule references; random nonce labels assigned after generation.
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
   is scored, not excused.

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
  evidence graph. Same endorsement protocol as A1/H. **H vs A2 is the only contrast that
  isolates the graph** (review §2).
- **B — dictionary graph only:** deterministic sense graph; source-supported signed
  relations under a frozen rule; frozen closure/fixpoint; rendered without generative
  semantic additions.
- **H — graph-constrained hybrid:** B's evidence graph → drafter compilation with
  clause-level evidence pointers → the matched endorsement protocol.
- **E — human/expert-from-evidence (new):** blinded human experts author the typed record
  from the identical packet under the same time budget. Since endorsement may dominate
  cost, the study must test whether the drafter or the graph actually reduces expert
  work; E also anchors the achievable-fidelity ceiling and lifecycle-cost comparison.
- **T — source-text null:** hash-pinned source definitions retrieved directly; no graph,
  AST, vector, or generated explication.
- **T′ — content-matched plain rendering (new):** a deterministic plain-prose rendering of
  the *same endorsed record* produced by the winning constructed arm, separating semantic
  content from schema/format — the T-vs-H confound fix (review §3).
- **S — shuffled controls:** independent permutation of the concept↔representation mapping
  for A1, A2, B, H, T, T′ within sense-type and token-length strata; bytes, token
  budgets, format unchanged.
- **N — no-context control:** claim only.

Method (c) remains excluded as a construction arm (a target model's internals cannot
independently define post-registration nonce concepts); SAE alignment runs descriptively
after construction, per §3.1 step 6.

### 4.4 Stage sequencing and consumer `[STIPULATED — review-1 fix 4]`

- **Stage 1 (primary, no host):** score every arm's typed records directly against the
  exact hidden rules (§4.5). Co-primary observables: construction fidelity, lifecycle
  cost, blinded-review metrics (agreement with CI, edit distance, review minutes,
  adjudication rate). A **pre-registered sequential futility/superiority boundary**
  allows stopping arms early.
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

### 4.5 Primary endpoint: exact construction fidelity `[STIPULATED — review-1 fix 4; PROPOSED-PREREG-ROW-99A-R1g]`

The generator knows the exact finite truth conditions and every arm emits a typed record —
so the primary endpoint compares **each record's denotation directly with the hidden
rule**, exhaustively over the finite micro-world where possible:

- **Primary composite (per concept):** exact denotational equivalence (record extension =
  rule extension over the enumerated micro-world), with pre-registered component metrics:
  unsupported-constraint rate, omission rate, boundary-error rate, and calibrated
  abstention score (credit for abstaining exactly where the packet underdetermines —
  see gate 1). The composite weighting is pinned pre-freeze and justified from
  calibration.
- **Secondary:** host balanced accuracy (Stage 2), per-concept macro-BA over the 3/3/3
  claims — explicitly a *consumer/compression* measurement, entangled with host
  comprehension, rendering, and truncation, and never a substitute for the primary.
- **Scoring is evaluator-run, never constructor-self-scored**; the denotational scorer is
  a deterministic program, self-tested exhaustively (gate 2).

Primary contrasts, in the fixed hierarchy of §4.6: H vs A2 (graph increment), A2 vs A1
(citation increment), A1 vs A0 (review increment), best-constructed vs T′/T (deflation),
each vs its shuffle, and E vs the best machine arm (cost realism).

### 4.6 Statistics `[STIPULATED — review-1 fix 4; PROPOSED-PREREG-ROW-99A-R1h]`

- **Unit:** concept (resampling and permutation at concept level); paired contrasts.
- **Exchangeability:** sign-flip permutation validity is secured by design — randomised
  arm-material assignment where applicable and **randomised reviewer assignment**;
  reviewers are crossed and blinded, and **no reviewer sees competing records for the
  same concept**.
- **Analysis:** 10,000 paired sign permutations, two-sided α=.05, BCa 95% CI and effect
  size; Holm correction across the fixed secondary family; equivalence claims by TOST
  only, never by non-significance.
- **Decision thresholds:** advance H-GRAPH only if the H−A2 lower confidence bound
  exceeds +0.08 on the primary composite. All gate thresholds that were bare points in
  the original (N ≤0.40; T−shuffled-T ≥0.20) become **pre-registered one-sided 95%
  confidence-bound tests** (e.g. upper bound of N's BA below the leakage bound; lower
  bound of the T−S(T) difference above the sensitivity bound).
- **Power:** simulate before freeze from calibration data; ≥90% power for the +0.08
  effect; the simulation must include **model-seed, renderer, reviewer, and discrete
  within-concept measurement variance** — not concept variance alone. One preregistered
  escalation to a maximum of 160 nonce concepts; if 90% power is unreachable at the
  maximum, the experiment is `INSTRUMENT-INVALID`, not run-and-hope.
- **Generality over the pipeline, not one draw:** multiple author seeds/model snapshots
  per arm (count pinned pre-freeze); conclusions attach to the pinned pipeline
  *distribution* per §1.3 criterion 4, not to a single stochastic draw.
- **Selection-bias fix:** "best constructed arm" for H-TEXT is determined by a **fixed
  pre-registered comparison hierarchy** (H → A2 → A1, first that clears its own
  superiority bar; simultaneous confidence intervals reported), never selected post hoc
  on the same outcomes.

### 4.7 Instrument gates `[STIPULATED — review-1 fix 4; PROPOSED-PREREG-ROW-99A-R1f]`

Failure of any gate yields `INSTRUMENT-INVALID`, not a substantive null:

1. **PACKET-IDENTIFIABILITY gate (new; decisive):** every scored label must be logically
   determined by the published packet alone. A deterministic checker verifies, per claim,
   that the packet's rendered evidence entails/contradicts/underdetermines the claim
   **as the gold label says** — with `UNDERDETERMINED` defined **relative to what the
   packet supports, not what the concealed rule says**. Claims failing the check are
   regenerated before freeze; a post-freeze failure invalidates the instrument. Without
   this gate a model can earn credit by guessing the hidden generator from prior/template
   cues.
2. **Gold gate:** the micro-world engine passes exhaustive rule/claim self-tests; a
   blinded 10% paraphrase audit reaches ≥95% correct interpretation.
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
8. **Independence gate (rewritten):** no LLM supplies **gold labels or endorsement
   decisions**; the Stage-2 host supplies predictions only (that is its role, not a
   breach); drafter model, host model, and auditing model are from pairwise different
   families; reviewer independence per §1.2.
9. **Reviewer-reliability gate (new):** chance-corrected reviewer agreement on
   calibration records must clear a pinned bound with its CI, else the endorsement
   instrument — not the constructions — is invalid.
10. **Access/prereg-integrity gate (new):** any breach of preregistration or access
    controls (constructor or reviewer exposure to gold, rule hashes, or competing
    records) → `INSTRUMENT-INVALID`.

### 4.8 Kill rules, ambiguity handling, and precedence matrix `[STIPULATED — review-1 fix 4; PROPOSED-PREREG-ROW-99A-R1i]`

Kill/selection rules (revised to the new endpoint and arms):

- **Kill H-GRAPH** if H fails to beat A2 by the primary rule; retain citation-constrained
  drafting if A2 beats A1.
- **Kill unreviewed drafting as canon-ready** if A0 fails to beat its shuffle by lower
  confidence bound +0.05, or if its unsupported-constraint precision has a 95% lower
  bound below 0.95; `ModelAuthored` candidate role survives.
- **Retain direct compilation** if A2/A1 and H are TOST-equivalent within ±0.05 and the
  direct arm has lower measured lifecycle cost.
- **Deflate to text** if T′ (first) or T is TOST-equivalent to the hierarchy winner
  within ±0.03 and cheaper in authoring, tokens, FLOPs, and maintenance.
- **Kill all construction-specific content claims at this scope** if correctly assigned
  structured arms are equivalent to their shuffles.
- **Efficiency verdict is separate** and passes only under the end-to-end Pareto rule of
  §1.3 criterion 8.
- **Human-cost verdict:** if E matches machine-arm fidelity within ±0.05 at lower
  lifecycle cost, neither drafter nor graph has earned its complexity for this sector.

**Precedence matrix (pre-registered; resolves every previously-unhandled ambiguous
outcome):** ordered highest-precedence first — a higher row's verdict dominates any
lower row's.

| Pr. | Outcome pattern | Verdict |
|---|---|---|
| 1 | Any gate of §4.7 fails | `INSTRUMENT-INVALID` — no substantive claim in either direction |
| 2 | Structured arms ≈ their shuffles | Representations carry no concept-specific evidence at this scope; all construction claims die |
| 3 | **T′/T TOST-equivalent to hierarchy winner and cheaper** | **Text deflation. Dominates every constructed-arm victory — explicitly including "H beats A2 but T′ ≈ H and cheaper"** |
| 4 | E matches machines within ±0.05, cheaper lifecycle | Human-from-evidence baseline verdict; machine construction unearned for this sector |
| 5 | H beats A2 by primary rule AND lifecycle cost non-dominated | H-GRAPH supported (scoped to tested sectors) |
| 6 | H beats A2 semantically but is dominated on lifecycle cost | Split verdict: fidelity supported, adoption unearned; graph stays hypothesis pending cost reduction |
| 7 | Graph reduces error but increases review time | Split verdict per pre-pinned fidelity-vs-review-cost trade rule (pinned pre-freeze from calibration) |
| 8 | H−A2 lower CI ≤ +0.08 AND ±0.05 TOST also fails | **Indeterminate — reported as indeterminate**; no adoption, no kill; one preregistered escalation (§4.6) or verdict stands as indeterminate |
| 9 | T/T′ equivalence inconclusive | No deflation claim; efficiency verdict withheld; constructed-arm verdicts stand scoped |
| 10 | Nonce and natural strata disagree | Primary (nonce) verdict stands **scoped to evidence-compilation**; natural-stratum disagreement is a pre-registered generalisation failure, blocking any natural-language scope claim |
| 11 | Effects reverse across concept types or reviewers | Heterogeneity verdict: report per-stratum with interaction CI; no pooled adoption claim |

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

The `[SV]` verifications are queued for the literature-researcher **after** Fable's
independent critique (see NEXT banner); until verified they cannot be promoted to
load-bearing use.

## 6. Honest uncertainty map

- **Settled by repository measurement [MEASURED]:** representation determinism ≠ semantic
  correctness (encoder); dictionary Core membership does not enrich NSM primes over a
  frequency-matched null; plain aligned text matched the kernel store at ~0.565× verifier
  FLOPs in K-NULL's tested mechanism; E8 has one positive cross-model pair and two
  non-replications; Framework-G legal yield was 13/50.
- **Settled by literature (pending [SV], supporting-only):** dictionary grounding-kernel
  non-uniqueness; FCA conditional uniqueness; SAE instability reports.
- **Open empirical (this is what KBUILD-0 buys):** H-GRAPH (graph increment over citation
  discipline); H-REVIEW (value of the gate); H-TEXT (text deflation at this scope);
  H-HUMAN (whether machine construction reduces expert cost); transfer from nonce
  compilation to natural senses; sector generalisation beyond formal/lexical.
- **Philosophical (not decidable by any experiment here, and not claimed):** whether any
  symbol-anchored record is "grounded" in the strong referential sense; whether
  convention-constituted concepts need grounding at all (§1.1 separates these so the
  empirical programme does not pretend to answer them).

## 7. Sequenced experimental programme (cheapest-most-decision-relevant first)

Each rung: question / method / pass-fail / cost / decision-unblocked. Rungs are
[STIPULATED] proposals; none is registered.

1. **Rung 1 — KBUILD-0 Stage 1 (construction fidelity, no host).** Q: does graph or
   citation discipline or review improve exact record fidelity over the pinned drafter,
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

- **PROPOSED-PREREG-ROW-99A-R1a:** independent-endorsement law — an endorsement counts
  for promotion only under §1.2's five recorded conditions (role independence incl.
  cross-family/evidence-blind model reviewers; competence/COI; pre-fixed sampling,
  number, threshold, uncertainty; fork/abstain/appeal/authority-ruling disagreement
  handling; model-endorsement never sole). [STIPULATED]
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
- **PROPOSED-PREREG-ROW-99A-R1g:** primary-endpoint law — exact construction fidelity
  (denotational comparison against the hidden rule, evaluator-scored, with
  unsupported/omission/boundary/abstention components) is PRIMARY; host balanced
  accuracy is secondary and conditional (Stage 2). [STIPULATED]
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

## Revision 1 — review fixes applied

Itemisation against the five review fixes (authoritative fix text:
`poc/gpt56-review/99a-proposal-review/last-message.json`):

1. **Keep the sound semantic-record-first reframing — ADOPTED.** The frame is retained
   verbatim in intent (§ "Bottom line", §1.3 definition, §3.1); the review's confirmation
   that it matches the implemented encoder architecture is recorded in §0b.
2. **Operationalise the criteria — ADOPTED.** Independent endorsement operationalised
   with five recorded conditions (§1.2, 99A-R1a); canonical vs evidence-adequate vs
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

## Mandatory self-check (final section)

1. **All 5 fixes addressed?** YES — itemised in "Revision 1" above with section anchors:
   (1) Bottom line/§1.3/§3.1; (2) §1.1/§1.2/§1.3-crit-4; (3) §3.2 + §2 rewording;
   (4) §4.2–§4.8; (5) §5.
2. **Graph-constraint DEMOTED to a hypothesis tested against the K-NULL cheaper-plain-text
   control?** YES — H-GRAPH (§3.2, 99A-R1d); tested via H-vs-A2; subordinate to arms
   T/T′ under precedence row 3, which explicitly dominates an H-beats-A2 victory; the
   [MEASURED] K-NULL 0.565×-FLOPs result is cited as the motivating evidence.
3. **Canonical / evidence-adequate / grounded separated with distinct operational
   tests?** YES — §1.1 gives one test per property (public selection procedure;
   evaluator-audited clause-evidence faithfulness; non-constructor operational/
   observational contact) plus the no-cross-evidencing rule (99A-R1b).
4. **KBUILD-0 has citation-only-no-graph ablation + construction-fidelity PRIMARY + fixed
   stats + precedence matrix?** YES — arm A2 (§4.3); §4.5 primary endpoint
   (denotational, evaluator-scored); §4.6 repaired statistics (3/3/3, CI-bound gates,
   power components, seeds, crossed reviewers, fixed hierarchy); §4.8 eleven-row
   precedence matrix covering every ambiguous outcome the review listed.
5. **Every load-bearing claim tagged?** YES — [MEASURED] for repository results (with
   file citations), [STIPULATED] for every design choice/criterion/gate/margin,
   [LIT-BACKED][SV] supporting-only for literature, [EXTRAPOLATION] used once (§3.2
   direction note) and marked direction-only, never a premise.
6. **No [MEASURED] on a choice?** YES — checked: every [MEASURED] tag anchors a
   repository result file; all criteria, arms, gates, margins, laws, and rungs carry
   [STIPULATED].
7. **No @handle/account strings?** YES — models and roles are referred to by
   model/pipeline names (Sol/GPT-5.6, largekern-10k, Haiku Framework-G) and role names
   only; no @-handles or account identifiers appear.
8. **No `ASM-<number>` minted?** YES — only `PROPOSED-PREREG-ROW-99A-R1a…j` labels; §8
   states ids are assigned at prereg-freeze; sibling rows referenced by their PROPOSED
   labels only.
9. **Nothing committed / registered / frozen?** YES — this is an in-place edit of the
   design document only; no git operations, no registry writes, no prereg-freeze, no
   runs launched; the top banner marks it NOT a maintainer submission and NOT a prereg
   freeze, with the required NEXT sequence (Fable independent critique →
   source-verify [SV] → THEN maintainer).
