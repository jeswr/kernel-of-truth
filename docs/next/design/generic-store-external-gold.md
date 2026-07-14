# generic-store-external-gold (id `gsx0`) — does a GENERIC store's verify-retry lift also survive blind EXTERNAL gold?

> STATUS: DESIGN DRAFT — prep only, awaiting coordinator review + review-gate
> (Fable + GPT-5.6) BEFORE any prereg-freeze. No registry record is frozen, no
> GPU/Modal run has been launched, nothing is committed. Authored by the
> Opus experiment-runner role as launch-readiness scaffolding; the DESIGN
> owner for freeze is Fable (Fable/Opus execution split) — this draft is
> input to that, not a substitute. Every claim is tagged **MEASURED**
> (computed from logged/committed data, with ref), **LIT-BACKED**,
> **STIPULATED** (design choice / assumption), or **EXTRAPOLATION** (none
> load-bearing).

---

## 1. The single question this experiment decides

From the knull-v2 + f2b-transfer dual-model reconcile
(`docs/next/analysis/knull-ufo-dual-model-reconcile-fable.md`, Part A,
Divergence 1 — MATERIAL):

- **f2b-transfer** (PASS, audit CONFIRMED 2026-07-11) showed the KERNEL
  store's verify-retry lift **survives blind, gold-label-independent external
  adjudication**: primary effect_size **+0.25067** on externally-adjudicated
  gold, endorsement A = 0.9610 (Wilson LB 0.9395), kill (d) did not fire
  [MEASURED, `registry/verdicts/f2b-transfer.json`, `data/d-adj-t/summary.json`].
- **knull-v2** (NULL / PASS-GENERIC) showed the store powering that mechanism
  is **content-generic on SELF-AUTHORED (membership) gold**: verify-retry
  lifts were kernel 0.2397, plain 0.2477, opaque 0.2357 — TOST-equivalent, and
  the opaque-nonce arm matched the kernel [MEASURED,
  `reports/auto/knull-v2/analysis-output.json`].

The composition licensed by the reconcile: *the mechanism is real and not
definitionally circular, and the store content is interchangeable — an aligned
deterministic answer key, even a nonce one, suffices — on SELF-AUTHORED gold.*
The genuinely open follow-up **neither frozen record tests**, verbatim from the
reconcile:

> **does a PLAIN/OPAQUE (generic, non-kernel) store's verify-retry lift ALSO
> survive the same blind EXTERNAL gold?** If yes, content attribution is fully
> dead on this line even under independent gold; if no, a real content signal
> reappears exactly where knull could not see it.

This experiment answers exactly that, and only that.

**Why knull cannot answer it and f2b-transfer cannot answer it.** knull
scored the plain/opaque arms against each arm's OWN membership gold — the
store's own content, so any aligned answer key wins by construction (the
opaque-nonce match is the proof). f2b-transfer replaced membership gold with
blind external adjudication but ran ONLY the kernel store. The open cell is the
diagonal neither ran: **generic store × external gold.**

---

## 2. Hypotheses and the verdict-enum mapping (equal prominence)

- **H-GT (generic-transfer; the DEFLATIONARY reading, load-bearing):** the
  PLAIN (generic, non-kernel) store's verify-retry lift over model-alone
  survives when item gold is adjudicated independently of the store by blind
  judges (the `data/d-adj-t` protocol re-run on the plain-rendered surfaces) —
  operationalised as absolute superiority of `plain-verify-retry` (fixed k=4)
  over `model-alone` (R1) on plain-externally-adjudicated gold, clearing the
  SAME bar as the f2b-transfer kernel primary. **Support => content-attribution
  is fully dead on this line even under independent gold: a plain dictionary
  transfers as well as the NSM kernel.**
- **H-KC (kernel-content-under-external-gold; the alternative, killed or
  supported symmetrically):** the plain store's lift does NOT survive external
  gold — either blind judges do not endorse the plain store's content on plain
  surfaces (stage-1 kill d), or the plain external-gold system lift does not
  materialise (kill a), while the kernel's did (+0.25067). **Support => a real,
  store-content-specific signal reappears exactly where knull could not see
  it** (knull's membership-gold blindness); the kernel's f2b-transfer PASS
  reflects something a generic store lacks.
- **H-INSTR (the negative-control validity check — OPAQUE store):** blind
  external gold is NOT a rubber stamp; a nonce store's content is NOT endorsed
  by blind judges (opaque endorsement A near option-chance). This is reported,
  never verdict-bearing. Its forecast confirmation (opaque kill d at $0 GPU) is
  what licenses reading a plain PASS as real — without it, "external gold
  endorses everything" is an unrefuted alternative.

**Verdict-enum mapping (kot-reg, equal prominence for all outcomes — the knull
discipline):** the mechanical verdict is *about H-GT for the plain store*.

| mechanical verdict | condition | programme meaning |
|---|---|---|
| FAIL | plain stage-1 endorsement kill (d): A_plain Wilson-LB < 0.70 ($0 GPU) | H-KC (strongest): plain content not blind-endorsed → kernel content distinctive |
| INSTRUMENT-INVALID | any gate fails (adjudication / extraction / engagement / headroom) | no hypothesis is read (RT-7a discipline) |
| FAIL | kill (a) no plain external-gold lift, OR (b) shuffled recovers ≥30%, OR (c) plain-gloss-self closes it | H-GT dead by route a/b/c (assessment reads the route) |
| PASS | primary_reject ∧ Holm(shuffled_low_recovery) ∧ Holm(beats_gloss_self_verify) | **H-GT: the generic store transfers → content-attribution dead under external gold** |
| NULL | TOST equivalence of plain-verify to plain-R1-alone (h=0.2) | no lift either way on the plain surfaces (assessment reads with the engagement gate) |
| INCONCLUSIVE | catch-all / INCOMPLETE-DATA (stage-1 passed, no stage-2 cells) | lawful intermediate between stages |

A PASS (H-GT) is the deflationary result and gets the SAME prominence as a
FAIL, exactly as knull's NULL did.

---

## 3. Design principle — minimal variant, maximal harness reuse

This is the f2b-transfer experiment with the store swapped from kernel to
generic, run through the identical two-stage machinery. Everything scientific
is carried over byte-for-byte; the ONLY new degrees of freedom are (i) the
store content the verifier consults, (ii) the item surfaces the judges
adjudicate, both of which come from the ALREADY-BUILT, ALREADY-token-matched
knull plain/opaque stores.

Reused verbatim (import, not fork):
- **Runner machinery** — `poc/f2b-transfer/runner/f2bt_runner.py`
  (`KernelVerifier`, `ShuffledKernelVerifier`, `run_alone`,
  `run_verify_retry`, `run_self_verify_retry`, `extract_record`,
  `build_prompt`, dual scoring `score_dual`, the RT-7a `verifier_engagement`
  block, `CellGuard`, `Emitter`, `FlopMeter`). Store injection is the
  knull-proven store swap: point `KernelVerifier` at the store dir
  (`poc/knull/runner/knull_runner.py` — `records_root =
  poc/knull/inputs-v4/stores/{plain-padded,opaque}`, the knull-v2
  verdict-backing v4 stores, §4.1), items already carry `record_path`
  relative to that store.
- **Adjudication protocol** — `data/d-adj-t/PROTOCOL.md` (§4 standards S1–S7)
  VERBATIM, re-run on the plain and opaque surfaces. Judge sourcing, blinding,
  escape hatch, resolution, single-draw immutability: unchanged.
- **Analysis statistics** — the f2b-transfer BCa/Holm/TOST/engagement/headroom/
  separation machinery, carried byte-identical into the pinned stdin analysis
  (§9); the stdin adapter is written verdict-gen-compatible FROM THE START
  (the CLI-only pin defect that killed knull/ufo-check-0 registration is not
  repeated — verified, §9).

New (the only two builds): `data/d-qa-t-plain/` and `data/d-qa-t-opaque/`
item corpora (§4), each with its own blind-adjudication corpus
(`data/d-adj-t-plain/`, `data/d-adj-t-opaque/`).

---

## 4. Corpora and builds

### 4.1 d-qa-t-plain, d-qa-t-opaque (items; built pre-freeze, pinned directly)

**The gsx0 "plain store" = the TOKEN-MATCHED plain dictionary.** The task
requires the generic arm matched to the kernel on *alignment AND token budget*.
knull-v4 ships two non-kernel real-content stores and one nonce store, with
MEASURED token ratios vs the kernel gloss (`poc/knull/inputs-v4/g3-token-band.json`):
`plain-padded` **0.99×** (within the ±10% band — a concise plain dictionary
padded to the kernel's token band by cyclic repetition of its OWN segments,
ASM-1082, no foreign content), `opaque` **1.00×** (token-matched nonce), and
the deliberately-concise `plain` **0.66×** (Option-B ruling ASM-1080 exempts it
from the band). So the **token-matched plain store is `plain-padded`** and it is
the gsx0 deflator store; the arm keeps the name `plain-verify-retry` (its store
content is a plain English dictionary; "padded" names only how it was matched to
the kernel's token budget) [STIPULATED design ruling — the concise-vs-padded
plain-store choice is a design decision, §12 B-1].

**Construction = store injection into the SAME d-qa-t eval skeletons.** For
each of the 360 `data/d-qa-t/items/covered.jsonl` items, hold the skeleton
FIXED (concept, template type, answer slot, distractor/donor concept
coordinates, option-slot layout) and substitute each rendered gloss with that
concept's gloss from the store:
- plain store (deflator): `poc/knull/inputs-v4/stores/plain-padded/<concept>.json`
  — dictionary-register English, zero NSM syntax, linter-gated, token-matched to
  the kernel (0.99×). Claim items are byte-identical plain vs plain-padded
  (manifest-proven), so padding only lengthens def/term-match glosses; surplus
  repetition of a concept's own true content does not break blind identification
  (PROTOCOL §4 S1(a): surplus truth is not error) [STIPULATED].
- opaque store (negative control): `poc/knull/inputs-v4/stores/opaque/<concept>.json`
  (seed-pinned nonce text, token-matched 1.00×).
- a-fortiori robustness option (NOT the primary): the concise `plain` store
  (0.66×) continues knull-v2's headline arm; a shorter store that transfers as
  well is even more deflationary, but it is NOT token-matched, so it is offered
  as an optional secondary, not the requirement-satisfying primary [STIPULATED].

MCQ options: option in slot S becomes the plain/opaque gloss of the concept
whose kernel gloss occupied slot S. Claim items (claim-true/false): the claim
becomes an admissible SEGMENT of the concept's plain/opaque gloss at the same
polarity (the knull plain store guarantees ≥2 admissible ≥15-char segments per
concept). The canonical record the verifier checks is the store record, so
`record_path` resolves under the store dir and the verifier's string-equality
seam operates on store bytes — exactly the knull mechanism.

**Builder scaffold:** derive `data/d-qa-t-plain/build.py` and
`data/d-qa-t-opaque/build.py` from `data/d-qa-t/build-dqat.py` by adding a
store-injection render hook (the SAME skeleton generator + seed →
identical concept-per-slot; only the per-concept rendered text swaps). Do NOT
reverse-engineer skeletons from option text — regenerate from the pinned
generator seed so pairing is exact and robust [STIPULATED design ruling].
Generator seeds, pre-committed verbatim:
`gsx0-plain/1|generic-store-external-gold|20260713` and
`gsx0-opaque/1|generic-store-external-gold|20260713`.

**Build gates (fail-closed, pre-freeze):**
- **G-COVER:** every concept appearing in ANY option/claim of the 360
  skeletons has a store record; missing → `ERR_STORE_COVER` (the knull stores
  cover the same 108 covered concepts, so this should pass, but it is asserted,
  not assumed) [STIPULATED].
- **G-LC8p:** full-prompt-surface disjointness of the plain/opaque surfaces
  from ALL 650 d-qa + 1000 d-qa-r items AND from d-qa-t (the store text
  differs, so this is a fresh check on the re-rendered bytes); counts recorded
  in `leak-check.json` [STIPULATED, LC8-t carried over].
- **G-TOK:** re-run the knull G-3 token-band check ON THE d-qa-t-plain /
  d-qa-t-opaque eval prefix at the pinned SmolLM2-135M tokenizer: mean prompt
  tokens of each token-matched generic surface within ±10% (pre-freeze) / ±20%
  (run-time FLOPs gate) of the kernel d-qa-t surface. knull v4 measured mean
  prompt tokens kernel 110.51 / plain-padded 109.43 (ratio **0.99**, within
  band) / opaque 110.96 (ratio **1.00**, within band) / concise plain 73.2
  (ratio **0.66**, band-exempt by ASM-1085) on ITS skeletons [MEASURED,
  `poc/knull/inputs-v4/g3-token-band.json`]; the same per-concept glosses
  re-rendered on d-qa-t skeletons should reproduce the band, but it is
  RE-VERIFIED on the actual eval prefix, not assumed [STIPULATED]. The concise
  plain arm, if run as the a-fortiori robustness option, has its 0.66× ratio
  metered and disclosed via the F0 FLOPs ledger (`cost_ratio_vs_R3`,
  DESCRIPTIVE), never a PASS/FAIL input — exactly the knull ASM-1085 treatment.
- Pinned at freeze as `pins.corpus_hashes["d-qa-t-plain"]` /
  `["d-qa-t-opaque"]` (kot-corpus-hash/1).

### 4.2 d-adj-t-plain, d-adj-t-opaque (blind adjudication labels; PINNED-AT-INPUTS)

The `data/d-adj-t/PROTOCOL.md` §4 standards VERBATIM (S1–S7, the pre-data
adjudication clarification), applied to the plain and opaque surfaces. Contents
per store: `PROTOCOL.md` (copy), per-judge raw responses, `labels.jsonl`
(`{id, gold_ext|null, undecided, unresolved, votes}`), `summary.json`
(`analysis_input_metrics` — the integers the stage-1 record carries). Each
corpus is hashed AFTER adjudication and the pin filled by ops amendment (fills
a declared PINNED-AT-INPUTS placeholder — allowed; can never touch design
scope).

**Judges (per store):** judge-1 = kernel-naive human (SOLE gold source, as in
the f2b-transfer run); judge-2 = blind LLM judge (GPT-5.6-sol via `codex`,
temperature 0, pinned prompt, item text only — the f2b-transfer sourcing);
judge-3 = GPT-5.6 tie-break on discordant, resolution rule issue-#9 (resolve to
human iff judge-3 == human, else UNRESOLVED). **Annotator-proxy fast path
(memory #11):** judge-1 may be a GPT-5.6 annotator stand-in for the affirmative
legs with human reconciliation on a private Google Sheet deferred, re-running
on disagreement — but whether judge-1 must be human up front is a
maintainer-judgement call (§12 B-2, surface as a GitHub issue). All sourcing
disclosed in every readout.

---

## 5. Arms, n, eval set (all FRESH final-phase runs under this record's prereg_hash)

Fresh-runs pre-commitment (carried from f2b-transfer): NO logged cell serves as
an arm output; the practice-5 `reuse-check` is run + recorded pre-spend with
the pre-committed decision "proceed-with-reason: fresh-runs pre-commitment".

**STAGE 1 — adjudication instruments ($0 GPU), both stores:**

| arm | role |
|---|---|
| `adjudication-instrument-plain` | PRIMARY stage-1 kill (d): plain endorsement A_plain; FAIL if Wilson-LB < 0.70 |
| `adjudication-instrument-opaque` | REPORTED negative control: opaque endorsement A_opaque (forecast: kill-d fires) |

**STAGE 2 — GPU arms on the PLAIN store surfaces (opaque stage 2 only if
opaque survives stage 1 — a coordinator decision, NOT pre-committed):**

| arm | rung | k | seeds | role |
|---|---|---|---|---|
| `model-alone` | R1 (SmolLM2-135M) | 0 | 0,1,2 | lift baseline + separation + headroom |
| `model-alone` | R3 (SmolLM2-1.7B) | 0 | 0,1,2 | separation gate + non-inferiority reference |
| `plain-verify-retry` | R1 | 4 | 0,1,2 | **THE deflator arm** (generic store; engagement-gated) |
| `shuffled-plain-verify-retry` | R1 | 4 | 0,1,2 | structure-null on the PLAIN store (seed-pinned Sattolo derangement; the one control NOT to cut) |
| `plain-gloss-self-verify-retry` | R1 | 4 | 0,1,2 | RT-2 commodity control at matched budget |

**Dual scoring** (every stage-2 cell): `item_correct_ext` against
`d-adj-t-plain` gold (ALL endpoints) + `item_correct_mem` against plain
membership gold (descriptive contrast only). **In-run extraction counters**
(`n_verify_calls`, `n_extraction_failures`) on the plain-verify cells feed the
store-appropriate extraction gate (§7); the f2b-transfer d-xif P10 gate is
kernel-rendered and CANNOT measure plain surfaces, so it is replaced by knull's
in-run per-arm Wilson-LB extraction gate [STIPULATED — documented deviation].

**n / eval set (frozen verbatim, mirrors f2b-transfer):** each store built at
n_generated = 360; adjudicate all 360; EVAL SET = the first `per_arm_items=250`
externally-labelled (resolved gold_ext, escapes/unresolved excluded) items in
pinned rank order; `eval_floor=200`, below which the runner refuses
(`ERR_EVAL_FLOOR`). 3 paired seeds, fixed k=4, no sweep. The plain eval prefix
is taken INDEPENDENTLY of f2b-transfer's kernel eval prefix (adjudication
resolution differs by surface), so the primary is a self-contained within-arm
test; item-level pairing to the kernel eval is NOT required for the verdict and
NOT claimed [STIPULATED, honesty note].

**Power:** advisor/P8 carry-over from f2b-transfer — n=250 items × 3 seeds ≈
0.92 one-sided power at absolute Δ=0.10 for the paired primary; the fixed k=4
removes retry-budget selection from the bootstrap; the stage-1 endorsement gate
is powered at n_planned=360 (Wilson LB at expected 0.85 is 0.816 > 0.70)
[STIPULATED, advisor formula from the f2b-transfer design].

---

## 6. The deflator

The word "deflator" has two referents here, both specified:

1. **The deflator ARM = `plain-verify-retry`.** A generic, non-kernel store
   standing in for the kernel in the identical mechanism. If it lifts
   external-gold accuracy as the kernel did, the kernel's f2b-transfer PASS
   carries no store-content-specific credit under independent gold. The
   `shuffled-plain-verify-retry` control ensures any plain lift is
   plain-CONTENT-specific (not retry-STRUCTURE) — so a plain PASS reads as
   "real aligned content, generically sourced," not "any oracle + retry."
2. **The deflator STATISTIC = `kernel_content_premium_ext`** (reported,
   descriptive, NEVER Holm/verdict-bearing):
   `premium = KERNEL_EXT_LIFT_REF − plain_ext_lift`, where
   `KERNEL_EXT_LIFT_REF = 0.25066666666666704` is the FROZEN f2b-transfer
   primary [MEASURED, `registry/verdicts/f2b-transfer.json`]. Reported with the
   plain-arm bootstrap CI on `plain_ext_lift` and `tost_equiv_to_kernel_ref`
   (|premium| within ±0.05, both 95% CI ends inside). When the primary clears
   the bar AND the premium straddles 0, the deflation is licensed: **the NSM
   kernel adds no external-gold premium over a generic plain store.** The
   kernel reference is a fixed constant from a frozen verdict — NOT
   co-resampled — so this is a cross-experiment DIAGNOSTIC, not a paired test
   (disclosed; the verdict-bearing deflation is carried by the primary + the
   shuffled control, both fully within THIS experiment) [STIPULATED].

The complete picture the two stores paint (forecast, NOT a premise):
- On membership gold (knull): even nonce works (opaque ≈ kernel) — membership
  gold IS the store's own content, so any aligned key wins by construction.
- On external gold (this experiment): nonce FAILS (opaque kill-d), plain WORKS
  (≈ kernel) — external gold requires content that actually describes the
  concept, which plain does and nonce does not, but the NSM kernel provides no
  advantage over a plain dictionary.

---

## 7. Endpoints, kills, gates (the frozen contract — mirrors the pinned analysis)

- **PRIMARY (absolute, no denominator, plain external gold):** `effect_size =
  acc_ext(plain-verify-retry, k=4) − acc_ext(R1-alone)`; seed-averaged
  per-item means on the 250-item plain-external-gold eval set; paired item BCa
  bootstrap, B=10000, PRNG seed 20260713; reject iff one-sided 95% BCa lower
  bound > 0 (superiority at margin 0). SESOI for the NULL branch: Cohen's
  h = 0.2 (TOST vs R1-alone). **This is the f2b-transfer primary bar applied to
  the generic store.**
- **Kills:** (d) STAGE-1, pre-GPU — A_plain Wilson-LB < 0.70 ⇒ FAIL, $0 GPU
  (plain content fails blind external adjudication → H-KC); (a) primary fails
  ⇒ the generic lift does not transfer; (b) `shuffled-plain` recovers ≥30% of
  the external-gold lift (point) ⇒ structure-not-content; (c)
  `plain-gloss-self-verify` closes as much at ≤ matched FLOPs/query (F0 ledger,
  point) ⇒ commodity-verification kill. Nulls require TOST (h=0.2 vs R1-alone).
- **Instrument gates (INSTRUMENT-INVALID, never FAIL/PASS):**
  - **adjudication (G-adj, plain):** n_adjudicated ≥ 300, unresolved ≤ 15%,
    raw two-judge agreement ≥ 0.80.
  - **extraction (in-run, plain-verify calls):** pooled Wilson-LB of extraction
    success over the plain-verify verify calls ≥ 0.90 (equiv. failure Wilson-LB
    ≤ 0.10); a missing `n_verify_calls`/`n_extraction_failures` block is itself
    a gate failure (fail closed).
  - **engagement (RT-7a, summed over plain-verify cells):** decidable_fraction
    ≥ 0.95, attempt-0 rejection rate ∈ [0.05, 0.95], ≥ 1 final ≠ attempt-0; a
    missing `verifier_engagement` block is a gate failure.
  - **headroom:** acc_ext(R1-alone) ≤ 0.85.
- **Separation gate (plain external gold; gates ONLY the R3 secondary):**
  acc_ext(R3-alone) − acc_ext(R1-alone) ≥ 0.05 AND one-sided 95% BCa LB > 0; on
  failure `noninferiority_vs_r3` leaves the Holm family BEFORE any p-comparison;
  the primary always reads.
- **Holm family F-secondary(gsx0), membership pre-declared:**
  `beats_gloss_self_verify`, `shuffled_low_recovery` (ub95 < 0.30), plus —
  conditional on the separation gate — `noninferiority_vs_r3` (plain-verify
  external-gold acc non-inferior to 1.7B-alone at margin 0).
- **Reported-only (never Holm, never verdict-bearing):** A_plain + CI;
  A_opaque + CI + opaque_stage1_fail (the H-INSTR control); dual-scoring
  contrast `lift_mem − lift_ext` + transfer_ratio; `kernel_content_premium_ext`
  + CI + `tost_equiv_to_kernel_ref` (the deflator statistic); seed-sign (3/3);
  cost_ratio_vs_R3 (F0).
- **Verdict rules (ordered, first match wins):** 1 INSTRUMENT-INVALID on G-adj
  failure → 2 FAIL on stage-1 endorsement kill (evaluable from the stage-1
  record alone) → 3 INSTRUMENT-INVALID on extraction/engagement/headroom → 4
  FAIL on kills a–c → 5 PASS iff primary ∧ Holm(shuffled_low_recovery) ∧
  Holm(beats_gloss_self_verify) → 6 NULL on TOST → 7 INCONCLUSIVE. Stage-1-
  passed-no-GPU yields INCOMPLETE-DATA (fields unset, fail closed).

---

## 8. What a PASS / FAIL removes (extrapolation envelope — binding, verbatim on freeze)

2 host rungs license a SIGN, not a slope; every claim is scoped to ≤1.7B
hosts, the kernel-covered SELF-AUTHORED templated definitional-QA family over
the same 108 covered concepts, the fixed k=4 budget, and THIS gold standard —
blind dual-judge external adjudication under the `data/d-adj-t` protocol re-run
on the generic surfaces, judge panel and sourcing disclosed. Coverage
disclosure (mandatory, verbatim): kernel-expressibility coverage 0.3542 at rung
molecules-v0 — MEASURED by m0b on one incomplete kernel-v0 instance, NOT
general coverage; every accuracy claim is bounded to the kernel-covered slice.

- A **PASS (H-GT)** licenses: *on this line, a generic aligned real-content
  store (plain dictionary) transfers to blind external gold as well as the NSM
  kernel — kernel-content attribution is dead even under gold-label
  independence.* It does NOT license: any statement about the KERNEL being
  worse (the premium is descriptive); external question-STYLE ecological
  validity (public-benchmark surfaces remain unmeasured — the deterministic
  verifier cannot engage them, MEASURED in f2b-replicate's d-ext slice); any
  coverage-general claim; any PRM comparison; any slope or >1.7B effect size.
- A **FAIL by kill (d)/(a)** licenses: *a store-content-specific signal
  survives external gold for the kernel but not for a generic plain store at
  this scope* — routed to the assessment with the firing route disclosed. It
  does NOT license kernel-content-in-general or transfer claims.
- The **opaque control** (H-INSTR): opaque kill-d confirms external gold
  detects non-content; opaque NOT killing would itself be a finding (external
  gold too permissive) and is disclosed.

Nothing here amends knull-v2 or f2b-transfer: their frozen verdicts, envelopes,
and assessments stand exactly as issued; this record tests the residual the
reconcile foregrounded.

---

## 9. The pinned analysis (verdict-gen-compatible stdin adapter — BUILT + VERIFIED)

`analysis/generic_store_external_gold_stdin.py` (this repo, uncommitted draft).
Written stdin-conformant from the start — the exact defect that blocked
knull/ufo-check-0 (argparse-required `--run-records`/`--sidecar` flags, which
`tools/registry/verdict-gen.py` step 5 cannot supply because it pipes eligible
records as JSONL on STDIN with NO argv) is NOT present. Confirmed against the
verdict-gen invocation (`subprocess.run(["nice","-n","10",python,script],
input=<eligible+reused JSONL>)`, verdict-gen.py:541).

- **Input:** eligible run records (event=="run", phase=="final", exit=="ok")
  as JSONL on stdin; per-cell records carry their own item vectors
  (`metrics.item_correct_ext/_mem`) — the f2b_transfer.py pattern, so no
  materialised campaign file / `metrics.rows` carrying is needed.
- **Statistics:** carried byte-identical from `analysis/f2b_transfer.py`
  (BCa paired-item bootstrap, Holm step-down, TOST on Cohen's h, engagement,
  separation, headroom); added: the opaque endorsement control, the in-run
  extraction gate, and the deflator (`kernel_content_premium_ext` +
  `tost_equiv_to_kernel_ref`).
- **Output:** canonical JSON on stdout with exactly the 64 `OUTPUT_FIELDS`
  (the `pins.analysis_script.output_fields` to freeze).
- **Fixture:** `--selftest` — HAND-COMPUTED point values asserted at every
  branch (adjudication both stores, extraction pass/fail/missing, engagement
  vacuity + missing-block, kills a/b/c, separation-drop, headroom-saturation,
  deflation branch where plain lift == kernel ref ⇒ premium≈0 ⇒ equiv true).
  **`--selftest` passes; a 15-cell stdin dry-run emits valid JSON covering all
  64 fields with 0 stderr** (verified this session).

The frozen record pins this file's sha256 in
`pins.analysis_script` alongside `output_fields`; `/pins/analysis_script` is
DESIGN_SCOPE and un-amendable post-freeze, so the stdin conformance MUST be
correct at freeze (it is).

---

## 10. Cost plan and GPU/Modal estimate [STIPULATED — dry-plan estimates, never measurements]

Anchors: f2b-replicate measured full run 0.604 GPU-h ≈ $1.27 (20 cells × 750
items incl. PRM/text); f2b-transfer stage-2 estimate ≈ 0.25 GPU-h ≈ $0.55 (15
cells × 250 items, no PRM/text/d-ext) [MEASURED / STIPULATED, f2b-transfer §9].
gsx0 stage 2 = the SAME 5-arm × 3-seed × 250-item plain run (15 GPU cells), no
PRM/text/d-ext ⇒ same order as f2b-transfer stage 2.

- **Stage 1 (adjudication, $0 GPU):** judge-2 GPT-5.6 LLM ≈ $1–3 per 360-item
  store × 2 stores ≈ $2–6; judge-3 tie-breaks ≈ $1–2; judge-1 human ≈ 2 h/store
  ≈ 4 h total (OR the memory-#11 GPT-5.6 annotator-proxy fast path ≈ +$3–6 LLM
  with deferred human reconciliation). LLM-judge subtotal ≈ $5–14.
- **Stage 2 (GPU, plain only):** point ≈ 0.25 GPU-h ≈ $0.55; worst case (2×
  overhead) ≈ 0.6 GPU-h ≈ $1.30. If opaque ALSO survives stage 1 (forecast: it
  will not — kill d), add one more plain-sized run ≈ +$0.55–1.30.
- **All-in point estimate ≈ $6–10; worst case (opaque survives + overhead) ≈
  $16.** Proposed caps: `usd_cap` **$20**, `gpu_hours_cap` **4 h**,
  `wall_clock_cap_hours` **24 h**, Tier-1 `tier_cap_usd` **80** — an order of
  magnitude inside the <$100 auto-authorization envelope, and the design can
  FAIL for ~$0 (opaque) or ~$5 LLM (plain kill-d) at stage 1.
- Infra: `modal`, single GPU (A100-40GB or A10G), concurrency_cap 5, foreground
  gates — the f2b-transfer image is already built + Modal-smoked; same pinned
  model revisions (`SmolLM2-135M@12fd25f7`, `SmolLM2-1.7B@31b70e2e`).
- Agent effort: two store-injection builders + 2× adjudication rounds + runner
  store-swap adaptation ≈ 1–2 agent-days.

---

## 11. Execution checklist (post-sign-off; Opus runner, practices 1–5)

1. Confirm the knull-v2 frozen plain/opaque store version + pin (B-1); commit
   `data/d-qa-t-plain/build.py`, `data/d-qa-t-opaque/build.py` (seeds §4.1
   verbatim); build both; G-COVER + G-LC8p + G-TOK must pass fail-closed;
   `corpus-pin` both.
2. Write the d-qa-t-plain / d-qa-t-opaque pins into the DRAFT record; write the
   analysis sha + output_fields pin; `prereg-freeze --experiment gsx0`; post
   frozen_sha256 to the coordination issue (RT-15).
3. Run §4.2 adjudication on BOTH stores (protocol verbatim); assemble
   d-adj-t-plain / d-adj-t-opaque; `corpus-pin`; ops amendment fills the pins;
   append the two stage-1 adjudication-instrument final-phase records.
4. verdict-gen: if plain kill (d) → stop, Codex audit, done ($0 GPU). If
   INCOMPLETE-DATA (plain stage-1 passed) → proceed for the plain store.
5. Pre-spend: `reuse-check` (record; pre-committed fresh-runs decision),
   dry-plan vs caps, mock run of the adapted runner.
6. Stage-2 GPU run (plain; single A100/A10G, foreground gates, cap 5); append
   final-phase records; verdict-gen; Codex GATE-A audit; then Fable
   interpretive assessment; the coordinator routes both the design (now) and
   the interpretation (later) through the GPT-5.6 review gate.

---

## 12. Freeze-readiness and blockers (what the coordinator must do)

**READY now (this prep produced):** the design (this doc); the pinned analysis
`analysis/generic_store_external_gold_stdin.py` (stdin-conformant, self-tested,
all 64 output_fields verified through the verdict-gen stdin path). The runner
adaptation is a mechanical store-swap of two proven harnesses (f2bt_runner +
knull store injection) with two small additions (in-run extraction counters +
the plain arm names) — spec'd in §3/§5/§7.

**BLOCKERS before freeze:**
- **B-1 (store-variant selection + pin — the one real plain-store design
  call):** the knull-v2 verdict-backing store tree is `poc/knull/inputs-v4/`
  (manifest sha256 `ae52862d9f95c83238230ed555628318140f69f9c456eb95fc82b25fcac2ebfe`,
  plain source `plain-authored.json` v4.0.0 sha256
  `97609abe17f87e10a384950a5d69d4e579e40935109573eaf782095bcb43c0d2`) [MEASURED
  + VERIFIED this session against the files and
  `registry/experiments/knull-v2.json` pins.harness_manifest]. Two lawful plain
  deflator stores exist: **`plain-padded` (0.99×, token-matched — RECOMMENDED
  primary**, satisfies the task's "matched token budget" requirement) vs the
  concise **`plain` (0.66×, NOT token-matched but continues knull-v2's headline
  arm, a-fortiori)**. This design defaults to `plain-padded`; the final choice
  (padded-only / concise-only / both) is a design-owner decision for Fable +
  maintainer sign-off (surface as a GitHub issue). `opaque` (1.00×) is the
  endorsement negative control either way. Pin the chosen store dirs exactly at
  freeze; the store bytes are load-bearing (they define both the verifier seam
  and the adjudicated surfaces).
- **B-2 (maintainer judgement — GitHub issue):** must judge-1 be a
  kernel-naive HUMAN up front (as in the f2b-transfer run), or is the memory-#11
  GPT-5.6 annotator-proxy fast path acceptable with deferred human
  reconciliation? Affects cost + timeline, not the design. Surface as a
  threaded issue on `jeswr/kernel-of-truth` (one decision, options + rec).
- **B-3 (build implementation):** the two store-injection builders are SPEC'd
  (§4.1) but NOT written — deriving them from `build-dqat.py` with a render
  hook is ~half a day and must reproduce identical skeletons + pass G-COVER/
  G-LC8p/G-TOK. Runner adaptation (§3) likewise spec'd, not written.
- **B-4 (opaque stage-2 policy):** decide whether opaque stage-2 GPU is
  pre-committed (forecast says opaque dies at stage-1 kill-d, so leaving it
  coordinator-conditional keeps the design minimal). Recommended:
  coordinator-conditional (run opaque stage 2 ONLY if opaque unexpectedly
  survives stage 1).
- **B-5 (review gate):** this design + the analysis must pass the standing
  GPT-5.6 + Fable review gate BEFORE the coordinator commits/freezes (memory:
  GPT-5.6 review gate).

**NOT blockers (settled):** stdin conformance (done — verified through the
verdict-gen path, full 15-cell run resolves all 64 output_fields, rc 0, no
stderr); statistics (carried byte-identical from the audit-CONFIRMED
f2b-transfer analysis); token-budget matching for the RECOMMENDED stores (knull
G-3 v4 MEASURED plain-padded 0.99× and opaque 1.00× within the ±10% band;
re-verified at build, not re-designed — the concise 0.66× plain is band-exempt
and only a robustness option, B-1); cost (well within caps).

**SCIENTIFIC RISKS (fail-safe, not freeze blockers — but launch-readiness
caveats the coordinator must weigh, and check at mock/pilot before the full
spend):**
- **R-1 (headroom on the easy plain surfaces — the sharpest risk).** Plain
  dictionary surfaces are markedly easier than kernel-rendered ones: knull
  MEASURED 1.7B-alone at **0.948 on plain surfaces** vs 0.691 kernel / 0.512
  opaque, and the f2b form-effect existed ONLY where the surface depressed the
  host's baseline [MEASURED, reconcile doc Part A, Divergence 3]. If
  135M-alone on plain external gold exceeds the 0.85 headroom cap, the run is
  **INSTRUMENT-INVALID** (a saturated baseline measures no lift) — GPU spent for
  no hypothesis read. The headroom gate makes this fail SAFE (never a false
  PASS/FAIL), but the run can still be uninformative. MITIGATION: measure
  135M-alone headroom on the plain eval prefix at the mock/pilot before the
  final run; if saturated, the plain surfaces cannot adjudicate the question at
  this rung and the coordinator should stop pre-spend. This risk is materially
  larger for gsx0 than it was for f2b-transfer (kernel surfaces left 135M-alone
  near 0.5).
- **R-2 (endorsement of the padded surface).** A_plain on `plain-padded`
  surfaces (own content with cyclic-repeated segments) is forecast high (real
  dictionary content, PROTOCOL §4 S1(a) surplus-truth rule), but the repetition
  is a novel adjudication surface not previously blind-judged; A_plain is
  measured at stage 1 for $0 GPU and kill (d) fires there if it is not — no GPU
  is at risk, but a surprise low A_plain would read as H-KC and should be sanity
  read against the concise-plain A before concluding.

---

## 13. Governance self-check (design-agent governance rules)

- **Mechanics tagged:** every claim carries MEASURED / STIPULATED / LIT-BACKED /
  EXTRAPOLATION; no EXTRAPOLATION is load-bearing. ✓
- **STIPULATED-not-MEASURED for choices:** all design rulings (store version,
  seeds, eval prefix independence, extraction-gate deviation, opaque-conditional
  stage 2, deflator-as-diagnostic) are tagged STIPULATED, not asserted as
  measurements. ✓
- **ASMs to register at freeze (register-ASM-with-commit — cannot commit in
  prep):** ASM-gsx0-1 plain-store-quality (a linter-gated plain dictionary is a
  faithful ordinary-meaning surface); ASM-gsx0-2 skeleton-injection preserves
  alignment + token band; ASM-gsx0-3 the kernel_content_premium cross-
  experiment diagnostic is descriptive-only (kernel ref not co-resampled);
  ASM-gsx0-4 plain eval prefix taken independently of the kernel eval prefix.
  Each to be registered with the freeze commit. ✓ (listed, not yet registered —
  prep constraint)
- **No @handle account strings:** none present. ✓
- **Mandatory self-check gate:** this section. Design is internally consistent
  with the frozen f2b-transfer contract it mirrors; no frozen record is edited.
  ✓
