# X1-q — adversarial margins at toy-native D (kot-enc-Bq/1)

date: 2026-07-07T04:54:05.077Z
corpus: kernel-v0 — 54 concepts, content-hash `f23f5211ff1755975dd1ce8128ff810b316051c00ee2c1d56bae488f8f928751`
criteria: per D: success > 5x fp16 floor at that D; failure < 2x; else inconclusive (poc-design X1 restated for kot-enc-Bq/1)

## D = 512

encoder content-hash: `3492799ed73b49a612bebca920421041edd31d7bd4098bcf55da52df127ab9ee`

- corpus fp16 floor (max over 54 authored vectors at D=512): **0.000225 rad** (worst: end)
- min corpus adversarial angle over **2475** neighbours: **0.002543 rad** (`archived`, filler-substitution: pred THERE-IS at clauses.1.roles.quote.clauses.2.args.0.roles.complement.clause.roles.time.restrictedBy.args.1)
- ratio: **11.3x floor** -> **SUCCESS** (pre-registered: success >5x, failure <2x)
- synthetics (n=495): floor 0.000232 rad, min 0.015115 rad = 65.1x -> SUCCESS
- min authored pair: `afraid` <-> `sad` at 0.111314 rad

| suite | n | min | p1 | p5 | median | p95 | max |
|---|---|---|---|---|---|---|---|
| corpus | 2475 | 0.0025 | 0.0114 | 0.0195 | 0.1058 | 0.3189 | 1.1061 |
| corpus/operator-flip | 290 | 0.0041 | 0.0170 | 0.0519 | 0.2374 | 0.3565 | 0.4226 |
| corpus/clause-swap | 82 | 0.0821 | 0.0894 | 0.1296 | 0.6324 | 0.9520 | 1.1061 |
| corpus/referent-index | 357 | 0.0026 | 0.0081 | 0.0244 | 0.1232 | 0.2822 | 0.3235 |
| corpus/filler-substitution | 1746 | 0.0025 | 0.0113 | 0.0189 | 0.0898 | 0.2304 | 0.3503 |
| synthetic | 495 | 0.0151 | 0.0284 | 0.0499 | 0.2035 | 0.7612 | 1.0726 |

### 5 tightest per-concept minima

| concept | neighbours | saturated | min angle (rad) | x floor |
|---|---|---|---|---|
| archived | 62 | true | 0.002543 | 11.3x |
| promise | 63 | true | 0.007379 | 32.8x |
| sad | 44 | true | 0.011026 | 49.0x |
| afraid | 31 | true | 0.012110 | 53.8x |
| kind | 122 | true | 0.013149 | 58.4x |

## D = 576

encoder content-hash: `6ad0b2bc01c06447aae8468f500e2a2178e9a40f0d95de048b0418afcaea77db`

- corpus fp16 floor (max over 54 authored vectors at D=576): **0.000223 rad** (worst: part-of)
- min corpus adversarial angle over **2475** neighbours: **0.002136 rad** (`archived`, filler-substitution: pred THERE-IS at clauses.1.roles.quote.clauses.2.args.0.roles.complement.clause.roles.time.restrictedBy.args.1)
- ratio: **9.6x floor** -> **SUCCESS** (pre-registered: success >5x, failure <2x)
- synthetics (n=495): floor 0.000258 rad, min 0.015190 rad = 59.0x -> SUCCESS
- min authored pair: `afraid` <-> `sad` at 0.108193 rad

| suite | n | min | p1 | p5 | median | p95 | max |
|---|---|---|---|---|---|---|---|
| corpus | 2475 | 0.0021 | 0.0094 | 0.0182 | 0.1025 | 0.3195 | 1.0731 |
| corpus/operator-flip | 290 | 0.0036 | 0.0153 | 0.0467 | 0.2306 | 0.3541 | 0.4167 |
| corpus/clause-swap | 82 | 0.0746 | 0.0873 | 0.1246 | 0.6366 | 0.9735 | 1.0731 |
| corpus/referent-index | 357 | 0.0022 | 0.0079 | 0.0222 | 0.1214 | 0.2776 | 0.3105 |
| corpus/filler-substitution | 1746 | 0.0021 | 0.0093 | 0.0176 | 0.0866 | 0.2326 | 0.3416 |
| synthetic | 495 | 0.0152 | 0.0282 | 0.0512 | 0.2005 | 0.7419 | 1.0748 |

### 5 tightest per-concept minima

| concept | neighbours | saturated | min angle (rad) | x floor |
|---|---|---|---|---|
| archived | 62 | true | 0.002136 | 9.6x |
| promise | 63 | true | 0.007655 | 34.4x |
| sad | 44 | true | 0.008591 | 38.6x |
| afraid | 31 | true | 0.010448 | 46.9x |
| give | 60 | true | 0.012341 | 55.4x |

> Neighbour suite: encoder-package mutator, seed family x1c/<id>/<s>, deduped,
> saturation-sampled (identical AST suite to X1-corpus at D=8192, so margins
> are directly comparable across encoders). Synthetics: harness/x1.ts seed
> families x1/<i>, x1mut/<i>. Cross-platform floor leg: X0-q goldens.