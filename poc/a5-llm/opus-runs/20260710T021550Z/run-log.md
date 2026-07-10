# a5-llm — Opus run-log: cross-vendor Codex GATE-A RE-AUDIT (pin-erratum in scope)

- UTC stamp: `20260710T021550Z` (`date -u +%Y%m%dT%H%M%SZ`)
- Executor: Opus (`claude-opus-4-8`), agent pseudonym `runner-6` (same runner id as
  the a5-llm run/original-audit trigger); role experiment-runner
  (`.claude/agents/experiment-runner.md`). MECHANICAL execution + cross-vendor audit
  trigger ONLY — no interpretation, no conclusion (practice 4).
- Purpose: re-run the a5-llm GATE-A cross-vendor Codex audit WITH the post-hoc pin
  erratum `registry/corrections/a5-llm/1-posthoc-pin-erratum.json` in the auditor's
  scope, and have the auditor INDEPENDENTLY VERIFY (not rubber-stamp) the erratum's
  three core claims before re-issuing GATE-A. Motivation: the original GATE-A audit
  (`poc/a5-llm/opus-runs/20260709T223054Z/audit-last-message.json`) was REJECT on
  `failing_step=pins` ONLY (11/12 checks ok, all endpoints reproduced).
- Custody: NO commit; did NOT touch Fable's erratum/assessment files,
  `registry/audit-status.jsonl`, or any `docs/design-*.md` (concurrent workflow owns
  those). This run-log + the `reaudit/` capture are the only new artifacts.

## Auditor (cross-vendor, run != audit)

- `codex --version` -> `codex-cli 0.142.5` (the GLOBAL codex; NOT upgraded).
- Vendor/model: OpenAI GPT-5.5 via `codex exec` (session
  `019f49d1-...` smoke; audit session in `reaudit-events.jsonl` seq 0
  `thread.started`). Auditor id in the brief: `auditor-4` (independent of `runner-6`).
- Sandbox read-only; reasoning effort high; schema-constrained final message.

## Commands run (this run-log is a BACKUP for later Fable audit)

1. Verify codex version (must stay 0.142.5, no upgrade):
   `codex --version` -> `codex-cli 0.142.5`.
2. Runner pin pre-checks (verify erratum's factual anchors reproduce, before writing
   the brief — mechanical, not interpretation):
   - `sha256(tools/axiom/kot_axiom.py)` = `b622694022000367349b158aea5322e63677379521c47b29a9d62f2e86e46ccf` (executed engine, design-named path)
   - `sha256(data/code-corpus-v0/src/kot_axiom.py)` = `d2064989c208c37df5a3d15a4fae6118c82516055fd6552f45a2a92fe2b7a659` (corpus mirror)
   - frozen `pins.artifact_hashes['kot_axiom.py']` = `d2064989...` (== corpus mirror)
   - `results-log/a5.jsonl` seq0 `config.engine_sha256` = `d2064989...` (a5-parent engine)
   - `results-log/a5-llm.jsonl` seq 0..8 all `pins_observed.engine.observed` = `b6226940...` (+ `config.engine_sha256` on R0 cells)
   - `reports/auto/a5-llm/analysis-output.json` `/analysis/engine_matches_a5` = 1, `/gates/instrument_valid` = true, `/analysis/bootstrap_B` = 10000
   - git `tools/axiom/kot_axiom.py`: `fa210a6` 2026-07-09T19:56:54Z + `9910052` 2026-07-09T22:25:52Z (define-op) precede freeze `2026-07-09T22:33:25Z`
3. Wrote the re-audit brief + schema (Opus operational artifacts; reuse the original
   brief's 12 checks + add the erratum-verification layer):
   - `reaudit/reaudit-brief.md`   sha256 `3f827575822b8171006b854c2c1cdebad1596159981ec61d7906b7a78033eab3`
   - `reaudit/reaudit-schema.json` sha256 `d79481e38cf122655dd90bbbdb2ac852fdf5cc702a74783c51447ceb85fd81a5`
4. Codex smoke (foreground): exact token `KOT-AUDIT-SMOKE-OK` (session
   `019f49d1-6adb-7040-97f1-4514ffd1720c`, model gpt-5.5, sandbox read-only).
   Logs: `reaudit/reaudit-smoke.log`, `reaudit/reaudit-smoke.stderr`.
5. Codex RE-AUDIT (FOREGROUND/blocking — detached codex jobs have died as orphans on
   this box). START `20260710T021829Z` / END `20260710T022241Z` (~4 min); exit 0.

### Exact reproducible launch command

```
REPO=/home/ec2-user/css/kernel/kernel-of-truth
RD="$REPO/poc/a5-llm/opus-runs/20260710T021550Z/reaudit"
codex exec --skip-git-repo-check -s read-only -C "$REPO" \
  -c model_reasoning_effort=high \
  --output-schema "$RD/reaudit-schema.json" \
  -o "$RD/reaudit-last-message.json" \
  --json - < "$RD/reaudit-brief.md" \
  > "$RD/reaudit-events.jsonl" 2> "$RD/reaudit-stderr.log"
```

(Same invocation shape as the original a5-llm GATE-A audit: `codex exec
--skip-git-repo-check -s read-only -C <repo> -c model_reasoning_effort=high
--output-schema <schema> -o <last-message> --json` with the prompt on stdin.)

## Inputs (paths + shas)

- Original audit brief:  `poc/a5-llm/opus-runs/20260709T223054Z/audit-brief.md`  `817e96ec...`
- Original audit schema: `poc/a5-llm/opus-runs/20260709T223054Z/audit-schema.json` `0f92cfe0...`
- Original audit result: `poc/a5-llm/opus-runs/20260709T223054Z/audit-last-message.json` `2d8a0095...` (REJECT, failing_step=pins)
- Erratum (in scope):    `registry/corrections/a5-llm/1-posthoc-pin-erratum.json`  `e62563d9...`
- Frozen record:         `registry/experiments/a5-llm.json`  `43a5a0fd...` (status FROZEN; frozen_sha256 `11c3dc4e...`)
- Verdict object:        `registry/verdicts/a5-llm.json`  `f893cf47...` (PASS-PENDING-AUDIT)
- Analysis output:       `reports/auto/a5-llm/analysis-output.json`  `f80a491e...`
- Pinned analysis:       `analysis/a5_llm.py`  `8f7aa880...`
- Results logs:          `results-log/a5-llm.jsonl` (seq 0..9), `results-log/a5.jsonl` (parent)

## Outputs (paths + shas)

- `reaudit/reaudit-brief.md`          `3f827575822b8171006b854c2c1cdebad1596159981ec61d7906b7a78033eab3`
- `reaudit/reaudit-schema.json`       `d79481e38cf122655dd90bbbdb2ac852fdf5cc702a74783c51447ceb85fd81a5`
- `reaudit/reaudit-last-message.json` `f099fa73b66c55012d5c95a480d76b9705301ed778e59ff3f3f6a4a90050104a` (schema-VALID; result=CONFIRM)
- `reaudit/reaudit-events.jsonl`      (52 lines; full codex event stream)
- `reaudit/reaudit-smoke.log` / `reaudit/reaudit-smoke.stderr` / `reaudit/reaudit-stderr.log`

## RE-AUDIT OUTCOME (mechanical — the auditor's own JSON, not an Opus conclusion)

- **result = CONFIRM**, failing_step = null. Schema-VALID against `reaudit-schema.json`.
- pins_given_erratum = **ok**; checks (erratum-conditioned pins): all 12 = ok
  (frozen_hash, log_chain, pins, analysis_script_sha, endpoint_recompute, verdict_rule,
  primary, cost_gate, instrument_gate, separation_gate, independence, scope).
- Three erratum claims INDEPENDENTLY VERIFIED by the auditor (recomputed, not trusted):
  - claim1 engine_matches_a5 = **verified** — `/analysis/engine_matches_a5`=1 reproduced
    from the chained log; executed engine b6226940 (all seq 0..8) reproduced the a5-parent
    (d2064989) per-query outcomes on the 977-query slice -> a d2064989 re-run is
    informationless for these endpoints.
  - claim2 stale-identity bookkeeping = **verified** — pin d2064989 == corpus mirror ==
    a5-parent engine; executed engine at the design-named path = b6226940; sibling pins
    (kot_code.py, a5_llm_instrument.py) follow live tool paths, so kot_axiom.py is the
    single convention deviation; git define-op commits precede the freeze; the delta is a
    define-op ADDITION unexercised by the a5-eval strata.
  - claim3 post-hoc erratum lawful = **verified** — record FROZEN with final-phase runs
    (seq 0..8) + unblind (seq 9) -> P-9 cutoff crossed -> reset-refreeze unlawful; erratum
    is a separate registry/corrections record that does not mutate the frozen record/log/
    verdict/index (append-never-edit).
- Endpoints reproduced IDENTICALLY to the original audit: engine_conj 1.0, best-LLM
  llm-rag-R3 0.3398157625383828, effect_size 0.6601842374616171, primary one-sided95
  lower 0.6345957011258956, cost_ratio_min 22835.94771419218, separation_gap
  -0.127942681678608, fabrication_rate 0.7868852459016393, engine_matches_a5 1,
  fired_rule_index 2, verdict PASS-PENDING-AUDIT, matches_verdict_object true,
  reproduces_analysis_output true.
- Independence: every eligible run record runner = runner-6, != auditor-4.

## Warranted audit-status value (for the COORDINATOR to record — Opus does NOT edit
   registry/audit-status.jsonl here)

- `codex_audited` = **CONFIRM** (the erratum soundly resolves the pin defect; all checks
  pass under the erratum-conditioned reading).
- `fable_interpretive_assessed` stays as the coordinator/Fable track dictates (Opus does
  not conclude); this run only supplies the mechanical cross-vendor re-audit result.
