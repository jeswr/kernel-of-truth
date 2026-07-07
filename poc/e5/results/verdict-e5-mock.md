# E5 verdict (MOCK — mechanics only, tiny random model)

date: 2026-07-07T12:21:47.504230+00:00  |  mode: MOCK  |  device: cpu  |  model: mock-llama-64
encoder pin: `40e8c8ba4c3d…`  |  gloss pin: `36181f9b6509…`

**Pre-registered spec (docs/poc-design.md E5 rev 2, verbatim):**
> E5 — adapter + shuffled-kernel control (3–6 GPU-h). Rev 2 (MINOR 23): n ≥ 20 nonce concepts; exact permutation test, α=0.05; scoring by a fixed non-LLM rubric (slot-filling accuracy against the nonce's explication) or a leak-checked judge (judge prompt contains no explications). Success: true kernel > shuffled kernel on nonce-concept usage.

**Pre-registered primary (poc/e5/inputs/e5-manifest.json, verbatim):**
> nonce slot-filling accuracy, true-kernel vs shuffled-kernel: per nonce j, d_j = mean over the 5 paired seeds of (acc_true[s,j] - acc_shuffled[s,j]) over that nonce's 5 items; one-sided exact sign-flip permutation over the 24 nonce-level paired differences (statistic = sum_j d_j; full 2^24 enumeration, exact integer-lattice convolution; p includes the observed assignment), alpha = 0.05. Operationalises the spec's "n >= 20 nonce concepts; exact permutation test, alpha=0.05" with the nonce as the permutation unit. Pinned caveat: nonce-level differences share the 5 trained adapter pairs; the seed-level secondary treats the training run as the unit.

**Pre-registered success criterion (verbatim):**
> SUCCESS (spec, verbatim): "true kernel > shuffled kernel on nonce-concept usage" = the primary test rejects at alpha=0.05 with positive mean difference AND the validity gate passed. Non-rejection with the gate passed = NULL (no TOST equivalence bound is pre-registered for E5). Gate failed = INSTRUMENT-INVALID.

## OUTCOME: **MOCK-INSTRUMENT-INVALID**

- Instrument-validity gate: 0/2 seeds beat chance on seen items (need >= 1) => FAILED
  - rule: the TRUE arm must beat chance on the SEEN validity items in >= 4 of 5 seeds (per-seed one-sided exact binomial vs 0.2 over 500 items, p < 0.05); otherwise the run is INSTRUMENT-INVALID (neither success nor null), no primary claim in either direction (the E1 step-0 lesson)
- Primary: mean nonce accuracy diff (true - shuffled) = +0.0125, one-sided exact sign-flip p = 0.328125 (alpha 0.05, n = 24 nonces)
- Secondary (Holm m=1): per-seed mean diffs ['+0.0083', '+0.0167'], p = 0.2500

### Nonce accuracy (5-way forced choice, chance 0.2)
| arm | seed0 | seed1 |
|---|---|---|
| true | 0.1917 | 0.2250 |
| shuffled | 0.1833 | 0.2083 |
| random | 0.2333 | 0.1833 |

### Seen validity accuracy (chance 0.2)
| arm | seed0 | seed1 |
|---|---|---|
| true | 0.0600 | 0.0600 |
| shuffled | 0.0600 | 0.0600 |
| random | 0.0800 | 0.0600 |

### Step-0 (untrained adapter) nonce accuracy — descriptive
| arm | seed0 | seed1 |
|---|---|---|
| true | 0.1417 | 0.1333 |
| shuffled | 0.1417 | 0.1750 |
| random | 0.1417 | 0.1917 |

### Compositional split (descriptive): 6/24 nonces share structure with seen set
- shared: mean diff +0.0333
- novel: mean diff +0.0056

LR selection (Common rule 5): true=0.001, shuffled=0.001, random=0.001

Scope limits (README O6 / Common rule 6) apply; the random arm is descriptive only.
Random-arm nonce accuracies (descriptive): seed0=0.2333, seed1=0.1833
