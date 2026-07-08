# f1 verdict — PASS

computed: 2026-07-08T17:21:39Z | report-gen/1 | analysis 885fde8e
frozen prereg: df1e2045 (frozen 2026-07-08T16:45:05Z) | amendments applied: none
encoder pin: 40e8c8ba | corpus pins: lexical-wn31:5e76def8 | log tail: e0b5f7cc

## Pre-registered statement (from the frozen record)

**Hypotheses:** HE5 — F1 — KOTK/2 byte accounting vs best compressed gloss-text store (HE5 byte premise; R0, deterministic measurement; decides the BYTE ratio only — the <=2x retrieval-latency sub-premise is NOT decided here and attaches to the F5 accuracy leg where retrieval is actually served; full-V discipline likewise attaches to F5; correction c-f1-1)
prereg doc: docs/research-plan/01-hypotheses-experiments.md (sha256 71768a9c)

## Pre-registered kill criterion (verbatim) — rendered beside EVERY verdict

> P1 §3 HE5 kill criterion (verbatim): 'F1: byte claim dropped if <2× vs compressed gloss text (M4 then proceeds, if at all, on verifiability alone — which is HC2's territory, not an efficiency claim).' Byte premise under test (P1 HE5 statement, verbatim): '(Byte premise) KOTK/2 beats the best general-purpose-compressed text store of the same records by ≥2× bytes at ≤2× retrieval latency.'

## OUTCOME: **PASS**

Fired rule 2 (declares `PASS`): `{"a":{"metric":"/analysis/byte_ratio"},"b":{"const":2.0},"op":"gte"}`
evaluated over analysis-output.json (sha256 bdf4d6b2).

## Endpoints (full pre-declared metric vector — all of them)

| endpoint | role | metric | value | pre-registered test |
|---|---|---|---|---|
| primary | primary | `/analysis/byte_ratio` | 6.736930894606587 | deterministic byte accounting: sum(gloss_zstd_bytes)/sum(kernel_pack_bytes) vs the pre-registered 2.0 line; deterministic measurement, no sampling test (P1 common rules: count-based criteria carry no test) |
| sec-bpr | secondary | `/analysis/bytes_per_record_kernel` | 2.898651000500887 | descriptive: measured KOTK/2 bytes/record vs the 2.90 B/rec prior; no threshold |

Raw analysis-output document (ALL derived statistics live here and nowhere else, G-4):

```json
{
  "analysis": {
    "byte_ratio": 6.736930894606587,
    "bytes_per_record_gloss": 19.52801147795672,
    "bytes_per_record_kernel": 2.898651000500887,
    "n_records": 117791,
    "n_runs": 1
  },
  "gates": {
    "instrument_valid": true
  }
}
```

## Coverage disclosure (mandatory)

No coverage_requirement is frozen on this record (the correction note on the record states why); the M0b NICHE-SCOPE discipline still binds any external quotation of this verdict (P1: m0b precedes first external quotation).

## Scale

Rungs measured: S1e5. Scale language licensed: **none** (>=3 rungs for slope adjectives; 2 for a sign; 1 licenses nothing).

### Extrapolation envelope (verbatim — binding on every citation of this verdict)

> P1 §4b row HE5 (verbatim): Measured range: Store 10³–10⁶ records (model-free); accuracy leg 70M–160M. Reasonable extrapolation envelope: Byte claim: store-size axis extrapolates freely (measured B/rec is size-independent); accuracy leg ≤410M without T3; direction to 7B via RETRO's published range. Literature anchor + licensing assumption: RETRO measured 150M–7B with benefit retained (and InstructRetro absorption caveat); that published trend is the only license to speak above 410M. This record decides the BYTE PREMISE only.

## Eligible & excluded runs

1 eligible final run(s).

| excluded seq | reason (the failed eligibility test, named) |
|---|---|
| 0 | phase!=final ('exploratory') |

## Audit

State: CONFIRMED (registry/audits/f1/1-gate-a-codex.json)

## Deviations & amendments

None applied to this verdict.

Pre-freeze correction notes on this record (lawful only before sign-off + before any final-phase run; they precede the freeze whose hash is above):
- registry/corrections/f1/1-prefreeze-correction.json

---
### Non-binding commentary (does not and cannot alter the verdict above)

(none)
