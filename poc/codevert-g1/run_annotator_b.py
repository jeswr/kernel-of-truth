#!/usr/bin/env python3
"""Annotator B ("gpt56-b") — gpt-5.6-sol via pinned npx codex invocation.

Per DESIGN-PIN.md sect 4 [PROPOSED-ASM: ASM-1113]: isolation mechanics
reused from poc/gpt56-review/codex-invoke.sh (fresh per-call CODEX_HOME with
auth.json copied in; --ephemeral; memories + web search disabled; read-only
sandbox; empty out-of-repo workdir). Reasoning effort medium (pinned,
disclosed deviation from judge-1p's low). One call per (repo x family)
prompt file; validity = stdout parses to a JSON array whose query_ids match
the batch; <=2 content retries then no-label. 3 parallel workers
(network-bound). Never prints auth contents.
"""
import json, os, re, shutil, subprocess, sys, tempfile, threading, time

BASE = os.path.dirname(os.path.abspath(__file__))
PROMPTS = os.path.join(BASE, "annotation", "prompts")
OUTDIR = os.path.join(BASE, "annotation", "answers-b")
LOGDIR = os.path.join(BASE, "annotation", "b-logs")
PKG = "@openai/codex@0.144.1"
MODEL = "gpt-5.6-sol"
EFFORT = "medium"
WORKERS = 3
lock = threading.Lock()


def extract_json_array(text):
    # strip code fences, find first top-level JSON array
    m = re.search(r"\[[\s\S]*\]", text)
    if not m:
        return None
    # try progressively: largest match first
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def call_codex(prompt_path, log_prefix):
    home = tempfile.mkdtemp(prefix="g1b-home.")
    work = tempfile.mkdtemp(prefix="g1b-work.")
    try:
        shutil.copy(os.path.expanduser("~/.codex/auth.json"),
                    os.path.join(home, "auth.json"))
        os.chmod(os.path.join(home, "auth.json"), 0o600)
        cfg = os.path.expanduser("~/.codex/config.toml")
        if os.path.exists(cfg):
            shutil.copy(cfg, os.path.join(home, "config.toml"))
        env = dict(os.environ, CODEX_HOME=home)
        with open(prompt_path, "rb") as fin, \
             open(log_prefix + ".out", "wb") as fout, \
             open(log_prefix + ".err", "wb") as ferr:
            rc = subprocess.call(
                ["npx", "-y", PKG, "exec", "-m", MODEL,
                 "-c", "model_reasoning_effort=" + EFFORT,
                 "-s", "read-only", "--ignore-user-config",
                 "--skip-git-repo-check", "--ephemeral",
                 "--disable", "memories",
                 "--disable", "standalone_web_search",
                 "-C", work, "--color", "never", "-"],
                stdin=fin, stdout=fout, stderr=ferr, env=env, timeout=1800)
        return rc, open(log_prefix + ".out", "rb").read().decode("utf-8", "replace")
    finally:
        shutil.rmtree(home, ignore_errors=True)
        shutil.rmtree(work, ignore_errors=True)


def expected_ids(prompt_path):
    ids = []
    for line in open(prompt_path):
        m = re.match(r"QUERY (g1q-\S+):", line)
        if m:
            ids.append(m.group(1))
    return ids


def process(batch):
    prompt_path = os.path.join(PROMPTS, batch)
    exp = expected_ids(prompt_path)
    outpath = os.path.join(OUTDIR, batch.replace(".txt", ".json"))
    if os.path.exists(outpath):
        return
    result = {"batch": batch, "annotator": "gpt56-b", "model": MODEL,
              "effort": EFFORT, "attempts": 0, "answers": None,
              "no_label": False}
    for attempt in range(1, 4):
        result["attempts"] = attempt
        lp = os.path.join(LOGDIR, "%s.a%d" % (batch[:-4], attempt))
        try:
            rc, out = call_codex(prompt_path, lp)
        except subprocess.TimeoutExpired:
            with lock:
                print("TIMEOUT", batch, "attempt", attempt, flush=True)
            continue
        arr = extract_json_array(out) if rc == 0 else None
        if isinstance(arr, list) and \
                sorted(a.get("query_id") for a in arr
                       if isinstance(a, dict)) == sorted(exp):
            result["answers"] = arr
            break
        with lock:
            print("INVALID", batch, "attempt", attempt, "rc", rc, flush=True)
    if result["answers"] is None:
        result["no_label"] = True
    with open(outpath, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)
    with lock:
        print("DONE" if not result["no_label"] else "NO-LABEL",
              batch, "attempts", result["attempts"], flush=True)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(LOGDIR, exist_ok=True)
    batches = sorted(p for p in os.listdir(PROMPTS) if p.endswith(".txt"))
    todo = [b for b in batches
            if not os.path.exists(os.path.join(OUTDIR, b.replace(".txt", ".json")))]
    print("batches todo:", len(todo), flush=True)
    q = list(todo)
    qlock = threading.Lock()

    def worker():
        while True:
            with qlock:
                if not q:
                    return
                b = q.pop(0)
            process(b)

    threads = [threading.Thread(target=worker) for _ in range(WORKERS)]
    t0 = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("all done in %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
