#!/usr/bin/env python3
"""Instrument-validity positive control for the b-cov define-lane census.

Proves the mapper->engine->§C5 pipeline yields a define-checkable (n==1, engine
DEFINE-MATCH true) when fed a question that DOES target an endorsed onto-obo
definition — so the census's 0.0000 kappa on the Tier-A benchmarks is a REAL
MEASURED null, not a broken harness. Target: GO:0000018 "regulation of DNA
recombination" = "biological regulation" (GO:0065007) that "regulates"
"DNA recombination" (GO:0006310). Run: python3 poc/b-cov-define-lane/positive_control.py
"""
import json, os, sys, subprocess, collections, tempfile

ROOT = "."
HERE = os.path.join(ROOT, "poc", "b-cov-define-lane")
sys.path.insert(0, os.path.join(ROOT, "tools", "axiom"))
sys.path.insert(0, HERE)
import kot_axiom as K  # noqa: E402
import census as C  # noqa: E402

ITEMS = [
    {"id": "pc-whichterm",
     "text": "which term means biological regulation that regulates DNA recombination",
     "options": ["regulation of DNA recombination", "photosynthesis"]},
    {"id": "pc-isa",
     "text": "is regulation of DNA recombination a biological regulation that regulates DNA recombination",
     "options": []},
    {"id": "pc-whatis",
     "text": "what is regulation of DNA recombination?", "options": []},
]


def main():
    eng = K.build_engine(ROOT)
    inv = collections.defaultdict(list)
    for x, e in eng.defn.items():
        inv[C.canon_key(e["genus"], e["differentiae"])].append(x)

    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False,
                                     dir=HERE, encoding="utf-8") as tf:
        for it in ITEMS:
            tf.write(json.dumps(it, ensure_ascii=False) + "\n")
        ip = tf.name
    op = ip + ".parses"
    subprocess.run(["node", os.path.join(HERE, "run_mapper.mjs"),
                    os.path.join(HERE, "define-index.json"), ip, op], check=True)

    ok = True
    for line in open(op, encoding="utf-8"):
        rec = json.loads(line)
        p = rec["parse"]
        kind = p["kind"]
        cand = (p.get("candidate") if kind == "candidate"
                else p["query"].get("candidate") if kind == "query" else None)
        if cand is not None:
            dp = [(d["relation"], d["filler"]) for d in cand["differentiae"]]
            n = len(inv.get(C.canon_key(cand["genus"], dp), ()))
            u = inv[C.canon_key(cand["genus"], dp)][0] if n == 1 else None
            match = (eng.query({"op": "define", "subject": u, "candidate": cand}).get("value")
                     if u else None)
            passed = (n == 1 and match is True)
            ok = ok and passed
            print("%-14s kind=%-9s C5_n=%d DEFINE-MATCH=%s %s" % (
                rec["id"], kind, n, match, "PASS" if passed else "FAIL"))
        elif kind == "query":
            st = eng.query(p["query"]).get("status")
            passed = st == "answer"
            ok = ok and passed
            print("%-14s kind=%-9s DEFINE-retrieve engine=%s %s" % (
                rec["id"], kind, st, "PASS" if passed else "FAIL"))
    os.unlink(ip)
    os.unlink(op)
    print("POSITIVE CONTROL:", "PASS (instrument valid)" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
