#!/usr/bin/env python3
"""Haiku triage + structured-extraction pipeline for the lit-KB (N-C §2.3, build-step B3).

Phases (each checkpointed; reruns skip finished work):
  triage   batch Haiku scoring of kb/queue/candidates.jsonl title+abstracts
           against the FIXED rubric (kb/triage-rubric.md; prompt file
           tools/kb/prompts/triage-system.txt, sha256 pinned per result line)
           -> kb/queue/triage-results.jsonl
  fetch    full text for the read tier (triage score >=2, arXiv ids):
           arxiv.org/html -> ar5iv fallback -> abstract-only. Bytes cached in
           kb/cache/ (gitignored) via kb_common.http_get.
  extract  one Haiku call per read-tier paper with the pinned extraction
           prompt (tools/kb/prompts/extract-system.txt) -> kot-lit/1 record at
           kb/records/<id>.json. Identity/biblio come from the queue row
           MECHANICALLY (never from the model). evidence is forced "claimed"
           (N-C §0: KB records are recall infrastructure, NOT evidence).
  apply-status  rewrite queue rows: extracted / triaged (abstract tier) / skipped.

BILLING: subscription CLI (`claude -p`), NOT metered API. total_cost_usd from
the CLI result is the API-equivalent estimate; every call is logged to
kb/eval/haiku-usage.jsonl and the run aborts if the cumulative estimate
crosses --budget-usd (standing approval $200; default guard 190).

Model: claude-haiku-4-5-20251001 (N-C §2.3). Concurrency default 4
(<=5-agent / subscription-governor discipline; usage-limit errors stop the
run immediately with a named error, resumable).

Usage:
  nice -n 10 python3 tools/kb/extract_pipeline.py triage  [--limit N] [--batch 16]
  nice -n 10 python3 tools/kb/extract_pipeline.py fetch   [--limit N]
  nice -n 10 python3 tools/kb/extract_pipeline.py extract [--limit N] [--concurrency 4]
  python3 tools/kb/extract_pipeline.py apply-status
  python3 tools/kb/extract_pipeline.py status
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kb_common as K  # noqa: E402

MODEL = "claude-haiku-4-5-20251001"
PROMPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
TRIAGE_PROMPT = os.path.join(PROMPT_DIR, "triage-system.txt")
EXTRACT_PROMPT = os.path.join(PROMPT_DIR, "extract-system.txt")
TRIAGE_RESULTS = os.path.join(K.KB_DIR, "queue", "triage-results.jsonl")
USAGE_LOG = os.path.join(K.KB_DIR, "eval", "haiku-usage.jsonl")
DROPPED_LOG = os.path.join(K.KB_DIR, "eval", "extract-demotions.jsonl")
FAIL_LOG = os.path.join(K.KB_DIR, "eval", "extract-failures.jsonl")
FULLTEXT_DIR = os.path.join(K.CACHE_DIR, "fulltext")
FULLTEXT_MAX_CHARS = 40000
SEAM_CELLS = ("text", "own-activations", "trained-bridge", "external-engine",
              "raw-foreign-coords", "none")

# polite intervals for the fulltext hosts (kb_common only pins the API hosts)
K._HOST_MIN_INTERVAL.setdefault("arxiv.org", 3.05)
K._HOST_MIN_INTERVAL.setdefault("ar5iv.labs.arxiv.org", 3.05)

_usage_lock = threading.Lock()
_spend = {"usd": 0.0, "calls": 0}


class UsageLimit(RuntimeError):
    pass


def _sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_spend():
    total = 0.0
    calls = 0
    for row in K.read_jsonl(USAGE_LOG):
        total += float(row.get("cost_usd") or 0.0)
        calls += 1
    _spend["usd"], _spend["calls"] = total, calls


def _log_usage(phase, ref, out, budget):
    cost = float(out.get("total_cost_usd") or 0.0)
    usage = out.get("usage") or {}
    with _usage_lock:
        _spend["usd"] += cost
        _spend["calls"] += 1
        K.append_jsonl(USAGE_LOG, {
            "at": _now(), "phase": phase, "ref": ref, "model": MODEL,
            "cost_usd": cost,
            "input_tokens": usage.get("input_tokens"),
            "cache_creation_input_tokens": usage.get("cache_creation_input_tokens"),
            "cache_read_input_tokens": usage.get("cache_read_input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "cumulative_usd": round(_spend["usd"], 4),
        })
        if _spend["usd"] > budget:
            raise UsageLimit("ERR_KB_BUDGET: cumulative est spend $%.2f > budget $%.2f — STOPPING"
                             % (_spend["usd"], budget))


def call_claude(system_file, user_text, budget, phase, ref, attempts=3, timeout_s=420):
    env = dict(os.environ, MAX_THINKING_TOKENS="0")
    cmd = ["nice", "-n", "10", "claude", "-p", "--model", MODEL,
           "--system-prompt-file", system_file, "--tools", "",
           "--strict-mcp-config", "--exclude-dynamic-system-prompt-sections",
           "--effort", "low", "--output-format", "json", "--max-turns", "1"]
    last = None
    for attempt in range(attempts):
        try:
            r = subprocess.run(cmd, input=user_text, capture_output=True,
                               text=True, env=env, timeout=timeout_s)
        except subprocess.TimeoutExpired:
            last = "claude timeout after %ss" % timeout_s
            time.sleep(5 * 3 ** attempt)
            continue
        if r.returncode == 0:
            try:
                out = json.loads(r.stdout)
            except Exception:
                last = "unparseable stdout: %r" % (r.stdout or "")[:200]
                time.sleep(5 * 3 ** attempt)
                continue
            if not out.get("is_error"):
                _log_usage(phase, ref, out, budget)
                return out.get("result") or ""
            blob = r.stdout
        else:
            blob = (r.stdout or "") + (r.stderr or "")
        if re.search(r"usage limit|session limit|limit reached|out of.*(quota|credits)|5-hour", blob, re.I):
            raise UsageLimit(blob[:800])
        if re.search(r"rate.?limit|overloaded|too many requests|429", blob, re.I):
            time.sleep(30 * (attempt + 1))
            last = "rate-limited"
            continue
        last = "claude exit %s: %r" % (r.returncode, blob[:300])
        time.sleep(5 * 3 ** attempt)
    raise RuntimeError(last)


def parse_json_reply(text):
    """Model replies are raw JSON, but strip fences defensively."""
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    # tolerate leading/trailing prose by locating the outermost bracket pair
    for opener, closer in (("[", "]"), ("{", "}")):
        a, b = t.find(opener), t.rfind(closer)
        if a != -1 and b > a:
            try:
                return json.loads(t[a:b + 1])
            except json.JSONDecodeError:
                continue
    return json.loads(t)  # raise with the original error


# ------------------------------------------------------------------- triage

def run_triage(args):
    rows = K.read_jsonl(K.QUEUE_PATH)
    done = {r["id"] for r in K.read_jsonl(TRIAGE_RESULTS)}
    todo = [r for r in rows if r["id"] not in done]
    if args.limit:
        todo = todo[: args.limit]
    prompt_sha = _sha256_file(TRIAGE_PROMPT)
    batches = [todo[i:i + args.batch] for i in range(0, len(todo), args.batch)]
    print("triage: %d candidates to score in %d batches (batch=%d, conc=%d)"
          % (len(todo), len(batches), args.batch, args.concurrency), flush=True)

    def one_batch(batch):
        lines = []
        for i, row in enumerate(batch):
            lines.append("PAPER %d\nID: %s\nTITLE: %s\nABSTRACT: %s\n"
                         % (i + 1, row["id"], row.get("title") or "[none]",
                            (row.get("abstract") or "[none]")[:2500]))
        user = ("Score the following %d papers per the rubric. Reply with the JSON array only.\n\n%s"
                % (len(batch), "\n".join(lines)))
        reply = call_claude(TRIAGE_PROMPT, user, args.budget_usd, "triage",
                            batch[0]["id"] + "+%d" % len(batch))
        arr = parse_json_reply(reply)
        by_id = {}
        if isinstance(arr, list):
            for item in arr:
                if isinstance(item, dict) and item.get("id"):
                    by_id[str(item["id"]).strip()] = item
        out = []
        for row in batch:
            item = by_id.get(row["id"])
            if item is None or not isinstance(item.get("score"), int) or not 0 <= item["score"] <= 3:
                out.append((row["id"], None))
                continue
            out.append((row["id"], {
                "id": row["id"], "triage_score": item["score"],
                "reason": str(item.get("reason") or "")[:400],
                "model": MODEL, "prompt_sha256": prompt_sha, "at": _now(),
                "schema_version": "kot-lit-triage/1",
            }))
        return out

    missed = 0
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = {ex.submit(one_batch, b): b for b in batches}
        done_n = 0
        for fut in as_completed(futs):
            for rid, res in fut.result():
                if res is None:
                    missed += 1
                else:
                    with _usage_lock:
                        K.append_jsonl(TRIAGE_RESULTS, res)
            done_n += 1
            if done_n % 5 == 0:
                print("triage: %d/%d batches, est $%.2f" % (done_n, len(batches), _spend["usd"]), flush=True)
    print("triage: done; %d unresolved (rerun to retry them); est cumulative $%.2f over %d calls"
          % (missed, _spend["usd"], _spend["calls"]), flush=True)


# -------------------------------------------------------------------- fetch

class _TextExtractor(HTMLParser):
    SKIP = {"script", "style", "svg", "math", "annotation", "nav", "header", "button"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip_depth += 1
        elif tag in ("p", "div", "section", "h1", "h2", "h3", "h4", "li", "tr", "figcaption", "br"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            self.parts.append(data)


def html_to_text(raw_bytes):
    p = _TextExtractor()
    try:
        p.feed(raw_bytes.decode("utf-8", errors="replace"))
    except Exception:
        return None
    text = "".join(p.parts)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def fulltext_path(rec_id):
    return os.path.join(FULLTEXT_DIR, rec_id.replace(":", "_").replace("/", "_") + ".txt")


def fetch_fulltext(row):
    """-> (text, source_url) or (None, None). Cached at kb/cache/fulltext/."""
    fp = fulltext_path(row["id"])
    meta_fp = fp + ".meta.json"
    if os.path.exists(fp) and os.path.exists(meta_fp):
        with open(fp, "r", encoding="utf-8") as f:
            txt = f.read()
        with open(meta_fp, "r", encoding="utf-8") as f:
            return (txt or None), json.load(f).get("url")
    if not row.get("arxiv"):
        return None, None
    os.makedirs(FULLTEXT_DIR, exist_ok=True)
    for url in ("https://arxiv.org/html/%s" % row["arxiv"],
                "https://ar5iv.labs.arxiv.org/html/%s" % row["arxiv"]):
        try:
            raw, _ = K.http_get(url, max_tries=2)
        except K.KotError:
            continue
        text = html_to_text(raw)
        # ar5iv serves a stub page for unconverted papers; demand real body text
        if text and len(text) > 5000 and "conversion failed" not in text[:2000].lower():
            with open(fp, "w", encoding="utf-8") as f:
                f.write(text)
            with open(meta_fp, "w", encoding="utf-8") as f:
                json.dump({"url": url, "sha256": K.sha256_hex(raw), "at": _now()}, f)
            return text, url
    with open(fp, "w", encoding="utf-8") as f:
        f.write("")
    with open(meta_fp, "w", encoding="utf-8") as f:
        json.dump({"url": None, "at": _now()}, f)
    return None, None


def read_tier(min_score=2):
    scores = {}
    for r in K.read_jsonl(TRIAGE_RESULTS):
        scores[r["id"]] = r  # last line wins
    rows = K.read_jsonl(K.QUEUE_PATH)
    tier = [r for r in rows if scores.get(r["id"], {}).get("triage_score", -1) >= min_score]
    return tier, scores


def run_fetch(args):
    tier, _ = read_tier()
    todo = [r for r in tier if r.get("arxiv") and not os.path.exists(fulltext_path(r["id"]) + ".meta.json")]
    if args.limit:
        todo = todo[: args.limit]
    print("fetch: %d read-tier papers to fetch (of %d in tier)" % (len(todo), len(tier)), flush=True)
    got = 0
    for i, row in enumerate(todo):
        text, url = fetch_fulltext(row)
        got += 1 if text else 0
        if (i + 1) % 20 == 0:
            print("fetch: %d/%d (%d with fulltext)" % (i + 1, len(todo), got), flush=True)
    print("fetch: done; %d/%d with fulltext" % (got, len(todo)), flush=True)


# ------------------------------------------------------------------ extract

def _norm_tag(t):
    t = re.sub(r"[^a-z0-9-]+", "-", str(t).lower()).strip("-")
    return re.sub(r"-{2,}", "-", t)


def _num_or_none(v):
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def sanitise_extraction(rec_id, ext):
    """Mechanical coercion of the model JSON into the kot-lit/1 extractable
    subset. Anything that cannot be coerced honestly is dropped and logged."""
    arch = ext.get("architecture") or {}
    seam = arch.get("seam_cell")
    if seam not in SEAM_CELLS:
        raise ValueError("bad seam_cell %r" % (seam,))
    architecture = {
        "summary": str(arch.get("summary") or "").strip(),
        "seam_cell": seam,
        "trained_components": [str(x) for x in (arch.get("trained_components") or [])],
        "frozen_components": [str(x) for x in (arch.get("frozen_components") or [])],
        "mechanism_tags": [t for t in (_norm_tag(x) for x in (arch.get("mechanism_tags") or [])) if t],
    }
    if not architecture["summary"]:
        raise ValueError("empty architecture.summary")
    claims = []
    demotions = []
    for c in (ext.get("claims") or [])[:8]:
        if not isinstance(c, dict) or not str(c.get("statement") or "").strip():
            continue
        ctype = c.get("type")
        if ctype not in ("quantitative", "qualitative", "negative", "theoretical"):
            ctype = "qualitative"
        metric = c.get("metric") if isinstance(c.get("metric"), str) else None
        value = _num_or_none(c.get("value"))
        dataset = c.get("dataset") if isinstance(c.get("dataset"), str) else None
        if ctype == "quantitative" and (metric is None or value is None or dataset is None):
            # Law-2: a number without its anchors is a decoration — demote, log.
            demotions.append({"id": rec_id, "statement": str(c["statement"])[:300],
                              "missing": [f for f, v in (("metric", metric), ("value", value),
                                                         ("dataset", dataset)) if v is None],
                              "at": _now()})
            ctype = "qualitative"
            metric = value = dataset = None
        baseline = c.get("baseline")
        if isinstance(baseline, dict) and baseline.get("name"):
            baseline = {"name": str(baseline["name"]), "value": _num_or_none(baseline.get("value"))}
        else:
            baseline = None
        scale = c.get("scale")
        if isinstance(scale, dict):
            scale = {"params": _num_or_none(scale.get("params")),
                     "rungs_measured": scale.get("rungs_measured")
                     if isinstance(scale.get("rungs_measured"), int) and scale["rungs_measured"] >= 0 else None}
            if scale["params"] is None and scale["rungs_measured"] is None:
                scale = None
        else:
            scale = None
        claims.append({
            "claim_id": "c%d" % (len(claims) + 1),
            "type": ctype,
            "statement": str(c["statement"]).strip(),
            "metric": metric, "value": value,
            "unit": c.get("unit") if isinstance(c.get("unit"), str) else None,
            "baseline": baseline, "dataset": dataset, "scale": scale,
            "compute_reported": bool(c.get("compute_reported")),
            # N-C §0 THE HONESTY BOUNDARY: extraction can never mint evidence.
            "evidence": "claimed",
            "evidence_ref": None,
        })
    repro = ext.get("reproduction") or {}
    reproduction = {
        "code_url": repro.get("code_url") if isinstance(repro.get("code_url"), str) else None,
        "weights_url": repro.get("weights_url") if isinstance(repro.get("weights_url"), str) else None,
    }
    return architecture, claims, reproduction, demotions


def build_record(row, architecture, claims, reproduction, prompt_sha, source_scope):
    rec = {
        "schema_version": "kot-lit/1",
        "id": row["id"],
        "identity": {
            "doi": row.get("doi"),
            "arxiv": row.get("arxiv"),
            "openalex": row.get("openalex"),
            "s2": row.get("s2"),
            "pdf_sha256": None,
        },
        "biblio": {
            "title": row.get("title"),
            "authors": row.get("authors") or [],
            "year": row.get("year"),
            "venue": row.get("venue"),
        },
        "architecture": architecture,
        "claims": claims,
        # N-C §2.3 step 3: relation pass is a FABLE judgement pass, run after
        # extraction; Haiku never writes these fields.
        "relation_to_kernel": {"hypotheses": [], "ledger_refs": [], "seams": [], "note": None},
        "reproduction": reproduction,
        "provenance": {
            "extractor_model": MODEL,
            "prompt_sha256": prompt_sha,
            "extracted_at": _now(),
            "source_scope": source_scope,
            "audit": {"state": "UNAUDITED", "by": None},
        },
    }
    if isinstance(row.get("citation_count"), dict):
        cc = row["citation_count"]
        if isinstance(cc.get("value"), int) and cc.get("as_of") and cc.get("source"):
            rec["biblio"]["citation_count"] = {"value": cc["value"], "as_of": cc["as_of"],
                                               "source": cc["source"]}
    rec["record_sha256"] = K.record_hash(rec)
    return rec


def run_extract(args):
    schema = K.load_schema("kot-lit-1.json")
    prompt_sha = _sha256_file(EXTRACT_PROMPT)
    tier, scores = read_tier()
    todo = [r for r in tier if not os.path.exists(K.record_path(r["id"]))]
    if args.no_arxiv_only:
        todo = [r for r in todo if not r.get("arxiv")]
    if args.limit:
        todo = todo[: args.limit]
    print("extract: %d read-tier papers to extract (tier=%d, already done=%d, conc=%d)"
          % (len(todo), len(tier), len(tier) - len(todo), args.concurrency), flush=True)

    def one(row):
        text, url = fetch_fulltext(row)
        scope = "fulltext" if text else "abstract-only"
        body = "TITLE: %s\nAUTHORS: %s\nYEAR: %s\nVENUE: %s\n\nABSTRACT:\n%s\n" % (
            row.get("title"), ", ".join(row.get("authors") or [])[:400], row.get("year"),
            row.get("venue"), row.get("abstract") or "[none]")
        if text:
            body += "\nFULL TEXT (excerpt, HTML-derived):\n%s\n" % text[:FULLTEXT_MAX_CHARS]
        body += "\nEmit the kot-lit/1 extraction JSON object for this paper now."
        last_err = None
        for attempt in range(2):
            reply = call_claude(EXTRACT_PROMPT, body, args.budget_usd, "extract", row["id"])
            try:
                ext = parse_json_reply(reply)
                architecture, claims, reproduction, demotions = sanitise_extraction(row["id"], ext)
                rec = build_record(row, architecture, claims, reproduction, prompt_sha, scope)
                errs = K.validate_schema(rec, schema)
                if errs:
                    raise ValueError("schema: %s" % "; ".join(errs))
                for d in demotions:
                    with _usage_lock:
                        K.append_jsonl(DROPPED_LOG, d)
                K.write_canonical_json(K.record_path(row["id"]), rec)
                return "ok", scope
            except (ValueError, json.JSONDecodeError, KeyError) as e:
                last_err = str(e)
                body_extra = ("\nYOUR PREVIOUS REPLY WAS REJECTED by the mechanical validator: %s\n"
                              "Reply again with ONLY the corrected raw JSON object." % last_err[:300])
                body = body + body_extra
        with _usage_lock:
            K.append_jsonl(FAIL_LOG, {"id": row["id"], "error": last_err[:400], "at": _now()})
        return "fail", scope

    ok = fail = 0
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = {ex.submit(one, r): r["id"] for r in todo}
        for i, fut in enumerate(as_completed(futs)):
            status, scope = fut.result()
            ok += status == "ok"
            fail += status == "fail"
            if (i + 1) % 10 == 0:
                print("extract: %d/%d (ok=%d fail=%d) est $%.2f"
                      % (i + 1, len(todo), ok, fail, _spend["usd"]), flush=True)
    print("extract: done ok=%d fail=%d; est cumulative $%.2f over %d calls"
          % (ok, fail, _spend["usd"], _spend["calls"]), flush=True)


# --------------------------------------------------------------- apply-status

def run_apply_status(args):
    _, scores = read_tier()
    rows = K.read_jsonl(K.QUEUE_PATH)
    counts = {"extracted": 0, "triaged": 0, "skipped": 0, "queued": 0}
    for row in rows:
        s = scores.get(row["id"], {}).get("triage_score")
        if s is not None:
            row["triage_score"] = s
        if os.path.exists(K.record_path(row["id"])):
            row["status"] = "extracted"
        elif s is None:
            row["status"] = "queued"
        elif s >= 2:
            row["status"] = "queued"   # read tier awaiting extraction
        elif s == 1:
            row["status"] = "triaged"  # abstract tier: chunk only, no record
        else:
            row["status"] = "skipped"
        counts[row["status"]] += 1
    tmp = K.QUEUE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(K.canonical_dumps(row) + "\n")
    os.replace(tmp, K.QUEUE_PATH)
    print("apply-status: %s" % counts, flush=True)


def run_status(args):
    _load_spend()
    results = K.read_jsonl(TRIAGE_RESULTS)
    from collections import Counter
    c = Counter(r["triage_score"] for r in results)
    nrec = len([f for f in os.listdir(K.RECORDS_DIR) if f.endswith(".json")]) if os.path.isdir(K.RECORDS_DIR) else 0
    print("triage results: %d  score-dist: %s" % (len(results), dict(sorted(c.items()))))
    print("paper records:  %d" % nrec)
    print("spend estimate: $%.2f over %d subscription calls (budget ceiling per standing approval: $200)"
          % (_spend["usd"], _spend["calls"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["triage", "fetch", "extract", "apply-status", "status"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--budget-usd", type=float, default=190.0)
    ap.add_argument("--no-arxiv-only", action="store_true",
                    help="extract only papers without an arXiv id (no HTTP; safe while fetch runs)")
    args = ap.parse_args()
    _load_spend()
    if args.budget_usd > 200:
        print("budget ceiling is $200 (standing approval); refusing", file=sys.stderr)
        return 2
    os.makedirs(os.path.join(K.KB_DIR, "eval"), exist_ok=True)
    try:
        {"triage": run_triage, "fetch": run_fetch, "extract": run_extract,
         "apply-status": run_apply_status, "status": run_status}[args.phase](args)
    except UsageLimit as e:
        print("USAGE-LIMIT/BUDGET STOP: %s" % str(e)[:500], file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
