# X3 — polarity pathology + weighting sensitivity (documentation)

date: 2026-07-07T01:58:25.672Z
encoder content-hash: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c` (weighting params pinned therein)
corpus: 200 synthetics

### params: default

| edit class | n | min cos | median cos | max cos |
|---|---|---|---|---|
| NOT-wrap (inverting) | 200 | 0.7450 | 0.8757 | 0.9753 |
| polarity flip (inverting) | 157 | 0.9363 | 0.9875 | 0.9994 |
| alpha-rename (preserving) | 54 | 0.6802 | 0.8027 | 0.9901 |
| mods reorder (preserving) | - | - | - | - |

### params: alphaStruct=0.5 (RDM Spearman vs default: 0.9944)

| edit class | n | min cos | median cos | max cos |
|---|---|---|---|---|
| NOT-wrap (inverting) | 200 | 0.7461 | 0.8757 | 0.9931 |
| polarity flip (inverting) | 157 | 0.9217 | 0.9954 | 1.0000 |
| alpha-rename (preserving) | 54 | 0.6947 | 0.8141 | 0.9971 |
| mods reorder (preserving) | - | - | - | - |

### params: alphaStruct=2 (RDM Spearman vs default: 0.9866)

| edit class | n | min cos | median cos | max cos |
|---|---|---|---|---|
| NOT-wrap (inverting) | 200 | 0.7434 | 0.8609 | 0.9480 |
| polarity flip (inverting) | 157 | 0.9384 | 0.9854 | 0.9988 |
| alpha-rename (preserving) | 54 | 0.6530 | 0.7817 | 0.9795 |
| mods reorder (preserving) | - | - | - | - |

### params: notBoost=2 (RDM Spearman vs default: 0.9798)

| edit class | n | min cos | median cos | max cos |
|---|---|---|---|---|
| NOT-wrap (inverting) | 200 | 0.5547 | 0.7597 | 0.8930 |
| polarity flip (inverting) | 157 | 0.9363 | 0.9864 | 0.9994 |
| alpha-rename (preserving) | 54 | 0.6802 | 0.8082 | 0.9918 |
| mods reorder (preserving) | - | - | - | - |

### params: notBoost=4 (RDM Spearman vs default: 0.8882)

| edit class | n | min cos | median cos | max cos |
|---|---|---|---|---|
| NOT-wrap (inverting) | 200 | 0.3241 | 0.5399 | 0.8265 |
| polarity flip (inverting) | 157 | 0.9285 | 0.9895 | 0.9996 |
| alpha-rename (preserving) | 54 | 0.6802 | 0.8149 | 0.9952 |
| mods reorder (preserving) | - | - | - | - |

> cosineAfterEdit close to 1 = edit barely moves the vector. The pathology is documented if meaning-INVERTING edits (notWrap/polarityFlip) sit near meaning-PRESERVING ones (alphaRename). A polarity-aware variant (notBoost>1) must push inverting edits further from 1 WITHOUT degrading the rest of the geometry (rdmSpearmanVsDefault) to count as dominating.

> Consumers of kernel similarity remain BANNED (architecture.md §1.2, panel O9)
> until a polarity-aware variant dominates on these measurements.