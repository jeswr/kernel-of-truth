#!/usr/bin/env python3
"""select_100.py -- deterministic, benchmark-blind selection of the FIRST 100
F1-K concepts, by CONTINUING the pilot's frozen round-robin selection rule
(poc/scale/concept-def-agent/select_test_concepts.py / gen_pilot.py) to
positions 1-100.

Identical rule to select_test_concepts.py, only the horizon changes (20 -> 100):
  P1 = eligible pool (greedy_disjoint_m8 & NOT header_cue_collision)
  -> genus prefilter into strata AGENTIVE / ACT / STATE (gloss-prefix match)
  -> within each stratum sort by URN byte order
  -> round-robin A, ACT, S (skip exhausted buckets), take positions 1..100.

Positions 1-15 are the pilot, 16-20 the smoke test; this is a superset, so
continuity with prior runs is guaranteed and no gloss/outcome is consulted for
ranking. $0, no git, no registry.
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
POOL = json.load(open(ROOT / "poc/scale/f1k-eligibility/candidate-pool.json"))

P1 = [x for x in POOL["candidates"]
      if x.get("greedy_disjoint_m8") and not x.get("header_cue_collision")]
STRATA = [
    ("AGENTIVE", [r"^someone who", r"^a person who", r"^a person that", r"^one who"]),
    ("ACT",      [r"^the act of", r"^an act of", r"^an event"]),
    ("STATE",    [r"^a state of", r"^the state of", r"^the quality of", r"^a feeling of"]),
]


def stratum(g):
    gl = g.lower().strip()
    for name, pats in STRATA:
        if any(re.match(p, gl) for p in pats):
            return name
    return None


buckets = {n: [] for n, _ in STRATA}
for x in P1:
    s = stratum(x["gloss"])
    if s:
        buckets[s].append(x)
for n in buckets:
    buckets[n].sort(key=lambda r: r["urn"])

order = ["AGENTIVE", "ACT", "STATE"]
idx = {n: 0 for n in order}
selected = []
N = 100
while len(selected) < N:
    progressed = False
    for n in order:
        if idx[n] < len(buckets[n]):
            selected.append((n, buckets[n][idx[n]]))
            idx[n] += 1
            progressed = True
            if len(selected) >= N:
                break
    if not progressed:
        break  # pool exhausted (shouldn't happen: 108 available)

assert len(selected) == N, "only %d concepts available" % len(selected)

rows = [{
    "position": 1 + i,
    "stratum": n,
    "concept": x["lemmas"][0],
    "urn": x["urn"],
    "pos": x["pos"],
    "lemmas": x["lemmas"],
    "wn31_gloss": x["gloss"],
    "m_test_screen": x["m_total"],
} for i, (n, x) in enumerate(selected)]

out = {
    "built": "consensus-100 first-100 F1-K selection ($0, benchmark-blind)",
    "rule": ("pilot's frozen rule (gen_pilot.py / select_test_concepts.py): "
             "P1(disjoint_m8 & header-clean) -> genus prefilter -> stratify "
             "AGENTIVE/ACT/STATE -> URN byte order -> round-robin; positions 1-100"),
    "n": N,
    "stratum_counts": {n: sum(1 for r in rows if r["stratum"] == n) for n in order},
    "concepts": rows,
}
json.dump(out, open(HERE / "concepts-100.json", "w"), indent=2, ensure_ascii=False)
print("stratum counts:", out["stratum_counts"])
print("first 3:", [(r["position"], r["concept"], r["urn"]) for r in rows[:3]])
print("last 3:", [(r["position"], r["concept"], r["urn"]) for r in rows[-3:]])
print("wrote", HERE / "concepts-100.json")
