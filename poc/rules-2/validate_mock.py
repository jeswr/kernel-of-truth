#!/usr/bin/env python3
"""RULES-2 mock-validation runner — produces the PINNED green-mock artifact
poc/rules-2/results/mock-validation.json (REWORK-2, cross-vendor prereg
review item 9: 'pin a green mock artifact — the wrapper currently only
prints reminders'; modal_rules2._launch_gates refuses any full run whose
staged bytes do not match this artifact's harness sha).

$0 CPU, deterministic mechanics; every number below is MOCK end-to-end and
NEVER a measurement. Steps (all fail-closed):
  1. monolithic --mock run (all arms, stub LM);
  2. the SAME campaign as the 10 canonical mock shard jobs
     (--arms/--seeds/--shard-tag) + merge_shards.py;
  3. the pinned analysis on BOTH; assert equality of every field except
     process-measured metrics (wall/RSS/engine-us/USD-derived), which can
     never reproduce across processes — the disclosed exclusion list is
     embedded in the artifact;
  4. evaluate the DRAFT record's verdict_rules over the merged analysis
     (the planted stub gradient must resolve a definite verdict);
  5. --dry-plan for the R1 and R2 tiers (must both be green).

This module states NO feasibility conclusion.

Usage: python3 poc/rules-2/validate_mock.py
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
RUNNER = os.path.join(_HERE, "rules2_runner.py")
MERGER = os.path.join(_HERE, "merge_shards.py")
ANALYSIS = os.path.join(_ROOT, "analysis", "rules_2_go.py")
WRAPPER = os.path.join(_HERE, "modal", "modal_rules2.py")
C8 = os.path.join(_HERE, "results", "c8-result.json")
RECORD = os.path.join(_ROOT, "registry", "experiments", "rules-2.json")

# process-measured metrics: legitimately non-reproducible across processes
# (CPU peak RSS is a process-wide high-water mark; engine-us and wall are
# timings; USD/gpu-hours/N* derive from them). EVERY other field must match.
MEASURED_FIELDS = {
    "engine_cpu_seconds_total", "engine_us_mean", "mean_engine_us",
    "engine_us_total", "usd_per_query_flops_share", "usd_per_query",
    "b2_usd_per_query", "b4_usd_per_query_flops_share", "n_star_queries",
    "saving_usd_per_query", "gpu_hours", "usd", "wall_seconds",
    "peak_mem_bytes", "peak_mem_bytes_max", "wall_hours", "usd_flops_share",
    "claim_carrier_b2_r1_train_peak_bytes", "per_arm_rung_train_peak_bytes",
    "per_arm_rung_eval_peak_bytes", "wallClockHours",
}

MOCK_SHARDS = [  # B4 STRUCK (issue #24 (C) + IP-4, PROPOSED-ASM-1847/1848)
    ("B0", "0", "b0-r1-s0"),
    ("B1", "0", "b1-r1-s0"), ("B1", "1", "b1-r1-s1"),
    ("B2", "0", "b2-r1-s0"), ("B2", "1", "b2-r1-s1"),
    ("B3", "0", "b3-r1-s0"), ("B3", "1", "b3-r1-s1"),
    ("c1p", "0", "c1p-r1-s0"), ("c1p", "1", "c1p-r1-s1"),
    ("B5", "0", "b5-r3-s0"),
]


def run(cmd, **kw):
    print("$ " + " ".join(cmd))
    r = subprocess.run(cmd, **kw)
    if r.returncode != 0:
        raise SystemExit("ERR_MOCK_VALIDATION: %r exited rc=%d"
                         % (cmd[1] if len(cmd) > 1 else cmd[0],
                            r.returncode))
    return r


def strip_measured(o):
    if isinstance(o, dict):
        return {k: strip_measured(v) for k, v in o.items()
                if k not in MEASURED_FIELDS}
    if isinstance(o, list):
        return [strip_measured(x) for x in o]
    return o


def eval_metric_expr(expr, out):
    """Evaluate a kot-reg/2 verdict_rules 'when' expression over the
    analysis output (metric paths '/gates/x', '/analysis/y')."""
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


def main():
    work = tempfile.mkdtemp(prefix="r2-mockval-")
    py = sys.executable

    # staged-bytes sha this validation pins against
    man_out = subprocess.run([py, WRAPPER, "--print-manifest"],
                             capture_output=True, text=True, check=True)
    staged_sha = man_out.stdout.strip().split()[-1]

    # 1) monolithic mock
    mono = os.path.join(work, "mono")
    run([py, RUNNER, "--out-dir", mono, "--mock"],
        stdout=subprocess.DEVNULL)

    # 2) sharded mock + merge
    shard_dirs = []
    for arm, seeds, tag in MOCK_SHARDS:
        d = os.path.join(work, "j-" + tag)
        run([py, RUNNER, "--out-dir", d, "--mock", "--arms", arm,
             "--seeds", seeds, "--shard-tag", tag],
            stdout=subprocess.DEVNULL)
        shard_dirs.append(d)
    merged = os.path.join(work, "merged")
    run([py, MERGER, "--out-dir", merged] + shard_dirs)

    # 3) pinned analysis on both; parity modulo measured metrics
    outs = {}
    for name, d in (("mono", mono), ("merged", merged)):
        r = subprocess.run(
            [py, ANALYSIS,
             "--run-records",
             os.path.join(d, "run-records-rules2-mock.jsonl"),
             "--results", os.path.join(d, "results-rules2-mock.json"),
             "--c8", C8, "--rules1-primary-lb", "0.10"],
            capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("ERR_MOCK_VALIDATION: analysis failed on %s: %s"
                             % (name, r.stderr[-500:]))
        outs[name] = json.loads(r.stdout)
    a = json.dumps(strip_measured(outs["mono"]), sort_keys=True)
    b = json.dumps(strip_measured(outs["merged"]), sort_keys=True)
    if a != b:
        raise SystemExit("ERR_MOCK_VALIDATION: monolithic and sharded+merged "
                         "analyses differ beyond process-measured metrics")
    print("parity: monolithic == sharded+merged (modulo measured metrics)")

    # 4) verdict mapping over the merged analysis
    rec = json.load(open(RECORD))
    verdict = None
    for rule in rec["verdict_rules"]:
        if eval_metric_expr(rule["when"], outs["merged"]):
            verdict = rule["verdict"]
            break
    if verdict is None:
        raise SystemExit("ERR_MOCK_VALIDATION: no verdict rule fired "
                         "(missing terminal catch-all?)")
    print("verdict mapping on MOCK planted gradient: %s "
          "(a mock-mechanics resolution, NEVER evidence)" % verdict)

    # 5) dry-plans (both tiers)
    for rungs in ("R1", "R2"):
        run([py, RUNNER, "--out-dir", os.path.join(work, "dry"),
             "--dry-plan", "--rungs", rungs], stdout=subprocess.DEVNULL)

    mono_res = json.load(open(os.path.join(mono,
                                           "results-rules2-mock.json")))
    merged_res = json.load(open(os.path.join(merged,
                                             "results-rules2-mock.json")))
    an = outs["merged"]["analysis"]
    artifact = {
        "artifact": "rules-2 pinned green-mock validation "
                    "(REWORK-2, review item 9)",
        "mode": "MOCK",
        "green": True,
        "date_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ",
                                                __import__("time").gmtime()),
        "harness_manifest_sha256": staged_sha,
        "status_note": "mock mechanics validation ONLY — the planted stub "
                       "gradient exists so gates/analysis/verdict-mapping "
                       "resolve; nothing here is a measurement or a "
                       "feasibility conclusion",
        "monolithic": {"n_rows": mono_res["n_rows"],
                       "records_sha256": mono_res["records_sha256"],
                       "outcome": mono_res["outcome"]},
        "sharded": {"n_shards": len(MOCK_SHARDS),
                    "n_rows": merged_res["n_rows"],
                    "records_sha256": merged_res["records_sha256"],
                    "shard_tags": [t for _a, _s, t in MOCK_SHARDS]},
        "analysis_parity": "monolithic == sharded+merged on every field "
                           "except the disclosed process-measured metrics",
        "measured_fields_excluded_from_parity": sorted(MEASURED_FIELDS),
        "gates_on_mock": {k: outs["merged"]["gates"][k]
                          for k in sorted(outs["merged"]["gates"])},
        "mock_verdict_mapping": verdict,
        "mock_primary_band": an["primary_band"]["value"],
        "dry_plans_green": ["R1", "R2"],
    }
    out_path = os.path.join(_HERE, "results", "mock-validation.json")
    with open(out_path, "w") as f:
        json.dump(artifact, f, indent=1, sort_keys=True)
        f.write("\n")
    print("green mock artifact -> %s (harness sha %s)"
          % (out_path, staged_sha[:16]))
    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
