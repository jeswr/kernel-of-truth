# SCALE-1 S1 (100k rung) — multi-source typing portfolio, increment 1: the concept census + UFO-typing-yield probe

**Role:** Fable build agent (builder-scale-s1), 2026-07-13. This ADVANCES the
large-kernel scale track (`docs/next/design/large-kernel-scale-track.md`, the
design; `docs/next/analysis/scale-s0-interpretation.md`, the S0 interpretation
and drafted S1 plan). It is additive to `rules-1-b`, `g2-import-v2`, DDC and
RULES-2 and does not modify, delay or reinterpret them. It touches neither the
locked E0 revision (`engine-inference-under-typing.md`) nor the locked KaE
revision (`glm52-followup-experiment.md`). It issues **no feasibility
conclusion**: CORRECTNESS and EFFICIENCY remain INCONCLUSIVE-PENDING (design §14).

Assumption block: `poc/scale/asm-2050-2059.json` (owner builder-scale-s1; range
ASM-2050..2055 verified free this tick — `grep -c ASM-205[0-9]
registry/assumptions.jsonl` = 0; chosen at 2050 to avoid the E0 (2043-2049) and
KaE (2034-2042) revisions in flight). The build agent does NOT write the registry.

Epistemic tags: **[MEASURED]** read from committed bytes this tick (arithmetic
folded in, steps shown); **[LIT-BACKED]** published grounding; **[STIPULATED]** a
design choice, never evidence; **[EXTRAPOLATION]** a forward claim with its
resolution path named, never a premise.

---

## 0. Which increment, and why it is the cheapest decisive one

The S0 10k readout measured four blockers for the 100k (S1) rung. Two of them
**gate whether the rung can be built at all**, and both are answered by one cheap
local measurement:

- **§2.3 — the selection rule exhausts at 27,210 < 100k.** WordNet-by-frequency
  cannot reach 100k concepts; the design §3.1 *multi-source portfolio* with
  type-level dedup is required. This is a hard prerequisite: no portfolio, no rung.
- **§2.1 — WordNet-only typing yields 0% identity / 0% dependence / 0%
  source-asserted ontic_category.** The design §4.3 hard-typing gate (lower-95%
  precision ≥ 0.95) is unreachable *in principle* on WordNet; the UFO fields must
  come from OBO/BFO anchoring and SUMO commitments (cascade steps 1-2).

The other two blockers are downstream of these: the ANN recall-gate (§2.2) is not
needed *at* 100k (the exact O(m²) scan still runs once at 100k, ~3.2 CPU-h, as ANN
ground truth — it only *dies* between 100k and 1M), and the duplicate/differentia
policy (§2.4) is a pre-registration that operates on the corpus the portfolio
produces. So the portfolio is the load-bearing unblocker, and **its first
measurable increment is a census, not a build**: before ingesting, crosswalking
and vectorising 100k records (the S1 dominant cost, 2-4 weeks engineering), we can
measure — over bytes already in the repo, in CPU-seconds — whether the union
*reaches* 100k and whether OBO/SUMO *move the UFO fields off zero*. If either
answer were "no", the whole S1 sequence would need redesign before any compute is
spent. That is exactly the "decisions that change downstream numbers before the
compute they change" discipline of the S0 plan §3.

**Increment 1 = the multi-source concept census + UFO-typing-yield probe.**
Artifact: `poc/scale/src/census.ts`; run `cd poc && npm run scale:census`
(wall 2.6 s, one niced core); outputs `poc/scale/results/scale-s1-census.{json,md}`.

## 1. What it measures, and what it deliberately does not

It reads only local, license-manifested bytes: `data/lexical-wn31` (WordNet 3.1),
`data/onto-obo` (12 OBO ontologies, 96,192 records), `data/onto-sumo` (SUMO 3,705
terms). No download, no license fetch, no GPU.

It measures **YIELD** — how many records *can* carry a source-asserted or
candidate UFO value — over the design §4.1 cascade steps 1-2 (imported commitment
+ crosswalk). It does **NOT** measure **PRECISION** — whether those values are
*correct* — because that requires the §4.3 stratified human audit, which this does
not perform and does not substitute for. This distinction is load-bearing: a
nonzero yield licenses "the portfolio has an evidential path to the UFO fields",
NOT "the portfolio passes the 0.95 gate".

## 2. Measured results (this tick) [MEASURED — `poc/scale/results/scale-s1-census.json`]

### 2.1 §2.3 — the union clears 100k (blocker retired)

| §3.5 count | value |
|---|---:|
| raw source records (WN 117,791 + OBO 96,192 + SUMO 3,705) | 217,688 |
| type-level clusters — **unmerged union upper bound** | **207,733** |
| — WordNet type-level (non-instance synsets) | 110,049 |
| — OBO classes | 95,201 |
| — SUMO classes | 2,483 |
| clears 100k **before** cross-source merge? | **YES** |

The union headroom is >100k where the tag_cnt rule floored at 27,210 (ASM-2050).
**Caveat (load-bearing):** this is a *pre-dedup upper bound*. Cross-source
duplicates (WordNet `cell` ↔ CL cell) are not merged, so the true post-crosswalk
type-level count is lower; the exactly-crosswalked and fully-resolved counts of
§3.5 are deliberately **NOT COMPUTED** (they need the S1 dedup engineering and
human endorsement). What is retired is the *exhaustion* blocker, not the exact
count.

### 2.2 §2.1 — OBO/SUMO move the UFO fields off zero (evidential path shown)

| field | WordNet-only (S0) | multi-source yield (this probe) |
|---|---|---|
| source-asserted ontic_category | **0%** | OBO is_a*→BFO: **54,018 / 95,201 = 56.74%**; SUMO subclass*: 2,482 / 3,705 = 67.0% |
| identity-provider candidate | **0%** | OBO genus-differentia genus chain: **24,693 / 95,201 = 25.94%** |
| dependence candidate | **0%** | OBO RO relationship edges: **46,755 / 95,201 = 49.11%** |
| argument/selectional typing | 0% | SUMO domain/range axioms: 177+170 term-level |

OBO BFO-reached ontic distribution: disposition 32,048 (MONDO diseases), object
18,948 (UBERON 14,974 + CL 3,325 + PO 1,659), mode 1,929 (PATO qualities), region
691, event 385, quality 13, role 2, proposition 2 — a metaphysically sensible
spread, not a spurious collapse. The genus count 24,693 sits within 0.5% of the
design's independently-cited 24,578 genus-differentia definitions (§1.1) — an
extraction/closure cross-check (ASM-2052).

### 2.3 The 56.74% is a floor set by the local extraction, not a ceiling [MEASURED, ASM-2053]

GO (38,256 records, 40% of OBO) reaches **zero** BFO anchors, because its three
roots (biological_process / molecular_function / cellular_component) carry no
explicit `is_a→BFO` edge in the local jsonl, whereas MONDO does (disease `is_a`
BFO:disposition). 40,779 OBO classes (42.83%) currently type only via the
ontology-grounded fallback (a STIPULATED per-ontology-root → category crosswalk,
reported separately and never conflated with the source-asserted yield). Closing
that gap — loading per-ontology BFO bridge axioms and the SUMO↔WordNet mapping —
is the S1 crosswalk step, *not new science*; the source-asserted yield rises when
the bridges are loaded.

**Increment 2 executed this [MEASURED, ASM-2056].** Loading the pinned
`data/onto-obo/bfo-bridge.json` (14 rows recovering the root→BFO edges the
subset-only extractor dropped — GO's 3 roots, SO's 4, CHEBI/NCBITaxon orphans,
MONDO:injury, OGMS→IAO/OBI; LIT-BACKED per row bar 2 STIPULATED) raises the OBO
source-asserted ontic yield from **56.74% → 99.99%** (+41,171 records; only 12
residual, all legitimately un-anchorable — the BFO root itself, RO relation
classes, obsolete UBERON — ASM-2058). The confirmed floor→ceiling lift closes
§2.1 as a *sourcing* gap: the OBO leg now carries a source-asserted UFO
`ontic_category` for essentially every class. PRECISION (the §4.3 0.95 bar) is
still a separate human-audit measurement.

### 2.4 The domain-balance gap [MEASURED, ASM-2054]

The source-asserted-typed mass is **entirely biological** (OBO = 45.83% of the
union; all of OBO is bio; largest single ontology GO = 18.42%). NCBITaxon is only
402 records locally, so single-*taxonomy* domination (the design's §0 worry) is
not the local risk — single-*domain* (biology) is. A design §0 domain-balanced
100k (count excluding single-domain domination) therefore needs a **non-biological
structured source with source-asserted typing** — the Wikidata class subset (§3.1,
CC0) — which is **not yet local**. This is the single missing ingredient for a
domain-balanced (as opposed to merely 100k-sized) rung.

## 3. The full increment sequence (this census is step 1 of 7)

The census retires the two rung-gating blockers on paper; the remaining S1 steps,
in the order that puts number-changing decisions before the compute they change
(carried from S0 interpretation §3.6, refined by the census):

| step | item | addresses | cost [tag] |
|---|---|---|---|
| **1 (done)** | **multi-source census + typing-yield probe** | §2.3, §2.1 | **2.6 s, $0 [MEASURED]** |
| **2 (done)** | **load recovered BFO bridges (`data/onto-obo/bfo-bridge.json`); re-run census** → source-asserted OBO ontic yield **56.74% → 99.99%** (+41,171 recovered, 12 residual) | §2.1 floor | **3.6 s, $0 [MEASURED, ASM-2056]** |
| **3 (done)** | add the Wikidata non-bio slice (4 domains, off-box Modal, exact external-ID decontam); **4-source census → biology share 49.77%, clears §0 45-65% band** | §0 balance | **~$0.033 total [MEASURED, ASM-2199/2200]** — prereg `scale-s1-position-ingest-prereg.md` |
| 4 | pre-register S1 selection rule + duplicate/differentia policy (§2.4) + §4.3 audit design | §2.3, §2.4 | ~1 wk design, $0 compute |
| 5 | source↔source exact crosswalk + type-level dedup → the §3.5 exactly-crosswalked & type-level counts | §2.3 exact | 2-4 wks engineering (S1 dominant cost); CPU-days [EXTRAPOLATION] |
| 6 | SCC fixture on the OBO 1,142-term SCC (multi-round §6.3 determinism) + vectorise 100k (six stores) | cycles, — | <1 + ~1.1 CPU-h [EXTRAPOLATION from S0 39.3 ms/concept] |
| 7 | one-off exact O(m²) ground truth + ANN build + ≥0.99 recall gate; metrics under the frozen policy | §2.2 | ~3.2 CPU-h exact + hours ANN [EXTRAPOLATION] |

**Cost envelope.** The whole S1 rung stays inside the design's §8 S1 band
(200-2,000 CPU-h; ~$200-1,000 cloud-equivalent; 4-8 weeks), with wide compute
headroom — the schedule risk is concentrated in step 5's crosswalk engineering and
the step 4 human-audit hours, exactly as the design's §10 [EXTRAPOLATION]
anticipated ("dominated by crosswalks, typing audits… rather than GPU time").
Increment 1 (this census) cost **$0 and 2.6 s**; increments 2-3 (bridge load +
Wikidata) — the next cheap, decisive measurements — cost single-digit CPU-hours
and $0-20, and each *re-runs the same census script* to measure the yield lift
before any 100k vectorise is committed.

## 4. Connection to the KaE / F1-K need [EXTRAPOLATION, ASM-2055; load_bearing=false]

F1-K (Kernel-as-Expert on GLM-5.2) is gated by **G-lex** — a harness-side lexical
phrase→concept matcher — and an **n_min = 240 benchmark-coverage gate** (the
kernel must cover ≥240 MMLU-pool items' concepts to have power)
(`poc/glm52-probe/interpretation-fable.md` §4). F1-K's full claim — that *kernel
content* helps a frontier model, not that *any* content helps — needs a real
**concept→content map** whose **scale governs whether F1-K is a toy demonstration
or an impactful result**:

- **Minimal first map (instruments the gate):** the ~24 probe concepts + the
  WordNet backbone. Enough to run F1-K on a hand-picked *known-concept subset* of
  MMLU and check the mechanism — but a coverage island, not a broad claim.
- **What makes F1-K impactful:** MMLU has an open-domain concept inventory. A
  bio-heavy ~208k union covers it only sparsely (the census shows the structured,
  source-asserted mass is 100% biology — §2.4). Moving F1-K from "known-concept
  subset" to "broad MMLU coverage that survives the concept-agnostic deflator"
  needs a **sense-split, domain-balanced kernel at ≥1M concepts** (design §7.7
  reach-and-successful-use; §10 SCALE-GROUND-1M). The sense-split requirement is
  not cosmetic: G-lex maps *phrases* to concepts, and a word-level kernel
  mis-routes polysemous triggers (the `break`-event-vs-material failure of
  `sense-split-first-construction.md`) — so the concept→content map F1-K consumes
  must be sense-split *and* large.

**Stated plainly:** the census-scale (~208k, biology-heavy, word-level) union is a
**machinery-qualification** corpus — it can instrument F1-K's gate on a subset and
qualify the vectoriser, but it cannot make F1-K an *impactful* result. That needs
the domain-balanced, sense-split **≥1M** kernel the S1→S2 sequence builds toward.
**Resolution path:** count G-lex's MMLU-pool concept coverage against (a) the
current census union and (b) a projected domain-balanced 1M union, to quantify the
coverage lift F1-K would gain — a cheap harness-side measurement that needs no
GLM-5.2 instance. This is [EXTRAPOLATION], load-bearing=false: no S1 or KaE
decision rests on it until measured.

## 5. Claim caps

**What increment 1 licenses** (all [MEASURED]-scoped to the local shards, all
YIELD not PRECISION):

- the WN∪OBO∪SUMO union has >100k type-level headroom — the §2.3 selection-rule
  exhaustion blocker is retired by the portfolio (exact post-merge count still
  open);
- OBO/SUMO give a nonzero source-asserted-ontic (56.7%), identity-provider-
  candidate (25.9%) and dependence-candidate (49.1%) yield where WordNet-only gave
  0% — the §2.1 evidential-path blocker has a demonstrated path;
- the source-asserted yield is a floor raised by loading BFO bridges (GO gap
  measured), and a domain-balanced rung needs a non-biological source (Wikidata).

**What it does NOT license** — hard caps:

- **No feasibility conclusion**: CORRECTNESS and EFFICIENCY remain
  INCONCLUSIVE-PENDING regardless (design §14). This qualifies S1 machinery; it
  does not test the thesis.
- **No typing-PRECISION claim**: yield ≠ correctness; the §4.3 0.95 gate has no
  estimator until the human audit runs (step 4).
- **No exact type-level count**: the 207,733 is a pre-dedup upper bound.
- **No transfer to construction B**: every number here is a property of the local
  extractions and the import path; nothing touches kot-enc-B/1.
- **No scale-thesis evidence**: the governing question (design §0, §7.2) is
  answered only by the SCALE-GROUND nested interaction at 1M with ≥30%
  tail-exposed items and a causally active store — none of which exists at census
  or at 100k.

---

*This document issues no feasibility conclusion. Registration of ASM-2050..2055 is
a coordinator action; this document only cites the candidates in
`poc/scale/asm-2050-2059.json`.*
