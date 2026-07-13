# concept-def prompt v4 — lexicographic-concision discipline (GPT-5.6 draft, coordinator custody)

Draft addition to append to `concept-def-prompt.md` §3.x, produced by GPT-5.6 (xhigh) from its own
0/5 critique of the v3 smoke output (`quality-review-gpt56.md`). Executes the programme's HARD
scholarly-definition standard. **Not yet integrated/re-tested** — routed to the designer (Fable) to
integrate as v4 and re-run the 5-concept smoke under the two-grader accept gate before ~100 scale.

## Discipline block (append to prompt)

## Lexicographic concision discipline

Write the shortest definition that uniquely preserves the intended synset: normally one apt genus followed by only the differentia needed to distinguish this sense. Every word must delimit the extension, identify the category, or express an essential relation.

- Preserve sense-correctness, part of speech, semantic roles, register, and extension. Never gain brevity by broadening, narrowing, or shifting the sense.
- Remain non-circular: do not use the headword, its inflections, transparent derivatives, or a synonym that merely sends the reader back to it.
- Delete motivation, consequence, mechanism, examples, intensifiers, praise, and repeated paraphrase unless indispensable to the sense. Remove padding such as “in such a way that,” “so that,” “serving to,” and “characterized by.”
- Prefer one exact verb or noun to a descriptive phrase: “costing” rather than “requiring much to be given in exchange”; “prod” rather than “touch abruptly while pressing briefly.”
- Use a natural genus, not a mechanical category tail. Do not append vague pronouns such as “the thing” or open-ended lists such as “or other role or benefit.” Replace them with the precise superordinate term, or retain a closed list only when the sense requires it.
- Avoid evaluative filler such as “great,” “important,” “successful,” or “strong” unless evaluation is criterial.
- Read the result as a dictionary entry, not an explanation. If a phrase can be removed without changing the sense or admitting a neighboring synset, remove it.

Before: “A quality such that one must give much in exchange to obtain the thing.”
After: “The quality of costing a great deal.”

Before: “An act that makes something move toward oneself or in the direction of one’s movement.”
After: “An act of applying force to move something toward or along with the agent.”

Before: “The act of touching someone abruptly and sharply by pressing briefly into the body.”
After: “A sudden, sharp prod with a finger or elbow.”

## Two-grader accept gate

Accept only when both records independently pass: (1) the generator records that the definition is synset-correct, non-circular, extension-preserving, idiomatic, and irreducibly concise; and (2) a strong separate model, shown the lemma, part of speech, synset/gloss, and proposed definition, answers yes to: “Would a first-rate scholarly English dictionary accept this wording without correction for sense, circularity, extension, diction, or unnecessary information?” Any no or disagreement triggers regeneration; after two failed regenerations, escalate for human lexicographic review.

## Residual risk (disclosed)

This discipline cannot reliably detect an incorrect or underspecified source synset, nor every subtle register or collocational mismatch. The cheapest check is a lemma-and-synset comparison against one authoritative dictionary entry or corpus evidence.

## Author self-check

Confirmed: the block explicitly preserves the intended synset, extension, part of speech, and semantic roles, and forbids headword-based or derivative circularity; concision is permitted only after those constraints are satisfied.
