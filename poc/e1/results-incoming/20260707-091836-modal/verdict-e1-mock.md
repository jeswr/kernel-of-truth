# E1 verdict (MOCK — pipeline check only)

**Evaluated concept set (Amendment A1): 52 of 54 vocab concept tokens — excluded by policy `a1-hybrid` (sha `e13dc838…`): kind, lost.**

Pre-registered criteria (docs/poc-design.md, quoted verbatim):
- **Primary:** "kernel-frozen > shuffled-kernel-frozen, paired permutation across 5 paired seeds, p<0.05, single look: kernel at the 50%-token checkpoint vs shuffled at the 100%-token endpoint"
- **Kill:** "null" requires the pre-registered smallest-effect-size-of-interest (Cohen's d = 0.5 on the primary endpoint) excluded by an equivalence bound (TOST), not mere non-significance
- **Circularity guard:** "every metric also evaluated on the untrained step-0 kernel-frozen model; trained success requires beating the step-0 baseline"
- **PPL rule:** "if concept-token PPL saturates within 2% across all arms it is declared uninformative, pre-registered"
- **Secondary:** "Kernel > random-frozen is secondary (Holm-corrected), demoted per BLOCKER 2"

## Verdict: MOCK RUN — machinery check only, not a result. (INCONCLUSIVE)

primary p = 1.0000 >= 0.05 but TOST does NOT exclude d = 0.5 — neither a pass nor a pre-registered null ("null" requires the pre-registered smallest-effect-size-of-interest (Cohen's d = 0.5 on the primary endpoint) excluded by an equivalence bound (TOST), not mere non-significance)

| quantity | value |
|---|---|
| kernel@50% held-out cloze (per seed) | 0.0156, 0.0469 |
| shuffled@100% held-out cloze (per seed) | 0.0625, 0.1094 |
| paired mean diff | -0.0547 |
| one-sided exact permutation p | 1.0000 (min attainable 0.2500) |
| TOST equivalent (d = 0.5) | False (pLower 0.9498, pUpper 0.0411) |
| step-0 kernel cloze mean | 0.0234 |
| beats step-0 (50% / 100%) | False / True |
| concept-slice PPL spread across arms | 4041.79% (saturated: False) |

## Secondaries (Holm-corrected, one-sided)

| contrast | mean diff | p | p (Holm) | reject |
|---|---|---|---|---|
| kernel100_vs_random100_cloze | 0.0156 | 0.5000 | 1.0000 | False |
| kernel100_vs_shuffled100_probe | 0.0023 | 0.5000 | 1.0000 | False |
| kernel100_vs_shuffled100_cloze | -0.0312 | 0.7500 | 1.0000 | False |
| kernel100_vs_trainable100_cloze | -0.0703 | 1.0000 | 1.0000 | False |
| kernel100_vs_kernelInit100_cloze | -0.0625 | 1.0000 | 1.0000 | False |

Concept-slice PPL by arm: {"kernel-frozen": 696.401, "kernel-init": 17.8261, "random-frozen": 577.5542, "shuffled-frozen": 723.5503, "trainable": 17.4695}
