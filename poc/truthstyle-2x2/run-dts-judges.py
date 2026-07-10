#!/usr/bin/env python3
"""run-dts-judges -- MECHANICAL executor of the truthstyle-2x2 3-judge blind
adjudication, per the FROZEN pinned invocation spec
`poc/truthstyle-2x2/judges-invocation.md` (harness_manifest, ops amendment
seq 1) and the frozen record `registry/experiments/truthstyle-2x2.json`
(frozen_sha256 18893369...). Opus experiment-runner EXECUTION role: this
script DESIGNS NOTHING and CONCLUDES NOTHING. It is a faithful port of the
proven poc/f2b-transfer/llmproxy-runs/.../run-judge1p.py for the two codex
judges, plus the pinned headless `claude -p` path for judge-p3 (ASM-0240).
Any situation the spec does not decide is a HARD ABORT (report to Fable);
the runner never improvises.

Invocation:  run-dts-judges.py <p1|p2|p3> <preflight|main> <run_dir>
             run-dts-judges.py finalize <run_dir>

Determinism: stdlib only; seeded-sort idiom byte-identical to run-judge1p.py.
RT-14: pseudonymous judge ids only; no names/emails in any recorded bytes.
"""
import json, os, sys, hashlib, subprocess, time

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"

# ---- section-0 pinned inputs (fail-close on every one; ERR_DTS_PIN) ----
PINS = {
    "data/d-ts/items.jsonl": "9194f61713cc6cf01c34fa1ca97e01cd25b6b6d8c3bbae7db9a1772ac0c57a2d",
    "data/d-ts/manifest.json": "9fc7abbf25c871fb5ba66e18aa4e9c4c8dab1f339eb7be76749127341d88c600",
    "poc/truthstyle-2x2/build-dts.py": "1edb96f46e726c5a961b042810a0ebcfdfc3be9a44547f50bb75861ee19d2849",
    "poc/truthstyle-2x2/style-rules.json": "b65837d4a1915a85b7632391e1b368398c9c79f7e3490e585d781e7d3478c902",
    "analysis/truthstyle_2x2.py": "bf171ed951c2100e0a768c9ecea571da604e912a08164e2dd563e103f1c071c8",
    "poc/truthstyle-2x2/output-schema-dts.json": "90d17f640c970d233d6b4addf90f0f331637802d9a27f974bb8e5c4d94206a5d",
    "poc/truthstyle-2x2/judge-p3-system-prompt.txt": "21f090ae004e3745640c0a88fc820265a610628bb538a72a6d2ad8a425914db8",
}
ITEMS_PATH = os.path.join(REPO, "data/d-ts/items.jsonl")
SCHEMA_DTS = os.path.join(REPO, "poc/truthstyle-2x2/output-schema-dts.json")
P3_SYSPROMPT_PATH = os.path.join(REPO, "poc/truthstyle-2x2/judge-p3-system-prompt.txt")
SPEC_PATH = os.path.join(REPO, "poc/truthstyle-2x2/judges-invocation.md")

JUDGE_CFG = {
    "p1": {"id": "judge-p1-gpt56sol", "kind": "codex", "model": "gpt-5.6-sol",
           "seed": "dts/1|judge-p1|20260710"},
    "p2": {"id": "judge-p2-gpt55", "kind": "codex", "model": "gpt-5.5",
           "seed": "dts/1|judge-p2|20260710"},
    "p3": {"id": "judge-p3-haiku45", "kind": "claude", "model": "claude-haiku-4-5-20251001",
           "seed": "dts/1|judge-p3|20260710"},
}

EXPECT_CODEX_VER = "codex-cli 0.144.1"
EXPECT_GLOBAL_CODEX = "codex-cli 0.142.5"
EFFORT = "low"
NPX_CODEX = ["npx", "-y", "@openai/codex@0.144.1"]

# codex §7.1 banned event-type substrings (tool/command use => attempt INVALID)
BANNED_TYPE_SUBSTR = ["exec_command", "terminal_interaction", "unified_exec",
                      "tool_call", "web_search", "patch_apply", "view_image",
                      "image_generation", "collab_"]
TRANSPORT_TYPE_SUBSTR = ["stream_error", "rate_limit", "rate-limit"]

# §7.3 blinding audit tokens (case-insensitive)
BLIND_TOKENS = (b"kernel", b"nsm", b"truthstyle", b"f2b")

TRANSPORT_BACKOFF = [30, 60, 120, 300, 300, 300, 300, 300, 300, 300]  # §7.5
MAX_TRANSPORT = 10
MAX_CONTENT = 3
NOLABEL_ABORT = 40           # §7.5 run-level abort (>~5% of 808)
ALLOWED = ("yes", "no", "cannot-say")

# §8 calibration probes (byte-exact from the spec)
CAL = [
    {"id": "cal-1", "expected": "yes", "prompt":
     'Here is a proposed definition of the word "chair".\n\n'
     'definition: a seat for one person, with a support for the back\n\n'
     'Does this definition correctly give the meaning of the word "chair" as '
     'ordinarily understood? Answer with exactly one word: yes / no / cannot-say.'},
    {"id": "cal-2", "expected": "no", "prompt":
     'Here is a proposed definition of the word "dog".\n\n'
     'definition: a large gray animal with a very long nose called a trunk\n\n'
     'Does this definition correctly give the meaning of the word "dog" as '
     'ordinarily understood? Answer with exactly one word: yes / no / cannot-say.'},
]


def die(msg):
    sys.stderr.write("RUN_DTS_ABORT: %s\n" % msg)
    sys.exit(2)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def file_sha(path):
    with open(path, "rb") as f:
        return sha_bytes(f.read())


def norm_version(s):
    # accepts "2.1.201 (Claude Code)" and "codex-cli 0.144.1"
    return s.strip()


def claude_version_tuple(s):
    tok = s.strip().split()[0]
    try:
        return tuple(int(x) for x in tok.split("."))
    except Exception:
        return None


def verify_pins(kind):
    for rel, want in PINS.items():
        got = file_sha(os.path.join(REPO, rel))
        if got != want:
            die("ERR_DTS_PIN: %s sha %s != pinned %s" % (rel, got, want))
    if os.path.exists(os.path.expanduser("~/.claude/CLAUDE.md")):
        die("ERR_DTS_PIN: ~/.claude/CLAUDE.md exists (would inject context) — ABORT (spec §8)")
    banners = {}
    if kind == "codex":
        ver = subprocess.run(NPX_CODEX + ["--version"], capture_output=True, text=True).stdout.strip()
        if ver != EXPECT_CODEX_VER:
            die("ERR_DTS_PIN: npx codex version %r != %r (BOUNDARY STOP)" % (ver, EXPECT_CODEX_VER))
        gver = subprocess.run(["codex", "--version"], capture_output=True, text=True).stdout.strip()
        if gver != EXPECT_GLOBAL_CODEX:
            die("ERR_DTS_PIN: GLOBAL codex %r != %r (must not be upgraded)" % (gver, EXPECT_GLOBAL_CODEX))
        banners = {"npx_codex": ver, "global_codex": gver}
    else:
        cv = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
        vt = claude_version_tuple(cv)
        if vt is None or vt < (2, 1, 201):
            die("ERR_DTS_PIN: claude version %r < 2.1.201 (BOUNDARY STOP)" % cv)
        banners = {"claude": cv}
    return banners


def load_items():
    return [json.loads(l) for l in open(ITEMS_PATH, encoding="utf-8") if l.strip()]


def seeded_order(items, seed):
    return sorted(items, key=lambda it: sha_bytes(("%s|%s" % (seed, it["id"])).encode("utf-8")))


def normalize(raw):
    """§6 uniform normalization -> a token in ALLOWED, or None."""
    if raw is None or not isinstance(raw, str):
        return None
    s = raw.strip(" \t\n\r\f\v")          # 1. strip ASCII whitespace
    if s.endswith("."):                    # 2. strip AT MOST ONE trailing '.'
        s = s[:-1]
    s = "".join(chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in s)  # 3. ASCII lower
    if s == "cannot say":                  # 4. map
        s = "cannot-say"
    return s if s in ALLOWED else None     # 5. VALID iff in set


def blinding_scan(paths):
    for p in paths:
        if not os.path.exists(p):
            continue
        data = open(p, "rb").read().lower()
        for t in BLIND_TOKENS:
            if t in data:
                return (os.path.basename(p), t.decode())
    return None


def collect_types(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "type" and isinstance(v, str):
                out.append(v)
            collect_types(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_types(v, out)


# ----------------------------- codex path (§4.1/4.2) -----------------------------
def run_codex(model, prompt_text, attempt_dir, workdir):
    os.makedirs(attempt_dir, exist_ok=True)
    up = os.path.join(attempt_dir, "user-prompt.txt")
    with open(up, "w", encoding="utf-8") as f:
        f.write(prompt_text)                # question bytes verbatim, no added newline
    last_msg = os.path.join(attempt_dir, "last-message.json")
    events = os.path.join(attempt_dir, "events.jsonl")
    stderr = os.path.join(attempt_dir, "stderr.log")
    cmd = NPX_CODEX + ["exec",
                       "-m", model,
                       "-c", 'model_reasoning_effort="%s"' % EFFORT,
                       "-s", "read-only",
                       "--ignore-user-config",
                       "--skip-git-repo-check",
                       "--ephemeral",
                       "--disable", "memories",
                       "--disable", "standalone_web_search",
                       "-C", workdir,
                       "--color", "never",
                       "--json",
                       "--output-schema", SCHEMA_DTS,
                       "-o", last_msg,
                       "-"]
    with open(up, "rb") as fin, open(events, "wb") as fout, open(stderr, "wb") as ferr:
        p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=ferr)
    return p.returncode


def validate_codex(exit_code, attempt_dir):
    """returns (status, label_or_None, answer_raw_or_None, reason)
    status in {valid, content_invalid, transport}."""
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
    parsed = None
    if os.path.exists(last_msg):
        try:
            parsed = json.loads(open(last_msg, "rb").read().decode("utf-8"))
        except Exception:
            parsed = None
    if exit_code != 0:
        if parsed is None:
            return ("transport", None, None, "transport")
        return ("content_invalid", None, None, "parse_failure")
    if transport:
        return ("transport", None, None, "transport")
    if tool_use:
        return ("content_invalid", None, None, "tool_use_detected")
    if not (isinstance(parsed, dict) and list(parsed.keys()) == ["answer"]):
        return ("content_invalid", None, None, "parse_failure")
    ans_raw = parsed["answer"]
    label = normalize(ans_raw)
    if label is None:
        return ("content_invalid", None, ans_raw if isinstance(ans_raw, str) else None, "parse_failure")
    return ("valid", label, ans_raw, None)


# ----------------------------- claude path (§4.3) -----------------------------
def read_p3_sysprompt():
    return open(P3_SYSPROMPT_PATH, encoding="utf-8").read().rstrip("\n")  # $(cat) strips trailing \n


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
    cmd = ["claude", "-p",
           "--model", "claude-haiku-4-5-20251001",
           "--system-prompt", sys_prompt,
           "--tools", "",
           "--setting-sources", "",
           "--no-session-persistence",
           "--output-format", "stream-json", "--verbose"]
    with open(up, "rb") as fin, open(events, "wb") as fout, open(stderr, "wb") as ferr:
        p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=ferr, cwd=workdir, env=env)
    return p.returncode


def validate_claude(exit_code, attempt_dir):
    """returns (status, label, answer_raw, reason). status in
    {valid, content_invalid, transport, abort}. 'abort' => identity tripwire
    (§7.2) => ABORT the pass, not just the item."""
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
    # §7.2 identity tripwires -> ABORT the pass on mismatch
    mu = result.get("modelUsage") or {}
    if not (init and init.get("model") == "claude-haiku-4-5-20251001"
            and init.get("apiKeySource") == "none"
            and set(mu.keys()) == {"claude-haiku-4-5-20251001"}):
        return ("abort", None, None,
                "identity_mismatch(model=%r apiKeySource=%r modelUsage=%r)"
                % (init.get("model") if init else None,
                   init.get("apiKeySource") if init else None, sorted(mu.keys())))
    # §7.1 zero-tool tripwires -> content INVALID
    tools0 = init.get("tools") == []
    denials0 = (result.get("permission_denials") or []) == []
    turns1 = result.get("num_turns") == 1
    tooluse = "tool_use" in assistant_blocks
    if not (tools0 and denials0 and turns1) or tooluse:
        return ("content_invalid", None, None, "tool_use_detected")
    ans_raw = result.get("result")
    label = normalize(ans_raw)
    if label is None:
        return ("content_invalid", None, ans_raw if isinstance(ans_raw, str) else None, "parse_failure")
    return ("valid", label, ans_raw, None)


# ----------------------------- per-item driver -----------------------------
def do_attempt(cfg, prompt, attempt_dir, workdir, sys_prompt):
    if cfg["kind"] == "codex":
        rc = run_codex(cfg["model"], prompt, attempt_dir, workdir)
        status, label, raw, reason = validate_codex(rc, attempt_dir)
    else:
        rc = run_claude(prompt, attempt_dir, workdir, sys_prompt)
        status, label, raw, reason = validate_claude(rc, attempt_dir)
    # §7.3 blinding audit (fail-closed ABORT on any hit anywhere)
    hit = blinding_scan([os.path.join(attempt_dir, "user-prompt.txt"),
                         os.path.join(attempt_dir, "events.jsonl"),
                         os.path.join(attempt_dir, "stderr.log")])
    if hit:
        die("ERR_DTS_BLINDING: token %r in %s (spec §7.3) — ABORT to Fable" % (hit[1], hit[0]))
    return status, label, raw, reason


def process_item(cfg, question, position, base_dir, workdir, sys_prompt, log):
    n_content = 0
    n_transport = 0
    last_reason = None
    last_raw = None
    for content_k in range(1, MAX_CONTENT + 1):
        transport_tries = 0
        while True:
            call_dir = os.path.join(base_dir, "c%d_t%d" % (content_k, transport_tries))
            status, label, raw, reason = do_attempt(cfg, question, call_dir, workdir, sys_prompt)
            if status == "abort":
                die("ERR_DTS_IDENTITY: pos %s %s — ABORT the pass (spec §7.2)" % (position, reason))
            if status == "transport":
                n_transport += 1
                transport_tries += 1
                if n_transport > MAX_TRANSPORT:
                    die("ERR_DTS_TRANSPORT: pos %s exceeded %d transport retries; ABORT run"
                        % (position, MAX_TRANSPORT))
                back = TRANSPORT_BACKOFF[min(n_transport - 1, len(TRANSPORT_BACKOFF) - 1)]
                log("  pos %s transport failure (try %d), backoff %ds" % (position, n_transport, back))
                time.sleep(back)
                continue
            break
        n_content = content_k
        if status == "valid":
            return {"answer_raw": raw, "label": label, "flags": [],
                    "n_content_attempts": n_content, "n_transport_retries": n_transport,
                    "position": position}
        last_reason = reason
        last_raw = raw
        log("  pos %s content attempt %d INVALID (%s)" % (position, content_k, reason))
    return {"answer_raw": last_raw, "label": None,
            "flags": ["judge_no_label", last_reason or "parse_failure"],
            "n_content_attempts": n_content, "n_transport_retries": n_transport,
            "position": position}


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


# ----------------------------- phases -----------------------------
def phase_preflight(pkey, run_dir):
    cfg = JUDGE_CFG[pkey]
    banners = verify_pins(cfg["kind"])
    workdir = make_workdir(pkey)
    sys_prompt = read_p3_sysprompt() if cfg["kind"] == "claude" else None
    pf_dir = os.path.join(run_dir, cfg["id"], "preflight")
    os.makedirs(pf_dir, exist_ok=True)
    with open(os.path.join(run_dir, cfg["id"], "workdir-path.txt"), "w") as f:
        f.write(workdir + "\n")
    results = []
    ok = True
    for c in CAL:
        call_dir = os.path.join(pf_dir, c["id"])
        status, label, raw, reason = do_attempt(cfg, c["prompt"], call_dir, workdir, sys_prompt)
        item_ok = (status == "valid") and (label == c["expected"])
        results.append({"id": c["id"], "status": status, "label": label,
                        "expected": c["expected"], "reason": reason, "pass": item_ok})
        if not item_ok:
            ok = False
    status_obj = {"phase": "preflight", "judge": cfg["id"], "banners": banners,
                  "workdir": workdir, "pass": ok, "results": results}
    with open(os.path.join(run_dir, "preflight-status-%s.json" % pkey), "w") as f:
        f.write(json.dumps(status_obj, indent=2, sort_keys=True) + "\n")
    print("PREFLIGHT %s %s: %s" % (pkey, cfg["id"], "PASS" if ok else "FAIL"), flush=True)
    for r in results:
        print("  %s status=%s label=%r expected=%r => %s"
              % (r["id"], r["status"], r["label"], r["expected"], "PASS" if r["pass"] else "FAIL"),
              flush=True)
    if not ok:
        die("preflight FAILED for %s; not running any real item (spec §8)" % pkey)


def phase_main(pkey, run_dir):
    cfg = JUDGE_CFG[pkey]
    banners = verify_pins(cfg["kind"])
    ps_path = os.path.join(run_dir, "preflight-status-%s.json" % pkey)
    if not os.path.exists(ps_path):
        die("no preflight-status-%s.json; run preflight first" % pkey)
    ps = json.load(open(ps_path))
    if not ps.get("pass"):
        die("preflight %s did not PASS; refusing main" % pkey)
    workdir = open(os.path.join(run_dir, cfg["id"], "workdir-path.txt")).read().strip()
    if not os.path.isdir(workdir):
        die("recorded workdir missing: %s" % workdir)
    sys_prompt = read_p3_sysprompt() if cfg["kind"] == "claude" else None

    items = load_items()
    if len(items) != 808:
        die("expected 808 items, got %d" % len(items))
    ordered = seeded_order(items, cfg["seed"])
    jdir = os.path.join(run_dir, cfg["id"])
    os.makedirs(jdir, exist_ok=True)
    with open(os.path.join(jdir, "%s-position-map.jsonl" % cfg["id"]), "w", encoding="utf-8") as f:
        for i, it in enumerate(ordered, 1):
            f.write(json.dumps({"position": i, "id": it["id"]}, sort_keys=True, ensure_ascii=False) + "\n")

    items_dir = os.path.join(jdir, "items")
    os.makedirs(items_dir, exist_ok=True)
    logf = open(os.path.join(jdir, "main-progress.log"), "a")

    def log(m):
        logf.write(m + "\n")
        logf.flush()

    t0 = time.time()
    log("MAIN %s start ts=%s banners=%s workdir=%s n=%d"
        % (cfg["id"], time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           json.dumps(banners, sort_keys=True), workdir, len(ordered)))
    responses = []
    n_nolabel = 0
    total_transport = 0
    for i, it in enumerate(ordered, 1):
        base_dir = os.path.join(items_dir, "pos-%03d" % i)
        os.makedirs(base_dir, exist_ok=True)
        # user-prompt.txt is written from it["question"] bytes verbatim (§7.3);
        # the blinding audit in do_attempt re-reads and greps it every attempt.
        r = process_item(cfg, it["question"], i, base_dir, workdir, sys_prompt, log)
        r["id"] = it["id"]
        r["judge"] = cfg["id"]
        responses.append(r)
        total_transport += r["n_transport_retries"]
        if r["label"] is None:
            n_nolabel += 1
        if i % 20 == 0 or i == len(ordered):
            log("  %d/%d nolabel=%d transport=%d elapsed=%.0fs"
                % (i, len(ordered), n_nolabel, total_transport, time.time() - t0))
        if n_nolabel > NOLABEL_ABORT:
            die("ERR_DTS_NOLABEL: %d no-label > %d for %s; degenerate pass, ABORT"
                % (n_nolabel, NOLABEL_ABORT, cfg["id"]))

    # re-check version banners after the pass (§4.3 / runner constraint)
    banners_after = verify_pins(cfg["kind"])
    if banners_after != banners:
        die("ERR_DTS_PIN: version banner drift during %s pass: %s -> %s"
            % (cfg["id"], banners, banners_after))

    responses_sorted = sorted(responses, key=lambda r: r["id"])
    resp_path = os.path.join(REPO, "data/d-ts-labels", "%s-responses.jsonl" % cfg["id"])
    os.makedirs(os.path.dirname(resp_path), exist_ok=True)
    fields = ["id", "answer_raw", "label", "flags", "n_content_attempts",
              "n_transport_retries", "position", "judge"]
    with open(resp_path, "w", encoding="utf-8") as f:
        for r in responses_sorted:
            f.write(json.dumps({k: r[k] for k in fields}, sort_keys=True, ensure_ascii=False) + "\n")

    def counts_of(rs):
        c = {}
        for r in rs:
            k = "null" if r["label"] is None else r["label"]
            c[k] = c.get(k, 0) + 1
        return c

    frag = {"judge": cfg["id"], "kind": cfg["kind"], "model": cfg["model"],
            "seed": cfg["seed"], "banners": banners, "workdir": workdir,
            "n_items": len(responses_sorted), "n_nolabel": n_nolabel,
            "n_labelled": len(responses_sorted) - n_nolabel,
            "total_transport_retries": total_transport,
            "label_counts": counts_of(responses_sorted),
            "responses_path": os.path.relpath(resp_path, REPO),
            "responses_sha256": file_sha(resp_path),
            "elapsed_seconds": round(time.time() - t0, 1),
            "preflight_pass": True}
    with open(os.path.join(run_dir, "run-summary-%s.json" % pkey), "w") as f:
        f.write(json.dumps(frag, indent=2, sort_keys=True) + "\n")
    log("MAIN %s done nolabel=%d transport=%d counts=%s"
        % (cfg["id"], n_nolabel, total_transport, json.dumps(counts_of(responses_sorted), sort_keys=True)))
    print("MAIN_DONE %s counts=%s nolabel=%d"
          % (pkey, json.dumps(counts_of(responses_sorted), sort_keys=True), n_nolabel), flush=True)


def phase_finalize(run_dir):
    """Merge the 3 per-judge responses -> data/d-ts-labels/labels.jsonl (valid
    labels only, sorted by (judge,item_id)) + summary.json (spec §10)."""
    frags = {}
    for pkey, cfg in JUDGE_CFG.items():
        fp = os.path.join(run_dir, "run-summary-%s.json" % pkey)
        if not os.path.exists(fp):
            die("missing run-summary-%s.json — finalize before all 3 passes done" % pkey)
        frags[cfg["id"]] = json.load(open(fp))
    labels = []
    for pkey, cfg in JUDGE_CFG.items():
        rp = os.path.join(REPO, "data/d-ts-labels", "%s-responses.jsonl" % cfg["id"])
        for l in open(rp, encoding="utf-8"):
            if not l.strip():
                continue
            r = json.loads(l)
            if r["label"] is not None:
                labels.append({"item_id": r["id"], "judge": cfg["id"], "label": r["label"]})
    labels.sort(key=lambda r: (r["judge"], r["item_id"]))
    labels_path = os.path.join(REPO, "data/d-ts-labels/labels.jsonl")
    with open(labels_path, "w", encoding="utf-8") as f:
        for r in labels:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")

    summary = {
        "experiment": "truthstyle-2x2",
        "spec_sha256": file_sha(SPEC_PATH),
        "judges": {jid: {k: frags[jid][k] for k in
                         ("kind", "model", "seed", "banners", "workdir", "n_items",
                          "n_labelled", "n_nolabel", "total_transport_retries",
                          "label_counts", "elapsed_seconds", "responses_sha256")}
                   for jid in frags},
        "n_labels_total": len(labels),
        "labels_path": "data/d-ts-labels/labels.jsonl",
        "labels_sha256": file_sha(labels_path),
        "judge_sourcing_disclosure":
            "judge-p3-haiku45 = Claude Haiku 4.5 (claude-haiku-4-5-20251001) via a "
            "headless tool-less single-shot Claude Code sub-process (claude -p), "
            "subscription auth, NO Anthropic API key; two of three judges are the "
            "same vendor as the design family (FORK-2 caveat, disclosed).",
    }
    with open(os.path.join(REPO, "data/d-ts-labels/summary.json"), "w") as f:
        f.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print("FINALIZE_DONE n_labels=%d labels_sha=%s" % (len(labels), summary["labels_sha256"]), flush=True)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "finalize":
        if len(sys.argv) != 3:
            die("usage: run-dts-judges.py finalize <run_dir>")
        phase_finalize(sys.argv[2])
        sys.exit(0)
    if len(sys.argv) != 4 or sys.argv[1] not in JUDGE_CFG or sys.argv[2] not in ("preflight", "main"):
        die("usage: run-dts-judges.py <p1|p2|p3> <preflight|main> <run_dir>  |  finalize <run_dir>")
    pkey, phase, run_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(run_dir, exist_ok=True)
    if phase == "preflight":
        phase_preflight(pkey, run_dir)
    else:
        phase_main(pkey, run_dir)
