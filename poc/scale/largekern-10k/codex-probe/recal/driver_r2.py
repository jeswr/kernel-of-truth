#!/usr/bin/env python3
"""driver_r2.py — codex-as-drafting-transport RE-CALIBRATION with the R=2 repair
loop, over the FIXED prompt (prompt.py now carries the full closed vocabulary).

Per concept: draft (wave 0) -> run the SAME acceptance stack the pipeline uses
(accept.parse_output + accept.lint_gloss + accept.validate_shards over the
encoder) -> if it fails and is not an abstention, feed the REAL ERR_* codes back
via prompt.repair_suffix and redraft, up to R=2 repairs (waves 1,2). Abstention
and malformed-parse are handled exactly as orchestrator.py does: abstention is
terminal (routed to QUARANTINED/ABSTAINED, counts against alpha); malformed
enters repair with the parse error.

Transport = the isolated-CODEX_HOME / gpt-5.6-sol / medium-effort / no-tools
pattern from run_codex_draft.sh (the probe's calibration transport, verbatim).

Measures: first-pass valid rate, post-repair valid rate, abstention rate, mean
calls/concept, per-call wall. alpha uses the pilot's OWN definition
(run_e2e.py:149-150): alpha = accepted/(accepted+quarantined), Wilson 95% LB,
where quarantined includes abstained + still-invalid-after-R2. No git ops.
"""
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.abspath(os.path.join(HERE, ".."))
PIPE = os.path.abspath(os.path.join(HERE, "..", "..", "pipeline"))
sys.path.insert(0, PIPE)
import prompt as promptmod    # noqa: E402
import accept                  # noqa: E402
import common                  # noqa: E402
sys.path.insert(0, os.path.join(common.REPO_ROOT, "tools", "registry"))
from kot_common import wilson_lower_bound  # noqa: E402 — the pilot's pinned Wilson LB

OUT = os.path.join(HERE, "out")
RUNS = os.path.join(OUT, "runs")
WRAPPER = os.path.join(PROBE, "run_codex_draft.sh")
R = common.R_REPAIR                    # 2
MAX_WAVES = R + 1                       # wave 0 draft + R repairs
CALL_TIMEOUT = 300                     # s; mean ~21s, generous ceiling
MAX_PARALLEL = 4                       # matches the probe's measured no-throttle 4-way

# The probe's transport framing, verbatim (codex exec is agentic; tell it to be
# a pure text generator). Whether output stays clean under it is part of the test.
TRANSPORT_PREAMBLE = (
    "You are acting purely as a text-generation model, NOT as a coding agent. "
    "Do NOT use any tools, do NOT read or write files, do NOT search, do NOT "
    "explain your reasoning. Follow the drafting contract below and respond with "
    "EXACTLY ONE JSON object per its OUTPUT PROTOCOL -- no code fences, no "
    "preamble, no trailing commentary. Your entire reply must be that JSON object.\n\n"
)

_FENCE = re.compile(r"^```[a-zA-Z0-9]*\s*|\s*```$", re.MULTILINE)


def build_prompt_text(rb, row, wave, prev_output, err_codes):
    suffix = (promptmod.draft_suffix(row) if wave == 0
              else promptmod.repair_suffix(row, prev_output or "", err_codes, wave=wave))
    return (TRANSPORT_PREAMBLE
            + "===== DRAFTING CONTRACT (developer) =====\n"
            + rb.prefix_text
            + "\n===== DRAFT TASK (user) =====\n"
            + suffix + "\n")


def extract_text(path):
    if not os.path.exists(path):
        return ""
    raw = open(path, "r", encoding="utf-8").read().strip()
    if not raw:
        return ""
    try:
        obj = json.loads(raw)
    except ValueError:
        return raw
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        for k in ("last_agent_message", "message", "text", "content", "output_text"):
            v = obj.get(k)
            if isinstance(v, str):
                return v
            if isinstance(v, list):
                return "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in v)
        return json.dumps(obj)
    return raw


def coerce_json_object(text):
    t = (text or "").strip()
    if not t:
        return None, "empty"
    try:
        json.loads(t); return t, "direct"
    except ValueError:
        pass
    stripped = _FENCE.sub("", t).strip()
    try:
        json.loads(stripped); return stripped, "stripped_fences"
    except ValueError:
        pass
    start = stripped.find("{")
    if start < 0:
        return None, "no_object"
    depth = 0; instr = False; esc = False
    for i in range(start, len(stripped)):
        c = stripped[i]
        if instr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': instr = False
            continue
        if c == '"': instr = True
        elif c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                cand = stripped[start:i + 1]
                try:
                    json.loads(cand); return cand, "brace_scan"
                except ValueError:
                    return None, "brace_scan_invalid"
    return None, "unbalanced"


def call_codex(prompt_text, wave_dir):
    os.makedirs(wave_dir, exist_ok=True)
    ppath = os.path.join(wave_dir, "prompt.txt")
    open(ppath, "w", encoding="utf-8").write(prompt_text)
    t0 = time.time()
    try:
        proc = subprocess.run(["bash", WRAPPER, ppath, wave_dir],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=CALL_TIMEOUT)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        rc = -9
    wall = time.time() - t0
    text = extract_text(os.path.join(wave_dir, "last-message.json"))
    open(os.path.join(wave_dir, "assistant-text.txt"), "w", encoding="utf-8").write(text)
    return rc, wall, text


def evaluate(cid, text):
    """Run the acceptance stack on one returned text. Returns
    (outcome, err_codes, detail) where outcome in
    {'accepted','abstain','invalid','malformed','no_output'} and err_codes is
    the REAL fail-closed list to feed the repair wave."""
    jtext, coerce = coerce_json_object(text)
    if jtext is None:
        return "malformed", ["ERR_OUTPUT_PARSE: %s" % coerce], {"coerce": coerce}
    kind, payload = accept.parse_output(jtext)
    if kind == "malformed":
        return "malformed", list(payload), {"coerce": coerce}
    if kind == "abstain":
        return "abstain", [], {"cannot_draft": payload, "coerce": coerce}
    # kind == 'draft'
    row_lemma = evaluate._lemma.get(cid, "")
    lint_errs = accept.lint_gloss(payload["gloss"], row_lemma)
    per_id, _ = accept.validate_shards({cid: payload["explication"]})
    ok, vcode = per_id.get(cid, (False, "ERR_NO_VALIDATOR_RESULT"))
    errs = list(lint_errs)
    if not ok:
        errs.append(vcode or "ERR_VALIDATE")
    if not errs:
        return "accepted", [], {"coerce": coerce, "gloss": payload["gloss"]}
    return "invalid", errs, {"coerce": coerce, "validatorCode": (None if ok else vcode),
                             "lintErrs": lint_errs}


evaluate._lemma = {}


def process_concept(idx, row, rb):
    cid = row["conceptId"]
    tag = "%02d-%s-%s" % (idx, row["pos"], re.sub(r"[^A-Za-z0-9]", "", row["lemma"])[:14])
    run_dir = os.path.join(RUNS, tag)
    waves = []
    prev_output, err_codes = None, None
    outcome = "no_output"
    for wave in range(MAX_WAVES):
        wave_dir = os.path.join(run_dir, "wave%d" % wave)
        ptext = build_prompt_text(rb, row, wave, prev_output, err_codes)
        rc, wall, text = call_codex(ptext, wave_dir)
        if rc != 0 or not text:
            waves.append({"wave": wave, "rc": rc, "wall": round(wall, 2),
                          "outcome": "no_output", "errs": [], "rawLen": len(text)})
            outcome = "no_output"
            break
        oc, errs, detail = evaluate(cid, text)
        waves.append({"wave": wave, "rc": rc, "wall": round(wall, 2), "outcome": oc,
                      "errs": errs, "rawLen": len(text), "coerce": detail.get("coerce")})
        outcome = oc
        if oc in ("accepted", "abstain"):
            break            # both terminal (abstain -> QUARANTINED/ABSTAINED)
        # invalid or malformed -> repair with the REAL errs, if budget remains
        prev_output, err_codes = text, errs
        if wave == MAX_WAVES - 1:
            outcome = "quarantined"   # still invalid after R repairs
            break
    rec = {
        "idx": idx, "conceptId": cid, "lemma": row["lemma"], "pos": row["pos"],
        "finalOutcome": ("quarantined" if outcome == "invalid" else outcome),
        "firstWaveOutcome": waves[0]["outcome"] if waves else "no_output",
        "calls": len(waves), "waves": waves,
        "wallTotal": round(sum(w["wall"] for w in waves), 2),
    }
    sys.stderr.write("[%2d] %s %-16s -> %-11s calls=%d waves=%s\n" % (
        idx, row["pos"], row["lemma"][:16], rec["finalOutcome"], rec["calls"],
        ">".join(w["outcome"] for w in waves)))
    sys.stderr.flush()
    return rec


def summarize(recs):
    import statistics
    n = len(recs)
    # provider/no-output failures are excluded from the alpha denominator
    # (they are the provider_failed lane, not accept/quarantine).
    scored = [r for r in recs if r["finalOutcome"] != "no_output"]
    accepted = [r for r in scored if r["finalOutcome"] == "accepted"]
    abstained = [r for r in scored if r["finalOutcome"] == "abstain"]
    quarantined = [r for r in scored if r["finalOutcome"] == "quarantined"]
    no_output = [r for r in recs if r["finalOutcome"] == "no_output"]

    # concepts the model actually DRAFTED (not abstain, not no_output) at wave 0
    drafted_w0 = [r for r in recs if r["firstWaveOutcome"] in ("accepted", "invalid", "malformed")]
    first_pass_valid = [r for r in drafted_w0 if r["firstWaveOutcome"] == "accepted"]

    attempted = len(scored)                 # accepted + abstained + quarantined
    alpha_point = len(accepted) / attempted if attempted else 0.0
    alpha_lb = wilson_lower_bound(alpha_point, attempted)

    all_walls = sorted(w["wall"] for r in recs for w in r["waves"] if w["rc"] == 0)
    calls = [r["calls"] for r in recs]

    def p90(xs):
        if not xs: return None
        return xs[max(0, int(round(0.9 * (len(xs) - 1))))]

    return {
        "n": n,
        "outcomes": {"accepted": len(accepted), "abstain": len(abstained),
                     "quarantined": len(quarantined), "no_output": len(no_output)},
        # --- the two effects, separated ---
        "firstPassValid_amongAllN": len(first_pass_valid),
        "firstPassValid_rate_pct": round(100.0 * len(first_pass_valid) / n, 1),
        "firstPassValid_amongDrafted_pct": (
            round(100.0 * len(first_pass_valid) / len(drafted_w0), 1) if drafted_w0 else None),
        "draftedAtWave0": len(drafted_w0),
        "postRepairValid_count": len(accepted),
        "postRepairValid_rate_pct": round(100.0 * len(accepted) / n, 1),
        "abstentionRate_pct": round(100.0 * len(abstained) / n, 1),
        "invalidAfterR2_count": len(quarantined),
        # --- alpha (pilot's OWN definition: accepted/(accepted+quarantined),
        #     quarantined INCLUDES abstained; run_e2e.py:149-150) ---
        "alpha_point": round(alpha_point, 4),
        "alpha_LB_wilson95": round(alpha_lb, 4),
        "alpha_denominator_attempted": attempted,
        "alpha_floor": common.ALPHA_FLOOR,
        # --- yield among concepts the model chose to draft (isolates the
        #     invalid-token failure mode the prompt fix targets) ---
        "acceptedAmongDrafted": len(accepted) - 0,  # accepted are all drafted
        "meanCallsPerConcept": round(statistics.mean(calls), 2) if calls else None,
        "totalCalls": sum(calls),
        "wallPerCall": {"mean": round(statistics.mean(all_walls), 2) if all_walls else None,
                        "p90": p90(all_walls), "min": all_walls[0] if all_walls else None,
                        "max": all_walls[-1] if all_walls else None},
    }


def main():
    os.makedirs(RUNS, exist_ok=True)
    sel = json.load(open(os.path.join(OUT, "selected-repr.json")))
    rb = promptmod.RequestBuilder()
    evaluate._lemma = {r["conceptId"]: r["lemma"] for r in sel}
    sys.stderr.write("cachePrefixHash %s  prefixBytes %d  concepts %d  R=%d parallel=%d\n" % (
        rb.cache_prefix_hash[:16], len(rb.prefix_text), len(sel), R, MAX_PARALLEL))

    recs = [None] * len(sel)
    with cf.ThreadPoolExecutor(max_workers=MAX_PARALLEL) as ex:
        futs = {ex.submit(process_concept, i, row, rb): i for i, row in enumerate(sel)}
        for fut in cf.as_completed(futs):
            i = futs[fut]
            recs[i] = fut.result()
            json.dump([r for r in recs if r], open(os.path.join(OUT, "results.partial.json"), "w"), indent=1)

    summary = summarize(recs)
    json.dump({"summary": summary, "results": recs},
              open(os.path.join(OUT, "results.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
