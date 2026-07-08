# g6 verdict — INCONCLUSIVE

computed: 2026-07-08T16:55:03Z | report-gen/1 | analysis 8affc8e2
frozen prereg: 7cf6fb67 (frozen 2026-07-08T16:45:07Z) | amendments applied: none
encoder pin: 40e8c8ba | corpus pins: kernel-v0:8209cada, lexical-wn31:5e76def8, molecules-v0:69f0c8a3, onto-sumo:80cf6eb0 | log tail: e71b71d7

## Pre-registered statement (from the frozen record)

**Hypotheses:** HS6 — G6 — AND-under-operator static count over the committed axiom corpora (HS6 / NF5; deterministic count, no test; the authored G4-set leg re-runs under a successor experiment id once d-ax exists — correction c-g6-1)
prereg doc: docs/research-plan/01-hypotheses-experiments.md (sha256 71768a9c)

## Pre-registered kill criterion (verbatim) — rendered beside EVERY verdict

> P1 §4 HS6 statement + kill (verbatim): '(HS6) <20% of the working axiom set needs AND-under-operator and all such are sidecar-expressible ⇒ the native fragment stays ∃-conjunctive-only.' Kill (P1 §8): '≥20% need + not sidecar-expressible ⇒ extend grammar.' Kill criteria are the numeric bounds from NF5, verbatim.

## OUTCOME: **INCONCLUSIVE**

Fired rule 3 (declares `INCONCLUSIVE`): `{"const":true}`
evaluated over analysis-output.json (sha256 c3ac261e).

## Endpoints (full pre-declared metric vector — all of them)

| endpoint | role | metric | value | pre-registered test |
|---|---|---|---|---|
| primary | primary | `/analysis/and_share` | 0.0005054999822007048 | deterministic static count vs the pre-registered 20% bound (NF5); count-based fork criterion, carries no statistical test (P1 common rules) |
| sec-sidecar | secondary | `/analysis/all_sidecar_expressible` | false | deterministic: every AND-under-operator axiom is sidecar-expressible |

Raw analysis-output document (ALL derived statistics live here and nowhere else, G-4):

```json
{
  "analysis": {
    "all_sidecar_expressible": false,
    "and_share": 0.0005054999822007048,
    "n_axioms": 280910
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
- registry/corrections/g6/1-prefreeze-correction.json

---
### Non-binding commentary (does not and cannot alter the verdict above)

(none)
