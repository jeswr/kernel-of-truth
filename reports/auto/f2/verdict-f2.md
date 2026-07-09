# f2 verdict — FAIL

computed: 2026-07-09T00:14:28Z | report-gen/1 | analysis 068f68b8
frozen prereg: 28874f2b (frozen 2026-07-08T17:07:09Z) | amendments applied: 1, 2, 3, 4, 5, 6
encoder pin: 40e8c8ba | corpus pins: definitional-qa-eval-set:(at-inputs), external-eval-slice:(at-inputs), extraction-labelled-set:(at-inputs), gloss-corpus-and-rag-index:(at-inputs), kernel-v0:8209cada, molecules-v0:69f0c8a3 | log tail: 5fe870b1

## Pre-registered statement (from the frozen record)

**Hypotheses:** HE1, HE2, HC3, HS12 — F2 — the pivot: verifier-offload buys parameters (HE1 primary; HE2 cascade, HC3 PRM, HS12 placement riders); SmolLM2 135M/360M/1.7B; P10 extraction-instrument gate; gloss-text self-verify+retry arm per P7 RT-2
prereg doc: docs/research-plan/01-hypotheses-experiments.md (sha256 71768a9c)

## Pre-registered kill criterion (verbatim) — rendered beside EVERY verdict

> P1 §3 HE1 kill criterion (track text + RT-2 amendment, verbatim): 'dead at a rung if (a) <50% of the s→S gap closed at best pre-registered retry budget, OR (b) the text null, matched-compute sampling, or the gloss-text self-verify + retry arm closes as much gap at ≤ the same FLOPs/query — HE1 cannot PASS without the kernel-verifier arm beating arm 10 at matched budget, OR (c) closing the gap costs ≥ running model_S directly. Nulls require TOST.' HE2 rider (verbatim): 'Dead if not strictly dominant over BOTH the logprob gate AND the gloss-text self-check gate — dominance means the verifier-gated frontier point is above each competing gate's at every pre-registered escalation budget (per-budget paired bootstrap, Holm-corrected across budgets, α=0.05); any budget where either competing gate wins breaks dominance.' HC3 rider (verbatim): 'If the generic PRM matches the kernel verifier on kernel-covered content at matched FLOPs, the kernel's verification contribution collapses into commodity verification; determinism/provenance revert to governance claims and HC3 (and M1/M5's kernel-specificity) is dead.' HS12 has no kill — latency (batch-1 and throughput modes) selects the surviving implementation.

## OUTCOME: **FAIL**

Fired rule 1 (declares `FAIL`): `{"a":{"metric":"/analysis/gap_below_half"},"b":{"a":{"metric":"/analysis/competitor_closes_asmuch"},"b":{"a":{"metric":"/analysis/cost_ratio_vs_S"},"b":{"const":1.0},"op":"gte"},"op":"or"},"op":"or"}`
evaluated over analysis-output.json (sha256 5952a7ff).

## Endpoints (full pre-declared metric vector — all of them)

| endpoint | role | metric | value | pre-registered test |
|---|---|---|---|---|
| primary | primary | `/analysis/gap_closed_fraction_R1R2` | -40.133333333333205 | paired item bootstrap (BCa, B=10000, PRNG seed 20260708), one-sided α=0.05: the one-sided 95% lower bound of gap_closed(R1,R2) must clear the pre-registered 0.5 bar; best retry budget k∈{1,2,4} reselected inside every resample (selection inside the CI, P8 §1.7); estimand per P8 §1.2 |
| sec-beats-gloss-self-verify | secondary | `/analysis/holm/beats_gloss_self_verify` | true | one-sided paired bootstrap vs arm 10 at matched retry budget and FLOPs; Holm within F-secondary(f2) at α=0.05 (RT-2: HE1 cannot PASS without this) |
| sec-beats-text-null | secondary | `/analysis/holm/beats_text_null` | true | one-sided paired bootstrap vs the kernel-as-text arm; Holm within F-secondary(f2) |
| sec-pair-r2r3 | secondary | `/analysis/holm/pair_r2r3` | true | gap_closed(R2,R3) vs the 0.5 bar, same machinery; second member of the frozen HE1 rung-pair set (IUT) |
| sec-cascade-dominance | secondary | `/analysis/holm/cascade_dominance` | false | HE2: verifier-gated cascade must beat BOTH the logprob gate AND the gloss-text self-check gate at EVERY pre-registered escalation budget (IUT across budgets: family p = worst budget p; per P1 HE2 kill text) |
| sec-prm | secondary | `/analysis/holm/prm_beaten` | true | HC3: kernel verifier vs trained-PRM arm at matched FLOPs, one-sided paired bootstrap, minimum effect h=0.2; PRM-parity as a positive claim requires TOST at the same margin |
| sec-external-slice | secondary | `/analysis/holm/external_slice` | false | RT-7a ecological-validity secondary on the externally-authored slice; Holm within F-secondary(f2) |
| sec-seed-sign | secondary | `/analysis/seed_sign_consistent` | true | C-4 robustness gate: >=4/5 sampling seeds same-direction verifier lift (pre-declared secondary, not a test) |
| sec-iface-instrument | secondary | `/gates/instrument_valid` | true | P10 extraction-failure instrument gate, success-direction rendering: extraction-success Wilson-LB must clear 0.90 at n>=300 labelled outputs per rung (equivalently failure Wilson-LB <= 0.10) |

Raw analysis-output document (ALL derived statistics live here and nowhere else, G-4):

```json
{
  "analysis": {
    "beats_gloss_self_verify": true,
    "beats_text_null": true,
    "best_retry_budget": 4,
    "competitor_closes_asmuch": true,
    "cost_ratio_vs_S": 0.43272024049088587,
    "effect_ci_high": -23.080000000000037,
    "effect_ci_low": -135.5999999999997,
    "effect_size": -40.133333333333205,
    "gap_below_half": true,
    "gap_closed_fraction_R1R2": -40.133333333333205,
    "gap_closed_fraction_R2R3": 2.732432432432447,
    "holm": {
      "beats_gloss_self_verify": true,
      "beats_gloss_self_verify_p": 9.999000099990002e-05,
      "beats_text_null": true,
      "beats_text_null_p": 9.999000099990002e-05,
      "cascade_dominance": false,
      "cascade_dominance_p": 0.04709529047095291,
      "external_slice": false,
      "external_slice_p": 1.0,
      "pair_r2r3": true,
      "pair_r2r3_p": 9.999000099990002e-05,
      "prm_beaten": true,
      "prm_beaten_p": 9.999000099990002e-05
    },
    "n_items": 500,
    "primary_p": 0.5674071041048214,
    "primary_reject": false,
    "seed_sign_consistent": true,
    "tost_equivalence_pass": false
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

Rungs measured: R1, R2, R3. Scale language licensed: **slope** (>=3 rungs for slope adjectives; 2 for a sign; 1 licenses nothing).

### Extrapolation envelope (verbatim — binding on every citation of this verdict)

> P1 §4b row HE1 (verbatim): Measured range: (135M,360M),(360M,1.7B). Envelope: 3 rungs ⇒ gap-closure-fraction trend to 7B, direction-only; bias stated: the s→S gap itself narrows as S grows. Anchor: Cascade/verification-routing literature measured to GPT-4-class (FrugalGPT-style) licenses mechanism existence, not effect size, above 7B. Row HE2 (verbatim): Measured range: 135M→1.7B cascade. Envelope: Same as HE1; the cascade topology is standard at frontier scale, only the kernel gate's marginal value needs re-measurement. Anchor: Same anchors as HE1. Row HC3 (verbatim): Measured range: 135M–1.7B. Envelope: Relative kernel-vs-PRM verdict extrapolates to ~7B ONLY under the stated assumption that the PRM is held at its measured size; a frontier-scale PRM re-opens the fork. Anchor: PRM literature (process supervision) improves with PRM scale; verdict is indexed to the PRM size class tested.

## Eligible & excluded runs

87 eligible final run(s).
Excluded: none.

## Audit

State: N/A

## Deviations & amendments

- amendment 1 (see registry/amendments/f2/)
- amendment 2 (see registry/amendments/f2/)
- amendment 3 (see registry/amendments/f2/)
- amendment 4 (see registry/amendments/f2/)
- amendment 5 (see registry/amendments/f2/)
- amendment 6 (see registry/amendments/f2/)

Pre-freeze correction notes on this record (lawful only before sign-off + before any final-phase run; they precede the freeze whose hash is above):
- registry/corrections/f2/1-prefreeze-correction.json

---
### Non-binding commentary (does not and cannot alter the verdict above)

(none)
