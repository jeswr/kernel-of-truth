<!-- Provenance: authored by GPT-5.6 (codex, gpt-5.6-sol) 2026-07-18 as the overflow-design lane while Fable was capped; coordinator (Opus) transcribed. Cross-model review + Fable review pending per the memo review-gate. Source brief: scratchpad/f1k-launch-arch-brief.md. -->

# Memo: F1-K construction-launch architecture

## Decision

Choose **Single-VM-Spot**: provision the bring-up VM as Spot and retain that same GCE instance through GREEN and the first guard-wrapped construction launch.

Do not land the current `construction-deploy` as written. Refactor its useful license, SHA, manifest, and Spot-validation helpers into a same-VM `construction-continue` path. The present fresh-VM implementation validates and stages files but cannot recreate the executable environment, exactly as the review found in [f1k-cdeploy-review-VERDICT.md](/home/ec2-user/css/kernel/kernel-of-truth/poc/gpt56-review/f1k-cdeploy-review-VERDICT.md).

This deliberately changes bring-up provisioning: the documented on-demand override in [f1k_gcp.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_gcp.py:137) leaves the normative path. An on-demand bring-up may remain a diagnostic, but its GREEN artifact must not hand off directly to construction.

### Fork comparison

| Dimension | Single-VM-Spot | Two-VM + construction-prep |
|---|---|---|
| Main seam | One prepared instance: worker builds/tests, gate returns GREEN, guard launches there. | GREEN must authorize a different VM, followed by 384 GB restore, clone, patch, build, test, and provenance reconstruction. |
| Compute cost | At representative tree rates of $0.174–$0.24/h, the 2–4 h timing portion is about $0.35–$0.96. No second restore/build. | The cited $0.579/h on-demand rate makes the timing portion about $1.16–$2.32, before staging/build; 8 h is $4.63 and 15 h is $8.69. Fresh Spot preparation adds another `prep_hours × Spot_rate`. |
| Wall clock | Saves the complete post-GREEN estate restore/build/test interval. Preemption can force a 2–4 h remeasurement. | Bring-up is less likely to be interrupted, but every GREEN pays another several-hour preparation path. |
| Robustness | Fewer identity, rate, artifact, path, and TOCTOU seams. Risk: Spot may repeatedly interrupt bring-up—the current source records a roughly 75-minute operational failure mode. | Stable bring-up, but fresh Spot prep is itself preemptible and can fail after GREEN; rate and provenance can drift between machines. |
| Review surface | Provisioning policy, resumable timing, same-VM handoff, guard checks, and durable budget controller. | All guard/budget work, plus a second heavy worker/prep implementation and its complete provenance equivalence proof. |

The dollar figures above are illustrations, not phase bounds. Construction’s 27–38-day duration and frozen `[260.6,900] h / [$73,$155]` window are unchanged under either fork.

## Clean gated handoff

1. **Provision one Spot instance.** `provision` must require `provisioningModel=SPOT`, the frozen machine type/zone, the required service account permissions, and durable control state. `KOT_F1K_ONDEMAND=1` must be refused for this normative path.

2. **Stage the complete payload before bring-up.** Extend `bringup-deploy` to include the tracked construction subset, including the byte-frozen builder and driver, rather than staging them after GREEN. The worker continues to restore the estate and build/test both engines as it already does in [f1k_worker.sh](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_worker.sh:117).

3. **Emit an executable ready manifest.** After engine tests, the worker writes `construction-ready.json` containing:

   - numeric GCE instance ID, project, zone, machine type, provisioning model, and boot/start identity;
   - builder absolute path and `a92be3e4…` SHA;
   - engine and tokenizer JSON argv;
   - tokenizer SHA/artifact;
   - engine-weights SHA/artifact;
   - dump-patch SHA/artifact;
   - token-sidecar path/SHA;
   - pin path/SHA/PIN_GB;
   - explicit rundir, workdir, and output paths;
   - source/bundle manifest SHA and engine-test evidence.

   No `KOT_F1K_*` placeholders remain for an operator to invent.

4. **Finish the existing bring-up protocol.** The runner confirms dump checks (a) and (c), reruns `collect` without retiming, and the control box runs `gate`. The VM remains alive and prepared.

5. **Return GREEN to that instance.** A refactored `construction-continue` verifies the same numeric instance ID, copies the exact GREEN artifact to the canonical path, starts and verifies the durable budget controller, and writes `construction-handoff.json`. Its SHA is also placed in a control-plane instance metadata attribute so copying or editing the local bundle cannot satisfy another VM.

6. **Invoke guard, not the builder.** `construction-continue` starts a detached/systemd unit whose `ExecStart` is the reviewed `guard --handoff …` command. Guard remains the only process that launches `build_carriers.py`.

This path is runnable end to end: it does not merely print a command or rely on undefined environment variables.

### Spot-safe timing

The sampling rule is already deterministic: fixed corpora, `SAMPLE_SEED`, deterministic rank selection, and stable sample IDs in [f1k_bringup_gate.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_bringup_gate.py:310).

Add a timing-epoch protocol:

- Persist and GCS-mirror `timing-epoch.json`, binding the sample-manifest SHA, corpus/tokenizer/engine/weights hashes, OMP settings, instance ID, and boot identity.
- Write every result and T1 stats file using temporary-file, fsync, atomic-rename semantics.
- Make `collect` reject duplicates, mixed epoch IDs, and partial sets. The current last-row-wins `_read_results` behavior at [f1k_bringup_gate.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_bringup_gate.py:484) is insufficient for resumability.
- If preemption occurs before construction SPEND-START, preserve estate/build state when valid but invalidate the incomplete timing epoch and rerun the complete T1→pin→T2 sequence against the same immutable sample manifest. This avoids mixing measurements from different boots or deriving a pin from a partial T1 union.
- If preemption occurs after GREEN but before SPEND-START, a changed boot identity invalidates the handoff; remeasure/re-gate on the current boot.
- Once construction has started, resume through the existing bound per-concept checkpoints and the new cumulative spend ledger rather than repeating bring-up timing.

## Finding-by-finding resolution

### 1. Decimal round-trip

The defect originates where `collect` validates the operator string by converting it to `float` and then serializes the rounded value in [f1k_bringup_gate.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_bringup_gate.py:543).

Resolution:

- Parse the original quote with `Decimal`, reject non-finite/non-positive values, and canonicalize numeric equality (`0.190` → `0.19`) without passing through binary float.
- Preserve that exact canonical string in the gate inputs and artifact, for example `rate.usd_per_hour_decimal`.
- Keep the existing numeric field only as a derived compatibility/projection value if changing all consumers is undesirable. Exact licensing comparisons use the canonical field.
- The live-rate resolver produces the same canonical representation.
- Add the rejected-review case `0.10000000000000001`, plus trailing-zero and exponent-form cases, to the oracle.

### 2. Full license at the spend boundary

`construction-deploy` checks several facts but launches nothing. Guard currently reaches its engagement probe and builder launch without those facts at [f1k_bringup_gate.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_bringup_gate.py:1501).

All authoritative checks must move into `guard`, before reset consumption, the dump-mode engagement probe, or any engine start. Guard must additionally re-verify:

- the required handoff manifest exists and its SHA equals the live instance-metadata attestation;
- the handoff’s numeric instance ID, project, zone, machine type, and boot identity equal live metadata;
- live scheduling metadata says `SPOT`;
- the authoritative live all-in rate quote is available and canonically equals the GREEN gate rate;
- local gate bytes equal the handoff’s gate SHA, with schema `/2` and verdict GREEN;
- the pin bytes/PIN_GB and Add7 block already checked by the landed guard;
- `args.tokens` bytes equal `gate.model_bundle.tokens_full_sha256`;
- the exact builder path resolves to `build_carriers.py`, its bytes equal `a92be3e4fe535…`, and the argv invokes `construct`; arbitrary builder programs are refused;
- engine/tokenizer argv and every provenance SHA/artifact pair exactly match `construction-ready.json`, with artifact bytes rehashed;
- the source/bundle manifest is complete and unchanged;
- rundir/workdir/out are the reviewed paths and an exclusive run lock is held;
- a valid, unexpired spend lease exists and the durable ledgers remain below their caps.

After verification, execute the validated absolute builder path. Make the payload tree read-only and rehash immediately before the probe; hostile root mutation can remain outside the stated threat model, but normal post-deploy modification and bundle copying must fail mechanically.

Keep the gate change small: add the runtime-license verifier, `--handoff`, builder/token checks, and corresponding refusal oracles around `cmd_guard`. Do not touch sampling, projection geometry, scientific pins, or the builder.

### 3. Durable cumulative time and cost

The existing checkpoint uses the frozen artifact rate for both projection and realized dollars [f1k_bringup_gate.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_bringup_gate.py:1032), while the current watchdog has an in-memory deadline and must be manually started [f1k_gcp.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_gcp.py:1225). Neither bounds cumulative billing across restarts.

Use two durable counters:

- **Frozen licensed ledger:** construction/campaign hours and dollars checked against the unchanged 900 h and $155 caps.
- **Outer operational ledger:** all F1-K infrastructure exposure checked against $300. The $300 limit does not grant automatic spend above $155; the lower currently licensed cap controls. If $300 is invoice-wide, reserve non-VM/GCS exposure up front rather than calling a compute-only counter a total bound.

The controller should:

- append hash-chained, fsynced events to durable PD/control-box storage and mirror them to GCS with generation checks;
- bind entries to numeric instance ID and record every RUNNING interval, rate quote, phase, and cost;
- reconcile an open interval after preemption from the recorded stop/start transition before issuing another lease;
- start automatically during provisioning and be verified—not merely printed;
- grant short, renewable spend leases. Guard stops when a lease expires or the controller heartbeat disappears;
- refuse launch/resume on missing, corrupt, rolled-back, or divergent ledger state;
- derive guest shutdown/systemd timers from remaining cumulative allowance on every boot rather than resetting a new 900 h timer.

The frozen performance checkpoints remain `{240,1056,2304}`, but their cap formula becomes:

`actual cumulative spend + realized-ratio × predicted remaining work + remaining reserve`

rather than scaling the whole campaign at one historic rate. Checkpoint artifacts record cumulative prior hours/dollars, remaining projection, license rate, live rate, and price-history digest.

**Yes, checkpoints must re-price remaining work at the live rate.** A rate sentry must also run on every guard/controller poll, because waiting until checkpoint 2304 leaves a long unobserved tail. If the live canonical rate differs from the current GREEN artifact, guard kills the process and writes a durable `rate-drift` terminal event. Existing timing can be recollected/re-gated at the new rate; resume requires a new GREEN handoff. There is no automatic window or ceiling change.

For a genuine hard-dollar bound, each lease also reserves its maximum unobserved exposure using a documented provider rate upper bound. If no authoritative upper bound can be established, the system must stop with sufficient fixed headroom and must not claim invoice-exact enforcement from catalog polling alone.

### 4. End-to-end runnable transition

This is structurally resolved by the same-VM fork:

- Estate, colibri checkout, KaE/dump engine, runtime dependencies, tests, and provenance already exist because the worker created them.
- The full construction source is staged before bring-up.
- `construction-ready.json` supplies every launch value currently represented by undefined variables.
- `construction-continue` installs the GREEN artifact, binds it to live instance metadata, arms and verifies the controller, and invokes guard.
- One canonical directory layout is used consistently in code and README.

Refactor the uncommitted `construction-deploy`; do not keep its fresh-VM staging/no-launch behavior as the normative command.

### 5. Existing-entrypoint regression

The rejected patch passed this finding, so retain it as an acceptance constraint.

The new fork intentionally changes provisioning policy and extends `bringup-deploy`, so byte identity is no longer the right test for those two entrypoints. Require instead:

- existing command names and argument parsing remain usable except that normative on-demand handoff is explicitly refused;
- `gate --selftest` remains green;
- module imports and shell syntax checks pass;
- the scientific files and frozen constants have no diff;
- `build_carriers.py` remains exactly `a92be3e4fe535…`;
- builder, driver, and existing gate consumers pass their current oracles;
- `ENTRY` includes the reviewed same-VM continuation command;
- direct guard invocation without a valid handoff fails before the engagement probe.

### 6. Documentation

Correct the README and construction plan as follows:

- Replace “complete environment” with the actual staged/prepared state; use the term only after `construction-ready.json` is verified.
- Say “starts and verifies the budget controller” only when that occurs. Otherwise say “prints instructions.”
- Describe the gate rate as the **authorization/projection anchor** and the live catalog quote/price history as the **billing authority**. Remove “single authoritative rate end-to-end.”
- Remove “$3–3.5 worst case.” Report formula-based estimates and the separately enforced bring-up retry/budget limit.
- State that same-VM removes inter-VM rate drift, not daily temporal price drift.
- Replace fresh-VM and `run-inputs`/`gate-tokens` contradictions with one literal canonical path set.
- Regenerate the self-check hashes after the final patch and include the new entrypoint.
- State clearly that the $155 frozen cap remains controlling; $300 is an outer maintainer-gated contingency, not an automatic enlarged license.

## Maintainer judgement versus engineering

Maintainer judgement is required for:

- accepting Spot preemption risk during bring-up instead of the current on-demand reliability preference;
- choosing the bring-up retry/cumulative-hour limit and spend-lease duration;
- defining whether the $300 ceiling includes storage and other non-GCE charges;
- any change to the frozen windows, rate window, reserve, $300 contingency, or scientific pins;
- abandoning Single-VM-Spot in favor of the two-VM preparation path after measured retry failure.

Everything else in the six findings is engineering work suitable for the review loop: decimal preservation, runtime identity checks, attestation, exact argv generation, SHA verification, durable accounting, live repricing, watchdog activation, preemption replay, path consistency, and truthful documentation.

## Implementation scope

1. `poc/gcp/f1k_gcp.py`: make the normative provision path Spot; stage the full payload initially; add live-rate/instance identity resolution; replace fresh-VM `construction-deploy` with same-VM `construction-continue`; start and verify the durable controller.

2. `poc/gcp/f1k_worker.sh`: add timing epochs and atomic per-item outputs; emit `construction-ready.json`; preserve the existing scientific procedure.

3. `poc/gcp/f1k_bringup_gate.py`: preserve canonical rate text; harden duplicate/epoch validation; add the small guard runtime-license delta; make checkpoints consume cumulative ledger state and live rate.

4. Add one operational helper for instance metadata, price evidence, attestation, spend leases, and ledger replay. Keep it independent of projection/sampling code.

5. Update `README.md` and `F1K-CONSTRUCTION-PLAN.md`; do not edit `build_carriers.py`, the frozen analysis, scientific pins, layer set, sampling rule, or frozen windows.

## Cross-model review gate

Require independent ACCEPTs from at least two models after all tests are green:

- **Launch/TOCTOU reviewer:** direct guard invocation, copied bundle, recreated same-name VM, wrong provisioning model, mutated builder/token/artifact, forged/stale manifest, undefined path, quote failure, and post-stage modification.
- **Budget/preemption reviewer:** preemption before/during T1, T2, handoff, probe, each checkpoint, and the final tail; controller restart; ledger rollback/corruption; rate change; quote outage; 900 h/$155/$300 boundary arithmetic.
- **Runbook reviewer:** execute the documented path from fresh Spot provisioning to the exact guard argv using fixtures, then verify the builder’s real argparse surface without launching a real construction pass.

The gate also requires the existing gate oracle, builder selftest, new runtime-license oracle, deterministic preemption-replay oracle, module/shell checks, clean diff checks, and the unchanged `a92be3e4` builder SHA. No blocker or unresolved “disagree” may be waived by documentation.

## RECOMMENDATION: SINGLE-VM-SPOT

Provision bring-up as Spot and retain the same numeric instance through GREEN → guard.  
Refactor the uncommitted fresh-VM deploy into a runnable same-VM continuation command.  
Make guard re-verify the complete live license before its engagement probe.  
Bound cumulative spend with durable ledgers, renewable leases, live repricing, and an active controller.  
Treat moving bring-up to Spot as the maintainer decision; the six review defects are engineering fixes.