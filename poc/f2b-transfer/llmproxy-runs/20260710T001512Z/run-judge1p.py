#!/usr/bin/env python3
"""run-judge1p -- MECHANICAL executor of the f2b-transfer-llmproxy Stage-1
judge-1p (GPT-5.6-Sol via npx-pinned codex CLI 0.144.1) adjudication STAND-IN,
per the FROZEN pinned spec `data/d-adj-t-llmproxy/judge-1p-invocation.md`
(sha 4e487159a95493eafff0374c84f3bf6393836c4781b6f60e003966f734450f34) and the
frozen record `registry/experiments/f2b-transfer-llmproxy.json`.

Opus experiment-runner EXECUTION role: this script DESIGNS NOTHING and
CONCLUDES NOTHING. It is a faithful port of the proven
`poc/f2b-transfer/opus-runs/20260709T232652Z/run-judge2.py` with EXACTLY the
frozen judge-1p deltas: npx-pinned `@openai/codex@0.144.1`, model
`gpt-5.6-sol`, the judge-1p prompt template, the judge-1 ROLE shuffle seed for
the 360 real items, a trailing 60-probe block in its own pinned shuffle,
pseudonym `judge-1p`, and NO judge-3 routing. Any situation the spec does not
decide is a HARD ABORT (report to Fable); the runner never improvises.

Phases (argv[1]):  preflight | main
  preflight : pins + workdir + 2 calibration items (spec section 7). Writes
              preflight-status.json (PASS/FAIL). Exit !=0 on FAIL.
  main      : re-verify pins + require preflight PASS + real 360 items in the
              judge-1 role order -> 60 probes in probe order -> response files.

Determinism: stdlib only; seeded-sort idiom byte-identical to run-judge2.py.
RT-14: pseudonym "judge-1p" only; no names/emails in any recorded bytes.
"""
import json, os, sys, hashlib, subprocess, time

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
RUN_TS = "20260710T001512Z"
RUN_DIR = os.path.join(REPO, "poc/f2b-transfer/llmproxy-runs", RUN_TS)

# ---- section-0 pinned inputs (runner fail-closes on every one; ERR_JUDGE1P_PIN) ----
PINS = {
    os.path.join(REPO, "poc/f2b-transfer/opus-runs/20260709T171156Z/blind-items-by-id.jsonl"):
        "ce820483336e6e25c607fa72e2591022f192d9e0eddc9a6689e02b4796af42cc",
    os.path.join(REPO, "data/d-adj-t-llmproxy/deranged-probe.jsonl"):
        "4479c6192c1830ef5eb3b75f564efef2114e369f5125786e95e9e79f27687e9c",
    os.path.join(REPO, "data/d-adj-t-llmproxy/deranged-probe-manifest.json"):
        "ff5d7c1f603c4981187aa52cea196ab95c154c2fcb5a5058fc04b7a34e6b343f",
    os.path.join(REPO, "data/d-adj-t-llmproxy/judge-1p-prompt-template.txt"):
        "19b029991f1dc0cb031192db45f397c3a171ec701488817f181827c0101d2d1e",
    os.path.join(REPO, "data/d-adj-t/judge-2-output-schema-mcq.json"):
        "1445fd021780dc54ec0c1cf94f5d70318f203ebe4ce8e2e4ad1a4d8a192deb38",
    os.path.join(REPO, "data/d-adj-t/judge-2-output-schema-claim.json"):
        "3af3eaed608b712178aa4d2a627ddda7c42048f0ebef0c79600b4bee91494727",
    os.path.join(REPO, "data/d-adj-t/judge-2-calibration.jsonl"):
        "8bdb22dac8380ff834889f83b5f9bc0b9733e6446e895963cf0e084a8cffb9a1",
}
ITEMS_PATH   = os.path.join(REPO, "poc/f2b-transfer/opus-runs/20260709T171156Z/blind-items-by-id.jsonl")
PROBE_PATH   = os.path.join(REPO, "data/d-adj-t-llmproxy/deranged-probe.jsonl")
PROBE_MANIFEST = os.path.join(REPO, "data/d-adj-t-llmproxy/deranged-probe-manifest.json")
TEMPLATE     = os.path.join(REPO, "data/d-adj-t-llmproxy/judge-1p-prompt-template.txt")
SCHEMA_MCQ   = os.path.join(REPO, "data/d-adj-t/judge-2-output-schema-mcq.json")
SCHEMA_CLAIM = os.path.join(REPO, "data/d-adj-t/judge-2-output-schema-claim.json")
CALIB_PATH   = os.path.join(REPO, "data/d-adj-t/judge-2-calibration.jsonl")
INVOCATION_SPEC = os.path.join(REPO, "data/d-adj-t-llmproxy/judge-1p-invocation.md")

JUDGE = "judge-1p"
JUDGE_SEED = "dadjt/1|judge-1|20260710"           # judge-1 ROLE shuffle (spec section 2), pinned verbatim
PROBE_SEED = "dadjt/1|judge-1p-probe|20260711"    # probe shuffle (spec section 2), pinned verbatim
EXPECT_N = 360
EXPECT_PROBE_N = 60
EXPECT_CODEX_VER = "codex-cli 0.144.1"
MODEL = "gpt-5.6-sol"
EFFORT = "low"
NPX_CODEX = ["npx", "-y", "@openai/codex@0.144.1"]  # pinned invocation section 3

# section-5 banned event-type substrings (tool/command use => attempt INVALID, E5 tripwire)
BANNED_TYPE_SUBSTR = ["exec_command", "terminal_interaction", "unified_exec",
                      "tool_call", "web_search", "patch_apply", "view_image",
                      "image_generation", "collab_"]
TRANSPORT_TYPE_SUBSTR = ["stream_error", "rate_limit", "rate-limit"]

TRANSPORT_BACKOFF = [30, 60, 120, 300, 300, 300, 300, 300, 300, 300]  # section 5, up to 10
MAX_TRANSPORT = 10
MAX_CONTENT = 3            # section 6
NOLABEL_ABORT = 18        # section 6 run-level abort (>5% of 360 real items)
PROBE_NOLABEL_ABORT = 6   # section 6 run-level abort (>6 probe no-labels)

ALLOWED_MCQ = ["A", "B", "C", "D", "NONE"]
ALLOWED_CLAIM = ["yes", "no", "cannot say"]


def die(msg):
    sys.stderr.write("RUN_JUDGE1P_ABORT: %s\n" % msg)
    sys.exit(2)


def sha256_hex_bytes(b):
    return hashlib.sha256(b).hexdigest()


def file_sha(path):
    with open(path, "rb") as f:
        return sha256_hex_bytes(f.read())


def verify_pins():
    for path, want in PINS.items():
        got = file_sha(path)
        if got != want:
            die("ERR_JUDGE1P_PIN: %s sha %s != pinned %s" % (path, got, want))
    ver = subprocess.run(NPX_CODEX + ["--version"], capture_output=True, text=True).stdout.strip()
    if ver != EXPECT_CODEX_VER:
        die("ERR_JUDGE1P_PIN: codex version %r != %r (BOUNDARY STOP)" % (ver, EXPECT_CODEX_VER))
    # global codex MUST remain 0.142.5 (operational constraint; judge-2 in flight)
    gver = subprocess.run(["codex", "--version"], capture_output=True, text=True).stdout.strip()
    if gver != "codex-cli 0.142.5":
        die("ERR_JUDGE1P_PIN: GLOBAL codex is %r != 'codex-cli 0.142.5' (must not be upgraded)" % gver)
    return ver


def load_jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def seeded_order(items, seed):
    """Canonical seeded sort: ascending by sha256_hex(seed | '|' | id)."""
    return sorted(items, key=lambda it: sha256_hex_bytes(
        ("%s|%s" % (seed, it["id"])).encode("utf-8")))


def item_rendering(it):
    """Byte-exact blind rendering (no trailing newline); spec section 1."""
    q = it["question"]
    if it["format"] == "mcq":
        opt = {o["key"]: o["text"] for o in it["options"]}
        lines = [q, ""]
        for k in ("A", "B", "C", "D"):
            lines.append("- %s) %s" % (k, opt[k]))
        lines.append("- NONE) none of these / cannot say")
        lines.append("")
        lines.append('Allowed answers: "A", "B", "C", "D", "NONE".')
        return "\n".join(lines)
    elif it["format"] == "claim-yes-no":
        return "\n".join([q, "", 'Allowed answers: "yes", "no", "cannot say".'])
    die("ERR_JUDGE1P_PIN: unknown format %r for id %s" % (it.get("format"), it.get("id")))


def build_prompt(template_bytes, it):
    if template_bytes.count("{{ITEM}}") != 1:
        die("ERR_JUDGE1P_PIN: template placeholder count != 1")
    return template_bytes.replace("{{ITEM}}", item_rendering(it))


def fmt_key(it):
    return "mcq" if it["format"] == "mcq" else "claim"


def allowed_set(it):
    return ALLOWED_MCQ if it["format"] == "mcq" else ALLOWED_CLAIM


def collect_types(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "type" and isinstance(v, str):
                out.append(v)
            collect_types(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_types(v, out)


def scan_events(events_path):
    types = []
    tokens = None
    if not os.path.exists(events_path):
        return types, False, False, tokens
    for line in open(events_path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        t = []
        collect_types(ev, t)
        types.extend(t)
        et = " ".join(t)
        if "token_count" in et or "token_usage" in et:
            tokens = ev
    tool_use = any(any(b in t for b in BANNED_TYPE_SUBSTR) for t in types)
    transport = any(any(b in t for b in TRANSPORT_TYPE_SUBSTR) for t in types)
    return types, tool_use, transport, tokens


def run_codex(prompt_text, fmt, attempt_dir, workdir):
    """One pinned section-3 codex invocation (npx-pinned 0.144.1). Returns exit code."""
    os.makedirs(attempt_dir, exist_ok=True)
    up = os.path.join(attempt_dir, "user-prompt.txt")
    with open(up, "w", encoding="utf-8") as f:
        f.write(prompt_text)
    schema = SCHEMA_MCQ if fmt == "mcq" else SCHEMA_CLAIM
    last_msg = os.path.join(attempt_dir, "last-message.json")
    events = os.path.join(attempt_dir, "events.jsonl")
    stderr = os.path.join(attempt_dir, "stderr.log")
    cmd = NPX_CODEX + ["exec",
           "-m", MODEL,
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
           "--output-schema", schema,
           "-o", last_msg,
           "-"]
    with open(up, "rb") as fin, open(events, "wb") as fout, open(stderr, "wb") as ferr:
        p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=ferr)
    return p.returncode


def validate_attempt(exit_code, attempt_dir, allowed):
    """section-5 validity. Returns (valid, answer, reason, lm_sha, tool_use, transport)."""
    last_msg = os.path.join(attempt_dir, "last-message.json")
    events = os.path.join(attempt_dir, "events.jsonl")
    _types, tool_use, transport, _tok = scan_events(events)
    parsed = None
    lm_sha = None
    if os.path.exists(last_msg):
        try:
            with open(last_msg, "rb") as f:
                raw = f.read()
            lm_sha = sha256_hex_bytes(raw)
            parsed = json.loads(raw.decode("utf-8"))
        except Exception:
            parsed = None
    if exit_code != 0:
        if parsed is None:
            return False, None, "transport", None, tool_use, True
        return False, None, "parse_failure", lm_sha, tool_use, transport
    if tool_use:
        return False, None, "tool_use_detected", lm_sha, True, transport
    if not (isinstance(parsed, dict) and list(parsed.keys()) == ["answer"]):
        reason = "refusal" if parsed is None else "parse_failure"
        return False, None, reason, lm_sha, tool_use, transport
    ans = parsed["answer"]
    if not (isinstance(ans, str) and ans in allowed):
        return False, None, "parse_failure", lm_sha, tool_use, transport
    return True, ans, None, lm_sha, tool_use, transport


def process_item(it, position, base_dir, workdir, template_bytes, log):
    """section 1-6 for one item. position may be an int (real) or 'pNN' (probe)."""
    allowed = allowed_set(it)
    fmt = fmt_key(it)
    prompt = build_prompt(template_bytes, it)
    n_content = 0
    n_transport = 0
    last_reason = None
    for content_k in range(1, MAX_CONTENT + 1):
        transport_tries = 0
        while True:
            call_dir = os.path.join(base_dir, "c%d_t%d" % (content_k, transport_tries))
            exit_code = run_codex(prompt, fmt, call_dir, workdir)
            valid, ans, reason, lm_sha, tool_use, transport = validate_attempt(
                exit_code, call_dir, allowed)
            if reason == "transport" or transport:
                n_transport += 1
                transport_tries += 1
                if n_transport > MAX_TRANSPORT:
                    die("ERR_TRANSPORT: item pos %s exceeded %d transport retries; "
                        "infra problem, aborting run" % (position, MAX_TRANSPORT))
                back = TRANSPORT_BACKOFF[min(n_transport - 1, len(TRANSPORT_BACKOFF) - 1)]
                log("  pos %s transport failure (try %d), backoff %ds" % (position, n_transport, back))
                time.sleep(back)
                continue
            break
        n_content = content_k
        if valid:
            return {"answer": ans, "flags": [], "format": it["format"],
                    "id": it["id"], "judge": JUDGE, "last_message_sha256": lm_sha,
                    "n_content_attempts": n_content, "n_transport_retries": n_transport,
                    "position": position}
        last_reason = reason
        log("  pos %s content attempt %d INVALID (%s)" % (position, content_k, reason))
    return {"answer": None, "flags": ["judge1p_no_label", last_reason or "parse_failure"],
            "format": it["format"], "id": it["id"], "judge": JUDGE,
            "last_message_sha256": None, "n_content_attempts": n_content,
            "n_transport_retries": n_transport, "position": position}


def make_workdir():
    """section 3 fresh empty dir OUTSIDE any git repo (pinned mktemp template)."""
    out = subprocess.run(["mktemp", "-d", "/tmp/judge1p-workdir.XXXXXX"],
                         capture_output=True, text=True)
    wd = out.stdout.strip()
    if not wd or not os.path.isdir(wd):
        die("ERR_WORKDIR: mktemp failed")
    if os.listdir(wd):
        die("ERR_WORKDIR: workdir not empty: %s" % wd)
    chk = subprocess.run(["git", "-C", wd, "rev-parse", "--is-inside-work-tree"],
                         capture_output=True, text=True)
    if chk.stdout.strip() == "true":
        die("ERR_WORKDIR: %s is inside a git repo" % wd)
    return wd


def phase_preflight():
    ver = verify_pins()
    workdir = make_workdir()
    with open(os.path.join(RUN_DIR, "workdir-path.txt"), "w") as f:
        f.write(workdir + "\n")
    template_bytes = open(TEMPLATE, encoding="utf-8").read()
    calib = load_jsonl(CALIB_PATH)
    pf_dir = os.path.join(RUN_DIR, "preflight")
    os.makedirs(pf_dir, exist_ok=True)
    logf = open(os.path.join(RUN_DIR, "preflight-log.txt"), "w")
    def log(m):
        logf.write(m + "\n"); logf.flush(); print(m, flush=True)
    log("PREFLIGHT start; codex=%s (npx-pinned) workdir=%s" % (ver, workdir))
    results = []
    ok = True
    for i, it in enumerate(calib, 1):
        allowed = allowed_set(it)
        fmt = fmt_key(it)
        prompt = build_prompt(template_bytes, it)
        call_dir = os.path.join(pf_dir, "cal%d" % i)
        exit_code = run_codex(prompt, fmt, call_dir, workdir)
        valid, ans, reason, lm_sha, tool_use, transport = validate_attempt(exit_code, call_dir, allowed)
        exp = it.get("expected")
        item_ok = bool(valid) and (ans == exp)
        results.append({"id": it["id"], "valid_first_attempt": valid, "answer": ans,
                        "expected": exp, "reason": reason, "pass": item_ok})
        log("  %s: valid=%s answer=%r expected=%r reason=%s => %s"
            % (it["id"], valid, ans, exp, reason, "PASS" if item_ok else "FAIL"))
        if not item_ok:
            ok = False
    status = {"phase": "preflight", "codex_version": ver, "workdir": workdir,
              "pass": ok, "results": results}
    with open(os.path.join(RUN_DIR, "preflight-status.json"), "w") as f:
        f.write(json.dumps(status, indent=2, sort_keys=True) + "\n")
    log("PREFLIGHT %s" % ("PASS" if ok else "FAIL"))
    logf.close()
    if not ok:
        die("preflight FAILED; not running any real item (spec section 7)")
    print("PREFLIGHT_PASS", flush=True)


def phase_main():
    ver = verify_pins()
    ps_path = os.path.join(RUN_DIR, "preflight-status.json")
    if not os.path.exists(ps_path):
        die("no preflight-status.json; run preflight first (spec section 7)")
    ps = json.load(open(ps_path))
    if not ps.get("pass"):
        die("preflight did not PASS; refusing main run")
    workdir = open(os.path.join(RUN_DIR, "workdir-path.txt")).read().strip()
    if not os.path.isdir(workdir):
        die("recorded workdir missing: %s" % workdir)

    template_bytes = open(TEMPLATE, encoding="utf-8").read()
    items = load_jsonl(ITEMS_PATH)
    if len(items) != EXPECT_N:
        die("expected %d real items, got %d" % (EXPECT_N, len(items)))
    probes = load_jsonl(PROBE_PATH)
    if len(probes) != EXPECT_PROBE_N:
        die("expected %d probes, got %d" % (EXPECT_PROBE_N, len(probes)))

    # real items in the judge-1 ROLE order (spec section 2)
    ordered = seeded_order(items, JUDGE_SEED)
    # probes in the probe order (spec section 2); cross-check against manifest run_position (fail closed)
    probe_ordered = seeded_order(probes, PROBE_SEED)
    manifest = json.load(open(PROBE_MANIFEST))
    man_pos = {r["probe_id"]: r["run_position"] for r in manifest["rows"]}
    for n, it in enumerate(probe_ordered, 1):
        if man_pos.get(it["id"]) != n:
            die("ERR_JUDGE1P_PIN: probe order mismatch for %s: computed %d != manifest %r"
                % (it["id"], n, man_pos.get(it["id"])))

    # position maps -> provenance (probe positions prefixed 'p')
    pos_map = [{"position": i, "id": it["id"]} for i, it in enumerate(ordered, 1)]
    pos_map += [{"position": "p%d" % i, "id": it["id"]} for i, it in enumerate(probe_ordered, 1)]
    with open(os.path.join(RUN_DIR, "judge-1p-position-map.jsonl"), "w", encoding="utf-8") as f:
        for r in pos_map:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")

    items_dir = os.path.join(RUN_DIR, "items")
    os.makedirs(items_dir, exist_ok=True)
    logf = open(os.path.join(RUN_DIR, "main-progress.log"), "a")
    def log(m):
        logf.write(m + "\n"); logf.flush()
    log("MAIN start ts=%s codex=%s workdir=%s n_real=%d n_probe=%d"
        % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), ver, workdir, len(ordered), len(probe_ordered)))

    t0 = time.time()
    # ---- real items ----
    responses = []
    n_nolabel = 0
    total_transport = 0
    for i, it in enumerate(ordered, 1):
        base_dir = os.path.join(items_dir, "pos-%03d" % i)
        os.makedirs(base_dir, exist_ok=True)
        r = process_item(it, i, base_dir, workdir, template_bytes, log)
        responses.append(r)
        total_transport += r["n_transport_retries"]
        if r["answer"] is None:
            n_nolabel += 1
        if i % 10 == 0 or i == len(ordered):
            log("  real %d/%d  nolabel=%d transport=%d  elapsed=%.0fs"
                % (i, len(ordered), n_nolabel, total_transport, time.time() - t0))
        if n_nolabel > NOLABEL_ABORT:
            die("ERR_NOLABEL: %d real no-label items > %d; judge instrument failing, aborting"
                % (n_nolabel, NOLABEL_ABORT))

    responses_sorted = sorted(responses, key=lambda r: r["id"])
    out_path = os.path.join(REPO, "data/d-adj-t-llmproxy/judge-1p-responses.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for r in responses_sorted:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")

    # ---- probes (own block; a probe failure never disturbs the real-item run) ----
    probe_responses = []
    n_probe_nolabel = 0
    for i, it in enumerate(probe_ordered, 1):
        base_dir = os.path.join(items_dir, "probe-p%02d" % i)
        os.makedirs(base_dir, exist_ok=True)
        r = process_item(it, "p%d" % i, base_dir, workdir, template_bytes, log)
        probe_responses.append(r)
        total_transport += r["n_transport_retries"]
        if r["answer"] is None:
            n_probe_nolabel += 1
        if i % 10 == 0 or i == len(probe_ordered):
            log("  probe %d/%d  nolabel=%d transport=%d  elapsed=%.0fs"
                % (i, len(probe_ordered), n_probe_nolabel, total_transport, time.time() - t0))
        if n_probe_nolabel > PROBE_NOLABEL_ABORT:
            die("ERR_NOLABEL: %d probe no-label items > %d; aborting"
                % (n_probe_nolabel, PROBE_NOLABEL_ABORT))

    probe_sorted = sorted(probe_responses, key=lambda r: r["id"])
    probe_out = os.path.join(REPO, "data/d-adj-t-llmproxy/judge-1p-probe-responses.jsonl")
    with open(probe_out, "w", encoding="utf-8") as f:
        for r in probe_sorted:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")

    def counts_of(rs):
        c = {}
        for r in rs:
            k = "null" if r["answer"] is None else r["answer"]
            c[k] = c.get(k, 0) + 1
        return c

    summary = {"run_ts": RUN_TS, "judge": JUDGE, "model": MODEL,
               "codex_version": ver, "codex_source": "npx -y @openai/codex@0.144.1",
               "reasoning_effort": EFFORT,
               "n_real_items": len(responses_sorted),
               "n_real_nolabel": n_nolabel,
               "n_probe_items": len(probe_sorted),
               "n_probe_nolabel": n_probe_nolabel,
               "total_transport_retries": total_transport,
               "real_label_counts": counts_of(responses_sorted),
               "probe_label_counts": counts_of(probe_sorted),
               "responses_path": "data/d-adj-t-llmproxy/judge-1p-responses.jsonl",
               "responses_sha256": file_sha(out_path),
               "probe_responses_path": "data/d-adj-t-llmproxy/judge-1p-probe-responses.jsonl",
               "probe_responses_sha256": file_sha(probe_out),
               "invocation_spec_sha256": file_sha(INVOCATION_SPEC),
               "preflight_pass": bool(ps.get("pass")),
               "elapsed_seconds": round(time.time() - t0, 1)}
    with open(os.path.join(RUN_DIR, "run-summary.json"), "w") as f:
        f.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    log("MAIN done real_nolabel=%d probe_nolabel=%d transport=%d real=%s probe=%s"
        % (n_nolabel, n_probe_nolabel, total_transport,
           json.dumps(counts_of(responses_sorted), sort_keys=True),
           json.dumps(counts_of(probe_sorted), sort_keys=True)))
    print("MAIN_DONE real=%s probe=%s"
          % (json.dumps(counts_of(responses_sorted), sort_keys=True),
             json.dumps(counts_of(probe_sorted), sort_keys=True)), flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("preflight", "main"):
        die("usage: run-judge1p.py preflight|main")
    if sys.argv[1] == "preflight":
        phase_preflight()
    else:
        phase_main()
