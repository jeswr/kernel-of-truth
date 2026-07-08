#!/usr/bin/env python3
"""D-EXT source conversion — pinned OpenBookQA parquet -> canonical jsonl.

Pure format conversion, NO selection, NO editing: every row of every split of
the `additional` config of allenai/openbookqa at the pinned HF revision is
emitted as one canonical JSON line (sorted keys, ensure_ascii, '\n'
terminator), in parquet row order. Fails closed if the source bytes do not
match the pinned per-file sha256 (= the HF LFS oids of the pinned revision).

Requires: pyarrow (any recent version; parquet decode of plain columns is
format-stable). Run:  python3 convert-source.py   (from this directory or
anywhere; paths resolve relative to this file).
"""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# allenai/openbookqa, revision 388097ea7776314e93a529163e0fea805b8a6454
# (refs/heads/main, cross-checked against /api/datasets/.../refs 2026-07-08).
# sha256 below = LFS oids reported by the HF tree API at that revision AND
# recomputed locally over the downloaded bytes before first conversion.
PINNED = {
    "source/additional/train-00000-of-00001.parquet":
        "d16d719e87efb86ed0a2ac4c8cdf380f7bfb94b602088393674c0a64ce9ed3d3",
    "source/additional/validation-00000-of-00001.parquet":
        "92e5e68e4da7bec7d130d925385abf377c2d82b89a16de502b4e1b9cf3f50a26",
    "source/additional/test-00000-of-00001.parquet":
        "33b318ea8e2354484868bc601c1b30a58149e9deb93162ff422bb8de980c7105",
}
EXPECTED_ROWS = {"train": 4957, "validation": 500, "test": 500}


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(1)


def main():
    try:
        import pyarrow.parquet as pq
    except ImportError:
        die("DEXT_ERR_DEP", "pyarrow is required (pip install pyarrow)")

    for rel, want in sorted(PINNED.items()):
        path = os.path.join(HERE, rel)
        if not os.path.exists(path):
            die("DEXT_ERR_SOURCE", "missing pinned source file %s" % rel)
        got = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if got != want:
            die("DEXT_ERR_PIN", "%s sha256 %s != pinned %s" % (rel, got, want))

    outdir = os.path.join(HERE, "source-jsonl")
    os.makedirs(outdir, exist_ok=True)
    for split in ("train", "validation", "test"):
        rel = "source/additional/%s-00000-of-00001.parquet" % split
        rows = pq.read_table(os.path.join(HERE, rel)).to_pylist()
        if len(rows) != EXPECTED_ROWS[split]:
            die("DEXT_ERR_SOURCE", "%s: %d rows, expected %d"
                % (split, len(rows), EXPECTED_ROWS[split]))
        out = os.path.join(outdir, "%s.jsonl" % split)
        with open(out, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, sort_keys=True) + "\n")
        print("wrote %s (%d rows)" % (os.path.relpath(out, HERE), len(rows)))


if __name__ == "__main__":
    main()
