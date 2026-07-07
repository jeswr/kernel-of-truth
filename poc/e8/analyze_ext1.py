#!/usr/bin/env python3
"""E8 extension-1 statistics: third-family replication (bead
kernel-of-truth-fnq; pre-registration: poc/e8/README.md §Extension 1,
fixed before any ext-1 code or download).

    python3 poc/e8/analyze_ext1.py poc/e8/results-incoming/<stamp>-ext1-modal

Consumes: the NEW extraction (family C signatures) + the COMMITTED original
stamp's family A/B signatures (sha-asserted against e8-manifest-ext1.json)
+ the committed E2 inputs and re-analysis RDMs. Runs analyze.full_battery
UNCHANGED once per pre-registered pair; analyze.py's bytes stay as committed
with the original verdict. Writes results-e8-ext1.json + verdict-e8-ext1.md
into the new stamp dir.
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
import analyze as e8  # noqa: E402  (full_battery + pins + machinery, unchanged)

r = e8.r
MANIFEST = os.path.join(HERE, "inputs", "e8-manifest-ext1.json")

REPLICATION_RULE_VERBATIM = (
    "the extension REPLICATES iff BOTH new pairs pass P1 AND P2 (p<0.01) with gates "
    "passed; anything weaker is reported per-pair, verbatim, no cherry-picking"
)


def sha256_file(path: str) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_signatures(npz_path: str) -> tuple:
    with np.load(npz_path) as z:
        return list(z["ids"]), np.asarray(z["signatures"], dtype=np.float64)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    stamp_dir = sys.argv[1].rstrip("/")
    with open(MANIFEST) as f:
        man = json.load(f)
    with open(os.path.join(stamp_dir, "e8-extraction.json")) as f:
        ext = json.load(f)
    mock = bool(ext.get("mock"))
    n_perm = 500 if mock else e8.N_PERM
    n_perm_retr = 100 if mock else e8.N_PERM_RETRIEVAL

    if ext["encoderContentHash"] != man["encoderContentHash"]:
        raise SystemExit("ERR_PIN_MISMATCH: extraction encoder hash differs from ext1 manifest")
    c_name = man["extraction_families"][0]
    if list(ext["families"]) != [c_name]:
        raise SystemExit(f"ERR_FAMILIES: extraction families {list(ext['families'])} != [{c_name}]")

    # ---- family C (new extraction) ----
    c_meta = ext["families"][c_name]
    c_ids, c_sigs = load_signatures(os.path.join(stamp_dir, c_meta["signature_file"]))
    if c_ids != ext["ids"]:
        raise SystemExit("ERR_ITEM_ORDER: family C signature ids differ from extraction ids")

    # ---- families A/B: committed signatures, sha-asserted (byte reuse) ----
    stamp0 = os.path.join(REPO, man["reusedSignatures"]["stamp"])
    reused: dict = {}
    for fam, pin in man["reusedSignatures"]["families"].items():
        path = os.path.join(stamp0, pin["file"])
        got = sha256_file(path)
        if got != pin["sha256"]:
            raise SystemExit(f"ERR_PIN_MISMATCH: {fam} committed signatures sha {got[:12]}… "
                             f"!= pinned {pin['sha256'][:12]}…")
        reused[fam] = load_signatures(path)
    with open(os.path.join(stamp0, "e8-extraction.json")) as f:
        ext0 = json.load(f)
    dead0 = {i for fam in ext0["families"].values() for i in fam["zero_signature_ids"]}

    # ---- shared inputs (kernel + baselines + emb4) ----
    inp = r.load_inputs(os.path.join(e8.E2_DIR, "inputs"))
    if inp["items"]["encoderContentHash"] != man["encoderContentHash"]:
        raise SystemExit("ERR_PIN_MISMATCH: E2 inputs encoder hash differs from ext1 manifest")
    analysis_ids = [it["id"] for it in inp["items"]["items"]]
    kernels_all = r.kernel_matrices(inp)

    per_pair = {}
    for fam_a, fam_b in man["pairs"]:
        assert fam_b == c_name, "pre-registered pairs put family C second"
        a_ids, a_sigs = reused[fam_a]
        dead_c = set(c_meta["zero_signature_ids"])
        keep_ids = [i for i in a_ids if i in set(c_ids) and i not in dead0 and i not in dead_c]
        sel_a = [a_ids.index(i) for i in keep_ids]
        sel_c = [c_ids.index(i) for i in keep_ids]
        sel_k = [analysis_ids.index(i) for i in keep_ids]

        kernels = {k: v[np.ix_(sel_k, sel_k)] for k, v in kernels_all.items()}
        orig3_ods = [
            r.offdiag(np.asarray(inp[k]["similarity"], dtype=np.float64)[np.ix_(sel_k, sel_k)])
            for k in ("word2vec", "wordnet", "gloss")
        ]
        emb4_ods = e8.load_emb4(man, keep_ids)
        SA = r.cosine_sim_matrix(a_sigs[sel_a])
        SB = r.cosine_sim_matrix(c_sigs[sel_c])

        print(f"\n=== pair ({fam_a}, {fam_b}): {len(keep_ids)} items ===", flush=True)
        res = e8.full_battery(kernels, SA, SB, orig3_ods, emb4_ods, n_perm, n_perm_retr)
        print(f"  gate p={res['gate_G']['p']:.5f}  P1 rho={res['P1_spearman_vs_Xsym']['rho']:.4f} "
              f"p={res['P1_spearman_vs_Xsym']['p']:.5f}  P2 rho={res['P2_partial_orig3_vs_Xsym']['rho']:.4f} "
              f"p={res['P2_partial_orig3_vs_Xsym']['p']:.5f}  -> {res['outcome']}", flush=True)
        per_pair[f"{fam_a}|{fam_b}"] = {"n_items": len(keep_ids), "battery": res}

    replicated = all(
        p["battery"]["decision_flags"]["gate_pass"]
        and p["battery"]["decision_flags"]["P1_pass"]
        and p["battery"]["decision_flags"]["P2_pass"]
        for p in per_pair.values()
    )
    outcome = ("REPLICATED (both new pairs PASS; E8 now reports 3/3 pairs across 3 "
               "architecture families)" if replicated
               else "NOT REPLICATED (per-pair outcomes reported verbatim)")

    out = {
        "experiment": "E8 extension 1: third-family replication",
        "bead": "kernel-of-truth-fnq",
        "date": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "mock": mock,
        "criterion_verbatim": e8.CRITERION_VERBATIM,
        "replication_rule_verbatim": REPLICATION_RULE_VERBATIM,
        "design_pin": "poc/e8/README.md §Extension 1 (fixed before any ext-1 code or download)",
        "family_c": c_meta["spec_pins"],
        "family_c_diagnostics": c_meta["diagnostics"],
        "family_c_attrition": {
            "in_vocab_dropped": c_meta["in_vocab_dropped_words"],
            "zero_signature_ids": c_meta["zero_signature_ids"],
        },
        "reused_signatures": man["reusedSignatures"],
        "pins": {
            "encoderContentHash": ext["encoderContentHash"],
            "corpusPin": ext["corpusPin"],
            "manifest_sha256": ext["manifest_sha256"],
            "primary_kernel_variant": e8.PRIMARY_KERNEL,
            "x4_distortion_rdm_spearman": man["stats"]["x4DistortionRdmSpearman"],
        },
        "seed": e8.SEED, "n_perm": n_perm, "n_perm_retrieval": n_perm_retr,
        "outcome": outcome,
        "replicated": replicated,
        "per_pair": per_pair,
    }
    jpath = os.path.join(stamp_dir, "results-e8-ext1.json")
    with open(jpath, "w") as f:
        json.dump(out, f, indent=2, default=e8._json_default)
    write_verdict(stamp_dir, out)
    print(f"\nwrote {jpath}\nOUTCOME: {outcome}")


def write_verdict(stamp_dir: str, out: dict) -> None:
    L = [
        "# E8 extension 1 — third-family replication: verdict",
        "",
        f"date: {out['date']}  |  mock: {out['mock']}  |  seed: {out['seed']}  |  "
        f"perms: {out['n_perm']} (retrieval {out['n_perm_retrieval']})  |  "
        f"kernel: {out['pins']['primary_kernel_variant']}",
        f"encoder: `{out['pins']['encoderContentHash']}`",
        "",
        "**Pre-registered criterion (docs/poc-design.md E8, verbatim):**",
        f"> {out['criterion_verbatim']}",
        "",
        "**Pre-registered replication rule (README §Extension 1, verbatim):**",
        f"> {out['replication_rule_verbatim']}",
        "",
        f"Family C: {out['family_c']['model_id']} + {out['family_c']['sae_repo']} "
        f"({out['family_c']['hookpoint']}, {out['family_c']['sae_arch']}, "
        f"d_sae {out['family_c']['d_sae']}) — MLP-output site; the site mismatch vs the "
        "residual-stream families A/B is a named confound (conservative direction).",
        f"Family C diagnostics: FVU {out['family_c_diagnostics']['fvu']:.4f}, "
        f"mean L0 {out['family_c_diagnostics']['mean_l0']:.1f}; "
        f"in-vocab drops: {out['family_c_attrition']['in_vocab_dropped'] or 'none'}; "
        f"zero signatures: {out['family_c_attrition']['zero_signature_ids'] or 'none'}.",
        f"Families A/B signatures reused byte-identically from "
        f"`{out['reused_signatures']['stamp']}` (sha-asserted).",
        "",
        f"## OUTCOME: **{out['outcome']}**",
        "",
        "| pair | items | gate acc (p) | P1 rho (p) | P2 rho (p) | pair outcome |",
        "|---|---|---|---|---|---|",
    ]
    for pair, pdata in out["per_pair"].items():
        b = pdata["battery"]
        g, p1, p2 = b["gate_G"], b["P1_spearman_vs_Xsym"], b["P2_partial_orig3_vs_Xsym"]
        L.append(f"| {pair} | {pdata['n_items']} | {g['acc']:.4f} ({g['p']:.5f}) "
                 f"| {p1['rho']:.4f} ({p1['p']:.5f}) | {p2['rho']:.4f} ({p2['p']:.5f}) "
                 f"| {b['outcome']} |")
    L += ["", "## Holm secondaries per pair", ""]
    for pair, pdata in out["per_pair"].items():
        b = pdata["battery"]
        L.append(f"**{pair}**")
        L.append("")
        L.append("| test | stat | p | p_holm | reject@0.05 |")
        L.append("|---|---|---|---|---|")
        for name, t in b["secondaries"].items():
            stat = t.get("rho", t.get("acc"))
            h = b["holm"][name]
            L.append(f"| {name} | {stat:.4f} | {t['p']:.5f} | {h['p_holm']:.5f} | "
                     f"{'yes' if h['reject_at_0.05'] else 'no'} |")
        L.append("")
    L += [
        "Scope: these are pairs 2 and 3 of three, all at toy/small-model scale; "
        "family C is an MLP-site dictionary. Pre-named weaknesses "
        "(poc/e8/README.md §6 + §Extension 1) apply unchanged.",
    ]
    if out["mock"]:
        L += ["", "**MOCK RUN — pipeline smoke test only; numbers are meaningless by construction.**"]
    with open(os.path.join(stamp_dir, "verdict-e8-ext1.md"), "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main())
