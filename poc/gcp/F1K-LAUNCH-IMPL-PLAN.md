<!-- Provenance: GPT-5.6 (gpt-5.6-sol) interface/schema plan for the Single-VM-Spot launch architecture, 2026-07-18, authored while Fable capped. This is the FULL-RIGOR (option A) spec; a proportionality decision (full vs leaner provider-native backstop) is pending on issue #53. Reusable regardless of rigor level: the schemas, guard 15-step pre-spend order, and oracle lists. -->

# F1-K Single-VM-Spot launch — full-rigor implementation plan (option A)

The implementation should use one new repository module, `poc/gcp/f1k_ops.py`, plus changes to the three named files and the two existing docs. The normative path becomes:

`Spot provision → full-payload bring-up → complete timing epoch → GREEN → same-instance handoff → controller-backed lease → guard → builder`

No code or files were changed this round.

## Fixed constraints

These are acceptance invariants, not implementation choices:

- Normative bring-up and construction use the same GCE instance with `provisioningModel=SPOT`. `KOT_F1K_ONDEMAND` is refused on this path.
- The outer operational ledger caps gross project-attributable GCP spend across every service at `$300`.
- The construction ledger remains controlled by `[260.6, 900]` instance-hours, `[$73, $155]`, the existing rate window, and the existing `$8` reserve.
- The `$300` ceiling never enlarges or supersedes the `$155` construction-compute license.
- Sampling, projection geometry, checkpoint schedule `{240,1056,2304}`, layer set, reserve, scientific pins, frozen analysis, and driver remain untouched.
- `build_carriers.py` remains byte-identical at `a92be3e4fe535c1dfefc41e2a422e010d25e8e40cf8e4cc123e7d829d63e9e61`.
- `guard` remains the only licensed launcher of `build_carriers.py`.
- Every change is operational enforcement only; it introduces no scientific assumption.

## 1. Dependency-ordered implementation units

### Unit 1 — Operational contracts and durable controller core

New repository file:

- `poc/gcp/f1k_ops.py`

Public functions:

- `canonical_decimal(value, *, field) -> str`
- `canonical_json_bytes(record) -> bytes`
- `atomic_write_json(path, record, *, mode=0o600) -> str`
- `read_live_instance_metadata(path, *, timeout_s=2.0, transport=None) -> str`
- `resolve_live_instance_identity(*, metadata_transport=None, compute_transport=None) -> dict`
- `resolve_live_rate(*, project_id, zone, machine_type, local_ssd_count, observed_at_utc=None, catalog_transport=None) -> tuple[str, dict]`
- `write_instance_metadata_attestation(*, project_id, zone, instance_name, expected_instance_id, handoff_sha256, expected_metadata_fingerprint, compute_transport=None) -> dict`
- `verify_instance_metadata_attestation(*, expected_handoff_sha256, metadata_transport=None) -> dict`
- `issue_spend_lease(*, ledger_state, handoff_sha256, live_identity, rate_evidence, now_utc, duration_seconds=21600) -> dict`
- `renew_spend_lease(*, current_lease, ledger_state, heartbeat, rate_evidence, now_utc, duration_seconds=21600) -> dict`
- `expire_spend_lease(*, current_lease, ledger_state, reason, now_utc) -> dict`
- `verify_spend_lease(*, lease, ledger_state, heartbeat, live_identity, now_utc) -> dict`
- `append_ledger_event(*, durable_paths, event_body, expected_head_sha256, expected_gcs_generation) -> tuple[dict, int]`
- `replay_ledger(*, pd_path, control_box_path, gcs_uri, expected_gcs_generation=None) -> dict`
- `reconcile_after_preemption(*, ledger_state, live_identity, compute_instance, billing_snapshot, rate_evidence, now_utc) -> dict`
- `mirror_state_generation_checked(*, local_path, gcs_uri, expected_generation, storage_transport=None) -> int`
- `run_controller(config_path) -> int`
- `selftest() -> int`

Also house strict validators for all five schemas below so shell, orchestration, and gate code share one parser without importing scientific projection code.

Dependencies: stdlib plus injectable HTTP/GCS transports. It must not import `f1k_bringup_gate.py`.

Status: **BRING-UP blocker**, because project-wide exposure must be reserved and recorded before the first provisioning mutation.

### Unit 2 — Gate decimal and timing-epoch collection hardening

File:

- `poc/gcp/f1k_bringup_gate.py`

New/refactored functions:

- `_canonical_rate(value, *, code) -> tuple[str, Decimal]`
- `_load_timing_epoch(path) -> dict`
- Replace `_read_results(path)` with `_read_epoch_results(path, *, phase, epoch_id, expected_ids) -> dict`
- `_validate_epoch_result_sets(epoch, t1, t2) -> None`
- Extend `cmd_collect(args)` with required `--epoch`
- Extend `project(...)` to carry the epoch and canonical rate into the GREEN artifact

This unit must not alter sampling, realization, knot building, interpolation, projection arithmetic, Add7 blocks, or frozen constants.

Status: **BRING-UP blocker**.

### Unit 3 — Worker timing epochs, atomic artifacts, ready manifest

File:

- `poc/gcp/f1k_worker.sh`

New shell functions:

- `atomic_publish_file SRC DEST`
- `atomic_publish_json DEST` — delegates JSON validation/writing to `f1k_ops.py`
- `mirror_generation_checked LOCAL URI GENERATION_FILE`
- `read_live_identity_json OUT`
- `begin_timing_epoch SAMPLE_MANIFEST`
- `invalidate_timing_epoch REASON`
- `complete_timing_epoch`
- `write_timing_result PHASE SAMPLE_ID RESULT_TMP`
- `publish_t1_stats SAMPLE_ID STATS_TMP`
- `emit_construction_ready`
- `worker_selftest`

Modify `run_gate_sample` to write one result file per sample instead of appending JSONL. The engine writes T1 stats to a temporary path; the worker fsyncs and renames only after the engine exits successfully and the file is nonempty.

Add two modes:

- Default: normal bring-up/resume.
- `--finalize-ready`: cheap revalidation after runner-confirmed dump checks; emits `construction-ready.json`.
- `--selftest`: local fixture oracle only.

Status: **BRING-UP blocker**.

### Unit 4 — Spot provisioning, full staging, controller activation

File:

- `poc/gcp/f1k_gcp.py`

New/refactored functions:

- `_build_provision_spec() -> dict`
- `_ensure_outer_budget_authority() -> dict`
- `_resolve_control_paths(instance_id) -> dict`
- `_copy_full_payload(bundle) -> dict`
- `_write_full_payload_manifest(bundle) -> dict`
- `_install_controller_unit(identity, paths, rate_evidence) -> None`
- `_verify_controller_unit(identity, paths) -> dict`
- `_bringup_deploy_selftest() -> int`

Modify:

- `cmd_plan`: include outer `$300` exposure/reserve proof.
- `cmd_provision`: reject `KOT_F1K_ONDEMAND`, reserve the create exposure before calling GCP, require the dedicated service account, create/attach durable control PD, require Spot, then install/start/verify the controller.
- `cmd_bringup_deploy`: stage the full tracked construction subset before worker launch; accept `--selftest`.
- `cmd_status`: report controller, ledger head, current exposure, retry count, and timing epoch.
- `cmd_teardown`: close resource intervals before deletion and retain the non-auto-delete control PD until ledger reconciliation is mirrored.
- Retire the current fresh-VM `construction-deploy`; it must not remain a runnable normative path.

After Units 1–4 and their oracles pass, the cheap, spend-safe **BRING-UP is unblocked**. Nothing may cross construction SPEND-START yet.

### Unit 5 — Guard runtime license and cumulative checkpoints

File:

- `poc/gcp/f1k_bringup_gate.py`

New functions:

- `_load_guard_runtime_license(args) -> dict`
- `_acquire_construction_lock(path) -> object`
- `_verify_runtime_budget(runtime_license, *, now_utc) -> dict`
- `_freeze_and_rehash_payload(runtime_license) -> None`
- `_terminate_builder(proc, *, reason) -> None`

Modify:

- `cmd_guard`
- `checkpoint_eval`
- `cmd_checkpoint`
- guard parser: add required `--handoff`

The old guard arguments may remain accepted for compatibility, but values omitted from the CLI are loaded from the ready manifest; any explicitly supplied value must exactly match it. A guard invocation without `--handoff` always refuses before the probe.

`checkpoint_eval` changes from whole-campaign historic-rate scaling to:

`actual cumulative licensed spend + realized ratio × predicted remaining work at live rate + remaining reserve`

Its artifact records prior cumulative hours/dollars, remaining work, gate rate, live rate, remaining reserve, operational exposure, and price-history digest.

Status: required **before the first CONSTRUCTION dollar**.

### Unit 6 — Same-instance `construction-continue`

File:

- `poc/gcp/f1k_gcp.py`

New functions:

- `_load_construction_ready(path) -> dict`
- `_build_construction_handoff(...) -> dict`
- `_publish_handoff_attestation(...) -> dict`
- `_render_systemd_unit(...) -> str`
- `_install_construction_unit(...) -> None`
- `_start_and_verify_construction_unit(...) -> dict`
- `_construction_continue_selftest() -> int`
- `cmd_construction_continue() -> None`

CLI:

- `construction-continue --gate PATH --ready PATH`
- `construction-continue --gate PATH --ready PATH --resume`
- `construction-continue --selftest`

`ENTRY` gains `construction-continue`. The uncommitted fresh-VM `construction-deploy` entry is removed.

Generated runtime units, not new repository files:

- `/etc/systemd/system/kot-f1k-budget-controller.service`
- `/etc/systemd/system/kot-f1k-construction.service`

The construction unit’s direct `ExecStart` is `f1k_bringup_gate.py guard --handoff …`; no shell wrapper and no direct builder invocation.

Status: required **before the first CONSTRUCTION dollar**.

### Unit 7 — Documentation, regression gates, independent review

Files:

- `poc/gcp/README.md`
- `poc/gcp/F1K-CONSTRUCTION-PLAN.md`

Replace the fresh-VM/on-demand sequence, undefined environment placeholders, “single authoritative rate,” compute-only `$300` wording, `$3–3.5 worst case`, and “complete environment” claims. Add the literal canonical paths and exact `construction-continue`/systemd behavior.

Status: runbook review is required before construction; the cheap bring-up may run after Units 1–4 if its own instructions are already accurate.

## 2. JSON contracts

### Common encoding rules

All new manifests use UTF-8, no BOM, lexicographically sorted keys, compact separators, and one trailing newline. SHA fields are 64 lowercase hexadecimal characters. RFC3339 timestamps use UTC `Z`. Monetary values, rates, hours, seconds used for accounting, quantities, and counters are canonical decimal strings—not JSON floats.

Absolute paths must be normalized, symlink-free at the final component, and under the reviewed roots.

Component abbreviations below:

- W: worker
- O: operational controller/helper
- C: `construction-continue`
- G: guard/checkpoint
- P: gate projection/collect

### `construction-ready.json`

Schema: `kot-f1k-construction-ready/1`  
Writer: W, only after engine tests and a complete timing epoch.  
Readers: C, G, O; P reads the timing binding.

| Field | Type | W/R | Contract |
|---|---|---|---|
| `schema` | string literal | W / C,G,O | Exact schema above. |
| `status` | `"READY"` | W / C,G | No provisional value is accepted. |
| `created_at_utc` | RFC3339 string | W / C,G | Informational, not identity. |
| `instance.instance_id` | decimal-digit string | W / C,G | Numeric GCE ID represented as a string to avoid 64-bit JSON precision loss. |
| `instance.name` | string | W / C,G | Informational; never substitutes for ID. |
| `instance.project_id` | string | W / C,G | Must equal live metadata. |
| `instance.project_number` | decimal-digit string | W / C,G | Must equal live metadata. |
| `instance.zone` | string | W / C,G | Short zone name. |
| `instance.machine_type` | string | W / C,G | Must equal `n2d-highmem-8`. |
| `instance.provisioning_model` | `"SPOT"` | W / C,G | Derived from Compute API, not operator input. |
| `instance.last_start_timestamp` | RFC3339 string | W / C,G | Control-plane start identity. |
| `instance.boot_id` | UUID string | W / C,G | `/proc/sys/kernel/random/boot_id`. |
| `timing_epoch.path` | absolute path | W / C,G,P | Exact persisted epoch file. |
| `timing_epoch.epoch_id` | SHA-256 string | W / C,G,P | Must match epoch binding. |
| `timing_epoch.file_sha256` | SHA-256 string | W / C,G,P | Hash of completed epoch bytes. |
| `payload.root` | absolute directory | W / C,G | Canonical `/opt/kot-f1k/repo`. |
| `payload.source_manifest.path/sha256` | path + SHA | W / C,G | Frozen `construction-manifest.jsonl`. |
| `payload.bundle_manifest.path/sha256/file_count` | path + SHA + integer | W / C,G | Complete staged payload manifest; every entry rechecked. |
| `builder.path` | absolute path | W / C,G | Must resolve to `build_carriers.py`. |
| `builder.sha256` | SHA-256 string | W / C,G | Must be the full `a92be3e4…` pin. |
| `builder.argv_base` | array of strings | W / G | Begins with exact builder path, then `construct`; excludes guard-owned engine/tokenizer flags. |
| `engine.argv` | array of strings | W / G | Exact construction-engine argv, including all fixed positional arguments. |
| `engine.executable_path/sha256` | path + SHA | W / G | Tested construction binary. |
| `engine.weights_artifact_path/sha256` | path + SHA | W / G | Exact artifact passed to builder provenance flags. |
| `tokenizer.argv` | array of strings | W / G | Exact wrapper argv, including tokenizer JSON. |
| `tokenizer.artifact_path/sha256` | path + SHA | W / G | Tokenizer JSON bytes. |
| `dump_patch.artifact_path/sha256` | path + SHA | W / G | Exact builder provenance pair. |
| `token_sidecar.path/sha256` | path + SHA | W / G,P | `tokens-full.jsonl`; must equal gate `model_bundle.tokens_full_sha256`. |
| `pin.path/sha256/pin_gb` | path + SHA + positive number | W / C,G | Exact campaign pin and licensed PIN_GB. |
| `launch.layers` | array of integers | W / G | Exactly `3..77`; guard verifies but does not redefine. |
| `launch.environment` | object string→string | W / G | Exact whitelist such as `SNAP`, `TOK_SHA256`, and OMP settings; no ambient placeholders. |
| `paths.rundir` | absolute path | W / G,O | `/var/lib/kot-f1k/run/guard`. |
| `paths.workdir` | absolute path | W / G,O | Reviewed construction checkpoint directory. |
| `paths.out` | absolute path | W / G,O | Reviewed construction output directory. |
| `engine_tests[]` | array of objects | W / C,G | Each has `name`, `path`, `sha256`, and literal `verdict:"PASS"` for KaE, dump a/b/c, functional inertness, and tokenizer/engine agreement evidence. |

### `timing-epoch.json`

Schema: `kot-f1k-timing-epoch/1`  
Writer: W; lifecycle transitions are atomic rewrites.  
Readers: W, P, C, G.

| Field | Type | W/R | Contract |
|---|---|---|---|
| `schema` | literal string | W / P,C,G | Exact schema. |
| `epoch_id` | SHA-256 string | W / P,C,G | SHA of the immutable `binding` object. |
| `generation` | integer ≥1 | W / P | Increases when an epoch is invalidated/restarted. |
| `state` | `OPEN`, `COMPLETE`, or `INVALID` | W / P,C | Only COMPLETE can reach ready/GREEN. |
| `created_at_utc` | timestamp | W / P | Audit field. |
| `retry_index` | integer ≥0 | W,O / P | Initial attempt is 0; retry count is operational. |
| `binding.instance.*` | same identity fields as ready | W / P,C | Binds numeric instance and boot. |
| `binding.sample_manifest.path/sha256` | path + SHA | W / P | Exact immutable sample. |
| `binding.sample_seed` | integer | W / P | Existing `SAMPLE_SEED`; no change. |
| `binding.corpus_sha256` | object filename→SHA | W / P | All four frozen corpora. |
| `binding.tokenizer.*` | path/SHA/argv | W / P | Exact timing tokenizer. |
| `binding.engine.*` | path/SHA/argv | W / P | Exact scoring engine. |
| `binding.weights_artifact.*` | path + SHA | W / P | Exact weights evidence. |
| `binding.omp` | object | W / P | `num_threads`, `dynamic`, `proc_bind`, `wait_policy`, `coli_omp_tuned`. |
| `expected.t1_sample_ids` | array of unique strings | W / P | Exact T1 set. |
| `expected.t2_sample_ids` | array of unique strings | W / P | Exact T2 set. |
| `completed.result_set_sha256` | SHA or null | W / P | Canonical digest of all result records. |
| `completed.pin_sha256` | SHA or null | W / P,C | Present only when COMPLETE. |
| `completed.pin_derivation_sha256` | SHA or null | W / P,C | Exact derivation sidecar. |
| `completed.at_utc` | timestamp or null | W / P | Present only when COMPLETE. |
| `invalidation.reason/at_utc` | strings or null | W,O / P | Required for INVALID. |

Each per-sample result additionally carries `schema`, `epoch_id`, `phase`, `sample_id`, finite positive `s`, `timer_n`, and `pin_evidence`. T1 stats have an atomic metadata sidecar binding `epoch_id`, `sample_id`, and stats SHA. `collect` rejects missing, extra, duplicate, filename/ID disagreement, mixed-epoch, mixed-phase, malformed, or partial sets.

### `construction-handoff.json`

Schema: `kot-f1k-construction-handoff/1`  
Writer: C on the control box, then copied atomically to the durable PD.  
Readers: G, O.

| Field | Type | W/R | Contract |
|---|---|---|---|
| `schema` | literal string | C / G,O | Exact schema. |
| `created_at_utc` | timestamp | C / G,O | Audit. |
| `mode` | `initial` or `resume` | C / G,O | Resume requires prior SPEND-START. |
| `generation` | integer ≥1 | C / G,O | Increases on post-preemption resume. |
| `instance.*` | live identity object | C / G,O | Must match live metadata at guard. |
| `previous_handoff_sha256` | SHA or null | C / G,O | Required for resume. |
| `ready.path/sha256/schema` | path + SHA + schema | C / G | Exact local ready bytes. |
| `gate.path/sha256/schema/verdict` | object | C / G | Exact local GREEN `/2` bytes. |
| `gate.timing_epoch_id` | SHA string | C / G | Must match ready and gate. |
| `rate.usd_per_hour_decimal` | canonical decimal string | C / G,O | Must equal GREEN and live resolver. |
| `rate.evidence_sha256` | SHA string | C / G,O | Exact catalog evidence. |
| `controller.service_name` | string | C / G | `kot-f1k-budget-controller.service`. |
| `controller.heartbeat_path` | absolute path | C / G | Atomic heartbeat. |
| `ledger.path/id/head_seq/head_sha256/gcs_generation` | object | C / G,O | Exact replay point. |
| `lease.path` | absolute path | C / G | Current renewable lease location. |
| `paths.*` | absolute paths | C / G | Must equal ready. |
| `service.exec_argv` | array of strings | C / G | Direct guard argv, normally only `guard --handoff PATH`. |
| `metadata_attestation.attribute` | fixed string | C / G | `kot-f1k-handoff-sha256`. |
| `metadata_attestation.value_rule` | fixed string | C / G | `sha256(exact handoff file bytes)`. |

The metadata value cannot be embedded in the file without a self-hash cycle. C writes the file, computes its SHA, sets that SHA in instance metadata, reads it back, and only then starts guard.

### Durable ledger event

Schema: `kot-f1k-ledger-event/1`  
Writer: the active O controller; control-box recovery may write only after fencing an expired controller.  
Readers: O, G, C, checkpoint logic.

| Field | Type | W/R | Contract |
|---|---|---|---|
| `schema` | literal string | O / O,G,C | Exact schema. |
| `ledger_id` | UUID/string | O / all | Constant across the project ledger. |
| `seq` | integer ≥0 | O / all | Strictly contiguous. |
| `prev_event_sha256` | SHA | O / all | Genesis uses 64 zeroes. |
| `event_sha256` | SHA | O / all | SHA of canonical schema/id/seq/previous/body, excluding this field. |
| `body.event_type` | enum string | O / all | Includes `ledger-created`, `resource-open/close`, `running-open/close`, `charge`, `reserve/release`, `lease-*`, `spend-start`, `checkpoint`, `rate-observed`, `rate-drift`, `reconcile`, `terminal-stop`. |
| `body.occurred_at_utc` | timestamp | O / all | Provider/event time. |
| `body.observed_at_utc` | timestamp | O / all | Controller observation time. |
| `body.controller_id` | string | O / all | Single-writer fencing identity. |
| `body.phase` | enum | O / all | `bringup`, `construction`, `pilot`, `guard`, `main`, `teardown`, `control`. |
| `body.instance` | identity object or null | O / all | Numeric ID and boot binding where applicable. |
| `body.interval` | object or null | O / all | `interval_id`, start/end timestamps, decimal duration seconds, reconciliation state. |
| `body.charge` | object or null | O / all | Service, SKU, resource, unit, decimal quantity/rate/cost, evidence digest. |
| `body.work_class` | enum or null | O / G | `projected`, `overhead`, `preemption-rework`, `other`; drives remaining reserve. |
| `body.rate` | object or null | O / G | Gate rate, live rate, provider-bound rate, evidence SHA. |
| `body.evidence` | object | O / all | Provider resource/version, billing watermark, URI/SHA, GCS generation. |
| `body.counters_after.frozen_licensed` | object | O / G,C | Decimal cumulative construction hours, construction-compute USD, reserve consumed/remaining. |
| `body.counters_after.outer_operational` | object | O / G,C | Gross invoiced USD, accrued-unexported USD, reserved USD, total exposure, and service subtotals. |
| `body.caps` | object | O / G,C | `hours_min=260.6`, `hours_max=900`, `usd_min=73`, `usd_max=155`, `operational_usd_max=300`, reserve 8. |
| `body.open_intervals` | array of IDs | O / O,G | Replay must reproduce exactly. |

The outer total is:

`gross invoiced through billing watermark + locally accrued after watermark + unobserved/reserved exposure`

Credits and promotional balances do not reduce it.

### Spend lease

Schema: `kot-f1k-spend-lease/1`  
Writer: O.  
Readers: G, C, O.

| Field | Type | W/R | Contract |
|---|---|---|---|
| `schema` | literal string | O / G,C,O | Exact schema. |
| `lease_id` | UUID/string | O / G,C | Stable across renewals or replaced with a chained successor. |
| `generation` | integer ≥1 | O / G,C | Increases on every renewal. |
| `status` | `ACTIVE` or `EXPIRED` | O / G,C | Only ACTIVE licenses spend. |
| `issued_at_utc/not_before_utc/expires_at_utc` | timestamps | O / G | Default duration 21,600 seconds. |
| `previous_lease_sha256` | SHA or null | O / G,O | Renewal chain. |
| `lease_sha256` | SHA | O / G,C | Canonical body hash excluding this field. |
| `controller.id/boot_id` | strings | O / G | Must match heartbeat. |
| `controller.heartbeat_sequence/sha256/max_age_seconds` | object | O / G | Recommended heartbeat 60 s; stale after 180 s. |
| `authorization.handoff_sha256` | SHA | O / G | Exact current handoff. |
| `authorization.gate_sha256/ready_sha256` | SHAs | O / G | Exact licensed bytes. |
| `authorization.instance` | identity object | O / G | Includes current boot. |
| `authorization.allowed_phase` | enum | O / G | No cross-phase use. |
| `ledger.id/head_seq/head_sha256` | object | O / G | Lease is invalid if ledger advances incompatibly or rolls back. |
| `rate.license_decimal/live_decimal/upper_bound_decimal` | decimal strings | O / G | Live must equal license; upper bound reserves unobserved exposure. |
| `rate.evidence_sha256` | SHA | O / G | Current quote evidence. |
| `reservation.frozen_hours_decimal` | decimal string | O / G | Maximum licensed interval exposure. |
| `reservation.frozen_compute_usd_decimal` | decimal string | O / G | Reserved against `$155`. |
| `reservation.outer_operational_usd_decimal` | decimal string | O / G | Reserved against `$300`, including non-compute allowances. |
| `caps_remaining.*` | decimal strings | O / G | Post-reservation remaining amounts. |
| `expired.reason/at_utc` | strings or null | O / G | Required when EXPIRED. |

Renew at one hour remaining, but only while heartbeat, quote, ledger, metadata, and both caps are healthy. Guard kills the builder at the first poll where heartbeat is stale, lease is expired, rate differs, or either ledger is invalid.

## 3. Durable operational behavior

Canonical durable locations:

- Guest control PD: `/var/lib/kot-f1k/`
- Payload: `/opt/kot-f1k/repo/`
- Scratch/work/output: `/mnt/nvme/kot-f1k/`
- Control-box mirror: `${XDG_STATE_HOME:-$HOME/.local/state}/kot/f1k/<project>/<instance-id>/`
- GCS mirror: `gs://$KOT_F1K_BUCKET/f1k/control/<project>/<instance-id>/`

Ledger, lease, heartbeat, ready, epoch, gate, and handoff live on the control PD and are mirrored to the control box and GCS. GCS updates use generation preconditions.

Append order is local append → file fsync → directory fsync → GCS compare-and-swap → local head/generation fsync. Recovery permits one mirror to be an exact prefix of another. Non-prefix divergence, a sequence gap, hash failure, or older unexpected GCS generation is terminal.

After preemption:

1. Replay and compare PD, control-box, and GCS chains.
2. Query the same numeric instance through `instances.get`.
3. Close an open RUNNING interval at `lastStopTimestamp`; open the new interval at `lastStartTimestamp`.
4. Price the closed interval using the maximum evidenced rate applicable to the interval.
5. If stop/start timestamps are absent or inconsistent, conservatively close at the new start using the upper-bound rate and refuse a new lease pending control-box reconciliation.
6. Append the reconciliation event before issuing any new lease.

Before SPEND-START, a changed boot invalidates timing, ready, GREEN, and handoff. After SPEND-START, the same numeric instance may receive a new `mode:"resume"` handoff for its new boot only after ledger reconciliation and full artifact/provenance revalidation; timing is not repeated.

## 4. Exact guard pre-spend order

`cmd_guard` must perform these checks before reset consumption, engagement probe, or any engine start:

1. Require `--handoff`; read exact handoff bytes, validate schema, hash them, and require the live instance metadata attribute `kot-f1k-handoff-sha256` to equal that hash.
2. Resolve live numeric instance ID, project, zone, machine type, `lastStartTimestamp`, and boot ID; require exact equality with the handoff.
3. Call Compute Engine `instances.get` and require `scheduling.provisioningModel == "SPOT"`; the metadata `preemptible` bit is corroborating evidence only.
4. Resolve the current all-in Spot rate and require canonical equality with `gate.rate.usd_per_hour_decimal`; quote failure is a refusal.
5. Hash the local gate bytes against the handoff; require schema `/2` and verdict `GREEN`.
6. Hash and validate ready bytes; require handoff, ready, gate, and timing epoch to form one binding.
7. Run the existing pin/PIN_GB and Add7 verification unchanged.
8. Require `sha256(args.tokens) == gate.model_bundle.tokens_full_sha256`.
9. Resolve the builder path without symlinks; require basename `build_carriers.py`, SHA `a92be3e4…`, first builder subcommand `construct`, and no alternate program/interpreter seam.
10. Require engine/tokenizer argv and every provenance path/SHA pair to equal ready; rehash the artifact bytes.
11. Verify the complete source/bundle manifest, file count, path containment, file modes, and all payload hashes.
12. Require rundir/workdir/out to equal ready; acquire the exclusive run lock and refuse contention.
13. Replay ledgers; require an active lease, fresh controller heartbeat, matching ledger head, cumulative frozen counters below 900 h/$155, and outer exposure below `$300`.
14. Make the payload/provenance tree non-writable and perform a final rehash of handoff, gate, ready, builder, tokens, pin, provenance artifacts, metadata attestation, live rate, ledger head, and lease.
15. Only now evaluate/consume any authorized reset, durably append SPEND-START immediately before the probe, run the engagement probe, and execute the validated absolute builder path.

Guard uses the metadata server for local identity and the attached service-account token for Compute `instances.get` and Catalog API calls. Provision with the `cloud-platform` scope and restrict the dedicated service account through IAM; Google recommends that combination over coarse access-scope authorization. [Google Cloud service-account guidance](https://docs.cloud.google.com/compute/docs/access/service-accounts)

The guest service account must not have `compute.instances.setMetadata`; only the control box writes the attestation.

## 5. Per-unit `$0` oracle plan

### Unit 1 oracle

Refuse:

- NaN/Infinity/nonpositive decimals; malformed exponent; precision loss.
- Missing/malformed metadata, recreated same-name VM, STANDARD scheduling.
- Missing/foreign attestation.
- Missing/duplicate/wrong-region/wrong-usage-type price SKUs.
- Quote outage or stale evidence.
- Ledger hash failure, sequence gap, rollback, divergent GCS generation, non-finite counter, double-counted billing watermark.
- Missing/expired lease, stale heartbeat, wrong boot/handoff/head.
- Exact 900 h, `$155`, and `$300` boundary overages.

Happy path:

- `0.190` and `1.90e-1` canonicalize to `0.19`.
- `0.10000000000000001` remains exact.
- Exact component-rate sum.
- Attestation write/read through fake Compute and metadata transports.
- Issue→renew→expire lease chain.
- Replay and deterministic preemption reconciliation.
- Project-total arithmetic includes compute, SSD, PD, GCS, operations, logging, and network categories.

### Unit 2 oracle

Extend the existing gate selftest:

- Preserve the original decimal string without a float round-trip.
- Verify canonical field propagation into gate input and GREEN artifacts.
- Reject duplicate, extra, missing, mixed-epoch, wrong-phase, and filename/ID-conflicting results.
- Reject a changed boot/sample/corpus/engine/OMP binding.
- Prove the existing float field can be lossy without authorizing equality.
- Retain every existing projection and scientific oracle result.

### Unit 3 oracle

`bash f1k_worker.sh --selftest` uses mock files only:

- Atomic publish leaves either old complete bytes or new complete bytes after injected interruption.
- No JSONL append or partial stats file can be consumed.
- Preemption invalidates the complete T1→pin→T2 sequence.
- Empty/malformed/mixed-epoch stats refuse.
- Ready refuses pending dump checks, relative/symlink paths, mutated builder, missing argv/env, or incomplete manifest.
- Happy path emits a COMPLETE epoch and deterministic READY manifest.

Also run `bash -n`.

### Unit 4 oracle

`bringup-deploy --selftest` renders plans only:

- Refuse `KOT_F1K_ONDEMAND`, STANDARD, wrong machine/zone, missing service account, absent control PD, fourth failed retry beyond policy, missing payload files, manifest drift, controller inactive, or stale heartbeat.
- Happy plan contains Spot, cloud-platform scope, durable PD, the full builder/driver/data payload, and controller start/verification.
- No `gcloud`, SSH, GCS, VM, or network operation occurs.

### Unit 5 oracle

For each ordered guard check, inject one failure and prove:

- Exit is before reset consumption.
- No probe evidence exists.
- No stub builder was started.
- No SPEND-START event exists.

Cases include copied bundle, recreated same-name VM, wrong boot, STANDARD scheduling, quote outage, rate drift, mutated gate/ready/pin/token/builder/artifact, wrong argv, incomplete manifest, path substitution, lock contention, expired lease, stale heartbeat, ledger corruption/rollback, and both cap boundaries.

Add a TOCTOU case mutating bytes between the first verification and the final barrier. Happy path uses stub engine/builder and exact handoff. Checkpoint fixtures prove cumulative-prior plus remaining-work arithmetic and live-rate repricing.

### Unit 6 oracle

`construction-continue --selftest` uses fake GCP/systemd transports:

- Refuse wrong numeric ID, changed pre-spend boot, mismatched ready/GREEN epoch, stale rate, GCS generation divergence, failed attestation readback, inactive controller, or insufficient lease reservation.
- Allow post-SPEND-START boot change only with the same numeric instance and reconciled ledger.
- Prove exact handoff bytes, metadata SHA, and direct systemd guard argv.
- Prove idempotent replay does not start a second guard.

### Required reviews

- Launch/TOCTOU reviewer: direct guard, copied bundle, recreated name, STANDARD, artifact mutations, forged/stale manifests, undefined paths, quote failure, post-stage and post-first-hash changes.
- Budget/preemption reviewer: preemption around T1, pin, T2, handoff, probe, every checkpoint, final tail; controller restart; ledger corruption/rollback; rate drift; quote outage; exact 900/$155/$300 arithmetic.
- Runbook reviewer: execute fixture-backed commands from fresh Spot planning through exact guard argv, then dry-parse the real `build_carriers.py` argparse surface without construction.

At least two independent model ACCEPTs, no blocker or unresolved disagreement, existing gate selftest, builder selftest, driver oracles, module/shell checks, and the unchanged builder SHA are required.

## 6. Ambiguities and recommended decisions

- **Live rate source:** Use Cloud Billing Catalog REST `services.skus.list`, not an operator environment variable or scraped pricing page. The API’s latest data can be up to 12 hours old, so preserve the full evidence and use a separate upper-bound reservation. [Catalog API](https://docs.cloud.google.com/billing/docs/reference/rest/v1/services.skus/list)
- **All-in construction rate:** Define it as Spot N2D vCPU + Spot N2D RAM + two Spot Local SSD hourly SKUs for `us-central1`, using exact catalog quantities. Boot/control PD, GCS, operations, logs, and network remain outer-operational only.
- **Rate volatility:** Spot prices can change daily. Poll every controller/guard cycle, append only new evidence digests, and terminal-stop on canonical drift. [Spot pricing behavior](https://docs.cloud.google.com/compute/docs/instances/spot)
- **Invoice-exact `$300`:** GCP billing exports have variable reporting delay and no delivery guarantee, so they cannot enforce a real-time hard cap alone. Use a dedicated F1-K project, prohibit unrelated resource writers/services, track local accrued exposure conservatively, and reconcile against detailed billing export. [Billing export latency](https://docs.cloud.google.com/billing/docs/how-to/export-data-bigquery-tables)
- **`$300` basis:** Use gross project cost before credits/refunds. Credits must not enlarge the license.
- **Service account:** Dedicated account, `cloud-platform` scope, custom `compute.instances.get`, bucket-scoped object CAS permissions, and only the minimum billing/export read permissions. No metadata-write or instance-admin permission.
- **Attestation location:** Instance-level custom metadata key `kot-f1k-handoff-sha256`, written with metadata-fingerprint CAS by the control box. Do not use guest attributes; any process in the guest can write those. [Guest-attribute warning](https://cloud.google.com/compute/docs/metadata/manage-guest-attributes)
- **Boot identity:** Bind both `/proc/sys/kernel/random/boot_id` and Compute `lastStartTimestamp`. Numeric instance ID alone does not distinguish a preemption boot.
- **Controller/process manager:** Use systemd, not nohup. Controller uses `Restart=always`; construction uses an enabled unit with `RestartPreventExitStatus=2`, direct guard `ExecStart`, controller dependency, and no automatic restart after a policy refusal.
- **Retry interpretation:** Treat the maintainer’s “retry ≤3×” as three retries after the initial attempt—four attempts maximum—and surface before a fifth. Record every attempt in the outer ledger.
- **Six-hour leases:** Use 21,600 seconds, renew with one hour remaining, heartbeat every 60 seconds, stale after 180 seconds. Lease expiry has no grace.
- **Local-SSD construction checkpoints:** Local SSD is not durable enough for post-preemption continuation. Mirror each completed, parseable, SHA-bound concept checkpoint to GCS with create/generation preconditions and restore it before a resume handoff; keep this in controller-side operational code, not the builder.
- **Ready timing:** Emit final READY only after runner-confirmed dump a/c, recollect, a COMPLETE epoch, and all PASS evidence. No provisional READY file should exist.
- **Construction SPEND-START:** The engagement probe is the first construction spend. Append SPEND-START after all checks/reset consumption and immediately before that probe.

### Six-line handoff

- One Spot instance spans bring-up, GREEN, and initial construction launch.
- Units 1–4 unblock spend-safe bring-up; Units 5–7 are mandatory before construction.
- READY, epoch, handoff, ledger, and lease are exact-byte/hash-bound contracts.
- `$155` remains the construction-compute controller; `$300` covers every project service.
- Guard alone crosses SPEND-START and launches the frozen `a92be3e4` builder.
- Recommended first code round: implement `poc/gcp/f1k_ops.py` plus its pure `$0` selftest.