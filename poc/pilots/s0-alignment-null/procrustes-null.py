#!/usr/bin/env python3
"""S0 pilot (EXPLORATORY, unregistered): Procrustes alignment-null calibration.

Question it answers (design input for the kernel-introduction-schedule S1
experiment, docs/next/kernel-introduction-schedule.md): if we later claim
"the learned model space contains a subspace alignable to the kernel via an
orthogonal map", how good does that alignment look UNDER THE NULL - i.e.
against targets with no shared structure - as a function of panel size n and
subspace dimension k? Any S1 alignability metric must beat these null bands,
not zero.

Conditions per (n, k) cell, 10 seeds each:
  planted(sigma): Y = row-normalised(K R + sigma*G)  - true shared structure,
                  orthogonal rotation R, Gaussian noise G (per-row unit-scaled)
  null-random   : Y = row-normalised Gaussian         - no shared structure
  null-shuffled : Y = derangement-permuted rows of K R (structure exists but
                  correspondence is wrong - the shuffled-kernel discipline)

Metrics per fit (W = argmin_{W orthogonal} ||K W - Y||_F, closed form via SVD):
  fitR2    : 1 - ||KW - Y||^2 / ||Y||^2      (the naive "alignment quality")
  meancos  : mean_i cos(K_i W, Y_i)           (per-concept match after map)
  gramRSA  : Spearman rho between off-diagonal Gram(K) and Gram(Y)
             (rotation-invariant relational recovery; unaffected by W)

Inputs: vectors-f64.bin (130 x 8192, seeded synthetic panel, pinned encoder
kot-enc-B/1). JL projection to k dims is a seeded Gaussian map (X4-class;
X4 validated 8192->512/576 distortion for this vector family).
$0, CPU-only, deterministic given seeds. NOT registry evidence.
"""
import json
import numpy as np
from pathlib import Path

HERE = Path(__file__).parent
rng_master = np.random.default_rng(20260709)

raw = np.fromfile(HERE / "vectors-f64.bin", dtype="<f8").reshape(130, 8192)
meta = json.loads((HERE / "vectors-meta.json").read_text())
assert meta["n"] == 130 and meta["d"] == 8192

def rownorm(X):
    return X / np.linalg.norm(X, axis=1, keepdims=True)

def procrustes_metrics(K, Y):
    # Orthogonal Procrustes: W = U V^T for K^T Y = U S V^T
    U, S, Vt = np.linalg.svd(K.T @ Y)
    W = U @ Vt
    KW = K @ W
    fit_r2 = 1.0 - np.linalg.norm(KW - Y) ** 2 / np.linalg.norm(Y) ** 2
    meancos = float(np.mean(np.sum(rownorm(KW) * rownorm(Y), axis=1)))
    return float(fit_r2), meancos

def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    return float((ra @ rb) / np.sqrt((ra @ ra) * (rb @ rb)))

def gram_rsa(K, Y):
    gk = (K @ K.T)[np.triu_indices(len(K), 1)]
    gy = (Y @ Y.T)[np.triu_indices(len(Y), 1)]
    return spearman(gk, gy)

def rand_orth(k, rng):
    A = rng.standard_normal((k, k))
    Q, R = np.linalg.qr(A)
    return Q * np.sign(np.diag(R))

def derangement(n, rng):
    while True:
        p = rng.permutation(n)
        if not np.any(p == np.arange(n)):
            return p

N_GRID = [16, 32, 65, 130]
K_GRID = [64, 128, 256, 512]
SIGMAS = [0.0, 0.25, 0.5, 1.0, 2.0]
N_SEEDS = 10

results = []
for n in N_GRID:
    for k in K_GRID:
        cells = {}
        for s in range(N_SEEDS):
            rng = np.random.default_rng(hash((20260709, n, k, s)) % 2**63)
            rows = rng.choice(130, size=n, replace=False)
            P = rng.standard_normal((8192, k)) / np.sqrt(k)  # JL-class projection
            K = rownorm(raw[rows] @ P)
            R = rand_orth(k, rng)
            for sigma in SIGMAS:
                G = rng.standard_normal((n, k))
                G = G / np.linalg.norm(G, axis=1, keepdims=True)
                Y = rownorm(K @ R + sigma * G)
                fit, mc = procrustes_metrics(K, Y)
                cells.setdefault(f"planted_s{sigma}", []).append((fit, mc, gram_rsa(K, Y)))
            Yr = rownorm(rng.standard_normal((n, k)))
            fit, mc = procrustes_metrics(K, Yr)
            cells.setdefault("null_random", []).append((fit, mc, gram_rsa(K, Yr)))
            Ys = (K @ R)[derangement(n, rng)]
            fit, mc = procrustes_metrics(K, Ys)
            cells.setdefault("null_shuffled", []).append((fit, mc, gram_rsa(K, Ys)))
        for cond, vals in cells.items():
            arr = np.array(vals)
            results.append({
                "n": n, "k": k, "condition": cond, "seeds": N_SEEDS,
                "fitR2_mean": round(float(arr[:, 0].mean()), 4),
                "fitR2_sd": round(float(arr[:, 0].std(ddof=1)), 4),
                "meancos_mean": round(float(arr[:, 1].mean()), 4),
                "meancos_sd": round(float(arr[:, 1].std(ddof=1)), 4),
                "gramRSA_mean": round(float(arr[:, 2].mean()), 4),
                "gramRSA_sd": round(float(arr[:, 2].std(ddof=1)), 4),
            })

out = {
    "pilot": "s0-alignment-null", "status": "EXPLORATORY-UNREGISTERED",
    "date": "2026-07-09", "encoder_pin": meta["algorithmVersion"],
    "panel": {"n": 130, "d": 8192, "seedPrefix": meta["seedPrefix"]},
    "grid": {"n": N_GRID, "k": K_GRID, "sigmas": SIGMAS, "seeds": N_SEEDS},
    "results": results,
}
(HERE / "s0-results.json").write_text(json.dumps(out, indent=2))

# console digest: the design-relevant comparison
print(f"{'n':>4} {'k':>4} {'condition':>14} {'fitR2':>8} {'meancos':>8} {'gramRSA':>8}")
for r in results:
    if r["condition"] in ("planted_s0.5", "null_random", "null_shuffled"):
        print(f"{r['n']:>4} {r['k']:>4} {r['condition']:>14} "
              f"{r['fitR2_mean']:>8.3f} {r['meancos_mean']:>8.3f} {r['gramRSA_mean']:>8.3f}")
