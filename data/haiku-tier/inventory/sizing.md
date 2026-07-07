# haiku-tier inventory — sizing (stage 0)

Generated deterministically by `build-inventory.py` from the pinned sources in
`pins.json` (sha256-verified at run time). 56628 ranked items;
13432 exclusions (audit trail: `inventory-excluded.jsonl`).
Full-depth inventory per maintainer direction 2026-07-07 (subscription
capacity is the budget; the session-governed runner processes in rank order,
so depth costs nothing — priority does the work).

| band | source | items | cumulative |
|---|---|---|---|
| A | M0b measured gaps (post-molecules-v0 top-500) | 335 | 335 |
| B | WordNet core (~5k senses -> single-word, non-proper lemmas) | 3266 | 3601 |
| C | OpenSubtitles-2018 frequency list (full 50k) content lemmas | 14389 | 17990 |
| D | remaining WordNet 3.1 single-word lemmas (SemCor-tag-mass ranked) | 38638 | 56628 |

Landmark: the historical ~$70-API-equivalent / ~9000-concept cut would
land in band C (rank 9000 = `plump`).
At a governed 500 calls per 5h window, one window ≈ ranks N..N+500; band A+B
(~3601) ≈ 8 windows; the full inventory ≈
114 windows.

## Exclusions by band and reason

| band | covered | prime | function | entity | sector | total |
|---|---|---|---|---|---|---|
| A | 1 | 3 | 0 | 0 | 1 | 5 |
| B | 102 | 28 | 10 | 1 | 21 | 162 |
| C | 23 | 4 | 0 | 2841 | 81 | 2949 |
| D | 0 | 19 | 74 | 9887 | 336 | 10316 |

Core-list preprocessing: 4997 entries -> 21 multiword
dropped (v0 targets single-token lemmas; multiword lexemes are a filed
follow-up), 8 capitalised (proper-noun) dropped,
3710 distinct lemmas considered.

Sector-routed lemmas (flagged to physics-v0/math-v0, not Haiku-authored):
['abamp', 'abampere', 'abcoulomb', 'abfarad', 'abhenry', 'abohm', 'abvolt', 'abwatt', 'acceleration', 'action', 'addition', 'ampere', 'angstrom', 'anna', 'arcdegree', 'archine', 'arcminute', 'arcsecond', 'ardeb', 'area', 'arpent', 'arroba', 'avo', 'baht', 'baisa', 'baiza', 'barye', 'bbl', 'boliviano', 'btu', 'butat', 'butut', 'byte', 'calorie', 'candela', 'carat', 'cattie', 'cedi', 'cental', 'centare', 'centas', 'centavo', 'centesimo', 'centiliter', 'centilitre', 'centimeter', 'centimetre', 'centimo', 'centner', 'chaldron', 'chetrum', 'chon', 'congius', 'conto', 'copeck', 'coulomb', 'cran', 'crith', 'cubit', 'cwt', 'dal', 'dalasi', 'daraf', 'decagram', 'decaliter', 'decalitre', 'decameter', 'decametre', 'decibel', 'decigram', 'deciliter', 'decilitre', 'decimeter', 'decimetre', 'dekagram', 'dekaliter', 'dekalitre', 'dekameter', 'dekametre', 'dessiatine', 'deutschmark', 'dg', 'dinar', 'diopter', 'dioptre', 'dirham', 'dkg', 'dkl', 'dkm', 'dl', 'dobra', 'doppelzentner', 'drachm', 'drachma', 'dram', 'dyne', 'eb', 'ebit', 'eib', 'eibit', 'em', 'en', 'energy', 'entropy', 'epha', 'ephah', 'equality', 'erg', 'erlang', 'escudo', 'euro', 'eurodollar', 'ev', 'exabit', 'exabyte', 'exbibit', 'exbibyte', 'eyrir', 'farad', 'femtometer', 'femtometre', 'femtovolt', 'fils', 'fingerbreadth', 'fistmele', 'florin', 'fluidounce', 'fluidram', 'footcandle', 'force', 'forint', 'franc', 'frequency', 'ft', 'fthm', 'furlong', 'gallon', 'gbit', 'gibibit', 'gibibyte', 'gibit', 'gigabit', 'gigabyte', 'gm', 'gourde', 'gramme', 'groschen', 'grosz', 'gulden', 'gy', 'handbreadth', 'handsbreadth', 'hao', 'hectare', 'hectogram', 'hectoliter', 'hectolitre', 'hectometer', 'hectometre', 'hertz', 'hin', 'hl', 'hm', 'horsepower', 'hp', 'hryvnia', 'hundredweight', 'integer', 'intersection', 'inti', 'jiao', 'joule', 'kapeika', 'karat', 'kb', 'kbit', 'kelvin', 'kg', 'khoum', 'kib', 'kibibit', 'kibibyte', 'kibit', 'kilderkin', 'kilo', 'kilobit', 'kilobyte', 'kilocalorie', 'kilogram', 'kiloliter', 'kilolitre', 'kilometer', 'kilometre', 'kiloton', 'kilovolt', 'kilowatt', 'kina', 'klick', 'km', 'kobo', 'kopeck', 'kopek', 'kopiyka', 'kor', 'koruna', 'krona', 'krone', 'kroon', 'kt', 'kv', 'kw', 'kwacha', 'kwai', 'kyat', 'lb', 'lek', 'lempira', 'length', 'leone', 'leu', 'lev', 'ligne', 'likuta', 'lilangeni', 'lira', 'litas', 'litre', 'lm', 'loonie', 'loti', 'lumen', 'lumma', 'lux', 'lwei', 'magneton', 'manat', 'markka', 'mass', 'maund', 'mbit', 'mcg', 'mebibit', 'mebibyte', 'megabit', 'megabyte', 'megaflop', 'megaton', 'megawatt', 'megohm', 'metical', 'metre', 'mflop', 'mho', 'mib', 'mibit', 'microbar', 'microfarad', 'microgauss', 'microgram', 'micromicron', 'micromillimeter', 'micromillimetre', 'micron', 'microradian', 'microvolt', 'mil', 'milliampere', 'millibar', 'millicurie', 'millidegree', 'millifarad', 'milligram', 'millihenry', 'milliliter', 'millilitre', 'millime', 'millimeter', 'millimetre', 'millimicron', 'milline', 'milliradian', 'millirem', 'millivolt', 'milliwatt', 'mips', 'ml', 'mm', 'mol', 'mole', 'momentum', 'mongo', 'morgen', 'mrem', 'multiplication', 'mutchkin', 'myg', 'mym', 'myriagram', 'myriameter', 'myriametre', 'naira', 'nanogram', 'nanometer', 'nanometre', 'nanovolt', 'newton', 'ng', 'ngultrum', 'ngwee', 'nybble', 'obolus', 'odd', 'ohm', 'ouguiya', 'oxtant', 'paisa', 'parsec', 'pascal', 'pataca', 'pbit', 'pdl', 'pebibit', 'pebibyte', 'penni', 'pennyweight', 'peseta', 'pesewa', 'peso', 'petabit', 'petabyte', 'pfennig', 'phon', 'phot', 'piaster', 'piastre', 'pib', 'pibit', 'picofarad', 'picometer', 'picometre', 'picovolt', 'picul', 'pint', 'pood', 'poundal', 'power', 'predecessor', 'pressure', 'pul', 'pula', 'pya', 'qepiq', 'qindarka', 'qintar', 'quart', 'quintal', 'qurush', 'rad', 'radian', 'rankine', 'rial', 'riel', 'ringgit', 'riyal', 'rotl', 'rouble', 'rubel', 'ruble', 'rupee', 'rupiah', 'santims', 'satang', 'schilling', 'second', 'secpar', 'sen', 'sene', 'seniti', 'sente', 'shekel', 'som', 'sone', 'steradian', 'sthene', 'stotinka', 'stp', 'subset', 'subunit', 'successor', 'tael', 'taka', 'tala', 'tambala', 'tbit', 'tebibit', 'tebibyte', 'tenge', 'terabit', 'terabyte', 'teraflop', 'tetri', 'thebe', 'therm', 'three', 'tib', 'tibit', 'tical', 'tiyin', 'toea', 'ton', 'tonne', 'torr', 'tughrik', 'tugrik', 'tyiyn', 'union', 'var', 'vara', 'verst', 'volt', 'volume', 'watt', 'ybit', 'yib', 'yibit', 'yobibit', 'yobibyte', 'yottabit', 'yottabyte', 'zb', 'zbit', 'zebibit', 'zebibyte', 'zero', 'zettabit', 'zettabyte', 'zib', 'zibit', 'zloty']

Entity rule and every other exclusion rule: see the module docstring of
`build-inventory.py` (the documented, mechanical rules).
