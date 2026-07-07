# X1 — adversarial single-edit margin suite

date: 2026-07-07T02:03:18.372Z
encoder content-hash: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c`
n = 500 (REDUCED run; full pre-registered run is n=10^4 via `npm run x1:full`), skipped (no applicable edit): 5

## Headline

- fp16 round-trip noise floor (max over 200 vectors): **0.000252 rad**
- min adversarial single-edit angle: **0.015988 rad**
- ratio: **63.4x floor** -> **SUCCESS** (success >5x, failure <2x)

## Adversarial angle distribution (radians)

| suite | n | min | p1 | p5 | median | p95 | max |
|---|---|---|---|---|---|---|---|
| all | 495 | 0.0160 | 0.0242 | 0.0478 | 0.2033 | 0.7343 | 1.0441 |
| operator-flip | 67 | 0.0384 | 0.0504 | 0.0698 | 0.2354 | 0.4783 | 0.4820 |
| clause-swap | 109 | 0.1302 | 0.2357 | 0.3120 | 0.6021 | 0.9081 | 1.0441 |
| referent-index | 49 | 0.0160 | 0.0196 | 0.0415 | 0.1561 | 0.3187 | 0.3518 |
| filler-substitution | 270 | 0.0177 | 0.0231 | 0.0432 | 0.1484 | 0.3672 | 0.4804 |

## Secondary (near-vacuous, for completeness)

- min pairwise angle over 500 random synthetics (distinct ASTs): 0.1433 rad (pair 416, 432); exact-duplicate AST pairs excluded: 2

> synthetic corpus only; kernel-v0 explications not yet authored (separate stream). Cross-platform leg of the floor is witnessed by X0 goldens.