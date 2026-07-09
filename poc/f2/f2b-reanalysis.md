# F2b re-analysis — gap_closed(135M → 1.7B) from logged F2 data

> **PHASE: EXPLORATORY (quarantined).** The (R1,R3) rung pairing was **not** in the
> frozen F2 HE1 pair set {(R1,R2),(R2,R3)}; this estimand was chosen **after**
> unblinding, over already-seen data. Per P2 P-10/G-13 and GR-7 it is uncitable as
> confirmatory evidence, cannot appear in `docs/`/`reports/` claims, and cannot flip
> the F2 verdict (which stands: **FAIL**, `registry/verdicts/f2.json`). Promotion
> path per G-13: register a **new** confirmatory experiment (see §5).
>
> Computed 2026-07-09 by `poc/f2/f2b_exploratory.py` (reuses the pinned
> `analysis/f2.py` machinery verbatim: seed-averaged per-item vectors, best retry
> budget k∈{1,2,4} reselected inside every bootstrap resample, BCa CIs from the item
> jackknife, B=10000, PRNG seed 20260708). **No new model calls, no GPU** — this is
> a purely statistical re-analysis of `results-log/f2.jsonl` (87 eligible final
> runs, 500 D-QA items × 5 seeds per cell). Reproduce:
> `python3 poc/f2/f2b_exploratory.py < results-log/f2.jsonl`

Every claim below is tagged **MEASURED** (computed from logged data), **LIT-BACKED**
(external literature), **STIPULATED** (assumption/design choice), or
**EXTRAPOLATION** (beyond measured range). Coverage disclosure (mandatory, from the
frozen F2 verdict): kernel-expressibility coverage **0.3542** at rung molecules-v0 —
**every accuracy claim here is bounded to the kernel-covered D-QA slice**.

## 1. Why F2 failed, in one paragraph (context)

**MEASURED** (frozen F2 readout, `reports/auto/f2/analysis-output.json`): the frozen
HE1 primary was gap_closed(R1,R2) on D-QA, and its denominator was degenerate —
360M model-alone (0.388) ≤ 135M model-alone (0.394), a −0.006 "gap", giving the
meaningless gap_closed(R1,R2) = −40.13, CI [−135.6, −23.1]. Kill clause (a)
(`gap_below_half`) fired on that artifact, and kill clause (b)
(`competitor_closes_asmuch`) fired on the **same** artifact: with the reference gap
at −40.13, any cheaper arm trivially "closes as much gap". Neither clause says
anything about the verifier on a separating pair. What the frozen record also shows,
**confirmatory** (pre-registered Holm secondaries, all passed at the bootstrap
p-floor ≈ 1e-4): gap_closed(R2,R3) = 2.73 clears the 0.5 bar (`pair_r2r3`); the
kernel verifier beats the gloss-text self-verify+retry arm at matched budget
(`beats_gloss_self_verify`, the RT-2 gate HE1 could not have passed without); beats
the text null (`beats_text_null`); and beats the trained PRM at matched FLOPs
(`prm_beaten`, HC3). Cascade dominance (HE2) **failed** confirmatory (Holm p=0.047,
worst-budget IUT) and stays failed — nothing here re-litigates it.

## 2. The (R1 → R3) estimand on the logged data

Estimand (same form as P8 §1.2, new pairing): gap_closed(R1,R3) =
(acc[135M+kernel-verify, best k] − acc[135M alone]) / (acc[1.7B alone] − acc[135M
alone]), best k∈{1,2,4} reselected inside every bootstrap resample.

**MEASURED** (exploratory; 95% BCa CIs over 500 items; accuracies are kernel-covered
D-QA slice, mean over 5 seeds):

| arm | acc | 95% BCa CI |
|---|---|---|
| 135M alone (R1) | 0.394 | [0.352, 0.436] |
| 360M alone (R2) | 0.388 | [0.342, 0.428] |
| 1.7B alone (R3) | 0.536 | [0.490, 0.576] |
| **135M + kernel-verify-retry (best k=4)** | **0.635** | **[0.602, 0.668]** |
| 135M + gloss-text self-verify-retry (best k=2) | 0.399 | [0.373, 0.426] |
| 135M + trained PRM verifier | 0.411 | [0.375, 0.447] |

| statistic | value |
|---|---|
| **gap_closed(R1,R3)** | **1.696**, 95% BCa CI **[1.396, 2.145]** |
| one-sided 95% BCa lower bound | 1.439 (clears the 0.5 bar; also clears 1.0) |
| p(gap > 0.5), p(gap > 0), p(gap > 1.0) | all at the bootstrap floor 1/(B+1) ≈ 1e-4 |
| gloss self-verify closes | 3.4% of the R1→R3 gap |
| trained PRM closes | 12.1% of the R1→R3 gap |
| verify beats gloss arm / PRM arm | p ≈ 1e-4 / p ≈ 1e-4 (paired bootstrap) |
| FLOPs/query, verify@k=4 vs 1.7B alone | **0.094×** (vs 360M alone: 0.433×) |
| item flips, verify@k=4 vs alone (covered slice) | 272/500 up, 0 down |
| seed direction (C-4, frozen output, same cells) | consistent (`seed_sign_consistent: true`) |

Plain reading (exploratory): on the covered slice, the 135M model with the kernel
verifier doesn't just close the gap to the 12.6×-larger 1.7B model — it **overshoots
it** (0.635 vs 0.536, non-overlapping 95% CIs) at ~9.4% of the 1.7B FLOPs/query,
while the same retry loop driven by gloss-text self-verification (3.4%) or a trained
PRM (12.1%) barely moves. The beats-gloss and beats-PRM comparisons are the same
R1-hosted arm contrasts that already passed as pre-registered Holm secondaries in
the frozen readout — only the gap-denominator (the pairing) is new here.

## 3. Instrument finding: the external-slice secondary was vacuous, not negative

**MEASURED**: the verify arm's `item_correct_external` vector is byte-identical to
the model-alone external vector at every k∈{1,2,4} (0 item flips; acc 0.240 = 0.240;
1.7B alone on the same slice: 0.614). **Cause (code, not conjecture)**: in
`poc/f2/runner/f2_runner.py`, `ext_vector()` calls `run_alone()` unconditionally —
the external D-EXT slice was **never passed through verify-retry in any arm**. The
frozen `external_slice` secondary (RT-7a, p=1.0) therefore compared alone-vs-alone
and could not have passed under any true effect. This **corrects the post-mortem
record** (kernel-of-truth-97r describes it as "gains do not transfer off in-house
D-QA items"): off-slice transfer was not refuted; it was **not measured**. The
programme currently has zero informative evidence on whether the verifier lift
transfers to externally-authored items.

## 4. Epistemic status — what is and is not citable

- **Confirmatory (citable now)**: the pre-registered, Holm-passed F2 secondaries —
  gap_closed(R2,R3) > 0.5, verifier beats gloss self-verify (RT-2), beats text null,
  beats trained PRM (HC3), each p ≈ 1e-4; instrument gate valid; seed-sign
  consistent. Also confirmatory: HE2 cascade dominance FAILED; the F2 primary FAILED
  (on a degenerate denominator, but FAIL is the verdict and it stands).
- **Exploratory (this document; uncitable as confirmatory)**: everything in §2.
  Three reasons it must stay quarantined even though the machinery is identical to
  the pinned script: (i) the (R1,R3) pairing was chosen **after** seeing that
  (R1,R2) was degenerate — a data-dependent estimand choice (the forking is bounded:
  it is the only remaining pairing with the verifier hosted at R1, but bounded
  forking is still forking); (ii) the same 500 items have now been used for best-k
  selection, the frozen readout, and this re-analysis; (iii) GR-7 is categorical —
  anything outside the pinned script is exploratory, no exceptions for "obvious"
  cases, because the exceptions are how post-hoc rationalisation gets in.
- **STIPULATED**: greedy decoding + fixed seeds make the logged pipeline
  deterministic, so re-running the *same* items would reproduce these numbers
  identically — a same-items "confirmation" run has zero evidential value.
- **EXTRAPOLATION guard**: nothing here extends the frozen extrapolation envelope
  (measured range 135M–1.7B; direction-only language to 7B; PRM verdict indexed to
  the PRM size class tested). The >100% closure at (R1,R3) is a covered-slice,
  ≤1.7B, this-PRM, this-item-distribution result.

## 5. Decision (delegated): fresh out-of-sample run — **YES, warranted**

**Recommendation: spend the ~$4–8 (STIPULATED estimate, consistent with logged
usd/query magnitudes; F2's cap was $60) on a small, pre-registered, out-of-sample
confirmatory experiment `f2b`.** The existing evidence does *not* suffice for the
headline the pivot needs, for four reasons:

1. **The pivot's headline claim is currently quarantined.** The story worth telling
   — "135M + kernel verifier matches/beats 1.7B-alone on covered content at ~0.09×
   FLOPs" — exists only in §2, which G-13 makes uncitable. The confirmatory
   secondaries support a *weaker* adjacent claim (R2-hosted verifier closes the
   R2→R3 gap; kernel verification beats gloss/PRM baselines) inside an experiment
   whose verdict line is FAIL. Reviewers will discount Holm secondaries of a failed
   primary; a clean pre-registered primary on new items is the difference between
   "post-hoc salvage" and "replicated finding".
2. **The transfer question is open because the instrument was broken (§3), and only
   a new run with the fixed runner can answer it.** This is not optional rigor: the
   current record (issue 97r) actively *mis-states* the external slice as a measured
   zero-transfer. Leaving that uncorrected is worse than the $8.
3. **Item reuse is real risk, not ritual**: best k=4 was selected on these 500
   items and the estimand was chosen after unblinding. The exploratory lower bound
   (1.44) is far above the 0.5 bar, so if the effect is real, replication on fresh
   items is near-certain to pass — and if it is not, that is exactly what we must
   find out before building on the pivot.
4. **Asymmetric cost/benefit**: ~$4–8 and a few GPU-hours vs. promoting the
   programme's central efficiency claim from quarantined to confirmatory. The
   already-stopped rerun was wasteful because it added no *new items*; this one is
   defined by them.

**What f2b must add (and must not be):**

- **NEW held-out items**: a fresh kernel-covered definitional-QA sample (new
  generator seed, item-ID-disjoint from `d-qa`), n ≥ 500 (n=1000 if per-item cost
  permits — the gap denominator ~0.14 makes the ratio CI denominator-noise-bound).
  **Not** a re-run of the logged items: deterministic decode would reproduce §2
  byte-for-byte (STIPULATED above) and add nothing.
- **Fixed instrument**: verify-retry actually applied to the externally-authored
  covered slice (patch `ext_vector` to run the arm's own pipeline), so RT-7a is
  measured for the first time.
- **Pre-registered before any final run** (G-13 promotion; new id, frozen record —
  F2 cannot be amended post-final): primary = gap_closed(R1,R3) one-sided 95% BCa
  lower bound > 0.5, best-k∈{1,2,4} in-resample, same kill clauses (a)–(c) rebound
  to the (R1,R3) pair; secondaries = beats-gloss at matched budget (RT-2), beats-PRM
  (HC3), text null, external slice (fixed instrument), and — registered this time,
  not read off post-hoc — gap_closed(R1,R3) > 1.0 ("135M+verifier ≥ 1.7B-alone").
- **Minimal arm set** (skip R2 entirely; skip cascades — HE2 dominance failed
  confirmatory and is not re-litigated without a design change; skip int4/RAG/SC):
  model-alone R1 and R3 (5 seeds), kernel-verify-retry R1 k∈{1,2,4} (5 seeds),
  gloss-self-verify R1 k∈{1,2,4}, PRM R1, kernel-as-text R1, extraction-instrument
  gate at R1 (P10, ≥300 labelled outputs). Roughly a third of F2's 87 cells.

If the maintainer instead chooses to publish on the existing record alone, the
honest characterisation is: "pre-registered secondaries show the kernel verifier
closes the 360M→1.7B gap and beats gloss-self-verify/text/PRM baselines (p≈1e-4
each, Holm) at 0.43× big-model FLOPs; the primary failed on a degenerate model pair;
the 135M→1.7B >100%-closure figure is exploratory; off-slice transfer unmeasured
(instrument defect)". That is publishable but visibly weaker than what $8 buys.

## Appendix — raw exploratory analysis output

```json
{
  "B": 10000,
  "acc": {
    "alone_R1_135M": 0.394,
    "alone_R2_360M": 0.388,
    "alone_R3_1p7B": 0.536,
    "gloss_self_verify_R1_bestk": 0.3988,
    "prm_R1": 0.41119999999999934,
    "verify_R1_bestk": 0.6347999999999995
  },
  "acc_ci95": {
    "alone_R1_135M": [0.352, 0.436],
    "alone_R2_360M": [0.342, 0.428],
    "alone_R3_1p7B": [0.49, 0.576],
    "gloss_self_verify_R1_bestk": [0.3727999999999997, 0.4263999999999999],
    "prm_R1": [0.3747999999999999, 0.4467999999999995],
    "verify_R1_bestk": [0.6023999999999993, 0.6675999999999993]
  },
  "best_retry_budget_gloss": 2,
  "best_retry_budget_verify": 4,
  "cost_ratio_vs_R2": 0.43272024049088587,
  "cost_ratio_vs_R3": 0.094193627873193,
  "estimand": "gap_closed(R1,R3) — post-hoc pairing, NOT pre-registered",
  "gap_clears_half_bar": true,
  "gap_closed_R1R3": 1.69577464788732,
  "gap_closed_R1R3_ci95": [1.3956043956043958, 2.1454545454545415],
  "gap_closed_R1R3_gloss_arm": 0.03380281690140824,
  "gap_closed_R1R3_onesided95_lower": 1.4385542168674637,
  "gap_closed_R1R3_prm_arm": 0.12112676056337553,
  "n_items": 500,
  "p_beats_gloss_self_verify": 9.999000099990002e-05,
  "p_beats_prm": 9.999000099990002e-05,
  "p_gap_gt_half": 9.999000099990002e-05,
  "p_gap_gt_one": 9.999000099990002e-05,
  "p_gap_gt_zero": 9.999000099990002e-05,
  "phase": "exploratory",
  "seed": 20260708
}
```
