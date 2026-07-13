#!/usr/bin/env python3
"""
select_test_concepts.py -- deterministic, benchmark-blind selection of the 5
NEW concepts for the concept-def-agent smoke test: CONTINUE the pilot's frozen
round-robin selection rule (poc/scale/f1k-explication/gen_pilot.py /
pilot-review.md §1) past position 15, taking positions 16-20. This guarantees
(a) eligibility (P1: greedy_disjoint_m8 & header-clean, so coverage gate §1.3
holds), (b) genus-prefilter shape (R), (c) ZERO overlap with the pilot's 15,
and (d) no cherry-picking: no gloss, model outcome, or eval item was consulted.

Writes test-concepts.json. $0, no git, no registry. Author: designer-34.
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
POOL = json.load(open(ROOT / "poc/scale/f1k-eligibility/candidate-pool.json"))

# --- the pilot's frozen rule, verbatim (gen_pilot.py) ------------------------
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
while len(selected) < 20:
    for n in order:
        if idx[n] < len(buckets[n]):
            selected.append((n, buckets[n][idx[n]]))
            idx[n] += 1
            if len(selected) >= 20:
                break

pilot = selected[:15]
test = selected[15:20]
assert not {x["urn"] for _, x in pilot} & {x["urn"] for _, x in test}

rows = [{
    "position": 16 + i,
    "stratum": n,
    "concept": x["lemmas"][0],
    "urn": x["urn"],
    "pos": x["pos"],
    "lemmas": x["lemmas"],
    "wn31_gloss": x["gloss"],
    "m_test_screen": x["m_total"],
} for i, (n, x) in enumerate(test)]

out = {
    "built": "designer-34 concept-def-agent 5-concept smoke-test selection ($0, benchmark-blind)",
    "rule": ("pilot's frozen rule (gen_pilot.py): P1(disjoint_m8 & header-clean) -> "
             "genus prefilter R -> stratify AGENTIVE/ACT/STATE -> URN byte order -> "
             "round-robin; CONTINUED past 15, positions 16-20"),
    "pilot_positions_1_15_urns": [x["urn"] for _, x in pilot],
    "test_concepts": rows,
}
json.dump(out, open(HERE / "test-concepts.json", "w"), indent=2, ensure_ascii=False)
print(json.dumps(rows, indent=2, ensure_ascii=False))
print("wrote", HERE / "test-concepts.json")
