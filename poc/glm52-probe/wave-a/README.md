# GLM-5.2 Wave-A expert profiling (Stage 2)

Stage-2 of the expert-profiling plan
(`docs/next/design/glm52-expert-profiling-plan-sol-20260715.md`): enumerate every
stored routed expert and profile its per-item/per-token router activation over a
480-item labelled, teacher-forced corpus, then build the expert atlas. Runs on the
GO-FULL-GLM52 backend proven by the smoke (`../smoke/`, acct4/OCI, RAM-capped).

**EXPLORATORY infra** — rigor relaxed vs a frozen experiment. Routing-affinity
evidence only (evidence_level 0): this maps what routes WHERE, not what an expert
DOES. Functional/causal labels require Stage 3.

## Layout

- `corpus/build_corpus.py` — deterministic generator → `corpus/wave_a_corpus.json`
  (480 items) + `corpus/corpus_manifest.json` (label vocab, family/split map).
  12 macrodomains × 4 template_families × 5 fills × (base + 1 controlled
  counterpart) = 480. `prompt_family` (240, macro.sub.fill) is the
  gate/bootstrap/split unit; `template_family` (48) is a reporting label. Split per
  fill: 3 discovery / 1 dev / 1 held_out, so every domain+template_family is in
  every split.
- `wave_driver.py` — in-container: tokenises the corpus, runs ONE traced glm
  invocation over all 480 items (per-item reset, DRAFT=0), checks integrity
  (`../smoke/trace_analyze.py`), aggregates (`atlas_agg.py`).
- `atlas_agg.py` — one-pass streaming aggregation of the kot-rtrace/1 trace into
  per-expert-cell sufficient statistics (runs in-container AND locally).
- `build_atlas.py` — local: enrichment, family-bootstrap CIs, coverage gates,
  honest labels → `atlas/expert_atlas.parquet` + `expert_atlas_index.json` +
  `atlas_summary.md` + `coverage_gates.json`.
- `selftest.py` — `$0` synthetic-trace validation of the local pipeline (injected
  specialists must be recovered; label branches exercised).
- `../../modal/modal_glm52_wave.py` — Modal wrapper (`wave_a` full / `wave_a_tiny`
  dry-run / `plan`). Outputs go to the named Volume `kot-glm52-wave-a-out`.
- `collect_and_build.sh` — pull the run outputs off the Volume + build the atlas.

## Reproduce

```bash
python3 corpus/build_corpus.py                 # $0, deterministic
python3 selftest.py                            # $0, validates local pipeline
# ~$0 plumbing dry-run on the tiny oracle over all 480 items:
COLIBRI_GIT_URL=https://github.com/JustVugg/colibri.git \
  poc/modal/.venv/bin/modal run poc/modal/modal_glm52_wave.py::tiny
# the Wave-A run (~2.2 h / ~$2.51, $25 stop-loss), client attached:
COLIBRI_GIT_URL=https://github.com/JustVugg/colibri.git \
  poc/modal/.venv/bin/modal run poc/modal/modal_glm52_wave.py::main
bash collect_and_build.sh full                 # download + build atlas ($0)
```

## Coverage gates (Stage-2 decision gate)

trace invariants 100% · ≥95% routing mass on experts with ≥100 events · stable
label = ≥100 events across ≥20 prompt families · discovery-vs-held-out layer
Spearman ≥0.8. Cells below the bar are marked rare/unresolved/unseen honestly —
"enumerate all" must not become "invent a speciality for all".
