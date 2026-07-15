# GLM-5.2 Wave-A expert atlas — Stage-2 summary

EXPLORATORY infra (rigor relaxed vs a frozen experiment). Routing-affinity evidence only (evidence_level 0): this maps what routes WHERE, not what an expert DOES. Functional/causal labels require Stage 3.

## Run

- trace rows aggregated: 2,800,800 (repeat items skipped: 2)
- items ended: 480  ·  active cells: 19,090 / 19,200 main
- topk_seen: [0, 1, 2, 3, 4, 5, 6, 7]  ·  layers active: 75

## Coverage gates (Stage-2 decision gate)

- trace invariants 100%: **True**
- routing mass on experts with >=100 events: **0.825** (gate >=0.95 -> FAIL)
- discovery-vs-held-out layer Spearman (median): **0.6328** (gate >=0.8 -> FAIL; frac layers>=0.8=0.0)
- stable-labelled cells: **4942** (>=100 events across >=20 families)

## Label-class census (all 19,200 main cells enumerated)

- stable: 4,942
- polysemantic: 3,532
- generalist: 329
- unresolved: 21
- rare: 10,266
- unseen: 110

## Top routing-specialised experts (stable; highest layer-normalised log2 enrichment)

| cell (site\|layer\|expert) | domain | enr log2 | repro | ci_lo | events | families |
|---|---|---|---|---|---|---|
| main|61|193 | science | 3.66 | 1.0 | 3.2843 | 173 | 20 |
| main|15|131 | multiling | 3.59 | 1.0 | 3.2328 | 107 | 24 |
| main|19|15 | legal_fin | 3.57 | 1.0 | 3.2543 | 159 | 26 |
| main|72|206 | legal_fin | 3.55 | 1.0 | 3.2634 | 132 | 26 |
| main|59|9 | science | 3.55 | 1.0 | 3.2049 | 219 | 39 |
| main|51|121 | legal_fin | 3.53 | 1.0 | 3.1913 | 136 | 22 |
| main|19|1 | legal_fin | 3.52 | 1.0 | 3.1662 | 103 | 21 |
| main|57|190 | multiling | 3.50 | 0.995 | 3.0818 | 131 | 35 |
| main|20|229 | legal_fin | 3.49 | 1.0 | 3.1563 | 146 | 24 |
| main|56|19 | multiling | 3.47 | 1.0 | 3.1135 | 130 | 27 |
| main|20|224 | science | 3.46 | 1.0 | 3.1544 | 241 | 39 |
| main|50|215 | legal_fin | 3.44 | 1.0 | 3.0994 | 124 | 22 |
| main|50|11 | legal_fin | 3.44 | 1.0 | 3.135 | 198 | 39 |
| main|21|97 | science | 3.43 | 1.0 | 3.1399 | 188 | 42 |
| main|16|243 | legal_fin | 3.43 | 1.0 | 3.1023 | 229 | 39 |
| main|59|246 | science | 3.43 | 1.0 | 3.1504 | 154 | 34 |
| main|17|191 | legal_fin | 3.42 | 1.0 | 3.0976 | 146 | 24 |
| main|31|244 | legal_fin | 3.41 | 1.0 | 3.0992 | 186 | 42 |
| main|71|187 | legal_fin | 3.41 | 1.0 | 3.1293 | 220 | 42 |
| main|47|45 | multiling | 3.40 | 1.0 | 3.0757 | 113 | 47 |

## Deterministic-replacement leads (Stage-4 candidates, routing-shaped)

### format: 15 candidate cell(s)
- main|56|45 — dom=structured op=complete fmt=xml · enr(dom/op/fmt)=2.60/0.99/5.24 · n=111 · stable
- main|63|217 — dom=structured op=complete fmt=xml · enr(dom/op/fmt)=2.47/0.68/5.13 · n=108 · stable
- main|17|233 — dom=structured op=complete fmt=xml · enr(dom/op/fmt)=2.77/0.96/5.12 · n=118 · stable
- main|69|149 — dom=structured op=complete fmt=csv · enr(dom/op/fmt)=2.40/0.70/4.94 · n=130 · stable
- main|60|243 — dom=structured op=complete fmt=xml · enr(dom/op/fmt)=2.62/0.83/4.88 · n=140 · stable
- main|66|59 — dom=legal_fin op=classify fmt=table · enr(dom/op/fmt)=3.22/1.33/4.85 · n=101 · stable
- main|70|200 — dom=legal_fin op=transform fmt=table · enr(dom/op/fmt)=2.84/0.55/4.85 · n=126 · stable
- main|62|137 — dom=structured op=complete fmt=xml · enr(dom/op/fmt)=2.55/0.74/4.84 · n=150 · stable

### copy: 15 candidate cell(s)
- main|20|211 — dom=multiling op=copy fmt=chinese · enr(dom/op/fmt)=2.22/1.25/3.81 · n=110 · stable
- main|55|110 — dom=multiling op=copy fmt=chinese · enr(dom/op/fmt)=2.31/1.30/3.47 · n=129 · stable
- main|42|119 — dom=multiling op=copy fmt=chinese · enr(dom/op/fmt)=2.04/0.92/3.42 · n=121 · polysemantic
- main|74|246 — dom=multiling op=copy fmt=chinese · enr(dom/op/fmt)=1.77/0.88/3.39 · n=255 · stable
- main|58|19 — dom=multiling op=copy fmt=chinese · enr(dom/op/fmt)=2.50/1.66/3.28 · n=154 · stable
- main|66|120 — dom=copy op=copy fmt=chinese · enr(dom/op/fmt)=2.26/2.29/3.05 · n=134 · stable
- main|43|152 — dom=copy op=translate fmt=whitespace · enr(dom/op/fmt)=2.32/3.02/1.46 · n=142 · polysemantic
- main|6|234 — dom=multiling op=copy fmt=chinese · enr(dom/op/fmt)=1.38/1.12/2.96 · n=152 · polysemantic

### arithmetic: 15 candidate cell(s)
- main|36|239 — dom=math op=arithmetic fmt=table · enr(dom/op/fmt)=2.99/3.41/0.67 · n=183 · stable
- main|44|227 — dom=math op=arithmetic fmt=plain · enr(dom/op/fmt)=2.78/3.40/0.44 · n=100 · stable
- main|39|187 — dom=legal_fin op=arithmetic fmt=table · enr(dom/op/fmt)=3.23/2.81/2.00 · n=160 · stable
- main|18|224 — dom=math op=arithmetic fmt=csv · enr(dom/op/fmt)=3.01/3.22/1.23 · n=153 · stable
- main|45|245 — dom=math op=arithmetic fmt=whitespace · enr(dom/op/fmt)=3.21/3.16/0.49 · n=136 · stable
- main|31|37 — dom=math op=arithmetic fmt=code · enr(dom/op/fmt)=3.20/2.71/0.29 · n=138 · stable
- main|6|123 — dom=multiling op=arithmetic fmt=chinese · enr(dom/op/fmt)=1.59/0.77/3.13 · n=119 · stable
- main|42|66 — dom=math op=arithmetic fmt=table · enr(dom/op/fmt)=2.82/3.13/2.54 · n=232 · stable

### semantic_lookup: 15 candidate cell(s)
- main|61|193 — dom=science op=lookup fmt=plain · enr(dom/op/fmt)=3.66/1.96/0.47 · n=173 · stable
- main|59|9 — dom=science op=lookup fmt=plain · enr(dom/op/fmt)=3.55/1.84/0.45 · n=219 · stable
- main|76|155 — dom=multiling op=lookup fmt=chinese · enr(dom/op/fmt)=1.84/1.00/3.51 · n=114 · stable
- main|20|224 — dom=science op=lookup fmt=table · enr(dom/op/fmt)=3.46/1.70/0.77 · n=241 · stable
- main|21|97 — dom=science op=lookup fmt=plain · enr(dom/op/fmt)=3.43/1.51/0.43 · n=188 · stable
- main|59|246 — dom=science op=lookup fmt=plain · enr(dom/op/fmt)=3.43/1.69/0.37 · n=154 · stable
- main|64|7 — dom=multiling op=lookup fmt=chinese · enr(dom/op/fmt)=2.07/0.92/3.39 · n=118 · stable
- main|26|150 — dom=science op=lookup fmt=table · enr(dom/op/fmt)=3.38/1.81/1.12 · n=133 · stable

## Honesty note

Cells below the coverage bar are marked rare/unresolved/unseen, NOT given a speciality. A routing-affinity label is evidence about the GATE, capped at evidence_level 0; it is not a functional claim and does not by itself justify replacement. Stage 3 (activation-max contrasts, local functional signatures, causal ablation) is required before any expert is called replaceable.
