# SCALE-1 S0 first rung — measured metrics at n=1000

date: 2026-07-12T14:24:15.825Z

## Epistemic status
- MEASURED: every number in the tables below is a direct local measurement of this pipeline.
- STIPULATED: subset selection rule, lexFile→UFO crosswalk, anchor lists, kot-enc-import/0-poc construction and its weights.
- EXTRAPOLATION: all 100k/1M projections; to be measured, never a premise.
- NO FEASIBILITY CONCLUSION: S0 qualifies machinery only (design §8, §14). Correctness/efficiency remain INCONCLUSIVE-PENDING.
- NOT construction B: these vectors are NOT kot-enc-B/1 outputs; nothing here touches the pinned encoder or its goldens.

## Ingest
- rule: top-N WordNet 3.1 synsets by summed SemCor tag_cnt from source index.sense; ties (tag_cnt, then URN ASC); pure function of pinned source + N
- selected n=1000 of 117791 synsets; boundary tag_cnt=40; pos mix {"a":132,"n":380,"r":108,"v":380}
- axioms: 13611 (13.61/concept)

## UFO typing — imported vs inferred split

| field | source-asserted | rule-inferred | soft-candidate | underdetermined |
|---|---|---|---|---|
| denotation_level | 5 (0.50%) | 995 (99.50%) | 0 (0.00%) | 0 (0.00%) |
| ontic_category | 0 (0.00%) | 505 (50.50%) | 377 (37.70%) | 118 (11.80%) |
| sortality | 0 (0.00%) | 70 (7.00%) | 25 (2.50%) | 905 (90.50%) |
| rigidity | 0 (0.00%) | 65 (6.50%) | 25 (2.50%) | 910 (91.00%) |
| identity | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 1000 (100.00%) |
| dependence | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 1000 (100.00%) |

## Encode cost (measured)

| store | D | wall s | µs/concept | atoms | FFTs |
|---|---|---|---|---|---|
| canon8192 | 8192 | 45.7 | 45734 | 14611 | 0 |
| proj512 | 512 | 45.7 | 45734 | 14611 | 0 |
| proj576 | 576 | 45.7 | 45734 | 14611 | 0 |
| native512 | 512 | 0.3 | 341 | 14611 | 0 |
| native576 | 576 | 0.4 | 372 | 14611 | 0 |
| native512lex | 512 | 0.4 | 351 | 17538 | 0 |

## Storage (measured fp32 on disk; fp64/fp16 derived)

| store | D | fp32 MB | fp64 MB | fp16 MB |
|---|---|---|---|---|
| canon8192 | 8192 | 32.77 | 65.54 | 16.38 |
| proj512 | 512 | 2.05 | 4.1 | 1.02 |
| proj576 | 576 | 2.3 | 4.61 | 1.15 |
| native512 | 512 | 2.05 | 4.1 | 1.02 |
| native576 | 576 | 2.3 | 4.61 | 1.15 |
| native512lex | 512 | 2.05 | 4.1 | 1.02 |

## Collision / margin — predicted (§6.5 √(2·ln m/D)) vs measured

| store | D | pred σ | meas σ (disjoint) | pred max-spurious | meas median per-concept max-DISJOINT | meas max disjoint pair | meas median per-concept max-ANY | meas p95 max-ANY |
|---|---|---|---|---|---|---|---|---|
| proj512 | 512 | 0.0442 | 0.0457 | 0.1643 | 0.1448 | 0.2015 | 0.1617 | 1 |
| proj576 | 576 | 0.0417 | 0.0434 | 0.1549 | 0.1373 | 0.204 | 0.1552 | 1 |

canon8192 (1k sample): pred σ 0.01105, meas σ 0.01096; pred max-spurious @sample 0.0411 (design quotes ≈0.046 @m=10⁴ → formula gives 0.0474); meas median per-concept max-disjoint 0.0344; meas max disjoint pair 0.0541; meas median max-ANY 0.0823.

## Duplicate census (§6.5 collision class 2)
- structural duplicate groups (identical token multisets): 12 groups covering 130 records; largest group 86 (e.g. urn:lexical-wn31:r-00002669 (barely); urn:lexical-wn31:r-00003864 (basically); urn:lexical-wn31:r-00005103 (merely); urn:lexical-wn31:r-00006486 (largely); urn:lexical-wn31:r-00007414 (approximately))
- vector pairs above cosine thresholds: proj512 {">0.99":3811,">0.999":3811,">0.9999":3811}; native512lex {">0.99":5,">0.999":5,">0.9999":5}
- §6.5 collision class 2: structurally indistinguishable AxiomsOnly records legitimately share a semantic block — the honest margin killer at this rung is DUPLICATE STRUCTURE, not Gaussian crosstalk.

## X4 RDM-Spearman re-measure (design cites 0.9718 / 0.9706 at 54 concepts)

| store | global RDM Spearman | top-pairs (cos>0.05) Spearman | NN recall@1 (all / strong-NN) | NN recall@10 (all / strong-NN) |
|---|---|---|---|---|
| proj512 | 0.2645 | 0.9768 | 0.396 / 0.635 | 0.504 / 0.767 |
| proj576 | 0.2783 | 0.9856 | 0.410 / 0.656 | 0.502 / 0.769 |
| native512 | 0.0442 | 0.9841 | 0.401 / 0.646 | 0.485 / 0.769 |
| native576 | 0.0542 | 0.9508 | 0.416 / 0.667 | 0.491 / 0.769 |
| native512lex | 0.0370 | 0.3741 | 0.236 / 0.380 | 0.342 / 0.536 |

top-pair count: 7051 of 499500 sample pairs. global RDM Spearman on a bulk-import store is dominated by the near-zero disjoint-pair noise floor (σ≈1/√8192≈0.011), which any D-reduction re-randomises — the kernel-v0 0.97 calibration does NOT transfer to bulk-import RDMs at this scale. Structure-bearing pairs (canon cos>0.05) and NN retrieval preservation are the operationally relevant fidelity numbers.

## Extrapolation (EXTRAPOLATION tags; to be measured, never premises)
```json
{
  "encodeCpuHours": {
    "perConceptSecondsCanon8192_inclJL": 0.0457,
    "at100k": 1.27,
    "at1M": 12.7,
    "designBandS1CpuHours": "200-2000 (all stages, not just vectorisation)",
    "designBandS2CpuHours": "2k-20k"
  },
  "exactNnCleanupWallHours_Onsquared": {
    "at10k_measuredSeconds": 1,
    "at100k_hours": 0,
    "at1M_hours": 3,
    "note": "O(m²) exact scan; this is the §6.5 decoder-cleanup/retrieval analogue — ANN + the ≥0.99 exact-vs-ANN recall gate becomes MANDATORY between 100k and 1M"
  },
  "storageGB_fp16_dense8192": {
    "at10k": 0.016,
    "at100k": 0.16,
    "at1M": 1.6,
    "design6_4": "0.16 / 1.64 / 16.38"
  }
}
```