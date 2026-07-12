#!/usr/bin/env python3
"""DECONF/1 Stage-B runner — the aligned-generic-store deconfound, GPU cell
(DRAFT registry record registry/experiments/deconf-b.json; freeze-ready spec
docs/next/design/deconf-stageb-spec.md; design DECONF.md rev-B §5;
ASM-0960..0966 + ASM-1010..1017 registered, PROPOSED-ASM-1100..1109 pending
coordinator registration).

WHY THIS EXPERIMENT EXISTS: f2b-transfer stage-2 measured the verifier-offload
lift on blind external gold (+0.2507 absolute, PASS-PENDING-AUDIT); DECONF-A1
measured the pinned checker extensionally computable from the urn-keyed
answer-key projection alone (C_dec = 1.0 over 40,576/40,576 — the GS-A arm is
bit-identical to the kernel arm under the pins). The one question neither
settles: is the ALIGNMENT (the item-aligned deterministic answer key) the
load-bearing ingredient, or does a generic lexical-retrieval store with a
generic menu acceptance signal, at matched budget through the identical retry
topology, reproduce the lift too? Stage B measures exactly
Delta_align = acc_ext(gsa-verify-retry) - acc_ext(gr-d-lite).

RIDER (verbatim, on every Stage-B sentence): self-authored items,
kernel-covered slice, oracle-addressed store; external adjudication removes
membership-gold circularity, not item-generation or store-addressing
circularity. Stage B is a G2-class covered-slice DIAGNOSTIC — never W1, never
G4; BM25-only is a cheap lexical PRECURSOR, never RAGC's "strong generic RAG
baseline"; R-1/135M only, no extrapolation to the 100M-2B rung range.

ARMS (all rung R1 = pinned SmolLM2-135M revision; eval set = ALL 333
resolved-gold_ext d-qa-t items in pinned rank order; seeds {0,1,2,3,4}; k=4):

  model-alone        attempt-0, no store, no retrieval (the shared floor)
  gsa-verify-retry   the GS-A aligned generic answer-key store
                     (poc/deconf-a1/gs-a.jsonl, sha-pinned) behind the
                     UNCHANGED pinned verify-retry loop; emits the RT-7a
                     verifier_engagement block (the arm the bridge gate and
                     the primary's minuend read)
  gr-a-lite          BM25 top-j rendered records injected via the harness's
                     existing context_docs path, attempt-0 only (RAGC GR-A
                     lexical precursor)
  gr-d-lite          gr-a-lite wrapped in the SAME loop shape — same k, same
                     resample rule, same exhaustion semantics — with
                     acceptance = RAGC frozen-menu item (i) self-consistency:
                     m=3 probes, accept iff >=2/3 exact-key agreement
                     (PROPOSED-ASM-1102; plain adoption of ASM-0924/0955)
  kernel-verify-retry OPTIONAL fallback arm (--kernel-arm reinstate,
                     PROPOSED-ASM-1105): the pinned true-record verifier, run
                     ONLY if the A1 registration has not landed at freeze —
                     then GS-A==kernel identity is a measured diagnostic of
                     this run instead of an omission licence
  extraction-instrument  P10 gate re-verification over the pinned d-xif
                     labelled set (R1; CPU-only)

CODE-CHANGE CONTRACT (PROPOSED-ASM-1108): poc/f2b/runner/f2b_runner.py stays
byte-identical at its A1-verified pin (sha b62c3a72...; any edit voids the A1
invariance lemma) and poc/f2b-transfer/runner/f2bt_runner.py stays
byte-identical at its stage-2 staged-bytes pin (sha 810dcbc5...). This module
IMPORTS the pinned machinery (answer_once, build_prompt, run_alone,
run_verify_retry, verify_answer, det_u/backends/CellGuard/Emitter lineage from
the pinned f2bt module; KernelVerifier from the pinned f2b module for the
fallback arm + P10 gate; GSAVerifier from the pinned A1 audit module) and adds
ONLY: the BM25 index/retrieval, the query-construction function + fail-closed
ERR_QUERY_LEAK check, the GR-D-lite loop, and the emit plumbing. All three
imported files are sha-verified BEFORE import (ERR_RUNNER_PIN / ERR_A1_PIN).

STOCHASTICITY KEYING (pinned det_u probe-key schema, PROPOSED-ASM-1102):
  deconfb-detu/1: every GR-D-lite generation calls the existing
  lm.choose(item, keys, gold, seed, attempt_code) scheme with
  attempt_code = attempt*(m+1) + probe_index, m=3; probe_index 0 is the
  candidate, 1..3 the probes; (attempt=0, probe_index=0) is the greedy
  argmax (IF-C attempt-0 semantics, mirroring run_verify_retry); every other
  code samples via torch.Generator(SEED_BASE*10000 + seed*100 + attempt_code)
  with SEED_BASE = 20260710 (the imported pinned f2bt module constant,
  disclosed — keying is shared across arms by (seed, attempt_code); the
  paired analysis conditions on items and claims no cross-arm independence).

RETRIEVAL CONTRACT (PROPOSED-ASM-1103/1104): corpus = the GS-A projection's
own strings, one document per covered record, "<label>: <canonical_text>" —
zero new prose; doc ids = record urns, used ONLY as index keys/tie-breakers,
never readable by the query function. BM25 k1=1.2 b=0.75 lowercase \\w+
tokenizer, stdlib in-repo (no new dependency => no image change). Query =
model-visible prompt bytes ONLY (question + option texts in prompt order for
MC; the claim question for yes/no — the d-qa-t claim template embeds the
claim text verbatim inside the question, so the question already carries
exactly the model-visible claim bytes once; appending the claim again would
duplicate bytes that appear once in the prompt and fail the byte-equality
check below — DISCLOSED instantiation of the spec's §2.3 formula, with the
machine check as the binding contract). Run-time leak check: the query is
re-derived from the RENDERED PROMPT bytes (post-build_prompt, stripping only
the pinned frame constants) and asserted byte-equal (ERR_QUERY_LEAK, fail
closed). top-j floats to fill the 512-token cap (prefix rule: docs added in
score order, ties by lexicographic doc id, stop at the first doc that would
exceed the cap); zero positive-score hits => EMPTY context, no fallback,
zero-hit count a mandatory disclosure; retrieval is deterministic and
seed-invariant per item (computed once, shared across seeds/attempts/probes).
hit@j against the item's pinned record urn is co-reported (diagnostic only —
the pinned urn is consumed in SCORING the diagnostic, never in the query or
context).

Usage:
  python3 stageb_runner.py --out-dir /tmp/deconfb --mock        # stub LM, CPU, $0
  python3 stageb_runner.py --out-dir /tmp/deconfb --dry-plan    # cost plan vs caps
  python3 stageb_runner.py --out-dir /tmp/deconfb --device cuda # real (Modal)

HARD RULES honoured here: --mock and --dry-plan spend $0 and never touch a
GPU or the network; mock numbers are labelled MOCK end-to-end and are never
measurements; real runs fail closed on any missing/mismatched pin (ERR_*).
RAW metrics only — verdicts belong to the pinned analysis/deconf_b.py +
tools/registry/verdict-gen.py under run-vs-audit separation. SAFETY: every
cell runs under the imported CellGuard (per-cell wall-clock timeout +
max-generations-per-item cap, raised to 24 here: GR-D-lite's structural max
is 5 attempts x (1 candidate + 3 probes) = 20); every completed cell's record
is flushed to disk immediately.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
POC = os.path.join(ROOT, "poc")
F2B_RUNNER_PATH = os.path.join(POC, "f2b", "runner", "f2b_runner.py")
F2BT_RUNNER_DIR = os.path.join(POC, "f2b-transfer", "runner")
F2BT_RUNNER_PATH = os.path.join(F2BT_RUNNER_DIR, "f2bt_runner.py")
A1_DIR = os.path.join(POC, "deconf-a1")
A1_AUDIT_PATH = os.path.join(A1_DIR, "audit_a1.py")
GSA_PATH = os.path.join(A1_DIR, "gs-a.jsonl")

# --- byte pins of every imported module (fail closed BEFORE import) ---------
# f2b_runner: the A1-verified sha (deconf-a1 certificate; PROPOSED-ASM-1108 —
# any edit voids the A1 invariance lemma and forces an A1 re-run).
F2B_RUNNER_SHA256_PIN = \
    "b62c3a72882b354f25b97a4b38251fb4863b1c3417220d1c942c84b24fc9b666"
# f2bt_runner: the f2b-transfer stage-2 staged-bytes sha (results-incoming/
# 20260711-184448-modal provenance staged_sha256['runner/f2bt_runner.py']).
F2BT_RUNNER_SHA256_PIN = \
    "810dcbc5105494f0fa188952a509ed80047223409553ce81ea1face273e2a338"
# audit_a1.py: the A1 complete-certificate module (GSAVerifier lineage).
A1_AUDIT_SHA256_PIN = \
    "91f9ed0e60077ed9e69d61391819351fd9f47177bfd2d4fa64366e64fc2ac7b1"
# gs-a.jsonl: the GS-A store as-built (deconf-a1 gsa-manifest; consumed
# as-built, no rebuild — PROPOSED-ASM-1106).
GSA_SHA256_PIN = \
    "4a28f7fae59c85d27fa4bc7d0c7d15d9856f0527fdc0492b00162af7dd41e9d5"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _pin(path, want, err):
    got = sha256_file(path)
    if got != want:
        raise SystemExit("%s: %s sha %s != pinned %s" % (err, path, got, want))


_pin(F2B_RUNNER_PATH, F2B_RUNNER_SHA256_PIN, "ERR_RUNNER_PIN")
_pin(F2BT_RUNNER_PATH, F2BT_RUNNER_SHA256_PIN, "ERR_RUNNER_PIN")
_pin(A1_AUDIT_PATH, A1_AUDIT_SHA256_PIN, "ERR_A1_PIN")
_pin(GSA_PATH, GSA_SHA256_PIN, "ERR_GSA_PIN")

sys.path.insert(0, F2BT_RUNNER_DIR)
sys.path.insert(0, A1_DIR)
import f2bt_runner as T  # noqa: E402  (pinned; brings f0 onto sys.path itself)
from audit_a1 import GSAVerifier  # noqa: E402  (pinned; re-verifies f2b pin)
import f2b_runner as F  # noqa: E402  (importable via audit_a1's path insert)
from f0 import FlopMeter  # noqa: E402

# ---------------------------------------------------------------------------
# Constants — arm names MUST equal analysis/deconf_b.py + registry IV levels
# ---------------------------------------------------------------------------
ARM_ALONE = "model-alone"
ARM_GSA = "gsa-verify-retry"
ARM_GRA = "gr-a-lite"
ARM_GRD = "gr-d-lite"
ARM_KERNEL = "kernel-verify-retry"      # PROPOSED-ASM-1105 fallback only
ARM_IFACE = "extraction-instrument"
ARM_EVALMAN = "eval-manifest"           # one provenance record: ids + types

PROBES_M = 3                            # PROPOSED-ASM-1102 (frozen at design)
ACCEPT_MIN = 2                          # accept iff >= 2/3 probes agree
RETRIEVED_TOKEN_CAP = 512               # PROPOSED-ASM-1103
DETU_SCHEMA = (
    "deconfb-detu/1: lm.choose(item, keys, gold, seed, attempt_code) with "
    "attempt_code = attempt*(m+1) + probe_index, m=3; probe_index 0 = "
    "candidate; (attempt=0, probe_index=0) greedy argmax (IF-C attempt-0 "
    "semantics); all other codes sample via torch.Generator(SEED_BASE*10000 "
    "+ seed*100 + attempt_code), SEED_BASE=20260710 (imported pinned f2bt "
    "module constant)")

# GR-D-lite structural max = (k+1) attempts x (1 candidate + m probes) = 20
# at k=4, so the f2b/f2bt default cap of 16 would trip structurally; 24 can
# only trip on a defect (safety semantics unchanged otherwise).
MAX_GEN_PER_ITEM_DEFAULT = 24
CELL_TIMEOUT_S_DEFAULT = {"A100": 5400.0, "A10G": 5400.0, "T4": 12000.0}


# ---------------------------------------------------------------------------
# BM25 — stdlib in-repo lexical index (PROPOSED-ASM-1103; RAG.md §6.2 BM25 as
# the robust zero-shot lexical baseline). No new dependency => no image change.
# ---------------------------------------------------------------------------
BM25_K1 = 1.2
BM25_B = 0.75
TOKEN_RE = re.compile(r"\w+")


def bm25_tokens(text):
    """Pinned tokenizer: lowercase \\w+ (PROPOSED-ASM-1103)."""
    return TOKEN_RE.findall(text.lower())


class BM25Index:
    """Okapi BM25 (k1=1.2, b=0.75) over the rendered GS-A documents.
    idf = ln(1 + (N - df + 0.5)/(df + 0.5)) — the non-negative (Lucene-form)
    variant, pinned; only documents sharing >= 1 query token receive a score,
    so every returned score is > 0 ('zero positive-score hits' is exactly
    'no returned doc'). Deterministic: docs sorted by doc_id at build."""

    def __init__(self, docs):
        self.docs = sorted(docs, key=lambda d: d["doc_id"])
        self.doc_len = {}
        self.postings = {}
        for d in self.docs:
            toks = bm25_tokens(d["rendered"])
            self.doc_len[d["doc_id"]] = len(toks)
            tf = {}
            for t in toks:
                tf[t] = tf.get(t, 0) + 1
            for t, c in tf.items():
                self.postings.setdefault(t, {})[d["doc_id"]] = c
        self.n_docs = len(self.docs)
        self.avgdl = (sum(self.doc_len.values()) / self.n_docs
                      if self.n_docs else 0.0)

    def scores(self, query):
        out = {}
        for tok in bm25_tokens(query):
            plist = self.postings.get(tok)
            if not plist:
                continue
            df = len(plist)
            idf = math.log(1.0 + (self.n_docs - df + 0.5) / (df + 0.5))
            for doc_id, tf in plist.items():
                dl = self.doc_len[doc_id]
                denom = tf + BM25_K1 * (1 - BM25_B + BM25_B * dl / self.avgdl)
                out[doc_id] = out.get(doc_id, 0.0) + idf * tf * (BM25_K1 + 1) / denom
        return out

    def canonical_blob(self):
        """Canonical-JSON serialisation of the full index state (pinned at
        freeze as bm25IndexSha256; the ledger's index-bytes figure)."""
        body = {"schema": "deconfb-bm25/1", "k1": BM25_K1, "b": BM25_B,
                "tokenizer": "lowercase \\w+", "n_docs": self.n_docs,
                "avgdl": self.avgdl, "doc_len": self.doc_len,
                "postings": self.postings}
        return json.dumps(body, sort_keys=True,
                          separators=(",", ":")).encode("utf-8")


def render_corpus(gsa_rows):
    """The ASM-0922-pinned deterministic text serialisation of the SAME 108
    covered records: one document per GS-A row, '<label>: <canonical_text>'
    from the projection's own columns — no new prose is authored. Doc ids =
    record urns (index keys + tie-breakers ONLY)."""
    docs = []
    for r in gsa_rows:
        labels = r["term_labels"]
        if len(labels) != 1:
            # A1 published the collision list empty; a multi-label row here
            # would be a store drift this runner must not paper over.
            raise SystemExit("ERR_GSA_LABELS: row %s has %d term_labels "
                             "(expected exactly 1)"
                             % (r["concept_id"], len(labels)))
        term, text = labels[0], r["canonical_text"]
        docs.append({"doc_id": r["concept_id"], "term": term, "text": text,
                     "rendered": "%s: %s" % (term, text)})
    return docs


def corpus_canonical_blob(docs):
    lines = [json.dumps({"doc_id": d["doc_id"], "rendered": d["rendered"]},
                        sort_keys=True, separators=(",", ":"))
             for d in docs]
    return ("\n".join(lines) + "\n").encode("utf-8")


# ---------------------------------------------------------------------------
# Query construction + fail-closed leak check (PROPOSED-ASM-1104)
# ---------------------------------------------------------------------------
def query_of_item(item):
    """The published, hash-pinned query function. Reads ONLY prompt-visible
    fields: item['question'] and item['options'][i]['text'] in prompt order.
    NEVER reads urn, record_path, record_sha256, answer/gold, id, type, or
    any metadata. For yes/no claim items the d-qa-t template embeds the claim
    text verbatim inside the question, so the question already carries the
    model-visible claim bytes exactly once (see module docstring)."""
    if item.get("options"):
        return (item["question"] + " "
                + " ".join(o["text"] for o in item["options"]))
    return item["question"]


_OPT_LINE_RE = re.compile(r"^([A-Za-z0-9]{1,3})\. (.*)$")


def query_from_prompt(prompt, frames):
    """Re-derive the query from the RENDERED PROMPT bytes alone, stripping
    only the pinned frame constants (qa_prefix / answer_cue / option_line
    shape). This is the machine check that makes non-oracularity a measured
    property: if query_of_item ever consumed a byte that is not in the
    model-visible prompt, byte-equality below fails (ERR_QUERY_LEAK)."""
    qa, cue = frames["qa_prefix"], frames["answer_cue"]
    if not prompt.startswith(qa) or not prompt.endswith(cue):
        raise SystemExit("ERR_QUERY_LEAK: rendered prompt does not carry the "
                         "pinned frame constants")
    core = prompt[len(qa):len(prompt) - len(cue)]
    lines = core.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]  # MC prompts end the option block with '\n'
    opt_texts = []
    while len(lines) > 1 and _OPT_LINE_RE.match(lines[-1]):
        opt_texts.append(_OPT_LINE_RE.match(lines[-1]).group(2))
        lines = lines[:-1]
    opt_texts.reverse()
    if opt_texts:
        # the '\n' build_prompt inserts between question and option block
        question = "\n".join(lines)
        if question.endswith("\n"):
            question = question[:-1]
        return question + " " + " ".join(opt_texts)
    return core


def query_fn_source_sha256():
    """sha256 over the source of the query + retrieval functions — the
    'query-fn + leak-check source sha256' pin of the frozen record (function-
    granularity freeze discipline on top of the whole-module pin)."""
    src = "".join(inspect.getsource(f) for f in (
        query_of_item, query_from_prompt, bm25_tokens, BM25Index,
        render_corpus, build_retrieval))
    return hashlib.sha256(src.encode("utf-8")).hexdigest()


def build_retrieval(items, index, docs_by_id, frames, count_tokens, cap):
    """Per-item retrieval, computed ONCE (deterministic + seed-invariant per
    item — the retrieved evidence never resamples; PROPOSED-ASM-1103) with
    the fail-closed leak check on every item. Returns (per_item docs-or-None,
    per-item stats rows)."""
    per_item, stats = {}, []
    for it in items:
        base_prompt = T.build_prompt(frames, it)  # model-visible, NO context
        q = query_of_item(it)
        q_rederived = query_from_prompt(base_prompt, frames)
        if q != q_rederived:
            raise SystemExit(
                "ERR_QUERY_LEAK: item %s query != prompt-derived query\n"
                "  query_of_item : %r\n  from_prompt   : %r"
                % (it["id"], q[:200], q_rederived[:200]))
        sc = index.scores(q)
        ranked = sorted(sc.items(), key=lambda kv: (-kv[1], kv[0]))
        chosen, total = [], 0
        for doc_id, _s in ranked:
            d = docs_by_id[doc_id]
            line = "- %s: %s\n" % (d["term"], d["text"])  # build_prompt's shape
            t = count_tokens(line)
            if total + t > cap:
                break  # prefix rule, pinned (docstring)
            chosen.append(d)
            total += t
        zero_hit = not ranked
        per_item[it["id"]] = chosen if chosen else None
        stats.append({"id": it["id"], "n_scored_docs": len(ranked),
                      "n_selected": len(chosen), "context_tokens": total,
                      "zero_hit": zero_hit,
                      # diagnostic ONLY: the pinned urn scores the diagnostic,
                      # never enters query or context construction
                      "hit_at_j": it["urn"] in {d["doc_id"] for d in chosen}})
    return per_item, stats


# ---------------------------------------------------------------------------
# Arm loops that are NEW here (everything else is imported pinned code)
# ---------------------------------------------------------------------------
def run_context_alone(lm, frames, items, docs_by_item, seed, meter, guard):
    """GR-A-lite: the pinned answer_once with retrieved context, attempt-0
    only — the run_alone(context_fn=retrieve) shape of DECONF §5.1, returning
    finals for dual scoring."""
    finals = []
    for it in items:
        guard.start_item(it)
        docs = docs_by_item[it["id"]]
        ans, _conf, lat, toks = T.answer_once(lm, frames, it, seed, 0, docs)
        guard.gen()
        meter.seq(lm, toks)
        meter.query_done(lat)
        finals.append(ans)
    return finals


def run_grd_lite(lm, frames, items, docs_by_item, k, seed, meter, guard):
    """GR-D-lite (PROPOSED-ASM-1102): the SAME loop shape as the pinned
    run_verify_retry — same k, same resample rule, exhaustion => final = LAST
    attempt's candidate, scored — with acceptance = self-consistency (RAGC
    frozen-menu item (i)): m=3 probes of the arm's OWN answer prompt
    (identical frames + item + the SAME retrieved docs), scored by the
    harness's existing closed-space option-scoring; agreement = exact key
    equality; accept iff >= 2/3. No judging template, no free-text parsing
    anywhere. Every probe generation is charged to this arm's ledger row.

    Returns (finals, calibration) — the §2.2 mandatory calibration block:
    acceptance rate, attempt-count distribution, per-attempt agreement
    histogram (0/3..3/3), exhaustion count."""
    finals = []
    calib = {"n_items": 0, "n_accepted": 0, "n_exhausted": 0,
             "accept_attempt_hist": [0] * (k + 1),
             "agree_hist": [0] * (PROBES_M + 1),
             "n_generations": 0}
    for it in items:
        guard.start_item(it)
        docs = docs_by_item[it["id"]]
        calib["n_items"] += 1
        cand = None
        accepted = False
        for attempt in range(k + 1):
            code = attempt * (PROBES_M + 1)  # probe_index 0 = candidate
            cand, _conf, lat, toks = T.answer_once(
                lm, frames, it, seed, code, docs)
            guard.gen()
            meter.seq(lm, toks)
            meter.query_done(lat)
            calib["n_generations"] += 1
            agree = 0
            for j in range(1, PROBES_M + 1):
                probe, _c, lat_p, toks_p = T.answer_once(
                    lm, frames, it, seed, code + j, docs)
                guard.gen()
                meter.seq(lm, toks_p)
                meter.query_done(lat_p)
                calib["n_generations"] += 1
                if probe == cand:
                    agree += 1
            calib["agree_hist"][agree] += 1
            if agree >= ACCEPT_MIN:
                accepted = True
                calib["n_accepted"] += 1
                calib["accept_attempt_hist"][attempt] += 1
                break
            # else REJECT -> resample (next attempt)
        if not accepted:
            calib["n_exhausted"] += 1  # final = LAST attempt, scored
        finals.append(cand)
    return finals, calib


# ---------------------------------------------------------------------------
# Emitter (filename differs from the pinned modules; semantics inherited)
# ---------------------------------------------------------------------------
class Emitter(T.Emitter):
    def __init__(self, out_dir, mock):
        self.records = []
        self.path = os.path.join(
            out_dir, "run-records-deconfb%s.jsonl" % ("-mock" if mock else ""))
        self.phase = "mock" if mock else "final"
        with open(self.path, "w"):
            pass  # truncate once; every record below is an immediate append


def cell_metrics(ext, mem, meter, lms, store_bytes, engagement=None,
                 calibration=None, retrieval=None):
    m = {"item_correct_ext": ext,
         "item_correct_mem": mem,
         "metric_vector": meter.ledger(lms, store_bytes)}
    if engagement is not None:
        m["verifier_engagement"] = engagement
    if calibration is not None:
        m["grd_calibration"] = calibration
    if retrieval is not None:
        m["retrieval_summary"] = retrieval
    return m


# ---------------------------------------------------------------------------
# Input loading + fail-closed pins
# ---------------------------------------------------------------------------
def load_inputs(args):
    with open(os.path.join(args.inputs_dir, "deconfb-manifest.json"),
              encoding="utf-8") as f:
        man = json.load(f)
    pins = man["pins"]
    checks = {
        "dqatCoveredItemsSha256": os.path.join(args.dqat_dir, "items", "covered.jsonl"),
        "dqatManifestSha256": os.path.join(args.dqat_dir, "manifest.json"),
        "dadjtLabelsSha256": os.path.join(args.dadjt_dir, "labels.jsonl"),
        "dadjtSummarySha256": os.path.join(args.dadjt_dir, "summary.json"),
        "dqaCoveredItemsSha256": os.path.join(args.dqa_dir, "items", "covered.jsonl"),
        "dqaManifestSha256": os.path.join(args.dqa_dir, "manifest.json"),
        "gsaStoreSha256": GSA_PATH,
        "gsaManifestSha256": os.path.join(A1_DIR, "gsa-manifest.json"),
        "f2bRunnerSha256": F2B_RUNNER_PATH,
        "f2btRunnerSha256": F2BT_RUNNER_PATH,
        "a1AuditSha256": A1_AUDIT_PATH,
    }
    for key, path in checks.items():
        if sha256_file(path) != pins[key]:
            raise SystemExit("ERR_PIN: %s: %s sha != deconfb-manifest pin"
                             % (key, path))
    for key, base in (("dqatCorpusKotHash", args.dqat_dir),
                      ("dadjtCorpusKotHash", args.dadjt_dir)):
        got = T.corpus_kot_hash(base)
        if got != pins[key]:
            raise SystemExit("ERR_PIN: %s: %s kot-corpus-hash %s != pin %s"
                             % (key, base, got, pins[key]))
    # query-fn + leak-check source pin (function-granularity freeze check)
    got = query_fn_source_sha256()
    if got != pins["queryFnSourceSha256"]:
        raise SystemExit("ERR_PIN: queryFnSourceSha256 %s != pin %s — the "
                         "retrieval/query functions drifted from the frozen "
                         "bytes" % (got, pins["queryFnSourceSha256"]))

    covered_t = T.load_jsonl(checks["dqatCoveredItemsSha256"])
    dqa_covered = T.load_jsonl(checks["dqaCoveredItemsSha256"])
    labels = T.load_jsonl(checks["dadjtLabelsSha256"])
    gsa_rows = T.load_jsonl(GSA_PATH)
    with open(checks["dadjtSummarySha256"], encoding="utf-8") as f:
        adj_summary = json.load(f)
    covered_t.sort(key=lambda x: x["rank"])
    dqa_covered.sort(key=lambda x: x["rank"])

    if adj_summary["analysis_input_metrics"]["labels_sha256"] != \
            pins["dadjtLabelsSha256"]:
        raise SystemExit("ERR_ADJ_PIN: summary.json labels_sha256 != the "
                         "pinned labels.jsonl sha")
    gold_ext = {row["id"]: row["gold_ext"] for row in labels}
    missing = [it["id"] for it in covered_t if it["id"] not in gold_ext]
    if missing:
        raise SystemExit("ERR_LABELS_MISSING: %d d-qa-t items missing from "
                         "labels.jsonl (first: %s)" % (len(missing), missing[0]))
    n_resolved = sum(1 for v in gold_ext.values() if v is not None)
    n_lab_pin = int(adj_summary["analysis_input_metrics"]["n_ext_labelled"])
    if n_resolved != n_lab_pin:
        raise SystemExit("ERR_ADJ_COUNTS: %d resolved gold_ext lines != "
                         "summary n_ext_labelled %d" % (n_resolved, n_lab_pin))
    return man, covered_t, dqa_covered, gold_ext, gsa_rows, adj_summary


def eval_ids_sha256(items):
    """Pinned recipe: sha256 over UTF-8 of one item id per line ('\\n'-
    terminated) in pinned rank order — the frozen record's item-id-list pin."""
    blob = ("\n".join(it["id"] for it in items) + "\n").encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def build_eval_set(man, covered_t, gold_ext, mock):
    """EVAL SET (PROPOSED-ASM-1100): ALL resolved-gold_ext d-qa-t items in
    pinned rank order — every one of the n_ext_labelled = 333 externally
    labelled items; NOT the stage-2 250-prefix (Stage B is a fresh prereg and
    pins all 333; the A1 certificate enumerated the full 360-item grid, so
    GS-A<->kernel concordance covers every eval item). Fail closed on any
    count or id-list drift."""
    dc = man["design_constants"]
    eval_items = [it for it in covered_t if gold_ext[it["id"]] is not None]
    n_want = int(dc["n_items"])
    if len(eval_items) != n_want:
        raise SystemExit("ERR_EVAL_N: %d resolved-gold_ext items != the "
                         "pre-registered n_items %d — refusing"
                         % (len(eval_items), n_want))
    got = eval_ids_sha256(eval_items)
    if got != man["pins"]["evalItemIdsSha256"]:
        raise SystemExit("ERR_EVAL_IDS: item-id-list sha %s != pin %s"
                         % (got, man["pins"]["evalItemIdsSha256"]))
    for it in eval_items:
        if it.get("type") not in T.DQA_TYPES or not it.get("kernel_checkable"):
            raise SystemExit("ERR_ITEM_CHECKABLE: eval item %s is not a "
                             "kernel-checkable DQA-type item" % it["id"])
        keys, _gold = T.item_keys_gold(it)
        if gold_ext[it["id"]] not in keys:
            raise SystemExit("ERR_GOLD_SURFACE: %s gold_ext %r not on the "
                             "item's answer surface %s"
                             % (it["id"], gold_ext[it["id"]], keys))
    if mock:
        eval_items = eval_items[:man["mock"]["n_eval_items"]]
    return eval_items


# ---------------------------------------------------------------------------
# --dry-plan: the real-run cost plan vs the caps. Stdlib only; ESTIMATES.
# ---------------------------------------------------------------------------
def dry_plan(man, eval_items, gpu, kernel_arm):
    plan = man["planning"]
    dc = man["design_constants"]
    frames = man["prompt_frames"]
    cpt = plan["chars_per_token_estimate"]
    tput = plan["throughput_tok_per_s"][gpu]["R1"]
    usd = man["flop_accounting"]["usd_per_hour"][gpu]
    seeds, k = dc["seeds"], int(dc["retry_k"])
    ctx_extra = plan["context_prompt_extra_tokens"]

    def est_tokens(item, ctx=False):
        keys, _ = T.item_keys_gold(item)
        t = len(T.build_prompt(frames, item)) / cpt + (ctx_extra if ctx else 0)
        return t * len(keys)

    tok_plain = sum(est_tokens(i) for i in eval_items)
    tok_ctx = sum(est_tokens(i, True) for i in eval_items)
    per_seed = (tok_plain                              # model-alone
                + tok_ctx                              # gr-a-lite
                + tok_plain * (k + 1)                  # gsa-verify-retry
                + tok_ctx * (k + 1) * (1 + PROBES_M))  # gr-d-lite worst
    if kernel_arm:
        per_seed += tok_plain * (k + 1)                # fallback kernel arm
    total_tok = per_seed * len(seeds)
    est_h = total_tok / tput / 3600.0
    worst_h = est_h * plan["overhead_factor"]
    cap = dc["budget"]
    lines = [
        "deconf-b Stage-B --dry-plan (ESTIMATES ONLY — planning constants from",
        "deconfb-manifest.json; no GPU, no network, $0 spent by this command)",
        "",
        "eval set: %d resolved-gold_ext d-qa-t items x %d seeds, k=%d, m=%d "
        "probes; kernel fallback arm: %s"
        % (len(eval_items), len(seeds), k, PROBES_M,
           "REINSTATED (+PROPOSED-ASM-1105 fallback)" if kernel_arm else "omitted"),
        "worst-case generations: %d"
        % (len(eval_items) * len(seeds)
           * (1 + 1 + (k + 1) + (k + 1) * (1 + PROBES_M)
              + ((k + 1) if kernel_arm else 0))),
        "",
        "GPU-hours estimate on %s (R1 %.0f tok/s): %.2f h; with %.1fx overhead: %.2f h"
        % (gpu, tput, est_h, plan["overhead_factor"], worst_h),
        "cost: point $%.2f, worst $%.2f, hard ceiling $%.2f (gpu_hours_cap %g h)"
        % (est_h * usd, worst_h * usd, cap["gpu_hours_cap"] * usd,
           cap["gpu_hours_cap"]),
        "caps: usd_cap $%g, gpu_hours_cap %g h, wall_clock_cap %g h"
        % (cap["usd_cap"], cap["gpu_hours_cap"], cap["wall_clock_cap_hours"]),
        "",
    ]
    verdicts = [
        ("worst case vs usd_cap ($%g)" % cap["usd_cap"],
         worst_h * usd <= cap["usd_cap"]),
        ("worst case vs gpu_hours_cap (%g h)" % cap["gpu_hours_cap"],
         worst_h <= cap["gpu_hours_cap"]),
    ]
    for name, ok in verdicts:
        lines.append("  %-42s %s" % (name, "OK" if ok else "OVER — DO NOT LAUNCH"))
    lines.append("")
    lines.append("spend stop (PROPOSED-ASM-1109): exhaustion before the primary")
    lines.append("readout = scientific stop + salvage, no retry.")
    print("\n".join(lines))
    return all(ok for _n, ok in verdicts)


# ---------------------------------------------------------------------------
# Cell driver
# ---------------------------------------------------------------------------
def run_cells(args, man, eval_items, dqa_covered, gold_ext, gsa_rows,
              emit, log):
    mock = args.mock
    dc = man["design_constants"]
    frames = man["prompt_frames"]
    seeds = man["mock"]["seeds"] if mock else dc["seeds"]
    k = int(dc["retry_k"])
    kernel_arm = args.kernel_arm == "reinstate"

    if not mock:
        if not os.path.isdir(args.dxif_dir or ""):
            raise SystemExit("ERR_MISSING_DXIF: d-xif labelled extraction set "
                             "missing — the P10 instrument gate cannot be "
                             "measured; refusing a final-phase run")
        for key, rel in (("dxifOutputsR1Sha256", os.path.join("outputs", "r1.jsonl")),
                         ("dxifManifestSha256", "manifest.json")):
            pin = man["pins"].get(key)
            path = os.path.join(args.dxif_dir, rel)
            if not pin or sha256_file(path) != pin:
                raise SystemExit("ERR_PIN: %s: %s sha != deconfb-manifest pin"
                                 % (key, path))
        iface_n = dc["iface_gate"]["n_min_per_rung"]
    else:
        iface_n = man["mock"]["iface_n_labelled"]

    # ---- stores ---------------------------------------------------------------
    gsa = GSAVerifier(gsa_rows)
    gsa.index_labels(eval_items)          # pinned eager init over eval items
    kernel = None
    if kernel_arm or not mock:
        # the P10 gate (real path) + fallback arm use the literal A1-audited
        # pinned checker class over the true records (record shas re-verified
        # per item by _load, ERR_RECORD_PIN)
        kernel = F.KernelVerifier(args.records_root)
        kernel.index_labels(eval_items)

    # ---- BM25 store (CPU; build cost on the ledger, ASM-0925 shape) ----------
    t_b = time.perf_counter()
    docs = render_corpus(gsa_rows)
    docs_by_id = {d["doc_id"]: d for d in docs}
    corpus_blob = corpus_canonical_blob(docs)
    corpus_sha = hashlib.sha256(corpus_blob).hexdigest()
    index = BM25Index(docs)
    index_blob = index.canonical_blob()
    index_sha = hashlib.sha256(index_blob).hexdigest()
    bm25_build_s = time.perf_counter() - t_b
    for key, got in (("bm25CorpusSha256", corpus_sha),
                     ("bm25IndexSha256", index_sha)):
        if man["pins"][key] != got:
            raise SystemExit("ERR_PIN: %s %s != pin %s"
                             % (key, got, man["pins"][key]))
    log("BM25 store: %d docs, corpus sha %s…, index sha %s…, build %.3fs, "
        "index %d bytes" % (len(docs), corpus_sha[:12], index_sha[:12],
                            bm25_build_s, len(index_blob)))

    def make_lm(rung="R1"):
        if mock:
            lm = T.StubLM(rung, man["mock"])
            lm.mock_xfail = man["mock"]["stub_extraction_fail_rate"]
            return lm
        spec = man["models"][rung]
        return T.HFLM(spec["repo"], spec["revision"], args.device)

    lm1 = make_lm("R1")
    fc = man["flop_accounting"]
    gpu = args.gpu_class

    def new_meter():
        return FlopMeter(fc, gpu)

    # ---- retrieval: once per item, seed-invariant, leak-checked --------------
    docs_by_item, retr_stats = build_retrieval(
        eval_items, index, docs_by_id, frames, lm1.count_tokens,
        int(dc["retrieved_token_cap"]))
    retr_agg = {
        "n_items": len(retr_stats),
        "zero_hit_count": sum(1 for r in retr_stats if r["zero_hit"]),
        "hit_at_j_count": sum(1 for r in retr_stats if r["hit_at_j"]),
        "mean_selected_docs": (sum(r["n_selected"] for r in retr_stats)
                               / max(1, len(retr_stats))),
        "mean_context_tokens": (sum(r["context_tokens"] for r in retr_stats)
                                / max(1, len(retr_stats))),
        "token_cap": int(dc["retrieved_token_cap"]),
    }
    with open(os.path.join(args.out_dir, "retrieval-stats.json"), "w") as f:
        json.dump({"aggregate": retr_agg, "per_item": retr_stats}, f,
                  indent=1, sort_keys=True)
        f.write("\n")
    log("retrieval built: zero-hit %d/%d, hit@j %d/%d, mean docs %.2f, "
        "mean ctx tokens %.1f (leak check passed on every item)"
        % (retr_agg["zero_hit_count"], retr_agg["n_items"],
           retr_agg["hit_at_j_count"], retr_agg["n_items"],
           retr_agg["mean_selected_docs"], retr_agg["mean_context_tokens"]))

    store_bytes_gsa = os.path.getsize(GSA_PATH)
    store_bytes_bm25 = len(corpus_blob) + len(index_blob)
    store_bytes_records = sum(
        os.path.getsize(os.path.join(args.records_root, p))
        for p in sorted({it["record_path"] for it in eval_items
                         if it.get("record_path")}))

    # ---- eval-manifest provenance record (ids + types, once) -----------------
    emit.emit(ARM_EVALMAN, "R1", 0, 0, 0, {
        "eval_item_ids_sha256": eval_ids_sha256(eval_items),
        "item_ids": [it["id"] for it in eval_items],
        "item_types": [it["type"] for it in eval_items],
        "detu_schema": DETU_SCHEMA,
        "bm25": {"corpus_sha256": corpus_sha, "index_sha256": index_sha,
                 "k1": BM25_K1, "b": BM25_B, "tokenizer": "lowercase \\w+",
                 "n_docs": len(docs), "build_cpu_s": bm25_build_s,
                 "corpus_bytes": len(corpus_blob),
                 "index_bytes": len(index_blob)},
        "retrieval_aggregate": retr_agg,
        "query_fn_source_sha256": query_fn_source_sha256(),
        "kernel_arm": args.kernel_arm})

    # ---- per-cell safety driver (f2b-replicate correction 1, carried over) ---
    def run_cell(arm, rung, kk, seed, fn):
        guard = T.CellGuard("%s/%s/k=%s/seed=%s" % (arm, rung, kk, seed),
                            args.cell_timeout_s, args.max_gen_per_item)
        try:
            metrics = fn(guard)
        except T.CellBudgetExceeded as e:
            emit.emit(arm, rung, kk, 0, seed, {
                "cell_budget_exceeded": {
                    "kind": e.kind, "item_id": e.item_id,
                    "elapsed_s": round(e.elapsed_s, 1),
                    "n_gen_on_item_at_breach": e.n_gen,
                    "cell_timeout_s": args.cell_timeout_s,
                    "max_gen_per_item": args.max_gen_per_item},
                "note": "INSTRUMENT event: cell self-terminated at its safety "
                        "bound; exit!=ok, so this record can never be an "
                        "eligible run record (no item_correct is fabricated)"},
                exit_status="timeout")
            log("ERR_CELL_TIMEOUT: %s" % e)
            raise SystemExit(
                "ERR_CELL_TIMEOUT: %s — run aborted in bounded time; all "
                "completed cells are flushed in %s" % (e, emit.path))
        emit.emit(arm, rung, kk, 0, seed, metrics)
        log("cell %s %s k=%s seed=%s done (%.1fs)"
            % (arm, rung, kk, seed, guard.elapsed()))
        return metrics

    # ---- model-alone (the shared floor) ---------------------------------------
    for seed in seeds:
        def cell(guard, seed=seed):
            meter = new_meter()
            finals = T.run_alone(lm1, frames, eval_items, seed, meter, guard)
            ext, mem = T.score_dual(eval_items, finals, gold_ext)
            return cell_metrics(ext, mem, meter, [lm1], 0)
        run_cell(ARM_ALONE, "R1", 0, seed, cell)

    # ---- gsa-verify-retry (the aligned answer-key arm; RT-7a block) ----------
    for seed in seeds:
        def cell(guard, seed=seed):
            meter = new_meter()
            finals, eng, _xf = T.run_verify_retry(
                lm1, frames, eval_items, gsa, k, seed, meter, guard)
            ext, mem = T.score_dual(eval_items, finals, gold_ext)
            return cell_metrics(ext, mem, meter, [lm1], store_bytes_gsa,
                                engagement=eng)
        run_cell(ARM_GSA, "R1", k, seed, cell)

    # ---- gr-a-lite (BM25 context, attempt-0) ----------------------------------
    for seed in seeds:
        def cell(guard, seed=seed):
            meter = new_meter()
            finals = run_context_alone(lm1, frames, eval_items, docs_by_item,
                                       seed, meter, guard)
            ext, mem = T.score_dual(eval_items, finals, gold_ext)
            return cell_metrics(ext, mem, meter, [lm1], store_bytes_bm25,
                                retrieval=retr_agg)
        run_cell(ARM_GRA, "R1", 0, seed, cell)

    # ---- gr-d-lite (BM25 context + self-consistency retry) --------------------
    for seed in seeds:
        def cell(guard, seed=seed):
            meter = new_meter()
            finals, calib = run_grd_lite(lm1, frames, eval_items,
                                         docs_by_item, k, seed, meter, guard)
            ext, mem = T.score_dual(eval_items, finals, gold_ext)
            return cell_metrics(ext, mem, meter, [lm1], store_bytes_bm25,
                                calibration=calib, retrieval=retr_agg)
        run_cell(ARM_GRD, "R1", k, seed, cell)

    # ---- kernel-verify-retry (PROPOSED-ASM-1105 fallback ONLY) ---------------
    if kernel_arm:
        for seed in seeds:
            def cell(guard, seed=seed):
                meter = new_meter()
                finals, eng, _xf = T.run_verify_retry(
                    lm1, frames, eval_items, kernel, k, seed, meter, guard)
                ext, mem = T.score_dual(eval_items, finals, gold_ext)
                return cell_metrics(ext, mem, meter, [lm1],
                                    store_bytes_records, engagement=eng)
            run_cell(ARM_KERNEL, "R1", k, seed, cell)

    # ---- P10 extraction-instrument gate (R1) ----------------------------------
    def cell_iface(guard):
        if mock:
            gate_v = GSAVerifier(gsa_rows)
            gate_v.index_labels(eval_items)
            return T.run_extraction_instrument_mock(
                lm1, frames, eval_items, gate_v, iface_n, seeds[0], guard)
        gate_verifier = F.KernelVerifier(args.records_root)
        gate_verifier.index_labels(dqa_covered)
        st = T.run_extraction_instrument_dxif(args.dxif_dir, "R1",
                                              dqa_covered, gate_verifier)
        if st["n_labelled"] < iface_n:
            raise SystemExit("ERR_DXIF_N: R1 has %d labelled outputs < the "
                             "pre-registered n_min_per_rung %d"
                             % (st["n_labelled"], iface_n))
        return st
    stats = run_cell(ARM_IFACE, "R1", 0, seeds[0], cell_iface)
    log("iface gate: %d labelled, %d extraction failures"
        % (stats["n_labelled"], stats["n_extraction_failures"]))

    return {"bm25_build_cpu_s": bm25_build_s,
            "bm25_corpus_sha256": corpus_sha, "bm25_index_sha256": index_sha,
            "bm25_corpus_bytes": len(corpus_blob),
            "bm25_index_bytes": len(index_blob),
            "retrieval_aggregate": retr_agg}


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs-dir", default=os.path.join(HERE, "inputs"))
    ap.add_argument("--dqat-dir", default=os.path.join(ROOT, "data", "d-qa-t"))
    ap.add_argument("--dadjt-dir", default=os.path.join(ROOT, "data", "d-adj-t"))
    ap.add_argument("--dqa-dir", default=os.path.join(ROOT, "data", "d-qa"))
    ap.add_argument("--records-root", default=ROOT,
                    help="root that item record_path fields resolve against")
    ap.add_argument("--dxif-dir", default=None,
                    help="d-xif labelled extraction set (REQUIRED for real runs)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--gpu-class", default="A100", choices=["T4", "A10G", "A100"])
    ap.add_argument("--kernel-arm", default="omit", choices=["omit", "reinstate"],
                    help="PROPOSED-ASM-1105: 'reinstate' ONLY if the A1 "
                         "registration has not landed at freeze (the frozen "
                         "record pins the choice; the runner records it)")
    ap.add_argument("--mock", action="store_true",
                    help="stub-LM mechanics check on CPU; $0; labelled MOCK")
    ap.add_argument("--dry-plan", action="store_true",
                    help="print the real-run cost plan vs caps; runs nothing")
    ap.add_argument("--max-hours", type=float, default=10.0)
    ap.add_argument("--cell-timeout-s", type=float, default=None)
    ap.add_argument("--max-gen-per-item", type=int,
                    default=MAX_GEN_PER_ITEM_DEFAULT,
                    help="per-item generation cap within one cell (structural "
                         "max is 20: gr-d-lite at k=4, m=3)")
    args = ap.parse_args()
    if args.cell_timeout_s is None:
        args.cell_timeout_s = CELL_TIMEOUT_S_DEFAULT[args.gpu_class]
    t0 = time.time()

    man, covered_t, dqa_covered, gold_ext, gsa_rows, adj_summary = \
        load_inputs(args)
    eval_items = build_eval_set(man, covered_t, gold_ext, args.mock)

    if args.dry_plan:
        full_eval = build_eval_set(man, covered_t, gold_ext, mock=False)
        ok = dry_plan(man, full_eval, args.gpu_class,
                      args.kernel_arm == "reinstate")
        sys.exit(0 if ok else 2)

    os.makedirs(args.out_dir, exist_ok=True)

    def log(msg):
        print("[deconfb %7.1fs] %s" % (time.time() - t0, msg), flush=True)

    label = "MOCK" if args.mock else "FULL"
    log("mode=%s device=%s eval_items=%d (ALL resolved-gold_ext d-qa-t items "
        "in pinned rank order) kernel_arm=%s"
        % (label, args.device, len(eval_items), args.kernel_arm))
    if not args.mock and args.device != "cuda":
        log("WARNING: real run requested on CPU — allowed but slow")

    emit = Emitter(args.out_dir, args.mock)
    artifacts = run_cells(args, man, eval_items, dqa_covered, gold_ext,
                          gsa_rows, emit, log)
    records_path = emit.write()

    hours = (time.time() - t0) / 3600.0
    if hours > args.max_hours:
        raise SystemExit("ERR_TIME_BUDGET: exceeded %.1fh" % args.max_hours)

    try:
        import resource
        peak_rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except Exception:  # noqa: BLE001
        peak_rss_kb = None

    suffix = "-mock" if args.mock else ""
    results = {
        "experiment": "deconf-b",
        "outcome": ("MOCK-HARNESS-COMPLETE" if args.mock else "HARNESS-COMPLETE"),
        "outcome_note": "NOT a hypothesis verdict — raw run-records only; the "
                        "verdict is computed by the pinned analysis/deconf_b.py "
                        "+ tools/registry/verdict-gen.py under run-vs-audit "
                        "separation. Rider on every downstream sentence: "
                        "self-authored items, kernel-covered slice, "
                        "oracle-addressed store; external adjudication removes "
                        "membership-gold circularity, not item-generation or "
                        "store-addressing circularity.",
        "mode": label,
        "date": T.utcnow(),
        "device": args.device,
        "gpu_class_assumed_for_usd": args.gpu_class,
        "pins": man["pins"],
        "models": ({"note": "MOCK — synthetic stub LM, no models loaded"}
                   if args.mock else {"R1": man["models"]["R1"]}),
        "kernel_arm": args.kernel_arm,
        "detu_schema": DETU_SCHEMA,
        "n_records": len(emit.records),
        "n_eval_items": len(eval_items),
        "records_file": os.path.basename(records_path),
        "seeds": man["mock"]["seeds"] if args.mock else
                 man["design_constants"]["seeds"],
        "retry_k": man["design_constants"]["retry_k"],
        "probes_m": PROBES_M,
        "accept_threshold": "%d/%d" % (ACCEPT_MIN, PROBES_M),
        "retrieved_token_cap": man["design_constants"]["retrieved_token_cap"],
        "lifecycle_ledger": dict(artifacts,
                                 peak_rss_kb=peak_rss_kb,
                                 gsa_store_bytes=os.path.getsize(GSA_PATH)),
        "wallClockHours": hours,
    }
    with open(os.path.join(args.out_dir, "results-deconfb%s.json" % suffix),
              "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    print("[deconfb] query-fn source sha256: %s" % query_fn_source_sha256())
    print("[deconfb] OUTCOME: %s (%d run-record bodies in %s)"
          % (results["outcome"], len(emit.records), records_path))


if __name__ == "__main__":
    main()
