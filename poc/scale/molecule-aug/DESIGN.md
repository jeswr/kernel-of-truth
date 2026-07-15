# Molecule-augmented generation (S5) — reference-lexicon AST generation vs the flat 65-prime baseline

> **⚠ SUPERSEDED IN PART BY `DESIGN-v2.md` (2026-07-15).** Following the GPT-5.6-sol
> readiness review (`docs/next/analysis/s5-readiness-review.md`, verdict
> NOT-YET-confirmatory), §§2, 6, 7, 8 of this file (arms, judging, endpoint/stats,
> run plan) are replaced by DESIGN-v2: matched flat-ensemble-vs-molecule-ensemble
> E2 primary at n=200 fresh, single-candidate expanded-rendering proxy judging,
> full bridge adjudication, prospective freeze. Stage 2 below will NOT run as
> designed. §§3–5 and 9 (lexicon, prompt/gate mechanics, ALGORITHM_VERSION
> analysis) remain the design of record.

**Status: DESIGN ONLY — exploratory methodology R&D.** No prereg-freeze, no registry
write, no git commit, no full run, no GPU. Every design choice below is
**STIPULATED-not-MEASURED** unless it cites a measured artefact by path. Author:
fable (lead designer). Builder–judge separation as in `poc/scale/ast-pipeline/DESIGN.md`:
this directory's author runs nothing beyond mechanical smoke tests; the coordinator
owns all generation sweeps and ALL judging.

---

## 1. Problem and the finding that motivates this

The concept-def pipeline (`poc/scale/concept-def-agent/`) forces flat decomposition
into ONLY the 65 NSM primes: `concept-def-prompt.md` §3.4 declares the primes "the
ONLY vocabulary … no way to add any", §2 mandates `references: []`, and
`define_concept.py check_record` hard-fails any record with `references != []`.
Measured cost of that policy (`poc/scale/consensus-100/ast-lossy-by-model.md`):
self-flagged AST-lossy rates of ~90% for the GPT family (sol 89 / luna 91 / terra 91)
and ~65–69% for the Claude family over the same 100 concepts. The blind cross-vendor
adjudication (`consensus-100/split-concept-adjudication.md`) put the flat renderable
ceiling at **≈51/100 concepts**; the remaining ~49 are the genuinely molecule-gated
tail (all six generators agree they are lossy in bare primes).

But the prohibition is **generation policy, not schema**, and the repo already owns
the missing layer:

- `encoder/src/ast.ts` has first-class `ConceptRef` / `ConceptHead` nodes;
  `encoder/src/validate.ts` accepts them (only a non-empty id is checked at the
  grammar gate); `encoder/src/encoder.ts encodeConceptSet` resolves a reference DAG
  memoised, failing closed on unresolved ids (`ERR_CONCEPT_UNRESOLVED`) and cycles
  (`ERR_CYCLIC_CONCEPT_REF`). The only reason references die in today's gate is one
  line: `validate-record.mjs` encodes each record in a **single-entry map**.
- `data/kernel-v0/` holds 54 gate-green `kot-ast/1` explications, **18 of them
  reference-bearing** (manifest `referenceBearingCount: 18`; e.g. teacher→learn,
  repair→broken→break, condolence→grieving→death→event at depth 3), pinned to the
  current encoder content hash. These are referenceable **today**.
- `data/molecules-v0/` holds 54 `kot-molecule/0` prose grounding records, and
  `docs/design-molecule-tier.md` **measured** that those 54 molecules lift the
  profile-1 expressibility ceiling from **58.2% → 87.6%** of TinyStories top-500
  content mass — direct evidence that a small mid-level lexicon removes most of the
  molecule gate, on that (favourable) distribution.

**Mechanically verified during this design** (smoke test, this session — see §5.2):
`encodeConceptSet` over all 54 kernel-v0 explications plus one NEW record referencing
`urn:kernel-v0:teacher` validates and encodes to a unit-norm D=8192 vector on the
**current encoder, zero code changes, no ALGORITHM_VERSION bump**.

**Hypothesis (exploratory, not preregistered).** Letting the generator compose from a
curated referenceable concept lexicon (65 primes + kernel-v0 + a bridge tier of
formally explicated molecule words) reduces AST-lossiness: judge-confirmed FAITHFUL
yield rises and self-flagged lossy rate falls, on the same concepts, under the same
blind judges, relative to the flat baseline.

## 2. The experiment in one paragraph

Same concept sample, same blind cross-vendor judge harness as
`poc/scale/ast-pipeline/` (this is strategy **S5** plugged into that pipeline's
candidate/prep/judge/score machinery), two generation arms per concept: **flat**
(the existing consensus-100 records, references forbidden — zero new calls) vs
**reference-augmented** (one new call per generator with the base prompt + the S5
`ref-addendum.md` + the referenceable-lexicon listing; records may cite lexicon ids;
the S5 variant gate `validate-record-ref.mjs` resolves references against the
lexicon before accepting). Primary endpoint: paired per-concept delta in
judge-confirmed FAITHFUL rate (S5 arm vs same-generator flat arm), McNemar exact
test; secondary: self-flag lossy-rate delta, quality-score delta, reference-usage
stats, gate pass rate, cost per net faithful AST. Two stages: a 24-concept pilot
riding the existing ast-pipeline sample, then (if the pilot lifts ≥ the STIPULATED
go threshold) a 100-concept in-sample run **plus a 30-concept held-out fresh sample**
that controls for the fact that the lexicon was mined from consensus-100's own lossy
notes.

## 3. The referenceable lexicon (85 ids: 54 reused + 31 authored)

### 3.1 Evidence base for the word list (MEASURED, this design session)

We mined all 599 consensus-100 generation records (`consensus-100/gen/*.json`,
one of 600 missing on disk): **470 lossy notes** vs 129 faithful. Mining script
committed alongside as `mine_lossy.py` (stopword/meta-word filtered, word-boundary
anchored, false positives audited). Findings that size the lexicon:

- Lossiness is concept-driven: 79/100 concepts are lossy in ≥4 of 6 models.
- The dominant nameable gap is socio-economic: law/legal/rule (66 notes),
  institution/social-role (65), money/payment (59), possession/transfer (50),
  war/violence/force (46), material/substance (39), profession/work (34),
  measurement (29) — plus heat/energy (25), food (22), animal/biology (40).
- Top single words: money 32, movement 24, authority 24, legal 22, force 22,
  institutional 21, contact 18, substance 17, material 17 …
- Greedy set-cover: the top-40 covering words address **327/470 = 70%** of all
  lossy notes; the curve flattens hard after ~30 words (marginal gain ≤3 notes),
  which is why the bridge tier below stops at 31.

### 3.2 Composition

**Tier A-0 (reuse, zero authoring): the 54 `data/kernel-v0/` records AS-IS.**
They already cover chunks of the mined buckets: possession/transfer (give, take,
find, lose, gift, thief), death/biology (death, birth, alive, dead), social acts
(help, teach→learn, promise, lie, friend), artefact-making (make, break, repair,
maker-of), mereology/space (part-of, has-part, inside, near).

**Tier A-1 (authored for this experiment): 31 bridge concepts**, selected by the
greedy cover subject to the mint-only-what-explication-cannot-reach discipline of
`docs/design-molecule-tier.md` §1.2 (words like *pay*, *buy*, *refund*, *medicine*
are deliberately NOT minted — they become explicable once *money*/*ill* exist,
which is the direction the programme wants pressure to flow). List, in topological
authoring order, with the lossy-notes coverage each buys and the molecules-v0
grounding-note seed where one exists (18 of 31):

| # | bridge concept | seeds from molecules-v0 | may reference | ≈lossy notes |
|---|---|---|---|---|
| 1 | money | money | give, take (kernel-v0) | 39 |
| 2 | surface | — | — | 14 |
| 3 | hot (heat) | fire | — | 24 |
| 4 | material (what a thing is made of) | water/rock/wood-adjacent | make | 17+ |
| 5 | group (organized people) | — | — | 19 |
| 6 | fight | — | — | 15 |
| 7 | measure (determined how-much) | — | — | 14 |
| 8 | kill | — | death | 11 |
| 9 | animal | animal | — | 9 |
| 10 | eat | eat | — | 6 |
| 11 | food | food | eat | 3 (15 raw) |
| 12 | grow | — | — | 3 (10 raw) |
| 13 | name (the word for X) | — | — | 4 |
| 14 | write | book | — | ~2 (20 raw bucket) |
| 15 | own (property) | — | take | 5 (28 raw) |
| 16 | ill (sick) | — | — | 3 (13 raw) |
| 17 | man (adult male) | man | — | — |
| 18 | woman (adult female) | woman | — | — |
| 19 | sex (mating) | — | man, woman | 8 |
| 20 | work (job) | — | money | 3 (16 raw) |
| 21 | status (social standing) | — | group | 32 |
| 22 | authority (over people) | — | group | 3 (30 raw) |
| 23 | law | — | authority | 21 |
| 24 | country | — | authority | 2 (10 raw) |
| 25 | institution | — | group, law | 7 |
| 26 | duty | — | work | 5 |
| 27 | worth (value) | money | money, give | 7 (23 raw) |
| 28 | tool | — | make | ~4 (11 raw) |
| 29 | machine | car | tool, make | 7 |
| 30 | art | picture | make | 10 |
| 31 | game | ball | — | 5 |

Estimated union coverage of the 31 + kernel-v0 54: **≈300/470 ≈ 64% of lossy
notes** (sum of greedy marginals for the selected words; STIPULATED estimate —
exact union recomputable with `mine_lossy.py`).

("≈lossy notes" = greedy-cover marginal; "(raw)" = total notes mentioning the word.
Man/woman carry no direct notes but are structurally required by *sex*, mirroring
molecules-v0's woman-for-mother rule.)

### 3.3 Record form, ids, and the authoring bar

Bridge records are **formal `kot-ast/1` explications in the kernel-v0 record shape**
(id, label, status, pattern, gloss, notes, references, explication) under a fresh
namespace `urn:molaug-v0:<slug>`, stored in `poc/scale/molecule-aug/lexicon/records/`.
They may reference kernel-v0 ids and EARLIER bridge ids only (topological order
above; acyclicity by construction, and `encodeConceptSet` fails closed on cycles
anyway). Authoring bar (all STIPULATED):

1. Authored by the explicator agent through the encoder/validator loop; every
   record must pass `validate-record-ref.mjs` (grammar + reference resolution +
   encode, fail-closed) before entering the lexicon.
2. Scholarly-definition standard for `gloss` (genus–differentia, no circularity,
   sense-fixed) — same §1 bar as `concept-def-prompt.md`.
3. Where a molecules-v0 grounding note exists, it SEEDS the content (the prose is
   a recognition anchor to formalize), but the bridge record never quotes or
   embeds the prose — it is a fresh formal explication.
4. **Honesty clause carried over from `docs/design-molecule-tier.md` §3:** several
   of these words (money, law, animal, material …) are exactly the words NSM
   scholarship treats as molecules because primes-only explication of them is
   itself approximate. Bridge records therefore carry the standard
   `notes: "AST adequacy: …"` self-flag, and a lossy bridge explication is
   ACCEPTED into the lexicon: the design claim is not that *money* is now
   perfectly explicated, but that its residual loss is **factored into one
   audited record** instead of being re-improvised (and re-lost) inside every
   downstream definition. This is admission-as-endorsement, not proof.
5. Human-maintainer spot-check of ≥5 of the 31 before any generation run
   (STIPULATED; cheap, and the lexicon is the experiment's main artefact).
6. `lexicon/manifest.json` pins: record list, per-record sha256, the sha256 of the
   sorted (id, record-hash) list as `lexiconSetHash`, and the encoder content hash.
   Every S5 generation report embeds `lexiconSetHash` — a record's canonical
   vector now depends on the referenced concepts' vectors, so provenance must pin
   the lexicon snapshot, not just the record.

### 3.4 Anti-leakage / anti-circularity gates

- **No eval-concept in the lexicon:** no bridge id's slug or synset may collide
  with any of the 100 consensus-100 concepts (or the 30 fresh held-out concepts,
  checked at selection time). Mechanical check in the lexicon build script.
  (Verified for the 31 above vs `concepts-100.json` slugs: no collision.)
- **In-sample fitting disclosed:** the word list is mined from consensus-100's own
  lossy notes, i.e. fitted to the evaluation sample's failure modes. The Stage-2
  **held-out fresh sample** (30 concepts drawn by deterministic stride from
  `poc/scale/f1k-eligibility/candidate-pool.json` URN order, excluding the 100 and
  excluding lexicon collisions) exists precisely to measure the generalization
  delta; the in-sample delta alone would be optimistic.
- **No benchmark/gold leakage:** mining reads generation-side self-notes only —
  never judge verdicts, never adjudication verdicts, never any eval item.
- **No self-reference:** a generated record may not reference its own id
  (`ERR_SELF_REF` in the variant gate); near-synonym genus references (e.g.
  *instructor* as a kind of `urn:kernel-v0:teacher`) are legitimate composition
  and are judged on whether differentia is added (§6).

## 4. The generation-prompt change (S5 arm)

The frozen `concept-def-prompt.md` is **not modified**. The S5 system prompt is
composed at gen time (same pattern as ast-pipeline's `compose_forcing_prompt`):

```
concept-def-prompt.md  +  ref-addendum.md  +  <generated LEXICON LISTING>
```

`ref-addendum.md` (written, in this directory) overrides exactly two base rules:
§3.4's "only vocabulary" becomes "65 primes + the listed lexicon ids", and §2's
`references: []` becomes "list exactly the distinct ids the AST mentions, sorted".
It adds the reference syntax (the two already-legal `ConceptRef` forms), a
≤8-distinct-references cap, a decompose-first discipline ("a reference you could
have decomposed is a fault"), and re-anchors the lossy escape hatch: `lossy` is now
declared only for content neither primes nor listed concepts can carry. The LEXICON
LISTING block is generated mechanically from the lexicon records — one line per id:
`urn:… — <label>: <first-sentence gloss>` (85 lines, ≈2k tokens; explications are
NOT shown to the generator — glosses only, keeping the prompt small and preventing
explication-style anchoring).

## 5. The validator change (S5 gate)

### 5.1 What stays

Everything in `define_concept.py` except two checks: the runner, strict-JSON
extraction, attempt/provenance/report format, identity tripwires, STOPCAP are
reused verbatim (S5 driver invokes `define_concept.py --prompt <composed-s5-prompt>`
and post-gates with the variant validator; alternatively a 6-line patch generalizes
`check_record`/`run_gate` — specced below — but the no-patch route keeps the pinned
file untouched and is the default).

### 5.2 The precise changes (implemented as `validate-record-ref.mjs`, this directory; smoke-tested green)

- **R1 — resolve, don't isolate.** Replace the pinned gate's
  `encodeConceptSet(new Map([[doc.id, doc.explication]]))` with an encode map
  pre-loaded with ALL lexicon explications (kernel-v0 54 + bridge 31) plus the
  candidate. `encodeConceptSet` then resolves the DAG; unresolved/cyclic refs still
  fail closed. *(Smoke-tested: ref-bearing record → ok, D=8192, norm=1.0,
  lexiconSize=54; same record under the pinned gate → `ERR_CONCEPT_UNRESOLVED`,
  reproducing the diagnosed gap.)*
- **R2 — references-policy moves out of check_record.** `references` must equal
  exactly the sorted set of concept ids mentioned in the AST
  (`ERR_REF_MISMATCH`), every id must be in the lexicon
  (`ERR_REF_NOT_IN_LEXICON`), no self-reference (`ERR_SELF_REF`).
- **R3 — flat records still pass.** A record with `references: []` and no
  `ConceptRef` nodes gates identically to the pinned path (superset behaviour),
  so one gate serves both arms in S5 tooling.
- **R4 — reference cap ≤8 distinct ids** (`ERR_REF_CAP`; STIPULATED: keeps records
  explications rather than bag-of-concept tag lists; expected usage 0–3).

If the maintainer later prefers patching the pinned path instead: in
`define_concept.py check_record`, replace the `references must be []` error with
the R2 equality check behind a `--lexicon` flag (default off ⇒ behaviour
unchanged), and in `run_gate` pass the flag through to the .mjs. NOT done here.

**Explicitly out of scope (no encoder change):** `encoder/` is untouched; the
encoder content hash and ALGORITHM_VERSION are unchanged (see §9); the decoder is
not exercised (the endpoint is judge-based, not vector-round-trip — decode
recovery of ConceptRef-bearing vectors against an 85-id lexicon is a follow-up,
Phase-X2-shaped question).

## 6. Judging — riding the ast-pipeline blind harness

S5 slots into `run_pipeline.py`'s stages: its records join the per-concept
candidate pool at `prep` (deduplicated, seeded letter shuffle, judge-key held
back), are judged by the same panel (A = gpt-5.6-sol, B = claude-opus-4-8,
T = gpt-5.6-terra on A/B disagreement, majority verdict), and are scored by the
same FAITHFUL/LOSSY + quality 0–3 rubric.

**One necessary instrument change, applied to ALL candidates in this experiment
(disclosed):** judges must know reference semantics, so `judge_prompt.md` gets a
composed S5 variant (`judge-addendum.md`, this directory) stating: a
`{"kind":"concept","id":…}` node imports the referenced concept's meaning; the
listing of referenced ids WITH THEIR GLOSSES is appended per concept (only ids
actually referenced by some candidate, to bound input size); a candidate that
merely wraps the headword in a near-synonym reference without differentia is
LOSSY (genus-by-reference plus rendered differentia is FAITHFUL); references do
not exempt a candidate from the no-generic-skeleton rule. Because flat and S5
candidates are judged in the SAME pool under the SAME variant prompt, the
instrument is constant across arms; but S5 results are therefore not directly
comparable to any earlier ast-pipeline run judged under the base prompt — rerun
flat candidates under the variant prompt rather than importing old verdicts.

**Blinding limits (disclosed):** judges remain blind to generator identity,
self-flags, and strategy labels, but a reference-bearing candidate is trivially
recognizable as the augmented arm. This is inherent to the manipulation. The
cross-vendor panel + majority rule is the mitigation; a judge biased for or
against references shows up as A/B disagreement, which is measured and reported.

## 7. Samples, arms, endpoint, stats

### 7.1 Stage 1 — pilot (rides the existing 24-concept ast-pipeline sample)

- Concepts: `ast-pipeline/sample.json` (4 unanimous-faithful / 12 SPLIT /
  8 unanimous-lossy; deterministic, adjudication-blind selection — reused as-is).
- Arms per concept: flat = existing consensus-100 records of gpt-5.6-luna and
  claude-fable-5 (0 new calls); S5 = ONE new call each for gpt-5.6-luna and
  claude-fable-5 with the composed S5 prompt (48 new gen calls). Both families are
  kept because the flat lossy rates differ 3× and the augmentation lift may too.
- Judged pool per concept: the ast-pipeline pool + 2 S5 records (if the
  coordinator runs this together with the S0–S4 campaign, judging is one merged
  run; S5 defines two scored strategies, S5-luna and S5-fable).

### 7.2 Stage 2 — main (GO iff pilot delta ≥ +15pp judged-FAITHFUL on either generator; STIPULATED)

- In-sample: all 100 consensus-100 concepts, flat (existing records) vs S5
  (1 new call per generator per concept: 200 calls).
- Held-out: 30 fresh concepts (deterministic stride over candidate-pool URN order,
  excluding the 100 and lexicon collisions), BOTH arms generated fresh (flat with
  the pinned prompt, S5 with the composed prompt: 120 calls) — the generalization
  estimate, immune to lexicon-fitted-to-sample bias.
- Judged pool per concept: 2 flat + 2 S5 records (4 candidates).

### 7.3 Endpoint and honest stats

- **Primary:** per generator, paired per-concept judge-confirmed FAITHFUL delta
  (S5 vs flat), exact McNemar test on discordant pairs; report point delta with
  95% CI (Wilson on the discordant-pair proportion). n=100 resolves ~14pp
  discordance at conventional levels; n=24 pilot is directional only (±10pp
  noise, stated in the readout as in ast-pipeline §6).
- **Secondary:** self-flag lossy-rate delta (and self-flag↔verdict calibration
  under augmentation); mean quality delta; per-stratum deltas (the case rests on
  the unanimous-lossy stratum); reference-usage distribution (refs/record, which
  ids, share of records using 0 refs — if S5 barely references, the null result
  is about generation policy, not the lexicon); gate pass rate incl.
  `ERR_REF_*` codes; held-out vs in-sample delta gap; cost per net faithful AST.
- **No hypothesis is preregistered** (mandate: no freeze). The GO threshold above
  and the interpretation rule below are STIPULATED in advance to bound
  post-hoc-ness, not to claim confirmatory status.
- **Interpretation rule (STIPULATED):** if the in-sample judged-FAITHFUL lift is
  <+10pp on both generators, molecule augmentation is not worth the lexicon
  maintenance and the FULL tier (§9) should be deprioritized; if the held-out
  lift is <half the in-sample lift, report the lexicon as overfitted to
  consensus-100 and size a frequency-based (not failure-mined) lexicon before
  scaling.

### 7.4 Predicted effect (reasoned, STIPULATED — recorded before any run)

Chain of reasoning from measured anchors: (i) flat renderable ceiling ≈51/100
(split-concept adjudication); (ii) 54 molecules lifted TinyStories expressibility
58.2%→87.6% of content mass (design-molecule-tier.md) — but consensus-100 is
WordNet-stride-sampled, abstract/socio-economic-heavy, harsher than TinyStories,
and our lexicon covers ≈64% of its mined lossy notes, so expect a ceiling lift to
roughly **75–85/100**, not 87%; (iii) realized yield trails ceilings: Claude flat
realizes ~33 of the 51-ceiling (~65%), GPT ~10 (~20%). Applying those realization
rates to a ~78 ceiling predicts judged-FAITHFUL of roughly **50–60/100 for
claude-fable-5 (from ~33) and 25–40/100 for gpt-5.6-luna (from ~10)**, i.e.
self-flag lossy dropping ~65%→~40–50% (Claude) and ~90%→~55–70% (GPT). Held-out
lift predicted at 60–80% of in-sample lift. These are honest guesses to be scored
against, not claims.

## 8. Cost + run plan (all cheap text API / subscription quota; no GPU)

Cost basis measured in `ast-pipeline/DESIGN.md` §7: Claude gen median $0.034
(mean $0.073) reported `total_cost_usd`; codex calls are subscription quota
(~$0.004–0.01 nominal); judge calls 2–4× a gen call, and grow with pool size
(+2 candidates ⇒ upper band).

| item | calls | quota | est. $ |
|---|---|---|---|
| Lexicon: author 31 bridge records (explicator agent, validator loop) | ~31 agent sessions | Claude subscription | ~$2–8 reported |
| Stage 1 gen: S5 luna 24 + S5 fable5 24 | 48 | codex + Claude | ~$0.2 + ~$1–2 |
| Stage 1 judging marginal (pool +2, riding the S0–S4 run) | 0 extra calls | — | ~$1–2 upper-band growth |
| Stage 2 gen: 100×2 S5 + 30×4 fresh | 320 | codex + Claude | ~$0.7 + ~$6–12 |
| Stage 2 judging: 130 concepts × judges A+B (+~25% T) | ~290 | codex + Claude | ~$12–25 (opus side dominates) |
| **Total, both stages** | **~690** | | **≈ $25–50** |

Wall-clock: lexicon ~1–2 days of agent authoring + spot-check; Stage 1 ~1 day
(gen ~1 h, judging rides the pending ast-pipeline run); Stage 2 ~2–3 days
elapsed, all resumable per-file, API-wait-bound (safe on this box's 2 shared
cores; `nice -n 10` throughout).

**What the coordinator runs** (builder runs nothing beyond a 2-concept dry run):

```bash
cd poc/scale/molecule-aug
# 0. after lexicon records land + maintainer spot-check:
node lexicon/build_manifest.mjs            # pins lexiconSetHash; checks eval-concept collisions
python3 run_s5.py compose                  # base prompt + ref-addendum + lexicon listing
python3 run_s5.py dryrun                   # 2 non-sample concepts, incl. one Claude-path check
# Stage 1 (with/after the ast-pipeline S0–S4 campaign):
nice -n 10 python3 run_s5.py gen --stage 1        # 48 calls via define_concept.py --prompt
python3 run_s5.py prep --stage 1                  # merge into ast-pipeline candidates/prep
nice -n 10 python3 ../ast-pipeline/run_pipeline.py judge --judge A --i-am-the-coordinator
nice -n 10 python3 ../ast-pipeline/run_pipeline.py judge --judge B --i-am-the-coordinator
nice -n 10 python3 ../ast-pipeline/run_pipeline.py judge --judge T --i-am-the-coordinator
python3 run_s5.py score --stage 1                 # paired stats + GO/NO-GO readout
# Stage 2 iff GO: same verbs with --stage 2 (adds the 30-concept held-out sample)
```

`run_s5.py` is TO BUILD (~300 lines: compose/dryrun/gen/prep/score, reusing
`define_concept.py` as a subprocess and `run_pipeline.py`'s prep/judge formats).
Deliverables already in this directory: `DESIGN.md` (this file), `ref-addendum.md`,
`judge-addendum.md`, `validate-record-ref.mjs` (smoke-tested), `mine_lossy.py`
(evidence reproduction), `lexicon/PLAN.md` (word list + authoring order + seeds).

## 9. The ALGORITHM_VERSION question — cheap tier vs full tier

**CHEAP tier (this experiment; no bump, verified).** Referencing *formal kot-ast/1
explications* is inside the current encoder contract: `ConceptRef` resolution via
`encodeConceptSet` is existing, tested encoder behaviour; kernel-v0's 18
reference-bearing records are already pinned green under the current
`encoderContentHash` (`data/kernel-v0/manifest.json`). The content hash pins
{schema, algorithm, D, codebook, weighting} — the *algorithm* is unchanged; the
lexicon is data supplied to it. Provenance handles data-side identity: every S5
artefact records `lexiconSetHash` (§3.3.6).

**FULL tier (extension; NOT designed to run, NOT implemented).** Referencing
`data/molecules-v0/` **prose** records as-is is a different animal: molecules have
no explication, hence no derivable vector, so the encoder would need the pinned
molecule-vector derivation specced in `docs/design-molecule-tier.md` §4.2 (e.g. a
codebook-style seeded row over SHA-256 of the NFC grounding-note bytes). That
changes the content-hash inputs ⇒ **ALGORITHM_VERSION bump, X0 golden
regeneration, Phase-X re-run** — a semi-permanent re-pin of the whole encoder
line. Design position: the cheap tier deliberately converts the highest-value 31
molecule words into formal explications instead, so the experiment runs today;
the full tier becomes worth pricing only if (a) the cheap tier shows a real lift
AND (b) lexicon scaling toward Goddard's ~180+ productive molecules makes
per-word formal explication the binding cost. **Maintainer sign-off required
before any FULL-tier work** (the bump is the expensive, semi-permanent part).

## 10. Limitations (read before trusting any result)

1. In-sample lexicon fitting (mitigated by the held-out sample; §3.4).
2. Judge instrument changes with the manipulation (reference-aware prompt;
   §6) — flat arms are re-judged under it, but cross-experiment comparison to
   prior ast-pipeline numbers is not valid.
3. Reference-visibility breaks arm-blindness at the judge (inherent; §6).
4. Bridge explications are themselves unproven (admission-as-endorsement;
   §3.3.4) — a FAITHFUL verdict on a referencing record is conditional on the
   referenced record meaning what its gloss says. Loss can hide inside the
   lexicon. Report is honest only with this stated.
5. Self-flag semantics shift between arms (the lossy bar moves with the
   vocabulary), so self-flag deltas are descriptive, not the endpoint.
6. LLM judges share training bias with generators; human spot-check of ~10
   verdicts per stage recommended (as in ast-pipeline §9).
7. Vector-side consequences (decoder recovery, similarity structure of
   reference-bearing vectors at D=8192, JL projection behaviour) are untested
   here — judge-based endpoint only; Phase-X2/X4-shaped follow-ups if adopted.
