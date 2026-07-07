# X4 — fixed JL projection distortion

date: 2026-07-07T02:00:05.810Z
encoder content-hash: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c`
corpus: 300 synthetics (298 adversarial pairs); JL: Achlioptas sign matrix, ±1/sqrt(d), signs from SHA-256 stream label jl/<D>/<d> (det.ts DET_DOMAIN)

Full-D reference: min adversarial angle 0.018222 rad; fp16 floor 0.000226 rad.

| projection | RDM Spearman | min adv angle (rad) | median adv angle | fp16 floor (rad) | min/floor |
|---|---|---|---|---|---|
| 8192 -> 512 | 0.9450 | 0.017693 | 0.2108 | 0.000238 | 74.4x |
| 8192 -> 576 | 0.9608 | 0.016702 | 0.2018 | 0.000231 | 72.3x |

> synthetic corpus; re-run on kernel v0 when authored. E-series claims inherit the R^d numbers (poc-design rule 3).