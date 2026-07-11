# P3-LR-RULE — Rule-Injection into Transformers

**Kernel of Truth Programme-3, Phase-0 literature review.**
Author: Fable (Claude Fable 5, literature-researcher discipline), 2026-07-11.
Bead: `kernel-of-truth-s55r.8` (P3-LR-RULE, programme rev-2 §5 Phase-0 table; scope §3.3).
Feeds (Phase-1): **P3-D-RULE** (co-blocked by P3-LR-NTP).

**Scope (verbatim from the Phase-0 table):** constrained/grammar decoding WITH executors
(not just grammars); KV-memory injection; steering/activation edits; adapter-encoded
procedures; bottleneck architectures; per-placement causal-provenance validation practice
(what counts as evidence beyond attention maps). Extends
`reports/lit-llm-injection-priorart.md`.

**Epistemic contract.** Every load-bearing line carries [MEASURED|STIPULATED|EXTRAPOLATION];
literature claims carry `[LIT: <id>]` keys into `docs/next/lit/RULE.sources.jsonl`
(one JSON object per source; `verified:true` = primary page fetched by me 2026-07-11 at the
URL given — NOT a claim that every body figure was independently re-derived; where a number
is load-bearing its metric definition is stated in-line; rows re-checked during the
2026-07-11 revision additionally carry a `locator` field (source version/date +
page/table/section) and a full locator retrofit for the remaining quantitative
decision-bearing rows is proposed in §10; `verified:false` = carried from a
prior verified in-repo review or KB recall, NOT re-fetched — flagged in-line as
UNVERIFIED-THIS-PASS). KB/lit records are recall infrastructure, not evidence; nothing here
amends any registry object. Matched-compute skepticism is applied throughout: every "X beat
Y" line states its accounting. Capability-limited vs fundamental judgements are §8's
explicit deliverable.

**Dedup statement (what already exists; this review builds on, does not repeat):**
- `reports/lit-llm-injection-priorart.md` (2026-07-08) — owns the injection-mechanics
  record (soft prompts, ToolkenGPT, GraphToken, xRAG, KEPLM verdict, retrieval lineage,
  SAE correction) and its three laws (interface-locality; capability-wins-live-on-the-
  symbol-side; the double-edged capability gradient). §§3–4 below cite those laws as
  carried, and extend the record where it moved (2025–26): KBLaM-line scaling, memory
  layers, cache steering, the steering reliability correction, AlphaEdit.
- `reports/lit-structured-parsing-and-inner-symbolic.md` (2026-07-09) — owns the
  grammar/type-constrained-decoding transport record (PICARD, SynCode, XGrammar, GAD,
  type-constrained PLDI-2025, format-tax) and the Thread-B inner-symbolic instrument
  survey (Patchscopes, back-patching, NVSA). §2 below re-anchors only what H-RULE-CD
  needs and adds the executor-coupled lineage (MGD, Synchromesh CSD, execution-guided
  decoding, IterGen, CRANE, 2026 caveats) which no prior report owns.
- `docs/next/lit/RAG.md` (P3-LR-RAG) — owns retrieval/RAG/verifier baselines incl.
  kNN-LM/RETRO cost accounting and KBLaM-as-retrieval-comparator. §3 treats KBLaM strictly
  as a KV-injection placement, not as a RAG recipe.
- lit-KB (`kb/records/`, 552 records; pipelines in `tools/kb/`) — already holds the
  steering/editing/KV cluster in structured form (ROME `arxiv_2202.05262`, editing-at-scale
  `arxiv_2401.07453`, ITI `arxiv_2306.03341`, ActAdd `arxiv_2308.10248`, CAA
  `arxiv_2312.06681`, RepE `arxiv_2310.01405`, steering-eval `arxiv_2410.17245`, KBLaM
  `arxiv_2410.10450`, K-Adapter `arxiv_2002.01808`, plug-and-play `arxiv_2305.17691`,
  VSA-rule-steering `arxiv_2502.01657`, causal abstraction `arxiv_2301.04709`, CB-LLM
  `arxiv_2412.07992`, hopping-too-late `arxiv_2406.12775`, CoT-depth-theory
  `arxiv_2305.15408`, MeKi `arxiv_2602.03359`, ATLAS-steering `arxiv_2601.03093`, and the
  constrained-decoding oldies 1704.07138/1804.06609/1906.07220). Per the KB honesty
  boundary those records are recall, not evidence — every load-bearing claim below was
  re-verified at a primary URL today or explicitly flagged. New sources found here are
  staged in `RULE.sources.jsonl` for the coordinator's central ingest — **no KB
  shard/index is mutated by this bead** (governance). [STIPULATED: dedup protocol]
- Net-new ground owned by this document: the executor-coupled (vs grammar-only)
  constrained-decoding distinction with its 2025–26 evidence; the KV-injection record
  read as a RULE placement; the 2024–26 steering-reliability correction; the
  bake-in/composition-limits line (physics-3.2, grokking, two-hop, depth theory) as a
  placement constraint; and the causal-provenance validation practice synthesis.

---

## 0. Executive verdict (one paragraph)

The five H-RULE placements (§3.3: CD, KV, AD, ACT, HL) are NOT equally supported by the
literature, and the evidence ordering matches the programme's stipulated test order
(ASM-0802) almost exactly — with one sharpening. **Decode-side, executor-coupled
constrained decoding is the only placement with repeated same-host ablation wins**: the
same model with an executor-derived token mask beats itself without one, from 2018
execution-guided SQL through PICARD/Synchromesh to Monitor-Guided Decoding — where a
static-analysis monitor lifts SantaCoder-**1.1B** above text-davinci-003 on compilation
rate and next-identifier match [LIT: mgd-2023] — and type-constrained decoding halves
compilation errors across model sizes [LIT: type-constrained-2025]; GRAMMAR-mask
transport overhead is engineering-solved [LIT: xgrammar-2025], though that number does
NOT price semantic-engine calls, per-token executor work, or backtracking (§2.3). These
are accuracy ablations on the same host, not resource-matched frontier wins under
KOT-COST/2 — the constrained arms do extra decoding work and often emit more tokens.
Its priced caveats (distribution distortion [LIT: gad-2024], reasoning/format tax
[LIT: format-tax-2024, crane-2025, cd-alignment-tax-2026]) have published mitigations
for the reasoning-tax component (reasoning-augmented grammars, alternating
constrained/unconstrained spans) — CRANE reports accuracy gains of up to 10pp on
GSM-symbolic and FOLIO on the same model, at MORE generated tokens than unconstrained
CoT in nearly every arm (Table 1: e.g. 131.3 vs 129.0 at Qwen2.5-1.5B, 235.8 vs 212.2
at R1-Distill-Qwen-7B) plus constrained-decoder work [LIT: crane-2025] — while
distribution distortion, coverage-aware abstention, and semantic-monitor cost remain
open or unpriced (§2.2). **KV injection of declarative content works
only through a trained bridge and is demonstrated only at 8B+** [LIT: kblam-2025,
atlaskv-2026]; no published system injects *rules* (procedures licensing inference) as KV
and validates the inference causally — the placement's core cell is EMPTY, and the KBLaM
line's own "attention weights show knowledge use" claim is exactly the evidence class §6
disqualifies. **Steering/activation editing took a hard 2024–26 correction**: prompting
beats every representation-level steering method on matched concept-steering evals at 2B
[LIT: axbench-2025]; across 36 models (1.5B–70B) steering often does nothing or hurts
[LIT: steering-off-course-2025]; unreliability traces to behaviours lacking a coherent
linear direction [LIT: steering-unreliability-2025] — while the one direct rule-injection
steering result (VSA encode–compute–decode in hidden space, 15.4× more rule-following
problems solved [LIT: vsa-rule-2025]) is a single-group EMNLP-2025 result on narrow tasks,
unreplicated, exactly the nsk1-shaped channel the programme already measured as
delivery-yes/integration-unresolved [MEASURED: registry/assessments/nsk1-*]. **Weight-space
placements (adapters/editing) reliably carry behaviours/procedures but repeatedly LOSE
to in-context alternatives as fact stores in same-host comparisons** (these studies test
KNOWLEDGE injection, not rules, and do not establish matched lifecycle/tuning compute):
RAG > unsupervised fine-tuning for knowledge [LIT:
ovadia-ft-vs-rag-2024], new-knowledge fine-tuning is slow then hallucinogenic [LIT:
gekhman-2024], parametric-RAG alone underperforms token-RAG [LIT: prag-2026], editing
methods fail ripple propagation and die under sequential edits with in-context editing
beating them all [LIT: ripple-2024, editing-scale-2024]. Beneath all of this sits a hard
bake-in constraint the literature now states from four independent directions: **a
transformer that stores knowledge perfectly still cannot MANIPULATE it in-weights without
surfacing intermediate steps** — classification/comparison fail without CoT and inverse
search is ~0% [LIT: physics-3.2-2024]; bounded-depth transformers provably cannot do
multi-step arithmetic without CoT tokens [LIT: cot-depth-theory-2023]; latent two-hop
composition over novel facts fails [LIT: twohop-2025, grokked-2024, hopping-2024]. For
H-RULE this is the load-bearing architectural PRIOR (measured in controlled synthetic
settings, proved for bounded-depth asymptotics; not a closed law — see §5's scope
statement): **placements that ask the HOST to execute rule composition in a forward pass
carry the burden of proof against this wall; placements that let the µs engine compute
and deliver RESULTS do not.** CD → KV first is not just
cheapest-first, it is the literature's ordering [EXTRAPOLATION: argued §5, §9 — the
P3-E-RULE-1 Pareto endpoint is what tests it].

---

## 1. The programme's own measured anchors (what any design must not contradict)

- The external verify-retry loop is the programme's only end-task positive
  (f2b-replicate +0.1507 at ~10% FLOPs, alignment-specific, formal inputs)
  [MEASURED: registry/verdicts/f2b-replicate.json — envelope in
  docs/next/feasibility-synthesis.md §2]. H-RULE asks whether moving the engine
  INSIDE the model beats that loop on Pareto frontiers (ASM-0806).
- Text-appended engine facts were NET-HARMFUL to a small host (g2d 0.76 → 0.43;
  0/24 rescues), and the residual-stream channel DELIVERS content at ECHO grade
  (keyacc 0.81/0.85) without resolving INTEGRATION (R− rescue 0/8)
  [MEASURED: registry/assessments/nsk1-{g2d,bprime2,stage1}.json, exploratory].
  Any H-RULE-ACT design inherits this caution directly.
- The NL front-end is a measured FAIL at scope (l3a-parse 47.6%, a5-nl 41.6% + S2
  fired) [MEASURED: registry/verdicts/{l3a-parse,a5-nl}.json] — so every NL leg of
  P3-E-RULE-1 is NLB-gated (ASM-0814) and this review's methods are evaluated on
  covered/formal slices first.
- Constrained decoding is TRANSPORT, not inference; attention maps are NOT causal
  provenance [STIPULATED: ASM-0815]. §2 and §6 test both stipulations against the
  literature; both survive, the second with strong independent support.

---

## 2. SQ1 — Constrained/grammar decoding WITH an external executor (H-RULE-CD)

### 2.1 The distinction that organizes the record

Executor-coupled CD is the decode-time relocation of the field's one proven
neuro-symbolic topology — neural author + deterministic external engine that owns
correctness (Logic-LM: +39.2% over standard prompting, +18.4% over CoT, with a solver in the loop —
abstract figures re-verified at the primary page 2026-07-11) [LIT: logic-lm-2023].

Grammar-only CD (masks from a CFG/regex/JSON schema) shapes the OUTPUT LANGUAGE and is a
solved transport problem: DFA mask stores eliminate JSON syntax errors and cut Python/Go
syntax errors 96% [LIT: syncode-2024], with near-zero serving overhead [LIT:
xgrammar-2025]. It derives nothing — without an engine the mask encodes only membership in
a language, which is why ASM-0815's "transport, not inference" is definitionally right.
**Executor-coupled CD** is the strictly stronger cell: a semantic engine (executor, type
system, static analyzer, completion engine) derives the VALID CONTINUATION SET from the
partial output's meaning, and the mask delivers that derivation. The lineage, verified:

- **Execution-guided decoding** (2018): execute partial SQL during beam decoding, prune
  faulty candidates; no retraining; then-SOTA 83.8% execution accuracy on WikiSQL across
  four model families [LIT: eg-decoding-2018]. Earliest clean instance.
- **PICARD** (EMNLP 2021): incremental parsing with schema-aware type-checking modes —
  already partially semantic; T5-3B to then-SOTA Spider/CoSQL, execution errors 12%→2%
  [LIT: picard-2021 — UNVERIFIED-THIS-PASS, carried from the 2026-07-09 parsing review].
- **Synchromesh / Constrained Semantic Decoding** (ICLR 2022): formalizes the "completion
  engine" — an oracle that, given a partial program, returns the set of valid
  continuations, enforcing syntax, SCOPE, TYPING, and contextual logic, with no
  retraining [LIT: synchromesh-2022]. This is the exact formal shape of H-RULE-CD: the
  kot-axiom engine is a completion engine over kot-query/1 (and over answer spans whose
  records it holds).
- **Monitor-Guided Decoding** (NeurIPS 2023): a static-analysis monitor (language-server
  protocol) computes type-consistent identifier continuations mid-decode.
  **SantaCoder-1.1B + MGD beats text-davinci-003** on compilation rate and
  next-identifier match on repository-level Java completion; gains consistent across
  scales [LIT: mgd-2023]. LOAD-BEARING: this is the only published result in our exact
  shape — tiny host + µs-class deterministic engine at the decode boundary — and it is at
  our rung (1.1B). Accounting: the same-model ± monitor comparison is a same-host
  ABLATION — the monitor's CPU-side static-analysis work and its decode-loop latency are
  real, unpriced resources, so this is an accuracy claim, not a resource-matched one; the
  cross-size headline (1.1B > 175B-class) is additionally a cross-model capability claim
  and is quoted here only in its same-model form. [LIT-BACKED: mgd-2023, read under this
  review's accounting discipline]
- **Type-constrained decoding** (PLDI 2025): prefix automata + inhabitable-type search
  make well-typedness soundly enforceable for TypeScript; compilation errors halved,
  functional correctness up on synthesis/translation/repair "across LLMs of various sizes
  and model families" [LIT: type-constrained-2025].
- **IterGen** (ICLR 2025): grammar-symbol-addressed BACKTRACKING with KV-cache reuse —
  decode, check a semantic predicate, resample the violating fragment; +18.5% mean over
  SOTA grammar-guided generation on SQL [LIT: itergen-2025]. Adds the missing control
  primitive (retract) that pure masking lacks.
- **CRANE** (ICML 2025): theory + method for the reasoning cost. Restricting output to an
  answer-only grammar provably reduces the model's usable computation; augmenting the
  grammar to admit intermediate reasoning, then constraining answer spans, recovers it —
  paper-reported accuracy of up to +10pp on GSM-symbolic/FOLIO over BOTH constrained and
  unconstrained baselines, same model, at slightly MORE generated tokens than
  unconstrained CoT (Table 1) — an accuracy win, not a resource-matched one
  [LIT: crane-2025].

### 2.2 The priced caveats (all confirmed; mitigation demonstrated only for the reasoning tax)

- **Distribution distortion**: greedy masking samples from a DIFFERENT distribution than
  the LM-conditioned-on-grammar; ASAp corrects it at extra sampling cost [LIT: gad-2024].
  For H-RULE-CD, where masks are exact engine derivations over COVERED spans, distortion
  applies to the residual freedom within the valid set — a measurable, second-order
  effect; pre-register a GAD-style likelihood audit rather than assuming it away.
- **Format/reasoning tax**: format restriction degrades reasoning, worse as constraints
  tighten [LIT: format-tax-2024]; constrained reflection can lock into
  format-satisfaction while semantic error detection collapses ("structure snowballing",
  Qwen3-8B) [LIT: cd-alignment-tax-2026]. Mitigation is exactly CRANE's: constrain ONLY
  the covered answer spans, leave reasoning tokens free — which is the H-RULE-CD design
  as already stated in §3.3 ("uncovered decode untouched").
- **The mask must include ABSTAIN**: no surveyed system constrains a span to
  {engine-valid continuations} ∪ {refusal} with fail-closed semantics when coverage is
  partial. LOAD-BEARING GAP: selective-span, coverage-aware, abstention-preserving CD is
  an EMPTY CELL in the literature — the programme would be first, which is the good kind
  of risk but must be built, not adopted [STIPULATED: gap claim from this survey; §9.2].

Scope of the mitigations: CRANE demonstrates the reasoning-tax mitigation on
GSM-Symbolic/FOLIO with specific hosts [LIT: crane-2025]; it does not close distribution
distortion (GAD's audit still needed), coverage-aware abstention (empty cell above),
semantic-monitor/executor cost (unpriced, §2.3), or arbitrary executor-coupled decoding
beyond those benchmarks. "Confirmed and priced" means each caveat has a named measurement
protocol, not that the placement is caveat-free. [STIPULATED: synthesis]

### 2.3 What beat which baselines, under what accounting

CD is the cleanest accounting in this whole review, but the correct claim is **same-host
ablation, not matched compute**: the canonical comparison is the SAME frozen model ±
mask, which controls the host but does NOT equalize resources under KOT-COST/2. The
constrained arm does extra work the papers do not price: mask/engine computation per
token, semantic-monitor calls (MGD's language-server analysis), backtracking re-decodes
(IterGen), and — where reasoning-admitting grammars are used — MORE generated tokens
than the unconstrained baseline (CRANE Table 1: 131.3 vs 129.0 at Qwen2.5-1.5B, 235.8
vs 212.2 at R1-Distill-Qwen-7B; more in nearly every reported arm) [LIT: crane-2025]. XGrammar's
near-zero overhead is measured for GRAMMAR-mask transport (context-independent-token
precheck, persistent stack) [LIT: xgrammar-2025]; it does NOT establish µs–ms cost for
semantic engines, per-token executor/kernel calls, or backtracking — extrapolating it to
engine-derived masks is an open engineering question, not a result (§9.2). Every §2.1
headline is therefore an ACCURACY claim on a fixed host, except the MGD cross-size quote
(flagged above) and PICARD's SOTA claims (fine-tuned parser + mask vs prior SOTA — a
systems claim, not an ablation). Two accounting obligations follow for Phase 1
[STIPULATED: hand-off requirement, frozen into §10]: (i) P3-E-RULE-1 must measure the
full resource vector — generated tokens, accelerator and CPU time, wall-clock latency,
energy, backtracking count, and executor work — for every arm, compared against H-VL
AND the neural/RAG frontier, not just the unconstrained twin; (ii) the reasoning-tax
control (a constrained run that loses reasoning tokens is not the same task) follows
CRANE's protocol [LIT: crane-2025]. [STIPULATED: synthesis]

### 2.4 Methods to adopt (P3-D-RULE inputs)

1. The **completion-engine formalization** [LIT: synchromesh-2022] as the interface spec
   for kot-axiom-as-decode-oracle (it gives the correctness obligations the engine must
   discharge: prefix-soundness, continuation-completeness).
2. **Span-scoped constraining** with free reasoning tokens (CRANE) + **backtracking on
   engine rejection** (IterGen) rather than mask-only.
3. **Likelihood-distortion audit** (GAD) and a **format-tax control arm** (same items,
   unconstrained + post-hoc engine check) as pre-registered controls.
4. Provenance: the engine's derivation trace gives exact **constraint/eligibility
   provenance** by construction (which continuations were licensed, and which records
   licensed them — record id per constrained span). It is causal ANSWER attribution only
   where the engine uniquely determines the span; where several continuations remain
   valid, WHY the LM picked one — and everything on unconstrained/uncovered spans — is
   outside the trace and needs §6's causal apparatus if claimed (§6).

---

## 3. SQ2 — KV-memory injection (H-RULE-KV)

### 3.1 The record

- **KBLaM** (ICLR 2025 — venue per the 2026-07-08 injection review; arXiv page re-fetched
  today): KB triples → fixed-length KV "knowledge tokens" via pre-trained sentence
  encoders + TRAINED linear adapters, read through rectangular attention; >10K triples
  into an **8B** host on one A100; overhead linear in KB size; base weights untouched but
  the projection is instruction-tuned on synthetic KBs [LIT: kblam-2025]. The authors'
  interpretability claim — "attention weights provide clear insights into how the model
  utilizes knowledge tokens... mimicking a soft retrieval process" [LIT:
  kblam-msr-blog-2025] — is precisely the evidence class §6 disqualifies as provenance
  (ASM-0815 independently corroborated: high attention to a record does not establish
  that the record caused the answer). Also from the primary blog: hallucination-reduction
  claimed only for KBs >~200 triples; "work to be done before it can be deployed at
  scale" [LIT: kblam-msr-blog-2025].
- **AtlasKV** (ICLR 2026): the scaling successor — KG2KV + hierarchical KV pruning push
  the same idea to ~1B triples in <20GB VRAM, sub-linear time/memory, no retraining for
  new knowledge [LIT: atlaskv-2026]. The line is alive and industrializing.
- **Memory Layers at Scale** (Meta 2024): TRAINED sparsely-activated KV memory layers
  replacing FFN capacity: beats dense baselines given >2× the compute, and beats MoE at
  matched compute AND params; up to 128B memory params over 1T tokens, base to 8B; gains
  concentrated on FACTUAL tasks [LIT: memory-layers-2024]. LOAD-BEARING for accounting:
  this is a genuine matched-FLOPs win — but it is a pretraining-time ARCHITECTURE (params
  up, memory trained end-to-end), i.e., prior art for H-GU/H-RULE-HL economics, not for
  bolting a deterministic rule store onto a frozen host.
- **Cache steering** (2025): training-free ONE-SHOT KV-cache intervention (vectors
  distilled from teacher reasoning traces) induces multi-step reasoning style in small
  models — SmolLM2-360M-class per the paper's experiments — with better hyperparameter
  stability and lower latency than continuous activation steering [LIT:
  cache-steering-2025]. The only training-free KV write demonstrated at OUR band; note it
  injects BEHAVIOUR (reasoning style), not content, and its vectors come from a teacher
  model, not an engine.
- **Larimar** (ICML 2024): external episodic memory conditioning the decoder; one-shot
  updates, 8–10× faster than locate-then-edit, comparable accuracy [LIT: larimar-2024] —
  memory-as-module rather than memory-as-KV; a trained bridge again.
- Interface-locality anchors, carried: kNN-LM (keys = the model's own hidden states)
  [LIT: knnlm-2020 — UNVERIFIED-THIS-PASS], Memorizing Transformers (memory = the
  model's own past KVs) [LIT: memorizing-transformers-2022 — UNVERIFIED-THIS-PASS]; the
  full retrieval lineage is owned by the injection report / RAG review [LIT:
  knn-lm-note-dedup]. 2026 continuations (MeKi ROM memory-experts for edge models [LIT:
  meki-2026]; FlashMem/dynamic-KV, KB recall only) all TRAIN the injection pathway.

### 3.2 Verdict for the placement

LOAD-BEARING [LIT-BACKED: kblam-2025, atlaskv-2026, memory-layers-2024, cache-steering-2025, larimar-2024; law per lit-llm-injection-priorart.md §3]: every working KV-side injection of CONTENT into a transformer runs through
a trained component (KBLaM/AtlasKV adapters + instruction tuning; memory layers trained
end-to-end; Larimar's trained memory module; cache steering's teacher-distilled vectors)
— the injection report's interface-locality law extends unbroken into 2026 [LIT:
kblam-2025, atlaskv-2026, memory-layers-2024, cache-steering-2025, larimar-2024;
EXTRAPOLATION as a law, per lit-llm-injection-priorart.md §3]. Two cells are EMPTY: (i)
KV injection demonstrated at ≤2B hosts (KBLaM/AtlasKV are 8B+; only behaviour-level cache
steering is in-band), and (ii) KV injection of RULES — content whose consumption requires
the host to EXECUTE an inference step the KV pair licenses — with causal validation of
that execution. (ii) is the H-RULE-KV bet, and §5's composition PRIOR predicts its failure
mode: the host must still COMPOSE the injected rule with query facts in-weights, which
is what transformers fail at in the controlled settings §5 surveys. The
literature-consistent variant is **KV injection of engine-DERIVED facts** (the engine
fires the rule per query; the KV pair carries the conclusion, keyed by kernel
content-hash), which demands only retrieval-shaped consumption — the shape KBLaM proves
at 8B. Because §5 is a prior, not a theorem, the design must carry BOTH arms:
KV-of-rule-premises stays in P3-E-RULE-1 as the explicit falsifier of §5's prediction,
alongside the derived-facts variant that the prior favours — the placement is tested,
not redefined away. [EXTRAPOLATION: design projection for P3-D-RULE; ASM-0806 is its
resolver]

---

## 4. SQ3+SQ4 — Activation steering / model editing (H-RULE-ACT) and adapter procedures (H-RULE-AD)

### 4.1 Steering: the positive line, then the correction

Positive line (2023–24): ITI lifts Alpaca TruthfulQA 32.5%→65.1% by shifting a few
attention heads along probe directions [LIT: iti-2023]; contrastive activation addition
steers Llama-2-Chat behaviours on top of finetuning/system prompts [LIT: caa-2024,
actadd-2023 — the latter UNVERIFIED-THIS-PASS]; function vectors show tasks live as
compact, transportable activation-space objects extracted by causal mediation [LIT:
function-vectors-2024]; RepE generalizes the reading/steering toolkit [LIT: repe-2023 —
UNVERIFIED-THIS-PASS].

The correction (2024–26), each verified today:

- Steerability is **highly variable across inputs**, substantially driven by spurious
  biases, brittle to reasonable prompt changes: "substantial limitations both in- and
  out-of-distribution" [LIT: steering-genrel-2024].
- Under an evaluation pipeline that fixes context-relevance/likelihood/baseline pitfalls,
  some RepE interventions are **less effective than previously reported**
  [LIT: steering-eval-2024].
- **AxBench** (Gemma-2-2B/9B — in/near our band): PROMPTING beats every
  representation-level steering method; finetuning second; SAE features not competitive
  [LIT: axbench-2025]. LOAD-BEARING [LIT-BACKED: axbench-2025]: on the only matched
  concept-steering harness at our scale, the text interface wins again — the same Law-2
  shape as the injection report.
- Across **36 models, 14 families, 1.5B–70B**, DoLa/function-vector/task-vector steering
  often yields no improvement or degradation; "fundamental flaws in the assumptions"
  [LIT: steering-off-course-2025].
- Mechanistic cause: steering fails when the target behaviour is **not represented by a
  coherent linear direction** — cosine similarity of training activation differences and
  pos/neg separation predict steerability [LIT: steering-unreliability-2025].

Direct rule-injection steering prior: **Dhanraj & Eliasmith** (EMNLP 2025) encode hidden
states into VSA vectors, run symbolic algorithms IN the vector space, decode and merge
back: 88.6% lower cross-entropy, 15.4× more rule-following math problems solved vs CoT
and LoRA baselines [LIT: vsa-rule-2025]. This is the strongest published H-RULE-ACT-shaped
result — and it is single-group, narrow-suite, unreplicated (the parsing/inner-symbolic
review's Thread-B caution stands), and structurally the nsk1 channel: the programme's own
measurement says delivery ≠ integration [MEASURED: nsk1 assessments, §1]. **ATLAS** (2026)
adds the executor-adjacent variant — a TRAINED verifier over latent states gates adaptive
steering, beating fixed steering on math/coding while cutting tokens [LIT:
atlas-steer-2026]; note the gate is learned, not deterministic, so its provenance is
PRM-grade, not engine-grade.

### 4.2 Editing: fact-rewrite, not rule-injection

ROME localizes factual recall to mid-layer MLPs and edits single associations (GPT-2 XL /
GPT-J) [LIT: rome-2022]; MEMIT scales to thousands (GPT-J-6B / NeoX-20B) [LIT:
memit-2023]; AlphaEdit's null-space projection lifts the whole locate-then-edit family by
avg 36.7% and fixes much of sequential-editing damage [LIT: alphaedit-2025]. Against
that: **localization does not inform editing** — the tracing signal does not predict the
best edit layer [LIT: hase-localization-2023]; edits fail to propagate entailed changes
and **a simple in-context baseline beats all parametric editors on RippleEdits** [LIT:
ripple-2024]; sequential editing produces gradual-then-catastrophic forgetting [LIT:
editing-scale-2024]; the field's own consolidation survey (KnowEdit) keeps all three
method families under evaluation rather than declaring a winner [LIT: knowedit-2024].
LOAD-BEARING [LIT-BACKED: ripple-2024, editing-scale-2024, alphaedit-2025, knowedit-2024]: nothing in the editing literature injects an INFERENCE RULE — every
benchmark item is a (subject, relation, object) rewrite; the ripple failures show that
even the CONSEQUENCES of one fact-edit (the simplest rule application imaginable) do not
propagate in-weights. Editing is maintenance tooling for parametric facts, and weak at
that; it is not a rule channel. [STIPULATED: synthesis of the verified rows above]

### 4.3 Adapters: procedures yes (softly), knowledge no

- Knowledge injection via adapters/fine-tuning, measured against in-context alternatives
  on the same host (accuracy comparisons; matched lifecycle/tuning compute NOT
  established in these studies), loses: RAG > unsupervised FT for both existing and new knowledge, and new
  facts need many paraphrase repetitions to enter at all [LIT: ovadia-ft-vs-rag-2024];
  new-knowledge examples are learned slowly and, once learned, linearly increase
  hallucination [LIT: gekhman-2024]; LoRA-encoded documents (parametric RAG) give
  "high-level guidance but limited evidence consolidation" and underperform token-level
  RAG alone [LIT: prag-2026]. K-Adapter/map-tuning wins were task-local, KEPLM-era, with
  the trained-bridge requirement throughout [LIT: k-adapter-2020,
  plugplay-injection-2023].
- Procedures/skills in weight space are more modular than facts: task vectors compose by
  arithmetic [LIT: task-arithmetic-2023]; LoRA modules compose gradient-free to few-shot
  ICL parity on unseen BBH tasks [LIT: lorahub-2024]. But "few-shot parity" is the
  ceiling anyone has shown, reliability is interference-bound, and NOTHING gives
  soundness or fail-closed behaviour.

Verdict for H-RULE-AD: adapters are the right vehicle for trained BEHAVIOURS the host
needs around the engine (e.g., "consult/format/defer" procedures — the A2/E5 bridge
precedent), and the wrong vehicle for the rules themselves: rule-as-adapter has no
soundness story, no provenance, no fail-closed mode, and the knowledge-side evidence
predicts hallucination amplification when the adapter's rule half-fires. Matches §3.3's
"no — must be measured" row; the literature says measure it LAST among the shallow
placements. [STIPULATED: placement ruling input]

---

## 5. SQ5 — Where inference CAN and CANNOT be baked in (the composition wall, read as a falsifiable prior)

Four independent lines, all verified today, converge:

1. **Storage ≠ manipulation.** Models with perfectly stored (name, attribute) knowledge
   fail simple CLASSIFICATION and COMPARISON over it unless CoT is used at BOTH training
   and inference; inverse search is ~0% regardless of prompt [LIT: physics-3.2-2024].
2. **Depth theory.** Bounded-depth transformers cannot directly produce answers to basic
   arithmetic/equation problems unless size grows super-polynomially in input length;
   constant-size autoregressive transformers WITH CoT tokens can [LIT:
   cot-depth-theory-2023]. Multi-step inference must surface into token space — or into
   an external engine, which is the same theorem read from the other side.
3. **Latent multi-hop is unreliable.** Two synthetic facts do not compose latently even
   after fine-tuning (synthetic+natural sometimes does) [LIT: twohop-2025]; grokked
   composition circuits generalize in-distribution but FAIL OOD, while comparison
   circuits generalize — circuit topology, not content quality, decides transfer [LIT:
   grokked-2024]; when two-hop fails, the second hop resolves TOO LATE in the layer
   stack, and back-patching a later state into an earlier layer rescues up to 66% of
   failures [LIT: hopping-2024]. Directionality is not even closed under inversion
   (reversal curse: GPT-4 79% forward vs 33% reverse) [LIT: reversal-2024].
4. **The one honest matched-compute bake-in win is architectural and trained**: memory
   layers beat dense at matched FLOPs by adding TRAINED lookup capacity — for FACTUAL
   recall, not multi-step inference [LIT: memory-layers-2024].

LOAD-BEARING (the placement PRIOR this review hands P3-D-RULE — a strong, falsifiable
prior with the burden of proof attached, NOT a proven architectural law): **the verified
record contains no instance of reliable depth-≥2 rule application inside a frozen (or
lightly adapted) forward pass; everything demonstrated to bake in or inject is (a)
single-hop lookup-shaped content and (b) trained BEHAVIOURS/styles.** Scope of the
evidence, stated honestly: the theory concerns constant-depth/log-precision transformers
on particular arithmetic/equation constructions — an asymptotic result that does not
prove impossibility for finite-length rule tasks, latent recurrent mechanisms, deeper
hosts, or trained adapters [LIT: cot-depth-theory-2023]; physics-3.2 is a controlled
synthetic knowledge-manipulation study, not a universal theorem about all rule
composition [LIT: physics-3.2-2024]; the two-hop/grokking rows are synthetic-fact
constructions with known partial escapes (grokked in-distribution circuits;
synthetic+natural mixes) [LIT: grokked-2024, twohop-2025]. What the four lines jointly
license is a DEFAULT and a burden: internal placements should deliver engine RESULTS
(derived facts, valid continuation sets) rather than rule PREMISES, and any placement
that requires host-side composition (KV-of-rules, AD-of-rules, HL) must carry the
burden of proof — which means those arms are KEPT as pre-registered falsifiers of this
prior (§3.2, §10), not excluded by it [EXTRAPOLATION: from rows 1–4; P3-E-RULE-1's G2
stages test it per placement]. This independently supports — and sharpens — the
stipulated CD → KV →
{AD, ACT} → HL ordering (ASM-0802): CD delivers derivations at the boundary (no host
composition), KV-of-derived-facts asks for lookup only, AD/ACT ask for behaviour change
plus composition, HL asks for everything at architecture-surgery cost.

**H-RULE-HL corollary (bottleneck architectures).** Concept-bottleneck models achieve
competitive accuracy at small scale with test-time concept intervention [LIT: cbm-2020],
and CB-LLMs claim classification parity + controlled generation inside LLMs [LIT:
cbllm-2025] — but concept LEAKAGE is documented: bottleneck units "do not correspond to
anything semantically meaningful in input space", failing interpretability/intervenability
goals [LIT: cbm-leakage-2021]. Naming units is not interpretability (§3.3's own words,
now with citations); an HL placement would need §6-grade causal validation of every
pinned unit PLUS a general-capability non-inferiority gate (the bottleneck-throttling
risk is real and unmeasured at generative-LLM scale). Nothing in the verified record
makes HL urgent; everything makes it expensive. [STIPULATED: placement ruling input]

---

## 6. SQ6 — Causal-provenance validation practice (what counts as evidence)

**Attention maps are not provenance.** Attention weights are frequently uncorrelated with
gradient importance measures, and adversarially different attention patterns produce
identical predictions [LIT: attention-not-expl-2019]; the strongest defense of attention
explanations concedes they require diagnostic tests (uniform baselines, seed variance,
frozen-weight diagnostics) and never license stand-alone claims [LIT:
attention-not-not-2019]. KBLaM's "attention shows knowledge use" is therefore
descriptive telemetry, not provenance [LIT: kblam-msr-blog-2025; STIPULATED: ASM-0815
corroborated].

**Causal methods are necessary — and have their own measured failure modes**, each of
which becomes a pre-registered control in P3-D-RULE's instrumentation:

| Threat | Evidence | Control to pre-register |
|---|---|---|
| Localization ≠ intervention success | causal tracing does not predict best edit layer [LIT: hase-localization-2023] | never infer "edit/inject HERE" from tracing alone; test the intervention directly |
| Protocol sensitivity | patching conclusions flip with metric (prob vs logit-diff vs KL) and corruption method [LIT: patching-best-2024] | fix metric suite in advance; report all three |
| Self-repair masks effects | ablating one attention layer recruits downstream compensation (Hydra effect) [LIT: hydra-2023] | resampling ablations over single-point ablations; effect sizes vs compensation-aware baselines |
| Dormant-pathway illusions | subspace patching can change behaviour via causally-disconnected parallel pathways [LIT: subspace-illusion-2023] | full-rank + random-subspace controls; require agreement |
| Hypothesis under-specification | causal scrubbing's resampling-ablation discipline [LIT: causal-scrubbing-2022 — UNVERIFIED-THIS-PASS at source, anchored via the verified causal-abstraction survey] | state the causal graph being claimed BEFORE intervening |
| Framework | interchange interventions / causal abstraction unify patching, scrubbing, tracing, steering [LIT: causal-abstraction-2025] | state per-placement provenance claims as causal-abstraction claims |

**The per-placement provenance ladder this review hands P3-D-RULE** [STIPULATED:
synthesis; the design bead freezes it]:

- **CD**: the ENGINE'S DERIVATION TRACE (record id per constrained span) is exact
  **constraint/eligibility provenance** by construction — it proves the continuation was
  licensed and by which records, with zero interpretability apparatus. It is causal
  ANSWER attribution only where the engine uniquely determines the span; where multiple
  continuations remain valid, or on unconstrained/uncovered spans, the trace attributes
  nothing and any causal claim needs the apparatus above. This is still the only
  placement where any provenance grade comes free; P3-D-RULE must state provenance
  sufficiency PER SPAN TYPE (uniquely-determined / multi-valid / uncovered).
- **KV**: knowledge-token ablation + INTERCHANGE interventions (swap record KVs between
  matched queries; the answer must follow the record, echo-vs-integration distinguished à
  la nsk1's derangement controls [MEASURED: nsk1 protocol]) + executor trace of what the
  engine derived. Attention maps: descriptive only.
- **ACT**: activation patching under the fixed metric suite + cross-seed steering-vector
  stability (steering's coherent-direction failure mode [LIT:
  steering-unreliability-2025]) + dormant-pathway controls [LIT: subspace-illusion-2023].
- **AD/HL**: behavioural counterfactuals with matched controls (shuffled-rule adapters;
  leakage probes for HL per [LIT: cbm-leakage-2021]); no unit-naming accepted as
  evidence.

---

## 7. Scale accounting — what is actually demonstrated at 100M–2B

| Placement | In-band (≤2B) evidence | Out-of-band only |
|---|---|---|
| CD+executor | MGD on SantaCoder-1.1B (and smaller code models) [LIT: mgd-2023]; type-constrained across sizes incl. small [LIT: type-constrained-2025]; grammar transport at any size [LIT: syncode-2024, xgrammar-2025] | Synchromesh (GPT-3/Codex) [LIT: synchromesh-2022]; CRANE hosts mostly >2B [LIT: crane-2025] |
| KV injection | cache steering (SmolLM2-360M-class; behaviour only) [LIT: cache-steering-2025] | KBLaM 8B; AtlasKV; memory layers (base to 8B, trained) [LIT: kblam-2025, atlaskv-2026, memory-layers-2024] |
| Steering | AxBench Gemma-2-2B (prompting wins) [LIT: axbench-2025]; steering-off-course from 1.5B (unreliable) [LIT: steering-off-course-2025] | ITI/CAA at 7B+ [LIT: iti-2023, caa-2024]; VSA-rule (host size unstated in abstract) [LIT: vsa-rule-2025] |
| Editing | ROME GPT-2-XL 1.5B [LIT: rome-2022] | MEMIT/AlphaEdit at 6B+ [LIT: memit-2023, alphaedit-2025] |
| Adapters | K-Adapter (RoBERTa-large 355M) [LIT: k-adapter-2020] | LoraHub/task-arithmetic hosts vary |
| HL bottleneck | CBMs at small vision scale [LIT: cbm-2020] | CB-LLM hosts [LIT: cbllm-2025] |

LOAD-BEARING [LIT-BACKED: table rows above, each source-keyed; the ranking sentence is this review's reading]: the placement with the STRONGEST in-band evidence is CD+executor; the
placement with the WEAKEST is KV (nothing content-level ≤2B). The in-band steering
evidence is predominantly NEGATIVE (AxBench, steering-off-course).

---

## 8. Capability-limited vs fundamental (per prior failure/limit, the §5-mandated judgement)

| # | Limit / failure | Judgement | Why |
|---|---|---|---|
| 1 | Grammar-only CD derives no inference | **Definitional** — transport, not inference (ASM-0815 confirmed) | the mask encodes language membership; the executor supplies semantics [LIT: synchromesh-2022, mgd-2023] |
| 2 | CD reasoning/format tax | **Instrument-limited, mitigation demonstrated** | span-scoped constraints + reasoning-admitting grammars recover accuracy on the same host, at modestly more generated tokens (not resource-matched) [LIT: crane-2025, format-tax-2024] |
| 3 | CD distribution distortion | **Instrument-limited** | ASAp corrects at sampling cost; second-order for exact-derivation masks [LIT: gad-2024] |
| 4 | KV injection needs a trained bridge | **Fundamental as a pattern** (interface-locality law, unbroken 2020→2026) | every working system trains the pathway [LIT: kblam-2025, atlaskv-2026, memory-layers-2024; injection report §3] |
| 5 | No KV-rule injection with validated inference | **Empty cell** — untested, not failed | the H-RULE-KV bet; §5 predicts the failure mode and dictates the derived-facts variant [EXTRAPOLATION] |
| 6 | Steering unreliability | **Substantially fundamental** for behaviours without a coherent linear direction [LIT: steering-unreliability-2025]; instrument-limited residue (better extraction/eval helps in-distribution [LIT: steering-eval-2024]) | representation geometry, not extraction quality, is the binding constraint; and prompting already wins at matched conditions [LIT: axbench-2025] |
| 7 | Editing ripple/sequential failures | **Fundamental as formulated** | distributed storage + in-context superiority; AlphaEdit mitigates damage, does not add rule semantics [LIT: ripple-2024, editing-scale-2024, alphaedit-2025] |
| 8 | In-weights multi-step rule application | **Strong falsifiable prior, burden-shifting** — proved only for bounded-depth asymptotics on specific constructions; measured only in controlled synthetic settings; does not rule out finite-length tasks, latent recurrence, deeper hosts, or trained adapters (§5 scope) | theory + three empirical lines converge on the default: externalize (CoT or engine); composition-requiring arms stay as falsifiers [LIT: cot-depth-theory-2023, physics-3.2-2024, twohop-2025, grokked-2024] |
| 9 | Adapter knowledge injection underperforms text | **Fundamental as formulated; capability-obviated** (stronger hosts read text better) | same-host comparisons consistently favour in-context — noting these test knowledge, not rules, and matched lifecycle/tuning compute is NOT established [LIT: ovadia-ft-vs-rag-2024, gekhman-2024, prag-2026]; consistent with injection report Law 2 |
| 10 | CBM/HL unit leakage | **Instrument-limited in principle** (causal validation can rescue specific units) but **economically dominated** | leakage documented [LIT: cbm-leakage-2021]; validation cost per unit is the real price; nothing makes HL urgent [LIT: cbllm-2025] |
| 11 | nsk1 integration gap (internal delivery ≠ use) | **Unresolved at scope, both sides measured** [MEASURED: nsk1] | the VSA-rule EMNLP-2025 result [LIT: vsa-rule-2025] is the strongest counter-signal; single-group, must be replicated at our rung before load-bearing use |

---

## 9. What this review settles, and what it leaves open

### 9.1 Settled (with the evidence class stated)

1. The CD → KV → {AD, ACT} → HL test ordering is literature-supported, not merely
   cheapest-first (ASM-0802's prior ordering gains independent support) [STIPULATED
   ruling over §§2–5 verified rows].
2. H-RULE-CD is buildable from established parts (completion-engine spec + masking +
   backtracking + span-scoping), with same-host ablation precedent at 1.1B and exact
   constraint/eligibility provenance by construction (causal answer attribution only on
   uniquely-determined spans, §6) [LIT: mgd-2023, synchromesh-2022, itergen-2025,
   crane-2025]. Resource-matched superiority under KOT-COST/2 is UNDEMONSTRATED in the
   literature and is exactly what P3-E-RULE-1 must measure (§2.3).
3. ASM-0815 (attention ≠ provenance; causal validation required) is independently
   corroborated by the attention-explanation literature and the KBLaM line's own claims;
   §6's threat/control table is ready to freeze into P3-D-RULE instrumentation.
4. H-RULE-KV leads with KV-of-engine-DERIVED-facts (lookup-shaped consumption), with a
   KV-of-rule-premises arm RETAINED as the pre-registered falsifier of §5's composition
   prior (composition-shaped consumption) — the prior assigns the burden of proof, it
   does not delete the arm [EXTRAPOLATION, to be tested].
5. H-RULE-ACT enters Phase-2 only as a replication-shaped bet (VSA-rule at our rung with
   nsk1-grade derangement/integration controls), not as a primary lane [STIPULATED
   ruling; LIT: vsa-rule-2025 + MEASURED: nsk1].
6. H-RULE-AD is re-scoped: adapters LEAD as vehicles for AROUND-engine behaviours
   (consult/format/defer); a rule-as-adapter arm is retained, measured LAST among the
   shallow placements, as the AD-side falsifier of §5's prior — not designed out
   [STIPULATED ruling over §4.3, burden per §5].
7. HL stays deferred (ASM-0802 unchanged); CBM leakage adds a named validation cost no
   shallower placement pays [LIT: cbm-leakage-2021].

### 9.2 Open questions for Phase-1 (P3-D-RULE must answer in design)

- **The abstention-preserving selective-span CD cell is empty** (§2.2): what is the
  correct mask when a span is UNCOVERED — free decode + fail-closed post-check, or
  refusal-token insertion? Both are designable; neither has prior art.
- Does engine-derived masking distort the within-valid-set distribution enough to matter
  on our verticals (GAD audit, §2.2)?
- Can the kot-axiom engine discharge Synchromesh's completion-engine obligations
  (prefix-soundness, continuation-completeness) over kot-query/1 at µs cost per token?
  (Engineering question; plausibly yes given 5–8 µs/query [MEASURED: l3a/a5 verdicts],
  but per-TOKEN calls change the constant, backtracking multiplies it, and XGrammar's
  near-zero grammar-transport number does NOT transfer to executor-derived masks (§2.3)
  — this must be measured, not assumed.)
- KV-of-derived-facts at ≤2B: does the KBLaM shape work at all below 8B, and does it need
  the trained projection (it will — interface-locality); what is the projection's
  training budget under KOT-COST/2 matched accounting?
- What Pareto endpoint operationalization (§3.3: accuracy-on-covered-slice, coverage,
  p95 latency, resource vector) lets CD and KV be compared to H-VL WITHOUT an NL leg
  before NLB clears? (Formal-input legs first; NL legs NLB-gated per ASM-0814.)
- Replication spec for VSA-rule-steering at our rung: which of its tasks map onto
  kernel-covered content, and what does its trained encode/decode cost under matched
  accounting?

---

## 10. Phase-1 hand-off

**Design bead to create (per the Phase-0 table; this bead's named spawn):**

- **P3-D-RULE** [DESIGN] P1 — blocked by P3-LR-RULE (this document, revised 2026-07-11
  per the independent GPT-5.6 review; closure of `kernel-of-truth-s55r.8` is the
  coordinator's call, and the bead remains `in_progress` at export) + P3-LR-NTP (in
  flight separately — the co-blocker stands; nothing here pre-empts it). Deliverable per
  §5 rev-2: H-RULE placement designs, **CD+KV first**, causal-provenance
  instrumentation, Pareto endpoint (§3.3); spawns P3-E-RULE-1. Opening inputs now
  answered by this review: the placement ordering rationale (§5, §8), the CD design
  template and its three pre-registered controls (§2.4), the KV derived-facts-lead +
  rule-premise-falsifier constraint (§3.2), the ACT replication-not-primary ruling
  (§9.1.5), the AD re-scope with retained falsifier arm (§9.1.6), the per-placement
  provenance ladder + threat/control table to freeze (§6), and the scale-gap register
  (§7: no content-level KV precedent ≤2B — the design must budget for being first).

**Acceptance/kill criteria P3-D-RULE MUST make explicit before P3-E-RULE-1 freezes**
[STIPULATED: hand-off contract; the design bead pre-registers the numbers, this review
only names the obligations]:

1. **KOT-COST/2 + lifecycle accounting** — every arm reports the full resource vector
   (generated tokens, accelerator + CPU time, p50/p95 latency, energy, backtracking
   count, executor/monitor work) AND lifecycle costs (any trained bridge/projection/
   adapter training budget); same-host ablations are not accepted as "matched compute"
   (§2.3).
2. **G1 coverage-ceiling gate** — endpoints scored on covered slices with coverage
   reported; a placement that wins only by shrinking coverage fails.
3. **Matched controls** — a generic RAG/tool-use arm and an unconstrained + post-hoc
   engine-check arm (§2.4's format-tax control) run alongside every constrained arm;
   comparisons target H-VL AND the neural/RAG frontier, not just the unconstrained twin.
4. **KV rule-premise vs derived-fact arms** — both pre-registered; the rule-premise arm
   is §5's falsifier, with its predicted failure mode stated in advance (§3.2).
5. **Provenance sufficiency by span type** — claims graded per §6's ladder:
   constraint/eligibility provenance vs causal answer attribution
   (uniquely-determined / multi-valid / uncovered spans stated separately).
6. **Declared dependencies** — the design names its couplings to the shared frontier
   operationalization, index/retrieval baseline, hardware profile, and the NLB gate
   (ASM-0814); NL legs stay gated.

Governance note: this session does not run `bd`; the coordinator creates P3-D-RULE with
the above as its opening description, citing this file. No KB shard/index mutated; new
sources staged in `RULE.sources.jsonl` for central ingest.

**Verified/unverified source counts:** 65 sources in `RULE.sources.jsonl`; 58
`verified:true` (primary URL fetched by me 2026-07-11 — `verified:true` asserts URL
fetch + abstract/landing-page consistency with the claim field, NOT independent
re-derivation of every body figure; rows re-checked during the 2026-07-11 revision
carry explicit version/date/locator fields), 7 `verified:false` (carried from prior
verified in-repo reviews or KB recall, flagged UNVERIFIED-THIS-PASS in-line:
picard-2021, knnlm-2020, memorizing-transformers-2022, actadd-2023, repe-2023,
causal-scrubbing-2022, plus the knn-lm-note-dedup pointer row; logic-lm-2023 was
re-verified at its primary page 2026-07-11). Proposed follow-up (in-doc; no registry
write from this session): a locator retrofit pass adding source version/date +
page/table/section locators to every remaining quantitative decision-bearing row in
`RULE.sources.jsonl`.

**Consistency link:** nothing here contradicts `docs/next/feasibility-synthesis.md` — the
external loop remains the only measured end-task positive; this review explains WHY the
literature expects the decode-boundary placements to be the first internal challengers
and equips P3-E-RULE-1 to test that expectation rather than assume it.
