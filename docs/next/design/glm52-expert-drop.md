# GLM-DROP (B1b) — kernel-guided GLM-5.2 expert-drop at matched experts-per-token

> **Status: DESIGN ONLY (Programme-3 family, efficiency redirect per issue #27
> option A). Nothing here is frozen, pre-registered, scheduled, or run; no frozen
> record, verdict, encoder pin, or registered assumption is touched; no model run,
> no spend, and no git action occurs in this pass. This document states NO
> feasibility conclusion — it designs the experiment that would produce one.**
> Author: Fable, architecture-design role (designer-8), 2026-07-13.
> REVISION 2 author: Fable, architecture-design role (designer-12), 2026-07-13.
> REVISION 3 author: Fable, architecture-design role (designer-17), 2026-07-13.
> REVISION 4 author: Fable, architecture-design role (designer-20), 2026-07-13.
>
> **Maintainer decision consumed (verbatim, issue #27 comment):** "Proceed with A
> (redirect), with a token underpowered-DDC secondary if you want the SmolLM
> cross-check." — the GLM-5.2 kernel-guided expert-drop (B1b) becomes the primary
> efficiency instrument; DDC's disposition (park vs token secondary) remains the
> coordinator's call and is not decided here.
>
> **Standing cost directive consumed (issue #28 thread, maintainer, verbatim):**
> "Yes that works; please also use similar cost saving measures on other GLM 5.2
> experiments (and other experiments generally if applicable)..." — SPOT i4i
> instances, expert-pinning/warm-cache, and co-location on the KaE (#28) instance
> are baked into this design as requirements, not options (§6).
>
> **ASM blocks claimed:** ASM-2230..2239 (R0, companion file
> `poc/glm52-probe/asm-glm-drop-2230-2239.json`, owner designer-8),
> ASM-2290..2293 (R1, companion file
> `poc/glm52-probe/asm-glm-drop-r1-2290-2293.json`, owner designer-8), and
> **ASM-2340..2352 (REVISION 2, companion file
> `poc/glm52-probe/asm-glm-drop-r2-2340-2352.json`, owner designer-12; range
> verified free at emission: central register tail in
> `registry/assumptions.jsonl` is ASM-2293; companion files elsewhere claim
> ASM-2300..2312 and ASM-2313..2330; repo-wide grep for `ASM-23[4-9][0-9]`
> empty before this emission).** [R2 note — stale-prose correction, review
> finding 13: the R0 and R1 blocks ARE now centrally registered
> (`registry/assumptions.jsonl` lines 1082–1091 and 1106–1109); earlier
> wording in this document saying the central register had not been written
> described the state at R0/R1 emission and is superseded. Central
> registration of the R2 block, and the supersession edits to the central
> copies of ASM-2232/2233/2234/2235/2236/2237/2238/2239/2290/2291/2292/2293
> listed in §R2.14, remain the coordinator's action with the landing commit.]
> [R3 note: REVISION 3 claims NO new ASM range; because the ASM-2340..2352
> block is not yet centrally registered, its companion file is AMENDED IN
> PLACE (each amended record carries an inline "[R3 amendment, designer-17,
> 2026-07-13: ...]" provenance note; pre-R3 companion bytes sha256
> 780ec24f4451adb8cac6bcf8a9da755e8fb19a7a5f2650771dc167a945840e34). Once the
> block lands centrally, any further change is supersede-by-citation, never
> in-place.]
> [R3 RANGE-ASSIGNMENT HAZARD, disclosed for the coordinator: a companion
> file that did not exist at R2 emission,
> `docs/next/design/asm-prompt-cache-2331-2345.json` (owner designer-14),
> states its ASSIGNED range as 2331..2345 while EMITTING only
> ASM-2331..2339. There is NO emitted-ID collision with this design's
> ASM-2340..2352 (verified this tick: no file emits an ASM-2340..2345 id
> except this design's companion), but the assignment ranges overlap on
> 2340..2345. The coordinator must adjudicate at central registration —
> either confirm this design's 2340..2352 claim (the prompt-cache block's
> unused 2340..2345 tail lapses) or renumber one block BEFORE either
> registers; neither block registers into a collision. Flagged here because
> this pass may not write the registry or either other file.]
>
> **REVISION 1 (2026-07-13, designer-8, same pass discipline):** the standing
> codex review of this design returned ISSUES on four points: (1) the masked
> deflator arms were not dose-matched (m-emb conditioned on one nearest cluster
> while m-kern may union multiple concepts; m-rand lacked the universal core);
> (2) map coverage was overstated as "~24 concepts" — the probe source is 24
> prompts across **8 concept clusters** (3 prompts/cluster); (3) the quality
> power target (0.90 at a true +3) was unsound under the joint licensing rule
> (p < 0.05 AND observed ≥ +3 has a ~50% power ceiling at true +3); (4) D2
> compared against the accuracy-selected maximum of the deflators instead of
> testing BOTH. All four are fixed in place below, tagged **[R1]**, and
> recorded in §R1. The R1 pass claimed ASM-2290..2293.
>
> **REVISION 2 (2026-07-13, designer-12, same pass discipline):** the standing
> GPT-5.6 xhigh review of the R1 design
> (`poc/gpt56-review/expert-drop-r1/out/last-message.json`, sha256
> f67aef03254faf3c3336d7edc319fd9565d192979132fb96a22073d0c4d290e4) returned
> **FIX-FIRST** with 9 blocking findings and 4 should-fix/minor findings. ALL
> THIRTEEN are resolved in place below, tagged **[R2]**, with the finding-by-
> finding audit trail in §R2. Headline changes: frozen analysis population,
> estimand, deterministic multilabel→analysis-cluster rule, and EXACT 2^8=256
> sign-flip enumeration with F1-K's registered sign-symmetry basis + bootstrap
> fallback imported (§5.2); frozen per-layer universal-core algorithm with a
> <64 cap (§2.1); every open arm parameter pinned and the TOPP branch REMOVED
> (§3.1, §4.2); failed-superiority readings reworded — no equivalence claim is
> licensed anywhere without a separately powered test (§5.3); the pilot moved
> to the F1-K dev-96 panel with a continuous statistic and aligned strict
> inequalities (§4.2); the standing F1-K co-location isolation clause
> implemented literally (§6.1); a separated correctness/performance regime
> with loads/token as the ONLY systems endpoint and arm-level tok/s
> comparisons declined (§4.3, §6.2); the DROP sidecar redefined as an
> immutable item-ID→mask table (§6.3); the cost model re-derived with R=3
> preregistered derangements, instance-hours and dollars stated separately
> (§6.4); per-mask-only footprint reporting (§5.1, §6.2); the tag schema
> closed to four tags with the ASM-2291/2292 splits (header, §R2.11); and the
> ASM-2238 contradiction superseded in full (§6.4, §R2.12). Review-OK
> foundations — the accuracy endpoint, the full-TOPK=8 reference (b0-full),
> the paired positive contrasts, fixed f=0.25, and dev-only selection — are
> retained.
>
> **REVISION 3 (2026-07-13, designer-17, same pass discipline):** the standing
> GPT-5.6 re-review of the R2 design
> (`poc/gpt56-review/expert-drop-r2/out/last-message.json`, sha256
> bde94f8510e0ad5e553a22998cbec5514f89ba8ec58926f7264457e3c474e37d) returned
> **materially improved, NOT freeze-ready**: findings 4/5/6/7/9/10/13 RESOLVED
> (none regressed here), findings 1/2/3/8/11/12 residually PARTIAL. R3 closes
> each residual by MATERIALIZING every pin computable from committed repo
> bytes this pass (CPU-only, ~$0, no model, no spend) and by explicitly
> re-classing every remaining deferral as a SEQUENCED-AFTER-F1-K-FREEZE pin —
> a named freeze-manifest entry that is a pure function of frozen inputs —
> never an open hole. Headline: the universal core is COMPUTED and hashed
> (76 layers, 2,108 cells, sizes 15–46, no layer at cap; §2.1); the
> concept→cluster table is MATERIALIZED and hashed (§2.1); the
> multilabel→analysis-cluster rule is made EXECUTABLE (longest-match /
> earliest-span / table-order, importing F1-K's registered precedence; §5.2);
> the PINNED PLANNING SIMULATION is RUN and hashed — all 2^8 = 256 sign flips
> enumerated; simulated MDE_true ≈ 16 pts at the n = 300 planning point,
> joint power ≈ 0.12 at true +3, HARSHER than the Gaussian ≈12-pt planning
> figure, which it supersedes (§5.2, Appendix A); the mask-construction PRNG
> is pinned to a SHA-256 DRBG with every seed named (§3.1); k-means is pinned
> to an own deterministic implementation (§3.1); the encoder-weights pin gets
> a fail-closed default (§3.1); the mask-table hashes and the C-patch
> approval are re-classed as sequenced pins / a named external gate with
> fail-closed defaults (§6.3); central ASM-2238's contradicted clauses are
> quoted VERBATIM with an interim precedence rule (§6.4); and a measured
> correction lands: the trace spans **76** MoE layers (3–78), not 75 (§2.1).
> Audit trail in §R3; a MoE-layer-count correction aside, no RESOLVED finding
> is touched.
>
> **REVISION 4 (2026-07-13, designer-20, same pass discipline):** the standing
> GPT-5.6 re-review of the R3 design
> (`poc/gpt56-review/expert-drop-r3/out/last-message.json`, sha256
> afcbfe7e83084d2bb238b6c002f1d7b2ea102cd452abc346e7dc5cfa7e69b95a) confirmed
> findings 1 and 2 RESOLVED and left findings 3, 8, 11, 12 residually PARTIAL.
> Findings 11 and 12 residuals are CENTRAL-REGISTRATION actions
> (registry write + landing commit) that are coordinator-owned and outside
> this pass's brief — they remain the explicitly sequenced pins §R3.11/§R3.12
> already classify, and R4 does not touch them. R4 closes the two remaining
> DESIGN blockers: (finding 3) the MULTILABEL COMBINATION RULE is pinned —
> one deterministic summed-score rule, identical across m-kern / m-emb /
> m-drng (per-cluster mean-centred conditional mass, summed over the item's
> conditioning clusters in ascending cluster-index order, single descending
> ranking, ascending-expert-index tie-break, filled to exactly 64/layer;
> §2.1 item 3, §3, §3.1 item 3); and (finding 8) the mask table's CANONICAL
> SERIALIZATION + HASH FRAMING are pinned NOW (record ordering, item-ID
> encoding, per-layer expert-bit ordering, the exact bytes under the
> per-entry and whole-table SHA-256s; §6.3) — each table is a PURE FUNCTION
> of its pinned inputs, with the item LIST the only sequenced-after-F1-K
> input, exactly as §5.1 already sequences it. Audit trail in §R4; no
> RESOLVED finding (1/2/4/5/6/7/9/10/13) is touched.
>
> **Tag convention (house discipline) [R2 — closed schema, review finding 11]:**
> every load-bearing claim carries EXACTLY ONE of `[MEASURED: ref]` = repository
> bytes or a pinned mechanical output read this tick, cited with full SHA-256
> (header table) plus the exact JSON key or log section; `[LIT-BACKED: ref]` = a
> published source verified at source; `[STIPULATED: ASM-id]` = a design choice
> made here, with rationale in the ASM record; `[EXTRAPOLATION: ASM-id]` = a
> registered projection, never a premise, always load_bearing:false with a
> resolution path. This schema is CLOSED: the two additional tags the R0/R1
> convention permitted are RETIRED and appear nowhere in this convention —
> arithmetic over tagged premises is stated inline with its premises' tags,
> and designer judgment appears only as explicitly non-binding prose
> ("designer prior, binding nothing"), never as a tag.
>
> **Inputs read this tick (full SHA-256; finding 13):**
> - `poc/glm52-probe/results/probe-main.log`
>   sha256 77023d2b94e5f7719bdf86955de26cfb720ad33eb53521b48d47e50bc2a52592
> - `poc/glm52-probe/results/routing-analysis.json`
>   sha256 f5d81dbd7d892aa3351efa6719b5db42fdfff0427aee14f1039080dfae847ec6
> - `poc/glm52-probe/results/routing-analysis-v2.json`
>   sha256 e9d6813f99a6efa03645a3c15260a84c3d47221a3d0061ad6bbc68749e1c57cc
>   (the coordinator-run R1–R3 mechanical record)
> - `poc/glm52-probe/interpretation-fable.md`
>   sha256 797cdd6793885727b613b46f5dcd9209b75f1005bf75c50b92d51e2a7aba9e01
> - `poc/glm52-probe/concept_prompts.json`
>   sha256 64df95a0095c892386e9ba71d3cc5be41d957e43cf308348d81eae248e81047f
> - `docs/next/design/glm52-followup-experiment.md`
>   sha256 9f18e5e09f5c8a2a933f3446697daf5849676447004540398237da7f8e67f2b6
>   (§R1.1, §R2, §R-REV4.1, §R-REV5; ASM-2010/2013/2030/2035/2036/2038/2048/2122)
> - `docs/next/design/glm52-f1k-cost-reduction.md`
>   sha256 fe2b5ea29387e9c16598a7cec575614d3ea99a5ae9cd21b07ea65bfefbbc83c0
>   (the standing cost model + the co-location isolation clause, line 30)
> - `poc/gpt56-review/expert-drop-r1/out/last-message.json`
>   sha256 f67aef03254faf3c3336d7edc319fd9565d192979132fb96a22073d0c4d290e4
>   (the FIX-FIRST review this revision answers)
> - `registry/assumptions.jsonl` (central register; tail ASM-2293; GLM-DROP
>   blocks at lines 1082–1091 and 1106–1109)
> - pre-R2 bytes of this document:
>   sha256 1f65f3e908964f1033ea749c03b5f087b14b6162398c8cb2f7b43cbc6f334307
> - issues #27/#28 with comments (as consumed at R0; not re-read this tick)
>
> **[R3] Additional inputs read/produced this tick (full SHA-256):**
> - `poc/gpt56-review/expert-drop-r2/out/last-message.json`
>   sha256 bde94f8510e0ad5e553a22998cbec5514f89ba8ec58926f7264457e3c474e37d
>   (the R2 re-review this revision answers)
> - pre-R3 bytes of this document:
>   sha256 a4d15944ded80445b3144826da4d526c94a92e6bd14dd1f8acdef76ad2f6fd57
> - pre-R3 bytes of `poc/glm52-probe/asm-glm-drop-r2-2340-2352.json`:
>   sha256 780ec24f4451adb8cac6bcf8a9da755e8fb19a7a5f2650771dc167a945840e34
> - `poc/glm52-probe/results/stats/f000.stats..f023.stats` (the 24 committed
>   fingerprints, read in full): pinned via the STATS ROSTER — the ASCII file
>   of lines `fNNN.stats:<file sha256>\n` in ascending filename order — whose
>   sha256 is e90a8d6e32bcd3abe8d4a7ef2334695d82ff5c0dd9670b83a8e853a5115cfcc0
>   (parse cross-checked this tick against routing-analysis-v2.json:
>   16,483 ever-active cells ✓, 10,591 universal ✓, universal_mass_frac
>   0.9392 reproduced as the MEAN of the 24 per-fingerprint fractions ✓)
> - produced (computed outputs pinned in §2.1/§5.2/Appendix A): the realized
>   universal core (sha256
>   632bcd182ae8a716b3f8843d640d43772f9ddfac6880d12ac531cf974cd3f18f), the
>   concept→cluster table (sha256
>   10cb109d651727d89bbb575ae39690e1cb4a0081dd373a9eec139986e7ac5e38), and
>   the planning power-simulation code + output (sha256
>   1dc1682a0cf37cec00b1f0f4444e54c27d6944b2fe70a870b7730b1ec801e3d4 /
>   9cdd2c01d300b648d0ad7c30cdb3320b53731755046b98725e98e82f5ede1769;
>   double-run byte-identical this tick)
>
> **[R4] Additional inputs read this tick (full SHA-256):**
> - `poc/gpt56-review/expert-drop-r3/out/last-message.json`
>   sha256 afcbfe7e83084d2bb238b6c002f1d7b2ea102cd452abc346e7dc5cfa7e69b95a
>   (the R3 re-review this revision answers)
> - pre-R4 bytes of this document:
>   sha256 a8372186d45b07dfa2b2f3678bef739894f001cd5f78f1bb0bab6e6e575e810c
> - pre-R4 bytes of `poc/glm52-probe/asm-glm-drop-r2-2340-2352.json`:
>   sha256 3bf0dd5a83290aa42521fcf6e6e159dba7e9037453e3da2a1e67fd081772431d
> - `poc/glm52-probe/analyze_routing_v2.py` (re-read for the exact
>   normalization/mean-centring construction the [R4] scoring functional
>   pins; its output hashes are already in this table)

---

## 0. Plain-language summary (maintainer-facing)

The P0 probe observed that simply telling GLM-5.2's router to use fewer experts
per token (a one-line environment knob, no kernel anywhere) ran ~1.9× faster at
4-of-8 experts and ~2.5× at 2-of-8 in ONE sequential sweep, with the sampled
answer staying coherent [MEASURED: probe-main.log §"P4 TOPK shrink-lever sweep",
lines 52–71; sha256 in header]. **[R2]** Those speed ratios are PRELIMINARY
systems observations — a single 8→6→4→2 run whose page-cache hit rate rose from
33.0% to 44.9% as it went, not a clean causal estimate (§4.3) — but the
expert-loads-per-token counter (1825.1 → 606.3), which is routing-determined and
cache-independent, is solid. That free knob is the bar. This experiment asks the
only question that earns a kernel sentence on the expert-drop seam: **if we must
drop experts, does dropping the ones the kernel's concept map judges irrelevant
preserve more answer quality than dropping uniformly by router weight — at
exactly the same number of experts computed per token — and more than a
kernel-free "importance" ranking (usage frequency / embedding-topic clusters)
would?** If kernel-guided dropping merely fails to beat those controls at the
registered resolution, the honest reading is "a kernel-specific advantage was
not demonstrated at this resolution," the uniform knob keeps the win, and no
kernel claim is made — and no claim that the kernel "adds nothing" is made
either, because this design powers no equivalence test (§5.3 [R2]). The
experiment rides the same spot-priced instance as the approved-track KaE
experiment (#28) to amortize cost — under the standing sealed-checkpoint /
fresh-process isolation protocol (§6.1 [R2]) — and is scored by cheap prefill
loglikelihood on a public-benchmark subset, not by generation. Nothing here
concludes feasibility; both directions of every gate are worded in advance.

---

## 1. Question, hypothesis, and the deflator crux

**Question [STIPULATED: ASM-2232].** At matched experts-computed-per-token k, on
public multiple-choice QA items restricted to kernel-covered concepts, does
restricting GLM-5.2's per-token expert selection to a *kernel-concept-retained*
candidate set preserve more accuracy than (a) the router's own uniform top-k
truncation over all experts, and (b) an equally-sized kernel-free
expert-importance retained set?

**Hypothesis under test (stated, not asserted).** The router's low-weight tail is
droppable (P0 showed the speed lever moves; its n=2 quality check bounds
nothing), but *which* survivors matter is workload-dependent; a
concept-conditioned candidate set concentrates the survivors on experts that
carry the concepts the item is actually about, so quality degrades less at the
same compute. The pre-named null: router weight is already a sufficient
per-token relevance signal, and any reasonable mask ties — "any drop works."

**The deflator crux (knull discipline, carried from four prior deflations)
[STIPULATED: ASM-2236].** A kernel sentence is licensed ONLY if the kernel-guided
arm beats BOTH:

1. **uniform-TOPK-drop at matched experts/token** — the zero-analysis, kernel-free
   knob whose speed lever P0 observed [MEASURED: probe-main.log §P4, lines
   52–71; the explicit design-amendment recorded in `interpretation-fable.md`
   §1.1]; and
2. **the kernel-free expert-importance baselines at the same retained fraction,
   the same per-item dose, and the same k** — pooled usage-frequency retention
   AND a matched-multilabel embedding-topic-cluster conditioned retention,
   EACH in its own named contrast: the kernel arm must beat **both**, never a
   best-of (or accuracy-selected) comparator [R1: ASM-2293]. The ASM-1977
   knull "kernel-guided helps, not any-structured-drop" discipline is carried
   by the dose-exact label-deranged mask m-drng (§3 [R1: ASM-2290]), which is
   a third mandatory D2 leg.

Anything less is reported with the pre-worded non-demonstration sentences of
§5.3 [R2: ASM-2346] — never as a demonstrated equivalence: a failed superiority
test at this design's resolution (§5.2) licenses "not demonstrated," not
"added nothing."

**What this experiment can and cannot feed.** Quality endpoints feed nothing
until verdict-gen's registered pathway runs; efficiency numbers (realized
loads/token — the ONLY systems endpoint, §4.3 [R2: ASM-2348]) are descriptive
systems observations. No outcome moves the EFFICIENCY or CORRECTNESS synthesis
verdicts, which remain INCONCLUSIVE-PENDING under their own experiments.
[STIPULATED: ASM-2236]

---

## 2. The concept→expert map — mechanism, and its honestly-stated scope

### 2.1 Construction [STIPULATED: ASM-2233; core algorithm R2: ASM-2343]

Built offline, CPU-only, from the committed P0 fingerprints
(`poc/glm52-probe/results/stats/`, 24 prompts spanning **8 concept clusters**,
3 prompts/cluster, with per-layer expert-usage histograms [R1: ASM-2291;
measured facts consolidated R2: ASM-2342]):

1. **Universal core (always retained) — FROZEN ALGORITHM [R2: ASM-2343].**
   10,591 of 16,483 ever-active (layer, expert) cells are active in all 24
   fingerprints, carrying 93.92% of histogram mass [MEASURED:
   routing-analysis-v2.json keys `/universal_cells` = 10591, `/keyspace` =
   16483, `/universal_mass_frac` = 0.9392; sha256 in header] — an average of
   ~139 universal cells per MoE layer (10,591 across **76** MoE layers —
   layers 3–78 in the committed stats files; the R0–R2 "75 MoE layers /
   ~141/layer" figure was a miscount, corrected [R3, MEASURED: stats roster,
   sha256 in header; layer indices re-derived this tick]; the 0.9392 is the
   MEAN of the 24 per-fingerprint universal-mass fractions — the pooled-mass
   fraction is 0.9303, computed this tick, stated for precision), so "retain
   all universal cells" is IMPOSSIBLE inside a 64-expert/layer budget;
   the core is necessarily a strict subset, and the R1 text deferring its size
   to pilot is superseded. The frozen rule, per MoE layer ℓ: rank all 256
   experts by pooled trace mass (sum over all 24 fingerprints), descending;
   ties broken by ascending expert index; core(ℓ) = the shortest prefix whose
   cumulative mass ≥ **50% of layer ℓ's pooled mass**, hard-capped at
   **48 experts** (75% of the 64-expert budget), guaranteeing ≥16 slots/layer
   for the concept-conditional tail. τ = 0.50 and cap 48 are a-priori design
   constants (rationale in ASM-2343), not tuned quantities. The identical
   core bytes are embedded in EVERY masked arm.
   **[R3 — review-2 finding 2 closed: the core is MATERIALIZED, not
   deferred.]** The rule above was EXECUTED this pass (CPU-only, ~$0) on the
   24 committed fingerprints (stats roster sha256
   e90a8d6e32bcd3abe8d4a7ef2334695d82ff5c0dd9670b83a8e853a5115cfcc0, header).
   Realized core [MEASURED: computed this tick from the roster-pinned bytes
   by the frozen rule; double-checked against the pinned
   `/universal_cells`/`/keyspace` parse]: **76 layers; total 2,108 core
   cells; per-layer sizes min 15 / max 46 / mean 27.7; NO layer reaches the
   48 cap**, so every layer keeps ≥ 64 − 46 = 18 concept-tail slots (the ≥16
   guarantee holds with margin). Canonical serialization (frozen): one ASCII
   line per MoE layer in ascending layer order, `"<layer>:" + comma-joined
   ascending retained expert indices + LF`; the canonical core's sha256 is
   **632bcd182ae8a716b3f8843d640d43772f9ddfac6880d12ac531cf974cd3f18f**.
   Per-layer sizes (layers 3→78): 31, 42, 41, 45, 45, 40, 44, 36, 30, 28,
   37, 33, 23, 25, 20, 19, 17, 15, 23, 22, 35, 31, 31, 37, 33, 23, 24, 27,
   22, 23, 19, 19, 19, 19, 22, 23, 18, 20, 19, 29, 21, 18, 27, 27, 24, 24,
   26, 24, 24, 20, 25, 30, 27, 27, 30, 30, 21, 26, 28, 28, 25, 24, 36, 22,
   28, 30, 26, 22, 30, 25, 35, 36, 34, 36, 37, 46. The freeze manifest
   copies this hash verbatim; the freeze-time regeneration must be
   byte-identical (mismatch = halt, fail-closed) — the pin exists NOW and
   freeze only re-verifies it.
2. **Concept-conditional tail.** For each concept cluster c, rank the remaining
   experts per layer by their mean-centred conditional mass (the residual space
   where concept separation actually lives: within 0.9119 vs across −0.0740,
   perm p = 0.0001 [MEASURED: routing-analysis-v2.json keys
   `/mean_centered/within`, `/mean_centered/across`,
   `/mean_centered/perm_p_10k`; sha256 in header]). An item's
   active concepts come from the same harness-side lexical trigger map (G-lex)
   that F1-K uses — no router signal is consumed for gating (G-route stays
   unsupported per `interpretation-fable.md` §4). The kernel-concept →
   trace-cluster correspondence is a frozen deterministic table [R2:
   ASM-2340], **MATERIALIZED and hashed HERE [R3 — review-2 finding 1
   sub-item]**: the trace clusters ARE the 8 probe concepts of
   `concept_prompts.json` (sha256 in header), in file group order, with the
   fingerprint roster read from probe-main.log §P3. Canonical serialization
   (frozen): one ASCII line per cluster,
   `"<cluster index>:<concept id>:<comma-joined fingerprint ids>" + LF`:
   `0:break.shatter:f000,f001,f002` / `1:break.violate:f003,f004,f005` /
   `2:break.interrupt:f006,f007,f008` / `3:bank.river:f009,f010,f011` /
   `4:bank.finance:f012,f013,f014` / `5:animal:f015,f016,f017` /
   `6:finance:f018,f019,f020` / `7:mathematics:f021,f022,f023`; table sha256
   **10cb109d651727d89bbb575ae39690e1cb4a0081dd373a9eec139986e7ac5e38**. A
   G-lex concept maps to cluster c iff it IS concept c of this table (or, at
   an expanded F1-K trigger inventory, iff F1-K's frozen trigger map declares
   it an alias of concept c — an item with ANY active concept outside this
   table is INELIGIBLE, §5.1); the freeze manifest copies this hash verbatim,
   fail-closed on mismatch.
3. **Retained set R_kern(item, f) — MULTILABEL COMBINATION RULE PINNED [R4 —
   review-3 finding 3; ASM-2344 as R4-amended].** Per layer: universal core ∪
   the top experts of ONE summed-score ranking, filled to exactly f·256
   experts. The rule, fully executable and deterministic:
   - **Per-cluster score (the scoring functional).** For fingerprint f, let
     x_f(ℓ,e) = f's histogram mass at cell (ℓ,e) over the 16,483-cell
     ever-active keyspace, L1-normalized over ALL cells jointly (exactly the
     `analyze_routing_v2.py` construction behind the pinned
     `/mean_centered/*` numbers; absent cells = 0; cells outside the
     keyspace = exactly 0.0). Let μ(ℓ,e) = the elementwise mean of x_f over
     the in-scope fingerprint roster (all 24; under leave-one-out below, the
     reduced roster), summed in ascending fingerprint-id order then divided
     by the roster size, float64. For concept cluster c with member set F_c
     (its fingerprints per the frozen §2.1 table; reduced under
     leave-one-out): s_c(ℓ,e) = [Σ_{f∈F_c, ascending fingerprint id}
     x_f(ℓ,e)] / \|F_c\| − μ(ℓ,e) — the mean-centred conditional mass.
   - **Combination (multiple active concepts).** S_item(ℓ,e) =
     Σ_{c ∈ C(item)} s_c(ℓ,e), a PLAIN UNWEIGHTED float64 sum over the
     item's active concepts in ascending frozen-table cluster-index order —
     no per-concept quota, no max, no normalization by \|C(item)\|
     (cardinality is matched across the item-conditioned arms, so a constant
     factor cannot change any ranking). For \|C(item)\| = 1 this reduces to
     the single-concept ranking verbatim.
   - **Fill and trim.** Per layer ℓ: rank all experts e ∉ core(ℓ) by
     S_item(ℓ,e) descending (exact float64 comparison); ties → ascending
     expert index [R2: ASM-2344]; retain core(ℓ) ∪ the first
     64 − \|core(ℓ)\| experts of that ranking — exactly 64/layer, always
     well-defined (every non-core expert carries a score, 0.0 if never
     active; the tie-break makes the order total). There is no other trim
     step: the core is fixed (§2.1 item 1) and the tail is one ranked
     prefix, so no union-of-top-r ambiguity exists.
   Leave-one-out within concept clusters wherever a test item's
   cluster has trace coverage from its own prompts (n=3/cluster [R1:
   ASM-2291]), so no item is scored against a map built from itself; under
   LOO, F_c and μ are recomputed over the reduced roster by the same
   formulas (deterministic — no other quantity changes).

### 2.2 Scope, honestly [STIPULATED: ASM-2233]

- **Kernel-specificity is OPEN.** The R4 replay legs (M_oracle, M_kernel — the
  oracle/kernel-vs-deflator pin quantities specified in
  `interpretation-fable.md` §2) have **never been computed**; the branch
  classifier (ASM-2013) is legitimately HELD. What IS mechanically on the record
  (routing-analysis-v2.json) shows concept-shaped routing structure exists
  (p = 0.0001 under the registered 10k-shuffle test) — it does NOT show that
  kernel labels exploit it beyond an embedding-topic conditioner. On the
  programme's four-deflation record, a kernel≈embedding tie is the outcome that
  record makes most likely (designer prior, binding nothing; resolved by D2
  itself — no tag, per the closed schema [R2]). This design treats it as an
  open empirical question, prices it with its own arm (m-emb), and requires R4
  to land before main-phase spend (§7).
- **Concept-vs-lexical confound unresolved.** 3 prompts/concept share content
  words; sense minimal-pairs argue against a purely surface account (break
  centred Δ +0.1955, perm p 0.0029; bank Δ +0.3259 at its n=6 permutation floor
  p 0.1026 [MEASURED: routing-analysis-v2.json keys
  `/sense_pairs_centered/break/*`, `/sense_pairs_centered/bank/*`; sha256 in
  header]) but surface-disjoint discrimination is
  F1-A's job, not this experiment's. Claims are scoped accordingly.
- **Map coverage is 8 concept clusters (24 prompts, 3/cluster) on one box
  [R1: ASM-2291; measured record R2: ASM-2342].** The earlier "~24 concepts"
  wording overstated this: the unit the map can condition on is the CLUSTER,
  and there are eight. Every claim in this design that rests on the count is
  scoped to C = 8 — in particular the cluster-aware inference and its power
  floor, re-derived in §5.2 [R1: ASM-2292; split and re-frozen R2:
  ASM-2340/2341]. Items whose active concepts lack trace coverage cannot get a
  kernel mask: the frozen eligibility rule, exclusion accounting, and
  coverage gates are in §5.1 [R2: ASM-2340].
- **Sense-level shards are NOT assumed.** Sense-granular retained sets are
  admissible only if the held classifier lands A1; otherwise word-level concepts
  only (ASM-2013 A1/A2 carried).

---

## 3. Arms [STIPULATED: ASM-2232; masked-arm dose protocol R1: ASM-2290; m-freq scope + frozen parameters R2: ASM-2343/2344]

All at the same operating point k\* (experts computed per token per MoE layer,
§4.2) and, for masked arms, the same retained fraction f = 0.25 per layer
(64/256; primary — f is a design constant, not a search dimension). Mechanism:
a per-item, per-layer candidate bitmask (the item-ID→mask table sidecar, §6.3
[R2: ASM-2349]) restricts the router's candidate set; the router then takes its
own top-k\* among survivors. Uniform arm is the unrestricted knob colibri
already exposes.

| Arm | Candidate set | Selection | What it isolates |
|---|---|---|---|
| **b0-full** | all 256/layer | TOPK=8 (config default) | retention reference |
| **u-topk** | all 256/layer | TOPK=k\* | uniform router-weight drop — deflator 1 (the P0 lever) |
| **m-drng** [R1; R2: R=3 realizations] | per-item: universal core ∪ concept-conditional fill under a seeded LABEL DERANGEMENT — item i is masked with item σ(i)'s active-concept set, σ a set-distinct derangement within strata of equal label-set cardinality (§3.1), so \|labels\| is preserved per item; **the fill is the §2.1 item 3 summed-score rule VERBATIM applied to σ(i)'s concept set [R4]**; exactly f·256/layer; **R = 3 preregistered realizations** (seeds §3.1) | TOPK=k\* among survivors | dose-exact structured mask with WRONG labels — the knull analog (replaces m-rand); D2 leg 3 |
| **m-freq** | universal core ∪ top experts by pooled trace usage mass, filled to exactly f·256/layer (the core is the head of the pooled ranking; stated explicitly for dose-exactness) | TOPK=k\* among survivors | kernel-free importance — **dose- and core-matched but intentionally item-UNCONDITIONED: m-freq consumes NO per-item labels; the matched-multilabel clause applies to m-kern/m-emb/m-drng only [R2: ASM-2343]** — deflator 2a; D2 leg 1 |
| **m-emb** [R1] | per-item: universal core ∪ top experts by SUMMED mean-centred embedding-cluster-conditional mass over the item's top-\|C(item)\| nearest clusters — **the §2.1 item 3 rule VERBATIM with the k-means cluster member sets (§3.1 item 2) in place of the concept-cluster member sets, summed in ascending k-means cluster-index order, same descending ranking, same ascending-expert-index tie-break, same fill-to-64 [R4 — review-3 finding 3]** — MATCHED MULTILABEL: the same number of conditioning labels as m-kern's active-concept set for that item (pinned encoder + clustering, §3.1; no kernel anywhere); exactly f·256/layer | TOPK=k\* among survivors | kernel-free CONDITIONED importance — deflator 2b; D2 leg 2 |
| **m-kern** | R_kern(item, f) per §2.1 — universal core ∪ concept-conditional fill for the item's \|C(item)\| active concepts; exactly f·256/layer | TOPK=k\* among survivors | the kernel arm |

**Dose-exact mask protocol [R1: ASM-2290; m-freq scope corrected R2: ASM-2343].**
The R1 review found the masked arms were not dose-matched. Fixed as a
construction invariant: every masked arm retains EXACTLY f·256 = 64 experts per
layer; every mask includes the SAME universal core; and per-item multilabel
structure is matched across the item-conditioned arms — m-kern conditions on
the item's \|C(item)\| active concepts, m-emb on the item's top-\|C(item)\|
nearest embedding clusters, m-drng on a same-cardinality deranged label set
drawn from the same concept inventory. **[R2]** Across the three
item-conditioned arms (m-kern / m-emb / m-drng) only the selection criterion
differs — dose, core, and per-item label-set cardinality do not; m-freq shares
the dose and the core but, by design, has NO per-item conditioning (that is
what makes it the workload-blind importance deflator). Dose is verified
mechanically: the run manifest records per-item, per-layer retained-set sizes
for every masked arm, and any inequality VOIDs the affected contrast (never
reinterpreted — the §4.1 discipline extended to mask dose). m-drng is what
licenses "kernel-guided helps" over "any-structured-drop helps": identical
pipeline, identical dose, identical structure, wrong labels.

Notes: m-emb, m-drng, and m-kern are structurally identical pipelines differing
only in the conditioning signal (matched-cardinality embedding clusters vs
deranged concept labels vs kernel concept labels) — this is deliberate; it is
the only construction that can attribute anything to the kernel labels
themselves. **[R4]** That identity is now LITERAL: all three arms use the ONE
scoring functional and the ONE multilabel combination rule of §2.1 item 3
(per-cluster mean-centred conditional mass; plain unweighted sum over the
item's conditioning clusters in ascending cluster-index order; single
descending ranking; ascending-expert-index tie-break; fill to exactly 64);
only the cluster MEMBER SETS and the item→label assignment differ. No
per-arm combination freedom exists. The retained-set Jaccard non-distinctness gate is defined precisely
in §3.1 [R2: ASM-2344]; a gated pair renders its D2 leg UNINFORMATIVE rather
than a tie.

### 3.1 Frozen mask-construction parameters [R2: ASM-2344 — review finding 3]

Every previously open, outcome-relevant arm choice is pinned here; anything not
listed is a config error that halts at bring-up. All seeds are enumerated in
the freeze manifest, disjoint from F1-K's seed sets.

1. **Embedding encoder (m-emb).** `sentence-transformers/all-MiniLM-L6-v2`,
   CPU inference, weights content-hash pinned in the freeze manifest at
   prereg-freeze (the exact artifact hash is a freeze-manifest entry — no
   floating revision). **[R3 — fail-closed default stated, review-2 finding
   3.]** The weight artifact is NOT repo bytes (verified this tick: no local
   copy exists), so this is an explicitly SEQUENCED-AT-FREEZE pin, not an
   open hole: at prereg-freeze the artifact files (`model.safetensors` +
   config + tokenizer files, enumerated) are fetched, each file's sha256
   recorded in the freeze manifest, and every m-emb embedding is computed
   from exactly those bytes; a missing, changed, or unhashable artifact
   HALTS the freeze (m-emb is never built from unpinned weights, and D2 leg
   (b) is never silently waived — an unresolvable artifact returns the
   design to the maintainer). Input text: the item's question stem VERBATIM
   (exactly the text G-lex scans; answer options excluded), Unicode
   NFC-normalized, internal whitespace collapsed to single spaces, stripped;
   NO case-folding. Output embedding L2-normalized. The same rule embeds the
   24 trace prompts (their `concept_prompts.json` prompt text).
2. **Trace-corpus clustering (m-emb).** k-means, k = 8, kmeans++ init, seed
   20260724, n_init = 10 (lowest inertia wins; exact tie → lowest init index),
   max_iter = 300, on the 24 L2-normalized trace-prompt embeddings. Cluster
   centroids = member means, L2-renormalized. **[R3 — implementation pinned,
   review-2 finding 3: NO library k-means]** (library RNG streams and
   tie-handling are version-dependent): the harness's OWN implementation to
   this frozen spec — float64 throughout; distances = squared Euclidean (on
   L2-normalized vectors this induces the cosine ordering); kmeans++ per
   init index r ∈ {0..9} on DRBG stream `kmeans:20260724:<r>` (item 8; the
   seed rides in the stream label): first centre
   = uniform draw on [0, 24); each next centre by the standard D²-weighted
   rule, one DRBG uniform on [0,1) against the cumulative D²/ΣD² in
   ascending prompt-index order; Lloyd iterations with assignment ties → the
   lowest centroid index; centroid = member mean, L2-renormalized; an empty
   cluster is re-seeded with the point of largest D² (tie → lowest prompt
   index); convergence = assignments unchanged, cap max_iter = 300; inertia
   compared as exact float64, lowest wins, tie → lowest init index. The
   realized assignment and centroids are frozen + hashed at prereg-freeze
   (SEQUENCED-AT-FREEZE: they are a pure function of the weight bytes pinned
   in item 1 and this spec — computable the moment the weights hash lands).
3. **Nearest-cluster rule (m-emb).** Item→cluster affinity = cosine(item
   embedding, centroid); the item's conditioning set = the top-\|C(item)\|
   clusters by descending cosine; ties → lower cluster index. **[R4 —
   review-3 finding 3: how MULTIPLE nearest clusters combine into ONE
   mask.]** The conditioning set enters the §2.1 item 3 rule verbatim:
   per layer, per non-core expert, the score is the PLAIN UNWEIGHTED
   float64 SUM of the per-cluster mean-centred conditional masses
   s_g(ℓ,e) over the conditioning set's clusters in ascending k-means
   cluster-index order, where cluster g's member set is its frozen
   k-means assignment (item 2) and x_f/μ are the §2.1 item 3 quantities
   over the full 24-fingerprint roster (no leave-one-out arises: benchmark
   items are never trace prompts of an embedding cluster); rank
   descending, ties → ascending expert index, fill core ∪ top experts to
   exactly 64. Cosine affinities pick WHICH clusters condition; they
   carry NO weight in the score (affinity-weighted variants are
   explicitly rejected — one more tunable would be one more degree of
   freedom). No ambiguity that changes the realized mask remains.
4. **Derangement policy (m-drng).** R = 3 preregistered realizations, seeds
   20260721 / 20260722 / 20260723. Unit deranged: the item → active-concept-SET
   assignment, within strata of equal label-set cardinality. Each realization:
   seeded Fisher–Yates shuffle within the stratum, rejection-resampled (max
   10,000 attempts, then fail-closed halt) until the permutation is (a)
   fixed-point-free AND (b) SET-DISTINCT — σ(i)'s label set must differ from
   item i's label set AS A SET, which prevents identical "wrong"-label sets.
   **[R3 — PRNG pinned, review-2 finding 3:]** "seeded Fisher–Yates" means
   the GLM-DROP-DRBG of item 8, stream `drng:<seed>:<cardinality>:<attempt>`
   — no library PRNG; strata processed in ascending label-set-cardinality
   order, items within a stratum in ascending byte-lexicographic item-ID
   order; Fisher–Yates from j = m−1 down to 1, swap with r uniform on
   [0, j+1]; the attempt counter increments on every failed (a)/(b) check.
   The three realized permutations are a PURE FUNCTION of (eligible-item
   list, these seeds, this DRBG); they are materialized and their canonical
   serializations hashed into the freeze manifest at prereg-freeze —
   SEQUENCED-AFTER-F1-K-FREEZE, because the eligible-item list derives from
   F1-K's frozen id lists and span sidecars (§5.1), which are not yet repo
   bytes (verified this tick). Not an open hole: function frozen here,
   inputs named, output hash committed at freeze, mismatch = halt.
   **Impossible strata:** items in strata where no valid assignment exists
   (singleton cardinality strata, or strata whose items all share one label
   set) are EXCLUDED from m-drng only, counted in the manifest; if such
   exclusions exceed 10% of eligible n, D2 leg (c) is declared UNINFORMATIVE
   (never silently narrowed). D2(c) is evaluated paired on the non-excluded
   subset, m-kern restricted to the same items for that contrast.
5. **Jaccard non-distinctness gate — aggregation defined.** For an arm pair,
   J(i, ℓ) = \|A∩B\|/\|A∪B\| over the two retained sets at item i, MoE layer ℓ;
   the GATE statistic is the mean of J(i, ℓ) over all eligible items and all
   MoE layers (for m-drng: pooled over the 3 realizations). Gate: mean > 0.95
   ⇒ the pair is non-distinct ⇒ that D2 leg is UNINFORMATIVE. Per-layer means
   and the per-item MAX distribution are reported descriptively (they do not
   gate).
6. **Load-gate matching level (completes §4.1).** The ±5% gate compares
   ARM-LEVEL MEANS: mean realized experts-loaded/token over the arm's full
   scored item set vs u-topk's mean over the identical items. Per-item ratios
   are reported descriptively. Violation VOIDs the arm's contrasts.
7. **TOPP branch: REMOVED [R2 — review finding 3, removal option taken].**
   The R1 escalation step "TOPP-tightened k=2" carried no TOPP value or
   selection rule; rather than freeze a grid this design does not need, the
   branch is deleted. Escalation order in §4.2 is k=1 ONLY, then STOP.
8. **GLM-DROP-DRBG + named seed registry [R3 — review-2 finding 3].** ALL
   run-time seeded randomness in this design (k-means++ draws, derangement
   shuffles, block-order shuffles, the correctness spot-set draw) uses ONE
   primitive, defined here so no library or version floats: for ASCII stream
   label L and draw counter t = 0, 1, 2, …, the raw draw is u_t = the first
   8 bytes, big-endian unsigned, of SHA-256(ASCII `glm-drop:` ‖ L ‖ `:` ‖
   decimal(t)). Uniform integer on [0, k): accept u_t iff
   u_t < 2^64 − (2^64 mod k) and return u_t mod k, else advance t (rejection
   kills modulo bias; the counter never resets within a stream). Uniform on
   [0, 1): u_t · 2^−64. House style: SHA-256 over fixed labels, zero PRNG
   dependencies (the encoder pin's own discipline). SEED REGISTRY (all
   named, all freeze-manifest entries; no other seed exists in this design;
   disjointness from F1-K's registered seed sets re-verified mechanically at
   freeze): 20260721/20260722/20260723 = m-drng realizations 1–3 (item 4);
   20260724 = trace clustering (item 2; stream `kmeans:20260724:<init>`);
   20260725 = pilot item bootstrap (§4.2); **20260726 = item-block-order
   shuffles (§4.3; stream `blocks:20260726:<arm>:<pass>`)**; **20260727 =
   the seeded 8-item correctness spot set (§4.3; stream
   `spotset:20260727`)**; every seed enters the DRBG through its stream
   label, decimal-rendered;
   20260728 = the pinned planning power simulation (§5.2, Appendix A — a
   pinned code artifact with its own internal counter-based generator,
   pinned by code + output hash rather than by this DRBG). Anything drawing
   randomness outside this registry is a config error and halts at bring-up.

---

## 4. Matched-experts protocol [STIPULATED: ASM-2234; pilot R2: ASM-2345; regimes R2: ASM-2348]

### 4.1 The matched quantity

Primary matched quantity: **realized experts-loaded-per-token**, read from the
engine's own counter (the `experts loaded/token` line: 1825.1 at TOPK=8, 998.9
at TOPK=4, 606.3 at TOPK=2 [MEASURED: probe-main.log §P4, counter lines 57 /
67 / 71; sha256 in header]) — this is the physical cost (expert I/O + matmul),
it is routing-determined (cache-state-independent), and it correctly absorbs
MTP union-loading across speculative drafts. All non-full arms run at the same
k\*, so nominal experts-computed/token match by construction; the realized
counter is the verification. **Match gate:** arm-level mean within ±5% of
u-topk's mean on identical items (aggregation frozen in §3.1 item 6 [R2]),
else the affected arm is VOID (not reinterpreted). With f = 0.25,
survivors/layer (64) ≫ k\* — no layer can run short; a short layer (impossible
unless f·256 < k\*) is a config error and halts.

### 4.2 Operating-point selection (pilot, dev-only) [R2: ASM-2345 — review finding 5]

The comparison is only informative where uniform dropping actually costs
quality — P0's coherence at TOPK=4 warns that k=4 may be quality-free on easy
items [MEASURED: probe-main.log §P4 lines 63–67; the n=2 factual check is too
small to call either way, `interpretation-fable.md` §1.1].

**Dev panel [R2].** The R1 pilot read 24 dev items — 4.17-pt accuracy
increments, making "≥3-pt deficit" a one-item rule. Replaced: the pilot panel
is **F1-K's frozen dev-96 split, reused verbatim** (id-list hash pinned in the
freeze manifest; stratified across F1-K's concept clusters by construction),
with the GLM-DROP-eligible subset (§5.1 rule) identified and reported.
**Gate:** ≥48 eligible dev items, else the pilot returns to the maintainer
before any further spend. The pilot statistic is computed on the eligible
subset; its granularity (100/n_dev-eligible points per item; ≈1.04 pts at 96)
is disclosed next to every pilot number.

**Selection rule (deterministic, frozen) [R2].** Run b0-full and u-topk at
k ∈ {4, 3, 2} on the dev panel. Primary pilot statistic: the dev accuracy
deficit acc(b0-full) − acc(u-topk@k) on eligible items. **k\* = the largest k
whose dev deficit is STRICTLY > 3.0 points** — aligned with D0, which
floor-binds at test deficit ≤ 3.0 (exactly-3 is insufficient in BOTH places;
the R1 strict/non-strict mismatch is gone). Escalation if no k qualifies:
k = 1 (one further cell); the TOPP branch is removed (§3.1 item 7). If NO
tested operating point shows a dev deficit > 3.0 points, **STOP and report**:
"no uniform-truncation deficit > 3 points was observed on the dev panel at
k ∈ {4, 3, 2, 1}" — a kernel-free efficiency datum scoped to the panel and
tested k values (NOT a claim that truncation is retention-free; that would be
an unpowered equivalence claim, §5.3 [R2]); the guided-drop question is then
unanswerable here (no measured deficit exists for guidance to recover) and
returns to the maintainer with that datum. Both directions pre-worded.

**Uncertainty (reported, non-gating) [R2].** Alongside the accuracy deficit,
the pilot reports a prespecified CONTINUOUS statistic with uncertainty: the
mean paired difference in correct-option log-likelihood margin, margin(arm, i)
= LL(correct option) − max over wrong options LL(wrong), between b0-full and
u-topk@k, with a seeded (20260725) 10,000-draw nonparametric item bootstrap
90% CI. If the continuous statistic's sign disagrees with the accuracy-rule
selection at k\*, the pilot surfaces to the maintainer BEFORE freeze instead
of proceeding (fail-closed). Dev selection may choose k\*; every rule above is
frozen before any test access. [STIPULATED: ASM-2345]

### 4.3 Instrument settings — correctness regime vs performance regime [R2: ASM-2348 — review finding 7]

Carried from ASM-2028 discipline: DRAFT=0 (greedy, deterministic scoring);
PILOT off; AUTOPIN/.coli_usage off in all arms (no adaptive routing/pinning
state anywhere); DIRECT off; item order randomized and seeded at block level
(seed 20260726, DRBG stream `blocks:20260726:<arm>:<pass>` [R3 — previously
unnamed, review-2 finding 3]); arm order rotated per item block; every run
emits a committed manifest (binary
hash, mask-table hash, knob values, per-item realized-loads counters, seeds).
Knob semantics re-verified from the checkout at bring-up; any surprise halts
for a protocol amendment BEFORE data collection. [STIPULATED: ASM-2234]

**[R2] The R1 text was contradictory (fresh caches at arm boundaries in §4.3
vs warm-cache/pinning in §6.2). Resolved by SEPARATING the regimes:**

- **Correctness regime.** Scoring must be cache-state independent — and that is
  now VERIFIED, not asserted: at bring-up, a seeded 8-item spot set (seed
  20260727, DRBG stream `spotset:20260727`, drawn without replacement from
  the eligible dev items [R3 — previously unnamed, review-2 finding 3]) is
  scored
  twice per condition — cold (fresh process, caches dropped) and warm (after
  preload) — and the per-option logits must be BYTE-IDENTICAL; any mismatch
  halts for a protocol amendment. Given that check passes, page-cache state
  during scored runs is unconstrained (it is a cost lever only), AUTOPIN stays
  off, and the PIN set — the universal core, and nothing selected by pilot
  outcomes — is IDENTICAL across all arms (including b0-full and u-topk) and
  recorded in the manifest, so no arm sees a pin policy another arm does not.
- **Performance regime.** **Realized experts-loaded/token is the ONLY systems
  endpoint of this experiment.** It is read from the deterministic counter and
  is cache-independent. Arm-level tok/s comparisons are explicitly DECLINED:
  cache/pinning state, arm order, and prompt-length variation confound them,
  and this design does not include the replicated fixed-length balanced-order
  protocol that clean tok/s attribution would need. The R1 "≤3-prompt seeded
  generative tok/s spot-check per arm" is REMOVED. The P0 1.9×/2.5× tok/s
  ratios are cited only as PRELIMINARY observations from one sequential
  8→6→4→2 run with monotonically rising hit rate (33.0% → 38.8% → 41.8% →
  44.9% [MEASURED: probe-main.log §P4 lines 56 / 61 / 66 / 70; sha256 in
  header]) — never as causal arm-level estimates. If a future pass wants
  arm-level throughput claims, it must preregister the full protocol the
  review specified (replicated fixed-length prompts, balanced arm order,
  identical RAM budgets, fixed reset/preload/warm-up rule, exclusion of
  warm-up/interrupted blocks, uncertainty intervals); this design does not.

---

## 5. Quality endpoint, statistics, decision rule

### 5.1 Endpoint, items, and the frozen analysis population [STIPULATED: ASM-2235; population frozen R2: ASM-2340 — review finding 1]

- **Item pool:** the F1-K known-concept subset, reused verbatim (MMLU filtered
  by the G-lex trigger map, supplemented mechanically from the
  ARC-Easy/Challenge / OpenBookQA / CommonsenseQA pool; ASM-2030/2038
  machinery) — the same items, the same frozen splits (test-1440 / dev-96 id
  lists), the same frozen scorer. Dev = F1-K's dev split (pilot only, §4.2);
  test untouched until arms freeze. Reuse is deliberate: it amortizes subset
  construction AND scores the drop arms on exactly the concept-covered
  workload the map exists for.
- **Eligibility rule (frozen, deterministic) [R2].** An item is ELIGIBLE iff
  its G-lex active-concept set is non-empty AND every active concept maps to a
  trace-covered cluster under the frozen concept→cluster table (§2.1 —
  MATERIALIZED at R3, sha256 10cb109d…7ac5e38). There
  is NO sampling step: **n = \|eligible test items\|, exactly** (≤ 1,440 by
  construction). At prereg-freeze the eligible-item ID list, its SHA-256, the
  exact n, the per-analysis-cluster counts m_c, and the exclusion count are
  all committed to the freeze manifest. **[R3 — review-2 finding 1: this is
  an explicitly SEQUENCED-AFTER-F1-K-FREEZE PIN, not an open hole.]** The
  eligible set is a pure function E(F1-K test-1440 id list, F1-K trigger-map
  version + per-item span sidecars, the §2.1 table); the first two inputs
  are F1-K freeze artifacts that DO NOT YET EXIST as repo bytes (verified
  this tick: no dev-96/test-1440 id-list file, trigger-map hash, or span
  sidecar is committed anywhere in the repo — they are produced by F1-K's
  own kot-reg/1 freeze under #28). GLM-DROP therefore CANNOT hash its
  population before F1-K's freeze lands, by construction and not by
  omission; the function, its inputs, its gates, and the fail-closed
  behaviour (no eligible-ID hash in the manifest ⇒ freeze cannot complete ⇒
  no spend) are all frozen HERE, and §6.1 step 5 already orders GLM-DROP's
  freeze before F1-K's test OUTCOMES, so the sequencing is
  F1-K-freeze → GLM-DROP-freeze → any test outcome. **Coverage gates (all fail to the
  maintainer BEFORE main-phase spend, MD-6):** exclusions > 20% of the test
  pool; n < 300; any of the 8 analysis clusters with m_c < 10 (an empty or
  thin cluster shrinks C and invalidates the §5.2 power basis — it is
  surfaced, never absorbed silently).
- **Scoring:** one prefill per item per arm with the frozen candidate-independent
  label-token template (F1-K §R1.1); per-option loglikelihood, argmax = answer.
  Generative benchmarking is unaffordable at 0.09–0.25 tok/s (ASM-1988 carried).
- **Primary endpoint:** per-item correctness, paired across arms (identical
  items). The licensing statistic is CLUSTER-BALANCED (§5.2); the item-weighted
  accuracy contrast Δ(arm) = acc(arm) − acc(b0-full) is reported descriptively
  alongside it.
- **Efficiency observations (descriptive only) [R2: ASM-2348/2351]:** realized
  loads/token per arm (the only systems endpoint); **per-mask routed-expert
  footprint** per arm. The R1 "projected deployment shard size f × 370 GB ≈
  93 GB" claim is WITHDRAWN (review finding 10): a per-item 25% mask does not
  imply a single deployable shard — the UNION footprint across the frozen
  workload's per-item masks is what a shard or page-cache claim would need,
  and it is MEASURED at pilot and reported before any such claim is made.
  No shard-size or page-cache-pool claim attaches to this experiment.

### 5.2 Statistics and power [R2: ASM-2340 (inference) + ASM-2341 (planning projections) — review finding 1; supersedes the R1 ASM-2292 record and ASM-2235's statistics clause]

**Analysis clusters and the multilabel rule (frozen; made EXECUTABLE at R3 —
review-2 finding 1 sub-item).** Unit of inference
= the trace concept cluster, C = 8. Deterministic multilabel→analysis-cluster
assignment: every eligible item i gets EXACTLY ONE analysis cluster A(i).
**[R3]** The R2 phrase "highest G-lex trigger score" was not executable
(G-lex is a phrase matcher; it emits matched spans, not a scalar). Replaced
by the executable rule, which imports F1-K's REGISTERED span-precedence rule
(longest trigger match → earliest span start → lowest concept id,
`glm52-followup-experiment.md` §"Gate resolution") verbatim: over all G-lex
trigger spans of item i in F1-K's frozen per-item span sidecar, A(i) = the
cluster of the active concept owning the span with (a) the LONGEST matched
trigger surface (in Unicode code points of the frozen template text); tie →
(b) the EARLIEST span start offset; tie → (c) the concept EARLIEST in the
frozen §2.1 concept→cluster table order. No scalar score exists or is
needed; every input is a frozen artifact and every comparison is total.
Eight map clusters therefore yield at most eight non-overlapping analysis
clusters by construction; the realized non-empty count and the m_c are
committed at prereg-freeze (§5.1 — the same sequenced-after-F1-K-freeze pin
as n), and the m_c ≥ 10 gate protects the basis.

**Estimand (frozen) [R2].** For a named contrast (arm X vs arm Y): per-item
d_i = 1{X correct on i} − 1{Y correct on i}; per-cluster mean D_c =
mean_{i∈c} d_i; the estimand is the CLUSTER-BALANCED mean θ = (1/8)·Σ_c E[D_c],
in accuracy points (×100). The +3-point effect floor applies to this estimand's
statistic T = mean_c D_c — NOT to the item-weighted accuracy difference, which
is reported descriptively and may differ when cluster sizes are unequal
(disclosed in the report whenever the two disagree in magnitude).

**Exact inference (frozen) [R2].** With C = 8, the cluster sign-flip reference
set is ENUMERATED IN FULL: all 2^8 = 256 sign vectors s ∈ {±1}^8, one-sided
p = #{s : T(s) ≥ T_obs} / 256 (identity included). No Monte-Carlo resampling
(the R1 "10,000 resamples" is superseded — it would approximate a set we can
enumerate). Attainable p-values are k/256; the registered rule "reject iff
p ≤ 0.05" therefore operates at effective size 12/256 ≈ 0.0469 (conservative;
disclosed). Licensing per named contrast remains the JOINT rule: p ≤ 0.05 AND
observed T ≥ +3 points.

**Exchangeability basis + fallback — IMPORTED from F1-K [R2].** The test's
validity basis is F1-K's registered sign-symmetry assumption (ASM-2122 /
`glm52-followup-experiment.md` §R-REV4.1a), carried verbatim: under the sharp
null of no differential effect, each cluster mean D_c is sign-symmetric about
0 and clusters are independent, so the enumeration is type-I exact for ANY
within-cluster ICC. If the dev-split sign-symmetry check fails, the
pre-registered FALLBACK is the cluster (concept-block) BCa bootstrap of T with
a 95% CI and the same +3-pt floor; the choice between enumeration and
bootstrap is frozen at prereg-freeze on the DEV check, never chosen on test
data.

**Power — planning projections, and what is committed at freeze
[R2: ASM-2341, EXTRAPOLATION, load-bearing on nothing].** The R1 correction
stands: the withdrawn "0.90 power at true +3" target appears nowhere — under
the joint rule, P(observed ≥ +3 | true +3) ≈ 0.5 caps joint power at ~50% at
ANY n. Power is stated as a true-effect MDE (KaE §R-REV4.1(b)/§R-REV5.1
discipline): MDE_true = max(3, c_α·SE) + 0.842·SE, where c_α·SE is the
one-sided 5% rejection boundary — Gaussian planning value 1.645·SE; the EXACT
boundary of the 256-flip enumeration is data-dependent and comes from the
pinned freeze study below. With SE² = (σ_d²/n)·(1 + (m−1)ρ), m = n/8, SE
floors at σ_d·√(ρ/8) as n grows — item count cannot buy power past the
8-cluster floor. Planning rows (σ_d ≈ 39 pts at a 15% paired per-item
disagreement rate, ρ = 0.10 — the F1-K planning premise family): n = 300 →
SE ≈ 4.8 pts, MDE_true ≈ 12 pts; n → ∞ → SE ≈ 4.3 pts, MDE_true ≈ 10.8 pts
(the floor). Honest joint power at a true +3: ≈ 0.15 at n = 300, ≤ 0.5 at any
n. These are PLANNING NUMBERS ONLY (EXTRAPOLATION; resolution path = the
pinned simulation, then the run itself — never quality metrics read as cost
resolutions or vice versa).

**[R3 — review-2 finding 1 closed: the PINNED SIMULATION now EXISTS and is
RUN at the planning point.]** The simulation code is pinned VERBATIM in
Appendix A (code bytes sha256
**1dc1682a0cf37cec00b1f0f4444e54c27d6944b2fe70a870b7730b1ec801e3d4**),
seed **20260728**, 20,000 Monte-Carlo replicates per grid point over the
planning DGP (C = 8; n = 300; m_c = [38,38,38,38,37,37,37,37]; q = 0.15
paired disagreement; cluster effect τ = 12.91 pts ⇒ ρ = 0.10), evaluating
the EXACT joint rule — ALL 2^8 = 256 sign flips enumerated per replicate,
reject iff #{s : T(s) ≥ T_obs} ≤ 12 (p ≤ 12/256 ≈ 0.0469) AND T_obs ≥ +3.
Pinned output (canonical JSON, sha256
**9cdd2c01d300b648d0ad7c30cdb3320b53731755046b98725e98e82f5ede1769**;
double-run byte-identical this tick; full grid in Appendix A): **joint power
at a true +3 = 0.119**; joint power 0.482 at true +10, 0.611 at +12, 0.776
at +15; **simulated MDE_true at 0.80 joint power = 16.0 pts** (0.5-pt grid).
The exact enumeration is thus HARSHER than the Gaussian approximation above
(≈16 vs ≈12 pts at n = 300): with only 8 clusters the discrete 256-flip
boundary is far coarser than 1.645·SE, and the Gaussian rows are retained
only as the derivation trail — **the pinned simulated figures supersede them
as this design's planning resolution, and every resolution-scope sentence in
§5.3 quotes ≈16 pts.** This makes the honest power statement worse, not
better; it is reported, not softened, and it sharpens the named lever: C
(more trace clusters), not n. What remains for prereg-freeze is ONLY the
RE-RUN of the SAME pinned code with (n, m_c) replaced by the frozen realized
values — a SEQUENCED-AFTER-F1-K-FREEZE pin (the realized m_c derive from the
eligible set, §5.1), whose code + output hashes enter the freeze manifest;
that re-run output becomes the MEASURED power record the maintainer decides
on (MD-6). Reproduction note: bit-exact on the pinned platform (CPython 3 +
numpy, this box); re-verification elsewhere accepts |Δpower| ≤ 2 MC-SE
(≤ 0.006 at 20,000 replicates) with the enumeration and rule logic
byte-identical. A non-significant result is scoped "powered to
resolve ≥ MDE_true pts at C = 8 cluster coverage", never "no effect".

n = \|eligible\| exactly (§5.1), fixed before test access; no optional
stopping, no post-hoc subgroups beyond the named sense-pair descriptive tag.

### 5.3 Decision rule — frozen wording, both directions [STIPULATED: ASM-2236; wording repaired R2: ASM-2346 — review finding 4]

Evaluated on the untouched test split at k\*, cluster-balanced statistic
throughout, in this order:

- **D0 (deficit check).** If the test deficit T(b0-full vs u-topk) ≤ 3.0 points
  (the dev deficit did not reproduce), the run is **floor-bound**: no
  guided-vs-uniform contrast is licensed; report and stop. (Strict/non-strict
  alignment with the pilot rule: §4.2 [R2].)
- **D1 (guided vs uniform).** T(m-kern vs u-topk) ≥ +3 points AND enumeration
  p ≤ 0.05 (§5.2), matched loads verified (§4.1).
- **D2 (kernel-specificity) [R1: ASM-2293].** THREE separate named paired
  contrasts, EACH under the joint rule: (a) m-kern vs m-freq; (b) m-kern vs
  m-emb; (c) m-kern vs the per-item MEAN over the R = 3 m-drng realizations
  [R2: ASM-2344]. **D2 passes only if ALL THREE pass** — never a best-of /
  accuracy-selected comparator. The conjunction is deliberately conservative;
  no multiplicity relief is taken in the kernel's favour. **D2 FAIL vs D2
  UNINFORMATIVE are DISTINCT recorded outcomes [R2]:** a leg voided as
  non-distinct (§3.1 Jaccard gate), dose-voided (§3), load-voided (§4.1), or
  derangement-excluded past the 10% bound (§3.1) makes D2 **UNINFORMATIVE**
  (the question was not asked cleanly); a leg that runs cleanly and misses the
  joint rule makes D2 **FAIL-TO-DEMONSTRATE** (the question was asked at the
  registered resolution and the advantage was not shown).

**Equivalence discipline [R2 — review finding 4].** A failed one-sided
superiority test is NEVER read as equivalence, sufficiency, deadness, or "added
nothing." This design powers NO equivalence test; therefore NO outcome of this
design licenses a sentence of the form "X adds nothing," "X is retention-free,"
"the deflator did the work," or "the kernel is one conditioner among several."
If the programme later wants an equivalence/sufficiency claim on this seam, it
requires a separately powered TOST/non-inferiority design with its own margin
and its own preregistration.

| Outcome | The entire licensed sentence |
|---|---|
| D1 ∧ D2 | "Kernel-concept-guided expert-drop preserved more accuracy than uniform router truncation and than kernel-free importance baselines at matched experts-per-token, on concept-covered QA items at this model and box." Nothing about intelligence, parity, general capability, or deployment. |
| D1 ∧ D2 FAIL-TO-DEMONSTRATE | "Kernel-guided expert-drop beat uniform truncation, but a kernel-SPECIFIC advantage over the kernel-free conditioned deflators was not demonstrated at the registered resolution (simulated MDE_true ≈ 16 pts at the n = 300 planning point, C = 8 — pinned simulation §5.2 [R3]; refreshed at freeze at realized n, m_c)." Reported at equal prominence. NOT reported as "the kernel is one conditioner among several" — that is an equivalence reading this design cannot license. |
| D1 ∧ D2 UNINFORMATIVE | "The guided-vs-uniform advantage was shown; the kernel-specificity question was not cleanly asked (voided leg(s) named)." Neither a pass nor a deflation. |
| ¬D1 | "A guided-vs-uniform advantage ≥ +3 points was not demonstrated at the registered resolution (simulated MDE_true ≈ 16 pts at the n = 300 planning point, C = 8 — pinned simulation §5.2 [R3]; refreshed at freeze at realized n, m_c) on this subset; uniform TOPK stands as a colibri-native, concept-free lever with no kernel sentence attached." Kernel-guided B1b is recorded NOT-DEMONSTRATED-at-this-resolution-scale-and-subset (not "dead", not "concept guidance added nothing" — both over-claim a null this design cannot power). |
| D2 leg (c) misses: T(m-kern vs m-drng mean) < +3 or p > 0.05 [R1; R2 wording] | "A kernel-label-specific advantage over dose-exact DERANGED labels was not demonstrated at the registered resolution." Subsumed by D2 FAIL-TO-DEMONSTRATE above; named separately because it is the sharpest deflation-shaped datum and the direct knull analog. It does NOT license "mask structure did the work" (equivalence). |

A non-demonstration at any rung is a real result and is filed at equal
structural prominence, always carrying its resolution scope. Verdict-gen's
registered pathway grades the run; this document never does.

---

## 6. Co-location, cost, and the standing cost directive [STIPULATED: ASM-2237; isolation R2: ASM-2347; costs R2: ASM-2350 (EXTRAPOLATION)]

### 6.1 Co-location on the KaE (#28) instance — the standing isolation clause, implemented literally [R2: ASM-2347 — review finding 6]

GLM-DROP runs on the SAME i4i.2xlarge that #28 authorizes for F1-K, amortizing
across both experiments exactly as promised in the #28 cost thread: one S3
model restore (~370 GB artifact, ~1 h), one bring-up + fact re-verification,
one echo+logprobs gateway patch, one known-concept subset construction, one
prefill-throughput measurement (F1-K's bring-up number is reused to price this
experiment's main phase before it starts — no separate bring-up line). If
#28's GATE 0/1 do not both land, GLM-DROP still runs on the same instance
class with its own restore; only the amortization is lost (the DROP patch does
not depend on the KaE patch, §6.3).

**[R2] The standing clause (`glm52-f1k-cost-reduction.md` line 30: "after
F1-K's durable checkpoint is sealed … as a fresh process with its own manifest
+ accounting; never interleave") is implemented as a mandatory ordered
protocol, each step logged in GLM-DROP's own manifest:**

1. **Seal first.** F1-K's arms complete and its durable checkpoint is SEALED
   (checkpoint SHA-256 recorded in F1-K's manifest). No GLM-DROP engine
   process may start before the seal record exists.
2. **Terminate.** F1-K's engine process is TERMINATED (its PID and exit are
   logged). No process survives across the boundary.
3. **Fresh process, verified state.** GLM-DROP starts under a NEW PID (logged
   in GLM-DROP's manifest) with `KAE`, `TOPK`, `TOPP`, `DROP`, `PIN`, and
   `AUTOPIN` explicitly RESET to GLM-DROP's frozen values and VERIFIED by an
   environment echo captured at startup into the manifest — inherited F1-K
   knob state is a halt condition, not a warning.
4. **Distinct namespaces.** GLM-DROP uses its own checkpoint namespace
   (`glm-drop/checkpoints/`), result namespace (`glm-drop/results/`), manifest
   (`glm-drop/manifest.json`), and **its own cost ledger**
   (`glm-drop/cost-ledger.json`) — no file is shared with F1-K's namespaces;
   accounting is separable by construction.
5. **Freeze-order firewall (shared test set).** GLM-DROP's eligible items are
   a subset of F1-K's test-1440, so F1-K's test outcomes are contaminating if
   seen pre-freeze. Rule: GLM-DROP's prereg freeze is committed BEFORE F1-K's
   test-set outcome files are generated; if scheduling makes that impossible,
   F1-K's test outcomes are FIREWALLED — read by no GLM-DROP role, with the
   firewall and any access recorded in both manifests — until GLM-DROP's
   freeze commit lands.
6. **Never interleaved** inside an arm (carried from R0).

### 6.2 Cost-saving measures baked in (maintainer directive, #28 thread) [footprint claims corrected R2: ASM-2351]

1. **SPOT instances:** i4i.2xlarge spot ≈ $0.20–0.28/h vs $0.69 on-demand
   (planning figures, verified at spin-up) — ~3× cut. The eval is one prefill
   per item per arm, checkpointed per item; a spot interruption resumes from the
   last completed item. Long runs launched nohup+setsid (house box discipline).
2. **Expert-pinning + warm cache — cost lever only, claims scoped [R2].** The
   PIN set is the universal core, identical across ALL arms (§4.3), within
   measured free RAM. The R1 claim that masked arms "draw from a ~93 GB pool"
   is WITHDRAWN (finding 10): whether the page cache runs hot depends on the
   UNION footprint across per-item masks, which is MEASURED at pilot (§5.1)
   before any cache-benefit expectation is stated as more than a hope. Pinning
   changes cost only; scoring cache-independence is VERIFIED at bring-up
   (§4.3), not asserted.
3. **Item-block batching:** items sharing active concepts are scheduled
   adjacently within an arm so their retained sets overlap in cache (order
   randomization operates at block level, seeded, recorded). Permissible
   because scoring is verified cache-independent and tok/s is not an endpoint
   (§4.3 [R2]).
4. **No idle instance:** the box is stopped between phases; artifact persists in
   S3 ($8.5/mo line already running).

### 6.3 The one C change: the item-ID→mask table [R2: ASM-2349 — review finding 8; supersedes the R0 read-once single-mask design]

The R0/R1 `DROP=<mask-file>` sidecar was read ONCE at startup — but m-kern,
m-emb, and m-drng need a DIFFERENT mask per item, which that design cannot
realize without per-item engine restarts (invalidating the cache and cost
assumptions). Replaced:

`DROP=<table-file>` — an **immutable item-ID→mask table**, loaded ONCE at
engine start: a sidecar mapping item-ID → per-layer 256-bit expert bitmask
(one entry per eligible item per masked arm realization; uniform arms carry no
table). The harness passes the item-ID with each scoring request; the engine
resolves the mask by **fail-closed lookup** — an unknown or missing ID refuses
the request and halts the run (NEVER a silent fall-through to unmasked
routing). Integrity: the table header carries a per-entry SHA-256 over each
(item-ID, bitmask) record, verified at load; the whole-table SHA-256 goes in
the run manifest and the freeze manifest. The table is bit-identical bytes for
the entire run (immutable; no reload path). Per-item engine restarts are
REJECTED as the alternative (they would multiply bring-up overhead and
invalidate §6.2's cache economics; if a future pass prefers restarts it must
preregister and price them explicitly, per the review's option).

**[R3 — review-2 finding 8: the two remaining opens re-classed, fail-closed
defaults stated.]** (1) *Table + entry hashes*: each arm-realization's table
is a PURE FUNCTION of (eligible-item ID list, the §2.1 core + table hashes,
the §3.1 parameters and seeds, the pinned encoder bytes for m-emb) — every
input either pinned by hash IN THIS DOCUMENT or a §5.1
sequenced-after-F1-K-freeze pin; the tables are therefore materialized, and
their per-entry + whole-table hashes committed, AT PREREG-FREEZE and cannot
exist earlier by construction (SEQUENCED-AFTER-F1-K-FREEZE, not an open
hole). Fail-closed default: the engine REFUSES to start unless the loaded
table's whole-table sha256 equals the freeze-manifest value, and refuses any
request whose item-ID misses (already above) — there is NO code path that
runs a masked arm without a hash-verified table. (2) *C-patch approval*: a
NAMED EXTERNAL GATE, not a design hole — the diff rides the #28 maintainer
patch-approval review (one decision, bundled); fail-closed default: while
unapproved, GLM-DROP has NO bring-up, NO freeze completion (§7 item 4 makes
approval a prerequisite), and NO spend; a refusal returns the design to the
maintainer with the restart-based alternative priced as the review's option.
Nothing in this design proceeds "pending" the patch.

**[R4 — review-3 finding 8: CANONICAL SERIALIZATION + HASH FRAMING, pinned
NOW; ASM-2349 as R4-amended.]** The "pure function" claim is made true by
freezing the exact bytes. Everything below is fixed in THIS document; the
only input that cannot exist yet is the eligible-item ID LIST, which is the
§5.1 sequenced-after-F1-K-freeze pin (pure function of F1-K's frozen
test-1440 id list + trigger map + span sidecars) — the serialization spec
and hash framing do NOT wait on it.

1. **Table identity.** One table file per (masked arm, realization): arm-ID ∈
   {`m-freq`, `m-emb`, `m-kern`, `m-drng-1`, `m-drng-2`, `m-drng-3`} —
   closed set; uniform arms carry no table. m-freq's per-item entries are
   identical by construction (item-unconditioned) but are still emitted
   per-item, keeping one loader code path and per-item dose verification.
2. **Encoding.** All-ASCII, LF line endings, no BOM, no padding, no trailing
   whitespace; integers decimal, unpadded; hex lowercase.
3. **Item-ID encoding.** The F1-K frozen id string VERBATIM, as its UTF-8
   bytes (F1-K ids are ASCII); an id containing `|`, `:`, a control byte, or
   any non-ASCII byte is a config error → halt (fail-closed, never escaped
   or rewritten).
4. **Per-layer expert-bit ordering.** Layers = the 76 MoE layers, ascending
   (3…78), every layer present in every record. A layer's 256-bit mask is 64
   hex chars c_0…c_63: c_j encodes experts 4j…4j+3, with expert 4j at the
   most-significant bit of the nibble (value 8) and expert 4j+3 at the
   least-significant (value 1); bit = 1 ⇔ expert retained. (Each record
   must carry exactly 64 retained bits per layer — the §3 dose invariant —
   verified at load; violation halts.)
5. **Record line.** `<item-id>|<layer>:<64-hex>|<layer>:<64-hex>|…` over the
   76 layers ascending, then LF. **Record ordering:** ascending
   byte-lexicographic item-ID (unsigned bytewise — the §3.1 item 4 ordering,
   reused).
6. **Per-entry hash framing.** SHA-256 over the ASCII bytes
   `glm-drop-mask:` ‖ arm-ID ‖ `:` ‖ the record line EXCLUSIVE of its
   trailing LF. (The arm-ID is inside the frame so an entry cannot be
   transplanted between arm tables undetected.)
7. **File layout (the exact bytes on disk).** Line 1:
   `glm-drop-table/1:<arm-ID>:<record-count decimal>:<§2.1 core sha256>`;
   then one line per entry, canonical order: `<item-id>|<per-entry sha256
   hex>`; then the separator line `--`; then the record lines (item 5),
   same order; final line LF-terminated like every other.
8. **Whole-table hash framing.** SHA-256 over the COMPLETE file bytes
   exactly as loaded (header line + per-entry-hash lines + separator +
   record lines — every byte, nothing else). This is the value copied into
   the freeze manifest and the run manifest; at engine start the table is
   re-hashed and refused on mismatch, then every per-entry hash is
   re-verified against its record (both checks fail-closed, §6.3 above).

With §2.1 item 3 / §3.1 pinning every score, tie-break, seed, and DRBG draw
[R4], and items 1–8 pinning every byte, each table is a PURE FUNCTION of
(eligible-item ID list, §2.1 core + concept→cluster hashes, §3.1
parameters/seeds/DRBG, pinned encoder bytes for m-emb): freeze-time
regeneration must be BYTE-IDENTICAL, and any two independent implementations
of this spec must agree byte-for-byte or halt. SEQUENCING, explicit: table
materialization and its hashes remain SEQUENCED-AFTER-F1-K-FREEZE solely
because the item list is (§5.1); nothing else about the table waits, and no
serialization choice remains open for the freeze pass to make.

Estimated **~120–200 lines** against the same pinned colibri commit the KaE
draft targets (a78a06fc5acc4b0dc0f9ef03987c66b0559d1250) — the R0 "40–60
lines" estimate is superseded; table parse + per-entry hash verification +
per-request lookup plumbing is more code than a read-once mask. Kept as an
in-repo diff, inert unless DROP is set, fail-closed on malformed tables
(engine refuses to start — never a silent partial arm). This is NOT a Law-1
matter (it selects among native experts; nothing writes activations) but it
EXCEEDS the P0 trace-dump-only C envelope (ASM-1986/1989), so the diff rides
maintainer patch approval — bundled into the #28 review for one decision, not
a new gate. Fork etiquette carried from ASM-1989; nothing is pushed upstream.

### 6.4 Cost — instance-hours and dollars, stated separately [R2: ASM-2350, EXTRAPOLATION — review findings 9 + 12; supersedes ASM-2238 IN FULL]

Prefill throughput on this box is UNKNOWN until F1-K bring-up measures it
(ASM-2023 carried); the model below is the STANDING F1-K cost model
(`glm52-f1k-cost-reduction.md`: 100 s/prefill pessimistic ÷ 1.20 pinning
speedup, spot $0.20–0.28/h), applied honestly — the R1 "$15–45 band / $60
spot-hours ceiling" was not derived from it and confused hours with dollars;
both defects are corrected here. All figures are planning EXTRAPOLATION,
resolved ONLY against GLM-DROP's own metered cost ledger
(`glm-drop/cost-ledger.json`), never against quality metrics.

**Derangement count [R2]:** **R = 3 preregistered derangement realizations**
(§3.1; following F1-K's registered R=3 policy — enough to average
realization noise in D2(c) without pricing mapping-precision repetitions),
so the main phase is **8 pass-equivalents**: b0-full, u-topk, m-freq, m-emb,
m-kern, 3 × m-drng.

**Volume:** pilot ≤ 480 prefills (dev-96: b0-full ×96 + u-topk ×96×3 for
k ∈ {4,3,2}, +96 if the k=1 escalation fires) + ~50 bring-up/verification
prefills (cold/warm logit checks, §4.3) ≈ **≤ 530**. Main: 8 × n.

| n | prefills (main + pilot) | instance-HOURS (100 s ÷ 1.20) | spot DOLLARS ($0.20–0.28/h) |
|---|---|---|---|
| 300 (planning point) | ≈ 2,930 | ≈ 68 h | ≈ $14–19 |
| 1,440 (pool cap) | ≈ 12,050 | ≈ 279 h | ≈ $56–78 |

(The review's independent arithmetic — n=300 ≈ $9–13 and n=1,440 ≈ $41–57 at
six passes, R=3 high-corner ≈ $76 — is reproduced by this table once the
larger dev-96 pilot and the 8th pass are included.)

**Band: ≈ 68–279 instance-hours ≈ $14–78 spot dollars.**
**CEILING: 320 instance-hours AND $95 spot dollars, whichever binds first.**
On-demand fallback (spot capacity dry) at $0.69/h ≈ $193–220 worst case —
a coordinator sign-off decision, never a silent fallback. Mask/map
construction is CPU-only, ~$0. S3 retention stays on the existing $8.5/mo
line.

**Pre-registered degradation order if the ceiling binds [R2; consistent with
ASM-2293]:** (1) drop the k=1 escalation pilot cell; (2) return to the
maintainer. **NO masked arm can be dropped, R never falls below 3, and n is
never cut below the frozen basis** — m-freq, m-emb, AND all three m-drng
realizations are required by the D2 conjunction (§5.3), and the frozen n is
the power record the maintainer decided on (MD-6). The R0 ASM-2238 degradation
clause (which permitted dropping m-rand and m-freq) is superseded IN FULL;
its resolution path is repointed to the metered cost ledger (§R2.12).

**[R3 — review-2 finding 12: the supersession made OPERATIVE to the limit of
a no-registry-write pass.]** The central record this supersedes is quoted
VERBATIM so the coordinator's transcription is exact and, until it lands,
no reader can mistake which text governs. Central ASM-2238
(`registry/assumptions.jsonl` line 1090, read this tick) contains:
(a) *degradation clause* — "Pre-registered degradation order if the ceiling
binds: (1) drop m-rand; (2) drop m-freq (m-emb, the stronger conditioned
deflator, is never dropped); (3) drop the escalation k-cell; (4) return to
the maintainer" — **VOID and superseded in full** by this section's order
(k=1 pilot cell, then maintainer; no masked arm ever dropped, R ≥ 3, n never
cut), because steps (1)–(2) contradict the registered D2 conjunction
(ASM-2293); and (b) *resolution path* — "Resolved by the measured GLM-5.2
expert-drop run …; the projection is discharged by the runs
quality-retention metrics under the frozen deflator policy" — **VOID and
repointed**: ASM-2350 resolves ONLY against the metered cost ledger
(`glm-drop/cost-ledger.json`), never against quality metrics. INTERIM
PRECEDENCE RULE (binding on every GLM-DROP role from this revision): any
conflict between central ASM-2238 and ASM-2350 resolves to ASM-2350; central
ASM-2238 is cited by no GLM-DROP artifact from R3 onward except to record
this supersession. The central-register edit itself is the coordinator's
transcription at the landing commit (§R2.14) — this pass writes no registry
byte, per its brief.

---

## 7. Sequencing, gating, and prerequisites [STIPULATED: ASM-2230/2231]

1. **R4 replay first, before any spend.** The offline M_oracle/M_kernel replay
   (`interpretation-fable.md` §2 R4) is CPU-only on committed bytes, ~$0, and
   MUST land through the coordinator's mechanical pathway before GLM-DROP's main
   phase: it completes the held ASM-2013 branch classifier and prices D2's prior
   (an M_kernel failure against the embedding deflator on the pin replay is
   registered prior evidence against D2 and is reported alongside GLM-DROP's
   result either way).
2. **Sequencing amendment to ASM-2010 (stipulated here, registered by the
   coordinator).** ASM-2010 gated B1b behind B1a's outcome. The maintainer's
   #27-A redirect promotes B1b to the primary efficiency instrument; ASM-2230
   amends the sequencing: GLM-DROP's admissibility no longer waits on a B1a live
   win — its physics lever (fewer experts computed) is TOPK-like and does not
   presuppose pin-miss structure — but it inherits every deflator obligation,
   and a Branch-B/C classifier outcome scopes (not blocks) its claims per §2.2.
   F1-K's primacy and gates (#28) are untouched.
3. **Own prereg before freeze.** This document is the design; the experiment
   still requires its own kot-reg/1 prereg (experiment-designer role) and
   runs only inside maintainer-approved ceilings. **[R3 — what the prereg
   still has to PRODUCE vs merely RE-VERIFY:]** already pinned in this
   document and only RE-VERIFIED at freeze (byte-identical or halt): all
   thresholds and seeds (§3.1 item 8), the universal-core hash (§2.1), the
   concept→cluster table hash (§2.1), the planning power simulation code +
   output hashes (§5.2, Appendix A). Still to be PRODUCED at freeze, each an
   explicitly sequenced pin with its fail-closed default stated where it
   lives: the eligible-item hash + n + m_c (§5.1,
   sequenced-after-F1-K-freeze), the derangement realizations (§3.1 item 4,
   same sequencing), the mask-table hashes (§6.3, same sequencing — [R4]
   the canonical serialization and hash framing are already pinned in-doc;
   ONLY the item list is what the tables wait on), the
   dev-96 id-list hash (§4.2), the encoder-weights hash (§3.1 item 1,
   sequenced-at-freeze), the power-simulation re-run at realized (n, m_c)
   (§5.2), and the pre-freeze skeptic attack. Nothing fires from this pass.
4. **Prerequisites:** F1-K bring-up artifacts (subset, scorer, throughput
   number) or, degraded, their independent construction; the DROP table patch
   approval (§6.3); R4 landed (item 1); the 24-fingerprint trace set (exists,
   committed).

**Honest risks (designer judgment, binding nothing) [R2 — untagged per the
closed schema]:** (i) the modal outcome on the programme's record is a D1
non-demonstration or a D1-pass with D2 not demonstrated — either is a
publishable systems datum and neither is a kernel result (nor a kernel
refutation: §5.3 equivalence discipline); (ii) the deficit regime may not
exist above k=1 on this subset (GLM-5.2 is strong; §4.2's STOP handles it
honestly); (iii) the map rests on 24 prompts across only 8 concept clusters
[R1: ASM-2291] — thin, disclosed, and doubly binding: C = 8 is also the
inference floor that fixes the planning MDE_true — simulated ≈ 16 pts at
n = 300 under the exact 256-flip joint rule (§5.2 [R3]); the
coverage gates, the Jaccard gate, and the dose gate exist because of it, and
the honest power lever is more trace clusters, not more items; (iv) spot
capacity for i4i.2xlarge can dry up — the ceiling names the on-demand
fallback as a decision, not a default; (v) the eligibility rule (every active
concept trace-covered) may cut n below 300 or leave a thin analysis cluster —
the §5.1 gates surface exactly that to the maintainer before spend.

---

## R1. REVISION 1 — codex design-review response [STIPULATED: ASM-2290..2293]

*(Historical audit trail, retained. Where R2 supersedes an R1 clause, §R2
governs; the central supersession map is §R2.14.)*

The standing codex review of this design (pre-revision bytes sha256
e52b3c3ac7ce0fe484db8f52e2bbb592221107680f6d0f8d22c9771b5773d966) returned
ISSUES on four points. Each was fixed in place (tagged [R1]); this section is
the audit trail. No review-OK item was touched: the fixed-compute k\* ±5%
matched-loads comparison (§4.1), the full-TOPK=8 retention reference
(b0-full), and the spot/pinning/co-location cost design (§6.1–6.3) stood
byte-for-byte at R1. [R2 note: §6.1–6.3 have since been revised by R2 per the
GPT-5.6 findings.]

1. **Deflator masking — dose-exact, matched multilabel [ASM-2290].** Found:
   m-emb conditioned on ONE nearest cluster while m-kern may union multiple
   concepts, and m-rand lacked the universal core — the drop-selection arms
   were not dose-matched, so a m-kern win could have reflected dose or
   structure, not labels. Fixed (§3): every masked arm retains exactly
   f·256 = 64 experts/layer including the same universal core; m-emb is
   matched-multilabel (top-\|C(item)\| clusters, the same per-item label
   cardinality as m-kern); m-rand is replaced by **m-drng**, a dose-exact
   LABEL-DERANGED mask (the m-kern pipeline under a seeded
   cardinality-stratified derangement of item→concept-set assignment).
   [R2 note: ASM-2290's clause reading the multilabel match across all FOUR
   masked arms was wrong about m-freq, which is item-unconditioned; corrected
   by ASM-2343, §R2.2.]
2. **Coverage corrected [ASM-2291].** Found: "~24 concepts" overstated the
   probe source, which is 24 prompts across only **8 concept CLUSTERS**
   (3 prompts/cluster). Fixed: §2.1, §2.2, and §7 risk (iii) now state the
   8-cluster coverage; every claim resting on the count is re-scoped to C = 8,
   and the power analysis is re-derived on that basis (item 3). [R2 note:
   ASM-2291 mixed the measured count with stipulated analysis consequences;
   split by ASM-2342 (MEASURED) + ASM-2340 (STIPULATED), §R2.11.]
3. **Quality power re-derived [ASM-2292].** Found: "0.90 power at a true +3"
   is impossible under the joint licensing rule (p < 0.05 AND observed ≥ +3):
   at true +3 the observed-margin leg alone has a ~50% ceiling. Fixed (§5.2):
   the target is withdrawn; power is restated as a true-effect MDE per the KaE
   §R-REV4.1(b)/§R-REV5.1 precedent. [R2 note: ASM-2292 was schema-mistagged
   (a projection recorded as a load-bearing stipulation) and left n and the
   simulation unfrozen; split and completed by ASM-2340 (frozen inference
   record) + ASM-2341 (EXTRAPOLATION planning figures) with the pinned
   simulation required at prereg-freeze, §R2.1/§R2.11.]
4. **D2 both-deflators rule [ASM-2293].** Found: D2 compared m-kern against
   max(acc(m-freq), acc(m-emb)) with a single test "against the STRONGER
   deflator" — an accuracy-selected comparator whose permutation null ignores
   the selection. Fixed (§5.3): D2 is a CONJUNCTION of three separate named
   paired contrasts — m-kern vs m-freq, m-kern vs m-emb, m-kern vs m-drng —
   each requiring the joint rule; all must pass. §1's crux and §6.4's
   degradation order are updated to match (no D2 comparator can ever be
   dropped). ASM-2232's m-rand arm, ASM-2235's power clause, and ASM-2236's
   D2 max clause are superseded on exactly these points; the ASM-2230..2239
   companion file is left intact as the pre-review record. [R2 note: central
   registration of R0+R1 has since occurred — see header.]

---

## R2. REVISION 2 — GPT-5.6 FIX-FIRST review response [STIPULATED: ASM-2340..2352]

The standing GPT-5.6 xhigh review of the R1 design
(`poc/gpt56-review/expert-drop-r1/out/last-message.json`, sha256
f67aef03254faf3c3336d7edc319fd9565d192979132fb96a22073d0c4d290e4; pre-R2
document bytes sha256
1f65f3e908964f1033ea749c03b5f087b14b6162398c8cb2f7b43cbc6f334307) returned
**FIX-FIRST**: 9 blocking findings, 4 should-fix/minor. Resolution audit
trail; every finding is RESOLVED (none declined):

1. **(Blocking) Sample/analysis population + inference not frozen → RESOLVED,
   §5.1 + §5.2 [ASM-2340/2341].** n = \|eligible\| exactly (no sampling rule
   needed), eligible-item ID list + SHA-256 + n + per-cluster m_c + exclusion
   count committed at prereg-freeze; deterministic multilabel→analysis-cluster
   rule (highest G-lex trigger score, frozen tie-break); cluster-balanced
   estimand θ = (1/8)ΣE[D_c] frozen, item-weighted accuracy demoted to
   descriptive; EXACT enumeration of all 2^8 = 256 sign flips (effective size
   12/256 disclosed) replacing 10k Monte-Carlo; F1-K's registered
   sign-symmetry basis (ASM-2122) + cluster-BCa-bootstrap fallback imported,
   choice frozen on the dev check; shortfall/thin-cluster gates fail to the
   maintainer; the pinned power simulation (code + output hashes) is a
   mandatory prereg-freeze artifact.
2. **(Blocking) Universal core undefined; ASM-2290 wrong about m-freq →
   RESOLVED, §2.1 + §3 [ASM-2343].** Frozen per-layer algorithm: pooled-mass
   ranking, ascending-index tie-break, cumulative-mass threshold τ = 0.50,
   hard cap 48 < 64 guaranteeing ≥16 concept-tail slots; core file hashed at
   freeze [R3 note: now hashed IN-DOCUMENT, §2.1 — freeze re-verifies]; the
   impossibility of retaining all ~141 [R3 correction: ~139, 76 layers]
   universal cells/layer stated with the measured numbers. ASM-2290 corrected: matched-multilabel
   scope restricted to m-kern/m-emb/m-drng; m-freq described as dose/core
   matched but intentionally item-unconditioned.
3. **(Blocking) Open arm choices → RESOLVED, §3.1 [ASM-2344].** Embedding
   encoder pinned (all-MiniLM-L6-v2, content-hash at freeze) + exact input
   text + normalization; clustering algorithm/k/seed/tie-breaks/nearest-rule
   pinned; derangement seeds (3), realization count R = 3, set-distinctness
   requirement (prevents identical wrong-label sets), impossible-stratum
   exclusion rule with a 10% UNINFORMATIVE bound; Jaccard gate aggregation
   defined (mean over items × layers, pooled over realizations); ±5% load
   gate defined at arm-mean level; **TOPP branch REMOVED** (the review's
   removal option taken).
4. **(Blocking) Failed superiority read as equivalence → RESOLVED, §5.3 +
   §4.2 [ASM-2346].** "Retention-free / added nothing / dead / one conditioner
   among several / mask structure did the work" all removed and replaced with
   "not demonstrated at the registered resolution (MDE_true ≈ 11–12 pts at
   C = 8)" [R3 note: the resolution figure in those sentences is now the
   pinned simulated ≈16 pts, §5.2/§5.3 — the wording discipline itself is
   unchanged]; D2 FAIL-TO-DEMONSTRATE and D2 UNINFORMATIVE are distinct recorded
   outcomes; an explicit equivalence-discipline clause states that no outcome
   licenses an equivalence/sufficiency sentence absent a separately powered
   TOST/non-inferiority design.
5. **(Blocking) Pilot too weak + inconsistent inequalities → RESOLVED, §4.2
   [ASM-2345].** Pilot panel = F1-K's frozen dev-96 (id-list hash pinned;
   ≥48-eligible gate; granularity disclosed); prespecified continuous
   statistic (correct-option LL margin) with seeded bootstrap 90% CI reported;
   sign-disagreement fails to the maintainer pre-freeze; inequalities aligned
   strictly (pilot requires dev deficit > 3.0; D0 floor-binds at test deficit
   ≤ 3.0 — exactly-3 insufficient in both).
6. **(Blocking) Isolation clause not implemented → RESOLVED, §6.1
   [ASM-2347].** Sealed-checkpoint-first, F1-K process terminated, GLM-DROP
   under a new PID with KAE/TOPK/TOPP/DROP/PIN/AUTOPIN reset + verified by a
   manifest-captured env echo, distinct checkpoint/result/manifest/cost-ledger
   namespaces, and a freeze-order firewall on F1-K's shared-test-set outcomes.
7. **(Blocking) Cache/throughput contradiction → RESOLVED, §4.3 + §6.2
   [ASM-2348].** Correctness regime: cold/warm per-option logits verified
   BYTE-IDENTICAL at bring-up (halt on mismatch); pin set = universal core,
   identical across ALL arms, never pilot-selected. Performance regime:
   **loads/token is the only systems endpoint; arm-level tok/s comparisons
   explicitly declined**; the generative spot-check removed; P0's 1.9×/2.5×
   re-scoped as preliminary (one sequential run, hit rate 33.0%→44.9%).
8. **(Blocking) Per-item masks impossible under read-once DROP → RESOLVED,
   §6.3 [ASM-2349].** Immutable item-ID→mask table loaded once, fail-closed ID
   lookup (refuse + halt, never fall through), per-entry SHA-256 verified at
   load, whole-table hash in both manifests; per-item restarts explicitly
   rejected (and what preregistering them would require, noted); line
   estimate revised to ~120–200.
9. **(Blocking) Cost model stale; derangement policy missing; $/hours
   confused → RESOLVED, §6.4 [ASM-2350].** R = 3 preregistered derangements
   chosen and justified; D2(c) tests m-kern against the per-item mean of the
   3 realizations; 8 pass-equivalents recomputed on the standing F1-K model
   with instance-HOURS and spot DOLLARS in separate columns (≈68 h/$14–19 at
   n=300; ≈279 h/$56–78 at n=1,440); ceiling restated as 320 h AND $95
   (dollars), on-demand fallback priced (~$193–220) as a sign-off decision;
   the reviewer's arithmetic reproduced and cited; resolution path repointed
   to GLM-DROP's own metered cost ledger, never quality metrics.
10. **(Should-fix) 93-GB shard/page-cache claims → RESOLVED, §5.1 + §6.2
    [ASM-2351].** Per-mask routed-expert footprint is the only reported
    footprint; the union footprint across the frozen workload is measured at
    pilot BEFORE any shard or page-cache claim; the f × 370 GB ≈ 93 GB
    projection withdrawn.
11. **(Should-fix) Tag schema + mixed ASMs → RESOLVED, header + §R2.14
    [ASM-2352].** DERIVED/ASSESSMENT removed from the tag convention AND the
    self-check (closed 4-tag schema); every former [DERIVED]/[ASSESSMENT] use
    re-tagged or rewritten as explicitly non-binding prose; ASM-2292 split
    into the frozen STIPULATED inference/decision record (ASM-2340) + a
    non-load-bearing EXTRAPOLATION with resolution path (ASM-2341) + the
    to-be-MEASURED pinned simulation at prereg-freeze; ASM-2291 split into
    the MEASURED coverage fact (ASM-2342) + the STIPULATED analysis design
    (ASM-2340).
12. **(Should-fix) ASM-2238 contradictory after R1 → RESOLVED, §6.4 + §R2.14
    [ASM-2350].** ASM-2238 superseded IN FULL: its degradation clause (drop
    m-rand/m-freq) contradicted ASM-2293 and cannot remain operative; its
    resolution path repointed from quality-retention metrics to the metered
    cost ledger; the supersession map (§R2.14) gives the coordinator the
    exact clause list so no superseded ASM-2232/2235/2236 clause remains
    simultaneously operative in the central register.
13. **(Minor) Evidence refs + stale governance prose → RESOLVED, header +
    throughout [ASM-2352].** Every input carries a full SHA-256 in the header
    table; every inline MEASURED cite names the exact JSON key or log
    line/section (e.g. `/universal_cells`, probe-main.log §P4 lines 56–71 —
    which also corrects the R1 conflation of the P1 baseline counter 1786.5
    with P4's TOPK=8 value 1825.1); the "central register not written" prose
    corrected (R0/R1 blocks ARE registered, lines 1082–1091 / 1106–1109).

### R2.14 Central supersession map (for coordinator transcription; this pass writes NO registry entry)

The corrected full ASM text lives in
`poc/glm52-probe/asm-glm-drop-r2-2340-2352.json` (its `central_supersessions`
section repeats this map machine-readably). Clauses to mark superseded in
`registry/assumptions.jsonl` at landing:

| Central ASM (line) | Superseded clause(s) | Superseded by |
|---|---|---|
| ASM-2232 (1084) | m-rand arm + single-cluster m-emb (already, per R1); Jaccard gate without aggregation rule; TOPP escalation reference | ASM-2290 (R1); ASM-2344 |
| ASM-2233 (1085) | "universal core sized at pilot to a pre-registered fraction" (deferred core); "~24 concepts" coverage wording | ASM-2343; ASM-2342 |
| ASM-2234 (1086) | 24-dev-item operating-point pilot, deficit "≥ 3" acceptance, TOPP escalation; "fresh caches at arm boundaries" + tok/s spot-check clause; load-gate aggregation level unstated | ASM-2345; ASM-2348; ASM-2344 |
| ASM-2235 (1087) | power clause (already, per R1); "10,000 resamples" statistics clause; item-unit estimand ambiguity; tok/s spot-check + f×370 GB shard clause | ASM-2292 (R1); ASM-2340; ASM-2351; ASM-2348 |
| ASM-2236 (1088) | D2 max clause (already, per R1); "added nothing"/"dead"/"one conditioner among several"/"any-mask regime" outcome wording | ASM-2293 (R1); ASM-2346 |
| ASM-2237 (1089) | "sequenced AFTER F1-K's arms complete" (under-specified isolation); "~93 GB retained pool" claim; asserted (unverified) cache-independence | ASM-2347; ASM-2351; ASM-2348 |
| ASM-2238 (1090) | **IN FULL** (degradation clause contradicts ASM-2293; hours/dollars confusion; no derangement count; resolution path pointed at quality metrics) | ASM-2350 |
| ASM-2239 (1091) | read-once `DROP=<mask-file>` single-mask design + 40–60 line estimate | ASM-2349 |
| ASM-2290 (1106) | "across m-kern/m-emb/m-drng/m-freq only the selection criterion differs … label-set cardinality do[es] not" (wrong for item-unconditioned m-freq) | ASM-2343 |
| ASM-2291 (1107) | **replaced as mixed-tag record**: measured fact → ASM-2342; stipulated analysis consequences → ASM-2340 | ASM-2340 + ASM-2342 |
| ASM-2292 (1108) | **replaced as mis-tagged record**: frozen rule → ASM-2340; projections → ASM-2341 (EXTRAPOLATION, non-load-bearing); simulation → MEASURED at prereg-freeze | ASM-2340 + ASM-2341 |
| ASM-2293 (1109) | degradation-order sentence referencing the (now removed) generative spot-checks | ASM-2350 (the D2 conjunction itself stands untouched) |

---

## R3. REVISION 3 — GPT-5.6 re-review (R2) residual-closure audit [designer-17]

The standing GPT-5.6 re-review of the R2 design
(`poc/gpt56-review/expert-drop-r2/out/last-message.json`, sha256
bde94f8510e0ad5e553a22998cbec5514f89ba8ec58926f7264457e3c474e37d; pre-R3
document bytes sha256
a4d15944ded80445b3144826da4d526c94a92e6bd14dd1f8acdef76ad2f6fd57) confirmed
findings 4/5/6/7/9/10/13 RESOLVED and left findings 1/2/3/8/11/12 PARTIAL.
Closure discipline: a residual is closed either by MATERIALIZING the artifact
this pass from committed bytes (CPU-only, ~$0), or by re-classing it as an
explicitly SEQUENCED pin — a pure function of named frozen inputs whose
output hash is a mandatory freeze-manifest entry with a fail-closed default —
with the reason the artifact CANNOT exist earlier stated. Per-finding:

1. **(PARTIAL → CLOSED, §5.1 + §5.2 + Appendix A.)** (a) Exact n /
   eligible-ID hash / m_c / exclusions: SEQUENCED-AFTER-F1-K-FREEZE with the
   reason verified this tick (F1-K's test-1440/dev-96 id lists, trigger-map
   hash, and span sidecars are not yet repo bytes — they are #28/F1-K freeze
   outputs); the eligibility function, gates, and fail-closed behaviour are
   frozen here and the concept→cluster table input is now materialized +
   hashed (10cb109d…7ac5e38). (b) "Highest-G-lex-trigger-score" replaced by
   an EXECUTABLE rule importing F1-K's registered span precedence
   (longest match → earliest start → table order). (c) The pinned simulation
   EXISTS and RAN at the planning point: code sha256 1dc1682a…801e3d4, seed
   20260728, all 256 sign flips enumerated per replicate, output sha256
   9cdd2c01…5ede1769, double-run byte-identical; simulated MDE_true ≈ 16 pts
   at n = 300 (joint power 0.119 at true +3) supersedes the Gaussian ≈12-pt
   figure and is quoted in every §5.3 resolution scope. Only the re-run at
   realized (n, m_c) remains, an explicitly sequenced-after-F1-K-freeze pin.
2. **(PARTIAL → CLOSED, §2.1.)** The universal core is MATERIALIZED this
   pass by the frozen ASM-2343 rule from the roster-pinned fingerprints:
   76 layers, 2,108 cells, per-layer sizes 15–46 (all published in §2.1), no
   layer at the 48 cap (≥18 tail slots everywhere), canonical serialization
   frozen, core sha256 632bcd18…4cd3f18f; freeze only re-verifies
   byte-identity. m-freq remains described as item-unconditioned (§3, §R2.2
   — untouched). Measured correction folded in: 76 MoE layers (3–78), not
   75; ~139 universal cells/layer, not ~141.
3. **(PARTIAL → CLOSED, §3.1 + §4.3.)** Encoder-weights hash: fail-closed
   sequenced-at-freeze pin with the no-unpinned-weights default stated
   (item 1). k-means implementation: pinned to an own deterministic
   spec — no library, no floating version (item 2). PRNG: the SHA-256
   GLM-DROP-DRBG defined in full (item 8), replacing the unpinned
   "seeded Fisher–Yates". Derangement realizations: pure function of
   (eligible set, seeds, DRBG), sequenced-after-F1-K-freeze, hashes at
   freeze (item 4). Block-order seed (20260726) and correctness-spot-set
   seed (20260727) NAMED, and the seed registry is closed — randomness
   outside it halts at bring-up (item 8, §4.3).
8. **(PARTIAL → CLOSED, §6.3.)** Table + entry hashes: re-classed
   sequenced-after-F1-K-freeze (pure function of pinned/sequenced inputs);
   fail-closed default — the engine refuses to start on any table whose
   whole-table hash misses the freeze manifest. The C-patch approval is a
   named external maintainer gate (#28 bundle) with the fail-closed default
   that nothing (bring-up, freeze, spend) proceeds while it is unapproved.
11. **(PARTIAL → CLOSED to the limit of this pass's brief, header + ASM
    file.)** The ASM-2291/2292 splits stand (STIPULATED rule → ASM-2340;
    non-load-bearing EXTRAPOLATION with resolution_path → ASM-2341; the
    simulation result now MEASURED at the planning point in Appendix A, its
    freeze re-run still to-be-MEASURED); the doc's tag convention carries no
    DERIVED/ASSESSMENT (grep-verified this tick — the tokens appear only in
    the §R2.11/§R3 audit prose describing their retirement). Central
    registration of ASM-2340..2352 requires a registry write and a landing
    commit, both outside this pass's brief (NO git, NO registry write):
    explicitly SEQUENCED-WITH-LANDING-COMMIT, coordinator-owned, and the
    design is not freeze-eligible before it lands (§7 item 3 discipline).
    The companion file is amended in place this pass (permissible only while
    unregistered; header note) with inline R3 provenance per record.
12. **(PARTIAL → CLOSED to the limit of this pass's brief, §6.4.)** Central
    ASM-2238's degradation clause and resolution path are quoted VERBATIM
    and declared VOID with an interim precedence rule binding every GLM-DROP
    role (conflicts resolve to ASM-2350; the metered cost ledger is the only
    resolution target). The physical central-register edit is the
    coordinator's transcription (§R2.14) — a registry write this pass may
    not perform.

No resolved finding (4/5/6/7/9/10/13) is reworded, weakened, or touched by
R3 beyond: the §5.3/§7 resolution-scope figures updating from the Gaussian
≈11–12 pts to the pinned simulated ≈16 pts (an honest tightening in the
non-demonstration direction, required by finding 1's own simulation), and
the measured 75→76 MoE-layer correction (finding-13 discipline: exact
citations, corrected where the R2 prose miscounted).

### Appendix A — pinned planning power simulation [R3; ASM-2341 resolution artifact]

Code bytes below (from the `#!/usr/bin/env python3` line through the final
line, LF newlines, one trailing LF): sha256
`1dc1682a0cf37cec00b1f0f4444e54c27d6944b2fe70a870b7730b1ec801e3d4`.
Executed twice this tick; canonical-JSON output byte-identical across runs,
sha256 `9cdd2c01d300b648d0ad7c30cdb3320b53731755046b98725e98e82f5ede1769`.

```python
#!/usr/bin/env python3
# glm-drop-power-sim v1 (GLM-DROP R3, ASM-2341 pin). Planning-point power for the
# EXACT 2^8=256 cluster sign-flip joint rule (p <= 12/256 AND T_obs >= +3 pts).
# DGP = the F1-K planning premise family: C=8, n=300, m_c=[38]*4+[37]*4,
# paired per-item difference d_i in {-1,0,+1}; P(d_i != 0) = q = 0.15;
# cluster effect delta_c = delta + tau*z_c (points), tau = 12.91 pts
# (ICC rho = tau_f^2/(tau_f^2+q) = 0.10, tau_f = tau/100), delta_c clipped to
# [-100q, +100q] so P(+1 | d!=0) = (1 + delta_c/(100q))/2 stays in [0,1];
# z_c ~ Irwin-Hall(12) - 6 (approximate standard normal; deliberate pinned
# choice: pure add/mul arithmetic, bit-stable, no libm special functions).
# PRNG: counter-based SplitMix64, seed 20260728; per-delta counter block
# offset = delta_index * 2**32. Pure uint64/float64 arithmetic throughout.
import json, hashlib
import numpy as np

SEED = 20260728
C, MC = 8, np.array([38, 38, 38, 38, 37, 37, 37, 37])
N = int(MC.sum())            # 300
Q, TAU = 0.15, 12.91         # disagreement rate; cluster sd in points
NSIM = 20000
ALPHA_COUNT = 12             # reject iff #{s: T(s) >= T_obs} <= 12 (p <= 12/256)
FLOOR = 3.0                  # observed-margin leg of the joint rule, points
DELTAS = [3.0] + [6.0 + 0.5 * i for i in range(29)]   # 3.0 and 6.0..20.0 by 0.5

M = np.uint64(0xFFFFFFFFFFFFFFFF)
def splitmix64(idx):         # idx: uint64 array -> uniforms in [0,1)
    z = (idx.astype(np.uint64) + np.uint64(1)) * np.uint64(0x9E3779B97F4B7C15) & M
    z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9) & M
    z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB) & M
    z = z ^ (z >> np.uint64(31))
    return (z >> np.uint64(11)).astype(np.float64) * (2.0 ** -53)

SIGNS = np.array([[1 if (s >> c) & 1 == 0 else -1 for c in range(C)]
                  for s in range(256)], dtype=np.float64)   # all 2^8 sign vectors

def joint_power(delta, block):
    base = np.uint64(SEED) + np.uint64(block) * np.uint64(2**32)
    k = NSIM * C * 12
    z = splitmix64(base + np.arange(k, dtype=np.uint64)).reshape(NSIM, C, 12)
    zc = z.sum(axis=2) - 6.0                       # Irwin-Hall(12) approx N(0,1)
    dc = np.clip(delta + TAU * zc, -100 * Q, 100 * Q)
    ppos = (1.0 + dc / (100 * Q)) / 2.0            # P(+1 | d != 0), per cluster
    D = np.empty((NSIM, C))
    off = base + np.uint64(k)
    for c in range(C):
        m = int(MC[c])
        u1 = splitmix64(off + np.arange(NSIM * m, dtype=np.uint64)).reshape(NSIM, m)
        off += np.uint64(NSIM * m)
        u2 = splitmix64(off + np.arange(NSIM * m, dtype=np.uint64)).reshape(NSIM, m)
        off += np.uint64(NSIM * m)
        nz = u1 < Q                                # item disagrees
        d = np.where(nz, np.where(u2 < ppos[:, c:c + 1], 1.0, -1.0), 0.0)
        D[:, c] = d.mean(axis=1) * 100.0           # cluster mean, points
    T = D.mean(axis=1)
    ge = (SIGNS @ D.T / C >= T[None, :] - 1e-12).sum(axis=0)  # exact 256-flip count
    return float(((ge <= ALPHA_COUNT) & (T >= FLOOR)).mean()), float(T.std())

rows = []
for i, d in enumerate(DELTAS):
    p, sd = joint_power(d, i)
    rows.append({"delta_true_pts": d, "joint_power": round(p, 4),
                 "sd_T_pts": round(sd, 2)})
mde = next((r["delta_true_pts"] for r in rows[1:] if r["joint_power"] >= 0.80), None)
out = {"sim": "glm-drop-power-sim v1", "seed": SEED, "n": N, "m_c": MC.tolist(),
       "q_disagree": Q, "tau_pts": TAU, "icc_rho": 0.10, "n_sims": NSIM,
       "rule": "p<=12/256 exact 256-sign-flip AND T_obs>=+3pts",
       "power_at_true_plus3": rows[0]["joint_power"],
       "mde_true_sim_pts_at_0.80": mde, "grid": rows}
b = json.dumps(out, sort_keys=True, separators=(",", ":")).encode("ascii")
print(b.decode("ascii"))
print("OUTPUT-SHA256:", hashlib.sha256(b).hexdigest())
```

Pinned output (the canonical-JSON line, wrapped here for reading; the hash
is over the unwrapped bytes): joint_power by delta_true_pts — 3.0: 0.1188;
6.0: 0.2467; 6.5: 0.2719; 7.0: 0.3016; 7.5: 0.3316; 8.0: 0.3613; 8.5:
0.3885; 9.0: 0.4217; 9.5: 0.4482; 10.0: 0.4822; 10.5: 0.5192; 11.0: 0.5484;
11.5: 0.5848; 12.0: 0.611; 12.5: 0.6389; 13.0: 0.6734; 13.5: 0.703; 14.0:
0.7316; 14.5: 0.7508; 15.0: 0.7756; 15.5: 0.7944; **16.0: 0.8192** (first
grid point ≥ 0.80 ⇒ `mde_true_sim_pts_at_0.80` = 16.0); 16.5: 0.8394; 17.0:
0.8566; 17.5: 0.871; 18.0: 0.8896; 18.5: 0.8972; 19.0: 0.9112; 19.5:
0.9257; 20.0: 0.9323; `power_at_true_plus3` = 0.1188; sd of T ranges 4.14
(δ=3) → 2.92 (δ=20) pts. Freeze re-run rule: the SAME code bytes with ONLY
the `MC` line (and therefore `N`) replaced by the frozen realized m_c — that
one-line diff is part of the freeze manifest next to the new code + output
hashes; any other edit is an encoder-pin-style version change and re-opens
this section.

---

## R4. REVISION 4 — GPT-5.6 r3 re-review residual-closure audit [designer-20]

The standing GPT-5.6 re-review of the R3 design
(`poc/gpt56-review/expert-drop-r3/out/last-message.json`, sha256
afcbfe7e83084d2bb238b6c002f1d7b2ea102cd452abc346e7dc5cfa7e69b95a; pre-R4
document bytes sha256
a8372186d45b07dfa2b2f3678bef739894f001cd5f78f1bb0bab6e6e575e810c) confirmed
findings 1 and 2 RESOLVED (under the explicitly allowed F1-K sequencing) and
left findings 3, 8, 11, 12 PARTIAL. Scope split, per the review's own text:
the 11/12 residuals are the CENTRAL-REGISTRATION actions (register
ASM-2340..2352 with the landing commit; physically supersede central
ASM-2238/2291/2292) — coordinator-owned, already classified
SEQUENCED-WITH-LANDING-COMMIT (§R3.11/§R3.12) with the interim precedence
rule in force, and NOT touched by this pass (NO git, NO registry write). R4
closes the two DESIGN blockers:

3. **(PARTIAL → CLOSED, §2.1 item 3 + §3 + §3.1 item 3.)** "Top experts for
   the item's active concepts" is now ONE deterministic rule: per-cluster
   score = mean-centred conditional mass s_c(ℓ,e) with x_f/μ pinned to the
   `analyze_routing_v2.py` normalization (L1 over the full ever-active
   keyspace; float64; summation orders fixed by ascending fingerprint id);
   combination = PLAIN UNWEIGHTED SUM over the item's conditioning clusters
   in ascending cluster-index order (no quota, no max, no \|C(item)\|
   normalization — cardinality is matched across the item-conditioned arms);
   selection = single descending ranking over non-core experts, exact
   float64 comparison, ties → ascending expert index; fill = core ∪ ranked
   prefix to exactly 64/layer (total order guaranteed; never-active experts
   score exactly 0.0; no residual trim step exists). m-emb combines its
   MULTIPLE nearest clusters by the SAME rule with the frozen k-means member
   sets (cosine affinity selects clusters, carries no weight — weighted
   variants explicitly rejected); m-drng applies the m-kern rule verbatim to
   σ(i)'s label set. The three item-conditioned pipelines now differ ONLY in
   member sets and item→label assignment; no ambiguity that changes a
   realized mask remains.
8. **(PARTIAL → CLOSED, §6.3 [R4 block].)** The canonical serialization is
   pinned NOW: closed arm-ID set; all-ASCII/LF encoding; item-ID = the F1-K
   id string's UTF-8 bytes verbatim with `|`/`:`/control/non-ASCII bytes a
   halt; per-layer bit order (76 MoE layers ascending 3…78; 64 lowercase hex
   chars/layer; c_j = experts 4j…4j+3, expert 4j at the nibble MSB; 1 =
   retained; 64-bits-per-layer dose verified at load); record line format
   and ascending byte-lexicographic record order; per-entry hash frame =
   SHA-256(`glm-drop-mask:` ‖ arm-ID ‖ `:` ‖ record line sans LF); file
   layout fixed byte-for-byte (header : entry-hash lines : `--` : records);
   whole-table hash = SHA-256 over the complete file bytes as loaded. Each
   table is thereby a PURE FUNCTION of its pinned inputs; the ITEM LIST is
   the single sequenced-after-F1-K-freeze input (§5.1), explicitly the only
   thing table materialization waits on — the freeze pass makes NO
   serialization choice.

No resolved finding (1/2/4/5/6/7/9/10/13) is reworded, weakened, or touched
by R4; the §5.1/§5.2 population and inference pins, the §2.1 core and
concept→cluster hashes, Appendix A, and the §6.4 supersession text stand
byte-identical. The companion ASM file is amended in place again this pass
(still permissible: the block remains centrally unregistered; pre-R4
companion bytes sha256
3bf0dd5a83290aa42521fcf6e6e159dba7e9037453e3da2a1e67fd081772431d) with
inline "[R4 amendment, designer-20, 2026-07-13: …]" provenance on ASM-2344
and ASM-2349 only.

---

## Self-check gate (governance)

Every load-bearing claim above carries EXACTLY one of MEASURED / LIT-BACKED /
STIPULATED / EXTRAPOLATION — the closed four-tag schema; no other tag token
appears in this document's convention, tags, or this self-check, and the two
tags the R0/R1 convention permitted beyond the schema are retired [R2].
Every MEASURED tag cites an artifact whose FULL SHA-256 is in the header
table plus the exact JSON key or log line/section; every EXTRAPOLATION
(ASM-2341, ASM-2350) is load_bearing:false with a resolution path pointing at
the pinned freeze simulation or the metered cost ledger — never at quality
metrics; every STIPULATED choice carries an ASM id in ASM-2230..2239,
ASM-2290..2293, or ASM-2340..2352 with a rationale in its companion record.
Both directions of every gate (D0/D1/D2, the §4.2 STOP, the §5.1
coverage/thin-cluster gates, the power shortfall) are worded in advance, and
no failed superiority reading is worded as equivalence anywhere (§5.3 [R2]).
The deflator arms (uniform-TOPK at matched loads; item-unconditioned
frequency; matched-multilabel embedding-cluster; dose-exact label-deranged
knull mask ×3 realizations) are mandatory before any kernel-specific sentence;
D2 requires beating EACH in its own named contrast (never a best-of); all
masked arms are dose-exact with the SAME frozen universal core (**[R3]
algorithm frozen AND executed: τ = 0.50, cap 48, tie-breaks stated; realized
76-layer / 2,108-cell core published in §2.1 with in-document sha256
632bcd18…4cd3f18f; freeze re-verifies byte-identity**), and **[R4] the
multilabel COMBINATION rule is pinned once for all item-conditioned arms
(summed per-cluster mean-centred conditional mass, ascending cluster-index
summation order, single descending ranking, ascending-expert-index
tie-break, fill to exactly 64; §2.1 item 3, §3, §3.1 item 3) — m-emb's
multiple nearest clusters and m-drng's deranged label sets combine by that
same rule; no per-arm combination freedom exists**. The probe
coverage is stated as 24 prompts across 8 concept clusters over 76 MoE
layers [R3 correction]; the analysis
population, cluster rule (executable: longest match → earliest span → table
order [R3]), estimand, and exact 256-flip inference are frozen
with their fail-closed gates; the power analysis is a true-effect MDE under
the joint rule at C = 8 — **[R3] the pinned simulation is RUN at the
planning point (Appendix A; code 1dc1682a…, output 9cdd2c01…, seed 20260728,
all 256 flips enumerated): simulated MDE_true ≈ 16 pts at n = 300, joint
power 0.119 at true +3, superseding the Gaussian planning figures and quoted
in every §5.3 resolution scope** — with the withdrawn 0.90-at-+3 target
recorded as withdrawn. **[R3; R4] Every pin in this design is now one of:
(i) materialized/frozen in-document (core + its sha256, concept→cluster
table + its sha256, simulation code + output sha256s, all seeds, the DRBG,
the k-means spec, **[R4] the multilabel combination rule and the mask-table
canonical serialization + per-entry/whole-table hash framing — the exact
bytes under every hash are now specified in §6.3**);
(ii) an explicitly SEQUENCED pin — a pure function of named frozen inputs,
hashed at prereg-freeze, fail-closed on absence or mismatch, with the reason
it cannot exist earlier stated where it lives (eligible set + n + m_c,
derangement realizations, mask-table BYTES + hashes — **[R4] waiting solely
on the eligible-item list, with no serialization choice left to the freeze
pass** —, dev-96 id-list hash, encoder-weights
hash, the simulation re-run at realized m_c); or (iii) a named external gate
with a fail-closed default (the #28 C-patch approval, central registration
by the coordinator). No pin is an unclassified deferral.**
Kernel-specificity is recorded OPEN pending the R4 REPLAY of
`interpretation-fable.md` §2 (§7 item 1 — the offline M_oracle/M_kernel
replay, distinct from this document's REVISION 4), not
assumed. No feasibility conclusion is stated. No frozen record, verdict,
encoder pin, or registered assumption is touched; `registry/assumptions.jsonl`
is not written; no git action, no model run, no spend occurs in this pass
(R3's computations are CPU-only mechanical derivations over committed bytes
and a pinned planning simulation — no GLM-5.2 process, no instance, ~$0;
REVISION 4 is text-only pin-tightening over already-committed bytes — no
computation beyond hashing, no model, no spend, no conclusion).
Companion assumptions:
`poc/glm52-probe/asm-glm-drop-2230-2239.json` (R0, intact),
`poc/glm52-probe/asm-glm-drop-r1-2290-2293.json` (R1, intact), and
`poc/glm52-probe/asm-glm-drop-r2-2340-2352.json` (REVISION 2; owner
designer-12; range verified free at emission — central register tail
ASM-2293, repo-wide grep for `ASM-23[4-9][0-9]` empty; **[R3] amended in
place by designer-17 with inline per-record provenance — see the
header note; pre-R3 bytes hashed in the header**; **[R4] amended in place
again this pass by designer-20 — ASM-2344 and ASM-2349 only, inline
provenance; still permissible because the block remains centrally
unregistered; pre-R4 bytes hashed in the header**). Central registration
of the (now R4-amended) block and the §R2.14 supersession edits is the
coordinator's action, with the landing commit, after the standing GPT-5.6
review gate; the design is not freeze-eligible before that registration
lands.
