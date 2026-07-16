#!/usr/bin/env python3
"""frame_sample.py — component 1: FRAME + SAMPLE (spec §1, P1; ASM-2474 builder
contract, ASM-2493 pinned frame values).

Materializes the pinned WordNet-10k frame from the pinned WN31 shards:
  frame = every kot-lex/1 record whose axioms carry NO instanceHypernym
  relation (the frozen screen_candidates.py load_instance_urns / SOP-1
  predicate, f1k-large-kernel-rebuild.md §2.1 step 2).
Recomputes count + frameSha256 = sha256(UTF-8("\n"-join(lexicographically
sorted frame synset URNs))) and FAILS CLOSED (ERR_FRAME_HASH) unless
count == 110,049 AND hash == the pinned value (§1).

Worklist exclusion (§9.3): every synset in alignment-kernel-v0.json (the 107
frozen kernel-v0 alignments) is excluded BEFORE the draw; any denylisted
synset found in a built worklist is ERR_FROZEN_OVERLAP.

Sampling rule (§1, pinned, seeded, single-draw): 10,000 synsets, seeded
stratified over POS x polysemy band (monosemous / 2-5 same-POS senses / >=6),
proportional to the frame composition (largest-remainder allocation).
Mechanical band definition [STIPULATED ASM-2498, designer-20]: a synset's
polysemy = max over its lemmas of the number of same-POS FRAME synsets whose
lemma list contains that lemma (case-sensitive, as extracted). Seed pinned in
common.SAMPLE_SEED and recorded in the manifest; the operative seed is
registered at prereg-freeze (a re-draw is a new experiment id).

Outputs (mock store): out/worklist.jsonl (one row per candidate:
{conceptId, lemma, pos, wnGloss, sourceRowSha256}) + out/sample-manifest.json.
No benchmark bytes, no eval items, no kernel explication text, no model
outputs are read (§1 blindness).
"""

import hashlib
import json
import os
import random
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import PipelineError


def load_frame():
    """Stream the pinned shards; return (frame_rows, n_total, n_instances).
    frame_rows: urn -> {lemma, lemmas, pos, gloss, sourceRowSha256}."""
    frame = {}
    total = 0
    instances = 0
    for fn in common.WN31_SHARDS:
        path = os.path.join(common.WN31_DIR, fn)
        with open(path, "rb") as f:
            for raw in f:
                total += 1
                d = json.loads(raw.decode("utf-8"))
                if any(a.get("rel") == "instanceHypernym" for a in d.get("axioms", [])):
                    instances += 1
                    continue
                ann = d.get("annotations", {})
                lemmas = ann.get("lemmas") or []
                frame[d["id"]] = {
                    "lemma": lemmas[0] if lemmas else "",
                    "lemmas": lemmas,
                    "pos": d.get("pos", "?"),
                    "gloss": ann.get("gloss", ""),
                    # exact source line bytes (incl. newline) -> sourceRowSha256
                    "sourceRowSha256": hashlib.sha256(raw).hexdigest(),
                }
    return frame, total, instances


def verify_frame(frame, total):
    """§1 fail-closed recompute-and-match (ERR_FRAME_HASH), against the
    ASM-2493 pinned values. Returns the recomputed hash."""
    if total != common.CENSUS_TOTAL:
        raise PipelineError("ERR_FRAME_HASH",
                            "shard census %d != pinned %d" % (total, common.CENSUS_TOTAL))
    urns = sorted(frame.keys())
    if len(urns) != common.FRAME_COUNT:
        raise PipelineError("ERR_FRAME_HASH",
                            "frame count %d != pinned %d" % (len(urns), common.FRAME_COUNT))
    h = hashlib.sha256("\n".join(urns).encode("utf-8")).hexdigest()
    if h != common.FRAME_SHA256:
        raise PipelineError("ERR_FRAME_HASH",
                            "frameSha256 %s != pinned %s" % (h, common.FRAME_SHA256))
    return h


def load_denylist():
    """§9.3: frozen kernel-v0 alignment synsets, never re-drafted."""
    a = common.read_json(common.ALIGNMENT_PATH)
    return set(row["synset"] for row in a["alignments"])


def check_frozen_overlap(worklist_urns, denylist):
    hits = sorted(set(worklist_urns) & denylist)
    if hits:
        raise PipelineError("ERR_FROZEN_OVERLAP",
                            "%d frozen kernel-v0 synsets in the worklist, e.g. %s" % (len(hits), hits[:3]))


def polysemy_bands(frame):
    """ASM-2498 mechanical banding. Returns urn -> band in {'mono','2-5','6+'}."""
    lemma_pos_count = defaultdict(int)
    for urn, row in frame.items():
        for lem in row["lemmas"]:
            lemma_pos_count[(lem, row["pos"])] += 1
    bands = {}
    for urn, row in frame.items():
        n = max((lemma_pos_count[(lem, row["pos"])] for lem in row["lemmas"]), default=1)
        bands[urn] = "mono" if n <= 1 else ("2-5" if n <= 5 else "6+")
    return bands


def stratified_draw(frame, denylist, n=None, seed=None):
    """Seeded stratified proportional single draw (§1). Deterministic:
    strata processed in sorted order, members sorted lexicographically,
    one Random seeded from sha256(seed string)."""
    n = n or common.SAMPLE_N
    seed = seed or common.SAMPLE_SEED
    bands = polysemy_bands(frame)
    eligible = [u for u in sorted(frame.keys()) if u not in denylist]
    strata = defaultdict(list)
    for u in eligible:
        strata[(frame[u]["pos"], bands[u])].append(u)
    total = len(eligible)
    keys = sorted(strata.keys())
    # largest-remainder proportional allocation
    quotas = [(k, n * len(strata[k]) / float(total)) for k in keys]
    alloc = {k: int(q) for k, q in quotas}
    short = n - sum(alloc.values())
    for k, q in sorted(quotas, key=lambda kq: (-(kq[1] - int(kq[1])), kq[0]))[:short]:
        alloc[k] += 1
    rng = random.Random(int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16) % (2 ** 64))
    sample = []
    strata_table = {}
    for k in keys:
        members = strata[k]  # already lexicographically sorted
        take = min(alloc[k], len(members))
        sample += rng.sample(members, take)
        strata_table["%s/%s" % k] = {"frame": len(members), "drawn": take}
    if len(sample) != n:
        raise PipelineError("ERR_SAMPLE_ALLOC", "drew %d != %d" % (len(sample), n))
    return sorted(sample), strata_table, bands


def build(out_dir=None, n=None, seed=None):
    out_dir = out_dir or common.OUT_DIR
    frame, total, instances = load_frame()
    frame_hash = verify_frame(frame, total)          # ERR_FRAME_HASH fail-closed
    denylist = load_denylist()
    sample, strata_table, bands = stratified_draw(frame, denylist, n=n, seed=seed)
    check_frozen_overlap(sample, denylist)           # ERR_FROZEN_OVERLAP (§9.3)

    worklist_path = os.path.join(out_dir, "worklist.jsonl")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with open(worklist_path, "w", encoding="utf-8") as f:
        for urn in sample:
            row = frame[urn]
            f.write(common.canonical_dumps({
                "conceptId": urn,
                "lemma": row["lemma"],
                "pos": row["pos"],
                "wnGloss": row["gloss"],
                "sourceRowSha256": row["sourceRowSha256"],
            }) + "\n")
    with open(__file__, "rb") as f:
        builder_sha = hashlib.sha256(f.read()).hexdigest()
    manifest = {
        "schema": "kv1d-sample-manifest/1",
        "specRef": "docs/next/design/gpt56-draft-pipeline-large-kernel.md r5 §1 (ASM-2474 contract, ASM-2493 values)",
        "frameSha256": frame_hash,
        "frameCount": common.FRAME_COUNT,
        "censusTotal": total,
        "instanceSynsetsExcluded": instances,
        "frozenOverlapDenylist": {"path": "data/lexical-wn31/alignment-kernel-v0.json",
                                  "count": len(denylist)},
        "sampleN": len(sample),
        "sampleSeed": seed or common.SAMPLE_SEED,
        "seedNote": "PINNED MOCK seed; operative seed registered at prereg-freeze (§1); a re-draw is a new experiment id",
        "polysemyBandRule": "max over the synset's lemmas of same-POS frame-synset count; bands mono/2-5/6+ [ASM-2498]",
        "sampleSha256": hashlib.sha256("\n".join(sample).encode("utf-8")).hexdigest(),
        "strata": strata_table,
        "builderSha256": builder_sha,
        "owner": "designer-20 (build); runner-1 (kb-pipeline-runner) operates",
    }
    common.write_json(os.path.join(out_dir, "sample-manifest.json"), manifest)
    return worklist_path, manifest


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--n", type=int, default=None)
    args = ap.parse_args()
    path, manifest = build(out_dir=args.out, n=args.n)
    print("OK frame %d hash %s… sample %d -> %s" % (
        manifest["frameCount"], manifest["frameSha256"][:12], manifest["sampleN"], path))
