#!/usr/bin/env python3
"""blinding-sweep — post-pass §7.3 audit sweep (blinding-audit-clarification.md §5).
usage: blinding-sweep.py <run_dir>   -> writes <run_dir>/blinding-sweep.json"""
import importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rdj", os.path.join(HERE, "run-dts-judges.py"))
rdj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rdj)
HEX = rdj._HEX_BYTES

def hex_embedded_occurrences(data, token):
    out, i = [], data.find(token)
    while i >= 0:
        j0, j1 = i, i + len(token)
        while j0 > 0 and data[j0 - 1] in HEX:
            j0 -= 1
        while j1 < len(data) and data[j1] in HEX:
            j1 += 1
        if (j0, j1) != (i, i + len(token)):
            out.append({"offset": i, "hex_run": data[j0:j1].decode()})
        i = data.find(token, i + 1)
    return out

def main(run_dir):
    hits, exclusions = [], []
    for dirpath, _, names in sorted(os.walk(run_dir)):
        for name in sorted(names):
            if name not in ("user-prompt.txt", "events.jsonl", "stderr.log"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, run_dir)
            if rdj.blinding_scan([path]):
                hits.append(rel)
            data = open(path, "rb").read().lower()
            for t in rdj.BLIND_TOKENS:
                if not all(c in HEX for c in t):
                    continue
                for occ in hex_embedded_occurrences(data, t):
                    occ.update({"file": rel, "token": t.decode()})
                    exclusions.append(occ)
    out = {"run_dir": os.path.basename(run_dir.rstrip("/")),
           "clarified_hits": hits, "n_exclusions": len(exclusions),
           "exclusions": exclusions,
           "verdict": "GREEN" if not hits else "RED"}
    with open(os.path.join(run_dir, "blinding-sweep.json"), "w") as f:
        f.write(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(out["verdict"], "hits=%d exclusions=%d" % (len(hits), len(exclusions)))
    sys.exit(0 if not hits else 1)

if __name__ == "__main__":
    main(sys.argv[1])
