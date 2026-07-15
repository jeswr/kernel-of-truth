#!/usr/bin/env python3
"""wave_driver.py — GLM-5.2 Wave-A 480-item traced profiling run (Stage 2).

Runs INSIDE the Modal container (or any host with a built patched `glm`). Mirrors
the backend smoke's machinery (poc/glm52-probe/smoke/smoke_driver.py) but runs the
480-item labelled teacher-forced corpus instead of the 12 probes, in ONE glm
invocation (model loads once; each item = one teacher-forced prefill, per-item
reset, DRAFT=0). Emits the kot-rtrace/1 router trace, checks integrity with
trace_analyze.py, and aggregates it with atlas_agg.py.

EXPLORATORY infra — rigor relaxed vs a frozen experiment. Writes rtrace.jsonl,
trace_summary.json, agg.json, facts.json; prints a JSON report. The $25 / wall
stop-loss is enforced by the caller (Modal wrapper) via --max-seconds.
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sh(cmd, env=None, timeout=None, cwd=None):
    e = dict(os.environ); e["COLI_NO_OMP_TUNE"] = "1"
    if env:
        e.update(env)
    p = subprocess.run(cmd, env=e, timeout=timeout, cwd=cwd,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout, p.stderr


def step_lscpu():
    rc, out, err = sh(["lscpu"])
    info = {}
    for ln in out.splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1); info[k.strip()] = v.strip()
    return {"model_name": info.get("Model name"), "cpus": info.get("CPU(s)"),
            "flags_avx2": ("avx2" in out.lower()), "raw_present": rc == 0}


def step_arch_selftest(glm_bin, snap_dir, glm_dir):
    if not snap_dir:
        return {"ran": False, "note": "no tiny snapshot"}
    ref = Path(glm_dir) / "ref_glm.json"
    if not (Path(snap_dir).exists() and ref.exists()):
        return {"ran": False, "note": "tiny oracle/ref absent"}
    rc, out, err = sh([glm_bin, "64", "16", "16"],
                      env={"SNAP": str(snap_dir), "TF": "1", "REF": str(ref)},
                      timeout=600, cwd=glm_dir)
    m = re.search(r"(\d+)/(\d+) positions", out + err)
    ok = int(m.group(1)) if m else -1
    tot = int(m.group(2)) if m else -1
    return {"ran": True, "positions_ok": ok, "positions_total": tot,
            "pass": ok == tot and tot > 0}


def step_iobench(glm_dir, shard_path):
    iob = Path(glm_dir) / "iobench"
    if not iob.exists():
        subprocess.run(["make", "-s", "iobench"], cwd=glm_dir)
    if not shard_path or not Path(shard_path).exists():
        return {"ran": False, "note": f"shard absent: {shard_path}"}
    res = {}
    for mode, flag in (("buffered", "0"), ("odirect", "1")):
        rc, out, err = sh([str(iob), str(shard_path), "19", "64", "8", flag], timeout=300)
        m = re.search(r"([\d.]+)\s*GB/s", out + err)
        res[mode] = float(m.group(1)) if m else None
    vals = [v for v in res.values() if v]
    res["gbps"] = max(vals) if vals else None
    res["ran"] = True
    return res


def build_manifest(corpus, mode, model_dir, out_path):
    """TRACE_SCORE manifest (item_id T n_prompt tok...). Full mode tokenises text
    with the model tokenizer; tiny mode uses the corpus tiny_ids. Appends the
    determinism-check repeats at id+repeat_id_offset."""
    probes = corpus["probes"]
    rep_off = corpus.get("repeat_id_offset", 10000)
    lines, meta = [], []
    idmap, nmap = {}, {}
    if mode == "tiny":
        for p in probes:
            ids = p["tiny_ids"]; npr = p["tiny_n_prompt"]
            idmap[p["id"]] = ids; nmap[p["id"]] = npr
            lines.append(" ".join(map(str, [p["id"], len(ids), npr] + ids)))
            meta.append({"id": p["id"], "domain": p["domain"], "T": len(ids), "n_prompt": npr})
    else:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
        for p in probes:
            pre = tok.encode(p["text_prompt"], add_special_tokens=False)
            tgt = tok.encode(p["text_target"], add_special_tokens=False)
            ids = pre + tgt; npr = len(pre)
            if not ids or npr == 0 or npr >= len(ids):
                # guarantee >=1 prompt and >=1 target token (teacher-forcing needs both)
                if not ids:
                    ids = [0, 0]
                if npr == 0:
                    npr = 1
                if npr >= len(ids):
                    ids = ids + [ids[-1]]
            idmap[p["id"]] = ids; nmap[p["id"]] = npr
            lines.append(" ".join(map(str, [p["id"], len(ids), npr] + ids)))
            meta.append({"id": p["id"], "domain": p["domain"], "T": len(ids), "n_prompt": npr})
    repeat_pairs = []
    for rid in corpus.get("repeat_probe_ids", []):
        ids, npr = idmap[rid], nmap[rid]
        new_id = rid + rep_off
        lines.append(" ".join(map(str, [new_id, len(ids), npr] + ids)))
        repeat_pairs.append((rid, new_id))
    Path(out_path).write_text("\n".join(lines) + "\n")
    return meta, repeat_pairs


def step_probes(glm_bin, snap, manifest, trace_path, ebits, dbits, cap, max_seconds):
    t0 = time.time()
    rc, out, err = sh([glm_bin, str(cap), str(ebits), str(dbits)],
                      env={"SNAP": snap, "RTRACE": trace_path, "TRACE_SCORE": manifest,
                           "DRAFT": "0"},
                      timeout=max_seconds)
    wall = time.time() - t0
    lm = re.search(r"loaded in ([\d.]+)s", out)
    load_s = float(lm.group(1)) if lm else 0.0
    rss_vals = [float(x) for x in re.findall(r"RSS ([\d.]+) GB", out + err)]
    return {"rc": rc, "wall_s": round(wall, 2), "load_s": load_s,
            "rss_gb_max": max(rss_vals) if rss_vals else None,
            "stdout_tail": out[-400:], "stderr_tail": err[-600:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["tiny", "full"], required=True)
    ap.add_argument("--glm-dir", required=True)
    ap.add_argument("--snap", required=True, help="model dir (tiny oracle or int4 estate)")
    ap.add_argument("--tiny-dir", help="tiny oracle dir for the arch self-test")
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--smoke-dir", default="/smoke", help="dir with trace_analyze.py")
    ap.add_argument("--atlas-dir", default="/wave", help="dir with atlas_agg.py")
    ap.add_argument("--iobench-shard")
    ap.add_argument("--ebits", type=int, default=4)
    ap.add_argument("--dbits", type=int, default=8)
    ap.add_argument("--cap", type=int, default=64)
    ap.add_argument("--out-dir", default="/tmp/wave-out")
    ap.add_argument("--trace-dir", default=None, help="where to write the (big) rtrace.jsonl")
    ap.add_argument("--max-seconds", type=int, default=20*3600)
    ap.add_argument("--price-per-hr", type=float, default=1.15)
    a = ap.parse_args()

    outd = Path(a.out_dir); outd.mkdir(parents=True, exist_ok=True)
    trace_dir = Path(a.trace_dir) if a.trace_dir else outd
    trace_dir.mkdir(parents=True, exist_ok=True)
    glm_bin = str(Path(a.glm_dir) / "glm")
    corpus = json.loads(Path(a.corpus).read_text())
    report = {"mode": a.mode, "snap": a.snap,
              "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    report["lscpu"] = step_lscpu()
    tiny_dir = a.tiny_dir or (a.snap if a.mode == "tiny" else None)
    report["arch_selftest"] = step_arch_selftest(glm_bin, tiny_dir, a.glm_dir)

    shard = a.iobench_shard
    if a.mode == "full" and not shard:
        cands = sorted(Path(a.snap).glob("out-000*.safetensors"))
        shard = str(cands[len(cands)//2]) if cands else None
    report["iobench"] = step_iobench(a.glm_dir, shard) if shard else {"ran": False, "note": "tiny"}

    manifest = str(outd / "trace_manifest.txt")
    trace = str(trace_dir / "rtrace.jsonl")
    meta, repeat_pairs = build_manifest(corpus, a.mode, a.snap, manifest)
    report["n_items"] = len(meta)
    report["repeat_pairs"] = [f"{x}:{y}" for x, y in repeat_pairs]
    report["total_prompt_tokens"] = sum(m["T"] for m in meta)

    pr = step_probes(glm_bin, a.snap, manifest, trace, a.ebits, a.dbits, a.cap, a.max_seconds)
    report["probes_run"] = pr
    n_items = len(meta)
    s_per_prefill = None
    if pr["rc"] == 0 and n_items:
        s_per_prefill = max(0.0, (pr["wall_s"] - pr["load_s"])) / (n_items + len(repeat_pairs))

    probes_complete = 0
    if Path(trace).exists():
        ended = set()
        with open(trace) as f:
            for ln in f:
                if '"t":"end"' in ln:
                    try:
                        ended.add(json.loads(ln)["item"])
                    except Exception:
                        pass
        probes_complete = len([m for m in meta if m["id"] in ended])

    facts = {"engine_ran": pr["rc"] == 0, "disk_gbps": report["iobench"].get("gbps"),
             "rss_gb": pr["rss_gb_max"], "s_per_prefill": s_per_prefill,
             "probes_complete": probes_complete}
    facts_path = str(outd / "facts.json"); Path(facts_path).write_text(json.dumps(facts, indent=2))
    report["facts"] = facts

    # integrity + go/no-go (reuse the smoke's trace_analyze)
    ta = Path(a.smoke_dir) / "trace_analyze.py"
    cmd = [sys.executable, str(ta), "--trace", trace, "--facts", facts_path,
           "--expect-probes", str(n_items), "--wave-items", str(n_items),
           "--price-per-hr", str(a.price_per_hr), "--out", str(outd / "trace_summary.json")]
    for x, y in repeat_pairs:
        cmd += ["--repeat", f"{x}:{y}"]
    rc, out, err = sh(cmd)
    try:
        summary = json.loads(out)
    except Exception:
        summary = {"error": "analyzer unparseable", "raw": out[-500:], "stderr": err[-500:]}
    report["trace_summary_gonogo"] = summary.get("go_no_go", {})
    report["integrity_errors"] = summary.get("integrity_errors", [])[:20]
    report["repeat_errors"] = summary.get("repeat_errors", [])

    # aggregate into the atlas sufficient-statistics (cross-check + report source)
    agg_path = str(outd / "agg.json")
    ag = Path(a.atlas_dir) / "atlas_agg.py"
    rc2, out2, err2 = sh([sys.executable, str(ag), "--trace", trace,
                          "--corpus", a.corpus, "--out", agg_path])
    try:
        report["agg_meta"] = json.loads(out2)
    except Exception:
        report["agg_meta"] = {"error": "agg unparseable", "stderr": err2[-500:]}

    (outd / "wave-report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
