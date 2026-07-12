# RULES-2 — train-time closure materialisation (BUILD, freeze-ready)

Built 2026-07-12 (fable-build-1) from `docs/next/design/rules-2-train-time.md`.
Registry record: `registry/experiments/rules-2.json` (**DRAFT** — the freeze is
the coordinator's). **No feasibility conclusion is stated anywhere in this
tree**; verdicts belong to `analysis/rules_2.py` + verdict-gen + the audit.

## What is here

| Path | Role |
|---|---|
| `materialise_closure.py` | $0-CPU deterministic pass: pin-verifies every RULES-1 artifact (fail closed), materialises the training default world's closure with the **pinned twin engine** → `data/rules2-train/` (21,796 examples; splits, c1′ derangement map, B1 upsample list, eval subsamples); subcommand `c8` runs the **train-bytes projection gate** (G2) |
| `data/rules2-train/` | the pinned training corpus, kot-corpus-hash `8e0b3945…` |
| `results/c8-result.json` | **G2 EXECUTED, $0 CPU**: S-out recovery 0/858 = 0.0 ≤ ceiling 0.10 → gate PASS; S-mem 1.0 (lookup by construction); S-held by kind (cover-cell string-leak disclosed); c4 floors. sha `2c34db34…` |
| `rules2_runner.py` | fine-tune + eval harness: arms B0/B1/B2/B3/B4/B5/c1p, LoRA (pinned HPs), greedy fp32 forced-choice eval (23-word menu + named refusal option), strata S-out/S-mem/S-held/guards, per-arm byte-identical repeat, `--mock` / `--dry-plan` |
| `inputs/rules2-manifest.json` | every pin + LoRA HPs + frames + planning constants + mock spec |
| `modal/modal_rules2.py` | Modal wrapper (modal_rules1/f2b pattern): stages bytes, asserts staged manifest in-container, ships opaque results + sidecar provenance; `--print-manifest` for the harness-manifest pin |
| `modal/requirements-image.txt` | pinned image = the f2b/rules-1 dep set + `peft==0.15.2` (`poc/modal/requirements-image.txt` untouched) |
| `asm-1440-1459.json` | EMITTED build ASM block (registry/assumptions.jsonl **not** written) |
| `analysis/rules_2.py` (repo root) | pinned pure-function analysis; sha `873e8c79…` |

Validated at $0: real materialisation (4.4 s CPU), real c8 gate PASS, green
`--mock` end-to-end (all 4 gates + primary/s1′/s2′/s4′ pass-shape on the
planted stub gradient), `--dry-plan` R1 tier worst **$13.48 / 12.3 h** vs caps
$18 / 14 h (OK); R1+R2 combined worst $25.10 → correctly fails closed pending
coordinator authorization (inside the $35 outer ceiling).

## Coordinator freeze + run protocol (exact steps)

1. **Sequencing gate first (PROPOSED-ASM-1420):** confirm the RULES-1 GPU
   readout exists (`registry/verdicts/rules-1*`). PASS → proceed (s3′ live).
   KILL-b → STOP: maintainer re-authorization required, s3′ struck.
   INSTRUMENT-INVALID/INCONCLUSIVE → blocked, no spend.
2. **Register ASMs centrally:** PROPOSED-ASM-1420..1439 (design appendix A)
   + PROPOSED-ASM-1440..1459 (`poc/rules-2/asm-1440-1459.json`) into
   `registry/assumptions.jsonl` (this build wrote neither).
3. **Re-verify + regenerate from pinned bytes** (deterministic, ~5 s CPU):
   `sha256sum poc/rules-2/materialise_closure.py analysis/rules_2.py` vs the
   record pins; then
   `python3 poc/rules-2/materialise_closure.py build && python3 poc/rules-2/materialise_closure.py c8`
   and confirm the printed kot-corpus-hash `8e0b3945…` and c8 sha `2c34db34…`
   reproduce byte-exactly.
4. **Pre-freeze skeptic pass** — flag list: PROPOSED-ASM-1452 (B0 padded /
   FT-arms unpadded prompt asymmetry; B3 proof-in-prompt deviation),
   ASM-1446 (refusal-option length bias, uniform), ASM-1444 (S-held cover-cell
   string leak, disclosed), ASM-1447 (B1 token-count parity approximate).
5. **Pin the harness manifest:**
   `python3 poc/rules-2/modal/modal_rules2.py --print-manifest`
   → write the printed sha into `pins.harness_manifest`
   (build-time value `b8e68d75…`; recompute at freeze).
6. **Freeze:** `tools/registry/prereg-freeze.py` on
   `registry/experiments/rules-2.json` (status DRAFT → FROZEN).
7. **Select the Modal account:** the standing profile on this box is
   `jmwright-045` (`~/.modal.toml`, active; Tier-0/F2 lineage, HF cache
   volume `kot-hf-cache` already warm). To use an idle account from the
   coordinator's `modalN.env` pool instead: `set -a; source modalN.env` (or
   `modal profile activate <name>`) before every `modal run` — the harness is
   account-agnostic (app `kot-rules2`; a fresh account auto-creates its own
   `kot-hf-cache` volume and re-downloads SmolLM2 weights once, ~pennies).
8. **$0 + pennies validation on the chosen account:**
   `.venv/bin/modal run poc/rules-2/modal/modal_rules2.py --dry-plan` (local, $0; must print all OK)
   then `.venv/bin/modal run poc/rules-2/modal/modal_rules2.py --mock`
   (transport smoke: builds the peft image, asserts staged manifest, runs the
   stub path in-container, ~pennies).
9. **Real R1 tier** (usd_cap $18 / 14 GPU-h; est $9, worst $13.48):
   `nohup setsid .venv/bin/modal run poc/rules-2/modal/modal_rules2.py --gpu a10g > /tmp/rules2-run.log 2>&1 &`
   — nohup+setsid per the standing bd memory; after killing ANY attached
   client run `modal app stop ap-<id>`. Results land in
   `poc/rules-2/results-incoming/<stamp>-modal/` (never auto-committed).
10. **Optional R2 rung** (separate authorization; combined worst $25.10 <
    $35 outer ceiling): re-launch with
    `--arms B0,B1,B2 --rungs R1,R2` (or `--rungs R1,R2` for both tiers in
    one run) after recording the authorization.
11. **Grade:** `python3 analysis/rules_2.py --run-records … --results … --c8
    poc/rules-2/results/c8-result.json --rules1-primary-lb <rules-1 primary
    LB95>` → verdict-gen with the record's `verdict_rules`; then the
    cross-vendor audit. Runner never grades; this build never runs.
