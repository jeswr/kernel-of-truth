# poc/e2/reanalysis — E2 post-hoc re-analysis: sentence-embedding baselines + polarity strata

**Posture (load-bearing):** this is a **LABELLED POST-HOC RE-ANALYSIS** commissioned by
`notes/panel-kernel-design-review.md` change 1 (§3.2). The original pre-registered E2
verdict (`poc/e2/results-incoming/20260707-091305-modal/verdict-e2.md`: PRIMARY
CRITERION MET, 3/3 families) **stands as reported**. Nothing here substitutes for it;
the re-analysis is reported alongside it. Beads: `kernel-of-truth-qha` (this
re-analysis), `kernel-of-truth-avt` (polarity stratification, E2 runner deviation 11).

**The question:** E2's partial Spearman controlled word2vec/GloVe cosine, WordNet
path, and gloss word-overlap — 2013-era relatedness proxies. If a modern sentence
encoder applied to the definition TEXT (kernel-v0 `gloss` field, or a deterministic
rendering of the explication tree) explains the kernel RDM's contribution, then E2
only showed "definitions carry relatedness signal" (Hill et al. 2016), and the
structured TPR/HRR kernel geometry added nothing measurable. Both directions are
tested: kernel beyond embeddings, and embeddings beyond kernel.

## Analysis plan (fixed 2026-07-07, BEFORE the extraction run; amendments would be listed here)

- **Items / kernel variant / layer / stats:** identical to the original run — the 51
  pre-registered analysis items, kernel jl512 primary (full-D + jl576 sensitivity),
  model layer L/2, Spearman with mid-rank ties, one-sided Mantel permutation
  p = (1+#{perm ≥ obs})/(1+10^4), seed 20260707, stats code imported from
  `poc/e2/runner/e2_runner.py` (no forked implementations).
- **Null convention:** permute the concept labels of the **tested** RDM only
  (kernel in forward tests, embedding RDM in reverse tests); model + covariates fixed.
  This generalises the original runner's deviation 6.
- **New baseline RDMs** (cosine, 51×51), computed in one Modal container
  (`poc/modal/modal_e2_reanalysis.py`, same pinned image as the original run):
  - `glossEmb.<embedder>` — kernel-v0 `gloss` field text, embedded;
  - `explEmb.<embedder>` — deterministic explication-tree rendering
    (`build_texts.py`, renderer spec in its docstring), embedded;
  - `wordEmb.<embedder>` — the bare probe word, embedded (descriptive extra);
  - embedders: `sentence-transformers/all-MiniLM-L6-v2` (mean-pool + L2) and
    `BAAI/bge-small-en-v1.5` (CLS-pool + L2) — two families so the result is not
    hostage to one encoder; resolved HF commit hashes recorded in provenance.
- **Forward tests** (tested = kernel jl512): partial Spearman vs model RDM
  controlling (a) orig3 (reproduction of the committed result), (b) orig3 + each new
  embedding RDM severally, (c) orig3 + all four gloss/expl embedding RDMs jointly
  ("the strongest baseline set"), (d) the four embedding RDMs alone, (e) descriptive:
  + wordEmb variants.
- **Reverse tests** (tested = explEmb / glossEmb per embedder): Spearman vs model
  RDM, then partial controlling kernel jl512 alone, and kernel + orig3.
- **Polarity strata (bead avt):** X3's corpus finding is that NOT-edits barely move
  kernel vectors, so the stratification signal is NOT-presence in the authored
  explication (26/51 items carry ≥1 NOT). Reported: (i) pair strata — both-NOT /
  one-NOT (polarity-divergent) / neither-NOT — Spearman + partial(orig3) +
  partial(orig3+emb4) per stratum on masked cells; (ii) item-subset RSA on the
  26 NOT items and the 25 non-NOT items. Post-hoc operationalisation: X3's
  pre-registered edit classes are per-concept mutations, not corpus pairs; this is
  the closest corpus-level analogue and is labelled as such.
- **Decision rules (fixed before any number is seen):**
  - "**kernel adds beyond text-embedding baselines**" iff partial p < 0.01 with the
    joint covariate set orig3+emb4 in ≥ 2 of 3 model families (mirrors the form of
    the original pre-registered rule);
  - the reverse claim ("embedded explication text adds beyond kernel") uses the
    symmetric rule: explEmb partial p < 0.01 controlling kernel+orig3 in ≥ 2 of 3
    families, for at least one embedder;
  - all four outcome quadrants are reportable findings; whatever comes out is the
    finding.

## Layout

- `build_texts.py` — deterministic AST→text renderer + input builder (writes
  `inputs/reanalysis-texts.json`; spec + honesty notes in the docstring).
- `inputs/reanalysis-texts.json` — generated, committed; pins encoderContentHash +
  corpusPin from `poc/e2/inputs/items.json`.
- `analyze.py` — CPU analysis over the Modal extraction output; writes
  `results-e2-reanalysis.json` + `verdict-e2-reanalysis.md` into the stamp dir.
- Extraction entrypoint: `poc/modal/modal_e2_reanalysis.py` (T4, ~minutes;
  `modal_e2.py` untouched). Results land in
  `poc/e2/results-incoming/<stamp>-reanalysis/`.

## Honesty notes

1. The gloss field and the rendered explication text are both NSM-register English;
   they are highly parallel by construction. That parallelism is the POINT of the
   deflation test: if their embeddings carry the kernel's partial-RSA signal, the
   deterministic encoder was not needed for the E2-class evidence.
2. The renderer was written for this re-analysis (no deterministic renderer
   existed); it is one author's fixed operationalisation. Sensitivity to rendering
   choices is NOT explored — two embedders are the only robustness axis here.
3. Model-side representations are re-extracted with the identical runner code,
   image, GPU class and seed; reproduction deltas vs the committed run are reported.
4. The re-extraction reuses the original contexts, items, and kernel/baseline
   matrices byte-identically (sha256-manifest asserted in-container).
