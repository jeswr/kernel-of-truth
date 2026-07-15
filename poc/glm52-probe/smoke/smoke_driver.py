#!/usr/bin/env python3
"""smoke_driver.py — GLM-5.2 colibri backend-feasibility SMOKE sequence.

Runs INSIDE the Modal container (or any host with a built patched `glm`). Executes
the plan's Stage-1 smoke (docs/next/design/glm52-expert-profiling-plan-sol-20260715.md
§"Modal smoke test"): lscpu; colibri architecture self-test (tiny GlmMoeDsa oracle,
teacher-forced 32/32); a 19 MB-block random-read benchmark on the local ephemeral
SSD (GB/s); the 12 teacher-forced traced probes (+2 repeats for byte-identity);
then trace_analyze.py for integrity + go/no-go (GO-FULL-GLM52 / PROXY-ONLY /
OFFLINE-ONLY).

MODES:
  --mode tiny  validation: run against the built tiny GlmMoeDsa oracle (glm_tiny),
               probes = corpus `tiny_ids`. ~$0. Proves the pipeline end-to-end.
  --mode full  the real smoke: run against the staged int4 estate, probes tokenised
               with the model tokenizer. The disk/throughput/cost gates decide GO.

WALL-CLOCK CEILING: --max-seconds aborts the probe loop early (the outer Modal
wrapper enforces the $25 / 2 h stop-loss; this is the in-driver backstop).

Nothing here is a frozen experiment — EXPLORATORY infra. It writes smoke-report.json
and prints the verdict; it never edits a registry or commits.
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sh(cmd, env=None, timeout=None, cwd=None):
    e = dict(os.environ); e["COLI_NO_OMP_TUNE"] = "1"
    if env: e.update(env)
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
    """colibri teacher-forced oracle self-test (expects 32/32). make_glm_oracle.py
    writes glm_tiny/ (weights) + ref_glm.json in the c/ dir; run from there so the
    engine finds the oracle reference."""
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
    """19 MB × 64 reads, 8 threads. buffered then O_DIRECT. GB/s = max of the two."""
    iob = Path(glm_dir) / "iobench"
    if not iob.exists():
        rc = subprocess.run(["make", "-s", "iobench"], cwd=glm_dir).returncode
    if not Path(shard_path).exists():
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
    """Emit the TRACE_SCORE manifest (item_id T n_prompt tok...). Returns item meta
    + repeat pairs (orig:repeat_id)."""
    probes = corpus["probes"]
    lines, meta = [], []
    if mode == "tiny":
        for p in probes:
            ids = p["tiny_ids"]; npr = p["tiny_n_prompt"]
            lines.append(" ".join(map(str, [p["id"], len(ids), npr] + ids)))
            meta.append({"id": p["id"], "domain": p["domain"], "T": len(ids), "n_prompt": npr})
        idmap = {p["id"]: p["tiny_ids"] for p in probes}
        nmap = {p["id"]: p["tiny_n_prompt"] for p in probes}
    else:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
        idmap, nmap = {}, {}
        for p in probes:
            pre = tok.encode(p["text_prompt"], add_special_tokens=False)
            tgt = tok.encode(p["text_target"], add_special_tokens=False)
            ids = pre + tgt; npr = len(pre)
            idmap[p["id"]] = ids; nmap[p["id"]] = npr
            lines.append(" ".join(map(str, [p["id"], len(ids), npr] + ids)))
            meta.append({"id": p["id"], "domain": p["domain"], "T": len(ids), "n_prompt": npr})
    # repeats for byte-identity: re-run repeat_probe_ids with id+1000
    repeat_pairs = []
    for rid in corpus.get("repeat_probe_ids", []):
        ids, npr = idmap[rid], nmap[rid]
        new_id = rid + 1000
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
            "stdout_tail": out[-400:], "stderr_tail": err[-400:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["tiny", "full"], required=True)
    ap.add_argument("--glm-dir", required=True, help="colibri c/ dir with built glm + iobench")
    ap.add_argument("--snap", required=True, help="model dir (tiny oracle or int4 estate)")
    ap.add_argument("--tiny-dir", help="tiny oracle dir for the arch self-test (defaults to --snap in tiny mode)")
    ap.add_argument("--corpus", default=str(HERE / "corpus" / "probes12.json"))
    ap.add_argument("--iobench-shard", help="a shard to benchmark random reads on (full mode)")
    ap.add_argument("--ebits", type=int, default=4)
    ap.add_argument("--dbits", type=int, default=8)
    ap.add_argument("--cap", type=int, default=64)
    ap.add_argument("--out-dir", default="/tmp/smoke-out")
    ap.add_argument("--max-seconds", type=int, default=7200, help="probe-loop wall ceiling (stop-loss backstop)")
    ap.add_argument("--price-per-hr", type=float, default=1.15)
    a = ap.parse_args()

    outd = Path(a.out_dir); outd.mkdir(parents=True, exist_ok=True)
    glm_bin = str(Path(a.glm_dir) / "glm")
    corpus = json.loads(Path(a.corpus).read_text())
    report = {"mode": a.mode, "snap": a.snap, "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    report["lscpu"] = step_lscpu()
    tiny_dir = a.tiny_dir or (a.snap if a.mode == "tiny" else None)
    report["arch_selftest"] = step_arch_selftest(glm_bin, tiny_dir, a.glm_dir)

    shard = a.iobench_shard
    if a.mode == "full" and not shard:
        cands = sorted(Path(a.snap).glob("out-000*.safetensors"))
        shard = str(cands[len(cands)//2]) if cands else None
    report["iobench"] = step_iobench(a.glm_dir, shard) if shard else {"ran": False, "note": "no shard (tiny)"}

    manifest = str(outd / "trace_manifest.txt")
    trace = str(outd / "rtrace.jsonl")
    meta, repeat_pairs = build_manifest(corpus, a.mode, a.snap, manifest)
    report["probe_meta"] = meta
    report["repeat_pairs"] = [f"{x}:{y}" for x, y in repeat_pairs]

    pr = step_probes(glm_bin, a.snap, manifest, trace, a.ebits, a.dbits, a.cap, a.max_seconds)
    report["probes_run"] = pr
    n_probes = len(meta)
    s_per_prefill = None
    if pr["rc"] == 0 and n_probes:
        # per-prefill = (wall - load) / (probes + repeats)
        s_per_prefill = max(0.0, (pr["wall_s"] - pr["load_s"])) / (n_probes + len(repeat_pairs))

    # count completed probes = items in the trace with an end line
    probes_complete = 0
    if Path(trace).exists():
        ended = set()
        for ln in Path(trace).read_text().splitlines():
            if '"t":"end"' in ln:
                try: ended.add(json.loads(ln)["item"])
                except Exception: pass
        probes_complete = len([m for m in meta if m["id"] in ended])

    facts = {"engine_ran": pr["rc"] == 0, "disk_gbps": report["iobench"].get("gbps"),
             "rss_gb": pr["rss_gb_max"], "s_per_prefill": s_per_prefill,
             "probes_complete": probes_complete}
    facts_path = str(outd / "facts.json"); Path(facts_path).write_text(json.dumps(facts, indent=2))
    report["facts"] = facts

    # analyzer
    cmd = [sys.executable, str(HERE / "trace_analyze.py"), "--trace", trace,
           "--facts", facts_path, "--expect-probes", str(n_probes),
           "--price-per-hr", str(a.price_per_hr), "--out", str(outd / "trace_summary.json")]
    for x, y in repeat_pairs:
        cmd += ["--repeat", f"{x}:{y}"]
    rc, out, err = sh(cmd)
    try:
        summary = json.loads(out)
    except Exception:
        summary = {"error": "analyzer output unparseable", "raw": out[-500:], "stderr": err[-500:]}
    report["trace_summary"] = summary
    verdict = summary.get("go_no_go", {}).get("verdict", "OFFLINE-ONLY")
    report["verdict"] = verdict

    (outd / "smoke-report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print(f"\n==== SMOKE VERDICT: {verdict} ====", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
