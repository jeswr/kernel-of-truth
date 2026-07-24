# F1-K single-instance run harness (colibri engine + KaE ADD patch)

> **BUILD + MOCK-VALIDATE pass only.** This directory contains the F1-K run
> driver, the carrier-construction generator, and bring-up scripts, built and
> validated end-to-end against stub engines for **$0**. Nothing here launched
> an instance, downloaded a model, took a git action, or wrote a results-log
> line. The **coordinator** owns the spot-instance launch, sharding
> orchestration, collection, and the go/no-go, and reviews this driver against
> the frozen protocol before any real run. No feasibility conclusion is stated
> by anything in this directory; the mock outcomes below are **wiring
> validations**, not evidence.
>
> Engine naming: the C engine is referred to only as **colibri**, pinned by
> base commit sha (no upstream org/author string appears in this harness,
> per the kae-patch-draft README etiquette).
>
> **Protocol revision note (2026-07-16).** This runbook states the CURRENT
> frozen REVISION-6 + freeze-(A)-completion protocol: **n = 1,573** test
> items over **C = 96** clusters (EQUALITY-form power gate), splice layers
> **3..77** (the registered A(iv) union; 75 DRAFT=0 MoE layers [ASM-2504]), **$129.40** mandatory-campaign
> worst case vs the **$155** cap (ASM-2374). The superseded n=1440 / $149 /
> C≥65 figures that earlier revisions of this file carried are historical
> only; where they appear in old logs they are superseded by
> `registry/experiments/f1k.json` (latest refreeze governs).

## Files

| File | What it is |
|---|---|
| `bringup.sh` | Instance bring-up: clone colibri @ `a78a06fc5acc4b0dc0f9ef03987c66b0559d1250`, verify + apply the gate-0 KaE patch (sha256-pinned), build, **assert 44/44 `test_kae` checks**, prove **inert-by-default** (per-function machine-code equivalence with `KAE` unset), and **document** (not execute) the model-fetch step. Fail-closed throughout. |
| `f1k_driver.py` | The run driver implementing the frozen protocol exactly: `--phase pilot` / `--phase guard` / `--phase test`, per-item checkpoint/resume, rows + sidecar in `analysis/f1k.py`'s exact schema, the `[R9-PROV]` carrier-construction provenance gate at ingest, `--mock` for the $0 end-to-end validation. Every frozen constant cites its source in-line. |
| `build_carriers.py` | The carrier-construction GENERATOR (sha-pinned in the frozen record): `manifest` ((A)-time, $0) → `construct --mode mock\|real` (96×16×3 = 4,608 forward passes; mode+sha-bound checkpoints; engine seed-echo verified, incl. on cached resume) → `verify --expect-mode mock\|real` (REQUIRED; never mode-blind) → `selftest` (22 probes: 21 fail-closed + 1 positive control). |
| `pilot.sh` | Pilot bring-up wrapper: preflight pins → `(L,g)` selection over the 4-member family-blind panel → affordability / power / placebo gates at pilot n → addenda (5)/(7) + (6)-inputs artifacts. |
| `mock_colibri.py` | Deterministic stub of the engine's `KAE_SCORE` path (exact interface; mock only). |
| `mock_colibri_dump.py` / `mock_tokenizer.py` | Deterministic stubs of the `kot-f1k-dump/1` hidden-state dump and `kot-f1k-tok/1` tokenizer contracts (construction seams; mock only, $0). |
| `mock_e2e_carriers.py` | $0 driver-acceptance proof: generator-built nc=96 / D=6144 tables through the untouched driver end-to-end; also proves the REAL-mode ingest gate REFUSES the same mock tables. |
| `mock-out/` | Regenerable mock outputs (not evidence; safe to delete). |

## Coordinator run sequence (the real run — every step coordinator-owned)

Ordering is the frozen §R-REV4.2 sequence; the test set stays untouched until
(A), (B0), (5), (7), (6) are ALL committed.

1. **Freeze-manifest (A) + corpus pins** — COMPLETE as of the freeze-(A)
   completion refreeze (2026-07-16): construction seed 20260716, d0 algorithm
   `kot-f1k-d0/1` (seed 7), the generator `build_carriers.py` sha-pinned, the
   (A)-time `construction-manifest.jsonl` committed, A(iv) splice layers
   RESOLVED + PINNED = **the 75 DRAFT=0-reachable MoE layers, engine ids 3..77 inclusive**
   (ASM-2504 amending ASM-2342/ASM-2406; pilot realization L1=[40], L2=[40,52,65,77], L3=all).
2. **Launch the spot i4i.2xlarge** (default for all GLM-5.2 runs;
   `docs/next/design/glm52-f1k-cost-reduction.md`).
3. **`bringup.sh`** (with `COLIBRI_GIT_URL` exported) — engine pinned, patch
   verified + applied, 44/44 unit checks, inert-by-default proven. Any
   failure aborts bring-up.
4. **Model fetch** (documented in `bringup.sh` step 6, not automated):
   stage the GLM-5.2 snapshot; **pin the weight content hash** →
   `f1k.json pins.model_revisions.glm52-weights` (PINNED-AT-INPUTS,
   ASM-1971); re-verify colibri knob semantics.
5. **Carrier construction + (B0)** — the frozen generator run
   (`build_carriers.py`, sha-pinned; §R-REV3.3): the runner implements the
   `kot-f1k-dump/1` construction-only engine patch and the `kot-f1k-tok/1`
   tokenizer wrapper at bring-up, then runs
   `construct --mode real --layers 3,...,77` with the three provenance shas
   **and the artifacts they derive from**
   (`--tokenizer-sha/--tokenizer-artifact`, `--engine-weights-sha/-artifact`,
   `--dump-patch-sha/-artifact` — each sha is re-DERIVED from the artifact
   bytes and compared; 96×16×3 = 4,608 forward passes EXACT), then
   `verify --expect-mode real`, and commits the realized tables +
   `norms.json` + `construction-report.json` as the pure-function addendum,
   completing `f1k-carriers-v1`. The engine must emit the
   `[KAE-DUMP] armed: ... seed=20260716` stderr echo (verified per batch AND
   on any cached-checkpoint resume).
6. **`pilot.sh --config run-config.json --outdir out/`** — produces
   `out/pilot/addendum-5-frozen-lg.json` (the frozen `(L,g)` the main run
   uses), `addendum-7-affordability.json` (measured s/prefill vs the $155
   ceiling, §R6 degradation order applied deterministically), and
   `addendum-6-inputs.json` (dev δ̂ upper-80, n at the cap, the dev
   cluster-difference distribution for the sign-symmetry check). Gates fail
   closed: power (EQUALITY form — exactly C = 96 clusters, each m ≥ 8,
   n = 1,573; ASM-2369), placebo (any-magnitude, ASM-2273), affordability
   ($155, ASM-2374). Pilot ≤ 2,112 prefills deterministic.
7. **Coordinator review + commits**: addenda (5)/(7), then the (6) power
   freeze including the dev-selected `inference.{method,
   dev_sign_symmetry_pass}` (§R-REV4.1a — the driver reports the dev data
   verbatim and never decides the method itself). These enter
   `run-config.json` (`frozen_lg`, `inference`, `freeze.manifest_flags`),
   plus the `carrier_provenance` block naming the pinned
   tokenizer/engine-weights/dump-patch artifact files (the `[R9-PROV]` gate
   DERIVES their sha256s and compares them to the construction-report
   binding — bare 64-hex assertions are never accepted).
   **The coordinator reviews this driver against the frozen protocol here,
   before any test prefill.**
8. **`f1k_driver.py --config run-config.json --phase guard --outdir out/`**
   — 60-item off-concept byte-identity guard (XCACHE forced off both
   directions, ASM-2306); any mismatch VOIDS.
9. **`f1k_driver.py --config run-config.json --phase test --outdir out/`**
   — the main campaign, 8 passes × 1,573 items (b0, d0, d1-drng ×3, d2,
   d3-text, K; REPLACE conditional on its §R-REV4.3 NI gate), one
   candidate-independent label-logit prefill per unit, per-item checkpoint
   (a spot interruption just resumes: re-run the same command). Every phase
   first re-runs the input seams: corpus pins, id-list hashes, AND the
   `[R9-PROV]` carrier-construction provenance gate (construction-report
   mode == real, D == 6144, layers == 3..77, seed == 20260716, bindings
   artifact-derived, every configured table byte-witnessed). Emits
   `out/test/rows.jsonl`, `out/test/sidecar.json`,
   `out/test/run-record.jsonl` (with the `pins_observed` carrier witness),
   `out/carrier-provenance.json`.
10. **Collection + verdict**: the coordinator collects the artifacts;
    log-append + verdict-gen pipe the eligible run records to the **pinned**
    `analysis/f1k.py` on stdin (the driver never grades; run-vs-analysis
    separation).

`run-config.json` schema: see the generated example at
`mock-out/fixtures/mock-config.json` (same keys; a real config points
`engine.argv` at the patched colibri binary + snapshot args, carries the
coordinator-committed freeze/inference blocks, and adds the
`carrier_provenance` artifact paths).

## $155 accounting (REVISION-6 / ASM-2374, freeze-(A) completion figures)

Worst case at the ASM-2205 pessimistic corner (100 s/prefill ÷ 1.20
expert-pinning lever × $0.28/h spot i4i.2xlarge), recomputed fail-closed by
the driver at every config load (`worst_case_usd`):

| Stage | Prefills (registered envelope) |
|---|---|
| Main arms (b0, d0, d1-drng ×3, d2, d3-text, K) | 8 × 1,573 = **12,584** |
| Carrier construction (`build_carriers.py`) | **4,608 EXACT** (96×16×3; WITHOUT shared between K and d2 — supersedes the 3,072 under-count) |
| Pilot (9 configs × 4 panel × 48 dev + dev-96 post-freeze + conditional dev REPLACE) | **≤ 2,112 deterministic** |
| Off-concept guard | **≤ 660** |
| **Mandatory total** | **19,964 → 462.1 h → $129.40 ≤ $155** |
| + conditional REPLACE arm | +1,573 → 498.5 h → **$139.59 ≤ $155** |

REPLACE runs ONLY if its §R-REV4.3 NI gate says RUN (n_NI =
δ_R·DEFF/SE_NI² ≤ 1,573, i.e. dev δ_R ≲ 0.0397 at the REVISION-6 geometry)
AND the bring-up-MEASURED addendum-(7) projection keeps the ledger ≤ $155
(ASM-2374 — never a silent cap raise); else DEFERRED (its registered modal
expectation). The cap is enforced three ways: at config load (recomputed
worst case), at every ledger accumulation, and again at sidecar emission;
the pinned analysis additionally enforces budget-honesty scale floors (an
under-reported ledger never validates). EC2 instance compute only;
storage/tax/transfer separately accounted.

Spot interruption safety: per-item checkpoint (`rows.jsonl` is the resume
state, torn-tail tolerant); re-invoking the same phase resumes. Expert
pinning is ENFORCED (`PIN=<bring-up stats-file>` validated + content-
hashed + engine-arming-verified [ASM-2513] + positive `PIN_GB`, recorded in ledger +
sidecar — the 1.20× lever the ceiling prices; ASM-2205/ASM-2374). The guard
**always** runs cache-off (ASM-2306).

## Frozen-protocol value audit (driver ↔ source)

Every constant in `f1k_driver.py` cites its source in-line; this table is
the coordinator's driver-vs-protocol audit map. **No invented thresholds.**

| Driver constant | Value | Frozen source |
|---|---|---|
| `ARMS_MAIN` | b0, d0, d1-drng, d2, d3-text, K | `f1k.json` `design.independent_vars.arm`, `arms_mandatory_baselines` |
| REPLACE | conditional on the frozen NI gate | §R-REV4.3/ASM-2124: n_NI ≤ 1,573 (dev δ_R ≲ 0.0397 at REVISION-6 geometry); gate-0 patch stubs REPLACE (`kae.h kae_replace_note`) |
| `R_DRNG` / `DRNG_SEEDS` | 3 / [101, 102, 103] | `f1k.json` `design.seeds`; §R6 step 1 pre-applied (ASM-2272); `analysis/f1k.py` `DRNG_SEEDS` |
| `N_TEST` | **1,573** | `f1k.json` `design.n_planned` (REVISION-6, ASM-2369; runs AT the cap); `analysis/f1k.py` `N_REGISTERED` |
| `C_REGISTERED` / power gate | **96**, EQUALITY form: n_clusters == 96 AND each m ≥ 8 AND n == 1,573 | `f1k.json` `design.n_planned.power_gate` (ASM-2369; RUN-HOLD equality fix) |
| `DEV_N` / `GUARD_N` | 96 / 60 | `f1k.json` `design.n_planned.dev_split_items` / `off_concept_guard_items` |
| Splice layers (A(iv)) | **3..77 inclusive** (the 75 DRAFT=0 MoE layers); pilot L1=[40], L2=[40,52,65,77], L3=all | freeze-(A) A(iv) resolution [ASM-2504 amending ASM-2342/ASM-2406]; `build_carriers.py REGISTERED_SPLICE_LAYERS`; driver `[R9-PROV]` gate |
| Construction | seed 20260716; 4,608 passes EXACT; d0 = `kot-f1k-d0/1` seed 7; kdrng seed 11 | `f1k.json` freeze_manifest A(vii) + freeze-(A) completion riders |
| Scorer | ONE prefill/item/arm; argmax over K label-token logits; lowest-index tie-break | §R1.1 / `f1k.json` dependent_vars.item_correct; engine `run_kae_score` via `KAE_SCORE` |
| Template identity | byte-identical across arms except d3-text (prompt text, no splice); spans frozen per item | §R1.1/§R-REV2.1; §2.6 arm d3-text |
| Pilot grid / subset | 3 layer sets × 3 g-multipliers on 48-item stratified dev ((A)-committed id list) | `f1k.json` `design.n_planned.pilot`; §2.3 |
| Panel + blindness | 4 members {K-true, K-drng seed 11, d2, d0 seed 7}; equal FAMILY-level weight; tie-break fewer layers → lower g | §R-REV2.3/§R-REV3.2 (ASM-2113); §R4; seeds: freeze-manifest A(vii) |
| Placebo gate | one-sided cluster sign-flip p < 0.05 at ANY magnitude | ASM-2273 (no +3 floor); §2.6 d0 row |
| Sign-flip mechanics | B=10,000, add-one, seed 20260713 + per-contrast sub-seeds | `analysis/f1k.py` `SEED/B` (ASM-2271) — driver mirrors it for the pilot alarm only; verdicts run exclusively in the pinned analysis |
| Power block | rho_U = 0.10, mu* = 4.09 pts, N_sim = 10,000, per-rung joint power {0.8043, 0.8058, 0.8001} EXACT + ASM-2376 intersection block | §R-REV5; ASM-2371/ASM-2376 (pinned EXACTLY, deviations fail closed) |
| `USD_CAP` / rate | **$155** / $0.28/h spot | `f1k.json` `budget.usd_cap` (ASM-2374); `glm52-f1k-cost-reduction.md` (ASM-2205 corner) |
| Degradation order | R 5→3 (pre-applied) → defer REPLACE → defer d3-text → STOP | §R6 |
| Guard rule | byte-identity vs b0; mismatch VOIDS; XCACHE off | §2.5; `f1k.json` kill_criterion_verbatim; expert-cache ASM-2306 |
| `CEILING_B0` | 0.95 (echoed, never moved) | §2.7; `analysis/f1k.py` `CEILING_B0` (immutable) |
| Inference block | `{method: signflip\|bca, dev_sign_symmetry_pass}` coordinator-committed at addendum (6) | §R-REV4.1a; coherence enforced fail-closed by the analysis |
| Carrier provenance gate | construction-report mode=real, D=6144, layers 3..77, seed 20260716; bindings artifact-DERIVED; tables byte-witnessed; witness pins on the run record | carrier re-review item 8 (2026-07-16); `[R9-PROV]` in `f1k_driver.py`; `build_carriers.py` binding (carrier-HOLD fix 1) |
| Carrier CONTENT authentication | real bindings denylisted vs repo mock-stack digests (a real report can never be satisfied by a mock table; mock verify = testing scope only, never the production dir); full-coverage non-degeneracy per (c,l) cell (all-zero/near-constant/min-variance bodies refused; floors 1e-3 std/rms, 1/1024 nonzero); per-concept checkpoint `content_sha256` (exact f64 bytes, slot/layers/D-bound) re-derived on every resume + witnessed in the report | carrier re-review round-10 (2026-07-16); `[R10-1/2/3]` in `f1k_driver.py` + `build_carriers.py` |
| Campaign resume auth | `rows.jsonl.auth.json`: running content hash (`kot-f1k-rows-auth/1`) over the exact row lines + binding to {K table, construction report, engine files, eval manifest, phase}; foreign/tampered/unauthenticated resume refused; uncovered tails dropped + re-scored | carrier re-review round-10 gap 4 (2026-07-16); `[R10-4]` in `f1k_driver.py` (pilot, guard, test) |
| Rows/sidecar schema | exact `analysis/f1k.py` input contract | `analysis/f1k.py` docstring "ROWS (JSONL)" / "SIDECAR" |
| Engine pins | colibri `a78a06fc…d1250`; patch sha `11f8b458…d9cb` | `f1k.json` `pins.model_revisions` / `pins.harness_manifest` |

## Mock validation record ($0)

- **Driver `--mock`** (2026-07-13, re-run at every hardening pass since,
  latest 2026-07-16): the ENTIRE wiring against the deterministic stub —
  pilot ((L,g) selection + gates + addenda) → KaE fail-closed probe → guard
  (60 × spliced passes byte-identical to b0) → test campaign (12,584+ units
  with a FORCED interruption and per-item-checkpoint resume, no duplicates)
  → sidecar → run-record (with `pins_observed`) → the OFFICIAL sandboxed
  log-append → verdict-gen → **pinned `analysis/f1k.py` ingest: exit 0**,
  all gates true, plus the fail-closed probe batteries ([R3-ATTEST]/
  [R3-POWER]/[R3-COST]/[R3-SEAM]/[R9-PROV]/[R10-1/2/3]/[R10-4]: incl.
  ALL-ZERO real tables refused, relabeled-mock bindings refused, missing
  checkpoint-content witness refused, and the resume-auth battery —
  tampered/unauthenticated/foreign rows refused, injected rows dropped).
  The stub plants a +10-pt K lift, so the mock reaches the full
  PASS-shaped verdict surface — demonstrating the machinery, **not** a
  result.
- **Generator + driver acceptance** (`mock_e2e_carriers.py`): tables built
  by the REAL generator (mock dump engine, nc=96 / D=6144) accepted by the
  untouched driver end-to-end under mock disclosure, AND **refused** by the
  REAL-mode ingest gate (the re-review item-8 exploit, proven closed).
- **Generator `selftest`**: 22 probes (mode-bound checkpoints,
  A(iv) enforcement, manifest fresh-derivation, engine echo fresh + cached,
  artifact-derived shas, cached-content integrity, mode-blind verify
  refused; round-10: replaced-vector/hashless/all-zero checkpoints
  rejected, relabeled-mock-under-real rejected, real-claiming-under-mock
  rejected, production-dir mock construct/verify refused, all-zero table
  set rejected by verify non-degeneracy; r3 dump-re-review finding 4:
  NaN-sum KAED and gated_count-vs-manifest-mismatch KAED each rejected
  consumer-side in `run_dump`, plus an uncorrupted-dump positive control
  proving no over-rejection).

## Governance self-check (this pass)

- engine referred to as **colibri** only; no author handle in any file
- NO git action, NO registry write, NO model download, NO instance launch,
  NO spend ($0); the mock stubs are the only things executed
- no new ASM entries claimed; no DERIVED tag used anywhere
- every frozen-protocol constant cites `f1k.json` / a design section
  (table above); the driver never grades — verdicts belong to the pinned
  `analysis/f1k.py` via verdict-gen
- REPLACE deferred unless its frozen NI gate + the measured (7) projection
  both license it (deferral is the registered modal expectation)
