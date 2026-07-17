#!/usr/bin/env python3
"""driver.py -- codex-as-drafting-transport probe for the largekern-10k pilot.

For each selected concept: build the FROZEN drafting prompt (prompt.py prefix +
draft_suffix), invoke codex exec (run_codex_draft.sh), measure wall-clock, then
run the SAME acceptance stack the pipeline uses (accept.parse_output +
accept.lint_gloss + accept.validate_shards over the encoder). Emits hard numbers.

No network except codex's own subscription call. No git ops. Idempotent-ish:
each concept's raw codex artifacts are saved so parsing can be re-run offline.
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.abspath(os.path.join(HERE, "..", "pipeline"))
sys.path.insert(0, PIPE)
import prompt as promptmod          # noqa: E402
import accept                        # noqa: E402
import common                        # noqa: E402

OUT = os.path.join(HERE, "out")
RUNS = os.path.join(OUT, "runs")
os.makedirs(RUNS, exist_ok=True)

# Thin codex-transport framing: codex exec is an AGENTIC harness with its own
# system prompt, so (unlike a raw /v1/responses call) it must be told to behave
# as a pure text generator. This is the minimal adaptation any codex-transport
# adoption would use; whether output stays clean under it is exactly what we test.
TRANSPORT_PREAMBLE = (
    "You are acting purely as a text-generation model, NOT as a coding agent. "
    "Do NOT use any tools, do NOT read or write files, do NOT search, do NOT "
    "explain your reasoning. Follow the drafting contract below and respond with "
    "EXACTLY ONE JSON object per its OUTPUT PROTOCOL -- no code fences, no "
    "preamble, no trailing commentary. Your entire reply must be that JSON object.\n\n"
)


def build_prompt_text(rb, row):
    # Frozen contract: developer=prefix, user=draft_suffix (prompt.py). codex
    # takes a single stdin prompt, so concatenate with the transport preamble.
    return (TRANSPORT_PREAMBLE
            + "===== DRAFTING CONTRACT (developer) =====\n"
            + rb.prefix_text
            + "\n===== DRAFT TASK (user) =====\n"
            + promptmod.draft_suffix(row) + "\n")


def extract_text(last_message_path):
    """Pull the assistant's final text out of codex's -o last-message.json,
    tolerating either a raw string or a wrapped object."""
    with open(last_message_path, "r", encoding="utf-8") as f:
        raw = f.read()
    raw = raw.strip()
    if not raw:
        return ""
    try:
        obj = json.loads(raw)
    except ValueError:
        return raw  # already plain text
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        for k in ("last_agent_message", "message", "text", "content", "output_text"):
            v = obj.get(k)
            if isinstance(v, str):
                return v
            if isinstance(v, list):  # content blocks
                parts = [b.get("text", "") if isinstance(b, dict) else str(b) for b in v]
                return "".join(parts)
        return json.dumps(obj)
    return raw


_FENCE = re.compile(r"^```[a-zA-Z0-9]*\s*|\s*```$", re.MULTILINE)


def coerce_json_object(text):
    """Best-effort: strip fences, then extract the first balanced {...} object.
    Returns (json_text_or_None, coercion_note)."""
    t = text.strip()
    # try direct
    try:
        json.loads(t); return t, "direct"
    except ValueError:
        pass
    stripped = _FENCE.sub("", t).strip()
    try:
        json.loads(stripped); return stripped, "stripped_fences"
    except ValueError:
        pass
    # balanced-brace scan for the first top-level object
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


def main():
    sel = json.load(open(os.path.join(OUT, "selected.json")))
    rb = promptmod.RequestBuilder()
    wrapper = os.path.join(HERE, "run_codex_draft.sh")
    results = []
    valid_drafts = {}   # conceptId -> explication (for the shard validator)
    concept_lint = {}   # conceptId -> lint errs

    for idx, row in enumerate(sel):
        cid = row["conceptId"]
        tag = "%02d-%s-%s" % (idx, row["pos"], re.sub(r"[^A-Za-z0-9]", "", row["lemma"])[:12])
        run_dir = os.path.join(RUNS, tag)
        os.makedirs(run_dir, exist_ok=True)
        ptext = build_prompt_text(rb, row)
        ppath = os.path.join(run_dir, "prompt.txt")
        with open(ppath, "w", encoding="utf-8") as f:
            f.write(ptext)

        sys.stderr.write("[%2d/12] %s %-10s calling codex...\n" % (idx + 1, row["pos"], row["lemma"]))
        sys.stderr.flush()
        t0 = time.time()
        proc = subprocess.run(["bash", wrapper, ppath, run_dir],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        wall = time.time() - t0
        rc = proc.returncode
        stderr_tail = proc.stderr.decode("utf-8", "replace")[-400:]

        lm = os.path.join(run_dir, "last-message.json")
        text = extract_text(lm) if os.path.exists(lm) else ""
        with open(os.path.join(run_dir, "assistant-text.txt"), "w", encoding="utf-8") as f:
            f.write(text)

        jtext, coerce = coerce_json_object(text) if text else (None, "empty")
        kind, payload, lint_errs, validator = "no_output", None, [], None
        if jtext is not None:
            kind, payload = accept.parse_output(jtext)
            if kind == "draft":
                lint_errs = accept.lint_gloss(payload["gloss"], row["lemma"])
                valid_drafts[cid] = payload["explication"]
                concept_lint[cid] = lint_errs

        rec = {
            "idx": idx, "conceptId": cid, "lemma": row["lemma"], "pos": row["pos"],
            "wallSec": round(wall, 2), "rc": rc,
            "rawTextLen": len(text),
            "coercion": coerce, "cleanDirect": (coerce == "direct"),
            "parseKind": kind,
            "glossLintErrs": lint_errs,
            "cannotDraft": (payload if kind == "abstain" else None),
            "stderrTail": stderr_tail,
        }
        results.append(rec)
        sys.stderr.write("        wall=%.1fs rc=%d parse=%s coerce=%s lint=%s\n"
                         % (wall, rc, kind, coerce, lint_errs or "ok"))
        # persist incrementally
        json.dump(results, open(os.path.join(OUT, "results.partial.json"), "w"), indent=1)

    # ---- run the encoder/validator shard over all parsed 'draft' explications
    validator_per_id = {}
    if valid_drafts:
        sys.stderr.write("\nrunning encoder/validate_shard over %d parsed drafts...\n" % len(valid_drafts))
        per_id, reports = accept.validate_shards(valid_drafts)
        validator_per_id = {k: {"ok": v[0], "code": v[1]} for k, v in per_id.items()}

    # ---- fold validator result + compute PASS/FAIL (parse ok + no lint err + validator ok)
    for rec in results:
        cid = rec["conceptId"]
        v = validator_per_id.get(cid)
        rec["validator"] = v
        rec["acceptPass"] = bool(
            rec["parseKind"] == "draft" and not rec["glossLintErrs"] and v and v["ok"])

    summary = summarize(results)
    out = {"summary": summary, "results": results, "validatorPerId": validator_per_id}
    json.dump(out, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


def summarize(results):
    import statistics
    walls = sorted(r["wallSec"] for r in results if r["rc"] == 0)
    n = len(results)
    def frac(pred): return sum(1 for r in results if pred(r))
    parse_ok = frac(lambda r: r["parseKind"] in ("draft", "abstain"))
    draft_parse = frac(lambda r: r["parseKind"] == "draft")
    clean_direct = frac(lambda r: r["cleanDirect"])
    accept_pass = frac(lambda r: r["acceptPass"])
    abstain = frac(lambda r: r["parseKind"] == "abstain")
    val_ok = frac(lambda r: r.get("validator") and r["validator"]["ok"])
    def pct(x): return round(100.0 * x / n, 1)
    def p90(xs):
        if not xs: return None
        k = max(0, int(round(0.9 * (len(xs) - 1))))
        return xs[k]
    mean = round(statistics.mean(walls), 2) if walls else None
    p90v = p90(walls)
    serial_10k_hr = round(mean * 10000 / 3600.0, 1) if mean else None
    return {
        "n": n,
        "wall": {"mean": mean, "p90": p90v, "min": walls[0] if walls else None,
                 "max": walls[-1] if walls else None, "all_sorted": walls},
        "rc_nonzero": frac(lambda r: r["rc"] != 0),
        "parse_success_rate_pct": pct(parse_ok),
        "draft_parsed": draft_parse,
        "abstained": abstain,
        "clean_direct_json_count": clean_direct,
        "validator_ok_count": val_ok,
        "accept_pass_count": accept_pass,
        "accept_pass_rate_pct": pct(accept_pass),
        "serial_10k_hours_at_mean": serial_10k_hr,
    }


if __name__ == "__main__":
    main()
