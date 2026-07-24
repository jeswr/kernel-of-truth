# Cross-vendor delta-check (GPT-5.6, xhigh) — S3 prereg Rev2 → NEW-DEFECT

> Rev2 fixed 8/9; the binding B-3 realized-layout G-P was NOT actually implemented (draw_mask iid-redrew).
> Fixed in Rev3 (frozen-incidence mode + --realized input path). Committed for the record.

---

Verdict: **NEW-DEFECT**

Rev2 fixes most Rev1 findings, and the published simulation numbers reproduce exactly. However, the binding realized-layout G‑P repair is not actually implemented.

| # | Delta verdict |
|---|---|
| 1 | **PASS with minor caveat.** δ_floor=.09 is honestly identified as an MIE, not forced. The run reproduces at-floor conjunction .262 and supports μ*≈.122 by interpolation (.787 at .120; .874 at .130). G‑D provides feasible headroom: 5% wrong→correct permits +.20 S₃, exceeding +.122, though achieving +.122 requires correcting about 61% of that headroom. Thus G‑D establishes possibility, not realism by itself; pilot-transition G‑P must do the latter. The claim that *below* .05 the effect is structurally impossible is too strong—.0305 headroom could theoretically support +.122. Retraction is otherwise complete; old language appears only as historical/retracted text. |
| 2 | **PASS gate; MINOR scope inconsistency.** G‑EQ is a genuine fail-closed, prefix-by-prefix next-token-set comparison against a pinned reference evaluator. C‑MECH and KILL‑1 carry the narrow claim. But the [coverage rider](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/s3-grounding-checker-prereg.md:747) does not actually repeat the answer-span/fixed-slot boundary despite §15 saying it does, and “structured-store admissibility is load-bearing” remains a broader headline at line 545. |
| 3 | **NUMBERS PASS; IMPLEMENTATION FAIL.** The committed hash matches the document, and unchanged execution reproduced every published constituent value for C=96, exact C=54, τ=.10, ρ=.30/.25, and concentrated stress. No t surrogate or fixed df remains. |
| 4 | **PASS.** Superpopulation, equal-cluster estimand, descriptive finite-universe value, concept exchangeability, and conditional sign-symmetry basis are coherently stipulated. |
| 5 | **FAIL through G‑P defect.** Dilution arithmetic and concentrated-stress numbers are correct, but the realized disagreement layout is not truly consumed. |
| 6 | **PASS.** PV5T-AUDIT now specifies auditable artifacts and makes them fail-closed pre-freeze gates. |
| 7 | **PASS.** The 24×5 pilot permits within/between decomposition; `max(τ̂_pilot, τ_planning)` prevents relaxing below planning variance. |
| 8 | **PASS.** Ranking score and closed reason-code classification are deterministic and complete. |
| 9 | **ACCEPTABLE.** The residual Anthropic author/screen dependence is disclosed and direct store leakage is blocked by the fail-closed store-blind envelope. This follows an explicit remedy allowed by Rev1, though it is not full family independence. |

Blocking defect: [`draw_mask()`](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/s3-prereg-power-sim.py:137) accepts only a C-length vector of disagreement probabilities. It then [Bernoulli-redraws disagreements](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/s3-prereg-power-sim.py:149) independently for every replication. Consequently, exact frozen per-cluster counts/item locations are discarded and an extra binomial variation layer is introduced. `run()` also has no realized-artifact input path. The published planning rows are reproducible, but the script cannot perform the preregistered conditional G‑P check on the frozen item×cluster table.

Freeze therefore remains blocked by this defect, in addition to the declared pre-freeze gates and M‑2/M‑4.