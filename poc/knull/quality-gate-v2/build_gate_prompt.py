#!/usr/bin/env python3
"""knull-v2 — build the BLIND full-store quality-gate prompt (all 108).

Instrument: the maintainer-RATIFIED ASM-0703 two-part rule, operationalized
as a blind lexicographer's review of the 108 re-authored plain definitions
(poc/knull/inputs-v2/plain-authored.json):

  part 1  DEFECT AUDIT — the maintainer's verbatim standard as four named
          defect classes (register/word-choice faults; vague anaphoric
          renaming; staged observers; non-definitional material). PASS
          requires ZERO findings in these classes from BOTH judge families.
  part 2  OVERALL NATURALNESS floor — the baseline rubric's 1-10 scale
          (anchors byte-carried from poc/knull/gpt56-plaindict-review /
          reauthor-sample prompts). PASS requires >= 5/10 from BOTH judges.
          Matched set size: the OLD 108-entry store measured 3/10 on this
          scale (gpt56-plaindict-review/review.raw.md).

Blindness (ASM-0701 mechanics, unchanged): headwords withheld, definition
texts only, deterministic ascending-label order, no project / NSM /
experiment context, the judge is never told a comparison set or a gate
exists. Judges: GPT-5.6 (codex-cli 0.144.1 exec, effort high — the baseline
instrument) + Claude Haiku 4.5 (headless claude -p per
poc/truthstyle-2x2/judges-invocation.md section 4.3 + 4.3.1).
"""
import json
import os
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
KNULL = os.path.dirname(HERE)

store = json.load(open(os.path.join(KNULL, "inputs-v2", "plain-authored.json"),
                       encoding="utf-8"))
labels = sorted(store["definitions"])

header = textwrap.dedent("""\
Below are 108 dictionary-style definitions of common English words. The
headword being defined has been removed from each entry, so you see only the
definition text. Review them as a senior lexicographer would when copy-editing
entries submitted for a general dictionary such as Merriam-Webster, the Oxford
Dictionary of English, or Collins.

Please answer in two parts, concretely and with quoted evidence.

PART 1 — DEFECT AUDIT. Work through the entries and report EVERY instance of
the following faults. For each instance, give the entry number and quote the
offending words. Judge each category strictly on its own terms; do not report
mere stylistic preferences where the wording used is itself correct and proper.

  (1) REGISTER OR WORD-CHOICE FAULTS: a word or phrase that is misused,
      unidiomatic, or improper in its place — a wrong collocation, a
      malapropism, a strained or affected substitute for the plain correct
      term, or diction out of keeping with an edited dictionary entry.
  (2) VAGUE ANAPHORIC RENAMING: the thing being defined re-referred to by an
      unnaturally vague placeholder noun phrase such as 'the item', 'the
      object', or 'the creature' where natural prose would use a pronoun or
      a precise term.
  (3) STAGED OBSERVERS: a clause that invents a generic onlooker to assert
      that something can be perceived or how people react to it (of the kind
      'anyone who looks in the right direction sees it', 'onlookers can tell
      that...').
  (4) NON-DEFINITIONAL MATERIAL: a clause that does not serve to state what
      the word means — narrated consequences or benefits of the thing,
      symptoms, practical or moral advice, emotional commentary, or a
      decorative literary flourish appended after the meaning is given.

If a category has no instances, write exactly: none found.

PART 2 — OVERALL NATURALNESS. On a 1-10 scale (10 = indistinguishable from a
professionally edited general dictionary; 1 = obviously artificial), how
natural do these read as human-authored dictionary entries? Give one number
and justify it, quoting the entries you weigh most heavily, and naming the
least and most natural entries.

Be candid and specific; do not soften the assessment. Quote liberally.

--- THE DEFINITIONS ---
""")

lines = [header]
for i, lab in enumerate(labels, 1):
    lines.append("%d. %s" % (i, store["definitions"][lab]))
out = os.path.join(HERE, "prompt.new108.txt")
body = "\n".join(lines) + "\n"
open(out, "w").write(body)
print("wrote %s: %d definitions, %d chars" % (out, len(labels), len(body)))

# order map (labels withheld from the judge; kept here for unblinding)
omap = os.path.join(HERE, "prompt.new108.order.json")
json.dump({str(i): lab for i, lab in enumerate(labels, 1)},
          open(omap, "w"), indent=1, sort_keys=True)
print("order map -> %s" % omap)
