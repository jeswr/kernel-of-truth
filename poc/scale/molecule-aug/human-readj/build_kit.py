#!/usr/bin/env python3
"""build_kit.py — deterministic builder of the s5-human-readj input corpus.

Builds data/s5-human-readj/ (the hash-pinned input packet for the 2-human
fidelity re-adjudication, registry/experiments/s5-human-readj.json) from the
EXISTING, frozen molecule-S5 re-pilot artefacts under
poc/scale/molecule-aug/s5-run/stage1-repilot/. Nothing is generated, judged,
or regenerated: this is a pure re-packaging with provenance verification.

Fail-closed (exit 1, ERR_HRA_*):
  ERR_HRA_FREEZE     FREEZE-v2.1.json missing or a verified pin mismatches
  ERR_HRA_KEY        judge-key-v2.json does not carry exactly the expected
                     95 fidelity cells (48 flat + 47 mol) over 24 concepts,
                     with conception.mol-fable the single exhausted cell
  ERR_HRA_ITEM       a judge-input item file is missing/empty or its sha does
                     not match a previously built corpus (tamper guard)
  ERR_HRA_PROXY      a proxy judgment file is unreadable, or the recomputed
                     proxy aggregate (b, c, delta_pp) does not equal the
                     pinned results-s5-v2.json primary (emission oracle)
  ERR_HRA_EXISTS     data/s5-human-readj exists with DIFFERENT content

Determinism: output bytes are a pure function of the pinned inputs (sorted
walks, no timestamps, seeded shuffle with the registered string seed). Running
twice is byte-idempotent; the kot-corpus-hash/1 digest is printed for the
registry pin.

Design sources: PROTOCOL.md (this dir) §3–§4; DESIGN-v2.md §2 (ITT, E2);
FREEZE-v2.1.json (re-pilot pins). Proxy final rule ported verbatim from
run_s5.py final_v2 (F1==F2 -> that verdict; else F3 majority; a failed F1/F2
leg -> UNJUDGED; missing F3 -> UNRESOLVED).
"""

import hashlib
import json
import os
import random
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOLAUG = os.path.dirname(HERE)                        # poc/scale/molecule-aug
ROOT = os.path.abspath(os.path.join(MOLAUG, "..", "..", ".."))
REPILOT = os.path.join(MOLAUG, "s5-run", "stage1-repilot")
OUT = os.path.join(ROOT, "data", "s5-human-readj")

ORDER_SEED = "s5-human-readj/1|order|20260716"        # registered permutation seed
CELLS = ("flat-luna", "flat-fable", "mol-luna", "mol-fable")
EXHAUSTED = ("conception", "mol-fable")               # ERR_REF_UPTAKE_EXHAUSTED, ITT LOSSY


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(1)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    with open(p, "rb") as f:
        return sha256_bytes(f.read())


def jload(p):
    with open(p) as f:
        return json.load(f)


def proxy_final(jroot, qid):
    """Ported verbatim from run_s5.py final_v2 (verdict only; quality dropped)."""
    def leg(j):
        p = os.path.join(jroot, j, qid + ".json")
        if not os.path.exists(p):
            return None
        try:
            d = jload(p)
        except Exception as e:
            die("ERR_HRA_PROXY", "unreadable %s: %s" % (p, e))
        return (d.get("verdicts") or {}).get("A") if d.get("ok") else None
    a, b = leg("F1"), leg("F2")
    if not a or not b:
        return {"F1": a and a["verdict"], "F2": b and b["verdict"],
                "F3": None, "final": "UNJUDGED"}
    if a["verdict"] == b["verdict"]:
        return {"F1": a["verdict"], "F2": b["verdict"], "F3": None,
                "final": a["verdict"]}
    t = leg("F3")
    if not t:
        return {"F1": a["verdict"], "F2": b["verdict"], "F3": None,
                "final": "UNRESOLVED"}
    votes = [a["verdict"], b["verdict"], t["verdict"]]
    return {"F1": a["verdict"], "F2": b["verdict"], "F3": t["verdict"],
            "final": max(set(votes), key=votes.count)}


def main():
    # --- verify the re-pilot freeze this packet derives from -----------------
    fz_path = os.path.join(MOLAUG, "FREEZE-v2.1.json")
    if not os.path.isfile(fz_path):
        die("ERR_HRA_FREEZE", "FREEZE-v2.1.json missing")
    freeze_sha = sha256_file(fz_path)
    fz = jload(fz_path)
    rubric_v21 = os.path.join(MOLAUG, "s5-judge-fidelity-v2.1.md")
    got = sha256_file(rubric_v21)
    want = fz["pins"]["s5_judge_fidelity_v21_sha256"]
    if got != want:
        die("ERR_HRA_FREEZE", "s5-judge-fidelity-v2.1.md sha %s != frozen %s"
            % (got, want))

    # --- load + validate the 95-cell key -------------------------------------
    key_path = os.path.join(REPILOT, "judge-key-v2.json")
    keyall = jload(key_path)
    fkey = keyall.get("fidelity") or die("ERR_HRA_KEY", "no fidelity key")
    slugs = sorted({v["slug"] for v in fkey.values()})
    cells = {(v["slug"], v["cell"]) for v in fkey.values()}
    if len(fkey) != 95 or len(slugs) != 24:
        die("ERR_HRA_KEY", "expected 95 cells / 24 concepts, got %d / %d"
            % (len(fkey), len(slugs)))
    missing = {(s, c) for s in slugs for c in CELLS} - cells
    if missing != {EXHAUSTED}:
        die("ERR_HRA_KEY", "exhausted-cell set %r != %r" % (missing, {EXHAUSTED}))
    n_flat = sum(1 for v in fkey.values() if v["cell"].startswith("flat-"))
    if (n_flat, 95 - n_flat) != (48, 47):
        die("ERR_HRA_KEY", "arm split %d/%d != 48/47" % (n_flat, 95 - n_flat))
    em = jload(os.path.join(REPILOT, "expanded-manifest.json"))["cells"]
    st = em.get("%s.%s" % EXHAUSTED, {}).get("status")
    if st == "ok":
        die("ERR_HRA_KEY", "%s.%s unexpectedly expanded ok" % EXHAUSTED)

    # --- proxy final verdicts + emission oracle vs pinned results ------------
    jroot = os.path.join(REPILOT, "judgments-fidelity")
    proxy = {qid: proxy_final(jroot, qid) for qid in sorted(fkey)}
    res_path = os.path.join(REPILOT, "results-s5-v2.json")
    res = jload(res_path)
    # recompute the proxy E2 primary from the finals (ITT; exhausted cell LOSSY)
    verd = {(m["slug"], m["cell"]): proxy[q]["final"] for q, m in fkey.items()}
    verd[EXHAUSTED] = "GATE-FAIL"
    b = c = 0
    for s in slugs:
        f = any(verd[(s, cl)] == "FAITHFUL" for cl in ("flat-luna", "flat-fable"))
        m = any(verd[(s, cl)] == "FAITHFUL" for cl in ("mol-luna", "mol-fable"))
        b += int(f and not m)
        c += int(m and not f)
    delta_pp = round(100.0 * (c - b) / 24, 1)
    p = res["primary_e2"]
    if (b, c, delta_pp) != (p["b_flat_only"], p["c_mol_only"], p["delta_pp"]):
        die("ERR_HRA_PROXY", "recomputed proxy primary (b=%d,c=%d,delta=%s) != "
            "pinned (b=%d,c=%d,delta=%s)" % (b, c, delta_pp, p["b_flat_only"],
                                             p["c_mol_only"], p["delta_pp"]))

    # --- assemble the corpus in memory ---------------------------------------
    items = {}
    for qid, meta in sorted(fkey.items()):
        p_txt = os.path.join(REPILOT, "judge-inputs-fidelity", qid + ".txt")
        if not os.path.isfile(p_txt):
            die("ERR_HRA_ITEM", "missing judge input %s" % p_txt)
        with open(p_txt, "rb") as f:
            data = f.read()
        if not data.strip():
            die("ERR_HRA_ITEM", "empty judge input %s" % p_txt)
        items[qid] = data

    order = sorted(items)
    rng = random.Random(ORDER_SEED)
    rng.shuffle(order)

    key_out = {
        "schema": "s5-human-readj-key/1",
        "coordinator_only": ("NEVER show any part of this file to an "
                             "adjudicator: it carries arm, cell, and proxy "
                             "verdicts (the blinding key)"),
        "order_seed": ORDER_SEED,
        "order_algorithm": ("python random.Random(order_seed).shuffle over the "
                            "lexicographically sorted item ids"),
        "cells": {qid: {
            "slug": m["slug"], "cell": m["cell"],
            "arm": m["cell"].split("-")[0], "generator": m["cell"].split("-")[1],
            "n_refs": m["n_refs"], "rendering_sha256": m["rendering_sha256"],
            "item_sha256": sha256_bytes(items[qid]),
            "proxy": proxy[qid],
        } for qid, m in sorted(fkey.items())},
        "exhausted_cell": {"slug": EXHAUSTED[0], "cell": EXHAUSTED[1],
                           "gate_code": "ERR_REF_UPTAKE_EXHAUSTED",
                           "itt": "LOSSY (never shown to adjudicators)"},
        "concepts": slugs,
        "proxy_pins": {
            "results_s5_v2_sha256": sha256_file(res_path),
            "judge_key_v2_sha256": sha256_file(key_path),
            "freeze_v21_sha256": freeze_sha,
            "primary_e2": {"b_flat_only": p["b_flat_only"],
                           "c_mol_only": p["c_mol_only"],
                           "delta_pp": p["delta_pp"],
                           "flat_e2": p["flat_e2"], "mol_e2": p["mol_e2"],
                           "mcnemar_exact_p": p["mcnemar_exact_p"],
                           "tango95_ci_pp": p["tango95_ci_pp"]},
            "judge_agreement_overall": res["judge_agreement"]["overall"],
            "judge_agreement_arm_mol": res["judge_agreement"]["arm_mol"],
        },
    }

    order_out = {"schema": "s5-human-readj-order/1", "seed": ORDER_SEED,
                 "algorithm": key_out["order_algorithm"], "n": len(order),
                 "order": order}

    tmpl_rows = ["order_index,item_id,verdict,missing,audit"]
    for i, qid in enumerate(order, 1):
        tmpl_rows.append("%d,%s,,," % (i, qid))
    template = ("\n".join(tmpl_rows) + "\n").encode()

    readme = open(os.path.join(HERE, "coordinator-readme.md"), "rb").read()
    rubric = open(os.path.join(HERE, "rubric.md"), "rb").read()
    recon = open(os.path.join(HERE, "reconciliation.md"), "rb").read()

    files = {"rubric.md": rubric, "reconciliation.md": recon,
             "README.md": readme,
             "order.json": (json.dumps(order_out, indent=1, sort_keys=True)
                            + "\n").encode(),
             "key.json": (json.dumps(key_out, indent=1, sort_keys=True)
                          + "\n").encode(),
             "answers-template.csv": template}
    for qid, data in items.items():
        files[os.path.join("items", qid + ".txt")] = data
    manifest = {"schema": "s5-human-readj-manifest/1",
                "n_items": len(items),
                "files": {rel: sha256_bytes(data)
                          for rel, data in sorted(files.items())}}
    files["manifest.json"] = (json.dumps(manifest, indent=1, sort_keys=True)
                              + "\n").encode()

    # --- write (byte-idempotent; refuse differing existing content) ----------
    if os.path.isdir(OUT):
        for rel, data in sorted(files.items()):
            p = os.path.join(OUT, rel)
            if os.path.exists(p) and sha256_file(p) != sha256_bytes(data):
                die("ERR_HRA_EXISTS", "%s exists with different content — "
                    "refusing to overwrite a pinned corpus" % p)
    os.makedirs(os.path.join(OUT, "items"), exist_ok=True)
    for rel, data in sorted(files.items()):
        p = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(data)

    # kot-corpus-hash/1 digest (tools/registry/corpus-pin.py reference recipe)
    sys.path.insert(0, os.path.join(ROOT, "tools", "registry"))
    import kot_common as kc
    print("kot-corpus-hash/1 s5-human-readj =", kc.corpus_hash(ROOT, "s5-human-readj"))
    print("items=%d order_seed=%r flat=%d mol=%d exhausted=%s.%s"
          % (len(items), ORDER_SEED, n_flat, 95 - n_flat, *EXHAUSTED))


if __name__ == "__main__":
    main()
