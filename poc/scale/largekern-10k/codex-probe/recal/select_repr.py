#!/usr/bin/env python3
"""select_repr.py — draw a REPRESENTATIVE ~25-concept calibration sample from
the materialized 10k worklist, stratified by POS x polysemy band exactly as the
pilot's own draw is (frame_sample.polysemy_bands, ASM-2498), proportional to the
worklist's stratum composition (largest-remainder allocation).

This is DELIBERATELY not the first probe's adversarial edge-case set
(war/aba/letter-C/crapulent/key-as-regulate-pitch). It is a proportional draw so
the measured accept-fraction extrapolates honestly to the 10k. Seed distinct from
the pilot's operative seed (this is a calibration draw, not the pilot draw).

Outputs: recal/out/selected-repr.json  +  recal/out/repr-sample-manifest.json
No network, no benchmark bytes, no model output read.
"""
import hashlib
import json
import os
import random
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.abspath(os.path.join(HERE, "..", "..", "pipeline"))
sys.path.insert(0, PIPE)
import common          # noqa: E402
import frame_sample    # noqa: E402

N = 25
SEED = "largekern10k-codexcal-repr-v1"   # calibration seed (NOT the pilot seed)
OUT = os.path.join(HERE, "out")


def main():
    os.makedirs(OUT, exist_ok=True)
    worklist = [json.loads(l) for l in open(os.path.join(common.OUT_DIR, "worklist.jsonl"))
                if l.strip()]
    # bands via the pilot's own mechanical banding (ASM-2498), over the full frame
    frame, total, _ = frame_sample.load_frame()
    frame_sample.verify_frame(frame, total)            # fail closed if frame drifted
    bands = frame_sample.polysemy_bands(frame)

    strata = defaultdict(list)
    for row in worklist:
        band = bands[row["conceptId"]]
        strata[(row["pos"], band)].append(row)
    keys = sorted(strata.keys())
    for k in keys:
        strata[k].sort(key=lambda r: r["conceptId"])   # deterministic member order
    total_wl = len(worklist)

    # largest-remainder proportional allocation of N over strata (matches
    # frame_sample.stratified_draw), so the sample mirrors the 10k composition.
    quotas = [(k, N * len(strata[k]) / float(total_wl)) for k in keys]
    alloc = {k: int(q) for k, q in quotas}
    short = N - sum(alloc.values())
    for k, q in sorted(quotas, key=lambda kq: (-(kq[1] - int(kq[1])), kq[0]))[:short]:
        alloc[k] += 1

    rng = random.Random(int(hashlib.sha256(SEED.encode("utf-8")).hexdigest(), 16) % (2 ** 64))
    sample, strata_table = [], {}
    for k in keys:
        members = strata[k]
        take = min(alloc[k], len(members))
        drawn = rng.sample(members, take)
        sample += drawn
        strata_table["%s/%s" % k] = {"worklist": len(members), "drawn": take}
    sample.sort(key=lambda r: r["conceptId"])
    if len(sample) != N:
        raise SystemExit("drew %d != %d" % (len(sample), N))

    json.dump(sample, open(os.path.join(OUT, "selected-repr.json"), "w"), indent=1)
    manifest = {
        "schema": "kv1d-codexcal-repr/1",
        "n": len(sample),
        "seed": SEED,
        "seedNote": "calibration draw seed; distinct from the pilot operative seed",
        "worklist": os.path.relpath(os.path.join(common.OUT_DIR, "worklist.jsonl"), common.REPO_ROOT),
        "worklistTotal": total_wl,
        "polysemyBandRule": "ASM-2498 (frame_sample.polysemy_bands)",
        "allocation": "largest-remainder proportional to worklist strata",
        "strata": strata_table,
        "sampleConceptIds": [r["conceptId"] for r in sample],
        "sampleSha256": hashlib.sha256(
            "\n".join(r["conceptId"] for r in sample).encode("utf-8")).hexdigest(),
    }
    json.dump(manifest, open(os.path.join(OUT, "repr-sample-manifest.json"), "w"), indent=1)
    print("OK drew %d from %d worklist rows" % (len(sample), total_wl))
    for k in keys:
        print("  %-8s worklist=%5d drawn=%d" % ("%s/%s" % k, len(strata[k]), alloc[k]))
    print("sampleSha256", manifest["sampleSha256"][:16])


if __name__ == "__main__":
    main()
