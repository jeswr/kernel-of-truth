# RULES-2 — train-time closure materialisation (GO; freeze-ready)

Built 2026-07-12 (fable-build-1) from `docs/next/design/rules-2-train-time.md`;
**rework-1** (cross-vendor review fixes 1–4), **rework-2** (fixes 5/6/9 + the
rules-1-b supersede + the sharded parallel launch), **REWORK-3** (the
rules-1-c ENTITY-FORM re-base) and the **GO finalisation** (fable-build-4,
same day; design doc **Appendix C**) — this tree's current state.
Registry record: `registry/experiments/rules-2.json` (**DRAFT** — the freeze
is the coordinator's). **No feasibility conclusion is stated anywhere in this
tree**; verdicts belong to `analysis/rules_2_go.py` + verdict-gen + the audit.

**GO headline (maintainer issue #24 decision (C), 2026-07-12):** RULES-2 is
the host-integration slot's replacement instrument after the rules-1-c
INSTRUMENT-INVALID readout. The **blocking instrument pilot** ran on real GPU
and reported **PILOT-PASS-WITH-FLAGS** (IP-1 separation ✓, IP-2 audit-teeth ✓,
IP-3 control ✓, IP-4 B4-vacuity FLAG TRUE), pinned as `pins.blocking_pilot`
(artifact `results-incoming/20260712-165344-instrpilot/instrpilot-result.json`,
sha `872477ef…`). Consequences, all landed in this tree:

- **B4 + s3′ + the `entailed2` gap surface are STRUCK** (ASM-1848): the
  imported rules-1-c A3 verify-retry channel is measured VACUOUS at the
  2-option entity operating point (attempts=1 everywhere — landed rows AND
  pilot IP-4); the verify-retry question is settled un-instrumentable at
  2-option scale. Arms: **B0/B1/B2/B3/B5/c1p**; Holm family **{s1′,s2′,s4′}**;
  the engine-at-inference price column is a DESCRIPTIVE cross-campaign pointer
  to the landed rules-1-c ledger; no break-even N\*.
- **Analysis successor `analysis/rules_2_go.py`** (ASM-1853): the pre-GO
  `analysis/rules_2.py` (sha `782bc9eb…`) was pinned inside the pilot artifact
  and is retained on disk UNEDITED; statistics carried verbatim, s3′/B4
  surfaces removed.
- **The MANDATORY knull analog EXISTS and its $0 leg is EXECUTED**
  (ASM-1849..1852): sibling campaign `registry/experiments/rules-2-knull.json`
  + `knull_analog.py`. Result: the plain-dictionary (knull) rules source
  derives the **byte-identical training corpus** — 21,780/21,780 examples
  surface-equal, family-2 13,020/13,020 at 1.0 (`results/knull-analog-result.json`,
  sha `afcf09e8…`). The GPU leg (c5k-vs-B2) is conditional-vacuous:
  registered, prohibited to run. Claim cap (ASM-1138/1438) resolves
  deflationary: NO rules-2 outcome licenses "kernel-specific value".
- **Sequencing gate re-registered** (ASM-1847): machine-readable
  `sequencing_gate` block in the record; `modal_rules2._launch_gates` opens
  the GPU path on FROZEN status + rules-1-c verdict EXISTS + the block +
  green pinned mock + per-tier dry-plan (+ `--authorize-r2` for R2).

## What is here

| Path | Role |
|---|---|
| `materialise_closure.py` | $0-CPU deterministic pass: pin-verifies every RULES-1 artifact (fail closed), materialises the training default world's closure with the **pinned twin engine** → `data/rules2-train/` (21,780 ENTITY-form examples); subcommand `c8` runs the **train-bytes projection gate** (G2) |
| `data/rules2-train/` | the pinned entity-form training corpus, kot-corpus-hash `c46aaa4e…` |
| `results/c8-result.json` | **G2 EXECUTED, $0 CPU**: S-out recovery 0/858 ≤ 0.10 → PASS. sha `674b424f…` |
| `results/mock-validation.json` | the **PINNED GREEN MOCK** (GO re-pin): monolithic + 10-shard mock runs, merge, successor-analysis parity, verdict mapping, both tier dry-plans; carries the GO staged-bytes sha; the wrapper refuses full runs without a matching green artifact |
| `rules2_runner.py` | fine-tune + eval harness, arms **B0/B1/B2/B3/B5/c1p** (B4 struck), LoRA (pinned HPs), greedy fp32 forced-choice eval (uniform 3-option decode), strata + per-arm byte-identical repeat, raw-byte pin gate before any pinned import, `--mock`/`--dry-plan`/shard flags |
| `merge_shards.py` | reconstructs the canonical results pair from independent shard jobs (fail-closed cross-shard assertions) |
| `validate_mock.py` | produces `results/mock-validation.json` (mono + sharded mock, parity vs `analysis/rules_2_go.py`, verdict mapping, dry-plans) |
| `knull_analog.py` | **KNULL ANALOG leg 1, EXECUTED $0 CPU** (ASM-1849..1852): regenerates the training examples under kernel AND knull TBoxes over the identical component set (kernel side anchored byte-equal to the pinned corpus, fail-closed) and compares per-id training surfaces → `results/knull-analog-result.json` |
| `results/knull-analog-result.json` | fully surface-equivalent (21,780/21,780; family-2 13,020/13,020 at 1.0; proof sidecars included). sha `afcf09e8…` — the sibling campaign's pinned leg-1 artifact |
| `inputs/rules2-manifest.json` | every pin + LoRA HPs + rules-1-c ENTITY frames + planning constants + shard plan + mock spec |
| `modal/modal_rules2.py` | Modal wrapper: **programmatic launch gates** (freeze / re-registered sequencing gate / pinned green mock / per-tier dry-plan / R2 authorization — fail-closed), parallel shard fan-out (`--jobs` for account splitting); `--print-manifest` / `--print-jobs` |
| `instr_pilot.py` + `validate_instrpilot.py` + `modal/modal_instrpilot.py` | the blocking instrument pilot (ASM-1814..1819) — **RAN 2026-07-12, PILOT-PASS-WITH-FLAGS** (`results-incoming/20260712-165344-instrpilot/`); pilot numbers are instrument-validity data only |
| `asm-1440-1459.json`, `asm-rework3-1800-1813.json`, `asm-instrpilot-1814-1819.json`, `asm-go-1847-1859.json` | EMITTED build ASM blocks (registry/assumptions.jsonl **not** written by builds) |
| `analysis/rules_2_go.py` (repo root) | pinned pure-function GO analysis (successor of `analysis/rules_2.py`, retained unedited) |

Validated at $0 at GO time (all in `results/mock-validation.json`): green
`--mock` end-to-end monolithic AND as the 10 canonical shard jobs +
`merge_shards.py` — successor-analysis outputs identical between the two
paths except process-measured metrics (disclosed); verdict mapping resolves
on the planted stub gradient; `--dry-plan` **R1 tier: 14 jobs, est $4.30 /
worst $6.46 (5.87 worst GPU-h; worst single job 0.57 h)** vs caps $18 / 14 h —
OK; **R2 tier: 7 jobs, worst $6.51 (worst single job 1.14 h)**; combined worst
≈ **$12.97** < $35 outer ceiling. `prereg-freeze --dry-run` = **DRY-RUN-OK**
at GO build time (non-fatal PAUSE on open EXTRAPOLATION rows).

## Coordinator freeze + launch protocol (GO; exact steps)

Step 0 is DONE: the blocking pilot reported PILOT-PASS-WITH-FLAGS on real GPU
(pinned as `pins.blocking_pilot`); the IP-4 flag is RESOLVED by the B4/s3′
strike (ASM-1848). The ASM-1806 DESIGN-OPEN (pick-the-non-bridge shortcut
residual) still goes through the GPT-5.6 review gate before freezing.

1. **Register ASMs centrally:** PROPOSED-ASM-1420..1439 (design appendix A) +
   1440..1459 + 1800..1813 + **1847..1859** (`asm-go-1847-1859.json`) into
   `registry/assumptions.jsonl` (builds wrote none of them).
2. **Re-verify + regenerate from pinned bytes** (deterministic CPU):
   `sha256sum poc/rules-2/materialise_closure.py analysis/rules_2_go.py poc/rules-2/merge_shards.py poc/rules-2/knull_analog.py`
   vs the record pins; then
   `python3 poc/rules-2/materialise_closure.py build && python3 poc/rules-2/materialise_closure.py c8 && python3 poc/rules-2/knull_analog.py`
   and confirm kot-corpus-hash `c46aaa4e…`, c8 sha `674b424f…` and
   knull-analog sha `afcf09e8…` reproduce byte-exactly.
3. **Re-run (or verify) the mock:** `python3 poc/rules-2/validate_mock.py` —
   must print parity + a verdict and carry the CURRENT `--print-manifest` sha.
4. **Pin the harness manifest:**
   `python3 poc/rules-2/modal/modal_rules2.py --print-manifest` → must match
   `pins.harness_manifest` and the mock artifact (any later staged-byte
   change needs a correction record, ASM-1459).
5. **Freeze:** `python3 tools/registry/prereg-freeze.py --experiment rules-2
   --agent-id coordinator-1 --dry-run` (expect DRY-RUN-OK), then without
   `--dry-run`.
6. **Per account:** activate the Modal profile, then
   `.venv/bin/modal run poc/rules-2/modal/modal_rules2.py --dry-plan` ($0)
   and optionally `… --mock` (transport smoke, pennies).
7. **R1 tier — PARALLEL (14 jobs; est $4.30, worst $6.46):** single account:
   `nohup setsid .venv/bin/modal run poc/rules-2/modal/modal_rules2.py --gpu a10g > /tmp/rules2-run.log 2>&1 &`
   Across N accounts: partition the 14 tags from `--print-jobs`, pass each
   account its subset via `--jobs tag1,tag2,…`; then
   `python3 poc/rules-2/merge_shards.py --out-dir <merged> <every shard dir>`.
   Failed shards: relaunch ONLY the failed tags with `--jobs`. nohup+setsid
   per the standing bd memory; `modal app stop ap-<id>` after killing ANY
   attached client.
8. **Optional R2 rung** (separate authorization; 7 jobs, worst $6.51;
   combined ≈$12.97): `… --rungs R2 --authorize-r2` after recording it.
9. **Grade:** `python3 analysis/rules_2_go.py --run-records
   <merged>/run-records-rules2.jsonl --results <merged>/results-rules2.json
   --c8 poc/rules-2/results/c8-result.json` → verdict-gen with the record's
   `verdict_rules`; then the cross-vendor audit. Runner never grades; this
   build never runs. The knull sibling's GPU leg is NOT launched (leg-1
   equivalence makes it vacuous; see rules-2-knull `kill_criterion_verbatim`).
