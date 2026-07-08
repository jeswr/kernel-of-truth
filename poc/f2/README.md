# poc/f2 — F2 verifier-offload harness (the Tier-1 pivot experiment)

**Status:** harness built + MOCK-VALIDATED, 2026-07-08. **No real run has happened; no GPU
dollar has been spent.** The frozen pre-registration is `registry/experiments/f2.json`
(FROZEN, sha `28874f2b…`) + ops amendments 1–2; GNG-0 is signed and the design is
**immutable** — this harness implements it, it may not reinterpret it.
**Hypotheses:** HE1 (verifier-offload buys parameters, the primary), HE2 (verifier-gated
cascade), HC3 (kernel verifier vs trained PRM), HS12 (retry vs in-decode placement rider).
**Design record:** P1 §3 (`docs/research-plan/01-hypotheses-experiments.md`),
efficiency track §4.2 (`docs/design-efficiency-track.md`), interface P10
(`docs/research-plan/10-model-record-interface.md`).

## Layout

| Path | What |
|---|---|
| `inputs/f2-manifest.json` | hash-pinned RunSpec: d-qa file pins, model revision pins (R1/R2 pinned, R3/PRM `null` → fail closed), frozen design constants (verbatim copy), arm plan, F0 accounting constants, mock spec |
| `runner/f2_runner.py` | the ONLY thing the GPU runs — all 13 frozen arms, F0 flop-meter, P10 IF-C extraction + instrument gate, raw-metrics emitter; `--mock` and `--dry-plan` are $0 stdlib paths |
| `smoke/check_mock.py` | end-to-end mock validation against the FROZEN contracts (arm set, raw-metrics lint, pinned `analysis/f2.py` field resolution, gate flip both directions, dry-plan caps) |
| `../modal/modal_f2.py` | Modal wrapper (modal_e9 pattern): stages runner+inputs+`data/{d-qa,kernel-v0,molecules-v0}`, asserts the staged manifest in-container, sidecar-only provenance, results to `results-incoming/` |

## The arms (frozen IV levels — names must match `analysis/f2.py` byte-for-byte)

1. `model-alone` @ R1/R2/R3 — SmolLM2-Instruct 135M/360M/1.7B baselines.
2. `kernel-verify-retry` @ R1,R2 × k∈{1,2,4} — **the kernel arm**: IF-C constrained answer →
   checkable record → deterministic check against the canonical record bytes (per-item
   `record_sha256` pin, fail closed) → reject → resample, final = last attempt (pre-declared).
3. `kernel-as-text` — Law-2 passive text null (pinned gloss in context).
4. `rag-over-text` — deterministic BM25 (pinned `rag-index.json`) top-3 context.
5. `self-consistency-flop-matched` — N=5 majority vote (FLOP envelope of k=4; ledger decides).
6. `gloss-self-verify-retry` — P7 RT-2 arm 10, the strongest ACTIVE text baseline: the model
   checks its own answer against the pinned gloss TEXT, identical retry sweep. **HE1 cannot
   PASS without beating this arm.**
7. `prm-verifier` — HC3: small trained reward model re-ranks best-of-2 (model unpinned — gate).
8. `int4-quantized` — int4 360M practitioner null.
9–12. `cascade-{verifier,logprob,text-self-check,in-decode}-gated-135m-1p7b` × budgets
   {0.1, 0.25, 0.5} — HE2 dominance set + the HS12 placement rider (latency both modes).
13. `extraction-instrument` — P10 gate measurement (n≥300 labelled outputs/rung; Wilson-LB
   failure >10% ⇒ INSTRUMENT-INVALID; failures are instrument events, never free wins/losses).

**Shared affordance (P10 §5):** every arm answers through the same constrained surface
(sequence-logprob selection over the pinned option set); arms differ only in context block and
verification instrument.

## Metric-emitter contract (what `analysis/f2.py` consumes)

One kot-log/1 record BODY per cell in `run-records-f2*.jsonl` (log-append.py stamps
seq/chain/ts/runner at commit time):

```
config.arm / config.rung / config.retry_budget / config.escalation_budget / config.seed
metrics.item_correct                 [0/1 × items, pinned order]   (all arms but iface)
metrics.item_correct_external        [0/1 …]                       (when d-ext exists)
metrics.item_correct_control        [0/1 …]  descriptive off-coverage raw
metrics.metric_vector.params.{n_total,n_active,n_trained}
metrics.metric_vector.memory.{weights_bytes,store_bytes,process_peak_rss_bytes,cuda_peak_bytes,peak_bytes_total}
metrics.metric_vector.inference_compute.{flops_per_query,model_flops_per_query,
    verifier_cpu_s_per_query,verifier_flops_per_query_at_pinned_rate,
    tokens_prefill_per_query,tokens_decode_per_query,latency_ms_p50,latency_ms_p95,usd_per_query}
metrics.metric_vector.training_compute.{flops,steps,tokens}        (0 — inference-only)
extraction-instrument cells instead: metrics.{n_labelled,n_extraction_failures,n_extraction_errors}
```

RAW only — no p-values, effect sizes, CIs, Holm/TOST anywhere (P2 §2.4 lint enforced in the
smoke test). Verdicts are computed downstream by the pinned `analysis/f2.py`
(sha `068f68b8…`) + `tools/registry/verdict-gen.py` under run-vs-audit separation.

## Validate for $0 (this box, CPU, ~10 s)

```bash
python3 poc/f2/smoke/check_mock.py     # all 13 arms + emitter + P10 gate + analysis contract
python3 poc/f2/runner/f2_runner.py --out-dir /tmp/f2 --dry-plan   # cost plan vs caps
```

Mock mode uses a SYNTHETIC deterministic stub LM (per-rung skill planted so the analysis
gap denominators resolve — the same trick as `analysis/f2.py --selftest`); the verifier,
extraction, gating, flop-meter and emitter code paths are the REAL ones. Every mock output is
labelled MOCK and is never a measurement.

## Cost plan (from `--dry-plan`, A10G, 2026-07-08)

99 cells, ~3.5 GPU-h point estimate → **~$3.9 point / ~$7.7 worst-case (2× overhead) /
$26.40 hard ceiling** (24 GPU-h registry cap × $1.10/h Modal list). All inside the frozen
caps: usd_cap $60, Tier-1 cap $80. T4 flavour: hard ceiling $14.16.

## Launch gates — the real run may NOT start until ALL hold

1. **d-xif** built + pinned (≥300 labelled model outputs per rung, P10 §4) — runner fails
   closed (`ERR_MISSING_DXIF`).
2. **d-ext** built + pinned (RT-7a external slice; M0b-filtered WiC → OpenBookQA → MMLU) —
   without it the frozen external-slice secondary is unresolvable and verdict-gen fails closed.
3. **R3 + PRM revisions** pinned by ops amendment (currently `null` → `ERR_UNPINNED_MODEL`).
4. **harness_manifest** ops amendment written from `modal_f2.py`'s printed staged manifest.
5. **Maintainer Tier-1 go** (P1 §5).

## Still to build (tracked, not in this drop)

- The real-path PRM backend (blocked on the PRM model pin; `ERR_PRM_TODO` fail-closed stub).
- d-xif / d-ext corpus builders (separate deterministic builders, d-qa discipline).
- Promotion of the F0 flop-meter from `runner/f2_runner.py` into the shared `poc/f0/` package
  (F2 carries its own F0-§3.3-conformant implementation until then).
- IF-1 fork pilot (n=200 constrained-format-tax measurement) before the final phase.
