# X1-grounding — results report

Rendered from committed artifacts. Method: PREREG.md (frozen). Reference: Vincent-Lamarre et al. 2016, *The Latent Structure of Dictionaries*.

## Census (stages 1-3)

| quantity | value |
|---|---|
| synsets | 117791 |
| \|V\| (all lemma nodes) | 147478 |
| \|V_sw\| (single-word nodes) | 83253 |
| edges (definer->defined) | 1175680 |
| self-reference tokens removed | 7241 |
| empty cleaned glosses | 0 |
| OOV token occurrences | 9324 |
| undefined nodes (in-deg 0) | 47 |

## Kernel / Core / Satellites and §4.3 corridor gates

| stratum | size | fraction |
|---|---|---|
| Kernel K | 19559 | 0.2349 of V_sw |
| Core | 17324 | 0.8857 of K |
| Satellites | 2235 | |
| Rest | 127919 | |

**2016-shape comparison:** paper found Kernel ~10%, Core = large fraction of Kernel, MinSets ~1%. Here Kernel = 23.5% of V_sw, Core = 88.6% of K.

| §4.3 gate | value | pass |
|---|---|---|
| \|K\|/\|V_sw\| in [0.01,0.40] | 0.2349 | True |
| \|Core\|/\|K\| >= 0.20 | 0.8857 | True |
| Core unique-largest >= 2x | 17324 vs 9 | True |
| cycle-containment | {'kernelMinOutDegreeOk': True, 'restAcyclic': True, 'restToKernelEdges': 0} | True |
| **CONSTRUCTION-ANOMALY** | | False |

## Prime -> node mapping (§5.1, frozen)

Evaluable primes: **51** (coverage gate: OK, min 45). Excluded: 14.

## T2 lemmatization audit (§8)

- population = 689339 resolutions; sample = 100 (seed 7); pipeline = post-stoplist (PREREG §9 Amendment 3, closed-class definer suppression active).
- error rate = **5%** (gate = 10%).
- pre-stoplist audit was 17% (strict) / 12% (function-word); resolved by §9 Amendment 3.
- gate tripped: **False** -> PASS-T2: post-stoplist audit error rate = 5% < 10% gate. nsm_test may proceed. The guardrail is confirmed working in-sample (far->far #87 and not->not #92 both survive as protected prime nodes).

## NSM test — endpoints and verdict (§5.4, §6)

**VERDICT: FAIL**

| statistic | observed | null mean | p | ER |
|---|---|---|---|---|
| T_core | 0.9804 | 0.9705 | 0.58314 | 1.0101948867976314 |
| T_kern | 0.9804 | 0.9747 | 0.73603 | 1.0057953930548742 |

Endpoints: {"E-core": false, "E-kern": false}

Sensitivity null (usage-matched) agrees on E-core direction: True

**Interpretation (flag).** 50/51 primes ARE in the Core (T_core=0.9804; only MAYBE is absent, out-degree 0 — used in no gloss). But the frequency-matched null lands in the Core 97.0% of the time, so ER=1.0101948867976314 and p=0.583: **no enrichment**. The Core spans 88.6% of the Kernel and ~97% of frequency-matched high-out-degree content words, so Core membership is near-universal and carries almost no information — a ceiling/saturation effect, not evidence that primes are absent from the grounding floor. The FAIL is 'no detectable selectivity', decisive under the pre-registered mechanical criteria (E-core fails AND E-kern fails, §6), and independent of the MinSet secondaries.

## Threats (PREREG §8)

T1 WordNet != full dictionary (14 primes excluded, logical/deictic-skewed); T2 lemmatization noise (audited above); T3 word-form not sense; T4 sense-collapse; T5 sampled minimal != minimum FVS; T6 null granularity (usage-matched sensitivity null); T7 analyst d.o.f. (frozen PREREG).

