# KOT-FAIR/2 Rev1 — Fable independent adversarial critique (Part-B revision stage)

> **STATUS: CRITIQUE ONLY — nothing edited, committed, registered, frozen, or run.** 2026-07-20,
> Programme-3 Phase-1, Fable adversarial-critique lane (bead-prescribed stage: Part-B revision →
> re-review + Fable critique → Part C / #57 → freeze). Target:
> [kot-fair-2-spec-p3mf0.md](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md) Revision 1 (2026-07-20), read against
> [kot-fair-2-review1-freeze-readiness.md](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-review1-freeze-readiness.md) (Part A + the 12-item Part B) and the
> companion [p3d-threat-factorial-controls.md](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/p3d-threat-factorial-controls.md) (P3-D-THREAT Rev1), which edit 10 adopts by
> reference. The Rev1 spec is treated as third-party work. Proposed items are labelled
> `PROPOSED-CRIT-*`; no `ASM-<number>` ids are minted.
>
> **Tags:** `[MEASURED: ref]` = a fact I verified by direct read of the named file/section;
> `[LIT-BACKED: ref]` = claim resting on a Phase-0 lit-review's content; `[STIPULATED]` = my proposed
> fix/design choice, for the coordinator to accept or reject; `[EXTRAPOLATION]` = my forward
> prediction beyond anything measured.

## Verdict

**NEEDS-REV2-THEN-REREVIEW.**

The 12 Part-B edits are directionally right and none should be reverted. But three of them are not
yet sound as written — one is internally contradictory (the two-stage statistics now runs two
incompatible resampling schemes), one is unexecutable (the per-rung floor census has no executing
instrument), and one introduces a new gaming channel the review did not have (repeatability-gate
comparator attrition). Several Part-A items the revision flagged OPEN are in fact load-bearing
dependencies of Part-B edits, not separable deferrals. All of this is repairable by a targeted Rev2
of bounded scope; nothing requires material redesign. Freeze remains blocked regardless by Part C /
#57 / THREAT ratification / the empirical ratifications — that is not in dispute here.

---

## Findings

### CRITICAL

---

#### C-1. The Rev1 statistics are internally contradictory: §6.2 retains the review-condemned benchmark-family resampling while §5.4(5) imports THREAT's corrected scheme into the same gatekeeping procedure

**Claim.** [MEASURED: spec §6.2] The Rev1 analysis plan still says: "At each replicate, resample
benchmark families within domain, then items within benchmark." [MEASURED: review, Statistics] The
same review this revision responds to says exactly this "can change the estimand and is unreliable
when a domain has only one or two families" and prescribes: keep benchmark/domain weights fixed,
resample item clusters *within* each benchmark (paradigm, rule template, story, source document,
paraphrase family). [MEASURED: THREAT §5.1] THREAT Rev1 adopted the corrected scheme verbatim.
[MEASURED: spec §5.4(5), §6.2] Edit 10 wires the attribution family into "THREAT Rev1 §5.1's frozen
two-stage gatekeeping procedure" whose stage 1 is "the W1 frontier + per-domain non-inferiority
family (§0, §6.2)".

**Why it's wrong.** One two-stage procedure now has stage 1 (W1 + per-domain NI, per §6.2)
resampling benchmark families within domains, and stage 2 (attribution, per THREAT §5.1) holding
benchmark weights fixed and resampling item clusters. These are different estimands under one FWER
umbrella; the "ratified-THREAT-prevails" rule then arguably rewrites §6.2 silently. Worse, the
defect is concentrated where it bites hardest: D6 (IFEval) has ONE benchmark and D5 has two
[MEASURED: spec §1.1], so family-resampling within those domains is degenerate or near-degenerate —
and Part-B edits 1 and 11 wired NEW binding inferences (the per-domain NI bounds, the sealed DiD
LCB) into exactly this resampling ("under the §6.2 resampling", §5.2). The revision's defence would
be that the resampling correction was Part A, not Part B; but edits 1, 10 and 11 each *consume*
§6.2, so the defect is no longer separable from the Part-B edits. A Rev1 that builds three new
binding gates on a resampling scheme its own source review calls unreliable is not ready for
re-review as-is.

**Fix** `[STIPULATED]` (`PROPOSED-CRIT-1`): replace §6.2 bullet 4 with the review/THREAT scheme —
fixed benchmark and domain weights; resample preregistered item clusters within each benchmark
(cluster taxonomy pinned per benchmark in the manifest: BLiMP paradigm, CLUTRR story/depth cell,
ProofWriter depth, PR-KOT rule/composition family, etc.); paired system outputs preserved; state
explicitly that §6.2 and THREAT §5.1 use the identical scheme. Also import the review's other two
directly-consequential statistics corrections that edits 1/6 now depend on: training seed as a
top-level random effect where the claim concerns a procedure, and day/session/run hierarchy for
resource UCBs.

---

#### C-2. Edit 3's per-rung LCB floor census has no executing instrument: P3-E-CAL performs a census only at R1

**Claim.** [MEASURED: spec §1.1, §1.4] The rung-membership rule says final per-rung membership "is
fixed by that census on each rung's anchor BEFORE any architecture output exists", with anchors R1 =
135M, R2 = 360M, R3 = 1.7B, R0 "pinned at P3-D-INDEX". [MEASURED: spec §7.2 step 3] But the only
census the calibration protocol actually runs is: "On `CAL-FLOOR`, apply the §1.4 floor and
saturation rules … Freeze `INDEX_COMMON` as the surviving **R1** component set." No step runs the
floor rules on the 360M or 1.7B anchors' `CAL-FLOOR` splits; no R0 anchor exists at all; §7.3's
GREEN criteria reference only `INDEX_COMMON`.

**Why it's wrong.** FOLIO's and GSM8K's R2+ placement, MMLU-Pro/BBH's R3+ placement, and the
promised return path ("R1 only on a passing LCB floor census") all resolve through a census that no
section of the framework performs above R1. The revision log lists "per-rung calibration census
scope" as an OPEN Part-A item "not silently resolved here" — but edit 3 as applied *depends* on it.
An OPEN item that a Part-B edit references normatively is a dependency, not a deferral: as written,
R2/R3 scalar membership at freeze would be fixed by assertion (the "pre-calibration hypothesis"
column), which is precisely what the review's edit 3 was meant to eliminate. So the rung manifest
does NOT yet "follow from a stated criterion rather than assertion" for any rung except R1.

Secondary defects inside the same edit:
- **Census power is a hidden membership knob.** The LCB direction is now correct (uncertainty →
  exclusion, the conservative side), but that means an *under-powered* census excludes a genuinely
  discriminating component. No census N, CI method (binomial? bootstrap?), or minimum-power
  requirement is stated for `CAL-FLOOR` per component. An operator who prefers a component out of
  the scalar benefits from a small census. [EXTRAPOLATION] With 20% `CAL-FLOOR` splits of small
  benchmarks (OpenBookQA test = 500 rows → ~100 census items; FOLIO 204 → ~41), `LCB95(score −
  chance) > 0.02` is genuinely at risk of failing on width alone for real above-chance components.
- **Anchor-construct bias.** The census runs on pure-neural SmolLM2 anchors only. Components where a
  tiny pure-neural model floors — deep ProofWriter, FOLIO, GSM8K below R2 — are exactly the
  add-capability territory where a governed engine-bearing system would differ most. A
  pure-neural-anchored census therefore systematically evicts the discriminating-for-S components
  from lower-rung scalars. This is defensible (the scalar should discriminate among *comparators*
  too) but it is a construct decision, currently unstated, and it interacts badly with C-4/M-4
  below.

**Fix** `[STIPULATED]` (`PROPOSED-CRIT-2`): (a) extend §7.2 with per-rung census steps — apply §1.4
on each rung's anchor over that rung's candidate component set, and make §7.3 GREEN conditional on a
frozen membership list per rung, not only `INDEX_COMMON`; (b) pin the R0 anchor before the census
can be claimed to exist for R0; (c) preregister the census CI method and a per-component minimum
census N (or a power target at effect size f), so census sizing cannot modulate membership; (d)
state explicitly that the census construct is "discriminates among pure-neural anchors", and record
the anchor-construct bias as a standing limitation in §"Residual gameability".

---

#### C-3. The every-arm repeatability gate (edit 6) creates a comparator-attrition channel: the noisiest — often strongest — comparators can exit F(B_k) by failing bands the literature says are too tight

**Claim.** [MEASURED: spec §3.5] "An arm or comparator whose measurement fails its bands is
remeasured under the frozen discard/repeat rule or becomes inadmissible; a comparator lost this way
is reported as such, never silently dropped from \(F(B_k)\)." [MEASURED: review Part A / KOT-COST]
The same review notes the SYS lit allows up to 10% within-day energy variation while the draft
applies 5% CoV to energy — and Rev1 left the §3.5 band table unchanged. [MEASURED: spec §5.3 item 6]
The frontier must include "adaptive retrieval and task-appropriate adaptive test-time compute,
including verifier-guided candidates".

**Why it's wrong.** "Reported as such" is fail-open, not fail-closed: a comparator that cannot pass
its bands leaves the roster (with a note), and S then no longer has to beat it. That is a
comparator-dodging channel created by the edit itself — the review's own threat table ("Comparator
dodging") is violated by the repair for its survivorship finding. And it is not a corner case:
adaptive test-time-compute and retry-heavy comparators are *intrinsically* high-variance in latency,
CPU-seconds and energy per query; [EXTRAPOLATION] a ±5% CoV band on energy/latency is plausibly
unpassable for a verifier-guided TTC arm as a matter of construction, not measurement failure — so
the gate preferentially removes exactly the comparator family most likely to threaten S. The
un-ratified band values are therefore not "legitimately deferred": with the every-arm gate attached,
the band constants are now load-bearing for frontier composition, and one of them (energy 5%) is
already contradicted by the framework's own cited literature [LIT-BACKED: reports/lit-p3-sys.md §Q4
via review Part A].

**Fix** `[STIPULATED]` (`PROPOSED-CRIT-3`): (a) make comparator loss fail-closed — if a
preregistered member of \(F(B_k)\) cannot pass repeatability after the frozen repeat rule, W1 at
that rung is BLOCKED (instrument failure), not evaluated against a shrunken frontier; at minimum
this must hold for the strongest-by-dev comparator and every per-domain frontier comparator
\(C^d\); (b) split the bands by arm class — deterministic-decode arms vs adaptive/TTC arms — with
class-specific bands ratified from P3-E-CAL *plus* the synthetic high-variance rig probes the review
already requested (Part A, Calibration); (c) align the energy band with the SYS-reported 10%
within-day figure or justify the tighter value empirically at ratification.

---

### MAJOR

---

#### M-1. The `UNPROVEN` movement-signature rule is not mechanically executable, contradicting the mechanical-grader requirement

[MEASURED: spec §3.1a] "The grader checks the co-reported CPU-seconds, storage/network bytes and
latency vector for such a movement signature; a signature without a covering measurement blocks any
energy-superiority wording." [MEASURED: spec §6.2] "Mechanical grader consumes only frozen per-item
rows and emits PASS/FAIL/INSTRUMENT-INVALID." No definition of "signature" exists: no thresholds, no
direction/magnitude rule, no preregistered detector. A grader cannot mechanically apply an
undefined heuristic, so either the `UNPROVEN` state is discretionary (post-hoc, gameable in both
directions) or it never fires. **Fix** (`PROPOSED-CRIT-4`) `[STIPULATED]`: preregister the signature
as an executable predicate, e.g. component-energy advantage claimed AND any unmeasured-domain proxy
(storage+network bytes/query, non-RAPL-covered CPU-seconds where applicable, p95 latency) exceeds
the comparator's by more than a ratified factor → `UNPROVEN`; put the predicate and its constants in
the ratification register.

#### M-2. Under energy path (b), the budget-FIT claim itself still leaks: unmeasured-domain offloading is blocked only from "energy-superiority wording", and the only quantitative closure (R1k I/O ceilings) has a free headroom parameter

[MEASURED: spec §3.1a] Path (b) binds CPU-package+DRAM and GPU-board energy separately with
`system_energy_status = UNMEASURED`; the `UNPROVEN` rule blocks *wording*. But W1's energy component
is a budget-fit condition (§0), and "S fits \(B_k\)" is itself an efficiency claim surface: an S
that moves work into disk/NIC/host-I/O fits the amended component budget *more easily* while its
true system energy is unbounded by anything except the R1k storage/network-bytes ceilings — whose
"per-metric deployment-rationale headroom" is an unbounded free text parameter (see M-3). So the
three states genuinely prevent mislabelled energy *superiority*, but they do not yet prevent an
uncovered-domain migration from making the *admissibility* half of the claim easier. **Fix**
(`PROPOSED-CRIT-5`) `[STIPULATED]`: under path (b), make the M-1 movement predicate additionally
gate ADMISSIBILITY wording ("fits \(B_k\)" must be co-stated as "component-energy budget only;
system energy unmeasured"), and require the I/O-byte and CPU-second ceilings of R1k to be binding
(branch 1) or in the Pareto budget (branch 2) — not merely co-reported — whenever path (b) is the
ratified energy path. (The "total energy" naming prohibition itself I could not break: §3.1, §3.2,
§7.3 and the boundary record are consistent; but see m-2 for the KOT-LIFE joules leak.)

#### M-3. The replacement absolute ceilings (R1k) smuggle endogeneity back through "deployment-rationale headroom": pre-S-*measurement* is not pre-S-*knowledge*

[MEASURED: spec §3.1] Branch 1 ceilings are "derived from the calibration anchors' measured values
plus a per-metric deployment-rationale headroom stated in the prereg — never derived from S".
Timing is exogenous (anchors are measured at P3-E-CAL before S is measured), but the *operator
choosing the headroom already knows S's architecture* — H-PS is a committed design
[MEASURED: p3d-threat-factorial-controls.md §2], and everyone knows it is CPU/engine/I-O-heavy
relative to a pure-neural anchor. Nothing bounds the headroom, so the operator can set "anchor ×
20" on CPU-seconds with a paragraph of deployment prose and reproduce the 3×-rule's laundering
allowance with a different derivation. The review's objection to 3× was partly "no construct, power,
or systems basis" — an unconstrained rationale sentence has exactly the same defect. Branch 2 is
cleaner in form but its coordinate values are entirely unspecified. **Fix** (`PROPOSED-CRIT-6`)
`[STIPULATED]`: require the headroom to be *derived*, not asserted — pinned to a named external
deployment envelope (e.g. an interactive-serving SLO class or a published serving-cost reference)
with the derivation shown; cap headroom at a ratified maximum multiple per metric; and require the
ratifier to adversarially confirm the ceilings would NOT admit an arm that the withdrawn 3× rule
would have rejected on the anchors' measured profile. Alternatively prefer branch 2 with
anchor-derived coordinates and the same derivation discipline.

#### M-4. Edit 1's NI family can silently shrink exactly where it matters: "every scalar-eligible domain in the frozen core-domain set" lets a floored-out core domain exit the non-inferiority gate

[MEASURED: spec §0] The NI condition ranges over "every scalar-eligible domain \(d\) in the rung's
frozen core-domain set". Scalar eligibility is dynamic (census + variance + saturation, §1.4); the
core set is static (ratification item 4). If a core domain loses all scalar-eligible components at
a rung — most likely the reasoning domains where the pure-neural anchor floors (C-2's bias) — the
per-domain NI constraint for that domain evaporates rather than blocking anything, quietly
re-opening the buy-a-gain-with-regressions channel in the domains least visible to the scalar.
Meanwhile §1.5 still says "at least three capability domains" with no reference to the core set —
the review's "'any three domains' is too weak" Part-A finding is listed OPEN, yet edit 1's wording
presupposes its resolution. **Fix** (`PROPOSED-CRIT-7`) `[STIPULATED]`: add the rule — if any
member of the frozen core-domain set is not scalar-eligible at rung \(R_k\), either (a) W1 is not
available at that rung, or (b) the NI condition for that domain runs on a preregistered vector
column (e.g. the domain's unclipped \(\tilde{s}\) mean) instead of silently dropping; and reconcile
§1.5(1) with the core-domain set (scalar requires the core set scalar-eligible, not "any three").

#### M-5. The construct-map freeze (OPEN Part-A) is now a load-bearing dependency of edit 1, not a separable deferral

[MEASURED: review Part A / INDEX] "Domain assignment, benchmark duplication, and family grouping
are weight-setting operations… Freeze a construct map and benchmark-family clustering." Rev1 left
this OPEN — legitimately, for the scalar. But edit 1 promoted *domain boundaries* into a binding
gate family: which per-domain NI constraints exist, and what \(C^d\) is strongest at, are both
functions of how benchmarks are grouped into domains. An operator can now shape the NI family
itself (merge a weak construct into a strong domain to dilute a regression; split a favourable one
to add an easy NI row) — strictly more gameable than before edit 1. **Fix** (`PROPOSED-CRIT-8`)
`[STIPULATED]`: pull the construct-map/domain-assignment freeze forward into the same ratification
package as the core-domain set (register item 4), with the review's grouping-sensitivity report
attached; state in §0 that the NI family is defined over the frozen construct map.

#### M-6. \(C^d\) is under-defined: selection statistic, challenger interaction, and re-pin rule are all missing

[MEASURED: spec §0, §5.3] \(C^d\) = "the strongest admissible comparator on domain \(d\)…, pinned
at roster closure". Unstated: strongest by which measurement (dev full-suite domain score,
presumably — but dev vs test, point estimate vs bound, is not written); what happens when the
five blinded challengers run *after* closure and one is strongest on a domain (the rebuild rule
triggers only on a 0.01 scalar regret — a challenger can be the true domain frontier without
triggering a rebuild, leaving \(C^d\) pinned to a weaker comparator); and whether \(C^d\) is
re-pinned on a frontier rebuild. The definition is not circular (it never references S), which is
right; it is merely incomplete, and each gap is a lenient-by-default hole in the NI gate. **Fix**
(`PROPOSED-CRIT-9`) `[STIPULATED]`: define \(C^d\) = argmax over admissible roster members of the
frozen dev domain score (point estimate, dev split pinned by hash); on any frontier rebuild or
challenger admission, \(C^d\) is recomputed before prereg-freeze; record the dev-selection caveat
(winner's-curse on the selection, unbiased at test) in the analysis plan.

#### M-7. Edit 10's "ratified-THREAT-prevails" rule has no freeze-time content-hash pin, so a frozen framework would defer to a mutable external document — and restatement drift has already begun

The by-reference structure is the right call — duplicating THREAT's matrix verbatim would fork it,
and §5.4 restates enough (the seven §2.2 families, \(J_{core}\), the locus law, the two-stage
statistics, the six dimensions) to be reviewable stand-alone. I verified the restatement against
THREAT Rev1: \(J_{core}=\{D,P,I,T^*,R^*\}\), the §3.0 locus list, `X*` conditionality, `T1/T2/T3`
split, family units, feedback factor, and §5.1 gatekeeping are all faithfully carried
[MEASURED: spec §5.4 vs THREAT §§3.0–3.9, §4.1, §5.1]. Two defects remain:

1. **No pin.** "Any divergence between this section and a ratified THREAT is resolved in THREAT's
   favour and triggers a framework revision here" [MEASURED: spec §5.4]. For a *frozen* prereg this
   is a prereg-integrity hole: the prevailing object must be a fixed document, or a post-freeze
   THREAT edit retroactively rewrites the frozen framework's control semantics without a version
   change. Nothing in §5.4, the ratification register (item 20), or the freeze conditions requires
   pinning the ratified THREAT's content hash into the P3-D-INDEX manifest.
2. **Drift instance already present.** §5.4(1)(d) scopes `G-*` to "graph arms"; THREAT §3.4 scopes
   it to every "graph, relational-structure, rule-composition, or topology **claim**" (and
   explicitly exempts terminal single-op H-PS claims) [MEASURED: THREAT §3.4]. Arm-conditioned vs
   claim-conditioned triggering is a real difference (a non-graph arm making a rule-composition
   claim needs `G-*` under THREAT but not under a literal reading of §5.4). Harmless today only
   because THREAT prevails — which is exactly why the pin in (1) matters.

**Fix** (`PROPOSED-CRIT-10`) `[STIPULATED]`: add to §5.4 and the freeze conditions — at
prereg-freeze, the ratified THREAT revision is content-hashed into the P3-D-INDEX manifest; the
prevails-rule applies to that hash only; any later THREAT change requires a framework version bump
and re-review. Correct §5.4(1)(d) to THREAT's claim-conditioned wording now (cheap, removes the one
known divergence).

#### M-8. The edit-11 decontamination gate is not mechanically decidable: pass thresholds are point rules while rule 9 demands CI-carrying gates

[MEASURED: spec §5.1] Rule 9 requires recall/FPR "reported with confidence bounds…, never as bare
points, and the gate wording must carry that bound"; the pass paragraph then says "Pass requires,
on the HELD-OUT set: 100% verbatim recall, ≥99% near-verbatim recall, ≥90% paraphrase recall and
≤2% false-positive rate, each published with its confidence bound." Published-with-bound but
*decided-on-point* is exactly the "bare point" defect with a CI stapled on; and the two readings
diverge materially: with 100 held-out paraphrases, observed 90/100 gives a Clopper–Pearson LCB
≈ 0.824, while requiring LCB95 ≥ 0.90 needs ≈ 96/100 observed. A grader cannot decide the gate as
written; a gamer picks the lenient reading. (Same ambiguity for "≤2% FPR" — point vs UCB — on 1,000
negatives.) **Fix** (`PROPOSED-CRIT-11`) `[STIPULATED]`: state the operative statistic per
criterion: verbatim recall observed = 100% AND its exact LCB reported; near-verbatim/paraphrase
recall gates bind on the one-sided LCB95 against ratified targets sized so the planned n can
actually pass (or the n is raised); FPR binds on the one-sided UCB95 ≤ the ratified bound.

#### M-9. The sealed DiD non-inferiority condition is the right form but its estimand is under-pinned

[MEASURED: spec §5.2, §6.2] `LCB95(Δ_sealed − Δ_public) > −0.03`, one-sided, CI-based — correct
direction and correct conversion of the old point rule. Unpinned: (a) "the advantages against the
strongest comparator" — strongest by what and when? If chosen after public results, the DiD
comparator is endogenous (pick the comparator whose public gap was smallest); if it differs between
suites, Δ_sealed and Δ_public are against different C. (b) "under the §6.2 resampling" — the two Δs
live on disjoint item sets (public suite vs sealed release); §6.2's hierarchy is defined for the
public suite, and nothing states the joint resampling (independent bootstraps and a difference of
bounds? one joint replicate over both suites?). Monte-Carlo procedure changes the bound. **Fix**
(`PROPOSED-CRIT-12`) `[STIPULATED]`: pin C for the DiD to the pre-declared strongest-by-dev
comparator (same C in both Δs), and specify the joint procedure: per replicate, resample both
suites' cluster hierarchies simultaneously (shared system-level pairing), compute Δ_sealed − Δ_public,
take the one-sided percentile/max-t bound. Also carried into C-1's fix, since this bound currently
inherits the defective §6.2 scheme.

#### M-10. The floor span f = 0.02 is in raw-score units over heterogeneous (u − c) spans, violating the spec's own "own units" discipline

[MEASURED: spec §1.4] The gate is `LCB95(raw_score − chance) > f`, `f = 0.02` global — not per
rung, per benchmark, or normalized. With c = 0.5/u = 0.964 (BLiMP), 0.02 raw ≈ 0.043 normalized;
with c = 0.10 (MMLU-Pro), ≈ 0.022; with c = 1/23 (CLUTRR), ≈ 0.021. So the effective
discrimination bar varies ~2× across components for no stated reason — in a revision that
elsewhere insists (edit 6, §3.5) that "measurement resolution is assessed in each metric's OWN
units". Not backward (the direction fix is real and complete — I found no residual UCB floor logic
anywhere; the remaining UCB95 uses in §3.1/§5.3 are resource-admissibility bounds, which is the
correct conservative direction), but the constant's unit basis is unjustified and interacts with
the census-power gap (C-2). **Fix** (`PROPOSED-CRIT-13`) `[STIPULATED]`: define f in normalized
units (f applied to \(\tilde{s}\)-scale LCB), or ratify per-benchmark raw floors with the
normalization shown; either way say which CI (binomial vs bootstrap) the census uses.

---

### MINOR

---

- **m-1. `UNPROVEN` conflated into the status enum.** [MEASURED: spec, PROPOSED-ROW-MF0-R1d vs
  §3.1a JSON] The row advertises "`MEASURED-WALL`/`UNMEASURED`/`UNPROVEN` states", but the record
  enum is `{MEASURED-WALL, UNMEASURED}` and `UNPROVEN` is a claim label on a win. Fix: word the row
  as "two record states + the UNPROVEN claim label", and say where `UNPROVEN` is recorded
  (grader output row, per M-1's predicate).
- **m-2. KOT-LIFE joules have no boundary record.** [MEASURED: spec §4 amortisation grid] The
  `"joules"` fields in the amortisation grid carry no §3.1a boundary reference — the one remaining
  surface where a component sum could be quoted as lifecycle "energy" without the prohibition
  biting. Fix: every KOT-LIFE joules figure carries (or references) a §3.1a boundary record; a
  component-sum joules figure is component-named there too.
- **m-3. δ_NI sign/notation duplicated.** [MEASURED: spec §0 vs §6.2] §0 defines margin δ_NI = 0.02
  with condition > −δ_NI; §6.2 says "Non-inferiority default margin is `−0.02`". Same rule, two
  sign conventions — in a prereg-destined document, pick one (positive margin, one-sided condition
  stated once, cross-referenced).
- **m-4. Licensed-claim wording overstates the NI gate.** [MEASURED: spec §0] "…with no
  preregistered domain regression beyond δ_NI" reads as no-regression *vs every comparator*; the
  actual gate is vs \(C^d\) only. Fix: "…no domain more than δ_NI below its preregistered
  per-domain frontier comparator."
- **m-5. No downward census path for MMLU-Pro/BBH.** [MEASURED: spec §1.1] FOLIO/GSM8K get an
  explicit census-conditioned return path; "MMLU-Pro and BBH remain R3+" is flat assertion with no
  criterion by which a census could ever move them. Asymmetric rules invite asymmetric argument
  later; state that R3+ placement is also census-confirmable (or that demotion below R3 is
  categorically excluded and why).
- **m-6. Server-cell rate can exceed stability for slow arms; the binding p95's load shape is
  unpinned.** [MEASURED: spec §3.3] Arrival rate = `0.5 / anchor_warm_median_service_time`; an arm
  ~2× slower than the anchor approaches utilization 1 → unbounded queue → mass timeouts. Timeouts
  scored incorrect is right for goodput, but the spec never says (a) which load shape's p95 binds
  the W1 budget component, or (b) whether INDEX accuracy is computed from load-cell runs (where
  queueing would contaminate capability) or from a separate unloaded scoring run. Pin both.
- **m-7. The Offline batch-shopping game survives Rev1 untouched.** [MEASURED: spec §3.3; review
  Part A] "Batch 8 or the largest batch fitting all arms, whichever is smaller" still lets one arm
  force everyone to batch 1. Listed OPEN — fine — but note it sits *inside* §3.3, the section edit
  6 claims to have hardened; the re-review should not read edit 6's ADOPTED status as covering it.

**Tag audit (requested):** I found no place where the Rev1 spec puts `[MEASURED]` on a stipulation —
the revision adds no `[MEASURED]` tags at all [MEASURED: spec self-check 7, verified by scan], and
`[EXTRAPOLATION]` is unused rather than smuggled as a premise. THREAT Rev1's single `[MEASURED:
rules1c]` is a genuine measured precedent with a source. The nearest thing to tag abuse is
structural, not lexical: LIT-BACKED tags on edits 3 and 6 cover the *direction* of the rules while
the load-bearing *constants* underneath (f, bands, SLOs) are stipulations — acceptable, since the
constants are separately `[STIPULATED]`-tagged, but the ratifier should not read the LIT-BACKED
tag as covering the numbers.

## What Rev1 got right

- **The UCB→LCB inversion is fixed completely.** The backward rule appears only inside its own
  withdrawal rationale; every other UCB95 in the document is a resource-admissibility bound, which
  is the correct conservative direction [MEASURED: spec §1.4, §3.1, §5.3].
- **The dual W1 condition is coherent.** Scalar superiority vs each comparator + NI vs the
  per-domain max is strictly harder than either alone, arithmetically consistent at
  δ_NI = δ_k = 0.02, and not trivially unpassable; the defects are in \(C^d\)'s definition and the
  NI family's membership dynamics (M-4/M-6), not the rule's logic.
- **The energy boundary record and naming prohibition are genuinely airtight on the naming side**
  (§3.1, §3.2, §7.3 all consistent; §7.3 fails closed on a missing binding energy cell); the
  residual holes are executability (M-1) and the path-(b)/R1k interlock (M-2/M-3), not the state
  machine.
- **The 3× withdrawal rationale is correct and well-argued**, and folding it into the KOT-COST
  repair was disclosed, not silent.
- **Edit 10's by-reference structure with restated contract is the right architecture** — the
  restatement is faithful on every point I checked (one drift instance, M-7.2), and joint
  ratification is the right coupling; it needs only the content-hash pin.
- **Survivorship gaming is closed on the accounting side**: denominator-event timeouts,
  issued/completed/dropped/unfinished counts, frozen queue/timeout policy, drift-invalidated cells
  — the review's "1,000 completed queries permits survivorship gaming" finding is genuinely
  answered; the residual load-side issues are m-6/m-7 and C-3's attrition channel.
- **Proxy-rung asymmetry (§1.6) is wired in verbatim and correctly**, including byte-identical
  cross-rung pins enforced via manifest hashes.
- **The Sardana quarantine, KOT-LIFE subledgers with TCO(q,t), and the win-rate prohibition** are
  clean, faithful-to-source edits; I found nothing to press on edits 2, 7, or 12 beyond m-2.
- **Part C's deferral is handled with discipline**: a true placeholder, correctly named as a freeze
  blocker, consistent with THREAT §5.2's identical deferral.

## Recommended next step

A **targeted Rev2 before the re-review**, scoped to: C-1 (one resampling scheme, stated once),
C-2 (per-rung census steps in §7 + census power/CI pins), C-3 (fail-closed comparator attrition +
class-split bands), M-1/M-2 (executable UNPROVEN predicate + path-(b) admissibility co-statement),
M-3 (derived, capped headroom), M-4/M-5 (core-set/eligibility collision rule; construct-map freeze
pulled into register item 4), M-6 (complete \(C^d\) definition), M-7 (THREAT content-hash pin +
one wording fix), M-8 (decidable decon gate), M-9 (DiD estimand pin), M-10 (f units) — plus the
minor edits. All are specification-level; none reopens the design. Then the re-review runs on Rev2.
Freeze remains blocked regardless by Part C / #57, THREAT ratification, P3-E-CAL GREEN, and the
empirical ratifications (base-image digest, hardware probe, band/SLO constants) — this critique
changes none of those gates.

---

## MANDATORY self-check

1. **Genuinely adversarial, not deferential?** YES — 3 CRITICAL + 10 MAJOR + 7 MINOR findings
   against a revision whose 12 edits I also verified individually; two Part-B edits are found
   internally contradictory or unexecutable as applied, and one is found to introduce a new gaming
   channel; the OPEN-items separability claim in the revision log is directly rebutted (C-2, M-5).
2. **Every finding has a concrete fix?** YES — each CRITICAL/MAJOR finding carries a
   `PROPOSED-CRIT-*` fix (1–13); each MINOR carries an inline fix.
3. **No @handle/account strings?** YES — checked; none present.
4. **No `ASM-<number>` ids minted?** YES — only `PROPOSED-CRIT-1…13` labels.
5. **Nothing committed/registered/frozen?** YES — this critique file is the only file created;
   no git operations, no bead/registry changes, no runs, no schedules.
6. **Spec file NOT edited?** YES — kot-fair-2-spec-p3mf0.md, the review file, and the THREAT file
   were read only; this critique was written to a new file
   (docs/next/design/kot-fair-2-rev1-fable-critique.md).
