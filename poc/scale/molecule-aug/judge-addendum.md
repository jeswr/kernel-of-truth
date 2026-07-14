# S5 judge addendum — reference-aware AST adequacy

> DESIGN ARTEFACT (DESIGN.md §6). At judge time this addendum is appended to the
> UNMODIFIED base `poc/scale/ast-pipeline/judge_prompt.md`, followed by a
> per-concept `REFERENCED CONCEPTS` block generated mechanically from the
> lexicon (only ids actually referenced by at least one candidate for this
> concept; label + gloss only, never the referenced explications). Applied to
> ALL candidates in a molecule-aug judging run — flat candidates included — so
> the instrument is constant across arms. Verdicts produced under this variant
> are not comparable to verdicts produced under the base prompt.

## Additional rule: concept references

Some candidates may contain nodes of the form `{"kind": "concept", "id": "urn:…"}`
(as an entity filler, or as the target of a `kindFrame`/`partFrame` head). Such a
node is a REFERENCE to an already-defined concept: read it as importing that
concept's full meaning at that position. The referenced concepts' labels and
definitions are listed for you in the `REFERENCED CONCEPTS` block below the
candidates. Candidates that use no references are judged exactly as before.

Calibration for reference-bearing candidates — both directions:

- **Credit real composition.** Genus-by-reference plus rendered differentia is
  legitimate and can be FAITHFUL: "a kind of `teacher` who …" carries the full
  meaning of the referenced *teacher* definition at that position. Do not mark a
  candidate LOSSY merely because it references instead of decomposing.
- **Do not credit a relabelling.** A candidate that merely wraps the concept in a
  near-synonymous reference and adds no criterial differentia — e.g. the whole
  explication is "a kind of X" where X is (near-)synonymous with the concept
  being defined — is a generic skeleton at best and circular at worst: LOSSY,
  quality 0–1. The no-generic-skeleton rule applies to what the references PLUS
  the clauses jointly render.
- **Judge the import at face value.** Take each referenced definition as meaning
  exactly what its listed gloss says — no more. If the candidate's meaning only
  works when the reference is read more broadly or more narrowly than its gloss,
  the surplus is dropped/wrong meaning: weigh it as such.
- **Wrong-reference errors are wrong meaning.** A reference whose imported
  meaning conflicts with this sense (e.g. referencing a *money* concept in a
  sense that is not economic) makes the candidate LOSSY for asserting wrong
  meaning, exactly like a wrong prime clause.

The verdict inventory, the quality scale, and the output format are unchanged.

<!-- REFERENCED CONCEPTS block is appended below this line by the S5 driver -->
