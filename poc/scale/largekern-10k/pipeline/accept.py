#!/usr/bin/env python3
"""accept.py — component 5: the ACCEPTANCE STACK + immutable ModelDrafted
minting (spec §§2, 4.1, 8, 9; P8 machinery reused from poc/plainv5).

Per returned draft, in order (all fail-closed):
  1. output-protocol parse (malformed JSON counts as an attempt and enters
     repair once with the parse error, §10.3; abstention is terminal, §2.3);
  2. gloss lint gates (§4.1 item 4): 15-100 words, whitespace-token cap
     (MOCK proxy for the pinned tokenizer, ASM-2496), non-circularity,
     8-token leakage vs the pinned mock eval fixture;
  3. the encoder/validator loop, sharded (validate_shard.mjs — REUSED encoder
     dist: validateExplication + ERR_REF_OUTSIDE_CATALOG closure +
     encodeConceptSet(opts.concepts) sanity, §4.1 items 1-3, §7.1);
  4. family-disjointness / provenance (P8, §9.1): authorFamily MUST equal
     resolve_family(draftAuthor) == "openai" under the PINNED resolver
     (never a string compare) — checked per batch on the store manifest via
     poc/plainv5/check_family_disjoint; consumer status gate per §9.2
     (ERR_STATUS_INELIGIBLE) — JSONL-aware wrapper here, semantics identical.
  5. minting (§2.1): pass => an IMMUTABLE ModelDrafted record
     (kernel-v1-draft/1) appended to a JSONL shard, recordSha256 into the
     shard manifest; fail => repair (wave < R) or QUARANTINED(code). No
     mutable transition exists; endorsement (out of scope) would MINT a new
     Explicated record.
"""

import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import PipelineError

sys.path.insert(0, os.path.join(common.REPO_ROOT, "poc", "plainv5"))
from check_family_disjoint import resolve_family, check_provenance  # noqa: E402 — pinned P8 impl
from invoke_seat import load_family_map                             # noqa: E402

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
VALIDATE_SHARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "validate_shard.mjs")

# Pinned MOCK eval fixture for the 8-token leakage gate (§2.3). The real
# pilot pins the actual eval-item set at prereg; the mock pins a tiny fixture
# so the code path is exercised, incl. one deliberate hit in tests.
MOCK_EVAL_ITEMS = [
    "the quick auditor checked whether the drafted gloss leaked benchmark phrasing into the record text",
    "a pinned evaluation item that no honest draft should ever quote at eight token length or more",
]


def _shingles(text, k=None):
    k = k or common.LEAKAGE_SHINGLE
    toks = [w.lower() for w in _WORD_RE.findall(text)]
    return set(tuple(toks[i:i + k]) for i in range(len(toks) - k + 1))


_EVAL_SHINGLES = set()
for _it in MOCK_EVAL_ITEMS:
    _EVAL_SHINGLES |= _shingles(_it)


def lint_gloss(gloss, lemma):
    """§4.1 item 4. Returns list of ERR_* codes (empty = pass)."""
    errs = []
    if not isinstance(gloss, str) or not gloss.strip():
        return ["ERR_GLOSS_EMPTY"]
    words = gloss.split()
    if len(words) < common.GLOSS_MIN_WORDS:
        errs.append("ERR_GLOSS_TOO_SHORT")
    if len(words) > common.GLOSS_MAX_WORDS:
        errs.append("ERR_GLOSS_TOO_LONG")
    if len(words) > common.GLOSS_MAX_TOKENS:   # MOCK whitespace-token proxy (ASM-2496)
        errs.append("ERR_GLOSS_TOKEN_CAP")
    lemma_tokens = {t.lower() for t in re.split(r"[_\s-]+", lemma) if t}
    gloss_tokens = {w.lower() for w in _WORD_RE.findall(gloss)}
    if lemma_tokens & gloss_tokens:
        errs.append("ERR_GLOSS_CIRCULAR")
    if _shingles(gloss) & _EVAL_SHINGLES:
        errs.append("ERR_LEAKAGE")             # hard reject (§2.3)
    return errs


def parse_output(output_text):
    """Output-protocol parse. Returns (kind, payload):
    kind in {'draft', 'abstain', 'malformed'}."""
    try:
        obj = json.loads(output_text)
    except ValueError as e:
        return "malformed", ["ERR_OUTPUT_PARSE: %s" % str(e)[:80]]
    if not isinstance(obj, dict):
        return "malformed", ["ERR_OUTPUT_PARSE: non-object output"]
    if "cannot_draft" in obj:
        return "abstain", obj["cannot_draft"]
    if not isinstance(obj.get("gloss"), str) or not isinstance(obj.get("explication"), dict):
        return "malformed", ["ERR_OUTPUT_PROTOCOL: missing gloss/explication"]
    return "draft", obj


def validate_shards(drafts, shard_b=None, keep_result=None):
    """Run the node validator over {id: explication} in B-bounded shards
    (§7.1). Returns (per_id: id -> (ok, code), shard_reports)."""
    shard_b = shard_b or common.VALIDATOR_SHARD_B
    ids = list(drafts.keys())
    per_id, reports = {}, []
    for s in range(0, len(ids), shard_b):
        chunk = ids[s:s + shard_b]
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            for i in chunk:
                f.write(common.canonical_dumps({"id": i, "explication": drafts[i]}) + "\n")
            shard_path = f.name
        out_path = shard_path + ".result.json"
        try:
            proc = subprocess.run(
                ["nice", "-n", "10", "node", VALIDATE_SHARD, "--shard", shard_path, "--out", out_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.returncode != 0:
                raise PipelineError("ERR_SHARD_VALIDATE",
                                    "validate_shard.mjs failed: %s" % proc.stderr.decode()[:300])
            rep = common.read_json(out_path)
            reports.append(rep)
            if keep_result:
                common.write_json(keep_result % len(reports), rep)
            for r in rep["perRecord"]:
                per_id[r["id"]] = (r["ok"], r.get("code"))
        finally:
            for p in (shard_path, out_path):
                if os.path.exists(p):
                    os.unlink(p)
    return per_id, reports


# ------------------------------------------------------------------ minting

class DraftStore(object):
    """Immutable ModelDrafted bucket (§2.1): JSONL shards (mock: uncompressed
    .jsonl for auditability; the real store gzips per §7.2 — noted ASM-2496),
    per-shard sha256 manifest, transcripts sharded alongside (§7.2)."""

    SHARD_MAX = 5000

    def __init__(self, store_dir=None):
        self.dir = store_dir or common.STORE_DIR
        self.records_dir = os.path.join(self.dir, "records")
        self.transcripts_dir = os.path.join(self.dir, "transcripts")
        for d in (self.records_dir, self.transcripts_dir):
            if not os.path.isdir(d):
                os.makedirs(d)
        self.fmap = load_family_map(common.FAMILY_MAP)
        self._counts = {"records": 0, "transcripts": 0}
        self._shas = {}          # draftId -> recordSha256
        self._quarantine = []

    def _shard_path(self, kind, n):
        d = self.records_dir if kind == "records" else self.transcripts_dir
        return os.path.join(d, "shard-%04d.jsonl" % (n // self.SHARD_MAX))

    def provenance_agreement(self):
        """§8/§9.1 P8 assertion: authorFamily == resolve_family(draftAuthor)
        == "openai" under the PINNED resolver."""
        fam = resolve_family(common.MODEL_SNAPSHOT_ID, self.fmap)
        if fam != "openai":
            raise PipelineError("ERR_FAMILY_PROVENANCE",
                                "resolve_family(%s)=%r != 'openai'" % (common.MODEL_SNAPSHOT_ID, fam))
        return fam

    def append_transcript(self, concept_id, suffix_and_output):
        n = self._counts["transcripts"]
        path = self._shard_path("transcripts", n)
        line = common.canonical_dumps({"conceptId": concept_id, "transcript": suffix_and_output})
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        self._counts["transcripts"] += 1
        return "%s#%d" % (os.path.basename(path), n % self.SHARD_MAX), len(line) + 1

    def mint(self, row, draft, provenance):
        """§2.1: write the immutable ModelDrafted record. Never edited after;
        any change is a new conceptVersion => new id => new ledger row."""
        author_family = self.provenance_agreement()
        rec = {
            "schema": "kernel-v1-draft/1",
            "id": "urn:kernel-v1-draft:%s@v%d" % (row["conceptId"], provenance["conceptVersion"]),
            "label": row["lemma"],
            "semanticStatus": "ModelDrafted",
            "candidateStatus": "Explicated",
            "gloss": draft["gloss"],
            "record": draft["explication"],
            "gatesPassed": True,
            "provenance": dict(provenance, authorFamily=author_family),
        }
        line = common.canonical_dumps(rec)
        rec_sha = hashlib.sha256(line.encode("utf-8")).hexdigest()
        n = self._counts["records"]
        with open(self._shard_path("records", n), "a", encoding="utf-8") as f:
            f.write(line + "\n")
        self._counts["records"] += 1
        self._shas[rec["id"]] = rec_sha
        return rec["id"], rec_sha, len(line) + 1

    def quarantine(self, row, code, detail, wave):
        """Terminal quarantine — data, never a record (§2.1), full provenance."""
        self._quarantine.append({
            "conceptId": row["conceptId"], "code": code,
            "detail": str(detail)[:300], "wave": wave,
        })

    def write_manifest(self, extra=None):
        shard_shas = {}
        for d, key in ((self.records_dir, "recordShards"), (self.transcripts_dir, "transcriptShards")):
            shard_shas[key] = {}
            for fn in sorted(os.listdir(d)):
                with open(os.path.join(d, fn), "rb") as f:
                    shard_shas[key][fn] = hashlib.sha256(f.read()).hexdigest()
        qpath = os.path.join(self.dir, "quarantine.jsonl")
        with open(qpath, "w", encoding="utf-8") as f:
            for q in self._quarantine:
                f.write(common.canonical_dumps(q) + "\n")
        manifest = dict({
            "schema": "kernel-v1-draft-manifest/1",
            "draftAuthor": common.MODEL_SNAPSHOT_ID,
            "authorFamily": "openai",     # must re-verify against the resolver below
            "pipelineOperator": "runner-1 (kb-pipeline-runner)",
            "counts": dict(self._counts, quarantined=len(self._quarantine)),
            "recordSha256": self._shas,
        }, **(shard_shas))
        if extra:
            manifest.update(extra)
        path = os.path.join(self.dir, "manifest.json")
        common.write_json(path, manifest)
        # P8 provenance-agreement check via the PINNED validator (never a
        # local string compare): check_provenance must return no findings.
        findings, _ = check_provenance(manifest, self.fmap)
        if findings:
            raise PipelineError("ERR_FAMILY_PROVENANCE",
                                "; ".join("%s %s" % fc for fc in findings))
        return path, manifest


# --------------------------------------------------- consumer gate (§9.2)

def check_status_eligibility_jsonl(record_paths, allowlist):
    """§9.2 consumer gate over kernel-v1-draft JSONL shards: builders take an
    explicit eligible-status allowlist and FAIL CLOSED (ERR_STATUS_INELIGIBLE)
    if a record whose semanticStatus is outside it reaches the slot.
    (The pinned check_family_disjoint.check_status_eligibility reads per-file
    .json records with a 'status' field; drafts live in JSONL shards with
    'semanticStatus' — this wrapper applies the identical semantics to the
    shard format; the interface wrinkle is reported for coordinator follow-up.)"""
    if not allowlist:
        return [("ERR_STATUS_INELIGIBLE", "no eligible-status allowlist supplied — the gate never default-passes")]
    findings = []
    for path in record_paths:
        opener = gzip.open if path.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8") as f:
            for i, line in enumerate(f):
                try:
                    rec = json.loads(line)
                except ValueError as e:
                    findings.append(("ERR_STATUS_INELIGIBLE", "%s:%d unreadable (%s)" % (path, i, e)))
                    continue
                status = rec.get("semanticStatus")
                if status not in allowlist:
                    findings.append(("ERR_STATUS_INELIGIBLE",
                                     "%s:%d status %r reaches a slot requiring one of %s"
                                     % (path, i, status, sorted(allowlist))))
    return findings
