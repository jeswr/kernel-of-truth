# haiku-tier stage 1 — prompting-framework experiments (kernel-of-truth-b96)

**Date:** 2026-07-07 · **Author:** Haiku-pipeline agent (Claude Fable 5) ·
**Model under test:** claude-haiku-4-5-20251001 via `claude -p`
(MAX_THINKING_TOKENS=0, --tools "", --strict-mcp-config,
--exclude-dynamic-system-prompt-sections, --effort low, --max-turns 1;
any change to this pinned call configuration is a pipeline version change).

## Setup

50 concepts: 35 drawn evenly from the stage-0 inventory bands (12 A, 12 B,
11 C — including deliberately hostile tail items like "don", "blah", "raj"),
plus 15 that also exist in the hand-authored corpora for fidelity comparison
(7 kernel-v0: begin, afraid, believe, break, find, death, conversation;
8 molecules-v0: dog, water, red, eat, sleep, house, money, music).
Input per concept: Wiktionary definitions (100% fetch success on all 50) +
Wikipedia lead where usable (52%), revision ids recorded.

Frameworks (system prompts in `prompts/`, sha256 in `prompts/prompt-meta.json`):

| fw | design |
|---|---|
| A | molecule-first routing, single pass |
| B | explication-first routing, single pass |
| C | = A + second self-check/repair pass (checklist prompt, blind: no validator output) |
| D | = A + hardened prompt: explicit trap list (observed A/B failure modes) + mandatory token-by-token final self-audit instruction |
| E | = D + second self-check/repair pass (blind) |
| F | = A + repair-first self-check (anti-abstention + anti-ref-hallucination instructions, still blind) |
| G | = A + **gate-in-the-loop repair**: the repair pass receives the REAL validator error list for the draft |

Every output is gated by the REAL validators (`gates.mjs`): encoder
`validateExplication` for explications; a verbatim port of the
molecules-v0 §3.5 mechanical gate for grounding notes (closed lexicon,
[m]-flag discipline, ref catalog = kernel-v0 + molecules-v0 depth ≤ 3,
self-reference ban, depth ≤ 4); `cannot-formalise` requires a non-empty
reason. Gate-pass numbers below are **of attempted records** (molecule +
explication outputs); cannot-formalise is reported separately — an honest
abstention is not a failure.

## Results

All numbers n=50 concepts. "Gate-pass" = share of *attempted* records
(molecule + explication outputs) that pass every mechanical gate; the honest
`cannot-formalise` rate (CF) and structurally-invalid-JSON outputs are shown
separately. "Records" = legal records out of 50 concepts.

| fw | pipeline | gate-pass (attempted) | records /50 | CF | parse-fail | calls/concept | API-equiv $/concept | s/call |
|---|---|---|---|---|---|---|---|---|
| A | molecule-first, 1 pass | 2.7% (1/37) | 1 | 16% | 5 | 1 | $0.0059 | 4.4 |
| B | explication-first, 1 pass | 5.4% (2/37) | 2 | 12% | 7 | 1 | $0.0061 | 4.9 |
| C | A + blind self-check | 12.1% (4/33) | 4 | 32% | 1 | 2 | $0.0199 | 6.0 |
| D | hardened 1 pass | 2.6% (1/39) | 1 | 14% | 4 | 1 | $0.0062 | 5.1 |
| E | D + blind self-check | 11.4% (4/35) | 4 | 22% | 4 | 2 | $0.0203 | 5.6 |
| F | A + repair-first blind check | 7.1% (3/42) | 3 | 10% | 3 | 2 | $0.0207 | 5.8 |
| **G** | **A + gate-error-fed repair** | **31.7% (13/41)** | **13** | 16% | 1 | ~1.8* | $0.0202 | 3.5 |

\* in the volume runner the repair pass only runs on gate-failing drafts
(measured: ~84% of drafts), so ≈1.8 calls/concept; the s1 G run repaired all
50 drafts.

**Winner: G.** Feeding the validator's actual error list to a single repair
pass is worth more than every prompt-engineering variant combined (2.6x the
best blind-repair rate; molecule notes — 0-1 passes under A-F — finally pass:
dog, water, rain, boat, gravel, muffin, posse, don). Its 13 legal records per
50 concepts = **26% concept yield**, at ~7 calls per legal record. Pipeline-side
normalization (lowercase + recomputed groundingRefs) recovered zero extra
passes on any framework — every REF_LIST mismatch co-occurs with real
violations — but the runner applies it anyway (free, correct).

**Quality note on repaired records:** repair sometimes buys legality with
thinness — G's `water` lost the human note's life-dependence clause; `muffin`
padded with a vacuous "it is a good thing". Surviving content is *correct*
(nothing wrong was introduced in the 13 passing records on inspection), which
is the right failure direction for a below-Explicated, human-upgradeable
tier.

## Failure-mode analysis

Single-pass (A/B) failures are dominated by ERR_GROUNDING_LEXICON: the model
writes semantically sensible notes in *almost*-controlled English but leaks
ordinary words the closed lexicon forbids — "and", "or", "has", "have",
number words ("four"), inflections not in the pinned table ("falls",
"looks"), bare content words where a ref is required ("water" instead of
`{urn:molecule-v0:water|water} [m]`), and content words with no catalog
entry ("blood", "hungry", "consciousness"). Explication failures are mostly
single local errors: referent-introduction discipline (ERR_REF_NOT_INTRODUCED
— using ref 2 without `bind` outside RelationalSchema), invented roles
("cause", "reason"), and ~10-14% structurally malformed JSON on deep
recursive records.

Error-code distribution (all outputs, counts are individual gate errors):

| fw | ERR_GROUNDING_LEXICON | ref errors (ERR_REF/_LIST/_SELF) | referent/valency (explication) | ERR_JSON |
|---|---|---|---|---|
| A | 187 | 9 | 11 | 5 |
| B | 148 | 2 | 16 | 7 |
| C | 96 | 7 | 8 | 1 |
| D | 146 | 12 | 5 | 4 |
| E | 111 | 2 | 7 | 4 |
| F | 111 | 7 | 16 | 3 |

Observations:
- The self-check pass (C/E) halves lexicon leakage and nearly eliminates
  malformed JSON, but introduces two pathologies of its own: **abstention
  inflation** (C sent dog, water, music, shoe, candle... to cannot-formalise
  — concepts the hand-authored corpus proves are formalisable) and
  **ref hallucination** (repairs invent urn:molecule-v0:wind/moon/blood/
  instrument, which are not in the catalog).
- In-prompt hardening without a second pass (D) does nothing: under
  MAX_THINKING_TOKENS=0 the model does not actually perform the instructed
  token-by-token final audit (A 2.7% vs D 2.6%).
- Pipeline-side normalization (lowercase + recompute groundingRefs — derived
  fields only) recovers **zero** additional passes on A-E: every REF_LIST
  mismatch co-occurs with real lexicon violations. The volume runner still
  applies it (it is free and correct), but it is not a lever.
- The closed grounding lexicon is the hard bottleneck: Haiku writes
  near-controlled English and reliably fails the last 5%% (bare "water"
  instead of a ref; "and"/"or"; off-table inflections like "falls").

## Fidelity vs hand-authored records (agent-judged — single annotator, Claude Fable 5; no inter-annotator agreement; treat as indicative)

Scale: 2 = captures the human record's semantic content (possibly with minor
additions/omissions); 1 = right neighbourhood, meaningful gaps or additions;
0 = wrong, misleading, or unusable.

The fidelity sample is judged on the **single-pass (A) outputs** — the
draft pass fixes the semantic content and the repair pass mostly touches
mechanics (C downgraded 6 of the 15 to cannot-formalise, which would thin
the sample; those downgrades are themselves a finding, see failure modes).
Gate legality is ignored here — this asks only: did Haiku say the right
thing?

| concept | score | one-line rationale |
|---|---|---|
| begin | 1 | temporal-polarity idea partly present (before+NOT); wrong frame; malformed JSON |
| afraid | 2 | human's three elements all present: maybe-bad-will-happen, don't-want, feel-bad |
| believe | 2 | near-identical to human record (THINK-quote-true + NOT-KNOW); one extra weak clause |
| break | 1 | one-thing-becomes-many + cannot-use present; loses time-anchored polarity |
| find | 1 | see+know-where present; human's before-not-knowing replaced by wanting-to-know |
| death | 1 | die + not-live-after present; misses event-kind framing; adds mourning |
| conversation | 1 | reciprocal SAY/HEAR present; clause structure mangled |
| dog | 2 | animal kind, lives with people, mutual good feeling; misses bark-audibility clause |
| water | 1 | drinking/life-dependence approximated; misses hear/touch clauses; adds phase changes |
| red | 2 | human's exact prototype strategy: color kind + fire + blood-descriptive |
| eat | 2 | mouth + into-the-body + food; misses the starvation clause |
| sleep | 1 | body-not-move / eyes-closed align; register break ("consciousness is reduced") |
| house | 2 | live-inside + keeps-water-out (human's rain clause); artifact framing present |
| money | 2 | give/take exchange convention + universal wanting — the human note's core |
| music | 1 | hear + feel present; register break (rhythm/melody); hallucinated instrument ref |

**Mean 1.47/2 — 7/15 fully faithful, 8/15 partial, 0/15 wrong or misleading.**
The semantic content is consistently in the right neighbourhood; what Haiku
cannot reliably do is stay inside the closed lexicon and the strict grammar —
i.e. quality is gated on discipline, not understanding.

## Economics and throughput (measured)

Measured from the runs (claude -p reported usage; Max20 subscription —
dollar figures are API-equivalent accounting, not spend):

- Draft pass (A): mean 742 in / 294 out tokens, ~4.5s/call, $0.0059/call.
- Repair pass (F/G prompt): mean ~1.0k in / ~0.4k out + draft+errors in the
  user turn, ~5.8s/call, $0.014/call. (Prompt-cache reads were inconsistent
  across parallel calls — A/B saw ~4.4k cached tokens/call, C/E/F/G runs saw
  ~0; a serialized warm-up helps but does not fully stick. Cost lever, not
  correctness.)
- G pipeline per concept: ~1.8 calls, ~$0.020 API-equivalent, ~8s of API time
  at concurrency 2 => **~7 calls / ~$0.078 API-equivalent per legal record.**

Session-governed volume projection (governor: 500 calls per 5h window,
concurrency 2, checkpointed — `runner/run-volume.py`, ready, NOT run):

| scope | concepts | calls (~1.8x) | windows | days @3 windows/day | projected legal records @26% |
|---|---|---|---|---|---|
| band A+B (measured gaps + WordNet core) | 3,601 | ~6.5k | 13 | ~4.5 | ~940 |
| bands A+B+C (+ freq list) | 17,990 | ~32k | 65 | ~22 | ~4,700 |
| full inventory | 56,628 | ~102k | 204 | ~68 | ~14,700 |

Wall-clock inside a window is ~20 min of actual API activity — the governor
(shared-plan capacity), not compute, is the binding constraint. Per-window
usage is logged to volume/usage-log.jsonl for maintainer visibility.

## Recommendation

**Conditional GO for the stage-2 pilot; NO-GO for an unattended multi-week
volume run on today's numbers.**

Grounds: the G pipeline (draft + gate-error-fed repair, now the volume
runner's default) turns 26% of concepts into gate-legal, provenance-pinned,
honestly-labelled modelAuthored records at ~7 calls each, abstains honestly
on 16%, and the inspected passing records contain no wrong content (some are
thin). That is real, auditable value per governed window (~70 records +
~40 abstentions per 500 calls) — enough to justify the pre-registered
"hundreds"-scale pilot on kernel-of-truth-63c, which is also where the
open questions get measured at scale:

1. **Second repair round** — untested; plausibly lifts 32% -> 45%+ of
   attempted for +0.8 calls/concept. Measure in the pilot before volume.
2. **Fidelity under repair** — agent-judged here (1.47/2 on drafts; repair
   thins some notes). The pilot should include a human- or stronger-model
   review sample before any coverage claims.
3. **Catalog growth** — the ref catalog is only 108 ids; as molecules-v0
   grows, the expressible space grows. Re-run the s1 sample after the
   next molecule batch to re-measure the ceiling.
4. **Escalation path** — the runner takes any model id; a
   sonnet-draft/haiku-repair A-B on ~50 concepts is a cheap pilot arm if
   26% yield is judged too low.

Recommended pilot shape: 2 windows (1,000 calls ≈ 550 band-A/B concepts),
default governor, then a quality readout in the same format as this report.
