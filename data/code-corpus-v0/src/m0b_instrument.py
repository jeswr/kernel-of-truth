#!/usr/bin/env python3
"""m0b_instrument — deterministic kernel-vocabulary coverage census (M0b).

    python3 tools/experiments/m0b_instrument.py [--root <repo>]

RAW OUTPUT ONLY (P2 §2.4): emits token-mass counts and their plain fraction;
renders NO verdict and knows nothing about the NICHE-SCOPE X=0.20 line (that
lives verbatim in the frozen m0b registry record and is applied by verdict-gen
over the frozen verdict_rules).

WHAT IT MEASURES (correction c-m0b-1, 2026-07-08, pre-sign-off): the fraction
of the pre-declared target-task content-word token mass (the committed
TinyStories-validation table, data/task-family-tinystories/m0b-vocab.json;
provenance in that directory's README) covered by the kernel vocabulary at
three rungs — ON-BOX, NO ANNOTATORS, a full census (no sampling, so no
sampling test; P1 common rules: count-based criteria carry no test):

  rung "kernel-v0"     a top-500 lemma is covered iff its committed
                       `kernelHits` list is non-empty (mapper-lexicon surface
                       hits against data/kernel-v0, baked into the table at
                       generation time; data/kernel-v0 is corpus-pinned so any
                       kernel drift invalidates the table's pin).
  rung "molecules-v0"  kernel-v0 coverage OR lemma appears in `corpusLemmas`
                       of any data/molecules-v0/molecules/*.json record.
  rung "wn31-aligned"  molecules-v0 coverage OR lemma equals a single-word
                       lowercase lemma of any data/lexical-wn31 synset. This
                       rung is the "AxiomsOnly-reachable" band
                       (design-bulk-kernel.md) — reported descriptively, never
                       quoted as explicated coverage.

Denominator = the FULL content-word mass (1,709,765 tokens); the non-top-500
tail (19.65% of content mass) counts as UNCOVERED at every rung — the
conservative direction. This membership census is a crude LOWER BOUND of the
original judgment-based "plausible profile-1 explication" estimate (which
needed annotators and is retained as exploratory context in
mapper/m0/results/); coverage here means "surface form reachable in the kernel
vocabulary today", stated as exactly that.

Deterministic: pure counting over committed files; no RNG, no network, no
model. Output metric keys are EXACTLY the frozen analysis contract's input
keys (analysis/m0b.py).
"""

import argparse
import glob
import json
import os
import sys

RUNGS = ("kernel-v0", "molecules-v0", "wn31-aligned")
PRIMARY_RUNG = "molecules-v0"
WN31_FILES = ("synsets-noun.jsonl", "synsets-verb.jsonl", "synsets-adj.jsonl", "synsets-adv.jsonl")


def fail(code, msg):
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="M0b raw coverage census (no verdict).")
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    root = args.root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    table_path = os.path.join(root, "data", "task-family-tinystories", "m0b-vocab.json")
    if not os.path.isfile(table_path):
        fail("ERR_M0B_CORPUS", "missing pinned target-task table %s" % table_path)
    with open(table_path, "r", encoding="utf-8") as f:
        table = json.load(f)
    rows = table["rows"]
    content_mass = int(table["contentMass"])
    if content_mass <= 0 or not rows:
        fail("ERR_M0B_CORPUS", "pinned table is empty")

    # molecules-v0 vocabulary: corpusLemmas of every committed molecule record.
    molecule_lemmas = set()
    mol_glob = os.path.join(root, "data", "molecules-v0", "molecules", "*.json")
    mol_files = sorted(glob.glob(mol_glob))
    if not mol_files:
        fail("ERR_M0B_CORPUS", "no molecule records under data/molecules-v0/molecules/")
    for path in mol_files:
        with open(path, "r", encoding="utf-8") as f:
            rec = json.load(f)
        for lemma in rec.get("corpusLemmas") or []:
            molecule_lemmas.add(lemma.strip().lower())

    # wn31 vocabulary: single-word lowercase synset lemmas (multi-word lemmas
    # cannot match single-token corpus lemmas and are excluded by definition).
    wn31_lemmas = set()
    for name in WN31_FILES:
        path = os.path.join(root, "data", "lexical-wn31", name)
        if not os.path.isfile(path):
            fail("ERR_M0B_CORPUS", "missing corpus file %s" % path)
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                for lemma in rec.get("annotations", {}).get("lemmas") or []:
                    lemma = lemma.strip().lower()
                    if lemma and "_" not in lemma and " " not in lemma:
                        wn31_lemmas.add(lemma)

    covered = {r: 0 for r in RUNGS}
    top500_mass = 0
    n_covered_lemmas = {r: 0 for r in RUNGS}
    for row in rows:
        lemma = row["lemma"].strip().lower()
        count = int(row["count"])
        top500_mass += count
        in_kernel = bool(row.get("kernelHits"))
        in_mol = in_kernel or lemma in molecule_lemmas
        in_wn = in_mol or lemma in wn31_lemmas
        for rung, hit in (("kernel-v0", in_kernel), ("molecules-v0", in_mol), ("wn31-aligned", in_wn)):
            if hit:
                covered[rung] += count
                n_covered_lemmas[rung] += 1

    metrics = {
        "coverage_rung": PRIMARY_RUNG,
        "n_covered": covered[PRIMARY_RUNG],
        "n_tokens_total": content_mass,
        "rungs": [
            {"coverage_rung": r, "n_covered": covered[r], "n_tokens_total": content_mass}
            for r in RUNGS
        ],
        "coverage": {
            "fraction": round(covered[PRIMARY_RUNG] / content_mass, 6),
            "rung": PRIMARY_RUNG,
        },
        "top500_mass": top500_mass,
        "n_top_lemmas": len(rows),
        "n_covered_lemmas_by_rung": {r: n_covered_lemmas[r] for r in RUNGS},
        "vocab_sizes": {"molecules-v0-lemmas": len(molecule_lemmas),
                        "wn31-single-word-lemmas": len(wn31_lemmas)},
    }
    print(json.dumps(metrics, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
