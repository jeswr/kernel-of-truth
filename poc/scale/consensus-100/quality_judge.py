#!/usr/bin/env python3
"""quality_judge.py -- BLIND, dual-judge definitional-QUALITY ranking over the
consensus-100 glosses.

For each of the 100 concepts:
  * take the 6 model glosses, ANONYMIZE + SHUFFLE with a deterministic
    per-concept permutation (seed + concept string; NO wall-clock randomness);
  * present the anonymized set (labels G1..Gn) + concept + WN synset/gloss to
    two INDEPENDENT judges, each scoring EVERY gloss 0-3 on the scholarly
    definition bar;
      Judge A = gpt-5.6-sol  (codex isolated-home pattern, read-only, $0 sub)
      Judge B = claude-opus-4-8 (claude -p define_concept.py pattern, $0 sub)
  * de-anonymize -> attach each score to its true model.

Blind: judges never see model identities, order is shuffled, and one gloss per
concept is (for the sol/opus judges) their own -- hence the anonymization.

Checkpointed: each (concept, judge) result is appended to a per-judge JSONL the
moment it lands; a re-run skips any (concept, judge) already present. If a judge
model caps mid-run, we stop that judge and finalize on what completed.

$0 marginal (subscription auth), no git, no registry.
"""
import argparse
import hashlib
import json
import os
import pathlib
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONSENSUS = HERE / "consensus.json"
CONCEPTS = HERE / "concepts-100.json"
CODEX_PKG = "@openai/codex@0.144.1"
KOT = pathlib.Path.home() / ".config/kot"

MODELS = ["claude-opus-4-8", "claude-fable-5", "claude-haiku-4-5",
          "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.6-terra"]

JUDGES = {
    "A": {"kind": "codex", "model": "gpt-5.6-sol"},
    "B": {"kind": "claude", "model": "claude-opus-4-8"},
}

# opus account fallback chain (mirrors run_batch.py). "#1" = this session's
# ~/.claude (no token env). fable's #1 is capped; opus #1 is fine.
ACCT_CHAIN = ["account3", "account4", "account2", "#1"]
MAX_PER_ACCT = 2
CODEX_CONCURRENCY = 4

_acct_tokens = {}
_acct_sems = {}
_codex_sem = threading.Semaphore(CODEX_CONCURRENCY)
_exhausted = set()          # (acct, model) known-capped
_judge_capped = set()       # judge-id fully capped -> stop scheduling it
_lock = threading.Lock()
_write_locks = {}

SYS_PROMPT = (
    "You are a professional lexicographer applying a strict scholarly-definition "
    "standard. You reply with EXACTLY one JSON object and nothing else."
)

PROMPT_TMPL = """You are scoring candidate DICTIONARY DEFINITIONS of one concept for QUALITY.

Concept word: {label}
Part of speech: {pos}
Lemmas: {lemmas}
WordNet 3.1 synset: {urn}
WordNet 3.1 gloss (authoritative SENSE-FIXING reference -- it pins WHICH sense of the word is meant; it is terse and is NOT itself a model of good lexicographic style): {wn_gloss}

Below are {n} independently-written candidate definitions of exactly this sense of "{label}", labelled [G1]..[G{n}]. Score EACH one, independently, 0-3 on definitional QUALITY against the scholarly-definition bar:

  3 = excellent, first-rate lexicographic definition: sense-correct, non-circular, correct extension (neither too broad nor too narrow), apt and economical wording, no unnecessary information.
  2 = good: sense-correct and usable, with only minor stylistic or scope imperfections.
  1 = correct sense but poor: clumsy register, padded / verbose, or mildly mis-scoped (slightly too broad or too narrow).
  0 = wrong: wrong sense, circular (defines the word by itself / a cognate), or broken/incoherent.

Judge each gloss ON ITS OWN MERITS against the fixed sense. Do NOT grade on a curve and do NOT reward mere agreement between the glosses; several may deserve the same score, and all may be excellent or all poor.

Definitions:
{items}

Reply with EXACTLY one JSON object, no prose, no code fences, one entry per label:
{{"G1": {{"score": <int 0-3>, "reason": "<=12 words"}}, ... , "G{n}": {{"score": <int 0-3>, "reason": "..."}}}}
"""


# --------------------------------------------------------------------------
def load_token(acct):
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
    for a in ACCT_CHAIN:
        _acct_sems[a] = threading.Semaphore(MAX_PER_ACCT)
        if a != "#1":
            tok = load_token(a)
            if tok:
                _acct_tokens[a] = tok
            else:
                _exhausted.add((a, "claude-opus-4-8"))


def extract_json(text):
    if not text:
        return None
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    m = re.search(r"\{.*\}", t, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        # tolerate trailing junk: greedily shrink
        s = m.group(0)
        while s:
            try:
                return json.loads(s)
            except Exception:
                nb = s.rfind("}")
                if nb <= 0:
                    return None
                s = s[:nb]
        return None


# --------------------------------------------------------------------------
def codex_call(model, prompt):
    auth = pathlib.Path.home() / ".codex/auth.json"
    base = pathlib.Path(os.environ.get(
        "CODEX_REVIEW_HOME_BASE", str(pathlib.Path.home() / ".codex-review-homes")))
    base.mkdir(parents=True, exist_ok=True)
    iso = pathlib.Path(tempfile.mkdtemp(prefix="qjudge.", dir=str(base)))
    try:
        shutil.copy(auth, iso / "auth.json")
        os.chmod(iso / "auth.json", 0o600)
        cfg = pathlib.Path.home() / ".codex/config.toml"
        if cfg.exists():
            shutil.copy(cfg, iso / "config.toml")
        env = dict(os.environ)
        env["CODEX_HOME"] = str(iso)
        out = iso / "last.json"
        cmd = ["npx", "-y", CODEX_PKG, "exec", "-m", model,
               "-c", "model_reasoning_effort=high", "-s", "read-only",
               "--ignore-user-config", "--skip-git-repo-check", "--ephemeral",
               "--disable", "memories", "--disable", "standalone_web_search",
               "-C", str(ROOT), "--color", "never", "--json", "-o", str(out), "-"]
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, env=env)
        err_tail = (p.stderr or "")[-400:]
        if re.search(r"usage limit|rate.?limit|quota|429|too many requests", err_tail, re.I):
            return None, {"stopcap": True, "error": "codex cap: " + err_tail}
        if not out.exists():
            return None, {"error": "no last-message rc=%d %s" % (p.returncode, err_tail)}
        raw = out.read_text()
        try:
            text = json.loads(raw)
            if not isinstance(text, str):
                text = raw
        except Exception:
            text = raw
        return text, {"error": None}
    finally:
        shutil.rmtree(iso, ignore_errors=True)


def claude_call(model, sys_prompt, user_msg, acct):
    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("ANTHROPIC_AUTH_TOKEN", None)
    env["MAX_THINKING_TOKENS"] = "0"
    env["DISABLE_AUTOUPDATER"] = "1"
    if acct != "#1":
        env["CLAUDE_CODE_OAUTH_TOKEN"] = _acct_tokens[acct]
    else:
        env.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
    iso = pathlib.Path(tempfile.mkdtemp(prefix="cjudge.", dir="/tmp"))
    try:
        cmd = ["claude", "-p", "--model", model,
               "--system-prompt", sys_prompt, "--tools", "",
               "--setting-sources", "", "--no-session-persistence",
               "--output-format", "stream-json", "--verbose"]
        events = iso / "events.jsonl"
        errlog = iso / "stderr.log"
        with open(events, "wb") as fout, open(errlog, "wb") as ferr:
            p = subprocess.run(cmd, input=user_msg.encode(), stdout=fout,
                               stderr=ferr, cwd=str(iso), env=env)
        init = result = None
        for line in open(events, encoding="utf-8", errors="replace"):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            if ev.get("type") == "system" and ev.get("subtype") == "init":
                init = ev
            elif ev.get("type") == "result":
                result = ev
        cap_text = " ".join(filter(None, [
            (result or {}).get("result") if isinstance((result or {}).get("result"), str) else None,
            errlog.read_text(errors="replace")[-2000:],
        ]))
        if (result or {}).get("api_error_status") == 429 or re.search(
                r"reached your .* limit|usage limit|/usage-credits|rate.?limit", cap_text, re.I):
            return None, {"stopcap": True, "error": "claude cap on %s" % acct}
        if p.returncode != 0:
            return None, {"error": "transport rc=%d %s" % (p.returncode, cap_text[-200:])}
        if result is None or result.get("subtype") != "success" or result.get("is_error"):
            return None, {"error": "no success result event"}
        return result.get("result"), {"error": None,
                                       "cost_usd": result.get("total_cost_usd"),
                                       "acct": acct}
    finally:
        shutil.rmtree(iso, ignore_errors=True)


# --------------------------------------------------------------------------
def build_anon(pc, seed):
    """Deterministic per-concept anonymization. Returns (order, label_map, items)
    where order[i] = model at position i (0-based) -> label G{i+1}."""
    present = [m for m in MODELS if m in pc["glosses"] and (pc["glosses"][m] or "").strip()]
    h = hashlib.sha256(("%d|%s" % (seed, pc["concept"])).encode()).hexdigest()
    rng = random.Random(int(h, 16))
    order = present[:]
    rng.shuffle(order)
    label_map = {"G%d" % (i + 1): order[i] for i in range(len(order))}
    items = "\n".join("[G%d] %s" % (i + 1, pc["glosses"][order[i]]) for i in range(len(order)))
    return order, label_map, items


def parse_scores(obj, label_map):
    """Return {model: int score} from a judge JSON obj keyed by G-labels."""
    if not isinstance(obj, dict):
        return None
    out = {}
    for lbl, model in label_map.items():
        v = obj.get(lbl)
        if v is None:
            # tolerate bare-int forms / lowercase keys
            v = obj.get(lbl.lower())
        if isinstance(v, dict):
            v = v.get("score")
        try:
            s = int(round(float(v)))
        except (TypeError, ValueError):
            return None
        if s < 0 or s > 3:
            return None
        out[model] = s
    if len(out) != len(label_map):
        return None
    return out


def run_claude_with_fallback(prompt_user):
    for acct in ACCT_CHAIN:
        with _lock:
            if (acct, "claude-opus-4-8") in _exhausted:
                continue
        sem = _acct_sems[acct]
        sem.acquire()
        try:
            text, meta = claude_call("claude-opus-4-8", SYS_PROMPT, prompt_user, acct)
        finally:
            sem.release()
        if meta.get("stopcap"):
            with _lock:
                _exhausted.add((acct, "claude-opus-4-8"))
            continue
        return text, meta
    with _lock:
        _judge_capped.add("B")
    return None, {"stopcap": True, "error": "all opus accounts exhausted"}


def load_done(path):
    done = set()
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if rec.get("scores_by_model") is not None:
                    done.add(rec["concept"])
            except Exception:
                pass
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260713)
    ap.add_argument("--limit", type=int, default=0, help="0 = all concepts")
    ap.add_argument("--judges", default="A,B")
    args = ap.parse_args()
    init_accounts()

    con = json.load(open(CONSENSUS))
    pcs = con["per_concept"]
    if args.limit:
        pcs = pcs[:args.limit]
    concepts = json.load(open(CONCEPTS))["concepts"]
    byurn = {c["urn"]: c for c in concepts}

    active = [j for j in args.judges.split(",") if j in JUDGES]
    out_paths = {j: HERE / ("quality-raw-judge%s.jsonl" % j) for j in active}
    for j in active:
        _write_locks[j] = threading.Lock()
    done = {j: load_done(out_paths[j]) for j in active}
    for j in active:
        print("judge %s: %d already done" % (j, len(done[j])), flush=True)

    # precompute anon per concept (shared across judges)
    anon = {}
    for pc in pcs:
        order, label_map, items = build_anon(pc, args.seed)
        row = byurn.get(pc["urn"], {})
        prompt = PROMPT_TMPL.format(
            label=pc["concept"], pos=row.get("pos", "?"),
            lemmas=", ".join(row.get("lemmas", [pc["concept"]])),
            urn=pc["urn"], wn_gloss=row.get("wn31_gloss", "(none)"),
            n=len(order), items=items)
        anon[pc["concept"]] = {"order": order, "label_map": label_map, "prompt": prompt}

    tasks_by_judge = {j: [pc for pc in pcs if pc["concept"] not in done[j]] for j in active}
    for j in active:
        print("judge %s: %d tasks to run" % (j, len(tasks_by_judge[j])), flush=True)

    def do_task(j, pc):
        with _lock:
            if j in _judge_capped:
                return j, pc["concept"], "capped-skip"
        a = anon[pc["concept"]]
        prompt = a["prompt"]
        if JUDGES[j]["kind"] == "codex":
            _codex_sem.acquire()
            try:
                text, meta = codex_call(JUDGES[j]["model"], SYS_PROMPT + "\n\n" + prompt)
            finally:
                _codex_sem.release()
            if meta.get("stopcap"):
                with _lock:
                    _judge_capped.add(j)
        else:
            text, meta = run_claude_with_fallback(prompt)
        obj = extract_json(text)
        scores = parse_scores(obj, a["label_map"]) if obj else None
        rec = {
            "concept": pc["concept"], "urn": pc["urn"],
            "stratum": pc.get("stratum"), "judge": j,
            "judge_model": JUDGES[j]["model"],
            "label_map": a["label_map"],
            "scores_by_model": scores,
            "reasons": {a["label_map"][k]: (obj.get(k) or {}).get("reason")
                        for k in a["label_map"]} if (obj and scores) else None,
            "error": None if scores else (meta.get("error") or "unparseable"),
            "raw": None if scores else (text or "")[:500],
            "meta": {k: meta.get(k) for k in ("cost_usd", "acct", "stopcap")},
        }
        with _write_locks[j]:
            with open(out_paths[j], "a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        status = "ok" if scores else ("CAP" if meta.get("stopcap") else "ERR")
        return j, pc["concept"], status

    # Run each judge in its OWN concurrent pool so the two judges never starve
    # each other (a shared pool + a codex semaphore would block worker slots and
    # starve the claude judge). Pool sizes match each judge's real concurrency.
    t0 = time.time()
    counts = {"ok": 0, "ERR": 0, "CAP": 0, "capped-skip": 0}
    counts_lock = threading.Lock()
    pool_size = {"A": CODEX_CONCURRENCY, "B": MAX_PER_ACCT * len(ACCT_CHAIN)}
    total = sum(len(tasks_by_judge[j]) for j in active)
    prog = {"i": 0}

    def run_judge_pool(j):
        tk = tasks_by_judge[j]
        if not tk:
            return
        with ThreadPoolExecutor(max_workers=pool_size[j]) as ex:
            futs = [ex.submit(do_task, j, pc) for pc in tk]
            for fut in as_completed(futs):
                try:
                    jj, concept, status = fut.result()
                except Exception as e:
                    print("task exception:", e, flush=True)
                    continue
                with counts_lock:
                    counts[status] = counts.get(status, 0) + 1
                    prog["i"] += 1
                    i = prog["i"]
                if i % 10 == 0 or status != "ok":
                    print("[%4d/%d] %.0fs judge=%s %-16s %s  (ok=%d err=%d cap=%d)" %
                          (i, total, time.time() - t0, jj, concept[:16], status,
                           counts["ok"], counts["ERR"], counts["CAP"] + counts["capped-skip"]),
                          flush=True)

    pool_threads = [threading.Thread(target=run_judge_pool, args=(j,), daemon=True)
                    for j in active]
    for th in pool_threads:
        th.start()
    for th in pool_threads:
        th.join()

    print("DONE", json.dumps(counts), flush=True)
    for j in active:
        with _lock:
            capped = j in _judge_capped
        print("judge %s capped=%s exhausted-accts=%s" %
              (j, capped, sorted(a for (a, m) in _exhausted)), flush=True)


if __name__ == "__main__":
    main()
