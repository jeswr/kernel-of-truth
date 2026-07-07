# X3 on kernel-v0 — polarity pathology + weighting sensitivity

date: 2026-07-07T03:45:37.146Z
corpus: kernel-v0 (authored; research-grade, NOT federation-endorsed) — 54 concepts
encoder content-hash: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c` (matches manifest pin: true)
corpus manifest sha256: `a9efbccdd9c7fe50f614d4687078584da603c5f07dce822cd323e0a5d7f4bdde`
corpus content-hash (concepts/*.json + manifest): `f23f5211ff1755975dd1ce8128ff810b316051c00ee2c1d56bae488f8f928751`

### params: default

| edit class | n | min cos | median cos | max cos |
|---|---|---|---|---|
| NOT-wrap (inverting) | 54 | 0.7490 | 0.8752 | 0.9570 |
| polarity flip (inverting) | 25 | 0.9372 | 0.9974 | 0.9999 |
| alpha-rename (preserving) | 16 | 0.6006 | 0.7036 | 0.9806 |
| mods reorder (preserving) | - | - | - | - |

### params: alphaStruct=0.5 (RDM Spearman vs default: 0.9963)

| edit class | n | min cos | median cos | max cos |
|---|---|---|---|---|
| NOT-wrap (inverting) | 54 | 0.7509 | 0.8925 | 0.9880 |
| polarity flip (inverting) | 25 | 0.9232 | 0.9990 | 1.0000 |
| alpha-rename (preserving) | 16 | 0.6007 | 0.7147 | 0.9928 |
| mods reorder (preserving) | - | - | - | - |

### params: alphaStruct=2 (RDM Spearman vs default: 0.9919)

| edit class | n | min cos | median cos | max cos |
|---|---|---|---|---|
| NOT-wrap (inverting) | 54 | 0.7469 | 0.8584 | 0.9143 |
| polarity flip (inverting) | 25 | 0.9640 | 0.9933 | 0.9990 |
| alpha-rename (preserving) | 16 | 0.5979 | 0.6866 | 0.9672 |
| mods reorder (preserving) | - | - | - | - |

### params: notBoost=2 (RDM Spearman vs default: 0.9894)

| edit class | n | min cos | median cos | max cos |
|---|---|---|---|---|
| NOT-wrap (inverting) | 54 | 0.5654 | 0.7473 | 0.8691 |
| polarity flip (inverting) | 25 | 0.9372 | 0.9974 | 0.9999 |
| alpha-rename (preserving) | 16 | 0.6006 | 0.7167 | 0.9806 |
| mods reorder (preserving) | - | - | - | - |

### params: notBoost=4 (RDM Spearman vs default: 0.9391)

| edit class | n | min cos | median cos | max cos |
|---|---|---|---|---|
| NOT-wrap (inverting) | 54 | 0.3396 | 0.5259 | 0.8189 |
| polarity flip (inverting) | 25 | 0.9372 | 0.9974 | 0.9999 |
| alpha-rename (preserving) | 16 | 0.6006 | 0.7169 | 0.9806 |
| mods reorder (preserving) | - | - | - | - |

## Inverting edits vs the corpus's own near-pairs (default params)

- nearest distinct authored pair: `afraid` <-> `sad` at cos 0.9933
  - next: `happy` <-> `sad` cos 0.9790 (#2)
  - next: `afraid` <-> `happy` cos 0.9751 (#3)
  - next: `repair` <-> `take` cos 0.8831 (#4)
  - next: `birth` <-> `death` cos 0.8697 (#5)
- meaning-inverting single edits measured: 79; of these, **13 sit CLOSER to their original than the nearest distinct pair does**
- inverting-edit cosine: min 0.7490, median 0.8976, max 0.9999
- preserving-edit cosine: min 0.6006, median 0.7036, max 0.9806

| concept (inverting edit) | cos after edit |
|---|---|
| afraid | 0.9999 |
| liar | 0.9997 |
| promise | 0.9996 |
| wrong | 0.9994 |
| trustworthy | 0.9993 |
| right | 0.9992 |
| angry | 0.9992 |
| happy | 0.9992 |
| sad | 0.9990 |
| break | 0.9977 |
| celebration | 0.9977 |
| archived | 0.9974 |
| friend | 0.9974 |

> cosineAfterEdit close to 1 = edit barely moves the vector. The pathology on authored data: every meaning-INVERTING single edit whose cosine exceeds the nearest distinct authored pair (give<->take cluster) means kernel similarity ranks 'concept vs its own negation' as MORE similar than the two closest genuinely-different concepts. notBoost>1 must widen inverting shifts without degrading the rest of the geometry (rdmSpearmanVsDefault) to count as dominating.

> Consumers of kernel similarity remain BANNED (architecture.md §1.2, panel O9)
> until a polarity-aware variant dominates on these measurements.