# Coverage census — measured finding + verdict input (D3 upper-sieve lane)

**Author:** Fable experiment agent, 2026-07-11 (rev-2 after GPT-5.6 review
`poc/gpt56-review/rev-covcensus-20260711/`) · **Scope:** the **D3 upper-sieve
lane** of the coverage-ceiling census POWER (`poc/p3-power/`,
`docs/next/design/POWER.md` rev-2) named as INCOMPLETE — **not** a full-suite
census (see honesty lines). This note reports a MEASURED finding and a
**verdict INPUT**; it does **not** write the final verdict (coordinator's
mechanical step + Fable interpretation) and touches no frozen record.
Tags: [MEASURED] / [STIPULATED] / [COMPUTED BOUND] / [EXTRAPOLATION].

## The blocker POWER named, and the lane completed here

POWER computed the general-index ceiling at Δ_max simUCB95 ≈ **0.8095** but
could not fire a formal kill: the existing censuses cover **one domain (D3)**, so
the bound is dominated by *full-headroom imputation* for 5 uncensused domains +
2 D4 benchmarks; the measured D3 slice (mapper-parse lane) was **0/1550 → 0**
[MEASURED: `poc/p3-power/coverage-ceiling-result.json`]. A *complete* census
needs (per POWER §2.1/§7): a **frozen P3-D-INDEX enumeration** of every
benchmark of every weighted domain; a whole-suite census in a **kill-sound
lane** (the cheap lemma-touch **upper sieve**, or the human-annotated
**oracle** lane which is **NOT ~$0**); plus pin block + eligibility.

This run built + ran the cheap sound tier for the one lane available to it —
the **lemma-touch upper-sieve census over the 7-benchmark D3 suite**
(`P3-X-SIEVE-CENSUS`), reusing the byte-identical m0b/d-ext covered-lemma
machinery (kernel-v0 + molecules-v0, 190 lemma types), then the POWER rig on
the normalised scale. It is a **D3-suite census**, not a full-suite census:
CLUTRR item data exists but was intentionally excluded (authored against the
store), ProofWriter has no data on disk, D1/D2/D5/D6 are unenumerated.

## Measured finding [MEASURED]

- **Upper-sieve coverage over the D3 suite: κ = 0.6665 pooled (1033/1550;
  0.39–0.84 per benchmark).** The *same* suite POWER measured at κ = 0/1550 on
  the mapper-parse lane is **two-thirds touched** on the kill-sound sieve lane.
  The mapper 0/1550 is a valid measured result **for the mapper-parse
  instrument**, which folds in the NL parse gap; it **cannot be treated as
  oracle coverage**, and the upper sieve shows the cheap unconditional-kill
  lane does not confirm it. (Attributing the *entire* mapper–sieve gap to NL
  parsing is [EXTRAPOLATION]: sieve false positives, missing endorsements, and
  non-derivability may explain part or all of it. The magnitude is consistent
  with the b-cov "≈49% lemma-touch / 0% checkability" datum — higher here, 67%,
  because the sieve predicate is the loosest.)
- **Normalised ceiling under the sound lane** [COMPUTED BOUND: MEASURED κ +
  PROVISIONAL/STIPULATED pin (unfrozen weights/ceilings/margins, a_cov=0
  imputation, full-headroom imputations)] — provisional pin, δ_k=0.03:
  Δ_max scalar simUCB95 = **0.9860** (vs 0.8095 mapper-parse), decomposed as
  **D3 censused 0.17651 + uncensused/full-headroom 0.80950 = 0.98600**
  [MEASURED: `poc/coverage-census/power-D3-uppersieve.result.json` — D4
  0.25950 + D1/D2/D5 0.15 each + D6 0.10]. (rev-2 correction: an earlier
  draft wrongly reported the uncensused mass as 0.8235 = 1 − 0.1765; the
  index's maximum aggregate headroom is not exactly 1 under the unclamped
  provisional normalisation. Note the uncensused mass numerically *equals* the
  old mapper-parse ceiling 0.8095 because D3 contributed 0 there.)
- **D3 own-axis under the sound lane = 0.8825 vs δ_k^D3 = 0.05** — the
  mapper-parse "would-fire" domain kill (0.0000 < 0.05) is **dissolved as a
  cheap unconditional kill**: the sieve lane that would have made it
  unconditional does not confirm the zero. (Not empirically *disproved* at the
  exact-oracle level — the oracle census does not exist.)

## Verdict input (coordinator draws the verdict)

**STILL-INCOMPLETE for the general-index kill; no unconditional kill is
supported by the cheap D3 upper-sieve run. The rig remains ILLUSTRATIVE-ONLY
and emits no G1 verdict.** (Scope: this run covers only the seven D3
benchmarks; it does not establish results for every family, suite component,
or possible cheap computation.)

- **General index:** sound-lane Δ_max simUCB95 = **0.986 ≫ δ_k = 0.03** under
  the provisional pin; the suite is not even fully *enumerated* (D1/D2/D5/D6
  carry weight with zero benchmarks in any pin that exists). Replacing the D3
  mapper-parse zero with the kill-sound upper sieve **raised** the provisional
  bound (0.8095 → 0.9860) — i.e. completing this lane of the census RAISED the
  ceiling. Mechanism, stated carefully: replacing *full-headroom imputations*
  with measurements can only lower or preserve Δ_max; what raised the ceiling
  here was replacing the already-censused D3 lane's mapper zero (unsound for an
  unconditional kill) with the generous kill-sound sieve value. Since D3 alone
  contributes **0.17651 > δ_k = 0.03**, this D3 sieve result cannot support the
  general-index kill under the provisional pin **even if every other component
  later contributed zero**. Whether the *eventual* frozen index can be cheaply
  killed is open (frozen weights/margins/suite composition do not yet exist).
  [COMPUTED BOUND → the forward conclusion is the coordinator's EXTRAPOLATION]
- **Domain-scoped D3:** sound-lane D3 own-axis = **0.8825 ≫ δ_k^D3 = 0.05** →
  **no sound D3 kill**. The free domain-scoped kill POWER flagged is dissolved
  *as a cheap unconditional kill* by the lane (sieve) that would have made it
  unconditional; the exact-oracle question stays open.
- **Exactly what is missing:** (1) the **frozen P3-D-INDEX enumeration** of
  D1/D2/D5/D6 (a normative freeze — not fabricable without manufacturing a
  kill); consequently no whole-suite item-data inventory or census can even be
  established for those domains; (2) **item data** for ProofWriter (D4), absent
  on disk; (3) the **tight-κ oracle census** (human-annotated, NOT ~$0) — the
  upper sieve already pushes the censused D3 components below full headroom;
  the oracle is the only *defined* lane that could tighten the bound **below
  the upper-sieve result** while remaining kill-sound. The sieve fails to kill
  *here* (κ≈0.67); no general over-counting threshold follows; (4) the census
  pin block + registered Form-A family eligibility (verdict-eligibility,
  POWER §4 step 0).

**No kill is manufactured.** Artifacts: `poc/coverage-census/` (RESULT.md,
`sieve_census.mjs`, `sieve-census.json`, `census-D3-uppersieve.MEASURED.json`,
`power-D3-uppersieve.result.json`, `coverage-census-result.json`).

## Proposed assumptions (coordinator appends if adopted; NOT written here)

Disjoint block ASM-1040 onward (1040–1049 reserved):
- **ASM-1040** [STIPULATED] upper-sieve predicate = surface(question + choices)
  ≥1 covered content lemma (loosest over-counting reading).
- **ASM-1041** [STIPULATED] sieve reuses m0b/d-ext covered-lemma set + machinery
  byte-for-byte (kernel-v0 + molecules-v0, 190 lemmas, m0b 2026-07-08); a
  store/kernel change invalidates these κ (POWER §2.2).
