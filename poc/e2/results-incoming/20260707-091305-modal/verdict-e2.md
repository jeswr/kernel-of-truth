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
