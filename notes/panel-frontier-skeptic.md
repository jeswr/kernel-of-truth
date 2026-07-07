# Panel review — frontier-lab skeptic (adversarial pass)

**Reviewer persona:** senior researcher at a frontier lab (pretraining + interpretability adjacent), 30-minute skeptical read of an external pitch. This is the meeting the programme says it wants; these are the objections that meeting will produce.
**Read:** docs/architecture.md, docs/poc-design.md; skim of reports/fixed-vectors-in-llms.md, reports/deterministic-concept-vectors.md; README.md, notes/mandate.md.
**Date:** 2026-07-07. **Register:** harshest fair reading. The docs' honesty is unusually good — several objections below are built from the programme's own evidence, which is exactly what a hostile reader will do with them.

---

## Ranked objections

### O1. No scaling story — and the genre's track record at scale is negative

**At full strength.** Even if E4 works at 15M params, why would anything survive to 1T? You have no scaling argument, and worse, your own citations establish the prior *against* you: semantic initialisation washes out with continued training (arXiv:2407.05841); the ERNIE/KnowBERT KG-injection line was brittle and "lost to scaling" (your §2, C4); LCM — the one scaled attempt to force a fixed semantic vector space — has a measurably *worse* scaling exponent (0.49–0.57 vs 0.79); in-domain frozen init helps only at 10–100M tokens. The pattern a frontier lab has watched a dozen times: input-side semantic scaffolding helps small models on narrow evals because small models are data-starved for exactly the structure you inject; big models learn that structure from data for free, and the scaffold becomes either inert or a constraint. A 15M-param positive is where these ideas *always* look best. Your kill chain even says "E4 positive ⇒ begin frontier-lab prospectus on the strong form" — that is precisely the move that gets a pitch dismissed: one tiny-scale positive, zero scale points, straight to the lab.

**Do the docs answer it?** No. The mixed-outcome branch of the kill chain mentions "the scaling caveat stated", but there is no scaling experiment anywhere in the ladder — not even two points to draw a slope through.

**What would.** A scale-trend result: the kernel-frozen advantage (E1/E4 metrics) measured at ≥3 model scales (e.g. 15M / 160M / 1B non-embedding params) with matched token budgets, showing the advantage flat or *growing* with scale — or a mechanistic argument for why it should (e.g. the claimed advantage lives in emission geometry for rare/unseen concepts, a coverage problem scaling doesn't fix, not a capacity problem it does). Without a slope, do not book the meeting.

### O2. The PoC cannot host the object the theory built: D ≈ 8k–32k vs d_model ≈ 384

**At full strength.** Your capacity mathematics — the genuinely strong part of the deterministic-vectors report — *mandates* D ≈ 8k–32k for decodable capped explications (2–4 kbit of structure at 0.2–0.5 bits/dim). Your E1/E4 host is a GPT-2-style model with 5–15M non-embedding params, i.e. d_model ≈ 256–512. Nowhere in poc-design.md is it stated what D the kernel vectors have in the E-series or how they enter the model. Every resolution loses: (a) down-project 8k→384 and you've destroyed the margins and decodability the whole §7.2 arithmetic exists to guarantee — the model sees a lossy shadow, and phase X validates an object the E-series never touches; (b) build the kernel natively at D = 384 for the toy — fine for 115 concepts by sphere-packing, but then the experiment says nothing about the 10⁵-concept, capacity-limited kernel you're actually proposing; (c) learn a projection — congratulations, you've reintroduced a trained adapter and A1 has silently collapsed into A2 before the first run. This is an internal-consistency hole a reviewer finds in ten minutes.

**Do the docs answer it?** No — the dimension question is entirely absent from poc-design.md. (Architecture.md's "tied input/output rows" makes it worse: tied rows must live in model dimension by construction.)

**What would.** State the injection mechanism per experiment, pre-registered. If (b), say explicitly that E1/E4 test "structure-derived content vs random at matched D" and *not* the capacity story, and add a separate bridge argument. If a fixed random (JL) projection, quantify the margin loss at D=384 for kernel v0 and show the property tests still pass through the projection.

### O3. The phrase→concept mapper is the ontology problem reborn — and it confounds your core experiment

**At full strength.** Tokenizers already learn subword semantics from data, maintenance-free, for every language and domain simultaneously. Your mapper — a deterministic lemma/multiword lexicon — reintroduces everything that killed hand-built ontologies: coverage (what fraction of real token mass maps?), ambiguity ("bank", "run", "set" — a deterministic mapper either picks wrong or abstains; both pollute the training signal on kernel rows), sense drift, multilinguality, and a permanent human maintenance burden. Cyc and WordNet are institutional memory at every lab; "deterministic path is primary, learned assist is an annotation" is a governance statement, not an error-rate statement. And it sits on the critical path of E1: the corpus augmentation runs through the mapper, so an E1 null is unattributable — is structure-derived content worthless, or did a noisy/sparse mapper never deliver the concepts to the model? You are about to spend your headline experiment on a confound.

**Do the docs answer it?** Partially acknowledged (architecture.md §3 fixes the policy), but there is no mapper evaluation anywhere: no precision/recall, no coverage measurement, no ambiguity-rate handling, and no analysis of E1's robustness to mapper error.

**What would.** A measured mapper: precision/recall against human annotation on a sample, % of corpus token mass mapped, ambiguity/abstention rates; plus either a controlled-noise-injection arm in E1 or a synthetic-corpus arm where the mapping is exact by construction (TinyStories partially provides this — say so and exploit it deliberately).

### O4. What fraction of reality is kernel-expressible? The 65-prime basis and the authoring economics

**At full strength.** NSM explications are notoriously verbose, contested among NSM scholars themselves, and expensive: your own report puts automatic explication at DeepNSM ≈ 24/100 — so kernel content is hand-authored. Hand-authored, at 10⁵ concepts, in a formalism requiring trained semanticists, with what inter-annotator agreement and at what cost per concept? And the basis cannot express most of what a frontier model's token mass actually is: code, mathematics beyond toy arithmetic, chemical nomenclature, procedures, perceptual description, named entities, jargon. If the kernel-expressible fraction of a real training distribution is low single-digit percent, that is a hard ceiling on *every* claimed benefit — accuracy, training efficiency, and dense I/O all scale with coverage. "Not locked into NSM; maths and units admissible" (mandate) is a hand-wave: each additional basis multiplies the authoring, governance, and mapper problems.

**Do the docs answer it?** The authoring limit is honestly stated (architecture.md §4, "what we do not claim"). The economic and coverage consequences are not confronted anywhere: no coverage estimate, no cost model, no stated scope boundary.

**What would.** A token-mass coverage measurement over a representative corpus slice (even crude: % of content words with a plausible profile-1 explication), a per-concept authoring cost estimate with an IAA figure from a small pilot, and an explicit scope claim ("the kernel covers definitional/abstract/regulatory vocabulary; here is why that slice is disproportionately valuable") rather than an implicit universal one.

### O5. The accuracy claim died in your own §2 — what exactly is the residual value proposition to us?

**At full strength.** Your architecture.md concedes C1 is contradicted: fixing a vector fixes a symbol, not its meaning; interpretation lives in trained mid-layer computation you don't touch. What survives is "misunderstanding becomes detectable and correctable at the interface" (A5: decode–verify with provenance). But we *ship* that: retrieval with citations, constrained decoding against KBs, post-hoc verifiers, refusal tuning. The burden is now on you to state the delta over deployed RAG-plus-citations — and notably, your experiment ladder never measures it: there is no experiment comparing decode-verify against a retrieval baseline on any grounding/hallucination benchmark. The tier you call "unconditionally deliverable" is also the tier with zero experimental support in the PoC.

**Do the docs answer it?** The reposition is honest (accountability, not infallibility) but the comparative case versus shipped retrieval is never made, and A5 has no experiment.

**What would.** Name the deltas precisely — (i) drift-free *identity* of reference (a citation points at text; a concept-hash points at a versioned, machine-checkable definition with O(1) equality), (ii) verification against *definitions* rather than retrieved passages (catches meaning-level errors retrieval can't), (iii) ZK-verifiable grounding commitments (prove the lookup without revealing the store) — and add one A5 experiment: decode-verify vs vanilla RAG on a factual-consistency benchmark, measuring what each catches that the other doesn't.

### O6. Why NSM-by-hand rather than a learned interpretable basis? You never mention SAEs

**At full strength.** Interpretability teams already extract millions of monosemantic feature directions with sparse autoencoders — discovered in the model's own geometry, with causal handles (steering, clamping, ablation), covering whatever the data contains, no semanticists required. Against that in-house capability, a hand-authored 65-prime basis at ~115 concepts looks like a toy from a different decade. That the architecture documents *never discuss SAE features* — the reigning "interpretable concept basis" at every frontier lab — will read as either unfamiliarity with the state of the art or evasion.

**Do the docs answer it?** No. Complete silence.

**What would.** The steelman is available and strong: SAE dictionaries are per-model, unstable across seeds/checkpoints, *unlabeled* (labeling is the expensive part), non-compositional, unversioned, and unusable as a cross-organisation reference. The kernel is the exact complement: stable, portable, definitional, versioned. The productive framing is kernel-as-canonical-label-space *for* learned features — which suggests the missing experiment (see "one result", below): align kernel vectors to SAE feature dictionaries across ≥2 model families; if kernel geometry predicts cross-model feature correspondence better than shuffled controls, interp teams will care. Add this to the docs or expect the room to ask why it isn't there.

### O7. E4 as specced is statistically weak and will be discounted as zero-shot learning, circa 2009

**At full strength.** Kernel v0 is ~115 concepts; 20% held out is ~23 concepts; top-10 over a 115-way vocabulary has a chance rate of ~8.7% — "unseen top-10 above chance" is a bar you could clear at 15% and claim victory. Confidence intervals over 23 items and 3 seeds are wide enough to drive a truck through. And the positive result, even cleanly obtained, has a 15-year-old precedent class: zero-shot classification via semantic output codes (Palatucci et al. 2009) and DeViSE (2013) — "geometry places unseen classes' read-outs" is established; your novelty is only that the code is training-free and compositional, which a reviewer will note in the first minute. "A positive here is the single cheapest result making the strong claim credible" (poc-design) overprices it.

**Do the docs answer it?** Pre-registration is to your credit; the bar itself is too low, and the ZSL lineage is uncited in the experiment design.

**What would.** Scale the concept vocabulary to ≥10³ before running E4 (synthetic capped explications are already generated for X1 — reuse them as emission targets); report top-1/top-10 with exact chance rates; add a compositional split (unseen concepts whose explications share structure with seen ones vs not) — the *compositional* generalisation is the part classic ZSL doesn't give you, so make it the measured thing. Cite Palatucci/DeViSE and position against them explicitly.

### O8. The update paradox: your own C1 evidence breaks your maintenance story

**At full strength.** The kernel is versioned and revisable; the rows are frozen. By your own account (C1, contradicted), the network learns its interpretation *around* whatever fixed symbol it is given. So when the kernel revises a concept — and content-addressing means the new explication is a *new* vector, with recomputation cascading through every concept that references it, Merkle-style — the deployed model's learned interpretation stays attached to the old geometry. You cannot hot-swap a frozen row and expect the trained computation above it to follow. Ergo: a "kernel-native" model is pinned to a kernel snapshot at training time, and drift-freedom of *reference* buys you nothing about deployed models tracking kernel *revisions*. The governance layer's best feature (versioned evolution) is inert exactly where the architecture claims it matters (inside the weights).

**Do the docs answer it?** No — versioning is discussed for the kernel object (identity layer, endorsement), never for the trained-model lifecycle.

**What would.** Concede it and reposition: models pin kernel snapshots like software pins dependency versions; revision compatibility is handled at the interface (A5 decode-verify against the *current* kernel, with hash-level detection of stale references), not in the weights. That's coherent — but it's another argument that the interface tier, not the vocabulary tier, is the real product.

### O9. The similarity pathology is load-bearing in more places than the docs admit

**At full strength.** You state honestly that provable similarity is structural overlap and a single deep NOT moves the vector ~1/s while inverting meaning. But then E2 — your "cheapest genuine falsifier" — is an RSA between kernel-cosine structure and model representations: a *positive* may reflect nothing but lexical overlap between definitions (your own report notes trained-embedding similarity is mostly lexical anyway — Wieting & Kiela, McCoy et al.), and a *negative* may reflect only the polarity pathology rather than the absence of shared geometry. E2 is a weak falsifier in both directions, yet the kill chain gives it a gate. The same pathology poisons the mapper's future embedding-similarity assist and any consumer of kernel-kNN (A5's interpolation toward kernel neighbours could interpolate toward an antonym).

**Do the docs answer it?** X3 measures and publishes the pathology — good — but no downstream consumer of similarity is re-analysed in its light, and E2's interpretation isn't conditioned on X3's numbers.

**What would.** Pre-register E2's interpretation contingent on X3 (e.g. run RSA on polarity-stratified subsets); ban raw kernel-cosine from A5 pending a polarity-aware variant that dominates in X3.

### O10. Content-addressed governance: irrelevant to our training pipeline — or the only part we'd buy? (steelman both ways)

**Against (the room's reflex).** Federation endorsement, multihash identities, ZK commitments — these solve *coordination between mutually distrusting parties*. A frontier lab's pretraining pipeline has one party. Internal teams version datasets in-house, don't need cryptographic fixity of concept reference, and will see the governance layer as pure overhead attached to an embedding table. If the pitch leads with governance, the research audience checks out.

**For (the steelman, which is real).** (i) *Provenance and compliance pressure is not hypothetical*: EU AI Act GPAI obligations (technical documentation, training-content summaries; in force for new models since Aug 2025), C2PA-style content credentials, and regulated verticals (medical, legal, finance) that demand auditable grounding. A content-addressed, versioned concept-and-fact layer with cryptographic commitments is a compliance artifact a policy team could deploy without touching pretraining. (ii) *Cross-version semantic regression testing*: labs ship model families; "did v(N+1)'s operational meaning of 'informed consent' move?" is a question with no current instrument; a fixed kernel plus per-model adapters (A2) is exactly that instrument. (iii) *Agent interop*: multi-agent systems across orgs need shared references with verifiable identity — a schema registry for meaning. (iv) *Verifiable claims to auditors/courts without revealing weights* — uniquely ZK-shaped. **Net:** the governance layer is irrelevant to the pretraining org and plausibly valuable to assurance/policy/enterprise orgs. Which means: if the meeting is with a research team, this material is ballast; if with an assurance team, it's the lede. The current docs pitch both at once, which lands with neither.

**Do the docs answer it?** Architecture.md §3/A5 states the composition with sparq/ZK but never asks *who inside a lab* is the customer.

**What would.** Split the prospectus: a research-team pitch (O1/O2/O6-shaped evidence, no governance) and an assurance-team pitch (A5 + provenance + AI Act mapping, no strong claim).

---

## Smaller nits the room will also land

- **3 seeds, non-overlapping 95% CIs** as the E1 bar: underpowered; at this scale seed variance on concept-slice metrics is large. Prefer ≥5 seeds and effect-size reporting.
- **TinyStories biases E1 toward the null**: a 1.5k-word vocabulary distribution has almost no rare-concept structure for kernel content to pay off on; the design stacks the deck against the very effect it tests, then the kill chain treats the null as informative.
- **"$30 kill chain" asymmetry**: cheap tiny-scale experiments can kill the claim but cannot establish it; the docs use the framing symmetrically. A lab will not.
- **Tied frozen rows**: your own report (§1) notes tying warps input embeddings toward output geometry and likelihood training degenerates output embeddings; freezing escapes degeneration but forces the network to compensate — an uncontrolled tax on the kernel-frozen condition specifically.
- **"Nothing like it has been published" [open novelty]**: do the search before the meeting; a reviewer finding the counterexample live is fatal to credibility that the honesty tags otherwise earn.

---

## The one result that moves the room

**E4 as currently specced is not it.** At 115 concepts / 23 held-out / top-10-above-chance it is statistically soft (O7), it will be discounted as compositional ZSL with a training-free code, and it carries no scale information (O1).

Two candidates actually move a frontier audience, and only one is in the ladder in embryo:

1. **The scale-slope result (not in the ladder).** Kernel-frozen advantage on concept-slice metrics at 15M / 160M / ~1B, matched tokens, ≥10³-concept vocabulary, advantage flat or growing with scale. This is the only currency the pretraining side trades in. Cost is no longer $30 — call it $2–10k — but it is the difference between "cute small-model trick" and "inductive bias worth a meeting". If forced to choose one headline experiment for the pitch, it is this, built on E1/E4's machinery.
2. **The cross-model alignment result (cheapest room-mover if the strong claim dies).** Extend E2/E5: show the kernel's designed geometry aligns — beyond shuffled-kernel and permutation nulls — with *learned* concept representations (embedding RSA, and ideally SAE feature dictionaries) across ≥2 model families, such that kernel coordinates predict cross-model feature correspondence. That is a Platonic-Representation-adjacent, interp-relevant claim: a canonical, versioned, *labeled* coordinate system for concept features that transfers across models. Interp teams currently lack exactly that label space. This survives the death of A1 entirely.

Verdict: run the kill chain as designed (it is cheap and honest), but do not walk into the lab with E4 alone. The meeting-worthy artifact is (1) if the strong claim lives, (2) if it doesn't.

---

## The fallback value proposition (the honest paragraph if the strong claim dies)

> The kernel is not a way to make models understand; it is a canonical, machine-checkable *reference layer for meaning* that lives outside the model. Each concept carries a content-addressed identity, a hand-audited formal definition, and a deterministically computed vector whose geometry provably reflects definitional structure — versioned, portable, and verifiable down to ZK commitments. Attached to any trained model through a small learned adapter (the configuration all convergence evidence actually supports), it gives labs and their customers three things they cannot currently buy: drift-free cross-model and cross-version reference (regression-test what a model family means by a term), grounding verified against *definitions* rather than retrieved text (with cryptographic provenance for auditors and AI-Act-shaped documentation), and a stable, labeled coordinate system to which learned interpretable features can be anchored across models. It makes no claim about what happens inside the weights; it makes the interface between model behaviour and human-governed meaning inspectable, and it is buildable now.

The strong claim's death leaves a standards-and-instrumentation play, not an architecture play. That is a smaller pitch, a different buyer (assurance/interp/enterprise, not pretraining), and — unlike the strong form — one the current evidence actually supports.
