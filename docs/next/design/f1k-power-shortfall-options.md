# F1-K power/inventory shortfall — options (GPT-5.6 overflow analysis, coordinator-transcribed)

> Produced by GPT-5.6 (codex, xhigh) as Fable-overflow (all Fable lanes were session-limited/capped),
> transcribed verbatim by the coordinator. Single-model; a Fable cross-check is available on request
> before the maintainer decides. Evidence: data/f1k-eval-v1/coverage-report.json (concept_universe_bound
> =54, n_clusters_realized=49, clusters_with_m_ge_8=46), poc/glm52-probe/f1k-harness/corpora/ (bd
> kernel-of-truth-lyvi), registry/experiments/f1k.json (ASM-2271: C>=65 each m>=8 at n=1440).

# F1-K power/inventory shortfall options

## Decision frame

The frozen F1-K record cannot run as written. Its hard pre-run gate requires at least 65 concept clusters, each with at least eight test items, at \(n=1{,}440\). The pinned `kernel-v0` contains only 54 concepts; the built corpus realizes 49 clusters, of which 46 have \(m\ge8\). This is the registered coverage-vs-power return path, not a result about the kernel or KaE intervention.

Two distinctions matter:

- Statistical validity is not the same as power. Reducing the cluster count does not invalidate the cluster sign-flip test, provided the registered cluster independence and sign-symmetry assumptions hold; it does reduce sensitivity.
- A C=49 run cannot remain a confirmatory run under the current frozen record. It must either be explicitly exploratory or be governed by a successor/re-freeze.

## Option 1 power calculation: run at C=49

The registered Gaussian planning model uses per-item paired-difference variance/discordance \(\delta=0.10\), ICC \(\rho_U=0.10\), and an unweighted mean of cluster means.

For equal cluster sizes:

\[
SE^2=\frac{\delta[1+(m-1)\rho]}{n}.
\]

At \(C=49,\ n=1{,}440,\ \bar m=29.39\):

- \(SE=1.63\) accuracy points.
- Gaussian one-sided significance boundary: \(1.645SE=2.69\) points, so the registered +3-point floor binds.
- Test-alone 80% MDE: \(2.487SE=4.06\) points.
- Joint-rule 80% MDE: \(3+0.842SE=4.37\) points.
- Approximate joint power at the +3-point SEOI: 50%.
- Approximate joint power at the frozen \(\mu^*=4.09\) points: 74.8%.

That balanced calculation is optimistic for the realized corpus. Its cluster sizes include \(m=1,1,2\), and clusters receive equal weight. Extending the same planning model to unequal sizes gives:

\[
SE^2=\frac{\delta}{C^2}
\sum_{c=1}^{C}\left[\rho+\frac{1-\rho}{m_c}\right].
\]

Using the full realized 49-cluster size vector:

- \(SE=1.90\) points.
- Gaussian significance boundary: \(1.645SE=3.12\) points. Significance, rather than the nominal +3 floor, now binds.
- Joint-rule 80% MDE: approximately **4.72 points**.
- Approximate joint power at a true +3-point effect: **47.4%**.
- Approximate joint power at the frozen \(\mu^*=4.09\): **69.5%**.

For comparison, the registered C=65 balanced floor geometry gives \(SE=1.47\), joint MDE \(=4.24\), and about 77.1% power at \(\mu^*=4.09\). Thus the actual C=49 geometry produces:

- about **29% higher SE**;
- a **0.48-point / 11% larger joint MDE**;
- about **7.6 percentage points less power at +4.09**.

Against the best-planning C=96 geometry, the realized MDE rises from 4.09 to 4.72 and power at +4.09 falls from about 80% to 69.5%.

These are Gaussian planning approximations, not exact permutation-test power. The frozen C=96 Monte Carlo result cannot be carried over. A successor would need to rerun the registered 10,000-simulation exact sign-flip power procedure using the actual cluster-size vector. K-2 also needs its own re-powering because an F1-K PASS requires both K-1 and K-2.

An honest non-fire caveat would be:

> At the realized 49-cluster geometry and planning \(\rho_U=0.10\), the experiment had approximately 80% joint power only for effects of at least 4.72 accuracy points and approximately 47% power at the registered +3-point SEOI. A non-fire therefore does not rule out effects between +3 and approximately +4.7 points.

A positive result satisfying both the exact p-value and +3-point rule remains statistically interpretable under the registered assumptions, but only as a result of a disclosed lower-power successor and only over this 49-concept instrument.

## Comparison

| Option | Mechanism | Realized power | Validity | Cost | Effort | What it licenses |
|---|---|---|---|---|---|---|
| **1. Accept reduced power** | Run the existing 1,440-item instrument with all 49 realized clusters, accepting three clusters below \(m=8\). | Balanced approximation: MDE 4.37, power at +4.09 74.8%. Actual unequal geometry: **MDE 4.72, power at +3 47.4%, power at +4.09 69.5%**. | The sign-flip test remains type-I valid under cluster independence and sign-symmetry. Fewer/unequal clusters weaken power, not that validity. The BCa fallback has less comfortable finite-cluster calibration. The current frozen gate nevertheless prohibits the run. | Main execution remains approximately the registered ≤$149 campaign; fewer carrier slots may slightly reduce construction, while test \(n\) and arms remain unchanged. | Low additional data work; normal carrier, tokenizer, pilot, and run effort remains. Confirmatory use also requires Option 3. | Without a successor: exploratory/descriptive only. With a successor: a positive K-1/K-2 result can license the existing model/box/corpus-scoped ladder wording; a non-fire carries the 4.72-point caveat. |
| **2a. Extend via the 191k large-kernel track** | Select a new concept universe from the 191,301-record typed core, create F1-K-ready explications and dictionary controls, align surfaces, rebuild triggers/eval, construct new carriers and derangements, and freeze a new experiment. | Can restore or exceed C=65 if at least 65 concepts realize \(m\ge8\). Current data require at least **19 additional qualifying clusters** beyond the present 46. Power depends on the new realized size vector and must be recalculated. | Potentially strongest design if selection, alignment, power, and all pins are fixed before model outcomes. It is a **different kernel/population**, not an extension of the frozen kernel-v0 result. The 191k core is a candidate pool, not 191k ready-made F1-K explications or eval clusters. | Main test spend can remain similar at \(n=1{,}440\), but concept preparation, alignment, coverage screening, carrier construction, and audits are additional and currently unpriced. Building carriers for all 191k would be unnecessary; a preselected subset is required. | High. New corpus design, human/semantic review, carrier construction, driver manifests, power simulation, successor registration, and re-freeze. | If fully re-frozen and powered, the same ladder claims over the selected large-kernel concept population. It does not license a verdict about kernel-v0 or the entire 191k store. |
| **2b. Add more evaluation data only** | Add or replace QA sources to increase items for existing kernel-v0 concepts and rebalance sparse clusters. | Cannot reach C=65: the cluster count remains bounded by 54 kernel concepts. Perfectly realizing every concept would still be 11 clusters short. It could improve balance and raise the three sparse clusters above eight, but not satisfy the gate. | Valid as a corpus improvement, subject to new source/template/population freezes. It does not repair the registered cluster-count shortfall by itself. | Low-to-medium data acquisition, licensing, filtering, and validation cost; model test cost remains similar. | Medium. New dataset pins, trigger filtering, split reconstruction, contamination checks, and corpus re-freeze. | Alone, no registered F1-K verdict. It licenses only improved within-concept coverage/adequacy. It becomes useful when combined with a larger kernel universe. |
| **3. Amend C≥65 to approximately C≥49** | Create a successor record, re-power, change the hard-coded analysis gate, re-pin the analysis/corpora, and freeze before any carrier/pilot/test outcomes. | Same realized power as Option 1. The exact threshold must be stated carefully: “C≥49 each \(m\ge8\)” still fails because only 46 qualify. The successor must specify either all 49 with unequal-size power or 46 eligible clusters under a different analysis population. | Statistical test validity can remain intact. The registered power guarantee is explicitly weakened. Relaxing a gate after observing inventory creates a garden-of-forking-paths concern, even though treatment outcomes have not been observed. A transparent successor mitigates but does not erase this. | Same model-run cost as Option 1, plus negligible CPU simulation and governance work. | Medium. Re-power K-1/K-2, rerun exact-test MC, revise validation constants and pins, document supersession, and re-freeze. | Only the successor’s claims—not a PASS under the original frozen record. Positive claims remain narrowly scoped; negative findings require the lower-power caveat. |
| **4. Accept F1-K as inventory-limited** | Exercise the registered pre-run return and record an adequacy stop analogous to E0. Preserve the built corpus and generator as successor inputs. | No intervention test and therefore no treatment-effect power claim. The measured adequacy fact is 49 realized/46 qualified clusters against 65 required. | Cleanest adherence to the frozen design. It avoids converting a failed adequacy gate into a kernel outcome. | No further model/prefill spend; only recording and handoff effort. | Low. | Licenses only: “The pinned 54-concept kernel and frozen known-concept QA construction cannot supply the registered cluster inventory.” It licenses no kernel, KaE, correctness, efficiency, PASS, FAIL, or NULL verdict. |

## Model-dependent build gaps

**Realized carriers:** This is principally a planned construction/run-time step, not an unexpected statistical blocker. The carrier tables are mean differences of GLM-5.2 hidden states and therefore require a colibri forward-pass construction run. Under the frozen ordering they are produced after the complete generator manifest (A) and committed as B0 before the pilot. Operationally they are blocked now because the power-gate maintainer decision precedes further spend. They should not be generated merely to investigate an already-known inventory failure.

**Tokenizer-derived manifest fields:** These are also a planned bring-up derivation rather than a conceptual blocker. `template_tokens`, `label_token_ids`, token-level spans, and `d3_template_tokens` are deterministic functions of the frozen text corpus and pinned GLM-5.2 tokenizer. However, they are a current driver-readiness blocker: the driver cannot run until the tokenizer step is implemented or materialized, single-token labels and span mappings validate, and the resulting eval corpus is re-pinned before addendum (6). A failed single-token or span check would become an instrument/scoring blocker; successful derivation is routine run preparation.

## RECOMMENDATION — MAINTAINER DECISION

**Recommend Option 4 for the frozen F1-K record: record an inventory-limited adequacy stop, with no kernel or programme verdict.**

This follows the experiment’s pre-registered return path, avoids weakening a gate to match the realized inventory, and preserves the distinction between “the intervention failed” and “the instrument could not meet its registered information requirement.” The current corpus and generator remain valuable successor assets.

If the F1-K scientific question remains a maintainer priority, the strongest successor is Option 2a combined with 2b: select a benchmark-blind, reviewed subset from the larger-kernel track with headroom above 65 qualifying concepts, build corresponding evaluation coverage, and freeze a new power analysis before model outcomes. Option 3 is a defensible lower-cost fallback only if the maintainer explicitly accepts an approximately 4.72-point MDE, the reduced negative-result value, and the post-inventory gate-relaxation risk.

This recommendation concerns the disposition of this frozen experiment only; it does not decide the programme’s fate.
