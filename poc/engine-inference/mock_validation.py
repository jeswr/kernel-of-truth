#!/usr/bin/env python3
# ENGINE-INF $0 mock validation (REVISION-1/2/3 build) — exercises the FULL
# mechanics chain on synthetic fixtures with hand-computed expected outputs,
# plus the pinned analysis script end-to-end through its stdin run-record
# contract, so the verdict path (verdict-gen step 5) is validated before
# freeze without touching campaign semantics. MOCK artifacts validate
# mechanics ONLY and never satisfy the pilot/freeze gate (protocol §3).
#
#   MV-1 engine adapter: CONSISTENT / ANOMALOUS / REFUSE verdicts on a
#        synthetic 2-class TBox exactly as hand-predicted
#   MV-2 scorer table: every (gold, verdict, derived) combination incl. the
#        ASM-1997/2116 G4 rule (vacuous CONSISTENT correct; CONSISTENT with
#        a derived class = confident wrong assertion) and honesty penalties
#   MV-3 statistics helpers on known values (descriptive only under R2)
#   MV-4 analysis script: synthetic PASS-shaped and DEFLATE-shaped row +
#        orbit-row sets drive band_pass_affirm / band_fail_deflate
#        respectively on a synthetic BINDING (frame=H, h_star) input; all
#        declared output_fields present; sha-pinned stdin contract enforced
#        (a wrong sha must fail closed); the deflate shape must also drive
#        the C-SHUF CONTENT-INERT flag (identity beaten by the orbit)

import hashlib
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
ARMS = ("K", "K-lemma-dom", "K-lemma-union", "D-word-dom", "D-word-union",
        "B-wn", "oracle")
N_ORBIT = 960

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
    # (gold, verdict, derived_cls) -> (correct, penalty); ASM-2116: on gold
    # REFUSE, CONSISTENT is correct IFF the derived-class set is empty
    expect = {
        ("CONSISTENT", "CONSISTENT", ()): (True, 0.0),
        ("CONSISTENT", "ANOMALOUS", ()): (False, 1.0),
        ("CONSISTENT", "REFUSE", ()): (False, 0.5),
        ("ANOMALOUS", "ANOMALOUS", ()): (True, 0.0),
        ("ANOMALOUS", "ANOMALOUS", ("urn:mock:cls:A",)): (True, 0.0),
        ("ANOMALOUS", "CONSISTENT", ()): (False, 1.0),
        ("ANOMALOUS", "REFUSE", ()): (False, 0.5),
        ("REFUSE", "REFUSE", ()): (True, 0.0),
        ("REFUSE", "CONSISTENT", ()): (True, 0.0),   # true vacuity
        ("REFUSE", "CONSISTENT", ("urn:mock:cls:A",)): (False, 1.0),
        ("REFUSE", "ANOMALOUS", ()): (False, 1.0),   # confident wrong
        ("REFUSE", "ANOMALOUS", ("urn:mock:cls:A",)): (False, 1.0),
    }
    ok = all(score({"verdict": g}, v, list(d)) == e
             for (g, v, d), e in expect.items())
    two_arg_ok = score({"verdict": "REFUSE"}, "CONSISTENT") == (True, 0.0)
    check("mv2-scorer-table", ok and two_arg_ok)


def mv3_stats():
    check("mv3-wilson", abs(wilson_lb(858, 858) - 0.9955) < 0.001,
          "%f" % wilson_lb(858, 858))
    check("mv3-cp-zero", clopper_pearson_lb(0, 10) == 0.0)
    lb = clopper_pearson_lb(10, 10)
    check("mv3-cp-perfect", 0.73 < lb < 0.75, "%f" % lb)


def synth_rows(shape):
    """Synthetic BINDING-frame fixtures (frame=H, h_star=true, one item per
    cell). 'pass': K wins every co-primary divergent cell across >= 2
    lemmas (deltas 1.0, floors 1.0, DIST-SPAN holds). 'deflate': K false-
    conflicts nothing but asserts CONSISTENT on gold-ANOMALOUS cells while
    K-lemma and B-wn get them right -> EP-A and EP-B deltas negative
    (FAIL-A + FAIL-B)."""
    rows = []
    lemmas = ("break", "find", "make")
    for i in range(30):  # G3 anomaly cells (op O2)
        gold = "ANOMALOUS"
        kv = "ANOMALOUS" if shape == "pass" else "CONSISTENT"
        av = "CONSISTENT" if shape == "pass" else "ANOMALOUS"
        cell = "mock:syn%02d|abst|mock:kind|anomaly" % i
        for arm in ARMS:
            v = {"K": kv, "K-lemma-dom": av, "K-lemma-union": av,
                 "D-word-dom": av, "D-word-union": av, "B-wn": av,
                 "oracle": gold}[arm]
            rows.append({"item": "m-anom-%02d" % i, "kind": "anomaly",
                         "lemma": lemmas[i % 3], "cell": cell, "frame": "H",
                         "h_star": True, "gold_rule": "G3",
                         "gold_verdict": gold, "arm": arm, "relation": "r",
                         "verdict": v,
                         "refusal": "ERR_CONFLICT" if v == "ANOMALOUS" else None,
                         "derived_cls": [],
                         "derived_sides": ["abst"] if arm == "K" else [],
                         "correct": v == gold,
                         "honesty_penalty": 0.0 if v == gold else 1.0})
    for i in range(10):  # G4 refusal cells (secondary only)
        cell = "mock:ref%02d|abst|mock:kind|refusal" % i
        for arm in ARMS:
            v = "REFUSE" if arm in ("K", "oracle") else "CONSISTENT"
            rows.append({"item": "m-ref-%02d" % i, "kind": "refusal",
                         "lemma": lemmas[i % 3], "cell": cell, "frame": "H",
                         "h_star": True, "gold_rule": "G4",
                         "gold_verdict": "REFUSE", "arm": arm, "relation": "r",
                         "verdict": v, "refusal":
                             "ERR_INSUFFICIENT_PREMISES" if v == "REFUSE" else None,
                         "derived_cls": [], "derived_sides": [],
                         "correct": True, "honesty_penalty": 0.0})
    for i in range(10):  # G1 attested cells (op O1), all arms convergent
        cell = "mock:att%02d|phys|mock:kind|attested" % i
        for arm in ARMS:
            rows.append({"item": "m-att-%02d" % i, "kind": "attested",
                         "lemma": lemmas[i % 3], "cell": cell, "frame": "H",
                         "h_star": True, "gold_rule": "G1+G2",
                         "gold_verdict": "CONSISTENT", "arm": arm,
                         "relation": "r", "verdict": "CONSISTENT",
                         "refusal": None, "derived_cls": [],
                         "derived_sides": [], "correct": True,
                         "honesty_penalty": 0.0})
    return rows


def synth_orbit(shape, rows):
    """Synthetic 960-member orbit rows over the fixture's G1∪G3 cells.
    Member 0 must reproduce the K arm (analysis consistency gate). 'pass':
    every non-identity member asserts CONSISTENT (wrong, but typing-active
    via derived_sides) on the anomaly cells -> p = 1/960. 'deflate': every
    non-identity member is ANOMALOUS (right) where K was wrong -> p = 1.0
    -> CONTENT-INERT."""
    k_rows = {r["cell"]: r for r in rows
              if r["arm"] == "K" and r["gold_rule"] in ("G1+G2", "G3")}
    orows = []
    for m in range(N_ORBIT):
        for cell, kr in sorted(k_rows.items()):
            if m == 0:
                v, ds = kr["verdict"], kr["derived_sides"]
            elif kr["kind"] == "anomaly":
                v = "CONSISTENT" if shape == "pass" else "ANOMALOUS"
                ds = ["abst"]
            else:
                v, ds = "CONSISTENT", []
            orows.append({"m": m, "cell": cell, "verdict": v,
                          "refusal": "ERR_CONFLICT" if v == "ANOMALOUS" else None,
                          "derived_sides": ds,
                          "gold_verdict": kr["gold_verdict"]})
    return orows


def mv4_analysis(tmp):
    declared = json.load(open(HERE / "output-fields.json"))
    results = {}
    for shape in ("pass", "deflate"):
        rows = synth_rows(shape)
        orows = synth_orbit(shape, rows)
        rows_path = tmp / ("mock-rows-%s.jsonl" % shape)
        orows_path = tmp / ("mock-orbit-%s.jsonl" % shape)
        with open(rows_path, "w") as f:
            for r in rows:
                f.write(json.dumps(r, sort_keys=True) + "\n")
        with open(orows_path, "w") as f:
            for r in orows:
                f.write(json.dumps(r, sort_keys=True) + "\n")
        rec = {"event": "run", "phase": "final", "exit": "ok",
               "artifacts": {
                   "rows_path": str(rows_path),
                   "rows_sha256":
                       hashlib.sha256(rows_path.read_bytes()).hexdigest(),
                   "orbit_rows_path": str(orows_path),
                   "orbit_rows_sha256":
                       hashlib.sha256(orows_path.read_bytes()).hexdigest()}}
        proc = subprocess.run([sys.executable, str(ANALYSIS)],
                              input=json.dumps(rec) + "\n",
                              capture_output=True, text=True)
        check("mv4-%s-exit0" % shape, proc.returncode == 0, proc.stderr[:300])
        if proc.returncode != 0:
            continue
        doc = json.loads(proc.stdout)
        missing = [f for f in declared if _resolve(doc, f) is None]
        check("mv4-%s-fields" % shape, not missing, str(missing))
        results[shape] = doc
        # fail-closed sha check: corrupt the pin
        rec_bad = dict(rec, artifacts=dict(rec["artifacts"],
                                           rows_sha256="0" * 64))
        proc_bad = subprocess.run([sys.executable, str(ANALYSIS)],
                                  input=json.dumps(rec_bad) + "\n",
                                  capture_output=True, text=True)
        check("mv4-%s-sha-fail-closed" % shape, proc_bad.returncode == 1)
    if "pass" in results:
        a = results["pass"]["analysis"]
        check("mv4-band-pass",
              a["band_pass_affirm"] is True
              and a["band_fail_deflate"] is False
              and a["binding"] is True
              and a["kill_e1_fired"] is False
              and a["kill_e2a_fired"] is False
              and a["kill_e2b_fired"] is False
              and a["cshuf_orbit_p"] == 1.0 / N_ORBIT
              and a["ep_a_dom"]["dist_span_ok"] is True,
              json.dumps({k: a[k] for k in ("band_pass_affirm",
                                            "ep_a_delta_dom", "ep_b_delta",
                                            "cshuf_orbit_p")}))
    if "deflate" in results:
        a = results["deflate"]["analysis"]
        check("mv4-band-deflate",
              a["band_fail_deflate"] is True
              and a["band_pass_affirm"] is False
              and a["fail_a"] is True and a["fail_b"] is True
              and a["content_inert_flag"] is True,
              json.dumps({k: a[k] for k in ("band_fail_deflate",
                                            "ep_a_delta_dom", "ep_b_delta",
                                            "cshuf_orbit_p")}))


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
        "emitted_by": "writer-5",
    }, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"mock_pass": ok,
                      "checks": {c["name"]: c["pass"] for c in checks}},
                     indent=1, sort_keys=True))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
