# X4 on kernel-v0 — fixed JL projection distortion

date: 2026-07-07T03:53:49.446Z
corpus: kernel-v0 (authored; research-grade, NOT federation-endorsed) — 54 concepts
encoder content-hash: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c` (matches manifest pin: true)
corpus manifest sha256: `a9efbccdd9c7fe50f614d4687078584da603c5f07dce822cd323e0a5d7f4bdde`
corpus content-hash (concepts/*.json + manifest): `f23f5211ff1755975dd1ce8128ff810b316051c00ee2c1d56bae488f8f928751`
adversarial pairs: 2475 (X1-corpus single-edit neighbour suite); JL: Achlioptas sign matrix, ±1/sqrt(d), signs from SHA-256 stream label jl/<D>/<d> (det.ts DET_DOMAIN) — pinned labels reused from harness/x4.ts, no new projections

Full-D reference: min adversarial angle 0.002342 rad (`archived`, referent-index); fp16 floor 0.000213 rad; ratio 11.0x.

| projection | RDM Spearman | min adv angle (rad) | median adv angle | fp16 floor (rad) | min/floor | X1-criteria verdict |
|---|---|---|---|---|---|---|
| 8192 -> 512 | 0.9718 | 0.002252 (`archived`, referent-index) | 0.1056 | 0.000222 | 10.1x | SUCCESS |
| 8192 -> 576 | 0.9706 | 0.002199 (`archived`, referent-index) | 0.1035 | 0.000223 | 9.9x | SUCCESS |

- min authored pair at d=512: `afraid` <-> `sad` at 0.110712 rad
- min authored pair at d=576: `afraid` <-> `sad` at 0.116987 rad

> E-series claims inherit these R^d numbers (poc-design rule 3). Neighbour suite = X1-corpus seed family x1c/<id>/<s>, deduped, saturation-sampled.