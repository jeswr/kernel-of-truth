# E2 — geometry-alignment probe: verdict

date: 2026-07-07T03:41:23.448834+00:00  |  mock: True  |  seed: 20260707  |  perms: 1000  |  k: 25
encoder: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c`

**Pre-registered primary criterion (poc-design.md E2, verbatim):**
> kernel RDM adds explanatory power beyond baseline relatedness RDMs (word2vec cosine, WordNet path, gloss word-overlap) via partial Spearman, p<0.01, in >=2 of 3 model families; the frequency-matched random word sets must fall below the kernel set (kernel rho > 95th percentile of k=100 random sets) or the result is reported as 'generic relatedness detected'

## OUTCOME: **NULL (no partial-RSA signal in >=2 families)**

| model | items | rho (L/2) | Mantel p | partial rho | partial p | partial<0.01 | rand 95th pctl | kernel>pctl |
|---|---|---|---|---|---|---|---|---|
| mock/family-a | 48 | 0.0039 | 0.43257 | 0.0168 | 0.27473 | fail | 0.0506 | fail |
| mock/family-b | 48 | 0.0108 | 0.35265 | 0.0118 | 0.35265 | fail | 0.0168 | fail |
| mock/family-c | 48 | -0.0031 | 0.51049 | -0.0155 | 0.67732 | fail | 0.0374 | fail |

Per-model in-vocabulary lists (pre-registered publication):
- **mock/family-a** (48 in-vocab): dropped = ['celebration', 'conversation', 'trustworthy']
- **mock/family-b** (48 in-vocab): dropped = ['celebration', 'conversation', 'trustworthy']
- **mock/family-c** (48 in-vocab): dropped = ['celebration', 'conversation', 'trustworthy']

Secondary: embedding-layer and jl576/full-D kernel-variant numbers are in results-e2.json.
Interpretation is conditioned on X3 (polarity); scope limits of poc-design.md Common rule 6 apply.

**MOCK RUN — pipeline smoke test only; numbers are meaningless by construction.**
