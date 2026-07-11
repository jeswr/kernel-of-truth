# coverage-census — D3 lemma-touch upper-sieve census + normalised coverage ceiling

**Run by:** Fable experiment agent, 2026-07-11 · **rev-2** (2026-07-11) after
GPT-5.6 review `poc/gpt56-review/rev-covcensus-20260711/` — arithmetic fix
(uncensused mass 0.8235 → 0.80950) + scope-wording narrowed · **Builds on:**
`poc/p3-power/` (POWER rig `power.py`, result `coverage-ceiling-result.json`) ·
**Design:** `docs/next/design/POWER.md` rev-2 §2.1 (census lanes), §3.1
(whole-index completeness rule) · **Governance:** no git / no bd / no kb-sync;
**no frozen record touched**; all outputs confined to `poc/coverage-census/` +
`docs/next/analysis/coverage-census.md`; **no verdict, no registry write**.

Tags: **[MEASURED]** computed count · **[COMPUTED BOUND]** measured κ combined
with a PROVISIONAL/STIPULATED pin · **[STIPULATED]** method choice ·
**[EXTRAPOLATION]** a forward conclusion left to the coordinator.

---

## 0. The question POWER left open, and what "complete" requires

POWER measured the general-index coverage ceiling at **Δ_max simUCB95 ≈ 0.8095**
and stated it **could not deliver a formal general-index kill** — not because
coverage is nonzero, but because the existing censuses are **INCOMPLETE**: they
cover exactly one domain (D3), so the bound is dominated by *full-headroom
imputation* for the five uncensused domains + two uncensused D4 benchmarks. The
measured slice (D3, mapper-parse lane) contributed **0/1550 → 0**.

Per POWER §2.1 / §7, a **complete** census that could formally kill (or fail to
kill) the store-dependent general-index families requires:

1. a **FROZEN `P3-D-INDEX` pin** that *enumerates every benchmark of every
   weighted domain* D1…D6 (chance/ceiling/metric_type/weight);
2. a coverage census over the **whole enumerated suite** in a **kill-SOUND
   lane**. Two lanes exist (POWER §2.1): the **lemma-touch UPPER SIEVE**
   (mechanical, CPU-only, ~$0, *over-counts* so a kill firing under it is
   unconditional) and the **ORACLE** lane (gold-parse + best-endorsement,
   **human-annotated, NOT ~$0**);
3. the census pin block + a registered Form-A family-eligibility ref
   (verdict-eligibility, POWER §4 step 0).

This run does the cheapest sound thing that is actually computable **for the
one lane available to it**: it builds and runs the **lemma-touch upper sieve**
(`P3-X-SIEVE-CENSUS`, the tier POWER named as *missing and cheap*) over the
**7-benchmark D3 suite**, on the normalised index scale. This is a **D3-suite
census**, not a full-suite census: CLUTRR item data exists on disk but was
intentionally excluded (authored against the store, §4), ProofWriter has no
item data, and D1/D2/D5/D6 have no enumerated benchmarks to census.

## 1. What was BUILT + RUN

`poc/coverage-census/sieve_census.mjs` — a deterministic (no RNG/clock) CPU pass
that reuses the **byte-identical** m0b / d-ext covered-lemma machinery
(`buildLexicon` + `lemmaCandidates` + `irregularBase` + the 204-entry
`FUNCTION_STOPLIST` + the 54 molecules-v0 records → **190 covered lemma types**;
store = kernel-v0 + molecules-v0, the m0b 2026-07-08 instance). The **upper-sieve
predicate** [STIPULATED]: an item is covered iff its surface (question stem + all
answer-choice texts) contains ≥ 1 covered content lemma — the loosest,
most-over-counting reading (no gold parse, no endorsement, no uniqueness filter,
no correct-answer restriction).

Then `poc/p3-power/power.py` on the resulting census
(`census-D3-uppersieve.MEASURED.json`, `coverage_lane=upper-sieve`,
`census_mode=exhaustive`, `label_fn_ub=0.0` — licensed: deterministic mechanical
classifier).

## 2. The MEASURED numbers

### 2.1 Lemma-touch UPPER-SIEVE coverage (the sound / unconditional lane) **[MEASURED]**

| Benchmark | Domain | N | touched | **κ_upper-sieve** |
|---|---|--:|--:|--:|
| OpenBookQA-test | D3 | 500 | 418 | **0.8360** |
| MMLU-college_biology-test | D3 | 144 | 92 | 0.6389 |
| MMLU-college_chemistry-test | D3 | 100 | 43 | 0.4300 |
| MMLU-medical_genetics-test | D3 | 100 | 39 | 0.3900 |
| MMLU-anatomy-test | D3 | 135 | 69 | 0.5111 |
| MMLU-clinical_knowledge-test | D3 | 265 | 158 | 0.5962 |
| MMLU-nutrition-test | D3 | 306 | 214 | 0.6993 |
| **Pooled** | **D3** | **1550** | **1033** | **0.6665** |

The **same** 7-benchmark D3 suite POWER censused at **κ = 0/1550** on the
*mapper-parse* lane measures **κ = 0.6665 pooled (0.39–0.84)** on the
kill-sound *upper-sieve* lane. Careful reading of the ≈0-vs-0.67 gap: the
mapper 0/1550 is a **valid measured result for the mapper-parse instrument**
(not literally an artifact), and that instrument folds in the NL parse gap
(POWER §2.1); but the mapper zero **cannot be treated as oracle coverage**, and
the upper sieve shows the cheap unconditional-kill lane does not confirm it.
Attributing the *entire* gap to NL parsing is [EXTRAPOLATION]: sieve false
positives, missing endorsements, and non-derivability may explain part or even
all of it. The magnitude is consistent with the b-cov "≈49% lemma-touch / 0%
checkability" datum — higher here (67%) because the sieve predicate is the
loosest.

### 2.2 Normalised-scale coverage ceiling under the sound lane **[COMPUTED BOUND: MEASURED κ + PROVISIONAL/STIPULATED pin]**

Provisional pin (`frozen=false`), δ_k=0.03, δ_k^D3=0.05. These ceilings are not
raw measurements: they combine measured sieve counts, the stipulated surface
predicate, provisional (unfrozen) weights/ceilings/margins, the
distribution-free `a_cov=0` imputation, and full-headroom imputations.

| Quantity | mapper-parse (POWER) | **upper-sieve (this run)** |
|---|--:|--:|
| Δ_max scalar simUCB95 (general index) | 0.8095 | **0.9860** |
| — D3 scalar contribution (censused) | 0.0000 | **0.17651** |
| — uncensused full-headroom mass | 0.8095 | **0.80950** |
| **D3 own-axis simUCB95** vs δ_k^D3=0.05 | **0.0000** | **0.8825** |
| Kill arithmetic (scalar) `< 0.03`? | FALSE | **FALSE** |
| Kill arithmetic (D3 own-axis) `< 0.05`? | *TRUE (would fire)* | **FALSE** |

Decomposition check [MEASURED: `power-D3-uppersieve.result.json`]: D3 censused
**0.1765086954** + uncensused/full-headroom **0.8094954649** (D4 CLUTRR 0.13194
+ D4 ProofWriter 0.12755 + D1 0.15 + D2 0.15 + D5 0.15 + D6 0.10) =
**0.9860041603**. *(rev-2 correction: rev-1 reported the uncensused mass as
0.8235, wrongly computed as 1 − 0.1765 — the index's maximum aggregate headroom
is not exactly 1 under the unclamped provisional normalisation. Note the
uncensused mass numerically equals the mapper-parse ceiling 0.8095 because D3
contributed exactly 0 on that lane.)*

## 3. The verdict INPUT (coordinator draws the final verdict; this is its input)

**General-index kill — NOT SUPPORTED / STILL-INCOMPLETE.** Statistic: sound-lane
Δ_max simUCB95 = **0.986 ≫ δ_k = 0.03** under the provisional pin; **0.80950**
of it is full-headroom imputation for D1/D2/D5/D6 (unenumerated), ProofWriter
(no data), and CLUTRR (authored-against-store). No frozen enumeration of the
suite exists, so the full index **cannot be named, let alone censused**.
Replacing the D3 mapper-parse zero with the kill-sound upper sieve **raised**
the provisional bound (0.8095 → 0.9860); and since D3 alone contributes
**0.17651 > δ_k = 0.03**, this cheap D3 sieve run cannot license either a D3 or
a general-index kill under the provisional pin **even if every other component
later contributed zero**. Whether the *eventual* frozen index (weights, margins,
suite composition not yet frozen) can be cheaply killed remains open.
**[COMPUTED BOUND → the forward conclusion is the coordinator's EXTRAPOLATION]**

**Domain-scoped D3 kill — NOT SUPPORTED on the sound lane.** Statistic:
sound-lane D3 own-axis simUCB95 = **0.8825 ≫ δ_k^D3 = 0.05**. The mapper-parse
"would fire" (0.0000 < 0.05) is thereby **dissolved as a cheap unconditional
kill** — the mapper zero cannot be treated as oracle coverage, and the sieve
lane that would have made the kill unconditional does not confirm it. It is
**not** empirically disproved at the exact-oracle level (a positive sieve
result alone does not prove oracle coverage is positive: sieve false positives,
missing endorsements, and non-derivability could account for part or all of the
gap); the oracle census does not exist.

**Why STILL-INCOMPLETE (exactly what is missing):**
- the **FROZEN P3-D-INDEX enumeration** of D1/D2/D5/D6 benchmarks — a normative
  freeze; **not fabricable here** (fabricating weights/benchmarks would
  manufacture a kill). Because those benchmarks are not yet enumerated, **no
  whole-suite item-data inventory or census can be established** for them;
- **item data** for ProofWriter (D4) — absent on disk;
- the **tight-κ ORACLE census** (human-annotated, **NOT ~$0**). The upper sieve
  already pushes the censused D3 components below full headroom; the oracle is
  the only *defined* lane that could tighten the bound **below the upper-sieve
  result** while remaining kill-sound. The sieve fails to license a kill *here*
  (κ≈0.67); no general over-counting threshold follows;
- the **census pin block** + a **registered Form-A family-eligibility** ref
  (verdict-eligibility, POWER §4 step 0) — required for any verdict-eligible
  run.

No kill is manufactured. The measured sound lane **raises** the ceiling
(0.8095 → 0.986) — i.e. completing the D3 lane of the census RAISED the
ceiling. Stated carefully: replacing *full-headroom imputations* with
measurements can only lower or preserve Δ_max (POWER's completeness rule keeps
uncensused cells at full headroom; it does not make new measurements raise the
ceiling). What raised the ceiling here was changing the **already-censused D3
lane** from a mapper zero that is unsound for an unconditional kill to the
generous kill-sound upper-sieve value.

## 4. Scope / honesty lines

- **This is a D3-suite census, not a full-suite census.** "Every benchmark for
  which item data exists" would overstate coverage: CLUTRR item data exists
  (`data/nsk1-clutrr/`) but was intentionally excluded — the corpus is
  **authored against the store** (URN world layer) → its lemma-touch coverage
  is ≈1 by construction, not an external measurement; ProofWriter has **no data
  on disk**. Both remain full-headroom.
- **Provisional pin only.** Every weight/ceiling/δ_k is `frozen=false` →
  ILLUSTRATIVE-ONLY by construction; no G1 verdict issues (as designed). All
  "cannot kill" statements are scoped to **this D3 sieve result under the
  provisional pin**, not to the eventual frozen index.
- **The sieve is an UPPER bound on coverage.** Δ_max is monotone increasing in κ,
  so the sieve gives the *largest* defensible Δ_max: a kill under it would be
  sound; a NO-KILL under it (this run) is the honest, conservative outcome — it
  does **not** by itself prove coverage is high, only that the cheap sound lane
  does not license a kill.
- **NO-KILL scope.** "No unconditional kill is supported by the cheap D3
  upper-sieve run; the rig remains ILLUSTRATIVE-ONLY and emits no G1 verdict."
  This run covers only seven D3 benchmarks; it does not establish results for
  every family, suite component, or possible cheap computation.
- **Reproduce:** `node poc/coverage-census/sieve_census.mjs && python3
  poc/p3-power/power.py --index poc/p3-power/inputs/index-pin.PROVISIONAL.json
  --census poc/coverage-census/census-D3-uppersieve.MEASURED.json`.

## 5. Proposed assumptions (for coordinator; NOT written to registry)

Disjoint block ASM-1040…ASM-1049 (PROPOSED-ASM; coordinator appends to
`registry/assumptions.jsonl` if adopted):
- **ASM-1040** [STIPULATED, load_bearing:false] — upper-sieve predicate =
  surface(question stem + all choice texts) contains ≥1 covered content lemma
  (loosest over-counting reading; no gold parse / endorsement / uniqueness).
- **ASM-1041** [STIPULATED, load_bearing:true] — the sieve reuses the m0b/d-ext
  covered-lemma set + machinery byte-for-byte (kernel-v0 + molecules-v0,
  190 lemma types, 204-stoplist, m0b 2026-07-08 instance); a store/kernel change
  invalidates these κ (POWER §2.2).
