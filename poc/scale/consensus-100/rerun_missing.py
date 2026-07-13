#!/usr/bin/env python3
"""rerun_missing.py -- re-run ONLY the missing concept x model cells with a HARD
per-call timeout, classifying each outcome as ok | timeout | cap | refused |
nonjson | error (never an indefinite retry). Refusal text (if any) is captured.

Coverage is a first-class signal: this writes coverage.jsonl with one row per
re-run cell so the report can state per-model completion/refusal/timeout.
$0, no git.
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFINE = ROOT / "poc/scale/concept-def-agent/define_concept.py"
GEN = HERE / "gen"
KOT = pathlib.Path.home() / ".config/kot"
SHORT = {"claude-opus-4-8": "opus48", "claude-fable-5": "fable5",
         "claude-haiku-4-5": "haiku45", "gpt-5.6-sol": "gpt56sol",
         "gpt-5.6-luna": "gpt56luna", "gpt-5.6-terra": "gpt56terra"}
CLAUDE = {"claude-opus-4-8", "claude-fable-5", "claude-haiku-4-5"}
ACCT = {"claude-fable-5": "account2", "claude-opus-4-8": "account3",
        "claude-haiku-4-5": "account4"}
CODEX_TIMEOUT = 300
CLAUDE_TIMEOUT = 150
REFUSAL_RE = re.compile(r"\b(I can'?t|I'?m sorry|I cannot (help|assist|comply|provide)|"
                        r"against .*polic|I won'?t|I am unable to|refuse to)\b", re.I)


def slug(l):
    s = l.lower().replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def token(acct):
    for line in (KOT / (acct + ".env")).read_text().splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[7:]
        if line.startswith("CLAUDE_CODE_OAUTH_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def refusal_text(sl, short):
    """look in the provenance attempts for a non-JSON reply / refusal text."""
    d = GEN / "provenance" / f"{sl}.{short}"
    texts = []
    for att in sorted(d.glob("attempt-*")):
        lm = att / "last-message.json"      # codex
        if lm.exists():
            t = lm.read_text()[:500]
            texts.append(t)
        ev = att / "events.jsonl"           # claude result event
        if ev.exists():
            for line in ev.read_text().splitlines():
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                if e.get("type") == "result" and isinstance(e.get("result"), str):
                    texts.append(e["result"][:500])
    return texts


def run_cell(concept, urn, model):
    sl = slug(concept)
    short = SHORT[model]
    env = dict(os.environ)
    env["DISABLE_AUTOUPDATER"] = "1"
    if model in CLAUDE and model in ACCT:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = token(ACCT[model])
    else:
        env.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
    to = CLAUDE_TIMEOUT if model in CLAUDE else CODEX_TIMEOUT
    cmd = [sys.executable, str(DEFINE), concept, urn, "--model", model, "--out", str(GEN)]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, env=env,
                           cwd=str(ROOT), timeout=to)
        rc, out, err = p.returncode, p.stdout, p.stderr
        timed = False
    except subprocess.TimeoutExpired as e:
        rc, out, err, timed = 124, e.stdout or "", (e.stderr or "") + "\n[TIMEOUT]", True
    dt = round(time.time() - t0, 1)

    rec_ok = (GEN / f"{sl}.{short}.json").exists()
    status = "ok" if rec_ok else "?"
    refusal = None
    if timed:
        status = "timeout"
    elif rec_ok:
        status = "ok"
    elif "STOPCAP" in (err + out):
        status = "cap"
    elif "identity_mismatch" in (err + out):
        status = "error-identity"
    else:
        txts = refusal_text(sl, short)
        if any(REFUSAL_RE.search(t) for t in txts):
            status = "refused"
            refusal = next((t for t in txts if REFUSAL_RE.search(t)), None)
        else:
            status = "nonjson"
            refusal = (txts[0][:300] if txts else (err[-300:] if err else None))
    return {"concept": concept, "urn": urn, "model": model, "status": status,
            "latency_s": dt, "timeout_budget_s": to, "record_written": rec_ok,
            "sample": refusal}


def main():
    data = json.load(open(HERE / "concepts-100.json"))
    by_concept = {r["concept"]: r for r in data["concepts"]}
    # recompute missing cells
    missing = []
    for r in data["concepts"]:
        sl = slug(r["concept"])
        for m in SHORT:
            if not (GEN / f"{sl}.{SHORT[m]}.json").exists():
                missing.append((r["concept"], r["urn"], m))
    print("missing cells to re-run:", len(missing), flush=True)
    covlog = HERE / "coverage-rerun.jsonl"
    results = []
    for concept, urn, model in missing:
        res = run_cell(concept, urn, model)
        results.append(res)
        with open(covlog, "a") as f:
            f.write(json.dumps(res, ensure_ascii=False) + "\n")
        print(f"  {res['status']:14} {concept:14} {model:16} {res['latency_s']}s", flush=True)
    from collections import Counter
    print("\noutcomes:", dict(Counter(r["status"] for r in results)))


if __name__ == "__main__":
    main()
