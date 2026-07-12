#!/usr/bin/env python3
"""run-ontg2.py -- MECHANICAL executor of the ONT-TYPE-G2/1 proxy
annotation rerun (registry g2-import). Faithful port of the proven
poc/g2/run-g2lp.py machinery (itself ported from g3-llmproxy-v3):
identical invocation forms, validity/retry/no-label contracts, blinding
audit, checkpointing -- parameterized by ARM (a1 | a2 | a3). DESIGNS
NOTHING, CONCLUDES NOTHING.

Protocol (maintainer directive #11, reused per plan section 7.4):
  judge-pA  gpt-5.6-sol via npx-pinned openai codex CLI 0.144.1,
            reasoning effort low, read-only, ephemeral, server-side
            output schema (PRIMARY construction)
  judge-pB  claude-haiku-4-5-20251001 via headless claude CLI, tools
            disabled, no session persistence (SENSITIVITY judge;
            vendor-family overlap with the materials' authoring agents
            DISCLOSED, never sole gold)
Stateless per-item calls; the SAME frozen g2 rubric
(poc/g2/materials/prompt-template.txt); FRESH per-judge-per-arm order
seeds (materials/manifest.json); {yes,no,cannot-say}; first valid
answer final; full blinding scans. Judges never see arm identity,
sources, derivation rules, vacuity flags, or the A0 baseline.

A0 is NOT re-adjudicated: the frozen g2 primary labels
(poc/g2/labels-proxy.jsonl, 33/84) are the baseline by plan section 7.2.

Scoring at assemble (plan section 7.3): score = 1 iff the judge label
is "yes" AND the slot is non-vacuous in that arm
(data/onto-softtype/soft-type-candidates.jsonl vacuous_by_arm);
missing / cannot-say / no-label / vacuous => 0. Fixed denominator 84.

Usage:
  run-ontg2.py preflight <pA|pB> <run_dir>
  run-ontg2.py real      <pA|pB> <a1|a2|a3> <run_dir>
  run-ontg2.py probe     <pA|pB> <a1|a2|a3> <run_dir>
  run-ontg2.py assemble  <run_dir>
  run-ontg2.py mock      <run_dir> <go|nogo|instrument>   (no LLM calls)
"""
import json
import os
import sys
import hashlib
import subprocess
import time

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
BASE = os.path.join(REPO, "poc/ontology-import-g2")
MAT = os.path.join(BASE, "materials")
G2MAT = os.path.join(REPO, "poc/g2/materials")
CODEX_HOME_ISO = "/tmp/ontg2-codex-home-iso"

sys.path.insert(0, os.path.join(REPO, "analysis"))
import g3_llmproxy_v3 as G   # pinned blinding-scan + fence-extraction impls

# ---- pinned inputs (fail-closed; ERR_ONTG2_PIN) ----
PINS = {
    "poc/ontology-import-g2/materials/arm-a1-bfo.jsonl":
        "e91c4cef43b9c685ab4223dbfda30c3577fdfc870017f9530da9ee20175aec4a",
    "poc/ontology-import-g2/materials/arm-a2-bfo-sumo.jsonl":
        "13ce9e116a44dca072a4e9b8f4103d4025c1fdc1527a67e321195b55a9c92bd7",
    "poc/ontology-import-g2/materials/arm-a3-bfo-sumo-framenet.jsonl":
        "4600941ae080991071e6ff4de2a97cd450b3ad4bc8ed8c63686729f78855d3e3",
    "poc/ontology-import-g2/materials/arm-a0-baseline.jsonl":
        "493c4b440d27ca10d5f17e5c2d102471cef6a1799447c2a848bf398bd3ef5300",
    "poc/ontology-import-g2/materials/probes-a1.jsonl":
        "c19576730437b1bdc3a4f95dd63892910aecf242d04fe4b3707277835af3aaa7",
    "poc/ontology-import-g2/materials/probes-a2.jsonl":
        "516efb1df208e57d3b32d1d5fb435d4e88c4aa3933a29b9038f39999154b540c",
    "poc/ontology-import-g2/materials/probes-a3.jsonl":
        "76c8d389d4980f99d088edb36e9b246b91cee3daf4f3df09de046ada9774a175",
    "poc/ontology-import-g2/materials/manifest.json":
        "e9b586ae8e09134da218620382579d2d3e04a4c0addb5e64581ddde2df142125",
    "poc/ontology-import-g2/materials/generation-report.json":
        "b8874a2408ea4a241f9adb04201c4233ed5a90aa7c9f578c2dbbf0b679f4d21b",
    "data/onto-softtype/soft-type-candidates.jsonl":
        "3a377cfc73b7e8a45c3a08ac98eed0a75d3f2b113928adfc00d5efad95c9fadb",
    "poc/g2/materials/items.jsonl":
        "7a4728840550227703338880a79f61491a3c93e5022f07215631f6caa7077008",
    "poc/g2/materials/prompt-template.txt":
        "d8724154a740e8c0e7174f9a083f6a8411dfb5fda17c87d6d52acfb4da31dcac",
    "poc/g2/materials/judge-pB-system-prompt.txt":
        "be9198312e4d8e54b7ac8db5a0b9f0a2f50d96327a6cfb56f5c0a1acbee4f297",
    "poc/g2/materials/output-schema.json":
        "c43725989beb58f8e65f952e00dea9c0d2896148d732277bd50402708ed4b13f",
    "poc/g2/materials/calibration-items.jsonl":
        "a2ba97735a437f704f0dcc79af8a5efdc7cc4c549f394da4d973691f9afb9d59",
    "poc/g2/labels-proxy.jsonl":
        "93a124478b8dba411bfd1a9fd07cbc96e874def8e6ac819202c54c1b121754b3",
    "analysis/ontg2.py":
        "5cca4b5cb12807d6099c0a73aed7dcec2e3b2a180b835440e238e69e1054545c",
    "analysis/g3_llmproxy_v3.py":
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
ARMS = ("a1", "a2", "a3")
ARM_FILE = {"a1": "arm-a1-bfo.jsonl", "a2": "arm-a2-bfo-sumo.jsonl",
            "a3": "arm-a3-bfo-sumo-framenet.jsonl"}

BANNED_TYPE_SUBSTR = ["exec_command", "terminal_interaction", "unified_exec",
                      "tool_call", "web_search", "patch_apply", "view_image",
                      "image_generation", "collab_"]
TRANSPORT_TYPE_SUBSTR = ["stream_error", "rate_limit", "rate-limit"]
TRANSPORT_BACKOFF = [30, 60, 120, 300, 300, 300, 300, 300, 300, 300]
MAX_TRANSPORT = 10
MAX_CONTENT = 3
N_ITEMS = 84
N_PROBES = 20
NOLABEL_ABORT_REAL = 5
NOLABEL_ABORT_PROBE = 3
BUDGET_MAX_CALLS = 628      # plan section 8; hard call ceiling

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
    sys.stderr.write("RUN_ONTG2_ABORT: %s\n" % msg)
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
        die("ERR_ONTG2_PIN: ~/.codex/auth.json missing")
    os.makedirs(CODEX_HOME_ISO, mode=0o700, exist_ok=True)
    with open(auth, "rb") as f:
        data = f.read()
    dst = os.path.join(CODEX_HOME_ISO, "auth.json")
    with open(dst, "wb") as f:
        f.write(data)
    os.chmod(dst, 0o600)
    cfg = os.path.expanduser("~/.codex/config.toml")
    if os.path.exists(cfg):
        with open(cfg, "rb") as fi, \
                open(os.path.join(CODEX_HOME_ISO, "config.toml"), "wb") as fo:
            fo.write(fi.read())


def verify_pins(kind):
    for rel, want in PINS.items():
        got = file_sha(PATHS[rel])
        if got != want:
            die("ERR_ONTG2_PIN: %s sha %s != pinned %s" % (rel, got, want))
    if os.path.exists(os.path.expanduser("~/.claude/CLAUDE.md")):
        die("ERR_ONTG2_PIN: ~/.claude/CLAUDE.md exists (would inject context)")
    banners = {}
    if kind == "codex":
        ensure_codex_home()
        env = dict(os.environ)
        env["CODEX_HOME"] = CODEX_HOME_ISO
        ver = subprocess.run(NPX_CODEX + ["--version"], capture_output=True,
                             text=True, env=env).stdout.strip()
        if ver != EXPECT_CODEX_VER:
            die("ERR_ONTG2_PIN: npx codex version %r != %r"
                % (ver, EXPECT_CODEX_VER))
        banners = {"npx_codex": ver}
        gv = subprocess.run(["codex", "--version"], capture_output=True,
                            text=True).stdout.strip()
        banners["global_codex_untouched"] = gv
    elif kind == "claude":
        cv = subprocess.run(["claude", "--version"], capture_output=True,
                            text=True).stdout.strip()
        vt = claude_version_tuple(cv)
        if vt is None or vt < (2, 1, 201):
            die("ERR_ONTG2_PIN: claude version %r < 2.1.201" % cv)
        banners = {"claude": cv}
    return banners     # kind == "none": pins only (assemble / mock)


def load_jsonl(rel):
    return [json.loads(l) for l in open(PATHS[rel], encoding="utf-8")
            if l.strip()]


def load_jsonl_abs(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def read_template():
    return open(PATHS["poc/g2/materials/prompt-template.txt"],
                encoding="utf-8").read()


def read_sysprompt():
    return open(PATHS["poc/g2/materials/judge-pB-system-prompt.txt"],
                encoding="utf-8").read().rstrip("\n")


def assemble_prompt(item_text, tmpl):
    if "{{ITEM}}" not in tmpl:
        die("ERR_ONTG2_PIN: template lacks {{ITEM}}")
    return tmpl.replace("{{ITEM}}", item_text)


# --------------- invocation (verbatim g2lp forms) ---------------
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
                       PATHS["poc/g2/materials/output-schema.json"],
                       "-o", last_msg, "-"]
    env = dict(os.environ)
    env["CODEX_HOME"] = CODEX_HOME_ISO
    with open(up, "rb") as fin, open(events, "wb") as fout, \
            open(stderr, "wb") as ferr:
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
                txt += "\n" + open(p, encoding="utf-8",
                                   errors="replace").read()
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
                for b in (ev.get("message", {}) or {}).get("content",
                                                           []) or []:
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
            call_dir = os.path.join(base_dir,
                                    "c%d_t%d" % (content_k, n_transport))
            status, fields, raw, reason = do_attempt(cfg, prompt, call_dir,
                                                     workdir, sys_prompt)
            if status == "abort":
                die("ERR_ONTG2_IDENTITY: pos %s %s" % (position, reason))
            if status == "transport":
                cap = _cap_hit(_cap_text(call_dir))
                if cap:
                    raise StopCap("pos %s: cap pattern %r; STOP (no retry). "
                                  "dir=%s" % (position, cap, call_dir))
                n_transport += 1
                if n_transport > MAX_TRANSPORT:
                    die("ERR_ONTG2_TRANSPORT: pos %s exceeded %d retries"
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
    out = subprocess.run(["mktemp", "-d",
                          "/tmp/ontg2judge%s-workdir.XXXXXX" % tag],
                         capture_output=True, text=True)
    wd = out.stdout.strip()
    if not wd or not os.path.isdir(wd):
        die("ERR_WORKDIR: mktemp failed")
    if os.listdir(wd):
        die("ERR_WORKDIR: workdir not empty: %s" % wd)
    chk = subprocess.run(["git", "-C", wd, "rev-parse",
                          "--is-inside-work-tree"],
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
    with open(os.path.join(jdir, "checkpoint.jsonl"), "a",
              encoding="utf-8") as f:
        f.write(json.dumps({"phase": phase, "id": item_id,
                            "response": response},
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
        die("ERR_ONTG2_SELFTEST(g3lp helpers): %s%s" % (st.stdout, st.stderr))
    st2 = subprocess.run([sys.executable, PATHS["analysis/ontg2.py"],
                          "--selftest"], capture_output=True, text=True)
    if st2.returncode != 0 or "ontg2 selftest OK" not in st2.stdout:
        die("ERR_ONTG2_SELFTEST(pinned analysis): %s%s"
            % (st2.stdout, st2.stderr))
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
            die("ERR_ONTG2_IDENTITY preflight %s: %s" % (cal["id"], reason))
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
    status_obj = {"phase": "preflight", "judge": cfg["id"],
                  "banners": banners, "workdir": workdir, "pass": ok,
                  "results": results}
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


def _budget_check(run_dir, adding):
    """Hard 628-call ceiling (plan section 8). Counts recorded calls."""
    cpath = os.path.join(run_dir, "call-count.json")
    n = 0
    if os.path.exists(cpath):
        n = json.load(open(cpath))["n"]
    if n + adding > BUDGET_MAX_CALLS:
        die("ERR_ONTG2_BUDGET: %d + %d > %d call ceiling; STOP, no partial "
            "scoring" % (n, adding, BUDGET_MAX_CALLS))
    with open(cpath, "w") as f:
        f.write(json.dumps({"n": n + adding}) + "\n")


def _run_block(pkey, arm, run_dir, phase, rows, n_expected, nolabel_cap,
               pos_prefix):
    if arm not in ARMS:
        die("ERR_ONTG2_ARM: %r" % arm)
    cfg = JUDGE_CFG[pkey]
    banners = verify_pins(cfg["kind"])
    jdir = os.path.join(run_dir, cfg["id"])
    workdir = _require_preflight(jdir, pkey)
    log = logger(jdir)
    manifest = json.load(open(os.path.join(MAT, "manifest.json")))
    key = "judge-%s|%s|%s" % (pkey, arm, phase)
    order = manifest["orders"][key]
    seed = manifest["seeds"][key]
    recomputed = sorted(order,
                        key=lambda i: sha_bytes(("%s|%s" % (seed, i))
                                                .encode()))
    if recomputed != order:
        die("ERR_ONTG2_ORDER: manifest %s order != recomputed" % key)
    if len(order) != n_expected:
        die("ERR_ONTG2_ORDER: %s has %d items != %d"
            % (key, len(order), n_expected))
    by_id = {r["id"]: r for r in rows}
    tmpl = read_template()
    sys_prompt = read_sysprompt() if cfg["kind"] == "claude" else None
    block = "%s-%s" % (arm, phase)
    done = load_checkpoint(jdir, block)
    _budget_check(run_dir, len([i for i in order if i not in done]))
    with open(os.path.join(jdir, "%s-position-map.jsonl" % block), "w",
              encoding="utf-8") as f:
        for i, iid in enumerate(order, 1):
            f.write(json.dumps({"position": "%s%d" % (pos_prefix, i),
                                "id": iid}, sort_keys=True) + "\n")
    log("%s %s start n=%d resume_done=%d banners=%s"
        % (block.upper(), cfg["id"], len(order), len(done),
           json.dumps(banners)))
    responses = {}
    n_nolabel = 0
    t0 = time.time()
    for i, iid in enumerate(order, 1):
        if iid in done:
            r = done[iid]
        else:
            base_dir = os.path.join(jdir, block, iid.replace(":", "_"))
            prompt = assemble_prompt(by_id[iid]["item"], tmpl)
            r = process_item(cfg, prompt, "%s%d" % (pos_prefix, i), base_dir,
                             workdir, sys_prompt, log)
            r["id"] = iid
            r["judge"] = cfg["id"]
            append_checkpoint(jdir, block, iid, r)
        responses[iid] = r
        if r.get("answer") is None:
            n_nolabel += 1
        if i % 10 == 0 or i == len(order):
            log("  %s %d/%d nolabel=%d elapsed=%.0fs"
                % (block, i, len(order), n_nolabel, time.time() - t0))
        if n_nolabel > nolabel_cap:
            die("ERR_ONTG2_NOLABEL: %d no-label > %d in %s %s; ABORT"
                % (n_nolabel, nolabel_cap, cfg["id"], block))
    banners_after = verify_pins(cfg["kind"])
    if banners_after != banners:
        die("ERR_ONTG2_PIN: banner drift")
    fld = ["id", "answer", "flags", "n_content_attempts",
           "n_transport_retries", "position", "judge"]
    rp = os.path.join(BASE, "judge-%s-%s-%s-responses.jsonl"
                      % (pkey, arm, phase))
    with open(rp, "w", encoding="utf-8") as f:
        for iid in sorted(responses):
            r = responses[iid]
            f.write(json.dumps({k: r.get(k) for k in fld}, sort_keys=True,
                               ensure_ascii=False) + "\n")
    log("%s %s done nolabel=%d -> %s"
        % (block.upper(), cfg["id"], n_nolabel, rp))
    print("%s_DONE %s nolabel=%d file=%s"
          % (block.upper(), pkey, n_nolabel, rp), flush=True)


def phase_real(pkey, arm, run_dir):
    _run_block(pkey, arm, run_dir, "real",
               load_jsonl("poc/ontology-import-g2/materials/%s"
                          % ARM_FILE[arm]),
               N_ITEMS, NOLABEL_ABORT_REAL, "")


def phase_probe(pkey, arm, run_dir):
    _run_block(pkey, arm, run_dir, "probe",
               load_jsonl("poc/ontology-import-g2/materials/probes-%s.jsonl"
                          % arm),
               N_PROBES, NOLABEL_ABORT_PROBE, "p")


# ---------------------------- assemble ----------------------------
def _assemble(resp_dir, out_dir, mock=False):
    """Pure counting + the pinned analysis (analysis/ontg2.py).
    Vacuity-zeroing per plan section 7.3; kappa on raw labels."""
    verify_pins("none")
    items = load_jsonl("poc/g2/materials/items.jsonl")
    ids = sorted(i["id"] for i in items)
    rule_of = {i["id"]: i["rule"] for i in items}
    soft = {r["position"]["g2_item"]: r for r in
            load_jsonl("data/onto-softtype/soft-type-candidates.jsonl")}
    a0 = {r["id"]: r for r in load_jsonl("poc/g2/labels-proxy.jsonl")}

    def load_resp(pk, arm, phase):
        p = os.path.join(resp_dir, "judge-%s-%s-%s-responses.jsonl"
                         % (pk, arm, phase))
        if not os.path.exists(p):
            die("missing %s" % p)
        return {r["id"]: r for r in load_jsonl_abs(p)}

    DEC = ("yes", "no")
    metrics = {"n_items": N_ITEMS, "baseline_yes": 33, "pins_ok": True}
    genrep = json.load(open(os.path.join(MAT, "generation-report.json")))
    metrics["forbidden_effects_ok"] = (
        genrep["hard_operational_axioms_emitted"] == 0)
    labels_all = {}
    for arm in ARMS:
        ra = load_resp("pA", arm, "real")
        rb = load_resp("pB", arm, "real")
        pa = load_resp("pA", arm, "probe")
        pb = load_resp("pB", arm, "probe")
        if sorted(ra) != ids or sorted(rb) != ids:
            die("ERR_ONTG2_IDS: %s response ids != item ids" % arm)
        t = {"both_yes": 0, "both_no": 0, "a_yes_b_no": 0, "a_no_b_yes": 0}
        yes_a = yes_b = dec_a = dec_b = 0
        pu = pc = 0
        r_yes = {"R1": 0, "R3": 0, "R4": 0}
        arm_labels = []
        for iid in ids:
            a = ra[iid].get("answer")
            b = rb[iid].get("answer")
            vac = soft[iid]["vacuous_by_arm"][arm]
            sa = (a == "yes") and not vac        # scored (plan 7.3)
            sb = (b == "yes") and not vac
            if a in DEC:
                dec_a += 1
            if b in DEC:
                dec_b += 1
            yes_a += int(sa)
            yes_b += int(sb)
            if sa:
                r_yes[rule_of[iid]] += 1
            if (sa or sb):
                pu += 1
            if (sa and sb):
                pc += 1
            if a in DEC and b in DEC:
                if a == "yes" and b == "yes":
                    t["both_yes"] += 1
                elif a == "no" and b == "no":
                    t["both_no"] += 1
                elif a == "yes":
                    t["a_yes_b_no"] += 1
                else:
                    t["a_no_b_yes"] += 1
            arm_labels.append({"id": iid, "arm": arm, "answer_pA": a,
                               "answer_pB": b, "vacuous": vac,
                               "scored_pA": int(sa), "scored_pB": int(sb)})
        labels_all[arm] = arm_labels

        def probe_stat(resp):
            lab = sum(1 for r in resp.values()
                      if r.get("answer") is not None)
            fs = sum(1 for r in resp.values() if r.get("answer") == "yes")
            return {"n_labelled": lab, "n_false_sat": fs}
        nv = sum(1 for iid in ids if not soft[iid]["vacuous_by_arm"][arm])
        nv3 = sum(1 for iid in ids if rule_of[iid] == "R3"
                  and not soft[iid]["vacuous_by_arm"][arm])
        metrics[arm] = {
            "yes_pA_scored": yes_a, "yes_pB_scored": yes_b,
            "decisive_pA": dec_a, "decisive_pB": dec_b,
            "agreement_raw": t,
            "probe_pA": probe_stat(pa), "probe_pB": probe_stat(pb),
            "nonvacuous": nv, "nonvacuous_r3": nv3,
            "pair_union_yes": pu, "pair_concordant_yes": pc,
            "r1_yes": r_yes["R1"], "r3_yes": r_yes["R3"],
            "r4_yes": r_yes["R4"],
        }
    # paired McNemar cells vs frozen A0 (judge-pA labels; scored)
    for arm in ("a2", "a3"):
        b_cell = c_cell = 0
        scored = {r["id"]: r["scored_pA"] for r in labels_all[arm]}
        for iid in ids:
            base_yes = a0[iid]["answer_pA"] == "yes"
            arm_yes = scored[iid] == 1
            if base_yes and not arm_yes:
                b_cell += 1
            if (not base_yes) and arm_yes:
                c_cell += 1
        metrics["mcnemar_%s_b" % arm] = b_cell
        metrics["mcnemar_%s_c" % arm] = c_cell

    p = subprocess.run([sys.executable, PATHS["analysis/ontg2.py"]],
                       input=json.dumps({"metrics": metrics}) + "\n",
                       capture_output=True, text=True)
    if p.returncode != 0:
        die("ERR_ONTG2_ANALYSIS: %s" % p.stderr)
    analysis_out = json.loads(p.stdout)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "analysis-output.json"), "w") as f:
        f.write(json.dumps(analysis_out, indent=1, sort_keys=True) + "\n")
    lp = os.path.join(out_dir, "labels-ontg2.jsonl")
    with open(lp, "w", encoding="utf-8") as f:
        for arm in ARMS:
            for r in labels_all[arm]:
                f.write(json.dumps(r, sort_keys=True, ensure_ascii=False)
                        + "\n")
    result = {
        "schema": "ontg2-result/1",
        "status": ("MOCK -- MECHANICS ONLY, NO EVIDENCE" if mock
                   else "PROVISIONAL-ON-LLM-PROXY"),
        "experiment": "g2-import",
        "baseline": {"source": "poc/g2/labels-proxy.jsonl (FROZEN g2 "
                               "primary readout; no new A0 calls)",
                     "yes": 33, "n": 84},
        "metrics": metrics,
        "analysis": analysis_out,
        "labels_sha256": file_sha(lp),
        "disclosure": (
            "PROVISIONAL-ON-LLM-PROXY (directive #11): judge-pA GPT-5.6-Sol "
            "primary, judge-pB Claude Haiku 4.5 sensitivity (vendor-family "
            "overlap with the materials' authoring agents DISCLOSED, never "
            "sole gold). kappa is pair stability, never human-agreement "
            "evidence. The later two-human adjudicated gold remains the "
            "sole authority for any permanent scientific adoption; "
            "reconcile + re-run when it arrives. The primary gate is a "
            "point-estimate engineering gate (>=34/84), not a claim of "
            "statistical superiority."),
    }
    rpath = os.path.join(out_dir, "result.json")
    with open(rpath, "w") as f:
        f.write(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"a1_yes": metrics["a1"]["yes_pA_scored"],
                      "a2_yes": metrics["a2"]["yes_pA_scored"],
                      "a3_yes": metrics["a3"]["yes_pA_scored"],
                      "baseline": 33,
                      "instrument_valid":
                          analysis_out["gates"]["instrument_valid"],
                      "informative_valid":
                          analysis_out["gates"]["informative_valid"],
                      "primary_pass":
                          analysis_out["analysis"]["primary_pass"]},
                     sort_keys=True))
    print("ASSEMBLE_DONE -> %s" % rpath)
    return analysis_out


def phase_assemble(run_dir):
    _assemble(BASE, BASE)


# ---------------------------- mock ----------------------------
def _mock_answer(scenario, pk, arm, iid, vac):
    h = int(hashlib.sha256(("mock|%s|%s|%s" % (pk, arm, iid))
                           .encode()).hexdigest(), 16)
    if scenario == "go":
        # target a3 ~ 45 yes, a2 ~ 40, a1 ~ 30 (pre-vacuity); pB shadows
        # pA with ~10% flips (kappa high)
        base = {"a1": 40, "a2": 55, "a3": 65}[arm]
        hA = int(hashlib.sha256(("mock|pA|%s|%s" % (arm, iid))
                                .encode()).hexdigest(), 16)
        ans = "yes" if (hA % 100) < base else "no"
        if pk == "pB" and (h % 10) == 0:
            ans = "no" if ans == "yes" else "yes"
        return ans
    if scenario == "nogo":
        base = {"a1": 15, "a2": 25, "a3": 30}[arm]
        hA = int(hashlib.sha256(("mock|pA|%s|%s" % (arm, iid))
                                .encode()).hexdigest(), 16)
        ans = "yes" if (hA % 100) < base else "no"
        if pk == "pB" and (h % 10) == 0:
            ans = "no" if ans == "yes" else "yes"
        return ans
    # scenario == "instrument": judges anti-correlated -> kappa collapses
    if pk == "pA":
        return "yes" if (h % 2) == 0 else "no"
    hA = int(hashlib.sha256(("mock|pA|%s|%s" % (arm, iid))
                            .encode()).hexdigest(), 16)
    return "no" if (hA % 2) == 0 else "yes"


def phase_mock(run_dir, scenario):
    """No-LLM end-to-end mechanics check: synthesizes deterministic judge
    response files, runs the REAL assemble + pinned analysis, then
    evaluates the DRAFT record's verdict_rules with the registry
    evaluator. MOCK output is mechanics evidence only."""
    if scenario not in ("go", "nogo", "instrument"):
        die("mock scenario must be go|nogo|instrument")
    verify_pins("none")
    st = subprocess.run([sys.executable, PATHS["analysis/ontg2.py"],
                         "--selftest"], capture_output=True, text=True)
    if st.returncode != 0 or "ontg2 selftest OK" not in st.stdout:
        die("ERR_ONTG2_SELFTEST: %s%s" % (st.stdout, st.stderr))
    mdir = os.path.join(run_dir, "mock-%s" % scenario)
    os.makedirs(mdir, exist_ok=True)
    soft = {r["position"]["g2_item"]: r for r in
            load_jsonl("data/onto-softtype/soft-type-candidates.jsonl")}
    for arm in ARMS:
        rows = load_jsonl("poc/ontology-import-g2/materials/%s"
                          % ARM_FILE[arm])
        probes = load_jsonl("poc/ontology-import-g2/materials/"
                            "probes-%s.jsonl" % arm)
        for pk in ("pA", "pB"):
            with open(os.path.join(mdir, "judge-%s-%s-real-responses.jsonl"
                                   % (pk, arm)), "w") as f:
                for r in rows:
                    vac = soft[r["id"]]["vacuous_by_arm"][arm]
                    ans = _mock_answer(scenario, pk, arm, r["id"], vac)
                    f.write(json.dumps({"id": r["id"], "answer": ans,
                                        "flags": [],
                                        "n_content_attempts": 1,
                                        "n_transport_retries": 0,
                                        "position": "m", "judge": "mock-%s"
                                        % pk}, sort_keys=True) + "\n")
            with open(os.path.join(mdir, "judge-%s-%s-probe-responses.jsonl"
                                   % (pk, arm)), "w") as f:
                for pr in probes:
                    # instrument scenario also breaks the probe gate
                    ans = ("yes" if scenario == "instrument" and
                           int(hashlib.sha256(pr["id"].encode())
                               .hexdigest(), 16) % 2 == 0 else "no")
                    f.write(json.dumps({"id": pr["id"], "answer": ans,
                                        "flags": [],
                                        "n_content_attempts": 1,
                                        "n_transport_retries": 0,
                                        "position": "m", "judge": "mock-%s"
                                        % pk}, sort_keys=True) + "\n")
    out = _assemble(mdir, mdir, mock=True)
    # evaluate the DRAFT record's verdict_rules mechanically
    sys.path.insert(0, os.path.join(REPO, "tools/registry"))
    import kot_common
    rec = json.load(open(os.path.join(
        REPO, "registry/experiments/g2-import.json")))
    doc = {"gates": out["gates"], "analysis": out["analysis"]}
    fired = None
    for rule in rec["verdict_rules"]:
        if kot_common.eval_expr(rule["when"], doc):
            fired = rule["verdict"]
            break
    expected = {"go": "PASS", "nogo": "FAIL",
                "instrument": "INSTRUMENT-INVALID"}[scenario]
    ok = fired == expected
    print("MOCK scenario=%s fired=%s expected=%s => %s"
          % (scenario, fired, expected, "GREEN" if ok else "RED"))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            die("usage: preflight <pA|pB> <run_dir> | "
                "real|probe <pA|pB> <a1|a2|a3> <run_dir> | "
                "assemble <run_dir> | mock <run_dir> <go|nogo|instrument>")
        mode = sys.argv[1]
        if mode == "preflight":
            phase_preflight(sys.argv[2], sys.argv[3])
        elif mode == "real":
            phase_real(sys.argv[2], sys.argv[3], sys.argv[4])
        elif mode == "probe":
            phase_probe(sys.argv[2], sys.argv[3], sys.argv[4])
        elif mode == "assemble":
            phase_assemble(sys.argv[2])
        elif mode == "mock":
            phase_mock(sys.argv[2], sys.argv[3])
        else:
            die("unknown mode %r" % mode)
    except StopCap as e:
        sys.stderr.write("RUN_ONTG2_STOPCAP: %s\n" % e)
        sys.exit(3)
    except AbortExperiment as e:
        sys.stderr.write("RUN_ONTG2_BLINDING_ABORT: %s\n" % e)
        sys.exit(4)
