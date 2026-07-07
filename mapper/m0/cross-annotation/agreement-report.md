# M0a cross-model annotation — codex-gpt vs Claude-agent agreement

**Date:** 2026-07-07 · **Sample:** `../annotation-sample.jsonl` (300 items; 100 concept /
100 prime / 50 abstain / 50 none) · **Annotator A:** agent (Claude Fable 5),
`../agent-judgments.jsonl` · **Annotator B:** OpenAI Codex CLI v0.142.5, model
**gpt-5.5** (reasoning effort: none — the CLI default), 15 serial batches of 20 via
`codex exec`, all 15 parsed on the first attempt, 0 retries, 0 failed batches. Raw
prompts/outputs in `raw/`; parsed judgments in `codex-judgments.jsonl`
(`annotator: codex-gpt`); machinery in `run-codex-annotation.py`; numbers from
`agreement-analysis.py` → `agreement.json`, `disagreements.jsonl`.

## Framing — read this first

Two AI annotators agreeing is **weak evidence of correctness**: both models were
trained on overlapping data and can share failure modes (e.g. both being lenient about
light-verb senses, both mis-modelling NSM copula semantics), so agreement here must not
be read as validation and **does not satisfy the pre-registered human-annotation item**
(poc-design.md Phase M). The value of this pass is (1) the **disagreement set** — 61
items where at least one AI annotator is wrong, which is the highest-yield place for
human attention — and (2) a **bound on how much the provisional P/R could move** under a
different annotator. A further asymmetry limits the none stratum: codex was *not* shown
the kernel-v0 inventory (54 concept labels + 65 prime exponent lists), so its
"should have mapped" judgments there are semantic coverage claims that may name targets
the kernel does not contain; the strict output contract (judgment only, no trueTarget)
means we cannot tell which. Codex also used `unclear` **zero** times in 300 judgments
(Claude: 11), consistent with a shallow, no-deliberation pass.

## Agreement (labels normalised to correct|incorrect|unclear = "was the mapper's decision right?")

| stratum | n | raw agreement | Cohen's κ |
|---|---|---|---|
| concept | 100 | 0.91 | 0.62 |
| prime | 100 | 0.89 | 0.64 |
| abstain | 50 | 0.50 | 0.17 |
| none | 50 | 0.68 | 0.00* |
| **overall** | **300** | **0.80** | **0.45** |

*κ = 0 on the none stratum because the Claude side has no label variance (50/50
correctly-unmapped); raw agreement is the informative number there.

Disagreements: **61** (concept 9, prime 11, abstain 25, none 16), ranked concept-first
in `disagreements.jsonl`. The direction is systematic, not random:

- **Mapped strata — codex more lenient.** 7 concept items Claude judged incorrect,
  codex correct (take=transport ×2, right=suitable/correct ×2, find=realize,
  find-its-way idiom, lie=recline); 2 unclear→correct. On primes codex broke Claude's
  9 unclears 3 correct / 6 incorrect and flipped 2 corrects to incorrect
  (`a`→A-LONG-TIME, `times`→WHEN~TIME). Net: sense-strictness standards differ.
- **Abstain — codex far harsher on the mapper.** All 25 disagreements are copulas
  (was ×14, were ×3, is ×3, are ×2, be ×2, i'm ×1): Claude called attributive/auxiliary
  copulas "grammatical glue, correctly abstained"; codex says a candidate
  (BE-SOMEWHERE / BE-SPEC / THERE-IS) was correct. Codex: 43/50 abstains had a correct
  candidate; Claude: 18/50. This is a single policy question — the NSM treatment of
  copulas — not 25 independent judgments.
- **None — codex claims 16/50 should have mapped** (Claude: 0/50): loved ×2, or, play,
  walked, into, put, spent, day, again, press, brave, dog, around, go, house. By mapper
  construction none of these has a lexicon entry for surface or lemma. Several name
  nothing in kernel-v0 at all (loved, play, dog, house, brave, or — no such
  concept/prime), so they cannot be recall misses under the pre-registered definition;
  others are at least arguable against the real inventory (into→INSIDE,
  day→WHEN~TIME, go/walked/put/around→MOVE, spent→FOR-SOME-TIME, press→TOUCH) and are
  genuine human-adjudication material.

## P/R sensitivity (compute-pr.py logic, codex judgments substituted; strict counts unclear as incorrect/miss)

| | precision (strict) | per-stratum P (concept/prime) | recall (strict) | abstain miss | none miss |
|---|---|---|---|---|---|
| Claude agent (report) | 0.820 | 0.82 / 0.82 | 0.887 | 0.36 | 0.00 |
| codex-gpt | 0.845 | 0.91 / 0.83 | 0.323 | 0.86 | 0.32 |
| decomposition: codex abstain only | 0.845 | — | 0.771 | 0.86 | 0.00 |
| decomposition: codex none only | 0.845 | — | 0.342 | 0.36 | 0.32 |

**Precision is robust to annotator identity** (0.82 → 0.85; it barely moves, and moves
*up*): whichever AI judges, the headline precision claim stands to within ~3 points.
**Recall is not robust** (0.887 → 0.323) — so for recall **the human pass matters even
more than the M0a report already says**. Under codex's reading, recall falls *below* the
report's stated 0.68 lower bound, because that bound covered only sampling error on the
0/50 none stratum, not annotator disagreement about criteria. The drop decomposes into
(a) the copula-abstention policy question alone pulling 0.89 → 0.77, and (b) the
none-stratum claims alone pulling 0.89 → 0.34 — with the caveat above that an unknown
(likely large) share of (b) dissolves against the actual inventory.

## Where the human should focus first

1. **Copula abstain items** (25 disagreements + 18 agreed-miss = 43 flagged of 50):
   one policy decision — when is an English copula a correct BE-SOMEWHERE/BE-SPEC/
   THERE-IS instance vs grammatical glue — resolves half the disagreement list and a
   ±0.12 recall swing. Highest leverage per minute spent.
2. **The 16 none-stratum items**, judged *with the kernel-v0 inventory in hand*;
   prioritise into/day/go/walked/put/around/spent/press (plausible in-inventory
   targets) over loved/play/dog/house/brave/or (no target exists).
3. **The 9 concept + 11 prime disagreements** — these set the sense-strictness standard
   (light verbs, take=transport, right=suitable, "one day", copular idioms) that the
   headline precision number rests on.
