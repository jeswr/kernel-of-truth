# M0b — kernel-expressibility estimate (pre-registered, poc-design.md Phase M)

**Date:** 2026-07-07 · **Caveat:** AGENT-JUDGED single-annotator classification
(Claude Fable 5); criteria stated in `../classify-m0b.py`; no inter-annotator
agreement measured. The pre-registration allows a judgment-based estimate with
criteria stated; treat class boundaries as ±few points.

**Basis:** TinyStories validation split; content-word mass = 1.71M tokens =
**45.6% of all word tokens** (function words excluded by a pinned stoplist).
Top-500 content lemmas cover **80.35%** of content mass; the unclassified long
tail (7,000 lemmas, 19.65%) skews toward rare concrete nouns and names, so the
percentages below are, if anything, generous to coverage.

## Frequency-weighted classes (% of top-500 content mass)

| class | % | meaning |
|---|---|---|
| **kernel (total)** | **28.4%** | dominant sense already in kernel v0 (54 concepts + 65 primes) |
| — kernel-lexicon | 26.0% | surface form in the mapper lexicon today |
| — kernel-synonym | 2.4% | sense covered, surface missing (start→begin, glad→happy, fix→repair, …) — mapper lexicon gaps, not kernel gaps |
| **plausibly profile-1-explicable** | **29.8%** | mental/social/evaluative/speech-act/relational vocabulary (love, ask, try, decide, brave, hello, …) |
| **molecule-needing** | **33.0%** | needs a semantic-molecule tier that does not exist: concrete/taxonomic nouns, body parts and bodily actions (eat, sleep, run, hug, laugh), percepts (colors, taste, temperature), kinship, day/night vocabulary, institutions |
| **out-of-scope** | **8.9%** | proper names (lily alone = 1.8% of content mass), titles, interjections |

## The coverage ceiling, stated unvarnished

- **Profile-1 ceiling ≈ 58% of top-500 content mass** (kernel + explicable),
  i.e. ≈ **26% of ALL word-token mass** once the 45.6% content share is applied
  — and this is TinyStories, the deliberately favourable ~1.5k-word domain.
  On real text (larger vocabulary, heavier named-entity and concrete-noun
  load) the ceiling drops further.
- **A third of content mass is molecule-gated.** No amount of explication
  authoring inside profile-1 reaches dog/water/red/eat/sleep/run; the
  molecule tier is load-bearing for any corpus-level coverage claim, and it
  is currently unbuilt and unsized.
- The current **kernel v0 covers 28.4%** of top-500 content mass, of which
  2.4 points are reachable only after adding synonym surface forms to the
  mapper lexicon (16 lemmas listed in `m0b-report.json` rows with
  `kernelTarget`).
- **False friends** (surface in lexicon, dominant corpus sense NOT the kernel
  sense): like=enjoy, way=route, kind=nice, right=correct — together ≈ 1.2%
  of content mass that the mapper currently maps or abstains on with the
  wrong/contested sense; these are classified by their dominant sense
  (explicable), not credited to the kernel.

Full per-lemma table with notes on borderline calls: `m0b-report.json`.
Reproduce: `node mapper/m0/run-m0b-vocab.mjs <TinyStories-valid.txt> && python3 mapper/m0/classify-m0b.py`
