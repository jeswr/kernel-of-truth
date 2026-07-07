# QCERT — quasi-orthogonal codebook coherence certification (kot-enc-Bq/1)

date: 2026-07-07T04:52:14.079Z
algorithm: kot-enc-Bq/1; construction: independent Rademacher(+/-1/sqrt(D)) atoms per (slot,filler), signs from SHA-256 stream label qatom/<D>/<slotId>/<fillerId> (codebookQ.ts; alternatives considered there)
corpus: kernel-v0, content-hash `f23f5211ff1755975dd1ce8128ff810b316051c00ee2c1d56bae488f8f928751`
encoder content-hash @ D=512: `3492799ed73b49a612bebca920421041edd31d7bd4098bcf55da52df127ab9ee`
encoder content-hash @ D=576: `6ad0b2bc01c06447aae8468f500e2a2178e9a40f0d95de048b0418afcaea77db`

## Pairwise |cos| (coherence) — measured vs reference scales

| D | atom set | atoms | pairs | max | p50 | p99 | p99.9 | Welch LB | sqrt(ln m/D) | E[max] random | pairs >= 5/sqrt(D) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 512 | full space | 3999 | 7994001 | **0.2461** | 0.0312 | 0.1133 | 0.1445 | 0.0413 | 0.1273 | 0.2492 | 3 |
| 512 | corpus-realised | 109 | 5886 | **0.1680** | 0.0312 | 0.1172 | 0.1562 | 0.0000 | 0.0957 | 0.1841 | 0 |
| 576 | full space | 3999 | 7994001 | **0.2153** | 0.0278 | 0.1076 | 0.1354 | 0.0386 | 0.1200 | 0.2349 | 1 |
| 576 | corpus-realised | 109 | 5886 | **0.1701** | 0.0278 | 0.1076 | 0.1285 | 0.0000 | 0.0902 | 0.1736 | 0 |

- **Welch LB**: no m-vector codebook in R^D can have max coherence below this; the gap to it is the price of a label-deterministic random construction.
- **sqrt(ln m/D)**: DCV §7.2 typical-pair quasi-orthogonal scale.
- **E[max] random**: expected maximum of P ~ N(0, 1/D) pairs — the concentration target; measured max should sit near it (certifies no pathological pair).
- **pairs >= 5/sqrt(D)**: pairs at/above the decoder matched-filter 5-sigma design floor — each such pair is a potential cleanup confusion; the exact D=8192 codebook has zero.

> D=8192 Hadamard codebook pairwise |cos| < 1e-12 measured (encoder/test/codebook.test.ts) — exact orthogonality is unavailable below 2^13 and the variant floor is nonzero by construction

> Realised set = atom cache of a fresh QuasiCodebook after encoding the
> 54-concept corpus (encodeConceptSetWith). Single-edit mutants stay within
> the same closed atom inventory except for fillers absent from the corpus;
> the FULL-space row above covers every atom any capped explication can use.