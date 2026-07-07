# E4 verdict (MOCK — pipeline check only)

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

## Verdict: MOCK RUN — machinery check only, not a result. (TIER-2 NULL (AT/NEAR CHANCE))

primary p = 1.0000 >= 0.05 — no pre-registered kernel-vs-shuffled advantage on tier-2 top-1 (kill-chain input: "E4 tier-2 at chance")

| quantity | value |
|---|---|
| candidate set | 1054-way (chance top-1 0.000949, top-10 0.009488) |
| tier-2 top-1 kernel (per seed) | 0.0000, 0.0000 |
| tier-2 top-1 shuffled (per seed) | 0.0000, 0.0000 |
| paired mean diff | 0.0000 |
| one-sided exact permutation p | 1.0000 (min attainable 0.2500) |
| control floor (shuffled pooled tier-2) | 0/100 in [0, 1] -> OK |
| kernel pooled tier-2 | 0/100 |
| random-frozen pooled tier-2 (descriptive) | 0/100 |
| gloss OOV rate (recorded at build) | 0.1400592416251086 |

## Secondaries (paired sign-flip, Holm-corrected)

| contrast | mean diff | p | p (Holm) | reject |
|---|---|---|---|---|
| tier1_top1 | 0.0200 | 0.5000 | 1.0000 | False |
| tier1_top10 | 0.0500 | 0.5000 | 1.0000 | False |
| tier2_top10 | 0.0000 | 1.0000 | 1.0000 | False |

## Fisher exact per seed (pooled items, Holm over seeds)

**tier2:**

| seed | kernel k/n | shuffled k/n | p | p (Holm) | reject |
|---|---|---|---|---|---|
| seed0 | 0/50 | 0/50 | 1.0000 | 1.0000 | False |
| seed1 | 0/50 | 0/50 | 1.0000 | 1.0000 | False |

**tier1:**

| seed | kernel k/n | shuffled k/n | p | p (Holm) | reject |
|---|---|---|---|---|---|
| seed0 | 2/50 | 0/50 | 0.2475 | 0.4949 | False |
| seed1 | 0/50 | 0/50 | 1.0000 | 1.0000 | False |

## Descriptive (per-arm means over seeds; compositional split)

| arm | tier2 top1 | tier2 top10 | tier1 top1 | tier1 top10 | t2 shared/novel top1 | t1 shared/novel top1 | seen-heldgloss top1 |
|---|---|---|---|---|---|---|---|
| kernel | 0.0000 | 0.0000 | 0.0200 | 0.0500 | 0.0000 / 0.0000 | 0.0333 / 0.0000 | 0.0000 |
| shuffled | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 / 0.0000 | 0.0000 / 0.0000 | 0.0167 |
| random | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 / 0.0000 | 0.0000 / 0.0000 | 0.0167 |

Compositional subsets are DESCRIPTIVE only (no inferential claim), per the pre-registration. seen-heldgloss top-1 is the task-learned sanity readout (should be far above chance in ALL arms if emission fine-tuning worked).
