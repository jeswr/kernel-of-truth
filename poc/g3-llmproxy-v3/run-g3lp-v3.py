#!/usr/bin/env python3
"""run-g3lp-v3 -- MECHANICAL executor of g3-llmproxy-v3, per the pinned spec
`poc/g3-llmproxy-v3/judge-invocation.md` and the registry record
`registry/experiments/g3-llmproxy-v3.json`. Opus experiment-RUNNER role:
DESIGNS NOTHING, CONCLUDES NOTHING. Faithful port of the proven
poc/truthstyle-2x2/run-dts-judges.py, adapted to the g3 two-pass protocol and
the v3 fence-extraction (ASM-0650) + A1 blinding-scan (ASM-0740) reference
implementations, which are IMPORTED verbatim from analysis/g3_llmproxy_v3.py
(never reimplemented). Any situation the spec does not decide is a HARD ABORT
(boundary stop to Fable); the runner never improvises.

Usage:
  run-g3lp-v3.py preflight <pA|pB> <run_dir>
  run-g3lp-v3.py pass <pA|pB> <A|B> <run_dir>
  run-g3lp-v3.py probe <pA|pB> <run_dir>
  run-g3lp-v3.py assemble <run_dir>
"""
import json, os, re, sys, hashlib, subprocess, time

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
SCRATCH = ("/tmp/claude-1000/-home-ec2-user-css/"
           "85798a0b-4e71-4020-b0b9-ac1fed9631d0/scratchpad")
CODEX_HOME_ISO = os.path.join(SCRATCH, "codex-home-iso")

sys.path.insert(0, os.path.join(REPO, "analysis"))
import g3_llmproxy_v3 as G   # the pinned §5 + §6 reference implementations

# ---- §0 pinned inputs (fail-close on every one; ERR_G3P_PIN) ----
PINS = {
    "data/instance-descriptions/instances.jsonl":
        "04cdfbfd77117e6f6e9313d53df6534b01077e241cd7664ca6f709cd7be311f1",
    "data/instance-descriptions/conditions.jsonl":
        "fec2bc669b40077d057f59d6480eee3501ef396f62af64171479676a4ed3590a",
    "data/instance-descriptions/annotation-protocol.md":
        "57610024480122a5db9596e2d27dd3cb717167a88673e2c9eeb4fa9a98414284",
    "poc/g3-llmproxy/prompt-template-pass-a.txt":
        "3cd7b450948770916ae937186f15ebbdb15d052c2a7c60f866642dacde8ea54e",
    "poc/g3-llmproxy/prompt-template-pass-b.txt":
        "dbb0693720cb0d1c9bf3f0861ef6a6cce5bbfaff83f87c4baa5343ea011f3380",
    "poc/g3-llmproxy/output-schema-pass-a.json":
        "fa1e46a3d5a4e0e1e49992c9f5f5f08b902ae66470dfb59aebb16aa0f26624d7",
    "poc/g3-llmproxy/output-schema-pass-b.json":
        "5576ee23c66bc797b7f443533279da3aaa963164c63bd7ffc0644ec47da55137",
    "poc/g3-llmproxy/judge-pB-system-prompt-pass-a.txt":
        "d82a0450f697562244cca2f172956424f6a902bd4bdb5ab80a752b9c5c4526d9",
    "poc/g3-llmproxy-v2/judge-pB-system-prompt-pass-b.txt":
        "d0672138241f2722f24be59cba2256ed2f834048ad89de2b9c2f70d94e7b9122",
    "poc/g3-llmproxy/probe-b.jsonl":
        "5691473c878df8623054664c02717274127b2a53eeb9068459064f08fa35b287",
    "poc/g3-llmproxy/probe-b-manifest.json":
        "7269a629f9fdbaa4eb4f2214e89da10e4e051dd24d07a0eada27d059509df7bc",
    "poc/g3-llmproxy/calibration-items.jsonl":
        "90ffc7dae4d60918d08ebc6c1a7fc355ee0f21aad4986219fcd9f6d944a045cc",
    "analysis/g3_llmproxy_v3.py":
        "fbaea0c0559962fed724cf1a94e3f7c7dccca68ddfbc364b6f05da4a3712d21e",
    "poc/g3-llmproxy-v3/judge-invocation.md":
        "9bae8b10788dc83ec0a56ed89a1cf3efa33dbb8accc389a8d0e276eafc4b9782",
}
INSTANCE_DESC_DIGEST = ("1a55a2194f667a0f647e8cd3ce21b2c6"
                        "327446b020dd24576c5263ea930d4f7d")

JUDGE_CFG = {
    "pA": {"id": "judge-pA-gpt56sol", "kind": "codex", "model": "gpt-5.6-sol"},
    "pB": {"id": "judge-pB-haiku45", "kind": "claude",
           "model": "claude-haiku-4-5-20251001"},
}

EXPECT_CODEX_VER = "codex-cli 0.144.1"
EFFORT = "low"
NPX_CODEX = ["npx", "-y", "@openai/codex@0.144.1"]

# codex §6 banned event-type substrings (tool/command use => attempt INVALID)
BANNED_TYPE_SUBSTR = ["exec_command", "terminal_interaction", "unified_exec",
                      "tool_call", "web_search", "patch_apply", "view_image",
                      "image_generation", "collab_"]
TRANSPORT_TYPE_SUBSTR = ["stream_error", "rate_limit", "rate-limit"]

TRANSPORT_BACKOFF = [30, 60, 120, 300, 300, 300, 300, 300, 300, 300]  # §7
MAX_TRANSPORT = 10
MAX_CONTENT = 3
NOLABEL_ABORT_PASS = 10       # §7: >10 no-label in one pass => ABORT
NOLABEL_ABORT_PROBE = 3       # §7: >3 no-label probes => ABORT

# Coordinator directive: on a Haiku/session/usage cap, STOP immediately and
# report exact error + counts (no retry-spin). These patterns short-circuit
# the transport backoff into an immediate StopCap.
CAP_PATTERNS = [
    "usage limit", "usage-limit", "rate limit reached", "quota",
    "session limit", "exceeded your", "too many requests",
    "resets at", "reset at", "try again later", "credit balance",
    "insufficient", "you've reached", "you have reached", "limit reached",
    "429", "upgrade to increase", "monthly limit", "weekly limit",
]

PATHS = {k: os.path.join(REPO, k) for k in PINS}


class AbortExperiment(Exception):
    pass


class StopCap(Exception):
    pass


def die(msg):
    sys.stderr.write("RUN_G3LP_ABORT: %s\n" % msg)
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


def verify_pins(kind):
    for rel, want in PINS.items():
        got = file_sha(PATHS[rel])
        if got != want:
            die("ERR_G3P_PIN: %s sha %s != pinned %s" % (rel, got, want))
    if os.path.exists(os.path.expanduser("~/.claude/CLAUDE.md")):
        die("ERR_G3P_PIN: ~/.claude/CLAUDE.md exists (would inject context)")
    # instance-descriptions corpus digest re-verify (spec §0/§8)
    dig = corpus_digest(os.path.join(REPO, "data/instance-descriptions"))
    if dig != INSTANCE_DESC_DIGEST:
        die("ERR_G3P_PIN: instance-descriptions digest %s != pinned %s"
            % (dig, INSTANCE_DESC_DIGEST))
    banners = {}
    if kind == "codex":
        env = dict(os.environ); env["CODEX_HOME"] = CODEX_HOME_ISO
        ver = subprocess.run(NPX_CODEX + ["--version"], capture_output=True,
                             text=True, env=env).stdout.strip()
        if ver != EXPECT_CODEX_VER:
            die("ERR_G3P_PIN: npx codex version %r != %r" % (ver, EXPECT_CODEX_VER))
        banners = {"npx_codex": ver}
    else:
        cv = subprocess.run(["claude", "--version"], capture_output=True,
                            text=True).stdout.strip()
        vt = claude_version_tuple(cv)
        if vt is None or vt < (2, 1, 201):
            die("ERR_G3P_PIN: claude version %r < 2.1.201" % cv)
        banners = {"claude": cv}
    return banners


def corpus_digest(root):
    """kot-corpus-hash/1 (reference: tools/registry/corpus-pin.py)."""
    lines = []
    for dp, _dn, fns in os.walk(root):
        for fn in fns:
            fp = os.path.join(dp, fn)
            if os.path.islink(fp) or not os.path.isfile(fp):
                continue
            rel = os.path.relpath(fp, root).replace(os.sep, "/")
            lines.append("%s  %s\n" % (file_sha(fp), rel))
    lines.sort(key=lambda ln: ln.split("  ", 1)[1])
    return sha_bytes("".join(lines).encode("utf-8"))


# ---------------------------- data loading ----------------------------
def load_jsonl_records(path):
    out = []
    for l in open(path, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        o = json.loads(l)
        if "_meta" in o and len(o) == 1:
            continue
        out.append(o)
    return out


def load_instances():
    recs = load_jsonl_records(os.path.join(REPO, "data/instance-descriptions/instances.jsonl"))
    return {r["instance_id"]: r for r in recs}


def load_conditions():
    recs = load_jsonl_records(os.path.join(REPO, "data/instance-descriptions/conditions.jsonl"))
    return {r["condition_set_id"]: r for r in recs}


def load_manifest():
    return json.load(open(os.path.join(REPO, "poc/g3-llmproxy/probe-b-manifest.json")))


def load_probes():
    recs = [json.loads(l) for l in
            open(os.path.join(REPO, "poc/g3-llmproxy/probe-b.jsonl"), encoding="utf-8")
            if l.strip()]
    return {r["id"]: r for r in recs}


def load_calibration():
    return [json.loads(l) for l in
            open(os.path.join(REPO, "poc/g3-llmproxy/calibration-items.jsonl"),
                 encoding="utf-8") if l.strip()]


def read_template(pas):
    p = os.path.join(REPO, "poc/g3-llmproxy/prompt-template-pass-%s.txt"
                     % ("a" if pas == "A" else "b"))
    return open(p, encoding="utf-8").read()


def read_sysprompt(pas):
    if pas == "A":
        p = os.path.join(REPO, "poc/g3-llmproxy/judge-pB-system-prompt-pass-a.txt")
    else:
        p = os.path.join(REPO, "poc/g3-llmproxy-v2/judge-pB-system-prompt-pass-b.txt")
    return open(p, encoding="utf-8").read().rstrip("\n")   # $(cat) strips trailing \n


def schema_path(pas):
    return os.path.join(REPO, "poc/g3-llmproxy/output-schema-pass-%s.json"
                        % ("a" if pas == "A" else "b"))


# ---------------------------- §2 prompt assembly ----------------------------
def concept_word(concept_id):
    return concept_id.rsplit(":", 1)[-1].replace("-", " ")


def bindings_block(bindings):
    return "\n".join("- %s = %s" % (k, v) for k, v in bindings.items())


def conditions_block(conds):
    return "\n".join("- %s: %s" % (c["cid"], c["text"]) for c in conds)


def assemble_pass_a(tmpl, text, target, word):
    s = tmpl.replace("{{TEXT}}", text)
    s = s.replace("{{TARGET}}", target)
    s = s.replace("{{WORD}}", word)
    return s


def assemble_pass_b(tmpl, text, bindings, conds):
    s = tmpl.replace("{{TEXT}}", text)
    s = s.replace("{{BINDINGS}}", bindings_block(bindings))
    s = s.replace("{{CONDITIONS}}", conditions_block(conds))
    return s


def prompt_for_real(item_id, pas, insts, conds_by_set, tmpl):
    it = insts[item_id]
    if pas == "A":
        return assemble_pass_a(tmpl, it["text"], it["target"],
                               concept_word(it["concept_id"]))
    cset = conds_by_set[it["condition_set_id"]]
    return assemble_pass_b(tmpl, it["text"], it["bindings"], cset["conditions"])


def prompt_for_probe(probe_id, probes, tmpl):
    r = probes[probe_id]
    return assemble_pass_b(tmpl, r["text"], r["bindings"], r["conditions"])


def prompt_for_cal(cal, tmpl):
    if cal["pass"] == "A":
        return assemble_pass_a(tmpl, cal["text"], cal["target"], cal["word"])
    return assemble_pass_b(tmpl, cal["text"], cal["bindings"], cal["conditions"])


def allowed_cids_real(item_id, pas, insts, conds_by_set):
    if pas == "A":
        return None
    cset = conds_by_set[insts[item_id]["condition_set_id"]]
    return [c["cid"] for c in cset["conditions"]]


# ---------------------------- invocation ----------------------------
def run_codex(model, prompt_text, attempt_dir, workdir, pas):
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
                       "--output-schema", schema_path(pas),
                       "-o", last_msg, "-"]
    env = dict(os.environ); env["CODEX_HOME"] = CODEX_HOME_ISO
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


def _cap_text(attempt_dir, extra=""):
    txt = extra
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


# §5 field checks -----------------------------------------------------------
def label_pass_a(obj):
    """obj -> (label, reason). label None => invalid."""
    if not (isinstance(obj, dict) and list(obj.keys()) == ["q1"]):
        return None, None, "parse_failure"
    tok = G.normalize_token(obj["q1"])
    if tok not in G.VALID_TOKENS:
        return None, None, "parse_failure"
    return tok, [], None


def label_pass_b(obj, allowed_cids):
    if not (isinstance(obj, dict)
            and set(obj.keys()) == {"q2", "q2_failing_conditions"}):
        return None, None, "parse_failure"
    tok = G.normalize_token(obj["q2"])
    if tok not in G.VALID_TOKENS:
        return None, None, "parse_failure"
    lst = obj["q2_failing_conditions"]
    if not isinstance(lst, list):
        return None, None, "parse_failure"
    for e in lst:
        if not (isinstance(e, str) and re.match(r"^c[0-9]+$", e)
                and e in allowed_cids):
            return None, None, "parse_failure"
    if tok == "no" and len(lst) == 0:
        return None, None, "parse_failure"
    if tok != "no" and len(lst) != 0:
        return None, None, "parse_failure"
    return tok, list(lst), None


def validate_codex(exit_code, attempt_dir, pas, allowed_cids):
    """(status, fields, raw_answer, reason). status in valid/content_invalid/transport."""
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
    if pas == "A":
        lab, _, reason = label_pass_a(obj)
        fields = {"q1": lab} if lab else None
    else:
        lab, flst, reason = label_pass_b(obj, allowed_cids)
        fields = {"q2": lab, "q2_failing_conditions": flst} if lab else None
    if fields is None:
        return ("content_invalid", None, raw, reason)
    return ("valid", fields, raw, None)


def validate_claude(exit_code, attempt_dir, pas, allowed_cids):
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
    # §6 identity tripwires -> ABORT the pass on mismatch
    mu = result.get("modelUsage") or {}
    if not (init and init.get("model") == "claude-haiku-4-5-20251001"
            and init.get("apiKeySource") == "none"
            and set(mu.keys()) == {"claude-haiku-4-5-20251001"}):
        return ("abort", None, None,
                "identity_mismatch(model=%r apiKeySource=%r modelUsage=%r)"
                % (init.get("model") if init else None,
                   init.get("apiKeySource") if init else None, sorted(mu.keys())))
    # §6 / H1 zero-tool tripwires -> content INVALID
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
    if pas == "A":
        lab, _, reason = label_pass_a(obj)
        fields = {"q1": lab} if lab else None
    else:
        lab, flst, reason = label_pass_b(obj, allowed_cids)
        fields = {"q2": lab, "q2_failing_conditions": flst} if lab else None
    if fields is None:
        return ("content_invalid", None, raw, reason)
    return ("valid", fields, raw, None)


def do_attempt(cfg, prompt, attempt_dir, workdir, sys_prompt, pas, allowed_cids):
    if cfg["kind"] == "codex":
        rc = run_codex(cfg["model"], prompt, attempt_dir, workdir, pas)
        status, fields, raw, reason = validate_codex(rc, attempt_dir, pas, allowed_cids)
    else:
        rc = run_claude(prompt, attempt_dir, workdir, sys_prompt)
        status, fields, raw, reason = validate_claude(rc, attempt_dir, pas, allowed_cids)
    # §6 blinding audit (pinned reference impls; ABORT on any non-excluded hit)
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


def process_item(cfg, prompt, position, base_dir, workdir, sys_prompt, pas,
                 allowed_cids, log):
    n_content = 0
    n_transport = 0
    last_reason = last_raw = None
    for content_k in range(1, MAX_CONTENT + 1):
        while True:
            call_dir = os.path.join(base_dir, "c%d_t%d" % (content_k, n_transport))
            status, fields, raw, reason = do_attempt(
                cfg, prompt, call_dir, workdir, sys_prompt, pas, allowed_cids)
            if status == "abort":
                die("ERR_G3P_IDENTITY: pos %s %s — ABORT the pass (spec §6)"
                    % (position, reason))
            if status == "transport":
                # cap short-circuit (coordinator directive): no retry-spin
                cap = _cap_hit(_cap_text(call_dir))
                if cap:
                    raise StopCap("pos %s: usage/session cap pattern %r hit; "
                                  "STOP (no retry). attempt_dir=%s"
                                  % (position, cap, call_dir))
                n_transport += 1
                if n_transport > MAX_TRANSPORT:
                    die("ERR_G3P_TRANSPORT: pos %s exceeded %d transport retries"
                        % (position, MAX_TRANSPORT))
                back = TRANSPORT_BACKOFF[min(n_transport - 1, len(TRANSPORT_BACKOFF) - 1)]
                log("  pos %s transport failure (try %d), backoff %ds"
                    % (position, n_transport, back))
                time.sleep(back)
                continue
            break
        n_content = content_k
        if status == "valid":
            r = {"flags": [], "n_content_attempts": n_content,
                 "n_transport_retries": n_transport, "position": position}
            r.update(fields)
            return r
        last_reason, last_raw = reason, raw
        log("  pos %s content attempt %d INVALID (%s)"
            % (position, content_k, reason))
    r = {"flags": ["judge_no_label", last_reason or "parse_failure"],
         "n_content_attempts": n_content, "n_transport_retries": n_transport,
         "position": position}
    if pas == "A":
        r["q1"] = None
    else:
        r["q2"] = None
        r["q2_failing_conditions"] = None
    return r


def make_workdir(tag):
    out = subprocess.run(["mktemp", "-d", "/tmp/judge%s-workdir.XXXXXX" % tag],
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


# ---------------------------- checkpoint helpers ----------------------------
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
    cp = os.path.join(jdir, "checkpoint.jsonl")
    with open(cp, "a", encoding="utf-8") as f:
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
    # runner-local selftest FIRST (spec §8, cal:g3lp-x1)
    st = subprocess.run([sys.executable, os.path.join(REPO, "analysis/g3_llmproxy_v3.py"),
                         "--selftest"], capture_output=True, text=True)
    if st.returncode != 0 or "g3-llmproxy-v3 selftest OK" not in st.stdout:
        die("ERR_G3P_SELFTEST: %s%s" % (st.stdout, st.stderr))
    banners = verify_pins(cfg["kind"])
    jdir = os.path.join(run_dir, cfg["id"])
    os.makedirs(jdir, exist_ok=True)
    workdir = make_workdir(pkey)
    with open(os.path.join(jdir, "workdir-path.txt"), "w") as f:
        f.write(workdir + "\n")
    log = logger(jdir)
    log("PREFLIGHT %s selftest=OK banners=%s workdir=%s"
        % (cfg["id"], json.dumps(banners), workdir))
    results = []
    ok = True
    for cal in load_calibration():
        pas = cal["pass"]
        tmpl = read_template(pas)
        sys_prompt = read_sysprompt(pas) if cfg["kind"] == "claude" else None
        prompt = prompt_for_cal(cal, tmpl)
        allowed = [c["cid"] for c in cal["conditions"]] if pas == "B" else None
        call_dir = os.path.join(jdir, "preflight", cal["id"])
        status, fields, raw, reason = do_attempt(
            cfg, prompt, call_dir, workdir, sys_prompt, pas, allowed)
        if status == "abort":
            die("ERR_G3P_IDENTITY preflight %s: %s" % (cal["id"], reason))
        got = fields if status == "valid" else None
        item_ok = (status == "valid") and (got == cal["expected"])
        results.append({"id": cal["id"], "status": status, "got": got,
                        "expected": cal["expected"], "reason": reason, "pass": item_ok})
        log("  PREFLIGHT %s status=%s got=%s expected=%s => %s"
            % (cal["id"], status, got, cal["expected"], "PASS" if item_ok else "FAIL"))
        if not item_ok:
            ok = False
    status_obj = {"phase": "preflight", "judge": cfg["id"], "banners": banners,
                  "workdir": workdir, "pass": ok, "results": results}
    with open(os.path.join(jdir, "preflight-status.json"), "w") as f:
        f.write(json.dumps(status_obj, indent=2, sort_keys=True) + "\n")
    print("PREFLIGHT %s %s: %s" % (pkey, cfg["id"], "PASS" if ok else "FAIL"), flush=True)
    for r in results:
        print("  %s status=%s got=%r expected=%r => %s"
              % (r["id"], r["status"], r["got"], r["expected"],
                 "PASS" if r["pass"] else "FAIL"), flush=True)
    if not ok:
        die("preflight FAILED for %s" % pkey)


def _require_preflight(jdir, pkey):
    ps = os.path.join(jdir, "preflight-status.json")
    if not os.path.exists(ps):
        die("no preflight-status.json for %s; run preflight first" % pkey)
    if not json.load(open(ps)).get("pass"):
        die("preflight %s did not PASS; refusing" % pkey)
    wp = os.path.join(jdir, "workdir-path.txt")
    workdir = open(wp).read().strip()
    if not os.path.isdir(workdir):
        die("recorded workdir missing: %s" % workdir)
    return workdir


def phase_pass(pkey, pas, run_dir):
    cfg = JUDGE_CFG[pkey]
    banners = verify_pins(cfg["kind"])
    jdir = os.path.join(run_dir, cfg["id"])
    workdir = _require_preflight(jdir, pkey)
    log = logger(jdir)
    insts = load_instances()
    conds = load_conditions()
    manifest = load_manifest()
    okey = "judge-%s-pass%s" % (pkey, pas)   # manifest keys: judge-pA-passA etc.
    order = manifest["real_orders"][okey]
    # defense-in-depth: manifest order == seed-pinned sha256 sort
    seed = manifest["seed_real_orders"][okey]
    recomputed = sorted(order, key=lambda i: sha_bytes(("%s|%s" % (seed, i)).encode()))
    if recomputed != order:
        die("ERR_G3P_ORDER: manifest %s order != recomputed seed sort" % okey)
    if len(order) != 200:
        die("ERR_G3P_ORDER: %s has %d items" % (okey, len(order)))
    tmpl = read_template(pas)
    sys_prompt = read_sysprompt(pas) if cfg["kind"] == "claude" else None
    phase = "pass%s" % pas
    done = load_checkpoint(jdir, phase)
    # position map (provenance)
    pref = "" if pas == "A" else "b"
    with open(os.path.join(jdir, "%s-position-map.jsonl" % cfg["id"]), "a",
              encoding="utf-8") as f:
        for i, iid in enumerate(order, 1):
            f.write(json.dumps({"position": "%s%d" % (pref, i), "id": iid},
                               sort_keys=True) + "\n")
    log("PASS %s %s start n=%d resume_done=%d banners=%s"
        % (cfg["id"], pas, len(order), len(done), json.dumps(banners)))
    responses = {}
    n_nolabel = 0
    t0 = time.time()
    for i, iid in enumerate(order, 1):
        if iid in done:
            r = done[iid]
        else:
            base_dir = os.path.join(jdir, phase, iid)
            allowed = allowed_cids_real(iid, pas, insts, conds)
            prompt = prompt_for_real(iid, pas, insts, conds, tmpl)
            r = process_item(cfg, prompt, "%s%d" % (pref, i), base_dir, workdir,
                             sys_prompt, pas, allowed, log)
            r["id"] = iid
            r["judge"] = cfg["id"]
            append_checkpoint(jdir, phase, iid, r)
        responses[iid] = r
        lab = r.get("q1") if pas == "A" else r.get("q2")
        if lab is None:
            n_nolabel += 1
        if i % 20 == 0 or i == len(order):
            log("  %s %d/%d nolabel=%d elapsed=%.0fs"
                % (pas, i, len(order), n_nolabel, time.time() - t0))
        if n_nolabel > NOLABEL_ABORT_PASS:
            die("ERR_G3P_NOLABEL: %d no-label > %d in %s pass %s; ABORT"
                % (n_nolabel, NOLABEL_ABORT_PASS, cfg["id"], pas))
    banners_after = verify_pins(cfg["kind"])
    if banners_after != banners:
        die("ERR_G3P_PIN: banner drift %s -> %s" % (banners, banners_after))
    # write responses file
    outdir = os.path.join(REPO, "data/g3-annot-llmproxy-v3")
    os.makedirs(outdir, exist_ok=True)
    fld = (["id", "q1", "flags", "n_content_attempts", "n_transport_retries",
            "position", "judge"] if pas == "A" else
           ["id", "q2", "q2_failing_conditions", "flags", "n_content_attempts",
            "n_transport_retries", "position", "judge"])
    rp = os.path.join(outdir, "judge-%s-pass-%s-responses.jsonl"
                      % (pkey, "a" if pas == "A" else "b"))
    with open(rp, "w", encoding="utf-8") as f:
        for iid in sorted(responses):
            r = responses[iid]
            f.write(json.dumps({k: r.get(k) for k in fld}, sort_keys=True,
                               ensure_ascii=False) + "\n")
    log("PASS %s %s done nolabel=%d -> %s" % (cfg["id"], pas, n_nolabel, rp))
    print("PASS_DONE %s %s nolabel=%d file=%s" % (pkey, pas, n_nolabel, rp), flush=True)


def phase_probe(pkey, run_dir):
    cfg = JUDGE_CFG[pkey]
    banners = verify_pins(cfg["kind"])
    jdir = os.path.join(run_dir, cfg["id"])
    workdir = _require_preflight(jdir, pkey)
    log = logger(jdir)
    manifest = load_manifest()
    probes = load_probes()
    order = manifest["probe_orders"]["judge-%s" % pkey]
    seed = manifest["seed_probe_orders"]["judge-%s" % pkey]
    recomputed = sorted(order, key=lambda i: sha_bytes(("%s|%s" % (seed, i)).encode()))
    if recomputed != order:
        die("ERR_G3P_ORDER: probe order != recomputed seed sort for %s" % pkey)
    if len(order) != 30:
        die("ERR_G3P_ORDER: probe has %d items" % len(order))
    tmpl = read_template("B")
    sys_prompt = read_sysprompt("B") if cfg["kind"] == "claude" else None
    phase = "probe"
    done = load_checkpoint(jdir, phase)
    with open(os.path.join(jdir, "%s-position-map.jsonl" % cfg["id"]), "a",
              encoding="utf-8") as f:
        for i, iid in enumerate(order, 1):
            f.write(json.dumps({"position": "p%d" % i, "id": iid}, sort_keys=True) + "\n")
    log("PROBE %s start n=%d resume_done=%d" % (cfg["id"], len(order), len(done)))
    responses = {}
    n_nolabel = 0
    for i, iid in enumerate(order, 1):
        if iid in done:
            r = done[iid]
        else:
            base_dir = os.path.join(jdir, phase, iid)
            allowed = [c["cid"] for c in probes[iid]["conditions"]]
            prompt = prompt_for_probe(iid, probes, tmpl)
            r = process_item(cfg, prompt, "p%d" % i, base_dir, workdir,
                             sys_prompt, "B", allowed, log)
            r["id"] = iid
            r["judge"] = cfg["id"]
            append_checkpoint(jdir, phase, iid, r)
        responses[iid] = r
        if r.get("q2") is None:
            n_nolabel += 1
        if n_nolabel > NOLABEL_ABORT_PROBE:
            die("ERR_G3P_NOLABEL: %d no-label probes > %d for %s; ABORT"
                % (n_nolabel, NOLABEL_ABORT_PROBE, cfg["id"]))
    banners_after = verify_pins(cfg["kind"])
    if banners_after != banners:
        die("ERR_G3P_PIN: banner drift %s -> %s" % (banners, banners_after))
    outdir = os.path.join(REPO, "data/g3-annot-llmproxy-v3")
    os.makedirs(outdir, exist_ok=True)
    fld = ["id", "q2", "q2_failing_conditions", "flags", "n_content_attempts",
           "n_transport_retries", "position", "judge"]
    rp = os.path.join(outdir, "judge-%s-probe-responses.jsonl" % pkey)
    with open(rp, "w", encoding="utf-8") as f:
        for iid in sorted(responses):
            r = responses[iid]
            f.write(json.dumps({k: r.get(k) for k in fld}, sort_keys=True,
                               ensure_ascii=False) + "\n")
    log("PROBE %s done nolabel=%d -> %s" % (cfg["id"], n_nolabel, rp))
    print("PROBE_DONE %s nolabel=%d file=%s" % (pkey, n_nolabel, rp), flush=True)


DEC = ("yes", "no")


def _load_resp(pk, tag):
    p = os.path.join(REPO, "data/g3-annot-llmproxy-v3",
                     "judge-%s-%s.jsonl" % (pk, tag))
    if not os.path.exists(p):
        die("missing response file %s" % p)
    out = {}
    for l in open(p, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        r = json.loads(l)
        out[r["id"]] = r
    return out


def phase_assemble(run_dir):
    """§9 assembly: labels-proxy.jsonl + summary.json + the final-record
    metrics (the exact _rec inputs of analysis/g3_llmproxy_v3.py). Pure
    counting over the pinned response files; DESIGNS/CONCLUDES nothing."""
    outdir = os.path.join(REPO, "data/g3-annot-llmproxy-v3")
    insts = load_instances()
    aA = _load_resp("pA", "pass-a-responses")
    aB = _load_resp("pA", "pass-b-responses")
    bA = _load_resp("pB", "pass-a-responses")
    bB = _load_resp("pB", "pass-b-responses")
    aP = _load_resp("pA", "probe-responses")
    bP = _load_resp("pB", "probe-responses")
    ids = sorted(insts.keys())
    if not (len(aA) == len(aB) == len(bA) == len(bB) == 200):
        die("response files not all 200: %d/%d/%d/%d"
            % (len(aA), len(aB), len(bA), len(bB)))

    # preflight_pass = AND of both judges' recorded preflight-status
    pf = True
    for jid in ("judge-pA-gpt56sol", "judge-pB-haiku45"):
        ps = os.path.join(run_dir, jid, "preflight-status.json")
        pf = pf and (os.path.exists(ps) and json.load(open(ps)).get("pass") is True)

    labels = []
    n_dual = 0
    nec = {"both": 0, "a": 0, "b": 0, "neither": 0}
    suf_conc = suf_union = 0
    nec_a = nec_b = suf_a = suf_b = 0
    hist = {}
    for iid in ids:
        q1a = aA[iid].get("q1"); q2a = aB[iid].get("q2")
        q1b = bA[iid].get("q1"); q2b = bB[iid].get("q2")
        fa = aB[iid].get("q2_failing_conditions")
        fb = bB[iid].get("q2_failing_conditions")
        dec_a = (q1a in DEC and q2a in DEC)
        dec_b = (q1b in DEC and q2b in DEC)
        dd = dec_a and dec_b
        nva = (q1a == "yes" and q2a == "no")
        nvb = (q1b == "yes" and q2b == "no")
        sva = (q1a == "no" and q2a == "yes")
        svb = (q1b == "no" and q2b == "yes")
        labels.append({"id": iid, "q1_pA": q1a, "q2_pA": q2a, "q2_failing_pA": fa,
                       "q1_pB": q1b, "q2_pB": q2b, "q2_failing_pB": fb,
                       "decisive_pA": dec_a, "decisive_pB": dec_b, "dual_decisive": dd,
                       "necessity_violation_pA": nva, "necessity_violation_pB": nvb,
                       "sufficiency_violation_pA": sva, "sufficiency_violation_pB": svb,
                       "flags": sorted(set(aA[iid].get("flags", []) + aB[iid].get("flags", [])
                                           + bA[iid].get("flags", []) + bB[iid].get("flags", [])))})
        if dd:
            n_dual += 1
            if nva and nvb: nec["both"] += 1
            elif nva: nec["a"] += 1
            elif nvb: nec["b"] += 1
            else: nec["neither"] += 1
            if sva and svb: suf_conc += 1
            if sva or svb: suf_union += 1
            if nva: nec_a += 1
            if nvb: nec_b += 1
            if sva: suf_a += 1
            if svb: suf_b += 1
        # failing-cid histogram over BOTH judges' real pass-B 'no' answers
        for f in (fa if q2a == "no" and isinstance(fa, list) else []):
            hist[f] = hist.get(f, 0) + 1
        for f in (fb if q2b == "no" and isinstance(fb, list) else []):
            hist[f] = hist.get(f, 0) + 1

    labels.sort(key=lambda r: r["id"])
    lp = os.path.join(outdir, "labels-proxy.jsonl")
    with open(lp, "w", encoding="utf-8") as f:
        for r in labels:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")

    def cs(d, key):
        return sum(1 for r in d.values() if r.get(key) == "cannot-say")

    def nl(d, key):
        return sum(1 for r in d.values() if r.get(key) is None)

    probe_lab_a = sum(1 for r in aP.values() if r.get("q2") is not None)
    probe_lab_b = sum(1 for r in bP.values() if r.get("q2") is not None)
    probe_fs_a = sum(1 for r in aP.values() if r.get("q2") == "yes")
    probe_fs_b = sum(1 for r in bP.values() if r.get("q2") == "yes")

    metrics = {
        "n_instances": 200, "n_dual_decisive": n_dual,
        "n_nec_both": nec["both"], "n_nec_neither": nec["neither"],
        "n_nec_a_only": nec["a"], "n_nec_b_only": nec["b"],
        "n_necessity_concordant": nec["both"],
        "n_necessity_union": nec["both"] + nec["a"] + nec["b"],
        "n_sufficiency_concordant": suf_conc, "n_sufficiency_union": suf_union,
        "n_cannot_say_a1": cs(aA, "q1"), "n_cannot_say_a2": cs(aB, "q2"),
        "n_cannot_say_b1": cs(bA, "q1"), "n_cannot_say_b2": cs(bB, "q2"),
        "n_nolabel_a1": nl(aA, "q1"), "n_nolabel_a2": nl(aB, "q2"),
        "n_nolabel_b1": nl(bA, "q1"), "n_nolabel_b2": nl(bB, "q2"),
        "n_probe_labelled_a": probe_lab_a, "n_probe_false_sat_a": probe_fs_a,
        "n_probe_labelled_b": probe_lab_b, "n_probe_false_sat_b": probe_fs_b,
        "n_necessity_a": nec_a, "n_necessity_b": nec_b,
        "n_sufficiency_a": suf_a, "n_sufficiency_b": suf_b,
        "failing_cid_histogram": {k: hist[k] for k in sorted(hist)},
        "preflight_pass": bool(pf), "labels_sha256": file_sha(lp),
    }
    summary = dict(metrics)
    summary["_spec_sha256"] = file_sha(PATHS["poc/g3-llmproxy-v3/judge-invocation.md"])
    summary["_disclosure"] = (
        "STAND-IN, NOT THE ADJUDICATING STUDY: a cross-family blind LLM pair "
        "(judge-pA GPT-5.6-Sol, judge-pB Claude Haiku 4.5) fills the two-human "
        "g3.annotate GATE-H role. WEAK FEASIBILITY PROXY; the human-annotated g3 "
        "remains FROZEN, unconsumed, and the sole adjudicator of HS3 and the only "
        "trigger of HS2 auto-resolution / g5 pruning / Pi demotion.")
    with open(os.path.join(outdir, "summary.json"), "w") as f:
        f.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    # emit the final-record metrics JSON for log-append
    with open(os.path.join(run_dir, "final-record-metrics.json"), "w") as f:
        f.write(json.dumps(metrics, sort_keys=True) + "\n")
    print(json.dumps({"n_dual_decisive": n_dual,
                      "necessity_concordant": metrics["n_necessity_concordant"],
                      "necessity_union": metrics["n_necessity_union"],
                      "labels_sha256": metrics["labels_sha256"],
                      "preflight_pass": metrics["preflight_pass"]}, sort_keys=True))
    print("ASSEMBLE_DONE labels=%s summary=%s"
          % (lp, os.path.join(outdir, "summary.json")))


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            die("usage: preflight|pass|probe|assemble ...")
        mode = sys.argv[1]
        if mode == "preflight":
            phase_preflight(sys.argv[2], sys.argv[3])
        elif mode == "pass":
            phase_pass(sys.argv[2], sys.argv[3], sys.argv[4])
        elif mode == "probe":
            phase_probe(sys.argv[2], sys.argv[3])
        elif mode == "assemble":
            phase_assemble(sys.argv[2])
        else:
            die("unknown mode %r" % mode)
    except StopCap as e:
        sys.stderr.write("RUN_G3LP_STOPCAP: %s\n" % e)
        sys.exit(3)
    except AbortExperiment as e:
        sys.stderr.write("RUN_G3LP_BLINDING_ABORT: %s\n" % e)
        sys.exit(4)
