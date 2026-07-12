# poc/pubeval — public-benchmark evaluation harness (SmolLM2 HFLM)

**Status:** exploratory infrastructure (built 2026-07-12). NOT a frozen
experiment — no registry record, no `assumptions.jsonl` writes; ASM rows below
are PROPOSED only (PROPOSED-ASM-1610..1629 block). Serves BOTH the
dimension-collapse compression experiment (weight-variant comparator arms) and
the 2026-07-12 maintainer directive *"use existing human-built benchmarks"*
(docs/next/analysis/existing-benchmarks-survey.md).

## Benchmarks wired (survey §4 top picks — HUMAN gold only, no LLM-PROXY)

| Benchmark | Split (eval / few-shot) | n | Task / scoring | License | Gold provenance |
|---|---|---|---|---|---|
| **FOLIO** | validation / train | 203 | 3-way forced choice (True/False/Uncertain), loglikelihood | MIT [search 2026-07-12] | HUMAN-AUTHORED |
| **ARC-Easy** | test / train | 2,376 | 4-way MC, loglikelihood (acc + acc_norm) | CC BY-SA 4.0 [search 2026-07-12] | HUMAN-SOURCED (EXAM) |
| **ARC-Challenge** | test / train | 1,172 | 4-way MC, loglikelihood (acc + acc_norm) | CC BY-SA 4.0 [search 2026-07-12] | HUMAN-SOURCED (EXAM) |
| **GSM8K** | test / train | 1,319 | greedy generation, exact match on final number (`#### N`) | MIT [search 2026-07-12] | HUMAN-AUTHORED |

Survey adoption #2 is the EntailmentBank+ARC *package*; EB is a
store-projection/attribution instrument, not a plain LM benchmark surface, so
only its ARC end-task carrier is wired here (EB projection stays with the
f2b-transfer lineage). Re-verify every license at source before any frozen
use (survey riders, PROPOSED-ASM-1590..1596).

**Metrics:** per-benchmark `acc` (sum-logprob argmax), `acc_norm`
(choice-string-length normalised — the actual lm-eval multiple_choice
convention; fixed 2026-07-12 from an incompatible per-token normalisation,
cross-vendor review finding #2), gold-continuation perplexity
(`gold_ppl`); GSM8K `exact_match` + gold-solution perplexity; aggregate =
unweighted macro-average of headlines (acc_norm for MC, EM for gen).
Loglikelihood tokenisation is JOINT context+continuation (lm-eval
`_encode_pair`; fixed 2026-07-12 from separate-encode-and-concatenate,
review finding #1 — regression: `test_boundary_regression.py`). NOTE:
PROPOSED-ASM-1615's wording ("per-token normalised") predates these fixes
and needs updating before that row is ever actually proposed.
**Comparability:** numbers are internal-relative (fixed prompts/shots/seed
20260712) — NOT leaderboard-comparable; the designed use is
baseline-vs-weight-variant deltas.

## Why not lm-evaluation-harness

The pinned Modal image (`poc/modal/requirements-image.txt`, sha `0fac7243…`,
the same image as the FROZEN f2b/deconf-b/rules-1 runs) contains only
numpy/torch/transformers/bitsandbytes/accelerate. `lm-eval` would add a new
dependency tree (datasets/pyarrow/…) — an image change barred by the
image-reuse discipline (PROPOSED-ASM-1106 lineage). The scorer here is
therefore self-contained: the forced-choice logprob math is the f2bt
`HFLM._option_logprobs` pattern (poc/f2b-transfer/runner/f2bt_runner.py)
generalised to (context, continuation), plus a small greedy exact-match path
for GSM8K.

## The weight-transform hook (dimcollapse seam)

```
fn(model, **kwargs) -> model | None     # None = modified in place
```

Applied ONCE after model load, BEFORE any scoring. Prompts, few-shot
exemplars, seeds and scoring code are identical across variants, so metric
deltas are attributable to the weight change alone. Before/after param counts
+ a weight fingerprint (sha over per-tensor name/shape/sum/abs-sum) are
recorded in the results JSON. Two entry points:

- **CLI:** `--transform path/to/file.py:func --transform-kwargs '{"fraction":0.5}'`
- **Programmatic:** `HFLM.from_model(model, tokenizer, name)` — wrap an
  already-modified model object and call `evaluate(...)`.

Reference transforms in `transforms.py`: `identity` (baseline),
`magnitude_prune` (fraction, per-tensor), `random_drop` (seeded control). The
kernel-normalised-dropped transform lives with the dimcollapse experiment and
plugs in through the same contract.

## Run commands

```bash
# 1. mock validation — CPU, stdlib only, $0, no network (StubLM + fixtures;
#    SYNTHETIC mechanics-only, never a measurement)
python3 poc/pubeval/pubeval_runner.py --mock
python3 poc/pubeval/pubeval_runner.py --mock --n 4 \
    --transform poc/pubeval/transforms.py:identity   # hook plumbing check

# 2. fetch + sha-pin data (pin-on-first-fetch; later drift fails closed)
python3 poc/pubeval/fetch_data.py            # FOLIO/ARC via HF datasets-server
python3 poc/pubeval/fetch_data.py --verify   # offline pin check

# 3. Modal (a10g; inference only). ALWAYS dry-plan + mock first.
python3 poc/pubeval/modal/modal_pubeval.py --print-manifest        # $0
.venv/bin/modal run poc/pubeval/modal/modal_pubeval.py --dry-plan  # $0
.venv/bin/modal run poc/pubeval/modal/modal_pubeval.py --mock      # pennies
.venv/bin/modal run poc/pubeval/modal/modal_pubeval.py --model smollm2-135m
.venv/bin/modal run poc/pubeval/modal/modal_pubeval.py --model smollm2-1.7b \
    --transform /root/kot/poc/pubeval/transforms.py:magnitude_prune \
    --transform-kwargs '{"fraction":0.5}'
```

Results: local runs → `poc/pubeval/results/`; Modal runs →
`poc/pubeval/results-incoming/<stamp>-modal/` with the standard sidecars
(provenance-modal.json, run log, RUNNER_EXIT) — never auto-committed. Modal
hygiene: `modal app stop ap-<id>` after killing any attached client (bd
memory, E5 lesson).

## Cost estimate (A10G ≈ $1.10/h; conservative batch-1; `--dry-plan` recomputes)

| Model (pinned revision) | Full suite est. | Est. $ |
|---|---|---|
| smollm2-135m `12fd25f7` | ~2.4 GPU-h | ~$2.6 |
| smollm2-360m `a10cc151` | ~3.8 GPU-h | ~$4.2 |
| smollm2-1.7b `31b70e2e` | ~6.4 GPU-h | ~$7.0 |

GSM8K generation dominates (~60–75%); drop it or `--n 500` for cheap passes.
Proposed worst-case cap **$10/run** — `--dry-plan` fails closed above it.
Revision provenance: R1/R3 verbatim from `poc/rules-1/inputs/rules1-manifest.json`
(FROZEN f2b-replicate/f2b-transfer chain); 360M from `poc/f2/inputs/f2-manifest.json`
(amendment 2-pin-model-revisions-r1-r2).

## Mock validation record (2026-07-12, this box, CPU, $0)

Full-fixture mock (n=8/benchmark, 5-shot, seed 20260712), AFTER the
2026-07-12 review fixes (joint encoding + choice-length acc_norm):
macro_acc 0.75 (folio .625, arc_easy .875, arc_challenge 1.0, gsm8k .50) —
SYNTHETIC stub outputs, mechanics-only; the shift from the pre-fix 0.78125
is the FOLIO acc_norm convention change, as expected. Re-running is
byte-deterministic modulo timestamps. Boundary-drift regression:
`python3 poc/pubeval/test_boundary_regression.py` (part A stdlib-only; parts
B/C run in-container before every Modal eval, fail closed).
Transform-hook plumbing validated via `identity` (before/after fingerprint
recorded, `changed_weights: false`). Wrapper `--print-manifest` and
`--dry-plan` validated at $0.

## Proposed ASM rows (PROPOSED-ASM-1610..1629 block; nothing written to registry)

```json
[
 {"id":"PROPOSED-ASM-1610","tag":"STIPULATED","claim":"poc/pubeval is shared exploratory eval infrastructure: a self-contained few-shot loglikelihood + greedy exact-match scorer over openly-licensed human-built benchmarks, chosen over lm-evaluation-harness because the pinned Modal image (requirements-image.txt sha 0fac7243) carries no lm-eval dependency tree and image-reuse discipline (PROPOSED-ASM-1106 lineage) bars image changes; the forced-choice math is the f2bt HFLM._option_logprobs pattern.","backing_ref":"poc/pubeval/pubeval_runner.py; poc/modal/requirements-image.txt","rationale":"Keeps the FROZEN-run image byte-stable while satisfying the human-built-benchmarks directive.","load_bearing":true,"status":"open","owner":"fable-infra","date":"2026-07-12"},
 {"id":"PROPOSED-ASM-1611","tag":"STIPULATED","claim":"Adopted pubeval benchmark set = survey top picks: FOLIO (MIT, HUMAN-AUTHORED, 203 validation), ARC-Easy/Challenge (CC BY-SA 4.0, HUMAN-SOURCED exam, 2376/1172 test), GSM8K (MIT, HUMAN-AUTHORED, 1319 test). EntailmentBank (survey adoption #2 package) is deferred: it is a store-projection instrument, not an LM benchmark surface; its ARC carrier IS wired. No LLM-PROXY gold anywhere (PROPOSED-ASM-1590 taxonomy).","backing_ref":"docs/next/analysis/existing-benchmarks-survey.md sec 4; poc/pubeval/benchmarks.py","rationale":"Implements the top openly-licensed human-gold recommendations verbatim.","load_bearing":true,"status":"open","owner":"fable-infra","date":"2026-07-12"},
 {"id":"PROPOSED-ASM-1612","tag":"STIPULATED","claim":"pubeval weight-transform hook contract: callable(model, **kwargs) -> model|None applied once after load and before any scoring; prompts, few-shot exemplars, seeds and scoring code are identical across variants; before/after parameter counts + weight fingerprints are recorded. This is the dimension-collapse comparability guarantee: baseline / kernel-normalised-dropped / magnitude-pruned / random-dropped variants are evaluated by byte-identical harness paths.","backing_ref":"poc/pubeval/pubeval_runner.py apply_transform; poc/pubeval/transforms.py","rationale":"Makes weight-variant metric deltas attributable to the weight change alone.","load_bearing":true,"status":"open","owner":"fable-infra","date":"2026-07-12"},
 {"id":"PROPOSED-ASM-1613","tag":"STIPULATED","claim":"pubeval model pins reuse the FROZEN carriers verbatim: SmolLM2-135M-Instruct 12fd25f7 and 1.7B-Instruct 31b70e2e from the f2b-replicate/f2b-transfer chain (via rules1-manifest), 360M-Instruct a10cc151 from the f2 amendment; unpinned loads fail closed (ERR_UNPINNED_MODEL) except explicit --model-path local checkpoints, which are recorded as local: names.","backing_ref":"poc/rules-1/inputs/rules1-manifest.json; poc/f2/inputs/f2-manifest.json; poc/pubeval/pubeval_runner.py MODEL_REGISTRY","rationale":"One provenance chain for every model byte the harness can load.","load_bearing":false,"status":"open","owner":"fable-infra","date":"2026-07-12"},
 {"id":"PROPOSED-ASM-1614","tag":"STIPULATED","claim":"pubeval data provenance is pin-on-first-fetch: FOLIO/ARC rows via the HF datasets-server JSON API (avoids the pyarrow dependency the pinned image lacks), GSM8K via openai/grade-school-math raw JSONL; sha256 + row counts pinned in data/manifest.json with row-count floors; any later drift fails closed (ERR_DATA_DRIFT). All [search 2026-07-12] license tags must be re-verified at source before any frozen use.","backing_ref":"poc/pubeval/fetch_data.py; poc/pubeval/data/manifest.json (on first fetch)","rationale":"nsk1 corpus-build discipline applied to third-party benchmark bytes.","load_bearing":false,"status":"open","owner":"fable-infra","date":"2026-07-12"},
 {"id":"PROPOSED-ASM-1615","tag":"STIPULATED","claim":"pubeval scoring conventions: MC acc (sum logprob) + acc_norm (per-token normalised) + gold-continuation perplexity; GSM8K greedy decode + final-number exact match + gold-solution perplexity; aggregate = unweighted macro-average of headlines (acc_norm/EM). Numbers are INTERNAL-RELATIVE under fixed prompts/shots/seed 20260712 and are not leaderboard-comparable; the designed use is baseline-vs-transformed deltas.","backing_ref":"poc/pubeval/pubeval_runner.py eval_mc/eval_gen","rationale":"Prevents over-read of absolute numbers against published harnesses with different conventions.","load_bearing":true,"status":"open","owner":"fable-infra","date":"2026-07-12"},
 {"id":"PROPOSED-ASM-1616","tag":"STIPULATED","claim":"pubeval --mock is SYNTHETIC mechanics-only (StubLM deterministic sha outputs over embedded fixtures shaped exactly like the released schemas); it validates plumbing, schema normalisers, the transform hook and result emission, and is never a measurement. Mock 2026-07-12 record: macro_acc 0.78125 over 4x8 fixture items, byte-deterministic modulo timestamps.","backing_ref":"poc/pubeval/pubeval_runner.py StubLM; poc/pubeval/results/results-pubeval-mock.json","rationale":"f2bt StubLM discipline carried over.","load_bearing":false,"status":"open","owner":"fable-infra","date":"2026-07-12"},
 {"id":"PROPOSED-ASM-1617","tag":"STIPULATED","claim":"pubeval cost envelope (inference only, A10G $1.10/h, conservative batch-1): full suite approx $2.6 (135M) / $4.2 (360M) / $7.0 (1.7B); GSM8K generation dominates; worst-case cap $10/run enforced fail-closed by --dry-plan (ERR_COST_CAP).","backing_ref":"poc/pubeval/modal/modal_pubeval.py _dry_plan","rationale":"LOW-cost posture stated before any GPU spend, per standing ops discipline.","load_bearing":false,"status":"open","owner":"fable-infra","date":"2026-07-12"},
 {"id":"PROPOSED-ASM-1618","tag":"STIPULATED","claim":"pubeval results are exploratory: no headline correctness/efficiency claim may rest on a pubeval run until a kot-reg/1 pre-registration freezes the exact benchmark set, splits, shots, seed, model pins, transform specs and analysis; CORRECTNESS and EFFICIENCY remain INCONCLUSIVE-PENDING (ASM-1380 lineage) regardless of pubeval outputs.","backing_ref":"poc/pubeval/README.md","rationale":"Infrastructure build must not smuggle in unregistered evidence.","load_bearing":true,"status":"open","owner":"fable-infra","date":"2026-07-12"},
 {"id":"PROPOSED-ASM-1619","tag":"STIPULATED","claim":"The pubeval Modal wrapper follows the modal_rules1 transport contract: staged-bytes manifest asserted in-container (ERR_STAGING_MISMATCH), runner outputs shipped as opaque bytes, sidecar-only provenance, hf-cache volume reuse, results never auto-committed; but as exploratory infrastructure it has no frozen record and its printed manifest sha is recorded for reproducibility only, not as a pins amendment.","backing_ref":"poc/pubeval/modal/modal_pubeval.py; poc/modal/modal_common.py","rationale":"Same fail-closed transport, honestly not dressed as a frozen experiment.","load_bearing":false,"status":"open","owner":"fable-infra","date":"2026-07-12"}
]
```

*(PROPOSED-ASM-1620..1629 unused; block reserved per instruction.)*

## Files

```
pubeval_runner.py     harness: HFLM loader (+ from_model), StubLM mock,
                      transform hook, eval core, results JSON
benchmarks.py         adapters + normalisers + few-shot frames + mock fixtures
transforms.py         identity / magnitude_prune / random_drop reference hooks
fetch_data.py         fetch + sha-pin data (stdlib urllib; pin-on-first-fetch)
modal/modal_pubeval.py  a10g wrapper (modal_rules1 pattern; T4|A10G)
data/                 fetched benchmark bytes (gitignored; re-fetchable)
results/              local run outputs (mock result committed as validation record)
```
