# nsk1 B′ fork — Gate-A audit custody record (coordinator, mechanical)

Coordinator custody record of the independent GPT-5.6 (xhigh) Gate-A statistical-integrity audit of the
nsk1 B′ Stage-0 PASS fork recommendation (`docs/next/analysis/nsk1-bprime-interpretation.md`, Fable
designer-11). This records the audit's mechanical outcome only; the fork conclusion is Fable's, the
verification is Codex's, and nsk1 remains DRAFT / MEASURED-exploratory (quarantined, uncitable in any
verdict). Raw audit transcript is at `poc/gpt56-review/nsk1-bprime-gatea/out/` (gitignored review dir).

## Audit verdict: PASS-QUALIFIED — the fork recommendation (PASS → redesign the internal-write family at R3) is upheld

Every decisive number was independently recomputed from the raw rows and reproduced; the PASS survives
corrections **stricter** than the registered plan. Confirmed (checks 1–5, 7, 8):
- **Keyed accuracy** from `poc/nsk1/out/bprime2/bprime2_rows.jsonl` via m = lp_top − lp_bridge, success
  m(+)>m(−): (16,16) = 170/200 = **0.850**; (12,16) = 162/200 = **0.810**.
- **Wilson lower bounds** ≥ 0.70 floor over the registered 9-cell real-arm family (z≈2.539); pass even if
  over-corrected across all 27 arm-cells (LBs 0.7627 / 0.7176).
- **Paired tests** are exact one-sided paired sign / McNemar tests; survive Bonferroni over **all 18**
  cell×control tests (largest adjusted passing p = **1.596×10⁻⁵**).
- **Chance = 0.5** verified from the frozen coin-XOR sign assignment (not merely "two labels"); all 3,600
  deranged-row coin bits matched the pinned SHA-256 recipe; zero ties.
- **Instrument validity**: text-only headroom 758/958 = 0.7912 (∈[0.05,0.85], n≥900); max coin-control
  Wilson LB 0.4231 < 0.5. Run-1 corroborates (control LB 0.4670 ≥ 0.15).
- **Scope** correctly labelled MEASURED-exploratory; nsk1 stays DRAFT (no frozen-index / results-log /
  verdict object); no programme-level conclusion.

## Carry-forward qualifications for the R3 redesign (audit check 6 & 8 — the "QUALIFIED")
These do NOT reverse the PASS (all four decisive p-values survive the stricter Bonferroni), but the R3
redesign must carry them:
1. **FWER spec defect (specification-level, not numerical):** the frozen rule
   (`docs/next/nsk1-bprime2-spec.md:226`) leaves the two paired-control tests at p<0.05 **per searched
   cell** with no multiplicity correction across the 3×3 grid. R3 must pre-register a complete
   multiplicity plan covering the paired-control tests, not only the Wilson floor.
2. **"Independent second cell" wording is inaccurate:** cell (12,16) uses the same 200 items, model, α,
   and derangement seed as (16,16) — it is corroborating, not independent. R3 wording must not claim
   independence; genuine independence needs fresh items/seed.
3. **"Confirmatory" wording:** "confirmatory as a fork decision" is defensible only as "a predeclared rule
   was mechanically applied"; it must never be shortened to "confirmatory result" — the study is adaptive,
   pre-freeze, single-run exploratory evidence.

## Coordinator disposition
Fork = **PASS-QUALIFIED**, Gate-A-verified. bh1n (interpretation + fork rec) is complete. The internal-write
family proceeds to an **R3 redesign** (not a verdict); the redesign inherits the three qualifications above
and the interpretation's EXTRAPOLATION boundaries (other hosts / R3+ scale / other forms / α<1.0 /
grounding / latent-timing all load_bearing:false). Feeds the FINAL feasibility synthesis (d8p8) as an
exploratory positive structure-side signal for the CORRECTNESS thesis — licensing nothing on its own.
