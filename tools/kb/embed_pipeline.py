#!/usr/bin/env python3
"""Chunk + embed pipeline for FORM V of the lit-KB (N-C §1.1/§1.3/§4.2).

Chunk sources (all committed, so the build is a pure function of the repo):
  reports/*.md            section-level   kind=lit-report   (verified synthesis)
  docs/**/*.md            section-level   kind=design-doc
  notes/**/*.md           section-level   kind=note
  kb/records/internal/*   one chunk each  kind=internal-verdict (generated summaries)
  kb/queue/candidates.jsonl  title+abstract  kind=paper-abstract

Every chunk carries {source_id, kind, sha256(source bytes), span} so a hit
resolves to an exact, hash-pinned location (N-C §1.3).

Output: kb/chunks/shard-NNN.jsonl + kb/embeddings/shard-NNN.f16.npy (row-aligned,
256-dim Matryoshka truncation, float16) + kb/manifest.json pins.

Run niced (box discipline): nice -n 10 python3 tools/kb/embed_pipeline.py
Checkpointed: re-running resumes at the first missing shard embedding.
"""

import datetime
import glob
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kb_common as K  # noqa: E402

SHARD_SIZE = 1024
MAX_CHUNK_CHARS = 4000
MIN_CHUNK_CHARS = 200

MD_SOURCES = (
    ("reports", "lit-report", "reports/*.md"),
    ("docs", "design-doc", "docs/**/*.md"),
    ("notes", "note", "notes/**/*.md"),
)


def _file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def split_markdown(text):
    """-> [(start, end)] section spans split on headings, size-bounded."""
    lines = text.split("\n")
    # heading line offsets
    offsets, pos = [], 0
    heads = [0]
    for line in lines:
        if re.match(r"^#{1,4} ", line) and pos > 0:
            heads.append(pos)
        offsets.append(pos)
        pos += len(line) + 1
    heads.append(len(text))
    spans = []
    for a, b in zip(heads, heads[1:]):
        seg = text[a:b]
        if len(seg.strip()) < 1:
            continue
        # size-bound long sections at paragraph boundaries
        start = a
        while b - start > MAX_CHUNK_CHARS:
            cut = text.rfind("\n\n", start + MAX_CHUNK_CHARS // 2, start + MAX_CHUNK_CHARS)
            if cut == -1:
                cut = start + MAX_CHUNK_CHARS
            spans.append((start, cut))
            start = cut
        spans.append((start, b))
    # merge tiny fragments forward
    merged = []
    for s in spans:
        if merged and (s[1] - s[0]) < MIN_CHUNK_CHARS and merged[-1][1] == s[0]:
            merged[-1] = (merged[-1][0], s[1])
        else:
            merged.append(list(s))
    return [(a, b) for a, b in merged if text[a:b].strip()]


def build_chunks():
    chunks = []

    def add(source_id, kind, sha, span, text):
        text = text.strip()
        if not text:
            return
        cid = K.sha256_hex(("%s|%d|%d|%s" % (source_id, span[0], span[1], sha)).encode("utf-8"))[:16]
        chunks.append(
            {
                "chunk_id": cid,
                "source_id": source_id,
                "kind": kind,
                "source_sha256": sha,
                "span": [span[0], span[1]],
                "text": text,
            }
        )

    for _, kind, pattern in MD_SOURCES:
        for path in sorted(glob.glob(os.path.join(K.REPO_ROOT, pattern), recursive=True)):
            rel = os.path.relpath(path, K.REPO_ROOT).replace(os.sep, "/")
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            sha = K.sha256_hex(text.encode("utf-8"))
            for span in split_markdown(text):
                add(rel, kind, sha, span, text[span[0] : span[1]])

    internal_dir = os.path.join(K.RECORDS_DIR, "internal")
    if os.path.isdir(internal_dir):
        for name in sorted(os.listdir(internal_dir)):
            if not name.endswith(".json"):
                continue
            path = os.path.join(internal_dir, name)
            with open(path, "rb") as f:
                raw = f.read()
            rec = json.loads(raw.decode("utf-8"))
            # design-doc stubs restate docs/ files that are already chunked
            # section-level above — chunking them again would double-count
            if rec.get("kind") == "design-doc":
                continue
            body = "%s — %s" % (rec.get("title", ""), rec.get("summary", ""))
            add(rec["id"], "internal-verdict", K.sha256_hex(raw), (0, len(raw)), body)

    # structured paper records (Form S -> Form V: key fields embedded, N-C §1.3)
    if os.path.isdir(K.RECORDS_DIR):
        for name in sorted(os.listdir(K.RECORDS_DIR)):
            if not name.endswith(".json"):
                continue
            path = os.path.join(K.RECORDS_DIR, name)
            with open(path, "rb") as f:
                raw = f.read()
            rec = json.loads(raw.decode("utf-8"))
            arch = rec.get("architecture") or {}
            parts = [
                "%s (%s)" % (rec.get("biblio", {}).get("title", ""), rec.get("biblio", {}).get("year")),
                "seam: %s; tags: %s" % (arch.get("seam_cell"), ", ".join(arch.get("mechanism_tags") or [])),
                arch.get("summary") or "",
            ]
            parts += ["claim %s [%s]: %s" % (c.get("claim_id"), c.get("type"), c.get("statement"))
                      for c in rec.get("claims") or []]
            body = "\n".join(p for p in parts if p)[:MAX_CHUNK_CHARS]
            add(rec["id"], "paper-record", K.sha256_hex(raw), (0, len(raw)), body)

    for row in K.read_jsonl(K.QUEUE_PATH):
        body = row.get("title") or ""
        if row.get("abstract"):
            body += "\n" + row["abstract"]
        sha = K.sha256_hex(K.canonical_bytes(row))
        add(row["id"], "paper-abstract", sha, (0, len(body)), body)

    return chunks


def main():
    import numpy as np

    chunks = build_chunks()
    print("chunker: %d chunks" % len(chunks))
    os.makedirs(K.CHUNKS_DIR, exist_ok=True)
    os.makedirs(K.EMBEDDINGS_DIR, exist_ok=True)

    # deterministic shard split; rewrite chunk shards every run (pure function)
    shard_names = []
    for i in range(0, len(chunks), SHARD_SIZE):
        n = i // SHARD_SIZE
        name = "shard-%03d" % n
        shard_names.append(name)
        with open(os.path.join(K.CHUNKS_DIR, name + ".jsonl"), "w", encoding="utf-8") as f:
            for c in chunks[i : i + SHARD_SIZE]:
                f.write(K.canonical_dumps(c) + "\n")
    # drop stale shards beyond the current count
    for path in glob.glob(os.path.join(K.CHUNKS_DIR, "shard-*.jsonl")):
        if os.path.basename(path)[: -len(".jsonl")] not in shard_names:
            os.remove(path)
    for path in glob.glob(os.path.join(K.EMBEDDINGS_DIR, "shard-*.f16.npy")):
        if os.path.basename(path)[: -len(".f16.npy")] not in shard_names:
            os.remove(path)

    # sha-based checkpointing: an embedding shard is reusable ONLY if the chunk
    # shard bytes still match the manifest pin it was built against (a
    # row-count match is not enough — chunk content can shift between shards).
    prev_pins = {}
    if os.path.exists(K.MANIFEST_PATH):
        with open(K.MANIFEST_PATH, "r", encoding="utf-8") as f:
            prev_pins = json.load(f).get("shards", {})

    emb = K.Embedder()
    t0 = datetime.datetime.now()
    for n, name in enumerate(shard_names):
        out_path = os.path.join(K.EMBEDDINGS_DIR, name + ".f16.npy")
        chunk_rel = "chunks/%s.jsonl" % name
        chunk_sha = _file_sha256(os.path.join(K.CHUNKS_DIR, name + ".jsonl"))
        rows = K.read_jsonl(os.path.join(K.CHUNKS_DIR, name + ".jsonl"))
        if os.path.exists(out_path):
            existing = np.load(out_path)
            if existing.shape[0] == len(rows) and prev_pins.get(chunk_rel) == chunk_sha:
                print("embed: %s unchanged (%d rows) — checkpoint skip" % (name, len(rows)))
                continue
        vecs = np.zeros((len(rows), K.EMBEDDER["dim_committed"]), dtype=np.float16)
        for j, row in enumerate(rows):
            vecs[j] = emb.embed([row["text"]])[0].astype(np.float16)
            if (j + 1) % 100 == 0:
                print("embed: %s %d/%d (%s elapsed)" % (name, j + 1, len(rows), datetime.datetime.now() - t0), flush=True)
        tmp = out_path + ".tmp.npy"
        np.save(tmp, vecs)
        os.replace(tmp, out_path)
        print("embed: wrote %s (%d rows)" % (out_path, len(rows)))

    # manifest pins (N-C §4.4)
    shards = {}
    for d, suffix in ((K.CHUNKS_DIR, ".jsonl"), (K.EMBEDDINGS_DIR, ".f16.npy")):
        for name in sorted(os.listdir(d)):
            if name.endswith(suffix):
                shards[os.path.join(os.path.basename(d), name)] = _file_sha256(os.path.join(d, name))
    rubric_path = os.path.join(K.KB_DIR, "triage-rubric.md")
    manifest = {
        "schema_version": "kot-kb-manifest/1",
        "built_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "embedder": {
            "hf_repo": K.EMBEDDER["hf_repo"],
            "hf_revision": K.EMBEDDER["hf_revision"],
            "onnx_file": K.EMBEDDER["onnx_file"],
            "onnx_sha256": K.EMBEDDER["onnx_sha256"],
            "dim_full": K.EMBEDDER["dim_full"],
            "dim_committed": K.EMBEDDER["dim_committed"],
            "max_tokens": K.EMBEDDER["max_tokens"],
            "doc_prefix": K.EMBEDDER["doc_prefix"],
            "query_prefix": K.EMBEDDER["query_prefix"],
            "post": K.EMBEDDER["post"],
            "pin_note": (
                "N-C §1.2 names 'nomic-embed-text-v2' but specifies 137M/~274MB/Matryoshka-768 — "
                "that spec is nomic-embed-text-v1.5 (v2-moe is 475M/1.9GB, not CPU-viable on this box). "
                "v1.5 pinned; KB-F3 retrieval eval is the licensed path to change this. "
                "Embedder change = KB version change: full re-embed + new manifest + changelog."
            ),
        },
        "chunk_count": len(chunks),
        "shards": shards,
        "triage_rubric_sha256": _file_sha256(rubric_path),
        "changelog": ["kb-v1 %s: initial build (bootstrap corpus)" % datetime.date.today().isoformat()],
    }
    # preserve prior changelog lines on rebuild
    if os.path.exists(K.MANIFEST_PATH):
        with open(K.MANIFEST_PATH, "r", encoding="utf-8") as f:
            old = json.load(f)
        if old.get("changelog"):
            entry = "kb rebuild %s: %d chunks" % (datetime.date.today().isoformat(), len(chunks))
            manifest["changelog"] = old["changelog"] + [entry]
    K.write_canonical_json(K.MANIFEST_PATH, manifest)
    print("manifest: %s written (%d shard files pinned)" % (K.MANIFEST_PATH, len(shards)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
