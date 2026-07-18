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
| `f1k_gcp.py` | Orchestrator (runs on the control box): `plan` ($0 dry-plan: pins + reuse-gate + SPOT/disk/window asserts), `provision` (Spot VM + 2 local SSD), `status`, `teardown`, `bringup-deploy` (RAID+mount NVMe, push the worker bundle + frozen gate corpora, launch the worker detached, arm the guest max-life), `watchdog --max-hours H` (box-side teardown loop; nohup it, verify `pgrep -f 'f1k_gcp.py watchdog'`), `gate` (**the bring-up gate verdict — kot-f1k-bringup-gate/2; GREEN is the ONLY construction license**; `--selftest` = $0 mock oracle), `pin-fetch` (fetch + byte-verify the licensed campaign pin → eval-safe explicit `PIN`/`PIN_GB` exports; `/2`+GREEN required [REV-B/C]), `affordability` (one-blended-s/prefill projection — **SECONDARY diagnostic ONLY, licenses nothing**). |
| `f1k_bringup_gate.py` | The FIXED bring-up gate machinery (`F1K-BRINGUP-GATE-FIX.md` v1+REV-B+REV-C, GAP-1/2/3): frozen deterministic stratified real-corpus sampling rule, full-corpus tokenization (measured f, per-item T), per-item-manifest bring-up pin derivation (fail-closed merge + provenance), per-item token-aware ledger projection + GREEN/STOP **`/2` model-bundle-bound** artifact (engagement-verified, unpinned refused), `checkpoint` = frozen-schedule construction early-abort re-projection, `guard` = **construction wrapper** (explicit pin env + dump-mode engagement probe + in-process checkpoints + kill-on-breach; the sha-pinned builder stays untouched), `config-affordability`/`config-cost` = executable gate→campaign-config seams; `selftest` = $0 mock oracle of the LOGIC seams only (no real engine/tokenizer/GCS/VM — honest scope printed). |
| `bringup_gcp.sh` | KaE bring-up on the VM: colibri@`a78a06fc` + KaE patch (`11f8b458`), build, 44/44 `test_kae`; objdump patch-shape checks (clone-aware, reference + native flags) are **ADVISORY-ONLY on the VM** (bead f2uk / ASM-2503: gcc-version-brittle even at `-O2 -march=x86-64-v3`; fail-closed objdump lives off-box on the gcc-11.5 basis; the frozen `bringup.sh` is untouched). The AUTHORITATIVE inertness proof is the functional KAE-unset byte-identity gate in `f1k_worker.sh`. |
| `f1k_worker.sh` | On-VM autonomous worker: STAGE (GCS mirror → else HF → NVMe, weight-hash pin) → BUILD scoring + construction engines → KaE bring-up → dump bring-up gate (b) → scaffolds (a)+(c) → **REAL-CORPUS gate inputs** (tokenize → measured f + per-item T; frozen stratified per-item timing, T1 unpinned → bring-up pin → T2 pinned; `gate-inputs.json`) → **STOP before construction spend**. Heartbeat + artifacts to GCS; idempotent (spot preemption re-runs, restages from GCS). |

## Run sequence (frozen §R-REV4.2 ordering; each paid step gated)

0. `source ~/.config/kot/gcp.env`; `python3 poc/gcp/f1k_gcp.py plan` ($0).
1. `provision` → **record the ACTUAL assigned spot $/h** (load-bearing for the
   affordability gate). Set `KOT_F1K_BUCKET=gs://…` (same-region estate mirror),
   `COLIBRI_GIT_URL` (coordinator-supplied), `KOT_F1K_SPOT_RATE=<measured>`.
2. `python3 poc/gcp/f1k_gcp.py bringup-deploy` — remote prep **verifies the
   fresh-worker dependencies** (`google-cloud-cli`/gsutil + `python3-pip`
   installed when the image lacks them, fail-closed) and RAID0+mounts the 2
   local SSD **by state** (`mountpoint -q`; reboot re-assembles `/dev/md0` and
   re-mounts, `mkfs` only on first creation — a bare `/mnt/nvme` dir never
   silently stages ~384 GB onto the boot disk); assembles + pushes the worker
   bundle (worker, `bringup_gcp.sh`, `f1k_bringup_gate.py`, `tok_glm52.py`,
   `kae-patch-draft/`, `dump-patch/`, `f1k_launch.sh` launcher, and
   `gate-corpus/` = the four frozen corpora `construction-manifest.jsonl` +
   `f1k-eval-v1/items/{test,dev,guard}.jsonl`, sha-manifested); launches the
   worker detached **via `f1k_launch.sh`** (ANY nonzero worker exit — `set -e`
   deaths included — writes a `FAILED` heartbeat the watchdog acts on
   promptly, never waiting out max-life); arms the guest max-life (verify
   on-VM: `sudo shutdown --show`). Then start the box-side watchdog:
   `nohup python3 poc/gcp/f1k_gcp.py watchdog --max-hours 8 &` — verify
   `pgrep -f 'f1k_gcp.py watchdog'` (plan §9: never agent-held).
3. Worker STAGE + BUILD + KaE bring-up + **dump bring-up gate**:
   - (b) unarmed byte-identity + `test_kae` 44/44 + `test_kae_dump` 43/43 +
     objdump inertness — automated via `dump-patch/real-checks.sh`.
   - (a) tiny real dump + `kot-f1k-tok/1` token-id consistency — **runner
     confirms ON-BOX** (echo `seed=20260716`; tok ids == engine-prefilled ids).
   - (c) independent MoE-input sum cross-check on MIXED positions — **runner
     confirms ON-BOX** (a separate capture path, not `kae_dump.h`, cell-for-cell
     equal to the engine dump). Its correctness cannot be validated blind, so
     it is a runner-confirmed PASS. ANY precondition failure → SALVAGE+STOP.
     **The recorded PASS of (a)/(b)/(c) + the functional gate is a HARD
     conjunct of the construction license** (v3-review): the runner writes
     the literal `PASS` into `tiny-dump.status`/`moe-sum-crosscheck.status`
     and re-runs the worker's collect command (no re-timing) — a
     `RUNNER-CONFIRM-REQUIRED` scaffold status makes `gate` STOP.
4. **Bring-up affordability gate** (`F1K-BRINGUP-GATE-FIX.md` v1+REV-B): the
   worker tokenizes the frozen corpora (measured **f** + per-item T), times
   the frozen stratified REAL-corpus sample per-item (T1 unpinned with
   **one `STATS=<file>` per run**, merged fail-closed over an explicit
   manifest → bring-up pin at measured PIN_GB → T2 pinned, per-run
   engagement banner recorded), and writes `gate-inputs.json`; then on the
   control box `f1k_gcp.py gate --inputs <pulled gate-inputs.json>` — **GREEN
   (exit 0) is the ONLY license for construction spend**; STOP = mandatory
   maintainer surface (plan §7). Caps are tested **reserve-inclusive**
   (+$8 / +$8÷rate hours [STIPULATED plan §8 reserve]; floors compute-only);
   dump (a)/(b)/(c) + functional PASS are hard conjuncts; **per-T2-run
   pin-ENGAGEMENT evidence for the bound sha/PIN_GB is a hard conjunct**
   (landed ASM-2513 banner grammar) and **regime `unpinned` is REFUSED**
   (shape (ii) rejected); `--replace` tests the 21,537 envelope and ANY
   tested STOP exits nonzero. The synthetic blend + `f1k_gcp.py
   affordability` remain a SECONDARY diagnostic, licensing nothing (exit 3
   even when clean).
5. **Construction** (gated on 3+4) **[REV-C: guard-wrapped; the sha-pinned
   builder is byte-untouched]**:
   a. Fetch + byte-verify the licensed pin:
      `python3 poc/gcp/f1k_gcp.py pin-fetch --gate bringup-gate.json --out
      <rundir>` (fail-closed: schema `/2` + GREEN only; fetched bytes must
      sha-match `pin.pin_file_sha256`; stdout = the exact `export PIN=` /
      `export PIN_GB=` lines, eval-safe — but step 5b consumes `--pin`
      directly, no ambient env needed).
   b. Launch construction THROUGH the guard (ONE command; the guard binds
      `PIN`/`PIN_GB` into the child env itself — never ambient; pops
      `STATS` and the mode knobs; probes engagement; runs the frozen
      checkpoints; kills on breach):
      `python3 poc/gcp/f1k_bringup_gate.py guard --gate bringup-gate.json
      --pin <rundir>/campaign-pin.stats --engine-cmd '<json argv>'
      --tokenizer-cmd '<json argv>'
      --layers 3,…,77 --tokens <gate-tokens/tokens-full.jsonl>
      --rundir <rundir>/guard --workdir <workdir> --
      python3 poc/glm52-probe/f1k-harness/build_carriers.py construct
      --mode real --layers 3,…,77 <provenance shas AND artifacts:
      --tokenizer-sha/-artifact --engine-weights-sha/-artifact
      --dump-patch-sha/-artifact> --out <out> --workdir <workdir>`
      (4,608 passes EXACT; ASM-2504 DRAFT=0 geometry, 75 layers).
      **ENGINE-ARGV UNITY [REV-D]: the guard OWNS `--engine-cmd`/
      `--tokenizer-cmd` — it probes the engine argv and INJECTS both
      values into the builder argv itself (construct-don't-compare), so
      the builder argv above is complete AS PRINTED (oracle-verified
      against the builder's real argparse surface) and deliberately
      carries NO engine/tokenizer flags; supplying them there is
      REFUSED before any engine start — including every
      argparse-resolvable ABBREVIATION (`--engine-c`, `--engine-cm`,
      `--tokenizer-c`, `--tokenizer-cm`, space and `=` forms): the
      guard's refusal floors equal the pinned builder's own
      prefix-resolution, oracle-proven against its real parser
      [REV-E].** The guard FIRST runs a
      **dump-mode pin-engagement probe** (one minimal `KAE_DUMP`
      invocation of that same engine argv/env; armed banner per the
      landed ASM-2513 grammar, sha/budget/source coherent — REFUSED ⇒
      no launch, exposure ≈ one engine start), then launches the builder
      (which passes its ambient env into every engine batch —
      `build_carriers.py:634`, verified bytes), and runs the
      **early-abort checkpoints** IN-PROCESS at n_done **240/1056/2304**
      (frozen concept-aligned schedule [REV-C/ASM-2517]; off-schedule
      n_done is refused; STOP exit 2 = builder process-group killed +
      `construction-abort.json` with the breach values; first exposure
      ≈ 9.1 h ≈ **$1.59**). **A checkpoint STOP is TERMINAL for the
      rundir [REV-D]: the guard refuses to start while
      `construction-abort.json` exists — resume needs a maintainer-
      authored `construction-reset.json` (schema
      `kot-f1k-bringup-gate/2:construction-reset`, `authorized_by`,
      `decision: "resume-construction"`, `abort_sha256` = sha256 of the
      abort file bytes). The STOP is DURABLE [REV-E]: it is also
      recorded as an append-only terminal event in
      `construction-events.jsonl` (fsynced, spend-start-sentinel
      mechanics) that every guard start reads — deleting the abort
      file never lifts stop authority. An authorized resume re-derives
      the FULL remaining schedule from the abort point (a raced-past
      frozen checkpoint refuses rather than being dropped) and
      CONSUMES the reset: reset and abort are archived
      (`construction-reset.consumed-<ordinal>-<abort-sha16>.json`)
      BEFORE any engine start, so a second use finds nothing —
      single-use by construction. (Editing the guard's event state
      itself is outside the threat boundary, as for the landed
      sentinel.)**
      Evidence: `construction-pin-probe.json`,
      `construction-checkpoint-<n>.json`, `construction-guard-final.json`
      (records the launched `builder_argv`).
   c. `verify --expect-mode real` (full cell-by-cell re-derivation, the
      #46 guarantee); commit the realized tables + `norms.json` +
      `construction-report.json` = **B0**, completing `f1k-carriers-v1`.
      Pin `glm52-weights` (ASM-1971 ops amendment).
   d. Transfer the realized cost basis + the licensed model bundle into
      the campaign config (executable, no pilot stall):
      `python3 poc/gcp/f1k_bringup_gate.py config-cost --final
      <rundir>/guard/construction-guard-final.json --prior-usd <metered
      pre-construction + failed-session spend> --prior-hours <the
      instance-hours behind that spend; REQUIRED when --prior-usd > 0
      [REV-D] — hours never vanish from the 900 h basis while their
      dollars are counted> --rate <campaign spot rate> --config
      run-config.json` (every numeric on this surface must be FINITE —
      `nan`/`inf` are refused at the parse, and the driver Ledger
      re-asserts finiteness at init: a NaN basis would fail OPEN
      through the 900 h cap comparisons [REV-E]) and
      `python3 poc/gcp/f1k_bringup_gate.py config-affordability --gate
      bringup-gate.json --tokens <gate-tokens/tokens-full.jsonl> --config
      run-config.json` (both refuse a conflicting existing block; the
      driver re-verifies EVERYTHING at consumption — schema `/2`, GREEN,
      shared-model sha, sidecar bytes vs the ARTIFACT-recorded sha,
      corpus item-universe, rate equality, pin identity).
   **Campaign pin [REV-C]: the LICENSED bring-up pin runs the WHOLE
   campaign.** Full-corpus re-derivation at the construction→pilot
   boundary is **DEFERRED** (it needs per-batch `STATS` hooks the
   sha-pinned builder does not have — a seq-4 builder re-freeze, tracked
   as a bead, NOT on this critical path); there is NO rebind record and
   NO rebind path — the driver REFUSES a campaign pin whose sha differs
   from the gate artifact's, and the landed ASM-2513 machinery (Ledger
   cross-phase basis + `check_addendum_pinning` + spend-start sentinel)
   enforces constancy across pilot/guard/test. Under-coverage of the
   bring-up pin shows up as throughput loss and is bounded by the
   checkpoints (≤ ≈$1.6/$7/$15 at 240/1056/2304) and the addendum-(7)
   pre-main gate. Never mid-phase, never silent.
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
