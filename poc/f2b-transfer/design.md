# f2b-transfer — design note + pre-registration text (prereg_doc for registry/experiments/f2b-transfer.json)

> STATUS: DESIGN, awaiting maintainer sign-off. No GPU, no spend, no
> execution has occurred. f2b-transfer is auto-authorized under $100 ONLY
> after (design + maintainer sign-off); this note is the decision package.
> Designed by FABLE (design owner per the Fable/Opus execution split);
> execution after sign-off is Opus-runner work under
> docs/next/opus-execution-practices.md practices 1–5.

Every claim below is tagged **MEASURED** (computed from logged/committed
data, with backing ref), **LIT-BACKED**, **STIPULATED** (design choice /
assumption), or **EXTRAPOLATION** (none load-bearing).

## 1. The question this experiment — and only this experiment — decides

f2b-replicate PASSED (audit-confirmed; `registry/verdicts/f2b-replicate.json`)
and its shuffled-derangement control showed the verifier lift is
kernel-CONTENT-specific (shuffled recovery −0.021 point, ub95 0.108 < 0.30)
[MEASURED, that verdict]. The sharpest residual, verbatim from the
interpretive assessment (`registry/assessments/f2b-replicate.json`,
does_not_license): **content-specificity ≠ ground-truth independence**. The
verifier accepts iff the answer string-equals the canonical record, and
d-qa/d-qa-r gold answers were **DEFINED by that same equality**. Under BOTH
the real-semantics reading AND the definitional-circularity reading, a
derangement destroys the lift — so no control run against self-defined gold
can separate them. The two live hypotheses:

- **H-TRANSFER (real content):** the kernel records carry semantic content
  that is true of the covered concepts as externally understood; steering a
  model toward record-consistent answers therefore raises accuracy against
  ANY honest gold standard, not just the kernel's own.
- **H-CIRC (circularity):** the records are an arbitrary-but-self-consistent
  codebook; the lift exists only because gold was defined as codebook
  content. Against externally-fixed gold, steering toward the codebook buys
  nothing (and hurts wherever the codebook is wrong).

Separating them requires items whose gold labels are fixed **independently of
the kernel's string-equality** while the verifier remains **decidable** (able
to engage) on them. Both properties at once are the whole design problem —
see §2.

## 2. Item source — and why the "public benchmark slice" form of RT-7a cannot adjudicate this

**The deterministic verifier cannot engage with externally-authored text.**
`KernelVerifier.check()` accepts a def-match/term-match option iff its text
string-equals a canonical record's gloss, and a claim iff it string-equals a
record segment (poc/f2b/runner/f2b_runner.py). Externally-authored option
texts are never byte-equal to NSM-style canonical glosses, so on any public
benchmark item the verifier either abstains off-coverage or rejects
everything — in both cases the retry loop degenerates and no lift is
mechanically possible **under either hypothesis**. This is not conjecture:

- [MEASURED] In F2, `ext_vector()` bypassed the pipeline entirely — the
  RT-7a secondary compared alone-vs-alone (p = 1.0 vacuously;
  poc/f2/f2b-reanalysis.md §3, code cause named).
- [MEASURED] In f2b-replicate the pipeline defect was fixed, and the d-ext
  (OpenBookQA) slice ran through the verify arm's own retry pipeline — and
  the verify-arm external vectors are **byte-identical** to the model-alone
  external vectors at every seed (acc 0.242 = 0.242, 0 flips, seeds 0/1/2;
  results-log/f2b-replicate.jsonl), because all 500 d-ext items are
  `kernel_checkable = false` by construction and the verifier abstains on
  100% of them. The instrument ran and was *degenerate by item construction*,
  exactly as the frozen record's assumption predicted.

So a run on OpenBookQA/MMLU-style items would produce a no-lift outcome that
is **over-determined** — attributable to checkability/coverage failure just
as well as to circularity — and would adjudicate nothing. Right-sizing
demands we not spend on an arm whose outcome is fixed in advance under both
hypotheses [STIPULATED design ruling; the two MEASURED bullets above are its
evidence].

**What breaks the circularity instead: externally-ADJUDICATED gold over
kernel-checkable items.** The circularity confound lives in one specific
place: *who fixes the gold label*. On d-qa/d-qa-r, gold := canonical-record
content — gold and verifier-acceptance are the same function by definition.
f2b-transfer keeps the item surface kernel-checkable (so the verifier
demonstrably engages — gated, §6) and replaces the gold-definition step with
**blind human adjudication**: judges who have never read the kernel records
answer each item from their own competence with the covered everyday
concepts (bird, eat, sleep, water, …), with a mandatory "cannot-say /
none-of-these" escape. External gold is then fixed by ordinary speakers'
understanding of the concepts — the same external authority that fixes the
answer keys of crowd-authored benchmarks — and NOT by the kernel:

- Under H-TRANSFER, blind judges endorse the kernel's content (they pick the
  concept's own gloss in def/term-match items; they affirm own-record claims
  and reject donor claims), so external gold ≈ membership gold and the
  verifier lift survives re-scoring.
- Under H-CIRC, an arbitrary codebook's glosses do not describe the concepts;
  judges pick "cannot-say" or scatter (all options are kernel-rendered, so
  register/style cannot cue the "intended" answer — style is constant across
  options and across claim polarities by construction), external gold
  decouples from membership gold, and steering toward the codebook cannot
  raise external-gold accuracy.

The decisive quantity has two layers, and the design measures both:

1. **Stage 1 — endorsement (adjudication, ~$0 GPU):** A = share of resolved
   adjudications where blind external gold equals membership gold. H-CIRC
   predicts A near option-chance/claim-base-rate; H-TRANSFER predicts A high.
   A pre-registered kill (§7 kill d) fires on low A **before any GPU spend**.
2. **Stage 2 — system transfer (GPU, ~$1–3):** the arms of f2b-replicate
   (minus the settled ones) re-run FRESH on the externally-labelled items,
   every cell dual-scored against external and membership gold. The primary
   is the verifier lift **on external gold**. This is the deployment-facing
   number: retry dynamics on the judge–kernel disagreement set are not a
   pure function of A, and promotion of verifier-offload beyond the
   self-authored slice requires the measured system-level result, not an
   inference from A [STIPULATED: measure, don't extrapolate].

**Scope honesty (what this does NOT cover):** the item *surface* stays
templated definitional QA over the 108 covered concepts. f2b-transfer
removes the gold-definition circularity — the confound f2b-replicate
foregrounded — NOT the template-style or benchmark-ecology questions (those
remain the separate f2b-template-style stub and the coverage-growth line;
the assessment lists them as distinct questions_opened). The envelope (§8)
binds this verbatim.

## 3. Corpora

### 3.1 d-qa-t (items; built pre-freeze, pinned directly)

- Generator: `data/d-qa-t/build-dqat.py`, derived from the committed
  `data/d-qa-r/build-dqar.py` (same four item templates, same 108 covered
  concepts, same canonical-record rendering contract, same fail-closed leak
  machinery; NO LLM authors, selects, or edits any item text) with a
  RE-AUTHORED per-concept item plan sized to exactly n=360. This resolves the
  20260709T164008Z boundary stop (bead kernel-of-truth-voc): the d-qa-r plan
  structurally emits 9–10 items/concept ([972, 1080] over 108 concepts), so
  no seed-and-count change can reach 360 — the COUNT stays (it carries the
  stage-1 endorsement power at n_planned=360, the G-adj n≥300 floor, the
  ~2 h/judge effort estimate, and the 250-item eval prefix + exclusion slack)
  and the PLAN moves [STIPULATED design ruling; resolution (a)].
- Per-concept plan (availability-aware): every concept draws **t1**
  def-match, **t2** term-match (LC1-substituted to def-match where the gloss
  contains the headword), and **t3** a TRUE-preferring claim (claim-true from
  the concept's own gloss where a fresh admissible segment remains under
  LC8-t, else substituted to claim-false, counts recorded); a 36-concept
  fourth-item subset (**t4**, same TRUE-preferring claim) prioritises
  concepts still holding a fresh segment after t3, then fills by seeded hash.
  3·108 + 36 = 360. WHY availability-aware [MEASURED, reproducible from the
  committed corpora]: d-qa + d-qa-r already consumed most claim-true prompt
  surfaces — only 57 fresh gloss segments over 43 concepts remain (65
  concepts have zero) — so a d-qa-r-style seeded-parity plan builds
  28 yes / 116 no claims and ABORTS on LC7's yes/no ≤ 0.75 bound, while this
  plan builds 56 yes / 88 no (no-share 0.611) and passes with margin. LC7
  (yes/no balance and answer-position balance) remains the fail-closed
  authority on the built counts; the claim-yes base rate is disclosed in
  `data/d-qa-t/leak-check.json`.
- **Generator seed, pre-committed verbatim here: `dqat/1|f2b-transfer|20260710`.**
  Single-draw rule: one build, one adjudication round. Any re-draw or
  re-adjudication requires a correction record under
  `registry/corrections/f2b-transfer/` BEFORE the freeze (after the freeze it
  is a new experiment id). This forecloses drawing items until Stage 1
  passes.
- n_generated = 360 items, ID namespace `dqat:`, pinned `rank` order, types
  as drawn by the generator (def-match / term-match / claim-true /
  claim-false), all `kernel_checkable = true`.
- Leak rule **LC8-t** (fail-closed at build): full-prompt-surface
  disjointness from ALL 650 d-qa items AND all 1000 d-qa-r items
  (cross-set references pinned in the d-qa-t manifest; substitution counts
  recorded in `data/d-qa-t/leak-check.json`).
- Pinned at freeze as `pins.corpus_hashes["d-qa-t"]` (kot-corpus-hash/1).

### 3.2 d-adj-t (blind adjudication labels; PINNED-AT-INPUTS, filled by ops amendment before Stage 1)

Contents: `PROTOCOL.md` (verbatim copy of §4 below), per-judge raw response
files, `labels.jsonl` (one line per item: {id, gold_ext | null, undecided |
unresolved flags, judge votes by pseudonym}), `summary.json` (the counts the
Stage-1 record carries). The whole corpus is hashed AFTER adjudication
completes and the pin is filled by ops amendment (it fills a declared
PINNED-AT-INPUTS placeholder — allowed; it can never touch design scope).

## 4. Adjudication protocol (FROZEN with this note — the record pins this file's sha)

1. **Judges.** Two blind judges + a tie-break adjudicator, all recorded as
   pseudonyms (judge-1, judge-2, judge-3; RT-14 — no names/emails anywhere in
   hashed bytes). judge-1 MUST be a human who has never read any
   kernel-v0/molecules-v0 record. judge-2: a second such human if available;
   **pre-declared fallback** (E5 leak-checked-judge discipline): the
   cross-vendor Codex/GPT-5.5 model via the `codex` CLI, temperature 0,
   pinned prompt stored in d-adj-t, shown ONLY the item text below (a
   different vendor from both the host models and the designer — the §8
   auditor-identity rationale). judge-3 (tie-break only): may be the
   maintainer, blind-shuffled, disagreement items only. The judge sourcing
   actually used is recorded in d-adj-t and disclosed in every readout.
2. **Blinding.** Each judge sees, per item, ONLY: the question text and (for
   MCQ) the option texts, in the model's own rendering — never urn,
   record_path, membership gold, type labels, provenance, or which option is
   the kernel's own gloss. Item order is shuffled per judge with a pinned
   permutation seed (`dadjt/1|judge-<n>|20260710`).
3. **Escape hatch (mandatory).** MCQ items offer "NONE of these / cannot
   say"; claim items offer yes / no / cannot-say. Forced choice would
   fabricate agreement under H-CIRC; the escape makes "the kernel's content
   does not describe this concept" expressible. A concordant escape verdict
   makes the item CONTENT-UNDECIDED: it counts as **non-agreement** in the
   endorsement statistic A and is excluded from the Stage-2 eval set — it is
   evidence against endorsement, never an instrument event.
4. **Resolution.** gold_ext(item) = the concordant judge-1/judge-2 label
   (including concordant escape ⇒ undecided). Discordant pairs go to judge-3
   blind; judge-3's label resolves. Still-unresolvable items (judge-3
   escapes where the pair split label-vs-label) are UNRESOLVED — instrument
   events, capped by gate G-adj below.
5. **Order and immutability.** Adjudication completes and `d-adj-t` is
   hash-pinned (ops amendment) BEFORE the Stage-1 record is appended and
   before any GPU cell runs. Labels are never revisited after the pin; the
   Stage-2 runner fail-closes on the pin (ERR_PIN).
6. **Effort** [STIPULATED estimate]: 360 items × ~20 s ≈ 2 h per judge;
   tie-breaks ~15 min; LLM-judge fallback ≈ $1–3 API spend. Within O-3
   patterns (D-IR-N blind adjudication precedent).
7. **Adjudication standards (pre-data clarification; correction 1).** Added
   by `registry/corrections/f2b-transfer/1-prefreeze-correction.json` BEFORE
   any adjudication datum existed (judge-1 not started, judge-2 not run);
   items 1–6 above and the blind item bytes are unchanged. These standards
   define "correctly gives the meaning" (MCQ) and "true of X" (claims) for
   both judges under ONE protocol. Each is the principled reading of
   ordinary-understanding endorsement, chosen so the escape fires exactly
   when the kernel's content does not describe the concept (§2) — never to
   tune A; the A-direction of every rule is disclosed at the end
   [STIPULATED design rulings].
   - **S1 — MCQ correctness = fit + identification.** An option correctly
     gives the meaning iff (a) **fit**: everything it says fits the concept
     as ordinarily understood, each clause read as a typical-case (generic)
     characterization that honors its own hedges ("at some times", "can",
     "many", "some"); AND (b) **identification**: taken as a whole it says
     what the word means — the definitional core is present and picks out
     this concept rather than a different one. A clause TRUE of the concept
     but not needed to define it NEVER disqualifies (surplus truth is not
     error: the kernel's NSM explication style carries prototypical
     non-essential clauses by design, so rejecting them would measure
     lexicographic minimality — a style question §2 scopes OUT — not
     content). A clause FALSE of the concept under the typical-case reading
     ALWAYS disqualifies. Degrees: minor or even dominant surplus with the
     core present → still correct; a pile of true facts that never says what
     the thing is → fails (b) → not correct; any misfitting clause → not
     correct.
   - **S2 — best fit before NONE.** If more than one option passes S1, the
     judge picks the one that best and most specifically gives the meaning
     of the asked word itself, not of a related word (the event of dying is
     not the meaning of "dead"). NONE iff no option passes S1 or the judge
     cannot decide; both readings are one token (§4.3), optionally
     distinguished in the comment field.
   - **S3 — term-match mirror.** The judge picks the word an ordinary
     speaker could be defining with the stem text (the S1 test in reverse;
     extra true clauses in the stem do not break fit). A parenthetical
     attached to a headword or option word ("find (X finds Y)", "right (of a
     doable something)", "kind (gufo:Kind, sortal type)") only disambiguates
     which sense/use of the word is meant; unfamiliar notation inside it is
     ignored beyond sense-picking and is never itself a ground for NONE. If
     the stem fits none of the four words → NONE; if it loosely fits two →
     the better fit.
   - **S4 — claims are judged at the generic standard, about what X means.**
     "According to the definition of X, is S true of X?" asks whether S is
     part of, or directly follows from, what X means as ordinarily
     understood — including X's typical-case picture. **yes**: S holds in
     the normal case / of normal instances ("birds fly"-style; exceptions do
     not make it false), or S's own hedge holds. **no**: S misdescribes X
     (not true even as a typical-case characterization; true only rarely or
     accidentally), OR S has nothing to do with what X means — a statement
     that X's definition neither says nor implies is answered no, including
     statements so generic they say nothing about X in particular. **cannot
     say**: inability only — S cannot be understood well enough to judge
     even charitably, or the judge genuinely cannot decide; never merely
     because S is oddly worded, partial, or only typically true, and never
     as a soft no.
   - **S5 — fragments, deixis, participants.** Claim statements are
     fragments extracted from a longer description: unresolved "this
     someone / this something / these parts / it", stray quote marks
     (quoted-thought fragments), and bracketed clarifiers ("[the bookmark]")
     are read charitably as pieces of a description of X's normal scenario;
     the judged question is whether the fragment could belong to describing
     X. X/Y letters name the participants given with the word's own title
     ("break (X breaks Y)": X breaks, Y gets broken); a statement whose X/Y
     match nothing in what the asked word means is not true of it → no.
   - **S6 — register immunity (reading key).** The deliberately simplified
     register is never a ground for NONE / no / cannot-say: "something of
     kind K" reads as "a K" ("a something of kind event" = "an event";
     "somethings of kind take happen" = "acts of taking happen"). Odd
     grammar is simplification, not error and not a trick. The key is
     constant across all items, options, and claim polarities, so it carries
     zero bits about any answer (§2 style-constancy argument unchanged).
   - **S7 — item independence.** Identical statements recur under different
     words; each item is judged only against its own word, never by pattern,
     recall, or reuse of an earlier answer.
   - **A-direction disclosure [STIPULATED, honest].** Relative to the terse
     pre-clarification judge wording ("close but not quite right → NONE"),
     S1, S4 and S6 RAISE A by removing minimality- and style-driven escapes
     that would fire under BOTH hypotheses (pure noise: under H-CIRC the
     clauses are false/misfitting and S1(a)/S4-no still force the escape or
     the disagreeing label, so no H-CIRC signal is lost). S4's
     irrelevance→no clause raises agreement on donor claims under H-TRANSFER
     AND lowers A under H-CIRC (arbitrary own-record content reads as
     no-against-membership-yes) — sharpening kill (d) in both directions.
     Two honest costs are accepted rather than patched: (i) contentless
     own-record segments lose credit (no / cannot-say against
     membership-yes); (ii) donor segments that genuinely belong to the
     target's meaning (e.g. rabbit ← tree "a living thing of one kind") must
     be answered yes and count as disagreement — an item-construction cost
     of membership gold, disclosed here, not an adjudicator error, expected
     order ~1% of items. No rule conditions on provenance or membership;
     every rule is applicable by a kernel-blind judge from ordinary
     understanding alone.

## 5. Arms (all FRESH final-phase runs under this record's prereg_hash)

Fresh-runs pre-commitment: the logged-result reuse ruling is under revision
at design time, so NO logged cell is consumed as an arm output here. The
practice-5 `reuse-check` is still run and recorded pre-spend; any hit carries
the pre-committed decision "proceed-with-reason: fresh-runs pre-commitment of
the frozen design" [STIPULATED]. Mechanically, the record is kot-reg/2 and
declares a `reuse_overrides` entry (deliberate fresh re-run,
machine-recorded reason) for the six arm × rung cells that collide with
logged f2/f2b-replicate rows — those rows cannot serve here even in
principle: the eval corpus differs (d-qa-t) and every endpoint is scored
against blind external gold (d-adj-t) that exists for no logged row.

| arm | rung | k | seeds | role |
|---|---|---|---|---|
| model-alone | R1 (SmolLM2-135M, pinned) | 0 | 0,1,2 | lift baseline + separation + headroom |
| model-alone | R3 (SmolLM2-1.7B, pinned) | 0 | 0,1,2 | separation gate + non-inferiority reference |
| kernel-verify-retry | R1 | 4 (fixed) | 0,1,2 | THE arm (true records; engagement-gated) |
| shuffled-kernel-verify-retry | R1 | 4 | 0,1,2 | carry-over content control (seed-pinned Sattolo derangement, map recorded) — the one control NOT to cut |
| gloss-self-verify-retry | R1 | 4 | 0,1,2 | RT-2 active-text commodity control at matched budget |
| extraction-instrument | R1 | – | – | P10 gate, CPU-only d-xif re-verification (unchanged) |
| adjudication-instrument | – | – | – | Stage-1 record (counts of §4; $0 GPU) |

**Dual scoring isolates transfer:** every arm cell emits `item_correct_ext`
(external gold — all endpoints) AND `item_correct_mem` (membership gold —
descriptive contrast only). Same runs, same answers, two golds: the only
varying factor between the headline number here and f2b-replicate's is the
gold definition, which is precisely the confound under test.

**Dropped vs f2b-replicate, with reasons:** trained-PRM arm (HC3 is closed at
the 1.5B class and indexed to it; transfer does not reopen that fork),
kernel-as-text (Law-2 passive null settled at this scope; no claim here needs
it), d-ext descriptive slice (measured degenerate, §2 — replaced by this
experiment's entire eval set), R2 / cascades / k-ladder / gold-oracle (already
dropped by the replicate right-size; their F2 readings stand). Eval set 250
items (deterministic prefix of the externally-labelled items in pinned rank
order; floor 200 — below it the runner refuses), 3 paired seeds, fixed k=4:
the advisor P8 sizing carries over (~0.92 one-sided power at absolute
Δ=0.10) [STIPULATED, advisor formula from the replicate design].

## 6. The RT-7a instrument, fixed for real (engagement gate)

The two prior failures were (i) pipeline-bypass (F2) and (ii)
items-not-checkable (f2b-replicate) — both produced a verify arm
byte-identical to alone, silently. The fix is structural, not a promise:

- Items are kernel-checkable **by construction** (d-qa-t), so the verifier
  has no abstention path on the eval set.
- Every kernel-verify-retry cell MUST emit
  `verifier_engagement = {n_items, n_decidable, n_attempt0_rejected,
  n_final_differs_attempt0}`.
- Pre-registered gate `/gates/engagement_valid` (INSTRUMENT-INVALID on
  failure, never FAIL/PASS): decidable_fraction ≥ 0.95 AND attempt-0
  rejection rate ∈ [0.05, 0.95] AND n_final_differs_attempt0 ≥ 1 (summed
  over verify cells). Rate 0 is the F2/d-ext vacuity signature (verify ≡
  alone); rate ~1 with no acceptances is the never-accepts degeneracy; a
  missing engagement block is itself a gate failure (fail closed).

## 7. Endpoints, kills, gates (the frozen contract — mirrors the record verbatim)

- **Primary (absolute, no denominator):** effect_size =
  acc_ext(135M + kernel-verify-retry, fixed k=4) − acc_ext(135M-alone);
  seed-averaged per-item means on the 250-item external-gold eval set;
  paired item BCa bootstrap, B=10000, PRNG seed 20260710; reject iff the
  one-sided 95% BCa lower bound > 0 (superiority at margin 0). SESOI for the
  NULL branch: Cohen's h = 0.2 (TOST vs R1-alone).
- **Kill criteria (verbatim in the record):** (a) primary fails ⇒ the
  verifier lift does not survive ground-truth-independent gold — the
  transfer claim is dead and the circularity reading stands for every
  deployment-facing purpose; (b) shuffled-verify recovers ≥ 30% of the
  external-gold lift (point) ⇒ structure-not-content on external gold;
  (c) gloss-self-verify closes as much external-gold lift at ≤ matched
  FLOPs/query (F0 ledger, point) ⇒ commodity-verification/Law-2 kill;
  (d) **STAGE-1, pre-GPU:** external endorsement A (share of resolved blind
  adjudications agreeing with membership gold; concordant cannot-say counts
  as disagreement) has one-sided 95% Wilson lower bound < 0.70 ⇒ the
  kernel's own content fails blind external adjudication — FAIL with ZERO
  GPU spend. Nulls require TOST (h = 0.2 vs R1-alone).
- **Instrument gates (INSTRUMENT-INVALID, never FAIL):** G-adj adjudication
  instrument (n_adjudicated ≥ 300; unresolved-disagreement ≤ 15%; raw
  two-judge agreement ≥ 0.80); P10 extraction gate (≥300 d-xif labelled,
  failure Wilson-LB ≤ 0.10, unchanged); engagement gate (§6); headroom gate
  (acc_ext(R1-alone) ≤ 0.85 — a saturated baseline cannot measure a lift).
- **Separation gate (external gold; gates ONLY the R3 secondary):**
  acc_ext(R3-alone) − acc_ext(R1-alone) ≥ 0.05 AND one-sided 95% BCa LB > 0;
  on failure `noninferiority_vs_r3` leaves the Holm family BEFORE any
  p-comparison (deterministic function of the alone arms only). The primary
  always reads.
- **Holm family F-secondary(f2b-t), membership pre-declared:**
  beats_gloss_self_verify, shuffled_low_recovery (ub95 < 0.30), plus —
  conditional on the separation gate — noninferiority_vs_r3 (LB ≥ 0 on
  external gold: the efficiency headline re-tested against honest gold).
- **Reported-only (never Holm, never verdict-bearing):** external
  endorsement A with CI; dual-scoring contrast lift_mem − lift_ext with CI
  and transfer_ratio (the circularity-signature diagnostics); seed-sign
  (3/3); cost_ratio_vs_R3 (F0).
- **Verdict rules (ordered; first match wins):** 1 INSTRUMENT-INVALID on
  G-adj failure → 2 FAIL on stage-1 endorsement kill (evaluable from the
  Stage-1 record alone) → 3 INSTRUMENT-INVALID on P10/engagement/headroom →
  4 FAIL on kills a–c → 5 PASS iff primary AND Holm(shuffled_low_recovery)
  AND Holm(beats_gloss_self_verify) → 6 NULL on TOST → 7 INCONCLUSIVE
  catch-all. Stage-1-passed-with-no-GPU-cells yields INCOMPLETE-DATA (fields
  unset — fail closed), which is the lawful intermediate state between
  stages.

## 8. Extrapolation envelope (verbatim in the record; binding on any PASS)

2 host rungs license a SIGN, not a slope; every claim is scoped to ≤1.7B
hosts, kernel-covered kernel-RENDERED templated definitional QA over the 108
covered concepts, the fixed k=4 budget, and THIS gold standard (blind
dual-judge adjudication under the pinned d-adj-t protocol, judge panel
disclosed). What a PASS removes is exactly ONE confound of the f2b-replicate
envelope: gold defined by the kernel's own string-equality. It does NOT
license: external question-STYLE ecological validity (public-benchmark
surfaces remain unmeasured — the deterministic verifier cannot engage them,
measured in f2b-replicate's d-ext slice); any coverage-general claim
(coverage 0.3542 at molecules-v0, MEASURED by m0b on one incomplete
kernel-v0 instance, restated mandatorily); any PRM comparison (HC3 stays
indexed to the 1.5B class of f2b-replicate; no PRM arm here); any slope or
>1.7B effect size (cascade/verification-routing literature licenses mechanism
existence above 7B, never effect size). A FAIL by kill (d) is likewise
scoped: it kills the kernel-content claim at this kernel instance and rung,
not the verify-retry mechanism as such.

## 9. Cost plan [STIPULATED — dry-plan estimates, never measurements]

Anchor: f2b-replicate's measured full run = 0.604 GPU-h, ≈$1.27, single GPU
(run-log 20260709T110510Z), covering 20 cells × (250 covered + 500 d-ext)
items including PRM and text arms. f2b-transfer runs 15 GPU cells × 250
items with no PRM, no text arm, no d-ext slice — strictly less work per cell
and fewer cells:

- Stage 1: $0 GPU; ~2 h × 2 judges human time (or ≈$1–3 cross-vendor LLM
  fallback for judge-2); tie-break ~15 min.
- Stage 2 point estimate ≈ 0.25 GPU-h ≈ $0.55; worst case (2× overhead)
  ≈ $1.10. Registry caps: usd_cap $15, gpu_hours_cap 4 h, wall-clock 24 h
  — an order of magnitude inside the <$100 auto-authorization envelope,
  and the design can FAIL for ~$0 at Stage 1.
- Agent effort: builder (authored and committed pre-freeze; §3.1 plan) +
  adjudication tooling + runner adaptation of poc/f2b (drop arms, add dual
  scoring + engagement block) ≈ 1–2 agent-days.

## 10. Decision table (design-time forecast; the assessment owns post-hoc meaning)

| outcome | mechanical verdict | what it adjudicates |
|---|---|---|
| A low (kill d) | FAIL, $0 GPU | blind judges do not endorse the kernel's content: H-CIRC supported at this kernel instance; verifier-offload promotion beyond self-authored slices is blocked |
| A high, primary + controls pass | PASS | the lift survives ground-truth-independent gold and stays content-specific and better-than-commodity: H-TRANSFER supported within §8's envelope; the circularity confound named by f2b-replicate is closed |
| A high, primary fails | FAIL (kill a) | content externally endorsed but the SYSTEM lift does not transfer — indicts retry dynamics on the disagreement set, not (necessarily) record content; assessment decides the follow-up |
| shuffled recovers ≥30% on ext gold | FAIL (kill b) | any external-gold lift was structure, not content |
| gloss arm closes as much at ≤ FLOPs | FAIL (kill c) | commodity verification suffices on honest gold |
| engagement/headroom/adjudication gates fail | INSTRUMENT-INVALID | instrument events; no hypothesis is read (the RT-7a lesson, enforced) |

## 11. Execution checklist (post-sign-off; Opus runner, practices 1–5)

1. Commit `data/d-qa-t/build-dqat.py` (seed §3.1 verbatim); build; LC8-t
   must pass fail-closed; `corpus-pin` d-qa-t.
2. Write d-qa-t pin into the DRAFT record (replacing its PINNED-AT-INPUTS
   placeholder pre-freeze, or by ops amendment post-freeze — either is
   lawful pre-final-run; pre-freeze is cleaner), then
   `prereg-freeze --experiment f2b-transfer`; post the frozen_sha256 to the
   coordination issue (RT-15).
3. Run §4 adjudication; assemble d-adj-t; `corpus-pin`; ops amendment fills
   the d-adj-t placeholder; append the Stage-1 adjudication-instrument
   final-phase record via log-append.
4. Run verdict-gen: if FAIL (kill d) → stop, Codex audit, done at ~$0. If
   INCOMPLETE-DATA (stage-1 passed) → proceed.
5. Pre-spend: `reuse-check` (record output; pre-committed fresh-runs
   decision), dry-plan vs caps, mock run of the adapted runner
   (poc/f2b-transfer; harness_manifest ops-amended in).
6. Stage-2 GPU run (single A100/A10G, foreground gates, concurrency cap 5);
   append final-phase records; verdict-gen; Codex GATE-A audit; then FABLE
   interpretive assessment (audit-status entry marked pending until then).
