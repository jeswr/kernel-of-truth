#!/usr/bin/env python3
"""f1 pinned analysis — HE5 byte premise (P1 §3 HE5 / F1; SAP: P8 §1.8 vocabulary).

Reads ELIGIBLE run records (kot-log/1 JSON lines, pre-filtered by verdict-gen
step 3) on stdin; writes the analysis-output JSON document on stdout.

Input metric contract (per final run record, one record per store-scale rung):
  metrics.store_scale             int    store size rung (1e3 / 1e5 / 1e6 records)
  metrics.n_records               int    records actually stored (same set both arms)
  metrics.kernel_store_bytes      int    KOTK/2 packed store, total bytes
  metrics.gloss_zstd_bytes        int    best general-purpose-compressed (zstd, JCS
                                         discipline) text store of the SAME records
  metrics.kernel_lookup_p50_us    float  p50 retrieval latency, kernel store
  metrics.gloss_lookup_p50_us     float  p50 retrieval latency, compressed text store

Output fields (all declared in the frozen record's pins.analysis_script.output_fields):
  /gates/instrument_valid          every scale has positive byte counts + n_records
  /analysis/byte_ratio             MIN over scales of gloss_bytes/kernel_bytes
                                   (conservative: the claim must hold at every scale)
  /analysis/latency_ratio          MAX over scales of kernel_p50/gloss_p50
  /analysis/byte_ratio_by_scale    per-scale ratios (reporting)
  /analysis/bytes_per_record_kernel, /analysis/bytes_per_record_gloss  (at largest scale)
  /analysis/n_scales               number of distinct scales measured

Deterministic: no sampling, no RNG (P1 common rules: deterministic counts carry
no test). Multiple runs at one scale are summed (byte totals are additive over
disjoint shards); latencies are averaged.

Fixture (--selftest, HAND-COMPUTED): one scale, gloss 990 / kernel 300
-> byte_ratio 3.3; latencies 10 vs 8 -> latency_ratio 1.25.
"""
import json
import sys


def analyze(records):
    scales = {}
    for r in records:
        m = r["metrics"]
        s = scales.setdefault(int(m["store_scale"]), {
            "kernel_bytes": 0, "gloss_bytes": 0, "n_records": 0,
            "k_lat": [], "g_lat": []})
        s["kernel_bytes"] += int(m["kernel_store_bytes"])
        s["gloss_bytes"] += int(m["gloss_zstd_bytes"])
        s["n_records"] += int(m["n_records"])
        s["k_lat"].append(float(m["kernel_lookup_p50_us"]))
        s["g_lat"].append(float(m["gloss_lookup_p50_us"]))

    instrument_valid = bool(scales) and all(
        s["kernel_bytes"] > 0 and s["gloss_bytes"] > 0 and s["n_records"] > 0
        and s["k_lat"] and all(v > 0 for v in s["g_lat"])
        for s in scales.values())

    out = {"gates": {"instrument_valid": instrument_valid}, "analysis": {}}
    if instrument_valid:
        by_scale, lat_ratios = {}, []
        for scale in sorted(scales):
            s = scales[scale]
            by_scale[str(scale)] = s["gloss_bytes"] / s["kernel_bytes"]
            lat_ratios.append((sum(s["k_lat"]) / len(s["k_lat"]))
                              / (sum(s["g_lat"]) / len(s["g_lat"])))
        top = scales[max(scales)]
        out["analysis"] = {
            "byte_ratio": min(by_scale.values()),
            "latency_ratio": max(lat_ratios),
            "byte_ratio_by_scale": by_scale,
            "bytes_per_record_kernel": top["kernel_bytes"] / top["n_records"],
            "bytes_per_record_gloss": top["gloss_bytes"] / top["n_records"],
            "n_scales": len(scales),
        }
    return out


def selftest():
    recs = [{"metrics": {"store_scale": 1000, "n_records": 10,
                         "kernel_store_bytes": 300, "gloss_zstd_bytes": 990,
                         "kernel_lookup_p50_us": 10.0, "gloss_lookup_p50_us": 8.0}}]
    out = analyze(recs)
    assert out["gates"]["instrument_valid"] is True
    assert abs(out["analysis"]["byte_ratio"] - 3.3) < 1e-12, out       # 990/300
    assert abs(out["analysis"]["latency_ratio"] - 1.25) < 1e-12, out   # 10/8
    assert out["analysis"]["bytes_per_record_kernel"] == 30.0
    assert analyze([])["gates"]["instrument_valid"] is False
    print("f1 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        records = [json.loads(l) for l in sys.stdin if l.strip()]
        print(json.dumps(analyze(records), sort_keys=True))
