#!/usr/bin/env python3
"""F1-K PINNED + concept-batched load-excluded per-prefill measurement.
Read-only w.r.t. frozen artifacts. Writes only under ~/f1k-pinmeas/.
Reuses the engine invocation contract from f1k_worker.sh run_gate_sample."""
import json, os, re, subprocess, sys, time, hashlib

HOME = os.path.expanduser("~")
ESTATE = "/mnt/nvme/glm52_i4"
ENGINE = HOME + "/colibri-score/c/glm"
TOKWRAP = HOME + "/f1k/tok_glm52.py"
TOKJSON = ESTATE + "/tokenizer.json"
GATEPY = HOME + "/f1k/f1k_bringup_gate.py"
MANIFEST = HOME + "/f1k/data/f1k-carriers-v1/generator/construction-manifest.jsonl"
TESTJSONL = HOME + "/f1k/data/f1k-eval-v1/items/test.jsonl"
S001 = HOME + "/f1k-gate/t1-stats/.stats-s001.QRsQAP.tmp"  # bring-up construction-row routing (extra pin breadth)

OUT = HOME + "/f1k-pinmeas"
os.makedirs(OUT, exist_ok=True)
CONT_TOKENS = 8
PIN_GB = float(os.environ.get("PIN_GB", "40"))
OMP = str(os.environ.get("OMP", "8"))
PER_RUN_TIMEOUT = int(os.environ.get("PER_RUN_TIMEOUT", "4200"))
TOK_SHA = hashlib.sha256(open(TOKJSON, "rb").read()).hexdigest()

results = {"meta": {"pin_gb": PIN_GB, "omp": OMP, "cont_tokens": CONT_TOKENS,
                    "tokenizer_sha256": TOK_SHA, "engine": ENGINE,
                    "estate": ESTATE, "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
           "phases": {}}
RES_PATH = OUT + "/results.json"

def save():
    json.dump(results, open(RES_PATH, "w"), indent=2)

def log(m):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), m)
    print(line, flush=True)

def tokenize(texts):
    """Call the pinned kot-f1k-tok/1 wrapper exactly as the gate does."""
    env = dict(os.environ, TOK_SHA256=TOK_SHA)
    p = subprocess.Popen([sys.executable, TOKWRAP, TOKJSON],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
    inp = "".join(json.dumps({"text": t}) + "\n" for t in texts)
    out, _ = p.communicate(inp.encode("utf-8"))
    if p.returncode != 0:
        raise SystemExit("tok wrapper exit %d" % p.returncode)
    return [json.loads(l)["ids"] for l in out.decode("utf-8").splitlines()]

def write_score(path, texts):
    """Write a run_score manifest: one line per text, ctx=T ids + 8 cont ids
    (last id repeated) => engine processes Tp=T+8 tokens (the projection unit)."""
    id_lists = tokenize(texts)
    lines, tlens = [], []
    for ids in id_lists:
        if len(ids) < 2:
            continue
        cont = [ids[-1]] * CONT_TOKENS
        lines.append("%d %d %s" % (len(ids), CONT_TOKENS,
                                   " ".join(map(str, ids + cont))))
        tlens.append(len(ids))
    open(path, "w").write("\n".join(lines) + "\n")
    return tlens

TIMER_RE = re.compile(r"\[score (\d+) req \| ([\d.]+)s \| RSS ([\d.]+) GB \| hit (\d+)%")

def run_engine(name, score_path, n_rows, stats=None, pin=None):
    env = dict(os.environ)
    for k in ["KAE","KAE_G","KAE_SCORE","KAE_DUMP","KAE_CARRIER","KAE_SPANS",
              "KAE_MODE","KAE_SEED","KAE_DUMP_LAYERS"]:
        env.pop(k, None)
    env.update({"SNAP": ESTATE, "SCORE": score_path, "OMP_NUM_THREADS": OMP,
                "OMP_DYNAMIC": "FALSE", "OMP_PROC_BIND": "close",
                "OMP_WAIT_POLICY": "active", "COLI_OMP_TUNED": "1"})
    if stats:
        env["STATS"] = stats
    if pin:
        env["PIN"] = pin
        env["PIN_GB"] = str(PIN_GB)
    outf = OUT + "/%s.out" % name
    errf = OUT + "/%s.err" % name
    log("RUN %s: rows=%d pin=%s stats=%s" % (name, n_rows, bool(pin), bool(stats)))
    t0 = time.time()
    timed_out = False
    with open(outf, "w") as so, open(errf, "w") as se:
        try:
            subprocess.run([ENGINE, "64", "4", "8"], env=env, stdout=so,
                           stderr=se, timeout=PER_RUN_TIMEOUT)
        except subprocess.TimeoutExpired:
            timed_out = True
    wall = time.time() - t0
    err = open(errf, encoding="utf-8", errors="replace").read()
    boundaries = [{"n": int(m[0]), "cum_s": float(m[1]), "rss_gb": float(m[2]),
                   "hit_pct": int(m[3])} for m in TIMER_RE.findall(err)]
    pin_ev = [l for l in err.splitlines() if "[PIN]" in l or "pinning DISABLED" in l]
    cap_ln = [l for l in err.splitlines() if "cap lowered" in l or "RAM_GB=" in l]
    rec = {"rows": n_rows, "wall_s": round(wall, 1), "timed_out": timed_out,
           "boundaries": boundaries, "pin_evidence": pin_ev[:4],
           "cap_line": cap_ln[:2]}
    # per-prefill: overall = last cum / last n ; warm = (cum10-cum5)/(n10-n5)
    if boundaries:
        b = boundaries[-1]
        rec["overall_s_per_prefill"] = round(b["cum_s"] / b["n"], 2)
        rec["final_hit_pct"] = b["hit_pct"]
        if len(boundaries) >= 2:
            a, c = boundaries[0], boundaries[-1]
            rec["warm_s_per_prefill"] = round((c["cum_s"] - a["cum_s"]) / (c["n"] - a["n"]), 2)
    results["phases"][name] = rec
    save()
    log("  -> %s boundaries=%s overall_spp=%s warm_spp=%s hit=%s%%" % (
        name, [(b["n"], b["cum_s"], b["hit_pct"]) for b in boundaries],
        rec.get("overall_s_per_prefill"), rec.get("warm_s_per_prefill"),
        rec.get("final_hit_pct")))
    return rec

# ---- build batches ----------------------------------------------------------
def load_construction(slot, limit):
    rows = []
    for ln in open(MANIFEST, encoding="utf-8"):
        r = json.loads(ln)
        if r["carrier_slot"] == slot:
            rows.append(r["text"])
            if len(rows) >= limit:
                break
    return rows

def load_construction_pinsrc(slots):
    """one with_k row per slot (broad routing for the pin)."""
    want = set(slots); got = {}
    for ln in open(MANIFEST, encoding="utf-8"):
        r = json.loads(ln)
        if r["carrier_slot"] in want and r["variant"] == "with_k" and r["carrier_slot"] not in got:
            got[r["carrier_slot"]] = r["text"]
        if len(got) == len(want):
            break
    return [got[s] for s in slots if s in got]

def load_eval_cluster(cluster, limit):
    texts = []
    for ln in open(TESTJSONL, encoding="utf-8"):
        r = json.loads(ln)
        if r.get("cluster") == cluster:
            texts.append(r["template_text"])
            if len(texts) >= limit:
                break
    return texts

log("PIN_GB=%.1f OMP=%s tok_sha=%s" % (PIN_GB, OMP, TOK_SHA[:12]))

# batches
pinsrc_texts = load_construction_pinsrc([1,2,3,4,5,6,7,8])
c0_texts     = load_construction(0, 10)          # concept "wrong" construction rows
ev_texts     = load_eval_cluster("urn:kernel-v0:wrong", 10)

pinsrc_score = OUT + "/pinsrc.score"
c0_score     = OUT + "/c0.score"
ev_score     = OUT + "/ev.score"
tl_pin = write_score(pinsrc_score, pinsrc_texts)
tl_c0  = write_score(c0_score, c0_texts)
tl_ev  = write_score(ev_score, ev_texts)
results["meta"]["batch_token_lengths"] = {
    "pinsrc_construction_c1-8_with_k": tl_pin,
    "c0_construction_concept_wrong": tl_c0,
    "eval_cluster_wrong_template": tl_ev}
save()
log("batches built: pinsrc T=%s | c0 T=%s | eval T=%s" % (tl_pin, tl_c0, tl_ev))
if os.environ.get("DRY") == "1":
    log("DRY=1: batches built, exiting before engine runs.")
    sys.exit(0)

# ---- Phase 1: pin-source routing (UNPINNED, STATS) --------------------------
stats_pin = OUT + "/stats_pinsrc.txt"
if os.path.exists(stats_pin):
    os.remove(stats_pin)
run_engine("pinsrc", pinsrc_score, len(pinsrc_texts), stats=stats_pin)

# ---- build the pin file at PIN_GB from construction routing (transfer pin) ---
# manifest lists the pin-source stats + the bring-up s001 construction-row stats
manifest = OUT + "/pin.manifest"
lines = []
if os.path.getsize(stats_pin) > 0:
    lines.append(stats_pin)
if os.path.exists(S001) and os.path.getsize(S001) > 0:
    lines.append(S001)
open(manifest, "w").write("\n".join(lines) + "\n")
pin_file = OUT + "/pin.stats"
pj = subprocess.run([sys.executable, GATEPY, "pinfile", "--stats-manifest", manifest,
                     "--pin-gb", str(PIN_GB), "--out", pin_file],
                    capture_output=True, text=True)
log("pinfile rc=%d out=%s err=%s" % (pj.returncode, pj.stdout.strip()[:300], pj.stderr.strip()[:300]))
try:
    results["meta"]["pin"] = json.loads(pj.stdout.strip().splitlines()[-1])
    results["meta"]["pin"]["stats_manifest"] = lines
except Exception as e:
    results["meta"]["pin_error"] = str(e) + " :: " + pj.stdout[-300:] + pj.stderr[-300:]
save()

# ---- decisive-first ordering: pinned before unpinned per regime -------------
run_engine("c0_pinned",   c0_score, len(c0_texts), pin=pin_file)
run_engine("c0_unpinned", c0_score, len(c0_texts), stats=OUT + "/stats_c0.txt")
run_engine("ev_pinned",   ev_score, len(ev_texts), pin=pin_file)
run_engine("ev_unpinned", ev_score, len(ev_texts), stats=OUT + "/stats_ev.txt")

results["meta"]["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
save()
log("DONE. results at %s" % RES_PATH)
