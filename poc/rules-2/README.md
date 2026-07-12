# RULES-2 — train-time closure materialisation (BUILD, freeze-ready)

Built 2026-07-12 (fable-build-1) from `docs/next/design/rules-2-train-time.md`;
**rework-1** (cross-vendor review fixes 1–4) and **rework-2** (fixes 5/6/9 +
the rules-1-b supersede + the sharded parallel launch) the same day.
Registry record: `registry/experiments/rules-2.json` (**DRAFT** — the freeze is
the coordinator's). **No feasibility conclusion is stated anywhere in this
tree**; verdicts belong to `analysis/rules_2.py` + verdict-gen + the audit.

**REWORK-2 headline:** rules-1's GPU campaign was VOIDED 2026-07-12 — its bare
`\nAnswer:` cue left the answer DIRECTION to the model and a cue-adjacent menu
line swamped the small host, keeping every arm (even engine-direct A7) at ~0 —
and was superseded by the frozen **rules-1-b** record. RULES-2 would have
inherited exactly that broken surface, so rework-2 rebuilt every prompt on the
rules-1-b frame contract: menu inside the task header + a direction-explicit
infill cue rendered from the question's own closed template
(`Answer: {b} is {a}'s` for relation questions, `Answer: {e} is a` for typing
questions), applied identically at TRAIN and EVAL time; B4 imports the
rules-1-b runner bytes (`1f423ac0…`).

## What is here

| Path | Role |
|---|---|
| `materialise_closure.py` | $0-CPU deterministic pass: pin-verifies every RULES-1 artifact (fail closed), materialises the training default world's closure with the **pinned twin engine** → `data/rules2-train/` (21,780 examples; splits, c1′ label-derangement map, B1 upsample list, eval subsamples); TOKEN-level eval-name collision guard (rework-2 — `wv0-elvis-presley` excluded + listed); subcommand `c8` runs the **train-bytes projection gate** (G2) |
| `data/rules2-train/` | the pinned training corpus, kot-corpus-hash `3465e63d…` |
| `results/c8-result.json` | **G2 EXECUTED, $0 CPU**: S-out recovery 0/858 = 0.0 ≤ ceiling 0.10 → gate PASS; S-mem 1.0 (lookup by construction); S-held by kind (cover-cell string-leak disclosed); c4 floors. sha `cb3fecd3…` |
| `results/mock-validation.json` | the **PINNED GREEN MOCK** (review fix 9): monolithic + 13-shard mock runs, merge, analysis parity, verdict-mapping resolution, both tier dry-plans; tied to staged-bytes sha `56c713d4…`; the wrapper refuses full runs without a matching green artifact. sha `7b206cb1…` |
| `rules2_runner.py` | fine-tune + eval harness: arms B0/B1/B2/B3/B4/B5/c1p, LoRA (pinned HPs), greedy fp32 forced-choice eval (23-word menu + named refusal option), strata S-out/S-mem/S-held/guards, per-arm byte-identical repeat, raw-byte pin gate BEFORE any pinned import (review fix 6), `--mock` / `--dry-plan` / shard flags `--seeds`/`--shard-tag` |
| `merge_shards.py` | reconstructs the canonical results pair from independent shard jobs under fail-closed cross-shard pin/surface/coverage assertions |
| `validate_mock.py` | produces `results/mock-validation.json` (monolithic + sharded mock, parity, verdict mapping, dry-plans) |
| `inputs/rules2-manifest.json` | every pin + LoRA HPs + rules-1-b frames + planning constants + shard plan + mock spec |
| `modal/modal_rules2.py` | Modal wrapper: **programmatic launch gates** (freeze / sequencing / pinned green mock / per-tier dry-plan / R2 authorization — fail-closed), parallel shard fan-out (`--jobs` for account splitting), staged-manifest assertion in-container; `--print-manifest` / `--print-jobs` |
| `modal/requirements-image.txt` | pinned image = the f2b/rules-1 dep set + `peft` (`poc/modal/requirements-image.txt` untouched) |
| `asm-1440-1459.json` | EMITTED build ASM block, rework-2-corrected (registry/assumptions.jsonl **not** written) |
| `analysis/rules_2.py` (repo root) | pinned pure-function analysis; sha `ba47f4d8…` (unchanged by rework-2) |

Validated at $0 (all in `results/mock-validation.json`): real materialisation
(~5 s CPU), real c8 gate PASS, green `--mock` end-to-end monolithic AND as the
13 canonical shard jobs with `merge_shards.py` — pinned-analysis outputs
identical between the two paths on every field except process-measured
metrics (walls/RSS/engine-µs, disclosed); verdict mapping resolves on the
planted stub gradient; `--dry-plan` R1 tier worst **$13.92 / 12.66 GPU-h**
summed over **17 independent jobs, worst single job 1.26 h** (12 h Modal
function timeout) vs caps $18 / 14 h — OK; R2 tier (7 jobs) worst **$11.78**;
combined worst $25.70 < $35 outer ceiling.

## Coordinator freeze + parallel run protocol (exact steps)

1. **Sequencing gate first (PROPOSED-ASM-1420, now on rules-1-b):** the gate
   is ENFORCED by `modal_rules2._launch_gates` — it requires
   `registry/verdicts/rules-1-b.json` with verdict PASS. KILL-b → STOP:
   maintainer re-authorization required, s3′ struck.
   INSTRUMENT-INVALID/INCONCLUSIVE → blocked, no spend. (Freezing the record
   before the readout is fine; LAUNCHING is what the gate blocks.)
2. **Register ASMs centrally:** PROPOSED-ASM-1420..1439 (design appendix A)
   + PROPOSED-ASM-1440..1459 (`poc/rules-2/asm-1440-1459.json`,
   rework-2-corrected rows supersede earlier emissions) into
   `registry/assumptions.jsonl` (this build wrote neither).
3. **Re-verify + regenerate from pinned bytes** (deterministic, ~10 s CPU):
   `sha256sum poc/rules-2/materialise_closure.py analysis/rules_2.py poc/rules-2/merge_shards.py` vs the
   record pins; then
   `python3 poc/rules-2/materialise_closure.py build && python3 poc/rules-2/materialise_closure.py c8`
   and confirm the printed kot-corpus-hash `3465e63d…` and c8 sha `cb3fecd3…`
   reproduce byte-exactly.
4. **Re-run the mock validation** (or verify the pinned one):
   `python3 poc/rules-2/validate_mock.py` — must print parity + a verdict and
   write `results/mock-validation.json` carrying the CURRENT
   `--print-manifest` sha (`56c713d4…` at rework-2 build time).
5. **Pre-freeze skeptic pass** — flag list: ASM-1446 (refusal-option length
   bias + the rework-2 agrammatical-continuation disclosure, uniform),
   ASM-1444 (S-held cover-cell string leak, disclosed), ASM-1447 (B1
   token-count parity approximate), ASM-1452 (B3 proof-in-prompt deviation).
6. **Pin the harness manifest:**
   `python3 poc/rules-2/modal/modal_rules2.py --print-manifest`
   → confirm the sha inside `pins.harness_manifest` matches (record the
   freeze-time value; any later staged-byte change needs a correction
   record).
7. **Freeze:** `python3 tools/registry/prereg-freeze.py --experiment rules-2
   --agent-id coordinator-1` (dry-run first; DRY-RUN-OK verified at rework-2
   build time, non-fatal PAUSE on the open EXTRAPOLATION rows).
8. **Choose Modal account(s):** the harness is account-agnostic (app
   `kot-rules2`; a fresh account auto-creates its own `kot-hf-cache` volume
   and re-downloads SmolLM2 weights once, ~pennies). Activate a profile or
   source the coordinator's env file before each `modal run`.
9. **$0 + pennies validation on each account:**
   `.venv/bin/modal run poc/rules-2/modal/modal_rules2.py --dry-plan` (local,
   $0; all OK) then `… --mock` (transport smoke, in-container stub path).
10. **Real R1 tier — PARALLEL (usd_cap $18 / 14 GPU-h; est $9.28, worst
    $13.92):** single account:
    `nohup setsid .venv/bin/modal run poc/rules-2/modal/modal_rules2.py --gpu a10g > /tmp/rules2-run.log 2>&1 &`
    — spawns all 17 shard jobs concurrently, collects, merges into
    `results-incoming/<stamp>-modal/merged/`. Across N accounts: partition
    the 17 tags from `--print-jobs` and pass each account its subset via
    `--jobs tag1,tag2,…`; afterwards
    `python3 poc/rules-2/merge_shards.py --out-dir <merged> <every shard dir>`.
    Failed shards: relaunch ONLY the failed tags with `--jobs`. nohup+setsid
    per the standing bd memory; `modal app stop ap-<id>` after killing ANY
    attached client. Results are never auto-committed.
11. **Optional R2 rung** (separate authorization; worst $11.78; combined
    $25.70 < $35): `… --rungs R2 --authorize-r2` (7 jobs) after recording the
    authorization.
12. **Grade:** `python3 analysis/rules_2.py --run-records <merged>/run-records-rules2.jsonl
    --results <merged>/results-rules2.json --c8 poc/rules-2/results/c8-result.json
    --rules1-primary-lb <rules-1-b primary LB95>` → verdict-gen with the
    record's `verdict_rules`; then the cross-vendor audit. Runner never
    grades; this build never runs.
