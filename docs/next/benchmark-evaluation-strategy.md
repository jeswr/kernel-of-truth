# Benchmark-evaluation strategy — the SmolLM2 standard suite + the coding-benchmark roadmap (N1-LB extension)

> **Status: STRATEGY / roadmap for maintainer sign-off. Nothing here is frozen,
> registered, or scheduled; no experiment is created and no registry record is touched.**
> Author: Fable, experiment-designer role (`kern/fable-designer`), 2026-07-10.
> This document EXTENDS `idea-leaderboard-benchmark-eval` (registry/ideas.jsonl, scoped
> 2026-07-09) and the N1-LB surface (`docs/next/architecture-ladder.md` §10) with (Part 1)
> the concrete SmolLM2-family standard-benchmark suite the programme's host models were
> published against, and (Part 2) a coding-benchmark roadmap for the code/SE track ending
> at SWE-Bench Pro. Where this document and §10 overlap, §10's machinery (b-cov census,
> LB-1, LB-GATE, §10.5 reporting law) is inherited verbatim, never redefined.
>
> Inputs read at source: `docs/next/architecture-ladder.md` §10; `docs/next/
> feasibility-synthesis.md`; `docs/next/eval-necessity-adjudication.md`;
> `registry/ideas.jsonl` (`idea-leaderboard-benchmark-eval`); `docs/
> design-a5-code-worldlayer-oracle.md`; `data/d-ext/manifest.json`; bead
> `kernel-of-truth-hu10`; benchmark sources verified directly 2026-07-10 (§1.1, §6.1).
> Deliberately NOT touched (concurrent nsk1 agent): `registry/assumptions.jsonl`, all
> nsk1 files, `docs/next/eval-necessity-adjudication.md`, every registry record, kb-sync.

---

## 0. Governing facts

Everything in this strategy is shaped by five measured facts, restated with scope:

- PREMISE: across the entire frozen registry there are ZERO audited end-task wins over
  the kernel-as-text null; the sole positive end-task PASS is confined to a
  self-authored oracle-favourable slice and is correct-alignment-specific, not
  kernel-content-specific [MEASURED: docs/next/feasibility-synthesis.md §0 + §2b,
  backed by registry/assessments/oracle-coverage.json and
  registry/assessments/f2b-replicate.json].
- PREMISE: kernel-vocabulary coverage is 0.3542 of content-word mass on the FRIENDLIEST
  measured corpus (TinyStories-validation) at the molecules-v0 rung of one incomplete
  kernel instance, and it transfers to no other corpus [MEASURED:
  registry/verdicts/m0b.json, audit CONFIRMED; non-transfer is the open
  [STIPULATED: ASM-0002] caution].
- PREMISE: vocabulary coverage and item CHECKABILITY are different quantities and
  checkability is the binding one — on OpenBookQA, lemma-touch ≈49% (2,903/5,957)
  coexists with item-checkability 0/500, and the strongest supported configuration was
  byte-identical to model-alone on all 500 externally-authored items at every seed
  [MEASURED: data/d-ext/manifest.json; registry/assessments/f2b-replicate.json].
- PREMISE: off the checkable slice the verify-retry mechanism abstains by construction,
  so any blended benchmark score is the arithmetic identity Δ_B = κ_B × Δ_covered — a
  near-zero blended delta at low κ_B is the coverage ceiling, not evidence about kernel
  quality [MEASURED: registry/assessments/f2b-replicate.json d-ext byte-identical;
  identity stated in docs/next/architecture-ladder.md §10.5].
- PREMISE: the deterministic substrate is real — the kot-axiom/1 v0 engine is exact and
  fail-closed on its covered slice at ~µs/query and ports across a domain vertical with
  a byte-identical binary — but this is instrument-adequacy measured inside the fortress
  wall, not usefulness to any model [MEASURED: registry/verdicts/l3a.json +
  registry/verdicts/a5.json, both audit CONFIRMED].

The design consequence, applied throughout: **coverage mismatch is the default, not the
exception.** Every benchmark below is presumed uncovered until a census measures
otherwise, and the honest per-benchmark questions are exactly three:

(a) does kernel support HELP on the census-identified covered subset, at matched budget,
against the mandatory nulls;
(b) does kernel support NOT HURT general capability anywhere else (non-regression);
(c) how do our model-alone numbers CONNECT to the models' published baselines
(anchoring), without ever making a leaderboard claim.

---

# PART 1 — the SmolLM2-family standard suite

## 1.1 The suite, verified (source-verified 2026-07-10)

The programme's host rungs are `HuggingFaceTB/SmolLM2-{135M,360M,1.7B}-Instruct`
(docs/research-plan/06-resources.md §2.1). The SmolLM2 release (Allal et al. 2025,
arXiv:2502.02737) published base-model scores on exactly the nine benchmarks the
maintainer names, evaluated with lighteval, zero-shot unless stated. Facts below were
verified this session against the HF dataset cards, upstream repos, and the SmolLM2
model cards; a `reports/lit-eval-benchmarks.md` extension is a REQUIRED pre-freeze
deliverable before any record premises them (the eval-necessity §5 discipline —
LIT-BACKED pending lit-report, flagged not hidden).

| Benchmark | Paper (arXiv, year) | Eval-relevant size | Licence (verified) | Format / metric | SmolLM2-card variant |
|---|---|---|---|---|---|
| ARC (Easy+Challenge) | Clark et al., 1803.05457 (2018) | 7,787 total; test 2,376 Easy + 1,172 Challenge | CC-BY-SA-4.0 (HF allenai/ai2_arc) | 4-way MC, accuracy | "ARC (Average)", zero-shot |
| OpenBookQA | Mihaylov et al., 1809.02789 (2018) | 5,957; test 500 | Apache-2.0 — already pinned in-repo (data/d-ext/manifest.json, HF rev 388097e) | 4-way MC, accuracy | zero-shot |
| HellaSwag | Zellers et al., 1905.07830 (2019) | val 10,042 (test labels hidden) | MIT (HF Rowan/hellaswag) | 4-ending completion, accuracy | zero-shot |
| CommonsenseQA | Talmor et al., 1811.00937 (2019) | 12,102; val 1,221 (test labels hidden) | MIT (HF tau/commonsense_qa) | 5-way MC, accuracy; ConceptNet-derived | zero-shot |
| WinoGrande | Sakaguchi et al., 1907.10641 (2019/AAAI-20) | 44k problems; dev 1,267 (test labels hidden) | dataset CC-BY, code Apache-2.0 (allenai/winogrande) | binary fill-in-blank, accuracy | zero-shot |
| PiQA | Bisk et al., 1911.11641 (2020/AAAI) | train 16k / dev ≈2k (test ≈3k, labels hidden) | AFL-3.1 (ybisk repo; HF card blank) | binary physical-commonsense choice, accuracy | zero-shot |
| MMLU | Hendrycks et al., 2009.03300 (2021/ICLR) | 57 subjects; test 14,042 | MIT (HF cais/mmlu) | 4-way MC, accuracy, per-subject | MMLU **cloze** on 135M/360M cards; the 1.7B card instead reports **MMLU-Pro (MCF)** — a DIFFERENT, harder derivative dataset |
| TriviaQA | Joshi et al., 1705.03551 (2017) | 95k QA pairs (rc; unfiltered val 11,313) | **UNRESOLVED** — HF card licence unknown; UW disclaims question/document copyright | open-ended EM | few-shot per card notes |
| GSM8K | Cobbe et al., 2110.14168 (2021) | 8.5k; test 1,319 | MIT (HF openai/gsm8k) | open-ended numeric, EM | 5-shot |

Published anchor scores (the "published baseline" of question (c)):

| Model (base card) | HellaSwag | ARC-avg | PIQA | MMLU-cloze | CSQA | TriviaQA | WinoGrande | OBQA | GSM8K-5shot |
|---|---|---|---|---|---|---|---|---|---|
| SmolLM2-135M | 42.1 | 43.9 | 68.4 | 31.5 | 33.9 | 4.1 | 51.3 | 34.6 | 1.4 |
| SmolLM2-360M | 54.5 | 53.0 | 71.7 | 35.8 | 38.0 | 16.9 | 52.5 | 37.4 | 3.2 |
| SmolLM2-1.7B | 68.7 | 60.5 | 77.6 | (card reports MMLU-Pro MCF 19.4, not MMLU-cloze) | 43.6 | 36.7 | 59.4 | 42.2 | 31.0 |

Anchor caveats, all binding on §1.5:

- The published nine-benchmark tables are for the **BASE** models; the programme runs
  the **Instruct** variants. The instruct cards publish only a subset (HellaSwag, ARC,
  PIQA, MMLU-cloze/MMLU-Pro, BBH, GSM8K — e.g. 135M-Instruct HellaSwag 40.9, ARC 37.3,
  GSM8K 1.4; 1.7B-Instruct GSM8K 48.2). Cells with no published instruct number get an
  explicit "no anchor" flag, never a borrowed base number.
- The MMLU variant is inconsistent across sizes on the cards (cloze at 135M/360M;
  MMLU-Pro MCF at 1.7B). Anchoring at 1.7B on plain MMLU therefore has no published
  cell; disclosed, not interpolated.
- Exact lighteval task variants (continuation scoring vs MCF, normalisation, shots) are
  a build-time pin: the harness-fidelity gate (§1.4) is only meaningful once our
  invocation is variant-matched to the card's.
- TriviaQA's unresolved licence triggers the d-ext fail-closed sourcing discipline: no
  derived TriviaQA artifact is committed to the repo until licence status is resolved
  at lit-report time. Census statistics (counts, κ) are fine; item bytes are not.

## 1.2 Triage — three dispositions, census before spend

"Disposition" here means the honest ROLE each benchmark can play, given the governing
facts. It refines §10.2's tiering for the SmolLM2 nine; where the maintainer's grouping
and §10.2's registered prior disagree (TriviaQA), both are stated and the census
decides.

- DECISION: each benchmark is assigned one of three dispositions — covered-help
  candidate (census-first), non-regression-only, or math-route — as a registered PRIOR
  about item type, converted per-benchmark to MEASURED by the b-cov census before any
  GPU spend; the prior is stipulated in a new register entry (§3, proposed entry 1)
  [MEASURED: the d-ext warning that type-priors can coexist with zero checkability —
  data/d-ext/manifest.json lemma-touch ≈49% vs checkable 0/500].

| Benchmark | Disposition | Why (item type) | Expected checkability route | Honest expectation today |
|---|---|---|---|---|
| ARC-Easy | **covered-help candidate** | grade-school science, many simple declarative facts (§10.2 Tier A) | science-fact world-layer ingestion + query-grammar growth | κ ≈ 0 until world-layer ingestion lands |
| ARC-Challenge | covered-help candidate, second line | mixed, minority kernel-shaped subset (§10.2 Tier B) | same | lower yield than Easy |
| OpenBookQA | **covered-help candidate — canonical growth target** | core-science facts; corpus already pinned in-repo (d-ext) | world-layer ingestion (the binding constraint, measured) | lemma-touch ≈49% MEASURED, checkable 0 MEASURED — the reference trajectory point |
| MMLU (per-subject) | **covered-help candidate for definitional-heavy subjects only**; remaining subjects non-regression pool | definitional/factual density varies enormously by subject; bead kernel-of-truth-hu10 already tasks the define-lane census over biomedical subjects | definition growth (haiku-tier mint) + world layer, per subject | most subjects κ ≈ 0; a few definitional subjects may show first non-zero yield |
| CommonsenseQA | covered-help candidate | ConceptNet-derived — relational/lexical by construction (§10.2 Tier A) | definition/molecule growth, no world layer needed | mapper in-context sense resolution is the priced risk |
| TriviaQA | **census-only** (maintainer groups it factual — type agreed; §10.2 places it Tier C because fact-coverage is authoring-cost-bound) | broad world trivia: named entities, events, places — exactly what the kernel does not author | structured-DB world-layer ingestion at scale | κ ≈ 0; census costs ~$0 and settles it; licence blocker (§1.1) |
| HellaSwag | **non-regression-only** | narrative plausibility continuation — no kernel-decidable proposition (§10.2 Tier C) | none at v0; revisit only on a named dependency | kernel will NOT help here; that is the expected cell |
| WinoGrande | **non-regression-only** | pronoun/commonsense disambiguation — no kernel-decidable proposition | none at v0 | same |
| PiQA | **non-regression-only** | physical affordances — no kernel-decidable proposition | none at v0 | same |
| GSM8K | **math-route** | multi-step arithmetic; the kernel has NO arithmetic — a math-basis vocabulary/sector is a separate unbuilt idea (§10.2 Tier C) | math-sector census gate first; no design until a math sector exists | κ = 0 by construction today; also serves the non-regression pool |

Two explicit honesty notes:

- The covered-help candidates are candidates for a CENSUS, not for a run. On today's
  kernel the measured reference point (OpenBookQA: checkable 0/500) says the likely
  census outcome for most rows is κ_B ≈ 0, reported with the same prominence as any
  positive. The suite's value now is establishing the per-benchmark trajectory
  baseline, exactly as §10.1 designed.
- HellaSwag / WinoGrande / PiQA / GSM8K are not discarded — they are re-purposed. Their
  seat is question (b): they are the cleanest possible NON-REGRESSION instruments
  precisely because the kernel has nothing to say on them, so any movement under an
  always-on kernel mechanism is pure side-effect signal.

## 1.3 The three honest questions, instrumented

### (a) Covered-help — LB-SMOL-HELP (an instantiation of LB-1, §10.3)

Not a new surface: LB-1's design (arms, kills, rungs, DVs) is inherited verbatim; this
section only pins the benchmark list (the SmolLM2 nine's covered-help candidates) and
the item-selection method.

**Coverage-mapping method (the mapper selects covered items).** Item selection is the
b-cov census predicate stack (§10.1), computed deterministically, no model calls:

1. lemma-touch sieve (the d-ext R-C filter verbatim) — cheap upper sieve, reported but
   never gating;
2. κ_B^verify — the F2-line runtime verifier's own kernel_checkable predicate (P10
   extraction target expressible + canonical record backing a decidable proposition);
3. κ_B^engine — stem+gold parses under the deterministic mapper (`a1-hybrid` lineage) +
   closed kot-axiom/1 query grammar into a query the L3 engine answers from records;
   gold-parse and mapper-parse counted SEPARATELY (stage-indictment discipline).

The covered slice for any run is the census output at a pinned {benchmark revision,
kernel corpus hashes, world-layer hash, mapper hash, grammar version} key; the census
hash rides in the frozen record. The census predicate and the runtime mechanism's
engagement must agree at run time — disagreement is INSTRUMENT-INVALID (fix the census,
never reinterpret), with the engagement floor pre-declared (§10.3 kill forms).

**Arms** (inherited): model-alone; the passed kernel mechanism (verify-retry enters
ONLY if f2b-transfer PASSes; a FAIL re-gates onto the next passed mode, L3b or L1a);
shuffled-kernel (content control); kernel-as-text at matched token budget (Law 2);
gloss-text self-verify at matched budget (commodity null). No mechanism is discovered
here — LB-SMOL-HELP prices already-passed mechanisms on public ground.

**Primary endpoint shape** (one per record): paired per-item accuracy delta
(kernel-mode minus model-alone) on the checkable slice of the SINGLE highest-κ
benchmark at the frozen rung set (R1+R3 minimum, sign-only language) — an ABSOLUTE
paired difference, never a ratio (the F2 degenerate-denominator lesson). All other
benchmarks and rungs are one Holm family of secondaries.

**Gate to run:** LB-GATE (§10.4) unchanged — f2b-transfer PASS (or successor mode's own
rung PASS), census yield ≥500 checkable items on ≥2 external benchmarks, κ thresholds
0.10/0.20, maintainer sign-off. Nothing in Part 1 relaxes it.

### (b) Non-regression — LB-SMOL-NOREG (new arm shape, defined here; dormant until an always-on mechanism exists)

The maintainer's question (b) — does kernel-steering hurt general capability — is
MECHANISM-INDEXED, and the honest design splits on one property:

- DECISION: for gated/abstaining mechanisms (verify-retry, L3b routed-hybrid),
  non-regression on uncovered items is satisfied BY CONSTRUCTION — the output is
  byte-identical to model-alone off-slice — so the non-regression instrument is not a
  scored eval but an ABSTENTION AUDIT: assert byte-identity of outputs on a
  deterministic uncovered subsample of every suite benchmark, ~$0 beyond the run itself
  [MEASURED: registry/assessments/f2b-replicate.json — d-ext 500/500 byte-identical at
  every seed is exactly this audit already passing once].
- DECISION: for ALWAYS-ON mechanisms that touch every token or every forward pass
  (activation steering of the nsk1 lineage if its rung passes; L1a input
  canonicalisation; any in-tokenisation/normalisation rung; lint mode-S constrained
  output), non-regression is a real measured question: a TOST non-inferiority test of
  mechanism-on vs OWN-HARNESS model-alone, per benchmark, on deterministic subsamples
  of the full nine (the non-regression pool includes HellaSwag / WinoGrande / PiQA /
  GSM8K / remaining MMLU — the uncovered benchmarks earn their seat here); margins per
  benchmark fixed at freeze; one Holm family; any benchmark whose TOST fails =
  named regression, reported with kill-level prominence [MEASURED: registry/verdicts/m0b.json — the comparator choice rests on the measured fact that harness/kernel-state differences move scores, so the binding comparator must be own-harness model-alone; the published card number anchors the harness, it is never the non-regression baseline].

LB-SMOL-NOREG is therefore DEFINED now and DORMANT: no always-on mechanism currently
holds a passed rung (the nsk1 steering rung is in flight and nothing is premised on
it). The moment one passes, the non-regression wave is the mandatory rider on its first
deployment claim. Costing: nine benchmarks × n≈500 subsample × 2 arms × R1+R3 is a
Tier-1 inference-only wave (~$10–40 with f2b harness reuse; sized properly at freeze).

### (c) Baseline-anchored comparison — the anchoring protocol

- DECISION: published SmolLM2 card numbers are used as a HARNESS-FIDELITY ANCHOR and as
  context rows in reports — never as a comparison arm and never as the baseline a
  kernel effect is measured against; the binding comparator in every arm contrast is
  own-harness model-alone under identical pins [MEASURED: data/d-ext/manifest.json — the cards' own variant inconsistencies (§1.1: base vs instruct, MMLU-cloze vs MMLU-Pro) plus the measured harness/kernel-state sensitivity make the published numbers non-comparable across cells except as anchors].

Protocol: before any kernel arm runs on a benchmark, reproduce model-alone under a
variant-matched lighteval invocation on the published cell(s); the run is
anchor-VALID if our number lands within a pre-declared tolerance of the published cell
(proposed constant ±2.0 pp, a stipulated instrument constant — §3, proposed entry 2;
maintainer-resettable at freeze). Anchor failure = instrument investigation before any
kernel arm result is interpreted, not a re-run until it passes. Cells with no published
number (most instruct cells) are flagged "no anchor" and lean on the model's other
anchored cells. This is the entire leaderboard connection: our tables print the
published number beside our model-alone number so a reader can see the harness is
faithful — and the §10.5 forbidden-phrasing law applies verbatim on top: no
"beats/improves <benchmark>", no leaderboard or SOTA claim language anywhere, licensed
template only ("on the κ_B = x checkable slice of <benchmark> (N = n of N_total),
<mode> moved accuracy a→b at c× compute; the remaining 1−κ_B is untouched by
construction").

## 1.4 Pre-registration shape

One kot-reg/1 record per wave, designer-frozen per the standing rails:

- **Record family:** `lb-smol-help-<n>` / `lb-smol-noreg-<n>` under the N1-LB surface;
  b-cov census extension needs NO record (Tier-0 instrument, census output hashed).
- **IVs:** benchmark (census-cleared list), mechanism (passed modes only), rung (R1+R3
  min), seed set. **DVs:** §10.3's verbatim (checkable-slice paired accuracy primary;
  full metric vector V with cost_ratio; engagement/abstention; model-alone
  checkable-vs-non-checkable disclosure; blended delta descriptive-only).
- **Exactly one primary**; Holm family for all secondaries; TOST margins for every
  potential null (non-regression margins per benchmark) fixed at freeze; power computed
  on the census-measured covered slice (LB-GATE's ≥500-item floor inherits f2b's
  advisor sizing, ~0.92 one-sided power at n=250×3 seeds for Δ≈0.10 — re-sized at
  freeze via --dry-plan).
- **Instrument gates, each with its own bound:** census-vs-runtime engagement floor;
  harness-fidelity anchor tolerance; extraction-failure ceiling; benchmark revision +
  census hash pins (fail-closed on provenance, the d-ext discipline).
- **Kill criteria** (forms fixed by §10.3, margins at freeze): kernel arm ≤
  kernel-as-text OR ≤ gloss-self-verify at matched budget on the checkable slice
  (Law-2/commodity kill); shuffled-kernel recovery ≥ pre-declared fraction (content
  kill); engagement below floor (instrument kill). Non-regression wave: TOST fail on
  any pool benchmark is a headline finding, never a footnote.
- **Provenance-triple disclosure** (eval-necessity §6): items third-party (benchmark),
  gold third-party (benchmark), grader programme-authored — printed in the record and
  every verdict.
- **Contamination:** SmolLM2's pretraining mixture plausibly contains suite items;
  carried as the accepted RT-7a limitation — the primary is a within-item ARM contrast,
  symmetric in first order; eval-split preference and a names/ordering scramble
  diagnostic are reported-only riders where format permits.

## 1.5 Anti-overclaiming envelope (binding on every number from this suite)

§10.5 is inherited verbatim: coverage-first reporting (κ_B + N_checkable/N_total +
census hash + kernel version in the same sentence or row); the blended-score identity
Δ_B = κ_B × Δ_covered stated to pre-empt both misreads (never a headline, never
quotable as "the kernel is bad" at low κ_B); forbidden phrasing + licensed template;
selection-effect disclosure; trajectory-is-the-deliverable; NICHE-SCOPE banner below
thresholds. Suite-specific additions:

1. No cross-benchmark aggregation: a single "suite score" over the nine is forbidden —
   it launders covered and uncovered benchmarks into one number the identity above
   cannot protect.
2. Variant-matching disclosure in every table (base vs instruct, cloze vs MCF, shots).
3. Anchor rows are context: "published (card, base, lighteval)" is printed as its own
   labelled column, never differenced against a kernel arm.
4. Non-regression results are mechanism-indexed: "steering does not regress the suite"
   licenses nothing about any other mechanism, and vice versa.

## 1.6 Sibling or nsk1 arm? — SIBLING. And the cheapest first cut

- DECISION: the SmolLM2-suite evaluation is a SIBLING experiment family under the
  N1-LB surface (LB-SMOL-HELP / LB-SMOL-NOREG instantiating LB-1), NOT an added arm or
  benchmark inside the nsk1 flagship [MEASURED: registry/assessments/oracle-coverage.json — because no mechanism yet holds an audited end-task win, LB can only PRICE already-passed mechanisms on ecologically-valid ground (§10.6, LB-1 "decides no architecture"), whereas nsk1 is a mechanism-DISCOVERY contrast; one-primary discipline then forbids bolting nine benchmarks onto a record that already has its primary].

Concretely: nsk1 proceeds untouched (concurrent agent; nothing here amends it). The
connection runs one way — IF nsk1's steering mechanism passes its rung, steering
becomes the first always-on mechanism and LB-SMOL-NOREG wakes up as its mandatory
non-regression rider; IF f2b-transfer passes, verify-retry claims the LB-SMOL-HELP
seat. The suite consumes flagship outcomes; it never feeds them.

**Cheapest first cut (recommended now, sign-off item 1):** `b-cov-smol` — extend the
already-designed b-cov census (§10.1) to the pinned SmolLM2 nine. Tier 0, ~$0,
CPU-only, this box, no model calls, no gate to run. Outputs per benchmark: N_total,
lemma-touch, κ_B^verify, κ_B^engine (gold and mapper separately), keyed to
{benchmark revision, kernel hashes, world-layer hash, mapper hash, grammar version};
appended to the per-kernel-version trajectory log. Split selection = the split
lighteval actually scores (validation where test labels are hidden: HellaSwag, CSQA,
WinoGrande, PiQA), pinned in the census manifest. This coexists with — and does not
supersede or claim — bead kernel-of-truth-hu10's define-lane census over the Tier-A
definitional benchmarks; b-cov-smol is the benchmark-list superset using the same
instrument, and the hu10 work proceeds unchanged. Expected honest outcome: κ ≈ 0 on
most or all nine rows today, published with the same prominence as any positive — that
IS the baseline trajectory point the maintainer's question needs.

---

# PART 2 — coding benchmarks (the code/SE track roadmap)

## 2.1 Coding-benchmark fact sheet (source-verified 2026-07-10)

Same discipline as §1.1: verified this session; lit-report extension required before
any record premises them.

| Benchmark | Source | Size | Licence | Metric | Status 2026-07 |
|---|---|---|---|---|---|
| HumanEval | Chen et al., arXiv:2107.03374 (2021, OpenAI) | 164 hand-written Python problems | MIT | pass@k by unit-test execution | standard function-level; long-saturated at frontier |
| MBPP | Austin et al., arXiv:2108.07732 (2021, Google) | 974 (test split 500; sanitized 427) | CC-BY-4.0 | pass@k via 3 asserts/problem | standard function-level |
| SWE-Bench | Jimenez et al., arXiv:2310.06770 (ICLR 2024) | 2,294 real issue→PR instances, 12 Python repos | MIT (harness) | % resolved (fail-to-pass tests) | superseded for claims by its subsets |
| SWE-Bench Verified | OpenAI + SWE-Bench (Aug 2024) | 500 human-validated instances (93 contracted developers screened solvability/tests) | as SWE-Bench | % resolved | **DEPRECATED by OpenAI 2026-02-23** — contamination in frontier training data + a large fraction of failed cases traced to flawed tests, saturation ~75–81%; reported via secondary coverage (the primary openai.com post is 403 from this box) — lit-report must verify at source |
| **SWE-Bench Pro** | Scale AI, arXiv:2509.16941 (Sept 2025; v2 Nov 2025) | 1,865 instances = **731 public** + 858 held-out + 276 commercial, across 41 repos (11 public, 12 held-out, 18 commercial) | public set on HF; public/held-out repos deliberately **GPL/copyleft** (contamination resistance); per-repo licences govern code bytes — pin at design time | % resolved, long-horizon agentic tasks, containerized | OpenAI-endorsed successor to Verified; release-era frontier agents scored <25% on the public set; 2026 leaderboard coverage reports rapid movement since — current SOTA is a lit-report deliverable, deliberately not premised here |

Note the design lesson inside these facts: the benchmark the maintainer names as the
north star exists BECAUSE self-serving evaluation surfaces (contaminated, flawed-test)
eventually collapse. The programme's own honesty rails (pinned revisions, provenance
triple, fail-closed sourcing) are the same move; SWE-Bench Pro's copyleft+held-out
design is independent convergence on it.

## 2.2 Where the code track actually is today — the honest gap

What is MEASURED: a5 — the kot-axiom/1 engine, byte-identical to the l3a pin, over a
deterministically-extracted code world layer (kot-code-extract/1, CPython ast,
RNG-free) answered 855/855 covered code-structure queries exactly and refused 122/122
controls strictly, at ~7.8 µs/query, audit CONFIRMED [MEASURED:
registry/verdicts/a5.json]. Its registered scope statement is explicit: 15-file
self-snapshot of this repo's own tooling, self-authored queries, coverage BY
CONSTRUCTION, six structural (NOT NSM-explicated) code concepts
[STIPULATED: ASM-0007], no NL, no LLM arm, no representativeness claim, "licenses no
statement about kernel usefulness to any model".

What is NOT measured, in order of mortality:

1. **The NL boundary** — a5-nl (designed, `docs/design-nl-boundary-l3a-parse-a5-nl.md`,
   UNRUN): can natural-language code questions reach the closed kot-query-code/1
   grammar through the mapper at a usable yield? Every prior programme lesson says
   this is where mechanisms die.
2. **External code** — everything so far is a self-snapshot; zero external repos, zero
   scale, one language, exact-name call resolution only.
3. **SE-concept semantics** — six structural definitions ≠ an SE-concept sector.
   Nothing NSM-explicated, no types/dataflow/behaviour, and the grammar deliberately
   refuses those asks today (fail-closed `ERR_BAD_QUERY`).
4. **Generation vs QA** — the oracle ANSWERS structure queries about existing code;
   coding benchmarks score GENERATED code (function-level) or REPO MODIFICATIONS
   (SWE-class). No mechanism connecting the oracle to either exists.
5. **The agentic loop** — SWE-class tasks presume a capable agent host navigating a
   repo over a long horizon. The programme's host rungs are 135M–1.7B models that
   score near zero on such tasks; a5-llm (the engine-vs-LLM head-to-head) is under a
   separate contested-audit ruling and nothing here premises on it in either direction
   [per docs/next/feasibility-synthesis.md — treated verbatim as REFUTE-on-pins,
   science reproduces, ruling in flight].

The distance from "microsecond structure oracle over 15 of our own files" to "helps on
SWE-Bench Pro" is the largest gap anywhere in this programme. This roadmap names every
intermediate surface and refuses to promise across the gap.

## 2.3 What kernel-assist on coding benchmarks could even BE

Three candidate mechanisms, with their honest opponents:

- **(i) Repo-structure context-provision (the strongest candidate).** The engine as a
  deterministic TOOL in an agent loop: the model proposes queries in NL or grammar,
  the engine answers repo-structure facts (callers/callees/where-defined/imports/
  contains) with provenance and licensed refusals; answers enter the context as text
  (Law 1). This is exactly the Law-3 topology (neural proposer ↔ formal language ↔
  deterministic engine). Honest opponents at matched budget: **the commodity
  deterministic-tooling null** — grep/ctags/LSP/type-checkers already own the
  deterministic seat in code (the a5 design says this verbatim), so any help-claim
  must beat an agent given the SAME facts via commodity tooling, not just
  kernel-as-text. The kernel's differentiable margin is canonical cross-domain concept
  identity + licensed provenance/refusal semantics — a THIN margin, stated candidly.
- **(ii) Structural verify of generated code.** Parse the model's generated code with
  the same deterministic extractor, check structural propositions against the world
  layer / axioms, retry on violation (the F2-line loop transplanted). Honest problem:
  compilers, linters and type-checkers perform strictly stronger checks for free; the
  kernel adds value only where a canonical-concept constraint is not expressible in
  commodity tooling. Candidate niche, not a default.
- **(iii) SE-concept grounding of task text.** Mapping issue/task descriptions into
  kernel SE concepts for retrieval/localization — where a5-nl's mapper leg either
  lives or dies first.

And where the kernel will likely NOT help, stated as the default:

- **HumanEval/MBPP are near-kernel-null BY CONSTRUCTION**: self-contained algorithmic
  problems with no repository, so the world-layer (repo structure) has nothing to
  assert; expected checkability ≈ 0 (registered as an extrapolation with a census
  resolution path — §3, proposed entry 3). Their honest roles are (a) the
  non-regression pool for any always-on code-side mechanism and (b) harness practice
  — NOT covered-help candidates.
- **Algorithmic correctness, idiomatic style, API knowledge** — the bulk of what
  coding benchmarks reward — are exactly the competencies the kernel does not encode.

The mechanism conclusion that shapes the roadmap: the kernel's only plausible
coding-benchmark contribution runs through REPO-LEVEL STRUCTURE (localization,
navigation, licensed repo facts), which is why the meaningful intermediate surface is
repo-structure QA / issue→file localization, not function-level generation.

## 2.4 The roadmap — milestones and gates

Milestones are surfaces; gates are what must be MEASURED before the next surface is
even meaningful. Thresholds are set at each design's freeze; the FORMS are fixed here.

| Milestone | Surface | State | Gate to pass BEFORE it |
|---|---|---|---|
| **M0** | a5 — deterministic code-structure oracle, self-snapshot | **DONE** (PASS, audit CONFIRMED; instrument-adequacy only) | — |
| **M1** | a5-nl — NL→grammar mapper leg on code-structure questions | designed, UNRUN (~$10, no GPU) | G-CODE-0 |
| **M2** | SE-concept grounding + repo-scale extraction | not designed | G-CODE-1 |
| **M3** | Repo-structure QA / issue→file localization help-test — **the first surface where a kernel HELP claim is possible** | not designed | G-CODE-2 |
| **M4** | Function-level benchmarks (HumanEval/MBPP) — non-regression pool + optional structural-verify probe only | not designed | G-CODE-2 (mechanism (ii) variant) |
| **M5** | Repo-level agentic: SWE-Bench-Verified data as DIAGNOSTIC/dev surface (deprecated for claims), then **SWE-Bench Pro public set as the claim-bearing north star** | not designed | G-CODE-3, then G-CODE-4 |

**G-CODE-0 — the code-bench census (now-eligible, Tier 0, ~$0).** b-cov's sibling over
coding benchmarks: for HumanEval (164), MBPP (974), and SWE-Bench Pro public task
statements (731), compute the fraction of items containing ≥1 kernel-checkable /
engine-parseable proposition at current code-v0 concepts + kot-query-code/1 grammar,
same key/pinning discipline as §10.1. Converts the ≈0 expectation to MEASURED before
any further code-track design. Also: pin the licence/provenance of each corpus
(SWE-Bench Pro's copyleft bytes get the d-ext quarantine treatment — eval-side only,
nothing enters kernel content).

**G-CODE-1 — the NL boundary.** a5-nl runs and its mapper-parse yield on
externally-phrased code-structure questions clears its own frozen floor (record
topology already registered [STIPULATED: ASM-0026]). A FAIL parks the entire coding
track behind mapper improvement — there is no route to any coding benchmark that does
not cross this boundary.

**G-CODE-2 — coverage + mechanism, jointly.** (a) An SE-concept sector exists beyond
the six structural concepts (either NSM-explicated code concepts per the a5 successor
note, or a versioned structural-v2 expansion), with the G-CODE-0 census re-run showing
material checkability on the TARGET benchmark's items (threshold at freeze; the κ ≥
0.10 headline-eligibility mirror of §10.4 is the default proposal). (b) An assist
mechanism — (i) context-provision or (ii) structural-verify — holds its OWN passed
rung on a small pre-registered probe whose nulls include BOTH kernel-as-text AND the
commodity deterministic-tooling null (grep/ctags/LSP at matched budget). No coding
benchmark run is meaningful before both halves exist: without (a) the run measures
coverage (the naive-run trap, already measured on d-ext); without (b) there is no
treatment to test.

**G-CODE-3 — repo scale.** The extractor (tree-sitter route, multi-language as needed)
validated on ≥1 pinned EXTERNAL repository at ≥100-file scale with the a5 discipline
intact (byte-determinism, fail-closed collisions, planted-violation capture), and the
M3 localization help-test read out: paired assist-delta of agent+kernel-oracle vs
agent+commodity-tooling on issue→file/function localization gold (SWE-Bench-Verified's
issue→gold-patch mapping is a fine THIRD-PARTY localization gold even though its
resolve-metric is deprecated — we consume its data, not its leaderboard; contamination
disclosed as RT-7a).

**G-CODE-4 — the agentic gate (SWE-Bench Pro).** All prior gates, PLUS: a capable
agent host (frontier-class, budget-gated — the SmolLM2 rungs cannot carry this
surface), maintainer sign-off on spend, and the claim shape fixed in advance: paired
assist-delta (same agent, same budget, kernel-oracle tool vs commodity-tooling arm) on
the PUBLIC set, reporting localization/context sub-metrics first and % resolved
second, under §10.5's licensed template. "Kernel improves SWE-Bench Pro by X" is
forbidden phrasing exactly as on every other benchmark.

## 2.5 What is explicitly NOT promised

- No SWE-Bench (any variant) number, promise, or timeline is attached to the current
  code-oracle. Today's measured artifact answers structure queries about 15 of its own
  files; the gap to agentic repo-level SE spans five unmeasured layers (§2.2), each of
  which has historically been where mechanisms die.
- Function-level pass@k improvement is NOT a kernel value thesis: HumanEval/MBPP are
  near-kernel-null by construction, and a null result there is the expected cell, not
  news.
- Even at M5, the claim shape is assist-delta at matched budget against commodity
  tooling on the covered/localization surface — never a leaderboard position, never
  SOTA language, never a blended resolve-rate headline (the Δ_B = κ_B × Δ_covered
  identity applies to repo tasks too: most SWE-Bench-Pro instances will not touch
  kernel-covered structure even at M5 maturity).
- Nothing in Part 2 competes with the flagship lane for resources before G-CODE-1:
  the only now-eligible spends are the two Tier-0 censuses and the already-designed
  ~$10 a5-nl run, in that order.

---

## 3. Assumptions to REPORT for registration (not written here)

Per the honesty-guard, this document registers nothing itself; the coordinator should
append these to the register (ids: the next sequential ids free at registration time)
and kb-sync. Marker lines above deliberately cite only already-registered ASM ids.

1. **STIPULATED — SmolLM2-suite triage prior.** Claim: the §1.2 dispositions
   (covered-help candidates ARC-Easy/ARC-Challenge/OpenBookQA/MMLU-definitional-
   subjects/CommonsenseQA; TriviaQA census-only; HellaSwag/WinoGrande/PiQA
   non-regression-only; GSM8K math-route) are a prior about item TYPE, not measured
   checkability; each cell is converted to MEASURED by the b-cov-smol census before
   any GPU spend on that benchmark. Owner: experiment-designer. load_bearing: true
   (benchmark-list membership decisions rest on it until the census lands).
   Resolution path: b-cov-smol census output per benchmark.
2. **STIPULATED — harness-fidelity anchor tolerance.** Claim: own-harness model-alone
   within ±2.0 pp of the published SmolLM2 card number on variant-matched (model,
   benchmark) cells is the anchor-validity gate for any LB-SMOL run; failure = 
   instrument investigation before interpretation. Maintainer may reset the constant
   at freeze. Owner: experiment-designer. load_bearing: true (question (c) rests on
   it). Resolution path: the anchor reproduction itself measures it per cell.
3. **EXTRAPOLATION (load_bearing: false) — coding-benchmark checkability ≈ 0.** Claim:
   at current code-v0 concepts + kot-query-code/1 grammar, the fraction of
   HumanEval/MBPP/SWE-Bench-Pro-public items containing any kernel-checkable
   proposition is expected ≈0. Never a premise; motivates census-first ordering only.
   Resolution path: the G-CODE-0 code-bench census (Tier 0, ~$0).

## 4. Recommended actions (ordered, costed — maintainer sign-off list)

1. **b-cov-smol census** over the pinned SmolLM2 nine (§1.6): Tier 0, ~$0, CPU, no
   gate. Establishes the per-benchmark κ baseline trajectory point. Complements (does
   not touch) bead kernel-of-truth-hu10's define-lane.
2. **G-CODE-0 code-bench census** over HumanEval/MBPP/SWE-Bench-Pro-public (§2.4):
   Tier 0, ~$0. Converts the coding-checkability extrapolation to MEASURED.
3. **Register the three assumptions** (§3) + kb-sync (coordinator).
4. **a5-nl run** (already designed, ~$10, no GPU) when the runner lane is free — the
   coding track's G-CODE-1 and also feasibility-synthesis's ranked item 5.
5. **LB-SMOL records**: design work begins only when LB-GATE inputs move (f2b-transfer
   readout or a first non-zero census yield); LB-SMOL-NOREG wakes only on an always-on
   mechanism's rung PASS. No GPU spend on any suite benchmark before then.
6. **lit-report extension** (`reports/lit-eval-benchmarks.md`): the §1.1/§2.1 fact
   sheets move from source-verified to lit-reported before any record premises them;
   includes at-source verification of the SWE-Bench-Verified deprecation post and
   TriviaQA licence resolution.

## Epistemic register (tags relied on in this document)

- MEASURED: feasibility-synthesis §0 null-bound; m0b 0.3542 (corpus/rung/instance-
  indexed, transfers nowhere); d-ext lemma-touch 2,903/5,957 vs checkable 0/500 +
  byte-identical off-slice (data/d-ext/manifest.json, registry/assessments/
  f2b-replicate.json); l3a + a5 engine PASSes (audit CONFIRMED, instrument-adequacy
  scope only); f2b-replicate +0.1507 correct-alignment-specific framing.
- LIT-BACKED pending lit-report (source-verified 2026-07-10; §1.1 + §2.1 tables):
  the nine SmolLM2-suite benchmark facts (papers, sizes, licences, metrics) and
  published card scores (HF model cards, lighteval); HumanEval arXiv:2107.03374 (164,
  MIT); MBPP arXiv:2108.07732 (974, CC-BY-4.0); SWE-Bench arXiv:2310.06770; SWE-Bench
  Pro arXiv:2509.16941 (1,865 = 731+858+276, 41 repos, copyleft design); SWE-Bench-
  Verified deprecation by OpenAI 2026-02-23 (secondary coverage; primary post 403 from
  this box — at-source verification is a named lit-report deliverable).
- STIPULATED (registered): ASM-0002 (m0b non-transfer caution); ASM-0007 (a5
  structural-not-NSM concepts); ASM-0026 (NL-boundary record topology). Proposed for
  registration: the three §3 entries.
- EXTRAPOLATION (flagged, never premised): κ expectations before any census (≈0 on
  most suite rows; ≈0 coding-benchmark checkability — §3 entry 3); current SWE-Bench
  Pro SOTA movement (2026 leaderboard coverage; deliberately not premised).
- Not adjudicated here: a5-llm (separate ruling in flight; treated verbatim as
  REFUTE-on-pins, science reproduces); nsk1 (concurrent agent; consumed as designed,
  untouched).
