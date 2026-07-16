#!/usr/bin/env python3
"""HOLD round-4 REAL-seam round-trip (build artifact, uncommitted evidence).

Runs the OFFICIAL f1k ingestion seam end-to-end in a sandboxed repo root
using the ACTUAL refrozen record + the REAL CLIs (log-append, verdict-gen)
+ the REAL pinned analysis/f1k.py:

  1. valid mock-A campaign (planted +10-pt lift, all-true sidecar)
       -> verdict PASS-PENDING-AUDIT (paired_artifacts_verified disclosed);
  2. VALUE defect  — guard.byte_identical = false (bool, attested failure)
       -> INSTRUMENT-INVALID (rule 0), never PASS;
  3. NESTED structural defect — power.mc_intersection = {"bogus": 1}
       -> ERR_P2_ANALYSIS abort, NO verdict of any kind;
  4. ROW defect — one row carries pass = "0" (string)
       -> ERR_P2_ANALYSIS abort, NO verdict;
  5. RECORD defect — metrics.rows_emitted off by one
       -> ERR_P2_ANALYSIS abort, NO verdict.

Each scenario gets a FRESH sandbox root so chains never interfere.
"""
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
f1k = __import__("f1k")

TOOLS = ROOT / "tools" / "registry"
FROZEN = json.loads((ROOT / "registry" / "frozen-index.json")
                    .read_text(encoding="utf-8"))["f1k"]

rng = random.Random(4242)
ROWS_A = f1k._mock_campaign({"b0": 0.70, "d0": 0.70, "d1-drng": 0.70,
                             "d2": 0.70, "d3-text": 0.71, "K": 0.80}, rng)


def sha256_file(p):
    import hashlib
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def make_root(mutate_side=None, mutate_rows=None, mutate_rec=None):
    td = Path(tempfile.mkdtemp(prefix="f1k-seam-"))
    for d in ("registry/schema", "registry/experiments", "results-log",
              "reports/auto", "analysis", "data/f1k-run"):
        (td / d).mkdir(parents=True, exist_ok=True)
    for s in ("kot-reg-1.json", "kot-reg-2.json", "kot-log-1.json",
              "kot-amend-1.json"):
        shutil.copy(ROOT / "registry" / "schema" / s,
                    td / "registry" / "schema" / s)
    shutil.copy(ROOT / "registry" / "experiments" / "f1k.json",
                td / "registry" / "experiments" / "f1k.json")
    (td / "registry" / "frozen-index.json").write_text(
        json.dumps({"f1k": FROZEN}), encoding="utf-8")
    shutil.copy(ROOT / "analysis" / "f1k.py", td / "analysis" / "f1k.py")

    rows = [dict(r) for r in ROWS_A]
    if mutate_rows:
        mutate_rows(rows)
    side = f1k._mock_sidecar()
    if mutate_side:
        mutate_side(side)
    rp = td / "data" / "f1k-run" / "rows.jsonl"
    sp = td / "data" / "f1k-run" / "sidecar.json"
    rp.write_text("\n".join(json.dumps(r) for r in rows) + "\n",
                  encoding="utf-8")
    sp.write_text(json.dumps(side), encoding="utf-8")
    body = {
        "event": "run", "phase": "final", "exit": "ok",
        "prereg_hash": FROZEN,
        "config": {"protocol": "f1k-main-campaign", "engine": "colibri",
                   "n_test_items": 1573, "r_drng_passes": 3},
        "metrics": {"rows_emitted": len(rows), "n_test_items": 1573},
        "artifacts": [
            {"path": "data/f1k-run/rows.jsonl", "sha256": sha256_file(rp),
             "role": "rows"},
            {"path": "data/f1k-run/sidecar.json", "sha256": sha256_file(sp),
             "role": "sidecar"}],
    }
    if mutate_rec:
        mutate_rec(body)
    p = subprocess.run(
        [sys.executable, str(TOOLS / "log-append.py"), "--experiment", "f1k",
         "--agent-id", "runner-1", "--record", "-", "--root", str(td),
         "--ts", "2026-07-16T03:00:00Z"],
        input=json.dumps(body), capture_output=True, text=True)
    assert p.returncode == 0, "log-append failed: %s" % p.stderr
    return td


def verdict_gen(td):
    return subprocess.run(
        [sys.executable, str(TOOLS / "verdict-gen.py"), "--experiment",
         "f1k", "--agent-id", "coordinator-1", "--root", str(td),
         "--computed-at", "2026-07-16T03:10:00Z"],
        capture_output=True, text=True)


def report(name, ok, detail):
    print("%s %-38s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        sys.exit(1)


# 1. valid -> PASS-PENDING-AUDIT
td = make_root()
p = verdict_gen(td)
v = json.loads((td / "registry" / "verdicts" / "f1k.json")
               .read_text(encoding="utf-8")) if p.returncode == 0 else {}
report("valid campaign", p.returncode == 0
       and v.get("verdict") == "PASS-PENDING-AUDIT"
       and v["inputs"]["paired_artifacts_verified"][0]["rows"]["rows"]
       == len(ROWS_A),
       "verdict=%s paired_verified=%s"
       % (v.get("verdict"),
          bool(v.get("inputs", {}).get("paired_artifacts_verified"))))
shutil.rmtree(td)

# 2. VALUE defect -> INSTRUMENT-INVALID
td = make_root(mutate_side=lambda s: s["guard"].update(
    {"byte_identical": False}))
p = verdict_gen(td)
v = json.loads((td / "registry" / "verdicts" / "f1k.json")
               .read_text(encoding="utf-8")) if p.returncode == 0 else {}
report("guard.byte_identical=false (value)", p.returncode == 0
       and v.get("verdict") == "INSTRUMENT-INVALID"
       and v.get("fired_rule_index") == 0,
       "verdict=%s rule=%s" % (v.get("verdict"), v.get("fired_rule_index")))
shutil.rmtree(td)


def expect_abort(name, td):
    p = verdict_gen(td)
    no_verdict = not (td / "registry" / "verdicts" / "f1k.json").exists()
    report(name, p.returncode != 0 and "ERR_P2_ANALYSIS" in p.stderr
           and no_verdict,
           "rc=%d no_verdict=%s stderr=%s"
           % (p.returncode, no_verdict,
              p.stderr.strip().splitlines()[-1][:150] if p.stderr else ""))
    shutil.rmtree(td)


# 3. nested structural defect
expect_abort('mc_intersection={"bogus":1} (nested)',
             make_root(mutate_side=lambda s: s["power"].update(
                 {"mc_intersection": {"bogus": 1}})))

# 4. row defect
expect_abort('row pass="0" (string, row schema)',
             make_root(mutate_rows=lambda rows: rows[0].update(
                 {"pass": "0"})))

# 5. record defect
expect_abort("metrics.rows_emitted off-by-one (record)",
             make_root(mutate_rec=lambda b: b["metrics"].update(
                 {"rows_emitted": len(ROWS_A) - 1})))

print("REAL-SEAM ROUND-TRIP: all 5 scenarios as specified.")
