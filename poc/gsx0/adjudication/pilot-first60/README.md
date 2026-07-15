# gsx0 STAGE-0 pilot — blind human adjudication (judge-1)

**~15–20 minutes. 60 short items. Your answers are the sole "gold" for a $1–2 go/no-go test.**

Download **`gsx0-pilot-adjudication.xlsx`** (below), fill the yellow **YOUR ANSWER** column on the
*Adjudication* tab, and send it back. `preview.csv` renders the same 60 items as a table here in the
browser if you just want to look first. (Prefer Google Sheets? Upload the `.xlsx` to Drive — it converts
automatically, dropdowns and all.)

## Who should do this — please read

judge-1 **must be kernel-naive**: someone who has **never read any of this project's concept definitions**
(the kernel-v0 / molecules-v0 records). Your answers are compared against the system's own definitions, so
if you have seen them, the comparison is no longer independent — please hand this to someone who hasn't.
Use only ordinary, everyday understanding of the words. **Do not look anything up.**

## What you're doing

Two kinds of item:

- **CLAIM** — *"According to the definition of X, is `<statement>` true of X?"* → answer **yes / no / cannot-say**.
- **CHOICE** — a definition (or a word) plus four options A–D → pick the best option, or **NONE-or-cannot-say**.

Judge every item **on its own**. The same sentence can appear under different words — never reuse an earlier
answer.

## How to decide (the standard this is scored against)

- **Fit + identification (choices).** An option is right only if (a) *everything* it says fits the word as
  ordinarily understood — read each clause as a typical case, honouring hedges like "can" / "often" / "some" —
  **and** (b) as a whole it says what the word *means* (picks out this concept, not a near one). Extra *true*
  facts beyond the core are fine (surplus truth ≠ error). Any clause that is *false* of the word disqualifies.
  A pile of true facts that never says what the thing *is* → not correct.
- **Best fit before NONE.** If two options pass, pick the one that most specifically gives the meaning of the
  *asked* word. Choose NONE-or-cannot-say only if none pass or you genuinely can't decide.
- **Word-match** (given a definition, pick the word) is the same test in reverse. A parenthetical like
  `find (X finds Y)` only tells you which *sense* is meant — ignore unfamiliar notation inside it; it is never
  itself a reason to answer NONE.
- **Claims** at the generic standard. **yes** = holds in the normal case (exceptions don't make it false), or
  its own hedge holds. **no** = misdescribes the word, *or* has nothing to do with what the word means
  (including statements so generic they say nothing in particular). **cannot-say** = *only* genuine inability
  to understand/decide — never a soft "no", never just because the wording is odd or only sometimes true.
- **Read charitably.** Claims are fragments of a longer description — unresolved "this someone / it / these
  parts", stray quote marks, and "[bracketed]" notes are pieces of a description of the word's normal
  scenario. The deliberately plain wording ("a something of kind event" = "an event") is never itself a reason
  to say NONE / no / cannot-say. Letters X/Y name the participants in the word's own title
  (`break (X breaks Y)`: X breaks, Y gets broken).

## What happens next

Your 60 labels are the human "gold". A blind LLM judge (different vendor, sees only the item text) and a
tie-breaker are run in parallel; where they and you disagree, the item is marked *unresolved*. Then a $1–2
GPU pilot decides whether a larger experiment is even worth running. Nothing is published from this.

*Items are shown in a fixed shuffled order (seed `dadjt/1|judge-1|20260710`); please don't reorder, add, or
delete rows.*
