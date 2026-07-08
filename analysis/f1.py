#!/usr/bin/env python3
"""f1 pinned analysis — HE5 byte premise (P1 §3 HE5 / F1; SAP: P8 §1.8 vocabulary).

Correction c-f1-1 (2026-07-08, pre-sign-off): the frozen input contract now
matches EXACTLY what the pinned byte instrument (tools/experiments/
f1_analysis.py) emits. The earlier contract demanded store_scale + retrieval-
latency fields no committed instrument measured; the latency sub-metric of the
HE5 premise ("at <=2x retrieval latency") is NOT decided by this record — it
moves to the F5 accuracy leg, where retrieval is actually served (see the f1
correction note). This record decides the BYTE ratio only.

Reads ELIGIBLE run records (kot-log/1 JSON lines, pre-filtered by verdict-gen
step 3) on stdin; writes the analysis-output JSON document on stdout.

Input metric contract (per final run record — the instrument's own keys):
  metrics.n_records          int   synset records stored (same set both arms)
  metrics.kernel_pack_bytes  int   KOTK/2 entropy-columnar pack, total bytes
  metrics.gloss_zstd_bytes   int   zstd-compressed glosses-only text store of
                                   the SAME records (as served), total bytes

Output fields (all declared in the frozen record's pins.analysis_script.output_fields):
  /gates/instrument_valid           every run has positive byte counts + n_records
  /analysis/byte_ratio              sum(gloss_zstd_bytes) / sum(kernel_pack_bytes)
                                    (byte totals are additive over disjoint shards)
  /analysis/bytes_per_record_kernel, /analysis/bytes_per_record_gloss
  /analysis/n_records               total records
  /analysis/n_runs                  eligible runs consumed

Deterministic: no sampling, no RNG (P1 common rules: deterministic counts
carry no test).

Fixture (--selftest, HAND-COMPUTED): one run, gloss 990 / kernel 300 over 10
records -> byte_ratio 3.3, 30.0 kernel B/rec, 99.0 gloss B/rec.
"""
import json
import sys


def analyze(records):
    K = G = N = 0
    valid = bool(records)
    for r in records:
        m = r["metrics"]
        k, g, n = int(m["kernel_pack_bytes"]), int(m["gloss_zstd_bytes"]), int(m["n_records"])
        if k <= 0 or g <= 0 or n <= 0:
            valid = False
        K += k
        G += g
        N += n
    out = {"gates": {"instrument_valid": valid}, "analysis": {}}
    if valid:
        out["analysis"] = {
            "byte_ratio": G / K,
            "bytes_per_record_kernel": K / N,
            "bytes_per_record_gloss": G / N,
            "n_records": N,
            "n_runs": len(records),
        }
    return out


def selftest():
    recs = [{"metrics": {"n_records": 10, "kernel_pack_bytes": 300, "gloss_zstd_bytes": 990}}]
    out = analyze(recs)
    assert out["gates"]["instrument_valid"] is True
    assert abs(out["analysis"]["byte_ratio"] - 3.3) < 1e-12, out       # 990/300
    assert out["analysis"]["bytes_per_record_kernel"] == 30.0
    assert out["analysis"]["bytes_per_record_gloss"] == 99.0
    assert analyze([])["gates"]["instrument_valid"] is False
    assert analyze([{"metrics": {"n_records": 0, "kernel_pack_bytes": 1,
                                 "gloss_zstd_bytes": 1}}])["gates"]["instrument_valid"] is False
    print("f1 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
