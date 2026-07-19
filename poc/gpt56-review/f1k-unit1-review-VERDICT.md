# F1-K Unit-1 (option-A) GPT-5.6 review verdict — NEEDS-FIX (do not commit)

Model gpt-5.6-sol, effort xhigh, 2026-07-19. Cross-vendor review of the Unit-1 durable-controller implementation in poc/gcp/f1k_ops.py against the frozen F1K-LAUNCH-IMPL-PLAN.md.

## Overall verdict

**Do not commit this as the Unit-1 foundation yet.** The public parameter signatures/defaults match the frozen list, and the basic hashes are constructed correctly, but several load-bearing paths admit stale authorization or under-count exposure. `run_controller` is explicitly only a replay stub, so Unit 1 is also functionally incomplete.

No files were changed during this review.

## Part A — conformance

The callable signatures match [§1’s public list](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/F1K-LAUNCH-IMPL-PLAN.md:32), except that the new functions omit the specified return annotations other than `run_controller`. That is minor unless annotations are part of introspected ABI.

| Function | Ruling |
|---|---|
| `write_instance_metadata_attestation` | Mostly conformant: fingerprint CAS, numeric-ID check, metadata replacement, readback, and new-fingerprint verification implement the intended cycle. The injected transport ABI is extra and requires a real adapter. |
| `verify_instance_metadata_attestation` | Conformant and fail-closed for missing, malformed, or mismatched metadata. |
| `issue_spend_lease` | Nonconformant: cannot establish heartbeat freshness; does not bind rate to the licensed GREEN rate; trusts rather than validates/re-hashes rate evidence; defaults upper bound to live; excludes non-compute reservation. |
| `renew_spend_lease` | Nonconformant: permits renewal exactly at expiry and arbitrarily early; heartbeat and ledger-forward checks are insufficient. |
| `expire_spend_lease` | Essentially conformant. Chaining and the EXPIRED record are sound; repeated expiration is allowed but not a safety problem. |
| `verify_spend_lease` | Nonconformant: accepts self-declared heartbeat max age, compatible/incompatible ledger advances indiscriminately, changed authorization, over-cap heads, and partial rather than exact identity equality. |
| `append_ledger_event` | Hash construction is correct, but the head check is not an atomic CAS and only checks PD before mutation. GCS CAS is real at the transport boundary, but the transport call omits `gcs["uri"]`. |
| `replay_ledger` | Structural prefix/hash checking works locally, but live `gs://` replay is impossible; it trusts head counters/open intervals rather than replaying transitions; generation and rollback checks are incomplete. |
| `reconcile_after_preemption` | Nonconformant and can under-count; details below. |
| `mirror_state_generation_checked` | Conformant at the injected-transport boundary. Minor gap: it accepts any nonempty `gcs_uri`, not specifically `gs://`. |
| `run_controller` | Materially nonconformant: it is explicitly a replay-only skeleton, with no heartbeat, lease lifecycle, rate polling, mirroring, terminal stop, or reconciliation loop [in the implementation](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:5623). |

`selftest_a1()` is a useful extra, but the frozen public `selftest()` does not include the option-A oracle.

### Validators

- `validate_ledger_event`: the self-hash recomputation is correct—the canonical core is exactly `{schema, ledger_id, seq, prev_event_sha256, body}` excluding `event_sha256` [here](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:3968). Genesis and chain fields are correctly typed. It is not strict enough for §2: `rate` and `evidence` can be arbitrary objects; charge multiplication, outer-total arithmetic, reserve arithmetic, counter monotonicity, billing watermark progression, event-type/nullable-field mapping, and interval transitions are not checked [here](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:3950).

- `validate_spend_lease`: the body hash excluding `lease_sha256` is correct. It does not enforce generation-1/null-previous relationships, `issued <= not_before < expires`, six-hour reservation arithmetic, reservation × upper-rate consistency, caps-remaining arithmetic, or the frozen 180-second heartbeat limit [here](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:4624).

- `validate_timing_epoch`: lifecycle/nullability and `epoch_id = SHA(canonical binding)` are correct. It accepts only one corpus instead of all four, and accepts nonsense such as `dynamic=[]`, `proc_bind=null`, and `wait_policy=3.14` because only `num_threads` is typed [here](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:5503). The T1⊆T2 restriction is not stated in §2, though it matches the current sampling design.

- The common path rule is not implemented: `_contract_path` checks only lexical absolute normalization, not final-component symlinks or reviewed-root containment [implementation](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:1497), contrary to [§2](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/F1K-LAUNCH-IMPL-PLAN.md:214).

- Unit 1 requires validators for all five schemas. The landed `validate_ready` expects lean-B `timing_results`, not option-A `timing_epoch` [here](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:1723), and `validate_handoff` explicitly validates only lean-B initial handoffs [here](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:2757). Thus the all-five requirement is unmet.

## Part B — correctness defects

### 1. Hash chain and CAS

The hash chain itself is sound: contiguous sequence, previous hash, genesis zero hash, canonical event hash, and cross-mirror non-prefix detection all work.

The CAS is not sound under concurrent or incompletely fenced writers:

- Two writers can both read head `H`, both construct sequence `N`, and both append different siblings before either GCS CAS. One wins GCS; both local files are now invalid/divergent. The expected-head check at [lines 4183–4200](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:4183) is a TOCTOU check, not an atomic CAS or lock.
- Control-box state is never checked before it is appended.
- `_gcs_cas_write` does not pass the URI to the transport [here](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:4099).

PD+CB one event ahead of GCS is a recoverable exact-prefix state only after a crash/transient failure where no competing GCS write occurred. After an actual generation conflict, it may represent a competing sibling and is a corruption state. Current replay’s “longest wins” rule can promote the local suffix without consulting a live GCS object.

Rollback detection is incomplete:

- A missing `.gen` sidecar is accepted even when `expected_gcs_generation` is supplied, and the expected value is then reported as though observed [here](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:4335).
- The committed `.head.json` sidecar is written but never checked by replay.
- Identical truncation/rollback across the available local mirrors is undetectable.
- Replay does not reproduce counters or intervals; it simply returns the final body’s claimed snapshots [here](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:4372). Example: append a validly hashed checkpoint after a `$299` head but set `total_exposure="0"`; replay returns zero and lease issuance can authorize more spend.

### 2. Lease window and caps

Confirmed wrong results:

- At `now == expires_at`, verification rejects the lease, but renewal succeeds because renewal tests `now > expires`, not `>=` [here](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:5002). A lease expiring at 18:00 produced an ACTIVE successor through midnight.
- A heartbeat five hours old was accepted when the heartbeat supplied `max_age_seconds=999999`; freshness uses that untrusted value rather than the lease/protocol’s 180 seconds [here](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:4926).
- A valid descendant head with changed authorization was accepted. A `terminal-stop`, `lease-expired`, cap-crossing, or phase-changing descendant would likewise remain “VALID”; the check proves only ancestry, not compatibility [here](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:4952).
- A live identity with the same instance ID and boot but different project/project-number was accepted because only those two fields are compared [here](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:5115).
- Lease issuance has no heartbeat timestamp and therefore cannot reject a stale controller.

The equal/over boundary operator is correct: a post-reservation remainder of exactly zero may be licensed; a negative remainder must refuse. The lower values 260.6 h/$73 are not minimum-spend gates.

Nevertheless, over-cap spend remains possible because the inputs are unsound: upper rate may default to live, non-compute allowance is omitted, rate evidence is not validated, and replay permits incoherent/decreasing exposure counters.

Early renewal is not harmless. Repeated immediate renewals slide the six-hour window indefinitely if counters have not advanced. Enforce renewal only when `0 < remaining <= 3600`, and reject at exact expiry.

### 3. Reconciliation

This has several direct under-count paths [implementation](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:5210):

- Running interval starts 11:00; inconsistent new `lastStartTimestamp=10:00`; missing stop. The negative duration is clamped to zero, yielding zero cost.
- A 1.9-second interval is truncated to 1 second by `int(total_seconds())`.
- State at 899 hours plus a two-hour interval produces 901 hours while returning `new_lease_allowed=True`.
- `billing_snapshot` monetary/service data is ignored; only its watermark is copied. A snapshot advancing gross exposure from $100 to $120 leaves the $20 absent.
- Pricing uses only current live/upper values, not the maximum evidenced rate applicable during the closed interval. Historical $0.30 with current/default upper $0.20 charges $0.20.
- The new running interval is not encoded in the hash-protected event. Only its ID appears in `open_intervals`; its start timestamp exists solely in the returned, non-ledger `opened_interval`.
- On the conservative path, no new interval is opened even though the restarted VM is already accruing spend.

These are blockers.

### 4. Attestation

The self-hash cycle is correct: caller hashes exact handoff bytes, writer performs fingerprint CAS, reads back, and guard verifies exact live metadata [implementation](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:3598). Missing, mismatched, old-handoff, malformed, or changed-fingerprint states fail closed.

Exact 64-hex matching without whitespace stripping is the right security behavior. If a real adapter observes framing whitespace, normalize only in that documented transport after proving provider semantics; do not silently strip in the verifier.

## Part C — 14 seams

1. **Must-fix-or-escalate.** The superset idea is right, but the shape is not. Freeze a derived-state schema containing a replay-proven chain summary, full fresh heartbeat including `updated_at`, current authorization/identity/rate/attestation, and reconstructed running intervals. Arbitrary controller-merged fields must not become authority.

2. **Must-fix-or-escalate.** The signature is internally inconsistent. Add an optional GCS read transport, or change `gcs_uri` to a documented transport handle. Production replay must read `gs://`; local-file substitution is oracle-only.

3. **Accept-with-follow-up.** Failing closed on `compute_transport=None` is safe. Freeze the transport ABI and provide a real control-box adapter that waits for setMetadata completion and rereads the fingerprint.

4. **Must-fix-or-escalate.** Defaulting upper=live contradicts the separate-upper-bound intent. Make upper evidence mandatory and define its reviewed derivation; reconciliation separately needs the maximum historical applicable rate.

5. **Must-fix-or-escalate.** Compute-only conflicts with “including non-compute allowances” [in the frozen lease contract](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/F1K-LAUNCH-IMPL-PLAN.md:393). Include incremental non-compute uncertainty in the lease reservation, while subtracting any standing ledger reservation exactly once.

6. **Accept.** Equal is allowed; strictly over refuses. At zero remaining, no further positive lease may issue.

7. **Must-fix-or-escalate.** Replay must reconstruct interval transitions and compare every claimed `open_intervals` snapshot. Prefer separate `running-close` and `running-open` events, followed by `reconcile`, instead of forcing two transitions into one `interval`.

8. **Accept.** The event-hash core is correct. “id” means `ledger_id`; excluding `event_sha256` is correct.

9. **Must-fix-or-escalate.** The project ledger ID should originate in outer-budget/controller configuration or a single atomic bootstrap. Require it for genesis; do not silently mint independent UUIDs on empty mirrors.

10. **Accept.** A closed 14-key body with explicit nulls is a good canonical contract. The missing work is semantic validation of those fields, not sparsity.

11. **Must-fix-or-escalate.** “Renew at one hour remaining” must be a hard gate because early renewal permits indefinite window sliding. Also reject renewal at exact expiry.

12. **Accept-with-follow-up.** Separate live re-quote in the guard is consistent with the frozen signature, provided it occurs immediately before lease verification and again at the final barrier. Add an integration oracle proving that ordering.

13. **Accept-with-follow-up.** Keep exact 64-hex verification. Add one real metadata-server integration fixture before Unit 6; do not weaken the core verifier preemptively.

14. **Must-fix-or-escalate.** Option-A handoff validation is owed in Unit 1, not deferred to Unit 6. The option-A READY validator is also missing. Two incompatible records must not share `/1`; either select option A and make the canonical validators match it, or version the lean-B schemas separately.

The required pre-commit fixes are therefore: real controller behavior; live GCS replay; atomic writer fencing/commit recovery; semantic ledger replay; lease freshness/renewal/compatibility checks; conservative reconciliation; mandatory upper/non-compute reservation policy; and option-A READY/handoff validators.