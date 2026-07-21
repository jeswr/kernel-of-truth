# colibri recon (2026-07-21) — current state mapped to programme seams

**Provenance (mechanical):** produced by the `colibri-recon` workflow (4 general-purpose research agents — capabilities / changelog-since-~Jul-10 / code-seams / issues-roadmap — → Opus synthesis; run `wf_7fe6be61-fa1`, 5 agents, ~399k tokens). SHAs/line-refs verified via `gh api`. This is a **research readout, not a decision**; design implications are flagged for Fable/maintainer. Relates to the GLM-5.2 shrink north-star.

## colibri (JustVugg/colibri) — current state mapped to programme seams S1/S2/S3

**Research readout, not a decision. Nothing here commits the programme to an architecture.** Repo at survey: `main` @ HEAD `153e6f4c` (2026-07-20), 17.3k stars, Apache-2.0, pure-C engine `c/glm.c` (~6.6k lines; a refactor split to `colibri.c` merged as #391 `72874f38a2` but `glm.c` remains on `main` — symbol/line refs are against `glm.c` HEAD). First tagged release **v1.0.0 landed 2026-07-19**. All four research facets (capabilities / changelog / code-seams / issues-roadmap) agree; SHAs verified via `gh api`.

> **Terminology guard:** everywhere in colibri, "kernel" means a *compute/SIMD kernel*. `SPEC_PIN=1` "kernel-pinned verification" = pinning draft+verify to one **compute-kernel** family, NOT a concept/knowledge kernel. Nothing in colibri maps to our concept-kernel — that remains ours to add.

### What's new since ~2026-07-10
- **v1.0.0 first tagged release** (07-19; CHANGELOG, release infra `05bba7994c`): semver + GitHub Releases + prebuilt Windows binaries.
- **S1 pruning lever built then QUARANTINED** — the headline S1 datapoint. `EXPERT_BUDGET=N` (miss-aware distinct-expert cap) landed #254 `a6895445a9` (07-15), then was forced to 0 unless `EXPERT_BUDGET_EXPERIMENTAL=1` via #303 `35f90b9e76` (07-16, gate `glm.c:6297`): measured empty operating window (budget=8 → HellaSwag **30% vs 90%** off; budget=4 → literal noise; MTP acceptance 56%→**0%**).
- **CACHE_ROUTE** — new S1 routing-side lever (#199 `62419af188`, 07-14): opt-in max-rank cache-aware routing, emits `swap%`/`route_agree`/`route_kl`.
- **Introspection now first-class in-engine:** `ROUTE_TRACE=<path>` per-(pos,layer) dump + coupling tools + `COUPLE` prefetch (#176, 07-14); **Expert Atlas** harness `c/tools/expert_atlas/` (#218/#245/#175, 07-15). `LOOKA=1` + `PILOT` shipped #12 `0778942` on **07-10** — the likely edge of our last build.
- **Tier-split telemetry** `hit_pin` vs `hit_ecache` (#336 `679c0742`, 07-17).
- **Measured-RSS guard** `rss_guard()` `glm.c:4947` + `RSS_GUARD_GB` + startup projected-peak `exit(2)` guard + `COLI_RAM_OVERCOMMIT` (#403 `c90e2cc43`, 07-19) — a measured RAM ground-truth for pruning experiments.
- **S2:** `SPEC_PIN=1` made default (#294); MTP int8 repair `repair_mtp_int8.py` (#397); grammar-forced drafts `GRAMMAR=` (#48/#70 `cec7d6b`, 07-11).
- **S3 primitives (structural only):** GBNF engine `c/grammar.h` w/ `gr_admissible`/`gr_forced`; JSON-Schema→GBNF `schema_to_gbnf()` via `SCHEMA=` (#148, 07-14). No semantic grounding.
- **Tool-calling landed end-to-end** in `c/openai_server.py` (#401 `2122c004d9` / test #408, 07-19) — note `docs/api.md` prose is **stale** (still claims tools error).
- **MTP-in-serve gap** surfaced as open FRs #358/#492 (#492 filed 07-21).
- **Model-agnostic pivot** on the roadmap (maintainer #406/#430; Kimi K3 / DeepSeek V4 / Inkling candidates) — colibri is generalising beyond GLM-5.2.

### Seam-by-seam mapping

#### S1 — MoE routing / pruning (incl. TOPK shrink lever + STATS/LOOKA probes) — richest surface
**Available now.** Our three probes are built-in env instruments: `STATS=<file>` histogram (`stats_dump_q()` `glm.c:5782`, invoked `:6554`); `LOOKA=1` predictability across 3 horizons (`glm.c:3050-3062`, footer `:4858`); `ROUTE_TRACE=<path>` per-(pos,layer) top-K dump, zero compute effect (`glm.c:3038-3042`). Shrink/routing levers as env vars: `TOPK`/`--topk` global count cut (`g_topk` `glm.c:1137`, applied `:2925`; sanctioned path `--policy experimental-fast --topk 4`), `TOPP` adaptive keep, `CACHE_ROUTE` cache-aware max-rank routing (#199, emits `swap%`/`route_agree`/`route_kl`), `PILOT`/`PILOT_TWO`/`COUPLE` lookahead prefetch (do not change expert IDs). Tooling: `c/tools/expert_atlas/` (`analyze.py`/`validate.py`/`sweep.sh`) + `route_coupling_report.py` + `route_pairs.py` (measured: LOO 96.7%, only **7.9% strong specialists**). Tier-split telemetry `hit_pin`/`hit_ecache` (#336); measured RAM ground-truth `rss_guard()` + `RSS_GUARD_GB` (#403).

**Plug-in point.** `moe()` at **`c/glm.c:2871`** owns routing+selection+streaming+compute (router matmul `:2919`; sigmoid+bias scoring `:2923`; plain top-K selection loop `:3010-3015`). STATS/LOOKA/ROUTE_TRACE/TOPK/TOPP/CACHE_ROUTE sweeps need **no code** (env only). A per-expert-ID **skiplist does NOT exist** and is a ~10-line add: filter in the selection loop (`if(skiplist[best]) continue;`) or post-selection compaction mirroring `EXPERT_BUDGET`'s `idxs[]`/`keff[]` rewrite at `:3115-3130`; dropping an eid before FASE C (`:3137`) prevents the disk load. Stream/cache path is fully eid-keyed.

**Gap.** Naive drop-experts/skiplist shrink is **empirically quarantined** (EXPERT_BUDGET empty window). Binding constraint: any change to *which experts fire* fights MTP speculation unless applied identically in draft+verify (`SPEC_PIN`). Atlas shows ~92% of experts are not strong specialists, so "one expert = one topic" pruning intuition is wrong. **A kernel-driven S1 shrink must beat this measured bar (quality gate + MTP contract), not re-propose capping.** The live datapoint argues the kernel's S1 value is more likely in *smarter routing/placement* than in raw expert-count reduction.

#### S2 — engine-as-speculative-decoder — mature but interior-only
**Available now.** Internal spec-decode is complete: three draft sources — n-gram `ngram_draft()` `glm.c:4133`, GLM's native MTP head `mtp_draft()` `:4152`/`mtp_absorb()` `:4192`, grammar-forced `grammar_draft()` `:4283` — all feed **one batch-union verify forward** (`moe()` handles S>1). `SPEC_PIN=1` default (#294/#163). MTP head must be int8 (int4 → 0-4% acceptance, #8; `repair_mtp_int8.py` #397). Grammar-forced drafts are guaranteed-accepted, lossless by construction, with adaptive shut-off <50%.

**Plug-in point.** The reusable primitive is the **draft-source abstraction** (all three emit an `int *draft` verified identically) — generalise it to accept an *external* draft buffer for the target-side path (verify machinery already exists). Grammar-forced drafts are the shipped pattern for "inject external constraints as pre-accepted drafts, let the target verify losslessly."

**Gap.** It is GLM's **own** MTP head, not an external kernel-grounded drafter — a kernel drafter is net-new. No external spec-decode HTTP interface: server has **no logprobs** (`openai_server.py:400-401` raises), no draft-submission endpoint. MTP is **off in serve** (`SERVE_BATCH=1`→`g_draft=0`; ~1 tok/s vs interactive 2-3 tok/forward; open #358/#492). Regime caveat: speculation **loses at full residency** (#472: DRAFT=0 3.65 vs DRAFT=3 2.65 tok/s) — MTP's win is disk-streaming-specific.

#### S3 — grounding-checker — does not exist; net-new but wide open
**Available now.** No grounding/verification-against-knowledge hook anywhere (`grounding`→0, `checker`→0 in code). Only **structural** primitives: GBNF engine `c/grammar.h` (`gr_admissible` byte-class mask `grammar.h:333`, `gr_forced` `:349`), wired via `GRAMMAR=` at `grammar_setup()` `glm.c:4228`; JSON-Schema→GBNF `schema_to_gbnf()` `c/schema_gbnf.h:220` via `SCHEMA=`; tool-call parse/validation in `openai_server.py` (`parse_tool_calls` `:244`, `COLI_TOOL_SALVAGE`); `REF`/`REF_FORCE`/`TF` A-B validation.

**Plug-in point.** Three net-new insertion points (primitives exist, wiring does not): (1) turn `gr_admissible` into a per-step **hard logit mask** in the sampler (grammar is currently draft-only, *never* a hard constraint); (2) post-sample hook at the emit site `gr_feed(t)` `glm.c:4269`; (3) server-side in `openai_server.py`.

**Gap.** Entire seam is net-new — colibri has neither built nor rejected it. Upside: live, unowned quality defects a grounding layer could target — #108 (int4 62.5% mean acc_norm vs 85-95% expectation; scoring-confounded), #455 (stochastic reasoning loops / EOS starvation, no loop protection), #401 (tools return plain text in serve).

### Proposed next experiments (tagged)
1. **[MECHANICAL-PROBE]** Refresh routing baseline on v1.0.0: `STATS=<file> LOOKA=1 ROUTE_TRACE=<path>` on a fixed prompt battery with atlas discipline (`TOPP=0 MTP=0 DRAFT=0`, clear `.coli_usage` per run) → `expert_atlas/analyze.py`; captures the new `hit_pin`/`hit_ecache` + `route_agree`/`route_kl`. No code.
2. **[MECHANICAL-PROBE]** TOPK shrink sweep via existing knob: `--policy experimental-fast --topk {8,6,4}` + `coli bench mmlu,hellaswag,arc_challenge` + `RSS_GUARD_GB`/tok-s logging; independently reproduces the pruning quality cliff through the TOPK path (distinct from the quarantined EXPERT_BUDGET) and quantifies the tradeoff curve on our hardware. Config-only.
3. **[MECHANICAL-PROBE]** CACHE_ROUTE characterization: `CACHE_ROUTE=1` vs stock under disk-streaming, capturing `swap%`/`route_agree`/`route_kl` + bench quality to bound how far routing can be redirected toward resident experts before quality moves. Config-only (expect neutral at full residency).
4. **[MECHANICAL-PROBE]** MTP-in-serve uplift check per #492 trace: force `SERVE_BATCH=0 --kv-slots 1`, measure whether MTP re-engages + serve tok/s uplift. Low-cost; flag it uses an unsupported config path.
5. **[DESIGN DECISION for Fable/maintainer]** Whether to prototype any net-new code seam — (a) per-expert-ID skiplist in `moe()` driven by a kernel importance ranking; (b) `gr_admissible`→hard sampler mask for S3; (c) external-drafter S2 interface. All are architecture-bearing engineering, not mechanical probes.

### Caveats / unknowns
- **EXPERT_BUDGET quarantine is a negative result about *naive* pruning**, not about smarter routing/placement — do not over-read it as "S1 is dead."
- `docs/api.md` prose is **stale** (says tools error); trust code+tests (#401/#408).
- #108's 62.5% int4 quality is **scoring-protocol confounded** (0-shot LL-MC on a reasoning model, no fp16 control) — not a clean capability number. TF oracle reported 30/32 not 32/32 on `glm_tiny` (#482).
- The crush recipe's `context_window: 131072` is a **display budget**; engine `CTX` default is 4096 (`glm.c:5335`).
- If colibri later removes `glm.c` (post-#391 refactor), the cited line numbers move — symbols (`moe`, `rss_guard`, `mtp_draft`, `gr_admissible`) are the durable anchors.
- **Regime dependence:** both speculation (S2) and CACHE_ROUTE (S1) neutralize/lose at full RAM residency; our seam value is measured in the **disk-streaming** regime.
- **Model-agnostic pivot** means any GLM-5.2-specific kernel assumption is against a moving target.
