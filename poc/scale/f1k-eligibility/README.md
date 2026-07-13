# f1k-eligibility — F1-K candidate concept pool, (b)+(c) screen (issue #33)

Design-independent eligibility screen over the large-kernel concept pool for
the powered F1-K rebuild. Produces the SCREENED POOL that the in-flight codex
design (criterion (a): explication sourcing + final cluster selection) selects
from. Built by `screen_candidates.py` — 2026-07-13 designer-29 ($0 pass:
no git/registry/freeze/spend, benchmark-blind, byte-deterministic on re-run).

## Criteria screened here

- **(b) clean WordNet-3.1 alignment** — pool = the census's **110,049
  TYPE-LEVEL WN31 synsets** (`poc/scale/results/scale-s1-census.json`; the
  7,742 named-individual synsets excluded). OBO (95,201) and SUMO (2,483)
  clusters are EXCLUDED from (b): the WN↔OBO↔SUMO crosswalk is NOT COMPUTED
  (census S1 step-3) and `data/onto-sumo` carries zero WordNet mappings —
  disclosed, not padded. A future crosswalk can only dedupe INTO synsets
  already screened here, so the WN-only screen is yield-complete for (b).
- **(c) ≥8 known-concept eval items** — counted with the SAME item→concept
  mapping machinery as `poc/glm52-probe/f1k-harness/corpora/build_corpora.py`
  (the kernel-v0 build that yielded 49 clusters / 46 with m≥8): WN synset
  lemmas + derivational '+'-pointer lemmas, OP-4 case-insensitive whole-word
  matching, over the five sha256-pinned benchmark snapshots in
  `data/f1k-eval-v1/source/` (MMLU / ARC-Easy / ARC-Challenge / OpenBookQA /
  CSQA; 19,311 admitted items). Counted over question+options text; the
  draft header/cue byte collisions are FLAGGED per concept (SOP-3), not
  silently counted.

## Headline numbers (coverage-report.json)

| funnel step | n |
|---|---|
| (b) WN-aligned type-level pool | 110,049 |
| matching ≥1 eval item | 50,453 |
| **(c) eligible, m_total ≥ 8** | **28,818** |
| … and header/cue-collision-free | 28,728 |
| … with ≥8 unambiguous-lemma items (SOP-6 aid) | 2,127 |
| greedy DISJOINT-items C lower bound (m≥8 each) | 2,404 (header-clean 2,401) |
| conservative disjoint bound, unambiguous evidence only | **1,475** |

**Adequacy vs the registered power gate (C ≥ 65 clusters each m ≥ 8,
ASM-2271): SUPPORTED WITH LARGE HEADROOM.** Even the most conservative
bound — clusters reaching m ≥ 8 on mutually disjoint items each matched via
a monosemous, lowercase-source direct lemma — is 1,475 ≥ 100+ target ≫ 65.
The kernel-v0 shortfall (C ≤ 54) was a universe problem, not an eval-supply
problem.

## Files

- `screen_candidates.py` — the deterministic screener (all screening
  operationalisations SOP-1..6 documented in its docstring and echoed in the
  report; every reused rule cites `build_corpora.py`).
- `candidate-pool.json` — the ranked 28,818-entry eligible pool: WN synset
  URN, POS, lemmas, gloss, m_total / m_stem / m_unambiguous_lemma,
  per-source breakdown, header_cue_collision + greedy-disjoint flags,
  `rank_by_unambiguous` alternative ranking, existing kernel-v0/molecule
  alignment flags (102 eligible synsets are already hand-aligned).
- `coverage-report.json` — funnel, gate arithmetic, m-distribution,
  item-contention histogram, operationalisations, governance block.

## Cautions for the (a)-design

- Raw `m_total` is inflated for hyper-ambiguous lemmas (single letters,
  function-word senses); select using `m_unambiguous_lemma` /
  `rank_by_unambiguous` and the `header_cue_collision` flag, or re-count m
  for the final selection with its own trigger map (item→cluster assignment
  under DES §R4 depends on WHICH concepts are selected).
- SOP-6 is a heuristic (WN lemma polysemy count + cased-source exclusion),
  not sense disambiguation: closed-class inflection collisions survive it
  (e.g. the area-unit synset "are"). Sense fit is criterion-(a) work.
- Nothing here is frozen; the eventual F1-K trigger map must be rebuilt from
  the design's selected concepts and re-verified header-trigger-free.
