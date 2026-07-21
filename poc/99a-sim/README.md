# 99a SIM-SPEC — FWER/power Monte-Carlo simulation (MOCK build)

Implementation of the pre-registration ACCEPTANCE-ARTIFACT simulation specified
in `docs/next/design/kernel-construction-methodology-proposal-99a.md`
(## SIM-SPEC, S1-S9; §4.6 analysis ledger + 12-claim graphical procedure; §4.8
operational layer; §5 null functions; §7 Rung-0). This is a MOCK build +
small-scale validation, NOT the frozen full-grid run. Nothing here is
registered, frozen, or committed by this build.

Environment (reportable version mismatch, S2/R8g): spec pins CPython 3.12 /
numpy 2.1.3 / scipy 1.14.1; this box runs **CPython 3.9.25 / numpy 2.0.2 /
scipy 1.13.1** (Python 3.9 cannot install the pinned versions). See
SPEC-DEFECTS.md B1.

## Module layout (spec cross-references in each file)

| File | Spec | Role |
|---|---|---|
| `pins.py` | S2/S3 | pinned parameters, seed pins, arm/claim indexing |
| `hypotheses.py` | S1/S5 | **the ONE shared truth engine**: null_j(theta) + truth_set, imported by BOTH the test engine and the truth derivation (S9 forbids duplication) |
| `seeds.py` | S2/R8g | Philox + SeedSequence, 13 named substreams, config_index->seed |
| `stats_util.py` | S2/S6/S7 | exact one-sided Clopper-Pearson bounds, t helpers |
| `copula.py` | S4.3 | concept-layer copula: gaussian / bounded-Beta / block regimes |
| `dgm.py` | S4.1/S4.4 | arm-side crossed-effects DGM (UCT, composite, format, gate) |
| `inference.py` | S4.2 | balanced crossed-family ANOVA closed-form contrast test (theta_hat, SE, Satterthwaite nu, one-sided p / test-CI bound) |
| `gate_test.py` | S4.4/§4.6(1b)(C) | crossed-binary latent-probit parametric-bootstrap gate test |
| `graphical.py` | §4.6(2)(3)(4) | initial weights, transition matrix, Bretz-2009 update, IUT/TOST |
| `rung0.py` | S4.8/§7 | nested cumulative interims, U_l(r), transfer envelope, F10 termination |
| `pipeline.py` | S1/S4.5-S4.7 | one full-pipeline replication + Stage-2 endogenous trigger, hierarchy selection |
| `grid.py` | S6/S7 | 74-cell FWER + 36 power + 4 gate-cal grid, config_index expansion |
| `driver.py` | S6/S7 | run a cell for R reps, count claim-level errors, CP bounds, timing |
| `emit_config.py` | S8 | normative resolved-config artifact (index->vector->computed truth set + rotation tables), hashed |
| `run_one.py`, `gate_cal_mock.py` | — | mock runners |

Grid enumeration resolves to exactly **74 FWER + 36 power + 4 gate-cal** cells;
the graph passes the Bretz-2009 conditions (nonneg initial weights sum 1, zero
diagonal, row sums <= 1); the S5 truth engine reproduces the S5-cited F4/F8/F9
truth-set corrections.

## Inference estimator (S4.2 operative path)

The frozen run pins REML + Giesbrecht-Burns Satterthwaite with R/lme4/lmerTest
as the executable oracle; S9 permits any numerically exact algorithm SUBJECT to
a one-time fixture-equivalence check. R is not available on this box, so this
mock implements the **balanced crossed-family ANOVA closed form** (which equals
REML in the interior for balanced data): one family ANOVA per family per
replication, from which every registered arm-mean contrast reads theta_hat, SE,
and a Satterthwaite df. It pools the seed x arm variance across ALL arms
((A-1)(S-1) df, vs the 2 df a single paired difference gives), which is what the
joint fit does. The lme4 fixture check is a SEPARATE, DEFERRED validation
(SPEC-DEFECTS B2), not asserted here. The p-values are valid (super-uniform
under the null), which is exactly what the FWER simulation validates.

## Mock-validation results (small scale; NOT the R=40k/10k full run)

FWER acceptance rule (S6): CP-upper95 <= tau_FWER = 0.055 for every cell.

| Cell | what | R | FWER (>=1 true null rejected) | CP-upper95 | verdict |
|---|---|---|---|---|---|
| **F3** (rho .1, base) | strong FWER: C-VAL opens ~99%, 7 downstream true nulls | 600 | 0.0100 +/- 0.0041 | **0.0196** | controlled |
| **F11** (rho .1, base) | GLOBAL NULL (all 12 nulls true) | 600 | 0.0000 | **0.0050** | controlled |
| **F4** (rho .1, base) | gate-boundary (pi_H=pi0) | 600 | 0.0000 | **0.0050** | controlled |
| **F5** (rho .1, base) | gate-boundary, gate is the BINDING true null | 600 | 0.0367 +/- 0.0077 | **0.0520** | controlled, reduced margin (see below) |

Global-null familywise rejection is 0.000 (<= alpha) -> **FWER control looks
correct** for the confirmatory graphical procedure.

Power cells (single-claim powers are all materially > alpha = 0.05):

| Cell | R | key power reads | path estimand |
|---|---|---|---|
| **P3** constructed-adoption (rho .5, base) | 500 | C-VAL 0.998, C-CON-SUP-H 0.414, C-GRAPH 0.048, stage2 fires 0.414 | P(C-VAL & C-CON-SUP-H & C-GRAPH) = 0.048 (CP-lower95 0.033) |
| **P3** (rho .5, ESCALATED n) | 500 | C-CON-SUP-H 0.446, C-GRAPH 0.066 | path = 0.066 (CP-lower95 0.049) — climbs with n |
| **P1** deflation-adoption (rho .5, base) | 500 | C-VAL 0.998, C-DEF-NSUP 0.100 | P(C-VAL & C-DEF-NSUP) = 0.100 (CP-lower95 0.079) |

The multi-claim CONJUNCTIVE path probabilities are well below the S7 0.90 floor
at these mock cells; the S7 floors are checked at the ESCALATED sample size and
escalation adds concepts, not seeds (n_seeds=3 is a hard precision floor via the
seed x arm variance). Whether the design meets the S7 floors is a SCIENTIFIC
question for the full run + design owners — NOT concluded here. The machinery
correctly: gates the family on C-VAL, controls FWER, fires the Stage-2 trigger
only when a C-CON-SUP is rejected, and increases power with n.

Rung-0 (rung0.py): F10 whole-branch termination rate 0.000 (CP-upper 0.004 <=
tau_term0 0.055), envelope coverage ~99.9%; P6 termination 0.000 (<= tau_term
0.025). Determinism: repeated (config, rep) yields identical rejection vectors.

### S4.4 gate calibration — A4 found + FIXED by Rev9/R9a (RESOLVED-PENDING-CONFIRM)

The first mock build MEASURED the mandated S4.4 battery FAILING (component gate
rejection ~0.075 at gamma 0.025 vs the 0.031 bar) — the pinned truncate-to-0
dependence plug-in under-disperses the null bootstrap at small seed/reviewer
dependence (SPEC-DEFECTS A4). Fable's **Rev9/R9a** replaced the bootstrap plug-in
with the FLOORED triple rho~ (floor seed/reviewer at rho_floor = 0.15, no concept
floor; point estimation unchanged). Applied to `gate_test.py` and re-validated at
R = 3000 over all 4 cells {rho in {.1,.8}} x {n_nonce in {96,160}}:

**ALL 4 cells x 4 arms x 2 gamma PASS** (worst CP-upper95: 0.0116 at gamma 0.025
vs bar 0.031; 0.0044 at gamma 0.00625 vs bar 0.0078). **Dispersion diagnostics:**
SD-ratio (bootstrap-null SD / empirical pihat SD) = 1.20-1.24 everywhere (>= 1,
mechanism confirmed; was ~0.70 pre-fix), no flags; floor-binding ~0.86-0.92.
Rejection rate collapsed ~10x (0.075 -> ~0.006). R9a makes the boundary gate
STRICTLY more conservative, so it can only REDUCE the pre-R9a F5 marginal FWER
(0.037), never inflate it. Full-run blocker CLEARED pending the routine
R = 40,000 battery. Artifacts: `results/gatecal_r9a/`.

## Full-run cost estimate (post gate-test optimization)

The gate test (95% of cost) was optimized: `orthant_p11` now uses the EXACT
closed-form bivariate-normal orthant (128-node Gauss-Legendre on the 1-D
reduction, raw `ndtr`) instead of scipy `multivariate_normal.cdf` — 20 vs 221
us/call, NUMERICALLY EQUIVALENT (gate p-value max abs diff 0.000 over 250 cases;
see SPEC-DEFECTS). The B=999 bootstrap is already loop-free (kept float64 for
exactness). Measured full-run-ready per-rep (futility+Rung-0 ON, fast orthant):
base n (48,96) **95.8 ms**, escalated n (96,160) **154 ms** (power 94 / 139 ms);
the bootstrap RNG is now the floor (orthant ~5%).

Full grid (R = 40,000 FWER / 10,000 power):
- FWER (50 base + 24 esc): ~94.3 core-h
- Power (18 base + 18 esc): ~11.6 core-h
- Gate-cal (4 cells, gate-only): ~2.7 core-h; bounded-Beta 10^7 recalib ~140 s
- **Total ~= 108.7 core-hours** (was ~220 pre-opt -> **2.0x**). Single-core ~4.5
  days; 2 cores ~2.3 days.

**Feasibility:** the loop is EMBARRASSINGLY PARALLEL (independent per
(config_index, replication)), so on the pinned-stack **many-core box it is
~3.4 h on 32 cores / ~1.7 h on 64 cores** — the recommended path. Not run here.

## Readiness — FULL-RUN-READY (pending the pinned-stack box + B2)

Everything the frozen run needs is coded and hard-verified:
- **A4** gate calibration FIXED (Rev9/R9a floored plug-in), re-validated: 4-cell
  battery ALL PASS, SD-ratio >= 1.20.
- **B3** Stage-1 futility (S4.6) + Rung-0 (S4.8/§7) WIRED (default ON): regression
  ON==OFF bit-identical; fires where params cross boundaries; FWER_ON <= FWER_OFF.
- **B4** bounded-Beta gate threshold recalibration (S4.4, 10^7 per-cell): marginal
  restored, beta gate-cal battery PASSES.
- **Gate-test optimization**: exact closed-form orthant, gate p-value max abs diff
  0.000 (numerically equivalent), 2.0x -> ~108.7 core-hours full grid.
- **S8 config** artifact emitted + hash-STABLE (byte-identical); **S2 determinism**
  100 pinned pairs bit-identical.

Remaining, both external to the code: (1) provision the pinned-stack (CPython
3.12 / numpy 2.1.3 / scipy 1.14.1) many-core box and run the full grid there
(~3-4 h on 32 cores); (2) **B2** the lme4/lmerTest S4.2 fixture-equivalence check
— DEFERRED (no R/Rscript on this host). See SPEC-DEFECTS.md.
