# truthstyle-2x2 — p3 re-run plan (post ERR_DTS_BLINDING at pos-102)

> Issued 2026-07-10 by FABLE (experiment-designer role; register owner
> designer-1), under blinding-audit-clarification.md AMENDMENT A1 (§9) and
> `registry/corrections/truthstyle-2x2/4-blinding-audit-amendment-a1.json`.
> The re-run shape ruling is [STIPULATED: ASM-0661]; the amended §7.3
> matching rule it depends on is [STIPULATED: ASM-0660]. This note is
> OPERATIONAL — it decides nothing beyond those two stipulations.

## Shape (one line)

Fresh, full judge-p3 pass ONLY — new run dir, §8 preflight then all 808
items in the frozen p3 seed order (`dts/1|judge-p3|20260710`, derived
mechanically by the unchanged `seeded_order`) — under the A1 runner.
judge-p1 and judge-p2 of `opus-runs/20260710T151231Z` STAND (complete
808/808, blinding-clean). No resume from pos-103. No redesign: pins, seeds,
judge order, prompts, and the §4.3 capture form are all byte-unchanged.

## pos-102 decision

The void p3 partial (pos-001–102, run 20260710T151231Z) is retained
BYTE-VERBATIM as provenance; pos-102 is NOT scrubbed and NOT re-captured in
place. Under A1 its 'nsm' occurrence inside
`"request_id":"req_011Cctc1sK9P4SujinnsMiWU"` is a listed `vendor_id`
exclusion, and the sweep is GREEN over the retained bytes as they are
[MEASURED: A1 self-test sweep-equivalent walk over 20260710T151231Z,
2026-07-10 — clarified hits = [], exclusions = 5 `f2b` hex-run + 1 `nsm`
vendor-id]. Scrubbing would break the clarification's retained-bytes
re-derivability guarantee (§5) for zero audit benefit. Disclosure carried in
§9.7: the coordinator read the void pos-102 capture (raw answer `no`) while
localizing the abort; that sample is void, enters no statistic, and the item
is re-judged fresh in the new pass.

## Runner checklist (coordinator/runner-owned; in order)

1. Verify the A1 executor bytes before launch — sha256 must equal the §9.5
   pins: `run-dts-judges.py`
   `1d6d7a396948414f886e0f4caea6557f54d90e31b74511cf656d6a9eba34a74f`,
   `blinding-sweep.py`
   `b53b6d7a2f2e2cfe684c18eda896c73cce3390896aa4584287e96ad7960bdcea`.
   Record both in the NEW run dir (e.g. `runner-sha256.txt`) before any call.
2. NEW run dir `opus-runs/<UTC-stamp>/`. Do NOT write into
   20260710T151231Z (its p3 subtree is retained void provenance; re-running
   p3 there would overwrite pos-001–102 captures).
3. `run-dts-judges.py p3 preflight <new_run_dir>` — fresh §8 preflight
   (both calibration probes must PASS first-attempt).
4. `run-dts-judges.py p3 main <new_run_dir>` — all 808 items; the pass
   writes `data/d-ts-labels/judge-p3-haiku45-responses.jsonl` at END.
5. Copy byte-identical `run-summary-p1.json`, `run-summary-p2.json`,
   `preflight-status-p1.json`, `preflight-status-p2.json` from
   20260710T151231Z into the new run dir (record their sha256s alongside);
   then `run-dts-judges.py finalize <new_run_dir>`.
6. `blinding-sweep.py` over BOTH `opus-runs/20260710T151231Z` and the new
   run dir. GREEN required on BOTH before the d-ts-labels ops amendment is
   written; commit both `blinding-sweep.json` outputs. Expected exclusions
   in 20260710T151231Z: the 5 `f2b` hex-run entries plus the pos-102 `nsm`
   `vendor_id` entry; anything else, or any clarified hit anywhere, is a
   boundary stop back to Fable — do not proceed.
7. Any NEW abort of any kind is its own boundary stop (ASM-0661 is one-shot,
   like ASM-0361 before it: it is not a standing resume-or-restart policy).

## Budget note

~102 discarded p3 calls at the measured 0.0002–0.003 USD/call ≈ 0.02–0.3
USD; well inside the frozen usd_cap 40. The p1/p2 passes are NOT re-run, so
the A1 restart costs two orders of magnitude less than a full campaign void.
