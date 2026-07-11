#!/usr/bin/env python3
"""DECONF/1 Stage A1 — GS-A builder (docs/next/design/DECONF.md §2.1, ASM-0961).

GS-A is a MECHANICAL FIELD PROJECTION of the pinned kernel-v0 / molecules-v0
store onto exactly the read-set of the pinned verifier's check():

    per covered concept, the four-column row
        {concept_id, term_labels, canonical_text, claims}

Every byte is copied/derived verbatim from the kernel's own records by the
SAME pinned derivation the checker itself uses at load time
(poc/f2b/runner/f2b_runner.py::KernelVerifier._load — gloss.strip() for
molecules-v0 records, render_plain(groundingNote) for kernel-v0 records,
claims = segments(canonical_text)).  ZERO authored prose: no new string enters
the store that is not a deterministic function of the pinned record bytes
(hence outside the ASM-0700/0703 authored-store quality-gate object class —
ASM-0961).

Deterministic and seed-free: output bytes depend only on the pinned inputs.
Fail-closed on every pin (ERR_*).

Inputs (all hash-verified before use):
  - the three pinned corpora item files (d-qa covered, d-qa-r covered,
    d-qa-t covered) — they carry the record_path + record_sha256 pins that
    key the projection (DECONF §2.1: "the same record_path keys the items
    already pin");
  - the canonical record files under data/kernel-v0/ + data/molecules-v0/,
    each verified against its per-item sha pin;
  - poc/f2b/runner/f2b_runner.py at the f2b-replicate harness pin (the
    derivation functions' source), verified against the staged-bytes sha
    recorded in the audited run's provenance
    (poc/f2b/results-incoming/20260709-114229-modal/provenance-modal.json
    staged_sha256["runner/f2b_runner.py"], cross-checked in
    poc/f2b/opus-runs/20260709T104212Z/run-log.md "Changed-file shas").

Outputs:
  - gs-a.jsonl        one canonical-JSON row per covered concept, sorted by
                      concept_id (the store; four columns only)
  - gsa-manifest.json input pins + the gs-a.jsonl content hash

Usage:  python3 build_gsa.py            (from anywhere; paths are repo-anchored)
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
RUNNER = os.path.join(ROOT, "poc", "f2b", "runner", "f2b_runner.py")

# poc/f2b/runner/f2b_runner.py at the f2b-replicate harness pin — the staged
# bytes of the audited 2026-07-09 Modal run (harness_manifest cffd6104...,
# frozen record sha 21d40177...); MEASURED provenance, see module docstring.
RUNNER_SHA256_PIN = \
    "b62c3a72882b354f25b97a4b38251fb4863b1c3417220d1c942c84b24fc9b666"

# kot-corpus-hash/1 pins, restated from the FROZEN registry records
# (registry/experiments/f2b-replicate.json + f2b-transfer.json pins.corpus_hashes).
CORPUS_PINS = {
    "d-qa":         "ad756a7e31f9281de3baaff149e87832d8195452b41b19b6f16883ff196571e6",
    "d-qa-r":       "0d548bf18ac78f9d7b2abb6686c567f0930acd494c5ca03cee49806c4996ec5e",
    "d-qa-t":       "7179ee6791bd0af643c410872925ff594945c29b563192f6d7c4a872397cee27",
    "kernel-v0":    "8209cadabcfc2eaa11631c5c1100c04a48f33673516780b1f36cbf957217c809",
    "molecules-v0": "69f0c8a354ce489d15e9156d611932ba548f80c41e78af4ffe597192067a59c4",
}

ITEM_FILES = [
    os.path.join(ROOT, "data", "d-qa", "items", "covered.jsonl"),
    os.path.join(ROOT, "data", "d-qa-r", "items", "covered.jsonl"),
    os.path.join(ROOT, "data", "d-qa-t", "items", "covered.jsonl"),
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def corpus_hash(root, name):
    """kot-corpus-hash/1 via the REFERENCE implementation
    (tools/registry/kot_common.py — 'this tool IS the recipe')."""
    sys.path.insert(0, os.path.join(root, "tools", "registry"))
    import kot_common  # noqa: E402
    return kot_common.corpus_hash(root, name)


def main():
    # ---- pin gates (fail closed) -----------------------------------------
    got = sha256_file(RUNNER)
    if got != RUNNER_SHA256_PIN:
        raise SystemExit("ERR_RUNNER_PIN: %s sha %s != pinned %s"
                         % (RUNNER, got, RUNNER_SHA256_PIN))
    for name, pin in sorted(CORPUS_PINS.items()):
        h = corpus_hash(ROOT, name)
        if h != pin:
            raise SystemExit("ERR_CORPUS_PIN: data/%s kot-corpus-hash %s != "
                             "registry pin %s" % (name, h, pin))
        print("pin OK  data/%-13s %s" % (name, h))

    # Import the PINNED derivation functions (render_plain, segments) from the
    # verified runner bytes — the projection uses the checker's own load-time
    # derivation, nothing else.
    sys.path.insert(0, os.path.dirname(RUNNER))
    import f2b_runner  # noqa: E402

    # ---- collect the covered-concept key set from the pinned items --------
    concepts = {}  # urn -> {record_path, record_sha256, item_label}
    for path in ITEM_FILES:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                it = json.loads(line)
                if not it.get("kernel_checkable"):
                    continue
                v = {"record_path": it["record_path"],
                     "record_sha256": it["record_sha256"],
                     "item_label": it["label"]}
                prev = concepts.get(it["urn"])
                if prev is not None and prev != v:
                    raise SystemExit("ERR_KEY_DRIFT: %s pins disagree across "
                                     "corpora" % it["urn"])
                concepts[it["urn"]] = v

    # ---- project ----------------------------------------------------------
    rows = []
    prov = {}
    for urn in sorted(concepts):
        meta = concepts[urn]
        rp = os.path.join(ROOT, meta["record_path"])
        got = sha256_file(rp)
        if got != meta["record_sha256"]:
            raise SystemExit("ERR_RECORD_PIN: %s sha %s != item pin %s"
                             % (meta["record_path"], got, meta["record_sha256"]))
        with open(rp, encoding="utf-8") as f:
            rec = json.load(f)
        # EXACTLY KernelVerifier._load's canonical-text derivation:
        canon = (rec["gloss"].strip() if "gloss" in rec
                 else f2b_runner.render_plain(rec["groundingNote"]))
        if rec["label"] != meta["item_label"]:
            raise SystemExit("ERR_LABEL_DRIFT: %s record label %r != item "
                             "label %r" % (urn, rec["label"], meta["item_label"]))
        rows.append({
            "concept_id": urn,
            "term_labels": [rec["label"]],
            "canonical_text": canon,
            "claims": f2b_runner.segments(canon),
        })
        prov[urn] = {"record_path": meta["record_path"],
                     "record_sha256": meta["record_sha256"],
                     "text_source_field": "gloss" if "gloss" in rec
                                          else "groundingNote(render_plain)"}

    if len(rows) != 108:
        raise SystemExit("ERR_CONCEPT_COUNT: expected 108 covered concepts, "
                         "got %d" % len(rows))
    labels = [r["term_labels"][0].lower() for r in rows]
    if len(set(labels)) != len(labels):
        raise SystemExit("ERR_LABEL_COLLISION: duplicate term labels in GS-A")

    # ---- write (canonical JSON, deterministic bytes) -----------------------
    out_store = os.path.join(HERE, "gs-a.jsonl")
    with open(out_store, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False) + "\n")
    store_sha = sha256_file(out_store)

    manifest = {
        "artifact": "GS-A — aligned generic answer-key store (DECONF/1 §2.1)",
        "derivation": "ASM-0961: mechanical four-column projection of the "
                      "pinned kernel-v0/molecules-v0 records onto the "
                      "check() read-set; canonical_text/claims derived by the "
                      "pinned runner's own load-time functions (gloss.strip / "
                      "render_plain, segments); zero authored prose; "
                      "deterministic + seed-free",
        "columns": ["concept_id", "term_labels", "canonical_text", "claims"],
        "n_rows": len(rows),
        "gs_a_sha256": store_sha,
        "runner_pin": {"path": "poc/f2b/runner/f2b_runner.py",
                       "sha256": RUNNER_SHA256_PIN},
        "corpus_pins_verified": CORPUS_PINS,
        "record_provenance": prov,
    }
    out_man = os.path.join(HERE, "gsa-manifest.json")
    with open(out_man, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    print("GS-A: %d rows -> %s" % (len(rows), out_store))
    print("gs_a_sha256 %s" % store_sha)
    print("manifest    %s" % out_man)


if __name__ == "__main__":
    main()
