# A-E2 — cross-lingual phrase-coverage savings census — RUN-LOG

**Census:** A-E2 (idea A's K-A2 gate metric). **Tier-0, r0-local-cpu, $0, no model calls.**
**Bead:** kernel-of-truth-5iu. **Run date:** 2026-07-10. **Branch:** opus/f2b-replicate-rightsize.
**Spec (authoritative):** `docs/next/io-compression-signoff.md` §3 (N-IOC-S; ASM-0461 input pins,
ASM-0462 bracketing convention); `docs/next/io-compression-ideas.md` §2.1, §2.7 (N-IOC).
**Executed by:** experiment-runner (Opus role). **Epistemic tag on every number: `MEASURED-exploratory`.**

> This is a CENSUS. It informs but does NOT gate the feasibility verdict. There is **NO verdict,
> NO freeze, NO interpretation** in these outputs — interpretation is Fable's lane. Numbers below
> are reported, not adjudicated.

## What was measured

`value(c) = Σ_ℓ w_ℓ · f_ℓ(s) · (bpe_ℓ(s) − 1) · m̂(s,ℓ)` → the achievable **prefill-token-savings
fraction vs number of concepts minted**, per-language + blended, for:
- **languages** en + es + fi + ja (ASM-0461);
- **tokenizers** SmolLM2-135M-Instruct (R1 mandatory) + Qwen2.5-0.5B-Instruct (R4-family);
- **weight arms** uniform (primary) + usage-share (sensitivity);
- **m̂** English-sampled via the a1-hybrid mapper; non-English membership-only (m̂=1, disclosed upper bound);
- **surface filter** all (raw) + wordlike (disclosed sensitivity — see §Flag 3).

`frac_prefill_saved(N) = cum_tokens_saved_per_word(top-N) / mean_bpe_per_word`. Denominator = weighted
mean BPE tokens per LISTED word; unlisted tail (~1% of running text) excluded from num & denom.

## Bracketing (ASM-0462), reported not adjudicated

- per-language unaligned curves = **LOWER** bracket of aligned value;
- blended pooled-unaligned = a tighter **LOWER** bracket at fixed concept budget;
- blended cross-language sum = **UPPER** bracket.
- K-A2 may fire only off the UPPER bracket; a go may rest only on the LOWER bracket; a between-brackets
  landing forces A-F1 (cross-lingual alignment) design before any mint decision.

## Headline (MEASURED-exploratory)

### Per-language prefill savings @ 10,000 concepts (membership; % of prefill tokens)

| tokenizer | lang | mean BPE/word | @10k (all) | @10k (wordlike) | max (cover-all-list) |
|---|---|---|---|---|---|
| SmolLM2-135M | en | 1.165 | 10.65% | 5.90% | 14.16% |
| SmolLM2-135M | es | 1.846 | 37.02% | 34.87% | 45.83% |
| SmolLM2-135M | fi | 3.150 | 46.25% | 44.30% | 68.26% |
| SmolLM2-135M | ja | 3.061 | 57.52% | 56.73% | 67.33% |
| Qwen2.5-0.5B | en | 1.145 | 9.32% | 4.50% | 12.66% |
| Qwen2.5-0.5B | es | 1.407 | 20.35% | 17.52% | 28.95% |
| Qwen2.5-0.5B | fi | 2.682 | 41.04% | 38.74% | 62.72% |
| Qwen2.5-0.5B | ja | 1.345 | 19.73% | 18.02% | 25.63% |

English m̂-weighting (a1-hybrid) barely moves English: SmolLM2 en @10k 10.65%→10.01% (all) /
5.90%→5.28% (wordlike). See §Flag 1.

### Blended prefill savings @ 10,000 concepts (% of prefill tokens; lower / upper bracket)

| tokenizer | weights | m̂ | filter | lower | upper |
|---|---|---|---|---|---|
| SmolLM2-135M | uniform | membership | all | 35.30% | 43.64% |
| SmolLM2-135M | uniform | membership | wordlike | 33.45% | 41.69% |
| SmolLM2-135M | usage-share | membership | all | 18.12% | 21.91% |
| SmolLM2-135M | usage-share | membership | wordlike | 14.45% | 18.15% |
| Qwen2.5-0.5B | uniform | membership | all | 21.11% | 26.74% |
| Qwen2.5-0.5B | uniform | membership | wordlike | 18.47% | 24.01% |
| Qwen2.5-0.5B | usage-share | membership | all | 9.57% | 11.88% |
| Qwen2.5-0.5B | usage-share | membership | wordlike | 5.29% | 7.56% |
| Qwen2.5-0.5B | usage-share | **m̂** | wordlike | **4.79%** | 7.06% |

Full grid (both m̂ modes × both filters × all N in the concept-budget grid) is in
`results/summary.json`. The K-A2 sanity-default floor is <5% blended prefill savings at 10k concepts
(STIPULATED; reset at freeze) — reported for reference only; NOT adjudicated here.

## Observations (descriptive; not conclusions)

- The value curve concentrates overwhelmingly in the **non-English, high-BPE-fertility** cells
  (fi, ja), and English alone sits near the low single-to-double digits — consistent in DIRECTION
  with the design's fertility-asymmetry expectation (now MEASURED on our pinned tokenizers, no longer
  [memory]).
- The result is **strongly tokenizer-dependent**: SmolLM2 tokenizes Japanese ~2.3× more expensively
  than Qwen (ja mean BPE/word 3.06 vs 1.34; ja @10k 57.5% vs 19.7%), because Qwen2.5's vocabulary has
  far more CJK coverage. The A-E3/consumption currency (ASM-0103) is therefore load-bearing.
- The result is **strongly weight-dependent**: an English-dominant usage-share roughly halves the
  blended curve vs uniform.
- Across the full cell grid the blended @10k spans **~4.8% (harshest: Qwen · English-dominant ·
  wordlike · m̂ · lower bracket) to ~43.6% (SmolLM2 · uniform · all · upper bracket)**.

## Flagged decisions the sign-off does not fully pin (for Fable / maintainer ratification)

The primary membership census is fully pinned by ASM-0461/0462 and was run mechanically. Three
sub-methods are NOT byte-pinned by the sign-off; I implemented the most literal reading and flag them
rather than STOP (the fully-pinned primary deliverable exists and the task requests the census run):

1. **English m̂ operationalisation.** ASM-0461 pins "sampled with the a1-hybrid mapper" but not the
   sampling procedure. I used the **isolated-surface a1-hybrid decision** (m̂=0 iff the mapper abstains
   on the surface; else 1; policy sha `e13dc838…`, kernel-v0 manifest). This abstains on only
   **164 / 321,180** English surfaces, so it is a near-no-op discount and is itself an UPPER bound
   (only intrinsic-surface collisions detected; context-dependent polysemy invisible to the 119-entry
   lexicon). The design's "sampling occurrences" implies IN-CONTEXT sampling (M0a-style), which I did
   NOT use because (a) the on-box TinyStories copy is NOT byte-identical to the M0a-pinned corpus
   (19,447,282 B / 21,989 stories vs pinned 19,432,980 B / 21,990), and (b) in-context abstention
   concentrates on already-single-token function words (bpe−1=0), so it is not expected to move the
   savings curve materially either. **Fable to ratify the m̂ estimator.**

2. **usage-share weight numbers.** ASM-0461 pins the arm's existence, not its values. I used an
   illustrative English-dominant web-content-share vector (raw en 0.520 / es 0.055 / ja 0.045 / fi
   0.005, normalised over the 4), tagged **STIPULATED-exploratory**, NOT a measurement. It is a
   sensitivity endpoint only. **Maintainer to ratify at freeze (workload-mix discipline).**

3. **wordlike surface filter (ADDED by this run, disclosed).** The raw wordfreq `large` lists include
   numeric/degenerate tokens ('0000', '00', '00,000') that are BPE-expensive and float to the top of
   the value ranking — inflating especially English (halved by the filter). Not in the sign-off. I
   report BOTH `all` and `wordlike` (≥1 alphabetic char AND no digit; numerator only, denominator over
   all surfaces); neither is adjudicated as canonical. **Fable/maintainer to decide the mint-candidate
   surface universe.**

## Inputs (pinned; fail-closed provenance in run-a-e2.py — full block in results/summary.json)

- wordfreq **3.1.1** `large` lists: en sha `dffae806…`, es `14f326b4…`, fi `98fb4981…`, ja `e6ab743b…`
  (data files inside the pip package; upstream github.com/rspeer/wordfreq).
- SmolLM2-135M-Instruct tokenizer.json @ rev `12fd25f7…` sha `9ca9acdd…`.
- Qwen2.5-0.5B-Instruct tokenizer.json @ rev `7ae55760…` sha `c0382117…`.
- kernel-v0 manifest sha `da56bf1f…`; a1-hybrid mapper policy sha `e13dc838…`.

## Reproduce

```
pip install --user wordfreq==3.1.1 tokenizers   # niced
# fetch tokenizer.json files per the URLs+revisions in results/summary.json (manifest); shas fail-closed
cd poc/a-e2 && nice -n 15 python3 run-a-e2.py    # ~5 min CPU; writes results/*
```

## Governance / provenance for this run

- Wrote NOTHING to `registry/**`. No personal handle or email strings in outputs. Ran no git mutations.
- `python3 tools/registry/registry-check.py` → **PASS** (post-run; poc/a-e2/ additions do not affect it).
- Large re-fetchable binary inputs are `.gitignore`d (pinned by sha in the manifest).
