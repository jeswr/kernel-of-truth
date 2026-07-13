#!/usr/bin/env python3
"""run-opus-pb-rejudge -- g3-llmproxy-v3 Pass-B RE-JUDGE with a strong Opus
judge (claude-opus-4-8), testing whether the registered g3-llmproxy-v3 = FAIL
(concordant necessity 36/195 = 0.1846, one-sided 95% Wilson LB 0.1433 > 0.10)
is an artifact of the judge-pB Haiku Pass-B over-flagging found by the human
reconciliation (docs/next/analysis/g3-human-proxy-reconciliation.md).

EXPLORATORY / ADVISORY ONLY -- writes ONLY under poc/g3-llmproxy-v3/
opus-pb-rejudge/. Does NOT touch the frozen g3 record, the registered
g3-llmproxy-v3 verdict, data/g3-annot-llmproxy-v3/, or the registry. The
coordinator does any formal re-verdict.

Design contract (change ONLY the Pass-B judge model):
  - SAME Pass-B prompt bytes: pinned poc/g3-llmproxy/prompt-template-pass-b.txt
    rendered through the pinned run-g3lp-v3.py assembly functions (imported,
    never reimplemented).
  - SAME judge-pB system prompt: pinned v2 hardened
    poc/g3-llmproxy-v2/judge-pB-system-prompt-pass-b.txt.
  - SAME item order: manifest real_orders["judge-pB-passB"], seed-reverified.
  - SAME invocation form (truthstyle section-4.3 headless `claude -p`), same
    env hardening (auth vars unset => subscription auth, MAX_THINKING_TOKENS=0,
    --tools "" --setting-sources "" --no-session-persistence), same section-5
    extraction + section-6 blinding scan via the pinned reference
    implementations imported from analysis/g3_llmproxy_v3.py, same section-7
    retry / no-label contract.
  - ONLY delta: --model claude-opus-4-8 (pinned; the alias IS the complete
    current model id -- no dated snapshot exists for Opus 4.8) instead of
    claude-haiku-4-5-20251001. "temperature 0" is discharged exactly as in the
    pinned spec: first VALID answer is final (claude -p exposes no temperature
    knob; identical to the registered run's convention).
  - DISCLOSED identity-check adaptation: on this claude-code version an Opus
    run's result event reports modelUsage keys {claude-opus-4-8,
    claude-haiku-4-5-*} -- the Haiku key is a CLI-internal sidecar call (it
    was invisible in the registered run only because the judge model WAS
    Haiku). The tripwire here requires init.model == claude-opus-4-8,
    apiKeySource == "none", claude-opus-4-8 present in modelUsage, and every
    OTHER modelUsage key to start with "claude-haiku-4-5" (the sidecar);
    anything else ABORTS.

Usage:
  run-opus-pb-rejudge.py run        # preflight (selftest+pins+cal-B) + all 200
  run-opus-pb-rejudge.py analyze    # recompute rates -> analysis.json
"""
import importlib.util
import json
import os
import subprocess
import sys
import time

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
HERE = os.path.join(REPO, "poc/g3-llmproxy-v3/opus-pb-rejudge")
PROV = os.path.join(HERE, "provenance")
OUT_LABELS = os.path.join(HERE, "opus-pb-responses.jsonl")
OUT_ANALYSIS = os.path.join(HERE, "analysis.json")

MODEL = "claude-opus-4-8"          # pinned exact current Opus id (see docstring)
JUDGE_ID = "judge-pB-opus48-rejudge"
SIDE_CAR_PREFIX = "claude-haiku-4-5"   # disclosed CLI-internal sidecar allowance

sys.path.insert(0, os.path.join(REPO, "analysis"))
import g3_llmproxy_v3 as G   # pinned section-5/6 reference impls + wilson_bounds

# import the pinned runner module verbatim (assembly, pins, loaders, label checks)
_spec = importlib.util.spec_from_file_location(
    "run_g3lp_v3", os.path.join(REPO, "poc/g3-llmproxy-v3/run-g3lp-v3.py"))
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

MAX_CONTENT = 3
MAX_TRANSPORT = 10
TRANSPORT_BACKOFF = [30, 60, 120, 300, 300, 300, 300, 300, 300, 300]
NOLABEL_ABORT = 10


def die(msg):
    sys.stderr.write("OPUS_PB_REJUDGE_ABORT: %s\n" % msg)
    sys.exit(2)


def log_open():
    os.makedirs(PROV, exist_ok=True)
    lf = open(os.path.join(PROV, "run-log.txt"), "a", encoding="utf-8")

    def log(m):
        ts = time.strftime("[%Y-%m-%dT%H:%M:%SZ]", time.gmtime())
        lf.write("%s %s\n" % (ts, m))
        lf.flush()
        print(m, flush=True)
    return log


# ---------------- invocation (SAME form as R.run_claude; model swapped) -----
def run_claude_opus(prompt_text, attempt_dir, workdir, sys_prompt):
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
    cmd = ["claude", "-p", "--model", MODEL,
           "--system-prompt", sys_prompt, "--tools", "",
           "--setting-sources", "", "--no-session-persistence",
           "--output-format", "stream-json", "--verbose"]
    with open(up, "rb") as fin, open(events, "wb") as fout, open(stderr, "wb") as ferr:
        p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=ferr,
                           cwd=workdir, env=env)
    return p.returncode


def validate_claude_opus(exit_code, attempt_dir, allowed_cids):
    """Adapted from the pinned R.validate_claude: identical section-5/6/H1
    checks; identity tripwire adapted for the Opus model + the disclosed
    Haiku sidecar modelUsage key (see module docstring)."""
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
    extra = [k for k in mu if k != MODEL]
    identity_ok = (init and init.get("model") == MODEL
                   and init.get("apiKeySource") == "none"
                   and MODEL in mu
                   and all(k.startswith(SIDE_CAR_PREFIX) for k in extra))
    if not identity_ok:
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
    lab, flst, reason = R.label_pass_b(obj, allowed_cids)
    if lab is None:
        return ("content_invalid", None, raw, reason)
    return ("valid", {"q2": lab, "q2_failing_conditions": flst}, raw, None)


def do_attempt(prompt, attempt_dir, workdir, sys_prompt, allowed_cids):
    rc = run_claude_opus(prompt, attempt_dir, workdir, sys_prompt)
    status, fields, raw, reason = validate_claude_opus(rc, attempt_dir, allowed_cids)
    # section-6 blinding audit (pinned reference impls; ABORT on any hit)
    hit = G.blinding_scan([os.path.join(attempt_dir, "user-prompt.txt"),
                           os.path.join(attempt_dir, "events.jsonl"),
                           os.path.join(attempt_dir, "stderr.log")])
    if hit:
        die("BLINDING file hit token=%r surface=%s dir=%s"
            % (hit[1], hit[0], attempt_dir))
    ahit = G.answer_blinding_hit(raw)
    if ahit:
        die("BLINDING answer-surface hit token=%r dir=%s" % (ahit, attempt_dir))
    return status, fields, raw, reason


def process_item(prompt, position, base_dir, workdir, sys_prompt, allowed, log):
    n_transport = 0
    last_reason = None
    for content_k in range(1, MAX_CONTENT + 1):
        while True:
            call_dir = os.path.join(base_dir, "c%d_t%d" % (content_k, n_transport))
            status, fields, raw, reason = do_attempt(
                prompt, call_dir, workdir, sys_prompt, allowed)
            if status == "abort":
                die("IDENTITY pos %s: %s" % (position, reason))
            if status == "transport":
                cap = R._cap_hit(R._cap_text(call_dir))
                if cap:
                    die("STOPCAP pos %s: usage/session cap pattern %r hit; "
                        "STOP (no retry-spin). dir=%s" % (position, cap, call_dir))
                n_transport += 1
                if n_transport > MAX_TRANSPORT:
                    die("TRANSPORT pos %s exceeded %d retries" % (position, MAX_TRANSPORT))
                back = TRANSPORT_BACKOFF[min(n_transport - 1, len(TRANSPORT_BACKOFF) - 1)]
                log("  pos %s transport failure (try %d), backoff %ds"
                    % (position, n_transport, back))
                time.sleep(back)
                continue
            break
        if status == "valid":
            r = {"flags": [], "n_content_attempts": content_k,
                 "n_transport_retries": n_transport, "position": position}
            r.update(fields)
            return r
        last_reason = reason
        log("  pos %s content attempt %d INVALID (%s)" % (position, content_k, reason))
    return {"flags": ["judge_no_label", last_reason or "parse_failure"],
            "n_content_attempts": MAX_CONTENT, "n_transport_retries": n_transport,
            "position": position, "q2": None, "q2_failing_conditions": None}


# ---------------- checkpoint ----------------
def cp_load():
    done = {}
    cp = os.path.join(PROV, "checkpoint.jsonl")
    if os.path.exists(cp):
        for l in open(cp, encoding="utf-8"):
            l = l.strip()
            if l:
                o = json.loads(l)
                done[o["id"]] = o["response"]
    return done


def cp_append(item_id, response):
    with open(os.path.join(PROV, "checkpoint.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"id": item_id, "response": response},
                           sort_keys=True, ensure_ascii=False) + "\n")


# ---------------- phases ----------------
def phase_run():
    log = log_open()
    # runner-local selftest FIRST (spec section 8)
    st = subprocess.run([sys.executable,
                         os.path.join(REPO, "analysis/g3_llmproxy_v3.py"),
                         "--selftest"], capture_output=True, text=True)
    if st.returncode != 0 or "g3-llmproxy-v3 selftest OK" not in st.stdout:
        die("SELFTEST: %s%s" % (st.stdout, st.stderr))
    banners = R.verify_pins("claude")   # section-0 pins + corpus digest + CLAUDE.md
    log("PREFLIGHT selftest=OK pins=OK banners=%s model=%s judge=%s"
        % (json.dumps(banners), MODEL, JUDGE_ID))
    workdir_file = os.path.join(PROV, "workdir-path.txt")
    if os.path.exists(workdir_file) and os.path.isdir(open(workdir_file).read().strip()):
        workdir = open(workdir_file).read().strip()
    else:
        workdir = R.make_workdir("pbopus")
        with open(workdir_file, "w") as f:
            f.write(workdir + "\n")
    log("workdir=%s" % workdir)

    tmpl = R.read_template("B")
    sys_prompt = R.read_sysprompt("B")

    # calibration: the two pass-B items, first-attempt exact match required
    cal_status_p = os.path.join(PROV, "calibration-status.json")
    if not (os.path.exists(cal_status_p) and json.load(open(cal_status_p)).get("pass")):
        cal_results, ok = [], True
        for cal in R.load_calibration():
            if cal["pass"] != "B":
                continue
            prompt = R.prompt_for_cal(cal, tmpl)
            allowed = [c["cid"] for c in cal["conditions"]]
            call_dir = os.path.join(PROV, "preflight", cal["id"])
            status, fields, raw, reason = do_attempt(
                prompt, call_dir, workdir, sys_prompt, allowed)
            if status == "abort":
                die("IDENTITY preflight %s: %s" % (cal["id"], reason))
            item_ok = (status == "valid") and (fields == cal["expected"])
            cal_results.append({"id": cal["id"], "status": status, "got": fields,
                                "expected": cal["expected"], "pass": item_ok})
            log("PREFLIGHT %s status=%s got=%s expected=%s => %s"
                % (cal["id"], status, fields, cal["expected"],
                   "PASS" if item_ok else "FAIL"))
            if not item_ok:
                ok = False
        with open(cal_status_p, "w") as f:
            json.dump({"pass": ok, "model": MODEL, "results": cal_results,
                       "banners": banners}, f, indent=2, sort_keys=True)
        if not ok:
            die("calibration FAILED for %s" % MODEL)

    insts = R.load_instances()
    conds = R.load_conditions()
    manifest = R.load_manifest()
    order = manifest["real_orders"]["judge-pB-passB"]
    seed = manifest["seed_real_orders"]["judge-pB-passB"]
    recomputed = sorted(order, key=lambda i: R.sha_bytes(("%s|%s" % (seed, i)).encode()))
    if recomputed != order or len(order) != 200:
        die("ORDER: manifest judge-pB-passB order failed seed re-verification")
    # position map (provenance)
    pm = os.path.join(PROV, "position-map.jsonl")
    if not os.path.exists(pm):
        with open(pm, "w", encoding="utf-8") as f:
            for i, iid in enumerate(order, 1):
                f.write(json.dumps({"position": "b%d" % i, "id": iid},
                                   sort_keys=True) + "\n")

    done = cp_load()
    log("PASS B (%s) start n=%d resume_done=%d" % (MODEL, len(order), len(done)))
    responses = {}
    n_nolabel = 0
    t0 = time.time()
    for i, iid in enumerate(order, 1):
        if iid in done:
            r = done[iid]
        else:
            base_dir = os.path.join(PROV, "passB", iid)
            allowed = R.allowed_cids_real(iid, "B", insts, conds)
            prompt = R.prompt_for_real(iid, "B", insts, conds, tmpl)
            r = process_item(prompt, "b%d" % i, base_dir, workdir, sys_prompt,
                             allowed, log)
            r["id"] = iid
            r["judge"] = JUDGE_ID
            cp_append(iid, r)
        responses[iid] = r
        if r.get("q2") is None:
            n_nolabel += 1
        if n_nolabel > NOLABEL_ABORT:
            die("NOLABEL: %d no-label > %d; ABORT" % (n_nolabel, NOLABEL_ABORT))
        if i % 20 == 0 or i == len(order):
            log("  B %d/%d nolabel=%d elapsed=%.0fs" % (i, len(order), n_nolabel,
                                                        time.time() - t0))
    banners_after = R.verify_pins("claude")
    if banners_after != banners:
        die("PIN: banner drift %s -> %s" % (banners, banners_after))
    fld = ["id", "q2", "q2_failing_conditions", "flags", "n_content_attempts",
           "n_transport_retries", "position", "judge"]
    with open(OUT_LABELS, "w", encoding="utf-8") as f:
        for iid in sorted(responses):
            r = responses[iid]
            f.write(json.dumps({k: r.get(k) for k in fld}, sort_keys=True,
                               ensure_ascii=False) + "\n")
    log("RUN_DONE nolabel=%d labels=%s sha256=%s"
        % (n_nolabel, OUT_LABELS, R.file_sha(OUT_LABELS)))


# ---------------- analysis ----------------
DEC = ("yes", "no")
BAR = 0.10

# Human labels recoverable from the verified reconciliation record
# (docs/next/analysis/g3-human-proxy-reconciliation.md). Full 15-item workbook
# is NOT in the repo; sanity comparison covers these named items only.
HUMAN_Q2 = {"g3-end-01": "no", "g3-end-06": "yes", "g3-end-07": "yes",
            "g3-end-09": "yes", "g3-begin-01": "yes", "g3-begin-03": "yes"}
HUMAN_Q1_FALSE = {"g3-end-03"}  # human says the concept does not apply (A=FALSE)


def phase_analyze():
    frozen = {}
    for l in open(os.path.join(REPO, "data/g3-annot-llmproxy-v3/labels-proxy.jsonl"),
                  encoding="utf-8"):
        o = json.loads(l)
        frozen[o["id"]] = o
    opus = {}
    for l in open(OUT_LABELS, encoding="utf-8"):
        o = json.loads(l)
        opus[o["id"]] = o
    ids = sorted(frozen)
    assert len(ids) == 200 and set(opus) == set(frozen), "id mismatch"

    # --- Variant 1 (PRIMARY): the frozen concordant formula with judge-pB's
    # Pass-B labels swapped Haiku -> Opus. Everything else (judge-pA q1+q2,
    # judge-pB q1) is the frozen data unchanged.
    n_dual = n_conc = n_union = n_a_only = n_b_only = 0
    n_suf_conc = n_suf_union = 0
    per = []
    for iid in ids:
        fz, op = frozen[iid], opus[iid]
        q1a, q2a = fz["q1_pA"], fz["q2_pA"]
        q1b = fz["q1_pB"]
        q2b_opus = op["q2"]
        dec_a = q1a in DEC and q2a in DEC
        dec_b = q1b in DEC and (q2b_opus in DEC)
        dd = dec_a and dec_b
        nva = q1a == "yes" and q2a == "no"
        nvb = q1b == "yes" and q2b_opus == "no"
        sva = q1a == "no" and q2a == "yes"
        svb = q1b == "no" and q2b_opus == "yes"
        per.append({"id": iid, "dual_decisive": dd, "nva": nva, "nvb_opus": nvb,
                    "q2_haiku": fz["q2_pB"], "q2_opus": q2b_opus})
        if dd:
            n_dual += 1
            if nva and nvb:
                n_conc += 1
            if nva or nvb:
                n_union += 1
            if nva and not nvb:
                n_a_only += 1
            if nvb and not nva:
                n_b_only += 1
            if sva and svb:
                n_suf_conc += 1
            if sva or svb:
                n_suf_union += 1
    rate_conc = n_conc / n_dual if n_dual else 0.0
    lb_conc, ub_conc = G.wilson_bounds(rate_conc, n_dual)
    rate_union = n_union / n_dual if n_dual else 0.0
    lb_union, ub_union = G.wilson_bounds(rate_union, n_dual)
    kappa = G.kappa_2x2(n_conc, n_dual - n_conc - n_a_only - n_b_only,
                        n_a_only, n_b_only)

    # --- Variant 2 (task-stated cross-judge marginal): judge-pA q1 AND Opus q2
    n2 = v2 = 0
    for iid in ids:
        q1a = frozen[iid]["q1_pA"]
        q2o = opus[iid]["q2"]
        if q1a in DEC and q2o in DEC:
            n2 += 1
            if q1a == "yes" and q2o == "no":
                v2 += 1
    rate2 = v2 / n2 if n2 else 0.0
    lb2, ub2 = G.wilson_bounds(rate2, n2)

    # --- Opus-pB vs Haiku-pB q2 agreement (both decisive) ---
    n_both = agree = 0
    hy_on = hn_oy = 0    # haiku yes/opus no; haiku no/opus yes
    yy = nn = 0
    for iid in ids:
        qh, qo = frozen[iid]["q2_pB"], opus[iid]["q2"]
        if qh in DEC and qo in DEC:
            n_both += 1
            if qh == qo:
                agree += 1
                if qh == "yes":
                    yy += 1
                else:
                    nn += 1
            elif qh == "yes":
                hy_on += 1
            else:
                hn_oy += 1
    kappa_hq = G.kappa_2x2(nn, yy, hn_oy, hy_on)  # 2x2 on q2=="no" indicator

    # --- sanity vs the recoverable human labels ---
    human_rows = []
    match = tot = 0
    for iid, hq2 in sorted(HUMAN_Q2.items()):
        qo = opus[iid]["q2"]
        ok = qo == hq2
        tot += 1
        match += ok
        human_rows.append({"id": iid, "human_q2": hq2, "opus_q2": qo,
                           "haiku_q2": frozen[iid]["q2_pB"], "opus_matches_human": ok})

    # verdict recommendation logic (advisory; mirrors the registered bracket):
    # FAIL-analog fires iff concordant LB > 0.10; PASS-analog iff union UB <= 0.10.
    swapped_fail = lb_conc > BAR
    swapped_pass = ub_union <= BAR
    if swapped_fail:
        rec = "FAIL-STANDS"
    elif not swapped_fail and (swapped_pass or rate_conc < BAR):
        rec = "FLIPS-TO-NOT-FAIL" if not swapped_pass else "FLIPS-TO-NOT-FAIL (PASS-analog)"
    else:
        rec = "INCONCLUSIVE"

    n_nolabel = sum(1 for iid in ids if opus[iid]["q2"] is None)
    n_cannot = sum(1 for iid in ids if opus[iid]["q2"] == "cannot-say")
    analysis = {
        "_what": "opus-pb-rejudge advisory recompute; frozen record untouched",
        "judge_pB_rejudge_model": MODEL,
        "judge_id": JUDGE_ID,
        "labels_sha256": R.file_sha(OUT_LABELS),
        "n_instances": 200,
        "opus_pB_nolabel": n_nolabel,
        "opus_pB_cannot_say": n_cannot,
        "registered": {"n_dual_decisive": 195, "necessity_concordant": 36,
                       "rate": 36 / 195,
                       "wilson_lb": G.wilson_bounds(36 / 195, 195)[0],
                       "verdict": "FAIL", "bar": BAR},
        "variant1_frozen_formula_pB_passB_swapped": {
            "definition": "concordant = (q1_pA=yes & q2_pA=no) AND (q1_pB[haiku,frozen]=yes & q2_pB[OPUS]=no), over dual-decisive",
            "n_dual_decisive": n_dual,
            "necessity_concordant": n_conc,
            "necessity_rate_concordant": rate_conc,
            "necessity_concordant_wilson_lb": lb_conc,
            "necessity_concordant_wilson_ub": ub_conc,
            "necessity_union": n_union,
            "necessity_rate_union": rate_union,
            "necessity_union_wilson_ub": ub_union,
            "necessity_a_only": n_a_only,
            "necessity_b_only": n_b_only,
            "kappa_pair_necessity": kappa,
            "sufficiency_concordant": n_suf_conc,
            "sufficiency_union": n_suf_union,
            "proxy_fail_fires": swapped_fail,
            "proxy_pass_fires": swapped_pass,
        },
        "variant2_crossjudge_pAq1_x_opusq2": {
            "definition": "violation = q1_pA=yes & q2[OPUS]=no, over items with both decisive (the reconciliation's cross-judge face)",
            "n_decisive": n2, "violations": v2, "rate": rate2,
            "wilson_lb": lb2, "wilson_ub": ub2,
        },
        "opus_vs_haiku_q2": {
            "n_both_decisive": n_both, "agree": agree,
            "agreement": agree / n_both if n_both else None,
            "haiku_yes_opus_no": hy_on, "haiku_no_opus_yes": hn_oy,
            "kappa_on_q2_no": kappa_hq,
        },
        "opus_vs_human_sanity": {
            "note": ("full 15-item human workbook not in repo; comparison covers "
                     "the %d items whose human q2 is recoverable verbatim from the "
                     "verified reconciliation record; g3-end-03 excluded (human "
                     "q1=no, q2 not stated)" % tot),
            "n": tot, "match": match, "rows": human_rows,
        },
        "recommendation": rec,
    }
    with open(OUT_ANALYSIS, "w") as f:
        json.dump(analysis, f, indent=2, sort_keys=True)
    with open(os.path.join(PROV, "per-item-recompute.jsonl"), "w") as f:
        for row in per:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    print(json.dumps({"recommendation": rec,
                      "swapped_concordant": "%d/%d" % (n_conc, n_dual),
                      "swapped_rate": round(rate_conc, 4),
                      "swapped_wilson_lb": round(lb_conc, 4),
                      "bar": BAR}, sort_keys=True))
    print("ANALYZE_DONE -> %s" % OUT_ANALYSIS)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("run", "analyze"):
        die("usage: run|analyze")
    if sys.argv[1] == "run":
        phase_run()
    else:
        phase_analyze()
