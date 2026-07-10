# instance-descriptions — G3 candidate materials (necessity-vs-sufficiency violation set)

Input materials for **G3**, the HS3 semantics-pin annotation study
(`registry/experiments/g3.json`, frozen_sha256
`ef9608c60fc0355074b2d50132bbc79cbe49c5e9b578c724d81d31ce95bef7aa`; P1 §4 HS3;
P3 `g3.inputs`). The frozen record's corpus pin for this directory is the
placeholder `PINNED-AT-INPUTS:g3.materials`; an **ops amendment** computes the
kot-corpus-hash/1 digest of this directory before any final-phase run. Nothing
here edits the frozen record.

## What this is — and is NOT

**CANDIDATE stimuli only. There is no gold anywhere in this corpus.**
[STIPULATED: ASM-0181] [STIPULATED: ASM-0182]

- 20 kernel-v0 concepts × 10 instance descriptions = **200 instances**
  (matching the frozen `n_planned`: 20 × 10, 200 instance judgments).
- Each concept's 10 instances are authored in three strata
  (**design intent, not gold**): 4 satisfying **controls** (typical instances
  expected to satisfy every explication condition), 3 **necessity-stress**
  candidates (arguably genuine instances of the concept, each constructed so
  that one specific explication condition plausibly fails), and 3
  **sufficiency-stress** candidates (near-miss non-instances constructed to
  satisfy as many explication conditions as possible).
- Whether any instance actually violates anything is **decided by the human
  annotation pass, not by the authoring intent**. A stress candidate becomes a
  confirmed violation only if annotators judge, blind to intent, that the
  concept applies while the conditions fail (necessity) or that the conditions
  hold while the concept does not apply (sufficiency). If the explications are
  sound, the stress candidates get rejected on one side or the other and no
  violation is recorded — the composition does not preordain the verdict.

## Files

| file | role | annotator-visible? |
|---|---|---|
| `instances.jsonl` | 200 stimuli: `instance_id, concept_id, condition_set_id, target, bindings, text` | via generated sheets only |
| `conditions.jsonl` | 20 enumerated condition sets (clause-wise rendering of each record's `gloss`), opaque ids K-01..K-20 | via pass-B sheets only |
| `design-intent.jsonl` | authoring stratum + targeted condition per instance — **NOT GOLD, never annotator-visible** | **never** |
| `annotation-protocol.md` | the two-pass annotation procedure + sheet spec + what the human pass decides | yes (instructions section) |
| `manifest.json` | counts, selection/ordering rules, pins, ASM ids | no |

Presentation order = file order of `instances.jsonl` (concept blocks and
within-block order deterministically shuffled under `kot-g3-mat/1|seed=0`,
the frozen record's `seeds:[0]`); instance ids were assigned **after** the
shuffle so id order carries no stratum signal. Instance texts never contain
the concept word or a close derivative (per-concept banned-lemma scrub); the
`target` claim and `bindings` carry it deliberately — they state the judgment.

## Concept selection [STIPULATED: ASM-0180]

Non-`knownWeak` kernel-v0 concepts only (the 22 flagged-weak records measure
authoring quality, not the semantics pin), frame-stratified quotas 6/6/8
(proportional to the corpus's 17/16/21), ranked by
`sha256("kot-g3-mat/1|seed=0|" + slug)`; `promise` (the HS2 litmus) would have
been force-included but ranked in naturally. Selected:

- InstanceSchema: lie, birth, bookmark, promise, reminder, death
- WhenTrue: lost, angry, afraid, broken, archived, useful
- RelationalSchema: end, give, begin, make, find, repair, believe, friend

Scope consequence: a G3 verdict on these materials licenses claims about the
non-flagged kernel-v0 explications; it says nothing about the `knownWeak` set.

## Composition and decidability [STIPULATED: ASM-0181]

Per concept 4/3/3 (control / necessity-stress / sufficiency-stress); totals
80/60/60. With the pinned analysis (`analysis/g3.py`, one-sided Wilson bounds
at z = 1.645, n = 200): **PASS** (upper bound ≤ 0.10) requires **≤ 13**
confirmed violations; **FAIL** (lower bound > 0.10) requires **≥ 27** — both
computed directly from the pinned formula. Each 60-instance stress lane
therefore makes BOTH branches of the frozen two-decision rule reachable
(≥ 27 of 60 confirmable, ≤ 13 of 60 deniable); a smaller lane (e.g. 20) could
never trip FAIL on its own and would bias the instrument toward PASS.
Interpretation consequence: the measured rates are violation rates **over this
deliberately stress-stratified candidate set** — a hard test of the ∀-shaped
pin C ⊑ Π(C), not an estimate of violation frequency in natural text. Any
readout must say so.

## What the human annotation pass must decide (out of scope here)

Two independent annotators (GATE-H `g3.annotate`, blind to hypotheses and to
`design-intent.jsonl`), per instance:

1. **Q1 (concept judgment, pass A):** is the `target` claim true of the
   situation in `text`, under the annotator's ordinary understanding of the
   concept word? (yes / no / cannot-say)
2. **Q2 (condition judgment, pass B):** does the situation satisfy **every**
   condition in the concept's condition set, with the referents fixed by
   `bindings`? (yes / no / cannot-say, plus which condition(s) fail)

Derived per the frozen design (P1 HS3 / F7 verbatim):
**necessity violation** := Q1 yes ∧ Q2 no; **sufficiency violation** := Q1 no
∧ Q2 yes. The analysis consumes only the counts (`n_judgments`,
`n_necessity_violations`, `n_sufficiency_violations`, and the 2×2
inter-annotator table on the necessity judgments) via `analysis/g3.py`.

Run-stage decisions this corpus does NOT make (for the `g3.annotate` owner):
annotator sourcing (O-3, deferred by maintainer direction), how the two
annotators' judgments combine into the single violation counts (the g2
precedent is blind adjudication of disagreements before scoring; G3's frozen
record requires only that κ be reported and n_judgments = 200), and handling
of cannot-say responses. These must be fixed before annotation starts.
