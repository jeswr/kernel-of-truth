# N0 — Current kernel↔LLM seams + broad architecture survey

**Kernel of Truth programme — next-direction seed, node N0.**
Author: Kern (Fable design agent). Date: 2026-07-08.
Status: **DESIGN/PLANNING document.** No new empirical claims are made here; every
empirical statement below either quotes the registry/verdict record verbatim-in-substance
or carries a literature citation. Nothing in this document amends any FROZEN registry
entry; every proposed fork must pass through `prereg-freeze` before anything runs
(directives §3). Binding constraints: `docs/kernel-design-directives.md` (esp. §1
no-semantic-web-legacy, §2 two value theses, §4 don't-guess-test, §6 honest stats).
Primary literature substrate: `reports/lit-llm-injection-priorart.md` (L3; verified
2026-07-08) and its companions; citations new to this document are tagged
**[search]** (live web verification, 2026-07-08) or **[memory]** (author training
knowledge, pre-2026 established work); untagged citations are carried from the repo's
verified L3/L1/L2 reports.

Purpose: (§1) state precisely and honestly how the kernel currently interacts with the
LLM — correcting the "it's just RAG" framing in both directions; (§2) survey the ML
architecture space relevant to making a symbolic kernel **more central to inference**,
by mechanism; (§3) the structured map; (§4) candidate forks for pillars A/B/C with kill
criteria; (§5) the constraint checklist any new seam must satisfy.

---

## 1. How the kernel currently touches the LLM — the honest statement

### 1.1 Correcting "just RAG" — in both directions

The claim "the kernel is just RAG" is wrong on the current evidence, twice over:

1. **A2 is in the network, not in the context window.** The A2 seam injects the
   deterministic kernel vector through a **trained affine adapter into the model's input
   stream as a soft token** — a continuous vector the frozen host consumes directly, not
   text retrieved into the prompt. It is precedented by the trained-bridge family
   (E-BERT, soft prompts, GraphToken, xRAG, KBLaM — L3 §1), and it has a real,
   pre-registered, replicated positive result (E5, §1.2 below). RAG has no trained
   component touching the model and delivers text; A2 has exactly one trained component
   (the adapter) and delivers geometry. What stays deterministic and training-free is the
   kernel vector itself; what is learned is only the per-model bridge.
2. **The verifier seam is not passage retrieval.** F2/E9's loop is: model generates →
   output extracted to a **machine-checkable record** (the P10 interface) → **deterministic
   decode-verify against canonical, content-addressed definitions and the endorsed axiom
   sidecar** → structured error → retry. A RAG citation points at *text*; a concept-hash
   points at a *versioned definition* with O(1) equality and fail-closed validation
   (architecture.md §A5). Retrieval finds passages that might be relevant; the verifier
   *checks* a claim against a closed formal object and can say *no*. Topologically it is
   tool-in-the-loop (external, Law-3 shape), but its instrument is a deterministic
   checker, not a similarity search.

And the honesty cut in the other direction: **nothing measured yet shows end-task benefit
of either seam over the kernel-as-text null.** E5 shows content transfer through the
adapter, not task value; the verifier seam's value is exactly what the currently-running
F2 pivot and the E9 family exist to decide, against mandatory strong text baselines
(including gloss-text self-verify+retry at matched budget — the arm Law 2 predicts wins).
Until those verdicts land, the defensible sentence is: *the kernel has one supported
in-network injection cell (A2, one rung, content-transfer only), one deployable external
verifier seam under active test, and a store/coverage substrate with two audited Tier-0
passes — and zero demonstrated end-task wins over text.*

### 1.2 Seam-by-seam ledger

| Seam | Mechanism | In/out of network | Trained parts | Evidence (registry/verdict record) | Status |
|---|---|---|---|---|---|
| **A2 adapter** | kernel vector → trained affine adapter → soft token into frozen host | **IN** (input stream) | adapter only | **E5 PASS**: adapter transfers kernel content to *unseen nonce concepts*, +28.5 pp over shuffled-kernel control, p<1e-6, 5/5 seeds, SmolLM2-135M. **E9-defl PASS**: structure-preserving semantic scramble recovers only ~8.2% of the E5 effect — the effect is **content, not format**. **E2 PASS** (correlational RSA hook, 3/3 families). | **Supported — narrowly.** One rung (R1, 135M); nonce-concept usage metric; no end-task-vs-text-null verdict (that is F4/HE4, Tier 2 DRAFT). |
| **Verifier seam (A5)** | generate → P10 extraction → deterministic decode-verify vs canonical records + axiom sidecar → retry | **OUT** (external engine, Law-3 topology) | none (deterministic checker; PRM comparator arm is off-the-shelf) | **F2 FROZEN 2026-07-08** (sha `28874f2b…`), Tier-1 pivot **running now** (Modal, ≤$60 under the $80 cap; SmolLM2 135M/360M/1.7B; 500 items/arm; 6 mandatory baseline arms incl. gloss-text self-verify+retry and a matched-FLOPs small PRM). Decides HE1 (verifier-offload buys parameters), HE2 (cascade), HC3 (deterministic verifier vs trained PRM), HS12 (placement). | **No verdict yet. Zero claims.** The programme's make-or-break. |
| **A1 frozen vocabulary** | kernel vectors as native frozen model I/O rows | IN (embedding table) | none — that is the point | **E1 INCONCLUSIVE** (kernel-frozen ≯ shuffled at the pre-registered look; TOST could not bound it either). **E4 MOCK-only** (no real-run emission verdict; literature prior is a null). L3 §1: the "hand-set vectors, zero trained interface" cell is empty across the literature **[established as absence]**. | **UNSUPPORTED.** Retained only as gated cheap falsification (HS13); a learned projection inside an A1 experiment is forbidden (it silently becomes A2). |
| **A6 kernel↔SAE label space** | kernel as canonical, versioned label/coordinate system for learned SAE features | OUT (instrument over model internals) | SAEs are trained (by others); alignment map is the experiment | **E8 PASS on 1 family pair + NOT-REPLICATED on the 3rd** — named site confound (MLP-output vs residual-stream SAE). e8-d/e8-r Tier-2 DRAFT with ground-truth design per RT-10. | **Live, unresolved.** The 2025 SAE correction (absorption, seed non-identifiability, non-canonicity — L3 §5) is the opening; the GDM bar (beat a simple baseline on a downstream task) is the acceptance test. |
| **Store / substrate (M4)** | content-addressed canonical record store; retrieval by hash, not similarity | OUT | none | **f1 PASS**: byte ratio **6.74×** vs best general-purpose-compressed gloss-text store (primary endpoint ≥2×), audit **CONFIRMED** cross-vendor (Codex/GPT-5.5, `registry/audits/f1/`) — scope: lexical-wn31 (117,791 records) at rung S1e5 ONLY, `scale_language_licensed:"none"`; store-size-conditional (upward-only on the same corpus process; contradicted at the 2,348-record haiku tier by measured table+header overhead, `docs/design-compact-kernel-serialization-v2.md` §3.3, f-efficiency D1); quoting 6.74× at any other tier/corpus is EXTRAPOLATION. **m0b coverage gate PASS** (audited; corpus-scoped: 0.3542 at rung molecules-v0 on the pinned TinyStories task family, measured on the incomplete kernel-v0+molecules-v0 instance of 2026-07-08 — per the verdict envelope it extrapolates to NO other corpus, rung, or kernel state; ASM-0001). | **Supported, model-free.** Decides the byte premise only; accuracy leg (F5) is double-gated Tier 4. |

**Inherited instrument constraints that bind every seam design below:**

- **X3 FAIL → cosine ban.** Raw kernel-cosine similarity is banned downstream: provable
  similarity is *structural overlap*; one deep NOT moves the vector ~1/s of its norm while
  inverting meaning. No naive kernel-kNN anywhere until a polarity-aware variant dominates.
- **X2 51/54 decode** was measured on *encoder-produced* vectors, never on model outputs —
  the P10 extraction interface is part of any system under test, with its own
  instrument-invalid gate (extraction-failure Wilson-LB > 10%).
- **X4**: JL projection 8192→512/576 preserves RDM structure (Spearman ≈0.97) — the
  projected path into small models is instrument-validated.
- **X1**: adversarial single-edit margins ~11× above the decision floor — identity is
  robust at the vector level; **X0** byte-determinism holds.

### 1.3 Supported vs not — the one-screen ledger

Empirically supported today (pre-registered, audited where required):
- Deterministic identity/margins/projection of the kernel vector space (X0/X1/X4).
- Coverage of the **pinned TinyStories task-family corpus** by the kernel+molecule
  tier as of 2026-07-08: 0.3542 at rung molecules-v0 (0.2210 at kernel-v0) of the
  **incomplete** kernel-v0+molecules-v0 instance (m0b, audited). Corpus-, rung-, and
  kernel-state-indexed — it extrapolates to no other corpus or rung (verdict envelope,
  verbatim) and says nothing about "eval-relevant content" in general; any new eval
  corpus needs its own census (register entries ASM-0001/ASM-0002).
- 6.7× byte advantage of the canonical store over compressed gloss text (f1, audited).
- Kernel *content* crosses a trained adapter into a frozen 135M host and transfers to
  unseen concepts; the effect is destroyed by semantic scramble (E5 + E9-defl, 5 seeds).
- Designed kernel geometry correlates with learned representational geometry above
  relatedness baselines (E2, correlational).
- One kernel↔SAE alignment family pair (E8, unreplicated on the third — site confound).

Not supported (and currently claimed by no programme document):
- Any end-task accuracy/correctness win over the kernel-as-text null (F2/E9/F4 pending).
- Any efficiency win involving a model (F1 is model-free bytes; HE1–HE6 pending).
- A1 in any form (frozen rows, native emission).
- Any similarity-based use of kernel vectors (X3 ban).
- Any claim above the measured rungs (scale-language license: none yet beyond R1/Tier-0).

### 1.4 The standing laws any new seam must respect

From the verified literature record (L3) and the directives — these are the design
boundary conditions for §§2–4:

1. **Interface-locality law** (L3 §3): what crosses into a model is text re-encoded by the
   model, the model's own activations, or vectors through a **trained** bridge. The
   raw-foreign-coordinates cell is empty. New seams must sit in a supported cell or be
   explicitly budgeted as falsifications.
2. **Law 2 — the text null is the real opponent**: as hosts strengthen, the text interface
   improves automatically; every mechanism must beat *its own content rendered as text*
   at matched budget, or it is dead regardless of its elegance.
3. **Absorption expectation** (InstructRetro; vocabulary wash-out): even successful
   injected/external structure tends to migrate into weights and become removable. Frame
   claims as training/inference **efficiency** and **auditability**, never "permanent
   residence".
4. **Law 3 — the winning topology**: neural proposer ↔ formal language ↔ deterministic
   external engine that owns correctness (AlphaGeometry, Logic-LM). The kernel's strongest
   seat is the engine seat.
5. **Directives §1**: no RDF/OWL/SHACL/DL semantics anywhere in a proposed mechanism;
   native `kot-axiom/1` formalism only; semantic-web renderings are lossy exports.
6. **Directives §2 + F0 accounting**: every proposal must be evaluable on the full metric
   vector V (accuracy, params, memory, inference compute, training compute, authoring
   cost) against strong baselines.
7. **X3 cosine ban** (§1.2 above) — any mechanism whose load-bearing step is "nearest
   kernel vector by cosine" is unbuildable as designed until the mitigation fork lands.

---

## 2. Survey — architectures for making a symbolic kernel more central to inference

Each line: *what it does* → *maturity* → *how a content-addressed NSM kernel could plug
in* (+ nearest programme hook). Four mechanism families: **NS** (neurosymbolic), **IN**
(in-network injection/retrieval), **CN** (concept-level I/O, tokenisation, normalisation,
regularisation), **RL** (internal rules-engine / symbolic lookup at inference).

### 2.1 Family NS — neurosymbolic architectures

**NS-1. Differentiable proving / neural theorem provers.** NTP (Rocktäschel & Riedel,
NeurIPS 2017, arXiv:1705.11040) **[memory]** backward-chains Prolog-style proofs where
symbol unification is replaced by embedding similarity, end-to-end differentiable;
Conditional Theorem Provers (arXiv:2007.06477) **[memory]** learn to select rules.
*Maturity:* research-grade; never scaled beyond small KBs (proof-tree blow-up); largely
dormant post-2021 in favour of LLM+solver pipelines. *Kernel plug-in:* the kernel is on
paper an ideal NTP symbol space (canonical vectors, compositional structure) — **but the
load-bearing operation is soft unification by similarity, which the X3 cosine ban
currently forbids** for kernel vectors. Only viable behind a polarity-aware similarity
fork; otherwise use the kernel on the discrete side (exact unification by hash) and let
the neural part be the proposer. *Hook:* none today; blocked-on-X3-mitigation.

**NS-2. Probabilistic-logic hybrids with neural predicates.** DeepProbLog (Manhaeve et
al., NeurIPS 2018, arXiv:1805.10872) **[memory]**: ProbLog programs whose predicates are
neural nets; exact weighted model counting makes inference prohibitively expensive at
scale. Scallop (Li et al., PLDI 2023, arXiv:2304.04812) **[memory]**: Datalog with
provenance semirings, tunable approximation, PyTorch-integrated — the scalable successor;
CTSketch (NeurIPS 2025) **[search]** pushes scalability further via compositional tensor
sketching. The reasoning-shortcut literature (arXiv:2507.11357) **[search]** documents how
these systems satisfy constraints via unintended concept assignments — the leakage failure
mode. *Maturity:* real, maintained frameworks; used at module scale, not LM scale.
*Kernel plug-in:* the **axiom sidecar (`kot-axiom/1`, stratum 3) is exactly the logic
program** such a layer executes: kernel concepts as ground terms (content-addressed —
identity is exact, no learned unification needed), sidecar axioms as rules, model outputs
(via P10 extraction) as the neural predicates' evidence. Two uses: (i) *inference-time*:
a Scallop-style engine as a richer verifier than record-equality — this is a **deepening
of the existing F2/A5 seam**, not a new seam; (ii) *training-time*: differentiable
relaxation of sidecar checks as a loss (see NS-3/CN-4). *Hook:* HC2 (sidecar catches what
text cannot), F6 (scaffolded training). Directives §1 note: Scallop is Datalog-flavoured
engineering machinery, not semantic-web semantics; adopting the *engine style* while
keeping `kot-axiom/1` semantics native is compliant.

**NS-3. Logic-as-regulariser.** Logic Tensor Networks (Badreddine et al., AIJ 2022,
arXiv:2012.13635) **[memory]** compile first-order axioms into fuzzy-logic losses;
Semantic Loss (Xu et al., ICML 2018, arXiv:1711.11157) **[memory]** does the same for
propositional constraints via weighted model counting. *Maturity:* established at
small/module scale; standard tools in the NeSy community; not demonstrated at LLM
pretraining scale. *Kernel plug-in:* render endorsed sidecar axioms as differentiable
penalties during **adapter training (A2/F4) or small-model distillation (F6)** — the
kernel stays out of the network, but its axioms shape the training signal. Cheap,
precedented, and composable with any other seam. *Hook:* new fork N-C2 (§4).

**NS-4. Kolmogorov–Arnold Networks.** KAN (arXiv:2404.19756, ICLR 2025) **[search]**:
learnable spline activations on edges, claimed better scaling and interpretability. The
2025–26 record corrected hard: a systematic critical assessment (arXiv:2407.11075)
**[search]** finds KANs win **only on symbolic-regression-style tasks**, underperform
MLPs across ML/CV/NLP, the advantage traces to B-spline activations rather than the
architecture, and compute overhead is 1.36–100×. *Maturity:* hype-corrected niche.
*Kernel plug-in:* none load-bearing. Recorded to close the survey loop honestly: KANs
solve "learn a readable function", not "give concepts canonical identity" — orthogonal to
the kernel's problem. *Hook:* none; deliberate non-adoption.

**NS-5. Concept-bottleneck models — the closest architectural template.** CBM (Koh et
al., ICML 2020, arXiv:2007.04612) **[memory]**: force prediction through a layer of
named, human-interpretable concepts; Concept Embedding Models (arXiv:2209.09056)
**[memory]** fix the accuracy tax; the known failure is **concept leakage** (unintended
information smuggled through the bottleneck). **CB-LLM (arXiv:2412.07992, ICLR 2025)
[search]** scales the idea to LLMs for classification *and generation*: interpretable
concept neurons enable concept detection, steering, and unlearning at competitive
accuracy — the first CBM at LLM scale. Adjacent: Bayesian CBMs with LLM-generated concept
priors (arXiv:2410.15555) **[search]**; Chat-CBM interactive bottlenecks over frozen LLMs
(arXiv:2509.17522) **[search]**. *Maturity:* moving fast; generation-side CB-LLM is one
group's ICLR 2025 result, not yet a replicated standard. *Kernel plug-in:* CB-LLMs
currently source their concept vocabulary from ad-hoc LLM-generated lists — unversioned,
unvalidated, no identity. The kernel is a drop-in **canonical concept vocabulary for the
bottleneck**: a head or adapter whose units are pinned 1:1 to kernel concept hashes
(definitions versioned, coverage measured by m0b machinery, labels free). This *merges
the A2 and A6 seams*: an in-network layer whose coordinates are kernel-labelled is
simultaneously an injection site and an interpretability instrument, and — unlike
post-hoc SAEs — its unit identities cannot drift across seeds (they are pinned by
construction; what varies is only how well the host uses them). Leakage is the known
failure mode and must be measured (the E9-defl scramble discipline transfers directly).
*Hook:* new fork N-A1 (§4); complements e8-d/e8-r rather than replacing them.

**NS-6. Neural author + deterministic external engine.** Logic-LM (arXiv:2305.12295),
LINC (EMNLP 2023), AlphaGeometry (Nature 2024), AlphaProof (2024); "Intermediate
Languages Matter" (arXiv:2502.17216) shows the formal language choice is a first-class
variable. *Maturity:* **the** established neurosymbolic success template (L3 §6).
*Kernel plug-in:* already adopted — this is the F2/A5 topology; the survey's marginal
additions are (i) feed the validator's fail-closed ERR_* codes back as structured
refinement signals (the measured +18–39% pattern), (ii) treat explication-profile choice
as an experimental variable via the AST profile system. *Hook:* F2 (running), E9-full.

### 2.2 Family IN — in-network knowledge injection & retrieval-in-the-network

**IN-1. Trained-bridge input injection (the supported cell).** Soft prompts
(arXiv:2104.08691), LoRA (arXiv:2106.09685) **[memory]**, ToolkenGPT (arXiv:2305.11554),
GraphToken (arXiv:2402.05862), xRAG (arXiv:2405.13792), KBLaM (arXiv:2410.10450), E-BERT.
*Maturity:* established; quantified fidelity ceiling (xRAG retains ~62–73% of text's
capability). *Kernel plug-in:* **this is A2**, already held with E5. The natural
extensions, in supported territory: (i) **concept-toolkens** — ~10³ new vocabulary items
whose embeddings are *frozen kernel-derived* vectors with only one shared adapter trained
(ToolkenGPT inverted; L3 §9's cheapest unrun A2 experiment); (ii) scaling F4/HE4 (dense
concept input vs full-text definitions at matched budget — the token-efficiency framing).
*Hook:* F4 (Tier 2, DRAFT), HE3/F3 dense-I/O.

**IN-2. Model-key-addressed external memory.** kNN-LM (arXiv:1911.00172), Memorizing
Transformers (arXiv:2203.08913), RETRO (arXiv:2112.04426), with the InstructRetro
absorption caveat (arXiv:2310.07713). *Maturity:* established. *Kernel plug-in:* kernel
**values addressed by model-native keys** — the model's own hidden state selects which
canonical record to consult; the kernel never imposes its coordinates on the model, only
the *payload* is canonical. Two concrete shapes: KBLaM-style rectangular attention over
(model-key, kernel-record-value) pairs; or RETRO-style chunked cross-attention where the
retrieved "neighbour" is the canonical record rendered per P10. Constraints: any
similarity step happens in *model* space (X3-compliant by construction); expect
absorption — frame as inference-efficiency and update-freshness (the store can change
under a fixed model; that is the A5 update story, architecture.md §"update paradox").
*Hook:* F5 accuracy leg (Tier 4, double-gated); HE5.

**IN-3. Trainable in-network memory layers — the strongest new evidence line.** Memory
Layers at Scale (Meta FAIR, arXiv:2412.09764) **[search]**: product-key trainable
key-value lookup layers replacing FFNs, scaled to 128B memory parameters / 1T tokens;
at matched FLOPs they beat dense and MoE baselines **most strongly on factual QA**. PEER
(arXiv:2407.04153) **[search/memory]** bridges memory layers and MoE with a million
rank-one experts; UltraMem (arXiv:2411.12364) and **UltraMemV2 (arXiv:2508.18756,
120B-parameter regime, parity with 8-expert MoE at far lower memory access) [search]**
make the line industrial. *Maturity:* now a serious production-architecture contender —
this is the literature's clearest statement that **explicit sparse lookup inside the
network wins for knowledge-heavy computation at matched compute**. Everything — keys,
values, routing — is learned. *Kernel plug-in (the survey's most concrete new
architecture):* a **kernel-addressed memory layer** — keep the memory-layer machinery,
but pin (a fraction of) the **key table** to kernel concept identities (X4-projected
kernel vectors, or hash-derived codes), values remain learned. What this buys if it
works: per-token, per-concept **attribution** (which canonical concept's slot fired — an
audit surface no learned memory has), **versioned editability** (concept's value row is
an addressable object; knowledge editing becomes a store write, cf. the ripple-failure
literature), and a bridge to the store thesis (the same content-addresses index the
external store and the in-network memory). The risk is exactly the frozen-embedding
precedent: pinned keys may cost accuracy vs learned keys — this is a *fork to test, not
a design to defend* (N-B1, §4; shuffled-kernel-keys control mandatory). *Hook:* new —
no current experiment covers the inside-the-FFN lookup cell.

**IN-4. Generative retrieval / semantic IDs.** DSI (arXiv:2202.06991) **[memory]**:
the model memorises a corpus and *emits document identifiers*; semantically-structured
docids help. *Maturity:* established in IR; known index-update brittleness. *Kernel
plug-in:* training a model to **emit concept hashes** is the E4/A1-emission shape; DSI
works because docids are trained *into* the model — which is precisely the
training-dependence the kernel wants to avoid, and the literature prior for zero-exposure
emission is a null. Keep as the labelled caution it already is (E4 MOCK-only). *Hook:*
E4, unfunded; HS13 gate.

### 2.3 Family CN — concept-level I/O, tokenisation/normalisation, regularisation

**CN-1. Concept-level prediction.** LCM + SONAR (arXiv:2412.08821) **[memory]**;
SONAR-LLM exponent measurements; **CALM (arXiv:2510.27688)**: next-vector prediction over
a *learned autoencoder latent* compressing K tokens — the concept-step efficiency win
recovered by **dropping** the fixed semantic space (L3 §4's controlled natural
experiment). *Maturity:* CALM is recent, unreplicated; LCM line dormant. *Kernel
plug-in:* the one untested middle path (L3 §9): a **CALM-style learned latent softly
regularised toward kernel coordinates** — regulariser, not target; the latent stays
learned and reconstruction-optimised, the kernel contributes a *pull* toward canonical
axes for covered concepts. If the regulariser can be dialled up without re-inheriting the
LCM scaling penalty, the result is a semi-canonical latent lane (partially auditable
step-space). *Hook:* new fork N-C1 (§4); scale-exponent kill criterion is mandatory
(directives §6: LCM/CALM is a named scaling-law comparison family in P8).

**CN-2. Tokenizer-free / byte-latent models.** ByT5 (arXiv:2105.13626), MEGABYTE
(arXiv:2305.07185), BLT (arXiv:2412.09871). *Maturity:* established to 8B. *Kernel
plug-in — honestly: this line argues against the kernel-as-unit.* Every successful
tokenizer replacement made the latent unit smaller, learned, dynamic, content-agnostic —
the opposite direction from fixed semantic units. Recorded as a boundary condition: the
kernel should not compete for the *unit-of-computation* seat; its seats are the engine,
the address space, and the label space. *Hook:* none; deliberate non-adoption.

**CN-3. Input canonicalisation / normalisation (the cheapest open seam).** The 2025–26
robustness literature quantifies LLM brittleness under meaning-preserving input change:
paraphrase and format perturbations degrade task accuracy by up to ~33%, larger models
only marginally more robust (Brittlebench, arXiv:2603.13285 **[search]**; segment-level
perturbation analysis arXiv:2605.01605 **[search]**; enterprise perturbation-consistency
benchmarks arXiv:2601.06341 **[search]**); training-side mitigation exists (Flip-Flop
Consistency, arXiv:2510.14242 **[search]**) but inference-side *canonicalisation* of
inputs is essentially unstudied beyond prompt compression (LLMLingua, arXiv:2310.05736
**[memory]**; gist tokens, arXiv:2304.08467 **[memory]**), which optimises tokens, not
meaning. *Kernel plug-in:* the programme already owns a deterministic **phrase→concept
mapper** (`mapper/`, Phase M: longest-match lexicon, rule lemmatiser, abstain-and-record
ambiguity policy with measured abstention rates, `a1-hybrid` preset signed 2026-07-07).
A **kernel input canonicaliser** rewrites/annotates input so that kernel-covered content
reaches the model in one canonical surface form (or with concept-hash annotations):
training-free, fully external, deterministic, and measurable as **variance reduction
across paraphrase suites** at matched accuracy. The honest null is strong: an LLM asked
to "rewrite this in plain canonical English" is the text-side normaliser the kernel must
beat, and abstention-rate coverage bounds apply. *Hook:* new fork N-C3 (§4) — the
cheapest new experiment in this survey (R0/R1, existing mapper, public perturbation
benchmarks).

**CN-4. Representation-space regularisation.** Relative representations
(arXiv:2209.15430) and the convergence literature (repo-carried); semantic loss / LTN as
training penalties (NS-3); the platonic-representation position (arXiv:2405.07987)
**[memory]**. *Maturity:* established techniques, position-paper theory. *Kernel
plug-in:* use the **kernel RDM/Gram structure as an anchor loss** during distillation or
small-model training — "make the student's concept geometry agree with the kernel's
*relational* structure" (RDM-level, not coordinate-level — X3-compliant because it uses
the whole Gram structure relationally, the E2 instrument). This is the training-time
sibling of A2 and the mechanism most likely to move the F6 scaffolding hypothesis from
its current literature-prior-null. *Hook:* F6 (HE6, Tier 3 DRAFT) — proposes an arm, not
a new experiment; and N-C2 (§4) for the adapter-training variant.

### 2.4 Family RL — internal rules-engine / symbolic-lookup inference

**RL-1. Mixture-of-experts routing.** Switch (arXiv:2101.03961) **[memory]**, DeepSeekMoE
(arXiv:2401.06066) **[memory]**, OLMoE (arXiv:2409.02060) **[memory]**; 2025–26
interpretability of experts: expert-level knowledge localisation via cross-lingual
inconsistency (arXiv:2603.17102 **[search]**), expert-aware causal tracing of factual
recall (arXiv:2606.03780 **[search]**), expert-level interpretation finding experts that
specialise in structured key-value associations (name→birthplace, country→capital;
arXiv:2604.02178 **[search]**), and theoretical task-routing models (arXiv:2606.14398
**[search]**). *Maturity:* MoE is production; expert-level *semantics* of routing is a
young, active research front — routing is known to be substantially token-identity-driven
at lower layers, with semantic specialisation emerging in stronger reasoning models
**[search]**. *Kernel plug-in:* two rungs. Near-term, defensible: **the kernel as the
label/probe space for expert specialisation** — the A6 instrument pointed at MoE experts
instead of SAE features (do experts cluster on kernel concepts? does a concept's expert
set predict cross-model correspondence beyond shuffled controls?). The same 2025 need
the SAE correction exposed (no stable labels, no versioning) exists for experts.
Speculative, consumer-side (Law-1 warning): **concept-conditioned routing** — a routing
prior from mapper-detected concept ids; this modifies the host and every precedent says
learned routing wins; instrument-first is the right order. *Hook:* new fork N-B2 (§4),
sibling of e8-d/e8-r.

**RL-2. Cheap lookup vs neural reasoning — the division-of-labour evidence.** Memory
layers' factual-QA-dominant gains (IN-3) **[search]**, kNN-LM's rare-fact wins, retrieval
heads (arXiv:2404.15574) **[memory]**: the literature increasingly supports "facts want
lookup; reasoning wants weights". *Kernel plug-in:* this is the **store thesis** the
programme already holds (F1 PASS on bytes; F5 to decide accuracy) — the kernel's
content-addressed store as the lookup half, models sized for the reasoning half. The
survey's addition: IN-3 shows the lookup half can live *inside* the network too, which is
what N-B1 tests. *Hook:* F5/HE5; N-B1.

**RL-3. Tool-in-the-loop and test-time verification.** Toolformer (arXiv:2302.04761)
**[memory]**, PAL (arXiv:2211.10435) **[memory]**, Logic-LM (NS-6); trained process
reward models ("Let's Verify Step by Step", arXiv:2305.20050 **[memory]**); the
self-verification caution (self-refine/CoVe lineage — the reason F2 carries the
gloss-self-verify arm); speculative decoding (arXiv:2211.17192 **[memory]**) as the
draft→verify→accept template. *Maturity:* established; test-time verification is the
dominant current paradigm for correctness. *Kernel plug-in:* **this is the F2 seam.** The
open literature cell the programme already owns is HC3: *deterministic* verifier vs
*trained* PRM at matched inference FLOPs — no published result covers a
content-addressed definitional verifier in the PRM seat. The cascade variant (HE2:
kernel verifier as accept/reject gate on a small model's drafts, escalate on reject) is
speculative decoding with a deterministic semantic acceptor. *Hook:* F2 (running) —
no new design needed; this family is where the kernel is *already* most central.

---

## 3. The structured map — mechanism × kernel-plug-in

| # | Mechanism | What crosses the model boundary | Trained interface? | Maturity | How the content-addressed NSM kernel plugs in | Programme hook | Supported-cell? / chief risk |
|---|---|---|---|---|---|---|---|
| NS-1 | Differentiable proving (NTP/CTP) | similarity-mediated unification | yes (embeddings) | dormant research | kernel as unification symbol space | none | **Blocked by X3 cosine ban**; scaling record poor |
| NS-2 | Probabilistic-logic engines (DeepProbLog/Scallop) | logic-program evidence | per-predicate nets | frameworks, module-scale | axiom sidecar as the program; richer F2 verifier; training signal | HC2, F6 | Supported as *external engine*; reasoning-shortcut leakage if trained-through |
| NS-3 | Logic-as-regulariser (LTN/semantic loss) | loss gradients only | yes (the trained model) | established, small scale | sidecar axioms as differentiable penalties in adapter/distill training | N-C2, F6 arm | Supported cell (training-side); effect size unknown |
| NS-4 | KANs | — | — | hype-corrected niche | none load-bearing | none | Deliberate non-adoption |
| NS-5 | Concept-bottleneck models (CB-LLM) | activations through named-concept layer | yes (bottleneck head) | LLM-scale since ICLR 2025 | kernel = canonical, versioned bottleneck vocabulary (merges A2+A6) | N-A1; e8 siblings | Promising; **concept leakage** is the failure mode |
| NS-6 | Neural author + deterministic engine | formal records + error codes (text) | no | **the** established NeSy template | kernel = the engine (validate/canonicalise/verify) | **F2 (running)**, E9 | Supported topology; value vs text-null is exactly what F2 decides |
| IN-1 | Trained-bridge injection (soft prompt/toolken/projector) | vectors via trained bridge | yes (small) | established | **A2 as held**; concept-toolkens with frozen kernel embeddings | E5 (PASS), F4, F3 | Supported (1 rung); fidelity ceiling ~62–73% (xRAG) |
| IN-2 | Model-key-addressed memory (kNN-LM/RETRO/KBLaM shape) | model's own keys; kernel payloads | small (cross-attn/projector) | established | kernel **values** addressed by model-native keys | F5/HE5 | Supported shape; absorption expectation |
| IN-3 | In-network memory layers (product-key/PEER/UltraMem) | nothing external — lookup layer inside FFN | yes (keys+values today) | industrial since 2025 | **kernel-addressed memory layer**: keys pinned to concept identities, values learned | **N-B1 (new)** | Empty cell worth testing; frozen-key penalty risk |
| IN-4 | Generative retrieval / semantic IDs (DSI) | emitted identifiers | yes (trained-in) | established (IR) | concept-hash emission | E4 (MOCK), HS13 | Literature prior null; caution label stands |
| CN-1 | Concept-level prediction (LCM→CALM) | learned latent per K tokens | yes | CALM recent | latent **regularised toward** kernel coordinates (not targeted) | **N-C1 (new)** | Must not re-inherit LCM exponent penalty |
| CN-2 | Byte-latent / tokenizer-free | bytes/dynamic patches | yes | established to 8B | none — boundary condition against kernel-as-unit | none | Deliberate non-adoption |
| CN-3 | Input canonicalisation | canonicalised **text** | **no** | unstudied gap (2025–26 brittleness record) | mapper-based kernel canonicaliser; variance-reduction claim | **N-C3 (new)** | Cheapest seam; must beat LLM-paraphrase null; abstention coverage bound |
| CN-4 | Representation regularisation (RDM anchors) | loss gradients only | yes (student) | established technique | kernel Gram/RDM as relational anchor in distillation | F6 arm, N-C2 | X3-compliant (relational); F6 prior is null |
| RL-1 | MoE routing | internal dispatch | yes | production; interp young | kernel as expert-label/probe space (instrument-first); concept-routing later | **N-B2 (new)** | Consumer-side routing change is Law-1-exposed; instrument is safe |
| RL-2 | Lookup-vs-reasoning split | store records | no | strengthening (memory-layer evidence) | content-addressed store as the lookup half | F1 (PASS), F5 | Accuracy leg undecided (Tier 4) |
| RL-3 | Tool-in-loop / test-time verification | records + retries (text) | no (PRM arm trained, off-shelf) | dominant paradigm | **kernel verifier in the PRM seat; deterministic acceptor in cascades** | **F2 (running)**, HC3, HE2 | The kernel's most central current seat |

Reading the map for the pillars: the kernel's *defensible centrality* today is entirely
in the **no-trained-interface rows** (NS-6, RL-2, RL-3, CN-3) plus the one supported
trained-bridge row (IN-1/A2). The genuinely new, empty-but-motivated cells this survey
adds are **IN-3 keys-pinned memory layers (N-B1)**, **NS-5 kernel-labelled bottleneck
(N-A1)**, **CN-1 kernel-regularised CALM latent (N-C1)**, **CN-3 input canonicaliser
(N-C3)**, with **NS-3/CN-4 regularisers (N-C2)** and **RL-1 expert labelling (N-B2)** as
low-cost riders.

---

## 4. Candidate forks (directives §4 form) — seeds for pillars A/B/C

All are DESIGN-STAGE. None is pre-registered; none may run before `prereg-freeze` with
full statistical plans (P8) and text-null arms. Ordering within each pillar is
cheapest-decisive-first. Every fork inherits §1.4's laws; every efficiency-relevant fork
reports the full vector V including authoring cost.

**N-A1 — kernel-labelled concept-bottleneck head (pillar A: correctness/interpretability).**
*Options:* (a) bottleneck adapter head over a frozen host with units pinned to kernel
concepts (CB-LLM recipe, kernel vocabulary); (b) post-hoc probe-only variant (no
bottleneck in the generation path). *Why uncertain:* CB-LLM shows LLM-scale viability
but with ad-hoc vocabularies; nobody has used a canonical, versioned vocabulary; leakage
may fake interpretability. *Deciding experiment:* nonce+covered-concept steering and
detection vs (i) CB-LLM with LLM-generated vocabulary of matched size, (ii)
shuffled-kernel labels, (iii) SAE-feature baseline (e8 machinery), with an E9-defl-style
scramble arm to measure leakage. *Kill:* kernel-labelled bottleneck ≤ ad-hoc-vocabulary
CB-LLM on detection/steering (TOST, pre-declared margin), or scramble arm recovers most
of the effect (leakage). *Cost class:* Tier 2-like (small host, adapter training).

**N-B1 — kernel-addressed in-network memory layer (pillar B: efficiency/centrality).**
*Options:* (a) fraction of product-key memory keys pinned to X4-projected kernel vectors,
values learned; (b) hash-derived discrete addressing (no geometry, pure content-address);
(c) fully learned baseline (Memory Layers at Scale recipe). *Why uncertain:* the
frozen-embedding record predicts pinned keys pay a penalty; the memory-layer record
predicts lookup wins for facts; the two have never been intersected — an empty cell in
the literature (verified against arXiv:2412.09764 / 2508.18756 lineage, 2026-07-08).
*Deciding experiment:* small memory-augmented LM (T1/T2 rungs), kernel-keys vs
learned-keys vs **shuffled-kernel-keys** at matched params/FLOPs; DVs: factual-QA
accuracy on kernel-covered slices, attribution quality (does the fired slot's concept
match the item's concept?), edit-locality (swap one concept's value row, measure ripple).
*Kill:* learned keys beat pinned keys by more than the pre-declared margin at matched
budget on the primary accuracy endpoint AND attribution/edit-locality gains fail their
minimum bars — either kills; passing requires the attribution/editability delta to be
real, since Law 2 says accuracy alone will favour unconstrained learning. *Cost class:*
Tier 3-like (requires pretraining small models — the most expensive fork here; gate
behind F2 outcome).

**N-B2 — kernel as MoE expert-label instrument (pillar B/interp rider).** *Options:*
probe OLMoE-class open MoE routers/experts against mapper-detected kernel concepts.
*Why uncertain:* routing may be too token-identity-driven at accessible scales for
concept structure to show. *Deciding experiment:* e8-style alignment: does kernel
concept identity predict expert activation clusters beyond shuffled-kernel and
token-identity controls, across ≥2 MoE families? *Kill:* no family pair beats both
controls. *Cost class:* Tier 2-like, inference-only. Rider on the e8-d/e8-r machinery.

**N-C1 — CALM-hybrid: learned latent regularised toward kernel coordinates (pillar C).**
*Options:* regulariser weight λ ∈ {0, small, large} on kernel-covered concepts only.
*Why uncertain:* L3 row 11 says fixed semantic *targets* are fundamental losers; whether
a *soft pull* inherits the penalty is exactly the open question L3 §9 names. *Deciding
experiment:* CALM-recipe small models across ≥3 rungs; primary endpoint: scaling exponent
vs λ=0 (P8 named-family comparison, LCM/CALM anchor); secondary: latent auditability
(decode-verify rate on covered concepts). *Kill:* any measurable exponent degradation vs
λ=0 (equivalence bound pre-declared) — the auditability gain may not buy a scaling tax.
*Cost class:* Tier 3–4; gate behind F2/F3.

**N-C2 — sidecar-axiom / kernel-RDM regularisers in adapter & distillation training
(pillar C, cheap rider).** *Options:* (a) LTN/semantic-loss rendering of `kot-axiom/1`
axioms as penalties during F4 adapter training; (b) kernel-RDM relational anchor during
F6 distillation. *Why uncertain:* established technique, unknown effect size at these
scales; F6's literature prior is a null. *Deciding experiment:* add as pre-registered
arms to F4/F6 rather than new experiments. *Kill:* no improvement over the same
experiments' existing arms at pre-declared margin. *Cost class:* marginal on existing
Tier 2–3 budgets.

**N-C3 — kernel input canonicaliser (pillar C, cheapest; recommended first).**
*Options:* (a) annotate-only (concept-hash tags added); (b) rewrite-to-canonical-surface
on mapper-confident spans (a1-hybrid policy); (c) rewrite via canonical-record rendering
(P10 inverse). *Why uncertain:* the 2025–26 brittleness record motivates it, but the
LLM-paraphrase-normalisation null is strong, and mapper abstention bounds coverage.
*Deciding experiment:* public paraphrase/format perturbation suites (Brittlebench-class)
filtered to kernel-covered items (m0b machinery), R1–R2 rungs: output-variance and
accuracy under perturbation for {raw, LLM-normalised, kernel-canonicalised} inputs at
matched preprocessing budget. *Kill:* variance reduction ≤ LLM-normalisation baseline, or
accuracy drops on canonicalised inputs (h = pre-declared), or covered-slice too small for
a powered test (decidability lint). *Cost class:* Tier 1–2-like, inference-only, reuses
mapper + M0 machinery — **the cheapest new decisive experiment this survey identifies.**

**Priority recommendation to the pillars (design opinion, not a verdict):** N-C3 and
N-C2 are cheap and run in supported cells; N-A1 is the most novel supported-cell
architecture (and strengthens the A6 pivot route); N-B1 is the highest-risk/highest-
centrality bet and should stay gated behind the F2 verdict; N-C1 and N-B2 are riders on
gates that already exist. Nothing here competes with F2 for priority: the pivot's
verdict reshapes which of these matters (an HE1 PASS makes verifier-adjacent forks
primary; an HE1 kill makes the A6/N-A1 interpretability lane the surviving pitch).

---

## 5. Constraint checklist for any new seam (apply before prereg)

1. Which §1.4 law applies, and which interface-locality cell does the seam sit in? If the
   empty cell — is it explicitly budgeted as a falsification?
2. Does any load-bearing step take cosine over kernel vectors? (X3 ban — redesign or
   block on the mitigation fork.)
3. What is the seam's **kernel-as-text null**, and is it in the arm list at matched
   budget?
4. Shuffled-kernel (and where relevant scramble/leakage) controls present?
5. Full metric vector V reportable, including authoring cost? Strong baselines named
   (RAG, distillation, quantisation, smaller-model-alone)?
6. Scale rungs declared (≥2 for any claim; ≥3 for any adjective), extrapolation envelope
   with a named literature anchor?
7. No semantic-web semantics smuggled in via tooling (engine style ≠ semantics)?
8. Absorption framing: is the claim efficiency/auditability (defensible) or permanent
   residence (indefensible)?
9. Coverage: does m0b machinery bound the covered slice, and is the experiment powered on
   that slice (decidability lint)?
10. Run-vs-audit separation and cross-vendor audit route identified (directives §8)?

---

*Cross-references:* `docs/kernel-design-directives.md` (binding);
`reports/lit-llm-injection-priorart.md` (L3 laws, §§1–9);
`docs/architecture.md` §4 (A1–A6); `docs/research-plan/01-hypotheses-experiments.md`
(evidence glossary, HC/HE/HS suites); `registry/status.json` (freeze state);
`registry/verdicts/` (f1, g6, g7, m0b); `mapper/README.md` (Phase M);
`docs/poc-design.md` (E-series pre-registrations).
