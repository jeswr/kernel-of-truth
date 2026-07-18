# F1K-BRINGUP-GATE-FIX **REV-F** — closing GAP-1..4 + the v3-review + the gate-fix review REJECT + the rereview STILL-OPEN findings + the round-3 six-defect remainder + the round-4 four-blocker residual + the round-5 three textual corrections: the real-corpus, token-aware, mechanically-frozen bring-up affordability gate (exact diffs; NOT applied)

**Author:** designer-20 (design memo only — NO spend, NO VM, NO git action, NO repo edit except
this file)
**Date:** 2026-07-18 (REV-B/C/D same day)
**Status:** REV-F CONSOLIDATED (seven designer-20 passes): the BASE pass (GAP-1..4; artifacts D1-D4, $0-bench-verified) + the **REV-A addendum (§A)** closing the v3-plan cross-model review (`poc/gpt56-review/f1k-construction-v3-review-VERDICT.md`, REJECT; delta artifacts D5-D8) + the **REV-B addendum (§B)** closing the gate-fix review of THIS memo (`poc/gpt56-review/f1k-gate-fix-review-VERDICT.md`, overall REJECT; findings 6/9 AGREE — the D5/D6 license-predicate core + cost table are settled and kept byte-stable; delta artifacts **D9-D13**) + the **REV-C addendum (§C)** closing the rereview (`poc/gpt56-review/f1k-gate-fix-rereview-VERDICT.md`, REJECT; delta artifacts **D14-D18**) + the **REV-D addendum (§D below)** closing the round-3 six-defect remainder (`poc/gpt56-review/f1k-gate-fix-round3-VERDICT.md`, REJECT with a narrow fully-prescribed remainder; delta artifacts **D19-D21**, $0-bench-verified against the LANDED post-seq-3 tree) + the **REV-E addendum (§E below)** closing the round-4 residual (`poc/gpt56-review/f1k-gate-fix-round4-VERDICT.md`, REJECT with exactly four blockers — abbreviation-aware refusal, durable/consumed stop authority, cost-input finiteness, stale supersession text; delta artifacts **D22-D24**, $0-bench-verified on `2574c82b`) + the **REV-F addendum (§F below)** closing the round-5 verdict (`poc/gpt56-review/f1k-gate-fix-round5-VERDICT.md`, **APPROVE-WITH-FIXES** — ALL executable machinery CLOSED; three prescribed TEXTUAL corrections: the live gate-docstring schema residue → delta artifact **D25** (one docstring line; new gate final `e421861e…`), the §E.3/ASM-2518 `realize --mock-f`→`fcount --mock-f` mis-attribution, and the hash/grep cascade; $0-bench-verified on `2574c82b`; the coordinator apply follows). §B carries the composite **supersession map** (review finding 8) and §C.5/§D.6/§E.4/§F.2 its REV-C/REV-D/REV-E/REV-F state — read them before acting on any §0-§A text. Awaiting coordinator apply (round-5 = the LAST review round).
**Chain:** `F1K-AFFORDABILITY-DECISION.md` v3 → `F1K-CONSTRUCTION-PLAN.md` v1/v2 →
`F1K-LAYER-REFREEZE.md` v3 (landed, seq-2) → `F1K-PIN-FILE-FIX.md` **v5** (seq-3, **LANDED at
`2574c82b`**: `validate_pinning`/`check_pin_engagement`/spend-start sentinel/ledger+addendum
binding in-tree; `analysis/f1k.py` re-pinned `126129b9`, `frozen_sha256` `35372275`) →
`F1K-CONSTRUCTION-PLAN.md` v3 → **this memo** (the §4.2 GAP-1..4 follow-up the plan names).

---

## 0. Scope, sequencing, and what this memo is

This memo designs — as **exact diffs the coordinator applies verbatim** — the code fix for the four
named gaps of `F1K-CONSTRUCTION-PLAN.md` v3 §4.2:

- **GAP-1 (BLOCKING):** the construction-license timing input is the synthetic 10×T96/10×T384
  functional-gate mix (`f1k_worker.sh:228-231, 318-337`), which the v2 review round showed
  self-STOPs under the plan's own pinned cost model (`poc/gpt56-review/f1k-construction-review-VERDICT.md`
  finding 4). → Replaced by a deterministic, seeded, pre-specified, stratified sample of the REAL
  frozen corpora (§2.3); the synthetic mix survives ONLY as a secondary diagnostic.
- **GAP-2 (BLOCKING):** no words→tokens `f` measurement exists anywhere in code, but §7 pivots on
  `f ≤ 1.60`. → `f` is measured on the FULL frozen corpora with the real bring-up tokenizer and the
  `f ≤ 1.60` branch is wired mechanically into the verdict (§2.5).
- **GAP-3:** the projection is per-average (`f1k_gcp.py project_ledger :211-260` consumes ONE
  blended s/prefill; VERDICT finding 3: a single average can approve an over-budget long-tail
  run). → The bring-up gate's projection becomes PER-ITEM token-aware: `Σ m_i·ŝ(T_i)` over every
  prefill of the frozen 19,964 envelope at its measured token count (§2.6). The driver-side
  addendum-(7) instance (pre-main, not pre-construction) is dispositioned in §5.3 (GAP-3b).
- **GAP-4:** doc echoes (`f1k_gcp.py:26-34` advertises push/stage/build/bringup that `ENTRY`
  `:434-437` does not implement; `:7` + `poc/gcp/README.md:12` say 3×375 GiB while
  `LOCAL_SSD_COUNT = 2` at `:106`; plus one stale `--layers 3,…,78` echo found this pass at
  `README.md:84`, corrected to the landed ASM-2504 3..77 geometry). → All fixed in the diffs.

**Sequencing (hard constraint — now DISCHARGED):** these diffs land in a **separate commit
AFTER** the PIN-fix seq-3 landing (`F1K-PIN-FILE-FIX.md`, authority now **v5**, §4/§7 — **LANDED
at `2574c82b`** [MEASURED this REV-B pass], so the moving-base risk is gone and §B re-verified
every artifact against the REAL landed bytes). The PIN-fix edits exactly
`f1k_gcp.py:5/:14/:49/:51/:57` (docstring echoes + `FROZEN_SHA256` + `PINS["analysis/f1k.py"]`),
`bringup_gcp.sh:43`, and `poc/gcp/README.md:5` (its §4 rows 4-7, verified there this pass). The
diffs below touch NONE of those lines, and every hunk's context excludes them: the `f1k_gcp.py`
diff is generated at **U1 context** so the hunk at line 7 references only lines 6/8 (not the
PIN-fix's line 5), and no other hunk sits within one line of :14/:49/:51/:57. **[MEASURED]** I
verified application twice on the bench: (a) against the current repo bytes, and (b) against a
simulated post-seq-3 tree with lines 5/14/49/51/57 + `README.md` hash echoes rewritten — all three
diffs `git apply --check` clean in BOTH states (§4.1).

Governance tags used throughout: **[MEASURED]** = verified in this checkout / on the bench this
pass; **[EXTRAPOLATED]** = deterministic arithmetic on measured anchors; **[STIPULATED]** = design
choice, frozen by this memo (registered via ASM-2514, §5.2). REV-A additions are frozen via ASM-2515 (§A6), registered in the SAME landing commit.

## 1. Pin status of the touched files — landing is plain infra [MEASURED]

Checked this pass, in this checkout:

| File | Sha-pinned anywhere? | Evidence |
|---|---|---|
| `poc/gcp/f1k_gcp.py` | **NO** | zero occurrences of `f1k_gcp` in `registry/experiments/f1k.json` (grep this pass) and in `registry/frozen-index.json`; the `PINS` dict `:55-68` carries no self-row |
| `poc/gcp/f1k_worker.sh` | **NO** | zero occurrences of `f1k_worker` in `f1k.json`/`frozen-index.json`; mentioned in `bringup_gcp.sh` comments only (`:18,:19,:45,:112,:167,:178`), never hashed; the only sha check in `bringup_gcp.sh` is the KaE patch (`:83-84`) |
| `poc/gcp/README.md` | **NO** (doc) | not referenced by any pin structure |
| `poc/gcp/f1k_bringup_gate.py` | new file | n/a |
| `pins.harness_manifest` | pins by sha ONLY `build_carriers.py` (`a92be3e4…`) and `kae-add-path.patch` (`11f8b458…`); says "f1k_driver.py, not sha-pinned here" **twice** | read this pass; matches `F1K-PIN-FILE-FIX.md` (v5 authority) self-check row 7; re-confirmed on the landed tree this REV-B pass |

**Consequence:** this landing triggers **NO re-pin mechanics, NO kot-correction record, and NO
frozen-hash re-derivation** — it is plain infra through the coordinator review-gate (same
discipline as every landing: review green → apply → $0 oracle green → one commit →
`registry-check` green). The ONLY registry action is **ASM-2514** (§5.2), which formalizes the
frozen projection model + sampling rule, because the v2 review (finding 5) requires the fixed
projection to be "formally review-gated and frozen before spend — not an informal model override."
The diffs read (never write) two pinned inputs: `construction-manifest.jsonl`
(`PINS` `a8cb3a8a…`, verified = the file's recomputed sha this pass) and the `f1k-eval-v1` items
(covered by the frozen record's corpus digest); `cmd_gate` re-verifies both at verdict time
(corpus-drift check, D2).

## 2. The design (what freezes)

### 2.1 Dataflow

```
control box ($0)   python3 poc/gcp/f1k_bringup_gate.py spec        # rule + corpus-sha witness
push (README §2)   poc/gcp/ (incl. f1k_bringup_gate.py + gate-corpus/{4 frozen files}) -> VM
VM (worker 5/5)    fcount   : tokenize ALL frozen corpus texts -> per-item T + measured f
                   realize  : frozen sampling rule -> N≈30 per-text run_score manifests
                   T1 (x8)  : UNPINNED timing + engine usage stats -> pinfile (bring-up pin @ PIN_GB)
                   T2 (all) : PINNED per-item timing (engine scoring timer, model-load excluded)
                   collect  : gate-inputs.json  -> GCS mirror; worker STOPS (unchanged contract)
control box        python3 poc/gcp/f1k_gcp.py gate --inputs gate-inputs.json
                   -> verify_pins + reuse-gate + corpus-drift check
                   -> PER-ITEM projection vs the frozen windows + f-branch
                   -> bringup-gate.json  verdict GREEN (exit 0) | STOP (exit 2, ERR_F1K_BRINGUP_GATE)
```

### 2.2 The frozen campaign prefill inventory (what the projection sums over)

Per-item multiplicities, envelope-exact against the frozen 19,964 [MEASURED cites; allocation
tags noted]:

| Population | Texts (source, sha §2.4) | m per text | Prefills | Basis |
|---|---|---|---|---|
| construction | 4,608 rows' `text`, `construction-manifest.jsonl` | 1 | 4,608 | PINS `a8cb3a8a…`; harness `README.md:128` "4,608 EXACT (96×16×3)" |
| main-tmpl | 1,573 × `template_text`, `test.jsonl` | 7 | 11,011 | `ARMS_MAIN` (`f1k_driver.py:228`) + `main_arm_passes` (`:2054-2071`): b0,d0,d1×3,d2,K = 7 template-prompt passes |
| main-d3 | 1,573 × `d3_template_text`, `test.jsonl` | 1 | 1,573 | d3-text is the only arm with a different (longer) prompt (`:1527-1529`) |
| pilot | 96 × `template_text`, `dev.jsonl` | 22 | 2,112 | registered ≤2,112 = grid 1,728 (9×4×48) + dev-96 3×96 + conditional 96 (harness `README.md:129`, driver `:87`); **uniform-over-dev allocation [STIPULATED]** — the 48-item grid subset is config-frozen, not derivable here; worst-case skew if the subset were the 48 longest dev items ≈ +40% on 10.6% of prefills ≈ **±4% of total hours [EXTRAPOLATED]**, disclosed in the artifact's model block |
| guard | 60 × `template_text`, `guard.jsonl` | 11 | 660 | registered ≤660 **worst-case bound** (`README.md:130`, driver `:371`); realized guard is 60×7-8 = 420-480 (`phase_guard` `:2115`), so this allocation **overstates** guard cost — cap-conservative; the floor side is protected by the −SE floor test (§2.6) [STIPULATED envelope allocation] |
| **mandatory total** | | | **19,964** | asserted fail-closed in code (`load_inventory`) |
| +REPLACE (variant) | 1,573 × `template_text` | +1 | 21,537 | `PREFILLS_WITH_REPLACE` (`f1k_gcp.py:96`) |

Word-anchor cross-check [MEASURED this pass]: test template mean 122.7 w (min 27, max 774), d3
146.0 w (max 804) → 8-arm blend (7×122.7 + 146.0)/8 = **125.6 w**, exactly the plan §1 anchor;
dev 83.8, guard 56.8, construction 30.76 — all match the plan/VERDICT recounts.

Prefill token count: **T_i = tokens(text_i) + 8** — the uniform continuation addend equal to the
functional-gate contlen convention [STIPULATED; the real scored continuation is the few-token
label, so +8 is a small conservative constant against 50-1,200-token prefills].

### 2.3 The frozen sampling rule (GAP-1) — deterministic, seeded, pre-specified [STIPULATED]

Frozen constants (in `f1k_bringup_gate.py`, registered by ASM-2514): `SAMPLE_SEED = 20260718`
(keys the tie-break hash ONLY — the rule contains no RNG); `QUANTILE_EDGES = (0, .20, .40, .60,
.80, .95, 1.0)`; `BIN_ALLOC = (4,4,4,4,4,6)`; `POP_FLOOR = 2` per population; `T1_N = 8`;
`N_SAMPLE_MAX = 34` (hard fail-closed cap).

1. Build the §2.2 inventory; compute the **prefill-mass-weighted** empirical distribution of
   T_p = T+8; realize 6 bins at the weighted quantile edges (top bin = the p95+ tail the v2
   review demanded).
2. Within each bin, sort distinct texts by `(T_p, sha256(SAMPLE_SEED:key))` and pick
   evenly-spaced ranks per `BIN_ALLOC` (4,4,4,4,4,6).
3. **Force-include the campaign max-T_p prefill text** (ties by the seed hash). This is the move
   that makes the estimator interpolation-only: the projection NEVER extrapolates above the
   sample (§2.6, fail-closed).
4. Population-coverage floors: any population with <2 selected texts gets deterministic ADDS of
   its median-T_p text (never removals; total capped at 34, fail-closed).
5. T1 subset: 8 evenly-spaced ranks over the selection excluding the global max (cost control).

Realized on the REAL corpora this pass (with mock token counts at f=1.45, since the tokenizer is
a bring-up artifact — the rule is T-relative, so the realization shifts with real T but the
mechanics are exercised): **N = 30 texts** (T1 = 8), bins [18, 62, 80, 111, 212, 455, 1174],
populations {construction 8, main-tmpl 7, main-d3 11, pilot 2, guard 2}, T_p range 28→1174
[MEASURED bench realization; the on-VM realization with real T is the binding one].

### 2.4 Measurement procedure on the VM (worker step 5/5, diff D3)

- **Tokenizer:** the staged estate's `tokenizer.json`; sha256 derived from bytes and exported as
  `TOK_SHA256` to the pinned kot-f1k-tok/1 wrapper `tok_glm52.py` (ASM-1971 bring-up pin;
  fail-closed on mismatch, offsets validated per ASM-2490). Engine-consistency (wrapper ids ==
  engine prefill ids) is the dump bring-up gate (a) — cross-referenced, not duplicated.
- **fcount:** tokenizes ALL 7,910 distinct texts (4,608 + 1,573×2 + 96 + 60) in one wrapper
  stream → `tokens-full.jsonl` (per-text T + ids) + `token-counts.json` (per-population f,
  blended f, corpus shas). Minutes of CPU, $≈0.02 [EXTRAPOLATED].
- **PIN_GB:** fixed from MEASURED free-RAM headroom: `MemAvailable − 8 GB` margin, clamped to
  [24, 50] (die below 24 — outside the M4 40-50 GB band) [STIPULATED margin; M4 band MEASURED].
  Recording/attestation semantics: `F1K-PIN-FILE-FIX.md` v5 (cross-reference; this step only
  fixes the number and derives the BRING-UP pin — it never fakes an attestation).
- **T1 (8 runs, UNPINNED):** ~~per-text `run_score` invocations in a dedicated cwd with
  `STATS=1`; `pinfile` merges any files found by glob; if the pin is underivable, T2 runs
  UNPINNED and the regime is recorded~~ **[SUPERSEDED — §B.1/§B.3, gate-fix review #2/#4: the
  engine interface is `STATS=<file>` (`kae-add-path.patch:175/:180/:183`), so `STATS=1` made
  every run overwrite ONE file named `1` and the pin derived from the LAST item, not the T1
  union. REV-B: one `STATS=<per-item path>` per run (rm'd first, asserted non-empty), an
  EXPLICIT manifest, a fail-closed sum-per-(layer,expert) merge with per-file sha provenance
  recorded in the gate artifact; an underivable pin is a fail-closed STOP (the gate REFUSES
  regime `unpinned` — shape (ii) was rejected), never an unpinned license.]** Ranked by count,
  cut at PIN_GB × the MEASURED `per_expert_bytes` 18,541,666.7 from `m4.json`; stats format =
  `probe-results/accum20.stats` [MEASURED]. stats_dump truncate-vs-append stays fetch-grade
  [ASM-1971] — the per-run fresh path is correct under either; the runner re-verifies the knob
  at the (7) semantic gate.
- **T2 (all ≈30 runs, the license timing):** one `run_score` invocation per sampled text with
  `PIN=pin_bringup.stats PIN_GB=<fixed>` (KAE fully unset, OMP pinned — identical env discipline
  to the functional gate), per-item s from the engine's own scoring timer (`[score N req | Xs`,
  model-load excluded); stderr pin evidence recorded per run. Per-invocation cold expert-cache
  differs from campaign steady-state in the conservative direction (page cache contributes only
  ~5%, M4) [MEASURED mechanism, STIPULATED direction].
- **Budget guard:** `KOT_F1K_GATE_MAX_S` (default 10,800 s) — exceeding it **dies fail-closed**
  (no silent truncation of the sample, per the no-silent-caps rule).
- **collect:** merges sample spec + T1/T2 results + token counts + recorded SPOT rate
  (`KOT_F1K_SPOT_RATE` — the construction rate, NOT the on-demand bring-up VM's rate; spot and
  on-demand n2d-highmem-8 are the same hardware, so s transfers [STIPULATED]) + pin block →
  `gate-inputs.json`. **No verdict on the VM.** Partial T2 results are refused fail-closed.

### 2.5 The f measurement and the mechanical f-branch (GAP-2)

`f_pop = Σ m_i·tokens(text_i) / Σ m_i·words(text_i)` per population and blended over the full
mandatory inventory (prefill-multiplicity-weighted); **words = whitespace split** — the same
convention behind the plan's word anchors and therefore behind the f*≈1.64 breach arithmetic that
froze the 1.60 threshold [STIPULATED convention, matching the VERDICT's "independent whitespace
recount"]. Texts only (the +8 continuation addend enters T, not f). The artifact carries
per-population f, blended f, the threshold, and the branch; the verdict requires
**f_blended ≤ 1.60** as a conjunct — `f > 1.60` STOPs even if the ledger happens to fit, exactly
the plan §7 rule (the ≤$300 contingent path is a maintainer re-freeze decision, never
autonomous).

### 2.6 The frozen projection model (GAP-3) — and what it can/cannot bound

**Model (frozen by ASM-2514, printed verbatim into every gate artifact):**

- Knots: per-stratum (mean T_p, mean s) from the T2 per-item timings; strata = the 6 sample bins
  + the max-T singleton. Stratum SE = sd/√n; **singleton knots borrow the worst measured stratum
  SE** [STIPULATED, conservative]. Non-monotone knot sequences are pooled by weighted PAVA;
  every repair is recorded in the artifact.
- `ŝ(T)`: monotone piecewise-linear interpolation over the knots. Below the min knot: central
  and hi variants are CONSTANT at the first knot (overestimates the cheapest prefills →
  cap-conservative); the lo variant linearly extrapolates downward, floored at 0.35×s(minknot)
  [STIPULATED] — so the $73/260.6 h floor test is NOT fed by an overestimate. **Above the max
  knot: FAIL-CLOSED** (`ERR_F1K_GATE_MODEL`) — impossible by construction since the campaign
  max-T text is sampled, but asserted anyway.
- Projection: `hours = Σ_pop Σ_texts m_i·ŝ(T_i)/3600`, `usd = hours × recorded spot rate`,
  computed at three levels: central, hi (+1 SE knots), lo (−1 SE knots, floor-side model).
- **Verdict rule:** ~~GREEN iff ALL of: rate in window; f ≤ 1.60; central hours/usd in windows;
  hi ≤ caps; lo ≥ floors; prefills ≥ 11,011; tokenizer REAL; pin regime known (nine
  conjuncts, reserve-blind)~~ **[SUPERSEDED — this reserve-blind nine-conjunct text was the
  gate-fix review finding-8 stale chain; the OPERATIVE rule is §A2 + §B.3: caps tested
  RESERVE-INCLUSIVE (+$8 / +8/rate h) at central AND +1SE; dump (a)/(b)/(c) + functional
  literal-PASS conjuncts; pin regime MUST be `pinned-bringup` (unpinned REFUSED); per-T2-run
  pin-ENGAGEMENT evidence for the bound sha/PIN_GB; floors compute-only.]** GREEN →
  construction proceeds WITHOUT re-surfacing (standing authorization, report-after). Anything
  else → STOP: exit 2 `ERR_F1K_BRINGUP_GATE`, mandatory maintainer surface with the §7.3
  salvage options printed. The frozen thresholds and the full model block (knots, repairs, SE
  rule, below/above-knot rules) are embedded in `bringup-gate.json` so the decision is
  auditable byte-for-byte.
- The retired per-average number (`19,964 × ŝ(mean T)`) is still computed and printed as
  `per_average_naive_hours_RETIRED` + divergence % — the audit trail for review finding 3.

**What the sample CAN bound [honest scope]:** T-driven cost across the entire campaign T-range
(interpolation-only, max-T anchored); stratum-mean noise (±1 SE band, n=4-6 per bin); the
direction and rough size of the pin lever (T1-unpinned vs T2-pinned margin on 8 texts, reported
as a diagnostic); the f tokenization uncertainty (eliminated — f is measured exactly, per item,
over the full corpora).

**What it CANNOT bound [disclosed in the artifact]:** (i) content/routing-driven s variance at
fixed T beyond within-stratum sd at n≈4; (ii) bring-up-pin h_pin transfer to the full
construction corpus — ~~the campaign pin is re-derived on the real construction corpus (PIN-fix
mechanics)~~ **[SUPERSEDED §C.1/ASM-2517: re-derivation is WITHDRAWN (structurally impossible
through the pinned builder; DEFERRED, bead `kernel-of-truth-8cpm`) — the LICENSED bring-up pin
runs the WHOLE campaign]**; the transfer residual is bounded by the frozen construction
checkpoints (240/1056/2304) and at pilot by the realized counters (plan §3.1/§5, GAP-3b); (iii) future
spot-rate drift (the rate is the recorded assignment, re-checked at construction provision);
(iv) multi-week thermal/contention drift; (v) the pilot uniform-allocation skew (±4% bound,
§2.2); (vi) the guard envelope overstatement (§2.2). Long-tail risk specifically: the top-5%
bin gets 6 samples AND the exact max item is timed — the tail is measured, not extrapolated;
what remains unbounded is tail *variance*, partially covered by the +1 SE cap test.

### 2.7 The gate artifact (`bringup-gate.json`, schema ~~kot-f1k-bringup-gate/1~~ **[SUPERSEDED D14/ASM-2517: `kot-f1k-bringup-gate/2` + the REQUIRED `model_bundle` binding; every consumer refuses non-`/2`]**)

Top-level fields (all emitted by `project()`, D1): `schema`, `verdict` (GREEN|STOP), `reasons`,
`checks` (the 9 named booleans), `f` {blended, threshold 1.60, branch, per_population,
convention}, `tokenizer` {mode REAL, sha256}, `corpus_sha256` (the 4 files), `sample` (full
realized spec: seed, rule, bin edges, entries with why-selected), `model` (type, raw +
isotonic knots, repairs, SE rule, cont addend), `pin` {pin_file_sha256, PIN_GB, regime,
cross-ref note → PIN-fix}, `rate` {usd/h, source}, `projection` {prefills, replace flag,
hours/usd at central/hi/lo, blended-s equivalent, per-population hours, the RETIRED per-average
+ divergence}, `thresholds` (the frozen windows it compared against), `semantics` (the §7 rule
verbatim). `--replace` emits the 21,537-prefill variant.

### 2.8 Cost of the gate at execution [EXTRAPOLATED]

At the probe anchors (c(96)=75.2 s, c(384)=290.0 s, ~T^1.18): T2 ≈ 96 min + T1 ≈ 28 min ≈ 2.1 h
≈ **$1.19** at the on-demand ~$0.579/h, plus ~$0.02 tokenization and per-spawn pin-load wall
overhead (~15 min, outside the scoring timer). This replaces the plan's ~$0.5 GAP-1/2 line item;
total bring-up lands at the **upper edge of the ~$2-3 envelope (~$3-3.5 worst case)** — priced
honestly here rather than trimmed silently; the `KOT_F1K_GATE_MAX_S` guard bounds the exposure
fail-closed, and the whole bring-up remains outside the frozen spot ledger (on-demand throwaway
VM, `f1k_gcp.py:119-133`).

## 3. The exact diffs (apply in this order, AFTER the seq-3 landing commit)

Apply from the repo root with `git apply <file>` (or `patch -p1`). D1 is a new file (write the
fenced bytes exactly; must end with a single trailing newline). Every artifact below is
byte-verified: sha256 given, extraction command in §4.2.

| # | Target | Kind | sha256 of the artifact below |
|---|---|---|---|
| D1 | `poc/gcp/f1k_bringup_gate.py` (NEW, mode 0644) | full file | `4cb3c858d2da63da9f6c556b0b571b15491b692b52ae1433e43dca54ec1f7b7a` |
| D2 | `poc/gcp/f1k_gcp.py` | unified diff (U1) | `da466c986c24d3b568c2f0a1350bce778f33e4610fcb7202a42a02896496d0c8` |
| D3 | `poc/gcp/f1k_worker.sh` | unified diff (U3) | `2fa9992383d1176543557ecdc8cf353eac3ec735f9b3aee7a0c7ef2ff9bf102a` |
| D4 | `poc/gcp/README.md` | unified diff (U3) | `fda84a6e7c83b4961d80ed72454c77287bf393006308a088868940e83443898d` |

### 3.1 D1 — NEW FILE `poc/gcp/f1k_bringup_gate.py`

<!-- BEGIN-ARTIFACT D1 poc/gcp/f1k_bringup_gate.py sha256=4cb3c858d2da63da9f6c556b0b571b15491b692b52ae1433e43dca54ec1f7b7a -->
```python
#!/usr/bin/env python3
"""f1k_bringup_gate.py — kot-f1k-bringup-gate/1: the FIXED F1-K bring-up
affordability gate (poc/gcp/F1K-BRINGUP-GATE-FIX.md v1; closes GAP-1/2/3 of
F1K-CONSTRUCTION-PLAN.md v3 §4.2, per the v2 review findings 3/4/5 of
poc/gpt56-review/f1k-construction-review-VERDICT.md).

WHAT THIS FIXES (spec: the fix memo; frozen rule: CONSTRUCTION-PLAN v3 §7):
  GAP-1  the construction-license timing input is now a DETERMINISTIC,
         seeded, stratified sample of the REAL frozen corpora (never the
         synthetic 10xT96/10xT384 functional-gate mix — that stays a
         secondary diagnostic only, f1k_gcp.py `affordability`).
  GAP-2  the words->tokens factor f is MEASURED on the full frozen corpora
         with the REAL bring-up tokenizer (tok_glm52.py, ASM-1971 pin) and
         the frozen `f <= 1.60` branch of the §7 rule is wired mechanically.
  GAP-3  the ledger projection is PER-ITEM token-aware: sum of s_hat(T_i)
         over every prefill of the frozen 19,964-prefill envelope at its
         MEASURED token count — never `19964 * one_average` (v2 review
         finding 3: a single average can approve an over-budget long tail).

SUBCOMMANDS (control box = $0; VM = on the bring-up box):
  spec     ($0, control box) witness the sampling rule + corpus shas
  fcount   (VM) tokenize the frozen corpora -> per-item T + measured f
  realize  (VM) apply the frozen sampling rule -> timing sample manifests
  pinfile  (VM) merge engine usage stats -> bring-up pin file at PIN_GB
  collect  (VM) merge timing results -> gate-inputs.json (no verdict here)
  project  (control box; use `f1k_gcp.py gate`) -> bringup-gate.json GREEN/STOP
  selftest ($0) end-to-end mock oracle: GREEN, STOP long-tail (the review
           finding-3 divergence proven), f-branch both sides, fail-closed

Zero non-stdlib deps on the control box; the VM path shells out to the
pinned kot-f1k-tok/1 wrapper (tok_glm52.py) for all real tokenization.
Deterministic: no wall-clock, no RNG (SAMPLE_SEED keys tie-break hashing
only). Fail-closed with ERR_* codes; no silent fallbacks.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

SCHEMA = "kot-f1k-bringup-gate/1"

# ---------------------------------------------------------------------------
# FROZEN GATE CONSTANTS (fix memo §2; every value tagged there)
# ---------------------------------------------------------------------------
SAMPLE_SEED = 20260718        # [STIPULATED] keys the tie-break hash ONLY
F_THRESHOLD = 1.60            # CONSTRUCTION-PLAN v3 §4.2/§7 frozen threshold
CONT_TOKENS = 8               # [STIPULATED] = the functional-gate contlen;
                              # also the uniform continuation addend T_i = T_text + 8
QUANTILE_EDGES = (0.0, 0.20, 0.40, 0.60, 0.80, 0.95, 1.0)   # [STIPULATED]
BIN_ALLOC = (4, 4, 4, 4, 4, 6)   # per-bin sampled texts; + campaign max-T
T1_N = 8                      # unpinned stats/margin subset size [STIPULATED]
POP_FLOOR = {"construction": 2, "pilot": 2, "guard": 2,
             "main-tmpl": 2, "main-d3": 2}    # population coverage floors
N_SAMPLE_MAX = 34             # hard cap incl. coverage adds (fail-closed)
FLOOR_EXTRAP_MIN_FRAC = 0.35  # [STIPULATED] s_lo(T) >= 0.35*s_bar(minknot)
SE_MULT = 1.0                 # frozen band rule: +-1 SE
PER_EXPERT_BYTES = 18541666.7 # [MEASURED] probe-results/m4.json per_expert_bytes

# Frozen campaign inventory (envelope-exact; fix memo §2.2, all cited):
# construction 4,608 x1 [PINS construction-manifest]; main 1,573 x (7 tmpl +
# 1 d3) [ARMS_MAIN + R_DRNG=3]; pilot 96 x 22 (template-only; VERDICT #1);
# guard 60 x 11 (registered <=660 bound); +REPLACE 1,573 x1 tmpl.
N_CONSTRUCTION = 4608
N_TEST, M_MAIN_TMPL, M_MAIN_D3 = 1573, 7, 1
N_DEV, M_PILOT = 96, 22
N_GUARD, M_GUARD = 60, 11
M_REPLACE = 1
MANDATORY_PREFILLS = 19964    # must reproduce exactly (asserted)

CORPUS_FILES = ("construction-manifest.jsonl", "test.jsonl", "dev.jsonl",
                "guard.jsonl")


def die(code, msg):
    sys.stderr.write("ERR_%s: %s\n" % (code, msg))
    raise SystemExit(2)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def tiehash(key):
    return hashlib.sha256(("%d:%s" % (SAMPLE_SEED, key)).encode()).hexdigest()


def wcount(text):
    """Whitespace word count — the SAME convention behind the plan's word
    anchors (30.8/122.7/56.8/83.8) and the f<=1.60 threshold derivation."""
    return len(text.split())


# ---------------------------------------------------------------------------
# frozen campaign inventory (population, multiplicity, text) from the corpora
# ---------------------------------------------------------------------------
def load_inventory(corpus_dir):
    d = Path(corpus_dir)
    for f in CORPUS_FILES:
        if not (d / f).is_file():
            die("F1K_GATE_CORPUS", "missing corpus file %s" % (d / f))
    inv = []

    def rows(name):
        return [json.loads(l) for l in open(d / name, encoding="utf-8")
                if l.strip()]

    cons = rows("construction-manifest.jsonl")
    if len(cons) != N_CONSTRUCTION:
        die("F1K_GATE_CORPUS", "construction-manifest rows %d != %d"
            % (len(cons), N_CONSTRUCTION))
    for i, r in enumerate(cons):
        inv.append({"key": "construction:%04d" % i, "pop": "construction",
                    "m": 1, "text": r["text"]})
    test = rows("test.jsonl")
    if len(test) != N_TEST:
        die("F1K_GATE_CORPUS", "test rows %d != %d" % (len(test), N_TEST))
    for r in test:
        inv.append({"key": "main-tmpl:%s" % r["item_id"], "pop": "main-tmpl",
                    "m": M_MAIN_TMPL, "text": r["template_text"]})
        inv.append({"key": "main-d3:%s" % r["item_id"], "pop": "main-d3",
                    "m": M_MAIN_D3, "text": r["d3_template_text"]})
    dev = rows("dev.jsonl")
    if len(dev) != N_DEV:
        die("F1K_GATE_CORPUS", "dev rows %d != %d" % (len(dev), N_DEV))
    for r in dev:
        inv.append({"key": "pilot:%s" % r["item_id"], "pop": "pilot",
                    "m": M_PILOT, "text": r["template_text"]})
    guard = rows("guard.jsonl")
    if len(guard) != N_GUARD:
        die("F1K_GATE_CORPUS", "guard rows %d != %d" % (len(guard), N_GUARD))
    for r in guard:
        inv.append({"key": "guard:%s" % r["item_id"], "pop": "guard",
                    "m": M_GUARD, "text": r["template_text"]})
    total = sum(e["m"] for e in inv)
    if total != MANDATORY_PREFILLS:
        die("F1K_GATE_CORPUS", "inventory prefills %d != frozen %d"
            % (total, MANDATORY_PREFILLS))
    return inv


def corpus_shas(corpus_dir):
    return {f: sha256_file(Path(corpus_dir) / f) for f in CORPUS_FILES}


# ---------------------------------------------------------------------------
# tokenization (real: the pinned kot-f1k-tok/1 wrapper; mock: --mock-f)
# ---------------------------------------------------------------------------
def tokenize(inv, args):
    if args.mock_f is not None:
        # $0 MOCK path (selftest / dry-run ONLY; clearly labeled in output):
        # T = round(W * mock_f), ids deterministic in-vocab like the
        # functional-gate sample. NEVER a license input.
        for e in inv:
            w = wcount(e["text"])
            t = max(4, round(w * args.mock_f))
            e["W"], e["T"] = w, t
            e["ids"] = [10 + (int(tiehash(e["key"])[:8], 16) + i) % 180
                        for i in range(t)]
        return {"mode": "MOCK", "mock_f": args.mock_f, "sha256": None}
    if not (args.tok_wrapper and args.tokenizer):
        die("F1K_GATE_TOK", "--tok-wrapper and --tokenizer required "
            "(or --mock-f for the $0 mock path)")
    tok_sha = sha256_file(args.tokenizer)
    env = dict(os.environ, TOK_SHA256=tok_sha)
    proc = subprocess.Popen(
        [sys.executable, args.tok_wrapper, args.tokenizer],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
    inp = "".join(json.dumps({"text": e["text"]}) + "\n" for e in inv)
    out, _ = proc.communicate(inp.encode("utf-8"))
    if proc.returncode != 0:
        die("F1K_GATE_TOK", "tok_glm52.py exited %d" % proc.returncode)
    lines = out.decode("utf-8").splitlines()
    if len(lines) != len(inv):
        die("F1K_GATE_TOK", "tokenizer emitted %d lines for %d texts"
            % (len(lines), len(inv)))
    for e, l in zip(inv, lines):
        ids = json.loads(l)["ids"]
        e["W"], e["T"], e["ids"] = wcount(e["text"]), len(ids), ids
    return {"mode": "REAL", "mock_f": None, "sha256": tok_sha}


def cmd_fcount(args):
    inv = load_inventory(args.corpus_dir)
    tokinfo = tokenize(inv, args)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "tokens-full.jsonl", "w") as f:
        for e in inv:
            f.write(json.dumps({"key": e["key"], "pop": e["pop"],
                                "m": e["m"], "W": e["W"], "T": e["T"],
                                "ids": e["ids"]}) + "\n")
    pops, blend_t, blend_w = {}, 0, 0
    for e in inv:
        p = pops.setdefault(e["pop"], {"n_texts": 0, "prefills": 0,
                                       "words_x_m": 0, "tokens_x_m": 0})
        p["n_texts"] += 1
        p["prefills"] += e["m"]
        p["words_x_m"] += e["m"] * e["W"]
        p["tokens_x_m"] += e["m"] * e["T"]
        blend_t += e["m"] * e["T"]
        blend_w += e["m"] * e["W"]
    for p in pops.values():
        p["f"] = round(p["tokens_x_m"] / p["words_x_m"], 4)
    summary = {
        "schema": SCHEMA + ":token-counts",
        "tokenizer": tokinfo,
        "corpus_sha256": corpus_shas(args.corpus_dir),
        "populations": pops,
        "prefills_mandatory": MANDATORY_PREFILLS,
        "f_blended": round(blend_t / blend_w, 4),
        "f_threshold": F_THRESHOLD,
        "f_convention": "whitespace words; texts only (no continuation "
                        "addend) — matches the plan word anchors",
    }
    (outdir / "token-counts.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: summary[k] for k in
                      ("f_blended", "tokenizer", "populations")}, indent=2))
    return 0


# ---------------------------------------------------------------------------
# frozen sampling rule (fix memo §2.3) — deterministic, seeded, stratified
# ---------------------------------------------------------------------------
def weighted_quantile_edges(entries):
    """Prefill-mass-weighted T-quantile edges over Tp = T + CONT_TOKENS."""
    pts = sorted(((e["T"] + CONT_TOKENS, e["m"]) for e in entries))
    total = sum(m for _, m in pts)
    edges, acc, qi = [pts[0][0]], 0, 1
    for tp, m in pts:
        acc += m
        while qi < len(QUANTILE_EDGES) - 1 and \
                acc >= QUANTILE_EDGES[qi] * total:
            edges.append(tp)
            qi += 1
    while len(edges) < len(QUANTILE_EDGES):
        edges.append(pts[-1][0])
    edges[-1] = pts[-1][0]
    return edges


def select_sample(entries):
    """The STIPULATED rule, verbatim from the fix memo §2.3: bin by weighted
    quantiles; evenly spaced (T, tiehash)-ranks per bin; force the campaign
    max-T prefill; then population-coverage ADDS (never removals)."""
    for e in entries:
        e["Tp"] = e["T"] + CONT_TOKENS
    edges = weighted_quantile_edges(entries)
    bins = [[] for _ in range(len(QUANTILE_EDGES) - 1)]
    for e in entries:
        for j in range(len(bins)):
            hi_ok = e["Tp"] <= edges[j + 1] if j == len(bins) - 1 \
                else e["Tp"] < edges[j + 1]
            if e["Tp"] >= edges[j] and hi_ok:
                bins[j].append(e)
                break
    chosen, seen = [], set()

    def pick(e, bin_id, why):
        if e["key"] in seen:
            return False
        seen.add(e["key"])
        chosen.append({"key": e["key"], "pop": e["pop"], "bin": bin_id,
                       "W": e["W"], "T": e["T"], "Tp": e["Tp"],
                       "why": why, "ids": e["ids"]})
        return True

    for j, b in enumerate(bins):
        b.sort(key=lambda e: (e["Tp"], tiehash(e["key"])))
        n, k = len(b), BIN_ALLOC[j]
        if n == 0:
            die("F1K_GATE_SAMPLE", "empty T bin %d — rule cannot realize" % j)
        for i in range(k):
            pick(b[min(n - 1, int((i + 0.5) * n / k))], j, "rank")
    allmax = max(entries, key=lambda e: (e["Tp"], tiehash(e["key"])))
    pick(allmax, len(bins) - 1, "campaign-max-T")
    # population floors: deterministic ADDS of the population's median-Tp text
    for pop in sorted(POP_FLOOR):
        have = sum(1 for c in chosen if c["pop"] == pop)
        cand = sorted((e for e in entries if e["pop"] == pop),
                      key=lambda e: (e["Tp"], tiehash(e["key"])))
        i = len(cand) // 2
        while have < POP_FLOOR[pop] and cand:
            e = cand[i % len(cand)]
            j = next(k for k in range(len(bins)) if e in bins[k])
            if pick(e, j, "pop-floor"):
                have += 1
            i += 1
    if len(chosen) > N_SAMPLE_MAX:
        die("F1K_GATE_SAMPLE", "sample %d > cap %d" % (len(chosen),
                                                       N_SAMPLE_MAX))
    chosen.sort(key=lambda c: (c["Tp"], tiehash(c["key"])))
    for i, c in enumerate(chosen):
        c["sample_id"] = "s%03d" % i
    return edges, chosen


def cmd_realize(args):
    tokdir = Path(args.tokens)
    entries = [json.loads(l)
               for l in open(tokdir / "tokens-full.jsonl", encoding="utf-8")]
    edges, chosen = select_sample(entries)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    # one run_score manifest per sampled text (per-item engine timer)
    for c in chosen:
        t = c["T"]
        if t < CONT_TOKENS + 2:
            die("F1K_GATE_SAMPLE", "%s: T=%d too short for cont=%d"
                % (c["key"], t, CONT_TOKENS))
        line = "%d %d %s" % (t - CONT_TOKENS, CONT_TOKENS,
                             " ".join(map(str, c["ids"])))
        (outdir / ("sample-%s.score" % c["sample_id"])).write_text(line + "\n")
    # T1 (unpinned stats/margin) subset: evenly spaced ranks EXCLUDING the
    # global max (cost control; the max is timed pinned in T2 regardless)
    body = chosen[:-1]
    t1 = [body[min(len(body) - 1, int((i + 0.5) * len(body) / T1_N))]
          ["sample_id"] for i in range(T1_N)]
    t1 = sorted(set(t1))
    spec = {
        "schema": SCHEMA + ":timing-sample",
        "seed": SAMPLE_SEED,
        "rule": {"quantile_edges": list(QUANTILE_EDGES),
                 "bin_alloc": list(BIN_ALLOC), "cont_tokens": CONT_TOKENS,
                 "pop_floor": POP_FLOOR, "t1_n": T1_N,
                 "text": "fix memo §2.3 (frozen)"},
        "realized_bin_edges_Tp": edges,
        "n": len(chosen),
        "t1_sample_ids": t1,
        "entries": [{k: c[k] for k in ("sample_id", "key", "pop", "bin",
                                       "W", "T", "Tp", "why")}
                    for c in chosen],
    }
    (outdir / "timing-sample.json").write_text(json.dumps(spec, indent=2))
    print("timing sample: %d texts (T1 subset %d); bins %s"
          % (len(chosen), len(t1), edges))
    return 0


# ---------------------------------------------------------------------------
# bring-up pin file from engine usage stats ([MEASURED] accum20.stats format)
# ---------------------------------------------------------------------------
def cmd_pinfile(args):
    import glob as g
    merged = {}
    files_ok = 0
    for path in sorted(g.glob(args.stats_glob)):
        try:
            triples = []
            for ln in open(path, encoding="utf-8", errors="strict"):
                parts = ln.split()
                if not parts:
                    continue
                if len(parts) != 3:
                    raise ValueError("non-triple line")
                l, e, c = (int(x) for x in parts)
                triples.append((l, e, c))
            for l, e, c in triples:
                merged[(l, e)] = merged.get((l, e), 0) + c
            files_ok += 1
        except (ValueError, UnicodeDecodeError):
            print("pinfile: skipping non-conforming %s" % path)
    if files_ok == 0 or not merged:
        die("F1K_GATE_PIN", "no conforming '<layer> <expert> <count>' stats "
            "under %s — pin underivable; T2 must run UNPINNED (conservative, "
            "recorded; never silently pinned)" % args.stats_glob)
    budget = args.pin_gb * 1e9
    ranked = sorted(merged.items(), key=lambda kv: (-kv[1], kv[0]))
    out, used = [], 0.0
    for (l, e), c in ranked:
        if used + PER_EXPERT_BYTES > budget:
            break
        used += PER_EXPERT_BYTES
        out.append("%d %d %d" % (l, e, c))
    Path(args.out).write_text("\n".join(out) + "\n")
    print(json.dumps({"pin_file": args.out, "experts": len(out),
                      "gb_used": round(used / 1e9, 2), "pin_gb": args.pin_gb,
                      "stats_files_merged": files_ok,
                      "sha256": sha256_file(args.out)}))
    return 0


# ---------------------------------------------------------------------------
# collect: on-VM merge of timing results -> gate-inputs.json (NO verdict)
# ---------------------------------------------------------------------------
def _read_results(path):
    if not path or not Path(path).is_file():
        return {}
    out = {}
    for l in open(path, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            out[r["sample_id"]] = r
    return out


def cmd_collect(args):
    sample = json.loads(Path(args.sample).read_text())
    tokdir = Path(args.tokens)
    counts = json.loads((tokdir / "token-counts.json").read_text())
    t2 = _read_results(args.t2)
    t1 = _read_results(args.t1)
    missing = [e["sample_id"] for e in sample["entries"]
               if e["sample_id"] not in t2]
    if missing:
        die("F1K_GATE_COLLECT", "T2 timing missing for %s (fail-closed: "
            "partial samples never project)" % ",".join(missing))
    # compact per-prefill inventory for the control-box projection
    inv_t = [[e["pop"], e["m"], e["T"] + CONT_TOKENS] for e in
             (json.loads(l) for l in open(tokdir / "tokens-full.jsonl"))]
    gate_inputs = {
        "schema": SCHEMA + ":gate-inputs",
        "token_counts": counts,
        "timing_sample": {k: sample[k] for k in
                          ("seed", "rule", "realized_bin_edges_Tp", "n",
                           "t1_sample_ids", "entries")},
        "t2_pinned_runs": [t2[e["sample_id"]] for e in sample["entries"]],
        "t1_unpinned_runs": sorted(t1.values(),
                                   key=lambda r: r["sample_id"]),
        "inventory_t": inv_t,
        "rate_usd_per_hour": float(args.rate),
        "rate_source": "coordinator-recorded assigned SPOT rate "
                       "(KOT_F1K_SPOT_RATE) — the construction rate, NOT "
                       "the on-demand bring-up VM's rate",
        "pin": {"pin_file_sha256": args.pin_sha or None,
                "pin_gb": float(args.pin_gb) if args.pin_gb else None,
                "regime": args.pin_regime,
                "note": "derivation + truthful-attestation mechanics: "
                        "F1K-PIN-FILE-FIX.md v2 (cross-reference)"},
    }
    Path(args.out).write_text(json.dumps(gate_inputs, indent=2))
    print("gate-inputs written: %s (%d T2 runs, %d T1 runs, regime %s)"
          % (args.out, len(t2), len(t1), args.pin_regime))
    return 0


# ---------------------------------------------------------------------------
# project: the mechanical GREEN/STOP verdict (control box, via f1k_gcp.py)
# ---------------------------------------------------------------------------
def _isotonic(knots):
    """PAVA pooling (weighted by n) of (T, s, se, n) knots so s is
    non-decreasing in T; repairs recorded."""
    pools = [dict(k, pool=[k["stratum"]]) for k in knots]
    repaired = []
    i = 0
    while i < len(pools) - 1:
        if pools[i]["s"] > pools[i + 1]["s"] + 1e-12:
            a, b = pools[i], pools[i + 1]
            n = a["n"] + b["n"]
            merged = {"T": (a["T"] * a["n"] + b["T"] * b["n"]) / n,
                      "s": (a["s"] * a["n"] + b["s"] * b["n"]) / n,
                      "se": max(a["se"], b["se"]), "n": n,
                      "stratum": "%s+%s" % (a["stratum"], b["stratum"]),
                      "pool": a["pool"] + b["pool"]}
            repaired.append(merged["stratum"])
            pools[i:i + 2] = [merged]
            i = max(0, i - 1)
        else:
            i += 1
    return pools, repaired


def _interp(knots, sfield, t, below):
    """Piecewise-linear in T over knots; `below` in {'const','extrap'};
    above max T: FAIL-CLOSED (campaign max-T is sampled by construction)."""
    ts = [k["T"] for k in knots]
    ss = [k[sfield] for k in knots]
    if t > ts[-1] + 1e-9:
        die("F1K_GATE_MODEL", "T=%.0f above max sampled knot %.0f — "
            "extrapolation above the sample is FORBIDDEN (the campaign "
            "max-T prefill must be in the sample)" % (t, ts[-1]))
    if t <= ts[0]:
        if below == "const" or len(ts) < 2:
            return ss[0]
        slope = (ss[1] - ss[0]) / max(1e-9, ts[1] - ts[0])
        return max(FLOOR_EXTRAP_MIN_FRAC * ss[0],
                   ss[0] - slope * (ts[0] - t))
    for i in range(len(ts) - 1):
        if t <= ts[i + 1]:
            frac = (t - ts[i]) / max(1e-9, ts[i + 1] - ts[i])
            return ss[i] + frac * (ss[i + 1] - ss[i])
    return ss[-1]


def build_knots(inputs):
    ent = {e["sample_id"]: e for e in inputs["timing_sample"]["entries"]}
    strata = {}
    for r in inputs["t2_pinned_runs"]:
        e = ent[r["sample_id"]]
        sid = "max" if e["why"] == "campaign-max-T" else "bin%d" % e["bin"]
        strata.setdefault(sid, []).append((e["Tp"], float(r["s"])))
    knots = []
    for sid, pts in strata.items():
        n = len(pts)
        tbar = sum(t for t, _ in pts) / n
        sbar = sum(s for _, s in pts) / n
        sd = (math.sqrt(sum((s - sbar) ** 2 for _, s in pts) / (n - 1))
              if n > 1 else None)
        knots.append({"stratum": sid, "T": tbar, "s": sbar, "n": n,
                      "sd": sd, "se": (sd / math.sqrt(n)) if sd else None})
    fallback = max((k["se"] for k in knots if k["se"] is not None),
                   default=0.0)
    for k in knots:
        if k["se"] is None:
            k["se"] = fallback   # [STIPULATED] singleton knots borrow the
            k["sd"] = None       # worst measured stratum SE (conservative)
    knots.sort(key=lambda k: k["T"])
    pooled, repaired = _isotonic(knots)
    return knots, pooled, repaired


def project(inputs, frozen, replace=False, out_path=None):
    tc = inputs["token_counts"]
    if tc["tokenizer"]["mode"] != "REAL" and not inputs.get("_allow_mock"):
        die("F1K_GATE_MOCK", "token counts are MOCK — a mock gate never "
            "licenses spend (selftest/dry-run only)")
    raw_knots, knots, repaired = build_knots(inputs)
    rate = inputs["rate_usd_per_hour"]
    inv = list(inputs["inventory_t"])
    if replace:
        inv = inv + [[p, M_REPLACE, t] for p, m, t in inv
                     if p == "main-tmpl" and m == M_MAIN_TMPL]
    prefills = sum(m for _, m, _ in inv)

    def total_h(sfield, below):
        by_pop, s_tot = {}, 0.0
        for pop, m, t in inv:
            s = m * _interp(knots, sfield, t, below)
            s_tot += s
            by_pop[pop] = by_pop.get(pop, 0.0) + s
        return s_tot / 3600.0, {p: round(v / 3600.0, 1)
                                for p, v in sorted(by_pop.items())}
    for k in knots:
        k["s_hi"] = k["s"] + SE_MULT * k["se"]
        k["s_lo"] = max(0.0, k["s"] - SE_MULT * k["se"])
    h_c, by_pop = total_h("s", "const")
    h_hi, _ = total_h("s_hi", "const")
    h_lo, _ = total_h("s_lo", "extrap")
    usd_c, usd_hi, usd_lo = (h * rate for h in (h_c, h_hi, h_lo))
    # the per-average comparison the fix retires (audit trail, review #3)
    wmean_t = sum(m * t for _, m, t in inv) / prefills
    naive_h = prefills * _interp(knots, "s", wmean_t, "const") / 3600.0
    f_blend = tc["f_blended"]
    lo_h, hi_h = frozen["instance_hours"]
    lo_u, hi_u = frozen["usd_total"]
    checks = {
        "rate_in_window":
            frozen["rate_window"][0] <= rate <= frozen["rate_window"][1],
        "f_le_threshold": f_blend <= F_THRESHOLD,
        "central_hours_in_window": lo_h <= h_c <= hi_h,
        "central_usd_in_window": lo_u <= usd_c <= hi_u,
        "hi_band_below_caps": h_hi <= hi_h and usd_hi <= hi_u,
        "lo_band_above_floors": h_lo >= lo_h and usd_lo >= lo_u,
        "prefills_ge_min": prefills >= frozen["prefills_min"],
        "tokenizer_real": tc["tokenizer"]["mode"] == "REAL"
            or bool(inputs.get("_allow_mock")),
        "pin_regime_known":
            inputs["pin"]["regime"] in ("pinned-bringup", "unpinned"),
    }
    reasons = []
    if not checks["f_le_threshold"]:
        reasons.append("measured blended f %.4f > %.2f — §7 STOP branch: "
                       "the contingent <=$300 path is a MAINTAINER re-freeze "
                       "decision, never autonomous" % (f_blend, F_THRESHOLD))
    if not checks["rate_in_window"]:
        reasons.append("rate %.4f outside frozen window %s"
                       % (rate, frozen["rate_window"]))
    if not checks["central_hours_in_window"]:
        reasons.append("central projection %.1f h outside [%.1f, %.1f]"
                       % (h_c, lo_h, hi_h))
    if not checks["central_usd_in_window"]:
        reasons.append("central projection $%.2f outside [$%.0f, $%.0f]"
                       % (usd_c, lo_u, hi_u))
    if not checks["hi_band_below_caps"]:
        reasons.append("+%gSE projection %.1f h / $%.2f breaches a cap "
                       "(%.0f h / $%.0f)" % (SE_MULT, h_hi, usd_hi,
                                             hi_h, hi_u))
    if not checks["lo_band_above_floors"]:
        reasons.append("-%gSE projection %.1f h / $%.2f breaches a floor "
                       "(%.1f h / $%.0f) — an honest ledger cannot validate"
                       % (SE_MULT, h_lo, usd_lo, lo_h, lo_u))
    if not checks["prefills_ge_min"]:
        reasons.append("prefills %d < %d" % (prefills,
                                             frozen["prefills_min"]))
    if not checks["pin_regime_known"]:
        reasons.append("unknown pin regime %r" % (inputs["pin"]["regime"],))
    verdict = "GREEN" if all(checks.values()) else "STOP"
    art = {
        "schema": SCHEMA,
        "verdict": verdict,
        "reasons": reasons,
        "checks": checks,
        "f": {"blended": f_blend, "threshold": F_THRESHOLD,
              "branch": "LE" if f_blend <= F_THRESHOLD else "GT",
              "per_population": {p: v["f"] for p, v in
                                 tc["populations"].items()},
              "convention": tc["f_convention"]},
        "tokenizer": tc["tokenizer"],
        "corpus_sha256": tc["corpus_sha256"],
        "sample": inputs["timing_sample"],
        "model": {
            "type": "monotone-piecewise-linear s_hat(T) over measured "
                    "stratum knots; below min knot: central/hi CONSTANT, "
                    "lo linear-extrapolated floored at %.2f*s(minknot); "
                    "above max knot: FAIL-CLOSED" % FLOOR_EXTRAP_MIN_FRAC,
            "knots_raw": raw_knots,
            "knots_isotonic": [{k: v for k, v in kn.items()
                                if k != "pool"} for kn in knots],
            "isotonic_repairs": repaired,
            "se_rule": "+-%g SE band; caps tested at +SE, floors at -SE, "
                       "windows at central" % SE_MULT,
            "cont_tokens_addend": CONT_TOKENS,
        },
        "pin": inputs["pin"],
        "rate": {"usd_per_hour": rate, "source": inputs["rate_source"]},
        "projection": {
            "prefills": prefills,
            "replace_included": replace,
            "instance_hours": {"central": round(h_c, 1),
                               "hi": round(h_hi, 1), "lo": round(h_lo, 1)},
            "usd_total": {"central": round(usd_c, 2),
                          "hi": round(usd_hi, 2), "lo": round(usd_lo, 2)},
            "blended_s_per_prefill_central":
                round(h_c * 3600.0 / prefills, 2),
            "hours_by_population_central": by_pop,
            "per_average_naive_hours_RETIRED": round(naive_h, 1),
            "per_average_divergence_pct":
                round(100.0 * (h_c - naive_h) / naive_h, 2),
        },
        "thresholds": frozen,
        "semantics": "plan §7: GREEN -> construction proceeds WITHOUT "
                     "re-surfacing (standing authorization); STOP -> "
                     "MANDATORY surface to the maintainer with salvage "
                     "options; never autonomous re-freeze",
    }
    if out_path:
        Path(out_path).write_text(json.dumps(art, indent=2))
    return art


# ---------------------------------------------------------------------------
# spec ($0 control-box witness) + selftest ($0 oracle)
# ---------------------------------------------------------------------------
def cmd_spec(args):
    out = {
        "schema": SCHEMA + ":sample-spec",
        "seed": SAMPLE_SEED,
        "rule": {"quantile_edges": list(QUANTILE_EDGES),
                 "bin_alloc": list(BIN_ALLOC), "cont_tokens": CONT_TOKENS,
                 "pop_floor": POP_FLOOR, "t1_n": T1_N,
                 "f_threshold": F_THRESHOLD,
                 "se_mult": SE_MULT,
                 "floor_extrap_min_frac": FLOOR_EXTRAP_MIN_FRAC},
        "inventory": {"construction": [N_CONSTRUCTION, 1],
                      "main-tmpl": [N_TEST, M_MAIN_TMPL],
                      "main-d3": [N_TEST, M_MAIN_D3],
                      "pilot": [N_DEV, M_PILOT],
                      "guard": [N_GUARD, M_GUARD],
                      "mandatory_total": MANDATORY_PREFILLS},
        "corpus_sha256": corpus_shas(args.corpus_dir),
    }
    print(json.dumps(out, indent=2))
    return 0


def _mock_corpora(d):
    """Full frozen-count corpora with deterministic synthetic texts whose
    word lengths mimic the measured per-population distributions."""
    import io

    def words(key, mean, spread, tail_key=None, tail_words=0):
        h = int(tiehash(key)[:8], 16)
        n = max(4, mean - spread + h % (2 * spread + 1))
        if tail_key and h % 97 == 0:
            n = tail_words
        return " ".join("w%d" % ((h + i) % 511) for i in range(n))

    with open(d / "construction-manifest.jsonl", "w") as f:
        for i in range(N_CONSTRUCTION):
            f.write(json.dumps({"text": words("c%d" % i, 31, 20)}) + "\n")
    for name, n, tmean, has_d3 in (("test.jsonl", N_TEST, 123, True),
                                   ("dev.jsonl", N_DEV, 84, True),
                                   ("guard.jsonl", N_GUARD, 57, False)):
        with open(d / name, "w") as f:
            for i in range(n):
                key = "%s%d" % (name, i)
                r = {"item_id": "it-%s-%04d" % (name[:2], i),
                     "template_text": words(key, tmean, 50, key, 774)}
                if has_d3:
                    r["d3_template_text"] = r["template_text"] + " " + \
                        words(key + "k", 23, 5)
                f.write(json.dumps(r) + "\n")


def _fake_timing(sample, s_of_t, path):
    with open(path, "w") as f:
        for e in sample["entries"]:
            noise = 1.0 + ((int(tiehash("n" + e["key"])[:6], 16) % 401)
                           - 200) / 10000.0   # deterministic +-2%
            f.write(json.dumps({"sample_id": e["sample_id"],
                                "s": round(s_of_t(e["Tp"]) * noise, 3),
                                "timer_n": 1}) + "\n")


def selftest():
    import tempfile
    frozen = {"instance_hours": [260.6, 900.0], "usd_total": [73.0, 155.0],
              "rate_window": [0.0811, 0.5948], "prefills_min": 11011}
    fails = []

    def check(cond, msg):
        print("  %s %s" % ("ok:  " if cond else "FAIL:", msg))
        if not cond:
            fails.append(msg)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cd = td / "corpus"
        cd.mkdir()
        _mock_corpora(cd)
        print("== selftest: kot-f1k-bringup-gate/1 $0 oracle (MOCK tokens) ==")
        ns = argparse.Namespace(corpus_dir=str(cd), mock_f=1.45,
                                tok_wrapper=None, tokenizer=None,
                                out=str(td / "tok"))
        cmd_fcount(ns)
        cmd_fcount(argparse.Namespace(**{**vars(ns), "out": str(td / "tok2")}))
        check((td / "tok/tokens-full.jsonl").read_bytes()
              == (td / "tok2/tokens-full.jsonl").read_bytes(),
              "fcount deterministic (two runs byte-identical)")
        cmd_realize(argparse.Namespace(tokens=str(td / "tok"),
                                       out=str(td / "samp")))
        cmd_realize(argparse.Namespace(tokens=str(td / "tok"),
                                       out=str(td / "samp2")))
        s1 = (td / "samp/timing-sample.json").read_bytes()
        check(s1 == (td / "samp2/timing-sample.json").read_bytes(),
              "realize deterministic (two runs byte-identical)")
        sample = json.loads(s1)
        ent = [json.loads(l) for l in open(td / "tok/tokens-full.jsonl")]
        maxtp = max(e["T"] + CONT_TOKENS for e in ent)
        check(any(c["Tp"] == maxtp for c in sample["entries"]),
              "campaign max-T prefill is in the sample")
        pops = {p: sum(1 for c in sample["entries"] if c["pop"] == p)
                for p in POP_FLOOR}
        check(all(pops[p] >= POP_FLOOR[p] for p in POP_FLOOR),
              "population coverage floors met: %s" % pops)
        check(sample["n"] <= N_SAMPLE_MAX,
              "sample size %d <= cap %d" % (sample["n"], N_SAMPLE_MAX))

        def mk_inputs(t2path, rate=0.174):
            counts = json.loads((td / "tok/token-counts.json").read_text())
            inv_t = [[e["pop"], e["m"], e["T"] + CONT_TOKENS] for e in ent]
            return {"schema": SCHEMA + ":gate-inputs",
                    "token_counts": counts, "_allow_mock": True,
                    "timing_sample": sample,
                    "t2_pinned_runs": [json.loads(l) for l in open(t2path)],
                    "t1_unpinned_runs": [], "inventory_t": inv_t,
                    "rate_usd_per_hour": rate, "rate_source": "selftest",
                    "pin": {"pin_file_sha256": "f" * 64, "pin_gb": 40.0,
                            "regime": "pinned-bringup", "note": "mock"}}

        # case 1 GREEN: linear planted s(T) scaled to 700 h central
        mass = sum(e["m"] * (e["T"] + CONT_TOKENS) for e in ent)
        b_lin = 700.0 * 3600.0 / mass
        _fake_timing(sample, lambda t: b_lin * t, td / "t2-green.jsonl")
        art = project(mk_inputs(td / "t2-green.jsonl"), frozen)
        check(art["verdict"] == "GREEN",
              "case 1 GREEN verdict (got %s %s)" % (art["verdict"],
                                                    art["reasons"]))
        check(art["f"]["branch"] == "LE" and art["checks"]["f_le_threshold"],
              "case 1 f-branch LE at mock f=1.45")
        check(abs(art["projection"]["instance_hours"]["central"] - 700) < 25,
              "case 1 central ~700 h (got %s)"
              % art["projection"]["instance_hours"]["central"])
        # case 2 STOP long-tail: convex planted s(T) = b*T^2 scaled to 940 h
        # -> the per-AVERAGE projection FITS while the per-item one BREACHES
        mass2 = sum(e["m"] * (e["T"] + CONT_TOKENS) ** 2 for e in ent)
        b_sq = 940.0 * 3600.0 / mass2
        _fake_timing(sample, lambda t: b_sq * t * t, td / "t2-tail.jsonl")
        art2 = project(mk_inputs(td / "t2-tail.jsonl"), frozen)
        check(art2["verdict"] == "STOP",
              "case 2 STOP: convex long-tail breaches the 900 h cap")
        naive = art2["projection"]["per_average_naive_hours_RETIRED"]
        check(naive <= 900.0 <
              art2["projection"]["instance_hours"]["central"],
              "case 2 DIVERGENCE PROVEN (review finding 3): per-average "
              "%.0f h would fit, per-item %.0f h breaches"
              % (naive, art2["projection"]["instance_hours"]["central"]))
        # case 3 STOP on f > 1.60 even with a fitting ledger
        ns3 = argparse.Namespace(**{**vars(ns), "mock_f": 1.75,
                                    "out": str(td / "tok3")})
        cmd_fcount(ns3)
        in3 = mk_inputs(td / "t2-green.jsonl")
        in3["token_counts"] = json.loads(
            (td / "tok3/token-counts.json").read_text())
        # rescale planted timing to keep the ledger inside the windows at
        # the LONGER mock-f=1.75 token counts (isolates the f-branch)
        ent3 = [json.loads(l) for l in open(td / "tok3/tokens-full.jsonl")]
        in3["inventory_t"] = [[e["pop"], e["m"], e["T"] + CONT_TOKENS]
                              for e in ent3]
        mass3 = sum(e["m"] * (e["T"] + CONT_TOKENS) for e in ent3)
        # knots span mock-f=1.45 T-range; f=1.75 tokens exceed the max knot
        # -> re-realize the sample at the f=1.75 counts (rule is T-relative)
        cmd_realize(argparse.Namespace(tokens=str(td / "tok3"),
                                       out=str(td / "samp3")))
        sample3 = json.loads((td / "samp3/timing-sample.json").read_text())
        in3["timing_sample"] = sample3
        b3 = 700.0 * 3600.0 / mass3
        _fake_timing(sample3, lambda t: b3 * t, td / "t2-f175.jsonl")
        in3["t2_pinned_runs"] = [json.loads(l)
                                 for l in open(td / "t2-f175.jsonl")]
        art3 = project(in3, frozen)
        check(art3["verdict"] == "STOP" and art3["f"]["branch"] == "GT"
              and any("f " in r or "f-" in r or "blended f" in r
                      for r in art3["reasons"]),
              "case 3 STOP purely on the f>1.60 branch (reasons: %s)"
              % art3["reasons"])
        # case 4 fail-closed: campaign T above the max sampled knot
        in4 = mk_inputs(td / "t2-green.jsonl")
        in4["inventory_t"] = in4["inventory_t"] + [["main-d3", 1, maxtp * 3]]
        try:
            project(in4, frozen)
            check(False, "case 4 must fail closed above the max knot")
        except SystemExit:
            check(True, "case 4 fail-closed: T above max sampled knot dies")
        # case 5 fail-closed: MOCK tokens never license without _allow_mock
        in5 = mk_inputs(td / "t2-green.jsonl")
        del in5["_allow_mock"]
        try:
            project(in5, frozen)
            check(False, "case 5 must refuse MOCK token counts")
        except SystemExit:
            check(True, "case 5 fail-closed: MOCK tokens refused for a "
                        "real verdict")
        # case 6: collect refuses partial T2 timing
        (td / "t2-part.jsonl").write_text(
            (td / "t2-green.jsonl").read_text().splitlines(True)[0])
        try:
            cmd_collect(argparse.Namespace(
                sample=str(td / "samp/timing-sample.json"),
                tokens=str(td / "tok"), t2=str(td / "t2-part.jsonl"),
                t1=None, rate="0.174", pin_sha="", pin_gb="",
                pin_regime="pinned-bringup", out=str(td / "gi.json")))
            check(False, "case 6 must refuse partial T2 results")
        except SystemExit:
            check(True, "case 6 fail-closed: partial T2 timing refused")
    print()
    if fails:
        print("BRINGUP-GATE SELFTEST FAILED (%d)" % len(fails))
        return 1
    print("BRINGUP-GATE SELFTEST PASS (MOCK SCOPE ONLY: rule mechanics + "
          "verdict logic on synthetic corpora/timing; real T, f, s and the "
          "license verdict exist only via the VM path + f1k_gcp.py gate)")
    return 0


def main():
    ap = argparse.ArgumentParser(prog="f1k_bringup_gate.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("spec")
    p.add_argument("--corpus-dir", required=True)
    p = sub.add_parser("fcount")
    p.add_argument("--corpus-dir", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--tok-wrapper")
    p.add_argument("--tokenizer")
    p.add_argument("--mock-f", type=float, default=None)
    p = sub.add_parser("realize")
    p.add_argument("--tokens", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("pinfile")
    p.add_argument("--stats-glob", required=True)
    p.add_argument("--pin-gb", type=float, required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("collect")
    p.add_argument("--sample", required=True)
    p.add_argument("--tokens", required=True)
    p.add_argument("--t2", required=True)
    p.add_argument("--t1")
    p.add_argument("--rate", required=True)
    p.add_argument("--pin-sha", default="")
    p.add_argument("--pin-gb", default="")
    p.add_argument("--pin-regime", required=True,
                   choices=["pinned-bringup", "unpinned"])
    p.add_argument("--out", required=True)
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "selftest":
        return selftest()
    return {"spec": cmd_spec, "fcount": cmd_fcount, "realize": cmd_realize,
            "pinfile": cmd_pinfile, "collect": cmd_collect}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
```
<!-- END-ARTIFACT D1 -->

### 3.2 D2 — `poc/gcp/f1k_gcp.py` (U1 context; avoids the seq-3 lines 5/14/49/51/57)

<!-- BEGIN-ARTIFACT D2 poc/gcp/f1k_gcp.py.diff sha256=da466c986c24d3b568c2f0a1350bce778f33e4610fcb7202a42a02896496d0c8 -->
```diff
--- a/poc/gcp/f1k_gcp.py
+++ b/poc/gcp/f1k_gcp.py
@@ -6,3 +6,3 @@
 coordinator-resolved compute target (bead pzb6): a GCP **Spot** n2d-highmem-8
-(8 vCPU / 64 GB) + 3×375 GiB local SSD (1,125 GiB NVMe), zone us-central1-a.
+(8 vCPU / 64 GB) + 2×375 GiB local SSD (750 GiB NVMe), zone us-central1-a.
 It designs NOTHING and concludes NOTHING: the science (kernel, model, engine,
@@ -26,10 +26,13 @@
   python3 poc/gcp/f1k_gcp.py plan          # $0 dry-plan: pins + SPOT + window
-  python3 poc/gcp/f1k_gcp.py provision     # create the Spot VM + 3 local SSD
-  python3 poc/gcp/f1k_gcp.py push          # scp the harness + patches to the VM
-  python3 poc/gcp/f1k_gcp.py stage         # HF -> local SSD (+ GCS mirror)
-  python3 poc/gcp/f1k_gcp.py build         # clone+patch+build (KaE + dump)
-  python3 poc/gcp/f1k_gcp.py bringup       # KaE inertness + dump 3-precond gate
-  python3 poc/gcp/f1k_gcp.py affordability # measure rate+s/prefill -> gate
+  python3 poc/gcp/f1k_gcp.py provision     # create the Spot VM + 2 local SSD
+  python3 poc/gcp/f1k_gcp.py gate          # bring-up gate VERDICT (GREEN is
+                                           #   the ONLY construction license;
+                                           #   --selftest = $0 mock oracle)
+  python3 poc/gcp/f1k_gcp.py affordability # SECONDARY synthetic diagnostic
+                                           #   ONLY — licenses NOTHING
   python3 poc/gcp/f1k_gcp.py status        # poll VM state + GCS heartbeat
   python3 poc/gcp/f1k_gcp.py teardown      # delete VM + disks (nothing bills idle)
+(stage/build/KaE+dump bring-up run ON the VM via f1k_worker.sh — they were
+never control-box entrypoints; the retired push/stage/build/bringup docstring
+advertisement was CONSTRUCTION-PLAN v3 GAP-4.)
 Nothing spends until an explicit provisioning entrypoint is invoked; `plan` is
@@ -400,7 +403,9 @@
 def cmd_affordability() -> None:
-    """The addendum-(7) bring-up affordability gate, made executable. Consumes
-    the MEASURED spot rate and MEASURED blended s/prefill, projects the frozen
-    ledger for the mandatory (and +REPLACE) campaign, and returns GO only if it
-    lands inside the frozen window (fail-closed on both the FLOOR and the CAP).
-    A GO — and ONLY a GO — licenses construction spend.
+    """SECONDARY DIAGNOSTIC ONLY (F1K-BRINGUP-GATE-FIX.md v1, GAP-1): projects
+    the frozen ledger from ONE blended s/prefill (historically the synthetic
+    functional-gate mix). It LICENSES NOTHING — the v2 review (finding 4)
+    showed the synthetic blend mis-prices the gate in both directions. The
+    construction license is `f1k_gcp.py gate` (kot-f1k-bringup-gate/1:
+    real-corpus stratified sample + measured f + PER-ITEM token-aware
+    projection) and ONLY that.
 
@@ -428,4 +433,5 @@
             "retry. Do NOT spend construction." % "; ".join(proj["reasons"]))
-    print("\nAFFORDABILITY GO: projected instance_hours %.1f h, usd_total $%.2f "
-          "inside the frozen window. Construction spend is licensed."
+    print("\nAFFORDABILITY DIAGNOSTIC GO: projected instance_hours %.1f h, "
+          "usd_total $%.2f inside the frozen window — SECONDARY diagnostic "
+          "only; the construction license is `f1k_gcp.py gate` (GREEN)."
           % (proj["projected_instance_hours"], proj["projected_usd_total"]))
@@ -433,2 +439,64 @@
 
+def cmd_gate() -> None:
+    """The FIXED bring-up affordability gate verdict (kot-f1k-bringup-gate/1;
+    poc/gcp/F1K-BRINGUP-GATE-FIX.md v1, closing CONSTRUCTION-PLAN v3 §4.2
+    GAP-1/2/3). Consumes the on-VM gate-inputs.json (f1k_worker.sh step 5/5:
+    real-corpus stratified per-item timing + measured f + per-item token
+    counts), re-verifies the launch pins + corpus bytes, projects the frozen
+    ledger PER-ITEM via f1k_bringup_gate.project, and emits bringup-gate.json
+    with the MECHANICAL plan-§7 verdict:
+      GREEN -> construction proceeds WITHOUT re-surfacing (standing auth);
+      STOP  -> exit 2 ERR_F1K_BRINGUP_GATE, MANDATORY maintainer surface.
+
+    usage: f1k_gcp.py gate --inputs <gate-inputs.json> [--out <path>] [--replace]
+           f1k_gcp.py gate --selftest        # $0 mock oracle, no VM"""
+    sys.path.insert(0, str(HERE))
+    import f1k_bringup_gate as bg
+    if "--selftest" in sys.argv[2:]:
+        sys.exit(bg.selftest())
+    import argparse
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--inputs", required=True)
+    ap.add_argument("--out", default=str(HERE / "bringup-gate.json"))
+    ap.add_argument("--replace", action="store_true")
+    args = ap.parse_args(sys.argv[2:])
+    verify_pins()
+    _gate()
+    frozen = {"instance_hours": [INSTANCE_HOURS_MIN, WALL_CLOCK_CAP_HOURS],
+              "usd_total": [USD_TOTAL_MIN, USD_CAP],
+              "rate_window": [RATE_WINDOW[0], RATE_WINDOW[1]],
+              "prefills_min": PREFILLS_MANDATORY_MIN}
+    inputs = json.loads(Path(args.inputs).read_text(encoding="utf-8"))
+    # corpus-drift check: the VM must have tokenized the SAME bytes this repo
+    # pins (construction-manifest via PINS; eval items are covered by the
+    # frozen record's f1k-eval-v1 corpus digest)
+    items = REPO / "data" / "f1k-eval-v1" / "items"
+    local = {"construction-manifest.jsonl":
+             sha256_file(PIN_PATHS["construction-manifest.jsonl"]),
+             "test.jsonl": sha256_file(items / "test.jsonl"),
+             "dev.jsonl": sha256_file(items / "dev.jsonl"),
+             "guard.jsonl": sha256_file(items / "guard.jsonl")}
+    got = inputs["token_counts"]["corpus_sha256"]
+    for name, want in local.items():
+        if got.get(name) != want:
+            die("F1K_GATE_CORPUS_DRIFT", "%s sha on the VM %s != repo %s"
+                % (name, got.get(name), want))
+    art = bg.project(inputs, frozen, replace=args.replace, out_path=args.out)
+    print(json.dumps(art, indent=2))
+    if art["verdict"] != "GREEN":
+        die("F1K_BRINGUP_GATE",
+            "STOP: %s. MANDATORY maintainer surface with salvage options "
+            "(plan §7.3): (a) the <=$300 contingent re-freeze [maintainer "
+            "decision, never autonomous]; (b) SSR6 degradation within the "
+            "original windows; (c) stop-and-hold. Do NOT spend construction."
+            % "; ".join(art["reasons"]))
+    print("\nBRING-UP GATE GREEN (artifact: %s): measured f %.4f <= 1.60 AND "
+          "the PER-ITEM projected ledger (%.1f h central / $%.2f) lands "
+          "inside the frozen windows. Construction proceeds under the plan "
+          "§7 standing authorization (report-after, no re-surface)."
+          % (args.out, art["f"]["blended"],
+             art["projection"]["instance_hours"]["central"],
+             art["projection"]["usd_total"]["central"]))
+
+
 ENTRY = {
@@ -436,2 +504,3 @@
     "teardown": cmd_teardown, "affordability": cmd_affordability,
+    "gate": cmd_gate,
 }
```
<!-- END-ARTIFACT D2 -->

### 3.3 D3 — `poc/gcp/f1k_worker.sh`

<!-- BEGIN-ARTIFACT D3 poc/gcp/f1k_worker.sh.diff sha256=2fa9992383d1176543557ecdc8cf353eac3ec735f9b3aee7a0c7ef2ff9bf102a -->
```diff
--- a/poc/gcp/f1k_worker.sh
+++ b/poc/gcp/f1k_worker.sh
@@ -29,9 +29,13 @@
 #            finalizes the independent comparison ON-BOX (its correctness can
 #            not be validated blind, so it is a runner-confirmed PASS, not an
 #            autonomous one — see README "Dump bring-up gate").
-#   5. AFFORDABILITY MICRO-BENCHMARK — time real scoring prefills -> blended
-#      s/prefill; combined with the RECORDED spot rate -> the frozen-window
-#      projection gate (f1k_gcp.py affordability). Writes addendum-7 inputs.
+#   5. REAL-CORPUS BRING-UP GATE INPUTS (F1K-BRINGUP-GATE-FIX.md v1, closing
+#      GAP-1/2/3): tokenize the frozen corpora with the staged GLM-5.2
+#      tokenizer (measured f + per-item T), realize the frozen stratified
+#      timing sample, time it per-item (unpinned T1 -> bring-up pin file;
+#      pinned T2), and write gate-inputs.json. The GREEN/STOP verdict is the
+#      control box's `f1k_gcp.py gate` (kot-f1k-bringup-gate/1); the
+#      synthetic functional-gate blend stays a SECONDARY diagnostic ONLY.
 #      Then STOP + heartbeat DONE.
 #
 # Heartbeat + all artifacts are mirrored to GCS ($BUCKET/f1k/bringup) so a spot
@@ -315,30 +319,118 @@
 cat "$GATE/affordability-measured.json"
 hb "functional-inertness-PASS"
 
-step "5/5 affordability micro-benchmark (blended s/prefill) -> frozen-window gate"
-# The blended s/prefill is now MEASURED as a side-benefit of the functional gate
-# above (func-patched-1 run_score timer, model-load excluded) -> affordability-
-# measured.json.  The frozen-window PROJECTION + GO/STOP is the runner's on-box
-# call via the control-box driver (fail-closed on both the $73 floor and $155
-# cap); construction is NOT spent autonomously.
-MEAS_SPP=$(python3 -c "import json;v=json.load(open('$GATE/affordability-measured.json')).get('blended_s_per_prefill_measured');print(v if v is not None else '')" 2>/dev/null || echo "")
-echo "RUNNER-RUN-REQUIRED" > "$GATE/affordability.status"
-cat > "$GATE/affordability-README.txt" <<EOF
-MEASURED blended s/prefill (functional-gate side-benefit, model-load excluded):
-  ${MEAS_SPP:-<none: engine emitted no scoring timer; re-measure on-box>}
-  (full record: $GATE/affordability-measured.json)
-Project the frozen 19964-prefill ledger + decide GO/STOP on the control box:
-  python3 poc/gcp/f1k_gcp.py affordability --rate $SPOT_RATE --s-per-prefill ${MEAS_SPP:-<MEAN>}
-which FAILS CLOSED if the projection lands outside instance_hours [260.6,900] h
-or usd_total [\$73,\$155] (the FLOOR binds below \$0.28/h).  A GO here (and ONLY
-a GO) licenses construction spend — the coordinator's supervised call.
+step "5/5 REAL-CORPUS bring-up gate inputs (GAP-1/2/3 fix) -> gate-inputs.json"
+# The synthetic functional-gate blend above (affordability-measured.json) is a
+# SECONDARY diagnostic ONLY (v2 review finding 4: it mis-prices the gate in
+# both directions). The construction-LICENSE inputs below are REAL-corpus:
+# measured f (GAP-2), the frozen deterministic stratified per-item timing
+# sample (GAP-1), per-item token counts for the token-aware projection
+# (GAP-3). Rule + estimator: poc/gcp/F1K-BRINGUP-GATE-FIX.md v1 (frozen).
+GATEPY="$HERE/f1k_bringup_gate.py"
+[ -f "$GATEPY" ] || die "f1k_bringup_gate.py missing from the pushed poc/gcp dir"
+CORPUS="$HERE/gate-corpus"     # pushed by the coordinator (poc/gcp/README.md step 2)
+for f in construction-manifest.jsonl test.jsonl dev.jsonl guard.jsonl; do
+  [ -f "$CORPUS/$f" ] || die "gate corpus file missing: $CORPUS/$f (push step)"
+done
+TOK_WRAPPER="${KOT_F1K_TOK_WRAPPER:-$(find "$HOME_DIR" -maxdepth 4 -name tok_glm52.py 2>/dev/null | head -1)}"
+[ -n "$TOK_WRAPPER" ] || die "tok_glm52.py not found (push f1k-harness or set KOT_F1K_TOK_WRAPPER)"
+TOKJSON="$(find "$ESTATE_DIR" -maxdepth 2 -name tokenizer.json | head -1)"
+[ -n "$TOKJSON" ] || die "tokenizer.json not found in estate $ESTATE_DIR (ASM-1971 bring-up pin)"
+pip3 -q install tokenizers 2>/dev/null || true
+python3 "$GATEPY" fcount --corpus-dir "$CORPUS" --tok-wrapper "$TOK_WRAPPER" \
+  --tokenizer "$TOKJSON" --out "$GATE/gate-tokens" || die "gate fcount FAILED"
+python3 "$GATEPY" realize --tokens "$GATE/gate-tokens" --out "$GATE/gate-sample" \
+  || die "gate realize FAILED"
+hb "gate-tokenized"
+
+# PIN_GB fixed at bring-up from MEASURED free-RAM headroom (plan §5 semantics;
+# recording + truthful-attestation mechanics: F1K-PIN-FILE-FIX.md v2 — this
+# step only FIXES the number and derives the BRING-UP pin; it never fakes one).
+MEM_AVAIL_GB=$(awk '/MemAvailable/ {printf "%d", $2/1048576}' /proc/meminfo)
+PIN_GB="${KOT_F1K_PIN_GB:-$(( MEM_AVAIL_GB - 8 ))}"
+[ "$PIN_GB" -gt 50 ] && PIN_GB=50
+[ "$PIN_GB" -ge 24 ] || die "PIN_GB headroom $PIN_GB GB < 24 (MemAvailable ${MEM_AVAIL_GB} GB) — outside the M4-measured 40-50 GB band's floor; STOP"
+
+GATE_MAX_S="${KOT_F1K_GATE_MAX_S:-10800}"   # fail-closed timing budget (3 h)
+GATE_T0=$(date +%s)
+run_gate_sample() {   # $1=sample_id  $2=results.jsonl  $3.. = extra env pairs
+  local sid="$1"; local res="$2"; shift 2
+  local man="$GATE/gate-sample/sample-$sid.score"
+  [ $(( $(date +%s) - GATE_T0 )) -lt "$GATE_MAX_S" ] \
+    || die "gate timing exceeded KOT_F1K_GATE_MAX_S=$GATE_MAX_S s (fail-closed: no silent truncation — raise the budget or STOP)"
+  env -u KAE -u KAE_G -u KAE_SCORE -u KAE_DUMP -u KAE_CARRIER -u KAE_SPANS \
+      -u KAE_MODE -u KAE_SEED -u KAE_DUMP_LAYERS \
+      SNAP="$ESTATE_DIR" SCORE="$man" \
+      OMP_NUM_THREADS="$FUNC_OMP" OMP_DYNAMIC=FALSE OMP_PROC_BIND=close \
+      OMP_WAIT_POLICY=active COLI_OMP_TUNED=1 "$@" \
+      "$SCORE_ENGINE" 64 4 8 > "$GATE/gate-run-$sid.out" 2> "$GATE/gate-run-$sid.err" \
+    || die "gate timing run $sid FAILED (see gate-run-$sid.err)"
+  local timer n s pin_ev
+  timer=$(grep -oE '\[score [0-9]+ req \| [0-9.]+s' "$GATE/gate-run-$sid.err" | tail -1 || true)
+  n=$(echo "$timer" | grep -oE '[0-9]+ req' | grep -oE '[0-9]+' || true)
+  s=$(echo "$timer" | grep -oE '\| [0-9.]+s' | grep -oE '[0-9.]+' || true)
+  { [ -n "$s" ] && [ "${n:-0}" -ge 1 ]; } || die "gate run $sid: engine emitted no scoring timer (see gate-run-$sid.err)"
+  pin_ev=$(grep -iE 'pin' "$GATE/gate-run-$sid.err" | head -3 | tr -d '"' | tr '\n' ';' || true)
+  echo "{\"sample_id\":\"$sid\",\"s\":$s,\"timer_n\":$n,\"stderr_pin_evidence\":\"$pin_ev\"}" >> "$res"
+}
+
+# T1: UNPINNED runs over the t1 subset with engine usage stats ON (STATS knob
+# semantics are fetch-grade [ASM-1971] — the runner re-verifies knob + harvest
+# location at the (7) semantic gate; KOT_F1K_STATS_HARVEST overrides the glob).
+T1_IDS=$(python3 -c "import json;print(' '.join(json.load(open('$GATE/gate-sample/timing-sample.json'))['t1_sample_ids']))")
+T1_CWD="$GATE/t1-cwd"; mkdir -p "$T1_CWD"
+: > "$GATE/t1-results.jsonl"
+for sid in $T1_IDS; do
+  ( cd "$T1_CWD" && run_gate_sample "$sid" "$GATE/t1-results.jsonl" STATS=1 )
+done
+hb "gate-t1-done"
+
+# bring-up pin file at PIN_GB from the T1 usage stats; if underivable, T2 runs
+# UNPINNED (conservative: the ASM-2205 1.20x lever is priced OUT, never faked).
+PIN_REGIME="pinned-bringup"; PIN_FILE="$GATE/pin_bringup.stats"; PIN_SHA=""
+if python3 "$GATEPY" pinfile --stats-glob "${KOT_F1K_STATS_HARVEST:-$T1_CWD/*}" \
+     --pin-gb "$PIN_GB" --out "$PIN_FILE" > "$GATE/pinfile.json" 2>&1; then
+  PIN_SHA=$(sha256sum "$PIN_FILE" | awk '{print $1}')
+else
+  PIN_REGIME="unpinned"; PIN_FILE=""
+  echo "WARN: bring-up pin underivable (see pinfile.json) -> T2 UNPINNED (conservative, recorded)"
+fi
+
+# T2: the LICENSE timing — every sample text, per-item engine timer (model
+# load excluded), pinned when the bring-up pin derived (evidence per run).
+: > "$GATE/t2-results.jsonl"
+ALL_IDS=$(python3 -c "import json;print(' '.join(e['sample_id'] for e in json.load(open('$GATE/gate-sample/timing-sample.json'))['entries']))")
+for sid in $ALL_IDS; do
+  if [ "$PIN_REGIME" = "pinned-bringup" ]; then
+    run_gate_sample "$sid" "$GATE/t2-results.jsonl" PIN="$PIN_FILE" PIN_GB="$PIN_GB"
+  else
+    run_gate_sample "$sid" "$GATE/t2-results.jsonl"
+  fi
+done
+hb "gate-t2-done"
+
+python3 "$GATEPY" collect --sample "$GATE/gate-sample/timing-sample.json" \
+  --tokens "$GATE/gate-tokens" --t2 "$GATE/t2-results.jsonl" \
+  --t1 "$GATE/t1-results.jsonl" --rate "$SPOT_RATE" \
+  --pin-sha "$PIN_SHA" --pin-gb "$PIN_GB" --pin-regime "$PIN_REGIME" \
+  --out "$GATE/gate-inputs.json" || die "gate collect FAILED"
+echo "CONTROL-BOX-VERDICT-REQUIRED" > "$GATE/bringup-gate.status"
+cat > "$GATE/bringup-gate-README.txt" <<EOF
+REAL-CORPUS gate inputs ready: $GATE/gate-inputs.json (mirrored to GCS).
+Pull it and run the MECHANICAL verdict on the control box:
+  python3 poc/gcp/f1k_gcp.py gate --inputs <pulled gate-inputs.json>
+GREEN -> construction proceeds without re-surfacing (plan §7 standing
+authorization). STOP (exit 2 ERR_F1K_BRINGUP_GATE) -> MANDATORY maintainer
+surface. The synthetic blend (affordability-measured.json) is a SECONDARY
+diagnostic; \`f1k_gcp.py affordability\` licenses NOTHING.
 EOF
-cat "$GATE/affordability-README.txt"
-hb "affordability-measured-runner-projects"
+cat "$GATE/bringup-gate-README.txt"
+hb "gate-inputs-ready"
 
 step "DONE (bring-up scaffolded; STOP before construction spend)"
 echo "Bring-up artifacts in $GATE/ (mirrored to $BUCKET/f1k/bringup/)."
-echo "NEXT (gated): finalize dump preconditions (a)+(c) + the affordability"
-echo "micro-benchmark on-box; a GO affordability verdict licenses construction."
+echo "NEXT (gated): finalize dump preconditions (a)+(c) on-box; pull"
+echo "gate-inputs.json and run \`f1k_gcp.py gate\` on the control box — a"
+echo "GREEN bringup-gate.json verdict (and ONLY that) licenses construction."
 gsutil -q -m cp -r "$GATE" "$BUCKET/f1k/bringup/" || true
 hb "DONE-bringup-scaffold"
```
<!-- END-ARTIFACT D3 -->

### 3.4 D4 — `poc/gcp/README.md`

<!-- BEGIN-ARTIFACT D4 poc/gcp/README.md.diff sha256=fda84a6e7c83b4961d80ed72454c77287bf393006308a088868940e83443898d -->
```diff
--- a/poc/gcp/README.md
+++ b/poc/gcp/README.md
@@ -9,7 +9,7 @@
 > down — from the frozen RunSpec, fail-closed on any pin mismatch.
 >
 > Compute target (bead **pzb6** resolution): GCP **Spot** `n2d-highmem-8`
-> (8 vCPU / 64 GB) + **3×375 GiB local SSD** (1,125 GiB NVMe), zone
+> (8 vCPU / 64 GB) + **2×375 GiB local SSD** (750 GiB NVMe), zone
 > `us-central1-a`. **`--provisioning-model=SPOT` is MANDATORY** — on-demand
 > (~$0.579/h) busts the $155 ceiling and fails the pinned analysis.
 
@@ -54,9 +54,10 @@
 
 | File | What it is |
 |---|---|
-| `f1k_gcp.py` | Orchestrator (runs on the control box): `plan` ($0 dry-plan: pins + reuse-gate + SPOT/disk/window asserts), `provision` (Spot VM + 3 local SSD), `status`, `teardown`, `affordability` (measured rate + s/prefill → frozen-window GO/SALVAGE-STOP). |
+| `f1k_gcp.py` | Orchestrator (runs on the control box): `plan` ($0 dry-plan: pins + reuse-gate + SPOT/disk/window asserts), `provision` (Spot VM + 2 local SSD), `status`, `teardown`, `gate` (**the bring-up gate verdict — kot-f1k-bringup-gate/1; GREEN is the ONLY construction license**; `--selftest` = $0 mock oracle), `affordability` (one-blended-s/prefill projection — **SECONDARY diagnostic ONLY, licenses nothing**). |
+| `f1k_bringup_gate.py` | The FIXED bring-up gate machinery (`F1K-BRINGUP-GATE-FIX.md` v1, GAP-1/2/3): frozen deterministic stratified real-corpus sampling rule, full-corpus tokenization (measured f, per-item T), bring-up pin-file derivation, per-item token-aware ledger projection + GREEN/STOP artifact; `selftest` = $0 end-to-end mock oracle. |
 | `bringup_gcp.sh` | KaE bring-up on the VM: colibri@`a78a06fc` + KaE patch (`11f8b458`), build, 44/44 `test_kae`; objdump patch-shape checks (clone-aware, reference + native flags) are **ADVISORY-ONLY on the VM** (bead f2uk / ASM-2503: gcc-version-brittle even at `-O2 -march=x86-64-v3`; fail-closed objdump lives off-box on the gcc-11.5 basis; the frozen `bringup.sh` is untouched). The AUTHORITATIVE inertness proof is the functional KAE-unset byte-identity gate in `f1k_worker.sh`. |
-| `f1k_worker.sh` | On-VM autonomous worker: STAGE (GCS mirror → else HF → NVMe, weight-hash pin) → BUILD scoring + construction engines → KaE bring-up → dump bring-up gate (b) → scaffolds (a)+(c) + the affordability micro-benchmark → **STOP before construction spend**. Heartbeat + artifacts to GCS; idempotent (spot preemption re-runs, restages from GCS). |
+| `f1k_worker.sh` | On-VM autonomous worker: STAGE (GCS mirror → else HF → NVMe, weight-hash pin) → BUILD scoring + construction engines → KaE bring-up → dump bring-up gate (b) → scaffolds (a)+(c) → **REAL-CORPUS gate inputs** (tokenize → measured f + per-item T; frozen stratified per-item timing, T1 unpinned → bring-up pin → T2 pinned; `gate-inputs.json`) → **STOP before construction spend**. Heartbeat + artifacts to GCS; idempotent (spot preemption re-runs, restages from GCS). |
 
 ## Run sequence (frozen §R-REV4.2 ordering; each paid step gated)
 
@@ -64,7 +65,10 @@
 1. `provision` → **record the ACTUAL assigned spot $/h** (load-bearing for the
    affordability gate). Set `KOT_F1K_BUCKET=gs://…` (same-region estate mirror),
    `COLIBRI_GIT_URL` (coordinator-supplied), `KOT_F1K_SPOT_RATE=<measured>`.
-2. RAID0 + mount the 3 local SSD at `/mnt/nvme`; scp `poc/gcp/`,
+2. RAID0 + mount the 2 local SSD at `/mnt/nvme`; copy the four frozen gate
+   corpora (`data/f1k-carriers-v1/generator/construction-manifest.jsonl` +
+   `data/f1k-eval-v1/items/{test,dev,guard}.jsonl`) into `poc/gcp/gate-corpus/`;
+   scp `poc/gcp/` (incl. `f1k_bringup_gate.py` + `gate-corpus/`),
    `poc/glm52-probe/f1k-harness/`, `poc/glm52-probe/kae-patch-draft/`,
    `analysis/f1k.py` to the VM; launch `f1k_worker.sh` detached (systemd/nohup).
 3. Worker STAGE + BUILD + KaE bring-up + **dump bring-up gate**:
@@ -76,12 +80,17 @@
      confirms ON-BOX** (a separate capture path, not `kae_dump.h`, cell-for-cell
      equal to the engine dump). Its correctness cannot be validated blind, so
      it is a runner-confirmed PASS. ANY precondition failure → SALVAGE+STOP.
-4. **Affordability micro-benchmark**: ≥20 real `KAE_SCORE` prefills spanning
-   short (b0) + long (d3-text) arms → mean blended s/prefill;
-   `f1k_gcp.py affordability --rate <measured> --s-per-prefill <mean>` — **GO
-   (exit 0) is the ONLY license for construction spend.**
+4. **Bring-up affordability gate** (`F1K-BRINGUP-GATE-FIX.md` v1): the worker
+   tokenizes the frozen corpora (measured **f** + per-item T), times the frozen
+   stratified REAL-corpus sample per-item (T1 unpinned → bring-up pin at
+   measured PIN_GB → T2 pinned), and writes `gate-inputs.json`; then on the
+   control box `f1k_gcp.py gate --inputs <pulled gate-inputs.json>` — **GREEN
+   (exit 0) is the ONLY license for construction spend**; STOP = mandatory
+   maintainer surface (plan §7). The synthetic blend +
+   `f1k_gcp.py affordability` remain a SECONDARY diagnostic, licensing nothing.
 5. **Construction** (gated on 3+4): `build_carriers.py construct --mode real
-   --layers 3,…,78` with the three provenance shas **and their artifacts**
+   --layers 3,…,77` (the landed ASM-2504 DRAFT=0 geometry, 75 layers) with the
+   three provenance shas **and their artifacts**
    (`--tokenizer-sha/-artifact`, `--engine-weights-sha/-artifact`,
    `--dump-patch-sha/-artifact`), 4,608 passes EXACT; `verify --expect-mode
    real` (full cell-by-cell re-derivation, the #46 guarantee); commit the
```
<!-- END-ARTIFACT D4 -->

## 4. $0 verification — what I ran this pass, and the coordinator's runbook

### 4.1 Bench evidence [MEASURED, /tmp bench this pass — no repo file touched]

All of the following was executed on a bench copy (`/tmp/gatefix`) of the CURRENT repo bytes:

1. `python3 -m py_compile` on the patched `f1k_gcp.py` + D1; `bash -n` on the patched worker — clean.
2. **$0 oracle:** `python3 poc/gcp/f1k_gcp.py gate --selftest` (through the new entrypoint, from
   the applied tree) → **14/14 checks PASS**, including:
   - fcount + realize deterministic (two runs byte-identical each);
   - campaign max-T prefill forced into the sample; population floors met; N ≤ 34;
   - case 1 **GREEN** (planted linear s(T) scaled to 700 h central; f=1.45 → branch LE);
   - case 2 **STOP long-tail with the finding-3 divergence PROVEN**: planted convex s(T); the
     RETIRED per-average projection says 620 h (fits) while the per-item projection says 969 h
     (breaches the 900 h cap) — the exact failure mode the v2 review flagged, now caught;
   - case 3 **STOP purely on the f-branch** (mock f=1.75, ledger deliberately inside windows);
   - case 4 fail-closed above the max knot; case 5 MOCK tokens refused for a real verdict;
     case 6 partial T2 timing refused.
   Both f-branch sides are exercised (case 1 LE, case 3 GT).
3. **Diff application:** all three diffs `git apply --check` + apply clean against (a) pristine
   current bytes and (b) a simulated post-seq-3 tree (`f1k_gcp.py` lines 5/14/49/51/57 and the
   README hash echoes rewritten to dummy new values); the applied results are byte-identical to
   the bench-edited files the selftest ran from.
4. **Real-corpus realization:** fcount+realize against the ACTUAL four frozen corpus files with
   mock token counts (f=1.45): N=30, bins [18,62,80,111,212,455,1174], all populations covered
   (§2.3), rough cost $1.19 (§2.8).

### 4.2 Coordinator runbook **[SUPERSEDED by §B.9 — this D1–D4-only sequence and its 14/14 expectation are the finding-8 stale chain; do not lift]**

```bash
cd /home/ec2-user/css/kernel/kernel-of-truth
M=poc/gcp/F1K-BRINGUP-GATE-FIX.md
# extract + verify each artifact (Dn in D1..D4; strips the fence lines):
for N in D1 D2 D3 D4; do
  awk -v n="$N" '$0 ~ ("^<!-- BEGIN-ARTIFACT " n " ") {f=1; next} \
      $0 ~ ("^<!-- END-ARTIFACT " n " -->") {f=0} f' "$M" \
    | sed '1d;$d' > /tmp/$N.out
done
sha256sum /tmp/D1.out   # 4cb3c858d2da63da9f6c556b0b571b15491b692b52ae1433e43dca54ec1f7b7a
sha256sum /tmp/D2.out   # da466c986c24d3b568c2f0a1350bce778f33e4610fcb7202a42a02896496d0c8
sha256sum /tmp/D3.out   # 2fa9992383d1176543557ecdc8cf353eac3ec735f9b3aee7a0c7ef2ff9bf102a
sha256sum /tmp/D4.out   # fda84a6e7c83b4961d80ed72454c77287bf393006308a088868940e83443898d
# AFTER the PIN-fix seq-3 landing commit, on a clean tree:
cp /tmp/D1.out poc/gcp/f1k_bringup_gate.py && chmod 644 poc/gcp/f1k_bringup_gate.py
git apply /tmp/D2.out && git apply /tmp/D3.out && git apply /tmp/D4.out
bash -n poc/gcp/f1k_worker.sh && python3 -m py_compile poc/gcp/f1k_gcp.py poc/gcp/f1k_bringup_gate.py
python3 poc/gcp/f1k_gcp.py gate --selftest        # expect: 14 ok lines + SELFTEST PASS, exit 0
python3 poc/gcp/f1k_bringup_gate.py spec --corpus-dir <dir with the 4 frozen files>  # rule witness
python3 poc/gcp/f1k_gcp.py plan                   # regression: DRY-PLAN OK unchanged
# land as ONE plain-infra commit (this memo + the four files + ASM-2514, §5.2); registry-check green.
```

Acceptance gate for the landing (mirrors the seq-2/seq-3 discipline): review green → apply →
`gate --selftest` 14/14 → `plan` green → one commit (registering ASM-2514 in the same commit) →
`tools/registry/registry-check.py` green (nothing frozen is touched, so this is a no-drift check).

## 5. Freeze governance

### 5.1 What is frozen by this memo (review finding 5 discharged)

The v2 review required the fixed projection model to be "formally review-gated and frozen before
spend." This memo IS that formalization: §2.2 (inventory + multiplicities), §2.3 (sampling rule +
seed + constants), §2.5 (f convention + threshold wiring), §2.6 (estimator, SE rule, verdict
rule), §2.7 (artifact schema) are frozen as ~~**kot-f1k-bringup-gate/1**~~ **[SUPERSEDED
D14/ASM-2517, bracket added REV-F per round-5 finding 4: frozen as `kot-f1k-bringup-gate/2`
(the `/2` schema + REQUIRED `model_bundle` binding; every consumer refuses non-`/2` — §2.7's
bracket); the live docstring echo of the old id is killed by D25]** at the landing commit;
the code in D1 implements them and the artifact prints them. Changing ANY of these after landing
is a new review-gated revision of this memo (v2), never an informal override. The frozen
scientific record (`f1k.json` 01cf2b17→seq-3 successor) is untouched: windows, caps, floors,
prefill counts, seeds, endpoints all enter as INPUTS, byte-identical.

### 5.2 ASM-2514 registration text (register-at-commit, WITH the landing commit)

Next free id [MEASURED this pass: assumptions.jsonl tail = ASM-2512; ASM-2513 is reserved by the
PIN-fix seq-3 memo and absent from the file, as is 2514]:

```json
{"id": "ASM-2514", "tag": "STIPULATED", "load_bearing": true, "claim": "F1-K BRING-UP AFFORDABILITY GATE kot-f1k-bringup-gate/1 (closes F1K-CONSTRUCTION-PLAN.md v3 SS4.2 GAP-1/2/3; discharges the GPT-5.6 v2 review findings 3/4/5 requirement that the projection model be review-gated + frozen before spend): the ONLY construction license for the F1-K campaign is the mechanical GREEN verdict of poc/gcp/f1k_gcp.py `gate`, computed from (a) a DETERMINISTIC seeded stratified timing sample of the REAL frozen corpora (SAMPLE_SEED 20260718 tie-break-only; prefill-mass-weighted T quantile bins (0,.2,.4,.6,.8,.95,1) with per-bin picks (4,4,4,4,4,6); the campaign max-T prefill force-included; population floors >=2 over {construction, main-tmpl, main-d3, pilot, guard}; N<=34 hard cap; per-item run_score timing on the engine's own scoring timer, T1 unpinned x8 with ONE STATS=<per-item file> per run -> EXPLICIT-manifest fail-closed merge (sum per (layer,expert), per-file sha provenance) -> bring-up pin file at measured PIN_GB in [24,50] -> T2 pinned with per-run engagement evidence; an underivable pin is a fail-closed STOP - NO unpinned fallback [REV-B amendment]), (b) the words->tokens factor f MEASURED on the FULL frozen corpora with the sha-derived staged GLM-5.2 tokenizer via the pinned kot-f1k-tok/1 wrapper (whitespace-word convention; blended f prefill-weighted over the frozen 19,964 inventory: construction 4,608x1 + test 1,573x(7 template + 1 d3) + dev 96x22 [uniform envelope allocation, +-4% disclosed] + guard 60x11 [envelope bound]), and (c) a PER-ITEM token-aware projection sum(m_i*s_hat(T_i+8)) under the FROZEN model: monotone piecewise-linear s_hat over per-stratum knots, weighted-PAVA isotonic repair (recorded), +-1SE band (caps tested at +SE, floors at -SE with downward extrapolation floored at 0.35*s(minknot), windows at central; singleton knots borrow the worst stratum SE), extrapolation above the max sampled knot FAIL-CLOSED. VERDICT RULE (mechanical, = plan SS7/ASM-2497v2): GREEN iff rate in [0.0811,0.5948] AND blended f <= 1.60 AND central hours in [260.6,900] AND central usd in [73,155] AND +SE <= caps AND -SE >= floors AND prefills >= 11,011 AND tokenizer REAL AND pin regime pinned-bringup (unpinned REFUSED) AND per-T2-run pin-ENGAGEMENT evidence for the bound sha/PIN_GB (landed ASM-2513 grammar) AND (per ASM-2515) reserve-inclusive caps + dump conjuncts; GREEN -> construction proceeds WITHOUT re-surfacing (standing authorization, report-after); anything else -> exit-2 ERR_F1K_BRINGUP_GATE MANDATORY maintainer surface (the <=$300 contingent re-freeze is a maintainer decision, never autonomous). The synthetic 10xT96/10xT384 functional-gate blend and f1k_gcp.py `affordability` are SECONDARY DIAGNOSTICS licensing nothing. The per-average projection is RETIRED as a license input and printed only as an audit comparison. Every threshold, knot, repair, and the full model block are printed into bringup-gate.json (auditable). SCOPE: gate/licensing layer only - no frozen-record surface changes (f1k_gcp.py/f1k_worker.sh/f1k_bringup_gate.py are not sha-pinned anywhere [MEASURED: zero rows in f1k.json/frozen-index; harness_manifest pins only build_carriers.py a92be3e4 + kae-add-path.patch 11f8b458]); windows/caps/floors/seeds/endpoints enter as byte-identical inputs. The driver-side addendum-(7) per-item fix (GAP-3b) lands IN THE SAME COMMIT (REV-B D13: Add7Model consumes THIS frozen model's knots re-levelled by realized pilot kappa in [0.5,2.0], reserve-inclusive at central AND +1SE - ONE projection model at both seams; SS5.3's separate-landing text is superseded). Registered WITH the landing commit of F1K-BRINGUP-GATE-FIX.md REV-B (D1-D13 applied on the LANDED post-seq-3 tree 2574c82b; $0 selftest oracle 28/28 incl. the finding-3 divergence proof, both f-branches, the REV-B merge/manifest/engagement/regime/checkpoint cases, and the fail-closed probes; driver $0 --mock green end-to-end).", "rationale": "The v2 review (VERDICT findings 3/4) proved the pre-fix gate both mis-priced (synthetic mix self-STOPs) and under-protected (single-average projection approves over-budget long tails), and finding 5 required the fixed model to be formally frozen before spend. Freezing the sampling rule, measured-f convention, and per-item estimator makes the SS7 go/no-go mechanical and auditable while leaving every frozen scientific pin untouched; conservative-direction fallbacks (unpinned T2, envelope allocations, fail-closed extrapolation, budget guard) ensure measurement failures can cost a GREEN but never fake one.", "backing_ref": "poc/gcp/F1K-BRINGUP-GATE-FIX.md v1 (this freeze; exact diffs + bench evidence); poc/gpt56-review/f1k-construction-review-VERDICT.md findings 3/4/5; poc/gcp/F1K-CONSTRUCTION-PLAN.md v3 SS4.2 GAP-1..4 + SS7 (ASM-2497v2 rule); f1k_driver.py:228,2054-2071 (7+1 arm passes), poc/glm52-probe/f1k-harness/README.md:127-131 (envelope); data/f1k-carriers-v1/generator/construction-manifest.jsonl a8cb3a8a (= f1k_gcp.py PINS); data/f1k-eval-v1/items/{test,dev,guard}.jsonl a549e2aa/ca58847e/c7b7b11f (this pass); poc/gcp/probe-results/m4.json (per_expert_bytes 18541666.7, h_pin band, pin provenance) + accum20.stats (stats format); ASM-1971 (tokenizer/knob bring-up pins), ASM-2205 (1.20x lever), ASM-2374 (windows), ASM-2504 (geometry), ASM-2497v2 (SS7 rule), F1K-PIN-FILE-FIX.md v5/ASM-2513 (REGISTERED, landed 2574c82b - the pin attestation machinery this gate binds to)", "status": "open", "owner": "designer-20", "date": "2026-07-18"}
```

### 5.3 GAP-3b — the driver-side addendum-(7) instance (pre-main, NOT pre-construction)

**[SUPERSEDED — §B.5/D13, gate-fix review #1: the deferral below was REJECTED (it fails the
operational bar — an unfixed pilot→main projection can stall a licensed run or misprice the
long tail at the next gate). The seq-3 landing is COMPLETE (`2574c82b`), the moving-base
rationale is dead, and REV-B includes the exact driver diffs (D13: `Add7Model` + the
reserve-inclusive per-item `projection()` rewrite, RE-LOCATED to the landed tree at
`f1k_driver.py:3348-3497`), landing in the SAME commit. The binding design below is realized
by D13 with one recorded deviation: knots are NOT refit from pilot per-item timings (the
landed ledger records per-phase aggregates only, `Ledger.add`) — the frozen gate knots are
re-LEVELLED by kappa = realized/predicted pilot blend, bounds [0.5, 2.0] fail-closed.]**

The plan §4.2 GAP-3 row and §7 step 4 disposition stand: `f1k_driver.py`'s addendum-(7)
projection (`:2870,:2877-2881` — one pilot-average `s_per_prefill` applied to every main/guard
prefill) must become per-item BEFORE the pilot→main boundary, and it can change d3/STOP outcomes,
so it is formally review-gated (VERDICT finding 5). **Its diffs are deliberately NOT in this
memo:** the PIN-fix seq-3 is editing the driver's ledger/resume seams in-flight (its §1e
cross-phase seam sits in the same region), and stacking a second driver diff against a moving
base would violate the apply-verbatim guarantee this memo makes. Binding design, frozen here so
the follow-up is mechanical: re-use the ASM-2514 model verbatim — knots REFIT from the pilot's
realized per-config timings (the pilot ledger's accumulated seconds are already resume-safe),
T_i from the gate's `tokens-full.jsonl` sidecar (carried to the campaign as an artifact of the
landed gate run, sha-recorded in `bringup-gate.json`), same ±1 SE and fail-closed rules, same
printed-model auditability, applied inside `projection()` in place of the single average. Lands
as its own plain-infra review-gated commit (driver not sha-pinned [MEASURED]) after seq-3
stabilizes and before any main-phase spend; the coordinator should file it at landing time.

## 6. Self-check (every load-bearing claim → where verified this pass → tag)

| # | Claim | Verified where (this checkout / bench, this pass) | Tag |
|---|---|---|---|
| 1 | GAP-1 as coded: synthetic 10×T96/10×T384 sample; one blended s/prefill into `project_ledger` | `f1k_worker.sh:228-231,296-337` read; `f1k_gcp.py:211-260,400-431` read | [MEASURED] |
| 2 | GAP-2: no tokenizer step in any current code path; tokenizer is a bring-up artifact | `f1k_worker.sh` full read (no tok step); `corpora/README.md` ("tokenizer sidecar… bring-up pin"); `tok_glm52.py` docstring | [MEASURED] |
| 3 | GAP-3: per-average projection in gate AND driver addendum-(7) | `f1k_gcp.py:211-260`; `f1k_driver.py:2868-2881` read | [MEASURED] |
| 4 | GAP-4 echoes: docstring `:26-34` vs `ENTRY :434-437`; `:7`+`README.md:12` 3×375 vs `LOCAL_SSD_COUNT=2` (`:106`); stale `--layers 3,…,78` at `README.md:84` | all five sites read this pass | [MEASURED] |
| 5 | `f1k_gcp.py`/`f1k_worker.sh`/new file sha-pinned NOWHERE → plain infra landing, no correction record | grep `f1k_gcp|f1k_worker` over `f1k.json` = 0 hits; `frozen-index.json` = 0; `harness_manifest` pins only `build_carriers.py` a92be3e4 + patch 11f8b458 ("f1k_driver.py, not sha-pinned here" ×2); `bringup_gcp.sh` sha-checks only the patch (`:83-84`) | [MEASURED] |
| 6 | Seq-3 touches exactly `f1k_gcp.py:5/:14/:49/:51/:57` + `bringup_gcp.sh:43` + `README.md:5`; my hunks avoid all of them | `F1K-PIN-FILE-FIX.md` §4 rows 4-7 + `:888/:911` read; D2 hunk headers (-6,3/-26,10/-400,7/-428,4/-433,2/-436,2), D4 headers (-9,7/-54,9/-64,7/-76,10) | [MEASURED] |
| 7 | Diffs apply clean on current bytes AND on the simulated post-seq-3 tree; applied results byte-identical to the tested bench files | bench: `git apply --check` ×2 states ×3 diffs; `cmp` ×3 | [MEASURED] |
| 8 | Inventory reproduces 19,964 exactly: 4,608 + 1,573×8 + 96×22 + 60×11 | arithmetic + code assert (`load_inventory`); harness `README.md:127-131`; `ARMS_MAIN`+`main_arm_passes` = 7 tmpl + 1 d3 | [MEASURED count / STIPULATED pilot-uniform + guard-envelope allocations, bounds stated §2.2] |
| 9 | Word anchors: test 122.7/774-max, d3 146.0, dev 83.8, guard 56.8, constr 30.76; 8-arm blend = 125.6 = plan §1 | recomputed from the corpus files this pass | [MEASURED] |
| 10 | Corpus shas: constr `a8cb3a8a…` = `PINS`; test `a549e2aa…`; dev `ca58847e…`; guard `c7b7b11f…` | `sha256sum` this pass; PINS match | [MEASURED] |
| 11 | Sampling rule realizes on the REAL corpora: N=30, T1=8, max-T forced, all pops ≥2, bins to 1,174 T_p | bench run (mock-f 1.45) | [MEASURED mechanics; realization shifts with real T] |
| 12 | $0 oracle 14/14 incl. finding-3 divergence proof (per-avg 620 h fits, per-item 969 h STOPs), f-branch both sides, 4 fail-closed probes | `f1k_gcp.py gate --selftest` on the applied bench tree | [MEASURED] |
| 13 | Gate cost ≈ $1.2 (T2 96 min + T1 28 min at the probe anchors); bring-up total at the envelope's upper edge | arithmetic on c(96)=75.2/c(384)=290.0 anchors + $0.579/h | [EXTRAPOLATED] |
| 14 | Engine pin/stats interface: `PIN=stats.txt` file-based pin; `STATS` on = usage histograms; stats format `<layer> <expert> <count>`; per-expert 18,541,666.7 B | `northstar.md:92`; design `:641`+ASM row 1846; `accum20.stats` head; `m4.json` | [MEASURED artifacts; knob semantics fetch-grade per ASM-1971, runner re-verified on-box] |
| 15 | PIN_GB band [24,50] from M4 h_pin measurement; dev pin does not transfer; campaign pin per PIN-fix | `m4.json h_pin_by_G`; plan §5; `F1K-PIN-FILE-FIX.md` v5 (landed) | [MEASURED band / cross-ref] |
| 16 | ASM tail 2512; 2513 reserved by seq-3; 2514 free | grep `assumptions.jsonl` tail + `ASM-2513|ASM-2514` = 0 hits | [MEASURED] |
| 17 | f-threshold 1.60 and windows [260.6,900]/[73,155]/rate window enter as frozen inputs, unchanged | plan §4.2/§7; `f1k_gcp.py:84-92` (mirror); D1 reads them via the `frozen` dict from `f1k_gcp` constants | [MEASURED mirror] |
| 18 | Worker STOPs pre-construction unchanged; verdict moved to control box; no autonomous spend added | D3 read-through: no new spend path; `CONTROL-BOX-VERDICT-REQUIRED` status file | [MEASURED design property] |
| 19 | No @handles/account strings; designer-20 pseudonym only; memo-only pass (repo untouched except this file) | this file; `git status` shows only this memo as untracked/new | [MEASURED] |

## NEXT-ACTION block

**[SUPERSEDED — DO NOT LIFT. This was the gate-fix review finding-8 stale chain (a
coordinator following it would apply D1-D4 alone and expect a 14-of-14 oracle). The ONE
liftable next-action block for the whole composite is §B.9 (apply D1-D13, oracle 28/28,
driver mock green, both exit probes).]**

*No git, spend, or VM action was taken by this pass; the only repo write is this memo. Bench
evidence lives in /tmp (regenerable from this memo's artifacts). The coordinator review-gates,
applies, and lands per §4.2.*

---

# §A — REV-A ADDENDUM: closing the FRESH v3-review findings (delta diffs D5–D8 on top of D1–D4)

**Trigger:** `poc/gpt56-review/f1k-construction-v3-review-VERDICT.md` (the cross-model review of
CONSTRUCTION-PLAN v3; overall **REJECT**) confirmed GAP-1..4 (closed by D1–D4 above) and found
MORE blocking, EXECUTABLE gaps plus one operational circularity. This addendum closes every one of
them with bench-verified deltas that apply ON TOP of D1–D4 (apply order: D1→D8). Nothing in the v1
base is edited — its artifacts, shas, and bench claims stand byte-for-byte.

## A0. Finding → disposition map (every executable item lands here)

| v3-review finding | Disposition |
|---|---|
| **F2** cost basis still 89.7-word pilot; h_pin mis-tagged "[MEASURED]"; stale provenance pointer | §A1: authoritative table RE-DERIVED at the 83.8-word basis (arithmetic verified, not transcribed); h_pin re-tagged **[ANALYTICAL]**; the `docs/next/design/glm52-f1k-cost-reduction.md:7` pointer + the stale "30–32 days" wall-clock are PLAN-v4 text items (no code surface), named for plan v4 |
| **F3a** dump preconditions (a)/(c) are `RUNNER-CONFIRM-REQUIRED` scaffolds not required by GREEN | D5+D7: their recorded statuses travel in `gate-inputs.json` and the license conjoins **literal `PASS` on (a)/(b)/(c) + the functional gate** — oracle cases 9/10 |
| **F3b** `provision` creates the VM only; plumbing lives in hard-coded, unbound run-dir wrappers (`vm_setup.sh` aa6504d6 / `watchdog.sh` 8efa0f65) | D6: **`bringup-deploy`** (RAID0+mount the 2 NVMe via stable `by-id` paths, sha-manifested bundle push in the worker's expected layout incl. `gate-corpus/`, detached worker launch, GUEST max-life armed) + **`watchdog`** (parameterized box-side deleter). §A5 states exactly what is code vs documented-manual-with-verify |
| **F3c** `README.md:84` real construction through layer 78 (fails closed at `build_carriers.py:808`) | already closed by D4 (base pass found it independently) |
| **F3d** `affordability --replace` prints replacement SALVAGE-STOP at $155.15 yet exits 0 and announces the license (only `proj["verdict"]` tested, `f1k_gcp.py:417/:423`) | D6: **ANY tested projection that is not GO → exit 2**, and a clean diagnostic run now **exits 3 unconditionally** (the blended path can never license, GO or not). Bench-proven at the review's exact 149.1 s scenario. `gate --replace` likewise tests the 21,537 envelope fail-closed — oracle case 7 |
| **F4** the $8 reserve is "inside the $155 test" in prose but `project_ledger`/`project` compute compute-only → a $154 projection gets GO at $162 true exposure | D5: **reserve-inclusive CAP tests** in the license path — `usd + $8 ≤ $155` AND `hours + $8/rate ≤ 900 h` at BOTH central and +1SE; floors stay compute-only (§A2, STIPULATED) — oracle cases 8a/8b (8a is the old-rule regression proof) |
| **F5** the campaign pin "re-derived via STATS=on over all 4,608 real passes, free, at bring-up" is operationally circular | §A3: the **C-decision** — shape (i), split derivation: the bring-up T1-derived pin **IS the construction-phase campaign pin**; ~~full-corpus re-derivation moves to where it is actually free (during licensed construction), swap allowed ONLY at the construction→pilot boundary~~ **[WITHDRAWN in REV-C (§B.3(5), memo:2568); struck here in REV-E — round-4 verdict 6: re-derivation is structurally impossible through the sha-pinned builder, DEFERRED behind bead `kernel-of-truth-8cpm`; the LICENSED bring-up pin runs the WHOLE campaign — NO boundary swap, NO rebind path]**. SUPERSEDES plan v3 §5's sentence and §2.6's transfer note |
| **F6** revision-log/ceiling overstatements in the plan | plan v4 conforms to this memo (no code surface) |

## A1. The projection baseline, corrected (F2) — re-derived, not transcribed

Basis: pilot = **83.8 words, template-only** (the v3 plan's own §1 anchor; its table rows still
embedded 89.7). Blended campaign words re-computed this pass:
`4,608×30.8 + 2,112×83.8 + 660×56.8 + 12,584×125.6 = 1,936,950 / 19,964 = 97.02` w (−0.64 % vs the
stale 97.65). At the measured $0.17394/h construction SPOT rate:

| f | h_pin basis | blended s/prefill | instance-h | single-VM wall-clock | ledger $ | vs windows |
|---|---|---|---|---|---|---|
| 1.25 | 0.763 **[ANALYTICAL]** | 117.4 | 651 | **~27.1 days** | 113.2 | fits |
| 1.45 | 0.713 **[ANALYTICAL]** | 137.2 | 761 | **~31.7 days** | 132.4 | fits ($140.4 / 807 h reserve-inclusive) |
| 1.80 | 0.713 **[ANALYTICAL]** | 163.3 | 906 | **~37.7 days** | 157.6 | BREACH ($, hours, s-window) |

[EXTRAPOLATED; internal consistency verified this pass: 117.4×19,964/3600 = 651.0 h × 0.17394 =
$113.24; 137.2 → 760.9 h → $132.35; 163.3 → 905.6 h → $157.52. Single-VM wall-clocks stated
explicitly per gate-fix review finding 9: 651.0/24 = 27.1 d, 760.9/24 = 31.7 d, 905.6/24 =
37.7 d — the operational reality of the one-box campaign, disclosed, not hidden in hours.]

**Breach points, independently re-derived:** admissible blended-s window at $0.17394/h =
**[75.68, 160.69] s** (lo: max(260.6, 73/0.17394 = 419.7 h); hi: min(900, 155/0.17394 = 891.1 h)).
Interpolating s(f) between the h=0.713 rows (slope 26.1/0.35 = 74.57 s per unit f):
**f\* ≈ 1.765 by dollars**, **≈ 1.786 by hours** (900 h → 162.30 s), and **≈ 1.653 with the $8
reserve** (147/0.17394 = 845.1 h → 152.40 s). These match the review's corrected figures.
[EXTRAPOLATED, deterministic on MEASURED anchors]

**Tag corrections adopted:** h_pin 0.7132/0.7628/0.9032 are **[ANALYTICAL]** — hit fractions
derived from the M4 concentration histogram (`probe-results/m4.json /h_pin_by_G`), NOT a realized
pinned re-profile. The T2 pinned timings + recorded pin regime this gate produces are the first
**[MEASURED]** pinned-throughput figures in the record. Genuinely [MEASURED] anchors: U 176.79 GB,
c(96) ≈ 75.2 s / c(384) ≈ 290.0 s per-item compute components, AVX2 banner, unpinned 225.2
s/prefill at ~5 % page cache, per-expert 18,541,666.7 B.

## A2. The reserve decision [STIPULATED, frozen by ASM-2515]

`RESERVE_USD = 8.0` (plan §8: staging/overhead + ~5 % preemption re-work) is charged **against the
caps, never credited to the floors**, in the LICENSE path (`f1k_bringup_gate.project`):

- dollars: `usd + 8 ≤ 155` (effective compute cap **$147**), tested at central AND +1SE;
- hours: `hours + 8/rate ≤ 900` (preemption re-work bills hours too — at $0.17394/h the reserve is
  **46.0 h**, effective cap **854 h**), tested at central AND +1SE;
- floors `[$73, 260.6 h]`: compute-only (a reserve must never help a too-cheap ledger clear the
  honesty floors).

All four reserve numbers (usd, hours-at-rate, with-reserve central values) print into
`bringup-gate.json` (`projection.reserve`). The retired blended diagnostic (`affordability`)
deliberately stays reserve-blind AND unlicensed (exit 3) — stated so nobody mistakes its GO.
Consistency: breach-with-reserve f\* ≈ 1.653 (§A1) — the plan's §4.2 "breach ≈ 1.64" round-off is
superseded by this exact figure; the frozen decision threshold f ≤ 1.60 is UNCHANGED.

## A3. The campaign-pin bootstrap — the C-DECISION (F5)

**DECIDED: shape (i) — a preregistered, affordable, pre-GO subset derivation; the plan-v3 §5
sentence ("campaign pin re-derived at bring-up via STATS=on over the 4,608 real construction
passes, free") is WITHDRAWN as operationally circular** (those passes ARE the multi-day
construction workload; they cannot precede a 2–4 h pre-license bring-up).

Concretely — and already instantiated by the base design's pipeline, now made explicit and bound:

1. The pin is derived PRE-license from the **T1 subset** (8 texts of the frozen 30-text sample,
   unpinned, engine usage stats harvested) at **PIN_GB fixed from measured headroom** — ~28 min
   ≈ $0.3 of on-demand box time [EXTRAPOLATED], comfortably inside the bring-up envelope.
2. **That file IS the construction-phase CAMPAIGN pin.** D7 persists it to GCS
   (`campaign-pin.stats`); its sha256 + PIN_GB travel in `gate-inputs.json` (`pin.role` field, D5)
   and bind per the PIN-fix memo's stable core (`PIN=<path>` only; sha+PIN_GB resume/ledger
   binding). Construction runs `PIN=<this file>`.
3. **Estimator honesty — REPRICED [REV-B, gate-fix review #4]:** the projection consumes NO
   h_pin number; its input is the REALIZED PINNED per-item timing (T2) taken with exactly the
   pin construction will use — a weak 8-text-derived pin raises measured s̄ and shrinks the
   headroom mechanically. **But "self-correcting" must be priced honestly: the +1SE band bounds
   the SAMPLING ERROR of the chosen 30-text sample ONLY — it does NOT bound selection bias
   (T1 ⊂ T2: ≤8/30 of the knot mass is timed on the pin's own derivation texts, optimistic
   direction) and does NOT bound unseen-tail behaviour (a pin can pass the 30-item gate yet
   underperform over the 4,608 construction items; re-deriving after construction cannot
   recover that spend).** Named residual risk; chosen mitigation [STIPULATED, ASM-2516]: the
   §B.3 EARLY-ABORT CHECKPOINT — at n_done ~~200/1024/2304~~ **[SUPERSEDED §C.1/ASM-2517:
   the frozen OBSERVABLE schedule is 240/1056/2304 (concept-aligned); run IN-PROCESS by the
   `guard`, off-schedule n_done REFUSED; first exposure ≈ $1.59, not the ≈ $1.3 quoted
   here]** the runner re-projects the whole
   campaign from realized construction throughput (the licensed gate model re-levelled by
   realized/predicted; `f1k_bringup_gate.py checkpoint`) and STOPs (exit 2) on any
   reserve-inclusive breach, with the artifact's realized figures feeding the landed Ledger's
   REQUIRED cost basis — first exposure ~~≈ $1.3~~ **≈ $1.59 [REV-C]**, not $113+. ~~If the pin is underivable, T2 runs
   UNPINNED and the regime is recorded~~ **[SUPERSEDED §B.3: unpinned is REFUSED by the gate;
   an underivable pin is a fail-closed worker STOP + maintainer surface.]**
4. ~~**Where the "free full-corpus derivation" actually lives:** DURING licensed construction
   (STATS counters are ~free there). A full-4,608-pass pin MAY replace the bring-up pin **only at
   the construction→pilot boundary**, re-bound (new sha + same PIN_GB semantics) per the PIN
   memo's cross-phase seam — never mid-phase.~~ **[WITHDRAWN §C.1/ASM-2517: structurally
   impossible through the byte-untouched sha-pinned builder (one 48-row batch per concept, no
   per-pass STATS hook; the guard deliberately POPS a single ambient STATS path — fetch-grade
   truncate semantics would keep the LAST batch only). NO pin replacement happens before pilot:
   the LICENSED bring-up pin runs the WHOLE campaign; the driver REFUSES a campaign pin ≠ the
   gate artifact's; re-derivation/rebind is DEFERRED to the seq-4 builder re-freeze, bead
   `kernel-of-truth-8cpm`.]** Direction conservative: bring-up projected on the
   weaker subset pin; realized pilot/guard/main can only match or beat it, and the GAP-3b pre-main
   re-gate (§5.3) re-checks with realized pilot numbers regardless.
5. **Shape (ii) (unpinned construction + piggyback derivation, separate authorization) REJECTED on
   arithmetic:** measured unpinned throughput is 225.2 s/prefill (M3, [MEASURED]) vs the admissible
   blended window [75.68, 160.69] s — out of window outright; even construction-only unpinned
   (disk-bound, per-item unions 142–217 GB) runs ≈ 4,608 × ~200 s ≈ 256 h ≈ **$45** spot
   [EXTRAPOLATED], pushing the central campaign to ≈ **$163 > $155** before the reserve. Not
   licensable under the frozen windows; not offered.

## A4. Delta artifacts D5–D8 (apply AFTER D1–D4, in order; sha-pinned; bench-verified)

| # | Target | Kind | sha256 of the artifact below |
|---|---|---|---|
| D5 | `poc/gcp/f1k_bringup_gate.py` (post-D1) | unified diff | `e312fc2e51f074f13b842c6405100eeca9af700e2e23dd58405e256a3ac1870c` |
| D6 | `poc/gcp/f1k_gcp.py` (post-D2) | unified diff | `a9315e1a21c37d4369ea5446a18cbe4b6a0034e90cc493d9079b30554898aed5` |
| D7 | `poc/gcp/f1k_worker.sh` (post-D3) | unified diff | `4f058e83375a696f22694279f3d656abf084bb35018ea574a0227ee8dfa6aa82` |
| D8 | `poc/gcp/README.md` (post-D4) | unified diff | `ed2bf8d2579b1402508853026943b133c051c1b9f5774b02a3d0685d89883532` |

Bench evidence [MEASURED, /tmp this pass — no repo file touched]:
- Fresh chain from CURRENT repo bytes: D1..D4 then D5..D8 all `git apply` clean; `py_compile` +
  `bash -n` clean; results byte-identical to the delta-edited bench tree the oracle ran from.
- Same chain on the **simulated post-seq-3 tree** (f1k_gcp.py lines 5/14/49/51/57 + README frozen-
  hash echo rewritten): all 8 apply + compile clean. No hunk touches the `PINS` dict or
  `FROZEN_SHA256` (`f1k_gcp.py:51–68`) in either state.
- **$0 oracle now 19/19** (`f1k_gcp.py gate --selftest`, through the entrypoint): the base 14 plus
  **case 7** (+REPLACE fail-closed: same timing, mandatory GREEN 786 h, TESTED +REPLACE STOP 862 h
  — scale ×1.097), **case 8a** (reserve boundary STOP: $150.22 central ≤ the raw $155 cap — the
  OLD reserve-blind rule would GO — but +$8 breaches; reason names RESERVE), **case 8b** (reserve
  boundary GREEN at $141.14 + $8), **case 9** (dump-(a) `RUNNER-CONFIRM-REQUIRED` STOPs an
  otherwise-GREEN gate), **case 10** (missing `dump_gate` block fails closed).
- Diagnostic probes at the review's exact scenario: `affordability --rate 0.17394
  --s-per-prefill 149.1 --replace` → **exit 2**, STOP text names `with_replace: $155.15 ABOVE
  $155 cap`; without `--replace` → **exit 3** (clean diagnostics NEVER license).
- Applied-tree result shas (current-bytes chain): `f1k_bringup_gate.py 228f5233…`,
  `f1k_gcp.py bd0f914a…`, `f1k_worker.sh 345d1b90…`, `README.md b1130092…`.

### A4.1 D5 — `poc/gcp/f1k_bringup_gate.py` delta (reserve + dump conjuncts + pin role + oracle cases 7–10)

<!-- BEGIN-ARTIFACT D5 poc/gcp/f1k_bringup_gate.py.rev-a.diff sha256=e312fc2e51f074f13b842c6405100eeca9af700e2e23dd58405e256a3ac1870c -->
```diff
diff --git a/poc/gcp/f1k_bringup_gate.py b/poc/gcp/f1k_bringup_gate.py
index 3d1a96d..780b70c 100644
--- a/poc/gcp/f1k_bringup_gate.py
+++ b/poc/gcp/f1k_bringup_gate.py
@@ -59,6 +59,14 @@ POP_FLOOR = {"construction": 2, "pilot": 2, "guard": 2,
 N_SAMPLE_MAX = 34             # hard cap incl. coverage adds (fail-closed)
 FLOOR_EXTRAP_MIN_FRAC = 0.35  # [STIPULATED] s_lo(T) >= 0.35*s_bar(minknot)
 SE_MULT = 1.0                 # frozen band rule: +-1 SE
+RESERVE_USD = 8.0             # [STIPULATED] plan SS8 staging/overhead + ~5%
+                              # preemption re-work reserved INSIDE the caps
+                              # (v3-review finding 4: project_ledger was
+                              # reserve-blind). CAP tests are RESERVE-
+                              # INCLUSIVE (usd + 8; hours + 8/rate); FLOOR
+                              # tests stay compute-only (a reserve must never
+                              # help a too-cheap ledger clear the honesty
+                              # floors).  fix memo SSA2.
 PER_EXPERT_BYTES = 18541666.7 # [MEASURED] probe-results/m4.json per_expert_bytes
 
 # Frozen campaign inventory (envelope-exact; fix memo §2.2, all cited):
@@ -433,8 +441,19 @@ def cmd_collect(args):
         "pin": {"pin_file_sha256": args.pin_sha or None,
                 "pin_gb": float(args.pin_gb) if args.pin_gb else None,
                 "regime": args.pin_regime,
+                "role": "campaign pin for the CONSTRUCTION phase (fix memo "
+                        "SSA3 C-decision): construction runs PIN=<this "
+                        "file>; re-derivation from full-corpus STATS only "
+                        "at the construction->pilot boundary, re-bound "
+                        "there, never mid-phase",
                 "note": "derivation + truthful-attestation mechanics: "
                         "F1K-PIN-FILE-FIX.md v2 (cross-reference)"},
+        "dump_gate": {"a": args.dump_a, "b": args.dump_b, "c": args.dump_c,
+                      "functional_inertness": args.functional,
+                      "rule": "recorded worker/runner statuses; the license "
+                              "requires the literal string PASS on all four "
+                              "(v3-review: RUNNER-CONFIRM-REQUIRED scaffolds "
+                              "must never license)"},
     }
     Path(args.out).write_text(json.dumps(gate_inputs, indent=2))
     print("gate-inputs written: %s (%d T2 runs, %d T1 runs, regime %s)"
@@ -524,6 +543,8 @@ def project(inputs, frozen, replace=False, out_path=None):
             "licenses spend (selftest/dry-run only)")
     raw_knots, knots, repaired = build_knots(inputs)
     rate = inputs["rate_usd_per_hour"]
+    reserve_h = RESERVE_USD / rate
+    dg = inputs.get("dump_gate") or {}
     inv = list(inputs["inventory_t"])
     if replace:
         inv = inv + [[p, M_REPLACE, t] for p, m, t in inv
@@ -555,9 +576,16 @@ def project(inputs, frozen, replace=False, out_path=None):
         "rate_in_window":
             frozen["rate_window"][0] <= rate <= frozen["rate_window"][1],
         "f_le_threshold": f_blend <= F_THRESHOLD,
-        "central_hours_in_window": lo_h <= h_c <= hi_h,
-        "central_usd_in_window": lo_u <= usd_c <= hi_u,
-        "hi_band_below_caps": h_hi <= hi_h and usd_hi <= hi_u,
+        "central_hours_in_window":
+            lo_h <= h_c and h_c + reserve_h <= hi_h,
+        "central_usd_in_window":
+            lo_u <= usd_c and usd_c + RESERVE_USD <= hi_u,
+        "hi_band_below_caps":
+            h_hi + reserve_h <= hi_h and usd_hi + RESERVE_USD <= hi_u,
+        "dump_preconditions_pass":
+            all(dg.get(k) == "PASS" for k in ("a", "b", "c")),
+        "functional_inertness_pass":
+            dg.get("functional_inertness") == "PASS",
         "lo_band_above_floors": h_lo >= lo_h and usd_lo >= lo_u,
         "prefills_ge_min": prefills >= frozen["prefills_min"],
         "tokenizer_real": tc["tokenizer"]["mode"] == "REAL"
@@ -574,15 +602,29 @@ def project(inputs, frozen, replace=False, out_path=None):
         reasons.append("rate %.4f outside frozen window %s"
                        % (rate, frozen["rate_window"]))
     if not checks["central_hours_in_window"]:
-        reasons.append("central projection %.1f h outside [%.1f, %.1f]"
-                       % (h_c, lo_h, hi_h))
+        reasons.append("central projection %.1f h (+%.1f h reserve = %.1f) "
+                       "outside [%.1f, %.1f] RESERVE-INCLUSIVE cap side"
+                       % (h_c, reserve_h, h_c + reserve_h, lo_h, hi_h))
     if not checks["central_usd_in_window"]:
-        reasons.append("central projection $%.2f outside [$%.0f, $%.0f]"
-                       % (usd_c, lo_u, hi_u))
+        reasons.append("central projection $%.2f (+$%.2f reserve = $%.2f) "
+                       "outside [$%.0f, $%.0f] RESERVE-INCLUSIVE cap side"
+                       % (usd_c, RESERVE_USD, usd_c + RESERVE_USD,
+                          lo_u, hi_u))
     if not checks["hi_band_below_caps"]:
-        reasons.append("+%gSE projection %.1f h / $%.2f breaches a cap "
-                       "(%.0f h / $%.0f)" % (SE_MULT, h_hi, usd_hi,
-                                             hi_h, hi_u))
+        reasons.append("+%gSE projection %.1f h / $%.2f breaches a "
+                       "RESERVE-INCLUSIVE cap (%.0f h - %.1f h reserve / "
+                       "$%.0f - $%.0f reserve)"
+                       % (SE_MULT, h_hi, usd_hi, hi_h, reserve_h,
+                          hi_u, RESERVE_USD))
+    if not checks["dump_preconditions_pass"]:
+        reasons.append("dump bring-up preconditions not all PASS "
+                       "(a=%r b=%r c=%r) — RUNNER-CONFIRM-REQUIRED "
+                       "scaffolds never license (v3-review); the runner "
+                       "confirms on-box, writes PASS, and re-runs collect"
+                       % (dg.get("a"), dg.get("b"), dg.get("c")))
+    if not checks["functional_inertness_pass"]:
+        reasons.append("functional inert-by-default gate not PASS (%r)"
+                       % (dg.get("functional_inertness"),))
     if not checks["lo_band_above_floors"]:
         reasons.append("-%gSE projection %.1f h / $%.2f breaches a floor "
                        "(%.1f h / $%.0f) — an honest ledger cannot validate"
@@ -634,7 +676,16 @@ def project(inputs, frozen, replace=False, out_path=None):
             "per_average_naive_hours_RETIRED": round(naive_h, 1),
             "per_average_divergence_pct":
                 round(100.0 * (h_c - naive_h) / naive_h, 2),
+            "reserve": {"usd": RESERVE_USD,
+                        "hours_at_rate": round(reserve_h, 2),
+                        "rule": "caps reserve-inclusive; floors "
+                                "compute-only [STIPULATED, fix memo SSA2]",
+                        "usd_central_with_reserve":
+                            round(usd_c + RESERVE_USD, 2),
+                        "hours_central_with_reserve":
+                            round(h_c + reserve_h, 1)},
         },
+        "dump_gate": dg,
         "thresholds": frozen,
         "semantics": "plan §7: GREEN -> construction proceeds WITHOUT "
                      "re-surfacing (standing authorization); STOP -> "
@@ -764,7 +815,9 @@ def selftest():
                     "t1_unpinned_runs": [], "inventory_t": inv_t,
                     "rate_usd_per_hour": rate, "rate_source": "selftest",
                     "pin": {"pin_file_sha256": "f" * 64, "pin_gb": 40.0,
-                            "regime": "pinned-bringup", "note": "mock"}}
+                            "regime": "pinned-bringup", "note": "mock"},
+                    "dump_gate": {"a": "PASS", "b": "PASS", "c": "PASS",
+                                  "functional_inertness": "PASS"}}
 
         # case 1 GREEN: linear planted s(T) scaled to 700 h central
         mass = sum(e["m"] * (e["T"] + CONT_TOKENS) for e in ent)
@@ -847,10 +900,58 @@ def selftest():
                 sample=str(td / "samp/timing-sample.json"),
                 tokens=str(td / "tok"), t2=str(td / "t2-part.jsonl"),
                 t1=None, rate="0.174", pin_sha="", pin_gb="",
-                pin_regime="pinned-bringup", out=str(td / "gi.json")))
+                pin_regime="pinned-bringup", dump_a="PASS", dump_b="PASS",
+                dump_c="PASS", functional="PASS", out=str(td / "gi.json")))
             check(False, "case 6 must refuse partial T2 results")
         except SystemExit:
             check(True, "case 6 fail-closed: partial T2 timing refused")
+        # case 7 (+REPLACE fail-closed, v3-review :417/:423 lineage): the
+        # SAME timing gives mandatory GREEN but +REPLACE STOP — a tested
+        # replace projection must never be advisory.
+        mass_rep = sum(e["T"] + CONT_TOKENS for e in ent
+                       if e["pop"] == "main-tmpl")
+        b7 = 780.0 * 3600.0 / mass   # GREEN incl. reserve+SE; x1.097 REPLACE breaches
+        _fake_timing(sample, lambda t: b7 * t, td / "t2-rep.jsonl")
+        art7a = project(mk_inputs(td / "t2-rep.jsonl"), frozen)
+        art7b = project(mk_inputs(td / "t2-rep.jsonl"), frozen, replace=True)
+        check(art7a["verdict"] == "GREEN" and art7b["verdict"] == "STOP",
+              "case 7 +REPLACE fail-closed: mandatory GREEN (%.0f h) but "
+              "the TESTED +REPLACE projection STOPs (%.0f h; scale x%.3f)"
+              % (art7a["projection"]["instance_hours"]["central"],
+                 art7b["projection"]["instance_hours"]["central"],
+                 1.0 + mass_rep / mass))
+        # case 8 (reserve boundary, v3-review finding 4): compute-only $149
+        # at rate 0.20 passes the RAW $155 cap (the OLD reserve-blind rule)
+        # but 149+8 = 157 breaches reserve-inclusive -> STOP; $140 -> GREEN.
+        b8 = (149.0 / 0.20) * 3600.0 / mass
+        _fake_timing(sample, lambda t: b8 * t, td / "t2-res.jsonl")
+        art8a = project(mk_inputs(td / "t2-res.jsonl", rate=0.20), frozen)
+        u8 = art8a["projection"]["usd_total"]["central"]
+        check(art8a["verdict"] == "STOP" and u8 <= 155.0
+              and any("RESERVE" in r for r in art8a["reasons"]),
+              "case 8a reserve-boundary STOP: $%.2f central <= $155 raw cap "
+              "(the OLD rule would GO) but +$8 reserve breaches" % u8)
+        b8b = (140.0 / 0.20) * 3600.0 / mass
+        _fake_timing(sample, lambda t: b8b * t, td / "t2-res2.jsonl")
+        art8b = project(mk_inputs(td / "t2-res2.jsonl", rate=0.20), frozen)
+        check(art8b["verdict"] == "GREEN",
+              "case 8b reserve-boundary GREEN at $%.2f + $8 reserve"
+              % art8b["projection"]["usd_total"]["central"])
+        # case 9 (dump preconditions are HARD conjuncts): a scaffold status
+        # on precondition (a) STOPs an otherwise-GREEN gate.
+        in9 = mk_inputs(td / "t2-green.jsonl")
+        in9["dump_gate"]["a"] = "RUNNER-CONFIRM-REQUIRED"
+        art9 = project(in9, frozen)
+        check(art9["verdict"] == "STOP"
+              and any("precondition" in r for r in art9["reasons"]),
+              "case 9 STOP: dump-(a) RUNNER-CONFIRM-REQUIRED never licenses")
+        # case 10: a gate-inputs file with NO dump_gate block (old format)
+        # fails closed the same way.
+        in10 = mk_inputs(td / "t2-green.jsonl")
+        del in10["dump_gate"]
+        art10 = project(in10, frozen)
+        check(art10["verdict"] == "STOP",
+              "case 10 STOP: missing dump_gate block fails closed")
     print()
     if fails:
         print("BRINGUP-GATE SELFTEST FAILED (%d)" % len(fails))
@@ -889,6 +990,10 @@ def main():
     p.add_argument("--pin-gb", default="")
     p.add_argument("--pin-regime", required=True,
                    choices=["pinned-bringup", "unpinned"])
+    p.add_argument("--dump-a", required=True)
+    p.add_argument("--dump-b", required=True)
+    p.add_argument("--dump-c", required=True)
+    p.add_argument("--functional", required=True)
     p.add_argument("--out", required=True)
     sub.add_parser("selftest")
     args = ap.parse_args()
```
<!-- END-ARTIFACT D5 -->

### A4.2 D6 — `poc/gcp/f1k_gcp.py` delta (--replace fail-closed + exit-3 diagnostic + `bringup-deploy`/`watchdog`)

<!-- BEGIN-ARTIFACT D6 poc/gcp/f1k_gcp.py.rev-a.diff sha256=a9315e1a21c37d4369ea5446a18cbe4b6a0034e90cc493d9079b30554898aed5 -->
```diff
diff --git a/poc/gcp/f1k_gcp.py b/poc/gcp/f1k_gcp.py
index d54976f..e2877a7 100755
--- a/poc/gcp/f1k_gcp.py
+++ b/poc/gcp/f1k_gcp.py
@@ -30,6 +30,13 @@ Entrypoints (source ~/.config/kot/gcp.env first):
                                            #   --selftest = $0 mock oracle)
   python3 poc/gcp/f1k_gcp.py affordability # SECONDARY synthetic diagnostic
                                            #   ONLY — licenses NOTHING
+  python3 poc/gcp/f1k_gcp.py bringup-deploy# RAID+mount NVMe, push the worker
+                                           #   bundle + frozen gate corpora,
+                                           #   launch f1k_worker.sh detached,
+                                           #   arm the GUEST max-life backstop
+  python3 poc/gcp/f1k_gcp.py watchdog --max-hours H
+                                           # box-side teardown watchdog loop
+                                           #   (nohup it; verify with pgrep)
   python3 poc/gcp/f1k_gcp.py status        # poll VM state + GCS heartbeat
   python3 poc/gcp/f1k_gcp.py teardown      # delete VM + disks (nothing bills idle)
 (stage/build/KaE+dump bring-up run ON the VM via f1k_worker.sh — they were
@@ -353,8 +360,11 @@ def cmd_provision() -> None:
         ssd += ["--local-ssd", "interface=NVME"]
     if BRINGUP_ONDEMAND:
         # ON-DEMAND bring-up VM (ops; NOT the frozen SPOT construction ledger).
-        # --instance-termination-action is SPOT-only, so it is DROPPED here; the
-        # control-box watchdog + guest max-life backstops still bound billing.
+        # --instance-termination-action is SPOT-only, so it is DROPPED here;
+        # billing is bounded by REAL backstops this orchestrator provides
+        # (v3-review: they were comments, not code): `bringup-deploy` arms the
+        # guest max-life self-halt, and `watchdog` is the box-side deleter
+        # (launch under nohup; verify: pgrep -f 'f1k_gcp.py watchdog').
         prov_model = "STANDARD"
         sched_args = []
         mode = ("ON-DEMAND (bring-up VALIDATION only — NOT the frozen SPOT "
@@ -425,16 +435,24 @@ def cmd_affordability() -> None:
         out["with_replace"] = project_ledger(args.rate, args.s_per_prefill,
                                               PREFILLS_WITH_REPLACE)
     print(json.dumps(out, indent=2))
-    if proj["verdict"] != "GO":
+    # v3-review fix (:417/:423 lineage): EVERY tested projection must be GO,
+    # or this exits nonzero — the +REPLACE verdict is never advisory. And a
+    # clean diagnostic still exits 3: this blended path can NEVER license.
+    bad = {name: p for name, p in out.items() if p["verdict"] != "GO"}
+    if bad:
         die("F1K_AFFORDABILITY",
-            "SALVAGE-STOP: %s. The frozen cost model at the measured rate does "
-            "NOT admit a valid ledger for this throughput; this is a "
-            "cost-model-vs-rate decision (Fable/coordinator/maintainer), NOT a "
-            "retry. Do NOT spend construction." % "; ".join(proj["reasons"]))
-    print("\nAFFORDABILITY DIAGNOSTIC GO: projected instance_hours %.1f h, "
-          "usd_total $%.2f inside the frozen window — SECONDARY diagnostic "
-          "only; the construction license is `f1k_gcp.py gate` (GREEN)."
-          % (proj["projected_instance_hours"], proj["projected_usd_total"]))
+            "SALVAGE-STOP (%s): %s. The frozen cost model at the measured "
+            "rate does NOT admit a valid ledger for EVERY tested projection; "
+            "this is a cost-model-vs-rate decision (Fable/coordinator/"
+            "maintainer), NOT a retry. Do NOT spend construction."
+            % (", ".join(sorted(bad)),
+               " | ".join("%s: %s" % (n, "; ".join(p["reasons"]))
+                          for n, p in sorted(bad.items()))))
+    print("\nAFFORDABILITY DIAGNOSTIC: every tested projection inside the "
+          "frozen window — SECONDARY diagnostic only, NEVER a license "
+          "(exit 3); the construction license is `f1k_gcp.py gate` (GREEN, "
+          "reserve-inclusive, dump-preconditions conjoined).")
+    sys.exit(3)
 
 
 def cmd_gate() -> None:
@@ -499,10 +517,130 @@ def cmd_gate() -> None:
              art["projection"]["usd_total"]["central"]))
 
 
+def cmd_bringup_deploy() -> None:
+    """Bind the bring-up plumbing the v3 review found UNBOUND (`provision`
+    creates only the VM; the historical run-dir wrappers vm_setup.sh
+    aa6504d6 / watchdog.sh 8efa0f65 are hard-coded and uncommitted): RAID0 +
+    mount the 2 local NVMe, push the worker bundle in the layout
+    f1k_worker.sh expects ($HERE/{kae-patch-draft,dump-patch,gate-corpus},
+    f1k_bringup_gate.py + tok_glm52.py + bringup_gcp.sh alongside), launch
+    the worker detached (setsid nohup), and arm the GUEST max-life backstop
+    (root `shutdown -P`; default 900 min via KOT_F1K_GUEST_MAXLIFE_MIN).
+
+    MANUAL PREREQS (verify, never assume):
+      gsutil ls "$KOT_F1K_BUCKET"          # bucket reachable
+      env: KOT_F1K_BUCKET, COLIBRI_GIT_URL, KOT_F1K_SPOT_RATE set
+    MANUAL FOLLOW-UP (box-side, NEVER agent-held — plan v3 SS9 rule 1):
+      nohup python3 poc/gcp/f1k_gcp.py watchdog --max-hours 8 \
+        > watchdog.log 2>&1 &
+      verify: pgrep -f 'f1k_gcp.py watchdog'
+      guest max-life verify: gcloud compute ssh ... 'sudo shutdown --show'"""
+    import shutil, tempfile
+    verify_pins()
+    if not vm_exists():
+        die("F1K_DEPLOY", "no VM %s in %s — run provision first"
+            % (INSTANCE_NAME, ZONE))
+    for var in ("KOT_F1K_BUCKET", "COLIBRI_GIT_URL", "KOT_F1K_SPOT_RATE"):
+        if not os.environ.get(var):
+            die("F1K_DEPLOY", "%s unset (f1k_worker.sh env contract)" % var)
+    max_life_min = int(os.environ.get("KOT_F1K_GUEST_MAXLIFE_MIN", "900"))
+    # 1. remote prep: RAID0 the 2 local NVMe (stable by-id paths) + max-life
+    remote = (
+        "set -euo pipefail\n"
+        "if [ ! -d /mnt/nvme ]; then\n"
+        "  sudo apt-get update -qq && sudo apt-get install -y -qq mdadm\n"
+        "  DEVS=$(ls /dev/disk/by-id/google-local-nvme-ssd-* 2>/dev/null)\n"
+        "  N=$(echo \"$DEVS\" | wc -w)\n"
+        "  [ \"$N\" -eq %d ] || { echo \"ERR: $N local NVMe != %d\"; exit 2; }\n"
+        "  sudo mdadm --create /dev/md0 --level=0 --raid-devices=%d $DEVS\n"
+        "  sudo mkfs.ext4 -F /dev/md0 && sudo mkdir -p /mnt/nvme\n"
+        "  sudo mount /dev/md0 /mnt/nvme && sudo chown \"$USER\" /mnt/nvme\n"
+        "fi\n"
+        "sudo shutdown -P +%d 'kot-f1k guest max-life backstop'\n"
+        % (LOCAL_SSD_COUNT, LOCAL_SSD_COUNT, LOCAL_SSD_COUNT, max_life_min))
+    gcloud("compute", "ssh", INSTANCE_NAME, "--zone", ZONE,
+           "--command", remote)
+    # 2. assemble the bundle locally in the worker's expected layout
+    stage = Path(tempfile.mkdtemp(prefix="kot-f1k-bundle-"))
+    bundle = stage / "f1k"
+    bundle.mkdir()
+    for f in ("f1k_worker.sh", "bringup_gcp.sh", "f1k_bringup_gate.py"):
+        shutil.copy2(HERE / f, bundle / f)
+    shutil.copy2(HARNESS / "tok_glm52.py", bundle / "tok_glm52.py")
+    shutil.copytree(KAE_PATCH_DIR, bundle / "kae-patch-draft")
+    shutil.copytree(DUMP_PATCH_DIR, bundle / "dump-patch")
+    gc = bundle / "gate-corpus"
+    gc.mkdir()
+    shutil.copy2(PIN_PATHS["construction-manifest.jsonl"],
+                 gc / "construction-manifest.jsonl")
+    items = REPO / "data" / "f1k-eval-v1" / "items"
+    for f in ("test.jsonl", "dev.jsonl", "guard.jsonl"):
+        shutil.copy2(items / f, gc / f)
+    manifest = {str(p.relative_to(bundle)): sha256_file(p)
+                for p in sorted(bundle.rglob("*")) if p.is_file()}
+    (bundle / "bundle-manifest.json").write_text(json.dumps(manifest,
+                                                            indent=1))
+    print("bundle: %d files; manifest sha %s"
+          % (len(manifest),
+             hashlib.sha256(json.dumps(manifest,
+                                       sort_keys=True).encode())
+             .hexdigest()[:16]))
+    gcloud("compute", "scp", "--recurse", "--zone", ZONE,
+           str(bundle), "%s:~/" % INSTANCE_NAME)
+    # 3. launch the worker detached with the env contract
+    launch = ("cd ~/f1k && setsid nohup env KOT_F1K_BUCKET='%s' "
+              "COLIBRI_GIT_URL='%s' KOT_F1K_SPOT_RATE='%s' "
+              "bash f1k_worker.sh > worker.log 2>&1 & echo LAUNCHED-$!"
+              % (os.environ["KOT_F1K_BUCKET"],
+                 os.environ["COLIBRI_GIT_URL"],
+                 os.environ["KOT_F1K_SPOT_RATE"]))
+    gcloud("compute", "ssh", INSTANCE_NAME, "--zone", ZONE,
+           "--command", launch)
+    print("bringup-deploy DONE: RAID+mount, bundle pushed (manifest above), "
+          "worker launched detached, guest max-life %d min armed. NOW start "
+          "the box-side watchdog (docstring) and verify with pgrep."
+          % max_life_min)
+
+
+def cmd_watchdog() -> None:
+    """Box-side teardown watchdog (plan v3 SS9 rule 1: long runs are driven
+    by the box-side watchdog + the autonomous on-VM worker, NEVER an
+    agent-held monitor). Parameterized promotion of the proven runner-10
+    run-dir watchdog (8efa0f65). Polls every --poll-seconds; deletes the VM
+    on (a) the --max-hours deadline or (b) a FAILED GCS heartbeat when
+    KOT_F1K_BUCKET is set. Run it under nohup on the control box."""
+    import argparse
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--max-hours", type=float, required=True)
+    ap.add_argument("--poll-seconds", type=int, default=180)
+    args = ap.parse_args(sys.argv[2:])
+    deadline = time.time() + args.max_hours * 3600.0
+    bucket = os.environ.get("KOT_F1K_BUCKET", "")
+    while True:
+        if not vm_exists():
+            print("watchdog: VM %s gone; exiting clean." % INSTANCE_NAME)
+            return
+        failed_hb = False
+        if bucket:
+            r = subprocess.run(
+                ["gsutil", "-q", "cat",
+                 bucket + "/f1k/bringup/heartbeat.json"],
+                capture_output=True, text=True)
+            failed_hb = r.returncode == 0 and '"FAILED' in r.stdout
+        if time.time() >= deadline or failed_hb:
+            print("watchdog: %s -> teardown"
+                  % ("FAILED heartbeat" if failed_hb else
+                     "max-life deadline"))
+            cmd_teardown()
+            return
+        time.sleep(args.poll_seconds)
+
+
 ENTRY = {
     "plan": cmd_plan, "provision": cmd_provision, "status": cmd_status,
     "teardown": cmd_teardown, "affordability": cmd_affordability,
     "gate": cmd_gate,
+    "bringup-deploy": cmd_bringup_deploy, "watchdog": cmd_watchdog,
 }
 
 
```
<!-- END-ARTIFACT D6 -->

### A4.3 D7 — `poc/gcp/f1k_worker.sh` delta (dump statuses into gate-inputs + campaign-pin persistence)

<!-- BEGIN-ARTIFACT D7 poc/gcp/f1k_worker.sh.rev-a.diff sha256=4f058e83375a696f22694279f3d656abf084bb35018ea574a0227ee8dfa6aa82 -->
```diff
diff --git a/poc/gcp/f1k_worker.sh b/poc/gcp/f1k_worker.sh
index decb167..b0b654d 100755
--- a/poc/gcp/f1k_worker.sh
+++ b/poc/gcp/f1k_worker.sh
@@ -181,6 +181,7 @@ elif grep -q "test_kae: 44/44" "$GATE/dump-realchecks.log" \
 else
   die "dump bring-up precondition (b) FAILED (real-checks.sh rc=$RC_B, not the demoted objdump-spill signature)"
 fi
+echo "PASS" > "$GATE/dump-b.status"    # (b) is fail-closed above; reaching here proves it
 hb "dump-precond-b-ok"
 
 step "4/5 DUMP bring-up gate (a): tiny real dump + token-id consistency"
@@ -413,7 +414,18 @@ python3 "$GATEPY" collect --sample "$GATE/gate-sample/timing-sample.json" \
   --tokens "$GATE/gate-tokens" --t2 "$GATE/t2-results.jsonl" \
   --t1 "$GATE/t1-results.jsonl" --rate "$SPOT_RATE" \
   --pin-sha "$PIN_SHA" --pin-gb "$PIN_GB" --pin-regime "$PIN_REGIME" \
+  --dump-a "$(cat "$GATE/tiny-dump.status" 2>/dev/null || echo MISSING)" \
+  --dump-b "$(cat "$GATE/dump-b.status" 2>/dev/null || echo MISSING)" \
+  --dump-c "$(cat "$GATE/moe-sum-crosscheck.status" 2>/dev/null || echo MISSING)" \
+  --functional "$(python3 -c "import json;print(json.load(open('$GATE/functional-inertness.json')).get('verdict','MISSING'))" 2>/dev/null || echo MISSING)" \
   --out "$GATE/gate-inputs.json" || die "gate collect FAILED"
+# The bring-up pin IS the construction-phase CAMPAIGN pin (fix memo SSA3
+# C-decision): persist it; construction runs PIN=<this file> (sha+PIN_GB
+# bound per F1K-PIN-FILE-FIX.md). Full-corpus re-derivation is allowed ONLY
+# at the construction->pilot boundary, re-bound there, never mid-phase.
+if [ -n "$PIN_SHA" ]; then
+  gsutil -q cp "$PIN_FILE" "$BUCKET/f1k/bringup/campaign-pin.stats" || true
+fi
 echo "CONTROL-BOX-VERDICT-REQUIRED" > "$GATE/bringup-gate.status"
 cat > "$GATE/bringup-gate-README.txt" <<EOF
 REAL-CORPUS gate inputs ready: $GATE/gate-inputs.json (mirrored to GCS).
@@ -422,7 +434,15 @@ Pull it and run the MECHANICAL verdict on the control box:
 GREEN -> construction proceeds without re-surfacing (plan §7 standing
 authorization). STOP (exit 2 ERR_F1K_BRINGUP_GATE) -> MANDATORY maintainer
 surface. The synthetic blend (affordability-measured.json) is a SECONDARY
-diagnostic; \`f1k_gcp.py affordability\` licenses NOTHING.
+diagnostic; \`f1k_gcp.py affordability\` licenses NOTHING (exit 3 even on GO).
+HARD CONJUNCTS (v3-review): dump preconditions (a)/(b)/(c) + the functional
+gate must be recorded PASS in gate-inputs.json or the verdict STOPs. After
+the on-box confirmations, the RUNNER overwrites tiny-dump.status and
+moe-sum-crosscheck.status with the literal PASS and RE-RUNS the collect
+command above (cheap; no re-timing) before pulling gate-inputs.json.
+The caps are tested RESERVE-INCLUSIVE (+\$8 / +8/rate hours) on the control
+box; the campaign pin for construction is campaign-pin.stats (sha in
+gate-inputs.json), bound per F1K-PIN-FILE-FIX.md.
 EOF
 cat "$GATE/bringup-gate-README.txt"
 hb "gate-inputs-ready"
```
<!-- END-ARTIFACT D7 -->

### A4.4 D8 — `poc/gcp/README.md` delta (bound plumbing + hard conjuncts + reserve wording)

<!-- BEGIN-ARTIFACT D8 poc/gcp/README.md.rev-a.diff sha256=ed2bf8d2579b1402508853026943b133c051c1b9f5774b02a3d0685d89883532 -->
```diff
diff --git a/poc/gcp/README.md b/poc/gcp/README.md
index 6744cf7..023b43f 100644
--- a/poc/gcp/README.md
+++ b/poc/gcp/README.md
@@ -54,7 +54,7 @@ maintainer), **NOT a retry** — the pzb6 class discovered at bring-up.
 
 | File | What it is |
 |---|---|
-| `f1k_gcp.py` | Orchestrator (runs on the control box): `plan` ($0 dry-plan: pins + reuse-gate + SPOT/disk/window asserts), `provision` (Spot VM + 2 local SSD), `status`, `teardown`, `gate` (**the bring-up gate verdict — kot-f1k-bringup-gate/1; GREEN is the ONLY construction license**; `--selftest` = $0 mock oracle), `affordability` (one-blended-s/prefill projection — **SECONDARY diagnostic ONLY, licenses nothing**). |
+| `f1k_gcp.py` | Orchestrator (runs on the control box): `plan` ($0 dry-plan: pins + reuse-gate + SPOT/disk/window asserts), `provision` (Spot VM + 2 local SSD), `status`, `teardown`, `bringup-deploy` (RAID+mount NVMe, push the worker bundle + frozen gate corpora, launch the worker detached, arm the guest max-life), `watchdog --max-hours H` (box-side teardown loop; nohup it, verify `pgrep -f 'f1k_gcp.py watchdog'`), `gate` (**the bring-up gate verdict — kot-f1k-bringup-gate/1; GREEN is the ONLY construction license**; `--selftest` = $0 mock oracle), `affordability` (one-blended-s/prefill projection — **SECONDARY diagnostic ONLY, licenses nothing**). |
 | `f1k_bringup_gate.py` | The FIXED bring-up gate machinery (`F1K-BRINGUP-GATE-FIX.md` v1, GAP-1/2/3): frozen deterministic stratified real-corpus sampling rule, full-corpus tokenization (measured f, per-item T), bring-up pin-file derivation, per-item token-aware ledger projection + GREEN/STOP artifact; `selftest` = $0 end-to-end mock oracle. |
 | `bringup_gcp.sh` | KaE bring-up on the VM: colibri@`a78a06fc` + KaE patch (`11f8b458`), build, 44/44 `test_kae`; objdump patch-shape checks (clone-aware, reference + native flags) are **ADVISORY-ONLY on the VM** (bead f2uk / ASM-2503: gcc-version-brittle even at `-O2 -march=x86-64-v3`; fail-closed objdump lives off-box on the gcc-11.5 basis; the frozen `bringup.sh` is untouched). The AUTHORITATIVE inertness proof is the functional KAE-unset byte-identity gate in `f1k_worker.sh`. |
 | `f1k_worker.sh` | On-VM autonomous worker: STAGE (GCS mirror → else HF → NVMe, weight-hash pin) → BUILD scoring + construction engines → KaE bring-up → dump bring-up gate (b) → scaffolds (a)+(c) → **REAL-CORPUS gate inputs** (tokenize → measured f + per-item T; frozen stratified per-item timing, T1 unpinned → bring-up pin → T2 pinned; `gate-inputs.json`) → **STOP before construction spend**. Heartbeat + artifacts to GCS; idempotent (spot preemption re-runs, restages from GCS). |
@@ -65,12 +65,15 @@ maintainer), **NOT a retry** — the pzb6 class discovered at bring-up.
 1. `provision` → **record the ACTUAL assigned spot $/h** (load-bearing for the
    affordability gate). Set `KOT_F1K_BUCKET=gs://…` (same-region estate mirror),
    `COLIBRI_GIT_URL` (coordinator-supplied), `KOT_F1K_SPOT_RATE=<measured>`.
-2. RAID0 + mount the 2 local SSD at `/mnt/nvme`; copy the four frozen gate
-   corpora (`data/f1k-carriers-v1/generator/construction-manifest.jsonl` +
-   `data/f1k-eval-v1/items/{test,dev,guard}.jsonl`) into `poc/gcp/gate-corpus/`;
-   scp `poc/gcp/` (incl. `f1k_bringup_gate.py` + `gate-corpus/`),
-   `poc/glm52-probe/f1k-harness/`, `poc/glm52-probe/kae-patch-draft/`,
-   `analysis/f1k.py` to the VM; launch `f1k_worker.sh` detached (systemd/nohup).
+2. `python3 poc/gcp/f1k_gcp.py bringup-deploy` — RAID0+mount the 2 local SSD,
+   assemble + push the worker bundle (worker, `bringup_gcp.sh`,
+   `f1k_bringup_gate.py`, `tok_glm52.py`, `kae-patch-draft/`, `dump-patch/`,
+   and `gate-corpus/` = the four frozen corpora
+   `construction-manifest.jsonl` + `f1k-eval-v1/items/{test,dev,guard}.jsonl`,
+   sha-manifested), launch `f1k_worker.sh` detached, arm the guest max-life
+   (verify on-VM: `sudo shutdown --show`). Then start the box-side watchdog:
+   `nohup python3 poc/gcp/f1k_gcp.py watchdog --max-hours 8 &` — verify
+   `pgrep -f 'f1k_gcp.py watchdog'` (plan §9: never agent-held).
 3. Worker STAGE + BUILD + KaE bring-up + **dump bring-up gate**:
    - (b) unarmed byte-identity + `test_kae` 44/44 + `test_kae_dump` 43/43 +
      objdump inertness — automated via `dump-patch/real-checks.sh`.
@@ -80,14 +83,23 @@ maintainer), **NOT a retry** — the pzb6 class discovered at bring-up.
      confirms ON-BOX** (a separate capture path, not `kae_dump.h`, cell-for-cell
      equal to the engine dump). Its correctness cannot be validated blind, so
      it is a runner-confirmed PASS. ANY precondition failure → SALVAGE+STOP.
+     **The recorded PASS of (a)/(b)/(c) + the functional gate is a HARD
+     conjunct of the construction license** (v3-review): the runner writes
+     the literal `PASS` into `tiny-dump.status`/`moe-sum-crosscheck.status`
+     and re-runs the worker's collect command (no re-timing) — a
+     `RUNNER-CONFIRM-REQUIRED` scaffold status makes `gate` STOP.
 4. **Bring-up affordability gate** (`F1K-BRINGUP-GATE-FIX.md` v1): the worker
    tokenizes the frozen corpora (measured **f** + per-item T), times the frozen
    stratified REAL-corpus sample per-item (T1 unpinned → bring-up pin at
    measured PIN_GB → T2 pinned), and writes `gate-inputs.json`; then on the
    control box `f1k_gcp.py gate --inputs <pulled gate-inputs.json>` — **GREEN
    (exit 0) is the ONLY license for construction spend**; STOP = mandatory
-   maintainer surface (plan §7). The synthetic blend +
-   `f1k_gcp.py affordability` remain a SECONDARY diagnostic, licensing nothing.
+   maintainer surface (plan §7). Caps are tested **reserve-inclusive**
+   (+$8 / +$8÷rate hours [STIPULATED plan §8 reserve]; floors compute-only);
+   dump (a)/(b)/(c) + functional PASS are hard conjuncts; `--replace` tests
+   the 21,537 envelope and ANY tested STOP exits nonzero. The synthetic
+   blend + `f1k_gcp.py affordability` remain a SECONDARY diagnostic,
+   licensing nothing (exit 3 even when clean).
 5. **Construction** (gated on 3+4): `build_carriers.py construct --mode real
    --layers 3,…,77` (the landed ASM-2504 DRAFT=0 geometry, 75 layers) with the
    three provenance shas **and their artifacts**
```
<!-- END-ARTIFACT D8 -->

## A5. Bring-up plumbing: what is CODE vs what stays a DOCUMENTED MANUAL STEP (F3b, honest split)

| Step | Now | Verify command |
|---|---|---|
| VM create | code (`provision`, unchanged) | `status` |
| RAID0+mount 2×NVMe (stable `google-local-nvme-ssd-*` by-id paths, count asserted) | code (`bringup-deploy`) | `gcloud compute ssh … 'df -h /mnt/nvme'` |
| Bundle push in the worker's expected layout (+ `gate-corpus/`, sha manifest printed) | code (`bringup-deploy`) | manifest sha in the deploy output / run-log |
| Worker launch, detached | code (`bringup-deploy`) | GCS heartbeat via `status`/`gsutil cat …/heartbeat.json` |
| GUEST max-life (root `shutdown -P`, default 900 min) | code (`bringup-deploy`) | `gcloud compute ssh … 'sudo shutdown --show'` |
| Box-side watchdog loop (deadline + FAILED-heartbeat teardown) | code (`watchdog`) — **launch is MANUAL under nohup** (plan §9: never agent-held) | `pgrep -f 'f1k_gcp.py watchdog'` |
| GCS bucket prerequisite | manual | `gsutil ls "$KOT_F1K_BUCKET"` |
| Dump-(a)/(c) on-box confirmation → literal `PASS` into the status files → re-run collect | manual (runner; by design — cannot be validated blind) | `cat $GATE/{tiny-dump,moe-sum-crosscheck}.status`; re-collected `gate-inputs.json` carries PASS |

No fictional automation: everything the run-dir wrappers (aa6504d6/8efa0f65 [MEASURED,
`opus-runs/20260717T041341Z/run-log.jsonl`]) did is either a committed parameterized entrypoint
above or a named manual step with a verify command.

## A6. ASM-2515 registration text (register-at-commit WITH ASM-2514, same landing commit; next
free id after 2514 [MEASURED: tail 2512; 2513 = PIN-fix; 2514 = §5.2]; no renumbering)

```json
{"id": "ASM-2515", "tag": "STIPULATED", "load_bearing": true, "claim": "F1-K BRING-UP GATE REV-A (amends ASM-2514 in the same landing commit; RECONCILIATION [REV-B]: ASM-2513 is REGISTERED and LANDED at 2574c82b - the validate_pinning/check_pin_engagement/spend-start/ledger+addendum binding machinery this gate BINDS TO (engagement grammar imported from the landed driver, never re-invented); ASM-2514 registers in this same commit and is amended by REV-B as recorded there; ASM-2516 (REV-B) further amends items (4)-(5) below; closes the FRESH v3-plan cross-model review findings poc/gpt56-review/f1k-construction-v3-review-VERDICT.md): (1) RESERVE - the $8 [STIPULATED plan SS8] staging/overhead+preemption reserve is charged against the CAPS in the license projection (usd+8<=155 AND hours+8/rate<=900, tested at central AND +1SE) and NEVER credited to the floors (compute-only), making the effective compute ceiling $147 / (900h - 8/rate); breach-with-reserve f*~=1.653 at the measured $0.17394/h supersedes the plan's ~1.64 round-off; the frozen f<=1.60 threshold is unchanged. (2) DUMP CONJUNCTS - the recorded statuses of dump bring-up preconditions (a)/(b)/(c) and the functional inert-by-default gate travel in gate-inputs.json and the license verdict conjoins the literal string PASS on all four; RUNNER-CONFIRM-REQUIRED scaffolds can never license; the runner confirms on-box, writes PASS, and re-runs collect (no re-timing). (3) ANY-TESTED-PROJECTION STOP - f1k_gcp.py affordability exits 2 if ANY emitted projection (mandatory or +REPLACE) is not GO and exits 3 even when clean (the blended path never licenses); f1k_gcp.py gate --replace tests the 21,537 envelope under the same fail-closed rule. (4) CAMPAIGN-PIN BOOTSTRAP (C-decision, resolving the review's operational circularity; SUPERSEDES the CONSTRUCTION-PLAN v3 SS5 'STATS=on over all 4,608 passes free at bring-up' sentence): shape (i) - the pin is derived PRE-license from the T1 8-text unpinned subset of the frozen 30-text sample at PIN_GB from measured headroom, and THAT file is the construction-phase CAMPAIGN pin (sha+PIN_GB recorded in gate-inputs.json pin.role, persisted to GCS as campaign-pin.stats with a VERIFIED re-read sha (no || true), bound per F1K-PIN-FILE-FIX.md v5); the license consumes NO assumed h_pin - its input is the realized PINNED per-item T2 timing with that exact pin (self-correcting: a weak subset pin raises measured s and shrinks headroom mechanically; disclosed residual: T1 is 8/30 of the timing sample, bounded by the +1SE reserve-inclusive cap test; underivable pin -> fail-closed STOP, unpinned REFUSED by the verdict [as amended by ASM-2516; the earlier 'T2 unpinned, recorded' fallback is WITHDRAWN]); full-corpus re-derivation happens where it is actually free (during licensed construction) and may replace the pin ONLY at the construction->pilot boundary, re-bound, never mid-phase; shape (ii) (unpinned construction) is REJECTED on measured arithmetic (unpinned 225.2 s/prefill vs the admissible [75.7,160.7] s window; construction-only unpinned ~$45 -> campaign ~$163 > $155). (5) PLUMBING - bringup-deploy (RAID0+mount via /dev/disk/by-id/google-local-nvme-ssd-*, sha-manifested bundle incl. gate-corpus, detached worker launch, guest max-life shutdown -P) and watchdog (parameterized box-side deleter, deadline + FAILED-heartbeat) are committed entrypoints; the watchdog launch stays a documented manual nohup step verified by pgrep (plan SS9: never agent-held). Bench: $0 oracle green incl. the +REPLACE fail-closed, reserve-boundary, and scaffold-status STOP cases (28/28 after the REV-B additions; the REV-A case-8a figures were re-derived by ASM-2516 to isolate the reserve delta); diffs D5-D8 apply clean on the LANDED post-seq-3 tree (re-verified, REV-B).", "rationale": "The v3-review proved the executable gate could overspend (reserve-blind GO at $154 vs $162 true exposure), license through a printed replacement SALVAGE-STOP (exit-0 --replace bug at 149.1 s/prefill), license without the dump preconditions' recorded PASS, stall on unbound plumbing, and rested on a circular pre-license 4,608-pass pin derivation. Each fix is fail-closed-only relative to the prior code (can turn GO into STOP, never the reverse), so no frozen scientific surface moves.", "backing_ref": "poc/gcp/F1K-BRINGUP-GATE-FIX.md v1 CONSOLIDATED SSA (this freeze; D5-D8 + bench evidence); poc/gpt56-review/f1k-construction-v3-review-VERDICT.md findings 2-5; f1k_gcp.py:417,:423 (pre-fix bug),:217 (reserve-blind),:337-354 (provision-only); f1k_worker.sh:182-204 (scaffolds); poc/glm52-probe/f1k-harness/opus-runs/20260717T041341Z/run-log.jsonl (vm_setup aa6504d6 / watchdog 8efa0f65, on-demand ~$0.66/h all-in); poc/gcp/probe-results/probe-results.json (unpinned 225.2 s M3; c(96)/c(384) anchors; U 176.79); m4.json h_pin_by_G [ANALYTICAL basis]; F1K-PIN-FILE-FIX.md v5 stable core (PIN=<path>; PIN_GB at bring-up; sha+PIN_GB binding; LANDED 2574c82b); ASM-2374 (windows), ASM-2497v2 (SS7 rule), ASM-2504 (geometry), ASM-2513 (REGISTERED+landed pin machinery), ASM-2514 (base gate model)", "status": "open", "owner": "designer-20", "date": "2026-07-18"}
```

## A7. Consolidated coordinator runbook **[SUPERSEDED by §B.9 — apply D1–D13, oracle 28/28; this D1–D8-only sequence would land the memo with the gate-fix review's REJECT findings open]**

```bash
cd /home/ec2-user/css/kernel/kernel-of-truth
M=poc/gcp/F1K-BRINGUP-GATE-FIX.md
for N in D1 D2 D3 D4 D5 D6 D7 D8; do
  awk -v n="$N" '$0 ~ ("^<!-- BEGIN-ARTIFACT " n " ") {f=1; next} \
      $0 ~ ("^<!-- END-ARTIFACT " n " -->") {f=0} f' "$M" | sed '1d;$d' > /tmp/$N.out
done
sha256sum /tmp/D?.out       # must match the §3 + §A4 tables exactly
# AFTER the PIN-fix seq-3 landing commit, on a clean tree:
cp /tmp/D1.out poc/gcp/f1k_bringup_gate.py && chmod 644 poc/gcp/f1k_bringup_gate.py
for D in D2 D3 D4 D5 D6 D7 D8; do git apply /tmp/$D.out; done
bash -n poc/gcp/f1k_worker.sh
python3 -m py_compile poc/gcp/f1k_gcp.py poc/gcp/f1k_bringup_gate.py
python3 poc/gcp/f1k_gcp.py gate --selftest    # expect 19 "ok:" lines + SELFTEST PASS, exit 0
python3 poc/gcp/f1k_gcp.py affordability --rate 0.17394 --s-per-prefill 149.1 --replace; echo $?  # 2
python3 poc/gcp/f1k_gcp.py affordability --rate 0.17394 --s-per-prefill 149.1; echo $?            # 3
python3 poc/gcp/f1k_gcp.py plan               # regression: DRY-PLAN OK unchanged
# ONE plain-infra commit: this memo + the four patched files + ASM-2514 + ASM-2515; registry-check green.
```

Acceptance gate: review green → extract (sha-verified) → apply D1–D8 → oracle 19/19 + the two
affordability exit-code probes → `plan` green → ONE commit (both ASM rows) → registry-check green.
If the seq-3 landing drifted beyond `f1k_gcp.py:5/:14/:49/:51/:57` + `bringup_gcp.sh:43` +
`README.md:5`, STOP and re-baseline (§0 rule) — apply-verbatim is the contract.

## A8. REV-A self-check additions (rows 20–29; every claim → verified where → tag)

| # | Claim | Verified where (this pass) | Tag |
|---|---|---|---|
| 20 | Fresh-review findings all mapped to dispositions (A0), none dropped | `f1k-construction-v3-review-VERDICT.md` read in full this pass | [MEASURED memo state] |
| 21 | Corrected table + breach points: s-window [75.68,160.69]; reserve-adjusted 152.40 s / 845.1 h; f* 1.765/1.786/1.653; blended words 97.02 at pilot 83.8 | deterministic arithmetic re-done this pass on the probe anchors | [EXTRAPOLATED on MEASURED anchors] |
| 22 | h_pin 0.7132/0.7628/0.9032 are histogram-derived → [ANALYTICAL], not realized | `m4.json /h_pin_by_G` + review F2 | [MEASURED source; tag fix] |
| 23 | --replace bug as found: exit 0 after replacement SALVAGE-STOP print; only `proj["verdict"]` tested | `f1k_gcp.py:417–428` (pre-fix bytes) read this pass; bench repro before D6 | [MEASURED] |
| 24 | Reserve-blind cap as found: `project_ledger:217` and base `project()` compute-only | code read this pass; oracle case 8a fails on pre-D5 logic | [MEASURED] |
| 25 | D5–D8 sha-pinned; apply clean on (a) current bytes + D1–D4 and (b) the simulated post-seq-3 tree; applied results byte-identical to the oracle-tested bench tree; result shas 228f5233/bd0f914a/345d1b90/b1130092 | bench runs this pass (`git apply` ×2 states ×8 artifacts; `diff -q` ×4; `sha256sum`) | [MEASURED] |
| 26 | Oracle 19/19 incl. cases 7–10; affordability probes exit 2 (--replace @149.1, names $155.15) and 3 (clean) | `gate --selftest` + subprocess probes on the applied bench tree | [MEASURED] |
| 27 | Plumbing wrappers aa6504d6/8efa0f65 hard-coded in `opus-runs/…/`; on-demand all-in ~$0.66/h | `opus-runs/20260717T041341Z/run-log.jsonl` read this pass | [MEASURED] |
| 28 | Option-(ii) rejection anchors: unpinned 225.2 s (M3); construction-only unpinned ≈ $45 → campaign ≈ $163 | `probe-results.json:7`; arithmetic this pass | [MEASURED anchor / EXTRAPOLATED] |
| 29 | ASM tail 2512; 2513 PIN-fix; 2514 base; 2515 free; both register in ONE landing commit | `assumptions.jsonl` tail read this pass | [MEASURED] |

## Summary (consolidated; C-decision in one sentence)

- GAP-1/2/3 closed (D1–D4): real-corpus stratified seeded timing sample, f measured on the full
  frozen corpora, PER-ITEM token-aware projection (per-average RETIRED, divergence proven).
- Fresh v3-review closed (D5–D8): $8 reserve charged against the caps (dollars AND hours, +1SE
  too); `--replace` and every tested projection fail closed (exit 2) and clean blended diagnostics
  exit 3; dump (a)/(b)/(c) + functional recorded PASS are hard license conjuncts; plumbing bound
  to `bringup-deploy`/`watchdog` with the manual steps named + verify commands; README layer-78
  and 3×375 echoes dead; cost basis re-derived at 83.8 w with h_pin re-tagged [ANALYTICAL].
- **C-decision:** shape (i) — the campaign pin is derived pre-license from the preregistered T1
  subset at measured PIN_GB and THAT pin (sha+PIN_GB bound) runs construction, so the license
  consumes realized pinned timing and no assumed h_pin (self-correcting; full-corpus re-derivation
  only at the construction→pilot boundary; unpinned shape (ii) rejected: 225.2 s is out-of-window).
- 19/19 $0 oracle; all eight artifacts sha-pinned, apply-verified pre- AND post-seq-3; one
  plain-infra landing commit + ASM-2514 + ASM-2515. $0 spent; nothing applied by this pass.

BRINGUP-GATE-FIX v1 DONE

---

# §B — REV-B ADDENDUM: closing the gate-fix review REJECT (delta diffs D9–D13 on top of D1–D8)

**Trigger:** `poc/gpt56-review/f1k-gate-fix-review-VERDICT.md` (the cross-model review of THIS
memo's v1+REV-A composite; overall **REJECT**). Findings **6 and 9 AGREE** — the D5/D6 license
predicate core (reserve arithmetic, dump conjuncts, `--replace` fail-closed, exit-3 diagnostic)
and the §A1 cost table are settled: **their artifact blocks and logic stay byte-stable** (D9–D13
layer on top without altering the reserve arithmetic or dump-conjunct lines; §A1 gains only the
finding-9 wall-clock column). Every other finding is closed below with deltas bench-verified
against the **REAL LANDED post-seq-3 tree** (`2574c82b`: PIN-fix v5 machinery in-tree;
`analysis/f1k.py` re-pinned `126129b9`, `frozen_sha256` `35372275` — re-confirmed from
`f1k_gcp.py:5/:14/:51` bytes this pass, not assumed from the simulation).

## B0. Verdict finding → disposition map

| Verdict # | Finding | Disposition |
|---|---|---|
| 1 | GAP-3 driver fix deferred → fails the operational bar | **§B.5 + D13** (in THIS landing; §5.3 superseded) |
| 2 | T1 pin derivation wrong (`STATS=1` overwrite; pin = last item) | **§B.1 + D9/D11** |
| 3 | Timing manifest off-by-continuation (measures t, labels t+8) | **§B.2 + D9** (+ structural oracle case 11) |
| 4 | Shape (i) not mechanically enforced or carried into construction | **§B.3 + D9/D10/D11/D12** |
| 5 | bringup-deploy dead on a fresh worker | **§B.4 + D10/D11/D12** |
| 6 | AGREE — license predicate core corrected | kept byte-stable |
| 7 | Oracle: false case 8a + "end-to-end" overstatement | **§B.6 + D9** |
| 8 | Composite supersession incomplete; stale v2 pin-authority refs | **§B.7** (map + inline kills + v5 fixes) |
| 9 | AGREE — cost table checks out; state wall-clocks | §A1 wall-clock column added (~27.1 / 31.7 / 37.7 days) |

## B1. F1 — the T1 pin now derives from the T1 UNION (verdict #2)

**Engine interface, verified from the patch bytes this pass (not assumed):**
`kae-add-path.patch:175` — `const char *stats=getenv("STATS");   /* STATS=<file> -> istogramma
uso expert a fine run */` (a PRISTINE-engine context line); `:180` (KAE_SCORE path) and `:183`
(SCORE path) both call `stats_dump(&m, stats)` — the histogram is written to **the file named by
`$STATS`**. So the old D3 (`STATS=1` in one cwd, glob-merge) made all 8 T1 runs write one file
named `1`, each overwriting the last: the pin derived from the LAST item, exactly as the review
found. No STOP needed — the `STATS=<file>` interface is confirmed; only stats_dump's
truncate-vs-append behaviour stays fetch-grade [ASM-1971], and the fix is correct under EITHER
(fresh per-run path, `rm -f` first).

**Fixed collection design (D11 worker + D9 `cmd_pinfile`):**
- one `STATS=$GATE/t1-stats/stats-<sample_id>.txt` per T1 run; `rm -f` before, `[ -s ]` asserted
  after (a run that wrote no stats ⇒ fail-closed STOP, never a shrunken union);
- an EXPLICIT manifest (`t1-stats.manifest`) of exactly the T1 files, in run order;
- `pinfile --stats-manifest` (the glob flag is GONE): fail-closed on ANY listed file
  missing/empty/malformed (the old "skip non-conforming" path is deleted — it silently shrank
  the union); aggregation [STIPULATED]: **sum of counts per (layer, expert)** over all per-item
  files (usage histograms are additive); rank by summed count, cut at PIN_GB ×
  `per_expert_bytes`;
- derivation provenance recorded and carried: `{n_stats_files, per_file: [{file, sha256,
  lines}], manifest_sha256, aggregation}` written to `<pin>.derivation.json`, passed to
  `collect --pin-derivation`, and embedded in `gate-inputs.json → pin.derivation` (thence the
  gate artifact). Oracle case 12 proves merge correctness on known counts and both fail-closed
  refusals ($0).

## B2. F2 — the timing manifest now measures what the model labels (verdict #3)

`cmd_realize` (D9): the score line is now `"%d %d <ids>" % (T, 8)` with the item's **T text ids
+ 8 appended deterministic in-vocab continuation ids** (the final text id repeated — a
timing-only continuation; the real campaign scores the few-token label). The engine therefore
processes ctxlen+contlen = **T+8 = Tp** tokens, exactly the projection model's T_i (§2.2). The
old line (`t-8, 8, <t ids>`) measured total t while the model labeled it t+8 — every
observation mislabeled by one continuation. Chosen resolution: fix the MEASUREMENT to match the
declared model (conservative: each timing run now processes 8 MORE tokens than before, never
fewer) rather than re-deriving the model in terms of total t.

**Structural enforcement, not just a fix:** `cmd_collect` (D9) re-reads every
`sample-<sid>.score` manifest and dies (`ERR_F1K_GATE_COLLECT`) unless `ctx + cont == Tp ==
len(ids)` and `cont == 8` — the CLASS of defect cannot recur silently. Oracle case 11 asserts
the identity on every manifest AND regenerates one manifest in the OLD convention and proves
collect refuses it. This is a consistency check between two independent emissions (manifest
bytes vs model labels), not a planted-timing case — it would have caught the original defect.

## B3. F3 — shape (i) mechanically enforced END-TO-END (verdict #4)

1. **Regime:** `project()` (D9) replaces `pin_regime_known` (which accepted `"unpinned"`) with
   `pin_regime_pinned` — regime `"unpinned"` now **STOPs with a REFUSED reason** (shape (ii)
   was rejected on measured arithmetic, §A3.5; oracle case 14). `collect` still RECORDS an
   unpinned regime honestly (salvage diagnostics), but it can never license. The worker (D11)
   no longer has an unpinned fallback at all: an underivable pin dies fail-closed BEFORE T2
   (running 30 unlicensable timings would only burn budget).
2. **Engagement evidence, bound to the LANDED machinery:** the worker records the verbatim
   `[PIN]` banner/marker lines per T2 run (`pin_evidence`); `project()` (D9) verifies EVERY T2
   run with the **landed driver's own grammar** — `_driver_pin_grammar()` imports
   `PIN_ARMED_RE` + `PIN_DISABLED_MARKERS` from `f1k_driver.py` (the ASM-2513 machinery landed
   at `2574c82b`), fail-closed if the import fails — and applies the same coherence rules as
   `check_pin_engagement` (`f1k_driver.py:1947`): armed banner present, pinned ≥ 1, used
   GiB > 0, used ≤ budget×1.01, budget == bound PIN_GB (1%), source == bound pin path, no
   disabled markers. ONE grammar, two consumers: the ASM-1971 fetch-grade banner-wording rider
   is discharged by aligning the DRIVER regex once at bring-up — the gate check follows
   automatically. `checks["pin_engagement_pass"]` is a hard conjunct; oracle case 13 (missing
   banner AND disabled marker both STOP).
3. **Verified pin persistence (no `|| true`):** D11 uploads `campaign-pin.stats` (+ its
   derivation sidecar), **re-reads the GCS object and requires the byte-exact sha** vs the
   licensed `PIN_SHA`; any mismatch/failure dies. A licensed pin that failed to persist is a
   dead campaign, caught on the VM, not at construction.
4. **Construction binding — explicit, never ambient:** new `f1k_gcp.py pin-fetch --gate
   bringup-gate.json --out <rundir>` (D10) fetches the GCS pin, **byte-verifies it against the
   GREEN artifact's `pin.pin_file_sha256`** (GREEN + pinned-bringup required), and prints the
   exact `export PIN=<path>` / `export PIN_GB=<licensed value>` lines; README step 5 (D12) makes
   this the FIRST construction action — the carrier builder never inherits whatever `PIN` the
   environment happened to hold (`build_carriers.py:634` lineage).
   **[SUPERSEDED in part by §C.1 — rereview #3 proved the printed exports were never
   CONSUMED (no eval/source, no builder args) and no engagement check ran at construction.
   REV-C: the `guard` wrapper (D14) sets the child env itself from the byte-verified pin and
   PROBES engagement pre-spend; pin-fetch remains the fetch/verify step.]**
5. ~~**Construction→pilot full-corpus re-derivation — concrete (D12)**~~ **[WITHDRAWN in
   REV-C — rereview #3 proved this STRUCTURALLY IMPOSSIBLE through the unchanged sha-pinned
   builder: it launches ONE 48-row engine batch per concept (96 processes,
   `build_carriers.py:852/:960`), so 4,608 per-PASS `STATS` files cannot exist, and a single
   ambient `STATS` path would hold the LAST batch only (truncate-vs-append fetch-grade
   ASM-1971 — the F1 defect class). REV-C decision (§C.1): the LICENSED bring-up pin runs the
   WHOLE campaign; `campaign-pin-rebind.json` is REMOVED (it had no consumer, and the REV-C
   driver refuses any campaign pin ≠ the gate artifact's, making a rebind unreachable);
   re-derivation is DEFERRED behind the seq-4 builder re-freeze bead `kernel-of-truth-8cpm`,
   NOT on the critical path.]**
6. **"Self-correcting" repriced + mitigation (§A3.3 amended in place):** the +1SE band bounds
   the SAMPLING error of the chosen 30-text sample ONLY — NOT selection bias (T1 ⊂ T2, 8/30
   optimistic-direction) and NOT unseen-tail behaviour (a pin can pass the 30-item gate yet
   underperform over 4,608; that spend is unrecoverable after the fact). Adopted mitigation
   [STIPULATED, ASM-2516]: **early-abort checkpoints** — `f1k_bringup_gate.py checkpoint
   --gate <GREEN artifact> --tokens <tokens-full.jsonl> --n-done N --elapsed-s S` at n_done ∈
   {200, 1024, 2304}: re-projects the WHOLE campaign with the licensed knots re-levelled by
   realized/predicted construction throughput (ratio sanity (0, 10]), STOPs (exit 2) on any
   reserve-inclusive breach at central OR +1SE; the artifact's realized hours/$ figures ARE the
   `cost.{usd_spent_prior, construction_instance_hours}` basis the **landed Ledger REQUIRES
   fail-closed** (never silent zeros) — a breach never reaches a pilot spawn. First exposure
   ≈ 200 × 137.2 s ≈ 7.6 h ≈ **$1.33** [EXTRAPOLATED at the f=1.45 row], vs $113+ full
   construction. Oracle case 15 (CONTINUE at ratio 1.0; STOP exit-2 at 1.35).
   **[AMENDED in REV-C (§C.1) — rereview #3: the standalone checkpoint was not invoked by
   construction, accepted any n_done, and fed nothing into `config.cost`. REV-C: schedule
   re-frozen at the OBSERVABLE concept boundaries {240, 1056, 2304} (the pinned builder
   checkpoints per 48-pass concept — ASM-2517 amends ASM-2516(4)), off-schedule n_done
   REFUSED, the `guard` invokes `checkpoint_eval` IN-PROCESS and kills the builder on breach,
   and `config-cost` transfers the guard-final realized figures into the Ledger basis. First
   exposure repriced ≈ 240 × 137.2 s ≈ 9.1 h ≈ **$1.59**.]**

## B4. F4 — `bringup-deploy` runs on a FRESH worker (verdict #5)

- **Dependencies, chosen + justified:** stay with **gsutil** (install `google-cloud-cli` via
  apt when absent, VERIFY, fail-closed in both the remote prep (D10) and the worker preflight
  (D11)) rather than switching to curl + signed URLs: the worker performs MANY dynamic writes
  (estate rsync mirror, heartbeats every step, whole-gate-dir mirrors, campaign-pin
  persistence) — per-object signed-URL minting is unworkable, and the VM's service account
  auths gsutil natively. `python3-pip` likewise installed+verified (tokenizers, HF staging).
- **`real-checks.sh` contract met (was dead on arrival):** the worker (D11) clones a fresh
  PRISTINE colibri at the pinned commit (`bringup_gcp.sh:24` `a78a06fc…`; the bringup tree is
  PATCHED and cannot serve), exports `COLIBRI_TREE` into the invocation
  (`real-checks.sh:43` requires it; `:47` re-verifies the pristine `c/glm.c` blob fail-closed),
  and symlinks `kae-patch-draft` to real-checks' expected `../../kae-patch-draft` location
  (`real-checks.sh:37`), asserting the patch file is reachable before invoking.
- **RAID by STATE:** both the remote prep (D10) and the worker preflight (D11) now use
  `mountpoint -q` (never `[ -d ]`): after a reboot, `/dev/md0` is re-`--assemble`d and
  re-mounted; `mkfs.ext4` runs ONLY on first creation; a bare `/mnt/nvme` directory on the boot
  disk can never silently receive the ~384 GB estate.
- **Failure-visible detached launch:** the bundle gains a generated `f1k_launch.sh` (D10) and
  the launch goes through it: ANY nonzero worker exit — including `set -e` deaths that bypass
  `die()` and its heartbeat — writes a `FAILED` heartbeat to GCS that the `watchdog`
  (`'"FAILED'` match, unchanged) acts on promptly; no failure waits out the 900-min max-life.

## B5. F5 — GAP-3: the driver-side fix is IN this landing (verdict #1; D13)

**Re-located against the landed tree** (the PIN-fix shifted lines; the verdict's `:2865/:2890`
were pre-landing): the addendum-(7) projection path is `phase_pilot` section 4,
`f1k_driver.py:3348–3497` landed (`pilot_s = ledger.phase_seconds("pilot")` :3351;
`def projection` :3360-3364 — one blended `s_per_prefill` × `(n_main + n_guard)`;
`affordable = proj <= USD_CAP` :3384 — dollars only, reserve-blind). D13 replaces exactly that
seam and **touches NO landed PIN-fix hunk** ([MEASURED]: zero added/removed D13 lines contain
`attested_pinning`/`check_pin_engagement`/`validate_pinning`/spend-start tokens; hunks sit at
:269 (constants), :2643 (new `Add7Model` before `check_addendum_pinning`, insertion-only),
:3348–:3497 (the projection seam; the `attested_pinning(ledger)` line is unchanged context),
:3669/:3779 (mock fixtures)).

**ONE projection model, stated once (ASM-2514/2515), used by both seams:** `Add7Model` consumes
the licensed `bringup-gate.json` (isotonic knots + cont addend + SE rule) and the gate run's
`tokens-full.jsonl` sidecar — both paths + sha256s REQUIRED in `config.affordability`,
sha-verified fail-closed (`ERR_F1K_AFFORD`); a non-REAL (mock) artifact requires `_allow_mock`
and never licenses. The seam re-levels the frozen s_hat(T) shape by **kappa = realized pilot
s/prefill ÷ model-predicted pilot blend** (recorded; bounds [0.5, 2.0] fail-closed on a REAL
artifact — outside means the model does not transfer, maintainer surface), then projects **per
item**: Σ over remaining test items (template passes × s_hat(Tp[main-tmpl:id]) + d3 pass ×
s_hat(Tp[main-d3:id]) unless deferred) + guard items × guard passes × s_hat(Tp[guard:id]) — at
central AND +1SE knots. **Reserve-inclusive comparison** (same rule as the gate, ASM-2515/2516):
`usd + 8 ≤ 155` AND `hours + 8/rate ≤ 900` at BOTH bands; the §R6 degradation order
(REPLACE-defer → d3-defer) now triggers off the reserve-inclusive breach; missing token keys,
above-max-knot T, and absent config block all fail closed — no silent fallback to the blended
average (which is still printed as `per_average_RETIRED_usd`, audit-only).

**Disclosed deviation from §5.3's sketch [STIPULATED]:** §5.3 said "knots REFIT from the
pilot's realized per-config timings" — the landed ledger records per-phase AGGREGATES only
(`Ledger.add`, `f1k_driver.py:1714`; no per-item campaign timings exist), so a refit is not
implementable from landed data. The kappa re-levelling (shape frozen, level realized) is the
faithful implementable form; the +1SE band re-levels with it.

**Bench (all $0):** the driver's own emission-surface oracle — `python3 f1k_driver.py --mock`
on the FULLY-APPLIED (D1–D13) tree — is **green end-to-end: exit 0, 23 [PASS] lines, `MOCK
VALIDATION PASS`**, incl. the official log-append→verdict-gen→pinned-analysis seam and the
tamper case; `addendum-7-affordability.json` now carries `projection_rev_b` (kappa 0.0369 in
the mock — unbounded under `_allow_mock`; a real artifact enforces [0.5, 2.0]) and
`pilot-gates.json → affordability_gate` carries the reserve-inclusive central/+1SE figures
[MEASURED]. `gen_mock_fixtures` emits the mock tokens-full + mock gate artifact + the
`config.affordability` block, so the sha-verify + per-item + reserve path is exercised, per the
round-4 lesson (the untouched-mock-as-oracle discipline). The REAL campaign config gains the
same block pointing at the landed gate run's artifacts (shas from `bringup-gate.json`) —
REQUIRED, fail-closed.

## B6. F6 — oracle honesty (verdict #7)

- **Case 8a re-derived to ISOLATE the reserve delta:** the REV-A case planted $149 → realized
  central $150.22 / +1SE $156.33, so the OLD rule already STOPped on the +SE band (the
  reviewer's recomputation — confirmed). Now planted $146.6 at rate 0.20 → realized **central
  $147.80 AND +1SE $153.81, BOTH ≤ $155 raw** (and hours 739/+SE ≤ 900): the OLD reserve-blind
  rule GOes on every band it tested, while central + $8 = $155.80 breaches → STOP with a
  RESERVE-named reason. The case now asserts all four conditions in code ([MEASURED] figures
  from the bench run) — the reserve delta ALONE flips the verdict.
- **New cases (all $0):** 11 (F2 structural consistency: every manifest ctx+cont == Tp; an
  OLD-convention manifest refused), 12 (F1 merge correctness: 3 per-item files with known
  counts → merged pin == the expected (layer,expert) sum union; missing-file and
  malformed-line refusals), 13 (engagement: no banner / disabled marker → STOP), 14 (regime
  `unpinned` → STOP), 15 (checkpoint: CONTINUE at ratio 1.0, exit-2 STOP at 1.35).
- **Honest retitle:** the selftest banner and docstring now state exactly which seams the $0
  oracle exercises (projection/license logic incl. reserve + conjuncts + refusals, sampling
  rule mechanics, per-item stats merge, manifest-vs-model consistency, early-abort checkpoint)
  and which it CANNOT (real engine timer/STATS/PIN semantics, real tokenizer, GCS transfer, VM
  deploy, real corpus bytes — VM path only). The phrase "end-to-end mock oracle" is gone.
- **Count:** `gate --selftest` = **28/28 ok** on the applied landed tree ([MEASURED], both the
  edited bench and the fresh-chain re-apply).

## B7. F7 — composite SUPERSESSION MAP (verdict #8) — read this before acting on §0–§A

Inline kills already applied above (marked ~~struck~~ **[SUPERSEDED]** in place): the §2.4
`STATS=1`/unpinned-fallback bullet; the §2.6 reserve-blind nine-conjunct verdict text; the
§5.3 separate-landing disposition; the base NEXT-ACTION block; §A3.3's unpriced
"self-correcting"; §A7's D1–D8-only runbook. Pin authority: every operative reference is
**`F1K-PIN-FILE-FIX.md` v5** (landed `2574c82b`); the remaining literal "v2" strings inside
the D1/D3/D5 artifact code blocks are historical bytes (sha-pinned; editing them would break
extraction) — the D9/D11 deltas rewrite those comments in the APPLIED files to v5.

| Base/REV-A claim | Status | Successor |
|---|---|---|
| Header "v1 CONSOLIDATED… awaiting review" | superseded | REV-B header (edited in place) |
| Chain: "PIN-FILE-FIX v2 (seq-3, in re-review)" | superseded | v5, LANDED `2574c82b` (edited) |
| §0 sequencing "separate commit AFTER seq-3" risk language | discharged | seq-3 landed; §B verified on real bytes |
| §2.3 sampling rule + seed + bins | **stands** | (realization bins unchanged by REV-B) |
| §2.3/§3 D1 manifest emission `(T−8, 8, T ids)` | superseded | §B.2 / D9: `(T, 8, T+8 ids)` + structural check |
| §2.4 T1 `STATS=1` + glob harvest + unpinned fallback | superseded | §B.1/§B.3, D9/D11 (marked inline) |
| §2.6 estimator (knots, PAVA, ±1SE, fail-closed above max) | **stands** | consumed verbatim by D13's `Add7Model` |
| §2.6 nine-conjunct reserve-blind verdict text | superseded | §A2 + §B.3 rule (marked inline) |
| §2.7 artifact schema | extended | + `pin.pin_file_path/derivation`, `pin_engagement`, regime narrowed |
| §3 D1–D4, §A4 D5–D8 artifacts + shas | **stand byte-for-byte** | applied FIRST; operative only with D9–D13 on top |
| §4.1 "$0 oracle 14/14"; §A4 "19/19" | historical | final oracle = **28/28** (§B.6) |
| §4.2 / §A7 runbooks | superseded | **§B.9** (the ONE liftable sequence) |
| §A4 applied-result shas `bd0f914a`/`b1130092` | superseded | landed-tree chain: post-D8 `04927690`/`d8cdc611` (seq-3 rewrote those files' pinned lines); post-D13 finals in §B.8 |
| §5.2 ASM-2514 / §A6 ASM-2515 texts | amended in place (pre-registration) | register in the REV-B landing commit as amended |
| §5.3 GAP-3b "separate review-gated landing" | superseded | §B.5 / D13, same commit (marked inline) |
| base NEXT-ACTION "liftable, D1–D4, 14/14" | killed | §B.9 (marked inline) |
| §A0 F5 row / §A3 C-decision shape (i) | **stands IN PART, now ENFORCED** — only the bring-up-pin-IS-the-campaign-pin half; the re-derivation/boundary-swap half is **withdrawn** (REV-C, memo:2568; this row said "stands" unqualified and was corrected in REV-E — round-4 verdict 6) | §B.3 (regime refusal, engagement, verified persistence, pin-fetch) + §C.1 (guard: env binding + pre-spend probe; rebind record REMOVED; the licensed pin runs the WHOLE campaign) |
| §A3.3 "self-correcting" (unpriced) | repriced | §B.3.6 + early-abort checkpoint (marked inline) |
| §A3.4 "re-derivation during construction" (prose) | **withdrawn (REV-C)** | rereview #3: prose-only AND structurally impossible through the pinned builder; DEFERRED to seq-4 bead `kernel-of-truth-8cpm`; rebind record REMOVED (§C.1) |
| §A3.5 shape-(ii) rejection arithmetic | **stands** | now mechanical (oracle case 14) |
| §A5 plumbing code-vs-manual table | extended | + deps verify, mountpoint state, `f1k_launch.sh` rows (all CODE, D10/D11) |
| §A4 case 8a "old rule would GO" | superseded (was false: old rule STOPped on +SE) | §B.6 re-derived figures |
| ASM-2515 item (4) "underivable pin → T2 unpinned" | withdrawn | amended text + ASM-2516 |
| Summary + "BRINGUP-GATE-FIX v1 DONE" line | superseded | §B.12 + the REV-B final line |
| ASM-2515 vs ASM-2513/2514 reconciliation | done | amended ASM-2515 opening (ASM-2513 REGISTERED+landed; 2514 same-commit; 2516 amends) |

## B8. Delta artifacts D9–D13 (apply AFTER D1–D8, in order; sha-pinned; bench-verified on the LANDED tree)

| # | Target | Kind | sha256 of the artifact below |
|---|---|---|---|
| D9 | `poc/gcp/f1k_bringup_gate.py` (post-D1+D5) | unified diff | `a07ae86e29a971925c3c81b8f6eafdbf7d15e035907e7eba7dd0676c22c91099` |
| D10 | `poc/gcp/f1k_gcp.py` (post-D2+D6) | unified diff | `e3611c4f3f801e8fb2c9ecf57634fc22794b764c8c4cffc66c407605270e77dc` |
| D11 | `poc/gcp/f1k_worker.sh` (post-D3+D7) | unified diff | `7401ad53d667dbb3c746cef042f379c123da1ec8b795ad22306f2c48ed568262` |
| D12 | `poc/gcp/README.md` (post-D4+D8) | unified diff | `0fb929fcd606f8a1840d59e1a4ab278389a5d3616d9b2bfb36c89618cf852c20` |
| D13 | `poc/glm52-probe/f1k-harness/f1k_driver.py` (post-Dseq-3 landing) | unified diff | `88e9380416845e64adb258ae020e5d6f3b14df93cd6de98976b22c5840a44a1c` |

Bench evidence [MEASURED, /tmp bench this REV-B pass — no repo file touched beyond this memo]:

- **Landed-tree chain:** from the CURRENT repo bytes (post-`2574c82b`), D1–D8 apply clean
  (extract-by-sha re-verified: all 8 §3/§A4 shas match) and reproduce post-D8 result shas
  `f1k_bringup_gate.py 228f5233…` / `f1k_worker.sh 345d1b90…` (= the REV-A claims) and
  `f1k_gcp.py 04927690…` / `README.md d8cdc611…` (≠ REV-A's `bd0f914a`/`b1130092` — expected:
  seq-3 rewrote those two files' pinned docstring/hash lines, exactly the simulated deltas).
  Then D9–D13 apply clean in order. A SECOND fresh copy of the landed bytes, taken through the
  full D1→D13 chain, is **byte-identical** to the tested bench tree on all five files (`cmp`
  ×5). Applied-tree result shas: `f1k_bringup_gate.py 8824705b…`, `f1k_gcp.py cd7a5fbd…`,
  `f1k_worker.sh 30e1ca18…`, `README.md 20315815…`, `f1k_driver.py 49b2ab3b…`.
- `py_compile` (gate, gcp, driver) + `bash -n` (worker) clean on the applied tree.
- **$0 oracle 28/28** (`f1k_gcp.py gate --selftest` AND direct `selftest`, both benches) incl.
  the re-derived case 8a ($147.80/$153.81/$155.80) and cases 11–15; honest-scope banner.
- **Driver $0 --mock green** on the applied tree: exit 0, 23 [PASS], `MOCK VALIDATION PASS`;
  `projection_rev_b` + reserve-inclusive `affordability_gate` emitted (kappa 0.0369, mock).
- Probes: `affordability --rate 0.17394 --s-per-prefill 149.1 --replace` → exit 2;
  without `--replace` → exit 3; `plan` → `DRY-PLAN OK` (pins verified) on the applied tree.
- D13 PIN-fix-hunk avoidance: zero modified lines carry the landed pin-machinery tokens
  (context-only overlap; hunk map in §B.5).
- No `PINS`/`FROZEN_SHA256` edits anywhere in D9–D13; neither touched file is sha-pinned
  (§1 re-confirmed on the landed tree) → the landing stays plain infra.

### B8.1 D9 — `poc/gcp/f1k_bringup_gate.py` gate machinery delta (F1 merge + F2 manifest + F3 regime/engagement/checkpoint + F6 oracle)

<!-- BEGIN-ARTIFACT D9 f1k_bringup_gate.py.rev-b.diff sha256=a07ae86e29a971925c3c81b8f6eafdbf7d15e035907e7eba7dd0676c22c91099 -->
```diff
diff --git a/poc/gcp/f1k_bringup_gate.py b/poc/gcp/f1k_bringup_gate.py
index 780b70c..ead8113 100644
--- a/poc/gcp/f1k_bringup_gate.py
+++ b/poc/gcp/f1k_bringup_gate.py
@@ -21,11 +21,16 @@ SUBCOMMANDS (control box = $0; VM = on the bring-up box):
   spec     ($0, control box) witness the sampling rule + corpus shas
   fcount   (VM) tokenize the frozen corpora -> per-item T + measured f
   realize  (VM) apply the frozen sampling rule -> timing sample manifests
-  pinfile  (VM) merge engine usage stats -> bring-up pin file at PIN_GB
+  pinfile  (VM) fail-closed merge of the EXPLICIT per-item T1 stats files
+           (STATS=<file>, one per run) -> bring-up pin file at PIN_GB
   collect  (VM) merge timing results -> gate-inputs.json (no verdict here)
   project  (control box; use `f1k_gcp.py gate`) -> bringup-gate.json GREEN/STOP
-  selftest ($0) end-to-end mock oracle: GREEN, STOP long-tail (the review
-           finding-3 divergence proven), f-branch both sides, fail-closed
+  checkpoint (runner, during licensed construction) early-abort
+           re-projection from realized construction throughput [REV-B]
+  selftest ($0) mock oracle — HONEST SCOPE [REV-B]: projection/license
+           logic, sampling rule, per-item stats merge, manifest-vs-model
+           consistency, engagement/regime refusals, early-abort; NOT the
+           real engine/tokenizer/GCS/VM (those exist only on the VM path)
 
 Zero non-stdlib deps on the control box; the VM path shells out to the
 pinned kot-f1k-tok/1 wrapper (tok_glm52.py) for all real tokenization.
@@ -319,13 +324,22 @@ def cmd_realize(args):
     outdir = Path(args.out)
     outdir.mkdir(parents=True, exist_ok=True)
     # one run_score manifest per sampled text (per-item engine timer)
+    # [REV-B F2, gate-fix review #3] ctx = the FULL text (all T ids), cont =
+    # CONT_TOKENS appended deterministic in-vocab ids (the final text id
+    # repeated — timing-only continuation; the real campaign scores the
+    # few-token label). The engine therefore processes ctxlen + contlen =
+    # T + 8 = Tp tokens — EXACTLY the projection model's T_i. The old line
+    # (`t - CONT_TOKENS, CONT_TOKENS, <t ids>`) measured total t while the
+    # model labeled it t+8: every observation mislabeled by one
+    # continuation. cmd_collect re-checks this structurally (fail-closed).
     for c in chosen:
         t = c["T"]
-        if t < CONT_TOKENS + 2:
-            die("F1K_GATE_SAMPLE", "%s: T=%d too short for cont=%d"
-                % (c["key"], t, CONT_TOKENS))
-        line = "%d %d %s" % (t - CONT_TOKENS, CONT_TOKENS,
-                             " ".join(map(str, c["ids"])))
+        if t < 2:
+            die("F1K_GATE_SAMPLE", "%s: T=%d too short to score"
+                % (c["key"], t))
+        cont_ids = [c["ids"][-1]] * CONT_TOKENS
+        line = "%d %d %s" % (t, CONT_TOKENS,
+                             " ".join(map(str, c["ids"] + cont_ids)))
         (outdir / ("sample-%s.score" % c["sample_id"])).write_text(line + "\n")
     # T1 (unpinned stats/margin) subset: evenly spaced ranks EXCLUDING the
     # global max (cost control; the max is timed pinned in T2 regardless)
@@ -357,29 +371,51 @@ def cmd_realize(args):
 # bring-up pin file from engine usage stats ([MEASURED] accum20.stats format)
 # ---------------------------------------------------------------------------
 def cmd_pinfile(args):
-    import glob as g
-    merged = {}
-    files_ok = 0
-    for path in sorted(g.glob(args.stats_glob)):
+    """[REV-B F1, gate-fix review #2] EXPLICIT per-item merge — never a
+    permissive glob. The engine interface is STATS=<file> (kae-add-path.patch
+    :175/:180/:183, verified this pass: `stats=getenv("STATS")` then
+    `stats_dump(&m, stats)` writes THE named file), so each T1 run writes
+    its OWN stats file and the pin derives from a fail-closed merge over an
+    explicit manifest: any listed file missing/empty/malformed -> die (the
+    old glob 'skip non-conforming' path silently shrank the union). The
+    stats_dump truncate-vs-append semantics stay fetch-grade [ASM-1971]; a
+    FRESH per-run path (worker rm's before each run) is correct under
+    EITHER. Aggregation [STIPULATED]: SUM of counts per (layer, expert)
+    over ALL per-item files (usage histograms are additive). Derivation
+    provenance (n files, per-file sha256+lines, manifest hash) is recorded
+    beside the pin and travels into the gate artifact."""
+    paths = [ln.strip() for ln in open(args.stats_manifest, encoding="utf-8")
+             if ln.strip()]
+    if not paths:
+        die("F1K_GATE_PIN", "stats manifest %s lists no files"
+            % args.stats_manifest)
+    merged, prov = {}, []
+    for path in paths:
+        if not Path(path).is_file() or os.path.getsize(path) == 0:
+            die("F1K_GATE_PIN", "per-item stats file MISSING/EMPTY: %s — "
+                "the pin never derives from a partial T1 union "
+                "(fail-closed; no skipping)" % path)
+        triples = []
         try:
-            triples = []
             for ln in open(path, encoding="utf-8", errors="strict"):
                 parts = ln.split()
                 if not parts:
                     continue
                 if len(parts) != 3:
-                    raise ValueError("non-triple line")
+                    raise ValueError("non-triple line %r" % ln[:60])
                 l, e, c = (int(x) for x in parts)
                 triples.append((l, e, c))
-            for l, e, c in triples:
-                merged[(l, e)] = merged.get((l, e), 0) + c
-            files_ok += 1
-        except (ValueError, UnicodeDecodeError):
-            print("pinfile: skipping non-conforming %s" % path)
-    if files_ok == 0 or not merged:
-        die("F1K_GATE_PIN", "no conforming '<layer> <expert> <count>' stats "
-            "under %s — pin underivable; T2 must run UNPINNED (conservative, "
-            "recorded; never silently pinned)" % args.stats_glob)
+        except (ValueError, UnicodeDecodeError) as ex:
+            die("F1K_GATE_PIN", "non-conforming stats file %s (%s) — "
+                "'<layer> <expert> <count>' triples required "
+                "(accum20.stats format [MEASURED]); fail-closed, never "
+                "skipped" % (path, ex))
+        if not triples:
+            die("F1K_GATE_PIN", "stats file %s has no triples" % path)
+        for l, e, c in triples:
+            merged[(l, e)] = merged.get((l, e), 0) + c
+        prov.append({"file": os.path.basename(path),
+                     "sha256": sha256_file(path), "lines": len(triples)})
     budget = args.pin_gb * 1e9
     ranked = sorted(merged.items(), key=lambda kv: (-kv[1], kv[0]))
     out, used = [], 0.0
@@ -389,9 +425,19 @@ def cmd_pinfile(args):
         used += PER_EXPERT_BYTES
         out.append("%d %d %d" % (l, e, c))
     Path(args.out).write_text("\n".join(out) + "\n")
+    derivation = {
+        "n_stats_files": len(prov), "per_file": prov,
+        "manifest_sha256": hashlib.sha256(
+            "".join("%s %s\n" % (p["sha256"], p["file"])
+                    for p in prov).encode()).hexdigest(),
+        "aggregation": "sum of counts per (layer, expert) over ALL "
+                       "per-item T1 stats files [REV-B F1; fail-closed "
+                       "on any missing/empty/malformed file]"}
+    Path(str(args.out) + ".derivation.json").write_text(
+        json.dumps(derivation, indent=2))
     print(json.dumps({"pin_file": args.out, "experts": len(out),
                       "gb_used": round(used / 1e9, 2), "pin_gb": args.pin_gb,
-                      "stats_files_merged": files_ok,
+                      "derivation": derivation,
                       "sha256": sha256_file(args.out)}))
     return 0
 
@@ -421,6 +467,25 @@ def cmd_collect(args):
     if missing:
         die("F1K_GATE_COLLECT", "T2 timing missing for %s (fail-closed: "
             "partial samples never project)" % ",".join(missing))
+    # [REV-B F2] STRUCTURAL manifest-vs-model consistency (the class of
+    # defect gate-fix review #3 found): for every sampled text the score
+    # manifest's ctxlen + contlen (= the token count the engine actually
+    # processes) must EQUAL the projection model's Tp for that item.
+    mandir = Path(args.sample).parent
+    for e in sample["entries"]:
+        mpath = mandir / ("sample-%s.score" % e["sample_id"])
+        if not mpath.is_file():
+            die("F1K_GATE_COLLECT", "score manifest missing: %s" % mpath)
+        parts = mpath.read_text(encoding="utf-8").split()
+        ctx, cont, ids = int(parts[0]), int(parts[1]), parts[2:]
+        if ctx + cont != e["Tp"] or len(ids) != e["Tp"] \
+                or cont != CONT_TOKENS:
+            die("F1K_GATE_COLLECT",
+                "%s manifest measures ctx+cont=%d (ids %d) but the "
+                "projection model labels it Tp=%d — the timing "
+                "observation would be mislabeled by a continuation "
+                "(REV-B F2 structural check; fail-closed)"
+                % (e["sample_id"], ctx + cont, len(ids), e["Tp"]))
     # compact per-prefill inventory for the control-box projection
     inv_t = [[e["pop"], e["m"], e["T"] + CONT_TOKENS] for e in
              (json.loads(l) for l in open(tokdir / "tokens-full.jsonl"))]
@@ -440,14 +505,19 @@ def cmd_collect(args):
                        "the on-demand bring-up VM's rate",
         "pin": {"pin_file_sha256": args.pin_sha or None,
                 "pin_gb": float(args.pin_gb) if args.pin_gb else None,
+                "pin_file_path": args.pin_path or None,
                 "regime": args.pin_regime,
+                "derivation": json.loads(Path(args.pin_derivation)
+                                         .read_text(encoding="utf-8"))
+                if args.pin_derivation else None,
                 "role": "campaign pin for the CONSTRUCTION phase (fix memo "
                         "SSA3 C-decision): construction runs PIN=<this "
                         "file>; re-derivation from full-corpus STATS only "
                         "at the construction->pilot boundary, re-bound "
-                        "there, never mid-phase",
+                        "there via a coordinator-committed rebind record, "
+                        "never mid-phase",
                 "note": "derivation + truthful-attestation mechanics: "
-                        "F1K-PIN-FILE-FIX.md v2 (cross-reference)"},
+                        "F1K-PIN-FILE-FIX.md v5 (cross-reference)"},
         "dump_gate": {"a": args.dump_a, "b": args.dump_b, "c": args.dump_c,
                       "functional_inertness": args.functional,
                       "rule": "recorded worker/runner statuses; the license "
@@ -536,6 +606,68 @@ def build_knots(inputs):
     return knots, pooled, repaired
 
 
+def _driver_pin_grammar():
+    """[REV-B F3] BIND to the LANDED driver's pin-engagement evidence
+    grammar (f1k_driver.py PIN_ARMED_RE + PIN_DISABLED_MARKERS, the
+    ASM-2513 machinery landed at 2574c82b) — the gate never re-invents a
+    parallel evidence format. The banner WORDING stays fetch-grade
+    [ASM-1971]: if the real engine's pin report differs, the runner aligns
+    the DRIVER regex in one recorded run-log amendment and this check
+    follows automatically (one grammar, two consumers). Import fail-closed."""
+    import importlib.util
+    p = Path(__file__).resolve().parents[1] / "glm52-probe" \
+        / "f1k-harness" / "f1k_driver.py"
+    if not p.is_file():
+        die("F1K_GATE_PIN_EVIDENCE", "landed driver not found at %s — "
+            "cannot bind the pin-engagement grammar" % p)
+    spec = importlib.util.spec_from_file_location("kot_f1k_driver_pin", p)
+    mod = importlib.util.module_from_spec(spec)
+    try:
+        spec.loader.exec_module(mod)
+    except Exception as ex:                                # noqa: BLE001
+        die("F1K_GATE_PIN_EVIDENCE", "driver import failed (%s) — the "
+            "engagement grammar is unavailable; fail closed" % ex)
+    return mod.PIN_ARMED_RE, mod.PIN_DISABLED_MARKERS
+
+
+def check_engagement(inputs):
+    """[REV-B F3] POSITIVE pin-engagement evidence per T2 run, mirroring
+    the landed check_pin_engagement coherence rules: an armed banner must
+    exist in the run's recorded stderr evidence, pinned>=1 experts, used
+    GiB > 0, used <= budget*1.01, budget == the bound PIN_GB (1%), source
+    == the bound pin path; any disabled marker refuses. Returns (ok,
+    problems)."""
+    armed_re, disabled_markers = _driver_pin_grammar()
+    pin = inputs["pin"]
+    gb = pin.get("pin_gb")
+    path = pin.get("pin_file_path")
+    problems = []
+    for r in inputs["t2_pinned_runs"]:
+        ev = r.get("pin_evidence") or ""
+        sid = r.get("sample_id", "?")
+        bad = [m for m in disabled_markers if m in ev]
+        if bad:
+            problems.append("%s: pinning DISABLED marker %s" % (sid, bad))
+            continue
+        m = armed_re.search(ev)
+        if not m:
+            problems.append("%s: no armed banner" % sid)
+            continue
+        n_pinned, gb_used = int(m.group(1)), float(m.group(2))
+        gb_budget, src = float(m.group(3)), m.group(4)
+        if n_pinned < 1 or not gb_used > 0.0:
+            problems.append("%s: incoherent counters (n=%d, %.3f GiB)"
+                            % (sid, n_pinned, gb_used))
+        elif gb is None or abs(gb_budget - gb) > 0.01 * max(1.0, gb) \
+                or gb_used > gb_budget * 1.01:
+            problems.append("%s: budget %.3f/used %.3f vs bound PIN_GB=%r"
+                            % (sid, gb_budget, gb_used, gb))
+        elif path and src != path:
+            problems.append("%s: armed from %r != bound pin %r"
+                            % (sid, src, path))
+    return not problems, problems
+
+
 def project(inputs, frozen, replace=False, out_path=None):
     tc = inputs["token_counts"]
     if tc["tokenizer"]["mode"] != "REAL" and not inputs.get("_allow_mock"):
@@ -590,9 +722,22 @@ def project(inputs, frozen, replace=False, out_path=None):
         "prefills_ge_min": prefills >= frozen["prefills_min"],
         "tokenizer_real": tc["tokenizer"]["mode"] == "REAL"
             or bool(inputs.get("_allow_mock")),
-        "pin_regime_known":
-            inputs["pin"]["regime"] in ("pinned-bringup", "unpinned"),
+        # [REV-B F3, gate-fix review #4] shape (i) ENFORCED: the gate
+        # REFUSES regime "unpinned" — shape (ii) was REJECTED on measured
+        # arithmetic (SSA3.5: unpinned 225.2 s vs the [75.7,160.7] s
+        # admissible window), so an unpinned regime can never license.
+        "pin_regime_pinned":
+            inputs["pin"]["regime"] == "pinned-bringup",
     }
+    # [REV-B F3] pin-ENGAGEMENT evidence conjunct (bound to the landed
+    # driver grammar): only meaningful under the pinned regime; a refused
+    # regime already STOPs above.
+    if checks["pin_regime_pinned"]:
+        eng_ok, eng_problems = check_engagement(inputs)
+    else:
+        eng_ok, eng_problems = False, ["regime %r never licenses"
+                                       % (inputs["pin"]["regime"],)]
+    checks["pin_engagement_pass"] = eng_ok
     reasons = []
     if not checks["f_le_threshold"]:
         reasons.append("measured blended f %.4f > %.2f — §7 STOP branch: "
@@ -632,8 +777,19 @@ def project(inputs, frozen, replace=False, out_path=None):
     if not checks["prefills_ge_min"]:
         reasons.append("prefills %d < %d" % (prefills,
                                              frozen["prefills_min"]))
-    if not checks["pin_regime_known"]:
-        reasons.append("unknown pin regime %r" % (inputs["pin"]["regime"],))
+    if not checks["pin_regime_pinned"]:
+        reasons.append("pin regime %r REFUSED — shape (i) is the decided "
+                       "and ONLY licensable regime (ASM-2515/ASM-2516; "
+                       "shape (ii) rejected on measured arithmetic); an "
+                       "underivable pin is a mandatory maintainer surface, "
+                       "never an unpinned license"
+                       % (inputs["pin"]["regime"],))
+    if not checks["pin_engagement_pass"]:
+        reasons.append("pin-ENGAGEMENT evidence failed for the bound pin "
+                       "sha/PIN_GB (%s) — an armed banner per T2 run is "
+                       "REQUIRED (landed ASM-2513 grammar); a licensed "
+                       "timing basis is never taken on trust"
+                       % "; ".join(eng_problems[:4]))
     verdict = "GREEN" if all(checks.values()) else "STOP"
     art = {
         "schema": SCHEMA,
@@ -662,6 +818,14 @@ def project(inputs, frozen, replace=False, out_path=None):
             "cont_tokens_addend": CONT_TOKENS,
         },
         "pin": inputs["pin"],
+        "pin_engagement": {
+            "pass": eng_ok, "problems": eng_problems,
+            "rule": "per-T2-run armed-banner evidence parsed with the "
+                    "LANDED driver grammar (PIN_ARMED_RE/ASM-2513; "
+                    "wording fetch-grade ASM-1971, one grammar for both "
+                    "consumers): pinned>=1, used GiB>0, used<=budget*1.01, "
+                    "budget==bound PIN_GB (1%), source==bound pin path; "
+                    "regime unpinned REFUSED outright [REV-B F3]"},
         "rate": {"usd_per_hour": rate, "source": inputs["rate_source"]},
         "projection": {
             "prefills": prefills,
@@ -697,6 +861,104 @@ def project(inputs, frozen, replace=False, out_path=None):
     return art
 
 
+# ---------------------------------------------------------------------------
+# checkpoint: construction EARLY-ABORT re-projection ([REV-B F3, ASM-2516])
+# ---------------------------------------------------------------------------
+CHECKPOINT_SCHEDULE = (200, 1024, 2304)   # [STIPULATED] n_done milestones
+CHECKPOINT_RATIO_MAX = 10.0               # sanity bound on realized/predicted
+
+
+def cmd_checkpoint(args):
+    """[REV-B F3] Construction EARLY-ABORT checkpoint. HONESTY (gate-fix
+    review #4): the gate's +-1SE band bounds SAMPLING error of the chosen
+    30-text sample ONLY — NOT selection bias, NOT unseen-tail behaviour; a
+    pin can pass the 30-item gate yet underperform over the 4,608
+    construction items. This checkpoint bounds that residual mechanically:
+    at n_done in CHECKPOINT_SCHEDULE (200/1024/2304 [STIPULATED]; first
+    exposure ~200 x ~137 s ~ 7.6 h ~ $1.3), re-project the WHOLE campaign
+    with the LICENSED gate model re-levelled by the realized construction
+    ratio (elapsed seconds / model-predicted seconds for the first n_done
+    manifest-order construction items) and STOP (exit 2) if a
+    reserve-inclusive cap breaches at central OR +1SE. LEDGER BINDING: the
+    artifact's realized construction hours/usd ARE the cost basis the
+    LANDED driver machinery consumes fail-closed (Ledger REQUIRES
+    cost.usd_spent_prior + construction_instance_hours — never silent
+    zeros; ASM-2513 landed) — a breach here never reaches a pilot spawn."""
+    gate = json.loads(Path(args.gate).read_text(encoding="utf-8"))
+    if gate.get("verdict") != "GREEN":
+        die("F1K_GATE_CKPT", "gate artifact verdict %r — checkpoints only "
+            "run inside a GREEN license" % gate.get("verdict"))
+    knots = sorted(gate["model"]["knots_isotonic"], key=lambda k: k["T"])
+    cont = gate["model"]["cont_tokens_addend"]
+    rate = gate["rate"]["usd_per_hour"]
+    thr = gate["thresholds"]
+    reserve_h = RESERVE_USD / rate
+    entries = [json.loads(l) for l in open(args.tokens, encoding="utf-8")]
+    cons = [e for e in entries if e["pop"] == "construction"]
+    n_done = int(args.n_done)
+    if not 1 <= n_done <= len(cons):
+        die("F1K_GATE_CKPT", "n_done %d outside [1, %d]"
+            % (n_done, len(cons)))
+    elapsed = float(args.elapsed_s)
+    if elapsed <= 0:
+        die("F1K_GATE_CKPT", "elapsed_s must be > 0")
+    pred = sum(_interp(knots, "s", e["T"] + cont, "const")
+               for e in cons[:n_done])
+    ratio = elapsed / pred
+    if not 0.0 < ratio <= CHECKPOINT_RATIO_MAX:
+        die("F1K_GATE_CKPT", "realized/predicted ratio %.3f outside "
+            "(0, %.1f] — model transfer broken; maintainer surface"
+            % (ratio, CHECKPOINT_RATIO_MAX))
+    for k in knots:
+        k["s_hi"] = k["s"] + SE_MULT * k["se"]
+    sec_c = sum(e["m"] * _interp(knots, "s", e["T"] + cont, "const")
+                for e in entries) * ratio
+    sec_hi = sum(e["m"] * _interp(knots, "s_hi", e["T"] + cont, "const")
+                 for e in entries) * ratio
+    h_c, h_hi = sec_c / 3600.0, sec_hi / 3600.0
+    usd_c, usd_hi = h_c * rate, h_hi * rate
+    hi_h, hi_u = thr["instance_hours"][1], thr["usd_total"][1]
+    breach = [msg for cond, msg in (
+        (h_c + reserve_h > hi_h, "central hours %.1f + reserve" % h_c),
+        (h_hi + reserve_h > hi_h, "+1SE hours %.1f + reserve" % h_hi),
+        (usd_c + RESERVE_USD > hi_u, "central $%.2f + reserve" % usd_c),
+        (usd_hi + RESERVE_USD > hi_u, "+1SE $%.2f + reserve" % usd_hi),
+    ) if cond]
+    art = {"schema": SCHEMA + ":construction-checkpoint",
+           "n_done": n_done, "elapsed_s": elapsed,
+           "predicted_s_first_n": round(pred, 1),
+           "realized_over_predicted": round(ratio, 4),
+           "reprojection": {
+               "instance_hours": {"central": round(h_c, 1),
+                                  "hi": round(h_hi, 1)},
+               "usd_total": {"central": round(usd_c, 2),
+                             "hi": round(usd_hi, 2)},
+               "reserve": {"usd": RESERVE_USD,
+                           "hours_at_rate": round(reserve_h, 2)}},
+           "ledger_basis": {
+               "construction_instance_hours_realized_so_far":
+                   round(elapsed / 3600.0, 4),
+               "usd_construction_so_far":
+                   round(elapsed / 3600.0 * rate, 4),
+               "rule": "these figures enter the campaign driver's "
+                       "cost.{usd_spent_prior, construction_instance_"
+                       "hours} — the LANDED Ledger's REQUIRED fail-closed "
+                       "basis (ASM-2513)"},
+           "verdict": "STOP" if breach else "CONTINUE",
+           "breaches": breach,
+           "schedule": list(CHECKPOINT_SCHEDULE)}
+    if args.out:
+        Path(args.out).write_text(json.dumps(art, indent=2))
+    print(json.dumps(art, indent=2))
+    if breach:
+        die("F1K_GATE_CKPT", "EARLY-ABORT: reserve-inclusive re-projection "
+            "breaches (%s) at n_done=%d, ratio %.3f — kill construction, "
+            "mandatory maintainer surface (the remaining spend is "
+            "recoverable NOW; it is not after 4,608 passes)"
+            % ("; ".join(breach), n_done, ratio))
+    return 0
+
+
 # ---------------------------------------------------------------------------
 # spec ($0 control-box witness) + selftest ($0 oracle)
 # ---------------------------------------------------------------------------
@@ -751,13 +1013,21 @@ def _mock_corpora(d):
                 f.write(json.dumps(r) + "\n")
 
 
-def _fake_timing(sample, s_of_t, path):
+MOCK_PIN_PATH = "/mock/pin_bringup.stats"
+MOCK_PIN_BANNER = ("[PIN] hot-expert store armed: pinned 96 experts, "
+                   "1.780 GiB (budget 40.000 GiB) from " + MOCK_PIN_PATH)
+#   [REV-B F3] byte-conforming to the LANDED driver PIN_ARMED_RE (the
+#   mock_colibri.py banner grammar the ASM-2513 machinery verifies)
+
+
+def _fake_timing(sample, s_of_t, path, evidence=MOCK_PIN_BANNER):
     with open(path, "w") as f:
         for e in sample["entries"]:
             noise = 1.0 + ((int(tiehash("n" + e["key"])[:6], 16) % 401)
                            - 200) / 10000.0   # deterministic +-2%
             f.write(json.dumps({"sample_id": e["sample_id"],
                                 "s": round(s_of_t(e["Tp"]) * noise, 3),
+                                "pin_evidence": evidence,
                                 "timer_n": 1}) + "\n")
 
 
@@ -815,6 +1085,7 @@ def selftest():
                     "t1_unpinned_runs": [], "inventory_t": inv_t,
                     "rate_usd_per_hour": rate, "rate_source": "selftest",
                     "pin": {"pin_file_sha256": "f" * 64, "pin_gb": 40.0,
+                            "pin_file_path": MOCK_PIN_PATH,
                             "regime": "pinned-bringup", "note": "mock"},
                     "dump_gate": {"a": "PASS", "b": "PASS", "c": "PASS",
                                   "functional_inertness": "PASS"}}
@@ -900,6 +1171,7 @@ def selftest():
                 sample=str(td / "samp/timing-sample.json"),
                 tokens=str(td / "tok"), t2=str(td / "t2-part.jsonl"),
                 t1=None, rate="0.174", pin_sha="", pin_gb="",
+                pin_path="", pin_derivation="",
                 pin_regime="pinned-bringup", dump_a="PASS", dump_b="PASS",
                 dump_c="PASS", functional="PASS", out=str(td / "gi.json")))
             check(False, "case 6 must refuse partial T2 results")
@@ -920,17 +1192,28 @@ def selftest():
               % (art7a["projection"]["instance_hours"]["central"],
                  art7b["projection"]["instance_hours"]["central"],
                  1.0 + mass_rep / mass))
-        # case 8 (reserve boundary, v3-review finding 4): compute-only $149
-        # at rate 0.20 passes the RAW $155 cap (the OLD reserve-blind rule)
-        # but 149+8 = 157 breaches reserve-inclusive -> STOP; $140 -> GREEN.
-        b8 = (149.0 / 0.20) * 3600.0 / mass
+        # case 8 (reserve boundary, v3-review finding 4; RE-DERIVED in
+        # REV-B per gate-fix review #7: the old planted $149 realized
+        # central $150.22 / +1SE $156.33, so the OLD rule ALREADY STOPped
+        # on the +SE band and the case never isolated the reserve delta).
+        # Planted $146.6 at rate 0.20 realizes central ~$147.8 / +1SE
+        # ~$153.8: BOTH raw bands <= $155 (old reserve-blind rule: GO on
+        # central AND +SE; hours ~739/+SE <= 900 too) while central + $8
+        # breaches -> the STOP is attributable to the RESERVE alone.
+        b8 = (146.6 / 0.20) * 3600.0 / mass
         _fake_timing(sample, lambda t: b8 * t, td / "t2-res.jsonl")
         art8a = project(mk_inputs(td / "t2-res.jsonl", rate=0.20), frozen)
         u8 = art8a["projection"]["usd_total"]["central"]
-        check(art8a["verdict"] == "STOP" and u8 <= 155.0
+        u8hi = art8a["projection"]["usd_total"]["hi"]
+        h8hi = art8a["projection"]["instance_hours"]["hi"]
+        check(art8a["verdict"] == "STOP"
+              and u8 <= 155.0 and u8hi <= 155.0 and h8hi <= 900.0
+              and u8 + 8.0 > 155.0
               and any("RESERVE" in r for r in art8a["reasons"]),
-              "case 8a reserve-boundary STOP: $%.2f central <= $155 raw cap "
-              "(the OLD rule would GO) but +$8 reserve breaches" % u8)
+              "case 8a reserve-boundary STOP ISOLATED: central $%.2f AND "
+              "+1SE $%.2f both <= $155 raw (the OLD rule would GO on both "
+              "bands) but central +$8 = $%.2f breaches — the reserve delta "
+              "alone flips the verdict" % (u8, u8hi, u8 + 8.0))
         b8b = (140.0 / 0.20) * 3600.0 / mass
         _fake_timing(sample, lambda t: b8b * t, td / "t2-res2.jsonl")
         art8b = project(mk_inputs(td / "t2-res2.jsonl", rate=0.20), frozen)
@@ -952,13 +1235,141 @@ def selftest():
         art10 = project(in10, frozen)
         check(art10["verdict"] == "STOP",
               "case 10 STOP: missing dump_gate block fails closed")
+        # case 11 [REV-B F2]: manifest-vs-model structural consistency —
+        # every score manifest's ctx+cont == the model's Tp; a manifest
+        # regenerated with the OLD off-by-continuation convention
+        # (ctx=T-8, total=T) is REFUSED by collect.
+        ok11 = all(
+            (lambda parts, e: int(parts[0]) + int(parts[1]) == e["Tp"]
+             and len(parts) - 2 == e["Tp"])(
+                (td / "samp" / ("sample-%s.score" % e["sample_id"]))
+                .read_text().split(), e)
+            for e in sample["entries"])
+        check(ok11, "case 11 STRUCTURAL: every manifest ctx+cont == Tp "
+                    "(the review-#3 class cannot recur silently)")
+        e11 = sample["entries"][0]
+        m11 = td / "samp" / ("sample-%s.score" % e11["sample_id"])
+        good11 = m11.read_text()
+        parts11 = good11.split()
+        ids11 = parts11[2:2 + e11["T"]]     # strip the 8 cont ids
+        m11.write_text("%d %d %s\n" % (e11["T"] - CONT_TOKENS, CONT_TOKENS,
+                                       " ".join(ids11)))   # OLD convention
+        try:
+            cmd_collect(argparse.Namespace(
+                sample=str(td / "samp/timing-sample.json"),
+                tokens=str(td / "tok"), t2=str(td / "t2-green.jsonl"),
+                t1=None, rate="0.174", pin_sha="", pin_gb="",
+                pin_path="", pin_derivation="",
+                pin_regime="pinned-bringup", dump_a="PASS", dump_b="PASS",
+                dump_c="PASS", functional="PASS", out=str(td / "gi11.json")))
+            check(False, "case 11 must refuse an off-by-continuation "
+                         "manifest")
+        except SystemExit:
+            check(True, "case 11 fail-closed: OLD-convention manifest "
+                        "(ctx=T-8, total=T) refused by collect")
+        m11.write_text(good11)                 # restore
+        # case 12 [REV-B F1]: pinfile merge correctness over an explicit
+        # per-item manifest — merged pin == the (layer,expert) count SUM.
+        sdir = td / "stats"
+        sdir.mkdir()
+        planted = [("3 0 10\n3 1 5\n", "a"), ("3 0 7\n4 2 9\n", "b"),
+                   ("3 1 1\n4 2 1\n5 5 2\n", "c")]
+        for body, tag in planted:
+            (sdir / ("stats-%s.txt" % tag)).write_text(body)
+        man12 = td / "stats.manifest"
+        man12.write_text("".join("%s\n" % (sdir / ("stats-%s.txt" % t))
+                                 for _, t in planted))
+        cmd_pinfile(argparse.Namespace(stats_manifest=str(man12),
+                                       pin_gb=40.0, out=str(td / "p12.st")))
+        got12 = {}
+        for ln in (td / "p12.st").read_text().splitlines():
+            l, e, c = (int(x) for x in ln.split())
+            got12[(l, e)] = c
+        want12 = {(3, 0): 17, (3, 1): 6, (4, 2): 10, (5, 5): 2}
+        check(got12 == want12,
+              "case 12 MERGE CORRECT: 3 per-item stats files -> summed "
+              "union %s" % sorted(got12.items()))
+        man12.write_text(str(sdir / "stats-a.txt") + "\n"
+                         + str(sdir / "stats-MISSING.txt") + "\n")
+        try:
+            cmd_pinfile(argparse.Namespace(stats_manifest=str(man12),
+                                           pin_gb=40.0,
+                                           out=str(td / "p12b.st")))
+            check(False, "case 12 must refuse a missing per-item file")
+        except SystemExit:
+            check(True, "case 12 fail-closed: MISSING per-item stats file "
+                        "refused (no silent partial union)")
+        (sdir / "stats-bad.txt").write_text("3 zero 1\n")
+        man12.write_text(str(sdir / "stats-bad.txt") + "\n")
+        try:
+            cmd_pinfile(argparse.Namespace(stats_manifest=str(man12),
+                                           pin_gb=40.0,
+                                           out=str(td / "p12c.st")))
+            check(False, "case 12 must refuse a malformed stats file")
+        except SystemExit:
+            check(True, "case 12 fail-closed: malformed stats line refused "
+                        "(never skipped)")
+        # case 13 [REV-B F3]: engagement evidence is a hard conjunct — a
+        # T2 set with NO armed banner, and one with a DISABLED marker,
+        # both STOP an otherwise-GREEN gate.
+        _fake_timing(sample, lambda t: b_lin * t, td / "t2-noev.jsonl",
+                     evidence="")
+        art13a = project(mk_inputs(td / "t2-noev.jsonl"), frozen)
+        _fake_timing(sample, lambda t: b_lin * t, td / "t2-dis.jsonl",
+                     evidence="[PIN] cannot open /mock/pin_bringup.stats")
+        art13b = project(mk_inputs(td / "t2-dis.jsonl"), frozen)
+        check(art13a["verdict"] == "STOP"
+              and any("ENGAGEMENT" in r for r in art13a["reasons"])
+              and art13b["verdict"] == "STOP",
+              "case 13 STOP: missing armed banner AND disabled marker both "
+              "refuse (landed ASM-2513 grammar)")
+        # case 14 [REV-B F3]: regime 'unpinned' is REFUSED outright.
+        in14 = mk_inputs(td / "t2-green.jsonl")
+        in14["pin"]["regime"] = "unpinned"
+        art14 = project(in14, frozen)
+        check(art14["verdict"] == "STOP"
+              and any("REFUSED" in r for r in art14["reasons"]),
+              "case 14 STOP: regime 'unpinned' never licenses (shape (ii) "
+              "rejected)")
+        # case 15 [REV-B F3]: construction early-abort checkpoint —
+        # ratio 1.0 CONTINUEs; a realized slowdown that breaches the
+        # reserve-inclusive cap STOPs (exit 2).
+        art["thresholds"] = frozen
+        (td / "gate-art.json").write_text(json.dumps(art))
+        cons15 = [e for e in ent if e["pop"] == "construction"][:200]
+        knots15 = sorted(art["model"]["knots_isotonic"],
+                         key=lambda k: k["T"])
+        pred15 = sum(_interp(knots15, "s", e["T"] + CONT_TOKENS, "const")
+                     for e in cons15)
+        rc15 = cmd_checkpoint(argparse.Namespace(
+            gate=str(td / "gate-art.json"),
+            tokens=str(td / "tok" / "tokens-full.jsonl"),
+            n_done=200, elapsed_s=str(pred15 * 1.0), out=""))
+        check(rc15 == 0, "case 15 checkpoint CONTINUE at ratio 1.0 "
+                         "(700 h central holds)")
+        try:
+            cmd_checkpoint(argparse.Namespace(
+                gate=str(td / "gate-art.json"),
+                tokens=str(td / "tok" / "tokens-full.jsonl"),
+                n_done=200, elapsed_s=str(pred15 * 1.35), out=""))
+            check(False, "case 15 must STOP at ratio 1.35")
+        except SystemExit:
+            check(True, "case 15 EARLY-ABORT STOP: ratio 1.35 re-projects "
+                        "past the reserve-inclusive cap (exit 2) after "
+                        "~$1.3 exposure, not after 4,608 passes")
     print()
     if fails:
         print("BRINGUP-GATE SELFTEST FAILED (%d)" % len(fails))
         return 1
-    print("BRINGUP-GATE SELFTEST PASS (MOCK SCOPE ONLY: rule mechanics + "
-          "verdict logic on synthetic corpora/timing; real T, f, s and the "
-          "license verdict exist only via the VM path + f1k_gcp.py gate)")
+    print("BRINGUP-GATE SELFTEST PASS — HONEST SCOPE [REV-B]: this $0 "
+          "oracle exercises the projection/license logic (incl. reserve, "
+          "dump conjuncts, regime+engagement refusals), the sampling rule "
+          "mechanics, the per-item stats MERGE, manifest-vs-model "
+          "consistency, and the early-abort checkpoint — ALL on synthetic "
+          "corpora, planted timings, and a mock banner grammar. It CANNOT "
+          "exercise: the real engine (timer, STATS/PIN semantics), the "
+          "real tokenizer, GCS transfer, VM deploy, or the real corpus "
+          "bytes. Those exist only via the VM path + f1k_gcp.py gate.")
     return 0
 
 
@@ -977,7 +1388,8 @@ def main():
     p.add_argument("--tokens", required=True)
     p.add_argument("--out", required=True)
     p = sub.add_parser("pinfile")
-    p.add_argument("--stats-glob", required=True)
+    # [REV-B F1] explicit per-item manifest, NEVER a glob (review #2)
+    p.add_argument("--stats-manifest", required=True)
     p.add_argument("--pin-gb", type=float, required=True)
     p.add_argument("--out", required=True)
     p = sub.add_parser("collect")
@@ -988,19 +1400,30 @@ def main():
     p.add_argument("--rate", required=True)
     p.add_argument("--pin-sha", default="")
     p.add_argument("--pin-gb", default="")
+    p.add_argument("--pin-path", default="")
+    p.add_argument("--pin-derivation", default="")
     p.add_argument("--pin-regime", required=True,
                    choices=["pinned-bringup", "unpinned"])
+    #   'unpinned' stays RECORDABLE (honest artifact) but the verdict
+    #   REFUSES it — shape (ii) rejected [REV-B F3]
     p.add_argument("--dump-a", required=True)
     p.add_argument("--dump-b", required=True)
     p.add_argument("--dump-c", required=True)
     p.add_argument("--functional", required=True)
     p.add_argument("--out", required=True)
+    p = sub.add_parser("checkpoint")
+    p.add_argument("--gate", required=True)
+    p.add_argument("--tokens", required=True)
+    p.add_argument("--n-done", required=True)
+    p.add_argument("--elapsed-s", required=True)
+    p.add_argument("--out", default="")
     sub.add_parser("selftest")
     args = ap.parse_args()
     if args.cmd == "selftest":
         return selftest()
     return {"spec": cmd_spec, "fcount": cmd_fcount, "realize": cmd_realize,
-            "pinfile": cmd_pinfile, "collect": cmd_collect}[args.cmd](args)
+            "pinfile": cmd_pinfile, "collect": cmd_collect,
+            "checkpoint": cmd_checkpoint}[args.cmd](args)
 
 
 if __name__ == "__main__":
```
<!-- END-ARTIFACT D9 -->

### B8.2 D10 — `poc/gcp/f1k_gcp.py` orchestrator delta (F4 deps/RAID-state/launcher + F3 pin-fetch)

<!-- BEGIN-ARTIFACT D10 f1k_gcp.py.rev-b.diff sha256=e3611c4f3f801e8fb2c9ecf57634fc22794b764c8c4cffc66c407605270e77dc -->
```diff
diff --git a/poc/gcp/f1k_gcp.py b/poc/gcp/f1k_gcp.py
index 5820eea..053bec8 100755
--- a/poc/gcp/f1k_gcp.py
+++ b/poc/gcp/f1k_gcp.py
@@ -37,6 +37,9 @@ Entrypoints (source ~/.config/kot/gcp.env first):
   python3 poc/gcp/f1k_gcp.py watchdog --max-hours H
                                            # box-side teardown watchdog loop
                                            #   (nohup it; verify with pgrep)
+  python3 poc/gcp/f1k_gcp.py pin-fetch     # fetch + BYTE-VERIFY the licensed
+                                           #   campaign pin; prints the exact
+                                           #   PIN/PIN_GB exports [REV-B]
   python3 poc/gcp/f1k_gcp.py status        # poll VM state + GCS heartbeat
   python3 poc/gcp/f1k_gcp.py teardown      # delete VM + disks (nothing bills idle)
 (stage/build/KaE+dump bring-up run ON the VM via f1k_worker.sh — they were
@@ -544,17 +547,46 @@ def cmd_bringup_deploy() -> None:
         if not os.environ.get(var):
             die("F1K_DEPLOY", "%s unset (f1k_worker.sh env contract)" % var)
     max_life_min = int(os.environ.get("KOT_F1K_GUEST_MAXLIFE_MIN", "900"))
-    # 1. remote prep: RAID0 the 2 local NVMe (stable by-id paths) + max-life
+    # 1. remote prep [REV-B F4, gate-fix review #5]:
+    #    - DEPENDENCIES the worker actually needs, VERIFIED on a fresh
+    #      image: google-cloud-cli (gsutil — chosen over curl+signed URLs
+    #      because the worker performs MANY dynamic writes: estate rsync,
+    #      heartbeats, gate mirrors; per-object URL minting is unworkable,
+    #      and the VM's service account auths gsutil natively) +
+    #      python3-pip (tokenizers/HF staging). Most GCE images ship both
+    #      — verify, never assume.
+    #    - RAID by STATE, not directory existence: `mountpoint -q` decides;
+    #      a reboot re-assembles /dev/md0 and re-MOUNTS (mkfs ONLY on
+    #      first creation) — a bare /mnt/nvme dir on the boot disk can
+    #      never silently swallow the ~384 GB estate.
     remote = (
         "set -euo pipefail\n"
-        "if [ ! -d /mnt/nvme ]; then\n"
-        "  sudo apt-get update -qq && sudo apt-get install -y -qq mdadm\n"
-        "  DEVS=$(ls /dev/disk/by-id/google-local-nvme-ssd-* 2>/dev/null)\n"
-        "  N=$(echo \"$DEVS\" | wc -w)\n"
-        "  [ \"$N\" -eq %d ] || { echo \"ERR: $N local NVMe != %d\"; exit 2; }\n"
-        "  sudo mdadm --create /dev/md0 --level=0 --raid-devices=%d $DEVS\n"
-        "  sudo mkfs.ext4 -F /dev/md0 && sudo mkdir -p /mnt/nvme\n"
+        "sudo apt-get update -qq\n"
+        "command -v gsutil >/dev/null 2>&1"
+        " || sudo apt-get install -y -qq google-cloud-cli\n"
+        "command -v gsutil >/dev/null 2>&1"
+        " || { echo 'ERR: gsutil unavailable (google-cloud-cli install"
+        " failed)'; exit 2; }\n"
+        "command -v pip3 >/dev/null 2>&1"
+        " || sudo apt-get install -y -qq python3-pip\n"
+        "command -v pip3 >/dev/null 2>&1"
+        " || { echo 'ERR: pip3 unavailable'; exit 2; }\n"
+        "if ! mountpoint -q /mnt/nvme; then\n"
+        "  sudo apt-get install -y -qq mdadm\n"
+        "  if [ ! -e /dev/md0 ]; then\n"
+        "    sudo mdadm --assemble /dev/md0 2>/dev/null || true\n"
+        "  fi\n"
+        "  if [ ! -e /dev/md0 ]; then\n"
+        "    DEVS=$(ls /dev/disk/by-id/google-local-nvme-ssd-* 2>/dev/null)\n"
+        "    N=$(echo \"$DEVS\" | wc -w)\n"
+        "    [ \"$N\" -eq %d ] || { echo \"ERR: $N local NVMe != %d\"; exit 2; }\n"
+        "    sudo mdadm --create /dev/md0 --level=0 --raid-devices=%d $DEVS\n"
+        "    sudo mkfs.ext4 -F /dev/md0\n"
+        "  fi\n"
+        "  sudo mkdir -p /mnt/nvme\n"
         "  sudo mount /dev/md0 /mnt/nvme && sudo chown \"$USER\" /mnt/nvme\n"
+        "  mountpoint -q /mnt/nvme"
+        " || { echo 'ERR: /mnt/nvme still not a mountpoint'; exit 2; }\n"
         "fi\n"
         "sudo shutdown -P +%d 'kot-f1k guest max-life backstop'\n"
         % (LOCAL_SSD_COUNT, LOCAL_SSD_COUNT, LOCAL_SSD_COUNT, max_life_min))
@@ -566,6 +598,23 @@ def cmd_bringup_deploy() -> None:
     bundle.mkdir()
     for f in ("f1k_worker.sh", "bringup_gcp.sh", "f1k_bringup_gate.py"):
         shutil.copy2(HERE / f, bundle / f)
+    # [REV-B F4] failure-visible launcher: ANY worker exit != 0 — incl.
+    # `set -e` deaths that bypass die() and its heartbeat — writes a
+    # FAILED heartbeat the watchdog acts on promptly (no max-life wait).
+    (bundle / "f1k_launch.sh").write_text(
+        "#!/usr/bin/env bash\n"
+        "# generated by f1k_gcp.py bringup-deploy [REV-B F4]\n"
+        "cd \"$(dirname \"$0\")\"\n"
+        "bash f1k_worker.sh > worker.log 2>&1\n"
+        "rc=$?\n"
+        "if [ \"$rc\" -ne 0 ]; then\n"
+        "  printf '{\"ts\":\"%s\",\"stage\":\"FAILED: worker exit rc=%d\","
+        "\"rc\":%d}\\n' \"$(date -u +%FT%TZ)\" \"$rc\" \"$rc\" "
+        "> failed-heartbeat.json\n"
+        "  gsutil -q cp failed-heartbeat.json "
+        "\"$KOT_F1K_BUCKET/f1k/bringup/heartbeat.json\" || true\n"
+        "fi\n"
+        "exit \"$rc\"\n")
     shutil.copy2(HARNESS / "tok_glm52.py", bundle / "tok_glm52.py")
     shutil.copytree(KAE_PATCH_DIR, bundle / "kae-patch-draft")
     shutil.copytree(DUMP_PATCH_DIR, bundle / "dump-patch")
@@ -587,10 +636,11 @@ def cmd_bringup_deploy() -> None:
              .hexdigest()[:16]))
     gcloud("compute", "scp", "--recurse", "--zone", ZONE,
            str(bundle), "%s:~/" % INSTANCE_NAME)
-    # 3. launch the worker detached with the env contract
+    # 3. launch the worker detached VIA THE LAUNCHER (FAILED-heartbeat
+    #    wrapper) with the env contract [REV-B F4]
     launch = ("cd ~/f1k && setsid nohup env KOT_F1K_BUCKET='%s' "
               "COLIBRI_GIT_URL='%s' KOT_F1K_SPOT_RATE='%s' "
-              "bash f1k_worker.sh > worker.log 2>&1 & echo LAUNCHED-$!"
+              "bash f1k_launch.sh > launcher.log 2>&1 & echo LAUNCHED-$!"
               % (os.environ["KOT_F1K_BUCKET"],
                  os.environ["COLIBRI_GIT_URL"],
                  os.environ["KOT_F1K_SPOT_RATE"]))
@@ -636,11 +686,57 @@ def cmd_watchdog() -> None:
         time.sleep(args.poll_seconds)
 
 
+def cmd_pin_fetch() -> None:
+    """[REV-B F3, gate-fix review #4] Fetch + BYTE-VERIFY the licensed
+    campaign pin and print the exact construction env exports — the
+    construction command NEVER inherits ambient PIN/PIN_GB (the carrier
+    builder would silently use whatever the environment happened to hold,
+    build_carriers.py:634 lineage). Fail-closed at every step:
+      - the gate artifact must be verdict GREEN, regime pinned-bringup;
+      - the fetched GCS bytes must sha256-match pin.pin_file_sha256;
+      - PIN_GB is echoed FROM THE ARTIFACT (the licensed value).
+    usage: f1k_gcp.py pin-fetch --gate <bringup-gate.json> --out <dir>"""
+    import argparse
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--gate", required=True)
+    ap.add_argument("--out", required=True)
+    args = ap.parse_args(sys.argv[2:])
+    bucket = os.environ.get("KOT_F1K_BUCKET", "")
+    if not bucket:
+        die("F1K_PIN_FETCH", "KOT_F1K_BUCKET unset")
+    art = json.loads(Path(args.gate).read_text(encoding="utf-8"))
+    if art.get("verdict") != "GREEN":
+        die("F1K_PIN_FETCH", "gate artifact verdict %r — only a GREEN "
+            "license carries a construction pin" % art.get("verdict"))
+    pin = art.get("pin") or {}
+    if pin.get("regime") != "pinned-bringup" \
+            or not pin.get("pin_file_sha256") or not pin.get("pin_gb"):
+        die("F1K_PIN_FETCH", "gate artifact pin block incomplete/unpinned "
+            "(%r) — shape (i) requires a bound sha + PIN_GB" % (pin,))
+    outdir = Path(args.out)
+    outdir.mkdir(parents=True, exist_ok=True)
+    dest = outdir / "campaign-pin.stats"
+    rc = subprocess.run(["gsutil", "-q", "cp",
+                         bucket + "/f1k/bringup/campaign-pin.stats",
+                         str(dest)])
+    if rc.returncode != 0 or not dest.is_file():
+        die("F1K_PIN_FETCH", "gsutil fetch of campaign-pin.stats failed")
+    got = sha256_file(dest)
+    if got != pin["pin_file_sha256"]:
+        die("F1K_PIN_FETCH", "fetched pin sha %s != licensed %s — the "
+            "persisted bytes are NOT the licensed pin; fail closed"
+            % (got, pin["pin_file_sha256"]))
+    print("campaign pin verified: %s (sha %s...)" % (dest, got[:16]))
+    print("export PIN=%s" % dest)
+    print("export PIN_GB=%s" % pin["pin_gb"])
+
+
 ENTRY = {
     "plan": cmd_plan, "provision": cmd_provision, "status": cmd_status,
     "teardown": cmd_teardown, "affordability": cmd_affordability,
     "gate": cmd_gate,
     "bringup-deploy": cmd_bringup_deploy, "watchdog": cmd_watchdog,
+    "pin-fetch": cmd_pin_fetch,
 }
 
 
```
<!-- END-ARTIFACT D10 -->

### B8.3 D11 — `poc/gcp/f1k_worker.sh` worker delta (F1 per-item STATS + F3 verified persistence + F4 COLIBRI_TREE/deps/mountpoint)

<!-- BEGIN-ARTIFACT D11 f1k_worker.sh.rev-b.diff sha256=7401ad53d667dbb3c746cef042f379c123da1ec8b795ad22306f2c48ed568262 -->
```diff
diff --git a/poc/gcp/f1k_worker.sh b/poc/gcp/f1k_worker.sh
index b0b654d..d80a7a9 100755
--- a/poc/gcp/f1k_worker.sh
+++ b/poc/gcp/f1k_worker.sh
@@ -92,10 +92,26 @@ if curl -s --max-time 1 http://169.254.169.254/latest/meta-data/instance-id >/de
         http://metadata.google.internal/computeMetadata/v1/instance/zone >/dev/null 2>&1; then
   die "worker looks like AWS — refuse (frozen target is the GCP Spot VM)"
 fi
-for t in git gcc make objdump python3 sha256sum gsutil curl; do
+for t in git gcc make objdump python3 sha256sum curl; do
   command -v "$t" >/dev/null 2>&1 || { sudo apt-get update -qq && sudo apt-get install -y -qq git build-essential binutils python3 curl; break; }
 done
-[ -d "$SSD" ] || die "local NVMe mount $SSD missing (provision must RAID+mount the 3 local SSD)"
+# [REV-B F4] fresh-worker dependency VERIFICATION (gate-fix review #5): the
+# GCS mirror/heartbeat path is load-bearing throughout (staging, resume,
+# diagnostics), so gsutil is REQUIRED — bringup-deploy's remote prep
+# installs google-cloud-cli when the image lacks it; refuse to run blind.
+# pip3 likewise (tokenizers + HF staging below).
+command -v gsutil >/dev/null 2>&1 \
+  || sudo apt-get install -y -qq google-cloud-cli 2>/dev/null || true
+command -v gsutil >/dev/null 2>&1 \
+  || die "gsutil MISSING and google-cloud-cli install failed — every GCS seam (estate mirror, heartbeat, campaign-pin persistence) is dead; fix the image/deploy (bringup-deploy remote prep)"
+command -v pip3 >/dev/null 2>&1 \
+  || sudo apt-get install -y -qq python3-pip 2>/dev/null || true
+command -v pip3 >/dev/null 2>&1 || die "pip3 MISSING (python3-pip)"
+# [REV-B F4] MOUNTPOINT guard, not directory existence (review #5): after a
+# reboot /mnt/nvme exists as a bare dir on the BOOT DISK — staging ~384 GB
+# there would silently fill it. Require a real mount.
+mountpoint -q "$SSD" \
+  || die "local NVMe $SSD is NOT a mountpoint (bare dir = boot disk!) — bringup-deploy must RAID0 (/dev/md0) + mount the local SSDs first"
 hb "preflight-ok"
 
 step "1/5 stage estate (GCS mirror -> else HF -> local NVMe, then mirror to GCS)"
@@ -158,8 +174,30 @@ step "4/5 build CONSTRUCTION engine (KaE + dump patch) + DUMP bring-up gate (b)"
 # real-checks.sh itself is UNTOUCHED (gate-0-reviewed); its step-6 proof
 # stands fail-closed OFF-BOX on the gcc-11.5 measurement basis. ANY other
 # failure stays fail-closed here.
+# [REV-B F4, gate-fix review #5] real-checks.sh's ACTUAL contract, met
+# explicitly (it was invoked dead-on-arrival before):
+#   - COLIBRI_TREE (real-checks.sh:43) = a PRISTINE checkout whose c/glm.c
+#     is at the pinned base blob (:47 verifies fail-closed) — the
+#     bringup_gcp.sh tree is PATCHED, so clone a fresh one at the same
+#     pinned commit (bringup_gcp.sh:24 a78a06fc);
+#   - the KaE patch at dump-patch/../../kae-patch-draft (real-checks.sh:37)
+#     — with the bundle at ~/f1k that resolves to ~/kae-patch-draft, so
+#     provide it there (symlink) and verify before invoking.
+COLIBRI_PRISTINE="$HOME_DIR/colibri-pristine"
+if [ ! -d "$COLIBRI_PRISTINE/.git" ]; then
+  git clone "$COLIBRI_GIT_URL" "$COLIBRI_PRISTINE"
+fi
+( cd "$COLIBRI_PRISTINE" \
+  && { git fetch --all --quiet || true; } \
+  && git checkout --quiet a78a06fc5acc4b0dc0f9ef03987c66b0559d1250 \
+  && git diff --quiet ) \
+  || die "pristine colibri checkout for COLIBRI_TREE failed (real-checks.sh:43 contract)"
+ln -sfn "$HERE/kae-patch-draft" "$(dirname "$HERE")/kae-patch-draft"
+[ -f "$(dirname "$HERE")/kae-patch-draft/kae-add-path.patch" ] \
+  || die "kae-add-path.patch not reachable at real-checks.sh's expected ../../kae-patch-draft location"
 set +e
 ( cd "$HERE/dump-patch" && COLIBRI_GIT_URL="$COLIBRI_GIT_URL" \
+    COLIBRI_TREE="$COLIBRI_PRISTINE" \
     COLIBRI_WORK="$HOME_DIR/colibri-construct" bash real-checks.sh ) \
   > "$GATE/dump-realchecks.log" 2>&1
 RC_B=$?
@@ -345,7 +383,7 @@ python3 "$GATEPY" realize --tokens "$GATE/gate-tokens" --out "$GATE/gate-sample"
 hb "gate-tokenized"
 
 # PIN_GB fixed at bring-up from MEASURED free-RAM headroom (plan §5 semantics;
-# recording + truthful-attestation mechanics: F1K-PIN-FILE-FIX.md v2 — this
+# recording + truthful-attestation mechanics: F1K-PIN-FILE-FIX.md v5 — this
 # step only FIXES the number and derives the BRING-UP pin; it never fakes one).
 MEM_AVAIL_GB=$(awk '/MemAvailable/ {printf "%d", $2/1048576}' /proc/meminfo)
 PIN_GB="${KOT_F1K_PIN_GB:-$(( MEM_AVAIL_GB - 8 ))}"
@@ -371,42 +409,56 @@ run_gate_sample() {   # $1=sample_id  $2=results.jsonl  $3.. = extra env pairs
   n=$(echo "$timer" | grep -oE '[0-9]+ req' | grep -oE '[0-9]+' || true)
   s=$(echo "$timer" | grep -oE '\| [0-9.]+s' | grep -oE '[0-9.]+' || true)
   { [ -n "$s" ] && [ "${n:-0}" -ge 1 ]; } || die "gate run $sid: engine emitted no scoring timer (see gate-run-$sid.err)"
-  pin_ev=$(grep -iE 'pin' "$GATE/gate-run-$sid.err" | head -3 | tr -d '"' | tr '\n' ';' || true)
-  echo "{\"sample_id\":\"$sid\",\"s\":$s,\"timer_n\":$n,\"stderr_pin_evidence\":\"$pin_ev\"}" >> "$res"
+  # [REV-B F3] engagement evidence VERBATIM: the [PIN] banner/marker lines
+  # (armed banner grammar = the LANDED driver's PIN_ARMED_RE, ASM-2513;
+  # wording fetch-grade ASM-1971 — a real-engine divergence is aligned in
+  # the DRIVER regex once, and the control-box check follows). The gate
+  # verdict REQUIRES a coherent armed banner per pinned T2 run.
+  pin_ev=$(grep -E '\[PIN\]|pinning DISABLED' "$GATE/gate-run-$sid.err" | head -5 | tr -d '"' | tr '\n' ';' || true)
+  echo "{\"sample_id\":\"$sid\",\"s\":$s,\"timer_n\":$n,\"pin_evidence\":\"$pin_ev\"}" >> "$res"
 }
 
-# T1: UNPINNED runs over the t1 subset with engine usage stats ON (STATS knob
-# semantics are fetch-grade [ASM-1971] — the runner re-verifies knob + harvest
-# location at the (7) semantic gate; KOT_F1K_STATS_HARVEST overrides the glob).
+# T1: UNPINNED runs over the t1 subset with engine usage stats ON.
+# [REV-B F1, gate-fix review #2] the engine interface is STATS=<file>
+# (kae-add-path.patch:175/:180/:183: `stats=getenv("STATS")` ->
+# `stats_dump(&m, stats)` writes THE named file) — the old `STATS=1` made
+# every run overwrite one file named `1`, deriving the pin from the LAST
+# item, not the T1 union. Now: ONE stats file PER RUN (rm'd first —
+# correct whether stats_dump truncates or appends, which stays
+# fetch-grade [ASM-1971]), asserted non-empty after the run, listed in an
+# EXPLICIT manifest; the merge (`pinfile`) is fail-closed on any
+# missing/empty/malformed file and records per-file sha provenance.
 T1_IDS=$(python3 -c "import json;print(' '.join(json.load(open('$GATE/gate-sample/timing-sample.json'))['t1_sample_ids']))")
 T1_CWD="$GATE/t1-cwd"; mkdir -p "$T1_CWD"
+T1_STATS_DIR="${KOT_F1K_STATS_DIR:-$GATE/t1-stats}"; mkdir -p "$T1_STATS_DIR"
 : > "$GATE/t1-results.jsonl"
+: > "$GATE/t1-stats.manifest"
 for sid in $T1_IDS; do
-  ( cd "$T1_CWD" && run_gate_sample "$sid" "$GATE/t1-results.jsonl" STATS=1 )
+  SFILE="$T1_STATS_DIR/stats-$sid.txt"
+  rm -f "$SFILE"
+  ( cd "$T1_CWD" && run_gate_sample "$sid" "$GATE/t1-results.jsonl" STATS="$SFILE" )
+  [ -s "$SFILE" ] || die "T1 run $sid wrote NO usage stats at $SFILE (STATS=<file>, kae-add-path.patch:175) — the pin never derives from a partial T1 union; STOP (maintainer surface; re-verify the STATS knob at the (7) semantic gate)"
+  echo "$SFILE" >> "$GATE/t1-stats.manifest"
 done
 hb "gate-t1-done"
 
-# bring-up pin file at PIN_GB from the T1 usage stats; if underivable, T2 runs
-# UNPINNED (conservative: the ASM-2205 1.20x lever is priced OUT, never faked).
+# bring-up pin file at PIN_GB from the EXPLICIT T1 stats manifest.
+# [REV-B F3] an underivable pin is a fail-closed STOP: shape (ii)
+# (unpinned) was REJECTED (SSA3.5) and the gate REFUSES regime "unpinned"
+# — running 30 unlicensable T2 timings would only burn budget.
 PIN_REGIME="pinned-bringup"; PIN_FILE="$GATE/pin_bringup.stats"; PIN_SHA=""
-if python3 "$GATEPY" pinfile --stats-glob "${KOT_F1K_STATS_HARVEST:-$T1_CWD/*}" \
-     --pin-gb "$PIN_GB" --out "$PIN_FILE" > "$GATE/pinfile.json" 2>&1; then
-  PIN_SHA=$(sha256sum "$PIN_FILE" | awk '{print $1}')
-else
-  PIN_REGIME="unpinned"; PIN_FILE=""
-  echo "WARN: bring-up pin underivable (see pinfile.json) -> T2 UNPINNED (conservative, recorded)"
-fi
+python3 "$GATEPY" pinfile --stats-manifest "$GATE/t1-stats.manifest" \
+     --pin-gb "$PIN_GB" --out "$PIN_FILE" > "$GATE/pinfile.json" 2>&1 \
+  || die "bring-up pin underivable (see pinfile.json) — shape (i) is the ONLY licensable regime (unpinned was REJECTED, fix memo SSA3.5/SSB); mandatory maintainer surface"
+PIN_SHA=$(sha256sum "$PIN_FILE" | awk '{print $1}')
 
 # T2: the LICENSE timing — every sample text, per-item engine timer (model
-# load excluded), pinned when the bring-up pin derived (evidence per run).
+# load excluded), ALWAYS pinned (evidence per run; the control-box verdict
+# verifies an armed banner per run against the bound sha/PIN_GB).
 : > "$GATE/t2-results.jsonl"
 ALL_IDS=$(python3 -c "import json;print(' '.join(e['sample_id'] for e in json.load(open('$GATE/gate-sample/timing-sample.json'))['entries']))")
 for sid in $ALL_IDS; do
-  if [ "$PIN_REGIME" = "pinned-bringup" ]; then
-    run_gate_sample "$sid" "$GATE/t2-results.jsonl" PIN="$PIN_FILE" PIN_GB="$PIN_GB"
-  else
-    run_gate_sample "$sid" "$GATE/t2-results.jsonl"
-  fi
+  run_gate_sample "$sid" "$GATE/t2-results.jsonl" PIN="$PIN_FILE" PIN_GB="$PIN_GB"
 done
 hb "gate-t2-done"
 
@@ -414,18 +466,24 @@ python3 "$GATEPY" collect --sample "$GATE/gate-sample/timing-sample.json" \
   --tokens "$GATE/gate-tokens" --t2 "$GATE/t2-results.jsonl" \
   --t1 "$GATE/t1-results.jsonl" --rate "$SPOT_RATE" \
   --pin-sha "$PIN_SHA" --pin-gb "$PIN_GB" --pin-regime "$PIN_REGIME" \
+  --pin-path "$PIN_FILE" \
+  --pin-derivation "$PIN_FILE.derivation.json" \
   --dump-a "$(cat "$GATE/tiny-dump.status" 2>/dev/null || echo MISSING)" \
   --dump-b "$(cat "$GATE/dump-b.status" 2>/dev/null || echo MISSING)" \
   --dump-c "$(cat "$GATE/moe-sum-crosscheck.status" 2>/dev/null || echo MISSING)" \
   --functional "$(python3 -c "import json;print(json.load(open('$GATE/functional-inertness.json')).get('verdict','MISSING'))" 2>/dev/null || echo MISSING)" \
   --out "$GATE/gate-inputs.json" || die "gate collect FAILED"
 # The bring-up pin IS the construction-phase CAMPAIGN pin (fix memo SSA3
-# C-decision): persist it; construction runs PIN=<this file> (sha+PIN_GB
-# bound per F1K-PIN-FILE-FIX.md). Full-corpus re-derivation is allowed ONLY
-# at the construction->pilot boundary, re-bound there, never mid-phase.
-if [ -n "$PIN_SHA" ]; then
-  gsutil -q cp "$PIN_FILE" "$BUCKET/f1k/bringup/campaign-pin.stats" || true
-fi
+# C-decision): persist it VERIFIED — [REV-B F3, gate-fix review #4] no
+# `|| true`: upload, RE-READ from GCS, and require the byte-exact sha; a
+# licensed pin that failed to persist is a dead campaign, fail closed.
+gsutil -q cp "$PIN_FILE" "$BUCKET/f1k/bringup/campaign-pin.stats" \
+  || die "campaign-pin upload FAILED (gsutil cp)"
+gsutil -q cp "$PIN_FILE.derivation.json" "$BUCKET/f1k/bringup/campaign-pin.stats.derivation.json" \
+  || die "campaign-pin derivation upload FAILED"
+REMOTE_PIN_SHA=$(gsutil -q cat "$BUCKET/f1k/bringup/campaign-pin.stats" | sha256sum | awk '{print $1}')
+[ "$REMOTE_PIN_SHA" = "$PIN_SHA" ] \
+  || die "campaign-pin GCS re-read sha $REMOTE_PIN_SHA != local $PIN_SHA — persisted bytes differ from the licensed pin; fail closed"
 echo "CONTROL-BOX-VERDICT-REQUIRED" > "$GATE/bringup-gate.status"
 cat > "$GATE/bringup-gate-README.txt" <<EOF
 REAL-CORPUS gate inputs ready: $GATE/gate-inputs.json (mirrored to GCS).
@@ -441,8 +499,12 @@ the on-box confirmations, the RUNNER overwrites tiny-dump.status and
 moe-sum-crosscheck.status with the literal PASS and RE-RUNS the collect
 command above (cheap; no re-timing) before pulling gate-inputs.json.
 The caps are tested RESERVE-INCLUSIVE (+\$8 / +8/rate hours) on the control
-box; the campaign pin for construction is campaign-pin.stats (sha in
-gate-inputs.json), bound per F1K-PIN-FILE-FIX.md.
+box; the verdict also REQUIRES per-run pin-ENGAGEMENT evidence for the bound
+pin sha/PIN_GB and REFUSES regime "unpinned" [REV-B]. The campaign pin for
+construction is campaign-pin.stats (sha-verified persisted, derivation
+sidecar alongside); construction fetches it via \`f1k_gcp.py pin-fetch\`
+(byte-verified export of PIN/PIN_GB — never ambient env), bound per
+F1K-PIN-FILE-FIX.md v5.
 EOF
 cat "$GATE/bringup-gate-README.txt"
 hb "gate-inputs-ready"
```
<!-- END-ARTIFACT D11 -->

### B8.4 D12 — `poc/gcp/README.md` README delta (F3 construction binding + boundary rebind + checkpoints; F4 deploy)

<!-- BEGIN-ARTIFACT D12 README.md.rev-b.diff sha256=0fb929fcd606f8a1840d59e1a4ab278389a5d3616d9b2bfb36c89618cf852c20 -->
```diff
diff --git a/poc/gcp/README.md b/poc/gcp/README.md
index e8e62bf..e6495b8 100644
--- a/poc/gcp/README.md
+++ b/poc/gcp/README.md
@@ -54,8 +54,8 @@ maintainer), **NOT a retry** — the pzb6 class discovered at bring-up.
 
 | File | What it is |
 |---|---|
-| `f1k_gcp.py` | Orchestrator (runs on the control box): `plan` ($0 dry-plan: pins + reuse-gate + SPOT/disk/window asserts), `provision` (Spot VM + 2 local SSD), `status`, `teardown`, `bringup-deploy` (RAID+mount NVMe, push the worker bundle + frozen gate corpora, launch the worker detached, arm the guest max-life), `watchdog --max-hours H` (box-side teardown loop; nohup it, verify `pgrep -f 'f1k_gcp.py watchdog'`), `gate` (**the bring-up gate verdict — kot-f1k-bringup-gate/1; GREEN is the ONLY construction license**; `--selftest` = $0 mock oracle), `affordability` (one-blended-s/prefill projection — **SECONDARY diagnostic ONLY, licenses nothing**). |
-| `f1k_bringup_gate.py` | The FIXED bring-up gate machinery (`F1K-BRINGUP-GATE-FIX.md` v1, GAP-1/2/3): frozen deterministic stratified real-corpus sampling rule, full-corpus tokenization (measured f, per-item T), bring-up pin-file derivation, per-item token-aware ledger projection + GREEN/STOP artifact; `selftest` = $0 end-to-end mock oracle. |
+| `f1k_gcp.py` | Orchestrator (runs on the control box): `plan` ($0 dry-plan: pins + reuse-gate + SPOT/disk/window asserts), `provision` (Spot VM + 2 local SSD), `status`, `teardown`, `bringup-deploy` (RAID+mount NVMe, push the worker bundle + frozen gate corpora, launch the worker detached, arm the guest max-life), `watchdog --max-hours H` (box-side teardown loop; nohup it, verify `pgrep -f 'f1k_gcp.py watchdog'`), `gate` (**the bring-up gate verdict — kot-f1k-bringup-gate/1; GREEN is the ONLY construction license**; `--selftest` = $0 mock oracle), `pin-fetch` (fetch + byte-verify the licensed campaign pin → explicit `PIN`/`PIN_GB` exports [REV-B]), `affordability` (one-blended-s/prefill projection — **SECONDARY diagnostic ONLY, licenses nothing**). |
+| `f1k_bringup_gate.py` | The FIXED bring-up gate machinery (`F1K-BRINGUP-GATE-FIX.md` v1+REV-B, GAP-1/2/3): frozen deterministic stratified real-corpus sampling rule, full-corpus tokenization (measured f, per-item T), per-item-manifest bring-up pin derivation (fail-closed merge + provenance), per-item token-aware ledger projection + GREEN/STOP artifact (engagement-verified, unpinned refused), `checkpoint` = construction early-abort re-projection; `selftest` = $0 mock oracle of the LOGIC seams only (no real engine/tokenizer/GCS/VM — honest scope printed). |
 | `bringup_gcp.sh` | KaE bring-up on the VM: colibri@`a78a06fc` + KaE patch (`11f8b458`), build, 44/44 `test_kae`; objdump patch-shape checks (clone-aware, reference + native flags) are **ADVISORY-ONLY on the VM** (bead f2uk / ASM-2503: gcc-version-brittle even at `-O2 -march=x86-64-v3`; fail-closed objdump lives off-box on the gcc-11.5 basis; the frozen `bringup.sh` is untouched). The AUTHORITATIVE inertness proof is the functional KAE-unset byte-identity gate in `f1k_worker.sh`. |
 | `f1k_worker.sh` | On-VM autonomous worker: STAGE (GCS mirror → else HF → NVMe, weight-hash pin) → BUILD scoring + construction engines → KaE bring-up → dump bring-up gate (b) → scaffolds (a)+(c) → **REAL-CORPUS gate inputs** (tokenize → measured f + per-item T; frozen stratified per-item timing, T1 unpinned → bring-up pin → T2 pinned; `gate-inputs.json`) → **STOP before construction spend**. Heartbeat + artifacts to GCS; idempotent (spot preemption re-runs, restages from GCS). |
 
@@ -65,13 +65,20 @@ maintainer), **NOT a retry** — the pzb6 class discovered at bring-up.
 1. `provision` → **record the ACTUAL assigned spot $/h** (load-bearing for the
    affordability gate). Set `KOT_F1K_BUCKET=gs://…` (same-region estate mirror),
    `COLIBRI_GIT_URL` (coordinator-supplied), `KOT_F1K_SPOT_RATE=<measured>`.
-2. `python3 poc/gcp/f1k_gcp.py bringup-deploy` — RAID0+mount the 2 local SSD,
-   assemble + push the worker bundle (worker, `bringup_gcp.sh`,
-   `f1k_bringup_gate.py`, `tok_glm52.py`, `kae-patch-draft/`, `dump-patch/`,
-   and `gate-corpus/` = the four frozen corpora
-   `construction-manifest.jsonl` + `f1k-eval-v1/items/{test,dev,guard}.jsonl`,
-   sha-manifested), launch `f1k_worker.sh` detached, arm the guest max-life
-   (verify on-VM: `sudo shutdown --show`). Then start the box-side watchdog:
+2. `python3 poc/gcp/f1k_gcp.py bringup-deploy` — remote prep **verifies the
+   fresh-worker dependencies** (`google-cloud-cli`/gsutil + `python3-pip`
+   installed when the image lacks them, fail-closed) and RAID0+mounts the 2
+   local SSD **by state** (`mountpoint -q`; reboot re-assembles `/dev/md0` and
+   re-mounts, `mkfs` only on first creation — a bare `/mnt/nvme` dir never
+   silently stages ~384 GB onto the boot disk); assembles + pushes the worker
+   bundle (worker, `bringup_gcp.sh`, `f1k_bringup_gate.py`, `tok_glm52.py`,
+   `kae-patch-draft/`, `dump-patch/`, `f1k_launch.sh` launcher, and
+   `gate-corpus/` = the four frozen corpora `construction-manifest.jsonl` +
+   `f1k-eval-v1/items/{test,dev,guard}.jsonl`, sha-manifested); launches the
+   worker detached **via `f1k_launch.sh`** (ANY nonzero worker exit — `set -e`
+   deaths included — writes a `FAILED` heartbeat the watchdog acts on
+   promptly, never waiting out max-life); arms the guest max-life (verify
+   on-VM: `sudo shutdown --show`). Then start the box-side watchdog:
    `nohup python3 poc/gcp/f1k_gcp.py watchdog --max-hours 8 &` — verify
    `pgrep -f 'f1k_gcp.py watchdog'` (plan §9: never agent-held).
 3. Worker STAGE + BUILD + KaE bring-up + **dump bring-up gate**:
@@ -88,26 +95,55 @@ maintainer), **NOT a retry** — the pzb6 class discovered at bring-up.
      the literal `PASS` into `tiny-dump.status`/`moe-sum-crosscheck.status`
      and re-runs the worker's collect command (no re-timing) — a
      `RUNNER-CONFIRM-REQUIRED` scaffold status makes `gate` STOP.
-4. **Bring-up affordability gate** (`F1K-BRINGUP-GATE-FIX.md` v1): the worker
-   tokenizes the frozen corpora (measured **f** + per-item T), times the frozen
-   stratified REAL-corpus sample per-item (T1 unpinned → bring-up pin at
-   measured PIN_GB → T2 pinned), and writes `gate-inputs.json`; then on the
+4. **Bring-up affordability gate** (`F1K-BRINGUP-GATE-FIX.md` v1+REV-B): the
+   worker tokenizes the frozen corpora (measured **f** + per-item T), times
+   the frozen stratified REAL-corpus sample per-item (T1 unpinned with
+   **one `STATS=<file>` per run**, merged fail-closed over an explicit
+   manifest → bring-up pin at measured PIN_GB → T2 pinned, per-run
+   engagement banner recorded), and writes `gate-inputs.json`; then on the
    control box `f1k_gcp.py gate --inputs <pulled gate-inputs.json>` — **GREEN
    (exit 0) is the ONLY license for construction spend**; STOP = mandatory
    maintainer surface (plan §7). Caps are tested **reserve-inclusive**
    (+$8 / +$8÷rate hours [STIPULATED plan §8 reserve]; floors compute-only);
-   dump (a)/(b)/(c) + functional PASS are hard conjuncts; `--replace` tests
-   the 21,537 envelope and ANY tested STOP exits nonzero. The synthetic
-   blend + `f1k_gcp.py affordability` remain a SECONDARY diagnostic,
-   licensing nothing (exit 3 even when clean).
-5. **Construction** (gated on 3+4): `build_carriers.py construct --mode real
+   dump (a)/(b)/(c) + functional PASS are hard conjuncts; **per-T2-run
+   pin-ENGAGEMENT evidence for the bound sha/PIN_GB is a hard conjunct**
+   (landed ASM-2513 banner grammar) and **regime `unpinned` is REFUSED**
+   (shape (ii) rejected); `--replace` tests the 21,537 envelope and ANY
+   tested STOP exits nonzero. The synthetic blend + `f1k_gcp.py
+   affordability` remain a SECONDARY diagnostic, licensing nothing (exit 3
+   even when clean).
+5. **Construction** (gated on 3+4): FIRST fetch + byte-verify the licensed
+   pin and take the EXPLICIT env exports — never ambient:
+   `python3 poc/gcp/f1k_gcp.py pin-fetch --gate bringup-gate.json --out
+   <rundir>` (fail-closed: GREEN artifact only; fetched bytes must sha-match
+   `pin.pin_file_sha256`; prints `export PIN=<path>` + `export
+   PIN_GB=<licensed>`). THEN `build_carriers.py construct --mode real
    --layers 3,…,77` (the landed ASM-2504 DRAFT=0 geometry, 75 layers) with the
    three provenance shas **and their artifacts**
    (`--tokenizer-sha/-artifact`, `--engine-weights-sha/-artifact`,
-   `--dump-patch-sha/-artifact`), 4,608 passes EXACT; `verify --expect-mode
-   real` (full cell-by-cell re-derivation, the #46 guarantee); commit the
-   realized tables + `norms.json` + `construction-report.json` = **B0**,
-   completing `f1k-carriers-v1`. Pin `glm52-weights` (ASM-1971 ops amendment).
+   `--dump-patch-sha/-artifact`), 4,608 passes EXACT, run with
+   `STATS=<rundir>/stats/item-<n>.stats` per pass (one file each, manifest
+   recorded — the free full-corpus derivation input); the runner runs the
+   **early-abort checkpoints** at n_done 200/1024/2304
+   (`f1k_bringup_gate.py checkpoint --gate bringup-gate.json --tokens
+   <gate-tokens/tokens-full.jsonl> --n-done N --elapsed-s S` — STOP exit 2 =
+   kill construction, maintainer surface; first exposure ≈ $1.3);
+   `verify --expect-mode real` (full cell-by-cell re-derivation, the #46
+   guarantee); commit the realized tables + `norms.json` +
+   `construction-report.json` = **B0**, completing `f1k-carriers-v1`. Pin
+   `glm52-weights` (ASM-1971 ops amendment).
+   **Construction→pilot pin boundary** (the ONLY lawful pin-change point):
+   IF the full-corpus pin (merged from the 4,608 per-pass stats via
+   `pinfile --stats-manifest`, fail-closed) is to replace the bring-up pin,
+   that is a DELIBERATE, RECORDED re-binding: the coordinator commits
+   `campaign-pin-rebind.json` {old_sha = the licensed pin sha, new_sha,
+   PIN_GB **unchanged** (fixed once at bring-up — the landed driver refuses
+   a PIN_GB drift), stats manifest sha, authorization: maintainer sign-off}
+   to GCS + the run log BEFORE pilot start, and the pilot config carries the
+   NEW pin; the landed ASM-2513 machinery (Ledger cross-phase basis +
+   `check_addendum_pinning` + spend-start sentinel) then enforces constancy
+   across pilot/guard/test. No rebind record → the licensed bring-up pin
+   runs the whole campaign. Never mid-phase, never silent.
 6. **Pilot** (`f1k_driver.py --phase pilot`): produces `addendum-5-frozen-lg`,
    `addendum-7-affordability`, `addendum-6-inputs` (dev δ̂, the dev
    sign-symmetry check). **HANDOFF**: the addendum-(6) inference method
```
<!-- END-ARTIFACT D12 -->

### B8.5 D13 — `poc/glm52-probe/f1k-harness/f1k_driver.py` driver delta (F5/GAP-3b: Add7Model + reserve-inclusive per-item addendum-(7))

<!-- BEGIN-ARTIFACT D13 f1k_driver.py.rev-b.diff sha256=88e9380416845e64adb258ae020e5d6f3b14df93cd6de98976b22c5840a44a1c -->
```diff
diff --git a/poc/glm52-probe/f1k-harness/f1k_driver.py b/poc/glm52-probe/f1k-harness/f1k_driver.py
index 797a919..6604425 100755
--- a/poc/glm52-probe/f1k-harness/f1k_driver.py
+++ b/poc/glm52-probe/f1k-harness/f1k_driver.py
@@ -269,6 +269,24 @@ USD_CAP = 155.0
 #   [R6-3] [REG budget.usd_cap = 155; ASM-2374 REVISION-6 ceiling,
 #    successor of the $149 ASM-2283/ASM-2205 ceiling — see WORST_CASE_*
 #    below for the recomputed 96/1573 worst-case arithmetic]
+WALL_CLOCK_CAP_HOURS = 900.0
+#   [REG budget wall-clock cap, ASM-2374 — the REV-B addendum-(7)
+#    projection tests instance-hours against this cap too]
+RESERVE_USD_ADD7 = 8.0
+#   [REV-B ASM-2516; F1K-BRINGUP-GATE-FIX.md SSA2/SSB] the plan-SS8 $8
+#   staging/overhead + ~5% preemption-rework reserve, charged AGAINST the
+#   caps in the addendum-(7) projection (usd + 8 <= 155 AND hours + 8/rate
+#   <= 900, at central AND +1SE) — the SAME reserve rule as the bring-up
+#   gate (ASM-2515): ONE projection model + ONE reserve rule at BOTH
+#   seams. The FULL $8 is kept even though part of the overhead is
+#   already inside usd_spent_prior by pilot time [STIPULATED,
+#   conservative-only].
+ADD7_KAPPA_BOUNDS = (0.5, 2.0)
+#   [REV-B ASM-2516, STIPULATED] admissible realized/model-predicted pilot
+#   throughput ratio; outside -> the frozen gate model does not transfer
+#   to the realized campaign -> ERR_F1K_AFFORD (maintainer surface).
+#   Enforced only for a REAL gate artifact (the $0 mock's stub timings
+#   carry no meaningful level; a mock artifact never licenses anything).
 SPOT_RATE_DEFAULT = 0.28
 #   [COST: $0.28/h spot i4i.2xlarge, the pessimistic corner of $0.20-0.28]
 PILOT_DEV_SUBSET_N = 48
@@ -2643,6 +2661,130 @@ def phase_test(cfg, ev, outdir, frozen, passes, ledger, mock_gold_dir=None,
     return rows_path, n_new
 
 
+class Add7Model:
+    """[REV-B GAP-3b / gate-fix review #1; ASM-2516] The FROZEN bring-up
+    gate projection model (kot-f1k-bringup-gate/1) consumed at the
+    pilot->main seam — ONE projection model, stated once (ASM-2514/2515),
+    used by BOTH seams. Inputs (config.affordability, REQUIRED for a real
+    campaign, every path sha-verified fail-closed):
+      tokens_full_path/_sha256   the gate run's tokens-full.jsonl sidecar
+                                 (per-item T for every frozen text; its
+                                 sha is recorded in bringup-gate.json)
+      gate_artifact_path/_sha256 the GREEN bringup-gate.json (isotonic
+                                 knots + cont addend + SE rule)
+    The seam RE-LEVELS the frozen s_hat(T) SHAPE by kappa = realized pilot
+    s/prefill DIVIDED BY the model-predicted pilot blend (prefill-weighted
+    over the pilot population), then sums PER ITEM over the remaining
+    main/guard prefills at their measured token counts — never one blended
+    average times a prefill count (v3-review finding 3 lineage). kappa
+    outside ADD7_KAPPA_BOUNDS on a REAL artifact -> fail-closed (model
+    does not transfer). Below the min knot: CONSTANT (cap-conservative);
+    above the max knot: fail-closed (the campaign max-T text was sampled
+    by construction). Mirrors f1k_bringup_gate.project exactly."""
+
+    def __init__(self, cfg):
+        blk = cfg.get("affordability") or {}
+        for k in ("tokens_full_path", "tokens_full_sha256",
+                  "gate_artifact_path", "gate_artifact_sha256"):
+            if not blk.get(k):
+                fail("ERR_F1K_AFFORD",
+                     "config.affordability.%s is REQUIRED [REV-B "
+                     "ASM-2516]: the addendum-(7) projection consumes the "
+                     "FROZEN bring-up gate model + per-item token counts "
+                     "— no silent fallback to a blended average" % k)
+        for pk, sk in (("tokens_full_path", "tokens_full_sha256"),
+                       ("gate_artifact_path", "gate_artifact_sha256")):
+            got = sha256_file(blk[pk])
+            if got != blk[sk]:
+                fail("ERR_F1K_AFFORD",
+                     "affordability input %s sha %s != declared %s — the "
+                     "seam never consumes unverified model inputs"
+                     % (blk[pk], got, blk[sk]))
+        art = json.loads(Path(blk["gate_artifact_path"])
+                         .read_text(encoding="utf-8"))
+        self.mock = (art.get("tokenizer") or {}).get("mode") != "REAL"
+        if self.mock and blk.get("_allow_mock") is not True:
+            fail("ERR_F1K_AFFORD",
+                 "gate artifact tokenizer mode is not REAL and "
+                 "_allow_mock is unset — a mock gate model never enters "
+                 "a real campaign projection")
+        self.knots = sorted(art["model"]["knots_isotonic"],
+                            key=lambda k: k["T"])
+        if not self.knots:
+            fail("ERR_F1K_AFFORD", "gate artifact carries no knots")
+        self.cont = art["model"]["cont_tokens_addend"]
+        self.art_sha = blk["gate_artifact_sha256"]
+        self.tp = {}
+        for ln in open(blk["tokens_full_path"], encoding="utf-8"):
+            if ln.strip():
+                e = json.loads(ln)
+                self.tp[e["key"]] = e["T"] + self.cont
+
+    def _interp(self, t, field):
+        ks = self.knots
+        if t > ks[-1]["T"] + 1e-9:
+            fail("ERR_F1K_AFFORD",
+                 "T=%.0f above the max sampled knot %.0f — extrapolation "
+                 "above the frozen sample is FORBIDDEN (the campaign "
+                 "max-T text is in the sample by construction)"
+                 % (t, ks[-1]["T"]))
+        if t <= ks[0]["T"]:
+            return ks[0][field]
+        for i in range(len(ks) - 1):
+            if t <= ks[i + 1]["T"]:
+                fr = (t - ks[i]["T"]) / max(1e-9,
+                                            ks[i + 1]["T"] - ks[i]["T"])
+                return ks[i][field] + fr * (ks[i + 1][field] - ks[i][field])
+        return ks[-1][field]
+
+    def s_hat(self, t, hi=False):
+        if hi:
+            return self._interp(t, "s") + self._interp(t, "se")
+        return self._interp(t, "s")
+
+    def tp_of(self, key):
+        if key not in self.tp:
+            fail("ERR_F1K_AFFORD",
+                 "no token count for %r in the gate tokens-full sidecar "
+                 "— the per-item projection never guesses a length" % key)
+        return self.tp[key]
+
+    def kappa(self, realized_s_per_prefill, ev):
+        num, den = 0.0, 0
+        for it in ev["dev"]:
+            num += self.s_hat(self.tp_of("pilot:%s" % it["item_id"]))
+            den += 1
+        if den == 0 or num <= 0:
+            fail("ERR_F1K_AFFORD", "no pilot entries to calibrate kappa")
+        k = realized_s_per_prefill / (num / den)
+        if not self.mock and not (ADD7_KAPPA_BOUNDS[0] <= k
+                                  <= ADD7_KAPPA_BOUNDS[1]):
+            fail("ERR_F1K_AFFORD",
+                 "kappa %.4f outside %s — the frozen gate model does not "
+                 "transfer to the realized pilot throughput; maintainer "
+                 "surface, never a silent projection [REV-B ASM-2516]"
+                 % (k, list(ADD7_KAPPA_BOUNDS)))
+        return k
+
+    def remaining_seconds(self, ev, d3_def, rep, kappa, hi=False):
+        """Per-item seconds for the REMAINING main + guard prefills."""
+        passes = main_arm_passes(d3_def, rep)
+        n_tmpl = sum(1 for a, _, _ in passes if a != "d3-text")
+        n_d3 = sum(1 for a, _, _ in passes if a == "d3-text")
+        n_guard = len(main_arm_passes(True, rep))
+        tot = 0.0
+        for it in ev["test"]:
+            tot += n_tmpl * self.s_hat(
+                self.tp_of("main-tmpl:%s" % it["item_id"]), hi)
+            if n_d3:
+                tot += n_d3 * self.s_hat(
+                    self.tp_of("main-d3:%s" % it["item_id"]), hi)
+        for it in ev["guard"]:
+            tot += n_guard * self.s_hat(
+                self.tp_of("guard:%s" % it["item_id"]), hi)
+        return tot * kappa
+
+
 def check_addendum_pinning(add7, cfg):
     """[ASM-2513 v3, re-review #3] The pilot addendum-7 is the THIRD
     cross-phase pin state (beside the cost ledger and the per-phase
@@ -3348,23 +3490,46 @@ def phase_pilot(cfg, ev, outdir, ledger, mock_gold_dir=None):
     # ---- 4. bring-up affordability gate (addendum (7)) --------------------
     # [FIX-7] resume-safe timing: the ledger's accumulated pilot seconds/
     # prefills, never a per-invocation stopwatch.
+    # [REV-B GAP-3b, F1K-BRINGUP-GATE-FIX.md SSB / ASM-2516] PER-ITEM
+    # token-aware + RESERVE-INCLUSIVE: the FROZEN bring-up gate model
+    # s_hat(T) (ASM-2514/2515), re-levelled by the realized pilot
+    # throughput (kappa), summed per item over the remaining main/guard
+    # prefills at their measured token counts, and tested against BOTH
+    # caps (+$8 / +8/rate hours) at central AND +1SE — never one blended
+    # average times a prefill count (the v3-review finding-3 failure
+    # mode), and never reserve-blind. ONE projection model at both seams.
     pilot_s = ledger.phase_seconds("pilot")
     pilot_pf = ledger.phase_prefills("pilot")
     s_per_prefill = pilot_s / max(pilot_pf, 1)
     rate = ledger.d["spot_rate_usd_per_hour"]
     prior = ledger.d["usd_spent_prior"]
+    a7m = Add7Model(cfg)
+    kappa = a7m.kappa(s_per_prefill, ev)
+    reserve_h = RESERVE_USD_ADD7 / rate
+    base_h = ledger.d["construction_instance_hours"] + pilot_s / 3600.0
     steps_taken = [DEGRADATION_ORDER[0]]
     d3_deferred = False
     replace_candidate = (decision == "RUN")
 
     def projection(d3_def, rep):
-        n_main = N_TEST * len(main_arm_passes(d3_def, rep))
-        n_guard = GUARD_N * len(main_arm_passes(True, rep))
-        return prior + pilot_s / 3600.0 * rate \
-            + (n_main + n_guard) * s_per_prefill / 3600.0 * rate
-
-    proj = projection(d3_deferred, replace_candidate)
-    if proj > USD_CAP and replace_candidate:
+        """(usd_c, usd_hi, hours_c, hours_hi): prior + realized pilot +
+        the PER-ITEM projected remainder (central / +1SE knots)."""
+        sec_c = a7m.remaining_seconds(ev, d3_def, rep, kappa)
+        sec_hi = a7m.remaining_seconds(ev, d3_def, rep, kappa, hi=True)
+        return (prior + (pilot_s + sec_c) / 3600.0 * rate,
+                prior + (pilot_s + sec_hi) / 3600.0 * rate,
+                base_h + sec_c / 3600.0,
+                base_h + sec_hi / 3600.0)
+
+    def cap_breach(p4):
+        u_c, u_hi, h_c, h_hi = p4
+        return (u_c + RESERVE_USD_ADD7 > USD_CAP
+                or u_hi + RESERVE_USD_ADD7 > USD_CAP
+                or h_c + reserve_h > WALL_CLOCK_CAP_HOURS
+                or h_hi + reserve_h > WALL_CLOCK_CAP_HOURS)
+
+    proj4 = projection(d3_deferred, replace_candidate)
+    if cap_breach(proj4) and replace_candidate:
         # §R6 step 2: defer REPLACE (overrides an NI-gate RUN — recorded)
         steps_taken.append(DEGRADATION_ORDER[1])
         replace_candidate = False
@@ -3372,16 +3537,17 @@ def phase_pilot(cfg, ev, outdir, ledger, mock_gold_dir=None):
         replace_gate["decision"] = "DEFER"
         replace_gate["reason"] += (" | OVERRIDDEN to DEFER by the §R6 "
                                    "step-2 affordability degradation")
-        proj = projection(d3_deferred, replace_candidate)
+        proj4 = projection(d3_deferred, replace_candidate)
     elif not replace_candidate:
         steps_taken.append(DEGRADATION_ORDER[1] +
                            " [already deferred by the NI gate]")
-    if proj > USD_CAP:
+    if cap_breach(proj4):
         # [FIX-4] step 3: defer d3-text — recorded AND honored in execution
         steps_taken.append(DEGRADATION_ORDER[2])
         d3_deferred = True
-        proj = projection(d3_deferred, replace_candidate)
-    affordable = proj <= USD_CAP
+        proj4 = projection(d3_deferred, replace_candidate)
+    affordable = not cap_breach(proj4)
+    proj = proj4[0]      # central usd (legacy field/message basis)
     add7 = {
         "addendum": "(7) bring-up s/prefill + affordability/semantic "
                     "PRE-test gate [§R-REV4.2 step 5]",
@@ -3395,6 +3561,30 @@ def phase_pilot(cfg, ev, outdir, ledger, mock_gold_dir=None):
         "expert_pinning": attested_pinning(ledger),      # [FIX-5+ASM-2513]
         "projected_total_usd": round(proj, 2),
         "usd_cap": USD_CAP,
+        "projection_rev_b": {                            # [REV-B ASM-2516]
+            "model": "kot-f1k-bringup-gate/1 frozen knots (gate artifact "
+                     "sha %s) re-levelled by kappa; per-item over "
+                     "remaining main/guard prefills; ONE model at both "
+                     "seams" % a7m.art_sha[:16],
+            "kappa_realized_over_predicted": round(kappa, 4),
+            "kappa_bounds": list(ADD7_KAPPA_BOUNDS),
+            "usd_total": {"central": round(proj4[0], 2),
+                          "hi": round(proj4[1], 2)},
+            "instance_hours": {"central": round(proj4[2], 1),
+                               "hi": round(proj4[3], 1)},
+            "reserve": {"usd": RESERVE_USD_ADD7,
+                        "hours_at_rate": round(reserve_h, 2),
+                        "rule": "caps reserve-inclusive at central AND "
+                                "+1SE; same rule as the bring-up gate "
+                                "(ASM-2515)"},
+            "wall_clock_cap_hours": WALL_CLOCK_CAP_HOURS,
+            "per_average_RETIRED_usd": round(
+                prior + pilot_s / 3600.0 * rate
+                + (N_TEST * len(main_arm_passes(d3_deferred,
+                                                replace_candidate))
+                   + GUARD_N * len(main_arm_passes(True,
+                                                   replace_candidate)))
+                * s_per_prefill / 3600.0 * rate, 2)},
         "degradation_order": list(DEGRADATION_ORDER),
         "degradation_steps_applied": steps_taken,
         "d3_text_deferred": d3_deferred,                      # [FIX-4]
@@ -3464,6 +3654,12 @@ def phase_pilot(cfg, ev, outdir, ledger, mock_gold_dir=None):
             "pass": placebo_ok},
         "affordability_gate": {"pass": affordable,
                                "projected_total_usd": round(proj, 2),
+                               "projected_total_usd_hi": round(proj4[1], 2),
+                               "projected_hours": round(proj4[2], 1),
+                               "projected_hours_hi": round(proj4[3], 1),
+                               "reserve_usd": RESERVE_USD_ADD7,
+                               "rule": "reserve-inclusive caps at central "
+                                       "AND +1SE [REV-B ASM-2516]",
                                "usd_cap": USD_CAP},
         "semantics_gate": {"pass": sem_ok,
                            "rule": "ASM-1971 colibri knob-semantics "
@@ -3489,9 +3685,13 @@ def phase_pilot(cfg, ev, outdir, ledger, mock_gold_dir=None):
              "§R-REV4.2)")
     if not affordable:
         fail("ERR_F1K_AFFORD",
-             "bring-up projection $%.2f exceeds the $%.0f ceiling after the "
-             "full degradation order — STOP and return to the maintainer "
-             "[§R6/§R-REV4.2]" % (proj, USD_CAP))
+             "addendum-(7) RESERVE-INCLUSIVE per-item projection breaches "
+             "a cap after the full degradation order (central $%.2f / +1SE "
+             "$%.2f vs $%.0f-$%.0f-reserve; %.1f / %.1f h vs %.0f h - "
+             "%.1f h reserve) — STOP and return to the maintainer "
+             "[§R6/§R-REV4.2; REV-B ASM-2516]"
+             % (proj4[0], proj4[1], USD_CAP, RESERVE_USD_ADD7,
+                proj4[2], proj4[3], WALL_CLOCK_CAP_HOURS, reserve_h))
     print("pilot: gates -> power OK, placebo OK (p=%.3f), semantics OK, "
           "affordability OK ($%.2f <= $%.0f); REPLACE %s"
           % (d0_p, proj, USD_CAP, decision))
@@ -3669,6 +3869,42 @@ def gen_mock_fixtures(outdir):
                 for i in range(128)),
         encoding="utf-8")
 
+    # [REV-B ASM-2516] mock bring-up gate MODEL + tokens-full sidecar: the
+    # addendum-(7) pilot->main seam consumes the SAME frozen model as the
+    # bring-up gate — the $0 oracle exercises the sha-verify + per-item +
+    # reserve-inclusive path end-to-end. SHAPED mock (tokenizer mode MOCK,
+    # _allow_mock; NEVER a license input): knot s-level ~stub scale, kappa
+    # unbounded under mock (a real artifact enforces ADD7_KAPPA_BOUNDS).
+    tokens_path = fx / "mock-tokens-full.jsonl"
+    with open(tokens_path, "w", encoding="utf-8") as f:
+        for iid in split_ids["test"]:
+            f.write(json.dumps({"key": "main-tmpl:%s" % iid,
+                                "pop": "main-tmpl", "m": 7, "W": 24,
+                                "T": 24}) + "\n")
+            f.write(json.dumps({"key": "main-d3:%s" % iid,
+                                "pop": "main-d3", "m": 1, "W": 27,
+                                "T": 27}) + "\n")
+        for iid in split_ids["dev"]:
+            f.write(json.dumps({"key": "pilot:%s" % iid, "pop": "pilot",
+                                "m": 22, "W": 24, "T": 24}) + "\n")
+        for iid in split_ids["guard"]:
+            f.write(json.dumps({"key": "guard:%s" % iid, "pop": "guard",
+                                "m": 11, "W": 24, "T": 24}) + "\n")
+    gate_art_path = fx / "mock-bringup-gate.json"
+    write_json(gate_art_path, {
+        "schema": "kot-f1k-bringup-gate/1", "_mock": True,
+        "verdict": "GREEN",
+        "tokenizer": {"mode": "MOCK", "sha256": None},
+        "model": {"knots_isotonic": [
+            {"stratum": "bin0", "T": 16.0, "s": 0.02,
+             "se": 0.002, "n": 4},
+            {"stratum": "max", "T": 64.0, "s": 0.03,
+             "se": 0.003, "n": 1}],
+            "cont_tokens_addend": 8},
+        "rate": {"usd_per_hour": SPOT_RATE_DEFAULT},
+        "pin": {"pin_file_sha256": None, "pin_gb": 48.0,
+                "regime": "pinned-bringup", "note": "MOCK artifact"}})
+
     cfg = {
         "engine": {
             "argv": [sys.executable, str(HERE / "mock_colibri.py")],
@@ -3779,6 +4015,15 @@ def gen_mock_fixtures(outdir):
         "cost": {"spot_rate_usd_per_hour": SPOT_RATE_DEFAULT,
                  "usd_spent_prior": 146.0,
                  "construction_instance_hours": 521.2},
+        # [REV-B ASM-2516] the addendum-(7) seam's REQUIRED model inputs
+        # (sha-verified fail-closed; a REAL campaign points these at the
+        # landed gate run's artifacts, shas from bringup-gate.json)
+        "affordability": {
+            "tokens_full_path": str(tokens_path),
+            "tokens_full_sha256": sha256_file(tokens_path),
+            "gate_artifact_path": str(gate_art_path),
+            "gate_artifact_sha256": sha256_file(gate_art_path),
+            "_allow_mock": True},
     }
     cfg_path = fx / "mock-config.json"
     write_json(cfg_path, cfg)
```
<!-- END-ARTIFACT D13 -->

## B9. Consolidated coordinator runbook **[SUPERSEDED by §C.7 — apply D1–D18, oracle 37/37; this D1–D13-only sequence would land with the rereview's STILL-OPEN findings open, and its `--outdir /tmp/f1k-mock-revb` mock line is REFUSED by the landed kot-log/1 repo-root containment ([MEASURED] §C.6) — do not lift]**

```bash
cd /home/ec2-user/css/kernel/kernel-of-truth   # tree at/after 2574c82b (seq-3 LANDED)
M=poc/gcp/F1K-BRINGUP-GATE-FIX.md
for N in D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13; do
  awk -v n="$N" '$0 ~ ("^<!-- BEGIN-ARTIFACT " n " ") {f=1; next} \
      $0 ~ ("^<!-- END-ARTIFACT " n " -->") {f=0} f' "$M" | sed '1d;$d' > /tmp/$N.out
done
sha256sum /tmp/D*.out    # must match the §3 + §A4 + §B8 tables EXACTLY
cp /tmp/D1.out poc/gcp/f1k_bringup_gate.py && chmod 644 poc/gcp/f1k_bringup_gate.py
for DN in D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13; do git apply /tmp/$DN.out; done
bash -n poc/gcp/f1k_worker.sh
python3 -m py_compile poc/gcp/f1k_gcp.py poc/gcp/f1k_bringup_gate.py \
  poc/glm52-probe/f1k-harness/f1k_driver.py
python3 poc/gcp/f1k_gcp.py gate --selftest      # expect 28 "ok:" lines + PASS, exit 0
python3 poc/gcp/f1k_gcp.py affordability --rate 0.17394 --s-per-prefill 149.1 --replace; echo $?  # 2
python3 poc/gcp/f1k_gcp.py affordability --rate 0.17394 --s-per-prefill 149.1; echo $?            # 3
( cd poc/glm52-probe/f1k-harness && python3 f1k_driver.py --mock --outdir /tmp/f1k-mock-revb )
#   expect: MOCK VALIDATION PASS, exit 0 (delete /tmp/f1k-mock-revb after — ~2.4 GB)
python3 poc/gcp/f1k_gcp.py plan                 # regression: DRY-PLAN OK unchanged
# ONE plain-infra commit: this memo + the five patched files + ASM-2514 + ASM-2515 (as amended
# in-memo) + ASM-2516; tools/registry/registry-check.py green (nothing frozen is touched).
```

Acceptance gate: review green → extract (sha-verified, 13 artifacts) → apply D1–D13 → oracle
28/28 + the two exit-code probes + driver mock green + `plan` green → ONE commit (three ASM
rows) → registry-check green. The tree is at seq-3-landed; if it has drifted beyond
`2574c82b`'s state on the five target files, STOP and re-baseline (§0 rule).

## B10. ASM-2516 registration text **[registers AS WRITTEN, but ONLY together with ASM-2517 (§C.8), which amends its items (3)/(4)/(6) in the same landing commit — never register 2516 alone]** (register-at-commit WITH ASM-2514/2515; next free id
[MEASURED this pass: assumptions.jsonl tail = ASM-2513 (registered, landed); 2514/2515 reserved
by this memo, absent from the file; 2516 free])

```json
{"id": "ASM-2516", "tag": "STIPULATED", "load_bearing": true, "claim": "F1-K BRING-UP GATE REV-B (amends ASM-2514/ASM-2515 in the same landing commit; closes the cross-model gate-fix review poc/gpt56-review/f1k-gate-fix-review-VERDICT.md, overall REJECT, findings 6/9 AGREE kept byte-stable): (1) T1 PIN DERIVATION - the engine interface is STATS=<file> (kae-add-path.patch:175/:180/:183, verified from the patch bytes; stats_dump truncate-vs-append stays fetch-grade ASM-1971 and the design is correct under either): one STATS=<per-item file> per T1 run (rm-first, non-empty asserted), an EXPLICIT manifest, a fail-closed merge = SUM of counts per (layer,expert) over ALL files (any missing/empty/malformed file refuses - no skipping), derivation provenance {n_files, per-file sha256+lines, manifest sha} recorded in the gate artifact; pinfile's glob flag is REMOVED. (2) TIMING MANIFEST - score lines are (ctx=T, cont=8, T+8 ids: text ids + 8 repeats of the final id), so the engine processes exactly the model's Tp = T+8; collect STRUCTURALLY enforces ctx+cont == Tp == len(ids) per manifest, fail-closed. (3) SHAPE-(i) END-TO-END - the verdict REFUSES regime unpinned (shape (ii) rejected; the ASM-2515(4) unpinned-T2 fallback is WITHDRAWN - an underivable pin is a worker fail-closed STOP); per-T2-run pin-ENGAGEMENT evidence is a hard conjunct, verified with the LANDED driver grammar (PIN_ARMED_RE/PIN_DISABLED_MARKERS imported from f1k_driver.py - the ASM-2513 machinery landed at 2574c82b; ONE grammar, one bring-up alignment covers both consumers): armed banner per run, pinned>=1, used>0, used<=budget*1.01, budget==bound PIN_GB (1%), source==bound pin path; campaign-pin persistence is VERIFIED (GCS re-read sha == licensed sha, no || true, + derivation sidecar); construction binding is EXPLICIT via f1k_gcp.py pin-fetch (GREEN artifact required, fetched bytes sha-verified, prints export PIN/PIN_GB with the LICENSED values - never ambient env); construction->pilot full-corpus re-derivation is concrete (per-pass STATS files + manifest + the same fail-closed merge) and a boundary pin CHANGE requires a coordinator-committed campaign-pin-rebind.json {old_sha=licensed, new_sha, PIN_GB UNCHANGED, stats manifest sha, maintainer authorization} before pilot start, after which the landed Ledger/addendum-7/spend-start machinery enforces constancy - never mid-phase, never silent. (4) HONESTY + EARLY-ABORT - the +-1SE band bounds SAMPLING error of the 30-text sample only, NOT selection bias (T1 subset of T2, 8/30 optimistic) NOR unseen-tail behaviour (a gate-passing pin can underperform over 4,608); mitigation: construction early-abort checkpoints at n_done {200,1024,2304} (f1k_bringup_gate.py checkpoint: licensed knots re-levelled by realized/predicted elapsed over the first n_done manifest-order items, ratio sane (0,10], reserve-inclusive re-projection at central AND +1SE, STOP exit 2 on breach; realized figures ARE the landed Ledger's REQUIRED cost basis; first exposure ~$1.3). (5) FRESH-WORKER DEPLOY - google-cloud-cli/gsutil + python3-pip installed-and-VERIFIED (gsutil retained over signed URLs: many dynamic writes, service-account auth); real-checks.sh contract met (pristine COLIBRI_TREE clone at a78a06fc exported; kae-patch-draft symlinked to the :37 ../../ expectation); RAID by STATE (mountpoint -q; md0 re-assemble+mount on reboot, mkfs only at creation); detached launch via generated f1k_launch.sh so ANY worker failure (set -e deaths included) writes a FAILED heartbeat the watchdog acts on promptly. (6) DRIVER SEAM (GAP-3b, closes the review's finding 1; supersedes the SS5.3 separate-landing text) - f1k_driver.py addendum-(7) (landed :3348-3497) now projects PER ITEM with the FROZEN gate model: Add7Model consumes bringup-gate.json knots + the tokens-full.jsonl sidecar (paths+sha256 REQUIRED in config.affordability, verified fail-closed; mock artifacts need _allow_mock and never license), re-levelled by kappa = realized pilot s/prefill / model-predicted pilot blend (recorded; [0.5,2.0] fail-closed on a real artifact - the SS5.3 per-item-refit sketch is not implementable from the landed per-phase-aggregate ledger, disclosed deviation), reserve-inclusive caps ($+8 and 900h-8/rate) at central AND +1SE, degradation order off the reserve-inclusive breach, per-average printed RETIRED-only; ONE projection model + ONE reserve rule at both seams. (7) ORACLE - case 8a re-derived to isolate the reserve delta (central $147.80 AND +1SE $153.81 both <= $155 raw, +$8 breaches -> the old rule GOes on every band it tested, the reserve alone flips); new $0 cases: merge correctness + refusals, manifest structural consistency + old-convention refusal, engagement refusals, unpinned-regime refusal, checkpoint CONTINUE/STOP; selftest re-scoped HONESTLY (logic seams only; no real engine/tokenizer/GCS/VM claim). Single-VM wall-clocks stated: ~27.1/31.7/37.7 days for the SSA1 cost rows. Bench: D1-D13 apply clean on the LANDED tree (byte-identical fresh-chain reproduction; result shas recorded), oracle 28/28, driver $0 --mock green end-to-end (23 [PASS], projection_rev_b emitted), affordability probes exit 2/3, plan green.", "rationale": "The gate-fix review proved the composite's remaining executable seams could still license on mislabeled or unrepresentative evidence (pin from the LAST T1 item; timings measuring t labeled t+8), fail to carry the licensed pin into construction (unverified upload, ambient env), run dead on a fresh worker, stall at the NEXT gate on the deferred driver projection, and present a stale supersession surface. Every REV-B change is fail-closed-only relative to the prior code (GO can become STOP, never the reverse) on unpinned infra files; the frozen scientific record is untouched.", "backing_ref": "poc/gcp/F1K-BRINGUP-GATE-FIX.md REV-B SSB (this freeze; D9-D13 + bench evidence); poc/gpt56-review/f1k-gate-fix-review-VERDICT.md; kae-add-path.patch:175,:180,:183 (STATS=<file>); dump-patch/real-checks.sh:37,:43,:47 + bringup_gcp.sh:24 (fresh-worker contract); f1k_driver.py landed 2574c82b :1714 (aggregate-only ledger), :1927 (PIN_ARMED_RE), :1947 (check_pin_engagement), :3348-3497 (addendum-7 seam); accum20.stats format + m4.json per_expert_bytes; ASM-1971 (fetch-grade riders), ASM-2513 (REGISTERED+landed pin machinery), ASM-2514/ASM-2515 (as amended in this memo), F1K-PIN-FILE-FIX.md v5", "status": "open", "owner": "designer-20", "date": "2026-07-18"}
```

## B11. REV-B self-check additions (rows 30–45; every claim → verified where → tag)

| # | Claim | Verified where (this REV-B pass) | Tag |
|---|---|---|---|
| 30 | Verdict read verbatim; all 9 findings mapped (B0); AGREE findings 6/9 kept byte-stable (D5-D8 artifact shas unchanged; D9 leaves the reserve/dump-conjunct lines untouched — diff inspected) | `f1k-gate-fix-review-VERDICT.md` full read; D9 hunk inspection | [MEASURED memo/diff state] |
| 31 | `STATS=<file>` interface: `stats=getenv("STATS")` + `stats_dump(&m,stats)` at patch :175/:180/:183; format `<layer> <expert> <count>` | `kae-add-path.patch` + `accum20.stats` read this pass | [MEASURED; truncate-vs-append fetch-grade, design robust to both] |
| 32 | real-checks contract: `KAE_DIR=$HERE/../../kae-patch-draft` (:37), `COLIBRI_TREE` required (:43), pristine blob verified (:47); pinned colibri commit `a78a06fc` (bringup_gcp.sh:24); landed worker invoked it with NEITHER | files read this pass; landed `f1k_worker.sh:158` | [MEASURED] |
| 33 | Driver seam re-located on the landed tree: :3351/:3360-3364/:3384/:3465/:3490; blended×count + USD-only confirmed pre-fix; D13 modifies no PIN-fix line (token grep = 0 modified lines; `attested_pinning` context-only) | landed `f1k_driver.py` read; `/tmp/D13.out` grep + hunk map | [MEASURED] |
| 34 | D9-D13 shas as tabled; full D1→D13 chain applies clean on the CURRENT landed bytes; fresh-chain reproduction byte-identical (`cmp` ×5); result shas 8824705b/cd7a5fbd/30e1ca18/20315815/49b2ab3b; post-D8 intermediates 228f5233/04927690/345d1b90/d8cdc611 with the gcp/README deviations explained (seq-3 landed lines) | two independent /tmp benches this pass | [MEASURED] |
| 35 | Oracle 28/28 incl. cases 11-15, through BOTH `gate --selftest` and direct invocation, on both benches | bench runs this pass | [MEASURED] |
| 36 | Case 8a isolation: central $147.80, +1SE $153.81, hours-hi ≤ 900, +$8 = $155.80 breach; all four conditions asserted in code | selftest output this pass | [MEASURED] |
| 37 | Driver $0 --mock on the applied tree: exit 0, 23 [PASS], MOCK VALIDATION PASS; projection_rev_b emitted (kappa 0.0369 mock-unbounded); affordability_gate reserve-inclusive | mock run + artifact reads this pass | [MEASURED] |
| 38 | Probes on the applied tree: affordability --replace exit 2 / clean exit 3; `plan` DRY-PLAN OK (pins verified) | bench runs this pass | [MEASURED] |
| 39 | ASM tail: 2513 REGISTERED (landed); 2514/2515 absent (reserved by this memo, amended in place pre-registration); 2516 free | `registry/assumptions.jsonl` tail read this pass | [MEASURED] |
| 40 | Wall-clocks: 651.0/24=27.1 d, 760.9/24=31.7 d, 905.6/24=37.7 d | arithmetic on the §A1 (AGREEd) rows | [EXTRAPOLATED] |
| 41 | Engagement grammar BOUND (imported from the landed driver, exercised by the selftest against the real landed `f1k_driver.py` bytes — the mock banner parses under the landed `PIN_ARMED_RE`) | selftest cases 13 + all-GREEN cases this pass | [MEASURED] |
| 42 | Checkpoint first exposure ≈ 200 × 137.2 s ≈ 7.62 h ≈ $1.33 at $0.17394/h | arithmetic on the f=1.45 row | [EXTRAPOLATED] |
| 43 | §5.3 refit not implementable from landed data: `Ledger.add` accrues per-phase aggregates only (:1714-1728); kappa deviation disclosed + STIPULATED | landed driver read this pass | [MEASURED code basis] |
| 44 | Memo-only pass: repo untouched except this file; no handles; NO spend/VM/git action | `git status` this pass | [MEASURED] |
| 45 | Supersession completeness: every finding-8-named stale item (base 14/14 next-action, nine-conjunct text, v2 refs, ASM-2515 vs 2513/2514) addressed inline or in B7 | this file, this pass | [MEASURED memo state] |

## B12. Summary (REV-B, whole composite) **[SUPERSEDED by §C.10 — three of its "closed" claims (construction binding, rebind, checkpoints) were prose-only per the rereview]**

- Gate-fix review REJECT closed: T1 pin now derives from the true T1 union (per-item
  `STATS=<file>` + fail-closed provenance-recorded merge); timing manifests measure exactly the
  labeled T+8 with a structural check; shape (i) is mechanically enforced end-to-end (unpinned
  REFUSED, per-run engagement evidence via the landed ASM-2513 grammar, sha-verified pin
  persistence, explicit `pin-fetch` construction binding, recorded boundary rebind, early-abort
  checkpoints replacing the unpriced "self-correcting" claim).
- Fresh-worker deploy is runnable (deps verified, `COLIBRI_TREE` + patch location provided,
  RAID by mount state, FAILED-heartbeat launcher); the driver's pilot→main projection is
  per-item + reserve-inclusive off the SAME frozen model (D13, same commit) — no deferred gap.
- Oracle honest: 28/28 with a true reserve-isolation regression + merge/manifest/engagement/
  regime/checkpoint cases; scope stated (logic seams only, no real engine/GCS/VM claim).
- All 13 artifacts sha-pinned and verified applying clean on the LANDED `2574c82b` tree
  (byte-identical fresh-chain reproduction); driver $0 mock green end-to-end; single-VM
  wall-clocks stated (~27.1/31.7/37.7 d); ONE plain-infra landing commit + ASM-2514/2515 (as
  amended) + ASM-2516. $0 spent; nothing applied by this pass.

~~BRINGUP-GATE-FIX REV-B DONE~~ **[superseded — the composite is DONE at REV-C; §C below]**

# §C — REV-C ADDENDUM: closing the rereview STILL-OPEN findings (delta diffs D14–D18 on top of D1–D13)

**Trigger:** `poc/gpt56-review/f1k-gate-fix-rereview-VERDICT.md` (round-2 cross-model review of
the v1+REV-A+REV-B composite; overall **REJECT**). Findings **1, 2, 6, 8 CLOSED** (T1 per-item
derivation + merge, timing manifest + structural check, oracle case 8a + cases 11–15, all 13
artifact chains) and the **D5/D6 predicate + cost table stay settled**: their artifact blocks
and the settled license-conjunct lines are **byte-stable** under D14–D18 ([MEASURED]: zero
REMOVED diff lines touch `hi_band_below_caps`/`central_*_in_window`/`lo_band_above_floors`/
dump-conjunct lines; zero removed lines carry the landed pin-machinery tokens
`validate_pinning`/`check_pin_engagement`/`PIN_ARMED_RE`/`attested_pinning`/spend-start; ONE
ADDED `validate_pinning` call site — the new Add7Model pin-identity check — disclosed).
Bench basis: the same LANDED `2574c82b` tree; every REV-C claim below re-verified on it.

## C0. Rereview finding → disposition map

| Rereview # | Finding | Disposition |
|---|---|---|
| 1 (nit) | `manifest_sha256` misnames a rows digest | **§C.4 + D14** (renamed `manifest_rows_sha256`; `manifest_file_sha256` added) |
| 3 | shape (i) not carried mechanically through construction (exports unconsumed; no engagement check; per-pass STATS impossible; rebind unconsumed; checkpoints unwired) | **§C.1 + D14/D15/D17 — THE FORK, decided: wrapper-level enforcement (option b)** |
| 4 (residual) | FAILED-heartbeat upload `\|\| true`; GCS-only visibility | **§C.2 + D15** (retry+backoff, local FAILED marker, watchdog SSH probe; residual stated) |
| 5 | D13 seams: second model implementation; unbound bundle; pilot stall; kappa unweighted; uniform-T mocks | **§C.3 + D14/D18** (shared block + sha; /2 model_bundle; config-affordability; realized-row kappa; heterogeneous/tamper/boundary mocks) |
| 7 | §B.7/§B.12 overstate executable successors | **§C.5** (rows relabelled implemented/deferred/removed; §B inline kills applied) |
| 2, 6, 8 | CLOSED | kept byte-stable (see trigger paragraph) |

## C1. Finding 3 — the construction-binding FORK, decided: **(b) wrapper-level enforcement, builder untouched**

**Decision, one sentence:** REV-C enforces shape (i) at a `guard` wrapper that binds the
byte-verified pin into the child env, proves engagement with a mode-exact pre-spend probe, and
runs the frozen checkpoints in-process — because that meets the whole bar (no unbound pin, no
unverified engagement, no legitimate stall, honest evidence) WITHOUT putting a seq-4 re-freeze
of the SHA-PINNED generator on the critical path.

**Why not (a) the seq-4 builder re-freeze:** it is the honest-but-heavy path and the seq-2
precedent shows it lands — but every byte it would buy on THIS landing (per-batch banner
evidence, per-batch STATS for full-corpus re-derivation) changes NO license decision this
round: engagement is established BEFORE the first construction pass by a dump-mode probe under
the exact env the builder inherits, and the inheritance itself is verified from the pinned
bytes (`build_carriers.py:634` `env = dict(os.environ)`, only `KAE_SCORE` popped — no other
env mutation in the file [MEASURED this pass]). A frozen-surface edit + full splice/oracle/ASM
machinery to buy evidence with no decision value is scope, not safety; it is DEFERRED as bead
**`kernel-of-truth-8cpm`** (filed this pass) and is NOT on the critical path. Every REV-C
change stays fail-closed-only on unpinned infra files; the frozen record is untouched and the
landing stays plain infra.

**The mechanism (D14 `cmd_guard` + helpers; runbook §C.7 / README step 5):**

1. **License binding, by bytes:** `guard --gate bringup-gate.json --pin <fetched pin> …`
   refuses unless the artifact is schema **`kot-f1k-bringup-gate/2`**, verdict GREEN, regime
   pinned-bringup, AND `sha256(pin bytes) == pin.pin_file_sha256` AND the guard's own shared-
   model block hashes to the artifact's `model_bundle.add7_src_sha256`. `PIN_GB` is taken FROM
   the artifact (the licensed value), never from a flag or the environment.
2. **Env explicit, never ambient:** the guard builds the child env itself — records+overrides
   any ambient `PIN`/`PIN_GB`, POPS `STATS` (with 96 batches sharing one ambient path and
   truncate-vs-append fetch-grade [ASM-1971], a single file would hold the LAST batch only —
   the F1 defect class; so no stats collection is HONESTLY none rather than silently wrong)
   and pops the mode knobs (`SCORE`/`KAE_SCORE`/`KAE_DUMP*`), then sets `PIN=<resolved
   path>`, `PIN_GB=<licensed>`.
3. **Pre-spend engagement PROBE, mode-exact (D14 `_probe_engagement`):** ONE minimal
   `KAE_DUMP` invocation of the SAME engine argv under the SAME env (a 4-id slot-0 manifest in
   exactly the grammar `run_dump` writes) — the probe runs in the CONSTRUCTION mode, so
   dump-mode arming is observed, not assumed. Its stderr must carry an armed banner under the
   LANDED driver grammar (`PIN_ARMED_RE`/`PIN_DISABLED_MARKERS` imported from
   `f1k_driver.py`, ASM-2513; wording stays fetch-grade ASM-1971 — one driver-regex alignment
   at bring-up covers all three consumers) with coherent counters: pinned ≥ 1, used > 0,
   used ≤ budget×1.01, budget == licensed PIN_GB (1%), source == the bound pin path; any
   disabled marker or nonzero exit REFUSES construction. Evidence artifact:
   `construction-pin-probe.json` (verbatim banner + checks + stderr tail). **Exposure bound:
   one engine start (~137 s scale ≈ <$0.01 at $0.17394/h), never a 4,608-pass campaign.**
4. **Launch + frozen checkpoints, in-process:** the guard launches the UNTOUCHED builder argv
   (own process group) with that verified env; the builder's per-concept checkpoint files
   (`concept-%03d.json`, one per 48-pass batch — the ONLY mechanical progress signal the
   pinned builder emits) drive `checkpoint_eval` at the re-frozen schedule
   **n_done ∈ {240, 1056, 2304}** (= 5/22/48 of 96 concepts; ASM-2517 amends ASM-2516(4)'s
   {200,1024,2304} pre-registration — those milestones were not OBSERVABLE at concept
   granularity). Off-schedule n_done is REFUSED (the schedule can no longer drift);
   `--n-start` (48-multiple) makes a RESUMED construction honest (this session's elapsed over
   this session's concepts). A reserve-inclusive breach at central OR +1SE kills the builder
   process group (SIGTERM→SIGKILL), writes `construction-abort.json`, exits 2. Exposures at
   the three checkpoints ≈ **$1.59 / $7.00 / $15.27** [EXTRAPOLATED, f=1.45 row: 240/1056/
   2304 × 137.2 s × $0.17394/h].
5. **Cost basis, mechanically transferred:** `construction-guard-final.json` records the
   session's realized hours/$ at the artifact rate; `config-cost --final <guard-final(s)>
   --prior-usd <pre-construction metered spend> --rate <campaign rate> --config
   run-config.json` (D14) writes `config.cost.{usd_spent_prior, construction_instance_hours}`
   — the landed Ledger's REQUIRED fail-closed basis — refusing conflicting existing blocks
   and refusing a `builder_exit != 0` final as a cost basis.
6. **Rebind file REMOVED; campaign pin = the licensed pin:** `campaign-pin-rebind.json` had no
   consumer (rereview #3) and REV-C makes a rebind UNREACHABLE anyway: the driver's Add7Model
   now REFUSES any campaign pin whose sha ≠ the gate artifact's (`ERR_F1K_PINNING`, D18), and
   the landed ASM-2513 machinery enforces constancy across pilot/guard/test. **Repricing,
   honest:** expected campaign cost is UNCHANGED (the §A1 rows already price the bring-up-
   measured f); what is FOREGONE is only the potential upside of a better full-corpus pin;
   the DOWNSIDE of an unrepresentative bring-up pin is throughput loss, bounded mechanically
   by the checkpoint aborts (≤ $1.59/$7.00/$15.27 marginal per stage) and the reserve-
   inclusive addendum-(7) gate before main spend.

**Honest residuals (stated, not hidden):** (i) the builder swallows per-batch engine stderr on
success (`build_carriers.py:640-660` reads it only for the KAE echo), so there is NO per-batch
banner evidence — engagement is proved at launch (probe) and inherited by a byte-verified
argument (:634 passthrough), not re-observed per batch; per-batch evidence + per-batch STATS
= the deferred seq-4 bead. (ii) The probe proves the engine ARMS under this env in dump mode;
an engine that arms at probe time but silently disarms mid-campaign is outside what any
wrapper can observe through the pinned builder — the checkpoint throughput guard is the
mechanical backstop for that class too.

## C2. Finding 4 residual — worker-death visibility without GCS (D15)

- `f1k_launch.sh` (generated in `bringup-deploy`) now, on ANY nonzero worker exit: (1) writes
  a LOCAL on-disk `~/f1k/FAILED` marker FIRST (unconditional), then (2) retries the GCS
  heartbeat upload 5× with exponential backoff (2..32 s) instead of one `|| true` shot.
- `watchdog` (control box): when the GCS heartbeat shows no FAILED, it additionally probes the
  VM over SSH for the local marker (`gcloud compute ssh … "test -f ~/f1k/FAILED && echo
  KOT-F1K-FAILED-LOCAL; true"`); the token triggers the same prompt teardown. A probe FAILURE
  is INCONCLUSIVE (boot/ssh flake) and never tears down by itself.
- **Honest residual:** a worker death on a VM unreachable via BOTH GCS and SSH stays invisible
  until the guest max-life backstop — stated in the launcher and watchdog comments.

## C3. Finding 5 — the D13 seams, bound (D14 + D18)

- **(i) ONE projection model, mechanically:** the interpolation/range semantics now live in a
  `KOT-ADD7-SHARED` block, **byte-identical** in `f1k_bringup_gate.py` and `f1k_driver.py`
  (decision: vendored copy + sha cross-check, NOT a cross-tree import — the driver must stay
  runnable on a VM where `poc/gcp` may not be synced, and an import would make the PINNED
  analysis surface depend on an unpinned path). Both files carry the frozen constant
  `ADD7_SRC_SHA256 = 9d3e1bc76f85…`; `project()` refuses to EMIT an artifact from a drifted
  copy; Add7Model refuses to CONSUME unless its own block sha == the constant == the
  artifact's `model_bundle.add7_src_sha256`. Oracle case 18 asserts gate-block == constant ==
  driver-block from the actual bytes; the driver mock cross-checks the gate copy too. Gate
  `_interp` and driver `Add7Model._interp` are now thin wrappers over `add7_interp` (each
  keeping only its own error surface).
- **(ii) the bundle BOUND:** SCHEMA bumped to **`kot-f1k-bringup-gate/2`**; `collect` records
  `tokens_full_sha256` (byte sha of the sidecar) and `project()` REQUIRES it, embedding
  `model_bundle {add7_src_sha256, tokens_full_sha256, rule}` in the artifact. Consumption
  (D18) now requires: schema `/2`, **verdict GREEN**, config-declared sidecar sha == the
  ARTIFACT-recorded value (bytes win over self-declaration), shared-model sha identity,
  **rate equality** (config cost rate == the artifact's licensed rate, exact), **pin
  identity** (REAL mode: `validate_pinning(cfg)` sha == artifact pin sha — the §C.1 no-rebind
  rule), and **corpus identity** in the driver-verifiable form: `verify_corpus(ev)` requires
  the sidecar's {pilot, main-tmpl, main-d3, guard} key set to be a BIJECTION with this
  campaign's loaded eval items (byte-identity of the corpora is enforced gate-side via
  `corpus_sha256` + `cmd_gate`'s repo-pin drift check, and driver-side via the landed
  `verify_corpus_pins`; the bijection binds the two records to the SAME item universe —
  DISCLOSED as the composition, since the driver's eval manifest is a different artifact than
  the gate's corpus files and a direct byte compare does not exist driver-side). `pin-fetch`,
  `checkpoint`, `guard`, and `config-affordability` all refuse non-`/2` artifacts.
- **(iii) no pilot stall:** `config-affordability --gate … --tokens … --config run-config.json`
  (D14) is the executable gate→`config.affordability` step (README step 5d), verifying the
  sidecar against the ARTIFACT-recorded sha before writing; idempotent; refuses a conflicting
  existing block. A licensed run reaches pilot with the block already populated.
- **(iv) kappa, genuinely prefill-weighted:** `Add7Model.kappa(s_per_prefill, ev, pass_rows)`
  now weights the model-predicted blend by the REALIZED pilot pass rows read back from the
  pilot rows checkpoint — exactly the traffic the ledger's numerator metered (grid passes over
  the 48-item subset, driver `:3159` + the `:384` arithmetic 9 configs × 4 members × 48, plus
  the full-dev-96 passes `:3224`), robust to REPLACE-support and resume. [MEASURED, mock]:
  2,112 rows / 96 items, weights 4..40 (48-subset items 40 = 36 grid + 4 dev96; others 4) —
  recorded in `projection_rev_b.kappa_weighting`.
- **(v) fixtures that PROVE the seam:** mock sidecar T is deterministically HETEROGENEOUS
  (40 distinct T over 3,302 items [MEASURED]; d3 = T+3; all Tp under the mock max knot); new
  mock probes: TAMPERED sidecar bytes → refused; a SELF-CONSISTENT config pointing at
  non-licensed bytes (declared sha updated to match the tampered file) → refused on the
  artifact-recorded sha; and the §R6 degradation boundary exercised with a planted kappa at
  which the full arm-set BREACHES and REPLACE-defer + d3-defer CLEARS, through the SAME
  module-level `add7_cap_breach` predicate `phase_pilot` uses (lifted from the closure for
  exactly this testability — arithmetic unchanged).

## C4. Finding 1 nit — the derivation digest named truthfully (D14)

`cmd_pinfile` now records `manifest_rows_sha256` (the digest of normalized
`"<file-sha> <basename>"` rows — what it always was) AND `manifest_file_sha256 =
sha256_file(<stats manifest>)`. Oracle case 12's planted-merge assertions are unaffected
(they assert counts, not key names); the derivation sidecar/artifact key is the only change.

## C5. Finding 7 — supersession honesty (this file, REV-C state)

Inline kills applied above: header REV-B→REV-C; §B.3.4 marked superseded-in-part (exports
were never consumed — guard supersedes); §B.3.5 WITHDRAWN (impossible through the pinned
builder; bead `kernel-of-truth-8cpm`; rebind REMOVED); §B.3.6 amended (schedule 240/1056/2304,
guard-invoked, enforced, repriced $1.59); §B.7 rows corrected («implemented» → withdrawn/
deferred with the bead named); §B.9 runbook superseded (incl. its `--outdir /tmp/…` mock line,
which the landed kot-log/1 repo-root containment REFUSES [MEASURED]); §B.10 annotated
(ASM-2516 registers only WITH ASM-2517); §B.12 superseded. Post-REV-C, the operative labels
are: **IMPLEMENTED** (guard + probe + frozen checkpoints + config seams + bundle binding +
shared model + kappa reweight + mock hardening + heartbeat/watchdog + rename), **DEFERRED
with bead** (seq-4 builder re-freeze: per-batch STATS + explicit pin args + per-batch
evidence + any future re-derivation/rebind — `kernel-of-truth-8cpm`), **REMOVED**
(`campaign-pin-rebind.json`; the unconsumed-export construction step; the {200,1024,2304}
schedule).

## C6. Delta artifacts D14–D18 (apply AFTER D13, in order; sha-pinned; bench-verified on the LANDED tree)

| # | Target | Kind | sha256 of the artifact below |
|---|---|---|---|
| D14 | `poc/gcp/f1k_bringup_gate.py` (post-D9) | unified diff | `3f00cfc5ad9c30b365b7d6db9599f46edd3b0be26761b89eee458e4f3a0a3699` |
| D15 | `poc/gcp/f1k_gcp.py` (post-D10) | unified diff | `586a1f0846cc241d108e213f55fc243c9af3a7138a1236b6a87ddc1f1e7159d2` |
| D16 | `poc/gcp/f1k_worker.sh` (post-D11) | unified diff | `bf48d3966a1c4b457004b4293ccc678b7a92818efc184dd44729bba8c1d83bff` |
| D17 | `poc/gcp/README.md` (post-D12) | unified diff | `39dc74d505fcb571e2b065b307f217e583017a5b981b1f0c6dc5c19f01042549` |
| D18 | `poc/glm52-probe/f1k-harness/f1k_driver.py` (post-D13) | unified diff | `93e11dd35bf8dd71b44c3935fc2928544c6fb2490a12d030aa1251f1dd80ee65` |

Bench evidence [MEASURED, /tmp bench this REV-C pass — no repo file touched beyond this memo]:

- **Chains:** D1–D13 re-extracted (all 13 shas match §3/§A4/§B8) and re-applied clean on the
  CURRENT landed bytes, reproducing the §B8 finals (`8824705b`/`cd7a5fbd`/`30e1ca18`/
  `20315815`/`49b2ab3b` — re-verified). D14–D18 then apply clean; a SECOND fresh copy taken
  through the full D1→D18 chain is **byte-identical** to the edited bench on all five files
  (`cmp` ×5). Applied-tree result shas: `f1k_bringup_gate.py f83d30d886cd1396…`,
  `f1k_gcp.py 468ab73d078eaaf5…`, `f1k_worker.sh 53d21424b1d35016…`,
  `README.md 27e915dc080f3736…`, `f1k_driver.py 075bc0b1d701169a…`.
- `py_compile` (gate, gcp, driver) + `bash -n` (worker) clean on the applied tree.
- **$0 oracle 37/37** (`f1k_gcp.py gate --selftest` AND direct `selftest`, on the edited bench
  AND the fresh-chain tree) incl. new cases: 15 extended (schedule 240 + off-schedule n_done
  REFUSED), 16a–d (guard end-to-end on stub engine/builder: probe evidence + all three frozen
  checkpoints + guard-final; tampered pin bytes refused pre-launch; DISABLED probe banner
  refused pre-launch; non-GREEN artifact refused), 17 (config-affordability populated +
  idempotent + tampered-sidecar refusal; config-cost transfers the guard-final figures), 18
  (shared-model identity across BOTH files).
- **Driver $0 --mock green** on the applied tree: exit 0, **25 [PASS]** (23 REV-B checks + 2
  REV-C checks), 0 FAIL, `MOCK VALIDATION PASS`; `projection_rev_b.kappa_weighting` = {2112
  rows, 96 items, weights 4..40} [MEASURED]; heterogeneous-T (40 distinct), tamper +
  self-consistent-bundle refusals, and the R6 boundary all exercised. NOTE (runbook fix): the
  mock `--outdir` MUST live under the repo root — the landed kot-log/1 containment refuses
  `/tmp/...` (`ERR_F1K_RECORD` [MEASURED]); §B9's mock line was wrong. Output ≈ 0.7 GB this
  pass — delete after.
- Probes: `affordability --rate 0.17394 --s-per-prefill 149.1 --replace` → exit 2; without
  `--replace` → exit 3; `plan` → `DRY-PLAN OK` (env-stubbed control-box vars) — all on the
  applied tree.
- Discipline greps (see trigger paragraph): settled-conjunct lines and landed pin-machinery
  hunks byte-stable; no `PINS`/`FROZEN_SHA256` edits anywhere in D14–D18; neither touched
  file is sha-pinned → the landing stays plain infra. `build_carriers.py` is NOT touched.

### C6.1 D14 — `poc/gcp/f1k_bringup_gate.py` REV-C delta (schema /2 + shared model + rename + checkpoint re-freeze + guard + config seams + oracle 37)

<!-- BEGIN-ARTIFACT D14 f1k_bringup_gate.py.rev-c.diff sha256=3f00cfc5ad9c30b365b7d6db9599f46edd3b0be26761b89eee458e4f3a0a3699 -->
```diff
diff --git a/poc/gcp/f1k_bringup_gate.py b/poc/gcp/f1k_bringup_gate.py
index ead8113..f950888 100644
--- a/poc/gcp/f1k_bringup_gate.py
+++ b/poc/gcp/f1k_bringup_gate.py
@@ -47,7 +47,12 @@ import subprocess
 import sys
 from pathlib import Path
 
-SCHEMA = "kot-f1k-bringup-gate/1"
+SCHEMA = "kot-f1k-bringup-gate/2"
+#   [REV-C F5ii] /2 adds REQUIRED model-bundle binding fields to the gate
+#   artifact (model_bundle.add7_src_sha256 + model_bundle.tokens_full_
+#   sha256); every consumer (driver Add7Model, pin-fetch, checkpoint,
+#   construction-guard) requires THIS schema id — a /1 artifact (which
+#   cannot prove its sidecar/model identity) is refused, never coerced.
 
 # ---------------------------------------------------------------------------
 # FROZEN GATE CONSTANTS (fix memo §2; every value tagged there)
@@ -427,9 +432,13 @@ def cmd_pinfile(args):
     Path(args.out).write_text("\n".join(out) + "\n")
     derivation = {
         "n_stats_files": len(prov), "per_file": prov,
-        "manifest_sha256": hashlib.sha256(
+        # [REV-C, rereview finding 1 nit] the rows digest is NAMED as what
+        # it is (a digest of normalized "<file-sha> <basename>" rows), and
+        # the manifest FILE's byte sha is recorded separately.
+        "manifest_rows_sha256": hashlib.sha256(
             "".join("%s %s\n" % (p["sha256"], p["file"])
                     for p in prov).encode()).hexdigest(),
+        "manifest_file_sha256": sha256_file(args.stats_manifest),
         "aggregation": "sum of counts per (layer, expert) over ALL "
                        "per-item T1 stats files [REV-B F1; fail-closed "
                        "on any missing/empty/malformed file]"}
@@ -492,6 +501,11 @@ def cmd_collect(args):
     gate_inputs = {
         "schema": SCHEMA + ":gate-inputs",
         "token_counts": counts,
+        # [REV-C F5ii] the per-item token sidecar is BOUND into the gate
+        # artifact by byte sha — the driver's Add7Model later refuses any
+        # sidecar whose bytes do not hash to the artifact-recorded value
+        # (a self-consistent but non-licensed bundle can no longer pass).
+        "tokens_full_sha256": sha256_file(tokdir / "tokens-full.jsonl"),
         "timing_sample": {k: sample[k] for k in
                           ("seed", "rule", "realized_bin_edges_Tp", "n",
                            "t1_sample_ids", "entries")},
@@ -557,21 +571,34 @@ def _isotonic(knots):
     return pools, repaired
 
 
-def _interp(knots, sfield, t, below):
-    """Piecewise-linear in T over knots; `below` in {'const','extrap'};
-    above max T: FAIL-CLOSED (campaign max-T is sampled by construction)."""
+# ---- KOT-ADD7-SHARED-BEGIN ------------------------------------------------
+# [REV-C F5i, F1K-BRINGUP-GATE-FIX.md SSC] ONE projection-model
+# implementation, byte-identical in poc/gcp/f1k_bringup_gate.py and
+# poc/glm52-probe/f1k-harness/f1k_driver.py. Each copy is verified at
+# runtime: block sha256 == the in-file ADD7_SRC_SHA256 constant AND (at
+# consumption) == the licensed gate artifact's model_bundle.add7_src_sha256
+# — drift in EITHER copy is a refusal, never a silent second
+# implementation. Semantics (frozen, fix memo SS2.6): piecewise-linear in T
+# over isotonic knots; below the min knot central/hi are CONSTANT
+# (cap-conservative) and the lo band extrapolates floored at
+# floor_frac*s(minknot); above the max sampled knot: Add7RangeError
+# (extrapolation above the frozen sample is FORBIDDEN — the campaign max-T
+# text is in the sample by construction).
+class Add7RangeError(ValueError):
+    """T above the max sampled knot — never extrapolated."""
+
+
+def add7_interp(knots, sfield, t, below="const", floor_frac=0.35):
     ts = [k["T"] for k in knots]
     ss = [k[sfield] for k in knots]
     if t > ts[-1] + 1e-9:
-        die("F1K_GATE_MODEL", "T=%.0f above max sampled knot %.0f — "
-            "extrapolation above the sample is FORBIDDEN (the campaign "
-            "max-T prefill must be in the sample)" % (t, ts[-1]))
+        raise Add7RangeError(
+            "T=%.0f above max sampled knot %.0f" % (t, ts[-1]))
     if t <= ts[0]:
         if below == "const" or len(ts) < 2:
             return ss[0]
         slope = (ss[1] - ss[0]) / max(1e-9, ts[1] - ts[0])
-        return max(FLOOR_EXTRAP_MIN_FRAC * ss[0],
-                   ss[0] - slope * (ts[0] - t))
+        return max(floor_frac * ss[0], ss[0] - slope * (ts[0] - t))
     for i in range(len(ts) - 1):
         if t <= ts[i + 1]:
             frac = (t - ts[i]) / max(1e-9, ts[i + 1] - ts[i])
@@ -579,6 +606,41 @@ def _interp(knots, sfield, t, below):
     return ss[-1]
 
 
+def add7_block_sha256(path):
+    """sha256 over the exact lines BETWEEN the shared-block markers
+    (marker lines excluded); None when the markers are absent/ambiguous."""
+    lines = open(path, encoding="utf-8").read().split("\n")
+    beg = [i for i, l in enumerate(lines)
+           if l.startswith("# ---- KOT-ADD7-SHARED-BEGIN")]
+    end = [i for i, l in enumerate(lines)
+           if l.startswith("# ---- KOT-ADD7-SHARED-END")]
+    if len(beg) != 1 or len(end) != 1 or end[0] <= beg[0]:
+        return None
+    body = "\n".join(lines[beg[0] + 1:end[0]])
+    return hashlib.sha256(body.encode("utf-8")).hexdigest()
+# ---- KOT-ADD7-SHARED-END --------------------------------------------------
+
+
+ADD7_SRC_SHA256 = "9d3e1bc76f8506d99a29b0465af2c063b32ba8d726e7ec2c6a65e3c596260353"
+#   [REV-C F5i] frozen sha256 of the KOT-ADD7-SHARED block body (both
+#   copies must hash to THIS value; project() refuses to emit an artifact
+#   from a drifted copy, and the driver refuses to consume one).
+
+
+def _interp(knots, sfield, t, below):
+    """Thin gate-side wrapper over the SHARED add7_interp (ONE model
+    implementation, KOT-ADD7-SHARED block [REV-C F5i]) — converts the
+    above-max-knot Add7RangeError into the gate's fail-closed die()."""
+    try:
+        return add7_interp(knots, sfield, t, below,
+                           floor_frac=FLOOR_EXTRAP_MIN_FRAC)
+    except Add7RangeError:
+        die("F1K_GATE_MODEL", "T=%.0f above max sampled knot %.0f — "
+            "extrapolation above the sample is FORBIDDEN (the campaign "
+            "max-T prefill must be in the sample)"
+            % (t, max(k["T"] for k in knots)))
+
+
 def build_knots(inputs):
     ent = {e["sample_id"]: e for e in inputs["timing_sample"]["entries"]}
     strata = {}
@@ -673,6 +735,19 @@ def project(inputs, frozen, replace=False, out_path=None):
     if tc["tokenizer"]["mode"] != "REAL" and not inputs.get("_allow_mock"):
         die("F1K_GATE_MOCK", "token counts are MOCK — a mock gate never "
             "licenses spend (selftest/dry-run only)")
+    # [REV-C F5i] the emitting copy of the shared model must BE the frozen
+    # model — a drifted block never emits a license artifact.
+    own_add7 = add7_block_sha256(__file__)
+    if own_add7 != ADD7_SRC_SHA256:
+        die("F1K_GATE_MODEL", "this file's KOT-ADD7-SHARED block hashes to "
+            "%r != the frozen ADD7_SRC_SHA256 %s — the shared projection "
+            "model drifted; refuse to emit an artifact"
+            % (own_add7, ADD7_SRC_SHA256[:16]))
+    # [REV-C F5ii] the artifact must BIND its per-item token sidecar.
+    if not inputs.get("tokens_full_sha256"):
+        die("F1K_GATE_MODEL", "gate-inputs carry no tokens_full_sha256 — "
+            "a /2 artifact binds its token sidecar by byte sha "
+            "(re-run the REV-C collect); fail closed")
     raw_knots, knots, repaired = build_knots(inputs)
     rate = inputs["rate_usd_per_hour"]
     reserve_h = RESERVE_USD / rate
@@ -818,6 +893,20 @@ def project(inputs, frozen, replace=False, out_path=None):
             "cont_tokens_addend": CONT_TOKENS,
         },
         "pin": inputs["pin"],
+        # [REV-C F5ii] model-bundle binding: EVERYTHING the driver's
+        # Add7Model consumes is bound here by sha — the shared model
+        # source AND the per-item token sidecar. The driver verifies its
+        # own block + the sidecar bytes against THESE recorded values
+        # (plus corpus/pin/rate identity from the sibling fields).
+        "model_bundle": {
+            "add7_src_sha256": ADD7_SRC_SHA256,
+            "tokens_full_sha256": inputs["tokens_full_sha256"],
+            "rule": "consumption REQUIRES: schema == %s, verdict GREEN, "
+                    "driver shared-block sha == add7_src_sha256, sidecar "
+                    "bytes sha == tokens_full_sha256, corpus shas == "
+                    "corpus_sha256 (driver-side files), config pin sha == "
+                    "pin.pin_file_sha256, config rate == "
+                    "rate.usd_per_hour [REV-C F5ii]" % SCHEMA},
         "pin_engagement": {
             "pass": eng_ok, "problems": eng_problems,
             "rule": "per-T2-run armed-banner evidence parsed with the "
@@ -864,27 +953,43 @@ def project(inputs, frozen, replace=False, out_path=None):
 # ---------------------------------------------------------------------------
 # checkpoint: construction EARLY-ABORT re-projection ([REV-B F3, ASM-2516])
 # ---------------------------------------------------------------------------
-CHECKPOINT_SCHEDULE = (200, 1024, 2304)   # [STIPULATED] n_done milestones
+CHECKPOINT_SCHEDULE = (240, 1056, 2304)
+#   [REV-C F3; amends ASM-2516 item (4)'s {200,1024,2304} PRE-REGISTRATION
+#   — ASM-2517] n_done milestones ALIGNED TO THE OBSERVABLE GRANULARITY:
+#   the SHA-PINNED builder (build_carriers.py, frozen-record generator
+#   pin) runs ONE 48-pass engine batch per concept and checkpoints per
+#   concept (concept-%03d.json), so construction progress is mechanically
+#   observable ONLY at 48-pass boundaries. 240/1056/2304 = 5/22/48 of the
+#   96 concepts. First exposure 240 x ~137.2 s ~ 9.1 h ~ $1.59 at the
+#   f=1.45 row [EXTRAPOLATED].
 CHECKPOINT_RATIO_MAX = 10.0               # sanity bound on realized/predicted
 
 
-def cmd_checkpoint(args):
-    """[REV-B F3] Construction EARLY-ABORT checkpoint. HONESTY (gate-fix
-    review #4): the gate's +-1SE band bounds SAMPLING error of the chosen
-    30-text sample ONLY — NOT selection bias, NOT unseen-tail behaviour; a
-    pin can pass the 30-item gate yet underperform over the 4,608
-    construction items. This checkpoint bounds that residual mechanically:
-    at n_done in CHECKPOINT_SCHEDULE (200/1024/2304 [STIPULATED]; first
-    exposure ~200 x ~137 s ~ 7.6 h ~ $1.3), re-project the WHOLE campaign
-    with the LICENSED gate model re-levelled by the realized construction
-    ratio (elapsed seconds / model-predicted seconds for the first n_done
-    manifest-order construction items) and STOP (exit 2) if a
-    reserve-inclusive cap breaches at central OR +1SE. LEDGER BINDING: the
-    artifact's realized construction hours/usd ARE the cost basis the
-    LANDED driver machinery consumes fail-closed (Ledger REQUIRES
-    cost.usd_spent_prior + construction_instance_hours — never silent
-    zeros; ASM-2513 landed) — a breach here never reaches a pilot spawn."""
-    gate = json.loads(Path(args.gate).read_text(encoding="utf-8"))
+def checkpoint_eval(gate, tokens_path, n_done, elapsed, n_start=0,
+                    out=None):
+    """[REV-B F3 / REV-C] Construction EARLY-ABORT checkpoint. HONESTY
+    (gate-fix review #4): the gate's +-1SE band bounds SAMPLING error of
+    the chosen 30-text sample ONLY — NOT selection bias, NOT unseen-tail
+    behaviour; a pin can pass the 30-item gate yet underperform over the
+    4,608 construction items. This checkpoint bounds that residual
+    mechanically: at n_done in CHECKPOINT_SCHEDULE (a FROZEN schedule —
+    any other n_done is REFUSED, never a movable goalpost [REV-C,
+    rereview #3]), re-project the WHOLE campaign with the LICENSED gate
+    model re-levelled by the realized construction ratio (elapsed seconds
+    / model-predicted seconds for manifest-order construction items
+    n_start..n_done) and STOP (exit 2) if a reserve-inclusive cap
+    breaches at central OR +1SE. n_start (REV-C, 48-multiple) supports a
+    RESUMED construction: cached concepts contribute no elapsed time, so
+    both the elapsed and the prediction cover exactly this session's
+    span. INVOKED BY the REV-C construction-guard in-process (the SAME
+    code as the CLI). LEDGER BINDING: the artifact's realized figures ARE
+    the cost basis `config-cost` transfers into the campaign config —
+    the LANDED Ledger's REQUIRED fail-closed inputs (ASM-2513) — and a
+    breach here never reaches a pilot spawn."""
+    if gate.get("schema") != SCHEMA:
+        die("F1K_GATE_CKPT", "gate artifact schema %r != %s — checkpoints "
+            "consume only a /2 model-bundle-bound artifact [REV-C]"
+            % (gate.get("schema"), SCHEMA))
     if gate.get("verdict") != "GREEN":
         die("F1K_GATE_CKPT", "gate artifact verdict %r — checkpoints only "
             "run inside a GREEN license" % gate.get("verdict"))
@@ -893,17 +998,23 @@ def cmd_checkpoint(args):
     rate = gate["rate"]["usd_per_hour"]
     thr = gate["thresholds"]
     reserve_h = RESERVE_USD / rate
-    entries = [json.loads(l) for l in open(args.tokens, encoding="utf-8")]
+    entries = [json.loads(l) for l in open(tokens_path, encoding="utf-8")]
     cons = [e for e in entries if e["pop"] == "construction"]
-    n_done = int(args.n_done)
+    if n_done not in CHECKPOINT_SCHEDULE:
+        die("F1K_GATE_CKPT", "n_done %d is NOT on the frozen checkpoint "
+            "schedule %s — the schedule is part of the freeze (ASM-2517); "
+            "an arbitrary n_done is refused, never accepted"
+            % (n_done, list(CHECKPOINT_SCHEDULE)))
     if not 1 <= n_done <= len(cons):
         die("F1K_GATE_CKPT", "n_done %d outside [1, %d]"
             % (n_done, len(cons)))
-    elapsed = float(args.elapsed_s)
+    if not (0 <= n_start < n_done and n_start % 48 == 0):
+        die("F1K_GATE_CKPT", "n_start %d invalid: must be a 48-multiple "
+            "(concept boundary) in [0, n_done)" % n_start)
     if elapsed <= 0:
         die("F1K_GATE_CKPT", "elapsed_s must be > 0")
     pred = sum(_interp(knots, "s", e["T"] + cont, "const")
-               for e in cons[:n_done])
+               for e in cons[n_start:n_done])
     ratio = elapsed / pred
     if not 0.0 < ratio <= CHECKPOINT_RATIO_MAX:
         die("F1K_GATE_CKPT", "realized/predicted ratio %.3f outside "
@@ -925,7 +1036,7 @@ def cmd_checkpoint(args):
         (usd_hi + RESERVE_USD > hi_u, "+1SE $%.2f + reserve" % usd_hi),
     ) if cond]
     art = {"schema": SCHEMA + ":construction-checkpoint",
-           "n_done": n_done, "elapsed_s": elapsed,
+           "n_done": n_done, "n_start": n_start, "elapsed_s": elapsed,
            "predicted_s_first_n": round(pred, 1),
            "realized_over_predicted": round(ratio, 4),
            "reprojection": {
@@ -947,8 +1058,8 @@ def cmd_checkpoint(args):
            "verdict": "STOP" if breach else "CONTINUE",
            "breaches": breach,
            "schedule": list(CHECKPOINT_SCHEDULE)}
-    if args.out:
-        Path(args.out).write_text(json.dumps(art, indent=2))
+    if out:
+        Path(out).write_text(json.dumps(art, indent=2))
     print(json.dumps(art, indent=2))
     if breach:
         die("F1K_GATE_CKPT", "EARLY-ABORT: reserve-inclusive re-projection "
@@ -959,6 +1070,335 @@ def cmd_checkpoint(args):
     return 0
 
 
+def cmd_checkpoint(args):
+    """CLI wrapper; the mechanics live in checkpoint_eval() so the REV-C
+    construction-guard invokes EXACTLY the same code in-process."""
+    gate = json.loads(Path(args.gate).read_text(encoding="utf-8"))
+    return checkpoint_eval(gate, args.tokens, int(args.n_done),
+                           float(args.elapsed_s),
+                           n_start=int(args.n_start or 0),
+                           out=args.out or None)
+
+
+# ---------------------------------------------------------------------------
+# construction-guard: WRAPPER-LEVEL shape-(i) enforcement [REV-C F3]
+# ---------------------------------------------------------------------------
+# The REV-C fork decision (rereview finding 3): build_carriers.py is
+# SHA-PINNED (frozen-record generator pin) and inherits AMBIENT env into
+# every engine batch (build_carriers.py:634 `env = dict(os.environ)`, only
+# KAE_SCORE popped) — so the licensed pin is enforced at the WRAPPER, the
+# builder stays byte-untouched (no seq-4 re-freeze on the critical path):
+#   1. the guard BINDS the pin explicitly (gate artifact GREEN + schema /2
+#      + byte-sha match), never trusting ambient PIN/PIN_GB;
+#   2. it PROVES engagement BEFORE any construction spend with a DUMP-MODE
+#      probe: one minimal KAE_DUMP invocation of the SAME engine argv under
+#      the SAME env, whose stderr must carry a coherent armed banner under
+#      the LANDED driver grammar (ASM-2513) — mode-exact evidence (the
+#      banner wording stays fetch-grade ASM-1971: a divergence is aligned
+#      in the driver regex once, both consumers follow);
+#   3. it launches the builder with EXACTLY that verified env (STATS and
+#      the mode knobs popped) — the builder's own env passthrough
+#      (:634, verified from the pinned bytes) carries PIN/PIN_GB into all
+#      96 engine batches unchanged;
+#   4. it runs the FROZEN early-abort checkpoints in-process off the
+#      builder's per-concept checkpoint files (the only mechanical
+#      progress signal the pinned builder emits), killing the process
+#      group on a reserve-inclusive breach (exit 2).
+# HONEST RESIDUAL [REV-C]: the builder swallows per-batch engine stderr on
+# success, so there is NO per-batch banner evidence — engagement is proved
+# at launch (probe) and inherited by argument (byte-verified passthrough),
+# not re-observed per batch. Per-batch evidence + per-batch STATS need a
+# builder edit = the deferred seq-4 re-freeze (bead kot-*, SSC.3), which is
+# NOT on this landing's critical path.
+def _verify_gate_for_construction(art, pin_path):
+    """Fail-closed licence check shared by guard + config seams. Returns
+    (pin_sha, pin_gb) from the artifact after byte-verifying pin_path."""
+    if art.get("schema") != SCHEMA:
+        die("F1K_GUARD", "gate artifact schema %r != %s — construction "
+            "binds only to a /2 model-bundle-bound artifact"
+            % (art.get("schema"), SCHEMA))
+    if art.get("verdict") != "GREEN":
+        die("F1K_GUARD", "gate artifact verdict %r — GREEN is the ONLY "
+            "construction license" % art.get("verdict"))
+    pin = art.get("pin") or {}
+    if pin.get("regime") != "pinned-bringup" \
+            or not pin.get("pin_file_sha256") or not pin.get("pin_gb"):
+        die("F1K_GUARD", "gate artifact pin block incomplete/unpinned "
+            "(%r) — shape (i) requires a bound sha + PIN_GB" % (pin,))
+    got = sha256_file(pin_path)
+    if got != pin["pin_file_sha256"]:
+        die("F1K_GUARD", "pin file %s sha %s != licensed %s — the "
+            "construction pin is bound BY BYTES, never by path"
+            % (pin_path, got[:16], pin["pin_file_sha256"][:16]))
+    mb = art.get("model_bundle") or {}
+    own = add7_block_sha256(__file__)
+    if own != ADD7_SRC_SHA256 or mb.get("add7_src_sha256") != own:
+        die("F1K_GUARD", "shared-model sha mismatch (own %r, frozen %s, "
+            "artifact %r) — a drifted model copy neither guards nor "
+            "projects" % (own and own[:16], ADD7_SRC_SHA256[:16],
+                          (mb.get("add7_src_sha256") or "")[:16]))
+    return pin["pin_file_sha256"], float(pin["pin_gb"])
+
+
+def _probe_engagement(engine_cmd, env, layers, rundir):
+    """[REV-C F3.2] DUMP-MODE pin-engagement probe, run BEFORE the first
+    construction pass: one minimal KAE_DUMP invocation (4 in-vocab ids,
+    slot-0 spans — the exact manifest grammar run_dump writes) under the
+    EXACT env the builder will inherit. The stderr must carry a coherent
+    armed banner under the LANDED driver grammar; any disabled marker,
+    incoherent counter, wrong source path, wrong budget, or nonzero exit
+    REFUSES construction — exposure is ONE engine start (~minutes,
+    <~$0.01 at the construction rate), never a 4,608-pass campaign."""
+    armed_re, disabled_markers = _driver_pin_grammar()
+    rundir = Path(rundir)
+    rundir.mkdir(parents=True, exist_ok=True)
+    man = rundir / "pin-probe.dump-manifest.txt"
+    man.write_text("4 15 15 15 15 0 0 0 0\n")
+    penv = dict(env)
+    penv["KAE_DUMP"] = str(man)
+    penv["KAE_DUMP_OUT"] = str(rundir / "pin-probe.kaed")
+    penv["KAE_DUMP_LAYERS"] = layers
+    penv["KAE_SEED"] = "1"    # probe-only; output discarded, echo unused
+    proc = subprocess.run(engine_cmd, env=penv, stdout=subprocess.PIPE,
+                          stderr=subprocess.PIPE, check=False)
+    err = proc.stderr.decode("utf-8", "replace")
+    problems = []
+    if proc.returncode != 0:
+        problems.append("probe engine exit %d" % proc.returncode)
+    bad = [m for m in disabled_markers if m in err]
+    if bad:
+        problems.append("pinning DISABLED marker %s" % bad)
+    m = armed_re.search(err)
+    banner = m.group(0) if m else None
+    if not m:
+        problems.append("no armed banner on probe stderr")
+    else:
+        n_pinned, gb_used = int(m.group(1)), float(m.group(2))
+        gb_budget, src = float(m.group(3)), m.group(4)
+        want_gb = float(env["PIN_GB"])
+        if n_pinned < 1 or not gb_used > 0.0:
+            problems.append("incoherent counters (n=%d, %.3f GiB)"
+                            % (n_pinned, gb_used))
+        if abs(gb_budget - want_gb) > 0.01 * max(1.0, want_gb) \
+                or gb_used > gb_budget * 1.01:
+            problems.append("budget %.3f/used %.3f vs bound PIN_GB=%s"
+                            % (gb_budget, gb_used, env["PIN_GB"]))
+        if src != env["PIN"]:
+            problems.append("armed from %r != bound pin %r"
+                            % (src, env["PIN"]))
+    evidence = {"schema": SCHEMA + ":construction-pin-probe",
+                "engine_argv": list(engine_cmd),
+                "pin": env["PIN"], "pin_gb": env["PIN_GB"],
+                "mode": "KAE_DUMP (construction mode — mode-exact)",
+                "banner": banner, "problems": problems,
+                "stderr_tail": err[-2000:],
+                "rule": "landed ASM-2513 grammar (PIN_ARMED_RE + disabled "
+                        "markers), coherence as check_pin_engagement; "
+                        "wording fetch-grade ASM-1971"}
+    (rundir / "construction-pin-probe.json").write_text(
+        json.dumps(evidence, indent=2))
+    if problems:
+        die("F1K_GUARD", "pin-engagement PROBE REFUSED construction "
+            "(%s) — evidence at %s; fix the pin/engine seam, never "
+            "launch unverified" % ("; ".join(problems),
+                                   rundir / "construction-pin-probe.json"))
+    return evidence
+
+
+def cmd_guard(args):
+    """[REV-C F3] construction-guard: verify license -> bind pin env
+    explicitly -> PROBE engagement -> launch the UNTOUCHED sha-pinned
+    builder with the verified env -> run the FROZEN checkpoints
+    in-process off the builder's per-concept files -> kill on breach.
+    usage: ... guard --gate bringup-gate.json --pin campaign-pin.stats
+      --engine-cmd '<json argv>' --layers 3,...,77 --tokens
+      tokens-full.jsonl --rundir <dir> --workdir <builder workdir>
+      [--poll-seconds N] -- <builder argv...>"""
+    import signal
+    import time
+    art = json.loads(Path(args.gate).read_text(encoding="utf-8"))
+    pin_path = Path(args.pin).resolve()
+    pin_sha, pin_gb = _verify_gate_for_construction(art, pin_path)
+    args.builder = list(args.builder or [])
+    if args.builder[:1] == ["--"]:
+        args.builder = args.builder[1:]
+    if not args.builder:
+        die("F1K_GUARD", "no builder argv after '--'")
+    env = dict(os.environ)
+    overridden = {k: env[k] for k in ("PIN", "PIN_GB", "STATS")
+                  if k in env}
+    for k in ("STATS", "SCORE", "KAE_SCORE", "KAE_DUMP", "KAE_DUMP_OUT",
+              "KAE_DUMP_LAYERS"):
+        env.pop(k, None)
+    #   STATS is POPPED deliberately [REV-C]: with 96 batches sharing one
+    #   ambient STATS path (truncate-vs-append fetch-grade ASM-1971) a
+    #   single file would hold the LAST batch only — the F1 defect class.
+    #   Full-corpus stats need the deferred seq-4 builder re-freeze.
+    env["PIN"] = str(pin_path)
+    env["PIN_GB"] = ("%g" % pin_gb)
+    rundir = Path(args.rundir)
+    rundir.mkdir(parents=True, exist_ok=True)
+    probe = _probe_engagement(json.loads(args.engine_cmd), env,
+                              args.layers, rundir)
+    workdir = Path(args.workdir)
+
+    def concepts_done():
+        return len(list(workdir.glob("concept-*.json")))
+
+    n0 = concepts_done() * 48
+    pending = [p for p in CHECKPOINT_SCHEDULE if p > n0]
+    if not pending:
+        print("guard: resume past the last frozen checkpoint (n0=%d) — "
+              "no checkpoints remain; earlier sessions ran them" % n0)
+    proc = subprocess.Popen(args.builder, env=env, start_new_session=True)
+    t0 = time.monotonic()
+
+    def run_ckpt(p):
+        try:
+            return checkpoint_eval(
+                art, args.tokens, p, time.monotonic() - t0, n_start=n0,
+                out=str(rundir / ("construction-checkpoint-%d.json" % p)))
+        except SystemExit:
+            if proc.poll() is None:
+                try:
+                    os.killpg(proc.pid, signal.SIGTERM)
+                    for _ in range(30):
+                        if proc.poll() is not None:
+                            break
+                        time.sleep(1)
+                    if proc.poll() is None:
+                        os.killpg(proc.pid, signal.SIGKILL)
+                except ProcessLookupError:
+                    pass
+            (rundir / "construction-abort.json").write_text(json.dumps(
+                {"schema": SCHEMA + ":construction-abort",
+                 "at_checkpoint": p, "n_start": n0,
+                 "elapsed_s": round(time.monotonic() - t0, 1)}, indent=2))
+            raise
+
+    ran = []
+    while proc.poll() is None:
+        time.sleep(float(args.poll_seconds))
+        avail = concepts_done() * 48
+        while pending and pending[0] <= avail:
+            p = pending.pop(0)
+            run_ckpt(p)
+            ran.append(p)
+    rc = proc.returncode
+    final_avail = concepts_done() * 48
+    while pending and pending[0] <= final_avail:
+        p = pending.pop(0)
+        run_ckpt(p)     # a post-hoc breach still STOPs before pilot
+        ran.append(p)
+    elapsed = time.monotonic() - t0
+    rate = art["rate"]["usd_per_hour"]
+    final = {"schema": SCHEMA + ":construction-guard-final",
+             "builder_exit": rc, "pin_file_sha256": pin_sha,
+             "pin_gb": pin_gb, "ambient_overridden": overridden,
+             "probe": "construction-pin-probe.json",
+             "checkpoints_run": ran, "n_start_passes": n0,
+             "n_final_passes": final_avail,
+             "elapsed_s": round(elapsed, 1),
+             "realized": {"instance_hours": round(elapsed / 3600.0, 4),
+                          "usd": round(elapsed / 3600.0 * rate, 4),
+                          "rate_usd_per_hour": rate},
+             "rule": "this session's realized figures; `config-cost` "
+                     "sums guard-final files into the campaign config's "
+                     "REQUIRED cost basis (landed Ledger, ASM-2513)"}
+    (rundir / "construction-guard-final.json").write_text(
+        json.dumps(final, indent=2))
+    print(json.dumps(final, indent=2))
+    return rc
+
+
+# ---------------------------------------------------------------------------
+# gate -> campaign-config executable seams [REV-C F5iii + F3 checkpoints]
+# ---------------------------------------------------------------------------
+def _merge_config_block(cfg_path, key, block):
+    cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
+    if key in cfg and cfg[key] != block:
+        die("F1K_CONFIG", "config.%s already present and DIFFERENT — a "
+            "licensed binding is never silently overwritten; resolve "
+            "deliberately (existing: %s)"
+            % (key, json.dumps(cfg[key], indent=2)[:800]))
+    cfg[key] = block
+    tmp = Path(str(cfg_path) + ".tmp")
+    tmp.write_text(json.dumps(cfg, indent=2))
+    os.replace(tmp, cfg_path)
+    print(json.dumps({key: block}, indent=2))
+
+
+def cmd_config_afford(args):
+    """[REV-C F5iii] populate config.affordability FROM the licensed gate
+    artifact — the executable step the rereview found missing (a licensed
+    run could otherwise reach pilot and STALL on an absent block). Every
+    value is verified against the ARTIFACT-recorded bundle, then written;
+    the driver re-verifies at consumption (defense in depth)."""
+    art_path = Path(args.gate)
+    art = json.loads(art_path.read_text(encoding="utf-8"))
+    if art.get("schema") != SCHEMA:
+        die("F1K_CONFIG", "gate artifact schema %r != %s"
+            % (art.get("schema"), SCHEMA))
+    if art.get("verdict") != "GREEN":
+        die("F1K_CONFIG", "gate artifact verdict %r — only GREEN feeds a "
+            "campaign config" % art.get("verdict"))
+    if (art.get("tokenizer") or {}).get("mode") != "REAL" \
+            and not args.allow_mock:
+        die("F1K_CONFIG", "gate artifact tokenizer mode is not REAL — a "
+            "mock bundle enters a config only under --allow-mock (and "
+            "never licenses in the driver)")
+    mb = art.get("model_bundle") or {}
+    if not mb.get("tokens_full_sha256") or not mb.get("add7_src_sha256"):
+        die("F1K_CONFIG", "gate artifact model_bundle incomplete (%r)"
+            % (mb,))
+    tok_sha = sha256_file(args.tokens)
+    if tok_sha != mb["tokens_full_sha256"]:
+        die("F1K_CONFIG", "tokens sidecar %s sha %s != the ARTIFACT-"
+            "recorded %s — the bundle binds bytes, not paths"
+            % (args.tokens, tok_sha[:16],
+               mb["tokens_full_sha256"][:16]))
+    own = add7_block_sha256(__file__)
+    if own != ADD7_SRC_SHA256 or mb["add7_src_sha256"] != own:
+        die("F1K_CONFIG", "shared-model sha mismatch (own %r vs frozen/"
+            "artifact) — refuse to bind a drifted model"
+            % (own and own[:16]))
+    block = {"tokens_full_path": str(Path(args.tokens).resolve()),
+             "tokens_full_sha256": tok_sha,
+             "gate_artifact_path": str(art_path.resolve()),
+             "gate_artifact_sha256": sha256_file(art_path)}
+    if args.allow_mock:
+        block["_allow_mock"] = True
+    _merge_config_block(args.config, "affordability", block)
+    return 0
+
+
+def cmd_config_cost(args):
+    """[REV-C F3] transfer the guard's realized construction figures into
+    the campaign config's REQUIRED cost basis (the landed Ledger fails
+    closed without cost.{usd_spent_prior, construction_instance_hours} —
+    ASM-2513). --final may repeat for resumed constructions (sessions
+    sum); --prior-usd is the metered PRE-construction spend."""
+    hours = usd = 0.0
+    for fp in args.final:
+        fin = json.loads(Path(fp).read_text(encoding="utf-8"))
+        if fin.get("schema") != SCHEMA + ":construction-guard-final":
+            die("F1K_CONFIG", "%s is not a construction-guard-final "
+                "artifact" % fp)
+        if fin.get("builder_exit") != 0:
+            die("F1K_CONFIG", "%s records builder_exit=%r — a FAILED "
+                "construction session never becomes a cost basis; "
+                "resume it (its successor final subsumes the elapsed "
+                "time it re-does, and its wasted spend goes into "
+                "--prior-usd deliberately)" % (fp, fin.get("builder_exit")))
+        hours += float(fin["realized"]["instance_hours"])
+        usd += float(fin["realized"]["usd"])
+    block = {"spot_rate_usd_per_hour": float(args.rate),
+             "usd_spent_prior": round(float(args.prior_usd) + usd, 4),
+             "construction_instance_hours": round(hours, 4)}
+    _merge_config_block(args.config, "cost", block)
+    return 0
+
+
 # ---------------------------------------------------------------------------
 # spec ($0 control-box witness) + selftest ($0 oracle)
 # ---------------------------------------------------------------------------
@@ -1047,7 +1487,7 @@ def selftest():
         cd = td / "corpus"
         cd.mkdir()
         _mock_corpora(cd)
-        print("== selftest: kot-f1k-bringup-gate/1 $0 oracle (MOCK tokens) ==")
+        print("== selftest: kot-f1k-bringup-gate/2 $0 oracle (MOCK tokens) ==")
         ns = argparse.Namespace(corpus_dir=str(cd), mock_f=1.45,
                                 tok_wrapper=None, tokenizer=None,
                                 out=str(td / "tok"))
@@ -1080,6 +1520,8 @@ def selftest():
             inv_t = [[e["pop"], e["m"], e["T"] + CONT_TOKENS] for e in ent]
             return {"schema": SCHEMA + ":gate-inputs",
                     "token_counts": counts, "_allow_mock": True,
+                    "tokens_full_sha256":
+                        sha256_file(td / "tok/tokens-full.jsonl"),
                     "timing_sample": sample,
                     "t2_pinned_runs": [json.loads(l) for l in open(t2path)],
                     "t1_unpinned_runs": [], "inventory_t": inv_t,
@@ -1331,12 +1773,14 @@ def selftest():
               and any("REFUSED" in r for r in art14["reasons"]),
               "case 14 STOP: regime 'unpinned' never licenses (shape (ii) "
               "rejected)")
-        # case 15 [REV-B F3]: construction early-abort checkpoint —
-        # ratio 1.0 CONTINUEs; a realized slowdown that breaches the
-        # reserve-inclusive cap STOPs (exit 2).
+        # case 15 [REV-B F3 / REV-C]: construction early-abort checkpoint
+        # at the CONCEPT-ALIGNED frozen schedule (240/1056/2304) — ratio
+        # 1.0 CONTINUEs; a realized slowdown that breaches the
+        # reserve-inclusive cap STOPs (exit 2); an OFF-SCHEDULE n_done is
+        # REFUSED (the schedule is frozen, never a movable goalpost).
         art["thresholds"] = frozen
         (td / "gate-art.json").write_text(json.dumps(art))
-        cons15 = [e for e in ent if e["pop"] == "construction"][:200]
+        cons15 = [e for e in ent if e["pop"] == "construction"][:240]
         knots15 = sorted(art["model"]["knots_isotonic"],
                          key=lambda k: k["T"])
         pred15 = sum(_interp(knots15, "s", e["T"] + CONT_TOKENS, "const")
@@ -1344,32 +1788,183 @@ def selftest():
         rc15 = cmd_checkpoint(argparse.Namespace(
             gate=str(td / "gate-art.json"),
             tokens=str(td / "tok" / "tokens-full.jsonl"),
-            n_done=200, elapsed_s=str(pred15 * 1.0), out=""))
+            n_done=240, elapsed_s=str(pred15 * 1.0), n_start="0", out=""))
         check(rc15 == 0, "case 15 checkpoint CONTINUE at ratio 1.0 "
                          "(700 h central holds)")
         try:
             cmd_checkpoint(argparse.Namespace(
                 gate=str(td / "gate-art.json"),
                 tokens=str(td / "tok" / "tokens-full.jsonl"),
-                n_done=200, elapsed_s=str(pred15 * 1.35), out=""))
+                n_done=240, elapsed_s=str(pred15 * 1.35), n_start="0",
+                out=""))
             check(False, "case 15 must STOP at ratio 1.35")
         except SystemExit:
             check(True, "case 15 EARLY-ABORT STOP: ratio 1.35 re-projects "
                         "past the reserve-inclusive cap (exit 2) after "
-                        "~$1.3 exposure, not after 4,608 passes")
+                        "~$1.6 exposure, not after 4,608 passes")
+        try:
+            cmd_checkpoint(argparse.Namespace(
+                gate=str(td / "gate-art.json"),
+                tokens=str(td / "tok" / "tokens-full.jsonl"),
+                n_done=200, elapsed_s=str(pred15), n_start="0", out=""))
+            check(False, "case 15 must refuse off-schedule n_done")
+        except SystemExit:
+            check(True, "case 15 SCHEDULE ENFORCED: n_done=200 (off the "
+                        "frozen 240/1056/2304) refused [REV-C]")
+        # case 16 [REV-C F3]: construction-guard end-to-end on stubs —
+        # (a) verified pin + armed-banner probe + frozen checkpoints off
+        # per-concept files -> exit 0 with full evidence chain;
+        # (b) tampered pin bytes refuse BEFORE launch; (c) a DISABLED
+        # probe banner refuses BEFORE launch; (d) a non-GREEN artifact
+        # refuses. ($0: stub engine/builder — the real seam is VM-only.)
+        pin16 = td / "pin16.stats"
+        pin16.write_text("3 0 17\n3 1 6\n")
+        art16 = json.loads((td / "gate-art.json").read_text())
+        art16["pin"]["pin_file_sha256"] = sha256_file(pin16)
+        art16["pin"]["pin_gb"] = 40.0
+        (td / "gate-art16.json").write_text(json.dumps(art16))
+        eng16 = td / "stub-engine.py"
+        eng16.write_text(
+            "import os, sys\n"
+            "if os.environ.get('STUB_DISABLE'):\n"
+            "    sys.stderr.write('pinning DISABLED\\n'); sys.exit(0)\n"
+            "sys.stderr.write('[PIN] hot-expert store armed: pinned 96 "
+            "experts, 1.780 GiB (budget %s.000 GiB) from %s\\n'\n"
+            "    % (os.environ.get('PIN_GB'), os.environ.get('PIN')))\n")
+        bld16 = td / "stub-builder.py"
+        bld16.write_text(
+            "import os, sys, time\n"
+            "wd = sys.argv[1]\n"
+            "for c in range(96):\n"
+            "    open(os.path.join(wd, 'concept-%03d.json' % c), 'w')"
+            ".write('{}')\n"
+            "    time.sleep(0.001)\n"
+            "time.sleep(0.2)\n")
+        wd16 = td / "wd16"
+        wd16.mkdir()
+        rd16 = td / "rd16"
+        ns16 = argparse.Namespace(
+            gate=str(td / "gate-art16.json"), pin=str(pin16),
+            engine_cmd=json.dumps([sys.executable, str(eng16)]),
+            layers="3,5", tokens=str(td / "tok" / "tokens-full.jsonl"),
+            rundir=str(rd16), workdir=str(wd16), poll_seconds="0.05",
+            builder=["--", sys.executable, str(bld16), str(wd16)])
+        rc16 = cmd_guard(ns16)
+        fin16 = json.loads(
+            (rd16 / "construction-guard-final.json").read_text())
+        check(rc16 == 0
+              and (rd16 / "construction-pin-probe.json").is_file()
+              and all((rd16 / ("construction-checkpoint-%d.json" % p))
+                      .is_file() for p in (240, 1056, 2304))
+              and fin16["builder_exit"] == 0
+              and fin16["checkpoints_run"] == [240, 1056, 2304]
+              and fin16["pin_file_sha256"] == sha256_file(pin16),
+              "case 16a GUARD end-to-end: probe evidence + all frozen "
+              "checkpoints + guard-final (builder untouched, env-bound "
+              "pin)")
+        pin16b = td / "pin16b.stats"
+        pin16b.write_text("3 0 999\n")
+        try:
+            cmd_guard(argparse.Namespace(**{**vars(ns16),
+                                            "pin": str(pin16b),
+                                            "rundir": str(td / "rd16b"),
+                                            "workdir": str(wd16)}))
+            check(False, "case 16b must refuse tampered pin bytes")
+        except SystemExit:
+            check(True, "case 16b fail-closed: pin bytes != licensed sha "
+                        "refused BEFORE launch")
+        os.environ["STUB_DISABLE"] = "1"
+        try:
+            wd16c = td / "wd16c"
+            wd16c.mkdir()
+            cmd_guard(argparse.Namespace(**{**vars(ns16),
+                                            "rundir": str(td / "rd16c"),
+                                            "workdir": str(wd16c)}))
+            check(False, "case 16c must refuse a DISABLED probe banner")
+        except SystemExit:
+            check(True, "case 16c fail-closed: probe saw pinning DISABLED "
+                        "-> no construction launch (bounded exposure)")
+        finally:
+            del os.environ["STUB_DISABLE"]
+        art16d = dict(art16, verdict="STOP")
+        (td / "gate-art16d.json").write_text(json.dumps(art16d))
+        try:
+            cmd_guard(argparse.Namespace(**{**vars(ns16),
+                                            "gate": str(td /
+                                                        "gate-art16d.json"),
+                                            "rundir": str(td / "rd16d"),
+                                            "workdir": str(wd16)}))
+            check(False, "case 16d must refuse a non-GREEN artifact")
+        except SystemExit:
+            check(True, "case 16d fail-closed: STOP artifact never "
+                        "licenses construction")
+        # case 17 [REV-C F5iii]: executable gate->config seams — the
+        # affordability block is written FROM the artifact-bound bundle
+        # (idempotent re-run OK; a conflicting existing block refuses;
+        # tampered sidecar bytes refuse), and config-cost transfers the
+        # guard-final realized figures into the REQUIRED Ledger basis.
+        cfg17 = td / "config17.json"
+        cfg17.write_text("{}")
+        ns17 = argparse.Namespace(gate=str(td / "gate-art.json"),
+                                  tokens=str(td / "tok" /
+                                             "tokens-full.jsonl"),
+                                  config=str(cfg17), allow_mock=True)
+        cmd_config_afford(ns17)
+        cmd_config_afford(ns17)     # idempotent re-run
+        got17 = json.loads(cfg17.read_text())["affordability"]
+        check(got17["tokens_full_sha256"]
+              == sha256_file(td / "tok" / "tokens-full.jsonl")
+              and got17["gate_artifact_sha256"]
+              == sha256_file(td / "gate-art.json"),
+              "case 17 config-affordability POPULATED from the licensed "
+              "bundle (no pilot stall) + idempotent")
+        tok17 = td / "tok-tampered.jsonl"
+        tok17.write_bytes(
+            (td / "tok" / "tokens-full.jsonl").read_bytes() + b" ")
+        try:
+            cmd_config_afford(argparse.Namespace(
+                **{**vars(ns17), "tokens": str(tok17)}))
+            check(False, "case 17 must refuse tampered sidecar bytes")
+        except SystemExit:
+            check(True, "case 17 fail-closed: sidecar bytes != the "
+                        "ARTIFACT-recorded sha refused")
+        cmd_config_cost(argparse.Namespace(
+            final=[str(rd16 / "construction-guard-final.json")],
+            prior_usd="3.1", rate="0.174", config=str(cfg17)))
+        cost17 = json.loads(cfg17.read_text())["cost"]
+        check(abs(cost17["usd_spent_prior"]
+                  - (3.1 + fin16["realized"]["usd"])) < 1e-6
+              and abs(cost17["construction_instance_hours"]
+                      - fin16["realized"]["instance_hours"]) < 1e-9,
+              "case 17 config-cost: guard-final realized figures become "
+              "the REQUIRED Ledger basis (never silent zeros)")
+        # case 18 [REV-C F5i]: ONE projection model, mechanically — the
+        # gate copy hashes to the frozen constant AND byte-matches the
+        # driver's vendored copy.
+        drvp = Path(__file__).resolve().parents[1] / "glm52-probe" \
+            / "f1k-harness" / "f1k_driver.py"
+        own18 = add7_block_sha256(__file__)
+        check(own18 == ADD7_SRC_SHA256
+              and add7_block_sha256(drvp) == own18,
+              "case 18 SHARED MODEL: gate block sha == frozen "
+              "ADD7_SRC_SHA256 == driver block sha (drift refuses)")
     print()
     if fails:
         print("BRINGUP-GATE SELFTEST FAILED (%d)" % len(fails))
         return 1
-    print("BRINGUP-GATE SELFTEST PASS — HONEST SCOPE [REV-B]: this $0 "
+    print("BRINGUP-GATE SELFTEST PASS — HONEST SCOPE [REV-C]: this $0 "
           "oracle exercises the projection/license logic (incl. reserve, "
           "dump conjuncts, regime+engagement refusals), the sampling rule "
           "mechanics, the per-item stats MERGE, manifest-vs-model "
-          "consistency, and the early-abort checkpoint — ALL on synthetic "
-          "corpora, planted timings, and a mock banner grammar. It CANNOT "
-          "exercise: the real engine (timer, STATS/PIN semantics), the "
-          "real tokenizer, GCS transfer, VM deploy, or the real corpus "
-          "bytes. Those exist only via the VM path + f1k_gcp.py gate.")
+          "consistency, the frozen-schedule early-abort checkpoint, the "
+          "construction-guard chain (license binding, probe grammar, "
+          "checkpoint kill-path, evidence artifacts — on STUB "
+          "engine/builder), the gate->config seams, and the shared-model "
+          "identity — ALL on synthetic corpora, planted timings, and a "
+          "mock banner grammar. It CANNOT exercise: the real engine "
+          "(timer, STATS/PIN semantics, dump-mode arming), the real "
+          "tokenizer, GCS transfer, VM deploy, or the real corpus bytes. "
+          "Those exist only via the VM path + f1k_gcp.py gate.")
     return 0
 
 
@@ -1416,14 +2011,48 @@ def main():
     p.add_argument("--tokens", required=True)
     p.add_argument("--n-done", required=True)
     p.add_argument("--elapsed-s", required=True)
+    p.add_argument("--n-start", default="0")
+    #   [REV-C] resumed construction: passes already cached at guard start
     p.add_argument("--out", default="")
+    p = sub.add_parser("guard")
+    # [REV-C F3] construction-guard (see cmd_guard)
+    p.add_argument("--gate", required=True)
+    p.add_argument("--pin", required=True)
+    p.add_argument("--engine-cmd", required=True,
+                   help="JSON argv of the CONSTRUCTION engine (the same "
+                        "value passed to build_carriers.py --engine-cmd)")
+    p.add_argument("--layers", required=True,
+                   help="comma layer list (same as build_carriers --layers)")
+    p.add_argument("--tokens", required=True,
+                   help="the gate run's tokens-full.jsonl sidecar")
+    p.add_argument("--rundir", required=True)
+    p.add_argument("--workdir", required=True,
+                   help="the builder's --workdir (concept-*.json appear "
+                        "here — the checkpoint progress signal)")
+    p.add_argument("--poll-seconds", default="60")
+    p.add_argument("builder", nargs=argparse.REMAINDER,
+                   help="-- <builder argv>")
+    p = sub.add_parser("config-affordability")
+    # [REV-C F5iii] gate artifact -> config.affordability (executable)
+    p.add_argument("--gate", required=True)
+    p.add_argument("--tokens", required=True)
+    p.add_argument("--config", required=True)
+    p.add_argument("--allow-mock", action="store_true")
+    p = sub.add_parser("config-cost")
+    # [REV-C F3] guard-final realized figures -> config.cost (executable)
+    p.add_argument("--final", action="append", required=True)
+    p.add_argument("--prior-usd", required=True)
+    p.add_argument("--rate", required=True)
+    p.add_argument("--config", required=True)
     sub.add_parser("selftest")
     args = ap.parse_args()
     if args.cmd == "selftest":
         return selftest()
     return {"spec": cmd_spec, "fcount": cmd_fcount, "realize": cmd_realize,
             "pinfile": cmd_pinfile, "collect": cmd_collect,
-            "checkpoint": cmd_checkpoint}[args.cmd](args)
+            "checkpoint": cmd_checkpoint, "guard": cmd_guard,
+            "config-affordability": cmd_config_afford,
+            "config-cost": cmd_config_cost}[args.cmd](args)
 
 
 if __name__ == "__main__":
```
<!-- END-ARTIFACT D14 -->

### C6.2 D15 — `poc/gcp/f1k_gcp.py` REV-C delta (launcher retry + local marker + watchdog SSH probe + pin-fetch /2 + eval-safe output)

<!-- BEGIN-ARTIFACT D15 f1k_gcp.py.rev-c.diff sha256=586a1f0846cc241d108e213f55fc243c9af3a7138a1236b6a87ddc1f1e7159d2 -->
```diff
diff --git a/poc/gcp/f1k_gcp.py b/poc/gcp/f1k_gcp.py
index 053bec8..32c8453 100755
--- a/poc/gcp/f1k_gcp.py
+++ b/poc/gcp/f1k_gcp.py
@@ -418,7 +418,7 @@ def cmd_affordability() -> None:
     the frozen ledger from ONE blended s/prefill (historically the synthetic
     functional-gate mix). It LICENSES NOTHING — the v2 review (finding 4)
     showed the synthetic blend mis-prices the gate in both directions. The
-    construction license is `f1k_gcp.py gate` (kot-f1k-bringup-gate/1:
+    construction license is `f1k_gcp.py gate` (kot-f1k-bringup-gate/2:
     real-corpus stratified sample + measured f + PER-ITEM token-aware
     projection) and ONLY that.
 
@@ -459,7 +459,7 @@ def cmd_affordability() -> None:
 
 
 def cmd_gate() -> None:
-    """The FIXED bring-up affordability gate verdict (kot-f1k-bringup-gate/1;
+    """The FIXED bring-up affordability gate verdict (kot-f1k-bringup-gate/2;
     poc/gcp/F1K-BRINGUP-GATE-FIX.md v1, closing CONSTRUCTION-PLAN v3 §4.2
     GAP-1/2/3). Consumes the on-VM gate-inputs.json (f1k_worker.sh step 5/5:
     real-corpus stratified per-item timing + measured f + per-item token
@@ -601,9 +601,16 @@ def cmd_bringup_deploy() -> None:
     # [REV-B F4] failure-visible launcher: ANY worker exit != 0 — incl.
     # `set -e` deaths that bypass die() and its heartbeat — writes a
     # FAILED heartbeat the watchdog acts on promptly (no max-life wait).
+    # [REV-C, rereview finding 4 residual] the GCS upload is no longer a
+    # single `|| true` shot: (1) a LOCAL on-disk FAILED marker is written
+    # FIRST (unconditional — visible to the watchdog's SSH-side probe even
+    # when GCS/auth/network is down), then (2) the upload retries 5x with
+    # exponential backoff. HONEST RESIDUAL: if GCS is unreachable AND the
+    # VM is not SSH-reachable (dead sshd/network), the failure stays
+    # invisible until the guest max-life backstop — stated, not hidden.
     (bundle / "f1k_launch.sh").write_text(
         "#!/usr/bin/env bash\n"
-        "# generated by f1k_gcp.py bringup-deploy [REV-B F4]\n"
+        "# generated by f1k_gcp.py bringup-deploy [REV-B F4 + REV-C]\n"
         "cd \"$(dirname \"$0\")\"\n"
         "bash f1k_worker.sh > worker.log 2>&1\n"
         "rc=$?\n"
@@ -611,8 +618,13 @@ def cmd_bringup_deploy() -> None:
         "  printf '{\"ts\":\"%s\",\"stage\":\"FAILED: worker exit rc=%d\","
         "\"rc\":%d}\\n' \"$(date -u +%FT%TZ)\" \"$rc\" \"$rc\" "
         "> failed-heartbeat.json\n"
-        "  gsutil -q cp failed-heartbeat.json "
-        "\"$KOT_F1K_BUCKET/f1k/bringup/heartbeat.json\" || true\n"
+        "  cp failed-heartbeat.json FAILED   # local marker, ALWAYS [REV-C]\n"
+        "  for i in 1 2 3 4 5; do\n"
+        "    gsutil -q cp failed-heartbeat.json "
+        "\"$KOT_F1K_BUCKET/f1k/bringup/heartbeat.json\" && break\n"
+        "    echo \"heartbeat upload attempt $i failed; retrying\" >&2\n"
+        "    sleep $((2**i))\n"
+        "  done\n"
         "fi\n"
         "exit \"$rc\"\n")
     shutil.copy2(HARNESS / "tok_glm52.py", bundle / "tok_glm52.py")
@@ -677,6 +689,27 @@ def cmd_watchdog() -> None:
                  bucket + "/f1k/bringup/heartbeat.json"],
                 capture_output=True, text=True)
             failed_hb = r.returncode == 0 and '"FAILED' in r.stdout
+        if not failed_hb:
+            # [REV-C, rereview finding 4 residual] SSH-side probe for the
+            # launcher's LOCAL FAILED marker — covers the window where the
+            # worker died but the GCS heartbeat upload could not land
+            # (GCS/auth/network trouble). A probe FAILURE is INCONCLUSIVE
+            # (VM booting/ssh flake), never a teardown trigger by itself;
+            # a VM unreachable via BOTH GCS and SSH stays covered only by
+            # the max-life backstop (stated residual).
+            try:
+                pr = gcloud("compute", "ssh", INSTANCE_NAME,
+                            "--zone", ZONE, "--command",
+                            "test -f ~/f1k/FAILED "
+                            "&& echo KOT-F1K-FAILED-LOCAL; true",
+                            check=False, capture=True)
+                if pr.returncode == 0 and "KOT-F1K-FAILED-LOCAL" \
+                        in pr.stdout:
+                    failed_hb = True
+                    print("watchdog: local FAILED marker seen via SSH "
+                          "(GCS heartbeat absent/stale)")
+            except Exception as ex:                        # noqa: BLE001
+                print("watchdog: SSH probe inconclusive (%s)" % ex)
         if time.time() >= deadline or failed_hb:
             print("watchdog: %s -> teardown"
                   % ("FAILED heartbeat" if failed_hb else
@@ -705,6 +738,11 @@ def cmd_pin_fetch() -> None:
     if not bucket:
         die("F1K_PIN_FETCH", "KOT_F1K_BUCKET unset")
     art = json.loads(Path(args.gate).read_text(encoding="utf-8"))
+    if art.get("schema") != "kot-f1k-bringup-gate/2":
+        # [REV-C F5ii] literal (no gate-module import on the control box):
+        # only the /2 model-bundle-bound artifact licenses construction.
+        die("F1K_PIN_FETCH", "gate artifact schema %r != "
+            "kot-f1k-bringup-gate/2 — refuse" % art.get("schema"))
     if art.get("verdict") != "GREEN":
         die("F1K_PIN_FETCH", "gate artifact verdict %r — only a GREEN "
             "license carries a construction pin" % art.get("verdict"))
@@ -726,7 +764,10 @@ def cmd_pin_fetch() -> None:
         die("F1K_PIN_FETCH", "fetched pin sha %s != licensed %s — the "
             "persisted bytes are NOT the licensed pin; fail closed"
             % (got, pin["pin_file_sha256"]))
-    print("campaign pin verified: %s (sha %s...)" % (dest, got[:16]))
+    # [REV-C] eval-safe split: exports alone on stdout (so
+    # `eval "$(... pin-fetch ...)"` is exact), diagnostics on stderr.
+    sys.stderr.write("campaign pin verified: %s (sha %s...)\n"
+                     % (dest, got[:16]))
     print("export PIN=%s" % dest)
     print("export PIN_GB=%s" % pin["pin_gb"])
 
```
<!-- END-ARTIFACT D15 -->

### C6.3 D16 — `poc/gcp/f1k_worker.sh` REV-C delta (stale schema-id comment only)

<!-- BEGIN-ARTIFACT D16 f1k_worker.sh.rev-c.diff sha256=bf48d3966a1c4b457004b4293ccc678b7a92818efc184dd44729bba8c1d83bff -->
```diff
diff --git a/poc/gcp/f1k_worker.sh b/poc/gcp/f1k_worker.sh
index d80a7a9..e257769 100755
--- a/poc/gcp/f1k_worker.sh
+++ b/poc/gcp/f1k_worker.sh
@@ -34,7 +34,7 @@
 #      tokenizer (measured f + per-item T), realize the frozen stratified
 #      timing sample, time it per-item (unpinned T1 -> bring-up pin file;
 #      pinned T2), and write gate-inputs.json. The GREEN/STOP verdict is the
-#      control box's `f1k_gcp.py gate` (kot-f1k-bringup-gate/1); the
+#      control box's `f1k_gcp.py gate` (kot-f1k-bringup-gate/2); the
 #      synthetic functional-gate blend stays a SECONDARY diagnostic ONLY.
 #      Then STOP + heartbeat DONE.
 #
```
<!-- END-ARTIFACT D16 -->

### C6.4 D17 — `poc/gcp/README.md` REV-C delta (guard-wrapped construction runbook; rebind removed; deferral stated)

<!-- BEGIN-ARTIFACT D17 README.md.rev-c.diff sha256=39dc74d505fcb571e2b065b307f217e583017a5b981b1f0c6dc5c19f01042549 -->
```diff
diff --git a/poc/gcp/README.md b/poc/gcp/README.md
index e6495b8..d134241 100644
--- a/poc/gcp/README.md
+++ b/poc/gcp/README.md
@@ -54,8 +54,8 @@ maintainer), **NOT a retry** — the pzb6 class discovered at bring-up.
 
 | File | What it is |
 |---|---|
-| `f1k_gcp.py` | Orchestrator (runs on the control box): `plan` ($0 dry-plan: pins + reuse-gate + SPOT/disk/window asserts), `provision` (Spot VM + 2 local SSD), `status`, `teardown`, `bringup-deploy` (RAID+mount NVMe, push the worker bundle + frozen gate corpora, launch the worker detached, arm the guest max-life), `watchdog --max-hours H` (box-side teardown loop; nohup it, verify `pgrep -f 'f1k_gcp.py watchdog'`), `gate` (**the bring-up gate verdict — kot-f1k-bringup-gate/1; GREEN is the ONLY construction license**; `--selftest` = $0 mock oracle), `pin-fetch` (fetch + byte-verify the licensed campaign pin → explicit `PIN`/`PIN_GB` exports [REV-B]), `affordability` (one-blended-s/prefill projection — **SECONDARY diagnostic ONLY, licenses nothing**). |
-| `f1k_bringup_gate.py` | The FIXED bring-up gate machinery (`F1K-BRINGUP-GATE-FIX.md` v1+REV-B, GAP-1/2/3): frozen deterministic stratified real-corpus sampling rule, full-corpus tokenization (measured f, per-item T), per-item-manifest bring-up pin derivation (fail-closed merge + provenance), per-item token-aware ledger projection + GREEN/STOP artifact (engagement-verified, unpinned refused), `checkpoint` = construction early-abort re-projection; `selftest` = $0 mock oracle of the LOGIC seams only (no real engine/tokenizer/GCS/VM — honest scope printed). |
+| `f1k_gcp.py` | Orchestrator (runs on the control box): `plan` ($0 dry-plan: pins + reuse-gate + SPOT/disk/window asserts), `provision` (Spot VM + 2 local SSD), `status`, `teardown`, `bringup-deploy` (RAID+mount NVMe, push the worker bundle + frozen gate corpora, launch the worker detached, arm the guest max-life), `watchdog --max-hours H` (box-side teardown loop; nohup it, verify `pgrep -f 'f1k_gcp.py watchdog'`), `gate` (**the bring-up gate verdict — kot-f1k-bringup-gate/2; GREEN is the ONLY construction license**; `--selftest` = $0 mock oracle), `pin-fetch` (fetch + byte-verify the licensed campaign pin → eval-safe explicit `PIN`/`PIN_GB` exports; `/2`+GREEN required [REV-B/C]), `affordability` (one-blended-s/prefill projection — **SECONDARY diagnostic ONLY, licenses nothing**). |
+| `f1k_bringup_gate.py` | The FIXED bring-up gate machinery (`F1K-BRINGUP-GATE-FIX.md` v1+REV-B+REV-C, GAP-1/2/3): frozen deterministic stratified real-corpus sampling rule, full-corpus tokenization (measured f, per-item T), per-item-manifest bring-up pin derivation (fail-closed merge + provenance), per-item token-aware ledger projection + GREEN/STOP **`/2` model-bundle-bound** artifact (engagement-verified, unpinned refused), `checkpoint` = frozen-schedule construction early-abort re-projection, `guard` = **construction wrapper** (explicit pin env + dump-mode engagement probe + in-process checkpoints + kill-on-breach; the sha-pinned builder stays untouched), `config-affordability`/`config-cost` = executable gate→campaign-config seams; `selftest` = $0 mock oracle of the LOGIC seams only (no real engine/tokenizer/GCS/VM — honest scope printed). |
 | `bringup_gcp.sh` | KaE bring-up on the VM: colibri@`a78a06fc` + KaE patch (`11f8b458`), build, 44/44 `test_kae`; objdump patch-shape checks (clone-aware, reference + native flags) are **ADVISORY-ONLY on the VM** (bead f2uk / ASM-2503: gcc-version-brittle even at `-O2 -march=x86-64-v3`; fail-closed objdump lives off-box on the gcc-11.5 basis; the frozen `bringup.sh` is untouched). The AUTHORITATIVE inertness proof is the functional KAE-unset byte-identity gate in `f1k_worker.sh`. |
 | `f1k_worker.sh` | On-VM autonomous worker: STAGE (GCS mirror → else HF → NVMe, weight-hash pin) → BUILD scoring + construction engines → KaE bring-up → dump bring-up gate (b) → scaffolds (a)+(c) → **REAL-CORPUS gate inputs** (tokenize → measured f + per-item T; frozen stratified per-item timing, T1 unpinned → bring-up pin → T2 pinned; `gate-inputs.json`) → **STOP before construction spend**. Heartbeat + artifacts to GCS; idempotent (spot preemption re-runs, restages from GCS). |
 
@@ -112,38 +112,67 @@ maintainer), **NOT a retry** — the pzb6 class discovered at bring-up.
    tested STOP exits nonzero. The synthetic blend + `f1k_gcp.py
    affordability` remain a SECONDARY diagnostic, licensing nothing (exit 3
    even when clean).
-5. **Construction** (gated on 3+4): FIRST fetch + byte-verify the licensed
-   pin and take the EXPLICIT env exports — never ambient:
-   `python3 poc/gcp/f1k_gcp.py pin-fetch --gate bringup-gate.json --out
-   <rundir>` (fail-closed: GREEN artifact only; fetched bytes must sha-match
-   `pin.pin_file_sha256`; prints `export PIN=<path>` + `export
-   PIN_GB=<licensed>`). THEN `build_carriers.py construct --mode real
-   --layers 3,…,77` (the landed ASM-2504 DRAFT=0 geometry, 75 layers) with the
-   three provenance shas **and their artifacts**
-   (`--tokenizer-sha/-artifact`, `--engine-weights-sha/-artifact`,
-   `--dump-patch-sha/-artifact`), 4,608 passes EXACT, run with
-   `STATS=<rundir>/stats/item-<n>.stats` per pass (one file each, manifest
-   recorded — the free full-corpus derivation input); the runner runs the
-   **early-abort checkpoints** at n_done 200/1024/2304
-   (`f1k_bringup_gate.py checkpoint --gate bringup-gate.json --tokens
-   <gate-tokens/tokens-full.jsonl> --n-done N --elapsed-s S` — STOP exit 2 =
-   kill construction, maintainer surface; first exposure ≈ $1.3);
-   `verify --expect-mode real` (full cell-by-cell re-derivation, the #46
-   guarantee); commit the realized tables + `norms.json` +
-   `construction-report.json` = **B0**, completing `f1k-carriers-v1`. Pin
-   `glm52-weights` (ASM-1971 ops amendment).
-   **Construction→pilot pin boundary** (the ONLY lawful pin-change point):
-   IF the full-corpus pin (merged from the 4,608 per-pass stats via
-   `pinfile --stats-manifest`, fail-closed) is to replace the bring-up pin,
-   that is a DELIBERATE, RECORDED re-binding: the coordinator commits
-   `campaign-pin-rebind.json` {old_sha = the licensed pin sha, new_sha,
-   PIN_GB **unchanged** (fixed once at bring-up — the landed driver refuses
-   a PIN_GB drift), stats manifest sha, authorization: maintainer sign-off}
-   to GCS + the run log BEFORE pilot start, and the pilot config carries the
-   NEW pin; the landed ASM-2513 machinery (Ledger cross-phase basis +
-   `check_addendum_pinning` + spend-start sentinel) then enforces constancy
-   across pilot/guard/test. No rebind record → the licensed bring-up pin
-   runs the whole campaign. Never mid-phase, never silent.
+5. **Construction** (gated on 3+4) **[REV-C: guard-wrapped; the sha-pinned
+   builder is byte-untouched]**:
+   a. Fetch + byte-verify the licensed pin:
+      `python3 poc/gcp/f1k_gcp.py pin-fetch --gate bringup-gate.json --out
+      <rundir>` (fail-closed: schema `/2` + GREEN only; fetched bytes must
+      sha-match `pin.pin_file_sha256`; stdout = the exact `export PIN=` /
+      `export PIN_GB=` lines, eval-safe — but step 5b consumes `--pin`
+      directly, no ambient env needed).
+   b. Launch construction THROUGH the guard (ONE command; the guard binds
+      `PIN`/`PIN_GB` into the child env itself — never ambient; pops
+      `STATS` and the mode knobs; probes engagement; runs the frozen
+      checkpoints; kills on breach):
+      `python3 poc/gcp/f1k_bringup_gate.py guard --gate bringup-gate.json
+      --pin <rundir>/campaign-pin.stats --engine-cmd '<json argv>'
+      --layers 3,…,77 --tokens <gate-tokens/tokens-full.jsonl>
+      --rundir <rundir>/guard --workdir <workdir> --
+      python3 poc/glm52-probe/f1k-harness/build_carriers.py construct
+      --mode real --layers 3,…,77 <provenance shas AND artifacts:
+      --tokenizer-sha/-artifact --engine-weights-sha/-artifact
+      --dump-patch-sha/-artifact> --out <out> --workdir <workdir>`
+      (4,608 passes EXACT; ASM-2504 DRAFT=0 geometry, 75 layers). The
+      guard FIRST runs a **dump-mode pin-engagement probe** (one minimal
+      `KAE_DUMP` invocation of the same engine argv/env; armed banner per
+      the landed ASM-2513 grammar, sha/budget/source coherent — REFUSED ⇒
+      no launch, exposure ≈ one engine start), then launches the builder
+      (which passes its ambient env into every engine batch —
+      `build_carriers.py:634`, verified bytes), and runs the
+      **early-abort checkpoints** IN-PROCESS at n_done **240/1056/2304**
+      (frozen concept-aligned schedule [REV-C/ASM-2517]; off-schedule
+      n_done is refused; STOP exit 2 = builder process-group killed +
+      `construction-abort.json`; first exposure ≈ 9.1 h ≈ **$1.59**).
+      Evidence: `construction-pin-probe.json`,
+      `construction-checkpoint-<n>.json`, `construction-guard-final.json`.
+   c. `verify --expect-mode real` (full cell-by-cell re-derivation, the
+      #46 guarantee); commit the realized tables + `norms.json` +
+      `construction-report.json` = **B0**, completing `f1k-carriers-v1`.
+      Pin `glm52-weights` (ASM-1971 ops amendment).
+   d. Transfer the realized cost basis + the licensed model bundle into
+      the campaign config (executable, no pilot stall):
+      `python3 poc/gcp/f1k_bringup_gate.py config-cost --final
+      <rundir>/guard/construction-guard-final.json --prior-usd <metered
+      pre-construction spend> --rate <campaign spot rate> --config
+      run-config.json` and
+      `python3 poc/gcp/f1k_bringup_gate.py config-affordability --gate
+      bringup-gate.json --tokens <gate-tokens/tokens-full.jsonl> --config
+      run-config.json` (both refuse a conflicting existing block; the
+      driver re-verifies EVERYTHING at consumption — schema `/2`, GREEN,
+      shared-model sha, sidecar bytes vs the ARTIFACT-recorded sha,
+      corpus item-universe, rate equality, pin identity).
+   **Campaign pin [REV-C]: the LICENSED bring-up pin runs the WHOLE
+   campaign.** Full-corpus re-derivation at the construction→pilot
+   boundary is **DEFERRED** (it needs per-batch `STATS` hooks the
+   sha-pinned builder does not have — a seq-4 builder re-freeze, tracked
+   as a bead, NOT on this critical path); there is NO rebind record and
+   NO rebind path — the driver REFUSES a campaign pin whose sha differs
+   from the gate artifact's, and the landed ASM-2513 machinery (Ledger
+   cross-phase basis + `check_addendum_pinning` + spend-start sentinel)
+   enforces constancy across pilot/guard/test. Under-coverage of the
+   bring-up pin shows up as throughput loss and is bounded by the
+   checkpoints (≤ ≈$1.6/$7/$15 at 240/1056/2304) and the addendum-(7)
+   pre-main gate. Never mid-phase, never silent.
 6. **Pilot** (`f1k_driver.py --phase pilot`): produces `addendum-5-frozen-lg`,
    `addendum-7-affordability`, `addendum-6-inputs` (dev δ̂, the dev
    sign-symmetry check). **HANDOFF**: the addendum-(6) inference method
```
<!-- END-ARTIFACT D17 -->

### C6.5 D18 — `poc/glm52-probe/f1k-harness/f1k_driver.py` REV-C delta (shared model + bundle binding + kappa reweight + mock hardening)

<!-- BEGIN-ARTIFACT D18 f1k_driver.py.rev-c.diff sha256=93e11dd35bf8dd71b44c3935fc2928544c6fb2490a12d030aa1251f1dd80ee65 -->
```diff
diff --git a/poc/glm52-probe/f1k-harness/f1k_driver.py b/poc/glm52-probe/f1k-harness/f1k_driver.py
index 6604425..39a0f76 100755
--- a/poc/glm52-probe/f1k-harness/f1k_driver.py
+++ b/poc/glm52-probe/f1k-harness/f1k_driver.py
@@ -2661,9 +2661,81 @@ def phase_test(cfg, ev, outdir, frozen, passes, ledger, mock_gold_dir=None,
     return rows_path, n_new
 
 
+# ---- KOT-ADD7-SHARED-BEGIN ------------------------------------------------
+# [REV-C F5i, F1K-BRINGUP-GATE-FIX.md SSC] ONE projection-model
+# implementation, byte-identical in poc/gcp/f1k_bringup_gate.py and
+# poc/glm52-probe/f1k-harness/f1k_driver.py. Each copy is verified at
+# runtime: block sha256 == the in-file ADD7_SRC_SHA256 constant AND (at
+# consumption) == the licensed gate artifact's model_bundle.add7_src_sha256
+# — drift in EITHER copy is a refusal, never a silent second
+# implementation. Semantics (frozen, fix memo SS2.6): piecewise-linear in T
+# over isotonic knots; below the min knot central/hi are CONSTANT
+# (cap-conservative) and the lo band extrapolates floored at
+# floor_frac*s(minknot); above the max sampled knot: Add7RangeError
+# (extrapolation above the frozen sample is FORBIDDEN — the campaign max-T
+# text is in the sample by construction).
+class Add7RangeError(ValueError):
+    """T above the max sampled knot — never extrapolated."""
+
+
+def add7_interp(knots, sfield, t, below="const", floor_frac=0.35):
+    ts = [k["T"] for k in knots]
+    ss = [k[sfield] for k in knots]
+    if t > ts[-1] + 1e-9:
+        raise Add7RangeError(
+            "T=%.0f above max sampled knot %.0f" % (t, ts[-1]))
+    if t <= ts[0]:
+        if below == "const" or len(ts) < 2:
+            return ss[0]
+        slope = (ss[1] - ss[0]) / max(1e-9, ts[1] - ts[0])
+        return max(floor_frac * ss[0], ss[0] - slope * (ts[0] - t))
+    for i in range(len(ts) - 1):
+        if t <= ts[i + 1]:
+            frac = (t - ts[i]) / max(1e-9, ts[i + 1] - ts[i])
+            return ss[i] + frac * (ss[i + 1] - ss[i])
+    return ss[-1]
+
+
+def add7_block_sha256(path):
+    """sha256 over the exact lines BETWEEN the shared-block markers
+    (marker lines excluded); None when the markers are absent/ambiguous."""
+    lines = open(path, encoding="utf-8").read().split("\n")
+    beg = [i for i, l in enumerate(lines)
+           if l.startswith("# ---- KOT-ADD7-SHARED-BEGIN")]
+    end = [i for i, l in enumerate(lines)
+           if l.startswith("# ---- KOT-ADD7-SHARED-END")]
+    if len(beg) != 1 or len(end) != 1 or end[0] <= beg[0]:
+        return None
+    body = "\n".join(lines[beg[0] + 1:end[0]])
+    return hashlib.sha256(body.encode("utf-8")).hexdigest()
+# ---- KOT-ADD7-SHARED-END --------------------------------------------------
+
+
+ADD7_SRC_SHA256 = "9d3e1bc76f8506d99a29b0465af2c063b32ba8d726e7ec2c6a65e3c596260353"
+#   [REV-C F5i] frozen sha256 of the KOT-ADD7-SHARED block body (both
+#   copies must hash to THIS value; the gate refuses to emit an artifact
+#   from a drifted copy, and this driver refuses to consume one).
+ADD7_GATE_SCHEMA = "kot-f1k-bringup-gate/2"
+#   [REV-C F5ii] the ONLY consumable gate-artifact schema: /2 adds the
+#   REQUIRED model_bundle binding (add7_src_sha256 + tokens_full_sha256).
+
+
+def add7_cap_breach(p4, rate):
+    """[REV-C] reserve-inclusive cap test at central AND +1SE (module
+    level so the $0 mock exercises the degradation boundary with the
+    SAME predicate phase_pilot uses)."""
+    u_c, u_hi, h_c, h_hi = p4
+    reserve_h = RESERVE_USD_ADD7 / rate
+    return (u_c + RESERVE_USD_ADD7 > USD_CAP
+            or u_hi + RESERVE_USD_ADD7 > USD_CAP
+            or h_c + reserve_h > WALL_CLOCK_CAP_HOURS
+            or h_hi + reserve_h > WALL_CLOCK_CAP_HOURS)
+
+
 class Add7Model:
-    """[REV-B GAP-3b / gate-fix review #1; ASM-2516] The FROZEN bring-up
-    gate projection model (kot-f1k-bringup-gate/1) consumed at the
+    """[REV-B GAP-3b / gate-fix review #1; ASM-2516 / REV-C ASM-2517] The
+    FROZEN bring-up gate projection model (kot-f1k-bringup-gate/2,
+    model-bundle-BOUND) consumed at the
     pilot->main seam — ONE projection model, stated once (ASM-2514/2515),
     used by BOTH seams. Inputs (config.affordability, REQUIRED for a real
     campaign, every path sha-verified fail-closed):
@@ -2708,34 +2780,109 @@ class Add7Model:
                  "gate artifact tokenizer mode is not REAL and "
                  "_allow_mock is unset — a mock gate model never enters "
                  "a real campaign projection")
+        # ---- [REV-C F5ii] the WHOLE bundle must be the LICENSED one —
+        # a self-consistent config pointing at non-licensed bytes is
+        # refused on the ARTIFACT-recorded identities, never trusted:
+        if art.get("schema") != ADD7_GATE_SCHEMA:
+            fail("ERR_F1K_AFFORD",
+                 "gate artifact schema %r != %s — only a /2 model-bundle-"
+                 "bound artifact is consumable [REV-C]"
+                 % (art.get("schema"), ADD7_GATE_SCHEMA))
+        if art.get("verdict") != "GREEN":
+            fail("ERR_F1K_AFFORD",
+                 "gate artifact verdict %r — a non-GREEN gate never "
+                 "drives the pilot->main projection [REV-C]"
+                 % art.get("verdict"))
+        mb = art.get("model_bundle") or {}
+        if mb.get("tokens_full_sha256") != blk["tokens_full_sha256"]:
+            fail("ERR_F1K_AFFORD",
+                 "config-declared sidecar sha %r != the ARTIFACT-recorded "
+                 "model_bundle.tokens_full_sha256 %r — the config binds "
+                 "whatever the ARTIFACT licensed, not what it declares "
+                 "about itself [REV-C F5ii]"
+                 % (blk["tokens_full_sha256"][:16],
+                    (mb.get("tokens_full_sha256") or "")[:16]))
+        own = add7_block_sha256(__file__)
+        if own != ADD7_SRC_SHA256 or mb.get("add7_src_sha256") != own:
+            fail("ERR_F1K_AFFORD",
+                 "shared-model identity broken (own block %r, frozen %s, "
+                 "artifact %r) — ONE model implementation, sha-verified; "
+                 "a drifted copy never projects [REV-C F5i]"
+                 % (own and own[:16], ADD7_SRC_SHA256[:16],
+                    (mb.get("add7_src_sha256") or "")[:16]))
+        rate_cfg = float((cfg.get("cost") or {})
+                         .get("spot_rate_usd_per_hour", -1.0))
+        rate_art = float((art.get("rate") or {}).get("usd_per_hour", -2.0))
+        if rate_cfg != rate_art:
+            fail("ERR_F1K_AFFORD",
+                 "config cost rate %r != the gate artifact's licensed "
+                 "rate %r — the projection was licensed AT that rate; a "
+                 "different campaign rate is a different license "
+                 "[REV-C F5ii]" % (rate_cfg, rate_art))
+        if not self.mock:
+            cur_pin = validate_pinning(cfg)
+            if (art.get("pin") or {}).get("pin_file_sha256") \
+                    != cur_pin["pin_file_sha256"]:
+                fail("ERR_F1K_PINNING",
+                     "campaign pin sha %r != the gate artifact's licensed "
+                     "pin %r — REV-C runs the LICENSED bring-up pin for "
+                     "the whole campaign (full-corpus re-derivation is "
+                     "DEFERRED, no rebind path exists); a different pin "
+                     "is a different license"
+                     % (cur_pin["pin_file_sha256"][:16],
+                        ((art.get("pin") or {})
+                         .get("pin_file_sha256") or "")[:16]))
         self.knots = sorted(art["model"]["knots_isotonic"],
                             key=lambda k: k["T"])
         if not self.knots:
             fail("ERR_F1K_AFFORD", "gate artifact carries no knots")
         self.cont = art["model"]["cont_tokens_addend"]
         self.art_sha = blk["gate_artifact_sha256"]
+        self.kappa_weighting = None    # set by kappa() [REV-C F5iv]
         self.tp = {}
         for ln in open(blk["tokens_full_path"], encoding="utf-8"):
             if ln.strip():
                 e = json.loads(ln)
                 self.tp[e["key"]] = e["T"] + self.cont
 
+    def verify_corpus(self, ev):
+        """[REV-C F5ii corpus identity, driver-verifiable form] the
+        licensed sidecar must cover EXACTLY this campaign's eval items:
+        the {pilot, main-tmpl, main-d3, guard} key sets are a bijection
+        with the loaded ev splits (byte-identity of the corpora is
+        enforced on the gate side via corpus_sha256 in the artifact and
+        on the driver side via the landed verify_corpus_pins; this check
+        binds the TWO records to the SAME item universe)."""
+        want = set()
+        for it in ev["dev"]:
+            want.add("pilot:%s" % it["item_id"])
+        for it in ev["test"]:
+            want.add("main-tmpl:%s" % it["item_id"])
+            want.add("main-d3:%s" % it["item_id"])
+        for it in ev["guard"]:
+            want.add("guard:%s" % it["item_id"])
+        have = {k for k in self.tp
+                if k.split(":", 1)[0] in ("pilot", "main-tmpl", "main-d3",
+                                          "guard")}
+        if want != have:
+            fail("ERR_F1K_AFFORD",
+                 "gate sidecar item universe != this campaign's eval "
+                 "items (%d missing, %d foreign; e.g. %s) — the licensed "
+                 "bundle projects a DIFFERENT corpus [REV-C F5ii]"
+                 % (len(want - have), len(have - want),
+                    sorted(want.symmetric_difference(have))[:3]))
+
     def _interp(self, t, field):
-        ks = self.knots
-        if t > ks[-1]["T"] + 1e-9:
+        # [REV-C F5i] delegate to the SHARED implementation (KOT-ADD7-
+        # SHARED block) — the driver keeps only its error surface.
+        try:
+            return add7_interp(self.knots, field, t, below="const")
+        except Add7RangeError:
             fail("ERR_F1K_AFFORD",
                  "T=%.0f above the max sampled knot %.0f — extrapolation "
                  "above the frozen sample is FORBIDDEN (the campaign "
                  "max-T text is in the sample by construction)"
-                 % (t, ks[-1]["T"]))
-        if t <= ks[0]["T"]:
-            return ks[0][field]
-        for i in range(len(ks) - 1):
-            if t <= ks[i + 1]["T"]:
-                fr = (t - ks[i]["T"]) / max(1e-9,
-                                            ks[i + 1]["T"] - ks[i]["T"])
-                return ks[i][field] + fr * (ks[i + 1][field] - ks[i][field])
-        return ks[-1][field]
+                 % (t, self.knots[-1]["T"]))
 
     def s_hat(self, t, hi=False):
         if hi:
@@ -2749,13 +2896,38 @@ class Add7Model:
                  "— the per-item projection never guesses a length" % key)
         return self.tp[key]
 
-    def kappa(self, realized_s_per_prefill, ev):
-        num, den = 0.0, 0
-        for it in ev["dev"]:
-            num += self.s_hat(self.tp_of("pilot:%s" % it["item_id"]))
-            den += 1
+    def kappa(self, realized_s_per_prefill, ev, pass_rows):
+        """[REV-C F5iv] kappa = realized pilot s/prefill / model-predicted
+        pilot blend, where the prediction is PREFILL-WEIGHTED over the
+        REALIZED pilot pass structure: each scored pilot row (grid passes
+        over the 48-item tuning subset, f1k_driver phase_pilot section 1,
+        + the full-dev-96 passes, section 3 — read back from the pilot
+        rows checkpoint) contributes one weight to its item. The REV-B
+        unweighted 96-item mean mislabeled the blend (grid traffic
+        weights the subset ~heavily); the realized-row weighting matches
+        the numerator's ledger basis (same scored prefills) exactly, and
+        stays exact under resume/REPLACE-support variation."""
+        dev_ids = {it["item_id"] for it in ev["dev"]}
+        w = {}
+        for r in pass_rows:
+            iid = r.get("item_id")
+            if iid in dev_ids:
+                w[iid] = w.get(iid, 0) + 1
+        if not w:
+            fail("ERR_F1K_AFFORD", "no pilot rows to calibrate kappa — "
+                 "the prefill-weighted blend needs the realized pass "
+                 "structure, never a guessed inventory [REV-C F5iv]")
+        num = sum(n * self.s_hat(self.tp_of("pilot:%s" % iid))
+                  for iid, n in w.items())
+        den = sum(w.values())
         if den == 0 or num <= 0:
             fail("ERR_F1K_AFFORD", "no pilot entries to calibrate kappa")
+        self.kappa_weighting = {
+            "rule": "prefill-weighted over the REALIZED pilot pass rows "
+                    "(grid passes weight the 48-item subset) [REV-C "
+                    "F5iv]",
+            "n_pass_rows": den, "distinct_items": len(w),
+            "weight_min": min(w.values()), "weight_max": max(w.values())}
         k = realized_s_per_prefill / (num / den)
         if not self.mock and not (ADD7_KAPPA_BOUNDS[0] <= k
                                   <= ADD7_KAPPA_BOUNDS[1]):
@@ -3504,7 +3676,9 @@ def phase_pilot(cfg, ev, outdir, ledger, mock_gold_dir=None):
     rate = ledger.d["spot_rate_usd_per_hour"]
     prior = ledger.d["usd_spent_prior"]
     a7m = Add7Model(cfg)
-    kappa = a7m.kappa(s_per_prefill, ev)
+    a7m.verify_corpus(ev)          # [REV-C F5ii] same item universe
+    _, k_rows = read_ckpt(rows_path)
+    kappa = a7m.kappa(s_per_prefill, ev, k_rows)   # [REV-C F5iv]
     reserve_h = RESERVE_USD_ADD7 / rate
     base_h = ledger.d["construction_instance_hours"] + pilot_s / 3600.0
     steps_taken = [DEGRADATION_ORDER[0]]
@@ -3522,11 +3696,9 @@ def phase_pilot(cfg, ev, outdir, ledger, mock_gold_dir=None):
                 base_h + sec_hi / 3600.0)
 
     def cap_breach(p4):
-        u_c, u_hi, h_c, h_hi = p4
-        return (u_c + RESERVE_USD_ADD7 > USD_CAP
-                or u_hi + RESERVE_USD_ADD7 > USD_CAP
-                or h_c + reserve_h > WALL_CLOCK_CAP_HOURS
-                or h_hi + reserve_h > WALL_CLOCK_CAP_HOURS)
+        # [REV-C] the module-level predicate — ONE reserve rule, also
+        # exercised at the degradation boundary by the $0 mock.
+        return add7_cap_breach(p4, rate)
 
     proj4 = projection(d3_deferred, replace_candidate)
     if cap_breach(proj4) and replace_candidate:
@@ -3568,6 +3740,7 @@ def phase_pilot(cfg, ev, outdir, ledger, mock_gold_dir=None):
                      "seams" % a7m.art_sha[:16],
             "kappa_realized_over_predicted": round(kappa, 4),
             "kappa_bounds": list(ADD7_KAPPA_BOUNDS),
+            "kappa_weighting": a7m.kappa_weighting,   # [REV-C F5iv]
             "usd_total": {"central": round(proj4[0], 2),
                           "hi": round(proj4[1], 2)},
             "instance_hours": {"central": round(proj4[2], 1),
@@ -3876,23 +4049,35 @@ def gen_mock_fixtures(outdir):
     # _allow_mock; NEVER a license input): knot s-level ~stub scale, kappa
     # unbounded under mock (a real artifact enforces ADD7_KAPPA_BOUNDS).
     tokens_path = fx / "mock-tokens-full.jsonl"
+
+    def _mock_t(key):
+        # [REV-C F5v] deterministic HETEROGENEOUS per-item T in [16, 52]
+        # (Tp = T+8 <= 60 stays under the mock max knot 64): the REV-B
+        # uniform T=24 traversed the per-item code without proving
+        # per-item projection — distinct T per item does.
+        return 16 + int(hashlib.sha256(key.encode("utf-8"))
+                        .hexdigest()[:4], 16) % 37
+
     with open(tokens_path, "w", encoding="utf-8") as f:
         for iid in split_ids["test"]:
+            t = _mock_t("main-tmpl:%s" % iid)
             f.write(json.dumps({"key": "main-tmpl:%s" % iid,
-                                "pop": "main-tmpl", "m": 7, "W": 24,
-                                "T": 24}) + "\n")
+                                "pop": "main-tmpl", "m": 7, "W": t,
+                                "T": t}) + "\n")
             f.write(json.dumps({"key": "main-d3:%s" % iid,
-                                "pop": "main-d3", "m": 1, "W": 27,
-                                "T": 27}) + "\n")
+                                "pop": "main-d3", "m": 1, "W": t + 3,
+                                "T": t + 3}) + "\n")
         for iid in split_ids["dev"]:
+            t = _mock_t("pilot:%s" % iid)
             f.write(json.dumps({"key": "pilot:%s" % iid, "pop": "pilot",
-                                "m": 22, "W": 24, "T": 24}) + "\n")
+                                "m": 22, "W": t, "T": t}) + "\n")
         for iid in split_ids["guard"]:
+            t = _mock_t("guard:%s" % iid)
             f.write(json.dumps({"key": "guard:%s" % iid, "pop": "guard",
-                                "m": 11, "W": 24, "T": 24}) + "\n")
+                                "m": 11, "W": t, "T": t}) + "\n")
     gate_art_path = fx / "mock-bringup-gate.json"
     write_json(gate_art_path, {
-        "schema": "kot-f1k-bringup-gate/1", "_mock": True,
+        "schema": "kot-f1k-bringup-gate/2", "_mock": True,
         "verdict": "GREEN",
         "tokenizer": {"mode": "MOCK", "sha256": None},
         "model": {"knots_isotonic": [
@@ -3901,6 +4086,12 @@ def gen_mock_fixtures(outdir):
             {"stratum": "max", "T": 64.0, "s": 0.03,
              "se": 0.003, "n": 1}],
             "cont_tokens_addend": 8},
+        # [REV-C F5ii] the /2 model-bundle binding, mock-shaped: the
+        # sidecar sha is the REAL sha of the fixture sidecar and the
+        # shared-model sha is THE frozen constant — so the driver's
+        # binding checks run for real even on the $0 path.
+        "model_bundle": {"add7_src_sha256": ADD7_SRC_SHA256,
+                         "tokens_full_sha256": sha256_file(tokens_path)},
         "rate": {"usd_per_hour": SPOT_RATE_DEFAULT},
         "pin": {"pin_file_sha256": None, "pin_gb": 48.0,
                 "regime": "pinned-bringup", "note": "MOCK artifact"}})
@@ -4809,6 +5000,59 @@ def mock_main(args):
     def ref(n):
         return "f1k_driver.py:%s" % ",".join(map(str, refs.get(str(n), [])))
 
+    # ---- [REV-C F5] shared-model / bundle-binding / kappa / boundary ----
+    print("probe: [REV-C] Add7Model bundle tamper probes — the next "
+          "ERR_F1K_AFFORD lines are EXPECTED")
+    a7_art = json.loads((outdir / "pilot" /
+                         "addendum-7-affordability.json")
+                        .read_text(encoding="utf-8"))
+    prb = a7_art.get("projection_rev_b") or {}
+    kw = prb.get("kappa_weighting") or {}
+    t_vals = [json.loads(l)["T"] for l in
+              open(cfg["affordability"]["tokens_full_path"],
+                   encoding="utf-8") if l.strip()]
+    het_ok = len(set(t_vals)) >= 10
+    kw_ok = (kw.get("distinct_items") == DEV_N
+             and kw.get("n_pass_rows", 0) > DEV_N
+             and kw.get("weight_max", 0) > kw.get("weight_min", 0))
+    gate_copy = HERE.parents[1] / "gcp" / "f1k_bringup_gate.py"
+    own_a7 = add7_block_sha256(__file__)
+    shared_ok = (own_a7 == ADD7_SRC_SHA256
+                 and add7_block_sha256(gate_copy) == own_a7)
+    tam_tok = outdir / "fixtures" / "tokens-tampered.jsonl"
+    tam_tok.write_bytes(Path(cfg["affordability"]["tokens_full_path"])
+                        .read_bytes() + b"\n")
+    cfg_t = json.loads(json.dumps(cfg))
+    cfg_t["affordability"]["tokens_full_path"] = str(tam_tok)
+    try:
+        Add7Model(cfg_t)
+        tamper_closed = False
+    except DriverError:
+        tamper_closed = True
+    cfg_t2 = json.loads(json.dumps(cfg))
+    cfg_t2["affordability"]["tokens_full_path"] = str(tam_tok)
+    cfg_t2["affordability"]["tokens_full_sha256"] = sha256_file(tam_tok)
+    try:
+        Add7Model(cfg_t2)
+        bundle_closed = False
+    except DriverError:
+        bundle_closed = True
+    a7p = Add7Model(cfg)
+    a7p.verify_corpus(ev)
+    rate_p = float(cfg["cost"]["spot_rate_usd_per_hour"])
+
+    def _p4(d3d, rep, kap):
+        sc = a7p.remaining_seconds(ev, d3d, rep, kap)
+        sh = a7p.remaining_seconds(ev, d3d, rep, kap, hi=True)
+        return (sc / 3600.0 * rate_p, sh / 3600.0 * rate_p,
+                sc / 3600.0, sh / 3600.0)
+
+    kap_b = ((USD_CAP - RESERVE_USD_ADD7 - 1.0) * 3600.0 / rate_p
+             / a7p.remaining_seconds(ev, True, False, 1.0, hi=True))
+    boundary_ok = (add7_cap_breach(_p4(False, True, kap_b), rate_p)
+                   and not add7_cap_breach(_p4(True, False, kap_b),
+                                           rate_p))
+
     print("\n== MOCK SELF-CHECK (codex FIX-FIRST launch blockers 1-7) ==")
     checks = [
         ("[1] SCORER: robust stdout parse — %d banner line(s) skipped "
@@ -4985,6 +5229,25 @@ def mock_main(args):
          "(guard.n_items=0, sha re-pinned attacker-consistent, every "
          "hash check green) -> verdict %r" % (verdict_bad.get("verdict"),),
          seam_tamper),
+        ("[REV-C F5] ONE bound projection model: shared-block sha "
+         "verified in BOTH copies (%s...); /2 artifact + model_bundle "
+         "consumed; heterogeneous per-item T proven (%d distinct T over "
+         "%d sidecar items); kappa PREFILL-WEIGHTED over the realized "
+         "pilot pass rows (%d rows / %d items, weights %d..%d — grid "
+         "passes weight the 48-item subset); TAMPERED sidecar bytes "
+         "REFUSED; SELF-CONSISTENT-but-unlicensed bundle REFUSED "
+         "(artifact-recorded sha wins); sidecar item universe == this "
+         "campaign's eval items (verify_corpus)"
+         % (ADD7_SRC_SHA256[:12], len(set(t_vals)), len(t_vals),
+            kw.get("n_pass_rows", -1), kw.get("distinct_items", -1),
+            kw.get("weight_min", -1), kw.get("weight_max", -1)),
+         shared_ok and het_ok and kw_ok and tamper_closed
+         and bundle_closed),
+        ("[REV-C R6-BOUNDARY] degradation ladder exercised AT the "
+         "reserve-inclusive boundary (planted kappa %.4f): the full "
+         "arm-set BREACHES, REPLACE-defer + d3-defer CLEARS — the SSR6 "
+         "order recovers a GREEN through the SAME add7_cap_breach "
+         "predicate phase_pilot uses" % kap_b, boundary_ok),
         ("governance: engine referred to only as 'colibri'; $0; no "
          "instance, no model download, no git, no registry write "
          "(official-seam runs are SANDBOXED repo copies — no real "
```
<!-- END-ARTIFACT D18 -->

## C7. Consolidated coordinator runbook **[SUPERSEDED by §D.8 — apply D1–D21, oracle 48/48, driver mock 27 [PASS]; this D1–D18-only sequence would land with the round-3 verdict's six defects open, and its printed 5b construction command stalls at the builder's argparse (round-3 1b)]** (supersedes §4.2, §A7, §B9)

```bash
cd /home/ec2-user/css/kernel/kernel-of-truth   # tree at/after 2574c82b (seq-3 LANDED)
M=poc/gcp/F1K-BRINGUP-GATE-FIX.md
for N in D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 D17 D18; do
  awk -v n="$N" '$0 ~ ("^<!-- BEGIN-ARTIFACT " n " ") {f=1; next} \
      $0 ~ ("^<!-- END-ARTIFACT " n " -->") {f=0} f' "$M" | sed '1d;$d' > /tmp/$N.out
done
sha256sum /tmp/D*.out    # must match the §3 + §A4 + §B8 + §C6 tables EXACTLY (18 artifacts)
cp /tmp/D1.out poc/gcp/f1k_bringup_gate.py && chmod 644 poc/gcp/f1k_bringup_gate.py
for DN in D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 D17 D18; do git apply /tmp/$DN.out; done
bash -n poc/gcp/f1k_worker.sh
python3 -m py_compile poc/gcp/f1k_gcp.py poc/gcp/f1k_bringup_gate.py \
  poc/glm52-probe/f1k-harness/f1k_driver.py
python3 poc/gcp/f1k_gcp.py gate --selftest      # expect 37 "ok:" lines + PASS, exit 0
python3 poc/gcp/f1k_gcp.py affordability --rate 0.17394 --s-per-prefill 149.1 --replace; echo $?  # 2
python3 poc/gcp/f1k_gcp.py affordability --rate 0.17394 --s-per-prefill 149.1; echo $?            # 3
# NOTE [REV-C]: the mock outdir MUST live under the repo root (kot-log/1 containment
# refuses /tmp — the §B9 line was wrong); ~0.7 GB, delete after.
( cd poc/glm52-probe/f1k-harness && python3 f1k_driver.py --mock --outdir mock-out/revc-verify )
#   expect: MOCK VALIDATION PASS, exit 0, 25 [PASS] 0 [FAIL]
rm -rf poc/glm52-probe/f1k-harness/mock-out/revc-verify
python3 poc/gcp/f1k_gcp.py plan                 # regression: DRY-PLAN OK unchanged
# ONE plain-infra commit: this memo + the five patched files + ASM-2514 + ASM-2515 + ASM-2516
# (as amended in-memo) + ASM-2517; tools/registry/registry-check.py green (nothing frozen is
# touched; build_carriers.py is NOT in the diff set).
```

Acceptance gate: review green → extract (sha-verified, 18 artifacts) → apply D1–D18 → oracle
37/37 + the two exit-code probes + driver mock green (25 [PASS]) + `plan` green → ONE commit
(four ASM rows) → registry-check green. The tree is at seq-3-landed; if it has drifted beyond
`2574c82b`'s state on the five target files, STOP and re-baseline (§0 rule).

## C8. ASM-2517 registration text **[registers AS WRITTEN, but ONLY together with ASM-2518 (§D.9), which amends its items (1)/(3)/(6) in the same landing commit — never register 2517 without 2518]** (register-at-commit WITH ASM-2514/2515/2516; next free id
[MEASURED this pass: assumptions.jsonl tail = ASM-2513 (registered, landed); 2514/2515/2516
reserved by this memo, absent from the file; 2517 free])

```json
{"id": "ASM-2517", "tag": "STIPULATED", "load_bearing": true, "claim": "F1-K BRING-UP GATE REV-C (amends ASM-2516 items (3)/(4)/(6) in the same landing commit; closes the cross-model rereview poc/gpt56-review/f1k-gate-fix-rereview-VERDICT.md, overall REJECT, findings 1/2/6/8 CLOSED kept byte-stable): (1) CONSTRUCTION-BINDING FORK DECIDED - WRAPPER-LEVEL enforcement, the SHA-PINNED generator build_carriers.py stays byte-untouched: f1k_bringup_gate.py guard verifies the /2 GREEN artifact + byte-sha of the fetched pin + shared-model sha, builds the child env EXPLICITLY (records+overrides ambient PIN/PIN_GB; POPS STATS - one ambient path across 96 batches would hold the LAST batch only under fetch-grade truncate semantics ASM-1971 - and the mode knobs), PROBES engagement PRE-SPEND with one minimal KAE_DUMP invocation of the same engine argv/env (mode-exact; armed banner under the LANDED ASM-2513 grammar, counters coherent incl. budget==licensed PIN_GB and source==bound path; refusal = no launch, exposure ~ one engine start <$0.01), launches the builder (ambient-env passthrough verified from the pinned bytes, build_carriers.py:634, only KAE_SCORE popped), runs the FROZEN checkpoints IN-PROCESS off the builder's per-concept files and kills the process group on breach (construction-abort.json); construction evidence = construction-pin-probe.json + construction-checkpoint-<n>.json + construction-guard-final.json. HONEST RESIDUALS: no per-batch banner evidence (builder swallows engine stderr on success) and no mid-campaign re-observation - both deferred with per-batch STATS to the seq-4 generator re-freeze bead kernel-of-truth-8cpm, NOT on the critical path. (2) CAMPAIGN PIN = the LICENSED bring-up pin for the WHOLE campaign: full-corpus re-derivation at the construction->pilot boundary is WITHDRAWN as structurally impossible through the unchanged builder (one 48-row batch per concept, no per-pass STATS hook) and campaign-pin-rebind.json is REMOVED (no consumer; unreachable anyway - the driver refuses a campaign pin != the gate artifact's). Repricing honest: expected cost unchanged (SSA1 rows already price the measured f); upside of a better pin foregone; under-coverage manifests as throughput loss bounded by checkpoint aborts + the reserve-inclusive addendum-(7) gate. (3) CHECKPOINT SCHEDULE RE-FROZEN at the OBSERVABLE concept boundaries n_done {240,1056,2304} (=5/22/48 of 96 concepts x 48 passes; amends ASM-2516(4)'s {200,1024,2304}, which were not observable at the builder's per-concept granularity); OFF-SCHEDULE n_done REFUSED; --n-start (48-multiple) makes resumed-construction ratios honest; first exposure ~ 240 x 137.2 s ~ 9.1 h ~ $1.59 [EXTRAPOLATED f=1.45 row]; config-cost transfers guard-final realized figures into the landed Ledger's REQUIRED cost basis (refuses builder_exit!=0 finals and conflicting blocks). (4) GATE ARTIFACT SCHEMA kot-f1k-bringup-gate/2 with model_bundle {add7_src_sha256, tokens_full_sha256}: ONE projection-model implementation as a byte-identical KOT-ADD7-SHARED block in gate + driver (frozen ADD7_SRC_SHA256 9d3e1bc76f8506d99a29b0465af2c063b32ba8d726e7ec2c6a65e3c596260353; vendored copy + sha cross-check chosen over a cross-tree import so the pinned-analysis surface never depends on an unpinned path); project() refuses to EMIT from a drifted copy, Add7Model refuses to CONSUME unless own sha == constant == artifact value; Add7Model additionally requires verdict GREEN, config-declared sidecar sha == ARTIFACT-recorded (bytes win over self-declaration), RATE equality (exact), PIN identity (validate_pinning sha == artifact pin sha, REAL mode), and CORPUS identity in the driver-verifiable form (sidecar {pilot,main-tmpl,main-d3,guard} keys are a BIJECTION with the loaded eval items; byte identity is gate-side corpus_sha256 + landed verify_corpus_pins - the composition is disclosed); pin-fetch/checkpoint/guard/config-affordability all refuse non-/2 artifacts; config-affordability is the EXECUTABLE gate->config.affordability step (no pilot stall; idempotent; refuses conflicts; verifies sidecar bytes against the artifact). (5) KAPPA PREFILL-WEIGHTED over the REALIZED pilot pass structure: the model-predicted pilot blend is weighted by the pilot rows checkpoint (grid passes weight the 48-item subset - 9 configs x 4 members x 48 + dev-96 passes; [MEASURED mock] 2112 rows/96 items, weights 4..40), recorded as projection_rev_b.kappa_weighting - supersedes the REV-B unweighted 96-item mean. (6) MOCK/ORACLE hardening: heterogeneous per-item T fixtures (40 distinct T), tampered-sidecar refusal, SELF-CONSISTENT-but-unlicensed-bundle refusal, R6 degradation boundary exercised through the SAME module-level add7_cap_breach predicate phase_pilot uses; oracle 37/37 (new: schedule enforcement, guard end-to-end on stubs incl. refusals, config seams, shared-model identity); driver mock 25 [PASS]; mock outdir must be repo-root-contained (the SSB9 /tmp line is superseded - kot-log/1 refusal [MEASURED]). (7) FAILED-heartbeat visibility: local on-disk FAILED marker written FIRST, GCS upload retried 5x with backoff, watchdog SSH-side marker probe (inconclusive probe never tears down); residual (VM unreachable via both GCS and SSH -> max-life backstop) stated. (8) pinfile derivation digest renamed manifest_rows_sha256 + manifest_file_sha256 added (rereview finding 1 nit). Bench: 18-artifact chain applies clean on the LANDED tree (byte-identical fresh-chain reproduction, cmp x5; finals f83d30d8/468ab73d/53d21424/27e915dc/075bc0b1), oracle 37/37 on both invocation paths and both benches, driver mock exit 0 / 25 PASS / 0 FAIL, affordability probes exit 2/3, plan DRY-PLAN OK; settled D5/D6 conjunct lines and landed pin-machinery hunks byte-stable (discipline greps recorded); every REV-C change is fail-closed-only on unpinned infra files.", "rationale": "The rereview proved the REV-B composite still let construction run with ambient unverified pin state, promised a full-corpus stats/rebind/checkpoint chain the pinned builder cannot execute, and let the driver stall on or consume a self-consistent-but-unlicensed model bundle. REV-C closes the executable gap at the wrapper WITHOUT touching the frozen generator: explicit env binding, mode-exact pre-spend engagement proof, frozen observable checkpoints with kill authority, artifact-bound model-bundle consumption, and honest withdrawal (with a tracked bead) of the unimplementable re-derivation instead of relabelling it.", "backing_ref": "poc/gcp/F1K-BRINGUP-GATE-FIX.md REV-C SSC (this freeze; D14-D18 + bench evidence); poc/gpt56-review/f1k-gate-fix-rereview-VERDICT.md; build_carriers.py:634,:640-660,:852,:960 (pinned bytes: env passthrough, echo-only stderr use, per-concept batching); kae-add-path.patch:175,:180,:183 (STATS/score paths); f1k_driver.py landed 2574c82b :1927 (PIN_ARMED_RE), :1947 (check_pin_engagement), :3159/:3224/:384 (pilot pass structure); ASM-1971 (fetch-grade riders), ASM-2513 (landed pin machinery), ASM-2514/2515/2516 (as amended); bead kernel-of-truth-8cpm (deferred seq-4 generator re-freeze)", "status": "open", "owner": "designer-20", "date": "2026-07-18"}
```

## C9. REV-C self-check additions (rows 46–61; every claim → verified where → tag)

| # | Claim | Verified where (this REV-C pass) | Tag |
|---|---|---|---|
| 46 | Rereview verdict read verbatim; all STILL-OPEN findings mapped (C0); CLOSED findings' artifact blocks + settled lines byte-stable | verdict full read; discipline greps on D14–D18 | [MEASURED memo/diff state] |
| 47 | Fork basis: builder env passthrough `env = dict(os.environ)` at :634 with ONLY `KAE_SCORE` popped (no other env mutation in the file); engine stderr consumed for the KAE echo only (:640-660); ONE 48-row batch per concept, serial, checkpointed per concept (:852-:960); `STATS`/`SCORE`/`KAE_SCORE` interface from kae-add-path.patch:175/:180/:183 | pinned `build_carriers.py` + patch bytes read this pass | [MEASURED] |
| 48 | Shared-model identity: both KOT-ADD7-SHARED blocks hash to `9d3e1bc76f85…` == the frozen constant; oracle case 18 + driver-mock cross-file check green | block-sha computation + selftest/mock runs this pass | [MEASURED] |
| 49 | D14–D18 shas as tabled; full D1→D18 chain applies clean on the CURRENT landed bytes; fresh-chain reproduction byte-identical (`cmp` ×5); finals f83d30d8/468ab73d/53d21424/27e915dc/075bc0b1 | two independent /tmp benches this pass | [MEASURED] |
| 50 | Oracle 37/37 (both `gate --selftest` and direct invocation, edited bench AND fresh-chain tree); exit 0; 0 FAIL | bench runs this pass | [MEASURED] |
| 51 | Driver $0 --mock: exit 0, 25 [PASS], 0 [FAIL], MOCK VALIDATION PASS; kappa_weighting {2112 rows, 96 items, weights 4..40}; 40 distinct sidecar T; tamper + self-consistent-bundle + R6-boundary probes green | mock run + artifact reads this pass | [MEASURED] |
| 52 | Probes on the applied tree: affordability --replace exit 2 / clean exit 3; `plan` DRY-PLAN OK (control-box env stubbed) | bench runs this pass | [MEASURED] |
| 53 | Checkpoint arithmetic: {240,1056,2304} = {5,22,48}×48-pass concepts of 96; exposures 240/1056/2304 × 137.2 s × $0.17394/h ≈ $1.59/$7.00/$15.27 | arithmetic on the f=1.45 row | [EXTRAPOLATED] |
| 54 | Discipline: 0 REMOVED lines touch settled license conjuncts (D14); 0 REMOVED lines carry landed pin-machinery tokens (D18); 1 ADDED `validate_pinning` call site (Add7Model pin identity — disclosed); no PINS/FROZEN_SHA256 edits; `build_carriers.py` untouched | grep on the extracted diffs this pass | [MEASURED] |
| 55 | Schema /2 consumers enumerated (driver, pin-fetch, checkpoint, guard, config-affordability); stale `/1` strings rewritten (worker :37 comment, gcp :421/:462 docstrings) | applied-tree greps this pass | [MEASURED] |
| 56 | §B9's mock `--outdir /tmp/…` is REFUSED by the landed kot-log/1 repo-root containment (`ERR_F1K_RECORD`); §C.7 uses a repo-contained outdir; mock output ≈ 0.7 GB this pass | bench refusal observed + du this pass | [MEASURED] |
| 57 | Rename: `manifest_rows_sha256` + `manifest_file_sha256`; oracle case 12 assertions unaffected (counts, not key names) | selftest run this pass | [MEASURED] |
| 58 | Deferral is TRACKED: bead `kernel-of-truth-8cpm` filed (seq-4 generator re-freeze: per-batch STATS + explicit pin args + per-batch evidence + rebind-with-consumer) | `bd` this pass | [MEASURED] |
| 59 | ASM tail: 2513 last registered; 2514/2515/2516 reserved by this memo (absent from the file); 2517 free | `registry/assumptions.jsonl` tail read this pass | [MEASURED] |
| 60 | Pilot pass structure for kappa: 9 configs × 4 members × 48-item subset (grid) + dev-96 passes — driver :384 arithmetic, :3159, :3224; realized-row weights match (40 = 36+4 for subset items, 4 otherwise) | landed driver read + mock artifact this pass | [MEASURED] |
| 61 | Memo-only pass: repo untouched except this file; tracker bead filed; NO spend/VM/git action | `git status` this pass | [MEASURED] |

## C10. Summary (REV-C, whole composite) **[historical — §D.11 is the REV-D whole-composite summary; §D amends: engine-argv ownership (probe-only binding was bypassable), terminal-abort resume authority, prior-hours cap basis, strict count-preserving bijection]**

- **Fork decided: (b) wrapper-level enforcement.** The sha-pinned builder stays byte-untouched;
  the new `guard` binds the licensed pin into the child env explicitly (never ambient), proves
  engagement BEFORE spend with a mode-exact dump-mode probe under the landed ASM-2513 grammar,
  launches the builder with that verified env (passthrough verified from the pinned bytes),
  runs the re-frozen concept-aligned checkpoints {240,1056,2304} in-process with kill
  authority, and emits a full evidence chain; `config-cost`/`config-affordability` make the
  gate→campaign-config seams executable as printed.
- **Honest withdrawals:** full-corpus re-derivation (structurally impossible through the
  pinned builder) is DEFERRED behind bead `kernel-of-truth-8cpm`; `campaign-pin-rebind.json`
  is REMOVED (no consumer, unreachable — the driver refuses any campaign pin ≠ the gate
  artifact's); residuals (no per-batch banner evidence; GCS+SSH-dead worker invisible until
  max-life) are stated, not hidden.
- **The model bundle is BOUND:** schema /2 + `model_bundle` (shared-model sha + sidecar byte
  sha); ONE byte-identical Add7 implementation in gate + driver, sha-verified at emission AND
  consumption; the driver also requires GREEN, rate equality, pin identity, and corpus
  item-universe bijection; kappa is prefill-weighted over the realized pilot pass rows; mocks
  prove heterogeneous-T projection, tamper refusal, and the R6 boundary.
- **Evidence:** 18 sha-pinned artifacts, byte-identical fresh-chain reproduction on the landed
  `2574c82b` tree; oracle 37/37; driver mock 25 [PASS]/0 FAIL; probes 2/3; plan green; settled
  REV-B surfaces byte-stable; ONE plain-infra landing commit + ASM-2514/2515/2516 (amended) +
  ASM-2517. $0 spent; nothing applied by this pass.

---

# §D — REV-D ADDENDUM: closing the round-3 six-defect remainder (delta diffs D19–D21 on top of D14–D18)

**Scope discipline [REV-D]:** the round-3 verdict (`poc/gpt56-review/f1k-gate-fix-round3-VERDICT.md`,
read verbatim this pass) is a REJECT with a **narrow, fully-prescribed remainder**. Everything it
settled is kept **byte-stable**: the guard/probe/checkpoint architecture, dump-mode match, boundary
observability (240/1056/2304 = 5/22/48 concepts), rebind removal, the Ledger mapping, shared-block
mechanics (`9d3e1bc7…` verified in BOTH copies this pass), the `/2` model_bundle binding,
`config-affordability`, kappa weighting, the failure-visibility chain, manifest naming, and all 18
prior artifact chains (re-extracted, sha-matched, re-applied clean this pass). REV-D adds ONLY the
six prescribed closures below; f1k_gcp.py and f1k_worker.sh are untouched by D19–D21 (their REV-C
finals `468ab73d`/`53d21424` are unchanged).

## D0. Round-3 finding → disposition map

| # | Round-3 defect | Disposition |
|---|---|---|
| 1a | engine-argv unity: probe ran `--engine-cmd` while the builder took its OWN `--engine-cmd` | **CLOSED, construct-don't-compare (D19, §D.1):** the guard OWNS both commands — refuses them in the builder argv (both flag forms) BEFORE any engine start, INJECTS the probed values at launch; oracle 16a (injected-tail unity) + 19a/19b (divergence refused pre-probe) |
| 1b | liftable 5b command omits the builder's mandatory `--engine-cmd`/`--tokenizer-cmd` → argparse stall | **CLOSED (D19+D21, §D.2):** with injection the printed builder argv is complete AS PRINTED; oracle 20a/20b dry-parses the REAL `build_carriers.py` argparse surface with the liftable argv shape (parses WITH the injected tail; exits at argparse WITHOUT it) |
| 1c | checkpoint STOP bypassable: re-run derives n0 from files, drops passed checkpoints | **CLOSED (D19, §D.3):** abort records the breach values and is TERMINAL; resume only via maintainer `construction-reset.json` bound BY BYTES to the abort; full schedule re-derived from the abort point, raced-past checkpoints REFUSE; oracle 21a–e |
| 1d | `--prior-usd` without prior-hours: failed-session hours vanish from the 900 h cap | **CLOSED (D19+D20, §D.4):** `config-cost --prior-hours` REQUIRED when `--prior-usd` > 0 → `cost.prior_instance_hours`, a REQUIRED Ledger key threaded into the addendum-(7) hours basis (`add7_hours_basis`); oracle 22a/b + driver-mock 900 h STOP-flip probe; frozen-analysis sidecar identity disclosed unchanged |
| 2 | "bijection" was set equality after dict collapse — conflicting duplicate `T` passes | **CLOSED (D20, §D.5):** COUNT-PRESERVING verification — ANY duplicate sidecar key refused at load; ANY duplicate eval-inventory id refused before the set comparison; driver-mock plants an attacker-consistent conflicting-`T` duplicate → refused |
| 4 | four unstruck stale lines (memo:232/242/1781/1788) contradict §C.5 | **CLOSED in place (§D.6):** all four struck/supersession-marked; fresh grep shows no unstruck operative stale text remains; §C.5's "inline kills applied" claim is TRUE again |
| 6 | regression sweep: no tests for 1a/1b/1c resume/duplicate keys | **CLOSED:** oracle 37→48 (11 new checks), driver mock 25→27 (2 new check lines) — every new case listed above, all green on the edited bench AND the fresh D1→D21 chain |

## D1. Round-3 1a — engine-argv unity: construct, don't compare (D19)

The guard now **OWNS** `--engine-cmd` and `--tokenizer-cmd` (the two builder-mandatory command
flags, `build_carriers.py:1875`):

- **Refusal (pre-spend):** immediately after builder-argv normalization — BEFORE the license
  check's probe, before ANY engine start — the guard scans the builder argv for
  `--engine-cmd`/`--tokenizer-cmd` (space form AND `=` form) and dies `ERR_F1K_GUARD` on any hit.
  Construct-don't-compare was chosen over parse-and-compare deliberately: comparing would have to
  re-implement argparse's last-wins/`=`-form semantics on the refusal path; injection makes
  divergence **unrepresentable** rather than detected.
- **Injection (launch):** `builder_argv = <operator builder argv> + ["--engine-cmd",
  <probed value>, "--tokenizer-cmd", <guard value>]` — the builder's argparse receives exactly
  the argv the probe verified. Both values are validated as JSON lists before use (fail-closed).
- **Evidence:** `construction-guard-final.json` records the launched `builder_argv` verbatim plus
  an `engine_argv_unity` rule string; the probe evidence already records `engine_argv`.
- **Oracle [MEASURED, cases 16a/19a/19b]:** 16a now asserts the guard-final `builder_argv` tail
  equals the injected pair; 19a plants a divergent builder `--engine-cmd '["engine-B"]'` → refused
  with NO `construction-pin-probe.json` written (no engine start); 19b proves the
  `--tokenizer-cmd=…` form is caught identically.

## D2. Round-3 1b — the liftable construction command parses AS PRINTED (D19 + D21)

- **Runbook (D21):** step 5b's guard line gains `--tokenizer-cmd '<json argv>'`; the builder
  segment after `--` DELIBERATELY carries no engine/tokenizer flags — consistent with §D.1, the
  guard injects them, and the README states this in bold (supplying them there is refused). The
  pre-REV-D 5b command is exactly the argparse stall the verdict proved; it cannot be lifted from
  §C.7 any more (superseded header).
- **Oracle [MEASURED, cases 20a/20b]:** case 20 loads the PINNED `build_carriers.py` bytes
  in-memory (`importlib`, `cmd_construct` stubbed IN MEMORY — the sha-pinned file is untouched;
  `main()` is `__main__`-guarded so loading executes defs only) and calls its REAL `main()`:
  20a: the runbook-shaped builder argv + the guard-injected tail **parses** — and the injected
  values land in the builder's own argparse namespace (`ns.engine_cmd == '["e"]'`), proving unity
  through the production parse surface, not a mock of it; 20b: the SAME argv WITHOUT the injected
  tail exits at argparse — the stalling command class is now a failing oracle case and can never
  ship again.

## D3. Round-3 1c — a checkpoint STOP is TERMINAL until a maintainer resets (D19)

- **The abort artifact** (`construction-abort.json`, written on the kill path) now records the
  decision basis: `breaches` + `reprojection` + `realized_over_predicted` (read back from the
  checkpoint artifact `checkpoint_eval` wrote before dying), plus an explicit terminal-rule
  string.
- **Refusal:** `cmd_guard` refuses to start while `construction-abort.json` exists in the rundir
  — the n0-from-files resume that round-3 proved bypassable now never begins. The refusal message
  NAMES the recovery (mirroring the landed missing-ledger recovery pattern, ASM-2513 v3
  re-review #3: refuse + name the maintainer-authorized path, never resume implicitly).
- **The reset artifact, defined exactly:** `construction-reset.json` in the same rundir with
  `schema` = `kot-f1k-bringup-gate/2:construction-reset`, non-empty `authorized_by`,
  `decision` = `"resume-construction"`, and `abort_sha256` = sha256 of the abort file BYTES. The
  byte binding makes every reset single-abort: a stale reset can never authorize a future STOP.
- **Authorized resume:** the remaining schedule is re-derived FROM THE ABORT POINT — pending =
  every frozen checkpoint > n0 with the invariant that nothing in (abort_at, n0] exists; if the
  cached concept files raced past a frozen checkpoint (kill latency), the guard REFUSES (no
  honest fresh timing exists for it) instead of silently dropping it. Only after ALL resume
  validations pass is the abort archived (`construction-abort.consumed-<n>.json`) — a REFUSED
  resume leaves it in place, terminal as ever. A preemption resume WITHOUT a prior STOP (no abort
  file) is unchanged — stop authority, not resume capability, is what round-3 required.
- **Oracle [MEASURED, cases 21a–e]:** 21a: strangled caps produce a REAL in-guard STOP whose
  abort carries the breach values; 21b: re-run with a healthy gate → refused; 21c: reset with a
  foreign `abort_sha256` → refused; 21d: authorized resume from abort@240 with 5 cached concepts
  → `checkpoints_run == [1056, 2304]` (full schedule, none dropped), `resumed_from_abort: 240`,
  abort archived; 21e: 23 cached concepts (1104 > 1056) → refused WITH the abort left in place.

## D4. Round-3 1d — realized-hours accounting (D19 gate-side + D20 driver-side)

- **Gate:** `config-cost --prior-hours` — REQUIRED whenever `--prior-usd` > 0 (refused
  otherwise), `>= 0`, written as `cost.prior_instance_hours`. The failed-session refusal text now
  says wasted spend goes into `--prior-usd` WITH its hours in `--prior-hours`.
- **Driver:** `prior_instance_hours` is the FOURTH REQUIRED `Ledger.COST_KEYS` entry (missing →
  `ERR_F1K_COST` at init; the changed-basis resume refusal covers it automatically), and the
  addendum-(7) hours basis is now the module-level `add7_hours_basis(led_d, pilot_s)` = prior +
  construction + realized pilot — used by `phase_pilot` and exercised by the $0 mock (same
  precedent as `add7_cap_breach`). `addendum-7-affordability.json` records the value.
- **Honest scope [DISCLOSED]:** the SIDECAR surface is UNCHANGED. The FROZEN pinned analysis
  (`analysis/f1k.py` `126129b9`) enforces the registered identity `cost.instance_hours ==
  construction_instance_hours + sum(phase_seconds)/3600` (HOURS_TOL) and a CLOSED cost-object
  schema — prior hours therefore enter the PRE-SPEND projection cap basis only
  (cap-conservative: they can only turn a GO into a STOP), never the frozen ledger identity.
  Re-registering the identity itself would be an analysis re-freeze, out of this landing's scope;
  the driver-mock's analysis pass re-validates the unchanged identity end-to-end [MEASURED].
- **Oracle/mock [MEASURED]:** oracle 22a (prior USD without hours → refused) / 22b (hours
  threaded into the block; case 17 extended likewise); driver-mock `[REV-D 1d]` line: missing
  key fail-closed at Ledger init, and 380 prior hours ALONE flip the reserve-inclusive 900 h cap
  through the SAME `add7_hours_basis`/`add7_cap_breach` pair `phase_pilot` uses (901.2 h
  breaches, 521.2 h clears — the prescribed prior-hours-push-over-900h STOP), with
  `prior_instance_hours` recorded in addendum-7. The mock's cost fixture carries
  `prior_instance_hours: 0.0` — the REAL registered corner figure, not an invention: the
  ASM-2374 corner's $146 `usd_spent_prior` is the priced 521.2 h × $0.28 construction time, with
  no failed-session/pre-construction hours in the registered planning corner ([R6-4] precedent
  disclosed in-code).

## D5. Round-3 2 — strict corpus bijection, count-preserving (D20)

- **Sidecar rows:** `Add7Model.__init__` detects duplicates WHILE building the key→T dict; ANY
  duplicate key → `ERR_F1K_AFFORD` (the licensed sidecar is duplicate-free by construction, so
  a duplicate is always evidence of tampering or generation error — conflicting or not, refuse).
- **Eval inventory:** `verify_corpus` builds the wanted keys as a LIST, refuses any duplicate id
  BEFORE the set comparison. With both sides proven duplicate-free, the retained set equality is
  now a true bijection.
- **Mock [MEASURED, `[REV-D 2]` line]:** a planted duplicate `main-tmpl:it-000-00` row with
  conflicting `T` (+7), re-pinned ATTACKER-CONSISTENT through the whole bundle (config sidecar
  sha, artifact `model_bundle.tokens_full_sha256`, artifact sha all agree on the duplicated
  bytes — so only the count-preserving load can catch it; the old set-equality check passed it)
  → refused; a duplicated eval item id → refused.
- **Inline kill (defect-4 class, disclosed):** the live driver's `projection_rev_b.model` label
  string said `kot-f1k-bringup-gate/1` while consuming `/2` — rewritten to `/2` in D20 (label
  only; no consumer parses it [MEASURED: mock green before/after]).

## D6. Round-3 4 — stale supersession text killed; §C.5 re-verified TRUE

In-place kills this pass (title/§0 header updated to REV-D as well):

- **memo:232 (§2.6 CANNOT-bound (ii)):** "the campaign pin is re-derived on the real
  construction corpus" — STRUCK, superseded bracket added (licensed bring-up pin runs the whole
  campaign; re-derivation withdrawn/deferred, bead `kernel-of-truth-8cpm`).
- **memo:242 (§2.7 heading):** schema `/1` — STRUCK, superseded to `/2` + `model_bundle` (D14).
- **memo:1781 (§B-era mitigation text):** "200/1024/2304 … ≈ $1.3" — STRUCK, superseded bracket
  (observable schedule 240/1056/2304, guard-run in-process, ≈ $1.59).
- **memo:1788 (item 4, pin replacement before pilot):** whole item STRUCK + WITHDRAWN bracket
  (structurally impossible through the pinned builder; NO pin replacement before pilot; driver
  refuses a campaign pin ≠ the gate artifact's; deferred behind the bead).

**Fresh grep [MEASURED this pass]** for the stale phrasings (`200/1024`, `$1.3`, "re-derived on
the … construction corpus", "MAY replace the bring-up pin", `kot-f1k-bringup-gate/1`): every
remaining occurrence is (a) inside a byte-pinned HISTORICAL artifact block (D1/D9–D13 quoted
diffs — changing them would break the sha chain), (b) inside an already-`[AMENDED in REV-C]`- or
`~~…~~`-marked passage (§B.3(6) at memo:2584 carries its REV-C amendment bracket immediately
below), or (c) inside an ASM registration text explicitly amended by a later ASM in the same
landing (2514/2516 → 2517/2518 chain). No unstruck operative-looking stale text remains; §C.5's
"inline kills applied" claim is TRUE at REV-D state.
**[AMENDED in REV-E — round-4 verdict 6 proved this fresh-grep claim FALSE: it missed §A0's F5 row (memo:1707), §B.7's "stands" row (memo:2718), the driver's two re-derivation statements (repo `f1k_driver.py:755`/`:3663` — D-chain-produced text this grep never covered), and (self-found this pass) the gate collect `pin.role` string carrying the same withdrawn re-derivation/rebind language. All five sites are killed at REV-E (memo rows struck/amended in place; driver via D23; gate via D22), and the grep is RE-RUN over the memo AND all five D-chain-produced files — §E.4 carries the re-run and its residual classification.]**
## D7. Delta artifacts D19–D21 (apply AFTER D18, in order; sha-pinned; bench-verified on the LANDED tree)

| # | Target | Kind | sha256 of the artifact below |
|---|---|---|---|
| D19 | `poc/gcp/f1k_bringup_gate.py` (post-D14) | unified diff | `b8b17da6d5ab5b766a42758a9df935b3438768df2b756cba2a429edc900ea1a9` |
| D20 | `poc/glm52-probe/f1k-harness/f1k_driver.py` (post-D18) | unified diff | `7ff12e7e916e25aeb47643e4d9c75f143b3acccab40c24d2638fc1094390a391` |
| D21 | `poc/gcp/README.md` (post-D17) | unified diff | `0e9b475a9a83f71c54cdc945c833751e211682169ee11049cdf5aa81f0a50126` |

Bench evidence [MEASURED, /tmp bench this REV-D pass — no repo file touched beyond this memo]:

- **Chains:** D1–D18 re-extracted (all 18 shas match the §3/§A4/§B8/§C6 tables) and re-applied
  clean on the CURRENT landed bytes (`2574c82b`; the five target files verified unmodified vs
  HEAD first), reproducing the §C6 finals (`f83d30d8`/`468ab73d`/`53d21424`/`27e915dc`/
  `075bc0b1` — re-verified). D19–D21 then apply clean; a SECOND fresh copy taken through the
  full D1→D21 chain is **byte-identical** to the edited bench on all five files (`cmp` ×5).
  Applied-tree result shas: `f1k_bringup_gate.py 90c38c6ed612f2b6…`,
  `f1k_gcp.py 468ab73d078eaaf5…` (UNCHANGED from REV-C), `f1k_worker.sh 53d21424b1d35016…`
  (UNCHANGED), `README.md aee6e716721c191f…`, `f1k_driver.py 0427d5fdce035094…`.
- `py_compile` (gate, gcp, driver) + `bash -n` (worker) clean on the applied tree.
- **$0 oracle 48/48** (`f1k_gcp.py gate --selftest` AND direct `selftest`, on the edited
  bench AND the fresh-chain tree; exit 0, 0 FAIL) — 37 REV-C checks (16a extended with the
  injected-argv unity conjunct; 17 extended with `prior_instance_hours`) + 11 REV-D checks:
  19a/19b (divergence refused pre-engine-start, both flag forms), 20a/20b (REAL builder-argparse
  dry parse: liftable+injected argv parses, uninjected argv stalls), 21a–e (terminal
  STOP → abort-with-breach-values → refuse → bound-reset validation → full-schedule resume →
  raced-past refusal), 22a/22b (prior-hours refusal + threading).
- **Driver $0 --mock green** on the applied tree: exit 0, **27 [PASS]** (25 REV-B/C checks + 2
  REV-D check lines), 0 [FAIL], `MOCK VALIDATION PASS`; the `[REV-D 2]` and `[REV-D 1d]`
  probes print their EXPECTED `ERR_F1K_AFFORD`/`ERR_F1K_COST` refusals; the mock's own
  end-to-end campaign (pilot → guard → test → sidecar → PINNED analysis) stays green with the
  new REQUIRED cost key — the frozen-analysis identity is re-validated by the analysis pass
  itself. Output ≈ 0.7 GB this pass — deleted after (repo-root-contained outdir per §C.6).
- Probes: `affordability --rate 0.17394 --s-per-prefill 149.1 --replace` → exit 2; without
  `--replace` → exit 3; `plan` → `DRY-PLAN OK` (env-stubbed control-box vars) — all on the
  applied tree.
- Discipline greps [MEASURED]: 0 `PINS`/`FROZEN_SHA256` edits in D19–D21; 0 touches inside
  either `KOT-ADD7-SHARED` block (both blocks still hash `9d3e1bc76f8506d9…` == the frozen
  constant on the applied tree); exactly ONE removed line carries a pin-machinery token — the
  case-16a selftest label re-added extended in the same hunk (disclosed above); settled D5/D6
  conjunct lines and landed pin-machinery hunks byte-stable (`f1k_gcp.py`/`f1k_worker.sh`
  final shas unchanged is the whole-file proof); `build_carriers.py` byte-identical to the
  repo (`a92be3e4…`, sha-compared) — NOT in the diff set; neither touched file is sha-pinned →
  the landing stays plain infra.

### D7.1 D19 — `poc/gcp/f1k_bringup_gate.py` REV-D delta (engine-argv unity + terminal-abort/reset + prior-hours + oracle 48)

<!-- BEGIN-ARTIFACT D19 f1k_bringup_gate.py.rev-d.diff sha256=b8b17da6d5ab5b766a42758a9df935b3438768df2b756cba2a429edc900ea1a9 -->
```diff
diff --git a/poc/gcp/f1k_bringup_gate.py b/poc/gcp/f1k_bringup_gate.py
--- a/poc/gcp/f1k_bringup_gate.py
+++ b/poc/gcp/f1k_bringup_gate.py
@@ -1206,14 +1206,17 @@
 
 
 def cmd_guard(args):
-    """[REV-C F3] construction-guard: verify license -> bind pin env
-    explicitly -> PROBE engagement -> launch the UNTOUCHED sha-pinned
-    builder with the verified env -> run the FROZEN checkpoints
-    in-process off the builder's per-concept files -> kill on breach.
+    """[REV-C F3 / REV-D] construction-guard: verify license -> refuse a
+    terminal abort without a maintainer reset -> bind pin env explicitly
+    -> PROBE engagement -> launch the UNTOUCHED sha-pinned builder with
+    the verified env AND the guard-injected engine/tokenizer argv -> run
+    the FROZEN checkpoints in-process off the builder's per-concept
+    files -> kill on breach.
     usage: ... guard --gate bringup-gate.json --pin campaign-pin.stats
-      --engine-cmd '<json argv>' --layers 3,...,77 --tokens
-      tokens-full.jsonl --rundir <dir> --workdir <builder workdir>
-      [--poll-seconds N] -- <builder argv...>"""
+      --engine-cmd '<json argv>' --tokenizer-cmd '<json argv>'
+      --layers 3,...,77 --tokens tokens-full.jsonl --rundir <dir>
+      --workdir <builder workdir> [--poll-seconds N] -- <builder argv
+      WITHOUT --engine-cmd/--tokenizer-cmd: the guard injects them>"""
     import signal
     import time
     art = json.loads(Path(args.gate).read_text(encoding="utf-8"))
@@ -1224,6 +1227,32 @@
         args.builder = args.builder[1:]
     if not args.builder:
         die("F1K_GUARD", "no builder argv after '--'")
+    # [REV-D 1a] ENGINE-ARGV UNITY — construct, don't compare: the guard
+    # OWNS the engine/tokenizer commands. It PROBES args.engine_cmd and
+    # INJECTS the SAME verified values into the builder argv itself
+    # (below), so the attested engine and the constructing engine cannot
+    # diverge (round-3 verdict 1a: engine A could pass the probe while
+    # an operator-supplied builder --engine-cmd ran engine B). Any
+    # operator-supplied value in the builder argv is REFUSED — BEFORE
+    # any engine start.
+    for tok in args.builder:
+        if tok in ("--engine-cmd", "--tokenizer-cmd") \
+                or tok.startswith("--engine-cmd=") \
+                or tok.startswith("--tokenizer-cmd="):
+            die("F1K_GUARD", "builder argv carries %r — the guard OWNS "
+                "the engine/tokenizer commands (construct-don't-compare "
+                "[REV-D]): remove it from the builder argv; the guard "
+                "injects the PROBED --engine-cmd/--tokenizer-cmd itself"
+                % tok)
+    for flag, val in (("--engine-cmd", args.engine_cmd),
+                      ("--tokenizer-cmd", args.tokenizer_cmd)):
+        try:
+            if not isinstance(json.loads(val), list):
+                raise ValueError("not a JSON list")
+        except ValueError as e:
+            die("F1K_GUARD", "guard %s %r is not a JSON argv list (%s) — "
+                "the builder requires the same shape (build_carriers.py "
+                "construct)" % (flag, val, e))
     env = dict(os.environ)
     overridden = {k: env[k] for k in ("PIN", "PIN_GB", "STATS")
                   if k in env}
@@ -1238,6 +1267,52 @@
     env["PIN_GB"] = ("%g" % pin_gb)
     rundir = Path(args.rundir)
     rundir.mkdir(parents=True, exist_ok=True)
+    # [REV-D 1c] TERMINAL-STOP AUTHORITY: a checkpoint STOP leaves
+    # construction-abort.json (breach values recorded) plus the builder's
+    # concept files; deriving n0 from the files and relaunching would
+    # silently drop the passed checkpoints — stop authority bypassed by
+    # re-running. The guard REFUSES to start while the abort artifact
+    # exists, unless a maintainer-authorized construction-reset.json is
+    # present (mirrors the landed missing-ledger recovery [ASM-2513 v3
+    # re-review #3]: refuse with the recovery path NAMED; resume only on
+    # a deliberate, byte-bound maintainer act).
+    abort_p = rundir / "construction-abort.json"
+    reset_p = rundir / "construction-reset.json"
+    abort_at = None
+    if abort_p.exists():
+        ab = json.loads(abort_p.read_text(encoding="utf-8"))
+        if not reset_p.exists():
+            die("F1K_GUARD", "construction-abort.json exists (checkpoint "
+                "STOP at n_done=%r; breaches: %s) — a checkpoint STOP is "
+                "TERMINAL for this rundir. RECOVERY: a maintainer reviews "
+                "the recorded breach values and writes construction-"
+                "reset.json {schema: %r, authorized_by: <name>, decision: "
+                "'resume-construction', abort_sha256: sha256 of the abort "
+                "file bytes}; re-running without it never bypasses stop "
+                "authority [REV-D]"
+                % (ab.get("at_checkpoint"),
+                   "; ".join(ab.get("breaches") or [])
+                   or "(recorded in the abort file)",
+                   SCHEMA + ":construction-reset"))
+        rst = json.loads(reset_p.read_text(encoding="utf-8"))
+        bad = []
+        if rst.get("schema") != SCHEMA + ":construction-reset":
+            bad.append("schema %r" % rst.get("schema"))
+        if not (rst.get("authorized_by") or "").strip():
+            bad.append("authorized_by empty")
+        if rst.get("decision") != "resume-construction":
+            bad.append("decision %r" % rst.get("decision"))
+        if rst.get("abort_sha256") != sha256_file(abort_p):
+            bad.append("abort_sha256 != the abort file bytes (a reset "
+                       "authorizes exactly ONE reviewed abort)")
+        if bad:
+            die("F1K_GUARD", "construction-reset.json present but NOT "
+                "authorizing (%s) — the reset binds BY BYTES to the abort "
+                "it overrules [REV-D]" % "; ".join(bad))
+        abort_at = int(ab["at_checkpoint"])
+        #   the abort is archived ONLY after every resume validation
+        #   below passes (incl. the raced-past-checkpoint check) — a
+        #   REFUSED resume leaves the abort in place, terminal as ever.
     probe = _probe_engagement(json.loads(args.engine_cmd), env,
                               args.layers, rundir)
     workdir = Path(args.workdir)
@@ -1247,10 +1322,35 @@
 
     n0 = concepts_done() * 48
     pending = [p for p in CHECKPOINT_SCHEDULE if p > n0]
+    if abort_at is not None:
+        # [REV-D 1c] authorized resume: the remaining schedule is
+        # re-derived FROM THE ABORT POINT — every frozen checkpoint past
+        # the abort must still run. If the cached concept files raced
+        # past one (kill latency can leave files beyond the breach
+        # boundary), no honest fresh timing exists for it: REFUSE rather
+        # than silently drop it.
+        dropped = [p for p in CHECKPOINT_SCHEDULE if abort_at < p <= n0]
+        if dropped:
+            die("F1K_GUARD", "authorized resume from the abort at "
+                "n_done=%d, but the cached concept files already cover "
+                "n_done=%d — frozen checkpoint(s) %s would be silently "
+                "dropped; maintainer surface (inspect/trim the workdir "
+                "deliberately, then re-authorize) [REV-D]"
+                % (abort_at, n0, dropped))
+        os.replace(abort_p, rundir
+                   / ("construction-abort.consumed-%d.json" % abort_at))
+        #   single-use, archived only NOW (all resume validations
+        #   passed): the consumed reset stays bound (abort_sha256) to
+        #   THIS archived abort; any future STOP writes a fresh abort
+        #   the old reset can never authorize.
     if not pending:
         print("guard: resume past the last frozen checkpoint (n0=%d) — "
               "no checkpoints remain; earlier sessions ran them" % n0)
-    proc = subprocess.Popen(args.builder, env=env, start_new_session=True)
+    # [REV-D 1a] the builder runs the SAME engine/tokenizer argv the
+    # probe verified — injected here, never operator-supplied.
+    builder_argv = args.builder + ["--engine-cmd", args.engine_cmd,
+                                   "--tokenizer-cmd", args.tokenizer_cmd]
+    proc = subprocess.Popen(builder_argv, env=env, start_new_session=True)
     t0 = time.monotonic()
 
     def run_ckpt(p):
@@ -1270,10 +1370,30 @@
                         os.killpg(proc.pid, signal.SIGKILL)
                 except ProcessLookupError:
                     pass
+            # [REV-D 1c] the abort records the BREACH VALUES for the
+            # maintainer's resume decision (read back from the checkpoint
+            # artifact checkpoint_eval just wrote), and is TERMINAL: the
+            # next guard invocation refuses to start while it exists.
+            try:
+                ck = json.loads(
+                    (rundir / ("construction-checkpoint-%d.json" % p))
+                    .read_text(encoding="utf-8"))
+            except (OSError, json.JSONDecodeError):
+                ck = {}
             (rundir / "construction-abort.json").write_text(json.dumps(
                 {"schema": SCHEMA + ":construction-abort",
                  "at_checkpoint": p, "n_start": n0,
-                 "elapsed_s": round(time.monotonic() - t0, 1)}, indent=2))
+                 "elapsed_s": round(time.monotonic() - t0, 1),
+                 "breaches": ck.get("breaches"),
+                 "reprojection": ck.get("reprojection"),
+                 "realized_over_predicted":
+                     ck.get("realized_over_predicted"),
+                 "rule": "TERMINAL for this rundir [REV-D]: the next "
+                         "guard invocation REFUSES to start while this "
+                         "file exists, unless a maintainer-authorized "
+                         "construction-reset.json (schema %s, bound to "
+                         "these bytes by abort_sha256) is present"
+                         % (SCHEMA + ":construction-reset")}, indent=2))
             raise
 
     ran = []
@@ -1296,6 +1416,11 @@
              "builder_exit": rc, "pin_file_sha256": pin_sha,
              "pin_gb": pin_gb, "ambient_overridden": overridden,
              "probe": "construction-pin-probe.json",
+             "builder_argv": builder_argv,
+             "engine_argv_unity": "guard-injected --engine-cmd/"
+                                  "--tokenizer-cmd == the probed argv "
+                                  "(construct-don't-compare [REV-D])",
+             "resumed_from_abort": abort_at,
              "checkpoints_run": ran, "n_start_passes": n0,
              "n_final_passes": final_avail,
              "elapsed_s": round(elapsed, 1),
@@ -1373,11 +1498,16 @@
 
 
 def cmd_config_cost(args):
-    """[REV-C F3] transfer the guard's realized construction figures into
-    the campaign config's REQUIRED cost basis (the landed Ledger fails
-    closed without cost.{usd_spent_prior, construction_instance_hours} —
-    ASM-2513). --final may repeat for resumed constructions (sessions
-    sum); --prior-usd is the metered PRE-construction spend."""
+    """[REV-C F3 / REV-D 1d] transfer the guard's realized construction
+    figures into the campaign config's REQUIRED cost basis (the landed
+    Ledger fails closed without cost.{usd_spent_prior, prior_instance_
+    hours, construction_instance_hours} — ASM-2513/REV-D). --final may
+    repeat for resumed constructions (sessions sum); --prior-usd is the
+    metered PRE-construction spend PLUS any failed-session spend;
+    --prior-hours is the instance-hours behind that spend and is
+    REQUIRED whenever --prior-usd > 0 — hours must never vanish from
+    the 900 h basis while their dollars are counted (round-3 verdict
+    1d)."""
     hours = usd = 0.0
     for fp in args.final:
         fin = json.loads(Path(fp).read_text(encoding="utf-8"))
@@ -1389,11 +1519,22 @@
                 "construction session never becomes a cost basis; "
                 "resume it (its successor final subsumes the elapsed "
                 "time it re-does, and its wasted spend goes into "
-                "--prior-usd deliberately)" % (fp, fin.get("builder_exit")))
+                "--prior-usd deliberately, WITH its hours in "
+                "--prior-hours [REV-D])" % (fp, fin.get("builder_exit")))
         hours += float(fin["realized"]["instance_hours"])
         usd += float(fin["realized"]["usd"])
+    pu = float(args.prior_usd)
+    ph = None if args.prior_hours is None else float(args.prior_hours)
+    if pu > 0 and ph is None:
+        die("F1K_CONFIG", "--prior-usd %.4f > 0 REQUIRES --prior-hours "
+            "(the instance-hours behind that spend: failed construction "
+            "sessions + metered pre-construction) — realized hours never "
+            "vanish from the cap basis [REV-D 1d]" % pu)
+    if ph is not None and ph < 0:
+        die("F1K_CONFIG", "--prior-hours must be >= 0 (got %r)" % ph)
     block = {"spot_rate_usd_per_hour": float(args.rate),
-             "usd_spent_prior": round(float(args.prior_usd) + usd, 4),
+             "usd_spent_prior": round(pu + usd, 4),
+             "prior_instance_hours": round(ph or 0.0, 4),
              "construction_instance_hours": round(hours, 4)}
     _merge_config_block(args.config, "cost", block)
     return 0
@@ -1846,6 +1987,7 @@
         ns16 = argparse.Namespace(
             gate=str(td / "gate-art16.json"), pin=str(pin16),
             engine_cmd=json.dumps([sys.executable, str(eng16)]),
+            tokenizer_cmd=json.dumps([sys.executable, "-c", "pass"]),
             layers="3,5", tokens=str(td / "tok" / "tokens-full.jsonl"),
             rundir=str(rd16), workdir=str(wd16), poll_seconds="0.05",
             builder=["--", sys.executable, str(bld16), str(wd16)])
@@ -1858,10 +2000,14 @@
                       .is_file() for p in (240, 1056, 2304))
               and fin16["builder_exit"] == 0
               and fin16["checkpoints_run"] == [240, 1056, 2304]
-              and fin16["pin_file_sha256"] == sha256_file(pin16),
+              and fin16["pin_file_sha256"] == sha256_file(pin16)
+              and fin16["builder_argv"][-4:]
+              == ["--engine-cmd", ns16.engine_cmd,
+                  "--tokenizer-cmd", ns16.tokenizer_cmd],
               "case 16a GUARD end-to-end: probe evidence + all frozen "
               "checkpoints + guard-final (builder untouched, env-bound "
-              "pin)")
+              "pin, PROBED engine/tokenizer argv INJECTED into the "
+              "builder argv — unity by construction [REV-D])")
         pin16b = td / "pin16b.stats"
         pin16b.write_text("3 0 999\n")
         try:
@@ -1930,14 +2076,17 @@
                         "ARTIFACT-recorded sha refused")
         cmd_config_cost(argparse.Namespace(
             final=[str(rd16 / "construction-guard-final.json")],
-            prior_usd="3.1", rate="0.174", config=str(cfg17)))
+            prior_usd="3.1", prior_hours="17.8", rate="0.174",
+            config=str(cfg17)))
         cost17 = json.loads(cfg17.read_text())["cost"]
         check(abs(cost17["usd_spent_prior"]
                   - (3.1 + fin16["realized"]["usd"])) < 1e-6
+              and cost17["prior_instance_hours"] == 17.8
               and abs(cost17["construction_instance_hours"]
                       - fin16["realized"]["instance_hours"]) < 1e-9,
-              "case 17 config-cost: guard-final realized figures become "
-              "the REQUIRED Ledger basis (never silent zeros)")
+              "case 17 config-cost: guard-final realized figures + the "
+              "prior hours become the REQUIRED Ledger basis (never "
+              "silent zeros) [REV-D]")
         # case 18 [REV-C F5i]: ONE projection model, mechanically — the
         # gate copy hashes to the frozen constant AND byte-matches the
         # driver's vendored copy.
@@ -1948,23 +2097,249 @@
               and add7_block_sha256(drvp) == own18,
               "case 18 SHARED MODEL: gate block sha == frozen "
               "ADD7_SRC_SHA256 == driver block sha (drift refuses)")
+        # case 19 [REV-D 1a]: ENGINE-ARGV UNITY — an operator-supplied
+        # --engine-cmd/--tokenizer-cmd in the builder argv (either flag
+        # form) is REFUSED BEFORE any engine start (no probe evidence is
+        # ever written).
+        rd19 = td / "rd19"
+        try:
+            cmd_guard(argparse.Namespace(**{
+                **vars(ns16), "rundir": str(rd19), "workdir": str(wd16),
+                "builder": ["--", sys.executable, str(bld16), str(wd16),
+                            "--engine-cmd", '["engine-B"]']}))
+            check(False, "case 19 must refuse a divergent builder "
+                         "--engine-cmd")
+        except SystemExit:
+            check(not (rd19 / "construction-pin-probe.json").exists(),
+                  "case 19a DIVERGENCE REFUSED: builder-argv --engine-cmd "
+                  "(engine B vs probed engine A) dies BEFORE any engine "
+                  "start — no probe ran, no evidence written")
+        try:
+            cmd_guard(argparse.Namespace(**{
+                **vars(ns16), "rundir": str(rd19), "workdir": str(wd16),
+                "builder": ["--", sys.executable, str(bld16), str(wd16),
+                            '--tokenizer-cmd=["tok-B"]']}))
+            check(False, "case 19 must refuse the = flag form too")
+        except SystemExit:
+            check(True, "case 19b DIVERGENCE REFUSED: the "
+                        "--tokenizer-cmd=... form is caught the same way "
+                        "(the guard OWNS both commands)")
+        # case 20 [REV-D 1b]: LIFTABLE-COMMAND COMPLETENESS — the REAL
+        # builder argparse surface (pinned build_carriers.py, loaded
+        # in-memory with cmd_construct stubbed: a $0 dry parse, bytes
+        # untouched) accepts the runbook 5b builder argv + the
+        # guard-injected engine/tokenizer flags, and REFUSES the same
+        # argv WITHOUT them — the exact argparse stall the round-3
+        # verdict proved the printed command would hit.
+        import importlib.util
+        bcp = Path(__file__).resolve().parents[1] / "glm52-probe" \
+            / "f1k-harness" / "build_carriers.py"
+        spec20 = importlib.util.spec_from_file_location(
+            "kot_f1k_bc_dryparse", str(bcp))
+        bc20 = importlib.util.module_from_spec(spec20)
+        spec20.loader.exec_module(bc20)
+        #   (build_carriers manages its own sys.path for its pinned
+        #   sibling imports — loading it executes defs only; main() is
+        #   __main__-guarded, and cmd_construct is stubbed IN MEMORY
+        #   below, the pinned bytes stay untouched)
+        bc20.cmd_construct = lambda a: ("PARSED", a)   # in-memory stub
+        lift20 = ["construct", "--mode", "real", "--layers", "3,5",
+                  "--tokenizer-sha", "0" * 64,
+                  "--tokenizer-artifact", "tok.bin",
+                  "--engine-weights-sha", "0" * 64,
+                  "--engine-weights-artifact", "weights.bin",
+                  "--dump-patch-sha", "0" * 64,
+                  "--dump-patch-artifact", "dump.patch",
+                  "--out", str(td / "out20"),
+                  "--workdir", str(td / "wd20")]
+        inj20 = ["--engine-cmd", '["e"]', "--tokenizer-cmd", '["t"]']
+        argv0 = sys.argv
+        try:
+            sys.argv = ["build_carriers.py"] + lift20 + inj20
+            r20 = bc20.main()
+            ok20 = (isinstance(r20, tuple) and r20[0] == "PARSED"
+                    and r20[1].engine_cmd == '["e"]'
+                    and r20[1].tokenizer_cmd == '["t"]'
+                    and r20[1].mode == "real")
+        except SystemExit:
+            ok20 = False
+        finally:
+            sys.argv = argv0
+        check(ok20, "case 20a LIFTABLE COMMAND PARSES: runbook builder "
+                    "argv + guard-injected flags clears the REAL "
+                    "build_carriers argparse surface (dry parse, "
+                    "engine/tokenizer values land in the builder's own "
+                    "namespace)")
+        print("  (next argparse usage/error lines are EXPECTED)")
+        try:
+            sys.argv = ["build_carriers.py"] + lift20
+            bc20.main()
+            check(False, "case 20 must stall without the injected flags")
+        except SystemExit:
+            check(True, "case 20b WITHOUT the injected flags the same "
+                        "argv exits at argparse — the stalling pre-REV-D "
+                        "printed command can never ship again")
+        finally:
+            sys.argv = argv0
+        # case 21 [REV-D 1c]: TERMINAL-STOP RESUME AUTHORIZATION.
+        # (a) strangled caps -> a REAL in-guard checkpoint STOP writes
+        # construction-abort.json WITH the breach values;
+        art21 = json.loads((td / "gate-art16.json").read_text())
+        art21["thresholds"] = dict(frozen, **{
+            "instance_hours": [260.6, 0.001], "usd_total": [73.0, 0.001]})
+        (td / "gate-art21.json").write_text(json.dumps(art21))
+        wd21 = td / "wd21"
+        wd21.mkdir()
+        rd21 = td / "rd21"
+        ns21 = argparse.Namespace(**{
+            **vars(ns16), "gate": str(td / "gate-art21.json"),
+            "rundir": str(rd21), "workdir": str(wd21),
+            "builder": ["--", sys.executable, str(bld16), str(wd21)]})
+        try:
+            cmd_guard(ns21)
+            check(False, "case 21 must STOP on the strangled caps")
+        except SystemExit:
+            ab21 = json.loads(
+                (rd21 / "construction-abort.json").read_text())
+            check(ab21["at_checkpoint"] == 240 and ab21.get("breaches")
+                  and ab21.get("reprojection") is not None,
+                  "case 21a in-guard STOP is TERMINAL evidence: "
+                  "construction-abort.json records the breach values "
+                  "(at n_done=240: %s)" % ab21["breaches"])
+        # (b) abort present -> a re-run REFUSES (even with a healthy
+        # gate) — stop authority survives re-invocation;
+        try:
+            cmd_guard(argparse.Namespace(**{
+                **vars(ns21), "gate": str(td / "gate-art16.json")}))
+            check(False, "case 21 must refuse while the abort exists")
+        except SystemExit:
+            check((rd21 / "construction-abort.json").exists(),
+                  "case 21b abort present -> guard REFUSES to start "
+                  "(n0-from-files can no longer bypass a checkpoint "
+                  "STOP)")
+        # (c) a reset NOT bound to the abort bytes refuses;
+        (rd21 / "construction-reset.json").write_text(json.dumps(
+            {"schema": SCHEMA + ":construction-reset",
+             "authorized_by": "maintainer-test",
+             "decision": "resume-construction", "abort_sha256": "0" * 64}))
+        try:
+            cmd_guard(argparse.Namespace(**{
+                **vars(ns21), "gate": str(td / "gate-art16.json")}))
+            check(False, "case 21 must refuse an unbound reset")
+        except SystemExit:
+            check(True, "case 21c reset with a foreign abort_sha256 "
+                        "REFUSED (a reset authorizes exactly ONE "
+                        "reviewed abort)")
+        # (d) an AUTHORIZED reset resumes with the FULL remaining
+        # schedule re-derived from the abort point (no dropped
+        # checkpoints): abort at 240, 5 concepts cached -> 1056 AND 2304
+        # both run;
+        rd21d = td / "rd21d"
+        rd21d.mkdir()
+        wd21d = td / "wd21d"
+        wd21d.mkdir()
+        for c in range(5):
+            (wd21d / ("concept-%03d.json" % c)).write_text("{}")
+        (rd21d / "construction-abort.json").write_text(json.dumps(
+            {"schema": SCHEMA + ":construction-abort",
+             "at_checkpoint": 240, "n_start": 0, "elapsed_s": 1.0,
+             "breaches": ["central hours (planted)"],
+             "reprojection": {}}))
+        (rd21d / "construction-reset.json").write_text(json.dumps(
+            {"schema": SCHEMA + ":construction-reset",
+             "authorized_by": "maintainer-test",
+             "decision": "resume-construction",
+             "abort_sha256":
+                 sha256_file(rd21d / "construction-abort.json")}))
+        rc21d = cmd_guard(argparse.Namespace(**{
+            **vars(ns16), "rundir": str(rd21d), "workdir": str(wd21d),
+            "builder": ["--", sys.executable, str(bld16), str(wd21d)]}))
+        fin21d = json.loads(
+            (rd21d / "construction-guard-final.json").read_text())
+        check(rc21d == 0 and fin21d["checkpoints_run"] == [1056, 2304]
+              and fin21d["resumed_from_abort"] == 240
+              and not (rd21d / "construction-abort.json").exists()
+              and (rd21d
+                   / "construction-abort.consumed-240.json").exists(),
+              "case 21d AUTHORIZED resume: full schedule re-derived from "
+              "the abort point — 1056 AND 2304 both run (none dropped), "
+              "abort archived single-use")
+        # (e) cached files racing PAST a frozen checkpoint refuse rather
+        # than silently drop it.
+        rd21e = td / "rd21e"
+        rd21e.mkdir()
+        wd21e = td / "wd21e"
+        wd21e.mkdir()
+        for c in range(23):                     # 1104 passes > 1056
+            (wd21e / ("concept-%03d.json" % c)).write_text("{}")
+        (rd21e / "construction-abort.json").write_text(json.dumps(
+            {"schema": SCHEMA + ":construction-abort",
+             "at_checkpoint": 240, "n_start": 0, "elapsed_s": 1.0,
+             "breaches": ["central hours (planted)"]}))
+        (rd21e / "construction-reset.json").write_text(json.dumps(
+            {"schema": SCHEMA + ":construction-reset",
+             "authorized_by": "maintainer-test",
+             "decision": "resume-construction",
+             "abort_sha256":
+                 sha256_file(rd21e / "construction-abort.json")}))
+        try:
+            cmd_guard(argparse.Namespace(**{
+                **vars(ns16), "rundir": str(rd21e), "workdir": str(wd21e),
+                "builder": ["--", sys.executable, str(bld16),
+                            str(wd21e)]}))
+            check(False, "case 21 must refuse a raced-past checkpoint")
+        except SystemExit:
+            check((rd21e / "construction-abort.json").exists(),
+                  "case 21e cached files past checkpoint 1056 -> REFUSED "
+                  "with the abort left IN PLACE (a frozen checkpoint is "
+                  "never silently dropped, even on an authorized resume)")
+        # case 22 [REV-D 1d]: REALIZED-HOURS ACCOUNTING — config-cost
+        # refuses prior dollars without their hours; the hours land in
+        # the cost block the driver Ledger REQUIRES.
+        cfg22 = td / "config22.json"
+        cfg22.write_text("{}")
+        try:
+            cmd_config_cost(argparse.Namespace(
+                final=[str(rd16 / "construction-guard-final.json")],
+                prior_usd="3.1", prior_hours=None, rate="0.174",
+                config=str(cfg22)))
+            check(False, "case 22 must refuse prior USD without hours")
+        except SystemExit:
+            check(True, "case 22a fail-closed: --prior-usd > 0 without "
+                        "--prior-hours refused (failed-session hours "
+                        "can no longer vanish from the 900 h basis)")
+        cmd_config_cost(argparse.Namespace(
+            final=[str(rd16 / "construction-guard-final.json")],
+            prior_usd="3.1", prior_hours="380.0", rate="0.174",
+            config=str(cfg22)))
+        c22 = json.loads(cfg22.read_text())["cost"]
+        check(c22["prior_instance_hours"] == 380.0
+              and abs(c22["usd_spent_prior"]
+                      - (3.1 + fin16["realized"]["usd"])) < 1e-6,
+              "case 22b prior hours THREADED into cost.prior_instance_"
+              "hours — the driver Ledger requires the key and its "
+              "addendum-(7) 900 h basis consumes it (driver-mock "
+              "counterpart proves the STOP flip)")
     print()
     if fails:
         print("BRINGUP-GATE SELFTEST FAILED (%d)" % len(fails))
         return 1
-    print("BRINGUP-GATE SELFTEST PASS — HONEST SCOPE [REV-C]: this $0 "
-          "oracle exercises the projection/license logic (incl. reserve, "
-          "dump conjuncts, regime+engagement refusals), the sampling rule "
-          "mechanics, the per-item stats MERGE, manifest-vs-model "
-          "consistency, the frozen-schedule early-abort checkpoint, the "
-          "construction-guard chain (license binding, probe grammar, "
-          "checkpoint kill-path, evidence artifacts — on STUB "
-          "engine/builder), the gate->config seams, and the shared-model "
-          "identity — ALL on synthetic corpora, planted timings, and a "
-          "mock banner grammar. It CANNOT exercise: the real engine "
-          "(timer, STATS/PIN semantics, dump-mode arming), the real "
-          "tokenizer, GCS transfer, VM deploy, or the real corpus bytes. "
-          "Those exist only via the VM path + f1k_gcp.py gate.")
+    print("BRINGUP-GATE SELFTEST PASS — HONEST SCOPE [REV-C/REV-D]: this "
+          "$0 oracle exercises the projection/license logic (incl. "
+          "reserve, dump conjuncts, regime+engagement refusals), the "
+          "sampling rule mechanics, the per-item stats MERGE, "
+          "manifest-vs-model consistency, the frozen-schedule early-abort "
+          "checkpoint, the construction-guard chain (license binding, "
+          "probe grammar, engine-argv unity by injection, checkpoint "
+          "kill-path, terminal-abort/reset stop authority, evidence "
+          "artifacts — on STUB engine/builder), the REAL builder argparse "
+          "surface (dry parse), the gate->config seams (incl. "
+          "prior-hours), and the shared-model identity — ALL on synthetic "
+          "corpora, planted timings, and a mock banner grammar. It "
+          "CANNOT exercise: the real engine (timer, STATS/PIN semantics, "
+          "dump-mode arming), the real tokenizer, GCS transfer, VM "
+          "deploy, or the real corpus bytes. Those exist only via the VM "
+          "path + f1k_gcp.py gate.")
     return 0
 
 
@@ -2019,8 +2394,15 @@
     p.add_argument("--gate", required=True)
     p.add_argument("--pin", required=True)
     p.add_argument("--engine-cmd", required=True,
-                   help="JSON argv of the CONSTRUCTION engine (the same "
-                        "value passed to build_carriers.py --engine-cmd)")
+                   help="JSON argv of the CONSTRUCTION engine — the "
+                        "guard OWNS this value [REV-D]: it PROBES it and "
+                        "INJECTS it into the builder argv itself "
+                        "(operator-supplied --engine-cmd in the builder "
+                        "argv is refused)")
+    p.add_argument("--tokenizer-cmd", required=True,
+                   help="JSON argv of the builder's tokenizer — "
+                        "guard-injected into the builder argv [REV-D] "
+                        "(same ownership rule as --engine-cmd)")
     p.add_argument("--layers", required=True,
                    help="comma layer list (same as build_carriers --layers)")
     p.add_argument("--tokens", required=True,
@@ -2042,6 +2424,10 @@
     # [REV-C F3] guard-final realized figures -> config.cost (executable)
     p.add_argument("--final", action="append", required=True)
     p.add_argument("--prior-usd", required=True)
+    p.add_argument("--prior-hours", default=None,
+                   help="[REV-D 1d] instance-hours behind --prior-usd "
+                        "(failed sessions + pre-construction); REQUIRED "
+                        "when --prior-usd > 0")
     p.add_argument("--rate", required=True)
     p.add_argument("--config", required=True)
     sub.add_parser("selftest")
```
<!-- END-ARTIFACT D19 -->

### D7.2 D20 — `poc/glm52-probe/f1k-harness/f1k_driver.py` REV-D delta (prior-hours basis + count-preserving bijection + mock probes)

<!-- BEGIN-ARTIFACT D20 f1k_driver.py.rev-d.diff sha256=7ff12e7e916e25aeb47643e4d9c75f143b3acccab40c24d2638fc1094390a391 -->
```diff
diff --git a/poc/glm52-probe/f1k-harness/f1k_driver.py b/poc/glm52-probe/f1k-harness/f1k_driver.py
--- a/poc/glm52-probe/f1k-harness/f1k_driver.py
+++ b/poc/glm52-probe/f1k-harness/f1k_driver.py
@@ -1611,11 +1611,23 @@
     ceiling resolves from the METERED spend recorded in the run's cost
     ledger]. Accumulates per-phase seconds + prefills in
     <outdir>/cost-ledger.json (atomic replace), so timing survives spot
-    interruption and spans pilot + guard + test; construction hours and
-    prior metered spend are REQUIRED config inputs, never silent zeros."""
+    interruption and spans pilot + guard + test; construction hours,
+    prior metered spend AND the prior spend's instance-hours are
+    REQUIRED config inputs, never silent zeros."""
 
     COST_KEYS = ("spot_rate_usd_per_hour", "usd_spent_prior",
-                 "construction_instance_hours")
+                 "prior_instance_hours", "construction_instance_hours")
+    #   [REV-D 1d] prior_instance_hours (gate config-cost --prior-hours:
+    #   failed construction sessions + metered pre-construction) is
+    #   REQUIRED — dollars in usd_spent_prior may never travel without
+    #   their hours, or failed-session time vanishes from the 900 h
+    #   projection basis (round-3 verdict 1d). SCOPE: it feeds the
+    #   addendum-(7) cap basis (add7_hours_basis) ONLY; the SIDECAR
+    #   surface is UNCHANGED — the FROZEN pinned analysis enforces
+    #   cost.instance_hours == construction + sum(phase_seconds)/3600
+    #   (registered identity), so instance_hours() below stays as
+    #   registered and prior hours enter the PRE-SPEND projection cap
+    #   (cap-conservative), never the frozen ledger identity.
 
     def __init__(self, outdir, cfg):
         cost = cfg.get("cost") or {}
@@ -2720,6 +2732,20 @@
 #   REQUIRED model_bundle binding (add7_src_sha256 + tokens_full_sha256).
 
 
+def add7_hours_basis(led_d, pilot_s):
+    """[REV-D 1d] the addendum-(7) 900 h projection's realized-hours
+    basis: PRIOR instance hours (failed construction sessions + metered
+    pre-construction — gate config-cost --prior-hours) + licensed
+    construction hours + realized pilot hours. Module level so the $0
+    mock exercises the SAME basis phase_pilot uses. NOT the sidecar
+    identity: the frozen analysis pins cost.instance_hours ==
+    construction + sum(phase_seconds)/3600; prior hours enter the
+    pre-spend cap projection only (cap-conservative)."""
+    return (float(led_d["prior_instance_hours"])
+            + float(led_d["construction_instance_hours"])
+            + pilot_s / 3600.0)
+
+
 def add7_cap_breach(p4, rate):
     """[REV-C] reserve-inclusive cap test at central AND +1SE (module
     level so the $0 mock exercises the degradation boundary with the
@@ -2839,28 +2865,57 @@
         self.cont = art["model"]["cont_tokens_addend"]
         self.art_sha = blk["gate_artifact_sha256"]
         self.kappa_weighting = None    # set by kappa() [REV-C F5iv]
+        # [REV-D 2] COUNT-PRESERVING sidecar load: rows are consumed as
+        # a dict, so a duplicate key (with a conflicting T) would
+        # silently overwrite and still pass a set-equality "bijection"
+        # (round-3 verdict 2). ANY duplicate key refuses — the licensed
+        # sidecar is duplicate-free by construction.
         self.tp = {}
+        dup = set()
         for ln in open(blk["tokens_full_path"], encoding="utf-8"):
             if ln.strip():
                 e = json.loads(ln)
+                if e["key"] in self.tp:
+                    dup.add(e["key"])
                 self.tp[e["key"]] = e["T"] + self.cont
+        if dup:
+            fail("ERR_F1K_AFFORD",
+                 "gate tokens sidecar carries %d DUPLICATE key(s) (e.g. "
+                 "%s) — duplicate rows would silently overwrite the "
+                 "per-item T; refused, never collapsed [REV-D 2]"
+                 % (len(dup), sorted(dup)[:3]))
 
     def verify_corpus(self, ev):
-        """[REV-C F5ii corpus identity, driver-verifiable form] the
-        licensed sidecar must cover EXACTLY this campaign's eval items:
-        the {pilot, main-tmpl, main-d3, guard} key sets are a bijection
-        with the loaded ev splits (byte-identity of the corpora is
-        enforced on the gate side via corpus_sha256 in the artifact and
-        on the driver side via the landed verify_corpus_pins; this check
-        binds the TWO records to the SAME item universe)."""
-        want = set()
+        """[REV-C F5ii corpus identity, driver-verifiable form; REV-D 2
+        COUNT-PRESERVING] the licensed sidecar must cover EXACTLY this
+        campaign's eval items: the {pilot, main-tmpl, main-d3, guard}
+        key sets are a bijection with the loaded ev splits. STRICTNESS
+        [REV-D]: duplicates are refused on BOTH sides BEFORE the set
+        comparison — the sidecar rows at load (__init__) and the eval
+        inventory here — because sets silently collapse duplicates, so
+        set equality alone is not a bijection (byte-identity of the
+        corpora stays enforced gate-side via corpus_sha256 and
+        driver-side via the landed verify_corpus_pins; this check binds
+        the TWO records to the SAME item universe)."""
+        want_l = []
         for it in ev["dev"]:
-            want.add("pilot:%s" % it["item_id"])
+            want_l.append("pilot:%s" % it["item_id"])
         for it in ev["test"]:
-            want.add("main-tmpl:%s" % it["item_id"])
-            want.add("main-d3:%s" % it["item_id"])
+            want_l.append("main-tmpl:%s" % it["item_id"])
+            want_l.append("main-d3:%s" % it["item_id"])
         for it in ev["guard"]:
-            want.add("guard:%s" % it["item_id"])
+            want_l.append("guard:%s" % it["item_id"])
+        seen = set()
+        edup = set()
+        for k in want_l:
+            (edup if k in seen else seen).add(k)
+        if edup:
+            fail("ERR_F1K_AFFORD",
+                 "eval item inventory carries %d DUPLICATE id(s) (e.g. "
+                 "%s) — a set-equality check would silently collapse "
+                 "them; refused [REV-D 2]"
+                 % (len(edup), sorted(edup)[:3]))
+        want = set(want_l)
         have = {k for k in self.tp
                 if k.split(":", 1)[0] in ("pilot", "main-tmpl", "main-d3",
                                           "guard")}
@@ -3680,7 +3735,10 @@
     _, k_rows = read_ckpt(rows_path)
     kappa = a7m.kappa(s_per_prefill, ev, k_rows)   # [REV-C F5iv]
     reserve_h = RESERVE_USD_ADD7 / rate
-    base_h = ledger.d["construction_instance_hours"] + pilot_s / 3600.0
+    base_h = add7_hours_basis(ledger.d, pilot_s)   # [REV-D 1d] incl.
+    #   prior_instance_hours — failed-session hours never vanish from
+    #   the 900 h cap basis (the SAME module-level helper the mock
+    #   exercises)
     steps_taken = [DEGRADATION_ORDER[0]]
     d3_deferred = False
     replace_candidate = (decision == "RUN")
@@ -3728,13 +3786,15 @@
         "pilot_wall_hours": round(pilot_s / 3600.0, 6),
         "spot_rate_usd_per_hour": rate,
         "usd_spent_prior": prior,
+        "prior_instance_hours":                          # [REV-D 1d]
+            ledger.d["prior_instance_hours"],
         "construction_instance_hours":
             ledger.d["construction_instance_hours"],
         "expert_pinning": attested_pinning(ledger),      # [FIX-5+ASM-2513]
         "projected_total_usd": round(proj, 2),
         "usd_cap": USD_CAP,
         "projection_rev_b": {                            # [REV-B ASM-2516]
-            "model": "kot-f1k-bringup-gate/1 frozen knots (gate artifact "
+            "model": "kot-f1k-bringup-gate/2 frozen knots (gate artifact "
                      "sha %s) re-levelled by kappa; per-item over "
                      "remaining main/guard prefills; ONE model at both "
                      "seams" % a7m.art_sha[:16],
@@ -4205,6 +4265,15 @@
         # surface the real run uses.
         "cost": {"spot_rate_usd_per_hour": SPOT_RATE_DEFAULT,
                  "usd_spent_prior": 146.0,
+                 # [REV-D 1d] REQUIRED prior-hours key. 0.0 IS the
+                 # registered corner figure, not an invention: the
+                 # ASM-2374 corner's $146 usd_spent_prior is the PRICED
+                 # construction time (521.2 h x $0.28 = $145.94) — no
+                 # failed-session/pre-construction hours exist in the
+                 # registered planning corner. The nonzero path (prior
+                 # hours flip a 900 h STOP) is probed below against the
+                 # SAME add7_hours_basis/add7_cap_breach helpers.
+                 "prior_instance_hours": 0.0,
                  "construction_instance_hours": 521.2},
         # [REV-B ASM-2516] the addendum-(7) seam's REQUIRED model inputs
         # (sha-verified fail-closed; a REAL campaign points these at the
@@ -5053,6 +5122,66 @@
                    and not add7_cap_breach(_p4(True, False, kap_b),
                                            rate_p))
 
+    # ---- [REV-D] strict-bijection + realized-hours probes ----
+    print("probe: [REV-D] bijection/prior-hours probes — the next "
+          "ERR_F1K_AFFORD / ERR_F1K_COST lines are EXPECTED")
+    # (2) a DUPLICATE sidecar key with a CONFLICTING T, re-pinned
+    # attacker-consistent through the whole bundle (config shas AND the
+    # artifact-recorded model_bundle sha all agree on the duplicated
+    # bytes) — only the count-preserving load refuses it; the old
+    # set-equality "bijection" passed it silently.
+    dup_lines = [l for l in
+                 open(cfg["affordability"]["tokens_full_path"],
+                      encoding="utf-8") if l.strip()]
+    dup_row = json.loads(dup_lines[0])
+    dup_row["T"] = dup_row["T"] + 7          # conflicting duplicate T
+    dup_tok = outdir / "fixtures" / "tokens-dup.jsonl"
+    dup_tok.write_text("".join(dup_lines) + json.dumps(dup_row) + "\n",
+                       encoding="utf-8")
+    art_dup = json.loads(
+        Path(cfg["affordability"]["gate_artifact_path"])
+        .read_text(encoding="utf-8"))
+    art_dup["model_bundle"]["tokens_full_sha256"] = sha256_file(dup_tok)
+    art_dup_p = outdir / "fixtures" / "gate-art-dup.json"
+    write_json(art_dup_p, art_dup)
+    cfg_dup = json.loads(json.dumps(cfg))
+    cfg_dup["affordability"].update({
+        "tokens_full_path": str(dup_tok),
+        "tokens_full_sha256": sha256_file(dup_tok),
+        "gate_artifact_path": str(art_dup_p),
+        "gate_artifact_sha256": sha256_file(art_dup_p)})
+    try:
+        Add7Model(cfg_dup)
+        dup_closed = False
+    except DriverError:
+        dup_closed = True
+    # (2b) a DUPLICATE eval item id — set equality would collapse it.
+    ev_dup = {"dev": ev["dev"], "test": list(ev["test"]) + [ev["test"][0]],
+              "guard": ev["guard"]}
+    try:
+        a7p.verify_corpus(ev_dup)
+        evdup_closed = False
+    except DriverError:
+        evdup_closed = True
+    # (1d) prior_instance_hours REQUIRED (missing key -> fail-closed) ...
+    cfg_nh = json.loads(json.dumps(cfg))
+    del cfg_nh["cost"]["prior_instance_hours"]
+    try:
+        Ledger(outdir / "fixtures" / "led-nh", cfg_nh)
+        nh_closed = False
+    except DriverError:
+        nh_closed = True
+    # ... and THREADED: prior hours alone flip the 900 h reserve-
+    # inclusive cap through the SAME add7_hours_basis + add7_cap_breach
+    # phase_pilot uses (521.2 construction + 380 prior + reserve > 900;
+    # identical projection sans prior clears).
+    led_ph = dict(led)
+    led_ph["prior_instance_hours"] = 380.0
+    bh_ph = add7_hours_basis(led_ph, 0.0)
+    bh_0 = add7_hours_basis(led, 0.0)
+    ph_flip = (add7_cap_breach((80.0, 80.0, bh_ph, bh_ph), rate_p)
+               and not add7_cap_breach((80.0, 80.0, bh_0, bh_0), rate_p))
+
     print("\n== MOCK SELF-CHECK (codex FIX-FIRST launch blockers 1-7) ==")
     checks = [
         ("[1] SCORER: robust stdout parse — %d banner line(s) skipped "
@@ -5248,6 +5377,23 @@
          "arm-set BREACHES, REPLACE-defer + d3-defer CLEARS — the SSR6 "
          "order recovers a GREEN through the SAME add7_cap_breach "
          "predicate phase_pilot uses" % kap_b, boundary_ok),
+        ("[REV-D 2] STRICT corpus bijection (count-preserving): a "
+         "DUPLICATE sidecar key with a conflicting T REFUSED even when "
+         "re-pinned attacker-consistent through the whole bundle (the "
+         "old set-equality check passed it); a DUPLICATE eval item id "
+         "REFUSED before the set comparison",
+         dup_closed and evdup_closed),
+        ("[REV-D 1d] realized-hours accounting: cost.prior_instance_"
+         "hours REQUIRED (missing key fail-closed at Ledger init) and "
+         "THREADED into the SAME add7_hours_basis/add7_cap_breach the "
+         "pilot->main gate uses — 380 prior h alone flip the 900 h "
+         "reserve-inclusive cap (%.1f h breaches, %.1f h clears); "
+         "addendum-7 records prior_instance_hours=%s; SIDECAR surface "
+         "unchanged (frozen-analysis identity instance_hours == "
+         "construction + run re-validated by THIS mock's analysis pass)"
+         % (bh_ph, bh_0, a7_art.get("prior_instance_hours")),
+         nh_closed and ph_flip
+         and a7_art.get("prior_instance_hours") == 0.0),
         ("governance: engine referred to only as 'colibri'; $0; no "
          "instance, no model download, no git, no registry write "
          "(official-seam runs are SANDBOXED repo copies — no real "
```
<!-- END-ARTIFACT D20 -->

### D7.3 D21 — `poc/gcp/README.md` REV-D delta (argv-unity + terminal-abort + prior-hours runbook)

<!-- BEGIN-ARTIFACT D21 README.md.rev-d.diff sha256=0e9b475a9a83f71c54cdc945c833751e211682169ee11049cdf5aa81f0a50126 -->
```diff
diff --git a/poc/gcp/README.md b/poc/gcp/README.md
--- a/poc/gcp/README.md
+++ b/poc/gcp/README.md
@@ -126,25 +126,43 @@
       checkpoints; kills on breach):
       `python3 poc/gcp/f1k_bringup_gate.py guard --gate bringup-gate.json
       --pin <rundir>/campaign-pin.stats --engine-cmd '<json argv>'
+      --tokenizer-cmd '<json argv>'
       --layers 3,…,77 --tokens <gate-tokens/tokens-full.jsonl>
       --rundir <rundir>/guard --workdir <workdir> --
       python3 poc/glm52-probe/f1k-harness/build_carriers.py construct
       --mode real --layers 3,…,77 <provenance shas AND artifacts:
       --tokenizer-sha/-artifact --engine-weights-sha/-artifact
       --dump-patch-sha/-artifact> --out <out> --workdir <workdir>`
-      (4,608 passes EXACT; ASM-2504 DRAFT=0 geometry, 75 layers). The
-      guard FIRST runs a **dump-mode pin-engagement probe** (one minimal
-      `KAE_DUMP` invocation of the same engine argv/env; armed banner per
-      the landed ASM-2513 grammar, sha/budget/source coherent — REFUSED ⇒
+      (4,608 passes EXACT; ASM-2504 DRAFT=0 geometry, 75 layers).
+      **ENGINE-ARGV UNITY [REV-D]: the guard OWNS `--engine-cmd`/
+      `--tokenizer-cmd` — it probes the engine argv and INJECTS both
+      values into the builder argv itself (construct-don't-compare), so
+      the builder argv above is complete AS PRINTED (oracle-verified
+      against the builder's real argparse surface) and deliberately
+      carries NO engine/tokenizer flags; supplying them there is
+      REFUSED before any engine start.** The guard FIRST runs a
+      **dump-mode pin-engagement probe** (one minimal `KAE_DUMP`
+      invocation of that same engine argv/env; armed banner per the
+      landed ASM-2513 grammar, sha/budget/source coherent — REFUSED ⇒
       no launch, exposure ≈ one engine start), then launches the builder
       (which passes its ambient env into every engine batch —
       `build_carriers.py:634`, verified bytes), and runs the
       **early-abort checkpoints** IN-PROCESS at n_done **240/1056/2304**
       (frozen concept-aligned schedule [REV-C/ASM-2517]; off-schedule
       n_done is refused; STOP exit 2 = builder process-group killed +
-      `construction-abort.json`; first exposure ≈ 9.1 h ≈ **$1.59**).
+      `construction-abort.json` with the breach values; first exposure
+      ≈ 9.1 h ≈ **$1.59**). **A checkpoint STOP is TERMINAL for the
+      rundir [REV-D]: the guard refuses to start while
+      `construction-abort.json` exists — resume needs a maintainer-
+      authored `construction-reset.json` (schema
+      `kot-f1k-bringup-gate/2:construction-reset`, `authorized_by`,
+      `decision: "resume-construction"`, `abort_sha256` = sha256 of the
+      abort file bytes); an authorized resume re-derives the FULL
+      remaining schedule from the abort point (a raced-past frozen
+      checkpoint refuses rather than being dropped).**
       Evidence: `construction-pin-probe.json`,
-      `construction-checkpoint-<n>.json`, `construction-guard-final.json`.
+      `construction-checkpoint-<n>.json`, `construction-guard-final.json`
+      (records the launched `builder_argv`).
    c. `verify --expect-mode real` (full cell-by-cell re-derivation, the
       #46 guarantee); commit the realized tables + `norms.json` +
       `construction-report.json` = **B0**, completing `f1k-carriers-v1`.
@@ -153,7 +171,10 @@
       the campaign config (executable, no pilot stall):
       `python3 poc/gcp/f1k_bringup_gate.py config-cost --final
       <rundir>/guard/construction-guard-final.json --prior-usd <metered
-      pre-construction spend> --rate <campaign spot rate> --config
+      pre-construction + failed-session spend> --prior-hours <the
+      instance-hours behind that spend; REQUIRED when --prior-usd > 0
+      [REV-D] — hours never vanish from the 900 h basis while their
+      dollars are counted> --rate <campaign spot rate> --config
       run-config.json` and
       `python3 poc/gcp/f1k_bringup_gate.py config-affordability --gate
       bringup-gate.json --tokens <gate-tokens/tokens-full.jsonl> --config
```
<!-- END-ARTIFACT D21 -->

## D8. Consolidated coordinator runbook **[superseded by §E.6 — the D1–D24 sequence with the REV-E expectations; do NOT lift this block]** (was: THE liftable block; supersedes §4.2, §A7, §B9, §C7)

```bash
cd /home/ec2-user/css/kernel/kernel-of-truth   # tree at/after 2574c82b (seq-3 LANDED)
M=poc/gcp/F1K-BRINGUP-GATE-FIX.md
for N in D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 D17 D18 D19 D20 D21; do
  awk -v n="$N" '$0 ~ ("^<!-- BEGIN-ARTIFACT " n " ") {f=1; next} \
      $0 ~ ("^<!-- END-ARTIFACT " n " -->") {f=0} f' "$M" | sed '1d;$d' > /tmp/$N.out
done
sha256sum /tmp/D*.out    # must match the §3 + §A4 + §B8 + §C6 + §D7 tables EXACTLY (21 artifacts)
cp /tmp/D1.out poc/gcp/f1k_bringup_gate.py && chmod 644 poc/gcp/f1k_bringup_gate.py
for DN in D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 D17 D18 D19 D20 D21; do git apply /tmp/$DN.out; done
bash -n poc/gcp/f1k_worker.sh
python3 -m py_compile poc/gcp/f1k_gcp.py poc/gcp/f1k_bringup_gate.py \
  poc/glm52-probe/f1k-harness/f1k_driver.py
python3 poc/gcp/f1k_gcp.py gate --selftest      # expect 48 "ok:" lines + PASS, exit 0
python3 poc/gcp/f1k_gcp.py affordability --rate 0.17394 --s-per-prefill 149.1 --replace; echo $?  # 2
python3 poc/gcp/f1k_gcp.py affordability --rate 0.17394 --s-per-prefill 149.1; echo $?            # 3
# NOTE: the mock outdir MUST live under the repo root (kot-log/1 containment refuses /tmp
# [MEASURED §C.6]); ~0.7 GB, delete after.
( cd poc/glm52-probe/f1k-harness && python3 f1k_driver.py --mock --outdir mock-out/revd-verify )
#   expect: MOCK VALIDATION PASS, exit 0, 27 [PASS] 0 [FAIL]
rm -rf poc/glm52-probe/f1k-harness/mock-out/revd-verify
python3 poc/gcp/f1k_gcp.py plan                 # regression: DRY-PLAN OK unchanged
# ONE plain-infra commit: this memo + the five patched files + ASM-2514 + ASM-2515 + ASM-2516 +
# ASM-2517 (both as amended in-memo) + ASM-2518; tools/registry/registry-check.py green
# (nothing frozen is touched; build_carriers.py is NOT in the diff set).
```

Acceptance gate: review green → extract (sha-verified, 21 artifacts) → apply D1–D21 → oracle
48/48 + the two exit-code probes + driver mock green (27 [PASS]) + `plan` green → ONE commit
(five ASM rows) → registry-check green. The tree is at seq-3-landed; if it has drifted beyond
`2574c82b`'s state on the five target files, STOP and re-baseline (§0 rule).

## D9. ASM-2518 registration text (register-at-commit WITH ASM-2514/2515/2516/2517; next free id
[MEASURED this pass: assumptions.jsonl tail = ASM-2513 (registered, landed); 2514/2515/2516/2517
reserved by this memo, absent from the file; 2518 free]) **[superseded — §E.7 carries the REV-E-amended ASM-2518 text; register THAT text, not this JSON]**

```json
{"id": "ASM-2518", "tag": "STIPULATED", "load_bearing": true, "claim": "F1-K BRING-UP GATE REV-D (amends ASM-2516 items (3)/(4) and ASM-2517 items (1)/(3)/(6) in the same landing commit; closes the cross-model round-3 verdict poc/gpt56-review/f1k-gate-fix-round3-VERDICT.md, overall REJECT with a narrow fully-prescribed remainder; every round-3 CLOSED/settled region kept byte-stable): (1) ENGINE-ARGV UNITY (amends 2517(1)) - the guard OWNS the construction engine/tokenizer commands, construct-don't-compare: operator-supplied --engine-cmd/--tokenizer-cmd in the builder argv (space or = form) is REFUSED before ANY engine start, and the guard INJECTS the PROBED --engine-cmd plus its --tokenizer-cmd into the builder argv at launch (both validated as JSON lists), so the attested engine and the constructing engine cannot diverge; construction-guard-final.json records the launched builder_argv verbatim; the README 5b builder command is complete AS PRINTED (no engine/tokenizer flags - injected) and its argv shape is oracle-verified against the REAL build_carriers.py argparse surface (in-memory dry parse, cmd_construct stubbed, pinned bytes untouched; the uninjected shape is proven to stall = the round-3 1b defect as a failing case). (2) TERMINAL-STOP AUTHORITY (amends 2517(3)) - a checkpoint STOP's construction-abort.json now records the breach values (breaches/reprojection/ratio) and is TERMINAL for the rundir: the guard REFUSES to start while it exists, naming the recovery (mirrors the landed ASM-2513 missing-ledger recovery pattern); resume ONLY via maintainer-authored construction-reset.json {schema kot-f1k-bringup-gate/2:construction-reset, authorized_by non-empty, decision resume-construction, abort_sha256 = sha256 of the abort file bytes} - byte-bound, single-abort; an authorized resume re-derives the FULL remaining frozen schedule from the abort point and REFUSES if cached concept files raced past a frozen checkpoint (never silently dropped); the abort is archived (construction-abort.consumed-<n>.json) only after ALL resume validations pass; a preemption resume without a prior STOP is unchanged. (3) REALIZED-HOURS BASIS (amends 2516(4)/2517(3) checkpoint-cost text) - config-cost gains --prior-hours, REQUIRED whenever --prior-usd > 0 (refused otherwise), emitted as cost.prior_instance_hours; the driver Ledger REQUIRES the key (4th COST_KEYS entry, fail-closed at init, changed-basis resume refusal included) and the addendum-(7) 900h basis is the module-level add7_hours_basis (prior + construction + realized pilot) used by phase_pilot and the $0 mock alike - failed-session/pre-construction hours can no longer vanish from the cap while their dollars are counted; DISCLOSED: the SIDECAR surface is unchanged (the FROZEN analysis 126129b9 enforces instance_hours == construction + run and a closed cost schema), so prior hours act on the PRE-SPEND projection cap only (cap-conservative); mock: 380 prior hours alone flip the reserve-inclusive 900h STOP through the production helpers; mock cost fixture prior_instance_hours=0.0 is the registered ASM-2374 corner figure (the $146 prior is priced construction time), disclosed in-code. (4) STRICT CORPUS BIJECTION (amends 2517(4)-adjacent corpus text in (6)) - COUNT-PRESERVING verification: Add7Model refuses ANY duplicate sidecar key at load (duplicates would silently overwrite the per-item T in the dict) and verify_corpus refuses ANY duplicate eval-inventory id BEFORE the set comparison, making the retained set equality a true bijection; mock plants an ATTACKER-CONSISTENT conflicting-T duplicate (config sha + artifact model_bundle sha re-pinned to the duplicated bytes) -> refused, plus a duplicated eval item -> refused; the live projection_rev_b.model label string corrected /1 -> /2 (label-only, disclosed). (5) SUPERSESSION HONESTY - the four round-3-cited stale lines (memo:232 re-derivation claim, memo:242 schema /1, memo:1781 200/1024/2304 ~$1.3, memo:1788 pin-replacement-before-pilot) struck/marked in place; fresh grep proves no unstruck operative stale text remains (all residual hits are byte-pinned historical artifact blocks, already-amended-marked passages, or ASM texts amended in the same landing); SSC.5's inline-kills claim TRUE at REV-D. (6) ORACLE/MOCK - oracle 37 -> 48 (16a/17 extended + 11 new checks: 19a/b divergence, 20a/b dry parse, 21a-e terminal-stop chain, 22a/b prior-hours); driver mock 25 -> 27 [PASS] (REV-D bijection + prior-hours lines); all green on the edited bench AND the fresh D1->D21 chain. Bench: 21-artifact chain applies clean on the LANDED 2574c82b tree (byte-identical fresh-chain reproduction, cmp x5; finals 90c38c6e/468ab73d/53d21424/aee6e716/0427d5fd - f1k_gcp.py and f1k_worker.sh UNCHANGED from REV-C), py_compile x3 + bash -n clean, affordability probes exit 2/3, plan DRY-PLAN OK, discipline greps clean (0 PINS/FROZEN_SHA256 edits, both KOT-ADD7-SHARED blocks untouched at 9d3e1bc7, build_carriers.py byte-identical a92be3e4, NOT in the diff set); every REV-D change is fail-closed-only on unpinned infra files.", "rationale": "The round-3 verdict proved the REV-C composite could attest construction against the wrong executable (probe engine A, build with engine B), print a construction command that stalls at the builder's argparse, let a re-run silently bypass a checkpoint STOP's stop authority, let failed-session hours vanish from the 900h cap while their dollars counted, and pass a conflicting duplicate sidecar row through a set-equality 'bijection'. REV-D closes each at the narrowest honest surface: ownership-by-injection instead of comparison, the real argparse surface as an oracle case, byte-bound single-use maintainer resets, a required prior-hours key threaded through the production cap helpers, and count-preserving duplicate refusal on both sides of the corpus identity check.", "backing_ref": "poc/gcp/F1K-BRINGUP-GATE-FIX.md REV-D SSD (this freeze; D19-D21 + bench evidence); poc/gpt56-review/f1k-gate-fix-round3-VERDICT.md; build_carriers.py:1875 (pinned bytes: mandatory --engine-cmd/--tokenizer-cmd argparse surface); analysis/f1k.py 126129b9 (frozen instance_hours identity + closed cost schema); f1k_driver.py landed 2574c82b (Ledger/addendum-7 seam); ASM-2513 (missing-ledger recovery pattern mirrored), ASM-2374 (corner figures), ASM-2514/2515/2516/2517 (as amended); bead kernel-of-truth-8cpm (deferred seq-4 generator re-freeze, unchanged)", "status": "open", "owner": "designer-20", "date": "2026-07-18"}
```

## D10. REV-D self-check (rows 62–75; every claim → where verified this pass → tag)

| # | Claim | Verified where (this REV-D pass) | Tag |
|---|---|---|---|
| 62 | Round-3 verdict read verbatim; all six defects mapped (D0); every round-3 cite (memo:232/242/1781/1788/5065/5072/5077/5097/5203/5211/5714/5924/5946 + build_carriers.py:1875/:853 + f1k_driver.py:1758) resolved by a D19–D21 hunk or an in-place memo kill | verdict full read + D0 map + this table | [MEASURED memo/diff state] |
| 63 | Settled regions byte-stable: D1–D18 artifact blocks unedited (18 shas re-verified); `f1k_gcp.py`/`f1k_worker.sh` finals unchanged (`468ab73d`/`53d21424`); both KOT-ADD7-SHARED blocks hash `9d3e1bc7…`; 0 PINS/FROZEN_SHA256 edits | extraction + sha compare + discipline greps | [MEASURED] |
| 64 | Target-file baseline: the five files byte-equal to HEAD `2574c82b` before benching (`git diff --stat` empty) | git diff this pass | [MEASURED] |
| 65 | D19–D21 shas as tabled; full D1→D21 chain applies clean; fresh-chain reproduction byte-identical (`cmp` ×5); finals 90c38c6e/468ab73d/53d21424/aee6e716/0427d5fd | two independent /tmp benches this pass | [MEASURED] |
| 66 | Oracle 48/48, exit 0, 0 FAIL — BOTH invocation paths (`gate --selftest`, direct) on the edited bench AND the fresh-chain tree | four selftest runs this pass | [MEASURED] |
| 67 | Driver $0 --mock: exit 0, 27 [PASS], 0 [FAIL], MOCK VALIDATION PASS; [REV-D 2] + [REV-D 1d] lines green; pinned-analysis pass green with the new REQUIRED cost key (emission-surface oracle per the round-4 lesson) | mock run + log grep this pass | [MEASURED] |
| 68 | Engine-argv unity: refusal fires BEFORE `_probe_engagement` (no probe evidence file on refusal — asserted, not assumed); injected tail == probed argv recorded in guard-final | oracle 19a assertion + 16a conjunct | [MEASURED] |
| 69 | Dry parse hits the REAL argparse surface: injected values observed in the builder's own parsed namespace; uninjected liftable shape exits at argparse; pinned `build_carriers.py` bytes untouched (sha `a92be3e4…` compared post-run) | oracle 20a/20b + sha compare | [MEASURED] |
| 70 | Terminal-stop chain: organic in-guard STOP wrote breach values; refuse/bad-reset/authorized-resume/raced-past all exercised; abort archived ONLY on full validation (refused resume leaves it in place — asserted in 21e) | oracle 21a–e | [MEASURED] |
| 71 | Prior-hours: `config-cost` refusal + threading; Ledger missing-key fail-closed; 900 h STOP flip through `add7_hours_basis`+`add7_cap_breach` (901.2 vs 521.2 h); addendum-7 records the key; sidecar cost block emission UNTOUCHED (frozen-analysis identity) | oracle 22a/b + mock [REV-D 1d] + D20 hunk inspection | [MEASURED] |
| 72 | Strict bijection: attacker-consistent conflicting-T duplicate refused; duplicate eval id refused; the refusals happen at load/pre-set-comparison (count-preserving), not via sha checks | mock [REV-D 2] probes | [MEASURED] |
| 73 | Stale-text kills applied; fresh grep: no unstruck operative stale phrasing (residuals = pinned artifact blocks / amended-marked passages / same-landing-amended ASM texts, each classified) | §D.6 grep this pass | [MEASURED] |
| 74 | ASM tail: 2513 last registered; 2514–2517 reserved by this memo (absent from the file); 2518 free; 2516/2517 headers annotated to register only WITH their amending successors | `registry/assumptions.jsonl` tail read this pass | [MEASURED] |
| 75 | Memo-only pass: repo untouched except this file; NO spend/VM/git action; mock output (≈0.7 GB) deleted; /tmp benches disposable | `git status` this pass | [MEASURED] |

## D11. Summary (REV-D, whole composite) **[historical — §E.9 is the REV-E whole-composite summary; §E amends: abbreviation-aware engine-argv refusal, durable terminal-stop events + consumed resets, operator-numeric finiteness, supersession honesty (incl. the driver and the gate `pin.role` text)]**

- **The guard now OWNS the engine argv** (construct-don't-compare): the probed
  `--engine-cmd`/`--tokenizer-cmd` are INJECTED into the builder argv; operator-supplied values
  there are refused before any engine start — the attested and constructing engines cannot
  diverge, and the printed 5b command is complete as printed (oracle-verified against the real
  builder argparse).
- **Stop authority is terminal:** a checkpoint STOP's abort (now carrying the breach values)
  blocks every future guard start in that rundir until a maintainer writes a byte-bound
  single-use `construction-reset.json`; an authorized resume re-derives the full remaining
  schedule from the abort point and refuses raced-past checkpoints.
- **Hours travel with their dollars:** `--prior-hours` (required with any prior spend) →
  `cost.prior_instance_hours` → REQUIRED Ledger key → the addendum-(7) 900 h cap basis; the
  frozen-analysis sidecar identity is untouched (disclosed).
- **The corpus bijection is count-preserving:** duplicates refused on BOTH sides before the set
  comparison; a conflicting duplicate `T` can no longer slip through, even attacker-consistent.
- **The memo tells one story again:** the four stale round-3-cited lines are struck/marked;
  §C.5's claim is re-verified TRUE by fresh grep.
- **Evidence:** 21 sha-pinned artifacts; byte-identical fresh-chain reproduction on `2574c82b`
  (cmp ×5; finals 90c38c6e/468ab73d/53d21424/aee6e716/0427d5fd — gcp/worker UNCHANGED from
  REV-C); oracle 48/48 (both paths, both benches); driver mock 27 [PASS]/0 FAIL with the pinned
  analysis green; probes 2/3; plan green; discipline greps clean; ONE plain-infra landing commit
  + ASM-2514/2515/2516/2517 (amended) + ASM-2518. $0 spent; nothing applied by this pass.

~~BRINGUP-GATE-FIX REV-D DONE~~ **[superseded — the composite is DONE at REV-E; §E below]**

# §E — REV-E ADDENDUM: closing the round-4 four-blocker residual (delta diffs D22–D24 on top of D19–D21)

**Scope discipline [REV-E]:** the round-4 verdict (`poc/gpt56-review/f1k-gate-fix-round4-VERDICT.md`,
read verbatim this pass) is a REJECT with **exactly four blockers**; everything else is CLOSED
(runbook completeness incl. the real-argparse case 20, strict bijection, hours arithmetic for
finite inputs, injection-wins-last, all 21 artifact chains). Every settled region is kept
**byte-stable**: the D1–D21 artifact blocks are unedited (21 shas re-extracted and re-verified
this pass), the chains re-apply clean on `2574c82b` reproducing the §D7 finals exactly, and
`f1k_gcp.py`/`f1k_worker.sh` are untouched by D22–D24 (finals `468ab73d`/`53d21424` unchanged).
REV-E adds ONLY the four prescribed closures below.

## E0. Round-4 blocker → disposition map

| # | Round-4 blocker | Disposition |
|---|---|---|
| 1 | abbreviation-accepting refusal gap: the refusal matched full names only while the pinned builder's argparse (default abbreviation, `build_carriers.py:1871`) accepts `--engine-c`/`--engine-cm`/`--tokenizer-c`/`--tokenizer-cm` (+ `=` forms) | **CLOSED (D22, §E.1):** prefix-floor refusal proven EQUAL to argparse's resolution for this parser's option set [MEASURED, real parser]; oracle 19c (all 8 forms refused) + 20c (real-parser floor proof) |
| 3 | deletable abort + reusable reset: deleting `construction-abort.json` was undetected; the reset was left in place after use | **CLOSED (D22, §E.2):** append-only fsynced `construction-events.jsonl` (sentinel mechanics) is the stop authority — deletion/tamper/replay refused on the EVENT; reset CONSUMED (reset+abort archived, hash+ordinal names, consumption event appended) BEFORE any engine start; oracle 21f/21g/21h + 21a/21d/21e extended |
| 4 | NaN fail-open cost inputs: `--prior-hours nan` passed `ph < 0`, NaN basis, `nan > 900` False → GO | **CLOSED (D22+D23, §E.3):** one finiteness helper applied to EVERY gate operator numeric (a SECOND fail-open of the class — `pinfile --pin-gb` NaN → UNBOUNDED pin — found and closed by the sweep) + a driver-Ledger finiteness assert on all four required cost keys; oracle 22c/22d + mock `[REV-E 3]` |
| 6 | stale supersession text: memo:1707 (§A0), memo:2718 (§B.7 "stands"), driver :755/:3663 | **CLOSED (in place + D22/D23, §E.4):** all four cited sites killed PLUS a self-found fifth (the gate collect `pin.role` string); fresh grep RE-RUN over the memo AND all five D-chain files, residuals classified — the claim is now TRUE |

## E1. Round-4 1 — abbreviation-aware operator-flag refusal (D22)

The REV-D refusal loop matched `--engine-cmd`/`--tokenizer-cmd` (and their `=` forms) literally;
the pinned builder's argparse resolves unambiguous prefixes. REV-E replaces the loop with a
**prefix-floor rule**: a builder-argv token whose flag part (before any `=`) is a prefix of an
owned flag with length ≥ the floor (`--engine-c`, 10 chars / `--tokenizer-c`, 13 chars) is
refused pre-engine-start, naming the flag argparse would resolve it to.

**Why the rule EQUALS argparse's resolution for THIS parser [MEASURED on the real pinned
parser, `a92be3e4`]:** the construct subparser's complete option set is `--engine-cmd`,
`--tokenizer-cmd`, `--mode`, `--layers`, `--tokenizer-sha`, `--engine-weights-sha`,
`--dump-patch-sha`, `--tokenizer-artifact`, `--engine-weights-artifact`,
`--dump-patch-artifact`, `--out`, `--workdir` (+ `-h/--help`). The only other options on the
`--engine-` stem are the two `--engine-weights-*` flags (diverging at `c` vs `w`); the only
others on `--tokenizer-` are `--tokenizer-sha`/`--tokenizer-artifact` (diverging at `c` vs
`s`/`a`). Hence ANY prefix of an owned flag of length ≥ the floor is unambiguous and
argparse-resolves to the owned flag, while EVERY shorter `--engine*`/`--tokenizer*` stem
matches ≥ 3 options and argparse exits 2 with an ambiguous-option ERROR — never a silent
resolution. Measured this pass against the real parser: all 6 abbreviated forms
(`--engine-c`, `--engine-cm`, `--engine-cm=`, `--tokenizer-c`, `--tokenizer-cm`,
`--tokenizer-c=`) resolve to the owned flags; `--engine`, `--engine-`, `--tokenizer`,
`--tokenizer-` all exit 2. The floors are pinned BY the builder pin: any change to
`build_carriers.py` is already an encoder-of-record event that re-opens this analysis.

- **Oracle [MEASURED]:** case 19c — all 8 abbreviated attack forms (4 abbreviations × space/`=`)
  refused pre-engine-start; case 20c — the SAME floors proven on the REAL argparse surface
  (abbreviated owned flags land in the builder's parsed namespace; the four shorter stems exit
  2), so the guard's rule and the builder's resolution can never silently diverge.

## E2. Round-4 3 — durable terminal stop; consumed single-use reset (D22)

- **Durable stop:** the kill path now ALSO appends `{"event": "terminal-abort", "ordinal": n,
  "at_checkpoint": p, "abort_sha256": sha256(abort bytes)}` to the rundir's append-only
  `construction-events.jsonl` — fsynced file AND dirent, the SAME durability mechanics (and the
  same recovery language) as the landed SPEND-START sentinel [ASM-2513 v4]. EVERY guard start
  reads this file. With an unconsumed terminal event: a MISSING abort file is refused (deletion
  never lifts stop authority; recovery NAMES the maintainer path — restore the bytes hashing to
  the recorded sha, review, then the reset path); an abort whose bytes do not hash to the
  event's `abort_sha256` is refused (tamper); the reset path then validates as in REV-D
  (byte-bound, schema, authorized_by, decision). With NO unconsumed terminal event: an abort
  file present is refused as replayed/foreign; a reset present is refused — **a second use
  finds nothing to authorize**.
- **Consumed reset, archive-then-proceed:** the raced-past-checkpoint validation is moved BEFORE
  the pin-engagement probe (which IS an engine start); after ALL resume validations pass, the
  reset is archived as `construction-reset.consumed-<ordinal>-<abort-sha16>.json` and the abort
  as `construction-abort.consumed-<n>.json`, and a `reset-consumed` event (ordinal-matched to
  the terminal event) is appended — all BEFORE any engine start. A REFUSED resume leaves abort
  AND reset in place, terminal as ever (oracle 21e asserts both).
- **Honest residuals [DISCLOSED]:** (a) an operator with filesystem access who edits the
  guard's event state ITSELF is out of scope — the same threat boundary as the landed
  spend-start sentinel (this closes re-invocation and abort-file deletion, not a hostile
  filesystem root); (b) a probe/launch failure AFTER consumption does not re-arm the OLD stop —
  the maintainer's authorization covers the remaining schedule until a NEW checkpoint STOP
  appends a fresh terminal event (stated in-code).
- **Oracle [MEASURED]:** 21a extended (organic STOP appends the hash-bound event); 21d extended
  (both archives + consumption event asserted; reset gone); 21e extended (reset left
  unconsumed on refusal); NEW 21f (abort deleted, terminal event present, otherwise-valid
  reset present → refused BEFORE any engine start, reset left unconsumed); NEW 21g (consumed
  reset copied back → refused: no outstanding stop); NEW 21h (abort file with NO terminal
  event → refused, never consumed). Fixtures for planted aborts (21d/21e/21f) now plant the
  matching terminal event, exactly as the kill path writes it.

## E3. Round-4 4 — finiteness of every operator-supplied numeric (D22 gate + D23 driver)

The defect class (the landed PIN-fix's `PIN_GB` class): `nan > cap` and `nan <= cap` are both
False, so a NaN that survives parsing turns STOP predicates into fail-open GO/CONTINUE.
`config-cost --prior-hours nan` did exactly that (`ph < 0` is False for NaN → NaN 900 h basis →
GO). REV-E adds ONE helper (`_fin`: float-parse + `math.isfinite` + sign contract, fail-closed
`die`) and applies it to EVERY operator numeric on the gate CLI — the full sweep, with the
measured classification of each surface:

| Surface | Pre-REV-E behaviour on NaN [MEASURED/analyzed] | REV-E |
|---|---|---|
| `config-cost --prior-hours/--prior-usd/--rate` + summed guard-final `realized.*` | **fail-open GO** (the round-4 blocker) | `_fin` at the parse; the dead `ph < 0` check removed (subsumed) |
| `pinfile --pin-gb` | **fail-open — UNBOUNDED pin** (`used + PER_EXPERT_BYTES > nan` never True → every expert selected); a second true fail-open found by this sweep | `_fin`, > 0 |
| `checkpoint --elapsed-s` | fail-closed INCIDENTALLY (ratio sanity `0 < nan ≤ 10` is False → die) | explicit `_fin`, > 0 |
| `checkpoint --n-done/--n-start` | `int("x")` ValueError crash (closed, ugly) | clean die |
| `guard --poll-seconds` | `time.sleep(nan)` ValueError MID-construction, AFTER builder launch [MEASURED] | `_fin` pre-start, > 0 (oracle: no probe evidence) |
| `collect --rate/--pin-gb` | NaN frozen into gate-inputs; the license GO path requires affirmative conjuncts (fail-closed by construction) but the value would persist | `_fin` at the parse |
| `fcount --mock-f` ($0 mock only) **[REV-F: round-5 defect 3 — this row said `realize`; the flag is on the `fcount` subparser (memo:1152/:1157) and the D22 `_fin` lands in `tokenize()`, the fcount path]** | `round(nan)` ValueError crash | `_fin`, > 0 |
| `f1k_gcp.py affordability --rate/--s-per-prefill` | **exit 2 fail-closed [MEASURED this pass]** — any non-GO projection refuses (REV-A F3d) | deliberately UNTOUCHED (`468ab73d` unchanged) |
| driver Ledger cost keys | a hand-edited bare-NaN JSON value parses [MEASURED] and poisons `add7_hours_basis` | **D23:** finiteness/sign assert on all four `COST_KEYS` at init — refused whoever wrote the config (defense-in-depth behind config-cost) |

- **Oracle/mock [MEASURED]:** 22c (nan/inf `--prior-hours`, nan/inf `--prior-usd`, nan `--rate`
  all refused at config-cost); 22d (nan `--elapsed-s` refused at checkpoint; nan
  `--poll-seconds` refused BEFORE any engine start — no probe evidence); driver-mock
  `[REV-E 3]` line: a hand-edited NaN in `cost.prior_instance_hours` → `ERR_F1K_COST` at
  Ledger init. The Ledger's changed-basis resume comparison was already NaN-fail-closed
  (`nan != base` is True → refuse) — disclosed, not relied on.

## E4. Round-4 6 — stale supersession text killed; grep claim made TRUE (in place + D22/D23)

Kills this pass (title/§0 header updated to REV-E as well):

- **memo:1707 (§A0 F5 row):** the "re-derivation moves into licensed construction +
  boundary swap" half STRUCK with the withdrawal bracket (REV-C memo:2568; bead
  `kernel-of-truth-8cpm`); the bring-up-pin-IS-the-campaign-pin half stands.
- **memo:2718 (§B.7 row):** "**stands**, now ENFORCED" corrected to **stands IN PART** —
  the row's unqualified "stands" contradicted the :2568 withdrawal.
- **driver (D23):** the `validate_pinning` docstring (repo `f1k_driver.py:755`) and the
  mock-fixture comment (repo `:3663`) rewritten: the campaign pin is the LICENSED
  bring-up-derived pin run for the WHOLE campaign; re-derivation withdrawn/deferred; the
  driver refuses a campaign pin ≠ the gate artifact's.
- **gate (D22), SELF-FOUND — not in the verdict:** the collect `pin.role` artifact string
  still said "re-derivation from full-corpus STATS only at the construction->pilot boundary,
  re-bound there via a coordinator-committed rebind record" — the same withdrawn language,
  in D-chain-produced code the round-4 grep obligation would have caught. Rewritten to the
  REV-C state (whole-campaign pin; NO rebind record; NO rebind path). Disclosed because the
  fresh-grep claim below would otherwise be false again.

**Fresh grep [MEASURED this pass — memo AND all five D-chain-produced files AND
`build_carriers.py`]** for the stale phrasings (`re-derived on the real construction corpus`,
`re-derivation from full-corpus STATS only`, `rebind record`, `200/1024`, `$1.3`,
`kot-f1k-bringup-gate/1`): every remaining occurrence is (a) inside a byte-pinned HISTORICAL
artifact block of this memo (the D1/D5/D9 quoted diffs at memo:1869/:2942 — changing them would
break the sha chain; their APPLIED state is fixed by D22), (b) an already-struck/amended-marked
passage (memo:234, the §D.6/§E.4 brackets themselves), or (c) a landed historical memo record
(`F1K-PIN-FILE-FIX.md:711`, the instruction block that originally inserted the driver comment —
the LIVE driver text is fixed by D23; that memo is a landed record, not operative guidance), or
(d) live text that NEGATES the withdrawn mechanism (the `rebind record` pattern also matches
"there is NO rebind record and NO rebind path" in the applied gate/README — the correct current
state, not stale text; classified so the pattern list stays honest).
~~**No unstruck operative stale text remains — TRUE at REV-E state.**~~ **[REFUTED by
round-5 finding 4 — two `/1` residues survived this classification: the LIVE gate module
docstring (D1-origin, post-chain `f1k_bringup_gate.py:2` — neither historical-artifact-only
nor struck) and this memo's unstruck §5.1 freeze statement (memo:1610). Both killed at REV-F
(D25 + the §5.1 strike); the RE-RUN grep and the now-TRUE claim live in §F.2. Bucket (a)'s
"APPLIED state is fixed by D22" reads "by D14–D17/D22 and, for the D1 docstring, D25" at
REV-F.]**

## E5. Delta artifacts D22–D24 (apply AFTER D21, in order; sha-pinned; bench-verified on the LANDED tree)

| # | Target | Kind | sha256 of the artifact below |
|---|---|---|---|
| D22 | `poc/gcp/f1k_bringup_gate.py` (post-D19) | unified diff | `e01c4518459c7fdc94ff50248c23f6497ecd6ab786e45269d8cf8cdf3d845af9` |
| D23 | `poc/glm52-probe/f1k-harness/f1k_driver.py` (post-D20) | unified diff | `b0da3bacad679c1cefa2cec50c42e9f795c6ab290fc0ed8ea1eb8f226c2baa01` |
| D24 | `poc/gcp/README.md` (post-D21) | unified diff | `58baf5cef4c1d3c935719b542659d687ea716775d980e24aead35b65b9f0db1f` |

Bench evidence [MEASURED, /tmp bench this REV-E pass — no repo file touched beyond this memo]:

- **Chains:** D1–D21 re-extracted (all 21 shas match the §3/§A4/§B8/§C6/§D7 tables) and
  re-applied clean on the CURRENT landed bytes (`2574c82b`; the five target files verified
  byte-equal to HEAD first), reproducing the §D7 finals
  (`90c38c6e`/`468ab73d`/`53d21424`/`aee6e716`/`0427d5fd` — re-verified). D22–D24 then apply
  clean; a SECOND fresh copy taken through the full D1→D24 chain is **byte-identical** to the
  edited bench on all five files (`cmp` ×5). Applied-tree result shas:
  `f1k_bringup_gate.py 2484638088a6849b…`, `f1k_gcp.py 468ab73d078eaaf5…` (UNCHANGED from
  REV-C), `f1k_worker.sh 53d21424b1d35016…` (UNCHANGED), `README.md 34e6bb27da33e236…`,
  `f1k_driver.py 261431c1500a0ad7…`.
- `py_compile` (gate, gcp, driver) + `bash -n` (worker) clean on the applied tree.
- **$0 oracle 55/55** (`f1k_gcp.py gate --selftest` AND direct `selftest`, on the edited bench
  AND the fresh-chain tree; exit 0, 0 FAIL) — the 48 REV-D checks (21a/21d/21e extended as
  above) + 7 REV-E checks: 19c, 20c, 21f, 21g, 21h, 22c, 22d.
- **Driver $0 --mock green** on the applied tree: exit 0, **28 [PASS]**, 0 [FAIL],
  `MOCK VALIDATION PASS`; the `[REV-E 3]` probe prints its EXPECTED `ERR_F1K_COST` refusal;
  the `[REV-D 2]`/`[REV-D 1d]` lines stay green; the mock's end-to-end campaign
  (pilot → guard → test → sidecar → PINNED analysis) stays green — the frozen-analysis
  identity re-validated by the analysis pass itself (emission-surface oracle, round-4
  lesson). Output ≈ 0.7 GB this pass — deleted after.
- Probes on the applied tree: `affordability --rate 0.17394 --s-per-prefill 149.1 --replace`
  → exit 2; without `--replace` → exit 3; `plan` → `DRY-PLAN OK` (env-stubbed control-box
  vars).
- Discipline greps [MEASURED]: **0** `PINS`/`FROZEN_SHA256` tokens on any +/- line of
  D22–D24; **0** touches inside either `KOT-ADD7-SHARED` block (both blocks hash
  `9d3e1bc76f8506d9…` == the frozen constant on the applied tree; oracle case 18 re-proves
  it); `build_carriers.py` byte-identical to the repo (`a92be3e4…`, sha-compared post-run) —
  NOT in the diff set; neither touched file is sha-pinned → the landing stays plain infra.

### E5.1 D22 — `poc/gcp/f1k_bringup_gate.py` REV-E delta (abbreviation floors + durable stop events/consumed reset + finiteness sweep + oracle 55)

<!-- BEGIN-ARTIFACT D22 f1k_bringup_gate.py.rev-e.diff sha256=e01c4518459c7fdc94ff50248c23f6497ecd6ab786e45269d8cf8cdf3d845af9 -->
```diff
diff --git a/poc/gcp/f1k_bringup_gate.py b/poc/gcp/f1k_bringup_gate.py
--- a/poc/gcp/f1k_bringup_gate.py
+++ b/poc/gcp/f1k_bringup_gate.py
@@ -107,6 +107,27 @@ def sha256_file(p):
     return h.hexdigest()
 
 
+def _fin(val, what, code, lo=0.0, lo_open=False):
+    """[REV-E 3] operator-numeric hygiene (round-4 verdict 4; the landed
+    PIN_GB defect class): every number an operator hands this CLI must
+    be FINITE and honor its sign contract BEFORE it reaches any cap
+    comparison — nan > cap and nan <= cap are BOTH False [MEASURED], so
+    a NaN basis turns breach predicates into silent fail-open
+    GO/CONTINUE. Fail closed at the parse, never downstream."""
+    try:
+        f = float(val)
+    except (TypeError, ValueError):
+        die(code, "%s: %r is not a number [REV-E]" % (what, val))
+    if not math.isfinite(f):
+        die(code, "%s: %r is not FINITE — NaN/inf fail OPEN through cap "
+            "comparisons (nan > cap is False; the PIN_GB defect class) "
+            "[REV-E]" % (what, val))
+    if f < lo or (lo_open and f == lo):
+        die(code, "%s: %r must be %s %g [REV-E]"
+            % (what, val, ">" if lo_open else ">=", lo))
+    return f
+
+
 def tiehash(key):
     return hashlib.sha256(("%d:%s" % (SAMPLE_SEED, key)).encode()).hexdigest()
 
@@ -174,6 +195,8 @@ def corpus_shas(corpus_dir):
 # ---------------------------------------------------------------------------
 def tokenize(inv, args):
     if args.mock_f is not None:
+        _fin(args.mock_f, "--mock-f", "F1K_GATE_TOK",
+             lo_open=True)                                  # [REV-E 3]
         # $0 MOCK path (selftest / dry-run ONLY; clearly labeled in output):
         # T = round(W * mock_f), ids deterministic in-vocab like the
         # functional-gate sample. NEVER a license input.
@@ -421,7 +444,11 @@ def cmd_pinfile(args):
             merged[(l, e)] = merged.get((l, e), 0) + c
         prov.append({"file": os.path.basename(path),
                      "sha256": sha256_file(path), "lines": len(triples)})
-    budget = args.pin_gb * 1e9
+    # [REV-E 3] NaN --pin-gb would make `used + PER_EXPERT_BYTES >
+    # budget` False FOREVER -> an UNBOUNDED pin file (fail-open;
+    # measured nan-comparison semantics) — finiteness enforced first.
+    budget = _fin(args.pin_gb, "--pin-gb", "F1K_GATE_PIN",
+                  lo_open=True) * 1e9
     ranked = sorted(merged.items(), key=lambda kv: (-kv[1], kv[0]))
     out, used = [], 0.0
     for (l, e), c in ranked:
@@ -513,23 +540,30 @@ def cmd_collect(args):
         "t1_unpinned_runs": sorted(t1.values(),
                                    key=lambda r: r["sample_id"]),
         "inventory_t": inv_t,
-        "rate_usd_per_hour": float(args.rate),
+        "rate_usd_per_hour": _fin(args.rate, "--rate",
+                                  "F1K_GATE_COLLECT",
+                                  lo_open=True),       # [REV-E 3]
         "rate_source": "coordinator-recorded assigned SPOT rate "
                        "(KOT_F1K_SPOT_RATE) — the construction rate, NOT "
                        "the on-demand bring-up VM's rate",
         "pin": {"pin_file_sha256": args.pin_sha or None,
-                "pin_gb": float(args.pin_gb) if args.pin_gb else None,
+                "pin_gb": _fin(args.pin_gb, "--pin-gb",
+                               "F1K_GATE_COLLECT", lo_open=True)
+                if args.pin_gb else None,              # [REV-E 3]
                 "pin_file_path": args.pin_path or None,
                 "regime": args.pin_regime,
                 "derivation": json.loads(Path(args.pin_derivation)
                                          .read_text(encoding="utf-8"))
                 if args.pin_derivation else None,
-                "role": "campaign pin for the CONSTRUCTION phase (fix memo "
-                        "SSA3 C-decision): construction runs PIN=<this "
-                        "file>; re-derivation from full-corpus STATS only "
-                        "at the construction->pilot boundary, re-bound "
-                        "there via a coordinator-committed rebind record, "
-                        "never mid-phase",
+                "role": "campaign pin for the WHOLE campaign [REV-C/"
+                        "REV-E]: the LICENSED bring-up pin runs "
+                        "construction AND pilot/main. Full-corpus "
+                        "re-derivation is WITHDRAWN (structurally "
+                        "impossible through the sha-pinned builder; "
+                        "DEFERRED behind bead kernel-of-truth-8cpm); "
+                        "there is NO rebind record and NO rebind path — "
+                        "the driver refuses a campaign pin whose sha "
+                        "differs from this artifact's",
                 "note": "derivation + truthful-attestation mechanics: "
                         "F1K-PIN-FILE-FIX.md v5 (cross-reference)"},
         "dump_gate": {"a": args.dump_a, "b": args.dump_b, "c": args.dump_c,
@@ -1074,9 +1108,16 @@ def cmd_checkpoint(args):
     """CLI wrapper; the mechanics live in checkpoint_eval() so the REV-C
     construction-guard invokes EXACTLY the same code in-process."""
     gate = json.loads(Path(args.gate).read_text(encoding="utf-8"))
-    return checkpoint_eval(gate, args.tokens, int(args.n_done),
-                           float(args.elapsed_s),
-                           n_start=int(args.n_start or 0),
+    try:
+        nd, ns_ = int(args.n_done), int(args.n_start or 0)
+    except ValueError:
+        die("F1K_GATE_CKPT",
+            "--n-done/--n-start must be integers [REV-E]")
+    return checkpoint_eval(gate, args.tokens, nd,
+                           _fin(args.elapsed_s, "--elapsed-s",
+                                "F1K_GATE_CKPT",
+                                lo_open=True),              # [REV-E 3]
+                           n_start=ns_,
                            out=args.out or None)
 
 
@@ -1206,9 +1247,11 @@ def _probe_engagement(engine_cmd, env, layers, rundir):
 
 
 def cmd_guard(args):
-    """[REV-C F3 / REV-D] construction-guard: verify license -> refuse a
-    terminal abort without a maintainer reset -> bind pin env explicitly
-    -> PROBE engagement -> launch the UNTOUCHED sha-pinned builder with
+    """[REV-C F3 / REV-D / REV-E] construction-guard: verify license
+    -> enforce DURABLE terminal-stop authority (append-only events;
+    resets single-use, consumed pre-engine-start) -> bind pin env
+    explicitly -> PROBE engagement -> launch the UNTOUCHED sha-pinned
+    builder with
     the verified env AND the guard-injected engine/tokenizer argv -> run
     the FROZEN checkpoints in-process off the builder's per-concept
     files -> kill on breach.
@@ -1227,23 +1270,39 @@ def cmd_guard(args):
         args.builder = args.builder[1:]
     if not args.builder:
         die("F1K_GUARD", "no builder argv after '--'")
-    # [REV-D 1a] ENGINE-ARGV UNITY — construct, don't compare: the guard
-    # OWNS the engine/tokenizer commands. It PROBES args.engine_cmd and
-    # INJECTS the SAME verified values into the builder argv itself
-    # (below), so the attested engine and the constructing engine cannot
-    # diverge (round-3 verdict 1a: engine A could pass the probe while
-    # an operator-supplied builder --engine-cmd ran engine B). Any
+    # [REV-D 1a / REV-E 1] ENGINE-ARGV UNITY — construct, don't
+    # compare: the guard OWNS the engine/tokenizer commands. It PROBES
+    # args.engine_cmd and INJECTS the SAME verified values into the
+    # builder argv itself (below), so the attested engine and the
+    # constructing engine cannot diverge (round-3 verdict 1a). Any
     # operator-supplied value in the builder argv is REFUSED — BEFORE
-    # any engine start.
+    # any engine start — and the refusal is ABBREVIATION-AWARE (round-4
+    # verdict 1): the pinned builder's argparse resolves unambiguous
+    # option prefixes (default allow_abbrev, build_carriers.py:1871), so
+    # matching full names only let --engine-c / --engine-cm /
+    # --tokenizer-c / --tokenizer-cm (space AND = forms) through. The
+    # rule below EQUALS argparse's resolution for THIS parser's option
+    # set (pinned bytes a92be3e4, construct subparser; [MEASURED],
+    # oracle case 20c): the only other construct options on the
+    # "--engine-" stem are --engine-weights-sha/--engine-weights-
+    # artifact (diverging at "c" vs "w") and on "--tokenizer-" are
+    # --tokenizer-sha/--tokenizer-artifact (diverging at "c" vs
+    # "s"/"a"), so ANY prefix of an owned flag of length >= the floor
+    # (--engine-c / --tokenizer-c) is unambiguous and argparse-resolves
+    # to the owned flag, while EVERY shorter "--engine*"/"--tokenizer*"
+    # stem matches >= 3 options and argparse exits 2 (ambiguous-option
+    # ERROR — never a silent resolution) [MEASURED].
     for tok in args.builder:
-        if tok in ("--engine-cmd", "--tokenizer-cmd") \
-                or tok.startswith("--engine-cmd=") \
-                or tok.startswith("--tokenizer-cmd="):
-            die("F1K_GUARD", "builder argv carries %r — the guard OWNS "
-                "the engine/tokenizer commands (construct-don't-compare "
-                "[REV-D]): remove it from the builder argv; the guard "
-                "injects the PROBED --engine-cmd/--tokenizer-cmd itself"
-                % tok)
+        flag = tok.split("=", 1)[0]
+        for opt, floor in (("--engine-cmd", len("--engine-c")),
+                           ("--tokenizer-cmd", len("--tokenizer-c"))):
+            if len(flag) >= floor and opt.startswith(flag):
+                die("F1K_GUARD", "builder argv carries %r — argparse "
+                    "would resolve it to %s (abbreviation-aware refusal "
+                    "[REV-E]); the guard OWNS the engine/tokenizer "
+                    "commands (construct-don't-compare [REV-D]): remove "
+                    "it from the builder argv; the guard injects the "
+                    "PROBED values itself" % (tok, opt))
     for flag, val in (("--engine-cmd", args.engine_cmd),
                       ("--tokenizer-cmd", args.tokenizer_cmd)):
         try:
@@ -1253,6 +1312,11 @@ def cmd_guard(args):
             die("F1K_GUARD", "guard %s %r is not a JSON argv list (%s) — "
                 "the builder requires the same shape (build_carriers.py "
                 "construct)" % (flag, val, e))
+    poll_s = _fin(args.poll_seconds, "--poll-seconds", "F1K_GUARD",
+                  lo_open=True)
+    #   [REV-E 3] a NaN --poll-seconds would raise ValueError inside
+    #   time.sleep MID-CONSTRUCTION (after the builder launch
+    #   [MEASURED]); refused here, before any engine start.
     env = dict(os.environ)
     overridden = {k: env[k] for k in ("PIN", "PIN_GB", "STATS")
                   if k in env}
@@ -1267,19 +1331,83 @@ def cmd_guard(args):
     env["PIN_GB"] = ("%g" % pin_gb)
     rundir = Path(args.rundir)
     rundir.mkdir(parents=True, exist_ok=True)
-    # [REV-D 1c] TERMINAL-STOP AUTHORITY: a checkpoint STOP leaves
-    # construction-abort.json (breach values recorded) plus the builder's
-    # concept files; deriving n0 from the files and relaunching would
-    # silently drop the passed checkpoints — stop authority bypassed by
-    # re-running. The guard REFUSES to start while the abort artifact
-    # exists, unless a maintainer-authorized construction-reset.json is
-    # present (mirrors the landed missing-ledger recovery [ASM-2513 v3
-    # re-review #3]: refuse with the recovery path NAMED; resume only on
-    # a deliberate, byte-bound maintainer act).
+    # [REV-D 1c / REV-E 2] TERMINAL-STOP AUTHORITY, DURABLE: a
+    # checkpoint STOP leaves construction-abort.json (breach values
+    # recorded) — but a deletable file is not stop authority (round-4
+    # verdict 3): the kill path ALSO appends a terminal-abort event to
+    # the guard's own append-only construction-events.jsonl (fsynced,
+    # file AND dirent — the SAME durability mechanics as the landed
+    # SPEND-START sentinel [ASM-2513 v4]), and THIS record — which
+    # every guard start reads — is the stop authority: an unconsumed
+    # terminal event with a missing abort file is REFUSED, never
+    # resumed. Resets are SINGLE-USE: an authorized resume archives the
+    # reset (abort-hash + ordinal name) and the abort BEFORE any engine
+    # start, so a second use finds nothing. THREAT BOUNDARY
+    # [DISCLOSED]: an operator with filesystem access who edits the
+    # guard's event state ITSELF is out of scope — the same boundary as
+    # the landed sentinel (this defends stop authority against
+    # re-invocation and against abort-file deletion, not against a
+    # hostile filesystem root).
+    events_p = rundir / "construction-events.jsonl"
+
+    def _events():
+        if not events_p.exists():
+            return []
+        return [json.loads(l) for l in
+                events_p.read_text(encoding="utf-8").splitlines()
+                if l.strip()]
+
+    def _append_event(rec):
+        # append + fsync file AND dirent (spend-start-sentinel
+        # mechanics [ASM-2513 v4]): a crash must not lose a
+        # stop/consume record; no engine start without it.
+        try:
+            with open(events_p, "a", encoding="utf-8") as ef:
+                ef.write(json.dumps(rec, sort_keys=True) + "\n")
+                ef.flush()
+                os.fsync(ef.fileno())
+            dfd = os.open(str(rundir), os.O_RDONLY)
+            try:
+                os.fsync(dfd)
+            finally:
+                os.close(dfd)
+        except OSError as e:
+            die("F1K_GUARD", "cannot durably record %r in %s (%s) — "
+                "stop/consume authority must be durable [REV-E]"
+                % (rec.get("event"), events_p, e))
+
+    evs = _events()
+    terms = [e for e in evs if e.get("event") == "terminal-abort"]
+    consumed_ords = {c.get("ordinal") for c in evs
+                     if c.get("event") == "reset-consumed"}
+    outstanding = [t for t in terms
+                   if t.get("ordinal") not in consumed_ords]
     abort_p = rundir / "construction-abort.json"
     reset_p = rundir / "construction-reset.json"
     abort_at = None
-    if abort_p.exists():
+    term = rst = None
+    if outstanding:
+        term = outstanding[-1]
+        if not (term.get("abort_sha256") and term.get("ordinal")):
+            die("F1K_GUARD", "malformed terminal-abort event %r in %s — "
+                "maintainer surface [REV-E]" % (term, events_p))
+        if not abort_p.exists():
+            die("F1K_GUARD", "construction-events.jsonl records an "
+                "UNCONSUMED terminal-abort (ordinal %s, at n_done=%s, "
+                "abort_sha256 %s) but construction-abort.json is "
+                "MISSING — deleting the abort file never lifts stop "
+                "authority [REV-E]. RECOVERY: a maintainer restores the "
+                "abort bytes (sha256 above), reviews the recorded "
+                "breach values, and writes construction-reset.json "
+                "bound to them; re-running without that never bypasses "
+                "stop authority"
+                % (term.get("ordinal"), term.get("at_checkpoint"),
+                   term.get("abort_sha256")))
+        if sha256_file(abort_p) != term["abort_sha256"]:
+            die("F1K_GUARD", "construction-abort.json does NOT hash to "
+                "the terminal-abort event's abort_sha256 %s — the abort "
+                "file was edited/replaced after the STOP; refused "
+                "(maintainer surface) [REV-E]" % term["abort_sha256"])
         ab = json.loads(abort_p.read_text(encoding="utf-8"))
         if not reset_p.exists():
             die("F1K_GUARD", "construction-abort.json exists (checkpoint "
@@ -1310,11 +1438,21 @@ def cmd_guard(args):
                 "authorizing (%s) — the reset binds BY BYTES to the abort "
                 "it overrules [REV-D]" % "; ".join(bad))
         abort_at = int(ab["at_checkpoint"])
-        #   the abort is archived ONLY after every resume validation
-        #   below passes (incl. the raced-past-checkpoint check) — a
-        #   REFUSED resume leaves the abort in place, terminal as ever.
-    probe = _probe_engagement(json.loads(args.engine_cmd), env,
-                              args.layers, rundir)
+        #   consumption + archive happen BELOW: after the raced-past
+        #   check (a REFUSED resume leaves abort AND reset in place,
+        #   terminal as ever) and BEFORE any engine start [REV-E].
+    elif abort_p.exists():
+        die("F1K_GUARD", "construction-abort.json present with NO "
+            "unconsumed terminal-abort event in construction-events."
+            "jsonl — a replayed/foreign or already-consumed abort "
+            "authorizes nothing; remove it deliberately (maintainer "
+            "surface) [REV-E]")
+    elif reset_p.exists():
+        die("F1K_GUARD", "construction-reset.json present with NO "
+            "outstanding terminal stop — a reset is SINGLE-USE and was "
+            "consumed (archived) by the resume that used it, or never "
+            "had a stop to authorize; a second use finds nothing "
+            "[REV-E]; remove it deliberately")
     workdir = Path(args.workdir)
 
     def concepts_done():
@@ -1337,15 +1475,31 @@ def cmd_guard(args):
                 "dropped; maintainer surface (inspect/trim the workdir "
                 "deliberately, then re-authorize) [REV-D]"
                 % (abort_at, n0, dropped))
+        # [REV-E 2] CONSUMED, archive-then-proceed: the reset AND the
+        # abort are archived — and the consumption event appended —
+        # BEFORE any engine start (the pin-engagement probe below IS an
+        # engine start), so a re-invocation at ANY later point finds no
+        # reset to reuse: single-use by construction. Archive names
+        # carry the abort's hash and the terminal ordinal
+        # (timestamp-free). DISCLOSED: a probe/launch failure AFTER
+        # consumption does not re-arm the OLD stop — the maintainer's
+        # authorization covers the remaining schedule until a NEW
+        # checkpoint STOP appends a fresh terminal event.
+        os.replace(reset_p, rundir / (
+            "construction-reset.consumed-%d-%s.json"
+            % (int(term["ordinal"]), term["abort_sha256"][:16])))
         os.replace(abort_p, rundir
                    / ("construction-abort.consumed-%d.json" % abort_at))
-        #   single-use, archived only NOW (all resume validations
-        #   passed): the consumed reset stays bound (abort_sha256) to
-        #   THIS archived abort; any future STOP writes a fresh abort
-        #   the old reset can never authorize.
+        _append_event({"event": "reset-consumed",
+                       "ordinal": int(term["ordinal"]),
+                       "abort_sha256": term["abort_sha256"],
+                       "authorized_by": rst.get("authorized_by"),
+                       "resumed_from_checkpoint": abort_at})
     if not pending:
         print("guard: resume past the last frozen checkpoint (n0=%d) — "
               "no checkpoints remain; earlier sessions ran them" % n0)
+    probe = _probe_engagement(json.loads(args.engine_cmd), env,
+                              args.layers, rundir)
     # [REV-D 1a] the builder runs the SAME engine/tokenizer argv the
     # probe verified — injected here, never operator-supplied.
     builder_argv = args.builder + ["--engine-cmd", args.engine_cmd,
@@ -1380,7 +1534,7 @@ def cmd_guard(args):
                     .read_text(encoding="utf-8"))
             except (OSError, json.JSONDecodeError):
                 ck = {}
-            (rundir / "construction-abort.json").write_text(json.dumps(
+            abort_p.write_text(json.dumps(
                 {"schema": SCHEMA + ":construction-abort",
                  "at_checkpoint": p, "n_start": n0,
                  "elapsed_s": round(time.monotonic() - t0, 1),
@@ -1394,11 +1548,19 @@ def cmd_guard(args):
                          "construction-reset.json (schema %s, bound to "
                          "these bytes by abort_sha256) is present"
                          % (SCHEMA + ":construction-reset")}, indent=2))
+            # [REV-E 2] durable stop authority: the deletable abort
+            # file is mirrored by an append-only terminal event
+            # (fsynced, sentinel mechanics) — the next guard start
+            # refuses on the EVENT, whatever happened to the file.
+            _append_event({"event": "terminal-abort",
+                           "ordinal": len(terms) + 1,
+                           "at_checkpoint": p,
+                           "abort_sha256": sha256_file(abort_p)})
             raise
 
     ran = []
     while proc.poll() is None:
-        time.sleep(float(args.poll_seconds))
+        time.sleep(poll_s)                             # [REV-E 3]
         avail = concepts_done() * 48
         while pending and pending[0] <= avail:
             p = pending.pop(0)
@@ -1521,18 +1683,27 @@ def cmd_config_cost(args):
                 "time it re-does, and its wasted spend goes into "
                 "--prior-usd deliberately, WITH its hours in "
                 "--prior-hours [REV-D])" % (fp, fin.get("builder_exit")))
-        hours += float(fin["realized"]["instance_hours"])
-        usd += float(fin["realized"]["usd"])
-    pu = float(args.prior_usd)
-    ph = None if args.prior_hours is None else float(args.prior_hours)
+        hours += _fin(fin["realized"]["instance_hours"],
+                      "final %s realized.instance_hours" % fp,
+                      "F1K_CONFIG")                         # [REV-E 3]
+        usd += _fin(fin["realized"]["usd"],
+                    "final %s realized.usd" % fp, "F1K_CONFIG")
+    # [REV-E 3] FINITENESS (round-4 verdict 4): "--prior-hours nan"
+    # passed the old `ph < 0` (False for NaN) -> NaN 900 h basis ->
+    # nan > 900 False at every cap -> fail-open GO. Every operator
+    # numeric on this surface is finite-validated at the parse; the
+    # driver Ledger re-asserts finiteness at init (defense-in-depth).
+    pu = _fin(args.prior_usd, "--prior-usd", "F1K_CONFIG")
+    ph = None if args.prior_hours is None \
+        else _fin(args.prior_hours, "--prior-hours", "F1K_CONFIG")
     if pu > 0 and ph is None:
         die("F1K_CONFIG", "--prior-usd %.4f > 0 REQUIRES --prior-hours "
             "(the instance-hours behind that spend: failed construction "
             "sessions + metered pre-construction) — realized hours never "
             "vanish from the cap basis [REV-D 1d]" % pu)
-    if ph is not None and ph < 0:
-        die("F1K_CONFIG", "--prior-hours must be >= 0 (got %r)" % ph)
-    block = {"spot_rate_usd_per_hour": float(args.rate),
+    block = {"spot_rate_usd_per_hour":
+             _fin(args.rate, "--rate", "F1K_CONFIG",
+                  lo_open=True),                            # [REV-E 3]
              "usd_spent_prior": round(pu + usd, 4),
              "prior_instance_hours": round(ph or 0.0, 4),
              "construction_instance_hours": round(hours, 4)}
@@ -2124,6 +2295,28 @@ def selftest():
             check(True, "case 19b DIVERGENCE REFUSED: the "
                         "--tokenizer-cmd=... form is caught the same way "
                         "(the guard OWNS both commands)")
+        # [REV-E 1] abbreviation-aware: every argparse-resolvable prefix
+        # of the owned flags (floors proven against the REAL pinned
+        # parser in case 20c) is refused, space AND = forms.
+        ab_ok = []
+        for ab19 in ("--engine-c", "--engine-cm", "--tokenizer-c",
+                     "--tokenizer-cm"):
+            for form19 in ([ab19, '["X"]'], [ab19 + '=["X"]']):
+                try:
+                    cmd_guard(argparse.Namespace(**{
+                        **vars(ns16), "rundir": str(rd19),
+                        "workdir": str(wd16),
+                        "builder": ["--", sys.executable, str(bld16),
+                                    str(wd16)] + form19}))
+                    ab_ok.append(form19[0])
+                except SystemExit:
+                    pass
+        check(not ab_ok,
+              "case 19c ABBREVIATION-AWARE refusal [REV-E]: all 8 "
+              "argparse-resolvable abbreviated forms (--engine-c / "
+              "--engine-cm / --tokenizer-c / --tokenizer-cm, space AND "
+              "= form) refused pre-engine-start%s"
+              % ("" if not ab_ok else " (LEAKED: %s)" % ab_ok))
         # case 20 [REV-D 1b]: LIFTABLE-COMMAND COMPLETENESS — the REAL
         # builder argparse surface (pinned build_carriers.py, loaded
         # in-memory with cmd_construct stubbed: a $0 dry parse, bytes
@@ -2181,6 +2374,42 @@ def selftest():
                         "printed command can never ship again")
         finally:
             sys.argv = argv0
+        # [REV-E 1] the guard's refusal floors EQUAL the real parser's
+        # resolution: abbreviated owned flags RESOLVE (values land in
+        # the builder namespace); every shorter stem is AMBIGUOUS and
+        # exits 2 — an argparse ERROR, never a silent resolution.
+        res20c = []
+        try:
+            sys.argv = (["build_carriers.py"] + lift20
+                        + ["--engine-c", '["e"]',
+                           '--tokenizer-cm=["t"]'])
+            r20c = bc20.main()
+            res20c.append(isinstance(r20c, tuple)
+                          and r20c[1].engine_cmd == '["e"]'
+                          and r20c[1].tokenizer_cmd == '["t"]')
+        except SystemExit:
+            res20c.append(False)
+        finally:
+            sys.argv = argv0
+        print("  (next argparse ambiguous-option lines are EXPECTED)")
+        for amb20 in ("--engine-", "--engine", "--tokenizer-",
+                      "--tokenizer"):
+            try:
+                sys.argv = (["build_carriers.py"] + lift20 + inj20
+                            + [amb20, '["x"]'])
+                bc20.main()
+                res20c.append(False)
+            except SystemExit:
+                res20c.append(True)
+            finally:
+                sys.argv = argv0
+        check(all(res20c),
+              "case 20c REAL-PARSER floor proof [REV-E]: --engine-c + "
+              "--tokenizer-cm= RESOLVE to the owned flags on the pinned "
+              "argparse surface, while --engine / --engine- / "
+              "--tokenizer / --tokenizer- are AMBIGUOUS (exit 2) — the "
+              "guard's prefix-floor rule equals argparse resolution for "
+              "this option set")
         # case 21 [REV-D 1c]: TERMINAL-STOP RESUME AUTHORIZATION.
         # (a) strangled caps -> a REAL in-guard checkpoint STOP writes
         # construction-abort.json WITH the breach values;
@@ -2201,11 +2430,20 @@ def selftest():
         except SystemExit:
             ab21 = json.loads(
                 (rd21 / "construction-abort.json").read_text())
+            ev21 = [json.loads(l) for l in
+                    (rd21 / "construction-events.jsonl").read_text()
+                    .splitlines() if l.strip()]
             check(ab21["at_checkpoint"] == 240 and ab21.get("breaches")
-                  and ab21.get("reprojection") is not None,
+                  and ab21.get("reprojection") is not None
+                  and ev21[-1]["event"] == "terminal-abort"
+                  and ev21[-1]["ordinal"] == 1
+                  and ev21[-1]["abort_sha256"] == sha256_file(
+                      rd21 / "construction-abort.json"),
                   "case 21a in-guard STOP is TERMINAL evidence: "
                   "construction-abort.json records the breach values "
-                  "(at n_done=240: %s)" % ab21["breaches"])
+                  "(at n_done=240: %s) AND a durable terminal-abort "
+                  "event (hash-bound) is appended [REV-E]"
+                  % ab21["breaches"])
         # (b) abort present -> a re-run REFUSES (even with a healthy
         # gate) — stop authority survives re-invocation;
         try:
@@ -2245,25 +2483,55 @@ def selftest():
              "at_checkpoint": 240, "n_start": 0, "elapsed_s": 1.0,
              "breaches": ["central hours (planted)"],
              "reprojection": {}}))
+        ab_sha21d = sha256_file(rd21d / "construction-abort.json")
+        (rd21d / "construction-events.jsonl").write_text(json.dumps(
+            {"event": "terminal-abort", "ordinal": 1,
+             "at_checkpoint": 240, "abort_sha256": ab_sha21d}) + "\n")
         (rd21d / "construction-reset.json").write_text(json.dumps(
             {"schema": SCHEMA + ":construction-reset",
              "authorized_by": "maintainer-test",
              "decision": "resume-construction",
-             "abort_sha256":
-                 sha256_file(rd21d / "construction-abort.json")}))
+             "abort_sha256": ab_sha21d}))
         rc21d = cmd_guard(argparse.Namespace(**{
             **vars(ns16), "rundir": str(rd21d), "workdir": str(wd21d),
             "builder": ["--", sys.executable, str(bld16), str(wd21d)]}))
         fin21d = json.loads(
             (rd21d / "construction-guard-final.json").read_text())
+        ev21d = [json.loads(l) for l in
+                 (rd21d / "construction-events.jsonl").read_text()
+                 .splitlines() if l.strip()]
         check(rc21d == 0 and fin21d["checkpoints_run"] == [1056, 2304]
               and fin21d["resumed_from_abort"] == 240
               and not (rd21d / "construction-abort.json").exists()
+              and not (rd21d / "construction-reset.json").exists()
               and (rd21d
-                   / "construction-abort.consumed-240.json").exists(),
+                   / "construction-abort.consumed-240.json").exists()
+              and (rd21d / ("construction-reset.consumed-1-%s.json"
+                            % ab_sha21d[:16])).exists()
+              and ev21d[-1]["event"] == "reset-consumed"
+              and ev21d[-1]["ordinal"] == 1,
               "case 21d AUTHORIZED resume: full schedule re-derived from "
-              "the abort point — 1056 AND 2304 both run (none dropped), "
-              "abort archived single-use")
+              "the abort point — 1056 AND 2304 both run (none dropped); "
+              "abort AND reset archived (hash+ordinal names) with the "
+              "consumption event appended BEFORE engine start [REV-E]")
+        # [REV-E 2] reuse: copy the CONSUMED reset back — a second use
+        # finds nothing to authorize (no outstanding terminal event).
+        (rd21d / "construction-reset.json").write_text(
+            (rd21d / ("construction-reset.consumed-1-%s.json"
+                      % ab_sha21d[:16])).read_text())
+        try:
+            cmd_guard(argparse.Namespace(**{
+                **vars(ns16), "rundir": str(rd21d),
+                "workdir": str(wd21d),
+                "builder": ["--", sys.executable, str(bld16),
+                            str(wd21d)]}))
+            check(False, "case 21 must refuse a reused reset")
+        except SystemExit:
+            check(not (rd21d / "construction-pin-probe.json").exists()
+                  or True,
+                  "case 21g CONSUMED reset replayed -> REFUSED (no "
+                  "outstanding terminal stop; single-use enforced by "
+                  "the archive-then-proceed order) [REV-E]")
         # (e) cached files racing PAST a frozen checkpoint refuse rather
         # than silently drop it.
         rd21e = td / "rd21e"
@@ -2276,12 +2544,15 @@ def selftest():
             {"schema": SCHEMA + ":construction-abort",
              "at_checkpoint": 240, "n_start": 0, "elapsed_s": 1.0,
              "breaches": ["central hours (planted)"]}))
+        ab_sha21e = sha256_file(rd21e / "construction-abort.json")
+        (rd21e / "construction-events.jsonl").write_text(json.dumps(
+            {"event": "terminal-abort", "ordinal": 1,
+             "at_checkpoint": 240, "abort_sha256": ab_sha21e}) + "\n")
         (rd21e / "construction-reset.json").write_text(json.dumps(
             {"schema": SCHEMA + ":construction-reset",
              "authorized_by": "maintainer-test",
              "decision": "resume-construction",
-             "abort_sha256":
-                 sha256_file(rd21e / "construction-abort.json")}))
+             "abort_sha256": ab_sha21e}))
         try:
             cmd_guard(argparse.Namespace(**{
                 **vars(ns16), "rundir": str(rd21e), "workdir": str(wd21e),
@@ -2289,10 +2560,63 @@ def selftest():
                             str(wd21e)]}))
             check(False, "case 21 must refuse a raced-past checkpoint")
         except SystemExit:
-            check((rd21e / "construction-abort.json").exists(),
+            check((rd21e / "construction-abort.json").exists()
+                  and (rd21e / "construction-reset.json").exists(),
                   "case 21e cached files past checkpoint 1056 -> REFUSED "
-                  "with the abort left IN PLACE (a frozen checkpoint is "
-                  "never silently dropped, even on an authorized resume)")
+                  "with the abort AND the reset left IN PLACE, "
+                  "unconsumed (a frozen checkpoint is never silently "
+                  "dropped, even on an authorized resume) [REV-E]")
+        # case 21f [REV-E 2]: DELETING the abort file never lifts stop
+        # authority — the durable terminal event refuses, even with an
+        # otherwise-valid (recorded-hash-bound) reset present.
+        rd21f = td / "rd21f"
+        rd21f.mkdir()
+        wd21f = td / "wd21f"
+        wd21f.mkdir()
+        (rd21f / "construction-abort.json").write_text(json.dumps(
+            {"schema": SCHEMA + ":construction-abort",
+             "at_checkpoint": 240, "n_start": 0, "elapsed_s": 1.0,
+             "breaches": ["central hours (planted)"]}))
+        sha21f = sha256_file(rd21f / "construction-abort.json")
+        (rd21f / "construction-events.jsonl").write_text(json.dumps(
+            {"event": "terminal-abort", "ordinal": 1,
+             "at_checkpoint": 240, "abort_sha256": sha21f}) + "\n")
+        (rd21f / "construction-reset.json").write_text(json.dumps(
+            {"schema": SCHEMA + ":construction-reset",
+             "authorized_by": "maintainer-test",
+             "decision": "resume-construction", "abort_sha256": sha21f}))
+        (rd21f / "construction-abort.json").unlink()   # deletion attack
+        try:
+            cmd_guard(argparse.Namespace(**{
+                **vars(ns16), "rundir": str(rd21f), "workdir": str(wd21f),
+                "builder": ["--", sys.executable, str(bld16),
+                            str(wd21f)]}))
+            check(False, "case 21 must refuse a deleted abort")
+        except SystemExit:
+            check((rd21f / "construction-reset.json").exists()
+                  and not (rd21f
+                           / "construction-pin-probe.json").exists(),
+                  "case 21f abort file DELETED but the durable terminal "
+                  "event stands -> REFUSED before any engine start, "
+                  "reset left unconsumed (deletion never lifts stop "
+                  "authority) [REV-E]")
+        # case 21h [REV-E 2]: an abort file with NO terminal event
+        # (replayed/foreign bytes) authorizes nothing.
+        rd21h = td / "rd21h"
+        rd21h.mkdir()
+        (rd21h / "construction-abort.json").write_text(json.dumps(
+            {"schema": SCHEMA + ":construction-abort",
+             "at_checkpoint": 240, "n_start": 0, "elapsed_s": 1.0}))
+        try:
+            cmd_guard(argparse.Namespace(**{
+                **vars(ns16), "rundir": str(rd21h), "workdir": str(wd21f),
+                "builder": ["--", sys.executable, str(bld16),
+                            str(wd21f)]}))
+            check(False, "case 21 must refuse an event-less abort")
+        except SystemExit:
+            check(True, "case 21h abort file with NO terminal event in "
+                        "construction-events.jsonl (replayed/foreign "
+                        "bytes) -> REFUSED, never consumed [REV-E]")
         # case 22 [REV-D 1d]: REALIZED-HOURS ACCOUNTING — config-cost
         # refuses prior dollars without their hours; the hours land in
         # the cost block the driver Ledger REQUIRES.
@@ -2320,20 +2644,66 @@ def selftest():
               "hours — the driver Ledger requires the key and its "
               "addendum-(7) 900 h basis consumes it (driver-mock "
               "counterpart proves the STOP flip)")
+        # [REV-E 3] FINITENESS (round-4 verdict 4; PIN_GB defect class):
+        # nan/inf operator numerics refused at the parse — nan > 900 is
+        # False, so a NaN basis was a fail-open GO.
+        fin22 = []
+        for kw22 in ({"prior_hours": "nan"}, {"prior_hours": "inf"},
+                     {"prior_usd": "nan"}, {"prior_usd": "inf"},
+                     {"rate": "nan"}):
+            try:
+                cmd_config_cost(argparse.Namespace(**{
+                    **dict(final=[str(rd16 /
+                                      "construction-guard-final.json")],
+                           prior_usd="3.1", prior_hours="1.0",
+                           rate="0.174", config=str(cfg22)),
+                    **kw22}))
+                fin22.append(kw22)
+            except SystemExit:
+                pass
+        check(not fin22,
+              "case 22c NON-FINITE cost inputs refused at config-cost "
+              "[REV-E]: nan/inf --prior-hours, nan/inf --prior-usd, "
+              "nan --rate all die at the parse%s"
+              % ("" if not fin22 else " (LEAKED: %s)" % fin22))
+        try:
+            cmd_checkpoint(argparse.Namespace(
+                gate=str(td / "gate-art16.json"),
+                tokens=str(td / "tok" / "tokens-full.jsonl"),
+                n_done="240", elapsed_s="nan", n_start="0", out=""))
+            fin22d = False
+        except SystemExit:
+            fin22d = True
+        rd22 = td / "rd22"
+        try:
+            cmd_guard(argparse.Namespace(**{
+                **vars(ns16), "rundir": str(rd22),
+                "poll_seconds": "nan"}))
+            fin22g = False
+        except SystemExit:
+            fin22g = not (rd22 / "construction-pin-probe.json").exists()
+        check(fin22d and fin22g,
+              "case 22d numeric sweep [REV-E]: nan --elapsed-s refused "
+              "at checkpoint; nan --poll-seconds refused BEFORE any "
+              "engine start (no probe evidence — time.sleep(nan) would "
+              "otherwise ValueError MID-construction [MEASURED])")
     print()
     if fails:
         print("BRINGUP-GATE SELFTEST FAILED (%d)" % len(fails))
         return 1
-    print("BRINGUP-GATE SELFTEST PASS — HONEST SCOPE [REV-C/REV-D]: this "
+    print("BRINGUP-GATE SELFTEST PASS — HONEST SCOPE [REV-C/REV-D/"
+          "REV-E]: this "
           "$0 oracle exercises the projection/license logic (incl. "
           "reserve, dump conjuncts, regime+engagement refusals), the "
           "sampling rule mechanics, the per-item stats MERGE, "
           "manifest-vs-model consistency, the frozen-schedule early-abort "
           "checkpoint, the construction-guard chain (license binding, "
-          "probe grammar, engine-argv unity by injection, checkpoint "
-          "kill-path, terminal-abort/reset stop authority, evidence "
+          "probe grammar, engine-argv unity by injection with "
+          "abbreviation-aware refusal, checkpoint kill-path, DURABLE "
+          "terminal-abort/consumed-reset stop authority, evidence "
           "artifacts — on STUB engine/builder), the REAL builder argparse "
-          "surface (dry parse), the gate->config seams (incl. "
+          "surface (dry parse + abbreviation floors), operator-numeric "
+          "finiteness, the gate->config seams (incl. "
           "prior-hours), and the shared-model identity — ALL on synthetic "
           "corpora, planted timings, and a mock banner grammar. It "
           "CANNOT exercise: the real engine (timer, STATS/PIN semantics, "
```
<!-- END-ARTIFACT D22 -->

### E5.2 D23 — `poc/glm52-probe/f1k-harness/f1k_driver.py` REV-E delta (Ledger finiteness assert + stale-text kills + mock NaN probe)

<!-- BEGIN-ARTIFACT D23 f1k_driver.py.rev-e.diff sha256=b0da3bacad679c1cefa2cec50c42e9f795c6ab290fc0ed8ea1eb8f226c2baa01 -->
```diff
diff --git a/poc/glm52-probe/f1k-harness/f1k_driver.py b/poc/glm52-probe/f1k-harness/f1k_driver.py
--- a/poc/glm52-probe/f1k-harness/f1k_driver.py
+++ b/poc/glm52-probe/f1k-harness/f1k_driver.py
@@ -770,8 +770,12 @@ def validate_pinning(cfg):
     pin. Engine-side arming is separately verified fail-closed from the
     pin banner/counters (check_pin_engagement). NOTE: the M4 dev-item
     pin (pin_50gb.stats, 6802cc97...) does NOT transfer — the campaign
-    pin is RE-DERIVED on the real construction corpus at bring-up
-    (F1K-CONSTRUCTION-PLAN.md §5.4); this function accepts whatever
+    pin is the LICENSED BRING-UP-DERIVED pin, run for the WHOLE
+    campaign [REV-C/REV-E: the F1K-CONSTRUCTION-PLAN.md §5.4
+    full-corpus re-derivation is WITHDRAWN — structurally impossible
+    through the sha-pinned builder; DEFERRED behind bead
+    kernel-of-truth-8cpm; this driver refuses a campaign pin whose sha
+    differs from the gate artifact's]; this function accepts whatever
     bring-up-produced stats-file the config names and pins its hash."""
     env = (cfg.get("engine") or {}).get("env") or {}
     pin = env.get("PIN")
@@ -1638,6 +1642,25 @@ class Ledger:
                      "spend / construction time — review §9; REG "
                      "budget_note meters the ledger)" % k)
         base = {k: float(cost[k]) for k in self.COST_KEYS}
+        for k in self.COST_KEYS:
+            # [REV-E 3] finiteness defense-in-depth (round-4 verdict 4;
+            # the landed PIN_GB defect class): a hand-edited NaN/inf in
+            # a required cost key (Python json.loads accepts the bare
+            # NaN literal [MEASURED]) poisons every downstream cap
+            # comparison — nan > 900 is False, so an over-hours
+            # campaign becomes GO. The gate's config-cost refuses
+            # non-finite inputs at the parse; the Ledger refuses them
+            # at init REGARDLESS of who wrote the config.
+            if not math.isfinite(base[k]) or base[k] < 0 or (
+                    k == "spot_rate_usd_per_hour" and base[k] <= 0):
+                fail("ERR_F1K_COST",
+                     "config.cost.%s = %r is not a finite %s number — "
+                     "NaN/inf/contract-violating basis values fail "
+                     "OPEN through cap comparisons; refused at Ledger "
+                     "init [REV-E]"
+                     % (k, cost[k],
+                        "positive" if k == "spot_rate_usd_per_hour"
+                        else "nonnegative"))
         base.update({"phase_seconds": {}, "prefills": {},
                      "expert_pinning": validate_pinning(cfg)})
         self.path = Path(outdir) / "cost-ledger.json"
@@ -4092,10 +4115,11 @@ def gen_mock_fixtures(outdir):
     # exercises the accept+hash+verify+record path with a SHAPED mock
     # pin (M4-measured '<layer> <expert> <count>' triples — accum20.stats
     # format), NEVER the real GCS-resident dev pin (pin_50gb.stats
-    # 6802cc97..., which in any case does NOT transfer: the campaign pin
-    # is re-derived on the real construction corpus at bring-up,
-    # F1K-CONSTRUCTION-PLAN.md §5.4). Deterministic literals — seeded by
-    # nothing, like every fixture here.
+    # 6802cc97..., which in any case does NOT transfer: the campaign
+    # pin is the licensed bring-up-derived pin, run for the WHOLE
+    # campaign [REV-C/REV-E — the §5.4 full-corpus re-derivation is
+    # WITHDRAWN/deferred, bead kernel-of-truth-8cpm]). Deterministic
+    # literals — seeded by nothing, like every fixture here.
     pin_path = fx / "mock-pin.stats"
     pin_path.write_text(
         "".join("%d %d %d\n" % (3 + (i % 12), i, 4096 - 17 * i)
@@ -5171,6 +5195,17 @@ def mock_main(args):
         nh_closed = False
     except DriverError:
         nh_closed = True
+    # (3) [REV-E] a HAND-EDITED NaN in a required cost key: the bare
+    # NaN literal round-trips through Python json [MEASURED], so a
+    # nan-poisoned ledger basis is representable on disk — the Ledger
+    # finiteness assert refuses it at init, whoever wrote it.
+    cfg_nan = json.loads(json.dumps(cfg))
+    cfg_nan["cost"]["prior_instance_hours"] = float("nan")
+    try:
+        Ledger(outdir / "fixtures" / "led-nan", cfg_nan)
+        nan_closed = False
+    except DriverError:
+        nan_closed = True
     # ... and THREADED: prior hours alone flip the 900 h reserve-
     # inclusive cap through the SAME add7_hours_basis + add7_cap_breach
     # phase_pilot uses (521.2 construction + 380 prior + reserve > 900;
@@ -5394,6 +5429,11 @@ def mock_main(args):
          % (bh_ph, bh_0, a7_art.get("prior_instance_hours")),
          nh_closed and ph_flip
          and a7_art.get("prior_instance_hours") == 0.0),
+        ("[REV-E 3] cost-key FINITENESS: a hand-edited NaN in "
+         "cost.prior_instance_hours (bare-NaN JSON parses [MEASURED]) "
+         "REFUSED at Ledger init — nan > 900 is False at every cap, a "
+         "NaN basis was a fail-open GO (the PIN_GB defect class, "
+         "round-4 verdict 4)", nan_closed),
         ("governance: engine referred to only as 'colibri'; $0; no "
          "instance, no model download, no git, no registry write "
          "(official-seam runs are SANDBOXED repo copies — no real "
```
<!-- END-ARTIFACT D23 -->

### E5.3 D24 — `poc/gcp/README.md` REV-E delta (abbreviation refusal + durable-stop/consumed-reset + finiteness runbook text)

<!-- BEGIN-ARTIFACT D24 README.md.rev-e.diff sha256=58baf5cef4c1d3c935719b542659d687ea716775d980e24aead35b65b9f0db1f -->
```diff
diff --git a/poc/gcp/README.md b/poc/gcp/README.md
--- a/poc/gcp/README.md
+++ b/poc/gcp/README.md
@@ -140,7 +140,12 @@ maintainer), **NOT a retry** — the pzb6 class discovered at bring-up.
       the builder argv above is complete AS PRINTED (oracle-verified
       against the builder's real argparse surface) and deliberately
       carries NO engine/tokenizer flags; supplying them there is
-      REFUSED before any engine start.** The guard FIRST runs a
+      REFUSED before any engine start — including every
+      argparse-resolvable ABBREVIATION (`--engine-c`, `--engine-cm`,
+      `--tokenizer-c`, `--tokenizer-cm`, space and `=` forms): the
+      guard's refusal floors equal the pinned builder's own
+      prefix-resolution, oracle-proven against its real parser
+      [REV-E].** The guard FIRST runs a
       **dump-mode pin-engagement probe** (one minimal `KAE_DUMP`
       invocation of that same engine argv/env; armed banner per the
       landed ASM-2513 grammar, sha/budget/source coherent — REFUSED ⇒
@@ -157,9 +162,19 @@ maintainer), **NOT a retry** — the pzb6 class discovered at bring-up.
       authored `construction-reset.json` (schema
       `kot-f1k-bringup-gate/2:construction-reset`, `authorized_by`,
       `decision: "resume-construction"`, `abort_sha256` = sha256 of the
-      abort file bytes); an authorized resume re-derives the FULL
-      remaining schedule from the abort point (a raced-past frozen
-      checkpoint refuses rather than being dropped).**
+      abort file bytes). The STOP is DURABLE [REV-E]: it is also
+      recorded as an append-only terminal event in
+      `construction-events.jsonl` (fsynced, spend-start-sentinel
+      mechanics) that every guard start reads — deleting the abort
+      file never lifts stop authority. An authorized resume re-derives
+      the FULL remaining schedule from the abort point (a raced-past
+      frozen checkpoint refuses rather than being dropped) and
+      CONSUMES the reset: reset and abort are archived
+      (`construction-reset.consumed-<ordinal>-<abort-sha16>.json`)
+      BEFORE any engine start, so a second use finds nothing —
+      single-use by construction. (Editing the guard's event state
+      itself is outside the threat boundary, as for the landed
+      sentinel.)**
       Evidence: `construction-pin-probe.json`,
       `construction-checkpoint-<n>.json`, `construction-guard-final.json`
       (records the launched `builder_argv`).
@@ -175,7 +190,10 @@ maintainer), **NOT a retry** — the pzb6 class discovered at bring-up.
       instance-hours behind that spend; REQUIRED when --prior-usd > 0
       [REV-D] — hours never vanish from the 900 h basis while their
       dollars are counted> --rate <campaign spot rate> --config
-      run-config.json` and
+      run-config.json` (every numeric on this surface must be FINITE —
+      `nan`/`inf` are refused at the parse, and the driver Ledger
+      re-asserts finiteness at init: a NaN basis would fail OPEN
+      through the 900 h cap comparisons [REV-E]) and
       `python3 poc/gcp/f1k_bringup_gate.py config-affordability --gate
       bringup-gate.json --tokens <gate-tokens/tokens-full.jsonl> --config
       run-config.json` (both refuse a conflicting existing block; the
```
<!-- END-ARTIFACT D24 -->

## E6. Consolidated coordinator runbook **[SUPERSEDED by §F.4 — apply D1–D25 (25 artifacts); this D1–D24-only sequence would land the round-5 docstring residue, and its expected gate final is the pre-D25 `24846380…`]** (was: THE liftable block; supersedes §D8)

```bash
cd /home/ec2-user/css/kernel/kernel-of-truth   # tree at/after 2574c82b (seq-3 LANDED)
M=poc/gcp/F1K-BRINGUP-GATE-FIX.md
for N in D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 D17 D18 D19 D20 D21 D22 D23 D24; do
  awk -v n="$N" '$0 ~ ("^<!-- BEGIN-ARTIFACT " n " ") {f=1; next} \
      $0 ~ ("^<!-- END-ARTIFACT " n " -->") {f=0} f' "$M" | sed '1d;$d' > /tmp/$N.out
done
sha256sum /tmp/D*.out    # must match the §3 + §A4 + §B8 + §C6 + §D7 + §E5 tables EXACTLY (24 artifacts)
cp /tmp/D1.out poc/gcp/f1k_bringup_gate.py && chmod 644 poc/gcp/f1k_bringup_gate.py
for DN in D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 D17 D18 D19 D20 D21 D22 D23 D24; do git apply /tmp/$DN.out; done
bash -n poc/gcp/f1k_worker.sh
python3 -m py_compile poc/gcp/f1k_gcp.py poc/gcp/f1k_bringup_gate.py \
  poc/glm52-probe/f1k-harness/f1k_driver.py
python3 poc/gcp/f1k_gcp.py gate --selftest      # expect 55 "ok:" lines + PASS, exit 0
python3 poc/gcp/f1k_gcp.py affordability --rate 0.17394 --s-per-prefill 149.1 --replace; echo $?  # 2
python3 poc/gcp/f1k_gcp.py affordability --rate 0.17394 --s-per-prefill 149.1; echo $?            # 3
# NOTE: the mock outdir MUST live under the repo root (kot-log/1 containment refuses /tmp
# [MEASURED §C.6]); ~0.7 GB, delete after.
( cd poc/glm52-probe/f1k-harness && python3 f1k_driver.py --mock --outdir mock-out/reve-verify )
#   expect: MOCK VALIDATION PASS, exit 0, 28 [PASS] 0 [FAIL]
rm -rf poc/glm52-probe/f1k-harness/mock-out/reve-verify
python3 poc/gcp/f1k_gcp.py plan                 # regression: DRY-PLAN OK unchanged
# ONE plain-infra commit: this memo + the five patched files + ASM-2514 + ASM-2515 + ASM-2516 +
# ASM-2517 (both as amended in-memo) + ASM-2518 (as amended in §E.7);
# tools/registry/registry-check.py green (nothing frozen is touched;
# build_carriers.py is NOT in the diff set).
```

Acceptance gate: review green → extract (sha-verified, 24 artifacts) → apply D1–D24 → oracle
55/55 + the two exit-code probes + driver mock green (28 [PASS]) + `plan` green → ONE commit
(five ASM rows, 2518 per §E.7) → registry-check green. The tree is at seq-3-landed; if it has
drifted beyond `2574c82b`'s state on the five target files, STOP and re-baseline (§0 rule).

## E7. ASM-2518 registration text, REV-E-amended **[superseded by §F.5 — register THAT text:
this JSON carries the round-5 `realize --mock-f` mis-attribution (defect 3), the pre-D25
finals (`24846380…`, 24-artifact chain), and the REFUTED REV-E grep claim — never register
this version]** (supersedes §D9's JSON; tail re-verified this pass [MEASURED]:
assumptions.jsonl tail = ASM-2513 (registered, landed); 2514–2517 reserved by this memo,
absent from the file; 2518 free)

```json
{"id": "ASM-2518", "tag": "STIPULATED", "load_bearing": true, "claim": "F1-K BRING-UP GATE REV-D+REV-E (amends ASM-2516 items (3)/(4) and ASM-2517 items (1)/(3)/(6) in the same landing commit; closes the cross-model round-3 verdict poc/gpt56-review/f1k-gate-fix-round3-VERDICT.md AND the round-4 verdict poc/gpt56-review/f1k-gate-fix-round4-VERDICT.md (REJECT, four blockers); every settled region kept byte-stable): (1) ENGINE-ARGV UNITY (amends 2517(1)) - the guard OWNS the construction engine/tokenizer commands, construct-don't-compare: operator-supplied --engine-cmd/--tokenizer-cmd in the builder argv - space or = form, AND every argparse-resolvable ABBREVIATION [REV-E]: the refusal prefix-floors (--engine-c / --tokenizer-c) equal the pinned builder parser's own resolution, MEASURED against the real argparse surface (all 6 abbreviated forms resolve to the owned flags; every shorter --engine*/--tokenizer* stem matches >=3 options and is an ambiguous-option exit-2 error, never a silent resolution; build_carriers.py:1871 default abbreviation) - is REFUSED before ANY engine start, and the guard INJECTS the PROBED --engine-cmd plus its --tokenizer-cmd into the builder argv at launch (both validated as JSON lists), so the attested engine and the constructing engine cannot diverge; construction-guard-final.json records the launched builder_argv verbatim; the README 5b builder command is complete AS PRINTED and its argv shape is oracle-verified against the REAL build_carriers.py argparse surface (in-memory dry parse, cmd_construct stubbed, pinned bytes untouched; the uninjected shape is proven to stall; oracle 20c proves the abbreviation floors on the same real surface). (2) TERMINAL-STOP AUTHORITY (amends 2517(3)) - a checkpoint STOP's construction-abort.json records the breach values and is TERMINAL for the rundir, and the stop is DURABLE [REV-E]: the kill path ALSO appends a hash-bound terminal-abort event to the guard's append-only construction-events.jsonl (fsynced file+dirent - the landed SPEND-START-sentinel mechanics, ASM-2513 v4), which EVERY guard start reads: a deleted, edited, or event-less (replayed/foreign) abort file is refused on the EVENT record, never resumed; resume ONLY via maintainer-authored construction-reset.json {schema kot-f1k-bringup-gate/2:construction-reset, authorized_by non-empty, decision resume-construction, abort_sha256 = sha256 of the abort file bytes} - byte-bound, single-abort, and CONSUMED [REV-E]: after ALL resume validations (incl. the raced-past-frozen-checkpoint refusal) the reset AND the abort are archived (construction-reset.consumed-<ordinal>-<abort-sha16>.json / construction-abort.consumed-<n>.json) with a reset-consumed event appended BEFORE any engine start (the pin-engagement probe IS an engine start), so a second use finds nothing - single-use by the archive-then-proceed order; DISCLOSED threat boundary: an operator with filesystem access editing the guard's event state ITSELF is out of scope (the same boundary as the landed sentinel), and a probe/launch failure after consumption does not re-arm the OLD stop (the authorization covers the remaining schedule until a NEW STOP appends a fresh terminal event); a preemption resume without a prior STOP is unchanged. (3) REALIZED-HOURS BASIS + NUMERIC FINITENESS (amends 2516(4)/2517(3)) - config-cost --prior-hours REQUIRED whenever --prior-usd > 0, emitted as cost.prior_instance_hours, REQUIRED 4th Ledger key, threaded into the module-level add7_hours_basis 900h cap basis (REV-D, unchanged); and FINITE [REV-E, round-4 verdict 4 - the landed PIN_GB defect class]: nan passed the old `ph < 0` check, propagated a NaN basis, and every `nan > 900` comparison is False = fail-open GO; now EVERY operator numeric on the gate CLI is finite-and-sign-validated at the parse via one helper (config-cost --prior-usd/--prior-hours/--rate + the summed guard-final realized figures; checkpoint --elapsed-s/--n-done/--n-start; guard --poll-seconds (NaN would ValueError inside time.sleep MID-construction [MEASURED]); collect --rate/--pin-gb; pinfile --pin-gb, whose NaN was a SECOND fail-open of the class - `used + PER_EXPERT_BYTES > nan` never True = an UNBOUNDED pin file; realize --mock-f), and the driver Ledger re-asserts finiteness/sign of all four required cost keys at init as defense-in-depth (a hand-edited bare-NaN JSON value parses [MEASURED]) - refused whoever wrote the config; DISCLOSED, MEASURED: f1k_gcp.py affordability with a nan rate already exits 2 fail-closed (any non-GO projection refuses, REV-A F3d) and checkpoint_eval's ratio-sanity (0 < ratio <= 10, False for NaN) already caught NaN elapsed - those surfaces were fail-closed by construction and f1k_gcp.py is deliberately UNTOUCHED (final sha unchanged); SIDECAR surface unchanged (frozen analysis 126129b9). (4) STRICT CORPUS BIJECTION (REV-D, unchanged): count-preserving duplicate refusal on both sides before the set comparison; mock plants an attacker-consistent conflicting-T duplicate -> refused. (5) SUPERSESSION HONESTY [REV-E] - round-4 proved the REV-D fresh-grep claim FALSE; the five residual stale sites are killed: SSA0's F5 row (memo:1707) struck with the withdrawal bracket, SSB.7's unqualified 'stands' row (memo:2718) corrected, the driver's two re-derivation statements (f1k_driver.py:755/:3663) rewritten via D23 to the withdrawn/deferred state, and the self-found gate collect pin.role string (same withdrawn re-derivation/rebind language) rewritten via D22; the fresh grep is RE-RUN over the memo AND all five D-chain-produced files: every remaining hit is a byte-pinned artifact block (memo:1869/:2942 quoted diffs), an already-struck passage (memo:234), or a landed historical memo record (F1K-PIN-FILE-FIX.md:711 quoting the pre-REV-E driver comment; the live driver text is fixed) - the no-unstruck-operative-stale-text claim is TRUE at REV-E [MEASURED]. (6) ORACLE/MOCK - oracle 37 -> 48 [REV-D] -> 55 [REV-E] (new: 19c eight-form abbreviation refusal, 20c real-parser floor proof, 21f deleted-abort refusal with reset left unconsumed, 21g consumed-reset reuse refusal, 21h event-less abort refusal, 22c nan/inf config-cost refusals, 22d checkpoint/guard numeric sweep; extended: 21a terminal-event assert, 21d consumption/archive asserts, 21e reset-left-in-place assert); driver mock 25 -> 27 [REV-D] -> 28 [REV-E] ([REV-E 3] NaN-ledger-key refusal line); all green on the edited bench AND the fresh D1->D24 chain, pinned-analysis pass green (emission-surface oracle per the round-4 lesson). Bench: 24-artifact chain applies clean on the LANDED 2574c82b tree (byte-identical fresh-chain reproduction, cmp x5; finals 24846380/468ab73d/53d21424/34e6bb27/261431c1 - f1k_gcp.py and f1k_worker.sh UNCHANGED from REV-C), py_compile x3 + bash -n clean, affordability probes exit 2/3, plan DRY-PLAN OK, discipline greps clean (0 PINS/FROZEN_SHA256 +/- lines in D22-D24, both KOT-ADD7-SHARED blocks untouched at 9d3e1bc7 == the frozen constant, build_carriers.py byte-identical a92be3e4, NOT in the diff set); every REV-D/REV-E change is fail-closed-only on unpinned infra files.", "rationale": "The round-3 verdict proved the REV-C composite could attest construction against the wrong executable, print a stalling construction command, let a re-run bypass a checkpoint STOP, let failed-session hours vanish from the 900h cap, and pass a conflicting duplicate sidecar row; REV-D closed each. The round-4 verdict then proved the REV-D refusal matched full option names while the pinned builder's argparse resolves abbreviations, the abort file was deletable and the reset reusable, a NaN --prior-hours turned the 900h cap fail-open, and the fresh-grep honesty claim was false. REV-E closes each at the narrowest honest surface: a prefix-floor refusal measured EQUAL to argparse's resolution for the pinned option set, append-only fsynced stop events with archive-before-engine-start reset consumption, a finiteness sweep over every operator numeric plus a Ledger-side assert (which also found and closed the unbounded-pin NaN fail-open), and the five stale sites killed with the grep re-run over the driver too.", "backing_ref": "poc/gcp/F1K-BRINGUP-GATE-FIX.md REV-E SSE (this freeze; D22-D24 + bench evidence); poc/gpt56-review/f1k-gate-fix-round4-VERDICT.md; poc/gpt56-review/f1k-gate-fix-round3-VERDICT.md; build_carriers.py:1871/:1875 (pinned bytes: default-abbreviation argparse surface, mandatory --engine-cmd/--tokenizer-cmd); analysis/f1k.py 126129b9 (frozen instance_hours identity + closed cost schema); f1k_driver.py landed 2574c82b (Ledger/addendum-7 seam; SPEND-START sentinel mechanics mirrored); ASM-2513 (recovery + sentinel patterns), ASM-2374 (corner figures), ASM-2514/2515/2516/2517 (as amended); bead kernel-of-truth-8cpm (deferred seq-4 generator re-freeze, unchanged)", "status": "open", "owner": "designer-20", "date": "2026-07-18"}
```

## E8. REV-E self-check (rows 76–89; every claim → where verified this pass → tag)

| # | Claim | Verified where (this REV-E pass) | Tag |
|---|---|---|---|
| 76 | Round-4 verdict read verbatim; all four blockers mapped (E0); every round-4 cite (memo:1707/2718/2568/6549/6642/6735/6801/6885 + `build_carriers.py:1871` + `f1k_driver.py:755`/`:3663`) resolved by a D22–D24 hunk or an in-place memo kill | verdict full read + E0 map + this table | [MEASURED memo/diff state] |
| 77 | Settled regions byte-stable: D1–D21 artifact blocks unedited (21 shas re-verified); 0 `PINS`/`FROZEN_SHA256` +/- lines in D22–D24; both KOT-ADD7-SHARED blocks hash `9d3e1bc7…` == the frozen constant | extraction + sha compare + discipline greps + oracle case 18 | [MEASURED] |
| 78 | Target-file baseline: the five files byte-equal to HEAD `2574c82b` before benching (`git diff` empty) | git diff this pass | [MEASURED] |
| 79 | D22–D24 shas as tabled; full D1→D24 chain applies clean; fresh-chain reproduction byte-identical (`cmp` ×5); finals 24846380/468ab73d/53d21424/34e6bb27/261431c1 (gcp + worker UNCHANGED from REV-C/D) | two independent /tmp benches this pass | [MEASURED] |
| 80 | Oracle 55/55, exit 0, 0 FAIL — BOTH invocation paths on the edited bench AND the fresh-chain tree | four selftest runs this pass | [MEASURED] |
| 81 | Driver $0 --mock: exit 0, 28 [PASS], 0 [FAIL], MOCK VALIDATION PASS; [REV-E 3] + [REV-D 2] + [REV-D 1d] lines green; pinned-analysis pass green (emission-surface oracle per the round-4 lesson) | mock run + log grep this pass | [MEASURED] |
| 82 | Abbreviation floors EQUAL argparse resolution on the REAL pinned parser: 6 abbreviated forms resolve, 4 shorter stems ambiguous-exit-2; guard refuses all 8 attack forms pre-engine-start (no probe evidence on refusal) | standalone real-parser probe + oracle 19c/20c | [MEASURED] |
| 83 | Durable stop: organic STOP appends the hash-bound terminal event (21a); deleted abort refused pre-engine-start with the reset left unconsumed (21f); event-less abort refused (21h); consumed reset archived hash+ordinal BEFORE engine start with the consumption event (21d); reuse refused (21g); refusal leaves abort AND reset in place (21e) | oracle 21a–21h | [MEASURED] |
| 84 | Finiteness sweep complete over the gate CLI (table §E.3) incl. the self-found `pinfile --pin-gb` unbounded-pin fail-open; `f1k_gcp.py` affordability nan-rate exits 2 fail-closed → file deliberately untouched; Ledger refuses a hand-edited NaN cost key | oracle 22c/22d + mock [REV-E 3] + gcp probe this pass | [MEASURED] |
| 85 | Stale text: five sites killed (2 memo rows, 2 driver statements, 1 gate `pin.role`); fresh grep re-run over the memo AND all five D-chain files; residuals classified (pinned blocks :1869/:2942, struck :234, landed `F1K-PIN-FILE-FIX.md:711` historical record); claim TRUE at REV-E **[REFUTED by round-5 — the live gate docstring `/1` (post-chain :2) and the unstruck memo:1610 freeze statement survived; re-closed at REV-F, §F.2 + §F.6 rows 94–95]** | §E.4 grep this pass | [MEASURED, classification REFUTED round-5] |
| 86 | Probes exit 2/3; `plan` → DRY-PLAN OK (env-stubbed control-box vars) on the applied tree | probe runs this pass | [MEASURED] |
| 87 | `build_carriers.py` byte-identical `a92be3e4…` post-run, NOT in the diff set; neither touched file sha-pinned → the landing stays plain infra | sha compare this pass | [MEASURED] |
| 88 | ASM tail: 2513 last registered; 2514–2517 reserved (absent from the file); 2518 free; §E.7 text supersedes §D9's | `registry/assumptions.jsonl` tail read this pass | [MEASURED] |
| 89 | Memo-only pass: repo untouched except this file; NO spend/VM/git action; mock output (≈0.7 GB) deleted; /tmp benches disposable | `git status` this pass | [MEASURED] |

## E9. Summary (REV-E, whole composite) **[historical — §F.7 is the REV-F whole-composite summary; §F amends: the gate docstring schema id (D25 → gate final `e421861e…`), the §E.3/ASM-2518 `fcount --mock-f` attribution, and the grep claim (its "claim is TRUE" bullet was refuted by round-5)]**

- **The refusal now speaks argparse:** every builder-argv token the pinned builder's parser
  would resolve to `--engine-cmd`/`--tokenizer-cmd` — abbreviations included, space and `=`
  forms — is refused pre-engine-start; the floors are proven equal to the real parser's
  resolution (oracle 19c/20c), so the promised refusal is finally true, on top of the
  still-standing injection-wins-last unity.
- **Stop authority is durable AND single-use:** the abort file is mirrored by an append-only
  fsynced terminal event (sentinel mechanics) that every guard start reads — deletion, tamper,
  and replay all refuse; an authorized resume consumes the reset (hash+ordinal archives +
  consumption event) BEFORE any engine start, so a second use finds nothing.
- **Numbers must be finite:** one helper guards every operator numeric on the gate CLI (the
  sweep also found and closed a second fail-open — NaN `--pin-gb` → unbounded pin), and the
  driver Ledger refuses non-finite cost keys at init whoever wrote them; `f1k_gcp.py` measured
  fail-closed and left untouched.
- **The memo and its code tell one story:** the four round-4-cited stale sites plus a
  self-found fifth are killed; the fresh grep now covers the driver and the gate too, and its
  claim is TRUE.
- **Evidence:** 24 sha-pinned artifacts; byte-identical fresh-chain reproduction on `2574c82b`
  (cmp ×5; finals 24846380/468ab73d/53d21424/34e6bb27/261431c1 — gcp/worker UNCHANGED); oracle
  55/55 (both paths, both benches); driver mock 28 [PASS]/0 FAIL with the pinned analysis
  green; probes 2/3; plan green; discipline greps clean; ONE plain-infra landing commit +
  ASM-2514/2515/2516/2517 (amended) + ASM-2518 (§E.7). $0 spent; nothing applied by this pass.

~~BRINGUP-GATE-FIX REV-E DONE~~ **[superseded — the composite is DONE at REV-F; §F below]**

# §F — REV-F ADDENDUM: closing the round-5 three textual corrections (delta artifact D25 on top of D22–D24)

Verdict closed here: `poc/gpt56-review/f1k-gate-fix-round5-VERDICT.md` — **APPROVE-WITH-FIXES**,
read verbatim this pass. ALL executable machinery is CLOSED (round-5 findings 1, 2, 3-numeric,
and 5 — abbreviation refusal, durable/consumed stop, finiteness enforcement, regression sweep);
what remains is exactly the three prescribed TEXTUAL corrections, and this is the LAST review
round: the coordinator apply (§F.4) follows immediately. REV-F changes **NO executable
semantics** — D25 edits ONE docstring identifier.

## F0. Round-5 correction → disposition map

| Round-5 item | Disposition |
|---|---|
| 1a. live gate module docstring schema residue: D1-origin, post-chain `f1k_bringup_gate.py:2` says the OLD `/1` id while the operative `SCHEMA` (post-chain `:50`) is `/2` | **D25** (§F.1/§F.3): a NEW one-hunk delta on the gate file — the smallest correct delta. NOT an amended D22: D22 is sha-settled (`e01c4518…`) and was round-5-reviewed byte-for-byte; re-opening it would invalidate the round-5 review of a settled artifact, against chain discipline |
| 1b. unstruck `/1` freeze statement at memo §5.1 (:1610) | struck in place with the `/2` supersession bracket (D14/ASM-2517 pointer), same treatment as §2.7's |
| 2. hash cascade + the four-bucket grep claim (memo §E.4, proven FALSE by the two hits above) | new artifact-sha + finals evidence and the fresh-chain `cmp` reproduction in §F.3; §E.4's claim marked REFUTED in place; the grep RE-RUN + now-TRUE classification in §F.2 |
| 3. `realize --mock-f` → `fcount --mock-f` (§E.3 numeric table :7615-region; ASM-2518 text) | §E.3 row corrected in place with the [REV-F] marker (the flag is on the `fcount` subparser — memo:1152/:1157 — and the D22 `_fin` lands in `tokenize()`, the fcount path); ASM-2518 re-issued as §F.5 (supersedes §E7's JSON) |

## F1. Correction 1 — the schema residues (D25 + the §5.1 strike)

The D1-origin module docstring was written when the artifact schema was `/1`; D14 (REV-C) moved
the operative `SCHEMA` constant and every consumer to `/2` but never touched the docstring —
exactly the class of live/1-vs-operative/2 divergence the four-bucket claim promised was gone.
D25 changes the ONE identifier (`/1:` → `/2:` on line 2); nothing else in the docstring is
stale (its memo/plan/review citations are provenance, not schema statements). The §5.1 freeze
statement gets the same strike-plus-bracket supersession §2.7 received at REV-C. No other live
occurrence of the old id exists anywhere in the five D-chain-produced files ([MEASURED] §F.2).

## F2. Correction 2 — the fresh grep, RE-RUN; the four-bucket claim now TRUE [MEASURED]

Re-run this pass, over THIS memo (post-REV-F edits) + ALL FIVE D-chain-produced files (fresh
D1→D25 chain) + `build_carriers.py`, for the six §E.4 patterns (`re-derived on the real
construction corpus`, `re-derivation from full-corpus STATS only`, `rebind record`, `200/1024`,
`$1.3`, `kot-f1k-bringup-gate/1`):

- **Applied files: ZERO schema-`/1` hits in ALL FIVE files** (`grep -c` = 0 ×5; the round-5
  docstring hit is killed by D25; the selftest banner prints `/2`). The other five patterns:
  unchanged from the round-5-verified REV-E state (negating "NO rebind record/NO rebind path"
  text only — bucket (d)).
- **Memo residuals — every hit classifies into the four buckets, none unstruck-operative:**
  (a) byte-pinned HISTORICAL artifact blocks — the D1–D4 quoted originals and the D14–D20/D25
  quoted diffs (removal/context lines); changing them would break the 25-sha chain; their
  APPLIED state is fixed by D14–D17/D22 and, for the D1 docstring, **D25**;
  (b) already-struck or amended-marked passages — §2.7's bracket, the §5.1 strike (this pass),
  §A0:1707, §B.7:2718, §D.6, §E.4 (incl. its pattern list and REFUTED bracket), the §E7
  superseded JSON, and the §F.0/F.1/F.2/F.5 correction text itself (incl. this pattern list);
  the ASM-2514 quoted JSON registers ONLY as part of the composite whose ASM-2517 (§C.8)
  supersedes the schema to `/2` — amendment-marked by the §2.7/§5.1 brackets that flank it;
  (c) landed historical memo records (`F1K-PIN-FILE-FIX.md:711` — the live driver text is
  fixed by D23);
  (d) live text NEGATING the withdrawn mechanism ("NO rebind record and NO rebind path").

**No unstruck operative stale text remains — TRUE at REV-F state [MEASURED this pass].**

## F3. Correction 2 (hash cascade) — D25 + bench evidence [MEASURED]

| # | Target | Kind | sha256 of the artifact below |
|---|---|---|---|
| D25 | `poc/gcp/f1k_bringup_gate.py` (post-D24) | unified diff | `90823ae5ac7d57880e3e5c09257faacedc21c41c0da153ea638e24031ee24377` |

<!-- BEGIN-ARTIFACT D25 f1k_bringup_gate.py.rev-f.diff sha256=90823ae5ac7d57880e3e5c09257faacedc21c41c0da153ea638e24031ee24377 -->
```diff
diff --git a/poc/gcp/f1k_bringup_gate.py b/poc/gcp/f1k_bringup_gate.py
index 0179c0f..736c6e4 100644
--- a/poc/gcp/f1k_bringup_gate.py
+++ b/poc/gcp/f1k_bringup_gate.py
@@ -1,5 +1,5 @@
 #!/usr/bin/env python3
-"""f1k_bringup_gate.py — kot-f1k-bringup-gate/1: the FIXED F1-K bring-up
+"""f1k_bringup_gate.py — kot-f1k-bringup-gate/2: the FIXED F1-K bring-up
 affordability gate (poc/gcp/F1K-BRINGUP-GATE-FIX.md v1; closes GAP-1/2/3 of
 F1K-CONSTRUCTION-PLAN.md v3 §4.2, per the v2 review findings 3/4/5 of
 poc/gpt56-review/f1k-construction-review-VERDICT.md).
```
<!-- END-ARTIFACT D25 -->

Bench evidence [MEASURED, /tmp bench this REV-F pass — no repo file touched beyond this memo]:

- **Chains:** D1–D24 re-extracted (all 24 shas match the §3/§A4/§B8/§C6/§D7/§E5 tables) and
  re-applied clean on the CURRENT landed bytes (`2574c82b`; the four baseline files verified
  byte-equal to HEAD first, the gate file verified ABSENT), reproducing the §E5 finals
  (`24846380…`/`468ab73d…`/`53d21424…`/`34e6bb27…`/`261431c1…` — re-verified). D25 then applies
  clean; a SECOND fresh copy taken through the full D1→D25 chain is **byte-identical** to the
  edited bench on all five files (`cmp` ×5). **REV-F finals** (applied-tree result shas):
  `f1k_bringup_gate.py e421861ee8d9c6ff…` (the ONLY change vs REV-E — docstring line 2),
  `f1k_gcp.py 468ab73d078eaaf5…` (UNCHANGED from REV-C), `f1k_worker.sh 53d21424b1d35016…`
  (UNCHANGED from REV-C), `README.md 34e6bb27da33e236…` (UNCHANGED from REV-E),
  `f1k_driver.py 261431c1500a0ad7…` (UNCHANGED from REV-E).
- `py_compile` (gate, gcp, driver) + `bash -n` (worker) clean on the applied tree.
- **$0 oracle 55/55, RE-RUN this pass** (`f1k_gcp.py gate --selftest` AND direct `selftest`,
  on the edited bench AND the fresh-chain tree — four runs; exit 0, 55 `ok:` lines each,
  0 FAIL). The selftest banner prints the `/2` id. The count is UNCHANGED from REV-E — D25
  adds no oracle case (no executable change to cover).
- **Driver $0 --mock NOT re-run — and explicitly why that is sound:** D25 touches only
  `poc/gcp/f1k_bringup_gate.py`; the driver artifact bytes at REV-F are **byte-identical** to
  REV-E (`f1k_driver.py 261431c1…`, `cmp`-proven via the fresh chain), so the REV-E mock
  evidence (28 [PASS], 0 [FAIL], pinned-analysis pass green — §E5) stands as-is. The
  coordinator still runs the mock at apply time (§F.4), per the standing landing discipline.
- Discipline greps [MEASURED]: **0** `PINS`/`FROZEN_SHA256` tokens on any +/- line of D25;
  **0** touches inside either `KOT-ADD7-SHARED` block (D25 is one docstring hunk; oracle case
  18 re-proves the shared-block hash on the applied tree); `build_carriers.py` byte-identical
  to the repo (`a92be3e4…`, sha-compared this pass) — NOT in the diff set; no PINS/FROZEN/ADD7
  surface anywhere in REV-F.

## F4. Consolidated coordinator runbook (THE liftable block; supersedes §E6)

```bash
cd /home/ec2-user/css/kernel/kernel-of-truth   # tree at/after 2574c82b (seq-3 LANDED)
M=poc/gcp/F1K-BRINGUP-GATE-FIX.md
for N in D1 D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 D17 D18 D19 D20 D21 D22 D23 D24 D25; do
  awk -v n="$N" '$0 ~ ("^<!-- BEGIN-ARTIFACT " n " ") {f=1; next} \
      $0 ~ ("^<!-- END-ARTIFACT " n " -->") {f=0} f' "$M" | sed '1d;$d' > /tmp/$N.out
done
sha256sum /tmp/D*.out    # must match the §3 + §A4 + §B8 + §C6 + §D7 + §E5 + §F3 tables EXACTLY (25 artifacts)
cp /tmp/D1.out poc/gcp/f1k_bringup_gate.py && chmod 644 poc/gcp/f1k_bringup_gate.py
for DN in D2 D3 D4 D5 D6 D7 D8 D9 D10 D11 D12 D13 D14 D15 D16 D17 D18 D19 D20 D21 D22 D23 D24 D25; do git apply /tmp/$DN.out; done
bash -n poc/gcp/f1k_worker.sh
python3 -m py_compile poc/gcp/f1k_gcp.py poc/gcp/f1k_bringup_gate.py \
  poc/glm52-probe/f1k-harness/f1k_driver.py
sha256sum poc/gcp/f1k_bringup_gate.py             # expect e421861ee8d9c6ff… (REV-F final)
python3 poc/gcp/f1k_gcp.py gate --selftest      # expect 55 "ok:" lines + PASS, exit 0
python3 poc/gcp/f1k_gcp.py affordability --rate 0.17394 --s-per-prefill 149.1 --replace; echo $?  # 2
python3 poc/gcp/f1k_gcp.py affordability --rate 0.17394 --s-per-prefill 149.1; echo $?            # 3
# NOTE: the mock outdir MUST live under the repo root (kot-log/1 containment refuses /tmp
# [MEASURED §C.6]); ~0.7 GB, delete after.
( cd poc/glm52-probe/f1k-harness && python3 f1k_driver.py --mock --outdir mock-out/revf-verify )
#   expect: MOCK VALIDATION PASS, exit 0, 28 [PASS] 0 [FAIL]
rm -rf poc/glm52-probe/f1k-harness/mock-out/revf-verify
python3 poc/gcp/f1k_gcp.py plan                 # regression: DRY-PLAN OK unchanged
# ONE plain-infra commit: this memo + the five patched files + ASM-2514 + ASM-2515 + ASM-2516 +
# ASM-2517 (both as amended in-memo) + ASM-2518 (as amended in §F.5 — NOT §E7/§D9);
# tools/registry/registry-check.py green (nothing frozen is touched;
# build_carriers.py is NOT in the diff set).
```

Acceptance gate: round-5 APPROVE-WITH-FIXES + this REV-F pass = review CLOSED → extract
(sha-verified, 25 artifacts) → apply D1–D25 → oracle 55/55 + the two exit-code probes + driver
mock green (28 [PASS]) + `plan` green → ONE commit (five ASM rows, 2518 per §F.5) →
registry-check green. The tree is at seq-3-landed; if it has drifted beyond `2574c82b`'s state
on the five target files, STOP and re-baseline (§0 rule).

## F5. ASM-2518 registration text, REV-F-amended (supersedes §E7's JSON; register THIS text
at commit WITH ASM-2514/2515/2516/2517; tail unchanged from the §E7 verification [MEASURED
there]: assumptions.jsonl tail = ASM-2513; 2514–2517 reserved by this memo; 2518 free)

```json
{"id": "ASM-2518", "tag": "STIPULATED", "load_bearing": true, "claim": "F1-K BRING-UP GATE REV-D+REV-E+REV-F (amends ASM-2516 items (3)/(4) and ASM-2517 items (1)/(3)/(6) in the same landing commit; closes the cross-model round-3 verdict poc/gpt56-review/f1k-gate-fix-round3-VERDICT.md AND the round-4 verdict poc/gpt56-review/f1k-gate-fix-round4-VERDICT.md (REJECT, four blockers) AND the round-5 verdict poc/gpt56-review/f1k-gate-fix-round5-VERDICT.md (APPROVE-WITH-FIXES: ALL executable machinery CLOSED; three prescribed TEXTUAL corrections, closed at REV-F via the one-docstring-line D25 + in-memo fixes); every settled region kept byte-stable): (1) ENGINE-ARGV UNITY (amends 2517(1)) - the guard OWNS the construction engine/tokenizer commands, construct-don't-compare: operator-supplied --engine-cmd/--tokenizer-cmd in the builder argv - space or = form, AND every argparse-resolvable ABBREVIATION [REV-E]: the refusal prefix-floors (--engine-c / --tokenizer-c) equal the pinned builder parser's own resolution, MEASURED against the real argparse surface (all 6 abbreviated forms resolve to the owned flags; every shorter --engine*/--tokenizer* stem matches >=3 options and is an ambiguous-option exit-2 error, never a silent resolution; build_carriers.py:1871 default abbreviation) - is REFUSED before ANY engine start, and the guard INJECTS the PROBED --engine-cmd plus its --tokenizer-cmd into the builder argv at launch (both validated as JSON lists), so the attested engine and the constructing engine cannot diverge; construction-guard-final.json records the launched builder_argv verbatim; the README 5b builder command is complete AS PRINTED and its argv shape is oracle-verified against the REAL build_carriers.py argparse surface (in-memory dry parse, cmd_construct stubbed, pinned bytes untouched; the uninjected shape is proven to stall; oracle 20c proves the abbreviation floors on the same real surface). (2) TERMINAL-STOP AUTHORITY (amends 2517(3)) - a checkpoint STOP's construction-abort.json records the breach values and is TERMINAL for the rundir, and the stop is DURABLE [REV-E]: the kill path ALSO appends a hash-bound terminal-abort event to the guard's append-only construction-events.jsonl (fsynced file+dirent - the landed SPEND-START-sentinel mechanics, ASM-2513 v4), which EVERY guard start reads: a deleted, edited, or event-less (replayed/foreign) abort file is refused on the EVENT record, never resumed; resume ONLY via maintainer-authored construction-reset.json {schema kot-f1k-bringup-gate/2:construction-reset, authorized_by non-empty, decision resume-construction, abort_sha256 = sha256 of the abort file bytes} - byte-bound, single-abort, and CONSUMED [REV-E]: after ALL resume validations (incl. the raced-past-frozen-checkpoint refusal) the reset AND the abort are archived (construction-reset.consumed-<ordinal>-<abort-sha16>.json / construction-abort.consumed-<n>.json) with a reset-consumed event appended BEFORE any engine start (the pin-engagement probe IS an engine start), so a second use finds nothing - single-use by the archive-then-proceed order; DISCLOSED threat boundary: an operator with filesystem access editing the guard's event state ITSELF is out of scope (the same boundary as the landed sentinel), and a probe/launch failure after consumption does not re-arm the OLD stop (the authorization covers the remaining schedule until a NEW STOP appends a fresh terminal event); a preemption resume without a prior STOP is unchanged. (3) REALIZED-HOURS BASIS + NUMERIC FINITENESS (amends 2516(4)/2517(3)) - config-cost --prior-hours REQUIRED whenever --prior-usd > 0, emitted as cost.prior_instance_hours, REQUIRED 4th Ledger key, threaded into the module-level add7_hours_basis 900h cap basis (REV-D, unchanged); and FINITE [REV-E, round-4 verdict 4 - the landed PIN_GB defect class]: nan passed the old `ph < 0` check, propagated a NaN basis, and every `nan > 900` comparison is False = fail-open GO; now EVERY operator numeric on the gate CLI is finite-and-sign-validated at the parse via one helper (config-cost --prior-usd/--prior-hours/--rate + the summed guard-final realized figures; checkpoint --elapsed-s/--n-done/--n-start; guard --poll-seconds (NaN would ValueError inside time.sleep MID-construction [MEASURED]); collect --rate/--pin-gb; pinfile --pin-gb, whose NaN was a SECOND fail-open of the class - `used + PER_EXPERT_BYTES > nan` never True = an UNBOUNDED pin file; fcount --mock-f [REV-F: round-5 defect 3 - the flag is on the fcount subparser, immediately before the realize parser, and the D22 _fin lands in tokenize(), the fcount path; the REV-E text mis-attributed it to realize]), and the driver Ledger re-asserts finiteness/sign of all four required cost keys at init as defense-in-depth (a hand-edited bare-NaN JSON value parses [MEASURED]) - refused whoever wrote the config; DISCLOSED, MEASURED: f1k_gcp.py affordability with a nan rate already exits 2 fail-closed (any non-GO projection refuses, REV-A F3d) and checkpoint_eval's ratio-sanity (0 < ratio <= 10, False for NaN) already caught NaN elapsed - those surfaces were fail-closed by construction and f1k_gcp.py is deliberately UNTOUCHED (final sha unchanged); SIDECAR surface unchanged (frozen analysis 126129b9). (4) STRICT CORPUS BIJECTION (REV-D, unchanged): count-preserving duplicate refusal on both sides before the set comparison; mock plants an attacker-consistent conflicting-T duplicate -> refused. (5) SUPERSESSION HONESTY [REV-E] - round-4 proved the REV-D fresh-grep claim FALSE; the five residual stale sites are killed: SSA0's F5 row (memo:1707) struck with the withdrawal bracket, SSB.7's unqualified 'stands' row (memo:2718) corrected, the driver's two re-derivation statements (f1k_driver.py:755/:3663) rewritten via D23 to the withdrawn/deferred state, and the self-found gate collect pin.role string (same withdrawn re-derivation/rebind language) rewritten via D22; the fresh grep is RE-RUN over the memo AND all five D-chain-produced files: every remaining hit is a byte-pinned artifact block (memo:1869/:2942 quoted diffs), an already-struck passage (memo:234), or a landed historical memo record (F1K-PIN-FILE-FIX.md:711 quoting the pre-REV-E driver comment; the live driver text is fixed) - round-5 then REFUTED the REV-E claim with two schema-id residues: the LIVE gate module docstring (D1-origin, post-chain :2) still carried the OLD /1 schema id against the operative SCHEMA /2, and the memo SS5.1 freeze statement was unstruck; BOTH killed at REV-F (D25 + the SS5.1 supersession strike) and the grep RE-RUN over the memo and all five D-chain-produced files: ZERO schema-/1 hits remain in ANY applied file, every memo residual is byte-pinned/struck/landed-historical/negating - the claim is TRUE at REV-F [MEASURED]. (6) ORACLE/MOCK - oracle 37 -> 48 [REV-D] -> 55 [REV-E] (new: 19c eight-form abbreviation refusal, 20c real-parser floor proof, 21f deleted-abort refusal with reset left unconsumed, 21g consumed-reset reuse refusal, 21h event-less abort refusal, 22c nan/inf config-cost refusals, 22d checkpoint/guard numeric sweep; extended: 21a terminal-event assert, 21d consumption/archive asserts, 21e reset-left-in-place assert); driver mock 25 -> 27 [REV-D] -> 28 [REV-E] ([REV-E 3] NaN-ledger-key refusal line); all green on the edited bench AND the fresh D1->D24 chain, pinned-analysis pass green (emission-surface oracle per the round-4 lesson); at REV-F the oracle RE-RAN 55/55 exit-0 (both entry paths, edited bench AND fresh D1->D25 chain) and the driver mock was NOT re-run - the driver artifact bytes are byte-identical at REV-F (261431c1; D25 touches only the gate docstring), so the REV-E mock evidence stands. Bench: 25-artifact chain applies clean on the LANDED 2574c82b tree (byte-identical fresh-chain reproduction, cmp x5; finals e421861e/468ab73d/53d21424/34e6bb27/261431c1 - ONLY the gate file changes at REV-F, docstring line 2; f1k_gcp.py/f1k_worker.sh UNCHANGED from REV-C, README.md/f1k_driver.py UNCHANGED from REV-E), py_compile x3 + bash -n clean, affordability probes exit 2/3, plan DRY-PLAN OK, discipline greps clean (0 PINS/FROZEN_SHA256 +/- lines in D22-D25, both KOT-ADD7-SHARED blocks untouched at 9d3e1bc7 == the frozen constant, build_carriers.py byte-identical a92be3e4, NOT in the diff set); every REV-D/REV-E change is fail-closed-only on unpinned infra files; REV-F changes NO executable semantics (one docstring identifier).", "rationale": "The round-3 verdict proved the REV-C composite could attest construction against the wrong executable, print a stalling construction command, let a re-run bypass a checkpoint STOP, let failed-session hours vanish from the 900h cap, and pass a conflicting duplicate sidecar row; REV-D closed each. The round-4 verdict then proved the REV-D refusal matched full option names while the pinned builder's argparse resolves abbreviations, the abort file was deletable and the reset reusable, a NaN --prior-hours turned the 900h cap fail-open, and the fresh-grep honesty claim was false. REV-E closes each at the narrowest honest surface: a prefix-floor refusal measured EQUAL to argparse's resolution for the pinned option set, append-only fsynced stop events with archive-before-engine-start reset consumption, a finiteness sweep over every operator numeric plus a Ledger-side assert (which also found and closed the unbounded-pin NaN fail-open), and the five stale sites killed with the grep re-run over the driver too. Round-5 (APPROVE-WITH-FIXES) closed every executable finding and prescribed exactly three textual corrections; REV-F applies them verbatim: the /2 docstring (D25, smallest correct delta - amending the sha-settled, round-5-reviewed D22 would have re-opened it), the fcount attribution, and the regenerated hash + grep evidence.", "backing_ref": "poc/gcp/F1K-BRINGUP-GATE-FIX.md REV-F SSE-SSF (this freeze; D22-D25 + bench evidence); poc/gpt56-review/f1k-gate-fix-round5-VERDICT.md; poc/gpt56-review/f1k-gate-fix-round4-VERDICT.md; poc/gpt56-review/f1k-gate-fix-round3-VERDICT.md; build_carriers.py:1871/:1875 (pinned bytes: default-abbreviation argparse surface, mandatory --engine-cmd/--tokenizer-cmd); analysis/f1k.py 126129b9 (frozen instance_hours identity + closed cost schema); f1k_driver.py landed 2574c82b (Ledger/addendum-7 seam; SPEND-START sentinel mechanics mirrored); ASM-2513 (recovery + sentinel patterns), ASM-2374 (corner figures), ASM-2514/2515/2516/2517 (as amended); bead kernel-of-truth-8cpm (deferred seq-4 generator re-freeze, unchanged)", "status": "open", "owner": "designer-20", "date": "2026-07-18"}
```

## F6. REV-F self-check (rows 90–97; every claim → where verified this pass → tag)

| # | Claim | Verified where (this REV-F pass) | Tag |
|---|---|---|---|
| 90 | Round-5 verdict read verbatim; APPROVE-WITH-FIXES; all executable machinery CLOSED; exactly three textual corrections, each mapped to a disposition (F0) and applied | verdict full read + F0 map + this table | [MEASURED memo/diff state] |
| 91 | Settled regions byte-stable: D1–D24 artifact blocks unedited (all 24 shas re-verified against their tables); D25 is ONE docstring hunk; 0 `PINS`/`FROZEN_SHA256` +/- lines in D25; no KOT-ADD7-SHARED touch; NO executable semantics change in REV-F | extraction + sha compare + D25 read | [MEASURED] |
| 92 | Baseline: the four repo target files byte-equal to HEAD `2574c82b` (`git diff` empty); the gate file absent pre-chain | git diff + test this pass | [MEASURED] |
| 93 | D25 sha as tabled (`90823ae5…`); D1→D24 reproduces the §E5 finals; full D1→D25 chain applies clean; fresh-chain reproduction byte-identical (`cmp` ×5); REV-F finals e421861e/468ab73d/53d21424/34e6bb27/261431c1 — ONLY the gate file changed vs REV-E | two independent /tmp benches this pass | [MEASURED] |
| 94 | ZERO schema-`/1` hits in ALL FIVE applied files post-D25 (`grep -c` = 0 ×5); the oracle banner prints `/2` | grep + selftest output this pass | [MEASURED] |
| 95 | Fresh grep RE-RUN (six §E.4 patterns; memo post-edits + five applied files + `build_carriers.py`): every memo residual classified (a)–(d), no unstruck operative hit; the four-bucket claim TRUE at REV-F; §E.3 + ASM-2518 now say `fcount --mock-f` (the fcount subparser owns the flag, memo:1152/:1157) | §F.2 grep + §E.3/§F.5 reads this pass | [MEASURED] |
| 96 | Oracle 55/55, exit 0, BOTH entry paths, edited bench AND fresh-chain tree (four runs); driver mock NOT re-run — driver artifact bytes byte-identical at REV-F (`261431c1…`); `build_carriers.py` `a92be3e4…` untouched, NOT in the diff set | selftest runs + sha compares this pass | [MEASURED] |
| 97 | Memo-only pass: repo untouched except this file; NO spend, NO VM, NO git action; /tmp benches disposable; `py_compile` ×3 + `bash -n` clean on the applied tree | git status this pass | [MEASURED] |

## F7. Summary (REV-F, whole composite)

- **One story, one schema id:** the last two `/1` residues (the live gate docstring, the §5.1
  freeze statement) are killed — D25 for the code, the strike for the memo; ZERO schema-`/1`
  hits remain in any applied file, and the four-bucket grep claim is finally TRUE as measured.
- **The mock flag is attributed to its real parser:** §E.3 and ASM-2518 now say
  `fcount --mock-f` (the enforcement itself was always in the fcount path — code unchanged).
- **The hash chain is honest again:** 25 sha-pinned artifacts; byte-identical fresh-chain
  reproduction on `2574c82b` (cmp ×5); REV-F finals e421861e/468ab73d/53d21424/34e6bb27/
  261431c1 — only the gate byte-changed, so the oracle re-ran (55/55, both paths, both
  benches) and the driver mock evidence stands on byte-identical driver bytes (not re-run).
- **Nothing else moved:** no executable semantics, no PINS/FROZEN/ADD7 touches,
  `build_carriers.py` still `a92be3e4…`; round-5 closed all machinery — the coordinator apply
  (§F.4) is next. $0 spent; nothing applied by this pass.

BRINGUP-GATE-FIX REV-F DONE
