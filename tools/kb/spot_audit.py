#!/usr/bin/env python3
"""Codex spot-audit of Haiku-extracted kot-lit/1 records (N-C §2.3 step 5).

Extends the run!=audit discipline to KB construction: a cross-vendor model
(Codex / GPT-5.x via `codex exec`) re-checks a deterministic ~5% sample
(min 5) of extracted records against the SAME source text the extractor saw
(kb/cache/fulltext/... or the queue abstract). Field-level check of
architecture.seam_cell + claims[] (statement fidelity, metric/value/dataset,
baseline, invented numbers).

Outputs:
  kb/eval/spot-audit-<date>.json            the audit record (verbatim verdicts)
  provenance.audit on each sampled record   -> SPOT-CONFIRMED / SPOT-REFUTED,
                                            by "auditor-1" (RT-14 pseudonym);
                                            record_sha256 recomputed.

Sampling is deterministic: sha256(record_id + SALT), lowest digests first,
so the sample is reproducible from the record set alone.

Usage: python3 tools/kb/spot_audit.py [--frac 0.05] [--min 5] [--apply]
"""

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kb_common as K  # noqa: E402

SALT = "kot-lit-spot-audit-2026-07-09"
AUDITOR = "auditor-1"
FULLTEXT_DIR = os.path.join(K.CACHE_DIR, "fulltext")
SOURCE_MAX_CHARS = 40000  # same excerpt bound the extractor used

PROMPT = """You are an adversarial extraction auditor. Below is (1) the SOURCE text of a paper (title/abstract, possibly a full-text excerpt) and (2) a STRUCTURED RECORD another model extracted from that exact source. Your job is fidelity checking ONLY: does the record faithfully restate what the source says? You do not judge the paper.

Check, against the source text only:
- architecture.seam_cell: is the classification defensible given the definitions? (text = only tokens cross the model boundary; own-activations = model's own hidden states/KV read or written; trained-bridge = trained projector/adapter/prefix maps an external representation in; external-engine = external symbolic/retrieval/verifier engine returns text/scores; raw-foreign-coords = untrained foreign vectors injected directly; none = no model-boundary mechanism.)
- architecture.summary: mechanism-level faithful, no invention?
- each claim: statement traceable to the source (verbatim or near)? metric/value/dataset actually stated in the source with those values? baseline correct? any number NOT present in the source (invention) is a REFUTE.
- reproduction URLs: stated in source?

Minor paraphrase, rounding stated by the source itself, and omission of non-load-bearing detail are OK. Wrong numbers, invented datasets/metrics, wrong baseline direction, or an indefensible seam_cell are NOT.

Reply with ONLY a raw JSON object (no fences):
{"record_id": "...", "verdict": "CONFIRMED" | "REFUTED",
 "field_findings": [{"field": "claims[c1].value" , "ok": true|false, "note": "<short>"}],
 "note": "<one or two sentences>"}
Use verdict REFUTED only for material infidelity (wrong/invented quantitative field, indefensible seam_cell, fabricated URL); otherwise CONFIRMED with the issues noted.

=== SOURCE TEXT ===
%s

=== EXTRACTED RECORD (architecture, claims, reproduction only) ===
%s
"""


def deterministic_sample(ids, frac, min_n):
    ranked = sorted(ids, key=lambda i: hashlib.sha256((SALT + i).encode()).hexdigest())
    n = max(min_n, int(round(frac * len(ids))))
    return ranked[: min(n, len(ids))]


def source_text_for(rec_id, queue_by_id):
    fp = os.path.join(FULLTEXT_DIR, rec_id.replace(":", "_").replace("/", "_") + ".txt")
    row = queue_by_id.get(rec_id, {})
    head = "TITLE: %s\nYEAR: %s\n\nABSTRACT:\n%s\n" % (
        row.get("title"), row.get("year"), row.get("abstract") or "[none]")
    if os.path.exists(fp):
        with open(fp, "r", encoding="utf-8") as f:
            t = f.read()
        if t.strip():
            return head + "\nFULL TEXT (excerpt):\n" + t[:SOURCE_MAX_CHARS]
    return head


def codex_audit(rec_id, source, record_subset, timeout_s=600):
    prompt = PROMPT % (source, json.dumps(record_subset, indent=1, sort_keys=True))
    with tempfile.NamedTemporaryFile("r", suffix=".txt", delete=False) as outf:
        out_path = outf.name
    try:
        r = subprocess.run(
            ["nice", "-n", "10", "codex", "exec", "--sandbox", "read-only",
             "--skip-git-repo-check", "--ephemeral", "--color", "never",
             "-o", out_path, "-"],
            input=prompt, capture_output=True, text=True, timeout=timeout_s,
            cwd=K.REPO_ROOT,
        )
        with open(out_path, "r", encoding="utf-8") as f:
            last = f.read().strip()
    finally:
        try:
            os.unlink(out_path)
        except OSError:
            pass
    if not last:
        raise RuntimeError("codex produced no last message (exit %s): %s"
                           % (r.returncode, (r.stderr or "")[:300]))
    t = last
    a, b = t.find("{"), t.rfind("}")
    if a == -1 or b <= a:
        raise RuntimeError("codex reply not JSON: %r" % t[:200])
    return json.loads(t[a:b + 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frac", type=float, default=0.05)
    ap.add_argument("--min", type=int, default=5)
    ap.add_argument("--apply", action="store_true",
                    help="write audit state back into sampled records")
    ap.add_argument("--ids", nargs="*", help="audit exactly these record ids")
    args = ap.parse_args()

    schema = K.load_schema("kot-lit-1.json")
    rec_files = sorted(f for f in os.listdir(K.RECORDS_DIR) if f.endswith(".json"))
    records = {}
    for name in rec_files:
        with open(os.path.join(K.RECORDS_DIR, name), "r", encoding="utf-8") as f:
            rec = json.load(f)
        records[rec["id"]] = rec
    queue_by_id = {r["id"]: r for r in K.read_jsonl(K.QUEUE_PATH)}
    sample = args.ids or deterministic_sample(sorted(records), args.frac, args.min)
    print("spot-audit: %d records sampled of %d (frac=%s min=%d)"
          % (len(sample), len(records), args.frac, args.min), flush=True)

    results = []
    for i, rid in enumerate(sample):
        rec = records[rid]
        subset = {"id": rid,
                  "architecture": rec["architecture"],
                  "claims": rec["claims"],
                  "reproduction": rec["reproduction"]}
        try:
            res = codex_audit(rid, source_text_for(rid, queue_by_id), subset)
            res["record_id"] = rid  # trust our id, not the model's echo
            res.setdefault("verdict", "REFUTED")
        except (RuntimeError, json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            res = {"record_id": rid, "verdict": "ERROR", "note": str(e)[:300]}
        results.append(res)
        print("spot-audit: %d/%d %s -> %s" % (i + 1, len(sample), rid, res["verdict"]), flush=True)

    date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    audit_doc = {
        "schema_version": "kot-lit-audit/1",
        "at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "auditor_backend": "codex exec (cross-vendor, subscription CLI)",
        "auditor_pseudonym": AUDITOR,
        "sample_rule": "sha256('%s'+id) ascending; frac=%s min=%d over %d records"
                       % (SALT, args.frac, args.min, len(records)),
        "results": results,
        "summary": {
            "confirmed": sum(r["verdict"] == "CONFIRMED" for r in results),
            "refuted": sum(r["verdict"] == "REFUTED" for r in results),
            "error": sum(r["verdict"] == "ERROR" for r in results),
        },
    }
    out_path = os.path.join(K.KB_DIR, "eval", "spot-audit-%s.json" % date)
    K.write_canonical_json(out_path, audit_doc)
    print("spot-audit: wrote %s summary=%s" % (out_path, audit_doc["summary"]), flush=True)

    if args.apply:
        for res in results:
            if res["verdict"] not in ("CONFIRMED", "REFUTED"):
                continue
            rec = records[res["record_id"]]
            rec["provenance"]["audit"] = {
                "state": "SPOT-CONFIRMED" if res["verdict"] == "CONFIRMED" else "SPOT-REFUTED",
                "by": AUDITOR,
            }
            rec["record_sha256"] = K.record_hash(rec)
            errs = K.validate_schema(rec, schema)
            if errs:
                print("ERR: %s fails schema after audit write: %s" % (res["record_id"], errs),
                      file=sys.stderr)
                return 1
            K.write_canonical_json(K.record_path(res["record_id"]), rec)
        print("spot-audit: audit states applied to %d records"
              % sum(r["verdict"] in ("CONFIRMED", "REFUTED") for r in results), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
