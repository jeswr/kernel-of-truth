#!/usr/bin/env python3
"""DDC direction-SELECTION module (docs/next/design/DDC.md §2.2/§2.3/§3).

Builds the per-boundary bases that ddc_surgery consumes, as BasisSpec
dicts. LAW-1 discipline: everything this module hands to the surgery seam
is derived from the MODEL's own activations (uncentred second moments,
admitted model-space alignment directions, complement top-ups) or from
seeded Haar randomness — never from a kernel vector. Kernel content enters
ONLY as calibration TEXT (the pinned corpora rendered upstream); kernel
VECTORS are consumed exclusively by g0_runner/g0_stats, whose outputs
reaching this module are model-space directions u_j in R^d.

Boundary convention (pinned, inputs/ddc-manifest.json surgery block):
L boundaries — l = 0 embedding output; l = 1..L-1 post-residual outputs of
blocks 0..L-2.

Basis conventions:
  * All PCA bases use the UNCENTRED second moment (1/N) X^T X, energy-
    ordered (ASM-1665) — identically in A1/A3/C1/C2/C3 and the A2 top-up;
    the massive-activation direction survives on its own mass and gate
    I-6 logs its energy capture per cell.
  * R1: Haar-random orthonormal Q (QR of seeded Gaussian, sign-fixed),
    seeds {0,1,2} (§3).
  * A2 (§2.3 basis assembly, ASM-1700): admitted directions ordered by
    null-beating strength (TEST score minus t*, descending; ties -> lower
    layer then lower candidate index), QR-orthonormalised in that order;
    A1 top-up projected onto the orthogonal complement, residuals with
    norm < 1e-6 discarded, survivors re-orthonormalised in energy order;
    top-up pool = the FULL d-vector uncentred eigenbasis; exhausting the
    pool below r_l raises ERR_DDC_BASIS_DEFICIENT — the cell fails closed
    as a basis-construction failure, never silently padded, never
    relabelled A1.

numpy-only math; torch used only in the activation-collection helpers.
"""

from __future__ import annotations

import hashlib
import json
import math
import os

import numpy as np

TOPUP_RESIDUAL_MIN = 1e-6   # §2.3 floating-point discard bound (ASM-1700)


def _die(code, msg):
    raise SystemExit("%s: %s" % (code, msg))


def load_corpus_texts(corpus_dir, max_sequences=None):
    """Pinned calibration corpora are directories of .txt (one sequence
    per file) and/or .jsonl ({'text': ...} rows). Deterministic order:
    POSIX relpath sort (the kot-corpus-hash/1 ordering)."""
    if not os.path.isdir(corpus_dir):
        _die("ERR_DDC_CORPUS", "no corpus directory %r" % corpus_dir)
    texts = []
    names = []
    for root, dirs, files in os.walk(corpus_dir):
        dirs.sort()
        for name in sorted(files):
            names.append(os.path.join(root, name))
    for path in sorted(names,
                       key=lambda p: os.path.relpath(p, corpus_dir)
                       .replace(os.sep, "/")):
        if path.endswith(".jsonl"):
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        row = json.loads(line)
                        texts.append(row["text"] if isinstance(row, dict)
                                     else str(row))
        elif path.endswith(".txt"):
            with open(path, encoding="utf-8") as fh:
                texts.append(fh.read())
    if not texts:
        _die("ERR_DDC_CORPUS", "corpus %r has no .txt/.jsonl sequences"
             % corpus_dir)
    if max_sequences:
        texts = texts[:max_sequences]
    return texts


# --------------------------------------------------------------------------
# Activation collection (torch)
# --------------------------------------------------------------------------

def collect_second_moments(model, tok, texts, device="cpu",
                           max_tokens=256, batch_log=None):
    """One fp32 forward pass over the corpus; per-boundary UNCENTRED
    second moments S_l = (1/N) X_l^T X_l over all tokens (ASM-1665).
    Returns (list of L numpy float64 (d,d), n_tokens)."""
    import torch
    m = model.model
    layers = list(m.layers)
    L = len(layers)
    d = m.embed_tokens.weight.shape[1]
    sums = [np.zeros((d, d), dtype=np.float64) for _ in range(L)]
    n_tok = 0
    acts = {}

    def hook(idx):
        def fn(_mod, _inp, out):
            h = out[0] if isinstance(out, tuple) else out
            acts[idx] = h.detach()
        return fn

    handles = [m.embed_tokens.register_forward_hook(hook(0))]
    for b in range(L - 1):                       # post-block outputs 0..L-2
        handles.append(layers[b].register_forward_hook(hook(b + 1)))
    try:
        with torch.no_grad():
            for i, text in enumerate(texts):
                ids = tok.encode(text, add_special_tokens=False)[:max_tokens]
                if not ids:
                    continue
                model(torch.tensor([ids], device=device))
                for l in range(L):
                    x = acts[l][0].to(torch.float64).cpu().numpy()
                    sums[l] += x.T @ x
                n_tok += len(ids)
                if batch_log and (i + 1) % 256 == 0:
                    batch_log("  moments %d/%d" % (i + 1, len(texts)))
    finally:
        for h in handles:
            h.remove()
    if n_tok == 0:
        _die("ERR_DDC_CORPUS", "corpus produced zero tokens")
    return [s / n_tok for s in sums], n_tok


def collect_boundary_activations(model, tok, texts, device="cpu",
                                 max_tokens=256):
    """Per-sequence per-boundary pooled activations for the G0 probe
    pipeline: returns dict {"mean": (n, L, d), "last": (n, L, d)} —
    mean over non-BOS tokens and last-token pooling (FORK-2 variants)."""
    import torch
    m = model.model
    layers = list(m.layers)
    L = len(layers)
    acts = {}

    def hook(idx):
        def fn(_mod, _inp, out):
            h = out[0] if isinstance(out, tuple) else out
            acts[idx] = h.detach()
        return fn

    handles = [m.embed_tokens.register_forward_hook(hook(0))]
    for b in range(L - 1):
        handles.append(layers[b].register_forward_hook(hook(b + 1)))
    mean_rows, last_rows = [], []
    try:
        with torch.no_grad():
            for text in texts:
                ids = tok.encode(text, add_special_tokens=False)[:max_tokens]
                if not ids:
                    ids = [tok.eos_token_id or 0]
                model(torch.tensor([ids], device=device))
                mrow, lrow = [], []
                for l in range(L):
                    x = acts[l][0].to(torch.float64).cpu().numpy()
                    mrow.append(x.mean(axis=0))      # all tokens are
                    lrow.append(x[-1])               # non-BOS (no BOS added)
                mean_rows.append(mrow)
                last_rows.append(lrow)
    finally:
        for h in handles:
            h.remove()
    return {"mean": np.array(mean_rows), "last": np.array(last_rows)}


# --------------------------------------------------------------------------
# Basis constructions (numpy)
# --------------------------------------------------------------------------

def _sign_fix(q):
    """Deterministic sign convention: first nonzero component of each
    column made positive (§2.3 tie-break convention)."""
    q = q.copy()
    for j in range(q.shape[1]):
        col = q[:, j]
        nz = np.nonzero(np.abs(col) > 0)[0]
        if len(nz) and col[nz[0]] < 0:
            q[:, j] = -col
    return q


def pca_full_bases(moments, calibration_corpus):
    """Full d x d uncentred-second-moment eigenbases, energy-ordered
    descending (ASM-1665). Returns a surgery-ready BasisSpec plus the
    per-boundary eigenvalues (for diagnostics/top-up)."""
    bases, eigvals = [], []
    for s in moments:
        w, v = np.linalg.eigh((s + s.T) / 2.0)
        order = np.argsort(w)[::-1]                  # energy descending
        bases.append(_sign_fix(v[:, order]))
        eigvals.append(w[order])
    return {"provenance": "model-activation-basis",
            "bases": bases,
            "meta": {"construction": "uncentred-second-moment PCA, "
                                     "energy-ordered (ASM-1665)",
                     "calibration_corpus": calibration_corpus}}, eigvals


def haar_full_bases(d, n_boundaries, seed):
    """R1: per-boundary Haar-random orthonormal Q = QR of seeded Gaussian
    (§3); sub-seeded per boundary from (seed, boundary) via sha256 so the
    basis set is reproducible independent of numpy call order."""
    bases = []
    for l in range(n_boundaries):
        sub = int(hashlib.sha256(
            ("ddc-r1|%d|%d" % (seed, l)).encode()).hexdigest()[:12], 16)
        rng = np.random.default_rng(sub)
        g = rng.standard_normal((d, d))
        q, r = np.linalg.qr(g)
        q = q * np.sign(np.diag(r))                  # Haar-correct sign fix
        bases.append(q)
    return {"provenance": "haar-random-basis",
            "bases": bases,
            "meta": {"construction": "QR of seeded Gaussian (Haar), "
                                     "sha256 sub-seeds", "seed": seed}}


def a2_assemble(admitted, t_star, topup_spec, rho, d):
    """§2.3 basis assembly (ASM-1700). `admitted`: list of
    {"layer": int, "dir_index": int, "test_score": float, "u": [d floats]}
    (model-space directions from the ddc0 readout — LAW-1: these are the
    model's own directions, selected against kernel geometry upstream).
    `topup_spec`: the A1 (K-static) FULL PCA BasisSpec. Returns a
    surgery-ready BasisSpec with r = ceil(rho * d) columns per boundary."""
    if topup_spec.get("provenance") != "model-activation-basis":
        _die("ERR_DDC_LAW1_TAINT", "A2 top-up must be the model-side "
             "uncentred PCA basis")
    r = int(math.ceil(rho * d))
    n_boundaries = len(topup_spec["bases"])
    by_layer = {}
    for a in admitted:
        by_layer.setdefault(int(a["layer"]), []).append(a)
    bases = []
    aligned_fraction = {}
    for l in range(n_boundaries):
        cands = sorted(by_layer.get(l, []),
                       key=lambda a: (-(a["test_score"] - t_star),
                                      a["layer"], a["dir_index"]))
        cols = []
        for a in cands:
            u = np.asarray(a["u"], dtype=np.float64)
            if u.shape != (d,):
                _die("ERR_DDC_BASIS_SHAPE",
                     "admitted direction layer %d has dim %r != %d"
                     % (l, u.shape, d))
            # QR step: orthogonalise against already-kept columns
            for c in cols:
                u = u - c * float(c @ u)
            nrm = float(np.linalg.norm(u))
            if nrm >= TOPUP_RESIDUAL_MIN:
                cols.append(u / nrm)
        k_aligned = len(cols)
        # complement-projected top-up: FULL d-vector eigenbasis in energy
        # order (ASM-1700 fewer-than-r fail-closed path)
        pool = topup_spec["bases"][l]
        for j in range(pool.shape[1]):
            if len(cols) >= r:
                break
            u = pool[:, j].astype(np.float64).copy()
            for c in cols:
                u = u - c * float(c @ u)
            nrm = float(np.linalg.norm(u))
            if nrm < TOPUP_RESIDUAL_MIN:
                continue                     # discard, disclosed by count
            cols.append(u / nrm)
        if len(cols) < r:
            _die("ERR_DDC_BASIS_DEFICIENT",
                 "boundary %d: %d columns after exhausting the full "
                 "top-up pool (< r=%d) — A2 cell is a basis-construction "
                 "failure (never silently padded, never relabelled A1; "
                 "ASM-1700)" % (l, len(cols), r))
        bases.append(_sign_fix(np.stack(cols, axis=1)))
        aligned_fraction[str(l)] = k_aligned / float(r)
    return {"provenance": "model-activation-basis",
            "bases": bases,
            "meta": {"construction": "A2: null-beating-strength-ordered QR "
                                     "of admitted model-space directions + "
                                     "complement-projected A1 top-up "
                                     "(ASM-1700)",
                     "t_star": t_star,
                     "aligned_budget_fraction": aligned_fraction}}


def energy_capture(basis_cols, direction):
    """Gate I-6 statistic: fraction of the (unit) massive-activation
    direction's energy captured by the kept subspace: ||Q_r^T v||^2."""
    v = np.asarray(direction, dtype=np.float64)
    v = v / max(np.linalg.norm(v), 1e-30)
    proj = basis_cols.T @ v
    return float(proj @ proj)


def massive_activation_directions(moments):
    """Super-weight / massive-activation census helper (§2.2/§2.5,
    ASM-1658): the top-energy eigendirection of each boundary's uncentred
    second moment — the direction whose deletion the I-6 tripwire guards.
    Returned as unit vectors per boundary; the T0 census artifact records
    them alongside the data-free super-weight coordinates."""
    dirs = []
    for s in moments:
        w, v = np.linalg.eigh((s + s.T) / 2.0)
        dirs.append(_sign_fix(v[:, [int(np.argmax(w))]])[:, 0])
    return dirs
