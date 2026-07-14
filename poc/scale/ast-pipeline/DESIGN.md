# AST-generation escalation/ensemble pipeline — design + blind assessment harness

**Status: exploratory methodology R&D.** No prereg-freeze, no registry write, no git commit.
Nothing here is a registered experiment; every design choice below is **STIPULATED-not-MEASURED**
unless it cites a measured artefact. Author: fable (lead designer). Builder-judge separation:
this directory's author runs NOTHING beyond a 2-concept dry run; the coordinator (Opus) owns the
full generation sweep and ALL judging, so the builder never grades its own homework.

## 1. Problem

A kot-ast/1 explication renders a concept's differentia using ONLY profile-1's 65 semantic
primes (`encoder/src/lexicon.ts` `PRIMES`; restated in `concept-def-prompt.md` §3.4).
Measured single-shot self-flagged faithful yield on consensus-100 (n=100, 6 models,
`poc/scale/consensus-100/ast-lossy-by-model.md`): Claude family ~33% (opus 31 / fable 35 /
haiku 34), GPT family ~10% (sol 11 / luna 9 / terra 9). A blind cross-vendor adjudication
(`split-concept-adjudication.md`) established the Claude surplus is GENUINE renderability, not
leniency, and that the concept-level renderable ceiling is ≈51/100.

The maintainer wants a PIPELINE that raises the odds of a good/complete AST cheaply — "try a
luna first; if it is in the ~90% AST-lossy case then try the ensemble" — and independent
cross-model assessment of the pipeline's output so we can trust it.

## 2. Data reused (zero new generation for S0/S1/S2)

- `poc/scale/consensus-100/gen/*.json` — 600 existing single-shot records + `.report.json`
  self-flags/costs. **Measured:** 20 of the 144 records covering this sample's 24 concepts fail
  the mechanical gate (`gate_validateExplication_encode.ok=false`; all 20 are opus48/haiku45
  referent-discipline errors; every fable5 and gpt56luna record in the sample is gate-clean).
  Gate-failing records are excluded from the judge pool and score as NOT-FAITHFUL for any
  strategy that would select them — a real pipeline would never ship a gate-invalid record.
- `poc/scale/consensus-100/concepts-100.json` — concept/urn/pos/lemmas/wn31_gloss rows.
- Self-flag buckets recomputed from the report files (STIPULATED recomputation rule: a concept
  is *unanimous-faithful* / *unanimous-lossy* iff all 6 flags agree; *SPLIT* otherwise;
  `predation` has only 5 flags on disk and is excluded). Result: 6 / 48 / 45 (+1 excluded) —
  matches `ast-lossy-by-model.md` up to its counting of the 5-flag concept.
- `poc/scale/concept-def-agent/define_concept.py` — the pinned generation runner (claude -p
  headless / codex exec isolated-home), reused verbatim as a subprocess for ALL new calls, so
  every new record passes the same strict-JSON extraction + mechanical checks + encoder gate
  and emits the same report/provenance format.

**Leakage rules.** The split-concept adjudication's per-concept verdicts are PRIOR EVIDENCE and
are NOT used anywhere in this pipeline: not in sample selection (selection is a deterministic
stride over URN order, blind to adjudication), not in any generation prompt (the forcing
addendum states general decomposition discipline only, no per-concept or aggregate verdicts),
and not shown to judges. Judges see no self-flags, no model identities, no `notes`, no
strategy labels. No benchmark/eval items are read anywhere.

## 3. The pipeline strategies compared (all scored by the same blind judges)

Per concept, each strategy nominates exactly one candidate AST (S2 nominates a set; see below).
Candidates are deduplicated across strategies before judging, so a record is judged once no
matter how many strategies select it.

| id | strategy | candidate rule | new calls |
|---|---|---|---|
| **S0** | baseline single-shot Luna | existing `gen/<slug>.gpt56luna.json` | 0 |
| **S1** | cascade Luna→Claude (maintainer's cheapest form) | Luna's record if Luna self-flagged *faithful*, else claude-fable-5's existing record (fable5 = highest measured faithful self-rate, 35/100; new Claude call ONLY if the record were absent — for this sample all are present) | 0 |
| **S2** | ensemble-select best-of-6 (achievable ceiling) | all gate-clean records among the 6 existing gens enter the judge pool; the strategy scores FAITHFUL iff ANY is judged faithful (post-hoc selection by judge — reported as the ceiling of "run several, keep the faithful one") | 0 |
| **S3** | forcing-retry | if Luna self-flagged *lossy*: ONE new gpt-5.6-luna call with the forcing prompt (base `concept-def-prompt.md` + `forcing-addendum.md` §6 decomposition discipline); else Luna's existing record. Run on GPT (Luna) to avoid Claude subscription quota contention — STIPULATED for quota reasons, and it also tests the prompt on the weakest self-yield family (~9%), the hardest test | 18 |
| **S4** | full cascade + ensemble-MERGE | S1's candidate where S1's selected record self-flags *faithful*; where BOTH Luna and fable5 self-flag lossy: ONE new gpt-5.6-luna call given the concept + the first 3 gate-clean records in priority order [fable5, opus48, gpt56sol, gpt56haiku-never — i.e. haiku45, gpt56terra, gpt56luna] anonymised, with `merge-addendum.md` §6 synthesis instructions; the merged record is the candidate | 11 |

S4 is included (the optional slot) because it is the maintainer's phrase "then try the
ensemble" taken literally, and it is the only strategy that can beat S2's ceiling (merge can
create a faithful record where none of the 6 singles is faithful). Merger = Luna (not sol/terra/
opus48) so NO judge model authors any NEW pipeline output — judges then only ever see their own
consensus-era records, under blinding (residual self-judging caveat disclosed in §5).

Sizing (measured from the sample's self-flags): 18 of 24 concepts have Luna=lossy (S3);
11 of 24 have Luna=lossy AND fable5=lossy (S4). Total new generation: **29 codex (Luna) calls,
0 Claude calls** (dry run adds ~4 more, incl. one deliberate Claude-path check).

## 4. The concept sample (`sample.json`)

STIPULATED stratification: the pipeline must add value where single-shot fails, with easy
controls retained — 4 unanimous-faithful (controls; every strategy should stay faithful) +
12 SPLIT (the value region: renderable-in-principle, single-shot flaky) + 8 unanimous-lossy
(the hard tail; tests whether forcing/merge extract anything and whether judges resist
over-crediting). n=24 keeps judging ≈ 24×2 batch calls.

STIPULATED selection rule (deterministic, adjudication-blind, no cherry-picking): within each
bucket sort members by URN byte order and take stride indices ⌊i·n/k⌋, i=0..k-1. Result:

- **unanimous-faithful (4):** appearance, exit, fidelity, repeater
- **SPLIT (12):** apparition, fastening, poisoning, access, depletion, dissociation, view,
  inhabitancy, wealth, feasibility, builder, medium
- **unanimous-lossy (8):** ransom, service, dislocation, conception, cheerfulness,
  bill poster, heir, stockholder

Incidental coverage check (measured, post-hoc): the SPLIT picks include both cascade branches
(wealth and medium have Luna=faithful, exercising S1's "accept Luna" arm) and both
fable-agrees/fable-disagrees cases. `sample.json` is regenerable via
`python3 run_pipeline.py sample` and carries per-concept buckets, flags, and the rule string.

## 5. Blind assessment harness

**What is judged.** Per concept, the deduplicated pool of gate-clean candidate ASTs (6 existing
minus gate failures, + S3 record, + S4 record; measured pool size 5–8). Judges see ONLY: the
concept label, pos, lemmas, the WordNet-3.1 gloss (sense-fixing), the 65-prime inventory + a
compositional-grammar note, and the candidates' bare `explication` JSON under shuffled letter
labels. Hidden: generator identity, gloss/pattern/notes/self-flags, strategy labels, and any
mention of vendors or the adjudication. Letter order is a per-concept seeded shuffle
(sha256(seed‖slug‖record-sha) sort key; seed recorded in `candidates.json`); the letter→record
mapping lives only in `judge-key.json`, which is never shown to a judge.

**Judges (coordinator-run; the builder never invokes these).**
- Judge A = **gpt-5.6-sol** (codex exec, xhigh, read-only isolated home — the pinned pattern).
- Judge B = **claude-opus-4-8** (`claude -p` headless — the pinned pattern).
- Tie-break T = **gpt-5.6-terra**, invoked ONLY on candidates where A and B disagree on the
  FAITHFUL/LOSSY verdict; final verdict = majority of {A,B,T}.
Cross-vendor by construction (mirrors the split-concept adjudication panel, which measured
96% A/B agreement). Quality score = mean over A and B (T excluded from quality; STIPULATED).

**Per-candidate outputs** (rubric in `judge_prompt.md`): verdict FAITHFUL|LOSSY (does the
explication render THIS sense's genus AND criterial differentia using only the 65 primes,
neither dropping criterial meaning nor asserting wrong meaning), `missing` (the dropped/wrong
differentia component(s), or ""), `quality` 0–3 (0 wrong/garbled or fits many sibling
concepts; 1 right genus but generic skeleton; 2 sound — genus + most criterial differentia,
minor looseness; 3 excellent — criterial differentia sharp and economical), one-line reason.

**Self-judging caveat (disclosed).** Every available model authored some consensus-era
candidate, so any judge choice grades some own-model output; mitigations: full blinding,
cross-vendor pairing, majority tie-break, and no judge authored any NEW (S3/S4) output.
Batched per-concept judging (one call per concept per judge, candidates shuffled in-context)
is STIPULATED for cost and within-concept score consistency; the known risk is in-context
anchoring across candidates, accepted for exploratory R&D.

## 6. Metrics

Primary: **judged-faithful rate per strategy** over the 24 concepts (verdict rule above),
overall and per stratum. Secondary: mean quality per strategy; marginal lift over S0 (per
stratum — the pipeline's case rests on SPLIT + unanimous-lossy lift); S2-vs-S4 (does merge
beat select-only ceiling?); self-flag↔judged-verdict confusion for Luna and fable5 (calibration
of the flags the cascade relies on); mechanical-gate pass rate of new S3/S4 records;
cost per net faithful AST per strategy. No hypothesis test is pre-registered; report counts
and honest uncertainty (n=24 ⇒ ±~10pp swings are noise; say so in the readout).

## 7. Honest cost model

Basis (measured from consensus-100 reports): Claude gens report `total_cost_usd` median
$0.034 / mean $0.073; codex gens report tokens only (subscription quota, ~19k in / ~2.4k out,
median 48 s; nominal ~$0.004–0.01/call if priced at API rates — the maintainer's "~$0.004"
figure). Judge calls carry 5–8 explication JSONs (~8–20k extra input tokens): estimate
2–4× a gen call.

| item | calls | quota | est. $ |
|---|---|---|---|
| S3 forcing-retry (luna) | 18 | codex | ~$0.10–0.20 nominal (quota-only in practice) |
| S4 merge (luna) | 11 | codex | ~$0.06–0.15 nominal |
| Judge A (sol) | 24 | codex | ~$0.25–0.75 nominal |
| Judge B (opus48) | 24 | Claude subscription | ~$1.50–4.00 reported cost_usd |
| Tie-break T (terra) | ≤24 (expect ~5–10) | codex | ~$0.10–0.30 nominal |
| **Total full run** | **~82–101 calls** | | **≈ $2–5.5** (of which only the opus judging draws Claude quota) |

Wall-clock, sequential: generation ~30–50 min; judging ~1.5–3 h. Everything is resumable
per-file, safe on this box's 2 shared cores (no compute-heavy load; these are API waits).

## 8. Files & commands

```
poc/scale/ast-pipeline/
  DESIGN.md               this file
  sample.json             the 24-concept stratified sample (regenerable)
  run_pipeline.py         resumable driver: sample|gen|prep|judge|score|dryrun
  forcing-addendum.md     S3 §6 addendum (composed → forcing-prompt.md at gen time)
  merge-addendum.md       S4 §6 addendum (+ per-concept candidates → merge-prompts/<slug>.md)
  judge_prompt.md         blind judge system prompt + rubric
  gen-s3/ gen-s4/         new records + reports + provenance (define_concept.py format)
  candidates.json  judge-key.json  strategies.json   (after `prep`)
  judge-inputs/<slug>.txt (blind judge user messages)
  judgments/<A|B|T>/<slug>.json   (coordinator-run)
  results.json results.md         (after `score`)
  dryrun/                 2-concept dry run (non-sample concepts), incl. DRYRUN.md
```

Builder runs: `sample`, `dryrun` only. Coordinator runs: `gen` → `prep` → `judge --judge A` →
`judge --judge B` → `judge --judge T` → `score`.

## 9. Limitations (read before trusting results)

n=24 is a pilot, not an estimate to cite beyond ±10pp; batched judging can anchor; judges are
LLMs sharing training biases with generators (human spot-check of a few verdicts recommended);
S2's "ceiling" is judge-defined, so S2 and the metric share an oracle (that is why S2 is
labelled a ceiling, not a deployable strategy — deployable S2 would need a judge-in-the-loop
cost entry, ~1 judge call per concept, which the cost table's judging rows already bound);
the forcing prompt was written with knowledge that renderability is usually possible
(adjudication aggregate), a deliberate, disclosed design input — but no per-concept verdicts
leaked into it.
