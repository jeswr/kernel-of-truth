#!/usr/bin/env python3
"""f2b-replicate mock validation — runs the harness in --mock (stub LM, CPU,
$0) and verifies the FROZEN contracts end-to-end:

1. every arm level of registry/experiments/f2b-replicate.json ran and
   emitted a record (incl. the NEW shuffled-verify + gold-oracle arms);
2. record bodies pass the kot-log/1 raw-metrics lint (no derived stats);
3. piping the run-records into the PINNED analysis script
   (analysis/f2b_replicate.py, sha re-checked against the registry record)
   resolves EVERY field in pins.analysis_script.output_fields;
4. the P10 extraction-failure instrument gate is exercised in both
   directions (mock data passes; a constructed high-failure set flips it);
5. the separation gate resolves and PASSES on the planted stub-skill
   gradient (R1 0.4 vs R3 0.9);
6. the shuffled-verifier permutation is a recorded, seed-pinned DERANGEMENT
   whose sha matches the one emitted on every shuffled-arm record, and the
   mock accuracies order as the design predicts
   (verify > shuffled ~ alone; gold-oracle >= verify);
7. the FIXED ext pipeline emitted item_correct_external on the arms that
   carry it (the F2 ext_vector defect stays closed);
8. --dry-plan runs from the same inputs and every cap checks OK;
9. SAFETY BOUNDS (correction 1, registry/corrections/f2b-replicate/): every
   record from a normal run is exit:"ok"; every gold-oracle cell records
   gold_attempts_cap + the per-item gold_reached_within_cap vector; a
   too-small --cell-timeout-s and a too-small --max-gen-per-item BOTH
   self-terminate with rc!=0, ERR_CELL_TIMEOUT, and a FLUSHED exit:"timeout"
   record on disk (bounded termination, partials preserved, nothing
   fabricated).

Usage:  python3 poc/f2b/smoke/check_mock.py   (from anywhere; ~1 min, CPU)
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RUNNER = os.path.join(ROOT, "poc", "f2b", "runner", "f2b_runner.py")
ANALYSIS = os.path.join(ROOT, "analysis", "f2b_replicate.py")
REG = os.path.join(ROOT, "registry", "experiments", "f2b-replicate.json")

sys.path.insert(0, os.path.join(ROOT, "tools", "registry"))
import kot_common as kc  # noqa: E402

EXPECTED_ARMS = {
    "model-alone", "kernel-verify-retry", "shuffled-kernel-verify-retry",
    "gloss-self-verify-retry", "prm-verifier", "kernel-as-text",
    "gold-oracle-retry", "extraction-instrument",
}
EXT_ARMS = {"model-alone", "kernel-verify-retry",
            "shuffled-kernel-verify-retry", "kernel-as-text"}


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
        fail("analysis/f2b_replicate.py sha %s != registry pin %s"
             % (sha[:12], pin[:12]))
    print("ok: analysis/f2b_replicate.py matches the registry pin (%s...)" % sha[:12])

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
        records_path = os.path.join(tmp, "run-records-f2b-mock.jsonl")
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

        # FIXED ext pipeline: external vectors present on the arms that carry them
        for arm in sorted(EXT_ARMS):
            cells = [r for r in lines if r["config"]["arm"] == arm]
            if not any("item_correct_external" in r["metrics"] for r in cells):
                fail("arm %s emitted no item_correct_external (ext fix regressed)"
                     % arm)
        print("ok: item_correct_external present on %s" % sorted(EXT_ARMS))

        # shuffled permutation: recorded, seed-pinned, derangement, sha-consistent
        with open(os.path.join(tmp, "shuffle-map.json")) as f:
            smap = json.load(f)
        perm = smap["map_urn_to_record_of"]
        if any(u == v for u, v in perm.items()):
            fail("shuffle map has a fixed point")
        if sorted(perm) != sorted(perm.values()):
            fail("shuffle map is not a permutation")
        blob = json.dumps(perm, sort_keys=True, separators=(",", ":")).encode()
        map_sha = hashlib.sha256(blob).hexdigest()
        if map_sha != smap["sha256_of_map"]:
            fail("shuffle-map sha mismatch with recorded value")
        for r in lines:
            if r["config"]["arm"] == "shuffled-kernel-verify-retry":
                if r["metrics"].get("shuffle_permutation_sha256") != map_sha:
                    fail("shuffled-arm record carries a different permutation sha")
        print("ok: shuffled permutation is a recorded derangement over %d "
              "concepts (sha %s...)" % (len(perm), map_sha[:12]))

        # pipe through the pinned analysis; every frozen output field resolves
        with open(records_path) as f:
            an = subprocess.run([sys.executable, ANALYSIS], stdin=f,
                                capture_output=True, text=True)
        if an.returncode != 0:
            fail("analysis rc=%d\n%s" % (an.returncode, an.stderr[-3000:]))
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

        a = out["analysis"]
        if not out["gates"]["instrument_valid"]:
            fail("mock extraction gate should PASS (stub fail rate 2%)")
        if not out["gates"]["separation_valid"]:
            fail("mock separation gate should PASS (stub skills 0.4 vs 0.9)")
        print("ok: P10 + separation gates PASS on mock data "
              "(sep=%.3f, delta=%.3f, best_k=%s)"
              % (a["separation_gap"], a["effect_size"], a["best_retry_budget"]))
        # design-predicted mock ordering (stub-skill mechanics, not measurements)
        if not (a["acc_verify_bestk"] > a["acc_shuffled_bestk"] + 0.1):
            fail("mock verify (%.3f) does not dominate shuffled (%.3f) — "
                 "the structure control is not content-destroying"
                 % (a["acc_verify_bestk"], a["acc_shuffled_bestk"]))
        if not (a["gold_oracle_acc_bestk"] >= a["acc_verify_bestk"] - 0.05):
            fail("mock gold-oracle ceiling (%.3f) below verify (%.3f)"
                 % (a["gold_oracle_acc_bestk"], a["acc_verify_bestk"]))
        print("ok: mock arm ordering sane (verify %.3f > shuffled %.3f; "
              "gold %.3f >= verify)" % (a["acc_verify_bestk"],
                                        a["acc_shuffled_bestk"],
                                        a["gold_oracle_acc_bestk"]))

        # gate flips: replace iface records with a high-failure set
        flipped = [r for r in lines if r["config"]["arm"] != "extraction-instrument"]
        flipped.append({"config": {"arm": "extraction-instrument", "rung": "R1",
                                   "retry_budget": 0, "escalation_budget": 0,
                                   "seed": 0},
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

        # ---- SAFETY BOUNDS (correction 1) --------------------------------
        # normal run: every record exit:"ok"; gold cells carry the bounded-
        # diagnostic fields (cap + per-item reached-gold-within-cap vector)
        if any(r.get("exit") != "ok" for r in lines):
            fail("a normal mock run emitted a non-ok record")
        gold = [r for r in lines
                if r["config"]["arm"] == "gold-oracle-retry"]
        for r in gold:
            m = r["metrics"]
            cap = m.get("gold_attempts_cap")
            if not isinstance(cap, int) or cap < 1 or cap > 8:
                fail("gold-oracle cell without a sane gold_attempts_cap: %r"
                     % cap)
            if cap > r["config"]["retry_budget"] + 1:
                fail("gold_attempts_cap %d exceeds k+1=%d"
                     % (cap, r["config"]["retry_budget"] + 1))
            if m.get("gold_reached_within_cap") != m["item_correct"]:
                fail("gold_reached_within_cap != item_correct (construction "
                     "invariant broken)")
        print("ok: gold-oracle-retry is explicitly capped (caps %s) and "
              "records gold_reached_within_cap"
              % sorted({r["metrics"]["gold_attempts_cap"] for r in gold}))

        # breach paths: both bounds must self-terminate with rc!=0 and a
        # flushed exit:"timeout" record (bounded time, partials preserved)
        for flag, val, want_kind in (
                ("--cell-timeout-s", "0.000000001", "wall-clock"),
                ("--max-gen-per-item", "1", "max-generations-per-item")):
            bdir = os.path.join(tmp, "breach-%s" % want_kind)
            os.makedirs(bdir, exist_ok=True)
            br = subprocess.run(
                [sys.executable, RUNNER, "--out-dir", bdir, "--mock",
                 flag, val], capture_output=True, text=True)
            if br.returncode == 0:
                fail("%s %s did not abort the run" % (flag, val))
            if "ERR_CELL_TIMEOUT" not in br.stdout + br.stderr:
                fail("%s breach did not report ERR_CELL_TIMEOUT" % flag)
            with open(os.path.join(bdir, "run-records-f2b-mock.jsonl")) as f:
                brecs = [json.loads(l) for l in f if l.strip()]
            last = brecs[-1]
            if last.get("exit") != "timeout":
                fail("%s breach: last flushed record exit=%r, want 'timeout'"
                     % (flag, last.get("exit")))
            kind = last["metrics"]["cell_budget_exceeded"]["kind"]
            if want_kind not in kind:
                fail("%s breach recorded kind %r" % (flag, kind))
            if any(r.get("exit") != "ok" for r in brecs[:-1]):
                fail("a pre-breach record is not exit:'ok'")
            if "item_correct" in last["metrics"]:
                fail("timeout record carries item_correct (fabrication risk)")
        print("ok: both safety bounds self-terminate (rc!=0, "
              "ERR_CELL_TIMEOUT, flushed exit:'timeout' record, no "
              "fabricated items)")

    print("\nF2B-REPLICATE MOCK SMOKE: ALL CHECKS PASSED "
          "($0 spent, no GPU, no network)")


if __name__ == "__main__":
    main()
