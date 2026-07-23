<!-- Provenance: Fable (architecture-advisor), 2026-07-23, bead kernel-of-truth-700k
     (+ folds in kernel-of-truth-wonu). Design/spec ONLY: nothing here is committed as
     executed work, deployed, or run by the author. The coordinator's executor builds
     this and a cross-vendor (GPT-5.6) review gate runs BEFORE any construction dollar.
     Supersedes-in-part: the plan-v4 REJECT's #3 staging characterization (stale against
     the landed bringup-deploy; see section 1). Defers-to: poc/gcp/F1K-CONSTRUCTION-
     SIDE-PLAN.md sections 2-3 (handoff schema + guard 15-step pre-spend order) and the
     landed option-B units in poc/gcp/f1k_ops.py (commit 153b9576, review-clean). -->

# F1-K `construction-continue` transition — implementable design

Bead `kernel-of-truth-700k`: the runnable, guarded, NO-SPEND transition from a GREEN
bring-up verdict to guard-wrapped Spot construction on the SAME GCE instance
(Single-VM-Spot, `poc/gcp/F1K-CONSTRUCTION-LAUNCH-ARCH.md`). This document is the
build spec for the executor; the paid construction RUN remains separately gated on the
maintainer spend-GO (issue #55) and is out of scope here.

Scope choice (a STIPULATED design choice, PROPOSED-CC-1; the executor registers it
as an ASM at commit): this design targets the lean-B contract already frozen in
`poc/gcp/f1k_ops.py` (schemas `kot-f1k-construction-ready/1`, `kot-f1k-bringup-gate/2`,
`kot-f1k-construction-handoff/1`, `kot-f1k-runtime-license/1`, `kot-f1k-rate-evidence/1`)
and changes NO landed validator, scientific pin, frozen window, sampling rule, or
builder byte [STIPULATED design choice PROPOSED-CC-1: the review-clean contract module
is the fixed interface; the transition is built AROUND it, so a contract edit re-enters
review only if a genuine defect is found].

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
5. Wall-clock sufficiency: `remaining_h = 900 - elapsed_hours(epoch)` must be `>=`
   the gate's +1SE projected instance-hours plus reserve-hours
   (`projection.instance_hours.hi` + `8/rate`); refuse `ERR_F1K_CONTINUE_WALLCLOCK`
   otherwise — never launch a run the 900 h self-delete is already guaranteed to kill
   [STIPULATED policy PROPOSED-CC-3: +1SE branch chosen as the conservative bound; a
   refusal here is a maintainer surface, not a retry].
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
    from the GCS mirror (authoritative copy; `_resolve_epoch_launch` semantics —
    mirror-only is valid, disagreement refuses). The epoch itself is written ONCE at
    provision time (section 4.1).
11. Render + install the B2 self-delete units (`render_selfdelete_unit` with
    `deadline = compute_selfdelete_deadline(epoch)`), `systemctl daemon-reload`,
    enable + start the timer. Idempotent: identical unit text re-install is a no-op;
    differing text refuses.

Phase 2 — the single pre-spend gate:

12. `preflight_launch_gate` (section 4) with real transports. `go: false` refuses and
    STOPS — deliberately leaving the B2 timer armed (an armed self-delete on a VM we
    are keeping is conservative, and `teardown` remains available).

Phase 3 — artifact placement (atomic, sha-read-back):

13. Write `live-rate-evidence.json` (canonical bytes from the SAME
    `resolve_live_rate` evidence used by the equality gate, re-checked for
    three-way canonical equality gate == preflight == evidence), scp to
    `/home/ubuntu/f1k-gate/live-rate-evidence.json`, read back sha.
14. Scp the GREEN gate artifact to `/home/ubuntu/f1k-gate/bringup-gate.json`
    (atomic: temp name + `mv`), read back sha == local sha.

Phase 4 — backstop swap (ordering is the point):

15. ONLY after preflight verified B2 armed: cancel the bring-up guest max-life
    (`sudo shutdown -c`). Order recorded in the continue transcript; the oracle
    asserts verify-before-cancel (this is F1K-CONSTRUCTION-LAUNCH-ARCH's "cancel the
    bring-up shutdown only after the provider delete is verified", adapted to the
    landed systemd mechanism).

Phase 5 — handoff production (section 4.2 for the provider block):

16. Build `construction-handoff.json` per the frozen contract; self-validate with
    `validate_handoff` AND `build_runtime_license(ready, gate, handoff)` locally —
    a handoff the guard would refuse is never uploaded. Atomic-write locally, scp to
    `/home/ubuntu/f1k-gate/construction-handoff.json`, read back sha.

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
| `machine_type`, `local_ssd_count` | `n2d-highmem-8`, `2` (landed constants) |
| `s_per_prefill` | the gate artifact's blended s/prefill (the measured value the projection used) — B4's product window then re-checks affordability shape at the live rate |
| `systemctl_transport` | SSH wrapper: the five fixed read-only queries (`is-active`, `oncalendar`, `persistent`, `triggered-unit`, `exec-start`) via `gcloud compute ssh ubuntu@<vm> -- systemctl show ...`, each mapped to the exact string the verifier expects; any SSH failure raises -> preflight returns NO-GO |
| `budget_transport` | Billing Budgets API get via gcloud, control-box credentials |
| `catalog_transport` | the landed live Cloud Billing Catalog HTTP transport |

Epoch origin: `cmd_provision` is extended to call `write_launch_epoch(now)`
immediately after a successful `instances create`, writing the control-box local
cache AND the GCS mirror (write-once; identical re-write idempotent; overwrite
refuses — B1 semantics) [MEASURED contract: `poc/gcp/f1k_ops.py:4963-5037`]. This
anchors the 900 h wall-clock cap at VM CREATION, covering bring-up + construction
on the one instance — strictly conservative, and it is what makes preflight's
`elapsed < 900` and seam ARMED-899 coherent. Provision refuses if an epoch already
exists for a live VM name (reuse-gate parity).

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
implemented by the B2 systemd self-delete (`_selfdelete_exec_start`,
`f1k_ops.py:5119-5128`). The diagnosis was ratified in the bead kernel-of-truth-wonu
notes, 2026-07-19.

Producer rule (normative, with the inline comment the wonu bead requires at the
populate site):

- `provider.instance_termination_action` := the literal `"DELETE"`, set ONLY from the
  CAP mechanism: the producer copies it from a successful
  `verify_selfdelete_armed(...)` result (which proved the timer is active,
  persistent, armed at exactly `epoch+900h`, and that its triggered service deletes
  THIS instance/zone/project). It is NEVER read from, derived from, or compared
  against the GCP `--instance-termination-action` provisioning flag. Comment at the
  site: `# CAP axis (900h systemd self-delete), NOT the Spot-preemption STOP flag —
  see bead wonu; echoing the GCP flag here produces a correct fail-closed refusal at
  validate_handoff and strands the launch.`
- `provider.termination_time_utc` := `compute_selfdelete_deadline(epoch_launch)` (the
  intended deadline).
- `provider.termination_timestamp_utc` := `verify_selfdelete_armed()["deadline_utc"]`
  (the READ-BACK attestation). `validate_handoff` requires the two equal — that
  equality is the "read-back DELETE" proof.
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
- Fail-closed statement: if `verify_selfdelete_armed` did not succeed this run, the
  producer has no value to copy and REFUSES — the handoff cannot be written with an
  unverified cap attestation, so the STOP-echo hazard the wonu bead names is
  structurally unreachable, not merely discouraged.

---

## 5. The guard `--handoff` interface (what continue depends on)

The construction unit's `ExecStart` is `guard --handoff <canonical path>`, so the
transition is runnable ONLY with the B3 guard delta landed. This design adopts the
already-in-repo spec — `poc/gcp/F1K-CONSTRUCTION-SIDE-PLAN.md` section 3 (the 15-step
pre-spend order) and its B3 unit — as the guard-side contract, and constrains it to:

- `--handoff PATH` loads READY + gate from the handoff's canonical refs (byte-sha
  equality), then `build_runtime_license(ready, gate, handoff)`; all legacy guard
  flags become optional and, if supplied, must equal the license values exactly;
- live identity (numeric ID + boot_id + SPOT) and live-rate canonical equality with
  the license are re-verified INSIDE guard before reset consumption, the engagement
  probe, or any engine start; a per-poll rate sentry kills the process group and
  writes a durable terminal `rate-drift` event via the landed terminal-stop mechanics
  on drift or quote outage;
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
2. Every path the license references (builder, driver, engine, weights, tokenizer
   artifact, dump patch, token sidecar, pin, rundir/workdir/out parents, payload
   manifests, `f1k_bringup_gate.py` at the payload root) EXISTS in the fixture root —
   asserted by enumerating the runtime-license paths and stat-ing each. A fixture
   with `f1k_driver.py` deleted FAILS this check (regression pin against the original
   #3 gap).
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
   the recorded call order satisfies: selfdelete-verify (inside preflight) BEFORE
   max-life cancel BEFORE handoff write BEFORE unit start (#2-adjacent ordering).
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

Regression baseline: the four landed oracles (`bringup-deploy --selftest`, worker
`--selftest`, `gate --selftest`, `f1k_ops.py selftest`) still pass, and
`build_carriers.py` remains byte-identical `a92be3e4...` — the continue build touches
neither.

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
- Bring-up dollars and instance-hours are carried into the eventual config-cost basis
  (they share the 900 h wall clock with construction under the provision-time epoch —
  section 4.1), so they cannot disappear from the analysis basis.

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
| 5 | B2 self-delete timer + service units | `/etc/systemd/system/` | rendered, installed, started, verified via preflight |
| 6 | `kot-f1k-construction.service` (guard ExecStart) | `/etc/systemd/system/` | installed + started + verified phase 6 |
| 7 | guest max-life CANCELLATION | VM | only after B2 verified (phase 4) |

Code deltas shipped with the build (not staged at continue time): the
`construction-continue` entrypoint + `f1k_ops` import + provision epoch-write +
`ubuntu@` SSH targeting in `f1k_gcp.py`; the guard `--handoff` (B3) delta in
`f1k_bringup_gate.py`; both land BEFORE any bring-up deploy.

---

## 9. Open items for the maintainer (none block the executor build)

1. `KOT_GCP_BILLING_ACCOUNT` + the $300 Billing Budget resource must exist before a
   real run (known GCP env/IAM setup gate; preflight fails closed without it).
2. Ratify the PROPOSED-CC-5 allowance numbers ($20 non-compute, $10 rate headroom) at
   the #55 spend-GO. Arithmetic, not policy, is what the code enforces.
3. The construction spend-GO itself (#55) — explicitly out of scope here.

## 10. Assumption register (PROPOSED — the executor registers on commit; no ids minted here)

- PROPOSED-CC-1 [STIPULATED]: the review-clean `f1k_ops.py` contract (153b9576) is
  the fixed interface; this design edits no validator. Owner: coordinator.
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
  is LIT-BACKED to the vendor doc it links).

---

## Self-check (mandatory, performed before hand-back)

1. End-to-end runnable on Single-VM-Spot: YES — precondition GREEN-on-this-instance;
   phases 0-6 fully ordered; staging delta enumerated exhaustively (section 8, items
   1-7 + the two code deltas); build-order constraint stated (B3 before deploy);
   nothing depends on an undefined variable or an operator-invented value.
2. Rate-equality gate: fail-closed (NO-GO on mismatch AND on quote outage), zero
   tolerance on canonical Decimal forms, round-trip-safe because both sides pass
   through the single normalizing canonicalizer and floats are refused as inputs;
   drift remedy specified ($0 re-collect/re-gate). Section 3.
3. preflight_launch_gate wired (phase 2, full transport table, epoch origin at
   provision) and wonu resolved: `instance_termination_action` populated ONLY from
   the `verify_selfdelete_armed` attestation with the required inline comment;
   STOP-echo structurally unreachable; fail-closed statements present. Section 4.
4. $0 oracle validates without spend: injectable fakes only, 16 named assertion
   groups covering GO/NO-GO logic, staging completeness, preflight legs, wonu
   regression pin, ordering, single-shot, and no-teardown. Section 6.
5. Plan-v4 findings: #2 resolved (mechanical interlock + ordering + normative text),
   #3 resolved (runnable transition; stale sub-claim documented), #4 resolved
   (equality at four enforcement points + remedy), #8 resolved (formula + un-trimmed
   worst case + enforced bounds). Section 7.
6. Load-bearing claims tagged: every marker-form premise line opens with a complete
   [MEASURED: file:line at commit] tag (`tools/registry/claims-check.py` run this
   pass: PASS, 5 marked premise lines); stipulated design choices are inline-tagged
   with PROPOSED-CC ids in non-marker prose, because the lint requires marker-form
   STIPULATED to cite a REGISTERED ASM-id, which cannot exist before the executor's
   commit — the executor registers PROPOSED-CC-1..6 at commit and may then promote
   those lines to marker form; the single EXTRAPOLATION (PROPOSED-CC-6) is
   load_bearing: false with a resolution path and is a premise of nothing.
7. No `ASM-<number>` minted — PROPOSED-CC-* only. Checked by grep before hand-back.
8. No @handle/account strings. Checked by grep before hand-back.
9. Nothing committed, deployed, registered, or run: this file is the sole artifact;
   no git/bd/gcloud state was mutated by its author.
