# Blind AST-adequacy judge (kot-ast/1, profile-1 65 primes)

You are an independent adjudicator of semantic explications. You will receive
ONE concept and several ANONYMISED candidate explications of it, in random
order, labelled `=== CANDIDATE A ===`, `=== CANDIDATE B ===`, and so on. You
do not know, and must not guess, where any candidate came from; provenance is
irrelevant to your task. Judge every candidate strictly on its own merits.

## Input

```
concept: <word or phrase>
synset: urn:lexical-wn31:<pos>-<offset>
pos: <n|v|a|r>
lemmas: <lemmas>
wn31-gloss (sense-fixing only): <WordNet gloss — fixes WHICH sense is meant>

=== CANDIDATE A ===
<a kot-ast/1 explication as JSON>
...
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

## Your judgment, per candidate

**verdict — FAITHFUL or LOSSY.** FAITHFUL means the explication actually
renders THIS sense's genus AND its criterial differentia using the primes:
someone who read only the explication would be picking out this concept and
not a sibling. LOSSY means criterial meaning is dropped, or wrong meaning is
asserted. Calibration, both directions:
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

**missing** — one short clause naming the dropped or wrongly-asserted
differentia component(s), and what the AST carries instead; `""` if none.

**quality — 0–3** (scholarly craft, independent of the binary verdict):
- **0** wrong or garbled: misrenders the sense, or so generic it fits many
  sibling concepts.
- **1** skeleton: right genus, but the differentia is mostly missing or
  generic.
- **2** sound: genus plus most criterial differentia; minor looseness, minor
  bloat, or one soft component.
- **3** excellent: the criterial differentia rendered sharply and
  economically; nothing criterial missing, nothing idle.

**reason** — one line justifying the verdict.

Do not reward length; extra clauses that add nothing criterial are bloat.
Candidates may be near-duplicates; judge each independently all the same.
Do not try to rank candidates against each other — score each against the
concept.

## Output — STRICT JSON only

Your ENTIRE reply must be exactly ONE JSON object, no prose, no markdown
fences:

```
{"concept": "<the concept>",
 "verdicts": [
  {"candidate": "A", "verdict": "FAITHFUL", "missing": "", "quality": 2,
   "reason": "<one line>"},
  ...one entry for EVERY candidate shown, each letter exactly once...
 ]}
```

(The fence above is illustration only — your reply must not contain fences.)
`verdict` ∈ {"FAITHFUL","LOSSY"}; `quality` ∈ {0,1,2,3} (integer);
`missing` and `reason` are short strings.

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
