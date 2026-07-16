# F1-K on GCP Spot — Opus-runner orchestration harness

> **Provision-ready + bring-up-capable.** This directory is the GCP-Spot
> orchestration layer for the **frozen** F1-K correctness run
> (`registry/experiments/f1k.json`, `frozen_sha256 505165ee…`). It DESIGNS
> nothing and CONCLUDES nothing: the kernel, model, engine, carriers, protocol,
> and analysis are frozen upstream (Fable). This layer only provisions, stages,
> builds, drives the pinned generator/driver, checkpoints, monitors, and tears
> down — from the frozen RunSpec, fail-closed on any pin mismatch.
>
> Compute target (bead **pzb6** resolution): GCP **Spot** `n2d-highmem-8`
> (8 vCPU / 64 GB) + **3×375 GiB local SSD** (1,125 GiB NVMe), zone
> `us-central1-a`. **`--provisioning-model=SPOT` is MANDATORY** — on-demand
> (~$0.579/h) busts the $155 ceiling and fails the pinned analysis.

## Why GCP Spot (and not Modal)

The pinned analysis `analysis/f1k.py` (sha `54924cfd`) hard-enforces a ledger
window: `instance_hours ∈ [260.6, 900] h`, `usd_total ∈ [$73, $155]`,
`usd_total ≈ usd_spent_prior + run_hours·rate` (±$0.01), `prefills ≥ 11,011`.
So the admissible **effective** rate is `[73/900, 155/260.6] = [$0.081,
$0.595]/h`. Modal ($1.15/h) has an **empty** window (`155/1.15 = 134.8 h <
260.6`) → certain no-verdict (bead pzb6). GCP Spot ~$0.19–0.24/h is in-window
with a **non-empty** valid `instance_hours` window.

## AFFORDABILITY — the FLOOR exposure (read before spending)

A spot rate **below $0.28/h** makes the **$73 `usd_total` floor** the binding
lower constraint (`usd_total ≥ 73` needs `instance_hours ≥ 73/rate > 260.6`).
Admissible **blended s/prefill** band for the 19,964-prefill mandatory campaign:

| rate | admissible instance_h | admissible blended s/prefill | corner ref |
|---|---|---|---|
| $0.19 | [384.2, 815.8] | [69.3, 147.1] | 83.3 |
| $0.20 | [365.0, 775.0] | [65.8, 139.8] | 83.3 |
| $0.24 | [304.2, 645.8] | [54.8, 116.5] | 83.3 |
| $0.28 | [260.7, 553.6] | [47.0, 99.8] | 83.3 |

The ASM-2205 pessimistic **corner** blended throughput (83.3 s/prefill) is
**inside** the band at every quoted rate → at corner throughput the ledger
validates. The run **STOPS fail-closed** at the affordability gate ONLY if the
REAL box measures blended s/prefill **below** the floor (65.8–69.3 s at
$0.19–0.20/h) — i.e. **>~1.2–1.27× faster** than the corner. Prior repo
GLM-5.2 throughput (`poc/modal` stage3 plan) projected 16–35 s/prefill on
SHORT teacher-forced items (not directly comparable to f1k's full-QA +
d3-text-prepend scoring prefills). Cutting the other way: `n2d` is AMD EPYC
(no AVX-512) vs the Intel i4i.2xlarge the corner was calibrated on → plausibly
slower, clearing the floor. **This is MEASURED + gated at bring-up**
(`f1k_gcp.py affordability`), never silently overspent OR under-run. A
below-floor result is a cost-model-vs-rate **decision** (Fable/coordinator/
maintainer), **NOT a retry** — the pzb6 class discovered at bring-up.

## Files

| File | What it is |
|---|---|
| `f1k_gcp.py` | Orchestrator (runs on the control box): `plan` ($0 dry-plan: pins + reuse-gate + SPOT/disk/window asserts), `provision` (Spot VM + 3 local SSD), `status`, `teardown`, `affordability` (measured rate + s/prefill → frozen-window GO/SALVAGE-STOP). |
| `bringup_gcp.sh` | KaE bring-up on the VM: colibri@`a78a06fc` + KaE patch (`11f8b458`), build, 44/44 `test_kae`, clone-aware inert-by-default proof (the PATCH-NOTES OQ2 `<([\w.]+)>` fix, ported; the frozen `bringup.sh` is untouched). |
| `f1k_worker.sh` | On-VM autonomous worker: STAGE (GCS mirror → else HF → NVMe, weight-hash pin) → BUILD scoring + construction engines → KaE bring-up → dump bring-up gate (b) → scaffolds (a)+(c) + the affordability micro-benchmark → **STOP before construction spend**. Heartbeat + artifacts to GCS; idempotent (spot preemption re-runs, restages from GCS). |

## Run sequence (frozen §R-REV4.2 ordering; each paid step gated)

0. `source ~/.config/kot/gcp.env`; `python3 poc/gcp/f1k_gcp.py plan` ($0).
1. `provision` → **record the ACTUAL assigned spot $/h** (load-bearing for the
   affordability gate). Set `KOT_F1K_BUCKET=gs://…` (same-region estate mirror),
   `COLIBRI_GIT_URL` (coordinator-supplied), `KOT_F1K_SPOT_RATE=<measured>`.
2. RAID0 + mount the 3 local SSD at `/mnt/nvme`; scp `poc/gcp/`,
   `poc/glm52-probe/f1k-harness/`, `poc/glm52-probe/kae-patch-draft/`,
   `analysis/f1k.py` to the VM; launch `f1k_worker.sh` detached (systemd/nohup).
3. Worker STAGE + BUILD + KaE bring-up + **dump bring-up gate**:
   - (b) unarmed byte-identity + `test_kae` 44/44 + `test_kae_dump` 43/43 +
     objdump inertness — automated via `dump-patch/real-checks.sh`.
   - (a) tiny real dump + `kot-f1k-tok/1` token-id consistency — **runner
     confirms ON-BOX** (echo `seed=20260716`; tok ids == engine-prefilled ids).
   - (c) independent MoE-input sum cross-check on MIXED positions — **runner
     confirms ON-BOX** (a separate capture path, not `kae_dump.h`, cell-for-cell
     equal to the engine dump). Its correctness cannot be validated blind, so
     it is a runner-confirmed PASS. ANY precondition failure → SALVAGE+STOP.
4. **Affordability micro-benchmark**: ≥20 real `KAE_SCORE` prefills spanning
   short (b0) + long (d3-text) arms → mean blended s/prefill;
   `f1k_gcp.py affordability --rate <measured> --s-per-prefill <mean>` — **GO
   (exit 0) is the ONLY license for construction spend.**
5. **Construction** (gated on 3+4): `build_carriers.py construct --mode real
   --layers 3,…,78` with the three provenance shas **and their artifacts**
   (`--tokenizer-sha/-artifact`, `--engine-weights-sha/-artifact`,
   `--dump-patch-sha/-artifact`), 4,608 passes EXACT; `verify --expect-mode
   real` (full cell-by-cell re-derivation, the #46 guarantee); commit the
   realized tables + `norms.json` + `construction-report.json` = **B0**,
   completing `f1k-carriers-v1`. Pin `glm52-weights` (ASM-1971 ops amendment).
6. **Pilot** (`f1k_driver.py --phase pilot`): produces `addendum-5-frozen-lg`,
   `addendum-7-affordability`, `addendum-6-inputs` (dev δ̂, the dev
   sign-symmetry check). **HANDOFF**: the addendum-(6) inference method
   (`signflip` vs `bca`) and the REPLACE run/defer are **Fable/coordinator**
   commits — the driver reports the dev data verbatim and **never decides**.
   Do not proceed to the test phase until those blocks are committed into
   `run-config.json`.
7. **Guard** (`--phase guard`): 60-item off-concept byte-identity (cache off).
8. **Test** (`--phase test`): 8 passes × 1,573 (+conditional REPLACE), one
   label-logit prefill per unit, per-item checkpoint to GCS. Spot preemption:
   the VM STOPs (`--instance-termination-action STOP`); re-provision +
   re-stage from GCS + re-run the same phase (resume-safe, `[R10-4]` auth).
9. **Verdict + audit**: assemble the `kot-log/1` D10-paired record →
   `log-append` (`phase:"final"`) → `verdict-gen` (mechanical) →
   `analysis/f1k.py` → PASS-PENDING-AUDIT → **Codex Gate-A cross-vendor audit**
   → update `registry/audit-status.jsonl`
   (`executed_by:"opus"`, `fable_interpretive_assessed:"pending"`). NEVER
   conclude — interpretation is Fable's.

## Honest scope (preserve — do not "fix")

Per-rung power ≥0.80 but the 3-rung full-PASS intersection ~0.62 → a 2-of-3
**INCONCLUSIVE** outcome (~38–48% expected) is a **pre-registered possibility,
NOT a retry trigger**. Any PASS is **PROXY-PROVISIONAL** (agent-authored
explications, human-unvalidated; ASM-2373). On any instrument-gate / degenerate
/ scientific failure → **SALVAGE+STOP, never retry the science**; infra
failures (spot preemption, disk, OOM) resume from checkpoint. Teardown deletes
the VM + local SSD so nothing bills idle.
