# F1-K generator re-pin (kot-correction/1 seq-4) — dump-patch r3 adoption

**Status: PREPARED, NOT LANDED. Review-gate REQUIRED before the registry
splice, and before any construction dollar.**
Date: 2026-07-24. Prepared by engineer-2 (fable subagent) for the coordinator.

## 1. What broke, and why it was fail-closed by design

The $0 bring-up oracles surfaced two reds:

- `f1k_gcp.py bringup-deploy --selftest` 10/11 — `build_carriers.py present
  and sha a92be3e4...`
- `f1k_worker.sh --selftest` 13/14 — the actual-layout READY fixture (the
  fixture stages the REAL repo files; `--finalize-ready` refused them against
  `BUILDER_PIN`/`DUMP_PATCH_PIN`).

Root cause, verified: commit `0065349e` (dump-patch r3, bead 2zh8) moved THREE
pinned artifacts off their pins —

| artifact | pinned (r2-era) | on disk (r3) |
|---|---|---|
| `build_carriers.py` | `a92be3e4…` | `91baba62…` |
| `dump-patch/kot-f1k-dump.patch` | `fb5d2f35…` | `e4e04177…` |
| `dump-patch/kae_dump.h` | `6ce77601…` | `485cd497…` |

Both failing oracle checks trace to the SAME root cause. The worker's 13/14 is
not a separate regression from the construction-continue landing (`2e629725`
touched neither the READY binding nor these pins).

## 2. Intended-vs-accidental judgment: INTENDED (conclusive)

1. The `build_carriers.py` diff in `0065349e` is exactly the r3 hardening item
   named in its own commit message — "consumer-side (build_carriers run_dump:
   finiteness + gc==count(span>=0))", gate-0 re-review finding 4 — plus
   selftest probes 4c/4d/4e. Nothing else changed in the file; zero
   `add_argument`/`add_parser` deltas (argparse surface identical).
2. The commit message states "Downstream pins NOT updated (pinning separately
   gated)".
3. `dump-patch/PATCH-NOTES.md` ("Downstream pin sites — update ONLY at the
   separately-gated pinning act — deliberately NOT updated here") prescribes
   the exact updates: `PINS` → `91baba62…`/`e4e04177…`/`485cd497…`,
   `DUMP_PATCH_PIN`, every `test_kae_dump: 43/43` expectation → `64/64`, and
   the `f1k.json` harness pins, "as one ops amendment". It states the stale
   pins are FAIL-CLOSED against r3 "which is intended: updating them IS the
   pinning act and needs the maintainer-gated GO + the passed re-review".
4. The re-review PASSED: `R3-REREVIEW-CLEAN.md` (commit `3cab08c0`), GPT-5.6,
   all r2 REJECT findings closed, "delta surgical".
5. Bead `kernel-of-truth-8cpm` and ASM-2518's backing_ref both reference the
   deferred "seq-4 generator re-freeze" as known future work. (8cpm's own
   scope — per-batch STATS etc. — is a FURTHER builder change and is NOT part
   of this amendment.)

So: NOT an accidental ride-along. Reverting `build_carriers.py` to `a92be3e4`
would strip a reviewed spend-safety fix and re-adopt the r2 dump patch that
the gate-0 review REJECTED (int-parse wrap-to-negative un-gating; non-finite
dumps surfacing only after paid batches). The coherent resolution is the
freeze amendment the r3 landing itself scheduled.

## 3. What this preparation changes (working tree, uncommitted)

Infra pin sites (none sha-pinned anywhere — ASM-2514 [MEASURED]); this is the
PATCH-NOTES "one ops amendment", applied verbatim:

- `poc/gcp/f1k_gcp.py`: `PINS["build_carriers.py"]` → `91baba62…`,
  `PINS["kot-f1k-dump.patch"]` → `e4e04177…`, `PINS["kae_dump.h"]` →
  `485cd497…`; deploy-check label; docstring. **`FROZEN_SHA256` →
  `7897dd0a…` (the POST-splice hash): until the registry splice lands,
  `verify_pins()` dies `F1K_PIN_FROZEN` — the interim tree cannot license a
  launch against the un-amended record. Fail-closed by construction.**
- `poc/gcp/f1k_worker.sh`: `BUILDER_PIN` → `91baba62…`, `DUMP_PATCH_PIN` →
  `e4e04177…`, READY-fixture builder sha, and all `test_kae_dump: 43/43`
  expectations → `64/64` (finalize-ready evidence check :414, identity
  fixture :961, gate-(b) advisory-demotion greps :1422, comments).
- `poc/gcp/f1k_ops.py`: `CONSTRUCTION_BUILDER_SHA256` → `91baba62…` (guards
  the runtime license / READY-gate binding / handoff surfaces).
- `poc/gcp/f1k_bringup_gate.py`: argparse-surface comment updated with the
  carry-over justification (zero argparse deltas in `0065349e`).
- `poc/gcp/bringup_gcp.sh`: frozen-record comment updated to name both
  hashes.

Registry files are NOT touched by this preparation (see §4).

## 4. The frozen-record splice — COORDINATOR-ONLY, POST-REVIEW

`registry/experiments/f1k.json` embeds the generator pin at two sites
(`pins.harness_manifest` + the FREEZE-(A) COMPLETION clause of
`design.n_planned.freeze_manifest.A_pre_spend`). Amending it is a freeze
change on the paid path and is deliberately left to the coordinator AFTER the
review gate; the permission boundary on this box enforced the same split.

To land, in ONE commit, after the GPT-5.6 review of this document passes.
**Order matters (Rev2 blocker 2 — the frozen-index is the launch marker and is
written LAST, so a launchable state always implies the correction + ASM are in
place):**

1. **Register ASM-2525** (below) in `registry/assumptions.jsonl` FIRST — the
   splice REFUSES to advance the index until it is present, so this precedes
   the splice.
2. `python3 poc/gcp/f1k_generator_repin_splice.py --apply` — asserted,
   deterministic, TRANSACTIONAL: verifies the pre-state (canonical, frozen
   hash `35372275…`, exactly 2 pin sites), runs the FULL identity/account lint
   on the draft correction, requires ASM-2525 already registered, then writes
   **record → correction → index (last)**, requiring the post-state hash to
   equal `7897dd0a8fbb432768d70e959a77abdd80c16c78ab93702ff6f1671828bf7802`.
   Any mid-write failure rolls record + index back to pre-splice bytes and
   removes the correction (never a launchable half-state). Post-write it
   re-runs `registry-check --frozen-drift` checking the RETURN CODE and the
   FULL hash.
3. Re-run the four $0 oracles + `construction-continue --selftest` (all green
   pre-landing; §6) + full `registry-check` (must be clean — see the note
   below).

**Money-path gate (Rev2 blocker 1):** `f1k_gcp.py construction-continue` now
calls `_construction_launch_gate()` BEFORE any mutation/launch —
`verify_pins()` (file pins + the fixed `--frozen-drift` return-code + full-hash
bind) plus `_frozen_governance(REPO, FROZEN_SHA256)` (the FULL `registry-check`
exit 0, frozen-index full-hash, the seq-4 correction bound to `7897dd0a…`, and
ASM-2525 registered). READY/GREEN bind only the builder SHA; this gate is what
binds the paid launcher to the landed governance. **Consequence:** the paid run
now refuses to spend against ANY registry/KB integrity violation anywhere in
the repo, not just F1-K — so the landing tree must pass a clean full
`registry-check` (regenerate/commit unrelated KB records first).

Prescribed-but-deferred (historical doc tables quoting r2 values —
`F1K-LAYER-REFREEZE.md`, `F1K-PIN-FILE-FIX.md`,
`docs/next/design/f1k-inertness-gate-resolution.md`): add supersession notes
at the coordinator's discretion; do NOT rewrite their [MEASURED] rows.

## 5. ASM for the coordinator to register (exact line, id ASM-2525 — next
free; verify uniqueness at landing per the duplicate-id defect)

```json
{"id": "ASM-2525", "tag": "STIPULATED", "load_bearing": true, "claim": "F1-K GENERATOR RE-PIN (kot-correction/1 seq-4; the pinning act deliberately deferred by the dump-patch r3 landing 0065349e/bead 2zh8): the frozen carrier-construction generator pin moves a92be3e4fe535c1dfefc41e2a422e010d25e8e40cf8e4cc123e7d829d63e9e61 -> 91baba62649ad81217a4dd51cfcb57536c81b50e7f38ce8e622a161c1056835b at BOTH f1k.json embed sites (pins.harness_manifest + freeze-manifest A_pre_spend), re-freezing 35372275… -> 7897dd0a… via the asserted deterministic splice poc/gcp/f1k_generator_repin_splice.py, and the r2-era harness pins move WITH it as one ops amendment (f1k_gcp.py PINS: dump patch -> e4e04177…, kae_dump.h -> 485cd497…; f1k_worker.sh BUILDER_PIN/DUMP_PATCH_PIN/READY fixture; f1k_ops.py CONSTRUCTION_BUILDER_SHA256; test_kae_dump expectations 43/43 -> 64/64). The a92be3e4->91baba62 delta is EXACTLY commit 0065349e [MEASURED: sole commit between the shas; zero add_argument/add_parser deltas]: consumer-side KAED re-verification in run_dump (finiteness + gated_count == manifest span>=0, gate-0 finding 4) + selftest probes 4c/4d/4e — refuse-only, construction semantics untouched; GPT-5.6 re-review CLEAN (R3-REREVIEW-CLEAN.md, 3cab08c0). Landing REQUIRES the passed cross-vendor review of poc/gcp/F1K-GENERATOR-REPIN.md (freeze change on the paid path — never self-approved); the paid run stays separately gated on #55-Q1/Q2 spend-GO + the four real-engine bring-up gates, which f1k_worker.sh enforces as READY prerequisites on the VM (status files + dump-realchecks evidence). Until the splice lands, f1k_gcp.py FROZEN_SHA256 already carries 7897dd0a…, so verify_pins dies F1K_PIN_FROZEN — the interim tree is fail-closed against launching the un-amended record. EVERY spend-capable f1k_gcp.py entry point — provision (creates the paid SPOT VM), bringup-deploy (launches the detached paid worker), and construction-continue — invokes the FULL governance gate _construction_launch_gate() = verify_pins (file pins + fixed --frozen-drift returncode + FULL frozen-index hash bind) + _frozen_governance (full registry-check exit 0, frozen-index full hash == 7897dd0a…, the seq-4 correction bound to 7897dd0a…, and an id==ASM-2525 assumptions.jsonl entry parsed as JSON — NOT a substring) BEFORE any mutation/GCP op; the deterministic splice writes record -> correction -> frozen-index (the launch marker) LAST with ASM-2525 required as a precondition and independent rollback on any mid-write failure, so no half-applied state is launchable. All four $0 oracles green on the amended tree [MEASURED: gate 74/74, bringup-deploy 11/11, f1k_ops 23/23, f1k_worker 14/14; construction-continue 83/83 incl. the wiring + id-parse + rollback proofs]. Kill criterion, endpoints, caps, floors, envelope, geometry, seeds UNCHANGED verbatim.", "rationale": "The r3 review chain proved the r2 dump instrumentation unsafe on the paid path (int-parse wrap-to-negative un-gating; non-finite dumps surfacing only after paid batches) and the r3 remediation surgical; the r3 landing left every downstream pin at r2 values so the estate fail-closes until a maintainer-gated, review-passed pinning act — this correction IS that act, executed with a hash-asserted splice so the freeze change is exactly the two generator-pin strings and nothing else.", "backing_ref": "registry/corrections/f1k/4-generator-repin.json (this landing); poc/gcp/F1K-GENERATOR-REPIN.md; poc/gcp/f1k_generator_repin_splice.py; poc/glm52-probe/f1k-harness/dump-patch/PATCH-NOTES.md 'Downstream pin sites'; R3-REREVIEW-CLEAN.md (3cab08c0); commits 0065349e/7d7f91ca; ASM-2488 (gated-count identity re-checked consumer-side), ASM-2504 (seq-2 precedent), ASM-2513 (seq-3 precedent), ASM-2514 (infra files not sha-pinned [MEASURED]), ASM-2518 (argparse-surface measurement basis)", "status": "open", "owner": "coordinator-1", "date": "2026-07-24"}
```

## 6. Verification on the amended tree ($0, this box)

- `python3 poc/gcp/f1k_gcp.py gate --selftest` — 74/74
- `python3 poc/gcp/f1k_gcp.py bringup-deploy --selftest` — 11/11
- `python3 poc/gcp/f1k_ops.py selftest` — 23/23
- `bash poc/gcp/f1k_worker.sh --selftest` — 14/14
- `python3 poc/gcp/f1k_gcp.py construction-continue --selftest` — 89/89
  (71 → 78 → 83 → 89; the +6 Rev4 checks: malformed-line-BEFORE,
  malformed-line-AFTER, and duplicate-`ASM-2525` all refuse; the 3 wiring
  proofs are now BOTH-legs — gate-present→gate AND gate-absent→cloud-sentinel
  for each of provision / bringup-deploy / construction-continue)
- splice rollback + retry-safety: a sandbox run with an injected
  correction-copy failure restores record+index to pre-splice, removes the
  PARTIAL correction, leaves the tree non-launchable, and a clean re-run then
  applies successfully (frozen-drift green) — verified with a realistic ledger
  carrying duplicate OTHER ids + exactly one ASM-2525
- `py_compile` f1k_gcp.py/f1k_ops.py/f1k_bringup_gate.py/
  f1k_generator_repin_splice.py + `bash -n` f1k_worker.sh/bringup_gcp.sh —
  clean
- `python3 tools/registry/registry-check.py --frozen-drift` — rc 0, f1k at
  `35372275…` (registry untouched, pre-splice, as it must be)
- Full `registry-check` presently rc 1 due to UNRELATED concurrent-agent KB
  edits (`kb/records/internal/…s3-grounding-checker…`), not F1-K; the F1-K
  registry surface is clean. Must be resolved to green before the real launch
  (the money-path gate refuses otherwise — by design).

## 7. Rev2 (this round) — four money-path fail-opens closed

The cross-vendor review returned REJECT-with-four-blockers on the Rev1
preparation (it confirmed the substance: intended-vs-accidental, the three
executable repins, the `7897dd0a` recompute, no scientific drift, ASM-2525
correctness, interim fail-closed). Closed:

1. **Launcher bypassed the frozen gate** — `cmd_construction_continue()` now
   calls `_construction_launch_gate()` (verify_pins + `_frozen_governance`)
   before any argparse side-effect / env / read / launch.
2. **Splice admitted a half-applied launchable state** — the splice is now
   transactional with the frozen-index written LAST as the sole completion
   marker, ASM-2525 required as a precondition, and rollback of record+index
   (and correction removal) on any mid-write failure; the launch gate
   independently re-checks the correction + ASM so a hand-forced index is not
   enough.
3. **`verify_pins()` ignored registry-check failure** — fixed to the flag form
   `--frozen-drift`, to CHECK the return code (fail-closed on nonzero), and to
   bind the FULL `7897dd0a…` hash from the frozen-index (the checker prints
   only an 8-hex prefix). Same fix applied at the splice's post-write check.
4. **Draft correction failed identity lint** — `author` is now the permitted
   pseudonym `coordinator-1` (installer, per seq-2/seq-3 precedent), with the
   fable-subagent provenance moved to a non-identity `preparation` field; the
   splice now enforces the FULL `check_identity_fields` +
   `require_no_account_strings` on the draft before copying it.

## 8. Rev3 (this round) — three residual money-path fail-opens closed

Rev2 re-review returned REJECT-but-confirmed-closures (ordering fail-closed;
verify_pins return-code + full-hash; `_frozen_governance` full-checker rc0-only;
draft `author: coordinator-1` passes lint; the 7 assertions isolate the
branches). Three residuals closed:

1. **`provision` and `bringup-deploy` bypassed the governance gate** — both are
   spend-capable (provision creates the paid SPOT VM; bringup-deploy launches
   the detached paid worker) yet called only `verify_pins()`. Both now call
   the full `_construction_launch_gate()` as their FIRST action, before any
   mutation / GCP op. All THREE spend-capable entry points are now gated.
2. **ASM-2525 "registration" was a substring search** — the launcher and the
   splice precondition accepted any occurrence of the string `ASM-2525`. Both
   now use `_asm_registered()`, which parses the JSONL and requires an entry
   whose `id == "ASM-2525"`. Proven: a foreign record with
   `"notes":"…ASM-2525…"` (different `id`) is REFUSED; a real `id==ASM-2525`
   entry among decoys is accepted.
3. **Rollback was incomplete** — `correction_created` was set only after the
   copy, so a create-then-fail leaked a partial file; the rollback writes were
   unguarded and swallowed unlink errors. Now: cleanup is existence-based (a
   partial correction is removed regardless of how far the copy got), each
   rollback step is independently attempted, and any rollback-step failure is
   surfaced with a STOP-and-inspect message (never a silent half-state). Proven
   in a sandbox: injected copy-failure → record+index restored, partial
   correction removed, non-launchable, and a clean re-run then applies (exit 0,
   frozen-drift green).

**End-to-end wiring proof (the review's "Also"):** `construction-continue
--selftest` now drives `provision` / `bringup-deploy` / `construction-continue`
with `verify_pins` stubbed to pass, `_frozen_governance` raising a GATE
sentinel, and every GCP-capable fn raising a GCP sentinel — each command hits
the GATE sentinel first (outcome=gate), so a regression back to a bare
`verify_pins()` would sail into a GCP sentinel and fail the check. This proves
the wiring, not just that `_frozen_governance` refuses when called directly.

## 9. Rev4 (this round) — two hardening corrections (final)

Rev3 re-review = SOUND-WITH-CORRECTIONS. Two concrete hardening items closed;
no further full review — coordinator verifies these mechanically then lands.

1. **`_asm_registered()` fully fail-closed** (both `f1k_gcp.py` and the splice).
   It no longer `continue`s past malformed JSON or returns on the first match.
   Now it scans the ENTIRE ledger, FAILS on any malformed / non-object line
   anywhere, and requires EXACTLY ONE object with `id == "ASM-2525"` (a
   duplicate target id is ambiguity → refuse). Project semantics preserved:
   the real ledger legitimately carries duplicate ids for OTHER assumptions
   (last-line-wins; e.g. ASM-0010, ASM-2389) — those do NOT block, because the
   exactly-one rule applies to the TARGET id only. Negative tests added:
   malformed-before, malformed-after, duplicate-target-id, non-object line —
   all REFUSE; a real single entry among decoys / other-id duplicates is
   accepted. This matters most for the SPLICE precondition, which (unlike the
   launcher) has no preceding full registry-check.
2. **Wiring oracle proves complete sentinel coverage.** The three commands now
   run BOTH legs. `construction-continue` gets valid fake `--gate/--ready`
   args + env + readable artifacts so it REACHES its launch boundary (it no
   longer exits early on missing args — the exact Rev3 gap). Every direct
   provider surface is sentineled: `gcloud`, `vm_exists`,
   `_require_cap_probe_green`, `_provision_execute`, `_gsutil_mirror`,
   `_blocking_delete`, `_describe_presence`, the paid orchestrator
   `_construction_continue`, and `f1k_ops._gcloud_compute_get` /
   `f1k_ops._catalog_http_list`; non-cloud local guards are no-op'd so they
   can't mask the boundary. Present leg: gate raises GATE → outcome=gate.
   Absent leg (gate stubbed away): each command reaches a cloud sentinel →
   outcome=gcp. A dropped gate flips the present leg; a sentinel gap flips the
   absent leg — either fails.

(Counts above recorded immediately after these edits; re-run at landing.)
