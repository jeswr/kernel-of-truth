# N1-A — The kernel-centrality architecture ladder (Pillar A)

**Kernel of Truth programme — next-direction seed, node N1-A (builds on N0
`docs/next/arch-survey.md`).**
Author: Kern (Fable design agent). Date: 2026-07-08.
Status: **DESIGN/PLANNING document. Nothing here is pre-registered.** Every rung below
is a *candidate* experiment: it becomes real only through `prereg-freeze` with a full
P8 statistical-analysis plan, and no rung may run before its declared gate. Binding
constraints: `docs/kernel-design-directives.md` (§1 no-semantic-web-legacy, §2 two
value theses + full metric vector V, §4 don't-guess-test, §6 honest stats).
Literature substrate: `reports/lit-llm-injection-priorart.md` (L3) and N0; citations
new to this document are tagged **[search]** (live web verification, 2026-07-08) or
**[memory]**; untagged citations are carried from the repo's verified reports.

**Question this document answers.** The programme currently touches the LLM at two
supported seams: an external deterministic verifier (F2, running) and a trained affine
input adapter (A2/E5, one rung). Both leave the LLM's *own* computation untouched.
This document lays out a **ladder of architectures in which the kernel becomes
progressively more central to inference itself** — from normalising what enters the
model, to living inside the model's layers, to *replacing* neural computation with
deterministic symbolic computation for the content it covers — each rung phrased as a
pre-registerable experiment with kill criteria, so the ladder is climbed (or cut)
by evidence, not preference.

---

## 0. The ladder on one screen

Centrality metric (definitional, for this document): **the fraction of
inference-critical computation and representation that flows through kernel-defined
structure**, from 0 (text-only LLM) upward. Each rung strictly increases it.

| Rung | Name | Kernel's role at inference | Topology | Trained parts | Cost tier (registry caps) | Gate | Existing hook |
|---|---|---|---|---|---|---|---|
| **L0** | Baseline seams | External verifier (A5/F2); input soft-token (A2) | out / in-at-input | none / adapter | Tier 1 (running) | GNG-0 (done) | F2 FROZEN, E5 PASS |
| **L1a** | Kernel input canonicaliser | Normalises the *text* before the model; no model change | out (preprocessor) | **none** | Tier 1–2 | none hard; POST-F2 for $ | N0 fork N-C3, mapper Phase M |
| **L1b** | Concept-dense I/O | Kernel-covered spans enter as dense concept tokens; kernel-covered answers leave as records | in at both edges | adapter + output head | Tier 3 | F2 read | **F3/HE3 (DRAFT)** + new output leg |
| **L2a** | Kernel-labelled concept bottleneck | A mid-network layer whose units are pinned to kernel concepts | **in, at depth** | bottleneck head | Tier 2–3 | POST-F2-INFRA-OPEN | N0 fork N-A1, e8 machinery |
| **L2b** | Kernel-addressed memory layer | In-FFN lookup keyed by kernel content-hashes | **in, at depth** | values (keys pinned) | Tier 3–4 | F2 verdict + maintainer | N0 fork N-B1 |
| **L3a** | Rules-engine oracle | kot-axiom engine + world-layer index answers covered queries alone | out (no LLM in loop) | **none** | **Tier 0–1** | none (r0-local-cpu arguable) | kot-axiom/1 design, mapper, P10 |
| **L3b** | Routed hybrid inference | Deterministic router: engine answers covered slice, LLM the rest | out, in the serving path | none (router deterministic) | Tier 1–2 | L3a PASS + F2 read | HE2 cascade sibling; F2 harness reuse |
| **L3c** | Engine-in-decode | Engine invoked mid-generation; answers constrained-decoded from records | interleaved | constrained-decode glue | Tier 3+ | L3b PASS | P10 interface |
| **L4** | Kernel-native substrate (horizon) | LLM only as NL boundary; all covered inference symbolic | — | — | not costable | **not proposed** | recorded for honesty only |

**Recommended order (cheapest-decisive-first, §5): L3a → L1a → L3b → L1b(=F3) →
L2a → L2b → L3c.** The two seeds that are genuinely new relative to N0 are the L3
rules-engine family (L3a/L3b/L3c) and L1b's output leg; L1a, L2a, L2b adopt N0's
N-C3/N-A1/N-B1 with the pre-registration skeletons completed here.

---

## 1. Ladder-wide rules (inherited, applied to every rung)

1. **Two nulls on every rung, no exceptions** (L3 Law 2; N0 §1.4): (i) the
   **text-only null** — same host, no kernel anything; (ii) the **kernel-as-text
   null** — the *same kernel content* rendered as text (pinned gloss dictionary, or
   RAG over canonically-rendered records) at matched token/FLOP budget. A rung that
   beats only (i) has shown nothing about the kernel.
2. **Full metric vector V** (directives §2, F0 accounting): accuracy/correctness,
   params, memory, inference FLOPs/latency/$, training FLOPs, **authoring cost**
   (world-layer population is labour; it goes on the ledger). Pareto reporting only.
3. **Model-scale axis**: every rung declares its rung set from the pinned ladder
   (R1 = SmolLM2-135M, R2 = 360M, R3 = 1.7B, R4 = Qwen2.5 family;
   `06-resources.md` §2.1). ≥2 rungs for any claim, ≥3 for any scale adjective
   (P8 §2.3); conjunctive claims under IUT.
4. **X3 cosine ban**: no load-bearing nearest-kernel-vector-by-cosine step anywhere.
   Every addressing step below is exact (content-hash / lexicon match) or happens in
   *model* space.
5. **Directives §1**: all symbolic machinery is `kot-axiom/1` + kernel-native records.
   Datalog-style *engine engineering* (Scallop-like evaluation strategies) is
   permitted machinery; RDF/OWL/SHACL semantics are not.
6. **Absorption framing** (L3 Law 3 / InstructRetro): claims are efficiency,
   auditability, correctness-at-the-interface — never "the model now uses our
   representation permanently".
7. **Run-vs-audit separation**: every PASS below requires the cross-vendor
   (Codex/GPT-5.5) audit before it is claimed (directives §8).
8. **Registry discipline**: each rung's experiment gets a registry id, DRAFT →
   prereg-freeze → run → verdict-gen; verdicts are pure functions of pre-declared
   statistics. Nothing in this document creates a registry entry.

---

## 2. L0 — the baseline rung (already held; the ladder's control surface)

**What it is.** The current seams, exactly as held: the F2 verifier pivot
(generate → P10 extraction → deterministic decode-verify against canonical records +
axiom sidecar → retry; FROZEN sha `28874f2b…`, running now) and the A2 adapter
(E5 PASS: content transfer to unseen nonce concepts at R1; no end-task claim).

**Role in the ladder — not "a rung to climb past" but the comparator set.** Every
higher rung must beat, at matched budget, *the best L0 configuration for the same
task*, because L0 is deployable today with zero architectural risk. Concretely: any
L1–L3 experiment carries an L0 arm (verifier-loop and/or A2-injection as applicable)
alongside the two nulls. This is the ladder's version of "beat strong baselines, not
no-intervention" (directives §2).

**No new pre-registration.** L0's open hypotheses (HE1/HE2/HC1–HC3/HS12) are frozen
or drafted already. The F2 verdict is the ladder's first branch point (§6).

**Why-now.** Already running; the only rung with money actively on the table.

---

## 3. L1 — kernel in tokenisation / normalisation (the boundary rung)

**Claim shape.** Most input text is superfluous to the computation the model must
perform: paraphrase variance, format noise, and multi-token spellings of concepts the
kernel can name in one canonical unit. Canonicalising input into few, dense,
high-level concepts before the model's interesting layers — and symmetrically letting
kernel-covered *answers* leave as canonical records rather than free tokens — buys
(a) **robustness** (one canonical surface form ⇒ variance collapse across
meaning-preserving perturbations) and (b) **cheap inference** (shorter prefill,
smaller KV cache, fewer decode steps).

**The normalisation framing, stated precisely.** This is inference-time input
normalisation — the semantic analogue of feature normalisation: collapse
nuisance variance (surface form) while preserving signal (meaning), *outside* the
model, deterministically. The 2025–26 brittleness record motivates it (up to ~33%
accuracy swing under meaning-preserving perturbation; Brittlebench arXiv:2603.13285,
arXiv:2605.01605, arXiv:2601.06341 — carried from N0); the training-side mitigation
exists (Flip-Flop Consistency, arXiv:2510.14242) but the inference-side
canonicalisation cell is open. The compression literature is the *baseline set*, not
the mechanism: LLMLingua (arXiv:2310.05736), gist tokens (arXiv:2304.08467) and their
successors (in-context gisting, arXiv:2504.08934 **[search]**; K-token latent merging,
arXiv:2604.15153 **[search]**) optimise tokens with trained components and no meaning
guarantee; the kernel canonicaliser is training-free and abstains where it cannot map
(mapper `a1-hybrid` policy, measured abstention).

**The LCM/CALM risk, stated honestly (mandatory caveat).** Concept-level I/O has a
measured scaling penalty when a *fixed semantic space is the prediction target*
(SONAR-LLM exponents α≈0.49–0.57 vs 0.79 token; L3 §4 row 11); CALM
(arXiv:2510.27688) recovered the step-compression win precisely by dropping semantic
fixedness — verified again this week: the CALM line and its successors (projected
autoregression, arXiv:2601.04854 **[search]**) keep the latent learned and
reconstruction-optimised. L1's defence is architectural, and it is falsifiable: the
kernel sits at the **interface** (what enters and leaves), never as the internal
prediction target — the model's latent computation and next-token objective are
untouched (L1a) or touched only at the embedding edges through a trained adapter in
the already-supported cell (L1b). HS10 ("efficiency lives at the interface, not dense
I/O") is exactly the hypothesis that decides whether even the edges are too far. If
L1b shows an exponent penalty, the ladder records it and retreats to L1a.

### 3.1 L1a — kernel input canonicaliser (training-free; adopts N0 fork N-C3)

- **Hypothesis (HL1a).** On paraphrase/format-perturbation suites filtered to
  kernel-covered items (m0b machinery), deterministic kernel canonicalisation of
  inputs (mapper-confident spans rewritten to one canonical surface form, or
  annotated with concept references) reduces output variance across perturbations
  and preserves accuracy, beating an LLM-paraphrase normaliser at matched
  preprocessing budget.
- **Decisive test.** Public perturbation benchmark (Brittlebench-class), covered
  slice; arms: {raw text; LLM-normalised ("rewrite in plain canonical English", same
  or smaller model as preprocessor); kernel-canonicalised (fork FK-L1-1 decides the
  variant); kernel-as-text null (concept glosses appended, no rewrite)}. DVs:
  per-item output-variance across perturbation sets (primary), accuracy delta
  (co-primary, non-inferiority), preprocessing + inference cost (full V). Rungs
  R1–R2, extension R3 on the pre-declared predicate.
- **Kill criteria.** Variance reduction ≤ LLM-normaliser arm's (paired bootstrap,
  α=0.05, pre-declared margin); OR accuracy non-inferiority fails (TOST, margin
  pre-declared); OR the powered covered-slice is too small (decidability lint —
  abstention rate bounds coverage; measured, not assumed).
- **Cost tier / infra.** Tier 1–2 (~$20–60, inference-only, Modal harness reuse).
- **Why-now.** The mapper exists and is signed (Phase M, `a1-hybrid`); the
  brittleness literature is fresh; zero training; the cheapest new *model-facing*
  experiment the programme has.

### 3.2 L1b — concept-dense input + record-constrained output (extends F3/HE3)

- **Hypothesis (HL1b = HE3 + output leg).** Replacing kernel-covered spans with
  dense concept tokens (X4-projected kernel vectors through the E5 adapter) cuts
  prefill FLOPs and KV-cache at accuracy parity vs full text (HE3 as drafted), **and**
  constraining kernel-covered *answers* to be emitted as P10 records (then rendered
  deterministically to canonical surface text) cuts decode steps at matched
  answer-correctness. The output leg is the new content: today F3 is input-side only.
- **Decisive test.** F3's seven arms as drafted (registry `f3`, Tier 3, $170 cap),
  plus two output-leg arms: (a) free decode (baseline), (b) record-constrained decode
  for covered answers + deterministic rendering. Mandatory baselines: matched-token
  *text* compression (LLMLingua/gist-class trained compressor — if a trained
  compressor achieves parity, the kernel adds nothing, HE3's existing kill), and the
  kernel-as-text null. DVs: full V with FLOPs split prefill/decode; extraction-failure
  gate on the P10 leg (X2 discipline: 51/54 was encoder-side, model-side is part of
  the system under test).
- **Kill criteria.** HE3's frozen kills stand (loses to matched-token text at d≥16;
  trained-compressor parity). Output leg dies if record-constrained decode loses
  answer-correctness by more than the pre-declared margin or if extraction-failure
  Wilson-LB > 10%. **Scaling-exponent tripwire:** if any L1b arm involves training
  beyond the adapter, a ≥3-rung exponent comparison vs the λ=0 configuration is
  mandatory before any efficiency adjective (the CALM/LCM anchor family, P8).
- **Cost tier.** Tier 3 (F3's existing cap absorbs the output leg: +~$20).
- **Why-now.** F3 already DRAFT; CALM's step-compression evidence says the *bandwidth*
  intuition is right — the open question is precisely whether canonical-at-the-edges
  avoids the fixed-space tax, and no one else can run that experiment (it needs a
  canonical concept space with a validated projection, which the programme uniquely
  has: X4).

---

## 4. L2 — kernel as internal layer (participation at depth)

**Claim shape.** Beyond the A2 input edge: kernel structure participating *inside*
the network at inference — a layer whose coordinates or addresses are kernel-defined.
Motivation for depth: the model's factual computation demonstrably lives mid-network
(ROME; L3 §1), so an injection/attribution surface at depth sits where the knowledge
is. Both L2 mechanisms sit in supported interface-locality cells (trained bridge /
model-native keys); both convert the A6 interpretability bet into an *architectural*
one: instead of aligning post-hoc to unstable learned dictionaries (the 2025 SAE
correction: absorption arXiv:2409.14507, seed non-identifiability arXiv:2501.16615,
non-canonicity arXiv:2502.04878), pin the coordinate system by construction and let
training fill in around it.

### 4.1 L2a — kernel-labelled concept-bottleneck layer (adopts N0 fork N-A1)

- **Hypothesis (HL2a).** A bottleneck layer over a frozen host whose units are pinned
  1:1 to kernel concept hashes (CB-LLM recipe, arXiv:2412.07992, ICLR 2025; kernel
  vocabulary instead of the ad-hoc LLM-generated one; cf. Concept Layers,
  arXiv:2502.13632 **[search]**, and the intrinsic-interpretability survey
  arXiv:2604.16042 **[search]**) matches the ad-hoc-vocabulary CB-LLM on concept
  detection and steering while adding what no learned vocabulary has: versioned,
  content-addressed, seed-stable unit identities — with concept leakage below a
  pre-declared bound.
- **Decisive test.** Detection + steering on covered and nonce concepts; arms:
  {kernel-pinned bottleneck; CB-LLM with matched-size LLM-generated vocabulary;
  shuffled-kernel labels (null); SAE-feature baseline (e8 machinery); E9-defl-style
  semantic-scramble arm to price leakage}. DVs: detection AUC, steering success,
  end-task accuracy tax of the bottleneck, leakage fraction (scramble-recovered
  effect), full V. Rungs R1–R2 (+R4-family replication for the interp claim).
- **Kill criteria.** Kernel-pinned ≤ ad-hoc CB-LLM on detection/steering (TOST,
  pre-declared margin) — the canonical vocabulary buys nothing; OR scramble arm
  recovers most of the effect (leakage, margin pre-declared); OR the bottleneck's
  accuracy tax exceeds the pre-declared ceiling (the CBM tax is the known failure).
- **Cost tier.** Tier 2–3 (adapter/head training on small hosts; ~$60–150).
- **Why-now.** CB-LLM made LLM-scale bottlenecks real in 2025 with the vocabulary as
  the acknowledged weak point; the GDM SAE deprioritisation left "stable labelled
  coordinates for model internals" as a documented unmet need; this rung merges the
  A2 and A6 seams into one architecture and strengthens the A6 pivot lane if F2
  fails.

### 4.2 L2b — kernel-addressed in-network memory layer (adopts N0 fork N-B1)

- **Hypothesis (HL2b).** In a product-key memory-layer LM (Memory Layers at Scale,
  arXiv:2412.09764; PEER arXiv:2407.04153; UltraMemV2 arXiv:2508.18756), pinning a
  fraction of the key table to kernel concept identities (option a: X4-projected
  vectors; option b: hash-derived discrete codes — fork FK-L2-2) costs no more than a
  pre-declared accuracy margin at matched params/FLOPs, while delivering two things
  no learned memory has: **per-token concept attribution** (the fired slot names its
  concept) and **edit-locality** (swapping one concept's value row edits that fact
  with bounded ripple — the knowledge-editing failure mode, inverted into a design
  property). Retrieval-in-network keyed by content: the lookup is exact-match in the
  pinned key space, so X3 is structurally avoided in option (b) and confined to
  model-side geometry in option (a).
- **Decisive test.** Small memory-augmented LMs trained from scratch (Pythia-suite
  T1/T2 configs), arms {kernel-pinned keys; learned keys (Meta recipe); shuffled-
  kernel keys (mandatory null)} at matched params/FLOPs; DVs: factual-QA accuracy on
  covered slices (primary), attribution precision (fired-slot concept vs item
  concept), edit-locality (ripple after one value-row swap), full V incl. training
  FLOPs.
- **Kill criteria.** Learned keys beat pinned keys beyond the pre-declared margin on
  the accuracy primary AND the attribution/edit-locality co-primaries miss their
  minimum bars — either alone kills, per N0: Law 2 predicts accuracy favours
  unconstrained learning, so a PASS requires the auditability deltas to be real and
  priced.
- **Cost tier.** Tier 3–4 (pretraining small models — the most expensive rung before
  L3c; **gated on the F2 verdict and maintainer sign-off**).
- **Why-now** (and why not first): the memory-layer line went industrial in 2025 and
  is the literature's clearest "explicit lookup wins for facts at matched compute"
  signal; the kernel × memory-layer intersection is a verified empty cell. But the
  frozen-embedding record predicts the pinned-key penalty, so this rung buys the most
  centrality per dollar *only if* cheaper rungs have already shown kernel value.

---

## 5. L3 — the internal neurosymbolic rules-engine (the maintainer's seed, worked)

**Claim shape.** For content the kernel covers, **inference itself becomes symbolic**:
cheap deterministic rules-based computation over the axiom sidecar + world layer
replaces neural reasoning. The maintainer's worked example, grounded in the existing
design: `mother` is explicated as a functional relation over persons; the endorsed
sidecar (stratum 3, `kot-axiom/1` — design-constraint-layer.md §3.3–3.4) states it as
`cardinality {path: has-parent, qualifier: female, min:1, max:1}` on `human` plus
`functional` on `mother-of`; Elvis→Gladys is a **world-layer record** (stratum 4,
outside concept identity per directives §5). Then *"who gave birth to Elvis?"* is:
mapper detects {mother/give-birth, Elvis} → the query normalises to
`mother-of(Elvis, ?x)` → the functional-relation axiom licenses a **unique-answer
index lookup** → `Gladys Presley`, with provenance, in microseconds on a CPU — no
GPU rounds, no sampling, no hallucination surface. The four strata make this
well-typed: profile (stratum 1) fixes the grammar, definitions (stratum 2) fix what
`mother` *means*, the sidecar (stratum 3) fixes the laws that make the lookup valid
(functionality ⇒ uniqueness), the world layer (stratum 4) holds the facts. The LLM's
remaining jobs are the NL boundary (parse in, render out) — and L1a is exactly the
parse-side instrument, which is why L1 and L3 compose.

**Literature seat.** This is Law-3 topology (neural proposer ↔ formal language ↔
deterministic engine) pushed one seat further: the engine stops *checking* answers
(F2) and starts *producing* them. The division-of-labour evidence trends this way —
memory layers' factual-QA-dominant wins (arXiv:2412.09764), kNN-LM's rare-fact wins
(arXiv:1911.00172), popularity-gated retrieval beating parametric recall (Mallen et
al., ACL 2023 **[memory]**), unreliable parametric recall even when the fact is
encoded (arXiv:2605.18732 **[search]**) — and the 2026 neurosymbolic serving
literature is converging on routed designs: SMT-based reasoning routers
(arXiv:2602.18095 **[search]**), LLM-grounded sound-and-complete tableau reasoning
over curated KBs (arXiv:2507.09751 **[search]**), ontology-constrained enterprise
agents (arXiv:2604.00555 **[search]**). None of these has a *canonical,
content-addressed, definition-grounded* store — that is the kernel's differentiator
and the novelty claim to defend in any write-up.

**The honest risks, named before the sub-rungs.**
1. **Coverage is the ceiling.** The engine answers only what the world layer holds
   and the sidecar licenses; world-layer population is authoring labour and goes on
   V (fork FK-L3-2). m0b bounds concept coverage, not *fact* coverage — a new
   fact-coverage gate is part of L3a.
2. **The router/parse must be nearly free.** If NL→query needs an LLM call, the
   compute win shrinks to (decode steps saved − parse cost); the design answer is the
   deterministic mapper + a closed query grammar (fork FK-L3-1), with the LLM parse
   as a measured fallback arm, and end-to-end latency/FLOPs/$ *including routing*
   pre-registered as the cost metric (energy/latency accounting per
   arXiv:2501.08219 **[search]**).
3. **Law 2 cuts here too.** The kernel-as-text null is the same world-layer facts
   rendered as text + RAG + a small LLM at matched budget. RAG-over-facts is cheap
   and strong; the engine's edge must show up as exactness (functional-relation
   uniqueness, axiom-licensed refusal when no record exists — the anti-hallucination
   surface RAG lacks) and/or cost. If it does not, L3 is dead regardless of elegance.
4. **Freshness/conflict.** Two records asserting different mothers is a sidecar
   violation the engine must surface, not resolve silently (fail-closed ERR_*
   discipline carries over).

### 5.1 L3a — engine-oracle (no LLM in the loop; the cheapest decisive rung)

- **Hypothesis (HL3a).** Over a covered factual-query slice with a populated world
  layer, the kot-axiom engine + world-layer index answers ≥ a pre-declared fraction
  exactly (with provenance, and with axiom-licensed refusal on unanswerable items),
  at ≥10³× lower inference cost (FLOPs/latency/$) than the smallest LLM rung that
  matches its accuracy on the same slice.
- **Decisive test.** Build: (i) a seeded world-layer corpus over the litmus families
  (human/parent/sex; bookmark/maker; promise/parties) + an extracted public-facts
  slice (provenance-stamped, per design-bulk-kernel discipline); (ii) a closed query
  grammar over `kot-axiom/1` relations (lookup, inverse, functional-unique, count,
  disjointness check — the v0 constraint inventory read as query operators); (iii) an
  eval of N≥500 NL questions authored *against the records* with held-out phrasings.
  Arms: {engine (mapper-parsed); engine (gold-parsed — isolates parse loss); text-only
  LLM (R1–R3); LLM+RAG over text-rendered facts}. DVs: exact-answer rate, refusal
  correctness on unanswerable items (co-primary — this is the anti-hallucination
  claim), end-to-end cost per query, parse-failure rate (the mapper's abstention
  surfaces here).
- **Kill criteria.** Engine-with-gold-parse answers < the pre-declared fraction
  (engine or store is inadequate — indict the stage); OR mapper-parse loses > a
  pre-declared fraction of gold-parse accuracy (the NL boundary eats the rung; L3
  waits for a better parser, not more GPU); OR LLM+RAG at R1 matches engine accuracy
  at comparable cost (the differentiator failed).
- **Cost tier / infra.** **Tier 0–1** (~$0–20: engine + eval are r0-local-cpu; the LLM
  comparison arms ride the F2 Modal harness). The only build cost is the v0 engine
  itself — the validator procedure of design-constraint-layer.md §3.3 plus an index,
  which is engineering the constraint layer needs anyway.
- **Why-now.** kot-axiom/1 is designed but unimplemented; L3a *is* its implementation
  test, double-dutied as the ladder's cheapest decisive experiment. It needs no
  model training, no F2 outcome, and it converts HC2's "a gloss file cannot count
  parents" from a verifier claim into a generator claim.

### 5.2 L3b — routed hybrid (the deployable form)

- **Hypothesis (HL3b).** On a mixed workload (covered factual + uncovered general
  queries at a pre-declared, sensitivity-analysed mix), a deterministic router
  (mapper-confidence + query-grammar match ⇒ engine; else ⇒ LLM) beats LLM-alone and
  LLM+RAG on accuracy at equal-or-lower total compute, and the accuracy win
  concentrates measurably on the covered slice (per-slice breakdown mandatory).
- **Decisive test.** Arms: {LLM alone; LLM+RAG-over-text-facts; router→engine/LLM;
  router→engine/LLM+verifier (L0 composition); oracle-router (upper bound)}. DVs:
  mixed-workload accuracy, per-slice accuracy, router precision/recall
  (mis-routes are the new error class and get their own gate: mis-route rate
  Wilson-UB below a pre-declared bound), full V end-to-end. Rungs R1–R3 on the LLM
  side (the scale axis here asks: does the hybrid's edge *shrink* as the LLM grows —
  the honest expectation — and what is the crossover?). Fit the trend per P8; the
  deployable claim is "hybrid dominates at ≤R_k", never "hybrid wins".
- **Kill criteria.** Hybrid ≤ LLM+RAG on mixed accuracy at matched cost (paired
  bootstrap, α=0.05, margin pre-declared); OR mis-route harm exceeds its bound; OR
  the covered-slice share needed for the win exceeds any defensible real-workload
  estimate (the workload-mix sensitivity analysis is pre-registered, not post-hoc).
- **Cost tier.** Tier 1–2 (~$30–80, inference-only). **Gated on L3a PASS + F2 read.**
- **Why-now.** It is the efficiency thesis (directives §2B) in its most direct form:
  answers that cost microjoules instead of GPU-seconds, with the LLM reserved for
  what actually needs it — and it composes with, rather than competes against, the
  F2 verifier (the engine that *answers* covered queries and the engine that
  *checks* LLM output on covered content are the same artefact in two seats).

### 5.3 L3c — engine-in-decode (interleaved; horizon of the L3 family)

- **Sketch, deliberately thin.** Mid-generation engine calls: when decoding enters a
  kernel-covered assertion, the covered span is constrained-decoded from the
  engine-supplied record (a deterministic sibling of speculative decoding: the engine
  drafts the *fact*, the model drafts the *prose*). Requires P10-in-reverse plus
  decode-time integration; only worth designing in full if L3b passes and the
  measured bottleneck is that covered facts occur *inside* long generations rather
  than as routable queries.
- **Gate.** L3b PASS + maintainer sign-off. Tier 3+. Pre-registration deferred — a
  full design here would be guessing (directives §4).

### 5.4 L4 — kernel-native substrate (recorded, not proposed)

For honesty about where the ladder points: the limit shape is "LLM as NL boundary
only; all covered inference symbolic". Not proposed, not costable, and the LCM
lesson plus Law 2 say the *incremental* rungs must earn their way there. Recorded so
nobody later claims the programme hid its ambition.

---

## 6. Ranking, gates, and the F2 branch

### 6.1 Cheapest-decisive-first ranking (design opinion, prereg order)

| Order | Rung | Tier / est. $ | What it decides | Expected insight per $ |
|---|---|---|---|---|
| 1 | **L3a** engine-oracle | 0–1 / ~$0–20 | Can the kernel *compute answers at all* on its covered slice, and at what cost ratio? | Highest — decisive on the L3 premise, builds the constraint-layer engine the programme owes anyway, no model training |
| 2 | **L1a** canonicaliser | 1–2 / ~$20–60 | Is deterministic semantic normalisation worth anything against the LLM-paraphrase null? | High — cheapest model-facing rung; also de-risks the parse side of L3 |
| 3 | **L3b** routed hybrid | 1–2 / ~$30–80 | Does symbolic answering survive contact with a mixed workload and strong RAG? | High — the deployable efficiency claim; gated on 1 |
| 4 | **L1b** dense I/O + output leg | 3 / F3 cap +$20 | Does canonical-at-the-edges compression beat trained text compression? | Medium-high — rides the existing F3 draft |
| 5 | **L2a** kernel bottleneck | 2–3 / ~$60–150 | Does a canonical vocabulary beat ad-hoc CB-LLM vocabularies? | Medium — strongest interp-lane rung; the A6 pivot's architectural form |
| 6 | **L2b** pinned memory keys | 3–4 / ~$150–400+ | Do pinned keys buy attribution/editability at acceptable accuracy cost? | Medium — most novel cell, most expensive, strongest gate |
| 7 | **L3c** engine-in-decode | 3+ | deferred | — |

Rationale: rungs 1–3 are inference-only, mostly CPU, and each is *independently*
decisive (a kill at any of them is a clean, publishable negative on that centrality
level without blocking the others). Rungs 4–6 involve training and inherit
POST-F2-INFRA-OPEN gating.

### 6.2 How the F2 verdict re-ranks the ladder

- **HE1 PASS (verifier offload buys parameters).** The engine seat is validated;
  L3a/L3b promote to the primary track (the verifier and the answerer are one
  artefact); L1a stays as the robustness rider; L2 stays gated.
- **HE1 KILL, HC2 PASS (verification wins only where axioms bite).** L3 narrows to
  axiom-licensed content (counting, functionality, disjointness) — still exactly the
  `mother` example; L3a proceeds with the narrowed slice; the interp lane (L2a) rises.
- **HE1 + HC2 KILL (text wins everywhere it was measured).** The correctness track's
  external seams are dead at measured rungs; the surviving pitches are L2a
  (interpretability, where the SAE correction keeps the need alive independent of
  end-task wins) and L3a's *cost* claim (exactness at negligible cost can survive an
  accuracy-parity world — but only with the workload-mix honesty of §5.2). L1a
  survives on its robustness endpoint, which no F2 outcome touches.

---

## 7. Forks (directives §4 form — first-class hypotheses, not decisions)

**FK-L1-1 — canonicaliser output form.** *(a)* annotate-only (concept tags added);
*(b)* rewrite-to-canonical-surface on mapper-confident spans; *(c)* full
canonical-record rendering (P10-inverse). *Why uncertain:* (a) is safest but adds
tokens; (b) risks meaning drift the mapper cannot see; (c) is strongest but
lowest-coverage. *Decided by:* L1a runs all three as arms. *Kill per arm:* loses to
the LLM-normaliser null.

**FK-L1-2 — output-layer step.** *(a)* free decode (no output leg); *(b)*
P10 record-constrained decode + deterministic rendering. *Why uncertain:* constrained
decode may tax answer accuracy more than it saves in steps; extraction failure is a
measured gap. *Decided by:* L1b's output-leg arms. *Kill:* accuracy margin or
extraction-failure Wilson-LB > 10%.

**FK-L2-1 — bottleneck placement and role.** *(a)* in-path bottleneck (CB-LLM style,
interventions possible, accuracy tax); *(b)* probe-only side head (no tax, no
intervention). *Why uncertain:* the CBM tax vs intervenability trade is task-dependent.
*Decided by:* L2a arms. *Kill:* in-path tax above ceiling ⇒ (b) only.

**FK-L2-2 — memory-key addressing.** *(a)* X4-projected geometric keys; *(b)*
hash-derived discrete codes (pure content-address, X3-immune); *(c)* learned baseline.
*Why uncertain:* geometry may help routing or may re-import similarity pathologies.
*Decided by:* L2b's three-way arm. *Kill:* both pinned variants beaten beyond margin
with no auditability win.

**FK-L3-1 — router identity.** *(a)* deterministic mapper + closed query grammar;
*(b)* tiny trained classifier; *(c)* LLM self-route ("answer or call the engine").
*Why uncertain:* (a) is free but abstention-bounded; (c) is the strongest parse but
spends the compute the rung exists to save. *Decided by:* L3b arms, cost-on-ledger.
*Kill per option:* mis-route bound or cost dominance.

**FK-L3-2 — world-layer population route.** *(a)* deterministic extraction from
existing structured sources (provenance-stamped lowering, the onto-obo pattern);
*(b)* LLM-authored + validator-gated records (G9/HS-A pattern); *(c)* hybrid.
*Why uncertain:* authoring cost vs coverage vs error rate — all three land on V.
*Decided by:* L3a's corpus build measures all three routes' cost and record-error
rate against a held-out audit sample. *Kill:* record-error rate above a pre-declared
bound makes the engine's "exactness" claim dishonest for that route.

**FK-L3-3 — engine expressivity.** *(a)* v0: kot-axiom validation semantics read as
query operators (lookup/inverse/functional-unique/count/disjoint) — no recursion, no
chaining; *(b)* +bounded rule layer (Datalog-style evaluation à la Scallop as
*engineering*, semantics native, closed and capped). *Why uncertain:* (a) may cover
too little of the query eval; (b) expands checking cost nonlinearly and flirts with
scope creep the constraint-layer design explicitly deferred. *Decided by:* L3a's
failure analysis — the fraction of missed queries that (b) would have answered is a
measured number before any (b) build. *Kill for (b):* that fraction below a
pre-declared bar.

---

## 8. Pre-registration checklist delta (beyond N0 §5, for ladder rungs)

11. **Composition accounting:** if the rung composes with L0 seams (e.g. L3b+verifier),
    the composed arm is declared at freeze — no post-hoc "but together they win".
12. **Routing/mis-route gate** (L3b/L3c): mis-routes are a first-class error class
    with their own pre-declared bound.
13. **Workload-mix sensitivity** (any mixed-workload claim): the mix is an IV with a
    pre-declared sweep, and the verdict names the mix range where the claim holds.
14. **Stage indictment:** multi-stage rungs (parse → engine → render) pre-declare
    per-stage instruments so a kill names the failed stage (L3a's gold-parse arm is
    the template).

---

*Cross-references:* `docs/next/arch-survey.md` (N0 — survey, forks N-A1/N-B1/N-C3,
laws §1.4); `docs/kernel-design-directives.md` (binding); `docs/design-constraint-layer.md`
§3 (`kot-axiom/1` grammar, litmus encoding, sidecar strata); `docs/research-plan/01-hypotheses-experiments.md`
(HC/HE/HS suites, F3/HE3, HE2 cascade); `docs/research-plan/06-resources.md` §2.1
(scale rungs R1–R5/T1–T3); `docs/research-plan/08-stats-and-extrapolation.md` (SAP
template, rung-set discipline); `docs/research-plan/10-model-record-interface.md`
(P10); `mapper/README.md` (Phase M, `a1-hybrid`); `registry/status.json` (tier caps,
freeze state); `reports/lit-llm-injection-priorart.md` (L3 laws).
