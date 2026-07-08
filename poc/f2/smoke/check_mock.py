#!/usr/bin/env python3
"""F2 mock validation — runs the harness in --mock (stub LM, CPU, $0) and
verifies the FROZEN contracts end-to-end:

1. every arm level of registry/experiments/f2.json ran and emitted a record;
2. record bodies pass the kot-log/1 raw-metrics lint (no derived stats);
3. piping the run-records into the PINNED analysis script (analysis/f2.py,
   sha re-checked against the frozen record) resolves EVERY field in
   pins.analysis_script.output_fields — the metric-emitter contract;
4. the P10 extraction-failure instrument gate is exercised in both
   directions (mock data passes it; a constructed high-failure record set
   flips it to INSTRUMENT-INVALID).

Usage:  python3 poc/f2/smoke/check_mock.py   (from anywhere; ~1 min, CPU)
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RUNNER = os.path.join(ROOT, "poc", "f2", "runner", "f2_runner.py")
ANALYSIS = os.path.join(ROOT, "analysis", "f2.py")
REG = os.path.join(ROOT, "registry", "experiments", "f2.json")

sys.path.insert(0, os.path.join(ROOT, "tools", "registry"))
import kot_common as kc  # noqa: E402

EXPECTED_ARMS = {
    "model-alone", "kernel-verify-retry", "kernel-as-text", "rag-over-text",
    "self-consistency-flop-matched", "gloss-self-verify-retry", "prm-verifier",
    "int4-quantized", "cascade-verifier-gated-135m-1p7b",
    "cascade-logprob-gated-135m-1p7b", "cascade-text-self-check-gated-135m-1p7b",
    "cascade-in-decode-gated-135m-1p7b", "extraction-instrument",
}


def fail(msg):
    print("SMOKE-FAIL: %s" % msg)
    sys.exit(1)


def resolve(out, pointer):
    cur = out
    for part in pointer.strip("/").split("/"):
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur


def main():
    with open(REG) as f:
        reg = json.load(f)

    # pinned-analysis integrity: the smoke test must exercise the EXACT script
    with open(ANALYSIS, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    pin = reg["pins"]["analysis_script"]["sha256"]
    if sha != pin:
        fail("analysis/f2.py sha %s != frozen pin %s" % (sha[:12], pin[:12]))
    print("ok: analysis/f2.py matches the frozen pin (%s...)" % sha[:12])

    # frozen arm levels == harness constants
    reg_arms = set(next(iv["levels"] for iv in reg["design"]["independent_vars"]
                        if iv["name"] == "arm"))
    if reg_arms != EXPECTED_ARMS:
        fail("registry arm levels != smoke expectation: %s"
             % sorted(reg_arms ^ EXPECTED_ARMS))

    with tempfile.TemporaryDirectory() as tmp:
        rc = subprocess.run(
            [sys.executable, RUNNER, "--out-dir", tmp, "--mock"],
            capture_output=True, text=True)
        sys.stdout.write(rc.stdout[-2000:])
        if rc.returncode != 0:
            fail("mock run rc=%d\n%s" % (rc.returncode, rc.stderr[-3000:]))
        records_path = os.path.join(tmp, "run-records-f2-mock.jsonl")
        with open(records_path) as f:
            lines = [json.loads(l) for l in f if l.strip()]

        arms_seen = {r["config"]["arm"] for r in lines}
        missing = EXPECTED_ARMS - arms_seen
        if missing:
            fail("arms never emitted: %s" % sorted(missing))
        print("ok: all %d frozen arm levels emitted (%d records)"
              % (len(EXPECTED_ARMS), len(lines)))

        # raw-metrics-only rule (P2 section 2.4) on every body
        for r in lines:
            bad = kc.find_forbidden_metric_keys(r.get("metrics", {}), "")
            if bad:
                fail("derived-stat keys in metrics: %s (arm %s)"
                     % (bad, r["config"]["arm"]))
        print("ok: no derived statistics in any metric body")

        # pipe through the pinned analysis; every frozen output field resolves
        with open(records_path) as f:
            an = subprocess.run([sys.executable, ANALYSIS], stdin=f,
                                capture_output=True, text=True)
        if an.returncode != 0:
            fail("analysis/f2.py rc=%d\n%s" % (an.returncode, an.stderr[-3000:]))
        out = json.loads(an.stdout)
        unresolved = []
        for field in reg["pins"]["analysis_script"]["output_fields"]:
            ok, _v = resolve(out, field)
            if not ok:
                unresolved.append(field)
        if unresolved:
            fail("frozen output fields unresolvable from mock records: %s"
                 % unresolved)
        print("ok: all %d frozen analysis output fields resolve"
              % len(reg["pins"]["analysis_script"]["output_fields"]))
        if not out["gates"]["instrument_valid"]:
            fail("mock extraction gate should PASS (stub fail rate 2%)")
        print("ok: P10 instrument gate PASSES on mock data "
              "(gap_R1R2=%.3f, best_k=%s)"
              % (out["analysis"]["gap_closed_fraction_R1R2"],
                 out["analysis"]["best_retry_budget"]))

        # gate flips: replace iface records with a high-failure set
        flipped = [r for r in lines if r["config"]["arm"] != "extraction-instrument"]
        for rung in ("R1", "R2"):
            flipped.append({"config": {"arm": "extraction-instrument",
                                       "rung": rung, "retry_budget": 0,
                                       "escalation_budget": 0, "seed": 0},
                            "metrics": {"n_labelled": 300,
                                        "n_extraction_failures": 60}})
        an2 = subprocess.run([sys.executable, ANALYSIS],
                             input="\n".join(json.dumps(r) for r in flipped),
                             capture_output=True, text=True)
        out2 = json.loads(an2.stdout)
        if out2["gates"]["instrument_valid"]:
            fail("gate failed to flip on 20% extraction-failure set")
        print("ok: P10 instrument gate flips to INVALID on a 20%-failure set")

        # --dry-plan runs from the same inputs, spends nothing
        dp = subprocess.run([sys.executable, RUNNER, "--out-dir", tmp,
                             "--dry-plan"], capture_output=True, text=True)
        if dp.returncode != 0:
            fail("--dry-plan rc=%d\n%s%s" % (dp.returncode, dp.stdout, dp.stderr))
        print("ok: --dry-plan runs and all caps check OK")

    print("\nF2 MOCK SMOKE: ALL CHECKS PASSED ($0 spent, no GPU, no network)")


if __name__ == "__main__":
    main()
