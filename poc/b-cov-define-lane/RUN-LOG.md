# b-cov define-lane census (bead kernel-of-truth-hu10) — RUN-LOG

**Status:** MEASURED-exploratory counts only. `fable_interpretive_assessed: pending`.
Opus (experiment-runner) reports mechanical counts; the meaning is Fable's to
interpret. NO verdict, NO freeze, NO registry write, NO extrapolation. Every number
below is tagged **MEASURED-exploratory**.
Run date: 2026-07-10. Branch: `opus/f2b-replicate-rightsize`. Tier-0, CPU, ~$0.

## What was measured
Per-benchmark **κ_B^engine** = the DEFINE-checkable fraction (mapper-parse lane)
**after the §C5 uniqueness filter**, over the Tier-A definitional benchmarks that
are AVAILABLE on-box, plus the diagnostic parse/§C5 breakdown. Pipeline invoked as
designed (memo `docs/design-kot-query-define-op.md`):

- leg 1 record — onto-obo `logicalDefinition`, endorsed shards `{go, so, mondo}`.
- leg 2 licence — `data/axioms-definitional-v0/` endorsements (`build_engine` loads).
- leg 3 mapper — `mapper/dist/src/defineTemplates.js` `parseDefineQuestion`
  (driven by `run_mapper.mjs`, DefineIndex injected from `build_define_index.py`).
- §C5 filter — inverse-index collision count over the §2.2 DEFINE-MATCH canonical
  form; item define-checkable iff `n==1`; dropped iff `n≥2`
  (`INELIGIBLE_DEFN_COLLISION`); `n==0` = candidate matches no licensed concept
  [ASM-0131, memo §6 C5].

**method_ref:** `docs/design-kot-query-define-op.md` §6 C5 / §2.2 (ASM-0131);
§7.2 (b-cov define-lane); §3.1 (ASM-0130 endorsement subject convention).

## Scope resolved at STEP 1
| Tier-A benchmark | Availability | Action |
|---|---|---|
| OpenBookQA (test, 500) | in-repo `data/d-ext/source-jsonl/test.jsonl` (Apache-2.0, HF rev 388097e) | RUN (control) |
| def-MMLU biomedical (6 subjects, test, 1,050) | canonical `cais/mmlu` (MIT) — fetched via HF datasets-server rows API | RUN |
| WiC | canonical `pilehvar/wic` returns **HTTP 401**; programme fail-closed sourcing (`data/d-ext/manifest.json`) already declined mirror substitution | **DATA-GAP — not run** |

MMLU subjects pinned per memo §7.2 / strategy §1.2: `college_biology,
college_chemistry, medical_genetics, anatomy, clinical_knowledge, nutrition`.
Split = `test` (the split lighteval scores). Fetched-byte sha256 per subject in
`data/mmlu-fetch-manifest.json` and echoed as `input_sha256` in the summary.

**Endorsed substrate honesty:** only `{go, so, mondo}` carry a `definitional`
endorsement today (CL / UBERON / PO / PATO / CHEBI are minted-on-disk but
**un-endorsed**), so anatomy/cell items whose terms live in those shards are OUT
of the licensed set BY CONSTRUCTION. Endorsement shas verified equal to current
shard bytes (go `9d661d25`, so `10fae0e4`, mondo `b9d20d63`).

## MEASURED-exploratory result — κ_B^engine (mapper-parse lane)
| benchmark | N_total | N_checkable (§C5 n==1) | **κ_B^engine** | no-template | slot-unresolved | abstain | define-retrieve | candidate-bearing |
|---|---|---|---|---|---|---|---|---|
| OpenBookQA-test | 500 | 0 | **0.0000** | 485 | 15 | 0 | 0 | 0 |
| MMLU-college_biology-test | 144 | 0 | **0.0000** | 144 | 0 | 0 | 0 | 0 |
| MMLU-college_chemistry-test | 100 | 0 | **0.0000** | 92 | 8 | 0 | 0 | 0 |
| MMLU-medical_genetics-test | 100 | 0 | **0.0000** | 100 | 0 | 0 | 0 | 0 |
| MMLU-anatomy-test | 135 | 0 | **0.0000** | 135 | 0 | 0 | 0 | 0 |
| MMLU-clinical_knowledge-test | 265 | 0 | **0.0000** | 252 | 12 | 0 | 1 | 0 |
| MMLU-nutrition-test | 306 | 0 | **0.0000** | 289 | 17 | 0 | 0 | 0 |

§C5 breakdown (n==0 no-match / n==1 checkable / n≥2 collision-dropped): **0 / 0 / 0**
on every benchmark — no item reached the §C5 candidate-bearing population, so the
uniqueness filter dropped nothing. κ_B^engine = 0.0000 on all seven rows.

Diagnostic reading of the parse histogram (mechanical, not interpretation):
- The mapper's closed templates (`what is X` / `define X` / `the definition of X`
  / `is X a G that R F` / `X is defined as G that R F` / `which term means G that
  R F`) matched almost no benchmark stem (`no-template` dominates).
- The few `slot-unresolved` rows are `what is <long phrase>` stems whose TERM span
  is a whole clause, not a single onto-obo label (e.g. OBQA "what is the best way
  to guess a babies eye color").
- The single `define-retrieve` (clinical_knowledge #101) matched `what-is`, its
  TERM resolved to one licensed onto-obo concept, but that concept carries no
  `logicalDefinition` → engine `ERR_NO_DEFINITION`.

## Engine definitional index at this run (context)
`defn_licensed=72,839  defn_resolved=13,824  defn_unresolved=3,387`;
`distinct_definition_keys=13,824`; **internal_collision_keys(n≥2)=0** — every
resolved definition in the endorsed substrate is structurally unique, so §C5 has no
collision to drop even in principle at this substrate. (Consistent with the
internal define-op coverage census `poc/define-op-census`, 13,824/17,211 resolved.)

## Instrument validity — the 0.0000 is a REAL null, not a broken harness
`positive_control.py` feeds three questions that DO target an endorsed definition
(GO:0000018 "regulation of DNA recombination" = "biological regulation" that
"regulates" "DNA recombination") and gets:
- `which term means biological regulation that regulates DNA recombination` →
  candidate parse → §C5 **n==1** → engine DEFINE-MATCH **True**;
- `is X a G that R F` → DEFINE-MATCH query → n==1 → True;
- `what is X?` → DEFINE-retrieve → engine `answer`.
`POSITIVE CONTROL: PASS`. So the pipeline yields a checkable when one exists; the
benchmark 0.0000 is the measured absence of define-template-shaped, substrate-
resolving items, not an instrument failure. Also, per-item instrument-validity
(census predicate n==1 ⟺ engine DEFINE-MATCH true) had **0 disagreements** (there
were 0 n==1 items to check on the benchmarks).

## Gold-parse vs mapper-parse
For third-party benchmark items there is no hand-authored grammar query, so the
**gold-parse lane is N/A** here; this census is the **mapper-parse lane**. The
gold-parse coverage lane is the internal define-op census (`poc/define-op-census`).

## Reproduce
```
python3 poc/b-cov-define-lane/fetch_mmlu.py          # canonical cais/mmlu -> data/
python3 poc/b-cov-define-lane/build_define_index.py  # DefineIndex over {go,so,mondo}
python3 poc/b-cov-define-lane/census.py              # -> census-summary.json + detail/
python3 poc/b-cov-define-lane/positive_control.py    # instrument-validity PASS
```

## Boundary-stop queued for Fable (NOT improvised)
**WiC data gap.** The pre-declared canonical source `pilehvar/wic` is HTTP-401
gated; programme fail-closed sourcing already declined mirror substitution.
Unblock requires a governance decision above the runner remit: EITHER (a) an HF
credential for `pilehvar/wic`, OR (b) a maintainer/Fable decision to accept a
specific pinned mirror (e.g. `super_glue` config `wic`) as the exploratory source.
Until then the WiC κ_B^engine cell is unmeasurable and is reported as a gap, not a
zero.

## Explicitly NOT done (governance)
No `registry/**` write (exploratory). No git. No `@handle`/email strings in
outputs. No child agents. No verdict / interpretation / freeze — Fable interprets.
