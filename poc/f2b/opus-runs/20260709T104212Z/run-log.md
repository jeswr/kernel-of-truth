# f2b-replicate — Opus run-log (right-size + reset-correct-refreeze)

- UTC stamp: `20260709T104212Z` (`date -u +%Y%m%dT%H%M%SZ`)
- Executor: Opus (`claude-opus-4-8`), agent pseudonym `runner-3`
- Task: apply the architecture-advisor RIGHT-SIZED design to f2b-replicate,
  reset-correct-refreeze, dry-plan + mock-smoke. NO full run performed. NO
  interpretation written (Opus-execution practice 4).
- This log is a BACKUP for a Fable agent to audit later (practice 1).

## Root-cause finding (mechanical; not an interpretation)

Inspected `poc/f2b/runner/f2b_runner.py` `run_cells`. Every retry/verify arm
(kernel-verify-retry, shuffled-kernel-verify-retry, gloss-self-verify-retry,
and the now-dropped gold-oracle-retry) ran ONLY at R1 (SmolLM2-135M); R3
(SmolLM2-1.7B) was invoked ONLY for the single-pass model-alone baseline
(k=0). There was NO 1.7B retry ladder — so R3-retries did NOT cause the
~3.5 h marathons. The heaviness was design magnitude: 1000 items x 5 seeds x
retry_sweep {1,2,4} (worst-case 2+3+5=10 attempt-passes per retry arm) x the
full arm set incl. gold-oracle x the 500-item external slice through every
arm's own pipeline. The runner's own --dry-plan estimated ~3.26 h point /
~6.52 h worst on A10G for that design. R1-only retries were left unchanged.

## Inputs (paths + shas)

- Frozen record: `registry/experiments/f2b-replicate.json`
  frozen_sha256 `21d401777d2b11bca98b0528a58ebb23e774e4d7e4bee5434a746be76a66771d`
  (== `registry/frozen-index.json[f2b-replicate]`), file sha256
  `9015b9e8909d67f19f08bd7390f402dbd75ef8c7f95301943785bd8c3e0d2cb3`.
- pins.harness_manifest `cffd61049bd6f6a08adf1dbe6ee3a2aa7dd3d032c630de10060edfbca5431d9c`.
- pins.analysis_script `analysis/f2b_replicate.py` sha256
  `711ac322573be939a03f60aa39ef9bb05b775336c6474d634e43ed20f57e8426` (UNCHANGED).
- Superseded freeze `a5c8b84bd326c60860ba291ebdd7ba7df9c8c328a29adc2cd10a515fa424005e`
  (removed from frozen-index at reset).
- Models (record.pins.model_revisions): SmolLM2-135M @12fd25f77366,
  SmolLM2-1.7B @31b70e2e869a, Skywork PRM 1.5B @98d69606595e.
- Corpora (record.pins.corpus_hashes, kot-corpus-hash/1; UNCHANGED — subset is
  a runtime rank-prefix, no corpus re-pin): d-qa `ad756a7e...`, d-qa-r
  `0d548bf1...`, d-xif `8c9aded6...`, d-ext `0c5306bb...`, kernel-v0
  `8209cada...`, molecules-v0 `69f0c8a3...`.

## Changed-file shas (after edits)

```
b62c3a72882b354f25b97a4b38251fb4863b1c3417220d1c942c84b24fc9b666  poc/f2b/runner/f2b_runner.py
da1fe9dddd9cbddc13143a7f7931ae3f0ced2548df8e36042244ee043fcb61f9  poc/f2b/inputs/f2b-manifest.json
c2fc2b3a50458e7353c7b687e0a5ea9820c2be0517c93831e76422de1555575d  poc/modal/modal_f2b.py
14bbc66840e1f2d7d57aeda22e52c69b5a1d99820562980d46b16f22541219a4  poc/f2b/smoke/check_mock.py
3209b4b0f94d6fbb07ccd63048ce4603e7def0605b50749bef6bd718c799e0d1  poc/f2/run-f2b-replicate.sh
711ac322573be939a03f60aa39ef9bb05b775336c6474d634e43ed20f57e8426  analysis/f2b_replicate.py (UNCHANGED)
```

## Commands run (in order) + key stdout

1. `python3 poc/f2b/runner/f2b_runner.py --dry-plan --gpu-class A100 --out-dir /tmp/f2b-dry`
   -> 19 cells, 3 seeds, 250 items; A100 0.38 h point / 0.76 h worst; $0.80 /
   $1.60; all caps OK. rc=0.
2. Recompute harness_manifest via `poc/modal/.venv/bin/python` importing
   `modal_f2b._manifest`/`_manifest_sha` (offline, no launch) -> 158 files,
   `cffd6104...`.
3. Reset record to DRAFT (status, drop frozen_*, set pins.harness_manifest),
   remove f2b-replicate from `registry/frozen-index.json`.
4. `python3 tools/registry/prereg-freeze.py --experiment f2b-replicate --agent-id runner-3`
   -> FROZEN, frozen_sha256 `21d40177...`.
5. `python3 tools/registry/registry-check.py` -> PASS.
6. `python3 tools/registry/test_fixtures.py` -> Ran 49 tests OK.
7. `python3 analysis/f2b_replicate.py --selftest` -> selftest OK.
8. `python3 poc/f2b/smoke/check_mock.py` -> ALL CHECKS PASSED ($0, CPU):
   7 arm levels x 14 records, all 50 output_fields resolve, separation+P10
   gates PASS, best_k=4, gold field null, both safety bounds self-terminate.
9. `poc/f2/run-f2b-replicate.sh --dry-plan` (end-to-end launcher) -> gate 1 OK
   (FROZEN, sha match), registry-check PASS, A100 dry-plan as in (1).

(An intermediate freeze `ee2a0c0a...` with harness pin `088dd995...` was
produced, then a mock-smoke KeyError revealed the shuffled-verifier
permutation must span the FULL covered-concept set, not the 250 subset; that
one-line revert changed the runner bytes, so the record was reset-refrozen a
second time to the FINAL sha `21d40177...` / harness `cffd6104...`. Both
intermediate freezes were pre-run and are superseded; no run record exists.)

## Reproducible launch command (the ONE script)

```
# $0 cost plan (safe default):
poc/f2/run-f2b-replicate.sh --dry-plan
# real single-A100 run (requires maintainer Tier-1 go):
KOT_TIER1_GO=1 poc/f2/run-f2b-replicate.sh --run
```

## Outputs (declared)

- On a real run: `poc/f2b/results-incoming/<UTC-stamp>-modal/run-records-f2b.jsonl`
  + `provenance.json` (NOT auto-committed).
- Verdict (separate run-vs-audit-separated step):
  `analysis/f2b_replicate.py` | `tools/registry/verdict-gen.py` ->
  `registry/verdicts/f2b-replicate.json`; append-only
  `results-log/f2b-replicate.jsonl`.
- This run produced NO run records and NO verdict (dry-plan + mock only).

## Ledger

`registry/audit-status.jsonl` row for f2b-replicate: executed_by=opus,
executor_model=claude-opus-4-8, codex_audited=pending,
fable_interpretive_assessed=pending. The INTERPRETIVE assessment (kill-chain
read, EXTRAPOLATION->MEASURED promotion) is PENDING for Fable (practice 4).
