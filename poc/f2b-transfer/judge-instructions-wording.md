# f2b-transfer §4.7 — human-facing judge wording (FABLE-authored, correction 1)

> Plain-language renderings of the §4.7 adjudication standards (design.md,
> this directory) for the two judge instruments. AUTHORED BY FABLE as part of
> the pre-data clarification; APPLIED BY OPUS mechanically (re-render CSV +
> README + judge-2 template, recompute shas, reset-refreeze). The blind item
> bytes (`judge-1-package/items-judge-1.jsonl`) are NOT touched by any of
> this — no re-draw occurs. Every block below is answer-neutral, constant
> across items/options/polarities, and usable by a kernel-blind judge; none
> mentions the kernel, provenance, membership, or intended answers.

## A. judge-1 CSV — replacement INSTRUCTIONS block

Replaces the whole `INSTRUCTIONS` list in the successor of
`opus-runs/20260709T174657Z/build-judge1-csv.py` (a fresh Opus run dir; do
not edit the logged run). Lines 1–4 and the last three lines are carried
over unchanged; lines 5–10 are new or rewritten. The superseded line
"IMPORTANT — 'close but not quite right' ... answer NONE" is REMOVED — it is
replaced by lines 6–8 below (see §4.7 A-direction disclosure).

1. READ THIS FIRST — this single file is everything you need. Please answer every one of the 360 items in the table below and send the file back. It takes about 2 hours (~20 seconds per item).
2. You are 'judge-1'. Do NOT write your name, email, or anything that identifies you anywhere in this file — you are recorded only as 'judge-1'.
3. ELIGIBILITY: please only do this if you have NEVER read this project's concept / 'kernel' definition records. The task measures whether an ordinary everyday understanding of common words agrees with those records, so having seen them would invalidate your answers. If you have seen them, please hand this to someone who has not.
4. YOUR TASK: for each item, answer from your OWN everyday understanding of the words involved (everyday things like bird, eat, sleep, water, jump). There is no trick and no 'intended' answer to guess.
5. HOW THE TEXTS READ: the definition texts use a deliberately tiny, plain vocabulary, so the grammar can sound odd — "a something of kind event" just means "an event"; "somethings of kind take happen" just means "acts of taking happen". Odd wording is never a trick and never by itself a reason to reject an option or a statement. The letters X and Y stand for the participants named with the word itself: in "break (X breaks Y)", X is the one who breaks and Y is what gets broken. A parenthesis after a word — like "right (of a doable something)" — just tells you which sense of the word is meant; if a parenthesis contains unfamiliar technical notation, ignore the notation and use the plain word. Square brackets like "[the bookmark]" are clarifications — read them as part of the text.
6. MULTIPLE-CHOICE items ("Which option gives the meaning of X" / "a word whose definition is: ..."): pick the option that correctly gives the meaning. An option is correct when (a) everything it says fits the word as you understand it, AND (b) as a whole it actually says what the word means — from it you could tell THIS word is being defined and not something else. Read each sentence the way ordinary definitions speak: as saying what is NORMALLY or TYPICALLY the case ("birds fly" is a fair thing to say even though penguins don't), and phrases like "at some times", "can", "many", "some" only claim what they say.
7. EXTRA TRUE DETAILS ARE FINE: if an option says something TRUE about the thing that a dictionary might leave out (say, a definition of "bird" adding that hearing birds can feel good), that does NOT make the option wrong — never answer NONE because of true extra detail. What DOES make an option wrong: anything in it that is FALSE of the thing, or that fits some other thing instead — or an option that is only a pile of true facts and never says what the thing actually IS.
8. IF MORE THAN ONE OPTION SEEMS RIGHT: pick the one that best and most exactly gives the meaning of the asked word itself, not of something closely related (the EVENT of dying is not the meaning of the word "dead"). Answer NONE only if NO option is genuinely correct, or if you cannot decide — both are the same answer, NONE; you can say which in the comment. NONE is a valid, expected answer — never treat it as a mistake.
9. YES/NO items ("According to the definition of X, is the following true of X? ..."): the quoted statement is a FRAGMENT taken from a longer description, so words like "this someone", "this something", "it", or a stray quote mark may point at things the fragment doesn't show — read it charitably, as a piece of a description of X's normal situation. Then answer: yes — if it says something that belongs to what X means as you understand it, or follows from it; things that are NORMALLY/TYPICALLY true of X count as true, and hedged phrases only claim what they say. no — if it does not fit what X means: it is false of X, or only rarely or accidentally true of X, or it really has nothing to do with X (if what X means neither says nor implies it, the answer is no — including statements so generic they say nothing about X in particular). cannot say — ONLY if you cannot understand the statement well enough to judge it at all, or you genuinely cannot decide. Do not use "cannot say" just because a statement is oddly worded, partial, or only typically true — and do not use "no" as a soft "cannot say": "no" means it does not fit X.
10. Some statements repeat under different words. Judge each item only against its own word — never reuse an earlier answer or look for a pattern across items.
11. The 'comment' column is OPTIONAL free text and is genuinely helpful: if an option is close-but-not-quite, or an item seems ambiguous, odd, or hard to call, feel free to note briefly why. It is never required.
12. Fill the 'your_answer' column for EVERY position. The valid answers for each item are shown in its 'allowed_answers' column.
13. PRACTICAL: work top to bottom in one sitting if you can. Please do NOT go back and 'correct' earlier answers to fit a pattern you think you see — your first-read judgement is exactly what we want. Do not look anything up about the project, the words, or any 'kernel'.

## B. judge-1 README — deltas

1. REMOVE from the maintainer note the sentence claiming the "close but not
   quite right → NONE" guidance is the frozen §4's own stance (it was a
   rendering over-reading; §4.7 supersedes it), and re-point it at the
   re-rendered CSV.
2. In "Your task", after the two format bullets, ADD: "How to judge them —
   the standards are spelled out inside `judge-1-adjudication.csv` itself
   (instruction lines 5–10) and are the authoritative §4.7 of `PROTOCOL.md`;
   in short: odd simplified grammar is never a reason to reject; true extra
   detail never makes an option wrong, false or misfitting content always
   does; yes/no statements are judged as typical-case claims about what the
   word means."
3. In "The mandatory escape", REPLACE the final sentence ("Do not force a
   choice. If the options do not describe the concept as you understand it,
   'NONE' / 'cannot say' is the correct answer.") WITH: "Do not force a
   choice. If no option correctly gives the meaning, NONE is the correct
   answer; if a statement cannot be judged at all, 'cannot say' is. But do
   not escape over style: odd wording, simplified grammar, or true extra
   detail is never by itself a reason for NONE, and 'cannot say' is never a
   soft 'no'."
4. "Authoritative rules" paragraph: unchanged (PROTOCOL.md remains the
   verbatim copy of §4 — now including §4.7 — and remains the authority).

## C. judge-2 pinned prompt template — replacement block

In `data/d-adj-t/judge-2-prompt-template.txt` (placeholder pin still
unfilled, so lawful to update pre-adjudication; recompute the sha256 quoted
in `data/d-adj-t/judge-2-prompt.md` and extend its rationale table with one
row: "judging standards block | §4.7 S1–S7, near-verbatim from judge-1 CSV
lines 5–10 — one protocol for both judges"). REPLACE the two paragraphs
"Answer the item from your own competence ..." and "The item offers an
escape answer ..." (and the "Do not force a choice ..." line) WITH:

```text
Answer the item from your own competence with the everyday concepts. You are NOT trying to guess an intended answer; there is no trick, and you must not try to infer what the item's author might have wanted.

How the texts read: the definition texts use a deliberately tiny, plain vocabulary, so the grammar can sound odd -- "a something of kind event" means "an event"; "somethings of kind take happen" means "acts of taking happen". Odd wording is never a trick and never by itself a reason to reject an option or a statement. The letters X and Y stand for the participants named with the word itself (in "break (X breaks Y)", X is the one who breaks, Y is what gets broken). A parenthesis after a word only tells you which sense of the word is meant; ignore unfamiliar technical notation inside it. Square brackets are clarifications; read them as part of the text.

For a multiple-choice item, pick the option that correctly gives the meaning: an option is correct when (a) everything it says fits the word as ordinarily understood, AND (b) as a whole it actually says what the word means -- you could tell this word is being defined and not something else. Read each sentence as saying what is NORMALLY or TYPICALLY the case ("birds fly" is a fair thing to say even though penguins don't); hedges like "at some times", "can", "many", "some" only claim what they say. True extra detail a dictionary might leave out does NOT make an option wrong; anything FALSE of the thing, or fitting some other thing instead, DOES -- as does an option that is only a pile of true facts and never says what the thing is. If more than one option seems right, pick the one that best and most exactly gives the meaning of the asked word itself, not of something closely related. Answer NONE only if no option is genuinely correct, or you cannot decide; NONE is a normal, expected answer.

For a yes/no item, the quoted statement is a FRAGMENT of a longer description; read "this someone", "this something", "it", or a stray quote mark charitably, as a piece of a description of the word's normal situation. Answer yes if the statement says something that belongs to what the word means, or follows from it (typically-true counts as true; hedges claim only what they say). Answer no if it does not fit what the word means: false of it, only rarely or accidentally true of it, or nothing to do with it -- if what the word means neither says nor implies the statement, the answer is no, including statements so generic they say nothing about this word in particular. Answer "cannot say" ONLY if you cannot understand the statement well enough to judge it at all, or you genuinely cannot decide -- never merely because it is oddly worded, partial, or only typically true, and never as a soft no.

Judge each item only against its own word; statements may repeat under different words -- never reuse an earlier answer or look for a pattern.
```

(The "Rules of conduct" block, output contract, and everything else in the
template are unchanged.)

## D. items-judge-1.md — preamble delta (presentation only)

In the third preamble bullet, REPLACE "use it whenever the options do not
fit or you genuinely cannot tell" WITH "use NONE whenever no option is
genuinely correct, and 'cannot say' whenever you genuinely cannot judge a
statement — but never over odd wording or true extra detail alone; the full
standards are in the CSV instructions / PROTOCOL.md §4.7". Item sections
1–360 are byte-unchanged.
