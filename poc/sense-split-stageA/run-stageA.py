#!/usr/bin/env python3
"""run-stageA.py -- MECHANICAL executor of the sense-split Stage-A V-A + V-B
measurements (docs/next/design/sense-split-first-construction.md section 5;
Stage-A GO ruling ASM-1909; assumption block data/kernel-v1/asm-stageA-*.json).
Faithful port of the audited poc/ontology-import-g2-v2/run-ontg2v2.py judge
machinery: identical invocation forms, validity/retry/no-label contracts,
blinding scans, checkpointing, live dollar abort. DESIGNS NOTHING, CONCLUDES
NOTHING. LAUNCH-READY, HELD: real phases refuse to run without BOTH
  (i)  SSA_MAINTAINER_GO=1 in the environment (the maintainer's explicit go
       on the section-A redirect -- the ~$10 spend is NOT approved by the
       build), and
  (ii) --channel proxy | human (the adjudication section-D pre-commitment:
       the GPT-5.6+Opus proxy pair judges these materials ONLY if the v2.2
       pilot passed AC1>=0.65; else the same materials go to the two-human
       panel and this driver's judge phases are NOT used).

Protocol (proxy channel):
  judge-pA  gpt-5.6-sol via npx-pinned openai codex CLI 0.144.1, reasoning
            effort low, read-only, ephemeral, server-side output schema
            (PRIMARY construction)
  judge-pB  claude-opus-4-8 via headless claude CLI, tools disabled, no
            session persistence (maintainer Haiku->Opus directive, issue
            #25; CLI background-haiku helper key tolerated in modelUsage,
            ASM-1873; vendor-family overlap DISCLOSED, never sole gold)
Rubric: the pinned v2.2 composite-hedge template, byte-reused. Calibration:
2 v1 items + 8 v2.2 hedge items per judge, 10/10 to proceed (retry ladder
identical to real items, ontg2v2 design 11.8).

Usage:
  run-stageA.py preflight <pA|pB> <run_dir>            (10 cal items)
  run-stageA.py va        <pA|pB> <run_dir>            (30 V-A items)
  run-stageA.py vb        <pA|pB> <run_dir>            (31 V-B items)
  run-stageA.py assemble  <run_dir>                    (agreement + resolution
                                                        + V-B soundness readout)
  run-stageA.py mock      <run_dir>                    ($0, no LLM calls: full
                                                        pipeline on deterministic
                                                        pseudo-judges)
  run-stageA.py dryplan                                ($0: prints the cost plan)
Flags: --channel proxy|human   (required for preflight/va/vb)
"""
import json
import os
import sys
import hashlib
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
MAT = os.path.join(HERE, "materials")
CODEX_HOME_ISO = "/tmp/ssa-codex-home-iso"

sys.path.insert(0, os.path.join(REPO, "analysis"))
import g3_llmproxy_v3 as G   # pinned blinding-scan + fence-extraction impls

# ---- pins (fail-closed) ----
# materials/manifest.json is pinned here; it pins every other consumed input
# (kernel-v1 corpus + typing, v2.2 template + calibration, g2 schema/sysprompt).
MANIFEST_PIN = "2ec36850d44599f8e9c1b2a33e2e55582516d09621a8c8c622422272d28b5e4f"
G3LP_PIN = "fbaea0c0559962fed724cf1a94e3f7c7dccca68ddfbc364b6f05da4a3712d21e"

JUDGE_CFG = {
    "pA": {"id": "judge-pA-gpt56sol", "kind": "codex", "model": "gpt-5.6-sol"},
    "pB": {"id": "judge-pB-opus48", "kind": "claude",
           "model": "claude-opus-4-8"},
}
HAIKU_MODEL = "claude-haiku-4-5-20251001"   # CLI background helper key only
OPUS_MODEL = "claude-opus-4-8"
OPUS_MU_ALLOWED = frozenset({OPUS_MODEL, HAIKU_MODEL})

EXPECT_CODEX_VER = "codex-cli 0.144.1"
EFFORT = "low"
NPX_CODEX = ["npx", "-y", "@openai/codex@0.144.1"]

BANNED_TYPE_SUBSTR = ["exec_command", "terminal_interaction", "unified_exec",
                      "tool_call", "web_search", "patch_apply", "view_image",
                      "image_generation", "collab_"]
TRANSPORT_TYPE_SUBSTR = ["stream_error", "rate_limit", "rate-limit"]
TRANSPORT_BACKOFF = [30, 60, 120, 300, 300, 300, 300, 300, 300, 300]
MAX_TRANSPORT = 10
MAX_CONTENT = 3
NOLABEL_ABORT = {"va": 3, "vb": 3}   # ~0.90 decisive floor per phase per judge

BUDGET_MAX_CALLS = 200               # incl. content-retry headroom (plan: 142)
PRICE_BOUND_USD_PER_CALL = 0.012     # pinned conservative bound (ASM-1874/1906)
USD_CAP = 10.0                       # design 6.1 Stage-A band
CAL_MIN = 10                         # 10/10 per judge

CAP_PATTERNS = [
    "usage limit", "usage-limit", "rate limit reached", "quota",
    "session limit", "exceeded your", "too many requests",
    "resets at", "reset at", "try again later", "credit balance",
    "insufficient", "you've reached", "you have reached", "limit reached",
    "429", "upgrade to increase", "monthly limit", "weekly limit",
]

CHANNEL = None
MOCK = False


class AbortExperiment(Exception):
    pass


class StopCap(Exception):
    pass


def die(msg):
    sys.stderr.write("RUN_SSA_ABORT: %s\n" % msg)
    sys.exit(2)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def file_sha(path):
    with open(path, "rb") as f:
        return sha_bytes(f.read())


def load_manifest():
    p = os.path.join(MAT, "manifest.json")
    got = file_sha(p)
    if got != MANIFEST_PIN:
        die("ERR_SSA_PIN: materials/manifest.json sha %s != pinned %s"
            % (got, MANIFEST_PIN))
    return json.load(open(p))


def verify_pins(kind):
    man = load_manifest()
    for rel, want in man["input_pins"].items():
        got = file_sha(os.path.join(REPO, rel))
        if got != want:
            die("ERR_SSA_PIN: %s sha %s != pinned %s" % (rel, got, want))
    got = file_sha(os.path.join(REPO, "analysis/g3_llmproxy_v3.py"))
    if got != G3LP_PIN:
        die("ERR_SSA_PIN: analysis/g3_llmproxy_v3.py sha %s != pinned %s"
            % (got, G3LP_PIN))
    if os.path.exists(os.path.expanduser("~/.claude/CLAUDE.md")):
        die("ERR_SSA_PIN: ~/.claude/CLAUDE.md exists (would inject context)")
    banners = {}
    if MOCK or kind == "none":
        return man, banners
    if kind == "codex":
        if not os.path.exists(os.path.expanduser("~/.codex/auth.json")):
            die("ERR_SSA_PIN: ~/.codex/auth.json missing")
        os.makedirs(CODEX_HOME_ISO, mode=0o700, exist_ok=True)
        dst = os.path.join(CODEX_HOME_ISO, "auth.json")
        with open(os.path.expanduser("~/.codex/auth.json"), "rb") as f:
            data = f.read()
        with open(dst, "wb") as f:
            f.write(data)
        os.chmod(dst, 0o600)
        env = dict(os.environ)
        env["CODEX_HOME"] = CODEX_HOME_ISO
        ver = subprocess.run(NPX_CODEX + ["--version"], capture_output=True,
                             text=True, env=env).stdout.strip()
        if ver != EXPECT_CODEX_VER:
            die("ERR_SSA_PIN: npx codex version %r != %r" % (ver, EXPECT_CODEX_VER))
        banners = {"npx_codex": ver}
    elif kind == "claude":
        cv = subprocess.run(["claude", "--version"], capture_output=True,
                            text=True).stdout.strip()
        banners = {"claude": cv}
    return man, banners


def require_go(phase):
    """Launch hold: the build is $0; the run needs the maintainer's explicit
    go AND the section-D channel resolution."""
    if MOCK:
        return
    if os.environ.get("SSA_MAINTAINER_GO") != "1":
        die("HOLD(%s): SSA_MAINTAINER_GO=1 not set. The Stage-A V-A/V-B run "
            "(~$10 worst-case band, expected ~$1.70) awaits the maintainer's "
            "explicit go on the section-A redirect; this driver is "
            "launch-ready but HELD (design section 6.3 / coordinator launch)."
            % phase)
    if CHANNEL != "proxy":
        die("HOLD(%s): --channel proxy required for the judge phases. If the "
            "v2.2 pilot FAILED AC1>=0.65, the pre-committed channel is the "
            "two-human panel (--channel human): hand materials/va-items.jsonl "
            "+ vb-items.jsonl to the panel; this driver's judge phases are "
            "not used (adjudication section D)." % phase)


def read_template():
    return open(os.path.join(
        REPO, "poc/ontology-import-g2-v2/prompt-template-v2.2.txt"),
        encoding="utf-8").read()


def read_sysprompt():
    return open(os.path.join(REPO, "poc/g2/materials/judge-pB-system-prompt.txt"),
                encoding="utf-8").read().rstrip("\n")


def assemble_prompt(item_text, tmpl):
    if "{{ITEM}}" not in tmpl:
        die("ERR_SSA_PIN: template lacks {{ITEM}}")
    return tmpl.replace("{{ITEM}}", item_text)


def load_jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def cal_rows():
    return (load_jsonl(os.path.join(REPO, "poc/g2/materials/calibration-items.jsonl"))
            + load_jsonl(os.path.join(
                REPO, "poc/ontology-import-g2-v2/calibration-hedge-v22.jsonl")))


# --------------- invocation (verbatim ontg2v2 forms) ---------------
def run_codex(model, prompt_text, attempt_dir, workdir):
    os.makedirs(attempt_dir, exist_ok=True)
    up = os.path.join(attempt_dir, "user-prompt.txt")
    with open(up, "w", encoding="utf-8") as f:
        f.write(prompt_text)
    last_msg = os.path.join(attempt_dir, "last-message.json")
    events = os.path.join(attempt_dir, "events.jsonl")
    stderr = os.path.join(attempt_dir, "stderr.log")
    cmd = NPX_CODEX + ["exec", "-m", model,
                       "-c", 'model_reasoning_effort="%s"' % EFFORT,
                       "-s", "read-only", "--ignore-user-config",
                       "--skip-git-repo-check", "--ephemeral",
                       "--disable", "memories",
                       "--disable", "standalone_web_search",
                       "-C", workdir, "--color", "never", "--json",
                       "--output-schema",
                       os.path.join(REPO, "poc/g2/materials/output-schema.json"),
                       "-o", last_msg, "-"]
    env = dict(os.environ)
    env["CODEX_HOME"] = CODEX_HOME_ISO
    with open(up, "rb") as fin, open(events, "wb") as fout, \
            open(stderr, "wb") as ferr:
        p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=ferr, env=env)
    return p.returncode


def run_claude(prompt_text, attempt_dir, workdir, sys_prompt, model):
    os.makedirs(attempt_dir, exist_ok=True)
    up = os.path.join(attempt_dir, "user-prompt.txt")
    with open(up, "w", encoding="utf-8") as f:
        f.write(prompt_text)
    events = os.path.join(attempt_dir, "events.jsonl")
    stderr = os.path.join(attempt_dir, "stderr.log")
    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("ANTHROPIC_AUTH_TOKEN", None)
    env["MAX_THINKING_TOKENS"] = "0"
    env["DISABLE_AUTOUPDATER"] = "1"
    cmd = ["claude", "-p", "--model", model,
           "--system-prompt", sys_prompt, "--tools", "",
           "--setting-sources", "", "--strict-mcp-config",
           "--no-session-persistence",
           "--output-format", "stream-json", "--verbose"]
    with open(up, "rb") as fin, open(events, "wb") as fout, \
            open(stderr, "wb") as ferr:
        p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=ferr,
                           cwd=workdir, env=env)
    return p.returncode


def collect_types(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "type" and isinstance(v, str):
                out.append(v)
            collect_types(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_types(v, out)


def _cap_text(attempt_dir):
    txt = ""
    for fn in ("stderr.log", "events.jsonl"):
        p = os.path.join(attempt_dir, fn)
        if os.path.exists(p):
            try:
                txt += "\n" + open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                pass
    return txt


def _cap_hit(text):
    low = text.lower()
    for pat in CAP_PATTERNS:
        if pat in low:
            return pat
    return None


def label_answer(obj):
    if not (isinstance(obj, dict) and list(obj.keys()) == ["answer"]):
        return None, "parse_failure"
    tok = G.normalize_token(obj["answer"])
    if tok not in G.VALID_TOKENS:
        return None, "parse_failure"
    return tok, None


def validate_codex(exit_code, attempt_dir):
    last_msg = os.path.join(attempt_dir, "last-message.json")
    events = os.path.join(attempt_dir, "events.jsonl")
    types = []
    if os.path.exists(events):
        for line in open(events, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            collect_types(ev, types)
    tool_use = any(any(b in t for b in BANNED_TYPE_SUBSTR) for t in types)
    transport = any(any(b in t for b in TRANSPORT_TYPE_SUBSTR) for t in types)
    raw = None
    if os.path.exists(last_msg):
        try:
            raw = open(last_msg, "rb").read().decode("utf-8")
        except Exception:
            raw = None
    if exit_code != 0:
        if raw is None:
            return ("transport", None, None, "transport")
        return ("content_invalid", None, raw, "parse_failure")
    if transport:
        return ("transport", None, raw, "transport")
    if tool_use:
        return ("content_invalid", None, raw, "tool_use_detected")
    obj = G.extract_answer_object(raw)
    if obj is None:
        return ("content_invalid", None, raw, "parse_failure")
    lab, reason = label_answer(obj)
    if lab is None:
        return ("content_invalid", None, raw, reason)
    return ("valid", {"answer": lab}, raw, None)


def validate_claude(exit_code, attempt_dir, model):
    events = os.path.join(attempt_dir, "events.jsonl")
    init = result = None
    assistant_blocks = []
    if os.path.exists(events):
        for line in open(events, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            t, st = ev.get("type"), ev.get("subtype")
            if t == "system" and st == "init":
                init = ev
            elif t == "result":
                result = ev
            elif t == "assistant":
                for b in (ev.get("message", {}) or {}).get("content", []) or []:
                    assistant_blocks.append(b.get("type"))
    if exit_code != 0:
        return ("transport", None, None, "transport")
    if result is None or result.get("subtype") != "success":
        return ("transport", None, None, "transport")
    mu = result.get("modelUsage") or {}
    # Opus pB: helper-key tolerance as in ontg2v2 --pb-model opus (ASM-1873);
    # the requested opus model MUST appear; fails closed on any other key set.
    mu_ok = (model in mu) and set(mu.keys()) <= OPUS_MU_ALLOWED
    if not (init and init.get("model") == model
            and init.get("apiKeySource") == "none" and mu_ok):
        return ("abort", None, None,
                "identity_mismatch(model=%r apiKeySource=%r modelUsage=%r)"
                % (init.get("model") if init else None,
                   init.get("apiKeySource") if init else None,
                   sorted(mu.keys())))
    tools0 = init.get("tools") == []
    denials0 = (result.get("permission_denials") or []) == []
    turns1 = result.get("num_turns") == 1
    tooluse = "tool_use" in assistant_blocks
    if not (tools0 and denials0 and turns1) or tooluse:
        return ("content_invalid", None, result.get("result"),
                "tool_use_detected")
    raw = result.get("result")
    obj = G.extract_answer_object(raw)
    if obj is None:
        return ("content_invalid", None, raw, "parse_failure")
    lab, reason = label_answer(obj)
    if lab is None:
        return ("content_invalid", None, raw, reason)
    return ("valid", {"answer": lab}, raw, None)


def mock_answer(pkey, item_id, expected=None):
    """Deterministic pseudo-judge for the $0 mock: calibration items answer
    their key; real items answer yes except a scripted pB 'no' on ONE V-B
    item, exercising the disagreement path in assemble. MOCK ONLY -- labels
    never leave the mock run_dir."""
    if expected is not None:
        return expected
    if pkey == "pB" and item_id == "ssA:vb:break.malfunction:ref1":
        return "no"
    return "yes"


def do_attempt(cfg, prompt, attempt_dir, workdir, sys_prompt):
    if cfg["kind"] == "codex":
        rc = run_codex(cfg["model"], prompt, attempt_dir, workdir)
        status, fields, raw, reason = validate_codex(rc, attempt_dir)
    else:
        rc = run_claude(prompt, attempt_dir, workdir, sys_prompt, cfg["model"])
        status, fields, raw, reason = validate_claude(rc, attempt_dir,
                                                      cfg["model"])
    hit = G.blinding_scan([os.path.join(attempt_dir, "user-prompt.txt"),
                           os.path.join(attempt_dir, "events.jsonl"),
                           os.path.join(attempt_dir, "stderr.log")])
    if hit:
        raise AbortExperiment("BLINDING file hit token=%r surface=%s dir=%s"
                              % (hit[1], hit[0], attempt_dir))
    ahit = G.answer_blinding_hit(raw)
    if ahit:
        raise AbortExperiment("BLINDING answer-surface hit token=%r dir=%s"
                              % (ahit, attempt_dir))
    return status, fields, raw, reason


def process_item(cfg, pkey, item_id, prompt, position, base_dir, workdir,
                 sys_prompt, log, expected=None):
    if MOCK:
        return {"answer": mock_answer(pkey, item_id, expected), "flags": ["MOCK"],
                "n_content_attempts": 0, "n_transport_retries": 0,
                "position": position}
    n_content = 0
    n_transport = 0
    last_reason = None
    for content_k in range(1, MAX_CONTENT + 1):
        while True:
            call_dir = os.path.join(base_dir, "c%d_t%d" % (content_k, n_transport))
            status, fields, raw, reason = do_attempt(cfg, prompt, call_dir,
                                                     workdir, sys_prompt)
            if status == "abort":
                die("ERR_SSA_IDENTITY: pos %s %s" % (position, reason))
            if status == "transport":
                cap = _cap_hit(_cap_text(call_dir))
                if cap:
                    raise StopCap("pos %s: cap pattern %r; STOP (no retry). "
                                  "dir=%s" % (position, cap, call_dir))
                n_transport += 1
                if n_transport > MAX_TRANSPORT:
                    die("ERR_SSA_TRANSPORT: pos %s exceeded %d retries"
                        % (position, MAX_TRANSPORT))
                back = TRANSPORT_BACKOFF[min(n_transport - 1,
                                             len(TRANSPORT_BACKOFF) - 1)]
                log("  pos %s transport failure (try %d), backoff %ds"
                    % (position, n_transport, back))
                time.sleep(back)
                continue
            break
        n_content = content_k
        if status == "valid":
            return {"answer": fields["answer"], "flags": [],
                    "n_content_attempts": n_content,
                    "n_transport_retries": n_transport, "position": position}
        last_reason = reason
        log("  pos %s content attempt %d INVALID (%s)"
            % (position, content_k, reason))
    return {"answer": None,
            "flags": ["judge_no_label", last_reason or "parse_failure"],
            "n_content_attempts": n_content,
            "n_transport_retries": n_transport, "position": position}


def make_workdir(tag):
    if MOCK:
        return "/tmp"
    out = subprocess.run(["mktemp", "-d", "/tmp/ssajudge%s-workdir.XXXXXX" % tag],
                         capture_output=True, text=True)
    wd = out.stdout.strip()
    if not wd or not os.path.isdir(wd):
        die("ERR_WORKDIR: mktemp failed")
    chk = subprocess.run(["git", "-C", wd, "rev-parse", "--is-inside-work-tree"],
                         capture_output=True, text=True)
    if chk.stdout.strip() == "true":
        die("ERR_WORKDIR: %s inside a git repo" % wd)
    return wd


def load_checkpoint(jdir, phase):
    cp = os.path.join(jdir, "checkpoint.jsonl")
    done = {}
    if os.path.exists(cp):
        for l in open(cp, encoding="utf-8"):
            l = l.strip()
            if not l:
                continue
            o = json.loads(l)
            if o.get("phase") == phase:
                done[o["id"]] = o["response"]
    return done


def append_checkpoint(jdir, phase, item_id, response):
    with open(os.path.join(jdir, "checkpoint.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"phase": phase, "id": item_id, "response": response},
                           sort_keys=True, ensure_ascii=False) + "\n")


def logger(jdir):
    os.makedirs(jdir, exist_ok=True)
    lf = open(os.path.join(jdir, "run-log.txt"), "a", encoding="utf-8")

    def log(m):
        ts = time.strftime("[%H:%M:%S]", time.gmtime())
        lf.write("%s %s\n" % (ts, m))
        lf.flush()
    return log


def _budget_check(run_dir, adding):
    cpath = os.path.join(run_dir, "call-count.json")
    n = 0
    if os.path.exists(cpath):
        n = json.load(open(cpath))["n"]
    if n + adding > BUDGET_MAX_CALLS:
        die("ERR_SSA_BUDGET: %d + %d > %d call ceiling; STOP, no partial scoring"
            % (n, adding, BUDGET_MAX_CALLS))
    usd_bound = (n + adding) * PRICE_BOUND_USD_PER_CALL
    if usd_bound > USD_CAP:
        die("ERR_SSA_BUDGET: bound-implied $%.2f > $%.2f hard stop"
            % (usd_bound, USD_CAP))
    with open(cpath, "w") as f:
        f.write(json.dumps({"n": n + adding, "usd_bound": usd_bound,
                            "price_bound_usd_per_call":
                                PRICE_BOUND_USD_PER_CALL,
                            "mock": MOCK}) + "\n")


# ---------------------------- phases ----------------------------
def phase_preflight(pkey, run_dir):
    require_go("preflight")
    cfg = JUDGE_CFG[pkey]
    man, banners = verify_pins(cfg["kind"])
    jdir = os.path.join(run_dir, cfg["id"])
    os.makedirs(jdir, exist_ok=True)
    workdir = make_workdir(pkey)
    with open(os.path.join(jdir, "workdir-path.txt"), "w") as f:
        f.write(workdir + "\n")
    log = logger(jdir)
    log("PREFLIGHT %s banners=%s mock=%s" % (cfg["id"], json.dumps(banners), MOCK))
    sys_prompt = read_sysprompt() if cfg["kind"] == "claude" else None
    tmpl = read_template()
    rows = cal_rows()
    if len(rows) != CAL_MIN:
        die("ERR_SSA_CAL: %d calibration rows != %d" % (len(rows), CAL_MIN))
    done = load_checkpoint(jdir, "cal")
    _budget_check(run_dir, len([r for r in rows if r["id"] not in done]))
    results = []
    for i, cal in enumerate(rows, 1):
        if cal["id"] in done:
            r = done[cal["id"]]
        else:
            prompt = assemble_prompt(cal["item"], tmpl)
            base_dir = os.path.join(jdir, "cal", cal["id"].replace(":", "_"))
            pr = process_item(cfg, pkey, cal["id"], prompt, "cal%d" % i,
                              base_dir, workdir, sys_prompt, log,
                              expected=cal["expected"])
            r = {"id": cal["id"], "got": pr["answer"],
                 "expected": cal["expected"],
                 "pass": pr["answer"] == cal["expected"],
                 "n_content_attempts": pr["n_content_attempts"],
                 "n_transport_retries": pr["n_transport_retries"]}
            append_checkpoint(jdir, "cal", cal["id"], r)
        results.append(r)
        log("  CAL %s got=%s expected=%s => %s"
            % (r["id"], r["got"], r["expected"], "PASS" if r["pass"] else "FAIL"))
    ok = all(r["pass"] for r in results)
    with open(os.path.join(jdir, "preflight-status.json"), "w") as f:
        f.write(json.dumps({"phase": "preflight", "judge": cfg["id"],
                            "channel": CHANNEL, "mock": MOCK,
                            "banners": banners, "workdir": workdir,
                            "pass": ok, "results": results},
                           indent=2, sort_keys=True) + "\n")
    print("PREFLIGHT %s %s: %s" % (pkey, cfg["id"], "PASS" if ok else "FAIL"),
          flush=True)
    if not ok:
        die("preflight FAILED for %s (10/10 required)" % pkey)


def _require_preflight(jdir, pkey):
    ps = os.path.join(jdir, "preflight-status.json")
    if not os.path.exists(ps):
        die("no preflight-status.json for %s; run preflight first" % pkey)
    pf = json.load(open(ps))
    if not pf.get("pass"):
        die("preflight %s did not PASS; refusing" % pkey)
    if bool(pf.get("mock")) != MOCK:
        die("ERR_SSA_MODE: preflight mock=%s but this invocation mock=%s"
            % (pf.get("mock"), MOCK))
    workdir = open(os.path.join(jdir, "workdir-path.txt")).read().strip()
    if not os.path.isdir(workdir):
        die("recorded workdir missing: %s" % workdir)
    return workdir


def phase_items(pkey, phase, run_dir):
    require_go(phase)
    cfg = JUDGE_CFG[pkey]
    man, banners = verify_pins(cfg["kind"])
    jdir = os.path.join(run_dir, cfg["id"])
    workdir = _require_preflight(jdir, pkey)
    log = logger(jdir)
    rows = load_jsonl(os.path.join(MAT, "%s-items.jsonl" % phase))
    key = "judge-%s|%s" % (pkey, phase)
    order = man["orders"][key]
    seed = man["seeds"][key]
    recomputed = sorted(order, key=lambda i: sha_bytes(("%s|%s" % (seed, i)).encode()))
    if recomputed != order:
        die("ERR_SSA_ORDER: manifest %s order != recomputed" % key)
    if sorted(order) != sorted(r["id"] for r in rows):
        die("ERR_SSA_ORDER: %s ids != items file" % key)
    by_id = {r["id"]: r for r in rows}
    tmpl = read_template()
    sys_prompt = read_sysprompt() if cfg["kind"] == "claude" else None
    done = load_checkpoint(jdir, phase)
    _budget_check(run_dir, len([i for i in order if i not in done]))
    with open(os.path.join(jdir, "%s-position-map.jsonl" % phase), "w",
              encoding="utf-8") as f:
        for i, iid in enumerate(order, 1):
            f.write(json.dumps({"position": "%s%d" % (phase, i), "id": iid},
                               sort_keys=True) + "\n")
    log("%s %s start n=%d resume_done=%d mock=%s"
        % (phase.upper(), cfg["id"], len(order), len(done), MOCK))
    responses = {}
    n_nolabel = 0
    for i, iid in enumerate(order, 1):
        if iid in done:
            r = done[iid]
        else:
            base_dir = os.path.join(jdir, phase, iid.replace(":", "_"))
            prompt = assemble_prompt(by_id[iid]["item"], tmpl)
            r = process_item(cfg, pkey, iid, prompt, "%s%d" % (phase, i),
                             base_dir, workdir, sys_prompt, log)
            r["id"] = iid
            r["judge"] = cfg["id"]
            append_checkpoint(jdir, phase, iid, r)
        responses[iid] = r
        if r.get("answer") is None:
            n_nolabel += 1
        if n_nolabel > NOLABEL_ABORT[phase]:
            die("ERR_SSA_NOLABEL: %d no-label > %d in %s %s; ABORT"
                % (n_nolabel, NOLABEL_ABORT[phase], cfg["id"], phase))
    fld = ["id", "answer", "flags", "n_content_attempts",
           "n_transport_retries", "position", "judge"]
    rp = os.path.join(run_dir, "judge-%s-%s-responses.jsonl" % (pkey, phase))
    with open(rp, "w", encoding="utf-8") as f:
        for iid in sorted(responses):
            r = responses[iid]
            f.write(json.dumps({k: r.get(k) for k in fld}, sort_keys=True,
                               ensure_ascii=False) + "\n")
    log("%s %s done nolabel=%d -> %s" % (phase.upper(), cfg["id"], n_nolabel, rp))
    print("%s_DONE %s nolabel=%d file=%s" % (phase.upper(), pkey, n_nolabel, rp),
          flush=True)


def _ac1(t):
    n = t["both_yes"] + t["both_no"] + t["a_yes_b_no"] + t["a_no_b_yes"]
    if n == 0:
        return None
    po = (t["both_yes"] + t["both_no"]) / n
    pi = ((2 * t["both_yes"] + t["a_yes_b_no"] + t["a_no_b_yes"]) / (2 * n))
    pe = 2 * pi * (1 - pi)
    if pe == 1.0:
        return None
    return (po - pe) / (1 - pe)


def _wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (round(c - h, 4), round(c + h, 4))


def phase_assemble(run_dir):
    man, _ = verify_pins("none")
    out = {"schema": "ssA-result/1", "mock": MOCK, "channel": CHANNEL,
           "phases": {}}
    resp = {}
    for pkey in ("pA", "pB"):
        for phase in ("va", "vb"):
            p = os.path.join(run_dir, "judge-%s-%s-responses.jsonl" % (pkey, phase))
            if not os.path.exists(p):
                die("assemble: missing %s" % p)
            resp[(pkey, phase)] = {r["id"]: r["answer"] for r in load_jsonl(p)}
    for phase in ("va", "vb"):
        ids = sorted(resp[("pA", phase)])
        t = {"both_yes": 0, "both_no": 0, "a_yes_b_no": 0, "a_no_b_yes": 0}
        per_item = {}
        indecisive = []
        for i in ids:
            a, b = resp[("pA", phase)][i], resp[("pB", phase)][i]
            per_item[i] = {"pA": a, "pB": b}
            if a in ("yes", "no") and b in ("yes", "no"):
                if a == "yes" and b == "yes":
                    t["both_yes"] += 1
                elif a == "no" and b == "no":
                    t["both_no"] += 1
                elif a == "yes":
                    t["a_yes_b_no"] += 1
                else:
                    t["a_no_b_yes"] += 1
            else:
                indecisive.append(i)
        out["phases"][phase] = {"n": len(ids), "table": t,
                                "ac1": _ac1(t), "indecisive": indecisive,
                                "per_item": per_item}
    # V-A resolution readout (pre-stated criterion; NOT a gate)
    rmap = json.load(open(os.path.join(MAT, "resolution-map.json")))
    resolved = {}
    for g2id, spec in rmap["items"].items():
        ok = all(
            resp[("pA", "va")][v] == resp[("pB", "va")][v]
            and resp[("pA", "va")][v] in ("yes", "no")
            for v in spec["va"])
        resolved[g2id] = ok
    out["va_resolution"] = {
        "resolved": resolved,
        "count": "%d/5" % sum(resolved.values()),
        "expectation": ">=4/5 (ASM-1907; readout expectation, not a gate)",
        "friend_latent_pair": {
            v: {"pA": resp[("pA", "va")][v], "pB": resp[("pB", "va")][v]}
            for v in rmap["latent_pair"]["g2:pi:040+g2:pi:041 (friend)"]["va"]},
    }
    # V-B sense-scoped soundness of the binding referent sorts
    vb_ids = sorted(resp[("pA", "vb")])
    sound = [i for i in vb_ids if resp[("pA", "vb")][i] == "yes"
             and resp[("pB", "vb")][i] == "yes"]
    k, n = len(sound), len(vb_ids)
    lo, hi = _wilson(k, n)
    out["vb_soundness"] = {
        "sound_both_yes": k, "n": n, "point": round(k / n, 4),
        "wilson95": [lo, hi],
        "replaces": "0.3929 word-scoped (ASM-1881) -- which stands, "
                    "re-labelled a word-scoped LOWER BOUND; this is the "
                    "sense-scoped quantity of record (design section 5 V-B)",
    }
    cpath = os.path.join(run_dir, "call-count.json")
    out["calls"] = json.load(open(cpath)) if os.path.exists(cpath) else None
    rp = os.path.join(run_dir, "result.json")
    with open(rp, "w") as f:
        f.write(json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({"assembled": rp, "mock": MOCK,
                      "va_ac1": out["phases"]["va"]["ac1"],
                      "vb_ac1": out["phases"]["vb"]["ac1"],
                      "va_resolved": out["va_resolution"]["count"],
                      "vb_soundness": out["vb_soundness"]["point"],
                      "vb_wilson95": out["vb_soundness"]["wilson95"]},
                     sort_keys=True), flush=True)


def phase_dryplan():
    man, _ = verify_pins("none")
    plan = dict(man["cost_plan"])
    plan.update({
        "phases": {"preflight": "10 cal x 2 judges = 20 calls",
                   "va": "30 items x 2 judges = 60 calls",
                   "vb": "31 items x 2 judges = 62 calls"},
        "judges": man["judges"],
        "rubric": man["rubric"],
        "channel_precondition": man["channel_precondition"],
        "hold": "LAUNCH-READY, HELD: needs SSA_MAINTAINER_GO=1 + --channel; "
                "the coordinator launches (this build spent $0)",
        "coordinator_launch": [
            "cd %s" % REPO,
            "R=poc/sense-split-stageA/runs/real-$(date -u +%Y%m%dT%H%M%SZ); mkdir -p $R",
            "SSA_MAINTAINER_GO=1 python3 poc/sense-split-stageA/run-stageA.py preflight pA $R --channel proxy",
            "SSA_MAINTAINER_GO=1 python3 poc/sense-split-stageA/run-stageA.py preflight pB $R --channel proxy",
            "SSA_MAINTAINER_GO=1 python3 poc/sense-split-stageA/run-stageA.py va pA $R --channel proxy",
            "SSA_MAINTAINER_GO=1 python3 poc/sense-split-stageA/run-stageA.py va pB $R --channel proxy",
            "SSA_MAINTAINER_GO=1 python3 poc/sense-split-stageA/run-stageA.py vb pA $R --channel proxy",
            "SSA_MAINTAINER_GO=1 python3 poc/sense-split-stageA/run-stageA.py vb pB $R --channel proxy",
            "python3 poc/sense-split-stageA/run-stageA.py assemble $R --channel proxy",
        ],
    })
    print(json.dumps(plan, indent=1, sort_keys=True))


def phase_mock(run_dir):
    global MOCK, CHANNEL
    MOCK = True
    CHANNEL = CHANNEL or "proxy"
    os.makedirs(run_dir, exist_ok=True)
    for pk in ("pA", "pB"):
        phase_preflight(pk, run_dir)
        phase_items(pk, "va", run_dir)
        phase_items(pk, "vb", run_dir)
    phase_assemble(run_dir)
    print("MOCK_DONE $0 (no LLM calls; labels are pipeline-exercise artifacts "
          "only, never evidence)", flush=True)


def main():
    global CHANNEL
    args = [a for a in sys.argv[1:]]
    if "--channel" in args:
        i = args.index("--channel")
        CHANNEL = args[i + 1]
        del args[i:i + 2]
        if CHANNEL not in ("proxy", "human"):
            die("--channel must be proxy|human")
    if not args:
        die(__doc__.strip().splitlines()[0])
    mode = args[0]
    if mode == "dryplan":
        phase_dryplan()
    elif mode == "mock":
        phase_mock(args[1])
    elif mode == "preflight":
        phase_preflight(args[1], args[2])
    elif mode in ("va", "vb"):
        phase_items(args[1], mode, args[2])
    elif mode == "assemble":
        phase_assemble(args[2] if len(args) > 2 else args[1])
    else:
        die("unknown mode %r" % mode)


if __name__ == "__main__":
    try:
        main()
    except StopCap as e:
        sys.stderr.write("RUN_SSA_CAPSTOP: %s\n" % e)
        sys.exit(3)
    except AbortExperiment as e:
        sys.stderr.write("RUN_SSA_BLINDING_ABORT: %s\n" % e)
        sys.exit(4)
