#!/usr/bin/env python3
"""
define_concept.py -- STATELESS per-concept runner for the kernel-v1
"define one concept" agent: one capable-model call per concept, strict-JSON
record out, mechanically gated.

  define_concept.py <label> <synset> [--model M] [--out DIR]

  <label>   the concept word/phrase (e.g. "builder", "artist's model")
  <synset>  WN-3.1 synset, "n-09898025" or "urn:lexical-wn31:n-09898025"
  --model   claude-opus-4-8 (default) | claude-fable-5 | gpt-5.6-sol
  --gloss/--pos/--lemmas  override the candidate-pool lookup (for concepts
            outside poc/scale/f1k-eligibility/candidate-pool.json)

What one call does (fail-closed at every step; report, never fake):
  1. resolve the synset row (urn/pos/lemmas/WN gloss) from the benchmark-blind
     candidate pool; assemble the 5-line input block the prompt specifies;
  2. run the model ONCE with the stateless few-shot system prompt
     concept-def-prompt.md (regenerable via build_prompt.py):
       - claude-opus-4-8 / claude-fable-5: the truthstyle section-4.3 headless
         `claude -p` pattern used by the pinned g3 judges
         (poc/g3-llmproxy-v3/opus-pb-rejudge/run-opus-pb-rejudge.py): auth env
         unset => subscription auth, MAX_THINKING_TOKENS=0, --tools ""
         --setting-sources "" --no-session-persistence, stream-json events,
         identity tripwire on init.model/apiKeySource/modelUsage (Haiku
         CLI-sidecar keys allowed, as disclosed there);
       - gpt-5.6-sol: the codex runner pattern of poc/gpt56-review/
         run-review.sh: fresh isolated CODEX_HOME with auth.json copied in,
         npx-pinned @openai/codex@0.144.1, read-only sandbox, --ephemeral,
         model_reasoning_effort=xhigh, --json + -o last-message.json;
     "temperature 0" is discharged exactly as in the pinned judge spec: neither
     CLI exposes a temperature knob; the FIRST VALID answer is final. Non-JSON
     output gets at most MAX_CONTENT fresh attempts (recorded); a JSON record
     that fails a check is NEVER retried -- that is a real capability signal.
  3. strict-JSON extraction: the entire reply must parse as ONE JSON object
     (a single ``` fence is stripped if present and counted as a format
     warning);
  4. mechanical record checks (schema fields, id/slug, synset echo, status,
     label prefix, gloss non-trivial and != WN gloss, notes carries the
     AST-adequacy flag);
  5. the pilot's mechanical gate, via validate-record.mjs -> the encoder's
     validateExplication + single-concept encodeConceptSet (fail-closed);
  6. write out/<slug>.<model-short>.json (the record, verbatim) +
     out/<slug>.<model-short>.report.json (provenance: attempts, latency,
     cost/tokens, sha256s, gate result). Exit 0 iff everything passed.

Governance: benchmark-blind (reads only the pool row; no eval items, no gold
answers, no model outcomes), no git, no registry write, no freeze. colibri
naming; no handles. Author: designer-34.
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROMPT_PATH = HERE / "concept-def-prompt.md"
POOL_PATH = ROOT / "poc/scale/f1k-eligibility/candidate-pool.json"

CLAUDE_MODELS = ("claude-opus-4-8", "claude-fable-5")
CODEX_MODEL = "gpt-5.6-sol"
CODEX_PKG = "@openai/codex@0.144.1"   # npx-pinned, never the global codex
SIDECAR_PREFIX = "claude-haiku-4-5"   # disclosed CLI-internal sidecar allowance
MAX_CONTENT = 3                        # fresh attempts on NON-JSON output only
ALLOWED_FIELDS = ["id", "label", "synset", "pattern", "gloss", "explication",
                  "references", "status", "notes"]
MODEL_SHORT = {"claude-opus-4-8": "opus48", "claude-fable-5": "fable5",
               "gpt-5.6-sol": "gpt56sol"}


def die(msg):
    sys.stderr.write("DEFINE_CONCEPT_ABORT: %s\n" % msg)
    sys.exit(2)


def sha256(b):
    if isinstance(b, str):
        b = b.encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def slugify(label):
    """Frozen slug rule (concept-def-prompt.md §2): lowercase; delete
    apostrophes; non-alphanumeric runs -> '-'; trim '-'."""
    s = label.lower().replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


# ---------------------------------------------------------------------------
# input assembly
# ---------------------------------------------------------------------------
def resolve_synset(arg):
    if re.fullmatch(r"[nvar]-\d{8}", arg):
        return "urn:lexical-wn31:" + arg
    if re.fullmatch(r"urn:lexical-wn31:[nvar]-\d{8}", arg):
        return arg
    die("synset must be like 'n-09898025' or 'urn:lexical-wn31:n-09898025', got %r" % arg)


def pool_row(urn):
    pool = json.load(open(POOL_PATH))
    for x in pool["candidates"]:
        if x["urn"] == urn:
            return x
    return None


def build_user_message(label, urn, pos, lemmas, wn_gloss):
    return (f"concept: {label}\n"
            f"synset: {urn}\n"
            f"pos: {pos}\n"
            f"lemmas: {', '.join(lemmas)}\n"
            f"wn31-gloss (sense-fixing only): {wn_gloss}")


# ---------------------------------------------------------------------------
# model invocation -- claude family (pinned g3-judge headless pattern)
# ---------------------------------------------------------------------------
def run_claude(model, sys_prompt, user_msg, attempt_dir):
    attempt_dir.mkdir(parents=True, exist_ok=True)
    (attempt_dir / "user-prompt.txt").write_text(user_msg)
    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("ANTHROPIC_AUTH_TOKEN", None)
    env["MAX_THINKING_TOKENS"] = "0"
    env["DISABLE_AUTOUPDATER"] = "1"
    cmd = ["claude", "-p", "--model", model,
           "--system-prompt", sys_prompt, "--tools", "",
           "--setting-sources", "", "--no-session-persistence",
           "--output-format", "stream-json", "--verbose"]
    t0 = time.time()
    with open(attempt_dir / "user-prompt.txt", "rb") as fin, \
         open(attempt_dir / "events.jsonl", "wb") as fout, \
         open(attempt_dir / "stderr.log", "wb") as ferr:
        p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=ferr,
                           cwd=str(attempt_dir), env=env)
    latency = time.time() - t0
    init = result = None
    for line in open(attempt_dir / "events.jsonl", encoding="utf-8"):
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
    # STOPCAP (mirrors the pinned judge runner's _cap_hit): a usage/session cap
    # must STOP the run, never retry-spin against the subscription.
    cap_text = " ".join(filter(None, [
        (result or {}).get("result") if isinstance((result or {}).get("result"), str) else None,
        (attempt_dir / "stderr.log").read_text(errors="replace")[-2000:],
    ]))
    if (result or {}).get("api_error_status") == 429 or re.search(
            r"reached your .* limit|usage limit|/usage-credits|rate.?limit", cap_text, re.I):
        die("STOPCAP: usage/session cap hit for %s; STOP (no retry-spin). dir=%s"
            % (model, attempt_dir))
    if p.returncode != 0:
        return None, {"error": "transport rc=%d" % p.returncode, "latency_s": latency}
    if result is None or result.get("subtype") != "success" or result.get("is_error"):
        return None, {"error": "no success result event", "latency_s": latency}
    # identity tripwire (adapted per the pinned opus-pb-rejudge disclosure)
    mu = result.get("modelUsage") or {}
    extra = [k for k in mu if k != model]
    identity_ok = (init and init.get("model") == model
                   and init.get("apiKeySource") == "none"
                   and model in mu
                   and all(k.startswith(SIDECAR_PREFIX) for k in extra))
    if not identity_ok:
        die("identity_mismatch(model=%r apiKeySource=%r modelUsage=%r)"
            % (init.get("model") if init else None,
               init.get("apiKeySource") if init else None, sorted(mu.keys())))
    if (init.get("tools") != [] or (result.get("permission_denials") or []) != []
            or result.get("num_turns") != 1):
        return None, {"error": "tool_use_or_multiturn_detected", "latency_s": latency}
    meta = {
        "latency_s": round(latency, 1),
        "cost_usd": result.get("total_cost_usd"),
        "duration_api_ms": result.get("duration_api_ms"),
        "usage": result.get("usage"),
        "model_usage_keys": sorted(mu.keys()),
    }
    return result.get("result"), meta


# ---------------------------------------------------------------------------
# model invocation -- gpt-5.6-sol (pinned codex isolated-home pattern)
# ---------------------------------------------------------------------------
def run_codex(sys_prompt, user_msg, attempt_dir):
    attempt_dir.mkdir(parents=True, exist_ok=True)
    auth = pathlib.Path.home() / ".codex/auth.json"
    if not auth.exists():
        die("~/.codex/auth.json missing -- cannot carry auth into isolated home")
    base = pathlib.Path(os.environ.get("CODEX_REVIEW_HOME_BASE",
                                       str(pathlib.Path.home() / ".codex-review-homes")))
    base.mkdir(parents=True, exist_ok=True)
    iso = pathlib.Path(tempfile.mkdtemp(prefix="home.", dir=str(base)))
    try:
        shutil.copy(auth, iso / "auth.json")
        os.chmod(iso / "auth.json", 0o600)
        cfg = pathlib.Path.home() / ".codex/config.toml"
        if cfg.exists():
            shutil.copy(cfg, iso / "config.toml")
        # codex exec has no separate system-prompt channel: prepend it.
        full = sys_prompt + "\n\n=== INPUT (define this one concept) ===\n" + user_msg + "\n"
        (attempt_dir / "user-prompt.txt").write_text(full)
        env = dict(os.environ)
        env["CODEX_HOME"] = str(iso)
        cmd = ["npx", "-y", CODEX_PKG, "exec",
               "-m", CODEX_MODEL,
               "-c", "model_reasoning_effort=xhigh",
               "-s", "read-only",
               "--ignore-user-config", "--skip-git-repo-check", "--ephemeral",
               "--disable", "memories", "--disable", "standalone_web_search",
               "-C", str(ROOT), "--color", "never", "--json",
               "-o", str(attempt_dir / "last-message.json"), "-"]
        t0 = time.time()
        with open(attempt_dir / "user-prompt.txt", "rb") as fin, \
             open(attempt_dir / "events.jsonl", "wb") as fout, \
             open(attempt_dir / "stderr.log", "wb") as ferr:
            p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=ferr, env=env)
        latency = time.time() - t0
        if p.returncode != 0:
            return None, {"error": "codex rc=%d" % p.returncode, "latency_s": latency}
        lm = attempt_dir / "last-message.json"
        if not lm.exists():
            return None, {"error": "no last-message.json", "latency_s": latency}
        raw = lm.read_text()
        try:  # -o may hold a JSON-encoded string of the final message
            text = json.loads(raw)
            if not isinstance(text, str):
                text = raw
        except Exception:
            text = raw
        usage = None
        for line in open(attempt_dir / "events.jsonl", encoding="utf-8"):
            try:
                ev = json.loads(line)
            except Exception:
                continue
            u = (ev.get("msg") or {}).get("info") if isinstance(ev.get("msg"), dict) else None
            for cand in (ev.get("usage"), (u or {}).get("total_token_usage")):
                if isinstance(cand, dict):
                    usage = cand
        return text, {"latency_s": round(latency, 1), "cost_usd": None,
                      "usage": usage,
                      "note": "subscription auth; codex reports tokens, not USD"}
    finally:
        shutil.rmtree(iso, ignore_errors=True)


# ---------------------------------------------------------------------------
# strict-JSON extraction + mechanical record checks
# ---------------------------------------------------------------------------
def extract_json(text):
    """The ENTIRE reply must be one JSON object; a single surrounding ``` fence
    is tolerated (recorded as a format warning). No scanning, no repair."""
    if text is None:
        return None, None, "empty reply"
    t = text.strip()
    warn = None
    if t.startswith("```"):
        warn = "reply was fenced despite the no-fences instruction"
        t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    if not t.startswith("{"):
        return None, warn, "reply does not start with '{'"
    try:
        obj = json.loads(t)
    except Exception as e:
        return None, warn, "json parse failure: %s" % e
    if not isinstance(obj, dict):
        return None, warn, "reply is not a JSON object"
    return obj, warn, None


def check_record(rec, label, urn, wn_gloss):
    errs, warns = [], []
    keys = list(rec.keys())
    missing = [k for k in ALLOWED_FIELDS if k not in keys]
    extra = [k for k in keys if k not in ALLOWED_FIELDS]
    if missing:
        errs.append("missing fields: %s" % missing)
    if extra:
        errs.append("unknown fields: %s" % extra)
    slug = slugify(label)
    if rec.get("id") != "urn:kernel-v1:%s" % slug:
        errs.append("id %r != 'urn:kernel-v1:%s'" % (rec.get("id"), slug))
    if not isinstance(rec.get("label"), str) or not rec["label"].startswith(label):
        errs.append("label %r must begin with %r" % (rec.get("label"), label))
    if rec.get("synset") != urn:
        errs.append("synset %r != input %r" % (rec.get("synset"), urn))
    if rec.get("status") != "draft":
        errs.append("status %r != 'draft'" % rec.get("status"))
    if rec.get("references") != []:
        errs.append("references must be []")
    g = rec.get("gloss")
    if not isinstance(g, str) or len(g.split()) < 8:
        errs.append("gloss missing or shorter than 8 words")
    elif g.strip() == wn_gloss.strip():
        errs.append("gloss is the verbatim WN gloss (d2/K collision, pilot-review §4)")
    n = rec.get("notes")
    m = re.match(r"^AST adequacy: (faithful|lossy)\b", n or "")
    if not m:
        errs.append("notes must begin 'AST adequacy: faithful — ' or 'AST adequacy: lossy — '")
    adequacy = m.group(1) if m else None
    if isinstance(g, str) and re.search(r"\b%s" % re.escape(label.split()[0].rstrip("s")),
                                        g, re.IGNORECASE):
        warns.append("gloss may contain the headword or a cognate -- check circularity")
    if not isinstance(rec.get("explication"), dict):
        errs.append("explication missing or not an object")
    return errs, warns, adequacy


def run_gate(record_path):
    p = subprocess.run(["node", str(HERE / "validate-record.mjs"), str(record_path)],
                       capture_output=True, text=True)
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        return {"ok": False, "code": "ERR_GATE_CRASH",
                "error": (p.stderr or p.stdout)[-500:]}


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("synset")
    ap.add_argument("--model", default="claude-opus-4-8",
                    choices=list(CLAUDE_MODELS) + [CODEX_MODEL])
    ap.add_argument("--out", default=str(HERE / "out"))
    ap.add_argument("--gloss", help="WN gloss override (concept outside the pool)")
    ap.add_argument("--pos", help="pos override")
    ap.add_argument("--lemmas", help="comma-separated lemma override")
    args = ap.parse_args()

    urn = resolve_synset(args.synset)
    row = pool_row(urn)
    if row is None and not args.gloss:
        die("synset %s not in candidate-pool.json and no --gloss given (fail-closed)" % urn)
    wn_gloss = args.gloss or row["gloss"]
    pos = args.pos or (row["pos"] if row else urn.split(":")[-1][0])
    lemmas = ([s.strip() for s in args.lemmas.split(",")] if args.lemmas
              else (row["lemmas"] if row else [args.label]))

    sys_prompt = PROMPT_PATH.read_text()
    user_msg = build_user_message(args.label, urn, pos, lemmas, wn_gloss)
    slug = slugify(args.label)
    short = MODEL_SHORT[args.model]
    outdir = pathlib.Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    prov = outdir / "provenance" / f"{slug}.{short}"

    report = {
        "concept": args.label, "synset": urn, "model": args.model,
        "prompt_sha256": sha256(sys_prompt), "user_msg_sha256": sha256(user_msg),
        "attempts": [], "ok": False,
    }

    raw, meta, obj, fmt_warn = None, {}, None, None
    for k in range(1, MAX_CONTENT + 1):
        adir = prov / ("attempt-%d" % k)
        if args.model in CLAUDE_MODELS:
            raw, meta = run_claude(args.model, sys_prompt, user_msg, adir)
        else:
            raw, meta = run_codex(sys_prompt, user_msg, adir)
        obj, fmt_warn, perr = extract_json(raw)
        report["attempts"].append({"n": k, "meta": meta,
                                   "parse_error": perr, "fenced": bool(fmt_warn)})
        if obj is not None:
            break
    if obj is None:
        report["failure"] = "NON-JSON after %d attempt(s); fail-closed, no record written" % len(report["attempts"])
        rp = outdir / f"{slug}.{short}.report.json"
        rp.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        sys.exit(2)

    errs, warns, adequacy = check_record(obj, args.label, urn, wn_gloss)
    if fmt_warn:
        warns.append(fmt_warn)
    record_path = outdir / f"{slug}.{short}.json"
    record_text = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    record_path.write_text(record_text)

    gate = run_gate(record_path)
    report.update({
        "record": str(record_path.relative_to(HERE)) if str(record_path).startswith(str(HERE)) else str(record_path),
        "record_sha256": sha256(record_text),
        "gloss": obj.get("gloss"),
        "ast_adequacy_self_flag": adequacy,
        "mechanical_check_errors": errs,
        "warnings": warns,
        "gate_validateExplication_encode": gate,
        "ok": bool(gate.get("ok")) and not errs,
    })
    rp = outdir / f"{slug}.{short}.report.json"
    rp.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
