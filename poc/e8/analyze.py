#!/usr/bin/env python3
"""E8 statistics battery (CPU, this box; design pin poc/e8/README.md §4;
bead kernel-of-truth-u0x).

    python3 poc/e8/analyze.py poc/e8/results-incoming/<stamp>

Consumes the Modal extraction (e8-extraction.json + signatures-*.npz), the
committed E2 inputs (kernel + baseline RDMs) and the committed E2 re-analysis
RDMs (emb4 covariates), and writes results-e8.json + verdict-e8.md into the
stamp dir.

All rank/partial/permutation primitives are IMPORTED from
poc/e2/runner/e2_runner.py and poc/e2/reanalysis/analyze.py — no forked
implementations. New logic here is only what E2 never needed: the
cross-family correspondence matrix X (masked profile-Spearman), the
kernel-free identification gate G, and the kernel-as-label retrieval
statistic (S4/S5). Nulls: ONE permutation scheme — permute the concept
labels of the tested KERNEL matrix (== shuffled-kernel, since a shuffled
kernel's RDM is exactly P K P^T); target + covariates stay fixed. The
kernel-free gate G permutes the correspondence labels instead (there is no
kernel in G).
"""

from __future__ import annotations

import datetime as _dt
import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
E2_DIR = os.path.join(REPO, "poc", "e2")
sys.path.insert(0, os.path.join(E2_DIR, "runner"))
import e2_runner as r  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "e2_reanalysis", os.path.join(E2_DIR, "reanalysis", "analyze.py"))
re2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(re2)  # mantel / MaskedSpearman / MaskedPartial

SEED = r.SEED                    # 20260707
N_PERM = r.N_PERM                # 10^4 (RDM-level tests)
N_PERM_RETRIEVAL = 2_000         # pinned (README §4): retrieval rebuilds the
                                 # full masked-profile matrix per permutation;
                                 # min p = 1/2001 << the Holm thresholds used
ALPHA_PRIMARY = 0.01
ALPHA_GATE = 0.05
ALPHA_SECONDARY = 0.05           # Holm-corrected over the 5 secondaries
PRIMARY_KERNEL = r.PRIMARY_KERNEL  # jl512
EMB4 = ["glossEmb.minilm", "glossEmb.bge", "explEmb.minilm", "explEmb.bge"]

CRITERION_VERBATIM = (
    "Align kernel geometry to SAE feature dictionaries across >=2 open model families "
    "(projected path, X4 distortion reported); criterion: kernel coordinates predict "
    "cross-model feature correspondence beyond shuffled-kernel and permutation nulls."
)


# ---------------------------------------------------------------------------
# New primitives (unit-tested in poc/e8/test_e8.py)
# ---------------------------------------------------------------------------


def _ranks_after_drop(vals: np.ndarray, base_ranks: np.ndarray, drop: int) -> np.ndarray:
    """Mid-rank ranks of `vals` with element `drop` removed, from precomputed
    ranks of the full vector. Exact for ties: removing x decrements the rank
    of every y > x by 1 and of every remaining y == x by 0.5 (the tie group
    shrinks by one). Verified against brute-force rankdata in test_e8.py."""
    x = vals[drop]
    adj = base_ranks - (vals > x) - 0.5 * (vals == x)
    return np.delete(adj, drop)


def masked_profile_matrix(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """M(c,c') = Spearman(A[c, mask], B[c', mask]), mask = all anchors except
    {c, c'} — self-cells excluded from BOTH profiles so diagonal 1s cannot
    leak identity (design pin §4). For c == c' the mask excludes just {c}.

    Implementation: per-row base ranks with the row's own anchor removed,
    then an exact single-removal rank adjustment per cell (retrieval nulls
    rebuild this matrix per permutation — the naive 2 rankdata calls per cell
    made that ~30x slower; equivalence is unit-tested against brute force)."""
    n = A.shape[0]
    a_vals = [np.delete(A[i], i) for i in range(n)]
    a_rank = [r.rankdata(v) for v in a_vals]
    b_vals = [np.delete(B[j], j) for j in range(n)]
    b_rank = [r.rankdata(v) for v in b_vals]
    out = np.empty((n, n), dtype=np.float64)
    for c in range(n):
        av, ar = a_vals[c], a_rank[c]
        for d in range(n):
            if d == c:
                out[c, d] = r.pearson(ar, b_rank[d])
                continue
            dpos = d - (d > c)   # position of anchor d in row c's reduced vector
            cpos = c - (c > d)   # position of anchor c in row d's reduced vector
            pa = _ranks_after_drop(av, ar, dpos)
            pb = _ranks_after_drop(b_vals[d], b_rank[d], cpos)
            out[c, d] = r.pearson(pa, pb)
    return out


def correspondence(SA: np.ndarray, SB: np.ndarray) -> tuple:
    X = masked_profile_matrix(SA, SB)
    return X, (X + X.T) / 2.0


def identification_gate(X: np.ndarray, n_perm: int, seed: int) -> dict:
    """Kernel-free precondition G: do the two SAE spaces correspond at all?
    Statistic = mean of both-direction top-1 identification accuracy; null =
    permutation of the cross-family concept pairing."""
    n = X.shape[0]
    a2b_hits = X.argmax(axis=1)   # for A-concept c, best B-concept
    b2a_hits = X.argmax(axis=0)   # for B-concept d, best A-concept

    def acc(perm: np.ndarray) -> float:
        inv = np.argsort(perm)
        return 0.5 * ((a2b_hits == perm).mean() + (b2a_hits == inv[np.arange(n)]).mean())

    ident = np.arange(n)
    obs = float(acc(ident))
    rng = np.random.default_rng(seed)
    exceed = int(sum(bool(acc(rng.permutation(n)) >= obs) for _ in range(n_perm)))
    ranks = [int((X[c] >= X[c, c]).sum()) for c in range(n)]  # 1 = best
    return {
        "acc": float(obs),
        "acc_a2b": float((a2b_hits == ident).mean()),
        "acc_b2a": float((b2a_hits == ident).mean()),
        "mean_diag_rank_a2b": float(np.mean(ranks)),
        "chance_acc": 1.0 / n,
        "p": (1.0 + exceed) / (1.0 + n_perm),
        "n_perm": n_perm,
    }


def retrieval_test(S: np.ndarray, K: np.ndarray, n_perm: int, seed: int) -> dict:
    """Kernel-as-label retrieval (A6 use case in miniature): match each SAE
    concept-signature row to a kernel row by masked profile-Spearman; top-1
    accuracy vs the shuffled-kernel null (labels of K permuted, matrix
    rebuilt per permutation — no shortcut, masks move with the labels)."""
    n = S.shape[0]

    def acc_for(Km: np.ndarray) -> float:
        R = masked_profile_matrix(S, Km)
        return float((R.argmax(axis=1) == np.arange(n)).mean())

    obs = acc_for(K)
    rng = np.random.default_rng(seed)
    exceed = 0
    for _ in range(n_perm):
        p = rng.permutation(n)
        if acc_for(K[np.ix_(p, p)]) >= obs:
            exceed += 1
    return {"acc": obs, "chance_acc": 1.0 / n, "p": (1.0 + exceed) / (1.0 + n_perm), "n_perm": n_perm}


def _json_default(o):
    """numpy scalars -> python (json.dump default hook; belt-and-braces —
    stats code returns python floats at source, but a leaked np.bool_/float64
    must not kill a finished analysis)."""
    if isinstance(o, np.generic):
        return o.item()
    raise TypeError(f"not JSON serializable: {type(o).__name__}")


def holm(named_p: dict) -> dict:
    """Holm step-down; returns {name: {p, p_holm, reject_at_0.05}}."""
    items = sorted(named_p.items(), key=lambda kv: kv[1])
    m = len(items)
    out, running = {}, 0.0
    for i, (name, p) in enumerate(items):
        running = max(running, (m - i) * p)
        out[name] = {"p": p, "p_holm": min(1.0, running),
                     "reject_at_0.05": min(1.0, running) < ALPHA_SECONDARY}
    return out


# ---------------------------------------------------------------------------
# The battery (importable; controls in test_e8.py call this directly)
# ---------------------------------------------------------------------------


def full_battery(
    kernels: dict,
    SA: np.ndarray,
    SB: np.ndarray,
    orig3_ods: list,
    emb4_ods: list | None,
    n_perm: int = N_PERM,
    n_perm_retrieval: int = N_PERM_RETRIEVAL,
) -> dict:
    """kernels: {'jl512': KxK sim, ...} (must contain PRIMARY_KERNEL).
    All matrices already restricted to the same analysed item order."""
    n = SA.shape[0]
    full_mask = np.ones(n * (n - 1) // 2, dtype=bool)
    K = kernels[PRIMARY_KERNEL]

    X, X_sym = correspondence(SA, SB)
    gate = identification_gate(X, n_perm, SEED)

    x_od = r.offdiag(X_sym)
    p1 = re2.mantel(K, re2.MaskedSpearman(x_od, full_mask).stat, n_perm)
    p2 = re2.mantel(K, re2.MaskedPartial(orig3_ods, x_od, full_mask).stat, n_perm)

    secondaries = {}
    if emb4_ods is not None:
        secondaries["S1_partial_orig3+emb4_vs_Xsym"] = re2.mantel(
            K, re2.MaskedPartial(orig3_ods + emb4_ods, x_od, full_mask).stat, n_perm)
    for tag, S in (("S2_partial_orig3_vs_S_famA", SA), ("S3_partial_orig3_vs_S_famB", SB)):
        secondaries[tag] = re2.mantel(
            K, re2.MaskedPartial(orig3_ods, r.offdiag(S), full_mask).stat, n_perm)
    secondaries["S4_retrieval_famA"] = retrieval_test(SA, K, n_perm_retrieval, SEED)
    secondaries["S5_retrieval_famB"] = retrieval_test(SB, K, n_perm_retrieval, SEED)
    holm_out = holm({k: v["p"] for k, v in secondaries.items()})

    sensitivity = {
        kv: re2.mantel(kernels[kv], re2.MaskedPartial(orig3_ods, x_od, full_mask).stat, n_perm)
        for kv in kernels if kv != PRIMARY_KERNEL
    }

    gate_pass = bool(gate["p"] < ALPHA_GATE)
    p1_pass = bool(p1["p"] < ALPHA_PRIMARY)
    p2_pass = bool(p2["p"] < ALPHA_PRIMARY)
    if not gate_pass:
        outcome = "PRECONDITION FAIL (no detectable cross-family correspondence; kernel claim untested)"
    elif p1_pass and p2_pass:
        outcome = "PASS (kernel coordinates predict cross-model feature correspondence beyond shuffled-kernel and permutation nulls)"
    elif p1_pass:
        outcome = "generic relatedness detected (P1 passed, P2 failed)"
    else:
        outcome = "NULL (no kernel signal on the correspondence structure)"

    return {
        "n_items": n,
        "gate_G": gate, "P1_spearman_vs_Xsym": p1, "P2_partial_orig3_vs_Xsym": p2,
        "secondaries": secondaries, "holm": holm_out,
        "kernel_variant_sensitivity_P2form": sensitivity,
        "direction_asymmetry": {"acc_a2b": gate["acc_a2b"], "acc_b2a": gate["acc_b2a"]},
        "outcome": outcome,
        "decision_flags": {"gate_pass": gate_pass, "P1_pass": p1_pass, "P2_pass": p2_pass},
    }


# ---------------------------------------------------------------------------
# I/O + verdict
# ---------------------------------------------------------------------------


def load_stamp(stamp_dir: str) -> tuple:
    with open(os.path.join(stamp_dir, "e8-extraction.json")) as f:
        ext = json.load(f)
    with open(os.path.join(HERE, "inputs", "e8-manifest.json")) as f:
        man = json.load(f)
    inp = r.load_inputs(os.path.join(E2_DIR, "inputs"))
    if ext["encoderContentHash"] != inp["items"]["encoderContentHash"]:
        raise SystemExit("ERR_PIN_MISMATCH: extraction encoder hash differs from E2 inputs")
    sigs = {}
    for fam, fdata in ext["families"].items():
        with np.load(os.path.join(stamp_dir, fdata["signature_file"])) as z:
            if list(z["ids"]) != ext["ids"]:
                raise SystemExit(f"ERR_ITEM_ORDER: {fam} signature ids differ from extraction ids")
            sigs[fam] = np.asarray(z["signatures"], dtype=np.float64)
    return ext, man, inp, sigs


def load_emb4(man: dict, keep_ids: list) -> list | None:
    path = os.path.join(REPO, man["reanalysisRdms"]["path"])
    if not os.path.exists(path):
        return None
    with open(path) as f:
        rd = json.load(f)
    sel = [rd["ids"].index(i) for i in keep_ids]
    ods = []
    for name in EMB4:
        key, emb = name.split(".")
        set_name = "gloss" if key == "glossEmb" else "explication"
        m = np.asarray(rd["embedders"][emb]["similarity_by_textset"][set_name], dtype=np.float64)
        ods.append(r.offdiag(m[np.ix_(sel, sel)]))
    return ods


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    stamp_dir = sys.argv[1].rstrip("/")
    ext, man, inp, sigs = load_stamp(stamp_dir)
    mock = bool(ext.get("mock"))
    n_perm = 500 if mock else N_PERM
    n_perm_retr = 100 if mock else N_PERM_RETRIEVAL

    # Analysed set: extraction survivors minus zero-signature items (either family).
    fam_names = list(sigs)
    dead = set()
    for fam in fam_names:
        dead |= set(ext["families"][fam]["zero_signature_ids"])
    keep = [i for i, cid in enumerate(ext["ids"]) if cid not in dead]
    keep_ids = [ext["ids"][i] for i in keep]

    analysis_ids = [it["id"] for it in inp["items"]["items"]]
    sel = [analysis_ids.index(i) for i in keep_ids]
    kernels = {k: v[np.ix_(sel, sel)] for k, v in r.kernel_matrices(inp).items()}
    orig3_ods = [
        r.offdiag(np.asarray(inp[k]["similarity"], dtype=np.float64)[np.ix_(sel, sel)])
        for k in ("word2vec", "wordnet", "gloss")
    ]
    emb4_ods = load_emb4(man, keep_ids)
    SA = r.cosine_sim_matrix(sigs[fam_names[0]][keep])
    SB = r.cosine_sim_matrix(sigs[fam_names[1]][keep])

    print(f"analysed items: {len(keep_ids)} (dropped zero-signature: {sorted(dead) or 'none'})", flush=True)
    res = full_battery(kernels, SA, SB, orig3_ods, emb4_ods, n_perm, n_perm_retr)

    out = {
        "experiment": "E8 kernel<->SAE alignment (docs/poc-design.md E8)",
        "date": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "mock": mock,
        "criterion_verbatim": CRITERION_VERBATIM,
        "bead": "kernel-of-truth-u0x",
        "design_pin": "poc/e8/README.md (fixed before build)",
        "families": {f: ext["families"][f]["spec_pins"] for f in fam_names},
        "family_order_note": f"famA={fam_names[0]}, famB={fam_names[1]}",
        "diagnostics": {f: ext["families"][f]["diagnostics"] for f in fam_names},
        "attrition": {
            "in_vocab_dropped": {f: ext["families"][f]["in_vocab_dropped_words"] for f in fam_names},
            "zero_signature_dropped_ids": sorted(dead),
            "analysed_ids": keep_ids,
        },
        "pins": {
            "encoderContentHash": ext["encoderContentHash"],
            "corpusPin": ext["corpusPin"],
            "manifest_sha256": ext["manifest_sha256"],
            "primary_kernel_variant": PRIMARY_KERNEL,
            "x4_distortion_rdm_spearman": man["stats"]["x4DistortionRdmSpearman"],
        },
        "seed": SEED, "n_perm": n_perm, "n_perm_retrieval": n_perm_retr,
        "alpha_primary": ALPHA_PRIMARY, "alpha_gate": ALPHA_GATE,
        "results": res,
        "outcome": res["outcome"],
    }
    jpath = os.path.join(stamp_dir, "results-e8.json")
    with open(jpath, "w") as f:
        json.dump(out, f, indent=2, default=_json_default)
    write_verdict(stamp_dir, out)
    print(f"\nwrote {jpath}\nOUTCOME: {out['outcome']}")


def write_verdict(stamp_dir: str, out: dict) -> None:
    res = out["results"]
    g, p1, p2 = res["gate_G"], res["P1_spearman_vs_Xsym"], res["P2_partial_orig3_vs_Xsym"]
    L = [
        "# E8 — kernel<->SAE alignment: verdict",
        "",
        f"date: {out['date']}  |  mock: {out['mock']}  |  seed: {out['seed']}  |  "
        f"perms: {out['n_perm']} (retrieval {out['n_perm_retrieval']})  |  kernel: {out['pins']['primary_kernel_variant']}",
        f"encoder: `{out['pins']['encoderContentHash']}`",
        f"families: {out['family_order_note']}",
        "",
        "**Pre-registered criterion (docs/poc-design.md E8, verbatim):**",
        f"> {out['criterion_verbatim']}",
        "",
        f"Projected path: jl512 primary; inherited X4 RDM-Spearman distortion "
        f"{out['pins']['x4_distortion_rdm_spearman']['jl512']:.4f} (8192->512), "
        f"{out['pins']['x4_distortion_rdm_spearman']['jl576']:.4f} (8192->576).",
        "",
        f"## OUTCOME: **{res['outcome']}**",
        "",
        f"- items analysed: {res['n_items']} "
        f"(zero-signature drops: {out['attrition']['zero_signature_dropped_ids'] or 'none'})",
        f"- gate G (kernel-free correspondence): acc {g['acc']:.4f} "
        f"(chance {g['chance_acc']:.4f}; A->B {g['acc_a2b']:.4f}, B->A {g['acc_b2a']:.4f}), p {g['p']:.5f}",
        f"- P1 Spearman(K_jl512, X_sym): rho {p1['rho']:.4f}, p {p1['p']:.5f} "
        f"({'PASS' if res['decision_flags']['P1_pass'] else 'fail'} at 0.01)",
        f"- P2 partial | orig3: rho {p2['rho']:.4f}, p {p2['p']:.5f} "
        f"({'PASS' if res['decision_flags']['P2_pass'] else 'fail'} at 0.01)",
        "",
        "## Secondaries (Holm-corrected)",
        "",
        "| test | stat | p | p_holm | reject@0.05 |",
        "|---|---|---|---|---|",
    ]
    for name, t in res["secondaries"].items():
        stat = t.get("rho", t.get("acc"))
        h = res["holm"][name]
        L.append(f"| {name} | {stat:.4f} | {t['p']:.5f} | {h['p_holm']:.5f} | "
                 f"{'yes' if h['reject_at_0.05'] else 'no'} |")
    L += [
        "",
        "## Sensitivity (descriptive; P2 form, kernel variants)",
        "",
    ]
    for kv, t in res["kernel_variant_sensitivity_P2form"].items():
        L.append(f"- {kv}: rho {t['rho']:.4f}, p {t['p']:.5f}")
    L += [
        "",
        "## Diagnostics",
        "",
    ]
    for f, d in out["diagnostics"].items():
        L.append(f"- {f}: FVU {d['fvu']:.4f}, mean L0 {d['mean_l0']:.1f}, span tokens {d['n_span_tokens']}")
    L += [
        "",
        "Nulls note: shuffled-kernel == Mantel concept-label permutation at the RDM level "
        "(P K P^T); one permutation scheme implements both pre-registered nulls.",
        "Scope: ONE family pair == ONE primary test; a PASS licenses exactly this pair. "
        "Pre-named weaknesses (poc/e8/README.md §6) apply, in particular: the SAE sees the "
        "exponent WORD in synthetic contexts, never the explication.",
    ]
    if out["mock"]:
        L += ["", "**MOCK RUN — pipeline smoke test only; numbers are meaningless by construction.**"]
    with open(os.path.join(stamp_dir, "verdict-e8.md"), "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main())
