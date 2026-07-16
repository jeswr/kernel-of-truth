# GLM-5.2 expert-profiling — Stage 3 (causal characterisation)

EXPLORATORY infra (rigor relaxed vs a frozen experiment). Turns the Stage-2
routing-affinity atlas into **causal** evidence: for a stratified ~32-expert
shortlist, exact contribution-ablation + route-around (+ module-swap on the
format/copy/arith leads) measured at the FINAL logits, to validate a first
**safe-to-drop / substitute skip-list** for colibri's `EXPERT_BUDGET`.

Spec: `docs/next/design/glm52-expert-profiling-plan-sol-20260715.md` §Stage-3.
Builds on the GO-FULL-GLM52 backend (`poc/glm52-probe/smoke/…`, OCI/RAM-capped)
and the Stage-2 atlas (`poc/glm52-probe/wave-a/atlas/…`).

## Artefacts

| file | what |
|---|---|
| `abl.h` | self-contained per-item ablation config (mode 0 off · 1 contribution-zero · 2 route-around · 3 module-swap); inert unless `g_abl.mode` set → byte-identical to the rtrace build |
| `ablation-add-path.patch` | `glm.c`+`Makefile`: `moe()` hooks (route-around/module-swap in FASE A; contribution skip in FASE C) + `run_ablate_score()` (`ABLATE_SCORE=<manifest>`, per-target-position final-logit read-out to `ABLATE_OUT=<file>`) + main dispatch. Applies **after** `rtrace-add-path.patch`. |
| `test_ablate.c` | `$0` unit test (18 checks): baseline==unpatched, ablating-an-unused-cell is a no-op, per-item reset, and each arm's semantics. Fail-closed at image build. |
| `stage3_select.py` | `$0` local: picks the ~32-expert stratified shortlist + activation-max/off-domain item pool from the Stage-2 atlas → `corpus/stage3_shortlist.json`, `corpus/stage3_corpus.json` |
| `stage3_driver.py` | in-container: tokenise → build the `ABLATE_SCORE` manifest (baseline + contrib + route + swap) → run `glm` → join baseline↔ablated into paired deltas (target-NLL, gold-logit margin, top-K KL, exact correctness) |
| `stage3_analyze.py` | pure function of the deltas: per-expert causal summaries, evidence-agreement causal confidence, SAFE-TO-DROP/LOAD-BEARING/DETERMINISTIC-REPLACEABLE classification, candidate skip-list. Re-runnable locally. |
| `../../modal/modal_glm52_stage3.py` | Modal entrypoints (`plan`/`tiny`/`stage3`) on the proven OCI/RAM-capped config; periodic partial-checkpoint to the output Volume |

## Manifest / trace schemas

`ABLATE_SCORE` manifest line: `item T n_prompt mode ncells (L E A){ncells} tok...`
(mode 0/1/2/3; A = module-swap target expert, −1 otherwise).
`ABLATE_OUT` (`kot-ablate/1`): per target position `{item,pos,gold,nll,glogit,molo,
mgn,am,amlogit,logZ,corr,tk:[[id,logit]×32]}`; plus per-item `ah` header echoing the
ablation cells. NLL/margin/correctness are exact; top-K KL is an approximation.

## Run

```bash
set -a; source ~/.config/kot/modal3.env; set +a          # acct3/acct4 (non-capped)
export COLIBRI_GIT_URL="https://github.com/JustVugg/colibri"
M=poc/modal/.venv/bin/modal
$M run poc/modal/modal_glm52_stage3.py::plan     # $0 config + cost projection
$M run poc/modal/modal_glm52_stage3.py::tiny     # ~$0 real-model inertness proof
$M run poc/modal/modal_glm52_stage3.py           # the run (~$10–18, 22h/$55 wall stop-loss, $60 hard cap)
```

## Collect + re-analyse locally

```bash
$M volume get kot-glm52-stage3-out full <dest>            # ablate_out.jsonl.gz, deltas, analysis, shortlist
# recompute classification/skip-list from the raw deltas (thresholds are in stage3_analyze.py):
python3 poc/glm52-probe/stage3/stage3_analyze.py \
  --deltas <dest>/stage3_deltas.json \
  --shortlist <dest>/stage3_shortlist.json --out <dest>/stage3_analysis.json
```

Classification thresholds are **STIPULATED** (documented in `stage3_analyze.py::TH`),
not measured; route-around target-NLL is the primary drop proxy, contribution-ablation
the upper bound. See `stage3_summary.md` for the run's headline + honest scoping.
