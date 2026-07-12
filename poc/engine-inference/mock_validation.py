#!/usr/bin/env python3
# ENGINE-INF $0 mock validation — exercises the FULL mechanics chain on
# synthetic fixtures with hand-computed expected outputs, plus the pinned
# analysis script end-to-end through its stdin run-record contract, so the
# verdict path (verdict-gen step 5) is validated before freeze without
# touching campaign semantics. MOCK artifacts validate mechanics ONLY and
# never satisfy the pilot/freeze gate (protocol §3 mode rule).
#
#   MV-1 engine adapter: CONSISTENT / ANOMALOUS / REFUSE verdicts on a
#        synthetic 2-class TBox exactly as hand-predicted
#   MV-2 scorer table: every (gold, verdict) combination incl. the ASM-1997
#        G4 rule and honesty penalties
#   MV-3 divergence signatures + statistics (Wilson / Clopper-Pearson on
#        known values)
#   MV-4 analysis script: synthetic PASS-shaped and DEFLATE-shaped row sets
#        drive band_pass_affirm / band_fail_deflate respectively; all
#        declared output_fields present; sha-pinned stdin contract enforced
#        (a wrong rows sha must fail closed)

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from engineinf_lib import (Closure, canon_sha, clopper_pearson_lb, load_tbox,
                           score, wilson_lb, ROOT)

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
ANALYSIS = ROOT / "analysis" / "engine_inference_stdin.py"
ARMS = ("K", "K-shuf", "D-word-dom", "D-word-union", "B-wn", "oracle")

checks = []


def check(name, ok, detail=""):
    checks.append({"name": name, "pass": bool(ok), "detail": detail})
    if not ok:
        print("MOCK FAIL: %s %s" % (name, detail), file=sys.stderr)


def mv1_engine(tmp):
    d = tmp / "tbox"
    d.mkdir()
    A, B = "urn:mock:cls:A", "urn:mock:cls:B"
    R = "urn:mock:rel:r"
    (d / "a.json").write_text(json.dumps(
        {"schema": "kot-axiom/1", "subject": A,
         "constraints": [{"kind": "classDeclaration"},
                         {"kind": "disjointWith", "target": B}]}))
    (d / "r.json").write_text(json.dumps(
        {"schema": "kot-axiom/1", "subject": R,
         "constraints": [{"kind": "range", "target": A}]}))
    tb = load_tbox([d])
    # consistent world: object already A
    cl = Closure(tb, [("rel", "x", R, "y"), ("cls", "y", A)])
    check("mv1-consistent", not cl.conflicts and ("cls", "y", A) in cl.facts())
    # anomalous world: object stated B, R derives A, A disjoint B
    cl2 = Closure(tb, [("rel", "x", R, "y"), ("cls", "y", B)])
    check("mv1-anomalous", len(cl2.conflicts) == 1
          and cl2.conflicts[0]["rule"] == "CAX-DW")
    # untyped relation: nothing derived
    cl3 = Closure(tb, [("rel", "x", "urn:mock:rel:untyped", "y"),
                       ("cls", "y", B)])
    check("mv1-vacuous", not cl3.conflicts and len(cl3.derived()) == 0)


def mv2_scorer():
    expect = {
        ("CONSISTENT", "CONSISTENT"): (True, 0.0),
        ("CONSISTENT", "ANOMALOUS"): (False, 1.0),
        ("CONSISTENT", "REFUSE"): (False, 0.5),
        ("ANOMALOUS", "ANOMALOUS"): (True, 0.0),
        ("ANOMALOUS", "CONSISTENT"): (False, 1.0),
        ("ANOMALOUS", "REFUSE"): (False, 0.5),
        ("REFUSE", "REFUSE"): (True, 0.0),
        ("REFUSE", "CONSISTENT"): (True, 0.0),   # vacuity is not wrongness
        ("REFUSE", "ANOMALOUS"): (False, 1.0),   # confident wrong assertion
    }
    ok = all(score({"verdict": g}, v) == e for (g, v), e in expect.items())
    check("mv2-scorer-table", ok)


def mv3_stats():
    check("mv3-wilson", abs(wilson_lb(858, 858) - 0.9955) < 0.001,
          "%f" % wilson_lb(858, 858))
    check("mv3-cp-zero", clopper_pearson_lb(0, 10) == 0.0)
    lb = clopper_pearson_lb(10, 10)
    check("mv3-cp-perfect", 0.73 < lb < 0.75, "%f" % lb)


def synth_rows(shape):
    """Synthetic row sets: 'pass' -> K wins the divergent frame;
    'deflate' -> B-wn matches/beats K."""
    rows = []
    lemmas = ("break", "find", "make")
    for i in range(30):  # G3 anomaly cells, K vs baselines divergent (O1+O2)
        gold = "ANOMALOUS"
        kv = "ANOMALOUS" if shape == "pass" else "CONSISTENT"
        bv = "CONSISTENT" if shape == "pass" else "ANOMALOUS"
        for arm in ARMS:
            v = {"K": kv, "K-shuf": "CONSISTENT", "D-word-dom": "CONSISTENT",
                 "D-word-union": "CONSISTENT", "B-wn": bv, "oracle": gold}[arm]
            rows.append({"item": "m-anom-%02d" % i, "kind": "anomaly",
                         "lemma": lemmas[i % 3], "gold_rule": "G3",
                         "gold_verdict": gold, "arm": arm, "relation": "r",
                         "verdict": v, "refusal": None,
                         "derived_cls": [],
                         "derived_sides": ["abst"] if arm == "K" else [],
                         "correct": v == gold or (gold == "REFUSE" and v == "CONSISTENT"),
                         "honesty_penalty": 0.0 if v == gold else 1.0})
    for i in range(10):  # G4 refusal cells (O3 divergence)
        for arm in ARMS:
            v = "REFUSE" if arm in ("K", "K-shuf", "oracle") else "CONSISTENT"
            rows.append({"item": "m-ref-%02d" % i, "kind": "refusal",
                         "lemma": lemmas[i % 3], "gold_rule": "G4",
                         "gold_verdict": "REFUSE", "arm": arm, "relation": "r",
                         "verdict": v, "refusal":
                             "ERR_INSUFFICIENT_PREMISES" if v == "REFUSE" else None,
                         "derived_cls": [], "derived_sides": [],
                         "correct": True, "honesty_penalty": 0.0})
    for i in range(10):  # attested cells; in the deflate shape the first 5
        # are K false-conflicts (realistic O2 divergence source vs D-dom)
        k_false = shape == "deflate" and i < 5
        for arm in ARMS:
            v = "ANOMALOUS" if (arm == "K" and k_false) else "CONSISTENT"
            rows.append({"item": "m-att-%02d" % i, "kind": "attested",
                         "lemma": lemmas[i % 3], "gold_rule": "G1+G2",
                         "gold_verdict": "CONSISTENT", "arm": arm,
                         "relation": "r", "verdict": v,
                         "refusal": "ERR_CONFLICT" if v == "ANOMALOUS" else None,
                         "derived_cls": [],
                         "derived_sides": [], "correct": v == "CONSISTENT",
                         "honesty_penalty": 0.0 if v == "CONSISTENT" else 1.0})
    return rows


def mv4_analysis(tmp):
    declared = json.load(open(HERE / "output-fields.json"))
    results = {}
    for shape in ("pass", "deflate"):
        rows = synth_rows(shape)
        rows_path = tmp / ("mock-rows-%s.jsonl" % shape)
        with open(rows_path, "w") as f:
            for r in rows:
                f.write(json.dumps(r, sort_keys=True) + "\n")
        import hashlib
        sha = hashlib.sha256(rows_path.read_bytes()).hexdigest()
        rec = {"event": "run", "phase": "final", "exit": "ok",
               "artifacts": {"rows_path": str(rows_path.relative_to(ROOT))
                             if str(rows_path).startswith(str(ROOT))
                             else str(rows_path),
                             "rows_sha256": sha}}
        # analysis resolves rows_path relative to ROOT; use absolute-safe path
        rec["artifacts"]["rows_path"] = str(rows_path)
        proc = subprocess.run([sys.executable, str(ANALYSIS)],
                              input=json.dumps(rec) + "\n",
                              capture_output=True, text=True)
        check("mv4-%s-exit0" % shape, proc.returncode == 0, proc.stderr[:300])
        if proc.returncode != 0:
            continue
        doc = json.loads(proc.stdout)
        missing = [f for f in declared
                   if _resolve(doc, f) is None]
        check("mv4-%s-fields" % shape, not missing, str(missing))
        results[shape] = doc
        # fail-closed sha check: corrupt the pin
        rec_bad = dict(rec, artifacts=dict(rec["artifacts"], rows_sha256="0" * 64))
        proc_bad = subprocess.run([sys.executable, str(ANALYSIS)],
                                  input=json.dumps(rec_bad) + "\n",
                                  capture_output=True, text=True)
        check("mv4-%s-sha-fail-closed" % shape, proc_bad.returncode == 1)
    if "pass" in results:
        a = results["pass"]["analysis"]
        check("mv4-band-pass", a["band_pass_affirm"] is True
              and a["band_fail_deflate"] is False
              and a["kill_e1_fired"] is False and a["kill_e2_fired"] is False,
              json.dumps({k: a[k] for k in ("band_pass_affirm",
                                            "k_pri_wilson_lb95",
                                            "delta_k_minus_bwn_pri")}))
    if "deflate" in results:
        a = results["deflate"]["analysis"]
        check("mv4-band-deflate", a["band_fail_deflate"] is True
              and a["band_pass_affirm"] is False,
              json.dumps({k: a[k] for k in ("band_fail_deflate",
                                            "delta_k_minus_bwn_pri")}))


def _resolve(doc, pointer):
    node = doc
    for tok in pointer.lstrip("/").split("/"):
        if not isinstance(node, dict) or tok not in node:
            return None
        node = node[tok]
    return node


def main():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        mv1_engine(tmp)
        mv2_scorer()
        mv3_stats()
        mv4_analysis(tmp)
    ok = all(c["pass"] for c in checks)
    OUT.mkdir(exist_ok=True)
    (OUT / "mock-validation.json").write_text(json.dumps({
        "schema": "kot-engineinf-mock/1",
        "mode": "MOCK",
        "role": ("harness-mechanics validation at $0; MOCK artifacts "
                 "validate mechanics only and NEVER satisfy the pilot or "
                 "freeze gates (blocking-pilot protocol §3)"),
        "pass": ok,
        "checks": checks,
        "cost_usd": 0.0,
        "emitted_by": "writer-4",
    }, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"mock_pass": ok,
                      "checks": {c["name"]: c["pass"] for c in checks}},
                     indent=1, sort_keys=True))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
