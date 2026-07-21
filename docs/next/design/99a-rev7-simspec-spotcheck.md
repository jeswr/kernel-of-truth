# 99a Rev7 — SIM-SPEC/ledger focused spot-check (cross-vendor)

**Reviewer:** GPT-5.6 (`gpt-5.6-sol`, xhigh). **Date:** 2026-07-21. **Target:** `kernel-construction-methodology-proposal-99a.md` (Rev7, `d8bfb6f4`) — SIM-SPEC + analysis ledger only (procedure validity NOT re-audited). **Raw:** `poc/gpt56-review/99a-rev7-spotcheck/`.

**Role note (mechanical):** verbatim reviewer output. **Verdict: TARGETED FIX NEEDED.** Rev7 CONFIRMED-FIXED: programmatic truth-set (F4–F9 correct), Monte-Carlo acceptance rule, transfer circularity/adverse-direction, gate-threshold orientation, Philox/grid pins, Rung-0 outer Welch + nested interims. Remaining 7 before-build corrections (all DGM↔ledger consistency + spec-completeness, NOT design): (1) unify DGM+ledger on one arm-level long-form data representation + reviewer/consumer consistent + publish rotations; (2) pin exact REML/variance-boundary/Satterthwaite per family OR one reference impl+version; (3) replace the gate test with a model-consistent crossed-binary procedure (the Gaussian-LMM-on-Bernoulli isn't super-uniform-valid) + fix the cross-stratum gate/contrast zero-correlation; (4) bounded-Beta as a centered unit-variance concept random-effect before S4.1 scaling; (5) add §4.8 operational variables + row-2/5–9 algorithms with real PRICE VECTORS (positive-scalar wL̂ can't reverse sign) + LCC-in-P1-estimand-or-rename; (6) Rung-0 integer look sizes + route/pilot covariance + explicit F10 criterion; (7) pin NumPy/SciPy versions + zero-based replication indices + named RNG substreams. **Disposition: Rev8 applies these → then straight to the (B) build (implementation as the final consistency test; residual ambiguity routes back via the spec's S9 clause).**

---

## Verbatim GPT-5.6 spot-check output

## Verdict: TARGETED FIX NEEDED

Rev7 fixes the truth ledger, Monte-Carlo rule, transfer circularity/direction, Philox/grid pins, and the explicit Rung-0 Welch/nesting defect. It still cannot be coded end-to-end without design choices because the rewritten DGM does not match the analysis ledger, the gate/Beta dependence models remain incomplete, and most claimed operational decisions lack simulated inputs.

I did not re-audit the already-confirmed multiplicity procedure.

1. Full pipeline: not yet

The control-flow scaffolding is present: hierarchy selection, Stage-1 futility, Stage-2 triggering, Rung-0, and claim-level error counting are explicitly specified in [S1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2146) and [S4.5–S4.9](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2324).

But the simulated data cannot execute the registered analysis exactly:

- Ledger family A requires arm-level observations fitted as  
  `Y = α_a + b_i + (ab)_{a,i} + v_s + u_k + ε` [§4.6](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1292). S4.1 instead generates contrast-level `d[i,s,j]` values [S4.1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2249). Those differences cannot reconstruct the arm-level model, concept×arm effects, or the specified consumer assignment.
- S4.1 generates reviewer effects, but S4.2 fits `d = θ + b_i + v_s (+u_k) + ε`, omitting reviewer [S4.1–S4.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2262). This also conflicts with §4.6’s requirement that reviewer be modeled on review-based endpoints.
- S4.9 says §4.8 rows 2 and 5–9 are computed [S4.9](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2385), but the DGM has no E-arm fidelity/LCC, per-arm LCC, review-time, or cost-dominance variables required by those rows [§4.8](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1833). Even the shuffle-equivalence margin for row 2 is not pinned.

Thus it is no longer “one-sample t-tests,” and errors are correctly counted at claim level, but it is not yet the full claimed executable pipeline.

2. Programmatic claim truth: fixed

This defect is cleanly repaired. One shared module is mandated [S1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2176), the null functions are written explicitly [S5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2397), and cells resolve defaults plus overrides without a hand-authored truth column.

The previously problematic truths now derive correctly:

- F4: both C-DEF nulls, all four C-CON-SUP nulls, and C-GRAPH are true.
- F8: C-DEF-SUP and all four C-CON-SUP nulls are true.
- F9: both C-DEF nulls, all four C-CON-SUP nulls, and C-GRAPH are true.
- F6/F7: both C-DEF nulls, three non-H C-CON-SUP nulls, and all four C-FMT nulls are true—not “only format.”
- F5 now has explicit numeric assignments, completed by the pinned defaults.

3. Other implementability defects: partly fixed

Correctly fixed:

- \(B^*\) removes the random-envelope circularity, and \(s_b=+1\) is the adverse false-termination direction [S4.8](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2359).
- The gate threshold orientation is algebraically corrected [S4.4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2310).
- Philox alone is pinned [S2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2186).
- The 70+4=74 grid count and expansion order are correct [S6](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2452).

Still defective:

- Gate \(Z\) is only described as “correlated at \(\rho\)” with \(C_i\); no joint formula or gate block membership is given. Moreover, gates live on the nonce stratum while C-CON-SUP contrasts live on the natural stratum, and S4.1 sets cross-stratum correlation to zero. Therefore the intended positive gate/UCT co-occurrence cannot arise through the stated concept layer.
- S4.1 requires a unit-variance concept latent \(C_i\), but bounded-Beta S4.3 maps the latent to an \(X_j\) having mean \(\theta_j\) and SD \(\sigma_j\). Substituting that into S4.1 adds \(\theta_j\) again and rescales by \(\sigma_j\) again. The bounded-Beta regime therefore has no internally consistent interpretation.
- Reviewer/consumer rotation is called “pinned,” but no actual mapping algorithm is provided.

4. Monte-Carlo acceptance: fixed

The operative specification now has one coherent rule:

- FWER: exact one-sided 95% CP upper bound \(\le .055\);
- floored power: exact one-sided 95% CP lower bound \(\ge .90\);
- false termination: exact upper bound \(\le .025\);
- planning targets .92/.015 are separate from acceptance boundaries.

There is no operative \(\hat p\le.05\) or `.05+2SE` requirement [S6–S7](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2470). Remaining appearances are retrospective descriptions or the explicitly superseded Rev6 self-check.

5. Analysis ledger: fields present, but not executable/valid as claimed

The estimand, stratum, unit, model, estimator, p-value directions, and CI inversions are all written down, and the p/CI algebra is consistent [analysis ledger](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1265).

Two blockers remain:

- “REML + Satterthwaite” is not a unique algorithm for these crossed models. The variance-component estimator, boundary handling, covariance derivatives, and exact Satterthwaite calculation are absent. S4.2 permits an unspecified closed-form ANOVA implementation and comparison to an unspecified “generic REML” fit [S4.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2278).
- The gate replacement is crossed-design-aware, but not established as a valid level test. It fits a Gaussian linear mixed model with REML/Satterthwaite to Bernoulli indicators [ledger C](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1318), while S4.4 generates correlated thresholded-normal Bernoulli data. Gaussian-residual t calibration—and therefore the claimed super-uniformity—does not follow.

So the exact-binomial problem was recognized, but its replacement is not yet a fully pinned crossed-design-valid test.

6. Rung-0: principal Rev6 defect fixed, residual implementation pins remain

The outer Welch–Satterthwaite formula, \(\nu_p=n_p-1\), conditionality, and cumulative nested interims are now explicit [§7](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2025).

Residuals:

- \(\nu_D(\ell,r)\) still depends on the unspecified mixed-model Satterthwaite implementation.
- `n_max` is not identified with a configured sample size, and 40%/70% of base \(n=96\) are nonintegers; no rounding or exact look-count table is given.
- The joint correlation of the four route datasets and four pilot estimates is unspecified.
- F10 says it checks the \(\alpha_0\) guarantee, but no F10 termination acceptance rule/output is declared.

## Concrete correction required

Before build:

1. Make the DGM and ledger use one identical data representation—preferably arm-side long-form observations—and include reviewer/consumer factors consistently. Publish the assignment rotations.
2. Pin exact REML, variance-boundary, and Satterthwaite formulas per family, or pin one reference implementation/version that supplies them.
3. Replace the gate test/DGM together with a model-consistent crossed binary procedure; fully specify its latent covariance, marginal-\(\pi\) mapping, test, CI inversion, fitting failures, and calibration.
4. Define bounded-Beta as a centered, unit-variance concept random effect before S4.1 scaling, rather than a second full outcome marginal.
5. Add the missing operational variables and exact row-2/5–9 algorithms. The current positive-scalar sweep \(w\hat L\) can never reverse sign; use actual price vectors applied to component cost vectors. Either include LCC in P1’s deflation-adoption estimand or rename P1 as confirmatory-path power.
6. Pin Rung-0 integer look sizes, route/pilot covariance, and an explicit F10 criterion.
7. For implementation-independent reproduction, pin NumPy/SciPy versions, zero-based replication indices, and named RNG substreams/draw ordering.

Margins, sample sizes, variance scenarios, \(\alpha_0\), look fractions, transfer constants, seeds, and replication counts remain legitimate freeze-time constants. The items above are algorithms, variables, and dependence definitions—not legitimate freeze-time deferrals.
