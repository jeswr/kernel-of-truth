#!/usr/bin/env python3
"""[ASM-2513 v4, round-3 #3] The SS4 re-pin splice — the ONE exact,
reusable implementation (spec: poc/gcp/F1K-PIN-FILE-FIX.md SS4). Run
from the REPO ROOT. Used verbatim by BOTH the live SS7-B1 splice
(ROOT=".") and the SS7-B1n negative-probe variants (ROOT=<scratch
copy>) — no verbatim-placeholder duplication. ROOT roots ONLY the
registry pair; the analysis bytes are always the working tree's.
Guards ([v3, re-review #5], CLOSED round 3 — logic and assert messages
byte-stable): (i) recomputed record/index consistency, then (ii) the
ORIG-counterfactual, BOTH before either exit path; writes come only
after both asserts."""
import copy, json, sys, hashlib
sys.path.insert(0, "tools/registry")
import kot_common as kc
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
ORIG_ANA = "54924cfd0f1b7878da53228aa54f3cdf3e405aa4d0ecefd185fcb75da9eea8eb"
ORIG_FRZ = "01cf2b17a882b2ab89873234a381720108dbb9d0dcd406a752962e280b71dc55"
NEW_ANA = hashlib.sha256(open("analysis/f1k.py", "rb").read()).hexdigest()
p = ROOT + "/registry/experiments/f1k.json"
raw = open(p, encoding="utf-8").read()
rec = json.loads(raw)
cur = rec["pins"]["analysis_script"]["sha256"]
assert raw.count(cur) == 1, "expected exactly one analysis-pin site"
idx = json.loads(open(ROOT + "/registry/frozen-index.json",
                      encoding="utf-8").read())
# [v3, re-review #5] BEFORE either the no-op exit OR the update path:
# (i) RECOMPUTED consistency — index, STORED record hash, and the
#     freshly RECOMPUTED frozen hash of the record AS IT IS must all
#     agree. A mismatch is a dirty/corrupt record, NOT a resume. (v2
#     compared only index == stored hash and the cur==NEW_ANA no-op
#     exited before any recomputation at all.)
assert idx["f1k"] == rec["frozen_sha256"] == kc.frozen_hash(rec), \
    "record/index/recompute desync — dirty or corrupt record; STOP"
# (ii) ORIG-COUNTERFACTUAL — normalizing ONLY the analysis pin back to
#     ORIG_ANA in a deep copy must reproduce ORIG_FRZ: the analysis
#     pin is PROVEN the SOLE delta being re-frozen. This also kills a
#     "forged-consistent" dirty record whose frozen_sha256 was
#     recomputed over unrelated edits — (i) alone passes that case
#     [MEASURED: both the pass and both refusal branches demoed on the
#     real committed record, this box 2026-07-18]. Subsumes v2's
#     first-pass-only chain-head check on every pass.
cf = copy.deepcopy(rec)
cf["pins"]["analysis_script"]["sha256"] = ORIG_ANA
assert kc.frozen_hash(cf) == ORIG_FRZ, \
    "record carries edits BEYOND the analysis pin — refusing to " \
    "re-freeze them; diff the record against the committed bytes"
if cur == NEW_ANA:
    print("no-op: record already pins the current analysis bytes")
    sys.exit(0)
rec["pins"]["analysis_script"]["sha256"] = NEW_ANA
new_frz = kc.frozen_hash(rec)          # status + frozen_sha256 excluded
rec["frozen_sha256"] = new_frz
kc.write_canonical_json(p, rec)
idx["f1k"] = new_frz
kc.write_canonical_json(ROOT + "/registry/frozen-index.json", idx)
print("NEW_ANALYSIS_SHA =", NEW_ANA)
print("NEW_FROZEN_SHA   =", new_frz)
