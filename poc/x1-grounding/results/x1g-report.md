# X1-grounding — results report

Rendered from committed artifacts. Method: PREREG.md (frozen). Reference: Vincent-Lamarre et al. 2016, *The Latent Structure of Dictionaries*.

## Census (stages 1-3)

| quantity | value |
|---|---|
| synsets | 117791 |
| \|V\| (all lemma nodes) | 147478 |
| \|V_sw\| (single-word nodes) | 83253 |
| edges (definer->defined) | 1405063 |
| self-reference tokens removed | 7279 |
| empty cleaned glosses | 0 |
| OOV token occurrences | 247264 |
| undefined nodes (in-deg 0) | 14 |

## Kernel / Core / Satellites and §4.3 corridor gates

| stratum | size | fraction |
|---|---|---|
| Kernel K | 19617 | 0.2356 of V_sw |
| Core | 17393 | 0.8866 of K |
| Satellites | 2224 | |
| Rest | 127861 | |

**2016-shape comparison:** paper found Kernel ~10%, Core = large fraction of Kernel, MinSets ~1%. Here Kernel = 23.6% of V_sw, Core = 88.7% of K.

| §4.3 gate | value | pass |
|---|---|---|
| \|K\|/\|V_sw\| in [0.01,0.40] | 0.2356 | True |
| \|Core\|/\|K\| >= 0.20 | 0.8866 | True |
| Core unique-largest >= 2x | 17393 vs 9 | True |
| cycle-containment | {'kernelMinOutDegreeOk': True, 'restAcyclic': True, 'restToKernelEdges': 0} | True |
| **CONSTRUCTION-ANOMALY** | | False |

## Prime -> node mapping (§5.1, frozen)

Evaluable primes: **51** (coverage gate: OK, min 45). Excluded: 14.

## T2 lemmatization audit (§8)

- population = 854458 resolutions; sample = 100 (seed 7).
- error rate (strict) = **17%**; function-word-only = 12%; inflection = 5%; gate = 10%.
- gate tripped: **True** -> HALT-T2: audit error rate exceeds the pre-registered 10% ceiling under both the strict reading (17%) and the conservative function-word-only reading (12%). Per PREREG §8 the run halts for a §9 amendment BEFORE nsm_test. nsm_test NOT run.

> A small, enumerable set of closed-class function words that happen to be rare WordNet content-homograph lemmas (in, or, as, by, so, an) survive §2.4's mechanical OOV drop-out and inject high-frequency spurious edges. 'or' alone appears 5x in the 100-sample. §2.4 explicitly PINS 'No stopword list' as the single source-derived lexical filter, so remediation (a minimal closed-class stoplist, or POS-restriction) conflicts with a pinned decision and is a coordinator design call, not a unilateral builder fix.

## NSM test

**Not run.** Held by the T2 audit gate (see above and PREREG §9 Amendment 2). nsm_test and stage-4 MinSets await the coordinator's remediation decision.

## Threats (PREREG §8)

T1 WordNet != full dictionary (14 primes excluded, logical/deictic-skewed); T2 lemmatization noise (audited above); T3 word-form not sense; T4 sense-collapse; T5 sampled minimal != minimum FVS; T6 null granularity (usage-matched sensitivity null); T7 analyst d.o.f. (frozen PREREG).

