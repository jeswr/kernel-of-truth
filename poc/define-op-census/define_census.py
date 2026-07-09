#!/usr/bin/env python3
"""MEASURED define-op internal-coverage census (Opus execution, no interpretation).
Drives the FROZEN engine tools/axiom/kot_axiom.py over the onto-obo logicalDefinition
concepts in the endorsed shards {go,so,mondo}, counting engine-CHECKABLE (status=answer)
vs refuse, broken down by shard x refusal code. The endorsement used to drive the engine
is an in-memory throwaway whose subject is a non-load-bearing placeholder concept URN:
the engine licenses the define-op BY SHARD MEMBERSHIP (source.shard), not by subject, so
the subject value does not affect any coverage count (verified: kot_axiom
_build_definitional_index ignores the endorsement subject)."""
import json, sys, collections
sys.path.insert(0, "tools/axiom")
import kot_axiom as K

ROOT = "."
SHARDS = ["go.jsonl", "so.jsonl", "mondo.jsonl"]
SHA = {  # sha256 of current bytes == manifest (verified 2026-07-09)
    "go.jsonl":    "sha256:6c65be58f05cd34a0efb35155ac58b3f1e668e6172d623d883b2d57c4e426d2d",
    "so.jsonl":    "sha256:46c98b1bd36297361ea48f9ea5554222c6ee119e756538b2a614ff0c372e6ca6",
    "mondo.jsonl": "sha256:232799bb92627fa90533686ea595d2fd1a6ff6dcbdfafe1e8fb41b8738fe3d6c",
}

bridge = K.load_mint_bridge(ROOT)
PLACEHOLDER_SUBJECT = bridge["urn:onto-obo:GO_0000018"]  # non-load-bearing (see docstring)

obo_shards = {s: K.load_obo_shard(ROOT, s) for s in SHARDS}
endorsements = []
for s in SHARDS:
    rec = {"schema": "kot-axiom/1", "subject": PLACEHOLDER_SUBJECT,
           "constraints": [{"kind": "definitional", "form": "obo-genus-differentia",
                            "source": {"corpus": "onto-obo", "shard": s,
                                       "sourceVersion": SHA[s]}}]}
    endorsements.append(("census-endorse/%s" % s, rec))

eng = K.Engine(endorsements, [], obo_shards=obo_shards, mint_bridge=bridge)

# Census population: every minted record carrying a logicalDefinition, per shard.
rows = collections.defaultdict(lambda: collections.Counter())
totals = collections.Counter()
unminted = collections.Counter()
for s in SHARDS:
    for r in obo_shards[s]:
        if not isinstance(r.get("logicalDefinition"), dict):
            continue
        totals[s] += 1
        urn = bridge.get(r.get("id"))
        if urn is None:
            unminted[s] += 1
            continue
        res = eng.query({"op": "define", "subject": urn})
        key = "ANSWER" if res.get("status") == "answer" else res.get("code")
        rows[s][key] += 1

print("=== MEASURED define-op internal coverage (DEFINE over logicalDefinition concepts) ===")
allkeys = ["ANSWER", "ERR_DEFN_UNRESOLVED", "ERR_NO_DEFINITION", "ERR_TERM_UNLICENSED"]
grand = collections.Counter()
for s in SHARDS:
    line = "%-11s pop=%5d  " % (s, totals[s])
    for k in allkeys:
        line += "%s=%d  " % (k, rows[s][k])
        grand[k] += rows[s][k]
    if unminted[s]:
        line += "UNMINTED=%d  " % unminted[s]
    print(line)
tot_pop = sum(totals.values())
print("%-11s pop=%5d  " % ("TOTAL", tot_pop) +
      "  ".join("%s=%d" % (k, grand[k]) for k in allkeys))
print("checkable(ANSWER)=%d / population=%d = %.4f" %
      (grand["ANSWER"], tot_pop, grand["ANSWER"]/tot_pop))
# index-level cross-check (independent of the per-record loop)
print("--- engine index cross-check ---")
print("defn_licensed=%d  defn(resolved)=%d  defn_unresolved=%d" %
      (len(eng.defn_licensed), len(eng.defn), len(eng.defn_unresolved)))
