#!/usr/bin/env python3
"""Independent assertions over an E9-defl mock run + the pre-registered
planted-effect and null controls (poc/e9/README.md "Controls before real
spend"; bead kernel-of-truth-xj2).

    python3 check_smoke.py <out-dir>
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.normpath(os.path.join(_HERE, "..", "..", "e5", "runner")))
import e5_runner as e5  # noqa: E402

ARMS = ["true", "shuffled", "defl"]


def indep_signflip_p_int(diffs):
    dist = {0: 1}
    for d in diffs:
        new = {}
        for v, c in dist.items():
            for s in (v + d, v - d):
                new[s] = new.get(s, 0) + c
        dist = new
    obs = sum(diffs)
    return sum(c for v, c in dist.items() if v >= obs) / float(2 ** len(diffs))


def main() -> None:
    out_dir = sys.argv[1]
    checks = 0

    # ---- planted-effect control (analytic): all-positive diffs => exact 2^-n --
    for n in (10, 24):
        planted = [1] * n
        assert e5.exact_signflip_p_int(planted) == 0.5 ** n
        assert indep_signflip_p_int(planted) == 0.5 ** n
        checks += 2
    # magnitude-weighted planted case, verified against the independent impl
    planted2 = [5, 3, 2, 4, 1, 5, 2, 3, 4, 5, 1, 2] * 2
    assert abs(e5.exact_signflip_p_int(planted2) - indep_signflip_p_int(planted2)) < 1e-15
    checks += 1

    # ---- null controls (analytic): no effect => no rejection ------------------
    assert e5.exact_signflip_p_int([0] * 24) == 1.0          # exactly-null diffs
    sym = [1, -1] * 12                                        # sign-symmetric
    p_sym = e5.exact_signflip_p_int(sym)
    assert abs(p_sym - indep_signflip_p_int(sym)) < 1e-15 and p_sym > 0.05
    rng = np.random.default_rng(20260707)                     # fixed-seed exchangeable null
    null_rejections = 0
    for _ in range(20):
        diffs = [int(d) for d in rng.integers(-3, 4, size=24)]
        p = e5.exact_signflip_p_int(diffs)
        assert abs(p - indep_signflip_p_int(diffs)) < 1e-12
        null_rejections += (p < 0.05) and (sum(diffs) > 0)
    assert null_rejections <= 3, f"null control rejected {null_rejections}/20 times"
    checks += 23

    # ---- mock-run re-derivation ------------------------------------------------
    with open(os.path.join(out_dir, "results-e9-mock.json")) as f:
        res = json.load(f)
    assert res["outcome"].startswith("MOCK-") and res["mode"] == "MOCK"
    seeds = res["seeds"]
    for key, summ in res["armSeed"].items():
        with open(os.path.join(out_dir, f"eval-items-{key}.json")) as f:
            recs = json.load(f)
        assert abs(float(np.mean([r["correct"] for r in recs["nonce"]])) - summ["nonceAcc"]) < 1e-12
        assert abs(float(np.mean([r["correct"] for r in recs["seen"]])) - summ["seenAcc"]) < 1e-12
        for r in recs["seen"] + recs["nonce"]:
            best = max(r["scores"])
            assert r["correct"] == ((r["scores"][0] == best) and (r["scores"].count(best) == 1))
        assert os.path.exists(os.path.join(out_dir, f"adapter-{key}.npz"))
        checks += 3 + len(recs["seen"]) + len(recs["nonce"])

    nonces = None
    counts = {}
    for arm in ARMS:
        for s in seeds:
            with open(os.path.join(out_dir, f"eval-items-{arm}-seed{s}.json")) as f:
                recs = json.load(f)["nonce"]
            if nonces is None:
                nonces = sorted({r["concept"] for r in recs})
            counts[(arm, s)] = {c: sum(1 for r in recs if r["concept"] == c and r["correct"])
                                for c in nonces}

    def diffs(a, b):
        return [sum(counts[(a, s)][c] - counts[(b, s)][c] for s in seeds) for c in nonces]

    d_td, d_ds = diffs("true", "defl"), diffs("defl", "shuffled")
    assert d_td == res["primary"]["intDiffs"]
    assert d_ds == res["secondaries"]["S1_defl_vs_shuffled"]["intDiffs"]
    assert abs(indep_signflip_p_int(d_td) - res["primary"]["p"]) < 1e-12
    assert abs(indep_signflip_p_int(d_ds) - res["secondaries"]["S1_defl_vs_shuffled"]["p"]) < 1e-12
    checks += 4

    sm = res["secondaries"]["S2_seedlevel_true_vs_defl"]["seedMeanDiffs"]
    obs = sum(sm)
    cnt = sum(1 for m in range(1 << len(seeds))
              if sum((d if (m >> i) & 1 else -d) for i, d in enumerate(sm)) >= obs - 1e-12)
    assert abs(cnt / (1 << len(seeds)) - res["secondaries"]["S2_seedlevel_true_vs_defl"]["p"]) < 1e-12
    checks += 1

    # gate + pinned outcome logic, re-derived independently
    gate_ok = sum(g["pass"] for g in res["instrumentValidityGate"]["perSeed"]) >= res[
        "instrumentValidityGate"]["needed"]
    assert gate_ok == res["instrumentValidityGate"]["passed"]
    pr = res["primary"]
    s1 = res["secondaries"]["S1_defl_vs_shuffled"]
    if not gate_ok:
        expect = "INSTRUMENT-INVALID"
    elif pr["p"] < 0.05 and pr["meanDiff"] > 0:
        expect = "PASS"
    elif s1["p"] < 0.05 and s1["meanDiff"] > 0:
        expect = "DEFLATED"
    else:
        expect = "AMBIGUOUS-NULL"
    assert res["outcome"] == f"MOCK-{expect}", (res["outcome"], expect)
    assert res["paramChecksum"]["before"] == res["paramChecksum"]["after"]
    checks += 3

    # verdict quotes the pre-registered strings verbatim
    with open(os.path.join(out_dir, "verdict-e9-mock.md")) as f:
        md = f.read()
    assert res["statisticsSpec"]["primaryEndpoint"] in md
    assert res["statisticsSpec"]["outcomes"] in md
    assert res["spec"] in md
    checks += 3

    print(f"check_smoke(e9): PASS ({checks} assertions incl. planted + null controls) "
          f"— outcome {res['outcome']}")


if __name__ == "__main__":
    main()
