#!/usr/bin/env python3
# ENGINE-INF deterministic engine harness (REVISION-1/2/3 build) — per-item
# closure-correctness rows for the 6 scored arms + the oracle arm, the
# divergence certificates (the ASM-1851 leg-1 analog, design §2.3), and the
# C-SHUF orbit rows (960 within-lemma relabelings evaluated on the
# outcome-equivalence cell frame; ASM-2114/2120). NO LLM anywhere; the
# entire instrument is pinned bytes -> certified engine -> string-equality
# scoring.
#
#   python3 engineinf_runner.py --dry-plan     # plan + worst-case cost, no run
#   python3 engineinf_runner.py                # EXPLORATORY frame run (seen
#                                              # items; exploratory-forever
#                                              # per ASM-2104 — mechanics
#                                              # validation only)
#   python3 engineinf_runner.py --holdout      # the REGISTERED confirmatory
#                                              # run over pinned items-H —
#                                              # REFUSES unless the
#                                              # coordinator's freeze marker
#                                              # exists and no H row exists
#
# HOLDOUT CUSTODY (design §2.5 [R1], ASM-2104 — mechanically enforced):
#   * EVERY mode (including --dry-plan) first scans results/ for any pinned
#     H item id and refuses (exit 3) on contamination.
#   * --holdout additionally refuses (exit 3) if rows for any H id already
#     exist ANYWHERE under results/, and refuses (exit 4) unless the file
#     FREEZE-AUTHORIZED exists next to this script (the coordinator creates
#     it at freeze; it is absent pre-freeze by construction).
#   * In --holdout the H divergence certificates are emitted BEFORE any
#     scoring, inside this same pipeline.
#
# Certificate discipline (rules-1): deterministic => no seeds; the WHOLE
# decision payload (rows + orbit rows) is computed twice and must be
# byte-identical.

import argparse
import json
import sys
import time
from pathlib import Path

from engineinf_lib import (ARM_NAMES, WN, OrbitEvaluator, arm_relation,
                           arm_tbox_paths, canon_sha, cell_key, cell_key_str,
                           divergence, derived_sides, kernel_inventory,
                           load_tbox, neutral_world, run_item, score,
                           sha256_file, MODULE, ROOT)

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
HOLDOUT = HERE / "holdout"
FREEZE_MARKER = HERE / "FREEZE-AUTHORIZED"


def holdout_item_ids():
    p = HOLDOUT / "items-h.json"
    if not p.is_file():
        return set()
    return {it["id"] for it in json.load(open(p))["items"]}


def scan_h_contamination(hids):
    """Mechanical custody scan (ASM-2104 clause 3/4): any pinned H item id
    appearing in ANY results artifact is contamination."""
    hits = []
    if not hids or not OUT.is_dir():
        return hits
    needles = {'"%s"' % i: i for i in hids}
    for p in sorted(OUT.rglob("*")):
        if not p.is_file() or p.suffix not in (".json", ".jsonl"):
            continue
        text = p.read_text(errors="replace")
        for needle, iid in sorted(needles.items()):
            if needle in text:
                hits.append({"file": str(p.relative_to(HERE)), "item": iid})
                break
    return hits


def refuse(code, msg):
    print("ENGINEINF-RUNNER REFUSAL: %s" % msg, file=sys.stderr)
    sys.exit(code)


def compute_rows(wn, items, gold, minted, arms_dir):
    """Engine pass THEN scoring pass, kept separable so the holdout mode can
    emit divergence certificates before any score is computed (§2.5)."""
    tboxes = {a: load_tbox(p) for a, p in sorted(arm_tbox_paths(arms_dir).items())}
    raw = {a: {} for a in ARM_NAMES}
    for it in items:
        world = neutral_world(wn, it)
        for arm in ARM_NAMES:
            rel = arm_relation(arm, it, minted)
            verdict, refusal, derived = run_item(tboxes[arm], world, rel)
            raw[arm][it["id"]] = {"relation": rel, "verdict": verdict,
                                  "refusal": refusal, "derived_cls": derived}
    return raw


def score_rows(wn, raw, items, gold, frame_label):
    rows_by_arm = {a: {} for a in ARM_NAMES}
    oracle = {}
    for it in items:
        g = gold[it["id"]]
        ck = cell_key_str(cell_key(wn, it))
        for arm in ARM_NAMES:
            r = raw[arm][it["id"]]
            correct, pen = score(g, r["verdict"], r["derived_cls"])  # ASM-2116
            rows_by_arm[arm][it["id"]] = {
                "item": it["id"], "kind": it["kind"], "lemma": it["lemma"],
                "cell": ck, "frame": frame_label,
                "h_star": bool(it.get("h_star", False)),
                "gold_rule": g["gold_rule"], "gold_verdict": g["verdict"],
                "arm": arm, "relation": r["relation"],
                "verdict": r["verdict"], "refusal": r["refusal"],
                "derived_cls": r["derived_cls"],
                "derived_sides": derived_sides(r["derived_cls"]),
                "correct": bool(correct), "honesty_penalty": pen}
        # oracle arm (PC-5): gold verdicts injected through the PINNED scorer
        ov = g["verdict"]
        ocorrect, open_ = score(g, ov)
        oracle[it["id"]] = {"item": it["id"], "kind": it["kind"],
                            "lemma": it["lemma"], "cell": ck,
                            "frame": frame_label,
                            "h_star": bool(it.get("h_star", False)),
                            "gold_rule": g["gold_rule"],
                            "gold_verdict": g["verdict"], "arm": "oracle",
                            "relation": None, "verdict": ov, "refusal": None,
                            "derived_cls": [], "derived_sides": [],
                            "correct": bool(ocorrect), "honesty_penalty": open_}
    return rows_by_arm, oracle


def g1g3_cells(wn, items, gold, holdout_mode):
    """The (G1∪G3) outcome-equivalence cell frame (ASM-2106); in holdout
    mode restricted to the NOVEL cells H* (design §2.5). One representative
    item per cell (lowest id) — exact under determinism."""
    cells = {}
    for it in sorted(items, key=lambda x: x["id"]):
        if gold[it["id"]]["gold_rule"] not in ("G1+G2", "G3"):
            continue
        if holdout_mode and not it.get("h_star", False):
            continue
        ck = cell_key_str(cell_key(wn, it))
        if ck not in cells:
            cells[ck] = {"cell": ck, "rep": it,
                         "gold_verdict": gold[it["id"]]["verdict"]}
    return [cells[k] for k in sorted(cells)]


def compute_orbit_rows(wn, minted, cells):
    """C-SHUF orbit rows: every member's decision on every frame cell
    (ASM-2114 mechanics; the A_union frame + calibrated p are computed at
    ANALYSIS from exactly these rows — ASM-2120 [R3])."""
    ev = OrbitEvaluator(wn, minted)
    per_member = ev.eval_cells(cells)
    gold_of = {c["cell"]: c["gold_verdict"] for c in cells}
    rows = []
    for m in sorted(per_member):
        for ck in sorted(per_member[m]):
            r = per_member[m][ck]
            rows.append({"m": m, "cell": ck, "verdict": r["verdict"],
                         "refusal": r["refusal"],
                         "derived_sides": r["derived_sides"],
                         "gold_verdict": gold_of[ck]})
    return rows, len(ev.members)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-plan", action="store_true")
    ap.add_argument("--holdout", action="store_true",
                    help="the registered confirmatory run over pinned "
                         "items-H (refuses pre-freeze)")
    args = ap.parse_args()

    # ---- custody gate, ALL modes, before anything else (ASM-2104) ----
    hids = holdout_item_ids()
    hits = scan_h_contamination(hids)
    if hits:
        refuse(3, "holdout item id(s) found in results artifacts — the "
                  "confirmatory outcomes must not exist before the "
                  "registered run: %s" % hits[:3])

    if args.holdout:
        if not hids:
            refuse(3, "--holdout requires pinned holdout/items-h.json")
        if not FREEZE_MARKER.is_file():
            refuse(4, "--holdout requires the coordinator's freeze marker "
                      "(FREEZE-AUTHORIZED). The registered run happens "
                      "AFTER the maintainer freezes — never before.")
        items_doc = json.load(open(HOLDOUT / "items-h.json"))
        gold = json.load(open(HOLDOUT / "gold-h.json"))["gold"]
        frame_label, suffix = "H", "-h"
    else:
        items_doc = json.load(open(OUT / "items.json"))
        gold = json.load(open(OUT / "gold.json"))["gold"]
        frame_label, suffix = "seen", ""
    items = items_doc["items"]
    minted, _, _ = kernel_inventory()

    plan = {
        "experiment": "engine-inference",
        "arms": list(ARM_NAMES) + ["oracle"],
        "orbit_members": 960,
        "items": len(items),
        "decisions": len(items) * (len(ARM_NAMES) + 1) * 2,
        "frame": frame_label,
        "channel": "DETERMINISTIC (pinned bytes -> certified twin engine -> "
                   "string-equality scoring vs third-party-derived gold); "
                   "no LLM, no host, no judge, no network",
        "worst_case_usd": 0.0,
        "compute": "CPU-only, single process, nice-appropriate; the rules-1 "
                   "certificate closed 958 worlds in <2s on this box — the "
                   "orbit adds ~960 x |cells| cached-TBox closures",
    }
    if args.dry_plan:
        print(json.dumps({"dry_plan": plan}, indent=1, sort_keys=True))
        return

    t0 = time.time()
    wn = WN()

    def one_pass():
        raw = compute_rows(wn, items, gold, minted, HERE / "arms")
        return raw

    raw = one_pass()

    # ---- divergence certificates BEFORE scoring (design §2.5 clause 4) ----
    pre_rows = {a: {iid: {"verdict": r["verdict"], "refusal": r["refusal"],
                          "derived_sides": derived_sides(r["derived_cls"])}
                    for iid, r in raw[a].items()} for a in ARM_NAMES}
    items_by_id = {it["id"]: it for it in items}
    certs = {b: divergence(pre_rows, b, items_by_id)
             for b in ARM_NAMES if b != "K"}
    cert_doc = {
        "schema": "kot-engineinf-divergence/2",
        "frame": frame_label,
        "role": ("Divergence certificate (design §2.3; the ASM-1851 leg-1 "
                 "analog): committed BEFORE any contrast is interpreted — "
                 "and, in holdout mode, emitted before any scoring "
                 "(ASM-2104 clause 4); 'full' = verdict-or-derived-side-set "
                 "differs (ASM-1994 signature), 'decision' = engine verdict "
                 "differs. A committed non-empty certificate over this "
                 "inventory is the ASM-1851 mechanical re-activation "
                 "artifact for the rules-2-shaped train-time twin "
                 "(ASM-1965)."),
        "divergence": {b: {"n_full": len(c["full"]),
                           "n_decision": len(c["decision"]),
                           "full": c["full"], "decision": c["decision"],
                           "composition": c["composition"]}
                       for b, c in sorted(certs.items())},
    }
    (OUT / ("divergence-certificate%s.json" % suffix)).write_text(
        json.dumps(cert_doc, indent=1, sort_keys=True) + "\n")

    # ---- scoring + orbit, double-run byte-identity ----
    rows_by_arm, oracle = score_rows(wn, raw, items, gold, frame_label)
    cells = g1g3_cells(wn, items, gold, args.holdout)
    orbit_rows, n_members = compute_orbit_rows(wn, minted, cells)

    raw2 = one_pass()
    rows2, oracle2 = score_rows(wn, raw2, items, gold, frame_label)
    orbit_rows2, _ = compute_orbit_rows(wn, minted,
                                        g1g3_cells(wn, items, gold,
                                                   args.holdout))
    sha1 = canon_sha({"rows": rows_by_arm, "oracle": oracle,
                      "orbit": orbit_rows})
    sha2 = canon_sha({"rows": rows2, "oracle": oracle2,
                      "orbit": orbit_rows2})

    with open(OUT / ("rows%s.jsonl" % suffix), "w") as f:
        for arm in ARM_NAMES:
            for iid in sorted(rows_by_arm[arm]):
                f.write(json.dumps(rows_by_arm[arm][iid], sort_keys=True) + "\n")
        for iid in sorted(oracle):
            f.write(json.dumps(oracle[iid], sort_keys=True) + "\n")
    with open(OUT / ("orbit-rows%s.jsonl" % suffix), "w") as f:
        for r in orbit_rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")

    per_arm = {}
    for arm in ARM_NAMES:
        rs = rows_by_arm[arm]
        per_arm[arm] = {
            "n": len(rs),
            "correct": sum(1 for r in rs.values() if r["correct"]),
            "honesty_penalty_sum": round(sum(r["honesty_penalty"]
                                             for r in rs.values()), 2),
            "refusals": sum(1 for r in rs.values() if r["verdict"] == "REFUSE"),
            "anomalous": sum(1 for r in rs.values()
                             if r["verdict"] == "ANOMALOUS")}
    per_arm["oracle"] = {"n": len(oracle),
                         "correct": sum(1 for r in oracle.values()
                                        if r["correct"])}

    pins = {
        "items_json": sha256_file((HOLDOUT / "items-h.json") if args.holdout
                                  else (OUT / "items.json")),
        "gold_json": sha256_file((HOLDOUT / "gold-h.json") if args.holdout
                                 else (OUT / "gold.json")),
        "rows_jsonl": sha256_file(OUT / ("rows%s.jsonl" % suffix)),
        "orbit_rows_jsonl": sha256_file(OUT / ("orbit-rows%s.jsonl" % suffix)),
        "divergence_certificate":
            sha256_file(OUT / ("divergence-certificate%s.json" % suffix)),
        "arm_manifest": sha256_file(HERE / "arms" / "arm-manifest.json"),
        "orbit_manifest": sha256_file(HERE / "arms" / "orbit-manifest.json"),
        "twin_engine_py": sha256_file(ROOT / "poc/rules-1/twin_engine.py"),
        "engineinf_lib_py": sha256_file(HERE / "engineinf_lib.py"),
        "engineinf_wn_py": sha256_file(HERE / "engineinf_wn.py"),
        "engineinf_runner_py": sha256_file(HERE / "engineinf_runner.py"),
        "module_manifest": sha256_file(MODULE / "manifest.json"),
    }
    result = {
        "schema": "kot-engineinf-run/2",
        "status": (("REGISTERED confirmatory holdout run (frozen record)."
                    if args.holdout else
                    "PRE-FREEZE EXPLORATORY execution of the pinned "
                    "deterministic harness on the SEEN frame "
                    "(exploratory-forever per ASM-2104; mechanics "
                    "validation only). NO feasibility conclusion is "
                    "stated; verdicts belong to verdict-gen over the "
                    "FROZEN record's registered holdout run.")),
        "plan": plan,
        "per_arm": per_arm,
        "n_g1g3_cells_frame": len(cells),
        "orbit": {"n_members": n_members,
                  "n_frame_cells": len(cells),
                  "n_rows": len(orbit_rows)},
        "divergence_counts": {b: {"full": len(c["full"]),
                                  "decision": len(c["decision"])}
                              for b, c in sorted(certs.items())},
        "determinism": {"double_run_sha_match": sha1 == sha2,
                        "decision_payload_sha256": sha1},
        "pins": pins,
        "timing_seconds": round(time.time() - t0, 3),
    }
    (OUT / ("run-result%s.json" % suffix)).write_text(
        json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in
                      ("per_arm", "divergence_counts", "determinism",
                       "n_g1g3_cells_frame", "orbit", "timing_seconds")},
                     indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
