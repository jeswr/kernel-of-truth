# a5 verdict — PASS

computed: 2026-07-09T02:45:06Z | report-gen/1 | analysis 87f23a69
frozen prereg: 6c42f8a8 (frozen 2026-07-09T02:31:56Z) | amendments applied: none
encoder pin: 40e8c8ba | corpus pins: a5-eval:3676d689, code-axioms-v0:dc930b4f, code-corpus-v0:1063ad50, code-v0:01009b1f, code-world-v0:b8a8a50a, kernel-v0:8209cada | log tail: 196c7b63

## Pre-registered statement (from the frozen record)

**Hypotheses:** HA5 — A5 - code world-layer + code-structure oracle: deterministic extraction, exact-answer + licensed-refusal gate (HA5 engine leg; idea-code-worldlayer-cpg, idea-registry NOW-list item 5)
prereg doc: docs/design-a5-code-worldlayer-oracle.md (sha256 da690903)

## Pre-registered kill criterion (verbatim) — rendered beside EVERY verdict

> HA5 (clause-1 analog of the HL3a kill, architecture-ladder.md section 5.1, instantiated for the code vertical): engine-with-deterministic-extraction answers below the pre-declared fractions indict the engine/store/extraction-mapping stage - covered exact-answer Wilson-LB must clear 0.98 AND control correct-refusal Wilson-LB must clear 0.95; either upper bound at-or-below its gate is the kill (the code vertical's engine leg is inadequate; fix the stage, not the narrative). The NL-parse and LLM-comparison kills belong to the pre-declared successors (a5-nl, a5-llm) and cannot be decided here; in particular NO engine-vs-LLM differentiator claim can pass or fail in this record.

## OUTCOME: **PASS**

Fired rule 2 (declares `PASS`): `{"a":{"a":{"metric":"/analysis/covered_exact_wilson_lb"},"b":{"const":0.98},"op":"gt"},"b":{"a":{"a":{"metric":"/analysis/control_refusal_wilson_lb"},"b":{"const":0.95},"op":"gt"},"b":{"a":{"metric":"/analysis/store_violations_detected"},"b":{"const":3},"op":"eq"},"op":"and"},"op":"and"}`
evaluated over analysis-output.json (sha256 aba98e8a).

## Endpoints (full pre-declared metric vector — all of them)

| endpoint | role | metric | value | pre-registered test |
|---|---|---|---|---|
| primary | primary | `/analysis/covered_exact_wilson_lb` | 0.9968450437316213 | engine covered exact-answer rate vs the 0.98 gate, one-sided Wilson 95% lower bound (z=1.645, kot_common formula) over the 855 pre-authored covered queries; expected rate ~1.0 for a correct deterministic engine (0.995 planning value passes the P8 section 1.6 decidability lint) |
| sec-refusal | secondary | `/analysis/control_refusal_wilson_lb` | 0.9783007677455842 | control correct-refusal rate (STRICT expected-ERR_*-code match) vs the 0.95 gate, one-sided Wilson 95% lower bound over the 122 control queries; co-gate in the PASS rule - the anti-hallucination half of the conjunctive primary |
| sec-baselines | secondary | `/analysis/baseline_answerall_covered_exact_rate` | 1.0 | descriptive: the two trivial-policy baselines bracket the conjunction (abstain-all: covered ~0 / refused-any ~1; answer-all: covered high / refused ~0); no threshold - demonstrates the conjunctive primary is not satisfiable by either degenerate policy |
| sec-cost | secondary | `/analysis/engine_mean_us_per_query` | 7.821020470829068 | descriptive: mean microseconds per query on the pinned r0 box; no LLM-relative cost or accuracy claim is tested in this record (successor a5-llm) |

Raw analysis-output document (ALL derived statistics live here and nowhere else, G-4):

```json
{
  "analysis": {
    "baseline_abstain_control_refused_any_rate": 1.0,
    "baseline_abstain_covered_exact_rate": 0.0,
    "baseline_answerall_control_refused_any_rate": 0.0,
    "baseline_answerall_covered_exact_rate": 1.0,
    "control_refusal_rate": 1.0,
    "control_refusal_wilson_lb": 0.9783007677455842,
    "control_refusal_wilson_ub": 1.0000000000000002,
    "covered_exact_rate": 1.0,
    "covered_exact_wilson_lb": 0.9968450437316213,
    "covered_exact_wilson_ub": 1.0,
    "engine_mean_us_per_query": 7.821020470829068,
    "n_control": 122,
    "n_covered": 855,
    "store_violations_detected": 3
  },
  "gates": {
    "instrument_valid": true
  }
}
```

## Coverage disclosure (mandatory)

No coverage_requirement is frozen on this record (the correction note on the record states why); the M0b NICHE-SCOPE discipline still binds any external quotation of this verdict (P1: m0b precedes first external quotation).

## Scale

Rungs measured: R0. Scale language licensed: **none** (>=3 rungs for slope adjectives; 2 for a sign; 1 licenses nothing).

### Extrapolation envelope (verbatim — binding on every citation of this verdict)

> Measured range: R0 - no host model; ONE engine build (kot_axiom.py, byte-identical to the l3a pin) + ONE desugaring layer (kot_code.py), ONE code axiom set (5 records), ONE world layer (889 records extracted by kot-code-extract/1 from ONE pinned 15-file Python snapshot of this repo's own tooling), ONE closed-grammar 977-query eval authored against those records. Reasonable extrapolation envelope: engine-correctness and fail-closed-licensing properties are formalism properties in the HS2-HS8 envelope class (kernel-size axis, not model-scale axis): re-verify by regression re-run when the axiom inventory, extractor version, snapshot corpus, or query grammar changes. This verdict extrapolates to NO other codebase or programming language, NO natural-language behaviour, NO extraction-soundness claim w.r.t. runtime semantics (ASM-0009), NO LLM-comparative accuracy or cost claim (the arXiv:2505.12118 motivation is literature, not a measurement of this record; successor a5-llm), and licenses NO statement about kernel usefulness to any model.

## Eligible & excluded runs

3 eligible final run(s).
Excluded: none.

## Audit

State: CONFIRMED (registry/audits/a5/1-gate-a-codex.json)

## Deviations & amendments

None applied to this verdict.

---
### Non-binding commentary (does not and cannot alter the verdict above)

(none)
