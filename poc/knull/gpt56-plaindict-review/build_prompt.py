#!/usr/bin/env python3
"""Build the BLIND naturalness-review prompt for the plain-dictionary store.

Feeds definition TEXTS ONLY (headwords withheld, matching the blind style
spot-check design) so the reviewer judges sentence-structure naturalness on the
prose alone. No project/NSM/experiment context is included -- the reviewer must
stay blind. Output: prompt.txt in this directory.
"""
import json, os, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

defs = json.load(open(os.path.join(ROOT, "poc/knull/inputs/plain-authored.json")))["definitions"]
# preserve file order; use VALUES ONLY (no headwords, no keys)
texts = list(defs.values())
N = len(texts)

header = textwrap.dedent(f"""\
Below are {N} dictionary-style definitions of common English words. The headword
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

lines = [header]
for i, t in enumerate(texts, 1):
    lines.append(f"{i}. {t}")

prompt = "\n".join(lines) + "\n"
out = os.path.join(HERE, "prompt.txt")
open(out, "w").write(prompt)
print(f"wrote {out}: {N} definitions, {len(prompt)} chars")
