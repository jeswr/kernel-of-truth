# m0b verdict — PASS-PENDING-AUDIT

computed: 2026-07-08T16:52:39Z | report-gen/1 | analysis 31ae9a69
frozen prereg: 902fe30c (frozen 2026-07-08T16:45:06Z) | amendments applied: none
encoder pin: 40e8c8ba | corpus pins: kernel-v0:8209cada, lexical-wn31:5e76def8, molecules-v0:69f0c8a3, task-family-tinystories:b6bcc9f6 | log tail: 26d1735c

## Pre-registered statement (from the frozen record)

**Hypotheses:** M0B-COVERAGE-GATE — M0b — kernel-vocabulary coverage census + NICHE-SCOPE gate (P1 §5 required pre-experiment gate; deterministic on-box census, no annotators, per correction c-m0b-1; P2 G-7: the number every later verdict restates; not itself a hypothesis)
prereg doc: docs/research-plan/01-hypotheses-experiments.md (sha256 71768a9c)

## Pre-registered kill criterion (verbatim) — rendered beside EVERY verdict

> P3 §1.1 m0b.gate consequence (RT-7, verbatim): 'coverage < X ⇒ every verdict template renders a NICHE-SCOPE banner and any frontier-pitch route must carry an explicit coverage-growth cost line — a gate with a consequence, not just disclosure.' Pre-declared default X = 20% of the target task family's content-word mass (GNG-0 ratification default, P7 second-pass verification list). FAIL here binds the NICHE-SCOPE banner; it does not stop Tier-1 (P1 §5: none of Tier 0 blocks Tier 1, but GATE-T1 requires m0b.close + m0b.gate evaluated).

## OUTCOME: **PASS-PENDING-AUDIT**

Fired rule 2 (declares `PASS`): `{"a":{"metric":"/analysis/coverage_fraction"},"b":{"const":0.2},"op":"gt"}`
evaluated over analysis-output.json (sha256 63ce6485).

**Not citable as PASS until the independent cross-vendor re-derivation (audit role, P5 R8/R10) confirms.**

## Endpoints (full pre-declared metric vector — all of them)

| endpoint | role | metric | value | pre-registered test |
|---|---|---|---|---|
| primary | primary | `/analysis/coverage_fraction` | 0.3542001386155407 | deterministic census fraction at the primary rung (molecules-v0) vs the pre-declared NICHE-SCOPE threshold X=0.20; count-based criterion, no statistical test (P1 common rules). Coverage here = surface form reachable in the kernel vocabulary today — a crude lower bound of judgment-based expressibility, stated as exactly that |
| sec-by-rung | secondary | `/analysis/coverage_by_rung` | {"kernel-v0": 0.2210239418867505, "molecules-v0": 0.3542001386155407, "wn31-aligned": 0.7841253037698164} | per-rung census fractions (kernel-v0 / molecules-v0 / wn31-aligned); the wn31-aligned rung is the AxiomsOnly-reachable band and is never quoted as explicated coverage; descriptive |

Raw analysis-output document (ALL derived statistics live here and nowhere else, G-4):

```json
{
  "analysis": {
    "coverage_by_rung": {
      "kernel-v0": 0.2210239418867505,
      "molecules-v0": 0.3542001386155407,
      "wn31-aligned": 0.7841253037698164
    },
    "coverage_fraction": 0.3542001386155407,
    "coverage_rung": "molecules-v0",
    "n_tokens_total": 1709765
  },
  "gates": {
    "instrument_valid": true
  }
}
```

## Coverage disclosure (mandatory)

Kernel-expressibility coverage (M0b): **0.3542** at rung **molecules-v0**. Every claim above is bounded to this covered slice.

## Scale

Rungs measured: R0. Scale language licensed: **none** (>=3 rungs for slope adjectives; 2 for a sign; 1 licenses nothing).

### Extrapolation envelope (verbatim — binding on every citation of this verdict)

> M0b has no P1 §4b row: coverage is corpus-indexed, not model-indexed. The measured coverage number extrapolates to NO other corpus or rung; it is restated verbatim with its rung in every later verdict (P2 G-7) and re-measured as the kernel grows (coverage-growth curve, P7 RT-11/§10).

## Eligible & excluded runs

1 eligible final run(s).
Excluded: none.

## Audit

State: PENDING

## Deviations & amendments

None applied to this verdict.

Pre-freeze correction notes on this record (lawful only before sign-off + before any final-phase run; they precede the freeze whose hash is above):
- registry/corrections/m0b/1-prefreeze-correction.json

---
### Non-binding commentary (does not and cannot alter the verdict above)

(none)
