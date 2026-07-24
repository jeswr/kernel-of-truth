# F1-K construction-continue build — cross-vendor review trail (SOUND after 5 rounds)

Build commit 2e629725. GPT-5.6 build-review REJECTed 4× (each a distinct REAL GCP money-leak),
SOUND on round 5. All at $0 (fakes-only oracle). Each round's verdict:
- R1 (f3b3796c): vm_exists treats any error as absent (fail-open money path).
- R2 (2bd14585): stderr-regex matches permission error as 404 (still fail-open).
- R3 (0faa12d0): blank stdout synthesized into []; delete accepts missing DONE status.
- R4 (1e39502d): gcloud allow_partial_error=true makes a failed list return (rc=0,[]).
- R5 (2e629725): SOUND — CLOUDSDK_COMPUTE_ALLOW_PARTIAL_ERROR=false forced; classifier
  confirms absence ONLY on rc=0 + nonblank JSON [] + 0 matches + partial_error_disabled;
  delete requires status==DONE; CAP-PROBE = the empirical gate (project/zone/commit/version/
  freshness-bound, partial_error_disabled mandatory PASS) before any real create.

## Round-5 SOUND verdict

Verdict: **SOUND** — no remaining real accidental fail-open. Ready for CAP-PROBE → bring-up gates → RUN.

- All production presence checks flow through `_describe_presence` → `gcloud()` with `CLOUDSDK_COMPUTE_ALLOW_PARTIAL_ERROR=false`; both capture modes receive the forced environment. The separate Compute describe path forces the same property. `partial_error_disabled=True` is asserted only on that production wrapper path; other uses are test seams. [f1k_gcp.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_gcp.py:493), [f1k_ops.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:504)
- A configuration file cannot override it: Google documents that `CLOUDSDK_SECTION_PROPERTY` environment variables take precedence over configured properties. ADC affects authentication, not this Compute property. [Google Cloud property precedence](https://docs.cloud.google.com/sdk/docs/properties)
- With partial errors disabled, only `rc=0` plus a nonblank JSON `[]` becomes absent. Exact name matches are present; malformed, alternate/wrapper, nonempty nonmatching, blank, or failed results become unknown. Thus aggregated/multi-zone or schema drift fails closed. [Google’s partial-success contract](https://docs.cloud.google.com/compute/docs/reference/rest/v1/instances/aggregatedList)
- Delete still requires structured `status == "DONE"` and no `error`; nonzero delete results require the same strict presence reconfirmation, and `_verified_delete` never accepts `present` or `unknown`. This matches GCE’s documented operation contract. [GCE operation handling](https://docs.cloud.google.com/compute/docs/api/how-tos/api-requests-responses)
- Create success is followed by strict structured describe/readback; SSH and budget paths do not classify VM absence or deletion from ambiguous output.

The CAP-PROBE is the correct empirical gate for the real GCE surface and partial-error behavior: `partial_error_disabled` is an exact mandatory PASS check, bound to the current project, zone, source commit, installed gcloud version, and freshness window, and is validated before the pre-create presence check or any create. [f1k_ops.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_ops.py:99), [f1k_gcp.py](/home/ec2-user/css/kernel/kernel-of-truth/poc/gcp/f1k_gcp.py:682)

No concrete non-adversarial `(rc, output, env)` reproducer remains.