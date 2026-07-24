# 99a v2 durable grid — RUN-RECORD (OPUS experiment-runner)

Corrected total-loss-proof harness (`kot_99a_grid_v2.py`) on the FRESH Modal
workspace **jesse-70413** (modal3.env), after the v1 loss (workspace spend-limit).
Mechanical results only — NO scientific conclusion on the acceptance artifact.

## Provenance / pins
- Workspace: jesse-70413; grid app `ap-J7bDiBKhxI7v7cr01RMaCe` (stopped).
- Pinned image rebuilt on fresh workspace, digest `im-sWxC9bdYsUS4CYB0mBNRfu`;
  `versions()` PASS: CPython 3.12.1 / numpy 2.1.3 / scipy 1.14.1 / R 4.4.1 /
  lme4 1.1.35.5 / lmerTest 3.1.3 (all 6 pins exact).
- Fail-closed PRE-FLIGHT gates re-verified on the fresh image, ALL PASS:
  exact-REML smoke (both families CompositeREML); B2/R12a fixture
  (UCT |Δp| 7.50e-7 ≤ B_run ~4.9e-6; COMP |Δp| 1.018e-6 ≤ ~4.9e-6); S8 hash
  `dc2ed1c5…d531`; determinism 100/100 (`74a870c8…9f`); small-slice
  (F3 CP-up 0.0152; F11 0.000; gate-cal min SD-ratio 1.2025).
- Seeds (S2/R8g): base_seed 990066001; per-rep SeedSequence([990066001,
  config_index, replication_index]).spawn(13) Philox; beta-cal stream tag
  999999999. config_index 0..113. Deterministic (determinism gate PASS).
- Harness: single `cpu=32` container, in-Pool 30 workers (BLAS threads pinned
  to 1), durable per-cell writes to Modal Volume `kot-99a-grid-vol` committed
  after each cell, resumable, shortest-first ordering, cell-level exception
  isolation (a raising cell -> durable ERROR record; batch continues).

## Outcome: 114/114 cells banked; 14 OK / 100 ERROR (fit-failure rate 0.8772)

The FROZEN exact-REML estimator raises `numpy.linalg.LinAlgError` on ~88% of
cells at full R. Durable + resumable design meant ZERO data loss this run.

### Fit-failure signature + path (for the Fable estimator-robustness fix)
- Exact error, 3 variants: `numpy.linalg.LinAlgError: N-th leading minor of the
  array is not positive definite`, with N ∈ {5 (61×), 10 (38×), 8 (1×)}.
- Fit path (both families): `pipeline.run_replication` →
  `reml_composite.get_comp(t).fit(Ycomp)` / `get_uct(t).fit(Yuct)` →
  `reml_composite.fit` (the L-BFGS-B `minimize` over the 6 variance components,
  lines 319/327 — BOTH the first-start and the second-start calls) →
  `obj` (line 315) → `deviance_fast` (line 220) → `scipy.linalg.cho_factor(XtVinvX)`.
  The GLS information matrix `XtVinvX` loses positive-definiteness while the
  optimizer probes φ (variance vector) during its finite-difference gradient.
  - N=10 ⇒ UCT family (10 arms, get_uct); N=5/8 ⇒ composite family (8 arms, get_comp).
- Trigger: a rare per-rep event (~1 in tens-of-thousands); at R=40,000/10,000
  it fires at least once in ~88% of cells (ERROR cells ran ~70 min mean before
  raising — the failure is LATE in the rep loop, not the first reps).

### PATTERN (which cells fail)
- **By kind:** gate-cal 4/4 OK (structurally exempt — gate-cal runs only the
  bootstrap gate test, NEVER the exact-REML estimator). FWER 71/74 ERROR (3 OK).
  Power 29/36 ERROR (7 OK).  ⇒ the failure is intrinsic to the exact-REML fit,
  which every FWER/power cell invokes.
- **Not** confined to low-ρ / boundary / gaussian: ERROR spans every ρ
  {0.0:17, 0.1:32, 0.5:24, 0.8:27}, every regime {gaussian:70, beta:27, block:3},
  both n-levels {base:60, esc:40}. Mild tendency for higher-ρ cells to survive
  (OK skews to ρ=0.8: 8 of 14 OK). The 14 OK cells are essentially the ones
  that did not trigger the edge case within their R reps (plus the 4 exempt
  gate-cal cells) — NOT a clean scientific subset.
- OK cells (idx): 17(F2 block), 56(F10 gauss ρ.8), 63(F11 beta ρ.5),
  76/77(P1), 81(P2), 88(P3), 94(P4), 100(P5), 109(P6), 110-113(gate-cal).
- Full inventory: `grid-run-v2/fit-failure-inventory.json`.

## Mechanical verdict — OK CELLS ONLY (14/114; NOT an acceptance)
FWER (S6, τ_FWER=0.055): 3/3 OK cells PASS — idx17 F2 CP-up 0.00227; idx56 F10
0.01198; idx63 F11 0.00007.
Gate-cal (S4.4): 4/4 PASS, min SD-ratio 1.211 (all γ bars).
Rung-0 termination: idx56 F10 CP-up 0.00007 ≤ 0.055 PASS; idx109 P6 CP-up
0.00030 ≤ 0.025 PASS.
Power floors (S7, escalated floored): the ONE OK escalated floored cell idx77
(P1, ρ=0.1) CVAL_DEFNSUP CP-lower 0.1126 < 0.90 (mechanical FAIL vs the floor);
base-level OK power reads reported in `mechanical-verdict.json`.
**These cover only the non-crashing cells; 71/74 FWER-family and 29/36 power
cells are UNEVALUABLE (fit-failure). No acceptance conclusion is drawn.**

## Actual cost / wall-clock (jesse-70413)
- Compute Σ`_wall_s` = 532,758 s ≈ **148 core-hours** actual work; container
  reserved cpu=32 for ~5.9 h (longest cell 21,177 s) ⇒ ~**190 core-h billed**
  ≈ **$30–45** (Modal CPU $0.135–0.192/core-h + 32 GB memory). Plus the fresh
  image build + 5 pre-flight gates + 2 crashed launches ≈ $5–10. Exact $ on the
  jesse-70413 dashboard. (Separate sunk v1 loss on jwrightwho ≈ $58–88.)
- Per-rep on the single container ran ~4× the isolated warm bench (Pool + vCPU
  contention), so wall-clock was ~5.9 h not the ~3.5 h projection.

## Disposition (Fable's call — NOT mine)
The frozen exact-REML estimator needs numerical hardening before the acceptance
simulation can complete: guard `deviance_fast`'s `cho_factor(XtVinvX)` (e.g.
symmetric jitter / `cho_factor(..., check_finite)` + PD-fallback, or a
pseudo-inverse / eigen-clip of XtVinvX, or reject non-PD φ in `obj` by returning
+inf), and/or add per-rep fit-failure handling in `driver.run_cell` with a
specified FWER treatment (S8 anticipates "fit-failure rates"). I did NOT touch
the frozen estimator and did NOT retry the failed cells — the durable Volume
`kot-99a-grid-vol` (114 cells, 14 OK already banked) means a post-fix re-run
skips the OK cells and re-runs ONLY the 100 failed cells cheaply.
`fable_interpretive_assessed: pending`.
