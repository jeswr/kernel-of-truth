# Correctness + spec-conformance review: F1-K option-B spend-cap backstop (`f1k_ops.py`)

Read-only correctness review of a newly-implemented, pure-local cost-accounting + timing state machine, before it is committed. No model/scientific code is involved. Repo root: `/home/ec2-user/css/kernel/kernel-of-truth`.

## Background (what B is and why it is deliberately small)
A maintainer decision selected the LEAN provider-native design (option B) over a heavier durable-ledger design (option A). B's whole job is a **hard spend cap** on a single cloud VM that runs a multi-day batch job. The hard bound is achieved by the cloud provider itself: the VM is scheduled to self-delete at a 900-hour wall-clock deadline, and because the VM (a Spot instance) resumes as the *same* instance after any interruption, its billed instance-hours can never exceed wall-clock hours, which can never exceed the cap. Two independent backstops sit under that: a $300 billing-budget alert, and a pre-spend guard that refuses to start if the live hourly price would fall outside a pre-registered affordability window. There is intentionally **no** bespoke ledger/lease machinery — please do not recommend adding one; assess only whether what is here is correct and conformant.

## What to read
- Implementation under review: `poc/gcp/f1k_ops.py` — the block between the comment banner `Option-B governance layer` and `def _main()`. New public functions: `write_launch_epoch`, `read_elapsed_hours`, `compute_selfdelete_deadline`, `render_selfdelete_unit`, `verify_selfdelete_armed`, `assure_billing_budget`, `guard_rate_within_window`, `preflight_launch_gate`; helpers `_utc_datetime`, `_elapsed_hours`, `_build_launch_epoch`, `_parse_launch_epoch`, `_load_epoch_bytes`, `_oncalendar`, `_check_rate_window`; oracle `selftest_b1` (32/32, pure-local). It builds on the existing `resolve_live_rate`, `atomic_write_json`, `canonical_decimal`, `canonical_json_bytes`, `_utc_timestamp`, `_decimal_value` — study those to judge conformance.

## Frozen numeric anchors (the values the code must enforce; verify each is used correctly)
- 900 h wall-clock cap (upper bound of `instance_hours ∈ [260.6, 900] h`, `analysis/f1k.py`).
- $300 billing ceiling (the maintainer's protective total; superset of the $155 compute cap).
- Spot hourly-rate window **[$0.081, $0.595]/h** (`poc/gcp/f1k_gcp.py`).
- Two-sided construction window: **s/prefill ∈ [47.0, 162.3] s** AND **rate × s/prefill ∈ [13.16, 27.95] $·s/h**.
- Boundary convention (matches the existing `selftest_b0` handoff validator): accept-at-equal, refuse strictly-outside.

## Part A — spec conformance
For each new function: are the signature, return shape, and behaviour consistent with the frozen anchors and with the conventions of the surrounding module (fail-closed `F1KOpsError` with stable `F1K_B_*` codes; canonical-Decimal money, never binary float; injectable transports that default to a closed/refusing state; no network at import or in the oracle)? Flag any deviation.

## Part B — correctness of the load-bearing arithmetic/state logic (what the oracle may not cover)
Scrutinise for defects independent of the passing oracle. Give a concrete input/state → wrong-output for anything real:
1. **Elapsed-time math** (`_utc_datetime`, `_elapsed_hours`, `read_elapsed_hours`): is the wall-clock hours computation exact (integer-microsecond Decimal division, no float), correct across day boundaries and fractional seconds, and does it fail closed on a future epoch, a missing epoch, or disagreeing durable sources? Is the "mirror authoritative, local must agree" rule sound for a resume-after-interruption where Local SSD contents are lost?
2. **Write-once epoch** (`write_launch_epoch`): can the launch clock ever be reset (which would extend the deadline)? Consider: mirror present but local absent, local present but mirror absent, both present with disagreement, a re-write of the identical epoch, and a mirror that returns a corrupt blob. Is the SHA self-check (`_parse_launch_epoch`) sufficient to detect tampering/corruption of the persisted record?
3. **Deadline arithmetic** (`compute_selfdelete_deadline`, `_oncalendar`, `render_selfdelete_unit`, `verify_selfdelete_armed`): is launch + 900 h computed correctly (incl. month/second granularity), is the systemd unit rendered so it fires even after a missed deadline across an interruption/reboot (`Persistent=true`), and does verify fail closed on an inactive timer or a deadline that does not match?
4. **Rate/affordability window** (`_check_rate_window`, `guard_rate_within_window`): are all three constraints (rate, s/prefill, product) enforced with the correct comparison direction and accept-at-equal boundary? Is the product computed exactly? Can any too-cheap/too-fast or too-expensive/too-slow combination pass?
5. **Budget assurance** (`assure_billing_budget`): does it fail closed on absent / wrong-amount / no-alert / malformed budget objects and on a missing transport?
6. **Preflight orchestration** (`preflight_launch_gate`): does it return GO only when every sub-check passes, NO-GO with the correct reason on each single failure, and is the deadline-consistency check (deadline_utc must equal launch + 900 h) correct? Any check whose failure could be swallowed into a GO?

## Part C — disclosed seams (adjudicate each: accept / accept-with-follow-up / must-fix)
1. `read_elapsed_hours` treats the mirror as authoritative and a present local copy as a cross-check; with `mirror_transport=None` it reads local only. Is that read-path acceptable given the write path *requires* a mirror?
2. `preflight_launch_gate` includes the epoch/deadline/self-delete/budget/rate checks but does NOT re-run the full construction-handoff/instance-identity attestation (`validate_handoff`, `resolve_live_instance_identity`) — those stay in the launch script that already calls them. Is deferring them out of this gate acceptable, or should the gate bind instance identity too?
3. Transport ABIs (`mirror_transport(action,key,data=)`, `systemctl_transport(action,unit)`, `budget_transport(action,billing_account=)`) are this module's invention. Reasonable and unambiguous?
4. The self-delete depends on the on-VM systemd timer actually being installed+enabled by the deploy step (out of scope here); this module only *renders* and *verifies* it. Acceptable division?

## Output
Free text. Part A conformance deltas; Part B any real defect (with the failing input/state → wrong result); Part C a per-seam ruling; and an overall verdict: **sound to commit as the option-B backstop with follow-ups tracked, or must specific items be fixed first?** Be concrete and terse; this drives a commit decision.
