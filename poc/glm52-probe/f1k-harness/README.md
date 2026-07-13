# F1-K single-instance run harness (colibri engine + KaE ADD patch)

> **BUILD + MOCK-VALIDATE pass only.** This directory contains the F1-K run
> driver and bring-up scripts, built and validated end-to-end against a stub
> engine for **$0**. Nothing here launched an instance, downloaded a model,
> took a git action, or wrote a registry entry. The **coordinator** owns the
> spot-instance launch, sharding orchestration, collection, and the go/no-go,
> and reviews this driver against the frozen protocol before any real run.
> No feasibility conclusion is stated by anything in this directory; the mock
> outcome below is a **wiring validation**, not evidence.
>
> Engine naming: the C engine is referred to only as **colibri**, pinned by
> base commit sha (no upstream org/author string appears in this harness,
> per the kae-patch-draft README etiquette). No new ASM entries are claimed
> by this pass.

## Files

| File | What it is |
|---|---|
| `bringup.sh` | Instance bring-up: clone colibri @ `a78a06fc5acc4b0dc0f9ef03987c66b0559d1250`, verify + apply the gate-0 KaE patch (sha256-pinned), build, **assert 44/44 `test_kae` checks**, prove **inert-by-default** (per-function machine-code equivalence with `KAE` unset), and **document** (not execute) the model-fetch step. Fail-closed throughout. |
| `f1k_driver.py` | The run driver implementing the frozen protocol exactly: `--phase pilot` / `--phase guard` / `--phase test`, per-item checkpoint/resume, rows + sidecar in `analysis/f1k.py`'s exact schema, `--mock` for the $0 end-to-end validation. Every frozen constant cites its source in-line. |
| `pilot.sh` | Pilot bring-up wrapper: preflight pins → `(L,g)` selection over the 4-member family-blind panel → affordability / power / placebo gates at pilot n → addenda (5)/(7) + (6)-inputs artifacts. |
| `mock_colibri.py` | Deterministic stub of the engine's `KAE_SCORE` path (exact interface; mock only). |
| `mock-out/` | Regenerable mock outputs (not evidence; safe to delete). |

## Coordinator run sequence (the real run — every step coordinator-owned)

Ordering is the frozen §R-REV4.2 sequence; the test set stays untouched until
(A), (B0), (5), (7), (6) are ALL committed.

1. **Freeze-manifest (A) + corpus pins** — already the coordinator's freeze
   package: `f1k-trigger-map-v1`, the carrier GENERATOR, all seeds, template
   bytes/label ids/tie-break, guard/dev/test id-list hashes
   (`registry/experiments/f1k.json` `design.n_planned.freeze_manifest`).
2. **Launch the spot i4i.2xlarge** (default for all GLM-5.2 runs;
   `docs/next/design/glm52-f1k-cost-reduction.md`).
3. **`bringup.sh`** (with `COLIBRI_GIT_URL` exported) — engine pinned, patch
   verified + applied, 44/44 unit checks, inert-by-default proven. Any
   failure aborts bring-up.
4. **Model fetch** (documented in `bringup.sh` step 6, not automated):
   stage the GLM-5.2 snapshot; **pin the weight content hash** →
   `f1k.json pins.model_revisions.glm52-weights` (PINNED-AT-INPUTS,
   ASM-1971); re-verify colibri knob semantics.
5. **Carrier construction + (B0)** — the frozen generator run (outside this
   driver; §R-REV3.3); realized tables + raw/rescaled norms committed as the
   pure-function addendum, completing `f1k-carriers-v1`.
6. **`pilot.sh --config run-config.json --outdir out/`** — produces
   `out/pilot/addendum-5-frozen-lg.json` (the frozen `(L,g)` the main run
   uses), `addendum-7-affordability.json` (measured s/prefill vs the $149
   ceiling, §R6 degradation order applied deterministically), and
   `addendum-6-inputs.json` (dev δ̂ upper-80, n at the cap, the dev
   cluster-difference distribution for the sign-symmetry check). Gates
   fail closed: power (C≥65 each m≥8, n=1440), placebo (any-magnitude,
   ASM-2273), affordability ($149).
7. **Coordinator review + commits**: addenda (5)/(7), then the (6) power
   freeze including the dev-selected `inference.{method,
   dev_sign_symmetry_pass}` (§R-REV4.1a — the driver reports the dev data
   verbatim and never decides the method itself). These enter
   `run-config.json` (`frozen_lg`, `inference`, `freeze.manifest_flags`).
   **The coordinator reviews this driver against the frozen protocol here,
   before any test prefill.**
8. **`f1k_driver.py --config run-config.json --phase guard --outdir out/`**
   — 60-item off-concept byte-identity guard (XCACHE forced off both
   directions, ASM-2306); any mismatch VOIDS.
9. **`f1k_driver.py --config run-config.json --phase test --outdir out/`**
   — the main campaign, 8 passes × 1,440 items, one candidate-independent
   label-logit prefill per unit, per-item checkpoint (a spot interruption
   just resumes: re-run the same command). Emits `out/test/rows.jsonl`,
   `out/test/sidecar.json`, `out/test/run-record.jsonl`.
10. **Collection + verdict**: the coordinator collects the artifacts;
    verdict-gen pipes the eligible run records to the **pinned**
    `analysis/f1k.py` on stdin (the driver never grades; run-vs-analysis
    separation).

`run-config.json` schema: see the generated example at
`mock-out/fixtures/mock-config.json` (same keys; a real config points
`engine.argv` at the patched colibri binary + snapshot args and carries the
coordinator-committed freeze/inference blocks).

## $149 accounting (validated reduced ceiling — ASM-2205)

Ceiling arithmetic (verbatim from `glm52-f1k-cost-reduction.md`):
`22,920 prefills × 100 s ÷ 1.20 (pinning, pessimistic) ÷ 3,600 × $0.28/h
(spot i4i.2xlarge) = $148.56 → **$149**`. EC2 instance compute only;
storage/tax/transfer separately accounted.

This driver's realized prefill volume sits **inside** the registered
worst-case envelope (`f1k.json design.n_planned.scoring_passes`):

| Stage | Prefills (this driver) | Registered envelope |
|---|---|---|
| Main arms (b0, d0, d1-drng ×3, d2, d3-text, K) | 8 × 1,440 = **11,520** | ≤ 12,960 (9 passes incl. conditional REPLACE) |
| Off-concept guard | 60 × 7 = **420** | ≤ 660 |
| Pilot (9 configs × 4 panel × 48 dev + b0 dev pass) | **1,776** | ~6,200 |
| Carrier construction (outside this driver) | ≤ 3,072 | ≤ 3,072 |
| **Total** | **≤ 16,788** | ≤ 22,920 |

At the pessimistic corner (100 s/prefill ÷ 1.20 × $0.28/h): ≈ 389 h ≈
**$109** — under the $149 cap with margin. The cap itself is enforced twice:
the pilot's addendum-7 affordability gate projects from the **measured**
s/prefill and applies the §R6 degradation order deterministically
(R 5→3 pre-applied; REPLACE already deferred; then defer d3-text; then STOP
— n is never cut below n_required, no ladder arm dropped), and the driver's
cost ledger lands in the sidecar (`cost.usd_total/instance_hours/prefills`)
for `/analysis/cost_ledger`.

Spot interruption safety: per-item checkpoint (`rows.jsonl` is the resume
state, torn-tail tolerant); re-invoking the same phase resumes. Expert
pinning (`PIN=`/`PIN_GB`) and the optional XCACHE cache are clean env
pass-through seams (`engine.env` in the config); the pilot may run
cache-off, and the guard **always** runs cache-off (ASM-2306).

## Frozen-protocol value audit (driver ↔ source)

Every constant in `f1k_driver.py` cites its source in-line; this table is
the coordinator's driver-vs-protocol audit map. **No invented thresholds.**

| Driver constant | Value | Frozen source |
|---|---|---|
| `ARMS_MAIN` | b0, d0, d1-drng, d2, d3-text, K | `f1k.json` `design.independent_vars.arm`, `arms_mandatory_baselines` |
| REPLACE | fail-closed refusal | no-op stub in gate-0 patch (`kae.h kae_replace_note`); DEFER unless dev δ_R ≤ ~0.038 (§R-REV4.3/ASM-2124) |
| `R_DRNG` / `DRNG_SEEDS` | 3 / [101, 102, 103] | `f1k.json` `design.seeds`; SSR6 step 1 pre-applied (ASM-2272); `analysis/f1k.py` `DRNG_SEEDS` |
| `N_TEST` | 1,440 | `f1k.json` `design.n_planned.n_test_items` (runs AT the cap, §R-REV3.1 item 4); `analysis/f1k.py` `N_REGISTERED` |
| `DEV_N` / `GUARD_N` | 96 / 60 | `f1k.json` `design.n_planned.dev_split_items` / `off_concept_guard_items` |
| `POWER_GATE_MIN_C/M` | 65 / 8 (each-cluster) | `f1k.json` `design.n_planned.power_gate` (ASM-2271) |
| Scorer | ONE prefill/item/arm; argmax over K label-token logits; lowest-index tie-break | §R1.1 / `f1k.json` dependent_vars.item_correct; engine `run_kae_score` via `KAE_SCORE` |
| Template identity | byte-identical across arms except d3-text (prompt text, no splice); spans frozen per item | §R1.1/§R-REV2.1; §2.6 arm d3-text |
| Pilot grid / subset | 3 layer sets × 3 g on 48-item stratified dev | `f1k.json` `design.n_planned.pilot`; §2.3 |
| Panel + blindness | 4 members {K-true, K-drng seed 11, d2, d0 seed 7}; equal FAMILY-level weight; tie-break fewer layers → lower g | §R-REV2.3/§R-REV3.2 (ASM-2113); §R4; seeds: freeze-manifest A(vii) |
| Placebo gate | one-sided cluster sign-flip p < 0.05 at ANY magnitude | ASM-2273 (no +3 floor); §2.6 d0 row |
| Sign-flip mechanics | B=10,000, add-one, seed 20260713 + per-contrast sub-seeds | `analysis/f1k.py` `SEED/B` (ASM-2271) — driver mirrors it for the pilot alarm only; verdicts run exclusively in the pinned analysis |
| δ̂ estimator | one-sided 80% upper bound; n_required = δ̂_U·DEFF/SE², SE ≤ 1.2 pts, ρ_U = 0.10 | §R-REV2.4 entry-6 rule; §R-REV2.2; §R-REV3.1 |
| `USD_CAP` / rate | $149 / $0.28/h spot | `f1k.json` `budget.usd_cap`; `glm52-f1k-cost-reduction.md` (ASM-2205) |
| Degradation order | R 5→3 → defer REPLACE → defer d3-text → STOP | §R6 |
| Guard rule | byte-identity vs b0; mismatch VOIDS; XCACHE off | §2.5; `f1k.json` kill_criterion_verbatim; expert-cache ASM-2306 |
| `CEILING_B0` | 0.95 (echoed, never moved) | §2.7; `analysis/f1k.py` `CEILING_B0` (immutable) |
| Inference block | `{method: signflip\|bca, dev_sign_symmetry_pass}` coordinator-committed at addendum (6) | §R-REV4.1a; `f1k.json` harness_manifest (coherence enforced fail-closed by the analysis) |
| Rows/sidecar schema | exact `analysis/f1k.py` input contract | `analysis/f1k.py` docstring "ROWS (JSONL)" / "SIDECAR" |
| Engine pins | colibri `a78a06fc…d1250`; patch sha `11f8b458…d9cb` | `f1k.json` `pins.model_revisions` / `pins.harness_manifest` |

## Mock validation record (2026-07-13, $0)

`python3 f1k_driver.py --mock` (also reachable as `pilot.sh --mock`) ran the
ENTIRE wiring against the deterministic stub — pilot ((L,g) selection +
three gates + addenda) → guard (60 × 6 spliced passes byte-identical to b0)
→ test campaign (11,520 units with a FORCED interruption after 2,000 units
and a per-item-checkpoint resume, no duplicates) → sidecar → run-record →
**pinned `analysis/f1k.py` ingest: exit 0**, all 7 gates true, all 50 output
fields emitted. The stub plants a +10-pt K lift (mirroring the analysis'
own `--selftest` campaign), so the mock reaches the full PASS-shaped verdict
surface (k1/k2 fire, ladder rung 2, kill/null false) — demonstrating the
machinery, **not** a result. Repeated runs are byte-identical on every
verdict-bearing artifact (rows, statistics); only measured wall-clock cost
fields differ, as designed.

## Governance self-check (this pass)

- engine referred to as **colibri** only; no author handle in any file
- NO git action, NO registry write, NO model download, NO instance launch,
  NO spend ($0); the mock stub is the only thing executed
- no new ASM entries claimed; no DERIVED tag used anywhere
- every frozen-protocol constant cites `f1k.json` / a design section
  (table above); the driver never grades — verdicts belong to the pinned
  `analysis/f1k.py` via verdict-gen
- REPLACE refused fail-closed (no-op stub; deferral is the registered modal
  expectation)
