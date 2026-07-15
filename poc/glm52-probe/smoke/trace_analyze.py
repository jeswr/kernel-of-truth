#!/usr/bin/env python3
"""trace_analyze.py — GLM-5.2 backend-smoke trace INTEGRITY + go/no-go.

Pure stdlib. Consumes a kot-rtrace/1 JSONL trace (emitted by the patched colibri
engine's read-only router trace, rtrace.h) plus the smoke's MEASURED backend
facts, and emits the plan's decision: GO-FULL-GLM52 / PROXY-ONLY / OFFLINE-ONLY
(docs/next/design/glm52-expert-profiling-plan-sol-20260715.md §"Measured go/no-go
criteria" + §"Decision gate").

Integrity checks (the anti-contamination + top-k invariants the plan requires):
  1. framing        — every item has begin+end; end.rows == emitted route rows.
  2. no carry-over  — every route row's item == the enclosing begin item (rows
                      cannot leak across items; the CONTAMINATION-NOTE bug).
  3. top-k          — per (item,tok,layer): ranks are 0..Ke-1 contiguous+distinct,
                      expert ids distinct, selection scores non-increasing by rank,
                      margin >= 0, weights finite and > 0.
  4. fingerprint    — independently recompute the FNV-1a-64 decision fingerprint
                      and match end.decident_fnv1a64 (so the repeat check is trusted).
  5. site           — draft=0 items are all "main"; "mtp" rows only in draft>=1.
  6. byte-identity  — each --repeat A:B pair has identical decision fingerprints
                      (deterministic routing on a repeated probe).

Go/no-go gates (all must hold for GO-FULL-GLM52):
  disk >= 1.0 GB/s · RSS < 60 GB · probes_complete == expected · integrity clean ·
  repeat byte-identity clean · projected 480-item Wave-A < 20 h AND < $25.

Usage:
  trace_analyze.py --trace t.jsonl [--facts facts.json] [--repeat 0:3 ...]
                   [--expect-probes 12] [--wave-items 480] [--price-per-hr 1.15]
                   [--wave-hours-cap 20] [--wave-cost-cap 25] [--out summary.json]
facts.json keys (MEASURED by smoke_driver.py in-container; optional for a
integrity-only dry run): engine_ran(bool) disk_gbps rss_gb s_per_prefill
probes_complete
"""
from __future__ import annotations
import argparse, json, sys
from collections import defaultdict

FNV_OFFSET = 1469598103934665603
FNV_PRIME  = 1099511628211
MASK64     = (1 << 64) - 1

def fnv_mix(h: int, v: int) -> int:
    v &= MASK64
    for _ in range(8):
        h ^= (v & 0xff)
        h = (h * FNV_PRIME) & MASK64
        v >>= 8
    return h

def decision_word(pos: int, layer: int, rank: int, e: int) -> int:
    return (((pos & 0xffffffff) << 40) ^ ((layer & 0xffffffff) << 24)
            ^ ((rank & 0xffffffff) << 16) ^ (e & 0xffffffff)) & MASK64

def load_trace(path):
    items = {}           # item_id -> {"begin":obj,"end":obj,"rows":[...] ,"order":int}
    order = 0
    cur = None
    hdr = None
    with open(path, "r") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            o = json.loads(ln)
            t = o.get("t")
            if t == "hdr":
                hdr = o
            elif t == "begin":
                cur = o["item"]
                items[cur] = {"begin": o, "end": None, "rows": [], "order": order}
                order += 1
            elif t == "r":
                if cur is None or o["item"] not in items:
                    items.setdefault(o["item"], {"begin": None, "end": None, "rows": [], "order": order})
                items[o["item"]]["rows"].append(o)
            elif t == "end":
                if o["item"] in items:
                    items[o["item"]]["end"] = o
                cur = None
    return hdr, items

def check_integrity(items):
    errs, warns = [], []
    per_item = {}
    for iid, it in items.items():
        b, e, rows = it["begin"], it["end"], it["rows"]
        if b is None:
            errs.append(f"item {iid}: route rows with NO begin (carry-over/leak)")
            continue
        if e is None:
            errs.append(f"item {iid}: no end line (truncated)")
        # framing: end.rows matches emitted
        if e is not None and e.get("rows") != len(rows):
            errs.append(f"item {iid}: end.rows={e.get('rows')} != emitted {len(rows)}")
        # no carry-over: every row belongs to this item
        leaked = [r for r in rows if r["item"] != iid]
        if leaked:
            errs.append(f"item {iid}: {len(leaked)} rows tagged a DIFFERENT item (carry-over)")
        draft = b.get("draft", 0)
        # group by (tok, layer)
        groups = defaultdict(list)
        for r in rows:
            groups[(r["tok"], r["layer"])].append(r)
        recomputed = FNV_OFFSET
        sites = set()
        # replay in emission order for the fingerprint
        for r in rows:
            recomputed = fnv_mix(recomputed, decision_word(r["tok"], r["layer"], r["rank"], r["e"]))
            sites.add(r["site"])
        for (tok, layer), grp in groups.items():
            grp_sorted = sorted(grp, key=lambda r: r["rank"])
            ranks = [r["rank"] for r in grp_sorted]
            Ke = len(grp_sorted)
            if ranks != list(range(Ke)):
                errs.append(f"item {iid} tok {tok} layer {layer}: ranks not 0..{Ke-1} contiguous: {ranks}")
            experts = [r["e"] for r in grp_sorted]
            if len(set(experts)) != Ke:
                errs.append(f"item {iid} tok {tok} layer {layer}: duplicate expert ids {experts}")
            sels = [r["sel"] for r in grp_sorted]
            if any(sels[i] < sels[i+1] - 1e-4 for i in range(Ke-1)):
                errs.append(f"item {iid} tok {tok} layer {layer}: sel not non-increasing by rank {sels}")
            mgn = grp_sorted[0].get("mgn", 0.0)
            if mgn < -1e-4:
                errs.append(f"item {iid} tok {tok} layer {layer}: negative top-k margin {mgn}")
            ws = [r["w"] for r in grp_sorted]
            if any((w != w) or w <= 0.0 for w in ws):   # NaN or non-positive
                errs.append(f"item {iid} tok {tok} layer {layer}: invalid weight(s) {ws}")
        # site policy
        if draft == 0 and "mtp" in sites:
            errs.append(f"item {iid}: draft=0 but has mtp rows (MTP must not fire at DRAFT=0)")
        # fingerprint faithfulness
        fp_ok = None
        if e is not None and "decident_fnv1a64" in e:
            got = e["decident_fnv1a64"]
            want = f"{recomputed:016x}"
            fp_ok = (got == want)
            if not fp_ok:
                errs.append(f"item {iid}: fingerprint mismatch emitted={got} recomputed={want}")
        per_item[iid] = {"rows": len(rows), "draft": draft, "sites": sorted(sites),
                         "fingerprint": (e or {}).get("decident_fnv1a64"),
                         "recomputed_ok": fp_ok, "n_tokens": len({r["tok"] for r in rows}),
                         "n_layers": len({r["layer"] for r in rows})}
    return errs, warns, per_item

def check_repeats(per_item, pairs):
    errs = []
    for a, b in pairs:
        if a not in per_item or b not in per_item:
            errs.append(f"repeat {a}:{b}: item missing from trace")
            continue
        fa, fb = per_item[a]["fingerprint"], per_item[b]["fingerprint"]
        if fa is None or fb is None:
            errs.append(f"repeat {a}:{b}: missing fingerprint")
        elif fa != fb:
            errs.append(f"repeat {a}:{b}: fingerprints DIFFER {fa} != {fb} (non-deterministic routing)")
    return errs

def go_no_go(integrity_clean, repeat_clean, facts, per_item, expect_probes,
             wave_items, price_per_hr, wave_hours_cap, wave_cost_cap):
    g = {}
    engine_ran = bool(facts.get("engine_ran", len(per_item) > 0))
    disk = facts.get("disk_gbps")
    rss = facts.get("rss_gb")
    spp = facts.get("s_per_prefill")
    probes = facts.get("probes_complete", len([i for i in per_item if per_item[i]["rows"] > 0]))
    g["engine_ran"] = engine_ran
    g["disk_gbps"] = disk
    g["disk_ge_1gbps"] = (disk is not None and disk >= 1.0)
    g["rss_gb"] = rss
    g["rss_lt_60gb"] = (rss is not None and rss < 60.0)
    g["probes_complete"] = probes
    g["probes_expected"] = expect_probes
    g["probes_all_complete"] = (probes == expect_probes)
    g["integrity_clean"] = integrity_clean
    g["repeat_byte_identical"] = repeat_clean
    if spp is not None:
        wave_h = wave_items * spp / 3600.0
        wave_cost = wave_h * price_per_hr
        g["proj_wave_hours"] = round(wave_h, 2)
        g["proj_wave_cost_usd"] = round(wave_cost, 2)
        g["wave_hours_lt_cap"] = wave_h < wave_hours_cap
        g["wave_cost_lt_cap"] = wave_cost < wave_cost_cap
    else:
        g["proj_wave_hours"] = g["proj_wave_cost_usd"] = None
        g["wave_hours_lt_cap"] = g["wave_cost_lt_cap"] = None
    hard = [g["disk_ge_1gbps"], g["rss_lt_60gb"], g["probes_all_complete"],
            g["integrity_clean"], g["repeat_byte_identical"],
            g["wave_hours_lt_cap"], g["wave_cost_lt_cap"]]
    if not engine_ran or not per_item:
        verdict = "OFFLINE-ONLY"
        reason = "engine did not run / no trace produced"
    elif all(x is True for x in hard):
        verdict = "GO-FULL-GLM52"
        reason = "all backend + trace-integrity + cost gates pass"
    else:
        # engine ran and produced valid traces, but a backend gate (disk/throughput/
        # cost) failed -> methodology can still be built on the proxy.
        failed = [k for k, v in [
            ("disk>=1GB/s", g["disk_ge_1gbps"]), ("rss<60GB", g["rss_lt_60gb"]),
            ("12/12 probes", g["probes_all_complete"]), ("integrity", g["integrity_clean"]),
            ("repeat-identical", g["repeat_byte_identical"]),
            ("wave<20h", g["wave_hours_lt_cap"]), ("wave<$25", g["wave_cost_lt_cap"])]
            if v is not True]
        if not g["integrity_clean"] or not g["repeat_byte_identical"]:
            verdict = "OFFLINE-ONLY"
            reason = f"trace integrity/determinism failed ({failed}) — do not scale"
        else:
            verdict = "PROXY-ONLY"
            reason = f"engine+traces OK but backend/cost gate failed ({failed})"
    g["verdict"] = verdict
    g["reason"] = reason
    return g

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", required=True)
    ap.add_argument("--facts")
    ap.add_argument("--repeat", action="append", default=[], help="A:B repeat pair (byte-identity)")
    ap.add_argument("--expect-probes", type=int, default=12)
    ap.add_argument("--wave-items", type=int, default=480)
    ap.add_argument("--price-per-hr", type=float, default=1.15)
    ap.add_argument("--wave-hours-cap", type=float, default=20.0)
    ap.add_argument("--wave-cost-cap", type=float, default=25.0)
    ap.add_argument("--out")
    a = ap.parse_args()

    hdr, items = load_trace(a.trace)
    errs, warns, per_item = check_integrity(items)
    pairs = []
    for p in a.repeat:
        x, y = p.split(":")
        pairs.append((int(x), int(y)))
    rep_errs = check_repeats(per_item, pairs)
    integrity_clean = len(errs) == 0
    repeat_clean = len(rep_errs) == 0
    facts = {}
    if a.facts:
        with open(a.facts) as f:
            facts = json.load(f)
    g = go_no_go(integrity_clean, repeat_clean, facts, per_item, a.expect_probes,
                 a.wave_items, a.price_per_hr, a.wave_hours_cap, a.wave_cost_cap)
    summary = {
        "schema": hdr.get("schema") if hdr else None,
        "n_items": len(per_item),
        "integrity_errors": errs,
        "repeat_errors": rep_errs,
        "warnings": warns,
        "per_item": per_item,
        "repeat_pairs": [f"{x}:{y}" for x, y in pairs],
        "go_no_go": g,
    }
    out = json.dumps(summary, indent=2)
    if a.out:
        with open(a.out, "w") as f:
            f.write(out + "\n")
    print(out)
    print(f"\nVERDICT: {g['verdict']}  ({g['reason']})", file=sys.stderr)
    # exit 0 always (verdict is data); the driver decides on the verdict string.
    return 0

if __name__ == "__main__":
    sys.exit(main())
