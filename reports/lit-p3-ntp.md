# P3-LR-NTP — Neural theorem proving, differentiable logic, neural algorithmic reasoning, proof-trace distillation (formalized)

**Bead:** P3-LR-NTP (Programme-3, Phase-0 [LIT]).
**Deliverable path:** `reports/lit-p3-ntp.md`.
**Author/role:** literature-review agent (Opus execution), independent source-verification pass.
**Date:** 2026-07-19. **Status:** DRAFT for coordinator review. Nothing here is frozen,
registered, or scheduled; no registry record / ASM / KB shard is touched; no bd/git operations.
**Parent:** `docs/next/programme-3-neurosymbolic-architecture.md` (rev 2) §3.3
(H-RULE-{CD,KV,AD,ACT,HL} placement ladder), §3.5 (H-GU build-strategy fork + the ≥3-point
scaling-direction protocol + the executor-in-the-loss variant list), §3.6 summary table, §5 Phase-0.
**Feeds:** **P3-D-GU** (co-input, with P3-LR-TINY + P3-LR-FUSE), **P3-D-RULE** (co-input, with
P3-LR-RULE), **P3-D-PS** (co-input, with P3-LR-PARSE).

> **Relationship to `docs/next/lit/NTP.md`.** A prior, careful NTP review exists (Fable,
> 2026-07-11, bead …s55r.6, already once-revised on a GPT-5.6 review `rev-NTP-20260711b`, with
> source ledger `NTP.sources.jsonl`, 54 entries). **This report is not a redo.** It is (a) an
> independent re-verification of the draft's load-bearing citations at their primary sources this
> session, (b) an explicit divergence log, and (c) a formalization at the requested `reports/` path,
> epistemic-tagged and refreshed to 2026-07-19. Where I re-fetched a source I say so; where I
> accepted the 07-11 verification without re-fetch I mark `[prior-verified: 2026-07-11]`.
> **Headline result of the verification pass: every load-bearing number the draft leans on holds at
> source** — including the two I most suspected (Pythagoras-Prover, a 2026 paper with an unusual
> arXiv id and a "~167× fewer parameters" claim; and the DeepSeek-V3 MoE activated-parameter figure
> that anchors the whole "80×/167× are NOT active-compute ratios" qualification). Divergences found
> are minor and provenance-level (§ Divergences) — chiefly one wording over-precision (Discrete-NAR
> "OOD") and one number I could not re-confirm at source behind the Nature paywall (AlphaProof's
> TPU-day figure), neither of which is load-bearing for a conclusion.

## Epistemic tag convention

- `[established]` — external empirical/methodological fact confirmed at a primary source this session
  or prior. `[claimed]` — asserted in a source but single-source, abstract-only, or not independently
  corroborated. `[speculative]` — my forward inference / design judgement.
- Provenance suffix: `[search: 2026-07-19]` = re-verified at source via WebSearch/WebFetch this
  session; `[prior-verified: 2026-07-11]` = verified at source in the 07-11 NTP.md, accepted here
  without re-fetch; `[memory]` = from the parent design doc / in-repo verdicts, not a literature
  source. `[UNVERIFIED]` = could not confirm at primary source this session (paywall / body-only /
  fetcher failure).
- Measurement register (inherited from the draft): a "MEASURED" number below is the *authors'*
  published measurement restated inside that paper's own envelope — never *our* measurement, and
  never a premise for a KoT verdict. Cross-paper readings are direction-only. Programme-internal
  `[memory]` measurements name their registry object.

---

## Top findings (read this first)

1. **The crux — does ANY NTP / differentiable-logic / NAR method beat a *matched-resource* neural
   baseline under fair accounting (same information + trainable params + train compute + causality
   by perturbation)? Honest answer: no — and the answer is the same shape FUSE found.**
   `[established][search: 2026-07-19]` Every demonstrated win in this scope is one of: (a) an
   **add-capability** win — the deterministic engine supplies soundness, exhaustive local deduction,
   a *provable* OOD-correctness guarantee, or a hard discrete state interface that the neural
   baseline **structurally lacks**; (b) **unmatched** compute/parameters/sample-budget; or (c) a
   **component ablation** that shares the base model but adds uncharged machinery (retrieval index,
   ATP calls, an extra training objective, compiler-feedback retries). **The single same-compute
   claim in the entire scope (Polu et al., expert-iteration > proof-search-only "at same compute
   budget", verified verbatim) is a *within-executor allocation* result — both arms already have the
   sound checker — not a neurosymbolic-vs-matched-neural-baseline-lacking-the-executor comparison.**
   So it does not answer the crux either. **This mirrors P3-LR-FUSE exactly, and it is the most
   important finding for Programme-3: the demonstrated NeSy value in this literature lives in the
   correctness thesis (an exact checker/interface the baseline cannot have), not the efficiency
   thesis (matched-resource superiority).**

2. **The strongest candidate, stated as strongly as honesty allows, and why it still fails the bar:
   Discrete-NAR.** `[established][search: 2026-07-19]` Forcing execution trajectories into a finite
   set of predefined discrete states (separating discrete/continuous flows, with state supervision)
   yields *perfect test scores in single- and multi-task setups* and lets the authors *"prove the
   correctness of the learned algorithms for any test data"* (ICML 2025). This is the strongest
   published support for the programme's central architectural intuition — a hard symbolic interface
   present during training buys OOD generalization. **But it is an add-capability win, not a
   matched-resource one:** the guarantee comes from imposing a discrete interface + state supervision
   the plain baseline does not have, on closed algorithmic tasks. Runner-up candidates: (i)
   Polu expert-iteration (only same-compute *claim*, but within-executor allocation, §1.2); (ii)
   CTP on CLUTRR (closest thing to a matched-resource reasoning win in differentiable logic —
   SOTA systematic generalization vs neural baselines — but resource-matching not established, and
   it is an add-*structure* win on a small closed world, §2).

3. **Trace-distillation *without* an executor/hard-interface in the loop is expected to shortcut —
   three independent negative lines, all re-anchored.** `[established][search: 2026-07-19 for the
   architectural read; prior-verified for two of the three abstracts]` SimpleLogic/paradox (BERT
   near-perfect in-distribution, fails other distributions of the *same* problem space), PrOntoQA
   (individual deduction steps fine, *proof planning/search* fails), and Faith-and-Fate (trace-trained
   transformers reduce to linearized subgraph matching, fail OOD *even with* explicit step-by-step
   trace supervision) jointly say: distilled traces alone do NOT induce a reasoner, and every H-GU
   eval must carry within-problem-space shift splits + multi-seed powering + depth extrapolation.
   The positive counterweight (RuleTaker/ProofWriter/LoGiPT) shows closed-world deduction over
   *stated* rules **is** learnable at ~350M–RoBERTa scale, and iterative single-step generation +
   solver-trace emulation transfer better than whole-proof generation — but all consume formal
   inputs and keep an executor-derived signal.

4. **What transfers to a µs deterministic engine-as-executor: the two shallow rungs cleanly, the
   data-factory partially, the hard-interface conditionally, the per-token regime as an unproven
   novel bet, the in-loss rung not at all.** `[established inputs, speculative mapping][search:
   2026-07-19]` Executor-as-data-filter (expert iteration / STaR / ReST-EM) and executor-as-RL-reward
   / feedback-consumption (RLPAF, RLEF, CodeRL, Goedel self-correction, Logic-LM error channel)
   transfer directly and are the best-evidenced rungs; RLEF is the direct precedent for *training*
   the H-VL retry policy, not just bolting retry on. The engine-as-data-factory (AlphaGeometry /
   Goedel scaffolded synthesis) transfers **partially** — µs removes the engine-execution term from
   trace generation, but generation/search/serialization/dedup/storage/training-token cost remains
   and dominates. The Discrete-NAR hard-interface transfer is **conditional on the engine actually
   emitting exact intermediate states cheaply** — asserted, not demonstrated (the §8 oracle/API gate).
   The candidate *novel* regime is per-token/inference-time engine consultation (H-RULE-CD
   continuation sets; H-VL negligible verify overhead): **no precedent found in this search** for a
   *semantic* executor consulted per decode step (grammar-mask automata are syntax-only;
   execution-guided partial-program decoding is the nearest program-fragment cousin) — this is where
   the µs property may be a real add-capability differentiator, and it is an H-RULE/H-VL question.
   Differentiable-executor-in-the-loss (semantic loss / blackbox-solvers / DeepProbLog-Scallop) does
   **not** cleanly transfer: module-scale only, no ≥100M-LM precedent found, and a discrete µs engine
   is not differentiable anyway.

5. **Parameter count is not the binding axis in frontier proving — but the "small beats huge"
   results are parameter-efficiency under a shared *sample-count* metric, not matched compute, and
   both arms have the executor.** `[established][search: 2026-07-19]` Goedel-Prover-V2-8B beats
   DeepSeek-Prover-V2-671B under the same pass@32 metric ("80× smaller", verified); Pythagoras-Prover-4B
   does the same ("86.1% vs 82.4%… ~167× fewer parameters", verified). **Mandatory qualification
   (verified verbatim): the 671B comparator is an MoE with 37B activated per token, so the active-
   parameter ratios are ~5×/~9×, not 80×/167×; and equal pass@32 pins only sample count — tokens,
   wall-clock, and search overhead are unpinned.** These are total-parameter-efficiency results under
   a common metric between two *neurosymbolic* systems, not matched-compute wins over a neural
   baseline. **No frontier-recipe prover has been published at ≤2B** — that the trend continues into
   the R-0 band is the explicit open question H-GU's sweep is the first to test.

---

## 1. Neural theorem proving: proposer + sound checker

### 1.1 The band, and what exists at 100M–2B `[established unless tagged]`

The architecture has been stable since 2020: a generative LM proposes proof steps (or whole proofs),
a **sound proof checker** (Metamath/Lean/Isabelle kernel) validates, a search allocates samples. The
standard yardstick is miniF2F (488 cross-system statements) `[prior-verified: 2026-07-11]`. Frontier
solve rates are now very high — **miniF2F-test 84.6% pass@32 at 8B, 88.1–93.0% at 32B**
(Goedel-Prover-V2-8B 84.6 / -32B 88.1; Pythagoras-32B 93.0 — all `[established][search: 2026-07-19]`)
— but **no current frontier prover is ≤2B.** What exists in/near our band:

- **ReProver (299M ByT5-small + premise retrieval)** — the ≤2B anchor. LeanDojo Benchmark Pass@1
  **51.2%** (random) / **26.3%** (novel-premises); no-retrieval same-model twin **47.6% / 23.2%**;
  miniF2F **26.5%**, ProofNet **13.8%**; GPT-4 zero-shot **29.0% / 7.4%**; **"one GPU week"** training
  vs prior "thousands of GPU-days". `[established][search: 2026-07-19 — all eight numbers re-verified
  at ar5iv Table 2, exact match to draft]`
- **GPT-f (160M–1.5B)** — best **56.22% held-out Metamath at 700M**; larger not always better at
  fixed data/search; expert-iteration sampling ~20k V100 GPU-h per iteration.
  `[prior-verified: 2026-07-11, ar5iv full text]`
- **Graph2Tac (~10M-scale GNN, Coq)** — online learning of new definitions; ≥1.48× more theorems than
  CoqHammer/Proverbot9001/a transformer baseline; 1.5× over its own offline twin; cross-system
  matching not stated. `[prior-verified: 2026-07-11]`
- **AlphaGeometry's LM is ~151M** (excl. embeddings), trained from scratch on ~100M engine-generated
  synthetic traces. In-band on parameters, far out-of-band on search (§1.3, §6).
  `[established: 25/30 result, search: 2026-07-19 via DeepMind/Wikipedia; 151M + 10,000-CPU-worker
  figures prior-verified: 2026-07-11, Nature body, paywalled this session]`

**Trend line (load-bearing for sizing):** total parameter count is not the binding axis
(Goedel-8B > 671B; Pythagoras-4B > 671B) — but see Top-Finding 5 for the MoE + sample-count
qualification. `[EXTRAPOLATION: that the recipe holds below 2B is NOT established — no frontier-recipe
prover published at ≤2B; explicit Phase-1 open question, §7-Q1.]`

### 1.2 What beat controlled baselines, under what accounting — the skeptical ledger

Filtered honestly, the ledger is **one same-compute *claim* plus four controlled component
ablations** — NOT five resource-matched wins, and NOT one matched-resource-vs-no-executor win. Per
KOT-COST/2 (no scalar diagnostic alone licenses "compute-matched" `[STIPULATED: programme-3 ASM-0810,
memory]`), sharing a base model and pass@k does not establish resource-matching.

| # | Win | vs baseline | Accounting reality | Matched-resource? |
|---|---|---|---|---|
| 1 | **Expert iteration > proof-search-only** `[established][search: 2026-07-19 — "at same compute budget… expert iteration… dramatically outperforms proof search only", verbatim; also finds a difficulty curriculum "without the need for associated ground-truth proofs"]` (Polu 2022) | proof-search-only | the field's cleanest same-compute claim, but **both arms use the sound checker** — a within-executor *allocation* result (train vs search), not vs a baseline lacking the executor; resource vector not independently audited | Same-compute *claim* ✓; but not the crux comparison |
| 2 | **Retrieval > no-retrieval, same 299M model** `[established][search: 2026-07-19]` (LeanDojo 2023) | its own no-retrieval twin | +3.6 / +3.1 pts; genuine same-model, same-k component ablation; retrieval index-build + per-query cost uncharged | Component ablation; not resource-vector-matched |
| 3 | **Proof-artifact co-training** 32%→48% held-out Lean `[prior-verified: 2026-07-11]` (PACT 2021) | same model without it | auxiliary self-supervised objective from kernel artifacts; extra data/compute uncharged | Component ablation |
| 4 | **Hammer+LM division of labour** PISA 39%→57%, +8.2% neither alone `[established][search: 2026-07-19 — verbatim]` (Thor 2022) | LM-only | complementarity is additive; ATP calls add cost outside the shared budget | Component ablation; **add-capability** in shape |
| 5 | **Verifier-guided self-correction** +2.3 pts at 32B (88.1→90.4 pass@32) `[established][search: 2026-07-19]` (Goedel-V2 2025) | same model, no correction | correction rounds consume extra tokens/compiler calls inside pass@32 | Component ablation |

**The *unmatched* headline results, named as such:** HTPS 82.6% Metamath (vs GPT-f 56.5%) on online
training + large search, no compute-matching stated `[prior-verified: 2026-07-11]`; Kimina 80.7% at
**pass@8192** — a 256× larger sample budget than the pass@32 rows it is tabled against
`[claimed][prior-verified: 2026-07-11, search-snippet only — UNVERIFIED at primary]`; AlphaProof's
IMO silver used a 3B model but **~80,000 TPU-days RL + ~100,000 TPU-days autoformalization** and
Test-Time RL trains on variants of the single target problem — an existence proof, not an economics
proof (**28-pt silver, 3 problems incl. Q6 re-confirmed `[search: 2026-07-19]`; the TPU-day figures
are Nature-body-level and I could NOT re-confirm them at source this session — Nature paywall;
`[prior-verified: 2026-07-11]`, and a secondary source corroborates the qualitative "limited entirely
by how many TPUs we could get" — § Divergences**).

**Benchmark-quality flag `[established][search: 2026-07-19 via draft's own re-verify + prior]`:**
>half of original miniF2F statements are misaligned with their informal versions; an end-to-end
(understand→formalize→prove) system reaches only ~36% on original miniF2F (despite 97%
autoformalization / 69% proving component-wise) and **improves to 70% on the corrected v2**
(miniF2F-v2, 2025). The correction *raises* end-to-end accuracy; what it exposes is severe
formal/informal misalignment in v1 that contaminates any informal-statement reading of v1-based
deltas. All miniF2F deltas above carry this caveat.

### 1.3 Accounting lessons this domain teaches (adopt into every Phase-1 prereg) `[STIPULATED unless tagged]`

- **The sample count k is a necessary pin but NOT a compute measure**: pass@k comparisons are
  meaningless across k (32 / 3200 / 8192 all appear in SOTA tables), and equal k ≠ equal tokens,
  active parameters, accelerator work, latency, or search overhead. KOT-COST/2 must pin k AND
  wall-clock AND the full resource vector per family arm (ASM-0810). `[established: the k-inflation
  facts; search: 2026-07-19 for STP pass@3200 and prior for Kimina pass@8192]`
- **Failure modes differ by verifier type (a pattern in the cited systems, not a field law):**
  sound-checker loops report **PLATEAU**; learned-verifier loops report **DECAY**. With a sound
  checker, false positives are impossible *relative to the checker's formal statement/axioms/kernel*
  — this keeps self-training data formally clean but does NOT protect against **wrong formalization
  of the intended statement** (the programme's main measured NL failure; exactly what miniF2F-v2
  exposes). STP identifies **scarcity of correct proofs on a fixed statement supply** as *one*
  plateau mechanism (LeanWorkbook 13.2%→28.5% via self-play conjecturing), not the established
  universal constraint. `[established][search: 2026-07-19 — STP "scarcity of correct proofs (sparse
  rewards)… 28.5%… doubling the previous best 13.2%", verbatim]` With a learned verifier, search
  DEGRADES below repeated sampling at large budgets (imperfect rankers prune all valid paths;
  scaling-flaws-2025, owned by RAG.md §4). `[EXTRAPOLATION]` The engine is sound on its covered slice,
  so the nearest KOT analog of "verifier failure" is **coverage exhaustion**, of "statement supply"
  is the synthetic generator + world-layer growth rate — and formalization/specification error is a
  third surface no checker property removes.
- **Checker latency is never the tested variable in any cited system's reported cost accounting.**
  Where costs are reported, the dominant figures attach to proposer sampling and search (~20k
  V100-h/iteration; the AlphaProof/AlphaGeometry TPU/CPU envelopes) and systems profit from checking
  at massive sample counts. `[EXTRAPOLATION — inference from the cited systems' reported costs, NOT a
  cross-system latency study; the "~10ms–s per check" range is assembled from these setups, not
  established by a study. See §6.]`

## 2. Differentiable logic: the matched-baseline record is negative at scale `[established unless tagged]`

- **NTP (differentiable backward chaining)** *"outperforms ComplEx… on three out of four benchmark
  knowledge bases"* — all toy-sized (Countries/Nations/Kinship/UMLS) — while inducing interpretable
  rules `[established][search: 2026-07-19 — verbatim]`. Its own successor concedes the computation
  graph does not scale: **GNTP** recovers tractability (*"orders of magnitude more efficient… on par
  with NTPs at a fraction of their cost… competitive link prediction results on large datasets"*
  `[established][search: 2026-07-19 — verbatim]`) — i.e. **scaling recovered feasibility, not
  superiority over matched dedicated predictors.**
- **The one clean benchmark win: CTP reports SOTA on CLUTRR systematic generalization** (train on
  small kinship graphs, test on larger) vs neural baselines, via learned rule-selection by gradient
  descent `[established][search: 2026-07-19 — "scalable and yield state-of-the-art results on the
  CLUTRR dataset… systematic generalisation… smaller graphs… larger ones", verbatim]`. Resource-
  matching of the comparison is **not** established. What the win *is*: a closed world, a small rule
  vocabulary, compositional depth as the test axis — structurally the closest published task shape to
  the kernel's covered slice (P3-LR-EVAL already carries CLUTRR). **This is the differentiable-logic
  result KOT should actually weigh — and it is an add-structure win, not a matched-resource one.**
- **∂ILP** is explicitly memory-bound (bounded predicates/templates): rule LEARNING at kernel-rule
  scale is feasible, rule REASONING at KB scale is not, in this family. `[prior-verified: 2026-07-11]`
- **DeepProbLog / Scallop** put a probabilistic-logic executor INSIDE the training objective; real
  systems, module-scale tasks (MNIST-addition class → eight apps); Scallop's own summary is
  "comparable or superior" accuracy with better efficiency via top-k provenance. Never demonstrated
  as a component of a ≥100M-LM training loss on open text. `[prior-verified: 2026-07-11]`
- **SATNet** remains the field's grounding cautionary tale: ~0% on visual Sudoku once leaked
  intermediate labels are removed — the interface (do hidden states actually decode to the symbols
  the logic layer consumes?) is the failure point, which is the nsk1 lesson from the programme's own
  measurements. `[claimed][prior-verified: 2026-07-11 — carried from the parsing report; UNVERIFIED
  at page level both passes]` `[memory: nsk1 delivery ECHO-grade, integration unresolved —
  feasibility-synthesis §0]`
- A **separate, coexisting** line — **LLM + external deterministic solver** — delivered at-scale
  gains (Logic-LM: +39.2% over standard prompting / +18.4% over CoT, self-refinement on solver error
  messages). Not evidence the differentiable-logic lineage "abandoned" in-loss reasoning (the lines
  coexist), but it shows the external-solver placement producing gains the in-loss line has not
  demonstrated at that scale. `[prior-verified: 2026-07-11; lit-KB arxiv_2305.12295]`

**Decision take `[speculative → Phase-1 prioritization at this review's search scope, not a
field-wide closure]`:** differentiable-logic-**as-architecture** (a logic layer inside the host,
trained end-to-end) has no at-scale matched win found in this search and two structural failure modes
(inference cost, symbol grounding). Deprioritized for Phase-1 (kept out of the P3-D-GU variant list
as an architecture, absent stronger evidence). Two narrow tools survive for the **training-signal
role only**: semantic-loss compilation of constraints and blackbox-differentiation through exact
solvers (§5.3) — and note these require a *differentiable* path a discrete µs engine does not natively
provide.

## 3. Neural algorithmic reasoning: hard interfaces buy OOD; traces alone do not `[established unless tagged]`

- **The benchmark and its accounting.** CLRS-30 poses 30 textbook algorithms as graph tasks with
  intermediate-state hints and OOD-larger-input evaluation. The headline progress — a single
  generalist GNN improving average single-task performance >20% over prior art — is
  **within-framework** (GNN vs GNN, synthetic tasks, micro-F1); **there is no matched external
  baseline in that number.** `[prior-verified: 2026-07-11]` Field self-criticism: real-task transfer
  (the blueprint's stated motivation) remains under-explored per 2025 surveys.
  `[claimed][search: 2026-07-11; not load-bearing]`
- **The result KOT should care about: Discrete-NAR.** Forcing trajectories into finite predefined
  discrete states (separating discrete/continuous flows) yields *"perfect test scores both in
  single-task and multitask setups"* and lets the authors *"prove the correctness of the learned
  algorithms for any test data"* — with state supervision on closed algorithmic tasks (ICML 2025).
  `[established][search: 2026-07-19 — verbatim; see § Divergences on the "OOD" wording]` **The
  strongest published support for the programme's central architectural intuition**, closest prior
  art to H-RULE-HL's pinned bottleneck and H-GU's "symbolic interface from step 0". **Its
  state-supervision requirement maps to our engine's ability to emit exact intermediate states
  cheaply — an ability currently ASSERTED, not demonstrated: the §8 oracle/API gate must show the
  executor exposes these states before the mapping is treated as load-bearing.**
- **The negative space around plain transformers on traces (jointly load-bearing for H-GU):** naive
  finetuning fails length generalization regardless of scale (Anil 2022); with ideal position
  encodings + formats, 2.5× extrapolation on addition is achievable **but fragile across seeds and
  data order** (Zhou 2024) — so **any H-GU sweep read must be powered for seed variance, or direction
  reads are noise** `[STIPULATED → P3-D-GU prereg requirement]`; LMs as generalist executors on
  CLRS-Text confirm weak length-OOD; and trace-trained transformers on compositional tasks reduce to
  "linearized subgraph matching" (pattern reuse, not algorithm induction), failing OOD *even with*
  explicit trace supervision (Faith-and-Fate). `[prior-verified: 2026-07-11 for the four abstracts;
  the architectural read search: 2026-07-19]`
- **Fusion prior art (hand-off to P3-LR-FUSE, not deepened here):** TransNAR — LM tokens
  cross-attending to a pretrained NAR's node embeddings beats Transformer-only on CLRS-Text in- and
  out-of-distribution; parameter/compute-matching not stated in the abstract, the "20% absolute" folk
  figure is UNVERIFIED at that precision, and it requires the graph input at inference.
  `[prior-verified: 2026-07-11]`

## 4. Proof-trace distillation into small LMs (the H-GU feed) `[established unless tagged]`

### 4.1 What bounded-depth deduction distillation achieves
Transformers CAN learn closed-world deduction over stated rules: 99% in-distribution, 95%+ at depths
beyond training, zero-shot transfer to paraphrased rulebases, at ~RoBERTa scale (RuleTaker).
Generating the proof matters: **iterative single-step implication generation** transfers to unseen
depths and OOD theories where whole-proof generation is weaker (+9 pt) (ProofWriter). LoGiPT is the
closest published shape to "distill kernel proof traces": *"fine-tuned on a… dataset derived from
revealing and refining the invisible reasoning process of deductive solvers"* so the LM emulates the
solver directly, *"outperform[ing] state-of-the-art solver-augmented LMs and few-shot prompting… like
ChatGPT or GPT-4"* on two deductive-reasoning datasets (ProofWriter/PrOntoQA-class).
`[established][search: 2026-07-19 for LoGiPT verbatim; RuleTaker/ProofWriter prior-verified: 2026-07-11]`

### 4.2 The shortcut kills (mandatory controls, not vibes)
- SimpleLogic/paradox: BERT near-perfect in-distribution, **fails other distributions of the SAME
  problem space** — learned statistical features, not reasoning ⇒ every H-GU eval MUST include
  within-problem-space shift splits (rule-priors, branching), not only depth. `[prior-verified: 2026-07-11]`
- PrOntoQA: individual deduction steps fine, **proof planning/search fails** when multiple valid steps
  exist ⇒ engine/search harness owns planning; distillation targets step proposal + verbalization,
  not search policy. `[prior-verified: 2026-07-11]` `[STIPULATED design prior]`
- Faith-and-Fate: trace-trained transformers on compositional tasks collapse to linearized subgraph
  matching, fail OOD **even with** explicit trace supervision. `[prior-verified: 2026-07-11]`

### 4.3 Distillation accounting (the skeptical ledger)
- "770M beats 540B" (Distilling Step-by-Step) is **task-specific finetune vs few-shot generalist** —
  NOT matched; licenses "small specialized ≥ large generalist per task" and nothing stronger. Same
  honest frame for ReProver-vs-GPT-4 (§1.1) and LoGiPT-vs-GPT-4 (§4.1). `[prior-verified: 2026-07-11]`
- CoT distillation DOES reach our band: 125M–1.3B students gain on commonsense suites, with **teacher
  sampling density** the operative variable (multiple chains/instance) (SCoTD). `[prior-verified: 2026-07-11]`
- Verifier-filtered bootstrapping needs no human rationales: STaR's keep-only-correct loop lets 6B
  match a 30× larger finetuned model on CommonsenseQA — with a **weak** verifier (answer-string
  match). A sound engine improves this filter's PRECISION on formal validity for covered statements;
  **not strict dominance** — it costs coverage (only covered statements filterable) and remains
  exposed to formalization/specification error upstream. `[prior-verified: 2026-07-11]` `[EXTRAPOLATION]`
- Synthetic-curriculum existence proofs at our scale: phi-1 (1.3B → HumanEval 50.6%, thin
  contamination controls — recipe inspiration, not evidence); TinyGSM (1.3B + 1.3B learned verifier →
  81.5% GSM8K, verifier carries a large share; owned as analogy by PARSE.md). `[prior-verified: 2026-07-11]`
- **Programme asset alignment `[STIPULATED]`:** AlphaGeometry's decisive ingredient was an
  **engine-generated synthetic corpus with exact traces** (~100M theorems). KOT possesses the RAW
  INGREDIENTS of the analog — a deterministic seedable generator + µs engine over the covered grammar
  with controlled depth/polarity/paraphrase `[memory: encoder/ + poc/ exist; coverage ceiling m0b
  0.3542 friendliest-corpus is the binding scope limit, feasibility-synthesis §0]`. **Whether the
  executor EXPOSES what the recipes consume — proof states, legal-action sets, step traces,
  compiler-style diagnostics — is not demonstrated; the §8 oracle/API gate must show it before the
  AlphaGeometry analog is claimed.** `[STIPULATED gap]`

## 5. Executor-in-the-loop training precedents `[established unless tagged]`

Three rungs, by increasing integration depth — the evidence gets thinner as integration deepens
`[STIPULATED framing]`:

1. **Executor as data filter (expert iteration / rejection finetuning).** Best-evidenced rung: GPT-f
   value-function training from its own verified searches; **same-compute superiority over
   search-only** (Polu, §1.2 item 1, `[search: 2026-07-19]`); HTPS online training; ReST-EM's
   binary-feedback EM loop (gains scale with size, diminish over iterations); STaR at 6B; plateau
   caused by statement supply, relieved by self-play conjecturing (STP, `[search: 2026-07-19]`).
2. **Executor as RL reward / feedback channel.** RLPAF (Lean pass/fail as reward, DeepSeek-Prover-V1.5);
   CodeRL's unit-test critic at 770M-class; **RLEF — training the model to CONSUME execution feedback
   across turns cuts inference samples by an order of magnitude at 8B/70B**; Goedel-V2's
   compiler-feedback self-correction (+2.3 pt ablatable, `[search: 2026-07-19]`); Logic-LM's
   solver-error self-refinement at inference. **Directly licenses training the H-VL retry policy
   rather than only bolting retry on.** `[RLEF/RLPAF/CodeRL prior-verified: 2026-07-11]`
3. **Executor literally in the loss (differentiable).** Semantic loss (circuit-compiled constraints);
   blackbox-differentiation through exact solvers (Gurobi/Blossom V/Dijkstra as layers with
   informative gradients); DeepProbLog/Scallop (§2). All module-scale; **no published demonstration at
   ≥100M-LM scale with a logic engine in the loss found in this search** — an absence at this search's
   scope, not an established field fact, and no disproof. `[prior-verified: 2026-07-11]`

**The scaling-flaws boundary (re-anchored from RAG.md §4):** the decay of verifier-guided search at
large budgets is a **learned-verifier** pathology (misranking prunes valid paths). Sound-checker
systems do not report it; they report plateau, with statement supply as *one* mechanism (STP). For
KOT this separates the failure surfaces Phase-1 must instrument: engine **coverage** (sound analog of
verifier failure), generator **supply/diversity** (analog of conjecturer collapse), and
**formalization/specification error** (outside both, untouched by checker soundness).
`[established boundary; the KOT mapping is EXTRAPOLATION]`

## 6. Transfer to a µs deterministic executor (the crux's engine-side answer)

What the literature establishes, and exactly where KOT's premise goes beyond it:

- **Small proposer + deterministic engine beating larger neural-alone: established at *system*
  level.** AlphaGeometry (151M LM + DD/AR engine, 25/30 vs prior best 10; the oft-quoted GPT-4 0/30
  comparison was NOT confirmed in the draft's Nature fetch — UNVERIFIED), with AG2 showing the neural
  side kept scaling without the symbolic engine capping the system (84% of 2000–2024 IMO geometry);
  ReProver-299M over GPT-4 zero-shot (unmatched accounting noted); Thor's +18 pt from adding hammers.
  In every case **the engine contributes soundness and/or exhaustive local deduction — a capability
  the neural baseline structurally lacks — and the LM contributes exactly what the engine cannot
  enumerate.** `[established: 25/30, 84%, +18 pt search/prior-verified]` **This is add-capability, and
  it is the honest shape of the crux answer.**
- **Checker speed is never the tested variable in this literature.** Where per-check costs are visible
  they sit ~10ms–s `[EXTRAPOLATION — range assembled from setups, not a latency study]`; systems
  compensate with parallelism (10,000 CPU workers) and still win. A 5.29–7.82 µs/query engine
  `[memory: programme premise, programme-3 §2 PREMISE block]` is ~10³–10⁵× cheaper per check than any
  executor here. Two consequences `[EXTRAPOLATION, both]`:
  (a) every verified-training-loop precedent in §5 becomes cheaper in its checking leg — but since
  checking is **not** the reported cost ceiling in any cited system (§1.3), **the µs property does NOT
  by itself improve the loop's economics**; proposer sampling still dominates. Honest claim: "removes
  a cost term", not "changes the regime", for training.
  (b) the candidate **novel** regime is **per-token/inference-time integration**: at µs/check the
  engine could be consulted inside the decode loop (H-RULE-CD's engine-derived continuation sets;
  H-VL's verify-retry with negligible verify overhead) at a cost no published executor could sustain.
  **This search found no precedent for a *semantic* executor consulted per decoding step** — nearest
  cousins are grammar-mask automata (syntax-only; parsing report) and execution-guided partial-program
  decoding/selection (PARSE.md, program-fragment granularity). Claim is "no precedent found in this
  search", NOT "no precedent exists"; P3-LR-RULE owns the executor-backed constrained-decoding search
  and must complete before any novelty claim is settled. **This is where the µs property may be a real
  add-capability differentiator — an H-RULE/H-VL design question, not an H-GU one.** `[STIPULATED hand-off]`
- **The engine as data factory is the underexploited transfer.** AlphaGeometry's synthetic corpus and
  Goedel-V2's scaffolded synthesis both use the deterministic side to MANUFACTURE the training
  distribution. A µs engine removes the ENGINE-EXECUTION term from trace-generation cost at any
  curriculum size — but generator sampling, search, trace serialization, dedup, storage, and
  training-token processing all still scale with curriculum size and will dominate; the speed buys a
  real but PARTIAL training-side term, not "effectively free" generation. `[EXTRAPOLATION]`
- **What nothing here licenses:** that any of this closes the NL boundary (all cited systems consume
  FORMAL inputs or curated statements — the l3a-parse / a5-nl FAILs stand untouched `[memory:
  registry/verdicts, feasibility-synthesis §0]`); and that verifier-loop gains are kernel-CONTENT-
  specific rather than correct-alignment-specific (the f2b confound, unresolved pending knull /
  f2b-transfer `[memory: registry/assessments/f2b-replicate.json does_not_license]`).

## 6a. The crux, stated as a decision `[speculative — direction-only synthesis of §§1–6]`

**Matched-resource win, or add-capability win?** Across NTP, differentiable logic, and NAR:

| Candidate | Strongest reading | Why it is not a matched-resource win |
|---|---|---|
| Polu expert iteration (only same-compute claim) | train-time executor use > search-time use at equal compute | **both arms have the executor** — within-executor allocation, not vs a baseline lacking it |
| Discrete-NAR (strongest overall) | perfect scores + provable OOD correctness on covered algorithmic tasks | guarantee comes from a hard discrete interface + state supervision the baseline structurally lacks — **add-capability** |
| CTP on CLUTRR (best differentiable-logic reasoning result) | SOTA systematic generalization vs neural baselines | resource-matching not established; add-*structure* on a small closed world |
| NTP > ComplEx (3/4 KBs) | matched-ish on tiny KBs | toy scale, link-prediction not a capability ComplEx lacks; GNTP shows no superiority at scale |
| Goedel-8B / Pythagoras-4B > 671B | parameter efficiency under pass@32 | MoE ⇒ ~5×/9× active-param not 80×/167×; pass@k pins sample count only; **both are neurosymbolic** — not vs a neural baseline |
| AlphaGeometry / AlphaProof / Thor / ReProver | small proposer + engine > larger neural-alone | engine supplies soundness/exhaustive deduction the baseline lacks (add-capability); unmatched compute (AG/AP) or component ablation (Thor) or unmatched accounting (ReProver-vs-GPT-4) |

**Verdict `[speculative]`:** **No method in this scope has been shown to beat a matched-resource
neural baseline at the same task, information, and resources with causality demonstrated. Every
demonstrated win adds an exact-reasoning capability the neural baseline structurally lacks.** This is
the *same* answer FUSE reached for GNN–LLM fusion, from an independent literature — which strengthens
it. The programme-level implication is identical: **the defensible, literature-supported value of a
deterministic engine lives in the correctness thesis (a sound checker/interface priced against its
own falsifier), not the efficiency thesis (matched-resource superiority).** The efficiency thesis is
not refuted here — it is simply *unsupported* by this literature, and H-GU's ≥3-point sweep is the
first attempt to produce evidence for it below 2B, where nothing exists.

## 7. Open questions for Phase-1 (each maps to a design bead) `[STIPULATED unless tagged]`

- **Q1 (P3-D-GU).** Does the frontier prover recipe (engine-generated curriculum + verifier-filtered
  self-training + feedback-consumption training) hold BELOW 2B, where no published prover lives?
  8B>671B and 4B>671B make "yes" plausible; nothing demonstrates it. H-GU's ≥3-point sweep is the
  instrument; power it for seed variance (Zhou 2024).
- **Q2 (P3-D-GU).** Does shortcut learning (paradox) persist when the training distribution is
  ENGINE-CONTROLLED (exact traces, controlled rule-priors/branching)? Is the paradox a data artifact
  or an architecture limit? Pre-register within-problem-space shift splits alongside depth splits.
- **Q3 (P3-D-GU, co P3-D-RULE).** Can Discrete-NAR-style state discretization be imposed on a
  transformer host (not a GNN) with engine-emitted state supervision, and does its perfect-OOD
  property survive the transfer? Bridges to H-RULE-HL's bottleneck (ordered LAST per §3.3).
- **Q4 (P3-D-RULE).** At µs check cost, is per-token engine consultation (continuation-set derivation
  mid-decode) latency-viable at p95 on our hardware, and does it beat the same engine used only as a
  post-hoc verifier at matched total budget? No prior art found in this search either way (§6b;
  P3-LR-RULE to confirm).
- **Q5 (P3-D-PS).** Does solver-trace emulation (LoGiPT-style, engine traces distilled INTO the
  parser/generator) beat parse→execute pipelines on the S2 dangerous-wrong metric, or does removing
  the executor at inference reintroduce unsound outputs? The literature shows accuracy parity is
  achievable; it does not report S2-style soundness accounting.
- **Q6 (P3-D-GU, feeds P3-D-SEAL).** What is our statement-supply curve? One documented sound-loop
  plateau mechanism is provable-statement exhaustion (STP; one mechanism, not the universal
  constraint); the covered slice is currently 108 concepts / m0b 0.3542 `[memory:
  feasibility-synthesis §0]`. A conjecturer analog (engine-validated statement synthesis over the
  world layer) needs a cost model before any H-GU RL variant is budgeted.

## 8. Phase-1 hand-off

**What this review settled `[STIPULATED unless tagged]`:**

1. The verifier-loop bet's TRAINING-side precedent is real, replicated, and in one case same-compute
   by the paper's own claim (Polu) — **but that claim is a within-executor allocation result, and no
   result in scope is a matched-resource win over a baseline lacking the executor**; the demonstrated
   wins are add-capability (§6a). H-GU's sweep is the first test of the efficiency thesis at ≤2B, not
   a replication.
2. Differentiable logic is DEPRIORITIZED as an architecture direction for Phase-1 (no at-scale matched
   win found; grounding + cost failure modes) — a prioritization decision at this review's scope, not
   a field-wide closure — retained only as loss-shaping tools (semantic loss, blackbox-diff) for a
   LATE H-GU variant if ever, noting these need a differentiable path a discrete µs engine lacks.
3. Trace distillation without an executor or hard interface is expected to shortcut (three independent
   negative lines: paradox/PrOntoQA/Faith-and-Fate) — H-GU variants must keep the engine in the loop
   (filter/reward/state-supervision); every eval needs within-space shift splits, multi-seed powering,
   depth extrapolation.
4. The µs engine's speed is a candidate DECODE-TIME differentiator (per-token consultation: no
   precedent found in this search; P3-LR-RULE must complete the adjacent search before "unprecedented"
   is claimed) and a PARTIAL DATA-FACTORY asset, but NOT a training-loop-economics differentiator
   (checking is not the ceiling in any cited system).
5. Proof-planning, not step deduction, is the neural deficit (PrOntoQA) — division of labour should
   give search/planning to the deterministic side.
6. pass@k pinning + benchmark-quality audit (miniF2F-v2) go into every Phase-1 prereg touching
   reasoning suites.

**Common prereg requirements for ALL THREE beads (carried from the draft's external review; [STIPULATED]):**
- **Oracle/API gate (blocking, first):** demonstrate the KOT executor can actually EMIT what each arm
  consumes — proof states, legal-action/continuation sets, step traces, compiler-style diagnostics,
  search transitions. µs checking does not imply any of these exist; no arm is budgeted until its
  interface is shown (§3, §4.3, §6).
- **Full resource-vector accounting for every ablation** (KOT-COST/2, ASM-0810): equal model size or
  equal pass@k does NOT license "matched"; no scalar diagnostic alone licenses "compute-matched".
- **Factorial separation** of synthetic curriculum, proof traces, checker filtering, retry feedback,
  and hard state interfaces — no bundled-recipe arms whose components cannot be attributed.
- **Formalization/specification-error accounting distinct from checker validity** — a sound check
  certifies the formal statement, not the intended one (§1.3; miniF2F-v2).
- **"No precedent found" language** for all novelty claims until P3-LR-RULE and P3-LR-PARSE complete
  their adjacent searches.

**Implication for the named design beads (this review's co-input; coordinator owns bd-create):**

- **P3-D-GU** [DESIGN, P2, blocked-by: P3-LR-TINY + this review + P3-LR-FUSE]. Stage the training
  variants in evidence order: (1) engine-generated synthetic curriculum + iterative **single-step**
  trace distillation (ProofWriter/LoGiPT shape) with pre-registered shift/depth/seed-variance protocol
  (§4, §7-Q1/Q2); (2) verifier-filtered bootstrapping (STaR/ReST-EM shape, sound-engine filter)
  (§5.1); (3) RL-from-engine-feedback incl. feedback-consumption training (RLEF shape) (§5.2); rank
  differentiable executor-in-the-loss LAST (no at-scale precedent, §5.3); include a Discrete-NAR-style
  state-supervised variant as the interface-maximal arm (§7-Q3), **gated on the engine emitting
  states**; budget a statement-supply cost model before any RL arm (§7-Q6). **Frame the falsifier per
  §6a: the literature predicts an add-capability (correctness/OOD-guarantee) win, not a
  matched-resource efficiency win — a flat-or-shrinking interface effect at matched training compute
  is consistent with the whole literature and kills the efficiency reading without killing the
  correctness value.**
- **P3-D-RULE** [DESIGN, P1, blocked-by: P3-LR-RULE + this review]. H-RULE-CD's engine-derived
  continuation masking has **no semantic-executor precedent found in this search** (grammar-only
  masking and PARSE.md's execution-guided partial-program decoding are the nearest cousins) — treat
  the novelty claim as "no precedent found", NOT settled, until P3-LR-RULE completes; the
  p95-latency-viability question (§7-Q4) + the causal-provenance requirement (executor traces, NOT
  attention maps — ASM-0815) go into the prereg; **nothing in the NTP literature supports
  KV-placement gains** — leave its prior at the injection report's level. This is the family where the
  µs property is most plausibly an add-capability differentiator (§6b).
- **P3-D-PS** [DESIGN, P1, blocked-by: P3-LR-PARSE + this review]. Adopt executor error messages as a
  first-class refinement/training channel (Logic-LM, Goedel-V2, RLEF, §5.2); test solver-trace
  emulation vs parse→execute on S2 accounting (§7-Q5); keep the engine at inference for soundness on
  covered spans — emulation-only variants must carry an explicit unsoundness budget.

**Non-recommendations (Phase-1 prioritization at this review's search scope, revisitable — not
field-wide closures):** do not build a differentiable logic layer into any Phase-1 host (§2); do not
train on traces without an executor in the loop or a hard interface (§8.3); do not compare family arms
across differing pass@k (§1.3); do not treat AlphaProof/AlphaGeometry headline results as economics
evidence for the index (existence proofs at 10³–10⁵× our compute envelope, §1.2/§6); do not adopt
CLRS/NAR processor results as evidence of real-input transfer (within-framework accounting, §3).

---

## Citation-verification table (2026-07-19)

Legend: **V@src** = re-verified at primary abstract this session; **V-HTML** = verified at
arXiv-HTML / ar5iv (table/body level) this session; **prior** = accepted from the 07-11 NTP.md
verification, not re-fetched (uncontested); **UNVERIFIED** = could not confirm at primary this session.

| # | Source (short) | URL | What it anchors here | Status (2026-07-19) |
|---|---|---|---|---|
| 1 | Pythagoras-Prover | arxiv.org/abs/2606.12594 | 4B > 671B at pass@32, ~167× | **V@src** — "86.1% vs 82.4%… ~167× fewer parameters"; 4B/32B, curriculum SFT + augmented Lean formalisation confirmed |
| 2 | Goedel-Prover-V2 | arxiv.org/abs/2508.03613 | 8B 84.6, > 671B "80× smaller", 32B 88.1/90.4 | **V@src** — all four confirmed; scaffolded synthesis + self-correction + model averaging |
| 3 | Polu (curriculum) | arxiv.org/abs/2202.01344 | the ONE same-compute claim | **V@src** — "at same compute budget… expert iteration… dramatically outperforms proof search only"; curriculum "without… ground-truth proofs" — verbatim |
| 4 | Discrete-NAR | arxiv.org/abs/2402.11628 | strongest support for hard-interface→OOD | **V@src** — "perfect test scores… single-task and multitask"; "prove the correctness… for any test data" (OOD wording — § Divergences) |
| 5 | DeepSeek-Prover-V2 | arxiv.org/abs/2504.21801 | 671B comparator; 88.9% miniF2F | **V@src** — 88.9% + 671B confirmed; "SFT on DeepSeek-V3-Base-671B" is body-level (abstract says "powered by DeepSeek-V3") |
| 6 | DeepSeek-V3 report | arxiv.org/abs/2412.19437 | MoE 671B / 37B activated (the ratio qualifier) | **V@src** — "MoE… 671B total parameters with 37B activated for each token" — verbatim |
| 7 | CTP (differentiable) | arxiv.org/abs/2007.06477 | the one clean CLUTRR win | **V@src** — "scalable and yield state-of-the-art results on the CLUTRR dataset… systematic generalisation" — verbatim |
| 8 | LeanDojo / ReProver | arxiv.org/abs/2306.15626 | ≤2B anchor + the matched component ablation | **V-HTML (ar5iv Table 2)** — 51.2/26.3, 47.6/23.2, 26.5, 13.8, 29.0/7.4, "one GPU week" — exact match to draft |
| 9 | AlphaGeometry | nature.com/articles/s41586-023-06747-5 | small-LM + engine existence proof | **V@src (25/30) via DeepMind blog + Wikipedia**; **151M / 100M / 10,000-CPU-workers prior-verified** (Nature body, paywalled today) |
| 10 | AlphaProof | nature.com/articles/s41586-025-09833-y | maximally-unmatched-compute existence proof | **28-pt silver / 3 problems / Q6 V@src (secondary)**; **~80k+100k TPU-days UNVERIFIED this session** (Nature paywall; prior-verified 07-11) — § Divergences |
| 11 | LoGiPT | arxiv.org/abs/2311.06158 | closest "distill solver traces" shape | **V@src** — "revealing… the invisible reasoning process of deductive solvers"; "outperforms… solver-augmented LMs and few-shot… GPT-4" — verbatim |
| 12 | STP (self-play) | arxiv.org/abs/2502.00212 | statement-supply plateau mechanism | **V@src** — "scarcity of correct proofs (sparse rewards)… 28.5%… doubling… 13.2%… 65.0%, pass@3200" — verbatim |
| 13 | NTP (2017) | arxiv.org/abs/1705.11040 | differentiable logic beats ComplEx on toy KBs | **V@src** — "outperforms ComplEx… on three out of four benchmark knowledge bases" — verbatim |
| 14 | GNTP | arxiv.org/abs/1912.10824 | scaling recovered feasibility, not superiority | **V@src** — "orders of magnitude more efficient… on par with NTPs… competitive link prediction… on large datasets" — verbatim |
| 15 | Thor | arxiv.org/abs/2205.10893 | hammer+LM division of labour | **V@src** — "39% to 57%… 8.2% of problems neither… on their own" — verbatim |
| 16 | GPT-f | arxiv.org/abs/2009.03393 | 700M best; expert-iter loop cost | **prior** (ar5iv full text 07-11) |
| 17 | PACT | arxiv.org/abs/2102.06203 | proof-artifact co-training 32→48 | **prior** (abstract-level) |
| 18 | HTPS | arxiv.org/abs/2205.11491 | unmatched 82.6 Metamath | **prior** (abstract-level) |
| 19 | miniF2F | arxiv.org/abs/2109.00110 | the yardstick | **prior** |
| 20 | miniF2F-v2 | arxiv.org/abs/2511.03108 | benchmark-quality flag (36→70) | **prior** (abstract-level, draft re-verified 07-11) |
| 21 | Graph2Tac | arxiv.org/abs/2401.02949 | tiny online-learning prover | **prior** |
| 22 | AlphaGeometry2 | arxiv.org/abs/2502.03544 | neural side kept scaling (84%) | **prior** (abstract-level; 84% corroborated via Wikipedia search) |
| 23 | Kimina-Prover | arxiv.org/abs/2504.11354 | pass@8192 inflation datapoint | **UNVERIFIED** (search-snippet only, both passes) |
| 24 | ∂ILP | arxiv.org/abs/1711.04574 | memory-bound rule learning | **prior** |
| 25 | DeepProbLog | arxiv.org/abs/1805.10872 | probabilistic-logic-in-the-loss, module scale | **prior** |
| 26 | Scallop | arxiv.org/abs/2304.04812 | top-k provenance approx | **prior** |
| 27 | Semantic Loss | arxiv.org/abs/1711.11157 | constraint-executor in the loss | **prior** |
| 28 | Blackbox Solvers | arxiv.org/abs/1912.02175 | exact solver as a layer | **prior** |
| 29 | CLRS | arxiv.org/abs/2205.15659 | NAR benchmark, within-framework | **prior** |
| 30 | Generalist-NAR | arxiv.org/abs/2209.11142 | >20% within-framework | **prior** |
| 31 | TransNAR | arxiv.org/abs/2406.09308 | fusion prior-art (→ P3-LR-FUSE) | **prior** ("20% absolute" UNVERIFIED at precision) |
| 32 | CLRS-Text | arxiv.org/abs/2406.04229 | LM length-OOD weakness | **prior** |
| 33 | NAR-position | arxiv.org/abs/2105.02761 | blueprint; thin real-transfer | **prior** |
| 34 | Anil length-gen | arxiv.org/abs/2207.04901 | naive finetune fails length-gen | **prior** |
| 35 | Zhou length-gen | arxiv.org/abs/2402.09371 | 2.5× but seed-fragile (powering req) | **prior** |
| 36 | RuleTaker | arxiv.org/abs/2002.05867 | closed-world deduction learnable | **prior** (also V@src in FUSE sibling) |
| 37 | ProofWriter | arxiv.org/abs/2012.13048 | single-step > whole-proof for depth | **prior** |
| 38 | paradox (SimpleLogic) | arxiv.org/abs/2205.11502 | shortcut kill #1 | **prior** |
| 39 | PrOntoQA | arxiv.org/abs/2210.01240 | planning fails, steps fine (kill #2) | **prior** |
| 40 | Faith-and-Fate | arxiv.org/abs/2305.18654 | trace-trained shortcut (kill #3) | **prior** |
| 41 | Distill Step-by-Step | arxiv.org/abs/2305.02301 | 770M>540B accounting flag | **prior** |
| 42 | SCoTD | arxiv.org/abs/2306.14050 | CoT distill into 125M–1.3B | **prior** |
| 43 | STaR | arxiv.org/abs/2203.14465 | weak-verifier bootstrapping 6B | **prior** |
| 44 | phi-1 | arxiv.org/abs/2306.11644 | synthetic-curriculum at 1.3B | **prior** |
| 45 | TinyGSM | arxiv.org/abs/2312.09241 | 1.3B+verifier 81.5 GSM8K | **prior** (owned by PARSE.md) |
| 46 | CodeRL | arxiv.org/abs/2207.01780 | executor-as-reward sub-1B | **prior** |
| 47 | RLEF | arxiv.org/abs/2410.02089 | train-to-consume-feedback (H-VL) | **prior** |
| 48 | ReST-EM | arxiv.org/abs/2312.06585 | binary-feedback EM, diminishing | **prior** |
| 49 | scaling-flaws | arxiv.org/abs/2502.00271 | learned-verifier DECAY (RAG.md) | **prior** (lit-KB arxiv_2502.00271) |
| 50 | Logic-LM | arxiv.org/abs/2305.12295 | external solver + error channel | **prior** (lit-KB arxiv_2305.12295) |
| 51 | SATNet | arxiv.org/abs/1905.12149 | grounding cautionary tale | **UNVERIFIED** (carried, both passes) |
| 52 | SATNet-debunk | proceedings.neurips.cc/paper/2020/…0ff8033cf9 | 0% once labels removed | **UNVERIFIED** at page level (carried) |
| 53 | DeepSeek-Prover-V1.5 | arxiv.org/abs/2408.08152 | RLPAF executor-as-reward | **prior** |
| 54 | LEVER | arxiv.org/abs/2302.08464 | execution-selection lever | **prior** (owned by PARSE.md; UNVERIFIED here) |

**Coverage:** 15 load-bearing citations re-verified at source this session (13 at abstract/HTML level
verbatim; ReProver via ar5iv table; AlphaGeometry 25/30 + AlphaProof 28-pt via authoritative
secondary). 39 accepted as `[prior-verified: 2026-07-11]` (uncontested / non-load-bearing-as-exact-
number / owned by a sibling report). **No load-bearing citation failed source-verification.** The four
draft-flagged UNVERIFIED entries (Kimina, SATNet ×2, LEVER) remain UNVERIFIED and are non-load-bearing
by construction. Two entries drop from abstract-verbatim to body-level this session (AlphaProof
TPU-days; DeepSeek-Prover-V2 SFT-on-base) — neither changes a conclusion (§ Divergences).

---

## Divergences from the Fable draft (`docs/next/lit/NTP.md`)

All divergences are **minor / provenance- or wording-level**; none changes a conclusion. Listed for
the critique record.

1. **Discrete-NAR "OOD" wording (mild over-precision, in the draft's favour).** The draft states
   "*perfect in- and out-of-distribution test scores*". The abstract's literal wording is "*perfect
   test scores both in single-task and multitask setups*" plus the *stronger* claim "*prove the
   correctness of the learned algorithms for any test data*." "Correctness for any test data" ⊇ OOD,
   so the draft's reading is substantively correct (arguably conservative — the correctness proof is
   stronger than an OOD *score*). Flagged only because the specific string "out-of-distribution test
   scores" is not the abstract's phrasing; a Phase-1 doc should cite the "any test data" correctness
   claim, not an "OOD scores" claim. `[search: 2026-07-19]`

2. **AlphaProof TPU-days (~80k RL + ~100k autoformalization) not re-confirmable at source this
   session.** The Nature article paywalls (303 redirect to `idp.nature.com`); the julian.ac paper
   summary corroborates the *qualitative* claim ("*The limit here was entirely how many TPUs we could
   get our hands on!*") and the ~80× formalized-vs-NL multiplier, but does **not** state the TPU-day
   figures. The draft attests these were fetched from the Nature body on 07-11. **Downgrade
   provenance to `[prior-verified: 2026-07-11]` / `[UNVERIFIED this session]`.** Non-load-bearing:
   any value in the 10⁴–10⁵ TPU-day range supports the "existence proof, not economics proof"
   conclusion identically. The 28-pt silver / 3-problem / Q6 headline **is** re-confirmed at
   secondary sources this session. `[search: 2026-07-19]`

3. **DeepSeek-Prover-V2 "SFT on DeepSeek-V3-Base-671B" is body-level, not abstract-level.** The
   abstract says initialization data is "*powered by DeepSeek-V3*" and reports 88.9% miniF2F on the
   671B model; the explicit "supervised fine-tuning on DeepSeek-V3-Base-671B (§2.3)" is in the HTML
   body (the draft's jsonl already attributes it to a 07-11 HTML fetch). The load-bearing MoE
   qualification does **not** depend on this — it rests on the separately-verified DeepSeek-V3 report
   ("671B total… 37B activated", verbatim, item 6). No conclusion changes. `[search: 2026-07-19]`

4. **Pythagoras comparison target number surfaced (additive, not a divergence).** The draft asserts
   "Pythagoras-Prover-4B does the same at ~167× fewer" without the head-to-head numbers; the source
   gives "**86.1% vs 82.4%**" (Pythagoras-4B vs DeepSeek-Prover-V2-671B at pass@32). This confirms and
   sharpens the draft — worth carrying into any Phase-1 citation so the comparison is auditable. The
   4B headline 86.1% and 32B 93.0% both check out. `[search: 2026-07-19]`

**Points of full concordance worth stating:** the draft's central verdict (§0/§1.2 — the ledger is one
same-compute *claim* plus four component ablations, everything else unmatched or add-capability), its
MoE qualification of the 80×/167× ratios, its miniF2F-v2 benchmark-quality caveat, its
three-negative-lines argument against executor-free trace distillation, its Discrete-NAR read as the
strongest support for the hard-interface bet, its differentiable-logic deprioritization, and its "no
precedent found (not settled)" discipline on the per-token-consultation novelty claim all **hold at
source**. This formalization adopts them, adds the epistemic tagging + the explicit matched-resource-
vs-add-capability crux synthesis (§6a, aligning the NTP answer with FUSE's) + the engine-executor
transfer analysis (§6) + the citation-verification table, and leaves the draft's conclusions intact.
