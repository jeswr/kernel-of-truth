# Round-2 verification review: F1-K option-B spend-cap backstop (`f1k_ops.py`)

A prior review of this pure-local cost-accounting/timing state machine returned "must fix". The implementation has been revised. This round verifies the fixes are correct and complete and that no new defect was introduced. Read-only. Repo root: `/home/ec2-user/css/kernel/kernel-of-truth`.

## What to read
`poc/gcp/f1k_ops.py` — the block between the banner `Option-B governance layer` and `def _main()` (revised), plus `selftest_b1` (now 44/44, pure-local). Build-on helpers `resolve_live_rate`, `atomic_write_json`, `canonical_decimal`, `_utc_timestamp`, `_decimal_value` are unchanged.

## Frozen anchors (must be enforced unchanged)
900 h cap; $300 billing ceiling (fixed, not overridable); rate ∈ [$0.081, $0.595]/h; s/prefill ∈ [47.0, 162.3] s; rate×s ∈ [13.16, 27.95] $·s/h; accept-at-equal boundaries.

## The round-1 findings and the claimed fixes — verify each was actually resolved
1. **Preflight epoch/deadline split (false GO).** Fix: `preflight_launch_gate` no longer takes a caller `launch_utc`; it resolves the launch from the persisted durable epoch (`_resolve_epoch_launch`), computes elapsed AND the expected deadline from THAT, and refuses unless `deadline_utc` equals persisted-launch + 900 h. Confirm the false-GO (deadline anchored to a caller value while elapsed comes from the epoch) is now structurally impossible.
2. **Inexact product (rounding false-accept).** Fix: `_exact_product` sets a localcontext precision ≥ sum of operand digit-lengths so `rate*s` is exact; `_check_rate_window` uses it. Verify `0.2 × 139.750000000000000000000000001` now refuses.
3. **Guard not fail-closed.** Fix: `guard_rate_within_window` and `preflight` require an explicit `catalog_transport` (raise/`NO-GO` `F1K_B_RATE_TRANSPORT` when absent) instead of inheriting the live HTTP default. Confirm.
4. **$300 overridable + weak alert check.** Fix: `assure_billing_budget` dropped `expected_usd` and hard-codes `BILLING_CEILING_USD`; each `threshold_rules` entry must be a dict. Confirm the ceiling cannot be weakened and `[None]` refuses.
5. **Timer verification too weak.** Fix: `verify_selfdelete_armed` now also checks `Persistent`, the triggered `Unit`, and that the service `ExecStart` deletes THIS instance (`instances delete <name>`, `--zone`, `--project`); `render_selfdelete_unit` adds `--project`, `AccuracySec=1s`, network-online ordering, and a retry loop. Confirm a timer that is active+correct-calendar but non-persistent / wrong-unit / unbound-target now refuses.
6. **Exceptions escaping as non-`F1K_B_*` / preflight only catching `F1KOpsError`.** Fix: transport calls and decimal parses are wrapped to `F1K_B_*`; `preflight` catches ANY exception and returns NO-GO (fail-closed). Confirm a raising budget/systemctl/mirror transport yields NO-GO, not a crash.
7. **Sub-microsecond timestamp truncation.** Fix: `_utc_datetime` rejects >6 fractional digits. Confirm.

## Also check
- Did any fix introduce a NEW defect (e.g. the exact-product precision, the broadened exception catch swallowing a real GO condition, the epoch-authoritative read changing a valid case to a refusal)?
- Are the documented residuals acceptable for a single-operator/one-VM/$300 context: (a) write-once cannot survive loss of BOTH durable copies; (b) non-atomic mirror get-then-put assumes a single writer; (c) full construction-handoff/instance-identity validation stays in the launch script, not this gate; (d) the cross-module note that provisioning currently requests STOP while `validate_handoff` expects DELETE?

## Output
Free text, terse. Per-finding: RESOLVED / PARTIAL / NOT-RESOLVED with the reason. Any new defect with a concrete failing input→wrong result. Overall verdict: **sound to commit now, or what remains.** This drives the commit decision.
