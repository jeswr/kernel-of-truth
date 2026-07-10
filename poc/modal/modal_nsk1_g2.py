#!/usr/bin/env python3
"""modal_nsk1_g2 — PRE-FREEZE HEADROOM CALIBRATION (design section 5.2 G2).

EXPLORATORY, phase:"exploratory": every number here is quarantined, uncitable,
and can NEVER flip a verdict. Runs on the DISCARDED 100-item headroom slice only
(data/nsk1-clutrr/headroom.jsonl); the 100 items + anything computed on them are
excluded from all final analysis. This is a runner-role $-bounded calibration of
the third-party surface, NOT the flagship campaign (which belongs to the frozen
record).

Two arms per rung, greedy decode, prompt format fixed + logged:
  text-only      story + question, answer one closed-vocabulary relation word.
  external-text  same + ONE appended engine-hop-1 feedback sentence (F2 topology;
                 matched token budget 24; NEVER contains the gold word — build
                 assertion S9.4). This IS the section-7 skeptic-item-2 external-arm
                 vacuousness check pointed at the CLUTRR surface.

G2 PASS iff at BOTH rungs (i) acc(text-only) in [0.05, 0.85] AND
(ii) acc(external-text) >= acc(text-only) + 0.02.

Rungs use the verified Modal path's SmolLM2 Instruct checkpoints (the same
capability probe poc/modal/modal_nsk1_hooksmoke.py exercised): R1 135M, R2 360M.
NOTE for the designer: registry/experiments/nsk1.json currently names the BASE
variants ("SmolLM2-135M"/"-360M", revision pinned at freeze); the calibration
uses the Instruct variants because the task is chat/QA-shaped and the verified
transport path is Instruct. Reconcile the frozen revision at G4.

    # dry-plan (no GPU, no spend):
    .venv/bin/modal run poc/modal/modal_nsk1_g2.py --dry-plan
    # real (A10G; ~ a few hundred short generations, << 1 GPU-h):
    .venv/bin/modal run poc/modal/modal_nsk1_g2.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import modal

_HERE = Path(__file__).resolve().parent
# Resolve the repo root ONLY where enough ancestors exist. In a Modal container
# the module lives at /root/modal_nsk1_g2.py (no parents[1]); the container only
# runs the GPU function (no repo files), so guard against the import-time crash.
_ROOT = _HERE.parents[1] if len(_HERE.parents) > 1 else _HERE
print("G2_BUILD=v2 module import ok (root=%s)" % _ROOT, flush=True)
sys.path.insert(0, str(_HERE))

HF_CACHE_MOUNT = "/root/.cache/huggingface"
RUNGS = {"R1": "HuggingFaceTB/SmolLM2-135M-Instruct",
         "R2": "HuggingFaceTB/SmolLM2-360M-Instruct"}
MAX_NEW_TOKENS = 16
FEEDBACK_TOKEN_BUDGET = 24  # matches the harness (nsk1_runner.py)


def _image_pins() -> list:
    p = _HERE / "requirements-image.txt"
    if not p.exists():
        return []
    return [ln.strip() for ln in p.read_text().splitlines()
            if ln.strip() and not ln.strip().startswith("#")]


app = modal.App("kot-nsk1-g2")
image = modal.Image.debian_slim(python_version="3.11").pip_install(*_image_pins())
hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


# ------------------------------------------------------------------ prompt build
INSTRUCTION = (
    "Answer with exactly one word naming the family relationship, chosen from "
    "this list: %s. Answer:")


def _build_specs():
    """Load the headroom slice + closed vocab; render both arms' prompts.
    Pure/local (torch-free); the engine already verified every hop-1 at build
    time (S9), so the external-text feedback is rendered from item fields."""
    lex = json.loads((_ROOT / "data/nsk1-clutrr/lexicon.json").read_text())
    vocab = lex["relations_answer_vocab"]
    rel_surface = {v: k for k, v in lex["relations"].items()}  # URN -> mother/father
    instr = INSTRUCTION % ", ".join(vocab)
    specs = []
    for line in (_ROOT / "data/nsk1-clutrr/headroom.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        it = json.loads(line)
        story = "\n".join(it["context"])
        base = "Story:\n%s\nQuestion: %s\n%s" % (story, it["question"], instr)
        # external-text: engine hop-1 rendered as ONE text sentence (F2 topology)
        subj = it["lexicon"][it["hop1"]["subject"]]
        bridge = it["lexicon"][it["hop1_bridge"]]
        rs = rel_surface[it["hop1"]["rel"]]
        fb = "Note: the %s of %s is %s." % (rs, subj, bridge)
        assert len(fb.split()) <= FEEDBACK_TOKEN_BUDGET, "feedback budget breach"
        assert it["gold_surface"].lower() not in [
            w.strip(".").lower() for w in fb.split()], "gold leaked into feedback"
        ext = ("Story:\n%s\nQuestion: %s\n%s\n%s"
               % (story, it["question"], fb, instr))
        specs.append({"item_id": it["item_id"], "gold": it["gold_surface"],
                      "prompt_text_only": base, "prompt_external_text": ext})
    return specs, vocab


def _score(generation: str, gold: str, vocab: list) -> bool:
    """Closed-vocabulary exact match (X3, no cosine): the FIRST vocabulary word
    that appears in the generation must equal the gold relation word."""
    import re
    text = generation.lower()
    best_pos, best_word = None, None
    for w in vocab:
        m = re.search(r"(?<![a-z-])%s(?![a-z-])" % re.escape(w.lower()), text)
        if m and (best_pos is None or m.start() < best_pos):
            best_pos, best_word = m.start(), w
    return best_word == gold


# ------------------------------------------------------------------ GPU function
def _generate(model_id: str, prompts: list) -> list:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float32)
    model.to("cuda").eval()
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    outs = []
    for i, p in enumerate(prompts):
        msgs = [{"role": "user", "content": p}]
        try:
            ids = tok.apply_chat_template(msgs, add_generation_prompt=True,
                                          return_tensors="pt")
        except Exception:
            ids = tok(p, return_tensors="pt").input_ids
        ids = ids.to("cuda")
        with torch.no_grad():
            gen = model.generate(ids, max_new_tokens=MAX_NEW_TOKENS,
                                 do_sample=False, num_beams=1,
                                 pad_token_id=tok.pad_token_id)
        new = gen[0][ids.shape[1]:]
        outs.append(tok.decode(new, skip_special_tokens=True))
        if (i + 1) % 50 == 0:
            print("[g2] %s generated %d/%d" % (model_id, i + 1, len(prompts)))
    try:
        hf_cache.commit()
    except Exception:
        pass
    return outs


@app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=3600)
def gen_a10g(model_id: str, prompts: list) -> list:
    return _generate(model_id, prompts)


@app.function(image=image, gpu="L4", volumes={HF_CACHE_MOUNT: hf_cache}, timeout=3600)
def gen_l4(model_id: str, prompts: list) -> list:
    return _generate(model_id, prompts)


@app.local_entrypoint()
def main(dry_plan: bool = False, gpu: str = "A10G"):
    specs, vocab = _build_specs()
    n = len(specs)
    total_gens = n * 2 * len(RUNGS)
    print("=== G2 headroom calibration plan (design 5.2) ===")
    print("headroom items      : %d" % n)
    print("arms                : text-only, external-text")
    print("rungs               : %s" % ", ".join("%s=%s" % (k, v) for k, v in RUNGS.items()))
    print("generations total   : %d (%d/rung), greedy, max_new_tokens=%d"
          % (total_gens, n * 2, MAX_NEW_TOKENS))
    print("gpu                 : %s" % gpu)
    print("worst-case wall/$   : << 1 GPU-h total; ~$1-3 bound (standing G2 go-ahead)")
    print("phase               : exploratory (quarantined, uncitable)")
    if dry_plan:
        print("DRY-PLAN ONLY — no GPU launched, $0 spent.")
        # sample prompt (logged)
        print("\n--- sample text-only prompt (item %s) ---\n%s" % (specs[0]["item_id"], specs[0]["prompt_text_only"][:600]))
        print("\n--- sample external-text prompt tail ---\n...%s" % specs[0]["prompt_external_text"][-400:])
        return

    genfn = gen_a10g if gpu == "A10G" else gen_l4
    results = {}
    for rung, model_id in RUNGS.items():
        to_gen = [s["prompt_text_only"] for s in specs] + \
                 [s["prompt_external_text"] for s in specs]
        gens = genfn.remote(model_id, to_gen)
        assert len(gens) == 2 * n
        to = gens[:n]
        ex = gens[n:]
        rows = []
        acc_to = acc_ex = 0
        for s, gt, ge in zip(specs, to, ex):
            ct = _score(gt, s["gold"], vocab)
            ce = _score(ge, s["gold"], vocab)
            acc_to += ct
            acc_ex += ce
            rows.append({"phase": "exploratory", "gate": "G2", "rung": rung,
                         "model": model_id, "item_id": s["item_id"],
                         "gold": s["gold"], "gen_text_only": gt,
                         "gen_external_text": ge, "correct_text_only": bool(ct),
                         "correct_external_text": bool(ce)})
        a_to, a_ex = acc_to / n, acc_ex / n
        results[rung] = {"model": model_id, "n": n, "acc_text_only": a_to,
                         "acc_external_text": a_ex, "delta": a_ex - a_to,
                         "rows": rows}
        print("[%s] %s : text-only=%.4f external-text=%.4f delta=%+.4f"
              % (rung, model_id, a_to, a_ex, a_ex - a_to))

    outdir = _ROOT / "poc/nsk1/out/g2"
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "g2_rows.jsonl", "w") as f:
        for rung in RUNGS:
            for r in results[rung]["rows"]:
                f.write(json.dumps(r, sort_keys=True) + "\n")
    summary = {rung: {k: v for k, v in results[rung].items() if k != "rows"}
               for rung in RUNGS}
    # gate: both rungs must pass both clauses
    gate = {}
    for rung in RUNGS:
        a_to = results[rung]["acc_text_only"]
        a_ex = results[rung]["acc_external_text"]
        c_i = 0.05 <= a_to <= 0.85
        c_ii = a_ex >= a_to + 0.02
        gate[rung] = {"clause_i_text_only_in_window": c_i,
                      "clause_ii_external_ge_text_plus_2pp": c_ii,
                      "pass": c_i and c_ii}
    g2_pass = all(gate[r]["pass"] for r in RUNGS)
    summary["gate"] = gate
    summary["G2_PASS"] = g2_pass
    with open(outdir / "g2_summary.json", "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    print("\n=== G2 RESULT (phase:exploratory) ===")
    print(json.dumps(summary, indent=1, sort_keys=True))
    print("G2_PASS =", g2_pass)
