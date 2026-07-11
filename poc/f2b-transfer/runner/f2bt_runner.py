#!/usr/bin/env python3
"""f2b-transfer STAGE-2 runner — ground-truth-independence test of the
verifier-offload lift (frozen design registry/experiments/f2b-transfer.json,
frozen_sha256 b341a0901e12023d3c56bdc196be0b9c492c7d348f988416d7e9c43aade20879;
prereg doc poc/f2b-transfer/design.md).

ADAPTED FROM poc/f2b/runner/f2b_runner.py per the frozen record's
runner_constraints.harness: "stage-2 GPU runner adapted from poc/f2b: drop
PRM/text/d-ext, add dual scoring + verifier_engagement block +
adjudication-instrument record; poc/f2b is left byte-identical to its
f2b-replicate pin". The verifier, extraction, prompt frames, IF-C constrained
answer surface, HF backends, CellGuard safety instrument and Emitter are
carried over with byte-identical semantics; nothing scientific is new except
what the frozen design mandates.

WHY THIS EXPERIMENT EXISTS: f2b-replicate PASSED but its gold labels were
DEFINED by the same string-equality the verifier checks (definitional
circularity — content-specificity != ground-truth independence). Stage 1
replaced the gold-definition step with blind external adjudication
(data/d-adj-t; endorsement A = 0.9610, Wilson LB 0.9395 > 0.70 — kill (d) did
not fire; the stage-1 record is ALREADY in results-log/f2b-transfer.jsonl).
This stage-2 runner re-runs the surviving arms FRESH on the externally-
labelled items and DUAL-SCORES every cell:

  item_correct_ext  — against gold_ext (data/d-adj-t/labels.jsonl): the
                      scoring rule for EVERY endpoint (the primary is
                      acc_ext(verify,k=4) - acc_ext(R1-alone))
  item_correct_mem  — against membership gold (the item's own answer field):
                      DESCRIPTIVE ONLY (dual-scoring contrast lift_mem -
                      lift_ext, the circularity-signature diagnostic)

ARMS (design.arms_mandatory_baselines; ALL fresh final-phase runs):
  model-alone                     R1 (SmolLM2-135M) and R3 (SmolLM2-1.7B),
                                  single pass, seeds 0/1/2
  kernel-verify-retry             R1, fixed k=4 — THE arm (true records);
                                  every cell emits the RT-7a
                                  verifier_engagement block
  shuffled-kernel-verify-retry    R1, k=4 — LOAD-BEARING oracle-CONTENT null:
                                  identical retry topology and cost, record
                                  content decoupled by a seed-pinned Sattolo
                                  derangement (map recorded); the one control
                                  NOT to cut
  gloss-self-verify-retry         R1, k=4 (P7 RT-2 commodity-verification
                                  control at matched budget)
  extraction-instrument           P10 gate re-verification over the pinned
                                  d-xif labelled set (R1; CPU-only)

DROPPED vs poc/f2b (frozen record dropped_arms): trained-PRM, kernel-as-text,
the d-ext external slice (measured degenerate — replaced by this experiment's
entire externally-adjudicated eval set), gold-oracle, R2, k-ladder, cascades,
int4, RAG, self-consistency.

EVAL SET (frozen verbatim): the first per_arm_items=250 EXTERNALLY-LABELLED
items of data/d-qa-t/items/covered.jsonl in pinned rank order — externally
labelled means labels.jsonl gold_ext != null (unresolved judge disagreements
and concordant-escape CONTENT-UNDECIDED items are EXCLUDED); deterministic
prefix; floor 200, below which this runner REFUSES (ERR_EVAL_FLOOR).

ADJUDICATION-INSTRUMENT RECORD: the REAL stage-1 record was appended to the
results log before any GPU spend (stage discipline) and is NEVER re-emitted
by a real run (the pinned analysis fails on a duplicate). The --mock path
emits a phase="mock" copy built verbatim from the pinned d-adj-t summary.json
integers so the full analysis pipeline validates end-to-end on the mock
records file alone; mock records are never log-appended.

Usage:
  python3 f2bt_runner.py --out-dir /tmp/f2bt --device cuda      # real (Modal)
  python3 f2bt_runner.py --out-dir /tmp/f2bt --mock             # stub LM, CPU, $0
  python3 f2bt_runner.py --out-dir /tmp/f2bt --dry-plan         # cost plan vs caps

HARD RULES honoured here: --mock and --dry-plan spend $0 and never touch a
GPU or the network; mock numbers are labelled MOCK end-to-end and are never
measurements; real runs fail closed on any missing/mismatched pin (ERR_*).
RAW metrics only — verdicts belong to the pinned analysis/f2b_transfer.py +
tools/registry/verdict-gen.py under run-vs-audit separation.

SAFETY (f2b-replicate correction 1, carried over): every cell runs under a
CellGuard (per-cell wall-clock timeout + max-generations-per-item cap) and
every completed cell's record is flushed to disk immediately, so a
pathological path self-terminates as a logged exit:"timeout" record
(ERR_CELL_TIMEOUT) with partials on disk instead of hanging a GPU container.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time

# F0 flop-meter — shared poc/f0/ package (the `f0-harness` depends_on gate).
_POC_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."))
if _POC_DIR not in sys.path:
    sys.path.insert(0, _POC_DIR)
from f0 import FlopMeter  # noqa: E402

# ---------------------------------------------------------------------------
# Constants — arm names MUST equal analysis/f2b_transfer.py + registry IV levels
# ---------------------------------------------------------------------------
ARM_ALONE = "model-alone"
ARM_VERIFY = "kernel-verify-retry"
ARM_SHUF = "shuffled-kernel-verify-retry"
ARM_SELFV = "gloss-self-verify-retry"
ARM_IFACE = "extraction-instrument"
ARM_ADJ = "adjudication-instrument"   # mock pipeline-validation copy ONLY

SEED_BASE = 20260710  # published fixed base seed (== the f2b-transfer SAP PRNG seed)

# SAFETY BOUNDS (f2b-replicate correction 1, carried over unchanged;
# implementation-only: no arm, endpoint, gate or kill is changed).
#   MAX_GEN_PER_ITEM_DEFAULT  largest structural count is gloss-self-verify at
#       k=4 (5 answers + 5 self-checks = 10), so 16 can only trip on a defect.
#   CELL_TIMEOUT_S_DEFAULT    per-cell wall-clock budget, ~4x the slowest
#       expected real cell (R3-alone) and far below the 12 h Modal timeout.
MAX_GEN_PER_ITEM_DEFAULT = 16
CELL_TIMEOUT_S_DEFAULT = {"A100": 3600.0, "A10G": 3600.0, "T4": 9000.0}


class CellBudgetExceeded(Exception):
    """A cell hit a safety bound. Carried data feeds the logged timeout
    record; never converted into item_correct values (nothing is fabricated)."""

    def __init__(self, kind, cell, item_id, elapsed_s, n_gen):
        super().__init__(
            "%s in cell %s at item %r after %.1fs (%d generations on that item)"
            % (kind, cell, item_id, elapsed_s, n_gen))
        self.kind = kind
        self.cell = cell
        self.item_id = item_id
        self.elapsed_s = elapsed_s
        self.n_gen = n_gen


class CellGuard:
    """Per-cell safety instrument: wall-clock timeout + max-generations-per-
    item cap (verbatim semantics from poc/f2b). A breach raises
    CellBudgetExceeded, which the cell driver turns into a flushed
    exit:"timeout" record (excluded from eligible run records by verdict-gen's
    exit=="ok" rule -> the run fails closed as INCOMPLETE-DATA, never as a
    hang, never as data)."""

    def __init__(self, cell, timeout_s, max_gen_per_item):
        self.cell = cell
        self.timeout_s = float(timeout_s)
        self.max_gen = int(max_gen_per_item)
        self.t0 = time.monotonic()
        self.item_id = None
        self.n_gen = 0

    def elapsed(self):
        return time.monotonic() - self.t0

    def _wall(self):
        el = self.elapsed()
        if el > self.timeout_s:
            raise CellBudgetExceeded(
                "wall-clock timeout (%.0fs)" % self.timeout_s,
                self.cell, self.item_id, el, self.n_gen)

    def start_item(self, item):
        self.item_id = item.get("id")
        self.n_gen = 0
        self._wall()

    def gen(self):
        self.n_gen += 1
        if self.n_gen > self.max_gen:
            raise CellBudgetExceeded(
                "max-generations-per-item cap (%d)" % self.max_gen,
                self.cell, self.item_id, self.elapsed(), self.n_gen)
        self._wall()


# d-qa item types the IF-C extraction + kernel verifier understand. Every
# d-qa-t eval item is one of these AND kernel_checkable=true by construction
# (design.md section 6) — the runner asserts this fail-closed at load
# (ERR_ITEM_CHECKABLE), so the verifier has NO abstention path on the eval set.
DQA_TYPES = frozenset({
    "def-match", "term-match", "claim-true", "claim-false",
    "control:def-match", "control:term-match", "control:claim-true",
    "control:claim-false",
})


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def corpus_kot_hash(base):
    """kot-corpus-hash/1 digest of a corpus DIRECTORY (recipe verbatim from
    tools/registry/kot_common.py CORPUS_RECIPE; reimplemented here because the
    staged container has no tools/ tree). Fails closed upstream on mismatch."""
    lines = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames.sort()
        for name in filenames:
            full = os.path.join(dirpath, name)
            if os.path.islink(full) or not os.path.isfile(full):
                continue
            rel = os.path.relpath(full, base).replace(os.sep, "/")
            lines.append((rel.encode("utf-8"), sha256_file(full)))
    if not lines:
        raise SystemExit("ERR_P2_CORPUS_PIN: %s contains no regular files" % base)
    lines.sort(key=lambda t: t[0])
    payload = b"".join(d.encode("ascii") + b"  " + r + b"\n" for r, d in lines)
    return hashlib.sha256(payload).hexdigest()


def utcnow():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def det_u(*keys):
    """Deterministic uniform in [0,1) from sha256 over the key tuple."""
    raw = "\x1f".join(str(k) for k in keys)
    h = hashlib.sha256(raw.encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") / 2.0 ** 64


# ---------------------------------------------------------------------------
# Canonical-record rendering — VERBATIM from data/d-qa/build-dqa.py (and
# data/d-qa-t/build-dqat.py, which copies it) so the verifier's canonical
# text is byte-identical to the item builders'.
# ---------------------------------------------------------------------------
URN_MARKUP_RE = re.compile(r"\{urn:[^|}]+\|([^}]*)\}")
MIN_SEGMENT_CHARS = 15


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
# Byte-identical semantics to poc/f2b/runner/f2b_runner.py::KernelVerifier.
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
        for it in items:
            if it.get("kernel_checkable"):
                self._load(it)

    def shown_definition(self, item):
        """The canonical definition text shown in a term-match question — an
        item-level fact (the question embeds the concept's own gloss)."""
        return self._load(item)["text"]

    def check(self, record, item):
        """record -> (decidable, consistent). Deterministic; CPU-only."""
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


class ShuffledKernelVerifier:
    """The oracle-STRUCTURE control (carried over from f2b-replicate,
    LOAD-BEARING here — kill (b) reads it on external gold).

    Identical machinery and retry topology to KernelVerifier, but every
    record lookup the verifier performs for its OWN belief goes through a
    seed-pinned DERANGEMENT of the covered-concept map (Sattolo cyclic
    permutation: provably no fixed points): item about concept u is checked
    against the canonical record of perm[u]; a chosen term's record is the
    record of perm[concept-of-term]. Item-level facts (the definition text
    shown inside a term-match question) are NOT permuted — they are part of
    the item, not of the verifier's belief."""

    def __init__(self, records_root, covered_items, perm_seed):
        import random
        self.base = KernelVerifier(records_root)
        self.meta = {}
        self.label_to_urn = {}
        for it in covered_items:
            if it.get("kernel_checkable") and it["urn"] not in self.meta:
                self.meta[it["urn"]] = {"urn": it["urn"], "id": it["id"],
                                        "record_path": it["record_path"],
                                        "record_sha256": it["record_sha256"],
                                        "kernel_checkable": True}
                self.label_to_urn[it["label"].lower()] = it["urn"]
        urns = sorted(self.meta)
        if len(urns) < 2:
            raise SystemExit("ERR_SHUFFLE: need >=2 covered concepts to derange")
        # Sattolo's algorithm: uniformly random CYCLIC permutation -> a
        # derangement by construction (no concept maps to its own record).
        shuffled = list(urns)
        rng = random.Random(perm_seed)
        for i in range(len(shuffled) - 1, 0, -1):
            j = rng.randrange(i)
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
        self.perm = dict(zip(urns, shuffled))
        if any(u == v for u, v in self.perm.items()):
            raise SystemExit("ERR_SHUFFLE: fixed point in permutation (bug)")
        self.perm_seed = perm_seed
        blob = json.dumps(self.perm, sort_keys=True,
                          separators=(",", ":")).encode("utf-8")
        self.perm_sha256 = hashlib.sha256(blob).hexdigest()

    def index_labels(self, items):
        self.base.index_labels(items)

    def _entry(self, urn):
        return self.base._load(self.meta[urn])

    def shown_definition(self, item):
        # item-level fact: the TRUE gloss embedded in the question text
        return self.base._load(item)["text"]

    def check(self, record, item):
        if not item.get("kernel_checkable"):
            return False, False
        t0 = time.perf_counter()
        entry = self._entry(self.perm[item["urn"]])
        kind = record.get("kind")
        if kind == "definition":
            ok = norm_text(record["text"]) == norm_text(entry["text"])
        elif kind == "term-for-definition":
            u = self.label_to_urn.get(record["term"].lower())
            chosen = self._entry(self.perm[u]) if u is not None else None
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
    VERBATIM semantics from poc/f2b/runner/f2b_runner.py (the measured
    instrument of the pinned d-xif gate)."""
    try:
        if item["type"] in ("def-match", "control:def-match"):
            opt = {o["key"]: o["text"] for o in item["options"]}[answer]
            return {"kind": "definition", "urn": item["urn"], "text": opt}
        if item["type"] in ("term-match", "control:term-match"):
            opt = {o["key"]: o["text"] for o in item["options"]}[answer]
            return {"kind": "term-for-definition", "urn": item["urn"],
                    "term": opt, "definition": None}  # definition filled by caller
        if answer not in ("yes", "no"):
            return None
        return {"kind": "claim", "urn": item["urn"], "claim": item["claim"],
                "verdict": answer}
    except (KeyError, TypeError):
        return None


# ---------------------------------------------------------------------------
# LM backends — one interface, two implementations (verbatim from poc/f2b;
# PRM backends dropped: no PRM arm in this design).
# ---------------------------------------------------------------------------
class StubLM:
    """SYNTHETIC mechanics-only stand-in (mock mode; no torch). Every output
    is a deterministic function of (rung, seed, item, attempt) via sha256.
    The planted per-rung skill gradient (toward MEMBERSHIP gold — the stub
    never sees gold_ext) exists ONLY so the analysis contract's gates and
    denominators resolve during mock validation. Never a measurement."""

    def __init__(self, rung, mock_spec):
        self.rung = rung
        self.skill = mock_spec["stub_skill"][rung]
        self.ctx_bonus = mock_spec["stub_context_bonus"]
        self.check_skill = mock_spec["stub_self_check_skill"]
        dims = mock_spec["stub_dims"][rung]
        self.n_active = dims["n_active"]
        self.layers = dims["layers"]
        self.d_attn = dims["d_attn"]
        self.name = "stub-%s" % rung
        self.weight_bytes = int(self.n_active * 2)

    def count_tokens(self, text):
        return max(1, len(text.split()))

    def choose(self, item, keys, gold, seed, attempt, has_context=False):
        p = min(0.98, self.skill + (self.ctx_bonus if has_context else 0.0))
        u = det_u("ans", self.name, item["id"], seed, attempt)
        if u < p:
            ans = gold
        else:
            wrong = [k for k in keys if k != gold]
            ans = wrong[int(det_u("wr", self.name, item["id"], seed, attempt)
                            * len(wrong))]
        c = det_u("conf", self.name, item["id"], seed, attempt)
        conf = 0.5 + 0.5 * c if ans == gold else 0.5 * c
        return ans, conf

    def self_check(self, item, answer, gold, seed, attempt):
        truth = answer == gold
        u = det_u("chk", self.name, item["id"], seed, attempt)
        return truth if u < self.check_skill else (not truth)


class HFLM:
    """Real path: SmolLM2 at the PINNED revision, forced-choice logprob
    scoring (the IF-C constrained surface). Never touched by --mock.
    Byte-identical to poc/f2b (SEED_BASE differs by design: this
    experiment's published seed)."""

    def __init__(self, repo, revision, device):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        if not revision:
            raise SystemExit("ERR_UNPINNED_MODEL: %s has no pinned revision" % repo)
        self.tok = AutoTokenizer.from_pretrained(repo, revision=revision)
        self.model = AutoModelForCausalLM.from_pretrained(
            repo, revision=revision, torch_dtype=torch.float16)
        self.model.to(device)
        self.model.eval()
        for p in self.model.parameters():
            p.requires_grad_(False)
        self.device = device
        self.torch = torch
        self.name = "%s@%s" % (repo, revision[:8])
        cfg = self.model.config
        self.n_active = sum(p.numel() for p in self.model.parameters())
        self.layers = cfg.num_hidden_layers
        self.d_attn = cfg.hidden_size
        self.weight_bytes = int(self.n_active * 2)

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
        conf = srt[0] - (srt[1] if len(srt) > 1 else srt[0])
        return keys[i], conf

    def self_check(self, item, answer, gold, seed, attempt, prompt=""):
        lps = self._option_logprobs(prompt, [" yes", " no"])
        return lps[0] > lps[1]


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
# Arm implementations. Each returns the per-item FINAL ANSWERS for one cell;
# dual scoring happens once, in score_dual(), for every arm identically.
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


def score_dual(items, finals, gold_ext_by_id):
    """DUAL SCORING (frozen design.dependent_vars): the SAME final answers
    scored against BOTH golds. item_correct_ext is the endpoint scoring rule;
    item_correct_mem is descriptive only. gold_ext is guaranteed non-null for
    every eval item by construction of the eval set."""
    ext = [1 if a == gold_ext_by_id[it["id"]] else 0
           for it, a in zip(items, finals)]
    mem = [1 if a == it["answer"] else 0 for it, a in zip(items, finals)]
    return ext, mem


def run_alone(lm, frames, items, seed, meter, guard):
    finals = []
    for it in items:
        guard.start_item(it)
        ans, _conf, lat, toks = answer_once(lm, frames, it, seed, 0)
        guard.gen()
        meter.seq(lm, toks)
        meter.query_done(lat)
        finals.append(ans)
    return finals


def verify_answer(verifier, item, ans):
    """IF-C extract + kernel check. Returns (extract_ok, decidable,
    consistent, cpu_s). Verbatim semantics from poc/f2b; on this eval set
    every item is a DQA type and kernel_checkable (asserted at load), so the
    off-coverage abstention path exists only defensively."""
    if item.get("type") not in DQA_TYPES:
        return True, False, False, 0.0
    rec = extract_record(item, ans)
    if rec is None:
        return False, False, False, 0.0
    if rec["kind"] == "term-for-definition":
        if not item.get("kernel_checkable"):
            return True, False, False, 0.0
        rec["definition"] = verifier.shown_definition(item)
    decidable, consistent = verifier.check(rec, item)
    return True, decidable, consistent, getattr(verifier, "last_cpu_s", 0.0)


def run_verify_retry(lm, frames, items, verifier, k, seed, meter, guard):
    """verify -> reject -> resample, max k; final answer = last attempt
    (pre-declared). Used by BOTH the true-record and the shuffled-record
    arms — the arms differ ONLY in the verifier object passed in.

    Returns (finals, engagement, extraction_failures). The engagement block
    is the RT-7a instrument made structural (frozen engagement_gate):
      n_items                  eval items processed by this cell
      n_decidable              items whose ATTEMPT-0 verification was
                               decidable (extraction succeeded AND the
                               verifier engaged)
      n_attempt0_rejected      items whose attempt-0 answer was decidable and
                               REJECTED (inconsistent) — rate 0 is the
                               F2/d-ext vacuity signature, rate ~1 the
                               never-accepts degeneracy
      n_final_differs_attempt0 items whose FINAL answer differs from the
                               attempt-0 answer (retry visibly changed an
                               output at least once)"""
    finals = []
    eng = {"n_items": 0, "n_decidable": 0, "n_attempt0_rejected": 0,
           "n_final_differs_attempt0": 0}
    extraction_failures = 0
    for it in items:
        guard.start_item(it)
        eng["n_items"] += 1
        ans = None
        ans0 = None
        for attempt in range(k + 1):
            ans, _conf, lat, toks = answer_once(lm, frames, it, seed, attempt)
            guard.gen()
            meter.seq(lm, toks)
            meter.query_done(lat)
            if attempt == 0:
                ans0 = ans
            ok_ext, decidable, consistent, cpu_s = verify_answer(verifier, it, ans)
            meter.verifier(cpu_s)
            if attempt == 0:
                if ok_ext and decidable:
                    eng["n_decidable"] += 1
                    if not consistent:
                        eng["n_attempt0_rejected"] += 1
            if not ok_ext:
                extraction_failures += 1
                break  # instrument event: no free wins/losses (P10 section 4)
            if not decidable or consistent:
                break  # accepted (or verifier abstains off-coverage)
        if ans != ans0:
            eng["n_final_differs_attempt0"] += 1
        finals.append(ans)
    return finals, eng, extraction_failures


def run_self_verify_retry(lm, frames, items, gloss_by_urn, k, seed, meter,
                          guard):
    """P7 RT-2 arm 10: the model checks its own answer against the pinned
    gloss TEXT and retries — identical retry topology; the instrument is the
    model + text instead of the deterministic verifier."""
    finals = []
    for it in items:
        guard.start_item(it)
        ans = None
        for attempt in range(k + 1):
            ans, _conf, lat, toks = answer_once(lm, frames, it, seed, attempt)
            guard.gen()
            meter.seq(lm, toks)
            meter.query_done(lat)
            gloss = gloss_by_urn.get(it["urn"])
            if gloss is None:
                break  # no pinned gloss -> no check possible
            frame = frames["self_verify_frame"].format(
                term=it["label"], gloss=gloss["text"],
                question=it["question"], answer=ans)
            t0 = time.perf_counter()
            if isinstance(lm, StubLM):
                ok = lm.self_check(it, ans, it["answer"], seed, attempt)
            else:
                ok = lm.self_check(it, ans, it["answer"], seed, attempt,
                                   prompt=frame)
            guard.gen()
            meter.seq(lm, lm.count_tokens(frame) * 2)
            meter.query_done(time.perf_counter() - t0)
            if ok:
                break
        finals.append(ans)
    return finals


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_extraction_instrument_dxif(dxif_dir, rung, dqa_covered, verifier):
    """P10 gate measurement, REAL path (unchanged from poc/f2b): re-verifies
    the pinned d-xif labelled set (>=300 real model outputs over the ORIGINAL
    d-qa items) through THIS harness's extraction machinery — stored flags are
    NOT trusted; failures/errors are recomputed from the stored constrained
    answers against the pinned records."""
    outputs = load_jsonl(os.path.join(dxif_dir, "outputs",
                                      "%s.jsonl" % rung.lower()))
    by_id = {it["id"]: it for it in dqa_covered}
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
            errs += 1
    return {"n_labelled": n, "n_extraction_failures": fails,
            "n_extraction_errors": errs}


def run_extraction_instrument_mock(lm, frames, items, verifier, n_labelled,
                                   seed, guard):
    """P10 gate, MOCK path: cycles the eval items through the REAL
    extraction machinery with the stub LM (labelled MOCK)."""
    n_fail = 0
    n_err = 0
    for i in range(n_labelled):
        it = items[i % len(items)]
        guard.start_item(it)
        ans, _c, _lat, _toks = answer_once(lm, frames, it, seed, i)
        guard.gen()
        if det_u("xfail", lm.name, it["id"], seed, i) < lm.mock_xfail:
            ans = "MALFORMED"
        rec = extract_record(it, ans)
        if rec is None:
            n_fail += 1
            continue
        ok_ext, decidable, consistent, _cpu = verify_answer(verifier, it, ans)
        if ok_ext and decidable and not consistent and ans == it["answer"]:
            n_err += 1
    return {"n_labelled": n_labelled, "n_extraction_failures": n_fail,
            "n_extraction_errors": n_err}


# ---------------------------------------------------------------------------
# Emitter — kot-log/1 record BODIES (config + RAW metrics). Verbatim from
# poc/f2b (correction 1: append + flush at emit time so a stopped/timed-out
# run leaves every completed cell's record on disk).
# ---------------------------------------------------------------------------
class Emitter:
    def __init__(self, out_dir, mock):
        self.records = []
        self.path = os.path.join(
            out_dir, "run-records-f2bt%s.jsonl" % ("-mock" if mock else ""))
        self.phase = "mock" if mock else "final"
        with open(self.path, "w"):
            pass  # truncate once; every record below is an immediate append

    def emit(self, arm, rung, retry_budget, escalation_budget, seed, metrics,
             exit_status="ok"):
        body = {
            "event": "run",
            "phase": self.phase,
            "config": {"arm": arm, "rung": rung, "retry_budget": retry_budget,
                       "escalation_budget": escalation_budget, "seed": seed},
            "metrics": metrics,
            "exit": exit_status,
        }
        self.records.append(body)
        with open(self.path, "a") as f:
            f.write(json.dumps(body, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return body

    def write(self):
        return self.path


def cell_metrics(ext, mem, meter, lms, store_bytes, engagement=None):
    """DUAL-SCORED cell metrics — the row shape analysis/f2b_transfer.py
    consumes: item_correct_ext (endpoints) + item_correct_mem (descriptive)
    + metric_vector (F0 ledger) + verifier_engagement (verify arms)."""
    m = {"item_correct_ext": ext,
         "item_correct_mem": mem,
         "metric_vector": meter.ledger(lms, store_bytes)}
    if engagement is not None:
        m["verifier_engagement"] = engagement
    return m


# ---------------------------------------------------------------------------
# Input loading + fail-closed pins
# ---------------------------------------------------------------------------
def load_inputs(args):
    with open(os.path.join(args.inputs_dir, "f2bt-manifest.json"),
              encoding="utf-8") as f:
        man = json.load(f)
    pins = man["pins"]
    checks = {
        "dqatCoveredItemsSha256": os.path.join(args.dqat_dir, "items", "covered.jsonl"),
        "dqatManifestSha256": os.path.join(args.dqat_dir, "manifest.json"),
        "dadjtLabelsSha256": os.path.join(args.dadjt_dir, "labels.jsonl"),
        "dadjtSummarySha256": os.path.join(args.dadjt_dir, "summary.json"),
        "dqaCoveredItemsSha256": os.path.join(args.dqa_dir, "items", "covered.jsonl"),
        "dqaGlossCorpusSha256": os.path.join(args.dqa_dir, "gloss-corpus.jsonl"),
        "dqaManifestSha256": os.path.join(args.dqa_dir, "manifest.json"),
    }
    for key, path in checks.items():
        if sha256_file(path) != pins[key]:
            raise SystemExit("ERR_PIN: %s: %s sha != f2bt-manifest pin" % (key, path))
    # corpus-level kot-corpus-hash/1 checks against the FROZEN record's pins
    # (d-qa-t) and the ops amendment (d-adj-t) — the two verdict-bearing new
    # corpora of this experiment; the stage-2 runner fail-closes on the pin
    # (frozen record stage_discipline / design.md section 3.2).
    for key, base in (("dqatCorpusKotHash", args.dqat_dir),
                      ("dadjtCorpusKotHash", args.dadjt_dir)):
        got = corpus_kot_hash(base)
        if got != pins[key]:
            raise SystemExit("ERR_PIN: %s: %s kot-corpus-hash %s != pin %s"
                             % (key, base, got, pins[key]))

    covered_t = load_jsonl(checks["dqatCoveredItemsSha256"])
    dqa_covered = load_jsonl(checks["dqaCoveredItemsSha256"])
    gloss_docs = load_jsonl(checks["dqaGlossCorpusSha256"])
    labels = load_jsonl(checks["dadjtLabelsSha256"])
    with open(checks["dadjtSummarySha256"], encoding="utf-8") as f:
        adj_summary = json.load(f)
    covered_t.sort(key=lambda x: x["rank"])
    dqa_covered.sort(key=lambda x: x["rank"])

    # ---- adjudication internal consistency (fail closed) --------------------
    if adj_summary["analysis_input_metrics"]["labels_sha256"] != \
            pins["dadjtLabelsSha256"]:
        raise SystemExit("ERR_ADJ_PIN: summary.json labels_sha256 != the pinned "
                         "labels.jsonl sha — d-adj-t is internally inconsistent")
    gold_ext = {}
    for row in labels:
        gold_ext[row["id"]] = row["gold_ext"]
    missing = [it["id"] for it in covered_t if it["id"] not in gold_ext]
    if missing:
        raise SystemExit("ERR_LABELS_MISSING: %d d-qa-t items have no "
                         "labels.jsonl line (first: %s)"
                         % (len(missing), missing[0]))
    n_resolved = sum(1 for v in gold_ext.values() if v is not None)
    n_lab_pin = int(adj_summary["analysis_input_metrics"]["n_ext_labelled"])
    if n_resolved != n_lab_pin:
        raise SystemExit("ERR_ADJ_COUNTS: %d resolved gold_ext lines != "
                         "summary n_ext_labelled %d" % (n_resolved, n_lab_pin))
    return man, covered_t, dqa_covered, gloss_docs, gold_ext, adj_summary


def build_eval_set(man, covered_t, gold_ext, adj_summary, mock):
    """EVAL SET, frozen verbatim: the first per_arm_items externally-labelled
    (resolved gold_ext) d-qa-t items in pinned rank order; floor eval_floor,
    below which the runner refuses. Deterministic prefix — no sampling."""
    dc = man["design_constants_from_frozen_record"]
    labelled = [it for it in covered_t if gold_ext[it["id"]] is not None]
    floor = int(dc["eval_floor"])
    if len(labelled) < floor:
        raise SystemExit("ERR_EVAL_FLOOR: only %d externally-labelled items "
                         "< the frozen floor %d — refusing" % (len(labelled), floor))
    eval_items = labelled[:int(dc["per_arm_items"])]
    # fail-closed structural asserts: the verifier must have NO abstention
    # path on the eval set, and every gold_ext must live on the item's own
    # constrained answer surface (design.md section 6; anything else is a
    # data defect this runner must not paper over).
    for it in eval_items:
        if it.get("type") not in DQA_TYPES or not it.get("kernel_checkable"):
            raise SystemExit("ERR_ITEM_CHECKABLE: eval item %s is not a "
                             "kernel-checkable DQA-type item" % it["id"])
        keys, _gold = item_keys_gold(it)
        if gold_ext[it["id"]] not in keys:
            raise SystemExit("ERR_GOLD_SURFACE: %s gold_ext %r not on the "
                             "item's answer surface %s"
                             % (it["id"], gold_ext[it["id"]], keys))
    if not mock:
        n_eval_pin = int(adj_summary["analysis_input_metrics"]["n_eval_items"])
        if len(eval_items) != n_eval_pin:
            raise SystemExit("ERR_ADJ_COUNTS: eval prefix %d != summary "
                             "n_eval_items %d" % (len(eval_items), n_eval_pin))
    else:
        eval_items = eval_items[:man["mock"]["n_eval_items"]]
    return eval_items


# ---------------------------------------------------------------------------
# --dry-plan: the real-run cost plan vs the caps. Stdlib only; ESTIMATES.
# ---------------------------------------------------------------------------
def dry_plan(man, eval_items, gpu):
    plan = man["planning"]
    dc = man["design_constants_from_frozen_record"]
    frames = man["prompt_frames"]
    cpt = plan["chars_per_token_estimate"]
    tput = plan["throughput_tok_per_s"][gpu]
    usd = man["flop_accounting"]["usd_per_hour"][gpu]
    seeds, ks = dc["seeds"], dc["retry_sweep"]

    def est_tokens(item):
        keys, _ = item_keys_gold(item)
        prompt = build_prompt(frames, item)
        return len(prompt) / cpt * len(keys)

    tok_cov = sum(est_tokens(i) for i in eval_items)

    cells = []  # (rung, tokens); retry worst case = k+1 attempts
    for _s in seeds:
        cells.append(("R1", tok_cov))                        # alone R1
        cells.append(("R3", tok_cov))                        # alone R3
        for k in ks:
            cells.append(("R1", tok_cov * (k + 1)))          # kernel-verify
            cells.append(("R1", tok_cov * (k + 1)))          # shuffled (NOT cut)
            cells.append(("R1", tok_cov * (k + 1) * 2))      # gloss self-verify (+check)
    # extraction-instrument: CPU-only re-verification of the pinned d-xif set
    # NO PRM / NO kernel-as-text / NO d-ext in this design (frozen dropped_arms)

    hours = {"R1": 0.0, "R3": 0.0}
    for rung, toks in cells:
        hours[rung] += toks / tput[rung] / 3600.0
    est_h = sum(hours.values())
    worst_h = est_h * plan["overhead_factor"]
    cap = dc["budget"]
    lines = [
        "f2b-transfer STAGE-2 --dry-plan (ESTIMATES ONLY — planning constants",
        "from f2bt-manifest.json; no GPU, no network, $0 spent by this command)",
        "",
        "eval set: %d externally-labelled d-qa-t items (deterministic rank "
        "prefix; frozen per_arm_items %d, floor %d)"
        % (len(eval_items), dc["per_arm_items"], dc["eval_floor"]),
        "cells inventoried: %d GPU cells (arms x k x %d seeds; the P10 iface "
        "gate is CPU-only; NO PRM / text / d-ext)"
        % (len(cells), len(seeds)),
        "",
        "GPU-hours estimate on %s (tok/s planning table %s):" % (gpu, tput),
        "  R1 %.2f h   R3 %.2f h   total %.2f h"
        % (hours["R1"], hours["R3"], est_h),
        "  with %.1fx overhead factor: %.2f h" % (plan["overhead_factor"], worst_h),
        "",
        "cost at Modal list $%.2f/h (%s):" % (usd, gpu),
        "  point estimate  $%.2f" % (est_h * usd),
        "  worst case      $%.2f  (overhead-inflated)" % (worst_h * usd),
        "  hard ceiling    $%.2f  (registry gpu_hours_cap %d h x $%.2f/h)"
        % (cap["gpu_hours_cap"] * usd, cap["gpu_hours_cap"], usd),
        "",
        "caps (registry/experiments/f2b-transfer.json): usd_cap $%d, "
        "gpu_hours_cap %d h, wall_clock_cap %d h; Tier-1 cap $%d"
        % (cap["usd_cap"], cap["gpu_hours_cap"], cap["wall_clock_cap_hours"],
           cap["tier_cap_usd"]),
        "",
    ]
    verdicts = [
        ("worst case vs usd_cap ($%d)" % cap["usd_cap"],
         worst_h * usd <= cap["usd_cap"]),
        ("hard ceiling vs Tier-1 cap ($%d)" % cap["tier_cap_usd"],
         cap["gpu_hours_cap"] * usd <= cap["tier_cap_usd"]),
        ("estimate vs gpu_hours_cap (%d h)" % cap["gpu_hours_cap"],
         worst_h <= cap["gpu_hours_cap"]),
    ]
    for name, ok in verdicts:
        lines.append("  %-42s %s" % (name, "OK" if ok else "OVER — DO NOT LAUNCH"))
    lines.append("")
    lines.append("frozen-design cost note honoured: the shuffled arm is the one")
    lines.append("control NOT to cut — inventoried at full item count at fixed k=4.")
    print("\n".join(lines))
    return all(ok for _n, ok in verdicts)


# ---------------------------------------------------------------------------
# Cell driver
# ---------------------------------------------------------------------------
def run_cells(args, man, eval_items, covered_t, dqa_covered, gloss_docs,
              gold_ext, adj_summary, log):
    mock = args.mock
    dc = man["design_constants_from_frozen_record"]
    frames = man["prompt_frames"]
    seeds = man["mock"]["seeds"] if mock else dc["seeds"]
    ks = dc["retry_sweep"]

    if not mock:
        # d-xif (P10 labelled extraction set) — fail closed on absence or pin
        if not os.path.isdir(args.dxif_dir or ""):
            raise SystemExit("ERR_MISSING_DXIF: d-xif labelled extraction set "
                             "missing — the P10 instrument gate cannot be "
                             "measured; refusing a final-phase run")
        for key, rel in (("dxifOutputsR1Sha256", os.path.join("outputs", "r1.jsonl")),
                         ("dxifManifestSha256", "manifest.json")):
            pin = man["pins"].get(key)
            path = os.path.join(args.dxif_dir, rel)
            if not pin or sha256_file(path) != pin:
                raise SystemExit("ERR_PIN: %s: %s sha != f2bt-manifest pin" % (key, path))
        iface_n = dc["iface_gate"]["n_min_per_rung"]
    else:
        iface_n = man["mock"]["iface_n_labelled"]

    verifier = KernelVerifier(args.records_root)
    verifier.index_labels(eval_items)
    # perm spans the FULL covered-concept set of d-qa-t (all 108 concepts),
    # not just the concepts present in the eval prefix: the derangement is
    # over concept urns and must cover every urn the verify pipeline may
    # query; index_labels(eval_items) restricts which items are SCORED.
    shuf = ShuffledKernelVerifier(args.records_root, covered_t,
                                  man["shuffle"]["perm_seed"])
    shuf.index_labels(eval_items)
    # record the seed-pinned permutation next to the results (frozen: recorded)
    shuffle_map = {"perm_seed": shuf.perm_seed, "algorithm": man["shuffle"]["algorithm"],
                   "n_concepts": len(shuf.perm), "map_urn_to_record_of": shuf.perm,
                   "sha256_of_map": shuf.perm_sha256,
                   "derangement_check": "no fixed points (asserted at build)"}
    with open(os.path.join(args.out_dir, "shuffle-map.json"), "w") as f:
        json.dump(shuffle_map, f, indent=1, sort_keys=True)
        f.write("\n")
    log("shuffled-verifier permutation: seed=%d sha=%s"
        % (shuf.perm_seed, shuf.perm_sha256[:12]))

    gloss_by_urn = {d["urn"]: d for d in gloss_docs if "urn" in d}
    for it in eval_items:
        if it["urn"] not in gloss_by_urn:
            raise SystemExit("ERR_GLOSS_MISSING: eval item %s urn %s has no "
                             "pinned gloss doc — the gloss-self-verify arm "
                             "would silently degenerate" % (it["id"], it["urn"]))
    store_bytes_gloss = os.path.getsize(os.path.join(args.dqa_dir,
                                                     "gloss-corpus.jsonl"))
    # store = UNIQUE canonical record bytes (F0 §3.4; fixed in f2b, kept here)
    store_bytes_records = sum(
        os.path.getsize(os.path.join(args.records_root, p))
        for p in sorted({it["record_path"] for it in eval_items
                         if it.get("record_path")}))

    def make_lm(rung):
        if mock:
            lm = StubLM(rung, man["mock"])
            lm.mock_xfail = man["mock"]["stub_extraction_fail_rate"]
            return lm
        spec = man["models"][rung]
        return HFLM(spec["repo"], spec["revision"], args.device)

    emit = Emitter(args.out_dir, mock)
    fc = man["flop_accounting"]
    gpu = args.gpu_class
    lms = {}

    def lm_for(rung):
        if rung not in lms:
            lms[rung] = make_lm(rung)
        return lms[rung]

    def new_meter():
        return FlopMeter(fc, gpu)

    # ---- mock-only adjudication-instrument record (pipeline validation) -----
    # Integers copied VERBATIM from the pinned d-adj-t summary.json so the
    # pinned analysis resolves its stage-1 fields from the mock records file
    # alone. phase="mock"; NEVER log-appended — the REAL stage-1 record is
    # already in results-log/f2b-transfer.jsonl (a real run emitting this
    # again would make the analysis fail on a duplicate, by design).
    if mock:
        emit.emit(ARM_ADJ, "R1", 0, 0, 0,
                  dict(adj_summary["analysis_input_metrics"]))
        log("mock adjudication-instrument record emitted (verbatim pinned "
            "summary integers; phase=mock, never a measurement of this run)")

    # ---- per-cell safety driver (f2b-replicate correction 1, carried over) --
    def run_cell(arm, rung, k, seed, fn):
        guard = CellGuard("%s/%s/k=%s/seed=%s" % (arm, rung, k, seed),
                          args.cell_timeout_s, args.max_gen_per_item)
        try:
            metrics = fn(guard)
        except CellBudgetExceeded as e:
            emit.emit(arm, rung, k, 0, seed, {
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
        emit.emit(arm, rung, k, 0, seed, metrics)
        log("cell %s %s k=%s seed=%s done (%.1fs)"
            % (arm, rung, k, seed, guard.elapsed()))
        return metrics

    # ---- model-alone at R1 and R3 (per seed for pairing) --------------------
    for rung in ("R1", "R3"):
        lm = lm_for(rung)
        for seed in seeds:
            def cell(guard, lm=lm, seed=seed):
                meter = new_meter()
                finals = run_alone(lm, frames, eval_items, seed, meter, guard)
                ext, mem = score_dual(eval_items, finals, gold_ext)
                return cell_metrics(ext, mem, meter, [lm], 0)
            run_cell(ARM_ALONE, rung, 0, seed, cell)

    lm1 = lm_for("R1")

    # ---- kernel-verify-retry (true records) and shuffled control ------------
    # Both emit the verifier_engagement block; the frozen engagement gate sums
    # it over kernel-verify-retry cells (the analysis reads only those); the
    # shuffled block is informative provenance at identical topology.
    for arm, ver in ((ARM_VERIFY, verifier), (ARM_SHUF, shuf)):
        for k in ks:
            for seed in seeds:
                def cell(guard, arm=arm, ver=ver, k=k, seed=seed):
                    meter = new_meter()
                    finals, eng, _xf = run_verify_retry(
                        lm1, frames, eval_items, ver, k, seed, meter, guard)
                    ext, mem = score_dual(eval_items, finals, gold_ext)
                    m = cell_metrics(ext, mem, meter, [lm1],
                                     store_bytes_records, engagement=eng)
                    if arm == ARM_SHUF:
                        m["shuffle_permutation_sha256"] = shuf.perm_sha256
                        m["shuffle_perm_seed"] = shuf.perm_seed
                    return m
                run_cell(arm, "R1", k, seed, cell)

    # ---- gloss-self-verify-retry (P7 RT-2 commodity control) ----------------
    for k in ks:
        for seed in seeds:
            def cell(guard, k=k, seed=seed):
                meter = new_meter()
                finals = run_self_verify_retry(lm1, frames, eval_items,
                                               gloss_by_urn, k, seed, meter,
                                               guard)
                ext, mem = score_dual(eval_items, finals, gold_ext)
                return cell_metrics(ext, mem, meter, [lm1], store_bytes_gloss)
            run_cell(ARM_SELFV, "R1", k, seed, cell)

    # ---- P10 extraction-instrument gate (R1 — the only verifier host rung) --
    def cell_iface(guard):
        if mock:
            return run_extraction_instrument_mock(lm1, frames, eval_items,
                                                  verifier, iface_n, seeds[0],
                                                  guard)
        gate_verifier = KernelVerifier(args.records_root)
        gate_verifier.index_labels(dqa_covered)
        st = run_extraction_instrument_dxif(args.dxif_dir, "R1",
                                            dqa_covered, gate_verifier)
        if st["n_labelled"] < iface_n:
            raise SystemExit("ERR_DXIF_N: R1 has %d labelled outputs < the "
                             "frozen n_min_per_rung %d"
                             % (st["n_labelled"], iface_n))
        return st
    stats = run_cell(ARM_IFACE, "R1", 0, seeds[0], cell_iface)
    log("iface gate: %d labelled, %d extraction failures"
        % (stats["n_labelled"], stats["n_extraction_failures"]))

    return emit


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    root3 = os.path.join(here, "..", "..", "..")
    ap.add_argument("--inputs-dir", default=os.path.join(here, "..", "inputs"))
    ap.add_argument("--dqat-dir", default=os.path.join(root3, "data", "d-qa-t"))
    ap.add_argument("--dadjt-dir", default=os.path.join(root3, "data", "d-adj-t"))
    ap.add_argument("--dqa-dir", default=os.path.join(root3, "data", "d-qa"))
    ap.add_argument("--records-root", default=root3,
                    help="root that item record_path fields resolve against")
    ap.add_argument("--dxif-dir", default=None,
                    help="d-xif labelled extraction set (REQUIRED for real runs)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--gpu-class", default="A10G", choices=["T4", "A10G", "A100"])
    ap.add_argument("--mock", action="store_true",
                    help="stub-LM mechanics check on CPU; $0; labelled MOCK")
    ap.add_argument("--dry-plan", action="store_true",
                    help="print the real-run cost plan vs caps; runs nothing")
    ap.add_argument("--max-hours", type=float, default=20.0)
    ap.add_argument("--cell-timeout-s", type=float, default=None,
                    help="per-cell wall-clock safety bound (f2b correction 1); "
                         "default %s s by --gpu-class"
                         % sorted(CELL_TIMEOUT_S_DEFAULT.items()))
    ap.add_argument("--max-gen-per-item", type=int,
                    default=MAX_GEN_PER_ITEM_DEFAULT,
                    help="per-item generation cap within one cell "
                         "(structural max is 10, gloss-self-verify at k=4)")
    args = ap.parse_args()
    if args.cell_timeout_s is None:
        args.cell_timeout_s = CELL_TIMEOUT_S_DEFAULT[args.gpu_class]
    t0 = time.time()

    man, covered_t, dqa_covered, gloss_docs, gold_ext, adj_summary = \
        load_inputs(args)
    eval_items = build_eval_set(man, covered_t, gold_ext, adj_summary,
                                args.mock)

    if args.dry_plan:
        # plan over the REAL frozen eval prefix (not the mock cut)
        full_eval = build_eval_set(man, covered_t, gold_ext, adj_summary,
                                   mock=False)
        ok = dry_plan(man, full_eval, args.gpu_class)
        sys.exit(0 if ok else 2)

    os.makedirs(args.out_dir, exist_ok=True)

    def log(msg):
        print("[f2bt %7.1fs] %s" % (time.time() - t0, msg), flush=True)

    label = "MOCK" if args.mock else "FULL"
    log("mode=%s device=%s eval_items=%d (externally-labelled d-qa-t rank "
        "prefix; %d labelled on disk)"
        % (label, args.device, len(eval_items),
           sum(1 for v in gold_ext.values() if v is not None)))
    if not args.mock and args.device != "cuda":
        log("WARNING: real run requested on CPU — allowed but slow")

    emit = run_cells(args, man, eval_items, covered_t, dqa_covered,
                     gloss_docs, gold_ext, adj_summary, log)
    records_path = emit.write()

    hours = (time.time() - t0) / 3600.0
    if hours > args.max_hours:
        raise SystemExit("ERR_TIME_BUDGET: exceeded %.1fh" % args.max_hours)

    suffix = "-mock" if args.mock else ""
    results = {
        "experiment": "f2b-transfer",
        "stage": 2,
        "outcome": ("MOCK-HARNESS-COMPLETE" if args.mock else "HARNESS-COMPLETE"),
        "outcome_note": "NOT a hypothesis verdict — raw run-records only; the "
                        "verdict is computed by the pinned "
                        "analysis/f2b_transfer.py + tools/registry/"
                        "verdict-gen.py under run-vs-audit separation (the "
                        "REAL stage-1 adjudication record is already in the "
                        "results log and is not re-emitted by a real run)",
        "mode": label,
        "date": utcnow(),
        "device": args.device,
        "gpu_class_assumed_for_usd": args.gpu_class,
        "pins": man["pins"],
        "models": ({"note": "MOCK — synthetic stub LM, no models loaded"}
                   if args.mock else
                   {r: man["models"][r] for r in ("R1", "R3")}),
        "n_records": len(emit.records),
        "n_eval_items": len(eval_items),
        "records_file": os.path.basename(records_path),
        "seeds": man["mock"]["seeds"] if args.mock else
                 man["design_constants_from_frozen_record"]["seeds"],
        "retry_sweep": man["design_constants_from_frozen_record"]["retry_sweep"],
        "shuffle": {"perm_seed": man["shuffle"]["perm_seed"],
                    "map_file": "shuffle-map.json"},
        "wallClockHours": hours,
    }
    with open(os.path.join(args.out_dir, "results-f2bt%s.json" % suffix), "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    log("OUTCOME: %s (%d run-record bodies in %s)"
        % (results["outcome"], len(emit.records), records_path))


if __name__ == "__main__":
    main()
