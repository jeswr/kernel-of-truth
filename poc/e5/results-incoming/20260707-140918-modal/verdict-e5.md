# E5 verdict

date: 2026-07-07T14:09:12.809594+00:00  |  mode: FULL  |  device: cuda  |  model: HuggingFaceTB/SmolLM2-135M
encoder pin: `40e8c8ba4c3d…`  |  gloss pin: `36181f9b6509…`

**Pre-registered spec (docs/poc-design.md E5 rev 2, verbatim):**
> E5 — adapter + shuffled-kernel control (3–6 GPU-h). Rev 2 (MINOR 23): n ≥ 20 nonce concepts; exact permutation test, α=0.05; scoring by a fixed non-LLM rubric (slot-filling accuracy against the nonce's explication) or a leak-checked judge (judge prompt contains no explications). Success: true kernel > shuffled kernel on nonce-concept usage.

**Pre-registered primary (poc/e5/inputs/e5-manifest.json, verbatim):**
> nonce slot-filling accuracy, true-kernel vs shuffled-kernel: per nonce j, d_j = mean over the 5 paired seeds of (acc_true[s,j] - acc_shuffled[s,j]) over that nonce's 5 items; one-sided exact sign-flip permutation over the 24 nonce-level paired differences (statistic = sum_j d_j; full 2^24 enumeration, exact integer-lattice convolution; p includes the observed assignment), alpha = 0.05. Operationalises the spec's "n >= 20 nonce concepts; exact permutation test, alpha=0.05" with the nonce as the permutation unit. Pinned caveat: nonce-level differences share the 5 trained adapter pairs; the seed-level secondary treats the training run as the unit.

**Pre-registered success criterion (verbatim):**
> SUCCESS (spec, verbatim): "true kernel > shuffled kernel on nonce-concept usage" = the primary test rejects at alpha=0.05 with positive mean difference AND the validity gate passed. Non-rejection with the gate passed = NULL (no TOST equivalence bound is pre-registered for E5). Gate failed = INSTRUMENT-INVALID.

## OUTCOME: **PASS**

- Instrument-validity gate: 5/5 seeds beat chance on seen items (need >= 4) => PASSED
  - rule: the TRUE arm must beat chance on the SEEN validity items in >= 4 of 5 seeds (per-seed one-sided exact binomial vs 0.2 over 500 items, p < 0.05); otherwise the run is INSTRUMENT-INVALID (neither success nor null), no primary claim in either direction (the E1 step-0 lesson)
- Primary: mean nonce accuracy diff (true - shuffled) = +0.2850, one-sided exact sign-flip p = 0.000000 (alpha 0.05, n = 24 nonces)
- Secondary (Holm m=1): per-seed mean diffs ['+0.3167', '+0.2500', '+0.2250', '+0.3083', '+0.3250'], p = 0.0312

### Nonce accuracy (5-way forced choice, chance 0.2)
| arm | seed0 | seed1 | seed2 | seed3 | seed4 |
|---|---|---|---|---|---|
| true | 0.4750 | 0.4583 | 0.4250 | 0.4583 | 0.5083 |
| shuffled | 0.1583 | 0.2083 | 0.2000 | 0.1500 | 0.1833 |
| random | 0.2167 | 0.1917 | 0.2583 | 0.1583 | 0.2000 |

### Seen validity accuracy (chance 0.2)
| arm | seed0 | seed1 | seed2 | seed3 | seed4 |
|---|---|---|---|---|---|
| true | 0.7700 | 0.7980 | 0.8020 | 0.7600 | 0.8220 |
| shuffled | 0.6500 | 0.7080 | 0.6640 | 0.7040 | 0.7000 |
| random | 0.9140 | 0.9040 | 0.9060 | 0.9080 | 0.8860 |

### Step-0 (untrained adapter) nonce accuracy — descriptive
| arm | seed0 | seed1 | seed2 | seed3 | seed4 |
|---|---|---|---|---|---|
| true | 0.1833 | 0.1833 | 0.1750 | 0.1833 | 0.1750 |
| shuffled | 0.1750 | 0.1833 | 0.1667 | 0.1917 | 0.1833 |
| random | 0.1917 | 0.1667 | 0.1750 | 0.1750 | 0.1917 |

### Compositional split (descriptive): 6/24 nonces share structure with seen set
- shared: mean diff +0.4733
- novel: mean diff +0.2222

LR selection (Common rule 5): true=0.003, shuffled=0.003, random=0.003

Scope limits (README O6 / Common rule 6) apply; the random arm is descriptive only.
Random-arm nonce accuracies (descriptive): seed0=0.2167, seed1=0.1917, seed2=0.2583, seed3=0.1583, seed4=0.2000
