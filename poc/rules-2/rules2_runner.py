#!/usr/bin/env python3
"""RULES-2 fine-tune + eval runner (DRAFT design registry/experiments/
rules-2.json; design doc docs/next/design/rules-2-train-time.md; build ASM
block PROPOSED-ASM-1440..1459 in poc/rules-2/asm-1440-1459.json).

WHAT THIS RUNNER MEASURES (raw rows only — verdicts belong to the pinned
analysis/rules_2.py + verdict-gen under run-vs-audit separation): does LoRA
fine-tuning a small frozen-family host on the ENGINE-MATERIALISED closure of
the training default world (data/rules2-train, generated $0-CPU by
materialise_closure.py from the PINNED RULES-1 twin engine) internalise the
inference — i.e. lift S-out accuracy (858 fresh-name nsk1-clutrr items,
third-party CLUTRR gold, NO engine anywhere at inference) over the plain
host — with the memorisation split (S-mem/S-held/S-out, ASM-1436) and the c8
train-bytes projection gate (ASM-1427) making lookup unable to fake it?

ARMS (design SS2.3):
  B0   plain host (R1; optionally R2) — RULES-1 A1 prompt format with
       token-matched padding on S-out; floor + headroom gate.
  B1   LoRA on families 1+3 (stated+refusal, NO entailments, size-matched via
       the pinned b1-upsample list) — exposure control (s2', ASM-1425).
  B2   LoRA on families 1+2+3 (stated + MATERIALISED CLOSURE + refusal) —
       THE treatment; internalisation claim attaches to S-out only
       (ASM-1423).
  B3   B2 + one-line proof rendered as a TRAINING-prompt block (rationale
       scaffold; descriptive; MD-R2-4; deviation disclosed in the manifest).
  B4   RULES-1 A3 VERBATIM (frozen R1 host + twin-engine verify-retry k=4 at
       inference) on the identical S-out slice — the gap-closure comparator
       (s3', ASM-1428). Drivers imported BYTE-IDENTICAL from
       poc/rules-1/rules1_runner.py (pin-verified); rules-1 trees unmodified.
  B5   R3 (1.7B) alone on S-out — big-model efficiency comparator.
  c1p  LoRA on the Sattolo-DERANGED closure (pinned c1shuf-map) — content
       control; the lift must collapse (s1', ASM-1426).

EVAL: greedy fp32 forced-choice over the 23-word CLUTRR menu + the named
refusal option (24th; ASM-1431/1446); strata S-out covered/control, S-mem,
S-held, stated-guard, refusal-guard (s4' Herron degradation guard,
ASM-1430); per-arm byte-identical in-process S-out repeat (G4, ASM-1439).
FT seeds {0,1,2}; eval deterministic at attempt 0.

FAIL-CLOSED PINS (mock included): kot-corpus-hash/1 on rules2-train +
nsk1-clutrr + axioms-v0 + axioms-kinship-v1; sha pins on twin_engine.py,
certificate.py, certificate-result.json (+ its SUCCESS flags),
rules1_runner.py (imported bytes), f2bt_runner.py, rules.n3; the c8 gate
artifact must exist, be REAL, sha-match and carry gate_pass=true — anything
else refuses BEFORE a cent of GPU is spent (ERR_PIN / ERR_C8_GATE).

Usage:
  python3 rules2_runner.py --out-dir /tmp/rules2 --mock       # stub LM, CPU, $0
  python3 rules2_runner.py --out-dir /tmp/rules2 --dry-plan   # cost plan vs caps
  python3 rules2_runner.py --out-dir /tmp/rules2 --device cuda  # real (Modal only)

HARD RULES: --mock and --dry-plan spend $0, never touch a GPU or the network;
mock numbers are labelled MOCK end-to-end and are never measurements; this
module states NO feasibility conclusion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
_RULES1 = os.path.join(_ROOT, "poc", "rules-1")
for p in (_HERE, _RULES1, os.path.join(_ROOT, "poc"),
          os.path.join(_ROOT, "poc", "f2b-transfer", "runner")):
    if p not in sys.path:
        sys.path.insert(0, p)

# REUSE, byte-identical (pins verified in load_inputs before any cell runs):
#   twin_engine.py / certificate.py — the FROZEN rules-1 engine + world glue
#   rules1_runner.py — arm drivers (A1 padding, A3 verify-retry, prompt
#                      frames, verbaliser, licensed rejections, gold-leak
#                      guard) for B0/B4/B5
#   f2bt_runner.py   — HFLM forced-choice scorer + CellGuard + helpers
import certificate as cert_mod  # noqa: E402
import rules1_runner as r1  # noqa: E402
from f2bt_runner import (  # noqa: E402
    CellBudgetExceeded, CellGuard, corpus_kot_hash, det_u, load_jsonl,
    sha256_file, utcnow,
)

FT_ARMS = ("B1", "B2", "B3", "c1p")
EVAL_ARMS = ("B0", "B4", "B5")
ALL_ARMS = ("B0", "B1", "B2", "B3", "B4", "B5", "c1p")
RUNG_REPO = {"B5": "R3", "B4": "R1"}  # others take the --rungs plan
CELL_TIMEOUT_S_DEFAULT = {"A100": 5400.0, "A10G": 5400.0, "T4": 10800.0}
MAX_GEN_PER_ITEM = 8


# ---------------------------------------------------------------------------
# Inputs + fail-closed pins
# ---------------------------------------------------------------------------
def load_inputs(args):
    man = json.load(open(os.path.join(args.inputs_dir,
                                      "rules2-manifest.json")))
    pins = man["pins"]
    for key, base in (
            ("rules2TrainCorpusKotHash", args.corpus_dir),
            ("nsk1ClutrrCorpusKotHash",
             os.path.join(args.data_root, "nsk1-clutrr")),
            ("axiomsV0CorpusKotHash",
             os.path.join(args.data_root, "axioms-v0")),
            ("axiomsKinshipV1CorpusKotHash",
             os.path.join(args.data_root, "axioms-kinship-v1"))):
        got = corpus_kot_hash(base)
        if got != pins[key]:
            raise SystemExit("ERR_PIN: %s: %s kot-corpus-hash %s != pin %s"
                             % (key, base, got, pins[key]))
    for key, path in (
            ("twinEnginePySha256", os.path.join(_RULES1, "twin_engine.py")),
            ("certificatePySha256", os.path.join(_RULES1, "certificate.py")),
            ("certificateResultSha256",
             os.path.join(_RULES1, "results", "certificate-result.json")),
            ("rules1RunnerPySha256",
             os.path.join(_RULES1, "rules1_runner.py")),
            ("rulesN3Sha256", os.path.join(_RULES1, "results", "rules.n3")),
            ("f2btRunnerPySha256",
             os.path.join(_ROOT, "poc", "f2b-transfer", "runner",
                          "f2bt_runner.py"))):
        if sha256_file(path) != pins[key]:
            raise SystemExit("ERR_PIN: %s: %s sha != rules2-manifest pin"
                             % (key, path))

    # certificate precondition (rules-1 frozen gate carried over, ASM-1437)
    cert = json.load(open(os.path.join(_RULES1, "results",
                                       "certificate-result.json")))
    cr = cert["certificate_result"]
    if not (cr["success_asm_1131"] and cr["gates_asm_1163_all_pass"]
            and not cr["kill_a_fired"]):
        raise SystemExit("ERR_CERT_PRECONDITION: pinned certificate bytes do "
                         "not carry SUCCESS+gates+no-KILL-a — no GPU spend")

    # c8 gate artifact (G2, PROPOSED-ASM-1427/1445): REAL, sha-pinned, PASS
    c8_path = os.path.join(_HERE, "results", "c8-result.json")
    if sha256_file(c8_path) != pins["c8ResultSha256"]:
        raise SystemExit("ERR_PIN: c8-result.json sha != rules2-manifest pin")
    c8res = json.load(open(c8_path))
    if c8res["mode"] != "REAL" or not c8res["gate"]["gate_pass"]:
        raise SystemExit("ERR_C8_GATE: c8-result is not a REAL pass "
                         "(mode=%s gate_pass=%s) — INSTRUMENT-INVALID, no "
                         "GPU spend" % (c8res["mode"],
                                        c8res["gate"]["gate_pass"]))

    # verbaliser/frames drift guard vs the imported rules-1 bytes
    if r1.verbalise_fact(("rel", "s", "u", "o"), {"s": "A", "o": "B"},
                         {"u": "w"}) != "B is A's w" or \
       r1.verbalise_fact(("cls", "e", r1.MAN), {"e": "E"}, {}) != "E is a man" or \
       r1.verbalise_fact(("diff", "a", "b"), {"a": "A", "b": "B"}, {}) != \
       "A and B are different people":
        raise SystemExit("ERR_FRAME_DRIFT: rules1_runner verbaliser changed")
    man1 = json.load(open(os.path.join(_RULES1, "inputs",
                                       "rules1-manifest.json")))
    f2 = man["prompt_frames"]
    for k in ("task_prefix", "fact_line", "una_line", "question_prefix",
              "menu_prefix", "answer_cue", "padding_sentence"):
        if f2[k] != man1["prompt_frames"][k]:
            raise SystemExit("ERR_FRAME_DRIFT: frame %r differs from the "
                             "rules-1 manifest" % k)
    return man, man1, cert, c8res


def load_corpus(args):
    corpus = load_jsonl(os.path.join(args.corpus_dir, "corpus.jsonl"))
    byid = {e["id"]: e for e in corpus}
    shuf = json.load(open(os.path.join(args.corpus_dir, "c1shuf-map.json")))
    ups = json.load(open(os.path.join(args.corpus_dir, "b1-upsample.json")))
    samples = json.load(open(os.path.join(args.corpus_dir,
                                          "eval-samples.json")))
    cman = json.load(open(os.path.join(args.corpus_dir, "manifest.json")))
    if cman["mode"] != "REAL":
        raise SystemExit("ERR_CORPUS_MODE: rules2-train manifest mode %r "
                         "(the pinned corpus must be the REAL build)"
                         % cman["mode"])
    return corpus, byid, shuf, ups, samples, cman


# ---------------------------------------------------------------------------
# Prompt construction (rules-1 frames + refusal note; B3 proof block)
# ---------------------------------------------------------------------------
def render_prompt(frames, context_lines, question, menu, proof_lines=None,
                  pad_to_tokens=None, lm=None):
    parts = [frames["task_prefix"]]
    for line in context_lines:
        parts.append(frames["fact_line"].format(line=line))
    parts.append(frames["una_line"])
    parts.append(frames["refusal_note"])
    if proof_lines:
        parts.append("\n" + frames["proof_prefix"])
        for line in proof_lines:
            parts.append(frames["proof_line"].format(line=line))
    parts.append(frames["question_prefix"] + question)
    parts.append(frames["menu_prefix"] + ", ".join(menu) + ".")
    base = "".join(parts)
    if pad_to_tokens is not None and lm is not None:
        # PROPOSED-ASM-1127 discipline carried over: neutral token-matching
        # padding, counted with the arm's own tokenizer, before the cue.
        pad_sent = " " + frames["padding_sentence"]
        cur = lm.count_tokens(base + frames["answer_cue"])
        block = ""
        while cur + lm.count_tokens(block + pad_sent) <= pad_to_tokens:
            block += pad_sent
        if block:
            base += "\n" + block.strip()
    return base + frames["answer_cue"]


def build_training_texts(arm, corpus, shuf_map, upsample_ids, byid, frames,
                         menu23, refusal):
    """(prompt, completion) pairs for one FT arm (design SS2.2/2.3)."""
    train = [e for e in corpus if e["split"] == "train"]
    out = []

    def one(e, answer):
        menu = menu23 if e["menu_class"] == "rel23" else ["man", "woman"]
        proof = ([e["proof_sidecar"]] if arm == "B3" and e["family"] == 2
                 and e["proof_sidecar"] else None)
        prompt = render_prompt(frames, e["context"], e["question"], menu,
                               proof_lines=proof)
        return (prompt, " " + answer)

    if arm in ("B2", "B3"):
        for e in train:
            out.append(one(e, e["answer"]))
    elif arm == "c1p":
        for e in train:
            ans = shuf_map["map"].get(e["id"], e["answer"]) \
                if e["family"] == 2 else e["answer"]
            out.append(one(e, ans))
    elif arm == "B1":
        for e in train:
            if e["family"] in (1, 3):
                out.append(one(e, e["answer"]))
        for iid in upsample_ids["ids"]:
            out.append(one(byid[iid], byid[iid]["answer"]))
    else:
        raise SystemExit("ERR_ARM: %r is not a fine-tune arm" % arm)
    return out


# ---------------------------------------------------------------------------
# Eval cells
# ---------------------------------------------------------------------------
def sout_cells(items_covered, items_control, ctx, frames, menu23, refusal):
    cells = []
    for it in items_covered:
        iid = it["item_id"]
        lines = r1.stated_lines(ctx["stated"][iid], ctx["names"][iid],
                                ctx["urn2word"])
        cells.append({"item_id": iid, "cell": "entailed", "lines": lines,
                      "question": it["question"], "menu": menu23,
                      "gold": it["gold_relation"]})
    for it in items_control:
        iid = it["item_id"]
        lines = r1.stated_lines(ctx["stated"][iid], ctx["names"][iid],
                                ctx["urn2word"])
        cells.append({"item_id": iid, "cell": "control", "lines": lines,
                      "question": it["question"], "menu": menu23,
                      "gold": refusal})
    return cells


def corpus_cells(ids, byid, menu23, refusal, cell_name):
    cells = []
    for iid in ids:
        e = byid[iid]
        menu = menu23 if e["menu_class"] == "rel23" else ["man", "woman"]
        gold = refusal if e["family"] == 3 else e["answer"]
        cells.append({"item_id": iid, "cell": cell_name,
                      "lines": e["context"], "question": e["question"],
                      "menu": menu, "gold": gold})
    return cells


def eval_cells(lm, cells, arm, rung, seed, frames, refusal, emitter, guard,
               pad_payloads=None, ctx=None, emit=True):
    """One deterministic greedy pass; returns the decision sha."""
    decisions = []
    for c in cells:
        guard.start_item({"id": c["item_id"]})
        pad = None
        if pad_payloads is not None and c["cell"] in ("entailed", "control"):
            # B0/B5 A1 discipline: pad to the A2-shaped injected count
            pay = pad_payloads[c["item_id"]]
            inj = r1.a2_shaped_injection(pay, ctx["names"][c["item_id"]],
                                         ctx["urn2word"])
            target = lm.count_tokens(render_prompt(
                frames, c["lines"], c["question"], c["menu"],
                proof_lines=inj or None))
            pad = target
        prompt = render_prompt(frames, c["lines"], c["question"], c["menu"],
                               pad_to_tokens=pad, lm=lm)
        options = c["menu"] + [refusal]
        guard.gen()
        ans, _conf = lm.choose({"id": c["item_id"], "cell": c["cell"],
                                "arm": arm}, options, c["gold"], seed, 0,
                               prompt=prompt)
        decisions.append((c["item_id"], c["cell"], ans))
        if emit:
            t_in = lm.count_tokens(prompt)
            t_opts = sum(lm.count_tokens(" %s" % w) for w in options)
            emitter.emit(
                item_id=c["item_id"], arm=arm, rung=rung, seed=seed,
                cell=c["cell"],
                item_correct_ext=int(ans == c["gold"] and c["gold"] != refusal),
                refused=int(ans == refusal), attempts=1, tokens_in=t_in,
                tokens_out=1,
                flops_formula=r1.flops_formula(
                    lm, t_in * len(options) + t_opts))
    blob = json.dumps(decisions, sort_keys=False,
                      separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


# ---------------------------------------------------------------------------
# LoRA fine-tune (real path; never touched by --mock)
# ---------------------------------------------------------------------------
def train_lora(spec, texts, hp, seed, device, log):
    import random as _random

    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.manual_seed(seed)
    tok = AutoTokenizer.from_pretrained(spec["repo"],
                                        revision=spec["revision"])
    base = AutoModelForCausalLM.from_pretrained(
        spec["repo"], revision=spec["revision"],
        torch_dtype=torch.float32)  # fp32 per the pinned dtype line
    n_active = sum(p.numel() for p in base.parameters())
    model = get_peft_model(base, LoraConfig(
        r=hp["r"], lora_alpha=hp["alpha"], lora_dropout=hp["dropout"],
        target_modules=list(hp["target_modules"]), task_type="CAUSAL_LM"))
    model.to(device)
    model.train()
    opt = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=hp["lr"], weight_decay=hp["weight_decay"])
    pad_id = tok.pad_token_id if tok.pad_token_id is not None \
        else tok.eos_token_id

    def encode(prompt, completion):
        pi = tok.encode(prompt, add_special_tokens=False)
        ci = tok.encode(completion, add_special_tokens=False) + \
            [tok.eos_token_id]
        ids = (pi + ci)[:hp["max_seq_len"]]
        labels = ([-100] * len(pi) + ci)[:hp["max_seq_len"]]
        return ids, labels

    order = list(range(len(texts)))
    t0 = time.time()
    tokens_seen = steps = 0
    accum = max(1, hp["batch"] // hp["micro_batch"])
    for epoch in range(hp["epochs"]):
        _random.Random(seed * 1000 + epoch).shuffle(order)
        opt.zero_grad()
        micro = 0
        for start in range(0, len(order), hp["micro_batch"]):
            batch = [encode(*texts[i])
                     for i in order[start:start + hp["micro_batch"]]]
            width = max(len(ids) for ids, _l in batch)
            x = torch.full((len(batch), width), pad_id, dtype=torch.long)
            y = torch.full((len(batch), width), -100, dtype=torch.long)
            att = torch.zeros((len(batch), width), dtype=torch.long)
            for i, (ids, labels) in enumerate(batch):
                x[i, :len(ids)] = torch.tensor(ids)
                y[i, :len(labels)] = torch.tensor(labels)
                att[i, :len(ids)] = 1
                tokens_seen += len(ids)
            out = model(input_ids=x.to(device), attention_mask=att.to(device),
                        labels=y.to(device))
            (out.loss / accum).backward()
            micro += 1
            if micro % accum == 0:
                steps += 1
                lr_scale = min(1.0, steps / max(1, hp["warmup_steps"]))
                for g in opt.param_groups:
                    g["lr"] = hp["lr"] * lr_scale
                opt.step()
                opt.zero_grad()
        log("epoch %d done (%.1fs, %d steps, loss %.4f)"
            % (epoch, time.time() - t0, steps, float(out.loss)))
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    ledger = {"wall_seconds": time.time() - t0, "tokens_seen": tokens_seen,
              "optimizer_steps": steps, "n_examples": len(texts),
              "flops_formula_train": 6.0 * n_active * tokens_seen,
              "n_active_base": n_active}
    lm = r1.Rules1HFLM.__new__(r1.Rules1HFLM)
    lm.tok, lm.model, lm.device, lm.torch = tok, model, device, torch
    lm.name = "%s@%s+lora" % (spec["repo"], spec["revision"][:8])
    lm.n_active = n_active
    lm.weight_bytes = int(n_active * 4)
    return lm, ledger


# ---------------------------------------------------------------------------
# Mock stubs (SYNTHETIC mechanics only; never a measurement)
# ---------------------------------------------------------------------------
class StubR2LM:
    """Deterministic det_u function of (arm, rung, item, cell, seed). The
    planted gradient (B2/B3 lift on entailed strata; c1p collapse; refusal
    trained into FT arms) exists ONLY so the pinned analysis gates resolve
    during mock validation."""

    def __init__(self, rung, arm, spec, refusal):
        self.rung, self.arm, self.spec, self.refusal = rung, arm, spec, refusal
        self.name = "stub-%s-%s" % (arm, rung)
        self.n_active = {"R1": 135_000_000, "R2": 360_000_000,
                         "R3": 1_700_000_000}[rung]

    def count_tokens(self, text):
        return max(1, len(text.split()))

    def choose(self, item, keys, gold, seed, attempt, has_context=False,
               prompt=""):
        s = self.spec
        ft = self.arm in FT_ARMS
        cell = item.get("cell", "entailed")
        # draw-stream keys are shared across arms of the same CLASS so the
        # paired analysis sees the planted CONTRAST, not stub sampling noise
        # (a mock-mechanics choice; never a measurement)
        if gold == self.refusal:
            cls = "ft" if ft else "plain"
            p = s["refuse_skill"][cls]
            if det_u("r2ref", cls, item["id"], seed) < p:
                return self.refusal, 1.0
            wrong = [k for k in keys if k != self.refusal]
            return wrong[int(det_u("r2refw", cls, item["id"], seed)
                             * len(wrong))], 0.5
        if cell == "stated":
            cls = "ft" if ft else "plain"
            p = s["stated_skill_ft"] if ft else s["stated_skill_plain"]
        else:
            cls = "treat" if self.arm in ("B2", "B3") else "plain"
            p = s["base_skill"][self.rung]
            if ft:
                p += (s["c1p_format_bonus"] if self.arm == "c1p"
                      else s["ft_format_bonus"])
            if self.arm in ("B2", "B3") and cell in ("entailed", "s_held"):
                p += s["ft_content_bonus"]
            if self.arm in ("B2", "B3") and cell == "s_mem":
                p += s["smem_lookup_bonus"]
            # c1p: content destroyed — no entailed bonus anywhere; its s_mem
            # answers were TRAINED deranged, so gold-match stays at base.
        p = min(0.98, p)
        if det_u("r2ans", cls, self.rung, item["id"], seed) < p \
                and gold in keys:
            return gold, 1.0
        wrong = [k for k in keys if k != gold and k != self.refusal]
        return wrong[int(det_u("r2wr", cls, self.rung, item["id"], seed)
                         * len(wrong))], 0.5


# ---------------------------------------------------------------------------
# --dry-plan (ESTIMATES only; $0)
# ---------------------------------------------------------------------------
def dry_plan(man, corpus, byid, shuf, ups, samples, items_covered,
             items_control, ctx, gpu, rungs):
    """Char-accurate plan that MIRRORS the execution structure: per FT arm
    3 seeds x (train + full S-out eval), strata + pinned-subsample repeat on
    the first seed only; B0 padded; B4 expected-attempt-factor 2 (rules-1
    planning constant); B5 on R3."""
    plan = man["planning"]
    hp = man["lora"]
    dc = man["design_constants_from_design_doc"]
    frames = man["prompt_frames"]
    refusal = man["refusal_answer"]
    cpt = plan["chars_per_token_estimate"]
    usd = plan["usd_per_hour"][gpu]
    tput_e = plan["throughput_tok_per_s_eval"][gpu]
    tput_t = plan["throughput_tok_per_s_train"][gpu]
    menu23 = ctx["menu"]
    n_opt = len(menu23) + 1

    # actual prompt chars: S-out + corpus strata (real render, no lm)
    sout = sout_cells(items_covered, items_control, ctx, frames, menu23,
                      refusal)
    sout_tok = sum(len(render_prompt(frames, c["lines"], c["question"],
                                     c["menu"])) / cpt * n_opt
                   for c in sout)
    rep_tok = sout_tok * dc["repeat_subsample_n"] / max(1, len(sout)) * 2
    strata_tok = 0.0
    for name, key in (("s_mem", "s_mem"), ("s_held", "s_held"),
                      ("stated_guard", "stated_guard"),
                      ("refusal_guard", "refusal_guard")):
        n = dc["strata_eval_counts"][name if name in
                                     dc["strata_eval_counts"] else key]
        for iid in samples[key][:n]:
            e = byid[iid]
            menu = menu23 if e["menu_class"] == "rel23" else ["man", "woman"]
            strata_tok += len(render_prompt(frames, e["context"],
                                            e["question"], menu)) \
                / cpt * (len(menu) + 1)

    # actual train tokens per arm (prompt+completion, epochs)
    train_tok = {}
    for arm in dc["ft_arms"]:
        texts = build_training_texts(arm, corpus, shuf, ups, byid, frames,
                                     menu23, refusal)
        train_tok[arm] = sum(len(p) + len(c) for p, c in texts) / cpt \
            * hp["epochs"]

    hours = {"train": 0.0, "eval": 0.0}
    for rung in [r for r in ("R1", "R2") if r in rungs]:
        arms_r = dc["ft_arms"] if rung == "R1" else \
            [a for a in dc["rungs_r2_arms"] if a in dc["ft_arms"]]
        for arm in arms_r:
            hours["train"] += len(dc["ft_seeds"]) * train_tok[arm] \
                / tput_t[rung] / 3600.0
            hours["eval"] += (len(dc["ft_seeds"]) * sout_tok + rep_tok
                              + strata_tok) / tput_e[rung] / 3600.0
        # B0 on this rung: S-out + repeat + strata (padding ~ +15%)
        hours["eval"] += (sout_tok * 1.15 + rep_tok + strata_tok) \
            / tput_e[rung] / 3600.0
    # B4 (R1): 23-option rules-1 surface, expected attempt factor 2, 3 seeds
    b4_tok = sum(len(r1.build_prompt(
        json.load(open(os.path.join(_RULES1, "inputs",
                                    "rules1-manifest.json")))
        ["prompt_frames"], it, ctx["stated"][it["item_id"]],
        ctx["names"][it["item_id"]], ctx["urn2word"], menu23)) / cpt * 23
        for it in items_covered)
    hours["eval"] += b4_tok * 2.0 * 3 / tput_e["R1"] / 3600.0
    # B5 (R3): S-out only + repeat
    hours["eval"] += (sout_tok * 1.15 + rep_tok) / tput_e["R3"] / 3600.0

    total = hours["train"] + hours["eval"]
    worst = total * plan["overhead_factor"]
    cap = dc["budget"]
    lines = [
        "rules-2 --dry-plan (ESTIMATES ONLY — planning constants from "
        "rules2-manifest.json; actual corpus/prompt chars; no GPU, no "
        "network, $0 spent by this command)",
        "",
        "rungs planned: %s | FT arms %s x %d seeds | train tokens/run: %s"
        % (rungs, dc["ft_arms"], len(dc["ft_seeds"]),
           {a: "%.1fM" % (t / 1e6) for a, t in train_tok.items()}),
        "eval: S-out %d cells x %d options (all seeds) + strata/repeat on "
        "first seed only" % (len(sout), n_opt),
        "GPU-hours on %s: train %.2f + eval %.2f = %.2f h; with %.1fx "
        "overhead %.2f h"
        % (gpu, hours["train"], hours["eval"], total,
           plan["overhead_factor"], worst),
        "cost at Modal list $%.2f/h: est $%.2f / worst $%.2f"
        % (usd, total * usd, worst * usd),
        "",
    ]
    verdicts = [
        ("worst case vs registry usd_cap ($%d)" % cap["usd_cap"],
         worst * usd <= cap["usd_cap"]),
        ("worst case vs coordinator ceiling ($%d)"
         % cap["coordinator_outer_ceiling_usd"],
         worst * usd <= cap["coordinator_outer_ceiling_usd"]),
        ("worst hours vs gpu_hours_cap (%d h)" % cap["gpu_hours_cap"],
         worst <= cap["gpu_hours_cap"]),
    ]
    for name, ok in verdicts:
        lines.append("  %-46s %s" % (name, "OK" if ok
                                     else "OVER — DO NOT LAUNCH"))
    print("\n".join(lines))
    return all(ok for _n, ok in verdicts)


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs-dir", default=os.path.join(_HERE, "inputs"))
    ap.add_argument("--data-root", default=os.path.join(_ROOT, "data"))
    ap.add_argument("--corpus-dir",
                    default=os.path.join(_ROOT, "data", "rules2-train"))
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--gpu-class", default="A10G",
                    choices=["T4", "A10G", "A100"])
    ap.add_argument("--arms", default="B0,B1,B2,B3,B4,B5,c1p")
    ap.add_argument("--rungs", default="R1",
                    help="R1 (default tier) or R1,R2 (R2 rung = the "
                         "coordinator-authorized second launch; B0/B1/B2 "
                         "only)")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--dry-plan", action="store_true")
    ap.add_argument("--cell-timeout-s", type=float, default=None)
    args = ap.parse_args()
    if args.cell_timeout_s is None:
        args.cell_timeout_s = CELL_TIMEOUT_S_DEFAULT[args.gpu_class]
    t0 = time.time()

    man, man1, cert, c8res = load_inputs(args)
    corpus, byid, shuf, ups, samples, cman = load_corpus(args)
    dc = man["design_constants_from_design_doc"]
    frames = man["prompt_frames"]
    refusal = man["refusal_answer"]
    hp = man["lora"]

    # S-out context via the BYTE-IDENTICAL rules-1 machinery
    class _A:  # minimal arg shim for rules1_runner.build_context
        data_root = args.data_root
    items, ctx = r1.build_context(_A, man1)
    covered = [i for i in items if i["stratum"] == "covered"]
    control = [i for i in items if i["stratum"] != "covered"]
    if len(covered) != dc["n_sout_covered"] or \
            len(control) != dc["n_sout_control"]:
        raise SystemExit("ERR_EVAL_COUNTS: %d/%d != %d/%d"
                         % (len(covered), len(control),
                            dc["n_sout_covered"], dc["n_sout_control"]))
    menu23 = ctx["menu"]

    rungs = [r.strip() for r in args.rungs.split(",") if r.strip()]
    if args.dry_plan:
        ok = dry_plan(man, corpus, byid, shuf, ups, samples, covered,
                      control, ctx, args.gpu_class, rungs)
        sys.exit(0 if ok else 2)

    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    bad = [a for a in arms if a not in ALL_ARMS]
    if bad:
        raise SystemExit("ERR_ARMS: unknown arm(s) %s" % bad)
    os.makedirs(args.out_dir, exist_ok=True)

    def log(msg):
        print("[rules2 %7.1fs] %s" % (time.time() - t0, msg), flush=True)

    if args.mock:
        mk = man["mock"]
        covered = covered[:mk["n_sout_covered"]]
        control = control[:mk["n_sout_control"]]
        strata_n = mk["strata_eval_counts"]
        ft_seeds = mk["ft_seeds"]
    else:
        strata_n = dc["strata_eval_counts"]
        ft_seeds = dc["ft_seeds"]

    sout = sout_cells(covered, control, ctx, frames, menu23, refusal)
    strata = {
        "s_mem": corpus_cells(samples["s_mem"][:strata_n["s_mem"]], byid,
                              menu23, refusal, "s_mem"),
        "s_held": corpus_cells(samples["s_held"][:strata_n["s_held"]], byid,
                               menu23, refusal, "s_held"),
        "stated": corpus_cells(samples["stated_guard"]
                               [:strata_n["stated_guard"]], byid, menu23,
                               refusal, "stated"),
        "refusal_train": corpus_cells(samples["refusal_guard"]
                                      [:strata_n["refusal_guard"]], byid,
                                      menu23, refusal, "refusal_train"),
    }

    emitter = r1.RowEmitter(args.out_dir, args.mock)
    stray = emitter.path  # RowEmitter names its file for rules-1; rename
    emitter.path = os.path.join(
        args.out_dir, "run-records-rules2%s.jsonl"
        % ("-mock" if args.mock else ""))
    if os.path.exists(stray) and stray != emitter.path:
        os.remove(stray)
    with open(emitter.path, "w"):
        pass
    repeat_shas = {}
    training_ledger = {}

    # G4 repeat subsample: pinned first-N-by-sha S-out covered cells
    rep_n = (man["mock"]["repeat_subsample_n"] if args.mock
             else dc["repeat_subsample_n"])
    rep_cells = sorted(
        [c for c in sout if c["cell"] == "entailed"],
        key=lambda c: hashlib.sha256(("rep|" + c["item_id"]).encode())
        .hexdigest())[:rep_n]

    def run_eval_arm(lm, arm, rung, seed, pad=False, sout_only=False,
                     first_seed=True):
        key = "%s/%s/seed=%s" % (arm, rung, seed)
        guard = CellGuard(key, args.cell_timeout_s, MAX_GEN_PER_ITEM)
        pads = ctx["payload_true"] if pad else None
        try:
            eval_cells(lm, sout, arm, rung, seed, frames, refusal,
                       emitter, guard, pad_payloads=pads, ctx=ctx)
            if first_seed:
                # per-arm byte-identical repeat on the pinned subsample
                sha_a = eval_cells(lm, rep_cells, arm, rung, seed, frames,
                                   refusal, emitter, guard,
                                   pad_payloads=pads, ctx=ctx, emit=False)
                sha_b = eval_cells(lm, rep_cells, arm, rung, seed, frames,
                                   refusal, emitter, guard,
                                   pad_payloads=pads, ctx=ctx, emit=False)
                repeat_shas[key] = {"a": sha_a, "b": sha_b,
                                    "byte_identical": sha_a == sha_b}
            if not sout_only and first_seed:
                for name, cells in strata.items():
                    eval_cells(lm, cells, arm, rung, seed, frames, refusal,
                               emitter, guard)
        except CellBudgetExceeded as e:
            emitter.emit(item_id=str(e.item_id), arm=arm, rung=rung,
                         seed=seed, cell="timeout", item_correct_ext=0,
                         refused=0, attempts=0, tokens_in=0, tokens_out=0,
                         flops_formula=0.0, exit="timeout")
            raise SystemExit("ERR_CELL_TIMEOUT: %s" % e)
        log("cell %s done (%.1fs%s)"
            % (key, guard.elapsed(),
               ", repeat %s" % repeat_shas[key]["byte_identical"]
               if key in repeat_shas else ""))

    ft_rungs = {a: (rungs if a in dc["rungs_r2_arms"] else ["R1"])
                for a in ALL_ARMS}

    for arm in arms:
        if arm == "B4":
            # RULES-1 A3 VERBATIM (frames + drivers byte-identical; k=4)
            for seed in dc["eval_only_seeds"]["B4"]:
                lm = (r1.StubRulesLM("R1", {"stub_skill":
                      man["mock"]["b4_stub"]["stub_skill"],
                      "stub_injection_bonus":
                      man["mock"]["b4_stub"]["stub_injection_bonus"],
                      "stub_feedback_bonus":
                      man["mock"]["b4_stub"]["stub_feedback_bonus"]})
                      if args.mock else
                      r1.Rules1HFLM(man["model_revisions"]["R1"]["repo"],
                                    man["model_revisions"]["R1"]["revision"],
                                    args.device))
                guard = CellGuard("B4/seed=%s" % seed, args.cell_timeout_s,
                                  MAX_GEN_PER_ITEM)
                r1.run_verify_retry_cell(
                    lm, "B4", man1["prompt_frames"], covered, ctx,
                    ctx["payload_true"], ctx["tbox_true"],
                    dc["k_retry_b4"], seed, emitter, guard)
                log("cell B4/seed=%s done (%.1fs)" % (seed, guard.elapsed()))
            # E5 control cells for B4: engine-decided named refusals (the
            # rules-1 run_control_cells semantics, emitted under arm=B4)
            for item in control:
                pay = ctx["payload_true"][item["item_id"]]
                refused = int(pay.refusal is not None and pay.answer is None)
                for seed in dc["eval_only_seeds"]["B4"]:
                    emitter.emit(item_id=item["item_id"], arm="B4",
                                 rung="R1", seed=seed, cell="control",
                                 item_correct_ext=0, refused=refused,
                                 attempts=0, tokens_in=0, tokens_out=0,
                                 engine_us=pay.engine_us, flops_formula=0.0,
                                 refusal_code=pay.refusal or "ERR_NONE_BUG")
            continue
        if arm == "B5":
            for seed in dc["eval_only_seeds"]["B5"]:
                lm = (StubR2LM("R3", "B5", man["mock"], refusal) if args.mock
                      else r1.Rules1HFLM(
                          man["model_revisions"]["R3"]["repo"],
                          man["model_revisions"]["R3"]["revision"],
                          args.device))
                run_eval_arm(lm, "B5", "R3", seed, pad=True, sout_only=True)
            continue
        for rung in ft_rungs[arm]:
            spec = man["model_revisions"][rung]
            if arm == "B0":
                for seed in dc["eval_only_seeds"]["B0"]:
                    lm = (StubR2LM(rung, "B0", man["mock"], refusal)
                          if args.mock else
                          r1.Rules1HFLM(spec["repo"], spec["revision"],
                                        args.device))
                    run_eval_arm(lm, "B0", rung, seed, pad=True)
                continue
            # fine-tune arms
            texts = build_training_texts(arm, corpus, shuf, ups, byid,
                                         frames, menu23, refusal)
            for seed in ft_seeds:
                key = "%s/%s/ft_seed=%d" % (arm, rung, seed)
                if args.mock:
                    lm = StubR2LM(rung, arm, man["mock"], refusal)
                    training_ledger[key] = {
                        "mode": "MOCK", "wall_seconds": 0.0,
                        "tokens_seen": 0, "n_examples": len(texts),
                        "flops_formula_train": 0.0}
                else:
                    log("LoRA fine-tune %s (%d examples)..."
                        % (key, len(texts)))
                    lm, ledger = train_lora(spec, texts, hp, seed,
                                            args.device, log)
                    ledger["mode"] = "REAL"
                    training_ledger[key] = ledger
                run_eval_arm(lm, arm, rung, seed,
                             first_seed=(seed == ft_seeds[0]))
                if not args.mock:
                    del lm  # free the adapter+base before the next seed
                    import torch
                    torch.cuda.empty_cache() if args.device == "cuda" else None

    records_sha = sha256_file(emitter.path)
    decision_rows = [{k: v for k, v in r.items() if k != "engine_us"}
                     for r in emitter.rows]
    decision_sha = hashlib.sha256(json.dumps(
        decision_rows, sort_keys=True, separators=(",", ":"))
        .encode()).hexdigest()
    results = {
        "experiment": "rules-2",
        "outcome": "MOCK-HARNESS-COMPLETE" if args.mock
                   else "HARNESS-COMPLETE",
        "outcome_note": "NOT a hypothesis verdict — raw run-record rows "
                        "only; the verdict is computed by the pinned "
                        "analysis/rules_2.py + tools/registry/verdict-gen.py "
                        "under run-vs-audit separation",
        "mode": "MOCK" if args.mock else "FULL",
        "date": utcnow(),
        "device": args.device,
        "gpu_class_assumed_for_usd": args.gpu_class,
        "arms": arms, "rungs": rungs, "ft_seeds": ft_seeds,
        "n_sout_covered": len(covered), "n_sout_control": len(control),
        "strata_eval_counts": strata_n,
        "n_rows": len(emitter.rows),
        "records_file": os.path.basename(emitter.path),
        "records_sha256": records_sha,
        "decision_sha256": decision_sha,
        "repeat_shas": repeat_shas,
        "repeat_note": "per-arm byte-identical S-out repeat (G4, "
                       "PROPOSED-ASM-1439/1451): pass 2 is scored in-process "
                       "and compared by decision sha; rows come from pass 1 "
                       "only",
        "training_ledger": training_ledger,
        "efficiency_constants": man["efficiency_ledger_constants"],
        "pins": man["pins"],
        "pins_verified": True,
        "certificate_precondition": {
            "sha256": man["pins"]["certificateResultSha256"],
            "success_asm_1131": True, "gates_asm_1163_all_pass": True,
            "kill_a_fired": False},
        "c8_gate": {"sha256": man["pins"]["c8ResultSha256"],
                    "gate_pass": c8res["gate"]["gate_pass"],
                    "sout_recovered_acc":
                        c8res["gate"]["sout_recovered_acc"]},
        "corpus_manifest_mode": cman["mode"],
        "models": ({"note": "MOCK — synthetic stub LM, no models loaded"}
                   if args.mock else man["model_revisions"]),
        "wallClockHours": (time.time() - t0) / 3600.0,
    }
    suffix = "-mock" if args.mock else ""
    with open(os.path.join(args.out_dir, "results-rules2%s.json" % suffix),
              "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    log("OUTCOME: %s (%d rows in %s, sha %s)"
        % (results["outcome"], len(emitter.rows), emitter.path,
           records_sha[:12]))


if __name__ == "__main__":
    main()
