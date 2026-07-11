# P3-LR-NTP — Neural Theorem Proving, Differentiable Logic, Neural Algorithmic Reasoning, Proof-Trace Distillation

**Kernel of Truth Programme-3, Phase-0 literature review.**
Author: Fable (Claude Fable 5, literature-researcher discipline), 2026-07-11.
Revised 2026-07-11 per external review `poc/gpt56-review/rev-NTP-20260711b` (GPT-5.6):
miniF2F-v2 direction corrected; "matched" ledger downgraded to one same-compute claim + four
component ablations; pass@32 relabelled sample count (not compute) with MoE qualification;
latency/plateau/free-generation claims re-scoped; closures/novelty claims converted to
scoped Phase-1 prioritization decisions; oracle/API-gate requirement added to hand-off.
Bead: `kernel-of-truth-s55r.6` (P3-LR-NTP, programme rev-2 §5 Phase-0 table, P1).
Feeds (Phase-1): **P3-D-GU** (co, with P3-LR-TINY + P3-LR-FUSE), **P3-D-RULE** (co, with
P3-LR-RULE), **P3-D-PS** (co, with P3-LR-PARSE).

**Epistemic contract.** Every load-bearing line carries [MEASURED|STIPULATED|EXTRAPOLATION];
literature claims carry `[LIT: <id>]` keys into `docs/next/lit/NTP.sources.jsonl`
(one JSON object per source; `verified:true` = primary page fetched by me 2026-07-11 at the
URL given AND the claim text checked against that page at abstract/headline level —
it attests that the source, venue-as-stated, and headline numbers are real; it does NOT
attest independent re-derivation of ablations, resource comparisons, or full-paper details,
which remain at the cited papers' own accounting — for six sources the arXiv abstract page
does not display the venue and the venue is flagged `[memory]` in the jsonl; where a
specific number is load-bearing its metric definition is stated in-line; `verified:false` =
carried from a prior verified review, KB recall, or search snippet, NOT page-fetched —
flagged in-line as UNVERIFIED-THIS-PASS).
KB/lit records are recall infrastructure, not evidence; nothing here amends any registry
object. [MEASURED] on a literature line means "measured by the cited paper, at ITS scope";
programme-internal measurements always name their registry object.

**Dedup statement (what already exists; this review builds on, does not repeat):**
- `docs/next/lit/RAG.md` (2026-07-11) — owns **learned neural verifiers as inference-time
  baseline components** (Cobbe outcome verifiers, Math-Shepherd PRMs, Small-LMs-need-strong-
  verifiers) and the test-time-compute comparator recipe. §5 below covers the *training-time*
  side (executor/verifier in the loss or loop) and only re-anchors the scaling-flaws result
  where the sound-vs-learned distinction is decision-relevant.
- `reports/lit-structured-parsing-and-inner-symbolic.md` (2026-07-09) — owns
  grammar/type-constrained decoding, the SATNet label-leakage cautionary tale, NVSA/in-algebra
  rule evaluation, and the "DeepProbLog/Scallop/LTN are module-scale" one-liner. §2 below
  extends that one-liner into the matched-baseline accounting the Phase-0 question demands.
- `reports/lit-llm-injection-priorart.md` — rule-injection placements; not re-covered
  (P3-LR-RULE extends it); §6 hands H-RULE only the executor-side findings.
- `docs/next/lit/PARSE.md` (2026-07-11) — owns execution-guided decoding/selection
  (EGD/MBR-EXEC/LEVER [LIT: lever-2023, UNVERIFIED-THIS-PASS]) and TinyGSM as pipeline
  analogy; re-anchored not re-argued.
- lit-KB (`kb/records/`) already holds directly relevant records: Logic-LM
  (`arxiv_2305.12295`), scaling-flaws (`arxiv_2502.00271`), Intermediate-Languages-Matter
  (`arxiv_2502.17216`), Safe/formal-step-verification (`doi_10.18653_v1_2025.acl-long.594`),
  the PRM cluster (RAG.md §0 lists it). New sources found here are staged in
  `NTP.sources.jsonl` for the coordinator's central ingest — **no KB shard/index is mutated
  by this bead** (governance).
- No prior programme document covers neural theorem proving proper, NAR, or proof-trace
  distillation — that is this document's net-new ground.

---

## 0. Executive verdict (one paragraph)

The strongest, most-replicated finding in this scope is that a **sound deterministic checker
sitting in a training loop** — filtering self-generated proofs (expert iteration), providing
RL reward, or supplying error messages for self-correction — reliably improves a neural
proposer, with one demonstration whose own abstract claims **equal-compute** superiority
[LIT: polu-curriculum-2022: expert iteration beats proof-search-only at equal compute, per
the paper's claim] and a 2025–26 trend of **recipe-over-parameters** results (8B and even
4B provers beating a 671B prover under the same pass@32 **sample count** — a shared metric,
NOT matched compute: tokens, wall-clock, and search overhead are unpinned, and the 671B
comparator is fine-tuned from an MoE base with ~37B activated per token, so these are
total-parameter-efficiency results, not active-compute ratios [LIT: goedel-v2-2025,
pythagoras-2026, dsprover-v2-2025, deepseek-v3-2024]). The flagship small-scale existence
proof is AlphaGeometry: a 151M LM trained purely on engine-generated synthetic proof traces,
proposing constructions to a deterministic symbolic engine, reaching near-gold IMO geometry
[LIT: alphageometry-2024] — though its search budget (beam 512 × 10,000 CPU workers) and
AlphaProof's ~180k TPU-days [LIT: alphaproof-2025] mark this family's headline results as
**maximally unmatched-compute**; the core with defensible accounting is much smaller
(§1.2–1.3). Differentiable logic has **no matched-baseline win beyond toy KBs and module
scale found in this search**, and the at-scale gains in that space have come from a
separate, coexisting external-solver line, not in-loss logic (§2). NAR
shows that hard **discrete interfaces buy OOD transfer on covered algorithmic tasks**
[LIT: discrete-nar-2025] while trace-trained plain transformers shortcut and fail OOD
[LIT: paradox-2022, prontoqa-2023, anil-lengthgen-2022] — jointly, the literature's cleanest
argument FOR the programme's bet shape (deterministic engine owns execution/search; small LM
owns proposal/surface) and AGAINST hoping distilled traces alone induce a reasoner.

## 1. Neural theorem proving: proposer + sound checker

### 1.1 State of the art, and what exists at 100M–2B

The field's architecture has been stable since 2020: a generative LM proposes proof steps
(or whole proofs), a **sound proof checker** (Metamath/Lean/Isabelle kernel) validates, and
a search procedure allocates samples [LIT: gptf-2020, htps-2022]. The standard yardstick is
miniF2F (488 olympiad/coursework statements, cross-system) [LIT: minif2f-2022]. Frontier
solve rates are now very high — miniF2F-test 84.6% pass@32 at 8B, 88–93% at 32B
[LIT: goedel-v2-2025, pythagoras-2026], with the 671B comparator's own page fetched this
revision (its pass@32 figures as comparison targets remain those reported in the
challengers' tables) [LIT: dsprover-v2-2025] — but **no current frontier prover
is ≤2B**. What exists in/near our band:

- **ReProver (299M ByT5 + premise retrieval)** — the ≤2B anchor. LeanDojo Benchmark Pass@1
  51.2% (random split) / 26.3% (novel-premises split); miniF2F 26.5%; trained in ~1 GPU-week
  on one A100 vs "thousands of GPU-days" for prior systems [LIT: leandojo-2023] [MEASURED at
  its scope]. Two accounting reads: vs its own no-retrieval twin (47.6%/23.2%) the retrieval
  win is a **controlled component ablation** (same model, same sample count; retrieval's own
  index/query cost is uncharged, so not resource-vector-matched — §1.2); vs GPT-4 zero-shot
  (29.0%/7.4%) it is finetuned-vs-few-shot, i.e., the distill-sbs caveat applies (§4.3).
- **GPT-f (160M–1.5B)** — best 56.22% held-out Metamath at **700M**; larger was not always
  better at fixed data/search [LIT: gptf-2020]. Expert-iteration sampling cost ~20k V100
  GPU-hours per iteration — the checker is sound but the LOOP is expensive.
- **Graph2Tac (GNN-scale, Coq)** — online learning of new definitions; ≥1.48× more theorems
  than CoqHammer/Proverbot9001/a transformer baseline; with a k-NN co-solver, 1.5× over its
  own offline twin [LIT: graph2tac-2024]. Evidence that tiny non-transformer provers with
  **definition-online-learning** beat bigger offline ones in interactive proving; matching
  of the cross-system comparisons is not stated.
- **AlphaGeometry's LM is 151M** (excl. embeddings), trained from scratch on 100M
  engine-generated synthetic theorem+proof traces [LIT: alphageometry-2024] — inside our
  band on parameters, far outside on search (§1.3).

**Trend line (load-bearing for sizing):** total parameter count is not the binding axis in
this domain. Goedel-Prover-V2-8B beats DeepSeek-Prover-V2-671B under the same pass@32 metric
at 80× fewer total parameters [LIT: goedel-v2-2025]; Pythagoras-Prover-4B does the same at
~167× fewer [LIT: pythagoras-2026]; both attribute the win to verifier-coupled data recipes
(scaffolded / curriculum synthesis, compiler-feedback self-correction), not architecture.
**MoE qualification (mandatory when quoting these ratios):** the 671B comparator is
fine-tuned from DeepSeek-V3-Base, a mixture-of-experts model with ~37B parameters activated
per token [LIT: dsprover-v2-2025, deepseek-v3-2024], so the active-parameter ratios are
~5×/~9×, not 80×/167×; and equal pass@32 pins only the sample count — these results
establish **parameter efficiency under a common metric**, not matched total compute, and do
not license "parameters are non-binding". [EXTRAPOLATION:
that this trend continues below 2B is NOT established — no frontier-recipe prover has been
published at ≤2B; this is an explicit Phase-1 open question, §7-Q1.]

### 1.2 What beat controlled baselines, under what accounting

Skeptically filtered, the ledger is **one same-compute claim plus four controlled component
ablations** — NOT five resource-matched wins. Per the programme's own resource-vector rule
(KOT-COST/2: no scalar diagnostic alone licenses "compute-matched" [STIPULATED: programme-3
ASM-0810]), sharing the base model and pass@k does not establish resource-matching:
retrieval calls, auxiliary training objectives, compiler retries, and ATP calls all add
cost the cited pages do not charge to the comparison. Only item 1's paper itself claims
equal compute.

1. **Expert iteration vs proof-search-only at equal compute budget** [LIT:
   polu-curriculum-2022] — the single cleanest result in the field for our purposes, and
   the only entry here whose own abstract claims same-compute superiority (the claim is the
   paper's; its resource vector is not independently audited): putting the sound checker's
   verdicts back into TRAINING beats spending the same compute on more search. It also
   self-organizes a difficulty curriculum from unordered statements.
2. **Retrieval vs no-retrieval, same 299M model, same k** [LIT: leandojo-2023] — +3.6/+3.1
   points; modest but honest. Component ablation: retrieval's index build and per-query
   cost are uncharged.
3. **Proof-artifact co-training vs same model without it**, 32%→48% on held-out Lean
   theorems [LIT: pact-2021] — auxiliary self-supervised tasks harvested from checker-level
   artifacts are cheap signal. Component ablation: the extra training objective's data and
   compute are uncharged.
4. **Hammer+LM division of labour vs LM-only**, PISA 39%→57%, +8.2% solved by neither
   component alone [LIT: thor-2022] — complementarity of neural proposal and deterministic
   automation is additive, not just substitutive. Component ablation: the ATP calls add
   cost outside the shared budget.
5. **Verifier-guided self-correction** (revise on Lean compiler messages) as an ablatable
   component: +2.3 points at 32B (88.1→90.4 pass@32) [LIT: goedel-v2-2025]. Component
   ablation: correction rounds consume extra tokens/compiler calls within the pass@32
   protocol.

The **unmatched** headline results, named as such: HTPS's 82.6% Metamath (vs GPT-f 56.5%)
rests on online training plus large search, with no compute-matching stated [LIT: htps-2022];
Kimina's 80.7% is at pass@8192 — a 256× larger sample budget than the pass@32 rows it is
often tabled against [LIT: kimina-prover-2025, UNVERIFIED-THIS-PASS]; AlphaProof's IMO
silver used a 3B model but ~80,000 TPU-days of RL plus ~100,000 TPU-days of
auto-formalization, and Test-Time RL trains on variants of the single target problem
[LIT: alphaproof-2025] — an existence proof, not an economics proof.

**Benchmark-quality flag:** >half of original miniF2F statements are misaligned with their
informal versions. On an end-to-end (understand→formalize→prove) pipeline, the best system
reaches only ~36% on original miniF2F — despite 97% autoformalization / 69% proving reported
component-wise — and **improves to 70% on the corrected v2** [LIT: minif2f-v2-2025;
re-verified at abstract 2026-07-11]. The correction RAISES end-to-end accuracy; what it
exposes is severe formal/informal misalignment in v1, which contaminates any
informal-statement reading of the v1-based deltas above. All miniF2F deltas carry this
caveat.

### 1.3 Accounting lessons this domain teaches (adopt into every Phase-1 prereg)

- **The sample count k is a necessary pin but NOT a compute measure**: pass@k comparisons
  are meaningless across k (32 vs 3200 vs 8192 all appear in SOTA tables) [LIT:
  goedel-v2-2025, stp-2025, kimina-prover-2025], and equal k does not equal equal tokens,
  active parameters, accelerator work, latency, or search overhead. KOT-COST/2 must pin k
  AND wall-clock AND the full resource vector per family arm (programme-3 ASM-0810).
  [STIPULATED]
- **In the cited systems, the observed failure modes differ by verifier type: sound-checker
  loops report PLATEAU, learned-verifier loops report DECAY.** This is a pattern in the
  cited systems, not a field law. With a sound checker, false positives are impossible
  **relative to the checker's formal statement, axioms, and kernel implementation** — this
  keeps self-training data formally clean but does NOT protect against wrong formalization
  of the intended statement (the programme's main measured NL failure, and exactly the
  failure miniF2F-v2 exposes at benchmark scale, §1.2). The cited loops plateau; STP
  identifies scarcity of correct proofs on a **fixed statement supply** as one plateau
  mechanism, relieved by conjecturer self-play (LeanWorkbook 13.2%→28.5% [LIT: stp-2025])
  or scaffolded synthesis [LIT: goedel-v2-2025] — but statement supply is not thereby
  established as the universal binding constraint; exploration quality, model capacity,
  proof representation, search policy, formal-library coverage, and training stability can
  also bind. With a learned verifier, search DEGRADES below repeated sampling at large
  budgets because imperfect rankers prune all valid paths [LIT: scaling-flaws-2025; owned
  by RAG.md §4]. Our engine is sound on its covered slice, so the nearest KOT analog of
  "verifier failure" is **coverage exhaustion**, the nearest analog of "statement supply"
  is the synthetic generator + world-layer growth rate — and formalization/specification
  error is a third surface no checker property removes. [EXTRAPOLATION — this mapping is
  an argument, not a measurement.]
- **Checker latency does not appear as the binding constraint in any cited system's
  reported cost accounting.** Where costs are reported, the dominant published figures
  attach to proposer sampling and search (~20k V100-hours per sampling iteration [LIT:
  gptf-2020]; ~180k TPU-days [LIT: alphaproof-2025]), and the systems profit from checking
  at massive sample counts. [EXTRAPOLATION — an inference from the cited systems' reported
  cost figures, NOT a cross-system latency study: no cited paper measures checker latency
  as the tested variable, and the "~10ms–seconds per check" range is assembled from these
  setups rather than established by a study. See §6 for what a µs engine changes and does
  not change.]

## 2. Differentiable logic: the matched-baseline record is negative at scale

Extending the parsing report's one-liner into the Phase-0 accounting question:

- **NTP (differentiable backward chaining)** beat ComplEx on 3 of 4 KBs — all toy-sized
  (Countries/Nations/Kinship/UMLS) [LIT: ntp-2017]. Its own successor line concedes the
  computation graph does not scale: GNTP recovers tractability (orders-of-magnitude cheaper)
  but reports "on par with NTPs" and only "competitive" link prediction on large KBs — i.e.,
  **scaling recovered feasibility, not superiority over matched dedicated predictors**
  [LIT: gntp-2020].
- **The one clean benchmark win: CTP reports SOTA on CLUTRR systematic generalization**
  (train on small kinship graphs, test on larger) vs neural baselines [LIT: ctp-2020] — a
  benchmark result; resource-matching of the comparison is not established. Note what the
  win is: a
  closed world, a small rule vocabulary, compositional depth as the test axis — structurally
  the closest published task shape to the kernel's covered slice, and P3-LR-EVAL already
  carries CLUTRR as a candidate suite. This is the differentiable-logic result KOT should
  actually weigh.
- **∂ILP** is explicitly memory-bound (bounded predicates/templates) [LIT: dilp-2018]:
  rule LEARNING at kernel-rule scale is feasible, rule REASONING at KB scale is not, in
  this family.
- **DeepProbLog / Scallop** put a probabilistic-logic executor INSIDE the training
  objective; real systems, module-scale tasks (MNIST-addition class → eight apps);
  Scallop's own summary is "comparable or superior" accuracy with better efficiency, via
  top-k provenance approximation of DeepProbLog's exact-WMC bottleneck [LIT:
  deepproblog-2018, scallop-2023]. Never demonstrated as a component of a ≥100M LM's
  training loss on open text.
- **SATNet** [LIT: satnet-2019, UNVERIFIED-THIS-PASS] remains the field's grounding
  cautionary tale: 0% on visual Sudoku once leaked
  intermediate labels are removed [LIT: satnet-debunk-2020, UNVERIFIED-THIS-PASS at page
  level; owned by the parsing report]. The interface — whether hidden states actually
  decode to the symbols the logic layer consumes — is the failure point, which is the nsk1
  lesson from the programme's own measurements [MEASURED: registry, via feasibility-synthesis
  §0 nsk1 INCONCLUSIVE/echo-grade].
- Meanwhile a **separate, coexisting** line — **LLM + external deterministic solver** —
  delivered at-scale gains (Logic-LM: +39.2% over standard prompting, +18.4% over CoT, with
  self-refinement driven by solver error messages) [LIT: logic-lm-2023]. This is not
  evidence that the differentiable-logic lineage "abandoned" in-loss reasoning — the two
  research lines coexist — but it does show the external-solver placement producing gains
  at a scale the in-loss line has not demonstrated.

**Decision take** [STIPULATED]: differentiable-logic-as-architecture (a logic layer inside
the host, trained end-to-end) has no at-scale matched win **found in this search** and two
structural failure modes (inference cost, symbol grounding) — it is **deprioritized for
Phase 1**: kept out of the P3-D-GU variant list as an architecture absent stronger
evidence. This is a Phase-1 prioritization decision at this review's search scope, not a
field-wide closure — the uncertainty is not "closed". Two narrow tools survive for the
training-signal role only: semantic-loss compilation of constraints
[LIT: semantic-loss-2018] and blackbox-differentiation through exact solvers
[LIT: blackbox-solvers-2020] (§5.3).

## 3. Neural algorithmic reasoning: interfaces buy OOD; traces alone do not

- **The benchmark and its accounting.** CLRS-30 poses 30 textbook algorithms as graph tasks
  with intermediate-state "hints" and OOD-larger-input evaluation [LIT: clrs-2022]. The
  headline progress — a single generalist GNN processor improving average single-task
  performance >20% over prior art [LIT: generalist-nar-2022] — is **within-framework**
  (GNN vs GNN, synthetic tasks, micro-F1); there is no matched external baseline in that
  number. Field self-criticism: transfer to real tasks, the blueprint's stated motivation
  [LIT: nar-position-2021], remains under-explored per 2025 surveys of the area [search,
  2026-07-11; not load-bearing].
- **The result KOT should care about: Discrete NAR.** Forcing execution trajectories into
  finite predefined discrete states (separating discrete from continuous flow) yields
  **perfect in- and out-of-distribution test scores** on covered tasks, single- and
  multi-task, with correctness provable on arbitrary test data (ICML 2025)
  [LIT: discrete-nar-2025]. This is the strongest published support for the programme's central
  architectural intuition — a hard symbolic interface present during training buys OOD
  transfer — with its honest scope: state supervision on closed algorithmic tasks. It is
  the closest prior art to H-RULE-HL's "pinned bottleneck" and to H-GU's "symbolic
  interface from step 0". Its state-supervision requirement maps to our engine's ability
  to emit exact intermediate states cheaply — an ability currently ASSERTED, not
  demonstrated: the §8 oracle/API gate must show the executor actually exposes these
  states before this mapping is treated as load-bearing.
- **The negative space around plain transformers on traces** (jointly load-bearing for
  H-GU): naive finetuning fails length generalization regardless of scale [LIT:
  anil-lengthgen-2022]; with ideal position encodings + formats, 2.5× extrapolation is
  achievable **but fragile across seeds and data order** [LIT: zhou-lengthgen-2024] — so
  any H-GU sweep read must be powered for seed variance, or direction reads are noise
  [STIPULATED → P3-D-GU prereg requirement]; LMs fine-tuned as generalist executors on
  CLRS-Text confirm weak length-OOD [LIT: clrs-text-2024]; and trace-trained transformers
  on compositional tasks reduce to "linearized subgraph matching" — pattern reuse, not
  algorithm induction — failing OOD even when trained on explicit step-by-step traces
  [LIT: faith-fate-2023] (detail in §4.2).
- **Fusion prior art (hand-off to P3-LR-FUSE, not deepened here):** TransNAR — LM tokens
  cross-attending to a pretrained NAR's node embeddings beats Transformer-only on
  CLRS-Text in- and out-of-distribution [LIT: transnar-2024]; parameter/compute-matching
  of that baseline is not stated in the abstract and the "20% absolute" folk figure is
  UNVERIFIED at that precision; it also requires the graph input at inference. Logged as
  a §3.2-sweep prior-art datapoint for P3-D-GNN.

## 4. Proof-trace distillation into small LMs (the H-GU feed)

### 4.1 What bounded-depth deduction distillation achieves

Transformers CAN learn closed-world deduction over explicitly stated rules: 99%
in-distribution, 95%+ at depths beyond training, with zero-shot transfer to paraphrased
rulebases, at ~RoBERTa scale [LIT: ruletaker-2020]. Generating the proof matters:
**iterative single-step implication generation** transfers to unseen depths and OOD
theories where whole-proof generation is weaker (+9pt over prior work) [LIT:
proofwriter-2021]. LoGiPT is the closest published shape to "distill kernel proof traces":
fine-tune on the *revealed internal step trace of a deductive solver* so the LM emulates
the solver directly — beating solver-augmented pipelines (whose NL→symbolic parse errors
are fatal) and few-shot GPT-4 on ProofWriter/PrOntoQA-class tasks [LIT: logipt-2023].

### 4.2 The shortcut kills (mandatory controls, not vibes)

- BERT trained on SimpleLogic: near-perfect in-distribution, **fails on other distributions
  of the SAME problem space** — it learned statistical features of reasoning data, not
  reasoning [LIT: paradox-2022]. ⇒ Every H-GU eval MUST include within-problem-space
  distribution shifts (rule-priors, branching factors), not only depth extrapolation.
- CoT parsed into formal proofs shows the deficit is localized: individual deduction steps
  are fine; **proof planning/search fails** when multiple valid steps exist [LIT:
  prontoqa-2023]. ⇒ The engine/search harness should own planning; distillation should
  target step proposal + verbalization, not search policy. [STIPULATED design prior]
- Trace-trained transformers on compositional tasks (multi-digit multiplication, logic
  grid puzzles, DP) collapse to linearized subgraph matching and fail OOD **even with
  explicit reasoning-trace supervision** [LIT: faith-fate-2023].

### 4.3 Distillation accounting (the skeptical ledger)

- "770M beats 540B" [LIT: distill-sbs-2023] is **task-specific finetune vs few-shot
  generalist** — NOT matched; it licenses "small specialized ≥ large generalist per task"
  and nothing stronger. This is also the honest frame for ReProver-vs-GPT-4 (§1.1) and
  LoGiPT-vs-GPT-4 (§4.1).
- CoT distillation DOES reach our band: 125M–1.3B students gain on commonsense suites, and
  **teacher sampling density is the operative variable** (multiple chains per instance)
  [LIT: scotd-2023].
- Verifier-filtered bootstrapping needs no human rationales: STaR's
  keep-only-correct-answer loop lets 6B match a 30× larger finetuned model on
  CommonsenseQA [LIT: star-2022] — with a WEAK verifier (answer string match). A sound
  engine improves this filter's PRECISION on formal validity for covered statements; it is
  not a strict dominance — it costs coverage (only covered statements can be filtered) and
  remains exposed to formalization/specification error upstream of the check.
  [EXTRAPOLATION]
- Synthetic-curriculum existence proofs at our scale: phi-1 (1.3B, 7B curated/synthetic
  tokens, HumanEval 50.6%) with thin contamination controls — recipe inspiration, not
  evidence [LIT: phi1-2023]; TinyGSM (1.3B + 1.3B learned verifier → 81.5% GSM8K, verifier
  carries a large share) [LIT: tinygsm-2023; owned as analogy by PARSE.md].
- The programme's own asset alignment [STIPULATED]: AlphaGeometry's decisive ingredient was
  an **engine-generated synthetic corpus with exact traces** (100M theorems; ~10M with
  auxiliary constructions) [LIT: alphageometry-2024]. KOT possesses the RAW INGREDIENTS of
  the analog: a deterministic, seedable synthetic generator + µs engine over the covered
  grammar with controlled depth/polarity/paraphrase axes [MEASURED: encoder/ + poc/
  infrastructure exists; coverage ceiling per m0b 0.3542 friendliest-corpus remains the
  binding scope limit, feasibility-synthesis §0]. Whether the executor EXPOSES what the
  cited recipes consume — proof states, legal-action sets, step traces, compiler-style
  diagnostics — has not been demonstrated; the §8 oracle/API gate must show it before the
  AlphaGeometry analog is claimed. [STIPULATED gap]

## 5. Executor-in-the-loop training precedents (verifier-guided training)

Three rungs, by increasing integration depth — the evidence gets thinner as integration
gets deeper [STIPULATED framing]:

1. **Executor as data filter (expert iteration / rejection finetuning).** The
   best-evidenced rung: GPT-f value-function training from its own verified searches
   [LIT: gptf-2020]; compute-matched superiority over search-only [LIT:
   polu-curriculum-2022]; HTPS online training [LIT: htps-2022]; ReST-EM's binary-feedback
   EM loop (gains scale with size, diminish over iterations) [LIT: restem-2024]; STaR at
   6B [LIT: star-2022]; plateau caused by statement supply, fixed by self-play
   conjecturing [LIT: stp-2025].
2. **Executor as RL reward / feedback channel.** RLPAF (Lean pass/fail as reward)
   [LIT: dsprover15-2024]; CodeRL's unit-test critic at 770M-class scale [LIT:
   coderl-2022]; RLEF — training the model to CONSUME execution feedback across turns cuts
   inference samples by an order of magnitude at 8B/70B [LIT: rlef-2024]; Goedel-V2's
   compiler-feedback self-correction as an ablatable +2.3pt component [LIT: goedel-v2-2025];
   Logic-LM's solver-error self-refinement at inference [LIT: logic-lm-2023]. Directly
   licenses training the H-VL retry policy rather than only bolting retry on.
3. **Executor literally in the loss (differentiable).** Semantic loss (circuit-compiled
   constraints) [LIT: semantic-loss-2018]; blackbox-differentiation through exact solvers
   (Gurobi/Blossom V/Dijkstra as layers with informative gradients) [LIT:
   blackbox-solvers-2020]; DeepProbLog/Scallop (§2). All module-scale; **no published
   demonstration at ≥100M-LM scale with a logic engine in the loss was found in this
   search**. This rung has no precedent found, and no disproof — an absence at this
   review's search scope, not an established field fact.

**The scaling-flaws boundary** (re-anchored from RAG.md §4): the decay of verifier-guided
search at large budgets is a LEARNED-verifier pathology (misranking prunes valid paths)
[LIT: scaling-flaws-2025]. The cited sound-checker systems do not report it; they report
plateau, with statement supply identified as one mechanism [LIT: stp-2025] (§1.3 — not
established as the universal constraint). For KOT this separates the failure surfaces
Phase-1 must instrument: engine **coverage** (the sound analog of verifier failure),
generator **supply/diversity** (the analog of conjecturer collapse), and
**formalization/specification error** (outside both, untouched by checker soundness).

## 6. Transfer to a µs deterministic executor (the verifier-loop bet's prior art)

What the literature establishes, and exactly where KOT's premise goes beyond it:

- **Small proposer + deterministic engine beating larger neural-alone: established at
  system level.** AlphaGeometry (151M LM + DD/AR engine, 25/30 vs prior best 10; the
  oft-quoted GPT-4 0/30 comparison was not confirmed in my Nature fetch — UNVERIFIED)
  [LIT: alphageometry-2024], with the successor showing the neural side kept scaling
  without the symbolic engine capping the system (84% of 25 years of IMO geometry)
  [LIT: alphageometry2-2025]; ReProver-299M's premise-retrieval system over GPT-4 zero-shot
  (unmatched accounting noted) [LIT: leandojo-2023]; Thor's +18pt from adding hammers
  [LIT: thor-2022]. In every case the engine contributes soundness and/or exhaustive local
  deduction; the LM contributes exactly what the engine cannot enumerate (constructions,
  premise relevance, tactic priors).
- **Checker speed is never the tested variable in this literature.** Where per-check costs
  are visible they sit around ~10ms–s [EXTRAPOLATION: range assembled from the cited
  systems' setups, not established by a latency study — same caveat as §1.3]; systems
  compensate with parallelism (10,000 CPU workers [LIT: alphageometry-2024])
  and still win. A 5.29–7.82 µs/query engine [MEASURED: programme premise,
  programme-3 §2 PREMISE block] is ~10³–10⁵× cheaper per check than any executor in this
  literature. Two consequences [EXTRAPOLATION, both]:
  (a) every verified-training-loop precedent in §5 becomes cheaper in its checking leg —
  but since checking is not reported as the cost ceiling in any cited system (§1.3),
  **the µs property does NOT by itself improve the loop's economics**; proposer sampling
  still dominates. The honest claim is "removes a cost term", not "changes the regime",
  for training. Cheap checking is also not automatically cheap trace generation,
  conjecture generation, proof search, tokenization, storage, or training (next bullet).
  (b) the candidate novel regime is **per-token/inference-time integration**: at µs per
  check, the engine could be consulted inside the decode loop (H-RULE-CD's engine-derived
  continuation sets; H-VL's verify-retry with negligible verify overhead) at a cost no
  published executor could sustain. **This search found no precedent** for a semantic
  executor consulted per decoding step — the nearest cousins are grammar-mask automata
  (syntax-only; owned by the parsing report), execution-guided partial-program
  decoding/selection (owned by PARSE.md — an acknowledged adjacent precedent at
  program-fragment granularity), and KV-side memories (no execution). The claim is "no
  precedent found in this search", NOT "no precedent exists": P3-LR-RULE owns the
  executor-backed constrained-decoding search and must complete before any novelty claim
  is treated as settled. This is where the µs property may be a real differentiator, and
  it is an H-RULE/H-VL design question, not an H-GU one. [STIPULATED hand-off]
- **The engine as data factory is the underexploited transfer.** AlphaGeometry's synthetic
  corpus and Goedel-V2's scaffolded synthesis both use the deterministic side to
  MANUFACTURE the training distribution [LIT: alphageometry-2024, goedel-v2-2025]. A µs
  engine removes the ENGINE-EXECUTION term from trace-generation cost at any curriculum
  size — but generator sampling, search, trace serialization, deduplication, storage, and
  training-token processing all still scale with curriculum size and will dominate; the
  speed buys a real but PARTIAL training-side term, not "effectively free" generation.
  [EXTRAPOLATION]
- **What nothing in this literature licenses:** that any of this closes the NL boundary
  (all cited systems consume FORMAL inputs or curated problem statements — the l3a-parse /
  a5-nl FAILs stand untouched [MEASURED: registry/verdicts, via feasibility-synthesis §0]);
  and that verifier-loop gains are kernel-CONTENT-specific rather than
  correct-alignment-specific (the f2b confound; unresolved pending knull / f2b-transfer
  [MEASURED: registry/assessments/f2b-replicate.json does_not_license]).

## 7. Open questions for Phase-1 (numbered; each maps to a design bead)

- **Q1 (P3-D-GU).** Does the frontier prover recipe (engine-generated curriculum +
  verifier-filtered self-training + feedback-consumption training) hold BELOW 2B, where no
  published prover lives? The 8B>671B and 4B>671B results make "yes" plausible; nothing
  demonstrates it. The H-GU ≥3-point sweep is exactly the right instrument; power it for
  seed variance per [LIT: zhou-lengthgen-2024].
- **Q2 (P3-D-GU).** Does shortcut learning [LIT: paradox-2022] persist when the training
  distribution is ENGINE-CONTROLLED (exact traces, controlled rule-priors/branching)?
  I.e., is the paradox a data artifact or an architecture limit? Pre-register
  within-problem-space shift splits alongside depth splits.
- **Q3 (P3-D-GU, co P3-D-RULE).** Can Discrete-NAR-style state discretization [LIT:
  discrete-nar-2025] be imposed on a transformer host (not a GNN) with engine-emitted
  state supervision, and does its perfect-OOD property survive the transfer? (Bridges to
  H-RULE-HL's bottleneck, ordered LAST in the placement ladder per programme §3.3.)
- **Q4 (P3-D-RULE).** At µs check cost, is per-token engine consultation (continuation-set
  derivation mid-decode) latency-viable at p95 on our hardware, and does it beat the same
  engine used only as a post-hoc verifier at matched total budget? No prior art found in
  this search either way (§6b; P3-LR-RULE to confirm).
- **Q5 (P3-D-PS).** Does solver-trace emulation (LoGiPT-style, engine traces distilled INTO
  the parser/generator) beat parse→execute pipelines on the S2 dangerous-wrong metric, or
  does removing the executor at inference reintroduce unsound outputs? The literature shows
  accuracy parity is achievable; it does not report S2-style soundness accounting.
- **Q6 (P3-D-GU, feeds P3-D-SEAL).** What is our statement-supply curve? One documented
  sound-loop plateau mechanism is provable-statement exhaustion [LIT: stp-2025;
  §1.3 — one mechanism, not the established universal constraint]; the covered slice is
  currently 108 concepts / m0b 0.3542 [MEASURED: feasibility-synthesis §0]. A conjecturer
  analog (engine-validated statement synthesis over the world layer) needs a cost model
  before any H-GU RL variant is budgeted.

## 8. Phase-1 hand-off

**What this review settled** (for the record; [STIPULATED] unless tagged):

1. The verifier-loop bet's TRAINING-side precedent is real, replicated, and in one case
   same-compute by the paper's own claim [LIT: polu-curriculum-2022]; the other headline
   comparisons are component ablations or unmatched (§1.2); its economics precedent at ≤2B
   is absent — H-GU's sweep is the first test, not a replication.
2. Differentiable logic is DEPRIORITIZED as an architecture direction for Phase-1 (no
   at-scale matched win found in this search; grounding + cost failure modes) — a
   prioritization decision at this review's scope, not a field-wide closure — retained
   only as loss-shaping tools (semantic loss, blackbox-diff) for a LATE H-GU variant if
   ever.
3. Trace distillation without an executor or hard interface is expected to shortcut
   (three independent negative lines: paradox/PrOntoQA/Faith-and-Fate) — H-GU variants
   must keep the engine in the loop (filter/reward/state-supervision), and every eval
   needs within-space shift splits, multi-seed powering, and depth extrapolation.
4. The µs engine's speed is a candidate DECODE-TIME differentiator (per-token
   consultation: no precedent found in this search; P3-LR-RULE must complete the adjacent
   search before "unprecedented" is claimed) and a partial DATA-FACTORY asset (removes the
   engine-execution term from trace curricula; generation/serialization/storage/training
   costs remain), but NOT a training-loop-economics differentiator (checking is not
   reported as the ceiling in any cited system).
5. Proof-planning, not step deduction, is the neural deficit [LIT: prontoqa-2023] —
   division of labour should give search/planning to the deterministic side.
6. pass@k pinning + benchmark-quality audit (miniF2F-v2 lesson) go into every Phase-1
   prereg touching reasoning suites.

**Common prereg requirements for ALL THREE beads (added per external review
rev-NTP-20260711b; [STIPULATED]):**

- **Oracle/API gate (blocking, first):** demonstrate that the KOT executor can actually
  EMIT what each proposed arm consumes — proof states, legal-action/continuation sets,
  step traces, compiler-style diagnostics, and search transitions. µs checking does not
  imply any of these exist; no arm is budgeted until its interface is shown (§3, §4.3, §6).
- **Full resource-vector accounting for every ablation** (KOT-COST/2, programme-3
  ASM-0810): equal model size or equal pass@k does NOT license "matched"; no scalar
  diagnostic alone licenses "compute-matched".
- **Factorial separation** of synthetic curriculum, proof traces, checker filtering,
  retry feedback, and hard state interfaces — no bundled-recipe arms whose components
  cannot be attributed.
- **Formalization/specification-error accounting distinct from checker validity** — a
  sound check certifies the formal statement, not the intended one (§1.3; miniF2F-v2).
- **"No precedent found" language** for all novelty claims until P3-LR-RULE and
  P3-LR-PARSE complete their adjacent searches.

**Design beads to create (coordinator: bd-create; this bead writes no beads per
governance):**

- **P3-D-GU** [DESIGN, P2, blocked-by: P3-LR-TINY + this review + P3-LR-FUSE]. This
  review's co-input: stage the training variants in the evidence order (1) engine-generated
  synthetic curriculum + iterative SINGLE-STEP trace distillation (ProofWriter/LoGiPT
  shape) with pre-registered shift/depth/seed-variance protocol (§4, §7-Q1/Q2); (2)
  verifier-filtered bootstrapping (STaR/ReST-EM shape, sound-engine filter) (§5.1); (3)
  RL-from-engine-feedback incl. feedback-consumption training (RLEF shape) (§5.2); rank
  differentiable executor-in-the-loss LAST (no at-scale precedent, §5.3); include a
  Discrete-NAR-style state-supervised variant as the interface-maximal arm (§7-Q3); budget
  a statement-supply cost model before any RL arm (§7-Q6).
- **P3-D-RULE** [DESIGN, P1, blocked-by: P3-LR-RULE + this review]. This review's
  co-input: H-RULE-CD's engine-derived continuation masking has no semantic-executor
  precedent FOUND IN THIS SEARCH (grammar-only masking and PARSE.md's execution-guided
  partial-program decoding are the nearest cousins) — treat the novelty claim as "no
  precedent found", NOT settled, until P3-LR-RULE (which owns the executor-backed
  constrained-decoding search) completes; the p95-latency-viability question (§7-Q4) plus
  the causal-provenance requirement (no attention-map evidence; executor traces qualify)
  go into the prereg; nothing in the NTP literature supports KV-placement gains — leave
  its prior at the injection report's level.
- **P3-D-PS** [DESIGN, P1, blocked-by: P3-LR-PARSE + this review]. This review's
  co-input: adopt executor error messages as a first-class refinement/training channel
  (Logic-LM, Goedel-V2, RLEF, §5.2); test solver-trace emulation vs parse→execute on S2
  accounting (§7-Q5); keep the engine at inference for soundness on covered spans —
  emulation-only variants must carry an explicit unsoundness budget.

**Non-recommendations (Phase-1 prioritization decisions at this review's search scope,
revisitable on new evidence — not field-wide closures):** do not build a
differentiable logic layer into any Phase-1 host (§2); do not train on traces without an executor
in the loop or a hard interface (§8.3); do not compare family arms across differing pass@k
(§1.3); do not treat AlphaProof/AlphaGeometry headline results as economics evidence for
the index (they are existence proofs at 10³–10⁵× our compute envelope, §1.2/§6); do not
adopt CLRS/NAR processor results as evidence of real-input transfer (within-framework
accounting, §3).

---

*Sources: `docs/next/lit/NTP.sources.jsonl` — 54 entries; 50 fetched-verified at primary
venue 2026-07-11 (six with venue-only [memory] flags where the arXiv page omits the venue;
`dsprover-v2-2025` and new entry `deepseek-v3-2024` fetched during the 2026-07-11 revision
pass), 4 carried (parsing-report/PARSE.md/search-snippet provenance) and marked
`verified:false`. Verification scope: page-fetch + abstract/headline-level claim check —
not an independent audit of full-paper ablations or resource accounting (see epistemic
contract).*
