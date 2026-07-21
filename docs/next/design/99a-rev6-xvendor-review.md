# 99a Rev6 — Cross-Vendor GPT-5.6 Re-Review (procedure VALID; SIM-SPEC + analysis-ledger residuals)

**Reviewer:** GPT-5.6 (`gpt-5.6-sol`, xhigh). **Date:** 2026-07-21. **Target:** `kernel-construction-methodology-proposal-99a.md` (Rev6, `181f6ff4`) vs `99a-rev5-xvendor-review.md`. **Raw:** `poc/gpt56-review/99a-rev6-xvendor/`.

**Role note (mechanical):** verbatim reviewer output. **Verdict: targeted revision needed — NOT material redesign. THE MULTIPLICITY PROCEDURE IS NOW VALID** (Bretz 2009 correctly applied to elementary nulls; IUT/TOST valid; "the recurring Rev5 defect is genuinely gone"; Rung-0 route-by-look Bonferroni correct; H-TEXT-FORMAT selection sound). "Once those targeted defects are corrected, the standard 12-node graphical design is suitable to carry forward, subject to the required simulation build and passing results." Residuals → **Rev7** (spec-level, no redesign): (1) per-component **analysis ledger** (estimand/stratum/unit/seed-aggregation/model/estimator/df/one-sided-p/CI-inversion; resolve exact-binomial gates vs crossed seed effects) + wording "every confirmatory decision bound"; (2) C-DEF-NSUP naming (noninferiority-of-T, not equivalence) + LCC operational-vs-confirmatory; (3) Rung-0 pin Welch df + nested interims; (4) **SIM-SPEC correctness** — DGM must simulate the FULL pipeline (hierarchy selection, futility boundary, Stage-2 trigger, crossed effects); **derive claim-truth PROGRAMMATICALLY from the same hypothesis functions the test engine uses** (the hand-maintained true-null ledger F4/F8/F9/F6/F7/F5 is wrong); fix b(r)=±B circularity + adverse direction + gate-copula sign + generator pin + grid count; and a **coherent Monte-Carlo acceptance rule** (one-sided exact UB below a ~.055 tolerance + lower power bound, planning targets separated from boundaries).

---

## Verbatim GPT-5.6 re-review output

## Overall verdict

**Targeted revision needed—not a material redesign.** Rev6 successfully fixes the central Rev5 multiplicity defect, and its graphical procedure can be retained. But the confirmatory experiment is not yet preregistration-suitable because the valid-component-p-value condition is insufficiently specified and the SIM-SPEC is neither internally correct nor implementable as the claimed end-to-end simulation.

### Assessment by question

| Area | Finding |
|---|---|
| Graphical multiplicity architecture | **Valid in principle** |
| Application’s component p-values | **Not yet established as valid** |
| IUT/TOST construction | **Valid** |
| Rev5 weight-release defect | **Eliminated** |
| Simplified confirmatory scope | **Mostly coherent** |
| Rung-0 sequential coverage | **Valid conditional on its model/envelope** |
| H-TEXT-FORMAT selection | **Valid for familywise claim decisions** |
| SIM-SPEC | **Blocking defects** |

## 1. Multiplicity procedure

The structural multiplicity repair is sound.

- Bretz et al.’s procedure is indeed a sequentially rejective weighted-Bonferroni graph whose vertices are elementary hypotheses; it derives from closed testing and provides strong FWER control when its local tests are valid. See [Bretz et al. 2009](https://onlinelibrary.wiley.com/doi/10.1002/sim.3495) and the underlying [closed-testing result](https://academic.oup.com/biomet/article-abstract/63/3/655/270960).
- The 12 nodes in the [claim ledger](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1137) are legitimate elementary hypotheses for this family, even where a node’s null is itself a union of component null sets.
- Initial weights are nonnegative and sum to one; the [transition rows](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1232) are nonnegative, zero-diagonal, and sum to at most one.
- For a union null, \(p_{\mathrm{IUT}}=\max_k p_k\) is valid: under the union null at least one component null is true, so rejection requires rejecting that true component at the same level. No dependence assumption or internal alpha split is required. That is the relevant result in [Berger 1982](https://asu.elsevierpure.com/en/publications/multiparameter-hypothesis-testing-and-acceptance-sampling/); ordinary TOST is the corresponding equivalence IUT described by [Berger and Hsu 1996](https://doi.org/10.1214/ss/1032280304).
- Consequently, the recurring Rev5 defect is genuinely gone. A node releases weight only after its entire union null is rejected. If any component null remains true, the node null is true and its rejection is already the counted FWER error. There is no longer a separate true elementary hypothesis “left behind.”

The unresolved condition is **valid component p-values**. The document asserts this at [§4.6 item 2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1201), but does not fully specify it:

- The crossed model does not pin the distribution/link, estimation method, degrees-of-freedom method, covariance structure, software, or test-to-CI inversion. “Model-based one-sided p” plus BCa intervals is not an executable inferential definition.
- Exact binomial/Clopper–Pearson gate tests require independent common-probability Bernoulli observations. The actual design has crossed author-seed/snapshot effects, so that requirement does not automatically follow.
- The four \(\pi_a\) gate-pass parameters do not identify the stratum or how multiple seed/snapshot records are collapsed to one concept-level indicator. The claim that every component’s endpoint and stratum is pinned is therefore too strong.

**Concrete fix:** publish an analysis ledger for every component specifying estimand population/stratum, observational unit, seed aggregation, model formula, estimator, denominator degrees of freedom, one-sided p-value, and its matching confidence-bound inversion. Either justify iid concept-level gate indicators or replace exact binomial tests with a preregistered cluster/crossed-design-valid test.

On thresholds, the accurate conclusion is:

- All **positive confirmatory** advancement/adoption tests use graphical procedure-adjusted levels.
- Not every **operative** threshold does. Operational kills use nominal 95%, hierarchy selection uses one-sided 95%, and instrument gates use standalone levels, as the document itself states at [§4.6 item 5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1269) and [§4.8](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1554).

That separation is defensible for strong FWER, because those rules do not create positive confirmatory rejections, but the document should say “every confirmatory decision bound,” not “every operative bound.”

## 2. Scope simplification

The downgrade ledger is coherent and unusually explicit: H-REVIEW, H-HUMAN, mechanism contrasts, A0 readiness, and T′-shuffle are clearly identified as descriptive or operational at [§4.6 item 6](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1288). Operational kills only withhold claims or adoption, so excluding them from the positive-claim FWER family is conservative for that error criterion.

One decision-rule inconsistency remains:

- C-DEF-NSUP establishes that no candidate beats T by \(m_T\).
- That is **one-sided noninferiority of T**, not two-sided equivalence.
- Nevertheless, the hypothesis and precedence matrix still say “equivalent with lower LCC,” while the controlling mapping says C-DEF-NSUP plus LCC fires the branch: compare [H-TEXT-SOURCE](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:649), [C-DEF-NSUP](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1163), and the [row-to-claim mapping](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1639).

**Fix:** rename that branch everywhere to “T is noninferior to every candidate within \(m_T\) and has lower LCC,” or restore an actual two-sided equivalence claim. Also state whether the LCC conclusion is an operational policy filter or a confirmatory component; if the latter, its null and p-value belong inside the IUT.

## 3. Rung-0 sequential looks

The route-by-look Bonferroni argument is correct. If every per-route/per-look upper bound has coverage \(1-\alpha_0/(4L)\), the union bound yields simultaneous coverage of at least \(1-\alpha_0\), without assumptions about dependence between looks or routes. On the simultaneous-coverage event, “all four \(U_\ell(r)<f\)” implies all four true route effects are below \(f\).

The [transfer formula](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1799) is valid **conditional on**:

- the deterministic assumption \(|b(r)|\le B(r)\);
- independence of pilot and campaign estimation errors;
- correct calibration of the stated t/Welch approximation.

It is not distribution-free, and \(B(r)\) is an assumption/sensitivity envelope rather than statistically learned coverage. The unboundable-increment fallback appropriately acknowledges this.

Before implementation, pin the actual Welch–Satterthwaite formula and component degrees of freedom. The simulation must also generate nested interim observations, not independent per-look estimates.

## 4. H-TEXT-FORMAT

The selection repair is sound for hypothesis decisions.

The endpoint is now exactly one endpoint at [§4.1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:677). Because all four C-FMT-c hypotheses are predeclared in the strong-FWER family, the event “the selected candidate receives a false format-equivalence rejection” is a subset of “at least one true C-FMT hypothesis is rejected.” This remains true under arbitrary correlation with Stage-1 selection.

Similarly, conditionally not executing Stage 2 can only remove rejection opportunities.

Two clarifications remain:

- Pin the C-FMT target stratum explicitly; SIM-SPEC assumes natural concepts, while the claim ledger does not say so.
- Describe the result as selection-valid graphical testing unless compatible simultaneous confidence intervals are actually constructed by inversion. Merely printing ordinary intervals at data-dependent final local levels does not by itself establish a general simultaneous-CI procedure.

## 5. SIM-SPEC

This is the principal blocker.

### It does not simulate the claimed actual procedure

S1 promises the exact full pipeline, but [S4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:1964) replaces the registered crossed model with one-sample concept-level t tests. It also lacks variables or algorithms for:

- the hierarchy-rung contrasts needed to select \(c^*\);
- the Stage-1 binding-futility boundary;
- the Stage-2 execution trigger;
- LCC uncertainty and robustness decisions;
- several operational kill/block outcomes;
- author-seed, reviewer, and consumer crossed effects.

P5 therefore cannot be implemented from the stated DGM, and the simulation cannot quantify the exact operating characteristics promised in S1.

### The true-null ledger is wrong

Examples from [S6](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kernel-construction-methodology-proposal-99a.md:2018):

- F4 has the other candidates at \(-0.15\), making **all four** C-CON-SUP nulls true, not only C-CON-SUP-H.
- F8 at \(\Delta_c=-\delta_T\) has C-DEF-SUP and all four C-CON-SUP nulls true.
- F9 likewise has all four C-CON-SUP nulls true.
- F6/F7 cannot have only the format nulls true in an adoption world: if an adoption contrast has \(\Delta_c>\delta_T\ge m_T\), both C-DEF nulls are true through that candidate.
- F5’s “contrasts deep-false” is not a parameter assignment and cannot determine a unique truth set.

**Fix:** give every cell a complete 24-parameter vector and derive claim truth programmatically from the same hypothesis functions used by the testing engine. Do not hand-maintain a separate truth column.

### Other implementability defects

- \(b(r)=\pm B(r)\) is circular because \(B(r)\) depends on the random pilot estimate whose distribution is itself centered using \(b(r)\).
- P6 uses \(b=-B\), although \(b=+B\) is the adverse direction for underestimating the campaign review increment and falsely terminating.
- The gate-copula sign is reversed: with positive correlation and \(g=1\{Z\le\Phi^{-1}(\pi)\}\), passes co-occur with low contrasts, contrary to the text.
- The bounded-Beta copula/correlation construction and block membership are unspecified.
- “Philox or PCG64” does not pin a reproducible generator.
- Grid expansion gives 70 cells before the unspecified block sensitivity, not “approximately 60”; expansion order and hence `config_index` seeds are not pinned.

### Acceptance criteria are statistically unstable

At a true FWER of exactly .05, requiring \(\hat p\le.05\) fails about half of otherwise correct Monte Carlo runs. That conflicts with the later “implementation defect” threshold of \(.05+2SE\). The same issue applies to point-estimated power exactly at .90.

**Fix:** use one coherent Monte Carlo decision rule—for example, a one-sided exact upper bound below a predeclared FWER tolerance such as .055, and a one-sided lower power bound above the required floor, with planning targets sufficiently separated from the acceptance boundaries.

## Freeze-time pins versus specification gaps

Legitimate freeze-time pins include margins, transition fractions, \(\alpha_0\), \(L\), look times, \(f\), transfer-envelope constants, sample sizes, variance scenarios, seeds, replication counts, and calibrated selection/instrument thresholds. Any change after simulation requires rerunning the full acceptance artifact.

Not legitimate deferrals are:

- the exact component-test and confidence-bound definitions;
- gate stratum/seed aggregation;
- hierarchy and futility algorithms;
- complete simulation variables and dependence construction;
- automatic truth-set derivation;
- the circular transfer DGM;
- Monte Carlo acceptance logic.

Once those targeted defects are corrected, the standard 12-node graphical design is suitable to carry forward, subject to the required simulation build and passing results.
