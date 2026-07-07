# Kernel of Truth — architecture synthesis (rev 1, pre-adversarial-panel)

**Status:** draft design record, 2026-07-07. Synthesises the five wave-1 reports in `../reports/`; every load-bearing external claim is cited there with primary sources — this document cites the reports and only repeats arXiv IDs where a single result carries an argument.
**Author:** Kern (Claude Fable 5), for @jeswr. Coordination: [sparq-org/sparq#1683](https://github.com/sparq-org/sparq/issues/1683).
**Honesty contract:** claims are tagged **[established]** / **[claimed]** / **[open]** / **[contradicted]**. Where the maintainer's original hypothesis is contradicted by evidence, this document says so plainly and states the strongest surviving form.

---

## 0. Executive summary

The wave-1 evidence supports a **layered restatement** of the hypothesis. The original strong form — *fixed concept vectors inside an LLM act as built-in ground truth the model can never misunderstand* — is **contradicted** by three independent lines of evidence (§2). But four things survive, and together they still amount to a serious programme:

1. **The kernel object itself is buildable and novel** [established feasibility, open novelty]. A deterministic, training-free explication→vector encoder with quantified capacity guarantees exists as a construction (§1); nothing like it has been published; and the identity layer (concept-hash) already has a working prototype in the estate.
2. **Frozen concept rows in an LM are mechanically viable** [established] — models train fine around frozen embedding rows; E-BERT-style frozen external vectors with a small learned adapter reached SOTA factual probing. The open question is whether *structure-derived content* in those vectors buys anything over random frozen vectors — no one has tested it (the niche is open), and the nearest result (frozen Unicode-glyph embeddings, arXiv:2507.04886) predicts the null.
3. **"Authoritative" survives at the interface, not inside the weights** (§3). Drift-free, content-addressed, cross-system concept *reference* — with verification, endorsement, and ZK-compatible commitments — is unconditionally deliverable and composes with the sparq estate today. What is NOT deliverable on current evidence is a guarantee about the model's internal *interpretation* of those references.
4. **The decisive experiments are cheap** (§5 pointer): the kill chain (geometry-alignment probe → frozen-content test → unseen-concept emission) prices the strong claim's life or death at roughly $30 of rented GPU time.

**Recommended posture:** build the kernel encoder and kernel v0 data now (this is novel work with standalone value); run the kill chain; stage the architecture bets (§4) on its outcome. Do not pitch the strong claim to a frontier lab before E1/E4 read out — pitch the kernel + evidence programme.

---

## 1. The kernel object (model-independent)

The kernel is a versioned set of concepts, each carrying three coordinated representations. This layer is independent of any LLM and is where most near-term construction happens.

### 1.1 Three representations per concept

| Layer | Object | Guarantee | Source |
|---|---|---|---|
| **Identity** | `urn:concept:<multihash>` over the definition record (PSS concept-hash design; prototype exists), plus an AHU-canonical-form + homomorphic multiset hash (LtHash-style) over the explication tree for O(1) incremental equality | Cryptographic fixity of reference; collision-resistant injectivity | [established] — reports/deterministic-concept-vectors.md §5.3, gist §6 |
| **Geometry** | Canonical vector `v(c) ∈ R^D`, `D ≈ 8k–32k`, from the two-level TPR/VSA encoder (§1.2) | Margin injectivity whp over the capped explication space; similarity = weighted structural overlap; decodability *given the kernel* | [established capacity math; construction novel] — reports/deterministic-concept-vectors.md §7 |
| **Structure** | The explication tree itself (profile-1 closed grammar: ≤32 clauses, ≤32 referents, closed role/operator inventories) | Ground truth for both hashes and vectors; the caps are load-bearing for the capacity bounds | gist §4–§5 |

### 1.2 The encoder (construction B, with C as its proof lens)

Primary construction, from reports/deterministic-concept-vectors.md §7.3:

- **Within a clause:** exact tensor-product binding over an *exactly orthonormal* deterministic codebook (Hadamard/DFT rows) for the ~200 closed atoms (65 primes + roles + operators + indices). Exact unbinding, zero crosstalk. Deterministic by construction — no seeds, no training.
- **Across clauses/depth:** unitary circular-convolution binding (depth-stable variance) + position permutation + superposition. Concept references bind the *referenced concept's own canonical vector* — compositionality by construction, and reference-not-inline is what keeps the structure budget `s ≈ 100–200` bound terms per concept.
- **Decoding:** recursive unbinding + nearest-neighbour cleanup against the kernel lexicon itself (every concept's vector is the cleanup memory), resonator networks for multi-factor terms. **The honest statement, always:** structure is recoverable *given the kernel*, never from the vector alone [established limitation].
- **Formal lens:** the resulting vector is a linear sketch of the explication's WL-subtree feature multiset; compressed-sensing results (exact ℓ₁ recovery at `D = O(s log N)`) are the right tool for *proving* decodability claims [established].
- **Arithmetic:** capped explications carry ~2–4 kbit of structure; published capacity constants (0.2–0.5 bits/dim robust) put **D ≈ 8k–32k** inside every relevant bound — 16–64 kB per concept fp16, 3–6 GB for a 10⁵-concept kernel [established].

**Known unsolved weakness — stated up front:** provable similarity is *structural overlap*, which diverges from semantic similarity exactly where meaning inverts cheaply: one deep `NOT` moves the vector ~1/s of its norm while flipping the meaning [established]. Mitigations (polarity-aware weighting, canonicalisation above the encoder, treating similarity as relational rather than metric) are design work, not solved problems. Any consumer of kernel-vector similarity must know this.

### 1.3 What sparq supplies (reports/sparq-estate.md)

The periphery exists: RDFC canonicalisation (`sparq-canon`), deterministic typed lane encoders (thermometer numerics, enum codebooks with exact decode, QUDT unit normalisation), hashing discipline (`Poseidon2(type_code, blake3(bytes))` with canonicalise-then-domain-separate — same shape as the concept-hash's header-in-digest), mmap'd vector stores + ANN, and grounding dispatch (vector/subgraph/NL/typed-value). Three named gaps the kernel must fill or negotiate: the store is u32-dict-id-keyed (a hash-keyed table is an acknowledged unbuilt follow-up), the store header carries no encoder/model provenance, and sparq's pooling is permutation-invariant while explication clause lists are **ordered**.

---

## 2. The maintainer's four claims against the evidence

From reports/fixed-vectors-in-llms.md and reports/nsm-and-knowledge-injection.md:

**C1 — "The model can never misunderstand kernel concepts": [contradicted] as stated.** Input embeddings are already static in every transformer; interpretation is constructed downstream in trained layers (detokenization stages; factual knowledge in mid-layer MLPs). Models train successfully around embeddings frozen to noise or Unicode-glyph pixels — networks treat fixed vectors as arbitrary identifiers whose interpretation they learn anyway. **Fixing a vector fixes a symbol, not its meaning.** Surviving form: misunderstanding becomes *detectable and correctable at the interface* — kernel-decoded output can be verified against explications outside the network (§4, A5) — and reference can never drift. That is an accountability guarantee, not an infallibility guarantee.

**C2 — training efficiency: [mostly contradicted].** Embeddings are among the least performance-critical parameters; semantic initialisation washes out; frozen random embeddings can *slow* convergence 5–10×; the knowledge still has to be trained into MLPs. Surviving form [open]: *content-bearing* frozen vectors have never been tested for sample-efficiency on concept-heavy distributions — that is exactly experiment E1, and arXiv:2507.04886 predicts the null. We run it to find out, not because we expect to win.

**C3 — dense concept I/O: [contradicted at scale, open at kernel scale].** Meta's LCM — the closest existing test — scales *worse* than token LMs (exponent ~0.5 vs ~0.79) in a frozen learned sentence space; the tokenizer-free architecture that works (BLT) uses learned dynamic units, the opposite design. Surviving forms: (i) a *compositional designed* space (ours) is a different object from SONAR — untested [open], toy-testable (E3); (ii) adapter-mediated dense injection has real partial wins (xRAG one-token documents at 62–73% fidelity; KBLaM linear-scaling KB attention) [established, lossy].

**C4 — internal rules-based inference: [speculative].** Only an unreviewed theory preprint; the KG-injection precedent (ERNIE/KnowBERT line) was brittle and lost to scaling; superposition/interpretability evidence says trained models store concepts as distributed non-orthogonal directions, so "one reserved internal vector per concept" is unsupported *inside* the network. Reposition: rules-based inference runs **kernel-side** (deterministic, verifiable, over explications and world-layer facts — sparq's reasoners already exist) with the LM as proposer — a neuro-symbolic loop at the interface, not inside the weights. Whether any of it belongs *inside* the architecture is deferred until E-series evidence exists.

**The cross-model convergence literature cuts in our favour** [established]: relative representations, model stitching, vec2vec, and the Platonic Representation Hypothesis all say independently trained models converge toward compatible geometries *up to a transform*. That is precisely the weak-kernel claim: one canonical geometry, per-model learned adapters. It is also precisely *not* the strong claim (shared raw coordinates with no adapter).

---

## 3. The system stack

Three tiers, restated from the mandate with what wave-1 makes concrete:

1. **Kernel** (small, definitional, abstract): 65 prime records + sanctioned molecules + explicated concepts. Each concept: identity hash + explication + canonical vector. Governance: federation endorsement per the concept-hash design; vectors published as signed `(concept-hash → vector)` annotations keyed by **(encoder-version, D, codebook-hash)** — the encoder itself is content-addressed, closing the "which encoder produced this" provenance gap sparq's store has.
2. **Phrase→concept mapper**: lemma/multiword lexicon first (deterministic, auditable), embedding-similarity assist later [design decision: the deterministic path is primary; a learned assist is an annotation, never identity]. This is the tokeniser-adjacent artefact of the mandate, made precise: a transducer from token sequences to kernel references, not a new tokeniser.
3. **World layer**: facts as explication-structured, content-addressed assertions *over* kernel concepts ("Jesse as a person"), assumed-true per the mandate's explicit deferral of qualification. Mechanically: this is sparq PKG territory — the `(concept-hash → embedding)` table seam plus named-graph facts; the kernel supplies the vocabulary, sparq supplies storage/query/ZK.

---

## 4. Architecture portfolio (staged bets, each tagged with the claim it tests)

Ordered from strongest claim to weakest; the PoC design (docs/poc-design.md) prices each. We hold all five honestly rather than pre-committing: the kill chain decides.

- **A1 — Kernel-native vocabulary** (tests C1/C2 strong form): reserved frozen rows `<c:…>` in an otherwise normal LM, tied input/output, phrase→concept mapper rewriting training text. Uninterpretable without the **random-frozen control** (the Unicode-glyph result is the pre-registered threat). Experiments E1/E4.
- **A2 — Adapter-bridged kernel** (tests "kernel geometry is informative", the relative-representations-supported weak form): kernel space fixed; one small learned map per model; **shuffled-kernel control** is load-bearing (any full-rank adapter absorbs a rotation). Experiment E5. Most plausible on current evidence; precedented (E-BERT, Frozen, GraphToken, CoLLEGe, LiT).
- **A3 — Kernel-latent LCM** (tests C3): symbolic, genuinely training-free encoder (mapper + explication lookup) → latent transformer over kernel vectors → trained decoder. LCM's own results make this high-risk; toy version only (E3), full version deferred.
- **A4 — Graph-input kernel** (tests the structure claim): explication trees as graph tokens with kernel vectors as fixed node features vs learned features vs flattened text, on compositional-generalisation splits. Phase 2 (E6).
- **A5 — Kernel as external memory + verifier** (weakest, deployable regardless): kNN-LM-style inference-time interpolation toward kernel neighbours (training-free), retrieval cross-attention later; plus the **decode–verify loop**: model emissions decoded against the kernel, checked against explications/world-layer, discrepancies surfaced with provenance. This is where "authoritative" cashes out unconditionally, and it is the piece that composes with sparq/ZK today (verifiable grounding: commit to the kernel snapshot, prove the lookup).

**What we do not claim, anywhere:** that fixing vectors fixes interpretation (C1 strong); that per-model adapters can be eliminated on current evidence; that explication-structural similarity is semantic similarity; that automatic explication authoring works (DeepNSM ≈ 24/100 by its own metric — kernel content is hand-authored, exactly as the concept-hash design already concluded).

## 5. Immediate build plan

1. **Kernel encoder v0** (TypeScript, `@jeswr` scope, on this box): construction B over profile-1 explication records, property-tested (injectivity margins on the corpus, decode-depth behaviour, NOT-flip similarity pathology measured and documented, byte-determinism cross-platform). Novel, standalone-valuable, no GPU needed.
2. **Kernel v0 data**: 65 prime records + the gist's walkthrough concepts (Event, Kind, bookmarks sector) + ~50 NSM-molecule-tier concepts, as profile-1 records (coordinate with PSS's `@jeswr/concept-hash` for minting).
3. **Kill chain on rented T4** (~$10–80 total): E2 → E1 → E4 (+E3/E5), pre-registered in docs/poc-design.md.
4. **Prospectus** to sparq#1683 for SPARQ/PSS review after the panel pass on this document.
