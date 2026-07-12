# SCALE-1 S0 first rung — measured metrics at n=10000

date: 2026-07-12T14:39:01.985Z

## Epistemic status
- MEASURED: every number in the tables below is a direct local measurement of this pipeline.
- STIPULATED: subset selection rule, lexFile→UFO crosswalk, anchor lists, kot-enc-import/0-poc construction and its weights.
- EXTRAPOLATION: all 100k/1M projections; to be measured, never a premise.
- NO FEASIBILITY CONCLUSION: S0 qualifies machinery only (design §8, §14). Correctness/efficiency remain INCONCLUSIVE-PENDING.
- NOT construction B: these vectors are NOT kot-enc-B/1 outputs; nothing here touches the pinned encoder or its goldens.

## Ingest
- rule: top-N WordNet 3.1 synsets by summed SemCor tag_cnt from source index.sense; ties (tag_cnt, then URN ASC); pure function of pinned source + N
- selected n=10000 of 117791 synsets; boundary tag_cnt=4; pos mix {"a":1810,"n":4713,"r":575,"v":2902}
- axioms: 58270 (5.83/concept)

## UFO typing — imported vs inferred split

| field | source-asserted | rule-inferred | soft-candidate | underdetermined |
|---|---|---|---|---|
| denotation_level | 127 (1.27%) | 9873 (98.73%) | 0 (0.00%) | 0 (0.00%) |
| ontic_category | 0 (0.00%) | 5204 (52.04%) | 4192 (41.92%) | 604 (6.04%) |
| sortality | 0 (0.00%) | 1196 (11.96%) | 254 (2.54%) | 8550 (85.50%) |
| rigidity | 0 (0.00%) | 1069 (10.69%) | 254 (2.54%) | 8677 (86.77%) |
| identity | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 10000 (100.00%) |
| dependence | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 10000 (100.00%) |

## Encode cost (measured)

| store | D | wall s | µs/concept | atoms | FFTs |
|---|---|---|---|---|---|
| canon8192 | 8192 | 392.7 | 39270 | 68270 | 0 |
| proj512 | 512 | 392.7 | 39270 | 68270 | 0 |
| proj576 | 576 | 392.7 | 39270 | 68270 | 0 |
| native512 | 512 | 2.6 | 258 | 68270 | 0 |
| native576 | 576 | 3.3 | 332 | 68270 | 0 |
| native512lex | 512 | 3.6 | 359 | 93495 | 0 |

## Storage (measured fp32 on disk; fp64/fp16 derived)

| store | D | fp32 MB | fp64 MB | fp16 MB |
|---|---|---|---|---|
| canon8192 | 8192 | 327.68 | 655.36 | 163.84 |
| proj512 | 512 | 20.48 | 40.96 | 10.24 |
| proj576 | 576 | 23.04 | 46.08 | 11.52 |
| native512 | 512 | 20.48 | 40.96 | 10.24 |
| native576 | 576 | 23.04 | 46.08 | 11.52 |
| native512lex | 512 | 20.48 | 40.96 | 10.24 |

## Collision / margin — predicted (§6.5 √(2·ln m/D)) vs measured

| store | D | pred σ | meas σ (disjoint) | pred max-spurious | meas median per-concept max-DISJOINT | meas max disjoint pair | meas median per-concept max-ANY | meas p95 max-ANY |
|---|---|---|---|---|---|---|---|---|
| proj512 | 512 | 0.0442 | 0.0456 | 0.1897 | 0.169 | 0.2415 | 0.3857 | 1 |
| proj576 | 576 | 0.0417 | 0.0432 | 0.1788 | 0.1621 | 0.2635 | 0.3867 | 1 |

canon8192 (1k sample): pred σ 0.01105, meas σ 0.01106; pred max-spurious @sample 0.0411 (design quotes ≈0.046 @m=10⁴ → formula gives 0.0474); meas median per-concept max-disjoint 0.0353; meas max disjoint pair 0.0866; meas median max-ANY 0.0594.

## Duplicate census (§6.5 collision class 2)
- structural duplicate groups (identical token multisets): 475 groups covering 2008 records; largest group 466 (e.g. urn:lexical-wn31:r-00002669 (barely); urn:lexical-wn31:r-00003864 (basically); urn:lexical-wn31:r-00005103 (merely); urn:lexical-wn31:r-00005348 (simply); urn:lexical-wn31:r-00005948 (automatically))
- vector pairs above cosine thresholds: proj512 {">0.99":124343,">0.999":124343,">0.9999":124343}; native512lex {">0.99":55,">0.999":55,">0.9999":55}
- §6.5 collision class 2: structurally indistinguishable AxiomsOnly records legitimately share a semantic block — the honest margin killer at this rung is DUPLICATE STRUCTURE, not Gaussian crosstalk.

## X4 RDM-Spearman re-measure (design cites 0.9718 / 0.9706 at 54 concepts)

| store | global RDM Spearman | top-pairs (cos>0.05) Spearman | NN recall@1 (all / strong-NN) | NN recall@10 (all / strong-NN) |
|---|---|---|---|---|
| proj512 | 0.2613 | 0.8093 | 0.266 / 0.410 | 0.359 / 0.517 |
| proj576 | 0.2820 | 0.8201 | 0.271 / 0.423 | 0.360 / 0.518 |
| native512 | 0.0530 | 0.8117 | 0.258 / 0.407 | 0.309 / 0.474 |
| native576 | 0.0458 | 0.8002 | 0.263 / 0.417 | 0.314 / 0.487 |
| native512lex | 0.0371 | 0.5571 | 0.156 / 0.246 | 0.226 / 0.352 |

top-pair count: 4639 of 499500 sample pairs. global RDM Spearman on a bulk-import store is dominated by the near-zero disjoint-pair noise floor (σ≈1/√8192≈0.011), which any D-reduction re-randomises — the kernel-v0 0.97 calibration does NOT transfer to bulk-import RDMs at this scale. Structure-bearing pairs (canon cos>0.05) and NN retrieval preservation are the operationally relevant fidelity numbers.

## Extrapolation (EXTRAPOLATION tags; to be measured, never premises)
```json
{
  "encodeCpuHours": {
    "perConceptSecondsCanon8192_inclJL": 0.0393,
    "at100k": 1.09,
    "at1M": 10.9,
    "designBandS1CpuHours": "200-2000 (all stages, not just vectorisation)",
    "designBandS2CpuHours": "2k-20k"
  },
  "exactNnCleanupWallHours_Onsquared": {
    "at10k_measuredSeconds": 117,
    "at100k_hours": 3.2,
    "at1M_hours": 324,
    "note": "O(m²) exact scan; this is the §6.5 decoder-cleanup/retrieval analogue — ANN + the ≥0.99 exact-vs-ANN recall gate becomes MANDATORY between 100k and 1M"
  },
  "storageGB_fp16_dense8192": {
    "at10k": 0.164,
    "at100k": 1.64,
    "at1M": 16.4,
    "design6_4": "0.16 / 1.64 / 16.38"
  }
}
```