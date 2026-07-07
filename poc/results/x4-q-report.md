# X4-q — native re-encode vs JL projection geometry (kot-enc-Bq/1)

date: 2026-07-07T04:53:08.901Z
corpus: kernel-v0 — 54 concepts, content-hash `f23f5211ff1755975dd1ce8128ff810b316051c00ee2c1d56bae488f8f928751`
base encoder (D=8192): `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c`; JL: Achlioptas sign matrix, +/-1/sqrt(d), signs from SHA-256 stream label jl/<D>/<d> (det.ts DET_DOMAIN) — pinned labels reused from harness/x4.ts, no new projections

| d | rho(8192, native) | rho(JL, native) | rho(8192, JL) | min pair (native) | min pair (JL) |
|---|---|---|---|---|---|
| 512 | 0.9711 | 0.9383 | 0.9718 | `afraid`<->`sad` @ 0.1113 | `afraid`<->`sad` @ 0.1107 |
| 576 | 0.9795 | 0.9480 | 0.9706 | `afraid`<->`sad` @ 0.1082 | `afraid`<->`sad` @ 0.1170 |

- d=512: |cos(native) - cos(8192)| over 1431 pairs: median 0.0263, p95 0.0800, max 0.1659
- d=576: |cos(native) - cos(8192)| over 1431 pairs: median 0.0236, p95 0.0729, max 0.1440

> The native re-encode is a DIFFERENT function of the AST, not a compression of the 8192-D vector: rho(8192, native) < 1 reflects codebook-level geometry change (quasi-orthogonal atoms + shared-D binding), while rho(8192, JL) reflects pure metric distortion. E1 interpretation: path-(i) results transfer to path-(ii) only to the extent rho(JL, native) is high.