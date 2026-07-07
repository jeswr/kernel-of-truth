# X2 on kernel-v0 — exact decode (minimal vs full-corpus cleanup lexicon)

date: 2026-07-07T03:44:22.235Z
corpus: kernel-v0 (authored; research-grade, NOT federation-endorsed) — 54 concepts
encoder content-hash: `40e8c8ba4c3d081c5051ea62d946d2ee9ee9f3205853b5c377a4c1e647e2d10c` (matches manifest pin: true)
corpus manifest sha256: `a9efbccdd9c7fe50f614d4687078584da603c5f07dce822cd323e0a5d7f4bdde`
corpus content-hash (concepts/*.json + manifest): `f23f5211ff1755975dd1ce8128ff810b316051c00ee2c1d56bae488f8f928751`

**Criterion (minimal lexicon): 54/54 exact -> FAIL** (51/54 exact; reference-bearing 18/18; min confidence 0.000 at `angry`)

Full-corpus lexicon (all 53 others as cleanup candidates): 51/54 exact (reference-bearing 18/18; min confidence 0.000). The gap between the two conditions measures
cleanup-lexicon interference: extra corpus vectors acting as false attractors during
the decoder's atomic-vs-concept competitions. Exact = canonical-JSON equality.

## Minimal lexicon (pre-registered setting)

| concept | frame | clauses | depth | crefs | exact | min-conf | ms |
|---|---|---|---|---|---|---|---|
| afraid | WhenTrue | 8 | 5 | 0 | **NO** | 0.624 | 3346 |
| alive | WhenTrue | 5 | 3 | 0 | yes | 0.976 | 1001 |
| angry | WhenTrue | 7 | 5 | 0 | **NO** | 0.000 | 7386 |
| archived | WhenTrue | 14 | 7 | 0 | yes | 0.000 | 6309 |
| begin | RelationalSchema | 6 | 3 | 0 | yes | 0.969 | 542 |
| believe | RelationalSchema | 5 | 3 | 0 | yes | 0.974 | 665 |
| birth | InstanceSchema | 7 | 4 | 1 | yes | 0.967 | 871 |
| bookmark | InstanceSchema | 11 | 5 | 0 | yes | 0.900 | 1711 |
| break | RelationalSchema | 13 | 5 | 0 | yes | 0.946 | 1530 |
| broken | WhenTrue | 7 | 5 | 1 | yes | 0.951 | 930 |
| cause | RelationalSchema | 9 | 3 | 0 | yes | 0.894 | 898 |
| celebration | InstanceSchema | 10 | 3 | 2 | yes | 0.867 | 1966 |
| change | InstanceSchema | 6 | 5 | 0 | yes | 0.955 | 853 |
| condolence | InstanceSchema | 7 | 3 | 1 | yes | 0.871 | 1229 |
| conversation | InstanceSchema | 8 | 3 | 1 | yes | 0.918 | 1633 |
| dead | WhenTrue | 6 | 4 | 0 | yes | 0.977 | 592 |
| death | InstanceSchema | 8 | 3 | 1 | yes | 0.949 | 2221 |
| end | RelationalSchema | 8 | 4 | 0 | yes | 0.969 | 1440 |
| event | InstanceSchema | 7 | 4 | 0 | yes | 0.969 | 1085 |
| find | RelationalSchema | 9 | 5 | 0 | yes | 0.893 | 1856 |
| forget | RelationalSchema | 6 | 3 | 0 | yes | 0.975 | 668 |
| friend | RelationalSchema | 9 | 4 | 0 | yes | 0.898 | 4678 |
| gift | InstanceSchema | 8 | 4 | 1 | yes | 0.949 | 2096 |
| give | RelationalSchema | 14 | 5 | 0 | yes | 0.951 | 2227 |
| grieving | WhenTrue | 6 | 3 | 2 | yes | 0.955 | 799 |
| happy | WhenTrue | 6 | 4 | 0 | yes | 0.164 | 1608 |
| has-part | RelationalSchema | 2 | 2 | 0 | yes | 0.969 | 414 |
| help | RelationalSchema | 6 | 3 | 0 | yes | 0.930 | 1232 |
| helpful | WhenTrue | 5 | 3 | 1 | yes | 0.929 | 1819 |
| inside | RelationalSchema | 4 | 2 | 0 | yes | 0.961 | 1005 |
| kind | InstanceSchema | 16 | 6 | 0 | yes | 0.953 | 7933 |
| learn | RelationalSchema | 8 | 3 | 0 | yes | 0.833 | 2229 |
| liar | InstanceSchema | 6 | 5 | 1 | yes | 0.894 | 1644 |
| lie | InstanceSchema | 10 | 4 | 0 | yes | 0.782 | 1478 |
| lose | RelationalSchema | 9 | 4 | 0 | yes | 0.971 | 2355 |
| lost | WhenTrue | 5 | 4 | 1 | yes | 0.949 | 788 |
| make | RelationalSchema | 6 | 3 | 0 | yes | 0.890 | 670 |
| maker-of | RelationalSchema | 7 | 3 | 1 | yes | 0.944 | 1256 |
| memory | InstanceSchema | 10 | 4 | 1 | yes | 0.950 | 1827 |
| near | RelationalSchema | 7 | 3 | 0 | yes | 0.908 | 690 |
| part-of | RelationalSchema | 6 | 4 | 0 | yes | 0.894 | 636 |
| promise | InstanceSchema | 10 | 5 | 0 | yes | 0.944 | 2639 |
| remember | RelationalSchema | 6 | 3 | 0 | yes | 0.901 | 712 |
| reminder | InstanceSchema | 14 | 4 | 2 | yes | 0.241 | 2466 |
| repair | RelationalSchema | 9 | 4 | 1 | yes | 0.967 | 1067 |
| right | WhenTrue | 7 | 4 | 0 | yes | 0.940 | 2544 |
| sad | WhenTrue | 8 | 6 | 0 | **NO** | 0.000 | 1713 |
| take | RelationalSchema | 10 | 5 | 0 | yes | 0.962 | 1649 |
| teacher | InstanceSchema | 7 | 4 | 1 | yes | 0.819 | 1598 |
| thief | InstanceSchema | 7 | 3 | 1 | yes | 0.916 | 1988 |
| trustworthy | WhenTrue | 8 | 4 | 2 | yes | 0.210 | 1457 |
| useful | WhenTrue | 9 | 4 | 0 | yes | 0.771 | 1281 |
| visible | WhenTrue | 7 | 3 | 0 | yes | 0.884 | 847 |
| wrong | WhenTrue | 7 | 4 | 0 | yes | 0.928 | 2981 |

### Non-exact (minimal)

- `afraid`: decode failed: ERR_REF_NOT_INTRODUCED at $.clauses[0].args[0].roles.quote.clauses[1].roles.complement: ref 2 used before its introducing occurrence (or out of quote scope); lowest-confidence step: {"path":"$.clauses[0].args[0].quote.clauses[2].args[0].time.anchor","decision":"anchor","value":"prime:NOW","confidence":0.624069033346798}
- `angry`: ok-but-wrong: decoded AST validates but differs from authored AST
- `sad`: ok-but-wrong: decoded AST validates but differs from authored AST

## Full-corpus lexicon (interference measurement)

| concept | frame | clauses | depth | crefs | exact | min-conf | ms |
|---|---|---|---|---|---|---|---|
| afraid | WhenTrue | 8 | 5 | 0 | **NO** | 0.624 | 1884 |
| alive | WhenTrue | 5 | 3 | 0 | yes | 0.976 | 550 |
| angry | WhenTrue | 7 | 5 | 0 | **NO** | 0.000 | 2950 |
| archived | WhenTrue | 14 | 7 | 0 | yes | 0.000 | 5854 |
| begin | RelationalSchema | 6 | 3 | 0 | yes | 0.969 | 473 |
| believe | RelationalSchema | 5 | 3 | 0 | yes | 0.974 | 689 |
| birth | InstanceSchema | 7 | 4 | 1 | yes | 0.331 | 926 |
| bookmark | InstanceSchema | 11 | 5 | 0 | yes | 0.900 | 1903 |
| break | RelationalSchema | 13 | 5 | 0 | yes | 0.946 | 2097 |
| broken | WhenTrue | 7 | 5 | 1 | yes | 0.169 | 921 |
| cause | RelationalSchema | 9 | 3 | 0 | yes | 0.894 | 930 |
| celebration | InstanceSchema | 10 | 3 | 2 | yes | 0.021 | 1461 |
| change | InstanceSchema | 6 | 5 | 0 | yes | 0.955 | 1011 |
| condolence | InstanceSchema | 7 | 3 | 1 | yes | 0.318 | 1557 |
| conversation | InstanceSchema | 8 | 3 | 1 | yes | 0.331 | 2213 |
| dead | WhenTrue | 6 | 4 | 0 | yes | 0.977 | 575 |
| death | InstanceSchema | 8 | 3 | 1 | yes | 0.330 | 1116 |
| end | RelationalSchema | 8 | 4 | 0 | yes | 0.969 | 850 |
| event | InstanceSchema | 7 | 4 | 0 | yes | 0.969 | 912 |
| find | RelationalSchema | 9 | 5 | 0 | yes | 0.893 | 1611 |
| forget | RelationalSchema | 6 | 3 | 0 | yes | 0.975 | 487 |
| friend | RelationalSchema | 9 | 4 | 0 | yes | 0.898 | 2885 |
| gift | InstanceSchema | 8 | 4 | 1 | yes | 0.334 | 2580 |
| give | RelationalSchema | 14 | 5 | 0 | yes | 0.951 | 2769 |
| grieving | WhenTrue | 6 | 3 | 2 | yes | 0.007 | 763 |
| happy | WhenTrue | 6 | 4 | 0 | yes | 0.164 | 1644 |
| has-part | RelationalSchema | 2 | 2 | 0 | yes | 0.969 | 698 |
| help | RelationalSchema | 6 | 3 | 0 | yes | 0.930 | 1261 |
| helpful | WhenTrue | 5 | 3 | 1 | yes | 0.415 | 1026 |
| inside | RelationalSchema | 4 | 2 | 0 | yes | 0.961 | 427 |
| kind | InstanceSchema | 16 | 6 | 0 | yes | 0.953 | 4584 |
| learn | RelationalSchema | 8 | 3 | 0 | yes | 0.833 | 1087 |
| liar | InstanceSchema | 6 | 5 | 1 | yes | 0.197 | 1194 |
| lie | InstanceSchema | 10 | 4 | 0 | yes | 0.782 | 1943 |
| lose | RelationalSchema | 9 | 4 | 0 | yes | 0.971 | 3007 |
| lost | WhenTrue | 5 | 4 | 1 | yes | 0.198 | 890 |
| make | RelationalSchema | 6 | 3 | 0 | yes | 0.890 | 735 |
| maker-of | RelationalSchema | 7 | 3 | 1 | yes | 0.230 | 1320 |
| memory | InstanceSchema | 10 | 4 | 1 | yes | 0.227 | 1812 |
| near | RelationalSchema | 7 | 3 | 0 | yes | 0.908 | 1001 |
| part-of | RelationalSchema | 6 | 4 | 0 | yes | 0.894 | 709 |
| promise | InstanceSchema | 10 | 5 | 0 | yes | 0.944 | 3229 |
| remember | RelationalSchema | 6 | 3 | 0 | yes | 0.901 | 886 |
| reminder | InstanceSchema | 14 | 4 | 2 | yes | 0.178 | 2475 |
| repair | RelationalSchema | 9 | 4 | 1 | yes | 0.215 | 1300 |
| right | WhenTrue | 7 | 4 | 0 | yes | 0.940 | 2585 |
| sad | WhenTrue | 8 | 6 | 0 | **NO** | 0.000 | 2238 |
| take | RelationalSchema | 10 | 5 | 0 | yes | 0.962 | 2333 |
| teacher | InstanceSchema | 7 | 4 | 1 | yes | 0.163 | 1944 |
| thief | InstanceSchema | 7 | 3 | 1 | yes | 0.117 | 1997 |
| trustworthy | WhenTrue | 8 | 4 | 2 | yes | 0.139 | 1534 |
| useful | WhenTrue | 9 | 4 | 0 | yes | 0.771 | 1821 |
| visible | WhenTrue | 7 | 3 | 0 | yes | 0.884 | 1629 |
| wrong | WhenTrue | 7 | 4 | 0 | yes | 0.928 | 6547 |

### Non-exact (full-corpus)

- `afraid`: decode failed: ERR_REF_NOT_INTRODUCED at $.clauses[0].args[0].roles.quote.clauses[1].roles.complement: ref 2 used before its introducing occurrence (or out of quote scope); lowest-confidence step: {"path":"$.clauses[0].args[0].quote.clauses[2].args[0].time.anchor","decision":"anchor","value":"prime:NOW","confidence":0.624069033346798}
- `angry`: ok-but-wrong: decoded AST validates but differs from authored AST
- `sad`: ok-but-wrong: decoded AST validates but differs from authored AST

> Decoding is stated, per the construction, as recoverable GIVEN THE KERNEL
> (codebook + concept lexicon as cleanup memory). Confidence = selection
> margin (best vs runner-up) or presence ratio per decode step.