# a5-llm — Opus run-log (PHASE 1: runner/wrapper BUILD + operational pin-fill + $0 validation; BOUNDARY-STOP at freeze)

- UTC stamp: `20260709T220646Z` (`date -u +%Y%m%dT%H%M%SZ`)
- Executor: Opus (`claude-opus-4-8`), agent pseudonym `runner-1`
- Role: experiment-runner (Opus EXECUTION; `.claude/agents/experiment-runner.md`).
  Scope: PHASE 1 only — BUILD the a5-llm Modal runner/wrapper (adapting the f2b
  harness), fill the record's operational input-completion pins, and run the
  $0 pre-spend validation. **No GPU spent. No frozen record produced. No score,
  no verdict, no interpretation** (all deferred; see BOUNDARY-STOP below).
- Bead: `kernel-of-truth-lbv` (a5-llm; maintainer sign-off 2026-07-09 for the
  spending experiment through the normal rails).

## BOUNDARY-STOP (binding; the reason there is no freeze and no GPU run)

The FROZEN-DESIGN record `registry/experiments/a5-llm.json` (authored by Fable,
DRAFT) **cannot pass `prereg-freeze`**: it declares `efficiency_relevant: true`
but its `design.dependent_vars` do not include the five metric-vector-V DV names
(`accuracy`, `params`, `memory`, `inference_compute`, `training_compute`) that
constraint 5 (`ERR_P2_MISSING_METRIC_VECTOR`, directives §2 full-V rule) requires
whenever `efficiency_relevant` is set. The sibling efficiency record
`f2b-replicate` carries exactly those five DV entries; a5-llm does not.

- Mechanical proof: `poc/a5-llm/opus-runs/20260709T220646Z/freeze-dryrun.log`
  (`prereg-freeze --dry-run` → `ERR_P2_MISSING_METRIC_VECTOR`, the ONLY failing
  check; with the five V DVs hypothetically added, ALL other freeze checks pass —
  corpus pins reproduce, reuse-override collision resolved, metric pointers,
  artifact-hash pins, endpoints, kill/envelope, powered gates).
- This is a DESIGN fix (the metric vector V definitions for THIS experiment =
  directives §2, definitional), which is **Fable's** jurisdiction, NOT Opus
  execution (`experiment-runner.md`: "If a task needs [design] and it is not
  ALREADY frozen by Fable, you STOP and queue it for Fable"). Opus does not
  improvise `dependent_vars`. Queued: bead for Fable (add the five V DV entries,
  mirroring f2b-replicate, then re-run `prereg-freeze`).
- Consequence: steps 2b–5 of the execution plan (freeze, GPU run, score,
  verdict-gen, Codex audit) are BLOCKED on the Fable fix. Everything Opus owns
  that does NOT require the freeze is DONE here so that the moment the five V
  DVs land, freeze + run proceed with zero further Opus design work.

## What was BUILT this phase (Opus operational work; committed)

The a5-llm GPU runner + Modal wrapper, adapting the f2b harness
(`poc/modal/modal_f2b.py` + `poc/f2b/runner/f2b_runner.py`) to free-form greedy
GENERATION over the pinned SmolLM2-Instruct ladder (f2b uses forced-choice
logprob; a5-llm needs the model to EMIT the JSON answer the instrument scores):

- `poc/a5-llm/runner/a5_llm_runner.py` — the ONLY GPU code. Loads each pinned
  revision once (R1→{direct,rag}, R2→…, R3→…), greedy-decodes
  (`do_sample=false, temperature 0, max_new_tokens 512, context 8192`, chat
  template as shipped), emits the six cells' `a5-llm-raw/1` files (header
  `arm/rung/model_revision/pack_sha256/decode_pins/gpu_class/batch_size/gpu_wall_seconds`;
  977 rows `qid/output_text/latency_ms/truncated/tokens_prompt/tokens_decode`).
  Carries the f2b safety discipline: per-cell wall-clock CellGuard
  (`ERR_CELL_TIMEOUT`) + a whole-run GPU-hours guard (`ERR_RUN_GPU_BUDGET`) +
  flush-per-batch (partials always on disk). Implements the pinned TRUNCATION
  rule (design §3.3) verbatim — drop record lines from the TAIL of the final
  user turn's CONTEXT block until `tok(prompt)+512 ≤ 8192` (truncation DOES fire:
  max prompt 32335 chars ≈ 8.7k tokens; the ~1-5 truncations are disclosed).
  `--mock` (stub LM, CPU, $0) and `--dry-plan` (stdlib, $0) spend nothing.
- `poc/modal/modal_a5_llm.py` — the Modal wrapper (f2b staging pattern): stages
  the runner+requirements+image-reqs+pack+manifest, asserts the staged-bytes
  manifest in-container (`ERR_STAGING_MISMATCH`), runs the runner over the six
  cells, ships the raw files back as opaque bytes with sidecar provenance.
  Local `--print-manifest` computes `pins.harness_manifest` without a Modal
  connection; `--dry-plan` runs the runner's $0 plan.
- `poc/a5-llm/inputs/a5-llm-pack.jsonl` — the deterministic prompt pack, emitted
  by `a5_llm_instrument.py --emit-prompts` (digest
  `4118269166883f7de7c84e03991870000f02781d1ff8e1587bc2e79ab43e2141`; 1954
  prompts; completeness-lint 0 violations → FK-A5L-2 = option (a)).
- `poc/a5-llm/inputs/a5-llm-manifest.json` — planning constants (dry-plan
  ESTIMATES, STIPULATED), budget caps, model/decode pins, `pack_sha256`.
- `poc/a5-llm/runner/requirements.txt` — torch/transformers floors (image pins
  the exact versions).

The CPU arms (engine/abstain-all/answer-all) are NOT run by the GPU runner; they
are the instrument's own $0 CPU cells (`--arm …`, reuse_overrides fresh re-run).

## Operational pins FILLED in the DRAFT record (Opus input-completion; committed)

`registry/experiments/a5-llm.json` (status stays DRAFT; NO design field touched):

- `pins.analysis_script.sha256` = `8f7aa8807b2bdda7dedd12910bc3b17552d425ee9f94123f0027cd5fa7966bc4`
  (== `sha256(analysis/a5_llm.py)`)
- `pins.artifact_hashes.a5-llm-prompt-pack` = `4118269166883f7de7c84e03991870000f02781d1ff8e1587bc2e79ab43e2141`
  (pack digest)
- `pins.artifact_hashes.a5_llm_instrument.py` = `94c5403faa05f5cab7216d99dc77afd4fde7c84ebe27a4fb1153e9ecc319772d`
  (== `sha256(tools/experiments/a5_llm_instrument.py)`)
- `pins.harness_manifest` = `f58874fa1c2f7cd81043b0ff50e423a46a3c71297656d657c845f0516419955f`
  (staged-bytes manifest sha printed by `modal_a5_llm.py --print-manifest`;
  f2b-replicate convention: launch reprints it, in-container check fails closed)

## $0 VALIDATION (mechanical; NOT a measurement)

- **runner --mock → instrument --score → analysis** (full transport + contract):
  the runner emitted six valid `a5-llm-raw/1` files (977 rows each, one exercised
  the truncation path); the pinned instrument `--score` ACCEPTED them
  (pack_sha256 / model_revision / decode_pins header checks all passed) and the
  pinned analysis resolved every field. (instrument_valid=False / best_llm=None
  are EXPECTED for random stub outputs — the mock validates the CONTRACT, never a
  measurement.) `engine_matches_a5=1`, `retrieval_completeness_violations=0`.
- **a5_llm_smoke.py** (`$0` freeze-validation smoke): ALL CHECKS PASSED — pack
  deterministic (411826…), completeness-lint 0, fresh engine pass reproduces
  `results-log/a5.jsonl` exactly (covered 855/855, control 122/122), all 35
  declared analysis output fields resolve, green mock verdictable, extraction
  gate flips to INVALID on garbage.
- **dry-plan (A10G)** (`dry-plan-a10g.log`): point est **2.29 GPU-h / $2.52**;
  worst-case (1.6× overhead) 3.67 GPU-h / $4.03 — all three checks OK vs
  usd_cap $25 / gpu_hours_cap 4 h / tier_cap $25. (A100 is the alternative flavour;
  chosen at launch. Design estimate was $3-8.)
- **reuse-check --gate** (`reuse-check-gate.log`): **exit 0** — 3 CPU cells
  (engine/abstain-all/answer-all @R0) covered by the record's `reuse_overrides`
  (deliberate fresh re-run, doubling as the engine-regression gate); 0 blocking;
  the 6 LLM cells are correctly unlogged/fresh.

## DEFERRED (NOT done here — blocked on the Fable freeze fix, or Fable-owned)

- FREEZE (`prereg-freeze --experiment a5-llm --agent-id runner-<n>`) → blocked on
  `ERR_P2_MISSING_METRIC_VECTOR` (Fable adds the five V DVs first).
- GPU run on Modal, instrument `--score`, `log-append` the 9 final-phase records,
  `verdict-gen`, Codex Gate-A audit, `audit-status` — all downstream of the freeze.
- Any interpretation of what a verdict would MEAN (Fable's, per the hard line).
