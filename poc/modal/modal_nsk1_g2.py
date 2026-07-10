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


# =====================================================================
# COMBINED G2 RE-RUN (design §5.2.1) — two forms, phase:"exploratory"
# ---------------------------------------------------------------------
# rung-1 G2 FAILED (acc=0 both rungs/arms; the flagship's relation task
# had no headroom at 135M/360M). §5.2.1 pre-declares (BEFORE this re-run)
# a combined two-form G2 on the SAME discarded 100-item headroom slice:
#   form 1b — relation task with the S8 question-DIRECTION bug fixed
#             (stem instantiated in REVERSED released query order); vocab,
#             scorer, and gold (released target verbatim) UNCHANGED.
#   form 2  — the pre-declared entity question "Who is the <gold> of
#             <base>?"; gold = chain-top entity surface; scorer = first
#             per-item-lexicon surface EXCLUDING the queried base name
#             (mechanical anti-echo, identical across arms).
# Both forms × {text-only, external-text} × 2 rungs × 100 items = 800
# short generations. A FORM passes iff at BOTH rungs (i) acc(text-only) ∈
# [0.05,0.85] AND (ii) acc(external) ≥ acc(text-only)+0.02. Freeze
# candidate = FIRST passing form in order [1b, 2]; neither → rung 3.
# Feedback sentence byte-identical to run 1; gold-not-in-feedback asserted
# per form at build (ABORT on violation). All rows phase:"exploratory".
# =====================================================================

INSTRUCTION_ENTITY = "Answer with exactly one word: the name of the person. Answer:"


def _build_specs_g2b():
    """Render BOTH forms' prompts for the 100 headroom items (§5.2.1).
    Pure/local (torch-free). Feedback sentence is byte-identical to run 1
    (`_build_specs`): 'Note: the <hop1-rel> of <base> is <bridge>.'"""
    lex = json.loads((_ROOT / "data/nsk1-clutrr/lexicon.json").read_text())
    vocab = lex["relations_answer_vocab"]
    rel_surface = {v: k for k, v in lex["relations"].items()}  # URN -> mother/father
    instr_rel = INSTRUCTION % ", ".join(vocab)  # form-1b instruction (run-1 identical)
    specs = []
    for line in (_ROOT / "data/nsk1-clutrr/headroom.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        it = json.loads(line)
        story = "\n".join(it["context"])
        subj_urn = it["hop1"]["subject"]
        bridge_urn = it["hop1_bridge"]
        item_lex = it["lexicon"]
        # 3-name, pairwise-distinct assertion (§5.2.1 / S4(f))
        surfaces = list(item_lex.values())
        assert len(item_lex) == 3 and len(surfaces) == 3, \
            "item %s not 3-name" % it["item_id"]
        assert len({s.lower() for s in surfaces}) == 3, \
            "item %s names not pairwise distinct" % it["item_id"]
        base_surface = item_lex[subj_urn]
        top_urns = [u for u in item_lex if u not in (subj_urn, bridge_urn)]
        assert len(top_urns) == 1, "item %s: no unique chain-top" % it["item_id"]
        top_surface = item_lex[top_urns[0]]
        gold_rel = it["gold_surface"]  # released target verbatim (grandmother/-father)

        # feedback: byte-identical to run 1 (F2 topology, matched budget 24)
        subj = item_lex[subj_urn]
        bridge = item_lex[bridge_urn]
        rs = rel_surface[it["hop1"]["rel"]]
        fb = "Note: the %s of %s is %s." % (rs, subj, bridge)
        assert len(fb.split()) <= FEEDBACK_TOKEN_BUDGET, "feedback budget breach"
        fb_tokens = [w.strip(".").lower() for w in fb.split()]
        # gold-not-in-feedback, per form (ABORT on violation):
        #  form 1b — relation-word token distinctness (S9.4, unchanged)
        assert gold_rel.lower() not in fb_tokens, \
            "form-1b gold relation leaked into feedback (%s)" % it["item_id"]
        #  form 2 — gold NAME (chain-top surface) absent from feedback tokens
        assert top_surface.lower() not in fb_tokens, \
            "form-2 gold name leaked into feedback (%s)" % it["item_id"]

        # ---- form 1b: S8 stem in REVERSED released query order (top, base) ----
        q1b = "How is %s related to %s?" % (top_surface, base_surface)
        f1b_to = "Story:\n%s\nQuestion: %s\n%s" % (story, q1b, instr_rel)
        f1b_ext = "Story:\n%s\nQuestion: %s\n%s\n%s" % (story, q1b, fb, instr_rel)

        # ---- form 2: entity question ----
        q2 = "Who is the %s of %s?" % (gold_rel, base_surface)
        f2_to = "Story:\n%s\nQuestion: %s\n%s" % (story, q2, INSTRUCTION_ENTITY)
        f2_ext = "Story:\n%s\nQuestion: %s\n%s\n%s" % (story, q2, fb, INSTRUCTION_ENTITY)

        specs.append({
            "item_id": it["item_id"],
            "f1b_gold": gold_rel, "f1b_to": f1b_to, "f1b_ext": f1b_ext,
            "f2_gold": top_surface, "f2_base": base_surface,
            "f2_surfaces": surfaces, "f2_to": f2_to, "f2_ext": f2_ext,
        })
    return specs, vocab


def _score_entity(generation: str, top_surface: str, base_surface: str,
                  all_surfaces: list) -> bool:
    """Form-2 anti-echo scorer (§5.2.1): the FIRST per-item-lexicon surface
    appearing in the generation, EXCLUDING the queried base surface, must
    equal the chain-top surface. No non-base lexicon name = incorrect.
    Word-boundary, case-insensitive (X3: exact surface match, no cosine)."""
    import re
    text = generation.lower()
    best_pos, best_surf = None, None
    for s in all_surfaces:
        if s.lower() == base_surface.lower():
            continue  # anti-echo: exclude the queried base name entirely
        m = re.search(r"(?<![a-z])%s(?![a-z])" % re.escape(s.lower()), text)
        if m and (best_pos is None or m.start() < best_pos):
            best_pos, best_surf = m.start(), s
    return best_surf is not None and best_surf.lower() == top_surface.lower()


@app.local_entrypoint()
def g2b(dry_plan: bool = False, gpu: str = "A10G"):
    specs, vocab = _build_specs_g2b()
    n = len(specs)
    total_gens = n * 2 * 2 * len(RUNGS)  # forms × arms × rungs × items
    print("=== G2b combined re-run plan (design §5.2.1) ===")
    print("headroom items      : %d" % n)
    print("forms               : 1b (reversed-order relation), 2 (entity question)")
    print("arms                : text-only, external-text")
    print("rungs               : %s" % ", ".join("%s=%s" % (k, v) for k, v in RUNGS.items()))
    print("generations total   : %d (%d/rung), greedy, max_new_tokens=%d"
          % (total_gens, n * 2 * 2, MAX_NEW_TOKENS))
    print("gpu                 : %s" % gpu)
    print("worst-case wall/$   : << 1 GPU-h total; ~$2-5 bound (standing G2 go-ahead)")
    print("phase               : exploratory (quarantined, uncitable)")
    if dry_plan:
        print("DRY-PLAN ONLY — no GPU launched, $0 spent.")
        s0 = specs[0]
        print("\n--- sample form-1b text-only (item %s) ---\n%s"
              % (s0["item_id"], s0["f1b_to"]))
        print("\n--- sample form-1b external tail ---\n...%s" % s0["f1b_ext"][-400:])
        print("\n--- sample form-2 text-only (item %s) ---\n%s"
              % (s0["item_id"], s0["f2_to"]))
        print("\n--- sample form-2 external tail ---\n...%s" % s0["f2_ext"][-400:])
        print("\nform-1b gold=%s | form-2 gold(top)=%s base=%s surfaces=%s"
              % (s0["f1b_gold"], s0["f2_gold"], s0["f2_base"], s0["f2_surfaces"]))
        return

    genfn = gen_a10g if gpu == "A10G" else gen_l4
    # per rung: one batch of 4*n in fixed order [1b_to, 1b_ext, 2_to, 2_ext]
    results = {}
    all_rows = []
    for rung, model_id in RUNGS.items():
        batch = ([s["f1b_to"] for s in specs] + [s["f1b_ext"] for s in specs]
                 + [s["f2_to"] for s in specs] + [s["f2_ext"] for s in specs])
        gens = genfn.remote(model_id, batch)
        assert len(gens) == 4 * n, "expected %d gens, got %d" % (4 * n, len(gens))
        g_1b_to = gens[0:n]
        g_1b_ex = gens[n:2 * n]
        g_2_to = gens[2 * n:3 * n]
        g_2_ex = gens[3 * n:4 * n]
        acc = {"1b_to": 0, "1b_ex": 0, "2_to": 0, "2_ex": 0}
        for i, s in enumerate(specs):
            # form 1b — closed-vocab first-match scorer (run-1 identical)
            c1b_to = _score(g_1b_to[i], s["f1b_gold"], vocab)
            c1b_ex = _score(g_1b_ex[i], s["f1b_gold"], vocab)
            # form 2 — anti-echo entity scorer
            c2_to = _score_entity(g_2_to[i], s["f2_gold"], s["f2_base"], s["f2_surfaces"])
            c2_ex = _score_entity(g_2_ex[i], s["f2_gold"], s["f2_base"], s["f2_surfaces"])
            acc["1b_to"] += c1b_to; acc["1b_ex"] += c1b_ex
            acc["2_to"] += c2_to; acc["2_ex"] += c2_ex
            all_rows.append({"phase": "exploratory", "gate": "G2b", "form": "1b",
                             "rung": rung, "model": model_id, "item_id": s["item_id"],
                             "gold": s["f1b_gold"], "gen_text_only": g_1b_to[i],
                             "gen_external_text": g_1b_ex[i],
                             "correct_text_only": bool(c1b_to),
                             "correct_external_text": bool(c1b_ex)})
            all_rows.append({"phase": "exploratory", "gate": "G2b", "form": "2",
                             "rung": rung, "model": model_id, "item_id": s["item_id"],
                             "gold": s["f2_gold"], "gen_text_only": g_2_to[i],
                             "gen_external_text": g_2_ex[i],
                             "correct_text_only": bool(c2_to),
                             "correct_external_text": bool(c2_ex)})
        results[rung] = {
            "model": model_id, "n": n,
            "form1b": {"acc_text_only": acc["1b_to"] / n,
                       "acc_external_text": acc["1b_ex"] / n,
                       "delta": (acc["1b_ex"] - acc["1b_to"]) / n},
            "form2": {"acc_text_only": acc["2_to"] / n,
                      "acc_external_text": acc["2_ex"] / n,
                      "delta": (acc["2_ex"] - acc["2_to"]) / n},
        }
        for fk, fn in (("form1b", "1b"), ("form2", "2")):
            r = results[rung][fk]
            print("[%s form %s] %s : text-only=%.4f external-text=%.4f delta=%+.4f"
                  % (rung, fn, model_id, r["acc_text_only"], r["acc_external_text"],
                     r["delta"]))

    # ---- gate application (§5.2.1): a FORM passes iff at BOTH rungs
    #      (i) acc(text-only) ∈ [0.05,0.85] AND (ii) external ≥ text-only+0.02
    def _form_gate(form_key):
        per_rung = {}
        for rung in RUNGS:
            r = results[rung][form_key]
            a_to = r["acc_text_only"]; a_ex = r["acc_external_text"]
            c_i = 0.05 <= a_to <= 0.85
            c_ii = a_ex >= a_to + 0.02
            per_rung[rung] = {"clause_i_text_only_in_window": c_i,
                              "clause_ii_external_ge_text_plus_2pp": c_ii,
                              "pass": c_i and c_ii}
        return {"per_rung": per_rung, "pass": all(per_rung[r]["pass"] for r in RUNGS)}

    gates = {"form1b": _form_gate("form1b"), "form2": _form_gate("form2")}
    freeze_candidate = None
    for fk, fname in (("form1b", "1b"), ("form2", "2")):
        if gates[fk]["pass"]:
            freeze_candidate = fname
            break

    summary = {"rungs": {rung: {k: v for k, v in results[rung].items()}
                         for rung in RUNGS},
               "gate": gates,
               "form1b_PASS": gates["form1b"]["pass"],
               "form2_PASS": gates["form2"]["pass"],
               "freeze_candidate": freeze_candidate,
               "rung3_required": freeze_candidate is None,
               "phase": "exploratory"}

    outdir = _ROOT / "poc/nsk1/out/g2b"
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "g2b_rows.jsonl", "w") as f:
        for r in all_rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(outdir / "g2b_summary.json", "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    print("\n=== G2b RESULT (phase:exploratory) ===")
    print(json.dumps(summary, indent=1, sort_keys=True))
    print("freeze_candidate =", freeze_candidate,
          "(None => rung 3 fires with its own G2 check)")


# =====================================================================
# RUNG-3 CUSTOM-SPLIT G2 (design §5.2.1 amendment) — g2c, phase:"exploratory"
# ---------------------------------------------------------------------
# g2b failed at both rungs on both of its forms (form 1b at the floor; form 2
# entity: text-only IN window but external DROPS below text-only, so clause
# (ii) fails). Per §5.2.1, rung 3 now fires and must FIRST pass the SAME
# two-clause G2 on the 100-item CUSTOM nsk1-eval calibration split before any
# rung-3 freeze. If it ALSO fails, the ladder is EXHAUSTED — the no-headroom
# feasibility finding is written up and host-scale-vs-task becomes a maintainer
# fork (NO silent host upgrade inside the record).
#
# FORMS APPLICABLE TO THE CUSTOM CORPUS (per §5.2.1's two forms):
#   form 2 (entity) — APPLICABLE. nsk1-eval is natively an entity-question
#     corpus ("Who is the mother of the mother of X?"; gold = an entity). Uses
#     the item's OWN question verbatim; gold = it["gold_surface"]; the anti-echo
#     scorer `_score_entity` is REUSED BYTE-VERBATIM; candidate set = the item's
#     story names; base = the hop1.subject surface.
#   form 1b (relation-word) — NOT APPLICABLE. nsk1-eval has NO closed
#     relation-answer vocab and NO relation-word gold (lexicon relations = only
#     {mother, father}; gold is an entity). There is no relation-word construct
#     to test, so form 1b is reported N/A (not a fail).
#
# OPERATIONAL ADAPTATIONS (§5.2.1 pins the gate + the form-2 scorer for the
# 3-name CLUTRR items; the custom corpus is shaped differently, so these are
# the faithful mechanical mappings to its structure — all phase:"exploratory",
# quarantined + uncitable, and FLAGGED in the runner handoff for Fable to
# confirm at interpretation):
#   (A) calibration split = the FIRST 100 covered items in file order
#       (nsk1-c0001..c0115; controls interleaved). §5.3 names a "100-item
#       calibration split" but pins no explicit selection rule; first-100-
#       covered is deterministic + reproducible.
#   (B) entity instruction requests the FULL name. Custom surfaces are
#       multi-token "First Last-Last"; the CLUTRR form-2 "exactly one word"
#       instruction is invalid for them, and first names REPEAT within an item
#       (measured 22-24 story names/item, first-name non-unique), so the full
#       surface is the only unambiguous target — matching the harness
#       ExactMapper, which keys on the full corpus-global surface.
#   (C) per-item candidate set = corpus-lexicon surfaces occurring (word-
#       boundary) in the item context. This is the custom analog of CLUTRR's
#       per-item 3-name lexicon and matches the harness `item_lexicon()` notion
#       of "the item's names".
# The feedback sentence is byte-identical to run 1 / g2b / the harness
# ("Note: the <hop1-rel> of <base> is <bridge>."); gold-not-in-feedback is
# asserted per item at build (ABORT on violation).
# =====================================================================

INSTRUCTION_ENTITY_CUSTOM = "Answer with the full name of the person. Answer:"


def _build_specs_g2c():
    """Render the custom entity form on the FIRST 100 covered nsk1-eval items
    (the rung-3 CUSTOM calibration split). Pure/local (torch-free). See the
    module block above for the (flagged) operational adaptations. Form 1b is
    N/A on this corpus. ABORTs on any build assertion (gold-in-names,
    base-in-names, gold-not-in-feedback, feedback budget)."""
    import re
    lex = json.loads((_ROOT / "data/nsk1-eval/lexicon.json").read_text())
    ent = lex["entities"]                              # urn -> surface (corpus-global)
    rel_surface = {v: k for k, v in lex["relations"].items()}  # urn -> mother/father
    surfaces_all = list(ent.values())

    def _story_names(story):
        return [s for s in surfaces_all
                if re.search(r"(?<![A-Za-z])%s(?![A-Za-z])" % re.escape(s), story)]

    specs = []
    for line in (_ROOT / "data/nsk1-eval/items.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        it = json.loads(line)
        if it.get("stratum") != "covered":
            continue
        story = "\n".join(it["context"])
        base_surface = ent[it["hop1"]["subject"]]
        bridge_surface = ent[it["hop1_bridge"]]
        gold_surface = it["gold_surface"]
        names = _story_names(story)
        assert gold_surface in names, "gold not in item names (%s)" % it["item_id"]
        assert base_surface in names, "base not in item names (%s)" % it["item_id"]
        assert gold_surface not in (base_surface, bridge_surface), \
            "gold coincides with base/bridge (%s)" % it["item_id"]
        rs = rel_surface[it["hop1"]["rel"]]
        fb = "Note: the %s of %s is %s." % (rs, base_surface, bridge_surface)
        assert len(fb.split()) <= FEEDBACK_TOKEN_BUDGET, "feedback budget breach"
        assert gold_surface.lower() not in fb.lower(), \
            "gold name leaked into feedback (%s)" % it["item_id"]
        q = it["question"]                             # native entity question
        f2_to = "Story:\n%s\nQuestion: %s\n%s" % (story, q, INSTRUCTION_ENTITY_CUSTOM)
        f2_ext = "Story:\n%s\nQuestion: %s\n%s\n%s" % (story, q, fb,
                                                       INSTRUCTION_ENTITY_CUSTOM)
        specs.append({"item_id": it["item_id"], "gold": gold_surface,
                      "gold_first": gold_surface.split()[0], "base": base_surface,
                      "surfaces": names, "f2_to": f2_to, "f2_ext": f2_ext})
        if len(specs) >= 100:
            break
    assert len(specs) == 100, "expected 100 calibration items, got %d" % len(specs)
    return specs


@app.local_entrypoint()
def g2c(dry_plan: bool = False, gpu: str = "A10G"):
    specs = _build_specs_g2c()
    n = len(specs)
    total_gens = n * 2 * len(RUNGS)   # entity form × 2 arms × 2 rungs
    print("=== G2c rung-3 CUSTOM-split G2 plan (design §5.2.1 amendment) ===")
    print("custom split        : first %d covered nsk1-eval items (%s..%s)"
          % (n, specs[0]["item_id"], specs[-1]["item_id"]))
    print("applicable form     : 2 (entity, native question); form 1b N/A "
          "(no relation-word construct in nsk1-eval)")
    print("arms                : text-only, external-text")
    print("rungs               : %s" % ", ".join("%s=%s" % (k, v) for k, v in RUNGS.items()))
    print("generations total   : %d (%d/rung), greedy, max_new_tokens=%d"
          % (total_gens, n * 2, MAX_NEW_TOKENS))
    print("gpu                 : %s" % gpu)
    print("worst-case wall/$   : << 1 GPU-h total; ~$1-3 bound (standing G2 go-ahead)")
    print("phase               : exploratory (quarantined, uncitable)")
    if dry_plan:
        s0 = specs[0]
        print("DRY-PLAN ONLY — no GPU launched, $0 spent.")
        print("\n--- sample entity text-only (item %s) ---\n%s"
              % (s0["item_id"], s0["f2_to"]))
        print("\n--- sample entity external tail ---\n...%s" % s0["f2_ext"][-400:])
        print("\nform-2 gold=%s base=%s | #candidate names=%d"
              % (s0["gold"], s0["base"], len(s0["surfaces"])))
        return

    genfn = gen_a10g if gpu == "A10G" else gen_l4
    import re

    def _has(word, text):
        return bool(re.search(r"(?<![A-Za-z])%s(?![A-Za-z])" % re.escape(word.lower()),
                              text.lower()))

    results = {}
    all_rows = []
    for rung, model_id in RUNGS.items():
        batch = [s["f2_to"] for s in specs] + [s["f2_ext"] for s in specs]
        gens = genfn.remote(model_id, batch)
        assert len(gens) == 2 * n, "expected %d gens, got %d" % (2 * n, len(gens))
        g_to = gens[:n]
        g_ex = gens[n:]
        acc_to = acc_ex = 0
        for i, s in enumerate(specs):
            c_to = _score_entity(g_to[i], s["gold"], s["base"], s["surfaces"])
            c_ex = _score_entity(g_ex[i], s["gold"], s["base"], s["surfaces"])
            acc_to += c_to
            acc_ex += c_ex
            all_rows.append({"phase": "exploratory", "gate": "G2c", "form": "2",
                             "split": "nsk1-eval-custom-calibration-first100covered",
                             "rung": rung, "model": model_id, "item_id": s["item_id"],
                             "gold": s["gold"], "base": s["base"],
                             "gen_text_only": g_to[i], "gen_external_text": g_ex[i],
                             "correct_text_only": bool(c_to),
                             "correct_external_text": bool(c_ex),
                             "gold_full_in_text_only": _has(s["gold"], g_to[i]),
                             "gold_full_in_external": _has(s["gold"], g_ex[i]),
                             "gold_first_in_text_only": _has(s["gold_first"], g_to[i]),
                             "gold_first_in_external": _has(s["gold_first"], g_ex[i])})
        a_to, a_ex = acc_to / n, acc_ex / n
        results[rung] = {"model": model_id, "n": n,
                         "form2": {"acc_text_only": a_to, "acc_external_text": a_ex,
                                   "delta": a_ex - a_to}}
        print("[%s form 2] %s : text-only=%.4f external-text=%.4f delta=%+.4f"
              % (rung, model_id, a_to, a_ex, a_ex - a_to))

    # gate (§5.2.1): a FORM passes iff at BOTH rungs (i) acc(text-only) ∈
    # [0.05,0.85] AND (ii) acc(external) ≥ acc(text-only)+0.02.
    per_rung = {}
    for rung in RUNGS:
        r = results[rung]["form2"]
        a_to = r["acc_text_only"]
        a_ex = r["acc_external_text"]
        c_i = 0.05 <= a_to <= 0.85
        c_ii = a_ex >= a_to + 0.02
        per_rung[rung] = {"clause_i_text_only_in_window": c_i,
                          "clause_ii_external_ge_text_plus_2pp": c_ii,
                          "pass": c_i and c_ii}
    form2_pass = all(per_rung[r]["pass"] for r in RUNGS)
    freeze_candidate = "2" if form2_pass else None
    ladder_exhausted = freeze_candidate is None  # form 1b N/A => form 2 is the only form
    summary = {"rungs": {rung: results[rung] for rung in RUNGS},
               "gate": {"form2": {"per_rung": per_rung, "pass": form2_pass}},
               "form1b_applicable": False,
               "form1b_status": ("N/A — nsk1-eval has no closed relation-answer "
                                 "vocab / no relation-word gold"),
               "form2_PASS": form2_pass,
               "rung3_freeze_candidate": freeze_candidate,
               "ladder_exhausted": ladder_exhausted,
               "phase": "exploratory"}
    outdir = _ROOT / "poc/nsk1/out/g2c"
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "g2c_rows.jsonl", "w") as f:
        for r in all_rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(outdir / "g2c_summary.json", "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    print("\n=== G2c RESULT (phase:exploratory) ===")
    print(json.dumps(summary, indent=1, sort_keys=True))
    print("form2_PASS =", form2_pass, "| freeze_candidate =", freeze_candidate,
          "| LADDER_EXHAUSTED =", ladder_exhausted)


# =====================================================================
# G2d — HOST-SCALE + FEW-SHOT HEADROOM PROBE (ladder-exhaustion fork A'+A'')
# ---------------------------------------------------------------------
# The fallback ladder (g2/g2b/g2c) EXHAUSTED at R1=135M / R2=360M zero-shot: no
# measurable headroom for the flagship's internal-vs-external contrast on EITHER
# eval surface. Per docs/next/nsk1-ladder-exhaustion.md §6 the maintainer chose
# the combined G2d fork (ranks 1+2), run here as ONE Modal launch:
#   A'  host-scale probe : the SAME two-clause G2 headroom check at
#       SmolLM2-1.7B-Instruct (the in-family R3 of f2/f2b), ZERO-SHOT — does the
#       "compose a delivered fact" capability exist in-family at 1.7B?
#   A'' few-shot rider   : the SAME check at R1=135M / R2=360M with k=2 compose
#       exemplars prepended (a DISCLOSED prompt amendment: zero-shot -> few-shot)
#       — is the g2b/g2c format-collapse / bridge-capture pathology a zero-shot
#       prompt artifact the smallest hosts can be rescued from?
# Forms + surfaces UNCHANGED from the ladder: CLUTRR forms {1b relation-word,
# 2 entity} on data/nsk1-clutrr/headroom.jsonl (TARGET prompts byte-reused from
# _build_specs_g2b) and form 2 on the custom nsk1-eval first-100-covered split
# (TARGET prompts byte-reused from _build_specs_g2c). Arms unchanged: text-only,
# external-text. The two-clause gate is REUSED VERBATIM (§5.2.1): a
# (form, host, shot) cell PASSES iff acc(text-only) in [0.05,0.85] AND
# acc(external) >= acc(text-only)+0.02. Every row is phase:"exploratory"
# (quarantined, uncitable, flips no verdict).
#
# FEW-SHOT EXEMPLAR CONSTRUCTION — a runner OPERATIONAL instantiation of Fable's
# "k-shot compose exemplars" mechanism (§6 A''); DISCLOSED here and FLAGGED in
# the handoff for Fable to confirm at interpretation (same status as the g2c
# operational adaptations above — mechanical, deterministic, phase:exploratory):
#   * k = 2 exemplars, prepended as worked examples in the SAME prompt format as
#     the target (each = the target's rendered prompt for that form/arm with the
#     gold answer appended after "Answer:"; examples separated by a blank line;
#     the whole few-shot string is ONE user turn, chat-templated exactly as the
#     zero-shot arm). The TARGET prompt is byte-identical to g2b/g2c, so the ONLY
#     change vs the zero-shot arm is the prepended prefix (clean host-scale and
#     shot contrasts).
#   * exemplar items are drawn DETERMINISTICALLY and DISJOINT from the scored
#     slice (never a scored item): CLUTRR = the first covered grandfather-gold and
#     first covered grandmother-gold items of data/nsk1-clutrr/items.jsonl NOT in
#     the 100-item headroom slice (class-balanced so neither relation is favoured);
#     custom = the first two covered nsk1-eval items AFTER the first-100
#     calibration split. Same exemplars for both CLUTRR forms.
#   * external-arm exemplars carry their OWN feedback sentence (byte-identical
#     renderer) and their answer is the COMPOSED grandparent / chain-top (NOT the
#     parroted bridge) — the demonstration whose absence g2b/g2c diagnosed.
#   * gold-not-in-feedback + feedback-budget + 3-name asserts hold per exemplar
#     (ABORT on violation), exactly as the target build gates do.
#
# Cells (9): {clutrr/1b, clutrr/2, custom/2} x {R3-1.7B zero-shot, R1-135M
# few-shot, R2-360M few-shot}. Generations: 3 hosts x (2 forms x 2 arms x 100
# CLUTRR + 1 form x 2 arms x 100 custom) = 3 x 600 = 1800 short greedy gens,
# max_new_tokens=16 (MAX_NEW_TOKENS), << a few GPU-h; ~$5-10 bound (standing G2
# envelope + the maintainer's explicit G2d fork choice). Outputs ->
# poc/nsk1/out/g2d/. Nothing above g2/g2b/g2c or the shared helpers is modified.
# =====================================================================

HOSTSCALE_MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"  # A' zero-shot probe (R3)
FEWSHOT_K = 2


def _clutrr_exemplar_items():
    """First covered grandfather-gold + grandmother-gold CLUTRR items NOT in the
    headroom slice, in file order (deterministic, class-balanced, DISJOINT from
    the 100 scored items). Returns [grandfather_item, grandmother_item]."""
    head_ids = set()
    for line in (_ROOT / "data/nsk1-clutrr/headroom.jsonl").read_text().splitlines():
        if line.strip():
            head_ids.add(json.loads(line)["item_id"])
    gf = gm = None
    for line in (_ROOT / "data/nsk1-clutrr/items.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        it = json.loads(line)
        if it.get("stratum") != "covered" or it["item_id"] in head_ids:
            continue
        if it["gold_surface"] == "grandfather" and gf is None:
            gf = it
        elif it["gold_surface"] == "grandmother" and gm is None:
            gm = it
        if gf is not None and gm is not None:
            break
    assert gf is not None and gm is not None, \
        "could not find disjoint grandfather/grandmother CLUTRR exemplars"
    return [gf, gm]


def _render_clutrr_exemplar(it, form, arm, vocab, rel_surface):
    """Render ONE CLUTRR exemplar (worked example) in the SAME format as the g2b
    TARGET prompt for (form, arm) with the gold answer appended after 'Answer:'.
    Feedback byte-identical to run 1 / g2b. ABORTs on the same build assertions."""
    lex = it["lexicon"]
    surfaces = list(lex.values())
    assert len(lex) == 3 and len({s.lower() for s in surfaces}) == 3, \
        "exemplar %s not 3-name-distinct" % it["item_id"]
    subj = it["hop1"]["subject"]
    br = it["hop1_bridge"]
    base = lex[subj]
    bridge = lex[br]
    tops = [u for u in lex if u not in (subj, br)]
    assert len(tops) == 1, "exemplar %s: no unique chain-top" % it["item_id"]
    top = lex[tops[0]]
    gold_rel = it["gold_surface"]
    story = "\n".join(it["context"])
    rs = rel_surface[it["hop1"]["rel"]]
    fb = "Note: the %s of %s is %s." % (rs, base, bridge)
    assert len(fb.split()) <= FEEDBACK_TOKEN_BUDGET, "exemplar feedback budget breach"
    fb_tokens = [w.strip(".").lower() for w in fb.split()]
    assert gold_rel.lower() not in fb_tokens, \
        "exemplar 1b gold leaked into feedback (%s)" % it["item_id"]
    assert top.lower() not in fb_tokens, \
        "exemplar 2 gold name leaked into feedback (%s)" % it["item_id"]
    instr_rel = INSTRUCTION % ", ".join(vocab)
    if form == "1b":
        q = "How is %s related to %s?" % (top, base)
        prompt = ("Story:\n%s\nQuestion: %s\n%s" % (story, q, instr_rel) if arm == "to"
                  else "Story:\n%s\nQuestion: %s\n%s\n%s" % (story, q, fb, instr_rel))
        gold = gold_rel
    else:  # form 2 (entity)
        q = "Who is the %s of %s?" % (gold_rel, base)
        prompt = ("Story:\n%s\nQuestion: %s\n%s" % (story, q, INSTRUCTION_ENTITY) if arm == "to"
                  else "Story:\n%s\nQuestion: %s\n%s\n%s" % (story, q, fb, INSTRUCTION_ENTITY))
        gold = top
    return "%s %s" % (prompt, gold)


def _fewshot_prefix_clutrr(exemplars, form, arm, vocab, rel_surface):
    blocks = [_render_clutrr_exemplar(it, form, arm, vocab, rel_surface)
              for it in exemplars]
    return "\n\n".join(blocks) + "\n\n"


def _custom_exemplar_items():
    """First FEWSHOT_K covered nsk1-eval items AFTER the first-100 calibration
    split (deterministic, DISJOINT from the scored custom split)."""
    covered = []
    for line in (_ROOT / "data/nsk1-eval/items.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        it = json.loads(line)
        if it.get("stratum") == "covered":
            covered.append(it)
    pool = covered[100:]
    assert len(pool) >= FEWSHOT_K, "custom disjoint exemplar pool too small"
    return pool[:FEWSHOT_K]


def _render_custom_exemplar(it, arm, ent, rel_surface):
    """Render ONE custom (nsk1-eval) form-2 exemplar in the SAME format as the
    g2c TARGET prompt for the arm, with the gold name appended. Feedback
    byte-identical to g2c. ABORTs on the same build assertions."""
    base = ent[it["hop1"]["subject"]]
    bridge = ent[it["hop1_bridge"]]
    gold = it["gold_surface"]
    story = "\n".join(it["context"])
    rs = rel_surface[it["hop1"]["rel"]]
    fb = "Note: the %s of %s is %s." % (rs, base, bridge)
    assert len(fb.split()) <= FEEDBACK_TOKEN_BUDGET, "custom exemplar feedback budget breach"
    assert gold.lower() not in fb.lower(), \
        "custom exemplar gold leaked into feedback (%s)" % it["item_id"]
    q = it["question"]
    prompt = ("Story:\n%s\nQuestion: %s\n%s" % (story, q, INSTRUCTION_ENTITY_CUSTOM)
              if arm == "to"
              else "Story:\n%s\nQuestion: %s\n%s\n%s" % (story, q, fb, INSTRUCTION_ENTITY_CUSTOM))
    return "%s %s" % (prompt, gold)


def _fewshot_prefix_custom(exemplars, arm, ent, rel_surface):
    blocks = [_render_custom_exemplar(it, arm, ent, rel_surface) for it in exemplars]
    return "\n\n".join(blocks) + "\n\n"


@app.local_entrypoint()
def g2d(dry_plan: bool = False, gpu: str = "A10G"):
    # ---- TARGET prompts: byte-reused from the ladder builders (unmodified) ----
    cl, vocab = _build_specs_g2b()            # CLUTRR forms 1b + 2 (100 items)
    cu = _build_specs_g2c()                   # custom form 2 (100 items)
    n_c = len(cl)
    n_cu = len(cu)

    # ---- few-shot exemplars (deterministic, disjoint, disclosed) ----
    lex_c = json.loads((_ROOT / "data/nsk1-clutrr/lexicon.json").read_text())
    rel_surface_c = {v: k for k, v in lex_c["relations"].items()}
    lex_cu = json.loads((_ROOT / "data/nsk1-eval/lexicon.json").read_text())
    ent = lex_cu["entities"]
    rel_surface_cu = {v: k for k, v in lex_cu["relations"].items()}

    ex_c = _clutrr_exemplar_items()
    ex_cu = _custom_exemplar_items()
    pfx_c = {(form, arm): _fewshot_prefix_clutrr(ex_c, form, arm, vocab, rel_surface_c)
             for form in ("1b", "2") for arm in ("to", "ext")}
    pfx_cu = {arm: _fewshot_prefix_custom(ex_cu, arm, ent, rel_surface_cu)
              for arm in ("to", "ext")}

    ex_c_ids = [it["item_id"] for it in ex_c]
    ex_cu_ids = [it["item_id"] for it in ex_cu]

    # ---- host configs: A' (1.7B zero-shot) + A'' (135M/360M few-shot) ----
    host_configs = [
        ("R3", HOSTSCALE_MODEL, "zero-shot"),
        ("R1", RUNGS["R1"], "few-shot"),
        ("R2", RUNGS["R2"], "few-shot"),
    ]
    gens_per_host = n_c * 2 * 2 + n_cu * 2   # 400 CLUTRR + 200 custom = 600
    total_gens = gens_per_host * len(host_configs)

    print("=== G2d host-scale + few-shot headroom probe (ladder-exhaustion §6 A'+A'') ===")
    print("CLUTRR items        : %d (data/nsk1-clutrr/headroom.jsonl)" % n_c)
    print("custom items        : %d (nsk1-eval first-100-covered)" % n_cu)
    print("forms               : CLUTRR {1b, 2}; custom {2} (form 1b N/A on custom)")
    print("arms                : text-only, external-text")
    print("host configs        : R3=%s (zero-shot) ; R1=%s (few-shot k=%d) ; R2=%s (few-shot k=%d)"
          % (HOSTSCALE_MODEL, RUNGS["R1"], FEWSHOT_K, RUNGS["R2"], FEWSHOT_K))
    print("few-shot exemplars  : CLUTRR=%s ; custom=%s (disjoint, class-balanced CLUTRR)"
          % (ex_c_ids, ex_cu_ids))
    print("generations total   : %d (%d/host), greedy, max_new_tokens=%d"
          % (total_gens, gens_per_host, MAX_NEW_TOKENS))
    print("gpu                 : %s (A10G fits 1.7B fp32 ~7GB)" % gpu)
    print("gate                : (form,host,shot) PASS iff text-only in [0.05,0.85] AND external >= text-only+0.02")
    print("worst-case wall/$   : << a few GPU-h; ~$5-10 bound (standing G2 envelope + maintainer G2d fork)")
    print("phase               : exploratory (quarantined, uncitable)")

    if dry_plan:
        print("\nDRY-PLAN ONLY — no GPU launched, $0 spent. All build asserts passed.")
        print("\n--- CLUTRR form-1b few-shot prefix (text-only) ---\n%s" % pfx_c[("1b", "to")])
        print("--- + target (item %s) ---\n%s" % (cl[0]["item_id"], cl[0]["f1b_to"]))
        print("\n--- CLUTRR form-2 few-shot prefix (external) tail ---\n...%s" % pfx_c[("2", "ext")][-500:])
        print("--- + target (item %s) tail ---\n...%s" % (cl[0]["item_id"], cl[0]["f2_ext"][-300:]))
        print("\n--- custom form-2 few-shot prefix (text-only) tail ---\n...%s" % pfx_cu["to"][-500:])
        print("--- + target (item %s) tail ---\n...%s" % (cu[0]["item_id"], cu[0]["f2_to"][-300:]))
        print("\nexemplar golds: CLUTRR 1b=%s | custom form2=%s"
              % ([it["gold_surface"] for it in ex_c], [it["gold_surface"] for it in ex_cu]))
        return

    genfn = gen_a10g if gpu == "A10G" else gen_l4

    def _assemble(shot):
        fewshot = (shot == "few-shot")
        b = []
        b += [(pfx_c[("1b", "to")] + s["f1b_to"]) if fewshot else s["f1b_to"] for s in cl]
        b += [(pfx_c[("1b", "ext")] + s["f1b_ext"]) if fewshot else s["f1b_ext"] for s in cl]
        b += [(pfx_c[("2", "to")] + s["f2_to"]) if fewshot else s["f2_to"] for s in cl]
        b += [(pfx_c[("2", "ext")] + s["f2_ext"]) if fewshot else s["f2_ext"] for s in cl]
        b += [(pfx_cu["to"] + s["f2_to"]) if fewshot else s["f2_to"] for s in cu]
        b += [(pfx_cu["ext"] + s["f2_ext"]) if fewshot else s["f2_ext"] for s in cu]
        return b

    all_rows = []
    cells = []
    for host_label, model_id, shot in host_configs:
        batch = _assemble(shot)
        assert len(batch) == gens_per_host, \
            "expected %d prompts, got %d" % (gens_per_host, len(batch))
        gens = genfn.remote(model_id, batch)
        assert len(gens) == gens_per_host, \
            "expected %d gens, got %d" % (gens_per_host, len(gens))
        g_c1b_to = gens[0:n_c]
        g_c1b_ex = gens[n_c:2 * n_c]
        g_c2_to = gens[2 * n_c:3 * n_c]
        g_c2_ex = gens[3 * n_c:4 * n_c]
        off = 4 * n_c
        g_cu_to = gens[off:off + n_cu]
        g_cu_ex = gens[off + n_cu:off + 2 * n_cu]

        acc = {"c1b_to": 0, "c1b_ex": 0, "c2_to": 0, "c2_ex": 0, "cu_to": 0, "cu_ex": 0}
        for i, s in enumerate(cl):
            c1b_to = _score(g_c1b_to[i], s["f1b_gold"], vocab)
            c1b_ex = _score(g_c1b_ex[i], s["f1b_gold"], vocab)
            c2_to = _score_entity(g_c2_to[i], s["f2_gold"], s["f2_base"], s["f2_surfaces"])
            c2_ex = _score_entity(g_c2_ex[i], s["f2_gold"], s["f2_base"], s["f2_surfaces"])
            acc["c1b_to"] += c1b_to
            acc["c1b_ex"] += c1b_ex
            acc["c2_to"] += c2_to
            acc["c2_ex"] += c2_ex
            all_rows.append({"phase": "exploratory", "gate": "G2d", "surface": "clutrr",
                             "form": "1b", "host": host_label, "model": model_id,
                             "shot": shot, "item_id": s["item_id"], "gold": s["f1b_gold"],
                             "gen_text_only": g_c1b_to[i], "gen_external_text": g_c1b_ex[i],
                             "correct_text_only": bool(c1b_to),
                             "correct_external_text": bool(c1b_ex)})
            all_rows.append({"phase": "exploratory", "gate": "G2d", "surface": "clutrr",
                             "form": "2", "host": host_label, "model": model_id,
                             "shot": shot, "item_id": s["item_id"], "gold": s["f2_gold"],
                             "base": s["f2_base"], "gen_text_only": g_c2_to[i],
                             "gen_external_text": g_c2_ex[i],
                             "correct_text_only": bool(c2_to),
                             "correct_external_text": bool(c2_ex)})
        for i, s in enumerate(cu):
            cu_to = _score_entity(g_cu_to[i], s["gold"], s["base"], s["surfaces"])
            cu_ex = _score_entity(g_cu_ex[i], s["gold"], s["base"], s["surfaces"])
            acc["cu_to"] += cu_to
            acc["cu_ex"] += cu_ex
            all_rows.append({"phase": "exploratory", "gate": "G2d", "surface": "custom",
                             "form": "2",
                             "split": "nsk1-eval-custom-calibration-first100covered",
                             "host": host_label, "model": model_id, "shot": shot,
                             "item_id": s["item_id"], "gold": s["gold"], "base": s["base"],
                             "gen_text_only": g_cu_to[i], "gen_external_text": g_cu_ex[i],
                             "correct_text_only": bool(cu_to),
                             "correct_external_text": bool(cu_ex)})

        def _cell(surface, form, a_to_c, a_ex_c, nn):
            a_to = a_to_c / nn
            a_ex = a_ex_c / nn
            c_i = 0.05 <= a_to <= 0.85
            c_ii = a_ex >= a_to + 0.02
            return {"surface": surface, "form": form, "host": host_label,
                    "model": model_id, "shot": shot, "n": nn,
                    "acc_text_only": a_to, "acc_external_text": a_ex,
                    "delta": a_ex - a_to,
                    "clause_i_text_only_in_window": c_i,
                    "clause_ii_external_ge_text_plus_2pp": c_ii,
                    "pass": c_i and c_ii}
        cells.append(_cell("clutrr", "1b", acc["c1b_to"], acc["c1b_ex"], n_c))
        cells.append(_cell("clutrr", "2", acc["c2_to"], acc["c2_ex"], n_c))
        cells.append(_cell("custom", "2", acc["cu_to"], acc["cu_ex"], n_cu))
        for cell in cells[-3:]:
            print("[%s %s form %s %s] %s : text-only=%.4f external-text=%.4f delta=%+.4f pass=%s"
                  % (host_label, shot, cell["form"], cell["surface"], model_id,
                     cell["acc_text_only"], cell["acc_external_text"], cell["delta"],
                     cell["pass"]))

    passing = [{"surface": c["surface"], "form": c["form"], "host": c["host"],
                "shot": c["shot"]} for c in cells if c["pass"]]
    summary = {
        "phase": "exploratory",
        "gate": "G2d",
        "spec_ref": "docs/next/nsk1-ladder-exhaustion.md §6 ranks 1+2 (A'+A'')",
        "gate_rule": "(form,host,shot) PASS iff acc(text-only) in [0.05,0.85] AND acc(external) >= acc(text-only)+0.02",
        "fewshot_k": FEWSHOT_K,
        "fewshot_exemplars": {"clutrr": ex_c_ids, "custom": ex_cu_ids},
        "host_configs": [{"host": h, "model": m, "shot": s} for h, m, s in host_configs],
        "cells": cells,
        "passing_cells": passing,
        "any_pass": bool(passing),
    }

    outdir = _ROOT / "poc/nsk1/out/g2d"
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "g2d_rows.jsonl", "w") as f:
        for r in all_rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(outdir / "g2d_summary.json", "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    print("\n=== G2d RESULT (phase:exploratory) ===")
    print(json.dumps(summary, indent=1, sort_keys=True))
    print("\nany_pass =", bool(passing), "| passing_cells =", passing)


# =====================================================================
# B′ — nsk1 Stage-0 INTERNAL-CHANNEL DIAGNOSTIC at R3, phase:"exploratory"
# ---------------------------------------------------------------------
# EXECUTES docs/next/nsk1-bprime-stage0-spec.md (Fable, runner-ready; the spec
# leaves ZERO design decisions to the runner). This entrypoint is APPENDED; the
# g2/g2b/g2c/g2d code and every shared helper above are byte-untouched. It
# reuses the verified G2d machinery: form-2 (entity) prompt construction
# byte-identical to _build_specs_g2b's f2 branch, the _score_entity scorer
# byte-verbatim, the g2d feedback sentence renderer, and the hooksmoke-verified
# residual read/write hook path (hidden_states[k] = output of decoder layer
# module k-1 = INPUT of module k).
#
# Two replacement-transplant probe families (Law 1: only the model's OWN
# activations ever enter the model — no raw kernel/encoder coordinates):
#   P1 self back-patch (GATE-BEARING): replace the final-prompt-token residual
#       carrying hidden_states[ℓt] (INPUT of decoder module ℓt) with the item's
#       OWN harvested hidden_states[ℓs], ℓs>ℓt, prefill-only. Control = source
#       from the seed-pinned deranged item σ(i).
#   P2 oracle bridge-patch (REPORTED-ONLY): patch the item's feedback-sentence
#       bridge-token residual hidden_states[ℓh] into the same target position.
#       Control = deranged bridge σ(i). Breakage = real bridge-patch on 100
#       text-only-correct items (no control).
#
# Host R3 = SmolLM2-1.7B-Instruct, zero-shot, CLUTRR entity form 2, all 958
# covered items (858 covered rows of data/nsk1-clutrr/items.jsonl + 100 rows of
# data/nsk1-clutrr/headroom.jsonl). Greedy, fp32, chat template, 16 new tokens.
# Every row phase:"exploratory" (quarantined, uncitable, flips no verdict).
#
#   .venv/bin/modal run poc/modal/modal_nsk1_g2.py::bprime --dry-plan   # $0
#   .venv/bin/modal run poc/modal/modal_nsk1_g2.py::bprime              # A10G
# =====================================================================

import math as _bp_math       # appended-only import (existing bytes untouched)
import random as _bp_random   # appended-only import

BPRIME_MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"  # R3 (ASM-0040)
BPRIME_SEED = 20260711        # σ derangement, C100 sample, 300-subsample (ASM-0041/spec §3)
BPRIME_FLOOR = 0.15           # Stage-0 floor VALUE (pre-declared, ASM-0041)
BPRIME_Z = 1.6449             # one-sided 95% (Φ⁻¹(0.95)); Wilson bounds (spec §4)
BPRIME_SWEEP_CAP = 300        # Swept cap (spec §3)
BPRIME_C100 = 100             # correct subsample size (spec §3)
BPRIME_BATCH = 16             # GPU mini-batch (memory-safe; OOM auto-halves)
BPRIME_WALL_CAP_S = 19800     # soft in-container wall guard (5.5 h) < Modal timeout


def _bprime_grid(L: int):
    """Fractional (ℓs,ℓt) grid (spec §2 Step 2). Pure function of L.
    lay(f)=min(L-1,max(1,round(f·L))); S=sources, T=targets;
    P1={(ℓs,ℓt)∈S×T: ℓs>ℓt}; P2=S×T. At L=24: S={12,14,16,18,20,22},
    T={2,4,6,8,10,12}, |P1|=35, |P2|=36."""
    def lay(f):
        return min(L - 1, max(1, int(round(f * L))))
    S = sorted({lay(f) for f in (1 / 2, 7 / 12, 2 / 3, 3 / 4, 5 / 6, 11 / 12)})
    T = sorted({lay(f) for f in (1 / 12, 1 / 6, 1 / 4, 1 / 3, 5 / 12, 1 / 2)})
    P1 = [(s, t) for s in S for t in T if s > t]
    P2 = [(h, t) for h in S for t in T]
    return S, T, P1, P2


def _build_specs_bprime():
    """Render the form-2 (entity) TEXT-ONLY prompt + the P2 carrier feedback for
    ALL 958 covered CLUTRR items, byte-identical in construction to
    _build_specs_g2b's f2 branch and the g2/g2b feedback renderer (spec §3 Step
    0 / Step 5). Order: covered rows of items.jsonl (file order) then
    headroom.jsonl (file order) — deterministic, seeds pinned over this order.
    Pure/local (torch-free). ABORTs (assert) on any build-gate violation."""
    lex = json.loads((_ROOT / "data/nsk1-clutrr/lexicon.json").read_text())
    rel_surface = {v: k for k, v in lex["relations"].items()}  # URN -> mother/father

    def _rows(path, stratum_filter):
        for line in (_ROOT / path).read_text().splitlines():
            if not line.strip():
                continue
            it = json.loads(line)
            if stratum_filter is not None and it.get("stratum") != stratum_filter:
                continue
            yield it

    src = list(_rows("data/nsk1-clutrr/items.jsonl", "covered")) + \
        list(_rows("data/nsk1-clutrr/headroom.jsonl", None))

    specs = []
    for it in src:
        item_lex = it["lexicon"]
        surfaces = list(item_lex.values())
        # 3-name pairwise-distinct (spec §3 Step 0 ASSERT)
        assert len(item_lex) == 3 and len(surfaces) == 3, \
            "item %s not 3-name" % it["item_id"]
        assert len({s.lower() for s in surfaces}) == 3, \
            "item %s names not pairwise distinct" % it["item_id"]
        subj_urn = it["hop1"]["subject"]
        bridge_urn = it["hop1_bridge"]
        base_surface = item_lex[subj_urn]
        top_urns = [u for u in item_lex if u not in (subj_urn, bridge_urn)]
        assert len(top_urns) == 1, "item %s: no unique chain-top" % it["item_id"]
        top_surface = item_lex[top_urns[0]]
        bridge_surface = item_lex[bridge_urn]
        gold_rel = it["gold_surface"]

        story = "\n".join(it["context"])
        # form-2 text-only prompt — byte-identical to _build_specs_g2b f2_to
        q2 = "Who is the %s of %s?" % (gold_rel, base_surface)
        f2_to = "Story:\n%s\nQuestion: %s\n%s" % (story, q2, INSTRUCTION_ENTITY)

        # P2 carrier feedback — byte-identical to run-1/g2b renderer
        rs = rel_surface[it["hop1"]["rel"]]
        fb = "Note: the %s of %s is %s." % (rs, base_surface, bridge_surface)
        # per-carrier asserts (spec §5, ABORT): gold-name-not-in-feedback,
        # feedback word-count ≤ 24
        assert len(fb.split()) <= FEEDBACK_TOKEN_BUDGET, \
            "feedback budget breach (%s)" % it["item_id"]
        fb_tokens = [w.strip(".").lower() for w in fb.split()]
        assert top_surface.lower() not in fb_tokens, \
            "gold name leaked into feedback (%s)" % it["item_id"]
        # bridge surface must occur in the feedback (P2 locus, in-container assert too)
        assert bridge_surface.lower() in fb.lower(), \
            "bridge surface absent from feedback (%s)" % it["item_id"]

        specs.append({
            "item_id": it["item_id"],
            "prompt": f2_to,               # container applies chat template
            "feedback": fb,                # tokenized RAW in container
            "bridge_surface": bridge_surface,
            "gold_top": top_surface,
            "base": base_surface,
            "surfaces": surfaces,
        })

    assert len(specs) == 958, "expected 958 covered items, got %d" % len(specs)
    return specs


def _bp_wilson(k: int, n: int, z: float = BPRIME_Z):
    """One-sided Wilson score interval bounds (spec §4). Returns (LB, UB)."""
    if n == 0:
        return (0.0, 0.0)
    phat = k / n
    denom = 1.0 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = (z / denom) * _bp_math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))
    return (max(0.0, center - half), min(1.0, center + half))


def _bp_binom_sf_ge(b: int, n: int, p: float = 0.5):
    """Exact one-sided binomial P(X >= b | n, p) (spec §4 paired excess)."""
    if n == 0:
        return 1.0
    return float(sum(_bp_math.comb(n, k) * (p ** k) * ((1 - p) ** (n - k))
                     for k in range(b, n + 1)))


def _bp_sattolo(n: int, seed: int):
    """Seed-pinned derangement (single-cycle Sattolo shuffle) of range(n);
    guaranteed fixed-point-free for n>=2 (spec §3 Step 3: seed 20260711,
    ASSERT fixed-point-free). Disclosed operational instantiation."""
    rng = _bp_random.Random(seed)
    perm = list(range(n))
    for i in range(n - 1, 0, -1):
        j = rng.randrange(i)  # 0 <= j < i (strict) => single cycle, no fixed pts
        perm[i], perm[j] = perm[j], perm[i]
    return perm


# ----------------------------------------------------- GPU body (torch, remote)
def _bprime_body(model_id, specs, headroom_ids, headroom_g2d_correct,
                 batch_size, wall_cap_s):
    import time
    import traceback
    try:
        return _bprime_body_impl(model_id, specs, headroom_ids,
                                 headroom_g2d_correct, batch_size, wall_cap_s)
    except Exception as e:  # noqa: BLE001
        tb = traceback.format_exc()
        print("BPRIME ERROR:", repr(e))
        print(tb)
        return {"aborted": True, "abort_reason": "EXCEPTION: %s" % repr(e),
                "traceback": tb, "rows": [], "swept_item_ids": [],
                "rescued_p1": [], "rescued_p1_ctrl": [], "rescued_p2": [],
                "rescued_p2_ctrl": []}


def _bprime_body_impl(model_id, specs, headroom_ids, headroom_g2d_correct,
                      batch_size, wall_cap_s):
    import time
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    t0 = time.time()
    n = len(specs)
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float32)
    model.to("cuda").eval()
    L = int(model.config.num_hidden_layers)
    d_model = int(model.config.hidden_size)
    assert L >= 12, "ABORT: L=%d < 12" % L
    layers = model.model.layers
    S, T, P1cells, P2cells = _bprime_grid(L)
    assert 20 <= len(P1cells) <= 40, "ABORT: |P1|=%d out of [20,40]" % len(P1cells)
    assert len(P2cells) <= 40, "ABORT: |P2|=%d > 40" % len(P2cells)
    harvest_layers = sorted(set(S) | set(T))  # spec §3 Step 1: "layer set of Step 2"
    commit = getattr(model.config, "_commit_hash", None)
    print("[bprime] model=%s L=%d d=%d commit=%s" % (model_id, L, d_model, commit))
    print("[bprime] S=%s T=%s |P1|=%d |P2|=%d" % (S, T, len(P1cells), len(P2cells)))

    # ---- patch hook state + robust forward-PRE-hook (edits INPUT of module ℓt)
    hook_state = {"vec": None}  # [bs, d] to write at final-prompt position, or None

    def pre_hook(module, args, kwargs):
        if hook_state["vec"] is None:
            return None
        hs = None
        where = None
        if len(args) > 0 and torch.is_tensor(args[0]) and args[0].dim() == 3:
            hs, where = args[0], "arg"
        elif torch.is_tensor(kwargs.get("hidden_states")):
            hs, where = kwargs["hidden_states"], "kw"
        if hs is None or hs.shape[1] <= 1:
            return None  # decode step (seq==1) -> prefill-only patch (spec §4)
        hs = hs.clone()
        hs[:, -1, :] = hook_state["vec"].to(hs.dtype)
        if where == "arg":
            return ((hs,) + tuple(args[1:]), kwargs)
        nk = dict(kwargs)
        nk["hidden_states"] = hs
        return (args, nk)

    def _chat_ids(prompt):
        msgs = [{"role": "user", "content": prompt}]
        try:
            return list(tok.apply_chat_template(msgs, add_generation_prompt=True))
        except Exception:  # noqa: BLE001
            return list(tok(prompt).input_ids)

    def _pad_batch(id_lists):
        maxlen = max(len(x) for x in id_lists)
        ii, am = [], []
        for x in id_lists:
            pad = maxlen - len(x)
            ii.append([tok.pad_token_id] * pad + x)
            am.append([0] * pad + [1] * len(x))
        return (torch.tensor(ii, device="cuda"),
                torch.tensor(am, device="cuda"), maxlen)

    def _gen(id_lists, patch_layer=None, patch_vecs=None):
        """Greedy 16-tok generate over a left-padded batch; optional prefill-only
        patch on decoder module patch_layer. OOM -> halve + recurse."""
        try:
            ii, am, maxlen = _pad_batch(id_lists)
            handle = None
            if patch_layer is not None:
                hook_state["vec"] = torch.stack(patch_vecs).to("cuda")
                handle = layers[patch_layer].register_forward_pre_hook(
                    pre_hook, with_kwargs=True)
            try:
                with torch.no_grad():
                    out = model.generate(
                        input_ids=ii, attention_mask=am,
                        max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
                        num_beams=1, pad_token_id=tok.pad_token_id)
            finally:
                if handle is not None:
                    handle.remove()
                hook_state["vec"] = None
            return [tok.decode(out[i][maxlen:], skip_special_tokens=True)
                    for i in range(len(id_lists))]
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if len(id_lists) == 1:
                raise
            mid = len(id_lists) // 2
            pv1 = patch_vecs[:mid] if patch_vecs is not None else None
            pv2 = patch_vecs[mid:] if patch_vecs is not None else None
            return (_gen(id_lists[:mid], patch_layer, pv1)
                    + _gen(id_lists[mid:], patch_layer, pv2))

    # =============== STEP 1: text-only pass + harvest (958 items) ===============
    prompt_ids = [_chat_ids(s["prompt"]) for s in specs]
    text_only = [False] * n
    text_gen = [None] * n
    harvest = [None] * n  # per item: {ℓ: fp32 cuda vector} for ℓ in harvest_layers
    for i, s in enumerate(specs):
        ids = prompt_ids[i]
        idt = torch.tensor([ids], device="cuda")
        with torch.no_grad():
            fwd = model(idt, output_hidden_states=True)
        hv = {}
        for ell in harvest_layers:
            hv[ell] = fwd.hidden_states[ell][0, -1, :].detach().float().clone()
        harvest[i] = hv
        del fwd
        gen = _gen([ids])[0]
        text_gen[i] = gen
        text_only[i] = bool(_score_entity(gen, s["gold_top"], s["base"], s["surfaces"]))
        if (i + 1) % 100 == 0:
            print("[bprime] step1 %d/%d  acc_running=%.3f  t=%.0fs"
                  % (i + 1, n, sum(text_only[:i + 1]) / (i + 1), time.time() - t0))

    acc_text = sum(text_only) / n
    headroom_ok = (0.05 <= acc_text <= 0.85) and (n >= 900)
    # reproducibility check on the 100 headroom items vs G2d R3/clutrr/form-2
    hid_set = set(headroom_ids)
    id_to_idx = {s["item_id"]: i for i, s in enumerate(specs)}
    repro_agree = 0
    repro_disagree = []
    for hid in headroom_ids:
        idx = id_to_idx[hid]
        if bool(text_only[idx]) == bool(headroom_g2d_correct[hid]):
            repro_agree += 1
        else:
            repro_disagree.append(hid)
    print("[bprime] STEP1 done: acc_text=%.4f headroom_ok=%s repro_agree=%d/100"
          % (acc_text, headroom_ok, repro_agree))

    rows = []
    for i, s in enumerate(specs):
        rows.append({"item_id": s["item_id"], "probe": "text-only", "cell": None,
                     "gen": text_gen[i], "correct": bool(text_only[i]),
                     "gold": s["gold_top"], "phase": "exploratory",
                     "gate": "BPRIME", "host": "R3", "model": model_id,
                     "surface": "clutrr", "form": "2"})

    base_summary = {
        "model": model_id, "model_commit": commit, "L": L, "d_model": d_model,
        "S": S, "T": T, "P1_cells": P1cells, "P2_cells": P2cells,
        "harvest_layers": harvest_layers, "seed": BPRIME_SEED,
        "n_items": n, "acc_text_only": acc_text, "n_scored": n,
        "headroom_ok": bool(headroom_ok),
        "repro_agree_headroom": repro_agree, "repro_disagreements": repro_disagree,
        "batch_size": batch_size,
    }

    # ABORT gates that must fire BEFORE any sweep spend (spec §3 Step 1 / §5.1)
    if repro_agree < 95:
        base_summary.update({"aborted": True,
                             "abort_reason": "REPRO_DRIFT repro_agree=%d<95" % repro_agree})
        return {"aborted": True, "abort_reason": base_summary["abort_reason"],
                "rows": rows, "summary": base_summary, "swept_item_ids": [],
                "rescued_p1": [], "rescued_p1_ctrl": [], "rescued_p2": [],
                "rescued_p2_ctrl": [], "elapsed_s": time.time() - t0}

    # =============== STEP 3: swept sets, C100, derangement ======================
    F = [i for i in range(n) if not text_only[i]]
    correct_idx = [i for i in range(n) if text_only[i]]
    if len(F) <= BPRIME_SWEEP_CAP:
        swept = list(F)
    else:
        swept = sorted(_bp_random.Random(BPRIME_SEED).sample(F, BPRIME_SWEEP_CAP))
    assert len(correct_idx) >= BPRIME_C100, \
        "ABORT: only %d correct items (<%d for C100)" % (len(correct_idx), BPRIME_C100)
    c100 = sorted(_bp_random.Random(BPRIME_SEED).sample(correct_idx, BPRIME_C100))
    assert not (set(swept) & set(c100)), "ABORT: Swept∩C100 nonempty"
    m = len(swept)
    perm = _bp_sattolo(m, BPRIME_SEED)  # derangement over swept positions
    assert all(perm[k] != k for k in range(m)), "ABORT: derangement has fixed point"
    sigma = {swept[k]: swept[perm[k]] for k in range(m)}  # item idx -> deranged item idx
    print("[bprime] |F|=%d |Swept|=%d |C100|=%d (derangement fixed-point-free)"
          % (len(F), m, len(c100)))
    base_summary.update({"n_failures": len(F), "n_swept": m, "n_c100": len(c100),
                         "swept_is_full_F": len(F) <= BPRIME_SWEEP_CAP})

    # =============== P2 carriers: feedback forward + bridge-token harvest =======
    carrier = {}   # item idx -> {ℓh: fp32 cuda vector} for ℓh in S
    need_carrier = sorted(set(swept) | set(c100))
    for i in need_carrier:
        s = specs[i]
        enc = tok(s["feedback"], return_offsets_mapping=True)
        ids = enc["input_ids"]
        offsets = enc["offset_mapping"]
        bridge = s["bridge_surface"]
        cstart = s["feedback"].rfind(bridge)
        assert cstart >= 0, "ABORT: bridge '%s' not in feedback (%s)" % (bridge, s["item_id"])
        cend = cstart + len(bridge)
        tok_idx = None
        for ti, (a, b) in enumerate(offsets):
            if a == b:  # special token (e.g. BOS) has zero-width span
                continue
            if a < cend and b > cstart:  # token overlaps the bridge span
                tok_idx = ti           # keep the LAST overlapping token
        assert tok_idx is not None, "ABORT: bridge token not located (%s)" % s["item_id"]
        idt = torch.tensor([ids], device="cuda")
        with torch.no_grad():
            fwd = model(idt, output_hidden_states=True)
        cv = {}
        for ell in S:
            cv[ell] = fwd.hidden_states[ell][0, tok_idx, :].detach().float().clone()
        carrier[i] = cv
        del fwd
    print("[bprime] carriers harvested: %d (no generation)" % len(need_carrier))

    # =============== STEP 4/5: P1 + P2 sweeps + breakage ========================
    def _mini(items):
        for a in range(0, len(items), batch_size):
            yield items[a:a + batch_size]

    rescued_p1 = {i: False for i in swept}
    rescued_p1_ctrl = {i: False for i in swept}
    rescued_p2 = {i: False for i in swept}
    rescued_p2_ctrl = {i: False for i in swept}
    p1_real_cell = {}
    p1_ctrl_cell = {}
    p2_real_cell = {}
    p2_ctrl_cell = {}
    breakage_cell = {}
    partial = False
    partial_reason = None

    def _sweep_cell_arm(cell_items, ls, lt, source_map, probe, cell_correct_acc,
                        rescued_acc):
        for mb in _mini(cell_items):
            idl = [prompt_ids[i] for i in mb]
            vecs = [source_map(i)[ls] for i in mb]
            gens = _gen(idl, patch_layer=lt, patch_vecs=vecs)
            for i, g in zip(mb, gens):
                s = specs[i]
                ok = bool(_score_entity(g, s["gold_top"], s["base"], s["surfaces"]))
                rows.append({"item_id": s["item_id"], "probe": probe,
                             "cell": [ls, lt], "gen": g, "correct": ok,
                             "gold": s["gold_top"], "phase": "exploratory",
                             "gate": "BPRIME", "host": "R3", "model": model_id,
                             "surface": "clutrr", "form": "2"})
                if ok:
                    cell_correct_acc[(ls, lt)] = cell_correct_acc.get((ls, lt), 0) + 1
                    if rescued_acc is not None:
                        rescued_acc[i] = True

    # ---- P1 self back-patch (gate-bearing): real + control ----
    for (ls, lt) in P1cells:
        if time.time() - t0 > wall_cap_s:
            partial, partial_reason = True, "WALL_CAP during P1"
            break
        _sweep_cell_arm(swept, ls, lt, lambda i: harvest[i], "p1",
                        p1_real_cell, rescued_p1)
        _sweep_cell_arm(swept, ls, lt, lambda i: harvest[sigma[i]], "p1-ctrl",
                        p1_ctrl_cell, rescued_p1_ctrl)
        print("[bprime] P1 cell (ls=%d,lt=%d) done t=%.0fs" % (ls, lt, time.time() - t0))

    # ---- P2 oracle bridge-patch (reported-only): real + control ----
    if not partial:
        for (lh, lt) in P2cells:
            if time.time() - t0 > wall_cap_s:
                partial, partial_reason = True, "WALL_CAP during P2"
                break
            _sweep_cell_arm(swept, lh, lt, lambda i: carrier[i], "p2",
                            p2_real_cell, rescued_p2)
            _sweep_cell_arm(swept, lh, lt, lambda i: carrier[sigma[i]], "p2-ctrl",
                            p2_ctrl_cell, rescued_p2_ctrl)
            print("[bprime] P2 cell (lh=%d,lt=%d) done t=%.0fs" % (lh, lt, time.time() - t0))

    # ---- P2 breakage on C100 (real bridge-patch, no control): correct->wrong ----
    if not partial:
        for (lh, lt) in P2cells:
            if time.time() - t0 > wall_cap_s:
                partial, partial_reason = True, "WALL_CAP during breakage"
                break
            for mb in _mini(c100):
                idl = [prompt_ids[i] for i in mb]
                vecs = [carrier[i][lh] for i in mb]
                gens = _gen(idl, patch_layer=lt, patch_vecs=vecs)
                for i, g in zip(mb, gens):
                    s = specs[i]
                    ok = bool(_score_entity(g, s["gold_top"], s["base"], s["surfaces"]))
                    flip = (not ok)  # C100 items are text-only-correct by construction
                    rows.append({"item_id": s["item_id"], "probe": "p2-breakage",
                                 "cell": [lh, lt], "gen": g, "correct": ok,
                                 "gold": s["gold_top"], "phase": "exploratory",
                                 "gate": "BPRIME", "host": "R3", "model": model_id,
                                 "surface": "clutrr", "form": "2"})
                    if flip:
                        breakage_cell[(lh, lt)] = breakage_cell.get((lh, lt), 0) + 1

    base_summary.update({
        "aborted": False, "partial": partial, "partial_reason": partial_reason,
        "heatmap_p1_real": {"%d_%d" % (a, b): p1_real_cell.get((a, b), 0) for (a, b) in P1cells},
        "heatmap_p1_ctrl": {"%d_%d" % (a, b): p1_ctrl_cell.get((a, b), 0) for (a, b) in P1cells},
        "heatmap_p2_real": {"%d_%d" % (a, b): p2_real_cell.get((a, b), 0) for (a, b) in P2cells},
        "heatmap_p2_ctrl": {"%d_%d" % (a, b): p2_ctrl_cell.get((a, b), 0) for (a, b) in P2cells},
        "heatmap_breakage_c100": {"%d_%d" % (a, b): breakage_cell.get((a, b), 0) for (a, b) in P2cells},
        "elapsed_s": time.time() - t0,
    })
    swept_ids = [specs[i]["item_id"] for i in swept]
    return {
        "aborted": False, "partial": partial, "partial_reason": partial_reason,
        "rows": [json.loads(json.dumps(r, default=str)) for r in rows],
        "summary": json.loads(json.dumps(base_summary, default=str)),
        "swept_item_ids": swept_ids,
        "rescued_p1": [1 if rescued_p1[i] else 0 for i in swept],
        "rescued_p1_ctrl": [1 if rescued_p1_ctrl[i] else 0 for i in swept],
        "rescued_p2": [1 if rescued_p2[i] else 0 for i in swept],
        "rescued_p2_ctrl": [1 if rescued_p2_ctrl[i] else 0 for i in swept],
        "elapsed_s": time.time() - t0,
    }


@app.function(image=image, gpu="A10G", volumes={HF_CACHE_MOUNT: hf_cache},
              timeout=21600)
def bprime_a10g(model_id, specs, headroom_ids, headroom_g2d_correct,
                batch_size, wall_cap_s):
    r = _bprime_body(model_id, specs, headroom_ids, headroom_g2d_correct,
                     batch_size, wall_cap_s)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return r


def _bprime_gate(res):
    """Mechanical ASM-0041 verdict from returned per-item rescue vectors + gate
    conditions. Computes Wilson bounds, paired excess, and the §5 label. The
    runner reports these numbers; interpretation is designer work."""
    r1 = res.get("rescued_p1", [])
    r1c = res.get("rescued_p1_ctrl", [])
    r2 = res.get("rescued_p2", [])
    r2c = res.get("rescued_p2_ctrl", [])
    ns = len(r1)
    k1 = sum(r1)
    k1c = sum(r1c)
    k2 = sum(r2)
    k2c = sum(r2c)
    lb1, ub1 = _bp_wilson(k1, ns)
    lb1c, ub1c = _bp_wilson(k1c, ns)
    lb2, ub2 = _bp_wilson(k2, ns)
    lb2c, ub2c = _bp_wilson(k2c, ns)

    def _excess(real, ctrl):
        b = sum(1 for x, y in zip(real, ctrl) if x and not y)
        c = sum(1 for x, y in zip(real, ctrl) if (not x) and y)
        p = _bp_binom_sf_ge(b, b + c, 0.5)
        return {"b": b, "c": c, "n_discordant": b + c, "p_one_sided": p,
                "excess_pass": bool((b > c) and (p < 0.05))}

    exc1 = _excess(r1, r1c)
    exc2 = _excess(r2, r2c)

    summary = res.get("summary", {})
    headroom_ok = bool(summary.get("headroom_ok", False))
    aborted = bool(res.get("aborted", False))
    partial = bool(res.get("partial", False))

    # §5 decision rule (evaluated in order)
    instrument_invalid = (not headroom_ok) or aborted or (lb1c >= BPRIME_FLOOR)
    if instrument_invalid:
        label = "INSTRUMENT-INVALID"
    elif (lb1 >= BPRIME_FLOOR) and exc1["excess_pass"]:
        label = "PASS"
    elif ub1 < BPRIME_FLOOR:
        label = "KILL-NO-LATENT-HEADROOM"
    else:
        label = "INCONCLUSIVE"

    return {
        "n_swept": ns,
        "rescue_p1": {"k": k1, "rate": (k1 / ns if ns else 0.0),
                      "wilson_lb95": lb1, "wilson_ub95": ub1},
        "rescue_p1_ctrl": {"k": k1c, "rate": (k1c / ns if ns else 0.0),
                           "wilson_lb95": lb1c, "wilson_ub95": ub1c},
        "rescue_p2": {"k": k2, "rate": (k2 / ns if ns else 0.0),
                      "wilson_lb95": lb2, "wilson_ub95": ub2},
        "rescue_p2_ctrl": {"k": k2c, "rate": (k2c / ns if ns else 0.0),
                           "wilson_lb95": lb2c, "wilson_ub95": ub2c},
        "paired_excess_p1": exc1,
        "paired_excess_p2": exc2,
        "floor": BPRIME_FLOOR,
        "headroom_ok": headroom_ok,
        "aborted": aborted, "partial": partial,
        "control_rescues_at_floor": bool(lb1c >= BPRIME_FLOOR),
        "instrument_invalid_triggers": {
            "not_headroom_ok": (not headroom_ok), "aborted": aborted,
            "ctrl_lb_ge_floor": bool(lb1c >= BPRIME_FLOOR)},
        "gate_label": label,
    }


@app.local_entrypoint()
def bprime(dry_plan: bool = False, gpu: str = "A10G"):
    import hashlib
    import time

    specs = _build_specs_bprime()
    n = len(specs)
    # byte-equality ASSERT: for the 100 headroom items, our f2_to == g2b's f2_to
    g2b_specs, _vocab = _build_specs_g2b()
    g2b_f2 = {s["item_id"]: s["f2_to"] for s in g2b_specs}
    mine = {s["item_id"]: s["prompt"] for s in specs}
    mism = [iid for iid in g2b_f2 if g2b_f2[iid] != mine.get(iid)]
    assert not mism, "ABORT: form-2 prompt not byte-equal to g2b for %s" % mism[:5]
    print("[bprime] byte-equality vs _build_specs_g2b f2_to: 100/100 OK")

    # G2d reproducibility reference vector (R3 / clutrr / form-2 text-only correct)
    headroom_ids = [json.loads(l)["item_id"]
                    for l in (_ROOT / "data/nsk1-clutrr/headroom.jsonl")
                    .read_text().splitlines() if l.strip()]
    g2d_correct = {}
    for l in (_ROOT / "poc/nsk1/out/g2d/g2d_rows.jsonl").read_text().splitlines():
        r = json.loads(l)
        if r.get("host") == "R3" and r.get("surface") == "clutrr" and r.get("form") == "2":
            g2d_correct[r["item_id"]] = bool(r["correct_text_only"])
    assert all(h in g2d_correct for h in headroom_ids), "ABORT: g2d repro vector incomplete"

    L_expected = 24  # SmolLM2-1.7B (asserted in-container from the real config)
    S, T, P1cells, P2cells = _bprime_grid(L_expected)
    est_swept = 230   # STIPULATED planning band (ASM-0042), from G2d 24/100 failure rate
    worst_swept = 300

    def _gencount(nsw):
        step1 = n
        carriers = nsw + BPRIME_C100  # forward-only, no generation
        p1 = nsw * len(P1cells) * 2
        p2 = nsw * len(P2cells) * 2
        breakage = BPRIME_C100 * len(P2cells)
        return step1, carriers, p1, p2, breakage, step1 + p1 + p2 + breakage

    s1, cf, p1g, p2g, brk, tot = _gencount(est_swept)
    _, cfw, p1w, p2w, brkw, totw = _gencount(worst_swept)
    # GPU-h / $ estimate: A10G ~$1.10/GPU-h; G2d throughput ~6 batch-1 gens/s,
    # batched sweeps materially faster; span the spec's own 3-8 GPU-h band.
    gpuh_lo, gpuh_hi = 2.0, 8.0
    usd_lo, usd_hi = round(gpuh_lo * 1.10, 1), round(gpuh_hi * 1.10, 1)

    print("=== B′ Stage-0 internal-channel diagnostic — PLAN (spec docs/next/nsk1-bprime-stage0-spec.md) ===")
    print("host                : R3 = %s (zero-shot, CLUTRR entity form 2)" % BPRIME_MODEL)
    print("items (covered)     : %d (858 items.jsonl covered + 100 headroom.jsonl)" % n)
    print("grid (L=%d expected) : S=%s T=%s  |P1|=%d  |P2|=%d" % (L_expected, S, T, len(P1cells), len(P2cells)))
    print("seeds               : %d (σ derangement / C100 / 300-subsample)" % BPRIME_SEED)
    print("floor / z           : %.2f / %.4f (one-sided Wilson 95%%)" % (BPRIME_FLOOR, BPRIME_Z))
    print("planning |Swept|    : %d (STIPULATED ASM-0042; actual = text-only failures, cap %d)" % (est_swept, BPRIME_SWEEP_CAP))
    print("gen count @|Swept|=%d: step1=%d  P1=%d  P2=%d  breakage=%d  TOTAL=%d (+%d carrier forwards, no-gen)"
          % (est_swept, s1, p1g, p2g, brk, tot, cf))
    print("gen count @|Swept|=%d: TOTAL=%d (+%d carrier forwards)  <- worst case" % (worst_swept, totw, cfw))
    print("GPU-h estimate      : %.1f–%.1f  |  $ estimate : $%.1f–$%.1f  (A10G, fp32)" % (gpuh_lo, gpuh_hi, usd_lo, usd_hi))
    print("HARD caps           : $25 / 10 GPU-h / 12 h wall  (in-container soft wall guard %ds)" % BPRIME_WALL_CAP_S)
    print("phase               : exploratory (quarantined, uncitable, flips no verdict)")
    print("decision rule       : ASM-0041 §5 — PASS iff Wilson-LB95(P1)>=%.2f AND paired-excess(P1); "
          "KILL iff Wilson-UB95(P1)<%.2f; ctrl-LB>=%.2f => INSTRUMENT-INVALID" % (BPRIME_FLOOR, BPRIME_FLOOR, BPRIME_FLOOR))

    caps_ok = (tot <= 60000 and totw <= 60000 and gpuh_hi <= 10 and usd_hi <= 25)
    print("within caps (plan)  : %s" % caps_ok)

    if dry_plan:
        s0 = specs[0]
        print("\nDRY-PLAN ONLY — no GPU launched, $0 spent. All build asserts passed.")
        print("\n--- sample form-2 text-only prompt (item %s) ---\n%s" % (s0["item_id"], s0["prompt"]))
        print("\n--- sample P2 carrier feedback (item %s) ---\n%s  [bridge=%s gold_top=%s]"
              % (s0["item_id"], s0["feedback"], s0["bridge_surface"], s0["gold_top"]))
        print("\nP1 cells (%d): %s" % (len(P1cells), P1cells))
        print("P2 cells (%d): %s" % (len(P2cells), P2cells))
        return

    if not caps_ok:
        raise SystemExit("ABORT: plan exceeds caps — not launching (tot=%d totw=%d)" % (tot, totw))

    genfn = bprime_a10g  # A10G only (spec §7)
    t_launch = time.time()
    res = genfn.remote(BPRIME_MODEL, specs, headroom_ids, g2d_correct,
                       BPRIME_BATCH, BPRIME_WALL_CAP_S)
    wall_s = time.time() - t_launch

    outdir = _ROOT / "poc/nsk1/out/bprime"
    outdir.mkdir(parents=True, exist_ok=True)
    rows = res.get("rows", [])
    with open(outdir / "bprime_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")

    gate = _bprime_gate(res)
    summary = dict(res.get("summary", {}))
    summary.update({
        "spec_ref": "docs/next/nsk1-bprime-stage0-spec.md",
        "gate": "BPRIME", "phase": "exploratory",
        "verdict": gate,
        "wall_clock_s_local": round(wall_s, 1),
        "gpu_h_estimate": round((res.get("summary", {}).get("elapsed_s", 0.0)) / 3600.0, 3),
        "usd_estimate": round((res.get("summary", {}).get("elapsed_s", 0.0)) / 3600.0 * 1.10, 3),
        "n_rows": len(rows),
        "aborted": bool(res.get("aborted", False)),
        "abort_reason": res.get("abort_reason"),
        "partial": bool(res.get("partial", False)),
        "partial_reason": res.get("partial_reason"),
        "hard_caps": {"usd": 25, "gpu_h": 10, "wall_h": 12},
        "seed": BPRIME_SEED, "floor": BPRIME_FLOOR,
    })
    with open(outdir / "bprime_summary.json", "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)

    def _sha(p):
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    sha_rows = _sha(outdir / "bprime_rows.jsonl")
    sha_sum = _sha(outdir / "bprime_summary.json")

    print("\n=== B′ RESULT (phase:exploratory) ===")
    print("aborted=%s partial=%s  n_rows=%d  elapsed=%.0fs (GPU) / %.0fs (wall)"
          % (res.get("aborted"), res.get("partial"), len(rows),
             res.get("summary", {}).get("elapsed_s", 0.0), wall_s))
    print(json.dumps(gate, indent=1, sort_keys=True))
    print("MECHANICAL VERDICT (ASM-0041 §5): %s" % gate["gate_label"])
    print("sha256 bprime_rows.jsonl    = %s" % sha_rows)
    print("sha256 bprime_summary.json  = %s" % sha_sum)
