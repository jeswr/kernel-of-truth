#!/usr/bin/env python3
"""F2 — verifier-offload on definitional QA (the Tier-1 pivot experiment).

The ONLY thing the GPU runs. Implements the FROZEN arm set of
registry/experiments/f2.json (HE1 primary; HE2 cascade, HC3 PRM, HS12
placement riders; P1 sections 3, design-efficiency-track.md section 4.2 as
amended by P7 RT-2) on the pinned D-QA corpus, and emits RAW kot-log/1
metric bodies whose keys match the pinned analysis script analysis/f2.py
(sha 068f68b8...) exactly. NO derived statistics are computed here —
verdicts belong to analysis/f2.py + verdict-gen (run-vs-audit separation).

Arms (independent-variable levels, VERBATIM from the frozen record):
  model-alone                          R1/R2/R3 baselines (arms 1-3)
  kernel-verify-retry                  135M + kernel decode-verify, k in {1,2,4} (arm 4)
  kernel-as-text                       Law-2 text null (arm 5)
  rag-over-text                        BM25 over the pinned gloss corpus (arm 6)
  self-consistency-flop-matched        matched-compute sampling (arm 7)
  gloss-self-verify-retry              P7 RT-2 arm 10 — the strongest ACTIVE text baseline
  prm-verifier                         HC3 trained-PRM comparator (EF3)
  int4-quantized                       practitioner null (int4 360M, arm 9)
  cascade-verifier-gated-135m-1p7b     F2b/HE2 (arm 8)
  cascade-logprob-gated-135m-1p7b      free-calibration gate
  cascade-text-self-check-gated-135m-1p7b  RT-2 cascade gate
  cascade-in-decode-gated-135m-1p7b    EF5/HS12 placement rider (latency both modes)
  extraction-instrument                P10 extraction-failure gate measurement

Shared affordance (P10 section 5, IF-C default): EVERY arm answers through
the same constrained-decoding surface — selection over the pinned option set
(A-D / yes-no) by sequence logprob. Arms differ only in context block and
verification instrument.

Usage:
  python3 f2_runner.py --inputs-dir ../inputs --dqa-dir ../../../data/d-qa \
      --records-root ../../.. --out-dir /tmp/f2 --device cuda      # real (Modal)
  python3 f2_runner.py ... --mock            # stub-LM mechanics check, CPU, ~1 min, $0
  python3 f2_runner.py ... --dry-plan        # cost plan vs Tier-1 cap; runs nothing

HARD RULES honoured here: --mock and --dry-plan spend $0 and never touch a
GPU or the network; mock numbers are labelled MOCK end-to-end and are never
measurements; real runs fail closed on any missing pin (ERR_*).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import time

# F0 flop-meter — promoted to the shared poc/f0/ package (the `f0-harness`
# depends_on gate; design-efficiency-track.md section 3). poc/ is resolved
# relative to this file so the import works both in-repo and on the Modal
# stage (/root/kot/poc/f2/runner -> /root/kot/poc/f0).
_POC_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."))
if _POC_DIR not in sys.path:
    sys.path.insert(0, _POC_DIR)
from f0 import FlopMeter  # noqa: E402

# ---------------------------------------------------------------------------
# Constants — arm names MUST equal analysis/f2.py + registry IV levels
# ---------------------------------------------------------------------------
ARM_ALONE = "model-alone"
ARM_VERIFY = "kernel-verify-retry"
ARM_TEXT = "kernel-as-text"
ARM_RAG = "rag-over-text"
ARM_SC = "self-consistency-flop-matched"
ARM_SELFV = "gloss-self-verify-retry"
ARM_PRM = "prm-verifier"
ARM_INT4 = "int4-quantized"
ARM_CV = "cascade-verifier-gated-135m-1p7b"
ARM_CL = "cascade-logprob-gated-135m-1p7b"
ARM_CT = "cascade-text-self-check-gated-135m-1p7b"
ARM_CD = "cascade-in-decode-gated-135m-1p7b"
ARM_IFACE = "extraction-instrument"

CASCADE_ARMS = (ARM_CV, ARM_CL, ARM_CT, ARM_CD)
SEED_BASE = 20260708  # published fixed base seed (matches the f2 SAP PRNG seed)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utcnow():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def det_u(*keys):
    """Deterministic uniform in [0,1) from sha256 over the key tuple
    (build-dqa.py determinism discipline: no wall-clock, no PRNG state)."""
    raw = "\x1f".join(str(k) for k in keys)
    h = hashlib.sha256(raw.encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") / 2.0 ** 64


# ---------------------------------------------------------------------------
# Canonical-record rendering — VERBATIM from data/d-qa/build-dqa.py so the
# verifier's canonical text is byte-identical to the item builder's.
# ---------------------------------------------------------------------------
URN_MARKUP_RE = re.compile(r"\{urn:[^|}]+\|([^}]*)\}")
MIN_SEGMENT_CHARS = 15  # = build-dqa.py MIN_SEGMENT_CHARS


def render_plain(text):
    text = URN_MARKUP_RE.sub(r"\1", text)
    text = text.replace(" [m]", "").replace("[m]", "")
    return re.sub(r"  +", " ", text).strip()


def segments(gloss):
    out = []
    for seg in re.split(r"[.;]", gloss):
        seg = seg.strip()
        if len(seg) >= MIN_SEGMENT_CHARS and '"' not in seg and seg not in out:
            out.append(seg)
    return out


def norm_text(t):
    return re.sub(r"\s+", " ", t.strip().rstrip(".")).lower()


# ---------------------------------------------------------------------------
# Kernel verifier — the deterministic instrument (REAL code in mock and full).
# Decode-verify per P1 HC1/HE1: the constrained-decode record is checked
# against the canonical record bytes (per-item record_sha256 pin, fail closed).
# ---------------------------------------------------------------------------
class KernelVerifier:
    def __init__(self, records_root):
        self.root = records_root
        self._by_urn = {}
        self._by_label = {}
        self._sha_ok = set()

    def _load(self, item):
        urn = item["urn"]
        if urn in self._by_urn:
            return self._by_urn[urn]
        path = os.path.join(self.root, item["record_path"])
        if path not in self._sha_ok:
            if sha256_file(path) != item["record_sha256"]:
                raise SystemExit("ERR_RECORD_PIN: %s sha != item record_sha256 (%s)"
                                 % (item["record_path"], item["id"]))
            self._sha_ok.add(path)
        with open(path, encoding="utf-8") as f:
            rec = json.load(f)
        canon = (rec["gloss"].strip() if "gloss" in rec
                 else render_plain(rec["groundingNote"]))
        entry = {"urn": urn, "label": rec["label"], "text": canon,
                 "claims": segments(canon)}
        self._by_urn[urn] = entry
        self._by_label[rec["label"].lower()] = entry
        return entry

    def index_labels(self, items):
        """Pre-load every covered record so term-match option labels resolve."""
        for it in items:
            if it.get("kernel_checkable"):
                self._load(it)

    def check(self, record, item):
        """record -> (decidable, consistent). Deterministic; CPU-only.

        def-match:  asserted definition text == canonical rendering
        term-match: canonical rendering of the CHOSEN label == the shown definition
        claim:      claim-segment membership in the canonical clause set vs verdict
        Control items (kernel_checkable false) are UNDECIDABLE — the verifier
        abstains (measures off-coverage behaviour; d-qa README).
        """
        if not item.get("kernel_checkable"):
            return False, False
        t0 = time.perf_counter()
        entry = self._load(item)
        kind = record.get("kind")
        if kind == "definition":
            ok = norm_text(record["text"]) == norm_text(entry["text"])
        elif kind == "term-for-definition":
            chosen = self._by_label.get(record["term"].lower())
            ok = (chosen is not None
                  and norm_text(chosen["text"]) == norm_text(record["definition"]))
        elif kind == "claim":
            member = any(norm_text(record["claim"]) == norm_text(c)
                         for c in entry["claims"])
            ok = member == (record["verdict"] == "yes")
        else:
            raise SystemExit("ERR_RECORD_KIND: %r" % kind)
        self.last_cpu_s = time.perf_counter() - t0
        return True, ok


def extract_record(item, answer):
    """P10 IF-C extraction: constrained answer -> kernel-checkable record.

    Under constrained decoding a malformed record is an OBSERVABLE event:
    return None on any structural failure (counted on the instrument ledger,
    never scored as a kernel success or failure — P10 section 4)."""
    try:
        if item["type"] in ("def-match", "control:def-match"):
            opt = {o["key"]: o["text"] for o in item["options"]}[answer]
            return {"kind": "definition", "urn": item["urn"], "text": opt}
        if item["type"] in ("term-match", "control:term-match"):
            opt = {o["key"]: o["text"] for o in item["options"]}[answer]
            return {"kind": "term-for-definition", "urn": item["urn"],
                    "term": opt, "definition": None}  # definition filled by caller
        # claim-true / claim-false
        if answer not in ("yes", "no"):
            return None
        return {"kind": "claim", "urn": item["urn"], "claim": item["claim"],
                "verdict": answer}
    except (KeyError, TypeError):
        return None


# ---------------------------------------------------------------------------
# BM25 retrieval over the pinned gloss corpus (deterministic; rag-index.json)
# ---------------------------------------------------------------------------
TOKEN_RE = re.compile(r"[a-z]+")


class BM25:
    def __init__(self, index, docs):
        self.df = index["df"]
        self.avgdl = index["avgdl"]
        self.k1 = index.get("k1", 1.2)
        self.b = index.get("b", 0.75)
        self.n_docs = index.get("n_docs", len(docs))
        self.docs = docs

    def top(self, query, k):
        q_terms = TOKEN_RE.findall(query.lower())
        scored = []
        for doc in self.docs:
            terms = TOKEN_RE.findall(doc["text"].lower())
            dl = len(terms)
            tf = {}
            for t in terms:
                tf[t] = tf.get(t, 0) + 1
            s = 0.0
            for t in q_terms:
                if t not in tf or t not in self.df:
                    continue
                idf = math.log(1 + (self.n_docs - self.df[t] + 0.5) / (self.df[t] + 0.5))
                s += idf * tf[t] * (self.k1 + 1) / (
                    tf[t] + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
            scored.append((-s, doc["doc_id"], doc))
        scored.sort(key=lambda x: (x[0], x[1]))  # deterministic tie-break
        return [d for _, _, d in scored[:k]]


# ---------------------------------------------------------------------------
# LM backends — one interface, two implementations.
# ---------------------------------------------------------------------------
class StubLM:
    """SYNTHETIC mechanics-only stand-in (mock mode; no torch).

    Every output is a deterministic function of (rung, seed, item, attempt)
    via sha256 — reproducible, zero-cost, clearly labelled MOCK. The planted
    per-rung skill gradient exists ONLY so the analysis contract's gap
    denominators resolve during mock validation (mirrors analysis/f2.py's own
    constructed selftest cells). Never a measurement."""

    def __init__(self, rung, mock_spec, int4=False):
        self.rung = rung
        self.int4 = int4
        self.skill = (mock_spec["stub_skill_int4"] if int4
                      else mock_spec["stub_skill"][rung])
        self.ctx_bonus = mock_spec["stub_context_bonus"]
        self.check_skill = mock_spec["stub_self_check_skill"]
        dims = mock_spec["stub_dims"][rung]
        self.n_active = dims["n_active"]
        self.layers = dims["layers"]
        self.d_attn = dims["d_attn"]
        self.name = "stub-%s%s" % (rung, "-int4" if int4 else "")
        self.weight_bytes = int(self.n_active * (0.5 if int4 else 2))

    def count_tokens(self, text):
        return max(1, len(text.split()))

    def choose(self, item, keys, gold, seed, attempt, has_context=False):
        """Constrained selection among `keys`; returns (answer, confidence)."""
        p = min(0.98, self.skill + (self.ctx_bonus if has_context else 0.0))
        u = det_u("ans", self.name, item["id"], seed, attempt)
        if u < p:
            ans = gold
        else:
            wrong = [k for k in keys if k != gold]
            ans = wrong[int(det_u("wr", self.name, item["id"], seed, attempt)
                            * len(wrong))]
        # confidence correlates with correctness so the logprob gate has signal
        c = det_u("conf", self.name, item["id"], seed, attempt)
        conf = 0.5 + 0.5 * c if ans == gold else 0.5 * c
        return ans, conf

    def self_check(self, item, answer, gold, seed, attempt):
        """Gloss-text self-verify: 'is my answer right?' yes/no."""
        truth = answer == gold
        u = det_u("chk", self.name, item["id"], seed, attempt)
        return truth if u < self.check_skill else (not truth)


class StubPRM:
    """SYNTHETIC PRM re-ranker stand-in (mock only)."""

    def __init__(self, mock_spec):
        self.skill = mock_spec["stub_prm_skill"]
        self.n_active = 500000
        self.weight_bytes = self.n_active * 2
        self.name = "stub-prm"

    def score(self, item, answer, gold, seed, idx):
        u = det_u("prm", item["id"], answer, seed, idx)
        return 0.5 + 0.5 * u if (answer == gold) == (u < self.skill) else 0.5 * u


class HFPRM:
    """HC3/EF3 trained-PRM comparator — the real backend for the prm-verifier
    arm: Skywork-o1-Open-PRM-Qwen-2.5-1.5B at the PINNED revision (ops
    amendment 3). The checkpoint's auto_map resolves AutoModel to its own
    Qwen2ForRewardModel (trust_remote_code custom classes, themselves pinned
    by the revision sha), whose forward returns the value-head reward logit
    pooled at the last non-pad token. Readout: sigmoid(last-token reward
    logit) over the chat-formatted (shared-affordance QA prompt, candidate
    answer) pair — the outcome-reward reading of the PRM; our candidates are
    single-step answers, so the last step IS the outcome step (Skywork
    step_token convention degenerates to this for one-step responses).

    Signature-compatible with StubPRM; `gold`, `seed` and `idx` are IGNORED
    on purpose — a real reward model never sees the gold answer."""

    def __init__(self, repo, revision, device, frames):
        import torch
        from transformers import AutoModel, AutoTokenizer
        if not repo or not revision:
            raise SystemExit("ERR_UNPINNED_MODEL: prm has no pinned repo/"
                             "revision (ops amendment required)")
        self.tok = AutoTokenizer.from_pretrained(
            repo, revision=revision, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(
            repo, revision=revision, trust_remote_code=True,
            torch_dtype=torch.bfloat16)
        self.model.to(device)
        self.model.eval()
        for p in self.model.parameters():
            p.requires_grad_(False)
        self.device = device
        self.torch = torch
        self.frames = frames
        self.n_active = sum(p.numel() for p in self.model.parameters())
        self.weight_bytes = int(self.n_active * 2)  # bf16
        self.name = "%s@%s" % (repo, revision[:8])

    def score(self, item, answer, gold, seed, idx):  # noqa: ARG002 (contract)
        prompt = build_prompt(self.frames, item)
        msgs = [{"role": "user", "content": prompt},
                {"role": "assistant", "content": str(answer)}]
        ids = self.tok.apply_chat_template(msgs, tokenize=True,
                                           return_tensors="pt").to(self.device)
        with self.torch.no_grad():
            out = self.model(input_ids=ids)
        return float(self.torch.sigmoid(out.logits.float()).item())


class HFLM:
    """Real path: SmolLM2 at the PINNED revision, forced-choice logprob
    scoring (the IF-C constrained surface). Only importable with torch +
    transformers present (the Modal image); never touched by --mock."""

    def __init__(self, repo, revision, device, int4=False):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        if not revision:
            raise SystemExit("ERR_UNPINNED_MODEL: %s has no pinned revision "
                             "(ops amendment required before any real run)" % repo)
        self.tok = AutoTokenizer.from_pretrained(repo, revision=revision)
        kwargs = {"revision": revision, "torch_dtype": torch.float16}
        if int4:
            try:
                from transformers import BitsAndBytesConfig
                # fp16 compute dtype: the practitioner-realistic int4 config
                # (bnb's fp32 default would unfairly inflate this null arm's
                # measured latency)
                kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
                del kwargs["torch_dtype"]
            except Exception as e:  # noqa: BLE001
                raise SystemExit("ERR_INT4_DEP: bitsandbytes unavailable: %s" % e)
        from_pretrained = AutoModelForCausalLM.from_pretrained
        self.model = from_pretrained(repo, **kwargs)
        if not int4:
            self.model.to(device)
        self.model.eval()
        for p in self.model.parameters():
            p.requires_grad_(False)
        self.device = device
        self.torch = torch
        self.name = "%s@%s%s" % (repo, revision[:8], "-int4" if int4 else "")
        cfg = self.model.config
        self.n_active = sum(p.numel() for p in self.model.parameters())
        self.layers = cfg.num_hidden_layers
        self.d_attn = cfg.hidden_size
        bytes_per = 0.5 if int4 else 2
        self.weight_bytes = int(self.n_active * bytes_per)
        self.int4 = int4

    def count_tokens(self, text):
        return len(self.tok.encode(text, add_special_tokens=False))

    def _option_logprobs(self, prompt, options):
        torch = self.torch
        pre = self.tok.encode(prompt, add_special_tokens=False)
        outs = []
        with torch.no_grad():
            for opt in options:
                oids = self.tok.encode(opt, add_special_tokens=False)
                ids = torch.tensor([pre + oids], device=self.device)
                logits = self.model(ids).logits[0]
                lp = torch.log_softmax(logits[:-1].float(), dim=-1)
                tgt = ids[0, 1:]
                start = len(pre) - 1
                outs.append(float(lp[start:, :].gather(
                    1, tgt[start:, None]).sum()))
        return outs

    def choose(self, item, keys, gold, seed, attempt, has_context=False,
               prompt=""):
        lps = self._option_logprobs(prompt, [" %s" % k for k in keys])
        if attempt == 0:
            i = max(range(len(keys)), key=lambda j: lps[j])
        else:
            torch = self.torch
            g = torch.Generator().manual_seed(
                SEED_BASE * 10000 + seed * 100 + attempt)
            probs = torch.softmax(torch.tensor(lps), dim=0)
            i = int(torch.multinomial(probs, 1, generator=g))
        srt = sorted(lps, reverse=True)
        conf = srt[0] - (srt[1] if len(srt) > 1 else srt[0])  # answer margin
        return keys[i], conf

    def self_check(self, item, answer, gold, seed, attempt, prompt=""):
        lps = self._option_logprobs(prompt, [" yes", " no"])
        return lps[0] > lps[1]


# ---------------------------------------------------------------------------
# F0 flop-meter: PROMOTED to poc/f0/flop_meter.py (imported above) — the
# shared accounting standard (design-efficiency-track.md section 3): formula
# FLOPs + measured wall-clock + memory ledger + $/query. RAW numbers only.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Prompt construction (shared affordance — identical frames for every arm)
# ---------------------------------------------------------------------------
def build_prompt(frames, item, context_docs=None):
    parts = [frames["qa_prefix"]]
    if context_docs:
        parts.append(frames["context_prefix"])
        for d in context_docs:
            parts.append("- %s: %s\n" % (d["term"], d["text"]))
        parts.append(frames["context_suffix"])
    parts.append(item["question"])
    if item.get("options"):
        parts.append("\n")
        for o in item["options"]:
            parts.append(frames["option_line"].format(key=o["key"], text=o["text"]) + "\n")
    parts.append(frames["answer_cue"])
    return "".join(parts)


def item_keys_gold(item):
    if item.get("options"):
        return [o["key"] for o in item["options"]], item["answer"]
    return ["yes", "no"], item["answer"]


# ---------------------------------------------------------------------------
# Arm implementations. Each returns (per-item 0/1 list, meter) for one cell.
# ---------------------------------------------------------------------------
def answer_once(lm, frames, item, seed, attempt, context_docs=None):
    keys, gold = item_keys_gold(item)
    prompt = build_prompt(frames, item, context_docs)
    t0 = time.perf_counter()
    if isinstance(lm, StubLM):
        ans, conf = lm.choose(item, keys, gold, seed, attempt,
                              has_context=bool(context_docs))
    else:
        ans, conf = lm.choose(item, keys, gold, seed, attempt,
                              has_context=bool(context_docs), prompt=prompt)
    lat = time.perf_counter() - t0
    t_prompt = lm.count_tokens(prompt)
    t_opts = sum(lm.count_tokens(" %s" % k) for k in keys)
    return ans, conf, lat, t_prompt * len(keys) + t_opts


def run_alone(lm, frames, items, seed, meter, context_fn=None):
    correct = []
    for it in items:
        docs = context_fn(it) if context_fn else None
        ans, _conf, lat, toks = answer_once(lm, frames, it, seed, 0, docs)
        meter.seq(lm, toks)
        meter.query_done(lat)
        correct.append(1 if ans == it["answer"] else 0)
    return correct


def verify_answer(verifier, item, ans):
    """IF-C extract + kernel check. Returns (extract_ok, decidable, consistent, cpu_s)."""
    rec = extract_record(item, ans)
    if rec is None:
        return False, False, False, 0.0
    if rec["kind"] == "term-for-definition":
        if not item.get("kernel_checkable"):
            # control item: no canonical record exists (record_path null) —
            # the verifier abstains off-coverage (d-qa README contract);
            # extraction itself succeeded
            return True, False, False, 0.0
        entry = verifier._load(item)  # canonical definition shown in the question
        rec["definition"] = entry["text"]
    decidable, consistent = verifier.check(rec, item)
    return True, decidable, consistent, getattr(verifier, "last_cpu_s", 0.0)


def run_verify_retry(lm, frames, items, verifier, k, seed, meter,
                     in_decode=False):
    """Arm 4/5 of the frozen design: verify -> reject -> resample, max k.
    Final answer = last attempt (pre-declared in the RunSpec). `in_decode`
    switches to the EF5 placement (verification inline before final emission
    — same accept set at k=1, different latency profile, measured)."""
    correct = []
    extraction_failures = 0
    for it in items:
        ans = None
        t_item0 = time.perf_counter()
        for attempt in range(k + 1):
            ans, _conf, lat, toks = answer_once(lm, frames, it, seed, attempt)
            meter.seq(lm, toks)
            if not in_decode:
                meter.query_done(lat)
            ok_ext, decidable, consistent, cpu_s = verify_answer(verifier, it, ans)
            meter.verifier(cpu_s)
            if not ok_ext:
                extraction_failures += 1
                break  # instrument event: no free wins/losses (P10 section 4)
            if not decidable or consistent:
                break  # accepted (or verifier abstains off-coverage)
        if in_decode:
            meter.query_done(time.perf_counter() - t_item0)
        correct.append(1 if ans == it["answer"] else 0)
    return correct, extraction_failures


def run_self_verify_retry(lm, frames, items, gloss_by_urn, k, seed, meter):
    """Arm 10 (P7 RT-2): the model checks its own answer against the pinned
    gloss TEXT and retries — identical retry topology to the kernel arm; the
    instrument is the model + text instead of the deterministic verifier."""
    correct = []
    for it in items:
        ans = None
        for attempt in range(k + 1):
            ans, _conf, lat, toks = answer_once(lm, frames, it, seed, attempt)
            meter.seq(lm, toks)
            meter.query_done(lat)
            gloss = gloss_by_urn.get(it["urn"])
            if gloss is None:
                break  # no pinned gloss -> no check possible (control items)
            frame = frames["self_verify_frame"].format(
                term=it["label"], gloss=gloss["text"],
                question=it["question"], answer=ans)
            t0 = time.perf_counter()
            if isinstance(lm, StubLM):
                ok = lm.self_check(it, ans, it["answer"], seed, attempt)
            else:
                ok = lm.self_check(it, ans, it["answer"], seed, attempt,
                                   prompt=frame)
            meter.seq(lm, lm.count_tokens(frame) * 2)  # yes/no scoring passes
            meter.query_done(time.perf_counter() - t0)
            if ok:
                break
        correct.append(1 if ans == it["answer"] else 0)
    return correct


def run_self_consistency(lm, frames, items, n_votes, seed, meter):
    correct = []
    for it in items:
        votes = {}
        t0 = time.perf_counter()
        for v in range(n_votes):
            ans, _c, _lat, toks = answer_once(lm, frames, it, seed, v + 1)
            meter.seq(lm, toks)
            votes[ans] = votes.get(ans, 0) + 1
        best = sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        meter.query_done(time.perf_counter() - t0)
        correct.append(1 if best == it["answer"] else 0)
    return correct


def run_prm(lm, prm, frames, items, n_cand, seed, meter):
    correct = []
    for it in items:
        cands = []
        t0 = time.perf_counter()
        for v in range(n_cand):
            ans, _c, _lat, toks = answer_once(lm, frames, it, seed, v)
            meter.seq(lm, toks)
            cands.append(ans)
        scored = [(prm.score(it, a, it["answer"], seed, i), -i, a)
                  for i, a in enumerate(cands)]
        # PRM forward cost on the ledger (F0: nothing waived)
        prompt_toks = lm.count_tokens(build_prompt(frames, it)) * n_cand
        meter.model_flops += 2.0 * prm.n_active * prompt_toks
        best = sorted(scored, reverse=True)[0][2]
        meter.query_done(time.perf_counter() - t0)
        correct.append(1 if best == it["answer"] else 0)
    return correct


def run_cascade(small, large, frames, items, gate, budget, verifier,
                gloss_by_urn, seed, meter):
    """Small answers everything; gate flags candidates; escalate the
    lowest-confidence flagged items up to ceil(budget*n) (RunSpec rule);
    measured p_escalate lands on the ledger."""
    n = len(items)
    cap = int(math.ceil(budget * n))
    stage = []
    for it in items:
        t0 = time.perf_counter()
        ans, conf, _lat, toks = answer_once(small, frames, it, seed, 0)
        meter.seq(small, toks)
        flagged = False
        if gate == "verifier":
            ok_ext, decidable, consistent, cpu_s = verify_answer(verifier, it, ans)
            meter.verifier(cpu_s)
            flagged = ok_ext and decidable and not consistent
        elif gate == "logprob":
            flagged = True  # ranked by confidence below; cap picks lowest-b
        elif gate == "text-self-check":
            gloss = gloss_by_urn.get(it["urn"])
            if gloss is not None:
                frame = frames["self_verify_frame"].format(
                    term=it["label"], gloss=gloss["text"],
                    question=it["question"], answer=ans)
                if isinstance(small, StubLM):
                    ok = small.self_check(it, ans, it["answer"], seed, 0)
                else:
                    ok = small.self_check(it, ans, it["answer"], seed, 0,
                                          prompt=frame)
                meter.seq(small, small.count_tokens(frame) * 2)
                flagged = not ok
        elif gate == "in-decode":
            ok_ext, decidable, consistent, cpu_s = verify_answer(verifier, it, ans)
            meter.verifier(cpu_s)
            flagged = ok_ext and decidable and not consistent
        stage.append({"item": it, "ans": ans, "conf": conf, "flag": flagged,
                      "t0": t0})
    flagged_idx = sorted((i for i, s in enumerate(stage) if s["flag"]),
                         key=lambda i: (stage[i]["conf"], i))[:cap]
    for i in flagged_idx:
        it = stage[i]["item"]
        ans, _c, _lat, toks = answer_once(large, frames, it, seed, 0)
        meter.seq(large, toks)
        stage[i]["ans"] = ans
    for s in stage:
        meter.query_done(time.perf_counter() - s["t0"])
    correct = [1 if s["ans"] == s["item"]["answer"] else 0 for s in stage]
    return correct, len(flagged_idx) / float(n)


def run_extraction_instrument_dxif(dxif_dir, rung, covered, control, verifier):
    """P10 gate measurement, REAL path: re-verifies the pinned d-xif labelled
    set (>=300 real model outputs per rung, built pre-final-phase by
    xif_runner.py) through the extraction machinery — the stored flags are
    NOT trusted; every failure/error is recomputed here from the stored
    constrained answers against the pinned records (fail closed on pins)."""
    outputs = load_jsonl(os.path.join(dxif_dir, "outputs",
                                      "%s.jsonl" % rung.lower()))
    by_id = {it["id"]: it for it in covered + control}
    n = fails = errs = 0
    for o in outputs:
        if o["slice"] != "covered":
            continue
        it = by_id.get(o["id"])
        if it is None:
            raise SystemExit("ERR_DXIF_ITEM: %s not in the pinned d-qa items"
                             % o["id"])
        ans = o["ifc_answer"]
        ok_ext, decidable, _cons, _cpu = verify_answer(verifier, it, ans)
        n += 1
        if not (ok_ext and decidable):
            fails += 1
            continue
        rec = extract_record(it, ans)
        if rec["kind"] in ("definition", "term-for-definition"):
            opt = {x["key"]: x["text"] for x in it["options"]}
            good = (rec.get("text") or rec.get("term")) == opt.get(ans)
        else:
            good = rec["claim"] == it["claim"] and rec["verdict"] == ans
        if not good:
            errs += 1  # well-formed but wrong record vs the asserted content
    return {"n_labelled": n, "n_extraction_failures": fails,
            "n_extraction_errors": errs}


def run_extraction_instrument(lm, frames, items, verifier, n_labelled, seed):
    """P10 gate measurement, MOCK path: cycles the d-qa items through the
    REAL extraction machinery with the stub LM as a clearly-labelled
    stand-in (real runs use run_extraction_instrument_dxif over the pinned
    d-xif labelled set instead)."""
    n_fail = 0
    n_err = 0
    for i in range(n_labelled):
        it = items[i % len(items)]
        ans, _c, _lat, _toks = answer_once(lm, frames, it, seed, i)
        if isinstance(lm, StubLM):
            # stub emits a malformed output at the configured synthetic rate
            if det_u("xfail", lm.name, it["id"], seed, i) < lm.mock_xfail:
                ans = "MALFORMED"
        rec = extract_record(it, ans)
        if rec is None:
            n_fail += 1
            continue
        ok_ext, decidable, consistent, _cpu = verify_answer(verifier, it, ans)
        if ok_ext and decidable and not consistent and ans == it["answer"]:
            n_err += 1  # well-formed but wrong record vs gold
    return {"n_labelled": n_labelled, "n_extraction_failures": n_fail,
            "n_extraction_errors": n_err}


# ---------------------------------------------------------------------------
# Emitter — kot-log/1 record BODIES (config + RAW metrics). log-append.py
# stamps seq/chain/ts/runner; analysis/f2.py consumes these lines directly.
# ---------------------------------------------------------------------------
class Emitter:
    def __init__(self, out_dir, mock):
        self.records = []
        self.path = os.path.join(out_dir,
                                 "run-records-f2%s.jsonl" % ("-mock" if mock else ""))
        self.phase = "mock" if mock else "final"

    def emit(self, arm, rung, retry_budget, escalation_budget, seed, metrics):
        body = {
            "event": "run",
            "phase": self.phase,
            "config": {"arm": arm, "rung": rung, "retry_budget": retry_budget,
                       "escalation_budget": escalation_budget, "seed": seed},
            "metrics": metrics,
            "exit": "ok",
        }
        self.records.append(body)
        return body

    def write(self):
        with open(self.path, "w") as f:
            for r in self.records:
                f.write(json.dumps(r, sort_keys=True) + "\n")
        return self.path


def cell_metrics(correct, meter, lms, store_bytes, external=None, control=None):
    m = {"item_correct": correct,
         "metric_vector": meter.ledger(lms, store_bytes)}
    if external is not None:
        m["item_correct_external"] = external
    if control is not None:
        m["item_correct_control"] = control
    return m


# ---------------------------------------------------------------------------
# Input loading + fail-closed pins
# ---------------------------------------------------------------------------
def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_inputs(inputs_dir, dqa_dir):
    with open(os.path.join(inputs_dir, "f2-manifest.json"), encoding="utf-8") as f:
        man = json.load(f)
    pins = man["pins"]
    checks = {
        "dqaCoveredItemsSha256": os.path.join(dqa_dir, "items", "covered.jsonl"),
        "dqaControlItemsSha256": os.path.join(dqa_dir, "items", "control.jsonl"),
        "dqaGlossCorpusSha256": os.path.join(dqa_dir, "gloss-corpus.jsonl"),
        "dqaRagIndexSha256": os.path.join(dqa_dir, "rag-index.json"),
        "dqaManifestSha256": os.path.join(dqa_dir, "manifest.json"),
    }
    for key, path in checks.items():
        if sha256_file(path) != pins[key]:
            raise SystemExit("ERR_PIN: %s: %s sha != f2-manifest pin" % (key, path))
    covered = load_jsonl(checks["dqaCoveredItemsSha256"])
    control = load_jsonl(checks["dqaControlItemsSha256"])
    gloss_docs = load_jsonl(checks["dqaGlossCorpusSha256"])
    with open(checks["dqaRagIndexSha256"], encoding="utf-8") as f:
        rag_index = json.load(f)
    covered.sort(key=lambda x: x["rank"])
    control.sort(key=lambda x: x["rank"])
    return man, covered, control, gloss_docs, rag_index


# ---------------------------------------------------------------------------
# --dry-plan: the real-run cost plan vs the Tier-1 cap. Stdlib only; prints
# ESTIMATES clearly labelled as such; runs nothing, spends nothing.
# ---------------------------------------------------------------------------
def dry_plan(man, covered, control, gpu):
    plan = man["planning"]
    dc = man["design_constants_from_frozen_record"]
    frames = man["prompt_frames"]
    cpt = plan["chars_per_token_estimate"]
    tput = plan["throughput_tok_per_s"][gpu]
    usd = man["flop_accounting"]["usd_per_hour"][gpu]
    seeds, ks, budgets = dc["seeds"], dc["retry_sweep"], dc["escalation_budgets"]
    items = covered + control
    n_ext = dc["per_arm_items"]  # d-ext planning placeholder (not built)

    def est_tokens(item, context=False):
        keys, _ = item_keys_gold(item)
        prompt = build_prompt(frames, item)
        t = len(prompt) / cpt
        if context:
            t += 200  # ~3 gloss docs
        return t * len(keys)

    tok_covered = sum(est_tokens(i) for i in items)
    tok_ctx = sum(est_tokens(i, True) for i in items)
    tok_ext = n_ext * 250 * 2  # planning placeholder: yes/no + short prompts

    # cell inventory (mirrors run_cells; retry worst case = k+1 attempts)
    cells = []  # (rung, tokens)
    for s in seeds:  # noqa: B007
        cells.append(("R1", tok_covered + tok_ext))            # alone R1
        cells.append(("R2", tok_covered + tok_ext))            # alone R2
        cells.append(("R3", tok_covered + tok_ext))            # alone R3 (extension-conditional)
        for k in ks:
            cells.append(("R1", (tok_covered + tok_ext) * (k + 1)))   # verify R1
            cells.append(("R2", (tok_covered + tok_ext) * (k + 1)))   # verify R2
            cells.append(("R1", (tok_covered + tok_ext) * (k + 1) * 2))  # self-verify (+check pass)
        cells.append(("R1", tok_covered * man["arm_plan"]["self_consistency_n"]))  # SC
        cells.append(("R1", tok_covered * man["arm_plan"]["prm_best_of_n"] * 1.5))  # PRM (+forwards)
    cells.append(("R1", tok_ctx))   # kernel-as-text (greedy, 1 cell)
    cells.append(("R1", tok_ctx))   # rag-over-text
    cells.append(("R2", tok_covered))  # int4 360M
    for _b in budgets:
        for _arm in CASCADE_ARMS:
            cells.append(("R1", tok_covered))
            cells.append(("R3", tok_covered * 0.5))  # worst-case escalation b=0.5
    cells.append(("R1", 300 * 300 / cpt * 4))  # iface labelled sets (300/rung)
    cells.append(("R2", 300 * 300 / cpt * 4))

    hours = {"R1": 0.0, "R2": 0.0, "R3": 0.0}
    for rung, toks in cells:
        hours[rung] += toks / tput[rung] / 3600.0
    est_h = sum(hours.values())
    worst_h = est_h * plan["overhead_factor"]
    cap = dc["budget"]
    lines = [
        "F2 --dry-plan (ESTIMATES ONLY — planning constants from f2-manifest.json;",
        "no GPU, no network, $0 spent by this command)",
        "",
        "eval set: %d covered + %d control d-qa items; external slice planned at %d"
        % (len(covered), len(control), n_ext) + " (d-ext NOT BUILT — see blockers)",
        "cells inventoried: %d  (arms x rungs x k x budgets x %d seeds)"
        % (len(cells), len(seeds)),
        "",
        "GPU-hours estimate on %s (tok/s planning table %s):" % (gpu, tput),
        "  R1 %.2f h   R2 %.2f h   R3 %.2f h   total %.2f h"
        % (hours["R1"], hours["R2"], hours["R3"], est_h),
        "  with %.1fx overhead factor (model loads, retries, batching slack): %.2f h"
        % (plan["overhead_factor"], worst_h),
        "",
        "cost at Modal list $%.2f/h (%s):" % (usd, gpu),
        "  point estimate  $%.2f" % (est_h * usd),
        "  worst case      $%.2f  (overhead-inflated)" % (worst_h * usd),
        "  hard ceiling    $%.2f  (registry gpu_hours_cap %d h x $%.2f/h)"
        % (cap["gpu_hours_cap"] * usd, cap["gpu_hours_cap"], usd),
        "  [F0 section 3.5 AWS cross-reference: T4 $0.53/h, A10G $1.01/h]",
        "",
        "caps (registry/experiments/f2.json, frozen): usd_cap $%d, gpu_hours_cap %d h,"
        % (cap["usd_cap"], cap["gpu_hours_cap"]),
        "  wall_clock_cap %d h; Tier-1 cap $%d (P1 section 5)"
        % (cap["wall_clock_cap_hours"], cap["tier_cap_usd"]),
        "",
    ]
    verdicts = [
        ("worst case vs usd_cap ($%d)" % cap["usd_cap"], worst_h * usd <= cap["usd_cap"]),
        ("hard ceiling vs Tier-1 cap ($%d)" % cap["tier_cap_usd"],
         cap["gpu_hours_cap"] * usd <= cap["tier_cap_usd"]),
        ("estimate vs gpu_hours_cap (%d h)" % cap["gpu_hours_cap"],
         worst_h <= cap["gpu_hours_cap"]),
    ]
    for name, ok in verdicts:
        lines.append("  %-42s %s" % (name, "OK" if ok else "OVER — DO NOT LAUNCH"))
    lines.append("")
    lines.append("launch gates: see f2-manifest inputs_status + README (d-xif/d-ext pins")
    lines.append("verified fail-closed at real-run start); maintainer Tier-1 go required.")
    lines.append("model revisions: ALL PINNED (amendments 2-3: R1/R2/R3 + PRM).")
    print("\n".join(lines))
    return all(ok for _n, ok in verdicts)


# ---------------------------------------------------------------------------
# Cell driver
# ---------------------------------------------------------------------------
def run_cells(args, man, covered, control, gloss_docs, rag_index, log):
    mock = args.mock
    dc = man["design_constants_from_frozen_record"]
    frames = man["prompt_frames"]
    plan = man["arm_plan"]
    seeds = man["mock"]["seeds"] if mock else dc["seeds"]
    ks = dc["retry_sweep"]
    budgets = dc["escalation_budgets"]

    if mock:
        mk = man["mock"]
        covered = covered[:mk["n_covered_items"]]
        control = control[:mk["n_control_items"]]
        # d-ext stand-in (SYNTHETIC, labelled as such): yes/no control items
        external = [dict(it, id="mock-ext:" + it["id"])
                    for it in control][:mk["n_external_items"]]
        iface_n = mk["iface_n_labelled"]
    else:
        # d-xif (P10 labelled extraction set) — fail closed on absence or pin
        if not os.path.isdir(args.dxif_dir or ""):
            raise SystemExit("ERR_MISSING_DXIF: d-xif labelled extraction set not "
                             "built; the P10 instrument gate cannot be measured "
                             "— refusing a final-phase run (P10 section 4)")
        for key, rel in (("dxifOutputsR1Sha256", os.path.join("outputs", "r1.jsonl")),
                         ("dxifOutputsR2Sha256", os.path.join("outputs", "r2.jsonl")),
                         ("dxifManifestSha256", "manifest.json")):
            pin = man["pins"].get(key)
            path = os.path.join(args.dxif_dir, rel)
            if not pin or sha256_file(path) != pin:
                raise SystemExit("ERR_PIN: %s: %s sha != f2-manifest pin" % (key, path))
        # d-ext (RT-7a external slice) — without it the frozen external-slice
        # secondary is unresolvable; fail closed
        if not os.path.isdir(args.dext_dir or ""):
            raise SystemExit("ERR_MISSING_DEXT: d-ext external eval slice not "
                             "built; the frozen external-slice secondary is "
                             "unresolvable — refusing a final-phase run")
        for key, rel in (("dextItemsSha256", os.path.join("items", "external.jsonl")),
                         ("dextManifestSha256", "manifest.json")):
            pin = man["pins"].get(key)
            path = os.path.join(args.dext_dir, rel)
            if not pin or sha256_file(path) != pin:
                raise SystemExit("ERR_PIN: %s: %s sha != f2-manifest pin" % (key, path))
        external = load_jsonl(os.path.join(args.dext_dir, "items", "external.jsonl"))
        external.sort(key=lambda x: x["rank"])
        iface_n = dc["iface_gate"]["n_min_per_rung"]

    verifier = KernelVerifier(args.records_root)
    verifier.index_labels(covered)
    gloss_by_urn = {d["urn"]: d for d in gloss_docs if "urn" in d}
    bm25 = BM25(rag_index, gloss_docs)
    store_bytes_gloss = os.path.getsize(os.path.join(args.dqa_dir, "gloss-corpus.jsonl"))
    store_bytes_rag = store_bytes_gloss + os.path.getsize(
        os.path.join(args.dqa_dir, "rag-index.json"))
    store_bytes_records = 0
    for it in covered:
        p = os.path.join(args.records_root, it["record_path"])
        store_bytes_records += os.path.getsize(p)

    def make_lm(rung, int4=False):
        if mock:
            lm = StubLM(rung, man["mock"], int4=int4)
            lm.mock_xfail = man["mock"]["stub_extraction_fail_rate"]
            return lm
        spec = man["models"][rung]
        return HFLM(spec["repo"], spec["revision"], args.device, int4=int4)

    emit = Emitter(args.out_dir, mock)
    fc = man["flop_accounting"]
    gpu = args.gpu_class
    lms = {}

    def lm_for(rung, int4=False):
        key = (rung, int4)
        if key not in lms:
            lms[key] = make_lm(rung, int4)
        return lms[key]

    def new_meter():
        return FlopMeter(fc, gpu)

    all_items = covered + control

    def ext_vector(lm, seed):
        if external is None:
            return None
        meter_ext = new_meter()
        return run_alone(lm, frames, external, seed, meter_ext)

    # ---- model-alone at each rung (per seed for C-4 pairing) ---------------
    rungs_alone = ["R1", "R2", "R3"]
    for rung in rungs_alone:
        lm = lm_for(rung)
        for seed in seeds:
            meter = new_meter()
            cov = run_alone(lm, frames, covered, seed, meter)
            ctl = run_alone(lm, frames, control, seed, meter)
            emit.emit(ARM_ALONE, rung, 0, 0, seed,
                      cell_metrics(cov, meter, [lm], 0,
                                   external=ext_vector(lm, seed), control=ctl))
            log("cell %s %s seed=%d done" % (ARM_ALONE, rung, seed))

    # ---- kernel-verify-retry at R1 and R2 (frozen rung-pair set) ------------
    for rung in ("R1", "R2"):
        lm = lm_for(rung)
        for k in ks:
            for seed in seeds:
                meter = new_meter()
                cov, _xf = run_verify_retry(lm, frames, covered, verifier, k,
                                            seed, meter)
                ctl, _xf2 = run_verify_retry(lm, frames, control, verifier, k,
                                             seed, meter)
                emit.emit(ARM_VERIFY, rung, k, 0, seed,
                          cell_metrics(cov, meter, [lm], store_bytes_records,
                                       external=ext_vector(lm, seed), control=ctl))
            log("cells %s %s k=%d done" % (ARM_VERIFY, rung, k))

    # ---- text arms at R1 (greedy, deterministic -> one cell each) ----------
    lm1 = lm_for("R1")
    meter = new_meter()
    cov = run_alone(lm1, frames, covered, seeds[0], meter,
                    context_fn=lambda it: [gloss_by_urn[it["urn"]]]
                    if it["urn"] in gloss_by_urn else None)
    emit.emit(ARM_TEXT, "R1", 0, 0, seeds[0],
              cell_metrics(cov, meter, [lm1], store_bytes_gloss,
                           external=ext_vector(lm1, seeds[0])))
    log("cell %s done" % ARM_TEXT)

    meter = new_meter()
    cov = run_alone(lm1, frames, covered, seeds[0], meter,
                    context_fn=lambda it: bm25.top(it["question"], plan["rag_top_k"]))
    emit.emit(ARM_RAG, "R1", 0, 0, seeds[0],
              cell_metrics(cov, meter, [lm1], store_bytes_rag))
    log("cell %s done" % ARM_RAG)

    # ---- matched-compute sampling + PRM + self-verify ----------------------
    for seed in seeds:
        meter = new_meter()
        cov = run_self_consistency(lm1, frames, covered,
                                   plan["self_consistency_n"], seed, meter)
        emit.emit(ARM_SC, "R1", 0, 0, seed,
                  cell_metrics(cov, meter, [lm1], 0))
    log("cells %s done" % ARM_SC)

    if mock:
        prm = StubPRM(man["mock"])
    else:
        spec = man["models"]["prm"]
        if not spec.get("repo") or not spec.get("revision"):
            raise SystemExit("ERR_UNPINNED_MODEL: prm arm requested but the PRM "
                             "is PINNED-AT-INPUTS (ops amendment required)")
        prm = HFPRM(spec["repo"], spec["revision"], args.device, frames)
    for seed in seeds:
        meter = new_meter()
        cov = run_prm(lm1, prm, frames, covered, plan["prm_best_of_n"], seed, meter)
        emit.emit(ARM_PRM, "R1", 0, 0, seed,
                  cell_metrics(cov, meter, [lm1, prm], 0))
    log("cells %s done" % ARM_PRM)

    for k in ks:
        for seed in seeds:
            meter = new_meter()
            cov = run_self_verify_retry(lm1, frames, covered, gloss_by_urn, k,
                                        seed, meter)
            emit.emit(ARM_SELFV, "R1", k, 0, seed,
                      cell_metrics(cov, meter, [lm1], store_bytes_gloss))
        log("cells %s k=%d done" % (ARM_SELFV, k))

    # ---- int4-quantized 360M (practitioner null) ---------------------------
    lm_int4 = lm_for("R2", int4=True)
    meter = new_meter()
    cov = run_alone(lm_int4, frames, covered, seeds[0], meter)
    emit.emit(ARM_INT4, "R2", 0, 0, seeds[0],
              cell_metrics(cov, meter, [lm_int4], 0))
    log("cell %s done" % ARM_INT4)

    # ---- cascades (R1 small -> R3 large), all gates, all budgets ------------
    lm_large = lm_for("R3")
    gate_of = {ARM_CV: "verifier", ARM_CL: "logprob",
               ARM_CT: "text-self-check", ARM_CD: "in-decode"}
    for arm in CASCADE_ARMS:
        for b in budgets:
            meter = new_meter()
            cov, p_esc = run_cascade(lm1, lm_large, frames, covered,
                                     gate_of[arm], b, verifier, gloss_by_urn,
                                     seeds[0], meter)
            m = cell_metrics(cov, meter, [lm1, lm_large], store_bytes_records
                             if arm in (ARM_CV, ARM_CD) else store_bytes_gloss)
            m["p_escalate_measured"] = p_esc
            emit.emit(arm, "R1", 0, b, seeds[0], m)
        log("cells %s done" % arm)

    # ---- P10 extraction-instrument gate measurement -------------------------
    for rung in ("R1", "R2"):
        if mock:
            stats = run_extraction_instrument(lm_for(rung), frames, all_items,
                                              verifier, iface_n, seeds[0])
        else:
            stats = run_extraction_instrument_dxif(args.dxif_dir, rung,
                                                   covered, control, verifier)
            if stats["n_labelled"] < iface_n:
                raise SystemExit("ERR_DXIF_N: %s has %d labelled outputs < "
                                 "the frozen n_min_per_rung %d"
                                 % (rung, stats["n_labelled"], iface_n))
        emit.emit(ARM_IFACE, rung, 0, 0, seeds[0], stats)
        log("cell %s %s done (%d labelled, %d failures)"
            % (ARM_IFACE, rung, stats["n_labelled"], stats["n_extraction_failures"]))

    return emit


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--inputs-dir", default=os.path.join(here, "..", "inputs"))
    ap.add_argument("--dqa-dir", default=os.path.join(here, "..", "..", "..",
                                                      "data", "d-qa"))
    ap.add_argument("--records-root", default=os.path.join(here, "..", "..", ".."),
                    help="root that item record_path fields resolve against")
    ap.add_argument("--dxif-dir", default=None,
                    help="d-xif labelled extraction set (REQUIRED for real runs)")
    ap.add_argument("--dext-dir", default=None,
                    help="d-ext external eval slice (REQUIRED for real runs)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--gpu-class", default="A10G", choices=["T4", "A10G"])
    ap.add_argument("--mock", action="store_true",
                    help="stub-LM mechanics check on CPU; $0; labelled MOCK")
    ap.add_argument("--dry-plan", action="store_true",
                    help="print the real-run cost plan vs caps; runs nothing")
    ap.add_argument("--max-hours", type=float, default=60.0)
    args = ap.parse_args()
    t0 = time.time()

    man, covered, control, gloss_docs, rag_index = load_inputs(
        args.inputs_dir, args.dqa_dir)

    if args.dry_plan:
        ok = dry_plan(man, covered, control, args.gpu_class)
        sys.exit(0 if ok else 2)

    os.makedirs(args.out_dir, exist_ok=True)

    def log(msg):
        print("[f2 %7.1fs] %s" % (time.time() - t0, msg), flush=True)

    label = "MOCK" if args.mock else "FULL"
    log("mode=%s device=%s items=%d covered / %d control"
        % (label, args.device, len(covered), len(control)))
    if not args.mock and args.device != "cuda":
        log("WARNING: real run requested on CPU — allowed but slow")

    emit = run_cells(args, man, covered, control, gloss_docs, rag_index, log)
    records_path = emit.write()

    hours = (time.time() - t0) / 3600.0
    if hours > args.max_hours:
        raise SystemExit("ERR_TIME_BUDGET: exceeded %.1fh" % args.max_hours)

    suffix = "-mock" if args.mock else ""
    results = {
        "experiment": "f2",
        "outcome": ("MOCK-HARNESS-COMPLETE" if args.mock else "HARNESS-COMPLETE"),
        "outcome_note": "NOT a hypothesis verdict — raw run-records only; the "
                        "verdict is computed by analysis/f2.py (pinned sha "
                        "068f68b8...) + tools/registry/verdict-gen.py under "
                        "run-vs-audit separation",
        "mode": label,
        "date": utcnow(),
        "device": args.device,
        "gpu_class_assumed_for_usd": args.gpu_class,
        "pins": man["pins"],
        "models": man["models"] if not args.mock else
                  {"note": "MOCK — synthetic stub LM, no models loaded"},
        "n_records": len(emit.records),
        "records_file": os.path.basename(records_path),
        "seeds": man["mock"]["seeds"] if args.mock else
                 man["design_constants_from_frozen_record"]["seeds"],
        "wallClockHours": hours,
    }
    with open(os.path.join(args.out_dir, "results-f2%s.json" % suffix), "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    log("OUTCOME: %s (%d run-record bodies in %s)"
        % (results["outcome"], len(emit.records), records_path))


if __name__ == "__main__":
    main()
