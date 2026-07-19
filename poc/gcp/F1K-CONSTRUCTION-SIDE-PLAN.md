<!-- Provenance: GPT-5.6 construction-side (leaner-B) implementation plan, 2026-07-19, Fable capped. Interface-first contract for the post-GREEN construction launch. KEY INSIGHT: leaner-B treats Spot preemption as TERMINAL (no resume) — the 38-day construction NEEDS option-A resume/ledger to survive preemption; B is a stepping stone. Real GREEN-dependent values fixture-testable now. -->

# F1-K construction-side (leaner-B) implementation plan

The leaner-B contract should be:

`provider delete armed at provision → READY + GREEN → same-instance construction-continue → systemd guard → pre-spend live-license checks → probe → frozen builder`

B contains no ledger, lease, controller heartbeat, metadata-attestation CAS, or post-preemption resume authorization. It treats a Spot preemption after handoff as terminal for that attempt.

The plan below is grounded in the landed [construction memo](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/F1K-CONSTRUCTION-LAUNCH-ARCH.md:7), [full-rigor schema plan](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/F1K-LAUNCH-IMPL-PLAN.md:304), READY writer [f1k_worker.sh](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_worker.sh:643), and current guard/checkpoint code [f1k_bringup_gate.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_bringup_gate.py:1127).

## 1. Dependency-ordered implementation units

### B0 — Shared construction contract validators

File: `poc/gcp/f1k_ops.py`.

Add pure operational validators, separate from scientific projection:

- Strict READY `/1` validator against the landed shape.
- Strict GREEN gate `/2` validator.
- READY↔gate binding validator.
- Strict handoff `/1` validator.
- A pure artifact verifier for normalized paths, path containment, symlink refusal, SHA pairs, builder pin, and argv shape.
- A normalized “runtime license” result consumed identically by `construction-continue` and guard.

Rules:

- Closed schemas: missing or unknown fields refuse.
- Canonical JSON uses landed `canonical_json_bytes`.
- Accounting/rate values are canonical decimal strings; no JSON floats.
- No imports from `f1k_bringup_gate.py`; scientific code remains one-way dependent on operational helpers.
- No ledger/lease/attestation functions.

Dependencies: none; build first.

### B1 — Provider wall-clock/delete backstop

File: `poc/gcp/f1k_gcp.py`, primarily `_provision_plan`, `cmd_provision`, `cmd_plan`, and `cmd_status`.

At VM creation, arm an absolute Compute Engine `terminationTime` with automatic `DELETE`; do not use a duration that is recomputed after a restart. Record and later verify the observed `terminationTimestamp`.

This must land before the relevant VM is provisioned. Retrofitting the setting onto a running VM requires stop/update/start, which would invalidate the prepared boot and endanger Local-SSD state.

Also create or verify a project-scoped `$300` Billing Budget as a secondary alert.

Dependencies: B0 only for evidence/schema validation; otherwise independently testable.

### B2 — Live-rate checkpoint evaluator

File: `poc/gcp/f1k_bringup_gate.py`.

Refactor only `checkpoint_eval`, `cmd_checkpoint`, the in-process guard call site, and checkpoint artifacts:

- `cmd_checkpoint` resolves live identity/rate through landed `f1k_ops`.
- The pure evaluator receives the canonical live rate and rate-evidence record rather than doing network I/O.
- Preserve `{240,1056,2304}`, current realized-ratio mechanics, upper-cap checks, reserve, and kill authority.
- Add cumulative-actual-plus-remaining arithmetic described below.
- Quote failure or canonical rate drift is terminal.

No changes to sampling, knots, interpolation, Add7, scientific constants, or projection geometry.

Dependencies: landed rate resolver; can be completed before guard.

### B3 — Small guard live-license delta

File: `poc/gcp/f1k_bringup_gate.py`.

Add:

- Required `--handoff`.
- One `_load_guard_runtime_license`-style helper at the top of `cmd_guard`.
- Legacy guard arguments become optional. The helper fills them from READY; if explicitly supplied, they must match exactly.
- Periodic live-rate sentry in the existing guard poll loop.
- A single exclusive construction lock.
- A final lightweight rehash/live-identity barrier before reset consumption.

Everything following successful loading—the existing reset authority, engagement probe, builder injection, checkpoint scheduling, and kill path—stays structurally unchanged.

Dependencies: B0 and B2.

### B4 — Same-instance `construction-continue`

File: `poc/gcp/f1k_gcp.py`.

CLI:

- `construction-continue --gate LOCAL_PATH --ready LOCAL_PATH`
- `construction-continue --selftest`
- No B `--resume`.

The command is control-box initiated, consistent with existing `f1k_gcp.py` orchestration. It:

1. Loads and hashes the exact local GREEN and READY files.
2. Resolves the live Compute identity and obtains the guest boot ID.
3. Requires exact equality with READY, including numeric ID, boot ID, and `lastStartTimestamp`.
4. Verifies SPOT, rate equality, provider deletion, `$300` envelope, and budget resource.
5. Cross-validates READY and GREEN.
6. Copies gate, rate evidence, and handoff atomically to the guest canonical paths and reads their SHAs back.
7. Cancels the existing 15-hour bring-up guest shutdown only after the provider delete is verified.
8. Installs and starts the systemd construction unit.
9. Verifies `ActiveState=active`, a nonzero MainPID, and the exact direct ExecStart.
10. Does not execute or mention a builder command outside the handoff.

Dependencies: B0, B1, B2, and B3.

### B5 — Integration/regression gate

Update the runbook only after B0–B4 are green. Require:

- Existing ops, worker, gate, and deploy selftests.
- Builder full SHA unchanged.
- `bash -n` and Python import/compile checks.
- No diff to Add7, sampling, projection geometry, pins, layers, analysis, driver, or builder.
- Fixture-backed dry run from GREEN+READY to an active stub guard unit.
- Independent launch/TOCTOU and budget/preemption review.

## 2. `construction-handoff.json`

Schema: `kot-f1k-construction-handoff/1`.

Encoding: UTF-8, sorted compact keys, one trailing newline; exact-byte SHA-256; lowercase 64-hex SHAs; UTC `Z` timestamps. Production path: `/home/ubuntu/f1k-gate/construction-handoff.json`.

This intentionally follows the landed `/home/ubuntu/f1k*` layout, not the not-yet-landed `/opt`/`/var/lib` paths from option A.

| Field | Type | Contract |
|---|---|---|
| `schema` | literal | `kot-f1k-construction-handoff/1`. |
| `created_at_utc` | RFC3339 UTC | Handoff creation time. |
| `mode` | literal | `"initial"` only in B. |
| `instance.instance_id` | decimal-digit string | Must equal READY, metadata, and Compute `instances.get`. |
| `instance.name` | string | Informational; never substitutes for numeric ID. |
| `instance.project_id` | string | Exact live project. |
| `instance.project_number` | decimal-digit string | Exact metadata project number. |
| `instance.zone` | string | Exact short zone. |
| `instance.machine_type` | string | Exact `n2d-highmem-8`. |
| `instance.provisioning_model` | literal | `"SPOT"`. |
| `instance.last_start_timestamp` | RFC3339 UTC | Exact live control-plane boot/start binding. |
| `instance.boot_id` | UUID | Exact `/proc/sys/kernel/random/boot_id`. |
| `ready.path` | absolute path | `/home/ubuntu/f1k-gate/construction-ready.json`. |
| `ready.sha256` | SHA | Exact READY file bytes. |
| `ready.schema` | literal | `kot-f1k-construction-ready/1`. |
| `ready.status` | literal | `"READY"`. |
| `gate.path` | absolute path | `/home/ubuntu/f1k-gate/bringup-gate.json`. |
| `gate.sha256` | SHA | Exact GREEN file bytes. |
| `gate.schema` | literal | `kot-f1k-bringup-gate/2`. |
| `gate.verdict` | literal | `"GREEN"`. |
| `binding.schema` | literal | `kot-f1k-ready-gate-binding/1`. |
| `binding.builder_sha256` | SHA | Full `a92be3e4fe535c1dfefc41e2a422e010d25e8e40cf8e4cc123e7d829d63e9e61`. |
| `binding.tokens_full_sha256` | SHA | READY token-sidecar SHA and gate model-bundle SHA must both equal it. |
| `binding.pin_sha256` | SHA | READY pin SHA and gate pin SHA must both equal it. |
| `binding.pin_gb_decimal` | decimal string | Canonicalized equality of READY and gate PIN_GB; no pin change. |
| `binding.tokenizer_sha256` | SHA | READY tokenizer artifact and gate tokenizer SHA. |
| `binding.construction_manifest_sha256` | SHA | READY source-manifest SHA and gate construction corpus SHA. |
| `binding.timing_result_set_sha256` | SHA | From landed `ready.timing_results.result_set_sha256`. |
| `binding.sample_sha256` | SHA | SHA of canonical gate `sample`; T1/T2 IDs must match READY timing IDs. |
| `rate.usd_per_hour_decimal` | decimal string | One value shared by gate, live resolver, and rate evidence. |
| `rate.local_ssd_count` | integer | Exactly `2`. |
| `rate.evidence.path` | absolute path | `/home/ubuntu/f1k-gate/live-rate-evidence.json`. |
| `rate.evidence.sha256` | SHA | Exact canonical `kot-f1k-rate-evidence/1` bytes. |
| `rate.evidence.schema` | literal | `kot-f1k-rate-evidence/1`. |
| `rate.evidence.observed_at_utc` | timestamp | Quote observation time. |
| `provider.campaign_started_at_utc` | timestamp | Anchor for the B wall-clock envelope; never GREEN time. |
| `provider.termination_time_utc` | timestamp | Configured absolute deadline. |
| `provider.termination_timestamp_utc` | timestamp | Read-back provider timestamp; must equal the intended deadline. |
| `provider.instance_termination_action` | literal | `"DELETE"`. |
| `provider.frozen_hours_max_decimal` | decimal string | `"900"`. |
| `provider.armed_hours_decimal` | decimal string | At most `899`, or earlier if required by the `$300` envelope. |
| `provider.non_compute_allowance_usd_decimal` | decimal string | Maintainer-approved outer-services allowance. |
| `provider.rate_headroom_usd_decimal` | decimal string | Allowance for quote/poll latency and termination lag. |
| `provider.compute_ceiling_usd_decimal` | decimal string | `armed_hours × licensed_rate`. |
| `provider.total_envelope_usd_decimal` | decimal string | Compute ceiling plus both allowances; must be `<=300`. |
| `provider.budget.resource_name` | string | Exact project-scoped GCP Budget resource. |
| `provider.budget.amount_usd_decimal` | literal decimal | `"300"`. |
| `provider.budget.project_id` | string | Same project as the live identity. |
| `paths.rundir` | absolute path | Must equal READY; landed production value `/home/ubuntu/f1k-gate/guard`. |
| `paths.workdir` | absolute path | Must equal READY. |
| `paths.out` | absolute path | Must equal READY and builder argv. |
| `service.manager` | literal | `"systemd"`. |
| `service.unit_name` | literal | `kot-f1k-construction.service`. |
| `service.user` | literal | `ubuntu`. |
| `service.working_directory` | absolute path | Exact READY payload root. |
| `service.exec_argv` | string array | Direct guard invocation only. |
| `service.restart_policy` | literal | `"no"`; a policy stop/crash never auto-relaunches spend. |
| `service.enabled_on_boot` | boolean | `false` in B; preemption requires a new licensed attempt. |

The exact `service.exec_argv` is:

- READY’s resolved Python interpreter;
- READY payload root plus `/f1k_bringup_gate.py`;
- `guard`;
- `--handoff`;
- `/home/ubuntu/f1k-gate/construction-handoff.json`.

The handoff deliberately omits option-A `generation`, `previous_handoff_sha256`, controller, heartbeat, ledger, lease, and metadata-attestation fields.

The landed gate has no `timing_epoch_id`; therefore the option-A `gate.timing_epoch_id` field must not be copied into B. Binding uses the landed READY `timing_results` plus the gate `sample`, pin, tokenizer, token-sidecar, and corpus fields.

## 3. Exact guard pre-spend order

Every item below completes before reset consumption, engagement probing, or any engine start:

1. Require `--handoff`; read exact bytes, reject symlinks/non-regular paths, validate the closed schema, and calculate the handoff SHA.
2. Resolve live identity through `f1k_ops.resolve_live_instance_identity`; require all nine identity fields to equal the handoff and READY identity.
3. Require live `scheduling.provisioningModel == SPOT`; verify `instanceTerminationAction=DELETE`, the provider `terminationTimestamp`, and sufficient remaining wall time.
4. Resolve the all-in live rate for project/zone/machine/two Local SSDs. Quote failure refuses. Require canonical equality with the handoff rate.
5. Hash the gate path against `gate.sha256`; require `/2`, GREEN, and `gate.rate.usd_per_hour_decimal == handoff.rate`.
6. Hash and validate READY; require READY↔gate↔handoff equality for identity, token sidecar, tokenizer, pin/PIN_GB, construction manifest, timing IDs, layers, and paths.
7. Run existing pin/PIN_GB and Add7 verification unchanged.
8. Rehash `args.tokens` from READY and require equality with `gate.model_bundle.tokens_full_sha256`.
9. Resolve the builder without symlinks; require the full `a92be3e4…` SHA, exact READY path, argv beginning with resolved interpreter + builder + `construct`, and no guard-owned engine/tokenizer options.
10. Validate engine/tokenizer argv and rehash READY’s engine, weights, tokenizer artifact, dump patch, source/bundle manifests, and PASS evidence. Explicit legacy CLI values must match READY exactly.
11. Require rundir/workdir/out equality and containment; acquire the exclusive construction lock. Require the systemd unit’s parsed ExecStart to equal `service.exec_argv`.
12. Final barrier: rehash handoff, gate, READY, builder, token sidecar, pin, and provenance artifacts; resolve identity and live rate once more.
13. Only now enter the existing terminal-abort/reset logic and, if authorized, consume a reset exactly as today.
14. Run the existing engagement probe unchanged.
15. Execute the validated READY builder argv with the existing guard-owned engine/tokenizer injection.

At every existing guard poll, refresh the live rate before checking progress. Quote failure or any canonical inequality kills the process group and writes a durable local `rate-drift` terminal artifact/event using the existing terminal-stop machinery. No automatic re-gate or window change is allowed.

## 4. Wall-clock deletion and `$300`

Recommendation: use the Compute Engine absolute VM time limit—`terminationTime` plus automatic `DELETE`—not Cloud Scheduler, a control-box watchdog, or a normal instance schedule.

Why:

- An absolute time is restored to the same value after a stop/start; a duration is recalculated from the latest start.
- Spot VMs support this feature, automatic deletion is provider-side, and 900 hours is within the 120-day maximum.
- Provider termination can begin up to 30 seconds late, so arm at no later than campaign start + 899 hours, leaving a full hour of margin. [Compute Engine VM runtime limits](https://docs.cloud.google.com/compute/docs/instances/limit-vm-runtime)
- A normal instance schedule only starts/stops, cannot stop this Local-SSD VM, and can run late by 15 minutes. [GCE instance-schedule limitations](https://docs.cloud.google.com/compute/docs/instances/schedule-instance-start-stop)

The tradeoff is explicit: `instanceTerminationAction=DELETE` also makes Spot preemption delete the VM. That is appropriate for B because B has no durable cumulative ledger or safe resume license. A preempted attempt gets a new VM, READY, GREEN, and handoff; it never carries the old GREEN forward.

If retaining a stopped numeric instance after preemption is mandatory, use a Cloud Scheduler job with an absolute campaign deadline and authenticated Compute DELETE as the fallback. It must use a fixed campaign deadline, retries, and an early safety margin; a control-box `nohup` process is not a hard bound.

The `$300` budget is only a tripwire: Google explicitly states that budgets do not cap usage or spending. [GCP Billing Budget behavior](https://docs.cloud.google.com/billing/docs/how-to/budgets)

Therefore B may claim a hard `$300` envelope only when, before provisioning and again before guard launch:

`armed_hours × licensed_live_rate + non_compute_allowance + rate/termination_headroom <= 300`

If that inequality cannot be established, construction-continue must refuse. The budget alert alone cannot repair it. The `$155` construction cap remains separately controlling through GREEN and checkpoints; `$300` never enlarges it.

## 5. Checkpoint live-rate formula

For checkpoint branch `b ∈ {central,+1SE}`:

- `A_h`: cumulative actual construction hours in the uninterrupted B guard session.
- `A_usd = A_h × R_live`.
- `P_done`: gate-model central seconds for completed construction items.
- `P_remaining_b`: gate-model seconds for every remaining licensed campaign item under branch `b`, including multiplicities.
- `r = actual_construction_seconds / P_done`.
- `R_live`: freshly resolved canonical live rate, required to equal the gate rate.
- Reserve remains exactly `$8`.

Then:

`projected_hours_b = A_h + r × P_remaining_b / 3600`

`projected_usd_b = A_usd + r × P_remaining_b / 3600 × R_live + 8`

`projected_hours_with_reserve_b = projected_hours_b + 8 / R_live`

STOP if either central or +1SE exceeds 900 hours or `$155`. The lower floors are unchanged and are not turned into early-spend targets.

Checkpoint artifacts add:

- Gate and live canonical rates.
- Rate-evidence SHA and observation time.
- Cumulative actual hours/USD.
- Predicted completed and remaining seconds.
- Realized ratio.
- Central/+1SE remaining hours and dollars.
- Unchanged reserve and thresholds.
- Provider termination time and remaining wall time.
- CONTINUE/STOP plus exact breach reasons.

B only supports this arithmetic for one uninterrupted construction launch. Resuming prior construction spend after process loss or preemption requires option A or a separately approved cumulative-state contract.

## 6. Per-unit `$0` oracle plan

### B0 contracts

Refuse:

- Wrong/missing/unknown schema fields.
- JSON floats in accounting/rate fields.
- Malformed SHA/timestamp/path.
- READY identity mismatch.
- Gate not `/2` or not GREEN.
- Token, tokenizer, pin, corpus, sample-ID, layer, or path mismatch.
- Symlink/path escape/special file.
- Builder drift or alternate builder/interpreter seam.

Happy path:

- Deterministic canonical bytes and SHA.
- Exact landed-shaped READY and GREEN fixtures produce one normalized runtime license.
- Reordering JSON keys does not alter canonical output.

### B1 provider bound

Refuse:

- `maxRunDuration` in place of an absolute time.
- STOP action, absent/late termination timestamp, deadline over 900 hours, or deadline already passed.
- STANDARD/preemptible rather than SPOT.
- Budget missing, wrong project, or amount other than `$300`.
- Nonpositive allowance/headroom or total envelope over `$300`.
- Remaining provider time below GREEN’s reserve-inclusive +1SE projection.

Happy path:

- Fake Compute insertion contains absolute termination and DELETE.
- Fake describe returns matching numeric ID, scheduling, and termination timestamp.
- Pure arithmetic chooses at most 899 hours.
- No gcloud/network/resource mutation occurs in selftest.

### B2 checkpoints

Refuse/STOP:

- Off-schedule checkpoint.
- Missing/failed/malformed live quote.
- Live rate different from gate even if both remain inside the frozen rate window.
- Live rate outside the frozen window.
- Rate evidence target mismatch.
- Nonfinite/negative actuals or ratio.
- Cumulative-actual-plus-remaining central or +1SE breach.
- Insufficient provider wall time.

Happy path:

- Synthetic equal gate/live rates reprice remaining work exactly.
- Changing both fixture gate and live rates changes dollars but not scientific seconds.
- Actual completed work is not projected a second time.
- `{240,1056,2304}` and kill behavior remain unchanged.

### B3 guard

For every ordered check, inject one failure and assert:

- No reset-consumed event.
- No probe artifact.
- No engine marker.
- No builder marker.

Cases include wrong numeric ID/name/boot, STANDARD, missing deletion, quote outage, rate drift, mutated handoff/gate/READY, pin/Add7 drift, token drift, builder drift, argv mismatch, provenance drift, path substitution, bundle escape, and lock contention.

Happy path uses the real landed READY shape with stub engine/builder and runs all checkpoints. A poll-time rate drift must kill the stub process group and make the next invocation terminally refuse.

### B4 construction-continue

Use fake gcloud, SSH, file-transfer, and systemd transports.

Refuse:

- READY/GREEN mismatch.
- Recreated same-name VM.
- Changed boot or `lastStartTimestamp`.
- Failed remote SHA readback.
- Missing/incorrect provider termination or budget.
- Live-rate mismatch.
- Existing active unit with different handoff/ExecStart.
- Inactive unit, missing MainPID, or systemd ExecStart containing a wrapper/builder.
- Any B resume request.

Happy path proves:

- Exact canonical handoff bytes.
- Exact remote gate/READY/rate-evidence bytes.
- Direct systemd guard argv only.
- Active guard unit verification.
- Idempotent replay returns the existing active unit and does not start a second guard.

### B5 regression

Run the existing 23/23 ops, 14/14 worker, 69/69 gate, and 11/11 deploy oracles; builder dry-parse/selftest; shell syntax; Python imports; static SHA checks; and a diff assertion covering Add7, sampling/projection regions, scientific pins, driver, analysis, and builder.

## 7. Decisions still required

1. **Preemption:** Recommend terminal DELETE in B. If same-ID STOP/restart is required, choose Cloud Scheduler or option A.
2. **`$300` scope:** Specify the fixed non-compute and rate-lag allowance. Without it, `$300` is an alert, not a hard all-services ceiling.
3. **Campaign anchor:** Recommend the first provision time, not GREEN/handoff time, and never reset it across retries.
4. **Rate drift:** Recommend terminal stop on any canonical inequality, including drift still inside the frozen rate window.
5. **Resume:** Recommend no B construction resume. Existing cached construction output may be inspected but not relaunched under the old handoff.
6. **Existing VM:** If the candidate VM is already running without an absolute provider termination time, decide between discarding/reprovisioning or using the Cloud Scheduler fallback; do not stop it merely to retrofit the GCE setting.
7. **Budget identity:** Provide the billing account/budget resource and alert recipients or Pub/Sub destination.
8. **Actual GREEN dependencies:** Gate SHA, READY SHA, instance/boot identity, rate/evidence SHA, deadline remaining, projection, and systemd MainPID cannot be populated until the real outputs exist. The validators and every refusal oracle remain `$0` and fixture-testable now.

No repository files were changed.

### Summary

- B is GREEN+READY → exact same boot/instance → systemd guard → frozen builder.
- The handoff binds exact live identity, artifacts, rate evidence, provider deletion, and direct guard argv.
- Guard performs all new checks before reset consumption or the engagement probe.
- Any quote failure or canonical rate drift kills construction; checkpoints use actual-plus-live-priced-remaining.
- `$300` is hard only with a declared outer-services/headroom envelope; the Budget is secondary.
- Recommended first code-round unit: **B0 shared handoff/READY/gate validators and their pure fixture oracle**.