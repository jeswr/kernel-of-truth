#!/usr/bin/env python3
"""Build the BLIND naturalness-gate prompts for the re-authoring sample.

Two prompts, byte-identical except for the definition texts:
  prompt.old12.txt  - the 12 concepts' CURRENT plain-authored definitions
                      (the paired control at matched set size)
  prompt.new12.txt  - the 12 RE-AUTHORED definitions

Rubric and blinding follow poc/knull/gpt56-plaindict-review/build_prompt.py
verbatim (headwords withheld; definition texts only; no project / NSM /
experiment context; the reviewer never learns which set is which or that a
second set exists). Definition order within each prompt is the deterministic
ascending-label order of the sample file, identical across the two prompts so
the only differing bytes are the definition texts themselves.
"""
import json
import os
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
KNULL = os.path.dirname(HERE)

sample = json.load(open(os.path.join(HERE, "plain-reauthored-sample.json")))
old = json.load(open(os.path.join(KNULL, "inputs", "plain-authored.json")))["definitions"]

labels = sorted(sample["definitions"])
sets = {
    "old12": [old[l] for l in labels],
    "new12": [sample["definitions"][l] for l in labels],
}

header = textwrap.dedent("""\
Below are 12 dictionary-style definitions of common English words. The headword
being defined has been removed from each entry, so you see only the definition
text. Read them as a lexicographer would and assess how natural they are as
human-authored dictionary entries -- the kind you would find in a general
dictionary such as Merriam-Webster, the Oxford Dictionary of English, or Collins.

Please answer, concretely and with quoted evidence:

(a) OVERALL NATURALNESS. On a 1-10 scale (10 = indistinguishable from a
    professionally edited general dictionary; 1 = obviously artificial), how
    natural do these read as human-authored dictionary entries? Give one number
    and justify it.

(b) STRUCTURAL TELLS. Is there a mechanical, formulaic, or repetitive SENTENCE-
    STRUCTURE pattern running through them -- something that would tell you the
    entries follow a rigid template or were machine-generated, rather than the
    varied prose an editorial team produces? Name the specific structural
    patterns you notice (clause shape, punctuation rhythm, opening constructions,
    the way second and third clauses are appended, recurring phrase frames, etc.)
    and QUOTE concrete examples from the entries for each pattern you name.

(c) WORST AND BEST. Which specific entries read as the LEAST natural / most
    templated, and which read as the MOST natural? Quote them and say why.

(d) DISCRIMINABILITY. Could a fluent English reader reliably distinguish this set
    from a real published dictionary on the basis of sentence STRUCTURE alone
    (setting aside the actual definitional content / word choice)? Roughly what
    accuracy would you expect such a reader to achieve, and on what structural
    cue would they most rely?

Be candid and specific; do not soften the assessment. Quote liberally.

--- THE DEFINITIONS ---
""")

for name, texts in sets.items():
    lines = [header]
    for i, t in enumerate(texts, 1):
        lines.append("%d. %s" % (i, t))
    out = os.path.join(HERE, "prompt.%s.txt" % name)
    body = "\n".join(lines) + "\n"
    open(out, "w").write(body)
    print("wrote %s: %d definitions, %d chars" % (out, len(texts), len(body)))
