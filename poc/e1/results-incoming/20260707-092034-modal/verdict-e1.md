# E1 verdict

**Evaluated concept set (Amendment A1): 52 of 54 vocab concept tokens — excluded by policy `a1-hybrid` (sha `e13dc838…`): kind, lost.**

Pre-registered criteria (docs/poc-design.md, quoted verbatim):
- **Primary:** "kernel-frozen > shuffled-kernel-frozen, paired permutation across 5 paired seeds, p<0.05, single look: kernel at the 50%-token checkpoint vs shuffled at the 100%-token endpoint"
- **Kill:** "null" requires the pre-registered smallest-effect-size-of-interest (Cohen's d = 0.5 on the primary endpoint) excluded by an equivalence bound (TOST), not mere non-significance
- **Circularity guard:** "every metric also evaluated on the untrained step-0 kernel-frozen model; trained success requires beating the step-0 baseline"
- **PPL rule:** "if concept-token PPL saturates within 2% across all arms it is declared uninformative, pre-registered"
- **Secondary:** "Kernel > random-frozen is secondary (Holm-corrected), demoted per BLOCKER 2"

## Verdict: INCONCLUSIVE

primary p = 0.8750 >= 0.05 but TOST does NOT exclude d = 0.5 — neither a pass nor a pre-registered null ("null" requires the pre-registered smallest-effect-size-of-interest (Cohen's d = 0.5 on the primary endpoint) excluded by an equivalence bound (TOST), not mere non-significance)

| quantity | value |
|---|---|
| kernel@50% held-out cloze (per seed) | 0.0208, 0.0339, 0.0208, 0.0234, 0.0234 |
| shuffled@100% held-out cloze (per seed) | 0.0365, 0.0208, 0.0339, 0.0286, 0.0260 |
| paired mean diff | -0.0047 |
| one-sided exact permutation p | 0.8750 (min attainable 0.0312) |
| TOST equivalent (d = 0.5) | False (pLower 0.4303, pUpper 0.0549) |
| step-0 kernel cloze mean | 0.0193 |
| beats step-0 (50% / 100%) | False / False |
| concept-slice PPL spread across arms | 81.62% (saturated: False) |

## Secondaries (Holm-corrected, one-sided)

| contrast | mean diff | p | p (Holm) | reject |
|---|---|---|---|---|
| kernel100_vs_random100_cloze | -0.0010 | 0.6250 | 1.0000 | False |
| kernel100_vs_shuffled100_cloze | -0.0021 | 0.6875 | 1.0000 | False |
| kernel100_vs_trainable100_cloze | -0.0104 | 0.9375 | 1.0000 | False |
| kernel100_vs_kernelInit100_cloze | -0.0172 | 0.9688 | 1.0000 | False |
| kernel100_vs_shuffled100_probe | -0.0176 | 0.9688 | 1.0000 | False |

Concept-slice PPL by arm: {"kernel-frozen": 28.4163, "kernel-init": 16.5728, "random-frozen": 23.2751, "shuffled-frozen": 30.0992, "trainable": 16.6723}
