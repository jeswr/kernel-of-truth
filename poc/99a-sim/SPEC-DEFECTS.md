# SPEC-DEFECTS / build notes — 99a SIM-SPEC mock implementation

Per SIM-SPEC S9, a genuine ambiguity or contradiction in the spec is a
REPORTABLE DESIGN DEFECT, not a thing the executor resolves locally. This file
records (A) genuine spec ambiguities/contradictions found while implementing,
(B) disclosed environment/scope deviations for the MOCK build (not spec
defects — flagged so the coordinator can price them), and (C) deferred
acceptance obligations the mock does not discharge.

## A4 UPDATE (2026-07-21) — Rev9/R9a floored plug-in applied + re-validated

Fable landed Rev9/R9a in the design doc (## Revision 9 + amended S4.4/§4.6(1b)(C)
+ §4.6 S4.6): the null-boundary bootstrap and the futility moment-SE now consume
the FLOORED triple rho~ instead of the per-rep truncated-to-0 point estimates.

**Code change applied (gate_test.py):** point estimation (`estimate_rho_points`)
is UNCHANGED — concordance-class inversion, no-root->0, rho_c = max(0, rho_cr -
rho_r). New `floored_triple()` builds rho~ in the pinned order: (i) floor the two
small-cluster components rho~_s = max(rho_hat_s, 0.15), rho~_r = max(rho_hat_r,
0.15), rho~_c = rho_hat_c (no concept floor); (ii) clip each into [0, 0.98];
(iii) proportional rescale if the sum > 0.98. `gate_pvalue` bootstraps at rho~
(with `return_diag` exposing pihat, the bootstrap-null SD, the point estimate,
and rho~). `pins.RHO_FLOOR = 0.15`. The §4.6 futility moment-SE would consume the
same rho~ (widening-only) once Stage-1 futility is wired (still B3-deferred; the
shared `floored_triple` is ready for it).

**Re-validation result — see the "A4 RE-VALIDATION" block appended at the end of
this file** for the per-(cell, arm, gamma) pass/fail with CP bounds and the
mandatory dispersion diagnostics.

## A. Genuine spec ambiguities / candidate defects

**A1. (minor) Bounded-Beta gate threshold recalibration references a per-cell
stream but the marginal-mapping obligation is under-operationalised for the
draw budget vs the run cost.** S4.4 pins: for the bounded-Beta regime, recompute
the gate threshold t_a as "the exact numerical (1 - pi_a)-quantile of Z's
distribution, computed once per cell by 10^7 pinned Monte-Carlo draws on the
dedicated PER-CELL calibration stream SeedSequence([BASE_SEED, config_index,
999_999_999]) before any replication runs." This is codeable and unambiguous as
written; the note is only that 10^7 draws x (per-cell) x the bounded-Beta cells
is a non-trivial one-off cost the S6 wall-clock accounting does not itemise. Not
a contradiction — flagged for cost transparency, resolved as written in the
frozen run.

**A2. (clarification, not a blocker) S4.2 "operative path" wording vs the task
brief.** The coordinator brief describes S4.2 as providing "the BALANCED
CLOSED-FORM mixed-model fit ... as the operative path." S4.2 as written does NOT
give a closed-form formula; it pins REML + Giesbrecht-Burns Satterthwaite with
an R/lme4/lmerTest reference implementation as the executable oracle, and S9
allows "any NUMERICALLY EXACT algorithm ... SUBJECT to the fixture-equivalence
check" against lme4. For balanced crossed designs the ANOVA/method-of-moments
variance components equal REML in the interior, so a balanced closed form is a
LEGITIMATE such algorithm — but the spec does not itself write it, and exact
lme4 equivalence must still be demonstrated on the S4.2 fixture. Recorded so the
"closed form" is understood as an executor choice under S9, gated by the
(deferred) fixture check, not something S4.2 hands over.

**A4. (GENUINE FINDING — needs design review) The mandated S4.4 gate-
calibration battery FAILS at the component level in a faithful implementation:
the crossed-binary parametric-bootstrap gate test is ANTI-CONSERVATIVE at the
null boundary when the seed/reviewer dependence is small.** Measured at the
gate-cal cell (rho=0.1, n_nonce=96, pi_a=pi0=0.60, R=1200, all four arms):
realised component rejection rate ~0.075 at gamma=0.025 (CP-upper ~0.088; the
S4.4 acceptance bar is <= 1.25*gamma = 0.031) and ~0.04 at gamma=0.00625
(CP-upper ~0.055; bar 0.0078). Diagnosis (isolated, not an estimator bug): the
concordance estimators are UNBIASED — averaged over reps, empirical Q_cr/Q_s/Q_r
match the theoretical bivariate-normal orthant probabilities at the true
(rho_c=0.5, rho_s=0.1, rho_r=0.1) to 3 dp, and inverting the mean concordances
recovers (0.606, 0.088, 0.108). The failure is that the SPEC-MANDATED per-
replication truncation ("if a concordance inversion has no root ... set that
rho_hat = 0") biases the SMALL components (rho_s, rho_r = 0.1, sitting just above
the independence floor) downward: per rep their noisy concordance often dips
below the floor and truncates to 0, so the estimated dependence under-states the
reviewer/seed clustering, the null-boundary bootstrap of pihat* is UNDER-
DISPERSED (sd 0.059-0.072 vs the true pihat sd 0.084), and the observed pihat
looks too extreme too often -> inflated rejection. Fed the TRUE (0.5,0.1,0.1),
the same bootstrap is well-calibrated (sd 0.091 >= 0.084). This is exactly the
failure mode the S4.4 battery exists to catch — so it is a real result about the
pinned test, not a harness artifact. **Claim-level consequence (measured):** the
IUT conjunction TEMPERS it — F4 (only pi_H at boundary, contrast component also
binding) FWER = 0.000; but F5 (Delta^UCT_H,A2IR = +0.16 ABOVE delta_T so the
CONTRAST component is a true effect and the GATE is the binding true null)
propagates the inflation to the claims: C-CON-SUP-H/A2IR reject ~0.02 each (vs
0.00625 local level) and familywise FWER = 0.037 (CP-upper95 = 0.052), still
under tau_FWER = 0.055 but with much less margin than the other cells (~0.01).
**Routing:** this is a candidate SPEC DEFECT (the pinned gate dependence
estimator + zero-truncation does not deliver the finite-sample level control the
graphical procedure requires at small seed/reviewer dependence) OR at least an
obligation the design must discharge before freeze — either revise the estimator
(e.g. a conservative dependence floor / shrinkage instead of hard truncation to
0, or a bias correction), or demonstrate gridwide that claim-level FWER holds
under tau_FWER despite the component-level battery result. Flagged, NOT resolved
locally (S9).

**A3. (no defect found) The 12-claim procedure, weights, transition matrix,
update algorithm, IUT/TOST composition, truth functions, grid expansion, and
seed system were all codeable with zero remaining design decisions** — grid cell
counts resolve to exactly the pinned 74 FWER + 36 power + 4 gate-cal, the graph
satisfies the Bretz-2009 conditions (nonneg initial weights sum 1, zero
diagonal, row sums <= 1), and the S5 truth functions reproduce the S5-cited
F4/F8/F9 truth-set corrections. No contradiction requiring design escalation was
hit in the confirmatory core.

## B. Disclosed environment / scope deviations (MOCK build — not spec defects)

**B1. Version pins unmet on this box.** S2/R8g pins CPython 3.12.x, numpy 2.1.3,
scipy 1.14.1. This box has CPython 3.9.25, numpy 2.0.2, scipy 1.13.1 (Python
3.9 cannot install the pinned numpy/scipy). The pinned Philox generator +
SeedSequence substream discipline is fully implemented and works identically on
these versions; bit-exact cross-version reproduction of the pinned draws is
therefore NOT asserted. A version bump is a logged re-pin per S2 — recorded here.

**B2. Inference estimator is the balanced pooled-ANOVA closed form, NOT the
byte-identical lme4 REML.** The mock fits, per family per replication, ONE
balanced crossed-family ANOVA (arm fixed; concept, concept x arm, seed, seed x
arm random; residual) and reads each registered contrast's theta_hat (= arm-mean
difference, = GLS under balance), SE, and Satterthwaite df from the pooled mean
squares. This is a VALID (super-uniform under the null) mixed-model contrast test
— which is the property the FWER simulation validates — and pools the seed x arm
component across arms so it carries (A-1)(S-1) df (18 for UCT, 14 for composite)
rather than the 2 df a single paired difference would give. It is NOT numerically
identical to lme4 to the S4.2 tolerances, so the mandatory fixture-equivalence
check (|d theta| <= 1e-7, rel SE <= 1e-5, rel nu <= 1e-3, |dp| <= 1e-6) is
DEFERRED (no R on this box), not asserted. Two documented conservatisms in the
pooled ANOVA (both cancel in the registered contrasts and only inflate the SE
mildly): consumer/reviewer crossed nuisance folded into the concept x arm /
residual strata; composite residual heteroscedasticity (reviewed vs unreviewed)
averaged into one pooled residual — affecting only the nonce shuffle
reviewed-vs-unreviewed C-VAL components, never the UCT / Delta^G true nulls.
Consequence for the results: FWER control is validated ROBUSTLY (the weighted-
Bonferroni graphical procedure controls FWER <= alpha for ANY valid component
p-values; Satterthwaite df only moves the realised rate toward but never above
alpha). Power is a fair estimate under the pooled closed form; the joint lme4
fit could differ at the S4.2 tolerance but not in the qualitative power picture.

**B3. Stage-1 binding futility (S4.6) and the Rung-0 nested-interim branch
(S4.8/§7) are implemented structurally but not wired into the mock FWER/power
cells, because for every mock cell their futility/rung-0 parameters sit far from
their boundaries (default d0=+0.20, pi=0.85 or pi0, Delta^G>=delta_G) so they
never fire.** Both are binding-futility-only: they can ONLY remove rejection
opportunities, hence are conservative for FWER — omitting them makes the FWER
test STRICTER, so the validated control is if-anything an upper bound. The
Rung-0 module (U_ell(r), transfer envelope, Welch-Satterthwaite df, integer
looks, F10 termination rule) is provided as rung0.py and exercised by its own
mock; the F10/P6 termination-acceptance cells still need a dedicated run.

**B4. Bounded-Beta gate threshold recalibration (S4.4) is stubbed to the
Gaussian threshold in the mock.** The Gaussian-regime and block-regime cells
(all mock validation cells here, and all of F4-F10 + the gate-calibration
battery) are unaffected. Bounded-Beta gate-boundary cells (the beta variants of
F4/F5/F11) require the pinned 10^7-draw per-cell recalibration before the frozen
run; the hook is present (dgm._gate_thresholds) but returns the Gaussian
threshold pending that implementation.

## C. Deferred acceptance obligations (NOT discharged by the mock)

- S2 determinism check (100 pinned (config, rep) pairs, bit-identical rejection
  vectors) — the seed system is deterministic and reproducible, but the formal
  100-pair artifact is not emitted.
- S4.2 fixture-equivalence vs R/lme4/lmerTest (B2) and the F2/P1 2,000-flip
  sign-permutation concordance.
- The S8 normative resolved-configuration JSON (config_index -> vector -> truth
  set + rotation tables), hashed before any replication — the enumeration and
  truth engine are implemented (grid.enumerate_cells + hypotheses.truth_set);
  the hashed artifact emission is a small addition for the frozen run.
- Full-scale acceptance (R = 40,000 FWER / 10,000 power) — the mock deliberately
  runs only hundreds-to-thousands of reps.

---

## A4 RE-VALIDATION (Rev9/R9a floored test — 2026-07-21) — RESOLVED-PENDING-CONFIRM

The R9a floored bootstrap plug-in (rho~; ledger-C `gate_test.floored_triple`)
was applied and the S4.4 gate-calibration battery re-run at MOCK scale (R = 3000
per cell; NOT the frozen R = 40,000) over the 4 pinned cells
{rho in {0.1, 0.8}} x {n_nonce in {96, 160}}, Gaussian, pi_a = pi0 = 0.60.

**Acceptance (every (cell, arm, gamma) CP-upper95 <= 1.25*gamma): ALL PASS.**
Worst-case across all 4 cells x 4 arms:
- gamma = 0.025 : worst realised rate ~0.008, worst CP-upper95 = 0.0116 (bar 0.03125) — PASS
- gamma = 0.00625: worst realised rate ~0.002, worst CP-upper95 = 0.0044 (bar 0.0078) — PASS
(Before R9a, the same cell measured ~0.075 at gamma=0.025 / CP-upper 0.088 — a
clean FAIL. The floored plug-in collapses the rejection rate by ~10x.)

**Mandatory dispersion diagnostics (R9a): PASS, no flags.**
- SD-ratio (mean bootstrap-null SD of pihat* / empirical SD of pihat) = 1.20-1.24
  in EVERY (cell, arm); min 1.20 >= 1 -> the R9a mechanism prediction (ratio >= 1,
  i.e. the null bootstrap is now OVER-dispersed, the super-uniform direction)
  HOLDS everywhere. No ratio < 1 flag. (Before R9a: ratio ~0.70, under-dispersed.)
- Floor-binding rates P(rho_hat_s < 0.15), P(rho_hat_r < 0.15) = 0.86-0.92 across
  cells — the floor is operative in ~9 of 10 reps, as expected in this
  battery-scoped floor-binding regime (true seed/reviewer dependence 0.10 < the
  0.15 floor). rho~ quartile medians: c ~ 0.51 (adaptive, unfloored), s = r =
  0.150 (floored). Above-floor adaptivity is retained but rarely triggered here
  by design.

Per-cell verdicts (all four): rho0.1/n96 PASS; rho0.8/n96 PASS; rho0.1/n160 PASS;
rho0.8/n160 PASS. Artifacts: `results/gatecal_r9a/cell_*_R3000.json`,
`results/gatecal_r9a/gatecal_r9a_summary.json`, `results/gatecal_r9a/log_*.txt`.

**Status: A4 RESOLVED-PENDING-CONFIRM.** The R9a fix demonstrably restores
finite-sample level control at the previously-failing cells with comfortable
margin, and the mechanism diagnostic (SD-ratio >= 1) confirms the intended
over-dispersion. "PENDING-CONFIRM" only because this is the R = 3000 MOCK; the
frozen-run obligation is the full R = 40,000 battery (tighter CP bounds; expected
to pass with even more margin since the point rates are already ~0.002-0.008 <<
the gammas). No claim-level FWER re-run was needed to clear the block: R9a makes
the boundary gate STRICTLY MORE conservative (over-dispersed null -> higher p ->
fewer rejections), so it can only REDUCE the F5 marginal FWER (0.037) measured
pre-R9a, never inflate it.

**Full-run unblock verdict:** the gate calibration now PASSES at mock scale on
all 4 cells with margin and clean dispersion diagnostics -> the A4 blocker is
cleared for the full run, pending the routine full-R=40,000 battery in the frozen
run. Remaining pre-freeze items are unchanged (B2 lme4 fixture; B3/B4 wire
futility+Rung-0 / bounded-Beta gate recalibration; compute path).

---

## FULL-RUN-READY INCREMENT (2026-07-21) — B3 / B4 / gate-opt / S8+determinism

Each item coded + hard-verified.  No full grid run; no git commit.

### B3 — Stage-1 futility (S4.6) + Rung-0 (S4.8/§7) WIRED — DONE
`futility.py` (S4.6 nominal moment-SE with the R9a floored rho~ and the exact
design pair counts; graph-branch UB) and `rung0.py` are wired into
`pipeline.run_replication` (flags `use_futility` / `use_rung0`, default ON =
full-run-ready).  Both are binding-futility-only and draw only from their own
substreams (rung0: SS_RUNG0/SS_PILOT; futility: no new draws), so ON-non-firing
== OFF exactly.  VERIFIED (verify_item1.py, R=300 paired on identical seeds):
- (a) regression F3: ON vs OFF rejection vectors bit-identical, 0/300 mismatch
  (futility fired harmlessly on 2.7% of reps, outcome unchanged).
- (b) gate-futility FIRES (custom pi_a=0.40 < pi0): fire rate 0.973; FWER_ON
  (0.0000) <= FWER_OFF (0.0000).
- (c) graph-futility FIRES (F9, Delta^G=0): graph_futile rate 0.607; FWER_ON
  (0.0100) <= FWER_OFF (0.0100).
- (d) Rung-0 TERMINATES (custom d0(r)=-0.5): terminate rate 0.987; C-VAL
  rejection drops 0.9967 (OFF) -> 0.0133 (ON) — a terminated branch tests no
  confirmatory claim, as pinned.
Monotonicity FWER_ON <= FWER_OFF held in every cell (conservative, as the theory
requires).

### B4 — bounded-Beta gate threshold recalibration (S4.4) — DONE
`dgm.compute_gate_thresholds(t, config_index)` replaces the Gaussian stub: for
the bounded-Beta regime it computes t_a = the (1-pi_a)-quantile of Z's marginal
from 10^7 pinned MC draws on SeedSequence([BASE_SEED, config_index,
999_999_999]) (chunked; Z = sqrt(fc)*Cbeta + sqrt(fs)*N + sqrt(fr)*N +
sqrt(fe)*N), computed ONCE per cell and threaded to the DGM.  VERIFIED
(test_b4.py):
- marginal mapping RESTORED: recalibrated threshold gives P(g=1)=0.595 ~= pi0
  (0.60); the naive Gaussian threshold gives 0.579 (biased low ~0.02).
- gate-cal battery on the bounded-Beta cell (rho=0.1, n=96, R=2000): ALL 4 arms
  x 2 gamma PASS (CP-upper 0.0078-0.0180 at g=0.025 <= 0.031; 0.0015-0.0052 at
  g=0.00625 <= 0.0078); SD-ratio 1.19-1.23 (>=1), no flags.
Artifact: results/gatecal_r9a/cell_beta_rho0.1_n96_R2000.json.

### Gate-test OPTIMIZATION (95% of full-run cost) — DONE, numerically equivalent
`gate_test.orthant_p11` replaced scipy.stats.multivariate_normal.cdf with the
EXACT closed-form bivariate-normal orthant via 128-node Gauss-Legendre on the
1-D reduction P = int_z^inf phi(x) Phi((rho x - z)/sqrt(1-rho^2)) dx (raw ndtr).
The B=999 bootstrap was already loop-free/vectorised (kept float64 to preserve
exactness).  VERIFIED (test_gate_opt.py):
- orthant vs scipy mvn.cdf: max abs diff 8e-15 over 3000 random (rho, z).
- end-to-end gate p-value (optimized vs mvn.cdf-orthant reference, identical
  bootstrap RNG state): **max abs diff 0.000e0 over 250 random cases** (0/250
  differ) — numerically equivalent, not an approximation.
- orthant 20 us/call (was 221 us scipy); per-rep F3 base 140->81 ms bare;
  full-run-ready (futility+rung0 ON) 95.8 ms base / 154 ms esc.
- REVISED full-grid estimate: **108.7 core-hours** (94.3 FWER + 11.6 power +
  2.7 gate-cal + beta recalib), vs the ~220 core-h pre-opt estimate — **2.0x**.
  Single-core ~4.5 days; 2-core ~2.3 days; the loop is embarrassingly parallel
  (independent per (config_index, replication)) so ~3.4 h on 32 cores, ~1.7 h
  on 64 cores.

### S8 artifacts + S2 determinism — DONE
- `emit_config.py` -> results/99a-r8-simspec-config.json (config_index ->
  parameter vector -> truth-engine-derived truth set + consumer/reviewer
  rotation tables), sha256 in-file.  VERIFIED hash STABLE: two emissions produce
  byte-identical files, sha256 dc2ed1c5...d531 both times.
- `determinism_check.py` -> results/99a-r8-simspec-determinism.json: 100 pinned
  (config_index, replication_index) pairs, each run TWICE.  VERIFIED **0/100
  mismatches — all rejection vectors bit-identical** (rejection-vectors sha256
  74a870c8...).

### B2 — lme4/lmerTest fixture-equivalence — DEFERRED (no R on box)
`which Rscript R` -> none installed on this host; the S4.2 fixture-equivalence
check against R 4.4.1 + lme4 1.1-35.5 + lmerTest 3.1-3 cannot run here and stays
DEFERRED to the pinned-stack many-core box (the only remaining coded-but-
unverified obligation).
