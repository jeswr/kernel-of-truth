# X1 — adversarial single-edit margin suite

date: 2026-07-07T04:34:46.574Z
encoder content-hash: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c`
n = 10000, skipped (no applicable edit): 119

## Headline

- fp16 round-trip noise floor (max over 200 vectors): **0.000252 rad**
- min adversarial single-edit angle: **0.011962 rad**
- ratio: **47.4x floor** -> **SUCCESS** (success >5x, failure <2x)

## Adversarial angle distribution (radians)

| suite | n | min | p1 | p5 | median | p95 | max |
|---|---|---|---|---|---|---|---|
| all | 9881 | 0.0120 | 0.0307 | 0.0510 | 0.1942 | 0.7506 | 1.0577 |
| operator-flip | 1228 | 0.0306 | 0.0517 | 0.0835 | 0.2348 | 0.4785 | 0.4830 |
| clause-swap | 2119 | 0.0435 | 0.1240 | 0.3264 | 0.5840 | 0.9231 | 1.0577 |
| referent-index | 991 | 0.0160 | 0.0274 | 0.0429 | 0.1465 | 0.3528 | 0.4182 |
| filler-substitution | 5543 | 0.0120 | 0.0281 | 0.0455 | 0.1457 | 0.3655 | 0.4804 |

## Secondary (near-vacuous, for completeness)

- min pairwise angle over 10000 random synthetics (distinct ASTs): 0.0420 rad (pair 432, 4656); exact-duplicate AST pairs excluded: 1536

> synthetic corpus only; kernel-v0 explications not yet authored (separate stream). Cross-platform leg of the floor is witnessed by X0 goldens.