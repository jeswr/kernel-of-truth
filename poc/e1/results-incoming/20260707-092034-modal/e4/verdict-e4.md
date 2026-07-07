# E4 verdict

**E1 evaluated concept set (Amendment A1): 52 of 54 — excluded by policy (sha `e13dc838…`): kind, lost. E4's candidate set is unaffected (1054-way; the exclusion shrinks E1's evaluated/attested slice only).**

Pre-registered criteria (poc/e4/inputs/holdout-manifest.json `statistics`, quoted verbatim):
- **Primary:** "tier-2 top-1 accuracy over the candidate set, kernel vs shuffled-kernel, one-sided exact paired sign-flip permutation across the 5 paired seeds, alpha = 0.05 (min attainable p = 1/32; Common rule 1 pairing)"
- **Secondary:** "tier-2 top-10 accuracy (same test)"
- **Secondary:** "tier-1 top-1 and top-10 accuracy (same test)"
- **Secondary:** "per-seed one-sided Fisher exact on pooled item counts (tier-2: 50 gloss-items/arm; tier-1: 1055 items/arm), Holm-corrected over seeds"
- **Secondary:** "compositional subsets (shared vs novel): descriptive accuracies, no inferential claim"
- **Control-floor validity:** "the shuffled-kernel arm must sit at empirical chance: pooled tier-2 accuracy inside the exact binomial 95% CI of 1/1054 — otherwise the control itself carries signal and the run is reported as invalid, not as a positive"
- **Advance rule:** "poc-design MAJOR 16: "credible" requires tier-2 success PLUS replication in a second model family; a single tier-1 positive triggers nothing"
- **Training-data rule:** "MAJOR 6: emission training may only consume the gloss file whose sha-256 equals GLOSS-HASH.txt (committed before any training); build_emission.py verifies this and fails closed"

## Verdict: TIER-2 NULL (AT/NEAR CHANCE)

primary p = 0.2500 >= 0.05 — no pre-registered kernel-vs-shuffled advantage on tier-2 top-1 (kill-chain input: "E4 tier-2 at chance")

| quantity | value |
|---|---|
| candidate set | 1054-way (chance top-1 0.000949, top-10 0.009488) |
| tier-2 top-1 kernel (per seed) | 0.0200, 0.0200, 0.0000, 0.0000, 0.0000 |
| tier-2 top-1 shuffled (per seed) | 0.0000, 0.0000, 0.0000, 0.0000, 0.0000 |
| paired mean diff | 0.0080 |
| one-sided exact permutation p | 0.2500 (min attainable 0.0312) |
| control floor (shuffled pooled tier-2) | 0/250 in [0, 1] -> OK |
| kernel pooled tier-2 | 2/250 |
| random-frozen pooled tier-2 (descriptive) | 0/250 |
| gloss OOV rate (recorded at build) | 0.0003376530123777611 |

## Secondaries (paired sign-flip, Holm-corrected)

| contrast | mean diff | p | p (Holm) | reject |
|---|---|---|---|---|
| tier2_top10 | 0.0480 | 0.0312 | 0.0938 | False |
| tier1_top1 | 0.0102 | 0.0312 | 0.0938 | False |
| tier1_top10 | 0.1077 | 0.0312 | 0.0938 | False |

## Fisher exact per seed (pooled items, Holm over seeds)

**tier2:**

| seed | kernel k/n | shuffled k/n | p | p (Holm) | reject |
|---|---|---|---|---|---|
| seed0 | 1/50 | 0/50 | 0.5000 | 1.0000 | False |
| seed1 | 1/50 | 0/50 | 0.5000 | 1.0000 | False |
| seed2 | 0/50 | 0/50 | 1.0000 | 1.0000 | False |
| seed3 | 0/50 | 0/50 | 1.0000 | 1.0000 | False |
| seed4 | 0/50 | 0/50 | 1.0000 | 1.0000 | False |

**tier1:**

| seed | kernel k/n | shuffled k/n | p | p (Holm) | reject |
|---|---|---|---|---|---|
| seed0 | 9/1055 | 2/1055 | 0.0324 | 0.0387 | True |
| seed1 | 17/1055 | 2/1055 | 0.0003 | 0.0010 | True |
| seed2 | 12/1055 | 0/1055 | 0.0002 | 0.0009 | True |
| seed3 | 13/1055 | 0/1055 | 0.0001 | 0.0006 | True |
| seed4 | 8/1055 | 1/1055 | 0.0193 | 0.0387 | True |

## Descriptive (per-arm means over seeds; compositional split)

| arm | tier2 top1 | tier2 top10 | tier1 top1 | tier1 top10 | t2 shared/novel top1 | t1 shared/novel top1 | seen-heldgloss top1 |
|---|---|---|---|---|---|---|---|
| kernel | 0.0080 | 0.0520 | 0.0112 | 0.1137 | 0.0100 / 0.0067 | 0.0121 / 0.0104 | 0.0581 |
| shuffled | 0.0000 | 0.0040 | 0.0009 | 0.0061 | 0.0000 / 0.0000 | 0.0012 / 0.0007 | 0.0046 |
| random | 0.0000 | 0.0000 | 0.0004 | 0.0047 | 0.0000 / 0.0000 | 0.0004 / 0.0004 | 0.0132 |

Compositional subsets are DESCRIPTIVE only (no inferential claim), per the pre-registration. seen-heldgloss top-1 is the task-learned sanity readout (should be far above chance in ALL arms if emission fine-tuning worked).
