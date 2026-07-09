#!/usr/bin/env python3
"""f2b-replicate — fresh-item replication + oracle-structure controls for the
F2 verifier-offload signal (architecture-advisor frozen design, implemented
faithfully; registry/experiments/f2b-replicate.json).

The ONLY thing the GPU runs. WHY THIS EXPERIMENT EXISTS: the F2 "135M+kernel
beats 1.7B" signal (quarantined exploratory, poc/f2/f2b-reanalysis.md) is
plausibly an ORACLE-LEAKAGE artifact — the verifier accepts iff the answer
string-equals the canonical record, and D-QA gold answers were DEFINED by
that same equality. This run separates REAL from NOT-LEAKY on fresh items:

RIGHT-SIZED (advisor 2026-07-09): 250 fresh items (rank-prefix subset), 3
paired seeds, a SINGLE pre-registered retry budget k=4 (retry_sweep=[4]; the
analysis best-k select over a singleton is a no-op = fixed k=4), gold-oracle
DROPPED, single A100-40GB. RETRIES RUN ONLY AT R1 (135M); R3 (1.7B) is used
ONLY for the single-pass alone baseline — there is NO 1.7B retry ladder.

  model-alone                     R1 (SmolLM2-135M) and R3 (SmolLM2-1.7B), single pass
  kernel-verify-retry             R1, k=4 — the kernel arm (true records) [PRIMARY]
  shuffled-kernel-verify-retry    R1, k=4 — LOAD-BEARING: identical retry topology,
                                  but the verifier checks each item against a PERMUTED
                                  record->concept map (seed-pinned derangement,
                                  recorded). If this recovers >=30% of the true arm's
                                  lift-over-alone, the lift is retry-against-any-oracle
                                  STRUCTURE, not kernel CONTENT, and the claim dies.
  gloss-self-verify-retry         R1, k=4 (P7 RT-2 arm 10, active text baseline)
  prm-verifier                    R1 (HC3 trained-PRM comparator; best-of-N, N=4)
  kernel-as-text                  R1 (Law-2 passive text null)
  extraction-instrument           P10 gate re-verification over the pinned d-xif
                                  labelled set (R1)

DROPPED vs F2 (advisor design): R2, gold-oracle ceiling, the k-ladder, all
cascades, int4, RAG, self-consistency.

FIXED vs F2 (instrument defect, f2b-reanalysis.md section 3): ext_vector no
longer bypasses the arm pipeline — the external D-EXT slice now runs through
each arm's OWN retry pipeline. NOTE the measured semantics: d-ext items are
not kernel-checkable (kernel_checkable=false by construction), so on this
slice the verifier ABSTAINS off-coverage; the vector measures deployed
off-coverage behaviour, not transfer (transfer = the gated f2b-TRANSFER
experiment).

Items: data/d-qa-r — FRESH, ID-disjoint, prompt-surface-disjoint draw
(new generator seed) over the same 108 covered concepts; NOT a rerun of the
logged 500 (deterministic decode would reproduce them).

Shared affordance (P10 section 5, IF-C): every arm answers through the same
constrained surface — sequence-logprob selection over the pinned option set;
arms differ only in context block and verification instrument.

Usage:
  python3 f2b_runner.py --out-dir /tmp/f2b --device cuda        # real (Modal)
  python3 f2b_runner.py --out-dir /tmp/f2b --mock               # stub LM, CPU, $0
  python3 f2b_runner.py --out-dir /tmp/f2b --dry-plan           # cost plan vs caps

HARD RULES honoured here: --mock and --dry-plan spend $0 and never touch a
GPU or the network; mock numbers are labelled MOCK end-to-end and are never
measurements; real runs fail closed on any missing pin (ERR_*). RAW metrics
only — verdicts belong to the pinned analysis/f2b_replicate.py +
tools/registry/verdict-gen.py under run-vs-audit separation.

SAFETY (correction 1, registry/corrections/f2b-replicate/): every cell runs
under a CellGuard — a per-cell wall-clock timeout plus a max-generations-
per-item cap on EVERY arm — and every completed cell's record is flushed to
disk immediately, so a pathological path self-terminates as a logged
exit:"timeout" record (ERR_CELL_TIMEOUT) with partials on disk instead of
hanging a GPU container silently. The gold-oracle-retry acceptance loop is
additionally hard-capped at GOLD_ORACLE_MAX_ATTEMPTS and records the
per-item reached-gold-within-cap vector. Implementation-only: arms,
endpoints, gates and kills are unchanged.
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

# F0 flop-meter — shared poc/f0/ package (the `f0-harness` depends_on gate).
_POC_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."))
if _POC_DIR not in sys.path:
    sys.path.insert(0, _POC_DIR)
from f0 import FlopMeter  # noqa: E402

# ---------------------------------------------------------------------------
# Constants — arm names MUST equal analysis/f2b_replicate.py + registry IV levels
# ---------------------------------------------------------------------------
ARM_ALONE = "model-alone"
ARM_VERIFY = "kernel-verify-retry"
ARM_SHUF = "shuffled-kernel-verify-retry"
ARM_SELFV = "gloss-self-verify-retry"
ARM_PRM = "prm-verifier"
ARM_TEXT = "kernel-as-text"
ARM_GOLD = "gold-oracle-retry"
ARM_IFACE = "extraction-instrument"

SEED_BASE = 20260709  # published fixed base seed (matches the f2b SAP PRNG seed)

# ---------------------------------------------------------------------------
# SAFETY BOUNDS (correction 1, registry/corrections/f2b-replicate/): every
# arm's per-cell work is bounded so that any pathological path SELF-TERMINATES
# as a LOGGED exit:"timeout" record instead of silently occupying a GPU
# container (the 2026-07-09 full run was stopped by the operator after 3.5 h
# with zero shipped artifacts — the run was in fact progressing, but nothing
# on disk or in the results channel could show it; see the correction record).
# Implementation-only: no arm, endpoint, gate or kill is changed.
#   GOLD_ORACLE_MAX_ATTEMPTS  explicit hard cap on the gold-oracle-retry
#       acceptance loop, independent of the retry_sweep values (structurally
#       the loop was already bounded at k+1 <= 5); every gold cell records
#       the realized cap and the per-item reached-gold-within-cap vector.
#   MAX_GEN_PER_ITEM_DEFAULT  cap on model generations (answer, self-check or
#       PRM score) for ONE item within ONE cell; the largest structural count
#       is gloss-self-verify at k=4 (5 answers + 5 self-checks = 10) so 16
#       can only trip on a defect.
#   CELL_TIMEOUT_S_DEFAULT    per-cell wall-clock budget (one emitted record
#       = one cell, ext slice included), ~4x the slowest expected real cell
#       (R3-alone, ~15 min on A10G) and far below the 12 h Modal timeout;
#       T4 is ~3x slower, hence the larger default.
GOLD_ORACLE_MAX_ATTEMPTS = 8
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
    item cap. Arms call start_item() once per item and gen() once per model
    generation; a breach raises CellBudgetExceeded, which the cell driver
    turns into a flushed exit:"timeout" record (excluded from eligible run
    records by verdict-gen's exit=="ok" rule -> the run fails closed as
    INCOMPLETE-DATA/INSTRUMENT-INVALID, never as a hang, never as data)."""

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

# d-qa item types the IF-C extraction + kernel verifier understand; anything
# else (e.g. d-ext obqa-mcq) is out of the verifier's domain: it ABSTAINS
# off-coverage WITHOUT attempting extraction (an abstention is a
# verifier-coverage fact, never a P10 extraction-instrument event).
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
# data/d-qa-r/build-dqar.py, which copies it) so the verifier's canonical
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
# Byte-identical semantics to poc/f2/runner/f2_runner.py::KernelVerifier,
# plus shown_definition() (the term-match question's definition text, which
# is a property of the ITEM, not of the verifier's belief — load-bearing for
# the shuffled arm below).
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
    """The oracle-STRUCTURE control (advisor design, load-bearing arm).

    Identical machinery and retry topology to KernelVerifier, but every
    record lookup the verifier performs for its OWN belief goes through a
    seed-pinned DERANGEMENT of the covered-concept map (Sattolo cyclic
    permutation: provably no fixed points): item about concept u is checked
    against the canonical record of perm[u]; a chosen term's record is the
    record of perm[concept-of-term]. Item-level facts (the definition text
    shown inside a term-match question) are NOT permuted — they are part of
    the item, not of the verifier's belief.

    What survives in this arm is exactly the retry-against-an-oracle
    STRUCTURE (rejection-driven resampling against pinned records at
    identical cost); what is destroyed is the record CONTENT's relation to
    the item. If accuracy lift survives here, the lift was never about the
    kernel's content.
    """

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
    VERBATIM semantics from poc/f2/runner/f2_runner.py (the measured
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
# LM backends — one interface, two implementations (int4 path dropped: the
# int4 arm is not in this design).
# ---------------------------------------------------------------------------
class StubLM:
    """SYNTHETIC mechanics-only stand-in (mock mode; no torch). Every output
    is a deterministic function of (rung, seed, item, attempt) via sha256.
    The planted per-rung skill gradient exists ONLY so the analysis
    contract's separation gate and gap denominators resolve during mock
    validation. Never a measurement."""

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
    """HC3/EF3 trained-PRM comparator — Skywork-o1-Open-PRM-Qwen-2.5-1.5B at
    the PINNED revision. Byte-identical semantics to the F2 backend (sigmoid
    of the last-token reward logit over the chat-formatted pair). `gold`,
    `seed`, `idx` are IGNORED on purpose — a real reward model never sees the
    gold answer."""

    def __init__(self, repo, revision, device, frames):
        import torch
        from transformers import AutoModel, AutoTokenizer
        if not repo or not revision:
            raise SystemExit("ERR_UNPINNED_MODEL: prm has no pinned repo/revision")
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
    scoring (the IF-C constrained surface). Never touched by --mock."""

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
# Arm implementations. Each returns a per-item 0/1 list for one cell.
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


def run_alone(lm, frames, items, seed, meter, guard, context_fn=None):
    correct = []
    for it in items:
        guard.start_item(it)
        docs = context_fn(it) if context_fn else None
        ans, _conf, lat, toks = answer_once(lm, frames, it, seed, 0, docs)
        guard.gen()
        meter.seq(lm, toks)
        meter.query_done(lat)
        correct.append(1 if ans == it["answer"] else 0)
    return correct


def verify_answer(verifier, item, ans):
    """IF-C extract + kernel check. Returns (extract_ok, decidable,
    consistent, cpu_s).

    THE F2 ext_vector DEFECT IS CLOSED HERE at the instrument level: items
    outside the verifier's domain (external d-ext items — type not a d-qa
    type) short-circuit to an off-coverage ABSTENTION (decidable=False)
    without attempting extraction; the retry loop then accepts the first
    answer. Abstention is a verifier-coverage fact on the record, never a
    P10 extraction-instrument event."""
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
    arms — the arms differ ONLY in the verifier object passed in."""
    correct = []
    extraction_failures = 0
    for it in items:
        guard.start_item(it)
        ans = None
        for attempt in range(k + 1):
            ans, _conf, lat, toks = answer_once(lm, frames, it, seed, attempt)
            guard.gen()
            meter.seq(lm, toks)
            meter.query_done(lat)
            ok_ext, decidable, consistent, cpu_s = verify_answer(verifier, it, ans)
            meter.verifier(cpu_s)
            if not ok_ext:
                extraction_failures += 1
                break  # instrument event: no free wins/losses (P10 section 4)
            if not decidable or consistent:
                break  # accepted (or verifier abstains off-coverage)
        correct.append(1 if ans == it["answer"] else 0)
    return correct, extraction_failures


def run_gold_oracle_retry(lm, frames, items, k, seed, meter, guard):
    """DIAGNOSTIC CEILING (advisor design): retry until the answer equals the
    true gold label, max k attempts-after-the-first AND never more than
    GOLD_ORACLE_MAX_ATTEMPTS total (correction 1: the cap is explicit and
    recorded, so the diagnostic — does the model reach gold within the cap —
    is preserved with a provably bounded loop); final = last attempt.
    NON-DEPLOYABLE BY CONSTRUCTION — the acceptance test reads the answer
    key. Reported only as the retry topology's ceiling; it can never be a
    shipped arm and never contributes to any PASS.

    Returns (correct, reached_gold_within_cap, attempts_cap). Because
    acceptance is exact-gold and the final answer is the last attempt,
    reached_gold_within_cap[i] == correct[i] by construction; it is recorded
    under its own name so the diagnostic reads as what it is."""
    attempts_cap = min(k + 1, GOLD_ORACLE_MAX_ATTEMPTS)
    correct = []
    reached = []
    for it in items:
        guard.start_item(it)
        ans = None
        for attempt in range(attempts_cap):
            ans, _conf, lat, toks = answer_once(lm, frames, it, seed, attempt)
            guard.gen()
            meter.seq(lm, toks)
            meter.query_done(lat)
            if ans == it["answer"]:
                break
        got = 1 if ans == it["answer"] else 0
        correct.append(got)
        reached.append(got)
    return correct, reached, attempts_cap


def run_self_verify_retry(lm, frames, items, gloss_by_urn, k, seed, meter,
                          guard):
    """P7 RT-2 arm 10: the model checks its own answer against the pinned
    gloss TEXT and retries — identical retry topology; the instrument is the
    model + text instead of the deterministic verifier."""
    correct = []
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
        correct.append(1 if ans == it["answer"] else 0)
    return correct


def run_prm(lm, prm, frames, items, n_cand, seed, meter, guard):
    correct = []
    for it in items:
        guard.start_item(it)
        cands = []
        t0 = time.perf_counter()
        for v in range(n_cand):
            ans, _c, _lat, toks = answer_once(lm, frames, it, seed, v)
            guard.gen()
            meter.seq(lm, toks)
            cands.append(ans)
        scored = []
        for i, a in enumerate(cands):
            scored.append((prm.score(it, a, it["answer"], seed, i), -i, a))
            guard.gen()
        prompt_toks = lm.count_tokens(build_prompt(frames, it)) * n_cand
        meter.model_flops += 2.0 * prm.n_active * prompt_toks
        best = sorted(scored, reverse=True)[0][2]
        meter.query_done(time.perf_counter() - t0)
        correct.append(1 if best == it["answer"] else 0)
    return correct


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_extraction_instrument_dxif(dxif_dir, rung, dqa_covered, verifier):
    """P10 gate measurement, REAL path: re-verifies the pinned d-xif labelled
    set (>=300 real model outputs, built pre-F2-final by xif_runner.py over
    the ORIGINAL d-qa items) through THIS harness's extraction machinery —
    stored flags are NOT trusted; failures/errors are recomputed from the
    stored constrained answers against the pinned records."""
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
    """P10 gate, MOCK path: cycles the fresh items through the REAL
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
# Emitter — kot-log/1 record BODIES (config + RAW metrics).
# ---------------------------------------------------------------------------
class Emitter:
    """Correction 1: records are APPENDED + FLUSHED to disk at emit time, so
    a stopped, timed-out or crashed run leaves every completed cell's record
    on disk (the 2026-07-09 stopped run left an EMPTY results channel after
    3.5 h because all 76 cells were buffered in memory until the very end —
    indistinguishable from a hang from outside the container)."""

    def __init__(self, out_dir, mock):
        self.records = []
        self.path = os.path.join(
            out_dir, "run-records-f2b%s.jsonl" % ("-mock" if mock else ""))
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


def cell_metrics(correct, meter, lms, store_bytes, external=None):
    m = {"item_correct": correct,
         "metric_vector": meter.ledger(lms, store_bytes)}
    if external is not None:
        m["item_correct_external"] = external
    return m


# ---------------------------------------------------------------------------
# Input loading + fail-closed pins
# ---------------------------------------------------------------------------
def load_inputs(inputs_dir, dqa_dir, dqar_dir):
    with open(os.path.join(inputs_dir, "f2b-manifest.json"), encoding="utf-8") as f:
        man = json.load(f)
    pins = man["pins"]
    checks = {
        "dqarCoveredItemsSha256": os.path.join(dqar_dir, "items", "covered.jsonl"),
        "dqarManifestSha256": os.path.join(dqar_dir, "manifest.json"),
        "dqaCoveredItemsSha256": os.path.join(dqa_dir, "items", "covered.jsonl"),
        "dqaGlossCorpusSha256": os.path.join(dqa_dir, "gloss-corpus.jsonl"),
        "dqaManifestSha256": os.path.join(dqa_dir, "manifest.json"),
    }
    for key, path in checks.items():
        if sha256_file(path) != pins[key]:
            raise SystemExit("ERR_PIN: %s: %s sha != f2b-manifest pin" % (key, path))
    covered_r = load_jsonl(checks["dqarCoveredItemsSha256"])
    dqa_covered = load_jsonl(checks["dqaCoveredItemsSha256"])
    gloss_docs = load_jsonl(checks["dqaGlossCorpusSha256"])
    covered_r.sort(key=lambda x: x["rank"])
    dqa_covered.sort(key=lambda x: x["rank"])
    return man, covered_r, dqa_covered, gloss_docs


# ---------------------------------------------------------------------------
# --dry-plan: the real-run cost plan vs the caps. Stdlib only; ESTIMATES.
# ---------------------------------------------------------------------------
def dry_plan(man, covered_r, gpu):
    plan = man["planning"]
    dc = man["design_constants_from_frozen_record"]
    frames = man["prompt_frames"]
    cpt = plan["chars_per_token_estimate"]
    tput = plan["throughput_tok_per_s"][gpu]
    usd = man["flop_accounting"]["usd_per_hour"][gpu]
    seeds, ks = dc["seeds"], dc["retry_sweep"]
    n_ext = 500  # pinned d-ext size

    def est_tokens(item, context=False):
        keys, _ = item_keys_gold(item)
        prompt = build_prompt(frames, item)
        t = len(prompt) / cpt
        if context:
            t += 70  # one gloss doc
        return t * len(keys)

    # advisor right-size: the plan reflects the fixed per_arm_items subset (250)
    covered_use = covered_r[:int(dc["per_arm_items"])]
    tok_cov = sum(est_tokens(i) for i in covered_use)
    tok_cov_ctx = sum(est_tokens(i, True) for i in covered_use)
    tok_ext = n_ext * 250 * 2  # yes/no + short prompts, planning placeholder

    cells = []  # (rung, tokens); retry worst case = k+1 attempts
    for _s in seeds:
        cells.append(("R1", tok_cov + tok_ext))                    # alone R1
        cells.append(("R3", tok_cov + tok_ext))                    # alone R3
        for k in ks:
            cells.append(("R1", (tok_cov + tok_ext) * (k + 1)))    # verify
            cells.append(("R1", (tok_cov + tok_ext) * (k + 1)))    # shuffled (NOT cut)
            cells.append(("R1", tok_cov * (k + 1) * 2))            # self-verify (+check)
            # gold-oracle DROPPED (advisor right-size); not inventoried
        cells.append(("R1", tok_cov * man["arm_plan"]["prm_best_of_n"] * 1.5))  # PRM
    cells.append(("R1", tok_cov_ctx + tok_ext))                    # kernel-as-text
    # extraction-instrument: CPU-only re-verification of the pinned d-xif set

    hours = {"R1": 0.0, "R3": 0.0}
    for rung, toks in cells:
        hours[rung] += toks / tput[rung] / 3600.0
    est_h = sum(hours.values())
    worst_h = est_h * plan["overhead_factor"]
    cap = dc["budget"]
    lines = [
        "f2b-replicate --dry-plan (ESTIMATES ONLY — planning constants from",
        "f2b-manifest.json; no GPU, no network, $0 spent by this command)",
        "",
        "eval set: %d FRESH d-qa-r covered items (rank-prefix of %d on disk); "
        "external slice %d (pinned d-ext)"
        % (len(covered_use), len(covered_r), n_ext),
        "cells inventoried: %d  (arms x k x %d seeds; iface gate is CPU-only)"
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
        "caps (registry/experiments/f2b-replicate.json): usd_cap $%d, "
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
    lines.append("advisor cost note honoured: the shuffled arm is the one cost NOT")
    lines.append("to cut — it is inventoried at full item count at the fixed k=4.")
    print("\n".join(lines))
    return all(ok for _n, ok in verdicts)


# ---------------------------------------------------------------------------
# Cell driver
# ---------------------------------------------------------------------------
def run_cells(args, man, covered_r, dqa_covered, gloss_docs, log):
    mock = args.mock
    dc = man["design_constants_from_frozen_record"]
    frames = man["prompt_frames"]
    plan = man["arm_plan"]
    seeds = man["mock"]["seeds"] if mock else dc["seeds"]
    ks = dc["retry_sweep"]

    if mock:
        mk = man["mock"]
        items = covered_r[:mk["n_covered_items"]]
        # external stand-in (SYNTHETIC, labelled as such): a disjoint slice of
        # fresh covered items so the FIXED ext pipeline (incl. verification)
        # is exercised end-to-end in mock
        external = [dict(it, id="mock-ext:" + it["id"])
                    for it in covered_r[mk["n_covered_items"]:
                                        mk["n_covered_items"] + mk["n_external_items"]]]
        iface_n = mk["iface_n_labelled"]
    else:
        # advisor right-size: evaluate a fixed pre-registered subset of the
        # pinned-order (by rank) fresh d-qa-r covered items. per_arm_items is a
        # frozen design constant (250); the full corpus stays on disk and keeps
        # its pinned kot-corpus-hash, so no corpus is re-pinned — the subset is
        # a deterministic prefix of the rank-sorted covered set.
        n_use = int(dc["per_arm_items"])
        if len(covered_r) < n_use:
            raise SystemExit("ERR_ITEMS_SHORT: d-qa-r has %d covered items < "
                             "per_arm_items %d" % (len(covered_r), n_use))
        items = covered_r[:n_use]
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
                raise SystemExit("ERR_PIN: %s: %s sha != f2b-manifest pin" % (key, path))
        # d-ext (external slice; descriptive raw vectors via the FIXED pipeline)
        if not os.path.isdir(args.dext_dir or ""):
            raise SystemExit("ERR_MISSING_DEXT: d-ext external eval slice missing "
                             "— refusing a final-phase run")
        for key, rel in (("dextItemsSha256", os.path.join("items", "external.jsonl")),
                         ("dextManifestSha256", "manifest.json")):
            pin = man["pins"].get(key)
            path = os.path.join(args.dext_dir, rel)
            if not pin or sha256_file(path) != pin:
                raise SystemExit("ERR_PIN: %s: %s sha != f2b-manifest pin" % (key, path))
        external = load_jsonl(os.path.join(args.dext_dir, "items", "external.jsonl"))
        external.sort(key=lambda x: x["rank"])
        iface_n = dc["iface_gate"]["n_min_per_rung"]

    verifier = KernelVerifier(args.records_root)
    verifier.index_labels(items)
    # perm spans the FULL covered-concept set (not the per_arm_items subset):
    # the derangement is over concept urns and must cover every urn any arm
    # (incl. the external-slice pipeline) may query; index_labels(items) below
    # restricts which items are actually SCORED to the right-sized subset.
    shuf = ShuffledKernelVerifier(args.records_root, covered_r,
                                  man["shuffle"]["perm_seed"])
    shuf.index_labels(items)
    # record the seed-pinned permutation next to the results (advisor: recorded)
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
    store_bytes_gloss = os.path.getsize(os.path.join(args.dqa_dir,
                                                     "gloss-corpus.jsonl"))
    # store = UNIQUE canonical record bytes (fixes F2's per-item double count)
    store_bytes_records = sum(
        os.path.getsize(os.path.join(args.records_root, p))
        for p in sorted({it["record_path"] for it in items
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

    # ---- per-cell safety driver (correction 1) -------------------------------
    # One emitted record == one cell == one CellGuard. On a safety breach the
    # cell's coordinates + breach data are FLUSHED as an exit:"timeout" record
    # (verdict-gen excludes exit!="ok" from eligible records, so the run fails
    # closed — INCOMPLETE-DATA at analysis — instead of hanging or fabricating
    # anything), then the run aborts in bounded time with partials on disk.
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

    # FIXED ext_vector (closes the F2 instrument defect): the external slice
    # runs through the arm's OWN pipeline, never through a run_alone bypass.
    # The caller's CellGuard covers this work too — it is part of the cell.
    def ext_vector(lm, seed, guard, pipeline="alone", ver=None, k=0):
        if external is None:
            return None
        meter_ext = new_meter()
        if pipeline == "alone":
            return run_alone(lm, frames, external, seed, meter_ext, guard)
        if pipeline == "verify":
            vec, _xf = run_verify_retry(lm, frames, external, ver, k, seed,
                                        meter_ext, guard)
            return vec
        if pipeline == "text":
            return run_alone(lm, frames, external, seed, meter_ext, guard,
                             context_fn=lambda it: [gloss_by_urn[it["urn"]]]
                             if it.get("urn") in gloss_by_urn else None)
        raise SystemExit("ERR_EXT_PIPELINE: %r" % pipeline)

    # ---- model-alone at R1 and R3 (per seed for pairing) --------------------
    for rung in ("R1", "R3"):
        lm = lm_for(rung)
        for seed in seeds:
            def cell(guard, lm=lm, seed=seed):
                meter = new_meter()
                cov = run_alone(lm, frames, items, seed, meter, guard)
                return cell_metrics(cov, meter, [lm], 0,
                                    external=ext_vector(lm, seed, guard))
            run_cell(ARM_ALONE, rung, 0, seed, cell)

    lm1 = lm_for("R1")

    # ---- kernel-verify-retry (true records) and shuffled control ------------
    for arm, ver in ((ARM_VERIFY, verifier), (ARM_SHUF, shuf)):
        for k in ks:
            for seed in seeds:
                def cell(guard, arm=arm, ver=ver, k=k, seed=seed):
                    meter = new_meter()
                    cov, _xf = run_verify_retry(lm1, frames, items, ver, k,
                                                seed, meter, guard)
                    m = cell_metrics(cov, meter, [lm1], store_bytes_records,
                                     external=ext_vector(lm1, seed, guard,
                                                         pipeline="verify",
                                                         ver=ver, k=k))
                    if arm == ARM_SHUF:
                        m["shuffle_permutation_sha256"] = shuf.perm_sha256
                        m["shuffle_perm_seed"] = shuf.perm_seed
                    return m
                run_cell(arm, "R1", k, seed, cell)

    # ---- gold-oracle-retry: DROPPED (advisor right-size 2026-07-09) ----------
    # The diagnostic retry ceiling is cut from the right-sized arm set (it reads
    # the answer key, is NON-DEPLOYABLE, and never bore any PASS/kill). The
    # pinned analysis handles its absence: gold fields resolve to null and are
    # never referenced by any verdict rule. run_gold_oracle_retry() is retained
    # in this module (unused) for provenance with the superseded design.

    # ---- kernel-as-text (greedy, deterministic -> one cell) -----------------
    def cell_text(guard):
        meter = new_meter()
        cov = run_alone(lm1, frames, items, seeds[0], meter, guard,
                        context_fn=lambda it: [gloss_by_urn[it["urn"]]]
                        if it["urn"] in gloss_by_urn else None)
        return cell_metrics(cov, meter, [lm1], store_bytes_gloss,
                            external=ext_vector(lm1, seeds[0], guard,
                                                pipeline="text"))
    run_cell(ARM_TEXT, "R1", 0, seeds[0], cell_text)

    # ---- gloss-self-verify-retry (P7 RT-2 arm 10) ----------------------------
    for k in ks:
        for seed in seeds:
            def cell(guard, k=k, seed=seed):
                meter = new_meter()
                cov = run_self_verify_retry(lm1, frames, items, gloss_by_urn,
                                            k, seed, meter, guard)
                return cell_metrics(cov, meter, [lm1], store_bytes_gloss)
            run_cell(ARM_SELFV, "R1", k, seed, cell)

    # ---- prm-verifier (HC3) --------------------------------------------------
    if mock:
        prm = StubPRM(man["mock"])
    else:
        spec = man["models"]["prm"]
        if not spec.get("repo") or not spec.get("revision"):
            raise SystemExit("ERR_UNPINNED_MODEL: prm repo/revision missing")
        prm = HFPRM(spec["repo"], spec["revision"], args.device, frames)
    for seed in seeds:
        def cell(guard, seed=seed):
            meter = new_meter()
            cov = run_prm(lm1, prm, frames, items, plan["prm_best_of_n"],
                          seed, meter, guard)
            return cell_metrics(cov, meter, [lm1, prm], 0)
        run_cell(ARM_PRM, "R1", 0, seed, cell)

    # ---- P10 extraction-instrument gate (R1 — the only verifier host rung) --
    def cell_iface(guard):
        if mock:
            return run_extraction_instrument_mock(lm1, frames, items,
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
    ap.add_argument("--dqa-dir", default=os.path.join(root3, "data", "d-qa"))
    ap.add_argument("--dqar-dir", default=os.path.join(root3, "data", "d-qa-r"))
    ap.add_argument("--records-root", default=root3,
                    help="root that item record_path fields resolve against")
    ap.add_argument("--dxif-dir", default=None,
                    help="d-xif labelled extraction set (REQUIRED for real runs)")
    ap.add_argument("--dext-dir", default=None,
                    help="d-ext external eval slice (REQUIRED for real runs)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--gpu-class", default="A10G", choices=["T4", "A10G", "A100"])
    ap.add_argument("--mock", action="store_true",
                    help="stub-LM mechanics check on CPU; $0; labelled MOCK")
    ap.add_argument("--dry-plan", action="store_true",
                    help="print the real-run cost plan vs caps; runs nothing")
    ap.add_argument("--max-hours", type=float, default=60.0)
    ap.add_argument("--cell-timeout-s", type=float, default=None,
                    help="per-cell wall-clock safety bound (correction 1); "
                         "default %s s by --gpu-class"
                         % sorted(CELL_TIMEOUT_S_DEFAULT.items()))
    ap.add_argument("--max-gen-per-item", type=int,
                    default=MAX_GEN_PER_ITEM_DEFAULT,
                    help="per-item generation cap within one cell "
                         "(correction 1; structural max is 10, gloss-self-"
                         "verify at k=4)")
    args = ap.parse_args()
    if args.cell_timeout_s is None:
        args.cell_timeout_s = CELL_TIMEOUT_S_DEFAULT[args.gpu_class]
    t0 = time.time()

    man, covered_r, dqa_covered, gloss_docs = load_inputs(
        args.inputs_dir, args.dqa_dir, args.dqar_dir)

    if args.dry_plan:
        ok = dry_plan(man, covered_r, args.gpu_class)
        sys.exit(0 if ok else 2)

    os.makedirs(args.out_dir, exist_ok=True)

    def log(msg):
        print("[f2b %7.1fs] %s" % (time.time() - t0, msg), flush=True)

    label = "MOCK" if args.mock else "FULL"
    log("mode=%s device=%s items=%d fresh covered (d-qa-r)"
        % (label, args.device, len(covered_r)))
    if not args.mock and args.device != "cuda":
        log("WARNING: real run requested on CPU — allowed but slow")

    emit = run_cells(args, man, covered_r, dqa_covered, gloss_docs, log)
    records_path = emit.write()

    hours = (time.time() - t0) / 3600.0
    if hours > args.max_hours:
        raise SystemExit("ERR_TIME_BUDGET: exceeded %.1fh" % args.max_hours)

    suffix = "-mock" if args.mock else ""
    results = {
        "experiment": "f2b-replicate",
        "outcome": ("MOCK-HARNESS-COMPLETE" if args.mock else "HARNESS-COMPLETE"),
        "outcome_note": "NOT a hypothesis verdict — raw run-records only; the "
                        "verdict is computed by the pinned "
                        "analysis/f2b_replicate.py + tools/registry/"
                        "verdict-gen.py under run-vs-audit separation",
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
        "shuffle": {"perm_seed": man["shuffle"]["perm_seed"],
                    "map_file": "shuffle-map.json"},
        "wallClockHours": hours,
    }
    with open(os.path.join(args.out_dir, "results-f2b%s.json" % suffix), "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    log("OUTCOME: %s (%d run-record bodies in %s)"
        % (results["outcome"], len(emit.records), records_path))


if __name__ == "__main__":
    main()
