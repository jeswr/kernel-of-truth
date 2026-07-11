# P3-LR-RAG — RAG, structured retrieval, knowledge graphs, tool-using neural baselines

- **Bead:** kernel-of-truth-s55r.4 (Phase-0 [LIT], Programme-3 revision 2, §5 table row P3-LR-RAG).
- **Author:** Fable (chief architect), 2026-07-11. Branch `opus/f2b-replicate-rightsize`.
- **Deliverable pair:** this review + `docs/next/lit/RAG.sources.jsonl` (one JSON per source).
- **Purpose (decision-oriented):** de-risk the **matched generic-RAG/tool-use control** that the
  GPT-5.6 review (`poc/gpt56-review/p3-review-20260711/review.md`, "Baselines need strengthening")
  names the single strongest missing baseline, and answer the six scoped questions so the Phase-1
  design beads P3-D-RAGC, P3-D-FRONTIER, and P3-D-GNN(co) open with the literature input assembled
  and their **remaining open design questions stated explicitly**. This review supplies ingredients
  and constraints; it does **not** close those designs (§7–§8 state what stays open).
- **Epistemic discipline:** every empirical claim below carries a primary citation
  (venue + year + URL fetched 2026-07-11); anything I could not verify at source is marked
  **UNVERIFIED**. Load-bearing lines carry [MEASURED | STIPULATED | EXTRAPOLATION]. In this
  document MEASURED = a published number restated strictly from a source I fetched, inside that
  paper's own envelope (it is the *authors'* measurement, not ours); EXTRAPOLATION = a
  cross-paper reading, direction-only, never a premise for a verdict; STIPULATED = a scoping or
  design decision made here.
- **Governance:** writes only this file + the sources JSONL; no KB ingest/embed, no registry or
  assumption mutation, no bd/git operations, no child agents.

---

## 0. Dedup — what already exists (surveyed first, built on, not duplicated)

- **Lit-KB (`kb/records/`, 552 records):** a scan over `biblio.title` + `architecture.mechanism_tags` +
  `architecture.summary` finds **~180 RAG/retrieval/verifier/tool-use-adjacent records**, including the
  canonical retrieval-LM lineage already extracted in structured form (kNN-LM `arxiv_1911.00172`,
  REALM `arxiv_2002.08909`, RETRO `arxiv_2112.04426`, Atlas `arxiv_2208.03299`, InstructRetro
  `arxiv_2310.07713`, Memorizing Transformers `arxiv_2203.08913`), KG/graph-RAG entries (KG-RAG
  `arxiv_2405.12035`, graph-RAG survey `arxiv_2501.13958`, KBLaM `arxiv_2410.10450`, AtlasKV
  `arxiv_2510.17934`), a deep PRM/verifier cluster (Math-Shepherd `doi_10.18653_v1_2024.acl-long.510`,
  GenPRM `arxiv_2504.00891`, scaling-flaws `arxiv_2502.00271`, Small-LMs-need-strong-verifiers
  `doi_10.18653_v1_2024.findings-acl.924`), tool-use entries (PAL `arxiv_2211.10435`, Chameleon
  `arxiv_2304.09842`), and Mallen et al. `arxiv_2212.10511`. Per the KB honesty boundary
  (`docs/next/literature-kb.md` §0) those records are **recall infrastructure, not evidence** — every
  load-bearing claim below was re-verified at its primary venue today, and this report is the
  promotion vehicle. [STIPULATED: dedup protocol]
- **Prior lit reports (`reports/lit-*.md`, 5):** none covers RAG/retrieval as a subject.
  `lit-llm-injection-priorart.md` covers injection channels (KV/adapters — P3-LR-RULE extends it);
  `lit-structured-parsing-and-inner-symbolic.md` touches constrained decoding and entity retrieval
  only tangentially. **This is the first dedicated retrieval/RAG/tool-use review in the repo.**
- **Internal evidence base this review must stay consistent with:** `docs/next/feasibility-synthesis.md`
  — in particular that a5-llm's PASS explicitly "does not license" any kernel-vs-RAG conclusion
  because it had **no conventional-substrate arm** ("nothing distinguishes the kot-axiom kernel from
  ANY typed store + checker"), and that f2b-replicate's +0.1507 already beat a *trained PRM*
  (Skywork-PRM-1.5B 0.5267) but never a matched generic-RAG arm. The whole point of P3-D-RAGC is to
  close exactly that gap. [MEASURED: feasibility-synthesis §1–2, repo-internal]

---

## 1. Strongest small-model (100M–2B) RAG and tool-use recipes — and what they achieve under MATCHED accounting

**State of the art, retrieval side.** The published wins that matter at or near our band:

- **kNN-LM** (ICLR 2020, https://arxiv.org/abs/1911.00172): interpolating a Wikitext-103 LM with a
  nearest-neighbour datastore over its own training set cuts perplexity 18.65 → **15.79 with no
  additional training** [MEASURED]. The win is bought with a token-level datastore + ANN search at
  every step — parameter count is flat but deployment bytes and query-time cost balloon (the paper
  does not charge for either).
- **RETRO** (arXiv 2021, ICML 2022, https://arxiv.org/abs/2112.04426): comparable performance to
  GPT-3/Jurassic-1 on the Pile "despite using 25× fewer parameters" — conditioned on a **2-trillion-token
  retrieval database** [MEASURED]. The 25× headline is a *parameter* claim, not a deployment-bytes
  claim; a bytes-inclusive comparison has **not been performed** (by the authors or anyone found in
  this sweep) — it plausibly reverses, but that is a calculation the P3-D-RAGC ledger must actually
  run, not a published result [EXTRAPOLATION, unperformed calculation].
- **Atlas** (JMLR 24(251), 2023, https://arxiv.org/abs/2208.03299, https://www.jmlr.org/papers/v24/23-0037.html):
  64-shot NQ >42%, beating a 540B-parameter model by 3% with "50× fewer parameters" [MEASURED] —
  again excluding the retrieval index (full Wikipedia + CC corpus) from the size claim.
- **When retrieval actually pays:** Mallen et al. (ACL 2023, https://arxiv.org/abs/2212.10511) show on
  PopQA (14k questions, 10 models) that "retrieval-augmented LMs largely outperform orders of
  magnitude larger LMs" **specifically on long-tail entities**, that scaling parameters "fails to
  appreciably improve memorization of factual knowledge in the long tail", and that *adaptive*
  retrieval (retrieve only when needed, popularity-thresholded) improves accuracy while cutting
  inference cost [MEASURED].
- **Datastore scaling is a real axis:** MassiveDS (NeurIPS 2024,
  https://proceedings.neurips.cc/paper_files/paper/2024/hash/a5d8aba27dfef4e849e8cb03fb87a954-Abstract-Conference.html,
  https://arxiv.org/abs/2407.12854): a 1.4T-token open datastore; datastore size improves LM and
  downstream performance monotonically without obvious saturation, and **"a smaller model augmented
  with a large datastore outperforms a larger LM-only model on knowledge-intensive tasks"**, with
  compute-optimal curves showing larger datastores dominate at fixed *training* compute [MEASURED].
- **Self-RAG** (arXiv 2023, ICLR 2024, https://arxiv.org/abs/2310.11511): 7B/13B LMs trained with
  reflection tokens (learned when-to-retrieve + self-critique) outperform ChatGPT and
  retrieval-augmented Llama2-chat on open-domain QA/fact-verification [MEASURED]. 7B is above our
  band but the *recipe* (learned adaptive retrieval + critique) is budget-portable.

**Tool-use side, at ≤2B genuinely:**

- **xLAM-1B / APIGen** (arXiv 2024, https://arxiv.org/abs/2406.18518): a 1B model trained on 60k
  execution-verified synthetic function-calling examples "surpass[es] GPT-3.5-Turbo and Claude-3
  Haiku" on the Berkeley Function-Calling Benchmark (the 7B sibling beats several GPT-4 variants)
  [MEASURED]. The lever is **verified synthetic data quality** (format check → actual execution →
  semantic check), not architecture. Scope note: function-calling-specific, but broad within that —
  the dataset spans **3,673 executable APIs across 21 categories** [MEASURED], so it is not
  narrow-curated in the TinyAgent sense.
- **TinyAgent-1.1B** (EMNLP 2024 demo, https://aclanthology.org/2024.emnlp-demo.9/,
  https://arxiv.org/abs/2409.00608): fine-tuned on 40k curated use-cases + a tool-retrieval step
  ("ToolRAG") + quantisation, reports 80.06% success vs GPT-4-Turbo's 79.08% **on its own curated
  task suite** — a **16-tool, task-specific Mac-assistant benchmark** [MEASURED; numbers from the
  project's paper/README — domain-narrow by construction]. Ledger note: ToolRAG uses a **separately
  fine-tuned DeBERTa tool selector**; its weights, training and inference compute are part of the
  system and must appear in any matched-resource ledger — the headline is accurate but not
  resource-matched.
- **Toolformer** (NeurIPS 2023, https://arxiv.org/abs/2302.04761): self-supervised API-call insertion
  (calculator/QA/search/translation/calendar) yields zero-shot performance "often competitive with
  much larger models" at 6.7B [MEASURED; above band, canonical recipe].

**The decision-relevant synthesis** [EXTRAPOLATION, direction-only]: at 100M–2B, **this 28-source
sweep found no published win over larger dense models under a deployment-bytes-inclusive,
matched-total-resource ledger**. Caveat on scope: this was a targeted sweep, not a documented
systematic search — read it as "none found here", not "none exists". Every "small beats large"
retrieval result in the sweep charges parameters but not the index (kNN-LM, RETRO, Atlas, MassiveDS
all follow this accounting); the ≤2B tool-use wins are domain-restricted, though not uniformly so —
TinyAgent is task-specific by construction (16 tools, one assistant domain, plus a separately
trained tool selector off-ledger), while xLAM/APIGen is function-calling-specific but spans 3,673
APIs across 21 categories. This is *good news for the fairness case*: the
matched-RAG control we must build is genuinely stronger accounting than the field's own norm, and
the frontier F(B_k) at small budgets is likely to be **dense-model + adaptive test-time compute +
modest local index**, not a trillion-token-datastore configuration (which busts any deployment-bytes
budget we would set). It also means the G4 comparator recipes to implement are: (i) verified-synthetic-data
fine-tune for tool use, (ii) adaptive/popularity-thresholded retrieval, (iii) datastore scaled *to
the same byte budget as the kernel store*.

---

## 2. Structured/KG retrieval vs dense retrieval — when each wins, and graph-size/depth dependence

- **GraphRAG** (arXiv 2024, https://arxiv.org/abs/2404.16130): LLM-built entity graph + pregenerated
  community summaries; wins over conventional RAG on **global sensemaking/query-focused summarisation**
  ("main themes of the corpus" questions, ~1M-token corpora) on comprehensiveness/diversity —
  *not* on local factoid QA; the index is built by LLM passes over the whole corpus. The paper
  does report construction/runtime information (including indexing wall time for its corpora) —
  what it lacks is a **complete bytes/build-compute lifecycle ledger** of the kind KOT-SIZE/2
  requires (see §3) [MEASURED].
- **HippoRAG** (NeurIPS 2024, https://arxiv.org/abs/2405.14831): KG + Personalized PageRank;
  **single-step** retrieval matches or beats iterative retrieval (IRCoT) on multi-hop QA while being
  "10–30× cheaper and 6–13× faster" online, and beats SOTA by up to 20% on multi-hop benchmarks
  [MEASURED]. The graph is still LLM-extracted offline (openIE passes — an indexing cost dense
  retrieval does not pay).
- **RAG vs. GraphRAG: A Systematic Evaluation** (arXiv 2025, https://arxiv.org/abs/2502.11371):
  under a unified protocol (same data preprocessing, retrieval config, generation settings),
  **neither paradigm uniformly dominates** — the two have distinct strengths by task, and combining
  them beats either [MEASURED].
- **When to use Graphs in RAG / GraphRAG-Bench** (arXiv 2025, https://arxiv.org/abs/2506.05690):
  "**GraphRAG frequently underperforms vanilla RAG on many real-world tasks**"; the paper builds a
  difficulty-graded benchmark (fact retrieval → complex reasoning → contextual summarisation →
  creative generation) with stage-wise evaluation from graph construction through retrieval to
  generation, to locate where structure pays [MEASURED].
- **MiniRAG** (arXiv 2025, https://arxiv.org/abs/2501.06713): the one *small-model-specific* graph
  result — a heterogeneous graph index (chunks + named entities) + topology-enhanced retrieval lets
  **SLMs reach performance comparable to LLM-based RAG with 25% of the storage** [MEASURED —
  author-reported *relative* comparison against their own LLM-RAG baseline, not evidence that the
  complete system fits 25% of an honestly-packed deployment budget]. The mechanism reading — graph
  structure "substitutes for" the semantic embedding quality small models lack — is the **authors'
  causal interpretation**, stronger than their reported system comparison supports. Directly
  relevant even so: structure compensating for weak dense semantics is the same bet H-GNN makes —
  as a *hypothesis to test*, not a result to build on.
- **LightRAG** (arXiv 2024, https://arxiv.org/abs/2410.05779): dual-level (entity/relation +
  vector) retrieval with incremental index updates; claims accuracy+efficiency improvements over
  graph-heavy predecessors [MEASURED, qualitative — its cost tables were not in the abstract I
  verified; specific token-cost numbers UNVERIFIED].

**When each wins** [EXTRAPOLATION, direction-only]: dense top-k wins **single-hop, local,
paraphrase-tolerant factoid** lookups (cheap index, no construction LLM passes, robust); graph
retrieval wins where the query needs **multi-hop composition or whole-corpus aggregation** — i.e.
where the answer is a *path or a summary over structure*, not a passage (HippoRAG multi-hop,
GraphRAG global). **Hypothesis, not established:** that the break-even moves in structure's favour
as (a) hops/aggregation depth grows, (b) the generator gets smaller (MiniRAG's causal reading —
authors' interpretation, §above), and (c) corpus knowledge is relational rather than descriptive.
None of these sources measures a hops/aggregation *threshold*, shows gains monotone in depth, or
shows a GNN encoder becoming preferable — HippoRAG shows a graph *retriever* can beat iterative
retrieval on selected multi-hop QA, no more. **Graph-size/depth dependence is thinly measured** —
GraphRAG-Bench's difficulty gradient is the best current instrument and there is no clean published
size×depth sweep of the kind §3.2 pre-registers; that sweep is genuinely novel territory for
P3-E-GNN-1. For P3-D-GNN(co), a hard scope limit: **every graph source in this ledger concerns
graph-based retrieval/indexing (GraphRAG, PageRank retrieval, global summarisation) — none studies
GNN-to-LM fusion vs text serialisation, and no GNN-fusion paper is in this ledger.** The
GNN-vs-text-serialisation question is therefore *not* de-risked here: it stays open pending
P3-LR-FUSE, and P3-D-GNN should carry an explicit "no prior" statement for its empirical premise.
The depth-threshold framing above is a design *hypothesis* the sweep should straddle — not a prior
it can assume.

---

## 3. Honest index accounting — size, build cost, query cost

What the strongest papers actually charge for, and don't [EXTRAPOLATION over §1–2 sources]:

| Cost axis | Field practice | Honest instances |
|---|---|---|
| Index bytes | Almost never counted against the "fewer parameters" headline | RETRO states 2T tokens; MassiveDS states 1.4T tokens + releases the pipeline; kNN-LM's datastore is same-order as training set; MiniRAG reports storage (25% — author-reported, relative to its own LLM-RAG baseline) |
| Build/construction | Rarely priced in full; GraphRAG-class methods add whole-corpus LLM passes (entity extraction + community summaries) — the flagship paper reports indexing runtime/wall time for its corpora but **no complete bytes/build-compute lifecycle ledger** | HippoRAG prices *online* retrieval (10–30× cheaper than IRCoT) but not offline graph build; GraphRAG-Bench evaluates the construction stage explicitly |
| Query-time | Sometimes latency, rarely energy; kNN-LM pays ANN search per token (uncharged); rerankers/late-interaction win BEIR zero-shot **at heavy compute cost** (stated qualitatively) | BEIR (NeurIPS 2021 D&B, https://arxiv.org/abs/2104.08663) is unusually explicit that its best zero-shot systems are the computationally expensive ones [MEASURED] |
| Comparability | Implementation variance so bad a toolkit exists to fix it | FlashRAG (arXiv 2405.13576; counts pinned to the **v2 abstract, revised 2025-02-24**): 16 reproduced methods + 38 standardised datasets (the 2024 v1 abstract reported 12 methods + 32 datasets — pin the release actually used when P3-D-RAGC adopts it), motivated by "absence of a standardized framework" making comparisons unreliable [MEASURED, v2 abstract re-fetched 2026-07-11] |

**Decision take** [STIPULATED]: KOT-SIZE/2's six-figure recipe (canonical packed bytes, compressed
distribution, warm RSS, cold working set, **index/store construction size and cost**, remote deps)
is stricter than the accounting practised in **any of the 28 papers reviewed here** — a reading of
this sweep, not a systematic-search result. Whether *any* published small-model RAG win would
survive figure 5 as a "smaller system" claim is an **open calculation**: settling it would require
a systematic search plus actual byte/build/query arithmetic per system, which neither this review
nor anyone else has performed. P3-D-RAGC must therefore (a) charge the generic-RAG arm and
the kernel arm identical ledgers (index bytes + build compute + query compute), and (b) pin the
retriever/index implementation from a standard harness (FlashRAG-style) so the control is not
weakened by our own implementation variance. The lifecycle ledger (KOT-LIFE/1) should book graph
construction LLM passes exactly like store authoring — the literature's silent asymmetry
(dense index ≈ free embed pass; graph index ≈ full LLM sweep) becomes an explicit line item.

---

## 4. The ICLR-2025 adaptive test-time-compute result — VERIFIED, with envelope

The review's citation resolves to **Snell, Lee, Xu & Kumar, "Scaling LLM Test-Time Compute Optimally
Can be More Effective than Scaling Model Parameters for Reasoning", ICLR 2025 (oral)**
(https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b623663fd9b874366f3ce019fdfdd44-Abstract-Conference.html,
fetched; also https://iclr.cc/virtual/2025/oral/31924). Its claims, restated inside their envelope:

- **Compute-optimal (difficulty-adaptive) test-time scaling improves efficiency by >4× versus a
  best-of-N baseline** — the strategy (best-of-N vs beam vs lookahead search against a PRM; vs
  adaptive revision of the response distribution) must be *selected per prompt difficulty*
  [MEASURED].
- **In a FLOPs-matched evaluation, test-time compute lets a smaller base model outperform a 14×
  larger model — on problems where the smaller base model has a non-trivial success rate**
  [MEASURED]. On the hardest prompts (base success ≈ 0), extra inference compute does not rescue
  the small model; pretraining scale still wins there. The exchange rate also depends on the
  assumed inference-to-pretraining token ratio.

Envelope constraints the headlines omit (all load-bearing for transfer to our setting):

- The experiments used **PaLM-2-class models on MATH, with fine-tuned revision models and PRMs** —
  not 135M–1.7B general-purpose models; nothing here is measured in our band or off math.
- **Prompt-difficulty estimation itself consumes non-trivial test-time compute**; a faithful
  implementation must budget the estimator, not treat difficulty as free oracle input.
- The **>4× and 14× findings are separate comparisons** (strategy-selection efficiency vs a
  FLOPs-matched model-size comparison) — they do not compose into a general "4× compute buys one
  model class" exchange rate.
- The authors **explicitly leave generalisation beyond math / easily-verified domains unresolved**.
- The 14× result is **conditional on prompt difficulty and on the assumed lifetime
  inference-to-pretraining token ratio**.

Corroborating and bounding results:

- **Inference Scaling Laws** (arXiv 2024, https://arxiv.org/abs/2408.00724): Llemma-7B + tree
  search consistently beats Llemma-34B on MATH at equal compute; "smaller models combined with
  advanced inference algorithms offer Pareto-optimal trade-offs" [MEASURED].
- **Scaling Flaws of Verifier-Guided Search** (arXiv 2025, https://arxiv.org/abs/2502.00271): as
  sample budget grows, verifier-guided search first beats then **underperforms plain repeated
  sampling**, across models (Mistral-7B, DeepSeekMath-7B), benchmarks (GSM8K/MATH) and verifier
  types — mechanism: **imperfect verifiers misrank and erroneously prune all valid paths**, worst
  on hard/OOD problems [MEASURED]. Scope: this is evidence for the **particular learned
  verifiers and search procedures tested** — it does not establish that every learned-verifier
  frontier must degrade at large budgets.

**What adaptive test-time compute actually buys** [EXTRAPOLATION, direction-only]: two *separate*
results, not one exchange rate — (a) >4× efficiency over a best-of-N baseline from
difficulty-adaptive strategy selection, and (b) in a different FLOPs-matched comparison, parity
with a 14× larger model **on the mid-difficulty band** — with two hard edges: no rescue where base
success ≈ 0, and (for the verifiers/search procedures tested in Scaling Flaws) decay at large
budgets. The review is right: best-of-k self-consistency is too weak to serve as F(B_k)'s
test-time-compute representative. But **"implement Snell-style" is not yet an executable baseline
recipe**: P3-D-FRONTIER still has to design a *budgeted* difficulty estimator (its compute charged
to the arm), the eligible search policies per budget rung, verifier training/build costs on the
ledger, a fallback policy where estimated base success ≈ 0, and a **non-math calibration gate**
before the >4× figure can be assumed to transfer (§7, §8). It must also report the large-budget
regime honestly — where the tested learned-verifier baselines degrade, an effect our symbolic
verifier is *claimed* to avoid on its covered slice. That immunity is a claim P3-E-VL-1 must
measure end-to-end, not assume: the scaling-flaws result neither generalises to all learned
verifiers nor establishes that a symbolic-verifier system is immune as a system.

---

## 5. Learned neural verifiers as baseline components (vs our symbolic verifier)

- **Cobbe et al., "Training Verifiers to Solve Math Word Problems"** (arXiv 2021,
  https://arxiv.org/abs/2110.14168): trained outcome verifiers + sample-and-rank "significantly
  improves performance on GSM8K" and **verification scales more effectively with data than
  finetuning** [MEASURED]. (The folk-cited "6B + verifier ≈ 30× larger finetuned model" figure is
  in the paper body, not the abstract I verified — UNVERIFIED here.)
- **Lightman et al., "Let's Verify Step by Step"** (ICLR 2024,
  https://proceedings.iclr.cc/paper_files/paper/2024/hash/aca97732e30bcf1303bc22ac3924fd16-Abstract-Conference.html):
  **process supervision > outcome supervision**; PRM-guided best-of-N solves 78% of a MATH test
  subset; cost side: **PRM800K = 800k step-level human labels** [MEASURED].
- **Math-Shepherd** (ACL 2024, https://aclanthology.org/2024.acl-long.510/): automatic
  (completion-rollout) process labels remove the human-annotation bottleneck; Mistral-7B 77.9→84.1
  GSM8K via step-PPO, 89.1 GSM8K / 43.5 MATH with verification [MEASURED].
- **Small LMs Need Strong Verifiers to Self-Correct Reasoning** (ACL Findings 2024,
  https://arxiv.org/abs/2404.17140): ≤13B models cannot reliably self-correct; gains require a
  strong external verifier — weak self-verification is the binding constraint [MEASURED].
- **Scaling Flaws** (§4 above): learned-verifier precision is what failed at scale **for the
  verifiers/search procedures tested** [MEASURED; not established as universal].

**Decision take** [STIPULATED]: F(B_k)'s verifier-baseline recipe is now clear — (i) an outcome
verifier (Cobbe-style) and (ii) a PRM trained with automatic process labels (Math-Shepherd-style;
no human-label budget needed), sized to fit the byte/compute budget, used both as best-of-N ranker
and as search guide; f2b-replicate's Skywork-PRM-1.5B arm was already the right *shape* and the
kernel arm beat it (0.5267 vs kernel arm, formal slice, alignment-confounded — feasibility-synthesis
§2). For the verifier/search combinations tested, the literature locates the learned verifier's
weakness at **precision under distribution shift and large sample budgets** (not shown universal —
§4) — the symbolic verifier's claimed differentiators (sound accept/reject on covered items,
fail-closed off-coverage, µs cost) attack exactly that weakness, but only *inside coverage*, and
end-to-end immunity of the symbolic *system* is itself unmeasured; the honest comparison is
therefore a **coverage-stratified verifier head-to-head**: on covered items (symbolic should dominate on precision at trivial cost)
and end-to-end (where the learned verifier's breadth can win despite noise). No published work runs
a sound symbolic verifier against a trained PRM under matched budgets — P3-E-VL-1's comparator set
would be, to my knowledge after this sweep, the first [EXTRAPOLATION].

---

## 6. Lessons on attributing a RAG "win" — separating retrieval from generation, corpus/index parity

The methodological toolkit the field converged on, and the traps it documents:

1. **Source-snapshot parity via a pinned shared snapshot.** KILT (NAACL 2021,
   https://arxiv.org/abs/2009.02252) grounds all tasks in the *same Wikipedia snapshot* and scores
   **provenance jointly with answers** [MEASURED] — the precedent for pinning the source snapshot
   and for scoring *which record was used*, not just the answer. Precedent scope, stated honestly:
   KILT does **not** mandate identical retrievers across systems, and it is **no precedent for the
   cross-representation control P3-D-RAGC needs**. "Same source snapshot" is not "same corpus, same
   retriever/index": converting the same source material into kernel records vs plain-text passages
   vs triples vs tool schemas changes the *indexed objects* and the retrieval problem itself, and
   the equivalence rules for that conversion have no published precedent (§ closing paragraph).
2. **Always include the lexical baseline.** BEIR (NeurIPS 2021 D&B,
   https://arxiv.org/abs/2104.08663): **BM25 is a robust zero-shot baseline** that dense retrievers
   frequently fail to beat out-of-domain; expensive rerankers win. A "structured store beats dense
   RAG" claim that never ran BM25 is unattributed [MEASURED].
3. **Retrieval quality and generation quality move independently.** FiD (arXiv 2020, EACL 2021,
   https://arxiv.org/abs/2007.01282): answer accuracy **scales with the number of retrieved passages
   aggregated by the generator** — generation-side evidence aggregation, not retrieval precision,
   drove SOTA [MEASURED]. Attribution requires reporting retrieval recall@k against gold provenance
   *separately* from end-task accuracy.
4. **Position confound.** Lost in the Middle (TACL 2023, https://arxiv.org/abs/2307.03172):
   accuracy depends strongly on *where* in the context the gold passage sits (best at edges,
   degraded mid-context) — context-order is a hidden variable in any RAG comparison [MEASURED].
5. **The random-document trap.** The Power of Noise (SIGIR 2024, https://arxiv.org/abs/2401.14887):
   high-scoring-but-irrelevant retrieved documents *hurt*, while **adding random documents improved
   accuracy by up to 35%** in their setting [MEASURED, their envelope; mechanism contested]. A
   measured "retrieval win" can be a prompt-perturbation effect — a random-document control arm is
   cheap and kills this reading.
6. **Gains concentrate in the long tail.** Mallen et al. (§1): retrieval's benefit is
   popularity-stratified; unstratified averages hide whether the store or the parametric memory
   answered [MEASURED].
7. **Implementation variance is a first-order confound.** FlashRAG (§3): the motivation for the
   toolkit is that un-standardised RAG comparisons were unreliable [MEASURED].

**What this supplies for P3-D-RAGC — and what it must still design** [STIPULATED]: the literature
supplies *necessary cells* for the control spec — same pinned **source snapshot** hash for kernel
store and RAG index (KILT pattern, scope-limited per (1)); both BM25 and dense retriever cells;
per-arm reporting of retrieval recall@k vs gold provenance separately from end-task accuracy (FiD
lesson); fixed, pre-registered context ordering + a position-shuffle cell (Lost-in-the-Middle); a
random-document cell (Power-of-Noise); popularity/long-tail stratified readout (Mallen);
implementation from a pinned standard harness (FlashRAG-style). These slot directly into the
§2.2(2) factorial as retrieval-architecture cells. **They are necessary, not sufficient: they do
not yet constitute an executable matched control.** P3-D-RAGC must still resolve, from scratch and
with no published precedent, at least these design rules:

1. **Equivalent source-content derivation + an information-parity criterion** — a rule for
   converting the same source snapshot into each arm's indexed objects (kernel records vs
   plain-text passages vs triples vs tool schemas) such that no arm receives more or better-curated
   information than another, and a way to *measure* that parity.
2. **Identical vs architecture-specific retrievers** — when forcing one shared retriever/index is
   the fair control and when it structurally handicaps an arm whose native retrieval operates over
   different objects; the spec must decide per cell and justify it.
3. **Retrieved-token/context budgets and ordering** — matched budgets for retrieved tokens and
   context length, and an ordering-parity rule, across arms.
4. **Generator, tool-executor, retry-policy, and tuning-compute parity** — same generator and
   decoding, same executor and retry semantics, matched tuning/adaptation compute per arm.
5. **Store/index-construction leakage and authoring effort** — construction passes (LLM sweeps,
   human authoring, selector training) booked identically on both arms, with leakage of evaluation
   knowledge into construction ruled out on both. On the six-way attribution
factorisation (§2.3): the literature separates *retrieval* from *generation* well, separates
*structured storage* from *retrieval* only recently (RAG-vs-GraphRAG unified protocol, GraphRAG-Bench
stage-wise evaluation), and has **no precedent for isolating "kernel semantics" from "typed store"**
— that cell (aligned-non-kernel store vs kernel store, same retriever) is our own instrument and
must carry the load alone.

---

## 7. Open questions for Phase-1 (honest gaps this review could not close from the literature)

1. **No executable matched-control precedent exists for cross-representation comparisons** — the
   five design rules in §6 (source-content derivation + information parity; identical vs
   architecture-specific retrievers; retrieved-token/context budgets + ordering; generator /
   tool-executor / retry-policy / tuning-compute parity; construction leakage + authoring effort)
   must be designed and pre-registered by P3-D-RAGC itself. The literature supplies cells, not the
   control. [STIPULATED: this is the largest open item, and the reason P3-D-RAGC is *not* closed
   by this review.]
2. **No deployment-bytes-matched small-RAG-vs-dense frontier was found in this sweep** (not a
   systematic search) — F(B_k) at our budgets must be constructed, not cited; the nearest recipes
   are §1(i)–(iii). [EXTRAPOLATION]
3. **No flagship graph-RAG paper publishes a complete bytes/build-compute lifecycle ledger**
   (GraphRAG reports indexing runtime for its corpora; HippoRAG prices online retrieval only) —
   P3-D-RAGC's graph cell needs its own measured build ledger; budget for measuring it, don't cite it.
4. **Graph-size×depth break-even is unmeasured, and GNN-to-LM fusion has no source in this ledger**
   — GraphRAG-Bench gives a difficulty gradient, not a size×depth sweep; the depth-threshold framing
   in §2 is hypothesis, not prior. P3-E-GNN-1's sweep is novel and should be powered as such;
   P3-D-GNN's empirical premise stays open pending P3-LR-FUSE and needs an explicit "no prior"
   statement.
5. **Verifier head-to-head (sound symbolic vs trained PRM, matched budgets, coverage-stratified)
   has no precedent** — design from scratch in P3-D-FRONTIER/P3-E-VL-1. Neither the learned
   verifier's large-budget decay (shown only for the tested verifiers/search procedures) nor the
   symbolic system's end-to-end immunity is established — both are measurements to make.
6. **Adaptive test-time compute at ≤2B on non-math tasks** is thin — Snell used PaLM-2-class models
   on MATH with fine-tuned revisers/PRMs; Wu is Llemma/MATH; the transfer of the >4× efficiency
   figure to our index suite at 135M–1.7B is an assumption until P3-E-CAL-adjacent calibration
   measures it. "Snell-style" is also not yet a recipe: budgeted difficulty estimator, per-rung
   search policies, verifier build costs, base-success≈0 fallback, and a non-math calibration gate
   all remain to be designed (§4, §8). [EXTRAPOLATION]
7. **Power-of-Noise mechanism** is unsettled in the literature — treat the random-document cell as
   a control, not as a tuning opportunity.

---

## 8. Phase-1 hand-off — design beads to bd-create (recommendation; creation is the coordinator's, not this bead's)

| Bead | One-line scope | What this review supplies — and what it leaves OPEN |
|---|---|---|
| **P3-D-RAGC** | Spec the matched generic-RAG/tool-use control: same pinned source snapshot, matched byte/compute budgets, factorial cells per §2.2(2)f — **the executable matched control itself is still to be designed** | **Supplies:** pinned-source-snapshot + provenance-scoring pattern (KILT — scope-limited: no same-retriever or cross-representation precedent, §6.1); BM25 + dense cells mandatory; retrieval-recall-vs-answer separation; position-shuffle, random-document, long-tail-stratified cells; pinned standard harness; identical index-bytes + build-cost + query-cost ledger on both arms (§3, §6). **OPEN — must be designed with no published precedent (§6 rules 1–5, §7.1):** equivalent source-content derivation + information-parity criterion (kernel records vs passages vs triples vs tool schemas index *different objects*); identical-vs-architecture-specific retriever policy; retrieved-token/context budgets + ordering parity; generator/tool-executor/retry-policy/tuning-compute parity; construction-leakage + authoring-effort accounting. **Not closed** — closest of the three, but "same source snapshot" is not yet "matched control". |
| **P3-D-FRONTIER** | The neural frontier-builder: per-budget strongest baselines — quantisation/pruning/distillation + retrieval per §1 recipes + **difficulty-adaptive test-time compute (Snell-style, NOT best-of-k)** + learned verifiers (outcome + auto-labelled PRM) | **Supplies:** ICLR-2025 citation verified with envelope (>4× vs best-of-N and 14×-larger-model parity are *separate, conditional* findings — PaLM-2/MATH/fine-tuned revisers+PRMs, not our band, not one exchange rate; §4); large-budget verifier decay must be reported (scaling-flaws — shown for the tested verifiers, not universal); verifier recipe *direction* (Cobbe outcome + Math-Shepherd auto-PRM, no human-label budget); ≤2B tool-use recipe direction (APIGen breadth / TinyAgent — whose DeBERTa selector goes on the ledger) (§1, §4, §5). **OPEN — "implement Snell-style" is not yet a baseline recipe:** budgeted difficulty estimator (compute charged); eligible search policies per budget rung; verifier training/build costs on the ledger; fallback where estimated base success ≈ 0; non-math calibration gate. |
| **P3-D-GNN (co-input)** | H-GNN designs + the size×depth sweep + six controls (P3-LR-FUSE leads; this review co-feeds the retrieval side) | **Supplies:** vanilla RAG frequently beats GraphRAG on flat tasks (GraphRAG-Bench) — the text-serialisation control is a *live threat*, not a formality; no published size×depth sweep exists, so the §3.2 sweep is novel; charge graph construction to the ledger explicitly (§2, §3). **OPEN — this review does NOT de-risk the GNN bet:** every graph source here is retrieval/indexing, **no GNN-to-LM-fusion paper is in this ledger**; "structure wins past a hops/aggregation threshold" and "helps more as the generator shrinks" are *hypotheses* (MiniRAG's causal reading is the authors' interpretation, §2) — the empirical premise stays with P3-LR-FUSE, and the design bead must carry an explicit "no prior" statement. |

---

## Source count

- **Ledger:** 28 entries in `RAG.sources.jsonl` — `verified: true` on 27; 1 entry (Cobbe) carries a
  `verified: false` flag on a specific folk-cited number ("30×"), whose abstract-level claims are
  otherwise verified. All fetched at primary venue 2026-07-11.
- **UNVERIFIED claims flagged inline:** Cobbe 30×-equivalence figure (§5); LightRAG quantitative
  cost tables (§2); venue attributions for Wu et al. 2408.00724, LightRAG, MiniRAG, When-to-use-Graphs,
  RAG-vs-GraphRAG beyond arXiv (claims verified at arXiv; no peer-reviewed venue confirmed today).
- **Version-sensitive counts:** FlashRAG method/dataset counts (16/38) are pinned to the arXiv v2
  abstract (revised 2025-02-24, re-fetched 2026-07-11); the 2024 v1 abstract reported 12/32 (§3).
- KB records consulted for recall only, per the honesty boundary; none cited as evidence.
