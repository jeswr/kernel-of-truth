# molecules-v0 — the semantic-molecule tier, v0

54 molecule records authored against the normative molecule rules in
concept-hash-design.md §3.5, selected to maximise measured TinyStories
coverage gain over the M0b molecule-needing class
(`mapper/m0/results/m0b-report.json`). Design record:
`docs/design-molecule-tier.md`. Measured coverage delta:
`mapper/m0/results-molecules-v0/`.

## What this is — and is not

**Research-grade, agent-authored; NOT federation-endorsed.** The gist is
explicit that molecule admission "is an explicit endorsement act" with
"deliberately no mechanical decomposability test" (§3.5 rule 6): these
records satisfy every *mechanical* rule (the hard gates below), and nobody
has performed the endorsement judgement. Every record carries
`researchGrade: true` and a `notes` field stating its known weaknesses.

Ids (`urn:molecule-v0:<slug>`) are **placeholder URNs**, exactly like
kernel-v0's — minting content-addressed `urn:concept:` identities is the
concept-hash pipeline's job.

## Contents

- `molecules/*.json` — one molecule per file: `{id, label, semanticStatus:
  "Molecule", flag: "[m]", groundingNote, groundingRefs, moleculeDepth,
  axioms: [], partialExplication: null, researchGrade, notes, corpusLemmas}`.
  `corpusLemmas` lists the top-500 TinyStories lemmas whose dominant sense
  the record covers (label first, then synonym surfaces) — the hook into the
  coverage measurement.
- `manifest.json` — ordered mint list (order is topological: grounding refs
  point only to kernel-v0 or *earlier* molecules), depths, per-record refs.
- `validate.mjs` — the mechanical §3.5 gate. All 54 must pass.

## The gates (validate.mjs, all fail-closed)

1. **Rule 1** — `semanticStatus: "Molecule"`, `[m]` flag surfaced on the
   record AND after every molecule ref inside grounding notes (kernel refs
   must not carry it).
2. **Rule 3** — exactly one grounding note; ≤1,024 bytes NFC; every token is
   a pinned prime exponent / pinned function-word allolex ("glue") /
   closed punctuation / linked ref `{urn:…|gloss}`. The glue table is
   molecules-v0's pinned choice — the gist delegates it to the (not yet
   existing) profile bundle; changing it is a corpus version change.
3. **Rule 4** — refs resolve only to kernel-v0 ids or earlier-minted
   molecules ⇒ grounding cycles are impossible by construction.
4. **Rule 5** — molecule depth ≤ 4 (primes and kernel-v0 explications are
   depth 0). Current max: 4 (`father`, via man → woman → child).

Rule 2 ("as much partial explication as the concept bears") is deliberately
NOT satisfied in v0: records carry `axioms: []` and
`partialExplication: null`. Authoring partial explications requires the
schema extension specced in the design note (kot-ast ConceptRef cannot yet
bind molecule vectors) — see the filed beads.

## Validation

```sh
node data/molecules-v0/validate.mjs   # exit 0 iff all 54 records pass
```
