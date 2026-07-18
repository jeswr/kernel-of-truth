# Candidate A — Stage-0 measurement package (FALSIFIER-1 routing re-analysis + saliency-flatness gate) — v3

> **Status: EXPLORATORY design memo v3 (designer-20, 2026-07-18). Working tree only —
> no spend, no VM, no git action taken. Feeds the Fable -> GPT-5.6 -> freeze
> pipeline; nothing here is prereg-grade or frozen.** Source steering:
> `docs/next/design/moe-expert-replacement-design-menu.md` §3 Candidate A + the
> coordinator dual-model steering note (2026-07-17); the maintainer sign-off venue
> for the priced step is GitHub issue #51. This package does **not** touch F1-K,
> which runs to its own registered readout (steering note, emphatic); the only
> F1-K contact is read-only reuse of already-committed probe bytes.

## Revision log (v3)

v2 was re-reviewed by GPT-5.6 (xhigh) → **APPROVE-WITH-FIXES**
(`poc/gpt56-review/candidate-a-v2-rereview/last-message.json`): 8/11 v2 fixes
RESOLVED; **Stage-0a is APPROVED to run as designed** (after the P0
probe-results commit + sha256 pin); three items are fixed here, in place,
before ASMs 2505–2512 are finalized/registered:

1. **(re-review #1) Stage-0b family-view predictor split was circular.**
   v2 conditioned the family-level predictor on `prompt_family × counterpart`,
   but `prompt_family` (`macro.sub.f{fill}`, 240) IS the discovery/dev/held-out
   split unit (`build_corpus.py:683-690` — split assigned per fill; each prompt
   family lies wholly in one split), so a prompt-family-conditioned shortlist
   has, by construction, ZERO discovery data for every held-out class —
   discovery-fit/held-out-scoring was vacuous. **Fixed choice, stated
   explicitly: the predictor grouping is `template_family × counterpart`**
   (`macro.sub`, 48 — spans all splits: fills 0–2 discovery / 3 dev / 4
   held-out within each subdomain), which IS cleanly available in the committed
   corpus manifest. Cells failing a held-out floor degrade to
   unresolved/DESCRIPTIVE, never silently into either bucket (§4 step 4).
2. **(re-review #7) ASM-2507's coverage gate protected selection MASS, not
   expert-CELL coverage.** v2's ≥90%-of-selection-mass resolution rule could
   mark a layer "resolved" while many expert cells — exactly the cellwise
   saliency tail at issue — stayed unmeasured, letting a flat verdict hide
   behind unmeasured cells. **ASM-2507 v3 re-stated cellwise:** every cell with
   <50 qualifying activations is conservatively imputed TAIL-COMPATIBLE
   (conditional saliency 0) inside ρ_ℓ^cons, so unmeasured cells mechanically
   count toward the cheap tail and a flat call cannot hide behind them
   (§5.3, ASM-2507 v3).
3. **(re-review #10, material) S1-tf's asymmetric load-bearing DEAD was
   UNSOUND and is withdrawn.** Teacher forcing has no established one-sided
   ordering for conditional-saliency FLATNESS — the one-sided optimism
   argument is for routing predictability/replaceability (ASM-2510's domain,
   unaffected), not saliency. S1-tf is reframed as a cheap COARSE first look
   (~$15–$20): a found tail is PROVISIONAL; a flat result is
   **PROVISIONAL/UNRESOLVED — suggestive, not decisive, NOT DEAD**; any DEAD
   verdict for the pruning direction requires a generation-side run (§5.2
   table + recommendation, §5.3, ASM-2512 v3). The coordinator has already
   posted this correction to issue #51.

**Stage-0a (§3: P0 + A1–A4 descriptive, verdict hard-coded
`PROVISIONAL-NEEDS-0b`) is UNAFFECTED by all three fixes** — none touches its
inputs, computations, schema, or verdict — and remains coordinator-runnable
NOW after the P0 commit + hash. All other v2 content is RESOLVED per the
re-review and left unchanged.

## Revision log (v2)

v1 was reviewed by GPT-5.6 (xhigh) → **APPROVE-WITH-FIXES**
(`poc/gpt56-review/candidate-a-review/last-message.json`). All cited defects are
fixed in place:

1. **A5 moved out of the $0-now tier.** The committed D5 parquet DROPS the
   family×counterpart conditional-mass maps (they exist only in the transient
   `agg.json`; `atlas_agg.py:20`, `build_atlas.py:318`) and retains only 6
   top-activation `(item,tok)` exemplars per cell — biased maxima that cannot
   estimate predictability. A5 now lives in Stage-0b (§4); §2/§3 re-state
   honestly what the committed tier can bound without it.
2. **D3 inputs are UNTRACKED, not committed.** `poc/gcp/probe-results/`
   (`accum20.stats`, `m4.json`, `probe-results.json`) exists on disk but is
   untracked in this checkout (`git status`: `?? poc/gcp/probe-results/`). The
   "all committed" premise of v1 was wrong; §3 now requires the coordinator to
   `git add`/commit these bytes and pin their sha256 BEFORE Stage-0a runs.
3. **0.2372 re-worded everywhere as an optimistically BIASED in-sample point
   estimate, not a deterministic out-of-sample floor.** The pin is ranked on
   the same histogram it is scored on; the true out-of-sample residual is
   *likely higher* but is NOT bounded below by 0.2372 deterministically.
4. **A3/A4 config conflation fixed.** D1 was collected MTP-ACTIVE (draft=3) on
   the expert-INT8 78-layer engine (`results/stats/f000.out:2,9`); the D3/target
   config is 75-layer int4 DRAFT=0. A3/A4 now EXCLUDE the MTP layer-78 cells,
   DISCLOSE the execution-config mismatch, and are re-scoped as prompt-fixed
   diagnostics — not clean cross-distribution/OOD evidence.
5. **Units bug fixed:** the exploitable-mass metric is now defined in
   SELECTION mass end-to-end, the same unit as the ASM-2505 threshold (v1's A5
   compared routed-WEIGHT mass against a selection-mass threshold, so no
   verdict could be licensed).
6. **ASM-2505 arithmetic corrected and reframed.** 5pp = 0.05/0.23716 = 21.1%
   of residual misses → wall-clock ceiling 1/(1−d·0.211) = **1.087×–1.203×**
   for d∈[0.38, 0.8] (v1 said 1.05–1.2×), and the d-range is widened to
   **[0.16, 0.8]** because the same M3 artifact contains longer rows with
   d ≈ 56.7/352.9 ≈ 0.16 (`probe-results.json:68,99`) → full band
   **1.035×–1.203×**. 5pp/10pp are now programme OPPORTUNITY-COST triage
   bands, not general impossibility claims.
7. **ASM-2507 flatness kill re-stated.** ρ≥0.5 is a stipulated no-cheap-tail
   threshold, not "indistinguishable from median"; the bootstrap CI direction
   is now a **lower** bound (kill only if even the conservative read is flat);
   the <50-activation exclusion now carries a fail-closed COVERAGE gate
   (unresolved layers count AGAINST a DEAD verdict).
8. **A2 downgraded:** the static GB curve bounds STATIC / prompt-level
   residency only — token/layer-conditioned swapping can reuse capacity across
   a diffuse tail (as A4 itself concedes), so A2 does not bound "any residency
   lever".
9. **Stage-0b counting fixed:** exploitable events are counted only when the
   event's expert is ACTUALLY in the discovery-fitted shortlist — not merely
   in a (layer,class) with ≥80% shortlist coverage (which overcounts up to
   20%).
10. **Stage-1 REPRICED — the load-bearing fix.** ~$2–3 was wrong by ~1.5–2
    orders of magnitude for 32,768 autoregressive DRAFT=0 tokens (Wave-A's
    $2.51 bought 4,668 TEACHER-FORCED tokens; decode is 0.05–0.1 tok/s). New
    first-principles band: **~$100–$210** for the v1 design. Because the #51
    sign-off was obtained against the wrong number, the corrected price MUST
    be re-surfaced to the maintainer BEFORE any run. §5 adds cheaper designs
    and recommends a teacher-forced first cut.
11. **Stage-0a verdict forced to PROVISIONAL-NEEDS-0b.** No $0 DEAD/GREENLIGHT
    is possible: A1–A4 are DESCRIPTIVE diagnostics only; the falsifier verdict
    needs the 0b volume retrieval and the corrected forward-predictor metric.

Governance (§4-AGREE items) is unchanged and preserved: kernel-out
calibration, broad non-kernel corpus, read-only F1-K reuse, Stage-1
sign-off/ledger gating, and the bar on flatness licensing the 50% headline.

---

**What this is.** The first, cheapest measurement package for Candidate A
(honestly-priced REAP-on-GLM-5.2 + kernel-as-optional-external-checker): the two
gates that can kill or unlock whole directions before any material spend —

1. **FALSIFIER-1 (routing-trace re-analysis, $0 tier + ~$0 retrieval tier):**
   what fraction of expert-load traffic is BOTH surface-feature-predictable AND
   not already served by the static hot set? If tiny, every routing / prefetch /
   short-circuit lever (DRS-class) is dead before any spend. **v2: the $0-now
   tier is descriptive only; the falsifier verdict itself requires the 0b
   retrieval tier (§4).**
2. **Saliency-flatness gate (REPRICED, SIGN-OFF GATED — see §5):** does GLM-5.2
   have a droppable low-conditional-impact expert tail at all (REAP saliency,
   DRAFT=0)? **v3: any DEAD (no-tail) verdict for the pruning direction
   requires a generation-side measurement passing the cellwise coverage gate
   (ASM-2507 v3).** The cheap teacher-forced first cut (S1-tf, §5.2) is a
   COARSE first look whose flat result is suggestive, not decisive
   (ASM-2512 v3).

This is a **measurement package whose NULL is itself the reportable datum**. It
does not presume the kernel earns anything (§6).

---

## 1. Data inventory — what routing data actually exists in-repo

All numbers below marked MEASURED were re-derived from on-disk bytes during
this design pass (commands: rank/accumulate the stats files; see §3 for the
reproducible recipes).

| # | Artifact | Granularity | Side | Distribution | Size / n |
|---|----------|-------------|------|--------------|----------|
| D1 | `poc/glm52-probe/results/stats/f000..f023.stats` (+`manifest.json`) | **Aggregate** per-(layer,expert) counts, SESSION-CUMULATIVE (see CONTAMINATION-NOTE.md); first-differencing recovers **per-prompt** aggregate fingerprints, n=23 (f000 unrecoverable). **Execution config [MEASURED, `f000.out:2,9`]: MTP ACTIVE (draft=3), experts @ INT8, 78 layers** — NOT the 75-layer int4 DRAFT=0 target config; see A3/A4 disclosure | ~20-token prompts, 1 gen token → effectively prefill | 24 concept-stratified probe prompts (kernel-concept corpus) | totals 111,904 → 371,336 selections |
| D2 | `poc/glm52-probe/routing-analysis-v3.json` (+`analyze_routing_v3.py`) | Derived concept-structure statistics on the D1 differenced fingerprints | — | — | n=23; universal cells 2,027 (mass 0.4178); centred within−across Δ=0.3303, p=0.0001 [MEASURED, in file] |
| D3 | `poc/gcp/probe-results/accum20.stats` (+`m4.json`, `probe-results.json`) — **UNTRACKED in this checkout** (`git status`: `?? poc/gcp/probe-results/`); files exist on disk but are NOT committed. Coordinator must `git add`+commit and pin sha256 before Stage-0a (§3 precondition P0) | **Aggregate** per-(layer,expert) counts, single histogram accumulated over 20 F1-K prefills | Prefill (F1-K probe, DRAFT=0 per exit-status P1) | F1-K probe corpus | 16,184 active cells of 19,200; 2,880,000 selections = 75 layers × 8 × 4,800 tokens [MEASURED] |
| D4 | `poc/glm52-probe/smoke/` — **kot-rtrace/1 per-token trace instrument** (`rtrace.h`, engine patch, `trace_schema.md`, `trace_analyze.py`) | **PER-TOKEN**: one row per selected expert per token per layer — (item, tok, io, layer, rank, expert id, raw, gate, sel, w, margin); framing + top-k + byte-identity invariants; FNV-1a-64 decision fingerprint | Teacher-forced prefill as driven so far | Instrument, not data | validated 12/12 probes, repeat byte-identical (smoke-oci-20260715) |
| D5 | `poc/glm52-probe/wave-a/atlas/` (`expert_atlas.parquet`, `expert_atlas_index.json`, `coverage_gates.json`) | **Aggregate** per-cell sufficient statistics of a full kot-rtrace/1 run: per (site,layer,expert): event/weight totals, rank histogram, io split, derived enrichment summaries with family-bootstrap CIs, and **6 top-activation `(item,tok)` exemplars only**. **The per-(prompt-family × counterpart) conditional-mass maps are NOT in the parquet — they exist only in the transient `agg.json` (`atlas_agg.py:20`, dropped at `build_atlas.py:318`) and are not committed. (The 0b family view itself conditions on template_family × counterpart, not prompt_family — v3 fix 1, §4 step 4.)** Raw per-token rows NOT committed either. | Teacher-forced prefill, DRAFT=0 | wave-a corpus: 480 items, 12 macrodomains × 48 template families × discovery/dev/held-out splits (committed: `wave-a/corpus/`) | 2,800,800 trace rows aggregated; 19,090/19,200 cells active |
| D6 | **Modal named volume `kot-glm52-wave-a-out`, path `full/rtrace.jsonl.gz` (+`trace_manifest.txt`)** — the wave-a RAW per-token trace | **PER-TOKEN**, full kot-rtrace/1 rows for all 480 items | Teacher-forced prefill, DRAFT=0 | wave-a corpus | ~2.8M route rows; NOT in repo; retention STIPULATED (ASM-2509) |

Headline MEASURED facts this package builds on:

- **Static-pin hit 0.7628 at the G50 (50 GB) budget is exactly reproducible from
  the on-disk bytes** [MEASURED, this pass]: ranking `accum20.stats` cells by
  count (desc) and taking the top 2,696 (= 50 GB at 18.54 MB/tensor) reproduces
  `m4.json` `h_pin_by_G.G50 = 0.7628` (and G40→0.7132, G100→0.9032). **This is
  in-sample** — the pin is ranked on the same histogram it is scored on — so
  0.7628 is optimistically biased HIGH and the residual **0.2372 is an
  optimistically biased (low) point estimate, NOT a deterministic out-of-sample
  floor**: the true out-of-sample residual is likely higher, but nothing here
  bounds it below deterministically. (v2 fix; v1's "≥ 0.2372" claim withdrawn.)
- The residual tail is long and flat at the top end [MEASURED, `m4.json`
  concentration curve]: rank 2,696→5,393 (i.e., +50 GB) buys only +0.14 hit;
  capturing the full tail needs 300 GB.
- The trace `r` rows carry **no token id**, but token identity at every
  (item, tok) is exactly recoverable: the corpus text is committed
  (`wave_a_corpus.json`), tokenisation is deterministic (host pre-tokenises via
  the model tokenizer; `trace_manifest.txt` with the literal token ids is also on
  the volume). So per-token **surface features are derivable** from D6.
- The wave-a atlas's own coverage gates **FAILED** [MEASURED,
  `coverage_gates.json`]: only 0.825 of routing mass sits on cells with ≥100
  events (gate ≥0.95), and discovery-vs-held-out layer Spearman median is 0.6328
  (gate ≥0.8; 0% of layers pass). 10,266/19,200 cells are labelled `rare`. The
  undersampled region is **exactly the non-resident residual** FALSIFIER-1 cares
  about → every conditional estimate from wave-a data needs CIs and a
  low-confidence flag, not point estimates.

## 2. The honest split: what FALSIFIER-1 can and cannot be computed from

The task's binary question — per-token traces or aggregate-only — has a
**three-tier** answer. v2 correction: the family-level predictable∩non-resident
computation (old A5) is NOT possible in the $0-now tier, because its required
input (per-cell family×counterpart conditional masses) was dropped from the
committed parquet and survives only in the transient `agg.json` and in the D6
raw trace. A5 therefore moves to the 0b tier, where it is subsumed by the full
token-level computation.

| Tier | Data | What it supports | What it cannot support |
|------|------|------------------|------------------------|
| **$0-now (committed + to-be-committed D3 bytes only)** | D1–D3, D5 | **DESCRIPTIVE diagnostics only:** residual mass point estimate + residual concentration (D3); static-GB economics of the tail (A2, static/prompt-level residency only); prompt-fixed hot-set stability and prompt-level oracle gap on the 23 D1 fingerprints, under the disclosed config mismatch (A3/A4). **No falsifier verdict is computable at this tier** — verdict forced PROVISIONAL-NEEDS-0b. | **Predictability of any kind — NOT computable.** D1/D3 are aggregate histograms; the committed D5 parquet aggregates away token identity AND drops the family-conditional masses (only 6 biased top-activation exemplars per cell remain). No committed artifact links a token/feature/family to a routing decision at estimable granularity. |
| **~$0-retrieval (Modal credentials, no compute)** | D6 (+ committed D5 corpus/splits) | The **full surface-feature half of FALSIFIER-1** at token granularity — per-(feature, layer) routing entropy, discovery-fit/held-out-scored predictable fraction, intersection with the static hot set — plus the family-level view (old A5) recomputed properly from raw rows; offline, CPU-only, on already-collected traces | Generation-side behaviour. D6 is teacher-forced prefill on a template corpus; prefill routing over-predicts exploitability (menu §risk-5) → a 0b GREENLIGHT is **provisional** (ASM-2510); a 0b DEAD is load-bearing |
| **Needs collection (SIGN-OFF GATED — REPRICED, see §5)** | Stage-1 run (§5) | Generation-side confirmation of FALSIFIER-1 **and** the saliency-flatness gate (v3: a DEAD flatness verdict requires a generation-side option — the teacher-forced S1-tf cut is coarse/provisional only, ASM-2512 v3) | Cost is NOT ~$2–3 (v2 fix 10); the corrected price must be re-ratified on issue #51 before any run |

**So: no half of FALSIFIER-1's predictability question is computable from
committed bytes.** But it does NOT require new *collection* either, provided
ASM-2509 holds — the per-token traces already exist on the wave-a output volume
and retrieval is a credentialed download, not a run. The genuinely-new
collection (generation-side) is Stage-1, which must first be re-priced with the
maintainer (§5).

## 3. Stage-0a — the exact $0 re-analysis (coordinator-executable now; DESCRIPTIVE ONLY)

**Precondition P0 (v2, fix 2):** `poc/gcp/probe-results/` is untracked. The
coordinator must `git add poc/gcp/probe-results/` and commit (the files exist
on disk; this is a tracking action, no data is regenerated), so that Stage-0a
runs on committed bytes with pinned sha256. Until then the D3 inputs are
uncommitted and every D3-derived number below is provisional-on-provenance.
(This memo itself takes no git action.)

New script `poc/glm52-probe/analyze_residual_v1.py` (stdlib + optional pyarrow
for D5; deterministic, seed 20260712 — same registered seed family as
`analyze_routing_v3.py`). **Reuse from `analyze_routing_v3.py` verbatim:** the
`load()` stats parser, the fail-closed `ERR_NOT_CUMULATIVE` monotonicity check,
the first-difference recipe (d_N = f_N − f_{N−1}, N=1..23, f000 dropped), and
the seeded permutation/bootstrap machinery. New analysis code needed: pin-set
reconstruction, oracle-gap, and the layer-alignment/exclusion logic (~150
lines total; the D5-parquet reader of v1 is no longer needed at this tier).

Inputs (record sha256 of each in the output provenance block, as v3 does):
`accum20.stats`, `m4.json` (both post-P0 committed), `results/stats/f000..f023.stats`
+ `manifest.json`, `wave-a/corpus/corpus_manifest.json`.

**Config-mismatch disclosure (v2, fix 4) [MEASURED, `f000.out:2,9`]:** D1 was
collected with **MTP ACTIVE (draft=3), experts @ INT8, 78 layers**; D3 and the
Candidate-A target run on the **75-layer int4 DRAFT=0** config. A3/A4 therefore
(a) EXCLUDE all layer-78 (MTP-position) cells from both sides so the comparison
covers the same 75 MoE layers, and (b) are labelled **prompt-fixed diagnostics
under a disclosed corpus+execution-config change** — v1's "cross-distribution"
framing conflated the two and is withdrawn. A3/A4 are NOT clean OOD evidence.

### Computations (A1–A4 are DESCRIPTIVE; no verdict is derivable from them)

- **A1 — Pin-set reconstruction + residual (verification anchor).** Rank
  `accum20.stats` cells by count desc, tie-break (layer, expert) asc; take top
  2,696. MUST reproduce h_pin = 0.7628 (fail closed if not). Residual mass
  R = 0.2372 — **an in-sample, optimistically-low-biased point estimate of the
  residual; NOT a deterministic out-of-sample floor** (the pin is fit and
  scored on the same histogram; true out-of-sample residual is likely higher
  but is not bounded here). Emit the pin-cell set for A2–A4 and Stage-0b.
- **A2 — Residual concentration / STATIC-residency economics.** Over non-pin
  cells of `accum20.stats`: cumulative hit-vs-GB curve (extends `m4.json`'s
  curve below the pin line at fine grain). Report GB required to capture the
  next 5pp and 10pp of total selection traffic. **Scope (v2, fix 8): this
  bounds STATIC and prompt-level residency levers only** — a
  token/layer-conditioned swapping policy can reuse the same physical capacity
  across a diffuse tail over time (exactly the possibility A4/ASM-2511
  concede), so this curve does NOT bound "any residency lever". Dynamic levers
  are addressed only by the predictability measurements (0b/Stage-1) plus the
  bandwidth ceiling noted in ASM-2511.
- **A3 — Hot-set stability across the D1 prompt set (prompt-fixed diagnostic,
  config-mismatched).** Score the A1 pin set (layer-78 cells excluded both
  sides per the disclosure above) against each of the 23 differenced D1
  fingerprints: distribution of per-prompt hit fractions, min/median, BCa
  bootstrap CI (n=23 — CI will be wide; report it anyway). Because corpus AND
  execution config both differ, a low hit here is ambiguous between concept
  shift and config shift — report it as a descriptive stability read with that
  ambiguity stated, not as an OOD counterweight.
- **A4 — Prompt-level oracle gap (upper bound at prompt granularity, same
  disclosure).** For each differenced fingerprint (layer 78 excluded): oracle
  per-prompt pin at the matched 2,696-cell budget minus the static-pin hit on
  that prompt. Δ_oracle bounds every **prompt-conditioned** residency policy
  *on this config-mismatched prompt set*. Complementary to — not a bound on —
  token-level FALSIFIER-1 (a within-sequence swapping policy could in principle
  exceed it; disk bandwidth in practice caps swapping — ASM-2511).
- **A5 — MOVED to Stage-0b (v2, fix 1).** The family-level
  predictable∩non-resident mass cannot be computed from the committed parquet
  (family×counterpart conditionals dropped at build time; only 6 biased
  top-activation exemplars per cell survive). In 0b it is computed from the
  raw D6 rows and subsumed by the token-level metric, in selection-mass units
  (fix 5).
- **A6 — Verdict assembly (v2, fix 11).** Stage-0a's verdict field is
  **hard-coded `PROVISIONAL-NEEDS-0b`**. A1–A4 cannot license DEAD or
  GREENLIGHT: no predictability estimate exists at this tier, the residual
  estimate is in-sample-biased, and A3/A4 are config-confounded. The
  falsifier verdict is emitted only by Stage-0b/Stage-1 under ASM-2505 with
  metric and threshold in the same unit (selection mass).

### Falsifier threshold (pre-stated; applies at 0b/Stage-1, NOT 0a)

**FALSIFIER-1 kill line [STIPULATED, ASM-2505 v2]:** if exploitable traffic —
**selection mass** that is predictable (per the operative tier's definition)
AND ∉ static G50 pin — is **< 5pp of total selections** (< 21.1% of the
0.23716 residual point estimate), the routing/prefetch/short-circuit direction
(DRS-class) is **DEAD-for-opportunity-cost** for GLM-5.2-on-this-estate.
Corrected pricing (v2, fix 6): +5pp hit cuts miss bytes by 0.05/0.23716 =
21.1%; the wall-clock ceiling is 1/(1 − d·0.211) where d is the disk
wall-share. MEASURED d spans **0.16–0.38 within the same M3 artifact**
(short rows ≈ 45/120 ≈ 0.38; longer rows ≈ 56.7/352.9 ≈ 0.16,
`probe-results.json:68,99`) and the northstar §1.3 stipulates up to 0.8 for
the i4i box → ceiling band **1.035×–1.203×** over d ∈ [0.16, 0.8]
(1.087×–1.203× on the MEASURED-OCI-to-stipulated-i4i subrange [0.38, 0.8]).
For 10pp (42.2% of residual) the band is 1.072×–1.509×. **Framing (v2):**
these are programme **opportunity-cost triage bands** — below 5pp the ceiling
is too small to beat REAP-class pruning as the competing lever at current
prices — NOT general impossibility claims about routing levers. Greenlight
(proceed to pricing a predictor) only if exploitable ≥ 10pp with the CI lower
bound ≥ 5pp.

### Output schema

`poc/glm52-probe/results/falsifier1-stage0a.json` (+ a short md report):

```
{ "schema": "kot-falsifier1/0a",
  "provenance": { source_sha256{...}, seed, script_sha256, tier: "committed-bytes-only",
                  d3_commit: "<commit that tracked poc/gcp/probe-results>" },
  "config": { pin_budget_gb: 50, pin_cells: 2696, layer78_excluded: true,
              thresholds: {kill_pp: 5, green_pp: 10}, nboot, seed },
  "A1": { h_pin_insample, residual_mass_insample_biased },
  "A2": { gb_for_next_5pp, gb_for_next_10pp, curve: [...], scope: "static/prompt-level residency only" },
  "A3": { per_prompt_hit: [...], median, min, ci95, config_mismatch: "D1 MTP-active int8 78L vs target int4 DRAFT=0 75L" },
  "A4": { delta_oracle_mean, ci95, per_prompt: [...] },
  "verdict": "PROVISIONAL-NEEDS-0b",   // hard-coded at this tier; DEAD/GREENLIGHT unreachable
  "caveats": ["descriptive only", "in-sample pin (residual biased low)",
              "A3/A4 config-confounded (layer 78 excluded, MTP/int8 vs int4 undisclosed in v1)",
              "no predictability estimate exists at this tier", ...] }
```

## 4. Stage-0b — ~$0 retrieval: the full token-level FALSIFIER-1

**Precondition:** ASM-2509 (volume retention) — first action is
`modal volume get kot-glm52-wave-a-out full/rtrace.jsonl.gz` (+
`full/trace_manifest.txt`), exactly as `wave-a/collect_and_build.sh` already
does. Credentialed download; no compute spend; if the volume was reaped, this
tier collapses into Stage-1 (the same computation runs on the Stage-1 trace).

New script `poc/glm52-probe/falsifier1_surface_v1.py` — streaming, stdlib,
CPU-only; reuse `smoke/trace_analyze.py`'s invariant checks (fail closed on any
violation) and `atlas_agg.py`'s streaming-reader + corpus/split-map pattern.

**Computation (the exact spec):**

1. Join each `r` row (item, tok) → token id via `trace_manifest.txt` (or
   deterministic re-tokenisation of the committed corpus — must agree; fail
   closed on mismatch). Derive per-token **surface features**: token char-class
   (punct / digit / whitespace / alpha-by-script / other), token id (top-1024
   frequent ids as singleton classes, rest bucketed by class), previous-token
   class, io flag, coarse position bucket. Features are **surface-only** by
   construction (computable before the forward pass) — that is the point.
2. Per (layer, feature-class): the conditional expert-selection distribution;
   its entropy; and top-m coverage. **Predictable [STIPULATED, ASM-2506]:** a
   feature-conditioned shortlist of m=16 experts (2k) capturing ≥80% of that
   (layer, class)'s selections, with the shortlist **fit on the wave-a
   discovery split and scored on the held-out split** (the corpus ships the
   split map — no in-sample optimism), min 200 held-out selections per cell
   else unresolved.
3. **Intersect with the static hot set — event-level membership (v2, fix 9):**
   exploitable mass = held-out **selection** mass over events e such that
   (i) the event's (layer, feature-class) is predictable per ASM-2506, AND
   (ii) **the event's selected expert is itself a member of the
   discovery-fitted m=16 shortlist for that (layer, class)** — events routed
   to non-shortlist experts inside a predictable class are NOT exploitable
   (v1's class-level counting overcounted these by up to 20%), AND
   (iii) the expert ∉ A1 pin-2696. Unit is selection mass throughout, matching
   ASM-2505 (fix 5). CIs: seeded bootstrap over the 240 prompt families
   (respects template correlation), 2,000 resamples.
4. **Family-level view (subsumes v1's A5) — predictor grouping corrected (v3,
   fix 1 / re-review #1):** the same exploitable-mass computation with
   **`template_family × counterpart`** (48 × 2 classes) as the conditioning
   class — NOT `prompt_family × counterpart`. Reason, stated: `prompt_family`
   (`macro.sub.f{fill}`, 240) IS the split unit — the split is assigned per
   fill within each subdomain, so each prompt family lies wholly in one split
   (`build_corpus.py:683-690`) and a prompt-family-conditioned shortlist has
   zero discovery data for every held-out class; discovery-fit/held-out
   scoring of it is circular/vacuous. `template_family` (`macro.sub`) spans
   all splits (fills 0–2 discovery / 3 dev / 4 held-out within every
   subdomain) and ships in the committed corpus manifest, so shortlists are
   fit on each class's discovery fills and scored on its held-out fill —
   well-defined. Computed from raw D6 rows (the committed parquet cannot
   supply this — v2 fix 1), reported alongside the surface-feature metric as
   a **secondary diagnostic** (only the ASM-2506 surface-feature metric feeds
   the ASM-2505 verdict). **Sample-size honesty:** held-out volume per
   (layer, template_family × counterpart) cell is thin — one held-out prompt
   family per class ⇒ ~10 tokens ⇒ ~80 selections per layer-cell, below
   ASM-2506's 200-selection gate — so this view uses a reduced ≥50
   held-out-selection floor per (layer, class); cells below it are UNRESOLVED
   and their mass goes to the **unresolved-mass** term, together with the
   `rare`-cell mass (atlas coverage gates FAILED), never silently folded into
   either bucket. If unresolved mass dominates a layer, the family view for
   that layer is reported DESCRIPTIVE-only.
5. Apply ASM-2505 (selection-mass units both sides). Output
   `falsifier1-stage0b.json`, schema as §3 with `tier: "wave-a-volume-trace"`
   plus per-layer entropy tables and the predictable / unpredictable /
   unresolved three-way mass split. This tier CAN emit DEAD (load-bearing) or
   GREENLIGHT-provisional (per ASM-2510); Stage-0a cannot.

**Honest limits of 0b [ASM-2510]:** teacher-forced prefill on a
template-generated corpus. Prefill routing over-predicts exploitability and the
corpus is not the deployment distribution — so a 0b **DEAD** verdict is strong
(prefill is the optimistic side), while a 0b **GREENLIGHT is provisional**
until the Stage-1 generation-side confirmation. This asymmetry is what makes
0b worth running before any spend: its kill is load-bearing, its pass is
merely encouraging.

## 5. Stage-1 — the saliency-flatness gate (SEPARATE SPEND; REPRICED — corrected number MUST go back to the maintainer on issue #51 BEFORE any run)

**Purpose (primary):** is there a droppable low-conditional-impact expert tail
on GLM-5.2 at all? **Secondary:** generation-side per-token routing trace →
the FALSIFIER-1 confirmation of §4.

### 5.1 The honest reprice (v2, fix 10 — supersedes v1's ~$2–3 and ASM-2508 v1)

v1 transferred Wave-A's $2.51 to the Stage-1 design. That transfer was
invalid: Wave-A's $2.51 / ~2.2 h [MEASURED, `wave-a/README.md`] covered
**4,668 TEACHER-FORCED tokens** (2,800,800 rows / (75 layers × 8) —
`expert_atlas_index.json:6`), i.e. batched prefill throughput ≈ 0.59 tok/s.
The v1 Stage-1 design is 256 items × ~128 free-generation tokens ≈ **32,768
AUTOREGRESSIVE DRAFT=0 decode tokens**, and documented decode throughput on
this class of box is **0.05–0.1 tok/s** (northstar §1.1:96, MEASURED-cold).
First principles:

- Wall-clock: 32,768 tok ÷ (0.05…0.1 tok/s) = **327,680…655,360 s ≈ 91–182
  hours** (plus prompt prefill, minor at ~0.59 tok/s).
- Box rate: $2.51 / 2.2 h ≈ **$1.14/h** [MEASURED, wave-a analogue].
- **Honest cost band: ~$104–$208 → call it ~$100–$210** — roughly **40–80×**
  the ~$2–3 the maintainer ratified on #51. [ASM-2508 v2]

**Governance consequence:** the #51 sign-off was obtained against a wrong
cost. The corrected band (or a cheaper redesign below) MUST be re-surfaced to
the maintainer on issue #51 and re-ratified BEFORE any Stage-1 run. No
run-script is written, let alone launched, until then.

### 5.2 Cheaper Stage-1 designs (priced the same way)

| Option | Design | Tokens | Wall-clock @ measured rates | Cost @ ~$1.14/h | Caveat |
|---|---|---|---|---|---|
| S1-full (v1 design, repriced) | 256 items × 128 gen tokens, DRAFT=0 | 32,768 decode | 91–182 h | **~$100–$210** | Full power; price likely above opportunity-cost bar |
| S1-lite-gen | 64 items × 32 gen tokens, DRAFT=0 | 2,048 decode | 5.7–11.4 h | **~$7–$13** | ~1.23M activations over 19,200 cells → under the cellwise coverage rule (ASM-2507 v3) undersampled cells are imputed tail-compatible, so this option almost certainly cannot license DEAD — a coarse generation-side look only |
| **S1-tf (RECOMMENDED first cut — COARSE look, NOT verdict-capable for DEAD)** | REAP conditional saliency computed TEACHER-FORCED over the broad 256-seq corpus (reuse the proven wave-a pipeline shape + kot-rtrace/2 `on` field; no free generation) | ~32,768 teacher-forced ≈ 15.5 h @ 0.59 tok/s | ~15.5 h | **~$15–$20** | **Power (v3, fix 3):** teacher forcing has no established one-sided ordering for conditional-saliency FLATNESS [ASM-2512 v3] → **a flat result is PROVISIONAL/UNRESOLVED (suggestive, not decisive) — DEAD is unreachable at this tier**; a found tail is likewise PROVISIONAL pending a generation-side confirmation, separately priced and ratified |

**Recommendation (v3, fix 3):** run **S1-tf** as a cheap COARSE first look
(~$15–$20, honest worst-case ledger written and the price re-ratified on #51
first; the coordinator has already posted the S1-tf verdict-asymmetry
CORRECTION to #51), explicitly **not verdict-capable for DEAD**: a found tail
is PROVISIONAL and motivates a separately-priced generation-side confirmation;
a flat result is PROVISIONAL/UNRESOLVED — suggestive, not decisive. **Any DEAD
verdict for the pruning direction requires a generation-side run that passes
the cellwise coverage gate (ASM-2507 v3)** — realistically a right-sized
S1-full, since S1-lite-gen's coverage almost certainly blocks DEAD. Whether a
flat S1-tf justifies that generation-side spend (versus parking the direction
as UNRESOLVED on opportunity-cost grounds) is a maintainer decision on #51
with both prices on the table. The generation-side FALSIFIER-1 confirmation
piggybacks on whichever generation run is eventually ratified; under S1-tf
alone, FALSIFIER-1's generation-side confirmation remains outstanding (0b's
verdict stays the operative one, with its ASM-2510 asymmetry — a ROUTING
claim, unaffected by fix 3).

### 5.3 Run design (unchanged where not repriced)

- **Box/config:** the proven GO-FULL-GLM52 wave-a configuration (OCI via the
  existing Modal wrapper; RAM_GB=55, CAP_RAISE=0, int4 estate, staging manifest
  as in the smoke). **DRAFT=0** (MTP off) so draft-path tokens neither pollute
  saliency nor leak retired-expert traffic — per the menu's probe rule. Nothing
  runs until the run-script's worst-case ledger is written and the REPRICED
  cost is signed off (issue #51).
- **Corpus:** ~256 **broad** calibration sequences, fixed seed, committed with
  sha256 before the run. HARD RULE (menu §3-A, freeze rule): broad-mix REAP-style
  calibration — **NOT** kernel-concept-stratified, NOT `concept_prompts.json`,
  no kernel-derived text at all (a 24-concept corpus is the
  c4-calibrated-a-coding-model failure in reverse). Under S1-tf the items are
  teacher-forced full sequences; under a generation option each item is a
  natural prompt + free generation.
- **Instrument:** kot-rtrace/2 = kot-rtrace/1 + one optional per-row field
  `on` = ‖expert output‖₂ (pre-router-weight), + decode-step emission (the
  rtrace hook already lives in `moe()`, which runs identically at decode).
  ~20–40 engine lines on top of the validated smoke patch; `test_rtrace.c` +
  `trace_analyze.py` invariants extended for the new field; without `RTRACE`
  set, engine output stays byte-identical to upstream (existing property).
- **Saliency:** REAP conditional-impact per cell:
  S(layer,e) = mean over activations of w_e(t)·‖E_e(x_t)‖₂ **conditional on
  activation** (decoupled from firing frequency — frequency is the known-collapse
  null, REAP Table 3), with activation counts reported; under S1-tf, over
  teacher-forced tokens with the ASM-2512 v3 caveat attached (no established
  flatness ordering — both S1-tf verdicts provisional). Report the top
  saliency tail too (super-expert candidates; no exclusion list exists yet for
  GLM-5.2 — this run seeds one but does not claim it).
- **Kill threshold [STIPULATED, ASM-2507 v3 — coverage unit corrected to
  expert CELLS, fix 2 / re-review #7]:** the flatness statistic is computed
  over each layer's full set of **256 expert cells** (19,200 / 75), not over
  selection mass — v2's ≥90%-of-selection-mass resolution rule is WITHDRAWN
  (selection mass concentrates on hot cells, so it could mark a layer
  "resolved" while much of the cellwise saliency tail — the very object under
  test — stayed unmeasured). The DEAD test, fail-closed:
  1. **Per-expert-cell coverage (fail closed):** a cell is MEASURED only if it
     has ≥50 qualifying activations. Report per layer: measured-cell count
     (of 256), the identity of unmeasured cells, and the selection mass they
     carry.
  2. **Conservative tail-compatible imputation:** every unmeasured cell
     (undersampled or unobserved) enters the flatness statistic imputed at
     conditional saliency 0 — treated as tail-COMPATIBLE, never
     tail-incompatible. ρ_ℓ^cons = mean(bottom-quartile conditional saliency
     over ALL 256 cells, with unmeasured cells imputed as above) /
     median(conditional saliency over MEASURED cells only). Both choices are
     conservative AGAINST a flat call: imputation depresses the numerator,
     and the median denominator is not diluted by imputed zeros.
  3. **CI direction (unchanged from v2):** per layer, the bootstrap-over-
     sequences **LOWER** 95% bound of ρ_ℓ^cons. The layer counts as flat only
     if that lower bound ≥ 0.5. ρ ≥ 0.5 remains a **stipulated no-cheap-tail
     threshold** (the bottom quartile costs at least half the median impact),
     not "indistinguishable from median".
  4. **Verdict:** **DEAD (no droppable tail) only if ≥80% of ALL 75 MoE layers
     are flat by the lower bound of ρ_ℓ^cons.** Because unmeasured cells are
     imputed tail-compatible, a layer whose unmeasured cells would occupy the
     bottom quartile can never be called flat — **a flat verdict cannot hide
     behind unmeasured cells.** If imputation alone blocks flatness on >20% of
     layers, the output verdict is UNRESOLVED-COVERAGE, never DEAD; the
     imputation-blocked layer count is always reported.
  5. **Run-type scope (v3, fix 3 / ASM-2512 v3):** under a TEACHER-FORCED run
     (S1-tf), DEAD is unreachable regardless of coverage — a fully flat
     result maps to **FLAT-PROVISIONAL** (suggestive, not decisive); the DEAD
     verdict requires a generation-side run.
  A passing gate licenses ONLY the next measurement (hit-rate-vs-union,
  int4-stacked retention probe, MTP-on acceptance — menu §3-A steps 2–3),
  **never** the 50% headline (steering note: "a flatness histogram must NOT
  license the 50% headline").
- **Outputs:** per-layer saliency histograms + verdict
  (`flatness-gate-v1.json`), and the trace on the output volume → rerun
  `falsifier1_surface_v1.py` unchanged on it → `falsifier1-stage1.json`
  (tier: "generation-side" or "stage1-teacher-forced" per the ratified
  option).

## 6. Honest scope

- **The null is the datum.** Each output (0a descriptive set, 0b falsifier,
  flatness) is a reportable measurement in both directions; DEAD verdicts
  foreclose directions cheaply, which is the steering's stated purpose. But
  (v2) only 0b/Stage-1 can emit falsifier verdicts; 0a is descriptive.
- **The kernel earns nothing here and is presumed to earn nothing.** It appears
  nowhere in the calibration distribution, the corpus, the saliency, or the
  predictor features. Its only Candidate-A role is the optional **post-hoc
  external checker** over a pruned model's outputs — a separate, later,
  separately-priced experiment whose null (kernel-as-text does as well, Law 2)
  must be priced on the real deployment config before any "kernel's home is the
  output seam" claim is banked (steering note's own caution).
- **F1-K untouched.** Read-only reuse of `accum20.stats`/`m4.json`; no contact
  with the F1-K harness, driver, freeze, or readout. (The P0 `git add` of
  `poc/gcp/probe-results/` tracks existing probe OUTPUT bytes; it does not
  touch the F1-K harness or its registered readout.)
- **Known biases carried openly:** in-sample pin (A1 — residual biased low,
  not a floor), config-confounded A3/A4 (MTP/int8/78L vs int4/DRAFT=0/75L),
  prefill-side traces (0b), template corpus (0b), failed atlas coverage gates
  + thin held-out volume (0b family view, template_family × counterpart),
  n=23 (A3/A4), and (v3) NO established one-sided ordering for teacher-forced
  conditional-saliency flatness — S1-tf's flat AND tail-found results are both
  provisional (ASM-2512 v3). Each is tagged where used.

## 7. New assumptions (owner: designer-20)

| ASM | Statement | Tag |
|-----|-----------|-----|
| ASM-2505 (v2) | FALSIFIER-1 kill line: exploitable (predictable ∩ non-resident) **selection mass** < 5pp of total selections at the G50 pin ⇒ routing/prefetch/short-circuit direction DEAD-for-opportunity-cost (wall-clock ceiling 1/(1−d·0.211) = 1.035×–1.203× over d∈[0.16 MEASURED … 0.8 STIPULATED]; 1.087×–1.203× on [0.38, 0.8]). Triage band vs the competing REAP lever, NOT a general impossibility claim. Greenlight needs ≥10pp with CI-low ≥5pp. Metric and threshold share the selection-mass unit. Applies at 0b/Stage-1 only | STIPULATED (threshold choice; arithmetic MEASURED-derived) |
| ASM-2506 (v3) | "Surface-predictable" operationalisation: per (layer, feature-class) with ≥200 held-out selections, a discovery-split-fit shortlist of m=16 experts capturing ≥80% of held-out selections; exploitable events require **event-level shortlist membership** (v2 fix 9). The secondary family-level view conditions on **template_family × counterpart** (spans all splits), never prompt_family (the split unit — circular, v3 fix 1), with a reduced ≥50 held-out-selection floor and unresolved-mass reporting | STIPULATED |
| ASM-2507 (v3) | Flatness kill, CELLWISE (coverage unit corrected — re-review #7): per layer over all 256 expert cells, unmeasured cells (<50 qualifying activations, incl. unobserved) are imputed TAIL-COMPATIBLE (conditional saliency 0) in ρ_ℓ^cons = mean(bottom-quartile saliency over ALL cells, imputed) / median(MEASURED cells only); flat only if the bootstrap **lower** 95% bound of ρ_ℓ^cons ≥ 0.5; DEAD only if ≥80% of all 75 layers flat. A flat verdict cannot hide behind unmeasured cells (v2's ≥90%-selection-mass resolution rule WITHDRAWN — it protected mass, not expert-cell coverage). ρ≥0.5 = stipulated no-cheap-tail threshold, not "indistinguishable from median". If imputation alone blocks >20% of layers: UNRESOLVED-COVERAGE, never DEAD. Under teacher forcing DEAD is unreachable (ASM-2512 v3) | STIPULATED |
| ASM-2508 (v2) | Stage-1 cost: v1's ~$2–3 transfer was INVALID (teacher-forced ≠ decode). First-principles band for the v1 design: ~$100–$210 (32,768 decode tok ÷ 0.05–0.1 tok/s × ~$1.14/h). S1-tf first cut ~$15–$20; S1-lite-gen ~$7–$13. Any figure must be re-ratified on issue #51 and confirmed by the run-script worst-case ledger before any run | STIPULATED (rates MEASURED: wave-a $2.51/2.2h; northstar decode 0.05–0.1 tok/s) |
| ASM-2509 | Modal named volume `kot-glm52-wave-a-out` still retains `full/rtrace.jsonl.gz` + `full/trace_manifest.txt` (named volumes survive app teardown; unverified this session — no credentials touched) | STIPULATED (verify first) |
| ASM-2510 | Teacher-forced prefill traces (0b) bound generation-side predictability optimistically: a 0b DEAD is load-bearing, a 0b GREENLIGHT is provisional until a generation-side confirmation | STIPULATED (direction supported by menu risk-5 literature) |
| ASM-2511 | The prompt-level oracle gap (A4) bounds prompt-conditioned residency policies but not within-sequence token-level swapping; treated as complementary evidence, not a FALSIFIER-1 bound. Same reason A2 bounds static/prompt-level residency only | STIPULATED |
| ASM-2512 (v3) | Teacher forcing has **NO established one-sided ordering for conditional-saliency FLATNESS** — the one-sided optimism argument is for routing predictability/replaceability (ASM-2510's domain, unaffected), not saliency. S1-tf is therefore a cheap COARSE first look only: a found tail is PROVISIONAL pending a separately-priced generation-side confirmation; a flat result is **PROVISIONAL/UNRESOLVED — suggestive, not decisive, NOT a load-bearing DEAD**. Any DEAD verdict for the pruning direction requires a generation-side measurement passing the ASM-2507 v3 cellwise gate (v2's asymmetric-DEAD claim WITHDRAWN; correction already posted to issue #51 by the coordinator) | STIPULATED |

## 8. Self-check

| Constraint | Status |
|---|---|
| Memo only, working tree only; no spend, no VM, no git | ✔ — one file revised; data inspection was read-only; no credentials, no network, no commits (P0 git-add is a coordinator instruction, not an action taken here) |
| Data inventory + honest $0-vs-needs-collection split is the load-bearing part | ✔ §1–§2; v2 answer: aggregate-only in-repo AND family-conditionals dropped from the committed parquet → NO predictability estimate at $0-now; per-token traces exist off-repo (volume) → three-tier split |
| Exact $0 plan coordinator can execute (inputs, computation, schema); reuse analyze_routing_v3.py; note new code | ✔ §3 (P0 + A1–A4 descriptive, A6 hard-coded PROVISIONAL-NEEDS-0b, JSON schema; v3 loader/differencing/bootstrap reused; ~150 new lines named) |
| Stage-1 spec: box, DRAFT=0, generation-side vs teacher-forced options, ~256 broad seqs, kill threshold; sign-off-gated spend (issue #51) | ✔ §5, ASM-2507 v3 / 2508 v2 / 2512 v3 |
| Kernel OUT of calibration; kernel only as optional post-hoc checker priced separately vs kernel-as-text; NULL reportable | ✔ §5.3 corpus hard rule, §6 |
| STIPULATED-vs-MEASURED tags throughout | ✔ — every load-bearing number tagged; MEASURED figures re-derived (h_pin 0.7628 reproduction; accum20 totals; coverage-gate failures; f000.out config; M3 d-range; wave-a $/h and token count) |
| ASM-2505+ with owner designer-20 | ✔ §7 (2505–2512) |
| No @handle strings | ✔ |
| Does not touch F1-K | ✔ — read-only reuse of probe output bytes; F1-K runs to its registered readout |
| **v2 fix 1: A5 out of $0 tier (parquet drops family conditionals)** | ✔ §1 D5 row, §2 tier table, §3 A5 tombstone, §4 step 4 |
| **v2 fix 2: D3 untracked — P0 commit precondition + sha pin** | ✔ §1 D3 row, §3 P0, output schema `d3_commit` |
| **v2 fix 3: 0.2372 = biased in-sample point estimate, not a floor** | ✔ §1 headline bullet, §3 A1, §6 |
| **v2 fix 4: A3/A4 exclude layer 78 + disclose MTP/int8-vs-int4 config mismatch; re-scoped prompt-fixed** | ✔ §3 disclosure block, A3, A4, output schema |
| **v2 fix 5: exploitable metric and threshold both in selection mass** | ✔ §4 step 3, ASM-2505 v2 |
| **v2 fix 6: ASM-2505 arithmetic 1.087–1.203× on [0.38,0.8], d-range widened to 0.16, opportunity-cost framing** | ✔ §3 threshold block, ASM-2505 v2 |
| **v2 fix 7: ASM-2507 lower-bound CI + fail-closed coverage gate + gloss corrected** | ✔ lower-bound CI + gloss retained; the coverage UNIT is superseded by v3 fix 2 (cellwise) — §5.3, ASM-2507 v3 |
| **v2 fix 8: A2 bounds static/prompt-level residency only** | ✔ §3 A2, ASM-2511 |
| **v2 fix 9: 0b counts event-level shortlist membership** | ✔ §4 step 3, ASM-2506 |
| **v2 fix 10: Stage-1 repriced ~$100–$210; must be re-surfaced on #51; cheaper options + recommendation** | ✔ §5.1–5.2, ASM-2508 v2 |
| **v2 fix 11: Stage-0a verdict hard-coded PROVISIONAL-NEEDS-0b** | ✔ §3 A6, output schema |
| **v3 fix 1 (re-review #1): 0b family-view predictor grouping = template_family × counterpart — prompt_family is the split unit (circular); choice stated; undersampled cells → unresolved/DESCRIPTIVE, never silently bucketed** | ✔ §4 step 4, ASM-2506 v3 |
| **v3 fix 2 (re-review #7): ASM-2507 coverage protects per-expert-CELL activation counts — unmeasured cells imputed tail-compatible; a flat verdict cannot hide behind unmeasured cells; selection-mass resolution rule withdrawn** | ✔ §5.3 steps 1–4, ASM-2507 v3, §5.2 S1-lite-gen caveat |
| **v3 fix 3 (re-review #10): S1-tf load-bearing-DEAD withdrawn — flat = PROVISIONAL/UNRESOLVED (coarse first look, suggestive-not-decisive); any pruning-direction DEAD requires generation-side confirmation; correction posted to #51 by coordinator** | ✔ headline bullet 2, §2 tier table, §5.2 table + recommendation, §5.3 step 5, ASM-2512 v3, NEXT-ACTION |
| **Stage-0a (A1–A4, PROVISIONAL-NEEDS-0b, descriptive) unaffected by all v3 fixes; remains coordinator-runnable NOW after P0 commit + hash** | ✔ §3 untouched in v3; re-review: Stage-0a APPROVED to run |

---

## NEXT-ACTION

**Runnable NOW ($0, no sign-off needed — coordinator, committed bytes only):**
1. **P0:** `git add poc/gcp/probe-results/` + commit (files exist, currently
   untracked), record the commit + sha256 of `accum20.stats`/`m4.json`.
2. Write + run `poc/glm52-probe/analyze_residual_v1.py` per §3 (A1–A4
   DESCRIPTIVE diagnostics; seed 20260712; fail closed if A1 ≠ 0.7628;
   layer 78 excluded from A3/A4 with the config-mismatch disclosure) →
   `falsifier1-stage0a.json` with verdict hard-coded `PROVISIONAL-NEEDS-0b`.
   This yields: the in-sample residual point estimate (biased low), the
   static-residency GB economics, and prompt-fixed stability/oracle-gap reads.
   **It cannot yield a falsifier verdict** — no predictability estimate exists
   in committed bytes.

**NEEDS RETRIEVAL (~$0, Modal credentials, no compute — the actual falsifier):**
3. Verify ASM-2509: `modal volume get kot-glm52-wave-a-out full/rtrace.jsonl.gz`
   (+ `full/trace_manifest.txt`). If present, run `falsifier1_surface_v1.py`
   per §4 (event-level shortlist counting, selection-mass units, family view
   recomputed from raw rows) → `falsifier1-stage0b.json`. A 0b DEAD under
   ASM-2505 v2 kills the routing direction outright; a GREENLIGHT is
   provisional (ASM-2510). If the volume was reaped, 0b collapses into the
   eventual Stage-1 trace.

**GATED — REPRICED; corrected cost MUST go back to the maintainer on issue #51
BEFORE any run (the existing ~$2–3 sign-off was against a wrong number):**
4. Re-surface Stage-1 pricing on #51: v1 design honestly costs **~$100–$210**
   (32,768 decode tokens at 0.05–0.1 tok/s, ~$1.14/h — §5.1), not ~$2–3.
   Propose the **S1-tf teacher-forced COARSE first cut (~$15–$20)** under the
   corrected ASM-2512 v3 framing — no established one-sided ordering for
   teacher-forced saliency flatness: tail-found = PROVISIONAL, flat =
   PROVISIONAL/UNRESOLVED (suggestive, not decisive), **DEAD unreachable at
   this tier**; the coordinator has already posted this correction to #51,
   and the re-priced band still needs maintainer re-ratification there.
   Present S1-lite-gen (~$7–$13) as a coarse generation-side look that the
   ASM-2507 v3 cellwise coverage gate almost certainly blocks from DEAD, and
   state plainly that **any DEAD verdict for the pruning direction requires a
   generation-side run passing the cellwise gate** (realistically a
   right-sized S1-full) — whether a flat S1-tf justifies that spend is the
   maintainer's #51 call with both prices on the table. Whatever is ratified
   then runs per §5.3 with the worst-case ledger, the ASM-2507 v3 cellwise
   flatness test, and the FALSIFIER-1 piggyback; neither verdict licenses the
   50%-prune headline.
