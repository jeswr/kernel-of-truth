# Kernel of Truth — architecture synthesis (rev 2, post-adversarial-panel)

**Status:** design record, 2026-07-07. Rev 2 incorporates the three panel reviews in `../notes/` (`panel-evidence-fidelity.md`, `panel-experiment-rigor.md`, `panel-frontier-skeptic.md`); rev-1 claims corrected by the panel are marked "(rev 2)". Synthesises the five wave-1 reports in `../reports/`; every load-bearing external claim is cited there with primary sources.
**Author:** Kern (Claude Fable 5), for @jeswr. Coordination: [sparq-org/sparq#1683](https://github.com/sparq-org/sparq/issues/1683).
**Honesty contract:** claims are tagged **[established]** / **[claimed]** / **[open]** / **[contradicted]**. Where the maintainer's original hypothesis is contradicted by evidence, this document says so plainly and states the strongest surviving form.

---

## 0. Executive summary

The wave-1 evidence supports a **layered restatement** of the hypothesis. The original strong form — *fixed concept vectors inside an LLM act as built-in ground truth the model can never misunderstand* — is **contradicted** by three independent lines of evidence (§2). But four things survive, and together they still amount to a serious programme:

1. **The kernel object itself is buildable, with scoped novelty** [established feasibility]. A deterministic, training-free explication→vector encoder with quantified capacity guarantees exists as a construction (§1) assembled from published pieces (nearest published artifact: GrapHD's deterministic graph→hypervector encoding with demonstrated reconstruction). (rev 2, novelty scoped:) **No published system uses structure-derived, training-free vectors as an LM's concept vocabulary** — that verdict is the wave-1 reports', "to the limit of several web searches", and the search must be repeated before any external pitch. The identity layer (concept-hash) has a working prototype in the estate (`@jeswr/concept-hash`; gist orchestrator note + §12 — 77 golden vectors).
2. **Frozen concept rows in an LM are mechanically viable** [established] — models train fine around frozen embedding rows; E-BERT-style frozen external vectors with a small learned adapter reached SOTA factual probing. The open question is whether *structure-derived content* buys anything over content-free frozen vectors — untested, and the nearest result (frozen Unicode-glyph embeddings, arXiv:2507.04886) predicts the null.
3. **"Authoritative" survives at the interface, not inside the weights** (§3). Drift-free, content-addressed concept *reference* — with verification, endorsement, and ZK-compatible commitments — is deliverable **after the small named adaptations in reports/sparq-estate.md §6** (hash-keyed rows, encoder provenance in the store header, ordered-clause pooling, Poseidon2 leaf re-target) (rev 2 — previously overstated as "composes today, unconditionally").
4. **The decisive first experiments are cheap, but cheapness is asymmetric** (rev 2): ~$30–80 of GPU time can *kill* the strong claim; it cannot *establish* it. Establishing anything frontier-relevant requires the scale-slope experiment (§5, E7) at ~$2–10k. We say this now so the kill chain is never mistaken for a proof chain.

**Recommended posture:** build the kernel encoder and kernel v0 data now (standalone value); run the kill chain; stage the architecture bets (§4) on its outcome. **Do not approach a frontier lab before E7 (scale slope) exists if the strong claim lives, or E8 (kernel↔SAE alignment) if it dies** — a tiny-scale positive alone is the exact pitch that gets dismissed (panel O1).

## 1. The kernel object (model-independent)

### 1.0 Foundations caveat (rev 2 — was wrongly omitted)

The kernel adopts NSM for its **engineering value, not its scientific claims** [established critiques]: Riemer 2006 shows NSM's own acceptance test (substitutability) is circular and analyst-dependent; von Fintel & Matthewson 2008 find "remarkably few convincing semantic universals" and call the prime inventory's empirical status unproven; Bohnemeyer's Yucatec work is a standing counterexample to prime universality (no lexical exponents of BEFORE/AFTER). What the kernel actually requires from NSM is narrower than NSM's theory: a **small, closed, human-auditable basis with a closed grammar** — not psychological reality, not cross-linguistic universality (though universality would strengthen the world-layer story). Competing bases remain admissible per the mandate; the concept-hash design's prime-set governance (competing prime sets as competing records) is the escape hatch if NSM's inventory shifts.

**Stipulative-definition posture (rev 3, design-review change 5).** The kernel takes no position on the psychology of concepts. Fodor's anti-definitionalism and the prototype/exemplar literature may well be right that most lexical concepts have no discovered definitional structure; kernel explications are **stipulative, endorsed conventions** — engineering artifacts fixing a shared reference meaning — not claims about mental representation. Consequently A5's "meaning-level verification" is scoped: *mechanical* in the formal sectors (dimension checks, canonical-form identity), *structural* in profile-1 (explication-consistency), and *social* for adequacy (endorsement, per the concept-hash design §8).

### 1.1 Three representations per concept

| Layer | Object | Guarantee | Source |
|---|---|---|---|
| **Identity** | `urn:concept:<multihash>` over the definition record (PSS concept-hash design; working prototype `@jeswr/concept-hash` — gist orchestrator note/§12), plus an AHU-canonical-form + homomorphic multiset hash (LtHash-style) for O(1) incremental equality | Cryptographic fixity of reference; collision-resistant injectivity | [established] — reports/deterministic-concept-vectors.md §5.3 for the LtHash math; the gist for the prototype |
| **Geometry** | Canonical vector `v(c) ∈ R^D`, `D ≈ 8k–32k`, from the two-level TPR/VSA encoder (§1.2) | Margin injectivity whp over the capped explication space; similarity = weighted structural overlap; decodability *given the kernel* | [established capacity math; construction assembled from published pieces] |
| **Structure** | The explication tree (profile-1 closed grammar: ≤32 clauses, ≤32 referents, closed inventories) | Ground truth for hashes and vectors; the caps are load-bearing for the capacity bounds | gist §4–§5 |

### 1.2 The encoder (construction B, with C as its proof lens)

From reports/deterministic-concept-vectors.md §7.3:

- **Within a clause:** exact tensor-product binding over an *exactly orthonormal* deterministic codebook (Hadamard/DFT rows) for the ~200 closed atoms. Exact unbinding, zero crosstalk, no seeds, no training.
- **Across clauses/depth:** unitary circular-convolution binding (depth-stable variance) + position permutation + superposition. Concept references bind the *referenced concept's own canonical vector* — compositionality by construction; reference-not-inline keeps the structure budget at `s ≈ 100–200` bound terms.
- **Decoding:** recursive unbinding + nearest-neighbour cleanup against the kernel lexicon itself; resonator networks for multi-factor terms. **Always stated as:** recoverable *given the kernel*, never from the vector alone [established limitation].
- **Formal lens:** the vector is a linear sketch of the explication's WL-subtree feature multiset; compressed-sensing results give the decodability proofs [established].
- **Arithmetic:** capped explications carry ~2–4 kbit of structure; at 0.2–0.5 bits/dim robust capacity, **D ≈ 8k–32k** sits inside every published bound — 16–64 kB per concept fp16, **1.6–6.4 GB** for a 10⁵-concept kernel (rev 2: arithmetic corrected; rev 1 repeated DCV's "3–6 GB", which matches neither endpoint — correction flagged back to the report).

**Known unsolved weaknesses — both stated up front (rev 2 adds the second):**
1. **Polarity/similarity pathology:** provable similarity is *structural overlap*; one deep `NOT` moves the vector ~1/s of its norm while inverting meaning [established]. Mitigations (polarity-aware weighting, canonicalisation above the encoder, relational rather than metric use of similarity) are design work, not solved problems. **No downstream consumer may use raw kernel-cosine similarity until X3's measured pathology numbers are published and a mitigation dominates** (panel O9); this bans naive kernel-kNN in A5 pending X3.
2. **Superposition weighting is a free parameter** that silently determines whether root or leaf differences dominate similarity (the TreeESN suffix-bias lesson in reverse) [established]. It is pinned by content-hash per encoder version (poc-design Common rules) and measured in X3.

### 1.3 The dimension problem (rev 2 — the panel's unanimous top finding)

The capacity math lives at D ≈ 8k–32k; PoC host models have d_model ≈ 256–896. There is no resolution that preserves everything, so the choice is now explicit and pre-registered per experiment (poc-design.md):

- **Toy-native path (E1/E4):** the kernel is *re-encoded natively at D = d_model* for the toy vocabulary. Sphere-packing makes ~10³ concepts comfortably distinguishable at d=512; what is **lost** is the full capacity/decodability story — so E1/E4 test "structure-derived content vs content-free at matched D", *not* the 10⁵-concept capacity claim, and are labelled accordingly.
- **Projection path (E2/E5/E8):** full-D kernel vectors with one **fixed, seeded, published JL projection per (D, d) pair**; the RDM distortion between R^D and R^d is measured and reported for kernel v0, and all margins restated in R^d (X4).
- **A learned projection is architecture A2 by definition** — using one in an A1 experiment silently changes the hypothesis and is forbidden.

At real scale, the honest statement is: a kernel-native vocabulary at D ≈ 8k–32k implies either models with that embedding width, a factorised/projected embedding (with the capacity loss quantified), or concept vectors living in an adapter-mediated side channel (A2/A5). This is an open architecture question, not a solved one.

## 2. The maintainer's four claims against the evidence

**C1 — "can never misunderstand": [contradicted] as stated.** Input embeddings are already static in every transformer; interpretation is constructed downstream (detokenization stages; factual knowledge in mid-layer MLPs; models train around noise/glyph embeddings). **Fixing a vector fixes a symbol, not its meaning.** Surviving form: misunderstanding becomes *detectable and correctable at the interface* (A5 decode–verify) and reference can never drift — accountability, not infallibility.

**C2 — training efficiency: [mostly contradicted].** Embeddings are among the least performance-critical parameters; semantic initialisation washes out; frozen random embeddings can slow convergence 5–10×; knowledge still trains into MLPs. Surviving [open] question: *content-bearing* frozen vectors on concept-heavy distributions — E1, with arXiv:2507.04886 predicting the null.

**C3 — dense concept I/O: [contradicted at scale on current evidence, open at kernel scale].** (rev 2, attribution corrected:) Meta's LCM paper itself **[established]** reports that concept-space autoregression in frozen SONAR space *did not surpass same-size token LLMs* on core English quality, with SONAR-space fragility for long sentences; the specific scaling exponents (~0.49–0.57 vs ~0.79 for token LMs) come from **SONAR-LLM (arXiv:2508.05305), a third-party follow-up, [claimed]** — corroborating, not primary. BLT — the tokenizer-free architecture that works — uses learned dynamic units, the opposite design. Surviving: a *compositional designed* space is a different object from SONAR [open], toy-testable (E3); adapter-mediated dense injection has real lossy wins (xRAG, KBLaM) [established].

**C4 — internal rules-based inference: [speculative].** One unreviewed theory preprint; the KG-injection line was brittle and lost to scaling; superposition/interpretability evidence says concepts in trained nets are distributed, non-orthogonal, learned directions. Reposition: rules run **kernel-side** over explications and world-layer facts with the LM as proposer; whether any inference belongs inside the architecture is deferred until E-series evidence exists.

**Convergence literature (rev 2, tags corrected):** relative representations and model stitching **[established]**, vec2vec **[claimed, replicated once]**, Platonic Representation Hypothesis **[claimed — position paper]** — together they support "one canonical geometry, per-model learned adapters" (A2), NOT shared raw coordinates (A1). **Carried caveat** (previously dropped): in every convergence result, the shared geometry is the *product of training on data* — precisely the resource the kernel proposes to skip. Convergence evidence says learned spaces agree with each other; it does not say they agree with *designed* spaces. That question is exactly E2/E8.

**The update paradox (rev 2 — panel O8, conceded):** since the network learns its interpretation *around* a frozen symbol (C1 evidence), a deployed kernel-native model cannot track kernel revisions by hot-swapping rows: its learned computation is pinned to the training-time kernel snapshot. Kernel versioning therefore works like dependency pinning — models declare their kernel snapshot; revision compatibility is handled at the interface (A5 decode-verify against the current kernel, stale references detected at hash level), never by editing frozen rows in place. This is one more argument that the interface tier, not the vocabulary tier, is the durable product.

## 3. The system stack

1. **Kernel** (small, definitional, abstract): 65 prime records (subject to §1.0's caveat) + sanctioned molecules + explicated concepts; identity hash + explication + canonical vector each; vectors published as signed `(concept-hash → vector)` annotations keyed by **(encoder-version-hash, D, codebook-hash)**. **Scope claim (rev 2 — panel O4):** the kernel covers definitional/abstract/relational vocabulary — the slice where drift, ambiguity and cross-system disagreement are most costly (legal, regulatory, safety, interop) — and does **not** aspire to cover code, mathematics beyond its basis, perceptual description, or named entities. Coverage of real token mass is an open empirical number: measuring it (even crudely) is now a pre-experiment (poc-design M0), as is authoring cost with inter-annotator agreement from a pilot. DeepNSM (~24/100 on its own metric) means authoring stays human [established].
2. **Phrase→concept mapper**: deterministic lemma/multiword lexicon first; learned assist as annotation, never identity. **(rev 2 — panel O3:)** the mapper is the ontology problem reborn (coverage, WSD, maintenance) and sits on E1's critical path; it therefore gets **measured before use** — precision/recall against human annotation, token-mass coverage, ambiguity/abstention rates (poc-design M0) — and E1 exploits TinyStories' semantically clean domain deliberately, where near-exact mapping is achievable by construction.
3. **World layer**: content-addressed, explication-structured assertions over kernel concepts; assumed-true per the mandate's explicit deferral. Mechanically sparq PKG territory after the SPQ §6 adaptations.

## 4. Architecture portfolio (staged bets)

- **A1 — Kernel-native vocabulary** (strong form): frozen concept rows, tied I/O, mapper-rewritten text. Only meaningful with the shuffled-kernel control (rev 2: primary null is now *shuffled*, not random — a random-frozen win could be generic correlated-dictionary benefit). Note the tied-rows tax [established]: tying warps input embeddings toward output geometry, an uncontrolled cost borne specifically by the frozen conditions. Tests: E1/E4.
- **A2 — Adapter-bridged kernel** (weak form, best-supported): kernel space fixed; small learned per-model map; shuffled-kernel control load-bearing. Precedented (E-BERT, Frozen, GraphToken, CoLLEGe, LiT). Tests: E5.
- **A3 — Kernel-latent LCM**: symbolic training-free encoder → latent transformer over kernel vectors → trained decoder. High-risk per LCM evidence; toy only (E3).
- **A4 — Graph-input kernel**: explication trees as graph tokens, kernel vectors as fixed node features. Phase 2 (E6).
- **A5 — Kernel as external memory + verifier** (deployable regardless): decode–verify loop with provenance; kNN interpolation **only after** a polarity-aware similarity variant dominates in X3 (§1.2). **(rev 2 — panel O5:) the deltas over shipped RAG-with-citations, stated precisely:** (i) a citation points at *text*; a concept-hash points at a *versioned, machine-checkable definition* with O(1) equality; (ii) verification against definitions catches meaning-level errors passage retrieval cannot; (iii) ZK-verifiable grounding commitments (prove the lookup without revealing the store). These claims now get their own experiment (E9, phase 2: decode-verify vs vanilla RAG on a factual-consistency benchmark, measuring what each catches that the other misses) — rev 1 had this tier "unconditionally deliverable" with zero experimental support, which the panel rightly flagged.
- **A6 — Kernel↔SAE anchor layer (rev 2 — new, from panel O6):** frontier labs already extract millions of learned interpretable feature directions with sparse autoencoders — per-model, seed-unstable, *unlabeled*, non-compositional, unversioned. The kernel is the exact complement: stable, portable, definitional, versioned, labeled. Proposal: use kernel geometry as a **canonical label/coordinate space for learned features** — align kernel vectors to SAE dictionaries across ≥2 model families; if kernel coordinates predict cross-model feature correspondence beyond shuffled controls (E8), the kernel becomes an interpretability instrument that survives A1's death entirely. Also enables cross-version semantic regression testing ("did v(N+1)'s operational meaning of 'informed consent' move?") — an instrument labs currently lack.

**Two audiences, two pitches (rev 2 — panel O10):** the research pitch (E1/E4/E7/E8 evidence; no governance material) and the assurance/policy pitch (A5 + provenance + EU-AI-Act-shaped documentation; no strong claim). The prospectus will be structured so these can be separated; pitching both at once lands with neither.

**What we do not claim, anywhere:** that fixing vectors fixes interpretation; that per-model adapters can be eliminated; that structural similarity is semantic similarity; that automatic explication authoring works; that tiny-scale positives license scale, cross-model, or cross-lingual claims (the pre-registered scope limits are in poc-design.md).

## 5. Immediate build plan

1. **Kernel encoder v0** (TypeScript, node 22, this box): construction B, property-tested (X0–X4 incl. the adversarial single-edit-neighbour suite), content-hash-versioned.
2. **Kernel v0 data**: 65 prime records + gist walkthrough concepts + ~50 molecule-tier concepts; plus ≥10³ synthetic capped explications (X1 corpus, reused as E4 emission targets per panel O7).
3. **M0 mapper + coverage pre-experiments** (this box): mapper precision/recall/coverage; token-mass kernel-expressibility estimate.
4. **Kill chain on rented T4/A10G** (~$30–80): E2 → E1 → E4 (+E3/E5), as pre-registered in poc-design.md rev 2.
5. **Gate (user decision):** if the strong claim survives → **E7 scale-slope** (15M/160M/~1B, matched tokens, ≥10³ concepts; ~$2–10k) — the only currency the pretraining audience trades in. If it dies → **E8 kernel↔SAE alignment** as the fallback room-mover. Neither is started without explicit maintainer sign-off on budget.
6. **Prospectus** (two-audience structure) to sparq#1683 for SPARQ/PSS review.
