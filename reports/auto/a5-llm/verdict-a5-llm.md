# a5-llm verdict — PASS-PENDING-AUDIT

computed: 2026-07-09T23:06:52Z | report-gen/1 | analysis 8f7aa880
frozen prereg: 11c3dc4e (frozen 2026-07-09T22:33:25Z) | amendments applied: none
encoder pin: 40e8c8ba | corpus pins: a5-eval:3676d689, code-axioms-v0:dc930b4f, code-corpus-v0:1063ad50, code-v0:01009b1f, code-world-v0:b8a8a50a, kernel-v0:8209cada | log tail: 48f42584

## Pre-registered statement (from the frozen record)

**Hypotheses:** HA5-LLM (the a5 successor head-to-head; per the a5 freeze, the ONLY record class licensed to state an engine-vs-LLM claim on this slice): on the pinned 977-query kot-query-code/1 slice, the deterministic kot-axiom engine beats every pinned small-LLM arm ({llm-direct,llm-rag} x {SmolLM2 R1,R2,R3}) on conjunctive accuracy (covered-exact AND control-refusal, arm-appropriate scoring with all leniency pro-LLM) by > 0.10 absolute, at > 10^3 lower usd/query — converting the arXiv:2505.12118 motivation from LIT-BACKED to MEASURED on this slice, in whichever direction the data says, H-FAB (anti-hallucination surface): on control queries (no licensed answer exists), LLM arms fabricate answers rather than refuse at a material rate (best-LLM cell fabrication Wilson-LB > 0.30) while the engine refuses with licensed ERR codes — the fail-closed surface RAG-plus-LLM lacks, quantified — a5-llm — engine-vs-LLM head-to-head on the pinned a5 code-structure slice: absolute conjunctive-accuracy superiority primary (engine vs best of {direct,RAG} x {R1,R2,R3}, NO denominator), oracle-strong kernel-as-text RAG null, 10^3x cost co-gate (HL3a cost clause measured), fabrication secondary, lenient pro-LLM extraction instrument with P10-analogue gates; fresh runs only (reuse DEFERRED; engine re-run declared via reuse_overrides and doubling as the regression gate); design-complete, maintainer sign-off pending
prereg doc: docs/design-a5-llm.md (sha256 16632a75)

## Pre-registered kill criterion (verbatim) — rendered beside EVERY verdict

> HA5-LLM kills (architecture-ladder section 5.1 third-kill instantiated for the code vertical + the HL3a cost clause; verbatim): (a) DIFFERENTIATOR-KILL — any extraction-gate-valid LLM cell (the exhaustive declared six-cell family only; trivial baselines excluded) reaches conjunctive accuracy within 0.05 (point estimate) of the engine's on the pinned 977-query slice: the exactness differentiator is dead on this slice regardless of cost, the record names the killing cell, and L3b's router premise must be re-argued from cost alone; (b) COST-KILL — cost_ratio_min <= 10^3 (usd/query, F0 accounting): HL3a's >=10^3x cost clause is dead at this scale and the efficiency thesis for the L3 code vertical reverts to unproven; (c) primary one-sided 95% UPPER bound <= 0.10: the superiority margin is demonstrably not met. Extraction-gate failures and engine-regression mismatches are INSTRUMENT events and can never fire a kill or a PASS. The NL-parse kill belongs to a5-nl and cannot fire here.

## OUTCOME: **PASS-PENDING-AUDIT**

Fired rule 2 (declares `PASS`): `{"a":{"a":{"metric":"/analysis/primary_lower_onesided95"},"b":{"const":0.1},"op":"gt"},"b":{"a":{"a":{"metric":"/analysis/cost_ratio_min"},"b":{"const":1000},"op":"gt"},"b":{"a":{"metric":"/analysis/engine_matches_a5"},"b":{"const":1},"op":"eq"},"op":"and"},"op":"and"}`
evaluated over analysis-output.json (sha256 f80a491e).

**Not citable as PASS until the independent cross-vendor re-derivation (audit role, P5 R8/R10) confirms.**

## Endpoints (full pre-declared metric vector — all of them)

| endpoint | role | metric | value | pre-registered test |
|---|---|---|---|---|
| primary | primary | `/analysis/effect_size` | 0.6601842374616171 | ABSOLUTE superiority, no denominator (f2b-replicate discipline): effect_size = conj_acc(engine) - conj_acc(best-LLM cell), best-LLM per the pre-declared max rule over the exhaustive six-cell family (gate-valid cells only); paired per-query BCa bootstrap over the 977 pinned queries (B=10000, PRNG seed 20260709), one-sided alpha=0.05; reject iff the one-sided 95% lower bound > 0.10 |
| sec-cost-gate | secondary | `/analysis/cost_ratio_min` | 22835.94771419218 | verdict-bearing co-gate (HL3a cost clause, MEASURED here for the first time): cost_ratio_min = min over the six LLM cells of usd_per_query(cell)/usd_per_query(engine), F0 section 3.3/3.4 accounting (engine CPU-metered at the pinned core rate, LLM at pinned Modal GPU rate); PASS requires > 1000; <= 1000 is the COST-KILL |
| sec-separation-gate | secondary | `/gates/separation_valid` | false | INSTRUMENT gate, pre-declared (not a hypothesis test, not a Holm member): conj(llm-direct-R3) - conj(llm-direct-R1) >= 0.05 AND one-sided 95% BCa lower bound > 0; on failure the scale_trend_rag secondary is INSTRUMENT-INVALID and leaves the Holm family BEFORE any p-value comparison; the absolute primary still reads |
| sec-covered-superiority | secondary | `/analysis/holm/covered_superiority` | true | covered-exact(engine) - covered-exact(best-LLM cell) one-sided 95% BCa lower bound > 0 over the 855 covered queries; Holm within F-secondary(a5-llm) at alpha=0.05 |
| sec-refusal-superiority | secondary | `/analysis/holm/refusal_superiority` | true | control-refusal(engine, STRICT code) - control-refusal-any(best-LLM cell, LENIENT) one-sided 95% BCa lower bound > 0 over the 122 control queries; Holm within F-secondary(a5-llm) |
| sec-rag-lift | secondary | `/analysis/holm/rag_lift_r3` | true | conj(llm-rag-R3) - conj(llm-direct-R3) one-sided 95% BCa lower bound > 0 (do handed facts rescue the LLM at the largest rung?); Holm within F-secondary(a5-llm) |
| sec-scale-trend | secondary | `/analysis/holm/scale_trend_rag` | false | conj(llm-rag-R3) - conj(llm-rag-R1) one-sided 95% BCa lower bound > 0; CONDITIONAL on the separation gate (else INSTRUMENT-INVALID, excluded from the family before any p comparison); 3 rungs of one family license SIGN + direction/order-of-magnitude language only, never a slope law |
| sec-fabrication | secondary | `/analysis/holm/fabrication_material` | true | fabrication rate (non-refusal answers on control queries) of the best-LLM cell, Wilson 95% lower bound > 0.30 — the anti-hallucination surface made quantitative; Holm within F-secondary(a5-llm) |
| sec-extraction-instrument | secondary | `/gates/instrument_valid` | true | P10-analogue extraction gate per LLM cell: extraction-success (parseable answer or recognisable refusal under the pinned lenient extractor) Wilson 95% LB >= 0.90 at n=977; a failing cell is excluded from best-LLM selection and its Holm members (disclosed); record-level validity requires >=1 llm-rag cell AND >=1 llm-direct cell passing, the pins/strata checks, retrieval_completeness_violations = 0, and the engine-regression check (fresh engine pass reproduces a5's logged per-query outcomes exactly + byte-identical repeat); failures are instrument events, never hypothesis events |

Raw analysis-output document (ALL derived statistics live here and nowhere else, G-4):

```json
{
  "analysis": {
    "best_llm_cell": "llm-rag-R3",
    "best_llm_conj_acc": 0.3398157625383828,
    "bootstrap_B": 10000,
    "cells": {
      "abstain-all-R0": {
        "arm": "abstain-all",
        "conj_acc": 0.12487205731832139,
        "control_refused_any_rate": 1.0,
        "covered_exact_rate": 0.0,
        "note": "STRICT a5 rules (engine) / descriptive bracket (trivial arms; control conjunct = refused-any)",
        "rung": "R0"
      },
      "answer-all-R0": {
        "arm": "answer-all",
        "conj_acc": 0.8751279426816786,
        "control_refused_any_rate": 0.0,
        "covered_exact_rate": 1.0,
        "note": "STRICT a5 rules (engine) / descriptive bracket (trivial arms; control conjunct = refused-any)",
        "rung": "R0"
      },
      "engine-R0": {
        "arm": "engine",
        "conj_acc": 1.0,
        "control_refused_any_rate": 1.0,
        "covered_exact_rate": 1.0,
        "note": "STRICT a5 rules (engine) / descriptive bracket (trivial arms; control conjunct = refused-any)",
        "rung": "R0"
      },
      "llm-direct-R1": {
        "arm": "llm-direct",
        "conj_acc": 0.26509723643807576,
        "control_fabricated_rate": 0.6475409836065574,
        "control_refused_any_rate": 0.3524590163934426,
        "covered_exact_rate": 0.25263157894736843,
        "extraction_gate_pass": true,
        "extraction_success_rate": 1.0,
        "flops_per_query_2N": 122570327533.2651,
        "latency_ms_p50": 17.338,
        "latency_ms_p95": 71.666,
        "mean_tokens_per_query": 453.96417604913,
        "rung": "R1",
        "truncation_count": 0,
        "usd_per_query": 7.643267371773003e-06
      },
      "llm-direct-R2": {
        "arm": "llm-direct",
        "conj_acc": 0.04094165813715456,
        "control_fabricated_rate": 0.9918032786885246,
        "control_refused_any_rate": 0.00819672131147541,
        "covered_exact_rate": 0.0456140350877193,
        "extraction_gate_pass": true,
        "extraction_success_rate": 1.0,
        "flops_per_query_2N": 333371791197.5435,
        "latency_ms_p50": 61.434,
        "latency_ms_p95": 98.48,
        "mean_tokens_per_query": 463.01637666325485,
        "rung": "R2",
        "truncation_count": 0,
        "usd_per_query": 2.1534629819174343e-05
      },
      "llm-direct-R3": {
        "arm": "llm-direct",
        "conj_acc": 0.13715455475946775,
        "control_fabricated_rate": 0.9016393442622951,
        "control_refused_any_rate": 0.09836065573770492,
        "covered_exact_rate": 0.14269005847953217,
        "extraction_gate_pass": true,
        "extraction_success_rate": 1.0,
        "flops_per_query_2N": 1584452200614.1248,
        "latency_ms_p50": 82.167,
        "latency_ms_p95": 164.574,
        "mean_tokens_per_query": 466.0153531218014,
        "rung": "R3",
        "truncation_count": 0,
        "usd_per_query": 3.3094450130785854e-05
      },
      "llm-rag-R1": {
        "arm": "llm-rag",
        "conj_acc": 0.2374616171954964,
        "control_fabricated_rate": 0.4016393442622951,
        "control_refused_any_rate": 0.5983606557377049,
        "covered_exact_rate": 0.18596491228070175,
        "extraction_gate_pass": true,
        "extraction_success_rate": 0.9866939611054247,
        "flops_per_query_2N": 786992517911.9755,
        "latency_ms_p50": 43.84,
        "latency_ms_p95": 342.806,
        "mean_tokens_per_query": 2914.787103377687,
        "rung": "R1",
        "truncation_count": 194,
        "usd_per_query": 8.650568634140796e-05
      },
      "llm-rag-R2": {
        "arm": "llm-rag",
        "conj_acc": 0.2968270214943705,
        "control_fabricated_rate": 0.36065573770491804,
        "control_refused_any_rate": 0.639344262295082,
        "covered_exact_rate": 0.247953216374269,
        "extraction_gate_pass": true,
        "extraction_success_rate": 1.0,
        "flops_per_query_2N": 2105326427840.3276,
        "latency_ms_p50": 137.272,
        "latency_ms_p95": 1403.717,
        "mean_tokens_per_query": 2924.064483111566,
        "rung": "R2",
        "truncation_count": 194,
        "usd_per_query": 0.00012550045490731265
      },
      "llm-rag-R3": {
        "arm": "llm-rag",
        "conj_acc": 0.3398157625383828,
        "control_fabricated_rate": 0.7868852459016393,
        "control_refused_any_rate": 0.21311475409836064,
        "covered_exact_rate": 0.35789473684210527,
        "extraction_gate_pass": true,
        "extraction_success_rate": 1.0,
        "flops_per_query_2N": 9968354554759.469,
        "latency_ms_p50": 402.231,
        "latency_ms_p95": 2549.9,
        "mean_tokens_per_query": 2931.8689866939612,
        "rung": "R3",
        "truncation_count": 194,
        "usd_per_query": 0.0002178060673262823
      }
    },
    "cost_ratio_min": 22835.94771419218,
    "differentiator_within_kill": false,
    "effect_size": 0.6601842374616171,
    "engine_conj_acc": 1.0,
    "engine_control_refusal_rate": 1.0,
    "engine_covered_exact_rate": 1.0,
    "engine_matches_a5": 1,
    "engine_usd_per_query": 3.3470331371545543e-10,
    "fabrication_rate_best_llm": 0.7868852459016393,
    "holm": {
      "covered_superiority": true,
      "covered_superiority_p": 9.999000099990002e-05,
      "fabrication_material": true,
      "fabrication_material_p": 1.6648951725090883e-28,
      "rag_lift_r3": true,
      "rag_lift_r3_p": 9.999000099990002e-05,
      "refusal_superiority": true,
      "refusal_superiority_p": 9.999000099990002e-05,
      "scale_trend_rag": false,
      "scale_trend_rag_p": 9.999000099990002e-05
    },
    "latency_ratio_min": 2235.71889103804,
    "n_control": 122,
    "n_covered": 855,
    "n_queries": 977,
    "primary_lower_onesided95": 0.6345957011258956,
    "primary_p": 9.999000099990002e-05,
    "primary_reject": true,
    "primary_upper_onesided95": 0.6827021494370522,
    "retrieval_completeness_violations": 0,
    "separation_gap": -0.127942681678608,
    "truncation_counts": {
      "llm-direct-R1": 0,
      "llm-direct-R2": 0,
      "llm-direct-R3": 0,
      "llm-rag-R1": 194,
      "llm-rag-R2": 194,
      "llm-rag-R3": 194
    }
  },
  "gates": {
    "instrument_valid": true,
    "separation_valid": false
  }
}
```

## Coverage disclosure (mandatory)

No coverage_requirement is frozen on this record (the correction note on the record states why); the M0b NICHE-SCOPE discipline still binds any external quotation of this verdict (P1: m0b precedes first external quotation).

## Scale

Rungs measured: R0, R1, R2, R3. Scale language licensed: **slope** (>=3 rungs for slope adjectives; 2 for a sign; 1 licenses nothing).

### Extrapolation envelope (verbatim — binding on every citation of this verdict)

> Measured range: R1-R3 SmolLM2-Instruct pinned revisions (135M/360M/1.7B — ONE model family, ONE vendor, 3 rungs => SIGN plus at most direction+order-of-magnitude trend language, never a slope law); ONE pinned 977-query closed-grammar eval authored against ONE extracted 889-record world layer from ONE 15-file Python snapshot; ONE prompt pack + ONE deterministic exact-match retrieval rule + ONE lenient extraction instrument (results are indexed to this instrument identity); greedy decode only. Coverage disclosure: the covered slice is covered BY CONSTRUCTION (queries authored against the extracted records) — every accuracy statement is bounded to this slice and licenses no representativeness claim for any other codebase, language, or query distribution. The verdict extrapolates to NO frontier or long-context model, NO deployable-RAG effectiveness claim (the null here is oracle-strong by design), NO NL behaviour (a5-nl), NO static-analysis-from-source claim (no such arm), and licenses NO statement about kernel usefulness to any model's internal computation. The closed-book direct arms measure fabrication/refusal behaviour, not knowledge. A PASS licenses the engine-vs-LLM differentiator AT these rungs on THIS slice; the s-vs-S honesty of f2b applies — nothing here speaks for larger hosts.

## Eligible & excluded runs

9 eligible final run(s).
Excluded: none.

## Audit

State: PENDING

## Deviations & amendments

None applied to this verdict.

---
### Non-binding commentary (does not and cannot alter the verdict above)

(none)
