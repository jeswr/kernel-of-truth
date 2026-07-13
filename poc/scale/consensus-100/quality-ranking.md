# Consensus-100 — blind dual-judge definitional-QUALITY ranking

Complements the embedding-agreement analysis (`scoring.json`, which measures
paraphrase-similarity / judge-Jaccard 0.42) with a **definitional-quality** view,
to answer the maintainer's real question: *does a cheap model set match the two
"more intelligent" models (gpt-5.6-sol + claude-fable-5) on definitional quality,
not just on embedding similarity?*

- **Data:** `consensus.json` → 6 model glosses per concept, 100 concepts.
  99/100 have all six glosses; `predation` is missing `claude-fable-5` (scored on 5).
- **Method:** blind, dual-judge. Per concept the 6 glosses are anonymized to
  `G1..Gn` and shuffled with a **deterministic per-concept permutation**
  (`SHA256(seed=20260713 | concept)` seeding `random.Random`; recorded in
  `label_map`, no wall-clock randomness). Each of two judges independently scores
  **every** gloss 0–3 on the scholarly-definition bar
  (0 = wrong sense / circular / broken; 1 = correct but poor register / padded /
  mis-scoped; 2 = good; 3 = first-rate — sense-correct, non-circular, right
  extension, apt wording, no unnecessary info). Scores are de-anonymized back to
  the true model. Blinding is essential because one gloss per concept is each
  judge's *own*.
  - **Judge A** = `gpt-5.6-sol` (codex isolated-home runner, read-only, reasoning=high).
  - **Judge B** = `claude-opus-4-8` (`claude -p`, define_concept.py pattern, `MAX_THINKING_TOKENS=0`).
- **Completion:** 100/100 concepts scored by **both** judges. 0 errors, 0 caps.
  $0 marginal (subscription auth). Runner `quality_judge.py`; analysis
  `quality_analyze.py`; raw per-judge per-concept scores in
  `quality-raw-judge{A,B}.jsonl`; machine-readable results in `quality-ranking.json`.

---

## 1. Per-model mean quality (0–3, averaged over the two judges and 100 concepts)

| rank | model | Judge A (sol) | Judge B (opus) | **overall** | vendor |
|---|---|---|---|---|---|
| 1 | **gpt-5.6-sol** | 2.68 | 2.72 | **2.70** | GPT |
| 2 | **gpt-5.6-luna** | 2.45 | 2.62 | **2.54** | GPT |
| 3 | **gpt-5.6-terra** | 2.35 | 2.56 | **2.46** | GPT |
| 4 | claude-haiku-4-5 | 1.59 | 2.23 | **1.91** | Claude |
| 5 | claude-opus-4-8 | 1.54 | 2.04 | **1.79** | Claude |
| 6 | claude-fable-5 | 1.48 | 1.97 | **1.72** | Claude |

**The three GPT models sweep the top; the three Claude models take the bottom** —
and *both* judges produce this **identical** ordering, including the Claude judge
(opus) ranking its own vendor's models last:

- Judge A (sol): sol 2.68 > luna 2.45 > terra 2.35 ≫ haiku 1.59 > opus 1.54 > fable 1.48
- Judge B (opus): sol 2.72 > luna 2.62 > terra 2.56 ≫ haiku 2.23 > opus 2.04 > fable 1.97
- Group means: GPT vs Claude = **2.49 vs 1.54** (judge A), **2.63 vs 2.08** (judge B).

Because the Claude judge, scoring blind, still puts every GPT gloss above every
Claude gloss, the gap is **not** a self/vendor artefact — it is a genuine quality
signal. (Judge B is uniformly ~0.3–0.5 more lenient than Judge A, but the *ranking*
is preserved.)

---

## 2. Quality REORDERS the models vs embedding-agreement

| model | embedding-agreement | rank | | quality (overall) | rank | move |
|---|---|---|---|---|---|---|
| gpt-5.6-luna | 0.94 | 1 | | 2.54 | 2 | −1 |
| claude-haiku-4-5 | 0.90 | 2 | | 1.91 | 4 | −2 |
| gpt-5.6-terra | 0.88 | 3 | | 2.46 | 3 | 0 |
| claude-fable-5 | 0.88 | 4 | | 1.72 | 6 | **−2** |
| gpt-5.6-sol | 0.86 | 5 | | 2.70 | 1 | **+4** |
| claude-opus-4-8 | 0.84 | 6 | | 1.79 | 5 | +1 |

**Agreement and quality are different axes.** High paraphrase-agreement does *not*
imply high quality:
- `gpt-5.6-sol` — *lowest* agreement (0.86, 5th) but *highest* quality (2.70, 1st).
- `claude-haiku-4-5` — high agreement (0.90, 2nd) but middling quality (1.91, 4th).
- `claude-fable-5` — mid agreement (0.88) but the *worst* quality (1.72, last), despite
  being the most expensive model.

Embedding-agreement rewards conformity to the consensus paraphrase; quality rewards
actual lexicographic merit. The two views coincide only for the cheap GPT models
(terra, luna), which happen to be both high-agreement and high-quality.

---

## 3. Inter-judge agreement (validates the judge)

Over the 599 gloss instances both judges scored:

| metric | value |
|---|---|
| Pearson r | **0.57** |
| quadratic-weighted κ (0–3) | **0.48** |
| exact agreement | 0.55 |
| within-1 agreement | **0.95** |
| Judge A (sol) grand mean | 2.02 |
| Judge B (opus) grand mean | 2.36 |

Agreement is **moderate** (κ ≈ 0.48, r ≈ 0.57): the two judges do not agree
concept-by-concept on the exact 0/1/2/3 grade, so any single-concept score is
noisy and the *absolute* means are only medium-confidence. But 95% of scores agree
within one point, and — decisively for this report — the two judges agree
**exactly** on the model ranking and on the GPT-over-Claude split. The disagreement
is mostly a calibration offset (opus scores ~0.34 higher across the board), not a
reordering. **Ranking confidence: high; absolute-level confidence: medium.**

---

## 4. Cheapest set matching the sol+fable quality reference

Reference = mean quality of {sol, fable} = **(2.70 + 1.72) / 2 = 2.211**.
Set quality = mean of member per-model qualities; set cost = sum of member costs
(`cost_table_usd_per_concept`).

**Cost–quality Pareto frontier** (every point is a GPT model; all Claude models are
dominated):

| set | cost $/concept | mean quality | clears ref 2.211? |
|---|---|---|---|
| **gpt-5.6-terra** | **0.00369** | 2.455 | ✅ (also within −0.1 tol) |
| gpt-5.6-luna | 0.00459 | 2.535 | ✅ |
| gpt-5.6-sol | 0.07318 | 2.700 | ✅ (quality ceiling) |

**Cheapest quality-matched set = `gpt-5.6-terra` alone, $0.00369/concept** — the
*same* model the embedding-agreement analysis recommended (`recommended_cheapest_ge95`).
terra costs ~20× less than sol and ~48× less than fable, yet its glosses out-score
the sol+fable reference average.

No Claude model reaches the frontier: e.g. `claude-haiku-4-5` ($0.0059, q 1.91) is
strictly dominated by `gpt-5.6-luna` ($0.00459, q 2.54) — cheaper *and* higher quality.

**Reference sensitivity** — the recommendation's survival depends on how the bar is set:

| reference | value | cheapest matching set (±0 / −0.1 tol) |
|---|---|---|
| mean{sol, fable} | 2.211 | **terra $0.00369** / terra $0.00369 |
| sol alone | 2.700 | sol $0.07318 / sol $0.07318 |
| max{sol, fable} | 2.700 | sol $0.07318 / sol $0.07318 |

Against the maintainer's literal reference (the *average* of the two "intelligent"
models) a cheap model matches. Against **sol alone** (the single best model) there is
**no** cheap substitute even with tolerance — you must pay for sol; the terra→sol gap
(0.245) exceeds the 0.1 tolerance. The average-reference bar is low precisely because
`claude-fable-5`, the most expensive model, writes the lowest-quality glosses and drags
the reference down.

---

## 5. Illustrative example — why GPT out-scores Claude

Concept **`drive`** (WN: *"the act of driving a herd of animals overland"*), the
largest GPT-over-Claude quality gap (Δ 1.83):

| score | model | gloss (truncated) |
|---|---|---|
| 3.0 | gpt-5.6-sol | "The organized act of causing and guiding a herd of animals to travel together across land." |
| 3.0 | gpt-5.6-luna | "The act of directing a herd of animals to travel together across land from one place to another." |
| 3.0 | gpt-5.6-terra | "The act of causing a herd of animals to travel over land … by directing and urging their movement." |
| 1.5 | claude-opus-4-8 | "The act of moving a large group of animals together across country on foot, someone guiding and urging …" (verbose) |
| 1.0 | claude-fable-5 | "… people make many animals travel together across country for a long time …" (padded, mis-scoped) |
| 1.0 | claude-haiku-4-5 | "… by **driving** them forward …" (**circular**) |

The recurring failure modes that cost Claude glosses points: **circularity** (defining
`drive`/`lover` with *drive*/*love*), **padding/verbosity**, and **over-specification**.
GPT glosses are consistently more economical and sense-precise — exactly the
scholarly-definition bar.

---

## 6. Bottom line

- **Does the cheap-ensemble recommendation survive the quality view?** **Yes.** The
  cheapest quality-matched set is `gpt-5.6-terra` alone ($0.00369/concept) — identical
  to the embedding-agreement recommendation — and it *exceeds* the sol+fable reference
  average (2.46 vs 2.21). The quality view **strengthens** the case for the cheap GPT
  models rather than overturning it.
- **But quality reorders the models sharply.** The ranking is
  **sol > luna > terra > haiku > opus > fable**, not the agreement ranking. The three
  cheap-to-mid GPT models are the three *highest-quality* definers; the three Claude
  models (including the two most expensive models overall, fable and opus) are the
  three lowest. High embedding-agreement did **not** predict high quality
  (haiku, fable).
- **Caveats.** (1) Inter-judge κ ≈ 0.48 — the ranking is robust (both judges agree
  on it) but absolute means are medium-confidence. (2) The recommendation matches the
  *average* of {sol, fable}; it does **not** match `sol` alone — if the maintainer's bar
  is "as good as the best model," only sol clears it and there is no cheap substitute.
  The average bar is low mainly because fable is weak. (3) Judges ran in their standard
  configs (codex reasoning=high; opus thinking off) — a known calibration asymmetry
  (opus +0.34 leniency) that shifts levels, not ranks.

*Uncommitted; outputs under `poc/scale/consensus-100/`. $0 marginal.*
