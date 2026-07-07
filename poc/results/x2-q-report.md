# X2-q — decode reality check at toy-native D (kot-enc-Bq/1; UNGATED)

date: 2026-07-07T04:54:37.709Z
corpus: kernel-v0 — 54 concepts, content-hash `f23f5211ff1755975dd1ce8128ff810b316051c00ee2c1d56bae488f8f928751`

**No gate.** The capacity arithmetic (DCV §7.2) places robust full decode at
D ≈ 4k-20k for the capped structure budget; at D = 512-576 the quasi-orthogonal
crosstalk floor (~1/sqrt(D) per sibling term, QCERT report) makes deep exact
recovery impossible by design. The numbers below quantify what survives.
Reference row: D=8192 exact codebook achieves 54/54 + 54/54 (X2-corpus).

## D = 512

encoder content-hash: `3492799ed73b49a612bebca920421041edd31d7bd4098bcf55da52df127ab9ee`

- minimal lexicon: **1/54 exact** (4 validated)
- full-corpus lexicon: **1/54 exact** (4 validated)

Exact-recovery rate by authored max depth (minimal | full-corpus):

| depth | minimal exact/total |
|---|---|
| 2 | 0/2 |
| 3 | 0/19 |
| 4 | 0/19 |
| 5 | 1/11 |
| 6 | 0/2 |
| 7 | 0/1 |

| depth | full-corpus exact/total |
|---|---|
| 2 | 0/2 |
| 3 | 0/19 |
| 4 | 0/19 |
| 5 | 1/11 |
| 6 | 0/2 |
| 7 | 0/1 |

<details><summary>Non-exact under minimal lexicon (53)</summary>

- `afraid` (depth 5, 8 clauses): decode failed: ERR_REF_NOT_INTRODUCED at $.clauses[0].args[0].roles.quote.clauses[1].roles.complement: ref 2 used before its introducing occurrence (or out of quote scope)
- `alive` (depth 3, 5 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `angry` (depth 5, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `archived` (depth 7, 14 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `begin` (depth 3, 6 clauses): ok-but-wrong: decoded AST validates but differs from authored AST
- `believe` (depth 3, 5 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `birth` (depth 4, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `bookmark` (depth 5, 11 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `break` (depth 5, 13 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `broken` (depth 5, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `cause` (depth 3, 9 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `celebration` (depth 3, 10 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `change` (depth 5, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `condolence` (depth 3, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `conversation` (depth 3, 8 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `dead` (depth 4, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `death` (depth 3, 8 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `end` (depth 4, 8 clauses): ok-but-wrong: decoded AST validates but differs from authored AST
- `event` (depth 4, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `find` (depth 5, 9 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `forget` (depth 3, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `friend` (depth 4, 9 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `gift` (depth 4, 8 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `give` (depth 5, 14 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `grieving` (depth 3, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `happy` (depth 4, 6 clauses): decode failed: ERR_REF_NEVER_INTRODUCED at $.referents: referent 2 declared but never introduced
- `has-part` (depth 2, 2 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `help` (depth 3, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `helpful` (depth 3, 5 clauses): ok-but-wrong: decoded AST validates but differs from authored AST
- `inside` (depth 2, 4 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `kind` (depth 6, 16 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `learn` (depth 3, 8 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `lie` (depth 4, 10 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `lose` (depth 4, 9 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `lost` (depth 4, 5 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `make` (depth 3, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `maker-of` (depth 3, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `memory` (depth 4, 10 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `near` (depth 3, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `part-of` (depth 4, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `promise` (depth 5, 10 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `remember` (depth 3, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `reminder` (depth 4, 14 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `repair` (depth 4, 9 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `right` (depth 4, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `sad` (depth 6, 8 clauses): decode failed: ERR_REF_NEVER_INTRODUCED at $.referents: referent 2 declared but never introduced
- `take` (depth 5, 10 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `teacher` (depth 4, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `thief` (depth 3, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `trustworthy` (depth 4, 8 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `useful` (depth 4, 9 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `visible` (depth 3, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `wrong` (depth 4, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode

</details>

## D = 576

encoder content-hash: `6ad0b2bc01c06447aae8468f500e2a2178e9a40f0d95de048b0418afcaea77db`

- minimal lexicon: **8/54 exact** (12 validated)
- full-corpus lexicon: **8/54 exact** (12 validated)

Exact-recovery rate by authored max depth (minimal | full-corpus):

| depth | minimal exact/total |
|---|---|
| 2 | 1/2 |
| 3 | 3/19 |
| 4 | 2/19 |
| 5 | 1/11 |
| 6 | 1/2 |
| 7 | 0/1 |

| depth | full-corpus exact/total |
|---|---|
| 2 | 1/2 |
| 3 | 3/19 |
| 4 | 2/19 |
| 5 | 1/11 |
| 6 | 1/2 |
| 7 | 0/1 |

<details><summary>Non-exact under minimal lexicon (46)</summary>

- `afraid` (depth 5, 8 clauses): decode failed: ERR_REF_NOT_INTRODUCED at $.clauses[0].args[0].roles.quote.clauses[1].roles.complement: ref 2 used before its introducing occurrence (or out of quote scope)
- `angry` (depth 5, 7 clauses): decode failed: ERR_REF_NEVER_INTRODUCED at $.referents: referent 2 declared but never introduced
- `archived` (depth 7, 14 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `begin` (depth 3, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `believe` (depth 3, 5 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `birth` (depth 4, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `bookmark` (depth 5, 11 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `break` (depth 5, 13 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `broken` (depth 5, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `cause` (depth 3, 9 clauses): decode failed: ERR_REF_NEVER_INTRODUCED at $.referents: referent 3 declared but never introduced
- `celebration` (depth 3, 10 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `change` (depth 5, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `condolence` (depth 3, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `conversation` (depth 3, 8 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `death` (depth 3, 8 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `end` (depth 4, 8 clauses): ok-but-wrong: decoded AST validates but differs from authored AST
- `event` (depth 4, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `find` (depth 5, 9 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `forget` (depth 3, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `friend` (depth 4, 9 clauses): ok-but-wrong: decoded AST validates but differs from authored AST
- `gift` (depth 4, 8 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `give` (depth 5, 14 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `grieving` (depth 3, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `happy` (depth 4, 6 clauses): decode failed: ERR_REF_NOT_INTRODUCED at $.clauses[0].args[0].roles.quote.clauses[1].roles.complement: ref 2 used before its introducing occurrence (or out of quote scope)
- `help` (depth 3, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `inside` (depth 2, 4 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `kind` (depth 6, 16 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `learn` (depth 3, 8 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `lie` (depth 4, 10 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `lose` (depth 4, 9 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `lost` (depth 4, 5 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `make` (depth 3, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `maker-of` (depth 3, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `memory` (depth 4, 10 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `near` (depth 3, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `part-of` (depth 4, 6 clauses): ok-but-wrong: decoded AST validates but differs from authored AST
- `promise` (depth 5, 10 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `remember` (depth 3, 6 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `reminder` (depth 4, 14 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `repair` (depth 4, 9 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `take` (depth 5, 10 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `teacher` (depth 4, 7 clauses): ok-but-wrong: decoded AST validates but differs from authored AST
- `trustworthy` (depth 4, 8 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `useful` (depth 4, 9 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `visible` (depth 3, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode
- `wrong` (depth 4, 7 clauses): decode failed: ERR_DECODE_INCOMPLETE: one or more clause positions failed to decode

</details>

> Protocol identical to X2-corpus: exact = canonical-JSON equality; minimal
> lexicon = referenced ids only; full-corpus = all 53 others as cleanup
> candidates. Decoder thresholds are heuristics, not part of the encoder pin.