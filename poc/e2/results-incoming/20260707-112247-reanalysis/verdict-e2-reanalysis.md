# E2 re-analysis — sentence-embedding baselines + polarity strata

**POST-HOC RE-ANALYSIS** (notes/panel-kernel-design-review.md change 1; beads kernel-of-truth-qha, kernel-of-truth-avt). The original pre-registered verdict below stands as reported; nothing here replaces it.

date: 2026-07-07T11:34:21.803296+00:00  |  seed: 20260707  |  perms: 10000  |  kernel: jl512  |  layer: L/2
embedders: sentence-transformers/all-MiniLM-L6-v2 (mean+l2norm, rev 1110a243fd); BAAI/bge-small-en-v1.5 (cls+l2norm, rev 5c38ec7c40)

## 1. Original pre-registered verdict (verbatim)

```
# E2 — geometry-alignment probe: verdict

date: 2026-07-07T09:13:02.162798+00:00  |  mock: False  |  seed: 20260707  |  perms: 10000  |  k: 100
encoder: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c`

**Pre-registered primary criterion (poc-design.md E2, verbatim):**
> kernel RDM adds explanatory power beyond baseline relatedness RDMs (word2vec cosine, WordNet path, gloss word-overlap) via partial Spearman, p<0.01, in >=2 of 3 model families; the frequency-matched random word sets must fall below the kernel set (kernel rho > 95th percentile of k=100 random sets) or the result is reported as 'generic relatedness detected'

## OUTCOME: **PRIMARY CRITERION MET**

| model | items | rho (L/2) | Mantel p | partial rho | partial p | partial<0.01 | rand 95th pctl | kernel>pctl |
|---|---|---|---|---|---|---|---|---|
| roneneldan/TinyStories-33M | 51 | 0.2162 | 0.00010 | 0.1653 | 0.00030 | PASS | 0.1108 | PASS |
| HuggingFaceTB/SmolLM2-135M | 51 | 0.2589 | 0.00010 | 0.2137 | 0.00010 | PASS | 0.1913 | PASS |
| Qwen/Qwen2.5-0.5B | 51 | 0.4022 | 0.00010 | 0.3136 | 0.00010 | PASS | 0.3064 | PASS |

Per-model in-vocabulary lists (pre-registered publication):
- **roneneldan/TinyStories-33M** (51 in-vocab): dropped = none
- **HuggingFaceTB/SmolLM2-135M** (51 in-vocab): dropped = none
- **Qwen/Qwen2.5-0.5B** (51 in-vocab): dropped = none

Secondary: embedding-layer and jl576/full-D kernel-variant numbers are in results-e2.json.
Interpretation is conditioned on X3 (polarity); scope limits of poc-design.md Common rule 6 apply.
```

## 2. Reproduction check (re-extracted reps, same runner bytes/image/GPU class)

| model | rho re-run | rho committed | partial(orig3) re-run | committed | delta partial |
|---|---|---|---|---|---|
| roneneldan/TinyStories-33M | 0.2162 | 0.2162 | 0.1653 | 0.1653 | +0.0000 |
| HuggingFaceTB/SmolLM2-135M | 0.2589 | 0.2589 | 0.2137 | 0.2137 | +0.0000 |
| Qwen/Qwen2.5-0.5B | 0.4022 | 0.4022 | 0.3136 | 0.3136 | +0.0000 |

## 3. Forward: kernel partial rho (p) by covariate set

| covariates | TinyStories-33M | SmolLM2-135M | Qwen2.5-0.5B |
|---|---|---|---|
| orig3 | 0.1653 (p=0.0004) | 0.2137 (p=9.999e-05) | 0.3136 (p=9.999e-05) |
| orig3+glossEmb.minilm | 0.1563 (p=0.0006999) | 0.1939 (p=9.999e-05) | 0.3003 (p=9.999e-05) |
| orig3+glossEmb.bge | 0.1530 (p=0.0011) | 0.1906 (p=9.999e-05) | 0.2995 (p=9.999e-05) |
| orig3+explEmb.minilm | 0.1846 (p=0.0002) | 0.1746 (p=9.999e-05) | 0.2830 (p=9.999e-05) |
| orig3+explEmb.bge | 0.1503 (p=0.0013) | 0.1753 (p=0.0002) | 0.2839 (p=9.999e-05) |
| orig3+emb4 | 0.1700 (p=0.0004) | 0.1839 (p=9.999e-05) | 0.2934 (p=9.999e-05) |
| emb4 | 0.1796 (p=0.0004) | 0.1754 (p=0.0002) | 0.3120 (p=9.999e-05) |
| glossEmb.minilm alone | 0.1698 (p=0.0004) | 0.1771 (p=9.999e-05) | 0.3367 (p=9.999e-05) |
| glossEmb.bge alone | 0.1697 (p=0.0004) | 0.1863 (p=0.0002) | 0.3475 (p=9.999e-05) |
| explEmb.minilm alone | 0.2053 (p=9.999e-05) | 0.1791 (p=9.999e-05) | 0.3134 (p=9.999e-05) |
| explEmb.bge alone | 0.1600 (p=0.0006999) | 0.1725 (p=0.0002) | 0.3059 (p=9.999e-05) |
| orig3+wordEmb.minilm | 0.1641 (p=0.0004) | 0.2140 (p=9.999e-05) | 0.3186 (p=9.999e-05) |
| orig3+wordEmb.bge | 0.1691 (p=0.0003) | 0.2231 (p=9.999e-05) | 0.3239 (p=9.999e-05) |
| orig3+emb4+word2 | 0.1754 (p=0.0003) | 0.1976 (p=9.999e-05) | 0.3084 (p=9.999e-05) |

## 4. Reverse: embedding-RDM partial rho (p) vs model

| tested RDM | control | TinyStories-33M | SmolLM2-135M | Qwen2.5-0.5B |
|---|---|---|---|---|
| glossEmb.minilm | spearman | 0.2224 (p=9.999e-05) | 0.4060 (p=9.999e-05) | 0.4270 (p=9.999e-05) |
| glossEmb.minilm | partial_kernel | 0.1777 (p=0.0018) | 0.3646 (p=9.999e-05) | 0.3676 (p=9.999e-05) |
| glossEmb.minilm | partial_kernel+orig3 | 0.0976 (p=0.05119) | 0.3153 (p=9.999e-05) | 0.2548 (p=9.999e-05) |
| glossEmb.bge | spearman | 0.2241 (p=0.0003) | 0.3630 (p=9.999e-05) | 0.3457 (p=9.999e-05) |
| glossEmb.bge | partial_kernel | 0.1798 (p=0.0027) | 0.3189 (p=9.999e-05) | 0.2764 (p=9.999e-05) |
| glossEmb.bge | partial_kernel+orig3 | 0.1086 (p=0.05139) | 0.2552 (p=9.999e-05) | 0.1565 (p=0.0007999) |
| explEmb.minilm | spearman | 0.0711 (p=0.1845) | 0.2513 (p=0.0002) | 0.3288 (p=9.999e-05) |
| explEmb.minilm | partial_kernel | -0.0164 (p=0.5609) | 0.1676 (p=0.0116) | 0.2013 (p=0.0006999) |
| explEmb.minilm | partial_kernel+orig3 | -0.0917 (p=0.8691) | 0.1134 (p=0.0483) | 0.0746 (p=0.09609) |
| explEmb.bge | spearman | 0.1742 (p=0.0168) | 0.2555 (p=9.999e-05) | 0.3338 (p=9.999e-05) |
| explEmb.bge | partial_kernel | 0.0939 (p=0.123) | 0.1672 (p=0.007799) | 0.1981 (p=0.0003) |
| explEmb.bge | partial_kernel+orig3 | 0.0208 (p=0.3906) | 0.0928 (p=0.07709) | 0.0530 (p=0.1699) |

## 5. Polarity strata (bead avt; X3 conditioning — post-hoc operationalisation: NOT-presence in the authored explication, 26/51 items)

| model | stratum | n pairs | rho (p) | partial orig3 (p) | partial orig3+emb4 (p) |
|---|---|---|---|---|---|
| TinyStories-33M | both-NOT | 325 | 0.3724 (p=9.999e-05) | 0.2808 (p=0.0006999) | 0.2455 (p=0.0021) |
| TinyStories-33M | one-NOT (polarity-divergent) | 650 | 0.2346 (p=9.999e-05) | 0.1924 (p=0.0002) | 0.1940 (p=0.0002) |
| TinyStories-33M | neither-NOT | 300 | 0.1127 (p=0.07339) | 0.0560 (p=0.2229) | 0.0415 (p=0.2845) |
| SmolLM2-135M | both-NOT | 325 | 0.2723 (p=0.0002) | 0.1979 (p=0.0028) | 0.2092 (p=0.0021) |
| SmolLM2-135M | one-NOT (polarity-divergent) | 650 | 0.2781 (p=9.999e-05) | 0.2506 (p=9.999e-05) | 0.2165 (p=9.999e-05) |
| SmolLM2-135M | neither-NOT | 300 | 0.2210 (p=0.0024) | 0.1646 (p=0.0159) | 0.0729 (p=0.1468) |
| Qwen2.5-0.5B | both-NOT | 325 | 0.4571 (p=9.999e-05) | 0.3665 (p=9.999e-05) | 0.3844 (p=9.999e-05) |
| Qwen2.5-0.5B | one-NOT (polarity-divergent) | 650 | 0.3800 (p=9.999e-05) | 0.3088 (p=9.999e-05) | 0.2930 (p=9.999e-05) |
| Qwen2.5-0.5B | neither-NOT | 300 | 0.3518 (p=9.999e-05) | 0.2792 (p=0.0002) | 0.1528 (p=0.0149) |

| model | item subset | n items | rho (p) | partial orig3 (p) | partial orig3+emb4 (p) |
|---|---|---|---|---|---|
| TinyStories-33M | NOT-items | 26 | 0.3724 (p=0.0003) | 0.2808 (p=0.005699) | 0.2455 (p=0.0129) |
| TinyStories-33M | non-NOT-items | 25 | 0.1127 (p=0.0219) | 0.0560 (p=0.1432) | 0.0415 (p=0.2093) |
| SmolLM2-135M | NOT-items | 26 | 0.2723 (p=0.0007999) | 0.1979 (p=0.0104) | 0.2092 (p=0.008299) |
| SmolLM2-135M | non-NOT-items | 25 | 0.2210 (p=0.0005999) | 0.1646 (p=0.0026) | 0.0729 (p=0.09309) |
| Qwen2.5-0.5B | NOT-items | 26 | 0.4571 (p=9.999e-05) | 0.3665 (p=9.999e-05) | 0.3844 (p=9.999e-05) |
| Qwen2.5-0.5B | non-NOT-items | 25 | 0.3518 (p=9.999e-05) | 0.2792 (p=9.999e-05) | 0.1528 (p=0.006999) |

## 6. Decision-rule outcomes (rules fixed in poc/e2/reanalysis/README.md before extraction)

- kernel beyond text-embedding baselines (partial p<0.01, orig3+emb4, >=2/3 families): **True** — pass: ['roneneldan/TinyStories-33M', 'HuggingFaceTB/SmolLM2-135M', 'Qwen/Qwen2.5-0.5B']
- embedded explication text beyond kernel (partial p<0.01, kernel+orig3, >=2/3 families, any embedder): **False** — pass: {'explEmb.minilm': [], 'explEmb.bge': []}

## 7. Verdict paragraph

<!-- VERDICT-PARAGRAPH (analyst: E2-reanalysis agent, Claude Fable 5, 2026-07-07; written after reading the numbers) -->

E2 is **not deflated**. The re-extraction reproduces the committed run exactly (deltas 0.0000 in
all three families), and the kernel RDM's partial correlation survives the modern text-embedding
baselines essentially unchanged: against the strongest joint covariate set (the three original
baselines plus MiniLM and BGE embeddings of both the gloss text and the rendered explication
text), kernel partial rho is 0.170 / 0.184 / 0.293 (TinyStories-33M / SmolLM2-135M / Qwen2.5-0.5B),
all p <= 4x10^-4, versus 0.165 / 0.214 / 0.314 with the original 2013-era baselines alone — and
adding word-level sentence embeddings on top changes nothing (0.175 / 0.198 / 0.308). Full-D and
jl576 kernel variants agree. The reverse direction is the sharp part: the **embedded
explication text carries no unique signal beyond the kernel** (partial | kernel+orig3: 0/3
families at p < 0.01, best case rho 0.113, p 0.048) — so for E2's purposes the deterministic
TPR/HRR geometry extracts everything the explication text has and more, not the other way round.
The free-text **gloss** embeddings DO carry unique signal beyond the kernel in the two stronger
families (rho 0.26–0.32, p <= 10^-4 in SmolLM2 and Qwen; p ~ 0.05 in TinyStories) — consistent
with the architecture's own posture that the kernel complements rather than replaces
distributional semantics, and a reminder that "the kernel wins" is a claim about unique structured
variance, not about total variance explained. On the pre-registered X3 conditioning: the kernel's
partial signal is *concentrated in polarity-involving pairs* (both-NOT and one-NOT strata all
significant in all families) and is weakest — unreliable at this n — in the neither-NOT stratum
(partial rho 0.04 / 0.07 / 0.15, p 0.28 / 0.15 / 0.015), so the X3 cosine pathology does not
erase the E2 signal where negation is in play, but the kernel's unique contribution over text
embeddings within purely non-polarity vocabulary is thin in the two smaller families and should
not be quoted without this caveat. Honest bottom line: structured kernel geometry **does** add
explanatory power beyond sentence-embedded definitions in this experiment's terms; the
deflationary reading ("Hill et al. 2016 with extra steps") is rejected on these items, at this
scale, for these three families — with the scope limits of poc-design.md Common rule 6 unchanged.

