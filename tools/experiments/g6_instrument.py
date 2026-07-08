#!/usr/bin/env python3
"""g6_instrument — deterministic AND-under-operator demand count (HS6 / NF5).

    python3 tools/experiments/g6_instrument.py [--root <repo>]

RAW OUTPUT ONLY (P2 §2.4): emits counts; renders NO verdict and knows nothing
about the pre-registered 20% bound (frozen in the g6 registry record, applied
by verdict-gen).

AXIOM UNIVERSE (correction c-g6-1, 2026-07-08, pre-sign-off — the G4 authored
axiom set does not exist yet; when it does, HS6 re-runs over it as a successor
experiment id per the P1 §4b regression provision):

  lexical-wn31   every entry of every record's `axioms` array — 269,960 typed
                 binary edges. Single-atom form BY CONSTRUCTION (one relation,
                 one target): such an axiom cannot need AND-under-operator.
                 Counted, and stated as zero-demand-by-construction.
  molecules-v0   `axioms` arrays (currently 0 entries — counted, reported).
  kernel-v0      contributes NO axiom sidecars yet (its `references` are
                 explication cross-links, not axioms) — reported as 0.
  onto-sumo      every axiom whose top-level operator is NOT in the pinned
                 metadata stoplist below. This is the only committed corpus
                 with operator-rich logical structure, i.e. the demand sample.

CLASSIFIER (pinned approximation; each rule cites
docs/design-dl-from-nsm-and-lean-reconstruction.md §2.1–§2.2 — the wall is
"operators take one clause"): an axiom NEEDS AND-under-operator iff its
canonical KIF parse contains
  R1  an `or` node whose parent is not `not`         (disjunction demands a
      clause-group; `not (or ...)` distributes to conjunction and is exempt)
  R2  an `and` node whose parent is `not`            (negated conjunction —
      not curryable; root-level implication-antecedent `and` IS curryable and
      never triggers)
Of the needing axioms, SIDECAR-EXPRESSIBLE (kot-axiom/1's closed inventory,
docs/design-constraint-layer.md §3.3 — no boolean combinators, no oneOf) iff
every trigger is an R2 whose `(not (and ...))` children are all plain atoms:
that shape and only that shape maps to the sidecar's `disjointWith`.

Deterministic: pure parsing/counting over committed files; no RNG, no model.
Output metric keys are EXACTLY the frozen analysis contract's input keys
(analysis/g6.py) plus reporting breakdowns.
"""

import argparse
import glob
import json
import os
import sys

# SUMO axiom rows whose top-level operator is documentation/rendering
# bookkeeping, not an axiom demanding grammar (pinned stoplist).
METADATA_OPS = frozenset({
    "documentation", "termFormat", "format", "names", "conventionalShortName",
    "abbreviation", "externalImage", "comment", "synonymousExternalConcept",
})

WN31_FILES = ("synsets-noun.jsonl", "synsets-verb.jsonl", "synsets-adj.jsonl", "synsets-adv.jsonl")


def fail(code, msg):
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def parse_kif(text):
    """Minimal KIF s-expression reader: lists, atoms, double-quoted strings."""
    tokens = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
        elif c in "()":
            tokens.append(c)
            i += 1
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            tokens.append(text[i:j + 1])
            i = j + 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in "()":
                j += 1
            tokens.append(text[i:j])
            i = j
    pos = [0]

    def read():
        if pos[0] >= len(tokens):
            raise ValueError("unexpected end of KIF")
        t = tokens[pos[0]]
        pos[0] += 1
        if t == "(":
            out = []
            while pos[0] < len(tokens) and tokens[pos[0]] != ")":
                out.append(read())
            if pos[0] >= len(tokens):
                raise ValueError("unbalanced KIF")
            pos[0] += 1  # consume ')'
            return out
        if t == ")":
            raise ValueError("unbalanced KIF")
        return t

    expr = read()
    if pos[0] != len(tokens):
        raise ValueError("trailing tokens")
    return expr


def is_atom(node):
    """A plain predicate application: a list whose members are all tokens."""
    return isinstance(node, list) and node and all(not isinstance(x, list) for x in node)


def classify(tree):
    """Return (needs_and_under_operator, sidecar_expressible)."""
    triggers = []  # ("R1"|"R2-disjointness"|"R2-general")

    def walk(node, parent_op):
        if not isinstance(node, list) or not node:
            return
        op = node[0] if isinstance(node[0], str) else None
        if op == "or" and parent_op != "not":
            triggers.append("R1")
        if op == "and" and parent_op == "not":
            if all(is_atom(c) for c in node[1:]):
                triggers.append("R2-disjointness")
            else:
                triggers.append("R2-general")
        for child in node[1:]:
            walk(child, op)

    walk(tree, None)
    needs = bool(triggers)
    sidecar = needs and all(t == "R2-disjointness" for t in triggers)
    return needs, sidecar


def main():
    ap = argparse.ArgumentParser(description="G6 raw AND-under-operator counts (no verdict).")
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    root = args.root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    by_source = {}

    # lexical-wn31: typed binary edges — zero-demand by construction.
    n = 0
    for name in WN31_FILES:
        path = os.path.join(root, "data", "lexical-wn31", name)
        if not os.path.isfile(path):
            fail("ERR_G6_CORPUS", "missing corpus file %s" % path)
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    n += len(json.loads(line).get("axioms") or [])
    by_source["lexical-wn31"] = {"n_axioms": n, "n_need": 0, "n_need_sidecar": 0,
                                 "note": "single-atom typed edges; zero-demand by construction"}

    # molecules-v0 axiom sidecars (currently empty — counted, reported).
    n = 0
    for path in sorted(glob.glob(os.path.join(root, "data", "molecules-v0", "molecules", "*.json"))):
        with open(path, "r", encoding="utf-8") as f:
            n += len(json.load(f).get("axioms") or [])
    by_source["molecules-v0"] = {"n_axioms": n, "n_need": 0, "n_need_sidecar": 0,
                                 "note": "axiom sidecars only; explication references excluded"}
    by_source["kernel-v0"] = {"n_axioms": 0, "n_need": 0, "n_need_sidecar": 0,
                              "note": "no axiom sidecars authored yet (d-ax pending)"}

    # onto-sumo: the operator-rich demand sample.
    sumo_path = os.path.join(root, "data", "onto-sumo", "axioms.jsonl")
    if not os.path.isfile(sumo_path):
        fail("ERR_G6_CORPUS", "missing corpus file %s" % sumo_path)
    n = need = need_sidecar = skipped_meta = parse_errors = 0
    with open(sumo_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("operator") in METADATA_OPS:
                skipped_meta += 1
                continue
            try:
                tree = parse_kif(rec["kif"])
            except (ValueError, KeyError):
                parse_errors += 1
                continue
            n += 1
            needs, sidecar = classify(tree)
            if needs:
                need += 1
                if sidecar:
                    need_sidecar += 1
    if parse_errors:
        fail("ERR_G6_PARSE", "%d unparseable KIF axioms — instrument refuses partial counts" % parse_errors)
    by_source["onto-sumo"] = {"n_axioms": n, "n_need": need, "n_need_sidecar": need_sidecar,
                              "n_metadata_rows_excluded": skipped_meta}

    metrics = {
        "n_axioms": sum(s["n_axioms"] for s in by_source.values()),
        "n_need_and_under_operator": sum(s["n_need"] for s in by_source.values()),
        "n_need_and_sidecar_expressible": sum(s["n_need_sidecar"] for s in by_source.values()),
        "by_source": by_source,
    }
    print(json.dumps(metrics, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
