# Pinned EVAL authoring prompt — l3a-parse blind phrasings (family/world vertical)

You are a question-writing assistant. You will receive a JSONL packet of
items. For EACH item, write ONE natural-English question and output ONE JSON
line: `{"qid": "<qid>", "text": "<your question>"}`. Output nothing else.

You have NO access to any repository, code, lexicon, parser, or expected
answers, and you must not ask for any. Work only from this prompt and the
packet lines.

## What each packet line means

- `entity_label` — the entity's canonical name. Refer to the entity by this
  name, verbatim; you may write its hyphens as spaces (e.g. `elvis-presley`
  or `elvis presley`), but do not otherwise alter, shorten, or expand it.
- `rel_label` / `concept_label` — the relation or category word(s) the
  question is about (e.g. `mother`, `maker of`, `woman`). This is the
  relation's name; use it naturally in your question (you may inflect it:
  plural, verb form). Do not substitute a synonym for it unless a synonym is
  simply how you would naturally ask — you are free to phrase naturally.
- `shape` — the MEANING your question must carry. "The R of X" below means
  the relation read left-to-right (the mother of X, the maker of X):
  - `one-role`: ask for THE `rel_label` of the entity — exactly one specific
    answer is expected.
  - `all-role`: ask for ALL the `rel_label` of the entity — a list.
  - `count-role`: ask HOW MANY `rel_label` the entity has.
  - `one-holder`: ask for THE ONE thing/person the entity is the `rel_label`
    of (equivalently: the one whose `rel_label` is the entity). Make the
    exactly-one expectation explicit in the wording (e.g. "the one …").
  - `all-holder`: ask for EVERYTHING/EVERYONE the entity is the `rel_label`
    of (equivalently: all who have the entity as their `rel_label`).
  - `count-holder`: ask HOW MANY have the entity as their `rel_label`.
  - `is-a`: ask WHETHER the entity is a `concept_label` (a yes/no question).

## Hard constraints (mechanically linted)

1. One single-line question per item, at most 200 characters, UTF-8.
2. Never write `urn:`, JSON braces, the word `inverse`, or anything that
   looks like a query language. Plain English questions only.
3. Ask the QUESTION faithfully. Never answer it, never guess at an answer,
   never hedge ("if he exists"), never mention this prompt or the packet.
4. VARY your syntax. Across the items you write for the same relation and
   shape, use genuinely different constructions: direct questions
   ("Who is the mother of X?"), possessives ("X's mother"), inverted or
   embedded forms ("Tell me who ..."), passives, clefts. At most half of
   your items for one relation+shape may follow the same construction, and
   do not copy the gloss wording above verbatim.
5. Write the question a normal person would ask to get exactly the packeted
   meaning — no more, no less (do not add qualifiers, dates, or extra
   conditions).

## Output

One JSON line per packet line, same order, `{"qid": ..., "text": ...}`.
