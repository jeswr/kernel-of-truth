#!/usr/bin/env python3
"""f1_analysis — pinned analysis for F1 (KOTK byte accounting; HE5 byte-premise precursor).

    python3 tools/experiments/f1_analysis.py [--root <repo>] [--zstd-level 19]

RAW OUTPUT ONLY (P2 §2.4): this script computes byte counts and their plain
ratio; it renders NO verdict, applies NO threshold, and knows nothing about
the >=2x kill line (that lives verbatim in the frozen F1 registry record and
is applied by verdict-gen over the frozen verdict_rules).

What it measures, on the committed lexical-wn31 corpus (P1 §HE5 / F1 in
docs/design-efficiency-track.md §4; measured priors 2.90 B/rec KOTK/2 vs
9.58 B/rec zstd identity-JCS; glosses-only text was the still-to-be-measured
baseline — this script measures it):

  kernel_bytes_per_concept      bytes of the KOTK/2 entropy-columnar pack
                                (tools/pack/proto-kotk2-entropy.mjs — the
                                winning codec of
                                docs/design-compact-kernel-serialization-v2.md;
                                the packer self-verifies: encode -> decode ->
                                re-mint ALL 117,791 URNs, exit 1 on mismatch)
                                divided by n_records.
  gloss_zstd_bytes_per_concept  bytes of the zstd-compressed glosses-only text
                                store (one gloss per line, UTF-8 — the
                                RAG-over-text store as actually served)
                                divided by n_records.
  ratio                         gloss_zstd_bytes_per_concept /
                                kernel_bytes_per_concept (>1 means the kernel
                                store is smaller).
  n_records                     synset records in the corpus.

Determinism/pinning notes: zstd level is a parameter (default 19, matching the
KOTK/2 decision record) run single-threaded; the packer is the committed file
whose sha256 the F1 registry record pins alongside this script. Heavy work is
`nice -n 10` (box constraints).

Analysis-script contract (P2 §3.1 step 5): eligible run records arrive as
JSONL on stdin and are read (never a hang: verdict-gen always pipes) but this
R0 instrument recomputes from the committed corpus — the run records' role for
F1 is provenance, not input data. Stdout is one JSON object.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

WN31_FILES = ("synsets-noun.jsonl", "synsets-verb.jsonl", "synsets-adj.jsonl", "synsets-adv.jsonl")


def fail(code, msg):
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="F1 raw byte accounting (no verdict).")
    ap.add_argument("--root", default=None)
    ap.add_argument("--zstd-level", type=int, default=19)
    args = ap.parse_args()
    root = args.root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Drain stdin if piped (verdict-gen supplies eligible records; see docstring).
    if not sys.stdin.isatty():
        try:
            sys.stdin.read()
        except Exception:
            pass

    corpus_dir = os.path.join(root, "data", "lexical-wn31")
    glosses = []
    n_missing_gloss = 0
    for name in WN31_FILES:
        path = os.path.join(corpus_dir, name)
        if not os.path.isfile(path):
            fail("ERR_F1_CORPUS", "missing corpus file %s" % path)
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                gloss = rec.get("annotations", {}).get("gloss")
                if gloss is None:
                    n_missing_gloss += 1
                    gloss = ""
                glosses.append(gloss)
    n_records = len(glosses)
    if n_records == 0:
        fail("ERR_F1_CORPUS", "no records found under %s" % corpus_dir)

    with tempfile.TemporaryDirectory(prefix="f1-") as tmp:
        # Baseline: the glosses-only text store, zstd-compressed (as served).
        gloss_txt = os.path.join(tmp, "glosses.txt")
        with open(gloss_txt, "w", encoding="utf-8") as f:
            f.write("\n".join(glosses) + "\n")
        gloss_raw_bytes = os.path.getsize(gloss_txt)
        gloss_zst = gloss_txt + ".zst"
        p = subprocess.run(
            ["nice", "-n", "10", "zstd", "-%d" % args.zstd_level, "-T1", "-q", "-f", "-o", gloss_zst, gloss_txt],
            capture_output=True,
        )
        if p.returncode != 0:
            fail("ERR_F1_ZSTD", p.stderr.decode("utf-8", "replace"))
        gloss_zstd_bytes = os.path.getsize(gloss_zst)

        # Kernel store: KOTK/2 entropy-columnar pack, self-verifying (exit 1 on
        # any URN re-mint mismatch — losslessness is asserted by the codec).
        pack_out = os.path.join(tmp, "wn31.kotk2")
        packer = os.path.join(root, "tools", "pack", "proto-kotk2-entropy.mjs")
        p = subprocess.run(
            ["nice", "-n", "10", "node", packer, "--out", pack_out],
            capture_output=True, cwd=root,
        )
        if p.returncode != 0:
            fail("ERR_F1_PACK", "packer failed (roundtrip/self-verify): %s"
                 % p.stderr.decode("utf-8", "replace")[-2000:] or p.stdout.decode("utf-8", "replace")[-2000:])
        stdout = p.stdout.decode("utf-8", "replace")
        if "hash verify: ok" not in stdout or " bad 0 " not in stdout:
            fail("ERR_F1_PACK", "packer did not report a clean URN re-mint: %s" % stdout[-500:])
        kernel_pack_bytes = os.path.getsize(pack_out)

    out = {
        "corpus": "lexical-wn31",
        "n_records": n_records,
        "n_missing_gloss": n_missing_gloss,
        "kernel_pack_bytes": kernel_pack_bytes,
        "kernel_bytes_per_concept": round(kernel_pack_bytes / n_records, 4),
        "gloss_text_bytes": gloss_raw_bytes,
        "gloss_zstd_bytes": gloss_zstd_bytes,
        "gloss_zstd_bytes_per_concept": round(gloss_zstd_bytes / n_records, 4),
        "ratio": round(gloss_zstd_bytes / kernel_pack_bytes, 4),
        "zstd_level": args.zstd_level,
    }
    print(json.dumps(out, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
