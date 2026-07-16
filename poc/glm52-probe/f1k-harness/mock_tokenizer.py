#!/usr/bin/env python3
"""mock_tokenizer.py — deterministic STUB of the kot-f1k-tok/1 tokenizer
contract (see build_carriers.py). MOCK ONLY: the real contract is the
pinned GLM-5.2 tokenizer wrapped at bring-up (ASM-1971; template-spec.json
tokenizer_derivation_rule).

stdin JSONL {"text": str} -> stdout JSONL {"ids": [int],
"offsets": [[start, end], ...]} (Python-str char offsets, end-exclusive).

Mock rule: maximal runs of \\w or single non-space punctuation chars are
tokens; id = 10 + (sha256(piece) mod 49990) — deterministic, vocabulary-
stable, offset-faithful.
"""
import hashlib
import json
import re
import sys

TOK_RE = re.compile(r"\w+|[^\w\s]")


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        text = json.loads(line)["text"]
        ids, offs = [], []
        for m in TOK_RE.finditer(text):
            piece = m.group(0)
            ids.append(10 + int.from_bytes(
                hashlib.sha256(piece.encode()).digest()[:4], "big") % 49990)
            offs.append([m.start(), m.end()])
        sys.stdout.write(json.dumps({"ids": ids, "offsets": offs}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
