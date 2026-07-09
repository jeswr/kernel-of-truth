"""kb_common — shared primitives for the Pillar-C literature KB (N-C).

Spec: docs/next/literature-kb.md (N-C). Reuses the P2 honesty-tooling spine
(tools/registry/kot_common.py) for canonical JSON, hashing, the RT-14
account-string lint, and the minimal fail-closed JSON-Schema validator —
tools/registry is law; nothing is re-implemented here.

THE HONESTY BOUNDARY (N-C §0, binding): KB records and chunks are RECALL
infrastructure, NOT evidence. `claims[].evidence` starts at "claimed" and may
only be upgraded by a commit that also cites a lit-report anchor
(`evidence_ref`); kb-check enforces this mechanically. Every query surface
prints EPISTEMICS_FOOTER.

Stdlib + NumPy only (NumPy needed for the embedding shards). onnxruntime /
tokenizers are imported lazily and only by the embedding paths, which fail
closed with a named error when the pinned local model is absent.
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "registry"))

from kot_common import (  # noqa: E402  (path bootstrap above is deliberate)
    KotError,
    account_lint,
    canonical_bytes,
    canonical_dumps,
    canonical_sha256,
    require_no_account_strings,
    require_pseudonym,
    sha256_hex,
    validate_schema,
    write_canonical_json,
)

KB_DIR = os.path.join(REPO_ROOT, "kb")
SCHEMA_DIR = os.path.join(KB_DIR, "schema")
RECORDS_DIR = os.path.join(KB_DIR, "records")
CHUNKS_DIR = os.path.join(KB_DIR, "chunks")
EMBEDDINGS_DIR = os.path.join(KB_DIR, "embeddings")
GRAPH_DIR = os.path.join(KB_DIR, "graph")
QUEUE_PATH = os.path.join(KB_DIR, "queue", "candidates.jsonl")
MANIFEST_PATH = os.path.join(KB_DIR, "manifest.json")
SOURCES_PATH = os.path.join(KB_DIR, "sources.json")
CACHE_DIR = os.path.join(KB_DIR, "cache")


def set_root(root):
    """Re-anchor every KB path under a different repo root.

    Used by `kb-check --root` (and fixtures, which run the lint against
    throwaway roots — the tools/registry SpineFixture pattern). Tool code
    stays where it is; only the DATA paths move.
    """
    global REPO_ROOT, KB_DIR, SCHEMA_DIR, RECORDS_DIR, CHUNKS_DIR
    global EMBEDDINGS_DIR, GRAPH_DIR, QUEUE_PATH, MANIFEST_PATH
    global SOURCES_PATH, CACHE_DIR, MODEL_CACHE_DIR
    REPO_ROOT = os.path.abspath(root)
    KB_DIR = os.path.join(REPO_ROOT, "kb")
    SCHEMA_DIR = os.path.join(KB_DIR, "schema")
    RECORDS_DIR = os.path.join(KB_DIR, "records")
    CHUNKS_DIR = os.path.join(KB_DIR, "chunks")
    EMBEDDINGS_DIR = os.path.join(KB_DIR, "embeddings")
    GRAPH_DIR = os.path.join(KB_DIR, "graph")
    QUEUE_PATH = os.path.join(KB_DIR, "queue", "candidates.jsonl")
    MANIFEST_PATH = os.path.join(KB_DIR, "manifest.json")
    SOURCES_PATH = os.path.join(KB_DIR, "sources.json")
    CACHE_DIR = os.path.join(KB_DIR, "cache")
    MODEL_CACHE_DIR = os.path.join(CACHE_DIR, "models", "nomic-embed-text-v1.5")

# N-C §0: printed under every kb search / filter / novelty result. Verbatim
# reminder so it lands in agent context every time.
EPISTEMICS_FOOTER = (
    "[KB epistemics] KB records/chunks are recall infrastructure, NOT evidence "
    "(N-C §0). Evidence tags stay 'claimed' until verified at source via a "
    "lit-report pass; cite reports/lit-*.md or registry verdicts, never a KB hit."
)

# N-C §2.2: closed enums (kb-check fails closed on anything outside these).
SEAM_CELLS = (
    "text",
    "own-activations",
    "trained-bridge",
    "external-engine",
    "raw-foreign-coords",
    "none",
)
CLAIM_TYPES = ("quantitative", "qualitative", "negative", "theoretical")
EVIDENCE_TAGS = ("established", "claimed", "speculative")
AUDIT_STATES = ("UNAUDITED", "SPOT-CONFIRMED", "SPOT-REFUTED")

# Canonical id grammar: arxiv > doi > url-slug (N-C §2.1).
ID_RE = re.compile(r"^(arxiv:[0-9]{4}\.[0-9]{4,5}(v[0-9]+)?|doi:10\.[^\s/]+/[^\s]+|url:[a-z0-9][a-z0-9._-]*)$")
ARXIV_ID_RE = re.compile(r"\b([0-9]{4}\.[0-9]{4,5})(v[0-9]+)?\b")
DOI_RE = re.compile(r"\b(10\.[0-9]{4,9}/[-._;()/:A-Za-z0-9]+[A-Za-z0-9])")

# Evidence upgrade rule (N-C §2.2): any tag above "claimed" needs a lit-report
# anchor in the claim's evidence_ref.
EVIDENCE_REF_RE = re.compile(r"reports/lit-[A-Za-z0-9._-]+\.md(#[A-Za-z0-9._%-]+)?")


class KbError(KotError):
    pass


def canonical_paper_id(arxiv=None, doi=None, url=None):
    """arxiv > doi > url-slug; normalised lowercase; strips arXiv versions."""
    if arxiv:
        m = ARXIV_ID_RE.search(arxiv)
        if m:
            return "arxiv:" + m.group(1)
    if doi:
        d = doi.strip().lower()
        d = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", d)
        # arXiv DataCite DOIs canonicalise back to the arxiv id
        m = re.match(r"^10\.48550/arxiv\.([0-9]{4}\.[0-9]{4,5})", d)
        if m:
            return "arxiv:" + m.group(1)
        if d.startswith("10."):
            return "doi:" + d
    if url:
        slug = re.sub(r"[^a-z0-9._-]+", "-", url.strip().lower()).strip("-")[:80]
        if slug:
            return "url:" + slug
    return None


def record_path(rec_id):
    """Filesystem path for a record id (':' and '/' are path-hostile)."""
    safe = rec_id.replace(":", "_").replace("/", "_")
    return os.path.join(RECORDS_DIR, safe + ".json")


def record_hash(record):
    """N-C §2.2: sha256 over canonical bytes minus record_sha256 itself."""
    stripped = {k: v for k, v in record.items() if k != "record_sha256"}
    return canonical_sha256(stripped)


def load_schema(name):
    path = os.path.join(SCHEMA_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        raise KbError("ERR_KB_MANIFEST", "kb/manifest.json missing — run the embed pipeline first")
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def read_jsonl(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise KbError("ERR_KB_JSONL", "%s line %d unparseable: %s" % (path, i, e))
    return out


def append_jsonl(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(canonical_dumps(obj) + "\n")


# ---------------------------------------------------------------- HTTP client
# Shared, throttled, cached fetcher for the ingest pipeline (N-C §4.2 "bytes
# hashed into kb/cache/"). Per-host minimum intervals honour the documented
# rate etiquette: S2 free tier ~1 RPS, arXiv 1 req / 3 s courtesy, OpenAlex
# well under its 100k/day.

_HOST_MIN_INTERVAL = {
    "api.semanticscholar.org": 1.15,
    "export.arxiv.org": 3.05,
    "api.openalex.org": 0.25,
    "api.crossref.org": 1.0,
}
_last_call = {}

USER_AGENT = "kot-lit-kb/1 (Kernel-of-Truth Pillar-C ingest; polite)"


def http_get(url, headers=None, cache_namespace="http", max_tries=5, timeout=60):
    """GET with per-host throttle, retry/backoff on 429/5xx, byte cache.

    Returns (bytes, from_cache). Cached responses live at
    kb/cache/<namespace>/<sha256(url)>.bin (gitignored); the cache is keyed by
    URL only — callers wanting freshness must bust the cache themselves.
    Never logs headers (keys stay out of every artefact).
    """
    cache_dir = os.path.join(CACHE_DIR, cache_namespace)
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, sha256_hex(url.encode("utf-8")) + ".bin")
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return f.read(), True

    safe_url = url.split("?", 1)[0]  # query strings may carry api keys — never in errors
    host = urllib.parse.urlparse(url).netloc
    interval = _HOST_MIN_INTERVAL.get(host, 0.5)
    delay = 2.0
    last_err = None
    for _ in range(max_tries):
        wait = _last_call.get(host, 0) + interval - time.time()
        if wait > 0:
            time.sleep(wait)
        _last_call[host] = time.time()
        req = urllib.request.Request(url, headers=dict(headers or {}, **{"User-Agent": USER_AGENT}))
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            tmp = cache_path + ".tmp"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, cache_path)
            return data, False
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (429, 500, 502, 503, 504):
                retry_after = e.headers.get("Retry-After") if e.headers else None
                try:
                    sleep_s = float(retry_after) if retry_after else delay
                except ValueError:
                    sleep_s = delay
                time.sleep(min(sleep_s, 60))
                delay *= 2
                continue
            raise KbError("ERR_KB_HTTP", "%s -> HTTP %d" % (safe_url, e.code))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            time.sleep(delay)
            delay *= 2
    raise KbError("ERR_KB_HTTP", "%s failed after %d tries: %s" % (safe_url, max_tries, type(last_err).__name__))


def api_keys():
    """API keys from the environment (source ~/.config/kot/lit-kb.env).

    Missing keys degrade politely (OpenAlex/arXiv work keyless today); the
    returned dict never gets printed or written anywhere.
    """
    return {
        "openalex": os.environ.get("OPENALEX_API_KEY", ""),
        "s2": os.environ.get("SEMANTIC_SCHOLAR_API_KEY", ""),
        "hf": os.environ.get("HUGGINGFACE_TOKEN", ""),
    }


# ---------------------------------------------------------------- embeddings
# Pinned embedder (N-C §1.2; see kb/manifest.json for the authoritative pins).
# NOTE (recorded discrepancy): N-C §1.2 names "nomic-embed-text-v2" but pins
# the spec "137M params, ~274 MB, 8192-token context, Matryoshka 768→64" —
# that spec is nomic-embed-text-v1.5 (v2-moe is 475M params / 1.9 GB and not
# CPU-viable on this box). We pin v1.5; KB-F3's retrieval eval is the licensed
# path to revisit. Any change is a KB version change (full re-embed, new
# manifest hash, changelog line) — never a silent swap.

EMBEDDER = {
    "hf_repo": "nomic-ai/nomic-embed-text-v1.5",
    "hf_revision": "e9b6763023c676ca8431644204f50c2b100d9aab",
    "onnx_file": "onnx/model.onnx",  # fp32 graph — byte-deterministic rebuilds
    "onnx_sha256": "147d5aa88c2101237358e17796cf3a227cead1ec304ec34b465bb08e9d952965",  # HF LFS oid @ pinned revision
    "tokenizer_file": "tokenizer.json",
    "dim_full": 768,
    "dim_committed": 256,  # Matryoshka truncation committed to the repo (N-C §1.1)
    "max_tokens": 512,  # chunking cap; model context is 8192 but CPU says 512
    "doc_prefix": "search_document: ",
    "query_prefix": "search_query: ",
    "post": "mean-pool -> layer_norm(eps=1e-5, no affine) -> truncate -> l2-normalize",
}

MODEL_CACHE_DIR = os.path.join(CACHE_DIR, "models", "nomic-embed-text-v1.5")


def _model_paths():
    return (
        os.path.join(MODEL_CACHE_DIR, "model.onnx"),
        os.path.join(MODEL_CACHE_DIR, "tokenizer.json"),
    )


def fetch_model():
    """Download the pinned embedder into kb/cache/models/ (gitignored).

    Uses HUGGINGFACE_TOKEN when present (public model, so keyless also works).
    Verifies the committed sha256 pin — a mismatched download fails closed.
    """
    os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
    keys = api_keys()
    headers = {"Authorization": "Bearer " + keys["hf"]} if keys["hf"] else {}
    base = "https://huggingface.co/%s/resolve/%s/" % (EMBEDDER["hf_repo"], EMBEDDER["hf_revision"])
    onnx_path, tok_path = _model_paths()
    for remote, local, pin in (
        (EMBEDDER["onnx_file"], onnx_path, EMBEDDER["onnx_sha256"]),
        (EMBEDDER["tokenizer_file"], tok_path, None),
    ):
        if os.path.exists(local):
            continue
        url = base + remote
        req = urllib.request.Request(url, headers=dict(headers, **{"User-Agent": USER_AGENT}))
        tmp = local + ".tmp"
        with urllib.request.urlopen(req, timeout=600) as resp, open(tmp, "wb") as f:
            while True:
                block = resp.read(1 << 20)
                if not block:
                    break
                f.write(block)
        if pin:
            import hashlib

            h = hashlib.sha256()
            with open(tmp, "rb") as f:
                for block in iter(lambda: f.read(1 << 20), b""):
                    h.update(block)
            if h.hexdigest() != pin:
                os.remove(tmp)
                raise KbError(
                    "ERR_KB_MODEL_PIN",
                    "%s sha256 %s != pinned %s" % (remote, h.hexdigest(), pin),
                )
        os.replace(tmp, local)
    return onnx_path, tok_path


class Embedder:
    """Pinned local CPU embedder. Fails closed if the model is not fetched."""

    def __init__(self):
        onnx_path, tok_path = _model_paths()
        if not (os.path.exists(onnx_path) and os.path.exists(tok_path)):
            raise KbError(
                "ERR_KB_MODEL_MISSING",
                "pinned embedder not in kb/cache/models/ — run: tools/kb/kb fetch-model",
            )
        try:
            import onnxruntime as ort
            from tokenizers import Tokenizer
        except ImportError as e:
            raise KbError("ERR_KB_DEPS", "embedding needs onnxruntime + tokenizers: %s" % e)
        self.tok = Tokenizer.from_file(tok_path)
        self.tok.enable_truncation(max_length=EMBEDDER["max_tokens"])
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 1  # box discipline: 2 shared cores, stay niced+narrow
        opts.inter_op_num_threads = 1
        self.sess = ort.InferenceSession(onnx_path, opts, providers=["CPUExecutionProvider"])

    def embed(self, texts, is_query=False, dim=None):
        """-> float32 array [n, dim], layer-normed, truncated, L2-normalised."""
        import numpy as np

        dim = dim or EMBEDDER["dim_committed"]
        prefix = EMBEDDER["query_prefix"] if is_query else EMBEDDER["doc_prefix"]
        out = np.zeros((len(texts), dim), dtype=np.float32)
        for i, text in enumerate(texts):
            enc = self.tok.encode(prefix + text)
            ids = np.array([enc.ids], dtype=np.int64)
            mask = np.array([enc.attention_mask], dtype=np.int64)
            feeds = {"input_ids": ids, "attention_mask": mask}
            if any(inp.name == "token_type_ids" for inp in self.sess.get_inputs()):
                feeds["token_type_ids"] = np.zeros_like(ids)
            (hidden,) = self.sess.run(["last_hidden_state"], feeds)
            m = mask[0].astype(np.float32)[:, None]
            pooled = (hidden[0] * m).sum(axis=0) / max(m.sum(), 1.0)
            # nomic Matryoshka recipe: layer_norm -> truncate -> l2 normalize
            pooled = (pooled - pooled.mean()) / np.sqrt(pooled.var() + 1e-5)
            v = pooled[:dim]
            n = np.linalg.norm(v)
            out[i] = v / n if n > 0 else v
        return out


def load_shards():
    """-> (matrix [n, dim] float32, chunk-metadata list) from committed shards.

    Shard pairing law (N-C §1.1/§4.4): kb/chunks/shard-NNN.jsonl row i is the
    text/provenance for kb/embeddings/shard-NNN.f16.npy row i.
    """
    import numpy as np

    mats, metas = [], []
    if os.path.isdir(EMBEDDINGS_DIR):
        for name in sorted(os.listdir(EMBEDDINGS_DIR)):
            if not name.endswith(".f16.npy"):
                continue
            chunk_file = os.path.join(CHUNKS_DIR, name[: -len(".f16.npy")] + ".jsonl")
            mat = np.load(os.path.join(EMBEDDINGS_DIR, name)).astype(np.float32)
            rows = read_jsonl(chunk_file)
            if len(rows) != mat.shape[0]:
                raise KbError(
                    "ERR_KB_SHARD_MISMATCH",
                    "%s has %d rows but %s has %d chunks" % (name, mat.shape[0], chunk_file, len(rows)),
                )
            mats.append(mat)
            metas.extend(rows)
    if not mats:
        return None, []
    return np.vstack(mats), metas
