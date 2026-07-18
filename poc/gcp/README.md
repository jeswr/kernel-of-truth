# F1-K on GCP Spot — Opus-runner orchestration harness

> **Provision-ready + bring-up-capable.** This directory is the GCP-Spot
> orchestration layer for the **frozen** F1-K correctness run
> (`registry/experiments/f1k.json`, `frozen_sha256 35372275…`). It DESIGNS
> nothing and CONCLUDES nothing: the kernel, model, engine, carriers, protocol,
> and analysis are frozen upstream (Fable). This layer only provisions, stages,
> builds, drives the pinned generator/driver, checkpoints, monitors, and tears
> down — from the frozen RunSpec, fail-closed on any pin mismatch.
>
> Compute target (bead **pzb6** resolution): GCP **Spot** `n2d-highmem-8`
> (8 vCPU / 64 GB) + **2×375 GiB local SSD** (750 GiB NVMe), zone
> `us-central1-a`. **`--provisioning-model=SPOT` is MANDATORY** — on-demand
> (~$0.579/h) busts the $155 ceiling and fails the pinned analysis.

## Why GCP Spot (and not Modal)

The pinned analysis `analysis/f1k.py` (sha `126129b9`) hard-enforces a ledger
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
| `f1k_gcp.py` | Control-box orchestrator: `plan` is the $0 pin/reuse/SPOT/disk/window check; `provision` creates the **single SPOT VM only** (explicitly refuses `KOT_F1K_ONDEMAND`), grants the `cloud-platform` OAuth scope, and arms the guest max-life from the startup script; `bringup-deploy` RAID0-mounts `/mnt/nvme`, stages the worker files flat in `~/f1k` (including `f1k_ops.py`) plus the reviewed construction payload under `~/f1k/poc/...`, launches the worker, and re-arms max-life. Also provides `status`, `teardown`, box-side `watchdog --max-hours H`, the mechanical `gate`, `pin-fetch`, and the non-licensing `affordability` diagnostic. There is no landed `construction-continue` entrypoint yet. |
| `f1k_bringup_gate.py` | The FIXED bring-up gate machinery (`F1K-BRINGUP-GATE-FIX.md` v1+REV-B+REV-C, GAP-1/2/3): frozen deterministic stratified real-corpus sampling rule, full-corpus tokenization (measured f, per-item T), per-item-manifest bring-up pin derivation (fail-closed merge + provenance), per-item token-aware ledger projection + GREEN/STOP **`/2` model-bundle-bound** artifact (engagement-verified, unpinned refused), `checkpoint` = frozen-schedule construction early-abort re-projection, `guard` = **construction wrapper** (explicit pin env + dump-mode engagement probe + in-process checkpoints + kill-on-breach; the sha-pinned builder stays untouched), `config-affordability`/`config-cost` = executable gate→campaign-config seams; `selftest` = $0 mock oracle of the LOGIC seams only (no real engine/tokenizer/GCS/VM — honest scope printed). |
| `bringup_gcp.sh` | KaE bring-up on the VM: colibri@`a78a06fc` + KaE patch (`11f8b458`), build, 44/44 `test_kae`; objdump patch-shape checks (clone-aware, reference + native flags) are **ADVISORY-ONLY on the VM** (bead f2uk / ASM-2503: gcc-version-brittle even at `-O2 -march=x86-64-v3`; fail-closed objdump lives off-box on the gcc-11.5 basis; the frozen `bringup.sh` is untouched). The AUTHORITATIVE inertness proof is the functional KAE-unset byte-identity gate in `f1k_worker.sh`. |
| `f1k_worker.sh` | On-VM autonomous worker: STAGE estate → BUILD scoring + construction engines → KaE + automated dump gate (b) → scaffold dump (a)/(c) → real-corpus tokenization and **preemption-safe per-sample timing** (temp+fsync+atomic rename; complete/same-boot validation; T1 unpinned → bring-up pin → T2 pinned) → `~/f1k-gate/gate-inputs.json` → **STOP before construction spend**. After the runner records literal `PASS` for dump (a)/(c) and re-runs `collect` without re-timing, `bash f1k_worker.sh --finalize-ready` emits `~/f1k-gate/construction-ready.json`, binding the live SPOT instance/boot, complete timing set, pin, payload, pinned builder `a92be3e4`, engine/tokenizer/artifact hashes and argv, and the real `~/f1k`/`/mnt/nvme`/`~/f1k-gate` launch paths with no undefined placeholders. |

## Run sequence — LANDED Single-VM-Spot "B" bring-up

Bring-up runs on Spot, and the same instance is retained through the mechanical
GREEN verdict and the forthcoming handoff to the guard. Do not tear it down and
do not provision a fresh construction VM.

0. On the control box, load GCP configuration, set the same-region estate bucket,
   coordinator clone URL, and the **current full construction Spot rate** for
   `n2d-highmem-8` plus 2 local SSDs in `us-central1`, then run the $0 plan:

   ```bash
   source ~/.config/kot/gcp.env
   export KOT_F1K_BUCKET=gs://kot-f1k-estate-85e2ca29
   export COLIBRI_GIT_URL=<coordinator>
   export KOT_F1K_SPOT_RATE=<current-construction-Spot-USD-per-hour>
   python3 poc/gcp/f1k_gcp.py plan
   ```

1. Provision the one B instance:

   ```bash
   python3 poc/gcp/f1k_gcp.py provision
   ```

   This path is SPOT-only: `KOT_F1K_ONDEMAND` is refused. Provision uses
   `--scopes cloud-platform` (an OAuth ceiling, not an IAM grant) and installs a
   startup script that arms `KOT_F1K_GUEST_MAXLIFE_MIN` (default 900 minutes).
   The VM remains the construction VM after GREEN.

2. Stage and launch bring-up, then arm the independent control-box watchdog:

   ```bash
   python3 poc/gcp/f1k_gcp.py bringup-deploy
   nohup python3 poc/gcp/f1k_gcp.py watchdog --max-hours <H> \
     > watchdog.log 2>&1 &
   pgrep -f 'f1k_gcp.py watchdog'
   ```

   `bringup-deploy` mounts the two local SSDs as `/mnt/nvme`; puts the worker
   bundle flat in `~/f1k` (including `f1k_ops.py`); adds the full reviewed
   construction/campaign subset under `~/f1k/poc/...` and its repo-relative
   dependency paths (`build_carriers.py` sha `a92be3e4`, `f1k_driver.py`, data,
   registry, and tooling); then launches `f1k_launch.sh`. Verify the guest timer
   with `sudo shutdown --show` on the VM. Keep the box-side watchdog detached;
   it tears down on deadline or a worker FAILED marker.

3. The autonomous worker performs STAGE from the bucket (or populates the mirror),
   BUILD of both engines, KaE, automated dump precondition (b), and scaffolding of
   dump (a)/(c). It then tokenizes the real corpora and writes each timing result
   atomically under `~/f1k-gate/{t1,t2}-results/`: T1 is unpinned, the bring-up
   pin is derived, and T2 is pinned with per-run engagement evidence. Complete-set
   and same-boot checks make preemption fail closed. The worker writes the initial
   `~/f1k-gate/gate-inputs.json` and **stops before construction spend**.

4. On the retained VM, the runner validates dump (a) and (c), writes literal
   `PASS`, re-runs only `collect`, and finalizes the launch manifest:

   ```bash
   export KOT_F1K_SPOT_RATE=<same-decimal-used-in-step-0>
   GATE="$HOME/f1k-gate"
   PIN_FILE="$GATE/pin_bringup.stats"
   PIN_SHA="$(sha256sum "$PIN_FILE" | awk '{print $1}')"
   PIN_GB="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["pin"]["pin_gb"])' "$GATE/gate-inputs.json")"

   printf 'PASS\n' > "$GATE/tiny-dump.status"
   printf 'PASS\n' > "$GATE/moe-sum-crosscheck.status"

   python3 "$HOME/f1k/f1k_bringup_gate.py" collect \
     --sample "$GATE/gate-sample/timing-sample.json" \
     --tokens "$GATE/gate-tokens" \
     --t2 "$GATE/t2-results" --t1 "$GATE/t1-results" \
     --rate "$KOT_F1K_SPOT_RATE" \
     --pin-sha "$PIN_SHA" --pin-gb "$PIN_GB" \
     --pin-regime pinned-bringup --pin-path "$PIN_FILE" \
     --pin-derivation "$PIN_FILE.derivation.json" \
     --dump-a "$(cat "$GATE/tiny-dump.status")" \
     --dump-b "$(cat "$GATE/dump-b.status")" \
     --dump-c "$(cat "$GATE/moe-sum-crosscheck.status")" \
     --functional "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["verdict"])' "$GATE/functional-inertness.json")" \
     --out "$GATE/gate-inputs.json"

   cd "$HOME/f1k"
   bash f1k_worker.sh --finalize-ready
   test -s "$HOME/f1k-gate/construction-ready.json"
   ```

   `collect` consumes the existing atomic T1/T2 files; it does not re-time. The
   finalizer refuses incomplete, cross-boot, stale, non-PASS, drifted, symlinked,
   or placeholder-bearing launch state. Pull the whole gate directory only after
   `construction-ready.json` exists:

   ```bash
   # control box
   mkdir -p ./gate-pull
   gcloud compute scp --recurse \
     "${KOT_F1K_VM:-kot-f1k-run}:~/f1k-gate" ./gate-pull/ \
     --zone "${KOT_GCP_ZONE:-us-central1-a}" --project "$KOT_GCP_PROJECT"
   ```

5. On the control box, emit the mechanical verdict from the final pulled inputs:

   ```bash
   python3 poc/gcp/f1k_gcp.py gate \
     --inputs ./gate-pull/f1k-gate/gate-inputs.json \
     --out ./gate-pull/bringup-gate.json
   ```

   **GREEN** is the standing authorization to continue on this same instance,
   without re-surfacing, within the controlling $155 campaign-compute cap and
   the $300 total-GCP envelope. Keep the VM alive; GREEN does not bypass the
   construction-side readiness gate below. **STOP** exits nonzero: surface
   `bringup-gate.json` with its breach values and spend no construction dollars.

6. **FORTHCOMING — CONSTRUCTION-SIDE, NOT LANDED:** `construction-continue` will
   bind the same-instance GREEN handoff to the already-landed guard under
   `systemd`; add guard-side live-license/identity/rate re-verification; install
   a provider-side 900-hour wall-clock hard-delete; and enforce live-rate
   checkpoints. The guard remains the sole construction launcher. This unit
   must be built, reviewed, and Fable-cross-reviewed before the first
   construction dollar; there is no runnable `construction-continue` command in
   the current `f1k_gcp.py` entry map.

The landed $0 oracle baseline for this B bring-up side is:

```bash
python3 poc/gcp/f1k_gcp.py bringup-deploy --selftest  # 11/11
bash poc/gcp/f1k_worker.sh --selftest                 # 14/14
python3 poc/gcp/f1k_gcp.py gate --selftest            # 69/69
python3 poc/gcp/f1k_ops.py selftest                    # 23/23
```

## Honest scope (preserve — do not "fix")

Per-rung power ≥0.80 but the 3-rung full-PASS intersection ~0.62 → a 2-of-3
**INCONCLUSIVE** outcome (~38–48% expected) is a **pre-registered possibility,
NOT a retry trigger**. Any PASS is **PROXY-PROVISIONAL** (agent-authored
explications, human-unvalidated; ASM-2373). On any instrument-gate / degenerate
/ scientific failure → **SALVAGE+STOP, never retry the science**; infra
failures (spot preemption, disk, OOM) resume from checkpoint. Teardown deletes
the VM + local SSD so nothing bills idle.
