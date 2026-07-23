# Cross-vendor review (GPT-5.6 `gpt-5.6-sol`, xhigh) — F1-K construction-continue transition (Rev1)

> Spend-safety review of the 700k transition design (Rev1). Verdict REJECT — 5 blocking fail-open
> paths where a paid VM could survive past the 900h/$300 cap, several in the LANDED option-B code
> (153b9576). All fixed in Rev2 (provider-side Cloud Scheduler cap + LC-1..12 landed-code changes).
> Committed for the record. Runner: poc/gpt56-review/run-review.sh (npx-pinned codex 0.144.1).

---

# Verdict: **REJECT**

The rate-equality design is basically sound, and the construction payload is present. However, the proposed 900-hour and $300 backstops are not mechanically fail-closed. There are concrete paths where the guest max-life is cancelled, construction launches, and the VM can survive past the claimed cap.

## Blocking spend-safety defects

1. **B2 attests unit configuration, not successful deletion capability.**

   `verify_selfdelete_armed()` proves only that systemd reports an active timer and an exact command string ([f1k_ops.py:5204](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:5204)). It does not prove:

   - the VM service account has `compute.instances.delete`;
   - `/usr/bin/gcloud` can authenticate at the deadline;
   - the Compute API is reachable;
   - deletion succeeds.

   Worse, the deletion service retries only six times at 30-second intervals and then exits permanently, with no `Restart=on-failure` or shutdown fallback ([f1k_ops.py:5119](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:5119), [f1k_ops.py:5150](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:5150)).

   Exact leak path:

   `timer text verifies → preflight GO → sudo shutdown -c → guard launches → deletion IAM/network failure at 900h → service gives up → running VM remains billable indefinitely`.

   A Spot preemption with action `STOP` creates another hole: if the VM is stopped at the deadline, the guest timer cannot execute until somebody restarts it. Persistent-disk and other retained-resource charges continue while stopped. Google documents that stopped VMs retain chargeable resources such as persistent disks, and budgets do not cap spending. [Stopped-instance charging](https://docs.cloud.google.com/compute/docs/reference/rest/v1/instances/stop), [budget behavior](https://docs.cloud.google.com/billing/docs/how-to/budgets).

   **Required fix:** use an independent provider-side absolute deletion or external authenticated scheduler with durable retries. If retaining `STOP` for preemption, keep a separate provider/control-plane DELETE backstop; do not represent the guest timer as a hard VM-deletion cap. At minimum, retain a guest poweroff fallback and verify deletion IAM before cancelling the 15-hour shutdown.

2. **The $300 budget check does not verify the claimed project-scoped resource.**

   `assure_billing_budget()` accepts only normalized amount and a nonempty threshold list. It receives no project ID or budget resource name and returns neither ([f1k_ops.py:5290](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:5290)). Therefore an account-wide $300 budget—or one filtering another project—can pass. Google explicitly supports both account-wide and filtered/project-scoped budgets. [Budget API scope](https://docs.cloud.google.com/billing/docs/how-to/budget-api).

   Meanwhile, `validate_handoff()` accepts any nonempty `resource_name` and merely checks that the handoff itself echoes the live project ID ([f1k_ops.py:3052](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:3052)). Nothing binds those fields to the API result.

   **Required fix:** require an exact configured budget resource, validate its billing account, USD currency, `$300` amount, project filter, thresholds, and notification configuration, and return that closed attestation through preflight for direct handoff population. Add wrong-project/account-wide/wrong-currency oracle cases.

3. **The wonu “verified DELETE provenance” is not structurally implemented by the fixed interface.**

   The design says `DELETE` is copied from `verify_selfdelete_armed()`, but that function returns only `armed`, `deadline_utc`, `oncalendar`, and `target`—no action field ([f1k_ops.py:5280](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:5280)). The handoff validator merely tests a literal `"DELETE"` and equal timestamp strings.

   It also does not recompute `armed_hours_decimal` from `campaign_started_at_utc` and `termination_time_utc`. A handoff with an actual 899-hour interval but `"armed_hours_decimal":"1"` can satisfy the validator’s `$300` arithmetic ([f1k_ops.py:2997](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:2997)).

   This contradicts the design’s claim that `validate_handoff` proves read-back DELETE and exact exposure.

   **Required fix:** change the supposedly fixed contract: return a closed cap attestation containing action/target/deadline, recompute timestamp ordering and armed hours in `validate_handoff`, and independently repeat those checks inside the guard.

4. **The inherited guard contract is contradictory.**

   The design adopts the side-plan’s exact 15-step guard order, whose step 3 requires live GCE `instanceTerminationAction=DELETE` and provider `terminationTimestamp` ([F1K-CONSTRUCTION-SIDE-PLAN.md:200](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/F1K-CONSTRUCTION-SIDE-PLAN.md:200)). Provisioning explicitly sets GCE action `STOP` ([f1k_gcp.py:576](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_gcp.py:576)).

   Following the inherited guard literally always refuses. Omitting that step to make the launch run removes the promised independent cap verification. The new design must explicitly replace that step and reverify B2 immediately before engine start and periodically thereafter.

5. **The epoch is not actually anchored conservatively at VM creation.**

   The design writes `now` after `instances create` returns. Unless `now` was captured before the create request, the deadline is later than actual VM creation, evading the claimed 900-hour wall clock by provisioning latency. A mirror-write failure after successful creation also leaves a paid VM without a durable B1 epoch.

   **Required fix:** capture the epoch no later than the create request, bind it to the numeric instance/campaign, and immediately delete the newly created VM if durable persistence/read-back fails. All epoch/cap code must land before `provision`, not merely before `bringup-deploy`.

## Other engineering corrections

- **Rate equality:** The canonical-Decimal, zero-tolerance comparison is correct. Gate and live rate strings are canonical, floats are refused, and no representation-based mismatch bypass was found. A mismatch or quote failure should remain NO-GO.

- **B4 transport false-refuse:** `projection.blended_s_per_prefill_central` is emitted as a JSON float, but `_check_rate_window()` refuses floats. Passing the gate value directly makes every real preflight fail ([f1k_ops.py:5357](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:5357)). Specify an exact compatibility conversion or add a decimal-string field.

- **Control-box identity false-refuse:** `resolve_live_instance_identity()` always reads the boot ID from the machine executing Python; boot-ID transport is not injectable ([f1k_ops.py:527](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:527), [f1k_ops.py:726](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:726)). Running it on the control box cannot yield the guest boot ID without changing the interface.

- **Wall-clock sufficiency:** The phase-0 check uses a rounded `hi` value and stale time, with no final guard-side recomputation after installation and transfer. It also is not repeated as realized performance changes. Recheck immediately before spend using conservative rounding plus transition/termination margin, then at checkpoints against the absolute deadline.

- **Plan-v4 #3:** The stale staging claim is genuinely resolved: `_construction_payload_files()` requires both `build_carriers.py` and `f1k_driver.py` ([f1k_gcp.py:169](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_gcp.py:169)). However, the oracle cannot “enumerate the driver from the runtime license,” because the runtime-license schema has no driver field; test its known staged path separately.

- **Plan-v4 #8:** The narrative is more honest, but “bring-up dollars and hours are carried into config-cost” has no executable step here. The design must produce and bind prior-hours/prior-cost evidence instead of relying on a later manual argument.

- **$0 oracle gaps:** Add delete-IAM/failure/outage, stopped-at-deadline, mirror absent while local exists, wrong budget scope/resource/currency, timestamp-to-armed-hours mismatch, B2 disarm between preflight and shutdown cancellation, guard pre-start and poll-time rate outage/drift, remote SHA failure, and systemd MainPID/ExecStart failure cases.

The build-order rule is necessary for READY’s bundle binding but insufficient: the epoch and hard-cap provisioning changes must be present before the VM is created. No paid launch should proceed from this design as written.