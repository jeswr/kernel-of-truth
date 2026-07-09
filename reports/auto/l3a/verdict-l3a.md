# l3a verdict — PASS

computed: 2026-07-09T01:25:42Z | report-gen/1 | analysis a583f942
frozen prereg: cc76d8db (frozen 2026-07-09T01:13:07Z) | amendments applied: none
encoder pin: 40e8c8ba | corpus pins: axioms-v0:bfcb2f45, kernel-v0:8209cada, l3a-eval:53eb788b, molecules-v0:69f0c8a3, world-v0:dfa51451 | log tail: 85d530d8

## Pre-registered statement (from the frozen record)

**Hypotheses:** HL3a — L3a — kot-axiom/1 v0 rules-engine oracle: gold-parse exact-answer + licensed-refusal gate (HL3a engine leg; architecture-ladder.md section 5.1)
prereg doc: docs/design-l3a-rules-engine-oracle.md (sha256 002afa81)

## Pre-registered kill criterion (verbatim) — rendered beside EVERY verdict

> architecture-ladder.md section 5.1 HL3a kill criteria (verbatim): 'Engine-with-gold-parse answers < the pre-declared fraction (engine or store is inadequate - indict the stage); OR mapper-parse loses > a pre-declared fraction of gold-parse accuracy (the NL boundary eats the rung; L3 waits for a better parser, not more GPU); OR LLM+RAG at R1 matches engine accuracy at comparable cost (the differentiator failed).' THIS RECORD instantiates clause 1 only, with the pre-declared fractions: covered exact-answer Wilson-LB must clear 0.98 AND control correct-refusal Wilson-LB must clear 0.95; either upper bound at-or-below its gate is the clause-1 kill (engine/store indicted). Clauses 2-3 belong to the pre-declared successors (l3a-parse, l3a-cost) and cannot be decided here.

## OUTCOME: **PASS**

Fired rule 2 (declares `PASS`): `{"a":{"a":{"metric":"/analysis/covered_exact_wilson_lb"},"b":{"const":0.98},"op":"gt"},"b":{"a":{"a":{"metric":"/analysis/control_refusal_wilson_lb"},"b":{"const":0.95},"op":"gt"},"b":{"a":{"metric":"/analysis/store_violations_detected"},"b":{"const":6},"op":"eq"},"op":"and"},"op":"and"}`
evaluated over analysis-output.json (sha256 58e3a9ae).

## Endpoints (full pre-declared metric vector — all of them)

| endpoint | role | metric | value | pre-registered test |
|---|---|---|---|---|
| primary | primary | `/analysis/covered_exact_wilson_lb` | 0.9955102074846524 | engine covered exact-answer rate vs the 0.98 gate, one-sided Wilson 95% lower bound (z=1.645, kot_common formula) over the 600 pre-authored covered queries; expected rate ~1.0 for a correct deterministic engine (0.995 planning value passes the P8 section 1.6 decidability lint) |
| sec-refusal | secondary | `/analysis/control_refusal_wilson_lb` | 0.9910605512394408 | control correct-refusal rate (STRICT expected-ERR_*-code match) vs the 0.95 gate, one-sided Wilson 95% lower bound over the 300 control queries; co-gate in the PASS rule — the anti-hallucination half of the conjunctive primary |
| sec-baselines | secondary | `/analysis/baseline_answerall_covered_exact_rate` | 1.0 | descriptive: the two trivial-policy baselines bracket the conjunction (abstain-all: covered ~0 / refused-any ~1; answer-all: covered high / refused ~0); no threshold — demonstrates the conjunctive primary is not satisfiable by either degenerate policy |
| sec-cost | secondary | `/analysis/engine_mean_us_per_query` | 5.293745555555555 | descriptive: mean microseconds per query on the pinned r0 box; reported on the V ledger; the HL3a >=10^3 cost-ratio claim is NOT tested in this record (successor l3a-cost) |

Raw analysis-output document (ALL derived statistics live here and nowhere else, G-4):

```json
{
  "analysis": {
    "baseline_abstain_control_refused_any_rate": 1.0,
    "baseline_abstain_covered_exact_rate": 0.0,
    "baseline_answerall_control_refused_any_rate": 0.0,
    "baseline_answerall_covered_exact_rate": 1.0,
    "control_refusal_rate": 1.0,
    "control_refusal_wilson_lb": 0.9910605512394408,
    "control_refusal_wilson_ub": 0.9999999999999998,
    "covered_exact_rate": 1.0,
    "covered_exact_wilson_lb": 0.9955102074846524,
    "covered_exact_wilson_ub": 1.0000000000000002,
    "engine_mean_us_per_query": 5.293745555555555,
    "n_control": 300,
    "n_covered": 600,
    "store_violations_detected": 6
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

> Measured range: R0 - no host model; ONE engine build (kot_axiom.py, pinned), ONE axiom set (6 records), ONE world layer (598 records, 324 entities), ONE closed-grammar gold-parsed 900-query eval authored against those records. Reasonable extrapolation envelope: engine-correctness and fail-closed-licensing properties are formalism properties in the HS2-HS8 envelope class (kernel-size axis, not model-scale axis): re-verify by regression re-run when the axiom inventory, world-layer size, or query grammar grows. This verdict extrapolates to NO natural-language behaviour, NO other corpus, NO real-world fact-coverage claim, NO LLM-comparative accuracy or cost claim (successors l3a-parse / l3a-cost), and licenses NO statement about kernel usefulness to any model.

## Eligible & excluded runs

3 eligible final run(s).
Excluded: none.

## Audit

State: CONFIRMED (registry/audits/l3a/1-gate-a-codex.json)

## Deviations & amendments

None applied to this verdict.

---
### Non-binding commentary (does not and cannot alter the verdict above)

> Runner note (runner-2, 2026-07-09, non-binding): `claims-check` on the pinned
> prereg doc reports 3 `ERR_ASM_UNTAGGED_PREMISE` findings for the PREMISE items
> in section 0. The epistemic tags ARE present in the document content
> ([MEASURED]/[LIT-BACKED], with refs) but sit on the markdown continuation line
> below the `PREMISE:` marker, and the lint is line-granular. The doc is pinned
> in the frozen record (sha 002afa81), so it is deliberately NOT edited
> post-freeze; the formatting-only fix belongs to any successor record's prereg
> doc. Process lesson recorded: run `claims-check` on the prereg doc BEFORE
> `prereg-freeze`. Also for the auditor (per ASM-0006): the audit should
> independently re-derive a sample of l3a-eval expected answers from
> data/world-v0 records; abstain-all's control_refused_correct_code=0 is by
> design (its blanket ABSTAIN code never matches the expected ERR_* code under
> the strict-code scoring rule).
