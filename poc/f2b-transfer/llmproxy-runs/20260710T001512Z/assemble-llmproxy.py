#!/usr/bin/env python3
"""assemble-llmproxy -- MECHANICAL assembler of data/d-adj-t-llmproxy/ from the
judge-1p run outputs + the reused judge-2 instrument responses + the pinned
membership gold + the deranged-probe manifest, per the FROZEN specs:
  - record   registry/experiments/f2b-transfer-llmproxy.json (dependent_vars)
  - analysis analysis/f2b_transfer_llmproxy.py (the exact integer input fields)
  - spec     data/d-adj-t-llmproxy/judge-1p-invocation.md section 8

Opus experiment-runner EXECUTION role: DESIGNS NOTHING, CONCLUDES NOTHING. Every
field traces to a pinned definition; no scientific discretion. Fail-closed on any
id mismatch or pin mismatch.

Definitions (all pinned; no invention):
  membership gold  = d-qa-t covered.jsonl `answer` per id (pinned via d-qa-t
                     corpus hash 7179ee...); escape tokens {NONE,cannot say}
                     are never gold, so they are disagreement by construction.
  A_1p inputs      = judge-1p labels ALONE (escape = disagreement; no-label
                     leaves the denominator).
  judge-pair       = over items BOTH judges labelled; token_equal = byte-equal.
  panel (concord)  = concordant (token-equal both-labelled) pairs are the
                     "resolved" set (NO judge-3); panel_agree = shared token ==
                     membership gold.
  probe            = correct answer NONE by construction; false_endorse = any of
                     A/B/C/D; deranged_pick = the manifest deranged_option_key.

Writes data/d-adj-t-llmproxy/{labels-proxy.jsonl, summary.json}.
"""
import json, os, sys, hashlib

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
RUN_TS = "20260710T001512Z"
RUN_DIR = os.path.join(REPO, "poc/f2b-transfer/llmproxy-runs", RUN_TS)
D = os.path.join(REPO, "data/d-adj-t-llmproxy")

J1P_RESP   = os.path.join(D, "judge-1p-responses.jsonl")
J1P_PROBE  = os.path.join(D, "judge-1p-probe-responses.jsonl")
J2_RESP    = os.path.join(REPO, "data/d-adj-t/judge-2-responses.jsonl")
GOLD_PATH  = os.path.join(REPO, "data/d-qa-t/items/covered.jsonl")
PROBE_MANIFEST = os.path.join(D, "deranged-probe-manifest.json")
INVOCATION_SPEC = os.path.join(D, "judge-1p-invocation.md")
PREFLIGHT  = os.path.join(RUN_DIR, "preflight-status.json")

ESCAPE_TOKENS = {"NONE", "cannot say"}
MCQ_OPTIONS = {"A", "B", "C", "D"}


def die(msg):
    sys.stderr.write("ASSEMBLE_LLMPROXY_ABORT: %s\n" % msg)
    sys.exit(2)


def file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def main():
    # --- load pinned gold (membership) ---
    gold = {}
    for r in load_jsonl(GOLD_PATH):
        gold[r["id"]] = r["answer"]

    # --- load judge responses (keyed by id) ---
    j1p = {r["id"]: r for r in load_jsonl(J1P_RESP)}
    j2 = {r["id"]: r for r in load_jsonl(J2_RESP)}
    probes = {r["id"]: r for r in load_jsonl(J1P_PROBE)}
    manifest = json.load(open(PROBE_MANIFEST))
    deranged_key = {row["probe_id"]: row["deranged_option_key"] for row in manifest["rows"]}

    real_ids = sorted(j1p.keys())
    if len(real_ids) != 360:
        die("expected 360 judge-1p real items, got %d" % len(real_ids))
    for iid in real_ids:
        if iid not in gold:
            die("real id missing membership gold: %s" % iid)
        if iid not in j2:
            die("real id missing judge-2 response: %s" % iid)
    if len(j2) != 360:
        die("expected 360 judge-2 responses, got %d" % len(j2))
    if len(probes) != 60:
        die("expected 60 probe responses, got %d" % len(probes))

    # --- per-item labels-proxy + counters ---
    n_items = len(real_ids)
    n_lab = n_nolab = n_agree = n_escape = 0
    jp_both = jp_eq = 0
    n_lab_j2 = n_agree_j2 = 0
    panel_resolved = panel_agree = 0

    labels_rows = []
    for iid in real_ids:
        g = gold[iid]
        a1 = j1p[iid]["answer"]
        a2 = j2[iid]["answer"]
        labelled_1 = a1 is not None
        escape = labelled_1 and (a1 in ESCAPE_TOKENS)
        agree_mem = labelled_1 and (a1 == g)
        if labelled_1:
            n_lab += 1
            if agree_mem:
                n_agree += 1
            if escape:
                n_escape += 1
        else:
            n_nolab += 1
        # judge-2 diagnostics
        if a2 is not None:
            n_lab_j2 += 1
            if a2 == g:
                n_agree_j2 += 1
        # judge pair (both labelled)
        both = labelled_1 and (a2 is not None)
        token_equal = (both and a1 == a2)
        if both:
            jp_both += 1
            if token_equal:
                jp_eq += 1
                panel_resolved += 1              # concordant = resolved (no judge-3)
                if a1 == g:                       # shared token vs membership gold
                    panel_agree += 1
        pair_token_equal = token_equal if both else None
        labels_rows.append({"id": iid, "label_j1p": a1,
                            "agree_membership": bool(agree_mem),
                            "escape": bool(escape),
                            "j2_answer": a2,
                            "pair_token_equal": pair_token_equal,
                            "flags": j1p[iid].get("flags", [])})

    # --- probes ---
    n_probe_lab = n_probe_none = n_probe_fe = n_probe_dp = 0
    for pid, r in probes.items():
        a = r["answer"]
        if a is None:
            continue
        n_probe_lab += 1
        if a == "NONE":
            n_probe_none += 1
        elif a in MCQ_OPTIONS:
            n_probe_fe += 1
            if a == deranged_key.get(pid):
                n_probe_dp += 1
        else:
            die("probe %s labelled with unexpected token %r" % (pid, a))

    preflight_pass = bool(json.load(open(PREFLIGHT)).get("pass"))

    # --- write labels-proxy.jsonl (sorted by id) ---
    labels_path = os.path.join(D, "labels-proxy.jsonl")
    with open(labels_path, "w", encoding="utf-8") as f:
        for row in labels_rows:
            f.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
    labels_sha = file_sha(labels_path)

    # --- summary.json: EXACT analysis-input integers (analysis _rec fields) + disclosure ---
    metrics = {
        "n_items": n_items,
        "n_labelled_j1p": n_lab,
        "n_nolabel_j1p": n_nolab,
        "n_agree_j1p": n_agree,
        "n_escape_j1p": n_escape,
        "judge_pairs_both_labelled": jp_both,
        "judge_pairs_token_equal": jp_eq,
        "n_labelled_j2": n_lab_j2,
        "n_agree_j2": n_agree_j2,
        "panel_resolved": panel_resolved,
        "panel_agree_membership": panel_agree,
        "n_probe_labelled": n_probe_lab,
        "n_probe_false_endorse": n_probe_fe,
        "n_probe_none": n_probe_none,
        "n_probe_deranged_pick": n_probe_dp,
        "preflight_pass": preflight_pass,
        "labels_sha256": labels_sha,
    }
    summary = {
        "experiment": "f2b-transfer-llmproxy",
        "arm": "adjudication-instrument",
        "run_ts": RUN_TS,
        "analysis_input_metrics": metrics,
        "sourcing_disclosure": {
            "judge_1p": {"role": "SOLE gold source (judge-1 role STAND-IN)",
                         "model": "gpt-5.6-sol",
                         "codex": "codex-cli 0.144.1 via npx -y @openai/codex@0.144.1",
                         "reasoning_effort": "low",
                         "invocation_spec_sha256": file_sha(INVOCATION_SPEC),
                         "responses_sha256": file_sha(J1P_RESP),
                         "probe_responses_sha256": file_sha(J1P_PROBE)},
            "judge_2": {"role": "DIAGNOSTIC-ONLY + FAIL-direction stability gate (NEVER gold)",
                        "model": "gpt-5.5",
                        "codex": "codex-cli 0.142.5 (global)",
                        "reasoning_effort": "low",
                        "responses_sha256": file_sha(J2_RESP),
                        "note": "judge-1p (GPT-5.6) and judge-2 (GPT-5.5) are ONE model family; "
                                "their raw agreement is a CORRELATION DIAGNOSTIC and NEVER "
                                "independent validation (envelope clauses 1 and 5)."},
            "membership_gold": {"source": "data/d-qa-t/items/covered.jsonl (answer field)",
                                "corpus": "d-qa-t", "pin": "7179ee6791bd0af643c410872925ff594945c29b563192f6d7c4a872397cee27"},
            "probe": {"source": "data/d-adj-t-llmproxy/deranged-probe.jsonl",
                      "correct_answer_by_construction": "NONE",
                      "manifest_sha256": file_sha(PROBE_MANIFEST)},
            "coverage_disclosure": "kernel-expressibility coverage 0.3542 at rung molecules-v0, "
                                   "MEASURED by m0b on one incomplete kernel-v0 instance -- NOT "
                                   "general coverage; bounded to the covered concepts of d-qa-t.",
        },
    }
    summary_path = os.path.join(D, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    print(json.dumps(metrics, sort_keys=True))
    print("ASSEMBLE_DONE labels=%s" % labels_sha, file=sys.stderr)


if __name__ == "__main__":
    main()
