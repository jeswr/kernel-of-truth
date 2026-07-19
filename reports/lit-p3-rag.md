# Lit review — P3-LR-RAG: RAG, structured retrieval, KGs, tool-using neural baselines

**Bead:** P3-LR-RAG (Programme-3, Phase-0 [LIT]).
**Author role:** literature-researcher (independent source-verification + formalization pass).
**Date:** 2026-07-19.
**Parent:** `docs/next/programme-3-neurosymbolic-architecture.md` (rev 2) §2.3
(baseline strength / frontier-builder / attribution factorisation), §2.2 (the answer-key
factorial controls), §3.4 (H-RB retrieve-vs-bake), §5 table row P3-LR-RAG.
**Feeds:** **P3-D-RAGC** (the matched generic-RAG/tool-use control — the strongest missing
baseline) and **P3-D-FRONTIER** (the standing neural frontier-builder), with co-input to
**P3-D-GNN** (retrieval side only) inside the KOT-FAIR/2 freeze.
**Status:** DRAFT for the review gate (GPT-5.6) + Fable critique. Not a freeze; takes no design
decision and stipulates nothing binding. Do **not** commit/push — coordinator review pending.

> **Relationship to `docs/next/lit/RAG.md`.** A prior, thorough RAG review exists (Fable, chief
> architect, 2026-07-11, bead …s55r.4) with a 28-entry source ledger
> `docs/next/lit/RAG.sources.jsonl`. **This report is not a redo.** It is (a) an independent
> re-verification, at source and this session, of every load-bearing citation in that ledger;
> (b) a divergence audit against the draft's claims; and (c) the formalized bead deliverable at
> the requested `reports/` path, refreshed to 2026-07-19 and epistemic-tagged. Where I re-fetched
> a source I say `[search: 2026-07-19]`; the citation-verification table (§8) records reachability
> and claim-support for all 28. **Headline verification result: all 28 sources reachable and
> claim-supporting at their primary/abstract source; two numeric/title divergences and two
> body-level caveats found (§9) — none overturns a load-bearing conclusion, but one (TinyAgent
> training-set size) is a clean factual error in the draft and jsonl.**

---

## 0. Epistemic conventions

- `[established]` — external empirical/methodological fact confirmed at a primary source this
  session. `[claimed]` — asserted in a source but single-source, or a causal reading stronger than
  the reported measurement. `[speculative]` — my forward inference / design judgement.
- Provenance suffix: `[search: 2026-07-19]` = re-verified via WebFetch this session;
  `[memory]` = from the parent design doc / in-repo verdicts, not re-checked at source.
- `[UNVERIFIED]` = a specific figure I could **not** confirm at the source I reached (usually
  because it lives in the paper body, not the abstract).
- Load-bearing lines additionally carry `[MEASURED | STIPULATED | EXTRAPOLATION]` in the draft's
  sense: MEASURED = a published number restated strictly inside its paper's own envelope (the
  *authors'* measurement, not ours); EXTRAPOLATION = a cross-paper, direction-only reading, never a
  premise for a verdict; STIPULATED = a scoping/design judgement made here.
- **Boundary reminder** (inherited from the draft and the KB honesty boundary): the lit-KB records
  are recall infrastructure, not evidence; nothing here is a registry mutation, ASM, or KB ingest.
  The internal anchor this review must stay consistent with is `docs/next/feasibility-synthesis.md`:
  a5-llm's PASS "does not license" any kernel-vs-RAG conclusion because it had **no
  conventional-substrate arm** ("nothing distinguishes the kot-axiom kernel from ANY typed store +
  checker"); f2b-replicate's +0.1507 beat a *trained PRM* (Skywork-PRM-1.5B 0.5267) but never a
  matched generic-RAG arm. **Closing that gap is the entire reason P3-D-RAGC exists.** [memory]

---

## Q1. Strongest small-model (100M–2B) RAG + tool-use recipes — the frontier S must beat

**Retrieval side.** [all `[established][search: 2026-07-19]` unless noted]

- **kNN-LM** (ICLR 2020, 1911.00172): interpolating a Wikitext-103 LM with a kNN datastore over the
  training set improves perplexity by **2.9 points (≈18.65 → 15.79) with no additional training**
  [MEASURED]. Verified verbatim. Cost is the datastore + per-token ANN search — uncharged in the
  headline.
- **RETRO** (ICML 2022, 2112.04426): with a **2-trillion-token** database, "comparable performance
  to GPT-3 and Jurassic-1 despite using **25× fewer parameters**" [MEASURED]. Verified verbatim.
  The 25× is a *parameter* claim; a deployment-bytes-inclusive comparison is unperformed by the
  authors [EXTRAPOLATION — the P3-D-RAGC ledger must run it, not cite it].
- **Atlas** (JMLR 24(251), 2208.03299): "over 42% accuracy on Natural Questions using only 64
  examples… outperforming a 540B parameters model by 3% despite having **50× fewer parameters**"
  [MEASURED]. Verified verbatim — index bytes excluded from the size claim.
- **MassiveDS** (NeurIPS 2024, 2407.12854): a **1.4-trillion-token** open datastore; "increasing the
  size of the datastore… monotonically improves… without obvious saturation" and "a smaller model
  augmented with a large datastore outperforms a larger LM-only model on knowledge-intensive tasks"
  [MEASURED]. Verified verbatim.
- **Mallen et al. / PopQA** (ACL 2023, 2212.10511): 14k questions, 10 models; "retrieval-augmented
  LMs largely outperform orders of magnitude larger LMs" **on long-tail entities**, "scaling fails
  to appreciably improve memorization… in the long tail", and adaptive (popularity-thresholded)
  retrieval "significantly improves… performance while reducing… inference costs" [MEASURED].
  Verified verbatim.
- **Self-RAG** (ICLR 2024, 2310.11511): 7B/13B with reflection tokens (learned when-to-retrieve +
  self-critique) "outperforms ChatGPT and retrieval-augmented Llama2-chat on Open-domain QA,
  reasoning and fact verification" [MEASURED]. Verified verbatim. 7B is above band; the *recipe* is
  budget-portable.

**Tool-use side, at ≤2B genuinely:**

- **xLAM-1B / APIGen** (2406.18518): 60k execution-verified synthetic function-calling examples over
  "**3,673 executable APIs across 21… categories**"; the 1B model "surpass[es] GPT-3.5-Turbo and
  Claude-3 Haiku" on the Berkeley Function-Calling Benchmark; the 7B "outperform[s] multiple GPT-4
  models" [MEASURED]. Verified verbatim. Lever = verified-synthetic-data quality (format→execution→
  semantic check), not architecture. Function-calling-specific but broad within that.
- **TinyAgent-1.1B** (EMNLP 2024 demo, 2409.00608): **80.06%** success (7B: **84.95%**) vs
  GPT-4-Turbo's **79.08%** on a **16-function** Mac-assistant suite, with a ToolRAG step using a
  **fine-tuned DeBERTa-v3-small** tool selector (0.998 tool recall) [MEASURED]. The 80.06/84.95/79.08
  numbers and the 16-tool scope are verified at the authors' BAIR blog (the arXiv abstract does not
  carry them). **Divergence (§9): the training-set size is 80K examples per the authors, not the
  "40k" in the draft and jsonl.** Domain-narrow by construction; the DeBERTa selector's weights /
  training / inference are off-ledger in the headline and must be booked in any matched-resource
  comparison.
- **Toolformer** (NeurIPS 2023, 2302.04761): self-supervised API-call insertion (calculator, QA,
  search×2, translation, calendar) yields "substantially improved zero-shot performance… often
  competitive with much larger models" at 6.7B [MEASURED, above band, canonical recipe]. Verified.

**Synthesis** [EXTRAPOLATION, direction-only]: at 100M–2B, this sweep finds **no published win over
larger dense models under a deployment-bytes-inclusive, matched-total-resource ledger**. Read this
as "none found in a targeted (not systematic) sweep", not "none exists". Every "small beats large"
*retrieval* result charges parameters but not the index (kNN-LM, RETRO, Atlas, MassiveDS all follow
this accounting); the ≤2B *tool-use* wins are domain-restricted (TinyAgent: one assistant domain,
16 tools, off-ledger selector) or function-calling-specific (APIGen: broad within that, 3,673 APIs).
**Implication for the frontier F(B_k):** at small budgets it is likely **dense-model + adaptive
test-time compute + a modest local index scaled to the same byte budget as the kernel store** — not
a trillion-token-datastore configuration, which would bust any deployment-bytes budget. The three
G4 comparator recipes to implement: (i) verified-synthetic-data fine-tune for tool use;
(ii) adaptive/popularity-thresholded retrieval; (iii) datastore scaled *to the kernel store's byte
budget*.

---

## Q2. Structured/KG retrieval vs dense — when each wins, and depth dependence

- **GraphRAG** (2404.16130): LLM-built entity graph + pregenerated community summaries; "substantial
  improvements over a conventional RAG baseline for both the comprehensiveness and diversity" on
  **global sensemaking** questions over **~1M-token** corpora — *not* local factoid QA [MEASURED,
  verified]. **Caveat (§9):** the *abstract* does not report indexing runtime; the draft's "reports
  indexing wall time for its corpora" is a body-level claim I did not re-verify at the body this
  session — treat as `[UNVERIFIED at body]`. The load-bearing conclusion (no complete
  bytes/build-compute lifecycle ledger exists) is unaffected.
- **HippoRAG** (NeurIPS 2024, 2405.14831): KG + Personalized PageRank; single-step retrieval
  "comparable or better… than iterative retrieval like IRCoT while being **10–30× cheaper and 6–13×
  faster**", "up to 20%" over SOTA on multi-hop QA [MEASURED, verified verbatim]. Graph is
  LLM-extracted offline — an indexing cost dense retrieval does not pay.
- **RAG vs. GraphRAG: A Systematic Evaluation** (2502.11371): under a unified protocol, "**neither…
  uniformly dominates**", strengths are task-dependent, and combining them yields "consistent…
  improvements" [MEASURED, verified].
- **When to use Graphs in RAG / GraphRAG-Bench** (2506.05690): "**GraphRAG frequently underperforms
  vanilla RAG on many real-world tasks**"; introduces a difficulty-graded benchmark with stage-wise
  evaluation (construction → retrieval → generation) [MEASURED, verified verbatim].
- **MiniRAG** (2501.06713): the one small-model-specific graph result — a heterogeneous graph index
  (chunks + named entities) + topology-enhanced retrieval lets SLMs reach "comparable performance to
  LLM-based methods… while requiring only **25% of the storage**" [MEASURED — author-reported
  *relative* to their own LLM-RAG baseline, verified verbatim]. **The mechanism reading (graph
  structure "substitutes for" the semantic embedding quality small models lack) is the authors'
  causal interpretation** [claimed], stronger than the reported system comparison — this is the same
  bet H-GNN makes, and it is a *hypothesis to test*, not a result to build on.
- **LightRAG** (2410.05779): dual-level (low/high, entity-relation + vector) retrieval + incremental
  index updates; "considerable improvements in retrieval accuracy and efficiency" [MEASURED,
  qualitative]. **The abstract contains no quantitative token-cost numbers** — the draft's UNVERIFIED
  flag on its cost tables is confirmed correct.

**When each wins** [EXTRAPOLATION, direction-only]: dense top-k wins single-hop, local,
paraphrase-tolerant factoid lookups (cheap index, no construction LLM passes); graph retrieval wins
where the answer is a *path or a summary over structure* (multi-hop composition, whole-corpus
aggregation). **Hypothesis, not established:** the break-even moves toward structure as
hops/aggregation depth grows and as the generator shrinks (MiniRAG's causal reading — authors').
No source here measures a hops/aggregation *threshold*, shows gains monotone in depth, or shows a
GNN encoder becoming preferable — HippoRAG shows a graph *retriever* can beat iterative retrieval on
selected multi-hop QA, no more. **Hard scope limit for P3-D-GNN:** every graph source in this ledger
concerns graph-based **retrieval/indexing** — **none studies GNN-to-LM fusion vs text
serialisation, and no GNN-fusion paper is in this ledger.** The GNN-vs-serialisation question is
therefore *not* de-risked here; it stays open pending P3-LR-FUSE, and P3-D-GNN must carry an explicit
"no prior" statement for its empirical premise. GraphRAG-Bench's difficulty gradient is the best
current instrument, but there is **no clean published size×depth sweep** of the kind §3.2
pre-registers — that sweep is genuinely novel territory for P3-E-GNN-1.

---

## Q3. Honest index accounting — size, build cost, query cost

What the strongest papers charge for, and don't [EXTRAPOLATION over Q1–Q2 sources]:

| Cost axis | Field practice | Honest instances (verified) |
|---|---|---|
| Index bytes | Almost never counted against the "fewer parameters" headline | RETRO 2T tokens; MassiveDS 1.4T tokens + released pipeline; kNN-LM datastore ≈ training-set order; MiniRAG reports storage (25%, author-relative) |
| Build/construction | Rarely priced in full; GraphRAG-class methods add whole-corpus LLM passes (entity extraction + community summaries) | HippoRAG prices *online* retrieval (10–30× cheaper than IRCoT) but not offline graph build; GraphRAG-Bench evaluates the construction stage explicitly |
| Query-time | Sometimes latency, rarely energy; kNN-LM pays ANN search per token (uncharged) | BEIR is unusually explicit that its best zero-shot systems (rerank/late-interaction) win "at high computational costs" [MEASURED, verified] |
| Comparability | Implementation variance so bad a toolkit exists to fix it | FlashRAG (2405.13576): **16 methods + 38 datasets** (current abstract, verified 2026-07-19 — matches the draft's v2 pin; v1 was 12/32), motivated by "the absence of a standardized framework" [MEASURED] |

**Decision take** [STIPULATED]: KOT-SIZE/2's six-figure recipe (packed bytes, compressed
distribution, warm RSS, cold working set, **index/store construction size and cost**, remote deps)
is stricter than the accounting practised in **any of the 28 papers reviewed** — a reading of this
sweep, not a systematic-search result. Whether *any* published small-model RAG win survives figure-5
as a "smaller system" claim is an **open calculation** (needs a systematic search + actual
byte/build/query arithmetic per system; unperformed by anyone found). P3-D-RAGC must therefore
(a) charge the generic-RAG arm and the kernel arm **identical ledgers** (index bytes + build compute
+ query compute), and (b) pin the retriever/index from a standard harness (FlashRAG-style) so the
control is not weakened by our own implementation variance. KOT-LIFE/1 should book graph-construction
LLM passes exactly like store authoring — the literature's silent asymmetry (dense index ≈ free embed
pass; graph index ≈ full LLM sweep) becomes an explicit line item. This also frames the H-RB
retrieve-vs-bake fork (§3.4): the disk-store side's per-query index bytes + ANN/PPR compute are
exactly the uncharged costs above, and must be measured at both retrieve and bake settings.

---

## Q4. Adaptive test-time compute (Snell — VERIFIED) + learned verifiers as baseline components

**The ICLR-2025 result — verified at source (arXiv:2408.03314), with envelope.** The citation
resolves to **Snell, Lee, Xu & Kumar, "Scaling LLM Test-Time Compute Optimally can be More Effective
than Scaling Model Parameters"** [note the draft/jsonl title appends "for Reasoning"; the canonical
arXiv title does **not** — minor §9 divergence]. Claims restated inside their envelope, verified
verbatim 2026-07-19:

- "we can improve the efficiency of test-time compute scaling by **more than 4×** compared to a
  best-of-N baseline" — via a difficulty-adaptive **"compute-optimal" scaling strategy** that
  "allocate[s] test-time compute adaptively per prompt" [MEASURED].
- "test-time compute can be used to **outperform a 14× larger model**" — but conditioned "on problems
  where a smaller base model attains somewhat non-trivial success rates" [MEASURED].

Envelope constraints the headlines omit (load-bearing for transfer to our band):
- Experiments used **PaLM-2-class models on MATH with fine-tuned revision models and PRMs**
  [body-level, well-established; the abstract I fetched names neither model nor benchmark — so treat
  "PaLM-2 / MATH" as `[claimed: body]`, though it is uncontested]. Nothing here is measured at
  135M–1.7B or off math.
- **Prompt-difficulty estimation itself consumes non-trivial test-time compute** — a faithful
  implementation must budget the estimator, not treat difficulty as free oracle input.
- The **>4× and 14× findings are separate comparisons** (strategy-selection efficiency vs a
  FLOPs-matched model-size comparison) — they do **not** compose into one "4× compute buys one model
  class" exchange rate.
- Authors leave generalisation beyond math / easily-verified domains **unresolved**; the 14× is
  conditional on difficulty and on the assumed inference-to-pretraining token ratio.

Corroborating / bounding:
- **Inference Scaling Laws** (Wu et al., 2408.00724): "the Llemma-7B model… paired with our novel
  tree search algorithm consistently outperforms the Llemma-34B model across all tested inference
  strategies on the MATH benchmark"; smaller models + advanced inference are "Pareto-optimal…"
  [MEASURED, verified verbatim].
- **Scaling Flaws of Verifier-Guided Search** (2502.00271): as sample budget grows, verifier-guided
  search "exhibits diminishing advantages and eventually underperforms repeated sampling" (Mistral-7B,
  DeepSeekMath-7B; GSM8K/MATH); mechanism = "imperfect verifiers misrank candidates and erroneously
  prune all valid paths", worst on hard/OOD [MEASURED, verified verbatim]. **Scope:** evidence for
  the *particular verifiers/search procedures tested* — it does **not** establish that every
  learned-verifier frontier must degrade, nor that a symbolic-verifier *system* is immune.

**Learned neural verifiers as baseline components** (the recipe F(B_k) needs) [all verified]:
- **Cobbe et al.** (2110.14168): trained outcome verifiers + sample-and-rank "significantly improves
  performance on GSM8K", and "verification scales more effectively with increased data than a
  finetuning baseline" [MEASURED]. **The folk-cited "6B+verifier ≈ 30× larger finetuned model" figure
  is NOT in the abstract** — the draft's UNVERIFIED flag is confirmed correct (it lives in the body).
- **Lightman et al.** (2305.20050): "process supervision significantly outperforms outcome
  supervision"; the PRM "solves 78% of problems from a representative subset of the MATH test set";
  releases **PRM800K = 800,000 step-level human labels** [MEASURED, verified verbatim].
- **Math-Shepherd** (2024.acl-long.510): automatic (no-human-label) process supervision; Mistral-7B
  **77.9 → 84.1** GSM8K via step-RL, **89.1 GSM8K / 43.5 MATH** with verification [MEASURED, verified
  verbatim].
- **Small LMs Need Strong Verifiers** (2404.17140): ≤13B models cannot reliably self-correct;
  improvement requires a **strong external verifier** (GPT-4-based here); weak self-verification is
  the binding constraint [MEASURED, verified].

**What this supplies** [EXTRAPOLATION, direction-only]: adaptive test-time compute buys **two
*separate* results** — (a) >4× efficiency over best-of-N from difficulty-adaptive strategy
selection, and (b) parity with a 14×-larger model **on the mid-difficulty band** in a distinct
FLOPs-matched comparison — with two hard edges: no rescue where base success ≈ 0, and (for the tested
verifiers/search) decay at large budgets. **The review's premise holds: best-of-k self-consistency is
too weak to serve as F(B_k)'s test-time-compute representative.** But **"implement Snell-style" is not
yet an executable recipe** — P3-D-FRONTIER must still design a *budgeted* difficulty estimator (its
compute charged to the arm), the eligible search policies per budget rung, verifier training/build
costs on the ledger, a base-success≈0 fallback, and a **non-math calibration gate** before the >4×
figure can be assumed to transfer. F(B_k)'s verifier recipe is clear: (i) a Cobbe-style outcome
verifier and (ii) a Math-Shepherd-style auto-labelled PRM (no human-label budget), sized to the
byte/compute budget, used as both best-of-N ranker and search guide. f2b's Skywork-PRM-1.5B arm was
already the right *shape* and the kernel arm beat it (0.5267 vs kernel, formal slice,
alignment-confounded — feasibility-synthesis §2) [memory].

---

## Q5. Attributing a RAG "win" — separating retrieval from generation, corpus/index parity

The methodological toolkit the field converged on, and the traps it documents [all verified verbatim
2026-07-19]:

1. **Source-snapshot parity.** KILT (NAACL 2021, 2009.02252) grounds all tasks in "the same snapshot
   of Wikipedia" and evaluates "downstream performance in addition to the ability of the models to
   provide provenance" [MEASURED]. **Scope, stated honestly:** KILT does **not** mandate identical
   retrievers across systems, and is **no precedent for the cross-representation control P3-D-RAGC
   needs** — "same source snapshot" is not "same corpus, same retriever/index". Converting the same
   source into kernel records vs passages vs triples vs tool schemas changes the *indexed objects*
   and the retrieval problem itself; the equivalence rules for that conversion have **no published
   precedent**.
2. **Always include the lexical baseline.** BEIR (2104.08663): "BM25 is a robust baseline" that dense
   retrievers "often underperform" out-of-domain; rerank/late-interaction win zero-shot "at high
   computational costs" [MEASURED]. A "structured store beats dense RAG" claim that never ran BM25 is
   unattributed.
3. **Retrieval quality and generation quality move independently.** FiD (2007.01282): "performance…
   significantly improves when increasing the number of retrieved passages" — generation-side
   evidence aggregation, not retrieval precision, drove SOTA on NQ/TriviaQA [MEASURED]. Report
   retrieval recall@k vs gold provenance *separately* from end-task accuracy.
4. **Position confound.** Lost in the Middle (TACL 2023, 2307.03172): accuracy "is often highest when
   relevant information occurs at the beginning or end… and significantly degrades" mid-context
   [MEASURED] — context order is a hidden variable in any RAG comparison.
5. **The random-document trap.** The Power of Noise (SIGIR 2024, 2401.14887): high-scoring-irrelevant
   documents hurt, while "adding random documents in the prompt improves the LLM accuracy by up to
   **35%**" [MEASURED, their envelope; mechanism contested]. A measured "retrieval win" can be a
   prompt-perturbation effect — a random-document control arm is cheap and kills this reading.
6. **Gains concentrate in the long tail.** Mallen (Q1): retrieval's benefit is popularity-stratified;
   unstratified averages hide whether the store or parametric memory answered [MEASURED].
7. **Implementation variance is a first-order confound.** FlashRAG (Q3): the toolkit's motivation is
   that un-standardised RAG comparisons were unreliable [MEASURED].

**The attribution bottom line for "typed store + retrieval" vs "kernel semantics."** The literature
separates *retrieval* from *generation* well (FiD, BEIR, Lost-in-the-Middle, Power-of-Noise), and
separates *structured storage* from *retrieval* only recently (RAG-vs-GraphRAG unified protocol,
GraphRAG-Bench stage-wise evaluation). It has **no precedent for isolating "kernel semantics" from
"typed store"** — the cell that matters most for our thesis (aligned-non-kernel store vs kernel
store, same retriever, the §2.2(2e) knull-lesson control) is **our own instrument and carries the
load alone**. This is the direct literature corroboration of the feasibility-synthesis warning that
a5-llm "does not distinguish the kot-axiom kernel from ANY typed store + checker": the field simply
has not built the discriminating control, so the draft's insistence that P3-D-RAGC + the
aligned-non-kernel cell must supply it de novo is well-founded [established + STIPULATED].

---

## Q6. The strongest-baseline honest read — how good is the frontier S must beat, really?

Asked to surface this plainly [EXTRAPOLATION, direction-only, my read]:

- **The RAG/tool-use frontier at 100M–2B is strong but not obviously winning under honest
  accounting.** The genuinely-small wins that exist are either (i) *retrieval* wins that only look
  like size wins because the index is off the ledger (kNN-LM, RETRO, Atlas, MassiveDS — every one),
  or (ii) *tool-use* wins that are domain-narrow (TinyAgent, 16 tools + off-ledger DeBERTa selector)
  or task-scoped (APIGen function-calling, though broad within it). Under KOT-SIZE/2's
  bytes-inclusive ledger, **the frontier's headline advantages are not established to survive** —
  but that is an *open calculation*, not a demonstrated weakness. Do not mistake "their accounting is
  lax" for "we will win": the honest reading is that the comparison **has not been run fairly by
  anyone**, in either direction.
- **This is good news for the fairness case, not for the win probability.** The matched-RAG control we
  must build is *stronger accounting than the field's own norm*. That raises the bar F(B_k) — a
  properly-built frontier (dense model + adaptive test-time compute + a byte-budgeted index + an
  auto-PRM verifier) is a **serious** comparator, materially stronger than f2b's Skywork-PRM arm,
  and there is no published result letting us assume the kernel beats it. S must beat *this*, not the
  literature's off-ledger headlines.
- **The single most dangerous baseline is the aligned-non-kernel typed store + retrieval** (§2.2 cell
  e + the §2.3 RAG control), precisely because the literature gives us no instrument to separate it
  from "kernel semantics." If the kernel arm's advantage collapses to that cell, the distinctive
  thesis is unsupported even if the *system* wins. The frontier that most threatens the thesis is
  therefore not the biggest dense model — it is a boringly-competent typed-store RAG at matched
  bytes.

---

## Q7. Capability-limited vs fundamental — per prior RAG/tool-use limitation

- **Off-ledger index accounting** (kNN-LM, RETRO, Atlas, MassiveDS): **capability-limited/cultural**,
  not fundamental — nothing prevents a bytes-inclusive comparison; the field just does not run it.
  This is the gap P3-D-RAGC exploits (fairly, in both directions).
- **Graph-construction cost opacity** (GraphRAG, HippoRAG, LightRAG): **capability-limited** — build
  cost is measurable, merely unmeasured/underreported. Budget to measure it; do not cite it.
- **Domain-narrow tool-use** (TinyAgent): **partly fundamental to the recipe** — curated-domain
  fine-tune + off-ledger selector is how the number is achieved; the win does not obviously generalise
  and should not be read as a general small-model tool-use frontier. APIGen (broad, execution-verified
  synthetic) is the more portable recipe.
- **Verifier-guided-search decay at large budgets** (Scaling Flaws): **fundamental for the
  learned-verifier family tested** (imperfect verifiers misrank + prune) but **not established as
  universal** — and specifically not established to bind a *sound symbolic* verifier on its covered
  slice. That immunity is a **claim P3-E-VL-1 must measure end-to-end**, not assume.
- **Small-model self-correction failure** (Small-LMs-Need-Strong-Verifiers): **fundamental for
  self-verification** at ≤13B — which is exactly why an *external* verifier (learned PRM or our
  symbolic checker) is the load-bearing component, not the base model's own judgement.
- **The middle-context / random-document effects** (Lost-in-the-Middle, Power-of-Noise): **artefacts
  of current LLM context use**, controllable — they are confounds to neutralise with fixed ordering +
  a random-document cell, not architecture verdicts.

---

## Implications for P3-D-RAGC and P3-D-FRONTIER (the concrete asks)

**P3-D-RAGC — comparator-pinning (the matched generic-RAG/tool-use control).** The literature
supplies **necessary cells, not an executable control**:
- *Supplied (verified):* same pinned **source-snapshot** hash + provenance scoring (KILT pattern,
  scope-limited — no same-retriever/cross-representation precedent); **both BM25 and dense** cells
  mandatory (BEIR); per-arm retrieval-recall@k vs gold provenance reported **separately** from
  end-task accuracy (FiD); fixed pre-registered context ordering + a **position-shuffle** cell
  (Lost-in-the-Middle); a **random-document** cell (Power-of-Noise); **popularity/long-tail-stratified**
  readout (Mallen); implementation from a **pinned standard harness** (FlashRAG, 16/38, v2 pin);
  **identical index-bytes + build-cost + query-cost ledger on both arms** (Q3).
- *Still to design from scratch, no published precedent (the largest open item):* (1) equivalent
  source-content derivation + an **information-parity criterion** across kernel records vs passages vs
  triples vs tool schemas (they index *different objects*); (2) identical-vs-architecture-specific
  retriever policy, decided and justified per cell; (3) retrieved-token/context budget + ordering
  parity; (4) generator / tool-executor / retry-policy / **tuning-compute** parity (§2.3 binds on
  total tuning compute, not config count); (5) construction-leakage + authoring-effort accounting,
  under the §2.2(1) decontamination hard gate. **"Same source snapshot" is not yet "matched
  control" — P3-D-RAGC is the closest of the three beads to closed but is NOT closed by this review.**

**P3-D-FRONTIER — the frontier-builder.** *Supplied (verified):* the ICLR-2025 citation confirmed at
source with its envelope (>4× vs best-of-N and 14×-larger parity are *separate, conditional* findings
on PaLM-2/MATH with fine-tuned revisers+PRMs — not our band, not one exchange rate); large-budget
verifier decay must be reported (Scaling-Flaws, tested-verifier scope); the verifier-recipe direction
(Cobbe outcome + Math-Shepherd auto-PRM, no human-label budget); the ≤2B tool-use recipe direction
(APIGen breadth / TinyAgent whose DeBERTa selector goes on the ledger). *Still open — "implement
Snell-style" is not yet a recipe:* budgeted difficulty estimator (compute charged); eligible search
policies per budget rung; verifier training/build costs on the ledger; base-success≈0 fallback;
non-math calibration gate before the >4× figure transfers to our 135M–1.7B index suite.

**P3-D-GNN (co-input, retrieval side only).** *Supplied:* vanilla RAG frequently beats GraphRAG on
flat tasks (GraphRAG-Bench) — the text-serialisation control is a **live threat**, not a formality;
no published size×depth sweep exists, so §3.2's sweep is novel and must be powered as such; charge
graph construction to the ledger explicitly. **This review does NOT de-risk the GNN bet:** every
graph source here is retrieval/indexing, **no GNN-to-LM-fusion paper is in this ledger**;
"structure wins past a hops/aggregation threshold" and "helps more as the generator shrinks" are
*hypotheses* (MiniRAG's causal reading is the authors' interpretation) — the empirical premise stays
with P3-LR-FUSE and the design bead must carry an explicit "no prior" statement.

---

## 8. Citation-verification table (ref → reachable? → supports the draft's claim?)

All 28 ledger entries re-fetched at their primary/abstract source **2026-07-19**. "Supports" = the
source's abstract (or, where noted, the authors' project page) carries the draft's load-bearing
claim verbatim or near-verbatim.

| # | id / arXiv | Reachable | Supports draft claim | Note |
|---|---|---|---|---|
| 1 | snell-ttc 2408.03314 | yes | **yes** | >4× & 14× & difficulty-adaptive & base-success caveat all verbatim; title diverges (§9); PaLM-2/MATH is body-level [claimed] |
| 2 | wu 2408.00724 | yes | yes | Llemma-7B>34B on MATH; Pareto-optimal — verbatim |
| 3 | cobbe 2110.14168 | yes | yes (with the draft's own caveat) | verification scales>finetuning verbatim; "30×/6B" figure NOT in abstract — draft flag correct |
| 4 | lightman 2305.20050 | yes | yes | process>outcome; 78%; PRM800K=800k — verbatim |
| 5 | math-shepherd 2024.acl-long.510 | yes | yes | 77.9→84.1; 89.1/43.5 — verbatim |
| 6 | slm-strong-verifiers 2404.17140 | yes | yes | ≤13B need strong external verifier — verified |
| 7 | scaling-flaws 2502.00271 | yes | yes | underperforms repeated sampling; misrank/prune — verbatim |
| 8 | knnlm 1911.00172 | yes | yes | 2.9-point (≈18.65→15.79), no additional training — verbatim |
| 9 | retro 2112.04426 | yes | yes | 2T tokens; 25× fewer params vs GPT-3/Jurassic-1 — verbatim |
| 10 | atlas 2208.03299 | yes | yes | >42% 64-shot NQ; +3% vs 540B; 50× fewer params — verbatim |
| 11 | mallen 2212.10511 | yes | yes | 14k Q, long-tail, adaptive cuts cost — verbatim |
| 12 | massiveds 2407.12854 | yes | yes | 1.4T tokens; monotone; small+datastore>large LM-only — verbatim |
| 13 | selfrag 2310.11511 | yes | yes | 7B/13B beat ChatGPT & RA-Llama2-chat — verbatim |
| 14 | toolformer 2302.04761 | yes | yes | self-supervised API calls; competitive w/ larger — verbatim |
| 15 | apigen-xlam 2406.18518 | yes | yes | 60k; 3,673 APIs/21 cats; 1B>GPT-3.5+Haiku; 7B>GPT-4s — verbatim |
| 16 | tinyagent 2409.00608 | yes (numbers via BAIR blog) | yes, EXCEPT training-set size | 80.06/84.95/79.08 & 16 tools & DeBERTa-v3 confirmed at blog; **"40k" in draft ≠ 80K in source (§9)** |
| 17 | graphrag 2404.16130 | yes | yes | KG+community summaries; global sensemaking; ~1M — verbatim; **abstract omits indexing runtime (§9)** |
| 18 | hipporag 2405.14831 | yes | yes | 10–30× cheaper/6–13× faster; up to 20% — verbatim |
| 19 | rag-vs-graphrag 2502.11371 | yes | yes | neither dominates; combining helps — verbatim |
| 20 | when-graphs-rag 2506.05690 | yes | yes | "GraphRAG frequently underperforms vanilla RAG" — verbatim |
| 21 | lightrag 2410.05779 | yes | yes (qualitative only) | dual-level + incremental; **no cost numbers in abstract — draft UNVERIFIED flag correct** |
| 22 | minirag 2501.06713 | yes | yes | 25% storage (author-relative); heterogeneous graph — verbatim; causal reading is authors' [claimed] |
| 23 | kilt 2009.02252 | yes | yes | same Wikipedia snapshot + provenance scoring — verbatim |
| 24 | beir 2104.08663 | yes | yes | 18 datasets; BM25 robust; rerank best but costly — verbatim |
| 25 | fid 2007.01282 | yes | yes | accuracy scales with #passages; SOTA NQ/TriviaQA — verbatim |
| 26 | lost-middle 2307.03172 | yes | yes | best at edges, degrades mid-context — verbatim |
| 27 | power-of-noise 2401.14887 | yes | yes | random docs +35%; high-scoring-irrelevant hurt — verbatim |
| 28 | flashrag 2405.13576 | yes | yes | 16 methods + 38 datasets (current abstract) — matches v2 pin |

**Verification outcome: 28/28 reachable; 28/28 support their load-bearing claim.** Two claims carry a
draft-supplied UNVERIFIED flag that I independently **confirm correct** (Cobbe "30×", LightRAG cost
tables — both genuinely absent from the abstract). One divergence is a **factual error to fix** in
the draft + jsonl (TinyAgent training-set size). Two are minor/soft (Snell title suffix; GraphRAG
indexing-runtime is body-level, not in abstract).

---

## 9. Divergences from the Fable draft (report explicitly, per discipline)

1. **TinyAgent training-set size — factual error [correct in the deliverable].** Draft §1 and
   `RAG.sources.jsonl` say "**40k** curated use-cases". The authors (BAIR blog + project data) state
   "**80K** training data, 1K validation, 1K testing". This is the closest analogue in this review to
   the prior pass's Sardana dollar-figure catch: a clean numeric divergence, not a reading dispute.
   **Impact: none on any load-bearing conclusion** — TinyAgent stays domain-narrow (16 tools) with an
   off-ledger DeBERTa selector regardless of 40k vs 80K. Recommend the coordinator correct the number
   to 80K in both `RAG.md` and `RAG.sources.jsonl`.
2. **Snell title suffix — minor.** Draft §4 and jsonl append "**for Reasoning**" to the title; the
   canonical arXiv:2408.03314 title is "Scaling LLM Test-Time Compute Optimally can be More Effective
   than Scaling Model Parameters" (no suffix). Cosmetic; the id and all numbers are correct.
3. **GraphRAG indexing runtime — body-level, not abstract [soft caveat, not a divergence].** Draft
   §2/§3 says the paper "reports indexing runtime/wall time for its corpora." The **abstract** does
   not; this is a body-level claim I did not re-verify at the body this session — marked
   `[UNVERIFIED at body]`. Does not affect the conclusion (no complete lifecycle ledger exists), but
   the draft should not imply abstract-level support for it.
4. **Snell PaLM-2 / MATH substrate — body-level [not a divergence, a precision note].** The draft
   correctly names PaLM-2-class models on MATH; the abstract I fetched names neither. This is
   uncontested and well-known from the body, but for strict source-discipline it is `[claimed: body]`,
   not abstract-verified.

No divergence overturns the draft's decision-relevant conclusions. The draft's own UNVERIFIED flags
(Cobbe 30×; LightRAG cost tables; the "no systematic search" scope caveats) were **conservative and
accurate** — this pass upgrades none of them to "verified" and confirms all as genuinely absent from
the abstracts.

---

## 10. Open questions carried forward (honest gaps this review cannot close)

1. **No executable matched-control precedent exists for cross-representation comparisons** — the five
   P3-D-RAGC design rules (source-content derivation + information parity; identical-vs-architecture-
   specific retriever; retrieved-token/context budgets + ordering; generator/executor/retry/tuning-
   compute parity; construction leakage + authoring effort) must be designed and pre-registered by
   the bead itself. Largest open item; the literature supplies cells, not the control. [STIPULATED]
2. **No deployment-bytes-matched small-RAG-vs-dense frontier found** (targeted, not systematic sweep)
   — F(B_k) must be constructed, not cited; nearest recipes are Q1(i)–(iii). [EXTRAPOLATION]
3. **No flagship graph-RAG paper publishes a complete bytes/build-compute lifecycle ledger** —
   P3-D-RAGC's graph cell needs its own measured build ledger; budget to measure, don't cite.
4. **Graph-size×depth break-even is unmeasured, and GNN-to-LM fusion has no source in this ledger** —
   GraphRAG-Bench gives a difficulty gradient, not a size×depth sweep; P3-E-GNN-1's sweep is novel;
   P3-D-GNN's empirical premise stays open pending P3-LR-FUSE with an explicit "no prior" statement.
5. **Verifier head-to-head (sound symbolic vs trained PRM, matched budgets, coverage-stratified) has
   no precedent** — design from scratch in P3-D-FRONTIER/P3-E-VL-1; neither the learned verifier's
   large-budget decay (tested-verifier scope only) nor the symbolic system's end-to-end immunity is
   established.
6. **Adaptive test-time compute at ≤2B on non-math tasks is thin** — Snell = PaLM-2/MATH with
   fine-tuned revisers/PRMs; Wu = Llemma/MATH; transfer of the >4× figure to our 135M–1.7B index
   suite is an assumption until calibration measures it; "Snell-style" still needs the five design
   pieces in Q4. [EXTRAPOLATION]
7. **Power-of-Noise mechanism is unsettled** — treat the random-document cell as a control, not a
   tuning opportunity.

---

## Source count

- **Ledger:** 28 entries in `docs/next/lit/RAG.sources.jsonl`, **all 28 re-verified at primary/
  abstract source 2026-07-19** (this pass). Reachability 28/28; claim-support 28/28.
- **Divergences (§9):** 1 factual error to fix (TinyAgent 40k→80K); 1 cosmetic (Snell title suffix);
  2 body-level precision notes (GraphRAG indexing runtime; Snell PaLM-2/MATH substrate).
- **UNVERIFIED, confirmed genuinely absent from abstracts:** Cobbe "30×/6B" equivalence figure;
  LightRAG quantitative cost tables. Both correctly flagged by the draft.
- **Version-sensitive:** FlashRAG 16 methods / 38 datasets confirmed as the *current* abstract
  (v2 pin), not the v1 12/32.
- KB records consulted for recall only; none cited as evidence.
</content>
</invoke>
