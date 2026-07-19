# Kernel construction methodology — GPT-5.6 PROPOSAL (bead 99a)

> **STATUS: REVIEWED (NEEDS-FIX) GPT-5.6 PROPOSAL — NOT ADOPTED, NOT YET maintainer-ready.** Produced
> 2026-07-19 via the overflow-Fable lane (Fable capped). Review-gate lens completed 2026-07-19
> (`poc/gpt56-review/99a-proposal-review/last-message.json`): verdict **NEEDS-FIX — send to Fable as a
> draft, NOT to the maintainer as the recommended path**. The "semantic-record-first; vector-derived"
> reframing is SOUND and should be retained. MINIMUM FIXES before it is maintainer-ready: (1) operationalise
> "independent endorsement" (independence from constructor/sources/host/gold/beneficiary; competence/COI;
> sampling/threshold/uncertainty; disagreement handling); separate canonical vs evidence-adequate vs
> empirically-grounded; soften criterion-4 reproducibility (stochastic LLMs → captured-output+stability, not
> byte-identical). (2) DEMOTE the graph constraint from recommendation to a pre-registered HYPOTHESIS (its own
> strongest objection dominates; K-NULL shows plain text equivalent/cheaper). (3) KBUILD-0: add a
> citation-only-no-graph arm (the decisive graph ablation) + a human/expert-from-evidence arm; add a
> PACKET-IDENTIFIABILITY gate + template/lexical-leakage audits; make EXACT construction-fidelity (record
> denotation vs the hidden rule) PRIMARY and host-BA secondary; fix the statistical thresholds (8-balanced-
> across-3-labels impossible; N/T point-thresholds need CIs; coverage conflates evaluator vs constructor
> failure; independence-gate wording; selection bias) + a preregistered precedence/ambiguity matrix. The three
> `[SV]` lit claims are correctly NON-load-bearing (illustrative). NEXT: revise (Fable when back, or a
> deliberate overflow cycle) → Fable adversarial critique → literature-researcher verifies [SV] → THEN
> maintainer. Do NOT treat as ratified. Source proposal: poc/gpt56-review/99a-kernel-methodology/.

---

# Methodology proposal: build the canon from evidence, not from a model

This is a proposal for the coordinator’s review gate and later Fable critique, not a final ruling. The bead database could not open under the read-only sandbox, so this uses the supplied bead brief and checked-in programme materials.

Bottom line: choose a specific hybrid, but change what is called “canonical.” The canonical object should be an independently endorsed, evidence-anchored semantic record. The deterministic vector should be a derived encoding of that record. Haiku should propose or compile records, dictionary graphs should constrain and audit them, and model internals should validate or bridge them—not decide their meaning.

Tag convention below:

- `[MEASURED-REPO]` means directly checked in this repository.
- Literature statements carry `[established][SV]`, `[claimed][SV]`, or `[speculative][SV]`. `SV` means a literature researcher must verify the primary source before load-bearing use.

## Repository evidence that should change the starting prior

- The current encoder already makes the right architectural separation: a typed explication is deterministically encoded by a pinned, training-free TPR/VSA construction; the vector is reproducible and decodable only given the kernel lexicon. This establishes representation determinism, not semantic correctness. [MEASURED-REPO: [architecture.md](/home/ec2-user/css/kernel/kernel-of-truth/docs/architecture.md), [encoder README](/home/ec2-user/css/kernel/kernel-of-truth/encoder/README.md)]

- The current Haiku pipeline is more defensible than “the LLM simply invents meanings”: it receives pinned Wiktionary/Wikipedia text, emits a candidate, receives mechanical gate errors once, and preserves provenance. Crucially, its schema already labels the result `ModelAuthored`, below endorsed `Explicated` or `Molecule`. That is the correct status. Stage 1 produced 13 legal records from 50 concepts, a 26% concept yield; its semantic-fidelity assessment was only a single-agent indicative review. [MEASURED-REPO: [Framework-G report](/home/ec2-user/css/kernel/kernel-of-truth/data/haiku-tier/s1-experiments/s1-report.md), [modelAuthored schema](/home/ec2-user/css/kernel/kernel-of-truth/data/haiku-tier/modelauthored-schema.md)]

- The programme’s own dictionary-grounding test found 50/51 evaluable NSM primes in the WordNet Core, but a frequency-matched null was already about 97% Core; enrichment was approximately 1.01, \(p\approx0.58\). Thus dictionary structure did not independently ratify NSM primes. [MEASURED-REPO: [grounding prior-art report §6](/home/ec2-user/css/kernel/kernel-of-truth/reports/lit-primitives-grounding-priorart.md)]

- E8 found kernel–SAE correspondence for GPT-2↔Pythia-160M—primary \(\rho=.386\), partial \(\rho=.360\), both permutation \(p=.0001\)—but the two new pairs involving SmolLM2 did not replicate. The named hook-site mismatch is a real confound, but the programme currently has one positive pair, not a model-independent canonical geometry. [MEASURED-REPO: [original E8 verdict](/home/ec2-user/css/kernel/kernel-of-truth/poc/e8/results-incoming/20260707-131303-modal/verdict-e8.md), [extension result](/home/ec2-user/css/kernel/kernel-of-truth/poc/e8/results-incoming/20260707-143903-ext1-modal/results-e8-ext1.json)]

- K-NULL is directly relevant to the efficiency thesis: kernel and aligned plain-dictionary stores were equivalent within the registered margin; the concise plain store was nominally more accurate and used about 0.565× the verifier-side FLOPs. The tested mechanism consumed aligned answer strings, not vectors or explication structure. [MEASURED-REPO: [knull-v2 interpretation](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/analysis/knull-ufo-dual-model-reconcile-fable.md)]

These results do not say “the kernel is useless.” They say that determinism, source provenance, graph convergence, and model alignment are four different properties and must not be allowed to masquerade as semantic grounding.

## 1. Canonicality and grounding criteria

A useful definition for this programme is:

> A concept representation is canonical only relative to a declared **sense, profile, authority, and version**, when a public procedure selects one normative record, independently anchored evidence supports it, and every downstream encoding is reproducibly derived from it.

Write the canonical semantic record as:

\[
K_{A,P,t}(s)=
(\text{sense key},\ \text{scope},\ \text{typed constraints},\
\text{examples},\ \text{counterexamples},\
\text{dependencies},\ \text{status})
\]

where \(A\) is the authority or endorsement community, \(P\) the semantic profile, \(t\) the version, and \(s\) the sense—not merely a lemma. The vector is then:

\[
v = \operatorname{Encode}_{h}(K_{A,P,t}(s))
\]

A deterministic encoder can make \(v\) canonical relative to \(K\); it cannot make \(K\) true.

The required criteria are:

1. **Sense and authority are explicit.** “Bank” without a sense is not a canonical concept. “Canonical for whom?” must have an answer: a standards body, domain community, language-use panel, formal theory, or named federation.

2. **The evidential chain terminates outside the constructor and evaluated model.** Acceptable anchors differ by sector:

   - formal: axioms, definitions, proofs;
   - operational: measurement or decision procedures;
   - observational: independently labelled examples and counterexamples;
   - institutional: an identified legal, scientific, or standards authority;
   - ordinary lexical: independently collected usage judgements and contrast cases.

   Dictionary prose is source evidence, but by itself is not referential grounding. Harnad’s symbol-grounding argument characterises a symbol system defined only through other symbols as an internal “merry-go-round.” `[established][SV]`

3. **Evidence provenance is complete but distinct from semantic identity.** Preserve two pins:

   - a semantic-content hash over the normative scope and constraints;
   - an evidence-release hash over source revisions, anchors, derivation logs, and endorsements.

   This respects the project rule that provenance and world facts do not silently become definitional content.

4. **Construction is reproducible and robust.** Same pinned inputs and policy must yield the same candidate. Changing source set, parser, prompt, model, graph policy, or reviewer decision creates a new derivation or version. Stability should also be measured across permissible paraphrases and author models.

5. **Adequacy includes exclusions and uncertainty.** A record must say not only what counts, but what does not count and where it abstains. Minimal negation, scope, polysemy, and near-neighbour counterexamples are load-bearing because the current encoder’s raw geometry can treat a meaning-inverting edit as small.

6. **Dependencies are auditable.** References must resolve; cycles must either terminate in independently anchored records or be explicitly marked as mutually stipulative. Graph reachability alone is not grounding.

7. **Correctness utility is independent and claim-specific.** A kernel can check whether a claim uses a concept consistently with an endorsed definition. It cannot establish “Alice is X” without world-layer evidence about Alice. Gold labels must not be generated from the same record the verifier consults.

8. **Efficiency is an end-to-end Pareto claim.** Count authoring and review cost, source acquisition, mapper errors, storage, context tokens, model parameters, FLOPs, latency, and accuracy. A construction earns the efficiency thesis only if it beats hash-pinned definition text, smaller-model-alone, and other strong controls—not merely an empty prompt.

9. **The method has a real way to lose.** Unsupported clauses, source conflicts, poor cross-source stability, failure against shuffled mappings, equivalence with plain text, and excessive review cost must all be capable of killing or demoting it.

## 2. Comparison of methodologies (a)–(d)

| Method | Where it bottoms out | Canonicality | Coverage, scale, cost | Falsifiability | Strongest failure mode | Proposed role |
|---|---|---|---|---|---|---|
| **(a) LLM-generated NSM explications** | In the weak version, the model’s learned distribution. In the current repository version, pinned dictionary prose plus the model’s translation of it. Neither is an independent referential anchor. | A pinned prompt/model makes the procedure inspectable, but semantic output is sensitive to sense choice, prompt, model revision, stochasticity, and repair. Mechanical legality does not imply adequacy. | Potentially broad and cheap per draft. Current Framework G nevertheless yielded only 26% legal records in its 50-concept test, and semantic review becomes the likely dominant cost. | Strong if evaluated on post-cutoff nonce concepts, held-out authorities, humans, or deterministic gold. Weak or circular if another correlated LLM endorses fluent NSM-shaped output. | Fluent completion can overwrite source meaning, hide unsupported distinctions, or become thinner during gate repair. The same model family can then “recognise” its own idiom and fabricate validation. | **Salvageable as a compiler/proposal generator. Not admissible as the canonical authority.** The existing `ModelAuthored` tier is the right status. |
| **(b) Dictionary graph + convergence/FCA** | Human-authored dictionary definitions and the relations extracted from them. It bottoms out in source convention, not objects or observations. | Highly reproducible once dictionaries, sense segmentation, extraction rules, edge direction, convergence rule, and tie policy are pinned. But the result is conditional on those choices. Published dictionary studies reportedly find a roughly 10% Grounding Kernel and many alternative roughly 1% MinSets; non-uniqueness matters. `[established][SV]` A formal concept lattice is unique up to isomorphism given a fixed formal context, but prose-to-incidence mapping and attribute scaling remain construction choices. `[established][SV]` | Excellent lexical coverage after source/licensing and word-sense work. Deterministic recomputation is cheap; high-quality relation extraction and source reconciliation are not. | Good: exact source holdouts, edge perturbations, alternative dictionaries, sense-level replication, and downstream claim tasks are available. Self-reconstruction of the originating dictionary is not a valid external test. | A fixpoint can make circular prose stable without making it grounded. Shared dictionary conventions or errors can converge. SCCs and MinSets identify compressibility and dependencies, not meaning or truth. | **Use for sense inventory, stable-relation discovery, molecule prioritisation, conflict detection, and cycle auditing—not as the final semantic authority.** |
| **(c) Extract from model internals/SAEs** | The model’s training data, objectives, architecture, and observed behaviour. It is grounded in what the model represents, not independently in what is correct. | Poor as a universal canon: learned dictionaries are subject to permutations, rotations, feature splitting/absorption, seed and site dependence. The recent SAE literature reports substantial non-identifiability and instability. `[claimed][SV]` | Broad implicit coverage, but requires model access, activations, SAE fitting or public dictionaries, feature matching, and labels. Per-model extraction scales poorly as a universal registry. | Strong if tested cross-seed, cross-site, cross-family, on held-out models, and on causal downstream tasks. Weak if an SAE from the target model is used to certify that same model’s claims. | It can canonise the model’s own errors and biases. “Faithful to this model” becomes confused with “true.” Cross-model consensus can still reflect shared training data rather than external reality. | **Use as an independent behavioural validation and adapter target. Never use target-model internals to author the definition that will verify that model.** |
| **(d) Principled hybrid** | Multiple pinned human sources plus at least one operational, observational, institutional, formal, or usage anchor; graph structure constrains; an LLM compiles; independent endorsement decides. | Canonical relative to a named authority/profile/version. Deterministic graph and encoder stages are reproducible; disagreements become explicit forks or revisions rather than hidden averaging. | More expensive per promoted record because review is real. Scale comes from tiering: unreviewed bulk remains `AxiomsOnly`/`ModelAuthored`; only reviewed records enter the canon. | Best of the four: source holdout, graph perturbation, nonce concepts, counterexamples, reviewer agreement, text nulls, shuffles, and held-out-model validation all attack different links. | Consensus can launder shared source bias, human governance can become slow or political, and the review cost may erase any compression benefit. | **Recommended primary construction methodology.** |

Two direct answers follow.

- **Is (a) fatally circular?** No, not when the LLM is a constrained translator from independently pinned evidence and its output is independently adjudicated. Yes, for the canonicality claim, if the LLM’s latent beliefs are the authority or if correlated models provide the only adequacy judgement.

- **Does (b) escape circularity?** No. It removes dependence on one generative model and exposes structure reproducibly, which is valuable. But convergence is a property of a human-authored symbol graph. It does not manufacture an external referent or make one of many possible MinSets uniquely semantic.

## 3. Recommendation and strongest objection

Adopt **an evidence-anchored, graph-constrained, independently endorsed hybrid**:

1. **Declare the unit.** Create records per sense, with profile, domain, language, authority, and intended verification scope fixed first.

2. **Assemble an evidence packet.** Require multiple independently pinned sources where available, plus at least one non-constructor anchor appropriate to the sector. Record source conflicts instead of silently synthesising them.

3. **Build a sense-level evidence graph.** Extract signed, typed relations with source-span pointers. Compute SCCs, dependency depth, alternative minimal bases, and cross-source stable relations. Use convergence to identify reusable molecules and suspicious cycles, not to pronounce a concept grounded.

4. **Use Haiku as a compiler.** Framework G may propose the `kot-ast` record, but every semantic clause must cite one or more evidence-graph edges. Unsupported clauses fail; source conflicts force abstention or an explicit adjudication request. Mechanical validator feedback remains useful.

5. **Apply an independent semantic gate.** Reviewers see the evidence, examples, counterexamples, and proposed record, but not downstream test gold. Promotion requires agreement or recorded adjudication. Unreviewed output stays `ModelAuthored`; deterministic source-only relations may stay `AxiomsOnly`.

6. **Derive identity and geometry only after promotion.** Hash the normative content; separately pin the evidence release; then run the current deterministic encoder. Changing the endorsed record changes the concept identity/vector. Changing only provenance or annotations changes the evidence release, not silently the semantic identity.

7. **Use model internals downstream.** E8-style SAE alignment can test whether the canon predicts model representations and can provide per-model adapters or regression instruments. It must not feed back into canonical content without new external evidence.

This preserves the best parts of all four methods: (b)’s auditability, (a)’s scalable translation, the current encoder’s reproducibility, and (c)’s behavioural validation.

**Strongest objection:** the hybrid may solve epistemic cleanliness by destroying the programme’s economics. Multi-source reconciliation and independent endorsement could cost more than the value of the resulting representation, while “consensus” may merely formalise shared dictionary biases. A direct LLM author may synthesise broader usage knowledge more accurately and cheaply than a constrained graph. If matched-review experiments show direct LLM records equivalent on independent gold and materially cheaper, the recommended graph constraint is wrong and should be removed. Even then, independent endorsement—not the LLM—would remain the act that makes a record canonical.

## 4. Cheap, decisive experiment: KBUILD-0

### Question and hypotheses

Test construction methodology before another scale build.

- **Primary hypothesis H-KBUILD:** at a fixed context budget and matched semantic-review budget, the recommended hybrid improves external claim-verification balanced accuracy over direct Framework-G construction by at least **0.08 absolute**.
- **Deflation hypothesis H-TEXT:** the best constructed kernel is equivalent to hash-pinned source text within **±0.03** while costing more. If supported by TOST, adopt the text store for this scope.
- **Assignment hypothesis H-SHUFFLE:** correctly assigned representations outperform within-stratum shuffled representations. Failure means the representation is not carrying concept-specific evidence.

### Evaluation set

Use two preregistered strata:

1. **Primary: 96 post-registration nonce senses.** Generate finite micro-worlds with exact hidden truth conditions using existing representable predicates, relations, negation, scope, and molecule references. Assign random nonce labels after generation. For each sense, publish to constructors only:

   - three independently rendered source descriptions;
   - positive, negative, and boundary exemplars;
   - source authority/provenance labels.

   Hold back the generating rule and eight balanced `ENTAILED`/`CONTRADICTED`/`UNDERDETERMINED` claims per concept. Because the concepts and labels are created after preregistration, success must come from the supplied evidence rather than memorised lexical beliefs.

2. **Confirmatory: 48 natural, ambiguity-rich senses.** Constructors receive two pinned build sources. Gold claims come from an independent held-out source plus two blinded human annotators and adjudication. This stratum tests whether the nonce result transfers to ordinary lexical material; it cannot rescue a failed primary.

Construction authors, reviewers, host-model operators, and result auditors remain role-separated.

### Construction arms

All constructors receive identical evidence packets and output the same typed record schema.

- **A0 — current method:** Framework G exactly as pinned: Haiku draft, one validator-error-fed repair, no semantic editing. Illegal output and abstention remain in the denominator.
- **A1 — reviewed current method:** A0 followed by the same fixed reviewer time budget and endorsement protocol used by the hybrid. This isolates graph constraint from the mere presence of humans.
- **B — dictionary graph:** deterministic sense graph; retain source-supported signed relations under a frozen rule, compute the frozen closure/fixpoint, and render without generative semantic additions.
- **H — recommended hybrid:** B’s evidence graph → Haiku compilation with clause-level evidence pointers → the matched independent endorsement protocol.
- **T — kernel-as-text null:** retrieve the hash-pinned source definitions directly, with no graph, AST, vector, or generated explication.
- **S — shuffled controls:** independently permute the concept↔representation mapping for A1, B, H, and T within sense type and token-length strata. Bytes, token budgets, and format stay unchanged.
- **N — no-context control:** claim only.

Method (c) is not a primary construction arm: a target model’s internals cannot independently define newly generated nonce concepts without receiving or learning their evidence. SAE alignment is instead run descriptively after construction to test whether any successful records predict held-out-model representations.

### Consumer and budget

Before freezing test outputs, select the smallest host from a preregistered local-model ladder that passes the calibration gate, starting with the repository’s pinned SmolLM2-135M-Instruct. The selected host is from a different family than Haiku and receives no training or adapter.

Every record is deterministically rendered. The host returns one of three fixed labels by log-probability scoring. The primary run uses a **256-token evidence ceiling**. Secondary compression curves use 64/128/256 tokens under frozen truncation/ranking rules.

This experiment tests construction and training-free contextual compression. It does not, by itself, validate raw-vector injection; vector bytes, AST bytes, and rendered tokens must nevertheless be reported so no vector-efficiency claim is inferred from a text-only consumer.

### Primary endpoint and statistics

**Primary endpoint:** per-concept macro balanced accuracy across the three claim labels on the 96 nonce senses, comparing **H versus A1** at 256 tokens.

- Unit of resampling/permutation: concept, not individual claim.
- Statistic: paired difference \(\Delta=\mathrm{BA}_{H}-\mathrm{BA}_{A1}\).
- Analysis: 10,000 paired sign permutations, two-sided \(\alpha=.05\), BCa 95% confidence interval and effect size.
- Advance hybrid only if the lower confidence bound exceeds **+0.08**.
- Before freezing, simulate power from calibration data; require at least 90% power for an 0.08 effect. If 96 concepts are insufficient, increase once to a preregistered maximum of 160 before any test run.
- Secondary contrasts use Holm correction. Equivalence claims use TOST, never non-significance.

### Instrument gates

Failure of any gate yields `INSTRUMENT-INVALID`, not a substantive null:

1. **Gold gate:** the micro-world engine passes exhaustive rule/claim self-tests; a blinded 10% paraphrase audit reaches at least 95% correct interpretation.
2. **Reader-competence gate:** on separate calibration concepts, the real T arm has one-sided 95% lower-bound balanced accuracy ≥0.70.
3. **Leakage gate:** N remains ≤0.40 balanced accuracy; nonce labels and gold-rule hashes are created after preregistration and withheld from every constructor and reviewer.
4. **Assignment-sensitivity gate:** real T exceeds shuffled T by at least 0.20 on calibration. Otherwise the host or task is not reading the evidence.
5. **Coverage gate:** every selected item and every construction failure remains in the denominator; no post-outcome attrition. Parser/renderer success must be ≥99%, or the relevant arm fails operationally.
6. **Independence gate:** no LLM supplies gold labels or primary judgements; the Haiku author cannot be the host or auditor.

### Kill and selection rules

- **Kill direct LLM generation as the primary constructor** if H beats A1 by the primary +0.08 rule. Haiku may remain a compiler inside H.
- **Kill unreviewed Framework G as canon-ready** if A0 fails to beat its shuffled control by a lower confidence bound of +0.05, or if its externally unsupported-constraint precision has a 95% lower bound below 0.95. Its `ModelAuthored` candidate role survives.
- **Retain direct LLM compilation** if A1 and H are TOST-equivalent within ±0.05 and A1 has lower measured lifecycle cost.
- **Reject graph convergence as a necessary ingredient** if B/H supply no corrected improvement over matched-review A1 and do not reduce semantic error or review time.
- **Deflate to hash-pinned text** if T is TOST-equivalent to the best constructed arm within ±0.03 and is cheaper in authoring, tokens, FLOPs, and maintenance.
- **Kill all construction-specific content claims at this scope** if correctly assigned structured arms are equivalent to their shuffles.
- **Efficiency passes only** if a constructed arm is non-inferior to T within −0.02 accuracy while using at most half its context tokens, or is more accurate at equal tokens, with full authoring/review/storage/FLOP costs reported. Otherwise correctness and efficiency receive separate verdicts.

This requires deterministic preprocessing, a few hundred Haiku calls, less than a GPU-day of small-model inference, and a bounded human review exercise. Most importantly, arbitrary post-registration concepts, deterministic gold, a text null, and assignment shuffles give the current LLM-generation approach nowhere circular to hide. The resulting report should go to the coordinator’s review gate and then to Fable for adversarial critique before any methodology is adopted.