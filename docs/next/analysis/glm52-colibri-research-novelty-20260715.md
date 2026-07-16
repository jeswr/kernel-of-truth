# GLM-5.2 / colibri — structure + novelty review

> Scope: (A) understand the real model + colibri's MoE/expert machinery; (B) decide whether our
> **expert-profiling → causal characterisation → deterministic-replacement** work is novel, and
> whether a public Show-and-Tell is worth posting. Tags: **[established]** (primary source or
> reproduced/measured), **[claimed]** (asserted by a vendor/community post, not independently
> verified), **[speculative]** (our inference). Sources + dates inline. Uncommitted — coordinator commits.

---

## Part A — The model and the engine

### A1. The real model + lineage

- **[established]** The estate `mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp` is a community int4/int8-MTP
  requant of **`zai-org/GLM-5.2-FP8`** (Zhipu AI / Z.ai), an open-weight (MIT) MoE. Our own HF-header
  read is authoritative for structure: `num_hidden_layers=78`, `first_k_dense_replace=3`,
  `n_routed_experts=256`, `n_shared_experts=1`, `num_experts_per_tok=8`, `num_nextn_predict_layers=1`,
  `scoring_func=sigmoid`, `topk_method=noaux_tc`, `hidden_size=6144`.
  (Source: our `poc/glm52-probe/stage1-feasibility-manifest.md`, config.json read 2026-07-15.)
- **[claimed]** Total ≈ **744B** params, ≈ **39–40B active/token**, **256 experts, top-8 routed + 1 shared
  (9 active)**, **1M-token context**, **DeepSeek Sparse Attention (DSA)**. Multiple 2026 write-ups agree;
  vLLM recipes list "743B / 39B active". Total-param headline drifts 743–753B across secondary posts —
  treat 744B (Z.ai/colibri figure) as canonical, the rest as blog rounding.
  (Sources: recipes.vllm.ai/zai-org/GLM-5.2; lucaberton.com GLM-5.2 744B MoE, 2026; eigent.ai/blog/glm-5-2, 2026.)
- **[established]** Lineage is **DeepSeek-V3-style MoE on the GLM trunk**: fine-grained 256 routed experts +
  1 always-on **shared** expert, **auxiliary-loss-free sigmoid gating** (`noaux_tc` = DeepSeek-V3 aux-free
  balancing w/ node-limited routing), and **MTP** — the same recipe GLM-4.5 already used (loss-free sigmoid
  routing, MTP, deep-over-wide), plus DSA added in GLM-5.
  (Sources: GLM-4.5 tech report **arXiv:2508.06471**, Aug 2025; GLM-5 report **arXiv:2602.15763**, Feb 2026
  — abstract confirms DSA + async agent-RL but withholds layer/expert counts; DeepSeekMoE **arXiv:2401.06066**, Jan 2024.)

### A2. Does 19,456 check out? **[established] YES — reconciled to the primary config.**

- 78 hidden layers − `first_k_dense_replace=3` dense (layers 0–2) = **75 sparse MoE layers (3–77)** × 256 =
  **19,200 main** routed cells; + `num_nextn_predict_layers=1` **MTP head (layer 78)** × 256 = **256** →
  **19,456**, byte-identical to our committed trace's 76×256 addressable cells. No hidden "stored-but-
  unreachable" experts, no converter duplication. The MTP 256 are int8 / DRAFT≥1-only (excluded from the
  DRAFT=0 main atlas). colibri's stray "**21,504**" is a **doc error** (=84×256; not reproducible from any
  config field); colibri's own Brain page and issue #175 use 19,456. (Source: our stage-1 manifest, 2026-07-15.)

### A3. colibri's expert machinery + the Expert Atlas (issue #175, `c/tools/expert_atlas/`)

- **[established] EXPERT_BUDGET** (PR/issue #254, **MERGED**): miss-aware cap on distinct experts/layer across
  the batch-union — keeps cache hits + highest-aggregate-gate-weight misses, drops the rest (never loaded).
  Reported +75% decode tok/s at budget=4 (253 GB I/O saved) on a 24 GB host, but degrades MTP acceptance
  (38%→21%) — a pure systems lever, no functional/expert semantics. (colibri #254.)
- **[established] CACHE_ROUTE** (`docs/CACHE_ROUTE.md`): opt-in cache-aware routing (prefer pin∪LRU-resident
  experts within a top-M window; `ROUTE_J/M/P`) — colibri's in-engine equivalent of the mobile
  "cache-conditional experts" idea (see B4). Off by default. (colibri repo, 2026.)
- **[established] Expert Atlas (#175, harness merged in #218; unified w/ dashboard in #245).** This is the
  decisive prior-art object. It already:
  - builds a **routing-affinity** atlas over all 19,456 experts by diffing `.coli_usage`/`STATS` snapshots
    per topic category (10 categories × 3 prompts × 64 tokens), with **replication-gating** (leave-one-
    prompt-out) that removed 587 single-prompt flukes;
  - reports **29/30 = 96.7%** leave-one-prompt-out topic classification (chance 10%); **1,041/13,260 (7.9%)
    strong specialists** (spec≥0.5, replicated) — i.e. ~92% of experts are generalists; a **depth curve**
    (early layers ≈syntax/generalist ~0.07, mid/late topical ~0.19–0.27); named specialists
    `L52/E174→code_sql, L53/E15→law, L16/E119→german, L21/E37→code_python, L17/E0→json_format`;
  - was **reproduced bit-exactly on three independent machines/microarchitectures**, yielding the strong claim
    *"expert specialisation is a pure function of the weights."*
  - **Confounds they already flag and control** (and that our infra must match): `TOPP` prunes ~38% of distinct
    experts; speculative drafts pollute the histogram (need `MTP=0 DRAFT=0`); `.coli_usage` accumulates; and
    intra-run routing is autocorrelated (one prompt ≠ N independent draws).
  - **Ceiling:** category-aggregated **routing-affinity only** — no per-item/per-token trace, **no causal
    ablation, no functional signatures, no replacement.** (Source: colibri #175 thread + `tools/expert_atlas/`, opened 2026-07-14; comments through 2026-07-15.)

---

## Part B — Novelty verdict (per item; strongest cited counterexample each)

**B1. Expert specialization / interpretability in MoE LLMs — [established prior art exists].**
A mature, crowded field. Strongest counterexamples: **DeepSeekMoE, arXiv:2401.06066** (Jan 2024, "ultimate
expert specialization", the fine-grained+shared design GLM-5.2 inherits); **Mixtral, arXiv:2401.04088** (Jan
2024, experts specialize by **syntax/token-id, not domain**); **"Part-of-Speech Sensitivity of Routers",
arXiv:2412.16971** (Dec 2024); **"The Expert Strikes Back: Interpreting MoE at Expert Level",
arXiv:2604.02178** (2026). Our domain/format/operation routing atlas is **incremental** on this body — and, for
GLM-5.2 specifically, is **already done by colibri #175** (more thoroughly than our gate-failed Wave-A).

**B2. Deterministic / rule-based replacement of experts, with a causal (ablation) basis — SPLIT verdict.**
- "*Which experts are safe to drop/skip*, domain-specialised, with an importance/ablation basis" →
  **[established prior art exists]**: **"Not All Experts Are Equal", arXiv:2402.14800** (ACL 2024; heuristic
  expert pruning by reconstruction loss + dynamic skipping, incl. domain-specific), and **MoNE,
  arXiv:2507.00390** (replaces low-usage/stable experts with **lightweight *learned* "novices"**). Our drop
  arm (`glm-edrop`) is incremental on these; our differentiator (kernel-guided vs uniform mask) is separate.
- "*Replace an identified expert/cohort with a **hand-built deterministic module** (DFA/parser/exact-arithmetic/
  copy-pointer), gated by a deterministic trigger, validated by causal ablation + module-swap at matched
  quality*" → **[appears novel]**. Three targeted searches (incl. "hardcoded algorithm / training-free FFN
  substitute") surfaced **no** direct prior art. Nearest published cousin: **SymTorch, arXiv:2602.21307**
  (Feb 2026) — but it distils components into **symbolic-regression-*learned* closed-form formulas** on **MLP
  layers** (3/28 layers → +8.3% throughput, ppl 10.62→13.76), **not** hand-built algorithms and **not** MoE
  experts. So the specific combination *(routed-MoE-expert × deterministic algorithmic module × causal
  validation × fail-open gating)* is, to the best of a source-verified search, unclaimed.

**B3. Published expert analysis/atlas of GLM-5.2 specifically — [partial prior art].**
Exactly one exists and it is **colibri #175** — a **community**, routing-affinity, cross-validated atlas
(not peer-reviewed, no causal/functional layer). **No academic** GLM-5.2 expert atlas found, and **no causal
or deterministic-replacement study of this model.** (Source: colibri #175, 2026-07-14/15.)

**B4. Adjacent efficiency baselines our speed claims must beat — [established, strong].**
**Mixture of Cache-Conditional Experts, arXiv:2412.00099** (training-free cache-aware routing, ~2× on mobile —
colibri's own citation, mirrored by CACHE_ROUTE); **ExpertFlow, arXiv:2410.17954** (predictive expert caching);
**"Local Routing Consistency" for offloading, arXiv:2505.16056**; expert pruning/compression
(**2402.14800; MoNE 2507.00390; MC# 2510.10962; DiEP 2509.16105**); plus colibri's shipped **EXPERT_BUDGET /
CACHE_ROUTE**. All *keep* the expert (cache/offload/skip) or *drop* capability (prune); **none eliminate the
load via a deterministic substitute** — which is our distinct mechanism, but the systems bar is high and any
speed claim must be A/B'd against CACHE_ROUTE + EXPERT_BUDGET on the same box.

---

## Bottom line — is the contribution novel, and post a Show-and-Tell?

- **[established]** The **routing-affinity atlas (our Stage 2) is NOT novel.** colibri #175 has already built,
  replication-gated, and **bit-exactly cross-validated** a GLM-5.2 expert-specialisation atlas, and MoE
  expert-specialization interpretability is a mature field. Our current Wave-A is *weaker* than theirs (coverage
  gates **failed**: routing-mass 0.825<0.95, held-out Spearman 0.63<0.8) — posting it now would **duplicate**
  their merged work and under-deliver.
- **[speculative→defensible]** The **genuinely novel core is Stages 3–5: causal functional characterisation +
  hand-built deterministic replacement of specific experts at matched quality.** No source-verified prior art
  ties MoE-expert identification to deterministic algorithmic substitution with causal validation; SymTorch and
  MoNE are the nearest cousins and are distinct on all of {expert-vs-layer, learned-vs-deterministic}. This is
  worth a Show-and-Tell — **but only once we have Stage-3 causal ablation + a Stage-5 replacement arm showing a
  quality-neutral speed win A/B'd against CACHE_ROUTE/EXPERT_BUDGET.**
- **Recommendation: DO NOT post a Show-and-Tell yet.** Today we would either duplicate colibri (routing atlas)
  or present gate-failed work. **Frame the eventual post as complementary to colibri #175** (cite it, reuse its
  probe set / confound controls, contribute the causal+replacement layer it explicitly lacks), not competitive.
  Gate the post on: (1) Stage-3 causal evidence on ≥ the shortlist, and (2) one validated deterministic-
  replacement cohort with a positive lower-bound speed delta at matched quality.
