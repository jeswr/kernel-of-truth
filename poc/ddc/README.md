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

## $0 validation (T0-ops re-validation 2026-07-12: ALL GREEN)

```bash
python3 poc/ddc/validate_mock.py
```

pins `results/mock-validation.json`: ddc0 + ddc1 verdict mappings resolve
on planted mock gradients; monolithic == sharded+merged (66 canonical
jobs) pinned-analysis parity modulo the disclosed measured cost fields;
LAW-1 static + runtime assertions; g0_stats planted-alignment self-test;
per-tier dry-plans green (t0 $2.63/2.4 GPU-h / ddc0 $2.52+1.2 GPU-h /
s1 $26.43 / s2 $24.98; campaign $56.56 < $60 ceiling; worst job
3.83 h < 12 h). `prereg-freeze --dry-run` re-confirmed DRY-RUN-OK for
BOTH records after the T0 pins landed (PAUSE flags ASM-1662/1706 by
design). Staged-bytes sha (pinned in both records' `harness_manifest` and
the green-mock artifact):
`c03ae3ea7dba042ecaeb03421fb737d6f41abd76ca88ae33c30b35e20b57d6a1`.

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

## T0 ops status (2026-07-12) + coordinator launch sequence

DONE by the T0 build (builders in `poc/ddc/t0/`; T0 stipulations emitted
as PROPOSED-ASM-1790..1799, `poc/ddc/asm-1790-1799.json`):

1. ✔ Seven corpora built + pinned (kot-corpus-hash/1 digests filled in
   `inputs/ddc-manifest.json` AND both DRAFT records): K-static (4096
   seqs, 482,501 donor tokens), K-hybrid (2048 K-static + 2048
   twin-engine-closure seqs), C4 sample (first-4096-rows rule, per-doc
   cap 131 tokens), knull render (108 defs cycled ~112x — MD-5), shuffled
   kernel, probe fixture (119 committed paired concepts + 30 synthetic
   minimal-contrast pairs, determinism-checked), det_u eval subset
   (500/task; folio = full 204). Gate I-3 parity table GREEN:
   `poc/ddc/t0/i3-token-parity.json`.
2. ✔ BASE donor revisions pinned (manifest + pubeval MODEL_REGISTRY +
   records; ERR_UNPINNED_MODEL cleared): 135M @ 93efa2f0…, 360M @
   f8027fd0…; configs re-verified at the pinned revisions. FOLIO bytes
   pinned from the Yale-LILY GitHub v0.0 release (204/1004 rows; the HF
   mirror is gated) — `poc/pubeval/fetch_data.py`.
3. ✔ `validate_mock.py` re-run green; `pins.harness_manifest` re-pinned
   in both records to the new staged sha; `prereg-freeze --dry-run`
   DRY-RUN-OK for ddc0 AND ddc1.

REMAINING (coordinator / runner identity — GPU + freeze, in this order):

```bash
# 1. t0 tier (~$2.63 / 2.4 GPU-h; NO freeze gate on t0):
.venv/bin/modal run poc/ddc/modal/modal_ddc.py --tier t0
# 2. measured pool + gate I-5 v3 power sim (CPU ~1 h; NEVER --quick):
python3 poc/ddc/t0/assemble_t0_block.py --a0-shard <collected-t0-dir> \
    --pool-out poc/ddc/t0/t0-pool.json --pool-only   # prints the pinned
nice -n 10 python3 poc/ddc/power_sim_ddc1.py --pool poc/ddc/t0/t0-pool.json \
    --out poc/ddc/t0/power-sim-result.json \
    --campaigns 2000 --bootstrap 10000 --seed 20260712
# 3. freeze ddc0 (record already pinned to the staged sha) and run G0:
python3 tools/registry/prereg-freeze.py --experiment ddc0 --agent-id <id>
.venv/bin/modal run poc/ddc/modal/modal_ddc.py --tier ddc0
python3 analysis/ddc0.py --candidates ... --maxstat-null ... --sidecar ... \
    > ddc0-analysis.json   # then verdict-gen (mechanical)
# 4. assemble the campaign t0-block (re-verify licenses first, I-4):
python3 poc/ddc/t0/assemble_t0_block.py --a0-shard <collected-t0-dir> \
    --power-result poc/ddc/t0/power-sim-result.json \
    --ddc0-analysis ddc0-analysis.json --licenses-verified \
    --out poc/ddc/inputs/t0-block.json
#    (+ stage inputs/ddc0-analysis.json + inputs/a2-directions-ddc0.json
#     if G0 passed — the A2 jobs read them)
# 5. inputs/ changed => re-run validate_mock.py, re-pin harness_manifest
#    in ddc1 (correction-free: still DRAFT), prereg-freeze ddc1, launch:
python3 poc/ddc/validate_mock.py
python3 tools/registry/prereg-freeze.py --experiment ddc1 --agent-id <id>
.venv/bin/modal run poc/ddc/modal/modal_ddc.py --tier s1
#    s2 only on the section-8 promotion rule: --tier s2 --authorize-s2
```

Known v1 harness limits (disclosed, beads-tracked): R1/M2 cells log
`energy_capture: null` pending census wiring (PROPOSED-ASM-1757); the
§5.3 kernel-distribution diagnostic suites are not yet wired into the
cell jobs; ddc0 stats-stage runtime is a projection (checkpointed,
resumable, CPU-container) to be measured at T0.
