# define-op internal-coverage census (Opus execution, 2026-07-09)

**Status:** MEASURED counts only. `fable_interpretive_assessed: pending` — Opus reports
mechanical counts; the meaning is Fable's to interpret. NO extrapolation to any benchmark
(WiC / def-MMLU / kappa_B) is asserted.

## What was measured
Over the 17,211 minted `logicalDefinition`-bearing onto-obo concepts (GO 9,307 + SO 219 +
MONDO 7,685), how many the frozen define-op (`tools/axiom/kot_axiom.py`, DEFINE op) makes
CHECKABLE (engine `status=answer`) vs refuses. Endorsement licensed by shard membership
(subject non-load-bearing for the measurement — see boundary-stop). Reproduce:
`python3 poc/define-op-census/define_census.py`.

## MEASURED result
| shard | population | checkable (answer) | ERR_DEFN_UNRESOLVED | fraction |
|---|---|---|---|---|
| go.jsonl | 9,307 | 9,307 | 0 | 1.0000 |
| so.jsonl | 219 | 18 | 201 | 0.0822 |
| mondo.jsonl | 7,685 | 103 | 7,582 | 0.0134 |
| **TOTAL** | **17,211** | **9,428** | **7,783** | **0.5478** |

Mechanical cause of ALL 7,783 unresolved (deterministic replay): the differentia relation
shorthand is not in the pinned 10-value alias table (built from the GO+PO histogram). 0
failures on unminted genus/filler. Top unaliased shorthands — SO: has_quality(163),
has_origin(29); MONDO: disease_has_location(2539), has_material_basis_in_germline_mutation_in(2502),
has_characteristic(1026). => the SO/MONDO gate is the shorthand->relation-IRI alias coverage
(bead kernel-of-truth-8es), NOT the define-op engine.

## Boundary-stops (queued for Fable, NOT improvised)
1. Production `definitional` endorsement `subject` field is unspecified by the memo (§3.1) —
   staged records under staged-endorsements/ carry an invalid `__PENDING_FABLE_SUBJECT_PIN__`
   subject (fail-closed). Fable pins the convention (minted corpus-marker URN vs concept-URN),
   then Opus finalizes to data/axioms-v0/defn-onto-obo-{go,so,mondo}.json.
2. Benchmark kappa_B census (N1-LB §10.1) needs a Fable instrument design + WiC/def-MMLU data
   (WiC 401-gated; def-MMLU unpinned) — NOT buildable by adapting m0b. Bead kernel-of-truth-hu10.

## RE-RUN post-8es + relation-reading engine (2026-07-09) — AUTHORITATIVE MEASURED
After bead 8es (extractor resolves differentia relations) + the engine reading the resolved
`relation` field + the endorsements loaded from data/axioms-definitional-v0/, re-running
`define_census.py` (shard shas updated to go 9d661d25 / so 10fae0e4 / mondo b9d20d63):

| shard | population | checkable (answer) | ERR_DEFN_UNRESOLVED |
|---|---|---|---|
| go.jsonl | 9,307 | 9,307 | 0 |
| so.jsonl | 219 | 219 | 0 |
| mondo.jsonl | 7,685 | 3,744 | 3,941 |
| **TOTAL** | **17,211** | **13,270** | **3,941** |

Checkable fraction **0.7710** (was 0.5478 pre-8es). SO fully unlocked (18->219); MONDO 103->3,744;
GO byte-unchanged. The 3,941 MONDO unresolved are ALL foreign fillers (HP/CHEBI/NCBITaxon) — the
held Wave-A ingestion gap, not the engine. Fable interpretation still pending (what this coverage
means for the linter Axis-A + benchmark N1-LB kappa_B).
