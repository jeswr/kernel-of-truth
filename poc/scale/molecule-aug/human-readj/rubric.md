# Blind HUMAN fidelity adjudication — rubric (s5-human-readj/1)

> INSTRUMENT ARTEFACT, frozen under registry/experiments/s5-human-readj.json.
> Derived from the pinned proxy instrument `s5-judge-fidelity-v2.1.md`
> (FREEZE-v2.1.json `s5_judge_fidelity_v21_sha256 6fa6da2e…2ec4`): the SAME
> criterial-feature checklist and the SAME mechanical verdict rule, re-addressed
> to a human adjudicator. Differences from the proxy instrument, exhaustively:
> (1) addressed to a human, answers go in a spreadsheet row, not strict JSON;
> (2) a CANNOT-SAY escape is available; (3) the 0–3 quality score is DROPPED
> (verdict only; quality was a proxy secondary, not re-measured here); (4) the
> F3/adjudicator section is DROPPED (reconciliation.md replaces it). Nothing
> else is changed. Judging under any other instruction is off-protocol.

You are one of two independent adjudicators of semantic explications. You will
receive 95 items, one at a time, in the fixed order of your answer sheet. Each
item is ONE concept and ONE anonymised candidate explication of it.

## Process rules (binding)

1. **Independence.** Work alone. Do not discuss any item, verdict, or
   impression with the other adjudicator — or anyone else — until BOTH complete
   answer sheets have been handed to the coordinator. A separate, pinned
   reconciliation step follows; it is the only place discussion is allowed.
2. **Blindness.** You do not know, and must not try to guess, where any
   candidate came from — which system, which method, which condition, or how
   any other judge scored it. Provenance is unknowable and irrelevant; surface
   features such as length, nesting, or style of composition tell you nothing
   you may use. Judge every candidate strictly on its own merits against its
   concept.
3. **No comparison, no memory.** Items are independent. Do not compare
   candidates across items, revisit earlier verdicts because of later items, or
   try to balance your counts. Some items may be near-duplicates; judge each
   independently all the same.
4. **No machine assistance.** No LLM, chatbot, or AI tool of any kind, for any
   part of the task. An ordinary dictionary for the everyday sense of a
   concept word is permitted; project materials, this repository, and web
   search about the task are not.
5. **One pass per item.** Read the item, run the decision procedure below,
   record the row, move on. You may fix a slip if you notice it immediately,
   but do not run systematic second passes over your sheet.

## Input

```
concept: <word or phrase>
synset: urn:lexical-wn31:<pos>-<offset>
pos: <n|v|a|r>
lemmas: <lemmas>
wn31-gloss (sense-fixing only): <WordNet gloss — fixes WHICH sense is meant>

=== CANDIDATE A ===
<a kot-ast/1 explication as JSON>
```

The WordNet gloss fixes which sense is meant and nothing more; your
scholarship determines that sense's true intension: its **genus** (what kind
of thing it is) and its **criterial differentia** (what distinguishes it from
its siblings under that genus — the components whose removal would let a
different concept satisfy the definition).

## The metalanguage the candidates must live within

A kot-ast/1 explication is a compositional reductive paraphrase built ONLY
from the 65 profile-1 semantic primes. Structure: frames (`InstanceSchema`,
`WhenTrue`, `RelationalSchema`), predications with role slots, operators
(`NOT`, `CAN`, `MAYBE`, `IF`, `BECAUSE`, `WHEN`, `LIKE`, `AFTER`, `BEFORE`),
substantive phrases with determiners/quantifiers/mods and `kindFrame` /
`partFrame` heads, embedded and quoted clauses, up to 32 clauses — so LENGTH
is not the limit; only the reach of the primes is. The 65 primes:

- substantive: I, YOU, SOMEONE, SOMETHING~THING, PEOPLE, BODY
- relational-substantive: KIND, PART
- determiner: THIS, THE-SAME, OTHER~ELSE~ANOTHER
- quantifier: ONE, TWO, SOME, ALL, MUCH~MANY, LITTLE~FEW
- evaluator: GOOD, BAD — descriptor: BIG, SMALL
- mental: THINK, KNOW, WANT, DON'T-WANT, FEEL, SEE, HEAR
- speech: SAY, WORDS, TRUE
- action/event/movement: DO, HAPPEN, MOVE
- location/existence/specification/possession: BE-SOMEWHERE, THERE-IS, BE-SPEC, IS-MINE
- life/death: LIVE, DIE
- time: WHEN~TIME, NOW, BEFORE, AFTER, A-LONG-TIME, A-SHORT-TIME, FOR-SOME-TIME, MOMENT
- space: WHERE~PLACE, HERE, ABOVE, BELOW, FAR, NEAR, SIDE, INSIDE, TOUCH
- logical: NOT, MAYBE, CAN, BECAUSE, IF
- intensifier/augmentor: VERY, MORE — similarity: LIKE~AS~WAY

**Candidates are fully expanded.** Every candidate has been mechanically
rewritten so that it contains ONLY profile-1 prime material. Where an
explication composed in another already-defined concept, that concept's own
explication has been inlined in place as a nested
`{"kind": "subExplication", "frame": …, "referents": […], "clauses": […]}`
block. Read a `subExplication` block as a self-contained sub-definition whose
full meaning applies at that position (its `referents` indices are local to
the block). Judge the meaning the nested material ACTUALLY renders in primes —
you are never asked to take any gloss or label on credit; none are shown.
Do not penalize (or reward) size, nesting, or style of composition as such.

## Decision procedure (mandatory, in this order)

**Step 1 — CRITERIAL FEATURES.** From the concept header (the sense-fixing
wn31 gloss plus lemmas/pos), enumerate 2–6 criterial features of THIS sense:
the genus (what kind of thing it is) and each differentia that distinguishes
this sense from its nearest neighbours and siblings. Number them. What is NOT
criterial: encyclopedic detail, typical-but-not-defining properties, register,
connotation, and anything true of the genus generally.

**Step 2 — FEATURE AUDIT.** For each numbered feature, classify it against the
RENDERED MATERIAL ONLY (primes + inlined subExplication content):
- **PRESENT** — the rendered clauses entail the feature. An approximate
  rendering counts as PRESENT if it still separates this sense from its
  siblings; prime-level paraphrase is the norm here, not a defect.
- **MISSING** — no rendered material carries the feature.
- **CONTRADICTED** — rendered material asserts something incompatible with the
  feature (or with the sense).

**Step 3 — MECHANICAL VERDICT.** `FAITHFUL` iff every criterial feature is
PRESENT and none is CONTRADICTED; otherwise `LOSSY`. No holistic override in
either direction: do not upgrade a MISSING-feature record because it "feels
close", and do not downgrade an all-PRESENT record because it is bloated,
ugly, or nested.

Calibration, both directions:
- Do NOT demand encyclopedic detail. If the WordNet gloss names an artefact,
  institution, or substance, what matters is whether the explication carries
  the CRITERIAL work that thing does in this sense (what people do with it,
  want from it, what happens because of it). Non-criterial encyclopedic
  residue does not make a candidate LOSSY.
- Do NOT credit a generic skeleton. An explication that is merely compatible
  with the concept — one that fits many sibling concepts equally well — is
  LOSSY even if nothing in it is false. Wrong assertions (meaning the sense
  does not have) also make it LOSSY.
- Judge the rendering that is actually there, not the best rendering you can
  imagine. A concept may be renderable in principle while a given candidate
  still fails.

### Micro-anchors (synthetic, not from any evaluation set)

- Concept "vow (a solemn promise)"; rendering says: someone says words to
  someone; because of this, this someone has to do something after now; this
  someone wants the other someone to know it is true. Features: 1 genus
  speech-act/promise: PRESENT; 2 commitment created: PRESENT; 3 solemn/binding
  seriousness: PRESENT (has-to + truth clauses carry it approximately) →
  **FAITHFUL**, even though "solemn" is rendered only approximately.
- Concept "orphan (a child whose parents are dead)"; rendering says: this
  someone is small; this someone is not with the mother and father. Features:
  1 genus child: PRESENT; 2 parents DIED: MISSING (absence ≠ death) →
  **LOSSY**, however well-formed the rest is.

## Your answer, per item (three spreadsheet columns)

- **verdict** — exactly one of `FAITHFUL`, `LOSSY`, `CANNOT-SAY`.
  `CANNOT-SAY` is an escape, not a middle grade: use it ONLY when you cannot
  run the procedure at all (you cannot determine the intended sense, or you
  cannot parse the candidate well enough to audit it). "Hard to decide" is not
  CANNOT-SAY — the mechanical rule decides hard cases.
- **missing** — the MISSING/CONTRADICTED feature(s), one short clause each;
  empty if none (or if CANNOT-SAY, why you could not judge).
- **audit** — your compact numbered audit, e.g.
  `1 genus event: PRESENT (clause 1); 2 spouse died before: MISSING; 3 …`.
  Mandatory for every item; it is what the reconciliation step works from.

Expect roughly 2–5 minutes per item; ~95 items total. Accuracy over speed —
but the verdict rule is mechanical: run it and record what it says.
