# gsx0 — generic-store-external-gold: PREREG DESIGN (rev-2, freeze contract)

> STATUS: FREEZE CANDIDATE (rev-2). This document is the prereg_doc pinned by
> `registry/experiments/gsx0.json`. It supersedes the DRAFT
> `docs/next/design/generic-store-external-gold.md` (kept as history; the
> GPT-5.6 readiness review `docs/next/analysis/gsx0-readiness-review.md`
> line-refs point there) by applying that review's corrections — the
> per-finding disposition log is §12. Design owner: Fable
> (experiment-designer). Every claim is tagged **MEASURED** / **LIT-BACKED** /
> **STIPULATED** / **EXTRAPOLATION** (none of the last is load-bearing).

---

## 1. The single question, and the NARROWED estimand (review finding 1)

f2b-transfer (PASS, audit CONFIRMED) showed the KERNEL store's verify-retry
lift survives blind, gold-label-independent external adjudication: primary
+0.25067 on externally-adjudicated gold, endorsement A=0.9610 (Wilson-LB
0.9395) [MEASURED, `registry/verdicts/f2b-transfer.json`]. knull-v2 (NULL /
PASS-GENERIC) showed the store content is interchangeable on SELF-AUTHORED
membership gold: lifts kernel 0.2397 / plain 0.2477 / plain-padded 0.2440 /
opaque 0.2357, TOST-equivalent [MEASURED,
`reports/auto/knull-v2/analysis-output.json`]. Neither frozen record tests the
diagonal: **generic store × external gold**.

**gsx0 decides exactly this and only this:** *does a PLAIN (generic,
non-kernel, token-matched) store's verify-retry lift over model-alone come out
POSITIVE when item gold is adjudicated independently of the store by blind
judges (the `data/d-adj-t` protocol re-run on the plain-rendered surfaces)?*

- A PASS licenses: **kernel content is not NECESSARY for a positive
  externally-adjudicated verify-retry lift on this line** — the content-
  attribution diagonal closes on the deflationary side at this scope.
- A PASS does NOT license: "the plain store transfers AS WELL AS the kernel",
  "the kernel-content premium is zero", or any kernel-vs-plain magnitude
  claim. The frozen f2b-transfer +0.25067 is an observed effect, not a
  rejection bar; the kernel-vs-plain magnitude comparison lives ONLY in the
  reported-only premium diagnostic (§7), which treats the frozen kernel point
  estimate as error-free and is therefore a conditional descriptive band. A
  verdict-grade "as well as the kernel" claim would require a concurrent
  matched kernel arm and a difference-in-lifts endpoint — deliberately out of
  scope (cost; portfolio Rank-4 framing), pre-declared as the natural
  successor if the premium band motivates it. [STIPULATED]

**This is not a four-condition kernel-specific result.** It closes the cheap
missing CORRECTNESS diagonal (does the f2b lift belong to grounded-kernel
content or merely to authoritative answer-bearing content?); it does not by
itself provide a structure-sensitive kernel-vs-generic verdict.

## 2. Hypotheses and the verdict mapping (revised; findings 2+3)

- **H-GT (generic-transfer; deflationary, load-bearing):** the plain store's
  verify-retry lift over R1-alone is positive on plain-externally-adjudicated
  gold (one-sided 95% BCa LB > 0 at the fixed k=4), content-specific
  (shuffled control), not commodity verification (gloss-self control), with
  blind judges demonstrably endorsing plain content (stage-1) and demonstrably
  rejecting nonce content (opaque control — PASS-gate-bearing).
- **H-KC (kernel-content-under-external-gold; the alternative):** the plain
  construction fails external adjudication AFFIRMATIVELY — stage-1 one-sided
  95% Wilson UPPER bound of A_plain < 0.70 (FAIL, ~$0 GPU) — or the plain
  system lift is affirmatively absent (TOST equivalence to R1-alone at h=0.2
  ⇒ NULL). Interpretive scope of either negative is bounded by §8 (the
  mandatory concise-plain sensitivity; no kernel-distinctive claim without a
  direct difference test).
- **H-INSTR (opaque negative control, now PASS-gate-bearing):** blind external
  gold is not a rubber stamp. Affirmative rejection = one-sided 95% Wilson
  UPPER bound of A_opaque < 0.70 — the same bar the plain store must clear
  from below (justified ceiling: gold that endorses content at 0.70 must
  demonstrably NOT endorse non-content at 0.70). A PASS REQUIRES a present,
  G-adj-valid, affirmatively-rejecting opaque adjudication; a permissive or
  missing opaque control blocks PASS (INCONCLUSIVE / INCOMPLETE-DATA), never
  FAIL for the plain store.

**Ordered verdict rules (first match wins; frozen verbatim in the record):**

| # | verdict | condition | reading |
|---|---|---|---|
| 1 | INSTRUMENT-INVALID | ¬G-adj(plain) | judge-quality event |
| 2 | FAIL | Wilson-UB(A_plain) < 0.70 | AFFIRMATIVE non-endorsement (H-KC route d′; $0 GPU) |
| 3 | INCONCLUSIVE | Wilson-LB(A_plain) < 0.70 | endorsement not demonstrated — mere non-rejection, never FAIL; stop, $0 GPU |
| 4 | INSTRUMENT-INVALID | ¬headroom (acc_ext(R1-alone) > 0.85) | evaluable at stage 2b-i, before the remaining cells are bought |
| 5 | INSTRUMENT-INVALID | ¬(extraction ∧ engagement) | RT-7a discipline |
| 6 | FAIL | primary_reject ∧ (shuffled recovers ≥30% (point) ∨ gloss-self closes as much at ≤ matched FLOPs) | a REAL lift that is structure-not-content (b) or commodity (c) |
| 7 | PASS | primary_reject ∧ Holm(shuffled_low_recovery) ∧ Holm(beats_gloss_self_verify) ∧ opaque_adjudication_valid ∧ opaque_rejected | H-GT |
| 8 | NULL | TOST equivalence to R1-alone (h=0.2) | affirmative no-lift |
| 9 | INCONCLUSIVE | catch-all | incl. lawful staged intermediates via INCOMPLETE-DATA |

Kills b/c are gated on primary_reject (review finding 3): a kill that
"explains" a lift may only fire when a lift is established; affirmative
absence routes to NULL; mere non-rejection routes to INCONCLUSIVE. A PASS
(deflationary) gets the SAME prominence as a FAIL — the knull discipline.

## 3. Corpora — BUILT, GATED, PINNED (review finding 7)

**Stores [MEASURED, knull-v2 verdict-backing tree `poc/knull/inputs-v4`,
manifest sha `ae52862d…ebfe`, plain source `plain-authored.json` sha
`97609abe…3d2`]:** deflator = `plain-padded` (token-matched plain dictionary,
0.99×); negative control = `opaque` (token-matched nonce, 1.00×). B-1
resolved: padded-only as the requirement-satisfying primary; the concise
`plain` (0.66×, band-exempt) is the MANDATORY post-verdict sensitivity for
negative interpretations (§8), not an arm here. [STIPULATED]

**Construction:** `data/d-qa-t-plain/build.py` builds BOTH
`data/d-qa-t-plain` and `data/d-qa-t-opaque` in ONE deterministic pass —
identical item skeletons across store conditions BY CONSTRUCTION. For each of
the 360 committed d-qa-t skeletons (corpus byte-verified against the frozen
f2b-transfer pin `7179ee…ee27` before any use) the concept/template/answer-
slot/donor/option-layout/rank is held fixed and each kernel gloss is replaced
by the same concept's store gloss. Seeds, pre-committed verbatim:
`gsx0-plain/1|generic-store-external-gold|20260713`,
`gsx0-opaque/1|generic-store-external-gold|20260713`. NO LLM authored,
selected, or edited any item text. Two disclosed rulings [STIPULATED]:

- **RULING G-1 (slot→concept mapping):** exact full-byte gloss match against
  the 108-concept pool, after pool-gloss uniqueness is asserted (108/108
  unique, fail-closed) — equivalent to regeneration (the committed corpus IS
  the pinned generator output), never text-similarity reverse-engineering.
- **RULING G-2 (claim polarity substitution) [MEASURED]:** plain-padded holds
  EXACTLY ONE unique admissible ≥15-char segment per concept (cyclic
  self-padding; the draft's "≥2 segments guaranteed" was wrong and is
  corrected). Rank-order rule: the first claim-true skeleton of a concept
  takes the seeded store segment; a second claim-true skeleton substitutes to
  claim-false (seeded donor, LC3-s-checked), identically in BOTH store
  corpora. Realised: 13 items (listed in each `leak-check.json`), answers
  yes→no vs the kernel skeleton on exactly those 13 — a disclosed deviation;
  plain↔opaque skeleton identity (the binding requirement) is asserted
  item-by-item, fail-closed. Item-level pairing to the KERNEL corpus is not
  required for the verdict and NOT claimed. Yes/no balance after
  substitution: 43/101 (no-share 0.701 ≤ 0.75, LC7 PASS) [MEASURED].

**Build gates, all PASS [MEASURED, fail-closed]:** G-COVER (108/108 store
records for every slot concept); G-LC8p (full-prompt disjointness from all
650 d-qa + 1000 d-qa-r + 360 d-qa-t items, between the two new corpora, and
intra-corpus); LC1-s (0 headword leaks into injected term-match definitions);
LC2/LC3-s/LC4/LC5/LC7 store analogues; **G-TOK** re-run on the ACTUAL gsx0
surfaces at the pinned SmolLM2-135M tokenizer (`poc/gsx0/gtok_check.py`,
tokenizer sha `9ca9acdd…47c` = revision 12fd25f7): mean prompt-surface tokens
kernel 93.59 / plain 93.19 (**1.00×**) / opaque 94.46 (**1.01×**) — inside
the ±10% pre-freeze band (`poc/gsx0/g3-token-band-gsx0.json`, pinned).

**Pins (kot-corpus-hash/1):** d-qa-t-plain
`ef2153076b9c30ac14a936b9cfc9bb7f25c4c39f3c828164a5a522ddb2ebf800`,
d-qa-t-opaque
`472e041cabe80a2c680edcc648758c01579992dc925e70ac09ffcd9795fefe81`.

## 4. Blind external adjudication (judge policy FROZEN; review finding 7)

`data/d-adj-t/PROTOCOL.md` §4 standards S1–S7 VERBATIM, re-run per store on
the plain and opaque surfaces → `data/d-adj-t-plain/`, `data/d-adj-t-opaque/`
(each: PROTOCOL copy, per-judge raw responses, `labels.jsonl`,
`summary.json` with the same `analysis_input_metrics` integer names as
f2b-transfer's d-adj-t). Hashed AFTER adjudication; the declared
PINNED-AT-INPUTS placeholders are filled by ops amendment before the stage-1
records are appended, then never revisited (single-draw).

**FROZEN judge policy (B-2 resolved; exact f2b-transfer mirror):** judge-1 =
kernel-naive HUMAN, the SOLE gold source; judge-2 = blind LLM judge
(GPT-5.6-sol via codex, temperature 0, pinned prompt, item text only);
judge-3 = GPT-5.6 tie-break on discordant, resolution rule issue-#9 (resolve
to human iff judge-3 == human, else UNRESOLVED). The draft's annotator-proxy
fast path for gold is REMOVED — an LLM proxy is not the same sourcing as
f2b-transfer and would break the exact-mirror claim. Sourcing disclosed in
every readout. [STIPULATED, review-mandated]

## 5. Stages, arms, n, power

Fresh-runs pre-commitment (carried from f2b-transfer): NO logged cell serves
as an arm output; reuse-check run + recorded pre-spend with the pre-committed
decision "proceed-with-reason: fresh-runs pre-commitment".

**STAGE 0 — the blinded headroom PILOT (first gated step; review finding 4;
portfolio Rank-4 requirement).** Items: the FIRST 60 items of d-qa-t-plain in
pinned rank order. Their blind adjudication (protocol §4 verbatim) is the
first 60 rows of the eventual d-adj-t-plain corpus — adjudicate once, reuse;
no re-draw, no re-adjudication. Run R1-alone (SmolLM2-135M), seeds 0/1/2,
phase="pilot" (never verdict-eligible), on the pilot items with resolved
external gold (floor: ≥40 resolved, else the pilot is re-read after the full
adjudication completes, still before any stage-2 spend). **Pre-committed,
binding stop rule — the NON-VACUOUS headroom gate:** STOP the experiment
pre-spend iff the one-sided 95% Wilson LOWER bound of the pilot pooled
per-item seed-mean R1-alone external-gold accuracy > **0.75**. Rationale:
0.75 = headroom cap 0.85 − powered Δ 0.10; if we are ≥95% confident the
baseline exceeds 0.75, the run cannot detect the registered effect inside the
headroom cap even where the 0.85 gate would nominally pass. The pilot outcome
is BINARY (STOP / PROCEED), is disclosed in every readout, and may not be
used for any other design choice (no discretionary redesign; review finding
4). Blinding: no verify-arm output exists at pilot time; judges are blind per
protocol. Forecast [MEASURED, knull-v2]: R1-alone on plain surfaces ≈
0.504–0.505 (membership gold) ⇒ PROCEED expected; the gate exists because
external-gold difficulty on THESE skeletons is unmeasured, and it can
genuinely fire (knull R3-alone-plain = 0.948 shows plain surfaces can
saturate a host). Cost ≈ $1–2. On STOP: file the pilot record + coordinator
decision; verdict remains INCOMPLETE-DATA (surfaces cannot adjudicate the
question at this rung); no GPU beyond the pilot cells is spent.

**STAGE 1 — adjudication instruments ($0 GPU), BOTH stores:** complete the
remaining 300 plain adjudications + all 360 opaque; pin both corpora (ops
amendment); append `adjudication-instrument-plain` and
`adjudication-instrument-opaque` final-phase records; verdict-gen. Rules 1–3
read here: FAIL (affirmative non-endorsement), INCONCLUSIVE (endorsement not
demonstrated), or proceed on INCOMPLETE-DATA.

**STAGE 2b-i — staged headroom (GPU):** `model-alone` R1 (seeds 0/1/2) ONLY,
on the 250-item plain external-gold eval set; append final-phase records;
verdict-gen. The pinned analysis emits the headroom gate from R1-alone data
alone, so a saturated baseline yields INSTRUMENT-INVALID after ~1/5 of the
stage-2 spend; headroom OK yields INCOMPLETE-DATA licensing 2b-ii.

**STAGE 2b-ii — the remaining four cells (GPU):**

| arm | rung | k | seeds | role |
|---|---|---|---|---|
| `model-alone` | R3 | 0 | 0,1,2 | separation gate + non-inferiority reference |
| `plain-verify-retry` | R1 | 4 | 0,1,2 | THE deflator arm (engagement-gated) |
| `shuffled-plain-verify-retry` | R1 | 4 | 0,1,2 | structure null (seed-pinned Sattolo derangement of the PLAIN store; the one control NOT to cut) |
| `plain-gloss-self-verify-retry` | R1 | 4 | 0,1,2 | RT-2 commodity control at matched budget |

Opaque stage-2 GPU is NOT pre-committed (B-4): it runs only if opaque
unexpectedly survives stage 1 — a coordinator decision.

**Dual scoring** on every stage-2 cell: `item_correct_ext` vs d-adj-t-plain
gold (ALL endpoints) + `item_correct_mem` vs plain membership gold
(descriptive contrast only). Every stage-2 record MUST carry
`metrics.eval_items_sha256` (sha256 of the pinned eval item-id list in
order); the pinned analysis hard-fails on any mismatch, on any missing/
duplicate/extra seed, on any partial arm configuration, and on any vector
shorter than the 200-item floor (review finding 6). In-run extraction
counters (`n_verify_calls`, `n_extraction_failures`) on the plain-verify
cells feed the store-appropriate extraction gate (§6) — the f2b-transfer
d-xif P10 gate is kernel-rendered and cannot measure plain surfaces
[STIPULATED, documented deviation].

**n / eval set (frozen verbatim, mirrors f2b-transfer):** n_generated=360 per
store; adjudicate all 360; EVAL SET = the first `per_arm_items=250`
externally-labelled items in pinned rank order; `eval_floor=200`
(`ERR_EVAL_FLOOR`). 3 paired seeds, fixed k=4, no sweep. The plain eval
prefix is taken independently of f2b-transfer's kernel eval prefix; item
pairing to the kernel eval is NOT claimed [STIPULATED].

**Power [STIPULATED, advisor/P8 carry-over]:** n=250 × 3 seeds ≈ 0.92
one-sided power at absolute Δ=0.10 for the paired primary; the stage-1
endorsement gate is powered at n=360 (Wilson LB at expected 0.85 = 0.816 >
0.70); the opaque rejection read is powered even pessimistically (Wilson UB
at A=0.5, n≈340 ≈ 0.545 < 0.70). The narrowed estimand (§1) removes the
magnitude-matching demand, so the 0.85 headroom cap is coherent with the
powered Δ=0.10 (review finding 4's cap note).

## 6. Endpoints, kills, gates (frozen contract; mirrors the pinned analysis)

- **PRIMARY (absolute, margin 0, plain external gold):** `effect_size =
  acc_ext(plain-verify-retry, k=4) − acc_ext(R1-alone)`; seed-averaged
  per-item means on the 250-item eval set; paired item BCa bootstrap,
  B=10000, PRNG seed 20260713; reject iff one-sided 95% BCa LB > 0. SESOI for
  NULL: Cohen's h = 0.2 (TOST vs R1-alone).
- **Kills:** (d′) stage-1 AFFIRMATIVE non-endorsement: Wilson-UB(A_plain) <
  0.70 ⇒ FAIL, $0 GPU. (b) shuffled-plain recovers ≥30% of the external-gold
  lift (point) — fires only with primary_reject. (c) plain-gloss-self closes
  as much at ≤ matched FLOPs/query (F0 ledger, point) — fires only with
  primary_reject. Affirmative no-lift ⇒ NULL (TOST); mere non-rejection ⇒
  INCONCLUSIVE.
- **Instrument gates (INSTRUMENT-INVALID, never FAIL/PASS/NULL):**
  adjudication G-adj(plain): n_adjudicated ≥ 300, unresolved ≤ 15%, raw
  two-judge agreement ≥ 0.80; extraction (in-run): pooled one-sided 95%
  Wilson LOWER bound of extraction SUCCESS over plain-verify verify calls ≥
  0.90 (equivalently failure Wilson UPPER bound ≤ 0.10; the draft's
  "failure Wilson-LB" phrasing was wrong — corrected); engagement (RT-7a):
  decidable ≥ 0.95, attempt-0 rejection ∈ [0.05,0.95], ≥1 final ≠ attempt-0;
  missing engagement/extraction blocks are gate failures (fail closed);
  headroom: acc_ext(R1-alone) ≤ 0.85, evaluable at stage 2b-i.
- **PASS-gate-bearing opaque control:** `opaque_adjudication_valid` (G-adj on
  the opaque record) ∧ `opaque_rejected` (Wilson-UB(A_opaque) < 0.70) are
  conjuncts of the PASS rule; missing opaque record ⇒ the PASS rule cannot
  evaluate ⇒ INCOMPLETE-DATA.
- **Separation gate (gates ONLY the R3 secondary):** acc_ext(R3-alone) −
  acc_ext(R1-alone) ≥ 0.05 ∧ one-sided 95% BCa LB > 0; on failure
  `noninferiority_vs_r3` leaves the Holm family before any p-comparison.
- **Holm family F-secondary(gsx0):** `beats_gloss_self_verify`,
  `shuffled_low_recovery` (ub95 < 0.30), plus — conditional on the separation
  gate — `noninferiority_vs_r3`. Forecast note [MEASURED, knull-v2]:
  R3-alone-plain ≈ 0.948, so noninferiority is expected to fail; it is
  retained for mirror-fidelity and is not load-bearing.
- **Reported-only (never Holm, never verdict-bearing):** A_plain ± bounds;
  A_opaque ± bounds; dual-scoring contrast + transfer_ratio; the premium
  diagnostic (§7); seed-sign (3/3); cost_ratio_vs_R3 (F0); pilot values.

## 7. The premium diagnostic (renamed; review finding 6)

`kernel_content_premium_ext = KERNEL_EXT_LIFT_REF − plain_ext_lift`, with
`KERNEL_EXT_LIFT_REF = 0.25066666666666704` the FROZEN f2b-transfer primary
POINT ESTIMATE [MEASURED, `registry/verdicts/f2b-transfer.json`]. Reported
with the plain-arm bootstrap CI and `premium_band_within_margin` (|premium|
CI inside ±0.05). The kernel ref is treated as ERROR-FREE (its own sampling
uncertainty is NOT propagated) and is not co-resampled: the band is a
CONDITIONAL DESCRIPTIVE cross-experiment diagnostic — it is NOT a test of
equivalence to the kernel effect, is never Holm/verdict-bearing, and its
disclosure sentence above travels verbatim with any readout that cites it.
The verdict-bearing deflation is carried entirely by the primary + the
shuffled control, both within THIS experiment. [STIPULATED]

## 8. What a PASS / FAIL / NULL licenses (envelope — binding verbatim)

2 host rungs license a SIGN, not a slope; every claim is scoped to ≤1.7B
hosts, the kernel-covered templated definitional-QA family over the same 108
covered concepts rendered through the PADDED plain dictionary (or nonce)
store, the fixed k=4 budget, and THIS gold standard (blind dual-judge
external adjudication, human judge-1 sole gold source, sourcing disclosed).
Coverage disclosure (mandatory, verbatim): kernel-expressibility coverage
0.3542 at rung molecules-v0 — MEASURED by m0b on one incomplete kernel-v0
instance, NOT general coverage; every accuracy claim is bounded to the
kernel-covered slice.

- **PASS (H-GT):** *kernel content is not necessary for a positive
  externally-adjudicated verify-retry lift on this line: a generic,
  token-matched plain-dictionary store produces a real, content-specific,
  blindly-endorsed external-gold lift at this scope.* NOT licensed: any
  kernel-vs-plain magnitude claim ("as well as", "premium is zero" — §7);
  any statement that the kernel is worse; external question-STYLE ecological
  validity; any coverage-general claim; any PRM comparison; any slope or
  >1.7B effect size.
- **FAIL (d′ affirmative non-endorsement) / NULL (affirmative no-lift):**
  *the PADDED plain construction fails this test where the kernel construction
  passed it.* NOT licensed without more: any kernel-content-distinctive
  claim. Two pre-registered obligations bind the interpretation: (i)
  **mandatory concise-plain sensitivity (review finding 5):** no
  kernel-distinctive reading may be advanced until a concise-plain (0.66×,
  non-padded) sensitivity — at minimum stage-1 blind adjudication of
  concise-plain surfaces; stage-2 if its stage-1 passes — replicates the
  negative under a non-padded construction (a new successor record; padding
  changes fluency/salience/adjudication surface, so a padded-store negative
  is ambiguous between content and padding artefact); (ii) a
  kernel-distinctive CLAIM additionally requires a direct kernel-vs-plain
  difference/interaction test (a successor experiment), since "kernel
  significant previously, plain not significant now" is not evidence the
  effects differ (review finding 3).
- **FAIL (b/c):** the established plain lift is retry-structure or commodity
  verification — scoped to the plain store; no kernel claim either way.
- **Opaque control:** rejection confirms external gold detects non-content;
  a permissive opaque (UB ≥ 0.70) blocks PASS and is itself a disclosed
  finding about the instrument, never a hypothesis outcome.

Nothing here amends knull-v2 or f2b-transfer: their frozen verdicts,
envelopes, and assessments stand exactly as issued.

## 9. The pinned analysis (verdict-gen-compatible stdin adapter)

`analysis/generic_store_external_gold_stdin.py` — stdin-conformant (JSONL of
eligible records on stdin, canonical JSON on stdout, no argv; the
knull/ufo-check-0 CLI-pin defect is absent, verified against
verdict-gen.py step 5). Statistics carried byte-identical in construction
from the audit-CONFIRMED `analysis/f2b_transfer.py` (BCa/Holm/TOST/
engagement/separation/headroom); gsx0 additions: staged 2b-i headroom read
from R1-alone data alone; opaque endorsement control with affirmative
rejection (Wilson UB); stage-1 affirmative non-endorsement (Wilson UB);
in-run extraction gate; the renamed premium diagnostic; and the
cell-integrity hard-fails of §5 (exit 1 ⇒ verdict-gen fails closed; an
analysis abort can never default to a verdict). 69 declared output fields
(`pins.analysis_script.output_fields`). `--selftest` PASSES (hand-computed
point values at every branch, including staged-headroom, permissive-opaque,
both stage-1 kill routes, and nine cell-integrity abort branches); green
mock through the stdin pipe path: full 17-record fixture ⇒ all 69 fields,
rc 0, 0 stderr; stage-1-only ⇒ 17 fields; stage-2b-i ⇒ 21 fields
(`poc/gsx0/mock/`). [MEASURED this session]

## 10. Cost plan and caps [STIPULATED — dry-plan estimates, never measurements]

Anchors: f2b-transfer stage-2 ≈ 0.25 GPU-h ≈ $0.55 (15 cells × 250 items);
f2b-replicate full run MEASURED 0.604 GPU-h ≈ $1.27. gsx0:
- **Stage 0 pilot:** 60-item adjudication (judge-2/3 LLM ≈ $0.5–1; judge-1
  human ≈ 0.5–1 h) + R1-alone pilot cells (minutes of GPU) ≈ **$1–2**.
- **Stage 1 remainder:** LLM judges ≈ $2–6 + tie-breaks ≈ $1–2 across both
  stores; judge-1 human ≈ 3–4 h total.
- **Stage 2 (GPU, plain):** point ≈ 0.25 GPU-h ≈ $0.55; worst case (2×) ≈
  $1.30; staged as 2b-i (~1/5) then 2b-ii. If opaque unexpectedly survives
  stage 1: +$0.55–1.30 (coordinator decision).
- **All-in point ≈ $6–10; pessimistic ceiling ≈ $16** — matches the
  portfolio Rank-4 framing; the design can FAIL for ~$0 GPU (stage 1) and
  can stop for ~$1–2 (pilot). Caps: `usd_cap` **$20**, `gpu_hours_cap` **4**,
  `wall_clock_cap_hours` **24**, Tier-1 `tier_cap_usd` **80**.
- Infra: modal, single A100-40GB/A10G, concurrency 5, foreground gates; the
  f2b-transfer image + pinned model revisions (`SmolLM2-135M@12fd25f7`,
  `SmolLM2-1.7B@31b70e2e`). Runner: mechanical store-swap adaptation of
  `poc/f2b-transfer/runner/f2bt_runner.py` (knull store injection; staged
  cell plan; `eval_items_sha256` + in-run extraction counters emitted per
  cell) — an execution-phase artifact under the PINNED-AT-INPUTS
  harness_manifest, built by the Opus runner and validated by the mandatory
  green mock BEFORE any final-phase run (§12 finding-7 disposition).

## 11. Execution checklist (post-freeze; Opus runner, practices 1–5)

1. RT-15: post the frozen_sha256 to the coordination issue.
2. Runner adaptation + `mock-check` green (harness_manifest ops amendment).
3. STAGE 0 pilot (§5): adjudicate first-60 → pilot R1-alone (phase=pilot) →
   binding STOP/PROCEED, recorded in the run-log.
4. STAGE 1: complete both adjudications; `corpus-pin`; ops amendments fill
   the d-adj-t-plain/-opaque pins; append both stage-1 final-phase records;
   verdict-gen (rules 1–3 may end the experiment at ~$0 GPU).
5. Pre-spend: reuse-check (pre-committed fresh-runs decision), dry-plan vs
   caps, mock re-check.
6. STAGE 2b-i: R1-alone final cells; verdict-gen (headroom). STAGE 2b-ii:
   remaining cells; verdict-gen; Codex GATE-A audit; Fable interpretive
   assessment under §8's obligations; GPT-5.6 review gate before any
   conclusion lands.

## 12. Readiness-review disposition log (rev-2 vs the 7 findings)

1. **Estimand/licenses — APPLIED.** PASS narrowed to "kernel content not
   necessary for a positive lift" (§1, §8); premium renamed + disclosed as a
   conditional descriptive band (§7); no concurrent kernel arm (cost;
   pre-declared successor if warranted).
2. **Opaque gate — APPLIED.** PASS now requires present + G-adj-valid +
   affirmatively-rejecting opaque (Wilson UB < 0.70, ceiling justified §2);
   missing ⇒ INCOMPLETE-DATA; permissive ⇒ PASS blocked.
3. **FAIL/NULL logic — APPLIED.** Affirmative-evidence discipline throughout:
   stage-1 FAIL needs UB < 0.70 (LB-only ⇒ INCONCLUSIVE); kills b/c gated on
   primary_reject; affirmative no-lift ⇒ NULL (now reachable); mere
   non-rejection ⇒ INCONCLUSIVE; kernel-distinctive claims deferred to a
   direct difference test (§8).
4. **Staged headroom — APPLIED.** Stage 2b-i (R1-alone first) + adapter
   emits the headroom decision from R1-only data; PLUS the binding blinded
   pilot with the non-vacuous 0.75 Wilson-LB stop rule (§5); the cap/target
   tension resolved by the narrowed estimand (Δ=0.10 within the 0.85 cap).
5. **Padding neutrality — APPLIED (as an interpretation-layer commitment).**
   Padded stays the token-matched primary; concise-plain is a pre-declared
   MANDATORY sensitivity for any negative/kernel-distinctive interpretation
   (§8); "a-fortiori" language dropped; results scoped to the padded
   construction.
6. **Adapter hardening — APPLIED.** Exact cell/seed cardinality, duplicate,
   vector-length/floor and item-identity (eval_items_sha256) hard-fails;
   premium renamed; extraction-bound prose corrected (§6, §9).
7. **Protocol/implementation — APPLIED with one disclosed narrowing.** Judge
   policy frozen (human judge-1 sole gold; proxy path removed, §4); corpora
   implemented, validated, pinned (§3). The RUNNER remains an
   execution-phase artifact under the PINNED-AT-INPUTS harness_manifest with
   a mandatory green mock before any final-phase run — the f2b-transfer
   precedent (audit CONFIRMED); no analysis output or verdict rule depends
   on runner bytes at freeze time, and the store-swap is a mechanical
   adaptation of two proven harnesses. [STIPULATED disagreement-in-part,
   flagged for the review gate]

## 13. Pre-freeze skeptic self-attack (Fable)

- *"The pilot double-uses data."* No: pilot adjudications are the first 60
  rows of the single-draw corpus (adjudicate-once); pilot GPU cells are
  phase=pilot, never eligible; final R1-alone re-runs fresh on the full eval
  set; the stop rule is binary and pre-committed.
- *"Rule 3 (INCONCLUSIVE) before stage-2 rules could mask a real stage-2
  read after a protocol violation."* Intended: if stage 2 ran despite an
  undemonstrated endorsement, the endorsement gate must dominate — external
  gold that cannot be shown to endorse the store's own content cannot ground
  a lift claim on that store's surfaces.
- *"Kill (c) at near-zero lifts could FAIL a lift-less run."* Fixed: kills
  b/c fire only with primary_reject (rule 6).
- *"Premium band with an error-free ref could still be quoted as
  equivalence."* The disclosure sentence travels verbatim (§7); the field is
  renamed so 'tost'/'equiv' no longer appear in it.
- *"Opaque UB < 0.70 is a weak rejection bar — a mediocre judge panel could
  pass it while endorsing junk at 0.5."* The bar is the SAME bar plain must
  clear from below, and G-adj (agreement ≥ 0.80) must hold on the opaque
  record itself; a panel endorsing junk at ~0.5 with high agreement would
  pass opaque_rejected — but such a panel would also depress A_plain toward
  the kill; residual risk disclosed, reported bounds published.
- *"13 polarity substitutions make the plain surfaces slightly easier/harder
  than the kernel's."* Cross-store identity (the requirement) is exact;
  kernel pairing is not claimed; the 13 are listed and the yes/no balance
  re-passes LC7.
- *"eval_items_sha256 is emitted by the runner being checked."* True — it
  proves cross-cell consistency, not corpus fidelity; corpus fidelity is
  carried by the corpus pins + the runner's fail-closed record_sha256 checks
  (f2bt_runner mechanism), and the Codex audit re-verifies.
- Residuals (disclosed, accepted): no concurrent kernel arm (finding-1
  narrowing instead); runner not built at freeze (finding-7 narrowing);
  judge-2/judge-3 share a model family (inherited from f2b-transfer,
  disclosed in sourcing).

## 14. ASMs to register with the freeze commit (register-ASM-with-commit)

- ASM-gsx0-1: a linter-gated plain dictionary is a faithful ordinary-meaning
  surface (STIPULATED).
- ASM-gsx0-2: skeleton injection preserves alignment + the token band
  (MEASURED at build: G-TOK 1.00×/1.01×; alignment by construction).
- ASM-gsx0-3: the kernel_content_premium diagnostic is descriptive-only
  (kernel ref not co-resampled, error-free by fiat; disclosed).
- ASM-gsx0-4: the plain eval prefix is taken independently of the kernel
  eval prefix; kernel pairing not claimed.
- ASM-gsx0-5: the pilot stop bar 0.75 = headroom cap − powered Δ; binding,
  binary, no other use.
- ASM-gsx0-6: RULING G-2's 13 polarity substitutions preserve the
  cross-store skeleton-identity requirement and the LC7 balance (MEASURED).

Governance self-check: every choice tagged STIPULATED (not asserted as
measurement); no EXTRAPOLATION load-bearing; no @handle account strings; no
frozen record edited; this section is the mandatory self-check gate. ✓
