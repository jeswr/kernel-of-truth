# f2b-transfer-llmproxy Stage-1 — Opus experiment-runner run-log

Runner: kern/opus-runner (experiment-runner role). Mechanical execution of a
FROZEN Fable design. NO interpretation, NO conclusion (Fable's; the reduced
envelope in the record binds). Governance path: `poc/f2b-transfer/llmproxy-design.md` §S5.

STAND-IN, NOT the adjudicating experiment. f2b-transfer (frozen_sha256
b341a0901e12023d3c56bdc196be0b9c492c7d348f988416d7e9c43aade20879) is byte-untouched.

## Pins verified at run start (all OK)

- blind-items-by-id.jsonl `ce820483…` (360 items; id-aligned to d-qa-t gold, unique)
- judge-2 template/schemas/calibration — all OK (see judge-2 spec §0)
- judge-1p template `19b02999…`, deranged-probe.jsonl `4479c619…`,
  deranged-probe-manifest.json `ff5d7c1f…`, judge-1p-invocation.md `4e487159…`
- analysis/f2b_transfer_llmproxy.py `94f0a181…` == record pin; `--selftest` OK
- membership gold = data/d-qa-t/items/covered.jsonl `answer` (d-qa-t corpus pin 7179ee…);
  all 360 blind ids have gold; gold values ∈ {A,B,C,D,yes,no} (no escapes in gold)
- probe run-order (seed `dadjt/1|judge-1p-probe|20260711`) reproduces manifest run_position (60/60)
- global codex `codex-cli 0.142.5` (judge-2 pin); npx `@openai/codex@0.144.1` → `codex-cli 0.144.1` (judge-1p pin); global untouched

## Step 1 — judge-2 diagnostic RE-RUN (DEMOTED; FAIL-only stability gate + reported diagnostic)

Prior run 20260709T232652Z DIED at ~30/360 (detached job orphaned). Re-run IN-PROCESS
(harness-monitored background, not detached) in the same run dir per task.

- preflight re-run (2 calibration items): PASS (bicycle→B, umbrella→yes), first-attempt-valid, codex 0.142.5, fresh workdir
- main re-run: `nice -n 10 python3 poc/f2b-transfer/opus-runs/20260709T232652Z/run-judge2.py main` (harness bg job)
- COMPLETE (exit 0): 360/360 items, n_judge2_nolabel=0, total_transport_retries=0, elapsed ~1499s
- responses: `data/d-adj-t/judge-2-responses.jsonl` sha256 `7291a9955f2bba2e8c98d97f0231a36a3ed29192379a57bb0cae8468009d3b60`
- label_counts: A44 B49 C71 D52 no85 yes58 cannot-say1 (216 mcq, 144 claim)
- RT-14 scrub gate: 0 @/email matches across judge-2 provenance (1440 items files + responses/summary/posmap) → 0 redactions

## Scripts written by the runner (mechanical operationalisations of the frozen specs)

- `poc/f2b-transfer/llmproxy-runs/20260710T001512Z/run-judge1p.py` — faithful port of the
  proven run-judge2.py; frozen judge-1p deltas only (npx codex 0.144.1, gpt-5.6-sol,
  judge-1 role shuffle `dadjt/1|judge-1|20260710`, trailing 60-probe block, pseudonym judge-1p, no judge-3)
- `poc/f2b-transfer/llmproxy-runs/20260710T001512Z/assemble-llmproxy.py` — mechanical join of
  judge-1p + judge-2 responses + membership gold + probe manifest → labels-proxy.jsonl + summary.json
  (analysis-input integers per the frozen analysis _rec fields; every field traces to a pinned definition)

## Step 2 — prereg-freeze (dry-run validated)

- `prereg-freeze --experiment f2b-transfer-llmproxy --agent-id coordinator-1 --dry-run`:
  DRY-RUN-OK, one expected non-fatal PAUSE on ASM-0021 (open EXTRAPOLATION). candidate hash printed.
- REAL freeze (`--agent-id coordinator-1`): status FROZEN, frozen_at 2026-07-10T00:37:19Z, frozen_by coordinator-1.
  **frozen_sha256 = `c9d81ee5c163db8febbf256878a4684e5e4b4984c5452dd303b5a0b0daa74d87`** (record == frozen-index).
  Same expected PAUSE on ASM-0021 (recorded to registry/pause-flags.jsonl). f2b-transfer UNTOUCHED (b341a090…).

## Step 3 — ops-amend judge-2-responses artifact pin

- `registry/amendments/f2b-transfer-llmproxy/1-pin-judge-2-responses.json` (kind ops, seq 1):
  replace `/pins/artifact_hashes/data~1d-adj-t~1judge-2-responses.jsonl` → `7291a995…`
- overlay verified via verdict-gen apply_amendment_overlay: applied [1]; judge-2 pin resolved;
  d-adj-t-llmproxy corpus placeholder still open (filled by seq 2 after judge-1p); post-overlay valid.

## Pre-spend reuse gate (BINDING, before paid judge-1p launch)

- `reuse-check.py check --record registry/experiments/f2b-transfer-llmproxy.json --gate`: EXIT 0
  (1 grid cell; 0 blocking, 0 covered, 0 provably-different, 1 unlogged). Clear to spend.

## Step 4 — judge-1p (GPT-5.6-Sol) run

- preflight (2 calibration items, npx codex 0.144.1, gpt-5.6-sol): PASS first-attempt (bicycle→B, umbrella→yes); global codex still 0.142.5
- main: 360 real d-qa-t items in judge-1 role shuffle `dadjt/1|judge-1|20260710` → 60 probes in `dadjt/1|judge-1p-probe|20260711`
  (probe run-order cross-checked against manifest run_position, fail-closed). COMPLETE (exit 0):
  360/360 real (0 no-label, 0 transport), 60/60 probes (0 no-label), elapsed ~1861s.
  real labels A43 B49 C71 D52 NONE1 no93 yes51; probe labels NONE59 A1.
- responses `d8337eb8…`, probe-responses `cf6eadc2…`. RT-14: no @ in judge-1p responses. Global codex still 0.142.5.

## Step 5 — assemble d-adj-t-llmproxy + corpus-pin + ops-amend

- `assemble-llmproxy.py` → labels-proxy.jsonl (`f0f1ada5…`, gold source judge-1p ALONE; membership gold = d-qa-t `answer`; escape=disagreement) + summary.json.
  analysis-input integers: n_items 360, n_labelled_j1p 360, n_nolabel_j1p 0, n_agree_j1p 342, n_escape_j1p 1,
  judge_pairs_both_labelled 360, judge_pairs_token_equal 347, n_labelled_j2 360, n_agree_j2 345,
  panel_resolved 347, panel_agree_membership 337, n_probe_labelled 60, n_probe_false_endorse 1,
  n_probe_none 59, n_probe_deranged_pick 1, preflight_pass true.
- corpus-pin d-adj-t-llmproxy → `5f442396…` (9 files; account_lint CLEAN, only @ is npm spec).
- ops amendment seq 2 (`2-pin-d-adj-t-llmproxy-corpus.json`): replace `/pins/corpus_hashes/d-adj-t-llmproxy` → `5f442396…`.
  Full overlay [1,2] applies clean: 0 remaining PINNED-AT-INPUTS; effective_record_sha256 `62a51505…`; corpus pin reproduces.

## Step 6 — log-append final record + verdict-gen

- log-append (runner-7): results-log/f2b-transfer-llmproxy.jsonl seq 0 (event run, phase final, exit ok, prereg_hash c9d81ee5…, config arm=adjudication-instrument).
- verdict-gen (runner-7): **verdict PASS-PENDING-AUDIT, fired_rule_index 2**. eligible_runs 1, amendments_applied [1,2], analysis_output_sha256 `73f4bce9…`, amended_record_sha256 `62a51505…`.
  Mechanical values: external_endorsement_proxy A_1p = 0.95 (342/360); Wilson one-sided 95% LB = 0.9275206595861619 (>> 0.70);
  adjudication_valid true; probe_valid true; probe_false_endorse_rate 0.016667 (1/60); judge_pair_agreement_raw 0.963889 (347/360);
  a_j2 0.958333 (345/360, diagnostic); a_panel_concordant 0.971182 (337/347, diagnostic); panel_unresolved_fraction 0.036111.
  verdict-gen appended the unblind line (seq 1).
- reuse-check.py build (post-final-append): 127 rows / 10 experiments. registry-check: PASS (after kb-sync-internal wrote internal_f2b-transfer-llmproxy.json).

## Step 7 — Codex Gate-A cross-vendor audit (family-overlap DISCLOSED)

- auditor auditor-4 = Codex/GPT-5.5 (global codex-cli 0.142.5), high reasoning, read-only, -C repo root.
- MANDATORY family-overlap disclosure baked into the brief: auditor shares GPT-5.x family with judge-1p (GPT-5.6) and judge-2 (GPT-5.5);
  audit certifies MECHANICS ONLY, never judge quality.
- smoke: KOT-AUDIT-SMOKE-OK returned. audit launched (recompute frozen hash / chain / overlay / pins / labels-from-bytes / analysis / gates / verdict rule).
- [audit outcome appended below]
