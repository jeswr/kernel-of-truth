# GLM-5.2 Stage-4 SPEED-validation cohort — `glm-s4speed-0` prereg-shaped design

> **Status: DESIGN ONLY, revision r3 (designer-1, Fable experiment-design role,
> 2026-07-16; r2 same day closed the design-integrity review's NEEDS-WORK items
> — closure map in §13; r3 same day closes the round-2 review's four
> internal-consistency residuals — closure map in §13.1). Nothing here is
> frozen, registered, scheduled, or run;
> no model run, no spend, no git action, no registry write occurs in this pass.
> This document states NO feasibility conclusion — it designs the cohort that
> would produce one. UNCOMMITTED — the coordinator commits after the standing
> GPT-5.6 review gate.**
>
> **ASM block claimed: ASM-2479..2484** (companion file
> `docs/next/design/asm-s4speed-2479-2484.json`, owner designer-1; range
> re-verified free at r2: the central register tail is now ASM-2478 in
> `registry/assumptions.jsonl` (ASM-2473..2478 registered with the gpt56
> draft-pipeline landing, `docs/next/design/gpt56-draft-pipeline-large-kernel.md`
> §12.1); the adjacent working-tree block ASM-2485..2491 belongs to the f1k
> dump-patch companion (`poc/glm52-probe/f1k-harness/dump-patch/asm-f1k-dump-2485-2491.json`)
> and does not overlap; a repo-wide grep for `ASM-24[7-9][0-9]` /
> `ASM-25[0-9][0-9]` over docs/poc/registry/notes/reports shows no other
> claimant of 2479..2484). The six ASM ids are LOCKED; ASM allocation is the
> COORDINATOR's, and central registration is the COORDINATOR's action with the
> landing commit; until then any change to the companion file is amend-in-place
> with inline provenance, and after registration it is supersede-by-citation
> only.
>
> **Relationship to `glm-s4drop-0` (frozen sibling, MUST NOT be confused):**
> `registry/experiments/glm-s4drop-0.json` + `docs/next/design/glm52-stage4-drop-efficiency.md`
> is the QUALITY-primary Stage-4 leg: composite-mask quality at matched
> removed-I/O, EXPERT_BUDGET **off**, DRAFT=0 (MTP out of scope), static
> S4_TABLE masks. THIS design is the complementary SPEED-primary leg: decode
> tok/s with **MTP on** and **EXPERT_BUDGET on**, causal skiplist vs the shipped
> blind heuristic at matched cap. The two share pinned corpora where lawful and
> share NO verdict; neither outcome is evidence for the other's endpoint.

## §0 Position in the programme

- Stage-3 causal ablation is COMPLETE [MEASURED:
  `poc/glm52-probe/stage3/results/full/stage3_analysis.json`]: 32 shortlisted
  cells, 244 items / 1,546 teacher-forced prefills → a 16-cell skiplist,
  `causal_confidence` 0.504–0.812 (an UNCALIBRATED evidence-agreement score),
  9 cells with `swap_to` targets, 7 pure-drop. Interpretation and load-bearing
  limits: `docs/next/analysis/stage3-causal-interpretation.md` [STIPULATED:
  ASM-2383 — individual-ablation, mean-ΔNLL-only, final-logit, enriched
  gate-failed-atlas shortlist; **no population rate, no simultaneous-drop
  guarantee**].
- Stage-3 evidence is FINAL-LOGIT ΔNLL only. It says NOTHING about
  autoregressive decode speed, MTP acceptance drift, or simultaneous-drop
  safety [MEASURED: same interp, §3(a), §2(d)]. This cohort MEASURES the
  decode speedup at matched quality.
- GATE PURPOSE: this cohort is the gate that unblocks the public colibri
  Show-and-Tell (#208). Until it lands with a positive LOWER-BOUND tok/s delta
  at matched quality, we post nothing — consistent with
  `docs/next/analysis/glm52-colibri-research-novelty-20260715.md` (bottom
  line): gate the post on causal evidence (done, Stage-3) AND "a positive
  lower-bound speed delta at matched quality" A/B'd against colibri's own
  EXPERT_BUDGET/CACHE_ROUTE. #207 stays PAUSED regardless of outcome;
  deterministic replacement stays unevidenced either way (Stage-3 caveat ii:
  zero DETERMINISTIC-REPLACEABLE cells).
- HONEST PRIOR, disclosed up front [ESTIMATE — never a decision premise]: the
  skiplist is 16/19,456 ≈ 0.08% of cells on 14 of the 76 MoE layers (3..78)
  [MEASURED: ASM-2342 + stage3_analysis.json skiplist]; the sibling
  design's full-scale mock put the 16-cell core at ~0.06% of decode
  expert-miss-I/O (SYNTHETIC telemetry). At matched cap the experts-computed
  channel is closed BY CONSTRUCTION (§2), so the live channels are cache
  composition and MTP acceptance only. The pre-registered null (§1) is
  therefore the likely outcome; the design's job is to buy that answer cheaply
  and irreversibly, with pre-spend stops so we never fund a verdict fixed in
  advance.

## §1 Claim and falsifiable hypotheses

**CLAIM under test.** Applying the 16-cell causal skiplist inside colibri's
shipped EXPERT_BUDGET mechanism yields a decode tok/s improvement with a
positive one-sided 95% lower bound versus the blind EXPERT_BUDGET heuristic at
the SAME cap, at matched output quality, with MTP on.

- **H-S (primary, falsifiable):** at matched cap N=4, arm (c) beats arm (b) on
  paired per-prompt decode tok/s: one-sided 95% lower bound of the pooled
  relative delta Δ_spd > 0 AND point estimate ≥ SESOI +3% [STIPULATED:
  ASM-2482 — a sub-3% delta is not postable].
- **Pre-named NULL (stated, not asserted):** at matched cap, blind gate-weight
  dropping and causal-skiplist exclusion mostly coincide (the skiplist cells
  are rarely kept by the blind rule anyway), so which cells drop changes
  nothing measurable: Δ_spd ≈ 0 and the causal layer adds no deployable speed
  value over the shipped heuristic at this cap.
- **H-M (MTP, first-class):** acceptance((c)) ≥ acceptance((b)) − 5pp
  (one-sided 95% lower bound of the paired difference ≥ −5pp, INCLUSIVE — the
  equality case PASSES; §5 states the identical ≥ −5pp bound) [STIPULATED:
  ASM-2483].
  Context: EXPERT_BUDGET alone already degrades acceptance 38%→21%
  [LIT-BACKED: colibri #254 thread, via
  docs/next/analysis/glm52-colibri-research-novelty-20260715.md A3; upstream
  figure, not re-measured locally]; arm (a) re-measures the shipped-baseline
  acceptance on the pinned commit.
- **H-Q (matched quality — a GATE, not a headline):** (Q1) mean ΔNLL((c)−(b))
  one-sided 95% upper bound < +0.05 nats/target-token on the pinned quality
  suite; (Q2) task accuracy acc((c))−acc((b)) point estimate ≥ −5pp overall
  AND no single stratum-domain drops > 15pp (screening-grade, disclosed as
  such); (Q3, no-post backstop) mean ΔNLL((c)−(a)) point estimate < +0.15
  nats/tok [STIPULATED: ASM-2481]. A speedup at degraded quality is a KILL,
  not a win.
- **H-SD (simultaneous-drop, pre-registered question — §7):** forcing all 16
  cells out AT ONCE in the deployment regime (cap on, MTP on) holds H-Q and
  H-M. Stage-3 ablated cells INDIVIDUALLY; there is NO prior evidence for
  this [MEASURED: stage-3 interp §2(d); STIPULATED: ASM-2383].
- **H-R (secondary, descriptive):** the swap arm (d) (9 `swap_to` remaps + 7
  drops) does not degrade quality or acceptance versus drop-only (c). Never
  pooled with (c); disclosed caveat: main|63|217→206 swap-arm mean ΔNLL was
  +0.0795, above the 0.05 line [MEASURED: stage3_analysis.json / interp §3].

## §2 Arms (IVs) and mechanism

| arm | config (all else identical) | quality (300 prefills + 120 acc) | throughput (2 passes) |
|---|---|---|---|
| (a) `spd-base` | merged pinned colibri, EXPERT_BUDGET off | ✓ (ladder rung 2 may cut) | ✓ |
| (b) `spd-blind` | EXPERT_BUDGET cap N=4, shipped gate-weight rule | ✓ | ✓ |
| (c) `spd-causal` | EXPERT_BUDGET cap N=4 + 16-cell forced exclusion | ✓ | ✓ |
| (d) `spd-swap` (optional) | as (c), but 9 cells remap to `swap_to` targets | ✓ | ✓ (ladder rung 1 cuts first) |

- **The head-to-head that matters is (c) vs (b) at matched cap.** (a) provides
  the shipped-baseline context numbers (absolute tok/s, absolute acceptance)
  for the eventual post and the no-post backstop Q3; it carries no clause of
  the primary.
- **Mechanism of (c) [STIPULATED: ASM-2480].** EXPERT_BUDGET (colibri #254,
  MERGED) caps distinct experts/layer across the batch-union: keep cache hits
  + highest-aggregate-gate-weight misses, drop the rest (never loaded)
  [LIT-BACKED: colibri #254 via the novelty doc A3]. Arm (c) removes the 16
  skiplist cells from the CANDIDATE set BEFORE the budget fill, with
  route-around renormalise semantics for any token that routed to them
  (identical to stage-3 mode-2); the keep-set then fills to the same ≤N from
  the remaining candidates. Consequence: both arms target the SAME effective
  keep-set size (cap N); at every (prompt × layer) site where the shipped
  budget binds in (b) — effective distinct-expert count = N — arm (c)'s count
  equals N EXACTLY; a count discrepancy is lawful ONLY where the budget is
  slack AND equals exactly the number of routed-but-excluded skiplist cells at
  that site (mechanically verified from PROF, §8 gate G6 — the identical
  exact-parity rule as the paired-parity bullet below); the arms differ only
  in WHICH cells drop. The contrast therefore isolates the
  marginal value of the causal information inside the shipped mechanism —
  exactly the "principled per-layer EXPERT_BUDGET exclusion" consumption path
  named by the Stage-3 interpretation §3.
- **Estimand, confirmed (OQ-2 RESOLVED by review ruling, r2).** The estimand
  is **identical N inside EXPERT_BUDGET with forced exclusion**: blind budget
  fill vs budget fill over a candidate set with the 16 skiplist cells removed,
  at the same cap N=4, everything downstream identical. The alternative
  reading (pure 16-cell mask at matched dose, no budget) is overruled as
  speed-vacuous (§12 OQ-2).
- **Semantic-parity obligation (r2, closes the arm-(c) parity CONCERN).**
  Arm (c) executes the SAME shipped keep-set builder and the SAME
  drop/route-around-renormalise code path as arm (b); the S4SPEED patch
  inserts exactly ONE candidate-eligibility filter upstream of the budget
  fill. A token whose expert is not kept receives the identical renorm
  treatment in both arms — in (b) because the blind rule dropped the cell, in
  (c) because eligibility excluded it; the treatment function is shared,
  byte-identical code in one build. **Differential proof that only candidate
  eligibility changes** (all three legs required, fail-closed):
  1. **Patch-scope check (static):** the pinned S4SPEED diff touches ONLY the
     candidate-set construction inside the EXPERT_BUDGET keep-set builder —
     a mechanical file+function allowlist over the diff hunks; any hunk in
     drop, renormalisation, dispatch, or MTP code fails the check (verified
     against the sha256-pinned diff at bring-up, gate G1).
  2. **Empty-table inertness (dynamic):** gate G3 — empty exclusion table →
     byte-identical outputs to the unpatched build (stage-3 inertness
     discipline).
  3. **Keep-set attribution (dynamic, on the pilot prompts):** paired
     (b)/(c) PROF + `.coli_usage`/STATS traces (#175 mechanism) must show
     every keep-set difference is exactly attributable to skiplist-cell
     eligibility — keep_set(c) = budget-fill(candidates ∖ skiplist) under the
     same shipped rule, recomputed offline from the trace fields; if the
     pinned commit's trace fields are insufficient to recompute the fill,
     gate G2 fails closed. Any non-attributable difference →
     INSTRUMENT-INVALID (gate G6).
- **Exact paired parity (r2, strengthens G6 beyond per-layer means).** For
  EVERY (prompt × layer) site: keep-set size ≤ N in both arms (exact);
  wherever arm (b)'s effective distinct-expert count equals N (the budget
  binds), arm (c)'s count equals N EXACTLY; a count discrepancy is lawful
  ONLY where the budget is slack AND equals exactly the number of
  routed-but-excluded skiplist cells at that site. Any other discrepancy →
  INSTRUMENT-INVALID (§8 gate G6; the old within-1% per-layer-mean check is
  retained as a cross-check only, never the gate).
- **Implementation seam (OQ-1 RESOLVED by review ruling, r2).** (c)/(d) use a
  **separate, minimal S4SPEED patch at the EXPERT_BUDGET keep-set seam** (an
  exclusion/remap table consulted by the candidate-set construction). The
  frozen sibling's committed s4drop S4_TABLE patch surface is **NOT
  modified** — no shared mutable surface with a frozen design; the
  differential proof above is REQUIRED for the S4SPEED patch. The patch diff
  sha256 is PINNED-AT-INPUTS by ops amendment BEFORE any spend; an EMPTY
  table must be byte-inert (bring-up gate G3 mirrors the stage-3 inertness
  proof: 18/18 checks, 0.0 logit diff on unused-cell ablation [MEASURED:
  poc/glm52-probe/stage3/stage3_summary.md]).
- **Cap choice.** N=4 [STIPULATED: ASM-2480]: the operating point at which
  upstream reported +75% decode tok/s / 253 GB I/O saved on a 24 GB host
  [LIT-BACKED: colibri #254] — i.e. the cap at which the budget BINDS hard and
  the blind rule does real damage (38%→21% acceptance), giving the causal
  information its best chance to matter. Bring-up gate G4 verifies the budget
  binds on our box; if it never binds, the head-to-head is vacuous → STOP.
- **Vacuity stop (pre-spend).** At bring-up, count skiplist-cell keep events
  under arm (b) config on the pilot prompts (via `.coli_usage`/STATS snapshot
  diff — the established #175 mechanism — plus PROF expert-I/O accounting).
  If the count is ZERO, then (b) ≡ (c) on this workload, Δ_spd is
  mathematically 0, and the campaign is a verdict fixed in advance →
  REGISTERED construction STOP, salvage the telemetry, return to the
  coordinator (§9 STOP-V; §10). A nonzero-but-small count PROCEEDS with the
  measured divergence rate disclosed — no stipulated floor masquerades as
  physics; the acceptance channel is nonlinear in which expert breaks.
- All arms: greedy decoding, **DRAFT=1 (MTP speculative decode ON — this
  cohort's entire point) as an EXACT pin, identical across arms**; every
  further MTP/SPEC_PIN knob the pinned commit exposes is enumerated with its
  EXACT value by the pin ops amendment and re-verified fail-closed at G1
  (§4.1 — no knob is left at an unstated "shipped default"), TOPK=8 (exact),
  PIN=auto (exact; #301, identical across arms), CACHE_ROUTE OFF in (a)/(b)/(c) and
  consulted ONLY for arm (d)'s remap table, PROF=1 ON everywhere (identical
  observer effect cancels in paired deltas; overhead numerically bounded ≤ 5%
  AND disclosed via G5),
  identical cache config (RAM_GB=55, the proven GO-FULL-GLM52 config
  [MEASURED: stage3_summary.md cost section]). ONLY EXPERT_BUDGET and the
  exclusion/remap table vary. [STIPULATED: ASM-2479 §4]

## §3 DVs and the instrument: colibri PR #232 `PROF=1`

The measurement harness is colibri PR #232 `PROF=1` (expert-I/O accounting,
hit-rate, tier-fill, per-forward latency percentiles, phase shares) — cited as
the instrument of record; this cohort hand-rolls NO instrumentation PROF
already provides [STIPULATED: ASM-2479; the exact field names are verified at
bring-up against the pinned commit — gate G2 fails closed if any required
field is absent].

| DV | source | role |
|---|---|---|
| **Decode tok/s (PRIMARY)** | harness wall-clock over the fixed-T generation loop (prefill excluded), per prompt; PROF per-forward latency percentiles + phase shares as cross-check and drift gate (G5) | primary endpoint §5 |
| **MTP acceptance rate** | engine speculative-decode acceptance counters on the pinned commit (accepted draft tokens / proposed, **PER PROMPT — OQ-5 RESOLVED by review ruling: aggregate-only counters are a G2 FAILURE; no interval-free aggregate fallback exists**; exact counter name bring-up-verified; #294 SPEC_PIN context) | first-class DV, H-M gate + mechanism attribution |
| **Quality: NLL** | teacher-forced mean NLL/target-token on the pinned 300-item suite, one prefill per (item × arm), under full arm config | gate Q1/Q3 |
| **Quality: task accuracy** | 120-item exact-answer set (§4), free-running greedy under full arm config, exact match | gate Q2 |
| **Expert-I/O bytes/token, hit-rate, tier-fill** | PROF expert-I/O accounting | mechanism DVs: verify matched cap (G6), attribute any Δ_spd (cache composition vs acceptance), no-double-count audit vs upstream wins (§4) |
| **Phase shares** | PROF | verify decode-phase dominance of the timed region; attribute deltas |

- MTP subtlety carried as a design premise [MEASURED: colibri #294, upstream
  measurement, not re-verified locally]: draft & verify must compute the same
  function; EXPERT_BUDGET already degrades acceptance 38%→21% [LIT-BACKED:
  #254]. A skiplist that speeds raw forwards but tanks acceptance shows up
  DIRECTLY in the primary (tok/s is end-to-end with MTP on); H-M additionally
  bounds the acceptance drift itself, and the kill composition in §9
  implements the pre-registered rule: acceptance-tank + (net slower OR quality
  worse) = KILL.
- Accuracy under MTP: speculative verification preserves the verifier's greedy
  output, so Q2 measures the arm's verifier config, not draft luck
  [LIT-BACKED: #294 SPEC_PIN premise; re-checked at bring-up by comparing one
  arm-(b) accuracy item DRAFT-on vs DRAFT-off — mismatch → G2 fails].

## §4 Pinned inputs and the MOVING-BASELINE constraint [STIPULATED: ASM-2479, load-bearing]

The colibri baseline is a moving target: #301 PIN=auto and #294 SPEC_PIN are
already MERGED; #223 cloxcache and #168 int3-g64 are in flight [STIPULATED,
task-relayed estate state; backing_ref = the two merged PRs]. Therefore:

1. The cohort pins ONE specific merged colibri commit (40-hex recorded by ops
   amendment BEFORE any spend; it MUST contain the #232 PROF, #294 SPEC_PIN,
   and #301 PIN=auto merges — bring-up verifies all three are present in the
   pinned tree, fail-closed).
2. Anything merged upstream AFTER the pin (#223, #168, anything else) is OUT
   of this cohort. All four arms run the SAME pinned commit; a claimed
   skiplist speedup therefore CANNOT silently double-count an
   eviction/cache/pin win that landed upstream — those wins are inside ALL
   arms' baseline, and the (a)-arm records their absolute effect on this box
   for the post.
3. Knobs held FIXED across all arms, as EXACT pins (§4.1): PIN=auto, cache
   config / RAM_GB=55, TOPK=8, DRAFT=1 plus the enumerated MTP/SPEC_PIN knob
   vector, PROF=1, CACHE_ROUTE off (except (d)'s remap table). Knobs VARIED:
   EXPERT_BUDGET (off in (a); cap 4 in (b)/(c)/(d)) and the exclusion/remap
   table ((c)/(d) only).
4. NOTE vs the sibling: `glm-s4drop-0` pinned
   `a78a06fc5acc4b0dc0f9ef03987c66b0559d1250`; this cohort deliberately pins a
   NEWER commit (it needs #232/#294/#301). The two cohorts' baselines are
   therefore different by design and their numbers are never merged.

| input | pin | status |
|---|---|---|
| colibri commit (contains #232/#294/#301) | 40-hex by ops amendment | PINNED-AT-INPUTS |
| GLM-5.2 int4(+int8-MTP) weights content hash | recorded at bring-up before any scored token | PINNED-AT-INPUTS |
| Exclusion/remap patch diff (S4SPEED table) | sha256 by ops amendment | PINNED-AT-INPUTS |
| 16-cell skiplist + swap_to (frozen stage-3 copy) | reuse corpus `glm-s4drop-stage3-inputs-v1` = `59bb0b70d0002df9281c6a84f607828bae1dbbc7dc2529fc845dc88b6f53ca2f` | MATERIALIZED |
| Quality suite (300 items) | reuse `glm-s4drop-quality-suite-v1` = `4723f7c40d4fa377a8dbc80213476afa4cb50a986b4898340cf5b5ff81dad11e` (disjoint from the 244 stage-3 items + 480 wave-A probes, mechanically enforced per ASM-2391) | MATERIALIZED |
| Accuracy set (120 exact-answer items, 9 stage-3 strata-domains incl. format/copy/arithmetic — the domains the skiplist cells LED; adversarial for us by construction) | `glm-s4speed-acc-v1`, sha256 at freeze; disjointness vs stage-3 items, wave-A probes, and the quality suite mechanically checked | TO MATERIALIZE at freeze |
| Decode corpus (24 prompts × 256 new tokens; domain mix weighted toward the skiplist strata — favourable-workload test, any win is scoped to it) | `glm-s4speed-decode-v1`, sha256 at freeze; disjoint same way | TO MATERIALIZE at freeze |
| Pilot decode set (8 prompts × 256 new tokens, same generator recipe/domain mix as the decode corpus; consumed UNSCORED by the §5 paired variance pilot only) | `glm-s4speed-pilot-v1`, sha256 at freeze; disjoint from the 24 scored decode prompts and every other suite, mechanically checked | TO MATERIALIZE at freeze |
| Analysis script | `analysis/glm_s4speed_stdin.py`, sha256 in record pins; green `--selftest` + $0 `--mock` REQUIRED before freeze | TO BUILD at freeze |
| Runner script + staged-bytes manifest | sha256s by ops amendment before spend | PINNED-AT-INPUTS |

Suite reuse (OQ-4 RESOLVED by review ruling, r2): evaluation-only reuse of
`glm-s4drop-quality-suite-v1` is APPROVED **conditional on ordering** — this
cohort's record `glm-s4speed-0` is FROZEN (corpora hashed, analysis script and
all thresholds pinned) BEFORE the `glm-s4drop-0` readout exists, so no sibling
result can change this cohort's analysis or thresholds (§7 sequencing). Both
uses are evaluation-only (no selection or tuning on the suite by us).

### §4.1 Execution environment — EXACT pin (CPU streaming inference, NOT GPU)

The inherited Stage-3 measured basis is **CPU-only colibri-int4 streaming
inference on AVX-512**, and this cohort runs the SAME class of environment.
**No number in this design, and no Stage-3 number it builds on, is a GPU
result**; all tok/s figures here are CPU streaming-inference figures and say
nothing about GPU serving (§10 already excludes GPU platforms).

- **Engine / build:** colibri C engine, `glm_moe_dsa` target, experts @ 4-bit
  + dense @ 8-bit (colibri-int4), integer-dot kernel `idot: avx512-vnni`
  [MEASURED: `poc/glm52-probe/stage3/results/full_run.log:685` engine banner];
  built `make glm ARCH=native` [MEASURED: full_run.log:53]. Because
  ARCH=native floats with the host, bring-up gate G1 REQUIRES the campaign
  container's banner to report `idot: avx512-vnni` (AVX-512 VNNI present and
  selected) — a different ISA silently changes the measured basis → fail
  closed.
- **ISA / host class:** x86-64 with AVX-512 VNNI; Modal OCI-class container,
  4 cores / 64 GiB / 900 GiB ephemeral [MEASURED basis:
  `poc/glm52-probe/stage3/stage3_summary.md:68` (GO-FULL-GLM52 config)].
- **Offload / streaming mode:** weights staged to container-local ephemeral
  storage (383.8 GB [MEASURED: stage3_summary.md cost section]); resident
  cache RAM_GB=55; non-resident experts streamed on miss (this IS the regime
  EXPERT_BUDGET exists for).
- **Threads / env knobs:** all 4 container cores; `COLI_NO_OMP_TUNE=1`
  (stage-3 driver discipline [MEASURED:
  `poc/glm52-probe/stage3/stage3_driver.py:33`]); the exact thread count and
  full engine env-var vector are recorded by the pin ops amendment and echoed
  into the run log, G1-verified.
- **Upstream commit:** the cohort's 40-hex colibri commit pin is BLANK in
  this document BY DESIGN — it is filled by the ops amendment at bring-up,
  BEFORE any spend (§4 item 1; it must contain #232/#294/#301). The Stage-3
  measured basis ran the OLDER pin `a78a06fc5acc4b0dc0f9ef03987c66b0559d1250`
  [MEASURED: full_run.log:22–40] with `MTP ACTIVE (draft=0)`
  [MEASURED: full_run.log:685] — i.e. the inherited timing basis is
  PREFILL-side, MTP-off, at a different commit; that is exactly why the
  decode tok/s rate here is UNKNOWN until the pilot and never assumed.
- **DRAFT/MTP as EXACT pins:** DRAFT=1 in ALL arms of this cohort (never
  "shipped default"); every further MTP/SPEC_PIN knob the pinned commit
  exposes is enumerated with its exact value in the same ops amendment and
  re-verified fail-closed at G1. Any knob not named in §2/§4 is frozen at the
  value echoed in the bring-up config dump recorded by that amendment.
- NOTE (r2 provenance): companion row ASM-2479 still carries the r1 phrase
  "DRAFT/MTP shipped default"; this §4.1 exact-pin wording supersedes that
  phrase, the row's load-bearing content (one pinned commit, fixed-vs-varied
  knob table, no double-counting) is unchanged, and the row is otherwise
  untouched. (coordinator: ASM-2479 registered 2026-07-16; row parenthetical synced to the r2 wording)

## §5 Primary endpoint, estimator, power [STIPULATED: ASM-2482]

**EXACTLY ONE primary.** Δ_spd = pooled mean over the 24 decode prompts of the
per-prompt paired relative delta (tok/s(c) − tok/s(b)) / tok/s(b), pooling
each prompt's two passes by mean first (prompt = the cluster unit; passes are
not independent). Interval: seeded SHA-256-DRBG percentile bootstrap over the
24 prompts, B = 10,000, seed 20260812. Decision quantity: the one-sided 95%
LOWER bound (5th percentile).

- **Protocol.** Fixed T = 256 new tokens per prompt (no EOS stop; tok/s =
  256/wall of the generation loop). Per (arm × pass) block: engine restart,
  cache reset to the pinned state, 1 unscored warm-up prompt, then the 24
  prompts in pinned order. Block order across arms randomized per pass, seed
  20260811. Two passes per arm.
- **Noise model + power (planning; resolution = the bring-up pilot, never the
  verdict).** Stipulated per-prompt paired-delta sd = 2–3% (planning prior;
  no local measurement exists yet) → se(Δ_spd) ≈ sd/√24 ≈ 0.41–0.61% →
  one-sided MDE_80 ≈ 2.487·se ≈ 1.0–1.5%, comfortably under the +3% SESOI.
  These planning figures are STIPULATED-not-MEASURED and are superseded by
  the pilot's sd_up (below).
- **Primary-variance pilot (bring-up, gate G7) — PAIRED (b,c), unscored (r2;
  closes the primary-variance CONCERN).** The pilot estimates the variance of
  the primary's OWN unit — the per-prompt paired relative delta
  d_i = (tok/s(c)_i − tok/s(b)_i) / tok/s(b)_i — DIRECTLY. (The r1 design's
  six-repeat same-arm pilot measured same-arm timing repeatability only; that
  quantity omits prompt×arm effect heterogeneity and CANNOT stand in for the
  paired-effect variance — it is withdrawn.) Design: the dedicated 8-prompt
  set `glm-s4speed-pilot-v1` (§4 — disjoint from the 24 scored decode
  prompts) is run in **2 paired pilot blocks**; each block = one full
  §5-protocol pass per arm for (b) and (c) only (engine restart, cache reset
  to the pinned state, 1 unscored warm-up, the 8 prompts in pinned order,
  T = 256; arm order alternates across blocks, seed 20260815). Replicate
  blocks are pooled per prompt FIRST — the same clustering as the campaign
  estimator — giving n_pilot = 8 per-prompt paired deltas → sd_hat with
  df = 7.
- **Conservative MDE re-derivation (the corrected variance basis).**
  sd_up = sd_hat · sqrt(df / χ²_{0.20, df=7}) = sd_hat · sqrt(7/3.822) ≈
  1.353·sd_hat — the one-sided 80% upper confidence bound on the sd, so the
  small-pilot uncertainty is inflated explicitly, not assumed away. Implied
  MDE_80 = (z_{0.95}+z_{0.80}) · sd_up/√n = 2.487 · sd_up/√24. **G7 passes
  iff MDE_80 ≤ 3% (the SESOI).** On failure: ONE registered resize 24→48
  scored prompts (a (b)/(c) decode-corpus extension; cost re-projected
  against the §10 cap BEFORE any scored pass) → recompute with √48; if still
  > 3% → STOP-V (§8/§9: registered pre-spend stop, not a verdict — no scored
  token has been spent). No post-hoc resize exists.
- **No peeking.** Pilot prompts are never scored; the pilot deltas feed ONLY
  sd_hat. The pilot MEAN is quarantined — it enters no verdict quantity and
  no gate, and is disclosed in the readout as bring-up telemetry only. (The
  pilot set is disjoint from the scored corpus, so it could not tune the
  primary even if read.)
- NOTE (r2 provenance): companion row ASM-2482's claim parenthetical still
  reads "6 repeated identical baseline blocks" (the r1 pilot). This §5 paired
  design supersedes ONLY that parenthetical; the row's load-bearing content
  (one primary, SESOI +3%, bootstrap spec, G7 MDE ≤ 3%, single lawful resize,
  K-P/K-DIR split) is unchanged and the row is otherwise untouched.
  (coordinator: ASM-2482 registered 2026-07-16; row parenthetical synced to the r2 wording)
- **Quality endpoints** (gates, §1 H-Q): Q1 uses the same estimator family as
  the sibling design — paired per-item ΔNLL, winsorized ±2.0 nats/tok (raw
  mean + winsorized count disclosed), family-cluster bootstrap over the
  suite's pinned 30 families, B = 10,000, seed 20260813, one-sided 95% UPPER
  bound < +0.05. Q2/Q3 are point-estimate screens with their bands stated in
  §1 and their low power DISCLOSED (Q2 at n=120 has se ≈ 2–4pp; it screens
  for gross breakage, it does not certify equivalence — no equivalence claim
  is licensed anywhere in this design).
- **H-M estimator:** per-prompt paired acceptance-rate difference (c)−(b),
  same bootstrap machinery, seed 20260814; one-sided 95% lower bound ≥ −5pp
  (inclusive, identical to the §1 H-M band — the equality case passes).

## §6 Matched quality is a GATE (composition rule)

VALIDATE requires ALL of: H-S lower bound > 0 AND point ≥ +3%; Q1; Q2; Q3;
H-M. Any quality gate failing while tok/s improves is a KILL (speed bought
with quality — §9 K-Q). H-M failing alone (acceptance tank) with H-S and H-Q
passing is NOT a validate and NOT a kill: it resolves
INCONCLUSIVE-scope-limited (the speedup rides on degraded speculative
behaviour; workload transfer unestablished) [STIPULATED: ASM-2483]. H-M
failing AND (H-S lb ≤ 0 OR any H-Q gate failing) composes to the KILL the
task pre-registers: a skiplist that speeds raw forwards but tanks MTP
acceptance with net decode slower or quality worse is dead.

## §7 Simultaneous-drop: a pre-registered question, never an assumption [MEASURED premise: stage-3 interp §2(d)]

Stage-3 ablated cells one at a time; this cohort applies all 16 at once, so
"does the simultaneous 16-cell drop hold quality" gets its own pre-registered
pass/kill here (H-SD): in the deployment regime (cap 4, MTP on), (c) must hold
Q1+Q2+Q3+H-M. FAIL → K-SD fires (§9) regardless of tok/s.

Division of labour with the sibling, so neither leans on the other:
`glm-s4drop-0`'s H-J tests the pure joint-16 drop (budget off, DRAFT=0,
teacher-forced) — the clean isolation; THIS H-SD tests the joint drop under
budget+MTP — the deployment regime. Sequencing [STIPULATED: ASM-2484; OQ-6
RESOLVED by review ruling, r2]: **FREEZE BEFORE, EXECUTE AFTER** the
`glm-s4drop-0` readout — the record `glm-s4speed-0` (corpora, analysis
script, all thresholds) is frozen before the sibling readout exists, so no
sibling result can change this cohort's analysis or thresholds (also the
OQ-4 reuse condition, §4); execution is scheduled after the sibling readout.
If the sibling's H-J KILLS (joint-16 unsafe even without budget), this cohort
proceeds at most through bring-up + construction and **campaign spend STOPS —
it may resume only under a separately reviewed amendment**, never by runner
or coordinator improvisation, rather than spending the campaign into a
predicted quality kill. Not a hard dependency; H-SD stands on its own either
way.

## §8 Instrument gates — each gate carries exactly ONE deterministic non-verdict state (r2)

Two non-verdict states exist, and every gate names its one state in its row:
**STOP-V** (registered PRE-SCORED-SPEND stop — bring-up gates G4 and G7 only;
consumes no VOID budget because no scored token has been spent) and
**INSTRUMENT-INVALID** (all other gates). A fired state is never
reinterpreted, never escalated to a different state, and never a verdict; §9
uses the same two names and no others.

- **G1 pins_valid [INSTRUMENT-INVALID]:** commit / image / weights / patch /
  table hashes re-verified fail-closed at engine start; all meta.pins are
  real 64-hex digests (placeholders rejected); the engine banner reports
  `idot: avx512-vnni` and the §4.1 exact knob/env vector (incl. DRAFT=1)
  matches the ops amendment; the S4SPEED patch passes the §2 patch-scope
  allowlist (no hunk outside candidate-set construction).
- **G2 prof_fields_valid [INSTRUMENT-INVALID]:** every required
  PROF/acceptance field present on the pinned commit with plausible nonzero
  values on a 2-prompt spot run; acceptance counters (accepted/proposed)
  available at PER-PROMPT granularity — aggregate-only exposure is a G2
  FAILURE with no fallback (OQ-5 ruling); trace fields sufficient to
  recompute the budget fill offline (§2 differential-proof leg 3); DRAFT-on
  vs DRAFT-off greedy-output identity on one item (§3).
- **G3 patch_inert [INSTRUMENT-INVALID]:** empty exclusion table →
  byte-identical outputs to the unpatched build on a seeded spot set
  (stage-3 inertness discipline; §2 differential-proof leg 2).
- **G4 budget_binds [STOP-V]:** PROF must show nonzero budget drops in arm
  (b) on the pilot prompts AND the §2 vacuity count (skiplist-cell
  keep-events under (b)) must be nonzero. EITHER failing — budget never
  binds, or zero keep-events ((b) ≡ (c)) — fires STOP-V: a registered
  pre-spend construction stop, telemetry salvaged, coordinator decides; never
  a verdict, never INSTRUMENT-INVALID.
- **G5 timing_sane [INSTRUMENT-INVALID] (r3, deterministic — no
  bring-up-recorded floor exists):** three numeric bounds, all frozen here in
  advance: (i) PROF per-forward p50 drift between an arm's two passes < 15%;
  (ii) decode-phase share of the timed region ≥ 80% in EVERY (arm × pass)
  block [STIPULATED: ASM-2479, instrument-of-record scope — below 80% the
  timed wall is dominated by non-decode overheads and the tok/s contrast no
  longer measures the §2 estimand]; (iii) PROF-on wall-clock overhead ≤ 5%
  versus one PROF-off spot pair (same prompt, same arm-(b) config; overhead
  disclosed either way) [STIPULATED: ASM-2479 — an instrument perturbing its
  own measurand by more than 5% is not a sane timer, even though the
  identical-across-arms observer effect cancels in paired deltas]. PASS iff
  all three bounds hold; ANY violation fails the gate → INSTRUMENT-INVALID.
  Both pass and fail directions are fixed by these stated thresholds; no
  bring-up judgment enters the gate.
- **G6 matched_cap_mechanical [INSTRUMENT-INVALID] (r2, EXACT paired
  parity):** for EVERY (prompt × layer) site, from PROF expert-I/O
  accounting: (i) keep-set size ≤ N in both (b) and (c) — exact; (ii)
  wherever (b)'s effective distinct-expert count = N (budget binds), (c)'s
  count = N exactly; (iii) any count discrepancy is lawful only where the
  budget is slack AND equals exactly the number of routed-but-excluded
  skiplist cells at that site (differences fully attributable to candidate
  eligibility, §2 differential-proof leg 3); slack-site discrepancies are
  enumerated and disclosed. Any other discrepancy fails the gate. The r1
  within-1% per-layer-mean check is retained as a cross-check only.
- **G7 variance_pilot [STOP-V]:** §5 paired pilot — implied MDE_80 (from
  sd_up) ≤ 3% at the registered or once-resized n; failure after the single
  lawful resize fires STOP-V (pre-scored-spend, telemetry salvaged).
- **G8 completeness [INSTRUMENT-INVALID]:** zero missing (c)/(b) primary
  pairs (decode AND quality); per-prompt accepted/proposed acceptance counts
  present for every (b)/(c) decode prompt (a missing count is a G8 failure,
  mirroring the OQ-5 ruling at analysis time); secondary arms ≤ 2 incomplete
  items each, disclosed.
- **G9 liveness [INSTRUMENT-INVALID]:** per-arm NLL stdev ≥ 1e-3 nats/tok and
  ≥ 50 distinct values (sibling review lesson B1/3b — an inert readout must
  never fire a kill); per-prompt tok/s values distinct across prompts.
- **G10 cost_ledger [INSTRUMENT-INVALID]:** live phase-boundary checkpoint
  ledger (staging, bring-up, pilot, quality-<arm>, acc-<arm>, decode-pass1,
  decode-pass2 — one label per arm actually run), distinct labels in
  registered order, monotone, every checkpoint and the total within §10
  caps; a malformed or over-cap ledger at analysis time fails the gate. (The
  runner's cap-hit ABORT — salvage-and-stop the moment accrued spend reaches
  a §10 cap — is the run-time protocol of §10, not a gate state; a cap-hit
  run reaches analysis with missing pairs and resolves through G8.)
- Everything computable from rows is recomputed in-script; residual runner
  booleans are scoped to the sidecar + the cross-vendor audit. VOID budget 1:
  an INSTRUMENT-INVALID readout obligates a coordinator rerun decision; a
  second VOID escalates to the maintainer. VOID is never a quiet exit from an
  impending kill. STOP-V consumes no VOID budget (nothing scored was spent).

## §9 Kill criteria (verbatim once frozen) and verdict structure

With all gates valid:

- **K-P (post-gate kill, the task's stipulated kill):** the primary one-sided
  95% lower bound of Δ_spd ≤ 0, OR any H-Q band is violated. Fires → #208
  stays blocked; NO public post; this cohort is one-shot at this cap/skiplist
  — no re-run without materially new upstream evidence (no
  retry-until-significant).
- **K-Q (quality-bought-speed kill):** H-S passes but any of Q1/Q2/Q3 fails —
  a speedup at degraded quality is a KILL, not a win.
- **K-SD (simultaneity kill):** H-SD fails (the joint 16-cell application
  breaks the quality/acceptance bands in the deployment regime) — fires
  regardless of tok/s.
- **K-M (MTP composition kill):** H-M fails AND (H-S lb ≤ 0 OR any H-Q gate
  fails) — the skiplist speeds nothing net and damages speculative decoding.
- **K-DIR (direction kill, affirmed null):** the one-sided 95% UPPER bound of
  Δ_spd < +3% — the data AFFIRM no postable matched-cap speed effect exists;
  the matched-cap raw-speed channel for the causal skiplist is dead (this is
  the no-spurious-kill discipline from the sibling's review finding D1: K-DIR
  affirms absence; K-P merely withholds the post).
- **VALIDATE:** §6 composition — unlocks ONLY the narrow Show-and-Tell framed
  complementary to colibri #175 per the novelty doc; #207 stays PAUSED;
  deterministic replacement stays unevidenced.
- **INCONCLUSIVE:** everything else — including lb ≤ 0 with upper bound ≥ +3%
  (underpowered region, reported at its resolution; still K-P for posting
  purposes) and the H-M-only failure of §6.
- **STOP-V (pre-scored-spend, registered — the ONLY non-verdict state of
  gates G4 and G7, §8):** G4 firing (the §2 vacuity count is zero, or the
  budget never binds) or G7 firing (MDE_80 > 3% after the single lawful
  resize) — construction-phase STOP before any scored campaign spend; the
  telemetry is salvaged; not a verdict, not INSTRUMENT-INVALID, consumes no
  VOID budget. Every other gate (G1–G3, G5, G6, G8–G10) has
  INSTRUMENT-INVALID as its one state (§8).

**Envelope (binding text lives in the frozen record).** Scope of ANY validate:
this pinned colibri commit, this box class, cap 4, this favourable-weighted
workload, this 16-cell skiplist. No population claim over cells, no claim
about other caps/hosts/workloads, no deterministic-replacement claim, no
claim that causal evidence beats frequency ranking in general (the sibling's
estimand lesson, ASM-2397, applies here unchanged).

## §10 Cost envelope, salvage-and-stop, sequencing [STIPULATED: ASM-2484]

Platform: Modal (OCI-class container; the proven GO-FULL-GLM52 config, 4
cores / 64 GiB / 900 GiB ephemeral, RAM_GB=55) — **CPU AVX-512 streaming
inference per the §4.1 exact environment pin; no GPU of any kind (this is not
a GPU experiment); Modal/OCI/GCP only.** Cost basis [MEASURED: stage-3 run
log via the interp header — ≈$6.1 total; ~$1.15/h; ~11.0 s/prefill; decode
tok/s UNKNOWN until the pilot, planned at 1–4 tok/s]:

**MANDATORY arms (a)/(b)/(c) — the cohort's irreducible core:**

- staging 383.8 GB ≈ 23 min ≈ $0.5 [MEASURED basis: stage3_summary.md]
- bring-up + gates + PAIRED variance pilot (§5: 2 blocks × 2 arms × 8 × 256 =
  8,192 decode tokens → 0.6–2.3 h) ≈ 1.6–3.3 h ≈ $2–4
- quality: 3 arms × 300 prefills × ~11 s ≈ 2.8 h ≈ $3.2
- accuracy: 3 arms × 120 items × (prefill + ≤32-tok answer) ≈ 1.5 h ≈ $1.9
- throughput: 3 arms × 2 passes × 24 × 256 tok = 36,864 tok at 1–4 tok/s
  ≈ 2.6–10.2 h ≈ $3–12

Mandatory subtotal: **point ≈ $13, band ≈ $10.5–21.5.**

**OPTIONAL arm (d) increment** (first ladder cut): quality ≈ $1.1 + accuracy
≈ $0.6 + decode 12,288 tok ≈ $1–4 → **≈ $2.7–5.7**.

**Registered resize branch** (§5 G7, 24→48 prompts, a (b)/(c) decode
extension only — (a)/(d) throughput stays at 24): +24,576 tok ≈ 1.7–6.8 h →
**≈ $2–8**, re-projected against the cap BEFORE any scored pass.

**Worst-case coherence at the $30 cap:** the full four-arm + resize case
clears the cap for decode rates ≥ ~1.3 tok/s (≈ $29: staging 0.5 + bring-up 4
+ quality 4.3 + accuracy 2.5 + decode 73,728 tok / 1.3 tok/s ≈ 15.8 h ≈
$18.1 — the 24 h wall binds nearly simultaneously there). Below ~1.3 tok/s
the naive sum would exceed $30, but that branch is unreachable: G7's
pre-scored-pass cost re-projection and ladder rung 1 (drop (d), −$2.7–5.7)
fire first, then rung 3 shortens decode — so every registered branch either
fits under the cap or is cut by a registered rung before spend reaches it.
**The $30 cap is therefore defensible. Planning point ≈ $14 [ESTIMATE — never
a decision premise]. Hard bounds: usd_cap = $30 AND wall = 24 h, whichever
binds first (unchanged from r1/ASM-2484).** NOTE (r2 provenance): companion
row ASM-2484 records the r1 band "$10–25" (the four-arm no-resize case);
this r2 breakdown separates mandatory/optional/resize and identifies the
~$29 admissible worst case; the row's load-bearing content (caps,
salvage-and-stop, ladder, sequencing) is unchanged. (coordinator: ASM-2484 registered 2026-07-16; row parenthetical synced to the r2 wording)

Live ledger per G10; on any instrument-gate failure or cap hit the runner
SALVAGES (flush partial rows + PROF dumps + ledger to the output volume) and
STOPS — never retries, never improvises. Degradation ladder (registered,
analysis-compatible): (1) drop arm (d) entirely; (2) drop arm (a)
quality+accuracy prefills (keep (a) throughput); (3) decode 256→160
tokens/prompt (both passes, all arms, one common budget); (4) STOP. The
(b)/(c) pairs — decode, quality, accuracy — are never cut.

Sequencing: GPT-5.6 review gate → coordinator commits doc + registers
ASM-2479..2484 → experiment-designer freezes record `glm-s4speed-0` (kot-reg/1;
corpora materialized, analysis script + selftests green, pre-freeze skeptic
attack) — the freeze lands BEFORE the `glm-s4drop-0` readout (§7, OQ-6
ruling) → ops amendments (commit pin, patch sha, runner sha) → runner
(experiment-runner role) executes AFTER the sibling readout: bring-up gates →
pilot → STOP-V check → campaign → verdict-gen → cross-vendor audit. This
designer never runs, grades, or audits.

## §11 Self-check gate (governance)

Closed four-tag schema for this document: MEASURED / STIPULATED / ESTIMATE /
LIT-BACKED; no other tag token appears. Every load-bearing claim above carries
exactly one tag; every MEASURED cites its artifact (stage3_analysis.json,
stage3_summary.md, the stage-3 interp, or an upstream colibri PR named as
such with local non-verification disclosed); every ESTIMATE (§0 prior, §10
cost band) is explicitly never a decision premise — decisions route through
gates, stops, and caps; every STIPULATED choice is labelled
STIPULATED-not-MEASURED and carries an ASM id in ASM-2479..2484 (companion
file `asm-s4speed-2479-2484.json`, range re-verified free at r2 against
register tail ASM-2478 and the adjacent f1k block ASM-2485..2491) or cites an
already-registered ASM (2342, 2383, 2391, 2397). The six ASM ids are LOCKED;
neither r2 nor r3 creates, renumbers, or alters ANY id (r3 amends ONE
companion row's TEXT in place — ASM-2480, brought to the §8 G6 exact-parity
wording, a lawful pre-registration amend-in-place with provenance in the
companion `_about`; the id is unchanged). The three r2 wording supersessions
(ASM-2479 §4.1, ASM-2482 §5, ASM-2484 §10) are flagged with explicit inline
coordinator-action markers; exactly THREE such actionable bracketed markers
exist in this document (§4.1, §5, §10), this sentence is a description of
them and is NOT itself a marker, and they touch no row. Exactly ONE primary endpoint
exists (§5); both directions of every gate and kill are worded in advance
(§8, §9), including the no-spurious-kill split (K-P withholds, K-DIR
affirms); every gate carries exactly ONE deterministic non-verdict state
(§8: G4/G7 → STOP-V, all others → INSTRUMENT-INVALID; §9 uses the same map);
no failed superiority reading is worded as equivalence anywhere (§5
explicitly declines equivalence claims for Q2/Q3). The primary-variance
pilot is PAIRED (b,c) and estimates the primary's own per-prompt paired-delta
variance with an explicit df-7 conservative inflation (§5). The execution
environment is pinned exactly — CPU AVX-512 colibri-int4 streaming
inference, never GPU (§4.1). The simultaneous-drop gap is a pre-registered
question with its own kill (§7), not an assumption. The moving-baseline
constraint is a registered load-bearing ASM (ASM-2479) with the
fixed-vs-varied knob table in §4. MTP acceptance is a first-class DV with its kill
composition (§3, §6, §9). The instrument is PR #232 PROF=1 with a field→DV
map and a fail-closed bring-up presence gate — no hand-rolled duplication.
No feasibility conclusion is stated. No frozen record, verdict, encoder pin,
or registered assumption is touched; `registry/assumptions.jsonl` is not
written; no git action, no model run, no spend occurs in this pass. Author
attribution is the pseudonym designer-1 only; neither this file nor its
companion contains any personal handle, account, or email string (verified
mechanically at self-check).

## §12 Open questions — ALL RESOLVED by the design-integrity review rulings (r2)

Kept verbatim for the record, each with its ruling folded into the body:

- **OQ-1 (patch seam) — RESOLVED:** author a **separate minimal S4SPEED patch
  at the EXPERT_BUDGET keep-set seam**; the frozen sibling's committed
  S4_TABLE surface is NOT modified; the §2 differential proof (three legs,
  fail-closed) is required. Folded into §2 (implementation seam) and G1.
- **OQ-2 (estimand reading) — RESOLVED, CONFIRMED:** the estimand is
  **identical N inside EXPERT_BUDGET with forced exclusion**; the pure-mask
  alternative is overruled as speed-vacuous. Folded into §2 (estimand bullet)
  with the differential proof that only candidate eligibility changes.
- **OQ-3 (cap sensitivity) — RESOLVED:** the N=8 half-cohort stays **OUT**.
  N=4 is the only registered cap; any N=8 work is a separately designed
  follow-up, never appended to this record.
- **OQ-4 (suite reuse) — RESOLVED, APPROVED CONDITIONALLY:** evaluation-only
  reuse of `glm-s4drop-quality-suite-v1` is approved PROVIDED this cohort is
  frozen before the sibling readout and no sibling result can change its
  analysis or thresholds. Folded into §4 and §7.
- **OQ-5 (acceptance counter) — RESOLVED:** missing per-prompt
  accepted/proposed counts are a **G2 FAILURE**; the interval-free aggregate
  fallback is NOT acceptable and no longer exists in this design. Folded into
  §3 (DV table), G2, and G8.
- **OQ-6 (sequencing) — RESOLVED:** **freeze before, execute after** the
  `glm-s4drop-0` readout; a sibling H-J kill stops campaign spend absent a
  separately reviewed amendment. Folded into §7 and §10 (sequencing).

## §13 r2 closure map (design-integrity review NEEDS-WORK items)

| # | review item | closure |
|---|---|---|
| 1 | primary-variance pilot measured same-arm repeat noise | §5: r1 pilot WITHDRAWN; paired (b,c) pilot over the dedicated 8-prompt `glm-s4speed-pilot-v1` set (2 blocks, pooled per prompt, df=7) estimates the paired-effect sd directly; MDE re-derived from sd_up = 1.353·sd_hat; G7 [STOP-V]; no-peeking clause; coordinator-action marker (§5) for ASM-2482's stale parenthetical |
| 2 | arm-(c) parity asserted, only per-layer means gated | §2: estimand confirmed (identical N + forced exclusion, OQ-2); semantic-parity obligation (shared drop/renorm code path); three-leg differential proof (patch-scope allowlist → G1, empty-table inertness → G3, keep-set attribution → G2/G6); §8 G6 rewritten to EXACT paired prompt×layer effective-count/cap parity, means demoted to cross-check |
| 3 | execution environment under-specified | §4.1: CPU colibri-int4 streaming inference, NOT GPU; `glm_moe_dsa`, experts@4-bit dense@8-bit, `idot: avx512-vnni` (full_run.log:685), ARCH=native + banner ISA check in G1, OCI 4-core/64GiB/900GiB + RAM_GB=55 streaming offload, 4 threads + COLI_NO_OMP_TUNE=1 (stage3_driver.py:33), 40-hex commit pin filled by ops amendment at bring-up (stated as such), DRAFT=1 + enumerated MTP knob vector as EXACT pins; §10 platform line updated |
| 4 | §8 blanket INSTRUMENT-INVALID vs G4→STOP-V | §8 header + per-gate state tags: exactly ONE deterministic non-verdict state per gate (G4, G7 → STOP-V; all others → INSTRUMENT-INVALID); §9 STOP-V bullet uses the identical map; cap-hit abort routed through §10 protocol + G8, not a third state |
| 5 | ASM range-text artifacts (2479..2478 / 2473-2478 / ASM-2473) | header, §10 sequencing, §11 (×2) corrected to ASM-2479..2484, companion `asm-s4speed-2479-2484.json`, moving-baseline id ASM-2479; free-space basis re-verified at r2 (register tail ASM-2478; f1k block 2485..2491 adjacent, no overlap); companion `_about` amended to match; zero ASM ids created/renumbered/altered |
| 6 | OQ rulings + cost band | §12 all six OQs resolved and folded (§2, §3, §4, §7, §8, §10); §10 band split MANDATORY (a)/(b)/(c) ≈ $10.5–21.5 vs optional (d) ≈ $2.7–5.7 vs resize ≈ $2–8, four-arm+resize admissible worst case ≈ $29 < $30 cap with the unreachable sub-1.3-tok/s branch cut by registered rungs |

## §13.1 r3 closure map (round-2 review internal-consistency residuals)

| # | residual | closure |
|---|---|---|
| 1 | §2 blanket "same NUMBER per layer" vs §2/§8 lawful slack-site discrepancies | §2 mechanism consequence rewritten to the identical exact-parity rule as the §2 paired-parity bullet and §8 G6: same target keep-set size (cap N); (c) = N EXACTLY wherever (b) binds at N; discrepancies lawful ONLY where slack AND exactly attributable to routed-but-excluded skiplist cells — the two sites now state the same rule |
| 2 | companion ASM-2480 row still described the within-1% mean verification | ASM-2480 claim + backing_ref amended IN PLACE (lawful pre-registration amend, id unchanged) to the §8 G6 exact paired prompt×layer parity, within-1% mean demoted to cross-check; companion `_about` carries the r3 provenance |
| 3 | G5 decode-share floor / PROF overhead left to bring-up (non-deterministic gate) | §8 G5 frozen numeric bounds, both directions: p50 drift < 15%; decode-phase share ≥ 80% every (arm × pass); PROF-on overhead ≤ 5% vs one PROF-off spot pair [STIPULATED: ASM-2479, one-line justifications inline]; pass iff all three hold, any violation → INSTRUMENT-INVALID; no bring-up-recorded floor remains |
| 4 | H-M bound "≥ −5pp" (§1) vs "> −5pp" (§5) | INCLUSIVE ≥ −5pp chosen; §1 and §5 both state it with the equality case explicitly PASSING; companion ASM-2483 already inclusive (>=), unchanged |
| 5 | §11 self-referential bracketed marker mistakable for a fourth actionable marker | §11 sentence reworded to plain prose (no bracketed marker form); exactly THREE actionable coordinator markers exist (§4.1 ASM-2479, §5 ASM-2482, §10 ASM-2484); §13 row-1 shorthand likewise de-bracketed; companion `_about` states the same count |
