#!/usr/bin/env python3
"""run-g2lp.py -- MECHANICAL executor of the g2 PROVISIONAL-ON-LLM-PROXY
annotation run (GPT-5.6 human-annotator STAND-IN; maintainer stand-in rule).
Faithful port of the proven poc/g3-llmproxy-v3/run-g3lp-v3.py machinery
(invocation forms, validity/retry/no-label contracts, blinding audit,
checkpointing) adapted to the g2 single-pass subsumption-judgment items in
poc/g2/materials/. DESIGNS NOTHING, CONCLUDES NOTHING.

Judges (mirroring the frozen two-annotator design in the g3-llmproxy-v3
cross-family form; kappa = pair stability, NEVER human-agreement evidence):
  judge-pA  gpt-5.6-sol via npx-pinned @openai/codex@0.144.1, effort low
            (the task-named PRIMARY stand-in)
  judge-pB  claude-haiku-4-5-20251001 via headless `claude -p`
            (cross-check half of the pair; vendor-family overlap with the
            materials' authoring agents DISCLOSED, never sole gold)

"Temperature 0" discharged as in data/d-adj-t-llmproxy/judge-1p-invocation.md
section 4: pinned model+CLI+prompt bytes, stateless per-item calls, lowest
reasoning effort, server-side output schema, FIRST VALID ANSWER IS FINAL.

Usage:
  run-g2lp.py preflight <pA|pB> <run_dir>
  run-g2lp.py real      <pA|pB> <run_dir>
  run-g2lp.py probe     <pA|pB> <run_dir>
  run-g2lp.py assemble  <run_dir>
"""
import json, os, sys, hashlib, subprocess, time

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
G2 = os.path.join(REPO, "poc/g2")
MAT = os.path.join(G2, "materials")
CODEX_HOME_ISO = "/tmp/g2lp-codex-home-iso"

sys.path.insert(0, os.path.join(REPO, "analysis"))
import g3_llmproxy_v3 as G   # pinned blinding-scan + fence-extraction impls

# ---- pinned inputs (fail-closed; ERR_G2P_PIN) ----
PINS = {
    "poc/g2/pi-derived.jsonl":
        "1ca76f1f2f306710b4adeefa4d3d5bb23eb8c5c00549c02063c31aae6c321600",
    "poc/g2/materials/items.jsonl":
        "7a4728840550227703338880a79f61491a3c93e5022f07215631f6caa7077008",
    "poc/g2/materials/probes.jsonl":
        "bc181daf5b77925c882d4c3edea92635ce054ab10c5d76879646953d78158962",
    "poc/g2/materials/calibration-items.jsonl":
        "a2ba97735a437f704f0dcc79af8a5efdc7cc4c549f394da4d973691f9afb9d59",
    "poc/g2/materials/prompt-template.txt":
        "d8724154a740e8c0e7174f9a083f6a8411dfb5fda17c87d6d52acfb4da31dcac",
    "poc/g2/materials/judge-pB-system-prompt.txt":
        "be9198312e4d8e54b7ac8db5a0b9f0a2f50d96327a6cfb56f5c0a1acbee4f297",
    "poc/g2/materials/output-schema.json":
        "c43725989beb58f8e65f952e00dea9c0d2896148d732277bd50402708ed4b13f",
    "poc/g2/materials/manifest.json":
        "81c15ef582b338e53bd0e66bf7a41a3806f04ca11e02cbcba49e1b9eebdbccdc",
    "analysis/g2.py":                     # the FROZEN pinned analysis script
        "04deddcf9f1496df2da72e7965a9b2ceca69a1d87e8086f209d9045231a6f5ce",
    "analysis/g3_llmproxy_v3.py":         # imported reference impls
        "fbaea0c0559962fed724cf1a94e3f7c7dccca68ddfbc364b6f05da4a3712d21e",
}
PATHS = {k: os.path.join(REPO, k) for k in PINS}

JUDGE_CFG = {
    "pA": {"id": "judge-pA-gpt56sol", "kind": "codex", "model": "gpt-5.6-sol"},
    "pB": {"id": "judge-pB-haiku45", "kind": "claude",
           "model": "claude-haiku-4-5-20251001"},
}
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
N_ITEMS = 84
N_PROBES = 20
NOLABEL_ABORT_REAL = 5     # ~5% of 84 (the g3lp 10/200 rate, rounded up)
NOLABEL_ABORT_PROBE = 3

CAP_PATTERNS = [
    "usage limit", "usage-limit", "rate limit reached", "quota",
    "session limit", "exceeded your", "too many requests",
    "resets at", "reset at", "try again later", "credit balance",
    "insufficient", "you've reached", "you have reached", "limit reached",
    "429", "upgrade to increase", "monthly limit", "weekly limit",
]


class AbortExperiment(Exception):
    pass


class StopCap(Exception):
    pass


def die(msg):
    sys.stderr.write("RUN_G2LP_ABORT: %s\n" % msg)
    sys.exit(2)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def file_sha(path):
    with open(path, "rb") as f:
        return sha_bytes(f.read())


def claude_version_tuple(s):
    tok = s.strip().split()[0]
    try:
        return tuple(int(x) for x in tok.split("."))
    except Exception:
        return None


def ensure_codex_home():
    if os.path.isdir(CODEX_HOME_ISO):
        return
    auth = os.path.expanduser("~/.codex/auth.json")
    if not os.path.exists(auth):
        die("ERR_G2P_PIN: ~/.codex/auth.json missing")
    os.makedirs(CODEX_HOME_ISO, mode=0o700, exist_ok=True)
    with open(auth, "rb") as f:
        data = f.read()
    dst = os.path.join(CODEX_HOME_ISO, "auth.json")
    with open(dst, "wb") as f:
        f.write(data)
    os.chmod(dst, 0o600)
    cfg = os.path.expanduser("~/.codex/config.toml")
    if os.path.exists(cfg):
        with open(cfg, "rb") as fi, open(os.path.join(CODEX_HOME_ISO, "config.toml"), "wb") as fo:
            fo.write(fi.read())


def verify_pins(kind):
    for rel, want in PINS.items():
        got = file_sha(PATHS[rel])
        if got != want:
            die("ERR_G2P_PIN: %s sha %s != pinned %s" % (rel, got, want))
    if os.path.exists(os.path.expanduser("~/.claude/CLAUDE.md")):
        die("ERR_G2P_PIN: ~/.claude/CLAUDE.md exists (would inject context)")
    banners = {}
    if kind == "codex":
        ensure_codex_home()
        env = dict(os.environ)
        env["CODEX_HOME"] = CODEX_HOME_ISO
        ver = subprocess.run(NPX_CODEX + ["--version"], capture_output=True,
                             text=True, env=env).stdout.strip()
        if ver != EXPECT_CODEX_VER:
            die("ERR_G2P_PIN: npx codex version %r != %r" % (ver, EXPECT_CODEX_VER))
        banners = {"npx_codex": ver}
        gv = subprocess.run(["codex", "--version"], capture_output=True,
                            text=True).stdout.strip()
        banners["global_codex_untouched"] = gv
    else:
        cv = subprocess.run(["claude", "--version"], capture_output=True,
                            text=True).stdout.strip()
        vt = claude_version_tuple(cv)
        if vt is None or vt < (2, 1, 201):
            die("ERR_G2P_PIN: claude version %r < 2.1.201" % cv)
        banners = {"claude": cv}
    return banners


def load_jsonl(rel):
    return [json.loads(l) for l in open(PATHS[rel], encoding="utf-8") if l.strip()]


def read_template():
    return open(PATHS["poc/g2/materials/prompt-template.txt"], encoding="utf-8").read()


def read_sysprompt():
    return open(PATHS["poc/g2/materials/judge-pB-system-prompt.txt"],
                encoding="utf-8").read().rstrip("\n")


def assemble_prompt(item_text, tmpl):
    if "{{ITEM}}" not in tmpl:
        die("ERR_G2P_PIN: template lacks {{ITEM}}")
    return tmpl.replace("{{ITEM}}", item_text)


# ---------------------------- invocation (g3lp-v3 forms) --------------------
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
                       "--output-schema", PATHS["poc/g2/materials/output-schema.json"],
                       "-o", last_msg, "-"]
    env = dict(os.environ)
    env["CODEX_HOME"] = CODEX_HOME_ISO
    with open(up, "rb") as fin, open(events, "wb") as fout, open(stderr, "wb") as ferr:
        p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=ferr, env=env)
    return p.returncode


def run_claude(prompt_text, attempt_dir, workdir, sys_prompt):
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
    cmd = ["claude", "-p", "--model", "claude-haiku-4-5-20251001",
           "--system-prompt", sys_prompt, "--tools", "",
           "--setting-sources", "", "--no-session-persistence",
           "--output-format", "stream-json", "--verbose"]
    with open(up, "rb") as fin, open(events, "wb") as fout, open(stderr, "wb") as ferr:
        p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=ferr, cwd=workdir, env=env)
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


def validate_claude(exit_code, attempt_dir):
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
    if not (init and init.get("model") == "claude-haiku-4-5-20251001"
            and init.get("apiKeySource") == "none"
            and set(mu.keys()) == {"claude-haiku-4-5-20251001"}):
        return ("abort", None, None,
                "identity_mismatch(model=%r apiKeySource=%r modelUsage=%r)"
                % (init.get("model") if init else None,
                   init.get("apiKeySource") if init else None, sorted(mu.keys())))
    tools0 = init.get("tools") == []
    denials0 = (result.get("permission_denials") or []) == []
    turns1 = result.get("num_turns") == 1
    tooluse = "tool_use" in assistant_blocks
    if not (tools0 and denials0 and turns1) or tooluse:
        return ("content_invalid", None, result.get("result"), "tool_use_detected")
    raw = result.get("result")
    obj = G.extract_answer_object(raw)
    if obj is None:
        return ("content_invalid", None, raw, "parse_failure")
    lab, reason = label_answer(obj)
    if lab is None:
        return ("content_invalid", None, raw, reason)
    return ("valid", {"answer": lab}, raw, None)


def do_attempt(cfg, prompt, attempt_dir, workdir, sys_prompt):
    if cfg["kind"] == "codex":
        rc = run_codex(cfg["model"], prompt, attempt_dir, workdir)
        status, fields, raw, reason = validate_codex(rc, attempt_dir)
    else:
        rc = run_claude(prompt, attempt_dir, workdir, sys_prompt)
        status, fields, raw, reason = validate_claude(rc, attempt_dir)
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


def process_item(cfg, prompt, position, base_dir, workdir, sys_prompt, log):
    n_content = 0
    n_transport = 0
    last_reason = None
    for content_k in range(1, MAX_CONTENT + 1):
        while True:
            call_dir = os.path.join(base_dir, "c%d_t%d" % (content_k, n_transport))
            status, fields, raw, reason = do_attempt(cfg, prompt, call_dir,
                                                     workdir, sys_prompt)
            if status == "abort":
                die("ERR_G2P_IDENTITY: pos %s %s" % (position, reason))
            if status == "transport":
                cap = _cap_hit(_cap_text(call_dir))
                if cap:
                    raise StopCap("pos %s: cap pattern %r; STOP (no retry). "
                                  "dir=%s" % (position, cap, call_dir))
                n_transport += 1
                if n_transport > MAX_TRANSPORT:
                    die("ERR_G2P_TRANSPORT: pos %s exceeded %d retries"
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
    out = subprocess.run(["mktemp", "-d", "/tmp/g2judge%s-workdir.XXXXXX" % tag],
                         capture_output=True, text=True)
    wd = out.stdout.strip()
    if not wd or not os.path.isdir(wd):
        die("ERR_WORKDIR: mktemp failed")
    if os.listdir(wd):
        die("ERR_WORKDIR: workdir not empty: %s" % wd)
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
    lf = open(os.path.join(jdir, "run-log.txt"), "a", encoding="utf-8")

    def log(m):
        ts = time.strftime("[%H:%M:%S]", time.gmtime())
        lf.write("%s %s\n" % (ts, m))
        lf.flush()
    return log


# ---------------------------- phases ----------------------------
def phase_preflight(pkey, run_dir):
    cfg = JUDGE_CFG[pkey]
    st = subprocess.run([sys.executable, PATHS["analysis/g3_llmproxy_v3.py"],
                         "--selftest"], capture_output=True, text=True)
    if st.returncode != 0 or "selftest OK" not in st.stdout:
        die("ERR_G2P_SELFTEST(g3lp helpers): %s%s" % (st.stdout, st.stderr))
    st2 = subprocess.run([sys.executable, PATHS["analysis/g2.py"],
                          "--selftest"], capture_output=True, text=True)
    if st2.returncode != 0 or "g2 selftest OK" not in st2.stdout:
        die("ERR_G2P_SELFTEST(g2 pinned analysis): %s%s" % (st2.stdout, st2.stderr))
    banners = verify_pins(cfg["kind"])
    jdir = os.path.join(run_dir, cfg["id"])
    os.makedirs(jdir, exist_ok=True)
    workdir = make_workdir(pkey)
    with open(os.path.join(jdir, "workdir-path.txt"), "w") as f:
        f.write(workdir + "\n")
    log = logger(jdir)
    log("PREFLIGHT %s selftests=OK banners=%s workdir=%s"
        % (cfg["id"], json.dumps(banners), workdir))
    tmpl = read_template()
    sys_prompt = read_sysprompt() if cfg["kind"] == "claude" else None
    results, ok = [], True
    for cal in load_jsonl("poc/g2/materials/calibration-items.jsonl"):
        prompt = assemble_prompt(cal["item"], tmpl)
        call_dir = os.path.join(jdir, "preflight", cal["id"].replace(":", "_"))
        status, fields, raw, reason = do_attempt(cfg, prompt, call_dir,
                                                 workdir, sys_prompt)
        if status == "abort":
            die("ERR_G2P_IDENTITY preflight %s: %s" % (cal["id"], reason))
        got = fields["answer"] if status == "valid" else None
        item_ok = (status == "valid") and (got == cal["expected"])
        results.append({"id": cal["id"], "status": status, "got": got,
                        "expected": cal["expected"], "reason": reason,
                        "pass": item_ok})
        log("  PREFLIGHT %s status=%s got=%s expected=%s => %s"
            % (cal["id"], status, got, cal["expected"],
               "PASS" if item_ok else "FAIL"))
        if not item_ok:
            ok = False
    status_obj = {"phase": "preflight", "judge": cfg["id"], "banners": banners,
                  "workdir": workdir, "pass": ok, "results": results}
    with open(os.path.join(jdir, "preflight-status.json"), "w") as f:
        f.write(json.dumps(status_obj, indent=2, sort_keys=True) + "\n")
    print("PREFLIGHT %s %s: %s" % (pkey, cfg["id"], "PASS" if ok else "FAIL"),
          flush=True)
    if not ok:
        die("preflight FAILED for %s" % pkey)


def _require_preflight(jdir, pkey):
    ps = os.path.join(jdir, "preflight-status.json")
    if not os.path.exists(ps):
        die("no preflight-status.json for %s; run preflight first" % pkey)
    if not json.load(open(ps)).get("pass"):
        die("preflight %s did not PASS; refusing" % pkey)
    workdir = open(os.path.join(jdir, "workdir-path.txt")).read().strip()
    if not os.path.isdir(workdir):
        die("recorded workdir missing: %s" % workdir)
    return workdir


def _run_block(pkey, run_dir, phase, rows, order_key, n_expected, nolabel_cap,
               pos_prefix):
    cfg = JUDGE_CFG[pkey]
    banners = verify_pins(cfg["kind"])
    jdir = os.path.join(run_dir, cfg["id"])
    workdir = _require_preflight(jdir, pkey)
    log = logger(jdir)
    manifest = json.load(open(PATHS["poc/g2/materials/manifest.json"]))
    order = manifest[order_key]["judge-%s" % pkey]
    seed = manifest["seed_real_orders" if order_key == "real_orders"
                    else "seed_probe_orders"]["judge-%s" % pkey]
    recomputed = sorted(order, key=lambda i: sha_bytes(("%s|%s" % (seed, i)).encode()))
    if recomputed != order:
        die("ERR_G2P_ORDER: manifest %s order != recomputed" % order_key)
    if len(order) != n_expected:
        die("ERR_G2P_ORDER: %s has %d items != %d"
            % (order_key, len(order), n_expected))
    by_id = {r["id"]: r for r in rows}
    tmpl = read_template()
    sys_prompt = read_sysprompt() if cfg["kind"] == "claude" else None
    done = load_checkpoint(jdir, phase)
    with open(os.path.join(jdir, "%s-position-map.jsonl" % phase), "w",
              encoding="utf-8") as f:
        for i, iid in enumerate(order, 1):
            f.write(json.dumps({"position": "%s%d" % (pos_prefix, i),
                                "id": iid}, sort_keys=True) + "\n")
    log("%s %s start n=%d resume_done=%d banners=%s"
        % (phase.upper(), cfg["id"], len(order), len(done), json.dumps(banners)))
    responses = {}
    n_nolabel = 0
    t0 = time.time()
    for i, iid in enumerate(order, 1):
        if iid in done:
            r = done[iid]
        else:
            base_dir = os.path.join(jdir, phase, iid.replace(":", "_"))
            prompt = assemble_prompt(by_id[iid]["item"], tmpl)
            r = process_item(cfg, prompt, "%s%d" % (pos_prefix, i), base_dir,
                             workdir, sys_prompt, log)
            r["id"] = iid
            r["judge"] = cfg["id"]
            append_checkpoint(jdir, phase, iid, r)
        responses[iid] = r
        if r.get("answer") is None:
            n_nolabel += 1
        if i % 10 == 0 or i == len(order):
            log("  %s %d/%d nolabel=%d elapsed=%.0fs"
                % (phase, i, len(order), n_nolabel, time.time() - t0))
        if n_nolabel > nolabel_cap:
            die("ERR_G2P_NOLABEL: %d no-label > %d in %s %s; ABORT"
                % (n_nolabel, nolabel_cap, cfg["id"], phase))
    banners_after = verify_pins(cfg["kind"])
    if banners_after != banners:
        die("ERR_G2P_PIN: banner drift")
    fld = ["id", "answer", "flags", "n_content_attempts",
           "n_transport_retries", "position", "judge"]
    rp = os.path.join(G2, "judge-%s-%s-responses.jsonl" % (pkey, phase))
    with open(rp, "w", encoding="utf-8") as f:
        for iid in sorted(responses):
            r = responses[iid]
            f.write(json.dumps({k: r.get(k) for k in fld}, sort_keys=True,
                               ensure_ascii=False) + "\n")
    log("%s %s done nolabel=%d -> %s" % (phase.upper(), cfg["id"], n_nolabel, rp))
    print("%s_DONE %s nolabel=%d file=%s" % (phase.upper(), pkey, n_nolabel, rp),
          flush=True)


def phase_real(pkey, run_dir):
    _run_block(pkey, run_dir, "real",
               load_jsonl("poc/g2/materials/items.jsonl"),
               "real_orders", N_ITEMS, NOLABEL_ABORT_REAL, "")


def phase_probe(pkey, run_dir):
    _run_block(pkey, run_dir, "probe",
               load_jsonl("poc/g2/materials/probes.jsonl"),
               "probe_orders", N_PROBES, NOLABEL_ABORT_PROBE, "p")


def wilson2(p, n):
    z = 1.96
    if n <= 0:
        return 0.0, 1.0
    z2 = z * z
    centre = p + z2 / (2 * n)
    spread = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return (centre - spread) / (1 + z2 / n), (centre + spread) / (1 + z2 / n)


def phase_assemble(run_dir):
    """Pure counting + the FROZEN pinned analysis (analysis/g2.py) run once
    per pre-declared gold construction. Designs/concludes nothing."""
    for rel, want in PINS.items():
        if file_sha(PATHS[rel]) != want:
            die("ERR_G2P_PIN: %s drifted" % rel)
    det = json.load(open(os.path.join(G2, "deterministic-checks.json")))

    def load_resp(pk, phase):
        p = os.path.join(G2, "judge-%s-%s-responses.jsonl" % (pk, phase))
        if not os.path.exists(p):
            die("missing %s" % p)
        return {r["id"]: r for r in
                (json.loads(l) for l in open(p, encoding="utf-8") if l.strip())}

    ra, rb = load_resp("pA", "real"), load_resp("pB", "real")
    pa, pb = load_resp("pA", "probe"), load_resp("pB", "probe")
    items = load_jsonl("poc/g2/materials/items.jsonl")
    ids = sorted(i["id"] for i in items)
    if sorted(ra) != ids or sorted(rb) != ids:
        die("ERR_G2P_IDS: response ids != item ids")
    DEC = ("yes", "no")
    labels = []
    t = {"both_yes": 0, "both_no": 0, "a_yes_b_no": 0, "a_no_b_yes": 0}
    nA_dec = nA_yes = nB_dec = nB_yes = 0
    for iid in ids:
        a, b = ra[iid].get("answer"), rb[iid].get("answer")
        da, db = a in DEC, b in DEC
        if da:
            nA_dec += 1
            nA_yes += int(a == "yes")
        if db:
            nB_dec += 1
            nB_yes += int(b == "yes")
        if da and db:
            if a == "yes" and b == "yes":
                t["both_yes"] += 1
            elif a == "no" and b == "no":
                t["both_no"] += 1
            elif a == "yes":
                t["a_yes_b_no"] += 1
            else:
                t["a_no_b_yes"] += 1
        it = next(x for x in items if x["id"] == iid)
        labels.append({"id": iid, "rule": it["rule"], "form": it["form"],
                       "subject": it["subject"], "answer_pA": a, "answer_pB": b,
                       "dual_decisive": da and db,
                       "flags": sorted(set(ra[iid].get("flags", [])
                                           + rb[iid].get("flags", [])))})
    n_dual = sum(t.values())
    probe_stats = {}
    for pk, resp in (("pA", pa), ("pB", pb)):
        lab = sum(1 for r in resp.values() if r.get("answer") is not None)
        fs = sum(1 for r in resp.values() if r.get("answer") == "yes")
        probe_stats[pk] = {"n_labelled": lab, "n_false_sat": fs,
                           "false_sat_rate": (fs / lab) if lab else None,
                           "instrument_ok": (lab > 0 and fs / lab < 0.30)}

    base = {"annot_both_yes": t["both_yes"], "annot_both_no": t["both_no"],
            "annot_a_yes_b_no": t["a_yes_b_no"],
            "annot_a_no_b_yes": t["a_no_b_yes"],
            "litmus_promise_recovered": det["litmus_promise_recovered"],
            "partition_axioms_recovered": det["partition_axioms_recovered"],
            "sidecar_conflicts": det["sidecar_conflicts"]}
    constructions = {
        "primary_gpt56_standin": dict(base, n_gold=nA_dec,
                                      n_derived_correct=nA_yes),
        "pair_concordant": dict(base, n_gold=n_dual,
                                n_derived_correct=t["both_yes"]),
        "pair_union": dict(base, n_gold=n_dual,
                           n_derived_correct=t["both_yes"] + t["a_yes_b_no"]
                           + t["a_no_b_yes"]),
    }
    analyses = {}
    with open(os.path.join(G2, "analysis-input.jsonl"), "w") as f:
        for name, m in sorted(constructions.items()):
            rec = {"construction": name, "metrics": m}
            f.write(json.dumps(rec, sort_keys=True) + "\n")
            p = subprocess.run([sys.executable, PATHS["analysis/g2.py"]],
                               input=json.dumps({"metrics": m}) + "\n",
                               capture_output=True, text=True)
            if p.returncode != 0:
                die("ERR_G2P_ANALYSIS: %s: %s" % (name, p.stderr))
            analyses[name] = json.loads(p.stdout)
            pt = m["n_derived_correct"] / m["n_gold"] if m["n_gold"] else None
            if pt is not None:
                lo, hi = wilson2(pt, m["n_gold"])
                analyses[name]["_estimation_two_sided_wilson95"] = [lo, hi]
    lp = os.path.join(G2, "labels-proxy.jsonl")
    with open(lp, "w", encoding="utf-8") as f:
        for r in labels:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
    result = {
        "schema": "g2lp-result/1",
        "status": "PROVISIONAL-ON-LLM-PROXY",
        "frozen_experiment": "g2",
        "frozen_sha256": "f66337ef70e4d6b90fc5d83f32d1e368e2f7a4c2528d4f143e0539287ea36061",
        "n_items": len(ids), "n_dual_decisive": n_dual,
        "judge_pA_decisive": nA_dec, "judge_pB_decisive": nB_dec,
        "judge_pA_yes": nA_yes, "judge_pB_yes": nB_yes,
        "agreement_table": t,
        "probe_stats": probe_stats,
        "deterministic_checks": {k: det[k] for k in
                                 ("litmus_promise_recovered",
                                  "partition_axioms_recovered",
                                  "sidecar_conflicts")},
        "constructions": constructions,
        "pinned_analysis_outputs": analyses,
        "labels_sha256": file_sha(lp),
        "disclosure": (
            "STAND-IN, NOT THE FROZEN g2.gold: a cross-family blind LLM pair "
            "(judge-pA GPT-5.6-Sol = the task-named primary stand-in; "
            "judge-pB Claude Haiku 4.5, vendor-family overlap with the "
            "materials' authoring agents DISCLOSED, never sole gold) fills "
            "the two-human n=500 GATE-H role over the FULL Pi dump (n=84 -- "
            "the frozen n_planned=500 is unattainable from kernel-v0; the "
            "frozen instrument gate n_gold>=500 therefore CANNOT pass on the "
            "pinned corpus, human or LLM). kappa is pair stability, never "
            "human-agreement evidence. The human g2.gold path stays open and "
            "solely adjudicating; reconcile + re-run when it arrives."),
    }
    with open(os.path.join(G2, "result.json"), "w") as f:
        f.write(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"n_items": len(ids), "n_dual_decisive": n_dual,
                      "table": t,
                      "kappa": analyses["pair_concordant"]["analysis"]["kappa"],
                      "precision_primary": analyses["primary_gpt56_standin"]
                      ["analysis"].get("precision"),
                      "probe": {k: v["false_sat_rate"]
                                for k, v in probe_stats.items()}},
                     sort_keys=True))
    print("ASSEMBLE_DONE -> poc/g2/result.json")


if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            die("usage: preflight|real|probe <pA|pB> <run_dir> | assemble <run_dir>")
        mode = sys.argv[1]
        if mode == "preflight":
            phase_preflight(sys.argv[2], sys.argv[3])
        elif mode == "real":
            phase_real(sys.argv[2], sys.argv[3])
        elif mode == "probe":
            phase_probe(sys.argv[2], sys.argv[3])
        elif mode == "assemble":
            phase_assemble(sys.argv[2])
        else:
            die("unknown mode %r" % mode)
    except StopCap as e:
        sys.stderr.write("RUN_G2LP_STOPCAP: %s\n" % e)
        sys.exit(3)
    except AbortExperiment as e:
        sys.stderr.write("RUN_G2LP_BLINDING_ABORT: %s\n" % e)
        sys.exit(4)
