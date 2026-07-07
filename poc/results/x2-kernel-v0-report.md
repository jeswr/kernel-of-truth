# X2 on kernel-v0 — exact decode (minimal vs full-corpus cleanup lexicon)

date: 2026-07-07T04:22:36.874Z
corpus: kernel-v0 (authored; research-grade, NOT federation-endorsed) — 54 concepts
encoder content-hash: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c` (matches manifest pin: true)
corpus manifest sha256: `a9efbccdd9c7fe50f614d4687078584da603c5f07dce822cd323e0a5d7f4bdde`
corpus content-hash (concepts/*.json + manifest): `f23f5211ff1755975dd1ce8128ff810b316051c00ee2c1d56bae488f8f928751`

**Criterion (minimal lexicon): 54/54 exact -> PASS** (54/54 exact; reference-bearing 18/18; min confidence 0.000 at `angry`)

Full-corpus lexicon (all 53 others as cleanup candidates): 54/54 exact (reference-bearing 18/18; min confidence 0.000). The gap between the two conditions measures
cleanup-lexicon interference: extra corpus vectors acting as false attractors during
the decoder's atomic-vs-concept competitions. Exact = canonical-JSON equality.

## Minimal lexicon (pre-registered setting)

| concept | frame | clauses | depth | crefs | exact | min-conf | ms |
|---|---|---|---|---|---|---|---|
| afraid | WhenTrue | 8 | 5 | 0 | yes | 0.549 | 2449 |
| alive | WhenTrue | 5 | 3 | 0 | yes | 0.976 | 1152 |
| angry | WhenTrue | 7 | 5 | 0 | yes | 0.000 | 4093 |
| archived | WhenTrue | 14 | 7 | 0 | yes | 0.000 | 5054 |
| begin | RelationalSchema | 6 | 3 | 0 | yes | 0.969 | 423 |
| believe | RelationalSchema | 5 | 3 | 0 | yes | 0.974 | 892 |
| birth | InstanceSchema | 7 | 4 | 1 | yes | 0.967 | 1008 |
| bookmark | InstanceSchema | 11 | 5 | 0 | yes | 0.900 | 2867 |
| break | RelationalSchema | 13 | 5 | 0 | yes | 0.946 | 1940 |
| broken | WhenTrue | 7 | 5 | 1 | yes | 0.951 | 1174 |
| cause | RelationalSchema | 9 | 3 | 0 | yes | 0.894 | 1113 |
| celebration | InstanceSchema | 10 | 3 | 2 | yes | 0.867 | 1912 |
| change | InstanceSchema | 6 | 5 | 0 | yes | 0.955 | 1052 |
| condolence | InstanceSchema | 7 | 3 | 1 | yes | 0.871 | 1412 |
| conversation | InstanceSchema | 8 | 3 | 1 | yes | 0.918 | 1740 |
| dead | WhenTrue | 6 | 4 | 0 | yes | 0.977 | 848 |
| death | InstanceSchema | 8 | 3 | 1 | yes | 0.949 | 1199 |
| end | RelationalSchema | 8 | 4 | 0 | yes | 0.969 | 1016 |
| event | InstanceSchema | 7 | 4 | 0 | yes | 0.969 | 978 |
| find | RelationalSchema | 9 | 5 | 0 | yes | 0.893 | 2015 |
| forget | RelationalSchema | 6 | 3 | 0 | yes | 0.975 | 625 |
| friend | RelationalSchema | 9 | 4 | 0 | yes | 0.898 | 3393 |
| gift | InstanceSchema | 8 | 4 | 1 | yes | 0.949 | 2172 |
| give | RelationalSchema | 14 | 5 | 0 | yes | 0.951 | 2651 |
| grieving | WhenTrue | 6 | 3 | 2 | yes | 0.955 | 981 |
| happy | WhenTrue | 6 | 4 | 0 | yes | 0.164 | 2300 |
| has-part | RelationalSchema | 2 | 2 | 0 | yes | 0.969 | 1097 |
| help | RelationalSchema | 6 | 3 | 0 | yes | 0.930 | 1325 |
| helpful | WhenTrue | 5 | 3 | 1 | yes | 0.929 | 1132 |
| inside | RelationalSchema | 4 | 2 | 0 | yes | 0.961 | 559 |
| kind | InstanceSchema | 16 | 6 | 0 | yes | 0.953 | 4210 |
| learn | RelationalSchema | 8 | 3 | 0 | yes | 0.833 | 1277 |
| liar | InstanceSchema | 6 | 5 | 1 | yes | 0.894 | 1302 |
| lie | InstanceSchema | 10 | 4 | 0 | yes | 0.782 | 1983 |
| lose | RelationalSchema | 9 | 4 | 0 | yes | 0.971 | 2340 |
| lost | WhenTrue | 5 | 4 | 1 | yes | 0.949 | 1017 |
| make | RelationalSchema | 6 | 3 | 0 | yes | 0.890 | 861 |
| maker-of | RelationalSchema | 7 | 3 | 1 | yes | 0.944 | 1826 |
| memory | InstanceSchema | 10 | 4 | 1 | yes | 0.950 | 1701 |
| near | RelationalSchema | 7 | 3 | 0 | yes | 0.908 | 1266 |
| part-of | RelationalSchema | 6 | 4 | 0 | yes | 0.894 | 849 |
| promise | InstanceSchema | 10 | 5 | 0 | yes | 0.944 | 2706 |
| remember | RelationalSchema | 6 | 3 | 0 | yes | 0.901 | 761 |
| reminder | InstanceSchema | 14 | 4 | 2 | yes | 0.241 | 2500 |
| repair | RelationalSchema | 9 | 4 | 1 | yes | 0.967 | 1437 |
| right | WhenTrue | 7 | 4 | 0 | yes | 0.940 | 2564 |
| sad | WhenTrue | 8 | 6 | 0 | yes | 0.000 | 2328 |
| take | RelationalSchema | 10 | 5 | 0 | yes | 0.962 | 1869 |
| teacher | InstanceSchema | 7 | 4 | 1 | yes | 0.819 | 2012 |
| thief | InstanceSchema | 7 | 3 | 1 | yes | 0.916 | 1885 |
| trustworthy | WhenTrue | 8 | 4 | 2 | yes | 0.210 | 1665 |
| useful | WhenTrue | 9 | 4 | 0 | yes | 0.771 | 1517 |
| visible | WhenTrue | 7 | 3 | 0 | yes | 0.884 | 1029 |
| wrong | WhenTrue | 7 | 4 | 0 | yes | 0.928 | 2694 |

## Full-corpus lexicon (interference measurement)

| concept | frame | clauses | depth | crefs | exact | min-conf | ms |
|---|---|---|---|---|---|---|---|
| afraid | WhenTrue | 8 | 5 | 0 | yes | 0.549 | 2331 |
| alive | WhenTrue | 5 | 3 | 0 | yes | 0.976 | 639 |
| angry | WhenTrue | 7 | 5 | 0 | yes | 0.000 | 4127 |
| archived | WhenTrue | 14 | 7 | 0 | yes | 0.000 | 5628 |
| begin | RelationalSchema | 6 | 3 | 0 | yes | 0.969 | 625 |
| believe | RelationalSchema | 5 | 3 | 0 | yes | 0.974 | 837 |
| birth | InstanceSchema | 7 | 4 | 1 | yes | 0.331 | 1994 |
| bookmark | InstanceSchema | 11 | 5 | 0 | yes | 0.900 | 2293 |
| break | RelationalSchema | 13 | 5 | 0 | yes | 0.946 | 2418 |
| broken | WhenTrue | 7 | 5 | 1 | yes | 0.169 | 1164 |
| cause | RelationalSchema | 9 | 3 | 0 | yes | 0.894 | 1194 |
| celebration | InstanceSchema | 10 | 3 | 2 | yes | 0.021 | 2059 |
| change | InstanceSchema | 6 | 5 | 0 | yes | 0.955 | 1439 |
| condolence | InstanceSchema | 7 | 3 | 1 | yes | 0.318 | 1527 |
| conversation | InstanceSchema | 8 | 3 | 1 | yes | 0.331 | 2064 |
| dead | WhenTrue | 6 | 4 | 0 | yes | 0.977 | 757 |
| death | InstanceSchema | 8 | 3 | 1 | yes | 0.330 | 1315 |
| end | RelationalSchema | 8 | 4 | 0 | yes | 0.969 | 1009 |
| event | InstanceSchema | 7 | 4 | 0 | yes | 0.969 | 1385 |
| find | RelationalSchema | 9 | 5 | 0 | yes | 0.893 | 2359 |
| forget | RelationalSchema | 6 | 3 | 0 | yes | 0.975 | 598 |
| friend | RelationalSchema | 9 | 4 | 0 | yes | 0.898 | 3601 |
| gift | InstanceSchema | 8 | 4 | 1 | yes | 0.334 | 2257 |
| give | RelationalSchema | 14 | 5 | 0 | yes | 0.951 | 2738 |
| grieving | WhenTrue | 6 | 3 | 2 | yes | 0.007 | 971 |
| happy | WhenTrue | 6 | 4 | 0 | yes | 0.164 | 1729 |
| has-part | RelationalSchema | 2 | 2 | 0 | yes | 0.969 | 532 |
| help | RelationalSchema | 6 | 3 | 0 | yes | 0.930 | 1413 |
| helpful | WhenTrue | 5 | 3 | 1 | yes | 0.415 | 1567 |
| inside | RelationalSchema | 4 | 2 | 0 | yes | 0.961 | 581 |
| kind | InstanceSchema | 16 | 6 | 0 | yes | 0.953 | 4941 |
| learn | RelationalSchema | 8 | 3 | 0 | yes | 0.833 | 1389 |
| liar | InstanceSchema | 6 | 5 | 1 | yes | 0.197 | 1455 |
| lie | InstanceSchema | 10 | 4 | 0 | yes | 0.782 | 2049 |
| lose | RelationalSchema | 9 | 4 | 0 | yes | 0.971 | 2924 |
| lost | WhenTrue | 5 | 4 | 1 | yes | 0.198 | 1045 |
| make | RelationalSchema | 6 | 3 | 0 | yes | 0.890 | 1044 |
| maker-of | RelationalSchema | 7 | 3 | 1 | yes | 0.230 | 1533 |
| memory | InstanceSchema | 10 | 4 | 1 | yes | 0.227 | 1855 |
| near | RelationalSchema | 7 | 3 | 0 | yes | 0.908 | 1007 |
| part-of | RelationalSchema | 6 | 4 | 0 | yes | 0.894 | 828 |
| promise | InstanceSchema | 10 | 5 | 0 | yes | 0.944 | 4015 |
| remember | RelationalSchema | 6 | 3 | 0 | yes | 0.901 | 788 |
| reminder | InstanceSchema | 14 | 4 | 2 | yes | 0.178 | 2528 |
| repair | RelationalSchema | 9 | 4 | 1 | yes | 0.215 | 1789 |
| right | WhenTrue | 7 | 4 | 0 | yes | 0.940 | 2626 |
| sad | WhenTrue | 8 | 6 | 0 | yes | 0.000 | 2311 |
| take | RelationalSchema | 10 | 5 | 0 | yes | 0.962 | 3182 |
| teacher | InstanceSchema | 7 | 4 | 1 | yes | 0.163 | 2000 |
| thief | InstanceSchema | 7 | 3 | 1 | yes | 0.117 | 1781 |
| trustworthy | WhenTrue | 8 | 4 | 2 | yes | 0.139 | 2075 |
| useful | WhenTrue | 9 | 4 | 0 | yes | 0.771 | 1611 |
| visible | WhenTrue | 7 | 3 | 0 | yes | 0.884 | 1132 |
| wrong | WhenTrue | 7 | 4 | 0 | yes | 0.928 | 3312 |

> Decoding is stated, per the construction, as recoverable GIVEN THE KERNEL
> (codebook + concept lexicon as cleanup memory). Confidence = selection
> margin (best vs runner-up) or presence ratio per decode step.