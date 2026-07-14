#!/usr/bin/env python3
"""R4 offline replay — M_oracle / M_kernel / M_emb pin simulation on the COMMITTED
GLM-5.2 probe fingerprints (poc/glm52-probe/results/stats/f000..f023).

Spec anchors:
  - poc/glm52-probe/interpretation-fable.md §2 R4 (the governing replay spec):
    oracle per-prompt pin vs global-hot pin -> M_oracle; kernel-concept pin
    (train-split concept histograms, held-out prompts, leave-one-out within
    concept groups) vs the STRONGER of global-hot and an embedding-cluster pin
    (off-the-shelf sentence embedding, CPU) -> M_kernel; miss-bytes approximated
    as unpinned-expert usage mass x expert bytes; static (no LRU dynamics).
  - docs/next/design/glm52-followup-experiment.md §3.1 (ASM-2013): quantity
    definitions; M_kernel margin 10%; M_oracle margin 15%.
  - docs/next/design/glm52-expert-drop.md §2.1 item 3 / §3.1 items 1-3 [R4]:
    mean-of-L1-normalized histogram construction, descending rank with
    ascending-(layer,expert) tie-break, MiniLM-L6-v2 embedding + own-impl
    k-means k=8 seed 20260724 n_init=10 (borrowed here for comparability;
    the freeze-grade house-DRBG k-means is NOT reproduced -- deviation noted
    in output).

ANALYSIS ONLY: this script fires no branch classifier and freezes nothing.
CPU-only, deterministic given the committed bytes + the pinned ONNX artifact.

Matched RAM budget: the probe's realized pin store (committed .out files) grew
from 522 experts (9.9 GB) to a steady 1048 experts (19.8 GB, the RAM_GB auto
cap ~20 GB) over the 24 runs. PRIMARY budget B=1048 pinned (layer,expert)
cells; sweep over {262, 524, 786, 1048, 1572, 2096} reported as robustness.
Uniform per-expert bytes (19.8 GB / 1048 ~ 18.9 MB) => relative miss-BYTE
reductions == relative miss-MASS reductions (STIPULATED-not-MEASURED: uniform
expert shard size; not verified against model shards, which are not on this box).
"""
import json, math, os, random, sys, unicodedata, hashlib
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.dirname(HERE)
STATS = os.path.join(PROBE, "results", "stats")
SEED_PERM = 20260712          # same seed family as analyze_routing_v2.py
KMEANS_SEED = 20260724        # design §3.1 item 2 seed (spec-borrowed)
NPERM = 10000
BUDGET_PRIMARY = 1048         # steady-state realized pin store (13/24 runs)
BUDGET_SWEEP = [262, 524, 786, 1048, 1572, 2096]

# ---------------------------------------------------------------- fingerprints
# DATA-INTEGRITY FINDING (MEASURED this run): the committed .stats files are
# SESSION-CUMULATIVE usage dumps, not per-prompt fingerprints — per-cell counts
# are monotone non-decreasing across f000..f023 (0/328,193 violations), totals
# grow 111,904 -> 371,336 (~11.5k/prompt), and f000 already contains the 99,752
# pre-P3 selections recorded in its [USAGE] line. Per-prompt fingerprints are
# recovered EXACTLY by first-differencing: d_N = f_N - f_(N-1), N = 1..23.
# f000's own fingerprint is NOT recoverable from committed bytes (its pre-P3
# baseline per-cell state was not committed) -> f000 is DROPPED; n = 23,
# concept break.shatter reduced to n=2. Consequence flagged for the record:
# every committed analysis that read the raw .stats as per-prompt fingerprints
# (analyze_routing.py, analyze_routing_v2.py) ran on cumulative histograms —
# adjacent prompts share almost all mass by construction, and within-concept
# prompts are ADJACENT blocks in run order, so concept structure and run-order
# adjacency are confounded there; this replay re-tests structure on the
# differenced data below.
manifest = json.load(open(os.path.join(STATS, "manifest.json")))
def _load(path):
    fp = {}
    for ln in open(path):
        p = ln.split()
        if len(p) >= 3:
            try:
                fp[(int(p[0]), int(p[1]))] = float(p[2])
            except ValueError:
                pass
    return fp

cum = [_load(os.path.join(STATS, os.path.basename(m["stats"]))) for m in manifest]
viol = sum(1 for i in range(1, len(cum)) for k, v in cum[i - 1].items()
           if cum[i].get(k, 0) < v)
assert viol == 0, f"cumulative monotonicity violated in {viol} cells"
prompts, concepts, senses, hists, fids = [], [], [], [], []
for i in range(1, len(cum)):
    d = {k: cum[i][k] - cum[i - 1].get(k, 0.0) for k in cum[i]
         if cum[i][k] - cum[i - 1].get(k, 0.0) > 0}
    m = manifest[i]
    prompts.append(m["prompt"]); concepts.append(m["concept"])
    senses.append(m.get("sense_group", "none")); hists.append(d)
    fids.append(f"f{i:03d}")
N = len(hists)
assert N == 23, f"expected 23 differenced fingerprints, got {N}"

keys = sorted(set().union(*[set(h) for h in hists]))   # ever-active keyspace
K = len(keys)
key_index = {k: i for i, k in enumerate(keys)}

RAW = np.zeros((N, K))
for i, h in enumerate(hists):
    for k, v in h.items():
        RAW[i, key_index[k]] = v
L1 = RAW / RAW.sum(axis=1, keepdims=True)              # x_f, §2.1 item 3

# tie-break: descending score, ties -> ascending (layer, expert) [R2: ASM-2344]
# implement via lexsort on (-score, layer, expert)
KEYARR = np.array(keys)  # (K,2)

def top_cells(score, B):
    order = np.lexsort((KEYARR[:, 1], KEYARR[:, 0], -score))
    return order[:B]

def miss_frac(i, pin_idx):
    """unpinned usage mass fraction of prompt i (uniform expert bytes =>
    relative miss-bytes == relative miss-mass)."""
    total = RAW[i].sum()
    pinned = RAW[i][pin_idx].sum()
    return float((total - pinned) / total)

concept_members = defaultdict(list)
for i, c in enumerate(concepts):
    concept_members[c].append(i)
concept_list = sorted(concept_members)                  # 8 concepts

# --------------------------------------- concept structure on DIFFERENCED data
# v2-style within/across cosine + 10k random label shuffles (seed 20260712),
# raw and mean-centred — context for whether the committed v2 separation
# (within 0.912 / across -0.074, p=0.0001, computed on CUMULATIVE histograms)
# survives once the cumulation artifact is removed.
def _structure_test(V):
    sim = V @ V.T / (np.linalg.norm(V, axis=1)[:, None] * np.linalg.norm(V, axis=1)[None, :])
    def wa(lbls):
        w = [sim[i][j] for i in range(N) for j in range(i + 1, N) if lbls[i] == lbls[j]]
        a = [sim[i][j] for i in range(N) for j in range(i + 1, N) if lbls[i] != lbls[j]]
        return float(np.mean(w)), float(np.mean(a)), float(np.mean(w) - np.mean(a))
    w, a, obs = wa(concepts)
    rnd = random.Random(SEED_PERM); cur = list(concepts); ge = 0
    for _ in range(NPERM):
        rnd.shuffle(cur)
        if wa(cur)[2] >= obs:
            ge += 1
    return {"within": round(w, 4), "across": round(a, 4), "delta": round(obs, 4),
            "perm_p_10k": round((ge + 1) / (NPERM + 1), 5)}

structure = {
    "raw_cosine": _structure_test(L1),
    "mean_centered": _structure_test(L1 - L1.mean(axis=0, keepdims=True)),
}

# ---------------------------------------------------------------- embeddings
def embed_prompts(texts):
    from tokenizers import Tokenizer
    import onnxruntime as ort
    tok = Tokenizer.from_file(os.path.join(HERE, "minilm", "tokenizer.json"))
    tok.enable_padding(); tok.enable_truncation(max_length=256)
    # design §3.1 item 1 text rule: NFC, collapse internal whitespace, strip,
    # NO case-folding
    norm = [" ".join(unicodedata.normalize("NFC", t).split()).strip() for t in texts]
    enc = tok.encode_batch(norm)
    ids = np.array([e.ids for e in enc], dtype=np.int64)
    att = np.array([e.attention_mask for e in enc], dtype=np.int64)
    sess = ort.InferenceSession(os.path.join(HERE, "minilm", "model.onnx"),
                                providers=["CPUExecutionProvider"])
    feeds = {"input_ids": ids, "attention_mask": att}
    if any(x.name == "token_type_ids" for x in sess.get_inputs()):
        feeds["token_type_ids"] = np.zeros_like(ids)
    out = sess.run(None, feeds)[0]                      # (N, T, 384)
    mask = att[:, :, None].astype(np.float64)
    emb = (out * mask).sum(axis=1) / mask.sum(axis=1)   # mean pool
    emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)
    return emb.astype(np.float64)

def kmeans8(X):
    """own-impl k-means to the design §3.1 item 2 spec SHAPE (kmeans++, n_init=10,
    float64, squared-Euclidean on L2-normalized vectors, assignment ties -> lowest
    centroid index, empty cluster reseeded with largest-D2 point, convergence =
    assignments unchanged, cap 300, lowest inertia wins, tie -> lowest init idx).
    DEVIATION from freeze-grade spec: stdlib random.Random(f"kmeans:{seed}:{r}")
    stream in place of the house SHA-256 DRBG (replay-grade, disclosed)."""
    n, k = len(X), 8
    best = None
    for r in range(10):
        rnd = random.Random(f"kmeans:{KMEANS_SEED}:{r}")
        centers = [X[rnd.randrange(n)]]
        while len(centers) < k:
            d2 = np.min([np.sum((X - c) ** 2, axis=1) for c in centers], axis=0)
            cum = np.cumsum(d2) / d2.sum()
            u = rnd.random()
            centers.append(X[int(np.searchsorted(cum, u, side="right"))])
        C = np.array(centers)
        assign = None
        for _ in range(300):
            d2 = ((X[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)
            new_assign = np.argmin(d2, axis=1)          # argmin -> lowest index on ties
            for j in range(k):                           # empty-cluster reseed
                if not np.any(new_assign == j):
                    dd = d2[np.arange(n), new_assign]
                    p = int(np.argmax(dd))               # tie -> lowest index
                    new_assign[p] = j
            if assign is not None and np.array_equal(new_assign, assign):
                break
            assign = new_assign
            for j in range(k):
                mem = X[assign == j]
                c = mem.mean(axis=0)
                C[j] = c / np.linalg.norm(c)
        inertia = float(((X - C[assign]) ** 2).sum())
        if best is None or inertia < best[0]:
            best = (inertia, assign.copy(), C.copy(), r)
    return best

emb = embed_prompts(prompts)
inertia, cluster, centroids, init_r = kmeans8(emb)
cluster_members = defaultdict(list)
for i, c in enumerate(cluster):
    cluster_members[int(c)].append(i)

def adjusted_rand(a, b):
    n = len(a)
    ct = defaultdict(int)
    for x, y in zip(a, b):
        ct[(x, y)] += 1
    A = defaultdict(int); B = defaultdict(int)
    for (x, y), v in ct.items():
        A[x] += v; B[y] += v
    comb = lambda m: m * (m - 1) / 2
    sum_ij = sum(comb(v) for v in ct.values())
    sum_a = sum(comb(v) for v in A.values())
    sum_b = sum(comb(v) for v in B.values())
    exp = sum_a * sum_b / comb(n)
    mx = (sum_a + sum_b) / 2
    return (sum_ij - exp) / (mx - exp) if mx != exp else 1.0

ari = adjusted_rand([concepts[i] for i in range(N)], list(map(int, cluster)))

# ---------------------------------------------------------------- pin policies
def policy_miss(B):
    rows = []
    emb_fallbacks = 0
    for i in range(N):
        others = [j for j in range(N) if j != i]
        # oracle: prompt's own trace
        m_orc = miss_frac(i, top_cells(L1[i], B))
        # global-hot: mean of L1-normalized histograms of the other 23 (LOO;
        # note the probe's REALIZED .coli_usage pin accumulated self-usage --
        # a leaky object; the held-out form is used here per ASM-2013)
        m_gh = miss_frac(i, top_cells(L1[others].mean(axis=0), B))
        # kernel-concept: mean over the concept's OTHER members (LOO, n=2)
        mates = [j for j in concept_members[concepts[i]] if j != i]
        m_ker = miss_frac(i, top_cells(L1[mates].mean(axis=0), B))
        # embedding-cluster: realized k-means cluster, LOO histogram
        cmates = [j for j in cluster_members[int(cluster[i])] if j != i]
        if cmates:
            m_emb = miss_frac(i, top_cells(L1[cmates].mean(axis=0), B))
        else:
            m_emb = m_gh; emb_fallbacks += 1
        rows.append(dict(fid=fids[i], concept=concepts[i], oracle=m_orc,
                         global_hot=m_gh, kernel=m_ker, emb=m_emb))
    return rows, emb_fallbacks

def rel_red(rows, num, den):
    return [1.0 - r[num] / r[den] for r in rows]

def med(x): return float(np.median(x))

def cluster_signflip_p(per_prompt_diff):
    """exact 2^8 sign-flip enumeration on concept-cluster mean differences,
    one-sided (positive = kernel better). Matches the design's exact-256-flip
    inference shape (ASM-2348); p floor = 1/256."""
    cmeans = np.array([np.mean([per_prompt_diff[i] for i in concept_members[c]])
                       for c in concept_list])
    obs = cmeans.mean()
    ge = 0; total = 2 ** len(cmeans)
    for mask in range(total):
        s = np.array([1 if (mask >> b) & 1 else -1 for b in range(len(cmeans))])
        if (cmeans * s).mean() >= obs - 1e-15:
            ge += 1
    return obs, ge / total

def prompt_signflip_p(per_prompt_diff, nperm=NPERM):
    """10k random sign-flips at prompt level (secondary; ignores clustering)."""
    d = np.array(per_prompt_diff); obs = d.mean()
    rnd = random.Random(SEED_PERM); ge = 0
    for _ in range(nperm):
        s = np.array([1 if rnd.random() < 0.5 else -1 for _ in range(len(d))])
        if (d * s).mean() >= obs - 1e-15:
            ge += 1
    return obs, (ge + 1) / (nperm + 1)

# ---------------------------------------------------------------- run
out = {
    "spec": "interpretation-fable.md §2 R4; ASM-2013 quantities; analysis-only replay",
    "data_integrity_finding": (
        "committed .stats files are SESSION-CUMULATIVE usage dumps (per-cell "
        "monotone across f000..f023, 0/328193 violations; totals 111904->371336; "
        "f000 contains the 99752 pre-P3 selections). Per-prompt fingerprints "
        "recovered exactly by first-differencing; f000 dropped (baseline not "
        "committed) -> n=23, break.shatter n=2. All committed analyses that read "
        ".stats as per-prompt fingerprints (analyze_routing.py, _v2.py, the "
        "pinned routing-analysis-v2.json numbers) ran on cumulative histograms; "
        "within-concept prompts are adjacent in run order, so concept structure "
        "and adjacency were confounded there. MEASURED: this run."),
    "structure_on_differenced_fingerprints": structure,
    "n_prompts": N, "keyspace_cells": K,
    "budget_primary_cells": BUDGET_PRIMARY,
    "budget_note": ("realized probe pin store grew 522->1048 experts (9.9->19.8GB) "
                    "across the 24 fresh-process runs; 1048 (13/24 runs, the ~20GB "
                    "RAM_GB auto cap) taken as the matched budget; sweep reported"),
    "uniform_expert_bytes": "STIPULATED-not-MEASURED (19.8GB/1048~18.9MB int4; shards not on box)",
    "static_replay_no_LRU": "STIPULATED approximation per interpretation-fable §2 R4",
    "embedding": {
        "model": "sentence-transformers/all-MiniLM-L6-v2 (ONNX runtime realization)",
        "model_sha256": hashlib.sha256(open(os.path.join(HERE, "minilm", "model.onnx"), "rb").read()).hexdigest(),
        "tokenizer_sha256": hashlib.sha256(open(os.path.join(HERE, "minilm", "tokenizer.json"), "rb").read()).hexdigest(),
        "deviation": ("ONNX artifact, not the design §3.1 freeze-pinned safetensors; "
                      "k-means RNG = stdlib MT streams, not the house SHA-256 DRBG. "
                      "Replay-grade, not freeze-grade."),
        "kmeans": {"k": 8, "seed": KMEANS_SEED, "n_init": 10, "winning_init": int(init_r),
                   "inertia": inertia,
                   "cluster_sizes": sorted(len(v) for v in cluster_members.values()),
                   "assignment": {fids[i]: int(cluster[i]) for i in range(N)},
                   "ari_vs_concept_partition": round(float(ari), 4)},
    },
    "budgets": {},
}

for B in BUDGET_SWEEP:
    rows, fb = policy_miss(B)
    rr_orc = rel_red(rows, "oracle", "global_hot")
    rr_ker_gh = rel_red(rows, "kernel", "global_hot")
    rr_emb_gh = rel_red(rows, "emb", "global_hot")
    med_miss = {p: med([r[p] for r in rows]) for p in ("oracle", "global_hot", "kernel", "emb")}
    # stronger deflator = lower median miss-frac (policy-level, ASM-2013 reading)
    stronger = "emb" if med_miss["emb"] < med_miss["global_hot"] else "global_hot"
    rr_ker_str = rel_red(rows, "kernel", stronger)
    # kernel-specificity contrast: per-prompt miss difference emb - kernel
    d_ke = [r["emb"] - r["kernel"] for r in rows]
    obs_c, p_c = cluster_signflip_p(d_ke)
    obs_p, p_p = prompt_signflip_p(d_ke)
    d_og = [r["global_hot"] - r["oracle"] for r in rows]
    obs_oc, p_oc = cluster_signflip_p(d_og)
    d_kg = [r["global_hot"] - r["kernel"] for r in rows]
    obs_kg, p_kg = cluster_signflip_p(d_kg)
    out["budgets"][str(B)] = {
        "emb_singleton_fallbacks": fb,
        "median_miss_frac": {k: round(v, 4) for k, v in med_miss.items()},
        "M_oracle_median_relred_vs_globalhot": round(med(rr_orc), 4),
        "M_oracle_mean": round(float(np.mean(rr_orc)), 4),
        "M_oracle_clusterflip_p": round(p_oc, 5),
        "stronger_deflator": stronger,
        "M_kernel_median_relred_vs_stronger": round(med(rr_ker_str), 4),
        "M_kernel_median_relred_vs_globalhot": round(med(rr_ker_gh), 4),
        "kernel_vs_globalhot_clusterflip_p": round(p_kg, 5),
        "M_emb_median_relred_vs_globalhot": round(med(rr_emb_gh), 4),
        "kernel_vs_emb": {
            "median_paired_missfrac_diff_emb_minus_kernel": round(med(d_ke), 5),
            "mean_diff": round(float(np.mean(d_ke)), 5),
            "prompts_kernel_better": int(sum(1 for d in d_ke if d > 0)),
            "clusterflip_exact256_p_onesided": round(p_c, 5),
            "promptflip_10k_p_onesided": round(p_p, 5),
        },
        "per_prompt": [{**{k: (round(v, 4) if isinstance(v, float) else v)
                           for k, v in r.items()}} for r in rows] if B == BUDGET_PRIMARY else None,
    }

json.dump(out, open(os.path.join(HERE, "r4-replay.json"), "w"), indent=2)
print(json.dumps({k: v for k, v in out.items() if k != "budgets"}, indent=2))
for B in BUDGET_SWEEP:
    b = out["budgets"][str(B)]
    print(f"B={B:5d} | M_oracle={b['M_oracle_median_relred_vs_globalhot']:+.3f} "
          f"| M_emb={b['M_emb_median_relred_vs_globalhot']:+.3f} "
          f"| M_kernel(vs {b['stronger_deflator']})={b['M_kernel_median_relred_vs_stronger']:+.3f} "
          f"| ker-vs-emb p256={b['kernel_vs_emb']['clusterflip_exact256_p_onesided']} "
          f"(kernel better on {b['kernel_vs_emb']['prompts_kernel_better']}/{N})")
