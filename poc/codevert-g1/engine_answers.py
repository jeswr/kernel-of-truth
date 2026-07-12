#!/usr/bin/env python3
"""Engine answers for the 200 sampled queries, normalized per ASM-1115.
Run AFTER prompts are frozen; output never enters any annotator context."""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "..", "codevert-g0"))
sys.setrecursionlimit(100000)
from extractor import Extractor
from engine import World, run_query


def main():
    sample = json.load(open(os.path.join(BASE, "annotation", "sample.json")))
    by_repo = {}
    for q in sample["queries"]:
        by_repo.setdefault(q["repo"], []).append(q)
    out = {}
    for repo, qs in sorted(by_repo.items()):
        root = os.path.join(BASE, "corpus", repo)
        ex = Extractor(root, repo)
        edges = ex.extract()
        world = World(edges, ex.modules)
        linecache = {}

        def to_line(file, off):
            if file not in linecache:
                linecache[file] = open(os.path.join(root, file), "rb").read()
            return linecache[file][:off].count(b"\n") + 1

        for q in qs:
            st, listing, blocking = run_query(world, q["family"], q["target"])
            norm = []
            for el in listing:
                if isinstance(el, tuple):  # where_defined: (file, span)
                    norm.append("%s:%d" % (el[0], to_line(el[0], el[1][0])))
                else:
                    norm.append(el)
            out[q["query_id"]] = {"status": st, "listing": sorted(set(norm)),
                                  "blocking": blocking}
    with open(os.path.join(BASE, "results", "sample-engine-answers.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    sts = {}
    for v in out.values():
        sts[v["status"]] = sts.get(v["status"], 0) + 1
    print("engine answers:", len(out), sts)


if __name__ == "__main__":
    main()
