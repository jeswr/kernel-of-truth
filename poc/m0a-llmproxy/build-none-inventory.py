#!/usr/bin/env python3
"""build-none-inventory — the pinned none-stratum sense inventory for
m0a-llmproxy (registry/experiments/m0a-llmproxy.json; design note
poc/m0a-llmproxy/design.md S2).

WHAT THIS BUILDS. none-inventory.txt: the full pinned surface inventory —
54 concept lemmas (alphabetical by slug; lemma = slug with '-' rendered as a
space; one-line sense = the record gloss verbatim) followed by the 65 prime
exponent entries (chart order; surfaces from the pinned exponent lists; one-
line sense from prime-glosses.json) — numbered 1..119. The rendered block is
BYTE-IDENTICAL across all 50 none-stratum items ({{INVENTORY}} in
prompt-template-none.txt); the item's answer space is the entry number or
'none' (output-schema-none.json). Blind by construction: entries carry
surfaces + sense lines only — no ids of any kind [STIPULATED: ASM-0640,
ASM-0541].

DETERMINISM. Single-draw build from pinned inputs, committed and sha-pinned
in the invocation spec before freeze. Fail-closed: refuses to run if the
kernel-v0 corpus digest or the prime-glosses file drifts from the pins below
(ERR_M0AP_REFPIN). A forbidden-string sweep (kernel / nsm / urn: / mapper,
case-insensitive) over the emitted bytes fails the build (ERR_M0AP_BLIND).
"""
import hashlib
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "registry"))
import kot_common as kc  # noqa: E402  (corpus_hash — kot-corpus-hash/1 reference impl)

# the record's pinned kernel-v0 digest (registry/experiments/m0a-llmproxy.json)
KERNELV0_PIN = "8209cadabcfc2eaa11631c5c1100c04a48f33673516780b1f36cbf957217c809"
# staged alongside this builder; sha re-verified so the inventory can only be
# rebuilt from the exact authored gloss bytes
PRIME_GLOSSES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "prime-glosses.json")
# the authored gloss bytes this inventory derives from (staged 2026-07-10)
PRIME_GLOSSES_PIN = "fdb004ccb495fd913c89bfe7262d3389d0d86276ff52f6657509735540cb2013"
CONCEPT_DIR = os.path.join(REPO, "data", "kernel-v0", "concepts")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "none-inventory.txt")
FORBIDDEN = re.compile(r"kernel|nsm|urn:|mapper", re.IGNORECASE)


def main():
    got = kc.corpus_hash(REPO, "kernel-v0")
    if got != KERNELV0_PIN:
        print("ERR_M0AP_REFPIN: kernel-v0 digest %s != pinned %s"
              % (got, KERNELV0_PIN), file=sys.stderr)
        sys.exit(1)
    with open(PRIME_GLOSSES, "rb") as f:
        praw = f.read()
    prime_sha = hashlib.sha256(praw).hexdigest()
    if prime_sha != PRIME_GLOSSES_PIN:
        print("ERR_M0AP_REFPIN: prime-glosses.json sha %s != pinned %s"
              % (prime_sha, PRIME_GLOSSES_PIN), file=sys.stderr)
        sys.exit(1)
    primes = json.loads(praw.decode("utf-8"))["glosses"]
    if len(primes) != 65:
        print("ERR_M0AP_SOURCE: expected 65 prime glosses, got %d"
              % len(primes), file=sys.stderr)
        sys.exit(1)

    slugs = sorted(fn[:-5] for fn in os.listdir(CONCEPT_DIR)
                   if fn.endswith(".json"))
    if len(slugs) != 54:
        print("ERR_M0AP_SOURCE: expected 54 concept records, got %d"
              % len(slugs), file=sys.stderr)
        sys.exit(1)

    lines = []
    n = 0
    for slug in slugs:                       # entries 1..54: concept lemmas
        with open(os.path.join(CONCEPT_DIR, slug + ".json"), "r",
                  encoding="utf-8") as f:
            gloss = json.load(f)["gloss"]
        n += 1
        lines.append("%d. %s -- %s" % (n, slug.replace("-", " "), gloss))
    for p in primes:                         # entries 55..119: prime exponents
        n += 1
        lines.append("%d. %s -- %s" % (n, " / ".join(p["exponents"]),
                                       p["gloss"]))
    body = "\n".join(lines) + "\n"
    if FORBIDDEN.search(body):
        print("ERR_M0AP_BLIND: forbidden string in inventory bytes",
              file=sys.stderr)
        sys.exit(1)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(body)
    with open(OUT, "rb") as f:
        print("%s  %s" % (hashlib.sha256(f.read()).hexdigest(),
                          os.path.relpath(OUT, REPO)))
    print("prime-glosses.json sha256 %s" % prime_sha)
    print("built %d inventory entries (54 concept + 65 prime)" % n)


if __name__ == "__main__":
    main()
