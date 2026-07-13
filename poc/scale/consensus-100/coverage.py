#!/usr/bin/env python3
"""coverage.py -- per-model COVERAGE over the 100 concepts: how many concepts
each model successfully defined (ok) vs failed (timeout / nonjson / refused /
cap / error), and WHICH concepts each model failed on. Coverage is a first-class
signal for the "cheapest viable model at scale" question.

Sources of truth (in priority order for a non-ok cell):
  1. a written record gen/<slug>.<short>.json  -> ok
  2. coverage-rerun.jsonl (the timed re-run classification) for that cell
  3. run-log.jsonl final status for that cell (fail/capped/done)
$0, no git.
"""
import json
import pathlib
import re
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
GEN = HERE / "gen"
SHORT = {"claude-opus-4-8": "opus48", "claude-fable-5": "fable5",
         "claude-haiku-4-5": "haiku45", "gpt-5.6-sol": "gpt56sol",
         "gpt-5.6-luna": "gpt56luna", "gpt-5.6-terra": "gpt56terra"}
MODELS = list(SHORT)


def slug(l):
    s = l.lower().replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def main():
    data = json.load(open(HERE / "concepts-100.json"))
    rows = data["concepts"]

    rerun = {}
    rf = HERE / "coverage-rerun.jsonl"
    if rf.exists():
        for l in rf.read_text().splitlines():
            if l.strip():
                d = json.loads(l)
                rerun[(d["concept"], d["model"])] = d

    runlog = {}
    lf = HERE / "run-log.jsonl"
    if lf.exists():
        for l in lf.read_text().splitlines():
            if not l.strip():
                continue
            d = json.loads(l)
            runlog[(d.get("concept"), d.get("model"))] = d

    per_model = {m: defaultdict(list) for m in MODELS}  # status -> [concepts]
    grid = []
    for r in rows:
        c = r["concept"]
        sl = slug(c)
        cell = {"concept": c, "position": r["position"]}
        for m in MODELS:
            if (GEN / f"{sl}.{SHORT[m]}.json").exists():
                st = "ok"
            elif (c, m) in rerun:
                st = rerun[(c, m)]["status"]
            elif (c, m) in runlog:
                s = runlog[(c, m)]["status"]
                st = {"done": "ok", "capped": "cap", "fail": "nonjson",
                      "gap": "gap"}.get(s, s)
            else:
                st = "missing"
            per_model[m][st].append(c)
            cell[m] = st
        grid.append(cell)

    summary = {}
    for m in MODELS:
        d = per_model[m]
        ok = len(d.get("ok", []))
        fails = {k: v for k, v in d.items() if k != "ok"}
        summary[m] = {
            "ok": ok, "coverage_rate": round(ok / len(rows), 4),
            "failures": {k: len(v) for k, v in fails.items()},
            "failed_concepts": {k: v for k, v in fails.items()},
        }

    out = {"built": "consensus-100 per-model coverage",
           "n_concepts": len(rows), "per_model": summary, "grid": grid}
    json.dump(out, open(HERE / "coverage.json", "w"), indent=2, ensure_ascii=False)

    print("=== PER-MODEL COVERAGE (of %d concepts) ===" % len(rows))
    for m in MODELS:
        s = summary[m]
        fl = s["failures"]
        fc = "; ".join(f"{k}:{v}" for k, v in s["failed_concepts"].items())
        print(f"  {m:18} ok={s['ok']:3}/{len(rows)} ({s['coverage_rate']*100:.0f}%)  "
              f"fails={fl or '{}'}  {('['+fc+']') if fc else ''}")
    print("wrote", HERE / "coverage.json")


if __name__ == "__main__":
    main()
