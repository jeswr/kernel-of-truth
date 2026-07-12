#!/usr/bin/env python3
# Definition->constraint mapping extractor (PROPOSED-ASM-1415, review fix 4).
#
# Emits inputs/def-constraint-mapping.json: one row per compiled k1
# constraint, pairing the FULL plain-dictionary definition text (from
# knull_kinship_defs.json) with the constraint kind, subject/slots and the
# licensed_by span+reading the compiler recorded. This is the artifact the
# INDEPENDENT reviewer (a role that did not author the definitions or the
# compiler) signs off in inputs/mapping-review.json — lexical span
# traceability alone (the lint) does not establish a competent comparator
# or exclude compiler-induced collapse; a human-auditable semantic mapping
# review does. Mechanical extraction only; no judgement is made here.

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFS = HERE / "knull_kinship_defs.json"
TBOX = HERE / "inputs" / "tbox-knull"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    defs = json.loads(DEFS.read_text())
    def_by_term = defs["definitions"]  # {term: plain definition text}
    rows = []
    files = sorted(TBOX.rglob("*.json"))
    urn2term = {}
    man = json.loads((TBOX / "axioms-kinship-v1" / "manifest.json")
                     .read_text())
    for term, urn in (man.get("minted_urns") or {}).items():
        urn2term[urn] = term
    for f in files:
        if f.name == "manifest.json":
            continue
        rec = json.loads(f.read_text())
        for i, c in enumerate(rec.get("constraints", [])):
            lb = c.get("licensed_by") or {}
            term = lb.get("term")
            dfn = def_by_term.get(term)
            rows.append({
                "file": str(f.relative_to(HERE)),
                "file_sha256": sha(f),
                "constraint_index": i,
                "kind": c.get("kind"),
                "subject": rec.get("subject"),
                "subject_term": urn2term.get(rec.get("subject")),
                "slots": {k: v for k, v in c.items()
                          if k not in ("kind", "licensed_by")},
                "licensed_by_term": term,
                "licensed_by_span": lb.get("span"),
                "licensed_by_reading": lb.get("reading"),
                "full_definition": dfn,
            })
    out = {
        "schema": "kot-knull-def-constraint-mapping/1",
        "source_defs": {"path": "knull_kinship_defs.json",
                        "sha256": sha(DEFS)},
        "tbox": "inputs/tbox-knull",
        "n_constraints": len(rows),
        "review_protocol": (
            "INDEPENDENT REVIEW REQUIRED PRE-FREEZE (ASM-1415): a reviewer "
            "role that authored neither the definitions nor the compiler "
            "judges, per row: (a) is the constraint semantically licensed "
            "by the quoted definition read in its plain-dictionary sense? "
            "(b) is any definition content that a competent kinship "
            "ruleset needs MISSING from the compiled constraints "
            "(compiler-induced collapse hazard)? Verdicts land in "
            "inputs/mapping-review.json; pass==true is a mandatory "
            "component of /gates/compilation_lint_valid."),
        "rows": rows,
    }
    dst = HERE / "inputs" / "def-constraint-mapping.json"
    dst.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("->", dst, "(%d constraint rows)" % len(rows))


if __name__ == "__main__":
    main()
