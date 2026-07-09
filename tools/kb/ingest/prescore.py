"""Mechanical keyword prescore (kb/triage-rubric.md §3). Heuristic ordering
signal ONLY — decides nothing, never citable, replaced by Haiku triage_score
next phase. Term lists are parsed from the rubric file itself so the rubric
stays the single source of truth (its sha256 is pinned in kb/manifest.json)."""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import kb_common as K  # noqa: E402

RUBRIC_PATH = os.path.join(K.KB_DIR, "triage-rubric.md")

_LIST_RE = re.compile(
    r"^\-\s+\*\*(?P<name>[a-z-]+) terms \(weight (?P<w>[−-]?\d+)\):\*\*\s*(?P<terms>.*)$"
)


def load_terms():
    """-> [(term, weight), ...] parsed from the rubric's §3 bullet lists."""
    with open(RUBRIC_PATH, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")
    out = []
    current_weight = None
    buf = []

    def flush():
        nonlocal buf, current_weight
        if current_weight is not None and buf:
            blob = " ".join(buf)
            for term in blob.split(","):
                term = term.strip().strip(".").lower()
                if term:
                    out.append((term, current_weight))
        buf = []

    for line in lines:
        m = _LIST_RE.match(line)
        if m:
            flush()
            current_weight = int(m.group("w").replace("−", "-"))
            buf = [m.group("terms")]
        elif current_weight is not None and line.startswith("  ") and line.strip():
            buf.append(line.strip())
        elif current_weight is not None and not line.strip():
            continue
        else:
            flush()
            current_weight = None
    flush()
    return out


def prescore(title, abstract, terms=None):
    """-> (score>=0, matched-term list)."""
    terms = terms if terms is not None else load_terms()
    hay = ((title or "") + " " + (abstract or "")).lower()
    score = 0
    matched = []
    for term, w in terms:
        if term in hay:
            score += w
            matched.append(term)
    return max(score, 0), matched
