# poc/e2 — E2 geometry-alignment probe: prep + runner

Pre-registration: `docs/poc-design.md` Phase E, **E2** (rev 2). This directory
contains everything E2 needs so the GPU run is one command:

```bash
poc/gpu/launch-e2.sh          # spot g4dn.xlarge, self-terminating, ~$1
# …or on any CUDA box with the repo cloned:
python3 poc/e2/runner/e2_runner.py --device cuda
```

## Layout

- `inputs/` — **generated, committed** artefacts, every one stamped with the
  encoder content-hash and a corpus pin (sha256 of `data/kernel-v0/manifest.json`
  + combined sha256 over all concept files):
  - `items.json` — published item set: 54 concepts, **51 analysed** (see
    deviations), per-item probe word + context-bank class.
  - `kernel-rdm.json` — pairwise cosine over the 54 encoder vectors at
    D=8192 **and** through the two pre-registered fixed JL projections
    (8192→512, 8192→576; bit-identical construction to `poc/harness/x4.ts`,
    so the X4 distortion numbers transfer — Common rule 3).
  - `baseline-word2vec.json`, `baseline-wordnet.json`, `baseline-gloss.json`
    — the three pre-registered relatedness baseline RDMs (51×51).
  - `contexts.json` — 24 naturalistic contexts per word (5 hand-authored
    banks; fail-closed check that no template contains a probe word).
  - `freq-matched-pools.json` — frequency- and frame-class-matched candidate
    pools for the k=100 random word sets.
  - `glove-slice-100d.txt`, `glove-ranks-top100k.txt`, `glove-slice-meta.json`
    — committed GloVe slice (51 words) + frequency-rank list (PDDL licence).
- `harness/` — TypeScript generators (run on the CPU box; all cheap):
  `npm install && npm run inputs` regenerates everything above
  (`fetch-glove` streams ~170 MB from the official GloVe archive but writes
  <2 MB — nothing large ever touches disk).
- `runner/e2_runner.py` — the single-file GPU runner (numpy-only in `--mock`
  mode). Implements the pre-registered analysis: layer L/2 + embedding layer,
  mean-pooling over ≥20 contexts, Mantel permutation over concept labels
  (10^4), partial Spearman vs the three baselines, k=100 frequency-matched
  random sets, per-model in-vocabulary lists, JSON + markdown verdict quoting
  the primary criterion verbatim.
- `test/` — node:test suite (`npm test`): stats parity (TS↔python mid-rank
  tie convention), JL determinism, gloss derivation, WordNet parser sanity,
  template/pool fail-closed checks, cross-artefact pin + item-order
  integration checks.
- `results/` — `results-e2-mock.json` + `verdict-e2-mock.md` from the CPU
  smoke run (pipeline evidence; numbers meaningless by construction). The
  GPU run writes `results-e2.json` + `verdict-e2.md` here on its results
  branch.

## Pre-registered protocol (what the runner enforces)

- Item set: explicated concepts only (kernel-v0 has no bare primes).
- Layer **L/2** per model (`num_hidden_layers // 2`), embedding layer
  reported as secondary; max-over-layers is NOT used (so no max-null needed).
- Each word in **24 ≥ 20** contexts, mean-pooled over the word's tokens
  (offset-mapping exact spans), then over contexts.
- **Mantel permutation over concept labels, 10^4 permutations**, one-sided;
  p = (1 + #{perm ≥ obs}) / (1 + N).
- **Primary criterion (verbatim):** "kernel RDM adds explanatory power beyond
  baseline relatedness RDMs (word2vec cosine, WordNet path, gloss
  word-overlap) via partial Spearman, p<0.01, in ≥2 of 3 model families; the
  frequency-matched random word sets must fall below the kernel set (kernel
  ρ > 95th percentile of k=100 random sets) or the result is reported as
  'generic relatedness detected'."
- Per-model in-vocabulary lists published in the results JSON + verdict.
- Model families: `roneneldan/TinyStories-33M`, `HuggingFaceTB/SmolLM2-135M`,
  `Qwen/Qwen2.5-0.5B`.

## DEVIATIONS AND OPERATIONALISATIONS (read before trusting any number)

Empirical-honesty register: everything below either deviates from the
pre-registered text or fixes a degree of freedom the text left open. Each was
fixed BEFORE any model run.

1. **Item set 51/54.** `has-part`, `maker-of`, `part-of` have multi-word
   labels with no single surface word to probe; excluded from the analysis
   set (they stay in the shipped 54×54 kernel matrices). Published in
   `items.json`.
2. **"word2vec cosine" → GloVe 6B 100d cosine.** The prep brief called for a
   small pretrained embedding slice ("e.g. GloVe 6B.50d"); 100d is used
   because it is the first member of the official archive and hence the only
   one streamable without writing ~800 MB to disk (1 GB budget). Different
   training algorithm than word2vec; same relatedness role.
3. **"WordNet path" → extended-relation-graph path similarity.** Classical
   NLTK `path_similarity` is undefined for adjectives (16/51 items) and
   across POS. Primary matrix uses 1/(1+d) over the full relation graph
   (hypernym/hyponym/instance, similar-to, attribute, derivationally-related,
   pertainym, verb-group; depth cap 16; all POS pooled). The classical
   same-POS hypernym variant (simulated root) is published alongside with
   its coverage mask (`classicalSimilarity`, 1435/2601 cells defined).
   One morphy fallback: `archived → archive`.
4. **Primary kernel variant = jl512.** Common rule 3 fixes the projected
   path and pre-registers both (8192→512) and (8192→576) but does not name
   which is E2-primary. jl512 declared primary; jl576 and full-D reported as
   sensitivity in the results JSON.
5. **Random-set statistic operationalised** (the pre-registered sentence
   underdetermines it): for each of k=100 sets, every item's label word is
   replaced by a frequency- and frame-class-matched random word in the SAME
   contexts; ρ_j = Spearman(kernel RDM, model RDM of the replacement words)
   at L/2; criterion: kernel ρ > 95th percentile of {ρ_j}. Verdict rule:
   PRIMARY MET iff ≥2 families pass partial p<0.01 AND the random-set check;
   "generic relatedness detected" iff ≥2 pass partial but <2 also pass the
   random-set check; else NULL.
6. **Partial-Spearman null** = permute the kernel matrix's concept labels
   only (model + baselines fixed), the direct reading of "Mantel permutation
   over concept labels". (Residual-permutation variants exist; this choice
   is fixed here, before any run.)
7. **Frequency proxy** = GloVe 6B vocabulary rank (corpus-frequency ordered).
   Candidate pools: rank band [r/2, 2r] within the top-100k, WordNet-attested
   in the item's bank POS, not a probe/template word, ≤80 per item. The
   `prep` bank (2 items) uses a hand-listed closed class of locative
   prepositions — only loosely frequency-matched (WordNet indexes no
   prepositions).
8. **In-vocab definition:** tokenize `" "+word` (no special tokens); in-vocab
   iff 1–4 tokens and no UNK id. BPE models never emit UNK for ASCII words,
   so attrition here means "shatters into >4 pieces".
9. **Contexts are deterministic** (all 24 bank templates per word; no
   sampling, so the "seeded" requirement is satisfied vacuously). Known
   naturalism compromises: `kind` (sortal noun) is awkward in definite-NP
   frames; `inside`/`near` share a locative bank; random candidates can be
   less natural in a few frames — this biases the random null toward LOWER
   ρ, i.e. AGAINST the kernel being beaten, so a random-set pass is weaker
   evidence than ideal and is flagged as such.
10. **Gloss word-overlap derivation** — surface word sets from the AST
    (primes/operators/determiners lowercased, first `~`-variant, hyphen
    split; referent kinds; concept refs → referenced slug words; structural
    material contributes nothing; no stopword removal; Jaccard). Full spec in
    `harness/glossRdm.ts`.
11. **X3 conditioning deferred** (at the original run). The pre-registration
    conditions interpretation on X3 polarity-stratified subsets; the runner
    does not compute those strata. LANDED 2026-07-07 as a labelled post-hoc
    analysis (bead kernel-of-truth-avt): `reanalysis/` + the verdict in
    `results-incoming/20260707-112247-reanalysis/` report NOT-presence pair
    strata and item-subset RSA alongside the sentence-embedding baseline
    re-analysis (design-review change 1, bead kernel-of-truth-qha). The
    original verdict stands as reported; quote the neither-NOT-stratum
    caveat from that file with any external use.
12. **Similarity convention.** All shipped matrices are similarity (not
    dissimilarity) matrices; Spearman-based statistics are invariant up to
    sign and the runner states the convention.

## Reproducing on this box (all cheap, `nice`d)

```bash
cd poc/e2 && npm install
npm run inputs       # items → kernel-rdm → gloss → wordnet → glove → word2vec → contexts → pools
npm test             # 12 tests incl. cross-artefact integration checks
python3 runner/e2_runner.py --mock   # CPU pipeline smoke (~1 min, numpy only)
```

Footprint: node_modules ≈ 60 MB (typescript + wordnet-db), inputs ≈ 2 MB,
numpy user-install ≈ 40 MB; GloVe streamed, never stored. Total well under
the 1 GB budget.
