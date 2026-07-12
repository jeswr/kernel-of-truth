#!/usr/bin/env python3
"""DDC mock-validation runner — produces the PINNED green-mock artifact
poc/ddc/results/mock-validation.json (rules-2 discipline:
modal_ddc._launch_gates refuses any full run whose staged bytes do not
match this artifact's harness sha).

$0 CPU, deterministic mechanics; every number below is MOCK end-to-end
and NEVER a measurement. Steps (all fail-closed):

  1. ddc0 monolithic --mock (g0_runner) -> the PINNED analysis
     (analysis/ddc0.py) -> the DRAFT ddc0 record's verdict_rules must
     resolve a definite verdict on the planted gradient;
  2. ddc1 monolithic --mock (ddc_runner, full ASM-1654 grid, both rungs)
     -> pinned analysis (analysis/ddc1.py);
  3. the SAME ddc1 campaign as the canonical per-cell shard jobs
     (t0 + s1 + s2 = 66 jobs, exactly modal_ddc --print-jobs) +
     merge_shards.py -> pinned analysis; assert EQUALITY of every
     analysis field except the disclosed measured cost ledger;
  4. the DRAFT ddc1 record's verdict_rules over the merged analysis
     (planted gradient must resolve a definite verdict);
  5. --dry-plan per tier + campaign ceiling (fail-closed $60 / $5 ddc0
     carve-out / 12 h per-job bound) — all green;
  6. LAW-1 mechanical assertion (DDC.md §1.2): STATIC — ddc_surgery.py
     (the only weights-touching module) references no kernel/codebook/
     encoder identifier and imports nothing from the selection estate;
     RUNTIME — assert_basis_provenance accepts model-side provenances
     and raises ERR_DDC_LAW1_TAINT on a kernel-provenance or tainted
     spec;
  7. g0_stats numpy micro self-test: a planted H->V alignment is
     recovered above its own (small-B) permutation null — the REAL §2.3
     statistics path exercised at $0.

This module states NO feasibility conclusion.

Usage: python3 poc/ddc/validate_mock.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, _HERE)

import ddc_common as C  # noqa: E402

DDC_RUNNER = os.path.join(_HERE, "ddc_runner.py")
G0_RUNNER = os.path.join(_HERE, "g0_runner.py")
MERGER = os.path.join(_HERE, "merge_shards.py")
WRAPPER = os.path.join(_HERE, "modal", "modal_ddc.py")
SURGERY = os.path.join(_HERE, "ddc_surgery.py")
AN_DDC0 = os.path.join(_ROOT, "analysis", "ddc0.py")
AN_DDC1 = os.path.join(_ROOT, "analysis", "ddc1.py")
REC_DDC0 = os.path.join(_ROOT, "registry", "experiments", "ddc0.json")
REC_DDC1 = os.path.join(_ROOT, "registry", "experiments", "ddc1.json")

# Measured process/cost metrics: legitimately non-reproducible across
# process boundaries; EVERY other analysis field must match byte-for-byte.
MEASURED_FIELDS = {"cost_ledger", "usd_total", "gpu_hours",
                   "wallClockHours"}

# LAW-1 static scan: none of these identifiers/paths may appear in the
# weights-touching module (kernel vectors select, they never enter).
LAW1_BANNED_TOKENS = ("codebookQ", "encoderQ", "kernel-v0", "molecules-v0",
                      "kot-enc", "ddc_selection", "g0_stats", "g0_runner",
                      "renderExplication", "generateExplication",
                      "plain-authored", "bag_vector", "probe-fixture")


def run(cmd, **kw):
    print("$ " + " ".join(cmd))
    r = subprocess.run(cmd, **kw)
    if r.returncode != 0:
        raise SystemExit("ERR_MOCK_VALIDATION: %r exited rc=%d"
                         % (cmd[1] if len(cmd) > 1 else cmd[0],
                            r.returncode))
    return r


def analysis(script, args):
    r = subprocess.run([sys.executable, script] + args,
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("ERR_MOCK_VALIDATION: %s failed: %s"
                         % (os.path.basename(script), r.stderr[-800:]))
    return json.loads(r.stdout)


def strip_measured(o):
    if isinstance(o, dict):
        return {k: strip_measured(v) for k, v in o.items()
                if k not in MEASURED_FIELDS}
    if isinstance(o, list):
        return [strip_measured(x) for x in o]
    return o


def eval_metric_expr(expr, out):
    """kot-reg/1 verdict_rules 'when' evaluator (metric paths '/gates/x',
    '/analysis/y') — the rules-2 validate_mock evaluator verbatim."""
    if "const" in expr:
        return bool(expr["const"])
    if "metric" in expr:
        node = out
        for part in expr["metric"].strip("/").split("/"):
            node = node[part]
        return bool(node)
    if expr.get("op") == "not":
        return not eval_metric_expr(expr["a"], out)
    a = eval_metric_expr(expr["a"], out)
    b = eval_metric_expr(expr["b"], out)
    return (a and b) if expr["op"] == "and" else (a or b)


def map_verdict(record_path, out):
    rec = json.load(open(record_path))
    for rule in rec["verdict_rules"]:
        if eval_metric_expr(rule["when"], out):
            return rule["verdict"]
    raise SystemExit("ERR_MOCK_VALIDATION: no verdict rule fired for %s "
                     "(missing terminal catch-all?)" % record_path)


def law1_static():
    src = open(SURGERY, encoding="utf-8").read()
    hits = [t for t in LAW1_BANNED_TOKENS if t in src]
    if hits:
        raise SystemExit("ERR_MOCK_VALIDATION: LAW-1 static scan FAILED — "
                         "ddc_surgery.py references %s" % hits)
    for line in src.splitlines():
        ls = line.strip()
        if ls.startswith(("import ", "from ")) and any(
                m in ls for m in ("ddc_selection", "g0_", "encoder",
                                  "benchmarks", "pubeval")):
            raise SystemExit("ERR_MOCK_VALIDATION: LAW-1 static scan "
                             "FAILED — surgery imports %r" % ls)
    return True


def law1_runtime():
    import ddc_surgery as S
    S.assert_basis_provenance({"provenance": "model-activation-basis",
                               "bases": [], "meta": {"construction": "t"}})
    S.assert_basis_provenance({"provenance": "haar-random-basis",
                               "bases": [], "meta": {"construction": "t"}})
    refused = 0
    for bad in ({"provenance": "kernel-codebook-vectors", "bases": [],
                 "meta": {}},
                {"provenance": "model-activation-basis", "bases": [],
                 "meta": {"construction": "t"},
                 "taint": "kernel-vector-derived"},
                {"provenance": None, "bases": []},
                "not-a-dict"):
        try:
            S.assert_basis_provenance(bad)
        except SystemExit as e:
            if "ERR_DDC_LAW1_TAINT" in str(e):
                refused += 1
    if refused != 4:
        raise SystemExit("ERR_MOCK_VALIDATION: LAW-1 runtime gate refused "
                         "%d/4 tainted specs" % refused)
    return True


def g0_stats_selftest():
    import numpy as np

    import g0_stats as G
    rng = np.random.default_rng(7)
    L, n, d = 2, 36, 20
    R = np.linalg.qr(rng.standard_normal((d, d)))[0]
    H = rng.standard_normal((L, n, d))
    V = H[0] @ R + 0.3 * rng.standard_normal((n, d))
    V -= V.mean(0)
    Vbag = rng.standard_normal((n, d))
    ids = ["c%02d" % i for i in range(n)]
    classes = ["prime"] * 18 + ["kernel-v0"] * 10 + ["molecules-v0"] * 8
    sp = G.make_splits(ids, classes, seed=0)
    assert not (set(sp["fit"]) & set(sp["sel"])), "split overlap"
    assert not (set(sp["fit"]) & set(sp["test"])), "split overlap"
    rows, t_b, _l = G.run_g0({"mean": H}, H * 0.98, H * 1.02, V, Vbag, sp,
                             sp["sel"][:5], B=12, perm_seed=1, crit_seed=1)
    top = max(rows, key=lambda r: r["test_score"])
    assert top["layer"] == 0, "planted alignment layer not recovered"
    assert top["test_score"] > max(t_b) - 1e-12 or \
        top["test_score"] > 0.8, "planted signal below its own null"
    return {"n_rows": len(rows), "top_layer": top["layer"],
            "top_score": round(top["test_score"], 4)}


def main():
    work = tempfile.mkdtemp(prefix="ddc-mockval-")
    py = sys.executable
    manifest = C.load_manifest()

    man_out = subprocess.run([py, WRAPPER, "--print-manifest"],
                             capture_output=True, text=True, check=True)
    staged_sha = man_out.stdout.strip().split()[-1]

    # 6+7) LAW-1 + statistics self-test first (cheapest, most load-bearing)
    law1_static()
    law1_runtime()
    print("LAW-1 assertions: static scan + runtime taint gate GREEN")
    g0self = g0_stats_selftest()
    print("g0_stats planted-alignment self-test GREEN: %s" % g0self)

    # 1) ddc0 monolithic mock -> pinned analysis -> verdict mapping
    d0 = os.path.join(work, "ddc0")
    run([py, G0_RUNNER, "--mock", "--out-dir", d0],
        stdout=subprocess.DEVNULL)
    out0 = analysis(AN_DDC0, [
        "--candidates", os.path.join(d0, "candidates-ddc0-mock.jsonl"),
        "--maxstat-null", os.path.join(d0, "maxstat-null-ddc0-mock.json"),
        "--sidecar", os.path.join(d0, "sidecar-ddc0-mock.json")])
    v0 = map_verdict(REC_DDC0, out0)
    print("ddc0 verdict mapping on MOCK planted gradient: %s "
          "(a mock-mechanics resolution, NEVER evidence)" % v0)

    # 2) ddc1 monolithic mock
    mono = os.path.join(work, "mono")
    run([py, DDC_RUNNER, "--mock", "--rungs", "r135,r360",
         "--out-dir", mono], stdout=subprocess.DEVNULL)
    fin = os.path.join(mono, "final")
    out_mono = analysis(AN_DDC1, [
        "--items", os.path.join(fin, "items-ddc1-mock.jsonl"),
        "--cells", os.path.join(fin, "cells-ddc1-mock.json"),
        "--sidecar", os.path.join(fin, "sidecar-ddc1-mock.json")])

    # 3) the SAME campaign as the canonical shard jobs + merge
    jobs = []
    for tier in ("t0", "s1", "s2"):
        jobs.extend(C.build_jobs(manifest, tier))
    shard_dirs = []
    t0 = time.time()
    for j in jobs:
        d = os.path.join(work, "j-" + j["tag"])
        run([py, DDC_RUNNER, "--mock", "--out-dir", d,
             "--rungs", j["rung"], "--arms", j["arm"],
             "--rhos", "%g" % j["rho"], "--seeds", str(j["seed"]),
             "--shard-tag", j["tag"]], stdout=subprocess.DEVNULL)
        shard_dirs.append(d)
    print("ran %d canonical mock shard jobs in %.1fs"
          % (len(jobs), time.time() - t0))
    merged = os.path.join(work, "merged")
    run([py, MERGER, "--out-dir", merged] + shard_dirs)
    out_merged = analysis(AN_DDC1, [
        "--items", os.path.join(merged, "items-ddc1-mock.jsonl"),
        "--cells", os.path.join(merged, "cells-ddc1-mock.json"),
        "--sidecar", os.path.join(merged, "sidecar-ddc1-mock.json")])

    a = json.dumps(strip_measured(out_mono), sort_keys=True)
    b = json.dumps(strip_measured(out_merged), sort_keys=True)
    if a != b:
        raise SystemExit("ERR_MOCK_VALIDATION: monolithic and "
                         "sharded+merged analyses differ beyond the "
                         "disclosed measured cost fields")
    print("parity: monolithic == sharded+merged "
          "(modulo the measured cost ledger)")

    # 4) verdict mapping over the merged ddc1 analysis
    v1 = map_verdict(REC_DDC1, out_merged)
    print("ddc1 verdict mapping on MOCK planted gradient: %s "
          "(a mock-mechanics resolution, NEVER evidence)" % v1)

    # 5) dry-plans: per tier + the campaign ceiling (all fail-closed)
    plans = {}
    for tier in ("t0", "ddc0", "s1", "s2"):
        plans[tier] = C.dry_plan_tier(manifest, tier, log=lambda *_: None)
    campaign = C.dry_plan_campaign(manifest, log=lambda *_: None)
    print("dry-plans GREEN: " + ", ".join(
        "%s $%.2f/%.1fh" % (t, p["usd"], p["gpu_hours"])
        for t, p in sorted(plans.items()))
        + "; campaign $%.2f < $%.0f ceiling"
        % (campaign["total_usd"], campaign["ceiling_usd"]))

    mono_res = json.load(open(os.path.join(mono,
                                           "results-ddc1-mock.json")))
    merged_res = json.load(open(os.path.join(merged,
                                             "results-ddc1-mock.json")))
    artifact = {
        "artifact": "ddc pinned green-mock validation (rules-2 build "
                    "discipline; modal_ddc launch gate 3)",
        "mode": "MOCK",
        "green": True,
        "date_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "harness_manifest_sha256": staged_sha,
        "status_note": "mock mechanics validation ONLY — the planted stub "
                       "gradients exist so gates/analysis/verdict-mapping "
                       "resolve; nothing here is a measurement or a "
                       "feasibility conclusion",
        "ddc0": {"verdict_mapping": v0,
                 "gates_on_mock": out0["gates"],
                 "n_layers_admitted_on_mock":
                     out0["analysis"]["n_layers_admitted"]},
        "ddc1": {
            "verdict_mapping": v1,
            "gates_on_mock": {
                k: v for k, v in out_merged["gates"].items()
                if isinstance(v, (bool, int, float, str))},
            "monolithic": {"n_rows": mono_res["n_rows"],
                           "records_sha256": mono_res["records_sha256"]},
            "sharded": {"n_shards": len(jobs),
                        "n_rows": merged_res["n_rows"],
                        "records_sha256": merged_res["records_sha256"],
                        "shard_tags": sorted(j["tag"] for j in jobs)},
            "analysis_parity": "monolithic == sharded+merged on every "
                               "field except the disclosed measured cost "
                               "fields",
        },
        "measured_fields_excluded_from_parity": sorted(MEASURED_FIELDS),
        "law1": {"static_scan": "GREEN (no kernel/codebook/encoder "
                                "identifier in ddc_surgery.py)",
                 "runtime_taint_gate": "GREEN (4/4 tainted specs refused "
                                       "with ERR_DDC_LAW1_TAINT)"},
        "g0_stats_selftest": g0self,
        "dry_plans_green": {t: {"usd": round(p["usd"], 2),
                                "gpu_hours": round(p["gpu_hours"], 2),
                                "worst_job_hours":
                                    round(p["worst_job_hours"], 2)}
                            for t, p in plans.items()},
        "campaign_dry_plan": {"total_usd": round(campaign["total_usd"], 2),
                              "ceiling_usd": campaign["ceiling_usd"]},
        "parallel_jobs": {"t0": 1, "ddc0": 2,
                          "s1": len(C.build_jobs(manifest, "s1")),
                          "s2": len(C.build_jobs(manifest, "s2"))},
    }
    out_path = os.path.join(_HERE, "results", "mock-validation.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(artifact, f, indent=1, sort_keys=True)
        f.write("\n")
    print("green mock artifact -> %s (harness sha %s)"
          % (out_path, staged_sha[:16]))
    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
