# P3-D-POWER — the coverage × max-gain paper-kill rig (G1 Δ_max)

> **Status: Phase-1 [DESIGN] deliverable of Programme-3 (bead
> `kernel-of-truth-s55r.12`, P3-D-POWER), REVISION 2 — revised against the
> independent GPT-5.6 review `poc/gpt56-review/rev-dPOWER-20260711/
> last-message.json` (read in full; every blocking finding and substantive gap
> is answered in-line and mapped in §10). Nothing here is frozen, scheduled,
> or run as an experiment; no verdict, audit, or KB shard is written. The
> stipulations this revision rests on ARE registered:
> `registry/assumptions.jsonl` ASM-0860…ASM-0865 (fresh block).**
> Author: Fable, chief-architect role (`kern/fable-designer`), 2026-07-11.
> Parent: `docs/next/programme-3-neurosymbolic-architecture.md` (revision 2)
> §4 (G1 gate), §3.1 (H-VL G1 kill), §7.1 (K-P3v2(1)). Blocked-by (per the WBS
> §5 table): **P3-LR-EVAL** (done — `docs/next/lit/EVAL.md`) + the coverage
> censuses. Feeds: the G1 verdicts for H-VL / H-RULE / store-side H-DD, and
> every P3-E-* prereg's power section.
>
> **What the review changed (headline):** the previously advertised "live
> define-lane kill" (`0.0038 < 0.03`) is **WITHDRAWN as invalid** — it summed
> only censused benchmarks (silent zero for the rest of the index), imputed
> `a_cov = chance` instead of the distribution-free 0, and summed per-term
> Wilson bounds that were not a simultaneous 95% bound. The corrected rig
> reproduces the review's diagnosis mechanically: on the same inputs it now
> reports `Δ_max` simUCB95 ≈ 0.81 (full headroom for everything uncensused)
> and refuses to emit any G1 verdict (§6). This bead is downgraded from
> "complete/runnable G1 deliverable" to: corrected design + corrected rig,
> G1-runnable only once the frozen index pin, oracle census, covered
> baselines, and eligibility registrations land.
>
> **Inputs read at source:** `docs/next/programme-3-neurosymbolic-architecture.md`
> rev-2 (§1.1 index, §1.4 W1/δ_k, §3.1 the adopted formula, §4 gate ladder,
> §7.1 K-P3v2); `docs/next/lit/EVAL.md` §5.3 (normalized-scale correction) +
> §2/§6 (floors, ceilings, weights-are-normative, accuracy-only transform);
> `docs/next/feasibility-synthesis.md` §0/§4 (the measured coverage wall);
> `registry/assessments/b-cov-define-lane.json` + `poc/b-cov-define-lane/
> census-summary.json` (MEASURED κ inputs, 0/1,550); `registry/verdicts/g8.json`
> (0/1,000 Mathlib); `registry/assessments/f2b-replicate.json` (covered-slice
> baselines); `docs/next/arch/round1-critique-synthesis.md` §A.3/§B.3;
> `poc/gpt56-review/rev-dPOWER-20260711/last-message.json` (the review).
>
> **Tag convention:** `[MEASURED: ref]` restates a programme verdict/census
> inside its envelope; `[LIT-BACKED: source]` an EVAL-verified external fact;
> `[STIPULATED: ASM-id]` a design choice registered in
> `registry/assumptions.jsonl`; `[EXTRAPOLATION]` a forward projection, never
> a premise.

---

## 0. What this bead is, in one paragraph

Before any GPU is spent on any store-dependent family (H-VL, H-RULE, store-side
H-DD, H-PS, the firewall P2), compute on paper the **largest index gain that
PERFECT oracle use of the store could possibly produce** at a rung, and compare
it to the pre-registered win margin δ_k. If even that best-case, oracle-friendly,
NL-wall-free ceiling cannot reach δ_k, the index-mover claim is **dead** and is
killed with **zero GPU** — because no mechanism result, however good, can exceed
a bound that already assumes the mechanism is perfect. This is the cheapest
decisive test in Programme-3 (`round1 §B.3` names it step 0), and it is the
direct instrument of the programme-level kill condition K-P3v2(1)
[MEASURED: programme doc §7.1]. The review confirmed the idea is sound and the
NL-boundary handling correct in principle (oracle access only makes the ceiling
generous; survival licenses nothing; no W1 claim crosses the oracle boundary) —
and found the previous implementation could issue **false kills**. This revision
fixes the false-kill paths and withdraws the previously claimed live kill.

The rig is `poc/p3-power/power.py` (corrected in this revision, §6). It is
Tier-0, CPU-only, deterministic, stdlib-only. It is **not** currently able to
fire a real G1 kill, by design: a verdict-eligible run requires inputs that do
not yet exist (§2, §4).

- DECISION: this bound is an **`oracle-diagnostic`** in the ASM-0814 sense — it
  assumes gold parse, gold retrieval, gold record-addressing, and perfect
  correction, all of which sit ABOVE the measured NL wall. It therefore licenses
  **no W1 claim and no positive claim of any kind**; its only outputs are KILL
  or SURVIVE-to-sizing, and only from a verdict-eligible run (§4). A family that
  *survives* the ceiling has proven nothing — it has merely failed to be killed
  for free [STIPULATED: ASM-0864].

---

## 1. The bound, corrected to the normalized index scale

### 1.1 The raw-scale identity (the starting point, and why it is not the answer)

The programme doc §3.1 adopted the referee's formula verbatim:

```
Δ_max  ≤  Σ_b  w_b · κ_b · (1 − a_b^cov)
```

where, per benchmark b: `w_b` = the benchmark's index weight, `κ_b` = the
store-covered fraction of its items, `a_b^cov` = the baseline's accuracy on the
covered items, and `κ_b(1 − a_b^cov)` = the raw-benchmark-accuracy rise if EVERY
covered item were corrected perfectly (covered items go to accuracy 1; uncovered
untouched). This is the whole-query **corrector** ceiling.

- LOAD-BEARING CORRECTION [LIT-BACKED: EVAL.md §5.3]: the raw form is
  **invalid under KOT-AI-INDEX/2**, because the index is not a raw accuracy
  average — it is a **chance/ceiling-normalized macro-average**
  (`s̃ = (s − chance)/(ceiling − chance)`, averaged within then across domains;
  programme doc §1.1). A raw-accuracy gain enters divided by that benchmark's
  normalization span and re-weighted by the domain macro-average. P3-D-POWER
  must restate the bound on the normalized scale before quoting any number.

### 1.2 The corrected corrector bound (Form A — for itemwise-accuracy components ONLY)

Because `s̃` is linear in raw accuracy, a raw gain `Δa_b` on benchmark b becomes a
normalized gain `Δa_b / (ceiling_b − chance_b)`, and enters the scalar index with
the **effective weight** `W_b` it carries after domain macro-averaging. So, over
**every component of the index** (never only the censused ones — §3.1):

```
                       ⎧ W_b · min( cap_b , κ_b·(1 − a_b^cov) / span_b )   if b is a censused,
                       ⎪                                                    Form-A-eligible accuracy component
Δ_max^A  =  Σ_b        ⎨
                       ⎪ W_b · cap_b                                        otherwise (uncensused, or metric
                       ⎩                                                    without a registered gain functional)

span_b = ceiling_b − chance_b;   cap_b = benchmark headroom (1 if the index clamps s̃,
                                          else (1 − chance_b)/span_b)
W_b    = domain_weight(d(b)) · within_domain_weight(b)      [Σ within a domain = 1]
```

`W_b` makes the index a weighted macro-average over domains of a weighted
macro-average within each domain (default within-domain weight = 1/|domain|; the
weights are a **registered NORMATIVE choice** — EVAL.md §2, §8.2 — pinned by
P3-D-INDEX, never by this bead) [STIPULATED: ASM-0860].

- **Metric-type contract** (review: "Form A is not universal across
  KOT-AI-INDEX/2"): the itemwise perfect-correction functional
  `κ(1 − a_cov)` is registered for **itemwise-accuracy metrics only** — the
  chance/ceiling transform itself is defined only for accuracy-type metrics
  [LIT-BACKED: EVAL.md §6, "the formula above is defined for ACCURACY-type
  metrics only"]. Every index component whose metric is loss, logprob,
  generation-scored, calibration, or anything else receives **full headroom
  `W_b · cap_b`** until a per-metric maximum-gain functional (with its
  registered score range) is added to the contract; it is never forced through
  the accuracy formula and never silently dropped [STIPULATED: ASM-0861].

### 1.2a The family-eligibility contract (which mechanisms Form A may be applied to)

The review is right that the bound is valid **only** for a mechanism that is
(i) **non-interfering off coverage** — behaviour on uncovered items is
identical to baseline — and (ii) **covered-support** — its entire incremental
benefit requires a covered, correctable item. That is plausible for fail-closed
verify/retry (H-VL) and executor-derived masking with fail-closed fallback
(H-RULE-CD), but **not established** for KV injection, adapters,
program-synthesis *training* (H-PS train-time variants), or H-DD weight
surgery, which can change uncovered behaviour or transfer knowledge globally.

- DECISION: Form A may be applied to a family only with a **registered
  eligibility argument** — a written causal-support/noninterference case
  (fail-closed architecture, or an intervention showing off-coverage deltas
  bounded at 0 within the harness's resolution), cited in the census input's
  `family_eligibility.noninterference_ref`. Families without one get **no free
  kill from this rig** (their G1 ceiling is vacuous, not violated): KV-injection,
  adapter, train-time-H-PS and H-DD-surgery variants each need either their own
  registered argument or a different ceiling design. The rig refuses to emit a
  verdict without the reference (§4) [STIPULATED: ASM-0861].

### 1.3 The firewall bound (Form B — for monotone wrong→abstain mechanisms)

A pure **claim-firewall** (P2; programme portfolio) cannot ADD correct answers —
it can only convert covered wrong answers to abstentions / improve calibration
[MEASURED: round1 §A.3]. On a pure-accuracy cell where abstention scores exactly
as a wrong answer, its gain is **zero**. Its ceiling is therefore not Form A but

```
Δ_max^B  =  Σ_b  W_b^abstain · (share of baseline ERRORS on b that are covered contradictions) · g_abstain
```

where `g_abstain` is the per-correct-abstention credit fixed by the P3-D-INDEX
**abstention-scoring rule** — an **open** P3-D-INDEX item (EVAL.md §8 Q1; round1
§B.2.3). Consequence, registered:

- DECISION: Form B is **uncomputable until P3-D-INDEX registers the
  abstention-scoring transform**; therefore any firewall-family G1 is BLOCKED on
  that decision, and the P3-D-INDEX freeze must register abstention scoring
  BEFORE any selective-mechanism G1 or G4 prereg freezes. On an accuracy-only
  index Form B ≡ 0 and the firewall's index-mover claim is dead by construction.
  The rig implements this as a fail-closed refusal (`ERR_FORM_B_UNREGISTERED`),
  not as a silent Form-A fallback [STIPULATED: ASM-0863].

### 1.4 The headroom cap (a tightening, now always applied)

Perfect correction cannot push a benchmark's raw score above 1, so its
normalized gain is capped at `cap_b = (1 − chance_b)/span_b` (or 1 exactly, if
the frozen index clamps `s̃` to [0,1] — the pin carries a `clamp_normalized`
flag). The corrected rig applies the cap to every term, including the
full-headroom imputations, so an imputed component contributes `W_b · cap_b`,
never an unbounded `1/span_b` artifact. Where a covered slice is already
high-accuracy the cap tightens the kill; it never loosens it
[STIPULATED: ASM-0860].

---

## 2. The exact inputs (provenance, and what is MEASURED vs pending)

| Symbol | Meaning | Source of truth | Status today |
|---|---|---|---|
| `κ_b` | covered fraction of benchmark b's items | the **oracle-coverage census** (§2.1, protocol below), keyed to the full census pin (§2.2) | define-lane 7 benchmarks MEASURED (mapper-parse lane, all 0) [MEASURED: b-cov-define-lane]; g8 Mathlib 0/1,000 [MEASURED: g8.json]; **frozen R-1 suite κ pending** b-cov-smol + G-CODE-0 + the oracle-census protocol (§2.1 — human annotation, NOT ~$0) |
| `a_b^cov` | baseline accuracy on covered items, as **integer correct/total counts** | own-harness model-alone on the census-covered subset, from **P3-E-CAL** (proposed bead P3-X-COVBASE) | f2b covered-slice baselines exist for d-qa-r (R1-alone 0.4920) [MEASURED: f2b-replicate]; per-suite covered-subset baselines pending |
| `W_b` | effective scalar weight of b | **P3-D-INDEX** freeze: domain weights × within-domain weights (NORMATIVE) | pending P3-D-INDEX; PROVISIONAL pin in §6 exercises the rig only |
| `chance_b`, `ceiling_b`, `metric_type_b`, clamping rule | normalization constants + metric class per component | **P3-D-INDEX**: chance = EVAL-verified MC floors; ceiling = pinned reference anchor + estimand + uncertainty + clamping rule; metric_type mandatory per component (§1.2) | MC chance floors verified [LIT-BACKED: EVAL.md §6]; ceilings pending P3-D-INDEX (only BLiMP has a verified human anchor, 0.886/0.964 — two estimands) |
| `δ_k` | the pre-registered win margin at rung k | **P3-D-INDEX / the §2.5 analysis plan** | pending; PROVISIONAL δ_1 = 0.03 exercises the rig only |
| below-floor exclusion set | which benchmarks are dropped as non-discriminative | **registered from P3-E-CAL BEFORE campaign results are seen** | pending P3-E-CAL |
| eligibility refs | per-family noninterference arguments (§1.2a) | registered design notes, cited in the census input | none yet — required before any verdict |

### 2.1 The κ input: the oracle-coverage census, its protocol, and its honest cost

`Δ_max` assumes perfect parse and best endorsement, so the κ it consumes must be
the **oracle-parse, best-endorsement checkability** — the fraction of items whose
gold answer the engine COULD decide if parsed perfectly and if the needed records
were endorsed — NOT the mapper-parse κ (which folds in the NL-wall parse gap that
Δ_max deliberately sits above). The three census lanes stack:

```
mapper-parse κ_B^engine   ≤   ORACLE (gold-parse, best-endorsement) κ   ≤   lemma-touch upper sieve
      (leg-3 parse gap)         (this bead's input)                        (loosest; cheap and mechanical)
```

[MEASURED: b-cov-define-lane keeps these lanes separate; internal define-op-census
gold-side 0.7710 vs external mapper-parse 0.0000]. Today only the mapper-parse
lane is measured externally (all 0); the gold-parse external lane is `N/A — no
hand-authored grammar queries` [MEASURED: census-summary.json].

The review is accepted on cost honesty: **the exact oracle census is NOT a ~$0
CPU pass.** Existing third-party data has no gold-parse lane; producing gold
semantic parses and deciding derivability-under-best-endorsement requires human
annotation and can itself introduce false-negative labels. The protocol this
bead commissions (bead P3-X-ORACLE-CENSUS, §9) is therefore two-tier:

- DECISION: **(a) the lemma-touch upper sieve is the mechanical, genuinely cheap
  tier** — a CPU pass that marks an item covered if any kernel/world-layer lemma
  is touched by the item's surface content; it strictly over-counts, so a kill
  that fires under it is coverage-sound with no annotation. **(b) The exact
  oracle census is a human-annotation instrument** with a registered protocol:
  per-item record schema `{item_id, benchmark_rev, gold_parse_sketch,
  derivable_under_best_endorsement: yes|no|unknown, records_touched,
  annotator_id, adjudication_id}`; double annotation on a preregistered
  subsample with inter-annotator agreement reported and disagreements
  adjudicated; ambiguity policy **`unknown ⇒ covered`** (fail toward headroom,
  never toward a kill); and a registered residual label false-negative
  allowance `label_fn_ub` from the adjudicated subsample, consumed by §3.2.
  Until (b) lands, the rig may run on mapper-parse κ or the sieve, and any
  numerically-firing kill under mapper-parse κ is flagged **contingent on the
  oracle census**; only sieve/oracle-lane kills are unconditional
  [STIPULATED: ASM-0862].

### 2.2 The census pin (cross-rung reuse guard)

The mathematics is scale-independent across 100M–2B, but `a_cov`, prompts,
seeds, the eligible suite, δ_k, the store version, and the mechanism all vary by
rung — a free-text `rung` string is not a pin. A verdict-eligible census input
MUST carry the full pin block, and the rig fails closed to ILLUSTRATIVE-ONLY
without it:

```
pin: { model_checkpoint, harness_hash, prompt_policy, seeds,
       store_hash, kernel_hash, world_layer_hash, mapper_hash,
       grammar_version, benchmark_revisions }
plus: coverage_lane ∈ {mapper-parse | oracle | upper-sieve}   (enforced enum)
      census_mode  ∈ {exhaustive | sampled}                    (§3.2)
      family_eligibility: {form: A|B, noninterference_ref}     (§1.2a)
```

No cross-rung or cross-store reuse of a census or a Δ_max verdict is permitted
unless every pin field matches; a store/kernel hash change invalidates κ
[STIPULATED: ASM-0865].

---

## 3. The computation

### 3.1 Per-component over the WHOLE index, then aggregate (no silent zeros)

For **every** component b of the frozen index pin (review blocking finding 1 —
never only the censused ones): if b is censused, Form-A-eligible, and
accuracy-metric, `contrib_b = W_b · min(cap_b, κ_b(1 − a_b^cov)/span_b)`;
otherwise `contrib_b = W_b · cap_b` (full headroom — an uncensused or
unsupported-metric component is assigned its maximal possible gain, effectively
`κ_UB = 1, a_cov_LB = 0`). A weighted domain with no enumerated components
contributes `domain_weight · 1` and marks the pin incomplete (a frozen pin must
enumerate every weighted domain, so this arm exists only to fail exploratory
runs safely). The scalar ceiling is `Δ_max = Σ_b contrib_b`; the **per-domain**
ceiling is the sum over that domain's components re-expressed on the domain's
own [0,1] axis, judged against a domain margin `δ_k^d`. Both are reported — the
programme is domain-vector-first (programme doc §1.1; EVAL.md §2 metabench
one-factor result) [LIT-BACKED: EVAL.md §2]. Consequence the review demanded and
the rig now exhibits: **a partial census can only make a kill harder, never
easier** — a whole-index kill is arithmetically impossible until the uncensused
weight is small [STIPULATED: ASM-0860].

### 3.2 Uncertainty propagation → a SIMULTANEOUS upper confidence bound (the kill quantity)

EVAL.md §5.3 mandates propagating uncertainty in κ and in covered-subset
accuracy. Because a kill must never fire falsely, the rig bounds Δ_max from
**above** with **family-wise, estimand-matched** intervals and kills only if
even that joint upper bound misses δ_k [STIPULATED: ASM-0860]:

- **Estimand match** (review: "the confidence model does not match the census
  estimand"). `census_mode = exhaustive`: every item of the frozen suite is
  classified, so the finite-suite κ is **exact conditional on the labels** — no
  Wilson term is taken; the residual uncertainty is oracle-label false
  negatives, bounded by the registered `label_fn_ub` (§2.1(b)):
  `κ_b^UB = min(1, κ_b + label_fn_ub)` (0.0 permitted only for a deterministic
  mechanical classifier, e.g. the mapper lane). `census_mode = sampled`: a
  registered sampling frame + stratification is mandatory, and κ gets a Wilson
  UPPER bound at the Bonferroni-adjusted level below. `N = 0` constrains
  nothing → full headroom.
- **`a_b^cov`:** consumed as **integer `correct_cov`/`n_cov` counts** (never a
  rounded rate); Wilson LOWER bound at the adjusted level (smaller a_cov ⇒
  bigger gain). If absent, the imputation is the **distribution-free lower
  bound `a_cov = 0`** — NOT chance: small models score below chance, and
  deliberately wrong predictions are perfectly correctable, so `chance`
  understates the ceiling and can false-kill (review blocking finding 2).
- **`span_b`:** a lower bound via the P3-D-INDEX-registered ceiling uncertainty
  (`ceiling_slack`), since a smaller span inflates the normalized gain.
- **Simultaneity** (review blocking finding 3): summing separate per-term 95%
  bounds does not give 95% joint coverage. The rig counts the m stochastic
  intervals it will take in the run (sampled-κ intervals + measured-a_cov
  intervals; exact-κ terms take none) and computes each **one-sided at
  α/m = 0.05/m** (Bonferroni). By the union bound the event "every parameter is
  inside its bound" has probability ≥ 0.95, and since Δ_max is monotone in each
  bounded parameter, `simUCB95(Δ_max) = Σ_b contrib_b^UB` is a valid
  simultaneous 95% upper bound. A survivor near the margin gets the tighter
  exact-joint / preregistered paired-bootstrap treatment in the sizing bead
  (§5), never a looser one here.

### 3.3 Why the direction is sound (no false kills) — and what it now requires

A false kill = declaring dead a claim that was actually reachable. The soundness
argument "every approximation pushes Δ_max up" is only true once §3.1–§3.2 hold:
the previous revision violated it three ways (silent-zero components, chance
imputation, non-simultaneous intervals — exactly the review's blocking
findings). With completeness (nothing contributes silent zero), zero-imputation
for missing baselines, headroom for unsupported metrics/families, and the
Bonferroni-joint bound, `simUCB95(Δ_max) < δ_k` implies the true best case is
`< δ_k` with family-wise confidence ≥ 95%. Using the most generous defensible κ
(oracle census with `unknown ⇒ covered`, or the lemma-touch sieve) keeps the
posture: the only cost of generosity is *forgoing* a free kill, never making a
wrong one [STIPULATED: ASM-0860].

### 3.4 The required-κ inversion (the "margin table")

Inverting the bound answers the coverage-growth question — *what κ would a family
need for δ_k to be reachable at all?*

- **Single carrying benchmark** (claim rests on b alone):
  `κ_b* = δ_k · span_b / (W_b · (1 − a_b^cov))`, with the imputed `a_cov = 0`
  when unmeasured (which makes κ_b* smaller, i.e. conservative against
  paper-killing a route). If `κ_b* > 1`, benchmark b **can never carry the
  claim even at 100% coverage** — a permanent paper-kill of that route. The rig
  emits the per-benchmark `κ_b*` column in its table (review: previously
  promised, not emitted — fixed).
- **Uniform coverage** across the censused accuracy components:
  `κ* = δ_k / Σ_b W_b (1 − a_b^cov)/span_b`. This κ* is the coverage target the
  coverage-growth/ingestion feeder line (`coverage-growth-ingestion-plan.md`,
  booked to KOT-LIFE/1) must hit for the family to clear G1 — the concrete
  output K-P3v2(1) consumes at the R-1 checkpoint [MEASURED: programme doc §7.1].

### 3.5 Resource accounting (KOT-FAIR/2): κ* is not actionable naked

Coverage is store-version- and budget-dependent, so a G1 run pins the
canonically packed store/kernel artifacts (§2.2 hashes; the rig echoes them into
its output) and the programme distinguishes three ceilings
[STIPULATED: ASM-0865]:

1. **Δ_max under the current admissible `B_k` store** — what §3.1 computes from
   the measured census of the pinned store;
2. **Δ_max under a preregistered maximum store-growth envelope** — the same
   computation re-run with the envelope's projected κ (an input scenario, never
   a measurement; always labelled as such);
3. **the cost of reaching κ*** — bytes, authoring/review/indexing human-hours,
   and `B_k` admissibility under KOT-LIFE/1, attached by the ingestion plan.

A naked "κ* = 0.13" is not a coverage target; the rig's output says so verbatim
and the ingestion bead must attach (3) before κ* is cited in any prereg.

---

## 4. The decision rule (verbatim) and what it licenses

- DECISION [STIPULATED: ASM-0864 — the P3-D-POWER decision rule, verbatim]:

  > For family F at rung k, on the frozen KOT-AI-INDEX/2-vN suite with its
  > registered weights `{W_b}`, normalization constants + metric types +
  > clamping rule, below-floor exclusion set (all registered from P3-E-CAL
  > BEFORE campaign results are seen), and margin `δ_k`:
  >
  > 0. **Verdict eligibility** (all required, else the run is ILLUSTRATIVE-ONLY
  >    and no verdict of any kind is emitted): frozen index pin
  >    (`frozen: true`); complete census pin block (§2.2); declared
  >    `coverage_lane` and `census_mode` (with `label_fn_ub` or sampling frame
  >    as §3.2 requires); a registered Form-A family-eligibility reference
  >    (§1.2a) or, for Form B, a registered abstention-scoring transform (§1.3).
  > 1. Read `κ_b` from the oracle-coverage census (§2.1); read integer
  >    `correct_cov/n_cov` from P3-E-CAL/P3-X-COVBASE; select Form A or Form B
  >    per F's registered mechanism class.
  > 2. Compute `simUCB95(Δ_max^F)` per §3.1–§3.2 over the WHOLE index (scalar
  >    and per-domain), full headroom for every uncensused or unsupported
  >    component.
  > 3. **KILL the index-mover claim for F at rung k iff
  >    `simUCB95(Δ_max^F) < δ_k`** (and, for a domain-scoped claim, iff
  >    `simUCB95(Δ_max^{F,d}) < δ_k^d` for every domain d the store touches,
  >    with that domain fully censused).
  > 4. A kill fired under mapper-parse κ is CONTINGENT and requires the oracle
  >    census (or the upper sieve) to confirm; a kill fired under oracle or
  >    upper-sieve κ is UNCONDITIONAL.
  > 5. A kill licenses **only** "no mechanism can move the index-mover claim
  >    for F at rung k by δ_k on this suite" — it is `oracle-diagnostic`, makes
  >    no W1 claim, and does not touch F's value as a scoped instrument (F may
  >    still be handed back as a covered-slice tool with its envelope).
  >    SURVIVAL licenses **nothing** except "proceed to G2 and to the §5
  >    sizing".

- **Relation to K-P3v2(1) (programme kill):** if, after this analysis at the R-1
  checkpoint (including any funded coverage-growth wave), `simUCB95(Δ_max) < δ_1`
  for **EVERY** store-dependent family on the frozen R-1 suite, the
  coverage-ceiling programme kill fires — perfect use of the store cannot reach
  the margin for any family [MEASURED: programme doc §7.1(1)]. P3-D-POWER is the
  computation that adjudicates it. Note the completeness rule cuts both ways
  honestly: K-P3v2(1) cannot fire off a partial census either.

---

## 5. The second computation — statistical power / sample sizing (survivors only)

**Status honesty (review: "the sizing deliverable is not implemented"):** this
section is a DESIGN SKETCH and requirements list. `power.py` contains **no**
sizing calculation; the implementation is the separate proposed bead
**P3-D-POWER-SIZE** (§9), and no G4 prereg may cite a sample size until that rig
exists and is calibrated. The previous revision's "the rig computes item×seed
power" language is withdrawn.

For a family that survives the ceiling, the achievable gain is some `Δ ≤ Δ_max`;
the G4 experiment must be sized so the pre-registered test can detect it.

- DECISION [STIPULATED: ASM-0864]: the G4 primary is
  `LCB95(INDEX(S) − INDEX(C)) > δ_k` with FWER control across the F(B_k)
  comparator set and a hierarchical bootstrap over items/prompts/seeds
  preserving paired predictions (programme doc §2.5). The sizing rig must
  consume, per benchmark: (a) the census-measured covered-item counts; (b) a
  planning effect `Δ_plan` (a preregistered fraction of `Δ_max`, never `Δ_max`
  itself); (c) **paired outcome variance and S/C correlation** on pilot or
  calibration runs — counts plus Δ are insufficient; (d) prompt-variance and
  seed-variance components; (e) the comparator multiplicity |F(B_k)| entering
  the FWER correction; (f) the exact bootstrap hierarchy (resample
  within-benchmark items and seeds; the registered suite is NOT resampled as a
  sample from a benchmark universe — EVAL.md §2). The single f2b calibration
  point (~0.92 one-sided power at n=250×3 seeds for Δ≈0.10 on one covered
  slice [MEASURED: benchmark-evaluation-strategy §1.4]) is an anchor for ONE
  metric on ONE domain and cannot supply (c)–(d) across metrics and domains;
  P3-E-CAL pilots must.
- Two EVAL.md §5.3 constraints bind the sizing: (a) near-floor MC benchmarks
  give an unstable `a_b^cov` → the below-floor exclusion set is applied first,
  registered from P3-E-CAL, never post hoc; (b) proxy-rung validity is
  per-metric-family (continuous/logprob metrics extrapolate across rungs, MC
  accuracy does not — EVAL.md §5) → the sizing must flag any covered slice
  whose metric does not support the rung's cross-rung inference
  [LIT-BACKED: EVAL.md §5].

---

## 6. The corrected rig + the demonstration runs (ILLUSTRATIVE-ONLY, no verdict)

### 6.1 Artifact

`poc/p3-power/power.py` — Tier-0, CPU-only, stdlib-only, deterministic (no RNG,
no clock). Inputs are two JSON files, both schema-validated fail-closed
(ERR_PIN_SCHEMA / ERR_CENSUS_SCHEMA on any missing field, range violation,
weight-sum violation, unknown benchmark, or float `a_cov`):

- an **index pin** `{frozen, clamp_normalized, delta_k, delta_k_domain,
  domains:{d:{weight}}, benchmarks:{b:{domain, metric_type, chance, ceiling,
  [within_domain_weight], [ceiling_slack]}}}` — the P3-D-INDEX freeze (the
  committed `inputs/index-pin.PROVISIONAL.json` has `frozen: false`, so no run
  on it can ever emit a verdict);
- a **census** `{family, rung, coverage_lane, census_mode, [label_fn_ub],
  [sampling_frame], [pin{…§2.2}], [family_eligibility], coverage:{b:{n_total,
  covered_count, [correct_cov, n_cov]}}}`.

Output: the per-benchmark contribution table **including the `κ_b*` column and
full-headroom imputation flags**, scalar + per-domain `Δ_max` (point and
simultaneous UCB95 with the Bonferroni m and z reported), the `κ*` inversion
(labelled "target only after KOT-LIFE/1 costing"), the store-pin echo, and the
verdict line — which is `ILLUSTRATIVE-ONLY` unless step 0 of §4 passes.
`--form B` fails closed (`ERR_FORM_B_UNREGISTERED`).

```
python3 poc/p3-power/power.py \
    --index  poc/p3-power/inputs/index-pin.PROVISIONAL.json \
    --census poc/p3-power/inputs/census-define-lane.MEASURED.json
```

### 6.2 Run on the MEASURED define-lane census — the previous "live kill" is withdrawn

The previous revision claimed a live G1 kill here (`UCB95 = 0.0038 < 0.03`).
**That claim is withdrawn as invalid** (review blocking findings 1–3: only the
7 censused benchmarks were summed, `a_cov = chance` was imputed, and the bound
was not simultaneous). The corrected rig on the same inputs:

```
FAMILY H-VL / store-side define-op (define-lane census) | RUNG R-1 | lane mapper-parse (exhaustive) | delta_k = 0.0300
simultaneous UCB: one-sided alpha=0.05, Bonferroni over m=0 interval(s) (finite-suite exact given labels)
benchmark                     dom     N  cov  kappa^   kUB  a_cov  contrib contribUB kappa*_b  status
OpenBookQA-test               D3    500    0  0.0000 0.000  0.000  0.00000   0.00000    0.682  censused
MMLU-college_biology-test     D3    144    0  0.0000 0.000  0.000  0.00000   0.00000    0.682  censused
MMLU-college_chemistry-test   D3    100    0  0.0000 0.000  0.000  0.00000   0.00000    0.682  censused
MMLU-medical_genetics-test    D3    100    0  0.0000 0.000  0.000  0.00000   0.00000    0.682  censused
MMLU-anatomy-test             D3    135    0  0.0000 0.000  0.000  0.00000   0.00000    0.682  censused
MMLU-clinical_knowledge-test  D3    265    0  0.0000 0.000  0.000  0.00000   0.00000    0.682  censused
MMLU-nutrition-test           D3    306    0  0.0000 0.000  0.000  0.00000   0.00000    0.682  censused
CLUTRR                        D4      0  n/a     n/a 1.000    n/a  0.13194   0.13194      n/a  FULL-HEADROOM (not censused)
ProofWriter                   D4      0  n/a     n/a 1.000    n/a  0.12755   0.12755      n/a  FULL-HEADROOM (not censused)
(no benchmarks enumerated)    D1                                   0.15000   0.15000      n/a  FULL-HEADROOM (empty weighted domain)
(no benchmarks enumerated)    D2                                   0.15000   0.15000      n/a  FULL-HEADROOM (empty weighted domain)
(no benchmarks enumerated)    D5                                   0.15000   0.15000      n/a  FULL-HEADROOM (empty weighted domain)
(no benchmarks enumerated)    D6                                   0.10000   0.10000      n/a  FULL-HEADROOM (empty weighted domain)
Delta_max (scalar, point)      = 0.8095
Delta_max (scalar, simUCB95)   = 0.8095   [kill uses this]
Delta_max (D3, own axis)       = point 0.0000 / simUCB95 0.0000  vs delta_k^d = 0.0500
Delta_max (D4, own axis)       = point 1.0380 / simUCB95 1.0380  vs delta_k^d = 0.0500   [domain NOT fully censused]
kappa* required (uniform)      = 0.0975   reachable(<=1)? True   [target only after KOT-LIFE/1 costing]
>>> VERDICT: ILLUSTRATIVE-ONLY — no G1 verdict (run not verdict-eligible)
```

Reading, honestly: with completeness enforced, the scalar `Δ_max` simUCB95 is
**0.81, not 0.0038** — a 7-benchmark census of a 6-domain index cannot support a
whole-index kill, exactly as the review said. What the run does show is the
*shape* of a future valid kill: the censused D3 slice contributes exactly 0
(exhaustive mapper-lane census, exact given the deterministic classifier), so a
**domain-scoped D3 kill** would fire (`0.0000 < 0.05`) once (a) the index pin is
frozen, (b) the census carries its full pin block and a registered H-VL
eligibility reference, and (c) the oracle census (or the lemma-touch sieve)
confirms the mapper-lane zeros — until then even that is CONTINGENT and
unissued. The κ_b* column also already yields a route-level fact that survives
all pending inputs: no single D3 benchmark can carry δ_1 = 0.03 below κ_b ≈ 0.68
under the provisional weights — an ingestion-scale statement, not a verdict
[EXTRAPOLATION — provisional pin; replaced at P3-D-INDEX freeze].

### 6.3 Run on the labelled-hypothetical D4 census (branch exercise)

`inputs/census-D4-hypothetical.STIPULATED.json` (a relational family, 45%/30%
oracle-lane coverage on CLUTRR/ProofWriter, placeholder integer baseline counts,
`label_fn_ub = 0.02`) yields `simUCB95(Δ_max) = 0.8658` (m = 2 intervals,
z = 1.96) — NO KILL, ILLUSTRATIVE-ONLY; per-domain D4 own-axis simUCB95 =
0.3402 vs δ^d = 0.05; uniform κ* ≈ 0.145; per-benchmark κ*: CLUTRR 0.327,
ProofWriter 0.261. This exercises the no-kill branch, the Bonferroni
adjustment, the exhaustive-census `label_fn_ub` path, and the κ_b* table, and
shows the rig does not trivially kill (or spare) anything: outcomes are driven
by the census, not by the rig.

---

## 7. Scope, limitations, and the discipline lines

- **No smuggled oracle.** Δ_max is explicitly the best-case oracle ceiling; it
  sits ABOVE the measured NL wall (§0). It is a diagnostic that can only KILL. A
  survival is not a win and is never reported as one — the `oracle-diagnostic`
  label rides every output [STIPULATED: ASM-0814].
- **The kill is per (family × suite × rung × store-pin).** It does not
  generalize across suites, rungs, or store versions (§2.2); a family killed on
  the R-1 suite may be re-examined at R-2 only through a fresh prereg with a
  fresh census.
- **Normalized-scale-only, accuracy-functional-only.** No number is quoted on
  the raw-accuracy scale (EVAL.md §5.3), and no non-accuracy metric is forced
  through the accuracy functional (§1.2) — unsupported metrics ride at full
  headroom until their functionals are registered.
- **Family eligibility is not assumed.** Form A applies only with a registered
  noninterference/covered-support argument (§1.2a); global-effect mechanisms
  (KV injection, adapters, train-time H-PS, H-DD surgery) get no free kill and
  no free pass from this rig.
- **κ is the binding uncertainty, and the oracle census is not free.** The
  measured censuses are exploratory and biomedical-skewed (define-lane) or
  wild-formal (g8); the frozen-R-1-suite κ needs b-cov-smol + G-CODE-0 + the
  §2.1 protocol, whose exact-oracle tier is a human-annotation instrument with
  a real budget (the sieve tier is the cheap one).
- **Below-floor exclusion is registered before results.** Components are dropped
  from the index (and thus from Δ_max) only via a criterion fixed on P3-E-CAL
  calibration data before campaign results are seen — never post hoc
  [LIT-BACKED: EVAL.md §5.3].
- **Weights are normative, pinned upstream.** This bead computes; it does not
  choose `W_b`, `δ_k`, ceilings, metric types, or the exclusion set — those are
  the P3-D-INDEX freeze. The rig fails closed if the index pin is absent or
  incomplete (it has no defaults for them).

---

## 8. Registered `registry/assumptions.jsonl` entries (this revision)

Registered in the fresh block ASM-0860…ASM-0865 (append-only; per the revision
governance for this bead — the review-mandated corrections are load-bearing
stipulations and must not float untracked):

| ASM | Claim (short) |
|---|---|
| ASM-0860 | The corrected G1 bound + kill-soundness contract: whole-index summation with full-headroom imputation (no silent zeros), headroom caps, a_cov-missing ⇒ 0, span lower-bounding, and the Bonferroni-simultaneous one-sided UCB as the kill quantity. Supersedes-in-part the raw-scale statement inside ASM-0817 and the previous in-doc §8(1)/(2) proposals. |
| ASM-0861 | The metric-type and family-eligibility contract: Form A registered for itemwise-accuracy only; unsupported metrics ride at full headroom; Form A applies to a family only with a registered noninterference/covered-support reference. |
| ASM-0862 | The oracle-coverage census protocol: two tiers (mechanical lemma-touch upper sieve; human-annotated exact oracle census with schema, double annotation, adjudication, `unknown ⇒ covered`, registered `label_fn_ub`); mapper-parse-lane kills are contingent; the exact tier is NOT ~$0. |
| ASM-0863 | The abstention-scoring dependency edge: Form B uncomputable until P3-D-INDEX registers the transform; rig fails closed; accuracy-only index ⇒ Form B ≡ 0. |
| ASM-0864 | The G1 decision rule verbatim (§4), including verdict-eligibility step 0, the contingent/unconditional lanes, oracle-diagnostic licensing, and the G4 primary-endpoint frame the sizing bead must implement. |
| ASM-0865 | The census/rung pin schema (§2.2) and KOT-FAIR/2 resource accounting (§3.5): no cross-rung/store reuse without a full pin match; κ* not actionable without KOT-LIFE/1 costing; the three-ceiling reporting split. |

---

## 9. New beads to propose to the coordinator (bd-create)

*None created here (governance).* Proposed:

| Proposed bead | Type | Pri | Blocked by | Deliverable |
|---|---|---|---|---|
| **P3-X-SIEVE-CENSUS** — frozen-suite lemma-touch upper sieve | [EXP/Tier-0] | P0 | frozen R-1 suite list (P3-D-INDEX draft) | mechanical over-counting coverage sieve per frozen-suite benchmark; CPU-only, genuinely cheap; sound basis for unconditional kills (§2.1(a)) |
| **P3-X-ORACLE-CENSUS** — frozen-suite exact oracle census | [EXP] | P0 | P3-X-SIEVE-CENSUS (protocol pilot) | gold-parse + best-endorsement κ_b per §2.1(b) protocol (schema, double annotation, adjudication, `label_fn_ub`); HUMAN-ANNOTATION BUDGETED, not ~$0 |
| **P3-X-COVBASE** — covered-subset baseline counts | [EXP] | P0 | P3-E-CAL | integer `correct_cov/n_cov` = own-harness model-alone on each census-covered subset |
| **P3-D-ELIG** — family noninterference arguments | [DESIGN] | P1 | none | the §1.2a registered eligibility references (H-VL fail-closed, H-RULE-CD masking; explicit non-eligibility or alternative ceilings for KV/adapter/train-time/H-DD-surgery variants) |
| **P3-D-POWER-SIZE** — the §5 sizing rig | [DESIGN] | P1 | P3-D-POWER + P3-D-INDEX (analysis plan) + P3-E-CAL pilots | paired-hierarchical-bootstrap sample-size/power calculator consuming §5(a)–(f) |

(The existing P3-D-FIREWALL bead — round1 §B.4 — already carries the Form B /
abstention-scoring dependency; ASM-0863 is its registered edge.)

---

## 10. Review-point → change map (rev-dPOWER-20260711)

| Review point | Where answered |
|---|---|
| Blocking 1: uncensused components silently zero | §3.1 whole-index summation + full-headroom imputation; `power.py` iterates the index pin, imputes `W_b·cap_b`, flags every imputation; empty weighted domains impute and mark the pin incomplete |
| Blocking 2: `a_cov = chance` imputation understates ceiling | §3.2: distribution-free `a_cov = 0`; rig rejects float `a_cov`, takes integer counts |
| Blocking 3: UCB95 not simultaneous | §3.2: Bonferroni α/m one-sided per interval, union-bound argument stated; rig reports m and z |
| Kill `0.0038 < 0.03` invalid | §6.2: withdrawn verbatim; corrected run shows 0.8095 ILLUSTRATIVE-ONLY |
| Form A not universal across metrics | §1.2 metric-type contract; unsupported metrics full headroom; pin requires `metric_type` |
| Family scope too broad | §1.2a registered eligibility references; verdict-eligibility step 0; P3-D-ELIG bead |
| Oracle census not a concrete ~$0 pass | §2.1 two-tier protocol (sieve vs annotated oracle), schema/adjudication/IAA/`unknown ⇒ covered`/`label_fn_ub`; cost honesty in §7 and §9 |
| Confidence model ≠ census estimand | §3.2 estimand match: exhaustive ⇒ exact-given-labels + `label_fn_ub`; sampled ⇒ registered frame + Bonferroni-Wilson |
| 100M–2B pinning incomplete | §2.2 full census pin block, enforced enums, no cross-rung/store reuse; rig echoes store pins |
| Sizing not implemented | §5 relabelled DESIGN SKETCH; "the rig computes" withdrawn; requirements (a)–(f) enumerated; P3-D-POWER-SIZE bead |
| Doc/code mismatches (κ_b* table, Form B, validation, rounded a_cov) | rig emits κ_b*; `--form B` fails closed; full schema/range/weight/completeness validation; integer counts only |
| KOT-FAIR/2 resource accounting | §3.5 three ceilings + store-pin echo + "κ* not actionable naked" in rig output |
| "Do not drive downstream family beads yet" | §9 proposes census/eligibility/sizing beads only; no family experiment beads driven |

---

## Epistemic register

- **STIPULATED (registered):** the corrected whole-index Form A bound, caps,
  zero-imputation, simultaneous UCB [ASM-0860]; metric-type + family-eligibility
  contract [ASM-0861]; the two-tier oracle-census protocol [ASM-0862]; the
  Form B abstention dependency [ASM-0863]; the decision rule + G4 endpoint frame
  [ASM-0864]; the census pin schema + resource accounting [ASM-0865];
  oracle-diagnostic status inherits [ASM-0814].
- **LIT-BACKED (EVAL.md, source-verified 2026-07-11):** the normalized-scale
  correction and uncertainty-propagation requirement (§5.3); MC chance floors
  and the accuracy-only definition of the chance/ceiling transform (§6);
  weights-are-normative and the metabench one-factor scalar caution (§2);
  proxy-rung per-metric validity (§5).
- **MEASURED (within envelope):** define-lane κ = 0/1,550 [b-cov-define-lane +
  census-summary.json]; g8 0/1,000 [g8.json]; f2b covered-slice baselines
  [f2b-replicate]; the internal 0.7710 vs external 0.0000 gold-vs-mapper
  gradient.
- **EXTRAPOLATION (never premises):** that the frozen-suite oracle κ will remain
  low enough for a domain-scoped kill (that is exactly what the census beads
  measure); the κ_b* ≈ 0.68 route statement under the provisional pin (§6.2);
  the hypothetical D4 numbers (§6.3, labelled STIPULATED-hypothetical inputs).
- **PROVISIONAL (demo-only, replaced by P3-D-INDEX):** every weight, ceiling,
  metric anchor, and δ_k in `index-pin.PROVISIONAL.json` (`frozen: false` —
  structurally incapable of producing a verdict).

This document changes no frozen object, no verdict, and no audit; it registers
ASM-0860…0825 (append-only) and proposes §9's beads.
