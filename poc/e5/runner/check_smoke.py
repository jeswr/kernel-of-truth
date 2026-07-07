#!/usr/bin/env python3
"""Independent assertions over an E5 mock run's outputs (bead
kernel-of-truth-c24) — poc/e1/e4 house practice: the smoke is only evidence
if a SEPARATE script re-derives the numbers from the shipped per-item records
and re-implements the statistics with a different construction.

    python3 check_smoke.py <out-dir>
"""

from __future__ import annotations

import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e5_runner  # noqa: E402  (function-level checks against known values)


def indep_signflip_p_int(diffs: list[int]) -> float:
    """Independent implementation: dict-based convolution (vs the runner's
    numpy lattice)."""
    dist = {0: 1}
    for d in diffs:
        new: dict[int, int] = {}
        for v, c in dist.items():
            for s in (v + d, v - d):
                new[s] = new.get(s, 0) + c
        dist = new
    obs = sum(diffs)
    return sum(c for v, c in dist.items() if v >= obs) / float(2 ** len(diffs))


def indep_binom_sf(k: int, n: int, p: float) -> float:
    """Independent binomial tail: iterative pmf recursion."""
    if k <= 0:
        return 1.0
    pmf = (1 - p) ** n
    total = pmf if 0 >= k else 0.0
    for i in range(1, n + 1):
        pmf *= (n - i + 1) / i * p / (1 - p)
        if i >= k:
            total += pmf
    return min(1.0, total)


def main() -> None:
    out_dir = sys.argv[1]
    with open(os.path.join(out_dir, "results-e5-mock.json")) as f:
        res = json.load(f)
    assert res["outcome"].startswith("MOCK-"), "mock outcome must be MOCK-labelled"
    assert res["mode"] == "MOCK"
    seeds = res["seeds"]
    checks = 0

    # 1) runner statistics functions against known exact values ---------------
    assert e5_runner.exact_signflip_p_int([1] * 10) == 1 / 1024
    assert e5_runner.exact_signflip_p_int([2, -2]) == 0.75  # sums {-4,0,0,4} >= 0
    assert e5_runner.exact_signflip_p_int([0, 3]) == 0.5    # {-3,-3,3,3} >= 3
    assert abs(e5_runner.binom_sf_geq(3, 10, 0.5) - 0.9453125) < 1e-9
    assert e5_runner.exact_signflip_p_float([0.5, 0.5]) == 0.25
    checks += 5

    # 2) accuracies re-derived from shipped per-item records ------------------
    for key, summ in res["armSeed"].items():
        with open(os.path.join(out_dir, f"eval-items-{key}.json")) as f:
            recs = json.load(f)
        seen_acc = float(np.mean([r["correct"] for r in recs["seen"]]))
        nonce_acc = float(np.mean([r["correct"] for r in recs["nonce"]]))
        assert abs(seen_acc - summ["seenAcc"]) < 1e-12, key
        assert abs(nonce_acc - summ["nonceAcc"]) < 1e-12, key
        assert summ["seenCorrect"] == sum(r["correct"] for r in recs["seen"])
        # per-item invariants: 5 scores, margin consistent, correct = strict argmax
        for r in recs["seen"] + recs["nonce"]:
            assert len(r["scores"]) == 5
            best = max(r["scores"])
            expect = (r["scores"][0] == best) and (r["scores"].count(best) == 1)
            assert r["correct"] == expect
            assert abs(r["margin"] - (r["scores"][0] - max(r["scores"][1:]))) < 1e-9
        checks += 4 + len(recs["seen"]) + len(recs["nonce"])

    # 3) primary/secondary p re-derived independently -------------------------
    nonces = sorted(res["perNonce"].keys())
    diffs = []
    for c in nonces:
        dj = 0
        for s in seeds:
            for arm, sign in (("true", 1), ("shuffled", -1)):
                with open(os.path.join(out_dir, f"eval-items-{arm}-seed{s}.json")) as f:
                    recs = json.load(f)["nonce"]
                dj += sign * sum(1 for r in recs if r["concept"] == c and r["correct"])
        diffs.append(dj)
    assert diffs == res["primary"]["intDiffs"], "per-nonce integer diffs re-derived"
    p_ind = indep_signflip_p_int(diffs)
    assert abs(p_ind - res["primary"]["p"]) < 1e-12, f"primary p {p_ind} vs {res['primary']['p']}"
    checks += 2

    obs = sum(res["secondary"]["seedMeanDiffs"])
    count = sum(
        1 for m in range(1 << len(seeds))
        if sum((d if (m >> i) & 1 else -d) for i, d in enumerate(res["secondary"]["seedMeanDiffs"]))
        >= obs - 1e-12
    )
    assert abs(count / (1 << len(seeds)) - res["secondary"]["p"]) < 1e-12
    checks += 1

    # 4) gate re-derived -------------------------------------------------------
    for g in res["instrumentValidityGate"]["perSeed"]:
        p = indep_binom_sf(g["seenCorrect"], g["seenN"], 0.2)
        assert abs(p - g["p"]) < 1e-9
        assert g["pass"] == (g["p"] < 0.05)
        checks += 2
    gate_ok = sum(g["pass"] for g in res["instrumentValidityGate"]["perSeed"]) >= res[
        "instrumentValidityGate"]["needed"]
    assert gate_ok == res["instrumentValidityGate"]["passed"]

    # 5) verdict consistency ---------------------------------------------------
    base = res["outcome"].removeprefix("MOCK-")
    if not gate_ok:
        assert base == "INSTRUMENT-INVALID"
    elif res["primary"]["p"] < 0.05 and res["primary"]["meanDiff"] > 0:
        assert base == "PASS"
    else:
        assert base == "FAIL"
    checks += 1

    # 6) frozen model + adapters ------------------------------------------------
    assert res["paramChecksum"]["before"] == res["paramChecksum"]["after"], "model frozen"
    for key in res["armSeed"]:
        z = np.load(os.path.join(out_dir, f"adapter-{key}.npz"))
        assert z["W"].shape[1] == 576 and z["b"].ndim == 1
        checks += 1

    # 7) verdict md quotes the pre-registered criteria verbatim -----------------
    with open(os.path.join(out_dir, "verdict-e5-mock.md")) as f:
        md = f.read()
    assert res["specVerbatim"] in md
    assert res["statisticsSpec"]["successCriterion"] in md
    assert res["statisticsSpec"]["primaryEndpoint"] in md
    checks += 3

    print(f"check_smoke: PASS ({checks} assertions) — outcome {res['outcome']}")


if __name__ == "__main__":
    main()
