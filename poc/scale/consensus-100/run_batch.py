#!/usr/bin/env python3
"""run_batch.py -- PARALLEL, checkpointed batch runner for the consensus-100
experiment: 100 concepts x 6 models = 600 stateless define_concept.py calls.

Design:
  * task = (concept_row, model). Records land in gen/<slug>.<short>.json via
    define_concept.py (schema/prompt untouched). Resume = skip any task whose
    record already exists (checkpoint is the on-disk record set + run-log).
  * ThreadPoolExecutor(max_workers) drives subprocesses concurrently.
  * Claude models are spread across the backup OAuth accounts to dodge the
    per-account/per-model usage cap and to parallelise:
        opus48 -> account3, fable5 -> account2, haiku45 -> account4,
    each with a fallback chain (other accounts, then this session #1).
    A (account, model) that STOPCAPs is marked exhausted and skipped thereafter.
  * Codex models (gpt-5.6-*) use ~/.codex/auth.json; no Claude account needed;
    subscription marginal cost = $0 (codex reports tokens, not USD).
  * Per-account concurrency is bounded by a semaphore so we never slam one
    subscription.

$0 marginal (all subscription auth), no git, no registry.
"""
import argparse
import json
import os
import pathlib
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFINE = ROOT / "poc/scale/concept-def-agent/define_concept.py"
GEN = HERE / "gen"
RUNLOG = HERE / "run-log.jsonl"
KOT = pathlib.Path.home() / ".config/kot"

MODEL_SHORT = {"claude-opus-4-8": "opus48", "claude-fable-5": "fable5",
               "claude-haiku-4-5": "haiku45",
               "gpt-5.6-sol": "gpt56sol", "gpt-5.6-luna": "gpt56luna",
               "gpt-5.6-terra": "gpt56terra"}
CLAUDE_MODELS = {"claude-opus-4-8", "claude-fable-5", "claude-haiku-4-5"}
MODELS = ["claude-opus-4-8", "claude-fable-5", "claude-haiku-4-5",
          "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.6-terra"]

# Claude-model account chains. "#1" = this session's ~/.claude (no token env).
ACCT_CHAIN = {
    "claude-opus-4-8":  ["account3", "account4", "account2", "#1"],
    "claude-fable-5":   ["account2", "account3", "account4"],  # #1 fable is capped
    "claude-haiku-4-5": ["account4", "account2", "account3", "#1"],
}
MAX_PER_ACCT = 3  # concurrent claude subprocesses per account

_acct_tokens = {}       # account name -> CLAUDE_CODE_OAUTH_TOKEN value (never logged)
_acct_sems = {}         # account name -> Semaphore
_exhausted = set()      # (account, model) known-capped
_lock = threading.Lock()
_log_lock = threading.Lock()


def load_token(acct):
    """Read CLAUDE_CODE_OAUTH_TOKEN from ~/.config/kot/<acct>.env (never print)."""
    p = KOT / (acct + ".env")
    if not p.exists():
        return None
    for line in p.read_text().splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[len("export "):]
        if line.startswith("CLAUDE_CODE_OAUTH_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def init_accounts():
    accts = {a for chain in ACCT_CHAIN.values() for a in chain}
    for a in accts:
        _acct_sems[a] = threading.Semaphore(MAX_PER_ACCT)
        if a != "#1":
            tok = load_token(a)
            if tok:
                _acct_tokens[a] = tok
            else:
                # missing token -> treat as permanently exhausted for all models
                for m in CLAUDE_MODELS:
                    _exhausted.add((a, m))


def record_exists(row, model):
    short = MODEL_SHORT[model]
    slug = slug_of(row["concept"])
    return (GEN / f"{slug}.{short}.json").exists()


def slug_of(label):
    import re
    s = label.lower().replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def append_log(obj):
    with _log_lock:
        with open(RUNLOG, "a") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def run_one_call(row, model, acct):
    """Invoke define_concept.py for (concept, model) under `acct` env.
    Returns (rc, stdout_path, stderr_text, latency)."""
    env = dict(os.environ)
    env["DISABLE_AUTOUPDATER"] = "1"
    if model in CLAUDE_MODELS and acct != "#1":
        env["CLAUDE_CODE_OAUTH_TOKEN"] = _acct_tokens[acct]
    else:
        env.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
    cmd = [sys.executable, str(DEFINE), row["concept"], row["urn"],
           "--model", model, "--out", str(GEN)]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(ROOT))
    dt = time.time() - t0
    return p.returncode, p.stdout, p.stderr, dt


def do_task(row, model):
    slug = slug_of(row["concept"])
    short = MODEL_SHORT[model]
    if record_exists(row, model):
        return {"concept": row["concept"], "model": model, "status": "skip-exists"}

    chains = ACCT_CHAIN.get(model, ["codex"])
    last_err = None
    for acct in chains:
        if model in CLAUDE_MODELS:
            with _lock:
                if (acct, model) in _exhausted:
                    continue
            sem = _acct_sems[acct]
            sem.acquire()
            try:
                rc, out, err, dt = run_one_call(row, model, acct)
            finally:
                sem.release()
        else:
            rc, out, err, dt = run_one_call(row, model, "codex")

        capped = ("STOPCAP" in (err or "")) or ("STOPCAP" in (out or ""))
        if capped and model in CLAUDE_MODELS:
            with _lock:
                _exhausted.add((acct, model))
            last_err = "STOPCAP@%s" % acct
            append_log({"ts": time.time(), "concept": row["concept"], "model": model,
                        "acct": acct, "status": "capped", "latency_s": round(dt, 1)})
            continue  # try next account

        # parse cost/ok from report
        cost, ok, gate_ok = None, None, None
        rp = GEN / f"{slug}.{short}.report.json"
        if rp.exists():
            try:
                rep = json.load(open(rp))
                ok = rep.get("ok")
                atts = rep.get("attempts") or []
                if atts:
                    cost = (atts[-1].get("meta") or {}).get("cost_usd")
                gate_ok = (rep.get("gate_validateExplication_encode") or {}).get("ok")
            except Exception:
                pass
        rec_ok = (GEN / f"{slug}.{short}.json").exists()
        result = {"ts": time.time(), "concept": row["concept"], "model": model,
                  "acct": acct if model in CLAUDE_MODELS else "codex",
                  "rc": rc, "record_written": rec_ok, "ok": ok, "gate_ok": gate_ok,
                  "cost_usd": cost, "latency_s": round(dt, 1),
                  "status": "done" if rec_ok else "fail",
                  "err_tail": (err or "")[-300:] if not rec_ok else None}
        append_log(result)
        return result

    # all accounts exhausted / failed
    res = {"ts": time.time(), "concept": row["concept"], "model": model,
           "status": "gap", "reason": last_err or "no-account"}
    append_log(res)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0, help="cap #concepts (debug)")
    ap.add_argument("--models", default="", help="comma-list to restrict models")
    args = ap.parse_args()

    GEN.mkdir(parents=True, exist_ok=True)
    init_accounts()
    data = json.load(open(HERE / "concepts-100.json"))
    rows = data["concepts"]
    if args.limit:
        rows = rows[: args.limit]
    models = args.models.split(",") if args.models else MODELS

    # interleave (concept-major, model-minor) so accounts aren't slammed in bursts
    tasks = [(r, m) for r in rows for m in models]
    todo = [(r, m) for (r, m) in tasks if not record_exists(r, m)]
    print(f"total tasks={len(tasks)} already-done={len(tasks)-len(todo)} todo={len(todo)} "
          f"workers={args.workers}", flush=True)

    t0 = time.time()
    done = capped = gap = fail = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(do_task, r, m): (r["concept"], m) for (r, m) in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            res = fut.result()
            st = res.get("status")
            if st == "done":
                done += 1
            elif st == "gap":
                gap += 1
            elif st == "fail":
                fail += 1
            if i % 10 == 0 or st in ("gap", "fail"):
                el = time.time() - t0
                print(f"[{i}/{len(todo)}] {res['concept'][:20]:20} {res['model']:18} "
                      f"{st:10} done={done} gap={gap} fail={fail} elapsed={el:.0f}s",
                      flush=True)
    el = time.time() - t0
    print(f"\nFINISHED todo={len(todo)} done={done} gap={gap} fail={fail} wall={el:.0f}s",
          flush=True)
    with _lock:
        if _exhausted:
            print("exhausted (account,model):", sorted(_exhausted), flush=True)


if __name__ == "__main__":
    main()
