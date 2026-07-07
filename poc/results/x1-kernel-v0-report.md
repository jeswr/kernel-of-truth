# X1 on kernel-v0 — adversarial single-edit margins + all authored pairs

date: 2026-07-07T03:37:39.508Z
corpus: kernel-v0 (authored; research-grade, NOT federation-endorsed) — 54 concepts
encoder content-hash: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c` (matches manifest pin: true)
corpus manifest sha256: `a9efbccdd9c7fe50f614d4687078584da603c5f07dce822cd323e0a5d7f4bdde`
corpus content-hash (concepts/*.json + manifest): `f23f5211ff1755975dd1ce8128ff810b316051c00ee2c1d56bae488f8f928751`

## Headline

- fp16 round-trip noise floor (max over all 54 authored vectors): **0.000213 rad** (worst: helpful)
- min adversarial single-edit angle over **2475** distinct neighbours: **0.002342 rad**
  (concept `archived`, edit referent-index: ref 3 at clauses.1.roles.quote.clauses.2.args.0.roles.complement.clause.roles.time.restrictedBy.args.1.roles.undergoer)
- ratio: **11.0x floor** -> **SUCCESS** (pre-registered: success >5x, failure <2x)

## Adversarial angle distribution (radians)

| suite | n | min | p1 | p5 | median | p95 | max |
|---|---|---|---|---|---|---|---|
| all | 2475 | 0.0023 | 0.0106 | 0.0188 | 0.1045 | 0.3187 | 1.0468 |
| operator-flip | 290 | 0.0041 | 0.0180 | 0.0514 | 0.2340 | 0.3585 | 0.4133 |
| clause-swap | 82 | 0.0793 | 0.0921 | 0.1277 | 0.6420 | 0.9264 | 1.0468 |
| referent-index | 357 | 0.0023 | 0.0081 | 0.0240 | 0.1228 | 0.2834 | 0.3181 |
| filler-substitution | 1746 | 0.0023 | 0.0106 | 0.0180 | 0.0891 | 0.2232 | 0.3562 |

### 10 tightest per-concept minima

| concept | neighbours | saturated | min angle (rad) | x floor |
|---|---|---|---|---|
| archived | 62 | true | 0.002342 | 11.0x |
| promise | 63 | true | 0.008085 | 38.0x |
| sad | 44 | true | 0.010619 | 50.0x |
| afraid | 31 | true | 0.012841 | 60.4x |
| kind | 122 | true | 0.013197 | 62.1x |
| give | 60 | true | 0.013848 | 65.1x |
| angry | 51 | true | 0.014079 | 66.2x |
| take | 36 | true | 0.015726 | 74.0x |
| bookmark | 82 | true | 0.018851 | 88.7x |
| find | 50 | true | 0.022151 | 104.2x |

## All authored-pair distances (54x53/2 = 1431 pairs)

- **minimum pair: `afraid` <-> `sad` at 0.115560 rad** (543.6x floor)
- pairwise distribution: min 0.1156, median 1.3084, max 1.5897 rad

| rank | pair | angle (rad) |
|---|---|---|
| 1 | afraid <-> sad | 0.115560 |
| 2 | happy <-> sad | 0.205097 |
| 3 | afraid <-> happy | 0.223819 |
| 4 | repair <-> take | 0.488447 |
| 5 | birth <-> death | 0.516249 |
| 6 | find <-> learn | 0.578033 |
| 7 | condolence <-> promise | 0.586838 |
| 8 | break <-> repair | 0.588521 |
| 9 | believe <-> forget | 0.603864 |
| 10 | find <-> lose | 0.641434 |

> Neighbour sets are enumerated with the encoder package's own seeded mutator
> (one valid single edit per seed), deduped by canonical JSON, sampled to
> saturation (no new mutant for max(500, 4x|found|) consecutive seeds).
> Exhaustiveness is therefore empirical, not proven; per-concept saturation
> flags above. Cross-platform leg of the floor is witnessed by X0 goldens.