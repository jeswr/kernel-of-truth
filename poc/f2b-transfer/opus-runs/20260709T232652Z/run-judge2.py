#!/usr/bin/env python3
"""run-judge2 — MECHANICAL executor of the f2b-transfer Stage-1 judge-2
(GPT-5.5 via codex CLI) adjudication, per the FROZEN pinned spec
`data/d-adj-t/judge-2-invocation.md` (§0-§9). Opus experiment-runner EXECUTION
role: this script DESIGNS NOTHING and CONCLUDES NOTHING. It fail-closes on every
§0 pin, runs the pinned per-item codex invocation, enforces §5 attempt validity
+ §6 retry/no-label, and writes judge-2's raw response file + provenance.

Nothing here amends the frozen record or the invocation spec; it operationalises
them byte-for-byte. Any situation the spec does not decide is a HARD ABORT (the
runner reports to Fable; it never improvises).

Phases (argv[1]):  preflight | main
  preflight : §0 pins + workdir + §7 two calibration items. Writes
              preflight-status.json (PASS/FAIL). Exit !=0 on FAIL.
  main      : re-verify §0 pins + require preflight PASS + §2 position map +
              §1-§6 over the 360 real items + §8 response file + summary.

Determinism: stdlib only; ordering is sha256 over the pinned judge seed + id
(repo canonical seeded-sort idiom, identical to build-judge1-package.py).
RT-14: pseudonym "judge-2" only; no names/emails in any recorded bytes.
"""
import json, os, sys, hashlib, subprocess, time

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
RUN_TS = "20260709T232652Z"
RUN_DIR = os.path.join(REPO, "poc/f2b-transfer/opus-runs", RUN_TS)

# ---- §0 pinned inputs (runner fail-closes on every one; ERR_JUDGE2_PIN) ----
PINS = {
    os.path.join(REPO, "poc/f2b-transfer/opus-runs/20260709T171156Z/blind-items-by-id.jsonl"):
        "ce820483336e6e25c607fa72e2591022f192d9e0eddc9a6689e02b4796af42cc",
    os.path.join(REPO, "data/d-adj-t/judge-2-prompt-template.txt"):
        "f21bfce38eda617fe6733efca75e8a2b3e754711931703119ef7c6602749931d",
    os.path.join(REPO, "data/d-adj-t/judge-2-output-schema-mcq.json"):
        "1445fd021780dc54ec0c1cf94f5d70318f203ebe4ce8e2e4ad1a4d8a192deb38",
    os.path.join(REPO, "data/d-adj-t/judge-2-output-schema-claim.json"):
        "3af3eaed608b712178aa4d2a627ddda7c42048f0ebef0c79600b4bee91494727",
    os.path.join(REPO, "data/d-adj-t/judge-2-calibration.jsonl"):
        "8bdb22dac8380ff834889f83b5f9bc0b9733e6446e895963cf0e084a8cffb9a1",
}
ITEMS_PATH   = os.path.join(REPO, "poc/f2b-transfer/opus-runs/20260709T171156Z/blind-items-by-id.jsonl")
TEMPLATE     = os.path.join(REPO, "data/d-adj-t/judge-2-prompt-template.txt")
SCHEMA_MCQ   = os.path.join(REPO, "data/d-adj-t/judge-2-output-schema-mcq.json")
SCHEMA_CLAIM = os.path.join(REPO, "data/d-adj-t/judge-2-output-schema-claim.json")
CALIB_PATH   = os.path.join(REPO, "data/d-adj-t/judge-2-calibration.jsonl")

JUDGE = "judge-2"
JUDGE_SEED = "dadjt/1|judge-2|20260710"          # design §4.2, invocation §2, pinned verbatim
EXPECT_N = 360
EXPECT_CODEX_VER = "codex-cli 0.142.5"
MODEL = "gpt-5.5"
EFFORT = "low"

# §5 banned event-type substrings (tool/command use => attempt INVALID, E5 tripwire)
BANNED_TYPE_SUBSTR = ["exec_command", "terminal_interaction", "unified_exec",
                      "tool_call", "web_search", "patch_apply", "view_image",
                      "image_generation", "collab_"]
# transport-failure event-type substrings (NOT content attempts; §5)
TRANSPORT_TYPE_SUBSTR = ["stream_error", "rate_limit", "rate-limit"]

TRANSPORT_BACKOFF = [30, 60, 120, 300, 300, 300, 300, 300, 300, 300]  # §5, up to 10 retries
MAX_TRANSPORT = 10
MAX_CONTENT = 3            # §6
NOLABEL_ABORT = 18        # §6 run-level abort (>5% of 360)

ALLOWED_MCQ = ["A", "B", "C", "D", "NONE"]
ALLOWED_CLAIM = ["yes", "no", "cannot say"]


def die(msg):
    sys.stderr.write("RUN_JUDGE2_ABORT: %s\n" % msg)
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
            die("ERR_JUDGE2_PIN: %s sha %s != pinned %s" % (path, got, want))
    ver = subprocess.run(["codex", "--version"], capture_output=True, text=True).stdout.strip()
    if ver != EXPECT_CODEX_VER:
        die("ERR_JUDGE2_PIN: codex version %r != %r (BOUNDARY STOP)" % (ver, EXPECT_CODEX_VER))
    return ver


def load_jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def judge_order(items):
    """§2 canonical seeded sort: ascending by sha256_hex(seed | '|' | id)."""
    return sorted(items, key=lambda it: sha256_hex_bytes(
        ("%s|%s" % (JUDGE_SEED, it["id"])).encode("utf-8")))


def item_rendering(it):
    """§1 byte-exact blind rendering (no trailing newline)."""
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
    die("ERR_JUDGE2_PIN: unknown format %r for id %s" % (it.get("format"), it.get("id")))


def build_prompt(template_bytes, it):
    """§1 USER_PROMPT = template with the single '{{ITEM}}' placeholder replaced."""
    if template_bytes.count("{{ITEM}}") != 1:
        die("ERR_JUDGE2_PIN: template placeholder count != 1")
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
    """Return (types, tool_use, transport_signal, token_usage_last)."""
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
        # token counts (best-effort, for the run log)
        et = " ".join(t)
        if "token_count" in et or "token_usage" in et:
            tokens = ev
    tool_use = any(any(b in t for b in BANNED_TYPE_SUBSTR) for t in types)
    transport = any(any(b in t for b in TRANSPORT_TYPE_SUBSTR) for t in types)
    return types, tool_use, transport, tokens


def run_codex(prompt_text, fmt, attempt_dir, workdir):
    """One pinned §3 codex invocation. Returns (exit_code)."""
    os.makedirs(attempt_dir, exist_ok=True)
    up = os.path.join(attempt_dir, "user-prompt.txt")
    with open(up, "w", encoding="utf-8") as f:
        f.write(prompt_text)
    schema = SCHEMA_MCQ if fmt == "mcq" else SCHEMA_CLAIM
    last_msg = os.path.join(attempt_dir, "last-message.json")
    events = os.path.join(attempt_dir, "events.jsonl")
    stderr = os.path.join(attempt_dir, "stderr.log")
    cmd = ["codex", "exec",
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
    """§5 validity. Returns (valid, answer_or_none, reason, last_msg_sha, tool_use, transport)."""
    last_msg = os.path.join(attempt_dir, "last-message.json")
    events = os.path.join(attempt_dir, "events.jsonl")
    _types, tool_use, transport, _tok = scan_events(events)
    # parse last-message
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
    # §5.1 exit 0
    if exit_code != 0:
        # nonzero exit with no model response => transport (handled by caller)
        if parsed is None:
            return False, None, "transport", None, tool_use, True
        return False, None, "parse_failure", lm_sha, tool_use, transport
    # §5.4 tool use
    if tool_use:
        return False, None, "tool_use_detected", lm_sha, True, transport
    # §5.2 object with exactly one key "answer"
    if not (isinstance(parsed, dict) and list(parsed.keys()) == ["answer"]):
        reason = "refusal" if parsed is None else "parse_failure"
        return False, None, reason, lm_sha, tool_use, transport
    ans = parsed["answer"]
    # §5.3 byte-exact in allowed
    if not (isinstance(ans, str) and ans in allowed):
        return False, None, "parse_failure", lm_sha, tool_use, transport
    return True, ans, None, lm_sha, tool_use, transport


def process_item(it, position, base_dir, workdir, template_bytes, log):
    """§1-§6 for one item. Returns response dict."""
    allowed = allowed_set(it)
    fmt = fmt_key(it)
    prompt = build_prompt(template_bytes, it)
    n_content = 0
    n_transport = 0
    last_reason = None
    for content_k in range(1, MAX_CONTENT + 1):
        # transport-retry loop around a single content attempt
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
                    die("ERR_TRANSPORT: item pos %d exceeded %d transport retries; "
                        "infra problem, aborting run" % (position, MAX_TRANSPORT))
                back = TRANSPORT_BACKOFF[min(n_transport - 1, len(TRANSPORT_BACKOFF) - 1)]
                log("  pos %d transport failure (try %d), backoff %ds" % (position, n_transport, back))
                time.sleep(back)
                continue
            break  # got a content result to accept/reject
        n_content = content_k
        if valid:
            return {"answer": ans, "flags": [], "format": it["format"],
                    "id": it["id"], "judge": JUDGE, "last_message_sha256": lm_sha,
                    "n_content_attempts": n_content, "n_transport_retries": n_transport,
                    "position": position}
        last_reason = reason
        log("  pos %d content attempt %d INVALID (%s)" % (position, content_k, reason))
    # §6 no label after 3 invalid content attempts
    return {"answer": None, "flags": ["judge2_no_label", last_reason or "parse_failure"],
            "format": it["format"], "id": it["id"], "judge": JUDGE,
            "last_message_sha256": None, "n_content_attempts": n_content,
            "n_transport_retries": n_transport, "position": position}


def make_workdir():
    """§3 fresh empty dir OUTSIDE any git repo (pinned mktemp template)."""
    out = subprocess.run(["mktemp", "-d", "/tmp/judge2-workdir.XXXXXX"],
                         capture_output=True, text=True)
    wd = out.stdout.strip()
    if not wd or not os.path.isdir(wd):
        die("ERR_WORKDIR: mktemp failed")
    if os.listdir(wd):
        die("ERR_WORKDIR: workdir not empty: %s" % wd)
    # verify not inside a git repo
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
    log("PREFLIGHT start; codex=%s workdir=%s" % (ver, workdir))
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
        die("preflight FAILED; not running any real item (§7)")
    print("PREFLIGHT_PASS", flush=True)


def phase_main():
    ver = verify_pins()
    # require preflight PASS
    ps_path = os.path.join(RUN_DIR, "preflight-status.json")
    if not os.path.exists(ps_path):
        die("no preflight-status.json; run preflight first (§7)")
    ps = json.load(open(ps_path))
    if not ps.get("pass"):
        die("preflight did not PASS; refusing main run")
    workdir = open(os.path.join(RUN_DIR, "workdir-path.txt")).read().strip()
    if not os.path.isdir(workdir):
        die("recorded workdir missing: %s" % workdir)

    template_bytes = open(TEMPLATE, encoding="utf-8").read()
    items = load_jsonl(ITEMS_PATH)
    if len(items) != EXPECT_N:
        die("expected %d items, got %d" % (EXPECT_N, len(items)))
    ordered = judge_order(items)

    # §2 position map -> provenance
    pos_map = [{"position": i, "id": it["id"]} for i, it in enumerate(ordered, 1)]
    with open(os.path.join(RUN_DIR, "judge-2-position-map.jsonl"), "w", encoding="utf-8") as f:
        for r in pos_map:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")

    items_dir = os.path.join(RUN_DIR, "items")
    os.makedirs(items_dir, exist_ok=True)
    logf = open(os.path.join(RUN_DIR, "main-progress.log"), "a")
    def log(m):
        logf.write(m + "\n"); logf.flush()
    log("MAIN start ts=%s codex=%s workdir=%s n=%d" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), ver, workdir, len(ordered)))

    t0 = time.time()
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
            el = time.time() - t0
            log("  progress %d/%d  nolabel=%d transport=%d  elapsed=%.0fs"
                % (i, len(ordered), n_nolabel, total_transport, el))
        # §6 run-level abort
        if n_nolabel > NOLABEL_ABORT:
            die("ERR_NOLABEL: %d no-label items > %d; judge instrument failing, aborting"
                % (n_nolabel, NOLABEL_ABORT))

    # §8 response file (sorted by id) -> data/d-adj-t/
    responses_sorted = sorted(responses, key=lambda r: r["id"])
    out_path = os.path.join(REPO, "data/d-adj-t/judge-2-responses.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for r in responses_sorted:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")

    # label counts (RAW; no interpretation)
    counts = {}
    for r in responses_sorted:
        key = "null" if r["answer"] is None else r["answer"]
        counts[key] = counts.get(key, 0) + 1
    n_mcq = sum(1 for r in responses_sorted if r["format"] == "mcq")
    n_claim = sum(1 for r in responses_sorted if r["format"] == "claim-yes-no")
    summary = {"run_ts": RUN_TS, "judge": JUDGE, "model": MODEL,
               "codex_version": ver, "reasoning_effort": EFFORT,
               "n_items": len(responses_sorted), "n_mcq": n_mcq, "n_claim_yes_no": n_claim,
               "n_judge2_nolabel": n_nolabel, "total_transport_retries": total_transport,
               "label_counts": counts,
               "responses_path": "data/d-adj-t/judge-2-responses.jsonl",
               "responses_sha256": file_sha(out_path),
               "invocation_spec_sha256": file_sha(os.path.join(REPO, "data/d-adj-t/judge-2-invocation.md")),
               "elapsed_seconds": round(time.time() - t0, 1)}
    with open(os.path.join(RUN_DIR, "run-summary.json"), "w") as f:
        f.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    log("MAIN done nolabel=%d transport=%d counts=%s" % (n_nolabel, total_transport, json.dumps(counts, sort_keys=True)))
    print("MAIN_DONE " + json.dumps(counts, sort_keys=True), flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("preflight", "main"):
        die("usage: run-judge2.py preflight|main")
    if sys.argv[1] == "preflight":
        phase_preflight()
    else:
        phase_main()
