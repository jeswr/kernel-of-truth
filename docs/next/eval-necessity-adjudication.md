# Eval-necessity adjudication — custom evals vs. standard benchmarks (nsk1, truthstyle-2x2, f2b-errors)

> **Status: RECOMMENDATION for maintainer sign-off. Nothing is redesigned, amended, or
> frozen by this document.** Author: Fable, experiment-designer role
> (`kern/fable-designer`), 2026-07-10. Design-vs-judge protocol: GPT-5.6 ADVISES (its
> salvaged interim synthesis is `poc/gpt56-review/eval-necessity-review.raw.md` line 323
> — the full structured answer was lost to a stderr truncation; `.err` is byte-identical),
> the DESIGNER DECIDES. This document is that decision.
>
> Inputs read at source: `docs/design-neurosym-kernel-internals.md`,
> `docs/design-truthstyle-2x2-f2-taxonomy.md`, `registry/experiments/{nsk1,
> truthstyle-2x2, f2b-errors}.json`, `docs/next/feasibility-synthesis.md`,
> `registry/assumptions.jsonl` (ASM-0023..0025), plus source-verification of the three
> candidate benchmarks (§5). Not touched, per tasking: the nl-boundary files, the
> f2b-transfer files, `poc/gpt56-review/*`, and all three DRAFT records.
>
> **Adoption note (2026-07-10, post-recommendation).** The maintainer adopted §2, and
> the nsk1 pivot is now EXECUTED: `registry/experiments/nsk1.json` (still DRAFT — lawful
> to edit) and `docs/design-neurosym-kernel-internals.md` carry the CLUTRR covered slice
> as the PRIMARY eval, the custom `nsk1-eval` demoted to calibration + a named secondary
> stratum, the runner build recipe (design doc §5.1) and the pre-freeze gates + fallback
> ladder (§5.2). ASM-0027 records the CLUTRR stipulation and supersedes ASM-0023
> (register updated, append-only last-line-wins); the §1 adoption criterion is
> registered as ASM-0028; the §3 and §4 verdicts as ASM-0029 / ASM-0030. The §3 LLMBar
> side-record and the §6 provenance-triple schema note remain recommendations awaiting
> their own execution.

---

## 0. The question and the three verdicts

The maintainer's question: the three newly-designed experiments build bespoke eval
material; given that the programme's KNOWN weakness is self-authored evals inflating
results, is each custom eval NECESSARY, or should an out-of-the-box benchmark replace or
supplement it?

PREMISE: across the entire frozen registry there are ZERO audited end-task wins over the kernel-as-text null, and the only positive end-task PASS is confined to a self-authored oracle-favourable slice [MEASURED: docs/next/feasibility-synthesis.md §0, backed by registry/assessments/oracle-coverage.json + registry/assessments/f2b-replicate.json].

PREMISE: the symmetric failure mode is real — the kernel's authored vocabulary is narrow (m0b coverage_fraction 0.3542 at molecules-v0, corpus-indexed on ONE pinned corpus and ONE incomplete kernel instance, transferring nowhere), so an open-domain benchmark that never touches the covered slice is a NULL INSTRUMENT, not a stronger one [MEASURED: registry/verdicts/m0b.json; ASM-0001/0002].

| Experiment | Verdict | One line |
|---|---|---|
| **nsk1** (flagship) | **SWAP → CLUTRR** (executed as a hybrid: CLUTRR primary + retained custom probe) | The primary eval surface moves to CLUTRR's public data — third-party items, gold labels, graph/proof provenance, and even third-party uncovered controls — with the custom `nsk1-eval` retained only as the calibration split and a named secondary stratum. Full plan §2. |
| **truthstyle-2x2** | **SUPPLEMENT with LLMBar** (custom stays primary and necessary; LLMBar as a separate judge-calibration side-record; do NOT delay the timing-critical freeze) | No external benchmark contains NSM-register definitions, and the estimand is a within-pair style contrast on the kernel's actual bytes — irreplaceable; LLMBar externally calibrates the judge pool's style-over-substance robustness. §3. |
| **f2b-errors** | **JUSTIFIABLY KEEP custom** (no swap, no supplement) | It has no eval items to swap; its only artifact is a closed cause taxonomy that is a pure function of THIS pipeline's logged fields. ProcessBench labels earliest-erroneous-step in math chains — it does not describe a verify-retry loop's mechanics, and importing its categories would mint undecidable labels. §4. |

The self-authoring risk is NOT uniform across the three, and the adjudication tracks the
provenance triple per experiment — who authored the ITEMS, the GOLD, and the
GRADER/VERIFIER — because the f2b lesson is specifically that two of those three sharing
provenance (gold defined by the grader's own accept test) inflates results
[MEASURED: registry/assessments/f2b-replicate.json does_not_license].

---

## 1. Where the confound actually binds (shared analysis)

Three distinct channels, in decreasing severity:

1. **First-order (the f2b class): gold coincides with the mechanism's accept test.**
   Already designed OUT of all three drafts — nsk1's gold is generator graph traversal
   with the engine seeing hop-1 only; truthstyle-2x2's endpoints never score gold
   agreement at all; f2b-errors consumes external-gold outcomes it did not author.
2. **Second-order: designer degrees of freedom over the item distribution.** The
   designer who knows the mechanism authored the corpus generator. In nsk1 this channel
   is REAL and identifiable: `nsk1-eval`'s invented unique surname-pairs and templated
   single-form fact sentences were chosen precisely to make the internal arm's
   patchscope-decode → exact-match read channel feasible. That is a mechanism-friendly
   authoring choice that differentially favours the internal arm — the arm contrast is
   within-item and symmetric in first order, but the read channel's difficulty is set by
   corpus authorship. A third-party corpus removes this channel entirely.
3. **Optics/credibility: even a clean PASS on self-authored data extends the
   documented pattern** ("a PASS confined to a self-authored slice") and cannot connect
   to any external reference point. For the FLAGSHIP specifically this channel matters
   most: it is the line the programme will be judged by.

DECISION: standard benchmarks are adopted exactly where they (a) actually exercise the covered slice and (b) preserve the experiment's estimand and provenance-independence structure; they are refused where they would be a null instrument or would rename the estimand. This is the maintainer's prior applied with the coverage caveat, and it lands differently on each of the three experiments [STIPULATED: ASM-0028].

---

## 2. nsk1 — SWAP the primary eval surface to CLUTRR (hybrid execution)

### 2.1 Verdict and rationale

DECISION: nsk1's primary eval moves to a covered slice of CLUTRR's public data (Sinha et al. 2019, arXiv:1908.06177); the custom nsk1-eval corpus is retained ONLY as (i) the calibration split for L*/α selection and (ii) a named secondary stratum. This supersedes FK-NSK-3's option-(a) choice and ASM-0023, both of which are re-decided BEFORE freeze (the record is DRAFT; re-deciding a registered fork on maintainer challenge + external review is exactly what forks are for) [STIPULATED: ASM-0027].

Why the swap is right here and only here:

- **The task shapes are near-isomorphic.** nsk1-eval is a synthetic-kinship-graph,
  k-hop relation-composition corpus with distractors and a closed lexicon — that IS
  CLUTRR's construction, eight years earlier, with published baselines. Building a
  private clone of an existing benchmark is the one configuration in which "custom" has
  the least defensible value.
- **CLUTRR preserves the two properties the custom corpus existed to guarantee.**
  (1) Gold-label independence: CLUTRR's `target`/`target_text` labels come from its own
  generator's composition rules — a third party — and the engine still resolves hop-1
  only, so the accept test and the scoring function remain disjoint AND gain
  third-party provenance on top. (2) Coverage: guaranteed by FILTER instead of by
  construction (§2.3) — the covered stratum is machine-checkable at build, same as now.
- **It upgrades the controls.** CLUTRR items whose derivation needs unminted relations
  (sibling/spouse/in-law/uncle chains) are natural, third-party UNCOVERED controls —
  currently the 100 uncovered controls are also self-authored.
- **It removes the second-order channel** (§1.2): item text, name distribution,
  distractor placement, question format, and gold all become bytes the programme cannot
  have tuned. The remaining programme-authored surfaces are exactly the mechanism
  (which is the thing under test) and the covered-slice filter (a committed, auditable
  pure function).
- **FK-NSK-3's original objection is discharged.** The fork rejected public benchmarks
  because they "import the unrun NL-parse boundary and sub-0.36 corpus-indexed
  coverage". Neither survives inspection for CLUTRR: the ENGINE never parses NL — its
  world store is derived mechanically from CLUTRR's structured `story_edges` +
  `genders` columns (§2.4), so the l3a-parse boundary is not imported; and coverage is
  restored by the slice filter. What IS imported is patchscope-extraction difficulty on
  natural-ish story text — a real risk, priced by a pre-freeze calibration blocker
  (§2.6), not a reason to keep a private clone.

What the hybrid retains and why: calibrating L* and α on the CUSTOM corpus and
evaluating on CLUTRR gives a strict tuning/eval provenance separation (zero analyst
contact between selection rules and the third-party surface); and the custom stratum
keeps the literature-matched entity-bridge task shape as a secondary, so an
extraction-driven INSTRUMENT-INVALID on CLUTRR cannot leave the family with zero
information for the GPU spent.

### 2.2 CLUTRR facts this plan rests on (source-verified 2026-07-10; §5 for tags)

- Licence: **CC-BY-NC-4.0** (repo LICENSE, facebookresearch/clutrr — authoritative; the
  HF mirror `CLUTRR/v1` lists "unknown" and is not the licence authority).
- Relation vocabulary (from `clutrr/store/relations_store.yaml`): 24 types — {son,
  daughter, father, mother, husband, wife, brother, sister, grandson, granddaughter,
  grandfather, grandmother, son/daughter/father/mother/brother/sister-in-law, nephew,
  niece, uncle, aunt, no-relation}.
- Released data fields (HF `CLUTRR/v1`): `story`, `query`, `target`, `target_text`,
  `clean_story`, `proof_state`, `f_comb`, `story_edges`, `edge_types`, `query_edge`,
  `genders`, `task_name`, `task_split` — i.e. the underlying kinship graph, the
  derivation, and the gold label ship WITH every item. ~70,631 rows across 6 configs
  (e.g. `gen_train23_test2to10`, `rob_train_clean_23_test_all_23`); story text is
  template/AMT-paraphrase generated.

### 2.3 Relation mapping — CLUTRR onto the kernel's covered concepts

Kernel concepts already minted (no new authoring for Phase A): `mother-of`,
`father-of`, `man`, `woman` — the same URNs `nsk1-eval`/axioms-v0 use.

- **Chain edges convertible with zero new minting:** `father`, `mother` edges map
  directly to father-of/mother-of records; `son`, `daughter` edges convert to the SAME
  two record types plus a man/woman class record (a "B is the son of A" edge is a
  parent edge A→B whose relation type is chosen by `genders[A]`, plus man(B)). All
  four basic edge types land in existing kot-world/1 vocabulary.
- **Covered stratum (Phase A, the primary):** k=2 items whose `f_comb` chain consists
  of UP-edges only ({mother, father}×{mother, father}) and whose `target_text` ∈
  {grandmother, grandfather}. Restricting to up-chains is a LICENSING requirement, not
  taste: hop-1 on an up-edge ("the mother of X") is axiom-licensed unique under the
  functional-parent axioms the engine already carries; hop-1 on a down-edge ("a son of
  X") is not functionally unique, so the engine would refuse — grandson/granddaughter
  targets are therefore EXCLUDED from Phase A rather than smuggled in with
  store-contingent uniqueness.
- **Third-party uncovered controls:** items whose chain contains any
  sibling/spouse/in-law/uncle/aunt/nephew/niece edge, plus parent-edge chains that
  compose to self/spouse/sibling targets. Correct loop behaviour = mapper abstain or
  engine refusal (feeds the existing false-fire gate ≤ 0.05).
- **Phase B (successor record, NOT nsk1):** mint native NSM explications for
  sibling-of/spouse-of to open the uncle/aunt/in-law slices. New authoring stays out of
  the flagship's first decisive run.
- **Build gates (mechanical, pre-freeze):** dedup by story-bytes hash across configs;
  covered-slice count n_covered ≥ 1,000 pooling k=2 rows across configs and
  `task_split` values (no training happens, so train rows are legitimate inference-only
  eval items; the official-test subset is additionally reported separately for
  literature comparability). If pooling yields 600 ≤ n < 1,000, power is recomputed at
  the achieved n before freeze; below 600 the fallback ladder (§2.6) fires.
  The slice count is a TO-MEASURE build fact — it is deliberately NOT estimated here.

### 2.4 What must be preserved (the GPT-5.6 condition, made concrete)

1. **Gold labels verbatim.** `target_text` is never recomputed, relabelled, or
   filtered-by-answer; scoring = exact match of the generated relation word against the
   closed 24-type vocabulary (X3-compatible closed lexicon — no cosine anywhere).
2. **Graph/proof provenance verbatim.** `story_edges`, `edge_types`, `genders`,
   `proof_state`, `f_comb`, `query_edge` are carried per-item into the derived-corpus
   manifest; the kot-world store is produced by a committed deterministic converter
   over `story_edges`+`genders` ONLY (the engine never sees or parses story text);
   `proof_state`/`f_comb` are used solely to compute the covered-slice filter and to
   identify the hop-1 edge — never shown to any model arm.
3. **Gold-label independence, unchanged in form.** The engine resolves the licensed
   hop-1 fact from the query entity and never the k-hop target; no arm's feedback ever
   contains the gold relation label.
4. **Item text verbatim.** `story` bytes as released (first run on the clean
   config, k=2; noise configs are successors). Question stem = CLUTRR's native "How is
   [A] related to [B]?" so the label space and difficulty stay comparable to published
   numbers.
5. **Everything else in the record stays structurally as designed:** the seven arms,
   budget matching (≤8-token side-decode vs ≤24-token feedback sentence), instrument
   gates, one absolute primary, TOST ±0.02, IUT across R1/R2, verdict logic.

### 2.5 The kernel-powered arm vs the matched baseline, on CLUTRR

- **internal:** hook at L\*; patchscope-decode → exact match against the item's closed
  name lexicon (built from CLUTRR's own `genders`/`story_edges` name set — third-party);
  engine licensed unique lookup of the matched entity's hop-1 up-edge in the converted
  world store → bridge-entity record → cached steering vector keyed by that record's
  exact identity, h ← h + α·v at L\*. Law 1 unchanged: the vectors are the model's own
  activations from carrier prompts; the kernel only picks which vector and when.
- **external-text (PRIMARY comparator):** the identical engine call; the same hop-1
  fact rendered as ONE sentence by the same deterministic renderer, phrased in CLUTRR's
  own fact-sentence surface grammar, appended adjacent to the question; regenerate;
  ≤24 extra tokens. Same ledger both arms.
- **text-only / kernel-as-text / shuffled / random-dir / noop-hook:** unchanged in
  role; kernel-as-text = the item's converted family records rendered as canonical text
  at matched budget with no engine resolution (Law-2 null on third-party items —
  strictly more meaningful than before).
- **Calibration:** L\*, α, and any few-shot exemplars for the base models are selected
  by the existing pre-declared mechanical rules ON THE CUSTOM CORPUS ONLY; CLUTRR items
  are never touched before the final campaign except by the 100-item headroom slice
  (§2.6), which is discarded from analysis.

### 2.6 New pre-freeze blockers, fallback ladder, and honest costs

**Freeze-blockers (mechanical, cheap):**
(i) build gates of §2.3; (ii) a 100-item CLUTRR calibration-slice headroom check per
rung — text-only accuracy ∈ [0.05, 0.85] AND external-text ≥ text-only + 2pp (the
existing skeptic-item-2 check, pointed at the new surface); ~$2–5 GPU, maintainer
sign-off required for even that spend.

**Pre-declared fallback ladder (decided by the blocker outcomes BEFORE freeze, never
after):** native CLUTRR relation task fails headroom → rung 2: entity-answer questions
("Who is the grandmother of X?") derived from CLUTRR's third-party graphs with
traversal gold (keeps third-party items/graph, re-admits programme-authored question
templates — disclosed) → rung 3: the current custom `nsk1-eval` primary, CLUTRR demoted
to a reported stratum. Whichever rung passes is what freezes; the frozen record names
the rung.

**What the swap costs (stated, not hidden):**
- *Headroom risk up.* SmolLM2-135M/360M on natural-ish stories with a relation-word
  answer may sit near floor — this is exactly what the blocker + ladder price.
  [STIPULATED planning concern; resolved by measurement pre-freeze.]
- *Harder read channel.* Ordinary first names are harder to patchscope-decode than
  invented unique surnames; extraction-failure gate (≤0.30) may bind. Honest framing:
  the custom corpus's easy lexicon was itself a mild oracle-favourable authoring choice
  — the difficulty is the honest one.
- *Contamination risk (new, benchmark-specific).* CLUTRR is public since 2019 and may
  be in SmolLM2 pretraining data. The primary is a within-item ARM contrast, so
  contamination is symmetric across arms in first order; its main effect is headroom
  compression (priced by the gate). A names-swapped scramble diagnostic is recommended
  as a reported-only memorization probe. [STIPULATED risk; symmetric by design.]
- *Weaker literature fit of the mechanism.* The back-patch/bridge-entity evidence
  (arXiv:2406.12775) is about entity retrieval; CLUTRR's native answer is a relation
  word, so the injected bridge-entity vector aids composition less directly. The
  retained custom stratum keeps the literature-matched shape [LIT-BACKED:
  arXiv:2406.12775 (2024), verified in reports/lit-structured-parsing-and-inner-symbolic.md].
- *Schedule:* corpus fetch/convert/pin + record amendment + calibration ≈ days of agent
  time and ~$5; the $60/14-GPU-h campaign budget is unchanged in order of magnitude.
- *Envelope rewrite:* the current envelope's "no public-benchmark claims" clause is
  replaced by an exact licence: "the CLUTRR covered slice (grandparent-target, up-chain
  k=2, named config), R1–R2, sign only". Leaderboard/SOTA language stays FORBIDDEN — an
  inference-only filtered subset is not the leaderboard task; published CLUTRR numbers
  are reported as context, never as a comparison claim.
- *ASM-0023 is superseded* by a successor assumption recording the CLUTRR choice and
  its own residuals (contamination, filter authorship); ASM-0024/0025 carry over
  unchanged. (Executed 2026-07-10: the successor is ASM-0027.)

### 2.7 CC-BY-NC-4.0 implications

- Research use, adaptation, and publication of RESULTS: permitted with attribution.
  The verdict/report cites Sinha et al. 2019 and the licence.
- The derived corpus (filtered items + converted world records embed CLUTRR text) is an
  adaptation → it may be committed to the repo (the persistence rule requires it) ONLY
  under CC-BY-NC-4.0 with attribution: `data/nsk1-clutrr/` carries a LICENSE notice +
  provenance manifest (source config, commit/release, per-item ids).
- **Quarantine rule (load-bearing for licence hygiene):** CLUTRR bytes are EVAL-side
  only. Nothing from CLUTRR may enter kernel concepts, explications, molecules, or
  axiom content — the kernel artifact itself stays licence-clean.
- NC constraint: no commercial product may ship this eval data. No conflict with the
  research programme; flagged as a standing constraint should any commercial eval
  packaging ever be contemplated.

---

## 3. truthstyle-2x2 — SUPPLEMENT with LLMBar; the custom 2×2 is necessary

DECISION: keep the custom d-ts 2x2 as the primary and only verdict-bearing instrument; add LLMBar as an EXTERNAL judge-calibration side-record; do not delay the timing-critical freeze for it [STIPULATED: ASM-0029].

Why no benchmark can replace it (GPT-5.6 concurs; adjudicated independently here):
- The estimand is a FACTORIAL style contrast — NSM-shaped vs plain register of the SAME
  content, crossed with truth — on the kernel's actual canonical gloss bytes, because
  the thing being protected is the f2b-line judges' endorsement of exactly those bytes.
  No public dataset contains NSM-register definitions, let alone content-matched
  two-register pairs of them; a swap would rename the estimand into a different
  experiment. The self-authoring worry is also structurally lower here: no endpoint
  scores agreement with kernel gold (the analysis never consults canonical-record
  equality; tier-1's gate gold is WordNet-external), so the f2b first-order channel is
  absent by construction.
- What a benchmark CAN do is calibrate the INSTRUMENT: LLMBar (Zeng et al.,
  arXiv:2310.07641; MIT; 419 instances: an instruction + two outputs, one faithful and
  one superficially appealing deviation, gold preference labels) measures precisely
  whether a judge is fooled by surface polish — the same failure family as
  H-FALSE-ACCEPT-INFLATION, on fully external ground with community-validated labels.

Recommended implementation (design sketch, for a separate ~Tier-0 record or a
pre-registered exploratory side-car — maintainer's choice):
- Run the pinned 3-judge pool (byte-identical invocation forms) on the LLMBar
  Adversarial set (or a seeded ~150-instance subsample if budget-bound); report
  per-judge adversarial accuracy as a judge-quality card cited alongside the probe's
  verdict. ~419×3 ≈ 1,257 invocations ≈ $10–20 (or ~$5 subsampled); zero GPU.
- Reported-only, never a gate on truthstyle-2x2: the formats differ (pairwise choice
  vs single-stimulus acceptance), so a hard cross-format gate would over-couple; the
  binding instrument gate remains tier-1 wn31 (same format as the primary).
- **Timing:** truthstyle-2x2 must freeze before f2b-transfer Stage-2 unblinds (R-2).
  The LLMBar calibration conditions on NO Stage-2 output and characterizes the judges,
  not the result, so it does NOT lose standing at unblinding and must not be allowed to
  delay the freeze. Freeze the 2x2 as designed; land LLMBar as its own small record.

What LLMBar adds that the custom probe alone cannot: an external, independently
authored answer to "are these three judges style-over-substance robust AT ALL?" — if a
judge scores near chance on LLMBar-Adversarial, a style-robust TOST PASS on d-ts reads
very differently, and the maintainer should see both numbers side by side.

---

## 4. f2b-errors — JUSTIFIABLY KEEP custom; no swap target exists

DECISION: the closed six-category taxonomy stays hand-authored and pipeline-specific; no established taxonomy is imported, and nothing supplements this record [STIPULATED: ASM-0030].

- There are NO eval items here to swap: the record is a $0 consumer of f2b-transfer
  Stage-2 logs. The only "custom" artifact is the category schema plus a deterministic
  assignment tree that is a PURE FUNCTION of the pre-declared logged fields
  (`poc/f2b-errors/taxonomy.json`).
- ProcessBench (arXiv:2412.06559; Apache-2.0; 3,400 cases over GSM8K/MATH/
  OlympiadBench/Omni-MATH; label = earliest erroneous step index, −1 if correct) is an
  error-LOCALIZATION dataset for step-indexed math chains. The f2b pipeline has no step
  chain — it has a string-equality verifier with abstention and k=4 bounded retries;
  its failure modes (extraction failure, non-engagement, gold-conflict,
  exhaust-stable/wander) are loop-mechanics categories with no counterpart in any
  step-label scheme. Importing PRM800K/ProcessBench-style categories would mint labels
  the logged fields cannot decide — exactly the "storytelling" the design doc already
  rejected when it refused GPT-5.6's earlier generic mapper/axiom categories.
- The self-authoring channel is different in kind: a descriptive taxonomy plus a
  cluster-bootstrap robustness primary cannot INFLATE a result — the primary can only
  qualify or undermine a Stage-2 PASS, never strengthen it, and the composition table
  is pre-frozen precisely so post-hoc narratives are impossible. The confound this
  record exists to price (pseudo-replication) is a statistics fact, not authored gold.
- Timing seals it: the record is dead as a confirmatory instrument the moment Stage-2
  unblinds (R-2). Any benchmark-flavoured redesign spends its confirmatory standing to
  buy nothing.
- For completeness: where process benchmarks COULD one day matter is a later F2-line
  generalization (the kernel verifier's retry loop on external math data) — a different
  experiment, gated on math-sector coverage that does not currently exist
  [EXTRAPOLATION, load_bearing: false; resolution path = a math-sector coverage census
  before any such design].

---

## 5. Benchmark fact sheet (verified at source, 2026-07-10)

All three of the maintainer's stated facts CHECK OUT. Sources verified directly this
session; a `reports/lit-eval-benchmarks.md` entry is a REQUIRED pre-freeze deliverable
if §2 is adopted, so these move from source-verified to properly lit-reported before
any record premises them. [LIT-BACKED pending lit-report — flagged, not hidden.]

| Benchmark | Paper | Licence (verified) | Content (verified) |
|---|---|---|---|
| CLUTRR | Sinha et al. 2019, arXiv:1908.06177 (EMNLP 2019) | **CC-BY-NC-4.0** (facebookresearch/clutrr LICENSE; HF mirror says "unknown" — repo governs) | Synthetic-kinship-graph k-hop relation composition; 24 relation types incl. grandmother/grandfather; released fields include `story_edges`, `edge_types`, `genders`, `proof_state`, `f_comb`, `target_text` — graph + derivation + gold ship with every item; ~70.6k rows over 6 configs; template/AMT-paraphrase story text; 7 noise configurations |
| LLMBar | Zeng et al., arXiv:2310.07641 (ICLR 2024) | **MIT** (princeton-nlp/LLMBar) | **419** instances (Natural + Adversarial{Neighbor, GPTInst, GPTOut, Manual}); instruction + 2 outputs, one faithful, one superficially better; gold preference; tests judge robustness to surface polish |
| ProcessBench | Qwen team, arXiv:2412.06559 (ACL 2025) | **Apache-2.0** (HF Qwen/ProcessBench) | **3,400** cases (GSM8K 400, MATH 1,000, OlympiadBench 1,000, Omni-MATH 1,000); task = identify earliest erroneous step; label = step index, −1 if fully correct |

---

## 6. One cross-cutting cheap step

Adopt a mandatory **provenance-triple disclosure** in every kot-reg record and verdict:
three one-line fields naming who authored the ITEMS, the GOLD, and the GRADER, with
"programme" / "third-party (source)" values. It costs nothing, makes the f2b-class
confound visible at a glance in every future design, and is the honest generalization
of what this adjudication did by hand. (Schema-rev recommendation only; no record is
touched by this document.)

---

## 7. Bottom line

LOAD-BEARING: the flagship should pivot its eval surface to CLUTRR — it is the rare case where a public benchmark preserves the experiment's entire honesty structure (gold-label independence, coverage-by-filter, matched-budget arm symmetry) while removing the programme's documented weakness at its most visible point, and the residual risks (headroom, extraction difficulty, contamination) are all priced by cheap pre-freeze mechanical blockers with a pre-declared fallback ladder [STIPULATED: ASM-0027; premises tagged in §0–§2].

The other two custom artifacts survive scrutiny for opposite reasons — truthstyle-2x2
because its estimand (an NSM-register factorial on the kernel's own bytes) exists in no
external dataset and its instrument should merely be externally calibrated (LLMBar,
side-record), f2b-errors because it has no eval data at all and imported taxonomies
would be undecidable from its logged fields. Both keep their custom cores; neither
freeze should wait on anything in this document except the maintainer's sign-off on the
nsk1 pivot.

---

## Epistemic register (tags relied on above)

- MEASURED: feasibility-synthesis §0 null-bound; m0b 0.3542 (corpus/rung/instance-indexed,
  transfers nowhere); l3a engine PASS (registry/verdicts/l3a.json); f2b confound
  characterization (registry/assessments/f2b-replicate.json).
- LIT-BACKED: arXiv:2406.12775 back-patching (via reports/lit-structured-parsing-and-inner-symbolic.md).
- LIT-BACKED pending lit-report (source-verified 2026-07-10, §5): CLUTRR
  (arXiv:1908.06177, CC-BY-NC-4.0, fields, relation set), LLMBar (arXiv:2310.07641,
  MIT, 419), ProcessBench (arXiv:2412.06559, Apache-2.0, 3,400, step labels).
  Pre-freeze deliverable: mint reports/lit-eval-benchmarks.md.
- STIPULATED: ASM-0023 (adopted — superseded by ASM-0027, which carries the CLUTRR
  choice and its residuals; ASM-0028..0030 register the §1 criterion and the §3/§4
  verdicts); headroom/contamination planning concerns in §2.6, each with a named
  pre-freeze measurement that resolves it.
- EXTRAPOLATION (load_bearing: false): the §4 note on future math-sector process-bench
  use; ASM-0024/0025 carry over unchanged.
- TO-MEASURE build facts deliberately NOT estimated here: the CLUTRR covered-slice
  count; SmolLM2 text-only accuracy on CLUTRR (the headroom blocker measures it).
