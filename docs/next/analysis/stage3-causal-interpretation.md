# GLM-5.2 Stage-3 causal ablation — interpretation (Fable, 2026-07-16, rev 2 post-review; UNCOMMITTED — coordinator commits)

Data: `poc/glm52-probe/stage3/results/full/stage3_analysis.json` (single run; method + real-model inertness proof, 18/18 checks:
`poc/glm52-probe/stage3/stage3_summary.md`). cost≈$6.1 / timed_out=False come from the run log `poc/glm52-probe/stage3/results/full_run.log`, NOT
the analysis JSON. Not a programme feasibility conclusion.

**1. What it shows.** [MEASURED] 32 shortlisted cells, 244 items / 1,546 teacher-forced prefills: 22 SAFE-TO-DROP / 6 CHARACTERISE-MORE / 4
LOAD-BEARING; 16-cell skiplist (causal_confidence 0.504–0.812; route-on mean ΔNLL −0.222…+0.042 nats/tok). [STIPULATED] "SAFE-TO-DROP" = route-on
and route-off **MEAN** ΔNLL point estimates under LOW=0.05 nats/tok, no correctness loss (`stage3_analyze.py::classify`), at the cell's selected
positions on THESE items. The gate tests the MEAN only; the intervals are 90% BOOTSTRAP percentile intervals (5th–95th), not 95% CIs, and 8/22 SAFE
cells (5/16 skiplist) have route-on upper bounds >0.05 (main|59|9: mean +0.0416, 90% CI [−0.1324, +0.2380]) — the claim is "MEAN ΔNLL below the
stipulated 0.05 line", NOT bounded harm. main|19|15 (+0.477, 90% CI [0.097, 0.898]) shows the detector is signal-RESPONSIVE — SAFE is contrast, not
insensitivity — but not a pre-declared positive control: NOT validated sensitivity/specificity. Strata only partly matched: all 4 control_rare
droppable, but only 1 of 6 named specialist cells LOAD-BEARING (4 SAFE, 1 CHARACTERISE-MORE). `causal_confidence` is an UNCALIBRATED
evidence-agreement score (equal-weight mean of coverage, route-sign stability, contrib/route sign agreement, on/off contrast) — not statistical
confidence or a posterior; 0.50–0.81 are not confidence levels.

**2. Extrapolation.** The shortlist came from the gate-FAILED Wave-A atlas (routing-mass 0.825<0.95, held-out Spearman 0.63<0.8;
`poc/glm52-probe/wave-a/atlas/atlas_summary.md`), enriched for candidate-droppable strata. **22/32 does not extrapolate** — "69% of 19,456 cells
droppable" must never be stated: (a) non-random enrichment alone forbids any population rate, even had the atlas gates passed; (b) off-items were
drawn from ~zero-routing-mass domains — no coverage of secondary/polysemantic contexts; (c) every tested cell is `main` — the 19,456 denominator
includes 256 untested MTP-only cells; (d) **cells were ablated INDIVIDUALLY** — NO evidence that dropping all 16 skiplist cells SIMULTANEOUSLY is
safe (interaction/additivity untested); (d) is load-bearing for the skiplist's usability. Defensible scope: per-cell characterisation on an enriched
candidate set, one cell at a time. [PROPOSED-ASM (next-free id ≥2383), tag=STIPULATED, load_bearing=true, claim="Stage-3 labels are
individual-ablation mean-ΔNLL evidence on an enriched gate-failed-atlas shortlist of main cells; no population rate, no simultaneous-drop
guarantee", backing_ref="poc/glm52-probe/stage3/results/full/stage3_analysis.json + poc/glm52-probe/wave-a/atlas/atlas_summary.md lines 14-15"]

**3. colibri feed.** Consumable: the 16-cell skiplist as a principled per-layer EXPERT_BUDGET exclusion (vs colibri #254's blind gate-weight
heuristic); the NINE non-null swap_to cells (seven swap_to=None) as CACHE_ROUTE remap targets — eight of nine have swap-arm mean ΔNLL <0.05,
main|63|217→206 sits at +0.0795. Before any speedup claim: (a) a decode-loop A/B — teacher-forced final-logit ΔNLL says nothing about autoregressive
drift or MTP acceptance (EXPERT_BUDGET already degrades acceptance 38%→21%); (b) 16/19,456 ≈ 0.08% of cells → direct I/O saving likely tiny,
near-term value is method validation [ESTIMATE]; (c) per 2(d), applying the whole list at once is itself untested.

**4. Caveats.** (i) n=10 on / 8 off items per cell; FIVE skiplist cells at causal_confidence 0.50–0.57 (0.570/0.564/0.546/0.509/0.504), barely over
stipulated SKIP_MIN_CONF=0.5; 7/32 low-bucket overall. (ii) **Zero cells earned DETERMINISTIC-REPLACEABLE** — that gate REQUIRES route-on mean ≥
MID=0.15 and none of the 15 swap-tested cells reached it (max +0.0899): the shortlist mostly failed to produce experts that NEEDED replacement, NOT
"15 harmful experts whose substitutes failed"; deterministic replacement stays unevidenced either way. (iii) SEVEN of 16 skiplist route-on means are
positive; +0.0386/+0.0416 are merely the two closest to the 0.05 line — LOW=0.05 is stipulated, not derived from a perplexity budget. (iv) Single
run, no item-set replication, item bias inherited from Wave-A; exclude the 6+4 unresolved cells explicitly, not silently.

**SUBJECTIVE (Fable).** Promising: the *instrument* — verified inert-safe ablation on a 744B model for ~$6, a signal-responsive detector; the causal
layer colibri #175 lacks. Oversold if repeated carelessly: the 22/32 headline (enriched sample), the word "safe" (mean-only, final-logit, 244 items,
no decode-loop or simultaneous-drop evidence), any hint deterministic replacement was shown. Next: measure the delta — Stage-4 speed cohort
(skiplist exclusion + swap_to remaps vs blind EXPERT_BUDGET at matched cap; tok/s + MTP acceptance + quality; kill must fire if earned; est. $10–25
[ESTIMATE]). **#207: stay PAUSED** — causal-evidence gate met; validated speed delta at matched quality not.
