# Cross-vendor delta-checks (GPT-5.6 `gpt-5.6-sol`, xhigh) — S3 grounding-checker scoping

> Two focused delta-checks in the S3 review loop. Rev1 review (NEEDS-REVISION) is the sibling
> `colibri-s3-scoping-xvendor-review.md`. Rev2 delta-check found a NEW-DEFECT (bundled mask+context
> C-KERN estimand); Rev3 resolved it via the crossed 2×2 → CLEAN-WITH-MINORS (two freeze-time residuals).
> Runner: poc/gpt56-review/run-review.sh (npx-pinned codex 0.144.1; global codex untouched).

---

## Rev2 delta-check — verdict NEW-DEFECT

# Verdict: **NEW-DEFECT**

Rev2 resolves most Rev1 findings, but the new C-KERN design is not yet identifiable as written.

1. **M_K−M_N is a bundled intervention.** M_K uses kernel text plus kernel mask; M_N uses non-kernel text plus non-kernel mask. Rev2 explicitly admits both channels are swapped ([§4.1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/colibri-s3-grounding-checker-scoping.md:393)). Therefore a PASS identifies value of the complete source package, not specifically “a kernel-compiled mask at the sampler seam.” Making M0_K−M0_N secondary does not repair the confirmatory estimand. Either isolate mask source while holding context fixed, promote a mask-only/crossed contrast, or narrow C-KERN to a full text-plus-mask source-stack claim.

2. **The proposed arm-N opponent is under-matched.** Coverage, set-size, bytes, runtime, and authoring-budget matching are good, but the manifest does not require matched semantic expressivity: relation inventory, axiom families, closure/entailment capability, and source-quality gates. A “generic schema-with-enums” can be structurally weaker than the kernel’s axioms and closure, making disagreement—and a kernel win—too easy. Moreover, the repository now explicitly describes knull-v2’s token-matched generic as a degenerate opponent and defines plain-v5-natural as its stronger successor ([plain-v5 §1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/plain-v5-natural-store-contract.md:66)). Thus maintainer question 5 is correctly reserved, but its current candidate/rationale is mis-framed as the strongest opponent.

3. **The new three-outcome trees can overlap.** Superiority fires on observed Δ ≥ 0.03 plus rejection of zero, while equivalence uses an unconstrained ±δ_eq TOST ([§3.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/colibri-s3-grounding-checker-scoping.md:347), [§4.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/colibri-s3-grounding-checker-scoping.md:447)). If δ_eq > 0.03, the same result can license both PASS and equivalence—for example, Δ=.04 with CI [.01,.049] and δ_eq=.05. The freeze must impose disjoint regions or an explicit precedence rule.

PRECERT-1 is a sound necessary guard: exact predicate identity genuinely makes C-KERN unidentifiable, and narrowing the claim is correct. Two qualifications remain:

- Failure at a nonzero ρ_min means “not identifiable/powerable under this planned design,” not theoretical unidentifiability unless the sets are identical.
- “Structured-store admissibility is load-bearing” is licensed only if C-MECH subsequently passes; failed PRECERT alone cannot establish it.

The remaining deltas are substantively resolved:

- M_K>T **and** M_K>G, unstable ratio removed, and unbanked separated from falsified—subject to the overlap defect above.
- KOT-HON/1, independent gold, and effective non-degeneracy are correctly added. At freeze, non-degeneracy should explicitly be certified separately for both K and N masks on the common item set.
- D^policy’s policy-specific two gates and evidential limits are correct.
- Power, clustering, corrected F1-K anchor, and lower-bound cost tagging are correct.
- P-strict primary/P-consistent separately-powered secondary is a sound hierarchy; maintainer question 6 is not mis-framed.
- Epistemic retagging and the honest Rev1 item-4 FAIL record are correct.

---

## Rev3 delta-check — verdict CLEAN-WITH-MINORS

## Verdict: CLEAN-WITH-MINORS

Rev3 resolves the bundled estimand, opponent-strength, and overlapping-region defects without introducing a new identification confound. It is bankable as a scoping document, subject to two freeze-time clarifications.

1. **Crossed 2×2: resolved.** Each simple effect changes only mask source while holding context text fixed:

   - Kernel context: `M_K − X_KN`
   - N context: `X_NK − M_NN`

   Thus Δ_mask genuinely identifies the average causal effect of assigning the kernel mask rather than the N mask across the two registered contexts. The cross cells are coherent controlled hybrids, not confounded package contrasts. Their possible semantic incongruence is effect modification captured by the context×mask interaction; dual-mask eligibility and the all-arm pilot protect against mechanical degeneracy. See [§4.1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/colibri-s3-grounding-checker-scoping.md:417) and [KILL-3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/colibri-s3-grounding-checker-scoping.md:545).

   The unweighted mean is a valid stipulated confirmatory estimand: it defines a 50/50 target mixture over these two context sources. An interaction—even a qualitative one—does not make that average undefined. It does limit interpretation: PASS means an average kernel-mask advantage across these contexts, not context-invariant superiority. Strictly, Δ_mask does average over heterogeneity; co-reporting ensures the interaction is not hidden.

2. **Opponent: substantively repaired, but certification remains to be operationalized.** ROW-S3-07 now specifies the right parity dimensions, uses identical closure machinery, disallows asserted-only opponents, and correctly positions plain-v5-natural as the minimum textual base. This defeats the Rev2 strawman. See [ROW-S3-07](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/colibri-s3-grounding-checker-scoping.md:460).

   Minor residual: “matched breadth,” “typed-store equivalents,” and “or stronger” are not yet auditable thresholds, while plain-v5-natural itself is a natural-definition contract and its typed facts/constraints are only a proposed extension. At freeze, the manifest should enumerate the relation mapping, realized—not merely available—axiom-family coverage, closure conformance tests, source-gate parity, and what qualifies as “stronger.” The present document establishes a fair opponent requirement but does not itself certify the eventual opponent.

3. **Decision regions: resolved.** With δ_eq < δ_floor, equivalence implies the estimate lies below δ_eq, whereas superiority requires it at or above δ_floor. They cannot co-fire. For the test case, δ_floor=.03 requires δ_eq<.03, so CI `[.01,.049]` cannot fit inside `(-δ_eq,+δ_eq)`; equivalence is impossible. Ordered evaluation also resolves possible harm/equivalence overlap. See [§3.3](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/colibri-s3-grounding-checker-scoping.md:376).

   Minor consistency point: KILL-3 references the common superiority→harm→equivalence order but explicitly lists only PASS/equivalence/inconclusive. Either define the Δ_mask harm test or describe KILL-3’s order as superiority→equivalence. This does not recreate PASS/equivalence overlap.

4. **PRECERT/non-degeneracy: resolved.** Rev3 correctly says nonzero-ρ_min failure means not identifiable/powerable under this design, reserves strict unidentifiability for identical masks, requires a later C-MECH PASS for the load-bearing headline, and restricts crossed cells to the common items independently passing non-degeneracy under both masks. See [PRECERT-1](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/colibri-s3-grounding-checker-scoping.md:487) and [§5.2](/home/ec2-user/css/kernel/kernel-of-truth/docs/next/design/colibri-s3-grounding-checker-scoping.md:602).