# P8 — Statistical analysis plan + scale-extrapolation methodology (directives §6)

**Status:** pre-registration draft for maintainer sign-off, 2026-07-08 (rev 3 — P7
red-team pre-freeze fixes applied: RT-4 G2 power analysis at the registered n = 500 +
freeze-time decidability lint for every Wilson-bound gate; the missing E8-R power analysis
added as a pre-D-SAE-spend precondition; RT-13 F-H0 family fixed at freeze — the 8
mechanism-primary members are pre-declared, and a member not read out is scored as a
non-rejection, never dropped (C-3, §1.4), matching 03 family-h0.reg and 02 §5.4; RT-12
rung-set / extension-predicate field added to the §1.9 SAP template (field 12) with its
`prereg-freeze` freeze-time lint, matching P1 §0 and §8). Component P8 of the
operational research plan (`docs/research-plan/`). Governed by
`docs/kernel-design-directives.md` §6 (binding): pre-registered analysis plan per experiment,
effect sizes + CIs (never p-values alone), Holm/FDR across pre-declared families, TOST for
every null claim, power justified up front, verdicts as pure functions of pre-declared
thresholds, and literature-grounded scale extrapolation (≥3 rungs, published-law comparison,
stated extrapolation range + uncertainty).
**Author:** Fable planning agent (P8), for @jeswr. Coordination: sparq-org/sparq#1683.
**Consumes:** P1 (`01-hypotheses-experiments.md` — the hypotheses, kill criteria, common
statistical rules, and §4b extrapolation envelopes; all frozen there, refined never relaxed
here), P2 (`02-data-and-reporting.md` §5.4 — the mechanics that pin and execute this plan),
`docs/design-efficiency-track.md` (F0 accounting, scale ladder), and the lit reports
(`reports/lit-llm-injection-priorart.md`, `reports/fixed-vectors-in-llms.md`) for the
published scaling anchors.
**Path note (for P2/P4 tooling):** P2 §5.4 provisionally referenced
`docs/research-plan/08-statistics.md`; the canonical path is **this file**
(`08-stats-and-extrapolation.md`). Registry `analysis_plan_ref.path` must point here; this is
an ops-level naming fix, not a design change.

**Precedence and the refinement rule (binding).** P1's "Common statistical rules" and
per-hypothesis test text are already frozen and binding. P8 may *tighten* (add a correction,
add a robustness gate, resolve an ambiguity conservatively) but never *relax*. Every place
this document goes beyond P1 is listed in §0.2 as an explicit, dated clarification so that
freeze-time review can verify the refinement direction.

---

## 0. Scope and clarifications register

### 0.1 What P8 owns

1. The normative **SAP (statistical analysis plan) template** every experiment's registry
   record instantiates before freeze (§1), including the exact statistic→verdict mapping the
   auto-report (`verdict-gen`, P2 §3) executes.
2. The **scale-extrapolation methodology** (§2): trend fitting across the ladder, functional
   forms, model selection, published-anchor comparison, prediction intervals, and the
   pre-declared rule for when a finding may / may not be claimed to persist at larger scale.
3. Two **worked examples** (§3): HC1 (correctness) and HE1 + HE7 (efficiency).

P8 owns methodology only. The mechanics that make it unalterable (freezing, hash-pinning,
unblinding cutoffs, run-vs-audit separation) are P2's; the numeric thresholds and kill texts
are P1's and are quoted, not restated.

### 0.2 Clarifications register (each a tightening or an ambiguity resolution)

| # | P1 text | P8 resolution | Direction |
|---|---|---|---|
| C-1 | "verdict read from the **Wilson 95% CI bound**" for one-sided α=0.05 threshold tests | Defined as the **one-sided 95% Wilson score bound** (z = 1.645), which corresponds exactly to the one-sided α=0.05 score test. (A two-sided 95% interval's bound would be z = 1.96 — stricter than the declared test; the one-sided bound is the coherent reading.) All threshold verdicts use z = 1.645 bounds; the two-sided 95% interval is additionally *reported* for estimation. | Ambiguity resolved; test and CI now provably agree |
| C-2 | "PASS at ≥2 rungs" (H0, HC/HE series) — no multiplicity rule stated for the rung conjunction | Conjunctive claims are tested as **intersection–union tests** (Berger 1982): every component (each rung, each mandatory-baseline comparison, the cost bound) tested one-sided at α=0.05; the joint claim's level is ≤0.05 with **no correction needed** — and requiring all components is strictly conservative. Where P1 explicitly demands Holm inside a conjunction (HE2 across budgets; HE4 across rungs), P1's stricter rule stands. | Tightening-consistent; principled basis stated |
| C-3 | H0 is a disjunction over 8 mechanism primaries; P1 declares no cross-experiment correction | New pre-declared **cross-experiment family F-H0** = the primary endpoints of {HC1, HC2, HE1, HE2, HE3, HE4, HE5, HE6} — the 8 mechanism-primary members are **fixed at freeze** (RT-13). An H0-YES additionally requires the winning mechanism's primary p to survive **Holm at α=0.05 over these 8 fixed members**; a member not read out (e.g. its tier pruned) is scored as a **non-rejection, never dropped from the family** — membership is never data-dependently selected (materialised as a `family-h0` registry record per P2 §5.4 / P3 family-h0.reg). Without this, 8 shots at α=0.05 give up to ~34% family-wise false-YES risk under the global null. | Pure tightening |
| C-4 | "≥5 paired seeds… paired permutation tests" — level of analysis unstated | Primary endpoints are **item-level, seed-stratified** (permute/bootstrap within seed blocks); a new pre-declared robustness secondary requires the effect sign to agree in **≥4/5 seeds** for any PASS involving a trained condition (E5 achieved 5/5). Seed-level-only tests can never carry a verdict (5 seeds have power 0.8 only for d ≈ 1.4 — §1.6). | Tightening |
| C-5 | TOST default "Cohen's d = 0.5"; proportion endpoints use h in several kill texts | Margin table fixed per endpoint type (§1.5); TOST operationalised as **two one-sided tests at α=0.05 each ⇔ the 90% CI lies inside the equivalence interval**. NULL requires TOST pass; non-significance without TOST pass is INCONCLUSIVE (P1 verbatim). | Ambiguity resolved |
| C-6 | "WLS slope on log-params, 90% CI" — no functional-form or PI procedure stated | §2 fixes the candidate forms, selection rule, and prediction-interval procedure; with exactly 3 rungs the parametric PI is nearly vacuous (t₀.₉₅,df=1 = 6.31), so the bootstrap envelope is primary and 3-rung extrapolations are capped at direction + order-of-magnitude (§2.3). | Ambiguity resolved conservatively |
| C-7 | Rounding unstated | Analysis scripts compute in IEEE-754 float64 end-to-end; **no rounding before any comparison**; display rounding only in rendered reports. Declared in every pinned script header (P2 §3.1 grammar note). | Ambiguity resolved |
| C-8 | P1 (post-RT-4) mandates a freeze-time decidability lint for Wilson-bound gates; E8-R previously had no power analysis anywhere (P7 §6) | §1.6 operationalises the lint (formula + the worked G2 n = 500 case, with the pre-computed INCONCLUSIVE band) and adds the **E8-R stable-pair power floor**: detectable ρ derived from the realized seed-stable subset size, with n ≳ 85 matched pairs required to power the E8 prior ρ ≈ 0.39 at α = 0.01 — a pre-D-SAE-spend precondition in the e8r SAP | Pure tightening (2026-07-08, P7 RT-4/§6) |

---

## 1. The per-experiment statistical analysis plan (SAP) template

Every registry experiment record (P2 §1.2) pins one instantiated SAP via `analysis_plan_ref`
(path = this file, anchor = the experiment's SAP block, sha256 at freeze). The pinned
`analysis_script` implements the SAP; the freeze-time review item "script implements plan"
(P2 §5.4) checks it field-by-field against §1.9's template. A SAP with any field marked TBD
cannot freeze.

### 1.1 Primary-test selection (decision table + justification)

Exactly one primary endpoint per experiment (P2 schema-enforced). The test is chosen by the
endpoint's data shape from this closed table; choosing outside the table requires a
freeze-time justification block reviewed by a non-author (same identity rule as P2 G-6).

| Endpoint shape | Primary test | Effect size + CI | Justification |
|---|---|---|---|
| Paired per-item binary outcomes, two arms (accuracy/catch/corrected) | **Seed-stratified paired permutation test** on the mean per-item difference (B = 10⁵ permutations, seed pinned); exact McNemar as cross-check when discordant pairs < 50 | Cohen's **h** (arcsine-stabilised) and raw risk difference (pp); **BCa bootstrap 95% CI** (B = 10⁴, resample items within seed blocks, seed pinned) | Distribution-free; respects the item pairing (same items, all arms — F0 fairness rule 1) and the seed blocking; h is variance-stabilising near the accuracy bounds |
| Rate vs fixed threshold (catch ≥0.80, precision ≥0.9, FP ≤2%, fragment ≥1%, location ≥80%) | **One-sided exact binomial** vs threshold, α=0.05; verdict from the **one-sided 95% Wilson score bound** (C-1) — the bound, not the point estimate, must clear the threshold (P1 verbatim) | Point rate + one-sided 95% Wilson bound (+ two-sided 95% interval, reported) | Exact small-sample validity; the Wilson bound rule makes the verdict a pure function of (x, n, threshold) |
| Paired continuous per-item quantities (FLOPs/query, latency, bytes, loss) | Seed-stratified paired permutation on the mean (or median where pre-declared for latency p50/p95) difference | Cohen's **d** on paired differences + raw ratio; BCa 95% CI | As row 1; ratios reported because kill criteria are stated as ratios (≤0.8×, ≤1/2) |
| Frontier/dominance across a pre-registered budget grid (HE2) | Per-budget paired bootstrap; **Holm across budgets** (P1 verbatim — stricter than the IUT minimum, kept) | Per-budget Δaccuracy at matched expected FLOPs, with CIs | P1-frozen; dominance = every budget significant post-Holm |
| Pareto-hull membership (HE5/F5, F0 §3.2) | Bootstrap over items → resampled frontier; primary statistic = fraction of resamples in which the candidate point lies strictly outside the baseline hull; reject iff ≥0.95 | Distance-to-hull (signed, in the frontier's y-units) + 95% CI | Hull membership is a deterministic geometric predicate; the bootstrap propagates measurement noise into it honestly |
| AUC comparison (E8-D) | **DeLong test**, one-sided, ΔAUC ≥ 0.05 margin (P1 verbatim) | ΔAUC + DeLong 95% CI | Standard correlated-AUC comparison |
| Correspondence vs nulls (E8-R) | Permutation test vs shuffled-kernel null (concept-label permutation, B = 10⁴), p < 0.01 per pair (P1 verbatim) | Spearman ρ + BCa bootstrap 95% CI | P1-frozen |
| Scale-slope claims (HC5, HE7, HS13) | **WLS on log₁₀(params)** per §2; "shrinking" ⇔ 90% CI on slope excludes 0 from below (P1 verbatim) | Slope per decade of params + 90% CI + PI at target rung | §2 owns this row |
| Deterministic counts over pinned corpora (G6/G7) | No test — deterministic count, threshold comparison (P1 verbatim) | The count and denominator | Nothing stochastic |
| Human-annotation rates with two annotators (G2/G3, HS-A) | Exact binomial vs threshold as row 2, on **adjudicated** labels; Cohen's κ reported; κ < 0.4 ⇒ INSTRUMENT-INVALID (pre-declared gate) | Rate + Wilson bounds; κ + 95% CI | Adjudication before unblinding of the rate; low agreement invalidates the instrument rather than the hypothesis |

**Sidedness rule.** Every kill criterion in P1 is directional; all primary tests are
one-sided at α=0.05 in the pre-declared direction. Two-sided tests appear only in
estimation-only secondaries.

### 1.2 Estimands (stated before tests)

Every SAP names its estimand in words and formula *before* naming the test — the quantity, the
population (which item corpus, which covered slice), the arm contrast, and the summary
(mean/median over items; median over seeds for the metric-vector V tables per P2 §3.2).
Example (HE1): "gap_closed(R1,R2) = (acc₄ − acc₁)/(acc₂ − acc₁), accuracies = mean per-item
kernel-covered-slice accuracy over the pinned item corpus, arm indices per the frozen record,
at the best pre-registered retry budget k∈{1,2,4} where 'best' is selected on the pre-declared
selection metric (accuracy at min expected FLOPs) — the selection is part of the estimand, so
no post-hoc knob-fitting (F0 §3.1)."

### 1.3 Alpha and error-rate policy

- Per-experiment primary: α = 0.05 one-sided.
- Conjunctive claims (multi-rung PASS, "beats text null AND cost bound"): intersection–union,
  each component at α=0.05, joint level ≤0.05 (C-2).
- Disjunctive claims: Holm within the pre-declared family (§1.4).
- Slope CIs at 90% (P1-frozen convention); everything else 95%.
- The verdict is computed from the pre-declared statistic vs threshold only (directives §6);
  p-values are never reported without effect size + CI (report template renders all three).

### 1.4 Multiple-comparison families (the pre-declared family definitions)

Families are declared here once; each experiment's SAP names which apply. No family may be
created, split, or merged after freeze except by pre-unblinding design amendment (P2 G-3).

| Family ID | Members | Correction | Rationale |
|---|---|---|---|
| **F-primary(exp)** | The single primary endpoint | None (exactly one test) | Schema-enforced singleton |
| **F-secondary(exp)** | All within-experiment secondaries | **Holm, α=0.05** (P1-frozen) | Verdict-adjacent; strong FWER control |
| **F-rungs(exp)** | The primary replicated across ladder rungs, when the claim is conjunctive ("at ≥2 rungs") | IUT: each rung α=0.05, no correction (C-2); where P1 says Holm (HE4), Holm | Conjunction is self-protecting |
| **F-budgets(F2b)** | HE2 dominance across escalation budgets | Holm, α=0.05 (P1 verbatim) | Frozen in P1 |
| **F-H0** | Primaries of {HC1, HC2, HE1–HE6} — the 8 members **fixed at freeze**, never data-dependently selected (RT-13) | **Holm at α=0.05 over the 8 fixed members**; a member not read out is scored as a **non-rejection (not dropped from the family)**; materialised as registry record `family-h0` (P2 §5.4 cross-experiment mechanism; P3 family-h0.reg) | The programme-level disjunction (C-3) |
| **F-explore(exp)** | Descriptive batteries: per-error-class breakdowns (HC1), per-violation-class rates (HC2), per-cell decode grids, ablation grids | **Benjamini–Hochberg FDR, q = 0.10**, flag-for-discussion only | Estimation/discussion; can never enter `verdict_rules` (P2 §2.4 keeps them out of the log's verdict path) |

Rule: a statistic corrected under F-explore may never be quoted as evidence of a hypothesis;
promoting one means a new confirmatory experiment (P2 G-13).

### 1.5 Equivalence testing (TOST) — margins fixed now

A NULL verdict (as opposed to INCONCLUSIVE) requires TOST: two one-sided tests at α=0.05,
equivalently the 90% CI of the effect entirely inside the pre-declared equivalence interval.
Margins by endpoint type, fixed before any run:

| Endpoint type | SESOI / equivalence margin | Source |
|---|---|---|
| Standardised paired continuous | \|d\| < 0.5 | P1 default, frozen |
| Paired proportions (catch/accuracy contrasts) | \|h\| < 0.2 | P1 (HC1, HC3, HE4 kill texts) |
| Ratio bounds (tokens-to-target ≤0.8×; FLOPs ≤1/2) | Equivalence to 1.0 declared iff 90% CI of the log-ratio ⊂ [log 0.9, log 1.11] (i.e. within ±10% of parity) | New, pre-declared here; a "no saving" NULL must exclude even a 10% saving |
| Slope (scale trends) | "flat" declared iff 90% CI ⊂ (−10%, +10%) per decade of params | Matches HE7's material-shrinkage bound |
| Rates vs thresholds | No TOST — the Wilson-bound rule is already two-decision (clear / not clear); "not clear + upper bound below threshold" = FAIL, between = INCONCLUSIVE (P1 HS3 pattern generalised) | C-1 |

The TOST outcome is a named boolean field in `analysis-output.json`
(`tost_equivalence_pass`), consumed by the NULL verdict rule — never computed ad hoc.

### 1.6 Power / sample-size justification (computed up front, formulas fixed)

Formulas (one-sided α=0.05, normal approximation; exact power by simulation in the pinned
script's fixture tests where n < 100):

- Paired proportions at effect h: n = (z₁₋α + z₁₋β)²/h². For h = 0.2, power 0.90:
  **n ≈ 215 items**. At the F2/E9 default n = 500: power ≈ 0.998 for h = 0.2; minimum
  detectable effect at power 0.90 is **h ≈ 0.13**.
- TOST at margin h = 0.2, true effect 0, power 0.90: n ≈ (1.645+1.645)²/0.2² ≈ **271 items**
  — so n = 500 also powers the NULL branch. **Rule: n_planned must power both the rejection
  branch (at the kill-criterion effect) and the TOST branch (at the margin, under true zero),
  each ≥0.90; the SAP shows both numbers.**
- Threshold rates via Wilson bound: reliable (power 0.90) clearance of threshold θ at n
  requires true rate ≳ θ + 2.93·√(θ(1−θ)/n) (crude approximation; exact power by simulation
  at the true-rate variance where it matters). Worked: HC2's catch ≥0.80 at n = 300 needs
  true rate ≳ **0.86**. **G2 at n = 500 — the worked decidability case (P7 RT-4).** At the
  originally-scheduled n ≈ 50–100 the 0.9 precision gate is undecidable at any realistic
  precision (n = 100 needs true precision ≳ **0.96**; a perfect 50/50 gives LB ≈ 0.93 and a
  single error drops it to the line). G2 is therefore **registered at n = 500 gold
  subsumption judgments** (P1 HS2 / P3 g2.gold): at n = 500 the one-sided Wilson lower bound
  clears 0.9 with power ≥0.90 when true precision ≳ **0.94** (critical p̂ ≈ 0.920), and the
  FAIL branch (upper bound below 0.9) is decidable with power ≥0.90 when true precision
  ≲ **0.86** (critical p̂ ≈ 0.876); the pre-computed not-well-decidable band ≈ (0.86, 0.94)
  is quoted in the g2 SAP so an in-between INCONCLUSIVE cannot be spun either way.
  These detectable-alternative numbers are printed in the SAP so an underpowered gate is
  visible before spend.
- **Decidability lint (freeze-time, binding; P7 RT-4 — mirrored verbatim in P1's common
  rules): every Wilson-bound gate must be shown, at freeze, to be powered for its threshold
  at its planned n.** The registry entry quotes the detectable alternative computed as above
  (exact/simulated where n < 100 or the rate is extreme), and n must make the gate decidable
  at the **expected** rate, not only the optimistic one; `prereg-freeze` refuses an entry
  failing this lint (the same fail-closed pattern as P3 GR-1's tier-sum lint). G2's n = 500
  sizing is the worked example; the same audit applies to every threshold gate in §1.1 row 2
  (E9-C FP ≤2% at n = 300 clean records needs true FP ≲ 1.1% — fine; G8's 1% fragment gate at
  n = 1000 — fine; G9's +10-point margin at N = 50 is tight and its SAP must print the
  detectable alternative before freeze).
- **E8-R correspondence power (added per P7 §6; required before any D-SAE spend).** E8-R's
  primary is a permutation test (p < 0.01, one-sided, P1 verbatim) on Spearman ρ over the
  **seed-stable matched concept–feature pairs** (~30% of features per Paulo–Belrose).
  Planning approximation (Fisher z with the Spearman SE inflation, SE ≈ 1.03/√(n−3); exact
  power by permutation simulation in the pinned script's fixtures): at α = 0.01 and power
  0.90 the minimum detectable ρ ≈ tanh(3.61·1.03/√(n−3)). Worked: n = 54 pairs (the full
  kernel-v0 concept set) detects only ρ ≳ **0.48** — **underpowered (power ≈ 0.70)** for the
  E8 prior ρ ≈ 0.39; detecting ρ ≈ 0.39 at power 0.90 needs **n ≳ 85 stable matched pairs**.
  The e8r SAP must therefore derive its detectable ρ from the **realized** stable-subset
  size before D-SAE spend: if the stable subset yields < 85 matched pairs, the entry must
  either widen the matched concept set (molecule-tier / wn31-aligned records) before freeze,
  or pre-declare the larger detectable ρ together with the pre-computed not-decidable band —
  a readout in that band is INCONCLUSIVE-by-design and is quoted as such (never as evidence
  against A6, and never as support).
- Seeds: 5 paired seeds give power 0.80 only for seed-level **d ≈ 1.4** (paired t, df = 4)
  and power 0.90 for d ≈ 1.6. Consequence (C-4): seeds are blocks, not the unit of test;
  the ≥4/5 sign-consistency gate is a robustness check, not a test.
- Slope power: with rung SEs from the per-rung analyses, the SAP includes the minimum
  detectable slope at 90% CI given the planned rungs (worked example §3.2). With 3 rungs
  df = 1; with 4 rungs (R1–R4) df = 2 — F7 SAPs must plan 4 rungs for any mechanism whose
  expected |slope| < 0.15/decade, else the CI cannot exclude 0.
- Annotation studies: G3's ~200 judgments are powered ≥0.90 to distinguish a true 10% from a
  true 20% violation rate at α=0.05 (P1 verbatim; verified: h = 0.28, n = 200 ⇒ power ≈ 0.98).

Corpus/#concepts sizing (the third axis): every SAP states the item-corpus size, the number
of distinct concepts it draws on, and the concepts-per-item multiplicity, because items
sharing concepts are not independent — the bootstrap therefore resamples at the level of the
**item×concept cluster** (cluster = the item's covered-concept set's hash) whenever
concepts-per-item overlap exceeds 20% of pairs; declared per experiment.

### 1.7 Paired/seed structure (exact resampling procedures)

- **Pairing:** all arms answer the same items under the same prompts (F0 fairness rule 1);
  analysis operates on per-item across-arm difference vectors.
- **Permutation:** within-item arm-label swaps, stratified within seed blocks (trained
  conditions) — the null respects both structures. B = 10⁵, PRNG seed pinned in the frozen
  record.
- **Bootstrap:** resample items (or item-clusters per §1.6) with replacement within seed
  blocks; recompute the full estimand pipeline per resample (including 'best retry budget'
  selection, so selection uncertainty is inside the CI). BCa acceleration from jackknife over
  items. B = 10⁴, seed pinned.
- **Trained conditions:** ≥5 paired seeds (P1); seed enters as a block; per-seed effects
  reported in the verdict object; the ≥4/5 sign gate (C-4) is a pre-declared secondary in
  F-secondary(exp).
- **Missing cells:** never imputed; P2 step-4 completeness gate ⇒ INCOMPLETE-DATA.

### 1.8 The exact statistic→verdict mapping (what verdict-gen executes)

The pinned analysis script writes `reports/auto/<id>/analysis-output.json` with this
**normative field vocabulary** (P2's expression grammar consumes these; unknown pointers fail
at freeze time):

```
/gates/instrument_valid          bool   pre-analysis instrument checks (e.g. F6: trained arms beat step-0; κ ≥ 0.4)
/analysis/primary_reject         bool   primary test rejection at α=0.05 (one-sided, pre-declared direction)
/analysis/primary_p              float  primary p-value (reported, never verdict-bearing alone)
/analysis/effect_size            float  pre-declared scale (h, d, ratio, ρ, ΔAUC, slope)
/analysis/effect_ci_low|high     float  BCa 95% (slope: 90%)
/analysis/wilson_lb|ub           float  one-sided 95% Wilson bounds (threshold endpoints)
/analysis/tost_equivalence_pass  bool   90% CI inside the pre-declared margin (§1.5)
/analysis/holm/<endpoint-id>     bool   per-secondary Holm-corrected rejection
/analysis/seed_sign_consistent   bool   ≥4/5 seeds same-direction (trained conditions)
/analysis/<named-kill-terms>     bool/float  one field per clause of the P1 kill criterion,
                                        e.g. gap_closed_fraction_R1R2, beats_text_null,
                                        text_null_parity_tost_pass, cost_ratio_vs_S,
                                        hull_outside_fraction, catch_rate_wilson_lb
/analysis/slope, slope_ci_low|high, pi_at_target_low|high, anchor_class   (§2 outputs)
```

**Canonical verdict-rule ordering (first-match-wins; instantiated per experiment with P1's
verbatim kill clauses; the catch-all is P2-schema-mandatory):**

```jsonc
[
 {"verdict":"INSTRUMENT-INVALID","when":{"op":"not","a":{"metric":"/gates/instrument_valid"}}},
 {"verdict":"FAIL","when": /* the P1 kill criterion, clause-by-clause, each clause a named
                              analysis field — never re-derived inside the rule grammar */},
 {"verdict":"PASS","when":{"op":"and",
    "a":{"metric":"/analysis/primary_reject"},
    "b":{"op":"and",
       "a": /* every conjunctive P1 requirement: beats_text_null, cost bound, rung IUT */,
       "b":{"metric":"/analysis/seed_sign_consistent"}}}},   // trained conditions only
 {"verdict":"NULL","when":{"metric":"/analysis/tost_equivalence_pass"}},
 {"verdict":"INCONCLUSIVE","when":{"const":true}}
]
```

Order rationale: kill clauses are evaluated **before** PASS so that an outcome satisfying
both (possible when a kill clause concerns a different quantity than the primary) resolves to
the pre-registered kill — the anti-overselling direction. NULL after PASS/FAIL because TOST
equivalence is only meaningful when neither directional criterion fired. The verdict
vocabulary is P2 §3.1's closed set; PASS additionally requires a role-separated re-derivation
before it is citable (P2 G-6 — outside the statistics, stated for completeness).

### 1.9 The SAP fill-in template (copied into each experiment's freeze packet)

```markdown
SAP — <EXP-ID> (hypotheses: <IDs>)                      [every field mandatory; no TBD at freeze]
1  ESTIMAND(S): words + formula; population/corpus + covered slice; arm contrast; summary stat.
2  DESIGN STRUCTURE: unit of analysis; pairing; seed blocks (n seeds); item corpus size + hash;
   #concepts + item×concept clustering decision (§1.6); arms (from the frozen record).
3  PRIMARY ENDPOINT: metric; direction; test (from §1.1 table row N + justification);
   α=0.05 one-sided.
4  EFFECT SIZE + CI: scale (h/d/ratio/ρ/ΔAUC/slope); BCa 95% (slope 90%); B; PRNG seeds.
5  SECONDARIES: list; family F-secondary(<exp>) under Holm α=0.05; estimation-only batteries
   under F-explore BH q=0.10 (flagged uncitable).
6  MULTIPLICITY: which families of §1.4 apply; conjunctive components under IUT (list them).
7  TOST: margin per §1.5 for every endpoint that can produce NULL; the 90%-CI operationalisation.
8  POWER: n_planned; power at the kill-criterion effect (≥0.90); TOST-branch power at the margin
   (≥0.90); minimum detectable effect at n_planned; detectable-alternative for threshold gates;
   seed-level power caveat (§1.6).
9  RESAMPLING SPEC: permutation scheme + B; bootstrap scheme + B; cluster level; seeds.
10 INSTRUMENT-VALIDITY GATES: pre-analysis checks that trip INSTRUMENT-INVALID (never FAIL).
11 STATISTIC→VERDICT MAP: the analysis-output field list (§1.8 vocabulary) and the ordered
   verdict_rules JSON, with P1 kill text quoted verbatim above it.
12 SCALE PLAN — RUNG SET + EXTENSION PREDICATE (P1 §0 rung-set discipline, RT-12): the member
   rung set of every conjunctive claim, DECLARED AT FREEZE and tested under IUT with exactly
   that membership; any conditional extension rung's trigger stated as a MACHINE PREDICATE
   over frozen registry fields (e.g. `primary_reject@R1 AND primary_reject@R2` for E9/HC1 and
   F2/HE1); extension rungs may only STRENGTHEN an already-satisfied conjunction ("PASS at
   R1–R2, replicated at R3"), never substitute into it. Also: per-rung endpoint reuse;
   whether this experiment feeds a §2 slope fit (and which one); the P1 §4b envelope row
   quoted verbatim. Freeze-time lint (binding): `prereg-freeze` checks this field against the
   registry entry's pinned rung set + extension predicate (P1 §8) and refuses to freeze if
   the rung set is undeclared, the extension trigger is not machine-evaluable over frozen
   fields, or the predicate could substitute rather than strengthen.
13 SCRIPT: path; fixture tests (hand-computed expected outputs on mock data — P2 R-4);
   float64/no-prerounding declaration (C-7).
```

---

## 2. Scale-extrapolation methodology (literature-grounded, directives §6)

### 2.1 Inputs and licensing preconditions

A scale-trend fit is licensed only when (P1-frozen): **≥3 rungs** carry the same pre-registered
endpoint under the same SAP (2 rungs license a sign; 1 licenses nothing — P2 G-12 encodes
this as `scale_language_licensed`). Inputs: per-rung effect estimates Δ_r with standard
errors SE_r from the per-rung analyses (never re-pooled raw items across rungs — rungs differ
in model, tokenizer, difficulty); x_r = log₁₀(N_params) for inference rungs, log₁₀(training
FLOPs-to-target) for T-rungs; the effect scale is the mechanism's natural one (fractional
cost saved at iso-accuracy for HE7; relative error-reduction for HC5; accuracy delta for
HS13), pre-declared per fit.

### 2.2 Candidate functional forms and model selection

Fixed candidate set (pre-declared; nothing else may be fit for a verdict):

- **M-lin:** Δ(x) = a + b·x — log-linear in params; the default; 2 parameters.
- **M-pow:** log Δ = log c + γ·x (⇔ Δ = c·N^γ) — power law; fit only when all Δ_r > 0;
  2 parameters. γ is directly comparable to published scaling exponents.
- **M-sat:** Δ(x) = A + B·ρ^x — saturating/exponential-decay; 3 parameters; **fit only with
  ≥4 rungs** (with 3 rungs it is exactly identified — zero residual df, no inference).

Fitting: weighted least squares, weights 1/SE_r²; slope (M-lin b, M-pow γ) with **90% CI**
(P1 convention), t-distribution with n_rungs − 2 df. Selection: **AICc**; retain the simpler
form unless ΔAICc > 2 favours the alternative. **Form-disagreement rule:** if retained and
runner-up forms disagree on the *sign* of Δ at the extrapolation target, the finding's scale
statement is downgraded to "form-dependent — direction-only", regardless of CI widths.

"Shrinking" (kill-relevant, HC5/HE7/HS13): the 90% CI on the M-lin slope excludes 0 from
below (P1 verbatim). "Flat": TOST-style, 90% CI ⊂ (−10%, +10%) per decade (§1.5).
"Flat-or-growing" (HE7 survival): CI lower bound > −10%/decade (P1 verbatim).

### 2.3 Uncertainty on the extrapolated value (prediction interval)

Two procedures, both reported; the **wider governs** the claim:

1. **Parametric WLS prediction interval** at target x*: Δ̂(x*) ± t₀.₉₅,df · s ·
   √(1 + leverage(x*)), df = n_rungs − 2. Honesty note (C-6): at exactly 3 rungs df = 1 and
   t₀.₉₅,₁ = 6.31 — the parametric PI is nearly vacuous; this is a feature, not a bug: 3-rung
   extrapolations are inherently weak and the interval says so.
2. **Parametric bootstrap over rung estimates:** resample Δ_r* ~ N(Δ_r, SE_r) per rung
   (10⁴ draws, seed pinned), refit the retained form, take the 5–95% envelope of Δ̂*(x*).
   This propagates measurement error but **not** form error — which is why the
   form-disagreement rule (§2.2) sits above it.

**Range cap (P1 §4b, restated as the operative rule):** extrapolation extends **at most one
order of magnitude in params beyond the top measured rung**, stated as direction-only unless
the 90% PI at the target is tight enough to exclude the practical-significance floor question
in one direction. Beyond one OOM: prohibited under every circumstance without new
measurement. Every extrapolated statement carries: the fitted form, the PI, the licensing
assumption (the P1 §4b envelope row, quoted verbatim by verdict-gen), and the literature bias
direction (§2.4).

### 2.4 Comparison against published scaling laws (the anchor table)

Procedure per finding: (i) look up the pre-declared anchor row below (mirrors P1 §4b);
(ii) transform the fitted trend into the anchor's units where possible (exponent vs exponent;
relative-lift-per-decade vs the anchor's reported trend); (iii) classify into one of four
pre-declared classes; the class is a named field (`/analysis/anchor_class`) in the analysis
output and appears in the verdict object:

- **CONSISTENT** — our 90% CI overlaps the anchor's direction and reported magnitude range.
- **DIRECTIONALLY-CONSISTENT** — sign agrees; magnitude not comparable or outside range.
- **ANCHOR-CONTRADICTING** — sign disagrees with an [established] anchor. Pre-declared
  consequence: **mandatory independent replication before any extrapolation claim** (a trend
  that contradicts the published record is more likely our artifact; cf. P1 HS13's rule).
- **NO-ANCHOR** — no published trend exists. Pre-declared consequence: the envelope is
  **hard-capped at the top measured rung**; direction-only language beyond it, with the
  "no published law" caveat verbatim.

**The anchor table (citations fixed now; each anchor's evidence tag from the lit reports):**

| Anchor | Published result | Applies to | Predicted bias direction at larger scale |
|---|---|---|---|
| **Test-time-compute scaling** — Snell et al. 2024, arXiv:2408.03314 [established]; Liu et al. 2025, arXiv:2502.06703 (1B > 405B on MATH-500 with a PRM; 0.5B > GPT-4o) [established on verifiable domains] | Compute-optimal test-time scaling lets small models beat ≫larger ones when a verifier exists; substitution measured up to frontier-class comparisons | HC3, HC5, HE1, HE2 | Mechanism (verification substitutes for params) persists to frontier; but their verifiers are *trained PRMs* — our deterministic verifier's *relative* value vs a PRM is indexed to the tested PRM size class (P1 HC3 envelope) and must be re-measured, not extrapolated, when the PRM scales |
| **Loss/error scaling of hosts** — Kaplan et al. 2020, arXiv:2001.08361; Hoffmann et al. 2022 (Chinchilla), arXiv:2203.15556 [established] | Host error falls predictably with scale; AND the cautionary anchor: Kaplan's fitted law mispredicted Chinchilla's optimum 1–2 OOM out — the canonical demonstration that fitted scaling laws extrapolate poorly | Every HC/HE trend; §2.3's OOM cap is calibrated to exactly this failure | Raw error headroom shrinks with scale ⇒ absolute verifier catch counts shrink; extrapolate *relative* lift on covered slices only (P1 HC1 envelope) |
| **Frozen-embedding penalty vs scale** — arXiv:2507.04886 (TMLR 2025): frozen non-semantic embeddings converge but 5–10× slower at 0.2–0.5B [established]; **no published scaling study of the penalty exists** (lit-llm-injection §8 open question) | The penalty is documented at ≥100M; its scale-trend is unknown in either direction | HE6 (F6), HS13 (E7) | **NO-ANCHOR** ⇒ envelope hard-capped at top measured rung (T2/T3); P1 §4b HE6 row verbatim |
| **LCM/CALM fixed-semantic-space penalty** — SONAR-LLM, arXiv:2508.05305: token-LM scaling exponent α≈0.79 vs 0.49–0.57 for concept-space variants [claimed]; CALM, arXiv:2510.27688: concept-level efficiency recovered by *abandoning* the fixed semantic space [claimed]; LCM/SONAR base result [established] | Predicting into a frozen semantic space pays a scaling-exponent penalty of ≈0.2–0.3; the penalty attaches to the fixed target geometry | HE3 (M2), M2-output rider, HS13 | Dense-I/O and frozen-space wins **decay** with host scale; any fitted HE3 slope is compared directly against the exponent gap; a non-decaying fit is ANCHOR-CONTRADICTING ⇒ replication first |
| **Parametric knowledge vs scale** — Mallen et al., ACL 2023, arXiv:2212.10511 (PopQA) [established]: larger models absorb popular knowledge, retrieval's edge persists on the long tail; Allen-Zhu & Li, arXiv:2404.05405 [established at their scales]: ~2 bits/param capacity; RETRO, arXiv:2112.04426 [established]: retrieval benefit measured 150M–7B and retained; InstructRetro absorption caveat, arXiv:2310.07713 [established] | Knowledge-externalisation benefits persist with scale but concentrate on the long tail; in-weights knowledge has a measured byte price | HE5 (F1/F5), HS9 | Store benefits shrink on head knowledge, persist on tail ⇒ report head/tail split; byte arithmetic (Allen-Zhu density) extrapolates freely as arithmetic; accuracy leg speaks above 410M only via RETRO's published range (P1 §4b HE5 row) |
| **Interface-locality / Law 2** — synthesis over Cohen et al. ripple results, RAG-over-KEPLM, xRAG's 62–73% fidelity ceiling (arXiv:2405.13792), InstructRetro (lit-llm-injection §7) [established inputs, our synthesis] | Text interfaces improve automatically with host scale; vector interfaces pay capability-independent tolls | HC1, HE3, HE4, HS1 | The kernel-as-**text** null *gains* on the vector/verifier arms as scale grows — the declared bias direction in every envelope that names Law 2; any fit must state whether the text-arm trend was measured concurrently (it always is: the text null is in every experiment) |
| **New-symbol vocabulary extension** — ToolkenGPT, Hao et al., arXiv:2305.11554 (LLaMA-13B/33B) [established] | Frozen hosts accept trained new-symbol embeddings at 13–33B | HE4 (F4), HS1 | Mechanism existence anchored to 33B; effect size vs the text null is NOT anchored — P1 §4b HE4 row: direction to 7B only via F7 |
| **Verify-don't-generate** — Leviathan et al., arXiv:2211.17192 (speculative decoding, 2–3×) [established] | Cheap verification of cheap drafts is a real efficiency primitive at production scale | HE2, HS12 | Topology persists at frontier; only the kernel gate's marginal value over logprob gating needs re-measurement (P1 §4b HE2 row) |
| **SAE feature stability** — Paulo & Belrose, arXiv:2501.16615 (~30% seed-stable) [established]; Templeton et al. 2024 (Anthropic, mid-size production models) [established] | Feature-space structure measured from 125M-class to mid-size production models; quantitative ρ does not transfer across SAE training regimes | HC4 (E8-R/E8-D) | Qualitative only above open-weights ≤7B (P1 §4b HC4 row) |

### 2.5 The pre-declared frontier-persistence rule

An effect **may** be described as "expected to persist at [target scale]" in any report,
paper, or pitch iff **all** of:

1. ≥3 rungs measured under the same frozen endpoint (4 for any M-sat fit);
2. the retained form's 90% slope CI excludes material shrinkage (lower bound > −10%/decade,
   or the mechanism's stricter pre-registered bound);
3. the 90% PI at the target rung (≤1 OOM past the top measured rung) lies entirely above the
   practical-significance floor (default 10% relative improvement — P1 HC5/HE7 verbatim);
4. `anchor_class` ∈ {CONSISTENT, DIRECTIONALLY-CONSISTENT};
5. the statement names the target scale explicitly and quotes the P1 §4b envelope verbatim
   (mechanised by P2's `--citations`/`--paper` scanners and the
   `extrapolation_envelope_verbatim` field).

An effect **may not** be claimed to persist — and the report must say "measured at
[rungs]; not licensed beyond [cap]" — if any of 1–4 fails, if the anchor predicts decay and
the fit cannot exclude decay (CI includes the anchor's predicted slope), or if the target
exceeds one OOM past the top rung. **Frontier-production-scale (≥70B) claims are prohibited
outright at every tier below Tier 5 + new measurement.** A toy-scale effect presented without
a measured trend carries the literature-referenced caveat named in its anchor row (directives
§6, final clause).

---

## 3. Worked examples

Numbers marked *(illustrative)* are fabricated to demonstrate the machinery and appear in no
registry record.

### 3.1 Correctness — HC1 (decode-verify; experiment E9-full)

**SAP instantiation (per §1.9):**

1. **Estimand.** Per-item caught-or-corrected rate difference: p₄₅ − p₃, where p₄₅ = mean
   per-item indicator "error caught (and corrected, arm 5)" for the best kernel arm (4 or 5,
   selection pre-declared: arm 5 iff its repair does not reduce end-task accuracy below arm
   4's), p₃ = same for the gloss-dictionary deflation arm; population = the pinned E9 item
   corpus restricted to the kernel-covered slice (M0b), n = 600 items/rung (raising E9-C's
   ≥300 floor to power the paired contrast; see field 8); rungs R1, R2 (R3 if sign).
2. **Structure.** Unit = item; all arms on all items; no trained condition beyond the pinned,
   already-costed adapter ⇒ seed blocks trivial (inference seeds pinned per arm);
   item×concept clustering ON (definitional items share concepts heavily).
3. **Primary test.** §1.1 row 1: seed-stratified (here: cluster-aware) paired permutation on
   the per-item caught/corrected difference, one-sided (kernel > gloss), α=0.05, B = 10⁵.
   Justification: paired binary outcomes on identical items; distribution-free.
4. **Effect size.** Cohen's h + raw pp difference; BCa 95% CI, B = 10⁴, cluster bootstrap.
5. **Secondaries (F-secondary(e9-full), Holm α=0.05):** end-task accuracy after repair vs
   arm 3 (kill-relevant); catch-set overlap fraction (arm 3's catches ∩ arm 4/5's, ≥90% ⇒
   kill clause); marginal cost ratio. **F-explore (BH q=0.10, uncitable):** per-error-class
   catch breakdown — mandatory in the report (P1: "any HC1 PASS must name the error classes
   only structure catches") but estimation-only.
6. **Multiplicity.** Rung conjunction (PASS needs ≥2 rungs) under IUT — each rung α=0.05.
   HC1's primary joins family **F-H0** (Holm across mechanisms for the H0-level claim).
7. **TOST.** Margin h = 0.2 (P1 verbatim); NULL iff 90% CI of h ⊂ (−0.2, 0.2).
8. **Power.** At n = 600, power at h = 0.2 ≈ 0.999; MDE at power 0.90 ≈ h = 0.12; TOST-branch
   power at margin 0.2 under true zero ≈ 0.95 (>0.90 required — satisfied). Threshold gates:
   none in HC1 (they live in HC2's SAP: catch ≥0.80 at n ≥ 300 planted violations needs true
   rate ≳0.86, FP ≤2% Wilson upper bound needs true FP ≲1.1% at n = 300 clean records).
9. **Resampling.** As §1.7; clusters = covered-concept-set hash.
10. **Instrument gates.** Non-LLM rubric agreement spot-check κ ≥ 0.4 on a 50-item audit
    sample; decode-stage health: X2-class decode failure rate on the ledger (a decode
    collapse ⇒ INSTRUMENT-INVALID naming the stage, per P1 HC2's "which stage failed" rule).
11. **Statistic→verdict map** (fields per §1.8; kill text quoted verbatim from P1 HC1):

```jsonc
[
 {"verdict":"INSTRUMENT-INVALID","when":{"op":"not","a":{"metric":"/gates/instrument_valid"}}},
 {"verdict":"FAIL","when":{"op":"or",
    "a":{"op":"and",   // kill clause (i): arm-3 coverage of the catch set at ≤ cost
       "a":{"op":"gte","a":{"metric":"/analysis/catch_overlap_by_gloss"},"b":{"const":0.90}},
       "b":{"op":"lte","a":{"metric":"/analysis/gloss_cost_ratio"},"b":{"const":1.0}}},
    "b":{"metric":"/analysis/endtask_delta_tost_pass"}}},    // kill clause (ii) as TOST-bounded null
 {"verdict":"PASS","when":{"op":"and",
    "a":{"metric":"/analysis/primary_reject"},
    "b":{"op":"and",
       "a":{"metric":"/analysis/primary_reject_rung2"},      // IUT: ≥2 rungs
       "b":{"op":"gte","a":{"metric":"/analysis/effect_size"},"b":{"const":0.2}}}}}, // h ≥ SESOI
 {"verdict":"NULL","when":{"metric":"/analysis/tost_equivalence_pass"}},
 {"verdict":"INCONCLUSIVE","when":{"const":true}}
]
```

12. **Scale plan.** Rung set declared at freeze: {R1, R2}; extension predicate (machine form,
    per the field-12 rung-set discipline): R3 runs iff `primary_reject@R1 AND
    primary_reject@R2` — R3 may only strengthen a satisfied R1–R2 conjunction, never
    substitute. 2–3 rungs; HC1 itself licenses at most a sign; the
    slope belongs to **HC5** (F7 slice): per-rung relative error-reduction Δ_r feeds §2's
    M-lin fit over R1–R4. Envelope row quoted: *"≤3B, direction-only; bias stated: hosts' raw
    error rates fall with scale (Kaplan/Hoffmann), so absolute catch counts shrink; the
    relative catch on kernel-covered slices is the quantity extrapolated"* (P1 §4b HC1).
    Anchor: test-time-compute row + Law 2 row (§2.4). *(Illustrative HC5 readout: Δ =
    {0.31, 0.27, 0.24, 0.22} at x = {8.13, 8.56, 9.23, 9.48}; M-lin slope −0.066/decade, 90%
    CI [−0.083, −0.049] ⇒ "shrinking"; PI at 7B (x = 9.85): 0.19 [0.15, 0.23] — above the 10%
    floor ⇒ HC5 not toy-only: shrinking but material; persistence claim licensed to 7B only,
    anchor_class DIRECTIONALLY-CONSISTENT with Law 2's predicted decay.)*
13. **Script.** `poc/e9/analyze_hc1.py`, fixture tests with hand-computed h/CI/TOST on a
    20-item mock; float64, no pre-rounding.

### 3.2 Efficiency — HE1 (verifier-offload; experiment F2), feeding HE7 (F7 slope)

**SAP instantiation:**

1. **Estimand.** gap_closed(R1,R2) = (acc₄ − acc₁)/(acc₂ − acc₁) on the kernel-covered slice
   (arm indices per the frozen F2 record; acc = mean per-item accuracy, n = 500 items), at
   the best pre-registered retry budget k ∈ {1,2,4} (selection metric: accuracy at min
   expected FLOPs — inside the bootstrap, per §1.7). Companion estimands, one per kill
   clause: text-null gap closure (arm 5), matched-compute gap closure (arm 7), cost ratio
   FLOPs(arm 4)/FLOPs(arm 2) per F0 §3.3 (verifier NN-cleanup on the ledger).
2. **Structure.** Unit = item, identical items across all 9 arms; inference-only (adapter
   pinned) ⇒ seed blocks trivial; cluster bootstrap ON.
3. **Primary test.** §1.1 row 1 on the arm-4-vs-arm-2 accuracy contrast under iso-accuracy
   discipline (P1 verbatim: "does 135M+verifier reach 360M?"): one-sided test that arm 4's
   accuracy is within/above arm 2's 95% CI *and* gap_closed ≥ 0.5, via paired bootstrap,
   α=0.05.
4. **Effect size.** gap_closed with BCa 95% CI; plus h for the arm4−arm1 lift; plus the full
   metric vector V per arm×rung (medians over inference seeds) — G-9 makes V mandatory.
5. **Secondaries (Holm):** HE2 dominance (F-budgets, Holm across budgets per P1); HC3
   kernel-vs-PRM contrast (h ≥ 0.2); HS12 latency comparison (estimation-only → F-explore).
6. **Multiplicity.** Rung-pair conjunction (R1,R2) and (R2,R3) under IUT; primary joins F-H0.
7. **TOST.** Kill clause (b) nulls ("text null closes as much gap") declared only via TOST at
   h = 0.2 on the arm5-vs-arm4 contrast; the ≤0.8×/cost-parity ratios use the log-ratio
   margin (§1.5).
8. **Power.** n = 500: power ≈ 0.998 at h = 0.2; MDE h ≈ 0.13. Gap-closure precision:
   *(illustrative)* if acc₂ − acc₁ ≈ 12 pp, SE(gap_closed) ≈ 0.07 at n = 500 ⇒ the 0.5
   threshold is decidable when true closure ≤0.35 or ≥0.65; between, expect INCONCLUSIVE —
   stated up front so an inconclusive readout cannot be spun as "nearly passed". TOST branch:
   n = 500 > 271 ⇒ powered.
9. **Resampling.** §1.7; retry-budget selection inside each bootstrap resample.
10. **Instrument gates.** Verifier false-accept rate on a clean control set (Wilson upper
    bound ≤2%); FLOP-meter cross-check within 2× of wall-clock-derived FLOPs (F0 §3.3) —
    breach ⇒ INSTRUMENT-INVALID.
11. **Statistic→verdict map** (P1 HE1 kill verbatim in `kill_criterion_verbatim`):

```jsonc
[
 {"verdict":"INSTRUMENT-INVALID","when":{"op":"not","a":{"metric":"/gates/instrument_valid"}}},
 {"verdict":"FAIL","when":{"op":"or",
    "a":{"op":"lt","a":{"metric":"/analysis/gap_closed_fraction_R1R2"},"b":{"const":0.5}},
    "b":{"op":"or",
       "a":{"op":"and",     // (b) text null or matched-compute closes as much at ≤ FLOPs
          "a":{"metric":"/analysis/text_null_parity_tost_pass"},
          "b":{"op":"lte","a":{"metric":"/analysis/text_null_cost_ratio"},"b":{"const":1.0}}},
       "b":{"op":"gte","a":{"metric":"/analysis/cost_ratio_vs_S"},"b":{"const":1.0}}}}}, // (c)
 {"verdict":"PASS","when":{"op":"and",
    "a":{"metric":"/analysis/primary_reject"},
    "b":{"op":"and",
       "a":{"metric":"/analysis/beats_text_null"},          // Holm-corrected secondary
       "b":{"op":"lt","a":{"metric":"/analysis/cost_ratio_vs_S"},"b":{"const":1.0}}}}},
 {"verdict":"NULL","when":{"metric":"/analysis/tost_equivalence_pass"}},
 {"verdict":"INCONCLUSIVE","when":{"const":true}}
]
```

12. **Scale plan → HE7 extrapolation (the full §2 pipeline, illustrative numbers).**
    Per-rung effect for the F7 fit: Δ_r = fractional cost saved at iso-accuracy. Suppose
    *(illustrative)* Δ = 0.42±0.05 (R1, x=8.13), 0.35±0.05 (R2, x=8.56), 0.30±0.06 (R3,
    x=9.23), 0.28±0.07 (R4, x=9.48). Fit M-lin (WLS): slope ≈ −0.10/decade, 90% CI
    [−0.16, −0.05] ⇒ CI excludes 0 from below ⇒ **"shrinking"**; M-pow γ ≈ −0.13 [−0.21,
    −0.06], AICc prefers M-lin (ΔAICc < 2 ⇒ simpler retained); both forms agree on sign at
    the target ⇒ no downgrade. Target = 7B (x* = 9.85, 0.37 decades past R4 — inside the
    1-OOM cap): Δ̂(7B) ≈ 0.24, parametric PI [0.11, 0.37] (df = 2, t = 2.92), bootstrap
    envelope [0.15, 0.33] ⇒ wider (parametric) governs. PI lower bound 0.11 > 0.10 floor ⇒
    **HE7 verdict: shrinking-but-material — NOT toy-only** (the HE7 kill needs shrinking AND
    extrapolation below 10%; only the first holds). Anchor: test-time-compute row —
    DIRECTIONALLY-CONSISTENT (substitution persists; magnitude decays as Law 2 predicts).
    Licensed claim, verbatim template: *"Verifier-offload saved 42%→28% of iso-accuracy cost
    from 135M to 3B (slope −0.10/decade, 90% CI [−0.16, −0.05]); the fitted trend predicts
    24% [11%, 37%] at 7B; direction-only beyond 7B; no published scaling law covers
    kernel-type verifiers — the test-time-compute literature (arXiv:2408.03314,
    arXiv:2502.06703) anchors mechanism persistence with trained PRMs, and the verdict is
    indexed to the tested PRM class."* Every clause of that sentence is a named field the
    P2 `--paper` scanner can check.
13. **Script.** `poc/f2/analyze.py` (already the pinned-path in P2's example record) +
    `poc/f7/fit_slopes.py`; fixtures include a hand-computed 4-point WLS case.

---

## 4. Integration, build items, and open decisions

**Integration (binding hand-offs).**
- P2 `analysis_plan_ref` points at this file + the experiment's SAP anchor; freeze pins the
  sha256. A change to §1/§2 after any experiment freezes is a design amendment for that
  experiment (P2 G-3) — pre-unblinding only.
- The `family-h0` cross-experiment record (C-3) is created per P2 §5.4 (its analysis script
  consumes member `analysis-output.json` files by pinned sha256; Holm over the 8 fixed
  members' primary p-values, non-read-out members scored as non-rejections (RT-13); output
  feeds the P3-encoded H0 decision tree).
- §1.8's field vocabulary is the normative namespace for every `verdict_rules` pointer;
  `registry-check` validates pointers against it at freeze (P2 §1.2 constraint 2).
- §2's outputs (`slope`, `slope_ci_*`, `pi_at_target_*`, `anchor_class`) plus
  `scale_language_licensed` (P2 G-12) are what the paper/explainer scanners read; §2.5 is the
  content of the `--paper` extrapolation gate.

**Build items (R0, ~$0, feed P3/P4):** (1) `tools/stats/` shared library — stratified
permutation, cluster BCa bootstrap, Wilson bounds (one- and two-sided), TOST, Holm/BH, WLS +
PI + parametric bootstrap, AICc — stdlib+numpy, byte-deterministic, fixture-tested against
hand-computed values; (2) per-experiment SAP blocks instantiated from §1.9 for Tier-0/1
experiments (F2 first — its freeze is the backbone's acceptance test per P2 §5.7); (3) the
`family-h0` record.

**Open decisions for the maintainer (@jeswr).**
1. **Sign off C-3 (the F-H0 Holm family).** It tightens P1's H0 gate: a single mechanism's
   PASS must survive Holm across the 8 mechanism primaries (fixed at freeze; non-read-out
   members scored as non-rejections, RT-13) before the *programme-level* "kernel principle
   is useful" claim is made. Alternative (rejected here, but yours to overrule): treat
   mechanism verdicts as independent and accept the ~34% family-wise risk with disclosure.
2. **Sign off C-4 (≥4/5 seed sign-consistency as a PASS requirement for trained conditions).**
   It can demote a statistically significant but one-seed-driven result to INCONCLUSIVE.
3. **Confirm n upgrades where power demands them:** HC1 at 600 items/rung; G2 at its
   **registered n = 500 gold subsumption judgments** (§1.6, P7 RT-4 — no longer conditional;
   ~12 annotator-hours per P3 g2.gold / P6 H-4); and the E8-R ≥85-stable-pair floor before
   D-SAE spend (§1.6) — all annotator/agent time, not GPU spend.
4. **Confirm the 1-OOM extrapolation cap and the ≥70B prohibition** (§2.3, §2.5) as the
   programme-wide rule for every external document, including the eventual paper.
