# f2b-replicate verdict — PASS

computed: 2026-07-09T11:57:31Z | report-gen/1 | analysis 711ac322
frozen prereg: 21d40177 (frozen 2026-07-09T10:52:06Z) | amendments applied: none
encoder pin: 40e8c8ba | corpus pins: d-ext:0c5306bb, d-qa:ad756a7e, d-qa-r:0d548bf1, d-xif:8c9aded6, kernel-v0:8209cada, molecules-v0:69f0c8a3 | log tail: b651682e

## Pre-registered statement (from the frozen record)

**Hypotheses:** HE1 (fresh-item replication, absolute non-inferiority form: the frozen F2 gap_closed primary died on a degenerate denominator; this primary has no denominator), H-STRUCT (new, load-bearing): the F2 verifier lift is kernel-CONTENT-specific, not retry-against-any-oracle STRUCTURE — operationalised by the shuffled-kernel-verify-retry arm (seed-pinned derangement of the record->concept map at identical retry topology and cost); motivated by the oracle-leakage hypothesis: the verifier accepts iff the answer string-equals the canonical record, and D-QA gold answers were DEFINED by that same equality (explains F2's 272/500-up, 0-down flip profile), HC3 (kernel verifier vs trained PRM at matched FLOPs, this PRM size class), RT-2 (kernel verifier vs gloss-text self-verify + retry at matched budget) — f2b-replicate — fresh-item replication of the F2 verifier-offload signal with oracle-structure controls: absolute non-inferiority primary (135M + kernel-verify vs 1.7B-alone, NO gap denominator), shuffled-record verifier null (load-bearing), separation gate, fixed external-slice instrument; architecture-advisor RIGHT-SIZED design (250 items, 3 seeds, fixed k=4, single A100, gold-oracle dropped) implemented faithfully; supersedes-in-spirit f2 (the F2 FAIL verdict stands untouched)
prereg doc: docs/research-plan/01-hypotheses-experiments.md (sha256 71768a9c)

## Pre-registered kill criterion (verbatim) — rendered beside EVERY verdict

> Architecture-advisor RIGHT-SIZED design for f2b-REPLICATE (verbatim kills; fixed pre-registered k=4, 250 items, 3 seeds): (a) primary fails => the headline is dead on fresh items; (b) SHUFFLED-verify recovers >= 30% of true-verify's lift-over-alone (point estimate) => the lift is retry-against-any-oracle STRUCTURE not kernel CONTENT, and the kernel-specific claim DIES even at high accuracy; (c) gloss-self-verify or the trained PRM closes as much lift at <= matched FLOPs/query (F0 ledger, point estimates) => Law-2 / commodity-verification kill. Nulls require TOST (equivalence to R3-alone at margin h=0.2). Inherited context (P1 §3 HE1 + P7 RT-2): the kernel arm cannot PASS without beating the gloss-text self-verify+retry arm at matched budget and the passive text null. The gold-oracle-retry diagnostic ceiling is DROPPED in the right-size (it read the answer key and was non-deployable; it never bore any kill or PASS).

## OUTCOME: **PASS**

Fired rule 2 (declares `PASS`): `{"a":{"metric":"/analysis/primary_reject"},"b":{"a":{"metric":"/analysis/holm/beats_gloss_self_verify"},"b":{"a":{"metric":"/analysis/holm/beats_text_null"},"b":{"metric":"/analysis/holm/shuffled_low_recovery"},"op":"and"},"op":"and"},"op":"and"}`
evaluated over analysis-output.json (sha256 90497614).

## Endpoints (full pre-declared metric vector — all of them)

| endpoint | role | metric | value | pre-registered test |
|---|---|---|---|---|
| primary | primary | `/analysis/effect_size` | 0.15066666666666662 | ABSOLUTE non-inferiority at margin 0 (NO denominator — fixes the degenerate-ratio failure that killed the F2 primary): effect_size = acc(135M + kernel-verify-retry, the single pre-registered retry budget k=4 (retry_sweep=[4]; no in-bootstrap k selection)) - acc(1.7B-alone); paired item BCa bootstrap (B=10000, PRNG seed 20260709), one-sided alpha=0.05; reject iff the one-sided 95% BCa lower bound >= 0. Accuracies are seed-averaged per-item means on the fresh kernel-covered d-qa-r slice (P8 §1.2/§1.7 discipline) |
| sec-separation-gate | secondary | `/gates/separation_valid` | true | INSTRUMENT gate, pre-declared (not a hypothesis test, not a Holm member): acc(R3-alone) - acc(R1-alone) >= 0.10 (3-seed mean) AND one-sided 95% BCa lower bound > 0; on failure the ratio secondaries are INSTRUMENT-INVALID (the absolute primary still reads) |
| sec-gap-r1r3-gt-one | secondary | `/analysis/holm/gap_r1r3_gt_one` | true | gap_closed(R1,R3) one-sided 95% BCa lower bound > 1.0 ('the 135M+verifier does not just close the gap, it overshoots it'); at the fixed pre-registered k=4; Holm within F-secondary(f2b); CONDITIONAL on the separation gate (else INSTRUMENT-INVALID, excluded from the family before any p comparison) |
| sec-gap-r1r3-gt-half | secondary | `/analysis/holm/gap_r1r3_gt_half` | true | gap_closed(R1,R3) one-sided 95% BCa lower bound > 0.5 (the F2 kill-bar analogue on the fresh pairing); at the fixed pre-registered k=4; same conditionality as sec-gap-r1r3-gt-one |
| sec-beats-gloss-self-verify | secondary | `/analysis/holm/beats_gloss_self_verify` | true | one-sided paired bootstrap vs gloss-text self-verify+retry at matched budget, BOTH arms at the fixed pre-registered k=4 (RT-2: the kernel arm cannot PASS without beating this); Holm within F-secondary(f2b) at alpha=0.05 |
| sec-beats-prm | secondary | `/analysis/holm/prm_beaten` | true | HC3: kernel verifier vs trained-PRM arm at matched FLOPs (F0 ledger), one-sided paired bootstrap; Holm within F-secondary(f2b); PRM-parity as a positive claim requires TOST at margin h=0.2 |
| sec-beats-text-null | secondary | `/analysis/holm/beats_text_null` | true | one-sided paired bootstrap vs the kernel-as-text arm (Law-2 passive text null); Holm within F-secondary(f2b) |
| sec-shuffled-low-recovery | secondary | `/analysis/holm/shuffled_low_recovery` | true | E9-defl semantics-control analogue, THE load-bearing new secondary: recovery = (acc(shuffled-verify, best k) - acc(R1-alone)) / (acc(kernel-verify, best k) - acc(R1-alone)), each at the fixed pre-registered k=4; passes iff the one-sided 95% BCa upper bound of recovery < 0.30; Holm within F-secondary(f2b). The KILL (clause b) fires on the POINT estimate >= 0.30 regardless of this test |
| sec-seed-sign | secondary | `/analysis/seed_sign_consistent` | true | C-4 robustness gate: >= ceil(0.8 * n_seeds) = 3/3 sampling seeds same-direction verifier lift over R1-alone (the pinned analysis rule at 3 seeds; STRICTER than the advisor 2/3 floor — a conservative, reported-only secondary that does NOT gate the PASS) |
| sec-iface-instrument | secondary | `/gates/instrument_valid` | true | P10 extraction-failure instrument gate at the verifier host rung (R1), success-direction rendering: extraction-success Wilson-LB must clear 0.90 at n>=300 labelled outputs (equivalently failure Wilson-LB <= 0.10); measured by mechanical re-verification of the pinned d-xif set |

Raw analysis-output document (ALL derived statistics live here and nowhere else, G-4):

```json
{
  "analysis": {
    "acc_alone_r1": 0.492,
    "acc_alone_r3": 0.6,
    "acc_gloss_self_verify_bestk": 0.4893333333333334,
    "acc_prm": 0.5266666666666665,
    "acc_shuffled_bestk": 0.48666666666666664,
    "acc_text_null": 0.492,
    "acc_verify_bestk": 0.7506666666666666,
    "beats_gloss_self_verify": true,
    "beats_text_null": true,
    "best_retry_budget": 4,
    "competitor_closes_asmuch": false,
    "cost_ratio_vs_R3": 0.10309731202870343,
    "effect_ci_high": 0.20266666666666633,
    "effect_ci_low": 0.09733333333333316,
    "effect_size": 0.15066666666666662,
    "gap_ci_high": 3.759259259259267,
    "gap_ci_low": 1.6666666666666696,
    "gap_closed_fraction_r1r3": 2.3950617283950613,
    "gap_lower_onesided95": 1.7619047619047612,
    "gold_oracle_acc_bestk": null,
    "gold_oracle_gap": null,
    "gold_oracle_gap_ci_high": null,
    "gold_oracle_gap_ci_low": null,
    "holm": {
      "beats_gloss_self_verify": true,
      "beats_gloss_self_verify_p": 9.999000099990002e-05,
      "beats_text_null": true,
      "beats_text_null_p": 9.999000099990002e-05,
      "gap_r1r3_gt_half": true,
      "gap_r1r3_gt_half_p": 9.999000099990002e-05,
      "gap_r1r3_gt_one": true,
      "gap_r1r3_gt_one_p": 9.999000099990002e-05,
      "prm_beaten": true,
      "prm_beaten_p": 9.999000099990002e-05,
      "shuffled_low_recovery": true,
      "shuffled_low_recovery_p": 9.999000099990002e-05
    },
    "n_items": 250,
    "primary_lower_onesided95": 0.10533333333333361,
    "primary_p": 9.999000099990002e-05,
    "primary_reject": true,
    "ratio_secondaries_valid": true,
    "recovery_defined_fraction": 1.0,
    "seed_sign_consistent": true,
    "separation_gap": 0.10799999999999998,
    "separation_lower_onesided95": 0.07199999999999995,
    "shuffled_recovers_geq_30": false,
    "shuffled_recovery_fraction": -0.020618556701031025,
    "shuffled_recovery_ub95": 0.10762331838564983,
    "tost_equivalence_pass": false
  },
  "gates": {
    "instrument_valid": true,
    "separation_valid": true
  }
}
```

## Coverage disclosure (mandatory)

Kernel-expressibility coverage (M0b): **0.3542** at rung **molecules-v0** — a corpus-indexed, rung-indexed, kernel-state-indexed measurement, NOT a general ("natural") coverage property of the kernel.

Full measured scope: census by experiment `m0b` (frozen 2026-07-08T16:45:06Z) over exactly its pinned inputs — kernel-v0:8209cada, lexical-wn31:5e76def8, molecules-v0:69f0c8a3, task-family-tinystories:b6bcc9f6 (encoder pin 40e8c8ba) — i.e. that one pinned corpus against the incomplete kernel instance as pinned at that freeze; coverage is re-measured as the kernel grows (coverage-growth curve, P7 RT-11/§10).

No-extrapolation envelope on this number (per the m0b verdict envelope and the assumption register, registry/assumptions.jsonl): it extrapolates to NO other corpus, rung, or kernel state. Every claim above is bounded to this covered slice, within exactly that scope.

## Scale

Rungs measured: R1, R3. Scale language licensed: **sign-only** (>=3 rungs for slope adjectives; 2 for a sign; 1 licenses nothing).

### Extrapolation envelope (verbatim — binding on every citation of this verdict)

> Advisor scope, binding on any PASS: 2 host rungs (135M, 1.7B) license a SIGN, not a slope; every claim is scoped to <=1.7B hosts, the kernel-covered SELF-AUTHORED item slice (templated definitional QA over the 108 covered concepts), this PRM size class (1.5B, pinned revision), and an oracle-favourable eval design; the s->S gap itself narrows as S grows, so absolute verifier catch-room shrinks with scale. Coverage disclosure (mandatory): kernel-expressibility coverage 0.3542 at rung molecules-v0 — MEASURED by m0b on one incomplete kernel-v0 instance, NOT general coverage. Inherited P1 §4b HE1 anchors: cascade/verification-routing literature licenses mechanism existence above 7B, never effect size; the HC3 verdict is indexed to the PRM size class tested and a frontier-scale PRM re-opens the fork.

## Eligible & excluded runs

20 eligible final run(s).
Excluded: none.

## Audit

State: CONFIRMED (registry/audits/f2b-replicate/1-gate-a-codex.json)

## Deviations & amendments

None applied to this verdict.

Pre-freeze correction notes on this record (lawful only before sign-off + before any final-phase run; they precede the freeze whose hash is above):
- registry/corrections/f2b-replicate/1-prefreeze-correction.json
- registry/corrections/f2b-replicate/2-prefreeze-correction.json

---
### Non-binding commentary (does not and cannot alter the verdict above)

(none)
