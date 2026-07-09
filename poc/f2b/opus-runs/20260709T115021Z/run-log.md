# f2b-replicate — Opus run-log (PHASE 3: mechanical verdict + cross-vendor audit + provenance)

- UTC stamp: `20260709T115021Z` (`date -u +%Y%m%dT%H%M%SZ`)
- Executor: Opus (`claude-opus-4-8`), agent pseudonym `runner-5`
- Scope: PHASE 3 only — verdict-gen (pure function) + report-gen (pure function)
  + Codex/GPT-5.5 cross-vendor GATE-A audit + audit-status ledger + provenance
  + commit/push. NO conclusive interpretation by Opus (practice 4): the mechanical
  verdict-gen output and the deterministic different-vendor audit are allowed; the
  interpretive/kill-chain/EXTRAPOLATION->MEASURED read is FABLE-PENDING.
- Phase 1 (right-size + reset-correct-refreeze + dry-plan + mock smoke): `runner-3`,
  `poc/f2b/opus-runs/20260709T104212Z/`.
- Phase 2 (real single-A100 run, rc=0, 0.604 GPU-h): `runner-4`,
  `poc/f2b/opus-runs/20260709T110510Z/` (results
  `poc/f2b/results-incoming/20260709-114229-modal/`, 20 phase:final records
  seq 0-19 appended to `results-log/f2b-replicate.jsonl`).

## Inputs (paths + shas — all pre-existing, unchanged this phase)

- Frozen record `registry/experiments/f2b-replicate.json`
  frozen_sha256 `21d401777d2b11bca98b0528a58ebb23e774e4d7e4bee5434a746be76a66771d`
  (== `registry/frozen-index.json[f2b-replicate]`; registry-check frozen-drift OK).
- Pinned analysis `analysis/f2b_replicate.py` sha256
  `711ac322573be939a03f60aa39ef9bb05b775336c6474d634e43ed20f57e8426`
  (== `pins.analysis_script.sha256`; `--selftest` OK this session).
- Raw run log `results-log/f2b-replicate.jsonl` (Phase-2 input): 20 phase:final
  run records by runner-4; chain-verified by registry-check (`ok chain … 21 records`
  after the unblind line was appended by verdict-gen).

## Commands run this phase (all recorded in `phase3-cmds.log`)

1. `python tools/registry/verdict-gen.py --experiment f2b-replicate --agent-id runner-5`
   - First call: eligible_runs=20, excluded_runs=[], analysis re-run under the
     re-verified pinned sha; verdict **PASS-PENDING-AUDIT** (fired_rule_index 2 =
     PASS rule), audit state PENDING. Wrote `reports/auto/f2b-replicate/analysis-output.json`
     (sha `90497614631a455fa672dce58fa3e3b99da5d0c29827deb45c5e5693df635a0c`) and the
     `unblind` log line (first-time only) to `results-log/f2b-replicate.jsonl`.
   - Verdict object at that point sha256
     `4b12309850338c624803dd3da42aa6ad744e6322216f426486fa51547a060a98` — this is the
     object the cross-vendor audit was run against (`verdict_object_audited_sha256`).
2. `python tools/registry/report-gen.py --experiment f2b-replicate`
   -> `reports/auto/f2b-replicate/verdict-f2b-replicate.md` (pure-function render).
3. Codex/GPT-5.5 cross-vendor GATE-A audit (run-vs-audit separation, directives §8):
   - Smoke: `codex exec … "print KOT-AUDIT-SMOKE-OK"` -> exact token
     (session `019f46b8-8073-77e0-bd67-095fbbd0cba0`).
   - Audit: `codex exec --skip-git-repo-check -s read-only -C <repo>
     -c model_reasoning_effort=high --output-schema audit-schema.json
     -o audit-last-message.json --json <prompt>`
     (codex-cli 0.142.5, model gpt-5.5, sandbox read-only, session
     `019f46b9-d82a-7001-932a-22db9043f687`). Events -> `codex-audit-events.jsonl`.
   - Auditor independently: recomputed the frozen canonical hash (=21d40177…),
     the analysis-script sha (=711ac322…), byte-verified the JSONL hash chain,
     recomputed the 4 raw per-arm accuracies directly from `metrics.item_correct`
     arrays, re-ran the pinned analysis and reproduced analysis-output.json,
     evaluated the frozen verdict_rules top-down to rule index 2 (PASS). Result
     **CONFIRM** (all 12 checks ok, failing_step null). Record written to
     `registry/audits/f2b-replicate/1-gate-a-codex.json` (kot-audit/1, outcome CONFIRMED).
4. `python tools/registry/verdict-gen.py …` re-run (post-audit): G-6 upgrade
   **PASS-PENDING-AUDIT -> PASS**, audit state CONFIRMED
   (`path registry/audits/f2b-replicate/1-gate-a-codex.json`). Final verdict object
   `registry/verdicts/f2b-replicate.json` sha256
   `0d40f7af70956e15c89bd1d741ff17a24626b3b9fae256bd4f6a7624ad8b3eae`.
   report-gen re-run against the upgraded verdict. Single `unblind` line (not duplicated).
5. Updated `registry/audit-status.jsonl` f2b-replicate row: codex_audited=CONFIRM,
   fable_interpretive_assessed=pending (explicitly awaiting Fable), verdict_path /
   run_log_path / run_script_path filled.

## MECHANICAL numbers (pure means / pure-function gates — NOT an interpretation)

Per-arm accuracies (seed-averaged per-item means, n=250 fresh d-qa-r covered items x 3 seeds):
- acc(alone-R1, SmolLM2-135M)      = 0.4920
- acc(alone-R3, SmolLM2-1.7B)      = 0.6000
- acc(kernel-verify-retry R1, k=4) = 0.750667   [PRIMARY numerator]
- acc(shuffled-verify R1, k=4)     = 0.486667   [load-bearing control]
- acc(gloss-self-verify R1, k=4)   = 0.489333
- acc(prm-verifier)                = 0.526667
- acc(kernel-as-text R1)           = 0.4920
- extraction-instrument: n_labelled=500, n_extraction_failures=0, n_extraction_errors=0

Pre-declared gates (each a pure function; PASS/FAIL only, no narrative):
- SEPARATION GATE (instrument): gap = acc(R3)-acc(R1) = 0.1080 >= 0.10 AND one-sided
  95% BCa lower bound 0.0720 > 0  => separation_valid TRUE (PASS).
- ABSOLUTE PRIMARY (no denominator): effect = acc(verify)-acc(alone-R3) = 0.150667;
  one-sided 95% BCa lower bound primary_lower_onesided95 = 0.105333 >= 0
  => primary_reject TRUE (PASS). primary_p = 9.999e-05.
- SHUFFLED KILL (E9-defl): recovered_fraction point = -0.020619 (< 0.30, kill-(b)
  does NOT fire); one-sided 95% upper bound shuffled_recovery_ub95 = 0.107623 < 0.30
  => holm.shuffled_low_recovery TRUE (PASS).
- INSTRUMENT GATE (P10): 500 labelled / 0 failures => instrument_valid TRUE (PASS).
- Holm F-secondary(f2b), all TRUE: beats_text_null, beats_gloss_self_verify,
  prm_beaten, shuffled_low_recovery, gap_r1r3_gt_half, gap_r1r3_gt_one
  (each p = 9.999e-05). seed_sign_consistent TRUE (3/3).
- Diagnostic (reported, non-verdict-bearing): gap_closed_fraction_r1r3 = 2.395
  (lower95 1.762); cost_ratio_vs_R3 = 0.1031; tost_equivalence_pass FALSE.

MECHANICAL VERDICT: **PASS** (frozen verdict_rules, fired_rule_index 2 =
primary_reject AND beats_gloss_self_verify AND beats_text_null AND
shuffled_low_recovery). Cross-vendor audit: **CONFIRMED**.

## Outputs (declared; committed this phase)

- `registry/verdicts/f2b-replicate.json` sha256 `0d40f7af70956e15c89bd1d741ff17a24626b3b9fae256bd4f6a7624ad8b3eae`
- `reports/auto/f2b-replicate/analysis-output.json` sha256 `90497614631a455fa672dce58fa3e3b99da5d0c29827deb45c5e5693df635a0c`
- `reports/auto/f2b-replicate/verdict-f2b-replicate.md` sha256 `f39f4f1c635d29cdeb3121dfc158c10dbcea06fb679204b8553ded70bbb88529`
- `registry/audits/f2b-replicate/1-gate-a-codex.json` sha256 `84755ca01cb9ec5ca0388d2c459ed9e03195fda5fed947178edd3ea65e55ed79`
- `results-log/f2b-replicate.jsonl` sha256 `b0280605da4a73f7ff11374587b02d6c33ea0faf272f5896966a2646a05d93d3` (21 lines: 20 run + 1 unblind)
- `registry/audit-status.jsonl` (f2b-replicate row updated)
- This dir: `run-log.md`, `phase3-cmds.log`, `codex-audit-events.jsonl`,
  `codex-audit-stderr.log`, `gates.log`, `test_fixtures.out`, `registry_check.out`,
  `claims_check.out`.

## Gates (this session)

- `test_fixtures.py`: 49 tests, **OK** (rc=0).
- `claims-check.py`: **PASS** (register + 39 docs).
- `registry-check.py`: ALL f2b-specific checks GREEN — chain (21 records),
  frozen-drift f2b-replicate (21d40177), all six f2b corpus-pins, account-lint on
  the f2b experiment/verdict/audit records, append-only, claims. The single overall
  violation is `ERR_KB_CHECK` — a `tools/kb/kb-check` Python traceback in
  `K.load_shards` caused by a CONCURRENT kb-pipeline agent's UNCOMMITTED `kb/`
  shards in the working tree (the same pre-existing KB issue runner-4 noted). It is
  independent of the f2b log chain and NOT touched by this commit (targeted add, no
  `kb/` paths staged). Out of scope for f2b.

## DEFERRED (practice 4 — NOT done here; no Opus conclusion written)

- FABLE interpretive assessment: kill-chain read, EXTRAPOLATION->MEASURED promotion,
  what the verifier lift MEANS (real kernel content vs artifact), kot-assess.
  Marked `fable_interpretive_assessed: pending` in `registry/audit-status.jsonl`.
