# g7 verdict — FAIL

computed: 2026-07-08T16:55:52Z | report-gen/1 | analysis 691fad36
frozen prereg: 9eb54caf (frozen 2026-07-08T16:45:07Z) | amendments applied: none
encoder pin: 40e8c8ba | corpus pins: kernel-v0:8209cada, lexical-wn31:5e76def8, molecules-v0:69f0c8a3 | log tail: fda37061

## Pre-registered statement (from the frozen record)

**Hypotheses:** HS7 — G7 — apply-clause cap/growth bulk projection over the committed corpora (HS7 / NF6; deterministic count, no test; pinned one-level inline projection, biased against the kill — correction c-g7-1)
prereg doc: docs/research-plan/01-hypotheses-experiments.md (sha256 71768a9c)

## Pre-registered kill criterion (verbatim) — rendered beside EVERY verdict

> P1 §4 HS7 statement + kill (verbatim): '(HS7) inlining relational content forces cap violations or >1.5× clause growth on >10% of records at bulk scale ⇒ apply-clauses (kot-ast/2) win; else defer.' Kill (P1 §8): 'cap violations/1.5× growth >10% ⇒ kot-ast/2.' Kill criteria are the numeric bounds from NF6, verbatim. FAIL here means the fork selects kot-ast/2 (a design selection, not a programme kill).

## OUTCOME: **FAIL**

Fired rule 1 (declares `FAIL`): `{"a":{"metric":"/analysis/breach_share"},"b":{"const":0.1},"op":"gt"}`
evaluated over analysis-output.json (sha256 bf97dcc0).

## Endpoints (full pre-declared metric vector — all of them)

| endpoint | role | metric | value | pre-registered test |
|---|---|---|---|---|
| primary | primary | `/analysis/breach_share` | 0.9133665255854587 | deterministic bulk-projection count vs the pre-registered 10% bound (NF6); count-based fork criterion, carries no statistical test (P1 common rules) |

Raw analysis-output document (ALL derived statistics live here and nowhere else, G-4):

```json
{
  "analysis": {
    "breach_share": 0.9133665255854587,
    "cap_violation_share": 0.25253818946725587,
    "growth_share": 0.9130866249925784,
    "n_records_bulk": 117899
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

> P1 §4b row HS2–HS8 (verbatim): Measured range: R0 — no host model. Reasonable extrapolation envelope: Model-scale-free (properties of the kernel formalism); the relevant axis is KERNEL size: verdicts on 54–10³ records re-checked at 10⁴–10⁵ during bulk authoring (G6/G7 re-run as regression). Literature anchor + licensing assumption: Formal-fragment properties don't vary with observer scale; only corpus composition shifts them.

## Eligible & excluded runs

1 eligible final run(s).
Excluded: none.

## Audit

State: N/A

## Deviations & amendments

None applied to this verdict.

Pre-freeze correction notes on this record (lawful only before sign-off + before any final-phase run; they precede the freeze whose hash is above):
- registry/corrections/g7/1-prefreeze-correction.json

---
### Non-binding commentary (does not and cannot alter the verdict above)

(none)
