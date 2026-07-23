<!-- Provenance: Fable (architecture-advisor), 2026-07-23, bead kernel-of-truth-700k
     (+ folds in kernel-of-truth-wonu). REVISION 2 (same date): incorporates the
     GPT-5.6 spend-safety review REJECT
     (poc/gpt56-review/f1k-cc-transition-review/last-message.json) — all 5 blocking
     defects + all engineering corrections; several fixes amend the LANDED option-B
     module (flagged in the LC register, section R2.7). Design/spec ONLY: nothing here
     is committed as executed work, deployed, or run by the author. The coordinator's
     executor builds this and a cross-vendor (GPT-5.6) review gate runs BEFORE any
     construction dollar. Supersedes-in-part: the plan-v4 REJECT's #3 staging
     characterization (stale; see section 1) AND the side-plan guard step 3 (replaced;
     see R2.4). Defers-to: poc/gcp/F1K-CONSTRUCTION-SIDE-PLAN.md sections 2-3
     (handoff schema + guard order, as amended by R2.4). -->

<!-- REV2 READING ORDER: sections 1-10 are the Rev1 body with in-place corrections
     marked "(Rev2)"; section "Revision 2" holds the defect-by-defect dispositions,
     the hard-cap architecture, and the landed-code change register. Where the body
     and the Revision 2 section conflict, Revision 2 governs. -->

<!-- REVISION 3 (2026-07-23, after the GPT-5.6 Rev2 delta-check NEW-DEFECT/
     STILL-REJECT, poc/gpt56-review/f1k-cc-rev2-deltacheck/last-message.json):
     resolves the cap-mechanism fork (PROPOSED-CC-7) from GCP documentation — the
     hard cap becomes the NATIVE GCE absolute runtime limit (terminationTime) with
     the unified STOP action, which coexists with Spot preemption-resume and
     eliminates the Scheduler/OIDC/async/cron defect family outright. Section
     "Revision 3" governs over both earlier layers wherever they conflict; R2.1's
     Cloud Scheduler L1 is SUPERSEDED. -->

# F1-K `construction-continue` transition — implementable design

Bead `kernel-of-truth-700k`: the runnable, guarded, NO-SPEND transition from a GREEN
bring-up verdict to guard-wrapped Spot construction on the SAME GCE instance
(Single-VM-Spot, `poc/gcp/F1K-CONSTRUCTION-LAUNCH-ARCH.md`). This document is the
build spec for the executor; the paid construction RUN remains separately gated on the
maintainer spend-GO (issue #55) and is out of scope here.

Scope choice (a STIPULATED design choice, PROPOSED-CC-1 as REVISED in Rev2; the
executor registers it as an ASM at commit): this design targets the lean-B contract
schemas frozen in `poc/gcp/f1k_ops.py` (`kot-f1k-construction-ready/1`,
`kot-f1k-bringup-gate/2`, `kot-f1k-construction-handoff/1`,
`kot-f1k-runtime-license/1`, `kot-f1k-rate-evidence/1`) and changes NO scientific
pin, frozen window, sampling rule, or builder byte. Rev1's stronger claim ("changes
no landed validator") is WITHDRAWN: the spend-safety review found genuine defects in
the landed option-B units themselves, so Rev2 specifies a bounded set of landed-code
amendments (the LC register, section R2.7) — exactly the "contract edit re-enters
review only if a genuine defect is found" clause firing. Every LC item requires
re-verification and fresh oracle cases before any provision.

---

## 1. Reconciled ground state (what exists, what is missing)

LOAD-BEARING: [MEASURED: repo read 2026-07-23, poc/gcp/f1k_gcp.py:169-246 + :843-853 at commit 96c3a204]
the landed `bringup-deploy` ALREADY stages the full reviewed
construction payload on the VM — `_construction_payload_files()` requires
`build_carriers.py`, `f1k_driver.py`, `tok_glm52.py`, `analysis/f1k.py`,
`registry/*`, `tools/registry`, `data/f1k-eval-v1`, `data/f1k-trigger-map-v1`, and the
harness mocks, sha-verifies `build_carriers.py` against `a92be3e4...` before staging,
and copies the subset under `~/f1k/poc/...` (payload resolver `:169-246`, call `:742`,
pin check + copy `:843-853`; corroborated by `poc/gcp/F1K-CONSTRUCTION-PLAN.md`
section 7 step 2 "LANDED").
The plan-v4 REJECT's #3 statement that `bringup-deploy` stages only the bring-up
harness was written against the pre-B code and is stale on that sub-point. Its
load-bearing core stands: there is still NO runnable path from GREEN to guarded
construction.

LOAD-BEARING: [MEASURED: repo read 2026-07-23 of poc/gcp/f1k_gcp.py + f1k_ops.py + f1k_bringup_gate.py at 153b9576]
the concrete missing pieces are exactly five:

1. No `construction-continue` in the entry map — `ENTRY` holds only
   `plan|provision|status|teardown|affordability|gate|bringup-deploy|watchdog|pin-fetch`
   (`poc/gcp/f1k_gcp.py:989-995`).
2. `f1k_gcp.py` never imports `f1k_ops` — `preflight_launch_gate` (B5,
   `poc/gcp/f1k_ops.py:5434`) is wired into NO launch path (grep this pass: the only
   `f1k_ops` references in `f1k_gcp.py` are staging-list strings).
3. No producer exists for `construction-handoff.json`; the only populated instance of
   `provider.instance_termination_action` is the selftest fixture
   (`poc/gcp/f1k_ops.py:3827`) — the bead-wonu contract slot is unfilled.
4. `cmd_guard` has no `--handoff` mode — its CLI is still
   `--gate/--pin/--engine-cmd/--tokenizer-cmd/--layers/--tokens/--rundir/--workdir --
   <builder argv>` (`poc/gcp/f1k_bringup_gate.py:1374-1387`), while the frozen license
   contract REQUIRES `service.exec_argv = [interpreter, <payload>/f1k_bringup_gate.py,
   guard, --handoff, /home/ubuntu/f1k-gate/construction-handoff.json]`
   (`poc/gcp/f1k_ops.py:3319-3337`).
5. No rate-equality enforcement anywhere between the collect-frozen gate rate and the
   live construction rate at deploy time; B4 checks the live rate against the frozen
   WINDOW only (`guard_rate_within_window`, `poc/gcp/f1k_ops.py:5389`), not equality
   with the licensed rate.

PREMISE: [MEASURED: commits 153b9576 + 96c3a204; oracles 11/11, 14/14, 69/69, 23/23 per the bead-700k milestone record]
the bring-up-side B stack (provision SPOT-only, bringup-deploy staging,
worker + READY writer, gate `/2`, `f1k_ops` option-B units B1-B5) is landed and
review-clean. Scope caveat: the oracle counts are cited from the bead
kernel-of-truth-700k milestone note and `F1K-CONSTRUCTION-PLAN.md` section 7, not
re-run by this author this pass — the executor re-runs all four before building on
them.

### 1.1 Two latent false-refuse seams this design must close (found this pass)

Seam W-USER. The frozen canonical artifact paths pin `/home/ubuntu/f1k-gate/...` and
`validate_handoff` requires `service.user == "ubuntu"`
[MEASURED: `poc/gcp/f1k_ops.py:69-77`, `:3125`], but every landed SSH/SCP call uses
`gcloud compute ssh INSTANCE_NAME` with no user override
[MEASURED: `poc/gcp/f1k_gcp.py:796,863,873,915`], which logs in as the CONTROL-BOX
username, not `ubuntu` — so on a real run the worker's `$HOME` would not be
`/home/ubuntu`, READY would land at a non-canonical path, and `validate_handoff` would
correctly refuse a legitimate launch (fail-closed strand, the exact hazard class bead
wonu warns about). Chosen wiring: every `gcloud compute ssh`/`scp` in `f1k_gcp.py`
(bringup-deploy remote prep, bundle scp, launch, watchdog probe, and the new
construction-continue) explicitly targets `ubuntu@<instance>` so `$HOME` is
`/home/ubuntu` on the Ubuntu image everywhere [STIPULATED design choice
PROPOSED-CC-2; the ubuntu-2204-lts image ships the `ubuntu` user; verified mechanically
by the new preflight step "remote `echo $HOME` == `/home/ubuntu`" which refuses
before any bring-up spend, so a wrong image/user fails at $0].

Seam ARMED-899. `preflight_launch_gate` requires `deadline == persisted-epoch-launch +
exactly 900 h` [MEASURED: `poc/gcp/f1k_ops.py:5444-5480`], while `validate_handoff`
caps `armed_hours_decimal <= 899` [MEASURED: `:3013-3023`]. These are consistent ONLY
if `campaign_started_at_utc` (construction start) is at least 1 h after the epoch
(VM creation): `armed_hours = hours(termination_time - campaign_started_at) =
900 - elapsed_bringup`. Bring-up (estate restore + build + timing) takes many hours in
practice, so the constraint is naturally satisfied; the producer still checks it and
refuses with `ERR_F1K_CONTINUE_ENVELOPE` if `armed_hours > 899` (fail-closed, never
fudged) rather than silently clamping.

---

## 2. The `construction-continue` entrypoint

New `f1k_gcp.py` subcommand, control-box initiated (consistent with all existing
orchestration), plus `construction-continue --selftest` (the $0 oracle, section 6).

```
python3 poc/gcp/f1k_gcp.py construction-continue \
  --gate  ./gate-pull/bringup-gate.json \
  --ready ./gate-pull/f1k-gate/construction-ready.json
```

Preconditions (all fail-closed, checked in phase 0 before ANY mutation):

- a GREEN `/2` gate artifact produced by `cmd_gate` from the FINAL re-collected
  gate-inputs (the runner's on-box (a)/(c) confirm + re-collect already happened —
  section 7.1);
- `construction-ready.json` pulled from the SAME live instance;
- the live instance IS the READY instance (numeric ID, boot_id, zone, machine type,
  provisioning model SPOT, lastStartTimestamp);
- env: `KOT_F1K_BUCKET`, `KOT_GCP_PROJECT`, `KOT_GCP_BILLING_ACCOUNT` (new, for B3)
  set; unset refuses.

### 2.1 Phase order (normative; the oracle asserts this order)

Phase 0 — pure checks, $0, no mutation anywhere:

1. Parse + strictly validate gate (`validate_gate`) and READY (`validate_ready`) and
   their binding (`validate_ready_gate_binding`) via `f1k_ops` (first real import of
   `f1k_ops` into `f1k_gcp.py`).
2. `verdict == "GREEN"`, `schema == kot-f1k-bringup-gate/2` (already enforced by
   `validate_gate`; re-stated as the entrypoint's named precondition).
3. Resolve live instance identity (`resolve_live_instance_identity` with the
   gcloud/SSH transports); require equality with `ready["instance"]` on every field,
   including `boot_id` — a preemption between READY and continue changes the boot id
   and correctly refuses (remedy: re-finalize READY on the current boot, re-gate).
4. RATE-EQUALITY GATE (section 3): live rate canonically equals the collect-frozen
   gate rate; NO-GO on mismatch or quote failure.
5. Wall-clock sufficiency (Rev2-hardened, R2.6-WC): `remaining_h = 900 -
   elapsed_hours(epoch)` must be `>=` the gate's +1SE projected instance-hours plus
   reserve-hours plus the transition/termination margin, with the projection values
   extracted from the RAW gate JSON via `parse_float=str` (no binary-float
   pass-through) and all arithmetic ROUND_CEILING; refuse `ERR_F1K_CONTINUE_WALLCLOCK`
   otherwise — never launch a run the 900 h cap is already guaranteed to kill
   [STIPULATED policy PROPOSED-CC-3 + PROPOSED-CC-9 (2 h margin): +1SE branch chosen
   as the conservative bound; a refusal here is a maintainer surface, not a retry].
   This phase-0 check is a pre-filter only: the guard RECOMPUTES it with a fresh
   clock immediately before engine start and re-checks projected completion against
   the absolute deadline minus margin at every checkpoint (R2.4).
6. Single-shot: refuse `ERR_F1K_CONTINUE_ALREADY` if
   `/home/ubuntu/f1k-gate/construction-handoff.json` exists on the VM, or the guard
   rundir's `construction-events.jsonl` is non-empty. A second attempt is an explicit
   operator/maintainer decision, never an automatic relaunch.
7. Watchdog interlock: refuse `ERR_F1K_CONTINUE_WATCHDOG` if a
   `f1k_gcp.py watchdog` process is alive on the control box (`pgrep -f`). The
   bring-up watchdog's teardown authority MUST be retired before construction, or its
   `--max-hours` deadline deletes a licensed run mid-flight (section 7.1).
8. Harness-version pin: sha256 of the ON-VM `~/f1k/f1k_bringup_gate.py` and
   `~/f1k/f1k_ops.py` must equal the control-box repo bytes. Refuse
   `ERR_F1K_CONTINUE_HARNESS_DRIFT` on mismatch. Continue NEVER re-pushes payload
   files — READY byte-binds the bundle manifest, so a re-push would invalidate the
   license by construction. Build-order corollary: the guard `--handoff` delta
   (section 5) MUST be landed BEFORE the bring-up that produces READY is deployed.
9. Remote-home check: `ssh ubuntu@<vm> 'echo $HOME'` returns `/home/ubuntu`
   (seam W-USER).

Phase 1 — VM mutation, still $0 exposure risk:

10. Materialize the B1 epoch VM-local cache at `/home/ubuntu/f1k-gate/launch-epoch.json`
    from the GCS mirror. (Rev2) In the launch context the MIRROR is mandatory:
    a mirror object that is absent while a local copy exists REFUSES
    (`require_mirror` semantics, LC-12) — mirror loss is a durability failure, not a
    fallback. The epoch itself is written ONCE at provision time, CAPTURED BEFORE the
    create request (section 4.1, Rev2/R2.5).
11. Render + install the Rev2-HARDENED L2 guest units (LC-1: extended retry loop,
    `Restart=on-failure`, terminal no-auth `poweroff -f` fallback) with
    `deadline = compute_selfdelete_deadline(epoch)`, `systemctl daemon-reload`,
    enable + start the timer. Idempotent: identical unit text re-install is a no-op;
    differing text refuses. (Rev2) The guest units are DEFENSE-IN-DEPTH ONLY; the
    hard cap is the provider-side L1 delete job armed at PROVISION time (R2.1).

Phase 2 — the single pre-spend gate:

12. `preflight_launch_gate` (section 4, as amended by LC-7; Rev3 R3.1) with real
    transports: B1 epoch + derived deadline; L1 NATIVE cap read-back — live
    `instances.get` scheduling: `terminationTime == epoch + 900 h`,
    `instanceTerminationAction == STOP`, `provisioningModel == SPOT`,
    discard-local-SSD-at-termination set (LC-3v3); hardened L2 guest-timer
    verification (LC-2); guest-side deletion-IAM dry-run (`testIamPermissions`
    including `compute.instances.delete`, executed FROM the VM with its own
    credentials — proves auth + API reachability + permission end-to-end without
    deleting, LC-4; under Rev3 this backs the CLEANUP/teardown layer, not the hard
    cap); exact-budget-resource attestation (LC-6, Rev3-extended per R3.3); and the
    B4 rate window. `go: false` refuses and STOPS — deliberately leaving every cap
    layer armed (an armed cap on a VM we are keeping is conservative, and
    `teardown` remains available).

Phase 3 — artifact placement (atomic, sha-read-back):

13. Write `live-rate-evidence.json` (canonical bytes from the SAME
    `resolve_live_rate` evidence used by the equality gate, re-checked for
    three-way canonical equality gate == preflight == evidence), scp to
    `/home/ubuntu/f1k-gate/live-rate-evidence.json`, read back sha.
14. Scp the GREEN gate artifact to `/home/ubuntu/f1k-gate/bringup-gate.json`
    (atomic: temp name + `mv`), read back sha == local sha.

Phase 4 — backstop swap (ordering is the point):

15. ONLY after preflight verified the FULL cap stack — L1 native runtime limit,
    hardened L2 guest units, AND the guest-side deletion-IAM dry-run — AND after an
    immediate re-probe of BOTH layers (Rev3, delta-check #4: a fresh L1
    `instances.get` scheduling read-back AND the L2 `is-active` query, run
    immediately before the cancel; if the runtime limit has been patched/removed or
    the timer disarmed since preflight, do NOT cancel — oracle groups 25 + 31):
    cancel the bring-up guest max-life (`sudo shutdown -c`). Order recorded in the
    continue transcript; the oracle asserts verify-before-cancel (this is
    F1K-CONSTRUCTION-LAUNCH-ARCH's "cancel the bring-up shutdown only after the
    provider delete is verified", now implemented with a provider-NATIVE cap,
    R3.1).

Phase 5 — handoff production (section 4.2 for the provider block):

16. Build `construction-handoff.json` per the contract (as amended by LC-8);
    self-validate with `validate_handoff` AND `build_runtime_license(ready, gate,
    handoff)` locally — a handoff the guard would refuse is never uploaded.
    Atomic-write locally, scp to `/home/ubuntu/f1k-gate/construction-handoff.json`,
    read back sha. (Rev2, R2.6-#8) In the same phase, produce
    `prior-spend-evidence.json` (`kot-f1k-prior-spend/1`): epoch launch,
    `campaign_started_at_utc`, bring-up elapsed hours (ROUND_CEILING 6 dp), the
    licensed rate, and `bringup_cost_usd_decimal = elapsed x rate` (ROUND_CEILING) —
    written to `/home/ubuntu/f1k-gate/` and kept on the control box; its sha is in
    the continue receipt. (Rev3, delta-check #5) Consumption is MECHANICAL, not a
    runbook promise: LC-13 amends `cmd_config_cost`
    (`poc/gcp/f1k_bringup_gate.py:1787`) to REQUIRE `--prior-evidence <path>`,
    validate its schema/sha/arithmetic/instance binding, DERIVE the prior
    dollars/hours from it, and REFUSE the manual `--prior-usd`/`--prior-hours`
    flags outright (any supplied value, including zero, is a hard error). Bring-up
    spend is thereby BOUND as evidence with an enforcing consumer.

Phase 6 — guard launch via systemd (guard remains the SOLE builder launcher):

17. Install `kot-f1k-construction.service` with `ExecStart` exactly equal to
    `service.exec_argv` from the handoff, `User=ubuntu`, `Restart=no`, NOT enabled on
    boot; `daemon-reload`; `systemctl start`.
18. Verify `ActiveState=active`, `MainPID > 0`, and `systemctl show -p ExecStart`
    parses to exactly `service.exec_argv`. Print the handoff sha + unit status as the
    continue receipt. The guard then re-verifies the complete live license itself
    before any reset consumption, probe, or engine start (section 5) — continue's
    checks are a pre-filter, never the spend authority.

Failure semantics: every refusal exits 2 with a stable `ERR_F1K_CONTINUE_*` code and
mutates nothing further; phases are ordered so that every abort point leaves the VM in
a strictly-safer-or-equal state (backstops armed, no spend process started).

---

## 3. The rate-equality gate (plan-v4 #4)

PREMISE: [MEASURED: repo read 2026-07-23, poc/gcp/f1k_bringup_gate.py:623-650 + :889-906 + :1062-1064 at 96c3a204]
the collect-frozen rate is `rate.usd_per_hour_decimal` in the `/2` gate
artifact — collect canonicalizes the operator's `KOT_F1K_SPOT_RATE` string through
`f1k_ops.canonical_decimal` (`:623-650`), the artifact carries the float field
explicitly demoted to a derived compatibility value, `project` re-derives and refuses
inequality (`:889-906`), and the artifact self-describes the decimal field as "the
authoritative licensing comparison" (`:1062-1064`).

Specification:

- Comparison: `Decimal(canonical_decimal(live_rate)) ==
  Decimal(canonical_decimal(gate.rate.usd_per_hour_decimal))` — equivalently, string
  equality of the two canonical forms, since `canonical_decimal` is a normalizing
  pure function (exponent-free, trailing zeros stripped: `"0.190"` -> `"0.19"`;
  binary floats REFUSED as inputs) [MEASURED: `poc/gcp/f1k_ops.py:95-145`].
- Tolerance: ZERO. Exact canonical equality. Round-trip safety comes from
  canonicalization, not from a tolerance band: no float ever enters the comparison,
  so the `0.10000000000000001` defect class (the prior Decimal-round-trip finding,
  F1K-CONSTRUCTION-LAUNCH-ARCH finding 1) cannot false-refuse. A tolerance band
  would instead silently license a rate the gate never priced.
- Live side: `resolve_live_rate(project, zone, machine_type=n2d-highmem-8,
  local_ssd_count=2)` — the all-in three-component quote with its evidence record
  (`kot-f1k-rate-evidence/1`).
- On mismatch: NO-GO, `ERR_F1K_CONTINUE_RATE_DRIFT`, printing both canonical values
  and the REMEDY: on-box re-run of `collect` with the new rate (collect consumes the
  existing atomic T1/T2 files — NO re-timing) + control-box `gate` re-run. A rate
  change therefore costs one $0 re-license, never a stranded GREEN and never a
  stale-rate checkpoint basis.
- On quote outage: NO-GO, `ERR_F1K_CONTINUE_RATE_QUOTE` (normalized by
  `guard_rate_within_window`'s existing fail-closed wrapper).
- Where enforced: (a) continue phase 0 step 4; (b) three-way re-check at phase 3
  (evidence write); (c) the guard's own pre-spend step and per-poll rate sentry
  (section 5) — so drift between continue and spend, or during the campaign, also
  kills fail-closed. The window check (B4) is retained IN ADDITION via preflight;
  equality does not subsume the window because the frozen window is the licensed
  envelope, equality is licence-identity.

---

## 4. `preflight_launch_gate` wiring + the wonu termination-action fix

### 4.1 Wiring

Wiring choice (a STIPULATED design choice, PROPOSED-CC-4): `preflight_launch_gate`
runs ON THE CONTROL BOX inside `construction-continue` phase 2, with injected
transports — the function is transport-injected precisely so it can run where the
operator's credentials live; an on-VM runner would need budget/catalog IAM on the VM
service account for no benefit:

| preflight input | wiring |
|---|---|
| `now_utc` / `observed_at_utc` | control-box UTC now |
| `local_epoch_path` | control-box epoch cache (written at provision; see below) |
| `mirror_transport` | GCS object `"$KOT_F1K_BUCKET"/f1k/ops/launch-epoch.json` via gsutil cat/cp (get/put) |
| `instance_name`, `zone`, `project_id` | the landed `INSTANCE_NAME`/`ZONE`/`PROJECT` constants |
| `deadline_utc` | `compute_selfdelete_deadline(epoch_launch)` — derived, never operator-supplied (preflight independently re-derives from the persisted epoch and refuses mismatch) |
| `billing_account` | new required env `KOT_GCP_BILLING_ACCOUNT` |
| `budget_resource_name`, `project_id` (Rev2, LC-6/LC-7) | new required env `KOT_F1K_BUDGET_RESOURCE` (exact `billingAccounts/<id>/budgets/<id>`) + the landed `PROJECT` — the budget check validates THIS resource, never "any budget" |
| `machine_type`, `local_ssd_count` | `n2d-highmem-8`, `2` (landed constants) |
| `s_per_prefill` | (Rev2, R2.6-B4) the gate artifact's blended s/prefill extracted by re-parsing the RAW gate JSON with `json.loads(..., parse_float=str)` and feeding the literal token to `canonical_decimal` — the artifact stores a JSON float and `_check_rate_window` refuses floats, so passing the parsed float would false-refuse EVERY real preflight; the literal-token re-parse is exact and needs no landed `/2` schema change |
| `systemctl_transport` | SSH wrapper: the read-only queries (`is-active`, `oncalendar`, `persistent`, `triggered-unit`, `exec-start`, and Rev2 LC-2's `restart-policy`) via `gcloud compute ssh ubuntu@<vm> -- systemctl show ...`, each mapped to the exact string the verifier expects; any SSH failure raises -> preflight returns NO-GO |
| `budget_transport` | Billing Budgets API get via gcloud, control-box credentials — full LC-6 validation |
| `catalog_transport` | the landed live Cloud Billing Catalog HTTP transport |
| `compute_transport` (LC-3v3, Rev3 — replaces Rev2's `scheduler_transport`) | live `instances.get` scheduling read-back: `terminationTime`, `instanceTerminationAction`, `provisioningModel`, discard-local-SSD flag — the L1 native cap verification (R3.1); no Cloud Scheduler in the load-bearing path |
| `iam_transport` (NEW, LC-4) | guest-side `instances.testIamPermissions` (SSH-invoked, VM credentials) — backs the cleanup/teardown deletion capability under Rev3 |

Boot-id note (Rev2, R2.6-BOOTID): phase-0 identity resolution uses LC-9's injectable
`bootid_transport` (SSH `cat /proc/sys/kernel/random/boot_id` as `ubuntu@<vm>`);
the landed function always read the LOCAL boot id, so a control-box call could never
match the guest and would false-refuse every launch.

Epoch origin (REVISED in Rev2 — R2.5; Rev3 strengthens further): `cmd_provision`
(LC-10) captures `t_epoch = UTC now` BEFORE issuing the create request and durably
persists it (control-box local + GCS mirror, write-once B1 semantics
[MEASURED contract: `poc/gcp/f1k_ops.py:4963-5037`]) BEFORE the VM exists, keyed to
(project, zone, instance name). (Rev3, R3.1) The L1 native cap is then carried IN
THE CREATE REQUEST ITSELF — `scheduling.terminationTime = t_epoch + 900 h` with the
unified `instanceTerminationAction = STOP` and the discard-local-SSD flag — so no
VM can exist, even transiently, without its cap; this is strictly stronger than
Rev2's arm-before-create external job (there is nothing separate to arm or to
read back BEFORE create — the delta-check's read-back demand is satisfied by the
$0 plan-oracle assertion on the request body plus the mandatory IMMEDIATE
post-create `instances.get` read-back below). After create, as the FIRST
post-create act: read back scheduling (terminationTime/action/SPOT/discard flags)
and write + mirror `epoch-binding.json` carrying the numeric instance id; if the
read-back mismatches or durable persistence fails, the just-created VM is
IMMEDIATELY deleted FAIL-CLOSED with the deletion VERIFIED to completion (poll the
zonal operation to DONE, check errors, confirm instance absence — the delta-check's
verified-cleanup requirement) and provision exits nonzero. Because `t_epoch`
predates actual creation by the provisioning latency, the deadline can only be
EARLIER than creation + 900 h — the conservative direction. Provision refuses if an
epoch already exists for a live VM name (reuse-gate parity). Build-order
consequence (R2.5): ALL epoch/cap code lands BEFORE any `provision` run.

Fail-closed statement (binding): preflight returns `{"go": false, reason}` on ANY
error — including transport exceptions — and `construction-continue` treats anything
but `go: true` as a hard refusal with no further phase executed
[MEASURED: `poc/gcp/f1k_ops.py:5440-5513` — the function already never raises].

### 4.2 Bead wonu: populating `provider.instance_termination_action`

PREMISE: [MEASURED: repo read 2026-07-23, poc/gcp/f1k_gcp.py:579 + poc/gcp/f1k_ops.py:2986-2995 + :5119-5128 at 153b9576]
the two termination-action sites are DISTINCT AXES, not a conflict — the GCP
provisioning flag `--instance-termination-action STOP` (`f1k_gcp.py:579`)
governs SPOT PREEMPTION (same-instance stop/resume, which keeps instance-hours <=
wall-clock and preserves the estate accounting), while `validate_handoff`'s required
`"DELETE"` (`f1k_ops.py:2986-2995`) attests the 900 h WALL-CLOCK CAP action,
implemented at Rev1 by the B2 systemd self-delete (`_selfdelete_exec_start`,
`f1k_ops.py:5119-5128`). The diagnosis was ratified in the bead kernel-of-truth-wonu
notes, 2026-07-19. (Rev2: the CAP action is now implemented by the L1 provider-side
delete plus the hardened L2 guest units — R2.1; the two-axes distinction itself
stands unchanged.)

Producer rule (normative, REVISED in Rev2 per review defect #3 — the landed
`verify_selfdelete_armed` returns NO action field, so Rev1's "copied from it" was
not structurally implementable; the fix is a real closed attestation, LC-5):

- `provider.instance_termination_action` := copied from
  `verify_cap_armed(...)["action"]` — the NEW composite closed cap attestation
  (LC-5) that composes (a) L1 provider delete-job verification (LC-3), (b) hardened
  L2 guest-timer verification (LC-2, which itself now returns
  `action: "DELETE"` + `mechanism: "guest-timer"`), and (c) the deletion-IAM dry-run
  (LC-4), and that carries `action`/`target`/`deadline_utc`/`mechanisms`/`iam`
  fields. The attestation exists ONLY if every leg succeeded this run. The value is
  NEVER read from, derived from, or compared against the GCP
  `--instance-termination-action` provisioning flag. Comment at the site:
  `# CAP axis (900h provider-side delete + guest fallback), NOT the Spot-preemption
  STOP flag — see bead wonu; echoing the GCP flag here produces a correct
  fail-closed refusal at validate_handoff and strands the launch.`
- `provider.termination_time_utc` := `compute_selfdelete_deadline(epoch_launch)` (the
  intended deadline).
- `provider.termination_timestamp_utc` := `verify_cap_armed()["deadline_utc"]`
  (the READ-BACK attestation — under Rev3, the live `instances.get`
  `terminationTime` and the L2 timer's verified OnCalendar, which LC-5 requires to
  agree before it returns at all). `validate_handoff` requires the two handoff
  fields equal — and (LC-8) additionally RECOMPUTES `armed_hours_decimal` from
  `campaign_started_at_utc -> termination_time_utc` under the producer's
  ROUND_CEILING/6 dp rule, requiring exact equality plus timestamp ordering, so an
  understated `"armed_hours_decimal"` (the review's `"1"`-against-899 h case) can no
  longer satisfy the $300 arithmetic. (Rev3, delta-check #3 residual:
  `validate_handoff` gains a required `now_utc` parameter and — repeated inside
  guard with a FRESH clock — requires `campaign_started_at_utc <= now_utc + 60 s`
  AND `campaign_started_at_utc <= created_at_utc <= now_utc + 60 s`, so a
  hand-built FUTURE start can no longer understate exposure.)
- (Rev3, R3.2) Under the native-STOP cap the provider block's semantics change and
  the handoff schema bumps to `kot-f1k-construction-handoff/2`: the cap attestation
  carries `cap.mechanism = "gce-termination-time"`, `cap.action = "STOP"` (the
  UNIFIED provider action, shared with preemption by the API itself),
  `cap.termination_time_utc` + read-back, and a `cleanup` sub-object (verified
  post-cap deletion semantics). The /1 literal-DELETE requirement encoded the
  superseded leaner-B premise. The wonu two-axes RULE survives intact in /2 form:
  the CAP attestation is populated ONLY from the live scheduling read-back
  composite (LC-5), never by echoing a provisioning flag — and the preemption axis
  is now separately asserted live (STOP) by guard step 3'(b).
- `provider.campaign_started_at_utc` := the continue-run UTC now (construction spend
  start), never GREEN time.
- `provider.armed_hours_decimal` := exact hours between `campaign_started_at_utc` and
  `termination_time_utc`, quantized UP (ROUND_CEILING) to 6 dp so the envelope
  arithmetic over-states exposure; must be `<= 899` (seam ARMED-899) or refuse.
- `provider.compute_ceiling_usd_decimal` := `armed_hours x licensed_rate` (exact
  Decimal, prec 80 — mirroring the validator's own recomputation);
  `total_envelope_usd_decimal` := ceiling + `non_compute_allowance_usd_decimal` +
  `rate_headroom_usd_decimal`, and must be `<= 300` or refuse.
- `provider.non_compute_allowance_usd_decimal` = `"20"` and
  `rate_headroom_usd_decimal` = `"10"` [STIPULATED defaults PROPOSED-CC-5: GCS
  estate + egress + API charges have been single-digit dollars to date and the quote
  headroom covers poll latency; these two numbers are maintainer-ratifiable at the
  #55 GO and the oracle only asserts arithmetic coherence, not the values].
- `provider.budget.*` := the verified $300 project-scoped budget resource from the B3
  check.
- Fail-closed statement: if `verify_cap_armed` did not succeed this run — any of
  the L1/L2/IAM legs failing — the producer has no attestation to copy from and
  REFUSES; the handoff cannot be written with an unverified cap attestation, so the
  STOP-echo hazard the wonu bead names is structurally unreachable, not merely
  discouraged. The guard independently repeats the same composite verification
  before engine start and periodically thereafter (R2.4).

---

## 5. The guard `--handoff` interface (what continue depends on)

The construction unit's `ExecStart` is `guard --handoff <canonical path>`, so the
transition is runnable ONLY with the B3 guard delta landed. This design adopts the
already-in-repo spec — `poc/gcp/F1K-CONSTRUCTION-SIDE-PLAN.md` section 3 (the 15-step
pre-spend order) and its B3 unit — as the guard-side contract, WITH ONE EXPLICIT
AMENDMENT (Rev2, R2.4, review defect #4): the side-plan's step 3 ("live GCE
`instanceTerminationAction=DELETE` + provider `terminationTimestamp`") is REPLACED —
followed literally it ALWAYS refuses, because provisioning correctly sets the
preemption action to STOP; omitted silently, it would drop the independent cap
verification. The replacement step 3' is:

- (a) live `scheduling.provisioningModel == SPOT`;
- (b) live GCE `instanceTerminationAction == STOP` — the UNIFIED action (Rev3):
  this single API field now serves BOTH axes at once — resume-preserving STOP on
  preemption AND the provider's action at the runtime limit (a DELETE
  mis-provision refuses);
- (c) `verify_cap_armed()` live (L1 native scheduling read-back:
  `terminationTime == epoch + 900 h` + discard flag; hardened L2 timer;
  deletion-IAM dry-run — LC-5 as revised R3.1) — with the L1 leg re-run at every
  checkpoint poll;
- (d) wall-clock sufficiency recomputed with a fresh clock, `parse_float=str`
  extraction, ROUND_CEILING, and the PROPOSED-CC-9 margin — which also absorbs the
  documented up-to-30 s provider termination latency;
- (e) (Rev3, delta-check #3) `campaign_started_at_utc <= fresh now + 60 s` and
  coherent ordering with handoff creation, independently of the validator.

The rest of the contract stands:

- `--handoff PATH` loads READY + gate from the handoff's canonical refs (byte-sha
  equality), then `build_runtime_license(ready, gate, handoff)`; all legacy guard
  flags become optional and, if supplied, must equal the license values exactly;
- live identity (numeric ID + guest boot_id via LC-9 + SPOT) and live-rate canonical
  equality with the license are re-verified INSIDE guard before reset consumption,
  the engagement probe, or any engine start; the guard also independently RECOMPUTES
  `armed_hours_decimal` and the $300 envelope from the handoff timestamps (repeating
  LC-8's arithmetic, defect #3);
- (Rev2) every checkpoint poll repeats: the rate sentry (drift/outage -> kill +
  durable terminal `rate-drift` event via the landed terminal-stop mechanics), step
  3'(c) cap re-verification, and step 3'(d) projected-completion vs
  absolute-deadline-minus-margin (breach -> kill, same terminal mechanics);
- everything downstream of license load — reset authority, argv-unity, probe, builder
  launch, checkpoints `{240,1056,2304}`, kill path — is the LANDED guard, unchanged
  [MEASURED: `poc/gcp/f1k_bringup_gate.py:1374-1510` read this pass].

Build-order constraint (restated because it is easy to violate): guard `--handoff` +
this entrypoint land TOGETHER, BEFORE any bring-up deploy, because READY byte-binds
the staged bundle (section 2.1 step 8) — landing B3 after a bring-up would force a
re-stage and invalidate READY.

---

## 6. The $0 oracle (`construction-continue --selftest`)

Green-mock validating the transition end-to-end with NO gcloud, network, GCP
resource, or spend — injectable fakes only, exactly the selftest style of the landed
`_bringup_deploy_selftest` / `selftest_b0` / `selftest_b1`. Fixture: the b0
READY/gate/handoff triple (`poc/gcp/f1k_ops.py:3419+`) extended with an on-disk
fixture VM-root (the worker-selftest pattern) and order-recording fake transports.

Mandatory assertions (each a named check; the executor may add more, remove none):

Staging completeness (plan-v4 #3):
1. Happy path: fixture GREEN + READY + fake transports -> continue runs phases 0-6,
   produces a handoff that `validate_handoff` AND `build_runtime_license` accept.
2. Every path the license references (builder, engine, weights, tokenizer
   artifact, dump patch, token sidecar, pin, rundir/workdir/out parents, payload
   manifests, `f1k_bringup_gate.py` at the payload root) EXISTS in the fixture root —
   asserted by enumerating the runtime-license paths and stat-ing each. (Rev2
   correction: the runtime-license schema has NO driver field, so the driver cannot
   be "enumerated from the license" — `f1k_driver.py` is asserted separately at its
   KNOWN staged path `<payload_root>/poc/glm52-probe/f1k-harness/f1k_driver.py`.) A
   fixture with `f1k_driver.py` deleted FAILS that separate check (regression pin
   against the original #3 gap).
3. The produced `service.exec_argv` is exactly
   `[interpreter, <root>/f1k_bringup_gate.py, guard, --handoff, <canonical handoff
   path>]` and the fake systemd unit's ExecStart parses to it.

Rate equality (plan-v4 #4):
4. Fake catalog rate `"0.219"` vs gate `"0.219"` -> GO.
5. Representation variants that are the SAME value — `"0.2190"`, `"0.21900"` (and,
   fed through the canonicalizer, an exponent-form input) -> GO (no false refuse).
6. `"0.2190000001"` and the review's `"0.10000000000000001"` (vs `"0.1"`) -> NO-GO
   `RATE_DRIFT`; transport raising -> NO-GO `RATE_QUOTE`; float input -> refused by
   the canonicalizer.
7. NO-GO paths assert NOTHING was mutated: no handoff bytes, no unit install call, no
   max-life cancel call recorded by the fakes.

Preflight wiring + wonu:
8. All B-fakes green -> preflight consulted exactly once, `go: true` observed, and
   the recorded call order satisfies: cap-verification legs (L1 + L2 + IAM, inside
   preflight) BEFORE max-life cancel BEFORE handoff write BEFORE unit start
   (#2-adjacent ordering).
9. Each preflight leg individually broken -> continue refuses at phase 2 with no
   later-phase calls recorded: epoch missing / future / mirror-local split; timer
   inactive / deadline drift / non-persistent / wrong triggered unit / unbound target
   / non-gcloud delete; budget absent / wrong amount; rate outside `[0.081, 0.595]`
   window (reusing the landed B1/B2/B3/B4 refusal fixtures).
10. The produced handoff has `provider.instance_termination_action == "DELETE"`,
    `termination_time_utc == termination_timestamp_utc ==` the fake systemctl
    OnCalendar deadline, and the value is sourced from the verify result object (the
    fake records the field's provenance); a handoff hand-built with `"STOP"` (the
    GCP-flag echo) is refused by `validate_handoff` (existing b0 case, re-asserted
    here as the wonu regression pin).
11. Envelope arithmetic: `armed_hours <= 899`, ceiling/envelope recomputation exact,
    `> 300` refuses; a fixture with continue attempted < 1 h after the epoch refuses
    `ENVELOPE` (seam ARMED-899).

Ordering + preconditions (plan-v4 #2 and single-shot):
12. Simulated live watchdog (fake pgrep) -> refuse `WATCHDOG`, no mutation.
13. Existing fixture handoff at the canonical path, or non-empty
    `construction-events.jsonl` -> refuse `ALREADY`.
14. Non-GREEN verdict, wrong schema, gate-byte drift vs pulled sha, READY boot_id !=
    fake live boot_id, harness-sha drift -> each refuses with its named code.
15. Wall-clock insufficiency: fixture with `elapsed` such that remaining < projected
    +1SE + reserve-hours -> refuse `WALLCLOCK`.
16. NO teardown call exists anywhere in the continue path (the fakes would record
    it); teardown remains a separate explicit entrypoint.

(Rev2) Groups 17-27 — the spend-safety review's oracle gaps — are specified in
section R2.6 and are equally mandatory.

Regression baseline: the four landed oracles (`bringup-deploy --selftest`, worker
`--selftest`, `gate --selftest`, `f1k_ops.py selftest`) are re-run and EXTENDED for
every LC item (section R2.7) — Rev2 changes landed option-B code, so "still pass
unchanged" no longer applies to `f1k_ops.py selftest`; its b0/b1 suites gain the LC
cases and the whole suite must be green. `build_carriers.py` remains byte-identical
`a92be3e4...` — the build still touches no scientific file.

---

## 7. Plan-v4 findings — disposition

### 7.1 Finding #2 (teardown sequenced before on-box confirms) — RESOLVED

The landed single-VM flow already places the runner's on-box (a)/(c) confirm +
literal-PASS + re-collect + `--finalize-ready` + full gate-dir pull BEFORE the verdict
and keeps the VM alive [MEASURED: `poc/gcp/README.md` run-sequence steps 4-5;
`F1K-CONSTRUCTION-PLAN.md` section 7 step 3]. What SURVIVES of the finding under B is
the bring-up watchdog and guest max-life: either can still destroy the retained VM
after worker completion but before finalization or between GREEN and continue. This
design closes that mechanically and textually:

- Mechanical: continue's watchdog interlock (phase 0 step 7) and the
  verify-B2-before-cancel-max-life ordering (phase 4); the runner runbook step gains
  an explicit max-life re-arm (`sudo shutdown -c && sudo shutdown -P +<N>`) if
  finalization needs more than the remaining guest max-life.
- Textual (executor applies with the build): plan section 7 and the README run
  sequence state the invariant verbatim: "the bring-up watchdog's ONLY teardown
  triggers are a FAILED heartbeat or its bring-up `--max-hours` deadline; the
  operator stops the watchdog AFTER the gate-dir pull and BEFORE
  `construction-continue`; no teardown authority may exist while a construction
  license is live except the 900 h self-delete and guard's own kill path."

### 7.2 Findings #3/#4 (no runnable transition; rate not revalidated) — RESOLVED

Sections 2-5 are the runnable, construction-rate-bound transition: staging delta
enumerated (section 8), rate-equality enforced at continue, at evidence-write, inside
guard pre-spend, and per-poll; the remedy for drift is a $0 re-collect/re-gate, so a
rate change can no longer produce a false STOP, a stale-rate checkpoint basis, or a
stranded GREEN. The stale sub-claim of #3 about payload staging is documented as
superseded (section 1).

### 7.3 Finding #8 (bring-up cost narrative trimmed) — RESOLVED

The authority's disclosed worst case was total bring-up "~$3-3.5 worst case" at the
on-demand ~$0.579/h basis, and the plan's "~$2-3" trimmed that upper edge [MEASURED:
`poc/gcp/F1K-BRINGUP-GATE-FIX.md` section 2.8 read this pass]. Under the landed
Single-VM-Spot basis the honest statement, which the executor writes into plan
sections 7/8 and NEXT-ACTION, is:

- Formula, not a bare point: `total bring-up ~= attempt_wall_hours x live Spot rate
  x attempts`, with `attempt_wall_hours` bounded by the guest max-life (default
  900 min = 15 h) and attempts bounded by the operator retry policy.
- Per-attempt worst case at the quoted Spot band $0.174-0.24/h and the 15 h max-life:
  ~$2.6-3.6 [EXTRAPOLATION from the frozen band x the default cap; load-bearing for
  nothing — the enforced bounds are the watchdog `--max-hours`, the guest max-life,
  and the $300 budget tripwire]. The superseded on-demand figure is cited as history,
  not silently dropped, and no "~$2-3" phrasing survives without its upper edge.
- (Rev2, R2.6-#8; Rev3-hardened per delta-check #5) Bring-up dollars and
  instance-hours are carried into the config-cost basis by an ENFORCED step:
  `construction-continue` phase 5 produces `prior-spend-evidence.json`, and LC-13
  amends `cmd_config_cost` (`poc/gcp/f1k_bringup_gate.py:1787`) to require +
  validate it and to REFUSE manual `--prior-usd`/`--prior-hours` (zero included).
  The oracle asserts production, arithmetic, tamper refusal, and the manual-flag
  refusal. They also share the 900 h wall clock with construction under the
  pre-create epoch (section 4.1), so they cannot disappear from the analysis basis.

---

## 8. The exact staging delta (what continue adds beyond bringup-deploy)

Already on the box after bring-up + runner finalization (continue adds NONE of
these, and MUST NOT touch them — READY byte-binds the payload):
flat worker bundle in `~/f1k` (incl. `f1k_bringup_gate.py`, `f1k_ops.py`,
`tok_glm52.py`, `kae-patch-draft/`, `dump-patch/`, `gate-corpus/` with the
construction manifest + eval items); the reviewed construction payload under
`~/f1k/poc/...` (incl. `build_carriers.py` `a92be3e4`, `f1k_driver.py`, analysis,
registry, tooling, data trees, mocks, `bundle-manifest.json`); the built estate +
both engines + weights + tokenizer artifacts on `/mnt/nvme`; and `~/f1k-gate/`
(T1/T2 atomic results, `pin_bringup.stats` + derivation, gate-sample, gate-tokens,
re-collected `gate-inputs.json`, functional-inertness + dump statuses,
`construction-ready.json`).

The delta — everything `construction-continue` adds, exhaustively:

| # | Item | Where | How |
|---|---|---|---|
| 1 | `bringup-gate.json` (GREEN, control-box product) | `/home/ubuntu/f1k-gate/` | atomic scp + sha read-back |
| 2 | `live-rate-evidence.json` (canonical bytes) | `/home/ubuntu/f1k-gate/` | atomic scp + sha read-back |
| 3 | `construction-handoff.json` | `/home/ubuntu/f1k-gate/` | produced phase 5, atomic scp + sha read-back |
| 4 | B1 epoch VM-local cache | `/home/ubuntu/f1k-gate/launch-epoch.json` | from the GCS mirror (authoritative) |
| 5 | hardened L2 guest timer + service units (LC-1) | `/etc/systemd/system/` | rendered, installed, started, verified via preflight |
| 6 | `kot-f1k-construction.service` (guard ExecStart) | `/etc/systemd/system/` | installed + started + verified phase 6 |
| 7 | guest max-life CANCELLATION | VM | only after the full cap stack verified + L2 re-probe (phase 4) |
| 8 | `prior-spend-evidence.json` (Rev2) | `/home/ubuntu/f1k-gate/` + control box | produced phase 5, sha in the receipt |

NOT in the continue delta but part of the transition surface: (Rev3) the L1 native
cap (`scheduling.terminationTime = epoch + 900 h`, unified STOP action, discard
flag) is set INSIDE the provision create request itself — no VM exists without it
— and is only VERIFIED here (read-back at preflight and again at the phase-4
re-probe).

Code deltas shipped with the build (not staged at continue time): the
`construction-continue` entrypoint + `f1k_ops` import + the LC-10/LC-11 provision
and teardown changes + `ubuntu@` SSH targeting in `f1k_gcp.py`; the guard
`--handoff` (B3) delta incl. step 3' in `f1k_bringup_gate.py`; the LC-1..9 + LC-12
amendments in `f1k_ops.py`; LC-13 (`cmd_config_cost`) and LC-14 (the control-box
cap-reaper) per R3. ALL of it lands as ONE reviewed bundle BEFORE any `provision`
run (R2.5) — Rev1's "before any bring-up deploy" was necessary but insufficient.

---

## 9. Open items for the maintainer (none block the executor build)

1. `KOT_GCP_BILLING_ACCOUNT` + the $300 Billing Budget resource must exist before a
   real run — and (Rev2) the budget must be SINGLE-PROJECT-FILTERED to this project,
   USD, exactly $300, with thresholds + notification config; its exact resource name
   is pinned in `KOT_F1K_BUDGET_RESOURCE` (known GCP env/IAM setup gate; preflight
   fails closed without it).
2. (Rev3, R3.1 — REPLACES the Rev2 Scheduler item) Ratify the resolved cap fork:
   variant B, the NATIVE absolute runtime limit (`terminationTime = epoch + 900 h`,
   unified `instanceTerminationAction = STOP`, discard-local-SSD flag) as the hard
   cap, with verified-deletion cleanup — versus variant A (unified DELETE: true
   deletion at cap but preemption becomes terminal, breaking the same-instance
   resume + instance-hours accounting premise). Recommendation and rationale in
   R3.1. NO Cloud Scheduler API, no OAuth caller SA, no handler deployment is
   needed under B; deletion IAM (for cleanup/teardown) rides the existing
   operator + VM service accounts.
3. (Rev3) Authorize the CAP-PROBE: a sub-dollar live probe (tiny Spot VM + 1 local
   SSD, short terminationTime + STOP) verifying the three provider semantics the
   docs leave to inference — timestamp re-arms across stop/resume, past-time
   restart refusal, STOP-with-discard on a local-SSD VM — BEFORE the build freezes
   (PROPOSED-CC-13; the mocks-calibrate-plumbing-not-semantics lesson applied to
   provider mechanics). Est. $0.10-0.30.
4. Budget resource per R3.3: all-services single-project $300 USD budget with an
   explicit period, no narrowing filters, VERIFIED notification channels; project
   live-linked to `KOT_GCP_BILLING_ACCOUNT`; exact name pinned in
   `KOT_F1K_BUDGET_RESOURCE`. Enable Monitoring API read for channel verification.
5. Ratify the PROPOSED-CC-5 allowance numbers ($20 non-compute, $10 rate headroom)
   and PROPOSED-CC-9 (2 h wall-clock margin) at the #55 spend-GO. Arithmetic, not
   policy, is what the code enforces.
6. The construction spend-GO itself (#55) — explicitly out of scope here.

## 10. Assumption register (PROPOSED — the executor registers on commit; no ids minted here)

- PROPOSED-CC-1 [STIPULATED, REVISED Rev2]: the lean-B contract SCHEMAS are the
  fixed interface; the option-B implementation is amended ONLY per the LC register
  (R2.7), each item re-verified with fresh oracle cases. Owner: coordinator.
- PROPOSED-CC-2 [STIPULATED]: all VM SSH/SCP targets `ubuntu@` so `$HOME =
  /home/ubuntu` matches the frozen canonical paths; mechanically verified at $0 by
  the remote-home check. Resolution path: the check itself on first provision.
- PROPOSED-CC-3 [STIPULATED]: wall-clock sufficiency uses the +1SE projection branch
  plus reserve-hours as the launch bound. Owner: coordinator; maintainer may tighten.
- PROPOSED-CC-4 [STIPULATED]: preflight runs control-box-side with SSH/gsutil/gcloud
  transports. Resolution path: the $0 oracle + first live preflight.
- PROPOSED-CC-5 [STIPULATED]: $20/$10 envelope allowances pending maintainer
  ratification at the #55 GO.
- PROPOSED-CC-6 [EXTRAPOLATION, load_bearing: false]: Spot preemption STOPs and can
  resume the same numeric instance with local SSD contents lost but GCS-restorable
  estate; the per-attempt bring-up cost band section 7.3. Resolution path: first real
  preemption observation + the GCP docs citations already carried in
  `F1K-CONSTRUCTION-SIDE-PLAN.md` section 4 (the budgets-do-not-cap-spend claim there
  is LIT-BACKED to the vendor doc it links; the review restates both with vendor
  links — stopped instances retain chargeable resources, budgets do not cap spend).
- PROPOSED-CC-7 [RESOLVED in Rev3 — see R3.1]: the shared-field question is
  ANSWERED from the vendor doc (the runtime-limit action and the Spot preemption
  action are ONE unified `instanceTerminationAction`), so Rev2's Scheduler-as-L1
  is WITHDRAWN; the hard cap is the NATIVE absolute `terminationTime` with the
  unified STOP action (variant B). Two provider behaviors remain doc-inferred and
  are pinned by the mandatory CAP-PROBE (PROPOSED-CC-13) before build freeze:
  re-arming of the absolute time across stop/resume, and past-time restart
  refusal mechanics.
- PROPOSED-CC-8 [STIPULATED, NEW Rev2; role narrowed in Rev3]: the L2 guest
  terminal fallback is `poweroff -f` after delete-retry exhaustion — no cloud auth
  needed; under Rev3 it is pure defense-in-depth beneath the native cap (covers a
  late/failed provider STOP); the residual (retained-resource charges until
  cleanup deletes) is disclosed, not hidden.
- PROPOSED-CC-9 [STIPULATED, NEW Rev2]: 2 h transition/termination margin on every
  wall-clock sufficiency check. Maintainer may tighten at the #55 GO.
- PROPOSED-CC-10 [STIPULATED, NEW Rev2; extended Rev3 per R3.3]: the budget
  attestation validates the exact `KOT_F1K_BUDGET_RESOURCE` (billing-account
  parent, USD, $300, single-project filter, NO other narrowing filters, explicit
  period, thresholds, VERIFIED notification channels, live project-to-account
  linkage); "any $300 budget" never passes.
- PROPOSED-CC-11 [STIPULATED, NEW Rev3]: variant B (native STOP cap + verified
  cleanup) over variant A (unified DELETE) because A makes every Spot preemption
  terminal — destroying same-instance resume, the instance-hours <= wall-clock
  accounting premise behind the frozen affordability decision, and the write-once
  epoch continuity (each re-provision would need a maintainer clock decision).
  B's post-cap residual is bounded to stopped-VM storage (order $0.5-0.6/day),
  tripwired by the $300 budget and removed by verified cleanup. Maintainer
  ratifies (section 9 item 2).
- PROPOSED-CC-12 [STIPULATED, NEW Rev3]: post-cap cleanup = the control-box
  cap-reaper (LC-14, nohup watchdog pattern): sleep to deadline, then
  delete -> poll operation to DONE -> verify absence, unbounded retries with
  backoff; best-effort by design, because its failure now leaks only stopped-VM
  storage. An off-box Cloud Scheduler + handler cleanup remains OPTIONAL and, if
  ever built, MUST follow the delta-check mechanics (OAuth access tokens not OIDC;
  handler polls to DONE + verifies absence + returns non-2xx until confirmed;
  minute-FLOORED UTC cron; retries until absence).
- PROPOSED-CC-13 [STIPULATED, NEW Rev3]: the sub-dollar CAP-PROBE (section 9 item
  3) is MANDATORY before build freeze; its recorded results gate the oracle's
  provider-semantics assumptions (group 30).

---

## Revision 2 — spend-safety review corrections

Source verdict: `poc/gpt56-review/f1k-cc-transition-review/last-message.json`
(GPT-5.6, REJECT; its file:line citations verified against the tree this pass).
The reviewer CONFIRMED sound — and Rev2 does not disturb — the canonical-Decimal
zero-tolerance rate-equality gate and the `_construction_payload_files()` staging of
`build_carriers.py` + `f1k_driver.py`.

The review's central finding, accepted in full: Rev1's 900 h and $300 backstops were
NOT mechanically fail-closed — the guest systemd timer attests configuration, not
deletion capability, and the budget check attests "a $300 budget exists somewhere".
Rev2 rebuilds the cap as layered, independently-verified mechanisms and amends the
landed option-B code where the defects live.

### R2.1 Defect #1 — the hard cap (ADOPTED, with a layered architecture)

**(Rev3: THIS SECTION'S L1 MECHANISM IS SUPERSEDED.** The Rev2 delta-check showed
the Cloud Scheduler L1 as specified here is not a functioning hard cap (OIDC
rejected by googleapis.com, no async-operation completion, minute-granularity
recurring cron, finite retries). Rev3 replaces it with the NATIVE GCE absolute
runtime limit — see R3.1, which governs. The layer PRINCIPLE (provider-side cap,
guest defense-in-depth, budget tripwire, verify-before-cancel) survives; the
Scheduler machinery does not.)

Disposition: ADOPTED. The guest timer is DEMOTED to defense-in-depth; the doc no
longer represents it as the hard cap anywhere.

The Rev2 cap stack, in enforcement order:

- L1 — THE HARD CAP, provider control-plane (PROPOSED-CC-7): a Cloud Scheduler job
  armed at PROVISION time (before the VM exists, R2.5) at the cron-encoded absolute
  deadline `epoch + 900 h`, making an OIDC-authenticated Compute API
  `instances.delete` call bound to exactly this project/zone/instance, with a
  durable retry configuration at a reviewed floor. Properties that make it the hard
  cap: it runs from the provider's control plane, so it is independent of guest
  auth, guest network, guest wedge, AND of the VM's run state — it deletes a
  STOPped (preempted) VM too, which closes the review's stopped-at-deadline hole
  (deletion ends retained-resource charges; the boot disk is created inline by
  `provision` and auto-deletes with the instance — executor verifies the
  auto-delete flag at build time). An orphaned job would re-fire at the same cron
  date a year later against a nonexistent instance (404, harmless); `teardown`
  (LC-11) deletes the job anyway.
- L2 — guest-side, best-effort (LC-1/LC-2, PROPOSED-CC-8): the hardened systemd
  timer/service — extended retry loop, `Restart=on-failure` with
  `StartLimitIntervalSec=0`, and a terminal `poweroff -f` fallback that needs NO
  cloud credentials and stops compute billing even under total IAM/API failure
  (residual: retained-resource charges continue until L1 deletes — disclosed).
- L3 — the $300 budget, tripwire only (LC-6, PROPOSED-CC-10): exact-resource,
  project-filtered attestation; never claimed as a cap (budgets do not cap spend —
  vendor-documented, cited in the review and side-plan section 4).
- Pre-cancel gate: the bring-up guest max-life is cancelled ONLY after L1 + L2 +
  the deletion-IAM dry-run all verified (phase 4), with an L2 `is-active` re-probe
  immediately before the cancel.

IAM verification before the max-life cancel (LC-4): `instances.testIamPermissions`
for `compute.instances.delete` executed FROM the VM with its own metadata
credentials — an end-to-end dry run of auth + API reachability + permission along
the L2 path without deleting; plus a control-plane read asserting the L1 job's
service-account IAM binding. Honest residual, stated not hidden: these prove
capability AT ARM TIME, not at the deadline; the deadline-time residual is
"Compute API unavailable for the entire L1 retry window AND the guest too wedged to
poweroff" — two independent failure modes that must coincide, with the L3 alert as
the final tripwire. No layer is claimed invoice-exact, consistent with the
launch-arch memo's standing rule.

Is the cap now genuinely provider-enforced? YES at the architecture level: the
primary deletion path executes in the provider control plane on an absolute
schedule fixed before the VM existed, independent of everything on the instance.
The one open verification (PROPOSED-CC-7 resolution path) is the executor's
build-time check of whether the native GCE runtime-limit could replace Cloud
Scheduler without forcing DELETE-on-preemption; either outcome leaves a
provider-side cap in place.

### R2.2 Defect #2 — exact budget attestation (ADOPTED)

Disposition: ADOPTED. `assure_billing_budget` (LC-6) gains required
`budget_resource_name` (env `KOT_F1K_BUDGET_RESOURCE`) + `project_id`; it fetches
THAT resource and validates: billing-account parent == `KOT_GCP_BILLING_ACCOUNT`;
currency USD; amount exactly 300 units / 0 nanos; budget filter naming EXACTLY this
one project (an account-wide or other-project budget REFUSES); well-formed
thresholds; notification configuration present. It returns a CLOSED attestation
which preflight (LC-7) passes through for direct handoff population, and
`validate_handoff` (LC-8) now also enforces the `billingAccounts/<id>/budgets/<id>`
format on `resource_name`; exact-resource equality is enforced live at continue
(the pure validator cannot know the deployment's resource name — the live check
binds it). (Rev3 correction, per the delta-check: Rev2's claim that the GUARD
re-fetches the budget live was not wired and is WITHDRAWN — the guest deliberately
lacks budget IAM. The honest wiring: the budget is verified live CONTROL-BOX-side
(preflight + continue); the guard verifies the budget ATTESTATION bytes against
the sha carried with the handoff, and post-launch live re-checks are the
control-box cap-reaper/monitor's job, best-effort, alongside the budget's own
threshold alerts.)

### R2.3 Defect #3 — real attestation provenance + armed-hours recompute (ADOPTED)

Disposition: ADOPTED. Rev1's "DELETE copied from `verify_selfdelete_armed`" was not
implementable against the landed return shape — conceded. Fixes: (a) LC-2 extends
the guest verifier's return with `action`/`mechanism`; (b) LC-5 introduces
`verify_cap_armed()`, the composite closed cap attestation (L1 + L2 + IAM legs; it
exists only if all legs succeeded, and it requires the L1 schedule and L2
OnCalendar deadlines to be identical) — the handoff producer copies
`instance_termination_action` and `termination_timestamp_utc` from IT (section 4.2,
revised); (c) LC-8 makes `validate_handoff` RECOMPUTE `armed_hours_decimal` from
`campaign_started_at_utc -> termination_time_utc` under the producer's
ROUND_CEILING/6 dp rule with exact-equality + timestamp-ordering requirements,
killing the understated-armed-hours bypass of the $300 arithmetic; (d) the guard
independently repeats the recompute and the composite verification (R2.4).

### R2.4 Defect #4 — the contradictory inherited guard step (ADOPTED)

Disposition: ADOPTED. The side-plan's guard step 3 is EXPLICITLY REPLACED by step 3'
(section 5): live SPOT check; live preemption action == STOP asserted (the resume
premise, refusing a DELETE-on-preemption mis-provision); `verify_cap_armed()` live
with deadline == `epoch + 900 h`; fresh wall-clock sufficiency with margin. Step 3'
runs immediately before engine start AND repeats at every checkpoint poll together
with the rate sentry and the projected-completion-vs-deadline check. The
independent cap verification the original step promised is therefore kept — in a
form that can actually pass on a correctly-provisioned VM.

### R2.5 Defect #5 — epoch anchoring (ADOPTED)

Disposition: ADOPTED. Rev1's post-create epoch write is WITHDRAWN. LC-10: capture
`t_epoch` BEFORE the create request; durably persist epoch (+ arm the L1 job)
BEFORE create; bind the numeric instance id in a mirrored `epoch-binding.json`
after create; READ BACK epoch + mirror + binding, and on any persistence/read-back
failure DELETE the just-created VM immediately and exit nonzero. Deadline error
from provisioning latency is now strictly in the conservative (earlier) direction.
Build-order rule strengthened accordingly: the ENTIRE Rev2 code set lands as one
reviewed bundle BEFORE any `provision` run (sections 4.1 and 8).

### R2.6 Engineering corrections (ALL ADOPTED)

- B4 float false-refuse: the blended s/prefill (and every projection value continue
  consumes) is extracted from the RAW gate JSON with `json.loads(...,
  parse_float=str)` and fed to `canonical_decimal` — exact, no binary-float
  pass-through, no landed `/2` schema change (section 4.1 table).
- Control-box boot-id false-refuse: LC-9 adds an injectable `bootid_transport` to
  `resolve_live_instance_identity` (default = local read, preserving the on-VM
  READY writer); the control box passes the SSH guest read (section 4.1 note).
- Wall-clock sufficiency: phase-0 pre-filter hardened (raw-decimal extraction,
  ROUND_CEILING, PROPOSED-CC-9 margin) + guard-side recompute immediately before
  engine start + repeated at every checkpoint against the absolute deadline minus
  margin (sections 2.1 step 5 and 5).
- Oracle driver enumeration: corrected — the runtime license has no driver field;
  `f1k_driver.py` is asserted at its known staged path (section 6 assertion 2).
- Plan-v4 #8 executable binding: `prior-spend-evidence.json` produced at phase 5,
  consumed by the config-cost step by name, oracle-asserted (sections 2.1 and 7.3).
- Expanded $0 oracle — groups 17-27, all mandatory:
  17. L1 cap job: absent / wrong schedule / wrong target instance / wrong service
      account / state PAUSED / retry config below floor -> preflight NO-GO each.
  18. Deletion IAM: `testIamPermissions` missing `compute.instances.delete` /
      transport failure / API unreachable -> NO-GO, all BEFORE any max-life cancel.
  19. L2 hardening: unit text lacking `Restart=on-failure` or the poweroff fallback
      -> LC-2 verify refuses; simulated retry exhaustion -> fallback invocation
      asserted on the order-recording fake.
  20. Stopped-at-deadline: fixture instance state TERMINATED -> the L1 leg of
      `verify_cap_armed` passes on control-plane config alone (structural assertion
      that L1 does not depend on guest run state); the L2 leg's non-execution is
      covered by L1 (documented assertion).
  21. Epoch anchoring order: the provision fake asserts epoch-persist and L1-arm
      call ordinals PRECEDE the create ordinal; mirror-put failure or read-back
      mismatch after create -> the fake records the immediate instance-delete call
      and nonzero exit.
  22. Mirror-absent-while-local-exists -> LC-12 `require_mirror` refusal in the
      launch context (mirror loss is not a fallback).
  23. Budget scope: account-wide (no project filter) / wrong-project filter / wrong
      currency / wrong resource name / amount 300.01 -> refuse each.
  24. Armed-hours integrity: real 899 h interval with `"armed_hours_decimal":"1"`
      -> `validate_handoff` refuses (LC-8 recompute); reversed/equal timestamps
      refuse.
  25. TOCTOU narrowing: L2 timer reported inactive at the phase-4 re-probe ->
      continue refuses BEFORE `shutdown -c` (order-recording fake).
  26. Guard-side: pre-start rate outage/drift -> refuse before probe; poll-time
      outage/drift -> kill + durable `rate-drift` terminal event; checkpoint
      projected-completion past deadline-minus-margin -> kill; step 3' cap
      re-verification failure at a poll -> kill.
  27. Mechanics: remote sha read-back failure on any scp -> refuse; systemd
      `ActiveState != active` / `MainPID == 0` / ExecStart mismatch -> named
      nonzero exit, no retry loop.

### R2.7 Landed option-B change register (EVERY item re-enters review with fresh oracle cases)

LOAD-BEARING: [MEASURED: review verdict poc/gpt56-review/f1k-cc-transition-review/last-message.json + repo reads at 153b9576]
the following amend LANDED, previously review-clean code; none touches a scientific
file, and `build_carriers.py` stays byte-identical:

| LC | Function / site | Change | Why |
|---|---|---|---|
| LC-1 | `_selfdelete_exec_start` + `render_selfdelete_unit` (`f1k_ops.py:5119,:5131`) | extended retry loop; `Restart=on-failure`, `RestartSec`, `StartLimitIntervalSec=0`; terminal `poweroff -f` fallback | defect #1: 6x30s-then-give-up left the VM billable |
| LC-2 | `verify_selfdelete_armed` (`:5204`) | verify restart policy + fallback presence; return closed attestation incl. `action:"DELETE"`, `mechanism` | defects #1/#3 |
| LC-3 | (Rev3: REVISED to LC-3v3) NEW `verify_provider_cap` | live `instances.get` scheduling read-back: `terminationTime == epoch+900h`, unified action STOP, SPOT, discard-local-SSD flag; injectable `compute_transport`. Rev2's Scheduler job create/verify is DROPPED from the load-bearing path (R3.1) | defect #1: the real hard cap, now native |
| LC-4 | NEW `verify_delete_iam` | guest-side `testIamPermissions` incl. `compute.instances.delete` + L1-SA IAM-binding read | defect #1: capability, not config |
| LC-5 | NEW `verify_cap_armed` | composite closed cap attestation (L1+L2+IAM; equal deadlines required); the ONLY source for handoff `instance_termination_action` / `termination_timestamp_utc` | defect #3 |
| LC-6 | `assure_billing_budget` (`:5290`) | required exact resource + project; validate account/currency/amount/filter/thresholds/notifications; closed attestation return | defect #2 |
| LC-7 | `preflight_launch_gate` (`:5434`) | consume LC-5 + LC-6; new `compute_transport` (Rev3) / `iam_transport` / budget params; attestations passed through in the result | defects #1/#2/#3 wiring |
| LC-8 | `validate_handoff` (`:2758`, decimals at `:2997`, budget at `:3052`) | recompute `armed_hours_decimal` from timestamps (ROUND_CEILING/6 dp, exact equality); timestamp ordering; budget `resource_name` format | defects #2/#3 |
| LC-9 | `resolve_live_instance_identity` (`:548`, boot id `:527`) | injectable `bootid_transport` (default local, preserving on-VM use) | boot-id false-refuse |
| LC-10 | `cmd_provision` (`f1k_gcp.py:550`) | pre-create epoch capture/persist + L1 arm; post-create binding + read-back; fail-closed delete of the new VM on persistence failure | defect #5 |
| LC-11 | (Rev3: REVISED to LC-11v3) `cmd_teardown` (`f1k_gcp.py:604`) | frozen ordering invariant: delete VM -> poll zonal operation to DONE (error-checked) -> verify absence (`instances.get` 404) -> ONLY THEN remove external cleanup machinery (reaper entry / optional job); any VM-delete failure LEAVES everything armed + exits nonzero; the epoch mirror is never deleted (historical record) | delta-check #4 teardown ordering |
| LC-12 | `_resolve_epoch_launch` (`:5040`) | `require_mirror` mode for the launch context: mirror-absent-with-local-present refuses | oracle gap 22 |

Each LC item: implemented by the executor, covered by new b0/b1/continue oracle
cases, and included in the cross-vendor re-review BEFORE any `provision` run. The
b0/b1 suites' counts will change; "23/23 unchanged" no longer applies and is not
claimed.

### R2.8 Per-defect disposition summary

| Review item | Disposition |
|---|---|
| #1 guest timer not a hard cap | ADOPTED — L1 provider-side Scheduler delete armed pre-create as THE cap; L2 hardened + poweroff fallback demoted to defense-in-depth; IAM dry-run before max-life cancel; stopped-at-deadline closed by L1 (R2.1) |
| #2 budget not project-verified | ADOPTED — exact-resource closed attestation (R2.2) |
| #3 attestation fiction + armed-hours | ADOPTED — `verify_cap_armed` composite + LC-8 recompute + guard repeat (R2.3) |
| #4 contradictory guard step | ADOPTED — step 3 explicitly replaced by step 3'; periodic re-verification (R2.4) |
| #5 epoch anchoring | ADOPTED — pre-create capture, pre-create L1 arm, fail-closed post-create delete (R2.5) |
| B4 float | ADOPTED — `parse_float=str` literal-token extraction (R2.6) |
| boot-id | ADOPTED — LC-9 injectable transport (R2.6) |
| wall-clock | ADOPTED — hardened + guard recompute + checkpoint repeat (R2.6) |
| oracle driver enumeration | ADOPTED-WITH-MODIFICATION — known-path assertion instead of license enumeration, keeping the regression pin (R2.6) |
| plan-v4 #8 binding | ADOPTED — executable `prior-spend-evidence.json` (R2.6) |
| oracle gaps | ADOPTED — groups 17-27 (R2.6) |

---

## Revision 3 — cap-mechanism fork resolution + Rev2 delta-check corrections

Source verdict: `poc/gpt56-review/f1k-cc-rev2-deltacheck/last-message.json`
(GPT-5.6, NEW-DEFECT / STILL-REJECT). The delta-check CONFIRMED, conditional on a
functioning cap: the guard STOP/DELETE axes (Rev1 defect #4) and the epoch
capture/persist/arm-before-create ordering (Rev1 defect #5) — Rev3 does not regress
either. It also confirmed the armed-hours core bypass is dead and the budget core
checks are right. Everything below amends the remaining findings.

### R3.1 The fork, resolved: NATIVE runtime limit, variant B (STOP-unified)

PREMISE: [LIT-BACKED: GCE "Limit the runtime of a VM" doc, docs.cloud.google.com/compute/docs/instances/limit-vm-runtime, fetched 2026-07-23]
the vendor doc answers the PROPOSED-CC-7 questions directly: (1) `terminationTime`
is an ABSOLUTE timestamp; `maxRunDuration` is a duration whose termination
timestamp "is recalculated by adding that duration to the VM's latest start time" —
so for a fixed 900 h wall-clock cap only `terminationTime` is correct; (2) the
runtime-limit action is `instanceTerminationAction`, values STOP or DELETE — the
SAME, UNIFIED field that governs Spot preemption (the doc treats it as one field
with no per-trigger variants), so DELETE-at-limit forces DELETE-on-preemption and
STOP-at-limit coexists with STOP-on-preemption; (3) limits run 30 s to 120 days
(900 h ~ 37.5 d fits); termination "might take up to 30 seconds longer" (absorbed
by the PROPOSED-CC-9 margin); (4) local-SSD VMs require
discard-local-SSDs-at-termination when the action is STOP; and (5) — decisive —
"the time must be in the future; otherwise, any requests to create or rerun the VM
fail until you update or remove the time": a PAST `terminationTime` blocks restart
PROVIDER-SIDE, so post-cap compute cannot resume without a deliberate, auditable
scheduling update.

Decision (PROPOSED-CC-11, maintainer ratifies): the hard cap is the NATIVE
combination `provisioningModel=SPOT` + unified `instanceTerminationAction=STOP` +
absolute `terminationTime = epoch + 900 h` + discard-local-SSD-at-termination, set
INSIDE the provision create request. This is the "correct combination giving BOTH
preemption-resume AND a hard <= 900 h bound" the delta-check asked for: preemption
STOPs and resumes the same instance (premise preserved — including the
instance-hours <= wall-clock accounting behind the frozen affordability decision);
at the cap the provider STOPs the VM (compute + local-SSD billing ends); past the
cap the provider refuses restarts. What variant B deliberately gives up is
DELETION at the cap: a stopped VM retains its boot disk (order $0.5-0.6/day for
the 100 GB pd-ssd — stopped instances stop compute charges but retain attached-
resource charges, per the vendor stop/suspend doc), so deletion is decoupled into
a VERIFIED CLEANUP: the control-box cap-reaper (LC-14) and `teardown` (LC-11v3)
both implement delete -> poll the zonal operation to DONE (error-checked) ->
verify instance ABSENCE -> only then remove cleanup machinery; retries continue
until absence is confirmed. The cleanup's failure mode leaks cents per day,
tripwired by the $300 budget — categorically different from Rev2's
running-VM-forever leak.

Variant A (unified DELETE) — true deletion at the cap, zero post-cap residual, and
the simplest possible machinery — is REJECTED as default because the unified field
makes every Spot preemption DELETE the instance: the same-instance resume premise,
the write-once epoch continuity (each re-provision would demand a maintainer
clock decision), and the frozen affordability accounting all break. It remains the
maintainer's documented alternative (section 9 item 2); under A the /1 handoff
DELETE literal and Rev1 wonu semantics stand unchanged.

Does native collapse the delta-check's #1-#3? YES — by elimination, not repair:
OAuth-vs-OIDC (#1), async-operation completion at the deadline (#2), and cron
granularity/finite-retry semantics (#3) were all defects of an EXTERNAL caller in
the load-bearing path; the native cap has no external caller, no auth, no
schedule encoding, and no retry semantics — the provider enforces its own
scheduling field. Those mechanics survive ONLY in the non-load-bearing cleanup
layer, where they are still specified correctly (PROPOSED-CC-12: OAuth access
tokens, poll-to-DONE + absence + non-2xx-until-confirmed, minute-FLOORED UTC cron,
retries-until-absence) should the optional off-box variant ever be built.

Residual doc-inference (honest): the vendor doc does not explicitly state that the
absolute `terminationTime` CONFIG re-arms after a preemption stop -> resume (the
read-only timestamp is "cleared" while stopped; the rerun-fails-when-past rule
implies the config persists). This and the local-SSD STOP path are pinned by the
MANDATORY sub-dollar CAP-PROBE (PROPOSED-CC-13) before build freeze: tiny Spot VM
+ 1 local SSD + short terminationTime + STOP; verify (a) it stops at the time,
(b) the config survives a manual stop/start and re-arms, (c) a past-time restart
is refused, (d) discard-at-termination behaves. The probe's recorded results gate
oracle group 30.

### R3.2 Contract impact (schema /2)

Under variant B the handoff provider block cannot honestly carry the /1 literal
`instance_termination_action == "DELETE"` (the live unified field is STOP; the
wonu lesson forbids attesting what is not there). LC-8v3 bumps the handoff schema
to `kot-f1k-construction-handoff/2`: the provider block carries a `cap` sub-object
(mechanism `gce-termination-time`, action `STOP` marked as the unified
shared-with-preemption action, intended time + live read-back) and a `cleanup`
sub-object (verified-deletion semantics + reaper identity). `validate_handoff`
refuses /1; `build_runtime_license` and the b0 fixtures follow. The two-axes wonu
pin re-lands in /2 form: the cap attestation is populated ONLY from the LC-5
composite (whose L1 leg is the live scheduling read-back), never by echoing a
provisioning flag, and guard step 3'(b) asserts the preemption-axis value (STOP)
live and separately. If the maintainer picks variant A, /1 stands and this item
is dropped — the schema choice follows the fork.

### R3.3 Budget attestation, closed (delta-check #2 partial -> closed)

LC-6v3 extends R2.2: REJECT any narrowing filter beyond the single-project scope
(`services`, resource ancestors, labels, subaccounts; credit treatment must be
the default all-credits basis); REQUIRE an explicit budget period (calendar or
custom) covering the campaign window; REQUIRE live project-to-billing-account
linkage (billing projects describe: account name == `KOT_GCP_BILLING_ACCOUNT` AND
billing enabled); REQUIRE EFFECTIVE notifications — `monitoringNotificationChannels`
non-empty with every channel fetched and in VERIFIED/enabled state (Monitoring API
read), not merely present. All folded into the closed attestation preflight
returns.

### R3.4 Attestation freshness (delta-check #3 residual -> closed)

LC-8v3: `validate_handoff(record, *, now_utc)` requires
`campaign_started_at_utc <= now_utc + 60 s` and
`campaign_started_at_utc <= created_at_utc <= now_utc + 60 s`; the guard repeats
the check with its own fresh clock at license load (guard step 3'(e)). A future
start can no longer understate exposure in either the validator or the guard.

### R3.5 Guard budget-refetch honesty (delta-check note -> closed)

Rev2's guard-live-budget-refetch claim is WITHDRAWN (the guest lacks budget IAM by
design). Wiring as corrected in R2.2's Rev3 note: control-box live verification at
preflight + continue; guard verifies the attestation BYTES against the handoff-
carried sha; post-launch periodic live re-checks belong to the control-box
reaper/monitor (best-effort, disclosed) plus the budget's own threshold alerts.

### R3.6 Oracle additions (groups 28-38; group 17 becomes conditional)

Group 17 (Scheduler-job cases) applies ONLY if the optional off-box cleanup is
built; groups 19/25 (L2), 18 (IAM), and all others stand. New mandatory groups:

28. Provision request body: terminationTime == epoch+900h, unified action STOP,
    SPOT, discard-local-SSD flag all asserted in the $0 plan/provision oracle;
    any missing -> refuse BEFORE create.
29. Post-create read-back mismatch or failure -> fail-closed delete of the new VM
    with poll-to-DONE + absence verified (order-recording fake asserts the full
    sequence and the nonzero exit).
30. Provider-semantics gate: the CAP-PROBE checklist (stop-at-time, config re-arm
    across stop/start, past-time restart refusal, discard behavior) exists and its
    recorded live results are GREEN; the oracle refuses build-complete status
    without them (PROPOSED-CC-13).
31. Phase-4 L1 re-probe: scheduling patched/removed between preflight and cancel
    (fake returns drifted terminationTime / missing limit / wrong action) ->
    refuse BEFORE `shutdown -c`.
32. Teardown ordering: delete -> DONE -> absence -> cleanup-removal asserted by
    ordinal; VM-delete failure or operation error -> cleanup NOT removed, nonzero
    exit; absence-check failure -> retries, never proceeds.
33. Budget extras: services/labels/ancestors/subaccounts filters present ->
    refuse; project not live-linked to the expected billing account -> refuse;
    unverified/disabled notification channel -> refuse; missing period -> refuse.
34. Future start: `campaign_started_at_utc` beyond now+60 s, or > created_at ->
    validator refuses AND guard (fresh clock) refuses.
35. config-cost (LC-13): missing evidence file / tampered sha / arithmetic or
    instance-binding mismatch -> refuse; `--prior-usd`/`--prior-hours` supplied
    at all (including zero) -> hard error; evidence-derived values flow into the
    emitted config.
36. Guard budget honesty: guard fixture asserts NO live budget call is attempted
    guest-side; attestation byte-sha verification only.
37. Cleanup on a stopped instance: reaper fake deletes a TERMINATED-state
    instance -> poll DONE -> absence verified; transient delete failures ->
    retry-until-absent (exercises the delete path itself, not just config —
    closing the delta-check's group-20 gap).
38. Schema /2 (if variant B): /1 handoff refused; /2 fixture with the live-STOP
    cap attestation passes; a /2 handoff whose cap block echoes the provisioning
    flag value without the LC-5 composite -> refused (the wonu pin, /2 form).

### R3.7 New/changed LC items (Rev3)

| LC | Site | Change |
|---|---|---|
| LC-3v3 | `f1k_ops.py` | `verify_provider_cap` = live scheduling read-back (replaces the Scheduler job create/verify) |
| LC-8v3 | `validate_handoff` | + `now_utc` freshness param (R3.4); + schema /2 provider block (R3.2, variant-B branch); + budget resource format |
| LC-6v3 | `assure_billing_budget` | + no-extra-filters, period, live linkage, verified channels (R3.3) |
| LC-10v3 | `cmd_provision` | cap fields INSIDE the create request; immediate post-create read-back; verified-completion cleanup delete on failure (R3.1) |
| LC-11v3 | `cmd_teardown` | frozen delete->DONE->absence->cleanup ordering (R2.7 table, revised row) |
| LC-13 | NEW: `cmd_config_cost` (`f1k_bringup_gate.py:1787`) | require + validate `--prior-evidence`; refuse manual `--prior-usd`/`--prior-hours` outright (delta-check #5) |
| LC-14 | NEW: control-box cap-reaper entrypoint (`f1k_gcp.py`) | post-deadline verified deletion loop (delete -> DONE -> absence, retries until absent), nohup watchdog pattern; best-effort by design (PROPOSED-CC-12) |

### R3.8 Delta-check disposition summary

| Delta-check finding | Disposition |
|---|---|
| #1 OIDC-vs-OAuth | ADOPTED-BY-ELIMINATION — no external caller in the load-bearing cap (native); OAuth spec retained for the optional cleanup only (R3.1) |
| #2 async completion | ADOPTED-BY-ELIMINATION for the cap; ADOPTED as poll-DONE+absence for cleanup, teardown, and the provision fail-closed delete (R3.1, LC-11v3, LC-14) |
| #3 cron granularity/retries | ADOPTED-BY-ELIMINATION — no schedule encoding in the native cap; minute-floored UTC cron specified for the optional cleanup only |
| #4 L1 TOCTOU + teardown ordering | ADOPTED — phase-4 re-probes BOTH L1 (scheduling read-back) and L2; teardown ordering frozen delete->DONE->absence->cleanup with failure leaving caps armed (phase 15, LC-11v3) |
| #5 config-cost binding | ADOPTED — LC-13 makes `cmd_config_cost` require the evidence and refuse manual priors including zero |
| Budget partial | CLOSED — R3.3 extensions |
| Attestation residual (future start) | CLOSED — R3.4 freshness in validator + guard |
| Guard budget-refetch not wired | CLOSED — claim withdrawn; honest control-box-side wiring stated (R3.5) |
| Oracle gaps | CLOSED — groups 28-38 (R3.6) |
| Confirmed-fixed #4/#5 (Rev1 numbering) | PRESERVED — axes check unchanged; epoch ordering strengthened (cap inside the create request; verified-completion cleanup) |

---

## Self-check (Rev2 — superseded by the Rev3 self-check below; retained for the record)

1. End-to-end runnable on Single-VM-Spot: YES — phases 0-6 fully ordered with the
   Rev2 amendments; staging delta exhaustive (section 8, items 1-8 + the L1
   provision-time job + the code deltas); build-order rule strengthened to
   before-any-provision (R2.5); nothing depends on an undefined variable or an
   operator-invented value.
2. Rate-equality gate: unchanged from Rev1 (reviewer-confirmed sound) — fail-closed,
   zero tolerance on canonical Decimal forms, round-trip-safe, drift remedy
   specified. Section 3.
3. preflight_launch_gate wired (Rev2-extended transports incl. scheduler/IAM legs;
   epoch pre-create) and wonu resolved STRUCTURALLY this time: the termination
   action is copied from the new `verify_cap_armed` composite attestation which
   cannot exist unless every cap leg verified; Rev1's non-implementable
   `verify_selfdelete_armed` provenance claim is withdrawn and corrected (R2.3).
4. $0 oracle: 16 Rev1 assertion groups + 11 Rev2 groups (17-27) covering
   delete-IAM/outage, stopped-at-deadline, epoch ordering + fail-closed provision
   delete, mirror-required, budget scope, armed-hours integrity, TOCTOU re-probe,
   guard poll-time kills, and systemd/sha mechanics — all injectable fakes, no
   spend. Sections 6 + R2.6.
5. Review findings: all 5 blocking defects ADOPTED with mechanical fixes; all
   engineering corrections ADOPTED (one with a stated modification); the two
   reviewer-confirmed-sound elements left undisturbed. R2.8 table. Honest note:
   defects #1/#2/#3 were defects in the LANDED option-B module that Rev1 built on
   top of without catching — Rev1's "changes no landed validator" scope claim is
   withdrawn, and the LC register (R2.7) flags every landed-code change for
   re-verification.
6. Load-bearing claims tagged: marker-form premise lines open with complete
   [MEASURED: ...] tags (`tools/registry/claims-check.py` re-run after Rev2: PASS —
   count reported in the hand-back); stipulated choices are inline-tagged
   PROPOSED-CC-1..10 in non-marker prose (the lint requires marker-form STIPULATED
   to cite a registered ASM-id, which cannot exist pre-commit; the executor
   registers them at commit); the single EXTRAPOLATION (PROPOSED-CC-6) remains
   load_bearing: false with a resolution path and is a premise of nothing.
7. No `ASM-<number>` minted — PROPOSED-CC-* only. Re-checked by grep after Rev2.
8. No @handle/account strings. Re-checked by grep after Rev2.
9. Nothing committed, deployed, registered, or run: this file remains the sole
   artifact; no git/bd/gcloud state was mutated by its author in either revision.

---

## Self-check (Rev3 — re-run in full; honest report)

1. The cap-mechanism fork is RESOLVED from the vendor doc, not guessed: unified
   `instanceTerminationAction` confirmed; absolute-vs-duration semantics
   confirmed; past-time restart refusal confirmed; the two remaining doc-inferred
   behaviors (config re-arm across stop/resume; local-SSD STOP path) are pinned by
   a mandatory sub-dollar CAP-PROBE before build freeze rather than assumed
   (R3.1, PROPOSED-CC-13). The recommendation (variant B) and the rejected
   alternative (variant A) are both stated with reasons; the maintainer call is
   flagged, and the design is buildable on B with A documented as the delta.
2. The load-bearing cap now has NO external caller, auth, schedule encoding, or
   retry semantics — delta-check #1/#2/#3 are eliminated, not patched; their
   mechanics are retained correctly-specified ONLY in the optional non-load-
   bearing cleanup (R3.1, PROPOSED-CC-12). Deletion is decoupled into verified
   cleanup (delete -> DONE -> absence) whose failure leaks bounded stopped-VM
   storage, disclosed with a dollar order.
3. Delta-check #4 closed: phase 4 re-probes BOTH L1 and L2 immediately before the
   max-life cancel; teardown ordering frozen with VM-delete failure leaving all
   caps armed (phase 15, LC-11v3). Delta-check #5 closed mechanically: LC-13
   names the real site (`cmd_config_cost`, f1k_bringup_gate.py:1787), requires
   the evidence, and refuses manual priors including zero.
4. Budget closed per R3.3 (no extra filters, explicit period, live linkage,
   verified channels); attestation freshness closed per R3.4 (validator `now_utc`
   + guard fresh-clock repeat); the unwired guard budget-refetch claim is
   withdrawn and replaced with the honest control-box-side wiring (R3.5).
5. Confirmed-fixed items preserved, not regressed: the STOP/DELETE axes check
   survives in /2 form with the preemption axis asserted live and the cap
   attestation sourced only from the LC-5 composite; epoch ordering is
   strengthened — the cap rides inside the create request, with immediate
   read-back and verified-completion cleanup on failure (R3.1/R3.2).
6. Load-bearing claims tagged: the new R3.1 premise line opens with a complete
   [LIT-BACKED: vendor doc URL, fetch date] tag; `tools/registry/claims-check.py`
   re-run after Rev3: PASS (count reported in the hand-back); stipulated choices
   remain inline-tagged PROPOSED-CC-1..13 (registered by the executor at commit);
   no EXTRAPOLATION is a premise of anything (PROPOSED-CC-6 remains
   load_bearing: false).
7. No `ASM-<number>` minted — PROPOSED-CC-* only. Re-checked by grep after Rev3.
8. No @handle/account strings. Re-checked by grep after Rev3.
9. Nothing committed, deployed, registered, or run across all three revisions;
   the only tool actions besides reads were documentation fetches of public GCP
   docs and edits to this file.
