# haiku-tier inventory — sizing (stage 0)

Generated deterministically by `build-inventory.py` from the pinned sources in
`pins.json` (sha256-verified at run time). 9166 ranked items;
1356 exclusions (audit trail: `inventory-excluded.jsonl`).

| band | source | items | cumulative |
|---|---|---|---|
| A | M0b measured gaps (post-molecules-v0 top-500) | 335 | 335 |
| B | WordNet core (~5k senses -> single-word, non-proper lemmas) | 3266 | 3601 |
| C | OpenSubtitles-2018 frequency top-10000 content lemmas | 5565 | 9166 |

**The ~9000 cut lands in band C** — every measured-gap and
core-WordNet concept is inside the budget; the cut point trims only the
frequency tail. At the cut: rank 9000 = lemma
`plump` (freq rank 18750).

## Exclusions by band and reason

| band | covered | prime | function | entity | sector | total |
|---|---|---|---|---|---|---|
| A | 1 | 3 | 0 | 0 | 1 | 5 |
| B | 102 | 28 | 10 | 1 | 21 | 162 |
| C | 21 | 4 | 0 | 1135 | 29 | 1189 |

Core-list preprocessing: 4997 entries -> 21 multiword
dropped (v0 targets single-token lemmas; multiword lexemes are a filed
follow-up), 8 capitalised (proper-noun) dropped,
3710 distinct lemmas considered.

Sector-routed lemmas (flagged to physics-v0/math-v0, not Haiku-authored):
['acceleration', 'action', 'addition', 'anna', 'area', 'baht', 'calorie', 'em', 'en', 'energy', 'equality', 'euro', 'ev', 'force', 'frequency', 'gallon', 'hm', 'horsepower', 'intersection', 'kelvin', 'kg', 'kilo', 'km', 'length', 'lira', 'lm', 'lux', 'mass', 'metre', 'mil', 'millimeter', 'mm', 'mole', 'momentum', 'newton', 'ng', 'odd', 'pascal', 'pint', 'power', 'predecessor', 'pressure', 'rad', 'second', 'sen', 'successor', 'three', 'ton', 'union', 'volume', 'zero']

Entity rule and every other exclusion rule: see the module docstring of
`build-inventory.py` (the documented, mechanical rules).
