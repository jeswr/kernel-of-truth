#!/usr/bin/env python3
"""stage3_driver.py — GLM-5.2 Stage-3 causal-ablation harness (runs INSIDE the
Modal container, or any host with a built patched `glm`).  Reuses the Stage-1/2
machinery (rtrace + teacher-forced manifest); adds the ABLATE_SCORE path.

For every shortlisted (layer,expert) cell it runs, on the cell's activation-max
on-domain items + matched off-domain controls:
    baseline (mode 0, once per unique item)
  + contribution-ablation (mode 1)   [routing kept, expert output -> 0]
  + route-around (mode 2)            [expert dropped, survivors renormalised]
  + module-swap (mode 3)             [replacement leads only; generic substitute]
and records, per target position, PAIRED deltas vs the item's baseline:
    target-NLL, gold-token logit margin, next-token top-K KL, exact correctness.

MODES:  --mode tiny  tiny GlmMoeDsa oracle (tiny_ids); ~$0 plumbing + a byte-identity
                     check (baseline == ablate-an-unused-cell) that PROVES the patch
                     is inert off-target on a REAL model.
        --mode full  the staged int4 estate; the real causal wave.

WALL/COST: --max-seconds aborts the sweep (the Modal wrapper enforces the $ stop-loss).
ABLATE_OUT is flushed per item, so a timeout still leaves usable partial results;
the manifest is ORDERED baseline-first then per-expert, so partial == complete for
the earliest experts.  EXPLORATORY infra — rigor relaxed vs a frozen experiment.
"""
from __future__ import annotations
import argparse, json, gzip, os, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sh(cmd, env=None, timeout=None, cwd=None):
    e = dict(os.environ); e["COLI_NO_OMP_TUNE"] = "1"
    if env: e.update(env)
    return subprocess.run(cmd, env=e, timeout=timeout, cwd=cwd,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def tokenize_items(items: dict, mode: str, model_dir: str) -> dict:
    """corpus_item_id -> {ids:[...], n_prompt:int}."""
    out = {}
    if mode == "tiny":
        for pid, it in items.items():
            out[int(pid)] = {"ids": it["tiny_ids"], "n_prompt": it["tiny_n_prompt"]}
        return out
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
    for pid, it in items.items():
        pre = tok.encode(it["text_prompt"], add_special_tokens=False)
        tgt = tok.encode(it["text_target"], add_special_tokens=False)
        out[int(pid)] = {"ids": pre + tgt, "n_prompt": len(pre)}
    return out


def build_manifest(shortlist, tokd, out_path, swap_on):
    """Emit the ABLATE_SCORE manifest and the mid->meta record map.
    Order: all baselines first, then per-expert (contrib+route+swap) so a partial
    run yields complete data for the earliest experts."""
    lines, records = [], []
    mid = 0

    def emit(cond, corpus_item, mode, cells):
        nonlocal mid
        t = tokd[corpus_item]; ids, npr = t["ids"], t["n_prompt"]
        if len(ids) < 2 or npr < 1 or npr >= len(ids):
            return  # skip degenerate (no target position)
        flat = []
        for (L, E, Aa) in cells: flat += [L, E, Aa]
        lines.append(" ".join(map(str, [mid, len(ids), npr, mode, len(cells)] + flat + ids)))
        records.append({"mid": mid, "cond": cond, "corpus_item": corpus_item,
                        "mode": mode, "cells": cells})
        mid += 1

    # 1) baseline for every unique referenced item
    uniq = sorted({pid for c in shortlist["experts"] for pid in (c["on_items"] + c["off_items"])})
    for pid in uniq:
        if pid in tokd: emit("baseline", pid, 0, [])

    # 2) per expert: contribution + route-around on all items; module-swap (leads) on-domain
    for c in shortlist["experts"]:
        L, E, cell = c["layer"], c["expert"], c["cell"]
        for arm, dom in (("on", c["on_items"]), ("off", c["off_items"])):
            for pid in dom:
                if pid not in tokd: continue
                emit(f"contrib:{cell}:{arm}", pid, 1, [[L, E, -1]])
                emit(f"route:{cell}:{arm}",   pid, 2, [[L, E, -1]])
        if c["swap_to"] is not None:
            for pid in c["on_items"][:swap_on]:
                if pid in tokd: emit(f"swap:{cell}:on", pid, 3, [[L, E, int(c["swap_to"])]])

    Path(out_path).write_text("\n".join(lines) + "\n")
    return records


def run_glm(glm_bin, snap, manifest, ablate_out, rtrace, ebits, dbits, cap, max_seconds):
    env = {"SNAP": snap, "ABLATE_SCORE": manifest, "ABLATE_OUT": ablate_out, "DRAFT": "0"}
    if rtrace: env["RTRACE"] = rtrace
    t0 = time.time()
    try:
        p = sh([glm_bin, str(cap), str(ebits), str(dbits)], env=env, timeout=max_seconds)
        rc, timed_out = p.returncode, False
        out, err = p.stdout, p.stderr
    except subprocess.TimeoutExpired as te:
        rc, timed_out = 0, True
        out = te.stdout.decode() if te.stdout else ""; err = te.stderr.decode() if te.stderr else ""
    wall = time.time() - t0
    lm = re.search(r"loaded in ([\d.]+)s", out)
    rss = [float(x) for x in re.findall(r"RSS ([\d.]+) GB", out + err)]
    return {"rc": rc, "timed_out": timed_out, "wall_s": round(wall, 1),
            "load_s": float(lm.group(1)) if lm else 0.0,
            "rss_gb_max": max(rss) if rss else None,
            "stdout_tail": out[-500:], "stderr_tail": err[-800:]}


def parse_ablate_out(path):
    """mid -> {pos -> logit-summary dict}.  Reads the JSONL ABLATE_OUT."""
    per = {}
    opn = gzip.open if str(path).endswith(".gz") else open
    with opn(path, "rt") as f:
        for ln in f:
            if '"t":"lg"' not in ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            per.setdefault(r["item"], {})[r["pos"]] = r
    return per


def topk_kl(base, abl):
    """Approximate KL(P_base || P_abl) over base's top-K support, with a floor for
    ids missing from abl's top-K (abl's K-th logit).  Exact endpoints are NLL/margin."""
    import math
    zb, za = base["logZ"], abl["logZ"]
    ab = {i: v for i, v in abl["tk"] if i >= 0}
    a_floor = min((v for _, v in abl["tk"] if _ >= 0), default=za - 40.0)
    kl = 0.0
    for i, vb in base["tk"]:
        if i < 0: continue
        pb = math.exp(vb - zb)
        la = ab.get(i, a_floor)
        pa = math.exp(la - za)
        if pb > 0 and pa > 0: kl += pb * (math.log(pb) - math.log(pa))
    return kl


def compute_deltas(records, per):
    """Join each ablated item to its baseline (same corpus_item, same positions) and
    emit per-(record, position) paired deltas."""
    base_by_item = {r["corpus_item"]: r["mid"] for r in records if r["mode"] == 0}
    rows = []
    for r in records:
        if r["mode"] == 0: continue
        bmid = base_by_item.get(r["corpus_item"])
        if bmid is None or bmid not in per or r["mid"] not in per: continue
        bpos, apos = per[bmid], per[r["mid"]]
        for pos, b in bpos.items():
            a = apos.get(pos)
            if a is None or a["gold"] != b["gold"]: continue
            rows.append({
                "cond": r["cond"], "corpus_item": r["corpus_item"], "mode": r["mode"],
                "cell": (r["cells"][0][0] if r["cells"] else None) and
                        f"main|{r['cells'][0][0]}|{r['cells'][0][1]}",
                "pos": pos, "gold": b["gold"],
                "dNLL": a["nll"] - b["nll"],
                "dMargin": a["mgn"] - b["mgn"],
                "base_corr": b["corr"], "abl_corr": a["corr"],
                "dCorr": a["corr"] - b["corr"],
                "KL": topk_kl(b, a),
            })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["tiny", "full"], required=True)
    ap.add_argument("--glm-dir", required=True)
    ap.add_argument("--snap", required=True)
    ap.add_argument("--shortlist", default=str(HERE / "corpus" / "stage3_shortlist.json"))
    ap.add_argument("--corpus", default=str(HERE / "corpus" / "stage3_corpus.json"))
    ap.add_argument("--out-dir", default="/tmp/stage3-out")
    ap.add_argument("--trace-dir", default="/tmp/stage3-out")
    ap.add_argument("--ebits", type=int, default=4)
    ap.add_argument("--dbits", type=int, default=8)
    ap.add_argument("--cap", type=int, default=64)
    ap.add_argument("--max-seconds", type=int, default=7200)
    ap.add_argument("--price-per-hr", type=float, default=1.15)
    ap.add_argument("--with-rtrace", action="store_true")
    a = ap.parse_args()

    outd = Path(a.out_dir); outd.mkdir(parents=True, exist_ok=True)
    glm_bin = str(Path(a.glm_dir) / "glm")
    shortlist = json.loads(Path(a.shortlist).read_text())
    corpus = json.loads(Path(a.corpus).read_text())["items"]
    report = {"mode": a.mode, "snap": a.snap,
              "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    tokd = tokenize_items(corpus, a.mode, a.snap)
    swap_on = int(shortlist.get("n_swap_on", 10))
    manifest = str(outd / "ablate_manifest.txt")
    records = build_manifest(shortlist, tokd, manifest, swap_on)
    report["n_manifest_items"] = len(records)
    report["n_experts"] = len(shortlist["experts"])
    (outd / "stage3_records.json").write_text(json.dumps(records))

    ablate_out = str(Path(a.trace_dir) / "ablate_out.jsonl")
    rtrace = str(Path(a.trace_dir) / "ablate_rtrace.jsonl") if a.with_rtrace else None
    run = run_glm(glm_bin, a.snap, manifest, ablate_out, rtrace,
                  a.ebits, a.dbits, a.cap, a.max_seconds)
    report["run"] = run

    per = parse_ablate_out(ablate_out) if Path(ablate_out).exists() else {}
    report["n_items_scored"] = len(per)
    rows = compute_deltas(records, per)
    (outd / "stage3_deltas.json").write_text(json.dumps(rows))
    report["n_delta_rows"] = len(rows)

    # in-container analysis (re-runnable locally on the downloaded deltas)
    an = sh([sys.executable, str(HERE / "stage3_analyze.py"),
             "--deltas", str(outd / "stage3_deltas.json"),
             "--shortlist", a.shortlist, "--out", str(outd / "stage3_analysis.json")])
    try:
        report["analysis"] = json.loads(an.stdout)
    except Exception:
        report["analysis"] = {"error": "analyze unparseable", "tail": an.stdout[-400:], "err": an.stderr[-400:]}

    report["cost_est_usd"] = round(run["wall_s"] / 3600.0 * a.price_per_hr, 2)
    (outd / "stage3-report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
