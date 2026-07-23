# Cross-vendor delta-checks (GPT-5.6 `gpt-5.6-sol`, xhigh) — F1-K construction-continue transition

> Spend-safety delta-checks after the Rev1 REJECT (see f1k-cc-transition-xvendor-review.md).
> Rev2 delta-check = NEW-DEFECT/STILL-REJECT (Scheduler L1 not a functioning hard cap: OIDC-not-OAuth,
> async-op not verified, cron granularity, retry semantics). Resolved in Rev3 via NATIVE GCE
> terminationTime+STOP (variant B) — collapses #1-#3 by elimination. Committed for the record.

---

## Rev2 delta-check — verdict NEW-DEFECT / STILL-REJECT

# Verdict: **NEW-DEFECT / STILL-REJECT**

Rev2 has the right architecture, but the specified L1 implementation is not a functioning hard cap. A live provision must remain blocked.

## Blocking findings

1. **The Scheduler target uses the wrong authentication type.**

   Rev2 requires an “OIDC-authenticated” direct call to `compute.googleapis.com` ([R2.1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/f1k-construction-continue-transition.md:733)). Google explicitly requires OAuth access tokens—not OIDC ID tokens—for Google APIs on `*.googleapis.com`. An OIDC-configured job can pass the proposed configuration/IAM read-back yet receive 401/403 at the deadline. [Cloud Scheduler authentication](https://docs.cloud.google.com/scheduler/docs/http-target-auth)

   Exact leak:

   `OIDC config verifies → max-life cancelled → VM STOPped or guest wedged → Scheduler DELETE rejected → finite retries exhaust → VM/resources remain billable past 900 h`.

2. **A direct Scheduler DELETE does not verify that deletion completed.**

   Compute mutations return an asynchronous `Operation`; the request is not complete until that operation reaches `DONE` without an error. Scheduler considers any HTTP 2xx response acknowledged and will not inspect or poll the returned operation. Therefore a DELETE accepted with 2xx but later failing is treated as Scheduler success, defeating the advertised retry layer. [Compute operation handling](https://cloud.google.com/compute/docs/api/how-tos/api-requests-responses), [Scheduler HTTP acknowledgment](https://docs.cloud.google.com/scheduler/docs/reference/rest/v1/projects.locations.jobs)

   L1 needs an authenticated provider-side handler that submits DELETE, polls the zonal operation, checks errors, verifies instance absence, and returns non-2xx until that is true.

3. **The absolute Scheduler deadline is not implementable as written.**

   Cloud Scheduler cron is five-field, minute-granularity, recurring, and has no year or seconds field. The landed deadline is second-granularity ([f1k_ops.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:5103)), while LC-5 requires exact L1/L2 deadline equality. Rev2 defines neither conservative minute flooring nor mandatory UTC timezone verification. [Scheduler cron format](https://docs.cloud.google.com/scheduler/docs/configuring-cron-job-schedules)

   The retry “reviewed floor” is also unspecified; Scheduler retry count is finite, after which this annual cron waits until the next scheduled occurrence. That is not a hard 900-hour cap.

4. **There are still L1-removal TOCTOU and teardown paths.**

   Phase 4 immediately re-probes only L2 before cancelling the 15-hour shutdown ([phase 4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/f1k-construction-continue-transition.md:219)). If L1 is paused/deleted after preflight, the max-life is still cancelled. The later guard refuses, but the VM is left with only the guest mechanism.

   LC-11 also says teardown deletes the Scheduler job without freezing safe ordering ([LC register](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/f1k-construction-continue-transition.md:896)). The required invariant is: delete VM, poll completion, verify absence, then delete L1. Any VM-delete failure must leave L1 armed.

5. **`prior-spend-evidence.json` is still not executable binding.**

   Rev2 produces evidence and says a runbook step “MUST consume it” ([phase 5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/f1k-construction-continue-transition.md:237)), but the exhaustive LC/code register contains no `cmd_config_cost` change. The landed command still accepts manually supplied `--prior-usd` and `--prior-hours`; supplying zero bypasses the new evidence. This leaves the prior-hours/cost correction unresolved and can understate the 900-hour/cost basis.

## Five-defect disposition

| Rev1 defect | Rev2 result |
|---|---|
| #1 hard cap | **Still open.** Provider-side concept is correct, but OIDC, asynchronous completion, timing, and retry semantics make this L1 non-hard. Correctly implemented Compute DELETE does work on a STOPped VM. |
| #2 budget scope | **Partial.** Exact resource, parent, USD, amount, and project-list validation are good. Still require rejection of extra narrowing filters (`services`, labels, ancestors, subaccounts), confirmation that the project is currently linked to that billing account, an explicit period, and effective—not merely present—notifications. The Budget API permits these additional scope fields. [Budget schema](https://docs.cloud.google.com/billing/docs/reference/budget/rest/v1/billingAccounts.budgets) |
| #3 attestation/hours | **Core bypass fixed, one residual.** The 899h-as-1h mismatch is killed, and the legitimate producer cannot proceed without the composite. But ordering alone permits a future `campaign_started_at_utc`; a hand-built handoff can still encode a future start and understate exposure. Validator and guard must require start ≤ fresh now and coherent ordering with handoff creation. |
| #4 guard contradiction | **Structurally fixed**, conditional on a functioning L1. STOP is correctly checked on the preemption axis and DELETE on the cap axis. |
| #5 epoch | **Structurally fixed**, conditional on L1. Capture/persist/arm-before-create is correctly ordered. Require actual L1 read-back before create—not merely a recorded call ordinal—and verified completion of any post-create cleanup DELETE. |

The budget attestation is bound correctly in the intended continuation producer, but Rev2’s claim that the guard re-fetches it is not wired: preflight is deliberately control-box-side because the guest lacks budget IAM, while the guard runs on the VM.

## LC/oracle assessment

The re-verification plan is not adequate yet. Groups 17–27 omit:

- OAuth-versus-OIDC, HTTP method, UTC timezone, cron rounding, and asynchronous operation failure.
- L1 pause/IAM loss between preflight and max-life cancellation.
- Teardown delete ordering and VM-delete failure.
- Extra budget filters, live project↔billing-account linkage, ineffective recipients, and period reset.
- Future campaign-start armed-hours bypass.
- Missing/tampered evidence and manual-zero substitution at `config-cost`.
- A stopped-instance test that actually exercises the delete handler and verifies absence; group 20 currently verifies configuration independence only.

## Mandatory maintainer setup gate

Before any live provision:

- Enable Cloud Scheduler, Compute, Billing Budgets, and required mirror APIs.
- Use a dedicated same-project Scheduler caller SA with **OAuth**, least-privilege `compute.instances.delete`, intact `roles/cloudscheduler.serviceAgent`, and creator `iam.serviceAccounts.actAs`. [Scheduler IAM requirements](https://docs.cloud.google.com/scheduler/docs/http-target-auth)
- Deploy and verify the delete-operation completion handler—or select native `terminationTime+DELETE` if the maintainer accepts its preemption semantics.
- Pin UTC, conservative pre-900 scheduling, retries after the deadline until absence is confirmed, and an immutable campaign/instance-ID check.
- Create the exact all-services, single-project $300 budget with effective recipients and verify the project’s live billing-account association.
- Extend `config-cost` to require and validate the prior-spend evidence directly.

Rev2 materially improves defects #3–#5, but defect #1 remains a concrete money leak and the prior-spend consumer remains unenforced.