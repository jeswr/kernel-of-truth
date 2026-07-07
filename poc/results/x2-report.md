# X2 — decode recovery by (depth x clause-count) cell

date: 2026-07-07T02:32:52.090Z
encoder content-hash: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c`
n per cell: 30; exact recovery = canonical-JSON equality; decoder defaults (3 refinement passes).

**Criterion (pre-registered): 100% at depth <= 4 -> FAIL**

| depth (requested) | top clauses | exact | ok-but-wrong | failed | mean measured depth | mean clause nodes | mean min-confidence |
|---|---|---|---|---|---|---|---|
| 1 | 1 | 30/30 | 0 | 0 | 1.0 | 1.0 | 1.000 |
| 1 | 2 | 30/30 | 0 | 0 | 1.0 | 2.0 | 1.000 |
| 1 | 4 | 30/30 | 0 | 0 | 1.0 | 4.0 | 0.999 |
| 1 | 8 | 30/30 | 0 | 0 | 1.0 | 8.0 | 0.997 |
| 2 | 1 | 30/30 | 0 | 0 | 2.0 | 2.0 | 0.971 |
| 2 | 2 | 30/30 | 0 | 0 | 2.0 | 3.4 | 0.960 |
| 2 | 4 | 30/30 | 0 | 0 | 2.0 | 6.3 | 0.945 |
| 2 | 8 | 30/30 | 0 | 0 | 2.0 | 12.9 | 0.920 |
| 3 | 1 | 30/30 | 0 | 0 | 3.0 | 3.0 | 0.972 |
| 3 | 2 | 30/30 | 0 | 0 | 3.0 | 4.6 | 0.934 |
| 3 | 4 | 30/30 | 0 | 0 | 3.0 | 9.0 | 0.901 |
| 3 | 8 | 30/30 | 0 | 0 | 3.0 | 15.9 | 0.879 |
| 4 | 1 | 30/30 | 0 | 0 | 4.0 | 4.0 | 0.971 |
| 4 | 2 | 30/30 | 0 | 0 | 4.0 | 5.7 | 0.946 |
| 4 | 4 | 30/30 | 0 | 0 | 4.0 | 9.5 | 0.914 |
| 4 | 8 | 29/30 | 1 | 0 | 4.0 | 17.2 | 0.853 |
| 5 | 1 | 30/30 | 0 | 0 | 5.0 | 5.0 | 0.969 |
| 5 | 2 | 30/30 | 0 | 0 | 5.0 | 6.9 | 0.930 |
| 5 | 4 | 30/30 | 0 | 0 | 5.0 | 10.7 | 0.894 |
| 5 | 8 | 30/30 | 0 | 0 | 5.0 | 18.8 | 0.848 |
| 6 | 1 | 30/30 | 0 | 0 | 6.0 | 6.0 | 0.968 |
| 6 | 2 | 30/30 | 0 | 0 | 6.0 | 8.0 | 0.932 |
| 6 | 4 | 30/30 | 0 | 0 | 6.0 | 11.1 | 0.896 |
| 6 | 8 | 30/30 | 0 | 0 | 6.0 | 19.3 | 0.864 |

> Decoding is stated, per the construction, as recoverable GIVEN THE KERNEL
> (codebook + lexicon as cleanup memory); depth beyond the SNR budget is
> expected to degrade — that boundary is what this table maps.