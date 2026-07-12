#!/usr/bin/env python3
# RULES-1 differential conformance check (PROPOSED-ASM-1124, MD-4a):
# sparq-reason (Rust, primary) vs the Python twin — EXACT agreement on Cl(S)
# for every item, or the run halts.
#
# Method: the same compiled rule inventory (WMRE-1 §3 rules.n3 — R-SUBP,
# R-DOM/RNG, R-CHAIN, the two compiled R-COVER-ELIM member-elimination Horn
# rules, and owl:differentFrom symmetry) is rendered ONCE from the pinned
# TBox into N3; each item's stated facts are appended; sparq-reason's
# reason_n3 fixpoint computes the closure via
# conformance/target/release/rules1-conformance; the twin computes Cl(S) in
# process. Closures are compared term-for-term after normalisation
# (rel -> (s,p,o); cls -> rdf:type; differentFrom -> unordered pair).
# DISCLOSURE: this exercises sparq-reason's N3 fixpoint entry point (the
# rules.n3 compilation target named in the design), not its OwlRl
# materializer; both engines consume the same compiled rule artifact.
#
# Coverage: all 958 nsk1-clutrr items + all 248 world-v0 E1 cells + the §3
# worked example. Zero disagreements required.

import json
import subprocess
import tempfile
from pathlib import Path

from twin_engine import load_tbox, Closure
from certificate import (TBOX_PINNED, MOTHER, FATHER, ROOT, HERE,
                         load_worlds, una, build_e1_cells)

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
DIFF = "http://www.w3.org/2002/07/owl#differentFrom"
DRIVER = HERE / "conformance" / "target" / "release" / "rules1-conformance"


def compile_rules_n3(tbox):
    """Render the pinned TBox as the WMRE-1 §3 rules.n3 artifact."""
    lines = []
    for p in sorted(tbox.subprop):
        for sup, ref in sorted(tbox.subprop[p]):
            lines.append(f"{{ ?x <{p}> ?y }} => {{ ?x <{sup}> ?y }} .")
    for p in sorted(tbox.domain):
        cls, _ = tbox.domain[p]
        lines.append(f"{{ ?x <{p}> ?y }} => {{ ?x <{RDF_TYPE}> <{cls}> }} .")
    for p in sorted(tbox.range):
        cls, _ = tbox.range[p]
        lines.append(f"{{ ?x <{p}> ?y }} => {{ ?y <{RDF_TYPE}> <{cls}> }} .")
    for p1, p2, sup, _ in sorted(tbox.chains):
        lines.append(f"{{ ?x <{p1}> ?y . ?y <{p2}> ?z }} => "
                     f"{{ ?x <{sup}> ?z }} .")
    lines.append(f"{{ ?a <{DIFF}> ?b }} => {{ ?b <{DIFF}> ?a }} .")
    # R-COVER-ELIM compiled per eliminable member (2-member kinship cover ->
    # the two Horn rules of WMRE-1 §3; premises ASM-1120/1121 named there).
    for P, members, _ in sorted(tbox.covers):
        for elim in members:
            if elim not in tbox.functional:
                continue
            rest = [m for m in members if m != elim]
            if len(rest) != 1:
                continue
            lines.append(
                f"{{ ?c <{elim}> ?m . ?c <{P}> ?p . ?m <{DIFF}> ?p }} => "
                f"{{ ?c <{rest[0]}> ?p }} .")
    return "\n".join(lines) + "\n"


def facts_n3(stated):
    out = []
    for f in stated:
        if f[0] == "rel":
            out.append(f"<{f[1]}> <{f[2]}> <{f[3]}> .")
        elif f[0] == "cls":
            out.append(f"<{f[1]}> <{RDF_TYPE}> <{f[2]}> .")
        else:
            out.append(f"<{f[1]}> <{DIFF}> <{f[2]}> .")
    return "\n".join(out) + "\n"


def normalise(triples):
    norm = set()
    for s, p, o in triples:
        if p == RDF_TYPE:
            norm.add(("cls", s, o))
        elif p == DIFF:
            norm.add(("diff",) + tuple(sorted((s, o))))
        else:
            norm.add(("rel", s, p, o))
    return norm


def twin_normal(cl):
    return {f if f[0] != "rel" else f for f in cl.facts()}


def main():
    tbox = load_tbox(TBOX_PINNED)
    rules = compile_rules_n3(tbox)
    u = json.load((ROOT / "data/axioms-kinship-v1/manifest.json")
                  .open())["minted_urns"]
    items = [json.loads(x) for x in
             (ROOT / "data/nsk1-clutrr/items.jsonl").open()]
    worlds = load_worlds()
    cases = []
    for it in items:
        cases.append((it["item_id"],
                      worlds.get(it["item_id"], []) +
                      una(it["lexicon"].keys())))
    for cell in build_e1_cells(u["parent"]):
        cases.append((cell["id"], cell["stated"]))
    cases.append(("worked-example-s3",
                  [("rel", "urn:kotw:x:andy", MOTHER, "urn:kotw:x:hazza"),
                   ("rel", "urn:kotw:x:andy", u["parent"],
                    "urn:kotw:x:bazza"),
                   ("diff", "urn:kotw:x:bazza", "urn:kotw:x:hazza")]))

    tmp = Path(tempfile.mkdtemp(prefix="rules1-conf-"))
    paths = []
    for cid, stated in cases:
        p = tmp / f"{cid}.n3"
        p.write_text(facts_n3(stated) + rules)
        paths.append((cid, stated, str(p)))

    agree = disagree = 0
    diffs = []
    B = 200
    for i in range(0, len(paths), B):
        batch = paths[i:i + B]
        res = subprocess.run([str(DRIVER)] + [p for _, _, p in batch],
                             capture_output=True, text=True, check=True)
        outs = [json.loads(line) for line in res.stdout.splitlines()]
        by_file = {o["file"]: o["triples"] for o in outs}
        for cid, stated, p in batch:
            sparq = normalise(by_file[p])
            twin = Closure(tbox, stated).facts()
            if sparq == twin:
                agree += 1
            else:
                disagree += 1
                if len(diffs) < 5:
                    diffs.append({"case": cid,
                                  "sparq_only": sorted(map(list,
                                                           sparq - twin))[:5],
                                  "twin_only": sorted(map(list,
                                                          twin - sparq))[:5]})
    result = {
        "check": "rules-1 differential conformance (ASM-1124)",
        "engines": {"primary": "sparq-reason reason_n3 (Rust, release, "
                               "commit of local checkout)",
                    "twin": "poc/rules-1/twin_engine.py"},
        "cases": len(paths), "agree": agree, "disagree": disagree,
        "exact_agreement": disagree == 0,
        "rules_n3_lines": rules.count("\n"),
        "first_disagreements": diffs,
        "disclosure": ("N3 fixpoint entry point exercised (the rules.n3 "
                       "compilation target); OwlRl materializer path not "
                       "exercised. Same compiled rule artifact consumed by "
                       "both engines."),
    }
    out = HERE / "results" / "conformance-result.json"
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    (HERE / "results" / "rules.n3").write_text(rules)
    print(json.dumps(result, indent=1))
    if disagree:
        raise SystemExit("ERR_TWIN_DISAGREEMENT")


if __name__ == "__main__":
    main()
