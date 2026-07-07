#!/usr/bin/env python3
"""E8 extension-2 statistics: at-scale geometry, 1,054 concepts
(pre-registration: poc/e8/README.md §Extension 2, fixed before any ext-2
code, encode, or download).

    python3 poc/e8/analyze_scale.py poc/e8/results-incoming/<stamp>-scale-modal

Consumes the Modal extraction (within-family gloss-signature RDMs + cov2
gloss-embedding RDMs) and the committed TS-built kernel RDM binaries
(poc/e8/scale/out, sha-asserted against e8-manifest-scale.json). Primitives
are imported from analyze.py (which imports the E2 machinery) — analyze.py's
bytes stay as committed. Scale battery per the pre-registration:

  gate G at 10^4 label permutations; P1 + P2' (partial | cov2) + S2'/S3'
  Mantel tests at 2,000 permutations (min p 5e-4); Holm over {S2', S3'};
  full-D + jl576 sensitivity; retrieval DESCRIPTIVE only (top-1 acc vs 1/n).

Decision per pair: PASS iff gate + P1 + P2' all pass; "gloss-surface
semantics not excluded" iff P1 passes and P2' fails; PRECONDITION FAIL iff
gate fails; else NULL. Headline: the at-scale claim holds iff the
(gpt2, pythia-160m) pair — the n=51 PASS — passes at n~1054.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import analyze as e8  # noqa: E402

r = e8.r
re2 = e8.re2
MANIFEST = os.path.join(HERE, "inputs", "e8-manifest-scale.json")


def sha256_file(path: str) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_kernel_rdms(man: dict, n_expect: int) -> dict:
    out = {}
    for name, pin in man["kernelRdmScale"]["rdms"].items():
        path = os.path.join(HERE, pin["file"])  # pin paths are e8-relative (scale/out/...)
        got = sha256_file(path)
        if got != pin["sha256"]:
            raise SystemExit(f"ERR_PIN_MISMATCH: {pin['file']} sha {got[:12]}… != pinned")
        m = np.fromfile(path, dtype=np.float32).astype(np.float64)
        n = int(round(len(m) ** 0.5))
        if n * n != len(m) or n != n_expect:
            raise SystemExit(f"ERR_PIN_MISMATCH: {pin['file']} is {n}x{n}, expected {n_expect}")
        out[name] = m.reshape(n, n)
    if e8.PRIMARY_KERNEL not in out:
        raise SystemExit(f"ERR_PIN_MISMATCH: kernel RDMs lack primary variant {e8.PRIMARY_KERNEL}")
    return out


def battery_scale(kernels: dict, SA: np.ndarray, SB: np.ndarray, cov2_ods: list,
                  n_perm_mantel: int, n_perm_gate: int) -> dict:
    n = SA.shape[0]
    full_mask = np.ones(n * (n - 1) // 2, dtype=bool)
    K = kernels[e8.PRIMARY_KERNEL]

    X, X_sym = e8.correspondence(SA, SB)
    gate = e8.identification_gate(X, n_perm_gate, e8.SEED)
    x_od = r.offdiag(X_sym)

    p1 = re2.mantel(K, re2.MaskedSpearman(x_od, full_mask).stat, n_perm_mantel)
    p2p = re2.mantel(K, re2.MaskedPartial(cov2_ods, x_od, full_mask).stat, n_perm_mantel)

    secondaries = {
        "S2p_partial_cov2_vs_S_famA": re2.mantel(
            K, re2.MaskedPartial(cov2_ods, r.offdiag(SA), full_mask).stat, n_perm_mantel),
        "S3p_partial_cov2_vs_S_famB": re2.mantel(
            K, re2.MaskedPartial(cov2_ods, r.offdiag(SB), full_mask).stat, n_perm_mantel),
    }
    holm_out = e8.holm({k: v["p"] for k, v in secondaries.items()})

    sensitivity = {
        kv: re2.mantel(kernels[kv], re2.MaskedPartial(cov2_ods, x_od, full_mask).stat, n_perm_mantel)
        for kv in kernels if kv != e8.PRIMARY_KERNEL
    }

    # retrieval: DESCRIPTIVE only at scale (pre-registered demotion)
    retrieval = {}
    for tag, S in (("famA", SA), ("famB", SB)):
        R = e8.masked_profile_matrix(S, K)
        retrieval[tag] = {"acc": float((R.argmax(axis=1) == np.arange(n)).mean()),
                          "chance_acc": 1.0 / n, "note": "descriptive; no permutation null at scale"}

    gate_pass = bool(gate["p"] < e8.ALPHA_GATE)
    p1_pass = bool(p1["p"] < e8.ALPHA_PRIMARY)
    p2_pass = bool(p2p["p"] < e8.ALPHA_PRIMARY)
    if not gate_pass:
        outcome = "PRECONDITION FAIL (no detectable cross-family correspondence; kernel claim untested)"
    elif p1_pass and p2_pass:
        outcome = "PASS (kernel predicts cross-model correspondence beyond shuffled-kernel/permutation nulls and gloss-embedding covariates)"
    elif p1_pass:
        outcome = "gloss-surface semantics not excluded (P1 passed, P2' failed)"
    else:
        outcome = "NULL (no kernel signal on the correspondence structure)"
    return {
        "n_items": n, "gate_G": gate,
        "P1_spearman_vs_Xsym": p1, "P2p_partial_cov2_vs_Xsym": p2p,
        "secondaries": secondaries, "holm": holm_out,
        "kernel_variant_sensitivity_P2pform": sensitivity,
        "retrieval_descriptive": retrieval,
        "direction_asymmetry": {"acc_a2b": gate["acc_a2b"], "acc_b2a": gate["acc_b2a"]},
        "outcome": outcome,
        "decision_flags": {"gate_pass": gate_pass, "P1_pass": p1_pass, "P2p_pass": p2_pass},
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    stamp_dir = sys.argv[1].rstrip("/")
    with open(MANIFEST) as f:
        man = json.load(f)
    with open(os.path.join(stamp_dir, "e8-scale-extraction.json")) as f:
        ext = json.load(f)
    mock = bool(ext.get("mock"))
    n_perm_mantel = 300 if mock else man["stats"]["nPermMantel"]
    n_perm_gate = 1000 if mock else man["stats"]["nPermGate"]

    if ext["encoderContentHash"] != man["encoderContentHash"]:
        raise SystemExit("ERR_PIN_MISMATCH: extraction encoder hash differs from scale manifest")
    if ext["glossHash"] != man["glossHash"]:
        raise SystemExit("ERR_PIN_MISMATCH: extraction gloss hash differs from scale manifest")

    n_ext = ext["n_concepts"]
    ids = man["ids"][:n_ext]  # mock --limit runs on a prefix; assert below
    if mock and n_ext < man["n"]:
        pass  # prefix semantics asserted via per-file id checks
    elif n_ext != man["n"]:
        raise SystemExit(f"ERR_PIN_MISMATCH: extraction n={n_ext} != manifest n={man['n']} on a real run")

    kernels_full = load_kernel_rdms(man, man["n"])

    def load_rdm(fname: str, sha: str) -> np.ndarray:
        path = os.path.join(stamp_dir, fname)
        if sha256_file(path) != sha:
            raise SystemExit(f"ERR_PIN_MISMATCH: {fname} sha differs from extraction meta")
        with np.load(path) as z:
            if list(z["ids"]) != ids:
                raise SystemExit(f"ERR_ITEM_ORDER: {fname} ids differ")
            return np.asarray(z["similarity"], dtype=np.float64)

    fam_rdms = {f: load_rdm(fd["rdm_file"], fd["rdm_sha256"]) for f, fd in ext["families"].items()}
    cov_rdms = {e: load_rdm(ed["rdm_file"], ed["rdm_sha256"]) for e, ed in ext["embedders"].items()}

    per_pair = {}
    for fam_a, fam_b in man["pairs"]:
        dead = set(ext["families"][fam_a]["zero_signature_ids"]) | set(
            ext["families"][fam_b]["zero_signature_ids"])
        keep = [i for i, cid in enumerate(ids) if cid not in dead]
        sel = np.ix_(keep, keep)
        kernels = {k: v[:n_ext, :n_ext][sel] for k, v in kernels_full.items()}
        cov2_ods = [r.offdiag(cov_rdms[e][sel]) for e in sorted(cov_rdms)]
        SA, SB = fam_rdms[fam_a][sel], fam_rdms[fam_b][sel]

        print(f"\n=== pair ({fam_a}, {fam_b}): {len(keep)} items ===", flush=True)
        res = battery_scale(kernels, SA, SB, cov2_ods, n_perm_mantel, n_perm_gate)
        print(f"  gate acc={res['gate_G']['acc']:.4f} p={res['gate_G']['p']:.5f}  "
              f"P1 rho={res['P1_spearman_vs_Xsym']['rho']:.4f} p={res['P1_spearman_vs_Xsym']['p']:.5f}  "
              f"P2' rho={res['P2p_partial_cov2_vs_Xsym']['rho']:.4f} "
              f"p={res['P2p_partial_cov2_vs_Xsym']['p']:.5f}  -> {res['outcome']}", flush=True)
        per_pair[f"{fam_a}|{fam_b}"] = {"n_items": len(keep), "battery": res}

    hb = per_pair["gpt2|pythia-160m"]["battery"]["decision_flags"]
    headline = bool(hb["gate_pass"] and hb["P1_pass"] and hb["P2p_pass"])
    outcome = ("AT-SCALE HOLDS (the n=51 PASS pair passes gate+P1+P2' at n~1054)" if headline
               else "AT-SCALE DOES NOT HOLD on the headline pair (per-pair outcomes reported verbatim)")

    out = {
        "experiment": "E8 extension 2: at-scale geometry, 1,054 concepts (gloss-based)",
        "date": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "mock": mock,
        "limit": ext.get("limit"),
        "criterion_verbatim": e8.CRITERION_VERBATIM,
        "headline_rule_verbatim": man["headlineRule"],
        "design_pin": man["designPin"],
        "estimator_changes": "gloss-based signatures; cov2 gloss-embedding covariates; "
                             "2000-perm Mantel; retrieval descriptive (README §Extension 2)",
        "pins": {
            "encoderContentHash": ext["encoderContentHash"],
            "glossHash": ext["glossHash"],
            "manifest_sha256": ext["manifest_sha256"],
            "primary_kernel_variant": e8.PRIMARY_KERNEL,
            "at_scale_distortion_rdm_spearman": man["kernelRdmScale"]["atScaleDistortionRdmSpearman"],
            "x4_kernel_v0_distortion": man["kernelRdmScale"]["x4KernelV0DistortionRdmSpearman"],
        },
        "diagnostics": {f: fd["diagnostics"] for f, fd in ext["families"].items()},
        "embedder_pins": ext["embedders"],
        "seed": e8.SEED, "n_perm_mantel": n_perm_mantel, "n_perm_gate": n_perm_gate,
        "outcome": outcome,
        "headline_pass": headline,
        "per_pair": per_pair,
    }
    jpath = os.path.join(stamp_dir, "results-e8-scale.json")
    with open(jpath, "w") as f:
        json.dump(out, f, indent=2, default=e8._json_default)
    write_verdict(stamp_dir, out)
    print(f"\nwrote {jpath}\nOUTCOME: {outcome}")


def write_verdict(stamp_dir: str, out: dict) -> None:
    L = [
        "# E8 extension 2 — at-scale geometry (1,054 concepts): verdict",
        "",
        f"date: {out['date']}  |  mock: {out['mock']}  |  seed: {out['seed']}  |  "
        f"mantel perms: {out['n_perm_mantel']}  |  gate perms: {out['n_perm_gate']}  |  "
        f"kernel: {out['pins']['primary_kernel_variant']}",
        f"encoder: `{out['pins']['encoderContentHash']}`  |  GLOSS-HASH: `{out['pins']['glossHash'][:16]}…`",
        "",
        "**Pre-registered criterion (docs/poc-design.md E8, verbatim):**",
        f"> {out['criterion_verbatim']}",
        "",
        "**Pre-registered headline rule (README §Extension 2, verbatim):**",
        f"> {out['headline_rule_verbatim']}",
        "",
        f"Estimator changes forced by scale (pre-registered): {out['estimator_changes']}.",
        f"Projected path: jl512 primary; at-scale distortion RDM-Spearman "
        f"{out['pins']['at_scale_distortion_rdm_spearman']['jl512']:.4f} (8192->512), "
        f"{out['pins']['at_scale_distortion_rdm_spearman']['jl576']:.4f} (8192->576) "
        f"(X4 kernel-v0 figures: {out['pins']['x4_kernel_v0_distortion']['jl512']:.4f} / "
        f"{out['pins']['x4_kernel_v0_distortion']['jl576']:.4f}).",
        "",
        f"## OUTCOME: **{out['outcome']}**",
        "",
        "| pair | items | gate acc (p) | P1 rho (p) | P2' rho (p) | pair outcome |",
        "|---|---|---|---|---|---|",
    ]
    for pair, pdata in out["per_pair"].items():
        b = pdata["battery"]
        g, p1, p2 = b["gate_G"], b["P1_spearman_vs_Xsym"], b["P2p_partial_cov2_vs_Xsym"]
        L.append(f"| {pair} | {pdata['n_items']} | {g['acc']:.4f} ({g['p']:.5f}) "
                 f"| {p1['rho']:.4f} ({p1['p']:.5f}) | {p2['rho']:.4f} ({p2['p']:.5f}) "
                 f"| {b['outcome']} |")
    L += ["", "## Holm secondaries + sensitivity + retrieval (descriptive)", ""]
    for pair, pdata in out["per_pair"].items():
        b = pdata["battery"]
        L.append(f"**{pair}**")
        for name, t in b["secondaries"].items():
            h = b["holm"][name]
            L.append(f"- {name}: rho {t['rho']:.4f} (p {t['p']:.5f}, holm {h['p_holm']:.5f}, "
                     f"{'reject' if h['reject_at_0.05'] else 'no reject'})")
        for kv, t in b["kernel_variant_sensitivity_P2pform"].items():
            L.append(f"- sensitivity {kv}: rho {t['rho']:.4f} (p {t['p']:.5f})")
        for tag, t in b["retrieval_descriptive"].items():
            L.append(f"- retrieval {tag}: top-1 acc {t['acc']:.4f} (chance {t['chance_acc']:.5f}; descriptive)")
        L.append("")
    L += [
        "Diagnostics: " + "; ".join(
            f"{f}: FVU {d['fvu']:.4f}, mean L0 {d['mean_l0']:.1f}" for f, d in out["diagnostics"].items()),
        "",
        "Scope + pre-named weaknesses (README §Extension 2): gloss-mediated signatures test "
        "correspondence of gloss RENDERINGS; glosses are programme-authored, not independent text; "
        "1,000/1,054 concepts are pure prime synthetic structures — at-scale correspondence, if "
        "found, is about structural geometry, not lexical semantics.",
    ]
    if out["mock"]:
        L += ["", "**MOCK RUN — pipeline smoke test only; numbers are meaningless by construction.**"]
    with open(os.path.join(stamp_dir, "verdict-e8-scale.md"), "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main())
