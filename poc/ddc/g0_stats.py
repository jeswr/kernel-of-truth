#!/usr/bin/env python3
"""ddc0 (G0) alignment statistics — the §2.3 mathematics of
docs/next/design/DDC.md, implemented exactly as stipulated
[ASM-1700 alignment/splits/scores, ASM-1701 joint max-stat family,
ASM-1702 admission criteria]. numpy only; no torch, no model — inputs are
the probe-stage arrays, so this module is locally testable at $0.

Inputs (per run_g0):
  H:      (L, n, d) probe representations, one pooling variant — already
          empty-carrier-subtracted, instance-averaged, grand-mean-centred
          (the probe stage does that; §2.3 probe construction).
  H12/H34:(L, n, d) carrier-half variants (criterion 2), same pipeline.
  V:      (n, d) column-centred canonical encoder vectors (kernel side —
          used HERE ONLY; nothing this module returns for surgery carries
          kernel coordinates: admitted directions are model-space u in R^d).
  V_bag:  (n, d) bag-of-primes structure-destroyed encodings (criterion 4).
  splits: {"fit": idx, "sel": idx, "test": idx} (concept-level, seed 0,
          stratified — made by make_splits below).
  mc_pairs: minimal-contrast pairs [(i, j), ...] housed in SEL.

Statistics, verbatim from §2.3:
  * Ridge-CCA: (S_hh+λI)^{-1} S_hv (S_vv+λI)^{-1} S_hv^T a = ρ² a solved
    as the whitened SVD T = (S_hh+λI)^{-1/2} S_hv (S_vv+λI)^{-1/2}
    (economy form in the JOINT ROW SPACE of the data — the unregularised
    problem is rank-deficient at n_F ≪ d; directions outside the row
    space have zero data support and are never candidates). Variates
    normalised aᵀ(S_hh+λI)a = 1; b_j = (S_vv+λI)^{-1} S_hvᵀ a_j / ρ_j;
    one λ on both blocks; grid {1e-4,1e-3,1e-2,1e-1,1}·tr(S_hh)/d;
    leave-one-concept-out selection with the loadings predictor
    v̂_i = Σ_j ρ_j (a_jᵀ h_i) β_j, β_j = V_Fᵀ(H_F a_j)/(n_F−1), ρ_j > 0;
    ties -> the larger λ.
  * Procrustes: thin SVD of M = H_Fᵀ V_F; tested objects are the pairs
    (u_j, w_j, σ_j); σ orders candidates ONLY.
  * Candidates: J = min(64, n_F − 1) per layer per method; deterministic
    sign convention (first nonzero model-side component positive);
    ordering ties -> lower index.
  * Score: signed one-sided Pearson correlation over TEST of
    (H_T u, V_T w).
  * Null (ASM-1701): B seeded global concept→vector permutations
    (seed 1, numpy default_rng single stream), partition membership fixed
    on the model side, FULL pipeline re-run per replicate (per-layer LOO
    λ re-selection included), T_b = max over methods × layers ×
    candidates (× poolings if FORK-2 routes) of the TEST score.
  * Criterion 2: carrier-half refits on FIT, halves' candidates matched
    by maximal kernel-side |cosine|; statistic |cos ∠(u12, u34)|.
  * Criterion 3: signed correlation on the SEL-housed minimal-contrast
    stratum, per-stratum permutation p (B=1000, same seed stream),
    positive sign required.
  * Criterion 4: seeded paired bootstrap (1e3 resamples over TEST
    concepts) of s − s_bag; emitted statistic = the 90% CI lower bound
    (5th percentile, nearest rank).

Emits raw per-candidate fields ONLY (test_score, carrier_half_cos,
minimal_contrast_p, bag_delta_ci90_low) — analysis/ddc0.py recomputes
every gate and admission from these; nothing here is a verdict.
"""

from __future__ import annotations

import hashlib
import math

import numpy as np

RIDGE_MULTS = (1e-4, 1e-3, 1e-2, 1e-1, 1.0)   # §2.3 pinned grid
J_MAX = 64
BAG_RESAMPLES = 1000
MC_PERMS = 1000


def _rng(seed, tag):
    sub = int(hashlib.sha256(("g0|%d|%s" % (seed, tag)).encode())
              .hexdigest()[:12], 16)
    return np.random.default_rng(sub)


def make_splits(concept_ids, classes, seed=0,
                fracs=(0.6, 0.2, 0.2)):
    """Concept-level FIT/SEL/TEST partition, seeded draw stratified by
    record class (§2.3): within each class (ids sorted for determinism),
    a seeded shuffle; per-class ceil-quota fill FIT then SEL then TEST.
    One partition serves every layer, both methods, every replicate."""
    rng = _rng(seed, "split")
    by_class = {}
    for i, cid in enumerate(concept_ids):
        by_class.setdefault(classes[i], []).append((cid, i))
    fit, sel, test = [], [], []
    for cls in sorted(by_class):
        entries = sorted(by_class[cls])
        idx = np.array([i for _cid, i in entries])
        perm = rng.permutation(len(idx))
        idx = idx[perm]
        n = len(idx)
        n_f = int(math.ceil(fracs[0] * n))
        n_s = int(math.ceil(fracs[1] * n))
        fit.extend(idx[:n_f].tolist())
        sel.extend(idx[n_f:n_f + n_s].tolist())
        test.extend(idx[n_f + n_s:].tolist())
    return {"fit": sorted(fit), "sel": sorted(sel), "test": sorted(test)}


def _sign_fix_vec(u, w):
    nz = np.nonzero(np.abs(u) > 0)[0]
    if len(nz) and u[nz[0]] < 0:
        return -u, -w
    return u, w


def _pearson(x, y):
    x = x - x.mean()
    y = y - y.mean()
    nx = float(np.linalg.norm(x))
    ny = float(np.linalg.norm(y))
    if nx <= 0 or ny <= 0:
        return 0.0
    return float(x @ y) / (nx * ny)


# --------------------------------------------------------------------------
# per-layer method fits (reduced coordinates: joint row space)
# --------------------------------------------------------------------------

def _reduce(mat, tol=1e-10):
    """Orthonormal basis of the row space of mat ((m, d) -> (d, k))."""
    _u, s, vt = np.linalg.svd(mat, full_matrices=False)
    k = int((s > tol * (s[0] if len(s) else 1.0)).sum())
    return vt[:max(k, 1)].T


def fit_cca(Hl, V, fit_idx):
    """Ridge-CCA on FIT with LOO λ selection (§2.3, verbatim recipe).
    Returns (candidates, lambda_star): candidates = [(u_d, w_d, rho_j)]
    in descending ρ, u/w in FULL d coordinates."""
    HF = Hl[fit_idx]
    VF = V[fit_idx]
    n_f = len(fit_idx)
    Bh = _reduce(HF)
    Bv = _reduce(VF)
    Hf = HF @ Bh
    Vf = VF @ Bv
    d = Hl.shape[1]
    tr = float((Hf * Hf).sum()) / n_f          # tr(S_hh), basis-invariant
    lam_grid = [m * tr / d for m in RIDGE_MULTS]

    def solve(Hs, Vs, lam):
        nf = Hs.shape[0]
        Shh = Hs.T @ Hs / nf
        Svv = Vs.T @ Vs / nf
        Shv = Hs.T @ Vs / nf
        wh, vh = np.linalg.eigh(Shh + lam * np.eye(Shh.shape[0]))
        wv, vv = np.linalg.eigh(Svv + lam * np.eye(Svv.shape[0]))
        ih = vh @ np.diag(1.0 / np.sqrt(np.maximum(wh, 1e-30))) @ vh.T
        iv = vv @ np.diag(1.0 / np.sqrt(np.maximum(wv, 1e-30))) @ vv.T
        t = ih @ Shv @ iv
        P, sig, Qt = np.linalg.svd(t, full_matrices=False)
        A = ih @ P                              # aᵀ(S_hh+λI)a = 1
        Bmat = iv @ iv @ Shv.T @ A / np.maximum(sig, 1e-30)  # (S_vv+λI)⁻¹...
        return A, Bmat, sig

    # LOO λ selection (loadings predictor, ρ_j > 0 components)
    best_lam, best_err = None, None
    for lam in lam_grid:
        err = 0.0
        for pos in range(n_f):
            keep = np.ones(n_f, dtype=bool)
            keep[pos] = False
            A, _B, sig = solve(Hf[keep], Vf[keep], lam)
            pos_j = sig > 0
            Z = Hf[keep] @ A[:, pos_j]                     # (n_f-1, J)
            beta = Vf[keep].T @ Z / (n_f - 1)              # (kv, J)
            proj = (Hf[pos] @ A[:, pos_j]) * sig[pos_j]
            vhat = beta @ proj
            diff = vhat - Vf[pos]
            err += float(diff @ diff)
        err /= n_f
        if best_err is None or err < best_err - 1e-15:
            best_lam, best_err = lam, err
        elif abs(err - best_err) <= 1e-15:
            best_lam = lam        # ties -> the larger λ (grid ascends)
    A, Bmat, sig = solve(Hf, Vf, best_lam)
    j = min(J_MAX, n_f - 1, A.shape[1])
    cands = []
    for jj in range(j):
        u = Bh @ A[:, jj]
        nrm = float(np.linalg.norm(u))
        u = u / max(nrm, 1e-30)                 # unit-normalised a_j (§2.3)
        w = Bv @ Bmat[:, jj]
        u, w = _sign_fix_vec(u, w)
        cands.append((u, w, float(sig[jj])))
    return cands, best_lam


def fit_procrustes(Hl, V, fit_idx):
    """Orthogonal-Procrustes alignment pairs (u_j, w_j, σ_j) from the thin
    SVD of M = H_Fᵀ V_F (§2.3; the map R* = UWᵀ itself is never tested)."""
    HF = Hl[fit_idx]
    VF = V[fit_idx]
    Bh = _reduce(HF)
    Bv = _reduce(VF)
    M = (HF @ Bh).T @ (VF @ Bv)
    U, sig, Wt = np.linalg.svd(M, full_matrices=False)
    j = min(J_MAX, len(fit_idx) - 1, U.shape[1])
    cands = []
    for jj in range(j):
        u = Bh @ U[:, jj]
        w = Bv @ Wt[jj]
        u, w = _sign_fix_vec(u, w)
        cands.append((u, w, float(sig[jj])))
    return cands, None


METHOD_FITS = {"ridge-cca": fit_cca, "procrustes": fit_procrustes}


def test_scores(cands, Hl, V, test_idx):
    """Signed one-sided TEST-partition Pearson correlation of
    (H_T u, V_T w) per candidate (§2.3 direction score)."""
    HT = Hl[test_idx]
    VT = V[test_idx]
    return [_pearson(HT @ u, VT @ w) for (u, w, _s) in cands]


def run_family(H_by_pool, V, splits, methods=("ridge-cca", "procrustes")):
    """One full pipeline pass: per pooling variant, per layer, per method
    -> candidate list + TEST scores. H_by_pool: {pooling: (L, n, d)}."""
    out = {}
    for pool, H in sorted(H_by_pool.items()):
        L = H.shape[0]
        for l in range(L):
            for m in methods:
                cands, lam = METHOD_FITS[m](H[l], V, splits["fit"])
                scores = test_scores(cands, H[l], V, splits["test"])
                out[(pool, l, m)] = {"cands": cands, "scores": scores,
                                     "lambda": lam}
    return out


_NULL_CTX = {}


def _null_one(args):
    b, perm = args
    H_by_pool = _NULL_CTX["H"]
    V = _NULL_CTX["V"]
    splits = _NULL_CTX["splits"]
    methods = _NULL_CTX["methods"]
    fits = run_family(H_by_pool, V[perm], splits, methods)
    t_max = max((s for cell in fits.values() for s in cell["scores"]),
                default=float("-inf"))
    return b, float(t_max)


def permutation_null(H_by_pool, V, splits, B, seed,
                     methods=("ridge-cca", "procrustes"), log=None,
                     workers=1, done=None, checkpoint=None):
    """ASM-1701: B seeded GLOBAL concept→vector permutations (v-rows
    permuted across all n concepts; partition membership stays with the
    concept on the model side); the FULL pipeline re-runs per replicate;
    T_b = the single maximum TEST score over the whole family.

    Determinism vs parallelism: ALL B permutations are drawn UP FRONT
    from the single pinned stream (seed 1), so the result is byte-
    identical for any worker count/scheduling. `done`: {b: t_b} already-
    computed replicates (checkpoint resume); `checkpoint(b, t)` called
    per finished replicate."""
    n = V.shape[0]
    rng = np.random.default_rng(seed)           # pinned PRNG stream, seed 1
    perms = [rng.permutation(n) for _ in range(B)]
    results = dict(done or {})
    todo = [(b, perms[b]) for b in range(B) if b not in results]
    _NULL_CTX.update({"H": H_by_pool, "V": V, "splits": splits,
                      "methods": methods})
    if workers > 1 and todo:
        import multiprocessing
        with multiprocessing.Pool(workers) as pool:
            for b, t in pool.imap_unordered(_null_one, todo, chunksize=4):
                results[b] = t
                if checkpoint:
                    checkpoint(b, t)
                if log and len(results) % 25 == 0:
                    log("  null replicate %d/%d" % (len(results), B))
    else:
        for item in todo:
            b, t = _null_one(item)
            results[b] = t
            if checkpoint:
                checkpoint(b, t)
            if log and len(results) % 25 == 0:
                log("  null replicate %d/%d" % (len(results), B))
    return [results[b] for b in range(B)]


# --------------------------------------------------------------------------
# admission-criteria raw statistics (criteria 2-4; filters, never FWER)
# --------------------------------------------------------------------------

def carrier_half_cos(cands, H12l, H34l, V, fit_idx, method):
    """Criterion 2 statistic per candidate: refit on the two fixed carrier
    halves; halves' candidates matched by maximal kernel-side |cosine|;
    statistic |cos ∠(u^{(12)}, u^{(34)})|."""
    c12, _ = METHOD_FITS[method](H12l, V, fit_idx)
    c34, _ = METHOD_FITS[method](H34l, V, fit_idx)
    out = []
    for (_u, w, _s) in cands:
        wn = w / max(np.linalg.norm(w), 1e-30)

        def best(cs):
            bi, bc = 0, -1.0
            for i, (_ui, wi, _si) in enumerate(cs):
                c = abs(float(wn @ wi)) / max(np.linalg.norm(wi), 1e-30)
                if c > bc:
                    bi, bc = i, c
            return bi
        if not c12 or not c34:
            out.append(0.0)
            continue
        u12 = c12[best(c12)][0]
        u34 = c34[best(c34)][0]
        cos = abs(float(u12 @ u34)) / (
            max(np.linalg.norm(u12), 1e-30) * max(np.linalg.norm(u34),
                                                  1e-30))
        out.append(cos)
    return out


def minimal_contrast_p(cands, Hl, V, mc_idx, seed):
    """Criterion 3: signed correlation on the SEL-housed minimal-contrast
    stratum with per-stratum permutation p (B=1000, same seed stream);
    p is 1.0 whenever the observed sign is not positive."""
    Hm = Hl[mc_idx]
    Vm = V[mc_idx]
    out = []
    for ci, (u, w, _s) in enumerate(cands):
        x = Hm @ u
        y = Vm @ w
        s_obs = _pearson(x, y)
        if s_obs <= 0:
            out.append(1.0)
            continue
        rng = _rng(seed, "mc|%d" % ci)
        hits = 0
        for _b in range(MC_PERMS):
            s_b = _pearson(x, y[rng.permutation(len(y))])
            if s_b >= s_obs:
                hits += 1
        out.append((1 + hits) / (MC_PERMS + 1.0))
    return out


def bag_delta_ci90_low(cands, Hl, V, V_bag, test_idx, seed):
    """Criterion 4: seeded paired bootstrap (1e3 resamples over TEST
    concepts) of s − s_bag; returns the 90% CI lower bound (5th
    percentile, nearest rank) per candidate."""
    HT = Hl[test_idx]
    VT = V[test_idx]
    BT = V_bag[test_idx]
    n_t = len(test_idx)
    out = []
    for ci, (u, w, _s) in enumerate(cands):
        x = HT @ u
        y = VT @ w
        yb = BT @ w
        rng = _rng(seed, "bag|%d" % ci)
        deltas = []
        for _b in range(BAG_RESAMPLES):
            idx = rng.integers(0, n_t, n_t)
            deltas.append(_pearson(x[idx], y[idx])
                          - _pearson(x[idx], yb[idx]))
        deltas.sort()
        k = max(0, min(BAG_RESAMPLES - 1,
                       int(math.ceil(0.05 * BAG_RESAMPLES)) - 1))
        out.append(float(deltas[k]))
    return out


def run_g0(H_by_pool, H12, H34, V, V_bag, splits, mc_idx, B=1000,
           perm_seed=1, crit_seed=1, family_poolings=("mean",),
           methods=("ridge-cca", "procrustes"), log=None, workers=1,
           null_done=None, null_checkpoint=None):
    """Full observed pipeline + null family. Returns (candidate_rows,
    t_b, per_layer_lambda) where candidate_rows carry exactly the raw
    fields analysis/ddc0.py consumes, plus the model-space direction u
    (for the ddc1 A2 basis; stripped before the analysis input)."""
    fam_H = {p: H_by_pool[p] for p in family_poolings}
    fits = run_family(fam_H, V, splits, methods)
    rows = []
    lambdas = {}
    for (pool, l, m), cell in sorted(fits.items()):
        if pool != family_poolings[0]:
            continue                    # candidates come from the pinned
                                        # pooling; extra poolings enter the
                                        # null family only (§2.3 FORK-2)
        cands = cell["cands"]
        scores = cell["scores"]
        lambdas["%d:%s" % (l, m)] = cell["lambda"]
        chc = carrier_half_cos(cands, H12[l], H34[l], V, splits["fit"], m)
        mcp = minimal_contrast_p(cands, H_by_pool[pool][l], V, mc_idx,
                                 crit_seed)
        bag = bag_delta_ci90_low(cands, H_by_pool[pool][l], V, V_bag,
                                 splits["test"], crit_seed)
        for j, (u, _w, _s) in enumerate(cands):
            rows.append({"layer": l, "method": m, "dir_index": j,
                         "test_score": float(scores[j]),
                         "carrier_half_cos": float(chc[j]),
                         "minimal_contrast_p": float(mcp[j]),
                         "bag_delta_ci90_low": float(bag[j]),
                         "u": [float(x) for x in u]})
        if log:
            log("  observed fits layer %d method %s: %d candidates"
                % (l, m, len(cands)))
    t_b = permutation_null(fam_H, V, splits, B, perm_seed, methods, log,
                           workers=workers, done=null_done,
                           checkpoint=null_checkpoint)
    return rows, t_b, lambdas


def c4_subspace_overlap(ker_bases, c4_bases, r):
    """§8 expected-tie statistic per layer: (1/r) ||P_ker P_C4||_F^2
    between the top-r kernel-corpus and C4-corpus uncentred activation
    subspaces (resolves ASM-1662)."""
    out = {}
    for l, (qk, qc) in enumerate(zip(ker_bases, c4_bases)):
        m = qk[:, :r].T @ qc[:, :r]
        out[str(l)] = float((m * m).sum()) / r
    return out


def template_variance_top_pc(H):
    """FORK-2 diagnostic: top-PC variance fraction of the (n, d) probe-set
    representation at its most template-dominated layer — reported as the
    MAX over layers (conservative: a single dominant direction anywhere is
    surfaced). H: (L, n, d), already grand-mean-centred."""
    worst = 0.0
    for l in range(H.shape[0]):
        x = H[l] - H[l].mean(axis=0)
        s = np.linalg.svd(x, compute_uv=False)
        tot = float((s * s).sum())
        if tot > 0:
            worst = max(worst, float(s[0] * s[0]) / tot)
    return worst
