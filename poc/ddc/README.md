# poc/ddc — DDC (kernel-guided dimension collapse) run harness

Harness for the two DRAFT pre-registrations
`registry/experiments/ddc0.json` (G0 statistics stage) and
`registry/experiments/ddc1.json` (the Δ\* arm campaign), implementing
`docs/next/design/DDC.md` (ASM-1650..1667, 1700..1706, 1720; build rows
emitted as `poc/ddc/asm-1750-1769.json`). **Freeze-before-run**: the
coordinator freezes both records before any final-phase launch. This
tree states NO feasibility conclusion; every mock number is SYNTHETIC
mechanics validation.

## Layout

| file | role |
|---|---|
| `inputs/ddc-manifest.json` | pinned design constants (grid, coverage, budgets, cost model, gates); staged + covered by the harness sha |
| `ddc_surgery.py` | the ONLY weights-touching module (SliceGPT rotate-and-slice, bridges, tied embedding; M1/M2 magnitude controls; gate I-1). **LAW-1 isolated**: kernel-blind, guarded by `assert_basis_provenance` (ERR_DDC_LAW1_TAINT) |
| `ddc_selection.py` | basis SELECTION (uncentred activation PCA per ASM-1665, Haar R1, §2.3 A2 assembly incl. ERR_DDC_BASIS_DEFICIENT, energy capture) |
| `g0_stats.py` | ddc0 §2.3 mathematics (ridge-CCA + Procrustes, joint max-stat family B=1000 seed 1, admission raw stats); numpy-only, locally testable |
| `g0_runner.py` | ddc0 stage runner: `--stage probe` (GPU) / `--stage stats` (CPU, checkpointed) / `--mock` / `--dry-plan` |
| `ddc_runner.py` | ddc1 cell runner (surgery + pubeval eval with per-item emission) + monolithic finaliser; `--mock` / `--dry-plan --tier ...` |
| `ddc_common.py` | job plan, expected grid, fail-closed dry-plan, shared `finalize()` (monolithic == merged by construction) |
| `merge_shards.py` | fail-closed shard merge (identical pins/t0-block, disjoint cells, unique rows, EXACT ASM-1654 coverage) |
| `modal/modal_ddc.py` | Modal wrapper (pinned f2b image 0fac7243…, NO new deps): `--print-manifest`, `--print-jobs`, `--dry-plan`, `--mock`, `--tier`, `--jobs`, launch gates |
| `validate_mock.py` | $0 green-mock validator → `results/mock-validation.json` (launch gate 3) |
| `power_sim_ddc1.py` | gate I-5 v3 power simulation (ASM-1720; pinned in the ddc1 record) |

## $0 validation (this build's status: ALL GREEN)

```bash
python3 poc/ddc/validate_mock.py
```

pins `results/mock-validation.json`: ddc0 + ddc1 verdict mappings resolve
on planted mock gradients; monolithic == sharded+merged (66 canonical
jobs) pinned-analysis parity modulo the disclosed measured cost fields;
LAW-1 static + runtime assertions; g0_stats planted-alignment self-test;
per-tier dry-plans green (t0 $2.63 / ddc0 $2.52+1.2 GPU-h / s1 $26.42 /
s2 $24.98; campaign $56.55 < $60 ceiling; worst job 3.83 h < 12 h).
`prereg-freeze --dry-run` re-confirmed DRY-RUN-OK for BOTH records after
the harness_manifest pins landed (PAUSE flags ASM-1662/1706 by design).

## Parallel job plan

t0 = 1 job · ddc0 = 2 sequential jobs (GPU probe → CPU stats) ·
s1 = 46 jobs · s2 = 19 jobs (conditional, `--authorize-s2`). Split across
workspaces (env-file basenames modal2/modal3/modal4 — ASM-1664) with
`--jobs tag1,tag2,…`; see `--print-jobs --tier <t>`. Merge ALL collected
shard dirs across tiers once the grid is complete:

```bash
python3 poc/ddc/merge_shards.py --out-dir <merged> <shard dirs...>
python3 analysis/ddc1.py --items <merged>/items-ddc1.jsonl \
    --cells <merged>/cells-ddc1.json --sidecar <merged>/sidecar-ddc1.json
```

## Remaining T0 (ops/runner identity — before freeze-for-launch)

1. Build + pin the corpora under `data/` (K-static ASM-1651, K-hybrid,
   C4 sample, knull render, shuffled kernel, probe fixture with the
   documented schema in `g0_runner.py`, det_u eval subset) via
   `tools/registry/corpus-pin.py`; fill `inputs/ddc-manifest.json` shas.
2. Pin the BASE donor revisions (manifest + pubeval `MODEL_REGISTRY`
   `smollm2-*-base` entries — currently fail closed by design).
3. Run A0 baselines (t0 tier) → informative-task filter; run
   `power_sim_ddc1.py` on the measured pool (never `--quick`); re-verify
   licenses; assemble `inputs/t0-block.json` (schema:
   `ddc_common.mock_t0_block`).
4. Re-run `validate_mock.py` (staging corpora changes the staged sha) and
   re-pin `pins.harness_manifest` in both records; re-run
   `prereg-freeze --dry-run`; then the coordinator freezes and launches
   tier by tier (t0 → ddc0 → freeze ddc1 → s1 → s2-on-promotion).

Known v1 harness limits (disclosed, beads-tracked): R1/M2 cells log
`energy_capture: null` pending census wiring (PROPOSED-ASM-1757); the
§5.3 kernel-distribution diagnostic suites are not yet wired into the
cell jobs; ddc0 stats-stage runtime is a projection (checkpointed,
resumable, CPU-container) to be measured at T0.
