# KOT-FAIR/2 Rev4 — Cross-Vendor GPT-5.6 Delta-Check Re-Review

**Reviewer:** GPT-5.6 (`gpt-5.6-sol`, xhigh). **Date:** 2026-07-21. **Target:** `kot-fair-2-spec-p3mf0.md` (Rev4, `22fbcb1a`). **Raw:** `poc/gpt56-review/kotfair2-rev4-deltacheck/`.

**Role note (mechanical):** verbatim reviewer output. **Verdict: targeted revision needed** — but the two converged CRITICALs are now VERIFIED FIXED (floor-dispersion admissibility fail-closed at all stages; census §0-contradiction gone). Residuals are SECOND-ORDER → **Rev5 (final Part-B polish)**: 1 HIGH (missing POWER-CENSUSED/FAIL state → W1 undefined) + 3 MEDIUM (exactly-5% p95 rank off-by-one; stale ≤50% in POWER-CENSUSED def; residual point-vs-favourable-bound membership choice) + 2 LOW (branch-1 "ceiling" wording; hash-partition under-pinned). Freeze remains externally gated regardless (#57/Part C/THREAT/empirical).

---

## Verbatim GPT-5.6 delta-check output

## Verdict

**Targeted revision needed.** Rev4 closes most prior defects and requires no material redesign, but its “sound” self-verdict is premature. I found one HIGH, three MEDIUM, and two LOW residuals.

## Findings

1. **HIGH — the three-state census taxonomy is not exhaustive.**

   A `POWER-CENSUSED` component can still fail `LCB95(s̃) > f`: 80% power explicitly allows false negatives, and genuinely weak anchors can fail more often. Yet [§1.4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:216) defines no `POWER-CENSUSED/FAIL` outcome, while [§0](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:84) and [§7.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:831) claim `WIDTH-LIMITED-INCONCLUSIVE/FAIL` is the only census-related scalar-ineligible state. That leaves W1 undefined after an adequately powered LCB failure.

   **Fix:** either add a fourth state, `POWER-CENSUSED/FAIL`, or retain exactly three eligibility outcomes by replacing the third with a generic `LCB-GATE-FAIL/FAIL`, carrying sizing status (`POWER-CENSUSED` versus width-limited) separately. Apply identically in §0, §1.4, §7.3, R4b, and the self-check.

2. **MEDIUM — exactly 5% incomplete requests do not produce `p95 = +∞` under the pinned rank.**

   [§3.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:414) uses rank `ceil(0.95n)`. With 100 issued requests and five `+∞` values, rank 95 is still finite; the infinities occupy ranks 96–100. Thus the stated “≥5%” consequence is false—only strictly more than 5% is guaranteed to trigger it.

   **Fix:** use rank `floor(0.95n)+1`, or explicitly override the quantile to `+∞` whenever `n_incomplete/n_issued ≥ 0.05`. Mirror that rule in §3.5, R4d, register item 10, and the self-check.

3. **MEDIUM — the 100% max-N branch has a stale 50% classification rule.**

   The main rule correctly permits 100% for components with no known-order contribution, but the immediately following POWER-CENSUSED definition still requires achievability at `≤50%` [§1.4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:216). A non-known-order component needing 51–100% is therefore neither POWER-CENSUSED nor width-limited, because it is achievable within its actual 100% cap.

   **Fix:** replace `≤50%` with “within the component’s branch-specific maximum-N cap.” Update the stale flat-50% assertion in the historical self-check or annotate it explicitly.

4. **MEDIUM — comparator membership still contains an unpinned point-versus-favourable-bound choice.**

   [§3.5](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:461) and [§5.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:674) say membership uses the point estimate, but then allow a favourable bound “instead.” Section 5.3 subsequently says only point-estimate violations are inadmissible. A point-fail/favourable-bound-pass comparator therefore has two possible dispositions.

   This does **not** reopen the requested point-goodput-fit/LCB-fail case—that case now correctly block/carries—but membership is not fully deterministic.

   **Fix:** mandate point-estimate membership throughout, or preregister one roster-wide alternative before any measurement. Delete the unused alternative everywhere else.

5. **LOW — branch 1 still calls minimum goodput a ceiling.**

   [§3.1 branch 1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:349) assigns an “ABSOLUTE ceiling” to minimum goodput, contradicting the explicit floor rule three lines later.

   **Fix:** say “absolute bounds: ceilings for CPU/accelerator/I/O/TTFT and a floor for minimum goodput”; change subsequent generic “ceilings” references to “bounds.”

6. **LOW — component-global is sound, but the actual hash partition is insufficiently pinned.**

   The scope choice is good, but “item-ID hash partition” does not pin canonical item-ID serialization, hash function, seed/domain separator, cutoff/tie rule, or the resulting per-item assignment [§1.4](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:215), [§7.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/kot-fair-2-spec-p3mf0.md:792). Without one of those being frozen, partition selection remains a calibration knob.

   **Fix:** add these pins—or the complete per-item partition manifest—to register item 4 before anchor outputs are inspected.

## What Rev4 got right

- The specific HIGH floor-dispersion case is now closed at builder, closure, and campaign stages: point goodput fit plus adverse LCB failure maps to tiered W1 block/carry and cannot silently exit.
- The old operative “point estimate (or LCB95)” wording is gone; remaining occurrences are historical/supersession text.
- `CENSUS-WIDTH-LIMITED/PASS` is consistently scalar-eligible across §0, §1.4, and §7.3. The remaining defect is the omitted adequately-powered FAIL outcome, not the former §0 contradiction.
- Most max-N wiring is correct: 50%/100% contribution rule, component-global scope, manifest fields, and item-17 return-for-revision consequence.
- Assigning incomplete latency observations `+∞` is the correct fail-closed design; only the 5% boundary convention needs repair.
- The budget-anchor path-(b) reference is sound and non-gameable: it exists before roster construction, is tied to \(B_k\), has a dedicated output field, and roster pairwise results are OR-aggregated so the anchor cannot cancel another fired comparison.
- The five-coordinate/four-class count is consistent.

The pending numerical constants, DEFF/taxonomy artifacts, \(\kappa_m/\tau_m\), and item-17 empirical decision are legitimate ratification inputs, not defects. I did not count the four acknowledged external freeze gates.
