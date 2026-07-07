# E1 verdict (MOCK — pipeline check only)

**Evaluated concept set (Amendment A1): 52 of 54 vocab concept tokens — excluded by policy `a1-hybrid` (sha `e13dc838…`): kind, lost.**

Pre-registered criteria (docs/poc-design.md, quoted verbatim):
- **Primary:** "kernel-frozen > shuffled-kernel-frozen, paired permutation across 5 paired seeds, p<0.05, single look: kernel at the 50%-token checkpoint vs shuffled at the 100%-token endpoint"
- **Kill:** "null" requires the pre-registered smallest-effect-size-of-interest (Cohen's d = 0.5 on the primary endpoint) excluded by an equivalence bound (TOST), not mere non-significance
- **Circularity guard:** "every metric also evaluated on the untrained step-0 kernel-frozen model; trained success requires beating the step-0 baseline"
- **PPL rule:** "if concept-token PPL saturates within 2% across all arms it is declared uninformative, pre-registered"
- **Secondary:** "Kernel > random-frozen is secondary (Holm-corrected), demoted per BLOCKER 2"

## Verdict: MOCK RUN — machinery check only, not a result. (INCONCLUSIVE)

primary p = 0.2500 >= 0.05 but TOST does NOT exclude d = 0.5 — neither a pass nor a pre-registered null ("null" requires the pre-registered smallest-effect-size-of-interest (Cohen's d = 0.5 on the primary endpoint) excluded by an equivalence bound (TOST), not mere non-significance)

| quantity | value |
|---|---|
| kernel@50% held-out cloze (per seed) | 0.0305, 0.0244 |
| shuffled@100% held-out cloze (per seed) | 0.0213, 0.0122 |
| paired mean diff | 0.0107 |
| one-sided exact permutation p | 0.2500 (min attainable 0.2500) |
| TOST equivalent (d = 0.5) | False (pLower 0.0411, pUpper 0.9498) |
| step-0 kernel cloze mean | 0.0183 |
| beats step-0 (50% / 100%) | True / True |
| concept-slice PPL spread across arms | 66.77% (saturated: False) |

## Secondaries (Holm-corrected, one-sided)

| contrast | mean diff | p | p (Holm) | reject |
|---|---|---|---|---|
| kernel100_vs_shuffled100_cloze | 0.0076 | 0.2500 | 1.0000 | False |
| kernel100_vs_random100_cloze | 0.0122 | 0.2500 | 1.0000 | False |
| kernel100_vs_trainable100_cloze | -0.0015 | 1.0000 | 1.0000 | False |
| kernel100_vs_kernelInit100_cloze | 0.0000 | 1.0000 | 1.0000 | False |
| kernel100_vs_shuffled100_probe | -0.0139 | 1.0000 | 1.0000 | False |

Concept-slice PPL by arm: {"kernel-frozen": 1591.5441, "kernel-init": 998.3812, "random-frozen": 1665.0061, "shuffled-frozen": 1658.0213, "trainable": 1006.0549}
