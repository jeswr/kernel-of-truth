# GLM52-NS — Kernel/engine integration with GLM-5.2 via colibri: north-star design + feasibility plan

> **Status: NORTH-STAR DESIGN + staged feasibility plan (Programme-3 family). Nothing
> here is frozen, pre-registered, scheduled, or run; no frozen record, verdict, encoder
> pin, or registered assumption is touched; no GPU/model run and no git action occurs in
> this pass. This document states NO feasibility conclusion on CORRECTNESS or
> EFFICIENCY — it maps integration seams, ranks them, and prices the cheapest honest
> probes.** Author: Fable, architecture-design role (designer-4), 2026-07-12.
>
> **Maintainer goal (verbatim scope):** once a comprehensive kernel + concept-computation
> engine exists, use it to (A) improve GLM-5.2's INTELLIGENCE, or (B) make GLM-5.2 run
> with much less INFERENCE-TIME COMPUTE. Reference implementation:
> `the colibri engine (open-source GLM-5.2 CPU runner)` — a single-file C engine running GLM-5.2 on ~25 GB
> consumer RAM with experts streamed from disk.
>
> **ASM block claimed: ASM-1970..1989** (companion file
> `docs/next/design/asm-glm52-1970-1989.json`, owner designer-4). Range verified free at
> emission: central register tail in `registry/assumptions.jsonl` is ASM-1967; repo-wide
> grep for `ASM-19[7-9][0-9]` empty. Central registration is the coordinator's action,
> with the commit; this pass writes the companion file only.
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = repository bytes or a pinned
> mechanical output read this tick; `[LIT-BACKED: ref]` = an external fact verified at
> source; `[LIT-BACKED(fetch)]` = an external fact obtained 2026-07-12 through a
> summarising web fetch of the named source — carries PARAPHRASE RISK and is re-verified
> mechanically at probe P0 before anything load-bearing rests on it; `[DERIVED]` =
> arithmetic over tagged premises; `[STIPULATED: ASM-id]` = a design choice made here;
> `[EXTRAPOLATION: ASM-id]` = a registered projection, never a premise;
> `[ASSESSMENT]` = this designer's judgment, one model's opinion, binding on nothing.
>
> **Inputs read this tick:** `the colibri engine (open-source GLM-5.2 CPU runner)` README + `c/glm.c` (via
> summarising fetch; file structure incl. `c/tools/` converter and `c/openai_server.py`
> confirmed present) and public GLM-5.2 architecture coverage; in-repo:
> `docs/next/design/DDC.md` (§§0–5), `docs/next/design/large-kernel-scale-track.md`
> (SCALE-1, in full), `docs/next/design/engine-inference-under-typing.md` (ENGINE-INF,
> in full), `docs/next/feasibility-synthesis-v6.md` (in full),
> `poc/rules-1/{twin_engine.py,certificate.py}` (headers + inventory).

---

## 0. Plain-language summary (maintainer-facing)

GLM-5.2 is a 744B-parameter mixture-of-experts model. Colibri runs it on a small
machine by keeping only the ~17B always-used ("dense") parameters in RAM and pulling
the other ~370 GB of "experts" off an SSD as each token needs them. **Reading experts
off disk is, by the author's own measurement, the bottleneck** — the machine spends
almost all its time waiting for the disk, and produces roughly 0.05–1 token per second
depending on hardware.

That bottleneck is the opportunity. If the kernel can tell the engine, from the
*concepts* in the input, **which experts the model is going to need** — before the
router asks for them, across the whole generation rather than one layer ahead — then
the engine can (i) keep the right experts in RAM (fewer disk reads per token, directly
more tokens per second), and eventually (ii) not load concept-irrelevant experts at all
(dimension-collapse on the expert axis: the same training-free "keep only what the
kernel accounts for" move DDC makes on dense weights, applied to whole experts). A
separate, smaller seam: colibri already accepts externally forced token spans
(grammar-constrained drafts) — the deterministic rules engine could inject its entailed
conclusions as drafts the big model merely verifies. And in the other direction (A),
colibri's OpenAI-compatible gateway is a natural place to bolt the engine on as a
grounding/verification layer over GLM-5.2's outputs — with the bonus that a locally
pinned, byte-replayable frontier host is the first *instrument-grade* large host the
programme has had.

What this document does NOT claim: that any of this works. The kernel today covers
fewer than 100 concepts at coverage 0.35; no efficiency experiment has ever validly
graded; and the strongest deflator here is built into colibri itself (its learning
cache already pins whatever was hot — the kernel must beat that, plus a plain
topic-clustering control, before any kernel-specific sentence is licensed). The plan
below is: a ~$20–50 measurement probe on one small EC2 instance first, an admission
gate on whether concept-conditioned routing structure even exists, and only then a
prototype.

---

## 1. The substrate: what colibri + GLM-5.2 actually are

### 1.1 Facts carried forward (task brief, verified this tick where possible)

All rows [LIT-BACKED(fetch): colibri README + `c/glm.c`, fetched 2026-07-12] unless
noted; every row is mechanically re-verified at P0 from the checkout and the model
`config.json` before anything is built on it [STIPULATED: ASM-1971].

| Fact | Value as fetched | Note |
|---|---|---|
| Model | GLM-5.2, 744B total params, MoE (DeepSeek-V3-style), weights MIT (Z.ai) | corroborated by public coverage [LIT-BACKED(fetch): vendor and third-party pages listed in ASM-1972] |
| Active per token | ~40B params; ~11 GB of *routed-expert* weight bytes change per token | |
| Resident dense | ~17B params ≈ 9.9 GB int4 in RAM (glm.c summary said ~8.7 GB; range 8.7–9.9 GB, resolve at P0) | |
| Routed experts | README states **21,504** routed experts ≈ 370 GB int4 on disk, ~19 MB each; README also states 75 MoE layers × 256 experts = **19,200** — the two do not reconcile exactly (Δ = 9×256). NOT load-bearing; exact counts read from `config.json` at P0 | discrepancy flagged honestly |
| Layers | 78 transformer layers; first 3 dense FFN, ~75 MoE; MTP head at layer-78 position | |
| Router | sigmoid scoring + per-expert bias, greedy top-k (k ≈ 6–8 — fetch sources disagree; config at P0), + shared expert(s), n_group=1; env overrides `TOPK=n`, `TOPP=p` (cumulative-weight expert gate), `g_norm_topk` | the routing seam is ALREADY parameterised from the environment |
| Expert cache | per-layer LRU (`ecache[layer]`, auto-sized from RAM) + **pinned hot set** (`pin[layer]`, bypasses LRU, loadable from a stats file `PIN=stats.txt`) + OS page cache as L2 + **learning cache**: `.coli_usage` records actual routing, AUTOPIN re-pins hottest experts on later runs | the pin interface is the zero-C-change integration point |
| Prefetch | `PILOT=1`: an I/O thread predicts layer L+1's experts from layer L's post-attention state — **71.6% predictable** — and prefetches; *measured neutral on saturated-disk systems*; `SPEC=1` cross-layer prefetch; `PIPE=1` async expert loads | one-layer horizon; neutrality on saturated disk is load-bearing for §2.2 |
| KV cache | MLA: 576 floats/token/layer (57× vs 32,768); persisted ~182 KB/token (~576×78×4 B) [DERIVED]; DSA sparse-attention indexer for long context | KV is RAM-cheap; NOT the measured bottleneck |
| Speculative decoding | native MTP head (must be int8; int4 → 0% acceptance); 39–59% acceptance ⇒ **2.2–2.8 tokens/forward**; lossless n-gram drafting; **grammar-forced drafts**: GBNF-constrained spans injected as pre-accepted drafts at ~1.0 acceptance, adaptive disable < 50% | an external-draft injection path EXISTS in production form |
| Performance | cold ~0.05–0.1 tok/s (12-core, ~1 GB/s NVMe); community 0.28–1.83 tok/s across hardware; bottleneck migrates RAM-capacity → disk-bandwidth → CPU-matmul as hardware grows | |
| Requirements | x86 AVX2 (+OpenMP), ≥16 GB RAM (25 GB recommended), ~370 GB **local** NVMe; converter streams FP8 shards 5 GB at a time (never needs the full 756 GB) | Graviton/ARM excluded by AVX2 |
| Surfaces | `coli chat`, `coli serve` (OpenAI-compatible `/v1/*`, 16 KV slots), `coli plan`/`doctor`/`iobench`; single C file ~2,400 lines + headers; **no plugin architecture** — customisation = editing `glm.c`, the converter, or `c/openai_server.py` | Apache-2.0; single-author project |

### 1.2 The one number that organises everything [DERIVED]

Cold decode reads ≈ L_moe × k × 19 MB ≈ 75 × 8 × 19 MB ≈ **11.4 GB/token** (README's
"~11 GB"). At effective read bandwidth B, disk-bound throughput is bounded by
`tok/s ≤ B / (miss_rate × 11.4 GB)` (misses = expert loads not served by pin/LRU/page
cache). Consequences, all arithmetic:

1. In the disk-bound regime, **throughput is inverse-linear in expert bytes actually
   read**. Halve the misses (better pinning) or halve the loads (fewer experts) →
   ~2× tok/s, until the CPU-matmul wall (~0.3–0.5 tok/s on mid hardware).
2. **Prefetch does not reduce bytes read; it only overlaps I/O with compute.** When
   I/O time ≫ compute time (11 GB vs seconds of matmul), overlap buys at most the
   compute fraction — colibri's own README reports PILOT *neutral* on saturated
   disks. So on small boxes the task brief's "raise prefetch recall" framing is the
   WRONG lever: the quality-safe lever is **what sits in RAM** (pin/cache selection)
   and the aggressive lever is **how many experts are loaded at all** (top-k/top-p
   reduction, expert-drop). Recall matters on balanced hardware (fast disk + strong
   CPU) where overlap has headroom. [DERIVED; ASM-1974]
3. MTP already amortises loads: k drafted tokens verified in one forward load the
   *union* of their expert sets once per layer — this is where 2.2–2.8 tok/forward
   comes from. Any external draft source (§2.3) inherits this amortisation.
4. RAM cache arithmetic: on a 32 GB box, cache ≈ 32 − ~10 (dense) − OS ≈ 15–18 GB ≈
   800–950 experts ≈ 4–5% of ~20k; on 64 GB ≈ 2,300–2,600 experts ≈ 12%. Whether a
   *concept-conditioned* 5% beats a *globally-hot* 5% is precisely the admission
   question (§3, G-B1). [DERIVED bands]

### 1.3 What the programme brings (state as of synthesis v6, restated inside its envelope)

- **Engine:** RULES-1 deterministic forward chainer, certified 858/858 vs third-party
  CLUTRR gold, entailed cells irreproducible from stated bytes, twin/SPARQ agreement
  1,207/1,207, closes 958 worlds in <2 s on 2 CPU cores [MEASURED-CERTIFICATE:
  synthesis v6 §2.1; `poc/rules-1/`]. Closed rule inventory; kinship + (designed,
  not yet run) sense-typing scope.
- **Kernel:** <100 thesis-relevant concepts today (65 primes, 54 kernel-v0, molecules,
  11 kernel-v1 senses); expressibility coverage 0.3542 at molecules-v0
  [MEASURED: synthesis v6 §4]. SCALE-1 designs the 10k→1M ladder; S0 (10k) qualified
  the vector substrate, not any thesis quantity.
- **Efficiency ledger:** zero valid data ever; DDC (training-free kernel-guided
  dimension collapse on SmolLM2) is the first live measurement, in flight
  [MEASURED: synthesis v6 §3].
- **Correctness ledger:** authored-content lift is real and audited (+0.25/+0.27) but
  explicitly NOT kernel-specific runtime structure; every runtime-judgment interface
  tried so far (5/5) failed its instrument; every deterministic channel (6/6)
  instrumented cleanly [MEASURED: synthesis v6 §2].
- **House law:** Law-1 interface-locality — no kernel vector enters a model's
  activations; kernel content enters as text/selection/external computation
  [MEASURED: DDC.md §1.2].

---

## 2. The seam map — every colibri/GLM-5.2 seam, for (A) and (B)

Taxonomy [STIPULATED: ASM-1973]. Five seams: **B1a** concept-conditioned expert
caching/pinning/prefetch; **B1b** concept-guided expert-drop ("DDC on the expert
axis"); **B2** engine as speculative drafter; **B3** concept-vector KV; **A1** engine
as grounding/verification gateway. B1a/B1b/B2/B3 serve thesis (B); A1 serves (A); B2
and A1 share machinery (both consume engine output at the gateway).

### 2.1 B1a — concept-conditioned expert selection for the CACHE (quality-safe)

**Mechanism.** Map input (and intended-output) concepts → a predicted expert working
set per layer → install it as colibri's pinned hot set (`PIN=stats.txt`) and/or as
prefetch hints. The concept→expert map is built offline from routing traces: run
concept-stratified corpora (kernel renderings per concept cluster; engine-closure
renderings for entailed content), record `.coli_usage`-style per-layer expert
histograms per concept cluster, invert into "experts that light up when this concept
region is active." At inference, the active concept set (from the prompt; later, from
the engine's computed closure — concepts *entailed* to become relevant, which is the
only part a generic topic model cannot do) selects which histograms to union.
[STIPULATED: ASM-1975]

**Why this is the safest seam:** pinning and prefetch are **quality-preserving by
construction** — a wrong concept map costs only cache misses, never output quality.
No verdict gate on model ability is needed; the endpoints are pure systems numbers
(hit rate, bytes/token, tok/s). [STIPULATED: ASM-1978]

**Quantified potential [EXTRAPOLATION: ASM-1979, resolution = P0 replay]:** in the
disk-bound regime, bytes/token scales with (1 − hit). Illustrative bands: if global-hot
pinning achieves hit H_g = 0.3 and concept-conditioned pinning at the same RAM budget
achieves H_c = 0.5 / 0.6 / 0.7, tok/s multiplies by 1.4× / 1.75× / 2.3×. Whether ANY
H_c > H_g exists is unknown — MoE routing in DeepSeek-style models is
high-entropy, and the sequence-level activation locality that offloading systems
exploit (e.g. MoE-Infinity, arXiv:2401.14361; Mixtral-offloading LRU+speculative,
arXiv:2312.17238; Pre-gated MoE, arXiv:2308.12066 — all cited at abstract level, not
source-verified this tick) is locality-in-general, not concept-conditioned locality.
The admission probe (§5, P0) measures it directly and costs almost nothing.

**The deflators, named now [STIPULATED: ASM-1977]:** (i) colibri's own AUTOPIN
learning cache — "pin what was hot recently" with zero kernel; (ii) an
embedding-topic-cluster prior — cluster prompts by any off-the-shelf embedding, build
per-cluster expert histograms, no kernel anywhere (the knull-analog for this seam);
(iii) router-lookahead itself. A kernel-specific sentence is licensed only if the
kernel arm beats (i) AND (ii) at matched RAM budget on held-out prompts — otherwise
the honest result is "concept/topic conditioning helps; the kernel is one way to
condition," the exact shape of the f2b/DECONF content-not-structure deflation, and it
must be reported as such.

### 2.2 B1b — concept-guided expert-DROP (dimension collapse on the expert axis)

**Mechanism.** Do not load experts outside the concept-relevant set at all: either
(soft) restrict the router's candidate set / re-bias `choice[e]` before top-k, or
(hard) build a deployment-specific expert subset — a *pruned expert shard* — for a
concept-profiled workload, shrinking both disk footprint (toward f × 370 GB for
retained fraction f) and per-token I/O (linearly, §1.2). This is DDC's move with the
expert as the unit of deletion instead of the residual-stream direction; colibri's
`TOPK`/`TOPP` knobs already implement the *router-weight-only* version from the
environment, giving the M1-analog control for free. [STIPULATED: ASM-1975]

**Difference from B1a, honestly:** expert-drop **changes the computed function** —
it needs DDC-style matched-compression retention evaluation (arms at matched expert
load-count: concept-guided vs router-weight-only truncation vs random-drop vs
frequency-only drop), with public-benchmark or loglikelihood endpoints
[STIPULATED: ASM-1978]. Note also the null worth pre-naming: the router's own weight
is already a strong per-token relevance signal; the concept prior's plausible
increment is *cross-token stability* (one set for the whole generation → cacheable,
shardable), not per-token selection quality. Expert-pruning literature exists (task-
and domain-conditioned expert pruning; cited at abstract level only) — the kernel arm
must beat those constructions' kernel-free analogues.

**Quantified potential [DERIVED + EXTRAPOLATION: ASM-1979]:** load 4-of-8 experts →
~2× disk-bound tok/s and ~½ I/O by arithmetic; the open question is entirely on the
quality side. A deployment shard for a concept-bounded domain at f = 0.25 would cut
the disk estate 370 → ~93 GB — meaningful for the "runs on a small box" story if
retention holds. No retention number is assumed anywhere in this document.

### 2.3 B2 — the deterministic engine as SPECULATIVE DRAFTER

**Mechanism.** Colibri's grammar-forced drafting is the existence proof of the
integration path: externally-computed token spans are injected as pre-accepted or
to-be-verified drafts, composing with MTP, with adaptive disable below 50% acceptance.
The engine-as-drafter seam: where the engine's closure licenses the continuation
(entailed answer spans, typed-slot fills, canonical renderings), render it and inject
it as a draft; GLM-5.2's forward verifies. Verification amortises expert I/O across
the draft span (§1.2.3), so in the disk-bound regime accepted drafts are nearly free
throughput. Two operating modes, distinct in claim type [STIPULATED: ASM-1980]:
(i) *lossless* — drafts verified by the model's own distribution (rejection sampling);
acceptance is measurable and the output distribution is unchanged — pure (B);
(ii) *forced* — engine-licensed spans forced as in grammar mode; output changes; this
is really an (A) mechanism (constrained correct decoding) wearing a (B) costume.

**Honest impact bound:** the accelerator only fires on output spans the engine can
derive; with today's kernel that is ≈ 0% of open-workload tokens. Value scales with
(coverage of engine-derivable spans) × (surface-form acceptance), the first factor
gated on SCALE-1 and the second unknown (engine renderings must match GLM-5.2's
lexical choices to be accepted losslessly — plausibly low outside heavily constrained
formats like JSON/structured QA, where grammar forcing already reigns).
[ASSESSMENT]

### 2.4 B3 — concept-vector KV / "one concept vector carries many tokens"

**Mechanism as proposed:** compress or augment MLA's per-token latents with
kernel-concept vectors so that a span of tokens rides one concept-level entry.
**Read, honestly:** (i) MLA KV is small and RAM-resident (576 floats/token/layer;
~182 KB/token persisted) — it is NOT the measured bottleneck at any context length
colibri users run; DSA already sparsifies long-context attention; (ii) GLM-5.2's
attention was trained to read ITS latents — substituting foreign vectors
training-free breaks function, and any adapter that learns the mapping is a training
intervention outside this programme's training-free tier; (iii) it violates the
programme's own Law-1 interface-locality discipline (no kernel vector enters the
model) as currently stated. Training-free KV *merging/eviction* methods exist
(kernel-free) and would be the mandatory deflators if this were ever pursued.
**Disposition: deferred indefinitely; recorded as a research note, not a seam with a
probe.** [STIPULATED: ASM-1981]

### 2.5 A1 — engine as grounding/verification layer over GLM-5.2 (thesis A)

**Mechanism.** All at the gateway (`c/openai_server.py` or a proxy in front of it),
zero C changes [STIPULATED: ASM-1982]:

1. **Pre-generation grounding:** map prompt content into kernel concepts/world facts;
   run engine closure; inject typed facts + proofs into context (the SCALE-GROUND A3/A4
   arm shapes, with GLM-5.2 as host).
2. **Post-generation checking:** extract claims from output; engine verdicts
   {CONSISTENT, ANOMALOUS, REFUSE}; on conflict → verify-retry regeneration or
   flagged output (honesty-first scoring alignment, issue #18).
3. **Constrained decoding:** engine-emitted GBNF grammars force licensed forms in
   structured outputs — the one mechanism that is simultaneously (A)-correctness and
   (B)-throughput (forced spans ≈ 1.0 acceptance).
4. **Instrument-grade host property:** a pinned-weights, locally-replayable,
   deterministic (DRAFT=0 greedy byte-reproducible) frontier-class host removes
   API-model drift from the instrument threat model — directly responsive to the
   programme's 0-for-5 runtime-interface failure ledger, where a leading explanation
   (45% weight, [SUBJECTIVE] per synthesis v6 §2.3) is that prior hosts were too
   SMALL to cooperate with verifiers. GLM-5.2-as-host is the natural scale-artifact
   test of that hypothesis.

**Honest bounds:** (a) thesis-grade (A) results are gated on kernel coverage — at
0.3542/<100 concepts, A1 today demonstrates plumbing on engine-covered domains
(kinship, the 11 senses), nothing more; (b) A1 does not actually need colibri —
GLM-5.2 by API is faster and cheaper for pure gateway experiments; colibri's A1 value
is ONLY determinism/pinning/logit access; (c) every (A) experiment must clear the
blocking-pilot protocol (ASM-1830..1836) and inherits the ENGINE-INF divergence-seam
discipline: kernel-specific value is askable only where kernel and non-kernel sources
derive divergent behaviour. [STIPULATED: ASM-1982]

---

## 3. Ranking, and the first target

Criterion: tractability × impact-on-stated-goal × testability-with-house-discipline
[STIPULATED: ASM-1975]. Rank:

| # | Seam | Tractability | Impact | Testability | One-line justification |
|---|---|---|---|---|---|
| 1 | **B1a cache/pin conditioning** | HIGH — zero-to-tiny C changes (`PIN=` file + env knobs exist) | direct hit on the measured bottleneck; ceiling = §2.1 bands | HIGH — pure systems endpoints, quality-safe, built-in deflator (AUTOPIN), offline trace replay | cheapest honest question with a mechanical admission gate |
| 2 | **B1b expert-drop** | MEDIUM — soft mode via TOPK/TOPP now; guided mode = glm.c router edit | larger (footprint AND I/O, linear) | MEDIUM — needs retention endpoints; eval throughput is the binding cost (§5.4) | run only after B1a's admission gate says routing structure exists |
| 3 | **A1 gateway grounding** | HIGH — no C changes | (A)-thesis; bounded hard by kernel coverage | MEDIUM — runtime-judgment interfaces are the programme's 0-for-5 zone; needs blocking pilots | build the plumbing cheap; thesis experiments wait for coverage + ENGINE-INF |
| 4 | **B2 engine drafts** | MEDIUM-HIGH — grammar-draft path exists | today ≈ 0 (coverage); grows with SCALE-1 | HIGH for acceptance-rate measurement; LOW for end-to-end value now | measure acceptance as a P1 side-quest; not a lead bet |
| 5 | **B3 concept-KV** | LOW — needs training + Law-1 change | not the bottleneck | LOW | deferred; research note only |

**First target: B1a, entered through a measurement-only probe (P0, §5).** Why: it is
the only seam whose decisive first question — *does concept-conditioned expert-routing
structure exist in GLM-5.2 at all?* — is answerable with no C modification, no quality
evaluation, no GPU, ~$20–50 of instance time, and a mechanical yes/no (an oracle-replay
margin, §5.3). It attacks the component colibri's author measured as the bottleneck;
its failure mode is cheap and informative (a measured "routing is too flat /
conditioning adds nothing over recency" datum kills B1b too, saving its larger cost);
and its success unlocks B1b with the concept→expert map already built. This ordering
also honours the house delegate-and-reanalyse rule: P0's traces are a dataset that can
be re-analysed repeatedly (different conditioning schemes, cluster granularities,
horizon lengths) without re-spending on collection. [STIPULATED: ASM-1975]

**Where each seam is speculative, said plainly [ASSESSMENT]:** B1a's existence
question is genuinely open — DeepSeek-family routers are trained with load-balancing
pressure that *fights* expert specialisation; flat conditional distributions would be
a fast honest kill. B1b adds an open quality question on top. B2's acceptance outside
constrained formats is likely poor. A1's mechanism is sound but its thesis value is
entirely downstream of a kernel that does not yet exist at coverage. B3 is not
currently a real seam.

---

## 4. Gating and prerequisites — the dependency line from today's tracks

What must exist before each stage of this north-star is reachable
[STIPULATED: ASM-1983]:

```
sense-split construction (Stage A done, B designed)     [kernel content]
        └─> SCALE-1 S0 ✓ → S1 (100k) → S2 (1M)          [kernel coverage + NL→concept mapper]
DDC ddc0/ddc1 (in flight)                               [drop-methodology + first efficiency datum]
ENGINE-INF E0 (designed, GO recommended)                [typed-closure correctness premise for A1]
RULES-1 certificate ✓ (engine exact at scope)           [the (A)/B2 computation source]
────────────────────────────────────────────────────────
GLM52-NS  P0 (probe: colibri up + routing traces)        needs: NOTHING above — only the EC2 box
          P1 (concept-conditioned pinning prototype)     needs: P0 admission + a concept-stratified corpus
                                                          (kernel renderings suffice at current size —
                                                          conditioning needs concept LABELS, not coverage)
          P2a (B1b guided drop + retention)              needs: P1 win + DDC's arm/control discipline
                                                          (and reads ddc1's verdict for method transfer)
          P2b (A1 thesis experiments on GLM-5.2 host)    needs: kernel coverage (SCALE-1 S1/S2) +
                                                          ENGINE-INF E0 verdict + blocking pilot per
                                                          ASM-1830..1836
          NS  (the actual north-star: comprehensive      needs: 1M kernel (SCALE-1 S2), engine at scale
              kernel drives routing + drafting + qc)      (RULES-SCALE), concept→expert map (net-new,
                                                          seeded at P0/P1), NL→concept mapper (SCALE-1's
                                                          named open — the l3a parse wall)
```

Explicitly: **the current tracks are not blocked by, and do not wait on, GLM52-NS** —
this is the roof they build toward. Conversely GLM52-NS P0/P1 need almost nothing from
them: conditioning experiments need concept *labels* on prompts, which the present
<100-concept kernel already provides for kernel-rendered corpora; what today's kernel
cannot provide is coverage of arbitrary user prompts — which is why P1's honest scope
is "concept-labelled workloads," and why the NS row is gated on SCALE-1. Two objects
are **net-new** and belong to this track alone: the concept→expert alignment map, and
(shared with SCALE-1 §6.6) the runtime prompt→concept conditioning path.
[STIPULATED: ASM-1983]

---

## 5. Infrastructure and the cheapest first probe

### 5.1 Instance spec [STIPULATED: ASM-1984; prices are planning figures, verify at spin-up [EXTRAPOLATION: ASM-1985]]

Constraints: x86 + AVX2 (Graviton excluded), ≥16 GB RAM (25 GB recommended), ≥400 GB
**instance-local** NVMe (network volumes explicitly warned against by colibri), enough
vCPU that conversion and matmul do not dominate; the maintainer has authorised an
extra EC2 instance.

| Option | vCPU / RAM / NVMe | ~On-demand (us-east-1) | Read |
|---|---|---|---|
| **i4i.xlarge** (recommended floor) | 4 / 32 GiB / 937 GB Nitro NVMe | ~$0.34/h (spot ~$0.10–0.15) | fits: 370 GB model + staging; 32 GB ⇒ ~15–18 GB expert cache; disk ~1 GB/s-class ⇒ expect dev-machine-like ~0.05–0.1 tok/s cold |
| **i4i.2xlarge** (recommended probe box) | 8 / 64 GiB / 1,875 GB | ~$0.69/h (spot ~$0.2) | 64 GB ⇒ ~45 GB cache ≈ 12% of experts — materially better hit-rate headroom for the conditioning experiments; 8 vCPU halves conversion + matmul time |
| m6id/c6id.2xlarge | 8 / 32 or 16 GiB / 474 GB | ~$0.40–0.47/h | 474 GB is tight (370 + OS + staging); c6id's 16 GB RAM is at colibri's floor — not recommended |

**Storage lifecycle:** instance-store NVMe is ephemeral — a stop destroys the 370 GB
artifact. Plan: convert once → `aws s3 cp` the int4 artifact to S3 (~370 GB ≈
$8.5/month standard class; restore ≈ 30–60 min at parallel throughput) → treat the
instance as disposable between sessions. Conversion itself streams the ~756 GB FP8
checkpoint shard-by-shard from HF (5 GB peak staging), so the download is bounded by
network: hours, not days; ingress is free. [STIPULATED: ASM-1984]

### 5.2 P0 — the cheapest first probe (measurement only, no C changes)

Budget: instance 24–72 h ⇒ **~$20–50 on-demand (~$8–20 spot) + S3 $8.5/mo; 2–4
agent-days**; $0 model-API spend; runs unattended after setup (nohup + checkpointed
scripts, per house box discipline). [STIPULATED: ASM-1986; costs EXTRAPOLATION:
ASM-1985]

1. **P0.1 bring-up + fact verification.** Build (`setup.sh`), convert, `coli doctor`,
   `iobench`; mechanically record from the checkout + `config.json`: expert count and
   geometry (resolving the 21,504 vs 19,200 and top-k 6-vs-8 discrepancies), the pin
   file format, LOOKA/PILOT semantics. Every §1.1 row flips from LIT-BACKED(fetch) to
   verified-at-source or gets corrected. Baselines: cold/warm tok/s, peak RSS,
   bytes-read/token (iostat), MTP acceptance, PILOT on/off, AUTOPIN on/off — our box's
   analogue of the README table.
2. **P0.2 routing-trace collection.** A prompt suite stratified by concept cluster:
   kernel-rendered explications + engine-closure renderings per cluster (kinship
   worlds, the 11 senses, molecule families), plus matched generic text (C1-analog),
   plus the knull plain-dictionary renderings (C2-analog). Run with routing-statistics
   recording (`.coli_usage`, LOOKA counters; if per-token per-layer expert IDs are not
   natively dumped, a ~20-line fprintf patch in `expert_load()`/router — the one
   permitted C touch, diff kept in-repo). Output: the trace dataset, committed
   (small: expert IDs, not weights).
3. **P0.3 offline replay analysis (the admission gate G-B1).** From traces alone,
   compute: (a) per-concept-cluster expert-activation histograms and their divergence
   from the global histogram (conditional-vs-marginal concentration, per layer);
   (b) **oracle replay**: for each candidate policy — global-hot pin (AUTOPIN-analog),
   recency-LRU (colibri default), embedding-topic-cluster pin (kernel-free deflator),
   kernel-concept pin, oracle per-prompt pin (upper bound) — the hit rate at matched
   RAM budgets, on held-out prompts. All closed-form counting over logged traces; CPU
   minutes; re-analysable forever. **Gate G-B1 [STIPULATED: ASM-1976]: the seam is
   ADMITTED iff concept-conditioned pinning beats BOTH the global-hot AND the
   topic-cluster deflators by a pre-registered margin (≥10% relative miss reduction
   at matched budget, exact threshold to be frozen in the P1 prereg) on held-out
   prompts; else B1a AND B1b are recorded dead-at-this-model and the track's residual
   value is A1 plumbing + B2 acceptance measurement.**

### 5.3 P1 — concept-guided pinning prototype (only if G-B1 passes)

Live (not replay) A/B at matched RAM budget: kernel-concept `PIN` files vs AUTOPIN vs
topic-cluster vs random, on held-out concept-labelled workloads; endpoints
bytes-read/token, tok/s, hit rate; plus B2 side-quest (engine-rendered drafts on
kinship/sense items → acceptance rate through the draft path). ~1–2 agent-weeks +
$50–150 instance time. **Gate G-P1:** kernel arm beats both deflators live with
quality byte-identity (pinning changes no computation — verified by DRAFT=0 output
equality). A win licenses at most: *"concept-conditioned expert caching reduces
expert I/O on concept-labelled workloads at this model/box"* — sign, not slope; a
kernel-vs-topic tie is the deflationary datum and is reported with equal prominence.
[STIPULATED: ASM-1986/1987]

### 5.4 P2 and beyond (shapes only, own preregs later)

- **P2a (B1b):** guided expert-drop at matched load-count, DDC-style arm structure;
  quality endpoints via **prefill/loglikelihood scoring, not generation** — prefill
  batches amortise expert loads across the whole sequence, so loglik endpoints (the
  `poc/pubeval` style) are 10–100× cheaper than generative eval at 0.1–1 tok/s; a
  small `openai_server.py` patch to expose echo+logprobs is a named build task.
  [STIPULATED: ASM-1988]
- **P2b (A1):** GLM-5.2-as-host verify-retry / grounding experiments under the
  blocking-pilot protocol, gated on ENGINE-INF E0 + coverage; colibri used for
  determinism, API used for throughput where determinism is not load-bearing.
- **NS:** the comprehensive-kernel integration — concept→expert shards, engine
  drafting at coverage, gateway grounding — gated on SCALE-1 S2 and RULES-SCALE.

### 5.5 Staged plan summary [STIPULATED: ASM-1986]

| Stage | What | Cost (planning bands) | Go/no-go |
|---|---|---|---|
| **P0** | colibri up; facts verified; baseline perf; routing traces; replay analysis | ~$20–50 + $8.5/mo S3; 2–4 agent-days | **G-B1** concept-conditional structure exists vs both deflators (mechanical, pre-registered margin) |
| **P1** | live concept-guided pinning A/B (+ B2 acceptance side-quest) | ~$50–150; 1–2 agent-weeks | **G-P1** kernel beats AUTOPIN + topic-cluster at matched budget, byte-identical outputs |
| **P2a** | guided expert-drop, matched-I/O retention (prefill-scored) | ~$100–300; 2–3 agent-weeks | DDC-style retention gates; needs its own prereg + pilot |
| **P2b** | (A) host experiments on GLM-5.2 | per-experiment | ENGINE-INF E0 + coverage + blocking pilot |
| **NS** | comprehensive-kernel integration | grant-class | SCALE-1 S2 + RULES-SCALE + everything above |

Every stage stops cleanly; no stage pre-commits the next; per the no-pre-surface rule,
once the maintainer approves a stage + ceiling it runs without re-surfacing inside the
ceiling.

---

## 6. Honest risks

1. **Routing may be flat.** Load-balanced MoE training actively resists the expert
   specialisation this whole track needs. G-B1 exists to find this out for ~$30
   instead of ~$300. [ASSESSMENT]
2. **The kernel-specificity bar is brutal here.** A topic model conditions routing
   without any NSM content; the programme's own history (four content-not-structure
   deflations) says to expect the tie. The one mechanism a topic model cannot
   replicate — conditioning on *entailed-but-unstated* concepts from engine closure —
   is exactly the part gated on engine coverage. A P1 "conditioning helps, kernel is
   one conditioner among several" outcome is the modal expectation and is still a
   useful systems result — but it must never be reported as kernel value.
   [ASSESSMENT; the wording discipline is STIPULATED: ASM-1977/1987]
3. **Single-file C, no plugin architecture, single upstream author.** Every C change
   is a fork-maintenance liability against a fast-moving 2,400-line file; mitigation:
   P0/P1 confine changes to a trace-dump patch + PIN files + gateway; anything larger
   waits for a maintainer call on fork-vs-upstream-PR etiquette (upstream-noise memory
   applies). [STIPULATED: ASM-1989]
4. **Evaluation throughput is the hidden cost of B1b/A1.** At 0.1–1 tok/s, generative
   benchmarks take days per arm; the prefill/loglik mitigation (§5.4) is load-bearing
   for P2a's affordability. [DERIVED + STIPULATED: ASM-1988]
5. **Fetched facts may be paraphrased wrong.** All §1.1 rows carry fetch-level
   provenance and two identified internal discrepancies; P0.1 re-verifies at source
   before anything is built on them. [STIPULATED: ASM-1971]
6. **Ephemeral NVMe.** Operational only (S3 lifecycle, §5.1), but a silent instance
   stop costs a half-day restore or a re-conversion.
7. **Scope temptation.** GLM-5.2 numbers will be quotable; claim caps are
   pre-registered (ASM-1987): nothing in P0–P1 licenses any intelligence, efficiency,
   parity, or cost claim about the programme theses — P0/P1 are systems measurements
   on one model on one box.

---

## 7. Feasibility read — (A) vs (B) [ASSESSMENT, one designer's opinion, binding on nothing]

**(B) inference-compute reduction is the better-posed near-term bet.** It attacks a
bottleneck the reference implementation has already quantified (disk-bound expert
streaming; inverse-linear throughput in expert bytes); its first question is admission-
gated, mechanical, and cheap (~$30); its interventions have a quality-safe rung (B1a)
before any function-changing rung (B1b); and its methodology imports directly from
DDC. Its honest weaknesses: the existence of concept-conditional routing structure is
unknown, and the kernel-specific increment over kernel-free conditioning is — on the
programme's own four-deflation record — more likely than not to tie until the engine
can predict *entailed* expert demand, which needs coverage. Expected-value read:
moderate probability of a real systems win for concept/topic-conditioned caching;
low-to-moderate probability that the KERNEL specifically earns the win at current
coverage; the probe prices this honestly at tens of dollars.

**(A) intelligence improvement is mechanism-sound but coverage-starved.** The gateway
+ engine-verdict + GBNF machinery is buildable this week and needs no C changes; but
with <100 concepts at coverage 0.35 every (A) demonstration stays at plumbing scale,
and the programme's 0-for-5 runtime-interface ledger demands blocking pilots before
any thesis experiment. The genuinely new (A) asset colibri contributes is
instrument-grade determinism on a frontier-class host — the right substrate for the
scale-artifact test of the verify-retry hypothesis once ENGINE-INF lands and coverage
grows. (A) should therefore trail (B) on this substrate, entering at P2b, not P0/P1.

**Both readings are pre-verdict expectations, not results; CORRECTNESS and EFFICIENCY
remain INCONCLUSIVE-PENDING per synthesis v6, and nothing in this document moves
either.**

---

## Self-check gate (governance)

Every load-bearing claim above carries MEASURED / LIT-BACKED(fetch, with paraphrase
risk disclosed and a named P0 re-verification) / DERIVED / STIPULATED / EXTRAPOLATION /
ASSESSMENT; every design CHOICE is STIPULATED with an ASM id, never smuggled as fact;
external-source discrepancies (expert count, top-k, dense-resident GB) are flagged
rather than resolved by fiat; both outcome directions of every gate are worded in
advance; deflator arms (AUTOPIN, topic-cluster, knull-analog) are mandatory before any
kernel-specific sentence; claim caps are registered (ASM-1987). No frozen record,
verdict, encoder pin, or registered assumption is touched; no git action, no model
run, no spend occurs in this pass. Assumption block ASM-1970..1989 emitted to
`docs/next/design/asm-glm52-1970-1989.json` (owner designer-4; range verified free at
emission — central register tail ASM-1967, repo-wide grep for `ASM-19[7-9][0-9]`
empty); central registration in `registry/assumptions.jsonl` is the coordinator's
action, in the same commit that lands this file, after the standing GPT-5.6 review
gate.
