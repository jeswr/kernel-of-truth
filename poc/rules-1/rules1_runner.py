#!/usr/bin/env python3
"""RULES-1-B GPU-arm runner (DRAFT registry/experiments/rules-1-b.json,
superseding rules-1 frozen_sha256 0ef03ee1... after the 2026-07-12 maintainer
VOID of its GPU run — degenerate host instrument; post-mortem
docs/next/analysis/rules1-void-degenerate-instrument.md. Fixes over the
rules-1 harness: direction-explicit answer cue (render_answer_cue — the root
cause), cue-aligned ground-(iii) feedback wording, and a mandatory real-model
CPU pilot mode (--pilot-n). Prereg doc docs/next/arch/world-model-rules-engine.md
§4 as amended by the cross-model synthesis; maintainer approvals MD-1..MD-9,
issue #19).

WHAT THIS RUNNER MEASURES (raw rows only — verdicts belong to the pinned
analysis/rules_1.py + verdict-gen under run-vs-audit separation): does the
deterministic proof-carrying rules engine at the prompt-time temporary-world
memory slot lift a frozen small host on ENTAILED-but-never-stated kinship
facts, on the nsk1-clutrr eval (858 covered two-hop items, third-party CLUTRR
gold predating the kernel; 100 control items scored on fail-closed refusal)?

ARMS (frozen design levels; the coordinator-scoped host-lift set + c1):
  A1  model-alone (R1, SmolLM2-135M): stated facts + neutral token-matching
      padding to the A2-shaped injection count (PROPOSED-ASM-1127) — inert
      floor and headroom gate.
  A3  engine-injected verify-retry (R1, k=4) — THE model-level claim carrier
      and GPU primary (PROPOSED-ASM-1128/1132/1161): the model answers from
      stated facts alone; the twin engine issues LICENSED rejections against
      Cl(S) with proof, injected at the memory slot on retry; final answer =
      last attempt. Retry topology + forced-choice scorer + seeded resampler
      REUSED BYTE-IDENTICAL from poc/f2b-transfer/runner/f2bt_runner.py
      (HFLM._option_logprobs / HFLM.choose, SEED_BASE 20260710, CellGuard);
      poc/f2b, poc/f2b-transfer and poc/deconf-b trees are NOT modified.
  A5  R3-alone (SmolLM2-1.7B): efficiency comparator (s3 noninferiority).
  A7  direct executor: the twin engine answers from Cl(S) with proof; the LM
      only renders (forced choice over the same surface with the derivation
      injected) — the attribution-clean systems arm (PROPOSED-ASM-1161).
  c1  shuffled-rules control: Sattolo-deranged axiom set at identical
      topology and token cost (PROPOSED-ASM-1129) — identical A3 loop, the
      verifier consults the deranged TBox. The one control NOT to cut: the
      frozen verdict_rules need s1 for any PASS.
      DISCLOSED PROPERTY (measured at build over all 858 covered items and a
      16-seed Sattolo sweep): EVERY derangement of this tightly-typed
      6-property module makes the fail-closed engine refuse on every covered
      item (ERR_CONFLICT / ERR_INSUFFICIENT_PREMISES) — deranged rules
      cannot license rejections, so the c1 oracle abstains and the lift
      channel is absent by construction. This is recorded, not hidden: the
      results JSON carries an engine_outcome_ledger for BOTH TBoxes so the
      analyst/auditor reads c1's engine engagement directly.

CELLS: entailed = the 858 covered items; control = the 100 uncovered items
(engine must refuse with a named ERR_* — E5 stratum; emitted for the
engine-bearing arms A3/A7, the two arms the pinned analysis reads). Stated
sanity cells are carried by the pinned CPU certificate (C_dec stated = 1.0),
not re-spent here.

ROW SHAPE (exactly what analysis/rules_1.py consumes): {item_id, arm, rung,
seed, cell, item_correct_ext, refused, attempts, tokens_in, tokens_out,
engine_us, flops_formula}.

GOLD-LEAK GUARD: no A3/c1 rejection feedback may contain the item's gold
surface word as a token — asserted fail-closed (ERR_GOLD_LEAK) on every
feedback line before it reaches a prompt (nsk1 S9-4 discipline).

FAIL-CLOSED PINS (mock included): kot-corpus-hash/1 on nsk1-clutrr +
axioms-v0 + axioms-kinship-v1; sha pins on twin_engine.py, certificate.py,
certificate-result.json (which must carry success_asm_1131=true AND
gates_asm_1163_all_pass=true AND kill_a_fired=false — the pinned PASSED
precondition; anything else refuses ERR_CERT_PRECONDITION and spends no GPU)
and the reused f2bt_runner.py bytes. ERR_* codes, no silent fallbacks.

Usage:
  python3 rules1_runner.py --out-dir /tmp/rules1 --mock         # stub LM, CPU, $0
  python3 rules1_runner.py --out-dir /tmp/rules1 --dry-plan     # cost plan vs caps
  python3 rules1_runner.py --out-dir /tmp/rules1 --device cuda  # real (Modal only)

HARD RULES: --mock and --dry-plan spend $0, never touch a GPU or the network;
mock numbers are labelled MOCK end-to-end and are never measurements; this
module states NO feasibility conclusion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
for p in (_HERE, os.path.join(_ROOT, "poc"),
          os.path.join(_ROOT, "poc", "f2b-transfer", "runner")):
    if p not in sys.path:
        sys.path.insert(0, p)

# REUSE, byte-identical (pins verified in load_inputs before any cell runs):
#   twin_engine.py — the FROZEN engine (artifact_hashes pin 399fcd8d...)
#   certificate.py — the pinned certificate module: world loading, item-scoped
#                    UNA (PROPOSED-ASM-1120) and the pinned TBox list
#   f2bt_runner.py — HFLM forced-choice scorer + seeded retry sampler +
#                    CellGuard/CellBudgetExceeded + hashing helpers (the
#                    f2b-transfer FULL-run harness bytes; SEED_BASE 20260710)
from twin_engine import Closure, EngineError, TBox  # noqa: E402
import certificate as cert_mod  # noqa: E402
from f2bt_runner import (  # noqa: E402
    CellBudgetExceeded, CellGuard, HFLM, corpus_kot_hash, det_u, load_jsonl,
    sha256_file, utcnow,
)

ARM_A1, ARM_A3, ARM_A5, ARM_A7, ARM_C1 = "A1", "A3", "A5", "A7", "c1"
RUNG_OF = {ARM_A1: "R1", ARM_A3: "R1", ARM_A7: "R1", ARM_C1: "R1",
           ARM_A5: "R3"}
REFUSAL_TOKEN = "<REFUSED>"

# class-concept URNs (data/axioms-v0/class-man.json + its range partners;
# same constants the pinned certificate uses)
MAN = "urn:kot:bciqkttqo6lnzwz7u72dbbpteqryr76cdyj7glivilcqribbggeqofsy"
WOMAN = "urn:kot:bciqbz6th7ul3gmk5bhtovyi2yifyv7twotuvwjcebgetthcs532sgoq"

CELL_TIMEOUT_S_DEFAULT = {"A100": 3600.0, "A10G": 3600.0, "T4": 9000.0}
MAX_GEN_PER_ITEM_DEFAULT = 8  # structural max is k+1=5 (A3/c1); 8 trips only on a defect


class Rules1HFLM(HFLM):
    """f2bt HFLM with ONLY the load dtype overridden to fp32 (frozen
    runner_constraints.hardware: 'single A10G (Modal), fp32, greedy').
    _option_logprobs / choose / count_tokens are inherited unchanged, so the
    forced-choice scorer and the seeded retry sampler are the reused bytes.
    dtype is overridable ONLY under --pilot-n (CPU instrument pilot: 1.7B
    fp32 does not fit a 7 GB box; the pilot validates the PROMPT FRAME, not
    the arithmetic — dtype is disclosed in the results JSON)."""

    def __init__(self, repo, revision, device, dtype="fp32"):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        if not revision:
            raise SystemExit("ERR_UNPINNED_MODEL: %s has no pinned revision" % repo)
        self.tok = AutoTokenizer.from_pretrained(repo, revision=revision)
        self.model = AutoModelForCausalLM.from_pretrained(
            repo, revision=revision,
            torch_dtype={"fp32": torch.float32,
                         "bf16": torch.bfloat16}[dtype])  # fp32 per frozen record
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
        self.weight_bytes = int(self.n_active * 4)


class StubRulesLM:
    """SYNTHETIC mechanics-only stand-in (mock mode; no torch). Deterministic
    function of (rung, item, seed, attempt) via sha256 (f2bt det_u reuse).
    The planted skill gradient exists ONLY so the pinned analysis gates
    (headroom/separation/engagement) resolve during mock validation. The
    injection/feedback bonuses make the stub SENSITIVE to the real prompt
    blocks, so A7 injection and A3 feedback measurably change mock outputs.
    Never a measurement."""

    def __init__(self, rung, spec):
        self.rung = rung
        self.skill = spec["stub_skill"][rung]
        self.inj_bonus = spec["stub_injection_bonus"]
        self.fb_bonus = spec["stub_feedback_bonus"]
        self.name = "stub-%s" % rung
        self.n_active = {"R1": 135_000_000, "R3": 1_700_000_000}[rung]

    def count_tokens(self, text):
        return max(1, len(text.split()))

    def choose(self, item, keys, gold, seed, attempt, has_context=False,
               prompt=""):
        p = self.skill
        if "Verified derivations" in prompt:
            p += self.inj_bonus
        if "Verifier feedback" in prompt:
            p += self.fb_bonus * min(attempt, 2)
        p = min(0.98, p)
        u = det_u("r1ans", self.name, item["id"], seed, attempt)
        if u < p and gold in keys:
            return gold, 1.0
        wrong = [k for k in keys if k != gold]
        i = int(det_u("r1wr", self.name, item["id"], seed, attempt)
                * len(wrong))
        return wrong[i], 0.5


# ---------------------------------------------------------------------------
# Engine side: closures, licensed answers/refusals, proof + feedback rendering
# ---------------------------------------------------------------------------
def load_tbox_records(paths):
    """Load the pinned axiom records as (name, record) pairs (files or dirs;
    manifest.json excluded) — the raw material for both the true TBox and the
    c1 derangement."""
    from pathlib import Path
    out = []
    for d in paths:
        d = Path(d)
        files = ([p for p in sorted(d.glob("*.json"))
                  if p.name != "manifest.json"] if d.is_dir() else [d])
        for p in files:
            out.append((str(p), json.loads(p.read_text())))
    return out


def build_tbox(records):
    tbox = TBox()
    for ref, rec in records:
        tbox.load_record(rec, ref)
    return tbox


def sattolo_derange_subjects(records, prop_urns, perm_seed):
    """c1 (PROPOSED-ASM-1129): Sattolo cyclic derangement over the kinship
    PROPERTY-record subject URNs — every property record's constraint body is
    re-hung on a DIFFERENT property subject. Identical record count,
    constraint shapes and token cost; rule content decoupled from the
    relation each record defines. Class records untouched."""
    import random
    urns = sorted(prop_urns)
    if len(urns) < 2:
        raise SystemExit("ERR_SHUFFLE: need >=2 property URNs to derange")
    shuffled = list(urns)
    rng = random.Random(perm_seed)
    for i in range(len(shuffled) - 1, 0, -1):
        j = rng.randrange(i)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    perm = dict(zip(urns, shuffled))
    if any(a == b for a, b in perm.items()):
        raise SystemExit("ERR_SHUFFLE: fixed point in permutation (bug)")
    deranged = []
    for ref, rec in records:
        rec2 = json.loads(json.dumps(rec))  # deep copy
        if rec2["subject"] in perm:
            rec2["subject"] = perm[rec2["subject"]]
        deranged.append((ref + "#deranged", rec2))
    blob = json.dumps(perm, sort_keys=True, separators=(",", ":")).encode()
    return deranged, perm, hashlib.sha256(blob).hexdigest()


def query_pair(item):
    """(a, b) URNs of the eval query, per the pinned certificate logic."""
    if item["hop1"]:
        a = item["hop1"]["subject"]
        b = [u for u in item["lexicon"]
             if u not in (a, item["hop1_bridge"])][0]
        return a, b
    q = item["question"]
    name_a, name_b = q[len("How is "):-1].split(" related to ")
    n2u = {v: k for k, v in item["lexicon"].items()}
    return n2u[name_a], n2u[name_b]


def verbalise_fact(f, names, urn2word):
    if f[0] == "rel":
        w = urn2word.get(f[2], "related-to")
        return "%s is %s's %s" % (names.get(f[3], f[3]),
                                  names.get(f[1], f[1]), w)
    if f[0] == "cls":
        cw = {MAN: "man", WOMAN: "woman"}.get(f[2], "person")
        return "%s is a %s" % (names.get(f[1], f[1]), cw)
    return "%s and %s are different people" % (names.get(f[1], f[1]),
                                               names.get(f[2], f[2]))


def render_proof(why, names, urn2word):
    """One-line proof from the twin's why() tree (regime-tagged rules named;
    stated leaves verbalised) — the A2-shaped canonical rendering the A7
    injection and the A1 padding count use."""
    if why.get("stated"):
        return verbalise_fact(tuple(why["fact"]), names, urn2word) + " (stated)"
    prem = "; ".join(render_proof(p, names, urn2word)
                     for p in why["premises"])
    return "%s [%s/%s from: %s]" % (
        verbalise_fact(tuple(why["fact"]), names, urn2word),
        why["rule"], why["regime"], prem)


class EnginePayload:
    """Per-item engine result against ONE TBox: licensed answer + proof, or a
    named refusal; plus the closure (for licensed rejection rendering)."""

    __slots__ = ("answer", "why", "refusal", "closure", "engine_us")

    def __init__(self, tbox, stated, a, b, vocab):
        t0 = time.perf_counter()
        self.closure = None
        self.answer = self.why = self.refusal = None
        try:
            cl = Closure(tbox, stated)
            self.closure = cl
            self.answer, self.why = cl.query_relation(a, b, vocab)
        except EngineError as e:
            self.refusal = e.code
        self.engine_us = (time.perf_counter() - t0) * 1e6


GOLD_LEAK_RE = re.compile(r"[a-z-]+")


def assert_no_gold_leak(text, gold_word, where):
    """nsk1 S9-4 discipline made structural: the gold surface word must never
    appear as a token of any A3/c1 feedback line. Fail closed."""
    if gold_word and gold_word.lower() in GOLD_LEAK_RE.findall(text.lower()):
        raise SystemExit("ERR_GOLD_LEAK: gold token %r in %s feedback: %r"
                         % (gold_word, where, text))


def licensed_rejection(payload, tbox, stated_set, a, b, word, vocab,
                       names, urn2word, gold_word):
    """The A3 rejection line for a proposed answer `word` (prereg §4.3 A3:
    'the engine issues a licensed rejection with its proof'). Three licensed
    grounds, checked in order; the returned line NEVER contains the gold
    token (asserted).

    Returns None when the proposal equals the engine's licensed answer
    (accept) or when the engine cannot decide (abstain — no free rejections).
    """
    if payload.refusal is not None:
        return None  # engine undecidable here -> verifier abstains
    if word == payload.answer:
        return None  # accept
    # Leak guard scope: feedback may quote the model's OWN proposal (already
    # known to the model) but must never INTRODUCE the gold token — so the
    # check is skipped only when the proposal itself is the gold word (a c1
    # deranged-verifier case; the true verifier accepts gold on covered).
    if word == gold_word:
        gold_word = None
    cl = payload.closure
    urn_w = vocab.get(word)
    an, bn = names.get(a, a), names.get(b, b)
    line = None
    if urn_w is not None:
        # (i) functional refutation: a's only <word> is x != b (UNA)
        if urn_w in tbox.functional:
            others = sorted({f[3] for f in cl.facts()
                             if f[0] == "rel" and f[1] == a
                             and f[2] == urn_w and f[3] != b})
            if others:
                x = names.get(others[0], others[0])
                line = ("'%s' is rejected: %s is %s's %s; %s and %s are "
                        "different people; a person has exactly one %s "
                        "(functional, by the definition of '%s')"
                        % (word, x, an, word, x, bn, word, word))
        # (ii) range refutation: b's stated gender conflicts with range(word)
        if line is None and urn_w in tbox.range:
            rng_cls, _ = tbox.range[urn_w]
            b_classes = {f[2] for f in stated_set
                         if f[0] == "cls" and f[1] == b}
            for c1, c2, _ref in tbox.disjoint:
                if (rng_cls == c1 and c2 in b_classes) or \
                        (rng_cls == c2 and c1 in b_classes):
                    have = "man" if MAN in b_classes else "woman"
                    need = "man" if rng_cls == MAN else "woman"
                    line = ("'%s' is rejected: %s is a %s, but someone's %s "
                            "must be a %s (by the definition of '%s')"
                            % (word, bn, have, word, need, word))
                    break
    if line is None:
        # (iii) not licensed: no derivation yields this word for (a, b).
        # Wording matches the direction-explicit answer cue ('{b} is {a}'s
        # <word>') so feedback and cue never disagree about direction.
        line = ("'%s' is rejected: no derivation from the stated facts "
                "licenses '%s is %s's %s'" % (word, bn, an, word))
    assert_no_gold_leak(line, gold_word, "A3/c1")
    return line


# ---------------------------------------------------------------------------
# Prompt construction — one shared affordance; arms differ only in blocks
# ---------------------------------------------------------------------------
def stated_lines(stated, names, urn2word):
    rels = [f for f in stated if f[0] == "rel"]
    clss = [f for f in stated if f[0] == "cls"]
    return ([verbalise_fact(f, names, urn2word) + "." for f in rels] +
            [verbalise_fact(f, names, urn2word) + "." for f in clss])


def render_answer_cue(frames, pair_names):
    """RULES-1-B FIX (root cause of the rules-1 void; post-mortem
    docs/next/analysis/rules1-void-degenerate-instrument.md): the CLUTRR gold
    convention for 'How is A related to B?' is the (A, gold, B) triple read
    'A's <gold> is B' — i.e. the gold word names what B IS TO A. The rules-1
    cue '\\nAnswer:' left the direction to the model, whose natural reading
    is the REVERSE (A is B's granddaughter/grandson), so the gold word was
    structurally un-elicitable and every arm scored 0. The cue is now the
    direction-explicit infill '\\nAnswer: {b_name} is {a_name}'s' — the exact
    surface of the engine's own derivation rendering ('Jason is Jennifer's
    grandfather'), identical for every arm (shared affordance preserved)."""
    if pair_names is None:
        raise SystemExit("ERR_FRAME: answer cue requires the item's (a, b) "
                         "surface names — no direction-ambiguous fallback")
    a_name, b_name = pair_names
    return frames["answer_cue"].format(a_name=a_name, b_name=b_name)


def build_prompt(frames, item, stated, names, urn2word, menu,
                 derived_lines=None, feedback_lines=None, pad_to_tokens=None,
                 lm=None, pair_names=None):
    # RULES-1-B FIX 2 (PROPOSED-ASM-1630, see also render_answer_cue): the
    # 23-word menu is rendered INSIDE the task header, not as a line adjacent
    # to the answer cue — measured on R1: a menu line immediately before the
    # cue swamps the small host's next-token distribution with menu-prior
    # words (gold drops from top-1 to rank ~9 even with the derivation
    # injected). The closed-vocabulary constraint itself is enforced by the
    # per-option logprob scorer, not by prompt text.
    parts = [frames["task_prefix"].format(menu=", ".join(menu))]
    for line in stated_lines(stated, names, urn2word):
        parts.append(frames["fact_line"].format(line=line))
    parts.append(frames["una_line"])
    if derived_lines:
        parts.append("\n" + frames["derived_prefix"])
        for line in derived_lines:
            parts.append(frames["derived_line"].format(line=line))
    if feedback_lines:
        parts.append("\n" + frames["feedback_prefix"])
        for line in feedback_lines:
            parts.append(frames["feedback_line"].format(line=line))
    parts.append(frames["question_prefix"] + item["question"])
    base = "".join(parts)
    cue = render_answer_cue(frames, pair_names)
    if pad_to_tokens is not None and lm is not None:
        # PROPOSED-ASM-1127: neutral token-matching padding, counted with the
        # arm's own tokenizer, appended before the answer cue.
        pad_sent = " " + frames["padding_sentence"]
        cur = lm.count_tokens(base + cue)
        block = ""
        while cur + lm.count_tokens(block + pad_sent) <= pad_to_tokens:
            block += pad_sent
        if block:
            base += "\n" + block.strip()
    return base + cue


def a2_shaped_injection(payload, names, urn2word):
    """The A2 canonical verbalisation (derived facts + one-line proofs) — the
    token-count target for A1/A5 padding (ASM-1127) and the A7 injection."""
    if payload.answer is None:
        return []
    return [render_proof(payload.why, names, urn2word) + "."]


# ---------------------------------------------------------------------------
# Row emission
# ---------------------------------------------------------------------------
class RowEmitter:
    def __init__(self, out_dir, suffix):
        self.rows = []
        self.path = os.path.join(
            out_dir, "run-records-rules1%s.jsonl" % suffix)
        with open(self.path, "w"):
            pass

    def emit(self, **row):
        self.rows.append(row)
        with open(self.path, "a") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())


def flops_formula(lm, tokens_scored):
    # F0 §3.3 first term (2*N_active*T); attention term omitted uniformly —
    # a DESCRIPTIVE ledger field, identical formula across arms.
    return 2.0 * float(lm.n_active) * float(tokens_scored)


# ---------------------------------------------------------------------------
# Arm drivers
# ---------------------------------------------------------------------------
def choose_word(lm, item, menu, gold, seed, attempt, prompt, guard):
    it = {"id": item["item_id"]}
    guard.gen()
    t0 = time.perf_counter()
    ans, _conf = lm.choose(it, menu, gold, seed, attempt, prompt=prompt)
    lat = time.perf_counter() - t0
    t_prompt = lm.count_tokens(prompt)
    t_opts = sum(lm.count_tokens(" %s" % w) for w in menu)
    return ans, lat, t_prompt * len(menu) + t_opts, t_prompt


def run_alone_cell(lm, rung, arm, frames, items, ctx, seed, emitter, guard):
    """A1 / A5: stated facts + neutral padding to the A2-shaped count."""
    for item in items:
        iid = item["item_id"]
        guard.start_item({"id": iid})
        pay = ctx["payload_true"][iid]
        names, stated = ctx["names"][iid], ctx["stated"][iid]
        a, b = ctx["pair"][iid]
        pn = (names.get(a, a), names.get(b, b))
        inj = a2_shaped_injection(pay, names, ctx["urn2word"])
        target = lm.count_tokens(build_prompt(
            frames, item, stated, names, ctx["urn2word"], ctx["menu"],
            derived_lines=inj, pair_names=pn))
        prompt = build_prompt(frames, item, stated, names, ctx["urn2word"],
                              ctx["menu"], pad_to_tokens=target, lm=lm,
                              pair_names=pn)
        ans, _lat, toks, t_in = choose_word(lm, item, ctx["menu"],
                                            item["gold_relation"], seed, 0,
                                            prompt, guard)
        emitter.emit(item_id=iid, arm=arm, rung=rung, seed=seed,
                     cell="entailed",
                     item_correct_ext=int(ans == item["gold_relation"]),
                     refused=0, attempts=1, tokens_in=t_in, tokens_out=1,
                     flops_formula=flops_formula(lm, toks))


def run_verify_retry_cell(lm, arm, frames, items, ctx, payloads, tbox, k,
                          seed, emitter, guard):
    """A3 (true TBox) and c1 (deranged TBox): identical loop; the arms differ
    ONLY in the payload/tbox consulted (f2bt run_verify_retry discipline:
    the true and shuffled arms share one code path)."""
    for item in items:
        iid = item["item_id"]
        guard.start_item({"id": iid})
        pay = payloads[iid]
        names, stated = ctx["names"][iid], ctx["stated"][iid]
        stated_set = set(map(tuple, stated))
        a, b = ctx["pair"][iid]
        gold = item["gold_relation"]
        feedback, toks_total, t_in_last = [], 0, 0
        ans, attempts = None, 0
        pn = (names.get(a, a), names.get(b, b))
        for attempt in range(k + 1):
            prompt = build_prompt(frames, item, stated, names,
                                  ctx["urn2word"], ctx["menu"],
                                  feedback_lines=feedback or None,
                                  pair_names=pn)
            ans, _lat, toks, t_in_last = choose_word(
                lm, item, ctx["menu"], gold, seed, attempt, prompt, guard)
            toks_total += toks
            attempts = attempt + 1
            rej = licensed_rejection(pay, tbox, stated_set, a, b, ans,
                                     ctx["vocab"], names, ctx["urn2word"],
                                     gold)
            if rej is None:
                break  # accepted, or verifier abstains (no free rejections)
            feedback.append(rej)
        emitter.emit(item_id=iid, arm=arm, rung="R1", seed=seed,
                     cell="entailed",
                     item_correct_ext=int(ans == gold), refused=0,
                     attempts=attempts, tokens_in=t_in_last, tokens_out=1,
                     engine_us=pay.engine_us,
                     flops_formula=flops_formula(lm, toks_total))


def run_direct_executor_cell(lm, frames, items, ctx, seed, emitter, guard):
    """A7: the engine answers from Cl(S) with proof; the LM only renders (the
    derivation + proof is injected; forced choice over the same surface)."""
    for item in items:
        iid = item["item_id"]
        guard.start_item({"id": iid})
        pay = ctx["payload_true"][iid]
        names, stated = ctx["names"][iid], ctx["stated"][iid]
        if pay.answer is None:
            emitter.emit(item_id=iid, arm=ARM_A7, rung="R1", seed=seed,
                         cell="entailed", item_correct_ext=0, refused=1,
                         attempts=0, tokens_in=0, tokens_out=0,
                         engine_us=pay.engine_us, flops_formula=0.0,
                         refusal_code=pay.refusal)
            continue
        a, b = ctx["pair"][iid]
        pn = (names.get(a, a), names.get(b, b))
        inj = a2_shaped_injection(pay, names, ctx["urn2word"])
        prompt = build_prompt(frames, item, stated, names, ctx["urn2word"],
                              ctx["menu"], derived_lines=inj, pair_names=pn)
        ans, _lat, toks, t_in = choose_word(lm, item, ctx["menu"],
                                            item["gold_relation"], seed, 0,
                                            prompt, guard)
        emitter.emit(item_id=iid, arm=ARM_A7, rung="R1", seed=seed,
                     cell="entailed",
                     item_correct_ext=int(ans == item["gold_relation"]),
                     refused=0, attempts=1, tokens_in=t_in, tokens_out=1,
                     engine_us=pay.engine_us,
                     flops_formula=flops_formula(lm, toks))


def run_control_cells(items_control, ctx, seeds, emitter, arms):
    """E5 refusal stratum for the engine-bearing arms (A3/A7 — the arms the
    pinned analysis reads for refusal_correctness_e5): the engine must draw
    the named fail-closed refusal and the arm abstains. CPU-only — the
    refusal is engine-decided; no generation is fabricated."""
    for item in items_control:
        iid = item["item_id"]
        pay = ctx["payload_true"][iid]
        refused = int(pay.refusal is not None and pay.answer is None)
        for arm in [a for a in (ARM_A3, ARM_A7) if a in arms]:
            for seed in seeds:
                emitter.emit(item_id=iid, arm=arm, rung="R1", seed=seed,
                             cell="control", item_correct_ext=0,
                             refused=refused, attempts=0, tokens_in=0,
                             tokens_out=0, engine_us=pay.engine_us,
                             flops_formula=0.0,
                             refusal_code=pay.refusal or "ERR_NONE_BUG")


# ---------------------------------------------------------------------------
# Inputs + fail-closed pins
# ---------------------------------------------------------------------------
def load_inputs(args):
    with open(os.path.join(args.inputs_dir, "rules1-manifest.json"),
              encoding="utf-8") as f:
        man = json.load(f)
    pins = man["pins"]

    for key, base in (("nsk1ClutrrCorpusKotHash", os.path.join(args.data_root, "nsk1-clutrr")),
                      ("axiomsV0CorpusKotHash", os.path.join(args.data_root, "axioms-v0")),
                      ("axiomsKinshipV1CorpusKotHash", os.path.join(args.data_root, "axioms-kinship-v1"))):
        got = corpus_kot_hash(base)
        if got != pins[key]:
            raise SystemExit("ERR_PIN: %s: %s kot-corpus-hash %s != pin %s"
                             % (key, base, got, pins[key]))
    for key, path in (("twinEnginePySha256", os.path.join(_HERE, "twin_engine.py")),
                      ("certificatePySha256", os.path.join(_HERE, "certificate.py")),
                      ("certificateResultSha256", os.path.join(_HERE, "results", "certificate-result.json")),
                      ("f2btRunnerPySha256", os.path.join(_ROOT, "poc", "f2b-transfer", "runner", "f2bt_runner.py"))):
        if sha256_file(path) != pins[key]:
            raise SystemExit("ERR_PIN: %s: %s sha != rules1-manifest pin"
                             % (key, path))

    # THE PINNED PASSED PRECONDITION (frozen sec-certificate-gate): anything
    # else is INSTRUMENT-INVALID before a cent of GPU is spent.
    with open(os.path.join(_HERE, "results", "certificate-result.json"),
              encoding="utf-8") as f:
        cert = json.load(f)
    cr = cert["certificate_result"]
    if not (cr["success_asm_1131"] and cr["gates_asm_1163_all_pass"]
            and not cr["kill_a_fired"]):
        raise SystemExit("ERR_CERT_PRECONDITION: pinned certificate bytes do "
                         "not carry SUCCESS+gates+no-KILL-a — no GPU spend")
    # the pinned certificate module resolves data/ from ITS OWN path; the
    # --data-root override must agree or the pins above verified other bytes
    cert_data = os.path.realpath(str(cert_mod.ROOT / "data"))
    if os.path.realpath(args.data_root) != cert_data:
        raise SystemExit("ERR_DATA_ROOT: --data-root %s != the pinned "
                         "certificate module's data root %s"
                         % (args.data_root, cert_data))
    return man, cert


def build_context(args, man):
    """CPU precompute: worlds, query pairs, TRUE + DERANGED engine payloads."""
    kin = json.load(open(os.path.join(args.data_root, "axioms-kinship-v1",
                                      "manifest.json")))
    u = kin["minted_urns"]
    vocab = {"mother": cert_mod.MOTHER, "father": cert_mod.FATHER,
             "grandfather": u["grandfather"], "grandmother": u["grandmother"]}
    urn2word = {v: k for k, v in vocab.items()}
    urn2word[u["parent"]] = "parent"
    urn2word[u["grandparent"]] = "grandparent"

    lex = json.load(open(os.path.join(args.data_root, "nsk1-clutrr",
                                      "lexicon.json")))
    menu = list(lex["relations_answer_vocab"])  # the closed 23-word surface

    items = load_jsonl(os.path.join(args.data_root, "nsk1-clutrr",
                                    "items.jsonl"))
    worlds = cert_mod.load_worlds()

    records = load_tbox_records(cert_mod.TBOX_PINNED)
    tbox_true = build_tbox(records)
    prop_urns = [cert_mod.MOTHER, cert_mod.FATHER, u["parent"],
                 u["grandparent"], u["grandfather"], u["grandmother"]]
    deranged_records, perm, perm_sha = sattolo_derange_subjects(
        records, prop_urns, man["shuffle"]["perm_seed"])
    tbox_shuf = build_tbox(deranged_records)

    ctx = {"vocab": vocab, "urn2word": urn2word, "menu": menu,
           "tbox_true": tbox_true, "tbox_shuf": tbox_shuf,
           "perm": perm, "perm_sha": perm_sha,
           "names": {}, "stated": {}, "pair": {},
           "payload_true": {}, "payload_shuf": {}}
    for item in items:
        iid = item["item_id"]
        stated = worlds.get(iid, []) + cert_mod.una(item["lexicon"].keys())
        a, b = query_pair(item)
        ctx["names"][iid] = dict(item["lexicon"])
        ctx["stated"][iid] = stated
        ctx["pair"][iid] = (a, b)
        ctx["payload_true"][iid] = EnginePayload(tbox_true, stated, a, b, vocab)
        try:
            ctx["payload_shuf"][iid] = EnginePayload(tbox_shuf, stated, a, b,
                                                     vocab)
        except SystemExit:
            raise
    return items, ctx


# ---------------------------------------------------------------------------
# --dry-plan (ESTIMATES only; $0)
# ---------------------------------------------------------------------------
def dry_plan(man, items_covered, ctx, gpu):
    plan = man["planning"]
    dc = man["design_constants_from_frozen_record"]
    frames = man["prompt_frames"]
    cpt = plan["chars_per_token_estimate"]
    tput = plan["throughput_tok_per_s"][gpu]
    usd = plan["usd_per_hour"][gpu]
    k = dc["k_retry"]
    seeds = dc["seeds"]
    n_menu = 23

    def est_choose_tokens(item, extra_lines=0):
        iid = item["item_id"]
        names = ctx["names"][iid]
        a, b = ctx["pair"][iid]
        prompt = build_prompt(frames, item, ctx["stated"][iid],
                              names, ctx["urn2word"], ctx["menu"],
                              pair_names=(names.get(a, a), names.get(b, b)))
        return (len(prompt) / cpt + 20 * extra_lines) * n_menu

    tok1 = sum(est_choose_tokens(i) for i in items_covered)
    tok_pad = sum(est_choose_tokens(i, extra_lines=2) for i in items_covered)
    hours = {"R1": 0.0, "R3": 0.0}
    cells = []
    for _s in seeds:
        cells.append(("R1", tok_pad))                       # A1 (padded)
        cells.append(("R3", tok_pad))                       # A5
        cells.append(("R1", tok_pad))                       # A7 (injection)
        cells.append(("R1", tok1 * (k + 1)))                # A3 worst case
        cells.append(("R1", tok1 * (k + 1)))                # c1 worst case
    for rung, toks in cells:
        hours[rung] += toks / tput[rung] / 3600.0
    worst_h = sum(hours.values())
    exp_h = worst_h - (2 * len(seeds) * tok1 * (k + 1 - plan["expected_attempt_factor"])
                       / tput["R1"] / 3600.0)
    cap = dc["budget"]
    lines = [
        "rules-1 --dry-plan (ESTIMATES ONLY — planning constants from "
        "rules1-manifest.json; no GPU, no network, $0 spent by this command)",
        "",
        "eval: %d covered entailed items x %d seeds; arms A1/A3/A5/A7/c1; "
        "k=%d on A3/c1 (worst case k+1 attempts); 23-option forced-choice "
        "surface (per-option scoring, f2bt bytes)"
        % (len(items_covered), len(seeds), k),
        "control cells (E5, A3/A7): CPU-only engine refusals — no GPU cost",
        "",
        "GPU-hours on %s (planning tok/s %s):" % (gpu, tput),
        "  worst case (all retries): R1 %.2f h  R3 %.2f h  total %.2f h"
        % (hours["R1"], hours["R3"], worst_h),
        "  expected (attempt factor %.1f): %.2f h"
        % (plan["expected_attempt_factor"], exp_h),
        "  with %.1fx overhead: worst %.2f h / expected %.2f h"
        % (plan["overhead_factor"], worst_h * plan["overhead_factor"],
           exp_h * plan["overhead_factor"]),
        "",
        "cost at Modal list $%.2f/h (%s):" % (usd, gpu),
        "  expected w/ overhead   $%.2f" % (exp_h * plan["overhead_factor"] * usd),
        "  worst case w/ overhead $%.2f" % (worst_h * plan["overhead_factor"] * usd),
        "",
    ]
    verdicts = [
        ("expected vs registry usd_cap ($%d)" % cap["usd_cap"],
         exp_h * plan["overhead_factor"] * usd <= cap["usd_cap"]),
        ("worst case vs coordinator ceiling ($%d)"
         % cap["coordinator_outer_ceiling_usd"],
         worst_h * plan["overhead_factor"] * usd
         <= cap["coordinator_outer_ceiling_usd"]),
        ("expected hours vs gpu_hours_cap (%d h)" % cap["gpu_hours_cap"],
         exp_h * plan["overhead_factor"] <= cap["gpu_hours_cap"]),
    ]
    for name, ok in verdicts:
        lines.append("  %-46s %s" % (name, "OK" if ok else "OVER — DO NOT LAUNCH"))
    lines.append("")
    lines.append("frozen cost note honoured: c1 (shuffled rules) is the one "
                 "control NOT to cut — inventoried at full item count, k=%d." % k)
    print("\n".join(lines))
    return all(ok for _n, ok in verdicts)


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs-dir", default=os.path.join(_HERE, "inputs"))
    ap.add_argument("--data-root", default=os.path.join(_ROOT, "data"))
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--gpu-class", default="A10G", choices=["T4", "A10G", "A100"])
    ap.add_argument("--arms", default="A1,A3,A5,A7,c1",
                    help="comma-set of arms to run (default: the frozen "
                         "host-lift set + c1)")
    ap.add_argument("--mock", action="store_true",
                    help="stub-LM mechanics check on CPU; $0; labelled MOCK")
    ap.add_argument("--dry-plan", action="store_true",
                    help="print the real-run cost plan vs caps; runs nothing")
    ap.add_argument("--pilot-n", type=int, default=None,
                    help="REAL-model instrument pilot on the first N covered "
                         "items, seed 0 only; labelled PILOT, never a "
                         "measurement or a final-phase row source (the "
                         "host-validity smoke the rules-1 void mandates)")
    ap.add_argument("--pilot-dtype", default="fp32",
                    choices=["fp32", "bf16"],
                    help="model load dtype for --pilot-n ONLY (bf16 lets the "
                         "1.7B A5 pilot fit a CPU box); real runs are fp32 "
                         "per the frozen runner_constraints")
    ap.add_argument("--cell-timeout-s", type=float, default=None)
    ap.add_argument("--max-gen-per-item", type=int,
                    default=MAX_GEN_PER_ITEM_DEFAULT)
    args = ap.parse_args()
    if args.cell_timeout_s is None:
        args.cell_timeout_s = CELL_TIMEOUT_S_DEFAULT[args.gpu_class]
    if args.pilot_n is not None and (args.mock or args.dry_plan):
        raise SystemExit("ERR_PILOT: --pilot-n is a REAL-model instrument "
                         "pilot; it cannot combine with --mock/--dry-plan")
    if args.pilot_dtype != "fp32" and args.pilot_n is None:
        raise SystemExit("ERR_PILOT: --pilot-dtype is pilot-only; real runs "
                         "are fp32 per the frozen runner_constraints")
    t0 = time.time()

    man, cert = load_inputs(args)
    dc = man["design_constants_from_frozen_record"]
    frames = man["prompt_frames"]
    items, ctx = build_context(args, man)
    covered = [i for i in items if i["stratum"] == "covered"]
    control = [i for i in items if i["stratum"] != "covered"]
    if len(covered) != dc["n_covered_entailed"] or \
            len(control) != dc["n_control"]:
        raise SystemExit("ERR_EVAL_COUNTS: %d covered / %d control != frozen "
                         "%d / %d" % (len(covered), len(control),
                                      dc["n_covered_entailed"],
                                      dc["n_control"]))

    if args.dry_plan:
        ok = dry_plan(man, covered, ctx, args.gpu_class)
        sys.exit(0 if ok else 2)

    os.makedirs(args.out_dir, exist_ok=True)

    def log(msg):
        print("[rules1 %7.1fs] %s" % (time.time() - t0, msg), flush=True)

    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    bad = [a for a in arms if a not in RUNG_OF]
    if bad:
        raise SystemExit("ERR_ARMS: unknown arm(s) %s" % bad)

    if args.mock:
        covered = covered[:man["mock"]["n_covered"]]
        control = control[:man["mock"]["n_control"]]
        seeds = man["mock"]["seeds"]
    elif args.pilot_n is not None:
        # PILOT: real models, tiny n, seed 0 only — instrument validation
        # (host-validity smoke) at ~$0 on CPU; NEVER final-phase rows.
        covered = covered[:args.pilot_n]
        control = control[:max(2, args.pilot_n // 4)]
        seeds = [0]
    else:
        seeds = dc["seeds"]

    # record the c1 derangement next to the results (frozen c1: recorded)
    with open(os.path.join(args.out_dir, "shuffle-map-rules1.json"), "w") as f:
        json.dump({"perm_seed": man["shuffle"]["perm_seed"],
                   "algorithm": man["shuffle"]["algorithm"],
                   "map_subject_urn_to": ctx["perm"],
                   "sha256_of_map": ctx["perm_sha"],
                   "derangement_check": "no fixed points (asserted at build)"},
                  f, indent=1, sort_keys=True)
        f.write("\n")
    log("c1 derangement: seed=%d sha=%s"
        % (man["shuffle"]["perm_seed"], ctx["perm_sha"][:12]))

    # engine sanity vs the pinned certificate (fail-closed, CPU): every
    # covered payload must answer, every control payload must refuse.
    n_ans = sum(1 for i in covered
                if ctx["payload_true"][i["item_id"]].answer is not None)
    n_ref = sum(1 for i in control
                if ctx["payload_true"][i["item_id"]].refusal is not None)
    if n_ans != len(covered) or n_ref != len(control):
        raise SystemExit("ERR_ENGINE_SANITY: covered answered %d/%d, control "
                         "refused %d/%d" % (n_ans, len(covered), n_ref,
                                            len(control)))

    def make_lm(rung):
        if args.mock:
            return StubRulesLM(rung, man["mock"])
        spec = man["model_revisions"][rung]
        return Rules1HFLM(spec["repo"], spec["revision"], args.device,
                          dtype=(args.pilot_dtype if args.pilot_n is not None
                                 else "fp32"))

    lms = {}

    def lm_for(rung):
        if rung not in lms:
            log("loading %s host..." % rung)
            lms[rung] = make_lm(rung)
        return lms[rung]

    suffix = ("-mock" if args.mock
              else "-pilot" if args.pilot_n is not None else "")
    emitter = RowEmitter(args.out_dir, suffix)
    k = dc["k_retry"]

    def run_cell(arm, seed, fn):
        guard = CellGuard("%s/seed=%s" % (arm, seed), args.cell_timeout_s,
                          args.max_gen_per_item)
        # CellGuard.start_item expects dict items with an "id" key; drivers
        # pass {"id": item_id} wrappers.
        try:
            fn(guard)
        except CellBudgetExceeded as e:
            # cell="timeout" so the pinned analysis (which reads only the
            # entailed/control cells) can never count this instrument event
            emitter.emit(item_id=str(e.item_id), arm=arm, rung=RUNG_OF[arm],
                         seed=seed, cell="timeout", item_correct_ext=0,
                         refused=0, attempts=0, tokens_in=0, tokens_out=0,
                         flops_formula=0.0, exit="timeout",
                         cell_budget_exceeded={
                             "kind": e.kind, "elapsed_s": round(e.elapsed_s, 1),
                             "n_gen_on_item_at_breach": e.n_gen})
            raise SystemExit("ERR_CELL_TIMEOUT: %s — run aborted in bounded "
                             "time; completed rows flushed in %s"
                             % (e, emitter.path))
        log("cell %s seed=%s done (%.1fs)" % (arm, seed, guard.elapsed()))

    for arm in arms:
        rung = RUNG_OF[arm]
        for seed in seeds:
            if arm in (ARM_A1, ARM_A5):
                lm = lm_for(rung)
                run_cell(arm, seed, lambda g, lm=lm, arm=arm, rung=rung,
                         seed=seed: run_alone_cell(
                             lm, rung, arm, frames, covered, ctx, seed,
                             emitter, g))
            elif arm == ARM_A3:
                lm = lm_for("R1")
                run_cell(arm, seed, lambda g, lm=lm, seed=seed:
                         run_verify_retry_cell(
                             lm, ARM_A3, frames, covered, ctx,
                             ctx["payload_true"], ctx["tbox_true"], k, seed,
                             emitter, g))
            elif arm == ARM_C1:
                lm = lm_for("R1")
                run_cell(arm, seed, lambda g, lm=lm, seed=seed:
                         run_verify_retry_cell(
                             lm, ARM_C1, frames, covered, ctx,
                             ctx["payload_shuf"], ctx["tbox_shuf"], k, seed,
                             emitter, g))
            elif arm == ARM_A7:
                lm = lm_for("R1")
                run_cell(arm, seed, lambda g, lm=lm, seed=seed:
                         run_direct_executor_cell(
                             lm, frames, covered, ctx, seed, emitter, g))

    # E5 control cells (CPU-only, engine-decided refusals) for A3/A7
    if ARM_A3 in arms or ARM_A7 in arms:
        run_control_cells(control, ctx, seeds, emitter, arms)
        log("control cells emitted (E5 refusal stratum, %s x %d seeds)"
            % ("/".join(a for a in (ARM_A3, ARM_A7) if a in arms),
               len(seeds)))

    records_sha = sha256_file(emitter.path)
    # decision-payload sha: rows with the volatile wall-clock field stripped
    # (engine_us is a MEASURED timing and legitimately differs across byte-
    # identical repeats) — THE comparator for the frozen repeat_byte_identical
    # gate (pass two of these to analysis/rules_1.py --repeat-sha-a/-b).
    decision_rows = [{k: v for k, v in r.items() if k != "engine_us"}
                     for r in emitter.rows]
    decision_sha = hashlib.sha256(json.dumps(
        decision_rows, sort_keys=True, separators=(",", ":"))
        .encode()).hexdigest()

    def outcome_ledger(payloads, its):
        from collections import Counter
        c = Counter()
        for i in its:
            p = payloads[i["item_id"]]
            c["answered" if p.answer is not None else p.refusal] += 1
        return dict(sorted(c.items()))

    label = ("MOCK" if args.mock
             else "PILOT" if args.pilot_n is not None else "FULL")
    results = {
        "experiment": "rules-1",
        "outcome": ("MOCK-HARNESS-COMPLETE" if args.mock
                    else "PILOT-HARNESS-COMPLETE" if args.pilot_n is not None
                    else "HARNESS-COMPLETE"),
        "outcome_note": "NOT a hypothesis verdict — raw run-record rows only; "
                        "the verdict is computed by the pinned "
                        "analysis/rules_1.py + tools/registry/verdict-gen.py "
                        "under run-vs-audit separation",
        "mode": label,
        "date": utcnow(),
        "device": args.device,
        "gpu_class_assumed_for_usd": args.gpu_class,
        "arms": arms,
        "seeds": seeds,
        "k_retry": k,
        "n_covered": len(covered),
        "n_control": len(control),
        "n_rows": len(emitter.rows),
        "records_file": os.path.basename(emitter.path),
        "records_sha256": records_sha,
        "decision_sha256": decision_sha,
        "decision_sha_note": "double-run comparator for the frozen "
                             "repeat_byte_identical gate (rows with the "
                             "volatile engine_us timing stripped; pass two "
                             "of THESE to analysis/rules_1.py "
                             "--repeat-sha-a/-b)",
        "engine_outcome_ledger": {
            "true_tbox_covered": outcome_ledger(ctx["payload_true"], covered),
            "true_tbox_control": outcome_ledger(ctx["payload_true"], control),
            "c1_deranged_tbox_covered": outcome_ledger(ctx["payload_shuf"],
                                                       covered),
            "note": "c1 DISCLOSURE (PROPOSED-ASM-1129 operationalisation): "
                    "every Sattolo derangement of this tightly-typed "
                    "6-property module fail-closes the engine on covered "
                    "items, so the c1 oracle licenses no rejections — the "
                    "lift channel is absent by construction, which is the "
                    "content-destruction result s1 measures"},
        "pins": man["pins"],
        "models": ({"note": "MOCK — synthetic stub LM, no models loaded"}
                   if args.mock else {r: man["model_revisions"][r]
                                      for r in ("R1", "R3")}),
        "shuffle": {"perm_seed": man["shuffle"]["perm_seed"],
                    "map_file": "shuffle-map-rules1.json",
                    "map_sha256": ctx["perm_sha"]},
        "certificate_precondition": {
            "sha256": man["pins"]["certificateResultSha256"],
            "success_asm_1131": True, "gates_asm_1163_all_pass": True,
            "kill_a_fired": False},
        "wallClockHours": (time.time() - t0) / 3600.0,
    }
    if args.pilot_n is not None:
        results["pilot"] = {
            "n_covered": len(covered), "n_control": len(control),
            "dtype": args.pilot_dtype,
            "note": "REAL-model instrument pilot (host-validity smoke): "
                    "tiny n, seed 0, CPU-class; numbers validate the "
                    "instrument only and are NEVER measurements or "
                    "final-phase rows"}
    with open(os.path.join(args.out_dir, "results-rules1%s.json" % suffix),
              "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    log("OUTCOME: %s (%d rows in %s, sha %s)"
        % (results["outcome"], len(emitter.rows), emitter.path,
           records_sha[:12]))


if __name__ == "__main__":
    main()
