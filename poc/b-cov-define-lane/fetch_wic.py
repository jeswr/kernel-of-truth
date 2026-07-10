#!/usr/bin/env python3
"""Fetch the WiC dev split from a VERIFIED-FAITHFUL DISCLOSED MIRROR for the
b-cov define-lane census WiC cell (bead kernel-of-truth-hu10).

DISCLOSED-MIRROR provenance (census-local; NOT a change to the programme
fail-closed sourcing policy in data/d-ext/manifest.json):
  * canonical pre-declared source = `pilehvar/wic` (HTTP 401 gated, unavailable).
  * mirror USED HERE = `aps/super_glue` config `wic` (SuperGLUE's incorporation of
    the Word-in-Context dataset, Pilehvar & Camacho-Collados 2019). SuperGLUE
    (Wang et al. 2019) bundles the WiC dataset itself; same items, same task, same
    labels. Public, CC BY 4.0 for the SuperGLUE packaging (WiC data CC BY-NC 4.0).
  * revision pinned: repo commit sha + parquet-convert sha recorded below.
  * EXPLICIT CAVEAT: exploratory mirror, NOT the canonical pilehvar/wic source.

Faithfulness was VERIFIED before selection (evidence echoed into the manifest):
  * dev/validation split == 638 items (the canonical WiC dev count).
  * schema == {word, sentence1, sentence2, start1, start2, end1, end2, idx, label},
    exactly the WiC spec; label is ClassLabel names ["False","True"] (0=False /
    different sense, 1=True / same sense).
  * dev label balance 319/319 (WiC dev is 50/50 by construction).
  * target-word offsets [startK:endK] recover the target lemma in both sentences
    (632/638 exact; the 6 "mismatches" are legitimate inflections buy/bought,
    leave/left, keep/kept, shake/shook, catch/caught — exactly WiC's inflected
    target usage), verified again at fetch time (fail-closed).
  * idx 0..2 dev items == the canonical WiC dev items (class / stripe / check).

Fail-closed: aborts on any HTTP / row-count / schema / offset mismatch rather than
writing a partial or non-faithful shard. Split = validation (dev) — the public
labelled WiC evaluation split (test labels are hidden, -1).
"""
import json, sys, time, hashlib, urllib.request, urllib.error, os

DATASET = "aps/super_glue"
CONFIG = "wic"
SPLIT = "validation"
EXPECT_N = 638
CANONICAL_SOURCE = "pilehvar/wic"
OUTDIR = os.path.join(os.path.dirname(__file__), "data")
ROWS = "https://datasets-server.huggingface.co/rows"
REFS = "https://huggingface.co/api/datasets/%s/refs" % DATASET
EXPECT_SCHEMA = ["word", "sentence1", "sentence2", "start1", "start2",
                 "end1", "end2", "idx", "label"]


def _get_json(url, timeout=40):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("unreachable")


def fetch_page(offset, length):
    url = "%s?dataset=%s&config=%s&split=%s&offset=%d&length=%d" % (
        ROWS, DATASET, CONFIG, SPLIT, offset, length)
    return _get_json(url)


def main():
    # revision pin (fail-closed on unavailable)
    refs = _get_json(REFS)
    main_sha = next(b["targetCommit"] for b in refs["branches"]
                    if b["name"] == "main")
    parquet_sha = next((c["targetCommit"] for c in refs.get("converts", [])
                        if c["name"] == "parquet"), None)

    rows = []
    first = fetch_page(0, 100)
    total = first["num_rows_total"]
    if total != EXPECT_N:
        sys.exit("FAIL: WiC %s split has %d rows, expected %d (fail-closed)"
                 % (SPLIT, total, EXPECT_N))
    rows.extend(r["row"] for r in first["rows"])
    offset = len(first["rows"])
    while offset < total:
        page = fetch_page(offset, 100)
        got = page["rows"]
        if not got:
            break
        rows.extend(r["row"] for r in got)
        offset += len(got)
        time.sleep(0.3)
    if len(rows) != total:
        sys.exit("FAIL: got %d rows, expected %d (fail-closed)"
                 % (len(rows), total))

    # schema check (fail-closed)
    for r in rows:
        if sorted(r.keys()) != sorted(EXPECT_SCHEMA):
            sys.exit("FAIL: row schema %s != expected %s (fail-closed)"
                     % (sorted(r.keys()), sorted(EXPECT_SCHEMA)))

    # label semantics + balance (fail-closed on unexpected label value)
    label_counts = {0: 0, 1: 0}
    for r in rows:
        lab = r["label"]
        if lab not in (0, 1):
            sys.exit("FAIL: dev label %r not in {0,1} (fail-closed)" % lab)
        label_counts[lab] += 1

    # offset -> target-lemma recovery check. WiC offsets mark the target word's
    # occurrence, which may be an IRREGULAR inflection (buy/bought, catch/caught)
    # where no shared char-prefix survives. Fail-closed on STRUCTURAL corruption
    # (out-of-bounds / empty / multi-token span), not on legitimate inflection;
    # require a high exact-recovery rate as positive faithfulness evidence.
    offset_exact = 0
    inflected = []
    for r in rows:
        w = r["word"].lower()
        for si, (sk, stk, etk) in enumerate(
                [("sentence1", "start1", "end1"), ("sentence2", "start2", "end2")]):
            s, a, b = r[sk], r[stk], r[etk]
            if not (0 <= a < b <= len(s)):
                sys.exit("FAIL: offsets word=%r %s [%d:%d] out of bounds (fail-closed)"
                         % (r["word"], sk, a, b))
            span = s[a:b]
            if (not span.strip()) or (" " in span):
                sys.exit("FAIL: offsets word=%r %s recover non-token %r (fail-closed)"
                         % (r["word"], sk, span))
        s1 = r["sentence1"][r["start1"]:r["end1"]].lower()
        s2 = r["sentence2"][r["start2"]:r["end2"]].lower()
        if s1 == w and s2 == w:
            offset_exact += 1
        # lemma consistency: the recovered span shares a 3-char lemma prefix with
        # the target word in BOTH sentences (covers regular inflection brush ->
        # brushes / minister -> ministers). Irregulars (buy -> bought) fail this
        # and are recorded separately after a plausible-inflection sanity gate.
        p = w[:3]
        if s1[:3] == p and s2[:3] == p:
            pass  # lemma-consistent
        else:
            # must still be a plausible inflection: single alpha token sharing the
            # target's first character in both sentences (else garbled mirror).
            if not (s1[:1] == w[:1] and s2[:1] == w[:1]
                    and s1.isalpha() and s2.isalpha()):
                sys.exit("FAIL: offsets word=%r recover implausible %r/%r "
                         "(fail-closed)" % (r["word"], s1, s2))
            inflected.append(r["word"])
    lemma_consistent = len(rows) - len(inflected)
    # positive faithfulness floor: the canonical WiC dev set recovers a lemma-
    # consistent target span in the large majority of items; a low rate would
    # signal a mis-aligned/garbled mirror.
    if lemma_consistent < 620:
        sys.exit("FAIL: only %d/%d lemma-consistent offset recoveries "
                 "(< 620 floor) — mirror alignment suspect (fail-closed)"
                 % (lemma_consistent, len(rows)))

    # idx 0..2 canonical-item check (fail-closed)
    head_words = [rows[i]["word"] for i in range(3)]
    if head_words != ["class", "stripe", "check"]:
        sys.exit("FAIL: dev idx0..2 words %s != canonical [class,stripe,check] "
                 "(fail-closed)" % head_words)

    # deterministic bytes: pinned source order, sorted keys per row
    path = os.path.join(OUTDIR, "wic-%s.jsonl" % SPLIT)
    buf = "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n"
                  for r in rows)
    with open(path, "w", encoding="utf-8") as f:
        f.write(buf)
    sha = hashlib.sha256(buf.encode("utf-8")).hexdigest()

    manifest = {
        "census_local_disclosed_input": True,
        "NOTE": "DISCLOSED MIRROR — census-local input only. This does NOT edit or "
                "relax the programme fail-closed sourcing policy in "
                "data/d-ext/manifest.json (which correctly declined mirror "
                "substitution for the frozen d-ext build). This is an exploratory "
                "census cell.",
        "canonical_predeclared_source": {
            "hf_repo": CANONICAL_SOURCE,
            "status": "UNAVAILABLE (HTTP 401 unauthenticated)",
            "license": "CC BY-NC 4.0",
        },
        "mirror_used": {
            "hf_repo": DATASET,
            "config": CONFIG,
            "split": SPLIT,
            "hf_commit_sha": main_sha,
            "hf_parquet_convert_sha": parquet_sha,
            "api": "datasets-server.huggingface.co/rows",
            "what_it_is": "SuperGLUE (Wang et al. 2019) incorporation of the "
                          "Word-in-Context dataset (Pilehvar & Camacho-Collados "
                          "2019, NAACL). Same items/task/labels as the WiC dataset.",
            "license_note": "SuperGLUE packaging CC BY 4.0; underlying WiC data "
                            "CC BY-NC 4.0 (research use).",
            "explicit_caveat": "EXPLORATORY MIRROR, NOT the canonical pilehvar/wic "
                               "source. Selected by the experiment-runner under a "
                               "maintainer delegation; faithfulness verified below.",
        },
        "faithfulness_verification": {
            "dev_split_n": len(rows),
            "expected_dev_n": EXPECT_N,
            "schema": EXPECT_SCHEMA,
            "label_type": "ClassLabel names [\"False\",\"True\"] -> 0=different "
                          "sense (False), 1=same sense (True)",
            "dev_label_balance": {"label0_diff_sense": label_counts[0],
                                  "label1_same_sense": label_counts[1]},
            "offset_target_lemma_exact": offset_exact,
            "offset_lemma_consistent_prefix3": lemma_consistent,
            "offset_irregular_inflection": len(inflected),
            "irregular_inflection_examples": inflected[:8],
            "offset_structural_check": "all spans in-bounds, non-empty, single-token",
            "canonical_head_items_idx0_2": head_words,
            "all_checks": "PASS (fail-closed; any mismatch aborts before write)",
        },
        "output": {"path": os.path.basename(path), "n": len(rows),
                   "sha256": "sha256:" + sha},
    }
    with open(os.path.join(OUTDIR, "wic-fetch-manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=False, ensure_ascii=False)
    print("WiC dev fetched: n=%d sha256:%s" % (len(rows), sha[:16]))
    print("mirror: %s config=%s split=%s commit=%s" % (
        DATASET, CONFIG, SPLIT, main_sha[:12]))
    print("label balance: 0(diff)=%d 1(same)=%d | offsets exact=%d "
          "lemma-consistent=%d irregular=%d"
          % (label_counts[0], label_counts[1], offset_exact,
             lemma_consistent, len(inflected)))
    print("faithfulness: PASS -> data/wic-fetch-manifest.json")


if __name__ == "__main__":
    main()
