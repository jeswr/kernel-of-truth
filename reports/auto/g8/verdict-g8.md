# g8 verdict — FAIL

computed: 2026-07-10T06:04:42Z | report-gen/1 | analysis e5769612
frozen prereg: a3c45101 (frozen 2026-07-08T17:07:09Z) | amendments applied: 1
encoder pin: 40e8c8ba | corpus pins: kernel-v0:8209cada, math-lean-sample:938df269, math-mm:d87a3fa0, math-v0:73e5d351, mathlib-1000-sample:(at-inputs) | log tail: 43e1b5f6

## Pre-registered statement (from the frozen record)

**Hypotheses:** HS8 — G8 — Lean-minting viability: fragment gate, verified LLM location, round-trip fixed point (HS8 / NF3)
prereg doc: docs/research-plan/01-hypotheses-experiments.md (sha256 71768a9c)

## Pre-registered kill criterion (verbatim) — rendered beside EVERY verdict

> P1 §4 HS8 kill criterion (verbatim): 'As NF3: below either bound ⇒ Metamath-only identity stands, Lean stays annotation-only; near-zero F-verification of LLM candidates kills the bridge programme. Tests: fragment rate vs the 1% gate by exact binomial over the 1,000-declaration sample (Wilson lower bound must clear 1%); top-5 location rate vs the 80% gate likewise (α=0.05, one-sided).'

## OUTCOME: **FAIL**

Fired rule 1 (declares `FAIL`): `{"a":{"a":{"metric":"/analysis/fragment_wilson_ub"},"b":{"const":0.01},"op":"lte"},"b":{"a":{"a":{"metric":"/analysis/location_wilson_ub"},"b":{"const":0.8},"op":"lte"},"b":{"a":{"metric":"/analysis/f_verification_rate"},"b":{"const":0.01},"op":"lt"},"op":"or"},"op":"or"}`
evaluated over analysis-output.json (sha256 6670c016).

## Endpoints (full pre-declared metric vector — all of them)

| endpoint | role | metric | value | pre-registered test |
|---|---|---|---|---|
| primary | primary | `/analysis/fragment_wilson_lb` | 0.0 | fragment rate vs the 1% gate by one-sided exact binomial over the 1,000-declaration sample, α=0.05; Wilson 95% lower bound must clear 0.01 |
| sec-location | secondary | `/analysis/location_wilson_lb` | 0.0638193834750099 | top-5 location rate vs the 80% gate, one-sided α=0.05, Wilson lower bound over the 39-target overlap set; detectable alternative: true rate ≳0.92 (tight — printed per the P8 §1.6 decidability lint) |
| sec-roundtrip | secondary | `/analysis/roundtrip_holds` | true | deterministic: every round-trip reaches the fixed point |
| sec-fver | secondary | `/analysis/f_verification_rate` | 0.050359712230215826 | F-verification rate of LLM candidates; near-zero (<0.01) kills the bridge programme (NF3) |

Raw analysis-output document (ALL derived statistics live here and nowhere else, G-4):

```json
{
  "analysis": {
    "f_verification_rate": 0.050359712230215826,
    "fragment_rate": 0.0,
    "fragment_wilson_lb": 0.0,
    "fragment_wilson_ub": 0.002698722190285034,
    "location_rate": 0.1282051282051282,
    "location_wilson_lb": 0.0638193834750099,
    "location_wilson_ub": 0.24083743769171598,
    "n_location_targets": 39,
    "n_mathlib_decls": 1000,
    "roundtrip_holds": true
  },
  "gates": {
    "instrument_valid": true
  }
}
```

## Coverage disclosure (mandatory)

Kernel-expressibility coverage (M0b): **0.3542** at rung **molecules-v0** — a corpus-indexed, rung-indexed, kernel-state-indexed measurement, NOT a general ("natural") coverage property of the kernel.

Full measured scope: census by experiment `m0b` (frozen 2026-07-08T16:45:06Z) over exactly its pinned inputs — kernel-v0:8209cada, lexical-wn31:5e76def8, molecules-v0:69f0c8a3, task-family-tinystories:b6bcc9f6 (encoder pin 40e8c8ba) — i.e. that one pinned corpus against the incomplete kernel instance as pinned at that freeze; coverage is re-measured as the kernel grows (coverage-growth curve, P7 RT-11/§10).

No-extrapolation envelope on this number (per the m0b verdict envelope and the assumption register, registry/assumptions.jsonl): it extrapolates to NO other corpus, rung, or kernel state. Every claim above is bounded to this covered slice, within exactly that scope.

## Scale

Rungs measured: R0. Scale language licensed: **none** (>=3 rungs for slope adjectives; 2 for a sign; 1 licenses nothing).

### Extrapolation envelope (verbatim — binding on every citation of this verdict)

> P1 §4b row HS2–HS8 (verbatim): Measured range: R0 — no host model. Reasonable extrapolation envelope: Model-scale-free (properties of the kernel formalism); the relevant axis is KERNEL size: verdicts on 54–10³ records re-checked at 10⁴–10⁵ during bulk authoring (G6/G7 re-run as regression). Literature anchor + licensing assumption: Formal-fragment properties don't vary with observer scale; only corpus composition shifts them.

## Eligible & excluded runs

1 eligible final run(s).
Excluded: none.

## Audit

State: N/A

## Deviations & amendments

- amendment 1 (see registry/amendments/g8/)

Pre-freeze correction notes on this record (lawful only before sign-off + before any final-phase run; they precede the freeze whose hash is above):
- registry/corrections/g8/1-prefreeze-correction.json

---
### Non-binding commentary (does not and cannot alter the verdict above)

(none)
