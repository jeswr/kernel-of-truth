#!/usr/bin/env python3
"""tok_glm52.py — kot-f1k-tok/1: the REAL-run tokenizer wrapper (ASM-1971).

Wraps a PINNED HuggingFace-format tokenizer.json (for F1-K: the GLM-5.2
snapshot's tokenizer file, staged with the weights at Modal bring-up) behind
the exact subprocess contract build_carriers.py freezes (module docstring
"TOKENIZER CONTRACT — kot-f1k-tok/1"):

  argv    tok_glm52.py <tokenizer.json>
  env     TOK_SHA256=<64hex>   OPTIONAL but REQUIRED for real runs: sha256
          the tokenizer.json bytes must hash to (fail closed on mismatch —
          the same pin the runner passes to build_carriers as
          --tokenizer-sha/--tokenizer-artifact, re-derived there from the
          artifact bytes; carrier RE-REVIEW item 8).
  stdin   JSONL {"text": <str>}
  stdout  JSONL {"ids": [<int>...], "offsets": [[start, end], ...]}
          Python-str CHARACTER offsets, end-exclusive, one pair per token.
  encode  add_special_tokens=False — no BOS/EOS injection, no normalisation
          beyond what the tokenizer.json itself performs (contract: "no
          BOS-stripping or normalisation beyond the engine's own prefill
          path").

FAIL-CLOSED offset validation (ASM-2490): every offset pair must satisfy
0 <= start <= end <= len(text) as PYTHON-STR indices, and len(offsets) ==
len(ids). HF `tokenizers` reports offsets against the original string; a
byte-indexed or normalizer-shifted tokenizer surfaces here as an
out-of-range/inconsistent pair on multibyte text and ABORTS the whole batch
(a silently wrong offset would gate the wrong tokens and corrupt every
carrier). --selftest exercises exactly that with multibyte fixtures.

BRING-UP CHECK (deferred, $0 here): the wrapper's ids must equal the ids
the engine's own prefill path (colibri tok.h) produces for the same text —
verified on the real snapshot at Modal bring-up, alongside the ASM-1971
weight pin, BEFORE any real dump. This file never fetches anything.

MOCK NOTE: the $0 pipeline keeps using mock_tokenizer.py; this wrapper is
for `construct --mode real` only.
"""
import hashlib
import json
import sys


def fail(msg):
    sys.stderr.write("ERR_F1K_TOK: %s\n" % msg)
    sys.exit(1)


def load_tokenizer(path, pin):
    data = open(path, "rb").read()
    got = hashlib.sha256(data).hexdigest()
    if pin is not None and got != pin.lower():
        fail("tokenizer.json sha256 %s != pinned TOK_SHA256 %s" % (got, pin))
    try:
        from tokenizers import Tokenizer
    except ImportError:
        fail("the 'tokenizers' package is required (pip install tokenizers)")
    return Tokenizer.from_file(path), got


def encode_line(tok, text):
    enc = tok.encode(text, add_special_tokens=False)
    ids, offs = list(enc.ids), [list(p) for p in enc.offsets]
    if len(ids) != len(offs):
        fail("ids/offsets length mismatch (%d != %d)" % (len(ids), len(offs)))
    n = len(text)
    for i, (s, e) in enumerate(offs):
        if not (isinstance(s, int) and isinstance(e, int) and 0 <= s <= e <= n):
            fail("token %d offset [%r,%r) is not a valid Python-str char "
                 "range for text of length %d (byte-indexed or shifted "
                 "offsets? ASM-2490 fails closed)" % (i, s, e, n))
    return ids, offs


def main():
    import os
    args = [a for a in sys.argv[1:] if a != "--selftest"]
    if "--selftest" in sys.argv[1:]:
        return selftest()
    if len(args) != 1:
        fail("usage: tok_glm52.py <tokenizer.json>   (or --selftest)")
    tok, got = load_tokenizer(args[0], os.environ.get("TOK_SHA256"))
    sys.stderr.write("[kot-f1k-tok/1] tokenizer %s sha256=%s%s\n"
                     % (args[0], got,
                        "" if os.environ.get("TOK_SHA256") else
                        " (UNPINNED — real runs must set TOK_SHA256)"))
    out = sys.stdout
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            text = json.loads(raw)["text"]
        except (ValueError, KeyError):
            fail("malformed input line (want JSONL {\"text\": ...})")
        if not isinstance(text, str):
            fail("\"text\" is not a string")
        ids, offs = encode_line(tok, text)
        out.write(json.dumps({"ids": ids, "offsets": offs}) + "\n")
    out.flush()
    return 0


def selftest():
    """$0 contract selftest on a tiny CONSTRUCTED tokenizer (no model, no
    network): multibyte char offsets, JSONL round-trip, the template-spec
    intersection rule, and the sha-pin fail-closed path."""
    import os
    import subprocess
    import tempfile
    fails = []

    def check(cond, msg):
        print("  %s %s" % ("ok:  " if cond else "FAIL:", msg))
        if not cond:
            fails.append(msg)

    from tokenizers import Tokenizer, models, pre_tokenizers
    vocab = {"the": 0, "héllo": 1, "wörld": 2, "café": 3,
             "世界": 4, "says": 5, "[UNK]": 6}
    tok = Tokenizer(models.WordLevel(vocab, unk_token="[UNK]"))
    tok.pre_tokenizer = pre_tokenizers.Whitespace()
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "tiny-tokenizer.json")
        tok.save(path)
        pin = hashlib.sha256(open(path, "rb").read()).hexdigest()

        print("== selftest: kot-f1k-tok/1 contract on a tiny tokenizer ==")
        # multibyte text: char offsets MUST index the Python str, not bytes
        text = "the héllo café 世界 says wörld"
        inp = json.dumps({"text": text}) + "\n" + \
              json.dumps({"text": "héllo héllo"}) + "\n"
        env = dict(os.environ, TOK_SHA256=pin)
        p = subprocess.run([sys.executable, __file__, path],
                           input=inp.encode(), stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, env=env)
        check(p.returncode == 0, "wrapper exits 0 under the correct TOK_SHA256 pin")
        lines = p.stdout.decode().splitlines()
        check(len(lines) == 2, "one JSONL output line per input line, order-preserving")
        r = json.loads(lines[0])
        check(r["ids"] == [0, 1, 3, 4, 5, 2], "token ids as expected")
        spans = [(s, e) for s, e in r["offsets"]]
        check(all(text[s:e] in vocab for s, e in spans),
              "every offset slices the ORIGINAL str to a vocab word "
              "(char offsets, not bytes; multibyte hé/café/世界)")
        check(spans[3] == (15, 17),
              "CJK token 世界 spans chars [15,17) — 2 chars, not 6 bytes")
        # template-spec intersection rule (the SAME rule build_carriers
        # applies): a char span over 'café' gates exactly that token
        cs, ce, slot = 10, 14, 42
        gated = [i for i, (s, e) in enumerate(spans) if s < ce and cs < e]
        check(gated == [2], "char span [10,14) gates exactly the café token "
                            "(intersection rule, slot %d)" % slot)
        # fail-closed: wrong pin
        p2 = subprocess.run([sys.executable, __file__, path],
                            input=inp.encode(), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            env=dict(os.environ, TOK_SHA256="0" * 64))
        check(p2.returncode != 0 and b"ERR_F1K_TOK" in p2.stderr,
              "wrong TOK_SHA256 pin -> fail closed, nonzero exit")
        # fail-closed: malformed input
        p3 = subprocess.run([sys.executable, __file__, path],
                            input=b"not json\n", stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env)
        check(p3.returncode != 0, "malformed input line -> fail closed")

    print()
    if fails:
        print("TOK SELFTEST FAILED (%d)" % len(fails))
        return 1
    print("TOK SELFTEST PASS (MOCK SCOPE ONLY: contract mechanics on a "
          "constructed tokenizer; the REAL GLM-5.2 tokenizer.json is pinned "
          "+ engine-consistency-checked at Modal bring-up, ASM-1971)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
