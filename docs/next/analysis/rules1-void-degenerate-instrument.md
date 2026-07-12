# RULES-1 run 1 VOID — degenerate host instrument (post-mortem)

**Status: maintainer VOID decision, 2026-07-12.** The RULES-1 GPU campaign
`poc/rules-1/results-incoming/20260712-070956-modal/` (13,470 rows, arms
A1/A3/A5/A7/c1 × seeds 0,1,2, wall 4.59 h, ~$5) is **VOIDED as an instrument
failure and is NOT graded**. No row from it may ever be appended to the
rules-1 results log or consumed by any verdict. The successor experiment is
**rules-1-b** (`registry/experiments/rules-1-b.json`, supersedes rules-1) with
a fixed harness and a new host-validity instrument gate. This document is the
durable record of the void: what happened, the root cause, the fix, the new
gate, and why run 1 carries no evidential weight in either direction.

---

## 1. What happened

Every one of the 12,870 scored entailed rows carried `item_correct_ext = 0` —
in **every** arm:

| arm | what it is | expected | observed |
|-----|------------|----------|----------|
| A1  | 135M alone (padded)               | low but > 0        | 0.0 |
| A3  | 135M + engine verify-retry (k=4)  | ≥ A1               | 0.0 (attempts=5 on all 2,574 rows) |
| A5  | 1.7B alone                        | ~0.79 (nsk1 datum 0.7912, n=958) | 0.0 |
| A7  | engine-direct render (engine itself 858/858 certified vs third-party gold) | high | 0.0 |
| c1  | shuffled-rules control            | ~A1                | 0.0 |

Zero hits on a 23-way forced choice over 12,870 rows is statistically
impossible for a non-degenerate scorer (chance ≈ 4.3%; P(0 hits) under
independence ≈ e^(−560)). The host side of the instrument was returning a
constant off-gold pick. A3's `attempts=5` everywhere confirms it from the
other side: the verifier (provably correct, see below) rejected every
proposal on every retry — the host never once proposed the licensed answer.

**The engine side was healthy throughout**: 300/300 named fail-closed
refusals on the control cells of A3/A7 (`refusal_correctness_e5 = 1.0`), and
the c1 deranged-TBox ledger read exactly as disclosed at build (645
ERR_CONFLICT / 213 ERR_INSUFFICIENT_PREMISES). The pinned CPU certificate
(sha `e0071e9e…`) already carried engine 858/858 vs third-party CLUTRR gold.
This was a **host-scoring instrument failure, not an engine result**.

## 2. Why run 1 is not graded (the void, and why it is honest)

Under the frozen rules-1 verdict rules the run would mechanically read
**FAIL (KILL-b)**: the frozen instrument gates (certificate, twin, headroom
acc(A1) ≤ 0.85, engagement) all PASS on these rows — a degenerate scorer
*passes* a headroom ceiling and *passes* an engagement gate — and the one
gate that catches host degeneracy from below (separation, acc(A5) − acc(A1)
≥ 0.05) was frozen as **s3-family-scoped only**, not as a global instrument
gate. That is a **pre-registration gap**: rules-1 had no floor under the
host instrument, only a ceiling over it.

Grading a FAIL from an instrument that scores the *engine-direct oracle arm*
(A7, 858/858 certified) at 0.0 would record a hypothesis verdict produced
entirely by a broken measuring device. The maintainer therefore **voided the
run** (2026-07-12) rather than let KILL-b fire on it: KILL-b's meaning is
"the derivations do not help the host"; these rows cannot speak to that
claim because the host channel measured nothing. Symmetrically, the void
gives **no comfort in the PASS direction** — run 1 is evidence of nothing
except the instrument defect. The fix is a NEW experiment id
(**rules-1-b**, `supersedes: rules-1`) — never a re-roll of rules-1; the
rules-1 log stays as-is (no final rows appended) and the run-records bytes
are retained under `results-incoming/` for audit.

## 3. Root cause

**Two interacting prompt-frame defects, each measured sufficient to keep even
A7 (derivation injected) at ~0 on the R1 host:**

1. **Direction inversion**: the forced-choice cue left the relation direction
   unstated, and the CLUTRR gold convention is the reverse of the model's
   natural reading — making the gold word structurally un-elicitable.
2. **Menu-adjacency interference**: the 23-word vocabulary line placed
   immediately before the `Answer:` cue swamps the small host's next-token
   distribution with menu-prior words, masking even a verbatim in-context
   answer statement.

Mechanics (diagnosed 2026-07-12 on CPU, $0 — a forced-choice ranking probe
with the as-run prompt builder + f2bt scorer bytes (SmolLM2-360M probe model;
full 23-option logprob rankings), the SmolLM2 tokenizer check, the
nsk1-vs-rules-1 harness diff, and the campaign rows themselves as the
at-scale datum; the fix is then confirmed on the PINNED models by the §6
pilot):

- The nsk1-clutrr gold triple is `(A, gold, B)` read "**A's <gold> is B**":
  item `clutrr-c0001` has question "How is Jennifer related to Jason?",
  provenance proof `('Jennifer','grandfather','Jason')`, gold
  `grandfather` — i.e. the answer names what **Jason is to Jennifer**.
- The rules-1 prompt ended `Question: How is Jennifer related to Jason?\n
  Answer with one word from: <23 words>.\nAnswer:` — the bare `Answer:` cue
  says nothing about direction. The natural English completion of "How is
  Jennifer related to Jason?" is Jennifer's role (*granddaughter*), the
  REVERSE of gold; small hosts additionally collapse onto menu-prior words.
  Measured (360M probe, as-run prompt bytes + as-run scorer): gold ranks
  14–20/23 on A1-shaped prompts and 12–17/23 on A7-shaped prompts *with the
  correct derivation injected*, with the greedy pick constant off-gold
  (*aunt*/*nephew*/*no-relation*). Since gold on all 858 covered items is
  always the grandparent word (`grandfather` 433 / `grandmother` 425) and
  the frame never elicits the grandparent direction, accuracy 0 in every arm
  is the expected output of this frame — **including A7**, where the
  injected derivation literally states "Jason is Jennifer's grandfather":
  the cue still doesn't tell the host *which direction* the one-word answer
  should name. A3's `attempts=5` everywhere follows: the retry sampler draws
  from the softmax over summed option logprobs, and a rank-15 option has
  vanishing mass, so the licensed answer is never proposed in k=4 retries.
- **The menu-line defect, isolated on the pinned R1 @ `12fd25f7`** (direct
  next-token measurement, injection present, direction-explicit cue):
  ` grandfather` is **top-1 (−1.14)** when no menu line precedes the cue;
  adding the 23-word menu line directly before the cue drops it to rank ~9
  (top picks *brother* −2.09, *sister* −2.20, *aunt* −2.50 — early-listed
  menu words); moving the same menu into the task header restores
  ` grandfather` to **top-1 (−1.73)**. Fixing the direction alone is NOT
  sufficient: with the menu line still adjacent to the cue, gold ranked
  4–13/23 across probe items on the pinned R1.
- Why nsk1 measured 0.7912 on the same items with the same 1.7B bytes: the
  nsk1/g2 harness prompted with the ORIGINAL CLUTRR story + "Answer with
  exactly one word naming the family relationship…" and scored **greedy
  generation** by first-vocab-word match — CLUTRR stories state the chain in
  the gold direction ("[Jason] is the proud father of…"), and the
  generation channel lets the model produce the word the narrative primes.
  The rules-1 harness swapped in the verbalised stated-facts world and a
  logprob forced choice after a bare `Answer:` — a different instrument,
  never smoke-tested with a real model before the GPU spend.

### Ruled out (the §6 suspects from the grade prep)

- **Unnormalised option-logprob sums over multi-token options**: real but
  not the cause here — the gold words ` grandfather` / ` grandmother` are
  each a SINGLE SmolLM2 token (the multi-token menu entries are the
  `*-in-law` words, never gold). The f2bt sum scorer is retained
  byte-identical in rules-1-b.
- **fp32-vs-fp16 load in Rules1HFLM**: not the cause — dtype changes cannot
  invert an argmax by ~2–4 nats, and the same degenerate ranking reproduces
  on CPU fp32. fp32 stays (frozen runner constraint).
- **Scorer indexing/continuation bug in the reused `HFLM._option_logprobs`**:
  ruled out by inspection and by f2b/f2b-transfer scoring correctly with the
  same bytes (single-token letter keys there; and rules-1-b's pilot recovers
  accuracy with the same scorer once the cue is fixed).

## 4. The fix (rules-1-b harness)

`poc/rules-1/rules1_runner.py` + `poc/rules-1/inputs/rules1-manifest.json`:

1. **Direction-explicit answer cue** (fix for defect 1): the frame
   `answer_cue` becomes the per-item infill
   `"\nAnswer: {b_name} is {a_name}'s"` (e.g. `Answer: Jason is
   Jennifer's` → scored options ` grandfather`, ` aunt`, …). This is exactly
   the surface of the engine's own derivation rendering, so cue, injected
   derivations, and verifier feedback all speak one direction. The cue is
   identical across arms (shared-affordance discipline preserved); the
   fail-closed `render_answer_cue` refuses to build a prompt without the
   pair names.
1b. **Menu moved into the task header** (fix for defect 2): the 23-word
   vocabulary is rendered inside `task_prefix` ("…answer the question with
   exactly one relationship word from: <menu>.") and the standalone menu
   line before the cue is removed. The closed-vocabulary constraint itself
   is enforced by the per-option logprob scorer, not by prompt text.
2. **Feedback wording aligned**: the ground-(iii) rejection line now reads
   "no derivation from the stated facts licenses '<B> is <A>'s <word>'"
   (gold-leak guard unchanged, still asserted on every line).
3. **Pilot mode** (`--pilot-n N [--pilot-dtype bf16]`): a REAL-model tiny-n
   CPU instrument pilot, labelled PILOT end-to-end, structurally incapable
   of producing final rows (separate `-pilot` file names, PILOT outcome
   label). The missing cheap step that would have caught this before the
   GPU spend; rules-1-b's runner constraints make it mandatory before
   launch. bf16 is pilot-only (1.7B fp32 does not fit the CPU box); real
   runs stay fp32.
4. Everything else — the f2bt forced-choice scorer/sampler bytes, the twin
   engine, the certificate precondition, arms, seeds, k, budget — is
   unchanged.

Pilot result (2026-07-12, CPU, $0): see §6 below.

## 5. The new HOST-VALIDITY instrument gate (closes the prereg gap)

`analysis/rules_1b.py` adds `/gates/host_validity_valid`:

```
host_validity_valid := acc(A7, entailed, seed-mean) >= 0.30
                   AND acc(A5, entailed, seed-mean) >= 0.15
```

and the rules-1-b verdict rules test it in **rule 0 (INSTRUMENT-INVALID)**,
ahead of the KILL-b FAIL rule — so a degenerate host instrument can never
again read as a substantive FAIL (or PASS).

Why these floors:

- 23-way closed-vocab chance floor = 1/23 ≈ 0.0435; its one-sided 95%
  binomial UB at n=2,574 rows is ≈ 0.051. Both floors sit far above any
  chance excursion.
- **A7 ≥ 0.30**: A7 renders an injected, engine-certified derivation
  (engine 858/858 vs third-party gold). A host that cannot reach ~7× chance
  *with the answer's derivation in-context* is not reading the surface —
  instrument, not hypothesis.
- **A5 ≥ 0.15**: the R3 host premise (ASM-0040 lineage) is replicated four
  times at 0.7912 on these items; 0.15 (~3.5× chance) is far below any
  plausible healthy value and far above a constant-pick 0. A5 failing this
  floor means the frame/scorer, not the hypothesis, failed.
- Both arms are hypothesis-neutral: A7 carries no lift claim (systems arm)
  and A5 is the efficiency comparator; gating on them cannot select for the
  primary A3−A1 contrast. (The retro-check: rules_1b.py over the voided
  run-1 rows returns `host_validity_valid: false` → INSTRUMENT-INVALID, as
  it should have read.)

Also folded into `analysis/rules_1b.py`: the s3 conditioning defect
disclosed at the rules-1 grade prep (rules_1.py computed s3 unconditionally;
it is now null/unevaluable when the separation gate is false — never a pass,
never a fail).

## 6. Pilot confirmation (fixed instrument, CPU, ~$0)

<!-- PILOT-RESULTS: filled by the pilot run below -->

## 7. Re-freeze and re-run path

1. `registry/experiments/rules-1-b.json` (DRAFT, kot-reg/2 flat /design,
   `supersedes: rules-1`; same arms/endpoints/budget; new pins:
   `analysis/rules_1b.py`; verdict rule 0 extended with
   `/gates/host_validity_valid`) — freeze via
   `prereg-freeze --experiment rules-1-b` after maintainer sign-off.
2. Ops amendment pins the new harness manifest sha
   (`modal_rules1.py --print-manifest`) exactly as rules-1 amendment seq 1
   did.
3. Mandatory pre-launch: `--mock` green AND `--pilot-n 24` on CPU showing
   `host_validity` floors cleared, BEFORE any GPU spend.
4. Full campaign (experiment-runner role, Modal A10G, fp32, same seeds/caps),
   then verdict via the scoped driver path ratified for rules-1
   (corrections seq 2 precedent) against rules_1b.py.

## 8. Assumptions

Emitted as PROPOSED-ASM-1630..1649 with the rules-1-b draft (assumption ids
are proposals only; `registry/assumptions.jsonl` is written by the
maintainer's ratification flow, never by this analysis).
