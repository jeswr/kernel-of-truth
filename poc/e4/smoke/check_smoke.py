#!/usr/bin/env python3
"""Independent E4 smoke assertions (bead kernel-of-truth-73u).

Checks the emitted artifacts, NOT the builder's own bookkeeping:
  - e4-vocab.json shape (EMIT special, 1054 candidate ids, uint16 range,
    authored ids inside the base vocab / synthetic ids appended);
  - train.bin streams: every sequence is either an emission sequence
    (exactly one EMIT, at position -2, followed by a candidate token) or an
    exposure line (no EMIT, exactly one candidate token); tier-2 tokens
    appear NOWHERE; tier-1 tokens never follow EMIT; emission targets are
    train concepts only; seeds differ in order but not multiset;
  - eval.jsonl: every tier-2 concept x 5 glosses present; items end at EMIT;
    seen-heldgloss variants match the holdout manifest;
  - vector tables: .f32 files' sha-256 match the manifest, kernel rows are
    unit-norm float32, shuffled permutations are derangements.

Writes results/smoke-log.txt + results/e4-smoke-meta.json on success.
"""

import hashlib
import json
import os
import sys
from array import array

import numpy as np


def fail(msg):
    raise SystemExit(f"SMOKE FAIL: {msg}")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_sequences(path, eos_id):
    data = array("H")
    with open(path, "rb") as f:
        data.frombytes(f.read())
    seqs, cur = [], []
    for t in data:
        if t == eos_id:
            seqs.append(tuple(cur))
            cur = []
        else:
            cur.append(t)
    if cur:
        fail(f"{path}: trailing tokens without <eos>")
    return seqs


def main():
    e4data, inputs_dir, results_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    log = []

    def ok(msg):
        log.append(f"OK  {msg}")
        print(f"OK  {msg}")

    with open(os.path.join(e4data, "e4-vocab.json")) as f:
        vocab = json.load(f)
    with open(os.path.join(e4data, "meta.json")) as f:
        meta = json.load(f)
    with open(os.path.join(inputs_dir, "holdout-manifest.json")) as f:
        holdout = json.load(f)
    with open(os.path.join(inputs_dir, "vector-tables-manifest.json")) as f:
        vman = json.load(f)

    # ---- vocab ---------------------------------------------------------------
    if vocab["artifact"] != "e4-vocab":
        fail("vocab artifact")
    n_cand = len(vocab["candidateIds"])
    if n_cand != holdout["vocab"]["total"]:
        fail(f"candidate ids {n_cand} != vocab total {holdout['vocab']['total']}")
    if len(vocab["tokens"]) > 65535:
        fail("vocab exceeds uint16")
    base = vocab["baseVocab"]["size"]
    emit_id = vocab["emitId"]
    if emit_id != base:
        fail("EMIT must be the first appended token")
    cids = vocab["conceptTokenIds"]
    for slug, tid in cids.items():
        if slug.startswith("e4-") and tid <= base:
            fail(f"synthetic {slug} not appended")
        if not slug.startswith("e4-") and tid >= base:
            fail(f"authored {slug} outside base vocab")
    ok(f"e4-vocab: {len(vocab['tokens'])} tokens, {n_cand} candidates, EMIT id {emit_id}")

    tier1_ids = {cids[slug_of(c)] for c in holdout["tiers"]["tier1"]["ids"]}
    tier2_ids = {cids[slug_of(c)] for c in holdout["tiers"]["tier2"]["ids"]}
    cand_set = set(vocab["candidateIds"])
    heldout_ids = tier1_ids | tier2_ids
    train_concept_ids = cand_set - heldout_ids

    # ---- train shards ---------------------------------------------------------
    seq_multisets = []
    for seed in meta["args"]["seeds"]:
        path = os.path.join(e4data, f"seed{seed}", "train.bin")
        seqs = read_sequences(path, eos_id=1)
        n_emit, n_expo = 0, 0
        for s in seqs:
            emits = [i for i, t in enumerate(s) if t == emit_id]
            in_seq_t2 = [t for t in s if t in tier2_ids]
            if in_seq_t2:
                fail(f"seed {seed}: tier-2 token {in_seq_t2[0]} in train stream")
            if emits:
                if len(emits) != 1 or emits[0] != len(s) - 2:
                    fail(f"seed {seed}: malformed emission sequence {s}")
                target = s[-1]
                if target not in cand_set:
                    fail(f"seed {seed}: EMIT followed by non-candidate {target}")
                if target in heldout_ids:
                    fail(f"seed {seed}: held-out token {target} supervised after EMIT")
                if target not in train_concept_ids:
                    fail(f"seed {seed}: emission target {target} not a train concept")
                n_emit += 1
            else:
                inline = [t for t in s if t in cand_set]
                if len(inline) != 1:
                    fail(f"seed {seed}: exposure line with {len(inline)} concept tokens")
                n_expo += 1
        ok(f"seed {seed}: {n_emit} emission + {n_expo} exposure sequences, all gates pass")
        # Emission sequences are seed-INDEPENDENT (only order + exposure-line
        # carrier draws vary with the seed).
        seq_multisets.append((sorted(s for s in seqs if emit_id in s),
                              sum(1 for s in seqs if emit_id not in s)))
    if len(seq_multisets) == 2:
        if seq_multisets[0][0] != seq_multisets[1][0]:
            fail("seeds emit different EMISSION sequence multisets")
        if seq_multisets[0][1] != seq_multisets[1][1]:
            fail("seeds emit different exposure-line counts")
        ok("seed 0/1: emission multisets identical; exposure counts match")

    # ---- eval ------------------------------------------------------------------
    items = [json.loads(l) for l in open(os.path.join(e4data, "eval.jsonl"))]
    t2 = {}
    for it in items:
        if it["ids"][-1] != emit_id:
            fail("eval item does not end at EMIT")
        if it["target"] not in cand_set:
            fail("eval target outside candidate set")
        if it["tier"] == "tier2":
            t2.setdefault(it["conceptId"], set()).add(it["variant"])
        if it["tier"] == "seen-heldgloss":
            want = holdout["evalGlossVariant"][it["conceptId"]]
            if it["variant"] != want:
                fail(f"seen-heldgloss variant {it['variant']} != manifest {want}")
        if it["tier"] in ("tier1", "tier2") and it["sharesStructureWithSeen"] is None:
            fail("held-out eval item missing compositional label")
    for c in holdout["tiers"]["tier2"]["ids"]:
        if t2.get(c) != {0, 1, 2, 3, 4}:
            fail(f"tier-2 concept {c} lacks 5 eval glosses")
    ok(f"eval.jsonl: {len(items)} items; tier-2 coverage complete")

    # ---- vector tables -----------------------------------------------------------
    kpath = os.path.join(inputs_dir, vman["kernel"]["file"])
    if sha256_file(kpath) != vman["kernel"]["sha256"]:
        fail("kernel-d512.f32 sha mismatch vs manifest")
    K = np.fromfile(kpath, dtype="<f4").reshape(vman["rows"], vman["D"])
    norms = np.linalg.norm(K.astype(np.float64), axis=1)
    if not np.allclose(norms, 1.0, atol=1e-5):
        fail(f"kernel rows not unit norm (max dev {abs(norms - 1).max():.2e})")
    for r in vman["randomFrozen"]:
        if sha256_file(os.path.join(inputs_dir, r["file"])) != r["sha256"]:
            fail(f"{r['file']} sha mismatch")
    for s in vman["shuffled"]:
        p = s["perm"]
        if sorted(p) != list(range(len(p))) or any(i == v for i, v in enumerate(p)):
            fail(f"shuffled seed {s['seed']} not a derangement")
    ok(f"vector tables verified: kernel {K.shape} unit-norm, "
       f"{len(vman['randomFrozen'])} random tables, {len(vman['shuffled'])} derangements; "
       f"pin {vman['pinnedHash'][:8]}...")

    if meta["counts"]["glossOovRate"] is not None:
        ok(f"gloss OOV rate (mock vocab, mechanics only): {meta['counts']['glossOovRate']:.3f}")

    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, "smoke-log.txt"), "w") as f:
        f.write("E4 data-pipeline smoke (mechanics only, mock e1 vocab)\n")
        f.write("\n".join(log) + "\nPASS\n")
    with open(os.path.join(results_dir, "e4-smoke-meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print("PASS")


def slug_of(concept_id):
    return concept_id.replace("urn:kernel-v0:", "").replace("urn:kernel-e4:", "e4-")


if __name__ == "__main__":
    main()
