# b-cov define-lane census — WiC CELL — RUN-LOG (bead kernel-of-truth-hu10)

**Status:** MEASURED-exploratory counts only. `fable_interpretive_assessed: pending`.
Opus (experiment-runner) reports mechanical counts; the meaning is Fable's to
interpret. NO verdict, NO freeze, NO registry write, NO extrapolation. Every number
below is tagged **MEASURED-exploratory**.
Run date: 2026-07-10. Branch: `opus/f2b-replicate-rightsize`. Tier-0, CPU, ~$0.

This closes the one cell hu10 could not run. It EXTENDS (does not clobber) the
committed hu10 results: new files only (`fetch_wic.py`, `census_wic.py`,
`positive_control_wic.py`, `data/wic-*`, `detail/wic-*`, `wic-census-summary.json`).

## STEP 1 — Mirror investigation (maintainer-delegated)

The canonical pre-declared source `pilehvar/wic` returns **HTTP 401** unauthenticated
(re-confirmed this run). Candidates probed via the HF datasets-server (same path
`fetch_mmlu.py` uses):

| candidate | result |
|---|---|
| `super_glue` config `wic` | **404** — "dataset has been renamed" (deprecated id) |
| `aps/super_glue` config `wic` | **200 accessible** — the current SuperGLUE mirror |
| `SetFit/wic` | **401** gated (not accessible unauthenticated) |
| `pilehvar/wic` (canonical) | **401** gated (unavailable — the original data gap) |

**SELECTED (VERIFIED FAITHFUL): `aps/super_glue` config `wic`.** SuperGLUE
(Wang et al. 2019) incorporates the Word-in-Context dataset (Pilehvar &
Camacho-Collados 2019, NAACL) directly — same items, same task, same labels.

### Faithfulness verification (fail-closed in `fetch_wic.py`; evidence in `data/wic-fetch-manifest.json`)
- **Dev split = 638 items** — the canonical WiC dev count. (train 5428 / test 1400
  also match the official WiC counts.)
- **Schema = `{word, sentence1, sentence2, start1, start2, end1, end2, idx, label}`**
  — exactly the WiC spec. `label` is a ClassLabel with names `["False","True"]`
  → **0 = different sense (False), 1 = same sense (True)** — the canonical WiC
  binary same-sense label.
- **Label balance 319 / 319** — WiC dev is 50/50 same/different by construction.
- **Label semantics spot-checked** against the WiC definition:
  - `label=0`: *class* ("professional class" vs "showed real class"), *stripe*,
    *check* — genuinely different senses. ✓
  - `label=1`: *minister* (clergy in both), *thing* (of spirit / of heart),
    *brush*, *contradistinction* — genuinely same sense. ✓
- **Target-word offsets** `[startK:endK]` recover the target token in both
  sentences: 631/638 lemma-consistent (3-char prefix), 387/638 exact; the 7
  non-prefix cases are legitimate **irregular inflections** (buy/bought,
  leave/left, keep/kept, shake/shook, catch/caught, go/went, rise/rose) — exactly
  WiC's inflected target usage. All 638 spans are in-bounds, non-empty, single-token.
- **`idx` 0..2 dev items = `class` / `stripe` / `check`** — the canonical WiC dev
  head items.

### DISCLOSED-MIRROR provenance flag (census-local; does NOT change fail-closed policy)
- canonical pre-declared source: `pilehvar/wic` — **UNAVAILABLE** (HTTP 401), CC BY-NC 4.0.
- mirror used: **`aps/super_glue` config `wic` split `validation`**
  - HF commit sha: `3de24cf8022e94f4ee4b9d55a6f539891524d646`
  - HF parquet-convert sha: `fd77e85946ac3435f3864f2a34bae3947c1561d0`
  - fetched-byte sha256: `sha256:dccc5a7709e2d016ed6dcab6566039da37dc2a6a1be2fd500f8b04952a5dcaec`
  - license: SuperGLUE packaging CC BY 4.0; underlying WiC data CC BY-NC 4.0.
- **EXPLICIT CAVEAT: exploratory mirror, NOT the canonical `pilehvar/wic` source.**
  Recorded as a census-local disclosed input only. `data/d-ext/manifest.json`
  (the frozen d-ext fail-closed sourcing policy) is **unchanged** — this cell does
  not relax or override it.

## STEP 2 — MEASURED-exploratory result

Item construction (faithful, non-reframing): each WiC dev item is fed as its
verbatim natural-language content — `text = "<sentence1> <sentence2>"`,
`options = [target word]`. Pipeline invoked **identically to hu10's other cells**
(`census.py` machinery reused verbatim via `import census`).

### Headline cell — κ_B^engine (mapper-parse lane)
| benchmark | N_total | N_checkable (§C5 n==1) | **κ_B^engine** | no-template | slot-unresolved | abstain | define-retrieve | candidate-bearing |
|---|---|---|---|---|---|---|---|---|
| **WiC-dev** | 638 | 0 | **0.0000** | 638 | 0 | 0 | 0 | 0 |

**§C5 breakdown (n==0 / n==1 / n≥2): 0 / 0 / 0.** No WiC item reached the §C5
candidate-bearing population (all 638 → `UNMAPPED_NO_TEMPLATE`), so the uniqueness
filter dropped nothing. `instrument_disagreements = 0`. This matches the design
projection that WiC presents no define-question shape [ASM-0019, `load_bearing:false`].

### Supplementary breadth diagnostic (NOT the headline κ_B — clearly labelled)
Of the 638 dev **target words**, how many resolve to a UNIQUE licensed onto-obo
concept, and of those how many carry a `logicalDefinition` (engine DEFINE-retrieve
answerable) — the design's §5.2 "how biomedical/definitional is WiC's vocabulary"
question:

| target-word resolution | count |
|---|---|
| unresolved (no onto-obo label match) | 615 |
| resolved to a unique licensed concept | 21 |
| abstain (>1 candidate URN) | 2 |
| **DEFINE-retrieve `answer` (checkable) over the 21 resolved** | **0** (all 21 → `ERR_NO_DEFINITION`) |

The 21 resolved words are general-vocabulary terms (`get, strand, char, dip, burn,
dig, …`) that collide with an onto-obo label but carry **no** `logicalDefinition`
in the endorsed `{go,so,mondo}` substrate. So **define-checkable-via-retrieve = 0**
as well. (MEASURED-exploratory; interpretation is Fable's.)

## Instrument validity — the 0.0000 is a REAL null, not a broken harness
`positive_control_wic.py` → **WIC-CELL POSITIVE CONTROL: PASS**:
- **(A) headline-path** — re-runs hu10's committed `positive_control.py` verbatim
  (GO:0000018 target): `which term means …` → §C5 **n==1** → DEFINE-MATCH **True**;
  `is X a G that R F` → n==1 → True; `what is X?` → DEFINE-retrieve `answer`.
- **(B) breadth-path** — feeds the WiC breadth diagnostic an in-substrate target
  word ("regulation of DNA recombination"): `resolved_unique=1`, DEFINE-retrieve
  `answer=1`.
So both the headline and the breadth diagnostic yield a positive when one exists;
the WiC nulls are the **measured absence** of define-template-shaped items and of
biomedical-definitional vocabulary, not an instrument failure.

## Engine definitional index at this run (context, identical to hu10)
`defn_licensed=72,839  defn_resolved=13,824  defn_unresolved=3,387`;
`distinct_definition_keys=13,824`; `internal_collision_keys(n≥2)=0`;
`define-index.json` sha256 `4915969c…`; endorsed shards `{go,so,mondo}`.

## Determinism
`census_wic.py` re-run byte-identical `wic-census-summary.json`
(`sha256:1d695895…`). No stray temp files.

## Reproduce
```
python3 poc/b-cov-define-lane/fetch_wic.py            # DISCLOSED faithful mirror -> data/wic-validation.jsonl
python3 poc/b-cov-define-lane/build_define_index.py   # (already committed) DefineIndex over {go,so,mondo}
python3 poc/b-cov-define-lane/census_wic.py           # -> wic-census-summary.json + detail/wic-*
python3 poc/b-cov-define-lane/positive_control_wic.py # instrument-validity PASS
```

## Governance
No `registry/**` write (exploratory). No git. No `@handle`/email strings in outputs.
No child agents. `data/d-ext/manifest.json` fail-closed sourcing policy untouched;
the mirror is a census-local DISCLOSED input. No verdict / interpretation / freeze —
Fable interprets. `python3 tools/registry/registry-check.py` run at close.
