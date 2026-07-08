#!/usr/bin/env python3
"""g8 pinned analysis — HS8 Lean-minting viability (P1 §4 HS8 / G8 = NF3).

Eligible run records on stdin; analysis-output JSON on stdout.

Input metric contract (counts summed over eligible records):
  metrics.n_mathlib_decls     random Mathlib declarations sampled (planned 1000; D-ML)
  metrics.n_in_fragment       declarations inside the mintable fragment
  metrics.n_location_targets  location-probe targets (math-v0 overlap set; planned 39)
  metrics.n_location_top5     verified LLM locations correct in top-5
  metrics.n_roundtrip         round-trip attempts on minted records
  metrics.n_roundtrip_fixed   round-trips reaching the fixed point
  metrics.n_llm_candidates    LLM-proposed candidate statements submitted to bridge F
  metrics.n_f_verified        candidates F actually verified

Output fields:
  /gates/instrument_valid   n_mathlib_decls >= 1000 AND n_location_targets >= 39
  /analysis/fragment_rate, /analysis/fragment_wilson_lb, /analysis/fragment_wilson_ub
  /analysis/location_rate, /analysis/location_wilson_lb, /analysis/location_wilson_ub
  /analysis/roundtrip_holds        bool (all attempts reach the fixed point, >=1 attempt)
  /analysis/f_verification_rate
  /analysis/n_mathlib_decls, /analysis/n_location_targets

Verdict mapping (frozen record): PASS iff fragment_wilson_lb > 0.01 AND
location_wilson_lb > 0.80 AND roundtrip_holds AND f_verification_rate >= 0.01;
FAIL iff fragment_wilson_ub <= 0.01 OR location_wilson_ub <= 0.80 OR
f_verification_rate < 0.01 (near-zero F-verification kills the bridge);
else INCONCLUSIVE. One-sided 95% Wilson bounds, z=1.645 (freeze-lint closed form).

Fixture (--selftest, HAND-COMPUTED): 30/1000 in fragment -> rate 0.03,
lb = 0.02232 (matches the freeze-lint value); 36/39 top-5 -> rate 0.92308.
"""
import json
import sys

Z = 1.645


def wilson_bounds(p, n):
    if n <= 0:
        return 0.0, 1.0
    z2 = Z * Z
    centre = p + z2 / (2 * n)
    spread = Z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre - spread) / (1 + z2 / n), (centre + spread) / (1 + z2 / n)


def analyze(records):
    tot = {k: 0 for k in ("n_mathlib_decls", "n_in_fragment", "n_location_targets",
                          "n_location_top5", "n_roundtrip", "n_roundtrip_fixed",
                          "n_llm_candidates", "n_f_verified")}
    for r in records:
        for k in tot:
            tot[k] += int(r["metrics"][k])
    out = {"gates": {"instrument_valid": (tot["n_mathlib_decls"] >= 1000
                                          and tot["n_location_targets"] >= 39)},
           "analysis": {}}
    a = out["analysis"]
    if tot["n_mathlib_decls"] > 0:
        a["fragment_rate"] = tot["n_in_fragment"] / tot["n_mathlib_decls"]
        a["fragment_wilson_lb"], a["fragment_wilson_ub"] = wilson_bounds(
            a["fragment_rate"], tot["n_mathlib_decls"])
        a["n_mathlib_decls"] = tot["n_mathlib_decls"]
    if tot["n_location_targets"] > 0:
        a["location_rate"] = tot["n_location_top5"] / tot["n_location_targets"]
        a["location_wilson_lb"], a["location_wilson_ub"] = wilson_bounds(
            a["location_rate"], tot["n_location_targets"])
        a["n_location_targets"] = tot["n_location_targets"]
    if tot["n_roundtrip"] > 0:
        a["roundtrip_holds"] = tot["n_roundtrip_fixed"] == tot["n_roundtrip"]
    if tot["n_llm_candidates"] > 0:
        a["f_verification_rate"] = tot["n_f_verified"] / tot["n_llm_candidates"]
    return out


def selftest():
    recs = [{"metrics": {"n_mathlib_decls": 1000, "n_in_fragment": 30,
                         "n_location_targets": 39, "n_location_top5": 36,
                         "n_roundtrip": 30, "n_roundtrip_fixed": 30,
                         "n_llm_candidates": 100, "n_f_verified": 20}}]
    out = analyze(recs)
    a = out["analysis"]
    assert abs(a["fragment_rate"] - 0.03) < 1e-12
    assert abs(a["fragment_wilson_lb"] - 0.02232) < 5e-5, a["fragment_wilson_lb"]
    assert abs(a["location_rate"] - 36 / 39) < 1e-12
    assert a["roundtrip_holds"] is True
    assert abs(a["f_verification_rate"] - 0.20) < 1e-12
    assert out["gates"]["instrument_valid"] is True
    print("g8 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
