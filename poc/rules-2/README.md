# RULES-2 — train-time closure materialisation (BUILD, freeze-ready; GPU HELD)

Built 2026-07-12 (fable-build-1) from `docs/next/design/rules-2-train-time.md`;
**rework-1** (cross-vendor review fixes 1–4), **rework-2** (fixes 5/6/9 + the
rules-1-b supersede + the sharded parallel launch) and **REWORK-3** (the
rules-1-c ENTITY-FORM re-base, this tree's current state) the same day.
Registry record: `registry/experiments/rules-2.json` (**DRAFT** — the freeze is
the coordinator's). **No feasibility conclusion is stated anywhere in this
tree**; verdicts belong to `analysis/rules_2.py` + verdict-gen + the audit.

**REWORK-3 headline:** rules-1-b never ran on GPU — its RELATION-WORD question
form is measured DEAD for unaided hosts
(`docs/next/analysis/rules1b-form-misattribution.md`), and it was superseded by
the frozen **rules-1-c** ENTITY form (`registry/experiments/rules-1-c.json`,
frozen_sha256 `09b246dc…`). RULES-2 as previously built could not run at all
(ERR_PIN on the rules-1-b runner pin; ERR_FRAME_DRIFT vs the entity-form
rules-1 manifest), so REWORK-3 re-based the ENTIRE train+eval surface onto the
rules-1-c contract: question `Who is the <rel> of <base>?` → object NAME,
direction-explicit entity cue `Answer: the {rel} of {a_name} is` (typing:
`Answer: {e_name} is a`), NO menu anywhere, uniform 3-option decode (per-cell
2-option anti-echo set + trained refusal; **chance 0.5, disclosed**); B4
imports the rules-1-c runner bytes (`91d780f3…`). Design record:
`docs/next/design/rules-2-train-time.md` **Appendix B**; ASM block
`asm-rework3-1800-1813.json`.

**B4 VACUITY FLAG (ASM-1808, for the coordinator):** the landed rules-1-c
campaign measured the A3 verify-retry channel VACUOUS (every A3 row
`attempts=1`; the imported `licensed_rejection` compares the engine's WORD
answer through a URN-keyed `urn2word` lookup — `rules1_runner.py:342` — and
abstains unconditionally). B4 inherits this byte-identically and degenerates to
attempt-0 entity rows; s3′ is conditional (ASM-1428) and drops out of the Holm
family under the predicted non-PASS parent branch. The B0–B5 train-time
internalisation arms do NOT use the verify-retry channel and are unaffected.
Repair belongs to rules-1-d under maintainer issue #24.

## What is here

| Path | Role |
|---|---|
| `materialise_closure.py` | $0-CPU deterministic pass: pin-verifies every RULES-1 artifact (fail closed), materialises the training default world's closure with the **pinned twin engine** → `data/rules2-train/` (21,780 ENTITY-form examples; splits, c1′ forced-flip map, B1 upsample list, eval subsamples); support-restricted family-2 chain contexts with per-cell unique-answer assertions (ASM-1801); TOKEN-level eval-name collision guard; subcommand `c8` runs the **train-bytes projection gate** (G2) on entity keys |
| `data/rules2-train/` | the pinned entity-form training corpus, kot-corpus-hash `c46aaa4e…` |
| `results/c8-result.json` | **G2 EXECUTED, $0 CPU (entity corpus)**: S-out recovery 0/858 = 0.0 ≤ ceiling 0.10 → gate PASS (ceiling chance-floor-independent); s_mem/s_held by kind with the entity-key ambiguity disclosure; c4 floors at chance 0.5. sha `674b424f…` |
| `results/mock-validation.json` | the **PINNED GREEN MOCK**: monolithic + 13-shard mock runs, merge, analysis parity, verdict-mapping resolution (PASS on the planted gradient), both tier dry-plans; tied to staged-bytes sha `d37640b2…`; the wrapper refuses full runs without a matching green artifact. sha `f72ad43d…` |
| `rules2_runner.py` | fine-tune + eval harness: arms B0/B1/B2/B3/B4/B5/c1p, LoRA (pinned HPs), greedy fp32 forced-choice eval (per-cell 2-option anti-echo set + named refusal = uniform 3-option decode), strata S-out/S-mem/S-held/guards, common 2-option `entailed2` gap cells, per-arm byte-identical repeat, raw-byte pin gate BEFORE any pinned import (review fix 6), `--mock` / `--dry-plan` / shard flags `--seeds`/`--shard-tag` |
| `merge_shards.py` | reconstructs the canonical results pair from independent shard jobs under fail-closed cross-shard pin/surface/coverage assertions |
| `validate_mock.py` | produces `results/mock-validation.json` (monolithic + sharded mock, parity, verdict mapping, dry-plans) |
| `inputs/rules2-manifest.json` | every pin + LoRA HPs + rules-1-c ENTITY frames + planning constants + shard plan + mock spec |
| `modal/modal_rules2.py` | Modal wrapper: **programmatic launch gates** (freeze / rules-1-c sequencing+issue-#24 hold / pinned green mock / per-tier dry-plan / R2 authorization — fail-closed), parallel shard fan-out (`--jobs` for account splitting), staged-manifest assertion in-container; `--print-manifest` / `--print-jobs` |
| `modal/requirements-image.txt` | pinned image = the f2b/rules-1 dep set + `peft` (`poc/modal/requirements-image.txt` untouched) |
| `instr_pilot.py` | **BLOCKING INSTRUMENT PILOT** (pre-freeze validity gate, PROPOSED-ASM-1814..1819): tiny real-GPU pilot at the operating point — IP-1 B2-pilot-vs-B0 separation non-degenerate (n=60 S-out, exact-binomial floor bound, headroom + refusal caps), IP-2 c8 shortcut-audit teeth (real lookup ≤ ceiling AND a planted exploiter FIRES the gate, $0 CPU), IP-3 c1p forced-flip control non-degenerate (no abstention/treatment collapse), IP-4 B4 verify-retry vacuity FLAG (attempts==1 ⇒ ASM-1808 inherited). PILOT-FAIL (rc=3) **blocks the freeze**; verdict is instrument-validity only, never campaign evidence |
| `validate_instrpilot.py` | $0 pilot validation: normal mock ⇒ PILOT-PASS-WITH-FLAGS, planted-DEGENERATE mock ⇒ PILOT-FAIL via IP-1 (the pilot's own gates have teeth), dry-plan ≤ $2 cap; writes `results/instrpilot-mock-validation.json` and asserts the CAMPAIGN staged-bytes sha `d37640b2…` is unchanged by the pilot build |
| `results/instrpilot-mock-validation.json` | the **PINNED GREEN PILOT MOCK** (pilot staged sha `24fc793c…`); `modal_instrpilot.py` refuses to launch without a matching green artifact |
| `modal/modal_instrpilot.py` | pilot Modal wrapper (own app `kot-rules2-instrpilot`, own staged sha — the campaign surface does not drift): gates = pinned green pilot mock + dry-plan ≤ $2; freeze/sequencing gates DELIBERATELY absent (it IS the pre-freeze gate; assessment §4 item 1: the pilot need not wait on the issue-#24 campaign hold) |
| `asm-1440-1459.json`, `asm-rework3-1800-1813.json`, `asm-instrpilot-1814-1819.json` | EMITTED build ASM blocks (registry/assumptions.jsonl **not** written) |
| `analysis/rules_2.py` (repo root) | pinned pure-function analysis (entity surface, `entailed2` gap cells); sha `782bc9eb…` |

Validated at $0 (all in `results/mock-validation.json`): real entity-form
materialisation (~2 min CPU on this box), real c8 gate PASS, green `--mock`
end-to-end monolithic AND as the 13 canonical shard jobs with
`merge_shards.py` — pinned-analysis outputs identical between the two paths on
every field except process-measured metrics (walls/RSS/engine-µs, disclosed);
verdict mapping resolves PASS on the planted stub gradient; `--dry-plan` R1
tier worst **$6.51 / 5.92 GPU-h** summed over **17 independent jobs, worst
single job 0.57 h** (12 h Modal function timeout) vs caps $18 / 14 h — OK; R2
tier (7 jobs) worst **$6.51**; combined worst ~$13.02 < $35 outer ceiling.
`prereg-freeze --dry-run` = **DRY-RUN-OK** at build time (non-fatal PAUSE on
open EXTRAPOLATION rows).

## BLOCKING INSTRUMENT PILOT — run BEFORE the freeze (PROPOSED-ASM-1814..1819)

The mandatory exercised-at-operating-point pilot demanded by
`docs/next/analysis/correctness-track-instrument-assessment.md` §2.2/§4
(its absence is why rules-1-c froze and then graded INSTRUMENT-INVALID).
Near-$0: **worst-case $0.27 on A10G** (est $0.18, ~0.16 GPU-h), hard-capped
fail-closed at $2. Standalone runner — the campaign staged-bytes sha
`d37640b2…` and its pinned mock are byte-identical before/after this build.

1. `python3 poc/rules-2/validate_instrpilot.py` — $0; re-pins
   `results/instrpilot-mock-validation.json` (normal mock PASS-WITH-FLAGS,
   degenerate mock FAIL, dry-plan ≤ $2, campaign sha unchanged). Green at
   build time (pilot staged sha `24fc793c…`).
2. `.venv/bin/modal run poc/rules-2/modal/modal_instrpilot.py --dry-plan`
   ($0, local) and optionally `… --mock` (transport smoke, pennies).
3. **THE pilot (coordinator launches; the only GPU spend):**
   `nohup setsid .venv/bin/modal run poc/rules-2/modal/modal_instrpilot.py --gpu a10g > /tmp/rules2-instrpilot.log 2>&1 &`
   — single job, ~15 min; `modal app stop ap-<id>` after killing any
   attached client (standing bd memory). Results →
   `results-incoming/<stamp>-instrpilot/instrpilot-result.json`.
4. Read the verdict: **PILOT-PASS / PILOT-PASS-WITH-FLAGS** (b4_vacuous
   expected TRUE per ASM-1808 → carry the flag into the issue-#24 B4/s3′
   disposition) ⇒ proceed to the freeze protocol below. **PILOT-FAIL
   (rc=3) ⇒ the freeze is BLOCKED** pending redesign or an explicit
   coordinator override record (ASM-1814). Pilot numbers are
   instrument-validity data only — never campaign evidence (ASM-1819).

## Coordinator freeze + launch protocol (exact steps; GPU HELD pending issue #24)

**Step 0 (NEW, blocking): the instrument pilot above must have reported
PILOT-PASS or PILOT-PASS-WITH-FLAGS on real GPU before `prereg-freeze`.**

1. **Sequencing gate first (ASM-1420 as corrected by ASM-1807, now on
   rules-1-c):** the gate is ENFORCED by `modal_rules2._launch_gates` — it
   requires `registry/verdicts/rules-1-c.json` with verdict PASS. The landed
   rows PREDICT INSTRUMENT-INVALID, so expect the gate to HOLD: every
   non-PASS branch requires the maintainer's **issue #24** host-integration
   slot decision (rules-1-d repair vs rules-2 as the replacement slot; B4/s3′
   fate) and a record amendment re-registering the gate; KILL-b additionally
   requires explicit maintainer re-authorization, s3′ struck. (Freezing the
   record before the readout is fine; LAUNCHING is what the gate blocks.)
2. **Resolve the ASM-1806 DESIGN-OPEN through the GPT-5.6 review gate**
   (pick-the-non-bridge shortcut residual: argue a bound or register an added
   gate/stratum) BEFORE freezing.
3. **Register ASMs centrally:** PROPOSED-ASM-1420..1439 (design appendix A) +
   1440..1459 (`asm-1440-1459.json`) + **ASM-1800..1813**
   (`asm-rework3-1800-1813.json`) into `registry/assumptions.jsonl` (this
   build wrote none of them).
4. **Re-verify + regenerate from pinned bytes** (deterministic CPU):
   `sha256sum poc/rules-2/materialise_closure.py analysis/rules_2.py poc/rules-2/merge_shards.py`
   vs the record pins (`66e45adc…` / `782bc9eb…` / `d82e239f…`); then
   `python3 poc/rules-2/materialise_closure.py build && python3 poc/rules-2/materialise_closure.py c8`
   and confirm the printed kot-corpus-hash `c46aaa4e…` and c8 sha `674b424f…`
   reproduce byte-exactly.
5. **Re-run the mock validation** (or verify the pinned one):
   `python3 poc/rules-2/validate_mock.py` — must print parity + a verdict and
   write `results/mock-validation.json` carrying the CURRENT
   `--print-manifest` sha (`d37640b2…` at REWORK-3 build time).
6. **Pre-freeze skeptic pass** — flag list: ASM-1802/1446 (refusal-option
   length bias + agrammatical continuation, uniform, disclosed), ASM-1804
   (s_mem anchor <1.0 on entity keys, disclosed), ASM-1806 (shortcut
   DESIGN-OPEN), ASM-1808 (B4 vacuity inheritance), ASM-1447 (B1 token-count
   parity approximate), ASM-1452 (B3 proof-in-prompt deviation).
7. **Pin the harness manifest:**
   `python3 poc/rules-2/modal/modal_rules2.py --print-manifest` → confirm the
   sha inside `pins.harness_manifest` matches (record the freeze-time value;
   any later staged-byte change needs a correction record).
8. **Freeze:** `python3 tools/registry/prereg-freeze.py --experiment rules-2
   --agent-id coordinator-1` (dry-run first; DRY-RUN-OK verified at REWORK-3
   build time, non-fatal PAUSE on the open EXTRAPOLATION rows).
9. **Choose Modal account(s):** the harness is account-agnostic (app
   `kot-rules2`; a fresh account auto-creates its own `kot-hf-cache` volume
   and re-downloads SmolLM2 weights once, ~pennies). Activate a profile or
   source the coordinator's env file before each `modal run`.
10. **$0 + pennies validation on each account:**
    `.venv/bin/modal run poc/rules-2/modal/modal_rules2.py --dry-plan` (local,
    $0; all OK) then `… --mock` (transport smoke, in-container stub path).
11. **Real R1 tier — PARALLEL (usd_cap $18 / 14 GPU-h; est $4.34, worst
    $6.51), ONLY after the gate opens per step 1:** single account:
    `nohup setsid .venv/bin/modal run poc/rules-2/modal/modal_rules2.py --gpu a10g > /tmp/rules2-run.log 2>&1 &`
    — spawns all 17 shard jobs concurrently, collects, merges into
    `results-incoming/<stamp>-modal/merged/`. Across N accounts: partition
    the 17 tags from `--print-jobs` and pass each account its subset via
    `--jobs tag1,tag2,…`; afterwards
    `python3 poc/rules-2/merge_shards.py --out-dir <merged> <every shard dir>`.
    Failed shards: relaunch ONLY the failed tags with `--jobs`. nohup+setsid
    per the standing bd memory; `modal app stop ap-<id>` after killing ANY
    attached client. Results are never auto-committed.
12. **Optional R2 rung** (separate authorization; worst $6.51; combined
    ~$13.02 < $35): `… --rungs R2 --authorize-r2` (7 jobs) after recording
    the authorization.
13. **Grade:** `python3 analysis/rules_2.py --run-records <merged>/run-records-rules2.jsonl
    --results <merged>/results-rules2.json --c8 poc/rules-2/results/c8-result.json
    --rules1-primary-lb <rules-1-c primary LB95, if a positive one exists>` →
    verdict-gen with the record's `verdict_rules`; then the cross-vendor
    audit. Runner never grades; this build never runs.
