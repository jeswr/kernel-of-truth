# E9-defl verdict

date: 2026-07-07T16:23:48.657933+00:00  |  mode: FULL  |  device: cuda  |  model: HuggingFaceTB/SmolLM2-135M

**What this is (poc/e9/README.md J1, verbatim):**
> poc/e9/README.md (NEW pre-registration, 2026-07-07, coordinator-directed): deflationary control kernel on the E5 instrument. NOT poc-design.md E9 (decode-verify vs RAG, phase 2), which remains pre-registered and untouched.

**Question:** Is the kernel's signal specifically the semantic content of the explications, or would ANY consistent structured deterministic vector set do?
**Principle:** The kernel machinery's marginal value over its own deflation is measured, never asserted. (docs/poc-design.md E9 rev 3 sentence; notes/panel-kernel-design-review.md §3.1)

**Pre-registered primary (inputs/e9-manifest.json, verbatim):**
> nonce slot-filling accuracy, true-kernel vs defl-kernel: per nonce j, d_j = mean over the 5 paired seeds of (acc_true[s,j] - acc_defl[s,j]) over that nonce's 5 items; one-sided exact sign-flip permutation over the 24 nonce-level paired differences (statistic = sum_j d_j; full 2^24 enumeration, exact integer-lattice convolution; p includes the observed assignment), alpha = 0.05. This is the marginal value of kernel content over its structural deflation, measured. Pinned caveat: nonce-level differences share the 5 trained adapter pairs; S2 treats the training run as the unit.

**Pre-registered outcome labels (verbatim):**
> gate failed => INSTRUMENT-INVALID; primary rejects => PASS (marginal value of content shown on this instrument); primary non-reject AND S1 rejects => DEFLATED (a semantics-scrambled structured code reproduces the transfer; every external quote of E5 must carry this); primary non-reject AND S1 non-reject => AMBIGUOUS-NULL (no measurable separation; power follow-up filed). All reported verbatim with full tables.

## OUTCOME: **PASS**

- Instrument-validity gate: 5/5 seeds (need >= 4) => PASSED
- Primary (true vs defl): mean diff +0.2617, one-sided exact sign-flip p = 3.8147e-06
- S1 (defl vs shuffled): mean diff +0.0233, p = 0.201904 (Holm 0.201904)
- S2 (seed-level true vs defl): diffs ['+0.2583', '+0.2417', '+0.2333', '+0.2667', '+0.3083'], p = 0.0312 (Holm 0.0625)
- Descriptive true vs shuffled (E5 replication): mean diff +0.2850
- Recovered fraction (defl-shuffled)/(true-shuffled), pooled: 0.0819

### Nonce accuracy (5-way forced choice, chance 0.2)
| arm | seed0 | seed1 | seed2 | seed3 | seed4 |
|---|---|---|---|---|---|
| true | 0.4750 | 0.4583 | 0.4250 | 0.4583 | 0.5083 |
| shuffled | 0.1583 | 0.2083 | 0.2000 | 0.1500 | 0.1833 |
| defl | 0.2167 | 0.2167 | 0.1917 | 0.1917 | 0.2000 |

### Seen validity accuracy (chance 0.2)
| arm | seed0 | seed1 | seed2 | seed3 | seed4 |
|---|---|---|---|---|---|
| true | 0.7700 | 0.7980 | 0.8020 | 0.7600 | 0.8220 |
| shuffled | 0.6500 | 0.7080 | 0.6640 | 0.7040 | 0.7000 |
| defl | 0.7020 | 0.6960 | 0.7360 | 0.6820 | 0.7380 |

### Step-0 (untrained adapter) nonce accuracy — descriptive
| arm | seed0 | seed1 | seed2 | seed3 | seed4 |
|---|---|---|---|---|---|
| true | 0.1833 | 0.1833 | 0.1750 | 0.1833 | 0.1750 |
| shuffled | 0.1750 | 0.1833 | 0.1667 | 0.1917 | 0.1833 |
| defl | 0.1833 | 0.1833 | 0.2000 | 0.1750 | 0.2000 |

### Drift vs committed E5 run (descriptive replication datum)
| arm-seed | E5 nonceAcc | E9 nonceAcc | delta |
|---|---|---|---|
| shuffled-seed0 | 0.1583 | 0.1583 | +0.0000 |
| shuffled-seed1 | 0.2083 | 0.2083 | +0.0000 |
| shuffled-seed2 | 0.2000 | 0.2000 | +0.0000 |
| shuffled-seed3 | 0.1500 | 0.1500 | +0.0000 |
| shuffled-seed4 | 0.1833 | 0.1833 | +0.0000 |
| true-seed0 | 0.4750 | 0.4750 | +0.0000 |
| true-seed1 | 0.4583 | 0.4583 | +0.0000 |
| true-seed2 | 0.4250 | 0.4250 | +0.0000 |
| true-seed3 | 0.4583 | 0.4583 | +0.0000 |
| true-seed4 | 0.5083 | 0.5083 | +0.0000 |

LR selection (Common rule 5): true=0.003, shuffled=0.003, defl=0.003

Scope limits: poc/e5 README O6 verbatim, plus: a PASS shows content-specificity relative to THIS deflation (shape-matched scrambled explications); it does not exclude every conceivable non-semantic channel and does not upgrade any A1 claim.
