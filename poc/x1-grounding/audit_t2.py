#!/usr/bin/env python3
"""
X1-grounding threat T2 audit (PREREG §8): sample 100 random (gloss token ->
lemma) resolutions with seed 7 for manual audit of lemmatization noise.
Emits t2-audit-sample.json (the 100 samples with gloss context).
Population = every successful (token -> lemma) resolution event, in synset
file order (noun,verb,adj,adv), token order within a synset gloss.
"""
import json
import os
import random

import x1g_lib as L
import build_graph


def collect_population():
    per_pos, union = L.load_index()
    exc = L.load_exc()
    morphy = L.Morphy(per_pos, union, exc)
    events = []  # (pos, synset_id, token, lemma, gloss)
    for pos, rec in build_graph.iter_synsets(L.SYNSET_FILES):
        gloss = (rec.get("annotations", {}).get("gloss", "") or "")
        cleaned = L.clean_gloss(gloss)
        for tok in L.tokenize(cleaned):
            for lem in morphy.resolve_token(tok):
                events.append((pos, rec.get("id", ""), tok, lem, gloss))
    return events


def main():
    events = collect_population()
    n = len(events)
    idx = sorted(random.Random(7).sample(range(n), 100))
    samples = []
    for rank, i in enumerate(idx):
        pos, sid, tok, lem, gloss = events[i]
        samples.append({
            "n": rank + 1,
            "populationIndex": i,
            "pos": pos,
            "synsetId": sid,
            "token": tok,
            "resolvedLemma": lem,
            "gloss": gloss,
        })
    out = {
        "schema": "x1g-t2-audit/1",
        "seed": 7,
        "populationSize": n,
        "sampleSize": 100,
        "samples": samples,
    }
    L.dump_json_pretty(out, os.path.join(L.HERE, "t2-audit-sample.json"))
    print("t2 audit: population=%d, wrote 100 samples" % n)
    for s in samples:
        print("%3d [%s] %-22s -> %-20s | %s" % (
            s["n"], s["pos"], s["token"], s["resolvedLemma"], s["gloss"][:70]))


if __name__ == "__main__":
    main()
