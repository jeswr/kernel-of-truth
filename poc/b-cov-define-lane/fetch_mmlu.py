#!/usr/bin/env python3
"""Fetch MMLU biomedical-subject TEST items from the CANONICAL source (cais/mmlu,
MIT) via the HF datasets-server rows API (JSON; no parquet/pyarrow needed).

Scope pin (docs/design-kot-query-define-op.md §7.2 + docs/next/
benchmark-evaluation-strategy.md §1.2): the six definitional-MMLU biomedical
subjects. Split = test (the split lighteval scores; SmolLM2 cards report MMLU on
test). MEASURED-exploratory census input; sha256 of each written jsonl recorded
by the census (no registry write, no frozen HF-revision pin — exploratory).
Fail-closed: aborts on any HTTP/row-count mismatch rather than writing a partial
shard.
"""
import json, sys, time, hashlib, urllib.request, urllib.error, os

SUBJECTS = ["college_biology", "college_chemistry", "medical_genetics",
            "anatomy", "clinical_knowledge", "nutrition"]
SPLIT = "test"
OUTDIR = os.path.join(os.path.dirname(__file__), "data")
BASE = "https://datasets-server.huggingface.co/rows"


def fetch_page(cfg, offset, length):
    url = "%s?dataset=cais/mmlu&config=%s&split=%s&offset=%d&length=%d" % (
        BASE, cfg, SPLIT, offset, length)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("unreachable")


def main():
    manifest = {}
    for cfg in SUBJECTS:
        rows = []
        first = fetch_page(cfg, 0, 100)
        total = first["num_rows_total"]
        rows.extend(r["row"] for r in first["rows"])
        offset = len(first["rows"])
        while offset < total:
            page = fetch_page(cfg, offset, 100)
            got = page["rows"]
            if not got:
                break
            rows.extend(r["row"] for r in got)
            offset += len(got)
            time.sleep(0.3)
        if len(rows) != total:
            sys.exit("FAIL %s: got %d rows, expected %d (fail-closed)"
                     % (cfg, len(rows), total))
        # deterministic bytes: pinned source order, sorted keys per row
        path = os.path.join(OUTDIR, "mmlu-%s-%s.jsonl" % (cfg, SPLIT))
        buf = "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n"
                      for r in rows)
        with open(path, "w", encoding="utf-8") as f:
            f.write(buf)
        sha = hashlib.sha256(buf.encode("utf-8")).hexdigest()
        manifest[cfg] = {"path": os.path.basename(path), "n": len(rows),
                         "sha256": "sha256:" + sha}
        print("%-20s test n=%d sha256:%s" % (cfg, len(rows), sha[:16]))
    with open(os.path.join(OUTDIR, "mmlu-fetch-manifest.json"), "w") as f:
        json.dump({"source": "cais/mmlu", "license": "MIT", "split": SPLIT,
                   "api": "datasets-server.huggingface.co/rows",
                   "subjects": manifest}, f, indent=1, sort_keys=True)
    print("TOTAL", sum(v["n"] for v in manifest.values()))


if __name__ == "__main__":
    main()
